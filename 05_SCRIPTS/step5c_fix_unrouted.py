# -*- coding: utf-8 -*-
"""
STEP 5c - pos-passe guiado pelo DRC: fecha as conexoes que o Freerouting deixou abertas.

Autor: Bruno Costa

Roda em ciclos: kicad-cli DRC -> JSON -> para cada par "unconnected" aplica, em ordem:
  A) pad de potencia (GND/+3V3/+5V): via de stitch perto do pad (plano GND em In2/B.Cu, +3V3 em In1,
     +5V nas zonas +5V) - para pinos do U7 a via vai por baixo do corpo do LQFP quando nao ha espaco fora;
  B) trilha com ponta solta em transicao de camada: via na ponta (ou recua ao longo da trilha);
  C) dois itens de sinal: via na ponta da trilha + trilha ate o pad / conexao direta reta ou em L;
  D) ilha de zona GND sem via: via no interior da ilha (liga ao plano In2).
Nunca toca itens travados (criticos do step5b, CAN H/L). Para quando nada mais muda ou unconnected == 0.
Uso:  python step5c_fix_unrouted.py [--rounds N] [--dry]
"""
import json, os, re, subprocess, sys, math
import pcbnew
from pcbnew import VECTOR2I, FromMM, ToMM

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(ROOT, "04_PROJECT", "HybridPanda", "HybridPanda.kicad_pcb")
KICAD_CLI = os.path.join(os.path.dirname(sys.executable), "kicad-cli.exe")
DRC_TMP = os.path.join(ROOT, "06_REPORTS", "tmp_drc_5c.json")
REPORT = os.path.join(ROOT, "06_REPORTS", "step5c_fix.json")
ROUNDS = int(sys.argv[sys.argv.index("--rounds") + 1]) if "--rounds" in sys.argv else 5
DRY = "--dry" in sys.argv
PLANE_NETS = {"GND": None, "+3V3": "In1.Cu"}  # via em qualquer lugar liga ao GND; +3V3 so dentro da zona In1
LAYERS4 = (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu)

board = pcbnew.LoadBoard(PCB)
u7 = board.FindFootprintByReference("U7"); u7c = u7.GetPosition()
nets = board.GetNetsByName()
report = {"rounds": [], "warnings": []}
W = report["warnings"].append

def mmv(x, y): return VECTOR2I(FromMM(x), FromMM(y))
def pt(p): return (round(ToMM(p.x), 3), round(ToMM(p.y), 3))
def dist(a, b): return ToMM((a - b).EuclideanNorm())

# ---------------------------------------------------------------- colisao (mesma logica do step5b)
all_pads = [p for f in board.GetFootprints() for p in f.Pads()]
KEEPOUTS = [z for z in board.Zones() if z.GetIsRuleArea()] + [z for fp in board.GetFootprints() for z in fp.Zones() if z.GetIsRuleArea()]
def tracks(): return list(board.GetTracks())
def seg_collides(a, b, width, layer, netcode, clearance=0.12):
    shp = pcbnew.SHAPE_SEGMENT(a, b, FromMM(width))
    for z in KEEPOUTS:
        if z.GetDoNotAllowTracks() and z.IsOnLayer(layer) and z.Outline().Collide(shp, FromMM(0.1)): return "keepout"
    for p in all_pads:
        if p.GetNetCode() == netcode or not p.IsOnLayer(layer): continue
        if p.GetEffectiveShape(layer).Collide(shp, FromMM(clearance)): return "pad %s.%s" % (p.GetParentFootprint().GetReference(), p.GetNumber())
    for t in tracks():
        if t.GetNetCode() == netcode or not t.IsOnLayer(layer): continue
        if t.GetEffectiveShape(layer).Collide(shp, FromMM(clearance)): return "track %s" % t.GetNetname()
    return None
def via_collides(pos, dia, netcode, clearance=0.15):
    shp = pcbnew.SHAPE_CIRCLE(pos, FromMM(dia / 2))
    for z in KEEPOUTS:
        if z.GetDoNotAllowVias() and z.Outline().Collide(shp, FromMM(clearance)): return "keepout"
    for p in all_pads:
        if p.GetNetCode() == netcode: continue
        for l in LAYERS4:
            if p.IsOnLayer(l) and p.GetEffectiveShape(l).Collide(shp, FromMM(clearance)): return "pad %s.%s" % (p.GetParentFootprint().GetReference(), p.GetNumber())
    for t in tracks():
        if t.GetNetCode() == netcode: continue
        for l in LAYERS4:
            if t.IsOnLayer(l) and t.GetEffectiveShape(l).Collide(shp, FromMM(clearance)): return "track %s" % t.GetNetname()
    # furo x furo (hole_to_hole 0.2 mm no baseline)
    for t in tracks():
        if t.GetClass() == "PCB_VIA" and dist(t.GetPosition(), pos) < 0.3 + 0.25: return "hole_to_hole via"
    for p in all_pads:
        if p.GetDrillSize().x > 0 and dist(p.GetPosition(), pos) < (ToMM(p.GetDrillSize().x) + 0.3) / 2 + 0.25: return "hole_to_hole pad"
    return None

added = []
def add_track(a, b, width, layer, netcode):
    if a == b: return None
    t = pcbnew.PCB_TRACK(board); t.SetStart(a); t.SetEnd(b); t.SetWidth(FromMM(width)); t.SetLayer(layer); t.SetNetCode(netcode)
    board.Add(t); added.append(("track", pt(a), pt(b), board.GetLayerName(layer))); return t
def add_via(pos, netcode, dia=0.6, drill=0.3):
    v = pcbnew.PCB_VIA(board); v.SetPosition(pos); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetWidth(FromMM(dia)); v.SetDrill(FromMM(drill))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNetCode(netcode)
    board.Add(v); added.append(("via", pt(pos))); return v

def zone_contains(netname, layer, pos):
    """pos esta dentro do contorno de alguma zona (nao-keepout) dessa net nessa camada?"""
    for z in board.Zones():
        if z.GetIsRuleArea() or z.GetNetname() != netname or not z.IsOnLayer(layer): continue
        if z.Outline().Contains(pos): return True
    return False
def plane_ok(netname, pos):
    if netname == "GND": return True
    if netname == "+3V3": return zone_contains("+3V3", pcbnew.In1_Cu, pos)
    if netname == "+5V": return any(zone_contains("+5V", l, pos) for l in LAYERS4)
    return False

def item_layer(p):
    if p.IsOnLayer(pcbnew.B_Cu) and not p.IsOnLayer(pcbnew.F_Cu): return pcbnew.B_Cu
    return pcbnew.F_Cu

# ---------------------------------------------------------------- parsing do DRC
RX_PAD = re.compile(r"^(PTH pad|Pad) (\S+) \[(.+?)\] of (\S+)(?: on (\S+))?")
RX_TRK = re.compile(r"^Track \[(.+?)\] on (\S+), length ([\d.,]+) mm")
RX_VIA = re.compile(r"^Via \[(.+?)\]")
RX_ZONE = re.compile(r"^Zone \[(.+?)\]")
def parse(it):
    d = it["description"]; pos = mmv(it["pos"]["x"], it["pos"]["y"])
    m = RX_PAD.match(d)
    if m:
        fp = board.FindFootprintByReference(m.group(4)); pad = fp.FindPadByNumber(m.group(2)) if fp else None
        if pad is None:  # pads duplicados com mesmo numero (SW1): escolhe o mais proximo
            pass
        if fp and pad is not None and dist(pad.GetPosition(), pos) > 0.05:
            pad = min((p for p in fp.Pads() if p.GetNumber() == m.group(2)), key=lambda p: dist(p.GetPosition(), pos))
        return {"kind": "pad", "net": m.group(3), "ref": m.group(4), "num": m.group(2), "pos": pos, "obj": pad, "pth": m.group(1) == "PTH pad"}
    m = RX_TRK.match(d)
    if m:
        lay = board.GetLayerID(m.group(2)); L = float(m.group(3).replace(",", "."))
        cands = [t for t in tracks() if t.GetClass() == "PCB_TRACK" and t.GetNetname() == m.group(1) and t.GetLayer() == lay
                 and (dist(t.GetStart(), pos) < 0.02 or dist(t.GetEnd(), pos) < 0.02)]
        cands.sort(key=lambda t: abs(ToMM(t.GetLength()) - L))
        return {"kind": "track", "net": m.group(1), "layer": lay, "pos": pos, "obj": cands[0] if cands else None}
    m = RX_VIA.match(d)
    if m:
        v = [t for t in tracks() if t.GetClass() == "PCB_VIA" and dist(t.GetPosition(), pos) < 0.02]
        return {"kind": "via", "net": m.group(1), "pos": pos, "obj": v[0] if v else None}
    m = RX_ZONE.match(d)
    if m: return {"kind": "zone", "net": m.group(1), "pos": pos, "obj": None}
    return {"kind": "?", "net": None, "pos": pos, "obj": None, "desc": d}

def run_drc():
    r = subprocess.run([KICAD_CLI, "pcb", "drc", "--format", "json", "--severity-all", "--units", "mm", "-o", DRC_TMP, PCB], capture_output=True, text=True, timeout=600)
    with open(DRC_TMP, encoding="utf-8") as f: return json.load(f)

# ---------------------------------------------------------------- estrategias
def attached(E, layer, netcode, me):
    """ponta E (na camada) toca algo da mesma net alem de 'me'?"""
    for p in all_pads:
        if p.GetNetCode() == netcode and p.IsOnLayer(layer) and p.GetEffectiveShape(layer).Collide(E, FromMM(0.01)): return True
    for t in tracks():
        if t.GetNetCode() != netcode or t.m_Uuid.AsString() == me.m_Uuid.AsString(): continue
        if t.IsOnLayer(layer) and t.GetEffectiveShape(layer).Collide(E, FromMM(0.01)): return True
    for z in board.Zones():
        if not z.GetIsRuleArea() and z.GetNetCode() == netcode and z.IsOnLayer(layer) and z.GetFilledPolysList(layer).Contains(E): return True
    return False

def free_ends(t):
    lay = t.GetLayer(); nc = t.GetNetCode()
    return [E for E in (t.GetStart(), t.GetEnd()) if not attached(E, lay, nc, t)]

def try_via_at(pos, netcode, netname, dia=0.6):
    if via_collides(pos, dia, netcode, 0.12): return None
    return add_via(pos, netcode, dia, 0.3)

def stitch_pad(pad, netname):
    """via de stitch a 0.6..2.2 mm do pad, 8 direcoes; para pinos do U7 tenta fora e depois por baixo do corpo."""
    nc = pad.GetNetCode(); c = pad.GetPosition(); lay = item_layer(pad)
    if pad.GetParentFootprint().GetReference() == "U7":
        d = VECTOR2I(c.x - u7c.x, c.y - u7c.y)
        ax = (1, 0) if abs(d.x) > abs(d.y) else (0, 1)
        sg = 1 if (d.x if ax[0] else d.y) > 0 else -1
        for s in (sg, -sg):
            for along in (1.2, 1.5, 1.8, 2.2, 2.6):
                for lat in (0, 0.25, -0.25, 0.5, -0.5, 0.75, -0.75):
                    pos = VECTOR2I(c.x + int(FromMM(along) * ax[0] * s + FromMM(lat) * -ax[1]), c.y + int(FromMM(along) * ax[1] * s + FromMM(lat) * ax[0]))
                    knee = VECTOR2I(c.x + int(FromMM(0.9) * ax[0] * s), c.y + int(FromMM(0.9) * ax[1] * s))
                    if not plane_ok(netname, pos): continue
                    if via_collides(pos, 0.6, nc, 0.12) or seg_collides(c, knee, 0.25, lay, nc, 0.1) or seg_collides(knee, pos, 0.25, lay, nc, 0.1): continue
                    add_track(c, knee, 0.25, lay, nc); add_track(knee, pos, 0.25, lay, nc); add_via(pos, nc, 0.6, 0.3)
                    return "stitch U7 %s" % ("fora" if s == sg else "dentro")
        return None
    ang0 = math.atan2(c.y - u7c.y, c.x - u7c.x)
    for d_ in (0.6, 0.75, 0.95, 1.2, 1.5, 1.9, 2.2):
        for k in (0, 1, -1, 2, -2, 3, -3, 4):
            ang = ang0 + k * math.pi / 4
            pos = VECTOR2I(int(c.x + FromMM(d_) * math.cos(ang)), int(c.y + FromMM(d_) * math.sin(ang)))
            if not plane_ok(netname, pos): continue
            if via_collides(pos, 0.6, nc, 0.12) or seg_collides(c, pos, 0.25, lay, nc, 0.1): continue
            add_via(pos, nc, 0.6, 0.3); add_track(c, pos, 0.25, lay, nc)
            return "stitch %.2f" % d_
    return None

def connect_direct(a, b, layer, netcode, width=0.2):
    """reto, depois L (2 variantes)."""
    if seg_collides(a, b, width, layer, netcode) is None:
        add_track(a, b, width, layer, netcode); return "reto"
    for mid in (VECTOR2I(a.x, b.y), VECTOR2I(b.x, a.y)):
        if seg_collides(a, mid, width, layer, netcode) is None and seg_collides(mid, b, width, layer, netcode) is None:
            add_track(a, mid, width, layer, netcode); add_track(mid, b, width, layer, netcode); return "L"
    return None

def nearest_same_net_copper(pos, layer, netcode, exclude_uuid=None, rmax=4.0):
    """ponto mais proximo em trilha/pad da mesma net nessa camada (ja conectado ao resto, idealmente)."""
    best = None
    for t in tracks():
        if t.GetNetCode() != netcode or t.GetClass() != "PCB_TRACK" or t.GetLayer() != layer: continue
        if exclude_uuid and t.m_Uuid.AsString() == exclude_uuid: continue
        for E in (t.GetStart(), t.GetEnd()):
            d_ = dist(E, pos)
            if d_ < rmax and (best is None or d_ < best[0]): best = (d_, E)
    for p in all_pads:
        if p.GetNetCode() != netcode or not p.IsOnLayer(layer): continue
        d_ = dist(p.GetPosition(), pos)
        if d_ < rmax and (best is None or d_ < best[0]): best = (d_, p.GetPosition())
    return best[1] if best else None

def island_items(obj):
    """todos os itens (trilhas/vias/pads) ligados galvanicamente a obj (sem zonas)."""
    conn = board.GetConnectivity(); seen = {}; stack = [obj]
    while stack:
        it = stack.pop(); k = it.m_Uuid.AsString()
        if k in seen: continue
        seen[k] = it
        try:
            stack.extend(conn.GetConnectedTracks(it)); stack.extend(conn.GetConnectedPads(it))
        except Exception: pass
    return list(seen.values())

def island_has_plane(items, netname):
    for it in items:
        if it.GetClass() == "PCB_VIA" and plane_ok(netname, it.GetPosition()): return True
        if it.GetClass() == "PAD" and it.GetDrillSize().x > 0 and plane_ok(netname, it.GetPosition()): return True
    return False

def island_via(obj, netname, nc):
    """via para o plano em qualquer ponto das trilhas (ou perto dos pads) da ilha de obj."""
    items = island_items(obj)
    if island_has_plane(items, netname): return None
    cands = []
    for it in items:
        if it.GetClass() == "PCB_TRACK":
            a, b = it.GetStart(), it.GetEnd(); L = dist(a, b); n = max(1, int(L / 0.4))
            for i in range(n + 1):
                cands.append(VECTOR2I(int(a.x + (b.x - a.x) * i / n), int(a.y + (b.y - a.y) * i / n)))
    for c in cands:
        if plane_ok(netname, c) and try_via_at(c, nc, netname): return "via ilha %s" % (pt(c),)
    for it in items:
        if it.GetClass() == "PAD":
            r = stitch_pad(it, netname)
            if r: return "%s %s.%s (ilha)" % (r, it.GetParentFootprint().GetReference(), it.GetNumber())
    return None

def connect_any(a, la, b, lb, nc, width=0.2):
    """liga ponto a (camada la) ao ponto b (camada lb): direto/L; senao via(s) e trilha na outra camada."""
    if la == lb:
        r = connect_direct(a, b, la, nc, width)
        if r: return r
    other = pcbnew.B_Cu if la == pcbnew.F_Cu else pcbnew.F_Cu
    for d_ in (0.0, 0.6, 0.8, 1.0, 1.3, 1.6):
        for k in range(8 if d_ else 1):
            ang = k * math.pi / 4
            va = VECTOR2I(int(a.x + FromMM(d_) * math.cos(ang)), int(a.y + FromMM(d_) * math.sin(ang)))
            if d_ and seg_collides(a, va, width, la, nc) is not None: continue
            if via_collides(va, 0.6, nc, 0.12): continue
            # lado b: mesma camada da via -> direto; senao segunda via perto de b
            if lb == other:
                if seg_collides(va, b, width, other, nc) is None:
                    add_via(va, nc)
                    if d_: add_track(a, va, width, la, nc)
                    add_track(va, b, width, other, nc); return "via+reto"
                for mid in (VECTOR2I(va.x, b.y), VECTOR2I(b.x, va.y)):
                    if seg_collides(va, mid, width, other, nc) is None and seg_collides(mid, b, width, other, nc) is None:
                        add_via(va, nc)
                        if d_: add_track(a, va, width, la, nc)
                        add_track(va, mid, width, other, nc); add_track(mid, b, width, other, nc); return "via+L"
            else:
                for e_ in (0.0, 0.6, 0.8, 1.0, 1.3):
                    for j in range(8 if e_ else 1):
                        ang2 = j * math.pi / 4
                        vb = VECTOR2I(int(b.x + FromMM(e_) * math.cos(ang2)), int(b.y + FromMM(e_) * math.sin(ang2)))
                        if e_ and seg_collides(b, vb, width, lb, nc) is not None: continue
                        if via_collides(vb, 0.6, nc, 0.12) or dist(va, vb) < 0.7: continue
                        path = None
                        if seg_collides(va, vb, width, other, nc) is None: path = [(va, vb)]
                        else:
                            for mid in (VECTOR2I(va.x, vb.y), VECTOR2I(vb.x, va.y)):
                                if seg_collides(va, mid, width, other, nc) is None and seg_collides(mid, vb, width, other, nc) is None:
                                    path = [(va, mid), (mid, vb)]; break
                        if path is None: continue
                        add_via(va, nc); add_via(vb, nc)
                        if d_: add_track(a, va, width, la, nc)
                        if e_: add_track(b, vb, width, lb, nc)
                        for s, e in path: add_track(s, e, width, other, nc)
                        return "2 vias+%s" % other
    return None

def fix_pair(A, B):
    net = A["net"] or B["net"]
    if net is None or net not in nets: return "net?"
    nc = nets[net].GetNetCode()
    kinds = (A["kind"], B["kind"])
    # D) zona x zona / zona x pad PTH: ilha -> via dentro da ilha tratada em fix_islands
    if kinds == ("zone", "zone"): return "island (ver D)"
    # A0) potencia: via para o plano em qualquer ponto da ilha que ainda nao toca o plano
    if net in ("GND", "+3V3", "+5V"):
        for it in (A, B):
            if it["kind"] in ("pad", "track", "via") and it["obj"] is not None:
                r = island_via(it["obj"], net, nc)
                if r: return r
    # A) pads de potencia
    for it in (A, B):
        if it["kind"] == "pad" and it["obj"] is not None and net in ("GND", "+3V3", "+5V"):
            r = stitch_pad(it["obj"], net)
            if r: return "%s %s.%s" % (r, it["ref"], it["num"])
    # B) trilha(s) com ponta solta -> via na ponta (potencia ou transicao de camada)
    trk = [it for it in (A, B) if it["kind"] == "track" and it["obj"] is not None and not it["obj"].IsLocked()]
    if len(trk) == 2 and A["layer"] != B["layer"]:
        ea, eb = free_ends(A["obj"]), free_ends(B["obj"])
        pairs = sorted(((dist(x, y), x, y) for x in (ea or [A["obj"].GetStart(), A["obj"].GetEnd()]) for y in (eb or [B["obj"].GetStart(), B["obj"].GetEnd()])), key=lambda k: k[0])
        for d_, x, y in pairs:
            if d_ > 1.5: break
            for cand in (x, y, VECTOR2I((x.x + y.x) // 2, (x.y + y.y) // 2)):
                if try_via_at(cand, nc, net):
                    if cand != x: add_track(x, cand, 0.2, A["layer"], nc)
                    if cand != y: add_track(y, cand, 0.2, B["layer"], nc)
                    return "via transicao %s" % (pt(cand),)
    for it in trk:
        t = it["obj"]
        for E in free_ends(t):
            if net in PLANE_NETS or net == "+5V":
                if plane_ok(net, E) and try_via_at(E, nc, net): return "via ponta %s" % (pt(E),)
                # recua ao longo da trilha
                O = t.GetEnd() if E == t.GetStart() else t.GetStart(); L = dist(E, O)
                for back in (0.35, 0.7, 1.0):
                    if back >= L: break
                    P = VECTOR2I(int(E.x + (O.x - E.x) * back / L), int(E.y + (O.y - E.y) * back / L))
                    if plane_ok(net, P) and try_via_at(P, nc, net): return "via recuo %s" % (pt(P),)
    # C) sinal: trilha x pad em camadas diferentes -> via na ponta + trilha ate o pad; mesma camada -> direto
    padit = next((it for it in (A, B) if it["kind"] == "pad" and it["obj"] is not None), None)
    other = B if padit is A else A
    if padit and other["kind"] in ("track", "via") and other["obj"] is not None:
        p = padit["obj"]; play = item_layer(p); pc = p.GetPosition()
        if other["kind"] == "via":
            r = connect_direct(other["pos"], pc, play, nc)
            if r: return "via->pad %s" % r
        else:
            t = other["obj"]
            ends = free_ends(t) or [t.GetStart(), t.GetEnd()]
            if t.GetLayer() == play:
                for E in sorted(ends, key=lambda e: dist(e, pc)):
                    r = connect_direct(E, pc, play, nc)
                    if r: return "trilha->pad %s" % r
            else:
                for E in sorted(ends, key=lambda e: dist(e, pc)):
                    v = try_via_at(E, nc, net)
                    if v:
                        r = connect_direct(E, pc, play, nc)
                        if r: return "via ponta + %s" % r
                        board.RemoveNative(v); added.pop()
    # fallback: ligar cada item ao cobre mais proximo da mesma net na propria camada
    # C2) sinal: pad x pad / pad x trilha com vias e trilha na outra camada
    if net not in ("GND", "+3V3", "+5V"):
        pts = []
        for it in (A, B):
            if it["obj"] is None: continue
            if it["kind"] == "pad": pts.append((it["obj"].GetPosition(), item_layer(it["obj"])))
            elif it["kind"] == "track":
                t = it["obj"]; ends = free_ends(t) or [t.GetStart(), t.GetEnd()]
                pts.append((ends[0], t.GetLayer()))
            elif it["kind"] == "via": pts.append((it["pos"], pcbnew.F_Cu))
        if len(pts) == 2:
            r = connect_any(pts[0][0], pts[0][1], pts[1][0], pts[1][1], nc)
            if r: return "connect_any %s" % r
    for it in (A, B):
        if it["kind"] == "pad" and it["obj"] is not None:
            lay = item_layer(it["obj"]); pc = it["obj"].GetPosition()
            tgt = nearest_same_net_copper(pc, lay, nc)
            if tgt is not None and dist(tgt, pc) > 0.05:
                r = connect_direct(pc, tgt, lay, nc)
                if r: return "pad->cobre %s" % r
        if it["kind"] == "track" and it["obj"] is not None:
            t = it["obj"]
            for E in free_ends(t):
                tgt = nearest_same_net_copper(E, t.GetLayer(), nc, t.m_Uuid.AsString())
                if tgt is not None:
                    r = connect_direct(E, tgt, t.GetLayer(), nc)
                    if r: return "ponta->cobre %s" % r
    return None

def fix_islands():
    """ilhas da zona GND em F.Cu/B.Cu sem via/PTH GND -> via no interior (liga ao plano In2)."""
    gnd = nets["GND"].GetNetCode(); n = 0
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    gvias = [t.GetPosition() for t in tracks() if t.GetClass() == "PCB_VIA" and t.GetNetCode() == gnd]
    gpth = [p.GetPosition() for p in all_pads if p.GetNetCode() == gnd and p.GetDrillSize().x > 0]
    for z in board.Zones():
        if z.GetIsRuleArea() or z.GetNetCode() != gnd: continue
        for lay in (pcbnew.F_Cu, pcbnew.B_Cu):
            if not z.IsOnLayer(lay): continue
            polys = z.GetFilledPolysList(lay)
            for i in range(polys.OutlineCount()):
                ol = polys.Outline(i)
                if ol.Area() < FromMM(1.0) * FromMM(1.0): continue
                if any(ol.PointInside(v) for v in gvias + gpth): continue
                # candidatos: centroide e pontos ao longo do contorno encolhido
                bb = ol.BBox(); cands = [VECTOR2I((bb.GetLeft() + bb.GetRight()) // 2, (bb.GetTop() + bb.GetBottom()) // 2)]
                for k in range(0, ol.PointCount(), max(1, ol.PointCount() // 24)):
                    v = ol.CPoint(k); cands.append(VECTOR2I(int(v.x + (cands[0].x - v.x) * 0.25), int(v.y + (cands[0].y - v.y) * 0.25)))
                for c in cands:
                    if ol.PointInside(c) and via_collides(c, 0.6, gnd, 0.15) is None:
                        add_via(c, gnd, 0.6, 0.3); n += 1; break
    return n

# ---------------------------------------------------------------- ciclo
prev = None
for rnd in range(ROUNDS):
    pcbnew.ZONE_FILLER(board).Fill(board.Zones()); board.BuildConnectivity()
    pcbnew.SaveBoard(PCB, board)
    drc = run_drc()
    unc = drc["unconnected_items"]
    rr = {"round": rnd, "unconnected": len(unc), "fixes": [], "unfixed": []}
    print("round %d: unconnected %d" % (rnd, len(unc)))
    if not unc or DRY: report["rounds"].append(rr); break
    before = len(added)
    for u in unc:
        A, B = parse(u["items"][0]), parse(u["items"][1])
        desc = " <> ".join(i["description"] for i in u["items"])
        try:
            r = fix_pair(A, B)
        except Exception as e:
            r = None; W("exc %s: %s" % (desc, e))
        (rr["fixes"] if r else rr["unfixed"]).append((desc, r) if r else desc)
        print("  ", "OK " if r else "-- ", desc[:110], "->", r)
    ni = fix_islands()
    if ni: rr["fixes"].append(("ilhas GND", "%d vias" % ni)); print("   ilhas GND: %d vias" % ni)
    report["rounds"].append(rr)
    if len(added) == before:
        print("nada mais a fazer"); break
report["added"] = added
pcbnew.ZONE_FILLER(board).Fill(board.Zones()); board.BuildConnectivity()
pcbnew.SaveBoard(PCB, board)
report["unrouted_final"] = board.GetConnectivity().GetUnconnectedCount(True)
with open(REPORT, "w", encoding="utf-8") as f: json.dump(report, f, indent=1, ensure_ascii=False, default=str)
if os.path.exists(DRC_TMP): os.remove(DRC_TMP)
print("unrouted_final:", report["unrouted_final"], "| added:", len(added), "| warnings:", report["warnings"])
