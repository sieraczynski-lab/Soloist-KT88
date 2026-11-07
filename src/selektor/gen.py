#!/usr/bin/env python3
"""Generator projektu KiCad 8: selektor 4 wejść + drabinka przekaźnikowa 63 dB + mute.

Wszystkie pliki (.kicad_pro, .kicad_sch, .kicad_pcb, biblioteka symboli) powstają
z jednej listy elementów, więc schemat i płytka mają identyczną netlistę.
"""
import json, math, os, re, sys, uuid, datetime

SRC_DIR = os.path.dirname(os.path.abspath(__file__))                      # src/selektor
REPO = os.path.dirname(os.path.dirname(SRC_DIR))                           # katalog repozytorium
ROOT = os.path.join(REPO, "hardware", "selektor")                         # wyniki generatora

PROJ = "tube_selector"
OUT = os.path.join(ROOT, "kicad")
FPLIB = os.environ.get("KICAD_FOOTPRINT_DIR", "")  # klon github.com/KiCad/kicad-footprints
NS = uuid.UUID("6f1c2a52-1d0e-4c3b-9a55-0b7e3e7c0a11")


def U(*k):
    return str(uuid.uuid5(NS, "/".join(map(str, k))))


ROOT_UUID = U("root")
DATE = datetime.date(2026, 10, 22).isoformat()
REV = "0.5"
TITLE = "Selektor wejść + drabinka przekaźnikowa"

# ----------------------------------------------------------------------------
# Wartości drabinki (impedancja 10 kΩ, szereg E192, 0,1 %)
# ----------------------------------------------------------------------------
LADDER = [  # (dB, Rs, Rp) — wartości 0,1 % dostępne w magazynie JLCPCB/LCSC (stan 2026-10-22)
    (1, 1100, 80600),
    (2, 2000, 32400),
    (4, 3750, 17400),
    (8, 6200, 6810),
    (16, 9100, 2000),
    (32, 10000, 270),
]
LCSC_01 = {1100: ('C473284', 'ERA6AEB112V'), 80600: ('C728657', 'RT0805BRD0780K6L'), 2000: ('C479096', 'PTFR0805B2K00P9'), 32400: ('C149970', 'TR0805B32K4P0550Z'), 3750: ('C374641', 'AR05BTB3751A010'), 17400: ('C47115938', 'PTFR0805B17K4P9'), 6200: ('C326695', 'RT0805BRD076K2L'), 6810: ('C728655', 'RT0805BRD076K81L'), 9100: ('C21571502', 'TC0525B9101T5G'), 10000: ('C110775', 'RT0805BRD0710KL'), 270: ('C351587', 'PTFR0805B270RN9')}
LCSC_1 = {'1k': ('C17513', '0805W8F1001T5E'), '4.7k': ('C17673', '0805W8F4701T5E'), '10k': ('C17414', '0805W8F1002T5E')}
R_TERM = 10000
R_SHUNT = 1000


def rstr(v):
    if v >= 1000:
        s = f"{v/1000:.3g}"
        if "." not in s and len(s) < 3 and v % 1000:
            s = f"{v/1000:.2f}"
        return s + "k"
    return f"{v:g}R"


def rval(v):
    """Ładny zapis wartości w stylu 1.10k / 82.5k / 255R."""
    if v >= 1000:
        x = v / 1000
        s = f"{x:.3g}"
        if len(s.replace(".", "")) < 3 and x < 100:
            s = f"{x:.2f}" if x < 10 else f"{x:.1f}"
        return s + "k"
    return f"{v}R"


# ----------------------------------------------------------------------------
# Symbole (biblioteka projektu TubeSel)
# pin: (numer, nazwa, x, y, kąt, długość)  — współrzędne biblioteki (oś Y w górę)
# ----------------------------------------------------------------------------
SYMBOLS = {
    "R": dict(
        ref="R", desc="Rezystor",
        pins=[("1", "~", 0, 3.81, 270, 1.27), ("2", "~", 0, -3.81, 90, 1.27)],
        gfx=['(rectangle (start -1.016 -2.54) (end 1.016 2.54) (stroke (width 0.254) (type default)) (fill (type none)))'],
        pin_names_hide=True, pin_numbers_hide=True,
        fref=(2.54, 1.27, 0), fval=(2.54, -1.27, 0), justify="left",
    ),
    "G6K-2F-Y": dict(
        ref="K", desc="Omron G6K-2F-Y, DPDT, cewka 12 V (1315 Ω). Pin 1 = cewka +, pin 8 = cewka −",
        pins=[("1", "+", -10.16, 5.08, 0, 2.54), ("8", "-", -10.16, -5.08, 0, 2.54),
              ("4", "NO1", 10.16, 7.62, 180, 2.54), ("3", "COM1", 10.16, 5.08, 180, 2.54),
              ("2", "NC1", 10.16, 2.54, 180, 2.54), ("5", "NO2", 10.16, -2.54, 180, 2.54),
              ("6", "COM2", 10.16, -5.08, 180, 2.54), ("7", "NC2", 10.16, -7.62, 180, 2.54)],
        gfx=['(rectangle (start -7.62 8.89) (end 7.62 -8.89) (stroke (width 0.254) (type default)) (fill (type background)))',
             '(rectangle (start -6.35 2.54) (end -3.81 -2.54) (stroke (width 0.254) (type default)) (fill (type none)))',
             '(polyline (pts (xy -6.35 -1.905) (xy -3.81 1.905)) (stroke (width 0.254) (type default)) (fill (type none)))',
             '(polyline (pts (xy -7.62 5.08) (xy -5.08 5.08) (xy -5.08 2.54)) (stroke (width 0) (type default)) (fill (type none)))',
             '(polyline (pts (xy -7.62 -5.08) (xy -5.08 -5.08) (xy -5.08 -2.54)) (stroke (width 0) (type default)) (fill (type none)))'],
        pin_names_hide=False, pin_numbers_hide=False,
        fref=(0, 10.16, 0), fval=(0, -10.16, 0), justify=None,
    ),
    "AudioConn": dict(
        ref="J", desc="Złącze audio stereo L / GND / R (JST XH 3p)",
        pins=[("1", "L", -5.08, 2.54, 0, 3.81), ("2", "GND", -5.08, 0, 0, 3.81), ("3", "R", -5.08, -2.54, 0, 3.81)],
        gfx=['(rectangle (start -1.27 3.81) (end 3.81 -3.81) (stroke (width 0.254) (type default)) (fill (type background)))'],
        pin_names_hide=False, pin_numbers_hide=False,
        fref=(1.27, 5.08, 0), fval=(1.27, -5.08, 0), justify=None,
    ),
    "C": dict(
        ref="C", desc="Kondensator",
        pins=[("1", "~", 0, 3.81, 270, 2.794), ("2", "~", 0, -3.81, 90, 2.794)],
        gfx=['(polyline (pts (xy -2.032 0.762) (xy 2.032 0.762)) (stroke (width 0.508) (type default)) (fill (type none)))',
             '(polyline (pts (xy -2.032 -0.762) (xy 2.032 -0.762)) (stroke (width 0.508) (type default)) (fill (type none)))'],
        pin_names_hide=True, pin_numbers_hide=True,
        fref=(2.54, 1.27, 0), fval=(2.54, -1.27, 0), justify="left",
    ),
    "SolderJumper": dict(
        ref="SJ", desc="Zworka lutownicza (domyślnie otwarta)",
        pins=[("1", "~", 0, 3.81, 270, 2.54), ("2", "~", 0, -3.81, 90, 2.54)],
        gfx=['(rectangle (start -1.016 1.778) (end 1.016 0.254) (stroke (width 0) (type default)) (fill (type outline)))',
             '(rectangle (start -1.016 -0.254) (end 1.016 -1.778) (stroke (width 0) (type default)) (fill (type outline)))'],
        pin_names_hide=True, pin_numbers_hide=True,
        fref=(2.54, 1.27, 0), fval=(2.54, -1.27, 0), justify="left",
    ),
    "MCP23017": dict(
        ref="U", desc="Ekspander I2C 16 bit, SOIC-28W",
        pins=[("9", "VDD", -15.24, 19.05, 0, 5.08), ("18", "~{RESET}", -15.24, 16.51, 0, 5.08),
              ("15", "A0", -15.24, 11.43, 0, 5.08), ("16", "A1", -15.24, 8.89, 0, 5.08), ("17", "A2", -15.24, 6.35, 0, 5.08),
              ("12", "SCL", -15.24, 1.27, 0, 5.08), ("13", "SDA", -15.24, -1.27, 0, 5.08),
              ("20", "INTA", -15.24, -6.35, 0, 5.08), ("19", "INTB", -15.24, -8.89, 0, 5.08),
              ("11", "NC", -15.24, -13.97, 0, 5.08), ("14", "NC", -15.24, -16.51, 0, 5.08), ("10", "VSS", -15.24, -19.05, 0, 5.08)]
             + [(str(21 + i), f"GPA{i}", 15.24, 19.05 - 2.54 * i, 180, 5.08) for i in range(8)]
             + [(str(1 + i), f"GPB{i}", 15.24, -1.27 - 2.54 * i, 180, 5.08) for i in range(8)],
        gfx=['(rectangle (start -10.16 21.59) (end 10.16 -21.59) (stroke (width 0.254) (type default)) (fill (type background)))'],
        pin_names_hide=False, pin_numbers_hide=False,
        fref=(0, 22.86, 0), fval=(0, 25.4, 0), justify=None,
    ),
    "ULN2803A": dict(
        ref="U", desc="8x Darlington z diodami (COM), SOIC-18W",
        pins=[(str(1 + i), f"I{1 + i}", -12.7, 8.89 - 2.54 * i, 0, 3.81) for i in range(8)]
             + [("9", "GND", -12.7, -12.7, 0, 3.81)]
             + [(str(18 - i), f"O{1 + i}", 12.7, 8.89 - 2.54 * i, 180, 3.81) for i in range(8)]
             + [("10", "COM", 12.7, -12.7, 180, 3.81)],
        gfx=['(rectangle (start -8.89 11.43) (end 8.89 -13.97) (stroke (width 0.254) (type default)) (fill (type background)))'],
        pin_names_hide=False, pin_numbers_hide=False,
        fref=(0, 12.7, 0), fval=(0, 15.24, 0), justify=None,
    ),
    "CtrlConn": dict(
        ref="J", desc="Złącze sterowania JST XH 6p: +12V, DGND, NC, SDA, SCL, DGND",
        pins=[("1", "+12V", -5.08, 6.35, 0, 3.81), ("2", "DGND", -5.08, 3.81, 0, 3.81), ("3", "NC", -5.08, 1.27, 0, 3.81),
              ("4", "SDA", -5.08, -1.27, 0, 3.81), ("5", "SCL", -5.08, -3.81, 0, 3.81), ("6", "DGND", -5.08, -6.35, 0, 3.81)],
        gfx=['(rectangle (start -1.27 7.62) (end 5.08 -7.62) (stroke (width 0.254) (type default)) (fill (type background)))'],
        pin_names_hide=False, pin_numbers_hide=False,
        fref=(1.27, 8.89, 0), fval=(1.27, -8.89, 0), justify=None,
    ),
    "DCDC_Module": dict(
        ref="U", desc="Moduł DC-DC step-down 12 V -> 3,3 V (1 -IN, 2 +IN, 3 OUT+, 4 OUT-)",
        pins=[("2", "+IN", -10.16, 2.54, 0, 2.54), ("1", "-IN", -10.16, -2.54, 0, 2.54),
              ("3", "OUT+", 10.16, 2.54, 180, 2.54), ("4", "OUT-", 10.16, -2.54, 180, 2.54)],
        gfx=['(rectangle (start -7.62 5.08) (end 7.62 -5.08) (stroke (width 0.254) (type default)) (fill (type background)))'],
        pin_names_hide=False, pin_numbers_hide=False,
        fref=(0, 6.35, 0), fval=(0, -6.35, 0), justify=None,
    ),
    "MountingHole": dict(
        ref="MH", desc="Otwór montażowy M3",
        pins=[],
        gfx=['(circle (center 0 0) (radius 1.27) (stroke (width 1.27) (type default)) (fill (type none)))'],
        pin_names_hide=True, pin_numbers_hide=True,
        fref=(0, 3.175, 0), fval=(0, -3.175, 0), justify=None,
    ),
    "MountingHole_Pad": dict(
        ref="MH", desc="Otwór montażowy M3 z padem (połączenie z obudową)",
        pins=[("1", "1", 0, -3.81, 90, 2.54)],
        gfx=['(circle (center 0 0) (radius 1.27) (stroke (width 1.27) (type default)) (fill (type none)))'],
        pin_names_hide=True, pin_numbers_hide=True,
        fref=(2.54, 1.27, 0), fval=(2.54, -0.635, 0), justify="left",
    ),
}

# ----------------------------------------------------------------------------
# Footprinty (z oficjalnej biblioteki KiCad, przepisane do formatu v8)
# ----------------------------------------------------------------------------
FOOTPRINTS = {
    "R": ("Resistor_SMD", "R_0805_2012Metric"),
    "C": ("Capacitor_SMD", "C_0805_2012Metric"),
    "SolderJumper": ("Jumper", "SolderJumper-2_P1.3mm_Open_Pad1.0x1.5mm"),
    "MCP23017": ("Package_SO", "SOIC-28W_7.5x17.9mm_P1.27mm"),
    "ULN2803A": ("Package_SO", "SOIC-18W_7.5x11.6mm_P1.27mm"),
    "DCDC_Module": ("TubeSel", "DCDC_Mini_4pin_14.17x8.24mm"),
    "CtrlConn": ("Connector_JST", "JST_XH_B6B-XH-A_1x06_P2.50mm_Vertical"),
    "G6K-2F-Y": ("Relay_SMD", "Relay_DPDT_Omron_G6K-2F-Y"),
    "AudioConn": ("Connector_JST", "JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical"),
    "MountingHole": ("MountingHole", "MountingHole_3.2mm_M3"),
    "MountingHole_Pad": ("MountingHole", "MountingHole_3.2mm_M3_Pad"),
}

# ----------------------------------------------------------------------------
# Lista elementów: ref, symbol, wartość, {pin: net}, pozycja schematu, pozycja PCB
# ----------------------------------------------------------------------------
X0, Y0 = 100.0, 100.0          # lewy górny róg płytki w Pcbnew
BW, BH = 96.0, 74.0
assert BW <= 100 and BH <= 100, "płytka max 10 x 10 cm"            # wymiary płytki [mm]

parts = []


def add(ref, sym, value, nets, sch, pcb, extra=None, nc=(), dnp=False, fp=None):
    parts.append(dict(ref=ref, sym=sym, value=value, nets=nets, sch=sch, pcb=pcb,
                      extra=dict(extra or {}), nc=set(nc), dnp=dnp, fp=fp or FOOTPRINTS[sym]))


G = "GND"
P12 = "+12V"

# --- Wejścia i selektor --------------------------------------------------------
for k in range(4):
    i = k + 1
    sy = 45.72 + 27.94 * k
    # złącze wejściowe
    add(f"J{i}", "AudioConn", f"IN{i}", {"1": f"IN{i}_L", "2": G, "3": f"IN{i}_R"},
        sch=(35.56, sy), pcb=(X0 + 16 + 14.5 * k + 2.5, Y0 + 8.0, 180))
    # przekaźnik wejścia
    cx = X0 + 16 + 14.5 * k
    add(f"K{i}", "G6K-2F-Y", "G6K-2F-Y 12V",
        {"1": P12, "8": f"COIL{i}",
         "3": f"IN{i}_L", "4": "BUS_L", "2": f"SH{i}_L",
         "6": f"IN{i}_R", "5": "BUS_R", "7": f"SH{i}_R"},
        sch=(88.9, sy), pcb=(cx, Y0 + 21.0, 180), extra={"Funkcja": f"Wejście {i}"})
    # obciążenie niewybranego wejścia
    add(f"R{2 * k + 1}", "R", "1k", {"1": f"SH{i}_L", "2": G},
        sch=(132.08, sy), pcb=(cx + 5.9, Y0 + 21.6, 90), extra={"Tolerancja": "1%"})
    add(f"R{2 * k + 2}", "R", "1k", {"1": f"SH{i}_R", "2": G},
        sch=(142.24, sy), pcb=(cx - 5.9, Y0 + 21.6, 90), extra={"Tolerancja": "1%"})

# --- Drabinka ------------------------------------------------------------------
def node(n, ch):
    if n == 0:
        return f"BUS_{ch}"
    if n == len(LADDER):
        return f"OUT_{ch}"
    return f"A{n}_{ch}"


for n, (db, rs, rp) in enumerate(LADDER, start=1):
    kref = f"K{4 + n}"
    col, row = (n - 1) // 3, (n - 1) % 3
    sx, sy = 190.5 + 114.3 * col, 45.72 + 53.34 * row
    cx, cy = X0 + 22 + 11.5 * (n - 1), Y0 + 41.0
    add(kref, "G6K-2F-Y", "G6K-2F-Y 12V",
        {"1": P12, "8": f"COIL{4 + n}",
         "3": node(n, "L"), "2": node(n - 1, "L"), "4": f"P{n}_L",
         "6": node(n, "R"), "7": node(n - 1, "R"), "5": f"P{n}_R"},
        sch=(sx, sy), pcb=(cx, cy, 180), extra={"Funkcja": f"Tłumik -{db} dB"})
    base = 8 + 4 * (n - 1)
    tol = {"Tolerancja": "0.1%"}
    add(f"R{base + 1}", "R", rval(rs), {"1": node(n - 1, "L"), "2": node(n, "L")},
        sch=(sx + 30.48, sy), pcb=(cx + 1.5, cy - 8.0, 90), extra=tol)
    add(f"R{base + 2}", "R", rval(rp), {"1": f"P{n}_L", "2": G},
        sch=(sx + 40.64, sy), pcb=(cx + 4.0, cy - 8.0, 90), extra=tol)
    add(f"R{base + 3}", "R", rval(rs), {"1": node(n - 1, "R"), "2": node(n, "R")},
        sch=(sx + 50.8, sy), pcb=(cx - 1.5, cy - 8.0, 90), extra=tol)
    add(f"R{base + 4}", "R", rval(rp), {"1": f"P{n}_R", "2": G},
        sch=(sx + 60.96, sy), pcb=(cx - 4.0, cy - 8.0, 90), extra=tol)

# --- Mute, terminator, wyjście ----------------------------------------------
add("K11", "G6K-2F-Y", "G6K-2F-Y 12V",
    {"1": P12, "8": "COIL11", "3": "OUT_L", "2": G, "6": "OUT_R", "7": G},
    sch=(88.9, 172.72), pcb=(X0 + 82, Y0 + 21.0, 180), nc=("4", "5"),
    extra={"Funkcja": "Mute (bez prądu = wyciszone)"})
add("R33", "R", "10k", {"1": "OUT_L", "2": G}, sch=(132.08, 172.72),
    pcb=(X0 + 82 + 5.9, Y0 + 21.6, 90), extra={"Tolerancja": "0.1%"})
add("R34", "R", "10k", {"1": "OUT_R", "2": G}, sch=(142.24, 172.72),
    pcb=(X0 + 82 - 5.9, Y0 + 21.6, 90), extra={"Tolerancja": "0.1%"})
add("J5", "AudioConn", "OUT", {"1": "OUT_L", "2": G, "3": "OUT_R"},
    sch=(170.18, 172.72), pcb=(X0 + 82 + 2.5, Y0 + 8.0, 180))

# --- Sterowanie: MCP23017 + 2x ULN2803A ---------------------------------------
DG, V33 = "DGND", "+3V3"
add("J6", "CtrlConn", "CTRL (do ESP32)", {"1": P12, "2": DG, "4": "SDA", "5": "SCL", "6": DG},
    sch=(190.5, 215.9), pcb=(X0 + 11.0, Y0 + 69.5, 0), nc=("3",), extra={"MPN": "JST B6B-XH-A + wtyk XHP-6"})
add("U4", "DCDC_Module", "DC-DC 3V3", {"2": P12, "1": DG, "3": V33, "4": DG}, sch=(127.0, 218.44),
    pcb=(X0 + 14.5, Y0 + 58.5, 0), extra={"MPN": "Mini DC-DC step-down 3,3 V (pinout: 1 -IN, 2 +IN, 3 OUT+, 4 OUT-)"})
add("C4", "C", "10u/10V", {"1": V33, "2": DG}, sch=(152.4, 220.98), pcb=(X0 + 26.5, Y0 + 58.5, 90),
    fp=("Capacitor_SMD", "C_1206_3216Metric"))
mcp = {"9": V33, "10": DG, "18": V33, "15": "MCP_A0", "16": "MCP_A1", "17": "MCP_A2", "12": "SCL", "13": "SDA"}
for i in range(8):
    mcp[str(21 + i)] = f"DRV{i + 1}"
for i in range(3):
    mcp[str(1 + i)] = f"DRV{9 + i}"
add("U1", "MCP23017", "MCP23017", mcp, sch=(241.3, 223.52), pcb=(X0 + 38.0, Y0 + 60.0, 270),
    nc=("11", "14", "19", "20", "4", "5", "6", "7", "8"), extra={"MPN": "MCP23017-E/SO"})
u2 = {"9": DG, "10": P12}
for i in range(8):
    u2[str(1 + i)] = f"DRV{i + 1}"; u2[str(18 - i)] = f"COIL{i + 1}"
add("U2", "ULN2803A", "ULN2803A", u2, sch=(299.72, 213.36), pcb=(X0 + 58.0, Y0 + 60.0, 90),
    extra={"MPN": "ULN2803G-S18-R"})
u3 = {"9": DG, "10": P12}
for i in range(3):
    u3[str(1 + i)] = f"DRV{9 + i}"; u3[str(18 - i)] = f"COIL{9 + i}"
for i in range(3, 8):
    u3[str(1 + i)] = DG
add("U3", "ULN2803A", "ULN2803A", u3, sch=(325.12, 254.0), pcb=(X0 + 73.0, Y0 + 60.0, 90),
    nc=tuple(str(18 - i) for i in range(3, 8)), extra={"MPN": "ULN2803G-S18-R"})
add("R36", "R", "4.7k", {"1": V33, "2": "SDA"}, sch=(198.12, 241.3), pcb=(X0 + 30.0, Y0 + 51.5, 0), extra={"Tolerancja": "1%"})
add("R37", "R", "4.7k", {"1": V33, "2": "SCL"}, sch=(205.74, 241.3), pcb=(X0 + 34.0, Y0 + 51.5, 0), extra={"Tolerancja": "1%"})
add("C1", "C", "100n", {"1": V33, "2": DG}, sch=(213.36, 264.16), pcb=(X0 + 38.5, Y0 + 51.5, 0))
add("C2", "C", "100n/25V", {"1": P12, "2": DG}, sch=(220.98, 264.16), pcb=(X0 + 86.0, Y0 + 63.0, 90))
add("C3", "C", "10u/25V", {"1": P12, "2": DG}, sch=(228.6, 264.16), pcb=(X0 + 86.0, Y0 + 57.0, 90),
    fp=("Capacitor_SMD", "C_1206_3216Metric"))
for k in range(3):
    add(f"R{38 + k}", "R", "10k", {"1": f"MCP_A{k}", "2": DG}, sch=(238.76 + 7.62 * k, 261.62),
        pcb=(X0 + 29.5 + 4.0 * k, Y0 + 68.0, 0), extra={"Tolerancja": "1%"})
    add(f"SJ{k + 1}", "SolderJumper", f"A{k}", {"1": V33, "2": f"MCP_A{k}"}, sch=(264.16 + 7.62 * k, 261.62),
        pcb=(X0 + 41.5 + 4.0 * k, Y0 + 68.0, 0))
add("R41", "R", "0R", {"1": G, "2": DG}, sch=(396.24, 200.66), pcb=(X0 + 26.5, Y0 + 51.5, 0), dnp=True,
    extra={"Uwaga": "Nie montować domyślnie; łączy masę cyfrową z masą audio"})

# --- Mechanika ------------------------------------------------------------------
add("MH1", "MountingHole_Pad", "M3 (GND->obudowa)", {"1": "CHASSIS"}, sch=(365.76, 200.66),
    pcb=(X0 + 4, Y0 + 4, 0))
add("R35", "R", "0R", {"1": G, "2": "CHASSIS"}, sch=(386.08, 200.66),
    pcb=(X0 + 8.5, Y0 + 12.0, 90), dnp=True,
    extra={"Uwaga": "Nie montować domyślnie; zworka masa audio - obudowa"})
for i, (px, py) in enumerate([(X0 + BW - 4, Y0 + 4), (X0 + 4, Y0 + BH - 4), (X0 + BW - 4, Y0 + BH - 4)]):
    add(f"MH{i + 2}", "MountingHole", "M3", {}, sch=(360.68 + 12.7 * i, 228.6), pcb=(px, py, 0))

# --- numery LCSC (montaż JLCPCB) -----------------------------------------------
LCSC_OTHER = {"G6K-2F-Y": ("C397192", "G6K-2F-Y-TR DC12"), "MCP23017": ("C47023", "MCP23017-E/SO"),
              "ULN2803A": ("C33924", "ULN2803G-S18-R (UTC)"), "100n": ("C49678", "CC0805KRX7R9BB104"),
              "100n/25V": ("C49678", "CC0805KRX7R9BB104"), "10u/25V": ("C13585", "CL31A106KBHNNNE"),
              "10u/10V": ("C13585", "CL31A106KBHNNNE")}
_r01 = {rval(v): c for v, c in LCSC_01.items()}
_r01["10k"] = LCSC_01[10000]
for p in parts:
    code = None
    if p["sym"] == "R" and not p["dnp"]:
        code = (_r01 if p["extra"].get("Tolerancja") == "0.1%" else LCSC_1).get(p["value"])
        assert code, f"brak LCSC dla {p['ref']} {p['value']}"
    elif p["sym"] in LCSC_OTHER:
        code = LCSC_OTHER[p["sym"]]
    elif p["value"] in LCSC_OTHER:
        code = LCSC_OTHER[p["value"]]
    if code:
        p["extra"]["LCSC"] = code[0]
        p["extra"]["MPN"] = code[1]

# porządek: unikalne referencje
refs = [p["ref"] for p in parts]
assert len(refs) == len(set(refs)), "zdublowane referencje"

# ----------------------------------------------------------------------------
# Pomocnicze
# ----------------------------------------------------------------------------
def f(v):
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


# ----------------------------------------------------------------------------
# Biblioteka symboli (.kicad_sym) i lib_symbols w schemacie
# ----------------------------------------------------------------------------
def symbol_def(name, s, prefix=""):
    out = [f'(symbol {q(prefix + name)}']
    if s["pin_numbers_hide"]:
        out.append("(pin_numbers hide)")
    if s["pin_names_hide"]:
        out.append("(pin_names (offset 0.254) hide)")
    else:
        out.append("(pin_names (offset 0.762))")
    out.append("(exclude_from_sim no) (in_bom yes) (on_board yes)")
    lib, fp = FOOTPRINTS[name]
    props = [("Reference", s["ref"], s["fref"], False), ("Value", name, s["fval"], False),
             ("Footprint", f"{lib}:{fp}", (0, 0, 0), True), ("Datasheet", "~", (0, 0, 0), True),
             ("Description", s["desc"], (0, 0, 0), True)]
    for pn, pv, (x, y, a), hid in props:
        j = f' (justify {s["justify"]})' if s["justify"] and pn in ("Reference", "Value") else ""
        out.append(f'(property {q(pn)} {q(pv)} (at {f(x)} {f(y)} {f(a)}) (effects (font (size 1.27 1.27)){j}{" hide" if hid else ""}))')
    out.append(f'(symbol {q(name + "_0_1")} ' + " ".join(s["gfx"]) + ")")
    pins = []
    for num, pname, x, y, a, ln in s["pins"]:
        pins.append(f'(pin passive line (at {f(x)} {f(y)} {f(a)}) (length {f(ln)}) '
                    f'(name {q(pname)} (effects (font (size 1.27 1.27)))) '
                    f'(number {q(num)} (effects (font (size 1.27 1.27)))))')
    out.append(f'(symbol {q(name + "_1_1")} ' + " ".join(pins) + ")")
    out.append(")")
    return "\n".join(out)


def write_symlib():
    body = "\n".join(symbol_def(n, s) for n, s in SYMBOLS.items())
    txt = f'(kicad_symbol_lib (version 20231120) (generator "tube_selector_gen") (generator_version "8.0")\n{body}\n)\n'
    open(os.path.join(OUT, "TubeSel.kicad_sym"), "w").write(txt)
    open(os.path.join(OUT, "fp-lib-table"), "w").write(
        '(fp_lib_table\n  (version 7)\n  (lib (name "TubeSel")(type "KiCad")(uri "${KIPRJMOD}/TubeSel.pretty")(options "")(descr "Footprinty projektu"))\n)\n')
    open(os.path.join(OUT, "sym-lib-table"), "w").write(
        '(sym_lib_table\n  (version 7)\n  (lib (name "TubeSel")(type "KiCad")(uri "${KIPRJMOD}/TubeSel.kicad_sym")(options "")(descr "Symbole projektu selektora"))\n)\n')


# ----------------------------------------------------------------------------
# Schemat
# ----------------------------------------------------------------------------
STUB = 2.54


def pin_abs(part, pin):
    sx, sy = part["sch"]
    _, _, px, py, a, _ = pin
    return sx + px, sy - py, a


def outward(a):
    # kierunek "na zewnątrz" od symbolu (w układzie schematu, Y w dół)
    return {0: (-1, 0), 180: (1, 0), 270: (0, -1), 90: (0, 1)}[a]


def label_angle(a):
    return {0: 180, 180: 0, 270: 90, 90: 270}[a]


def write_sch():
    items = []
    used_syms = sorted({p["sym"] for p in parts})
    libsyms = "\n".join(symbol_def(n, SYMBOLS[n], prefix="TubeSel:") for n in used_syms)

    for p in parts:
        s = SYMBOLS[p["sym"]]
        sx, sy = p["sch"]
        lib, fp = p["fp"]
        su = U("sym", p["ref"])
        fr = s["fref"]; fv = s["fval"]
        j = f' (justify {s["justify"]})' if s["justify"] else ""
        props = [
            f'(property "Reference" {q(p["ref"])} (at {f(sx + fr[0])} {f(sy - fr[1])} 0) (effects (font (size 1.27 1.27)){j}))',
            f'(property "Value" {q(p["value"])} (at {f(sx + fv[0])} {f(sy - fv[1])} 0) (effects (font (size 1.27 1.27)){j}))',
            f'(property "Footprint" {q(lib + ":" + fp)} (at {f(sx)} {f(sy)} 0) (effects (font (size 1.27 1.27)) hide))',
            f'(property "Datasheet" "~" (at {f(sx)} {f(sy)} 0) (effects (font (size 1.27 1.27)) hide))',
            f'(property "Description" {q(s["desc"])} (at {f(sx)} {f(sy)} 0) (effects (font (size 1.27 1.27)) hide))',
        ]
        for k, v in p["extra"].items():
            props.append(f'(property {q(k)} {q(v)} (at {f(sx)} {f(sy)} 0) (effects (font (size 1.27 1.27)) hide))')
        pins = " ".join(f'(pin {q(pn[0])} (uuid {q(U("pin", p["ref"], pn[0]))}))' for pn in s["pins"])
        items.append(
            f'(symbol (lib_id {q("TubeSel:" + p["sym"])}) (at {f(sx)} {f(sy)} 0) (unit 1)\n'
            f'  (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp {"yes" if p["dnp"] else "no"}) (fields_autoplaced yes)\n'
            f'  (uuid {q(su)})\n  ' + "\n  ".join(props) + f"\n  {pins}\n"
            f'  (instances (project {q(PROJ)} (path {q("/" + ROOT_UUID)} (reference {q(p["ref"])}) (unit 1))))\n)')

        # odcinki przewodów + etykiety na każdym pinie
        for pn in s["pins"]:
            num = pn[0]
            x, y, a = pin_abs(p, pn)
            if num in p["nc"]:
                items.append(f'(no_connect (at {f(x)} {f(y)}) (uuid {q(U("nc", p["ref"], num))}))')
                continue
            net = p["nets"][num]
            dx, dy = outward(a)
            x2, y2 = x + dx * STUB, y + dy * STUB
            items.append(f'(wire (pts (xy {f(x)} {f(y)}) (xy {f(x2)} {f(y2)})) (stroke (width 0) (type default)) (uuid {q(U("w", p["ref"], num))}))')
            la = label_angle(a)
            just = {0: "left bottom", 90: "left bottom", 180: "right bottom", 270: "right bottom"}[la]
            items.append(f'(label {q(net)} (at {f(x2)} {f(y2)} {la}) (fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify {just})) (uuid {q(U("lbl", p["ref"], num))}))')

    # opisy bloków
    def text(t, x, y, size=2.0, bold=False):
        b = " bold" if bold else ""
        items.append(f'(text {q(t)} (exclude_from_sim no) (at {f(x)} {f(y)} 0) (effects (font (size {size} {size}){b}) (justify left bottom)) (uuid {q(U("txt", t, x, y))}))')

    text("WEJŚCIA (JST XH, kabel ekranowany do gniazd RCA)", 15.24, 30.48, 2.0, True)
    text("SELEKTOR: COM = wejście, NO = szyna, NC = 1k do masy", 76.2, 30.48, 2.0, True)
    text("DRABINKA 0..63 dB co 1 dB, Z = 10 kΩ (Rs szeregowy, Rp do masy, rezystory 0,1%)", 180.34, 25.4, 2.0, True)
    for n, (db, rs, rp) in enumerate(LADDER, start=1):
        col, row = (n - 1) // 3, (n - 1) % 3
        sx, sy = 190.5 + 114.3 * col, 45.72 + 53.34 * row
        text(f"Bit {n - 1}: -{db} dB  (Rs {rval(rs)}, Rp {rval(rp)})", sx - 10.16, sy - 12.7, 1.524, True)
    text("MUTE (fail-safe) + TERMINATOR + WYJŚCIE", 76.2, 157.48, 2.0, True)
    text("Cewka K11 bez prądu = wyjście zwarte do masy.\nDźwięk dopiero po załączeniu K11 (np. gdy lampy nagrzane i bias OK).",
         76.2, 190.5, 1.524)
    text("ZASILANIE 3,3 V: moduł DC-DC 12 V -> 3,3 V (wersja stała 3,3 V)", 76.2, 205.74, 2.0, True)
    text("Pobór z 3,3 V: kilka mA (MCP23017 + pull-upy).\nJ6 pin 3 nie jest podłączony: nie łącz 3,3 V z ESP32 z tą płytką.", 76.2, 236.22, 1.524)
    text("STEROWANIE: MCP23017 (I2C) + 2x ULN2803A (diody gaszące wbudowane, COM -> +12V)", 180.34, 190.5, 2.0, True)
    text("J6 do ESP32: 1 +12V, 2 DGND, 3 n/c, 4 SDA, 5 SCL, 6 DGND.\n"
         "Adres I2C: SJ1..SJ3 otwarte = 0x20 (zwarcie SJn ustawia bit An: 0x20..0x27).\n"
         "GPA0..7 -> K1..K8, GPB0..2 -> K9..K11 (wyjście H = cewka ON). GPB3..7 wolne.\n"
         "Masa cyfrowa DGND oddzielona od audio GND; R41 (0R, DNP) łączy je w jednym punkcie, jeśli trzeba.",
         180.34, 283.21, 1.524)
    text("MECHANIKA / MASY", 355.6, 190.5, 2.0, True)
    text("R35 (0R, DNP) łączy masę audio z obudową przez MH1.\nMontuj tylko jeśli masa nie jest łączona z obudową w innym miejscu.",
         355.6, 246.38, 1.524)
    notes = ("UWAGI:\n"
             "1. Biegunowość cewki G6K: pin 1 = + (+12V), pin 8 = - (do ULN2803) - potwierdzone z opisu przekaźnika.\n"
             "   Przy montażu ustaw znacznik pinu 1 na obudowie zgodnie ze znacznikiem na sitodruku.\n"
             "2. Bity drabinki: K5=1dB, K6=2dB, K7=4dB, K8=8dB, K9=16dB, K10=32dB (cewka ON = tłumienie).\n"
             "   Zmiana głośności: najpierw ZAŁĄCZ nowe bity, ~5 ms, potem WYŁĄCZ zbędne.\n"
             "3. Źródło widzi zawsze 10 kΩ; impedancja wyjściowa max ok. 5 kΩ -> krótko do siatki pierwszej lampy.")
    text(notes, 15.24, 256.54, 1.524)

    sch = (f'(kicad_sch (version 20231120) (generator "eeschema") (generator_version "8.0")\n'
           f'(uuid {q(ROOT_UUID)})\n(paper "A3")\n'
           f'(title_block (title {q(TITLE)}) (date {q(DATE)}) (rev {q(REV)}) (company "Wzmacniacz lampowy") '
           f'(comment 1 "4 wejścia stereo, drabinka 6 bit 0-63 dB, mute fail-safe") (comment 2 "Przekaźniki Omron G6K-2F-Y 12 V"))\n'
           f'(lib_symbols\n{libsyms}\n)\n' + "\n".join(items) +
           f'\n(sheet_instances (path "/" (page "1")))\n)\n')
    open(os.path.join(OUT, PROJ + ".kicad_sch"), "w").write(sch)


# ----------------------------------------------------------------------------
# Parser starych footprintów (.kicad_mod v5) -> struktura
# ----------------------------------------------------------------------------
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


def kv(node, key):
    for x in node:
        if isinstance(x, list) and x and x[0] == key:
            return x
    return None


def load_fp(lib, name):
    base = OUT if lib == "TubeSel" else FPLIB
    tree = sexp(open(f"{base}/{lib}.pretty/{name}.kicad_mod").read())
    fp = dict(descr="", tags="", attr=None, gfx=[], pads=[], ref_at=(0, -2), val_at=(0, 2), fab_ref=None, model=None)
    for n in tree[2:]:
        if not isinstance(n, list):
            continue
        h = n[0]
        if h == "descr":
            fp["descr"] = n[1]
        elif h == "tags":
            fp["tags"] = n[1]
        elif h == "attr":
            fp["attr"] = n[1]
        elif h == "fp_text":
            at = kv(n, "at"); lay = kv(n, "layer")[1]
            pos = (float(at[1]), float(at[2]))
            if n[1] == "reference":
                fp["ref_at"] = pos
            elif n[1] == "value":
                fp["val_at"] = pos
            elif n[1] == "user" and lay.endswith("Fab"):
                fp["fab_ref"] = pos
        elif h == "fp_line":
            s = kv(n, "start"); e = kv(n, "end")
            fp["gfx"].append(("line", float(s[1]), float(s[2]), float(e[1]), float(e[2]),
                              kv(n, "layer")[1], float(kv(n, "width")[1])))
        elif h == "fp_circle":
            c = kv(n, "center"); e = kv(n, "end")
            fp["gfx"].append(("circle", float(c[1]), float(c[2]), float(e[1]), float(e[2]),
                              kv(n, "layer")[1], float(kv(n, "width")[1])))
        elif h == "pad":
            at = kv(n, "at"); sz = kv(n, "size"); dr = kv(n, "drill"); rr = kv(n, "roundrect_rratio")
            layers = kv(n, "layers")[1:]
            fp["pads"].append(dict(num=n[1], type=n[2], shape=n[3],
                                   x=float(at[1]), y=float(at[2]), rot=float(at[3]) if len(at) > 3 else 0.0,
                                   w=float(sz[1]), h=float(sz[2]), drill=float(dr[1]) if dr else None,
                                   layers=layers, rr=float(rr[1]) if rr else None))
        elif h == "model":
            fp["model"] = n[1].replace("${KISYS3DMOD}", "${KICAD8_3DMODEL_DIR}")
    if fp["attr"] is None:
        fp["attr"] = "smd" if all(p["type"] == "smd" for p in fp["pads"]) else "through_hole"
    return fp


def rot(x, y, a):
    """Obrót jak w Pcbnew (kąt dodatni = przeciwnie do wskazówek zegara na ekranie, Y w dół)."""
    r = math.radians(a)
    return x * math.cos(r) + y * math.sin(r), -x * math.sin(r) + y * math.cos(r)


# ----------------------------------------------------------------------------
# PCB
# ----------------------------------------------------------------------------
def all_nets():
    names = set()
    for p in parts:
        names |= set(p["nets"].values())
    order = ["GND", "+12V"] + sorted(n for n in names if n not in ("GND", "+12V"))
    return {n: i + 1 for i, n in enumerate(order)}


def pcb_net(n):
    return "/" + n


def write_pcb():
    nets = all_nets()
    out = [f'(kicad_pcb (version 20240108) (generator "pcbnew") (generator_version "8.0")',
           '(general (thickness 1.6) (legacy_teardrops no))',
           '(paper "A4")',
           f'(title_block (title {q(TITLE)}) (date {q(DATE)}) (rev {q(REV)}) (company "Wzmacniacz lampowy"))',
           '(layers (0 "F.Cu" signal) (31 "B.Cu" signal) (32 "B.Adhes" user "B.Adhesive") (33 "F.Adhes" user "F.Adhesive") '
           '(34 "B.Paste" user) (35 "F.Paste" user) (36 "B.SilkS" user "B.Silkscreen") (37 "F.SilkS" user "F.Silkscreen") '
           '(38 "B.Mask" user) (39 "F.Mask" user) (40 "Dwgs.User" user "User.Drawings") (41 "Cmts.User" user "User.Comments") '
           '(42 "Eco1.User" user "User.Eco1") (43 "Eco2.User" user "User.Eco2") (44 "Edge.Cuts" user) (45 "Margin" user) '
           '(46 "B.CrtYd" user "B.Courtyard") (47 "F.CrtYd" user "F.Courtyard") (48 "B.Fab" user) (49 "F.Fab" user))',
           '(setup (pad_to_mask_clearance 0) (allow_soldermask_bridges_in_footprints no))',
           '(net 0 "")']
    for n, i in nets.items():
        out.append(f'(net {i} {q(pcb_net(n))})')

    fpcache = {}
    for p in parts:
        lib, name = p["fp"]
        if name not in fpcache:
            fpcache[name] = load_fp(lib, name)
        fp = fpcache[name]
        x, y, a = p["pcb"]
        A = f" {f(a)}" if a else ""
        L = [f'(footprint {q(lib + ":" + name)} (layer "F.Cu") (uuid {q(U("fp", p["ref"]))}) (at {f(x)} {f(y)}{A})',
             f'  (descr {q(fp["descr"])}) (tags {q(fp["tags"])})',
             f'  (property "Reference" {q(p["ref"])} (at {f(fp["ref_at"][0])} {f(fp["ref_at"][1])}{A}) (layer "F.SilkS") (uuid {q(U("fpr", p["ref"]))}) (effects (font (size 0.8 0.8) (thickness 0.12))))',
             f'  (property "Value" {q(p["value"])} (at {f(fp["val_at"][0])} {f(fp["val_at"][1])}{A}) (layer "F.Fab") (uuid {q(U("fpv", p["ref"]))}) (effects (font (size 0.8 0.8) (thickness 0.12))))',
             f'  (path {q("/" + U("sym", p["ref"]))}) (sheetname "Root") (sheetfile {q(PROJ + ".kicad_sch")})',
             f'  (attr {fp["attr"]}{" dnp" if p["dnp"] else ""})']
        for g in fp["gfx"]:
            kind, x1, y1, x2, y2, lay, w = g
            if kind == "line":
                L.append(f'  (fp_line (start {f(x1)} {f(y1)}) (end {f(x2)} {f(y2)}) (stroke (width {f(w)}) (type solid)) (layer {q(lay)}) (uuid {q(U("g", p["ref"], len(L)))}))')
            else:
                L.append(f'  (fp_circle (center {f(x1)} {f(y1)}) (end {f(x2)} {f(y2)}) (stroke (width {f(w)}) (type solid)) (fill none) (layer {q(lay)}) (uuid {q(U("g", p["ref"], len(L)))}))')
        if fp["fab_ref"] is not None:
            L.append(f'  (fp_text user "${{REFERENCE}}" (at {f(fp["fab_ref"][0])} {f(fp["fab_ref"][1])}{A}) (layer "F.Fab") (uuid {q(U("fpt", p["ref"]))}) (effects (font (size 0.8 0.8) (thickness 0.12))))')
        for pad in fp["pads"]:
            num = "" if pad["type"] == "np_thru_hole" else pad["num"]
            pr = (pad["rot"] + a) % 360
            PR = f" {f(pr)}" if pr else ""
            layers = " ".join(q(l) for l in pad["layers"])
            s = f'  (pad {q(num)} {pad["type"]} {pad["shape"]} (at {f(pad["x"])} {f(pad["y"])}{PR}) (size {f(pad["w"])} {f(pad["h"])})'
            if pad["drill"] is not None:
                s += f' (drill {f(pad["drill"])})'
            s += f' (layers {layers})'
            if pad["rr"] is not None:
                s += f' (roundrect_rratio {f(pad["rr"])})'
            if num and num in p["nets"]:
                nn = p["nets"][num]
                s += f' (net {nets[nn]} {q(pcb_net(nn))}) (pintype "passive")'
            elif num:
                s += f' (pintype "passive+no_connect")'
            s += f' (uuid {q(U("pad", p["ref"], pad["num"], pad["x"], pad["y"]))}))'
            L.append(s)
        if fp["model"]:
            L.append(f'  (model {q(fp["model"])} (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))')
        L.append(")")
        out.append("\n".join(L))

    # obrys płytki (zaokrąglone narożniki r = 2 mm)
    r = 2.0
    x1, y1, x2, y2 = X0, Y0, X0 + BW, Y0 + BH
    segs = [((x1 + r, y1), (x2 - r, y1)), ((x2, y1 + r), (x2, y2 - r)),
            ((x2 - r, y2), (x1 + r, y2)), ((x1, y2 - r), (x1, y1 + r))]
    for i, (s, e) in enumerate(segs):
        out.append(f'(gr_line (start {f(s[0])} {f(s[1])}) (end {f(e[0])} {f(e[1])}) (stroke (width 0.1) (type default)) (layer "Edge.Cuts") (uuid {q(U("edge", i))}))')
    c45 = r * (1 - math.sqrt(0.5))
    arcs = [((x1, y1 + r), (x1 + c45, y1 + c45), (x1 + r, y1)),
            ((x2 - r, y1), (x2 - c45, y1 + c45), (x2, y1 + r)),
            ((x2, y2 - r), (x2 - c45, y2 - c45), (x2 - r, y2)),
            ((x1 + r, y2), (x1 + c45, y2 - c45), (x1, y2 - r))]
    for i, (s, m, e) in enumerate(arcs):
        out.append(f'(gr_arc (start {f(s[0])} {f(s[1])}) (mid {f(m[0])} {f(m[1])}) (end {f(e[0])} {f(e[1])}) (stroke (width 0.1) (type default)) (layer "Edge.Cuts") (uuid {q(U("arc", i))}))')

    # opisy na sitodruku
    def gtext(t, x, y, size=1.0, layer="F.SilkS", ang=0, mirror=False):
        m = " mirror" if mirror else ""
        A = f" {f(ang)}" if ang else ""
        out.append(f'(gr_text {q(t)} (at {f(x)} {f(y)}{A}) (layer {q(layer)}) (uuid {q(U("gt", t, x, y, layer))}) '
                   f'(effects (font (size {size} {size}) (thickness {f(size * 0.15)})) (justify{m})))')

    for k in range(4):
        cx = X0 + 16 + 14.5 * k
        gtext(f"IN{k + 1}", cx + 2.5 - 2.5, Y0 + 2.6, 1.0)
        gtext("R  G  L", cx + 2.5 - 2.5, Y0 + 12.2, 0.7)
    gtext("OUT", X0 + 82, Y0 + 2.6, 1.0)
    gtext("R  G  L", X0 + 82, Y0 + 12.2, 0.7)
    gtext("MUTE", X0 + 90.5, Y0 + 28.0, 0.8)
    for n, (db, _, _) in enumerate(LADDER, start=1):
        gtext(f"-{db}dB", X0 + 22 + 11.5 * (n - 1), Y0 + 47.6, 0.7)
    gtext("J6: 12V GND -- SDA SCL GND", X0 + 17.25, Y0 + 65.75, 0.6)
    gtext("DC-DC 12V->3V3", X0 + 14.5, Y0 + 51.3, 0.8)
    gtext("+IN", X0 + 7.4 + 3.2, Y0 + 62.6, 0.6)
    gtext("-IN", X0 + 7.4 + 3.2, Y0 + 54.4, 0.6)
    gtext("OUT+", X0 + 21.6 - 3.4, Y0 + 62.6, 0.6)
    gtext("OUT-", X0 + 21.6 - 3.4, Y0 + 54.4, 0.6)
    gtext("A0  A1  A2 (I2C 0x20+)", X0 + 45.5, Y0 + 70.6, 0.6)
    gtext(f"TubeSel v{REV}  selektor 4in + drabinka 63dB", X0 + BW / 2, Y0 + BH - 7, 1.2, "B.SilkS", mirror=True)
    gtext("Omron G6K-2F-Y 12V | R 0805 0.1%", X0 + BW / 2, Y0 + BH - 4.5, 0.9, "B.SilkS", mirror=True)

    # strefy masy na obu warstwach
    m = 0.5
    pts = f"(xy {f(x1 + m)} {f(y1 + m)}) (xy {f(x2 - m)} {f(y1 + m)}) (xy {f(x2 - m)} {f(y2 - m)}) (xy {f(x1 + m)} {f(y2 - m)})"
    yd = Y0 + 49.5
    dpts = f"(xy {f(x1 + m)} {f(yd)}) (xy {f(x2 - m)} {f(yd)}) (xy {f(x2 - m)} {f(y2 - m)}) (xy {f(x1 + m)} {f(y2 - m)})"
    for lay in ("F.Cu", "B.Cu"):
        for net, poly, prio in (("GND", pts, 0), ("DGND", dpts, 1)):
            out.append(f'(zone (net {nets[net]}) (net_name {q(pcb_net(net))}) (layer {q(lay)}) (uuid {q(U("zone", lay, net))}) '
                       f'(name {q(net + "_" + lay)}) (hatch edge 0.5) (priority {prio}) '
                       f'(connect_pads (clearance 0.3)) (min_thickness 0.25) (filled_areas_thickness no) '
                       f'(fill (thermal_gap 0.4) (thermal_bridge_width 0.4)) (polygon (pts {poly})))')
    out.append(")")
    open(os.path.join(OUT, PROJ + ".kicad_pcb"), "w").write("\n".join(out) + "\n")


# ----------------------------------------------------------------------------
# Projekt (.kicad_pro) z regułami i klasami sieci
# ----------------------------------------------------------------------------
def write_pro():
    audio = sorted({n for p in parts for n in p["nets"].values()
                    if n not in ("GND", "+12V", "CHASSIS", "DGND", "+3V3", "SDA", "SCL")
                    and not n.startswith(("COIL", "DRV", "MCP_"))})
    coil = sorted({n for p in parts for n in p["nets"].values() if n.startswith("COIL")} | {"+12V"})
    pro = {
        "board": {
            "design_settings": {
                "defaults": {"board_outline_line_width": 0.1, "copper_line_width": 0.2, "copper_text_size_h": 1.5,
                             "copper_text_size_v": 1.5, "silk_line_width": 0.12, "silk_text_size_h": 1.0,
                             "silk_text_size_v": 1.0, "silk_text_thickness": 0.15},
                "rules": {"min_clearance": 0.2, "min_track_width": 0.2, "min_via_diameter": 0.5,
                          "min_through_hole_diameter": 0.3, "min_copper_edge_clearance": 0.3,
                          "min_hole_clearance": 0.25, "min_silk_clearance": 0.0},
                "track_widths": [0.0, 0.3, 0.5],
                "via_dimensions": [{"diameter": 0.0, "drill": 0.0}, {"diameter": 0.6, "drill": 0.3}],
            }
        },
        "meta": {"filename": PROJ + ".kicad_pro", "version": 1},
        "net_settings": {
            "classes": [
                {"name": "Default", "clearance": 0.2, "track_width": 0.3, "via_diameter": 0.6, "via_drill": 0.3,
                 "microvia_diameter": 0.3, "microvia_drill": 0.1, "diff_pair_width": 0.2, "diff_pair_gap": 0.25,
                 "wire_width": 6, "bus_width": 12, "line_style": 0, "schematic_color": "rgba(0, 0, 0, 0.000)",
                 "pcb_color": "rgba(0, 0, 0, 0.000)"},
                {"name": "Audio", "clearance": 0.3, "track_width": 0.4, "via_diameter": 0.6, "via_drill": 0.3,
                 "microvia_diameter": 0.3, "microvia_drill": 0.1, "diff_pair_width": 0.2, "diff_pair_gap": 0.25,
                 "wire_width": 6, "bus_width": 12, "line_style": 0, "schematic_color": "rgba(0, 0, 0, 0.000)",
                 "pcb_color": "rgba(0, 0, 0, 0.000)"},
                {"name": "Coil", "clearance": 0.25, "track_width": 0.3, "via_diameter": 0.6, "via_drill": 0.3,
                 "microvia_diameter": 0.3, "microvia_drill": 0.1, "diff_pair_width": 0.2, "diff_pair_gap": 0.25,
                 "wire_width": 6, "bus_width": 12, "line_style": 0, "schematic_color": "rgba(0, 0, 0, 0.000)",
                 "pcb_color": "rgba(0, 0, 0, 0.000)"},
            ],
            "meta": {"version": 3},
            "netclass_assignments": None,
            "netclass_patterns": [{"netclass": "Audio", "pattern": "/" + n} for n in audio]
                                 + [{"netclass": "Coil", "pattern": "/" + n} for n in coil],
        },
        "schematic": {"legacy_lib_dir": "", "legacy_lib_list": []},
        "sheets": [[ROOT_UUID, "Root"]],
        "text_variables": {},
    }
    open(os.path.join(OUT, PROJ + ".kicad_pro"), "w").write(json.dumps(pro, indent=2, ensure_ascii=False) + "\n")


def write_bom():
    from collections import OrderedDict
    groups = OrderedDict()
    for p in sorted(parts, key=lambda p: (p["sym"], p["value"], p["ref"])):
        if p["sym"].startswith("MountingHole"):
            continue
        lib, fp = p["fp"]
        key = (fp if p["sym"] in ("AudioConn",) else p["value"], fp, p["extra"].get("Tolerancja", ""), p["dnp"], p["extra"].get("LCSC", ""))
        groups.setdefault(key, []).append(p["ref"])

    def natkey(r):
        m = re.match(r"([A-Z]+)(\d+)", r)
        return (m.group(1), int(m.group(2)))

    lines = ["Ilość;Referencje;Wartość;Tolerancja;Obudowa;LCSC;Uwagi"]
    for (val, fp, tol, dnp, _lc), rs in sorted(groups.items(), key=lambda kv: natkey(sorted(kv[1], key=natkey)[0])):
        rs = sorted(rs, key=natkey)
        note = "NIE MONTOWAĆ (opcja)" if dnp else ""
        if fp.startswith("Relay"):
            note = "Omron G6K-2F-Y DC12"
        if fp.startswith("JST"):
            note = "JST B3B-XH-A + wtyk XHP-3 (IN1..IN4, OUT)"
        mp = next((pp["extra"].get("MPN") for pp in parts if pp["ref"] == rs[0]), None)
        if mp:
            note = mp
        if fp.startswith("C_"):
            note = "X7R" if "100n" in val else "X5R/X7R"
        if val.endswith("k") or val.endswith("R"):
            note = note or ("cienkowarstwowy, np. Vishay TNPW / Susumu RG" if tol == "0.1%" else "")
        lc = next((pp["extra"].get("LCSC", "") for pp in parts if pp["ref"] == rs[0]), "")
        lines.append(f"{len(rs) if not dnp else 0};{', '.join(rs)};{val};{tol};{fp};{lc};{note}")
    open(os.path.join(OUT, "BOM.csv"), "w", encoding="utf-8-sig").write("\n".join(lines) + "\n")


def write_lcsc(boards=2):
    """Plik do narzędzia BOM na lcsc.com: komplet do samodzielnego montażu (+ zapas, + złącza JST)."""
    import csv
    per = {}
    for p in parts:
        c = p["extra"].get("LCSC")
        if not c:
            continue
        d = per.setdefault(c, [p["extra"].get("MPN", ""), f"{p['value']} {p['fp'][1]}", []])
        d[2].append(p["ref"])
    extra = [("C144394", "B3B-XH-A(LF)(SN)", "JST XH 3p gniazdo proste do PCB (J1-J5)", ["J1", "J2", "J3", "J4", "J5"]),
             ("C144397", "B6B-XH-A(LF)(SN)", "JST XH 6p gniazdo do PCB (J6)", ["J6"]),
             ("C144402", "XHP-3", "JST XH 3p wtyk (obudowa kabla)", ["J1", "J2", "J3", "J4", "J5"]),
             ("C144405", "XHP-6", "JST XH 6p wtyk (obudowa kabla)", ["J6"]),
             ("C140573", "SXH-001T-P0.6", "JST XH pin do zaciskania, AWG 22-28", ["5x3 + 6 pinów"])]

    def natkey(r):
        m = re.match(r"([A-Z]+)(\d+)", r)
        return (m.group(1), int(m.group(2))) if m else (r, 0)

    rows = []
    for c, (mpn, desc, refs) in per.items():
        n = len(refs)
        spare = 2 if c == "C397192" else (1 if desc.split()[1].startswith("SOIC") else 5)
        rows.append([c, mpn, desc, ",".join(sorted(refs, key=natkey)), n, n * boards + spare])
    for c, mpn, desc, refs in extra:
        if c == "C140573":
            n, q = 21, 21 * boards + 10
        else:
            n = len(refs); q = n * boards + 1
        rows.append([c, mpn, desc, ",".join(refs), n, q])
    with open(os.path.join(OUT, "LCSC_zamowienie.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["LCSC Part Number", "Manufacturer Part Number", "Description", "Designator", "Qty per board", "Quantity"])
        w.writerows(rows)


def write_jlc():
    """BOM w formacie JLCPCB (tylko elementy SMD montowane automatycznie)."""
    import csv
    from collections import OrderedDict
    g = OrderedDict()
    for p in parts:
        if "LCSC" not in p["extra"]:
            continue
        k = (p["value"], p["fp"][1], p["extra"]["LCSC"])
        g.setdefault(k, []).append(p["ref"])
    with open(os.path.join(OUT, "JLCPCB_BOM.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for (val, fp, code), rs in g.items():
            w.writerow([val, ",".join(rs), fp, code])


if __name__ == "__main__":
    if not os.path.isdir(os.path.join(FPLIB, "Relay_SMD.pretty")):
        sys.exit("Ustaw KICAD_FOOTPRINT_DIR na klon https://github.com/KiCad/kicad-footprints (patrz tools/README.md)")
    os.makedirs(OUT, exist_ok=True)
    write_symlib()
    write_sch()
    write_pcb()
    write_pro()
    write_bom()
    write_jlc()
    write_lcsc()
    print("OK", len(parts), "elementów")
