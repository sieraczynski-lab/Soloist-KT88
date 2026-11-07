"""Tiny schematic-drawing helpers emitting SVG with CSS classes (theme via page CSS)."""
import math

class Sheet:
    def __init__(self, w, h, title, dy=0):
        self.w, self.h, self.title, self.dy = w, h, title, dy
        self.el = []

    # ---------- basics ----------
    def add(self, s):
        self.el.append(s)

    def wire(self, *pts, cls="w"):
        p = " ".join(f"{x},{y}" for x, y in pts)
        self.add(f'<polyline class="{cls}" points="{p}"/>')

    def dot(self, x, y):
        self.add(f'<circle class="dot" cx="{x}" cy="{y}" r="3.6"/>')

    def hop(self, x, y, r=6):
        # hop drawn on a horizontal wire crossing a vertical one at (x,y)
        self.add(f'<line class="erase" x1="{x-r}" y1="{y}" x2="{x+r}" y2="{y}"/>')
        self.add(f'<path class="w" d="M{x-r},{y} A{r},{r} 0 0 1 {x+r},{y}"/>')

    def text(self, x, y, s, cls="ref", anchor="start"):
        self.add(f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{s}</text>')

    def lab(self, x, y, ref, val, anchor="start", dy=13):
        if ref:
            self.text(x, y, ref, "ref", anchor)
        if val:
            self.text(x, y + dy, val, "val", anchor)

    def volt(self, x, y, s, anchor="start"):
        self.text(x, y, s, "hv", anchor)

    # ---------- passives ----------
    def resv(self, x, y1, y2, ref=None, val=None, side="r", L=34, W=12, opt=False):
        m = (y1 + y2) / 2
        a, b = m - L / 2, m + L / 2
        c = "w opt" if opt else "w"
        self.wire((x, y1), (x, a), cls=c)
        self.wire((x, b), (x, y2), cls=c)
        self.add(f'<rect class="body{" opt" if opt else ""}" x="{x-W/2}" y="{a}" width="{W}" height="{L}"/>')
        if side == "r":
            self.lab(x + 11, m - 2, ref, val)
        else:
            self.lab(x - 11, m - 2, ref, val, "end")

    def resh(self, x1, x2, y, ref=None, val=None, side="t", L=34, W=12, opt=False):
        m = (x1 + x2) / 2
        a, b = m - L / 2, m + L / 2
        c = "w opt" if opt else "w"
        self.wire((x1, y), (a, y), cls=c)
        self.wire((b, y), (x2, y), cls=c)
        self.add(f'<rect class="body{" opt" if opt else ""}" x="{a}" y="{y-W/2}" width="{L}" height="{W}"/>')
        if side == "t":
            self.lab(m, y - 22, ref, val, "middle")
        else:
            self.lab(m, y + 20, ref, val, "middle")

    def potv(self, x, y1, y2, ref=None, val=None, side="r"):
        self.resv(x, y1, y2, ref, val, side)
        m = (y1 + y2) / 2
        self.add(f'<line class="w" x1="{x-13}" y1="{m+13}" x2="{x+13}" y2="{m-13}"/>')
        self.add(f'<path class="arrowhead" d="M{x+13},{m-13} l-8,1.5 l6.5,6.5 z"/>')

    def poth(self, x1, x2, y, ref=None, val=None, side="t"):
        self.resh(x1, x2, y, ref, val, side)
        m = (x1 + x2) / 2
        self.add(f'<line class="w" x1="{m-15}" y1="{y+11}" x2="{m+15}" y2="{y-11}"/>')
        self.add(f'<path class="arrowhead" d="M{m+15},{y-11} l-8,1 l5.5,6.5 z"/>')

    def capv(self, x, y1, y2, ref=None, val=None, side="r", elec=False, plus_top=True, opt=False):
        m = (y1 + y2) / 2
        c = "w opt" if opt else "w"
        self.wire((x, y1), (x, m - 4), cls=c)
        self.wire((x, m + 4), (x, y2), cls=c)
        if elec:
            # straight plate = +, curved plate = -
            if plus_top:
                self.add(f'<line class="plate" x1="{x-11}" y1="{m-4}" x2="{x+11}" y2="{m-4}"/>')
                self.add(f'<path class="plate" d="M{x-11},{m+8} Q{x},{m+1} {x+11},{m+8}"/>')
                self.text(x - 17, m - 8, "+", "pl", "middle")
            else:
                self.add(f'<path class="plate" d="M{x-11},{m-8} Q{x},{m-1} {x+11},{m-8}"/>')
                self.add(f'<line class="plate" x1="{x-11}" y1="{m+4}" x2="{x+11}" y2="{m+4}"/>')
                self.text(x - 17, m + 18, "+", "pl", "middle")
        else:
            self.add(f'<line class="plate{" opt" if opt else ""}" x1="{x-11}" y1="{m-4}" x2="{x+11}" y2="{m-4}"/>')
            self.add(f'<line class="plate{" opt" if opt else ""}" x1="{x-11}" y1="{m+4}" x2="{x+11}" y2="{m+4}"/>')
        if side == "r":
            self.lab(x + 16, m - 2, ref, val)
        else:
            self.lab(x - 16, m - 2, ref, val, "end")

    def caph(self, x1, x2, y, ref=None, val=None, side="t", opt=False):
        m = (x1 + x2) / 2
        c = "w opt" if opt else "w"
        self.wire((x1, y), (m - 4, y), cls=c)
        self.wire((m + 4, y), (x2, y), cls=c)
        for dx in (-4, 4):
            self.add(f'<line class="plate{" opt" if opt else ""}" x1="{m+dx}" y1="{y-11}" x2="{m+dx}" y2="{y+11}"/>')
        if side == "t":
            self.lab(m, y - 24, ref, val, "middle")
        else:
            self.lab(m, y + 24, ref, val, "middle")

    def gnd(self, x, y, stub=10):
        self.wire((x, y), (x, y + stub))
        yy = y + stub
        self.add(f'<line class="w" x1="{x-10}" y1="{yy}" x2="{x+10}" y2="{yy}"/>')
        self.add(f'<line class="w" x1="{x-6}" y1="{yy+4}" x2="{x+6}" y2="{yy+4}"/>')
        self.add(f'<line class="w" x1="{x-2}" y1="{yy+8}" x2="{x+2}" y2="{yy+8}"/>')

    def flag(self, x, y, label, d="up", sub=None):
        if d == "up":
            self.add(f'<line class="w" x1="{x-9}" y1="{y}" x2="{x+9}" y2="{y}"/>')
            self.text(x, y - 7, label, "rail", "middle")
        elif d == "down":
            self.add(f'<line class="w" x1="{x-9}" y1="{y}" x2="{x+9}" y2="{y}"/>')
            self.text(x, y + 17, label, "rail", "middle")
        elif d == "left":
            self.add(f'<line class="w" x1="{x}" y1="{y-9}" x2="{x}" y2="{y+9}"/>')
            self.text(x - 6, y + 4, label, "rail", "end")
        elif d == "right":
            self.add(f'<line class="w" x1="{x}" y1="{y-9}" x2="{x}" y2="{y+9}"/>')
            self.text(x + 6, y + 4, label, "rail", "start")

    def term(self, x, y, label, anchor="start", dx=9):
        self.add(f'<circle class="term" cx="{x}" cy="{y}" r="4.5"/>')
        self.text(x + (dx if anchor == "start" else -dx), y + 4, label, "rail", anchor)

    def coil_v(self, x, y1, y2, n, bulge=1):
        r = (y2 - y1) / (2 * n)
        d = f"M{x},{y1}"
        sweep = 1 if bulge > 0 else 0
        for i in range(n):
            d += f" A{r},{r} 0 0 {sweep} {x},{y1 + 2*r*(i+1)}"
        self.add(f'<path class="w" d="{d}"/>')

    def coil_h(self, x1, x2, y, n):
        r = (x2 - x1) / (2 * n)
        d = f"M{x1},{y}"
        for i in range(n):
            d += f" A{r},{r} 0 0 1 {x1 + 2*r*(i+1)},{y}"
        self.add(f'<path class="w" d="{d}"/>')

    def diode(self, x1, y1, x2, y2, s=9):
        """diode on segment from anode (x1,y1) to cathode (x2,y2)"""
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        px, py = -uy, ux
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        a = (mx - ux * s, my - uy * s)
        c = (mx + ux * s * 0.8, my + uy * s * 0.8)
        self.wire((x1, y1), a)
        self.wire(c, (x2, y2))
        tri = [(a[0] + px * s, a[1] + py * s), (a[0] - px * s, a[1] - py * s), c]
        self.add('<polygon class="diode" points="' + " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in tri) + '"/>')
        self.add(f'<line class="w" x1="{c[0]+px*s:.1f}" y1="{c[1]+py*s:.1f}" x2="{c[0]-px*s:.1f}" y2="{c[1]-py*s:.1f}"/>')

    def zener(self, x1, y1, x2, y2, s=8):
        """zener from anode (x1,y1) to cathode (x2,y2)"""
        import math as _m
        self.diode(x1, y1, x2, y2, s)
        dx, dy = x2 - x1, y2 - y1
        L = _m.hypot(dx, dy); ux, uy = dx / L, dy / L; px, py = -uy, ux
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        c = (mx + ux * s * 0.8, my + uy * s * 0.8)
        e1 = (c[0] + px * s, c[1] + py * s); e2 = (c[0] - px * s, c[1] - py * s)
        self.add(f'<line class="w" x1="{e1[0]:.1f}" y1="{e1[1]:.1f}" x2="{e1[0]-ux*4:.1f}" y2="{e1[1]-uy*4:.1f}"/>')
        self.add(f'<line class="w" x1="{e2[0]:.1f}" y1="{e2[1]:.1f}" x2="{e2[0]+ux*4:.1f}" y2="{e2[1]+uy*4:.1f}"/>')

    def bridge(self, cx, cy, r=42, pos="right"):
        """full bridge diamond; pos = corner where + appears ('right' or 'left'). returns corners"""
        T, B, Lc, Rc = (cx, cy - r), (cx, cy + r), (cx - r, cy), (cx + r, cy)
        if pos == "right":
            self.diode(*Lc, *T); self.diode(*Lc, *B); self.diode(*T, *Rc); self.diode(*B, *Rc)
        else:
            self.diode(*T, *Lc); self.diode(*B, *Lc); self.diode(*Rc, *T); self.diode(*Rc, *B)
        return dict(top=T, bot=B, left=Lc, right=Rc)

    def switch_h(self, x1, x2, y, label=None, sub=None, dashed_to=None):
        """normally-open contact from x1 to x2"""
        a, b = x1 + 8, x2 - 8
        self.wire((x1, y), (a, y))
        self.wire((b, y), (x2, y))
        self.add(f'<circle class="term" cx="{a}" cy="{y}" r="2.6"/>')
        self.add(f'<circle class="term" cx="{b}" cy="{y}" r="2.6"/>')
        self.add(f'<line class="w" x1="{a}" y1="{y}" x2="{b-2}" y2="{y-13}"/>')
        if label:
            self.lab((x1 + x2) / 2, y - 22 if not sub else y - 33, label, sub, "middle")

    def fuse_h(self, x1, x2, y, ref, val):
        m = (x1 + x2) / 2
        self.wire((x1, y), (m - 17, y)); self.wire((m + 17, y), (x2, y))
        self.add(f'<rect class="body" x="{m-17}" y="{y-6}" width="34" height="12"/>')
        self.add(f'<line class="w" x1="{m-17}" y1="{y}" x2="{m+17}" y2="{y}"/>')
        self.lab(m, y - 22, ref, val, "middle")

    def fuse_v(self, x, y1, y2, ref, val, side="l"):
        m = (y1 + y2) / 2
        self.wire((x, y1), (x, m - 17)); self.wire((x, m + 17), (x, y2))
        self.add(f'<rect class="body" x="{x-6}" y="{m-17}" width="12" height="34"/>')
        self.add(f'<line class="w" x1="{x}" y1="{m-17}" x2="{x}" y2="{m+17}"/>')
        if side == "r":
            self.lab(x + 11, m - 2, ref, val)
        else:
            self.lab(x - 11, m - 2, ref, val, "end")

    # ---------- tubes ----------
    def pentode(self, cx, cy, ref, typ, R=50):
        A = self.add
        A(f'<circle class="env" cx="{cx}" cy="{cy}" r="{R}"/>')
        A(f'<line class="anode" x1="{cx-18}" y1="{cy-30}" x2="{cx+18}" y2="{cy-30}"/>')
        self.wire((cx, cy - 30), (cx, cy - R))
        for yy, side in ((-16, -1), (-2, 1), (12, -1)):
            A(f'<line class="grid" x1="{cx-22}" y1="{cy+yy}" x2="{cx+22}" y2="{cy+yy}"/>')
            ex = cx + side * math.sqrt(R * R - yy * yy)
            self.wire((cx + side * 22, cy + yy), (round(ex, 1), cy + yy))
        A(f'<path class="w" d="M{cx-18},{cy+23} L{cx-18},{cy+28} L{cx+18},{cy+28} L{cx+18},{cy+23}"/>')
        self.wire((cx, cy + 28), (cx, cy + R))
        self.text(cx + R + 6, cy - R + 6, ref, "tref")
        self.text(cx + R + 6, cy - R + 21, typ, "ttyp")
        return dict(a=(cx, cy - R), g3=(round(cx - math.sqrt(R*R-256), 1), cy - 16),
                    g2=(round(cx + math.sqrt(R*R-4), 1), cy - 2),
                    g1=(round(cx - math.sqrt(R*R-144), 1), cy + 12), k=(cx, cy + R))

    def beam(self, cx, cy, ref, typ, flip=False, R=50, lab_side="l"):
        s = -1 if flip else 1
        A = self.add
        A(f'<circle class="env" cx="{cx}" cy="{cy}" r="{R}"/>')
        A(f'<line class="anode" x1="{cx-18}" y1="{cy-30*s}" x2="{cx+18}" y2="{cy-30*s}"/>')
        self.wire((cx, cy - 30 * s), (cx, cy - R * s))
        # g2 (right), g1 (left)
        for yy, side in ((-6, 1), (12, -1)):
            y = cy + yy * s
            A(f'<line class="grid" x1="{cx-22}" y1="{y}" x2="{cx+22}" y2="{y}"/>')
            ex = cx + side * math.sqrt(R * R - yy * yy)
            self.wire((cx + side * 22, y), (round(ex, 1), y))
        # beam plates
        for side in (-1, 1):
            A(f'<path class="beamp" d="M{cx+side*27},{cy-20*s} L{cx+side*31},{cy-6*s} L{cx+side*31},{cy+16*s}"/>')
        A(f'<path class="w" d="M{cx-18},{cy+23*s} L{cx-18},{cy+28*s} L{cx+18},{cy+28*s} L{cx+18},{cy+23*s}"/>')
        self.wire((cx, cy + 28 * s), (cx, cy + R * s))
        ty = cy - R + 4 if not flip else cy + R - 12
        tx = cx - R - 4
        self.text(tx, ty, ref, "tref", "end")
        self.text(tx, ty + 15, typ, "ttyp", "end")
        return dict(a=(cx, cy - R * s), g2=(round(cx + math.sqrt(R*R-36), 1), cy - 6 * s),
                    g1=(round(cx - math.sqrt(R*R-144), 1), cy + 12 * s), k=(cx, cy + R * s))

    def triode(self, cx, cy, ref, typ, gside=-1, R=40, lab=(0, 0)):
        A = self.add
        A(f'<circle class="env" cx="{cx}" cy="{cy}" r="{R}"/>')
        A(f'<line class="anode" x1="{cx-15}" y1="{cy-20}" x2="{cx+15}" y2="{cy-20}"/>')
        self.wire((cx, cy - 20), (cx, cy - R))
        A(f'<line class="grid" x1="{cx-18}" y1="{cy}" x2="{cx+18}" y2="{cy}"/>')
        self.wire((cx + gside * 18, cy), (cx + gside * R, cy))
        A(f'<path class="w" d="M{cx-15},{cy+15} L{cx-15},{cy+20} L{cx+15},{cy+20} L{cx+15},{cy+15}"/>')
        self.wire((cx, cy + 20), (cx, cy + R))
        tx = cx - gside * (R + 6)
        anc = "start" if gside < 0 else "end"
        self.text(tx + lab[0], cy - 8 + lab[1], ref, "tref", anc)
        self.text(tx + lab[0], cy + 7 + lab[1], typ, "ttyp", anc)
        return dict(a=(cx, cy - R), g=(cx + gside * R, cy), k=(cx, cy + R))

    def box(self, x, y, w, h, title, lines=(), cls="blk"):
        self.add(f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/>')
        self.text(x + 12, y + 22, title, "btitle")
        for i, l in enumerate(lines):
            self.text(x + 12, y + 42 + i * 17, l, "bline")

    def svg(self):
        body = "\n".join(self.el)
        return (f'<svg class="sch" viewBox="0 0 {self.w} {self.h}" width="{self.w}" '
                f'role="img" aria-label="{self.title}" xmlns="http://www.w3.org/2000/svg">\n<g transform="translate(0,{self.dy})">{body}</g>\n</svg>')
