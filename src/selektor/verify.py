#!/usr/bin/env python3
"""Niezależna weryfikacja wygenerowanych plików KiCad (bez KiCada).

1. Składnia S-expression (zbalansowane nawiasy, pełne parsowanie).
2. Netlista ze schematu odtworzona z GEOMETRII (piny, przewody, etykiety).
3. Netlista z PCB odczytana z padów; porównanie 1:1 ze schematem.
4. Kolizje courtyardów i mieszczenie się w obrysie płytki.
5. Symulacja drabinki: tłumienie dla 64 kodów, impedancje.
"""
import math, os, re, sys, itertools
import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "hardware", "selektor")
P = os.path.join(ROOT, "kicad", "tube_selector")
errors = []


def sexp(txt):
    toks = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', txt)
    depth = 0
    for t in toks:
        depth += t == "("
        depth -= t == ")"
        if depth < 0:
            raise ValueError("nadmiarowy nawias")
    if depth != 0:
        raise ValueError(f"niezbalansowane nawiasy: {depth}")
    st = [[]]
    for t in toks:
        if t == "(":
            st.append([])
        elif t == ")":
            x = st.pop(); st[-1].append(x)
        else:
            st[-1].append(t[1:-1] if t.startswith('"') else t)
    assert len(st) == 1 and len(st[0]) == 1
    return st[0][0]


def kids(n, key):
    return [x for x in n if isinstance(x, list) and x and x[0] == key]


def kid(n, key):
    k = kids(n, key)
    return k[0] if k else None


# ---------------------------------------------------------------- 1. składnia
trees = {}
for ext in ("kicad_sch", "kicad_pcb"):
    trees[ext] = sexp(open(f"{P}.{ext}").read())
sexp(open(os.path.join(ROOT, "kicad", "TubeSel.kicad_sym")).read())
print("[1] Składnia S-expr: OK (sch, pcb, sym)")

# ---------------------------------------------------------------- 2. schemat
sch = trees["kicad_sch"]
lib = {}
for s in kid(sch, "lib_symbols")[1:]:
    name = s[1]
    pins = {}
    for sub in kids(s, "symbol"):
        for p in kids(sub, "pin"):
            at = kid(p, "at"); num = kid(p, "number")[1]
            pins[num] = (float(at[1]), float(at[2]))
    lib[name] = pins

R = lambda v: round(v * 1000)
pinpts = {}      # (ref,pin) -> pkt
values = {}
for s in kids(sch, "symbol"):
    lid = kid(s, "lib_id")[1]
    at = kid(s, "at"); sx, sy, ang = float(at[1]), float(at[2]), float(at[3])
    assert ang == 0, "obsługiwany tylko kąt 0"
    props = {p[1]: p[2] for p in kids(s, "property")}
    ref = props["Reference"]; values[ref] = props["Value"]
    for num, (px, py) in lib[lid].items():
        pinpts[(ref, num)] = (R(sx + px), R(sy - py))

parent = {}
def find(a):
    parent.setdefault(a, a)
    while parent[a] != a:
        parent[a] = parent[parent[a]]; a = parent[a]
    return a
def union(a, b):
    parent[find(a)] = find(b)

wire_pts = set()
for w in kids(sch, "wire"):
    pts = kid(w, "pts")[1:]
    a = (R(float(pts[0][1])), R(float(pts[0][2]))); b = (R(float(pts[1][1])), R(float(pts[1][2])))
    union(a, b); wire_pts |= {a, b}

labels = {}
for l in kids(sch, "label"):
    at = kid(l, "at"); pt = (R(float(at[1])), R(float(at[2])))
    if pt not in wire_pts and pt not in set(pinpts.values()):
        errors.append(f"etykieta {l[1]} nie leży na końcu przewodu ani pinie")
    labels.setdefault(l[1], []).append(pt)
for name, pts in labels.items():
    for a, b in zip(pts, pts[1:]):
        union(a, b)

ncs = {(R(float(kid(n, "at")[1])), R(float(kid(n, "at")[2]))) for n in kids(sch, "no_connect")}

group_name = {}
for name, pts in labels.items():
    g = find(pts[0])
    if g in group_name and group_name[g] != name:
        errors.append(f"zwarcie etykiet {group_name[g]} i {name}")
    group_name[g] = name

sch_nets = {}
for (ref, num), pt in pinpts.items():
    if pt in ncs:
        continue
    g = find(pt)
    if g not in group_name:
        errors.append(f"pin {ref}.{num} niepodłączony (brak etykiety/no_connect)")
        continue
    sch_nets.setdefault(group_name[g], set()).add((ref, num))
for n, m in sch_nets.items():
    if len(m) < 2:
        errors.append(f"sieć {n} ma tylko jeden pin: {m}")
print(f"[2] Schemat: {len(pinpts)} pinów, {len(sch_nets)} sieci, {len(ncs)} no_connect")

# ---------------------------------------------------------------- 3. PCB
pcb = trees["kicad_pcb"]
pcb_nets = {}
fps = []
for fp in kids(pcb, "footprint"):
    props = {p[1]: p[2] for p in kids(fp, "property")}
    ref = props["Reference"]
    at = kid(fp, "at"); x, y = float(at[1]), float(at[2]); a = float(at[3]) if len(at) > 3 else 0.0
    crt = [(float(kid(g, "start")[1]), float(kid(g, "start")[2]), float(kid(g, "end")[1]), float(kid(g, "end")[2]))
           for g in kids(fp, "fp_line") if kid(g, "layer")[1] == "F.CrtYd"]
    circ = [(float(kid(g, "center")[1]), float(kid(g, "center")[2]), float(kid(g, "end")[1]), float(kid(g, "end")[2]))
            for g in kids(fp, "fp_circle") if kid(g, "layer")[1] == "F.CrtYd"]
    if crt:
        xs = [c[0] for c in crt] + [c[2] for c in crt]; ys = [c[1] for c in crt] + [c[3] for c in crt]
        box = (min(xs), min(ys), max(xs), max(ys))
    else:
        cx, cy, ex, ey = circ[0]; r = math.hypot(ex - cx, ey - cy)
        box = (cx - r, cy - r, cx + r, cy + r)
    pads = []
    for p in kids(fp, "pad"):
        num = p[1]; net = kid(p, "net")
        pat = kid(p, "at")
        pads.append((num, float(pat[1]), float(pat[2]), net[2] if net else None))
        if net:
            pcb_nets.setdefault(net[2].lstrip("/"), set()).add((ref, num))
    fps.append(dict(ref=ref, x=x, y=y, a=a, box=box, pads=pads, value=props["Value"]))

# porównanie
sch_set = {k: frozenset(v) for k, v in sch_nets.items()}
pcb_set = {k: frozenset(v) for k, v in pcb_nets.items()}
for n in sorted(set(sch_set) | set(pcb_set)):
    if sch_set.get(n) != pcb_set.get(n):
        errors.append(f"różnica sieci {n}: sch={sorted(sch_set.get(n, []))} pcb={sorted(pcb_set.get(n, []))}")
# piny symbolu vs pady footprintu
sym_pins = {}
for (ref, num) in pinpts:
    sym_pins.setdefault(ref, set()).add(num)
for f_ in fps:
    padnums = {p[0] for p in f_["pads"] if p[0]}
    if padnums != sym_pins.get(f_["ref"], set()):
        errors.append(f"{f_['ref']}: pady {sorted(padnums)} != piny {sorted(sym_pins.get(f_['ref'], set()))}")
print(f"[3] PCB: {len(fps)} footprintów, {len(pcb_nets)} sieci; zgodność ze schematem: "
      f"{'OK' if not [e for e in errors if 'sieci' in e or 'pady' in e] else 'BŁĄD'}")


# ---------------------------------------------------------------- 4. kolizje
def rot(x, y, a):
    r = math.radians(a)
    return x * math.cos(r) + y * math.sin(r), -x * math.sin(r) + y * math.cos(r)

abs_boxes = {}
for f_ in fps:
    x0, y0, x1, y1 = f_["box"]
    cs = [rot(px, py, f_["a"]) for px, py in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    xs = [f_["x"] + c[0] for c in cs]; ys = [f_["y"] + c[1] for c in cs]
    abs_boxes[f_["ref"]] = (min(xs), min(ys), max(xs), max(ys))

edges = [kid(g, "start") for g in kids(pcb, "gr_line") if kid(g, "layer")[1] == "Edge.Cuts"]
ex = [float(e[1]) for e in edges]; ey = [float(e[2]) for e in edges]
bx0, by0, bx1, by1 = min(ex), min(ey), max(ex), max(ey)
n_ov = 0
for a, b in itertools.combinations(abs_boxes, 2):
    A, B = abs_boxes[a], abs_boxes[b]
    if A[0] < B[2] - 1e-6 and B[0] < A[2] - 1e-6 and A[1] < B[3] - 1e-6 and B[1] < A[3] - 1e-6:
        errors.append(f"kolizja courtyardów {a} / {b}"); n_ov += 1
for r_, B in abs_boxes.items():
    if B[0] < bx0 or B[1] < by0 or B[2] > bx1 or B[3] > by1:
        errors.append(f"{r_} wystaje poza płytkę {B}")
print(f"[4] Kolizje courtyardów: {n_ov}; płytka {bx1 - bx0:.0f} x {by1 - by0:.0f} mm")

# odległość padów od krawędzi
for f_ in fps:
    for num, px, py, net in f_["pads"]:
        dx, dy = rot(px, py, f_["a"])
        X, Y = f_["x"] + dx, f_["y"] + dy
        d = min(X - bx0, bx1 - X, Y - by0, by1 - Y)
        if d < 1.0:
            errors.append(f"pad {f_['ref']}.{num} {d:.2f} mm od krawędzi")


# ---------------------------------------------------------------- 5. drabinka
def parse_val(v):
    v = v.split()[0]
    if v.endswith("k"):
        return float(v[:-1]) * 1e3
    if v.endswith("R"):
        return float(v[:-1])
    return float(v)

# drabinka odtworzona z netlisty PCB (kanał L)
res = {f_["ref"]: (parse_val(f_["value"]), [p[3].lstrip("/") for p in f_["pads"] if p[3]])
       for f_ in fps if f_["ref"].startswith("R") and f_["value"] != "0R"}
relay_nets = {f_["ref"]: {p[0]: (p[3].lstrip("/") if p[3] else None) for p in f_["pads"]}
              for f_ in fps if f_["ref"].startswith("K")}


def simulate(code, ch="L", rsrc=0.0):
    """Analiza węzłowa toru: źródło -> BUS -> drabinka -> OUT (+ terminator)."""
    pole = {"L": ("3", "2", "4"), "R": ("6", "7", "5")}[ch]
    edges_ = []
    for ref, (val, nn) in res.items():
        if len(nn) == 2 and all(n.endswith("_" + ch) or n == "GND" for n in nn):
            edges_.append((nn[0], nn[1], val))
    for i in range(6):
        k = relay_nets[f"K{5 + i}"]
        com, nc, no = (k[p] for p in pole)
        on = (code >> i) & 1
        edges_.append((com, no if on else nc, 1e-3))
    nodes = sorted({n for e in edges_ for n in e[:2]} - {"GND"} | {f"BUS_{ch}"})
    idx = {n: i for i, n in enumerate(nodes)}
    Gm = np.zeros((len(nodes), len(nodes))); I = np.zeros(len(nodes))
    def stamp(a, b, g):
        for x, y, s in ((a, a, 1), (b, b, 1), (a, b, -1), (b, a, -1)):
            if x != "GND" and y != "GND":
                Gm[idx[x], idx[y]] += s * g
    for a, b, r in edges_:
        stamp(a, b, 1 / r)
    # źródło 1 V przez rsrc (Norton)
    rs = max(rsrc, 1e-3)
    Gm[idx[f"BUS_{ch}"], idx[f"BUS_{ch}"]] += 1 / rs; I[idx[f"BUS_{ch}"]] += 1 / rs
    v = np.linalg.solve(Gm, I)
    vin = v[idx[f"BUS_{ch}"]]; vout = v[idx[f"OUT_{ch}"]]
    zin = vin / ((1 - vin) / rs)
    return 20 * math.log10(vout), zin

worst = 0; zmin, zmax = 1e9, 0
for code in range(64):
    db, zin = simulate(code)
    worst = max(worst, abs(db + code)); zmin = min(zmin, zin); zmax = max(zmax, zin)
    dbr, _ = simulate(code, "R")
    if abs(dbr - db) > 1e-6:
        errors.append(f"kanały L/R różnią się dla kodu {code}")
# impedancja wyjściowa: źródło zwarte, wstrzyknięcie prądu w OUT
def zout(code):
    a, _ = simulate(code, rsrc=1e-3)
    # metoda: Zout = Rth; z dzielnika z obciążeniem 1 MΩ różnica pomijalna -> licz bezpośrednio
    return None
print(f"[5] Drabinka: max błąd tłumienia {worst:.3f} dB (64 kody), Zin {zmin/1e3:.2f}..{zmax/1e3:.2f} kΩ, L=R")

# ---------------------------------------------------------------- wynik
if errors:
    print("\nBŁĘDY:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("\nWSZYSTKO OK")
