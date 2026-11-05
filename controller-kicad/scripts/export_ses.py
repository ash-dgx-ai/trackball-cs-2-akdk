#!/usr/bin/env python3
"""Write a Specctra SES session from the routed board.

Freerouting is not deterministic; this lets a verified routing be frozen as
`controller.ses` and re-imported on a clean rebuild.  GND is excluded (it is
handled by the copper pours and stitching vias).
"""
import os
import pcbnew

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(HERE, "controller.kicad_pcb")
SES = os.path.join(HERE, "controller.ses")


def mm(v):
    return pcbnew.ToMM(v)


def ses_xy(x, y):
    return int(round(x * 10000)), int(round(-y * 10000))


def via_name(v):
    d = int(round(mm(v.GetWidth(pcbnew.F_Cu)) * 1000))
    drill = int(round(mm(v.GetDrillValue()) * 1000))
    return "Via[0-1]_%d:%d_um" % (d, drill)


def main():
    board = pcbnew.LoadBoard(PCB)

    # Placement block: SES uses 0.1 um units and negated Y.  Rotation is the
    # negative of the KiCad footprint angle (bottom-side convention used by
    # the Freerouting sessions this project has produced).
    groups = {}
    for fp in board.GetFootprints():
        name = str(fp.GetFPID().GetLibItemName())
        p = fp.GetPosition()
        x, y = ses_xy(mm(p.x), mm(p.y))
        side = "back" if fp.GetLayer() == pcbnew.B_Cu else "front"
        if side == "back":
            rot = int(round((fp.GetOrientationDegrees() - 180.0) % 360.0))
        else:
            rot = int(round(fp.GetOrientationDegrees() % 360.0))
        groups.setdefault(name, []).append((fp.GetReference(), x, y, side, rot))

    padstacks = {}
    nets = {}
    for t in board.Tracks():
        name = t.GetNetname()
        if not name or name == "GND":
            continue
        nets.setdefault(name, {"wires": [], "vias": []})
        if t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            x, y = ses_xy(mm(p.x), mm(p.y))
            vname = via_name(t)
            padstacks[vname] = int(round(mm(t.GetWidth(pcbnew.F_Cu)) * 10000))
            nets[name]["vias"].append((vname, x, y))
        else:
            s, e = t.GetStart(), t.GetEnd()
            x1, y1 = ses_xy(mm(s.x), mm(s.y))
            x2, y2 = ses_xy(mm(e.x), mm(e.y))
            width = int(round(mm(t.GetWidth()) * 10000))
            layer = "F.Cu" if t.GetLayer() == pcbnew.F_Cu else "B.Cu"
            nets[name]["wires"].append((layer, width, x1, y1, x2, y2))

    out = ["(session controller", "  (base_design controller)", "  (placement",
           "    (resolution um 10)"]
    for name in sorted(groups):
        out.append('    (component "%s"' % name)
        for ref, x, y, side, rot in groups[name]:
            out.append("      (place %s %d %d %s %d)" % (ref, x, y, side, rot))
        out.append("    )")
    out.append("  )")
    out.append("  (routes ")
    out.append("    (resolution um 10)")
    out.append("    (parser")
    out.append('      (host_cad "KiCad\'s Pcbnew")')
    out.append('      (host_version "9.0.8")')
    out.append("    )")
    out.append("    (library_out ")
    for vname in sorted(padstacks):
        dia = padstacks[vname]
        out.append('      (padstack "%s"' % vname)
        out.append("        (shape")
        out.append("          (circle F.Cu %d 0 0)" % dia)
        out.append("        )")
        out.append("        (shape")
        out.append("          (circle B.Cu %d 0 0)" % dia)
        out.append("        )")
        out.append("        (attach off)")
        out.append("      )")
    out.append("    )")
    out.append("    (network_out ")
    for name in sorted(nets):
        out.append("      (net %s" % name)
        for layer, width, x1, y1, x2, y2 in nets[name]["wires"]:
            out.append("        (wire")
            out.append("          (path %s %d" % (layer, width))
            out.append("            %d %d" % (x1, y1))
            out.append("            %d %d" % (x2, y2))
            out.append("          )")
            out.append("        )")
        for vname, x, y in nets[name]["vias"]:
            out.append('        (via "%s" %d %d)' % (vname, x, y))
        out.append("      )")
    out.append("    )")
    out.append("  )")
    out.append(")")
    open(SES, "w").write("\n".join(out) + "\n")
    print("wrote", SES, "nets", len(nets))


if __name__ == "__main__":
    main()
