"""Orthographic z-buffer renderer for faceted solids (faces with holes) -> PNG."""
import sys, os, math
import numpy as np
from matplotlib.path import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stepw import newell, dot

def view_matrix(azim, elev):
    a, e = math.radians(azim), math.radians(elev)
    # camera looks from direction d (pointing from scene to camera)
    d = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
    up = np.array([0, 0, 1.0])
    r = np.cross(up, d); r /= np.linalg.norm(r)
    u = np.cross(d, r)
    return np.stack([r, u, d])   # rows: screen x, screen y, depth (towards camera)

def render(solids, path, azim=-60, elev=25, W=1600, H=1150, title="", skip=(), light=(-0.3, -0.8, 0.9), bbox=None):
    M = view_matrix(azim, elev)
    faces = []
    allp = []
    for S in solids:
        if any(S.name.startswith(p) for p in skip):
            continue
        for loops in S.faces:
            P = [np.array(l, float) @ M.T for l in loops]
            n = np.array(newell(loops[0]), float); n /= (np.linalg.norm(n) or 1)
            faces.append((S, loops, P, n))
            allp.append(P[0])
    pts = np.vstack(allp)
    mn, mx = pts.min(0), pts.max(0)
    pad = 20
    sc = min((W - 2 * pad) / (mx[0] - mn[0]), (H - 2 * pad - 40) / (mx[1] - mn[1]))
    ox, oy = pad - mn[0] * sc + (W - 2 * pad - (mx[0] - mn[0]) * sc) / 2, pad + 40 - mn[1] * sc
    zbuf = np.full((H, W), -1e18)
    img = np.ones((H, W, 3))
    L = np.array(light, float); L /= np.linalg.norm(L)
    ndir = M[2]
    for S, loops, P, n in faces:
        if np.dot(n, ndir) <= 1e-6:       # back-face
            continue
        loops2 = [np.column_stack([p[:, 0] * sc + ox, H - (p[:, 1] * sc + oy)]) for p in P]
        xy0 = loops2[0]
        x0, y0 = max(int(xy0[:, 0].min()), 0), max(int(xy0[:, 1].min()), 0)
        x1, y1 = min(int(xy0[:, 0].max()) + 1, W - 1), min(int(xy0[:, 1].max()) + 1, H - 1)
        if x1 < x0 or y1 < y0:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        q = np.column_stack([gx.ravel(), gy.ravel()])
        inside = Path(xy0).contains_points(q)
        for hl in loops2[1:]:
            hb = (hl[:, 0].min(), hl[:, 1].min(), hl[:, 0].max(), hl[:, 1].max())
            sel = (q[:, 0] >= hb[0]) & (q[:, 0] <= hb[2]) & (q[:, 1] >= hb[1]) & (q[:, 1] <= hb[3]) & inside
            if sel.any():
                idx = np.nonzero(sel)[0]
                inside[idx[Path(hl).contains_points(q[idx])]] = False
        inside = inside.reshape(gx.shape)
        if not inside.any():
            continue
        # depth from plane: n_view . (X - X0) = 0
        nv = M @ n
        X0 = P[0][0]
        sx = (gx - ox) / sc; sy = ((H - gy) - oy) / sc
        if abs(nv[2]) < 1e-9:
            continue
        depth = X0[2] - (nv[0] * (sx - X0[0]) + nv[1] * (sy - X0[1])) / nv[2]
        zb = zbuf[y0:y1 + 1, x0:x1 + 1]
        upd = inside & (depth > zb)
        zb[upd] = depth[upd]
        k = 0.42 + 0.58 * max(0.0, float(np.dot(n, L)))
        col = np.array(S.color) * k
        im = img[y0:y1 + 1, x0:x1 + 1]
        im[upd] = np.clip(col, 0, 1)
    # edge darkening: depth discontinuities
    dz = np.zeros_like(zbuf)
    valid = zbuf > -1e17
    zz = np.where(valid, zbuf, np.nan)
    gxz = np.abs(np.diff(zz, axis=1, prepend=np.nan)); gyz = np.abs(np.diff(zz, axis=0, prepend=np.nan))
    edge = (np.nan_to_num(gxz, nan=1e9) > 2.0) | (np.nan_to_num(gyz, nan=1e9) > 2.0)
    edge &= valid
    img[edge] *= 0.55
    fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
    plt.imshow(img); plt.axis("off")
    if title:
        plt.text(W / 2, 28, title, ha="center", fontsize=16)
    plt.subplots_adjust(0, 0, 1, 1)
    plt.savefig(path)
    plt.close(fig)
