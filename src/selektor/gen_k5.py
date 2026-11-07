#!/usr/bin/env python3
"""Eksport projektu do formatu KiCad 5.1 (import do EasyEDA Pro).

Korzysta z tych samych danych co gen.py (lista elementów, symbole, footprinty),
więc netlista jest identyczna z wersją KiCad 8. Paczka jest samowystarczalna:
symbole w TubeSel.lib (+ cache), wszystkie footprinty w TubeSel.pretty.
"""
import os, re, shutil, zlib
import gen  # buduje gen.parts przy imporcie

PROJ = gen.PROJ
OUT = os.path.join(gen.ROOT, "kicad5-easyeda")
MIL = 0.0254


def m(v):
    """mm -> mils (siatka 50 mil = 1,27 mm)."""
    return int(round(v / MIL))


def ts(*k):
    """8-znakowy znacznik czasu/UUID w stylu KiCad 5."""
    return f"{zlib.crc32('/'.join(map(str, k)).encode()) & 0xFFFFFFFF:08X}"


def qs(s):
    return '"' + str(s).replace('"', "'") + '"'


def pinname(n):
    return n.replace("~{", "~").replace("}", "") if n.startswith("~{") else n


# ---------------------------------------------------------------- footprinty
def fp_ref(p):
    lib, name = p["fp"]
    return name


def collect_footprints():
    os.makedirs(os.path.join(OUT, "TubeSel.pretty"), exist_ok=True)
    seen = set()
    for p in gen.parts:
        lib, name = p["fp"]
        if name in seen:
            continue
        seen.add(name)
        base = gen.OUT if lib == "TubeSel" else gen.FPLIB
        src = f"{base}/{lib}.pretty/{name}.kicad_mod"
        txt = open(src).read()
        # nazwa modułu i ścieżka modelu 3D jak w KiCad 5
        open(os.path.join(OUT, "TubeSel.pretty", name + ".kicad_mod"), "w").write(txt)
    return seen


# ---------------------------------------------------------------- symbole (.lib)
def lib_text(prefix=""):
    out = ["EESchema-LIBRARY Version 2.4", "#encoding utf-8"]
    used = sorted({p["sym"] for p in gen.parts})
    for name in used:
        s = gen.SYMBOLS[name]
        off = 10 if s["pin_names_hide"] else 30
        out += ["#", f"# {prefix}{name}", "#",
                f'DEF {prefix}{name} {s["ref"]} 0 {off} {"N" if s["pin_numbers_hide"] else "Y"} '
                f'{"N" if s["pin_names_hide"] else "Y"} 1 F N']
        fr, fv = s["fref"], s["fval"]
        hj = "L" if s["justify"] == "left" else "C"
        out.append(f'F0 "{s["ref"]}" {m(fr[0])} {m(fr[1])} 50 H V {hj} CNN')
        out.append(f'F1 "{name}" {m(fv[0])} {m(fv[1])} 50 H V {hj} CNN')
        out.append(f'F2 "" 0 0 50 H I C CNN')
        out.append(f'F3 "" 0 0 50 H I C CNN')
        out.append("DRAW")
        for g in s["gfx"]:
            t = gen.sexp(g)
            fill = gen.kv(t, "fill")
            ft = fill[1][1] if fill and isinstance(fill[1], list) else (fill[1] if fill else "none")
            F = {"none": "N", "background": "f", "outline": "F"}.get(ft, "N")
            w = gen.kv(gen.kv(t, "stroke"), "width")
            wm = m(float(w[1])) if w else 0
            if t[0] == "rectangle":
                a, b = gen.kv(t, "start"), gen.kv(t, "end")
                out.append(f"S {m(float(a[1]))} {m(float(a[2]))} {m(float(b[1]))} {m(float(b[2]))} 0 1 {wm} {F}")
            elif t[0] == "polyline":
                pts = gen.kv(t, "pts")[1:]
                xy = " ".join(f"{m(float(p[1]))} {m(float(p[2]))}" for p in pts)
                out.append(f"P {len(pts)} 0 1 {wm} {xy} {F}")
            elif t[0] == "circle":
                c = gen.kv(t, "center"); r = gen.kv(t, "radius")
                out.append(f"C {m(float(c[1]))} {m(float(c[2]))} {m(float(r[1]))} 0 1 {wm} {F}")
        for num, pname, x, y, a, ln in s["pins"]:
            o = {0: "R", 180: "L", 90: "U", 270: "D"}[int(a)]
            out.append(f"X {pinname(pname)} {num} {m(x)} {m(y)} {m(ln)} {o} 50 50 1 1 P")
        out += ["ENDDRAW", "ENDDEF"]
    out += ["#", "#End Library", ""]
    return "\n".join(out)


# ---------------------------------------------------------------- schemat (.sch)
def write_sch():
    L = ["EESchema Schematic File Version 4", "EELAYER 30 0", "EELAYER END",
         "$Descr A3 16535 11693", "encoding utf-8", "Sheet 1 1",
         f'Title "{gen.TITLE}"', f'Date "{gen.DATE}"', f'Rev "{gen.REV}"', 'Comp "Wzmacniacz lampowy"',
         'Comment1 "4 wejscia stereo, drabinka 6 bit 0-63 dB, mute fail-safe"',
         'Comment2 "Przekazniki Omron G6K-2F-Y 12 V; sterowanie MCP23017 + 2x ULN2803A"',
         'Comment3 ""', 'Comment4 ""', "$EndDescr"]
    for p in gen.parts:
        s = gen.SYMBOLS[p["sym"]]
        sx, sy = p["sch"]
        X, Y = m(sx), m(sy)
        fr, fv = s["fref"], s["fval"]
        hj = "L" if s["justify"] == "left" else "C"
        L += ["$Comp", f'L TubeSel:{p["sym"]} {p["ref"]}', f'U 1 1 {ts("sym", p["ref"])}', f"P {X} {Y}",
              f'F 0 "{p["ref"]}" H {m(sx + fr[0])} {m(sy - fr[1])} 50  0000 {hj} CNN',
              f'F 1 {qs(p["value"])} H {m(sx + fv[0])} {m(sy - fv[1])} 50  0000 {hj} CNN',
              f'F 2 "TubeSel:{fp_ref(p)}" H {X} {Y} 50  0001 C CNN',
              f'F 3 "~" H {X} {Y} 50  0001 C CNN']
        k = 4
        for key, val in p["extra"].items():
            L.append(f'F {k} {qs(val)} H {X} {Y} 50  0001 C CNN {qs(key)}'); k += 1
        L += [f"\t1    {X} {Y}", "\t1    0    0    -1  ", "$EndComp"]
    for p in gen.parts:
        s = gen.SYMBOLS[p["sym"]]
        for pn in s["pins"]:
            num = pn[0]
            x, y, a = gen.pin_abs(p, pn)
            if num in p["nc"]:
                L.append(f"NoConn ~ {m(x)} {m(y)}")
                continue
            dx, dy = gen.outward(a)
            x2, y2 = x + dx * gen.STUB, y + dy * gen.STUB
            L += ["Wire Wire Line", f"\t{m(x)} {m(y)} {m(x2)} {m(y2)}"]
            spin = {0: 0, 90: 1, 180: 2, 270: 3}[gen.label_angle(a)]
            L += [f"Text Label {m(x2)} {m(y2)} {spin}    50   ~ 0", p["nets"][num]]
    # opisy: przepisane z wygenerowanego schematu KiCad 8
    tree = gen.sexp(open(os.path.join(gen.OUT, PROJ + ".kicad_sch")).read())
    for t in [x for x in tree if isinstance(x, list) and x and x[0] == "text"]:
        at = gen.kv(t, "at"); font = gen.kv(gen.kv(t, "effects"), "font")
        size = float(gen.kv(font, "size")[1]); bold = 1 if "bold" in font else 0
        txt = t[1].replace("\\n", "\n").replace("\n", "\\n")
        L += [f"Text Notes {m(float(at[1]))} {m(float(at[2]))} 0    {m(size)}   ~ {bold}", txt]
    L.append("$EndSCHEMATC")
    open(os.path.join(OUT, PROJ + ".sch"), "w", encoding="utf-8").write("\n".join(L) + "\n")


# ---------------------------------------------------------------- PCB (v5)
def net5(n):
    return "/" + n


def write_pcb():
    nets = gen.all_nets()
    o = ["(kicad_pcb (version 20171130) (host pcbnew 5.1.12)",
         "  (general (thickness 1.6) (drawings 0) (tracks 0) (zones 0) (modules %d) (nets %d))" % (len(gen.parts), len(nets) + 1),
         "  (page A4)",
         f'  (title_block (title "{gen.TITLE}") (date {gen.DATE}) (rev {gen.REV}) (company "Wzmacniacz lampowy"))',
         "  (layers (0 F.Cu signal) (31 B.Cu signal) (32 B.Adhes user) (33 F.Adhes user) (34 B.Paste user) (35 F.Paste user)"
         " (36 B.SilkS user) (37 F.SilkS user) (38 B.Mask user) (39 F.Mask user) (40 Dwgs.User user) (41 Cmts.User user)"
         " (42 Eco1.User user) (43 Eco2.User user) (44 Edge.Cuts user) (45 Margin user) (46 B.CrtYd user) (47 F.CrtYd user)"
         " (48 B.Fab user) (49 F.Fab user))",
         "  (setup (last_trace_width 0.3) (trace_clearance 0.2) (zone_clearance 0.3) (zone_45_only no) (trace_min 0.2)"
         " (via_size 0.6) (via_drill 0.3) (via_min_size 0.5) (via_min_drill 0.3) (uvia_size 0.3) (uvia_drill 0.1)"
         " (uvias_allowed no) (uvia_min_size 0.2) (uvia_min_drill 0.1) (edge_width 0.1) (segment_width 0.2)"
         " (pcb_text_width 0.15) (pcb_text_size 1 1) (mod_edge_width 0.12) (mod_text_size 1 1) (mod_text_width 0.15)"
         " (pad_size 1.524 1.524) (pad_drill 0.762) (pad_to_mask_clearance 0) (aux_axis_origin 0 0) (visible_elements FFFFFF7F))",
         '  (net 0 "")']
    for n, i in nets.items():
        o.append(f"  (net {i} {qs(net5(n))})")
    audio = [n for n in nets if n not in ("GND", "+12V", "CHASSIS", "DGND", "+3V3", "SDA", "SCL")
             and not n.startswith(("COIL", "DRV", "MCP_"))]
    rest = [n for n in nets if n not in audio]
    for cls, members, w, cl in (("Default", rest, 0.3, 0.2), ("Audio", audio, 0.4, 0.3)):
        o.append(f'  (net_class {cls} "{cls}" (clearance {cl}) (trace_width {w}) (via_dia 0.6) (via_drill 0.3)'
                 f' (uvia_dia 0.3) (uvia_drill 0.1) ' + " ".join(f"(add_net {qs(net5(n))})" for n in members) + ")")

    F = gen.f
    for p in gen.parts:
        lib, name = p["fp"]
        fp = gen.load_fp(lib, name)
        x, y, a = p["pcb"]
        A = f" {F(a)}" if a else ""
        L = [f"  (module TubeSel:{name} (layer F.Cu) (tedit 0) (tstamp {ts('fp', p['ref'])})",
             f"    (at {F(x)} {F(y)}{A})",
             f"    (descr {qs(fp['descr'])}) (tags {qs(fp['tags'])})",
             f"    (path /{ts('sym', p['ref'])})"]
        if fp["attr"] == "smd":
            L.append("    (attr smd)")
        L.append(f"    (fp_text reference {p['ref']} (at {F(fp['ref_at'][0])} {F(fp['ref_at'][1])}{A}) (layer F.SilkS)"
                 f" (effects (font (size 0.8 0.8) (thickness 0.12))))")
        L.append(f"    (fp_text value {qs(p['value'])} (at {F(fp['val_at'][0])} {F(fp['val_at'][1])}{A}) (layer F.Fab)"
                 f" (effects (font (size 0.8 0.8) (thickness 0.12))))")
        for kind, x1, y1, x2, y2, lay, w in fp["gfx"]:
            if kind == "line":
                L.append(f"    (fp_line (start {F(x1)} {F(y1)}) (end {F(x2)} {F(y2)}) (layer {lay}) (width {F(w)}))")
            else:
                L.append(f"    (fp_circle (center {F(x1)} {F(y1)}) (end {F(x2)} {F(y2)}) (layer {lay}) (width {F(w)}))")
        for pad in fp["pads"]:
            num = "\"\"" if pad["type"] == "np_thru_hole" else pad["num"]
            pr = (pad["rot"] + a) % 360
            PR = f" {F(pr)}" if pr else ""
            s = f"    (pad {num} {pad['type']} {pad['shape']} (at {F(pad['x'])} {F(pad['y'])}{PR}) (size {F(pad['w'])} {F(pad['h'])})"
            if pad["drill"] is not None:
                s += f" (drill {F(pad['drill'])})"
            s += " (layers " + " ".join(pad["layers"]) + ")"
            if pad["rr"] is not None:
                s += f" (roundrect_rratio {F(pad['rr'])})"
            if pad["type"] != "np_thru_hole" and pad["num"] in p["nets"]:
                nn = p["nets"][pad["num"]]
                s += f" (net {nets[nn]} {qs(net5(nn))})"
            L.append(s + ")")
        if fp["model"]:
            mdl = fp["model"].replace("${KICAD8_3DMODEL_DIR}", "${KISYS3DMOD}")
            L.append(f"    (model {mdl} (at (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))")
        L.append("  )")
        o.append("\n".join(L))

    # obrys (narożniki proste - najbezpieczniejsze przy imporcie)
    x1, y1, x2, y2 = gen.X0, gen.Y0, gen.X0 + gen.BW, gen.Y0 + gen.BH
    for s_, e_ in (((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)), ((x2, y2), (x1, y2)), ((x1, y2), (x1, y1))):
        o.append(f"  (gr_line (start {F(s_[0])} {F(s_[1])}) (end {F(e_[0])} {F(e_[1])}) (layer Edge.Cuts) (width 0.1))")

    # napisy i strefy przepisane z wersji KiCad 8
    tree = gen.sexp(open(os.path.join(gen.OUT, PROJ + ".kicad_pcb")).read())
    for t in [x for x in tree if isinstance(x, list) and x and x[0] == "gr_text"]:
        at = gen.kv(t, "at"); lay = gen.kv(t, "layer")[1]
        font = gen.kv(gen.kv(t, "effects"), "font")
        sz = gen.kv(font, "size"); th = gen.kv(font, "thickness")
        just = gen.kv(gen.kv(t, "effects"), "justify")
        mir = " (justify mirror)" if just and "mirror" in just else ""
        ang = f" {at[3]}" if len(at) > 3 else ""
        o.append(f"  (gr_text {qs(t[1])} (at {at[1]} {at[2]}{ang}) (layer {lay})"
                 f" (effects (font (size {sz[1]} {sz[2]}) (thickness {th[1]})){mir}))")
    for z in [x for x in tree if isinstance(x, list) and x and x[0] == "zone"]:
        net = gen.kv(z, "net_name")[1]; lay = gen.kv(z, "layer")[1]
        prio = gen.kv(z, "priority"); pts = gen.kv(gen.kv(z, "polygon"), "pts")[1:]
        P = f" (priority {prio[1]})" if prio and prio[1] != "0" else ""
        xy = " ".join(f"(xy {p[1]} {p[2]})" for p in pts)
        o.append(f"  (zone (net {nets[net.lstrip('/')]}) (net_name {qs(net)}) (layer {lay}) (tstamp {ts('z', net, lay)})"
                 f" (hatch edge 0.508){P}\n    (connect_pads (clearance 0.3))\n    (min_thickness 0.254)\n"
                 f"    (fill (arc_segments 32) (thermal_gap 0.4) (thermal_bridge_width 0.4))\n    (polygon (pts {xy})))")
    o.append(")")
    open(os.path.join(OUT, PROJ + ".kicad_pcb"), "w").write("\n".join(o) + "\n")


def write_misc():
    open(os.path.join(OUT, "TubeSel.lib"), "w", encoding="utf-8").write(lib_text())
    # cache w stylu KiCad 5 (nazwy z prefiksem biblioteki)
    open(os.path.join(OUT, PROJ + "-cache.lib"), "w", encoding="utf-8").write(lib_text(prefix="TubeSel_"))
    open(os.path.join(OUT, "sym-lib-table"), "w").write(
        "(sym_lib_table\n  (lib (name TubeSel)(type Legacy)(uri ${KIPRJMOD}/TubeSel.lib)(options \"\")(descr \"Symbole projektu\"))\n)\n")
    open(os.path.join(OUT, "fp-lib-table"), "w").write(
        "(fp_lib_table\n  (lib (name TubeSel)(type KiCad)(uri ${KIPRJMOD}/TubeSel.pretty)(options \"\")(descr \"Footprinty projektu\"))\n)\n")
    open(os.path.join(OUT, PROJ + ".pro"), "w").write(
        "update=22/10/2026 02:00:00\nversion=1\nlast_client=kicad\n[general]\nversion=1\nRootSch=\nBoardNm=\n"
        "[pcbnew]\nversion=1\nLastNetListRead=\nUseCmpFile=1\nPadDrill=0.762\nPadDrillOvalY=0.762\nPadSizeH=1.524\n"
        "PadSizeV=1.524\nPcbTextSizeV=1\nPcbTextSizeH=1\nPcbTextThickness=0.15\nModuleTextSizeV=1\nModuleTextSizeH=1\n"
        "ModuleTextSizeThickness=0.15\nSolderMaskClearance=0\nSolderMaskMinWidth=0\nDrawSegmentWidth=0.2\n"
        "BoardOutlineThickness=0.1\nModuleOutlineThickness=0.12\n[cvpcb]\nversion=1\nNetIExt=net\n"
        "[eeschema]\nversion=1\nLibDir=\n[eeschema/libraries]\n")
    for fn in ("BOM.csv", "JLCPCB_BOM.csv", "LCSC_zamowienie.csv"):
        shutil.copy(os.path.join(gen.OUT, fn), os.path.join(OUT, fn))


if __name__ == "__main__":
    shutil.rmtree(os.path.join(OUT, "TubeSel.pretty"), ignore_errors=True)
    os.makedirs(OUT, exist_ok=True)
    n = collect_footprints()
    write_sch(); write_pcb(); write_misc()
    print("OK KiCad 5:", len(gen.parts), "elementów,", len(n), "footprintów")
