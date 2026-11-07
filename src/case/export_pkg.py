import sys, os, zipfile, shutil, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stepw
orig = stepw.prism
REC = {}
def rec(name, color, outer, holes, w0, w1, frame="XY", ref=False, offset=(0, 0, 0)):
    REC[name] = (outer, holes, abs(w1 - w0))
    return orig(name, color, outer, holes, w0, w1, frame, ref, offset)
stepw.prism = rec
import model
from views import *  # renders
out = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(out, "Soloist88_obudowa_v0.4"); shutil.rmtree(D, ignore_errors=True)
os.makedirs(os.path.join(D, "DXF"))
def dxf(path, loops, ox, oy):
    L = ["0", "SECTION", "2", "ENTITIES"]
    for lp in loops:
        if getattr(lp, "circ", None):
            cx, cy, r = lp.circ
            L += ["0", "CIRCLE", "8", "0", "10", "%.4f" % (cx - ox), "20", "%.4f" % (cy - oy), "40", "%.4f" % r]
            continue
        if getattr(lp, "segs", None):
            L += ["0", "POLYLINE", "8", "0", "66", "1", "70", "1"]
            for sg in lp.segs:
                st = stepw.seg_start(sg)
                bulge = 0.0
                if sg[0] == "A":
                    th = sg[4] - sg[3]
                    bulge = math.tan(th / 4)
                L += ["0", "VERTEX", "8", "0", "10", "%.4f" % (st[0] - ox), "20", "%.4f" % (st[1] - oy), "42", "%.6f" % bulge]
            L += ["0", "SEQEND"]
            continue
        L += ["0", "POLYLINE", "8", "0", "66", "1", "70", "1"]
        for (x, y) in lp:
            L += ["0", "VERTEX", "8", "0", "10", "%.4f" % (x - ox), "20", "%.4f" % (y - oy)]
        L += ["0", "SEQEND"]
    L += ["0", "ENDSEC", "0", "EOF"]
    open(path, "w").write("\n".join(L) + "\n")
mat = lambda n: ("aluminium 5754" if n.startswith("AL_") else "stal nierdzewna" if n.startswith("SS_") else "profil stalowy 20x20x1,5 ocynk/czarny - dlugosc" if n.startswith("ST_") else "MDF + fornir")
rows = []
groups = {}
for S in model.parts:
    if S.name.startswith("SS_tulejka"):
        groups.setdefault("SS_tulejka_D10_D4.4_L49.5", 0); groups["SS_tulejka_D10_D4.4_L49.5"] += 1
        continue
    outer, holes, th = REC[S.name]
    xs = [p[0] for p in outer]; ys = [p[1] for p in outer]
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    rows.append((S.name, mat(S.name), th, w, h, len(holes)))
    ox, oy = min(xs), min(ys)
    if S.name.startswith("ST_"):
        continue
    dxf(os.path.join(D, "DXF", S.name + ".dxf"), [outer] + list(holes), ox, oy)
with open(os.path.join(D, "lista_czesci.csv"), "w", encoding="utf-8-sig") as fh:
    fh.write("Czesc;Material;Grubosc [mm];Wymiar A [mm];Wymiar B [mm];Otwory/gniazda;Szt.\n")
    for r in rows:
        fh.write("%s;%s;%.1f;%.1f;%.1f;%d;1\n" % r)
    for k, v in groups.items():
        fh.write("%s;stal nierdzewna (rurka 10x2,8 lub toczona);;10;49,5;;%d\n" % (k, v))
for f in ("Soloist88_obudowa.step", "Soloist88_obudowa_z_elementami.step", "widok_przod.png", "widok_tyl.png", "widok_wnetrze.png", "widok_czesci.png", "widok_trafo.png"):
    shutil.copy(os.path.join(out, f), D)
shutil.copy(os.path.join(out, "CZYTAJ_MNIE_obudowa.txt"), D)
zp = os.path.join(out, "Soloist88_obudowa_v0.4.zip")
if os.path.exists(zp): os.remove(zp)
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(D):
        for f in sorted(files):
            p = os.path.join(root, f); z.write(p, os.path.relpath(p, out))
print(zp, len(rows))
