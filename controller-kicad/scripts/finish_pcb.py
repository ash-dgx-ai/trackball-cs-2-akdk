#!/usr/bin/env python3
"""Import the Freerouting session, restore GND, add copper pours and keepout.

Run with the KiCad AppImage Python:
  /home/fum198/.local/opt/squashfs-root/bin/python3.11 scripts/finish_pcb.py
"""
import os
import pcbnew

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(HERE, "controller.kicad_pcb")
SES = os.path.join(HERE, "controller.ses")
MM = pcbnew.FromMM
V = pcbnew.VECTOR2I_MM

GND_PADS = {
    "J1": ["A1B12", "B1A12", "1", "2", "3", "4"],
    "U1": ["5", "21", "24"],
    "U2": ["2"],
    "J2": ["2"],
    "SW1": ["6"],
    "J3": ["1", "7", "8"],
    "J4": ["3", "5", "9"],
    "R1": ["2"], "R2": ["2"], "R3": ["2"], "R5": ["2"],
    "C1": ["2"], "C2": ["2"], "C3": ["2"], "C4": ["2"], "C5": ["2"], "C6": ["2"],
    "LED1": ["1"],
}


def add_zone(board, net, layer, inset=0.2):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(net)
    z.SetLocalClearance(MM(0.2))
    z.SetMinThickness(MM(0.2))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    z.Outline().NewOutline()
    for x, y in [(inset, inset), (98 - inset, inset),
                 (98 - inset, 29 - inset), (inset, 29 - inset)]:
        z.Outline().Append(V(x, y))
    board.Add(z)
    return z


def add_antenna_keepout(board):
    k = pcbnew.ZONE(board)
    k.SetIsRuleArea(True)
    k.SetDoNotAllowCopperPour(True)
    k.SetDoNotAllowTracks(False)
    k.SetDoNotAllowVias(False)
    k.SetDoNotAllowPads(False)
    ls = pcbnew.LSET()
    ls.AddLayer(pcbnew.F_Cu)
    ls.AddLayer(pcbnew.B_Cu)
    k.SetLayerSet(ls)
    k.Outline().NewOutline()
    for x, y in [(95.0, 8.0), (98.0, 8.0), (98.0, 21.0), (95.0, 21.0)]:
        k.Outline().Append(V(x, y))
    board.Add(k)


def main():
    board = pcbnew.LoadBoard(PCB)
    pcbnew.ImportSpecctraSES(board, SES)

    gnd = board.FindNet("GND")
    if gnd is None:
        gnd = pcbnew.NETINFO_ITEM(board, "GND")
        board.Add(gnd)
    for ref, nums in GND_PADS.items():
        fp = board.FindFootprintByReference(ref)
        if fp is None:
            continue
        for num in nums:
            p = fp.FindPadByNumber(str(num))
            if p is not None:
                p.SetNet(gnd)

    add_zone(board, gnd, pcbnew.B_Cu)
    add_zone(board, gnd, pcbnew.F_Cu)
    add_antenna_keepout(board)

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    pcbnew.SaveBoard(PCB, board)
    print("Saved", PCB, "zones", len(board.Zones()))


if __name__ == "__main__":
    main()
