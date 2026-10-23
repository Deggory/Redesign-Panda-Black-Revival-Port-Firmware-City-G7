# -*- coding: utf-8 -*-
"""
STEP 5b - roteamento do HybridPanda (H725 em B.Cu).

Fases:
  N  netclasses no .kicad_pro (CAN_DIFF para BUS*_H/_L, USB para USB_D*/USB_R_D*)
  Z  estende a zona +3V3 (In1.Cu) para cobrir a área do U7
  C  trilhas críticas diretas (mesma camada, sem via): VCAP, HSE, SMPS, VDDA, desacoplamento B.Cu
  V  vias GND / +3V3 junto aos pads dos capacitores de suporte
  L  trava (lock) trilhas do baseline em BUS*_H/_L + tudo criado aqui
  X  exporta DSN -> Freerouting (Java 25) -> importa SES
  F  refill de zonas, salva, relatório 06_REPORTS/step5b_route.json

Uso:  python step5b_route.py [--no-freerouting]
Idempotente: parte de HybridPanda.kicad_pcb.step5a (criado na 1ª execução a partir do PCB atual).
"""
import json, os, shutil, subprocess, sys, time, re
import pcbnew
from pcbnew import VECTOR2I, FromMM, ToMM

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(ROOT, "04_PROJECT", "HybridPanda", "HybridPanda.kicad_pcb")
PRO = os.path.join(ROOT, "04_PROJECT", "HybridPanda", "HybridPanda.kicad_pro")
SNAP = PCB + ".step5a"
DSN = os.path.join(ROOT, "06_REPORTS", "HybridPanda_step5b.dsn")
SES = os.path.join(ROOT, "06_REPORTS", "HybridPanda_step5b.ses")
REPORT = os.path.join(ROOT, "06_REPORTS", "step5b_route.json")
JAVA = r"C:\Program Files\Java\jdk-25.0.4.1\bin\java.exe"
FR_JAR = os.path.join(ROOT, "05_SCRIPTS", "tools", "freerouting", "freerouting-2.5.0.jar")
NO_FR = "--no-freerouting" in sys.argv
FR_PASSES = int(sys.argv[sys.argv.index("--passes") + 1]) if "--passes" in sys.argv else 60

report = {"phases": {}, "warnings": []}
W = report["warnings"].append

# ---------------------------------------------------------------- N: netclasses
with open(PRO, encoding="utf-8") as f:
    pro = json.load(f)
classes = pro["net_settings"]["classes"]
names = [c["name"] for c in classes]
default = next(c for c in classes if c["name"] == "Default")
if "CAN_DIFF" not in names:
    classes.append(dict(default))
if True:
    c = classes[-1] if classes[-1].get("name") == "CAN_DIFF" else next(c for c in classes if c["name"] == "CAN_DIFF")
    c.update({"name": "CAN_DIFF", "track_width": 0.25, "clearance": 0.1,
              "diff_pair_width": 0.25, "diff_pair_gap": 0.2, "diff_pair_via_gap": 0.25,
              "via_diameter": 0.7, "via_drill": 0.3, "priority": 0})
usb = next(c for c in classes if c["name"] == "USB")
# baseline tinha 0.05 mm (abaixo do min_track_width 0.1375) -> alinha com Default
if usb["track_width"] < 0.1375:
    report["phases"]["N_usb_fixed_from"] = usb["track_width"]
    usb["track_width"] = 0.2; usb["clearance"] = 0.1
usb["via_diameter"] = 0.7; usb["via_drill"] = 0.3
default["via_diameter"] = 0.7; default["via_drill"] = 0.3
rules = pro["board"]["design_settings"]["rules"]
rules["allow_blind_buried_vias"] = False; rules["allow_microvias"] = False
rules["min_through_hole_diameter"] = 0.3; rules["min_via_diameter"] = 0.4
pats = pro["net_settings"].setdefault("netclass_patterns", [])
have = {(p["netclass"], p["pattern"]) for p in pats}
for pat in ("BUS0_H", "BUS0_L", "BUS1N_H", "BUS1N_L", "BUS1O_H", "BUS1O_L", "BUS2_H", "BUS2_L"):
    if ("CAN_DIFF", pat) not in have: pats.append({"netclass": "CAN_DIFF", "pattern": pat})
for pat in ("USB_D+", "USB_D-", "USB_R_D+", "USB_R_D-"):
    if ("USB", pat) not in have: pats.append({"netclass": "USB", "pattern": pat})
with open(PRO, "w", encoding="utf-8") as f:
    json.dump(pro, f, indent=2, ensure_ascii=False)
report["phases"]["N"] = {"classes": [c["name"] for c in classes], "patterns": len(pats)}

# ---------------------------------------------------------------- load (snapshot idempotente)
if not os.path.exists(SNAP):
    shutil.copy2(PCB, SNAP)
else:
    shutil.copy2(SNAP, PCB)
board = pcbnew.LoadBoard(PCB)
ds = board.GetDesignSettings()
ds.m_BlindBuriedViaAllowed = False; ds.m_MicroViasAllowed = False
ds.m_MinThroughDrill = FromMM(0.3); ds.m_ViasMinSize = FromMM(0.4)
fps = {f.GetReference(): f for f in board.GetFootprints()}
u7 = fps["U7"]
u7c = u7.GetPosition()
nets = board.GetNetsByName()
def net(n): return nets[n]

def mm(v): return VECTOR2I(FromMM(v[0]), FromMM(v[1]))
def pt(p): return (round(ToMM(p.x), 3), round(ToMM(p.y), 3))

# ---------------------------------------------------------------- Z: zona +3V3 In1 sob o MCU
z3 = [z for z in board.Zones() if z.GetNetname() == "+3V3" and z.IsOnLayer(pcbnew.In1_Cu)]
if z3:
    z = z3[0]
    poly = pcbnew.SHAPE_POLY_SET()
    poly.NewOutline()
    # faixa antiga (96.1-101 x 38.7-64.3) + bloco sob o U7, abaixo das zonas +5V In1 (y<=47.4)
    for v in [(96.1, 38.7), (101.0, 38.7), (101.0, 47.6), (123.5, 47.6), (123.5, 71.5), (96.1, 71.5)]:
        poly.Append(mm(v))
    z.SetOutline(poly)
    report["phases"]["Z"] = {"+3V3_In1_outline": [(96.1, 38.7), (101.0, 38.7), (101.0, 47.6), (123.5, 47.6), (123.5, 71.5), (96.1, 71.5)]}
else:
    W("zona +3V3 In1 não encontrada")

# ---------------------------------------------------------------- limpeza: fragmentos do baseline sem via/pad (sobras do STEP 5a)
def _touch(pt, layer, it, me):
    if it.m_Uuid.AsString() == me.m_Uuid.AsString(): return False
    if it.GetClass() == "PCB_VIA": return it.GetPosition() == pt
    if it.GetClass() in ("PCB_TRACK", "PCB_ARC"): return it.GetLayer() == layer and (it.GetStart() == pt or it.GetEnd() == pt)
    return it.IsOnLayer(layer) and it.HitTest(pt)
frag_removed = 0
_seen = set()
for t in list(board.GetTracks()):
    if t.IsLocked(): continue
    key = (t.GetNetCode(), t.GetLayer(), t.GetClass()) + tuple(sorted([(t.GetStart().x, t.GetStart().y), (t.GetEnd().x, t.GetEnd().y)])) if t.GetClass() != "PCB_VIA" else (t.GetNetCode(), "V", t.GetPosition().x, t.GetPosition().y)
    if key in _seen: board.RemoveNative(t); frag_removed += 1
    else: _seen.add(key)
report["phases"]["cleanup_duplicates_removed"] = frag_removed
frag_removed = 0
for _ in range(30):
    dirty = False
    pads_by_net = {}
    for f in board.GetFootprints():
        for p in f.Pads(): pads_by_net.setdefault(p.GetNetCode(), []).append(p)
    trk_by_net = {}
    for t in board.GetTracks(): trk_by_net.setdefault(t.GetNetCode(), []).append(t)
    for t in list(board.GetTracks()):
        if t.IsLocked() or t.GetClass() == "PCB_VIA" or re.match(r"BUS\w+_[HL]$", t.GetNetname()): continue
        items = trk_by_net.get(t.GetNetCode(), []) + pads_by_net.get(t.GetNetCode(), [])
        if not (any(_touch(t.GetStart(), t.GetLayer(), i, t) for i in items) and any(_touch(t.GetEnd(), t.GetLayer(), i, t) for i in items)):
            board.RemoveNative(t); frag_removed += 1; dirty = True
    for t in list(board.GetTracks()):
        if t.IsLocked() or t.GetClass() != "PCB_VIA": continue
        items = [i for i in trk_by_net.get(t.GetNetCode(), []) if i.GetClass() != "PCB_VIA"]
        att = sum(1 for i in items if i.GetStart() == t.GetPosition() or i.GetEnd() == t.GetPosition())
        if att == 0 and not any(p.HitTest(t.GetPosition()) for p in pads_by_net.get(t.GetNetCode(), [])):
            board.RemoveNative(t); frag_removed += 1; dirty = True
    if not dirty: break
report["phases"]["cleanup_fragments_removed"] = frag_removed

# ---------------------------------------------------------------- helpers de colisão
all_pads = [p for f in board.GetFootprints() for p in f.Pads()]
base_tracks = list(board.GetTracks())

def seg_collides(a, b, width, layer, netcode, clearance=0.12):
    shp = pcbnew.SHAPE_SEGMENT(a, b, FromMM(width))
    for z in KEEPOUTS:
        # keepout só vale na própria camada (os do SW1 são F.Cu-only)
        if z.GetDoNotAllowTracks() and z.IsOnLayer(layer) and z.Outline().Collide(shp, FromMM(0.1)): return "keepout"
    for p in all_pads:
        if p.GetNetCode() == netcode or not p.IsOnLayer(layer): continue
        if p.GetEffectiveShape(layer).Collide(shp, FromMM(clearance)): return "pad %s.%s" % (p.GetParentFootprint().GetReference(), p.GetNumber())
    for t in base_tracks + new_items:
        if t.GetNetCode() == netcode or not t.IsOnLayer(layer): continue
        if t.GetEffectiveShape(layer).Collide(shp, FromMM(clearance)): return "track %s" % t.GetNetname()
    return None

KEEPOUTS = [z for z in board.Zones() if z.GetIsRuleArea()] + [z for fp in board.GetFootprints() for z in fp.Zones() if z.GetIsRuleArea()]
def via_collides(pos, dia, netcode, clearance=0.15):
    shp = pcbnew.SHAPE_CIRCLE(pos, FromMM(dia / 2))
    for z in KEEPOUTS:
        if z.GetDoNotAllowVias() and z.Outline().Collide(shp, FromMM(clearance)): return "keepout"
    for p in all_pads:
        if p.GetNetCode() == netcode: continue
        for l in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu):
            if p.IsOnLayer(l) and p.GetEffectiveShape(l).Collide(shp, FromMM(clearance)): return "pad %s.%s" % (p.GetParentFootprint().GetReference(), p.GetNumber())
    for t in base_tracks + new_items:
        if t.GetNetCode() == netcode: continue
        if t.GetClass() == "PCB_VIA" or True:
            for l in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu):
                if t.IsOnLayer(l) and t.GetEffectiveShape(l).Collide(shp, FromMM(clearance)): return "track %s" % t.GetNetname()
    return None

new_items = []
def add_track(a, b, width, layer, netcode):
    for t in new_items:  # dedupe
        if t.GetClass() == "PCB_TRACK" and t.GetLayer() == layer and {(t.GetStart().x, t.GetStart().y), (t.GetEnd().x, t.GetEnd().y)} == {(a.x, a.y), (b.x, b.y)}:
            return t
    t = pcbnew.PCB_TRACK(board); t.SetStart(a); t.SetEnd(b); t.SetWidth(FromMM(width)); t.SetLayer(layer); t.SetNetCode(netcode); t.SetLocked(True)
    board.Add(t); new_items.append(t); return t
def add_via(pos, netcode, dia=0.7, drill=0.3):
    v = pcbnew.PCB_VIA(board); v.SetPosition(pos); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetWidth(FromMM(dia)); v.SetDrill(FromMM(drill))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNetCode(netcode); v.SetLocked(True)
    board.Add(v); new_items.append(v); return v

def pad(ref, num):
    p = fps[ref].FindPadByNumber(str(num))
    if p is None: raise KeyError("%s.%s" % (ref, num))
    return p

# ---------------------------------------------------------------- C: trilhas críticas diretas
CRIT = [  # (cap ref, cap pad, U7 pin, width)
    ("C39", 1, 68, 0.3), ("C40", 1, 140, 0.3),            # VCAP
    ("Y1", 1, 25, 0.2), ("Y1", 3, 26, 0.2),               # HSE
    ("C23", 1, 25, 0.2), ("C24", 1, 26, 0.2),             # HSE load caps
    ("L5", 1, 15, 0.3), ("C41", 1, 15, 0.3), ("C42", 1, 17, 0.25),  # SMPS
    ("C44", 1, 36, 0.2), ("C43", 1, 35, 0.2), ("FB1", 1, 36, 0.2),  # VDDA
    ("C38", 1, 27, 0.2),                                  # NRST
]
for r in range(45, 64):
    pass
dec_pins = {"C45": 7, "C46": 13, "C47": 19, "C48": 32, "C49": 42, "C50": 56, "C51": 71, "C52": 79, "C53": 92, "C54": 106,
            "C55": 119, "C56": 129, "C57": 144, "C58": 91, "C59": 90, "C60": 7, "C61": 56, "C62": 106, "C63": 8}
for ref, pin in dec_pins.items():
    CRIT.append((ref, 1, pin, 0.2))

routed, skipped = [], []
for ref, cp, pin, w in CRIT:
    if ref not in fps: skipped.append((ref, "ausente")); continue
    a_pad, b_pad = pad(ref, cp), pad("U7", pin)
    if a_pad.GetNetCode() != b_pad.GetNetCode():
        skipped.append((ref, "net diferente %s vs %s" % (a_pad.GetNetname(), b_pad.GetNetname()))); continue
    if not a_pad.IsOnLayer(pcbnew.B_Cu):
        skipped.append((ref, "em F.Cu -> Freerouting")); continue
    a, b = a_pad.GetPosition(), b_pad.GetPosition()
    nc = a_pad.GetNetCode()
    # tenta reto; senão L (dois segmentos, saindo do pino na direção do seu eixo)
    hit = seg_collides(a, b, w, pcbnew.B_Cu, nc)
    if hit is None:
        add_track(a, b, w, pcbnew.B_Cu, nc); routed.append((ref, pin, "reto", round(ToMM((a - b).EuclideanNorm()), 2)))
        continue
    ok = False
    for mid in (VECTOR2I(a.x, b.y), VECTOR2I(b.x, a.y)):
        if seg_collides(a, mid, w, pcbnew.B_Cu, nc) is None and seg_collides(mid, b, w, pcbnew.B_Cu, nc) is None:
            add_track(a, mid, w, pcbnew.B_Cu, nc); add_track(mid, b, w, pcbnew.B_Cu, nc)
            routed.append((ref, pin, "L", round(ToMM((a - mid).EuclideanNorm() + (mid - b).EuclideanNorm()), 2))); ok = True; break
    if not ok:
        # escape: sai do pino perpendicular à fileira (afastando do centro do U7), depois dobra até o pad
        import math
        d = VECTOR2I(b.x - u7c.x, b.y - u7c.y)
        ax = (1, 0) if abs(d.x) > abs(d.y) else (0, 1)
        sg = 1 if (d.x if ax[0] else d.y) > 0 else -1
        for e in (0.9, 1.2, 1.5, 1.9, 2.4, 3.0, 3.6):
            m1 = VECTOR2I(b.x + int(FromMM(e) * ax[0] * sg), b.y + int(FromMM(e) * ax[1] * sg))
            for m2 in (VECTOR2I(a.x, m1.y), VECTOR2I(m1.x, a.y)):
                segs = [(b, m1), (m1, m2), (m2, a)]
                if all(seg_collides(s, t, w, pcbnew.B_Cu, nc) is None for s, t in segs):
                    for s, t in segs:
                        if s != t: add_track(s, t, w, pcbnew.B_Cu, nc)
                    L = sum(ToMM((s - t).EuclideanNorm()) for s, t in segs)
                    routed.append((ref, pin, "escape%.1f" % e, round(L, 2))); ok = True; break
            if ok: break
    if not ok: skipped.append((ref, "colisão: %s" % hit))

# cristal: terminal diagonal (Y1.1) contorna o próprio pad GND pelo lado do C23, no corredor Y1.4 <-> C23.2
if ("Y1", "colisão: pad Y1.4") in skipped:
    a = pad("Y1", 1).GetPosition(); nc = pad("Y1", 1).GetNetCode()
    y1bb = fps["Y1"].GetBoundingBox(False, False); c23bb = fps["C23"].GetBoundingBox(False, False)
    xg = (max(y1bb.GetRight(), pad("Y1", 4).GetBoundingBox().GetRight()) + c23bb.GetLeft()) // 2
    hse = [t for t in new_items if t.GetNetCode() == nc and t.GetClass() == "PCB_TRACK" and t.GetStart().y == t.GetEnd().y]
    if hse:
        yj = hse[0].GetStart().y
        m1, m2 = VECTOR2I(xg, a.y), VECTOR2I(xg, yj)
        if all(seg_collides(s, t, 0.2, pcbnew.B_Cu, nc) is None for s, t in ((a, m1), (m1, m2))):
            add_track(a, m1, 0.2, pcbnew.B_Cu, nc); add_track(m1, m2, 0.2, pcbnew.B_Cu, nc)
            skipped.remove(("Y1", "colisão: pad Y1.4"))
            routed.append(("Y1", 25, "contorno x=%.2f" % ToMM(xg), round(ToMM((a - m1).EuclideanNorm() + (m1 - m2).EuclideanNorm()), 2)))
        else: W("Y1.1 contorno colide")
report["phases"]["C"] = {"routed": routed, "skipped_to_freerouting": skipped}

# ---------------------------------------------------------------- V: vias GND/+3V3 nos caps de suporte
def stitch_via(p, netname, label):
    """via a ~0.75 mm do pad, do lado oposto ao centro do U7; tenta 8 direções."""
    nc = net(netname).GetNetCode()
    if p.GetNetCode() != nc: return (label, "net %s != %s" % (p.GetNetname(), netname))
    c = p.GetPosition()
    d = VECTOR2I(c.x - u7c.x, c.y - u7c.y)
    import math
    ang0 = math.atan2(d.y, d.x)
    for k in (0, 1, -1, 2, -2, 3, -3, 4):
        ang = ang0 + k * math.pi / 4
        for dist in (0.75, 0.95, 1.2, 1.5, 1.9):
            pos = VECTOR2I(int(c.x + FromMM(dist) * math.cos(ang)), int(c.y + FromMM(dist) * math.sin(ang)))
            if via_collides(pos, 0.7, nc): continue
            lay = pcbnew.B_Cu if p.IsOnLayer(pcbnew.B_Cu) and not p.IsOnLayer(pcbnew.F_Cu) else pcbnew.F_Cu
            if seg_collides(c, pos, 0.25, lay, nc, 0.1): continue
            add_via(pos, nc); add_track(c, pos, 0.25, lay, nc)
            return (label, "ok", pt(pos))
    return (label, "sem espaço")

# vias GND de escape para os pinos GND do U7 (pitch 0.5 mm não permite spoke térmico da zona)
import math
U7_GND = [6, 12, 14, 18, 21, 22, 23, 24, 33, 34, 41, 55, 69, 80, 89, 104, 118, 128, 141]
gnd_nc = net("GND").GetNetCode(); u7v = []; U7_GND_REASONS = {}
# grupos de pinos GND consecutivos: uma ponte na ponta dos pads + uma via só
GND_GROUPS = {21: [21, 22, 23, 24], 22: None, 23: None, 24: None}
def _axis(c):
    d = VECTOR2I(c.x - u7c.x, c.y - u7c.y)
    ax = (1, 0) if abs(d.x) > abs(d.y) else (0, 1)
    return ax, (1 if (d.x if ax[0] else d.y) > 0 else -1)
def _off(c, ax, sg, along, lat):
    return VECTOR2I(c.x + int(FromMM(along) * ax[0] * sg + FromMM(lat) * -ax[1]), c.y + int(FromMM(along) * ax[1] * sg + FromMM(lat) * ax[0]))
def _try_gnd(pin, group, ax, sg, knee_d, dists, tag):
    """tenta knee+via na direção sg (+1 = para fora do U7, -1 = por baixo do corpo, em B.Cu)."""
    knees = [_off(pad("U7", g).GetPosition(), ax, sg, knee_d, 0) for g in group]
    pre = [(pad("U7", g).GetPosition(), k) for g, k in zip(group, knees)]
    if len(group) > 1: pre.append((knees[0], knees[-1]))  # ponte entre as pontas
    hp = [seg_collides(s, t, 0.25, pcbnew.B_Cu, gnd_nc, 0.1) for s, t in pre]
    if any(hp):
        U7_GND_REASONS.setdefault(pin, {})["%s ponte" % tag] = [h for h in hp if h]; return None
    for dist in dists:
        for lat in (0, 0.25, -0.25, 0.5, -0.5, 0.75, -0.75, 1.0, -1.0):
            for k in knees:  # a via pode sair de qualquer pino do grupo
                pos = _off(k, ax, sg, dist - knee_d, lat)
                hv = via_collides(pos, 0.6, gnd_nc, 0.12) or seg_collides(k, pos, 0.25, pcbnew.B_Cu, gnd_nc, 0.1)
                if hv: U7_GND_REASONS.setdefault(pin, {}); U7_GND_REASONS[pin][hv] = U7_GND_REASONS[pin].get(hv, 0) + 1; continue
                for s, t in pre: add_track(s, t, 0.25, pcbnew.B_Cu, gnd_nc)
                add_via(pos, gnd_nc, 0.6, 0.3); add_track(k, pos, 0.25, pcbnew.B_Cu, gnd_nc)
                return (pin if len(group) == 1 else "+".join(map(str, group)), tag, dist, lat)
    return None
for i, pin in enumerate(U7_GND):
    if GND_GROUPS.get(pin, 0) is None: continue  # coberto pela ponte do grupo
    c = pad("U7", pin).GetPosition()
    ax, sg = _axis(c)
    group = GND_GROUPS.get(pin) or [pin]
    dists = (1.2, 1.5, 1.8, 2.2, 2.6, 3.0, 3.5) if i % 2 == 0 else (1.5, 1.2, 1.8, 2.2, 2.6, 3.0, 3.5)
    r = _try_gnd(pin, group, ax, sg, 0.9, dists, "fora")
    # fallback: via sob o corpo do LQFP (lado B.Cu, sem componentes), ponta interna dos pads em ~0.74 mm
    if r is None: r = _try_gnd(pin, group, ax, -sg, 0.9, (1.4, 1.7, 2.0, 2.4, 2.8), "dentro")
    if r is None: r = _try_gnd(pin, group, ax, -sg, 0.6, (1.4, 1.7, 2.0, 2.4, 2.8), "dentro-k0.6")
    u7v.append(r if r else (pin, "sem espaço"))
U7_GND_RESULT = u7v
vias = []
GND_PADS = [("C39", 2), ("C40", 2), ("C23", 2), ("C24", 2), ("Y1", 2), ("Y1", 4), ("C41", 2), ("C42", 2), ("C43", 2), ("C44", 2), ("C38", 2)]
GND_PADS += [(r, 2) for r in dec_pins]
for ref, n in GND_PADS:
    if ref in fps: vias.append(stitch_via(pad(ref, n), "GND", "%s.%s" % (ref, n)))
# +3V3: pad 1 dos desacoplamentos + FB1.2 (entrada do filtro VDDA) + VCAP não (é VCAP)
for ref in list(dec_pins) + ["FB1"]:
    if ref in fps:
        p = pad(ref, 2 if ref == "FB1" else 1)
        if p.GetNetname() == "+3V3": vias.append(stitch_via(p, "+3V3", "%s.%s" % (ref, p.GetNumber())))
report["phases"]["V"] = {"ok": sum(1 for v in vias if v[1] == "ok"), "detail": vias, "u7_gnd_vias": U7_GND_RESULT, "u7_gnd_fail_reasons": U7_GND_REASONS}


# ---------------------------------------------------------------- L: travar trilhas baseline CAN H/L (sem via, F.Cu)
can_locked = 0; can_vias = []
for t in base_tracks:
    nn = t.GetNetname()
    if re.match(r"BUS\w+_[HL]$", nn):
        t.SetLocked(True); can_locked += 1
        if t.GetClass() == "PCB_VIA": can_vias.append((nn, pt(t.GetPosition())))
# trava TODO o baseline antes do DSN: o export marca trilhas como "protect" mas vias destravadas como "route",
# e o Freerouting então realoca vias deixando trilhas protegidas sem transição de camada
base_unlocked = [t for t in base_tracks if not t.IsLocked()]
for t in base_unlocked: t.SetLocked(True)
report["phases"]["L"] = {"can_tracks_locked": can_locked, "can_vias_baseline": can_vias, "baseline_items_temp_locked": len(base_unlocked)}
if can_vias: W("LAYOUT_CONFLICT candidato: vias em BUS*_H/_L herdadas do baseline (protocolo 0x05: CAN só F.Cu)")

pcbnew.SaveBoard(PCB, board)

# ---------------------------------------------------------------- X: Freerouting
def count_unrouted(b):
    b.BuildConnectivity(); return b.GetConnectivity().GetUnconnectedCount(True)
report["phases"]["X"] = {"unrouted_before": count_unrouted(board)}
if not NO_FR:
    # DSN de uma cópia sem zonas de potência (Freerouting trataria +3V3/+5V como plano e omitiria vias);
    # exportado em subprocesso porque LoadBoard só funciona uma vez por processo.
    helper = r'''
import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1])
for z in list(b.Zones()):
    if not z.GetIsRuleArea() and z.GetNetname() != "GND": b.RemoveNative(z)
print("DSN", pcbnew.ExportSpecctraDSN(b, sys.argv[2]))
'''
    hp = os.path.join(ROOT, "06_REPORTS", "_dsn_export_helper.py")
    with open(hp, "w", encoding="utf-8") as f: f.write(helper)
    r0 = subprocess.run([sys.executable, hp, PCB, DSN], capture_output=True, text=True, timeout=600)
    os.remove(hp)
    report["phases"]["X"]["dsn_exported"] = "DSN True" in r0.stdout
    with open(DSN, encoding="utf-8") as f: dsn = f.read()
    dsn2 = re.sub(r'(\(via(?: "Via\[0-3\]_\d+:\d+_um")+\))', lambda m: m.group(1).replace(' "Via[0-3]_450:250_um"', ''), dsn, count=1)
    report["phases"]["X"]["dsn_small_via_removed"] = dsn2 != dsn
    with open(DSN, "w", encoding="utf-8") as f: f.write(dsn2)
    cmd = [JAVA, "-jar", FR_JAR, "-l", "en", "--gui.enabled=false", "-de", DSN, "-do", SES,
           "--router.autorouter.max_passes=%d" % FR_PASSES, "--router.plane_nets=GND", "--router.via_costs=80", "--router.automatic_neckdown=false", "--router.result_json=" + os.path.join(ROOT, "06_REPORTS", "step5b_fr_result.json")]
    t0 = time.time()
    if os.path.exists(SES): os.remove(SES)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600, cwd=os.path.dirname(DSN))
    report["phases"]["X"]["freerouting_rc"] = r.returncode
    report["phases"]["X"]["freerouting_s"] = round(time.time() - t0, 1)
    log = (r.stdout + r.stderr)
    with open(os.path.join(ROOT, "06_REPORTS", "step5b_freerouting.log"), "w", encoding="utf-8") as f: f.write(log)
    report["phases"]["X"]["freerouting_tail"] = log.strip().splitlines()[-8:]
    if os.path.exists(SES):
        ok = pcbnew.ImportSpecctraSES(board, SES)
        report["phases"]["X"]["ses_imported"] = bool(ok)
    else:
        W("Freerouting não gerou SES")

# destrava o baseline (mantém travados só os itens críticos criados aqui e CAN H/L)
for t in base_unlocked:
    if not re.match(r"BUS\w+_[HL]$", t.GetNetname()): t.SetLocked(False)

# ---------------------------------------------------------------- F: refill + salvar
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
board.BuildConnectivity()
report["phases"]["F"] = {"unrouted_after": count_unrouted(board),
                         "tracks": sum(1 for t in board.GetTracks() if t.GetClass() == "PCB_TRACK"),
                         "vias": sum(1 for t in board.GetTracks() if t.GetClass() == "PCB_VIA")}
pcbnew.SaveBoard(PCB, board)
with open(REPORT, "w", encoding="utf-8") as f: json.dump(report, f, indent=1, ensure_ascii=False, default=str)
print(json.dumps({k: v for k, v in report["phases"].items() if k != "V"}, ensure_ascii=False, default=str, indent=1))
print("V ok:", report["phases"]["V"]["ok"], "/", len(vias), [v for v in vias if v[1] != "ok"])
print("warnings:", report["warnings"])
