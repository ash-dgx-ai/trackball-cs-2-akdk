#!/usr/bin/env python3
"""Generate JLCPCB-style BOM and CPL CSV files from the routed PCB."""
import csv
import os
from collections import defaultdict
import pcbnew

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(HERE, "controller.kicad_pcb")
BOM = os.path.join(HERE, "jlcpcb_bom.csv")
CPL = os.path.join(HERE, "jlcpcb_cpl.csv")

# J5 is the conthrough pad array (not a purchased part); J4 is a hand-soldered
# SWD header (no LCSC part in the JLCPCB library).
SKIP = {"J5", "J4"}


def main():
    board = pcbnew.LoadBoard(PCB)
    bom_groups = defaultdict(list)
    cpl_rows = []
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref in SKIP:
            continue
        lcsc = fp.GetFieldText("LCSC Part").strip()
        if not lcsc:
            continue
        value = fp.GetValue()
        footprint = fp.GetFPIDAsString()
        bom_groups[(value, footprint, lcsc)].append(ref)
        pos = fp.GetPosition()
        x = pcbnew.ToMM(pos.x)
        y = pcbnew.ToMM(pos.y)
        layer = "Bottom" if fp.GetLayer() == pcbnew.B_Cu else "Top"
        rot = fp.GetOrientationDegrees() % 360.0
        cpl_rows.append((ref, f"{x:.3f}", f"{y:.3f}", layer, f"{rot:.1f}"))

    with open(BOM, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for (value, footprint, lcsc), refs in sorted(bom_groups.items()):
            w.writerow([value, ",".join(sorted(refs)), footprint, lcsc])

    with open(CPL, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        for row in sorted(cpl_rows):
            w.writerow(row)

    print("Saved", BOM, CPL)


if __name__ == "__main__":
    main()
