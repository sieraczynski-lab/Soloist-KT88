"""Generator of KiCad 4 legacy schematic + library + kicad_pcb (version 4) for EasyEDA Standard import.

All footprints are generated here and embedded in the PCB, all modules are placed with rotation 0
(orientation is baked into the footprint geometry) to keep importers happy.
"""
import math, csv, os, itertools

# =====================================================================================
# Footprints  (mm, y down).  pad = dict(num, x, y, shape, w, h, drill, drill_w(optional))
# =====================================================================================
class FP:
    def __init__(self, name, pads, rects=(), circles=(), lines=(), keepout=None, note=""):
        self.name, self.pads = name, pads
        self.rects, self.circles, self.lines = list(rects), list(circles), list(lines)
        self.note = note
        xs, ys = [], []
        for p in pads:
            xs += [p["x"] - p["w"] / 2, p["x"] + p["w"] / 2]; ys += [p["y"] - p["h"] / 2, p["y"] + p["h"] / 2]
        for (x1, y1, x2, y2) in self.rects:
            xs += [x1, x2]; ys += [y1, y2]
        for (cx, cy, r) in self.circles:
            xs += [cx - r, cx + r]; ys += [cy - r, cy + r]
        self.bbox = keepout or (min(xs), min(ys), max(xs), max(ys))

def _pad(num, x, y, w, drill, shape=None, h=None, dw=None):
    return dict(num=str(num), x=round(x, 4), y=round(y, 4), shape=shape or ("rect" if str(num) == "1" else "circle"),
                w=w, h=h or w, drill=drill, dw=dw)

def _rot(fp_pads, rects, vertical):
    if not vertical:
        return fp_pads, rects
    for p in fp_pads:
        p["x"], p["y"] = -p["y"], p["x"]
        p["w"], p["h"] = p["h"], p["w"]
    rects = [(-y2, x1, -y1, x2) for (x1, y1, x2, y2) in rects]
    return fp_pads, rects

def axial(name, pitch, blen, bdia, drill=1.0, pad=2.0, v=False, square1=False):
    pads = [_pad(1, -pitch / 2, 0, pad, drill, "rect" if square1 else "circle"), _pad(2, pitch / 2, 0, pad, drill)]
    rects = [(-blen / 2, -bdia / 2, blen / 2, bdia / 2)]
    pads, rects = _rot(pads, rects, v)
    return FP(name + ("_V" if v else ""), pads, rects)

def box_cap(name, pitch, L, W, drill=1.0, pad=2.0, v=False):
    pads = [_pad(1, -pitch / 2, 0, pad, drill, "circle"), _pad(2, pitch / 2, 0, pad, drill)]
    rects = [(-L / 2, -W / 2, L / 2, W / 2)]
    pads, rects = _rot(pads, rects, v)
    return FP(name + ("_V" if v else ""), pads, rects)

def radial_cp(name, D, pitch, drill=1.0, pad=2.0):
    pads = [_pad(1, -pitch / 2, 0, pad, drill, "rect"), _pad(2, pitch / 2, 0, pad, drill)]
    return FP(name, pads, circles=[(0, 0, D / 2)])

def snapin(name, D, pitch=10.0):
    pads = [_pad(1, -pitch / 2, 0, 3.6, 2.0, "rect"), _pad(2, pitch / 2, 0, 3.6, 2.0)]
    return FP(name, pads, circles=[(0, 0, D / 2)])

def noval(name="Noval_B9A_PCB"):
    r = 11.89 / 2
    pads = []
    for n in range(1, 10):
        a = math.radians(90 - 36 * n)
        pads.append(_pad(n, r * math.cos(a), r * math.sin(a), 2.4, 1.3, "rect" if n == 1 else "circle"))
    return FP(name, pads, circles=[(0, 0, 11.0)], note="Podstawka PCB B9A, widok od strony elementów")

def to220v(name, hs=(20, 16)):
    pads = [_pad(1, -2.54, 0, 1.8, 1.2, "rect", 2.6), _pad(2, 0, 0, 1.8, 1.2, "oval", 2.6), _pad(3, 2.54, 0, 1.8, 1.2, "oval", 2.6)]
    rects = [(-5.1, -3.2, 5.1, 1.5)]
    if hs:
        rects.append((-hs[0] / 2, -3.2 - hs[1], hs[0] / 2, -3.2))
    return FP(name, pads, rects, note="Radiator za tylną ścianką obudowy TO-220")

def trimmer3296(name="Trim_3296W"):
    pads = [_pad(1, -2.54, 0, 1.7, 0.9, "rect"), _pad(2, 0, 0, 1.7, 0.9), _pad(3, 2.54, 0, 1.7, 0.9)]
    return FP(name, pads, [(-4.8, -2.6, 4.8, 2.4)])

def wirepad(name="WirePad_3.5", d=3.5, drill=1.5):
    return FP(name, [_pad(1, 0, 0, d, drill, "circle")], circles=[(0, 0, d / 2 + 0.6)])

def testpoint(name="TestPoint_2"):
    return FP(name, [_pad(1, 0, 0, 2.2, 1.0, "circle")], circles=[(0, 0, 1.6)])

def header(name, n, pitch=2.54, v=True):
    pads = [_pad(i + 1, 0, (i - (n - 1) / 2) * pitch, 1.7, 1.0, "rect" if i == 0 else "circle") for i in range(n)]
    rects = [(-1.27, -n * pitch / 2, 1.27, n * pitch / 2)]
    if not v:
        for p in pads:
            p["x"], p["y"] = p["y"], p["x"]
        rects = [(-n * pitch / 2, -1.27, n * pitch / 2, 1.27)]
    return FP(name, pads, rects)

def dip(name, n, row=7.62):
    half = n // 2
    pads = []
    for i in range(half):
        pads.append(_pad(i + 1, -row / 2, (i - (half - 1) / 2) * 2.54, 1.6, 0.8, "rect" if i == 0 else "oval", 2.0))
    for i in range(half):
        pads.append(_pad(half + i + 1, row / 2, ((half - 1) / 2 - i) * 2.54, 1.6, 0.8, "oval", 2.0))
    return FP(name, pads, [(-row / 2 + 1.3, -half * 1.27 - 0.3, row / 2 - 1.3, half * 1.27 + 0.3)])

def relay(name, poles, L=29.0, W=12.7):
    """Approximate Finder 40.31 / 40.52 style layout (verify against datasheet!)."""
    pads = [_pad("A1", -L / 2 + 3.2, -3.75, 2.2, 1.3, "rect"), _pad("A2", -L / 2 + 3.2, 3.75, 2.2, 1.3)]
    if poles == 1:
        pads += [_pad("11", -L / 2 + 8.2, 0, 2.6, 1.5), _pad("12", L / 2 - 3.2, -3.75, 2.6, 1.5), _pad("14", L / 2 - 3.2, 3.75, 2.6, 1.5)]
    else:
        pads += [_pad("11", -L / 2 + 8.2, -3.75, 2.4, 1.3), _pad("21", -L / 2 + 8.2, 3.75, 2.4, 1.3),
                 _pad("12", L / 2 - 8.2, -3.75, 2.4, 1.3), _pad("22", L / 2 - 8.2, 3.75, 2.4, 1.3),
                 _pad("14", L / 2 - 3.2, -3.75, 2.4, 1.3), _pad("24", L / 2 - 3.2, 3.75, 2.4, 1.3)]
    return FP(name, pads, [(-L / 2, -W / 2, L / 2, W / 2)], note="Rozstaw wyprowadzeń przybliżony: podmień na footprint z biblioteki LCSC")

def esp32_devkit(name="ESP32-S3-DevKitC-1"):
    pads = []
    for i in range(22):
        y = (i - 10.5) * 2.54
        pads.append(_pad("L%d" % (i + 1), -11.43, y, 1.7, 1.0, "rect" if i == 0 else "circle"))
        pads.append(_pad("R%d" % (i + 1), 11.43, y, 1.7, 1.0, "rect" if i == 0 else "circle"))
    return FP(name, pads, [(-12.75, -31.5, 12.75, 31.5)], note="Rozstaw rzędów 22,86 mm: sprawdź na swoim module")

def ads1115_mod(name="ADS1115_Module"):
    pads = [_pad(i + 1, (i - 4.5) * 2.54, 0, 1.7, 1.0, "rect" if i == 0 else "circle") for i in range(10)]
    return FP(name, pads, [(-14, -1.5, 14, 16.0)])

def mounting_hole(name="MountingHole_M3"):
    return FP(name, [dict(num="", x=0, y=0, shape="np", w=3.2, h=3.2, drill=3.2, dw=None)], circles=[(0, 0, 3.6)])

def cap_box_axial(name, box_pitch=27.5, box=(31.5, 11.0), ax_pitch=52.0, ax=(46.0, 22.0)):
    """Vertical: box film cap pads + alternative axial cap pads on the same nets (pads 1/1, 2/2)."""
    pads = [_pad(1, 0, -box_pitch / 2, 2.4, 1.2, "rect"), _pad(2, 0, box_pitch / 2, 2.4, 1.2),
            _pad(1, 0, -ax_pitch / 2, 2.6, 1.4, "rect"), _pad(2, 0, ax_pitch / 2, 2.6, 1.4)]
    rects = [(-box[1] / 2, -box[0] / 2, box[1] / 2, box[0] / 2), (-ax[1] / 2, -ax[0] / 2, ax[1] / 2, ax[0] / 2)]
    return FP(name, pads, rects, note="Pola pod kondensator prostopadloscienny (raster 27,5) LUB osiowy (raster 52, max 46x22 mm)")

def fuse_dual(name="Fuseholder_5x20_P22.5_or_6.3x32_P30"):
    """Closed PCB fuse holder: 5x20 (pitch 22.5) OR 6.3x32 (pitch 30) on the same nets."""
    pads = [_pad(1, -11.25, 0, 2.8, 1.5, "rect"), _pad(2, 11.25, 0, 2.8, 1.5),
            _pad(1, -15.0, 0, 2.8, 1.5, "rect"), _pad(2, 15.0, 0, 2.8, 1.5)]
    rects = [(-14.0, -5.0, 14.0, 5.0), (-20.0, -6.0, 20.0, 6.0)]
    return FP(name, pads, rects, note="Oprawka 5x20 (raster 22,5) LUB 6,3x32 (raster 30) - wymiary przyblizone")

def terminal(name, n, pitch, drill, pad, depth, v=False):
    """PCB screw terminal block, n poles in a row (pin 1 square)."""
    pads = [_pad(i + 1, (i - (n - 1) / 2) * pitch, 0, pad, drill, "rect" if i == 0 else "circle") for i in range(n)]
    rects = [(-n * pitch / 2, -depth / 2, n * pitch / 2, depth / 2)]
    pads, rects = _rot(pads, rects, v)
    return FP(name + ("_V" if v else ""), pads, rects, note="Zlacze srubowe; wejscia przewodow w strone krawedzi plytki")

def _smd(num, x, y, w, h):
    return dict(num=str(num), x=round(x, 4), y=round(y, 4), shape="rect", w=w, h=h, drill=0, dw=None)

def soic(name, n, pitch, row, pw, ph, crt, note=""):
    """Dual-row SMD package (SOIC/MSOP), pin 1 top-left, counter-clockwise (KiCad library geometry)."""
    half = n // 2
    pads = [_smd(i + 1, -row, (i - (half - 1) / 2) * pitch, pw, ph) for i in range(half)]
    pads += [_smd(half + i + 1, row, ((half - 1) / 2 - i) * pitch, pw, ph) for i in range(half)]
    return FP(name, pads, [crt], note=note)

def smd2(name, dx, pw, ph, crt, v=False):
    pads = [_smd(1, -dx, 0, pw, ph), _smd(2, dx, 0, pw, ph)]
    rects = [crt]
    pads, rects = _rot(pads, rects, v)
    return FP(name + ("_V" if v else ""), pads, rects)

def g2rl2(name="Relay_DPDT_Omron_G2RL"):
    """Omron G2RL-2 (KiCad Relay_THT:Relay_DPDT_Omron_G2RL, centred). 1/8 coil; 3 COM1, 2 NC1, 4 NO1; 6 COM2, 7 NC2, 5 NO2."""
    ox, oy = 12.1, -3.75
    pos = {"1": (0, 0), "2": (15, 0), "3": (20, 0), "4": (25, 0), "5": (25, -7.5), "6": (20, -7.5), "7": (15, -7.5), "8": (0, -7.5)}
    pads = [_pad(n, x - ox, y - oy, 2.5, 1.5, "rect" if n == "1" else "circle") for n, (x, y) in sorted(pos.items())]
    return FP(name, pads, [(-14.4, -6.25, 14.4, 6.25)],
              note="Omron G2RL-2 (29 x 12,7 mm), uklad otworow wg biblioteki KiCad Relay_DPDT_Omron_G2RL")

def uid(ref):
    """Stable ID shared by schematic symbol and PCB footprint (KiCad tstamp/path)."""
    import zlib
    return "%08X" % (0x50000000 | (zlib.crc32(ref.encode()) & 0x0FFFFFFF))

FOOT = {}
def reg(fp):
    FOOT[fp.name] = fp
    return fp.name

F = dict(
    R05=reg(axial("R_Axial_0.5W_P12.7", 12.7, 9.0, 3.2, 0.9, 1.8)),
    R05V=reg(axial("R_Axial_0.5W_P12.7", 12.7, 9.0, 3.2, 0.9, 1.8, v=True)),
    R1=reg(axial("R_Axial_1W_P15.24", 15.24, 11.5, 4.5, 1.0, 2.0)),
    R1V=reg(axial("R_Axial_1W_P15.24", 15.24, 11.5, 4.5, 1.0, 2.0, v=True)),
    R2=reg(axial("R_Axial_2W_P20.32", 20.32, 16.0, 5.5, 1.1, 2.2)),
    R7=reg(axial("R_Axial_5-7W_P35.56", 35.56, 30.0, 9.0, 1.3, 2.6)),
    R10=reg(axial("R_Cement_10W_P55.88", 55.88, 48.0, 10.0, 1.4, 2.8)),
    DO41=reg(axial("D_DO-41_P10.16", 10.16, 5.2, 2.7, 1.0, 2.0, square1=True)),
    DO41V=reg(axial("D_DO-41_P10.16", 10.16, 5.2, 2.7, 1.0, 2.0, v=True, square1=True)),
    DO201=reg(axial("D_DO-201_P15.24", 15.24, 9.5, 5.3, 1.5, 2.8, square1=True)),
    DO201V=reg(axial("D_DO-201_P15.24", 15.24, 9.5, 5.3, 1.5, 2.8, v=True, square1=True)),
    DO35=reg(axial("D_DO-35_P7.62", 7.62, 4.0, 1.9, 0.8, 1.6, square1=True)),
    DO35V=reg(axial("D_DO-35_P7.62", 7.62, 4.0, 1.9, 0.8, 1.6, v=True, square1=True)),
    C5=reg(box_cap("C_Box_P5_7x4", 5.0, 7.2, 4.5, 0.8, 1.6)),
    C10=reg(box_cap("C_Box_P10_13x5", 10.0, 13.0, 5.0)),
    C15=reg(box_cap("C_Box_P15_18x6", 15.0, 18.0, 6.0)),
    C15V=reg(box_cap("C_Box_P15_18x6", 15.0, 18.0, 6.0, v=True)),
    C22=reg(box_cap("C_Box_P22.5_26.5x8.5", 22.5, 26.5, 8.5)),
    C27=reg(box_cap("C_Box_P27.5_31.5x11", 27.5, 31.5, 11.0, 1.2, 2.4)),
    C27V=reg(box_cap("C_Box_P27.5_31.5x11", 27.5, 31.5, 11.0, 1.2, 2.4, v=True)),
    CBA=reg(cap_box_axial("C_Box27.5_or_Axial52_V")),
    CBAH=reg(FP("C_Box27.5_or_Axial52_H", [dict(p, x=p["y"], y=p["x"]) for p in cap_box_axial("x").pads],
                [(y1, x1, y2, x2) for (x1, y1, x2, y2) in cap_box_axial("x").rects])),
    SNAP30=reg(snapin("CP_SnapIn_D30_P10", 30)),
    R2V=reg(axial("R_Axial_2W_P20.32", 20.32, 16.0, 5.5, 1.1, 2.2, v=True)),
    R7V=reg(axial("R_Axial_5-7W_P35.56", 35.56, 30.0, 9.0, 1.3, 2.6, v=True)),
    R10V=reg(axial("R_Cement_10W_P55.88", 55.88, 48.0, 10.0, 1.4, 2.8, v=True)),
    TO220S=reg(to220v("TO-220_Vertical_SmallHeatsink", hs=(13, 12))),
    TO220=reg(to220v("TO-220_Vertical", hs=None)),
    C22V=reg(box_cap("C_Box_P22.5_26.5x8.5", 22.5, 26.5, 8.5, v=True)),
    CS10=reg(box_cap("C_Disc_1kV_P10", 10.0, 12.0, 5.0, 0.9, 1.8, v=True)),
    CP10=reg(radial_cp("CP_Radial_D10_P5", 10, 5.0)),
    CP12=reg(radial_cp("CP_Radial_D12.5_P5", 12.5, 5.0)),
    CP18=reg(radial_cp("CP_Radial_D18_P7.5", 18, 7.5, 1.0, 2.2)),
    CP6=reg(radial_cp("CP_Radial_D6.3_P2.5", 6.3, 2.5, 0.8, 1.6)),
    SNAP35=reg(snapin("CP_SnapIn_D35_P10", 35)),
    NOVAL=reg(noval()),
    TO220HS=reg(to220v("TO-220_Vertical_Heatsink")),
    TRIM=reg(trimmer3296()),
    PAD=reg(wirepad()),
    PADL=reg(wirepad("WirePad_4.5", 4.5, 2.0)),
    TP=reg(testpoint()),
    RLY1=reg(relay("Relay_SPDT_Finder40.31", 1)),
    RLY2=reg(relay("Relay_DPDT_Finder40.52", 2)),
    ESP=reg(esp32_devkit()),
    ADS=reg(ads1115_mod()),
    DIP18=reg(dip("DIP-18_W7.62", 18)),
    DIP4=reg(dip("DIP-4_W7.62", 4)),
    MH=reg(mounting_hole()),
    FUSE=reg(box_cap("Fuseholder_5x20_Closed_P22.5", 22.5, 28.0, 10.0, 1.5, 3.0)),
    FUSE2=reg(fuse_dual()),
    TB2=reg(terminal("TerminalBlock_1x02_P5.08", 2, 5.08, 1.3, 2.4, 8.5)),
    TB2V=reg(terminal("TerminalBlock_1x02_P5.08", 2, 5.08, 1.3, 2.4, 8.5, v=True)),
    TB3V=reg(terminal("TerminalBlock_1x03_P5.08", 3, 5.08, 1.3, 2.4, 8.5, v=True)),
    TB762_2V=reg(terminal("TerminalBlock_1x02_P7.62", 2, 7.62, 1.5, 3.0, 10.0, v=True)),
    SIP3=reg(FP("SIP-3_P2.54_DCDC", [_pad(1, -2.54, 0, 1.8, 1.0, "rect"), _pad(2, 0, 0, 1.8, 1.0), _pad(3, 2.54, 0, 1.8, 1.0)], [(-5.8, -2.0, 5.8, 6.5)], note="R-78E5.0-1.0 / zamiennik 7805: 1 Vin, 2 GND, 3 Vout")),
    IRM=reg(FP("MeanWell_IRM-15_approx", [_pad(1, 20.3, -5.08, 2.6, 1.3, "rect"), _pad(2, 20.3, 5.08, 2.6, 1.3),
                                           _pad(3, -20.3, 5.08, 2.6, 1.3), _pad(4, -20.3, -5.08, 2.6, 1.3)],
               [(-26.2, -13.6, 26.2, 13.6)], note="Mean Well IRM-15-12, 52,4 x 27,2 x 24 mm; RASTER PRZYBLIZONY - podmien na footprint LCSC C6394169")),
    DCDC4=reg(FP("DCDC_5V_mini_14.17x8.24", [_pad(1, -7.085, -4.120, 2.0, 1.0, "rect"), _pad(2, -7.085, 4.120, 2.0, 1.0),
                                              _pad(3, 7.085, 4.120, 2.0, 1.0), _pad(4, 7.085, -4.120, 2.0, 1.0)],
                 [(-8.8, -6.1, 8.8, 6.1)], note="mini przetwornica 5 V: 1 -IN, 2 +IN, 3 OUT+, 4 OUT-; raster 557,9 x 324,4 mil (14,17 x 8,24 mm)")),
    LED3=reg(radial_cp("LED_D3.0_P2.54", 3.2, 2.54, 0.8, 1.6)),
    G2RL=reg(g2rl2()),
    TB762_3V=reg(terminal("TerminalBlock_1x03_P7.62", 3, 7.62, 1.5, 3.0, 10.0, v=True)),
    # --- SMD (geometria z bibliotek KiCad) ---
    MSOP10=reg(soic("MSOP-10_3x3mm_P0.5mm", 10, 0.5, 2.2, 1.4, 0.3, (-3.15, -1.85, 3.15, 1.85))),
    SOIC14=reg(soic("SOIC-14_3.9x8.7mm_P1.27mm", 14, 1.27, 2.475, 1.95, 0.6, (-3.7, -4.58, 3.7, 4.58))),
    SOIC18W=reg(soic("SOIC-18W_7.5x11.6mm_P1.27mm", 18, 1.27, 4.65, 2.05, 0.6, (-5.93, -6.02, 5.93, 6.02))),
    R0805=reg(smd2("R_0805_2012Metric", 0.9125, 1.025, 1.4, (-1.68, -0.95, 1.68, 0.95))),
    R0805V=reg(smd2("R_0805_2012Metric", 0.9125, 1.025, 1.4, (-1.68, -0.95, 1.68, 0.95), v=True)),
    C0805=reg(smd2("C_0805_2012Metric", 0.95, 1.0, 1.45, (-1.7, -0.98, 1.7, 0.98))),
    C0805V=reg(smd2("C_0805_2012Metric", 0.95, 1.0, 1.45, (-1.7, -0.98, 1.7, 0.98), v=True)),
    R1206=reg(smd2("R_1206_3216Metric", 1.4625, 1.125, 1.75, (-2.28, -1.12, 2.28, 1.12))),
    R1206V=reg(smd2("R_1206_3216Metric", 1.4625, 1.125, 1.75, (-2.28, -1.12, 2.28, 1.12), v=True)),
    SOD123=reg(smd2("D_SOD-123", 1.65, 0.9, 1.2, (-2.35, -1.15, 2.35, 1.15))),
    SOD123V=reg(smd2("D_SOD-123", 1.65, 0.9, 1.2, (-2.35, -1.15, 2.35, 1.15), v=True)),
)
for n in (2, 3, 4, 5, 6):
    F["H%d" % n] = reg(header("PinHeader_1x%02d_P2.54" % n, n))
    F["H%dH" % n] = reg(header("PinHeader_1x%02d_P2.54_H" % n, n, v=False))

# =====================================================================================
# Symbols (legacy .lib, mils, y up). Each symbol: list of pins (name, num, x, y, len, orient, type)
# =====================================================================================
class Sym:
    def __init__(self, name, ref, pins, draw, show_names=False, show_nums=True, value_pos=(0, 0), ref_pos=(0, 0)):
        self.name, self.ref, self.pins, self.draw = name, ref, pins, draw
        self.show_names, self.show_nums = show_names, show_nums
        self.value_pos, self.ref_pos = value_pos, ref_pos

    def lib_text(self):
        o = ["#", "# " + self.name, "#",
             "DEF %s %s 0 30 %s %s 1 F N" % (self.name, self.ref, "Y" if self.show_nums else "N", "Y" if self.show_names else "N"),
             'F0 "%s" %d %d 50 H V L CNN' % (self.ref, self.ref_pos[0], self.ref_pos[1]),
             'F1 "%s" %d %d 50 H V L CNN' % (self.name, self.value_pos[0], self.value_pos[1]),
             'F2 "" 0 0 50 H I C CNN', 'F3 "" 0 0 50 H I C CNN', "DRAW"]
        o += self.draw
        for (nm, num, x, y, ln, ori, et) in self.pins:
            o.append("X %s %s %d %d %d %s 50 50 1 1 %s" % (nm, num, x, y, ln, ori, et))
        o += ["ENDDRAW", "ENDDEF"]
        return "\n".join(o)

SYM = {}
def sym(s):
    SYM[s.name] = s

sym(Sym("R", "R", [("~", "1", 0, 150, 50, "D", "P"), ("~", "2", 0, -150, 50, "U", "P")],
        ["S -40 -100 40 100 0 1 10 N"], value_pos=(60, -60), ref_pos=(60, 20)))
sym(Sym("C", "C", [("~", "1", 0, 150, 120, "D", "P"), ("~", "2", 0, -150, 120, "U", "P")],
        ["P 2 0 1 20 -80 30 80 30 N", "P 2 0 1 20 -80 -30 80 -30 N"], value_pos=(100, -60), ref_pos=(100, 20)))
sym(Sym("CP", "C", [("~", "1", 0, 150, 120, "D", "P"), ("~", "2", 0, -150, 120, "U", "P")],
        ["P 2 0 1 20 -80 30 80 30 N", "P 3 0 1 20 -80 -50 0 -30 80 -50 N", "P 2 0 1 0 -70 90 -30 90 N", "P 2 0 1 0 -50 110 -50 70 N"],
        value_pos=(100, -60), ref_pos=(100, 20)))
sym(Sym("D", "D", [("K", "1", 0, -150, 100, "U", "P"), ("A", "2", 0, 150, 100, "D", "P")],
        ["P 4 0 1 10 -50 50 50 50 0 -50 -50 50 F", "P 2 0 1 10 -50 -50 50 -50 N"], value_pos=(80, -60), ref_pos=(80, 20)))
sym(Sym("ZENER", "D", [("K", "1", 0, -150, 100, "U", "P"), ("A", "2", 0, 150, 100, "D", "P")],
        ["P 4 0 1 10 -50 50 50 50 0 -50 -50 50 F", "P 4 0 1 10 -70 -30 -50 -50 50 -50 70 -70 N"], value_pos=(80, -60), ref_pos=(80, 20)))
sym(Sym("POT", "P", [("~", "1", 0, 150, 50, "D", "P"), ("W", "2", 150, 0, 70, "L", "P"), ("~", "3", 0, -150, 50, "U", "P")],
        ["S -40 -100 40 100 0 1 10 N", "P 3 0 1 10 80 0 45 0 60 15 N"], value_pos=(-300, -60), ref_pos=(-300, 20)))
sym(Sym("EF86", "V",
        [("G1", "9", -400, 100, 150, "R", "I"), ("G3", "8", -400, 0, 150, "R", "P"), ("K", "3", -400, -100, 150, "R", "P"),
         ("IS", "2", -400, -200, 150, "R", "P"), ("IS", "7", -400, -300, 150, "R", "P"),
         ("A", "6", 400, 100, 150, "L", "P"), ("G2", "1", 400, 0, 150, "L", "P"),
         ("H", "4", 400, -200, 150, "L", "W"), ("H", "5", 400, -300, 150, "L", "W")],
        ["S -250 -400 250 250 0 1 10 f"], show_names=True, value_pos=(-250, 280), ref_pos=(-250, 360)))
sym(Sym("E88CC", "V",
        [("G1", "2", -400, 100, 150, "R", "I"), ("A1", "1", -400, 0, 150, "R", "P"), ("K1", "3", -400, -100, 150, "R", "P"),
         ("S", "9", -400, -300, 150, "R", "P"),
         ("G2", "7", 400, 100, 150, "L", "I"), ("A2", "6", 400, 0, 150, "L", "P"), ("K2", "8", 400, -100, 150, "L", "P"),
         ("H", "4", 400, -200, 150, "L", "W"), ("H", "5", 400, -300, 150, "L", "W")],
        ["S -250 -400 250 250 0 1 10 f"], show_names=True, value_pos=(-250, 280), ref_pos=(-250, 360)))
sym(Sym("DN2540", "Q", [("G", "1", -300, 0, 150, "R", "I"), ("D", "2", 0, 300, 150, "D", "P"), ("S", "3", 0, -300, 150, "U", "P")],
        ["S -150 -150 150 150 0 1 10 f"], show_names=True, value_pos=(180, -60), ref_pos=(180, 20)))
sym(Sym("LM7805", "U", [("IN", "1", -350, 0, 150, "R", "W"), ("GND", "2", 0, -250, 100, "U", "W"), ("OUT", "3", 350, 0, 150, "L", "w")],
        ["S -200 -150 200 150 0 1 10 f"], show_names=True, value_pos=(-200, 180), ref_pos=(-200, 260)))
sym(Sym("PAD", "J", [("~", "1", -150, 0, 100, "R", "P")], ["C 0 0 50 0 1 10 N"], value_pos=(80, -60), ref_pos=(80, 20)))
sym(Sym("DCDC4", "U", [("+IN", "2", -400, 0, 150, "R", "W"), ("-IN", "1", -50, -350, 150, "U", "W"), ("OUT-", "4", 50, -350, 150, "U", "W"), ("OUT+", "3", 400, 0, 150, "L", "w")],
        ["S -250 -200 250 200 0 1 10 f"], show_names=True, value_pos=(-250, 230), ref_pos=(-250, 310)))
sym(Sym("IRM", "PS", [("AC/L", "1", -450, 100, 150, "R", "W"), ("AC/N", "2", -450, -100, 150, "R", "W"), ("-V", "3", 450, -100, 150, "L", "w"), ("+V", "4", 450, 100, 150, "L", "w")],
        ["S -300 -200 300 200 0 1 10 f"], show_names=True, value_pos=(-300, 230), ref_pos=(-300, 310)))
sym(Sym("FUSE", "F", [("~", "1", -150, 0, 50, "R", "P"), ("~", "2", 150, 0, 50, "L", "P")],
        ["S -100 -35 100 35 0 1 10 N", "P 2 0 1 10 -100 0 100 0 N"], value_pos=(-80, -90), ref_pos=(-80, 60)))
sym(Sym("TP", "TP", [("~", "1", 0, -150, 100, "U", "P")], ["C 0 0 50 0 1 10 N"], value_pos=(80, -60), ref_pos=(80, 20)))
sym(Sym("RELAY_1P", "K",
        [("A1", "A1", -400, 100, 150, "R", "P"), ("A2", "A2", -400, -100, 150, "R", "P"),
         ("COM", "11", 400, 100, 150, "L", "P"), ("NC", "12", 400, 0, 150, "L", "P"), ("NO", "14", 400, -100, 150, "L", "P")],
        ["S -250 -200 250 200 0 1 10 f"], show_names=True, value_pos=(-250, 230), ref_pos=(-250, 310)))
sym(Sym("RELAY_2P", "K",
        [("A1", "A1", -400, 200, 150, "R", "P"), ("A2", "A2", -400, 100, 150, "R", "P"),
         ("COM1", "11", 400, 300, 150, "L", "P"), ("NC1", "12", 400, 200, 150, "L", "P"), ("NO1", "14", 400, 100, 150, "L", "P"),
         ("COM2", "21", 400, -100, 150, "L", "P"), ("NC2", "22", 400, -200, 150, "L", "P"), ("NO2", "24", 400, -300, 150, "L", "P")],
        ["S -250 -400 250 400 0 1 10 f"], show_names=True, value_pos=(-250, 430), ref_pos=(-250, 510)))
sym(Sym("RELAY_G2RL", "K",
        [("A1", "1", -400, 200, 150, "R", "P"), ("A2", "8", -400, 100, 150, "R", "P"),
         ("COM1", "3", 400, 300, 150, "L", "P"), ("NC1", "2", 400, 200, 150, "L", "P"), ("NO1", "4", 400, 100, 150, "L", "P"),
         ("COM2", "6", 400, -100, 150, "L", "P"), ("NC2", "7", 400, -200, 150, "L", "P"), ("NO2", "5", 400, -300, 150, "L", "P")],
        ["S -250 -400 250 400 0 1 10 f"], show_names=True, value_pos=(-250, 430), ref_pos=(-250, 510)))
_ic = lambda left, right, h: ([(n, num, -450, h - 100 * i, 150, "R", "P") for i, (n, num) in enumerate(left)] +
                              [(n, num, 450, h - 100 * i, 150, "L", "P") for i, (n, num) in enumerate(right)])
sym(Sym("ADS1115", "U", _ic([("VDD", "8"), ("GND", "3"), ("ADDR", "1"), ("ALRT", "2"), ("SCL", "10"), ("SDA", "9")],
                            [("AIN0", "4"), ("AIN1", "5"), ("AIN2", "6"), ("AIN3", "7")], 250),
        ["S -300 -350 300 350 0 1 10 f"], show_names=True, value_pos=(-300, 380), ref_pos=(-300, 460)))
sym(Sym("MCP4728", "U", _ic([("VDD", "1"), ("VSS", "10"), ("SCL", "2"), ("SDA", "3"), ("~LDAC", "4"), ("RDY", "5")],
                            [("VOUTA", "6"), ("VOUTB", "7"), ("VOUTC", "8"), ("VOUTD", "9")], 250),
        ["S -300 -350 300 350 0 1 10 f"], show_names=True, value_pos=(-300, 380), ref_pos=(-300, 460)))
sym(Sym("LM324", "U",
        [(n, num, -450, 450 - 100 * i, 150, "R", "P") for i, (n, num) in enumerate(
            [("+1", "3"), ("-1", "2"), ("+2", "5"), ("-2", "6"), ("+3", "10"), ("-3", "9"), ("+4", "12"), ("-4", "13"), ("V+", "4"), ("GND", "11")])] +
        [(n, num, 450, y, 150, "L", "P") for (n, num, y) in (("OUT1", "1", 400), ("OUT2", "7", 200), ("OUT3", "8", 0), ("OUT4", "14", -200))],
        ["S -300 -550 300 550 0 1 10 f"], show_names=True, value_pos=(-300, 580), ref_pos=(-300, 660)))
sym(Sym("PC817", "U", [("A", "1", -350, 50, 150, "R", "P"), ("K", "2", -350, -50, 150, "R", "P"),
                       ("C", "4", 350, 50, 150, "L", "P"), ("E", "3", 350, -50, 150, "L", "P")],
        ["S -200 -150 200 150 0 1 10 f"], show_names=True, value_pos=(-200, 180), ref_pos=(-200, 260)))
_uln = []
for i in range(8):
    _uln.append(("IN%d" % (i + 1), str(i + 1), -450, 400 - i * 100, 150, "R", "I"))
    _uln.append(("OUT%d" % (i + 1), str(18 - i), 450, 400 - i * 100, 150, "L", "O"))
_uln += [("GND", "9", -450, -450, 150, "R", "W"), ("COM", "10", 450, -450, 150, "L", "P")]
sym(Sym("ULN2803", "U", _uln, ["S -300 -550 300 500 0 1 10 f"], show_names=True, value_pos=(-300, 530), ref_pos=(-300, 610)))
_ads = [("VDD", "1"), ("GND", "2"), ("SCL", "3"), ("SDA", "4"), ("ADDR", "5"), ("ALRT", "6"), ("A0", "7"), ("A1", "8"), ("A2", "9"), ("A3", "10")]
sym(Sym("ADS1115_MOD", "U", [(n, num, -450, 450 - i * 100, 150, "R", "P") for i, (n, num) in enumerate(_ads)],
        ["S -300 -550 300 550 0 1 10 f"], show_names=True, value_pos=(-300, 580), ref_pos=(-300, 660)))
ESP_L = ["3V3", "3V3", "RST", "IO4", "IO5", "IO6", "IO7", "IO15", "IO16", "IO17", "IO18", "IO8", "IO3", "IO46", "IO9", "IO10", "IO11", "IO12", "IO13", "IO14", "5V", "GND"]
ESP_R = ["GND", "TX", "RX", "IO1", "IO2", "IO42", "IO41", "IO40", "IO39", "IO38", "IO37", "IO36", "IO35", "IO0", "IO45", "IO48", "IO47", "IO21", "IO20", "IO19", "GND", "GND"]
sym(Sym("ESP32S3_DEVKITC", "U",
        [(n, "L%d" % (i + 1), -600, 1050 - i * 100, 150, "R", "P") for i, n in enumerate(ESP_L)] +
        [(n, "R%d" % (i + 1), 600, 1050 - i * 100, 150, "L", "P") for i, n in enumerate(ESP_R)],
        ["S -450 -1150 450 1150 0 1 10 f"], show_names=True, value_pos=(-450, 1180), ref_pos=(-450, 1260)))
for n in (2, 3):
    sym(Sym("CONNR_%d" % n, "J", [("P%d" % (i + 1), str(i + 1), 300, (n - 1) * 50 - i * 100, 150, "L", "P") for i in range(n)],
            ["S -100 %d 150 %d 0 1 10 f" % (-(n - 1) * 50 - 80, (n - 1) * 50 + 80)], show_names=False,
            value_pos=(-100, (n - 1) * 50 + 110), ref_pos=(-100, (n - 1) * 50 + 190)))
for n in (2, 3, 4, 5, 6):
    sym(Sym("CONN_%d" % n, "J", [("P%d" % (i + 1), str(i + 1), -300, (n - 1) * 50 - i * 100, 150, "R", "P") for i in range(n)],
            ["S -150 %d 100 %d 0 1 10 f" % (-(n - 1) * 50 - 80, (n - 1) * 50 + 80)], show_names=False,
            value_pos=(-150, (n - 1) * 50 + 110), ref_pos=(-150, (n - 1) * 50 + 190)))

# =====================================================================================
# Board model
# =====================================================================================
class Comp:
    def __init__(self, ref, value, symbol, fp, x, y, nets, group, note="", side="T"):
        self.ref, self.value, self.symbol, self.fp = ref, value, symbol, fp
        self.x, self.y, self.nets, self.group, self.note, self.side = x, y, nets, group, note, side

    def geom(self):
        """absolute pads [(num,x,y,w,h,shape,drill)], rects, circles as seen from TOP (bottom parts mirrored in x)"""
        f = FOOT[self.fp]
        m = -1 if self.side == "B" else 1
        pads = [(p["num"], self.x + m * p["x"], self.y + p["y"], p["w"], p["h"], p["shape"], p["drill"]) for p in f.pads]
        rects = [(self.x + min(m * x1, m * x2), self.y + y1, self.x + max(m * x1, m * x2), self.y + y2) for (x1, y1, x2, y2) in f.rects]
        circ = [(self.x + m * cx, self.y + cy, r) for (cx, cy, r) in f.circles]
        return pads, rects, circ

class Board:
    def __init__(self, name, title, w, h):
        self.name, self.title, self.w, self.h = name, title, w, h
        self.comps = []
        self.texts = []      # (x, y, text, size)
        self.zones = []      # (x1, y1, x2, y2, label)

    def add(self, ref, value, symbol, fp, x, y, nets, group, note="", side="T"):
        pins = [p[1] for p in SYM[symbol].pins] if symbol else []
        if isinstance(nets, (list, tuple)):
            assert len(nets) == len(pins), (ref, pins, nets)
            nets = dict(zip(pins, nets))
        f = FOOT[fp]
        if symbol and f.pads and f.pads[0]["num"]:
            fpn = sorted({p["num"] for p in f.pads})
            assert sorted(pins) == fpn, (ref, sorted(pins), fpn)
        self.comps.append(Comp(ref, value, symbol, fp, x, y, nets, group, note, side))

    def nets(self):
        d = {}
        for c in self.comps:
            for pin, n in c.nets.items():
                if n is None:
                    continue
                d.setdefault(n, []).append((c.ref, pin))
        return d

    # ---------- checks ----------
    @staticmethod
    def cinfo(c):
        pads, rects, circ = c.geom()
        bodies = [("r",) + r for r in rects] + [("c", cx, cy, r) for (cx, cy, r) in circ]
        if c.fp == F["MH"]:
            side = "TB"; bodies = [("c", c.x, c.y, 3.6)]
        elif c.fp in (F["PAD"], F["PADL"], F["TP"]):
            side = ""; bodies = []
        else:
            side = c.side
        pb = [("r", x - w / 2, y - h / 2, x + w / 2, y + h / 2, c.nets.get(n)) for (n, x, y, w, h, sh, d) in pads]
        return side, bodies, pb

    @staticmethod
    def _ov(a, b, g):
        if a[0] == "c" and b[0] == "c":
            return ((a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5 < a[3] + b[3] + g
        if a[0] == "c":
            a, b = b, a
        if b[0] == "c":
            cx, cy, r = b[1:]
            nx = min(max(cx, a[1]), a[3]); ny = min(max(cy, a[2]), a[4])
            return ((nx - cx) ** 2 + (ny - cy) ** 2) ** 0.5 < r + g
        return a[1] < b[3] + g and b[1] < a[3] + g and a[2] < b[4] + g and b[2] < a[4] + g

    HVSET = set()
    VOLT = {}

    @classmethod
    def pair_conflict(cls, i1, i2):
        s1, B1, P1 = i1; s2, B2, P2 = i2
        if set(s1) & set(s2) and any(cls._ov(a, b, -0.3) for a in B1 for b in B2):
            return "bodies"
        for a in P1:
            for b in P2:
                g = 0.5
                if a[5] != b[5] and a[5] is not None and b[5] is not None:
                    va, vb = cls.VOLT.get(a[5], 0), cls.VOLT.get(b[5], 0)
                    if va == "AC" or vb == "AC":
                        g = 2.5
                    else:
                        dv = abs(va - vb)
                        g = 2.5 if dv >= 200 else (1.0 if dv >= 50 else 0.5)
                if cls._ov(a, b, g):
                    return "pads-HV" if g > 0.5 else "pads"
        if any(cls._ov(a, b, 0.2) for a in B1 for b in P2) or any(cls._ov(a, b, 0.2) for a in B2 for b in P1):
            return "body/pad"
        return None

    def inside(self, inf, m=0.5):
        s, B, P = inf
        for e in B + P:
            if e[0] == "c":
                x1, y1, x2, y2 = e[1] - e[3], e[2] - e[3], e[1] + e[3], e[2] + e[3]
            else:
                x1, y1, x2, y2 = e[1:5]
            if x1 < m or y1 < m or x2 > self.w - m or y2 > self.h - m:
                return False
        return True

    def check(self):
        msgs = []
        refs = [c.ref for c in self.comps]
        dup = {r for r in refs if refs.count(r) > 1}
        if dup:
            msgs.append("DUPLICATE refs: %s" % dup)
        for n, lst in self.nets().items():
            if len(lst) < 2:
                msgs.append("single-pin net %s: %s" % (n, lst))
        info = [(c.ref, self.cinfo(c)) for c in self.comps]
        for (r1, i1), (r2, i2) in itertools.combinations(info, 2):
            h = self.pair_conflict(i1, i2)
            if h:
                msgs.append("overlap(%s) %s / %s" % (h, r1, r2))
        for r, inf in info:
            if not self.inside(inf):
                msgs.append("outside board %s" % r)
        return msgs

    def autoplace(self, order, prefs, fixed_refs, maxr=60, step=1.0):
        """order: refs to place; prefs: ref -> (x, y, side, [fp keys]); others stay fixed."""
        byref = {c.ref: c for c in self.comps}
        placed = [self.cinfo(byref[r]) for r in fixed_refs]
        failed = []
        for ref in order:
            c = byref[ref]
            px, py, side, fps = prefs[ref]
            c.side = side or "T"
            ok = False
            for rad in [0] + [k * step for k in range(1, int(maxr / step))]:
                n = max(1, int(2 * 3.14159 * rad / step))
                cands = [(px, py)] if rad == 0 else []
                if rad:
                    import math
                    pts = set()
                    for k in range(n):
                        a = 2 * math.pi * k / n
                        pts.add((round((px + rad * math.cos(a)) * 2) / 2, round((py + rad * math.sin(a)) * 2) / 2))
                    cands = sorted(pts, key=lambda q: (abs(q[1] - py), abs(q[0] - px)))
                for (x, y) in cands:
                    for fk in fps:
                        c.x, c.y, c.fp = x, y, F[fk]
                        inf = self.cinfo(c)
                        if not self.inside(inf):
                            continue
                        if any(self.pair_conflict(inf, o) for o in placed):
                            continue
                        ok = True; break
                    if ok: break
                if ok: break
            if ok:
                placed.append(self.cinfo(c))
            else:
                failed.append(ref)
        return failed

    # ---------- writers ----------
    def write_lib(self, path, prefix=""):
        used = sorted({c.symbol for c in self.comps if c.symbol})
        o = ["EESchema-LIBRARY Version 2.4" if prefix else "EESchema-LIBRARY Version 2.3", "#encoding utf-8"]
        for u in used:
            t = SYM[u].lib_text()
            if prefix:
                t = t.replace("# %s\n" % u, "# %s%s\n" % (prefix, u), 1).replace("DEF %s " % u, "DEF %s%s " % (prefix, u), 1)
                t = t.replace('F1 "%s"' % u, 'F1 "%s%s"' % (prefix, u), 1)
            o.append(t)
        o += ["#", "#End Library", ""]
        open(path, "w").write("\n".join(o))

    def write_sch(self, path, libname, v5=False):
        comps = [c for c in self.comps if c.symbol and c.symbol in SYM and FOOT[c.fp].pads[0]["num"] != ""]
        groups = []
        for c in comps:
            if c.group not in groups:
                groups.append(c.group)
        # layout in columns per group
        X0, Y0 = 600, 900
        colw = {"EF86": 2600, "E88CC": 2600, "ESP32S3_DEVKITC": 3400, "ULN2803": 2600, "ADS1115_MOD": 2400,
                "RELAY_1P": 2400, "RELAY_2P": 2400, "DN2540": 1800, "LM7805": 2000}
        rowh = {"EF86": 1400, "E88CC": 1400, "ESP32S3_DEVKITC": 2900, "ULN2803": 1600, "ADS1115_MOD": 1600,
                "RELAY_1P": 1000, "RELAY_2P": 1400, "CONN_5": 1000, "CONN_6": 1100}
        maxw = 22000
        out = []
        ts = itertools.count(0x5A000001)
        x, y = X0, Y0
        rowmax = 0
        notes = []
        for g in groups:
            gc = [c for c in comps if c.group == g]
            if x != X0:
                x = X0; y += rowmax + 500; rowmax = 0
            notes.append((x, y - 250, g))
            for c in gc:
                w = colw.get(c.symbol, 1500)
                h = rowh.get(c.symbol, 900)
                if x + w > maxw:
                    x = X0; y += rowmax + 250; rowmax = 0
                cx, cy = x + w // 2, y + h // 2
                out.append((c, cx, cy))
                x += w
                rowmax = max(rowmax, h)
        H = y + rowmax + 600
        W = maxw + 600
        sheet = ("A2", 23386, 16535) if H <= 16535 else ("A1", 33110, 23386)
        hdr = ["EESchema Schematic File Version 4", "EELAYER 30 0", "EELAYER END"] if v5 else \
              ["EESchema Schematic File Version 2", "LIBS:%s" % libname, "EELAYER 25 0", "EELAYER END"]
        L = hdr + [
             "$Descr %s %d %d" % sheet, "encoding utf-8", "Sheet 1 1", 'Title "%s"' % self.title, 'Date ""', 'Rev "0.3"',
             'Comp ""', 'Comment1 "Soloist 88 Stereo"', 'Comment2 "Schemat z etykietami sieci"', 'Comment3 ""', 'Comment4 ""', "$EndDescr"]
        for (nx, ny, g) in notes:
            L += ["Text Notes %d %d 0    80   ~ 16" % (nx, ny), g]
        for (c, cx, cy) in out:
            s = SYM[c.symbol]
            L += ["$Comp", "L %s%s %s" % ((libname + ":") if v5 else "", c.symbol, c.ref), "U 1 1 %08X" % next(ts), "P %d %d" % (cx, cy),
                  'F 0 "%s" H %d %d 50  0000 L CNN' % (c.ref, cx + s.ref_pos[0], cy - s.ref_pos[1]),
                  'F 1 "%s" H %d %d 50  0000 L CNN' % (c.value, cx + s.value_pos[0], cy - s.value_pos[1]),
                  'F 2 "%s:%s" H %d %d 50  0001 C CNN' % (libname, c.fp, cx, cy),
                  'F 3 "%s" H %d %d 50  0001 C CNN' % ("~" if v5 else "", cx, cy),
                  "\t1    %d %d" % (cx, cy), "\t1    0    0    -1  ", "$EndComp"]
            for (nm, num, px, py, ln, ori, et) in s.pins:
                ex, ey = cx + px, cy - py
                net = c.nets.get(num)
                stub = 100
                dx, dy, lo = {"D": (0, -stub, 0), "U": (0, stub, 0), "R": (-stub, 0, 2), "L": (stub, 0, 0)}[ori]
                if net is None:
                    L += ["NoConn ~ %d %d" % (ex, ey)]
                    continue
                L += ["Wire Wire Line", "\t%d %d %d %d" % (ex, ey, ex + dx, ey + dy)]
                L += ["Text Label %d %d %d    50   ~ 0" % (ex + dx, ey + dy, lo), net]
        L += ["$EndSCHEMATC", ""]
        open(path, "w").write("\n".join(L))

    def write_pcb(self, path, libname, ox=40.0, oy=40.0, v5=False):
        nets = sorted(self.nets().keys(), key=lambda n: (n != "GND", n))
        nid = {n: i + 1 for i, n in enumerate(nets)}
        o = [("(kicad_pcb (version 20171130) (host pcbnew 5.1.9-73d0e3b20d~88~ubuntu20.04.1)" if v5 else
              "(kicad_pcb (version 4) (host pcbnew 4.0.7-e2-6376~58~ubuntu16.04.1)"), "",
             "  (general", "    (links 0)", "    (no_connects 0)", "    (area %.1f %.1f %.1f %.1f)" % (ox, oy, ox + self.w, oy + self.h),
             "    (thickness 1.6)", "    (drawings %d)" % (4 + len(self.texts)), "    (tracks 0)", "    (zones 0)",
             "    (modules %d)" % len(self.comps), "    (nets %d)" % (len(nets) + 1), "  )", "", "  (page A3)",
             "  (layers", "    (0 F.Cu signal)", "    (31 B.Cu signal)",
             "    (32 B.Adhes user)", "    (33 F.Adhes user)", "    (34 B.Paste user)", "    (35 F.Paste user)",
             "    (36 B.SilkS user)", "    (37 F.SilkS user)", "    (38 B.Mask user)", "    (39 F.Mask user)",
             "    (40 Dwgs.User user)", "    (41 Cmts.User user)", "    (42 Eco1.User user)", "    (43 Eco2.User user)",
             "    (44 Edge.Cuts user)", "    (45 Margin user)", "    (46 B.CrtYd user)", "    (47 F.CrtYd user)",
             "    (48 B.Fab user)", "    (49 F.Fab user)", "  )", "",
             "  (setup", "    (last_trace_width 0.5)", "    (trace_clearance 0.3)", "    (zone_clearance 0.6)", "    (zone_45_only no)",
             "    (trace_min 0.25)", "    (segment_width 0.2)", "    (edge_width 0.15)", "    (via_size 1.2)", "    (via_drill 0.6)",
             "    (via_min_size 0.6)", "    (via_min_drill 0.3)", "    (uvia_size 0.3)", "    (uvia_drill 0.1)", "    (uvias_allowed no)",
             "    (uvia_min_size 0.2)", "    (uvia_min_drill 0.1)", "    (pcb_text_width 0.3)", "    (pcb_text_size 1.5 1.5)",
             "    (mod_edge_width 0.15)", "    (mod_text_size 1 1)", "    (mod_text_width 0.15)", "    (pad_size 2 2)", "    (pad_drill 1)",
             "    (pad_to_mask_clearance 0.1)", "    (aux_axis_origin 0 0)", "    (visible_elements FFFFFF7F)", "  )", "",
             '  (net 0 "")']
        for n in nets:
            o.append('  (net %d "%s")' % (nid[n], n))
        try:
            from netclasses import CLASSES
            cls = CLASSES.get(self.name, [])
        except ImportError:
            cls = []
        assigned = {n: k for (k, tw, cl, sp, ns, note) in cls for n in ns.split()}
        def _nc(name, desc, cl, tw, members):
            r = ["", '  (net_class %s "%s"' % (name, desc), "    (clearance %s)" % cl, "    (trace_width %s)" % tw,
                 "    (via_dia %s)" % max(1.2, tw + 0.6), "    (via_drill %s)" % max(0.6, round(tw * 0.6, 2)),
                 "    (uvia_dia 0.3)", "    (uvia_drill 0.1)"]
            r += ['    (add_net "%s")' % n for n in members]
            return r + ["  )"]
        o += _nc("Default", "Domyslna", 0.3, 0.4, [n for n in nets if n not in assigned])
        for (k, tw, cl, sp, ns, note) in cls:
            o += _nc(k, (note + ("; " + sp if sp else "")).replace('"', "'"), cl, tw, [n for n in nets if assigned.get(n) == k])
        o += [""]
        ts = itertools.count(0x5B000001)
        for c in self.comps:
            f = FOOT[c.fp]
            X, Y = ox + c.x, oy + c.y
            b = f.bbox
            B = c.side == "B"
            m = -1 if B else 1
            Ls = "B.SilkS" if B else "F.SilkS"; Lf = "B.Fab" if B else "F.Fab"; Lc = "B.CrtYd" if B else "F.CrtYd"
            mir = " (justify mirror)" if B else ""
            o.append("  (module %s:%s (layer %s) (tedit 5B000000) (tstamp %s)" % (libname, f.name, "B.Cu" if B else "F.Cu", uid(c.ref)))
            o.append("    (at %.3f %.3f)" % (X, Y))
            o.append("    (path /%s)" % uid(c.ref))
            if f.pads and all(p["drill"] == 0 for p in f.pads):
                o.append("    (attr smd)")
            o.append('    (fp_text reference %s (at %.2f %.2f) (layer %s)' % (c.ref, m * (b[0] + b[2]) / 2, b[1] - 1.2, Ls))
            o.append("      (effects (font (size 1.2 1.2) (thickness 0.18))%s)\n    )" % mir)
            o.append('    (fp_text value "%s" (at %.2f %.2f) (layer %s)' % (c.value, m * (b[0] + b[2]) / 2, b[3] + 1.2, Lf))
            o.append("      (effects (font (size 1 1) (thickness 0.15))%s)\n    )" % mir)
            for (x1, y1, x2, y2) in f.rects:
                for (a, bb, cc, d) in ((x1, y1, x2, y1), (x2, y1, x2, y2), (x2, y2, x1, y2), (x1, y2, x1, y1)):
                    o.append("    (fp_line (start %.3f %.3f) (end %.3f %.3f) (layer %s) (width 0.15))" % (m * a, bb, m * cc, d, Ls))
            for (cx, cy, r) in f.circles:
                o.append("    (fp_circle (center %.3f %.3f) (end %.3f %.3f) (layer %s) (width 0.15))" % (m * cx, cy, m * cx + r, cy, Ls))
            o.append("    (fp_line (start %.3f %.3f) (end %.3f %.3f) (layer %s) (width 0.05))" % (m * (b[0] - .25), b[1] - .25, m * (b[2] + .25), b[1] - .25, Lc))
            o.append("    (fp_line (start %.3f %.3f) (end %.3f %.3f) (layer %s) (width 0.05))" % (m * (b[2] + .25), b[1] - .25, m * (b[2] + .25), b[3] + .25, Lc))
            o.append("    (fp_line (start %.3f %.3f) (end %.3f %.3f) (layer %s) (width 0.05))" % (m * (b[2] + .25), b[3] + .25, m * (b[0] - .25), b[3] + .25, Lc))
            o.append("    (fp_line (start %.3f %.3f) (end %.3f %.3f) (layer %s) (width 0.05))" % (m * (b[0] - .25), b[3] + .25, m * (b[0] - .25), b[1] - .25, Lc))
            for p in f.pads:
                if p["shape"] == "np":
                    o.append('    (pad "" np_thru_hole circle (at 0 0) (size %.2f %.2f) (drill %.2f) (layers *.Cu *.Mask))' % (p["w"], p["w"], p["drill"]))
                    continue
                shape = {"rect": "rect", "circle": "circle", "oval": "oval"}[p["shape"]]
                if shape == "circle" and abs(p["w"] - p["h"]) > 0.01:
                    shape = "oval"
                net = c.nets.get(p["num"])
                ns = (' (net %d "%s")' % (nid[net], net)) if net else ""
                if not p["drill"]:
                    lay = "B.Cu B.Paste B.Mask" if B else "F.Cu F.Paste F.Mask"
                    o.append("    (pad %s smd rect (at %.3f %.3f) (size %.3f %.3f) (layers %s)%s)" %
                             (p["num"], m * p["x"], p["y"], p["w"], p["h"], lay, ns))
                    continue
                o.append("    (pad %s thru_hole %s (at %.3f %.3f) (size %.2f %.2f) (drill %.2f) (layers *.Cu *.Mask)%s)" %
                         (p["num"], shape, m * p["x"], p["y"], p["w"], p["h"], p["drill"], ns))
            o.append("  )")
        # outline
        pts = [(ox, oy), (ox + self.w, oy), (ox + self.w, oy + self.h), (ox, oy + self.h)]
        for i in range(4):
            a, b2 = pts[i], pts[(i + 1) % 4]
            o.append("  (gr_line (start %.2f %.2f) (end %.2f %.2f) (angle 90) (layer Edge.Cuts) (width 0.15))" % (a[0], a[1], b2[0], b2[1]))
        for (tx, ty, t, sz) in self.texts:
            o.append('  (gr_text "%s" (at %.2f %.2f) (layer F.SilkS)\n    (effects (font (size %.1f %.1f) (thickness 0.2)))\n  )' % (t, ox + tx, oy + ty, sz, sz))
        for (x1, y1, x2, y2, lab) in self.zones:
            for (a, bb, cc, d) in ((x1, y1, x2, y1), (x2, y1, x2, y2), (x2, y2, x1, y2), (x1, y2, x1, y1)):
                o.append("  (gr_line (start %.2f %.2f) (end %.2f %.2f) (angle 90) (layer Cmts.User) (width 0.2))" % (ox + a, oy + bb, ox + cc, oy + d))
            o.append('  (gr_text "%s" (at %.2f %.2f) (layer Cmts.User)\n    (effects (font (size 1.5 1.5) (thickness 0.2)) (justify left))\n  )' % (lab, ox + x1 + 1, oy + y1 + 2))
        o += [")", ""]
        open(path, "w").write("\n".join(o))

    def write_csv(self, dirpath):
        with open(os.path.join(dirpath, self.name + "_BOM.csv"), "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh, delimiter=";")
            import jlc
            w.writerow(["Oznaczenie", "Wartosc", "Footprint", "Strona", "X [mm]", "Y [mm]", "Grupa", "LCSC", "Uwagi"])
            for c in self.comps:
                w.writerow([c.ref, c.value, c.fp, "GORA" if c.side == "T" else "DOL", "%.2f" % c.x, "%.2f" % c.y, c.group,
                            jlc.lookup(c)[1], c.note])
        with open(os.path.join(dirpath, self.name + "_netlista.csv"), "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh, delimiter=";")
            w.writerow(["Siec", "Polaczenia (element-pin)"])
            for n, lst in sorted(self.nets().items(), key=lambda kv: (kv[0] != "GND", kv[0])):
                w.writerow([n, " ".join("%s-%s" % rp for rp in lst)])

    def svg(self, scale=4.0, hv_nets=()):
        """Placement drawing; returns svg string with mm-based viewBox."""
        pad = 6
        W, H = self.w + 2 * pad, self.h + 2 * pad
        o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="%.1f %.1f %.1f %.1f" width="%.1fmm" height="%.1fmm" font-family="IBM Plex Mono, monospace">'
             % (-pad, -pad, W, H, W, H)]
        o.append('<rect x="0" y="0" width="%.2f" height="%.2f" class="board"/>' % (self.w, self.h))
        for (x1, y1, x2, y2, lab) in self.zones:
            o.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" class="zone"/>' % (x1, y1, x2 - x1, y2 - y1))
            o.append('<text x="%.2f" y="%.2f" class="zl">%s</text>' % (x1 + 1, y1 + 3, lab))
        order = sorted(self.comps, key=lambda c: 0 if c.side == "B" else 1)
        for c in order:
            pads, rects, circ = c.geom()
            bc = "body bot" if c.side == "B" else "body"
            for (x1, y1, x2, y2) in rects:
                o.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" class="%s"/>' % (x1, y1, x2 - x1, y2 - y1, bc))
            for (cx, cy, r) in circ:
                o.append('<circle cx="%.2f" cy="%.2f" r="%.2f" class="%s"/>' % (cx, cy, r, bc))
        for c in order:
            pads, rects, circ = c.geom()
            for (num, x, y, w, h, sh, d) in pads:
                net = c.nets.get(num)
                cls = "pad hv" if net in hv_nets else "pad"
                if sh == "np":
                    o.append('<circle cx="%.2f" cy="%.2f" r="%.2f" class="hole"/>' % (x, y, d / 2))
                elif sh == "rect":
                    o.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" class="%s"/>' % (x - w / 2, y - h / 2, w, h, cls))
                else:
                    o.append('<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f" class="%s"/>' % (x, y, w / 2, h / 2, cls))
        for c in order:
            pads, rects, circ = c.geom()
            xs = [r[0] for r in rects] + [r[2] for r in rects] + [cx - r for cx, cy, r in circ] + [cx + r for cx, cy, r in circ] + [p[1] for p in pads]
            ys = [r[1] for r in rects] + [r[3] for r in rects] + [cy - r for cx, cy, r in circ] + [cy + r for cx, cy, r in circ] + [p[2] for p in pads]
            lx, ly = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
            if c.fp in (F["PAD"], F["PADL"], F["TP"]):
                o.append('<text x="%.2f" y="%.2f" class="lab" text-anchor="middle">%s</text>' % (c.x, max(ys) + 2.6, c.value))
            elif c.fp != F["MH"]:
                o.append('<text x="%.2f" y="%.2f" class="%s" text-anchor="middle">%s</text>' % (lx, ly + 0.9, "ref bot" if c.side == "B" else "ref", c.ref))
        for (tx, ty, t, sz) in self.texts:
            o.append('<text x="%.2f" y="%.2f" class="title">%s</text>' % (tx, ty, t))
        o.append("</svg>")
        return "\n".join(o)
