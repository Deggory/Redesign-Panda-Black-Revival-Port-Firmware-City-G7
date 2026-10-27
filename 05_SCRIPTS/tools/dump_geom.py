import pcbnew, sys, os
from pcbnew import ToMM
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import hp_common as hp
b = pcbnew.LoadBoard(os.path.join(str(hp.OUTPUT_ROOT), "04_PROJECT", "HybridPanda", "HybridPanda.kicad_pcb"))


def near(x, y, r, layer=None):
    for t in b.GetTracks():
        bb = t.GetBoundingBox()
        if abs(ToMM(bb.GetCenter().x) - x) < r and abs(ToMM(bb.GetCenter().y) - y) < r:
            if t.GetClass() == "PCB_VIA":
                print("  VIA %s (%.3f,%.3f) d=%.2f/%.2f" % (t.GetNetname(), ToMM(t.GetPosition().x), ToMM(t.GetPosition().y), ToMM(t.GetWidth()), ToMM(t.GetDrillValue())))
            else:
                if layer and b.GetLayerName(t.GetLayer()) != layer:
                    continue
                print("  TRK %s %s (%.3f,%.3f)->(%.3f,%.3f) w=%.2f" % (t.GetNetname(), b.GetLayerName(t.GetLayer()), ToMM(t.GetStart().x), ToMM(t.GetStart().y), ToMM(t.GetEnd().x), ToMM(t.GetEnd().y), ToMM(t.GetWidth())))


def fpinfo(ref):
    fp = b.FindFootprintByReference(ref)
    print(ref, "(%.3f,%.3f) rot %.0f %s %s" % (ToMM(fp.GetPosition().x), ToMM(fp.GetPosition().y), fp.GetOrientationDegrees(), b.GetLayerName(fp.GetLayer()), fp.GetFPID().GetUniStringLibId()))
    for p in fp.Pads():
        s = p.GetSize(pcbnew.PADSTACK.ALL_LAYERS)
        print("   pad %s [%s] (%.3f,%.3f) %.2fx%.2f" % (p.GetNumber(), p.GetNetname(), ToMM(p.GetPosition().x), ToMM(p.GetPosition().y), ToMM(s.x), ToMM(s.y)))
    cy = fp.GetCourtyard(pcbnew.F_CrtYd if not fp.IsFlipped() else pcbnew.B_CrtYd).BBox()
    print("   crtyd (%.3f,%.3f)-(%.3f,%.3f)" % (ToMM(cy.GetLeft()), ToMM(cy.GetTop()), ToMM(cy.GetRight()), ToMM(cy.GetBottom())))
    r = fp.Reference()
    print("   ref vis=%s (%.2f,%.2f) size=%.2f layer=%s" % (r.IsVisible(), ToMM(r.GetPosition().x), ToMM(r.GetPosition().y), ToMM(r.GetTextHeight()), b.GetLayerName(r.GetLayer())))


if __name__ == "__main__":
    for a in sys.argv[1:]:
        if a.startswith("near:"):
            x, y, r = [float(v) for v in a[5:].split(",")]
            print("tracks near", x, y)
            near(x, y, r)
        else:
            fpinfo(a)
