#!/usr/bin/env python3
"""Connect isolated GND pour islands with stitching vias.

The dense autorouted board splits the bottom GND pour into several islands.
This script builds the connectivity graph of the filled zone outlines and
adds the minimum number of GND vias needed to connect every island to the
main GND (the F.Cu main pour, outline 0).

Run after patch_pcb.py. The script is a no-op if everything is already
connected.
"""
import math
import os
import pcbnew

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(HERE, "controller.kicad_pcb")
VIA_D = 0.4
VIA_DRILL = 0.2
CLEAR = VIA_D / 2.0 + 0.1


def mm(v):
    return pcbnew.ToMM(v)


def rect_dist(p, r):
    x, y = p
    x0, y0 = mm(r.GetX()), mm(r.GetY())
    x1, y1 = x0 + mm(r.GetWidth()), y0 + mm(r.GetHeight())
    dx = max(x0 - x, 0.0, x - x1)
    dy = max(y0 - y, 0.0, y - y1)
    return math.hypot(dx, dy)


def seg_dist(p, a, b):
    px, py = p
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    l2 = dx * dx + dy * dy
    if l2 == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


class Graph:
    def __init__(self, f_count, b_count):
        self.nodes = [("F", i) for i in range(f_count)] + \
                     [("B", i) for i in range(b_count)]
        self.parent = {n: n for n in self.nodes}

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra

    def component(self, n):
        return self.find(n)

    def connected_to_main(self):
        root = self.find(("F", 0))
        return [n for n in self.nodes if self.find(n) == root]


def outlines_containing(ps, p):
    return [i for i in range(ps.OutlineCount())
            if ps.Outline(i).PointInside(p)]


def find_point(ps_a, idx_a, ps_b, idx_b, obstacles, threshold):
    """Point inside outline idx_a of ps_a and idx_b of ps_b, clear."""
    a = ps_a.Outline(idx_a)
    b = ps_b.Outline(idx_b)
    bb = a.BBox()
    x0, y0 = mm(bb.GetX()), mm(bb.GetY())
    x1, y1 = x0 + mm(bb.GetWidth()), y0 + mm(bb.GetHeight())
    best = None
    x = x0 + 0.2
    while x < x1 - 0.1:
        y = y0 + 0.2
        while y < y1 - 0.1:
            p = pcbnew.VECTOR2I_MM(x, y)
            if a.PointInside(p) and b.PointInside(p):
                md = 1e9
                for kind, half, o1, o2 in obstacles:
                    if kind == "pad":
                        d = rect_dist((x, y), o2)
                    elif kind == "via":
                        d = math.hypot(x - o1[0], y - o1[1]) - half
                    else:
                        d = seg_dist((x, y), o1, o2) - half
                    md = min(md, d)
                md = min(md, x - 0.2, y - 0.2,
                         98 - x - 0.2, 29 - y - 0.2)
                if md > threshold and (best is None or md > best[0]):
                    best = (md, x, y)
            y += 0.2
        x += 0.2
    return best


def add_via(board, gnd, x, y):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I_MM(round(x, 3), round(y, 3)))
    v.SetWidth(pcbnew.FromMM(VIA_D))
    v.SetDrill(pcbnew.FromMM(VIA_DRILL))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetNet(gnd)
    board.Add(v)


def main():
    board = pcbnew.LoadBoard(PCB)
    gnd = board.FindNet("GND")
    fz = [z for z in board.Zones()
          if z.GetNetname() == "GND" and z.IsOnLayer(pcbnew.F_Cu)]
    bz = [z for z in board.Zones()
          if z.GetNetname() == "GND" and z.IsOnLayer(pcbnew.B_Cu)]
    if not fz or not bz:
        print("missing GND zones")
        return
    fps = fz[0].GetFilledPolysList(pcbnew.F_Cu)
    bps = bz[0].GetFilledPolysList(pcbnew.B_Cu)

    obstacles = []
    for t in board.Tracks():
        if t.GetNetname() == "GND":
            continue
        s, e = t.GetStart(), t.GetEnd()
        a = (mm(s.x), mm(s.y))
        c = (mm(e.x), mm(e.y))
        if t.Type() == pcbnew.PCB_VIA_T:
            obstacles.append(("via", mm(t.GetWidth(pcbnew.F_Cu)) / 2.0, a, None))
        else:
            obstacles.append(("trk", mm(t.GetWidth()) / 2.0, a, c))
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname() == "GND":
                continue
            obstacles.append(("pad", 0.0, None, p.GetBoundingBox()))

    g = Graph(fps.OutlineCount(), bps.OutlineCount())
    for t in board.Tracks():
        if t.Type() != pcbnew.PCB_VIA_T or t.GetNetname() != "GND":
            continue
        p = t.GetPosition()
        fi = outlines_containing(fps, p)
        bi = outlines_containing(bps, p)
        for a in fi:
            for b in bi:
                g.union(("F", a), ("B", b))

    # 1. Connect every B.Cu island to the main F.Cu pour (outline 0).
    for i in range(bps.OutlineCount()):
        if g.component(("B", i)) == g.component(("F", 0)):
            continue
        best = find_point(bps, i, fps, 0, obstacles, CLEAR)
        if best:
            add_via(board, gnd, best[1], best[2])
            g.union(("B", i), ("F", 0))
            print("B%d -> F0 via %.2f %.2f (clearance %.2f)" %
                  (i, best[1], best[2], best[0]))

    # 2. Connect any remaining F.Cu island to a B.Cu island that is already
    #    on the main GND component.
    main = set(g.connected_to_main())
    for i in range(1, fps.OutlineCount()):
        if g.component(("F", i)) == g.component(("F", 0)):
            continue
        best = None
        for j in range(bps.OutlineCount()):
            if g.component(("B", j)) != g.component(("F", 0)):
                continue
            cand = find_point(fps, i, bps, j, obstacles, CLEAR)
            if cand and (best is None or cand[0] > best[0]):
                best = cand
        if best:
            add_via(board, gnd, best[1], best[2])
            print("F%d -> main via %.2f %.2f (clearance %.2f)" %
                  (i, best[1], best[2], best[0]))

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    pcbnew.SaveBoard(PCB, board)
    print("stitched", PCB)


if __name__ == "__main__":
    main()
