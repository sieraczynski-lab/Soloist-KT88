import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import model
from stepw import newell, dot

def shade(color, n, light=(-0.4, -0.7, 0.9)):
    L = math.sqrt(dot(light, light)); nl = math.sqrt(dot(n, n)) or 1
    k = 0.45 + 0.55 * max(0, dot(n, light) / (L * nl))
    return tuple(min(1, c * k) for c in color)

def render(solids, path, elev=24, azim=-58, title="", skip=()):
    fig = plt.figure(figsize=(14, 10), dpi=110)
    ax = fig.add_subplot(111, projection="3d")
    polys, cols = [], []
    for S in solids:
        if any(S.name.startswith(p) for p in skip):
            continue
        for loops in S.faces:
            n = newell(loops[0]); nl = math.sqrt(dot(n, n)) or 1; n = (n[0] / nl, n[1] / nl, n[2] / nl)
            polys.append(loops[0]); cols.append(shade(S.color, n))
            for h in loops[1:]:
                off = [(p[0] + n[0] * 0.05, p[1] + n[1] * 0.05, p[2] + n[2] * 0.05) for p in h]
                polys.append(off); cols.append((0.08, 0.08, 0.1))
    pc = Poly3DCollection(polys, facecolors=cols, edgecolors=(0, 0, 0, 0.12), linewidths=0.2)
    ax.add_collection3d(pc)
    ax.set_xlim(-40, 460); ax.set_ylim(-60, 500); ax.set_zlim(-20, 300)
    ax.set_box_aspect((500, 560, 320))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_title(title, fontsize=14)
    plt.tight_layout()
    plt.savefig(path)
    plt.close(fig)

if __name__ == "__main__":
    out = os.path.dirname(os.path.abspath(__file__))
    allp = model.parts + model.ref
    render(allp, os.path.join(out, "widok_przod.png"), 22, -62, "Soloist 88 - obudowa (propozycja), widok z przodu")
    render(allp, os.path.join(out, "widok_tyl.png"), 24, 120, "Widok z tylu", skip=())
    render(allp, os.path.join(out, "widok_wnetrze.png"), 38, -55, "Wnetrze (bez pokrywy, drewna i dachu trafo)",
           skip=("AL_pokrywa", "DREWNO", "AL_trafo_dach", "SS_", "REF_pret", "REF_nakretka"))
