"""Wired schematic writer (KiCad 4/5 legacy) with geometric connectivity verification."""
import itertools
from pcbgen import SYM, Sym, sym, FOOT, uid
import jlc

# ---------------- extra symbols for nicer drawing ----------------
sym(Sym("RH", "R", [("~", "1", -150, 0, 50, "R", "P"), ("~", "2", 150, 0, 50, "L", "P")],
        ["S -100 -40 100 40 0 1 10 N"], value_pos=(-60, -70), ref_pos=(-60, 60)))
sym(Sym("FUSE_H", "F", [("~", "1", -150, 0, 50, "R", "P"), ("~", "2", 150, 0, 50, "L", "P")],
        ["S -100 -35 100 35 0 1 10 N", "P 2 0 1 10 -100 0 100 0 N"], value_pos=(-80, -90), ref_pos=(-80, 60)))
sym(Sym("CH", "C", [("~", "1", -150, 0, 120, "R", "P"), ("~", "2", 150, 0, 120, "L", "P")],
        ["P 2 0 1 20 -30 -80 -30 80 N", "P 2 0 1 20 30 -80 30 80 N"], value_pos=(-60, -110), ref_pos=(-60, 100)))
sym(Sym("CHR", "C", [("~", "2", -150, 0, 120, "R", "P"), ("~", "1", 150, 0, 120, "L", "P")],
        ["P 2 0 1 20 -30 -80 -30 80 N", "P 2 0 1 20 30 -80 30 80 N"], value_pos=(-60, -110), ref_pos=(-60, 100)))
sym(Sym("PAD_L", "J", [("~", "1", 150, 0, 100, "L", "P")], ["C 0 0 50 0 1 10 N"], value_pos=(-250, -60), ref_pos=(-250, 20)))
sym(Sym("TP_D", "TP", [("~", "1", 0, 150, 100, "D", "P")], ["C 0 0 50 0 1 10 N"], value_pos=(80, -60), ref_pos=(80, 20)))
sym(Sym("ZENER_H", "D", [("A", "2", -150, 0, 100, "R", "P"), ("K", "1", 150, 0, 100, "L", "P")],
        ["P 4 0 1 10 -50 50 -50 -50 50 0 -50 50 F", "P 4 0 1 10 30 70 50 50 50 -50 70 -70 N"], value_pos=(-60, -110), ref_pos=(-60, 90)))
sym(Sym("D_H", "D", [("A", "2", -150, 0, 100, "R", "P"), ("K", "1", 150, 0, 100, "L", "P")],
        ["P 4 0 1 10 -50 50 -50 -50 50 0 -50 50 F", "P 2 0 1 10 50 50 50 -50 N"], value_pos=(-60, -110), ref_pos=(-60, 90)))
sym(Sym("D_V", "D", [("A", "2", 0, -150, 100, "U", "P"), ("K", "1", 0, 150, 100, "D", "P")],
        ["P 4 0 1 10 -50 -50 50 -50 0 50 -50 -50 F", "P 2 0 1 10 -50 50 50 50 N"], value_pos=(70, -60), ref_pos=(70, 20)))
sym(Sym("EF86W", "V",
        [("A", "6", 0, 450, 150, "D", "P"), ("G1", "9", -400, 50, 150, "R", "I"), ("G3", "8", -400, -50, 150, "R", "P"),
         ("IS", "2", -200, -450, 150, "U", "P"), ("K", "3", -100, -450, 150, "U", "P"), ("IS", "7", 0, -450, 150, "U", "P"),
         ("G2", "1", 400, 150, 150, "L", "P"), ("H", "4", 400, -150, 150, "L", "W"), ("H", "5", 400, -250, 150, "L", "W")],
        ["S -250 -300 250 300 0 1 10 f"], show_names=True, value_pos=(280, 330), ref_pos=(280, 410)))
sym(Sym("E88CCW", "V",
        [("A1", "1", -150, 450, 150, "D", "P"), ("A2", "6", 150, 450, 150, "D", "P"),
         ("G1", "2", -500, 0, 150, "R", "I"), ("G2", "7", 500, 0, 150, "L", "I"),
         ("K1", "3", -150, -450, 150, "U", "P"), ("K2", "8", 150, -450, 150, "U", "P"),
         ("S", "9", -500, -200, 150, "R", "P"), ("H", "4", 500, -150, 150, "L", "W"), ("H", "5", 500, -250, 150, "L", "W")],
        ["S -350 -300 350 300 0 1 10 f"], show_names=True, value_pos=(380, 330), ref_pos=(380, 410)))
sym(Sym("DN2540W", "Q", [("G", "1", -300, 0, 150, "R", "I"), ("D", "2", 0, 300, 150, "D", "P"), ("S", "3", 0, -300, 150, "U", "P")],
        ["S -150 -150 150 150 0 1 10 f"], show_names=True, value_pos=(180, -60), ref_pos=(180, 20)))


def pin_points(symname, cx, cy):
    out = {}
    for (nm, num, px, py, ln, ori, et) in SYM[symname].pins:
        out[num] = (cx + px, cy - py, ori)
    return out


class WiredSch:
    def __init__(self, board, sheet=("A2", 23386, 16535)):
        self.b, self.sheet = board, sheet
        self.place = {}          # ref -> (symbol, x, y)
        self.segs = []           # ((x1,y1),(x2,y2))
        self.labels = []         # (x, y, net, orient)
        self.notes = []          # (x, y, text, size)
        self.comps = {c.ref: c for c in board.comps}

    def put(self, ref, symbol, x, y):
        assert ref in self.comps, ref
        self.place[ref] = (symbol or self.comps[ref].symbol, x, y)

    def p(self, ref, num):
        s, x, y = self.place[ref]
        a = pin_points(s, x, y)[str(num)]
        return (a[0], a[1])

    def w(self, *pts):
        pts = [self.p(*q) if isinstance(q[0], str) else q for q in pts]
        for a, b in zip(pts, pts[1:]):
            assert a[0] == b[0] or a[1] == b[1], ("non-orthogonal", a, b)
            if a != b:
                self.segs.append((a, b))

    def lab(self, pt, net, orient=0, stub=None):
        if isinstance(pt[0], str):
            pt = self.p(*pt)
        if stub:
            dx, dy = stub
            q = (pt[0] + dx, pt[1] + dy)
            self.w(pt, q)
            pt = q
        self.labels.append((pt[0], pt[1], net, orient))

    def note(self, x, y, t, size=80):
        self.notes.append((x, y, t, size))

    # automatic label stubs for any pin not touched by wires/labels
    def autolabel(self):
        touched = set()
        for a, b in self.segs:
            touched.add(a); touched.add(b)
        for (x, y, n, o) in self.labels:
            touched.add((x, y))
        for ref, (s, x, y) in self.place.items():
            c = self.comps[ref]
            for num, (px, py, ori) in pin_points(s, x, y).items():
                if (px, py) in touched or self._on_seg((px, py)):
                    continue
                net = c.nets.get(num)
                if net is None:
                    continue
                dx, dy, lo = {"D": (0, -100, 1), "U": (0, 100, 3), "R": (-100, 0, 2), "L": (100, 0, 0)}[ori]
                self.lab((px, py), net, lo, stub=(dx, dy))

    def _on_seg(self, pt):
        for a, b in self.segs:
            if self._between(pt, a, b):
                return True
        return False

    @staticmethod
    def _between(p, a, b):
        if a[0] == b[0] == p[0]:
            return min(a[1], b[1]) <= p[1] <= max(a[1], b[1])
        if a[1] == b[1] == p[1]:
            return min(a[0], b[0]) <= p[0] <= max(a[0], b[0])
        return False

    def _split(self):
        pts = set()
        for a, b in self.segs:
            pts.add(a); pts.add(b)
        for ref, (s, x, y) in self.place.items():
            for num, (px, py, o) in pin_points(s, x, y).items():
                pts.add((px, py))
        for (x, y, n, o) in self.labels:
            pts.add((x, y))
        out = []
        for a, b in self.segs:
            inner = [q for q in pts if q != a and q != b and self._between(q, a, b)]
            key = (lambda q: q[1]) if a[0] == b[0] else (lambda q: q[0])
            seq = sorted([a, b] + inner, key=key)
            out += list(zip(seq, seq[1:]))
        self.segs = out

    # ---------------- connectivity ----------------
    def connectivity(self):
        self._split()
        parent = {}
        def f(x):
            parent.setdefault(x, x)
            while parent[x] != x:
                parent[x] = parent[parent[x]]; x = parent[x]
            return x
        def u(a, b):
            parent[f(a)] = f(b)
        for a, b in self.segs:
            u(("pt",) + a, ("pt",) + b)
        for (x, y, n, o) in self.labels:
            u(("pt", x, y), ("net", n))
        pins = {}
        for ref, (s, x, y) in self.place.items():
            for num, (px, py, o) in pin_points(s, x, y).items():
                u(("pin", ref, num), ("pt", px, py))
                pins[(ref, num)] = ("pin", ref, num)
        groups = {}
        for (ref, num), key in pins.items():
            groups.setdefault(f(key), set()).add((ref, num))
        return [g for g in groups.values()]

    def verify(self):
        errs = []
        missing = [c.ref for c in self.b.comps if c.symbol and c.ref not in self.place]
        if missing:
            errs.append("not placed: %s" % missing)
        groups = self.connectivity()
        want = {}
        for n, lst in self.b.nets().items():
            want[n] = {(r, p) for r, p in lst if r in self.place}
        pin2net = {}
        for n, s in want.items():
            for rp in s:
                pin2net[rp] = n
        for g in groups:
            nets = {pin2net.get(rp) for rp in g}
            real = {n for n in nets if n is not None}
            if len(real) > 1:
                errs.append("SHORT between %s : %s" % (sorted(real), sorted(g)))
            if None in nets and len(g) > 1:
                errs.append("NC pin wired: %s" % sorted(rp for rp in g if pin2net.get(rp) is None))
        for n, s in want.items():
            gs = [g for g in groups if g & s]
            if len(gs) > 1:
                errs.append("OPEN net %s split into %s" % (n, [sorted(g & s) for g in gs]))
        # endpoints dangling (wire end touching nothing else)
        deg = {}
        for a, b in self.segs:
            deg[a] = deg.get(a, 0) + 1; deg[b] = deg.get(b, 0) + 1
        pinpts = set()
        for ref, (s, x, y) in self.place.items():
            for num, (px, py, o) in pin_points(s, x, y).items():
                pinpts.add((px, py))
        labpts = {(x, y) for (x, y, n, o) in self.labels}
        for pt, d in deg.items():
            if d == 1 and pt not in pinpts and pt not in labpts:
                errs.append("dangling wire end at %s" % (pt,))
        return errs

    # ---------------- writer ----------------
    def write(self, path, libname, v5=True):
        self._split()
        L = (["EESchema Schematic File Version 4", "EELAYER 30 0", "EELAYER END"] if v5 else
             ["EESchema Schematic File Version 2", "LIBS:%s" % libname, "EELAYER 25 0", "EELAYER END"])
        L += ["$Descr %s %d %d" % self.sheet, "encoding utf-8", "Sheet 1 1", 'Title "%s"' % self.b.title, 'Date ""', 'Rev "0.4"',
              'Comp ""', 'Comment1 "Soloist 88 Stereo"', 'Comment2 ""', 'Comment3 ""', 'Comment4 ""', "$EndDescr"]
        ts = itertools.count(0x5C000001)
        for ref, (s, x, y) in self.place.items():
            c = self.comps[ref]; S = SYM[s]
            L += ["$Comp", "L %s%s %s" % ((libname + ":") if v5 else "", s, ref), "U 1 1 %s" % uid(ref), "P %d %d" % (x, y),
                  'F 0 "%s" H %d %d 50  0000 L CNN' % (ref, x + S.ref_pos[0], y - S.ref_pos[1]),
                  'F 1 "%s" H %d %d 50  0000 L CNN' % (c.value, x + S.value_pos[0], y - S.value_pos[1]),
                  'F 2 "%s:%s" H %d %d 50  0001 C CNN' % (libname, c.fp, x, y),
                  'F 3 "%s" H %d %d 50  0001 C CNN' % ("~" if v5 else "", x, y)]
            desc, lcsc = jlc.lookup(c)
            if lcsc:
                L += ['F 4 "LCSC" H %d %d 50  0001 C CNN "Supplier"' % (x, y),
                      'F 5 "%s" H %d %d 50  0001 C CNN "Supplier Part"' % (lcsc, x, y)]
            L += ["\t1    %d %d" % (x, y), "\t1    0    0    -1  ", "$EndComp"]
        for a, b in self.segs:
            L += ["Wire Wire Line", "\t%d %d %d %d" % (a[0], a[1], b[0], b[1])]
        # junctions
        cnt = {}
        for a, b in self.segs:
            cnt[a] = cnt.get(a, 0) + 1; cnt[b] = cnt.get(b, 0) + 1
        for ref, (s, x, y) in self.place.items():
            for num, (px, py, o) in pin_points(s, x, y).items():
                if (px, py) in cnt:
                    cnt[(px, py)] += 1
        for pt, n in cnt.items():
            if n >= 3:
                L += ["Connection ~ %d %d" % pt]
        for (x, y, n, o) in self.labels:
            L += ["Text Label %d %d %d    50   ~ 0" % (x, y, o), n]
        for (x, y, t, sz) in self.notes:
            L += ["Text Notes %d %d 0    %d   ~ 16" % (x, y, sz), t]
        # NC pins
        for ref, (s, x, y) in self.place.items():
            c = self.comps[ref]
            for num, (px, py, o) in pin_points(s, x, y).items():
                if c.nets.get(num) is None:
                    L += ["NoConn ~ %d %d" % (px, py)]
        L += ["$EndSCHEMATC", ""]
        open(path, "w").write("\n".join(L))

    def used_symbols(self):
        return sorted({s for (s, x, y) in self.place.values()})
