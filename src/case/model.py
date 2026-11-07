"""Soloist 88 - obudowa (propozycja v0.1). Wymiary w mm.
Uklad osi: X w prawo (patrzac od przodu), Y do tylu, Z w gore. 0,0,0 = lewy przedni dolny rog dna aluminiowego."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pcb"))
from stepw import *

# ================================================================ parametry
T = 3.0          # aluminium
TS = 2.5         # stal nierdzewna oslony lamp
WOOD = 20.0      # MDF + fornir (boki), przod = 5 lico + 15 rama
W, D = 400.0, 460.0          # dno aluminiowe
H_CH = 100.0                 # wysokosc wnetrza czesci lampowej (dno->pokrywa)
Z_COV = T + H_CH             # 103 - spod pokrywy
Y_BOX = 310.0                # przednia scianka obudowy trafo (y 310..313)
Y_STEP = 307.0               # od tego miejsca boczne scianki sa wysokie
Z_LID = 153.0                # spod dachu obudowy trafo
TAB = 15.0                   # dlugosc wypustu
CL = 0.1                     # luz gniazda (na strone)
X_P1, X_P2 = 127.0, 270.0    # przegrody w obudowie trafo

ALU = (0.78, 0.80, 0.83); ALU2 = (0.70, 0.72, 0.76); SS = (0.86, 0.87, 0.88)
WOODC = (0.55, 0.36, 0.20); WOODF = (0.62, 0.43, 0.26)
REFC = (0.25, 0.45, 0.75); GLASS = (0.85, 0.75, 0.55); BLACK = (0.12, 0.12, 0.12); PCB = (0.10, 0.45, 0.20)
TRAFO = (0.30, 0.30, 0.32)

def tabs(centers, d):
    return [(c - TAB / 2, c + TAB / 2, d) for c in centers]
def slot(cu, cv, lu, lv):
    return rect(cu - lu / 2 - CL, cv - lv / 2 - CL, cu + lu / 2 + CL, cv + lv / 2 + CL)

# lampy
KT = [(50.0, 235.0), (120.0, 235.0), (280.0, 235.0), (350.0, 235.0)]
SMALL = [(48.0, 120.0, "V101_L EF86"), (122.0, 120.0, "V102_L E88CC"), (278.0, 120.0, "V102_R E88CC"), (352.0, 120.0, "V101_R EF86")]
# plytki (x0, y0, obrot180?)
BOARD_KANAL = {"L": (35.0, 90.0, False), "R": (265.0, 50.0, True)}   # wejscia przy zewnetrznych krawedziach
BOARDS_DNO = {"sterowanie": (150.0, 5.0), "zasilacz_siec": (150.0, 107.0), "zasilacz_hv": (150.0, 209.0)}
TRAFO_POS = {"OT_L": (65.0, 385.0, 120.0, 65.0), "TR1": (200.0, 385.0, 130.0, 65.0), "OT_R": (335.0, 385.0, 120.0, 65.0)}
OT_RAISE = 35.0      # TG podniesione na tulei - pod nimi profil z przewodami wejsciowymi
PROF = 20.0; PROF_T = 1.5; PROF_Y0 = 300.0   # profil stalowy 20x20x1.5, od Y 290 do tylnej scianki
PROF_X = [T, W - T - PROF]                 # lewa krawedz profilu L i P
RCA = [(T + PROF / 2, T + PROF / 2), (W - T - PROF / 2, T + PROF / 2)]   # (x, z) gniazd RCA w tylnej sciance
CORNER_POSTS = [(12.0, 12.0), (388.0, 12.0), (12.0, 295.0), (388.0, 295.0)]
FEET = [(35.0, 25.0), (365.0, 25.0), (45.0, 440.0), (355.0, 440.0)]
GL_X0, GL_Y0 = 82.0, 340.0     # plytka przelacznika glosnikow pod lewym TG: (bx, by) -> (GL_X0 + by, GL_Y0 + bx)
SPK_MAR = [(35, 100), (60, 100), (340, 100), (365, 100)]   # zaciski z Marantza (x, z) w tylnej sciance
SPK_OUT = [(35, 70), (60, 70), (340, 70), (365, 70)]       # zaciski do kolumn
TRIG_JACK = (245.0, 45.0)                                  # gniazdo jack 3,5 mm TRIGGER (izolowane)

# front: (x, z)
FR_BTN, FR_LED, FR_SEL, FR_VOL, FR_IR = (35.0, 48.0), (35.0, 80.0), (100.0, 53.0), (300.0, 53.0), (365.0, 53.0)
FR_DISP = [(165.0, 55.0), (235.0, 55.0)]

# oslona lamp - pret M4 (x,y) dla kanalu L; R = lustro
GUARD_RODS_KT = [(19.0, 198.0), (151.0, 198.0), (19.0, 272.0), (151.0, 272.0)]
GUARD_ROD_FRONT = (85.0, 120.0)
Z_G1 = Z_COV + T                 # 106 - spod dolnej ramki
Z_G2 = 165.0                     # spod srodkowej ramki
Z_G3 = 225.0                     # spod gornej ramki (+15 mm - miesci KT120 do 144 mm)

def mirror_x(p):
    return (W - p[0], p[1])

def board_mh(name):
    import boards
    b = getattr(boards, name)()
    return [(c.x, c.y) for c in b.comps if c.ref.startswith("MH")]

def kanal_mh():
    import boards
    b = boards.kanal()
    return [(c.x, c.y) for c in b.comps if c.ref.startswith("MH")]

def kanal_abs(side, lx, ly):
    x0, y0, rot = BOARD_KANAL[side]
    return (x0 + 100 - lx, y0 + 100 - ly) if rot else (x0 + lx, y0 + ly)

# ================================================================ czesci
parts = []

# ---------------- DNO
def dno():
    f = {"left": tabs([50, 160, 270, 380], -T), "right": tabs([50, 160, 270, 380], -T),
         "bottom": tabs([60, 200, 340], -T), "top": tabs([60, 200, 340], -T)}
    outer = edge_features(0, 0, W, D, f)
    H = []
    for x in (60, 200, 340):
        H.append(slot(x, Y_BOX + T / 2, TAB, T))                   # przednia scianka trafo
    for xp in (X_P1, X_P2):
        for y in (335, 385, 435):
            H.append(slot(xp + T / 2, y, T, TAB))                  # przegrody
    for (cx, cy) in KT:
        H += [circle(cx + 25 * math.cos(math.radians(15 * k)), cy + 25 * math.sin(math.radians(15 * k)), 3.5) for k in range(24)]
        nb = [k for k in KT if k != (cx, cy) and abs(k[1] - cy) < 1 and abs(k[0] - cx) < 100][0]
        for k in range(12):
            a = math.radians(30 * k)
            dxn = 1 if nb[0] > cx else -1
            if dxn * math.cos(a) > 0.5:
                continue
            vx, vy = cx + 36 * math.cos(a), cy + 36 * math.sin(a)
            if any(math.hypot(vx - (x0 + mx), vy - (y0 + my)) < 9 for name, (x0, y0) in BOARDS_DNO.items() for (mx, my) in board_mh(name)):
                continue
            H.append(circle(vx, vy, 6))
    for (x, y, dd, h) in TRAFO_POS.values():
        H.append(circle(x, y, 8.5))
    for name, (x0, y0) in BOARDS_DNO.items():
        H += [circle(x0 + mx, y0 + my, 3.5) for (mx, my) in board_mh(name)]
    H += [circle(px + PROF / 2, y, 4.5) for px in PROF_X for y in (330, 430)]          # mocowanie profili
    H += [circle(GL_X0 + my, GL_Y0 + mx, 3.5) for (mx, my) in board_mh("glosniki")]      # plytka glosnikow
    H += [circle(x, y, 4.5) for (x, y) in CORNER_POSTS]
    H += [circle(x, y, 5.0) for (x, y) in FEET]
    return prism("AL_dno_400x460x3", ALU2, outer, H, 0, T, "XY")
parts.append(dno())

# ---------------- SCIANKI BOCZNE (jedna czesc: nisko z przodu, wysoko przy trafo)
FING_FRONT = [(13, 28), (48, 63), (78, 93)]               # z (v) zakresy wypustow do sciany przedniej
FING_REAR = [(15, 30), (55, 70), (95, 110), (130, 145)]    # do sciany tylnej
BOXFRONT_TABS = [(25, 40), (70, 85), (115, 130)]                     # wypusty przedniej scianki trafo w scianki boczne
def side(name, x0):
    # lokalnie u=y, v=z
    P = [(T, T)]
    for (a, b) in [(c - TAB / 2, c + TAB / 2) for c in (50, 160, 270, 380)]:
        P += [(a, T), (a, 0), (b, 0), (b, T)]
    P.append((D - T, T))
    for (a, b) in FING_REAR:
        P += [(D - T, a), (D, a), (D, b), (D - T, b)]
    P.append((D - T, Z_LID))
    for (a, b) in sorted([(c - TAB / 2, c + TAB / 2) for c in (335, 385, 435)], reverse=True):
        P += [(b, Z_LID), (b, Z_LID + T), (a, Z_LID + T), (a, Z_LID)]
    P += [(Y_STEP, Z_LID), (Y_STEP, Z_COV), (T, Z_COV)]
    for (a, b) in sorted(FING_FRONT, reverse=True):
        P += [(T, b), (0, b), (0, a), (T, a)]
    H = [slot(Y_BOX + T / 2, (a + b) / 2, T, b - a) for (a, b) in BOXFRONT_TABS]
    H += [circle(y, 53, 4.5) for y in (60, 180, 290, 400)]       # mocowanie bokow drewnianych
    return prism(name, ALU, P, H, x0, x0 + T, "YZ")
parts.append(side("AL_bok_lewy", 0.0))
parts.append(side("AL_bok_prawy", W - T))

# ---------------- PRZEDNIA SCIANKA ALUMINIOWA (za frontem drewnianym)
def front_wall():
    f = {"bottom": tabs([60, 200, 340], T),
         "left": [(a, b, -T) for (a, b) in FING_FRONT], "right": [(a, b, -T) for (a, b) in FING_FRONT]}
    outer = edge_features(0, T, W, Z_COV, f)
    H = [circle(*FR_BTN, 22), circle(*FR_LED, 10), circle(*FR_SEL, 7.5), circle(*FR_VOL, 7.5), circle(*FR_IR, 12)]
    H += [rect(x - 12, z - 6, x + 12, z + 6) for (x, z) in FR_DISP]
    H += [circle(x, z, 4.5) for (x, z) in ((60, 20), (340, 20), (200, 20), (200, 90))]
    return prism("AL_przod_wewn", ALU, outer, H, 0, T, "XZ")
parts.append(front_wall())

# ---------------- OBUDOWA TRAFO: scianka przednia
PART_END_TABS = [(30, 45), (70, 85), (110, 125)]
def box_front():
    f = {"bottom": tabs([60, 200, 340], T), "top": tabs([60, 200, 340], T),
         "left": [(a, b, T) for (a, b) in BOXFRONT_TABS], "right": [(a, b, T) for (a, b) in BOXFRONT_TABS]}
    P = edge_features(T, T, W - T, Z_LID, f)
    # wyciecia na profile w dolnych rogach (x T..T+PROF+0.5, z T..T+PROF+0.5)
    nb = T + PROF + 0.5
    Q = []
    for (u, v) in P:
        if abs(v - T) < 1e-6 and abs(u - T) < 1e-6:
            Q += [(T, nb), (T + PROF + 0.5, nb), (T + PROF + 0.5, T)]
        elif abs(v - T) < 1e-6 and abs(u - (W - T)) < 1e-6:
            Q += [(W - T - PROF - 0.5, T), (W - T - PROF - 0.5, nb), (W - T, nb)]
        else:
            Q.append((u, v))
    H = [slot(xp + T / 2, (a + b) / 2, T, b - a) for xp in (X_P1, X_P2) for (a, b) in PART_END_TABS]
    H += [circle(x, 40, 16) for x in (65, 185, 215, 335)]          # przepusty przewodow (gumowe)
    return prism("AL_trafo_przod", ALU, Q, H, Y_BOX, Y_BOX + T, "XZ")
parts.append(box_front())

def box_rear():
    f = {"bottom": tabs([60, 200, 340], T), "top": tabs([60, 200, 340], T),
         "left": [(a, b, -T) for (a, b) in FING_REAR], "right": [(a, b, -T) for (a, b) in FING_REAR]}
    outer = edge_features(0, T, W, Z_LID, f)
    H = [slot(xp + T / 2, (a + b) / 2, T, b - a) for xp in (X_P1, X_P2) for (a, b) in PART_END_TABS]
    H.append(rect(200 - 13.75, 45 - 16, 200 + 13.75, 45 + 16))      # gniazdo IEC C14 z bezpiecznikiem
    H += [circle(x, z, 9) for (x, z) in SPK_MAR + SPK_OUT]          # zaciski glosnikowe: gora z Marantza, dol do kolumn
    H.append(circle(TRIG_JACK[0], TRIG_JACK[1], 6))                   # gniazdo TRIGGER 3,5 mm (otwor 6 mm, wersja panelowa)
    H.append(circle(200, 110, 4.5))                                   # zacisk PE / masa
    H += [circle(x, z, 10) for (x, z) in RCA]                         # gniazda RCA (izolowane) w osi profili
    return prism("AL_trafo_tyl", ALU, outer, H, D - T, D, "XZ")
parts.append(box_rear())

def partition(name, x0):
    f = {"bottom": tabs([335, 385, 435], T), "top": tabs([335, 385, 435], T),
         "left": [(a, b, T) for (a, b) in PART_END_TABS], "right": [(a, b, T) for (a, b) in PART_END_TABS]}
    outer = edge_features(Y_BOX + T, T, D - T, Z_LID, f)
    H = [circle(y, 25, 16) for y in (360, 410)]
    return prism(name, ALU2, outer, H, x0, x0 + T, "YZ")
parts.append(partition("AL_trafo_przegroda_L", X_P1))
parts.append(partition("AL_trafo_przegroda_P", X_P2))

def lid():
    f = {"left": tabs([335, 385, 435], -T), "right": tabs([335, 385, 435], -T), "top": tabs([60, 200, 340], -T)}
    outer = edge_features(0, Y_STEP, W, D, f)
    H = [slot(x, Y_BOX + T / 2, TAB, T) for x in (60, 200, 340)]
    H += [slot(xp + T / 2, y, T, TAB) for xp in (X_P1, X_P2) for y in (335, 385, 435)]
    for (xa, xb) in ((15, 115), (142, 258), (285, 385)):
        nx = int((xb - xa) // 12)
        for i in range(nx + 1):
            for j in range(10):
                x = xa + (xb - xa - nx * 12) / 2 + i * 12
                y = 330 + j * 12
                if abs(y - 345) < 9 or abs(y - 425) < 9:
                    pass
                H.append(circle(x, y, 6))
    return prism("AL_trafo_dach", ALU, outer, H, Z_LID, Z_LID + T, "XY")
parts.append(lid())

# ---------------- POKRYWA GORNA (zdejmowana, 4 wkrety w rogach)
def cover():
    outer = rect(0, 0, W, Y_STEP)
    H = [circle(x, y, 4.5) for (x, y) in CORNER_POSTS]
    H += [circle(x, y, 60) for (x, y) in KT]
    H += [circle(x, y, 27) for (x, y, n) in SMALL]
    for side_ in ("L", "R"):
        H += [circle(*kanal_abs(side_, mx, my), 3.4) for (mx, my) in kanal_mh()]
    rods = GUARD_RODS_KT + [GUARD_ROD_FRONT]
    H += [circle(x, y, 4.5) for (x, y) in rods] + [circle(*mirror_x(p), 4.5) for p in rods]
    for i in range(7):
        for j in range(14):
            x, y = 164 + i * 12, 130 + j * 12
            H.append(circle(x, y, 6))
    return prism("AL_pokrywa_gorna", ALU, outer, H, Z_COV, Z_COV + T, "XY")
parts.append(cover())

# ---------------- OSLONA LAMP (stal nierdzewna)
def guard_parts(side_):
    m = (lambda p: p) if side_ == "L" else mirror_x
    tag = "L" if side_ == "L" else "P"
    out = []
    def pts(lst): return [m(p) for p in lst]
    kts = pts(KT[:2])
    small = pts([(48.0, 120.0), (122.0, 120.0)])
    rods = pts(GUARD_RODS_KT)
    xs = sorted([m((11.0, 0))[0], m((159.0, 0))[0]])
    o1 = rrect(xs[0], 98, xs[1], 280, 10)
    H1 = [circle(x, y, 62) for (x, y) in kts] + [circle(x, y, 30) for (x, y) in small]
    H1 += [circle(x, y, 4.5) for (x, y) in rods + [m(GUARD_ROD_FRONT)]]
    out.append(prism("SS_oslona_%s_dolna" % tag, SS, o1, H1, Z_G1, Z_G1 + TS, "XY"))
    o2 = rrect(xs[0], 190, xs[1], 280, 10)
    H2 = [circle(x, y, 62) for (x, y) in kts] + [circle(x, y, 4.5) for (x, y) in rods]
    out.append(prism("SS_oslona_%s_srodkowa" % tag, SS, o2, H2, Z_G2, Z_G2 + TS, "XY"))
    out.append(prism("SS_oslona_%s_gorna" % tag, SS, o2, H2, Z_G3, Z_G3 + TS, "XY"))
    for k, (x, y) in enumerate(rods):
        out.append(cyl("SS_tulejka_%s%d_a" % (tag, k + 1), SS, x, y, 10, Z_G1 + TS, Z_G2, ref=False, hole=4.4))
        out.append(cyl("SS_tulejka_%s%d_b" % (tag, k + 1), SS, x, y, 10, Z_G2 + TS, Z_G3, ref=False, hole=4.4))
    return out
parts += guard_parts("L") + guard_parts("R")

# ---------------- PROFILE STALOWE na przewody wejsciowe (pod podniesionymi TG)
STEEL = (0.18, 0.18, 0.2)
for k, px in enumerate(PROF_X):
    tag = "L" if k == 0 else "P"
    outer = rect(px, T, px + PROF, T + PROF)
    inner = rect(px + PROF_T, T + PROF_T, px + PROF - PROF_T, T + PROF - PROF_T)
    parts.append(prism("ST_profil_20x20x1.5_%s_dl%d" % (tag, int(D - T - PROF_Y0)), STEEL, outer, [inner], PROF_Y0, D - T, "XZ"))

# ---------------- EKRAN NAD PLYTKA STEROWANIA (aluminium, na tulejach M3 30 mm)
def screen():
    x0, y0 = BOARDS_DNO["sterowanie"]
    o = rect(x0 - 2, y0 + 0.5, x0 + 102, y0 + 101)
    H = [circle(x0 + mx, y0 + my, 3.4) for (mx, my) in board_mh("sterowanie")]
    H += [rect(x0 + 5, y0 + 20, x0 + 30, y0 + 30)]                     # przepust tasm/przewodow
    return prism("AL_ekran_sterowania", ALU2, o, H, 47, 47 + T, "XY")
parts.append(screen())

# ---------------- DREWNO
def wood_front():
    X0, X1 = -WOOD, W + WOOD
    skin_h = [circle(*FR_BTN, 16.2), circle(*FR_LED, 5.2), circle(*FR_SEL, 9), circle(*FR_VOL, 9), circle(*FR_IR, 6)]
    skin_h += [circle(x, z, 33) for (x, z) in FR_DISP]
    frame_h = [circle(*FR_BTN, 26), circle(*FR_LED, 12), circle(*FR_SEL, 30), circle(*FR_VOL, 30), circle(*FR_IR, 14)]
    frame_h += [circle(x, z, 40) for (x, z) in FR_DISP]
    return [prism("DREWNO_front_lico_5mm", WOODF, rect(X0, 0, X1, Z_COV + T), skin_h, -WOOD, -WOOD + 5, "XZ"),
            prism("DREWNO_front_rama_15mm", WOODC, rect(X0, 0, X1, Z_COV + T), frame_h, -WOOD + 5, 0, "XZ")]
parts += wood_front()
parts.append(prism("DREWNO_bok_lewy", WOODF, rect(0, 0, D, Z_COV + T), [], -WOOD, 0, "YZ"))
parts.append(prism("DREWNO_bok_prawy", WOODF, rect(0, 0, D, Z_COV + T), [], W, W + WOOD, "YZ"))

# ================================================================ elementy odniesienia (REF)
ref = []
for (x, y) in KT:
    ref.append(cyl("REF_podstawka_KT88", (0.92, 0.90, 0.85), x, y, 45, 50, 62))
    ref.append(cyl("REF_KT88_cokol", BLACK, x, y, 40, 62, 88))
    ref.append(cyl("REF_KT88_banka", GLASS, x, y, 52, 88, 195))
    for s in (-1, 1):
        ref.append(cyl("REF_szpilka_M3", BLACK, x + 25 * s, y, 3, T, 50, n=8))
for (x, y, n) in SMALL:
    ref.append(cyl("REF_" + n.replace(" ", "_"), GLASS, x, y, 22, 92, 150))
for side_, (x0, y0, rot) in BOARD_KANAL.items():
    ref.append(box("REF_plytka_kanal_" + side_, PCB, x0, y0, 88, x0 + 100, y0 + 100, 89.6))
for name, (x0, y0) in BOARDS_DNO.items():
    ref.append(box("REF_plytka_" + name, PCB, x0, y0, 13, x0 + 100, y0 + 100, 14.6))
for k, (cx, cy) in enumerate([(16, 84), (47, 84), (16, 53), (47, 53)]):
    x0, y0 = BOARDS_DNO["zasilacz_hv"]
    ref.append(cyl("REF_C_snapin_%d" % k, BLACK, x0 + cx, y0 + cy, 30, 14.6, 64.6))
for name, (x, y, dd, h) in TRAFO_POS.items():
    z0 = T + 3 + (OT_RAISE if name.startswith("OT") else 0)
    ref.append(cyl("REF_" + name, TRAFO, x, y, dd, z0, z0 + h, hole=20))
    if name.startswith("OT"):
        ref.append(cyl("REF_tuleja_TG_%dmm" % OT_RAISE, BLACK, x, y, 30, T, T + 3 + OT_RAISE, hole=8.5))
for (x, z) in RCA:
    ref.append(cyl("REF_gniazdo_RCA", (0.85, 0.7, 0.2), x, z, 9, D, D + 18, axis="Y"))
x0, y0 = BOARDS_DNO["sterowanie"]
for (mx, my) in board_mh("sterowanie"):
    if True:
        ref.append(cyl("REF_tulejka_M3_ekran", BLACK, x0 + mx, y0 + my, 5.5, 14.6, 47, n=6))
ref.append(cyl("REF_dlawik_L1", (0.35, 0.25, 0.25), 200, 385, 105, T + 3 + 65 + 3, T + 3 + 65 + 3 + 55, hole=20))
for (x, y) in CORNER_POSTS:
    ref.append(cyl("REF_tulejka_M4_100mm", BLACK, x, y, 7, T, Z_COV, n=6))
for (x, y) in FEET:
    ref.append(cyl("REF_noga", BLACK, x, y, 40, -15, 0))
for (x, z) in (FR_SEL, FR_VOL):
    ref.append(cyl("REF_galka", (0.6, 0.6, 0.62), x, z, 32, -WOOD - 22, -WOOD, axis="Y"))
ref.append(cyl("REF_przycisk", (0.6, 0.6, 0.62), FR_BTN[0], FR_BTN[1], 16, -WOOD - 3, -WOOD + 5, axis="Y"))
ref.append(cyl("REF_LED_2kol", (0.9, 0.3, 0.2), FR_LED[0], FR_LED[1], 5, -WOOD - 2, -WOOD + 5, axis="Y"))
for (x, z) in FR_DISP:
    ref.append(cyl("REF_wyswietlacz_okragly", BLACK, x, z, 38, -WOOD + 5, -WOOD + 9, axis="Y"))
for p in GUARD_RODS_KT + [GUARD_ROD_FRONT]:
    for q in (p, mirror_x(p)):
        top = Z_G3 + TS if p != GUARD_ROD_FRONT else Z_G1 + TS
        ref.append(cyl("REF_pret_M4", BLACK, q[0], q[1], 4, Z_COV - 6, top + 6, n=8))
        ref.append(cyl("REF_nakretka_kolpakowa_M4", SS, q[0], q[1], 7, top, top + 8, n=12))
for k, (x, z) in enumerate(SPK_MAR + SPK_OUT):
    ref.append(cyl("REF_zacisk_glosnikowy", (0.8, 0.1, 0.1) if k % 2 == 0 else BLACK, x, z, 12, D, D + 22, axis="Y"))
ref.append(cyl("REF_gniazdo_trigger_3.5mm", BLACK, TRIG_JACK[0], TRIG_JACK[1], 8, D - T - 12, D + 8, axis="Y"))
ref.append(box("REF_plytka_glosniki", PCB, GL_X0, GL_Y0, 9, GL_X0 + 42, GL_Y0 + 100, 10.6))
for cxb in (30, 72):
    ref.append(box("REF_przekaznik_G2RL", BLACK, GL_X0 + 28 - 6.25, GL_Y0 + cxb - 14.4, 10.6, GL_X0 + 28 + 6.25, GL_Y0 + cxb + 14.4, 26.3))
ref.append(box("REF_gniazdo_IEC", BLACK, 200 - 15, D, 45 - 17, 200 + 15, D + 4, 45 + 17))  # placeholder (orientacja XY)
for S in ref:
    S.ref = True

if __name__ == "__main__":
    out = os.path.dirname(os.path.abspath(__file__))
    bad = 0
    for S in parts + ref:
        b = check_closed(S); v = volume(S)
        if b or v <= 0:
            print("PROBLEM", S.name, b, v); bad += 1
    print("parts", len(parts), "ref", len(ref), "problems", bad)
    write_step(os.path.join(out, "Soloist88_obudowa.step"), parts, "Soloist88_obudowa")
    write_step(os.path.join(out, "Soloist88_obudowa_z_elementami.step"), parts + ref, "Soloist88_obudowa_z_elementami")
