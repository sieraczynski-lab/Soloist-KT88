"""Minimal STEP AP214 writer: faceted B-rep solids (planar faces, polygon loops with holes),
assembly of named parts with colours. Plus geometry helpers for extruded plates."""
import math, datetime

# ---------------------------------------------------------------- 2D helpers
class Circ(list):
    """Polygon approximation (for preview) + exact circle (cx, cy, r) for STEP/DXF."""
    circ = None

class Segs(list):
    """Polygon approximation + exact segment list: ('L', p0, p1) / ('A', c, r, a0, a1, ccw)."""
    segs = None

def circle(cx, cy, d, n=None):
    if n is None:
        n = 48 if d >= 40 else (32 if d >= 12 else 16)
    r = d / 2
    c = Circ([(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)])
    c.circ = (cx, cy, r)
    return c

def rect(u0, v0, u1, v1):
    return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]

def rrect(u0, v0, u1, v1, r, n=6):
    pts = []
    for (cx, cy, a0) in ((u1 - r, v0 + r, -90), (u1 - r, v1 - r, 0), (u0 + r, v1 - r, 90), (u0 + r, v0 + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    S = Segs(pts)
    h = math.pi / 2
    S.segs = [("L", (u0 + r, v0), (u1 - r, v0)), ("A", (u1 - r, v0 + r), r, -h, 0.0, True),
              ("L", (u1, v0 + r), (u1, v1 - r)), ("A", (u1 - r, v1 - r), r, 0.0, h, True),
              ("L", (u1 - r, v1), (u0 + r, v1)), ("A", (u0 + r, v1 - r), r, h, 2 * h, True),
              ("L", (u0, v1 - r), (u0, v0 + r)), ("A", (u0 + r, v0 + r), r, 2 * h, 3 * h, True)]
    return S

# ---------------------------------------------------------------- exact segments
def seg_pts(sg, n=4):
    if sg[0] == "L":
        return [sg[1]]
    _, c, r, a0, a1, cw = sg
    return [(c[0] + r * math.cos(a0 + (a1 - a0) * k / n), c[1] + r * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n)]

def seg_start(sg):
    return sg[1] if sg[0] == "L" else (sg[1][0] + sg[2] * math.cos(sg[3]), sg[1][1] + sg[2] * math.sin(sg[3]))

def seg_end(sg):
    return sg[2] if sg[0] == "L" else (sg[1][0] + sg[2] * math.cos(sg[4]), sg[1][1] + sg[2] * math.sin(sg[4]))

def seg_rev(sg):
    if sg[0] == "L":
        return ("L", sg[2], sg[1])
    return ("A", sg[1], sg[2], sg[4], sg[3], not sg[5])

def exact_loop(loop):
    if getattr(loop, "circ", None):
        cx, cy, r = loop.circ
        segs = [("A", (cx, cy), r, 0.0, math.pi, True), ("A", (cx, cy), r, math.pi, 2 * math.pi, True)]
    elif getattr(loop, "segs", None):
        segs = list(loop.segs)
    else:
        segs = [("L", loop[i], loop[(i + 1) % len(loop)]) for i in range(len(loop))]
    pts = [p for sg in segs for p in seg_pts(sg)]
    if area2(pts) < 0:
        segs = [seg_rev(sg) for sg in reversed(segs)]
    return segs

def area2(poly):
    return sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly))) / 2

def ccw(poly):
    return poly if area2(poly) > 0 else poly[::-1]

def edge_features(u0, v0, u1, v1, feats):
    """Rectangle outline with features. feats: dict edge -> list of (a, b, d) where a<b along the edge axis
    (u for bottom/top, v for left/right), d>0 protrudes outward, d<0 notches inward. Returns CCW polygon."""
    P = [(u0, v0)]
    for (a, b, d) in sorted(feats.get("bottom", [])):
        P += [(a, v0), (a, v0 - d), (b, v0 - d), (b, v0)]
    P.append((u1, v0))
    for (a, b, d) in sorted(feats.get("right", [])):
        P += [(u1, a), (u1 + d, a), (u1 + d, b), (u1, b)]
    P.append((u1, v1))
    for (a, b, d) in sorted(feats.get("top", []), reverse=True):
        P += [(b, v1), (b, v1 + d), (a, v1 + d), (a, v1)]
    P.append((u0, v1))
    for (a, b, d) in sorted(feats.get("left", []), reverse=True):
        P += [(u0, b), (u0 - d, b), (u0 - d, a), (u0, a)]
    # remove duplicates
    out = []
    for p in P:
        if not out or (abs(out[-1][0] - p[0]) > 1e-9 or abs(out[-1][1] - p[1]) > 1e-9):
            out.append(p)
    if abs(out[0][0] - out[-1][0]) < 1e-9 and abs(out[0][1] - out[-1][1]) < 1e-9:
        out.pop()
    return out

# ---------------------------------------------------------------- 3D frames
FRAMES = {
    "XY": lambda u, v, w: (u, v, w),
    "XZ": lambda u, v, w: (u, w, v),   # plate with normal along Y
    "YZ": lambda u, v, w: (w, u, v),   # plate with normal along X
}

def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])

def newell(loop):
    nx = ny = nz = 0.0
    for i in range(len(loop)):
        a, b = loop[i], loop[(i + 1) % len(loop)]
        nx += (a[1] - b[1]) * (a[2] + b[2]); ny += (a[2] - b[2]) * (a[0] + b[0]); nz += (a[0] - b[0]) * (a[1] + b[1])
    return (nx, ny, nz)

class Solid:
    def __init__(self, name, color, ref=False):
        self.name, self.color, self.ref = name, color, ref
        self.exact = None
        self.faces = []   # list of loops (first outer), loops = list of 3D points, oriented

    def add_face(self, loops):
        self.faces.append(loops)

def prism(name, color, outer, holes, w0, w1, frame="XY", ref=False, offset=(0, 0, 0)):
    """Extrude 2D outer polygon with holes between w0 and w1 in given frame."""
    F = FRAMES[frame]
    def P(u, v, w):
        x, y, z = F(u, v, w)
        return (round(x + offset[0], 4), round(y + offset[1], 4), round(z + offset[2], 4))
    S = Solid(name, color, ref)
    S.exact = (exact_loop(outer), [exact_loop(h) for h in holes], w0, w1, P)
    outer = ccw(outer)
    holes = [ccw(h) for h in holes]
    wdir = sub(P(0, 0, 1), P(0, 0, 0))
    def oriented(loop, want):
        n = newell(loop)
        return loop if dot(n, want) > 0 else loop[::-1]
    up = wdir; down = (-wdir[0], -wdir[1], -wdir[2])
    S.add_face([oriented([P(u, v, w1) for u, v in outer], up)] + [oriented([P(u, v, w1) for u, v in h], down) for h in holes])
    S.add_face([oriented([P(u, v, w0) for u, v in outer], down)] + [oriented([P(u, v, w0) for u, v in h], up) for h in holes])
    for loop, is_hole in [(outer, False)] + [(h, True) for h in holes]:
        n = len(loop)
        for i in range(n):
            (ua, va), (ub, vb) = loop[i], loop[(i + 1) % n]
            du, dv = ub - ua, vb - va
            out2 = (-dv, du) if is_hole else (dv, -du)
            o3 = sub(P(ua + out2[0], va + out2[1], w0), P(ua, va, w0))
            q = [P(ua, va, w0), P(ub, vb, w0), P(ub, vb, w1), P(ua, va, w1)]
            S.add_face([oriented(q, o3)])
    return S

def cyl(name, color, cx, cy, d, z0, z1, axis="Z", ref=True, hole=None, n=None):
    """Cylinder (polygonal). axis Z: (cx,cy)=(x,y); axis Y: (cx,cy)=(x,z), z0..z1 along y; axis X: (cx,cy)=(y,z)."""
    holes = [circle(cx, cy, hole, n)] if hole else []
    fr = {"Z": "XY", "Y": "XZ", "X": "YZ"}[axis]
    return prism(name, color, circle(cx, cy, d, n), holes, z0, z1, fr, ref)

def box(name, color, x0, y0, z0, x1, y1, z1, ref=True):
    return prism(name, color, rect(x0, y0, x1, y1), [], z0, z1, "XY", ref)

# ---------------------------------------------------------------- checks
def check_closed(S):
    E = {}
    for f in S.faces:
        for loop in f:
            for i in range(len(loop)):
                e = (loop[i], loop[(i + 1) % len(loop)])
                E[e] = E.get(e, 0) + 1
    bad = 0
    for (a, b), c in E.items():
        if c != 1 or E.get((b, a), 0) != 1:
            bad += 1
    return bad

def volume(S):
    v = 0.0
    for f in S.faces:
        for loop in f:
            o = loop[0]
            for i in range(1, len(loop) - 1):
                v += dot(o, cross(loop[i], loop[i + 1])) / 6
    return v

# ---------------------------------------------------------------- STEP writer
class StepWriter:
    def __init__(self):
        self.lines = []; self.n = 0
    def add(self, s):
        self.n += 1
        self.lines.append("#%d=%s;" % (self.n, s))
        return "#%d" % self.n

def fmt(x):
    s = ("%.4f" % x).rstrip("0")
    if s.endswith("."): s += "0"
    if s in ("-0.0",): s = "0.0"
    return s


# ---------------------------------------------------------------- exact (advanced) B-rep
def _unit(v):
    l = math.sqrt(dot(v, v)); return (v[0] / l, v[1] / l, v[2] / l)

def write_advanced(A, S, ctx_unused=None):
    outer, holes, w0, w1, P = S.exact
    O = P(0, 0, 0)
    U = _unit(sub(P(1, 0, 0), O)); V = _unit(sub(P(0, 1, 0), O)); Wd = _unit(sub(P(0, 0, 1), O))
    if w1 < w0:
        w0, w1 = w1, w0
    UxV = cross(U, V)
    cache = {}
    def cp(q):
        k = ("P", q)
        if k not in cache:
            cache[k] = A("CARTESIAN_POINT('',(%s,%s,%s))" % (fmt(q[0]), fmt(q[1]), fmt(q[2])))
        return cache[k]
    def dr(d):
        d = _unit(d); k = ("D", tuple(round(x, 9) for x in d))
        if k not in cache:
            cache[k] = A("DIRECTION('',(%s,%s,%s))" % tuple(fmt(x) for x in d))
        return cache[k]
    def g(u, v, w):
        x, y, z = P(u, v, w); return (round(x, 4), round(y, 4), round(z, 4))
    def vp(q):
        k = ("V", q)
        if k not in cache:
            cache[k] = A("VERTEX_POINT('',%s)" % cp(q))
        return cache[k]
    def ax(origin, zdir, xdir):
        return A("AXIS2_PLACEMENT_3D('',%s,%s,%s)" % (cp(origin), dr(zdir), dr(xdir)))
    loops = [(outer, False)] + [(h, True) for h in holes]
    # edges per loop
    E = []   # per loop: list of dict(bot, top, vert_start)
    for segs, is_hole in loops:
        el = []
        for sg in segs:
            (su, sv), (eu, ev) = seg_start(sg), seg_end(sg)
            rec = {}
            for lvl, w in (("bot", w0), ("top", w1)):
                a, b = g(su, sv, w), g(eu, ev, w)
                if sg[0] == "L":
                    d = sub(b, a); L = math.sqrt(dot(d, d))
                    crv = A("LINE('',%s,%s)" % (cp(a), A("VECTOR('',%s,%s)" % (dr(d), fmt(L)))))
                    sense = ".T."
                else:
                    c3 = g(sg[1][0], sg[1][1], w)
                    crv = A("CIRCLE('',%s,%s)" % (ax(c3, UxV, U), fmt(sg[2])))
                    sense = ".T." if sg[5] else ".F."
                rec[lvl] = A("EDGE_CURVE('',%s,%s,%s,%s)" % (vp(a), vp(b), crv, sense))
            pb, pt = g(su, sv, w0), g(su, sv, w1)
            rec["vert"] = A("EDGE_CURVE('',%s,%s,%s,.T.)" % (vp(pb), vp(pt), A("LINE('',%s,%s)" % (cp(pb), A("VECTOR('',%s,%s)" % (dr(Wd), fmt(w1 - w0)))))))
            el.append(rec)
        E.append(el)
    faces = []
    def oe(edge, fwd):
        return (edge, fwd)
    def loop_entity(items):
        return A("EDGE_LOOP('',(%s))" % ",".join(A("ORIENTED_EDGE('',*,*,%s,%s)" % (e, ".T." if f else ".F.")) for e, f in items))
    def orient(items, samples, want):
        n = newell(samples)
        if dot(n, want) < 0:
            items = [(e, not f) for e, f in reversed(items)]
        return items
    # side faces
    for li, (segs, is_hole) in enumerate(loops):
        el = E[li]; nseg = len(segs)
        for i, sg in enumerate(segs):
            nxt = el[(i + 1) % nseg]
            items = [oe(el[i]["bot"], True), oe(nxt["vert"], True), oe(el[i]["top"], False), oe(el[i]["vert"], False)]
            pts2 = seg_pts(sg, 6) + [seg_end(sg)]
            samples = [g(u, v, w0) for u, v in pts2] + [g(u, v, w1) for u, v in reversed(pts2)]
            # desired outward normal at segment middle
            if sg[0] == "L":
                (su, sv), (eu, ev) = sg[1], sg[2]; tu, tv = eu - su, ev - sv
                mu, mv = (su + eu) / 2, (sv + ev) / 2
            else:
                am = (sg[3] + sg[4]) / 2
                mu, mv = sg[1][0] + sg[2] * math.cos(am), sg[1][1] + sg[2] * math.sin(am)
                tu, tv = (-math.sin(am), math.cos(am)) if sg[5] else (math.sin(am), -math.cos(am))
            n2 = (-tv, tu) if is_hole else (tv, -tu)
            want = (n2[0] * U[0] + n2[1] * V[0], n2[0] * U[1] + n2[1] * V[1], n2[0] * U[2] + n2[1] * V[2])
            items = orient(items, samples, want)
            bound = A("FACE_OUTER_BOUND('',%s,.T.)" % loop_entity(items))
            if sg[0] == "L":
                surf = A("PLANE('',%s)" % ax(g(mu, mv, w0), want, Wd))
                same = ".T."
            else:
                c3 = g(sg[1][0], sg[1][1], w0)
                surf = A("CYLINDRICAL_SURFACE('',%s,%s)" % (ax(c3, Wd, U if abs(dot(U, Wd)) < 0.9 else V), fmt(sg[2])))
                radial = sub(g(mu, mv, w0), c3)
                same = ".T." if dot(radial, want) > 0 else ".F."
            faces.append(A("ADVANCED_FACE('',(%s),%s,%s)" % (bound, surf, same)))
    # caps
    for lvl, w, want in (("top", w1, Wd), ("bot", w0, (-Wd[0], -Wd[1], -Wd[2]))):
        bounds = []
        for li, (segs, is_hole) in enumerate(loops):
            items = [oe(E[li][i][lvl], True) for i in range(len(segs))]
            samples = [g(u, v, w) for sg in segs for (u, v) in seg_pts(sg, 6)]
            target = want if not is_hole else (-want[0], -want[1], -want[2])
            items = orient(items, samples, target)
            bounds.append(A("%s('',%s,.T.)" % ("FACE_OUTER_BOUND" if not is_hole else "FACE_BOUND", loop_entity(items))))
        surf = A("PLANE('',%s)" % ax(g(0, 0, w), want, U if abs(dot(U, want)) < 0.9 else V))
        faces.append(A("ADVANCED_FACE('',(%s),%s,.T.)" % (",".join(bounds), surf)))
    sh = A("CLOSED_SHELL('',(%s))" % ",".join(faces))
    return A("MANIFOLD_SOLID_BREP('%s',%s)" % (S.name, sh))

def write_step(path, solids, assy_name="ASSEMBLY"):
    W = StepWriter(); A = W.add
    ac = A("APPLICATION_CONTEXT('automotive design')")
    A("APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,%s)" % ac)
    pc = A("PRODUCT_CONTEXT('',%s,'mechanical')" % ac)
    pdc = A("PRODUCT_DEFINITION_CONTEXT('part definition',%s,'design')" % ac)
    lu = A("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
    au = A("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
    su = A("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
    um = A("UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-04),%s,'distance_accuracy_value','confusion accuracy')" % lu)
    ctx = A("(GEOMETRIC_REPRESENTATION_CONTEXT(3)GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((%s))GLOBAL_UNIT_ASSIGNED_CONTEXT((%s,%s,%s))REPRESENTATION_CONTEXT('Context3D','3D'))" % (um, lu, au, su))
    o = A("CARTESIAN_POINT('',(0.,0.,0.))"); dz = A("DIRECTION('',(0.,0.,1.))"); dx = A("DIRECTION('',(1.,0.,0.))")
    def axis():
        return A("AXIS2_PLACEMENT_3D('',%s,%s,%s)" % (o, dz, dx))
    def product(name):
        p = A("PRODUCT('%s','%s','',(%s))" % (name, name, pc))
        pf = A("PRODUCT_DEFINITION_FORMATION('','',%s)" % p)
        pd = A("PRODUCT_DEFINITION('design','',%s,%s)" % (pf, pdc))
        pds = A("PRODUCT_DEFINITION_SHAPE('','',%s)" % pd)
        return p, pd, pds
    prods = []
    ap, apd, apds = product(assy_name); prods.append(ap)
    assy_items = [axis()]
    styled = []
    colors = {}
    for i, S in enumerate(solids):
        p, pd, pds = product(S.name); prods.append(p)
        br = write_advanced(A, S)
        ax_child = axis()
        sr = A("ADVANCED_BREP_SHAPE_REPRESENTATION('%s',(%s,%s),%s)" % (S.name, ax_child, br, ctx))
        A("SHAPE_DEFINITION_REPRESENTATION(%s,%s)" % (pds, sr))
        # colour
        c = S.color
        if c not in colors:
            colors[c] = A("COLOUR_RGB('',%s,%s,%s)" % tuple(fmt(x) for x in c))
        fasc = A("FILL_AREA_STYLE_COLOUR('',%s)" % colors[c])
        fas = A("FILL_AREA_STYLE('',(%s))" % fasc)
        ssfa = A("SURFACE_STYLE_FILL_AREA(%s)" % fas)
        sss = A("SURFACE_SIDE_STYLE('',(%s))" % ssfa)
        ssu = A("SURFACE_STYLE_USAGE(.BOTH.,%s)" % sss)
        psa = A("PRESENTATION_STYLE_ASSIGNMENT((%s))" % ssu)
        styled.append(A("STYLED_ITEM('color',(%s),%s)" % (psa, br)))
        # assembly link
        ax_parent = axis(); assy_items.append(ax_parent)
        nauo = A("NEXT_ASSEMBLY_USAGE_OCCURRENCE('%d','%s','',%s,%s,$)" % (i + 1, S.name, apd, pd))
        pdsn = A("PRODUCT_DEFINITION_SHAPE('','',%s)" % nauo)
        idt = A("ITEM_DEFINED_TRANSFORMATION('','',%s,%s)" % (ax_child, ax_parent))
        rr = "PLACEHOLDER_ASSY_SR"
        W.lines.append(("RR", idt, sr, pdsn))
    asr = A("SHAPE_REPRESENTATION('%s',(%s),%s)" % (assy_name, ",".join(assy_items), ctx))
    A("SHAPE_DEFINITION_REPRESENTATION(%s,%s)" % (apds, asr))
    # resolve relationships
    final = []
    for ln in W.lines:
        if isinstance(ln, tuple):
            _, idt, sr, pdsn = ln
            W.n += 1; rrid = "#%d" % W.n
            final.append("%s=(REPRESENTATION_RELATIONSHIP('','',%s,%s)REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION(%s)SHAPE_REPRESENTATION_RELATIONSHIP());" % (rrid, sr, asr, idt))
            W.n += 1
            final.append("#%d=CONTEXT_DEPENDENT_SHAPE_REPRESENTATION(%s,%s);" % (W.n, rrid, pdsn))
        else:
            final.append(ln)
    W.lines = final
    A("MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION('',(%s),%s)" % (",".join(styled), ctx))
    A("PRODUCT_RELATED_PRODUCT_CATEGORY('part',$,(%s))" % ",".join(prods))
    now = datetime.datetime(2026, 10, 19, 20, 0, 0).isoformat()
    head = ["ISO-10303-21;", "HEADER;", "FILE_DESCRIPTION(('Soloist 88 - obudowa'),'2;1');",
            "FILE_NAME('%s','%s',('Claude'),(''),'stepw.py','','');" % (path.split('/')[-1], now),
            "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));", "ENDSEC;", "DATA;"]
    with open(path, "w") as fh:
        fh.write("\n".join(head + W.lines + ["ENDSEC;", "END-ISO-10303-21;", ""]))
