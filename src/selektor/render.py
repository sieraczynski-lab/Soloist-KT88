#!/usr/bin/env python3
"""Podgląd PCB (rozmieszczenie, pady, ratsnest) i schematu — render z plików KiCad."""
import math, os, re, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.join(REPO, "hardware", "selektor")
P = os.path.join(ROOT, "kicad", "tube_selector")
OUTD = os.path.join(REPO, "docs", "img")
import os; os.makedirs(OUTD, exist_ok=True)


def sexp(txt):
    toks = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', txt)
    st = [[]]
    for t in toks:
        if t == "(":
            st.append([])
        elif t == ")":
            x = st.pop(); st[-1].append(x)
        else:
            st[-1].append(t[1:-1] if t.startswith('"') else t)
    return st[0][0]


kids = lambda n, k: [x for x in n if isinstance(x, list) and x and x[0] == k]
def kid(n, k):
    r = kids(n, k); return r[0] if r else None


def rot(x, y, a):
    r = math.radians(a)
    return x * math.cos(r) + y * math.sin(r), -x * math.sin(r) + y * math.cos(r)


# ------------------------------------------------------------------ PCB
pcb = sexp(open(P + ".kicad_pcb").read())
fig, ax = plt.subplots(figsize=(13, 9.6), dpi=130)
ax.set_facecolor("#0d3b1e")
# obrys
for g in kids(pcb, "gr_line"):
    if kid(g, "layer")[1] == "Edge.Cuts":
        s, e = kid(g, "start"), kid(g, "end")
        ax.plot([float(s[1]), float(e[1])], [float(s[2]), float(e[2])], color="#f5d000", lw=1.5)
for g in kids(pcb, "gr_arc"):
    s, m, e = kid(g, "start"), kid(g, "mid"), kid(g, "end")
    ax.plot([float(s[1]), float(m[1]), float(e[1])], [float(s[2]), float(m[2]), float(e[2])], color="#f5d000", lw=1.5)

COL = {"GND": "#4a90d9", "+12V": "#e05050"}
padpos = {}
for fp in kids(pcb, "footprint"):
    props = {p[1]: p[2] for p in kids(fp, "property")}
    ref = props["Reference"]
    at = kid(fp, "at"); X, Y = float(at[1]), float(at[2]); A = float(at[3]) if len(at) > 3 else 0
    for g in kids(fp, "fp_line"):
        lay = kid(g, "layer")[1]
        if lay not in ("F.CrtYd", "F.SilkS"):
            continue
        s, e = kid(g, "start"), kid(g, "end")
        x1, y1 = rot(float(s[1]), float(s[2]), A); x2, y2 = rot(float(e[1]), float(e[2]), A)
        ax.plot([X + x1, X + x2], [Y + y1, Y + y2], color="#d0d0d0" if lay == "F.SilkS" else "#ff66cc",
                lw=0.6 if lay == "F.SilkS" else 0.35, alpha=0.9 if lay == "F.SilkS" else 0.6)
    for g in kids(fp, "fp_circle"):
        if kid(g, "layer")[1] != "F.CrtYd":
            continue
        c, e = kid(g, "center"), kid(g, "end")
        r = math.hypot(float(e[1]) - float(c[1]), float(e[2]) - float(c[2]))
        ax.add_patch(Circle((X, Y), r, fill=False, ec="#ff66cc", lw=0.35, alpha=0.6))
    for p in kids(fp, "pad"):
        pat = kid(p, "at"); sz = kid(p, "size"); net = kid(p, "net")
        px, py = rot(float(pat[1]), float(pat[2]), A)
        w, h = float(sz[1]), float(sz[2])
        pa = float(pat[3]) if len(pat) > 3 else 0
        if round(pa) % 180 == 90:
            w, h = h, w
        nn = net[2].lstrip("/") if net else None
        col = COL.get(nn, "#c88a3a") if p[2] != "np_thru_hole" else "#111"
        if p[2] in ("thru_hole", "np_thru_hole") and p[3] == "circle":
            ax.add_patch(Circle((X + px, Y + py), w / 2, fc=col, ec="none"))
        else:
            ax.add_patch(Rectangle((X + px - w / 2, Y + py - h / 2), w, h, fc=col, ec="none"))
        if kid(p, "drill"):
            d = float(kid(p, "drill")[1])
            ax.add_patch(Circle((X + px, Y + py), d / 2, fc="#0d3b1e" if p[2] != "np_thru_hole" else "#000", ec="none"))
        if nn:
            padpos.setdefault(nn, []).append((X + px, Y + py))
    fs = 5.5 if ref[0] in "KJ" else 3.6
    ax.text(X, Y, ref, color="white", fontsize=fs, ha="center", va="center", weight="bold", zorder=5)

# ratsnest (minimalne drzewo rozpinające na sieć, bez GND)
for nn, pts in padpos.items():
    if nn == "GND" or len(pts) < 2:
        continue
    done = [pts[0]]; rest = pts[1:]
    while rest:
        best = min(((math.dist(a, b), a, b) for a in done for b in rest))
        _, a, b = best
        ax.plot([a[0], b[0]], [a[1], b[1]], color="#ffffff" if not nn.startswith(("COIL", "+12")) else "#ff8080",
                lw=0.35, alpha=0.55, zorder=4)
        done.append(b); rest.remove(b)

for g in kids(pcb, "gr_text"):
    at = kid(g, "at"); lay = kid(g, "layer")[1]
    if lay == "F.SilkS":
        ax.text(float(at[1]), float(at[2]), g[1], color="#f0f0f0", fontsize=4.3, ha="center", va="center", zorder=6)

ax.set_xlim(97, 199); ax.set_ylim(176.5, 97); ax.set_aspect("equal")
ax.set_title("TubeSel v0.5 — rozmieszczenie (strona TOP), ratsnest: biały = audio, czerwony = cewki/+12V; "
             "pady: niebieski = GND, czerwony = +12V", fontsize=8)
ax.tick_params(labelsize=6)
fig.tight_layout()
fig.savefig(f"{OUTD}/selektor_plytka.png")
plt.close(fig)

# ------------------------------------------------------------------ schemat
sch = sexp(open(P + ".kicad_sch").read())
lib = {}
for s in kid(sch, "lib_symbols")[1:]:
    g = {"rect": [], "pins": [], "circ": [], "poly": []}
    for sub in kids(s, "symbol"):
        for r in kids(sub, "rectangle"):
            a, b = kid(r, "start"), kid(r, "end")
            g["rect"].append((float(a[1]), float(a[2]), float(b[1]), float(b[2])))
        for c in kids(sub, "circle"):
            cc = kid(c, "center"); g["circ"].append((float(cc[1]), float(cc[2]), float(kid(c, "radius")[1])))
        for pl in kids(sub, "polyline"):
            g["poly"].append([(float(p[1]), float(p[2])) for p in kid(pl, "pts")[1:]])
        for p in kids(sub, "pin"):
            at = kid(p, "at")
            g["pins"].append((float(at[1]), float(at[2]), float(at[3]), float(kid(p, "length")[1]),
                              kid(p, "name")[1], kid(p, "number")[1]))
    g["shownames"] = not any(isinstance(x, list) and x[0] == "pin_names" and "hide" in x for x in s)
    g["shownums"] = not any(isinstance(x, list) and x[0] == "pin_numbers" for x in s)
    lib[s[1]] = g

fig, ax = plt.subplots(figsize=(23.4, 16.5), dpi=110)
ax.add_patch(Rectangle((5, 5), 410, 287, fill=False, ec="#8a1a1a", lw=0.8))
for s in kids(sch, "symbol"):
    g = lib[kid(s, "lib_id")[1]]
    at = kid(s, "at"); sx, sy = float(at[1]), float(at[2])
    props = {p[1]: (p[2], p) for p in kids(s, "property")}
    for x0, y0, x1, y1 in g["rect"]:
        ax.add_patch(Rectangle((sx + min(x0, x1), sy - max(y0, y1)), abs(x1 - x0), abs(y1 - y0),
                               fill=True, fc="#fffbe0", ec="#8a1a1a", lw=0.8))
    for cx, cy, r in g["circ"]:
        ax.add_patch(Circle((sx + cx, sy - cy), r, fill=False, ec="#8a1a1a", lw=1.2))
    for pl in g["poly"]:
        ax.plot([sx + x for x, y in pl], [sy - y for x, y in pl], color="#8a1a1a", lw=0.8)
    for x, y, a, ln, name, num in g["pins"]:
        dx, dy = {0: (1, 0), 180: (-1, 0), 90: (0, 1), 270: (0, -1)}[int(a)]
        x1, y1 = sx + x, sy - y
        x2, y2 = x1 + dx * ln, y1 - dy * ln
        ax.plot([x1, x2], [y1, y2], color="#8a1a1a", lw=0.8)
        if g["shownames"] and name != "~":
            ha = "left" if dx > 0 else "right" if dx < 0 else "center"
            ax.text(x2 + dx * 0.6, y2, name, fontsize=4.5, ha=ha, va="center", color="#006060")
        if g["shownums"]:
            ax.text((x1 + x2) / 2, y1 - 0.5, num, fontsize=3.8, ha="center", va="bottom", color="#8a1a1a")
    for key in ("Reference", "Value"):
        v, p = props[key]
        pat = kid(p, "at")
        just = kid(kid(p, "effects"), "justify")
        ha = "left" if just and "left" in just else "center"
        ax.text(float(pat[1]), float(pat[2]), v, fontsize=5.5 if key == "Reference" else 4.8, ha=ha, va="center",
                color="#006060" if key == "Reference" else "#444", weight="bold" if key == "Reference" else "normal")
for w in kids(sch, "wire"):
    pts = kid(w, "pts")[1:]
    ax.plot([float(pts[0][1]), float(pts[1][1])], [float(pts[0][2]), float(pts[1][2])], color="#008000", lw=0.9)
for l in kids(sch, "label"):
    at = kid(l, "at"); a = int(float(at[3]))
    ha = {0: "left", 180: "right", 90: "center", 270: "center"}[a]
    va = {0: "center", 180: "center", 90: "bottom", 270: "top"}[a]
    ax.text(float(at[1]) + (0.4 if a == 0 else -0.4 if a == 180 else 0),
            float(at[2]) + (-0.4 if a == 90 else 0.4 if a == 270 else 0), l[1], fontsize=4.6,
            rotation=90 if a in (90, 270) else 0, ha=ha, va=va, color="#000")
for n in kids(sch, "no_connect"):
    at = kid(n, "at"); x, y = float(at[1]), float(at[2])
    ax.plot([x - .8, x + .8], [y - .8, y + .8], color="#0000c0", lw=0.8)
    ax.plot([x - .8, x + .8], [y + .8, y - .8], color="#0000c0", lw=0.8)
for t in kids(sch, "text"):
    at = kid(t, "at"); size = float(kid(kid(kid(t, "effects"), "font"), "size")[1])
    bold = "bold" in kid(kid(t, "effects"), "font")
    ax.text(float(at[1]), float(at[2]), t[1].replace("\\n", "\n"), fontsize=size * 2.6, ha="left", va="bottom",
            color="#000080", weight="bold" if bold else "normal")
ax.set_xlim(0, 420); ax.set_ylim(297, 0); ax.set_aspect("equal"); ax.axis("off")
fig.tight_layout()
fig.savefig(f"{OUTD}/selektor_schemat.png")
print("ok")
