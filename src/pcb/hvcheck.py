import sys, itertools
sys.path.insert(0, '.')
import boards
from pcbgen import Board
boards.Board = Board
def hv_report(b, hv, mind=2.0):
    pads = []
    for c in b.comps:
        P, R, C = c.geom()
        for (n, x, y, w, h, sh, d) in P:
            net = c.nets.get(n)
            if net:
                pads.append((c.ref, n, net, x, y, max(w, h) / 2))
    out = []
    for a, bb in itertools.combinations(pads, 2):
        if a[2] == bb[2]:
            continue
        V = boards.Board.VOLT
        va, vb = V.get(a[2], 0), V.get(bb[2], 0)
        need = 2.5 if ("AC" in (va, vb) or abs((0 if va == "AC" else va) - (0 if vb == "AC" else vb)) >= 200) else 0
        if not need:
            continue
        d = ((a[3] - bb[3]) ** 2 + (a[4] - bb[4]) ** 2) ** 0.5 - a[5] - bb[5]
        if d < need and not (a[0] == bb[0] and a[0].startswith("V")):
            out.append("%.2f mm  %s.%s(%s) - %s.%s(%s)" % (d, a[0], a[1], a[2], bb[0], bb[1], bb[2]))
    return out
if __name__ == "__main__":
    for n in sys.argv[1:]:
        b = getattr(boards, n)()
        r = hv_report(b, boards.HV[b.name])
        print(n, len(r)); print("\n".join(r))
