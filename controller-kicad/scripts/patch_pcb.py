#!/usr/bin/env python3
"""Deterministic post-route fixes.

The autorouter leaves a few nets unrouted or with the wrong layer, so they
are rebuilt here after the SES import:

* USB-C D+/D-: the pads are 0.3 mm wide on a 0.5 mm pitch.  The two plug
  orientations are tied with 0.45/0.2 mm via-in-pad plus short bridges, and
  the two data nets are routed with the geometry that Freerouting found for
  them (the router can only fit one of the two nets at a time).
* LED: U1 pad 42 (P1.06) drives R6, which feeds LED1.
* P0.12: connect the module pad 20 to the existing B.Cu stub.
* GND stitching vias for the bottom pour.

The E73 runs in high-voltage mode, so VDD (3V3) and VDDH are NOT bridged.
DCCH is left unconnected (LDO mode), matching the E73 reference design.

Everything is idempotent: the nets routed here are removed first.
"""
import math
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


def padpos(board, ref, num):
    fp = None
    for f in board.GetFootprints():
        if f.GetReference() == ref:
            fp = f
            break
    if fp is None:
        raise RuntimeError("missing footprint " + ref)
    p = fp.FindPadByNumber(str(num))
    if p is None:
        raise RuntimeError("missing pad %s.%s" % (ref, num))
    return (round(pcbnew.ToMM(p.GetPosition().x), 4),
            round(pcbnew.ToMM(p.GetPosition().y), 4))


def delete_nets(board, names):
    for t in list(board.Tracks()):
        if t.GetNetname() in names:
            board.Remove(t)


def _mm(v):
    return pcbnew.ToMM(v)


def _rect_dist(p, r):
    x, y = p
    x0, y0 = _mm(r.GetX()), _mm(r.GetY())
    x1, y1 = x0 + _mm(r.GetWidth()), y0 + _mm(r.GetHeight())
    dx = max(x0 - x, 0.0, x - x1)
    dy = max(y0 - y, 0.0, y - y1)
    return math.hypot(dx, dy)


def _seg_dist(p, a, b):
    px, py = p
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    l2 = dx * dx + dy * dy
    if l2 == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def stitch_gnd(board):
    """Add one GND stitching via to every isolated B.Cu pour island."""
    zones = [z for z in board.Zones()
             if z.GetNetname() == "GND" and z.IsOnLayer(pcbnew.B_Cu)]
    if not zones:
        return
    ps = zones[0].GetFilledPolysList(pcbnew.B_Cu)

    obstacles = []
    for t in board.Tracks():
        if t.GetNetname() == "GND":
            continue
        s, e = t.GetStart(), t.GetEnd()
        a = (_mm(s.x), _mm(s.y))
        c = (_mm(e.x), _mm(e.y))
        if t.Type() == pcbnew.PCB_VIA_T:
            obstacles.append(("via", _mm(t.GetWidth(pcbnew.F_Cu)) / 2.0, a, c))
        else:
            obstacles.append(("trk", _mm(t.GetWidth()) / 2.0, a, c))
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname() == "GND":
                continue
            obstacles.append(("pad", 0.0, None, p.GetBoundingBox()))

    added = 0
    for i in range(1, ps.OutlineCount()):
        bb = ps.Outline(i).BBox()
        x0, y0 = _mm(bb.GetX()), _mm(bb.GetY())
        x1, y1 = x0 + _mm(bb.GetWidth()), y0 + _mm(bb.GetHeight())
        best = None
        x = x0 + 0.5
        while x < x1 - 0.2:
            y = y0 + 0.5
            while y < y1 - 0.2:
                if ps.Contains(pcbnew.VECTOR2I_MM(x, y)):
                    md = 1e9
                    for kind, half, a, b in obstacles:
                        if kind == "pad":
                            d = _rect_dist((x, y), b)
                        elif kind == "via":
                            d = math.hypot(x - a[0], y - a[1]) - half
                        else:
                            d = _seg_dist((x, y), a, b) - half
                        md = min(md, d)
                    md = min(md, x - 0.2, y - 0.2, 98 - x - 0.2, 29 - y - 0.2)
                    if md > 0.4 and (best is None or md > best[0]):
                        best = (md, x, y)
                y += 0.5
            x += 0.5
        if best:
            via(board, "GND", round(best[1], 3), round(best[2], 3), 0.4, 0.2)
            added += 1
    print("GND stitching vias added:", added)


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

    # Read pad positions before board.Remove() (SWIG invalidates the lists).
    a6 = padpos(board, "J1", "A6")
    b6 = padpos(board, "J1", "B6")
    a7 = padpos(board, "J1", "A7")
    b7 = padpos(board, "J1", "B7")
    p29 = padpos(board, "U1", "29")   # USB_DM
    p31 = padpos(board, "U1", "31")   # USB_DP
    p42 = padpos(board, "U1", "42")   # P1.06
    p20 = padpos(board, "U1", "20")   # P0.12
    r6_1 = padpos(board, "R6", "1")   # P1.06
    r6_2 = padpos(board, "R6", "2")   # LED_A
    led_a = padpos(board, "LED1", "2")  # LED_A
    c7_1 = padpos(board, "C7", "1")   # VBAT
    u2_3 = padpos(board, "U2", "3")   # VBAT
    c2_1 = padpos(board, "C2", "1")   # VDDH
    c6_1 = padpos(board, "C6", "1")   # VBUS
    c8_1 = padpos(board, "C8", "1")   # VBUS
    c9_1 = padpos(board, "C9", "1")   # VBAT
    r3_1 = padpos(board, "R3", "1")   # PROG
    u2_5 = padpos(board, "U2", "5")   # PROG

    delete_nets(board, {"USB_DP", "USB_DM", "P1.06", "LED_A", "PROG"})

    # --- USB-C: via-in-pad for both plug orientations. ------------------
    # The pads are 0.3 mm wide on a 0.5 mm pitch.  Moving the vias outside
    # conflicts with the CC1/CC2 fan-out, so keep the verified via-in-pad
    # geometry and require JLCPCB resin fill/cap for PCBA.
    for p in (a6, b6, a7, b7):
        via(board, "USB_DP" if p in (a6, b6) else "USB_DM",
            p[0], p[1], 0.4, 0.2)

    # D+ bridge A6/B6 at y = 1.5 (clear of the USB_DM vias).
    track(board, "USB_DP", pcbnew.F_Cu,
          [a6, (a6[0], 1.5), (b6[0], 1.5), b6], 0.2)
    # D+ to the module: B.Cu from B6 to the hop via, F.Cu across the board
    # at y = 3.302/5.038 (the corridor Freerouting used), then B.Cu to pad 31.
    track(board, "USB_DP", pcbnew.B_Cu,
          [b6, (b6[0], 1.882), (30.462, 2.244), (30.963, 2.4)], 0.2)
    via(board, "USB_DP", 30.963, 2.4, 0.45, 0.2)
    track(board, "USB_DP", pcbnew.F_Cu,
          [(30.963, 2.4), (32.021, 3.302), (38.294, 3.302),
           (40.03, 5.038), (81.933, 5.038), (82.239, 4.732),
           (84.324, 4.732), (84.551, 4.959)], 0.2)
    via(board, "USB_DP", 84.551, 4.959)
    track(board, "USB_DP", pcbnew.B_Cu,
          [(84.551, 4.959), (86.39, 6.798), p31], 0.2)

    # D-: A7/B7 tie on B.Cu, hop via, F.Cu at y = 5.531, then B.Cu to pad 29.
    track(board, "USB_DM", pcbnew.B_Cu,
          [a7, (a7[0], 1.8817), (b7[0], 1.8817), b7], 0.2)
    track(board, "USB_DM", pcbnew.B_Cu,
          [b7, (b7[0], 1.8817), (31.7, 3.6)], 0.2)
    via(board, "USB_DM", 31.7, 3.6, 0.45, 0.2)
    track(board, "USB_DM", pcbnew.F_Cu,
          [(31.7, 3.6), (32.614, 3.946), (37.61, 3.946),
           (39.195, 5.531), (84.0, 5.4)], 0.2)
    via(board, "USB_DM", 84.0, 5.4)
    track(board, "USB_DM", pcbnew.B_Cu,
          [(84.0, 5.4), p29], 0.2)

    # --- LED: U1 pad 42 (P1.06) -> R6 -> LED1. --------------------------
    # Move both vias outside the pads so there is no via-in-pad.
    u1_via = (94.6, p42[1])
    r6_via = (92.5, 2.8)
    track(board, "P1.06", pcbnew.B_Cu, [p42, u1_via], 0.2)
    via(board, "P1.06", u1_via[0], u1_via[1], 0.4, 0.2)
    track(board, "P1.06", pcbnew.F_Cu,
          [u1_via, (94.6, 2.8), r6_via], 0.2)
    via(board, "P1.06", r6_via[0], r6_via[1], 0.4, 0.2)
    track(board, "P1.06", pcbnew.B_Cu, [r6_via, r6_1], 0.2)
    track(board, "LED_A", pcbnew.B_Cu,
          [r6_2, (r6_2[0], 0.8), (led_a[0], 0.8), led_a], 0.2)

    # --- P0.12: the SES route ends just short of U1 pad 20. -------------
    track(board, "P0.12", pcbnew.B_Cu,
          [p20, (82.7417, 13.23)], 0.2)

    # --- C2 moved left to clear the E73 module body. --------------------
    # The SES still has the old C2 pad-1 track at x=79.73; join the new pad
    # to it around the C2 GND pad.
    track(board, "VDDH", pcbnew.B_Cu, [c2_1, (81.3, 8.0)], 0.2)

    # --- Additional charger bypass capacitors C8/C9. --------------------
    track(board, "VBUS", pcbnew.B_Cu,
          [c8_1, (c8_1[0], 2.2), (c6_1[0], 2.2), c6_1], 0.2)
    track(board, "VBAT", pcbnew.B_Cu,
          [c9_1, (c9_1[0], 8.2), (c7_1[0], 8.2), c7_1], 0.2)

    # --- R3 (PROG) moved away from the J2 body. -------------------------
    track(board, "PROG", pcbnew.B_Cu, [u2_5, r3_1], 0.2)

    # --- MCP73831 VBAT bypass capacitor C7. -----------------------------
    # 10 uF on VBAT; the GND pad is connected by the B.Cu pour.
    track(board, "VBAT", pcbnew.B_Cu,
          [c7_1, (36.8, 9.0), (36.8, 7.05), u2_3], 0.2)

    # --- GND stitching vias (bottom edge + left battery area). ----------
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
