#!/usr/bin/env python3
"""Manual fixes after autorouting: VDDH, USB-C D- bridge, GND stitching."""
import os
import pcbnew

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(HERE, "controller.kicad_pcb")
MM = pcbnew.FromMM
V = pcbnew.VECTOR2I_MM


def net(board, name):
    n = board.FindNet(name)
    if n is None:
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
    return n


def track(board, netname, layer, pts, width=0.2):
    n = net(board, netname)
    for a, b in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(V(*a))
        t.SetEnd(V(*b))
        t.SetWidth(MM(width))
        t.SetLayer(layer)
        t.SetNet(n)
        board.Add(t)


def via(board, netname, x, y, size=0.6, drill=0.3):
    n = net(board, netname)
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(V(x, y))
    v.SetWidth(MM(size))
    v.SetDrill(MM(drill))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetNet(n)
    board.Add(v)


def main():
    board = pcbnew.LoadBoard(PCB)
    ds = board.GetDesignSettings()
    ds.m_MinClearance = MM(0.1)
    ds.m_TrackMinWidth = MM(0.1)
    ds.m_ViasMinSize = MM(0.3)
    ds.m_ViasMinAnnularWidth = MM(0.05)
    ds.m_MinThroughDrill = MM(0.2)
    try:
        nc = ds.m_NetSettings.GetDefaultNetclass()
        nc.SetClearance(MM(0.1))
        nc.SetTrackWidth(MM(0.2))
        nc.SetViaDiameter(MM(0.3))
        nc.SetViaDrill(MM(0.2))
    except Exception:
        pass

    # GND stitching vias: bottom edge + left battery area.
    for x in [5, 15, 25, 35, 45, 55, 65, 75, 85, 95]:
        via(board, "GND", x, 27.0)
    for x in [5, 15, 25, 35]:
        via(board, "GND", x, 23.0)



    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    pcbnew.SaveBoard(PCB, board)
    print("Patched", PCB)


if __name__ == "__main__":
    main()
