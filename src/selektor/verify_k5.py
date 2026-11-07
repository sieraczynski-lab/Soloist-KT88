#!/usr/bin/env python3
"""Weryfikacja eksportu KiCad 5: schemat (.sch + .lib) vs PCB vs wersja KiCad 8."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen

D = os.path.join(gen.ROOT, "kicad5-easyeda") + "/"
err = []

# --- biblioteka
lib = {}
cur = None
for line in open(D + "TubeSel.lib", encoding="utf-8"):
    t = line.split()
    if not t:
        continue
    if t[0] == "DEF":
        cur = t[1]; lib[cur] = {}
    elif t[0] == "X":
        lib[cur][t[2]] = (int(t[3]), int(t[4]))
cache = {}
for line in open(D + "tube_selector-cache.lib", encoding="utf-8"):
    t = line.split()
    if t and t[0] == "DEF":
        cache[t[1]] = True
for k in lib:
    if "TubeSel_" + k not in cache:
        err.append(f"brak {k} w cache")

# --- schemat
txt = open(D + "tube_selector.sch", encoding="utf-8").read()
assert txt.startswith("EESchema Schematic File Version 4") and txt.rstrip().endswith("$EndSCHEMATC")
pins = {}
for c in re.findall(r"\$Comp\n(.*?)\$EndComp", txt, re.S):
    L = c.split("\n")
    sym = L[0].split()[1].split(":")[1]; ref = L[0].split()[2]
    px, py = map(int, L[2].split()[1:3])
    mat = L[-2].split()
    assert mat == ["1", "0", "0", "-1"], mat
    for num, (x, y) in lib[sym].items():
        pins[(ref, num)] = (px + x, py - y)
parent = {}
def find(a):
    parent.setdefault(a, a)
    while parent[a] != a:
        parent[a] = parent[parent[a]]; a = parent[a]
    return a
for a, b, c, d in re.findall(r"Wire Wire Line\n\t(-?\d+) (-?\d+) (-?\d+) (-?\d+)", txt):
    parent[find((int(a), int(b)))] = find((int(c), int(d)))
labels = {}
for x, y, name in re.findall(r"Text Label (-?\d+) (-?\d+) \d+ +\d+ +~ 0\n(\S+)", txt):
    labels.setdefault(name, []).append((int(x), int(y)))
for name, pts in labels.items():
    for a, b in zip(pts, pts[1:]):
        parent[find(a)] = find(b)
gname = {find(pts[0]): n for n, pts in labels.items()}
nc = {(int(x), int(y)) for x, y in re.findall(r"NoConn ~ (-?\d+) (-?\d+)", txt)}
sch = {}
for (ref, num), pt in pins.items():
    if pt in nc:
        continue
    g = find(pt)
    if g not in gname:
        err.append(f"pin {ref}.{num} niepodłączony"); continue
    sch.setdefault(gname[g], set()).add((ref, num))

# --- PCB v5
pcb_txt = open(D + "tube_selector.kicad_pcb").read()
depth = 0
for ch in pcb_txt:
    depth += (ch == "(") - (ch == ")")
    if depth < 0:
        break
if depth != 0:
    err.append(f"PCB: niezbalansowane nawiasy ({depth})")
pcb = {}
for mod in re.findall(r"\(module (.*?)\n  \)", pcb_txt, re.S):
    ref = re.search(r"fp_text reference (\S+)", mod).group(1)
    for num, net in re.findall(r'\(pad (\S+) [^\n]*?\(net \d+ "([^"]+)"\)', mod):
        pcb.setdefault(net.lstrip("/"), set()).add((ref, num))

# --- referencja: wersja KiCad 8 (z danych generatora)
ref8 = {}
for p in gen.parts:
    for num, n in p["nets"].items():
        ref8.setdefault(n, set()).add((p["ref"], num))

for name, a, b in (("sch5 vs pcb5", sch, pcb), ("sch5 vs KiCad8", sch, ref8)):
    ka = {k: frozenset(v) for k, v in a.items()}; kb = {k: frozenset(v) for k, v in b.items()}
    diff = [n for n in set(ka) | set(kb) if ka.get(n) != kb.get(n)]
    print(f"{name}: {len(ka)} / {len(kb)} sieci, różnic: {len(diff)}")
    for n in diff[:10]:
        err.append(f"{name}: {n}")

mods = len(re.findall(r"\(module ", pcb_txt)); zones = len(re.findall(r"\(zone ", pcb_txt))
print(f"PCB v5: {mods} modułów, {zones} stref, symboli w .lib: {len(lib)}")
if err:
    print("BŁĘDY:", *err, sep="\n - "); sys.exit(1)
print("KiCad 5: WSZYSTKO OK")
