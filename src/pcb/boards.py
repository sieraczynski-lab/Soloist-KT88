from pcbgen import Board, F

# =====================================================================================
# 1. KANAL  (one channel, build twice: L = 1xx, R = 2xx -> designators here use 1xx)
# =====================================================================================
KFIX = {
    "V101": (13, 30, "T", "NOVAL"), "V102": (87, 30, "T", "NOVAL"),
    "C130": (47, 19, "B", "SNAP35"),
    "R112": (47, 44, "B", "R7"), "R111": (47, 53.5, "B", "R7"),
    "C105": (47, 64.5, "B", "C27"), "C106": (47, 77.5, "B", "C27"),
    "MH101": (4.5, 4.5, "", "MH"), "MH102": (95.5, 4.5, "", "MH"), "MH103": (4.5, 95.5, "", "MH"),
    "MH104": (95.5, 95.5, "", "MH"), "MH105": (22, 72, "", "MH"),
}
KAUTO = [  # placed in this order: ref, (pref x, pref y, side, footprint options)
    ("R102", (21, 42, "T", ["R05V", "R05"])), ("R108", (76, 42, "T", ["R05V", "R05"])), ("R110", (86, 46, "T", ["R05", "R05V"])),
    ("C131", (84, 88, "B", ["CP18"])),
    ("Q101", (72, 30, "B", ["TO220S"])),
    ("R113", (70, 18, "T", ["R05V", "R05"])), ("D105", (72, 10, "B", ["DO41", "DO41V"])), ("P101", (66, 6, "B", ["TRIM"])),
    ("R114", (74, 4, "T", ["R05", "R05V"])),
    ("C102", (27, 30, "B", ["C15V", "C15"])), ("C101", (13, 52, "B", ["C10"])),
    ("C104", (10, 78, "B", ["C22V", "C22"])),
    ("R130", (90, 60, "B", ["R2V", "R2"])), ("R131", (30, 46, "T", ["R1", "R1V"])),
    ("R103", (27, 42, "T", ["R05V", "R05"])), ("R104", (27, 52, "T", ["R05", "R05V"])), ("C103", (27, 58, "B", ["C5"])),
    ("R101", (12, 62, "T", ["R05V", "R05"])), ("R105", (32, 8, "T", ["R1", "R1V"])), ("R106", (28, 14, "T", ["R05", "R05V"])),
    ("R107", (28, 20, "T", ["R05", "R05V"])), ("R109", (68, 46, "T", ["R05", "R05V"])),
    ("R128", (10, 10, "T", ["R05V", "R05"])), ("C107", (18, 6, "B", ["C5"])),
    ("R129", (60, 4, "T", ["R05", "R05V"])), ("C108", (56, 8, "B", ["C5"])),
    ("R115", (70, 62, "T", ["R05V", "R05"])), ("P102", (78, 60, "B", ["TRIM"])), ("R119", (76, 68, "T", ["R05V", "R05"])),
    ("R121", (82, 68, "T", ["R05V", "R05"])),
    ("R116", (70, 80, "T", ["R05V", "R05"])), ("P103", (78, 76, "B", ["TRIM"])), ("R120", (76, 84, "T", ["R05V", "R05"])),
    ("R122", (82, 82, "T", ["R05V", "R05"])),
    ("J101", (3.5, 50, "", ["PAD"])), ("J102", (3.5, 57, "", ["PAD"])), ("J103", (3.5, 64, "", ["PAD"])),
    ("J109", (36, 97, "", ["PAD"])), ("J110", (43, 97, "", ["PAD"])),
    ("J104", (96.5, 50, "", ["PADL"])), ("J105", (96.5, 57, "", ["PADL"])), ("J106", (96.5, 64, "", ["PAD"])),
    ("J107", (96.5, 71, "", ["PAD"])), ("J108", (96.5, 78, "", ["PAD"])),
    ("TP101", (36, 50, "", ["TP"])), ("TP102", (58, 50, "", ["TP"])), ("TP103", (66, 24, "", ["TP"])),
    ("TP104", (66, 52, "", ["TP"])), ("TP105", (66, 40, "", ["TP"])), ("TP106", (64, 62, "", ["TP"])),
    ("TP107", (64, 80, "", ["TP"])), ("TP108", (24, 6, "", ["TP"])), ("TP109", (22, 58, "", ["TP"])),
]
KPOS = dict(KFIX)
KPOS.update({r: (p[0], p[1], p[2], p[3][0]) for r, p in KAUTO})

def kanal():
    b = Board("kanal", "Soloist 88 - plytka kanalu (x2)", 100, 100)
    g_in, g_ef, g_ltp, g_ccs, g_out, g_bias, g_pwr, g_con, g_tp, g_mh = (
        "WEJSCIE", "EF86", "LTP E88CC", "ZRODLO PRADOWE", "SPRZEGANIE DO KT88", "BIAS KT88", "ZASILANIE KANALU",
        "ZLACZA", "PUNKTY POMIAROWE", "OTWORY")
    def A(ref, value, symbol, nets, group, note=""):
        x, y, side, fk = KPOS[ref]
        b.add(ref, value, symbol, F[fk], x, y, nets, group, note, side or "T")
    A("J101", "IN", "PAD", ["IN"], g_con, "wejscie sygnalu (ekranowany, oplot do J102)")
    A("J102", "GND_IN", "PAD", ["GND"], g_con, "masa wejscia")
    A("J103", "FB", "PAD", ["FB"], g_con, "sprzezenie zwrotne z wyjscia 4 ohm")
    A("J104", "B+3", "PAD", ["B+3"], g_con, "465 V z plytki zasilacza HV")
    A("J105", "GND", "PAD", ["GND"], g_con, "masa zasilania - przewod do gwiazdy")
    A("J106", "-78V", "PAD", ["VBIAS"], g_con, "szyna biasu")
    A("J107", "G1_V103", "PAD", ["GRID_T"], g_con, "do R117 przy podstawce V103")
    A("J108", "G1_V104", "PAD", ["GRID_B"], g_con, "do R118 przy podstawce V104")
    A("J109", "HTR_A", "PAD", ["HTR_A"], g_con, "zarzenie 6,3 V")
    A("J110", "HTR_B", "PAD", ["HTR_B"], g_con, "zarzenie 6,3 V")
    A("C101", "47n/250V", "C", ["IN", "IN2"], g_in)
    A("R101", "220k", "R", ["IN2", "GND"], g_in)
    A("R102", "1k", "R", ["IN2", "G1_EF"], g_in, "przy podstawce, pin 9")
    A("V101", "EF86", "EF86",
      {"9": "G1_EF", "8": "K_EF", "3": "K_EF", "2": "K_EF", "7": "K_EF", "6": "A_EF", "1": "G2_EF", "4": "HTR_A", "5": "HTR_B"}, g_ef,
      "montaz antymikrofonowy; pin 2,7 ekran do katody")
    A("R103", "330R", "R", ["K_EF", "GND"], g_ef)
    A("R104", "27k*", "R", ["K_EF", "FB"], g_ef, "dobor 22-33k")
    A("C103", "120p*", "C", ["K_EF", "FB"], g_ef, "mika/C0G 500V, dobor 68-220p")
    A("R105", "100k 1W", "R", ["B+1", "A_EF"], g_ef)
    A("R106", "470k", "R", ["B+1", "G2_EF"], g_ef)
    A("C102", "47n/400V", "C", ["G2_EF", "K_EF"], g_ef)
    A("R107", "1M5", "R", ["G2_EF", "GND"], g_ef)
    A("R128", "4k7 (opcja)", "R", ["A_EF", "STEP"], g_ef, "opcja: siec schodkowa")
    A("C107", "33p (opcja)", "C", ["STEP", "GND"], g_ef, "opcja: siec schodkowa")
    A("V102", "E88CC", "E88CC",
      {"2": "G_A", "1": "ANODE_A", "3": "TAIL", "9": "GND", "7": "G_B", "6": "ANODE_B", "8": "TAIL", "4": "HTR_A", "5": "HTR_B"}, g_ltp,
      "E88CC/6922/6N23P-EV; wariant B: 6N6P")
    A("R108", "1k", "R", ["A_EF", "G_A"], g_ltp, "przy podstawce, pin 2")
    A("R109", "1M", "R", ["A_EF", "N_GB"], g_ltp)
    A("R110", "1k", "R", ["G_B", "N_GB"], g_ltp, "przy podstawce, pin 7")
    A("C104", "470n/400V", "C", ["N_GB", "GND"], g_ltp)
    A("R111", "27k 5W", "R", ["B+2", "ANODE_A"], g_ltp, "para 1%; pola pod 7W (wariant B 12k)")
    A("R112", "27k 5W", "R", ["B+2", "ANODE_B"], g_ltp, "para 1%; pola pod 7W (wariant B 12k)")
    A("R129", "1M2 (opcja)", "R", ["A_EF", "CC_MID"], g_ltp, "opcja: korekcja fazy")
    A("C108", "2p7 (opcja)", "C", ["CC_MID", "ANODE_B"], g_ltp, "opcja: korekcja fazy")
    A("Q101", "DN2540N5", "DN2540", {"1": "Q_G", "2": "TAIL", "3": "Q_S"}, g_ccs, "maly radiator nasuwany ok. 20 K/W (6N6P: wiekszy)")
    A("R113", "1k", "R", ["Q_G", "GND"], g_ccs, "przy bramce Q101")
    A("D105", "1N4742A 12V", "ZENER", {"1": "Q_S", "2": "Q_G"}, g_ccs, "katoda do zrodla")
    A("P101", "200R", "POT", {"1": "Q_S", "2": "RS_MID", "3": "RS_MID"}, g_ccs, "prad ogona 14 mA")
    A("R114", "100R", "R", ["RS_MID", "GND"], g_ccs)
    A("C105", "0,47u/630V", "C", ["GRID_T", "ANODE_B"], g_out, "MKP 630V, obudowa raster 27,5 mm; wiekszy (osiowy) - poza plytka na przewodach")
    A("C106", "0,47u/630V", "C", ["GRID_B", "ANODE_A"], g_out, "MKP 630V, obudowa raster 27,5 mm; wiekszy (osiowy) - poza plytka na przewodach")
    A("R115", "100k", "R", ["BIAS_T", "GRID_T"], g_bias)
    A("R116", "100k", "R", ["BIAS_B", "GRID_B"], g_bias)
    A("R119", "27k", "R", ["VBIAS", "BIAS_T"], g_bias)
    A("P102", "50k", "POT", {"1": "BIAS_T", "2": "BMID_T", "3": "BMID_T"}, g_bias, "wieloobrotowy; przed startem na max")
    A("R121", "27k", "R", ["BMID_T", "GND"], g_bias)
    A("R120", "27k", "R", ["VBIAS", "BIAS_B"], g_bias)
    A("P103", "50k", "POT", {"1": "BIAS_B", "2": "BMID_B", "3": "BMID_B"}, g_bias, "wieloobrotowy; przed startem na max")
    A("R122", "27k", "R", ["BMID_B", "GND"], g_bias)
    A("R130", "330R 2W", "R", ["B+3", "B+2"], g_pwr)
    A("C130", "220u/550V", "CP", ["B+2", "GND"], g_pwr, "snap-in D35")
    A("R131", "68k 1W", "R", ["B+2", "B+1"], g_pwr)
    A("C131", "47u/500V", "CP", ["B+1", "GND"], g_pwr)
    for ref, net in (("TP101", "B+1"), ("TP102", "B+2"), ("TP103", "TAIL"), ("TP104", "ANODE_A"), ("TP105", "ANODE_B"),
                     ("TP106", "BIAS_T"), ("TP107", "BIAS_B"), ("TP108", "A_EF"), ("TP109", "K_EF")):
        A(ref, net, "TP", [net], g_tp)
    for r in ("MH101", "MH102", "MH103", "MH104", "MH105"):
        A(r, "M3", None, {}, g_mh)
    Board.VOLT = VOLT["kanal"]
    failed = b.autoplace([r for r, p in KAUTO], dict(KAUTO), list(KFIX))
    b.failed = failed
    b.zones = []
    b.texts = [(32, 74.5, "SOLOIST 88 KANAL L/R", 1.2)]
    return b


# =====================================================================================
# helper
# =====================================================================================
def _build(name, title, w, h, fixed, auto, comps, volt):
    """comps: list of (ref, value, symbol, nets, group, note). fixed/auto give positions."""
    b = Board(name, title, w, h)
    pos = dict(fixed)
    pos.update({r: (p[0], p[1], p[2], p[3][0]) for r, p in auto})
    for (ref, value, symbol, nets, group, note) in comps:
        x, y, side, fk = pos[ref]
        b.add(ref, value, symbol, F[fk], x, y, nets, group, note, side or "T")
    Board.VOLT = volt
    b.failed = b.autoplace([r for r, p in auto], dict(auto), list(fixed))
    return b


# =====================================================================================
# 2a. ZASILACZ - SIEC 230 V, BIAS, ZARZENIE
# =====================================================================================
def zasilacz_siec():
    g_m, g_b, g_h, g_r, g_c, g_mh = "SIEC 230 V", "BIAS -78 V", "ZARZENIE", "CEWKI K1/K2", "ZLACZA", "OTWORY"
    comps = [
        ("J1", "SIEC", "CONN_2", ["L_SW", "N_SW"], g_m, "zlacze srubowe: 1 L (po F1 w gniezdzie IEC i SW1), 2 N"),
        ("J3", "TR2", "CONN_2", ["L_TR2", "N_SW"], g_m, "zlacze srubowe: zasilanie czuwania PS1 (Mean Well IRM-15-12), 1 L (za F2), 2 N"),
        ("F2", "T500mA 250V", "FUSE", ["L_TR2", "L_SW"], g_m, "bezpiecznik PS1 (IRM-15-12), zwloczny 5x20 - sprawdz zalecenie w karcie modulu"),
        ("J38", "S1_HT", "CONN_2", ["HT_TR", "HT_F"], g_m, "zlacze srubowe 7,62 mm min. 400 V: 1 z TR1 S1, 2 do plytki HV J7"),
        ("F3", "T1A 500V", "FUSE", ["HT_TR", "HT_F"], g_m, "bezpiecznik anodowy w uzwojeniu S1; napiecie znamionowe >= 400 V AC; oprawka 5x20 lub 6,3x32"),
        ("K1", "G2RL-2-DC12", "RELAY_G2RL", {"1": "+12V", "8": "RLY1", "3": "L_SW", "6": "L_SW", "4": "L_K1", "5": "L_K1", "2": None, "7": None}, g_m, "siec; Omron G2RL-2 12 V, 2 styki rownolegle (LCSC C61458)"),
        ("K2", "G2RL-2-DC12", "RELAY_G2RL", {"1": "+12V", "8": "RLY2", "3": "L_K1", "6": "L_K1", "4": "L_TR", "5": "L_TR", "2": None, "7": None}, g_m, "bocznik R_SS; Omron G2RL-2, 2 styki rownolegle"),
        ("R1", "47R 10W", "R", ["L_K1", "L_TR"], g_m, "R_SS, rezystor cementowy"),
        ("J5", "TR1_PRI", "CONN_2", ["L_TR", "N_SW"], g_m, "zlacze srubowe: uzwojenie pierwotne TR1, 1 L, 2 N"),
        ("J19", "BIAS_AC", "CONN_2", ["B_AC1", "B_AC2"], g_b, "zlacze srubowe: S4 65 V"),
        ("D5", "1N4007", "D", {"1": "GND", "2": "B_AC1"}, g_b, ""),
        ("D6", "1N4007", "D", {"1": "GND", "2": "B_AC2"}, g_b, ""),
        ("D7", "1N4007", "D", {"1": "B_AC1", "2": "VB_RAW"}, g_b, ""),
        ("D8", "1N4007", "D", {"1": "B_AC2", "2": "VB_RAW"}, g_b, ""),
        ("C141", "100u/160V", "CP", ["GND", "VB_RAW"], g_b, "+ do masy"),
        ("R142", "1k 1W", "R", ["VB_RAW", "VBIAS"], g_b, "1k (bylo 1k5): szyna ok. -80 V przy obciazeniu ok. 7 mA (z korekta biasu)"),
        ("C142", "100u/160V", "CP", ["GND", "VBIAS"], g_b, "+ do masy"),
        ("J21", "-78V", "CONN_3", ["VBIAS", "VBIAS", "VBIAS"], g_b, "zlacze srubowe: 1 kanal L, 2 kanal R, 3 sterowanie J5"),
        ("J24", "H2", "CONN_2", ["H2_A", "H2_B"], g_h, "zlacze srubowe: S2 6,3 V/7 A - tylko odczep, przewody KT88 poza plytka"),
        ("R11", "100R 1W", "R", ["H2_A", "GND"], g_h, "sztuczny srodek"),
        ("R12", "100R 1W", "R", ["H2_B", "GND"], g_h, ""),
        ("J26", "H3_IN", "CONN_2", ["H3_A", "H3_B"], g_h, "zlacze srubowe: S3 6,3 V/3 A"),
        ("R13", "100R 1W", "R", ["H3_A", "HTR_ELEV"], g_h, ""),
        ("R14", "100R 1W", "R", ["HTR_ELEV", "H3_B"], g_h, ""),
        ("J28", "H3_KAN_L", "CONN_2", ["H3_A", "H3_B"], g_h, "zlacze srubowe: zarzenie kanalu L"),
        ("J30", "H3_KAN_R", "CONN_2", ["H3_A", "H3_B"], g_h, "zlacze srubowe: zarzenie kanalu R"),
        ("J32", "RELAY_A", "CONN_3", ["+12V", "RLY1", "RLY2"], g_r, "z plytki sterowania (J2 piny 1,2,3)"),
        ("D9", "1N4148", "D", {"1": "+12V", "2": "RLY1"}, g_r, ""),
        ("D10", "1N4148", "D", {"1": "+12V", "2": "RLY2"}, g_r, ""),
        ("J34", "Z_HV", "CONN_2", ["HTR_ELEV", "GND"], g_c, "zlacze srubowe: 1 +42 V z plytki HV J36, 2 GND z plytki HV J37 (gwiazda)"),
    ] + [("MH%d" % k, "M3", None, {}, g_mh, "") for k in (1, 2, 3, 4)]
    fixed = {"K1": (25, 12, "T", "G2RL"), "K2": (25, 30, "T", "G2RL"), "R1": (64, 21, "T", "R10V"),
             "MH1": (4.5, 4.5, "", "MH"), "MH2": (95.5, 4.5, "", "MH"), "MH3": (4.5, 95.5, "", "MH"), "MH4": (95.5, 95.5, "", "MH")}
    fixed["R1"] = (52, 45, "T", "R10")
    auto = [
        ("J1", (5, 18, "", ["TB2V"])), ("J3", (5, 37, "", ["TB2V"])),
        ("J5", (95, 18, "", ["TB2V"])),
        ("F2", (66, 9, "T", ["FUSE"])), ("F3", (66, 26, "T", ["FUSE2"])),
        ("J38", (94.5, 38, "", ["TB762_2V"])),
        ("J19", (5, 64, "", ["TB2V"])),
        ("D5", (14, 62, "T", ["DO41V", "DO41"])), ("D6", (20, 62, "T", ["DO41V", "DO41"])),
        ("D7", (26, 62, "T", ["DO41V", "DO41"])), ("D8", (32, 62, "T", ["DO41V", "DO41"])),
        ("C141", (42, 62, "T", ["CP12"])), ("R142", (52, 62, "T", ["R1V", "R1"])), ("C142", (62, 62, "T", ["CP12"])),
        ("J21", (78, 65, "", ["TB3V"])),
        ("J24", (5, 84, "", ["TB2V"])), ("R11", (14, 84, "T", ["R1V", "R1"])), ("R12", (20, 84, "T", ["R1V", "R1"])),
        ("J26", (34, 95, "", ["TB2"])), ("R13", (34, 80, "T", ["R1V", "R1"])), ("R14", (40, 80, "T", ["R1V", "R1"])),
        ("J34", (50, 95, "", ["TB2"])),
        ("J28", (65, 95, "", ["TB2"])), ("J30", (79, 95, "", ["TB2"])),
        ("J32", (88, 80, "T", ["H3", "H3H"])), ("D9", (82, 82, "T", ["DO35V", "DO35"])), ("D10", (78, 82, "T", ["DO35V", "DO35"])),
    ]
    volt = {"L_SW": "AC", "L_K1": "AC", "L_TR": "AC", "N_SW": "AC", "L_TR2": "AC", "HT_TR": "AC", "HT_F": "AC", "B_AC1": 92, "B_AC2": -92, "VB_RAW": -90, "VBIAS": -78,
            "H2_A": 0, "H2_B": 0, "H3_A": 42, "H3_B": 42, "HTR_ELEV": 42, "+12V": 12, "RLY1": 12, "RLY2": 12}
    b = _build("zasilacz_siec", "Soloist 88 - zasilacz: siec, bias, zarzenie", 100, 100, fixed, auto, comps, volt)
    b.texts = [(30, 52, "SOLOIST 88 ZASILACZ 230V/BIAS/ZARZENIE", 1.1)]
    return b


# =====================================================================================
# 2b. ZASILACZ - WYSOKIE NAPIECIE
# =====================================================================================
def zasilacz_hv():
    g_ht, g_f, g_s, g_e, g_r, g_c, g_mh = ("ANODY - PROSTOWNIK", "FILTR B+3", "POMIAR B+", "ELEWACJA ZARZENIA",
                                         "CEWKI K3/K4", "ZLACZA", "OTWORY")
    g_bl = "LED HV"
    comps = [
        ("J7", "HT_AC1", "PAD", ["HT_AC1"], g_ht, "S1 360 V przez F3 (plytka sieciowa J38 pin 2)"),
        ("J8", "HT_AC2", "PAD", ["HT_AC2"], g_ht, "S1 360 V"),
        ("K3", "G2RL-2-DC12", "RELAY_G2RL", {"1": "+12V", "8": "RLY3", "3": "HT_AC1", "2": None, "4": "K3_MID",
                                       "6": "K3_MID", "7": None, "5": "HT_K3"}, g_ht, "Omron G2RL-2, dwa styki szeregowo (360 V AC)"),
        ("K4", "G2RL-2-DC12", "RELAY_G2RL", {"1": "+12V", "8": "RLY4", "3": "HT_K3", "6": "HT_K3", "4": "HT_IN", "5": "HT_IN", "2": None, "7": None}, g_ht, "bocznik R_IN; Omron G2RL-2, 2 styki rownolegle"),
        ("R2", "100R 10W", "R", ["HT_K3", "HT_IN"], g_ht, "R_IN: 100R (bylo 47R) - udar ladowania C1 ok. 5 A zamiast 11 A przez styki K3"),
        ("D1", "UF5408", "D", {"1": "HV_RAW", "2": "HT_IN"}, g_ht, ""),
        ("D2", "UF5408", "D", {"1": "HV_RAW", "2": "HT_AC2"}, g_ht, ""),
        ("D3", "UF5408", "D", {"1": "HT_IN", "2": "GND"}, g_ht, ""),
        ("D4", "UF5408", "D", {"1": "HT_AC2", "2": "GND"}, g_ht, ""),
        ("C3", "10n/1kV", "C", ["HV_RAW", "HT_IN"], g_ht, "snubber D1"),
        ("C4", "10n/1kV", "C", ["HV_RAW", "HT_AC2"], g_ht, "snubber D2"),
        ("C5", "10n/1kV", "C", ["HT_IN", "GND"], g_ht, "snubber D3"),
        ("C6", "10n/1kV", "C", ["HT_AC2", "GND"], g_ht, "snubber D4"),
        ("C1A", "470u/400V", "CP", ["HV_RAW", "C1_MID"], g_f, "snap-in 30x50"),
        ("C1B", "470u/400V", "CP", ["C1_MID", "GND"], g_f, "snap-in 30x50"),
        ("R3", "150k 1W", "R", ["HV_RAW", "C1_MID"], g_f, "balans + rozladowanie (150k: 0,43 W przy 255 V)"),
        ("R4", "150k 1W", "R", ["C1_MID", "GND"], g_f, ""),
        ("J9", "L1_IN", "PAD", ["HV_RAW"], g_f, "do dlawika L1"),
        ("J10", "L1_OUT", "PAD", ["B+3"], g_f, "z dlawika L1"),
        ("C2A", "470u/400V", "CP", ["B+3", "C2_MID"], g_f, "snap-in 30x50"),
        ("C2B", "470u/400V", "CP", ["C2_MID", "GND"], g_f, "snap-in 30x50"),
        ("R5", "150k 1W", "R", ["B+3", "C2_MID"], g_f, ""),
        ("R6", "150k 1W", "R", ["C2_MID", "GND"], g_f, ""),
        ("R7", "1M 1600V", "R", ["B+3", "HVS1"], g_s, "pomiar B+ (opcja)"),
        ("R8", "1M 1600V", "R", ["HVS1", "HVS2"], g_s, ""),
        ("R9", "1M 1600V", "R", ["HVS2", "HV_SENSE"], g_s, ""),
        ("R10", "15k", "R", ["HV_SENSE", "GND"], g_s, ""),
        ("J18", "HV_SENSE", "PAD", ["HV_SENSE"], g_s, "do sterowania"),
        ("J11", "B+3_CT_L", "PAD", ["B+3"], g_c, "srodek T101"),
        ("J12", "B+3_CT_R", "PAD", ["B+3"], g_c, "srodek T201"),
        ("J13", "B+3_KAN_L", "PAD", ["B+3"], g_c, ""),
        ("J14", "B+3_KAN_R", "PAD", ["B+3"], g_c, ""),
        ("J15", "GND_STAR", "PAD", ["GND"], g_c, "punkt gwiazdy masy"),
        ("J16", "GND_KAN_L", "PAD", ["GND"], g_c, ""),
        ("J17", "GND_KAN_R", "PAD", ["GND"], g_c, ""),
        ("J37", "GND_SIEC", "PAD", ["GND"], g_c, "masa plytki sieciowej"),
        ("R140A", "150k 1W", "R", ["B+3", "ELEV_MID"], g_e, "elewacja +42 V z B+3; 2x150k szeregowo - po ok. 212 V na rezystor"),
        ("R140B", "150k 1W", "R", ["ELEV_MID", "HTR_ELEV"], g_e, "elewacja, druga polowa"),
        ("R141", "30k", "R", ["HTR_ELEV", "GND"], g_e, ""),
        ("C140", "47u/100V", "CP", ["HTR_ELEV", "GND"], g_e, ""),
        ("J36", "HTR_ELEV", "PAD", ["HTR_ELEV"], g_e, "do plytki sieciowej (J34 pin 1)"),
        ("J33", "RELAY_B", "CONN_3", ["+12V", "RLY3", "RLY4"], g_r, "z plytki sterowania (J2 piny 1,4,5)"),
        ("D11", "1N4148", "D", {"1": "+12V", "2": "RLY3"}, g_r, ""),
        ("D12", "1N4148", "D", {"1": "+12V", "2": "RLY4"}, g_r, ""),
        ("R16", "220k 1W", "R", ["B+3", "LED_M"], g_bl, "LED HV, ok. 1 mA"),
        ("R17", "220k 1W", "R", ["LED_M", "LED_A"], g_bl, ""),
        ("D13", "LED HV czerwona", "D", {"1": "GND", "2": "LED_A"}, g_bl, "swieci, dopoki B+ > ok. 30-50 V; dioda wysokiej sprawnosci 2 mA"),
    ] + [("MH%d" % k, "M3", None, {}, g_mh, "") for k in (1, 2, 3, 4)]
    fixed = {"C1A": (16, 84, "T", "SNAP30"), "C1B": (47, 84, "T", "SNAP30"), "C2A": (16, 53, "T", "SNAP30"), "C2B": (47, 53, "T", "SNAP30"),
             "K3": (25, 11, "T", "G2RL"), "K4": (58, 11, "T", "G2RL"), "R2": (36, 29, "T", "R10"),
             "MH1": (4.5, 4.5, "", "MH"), "MH2": (95.5, 4.5, "", "MH"), "MH3": (67, 95.5, "", "MH"), "MH4": (95.5, 95.5, "", "MH")}
    auto = [
        ("J7", (80, 6, "", ["PADL"])), ("J8", (88, 12, "", ["PADL"])),
        ("D1", (72, 30, "T", ["DO201V"])), ("D2", (80, 30, "T", ["DO201V"])), ("D3", (72, 50, "T", ["DO201V"])), ("D4", (80, 50, "T", ["DO201V"])),
        ("C3", (88, 30, "T", ["CS10"])), ("C4", (94, 30, "T", ["CS10"])), ("C5", (88, 50, "T", ["CS10"])), ("C6", (94, 50, "T", ["CS10"])),
        ("R3", (34, 68, "T", ["R1V", "R1"])), ("R4", (34, 98, "T", ["R1V", "R1"])),
        ("R5", (32, 40, "T", ["R1V", "R1"])), ("R6", (34, 66, "T", ["R1V", "R1"])),
        ("J9", (70, 64, "", ["PADL"])), ("J10", (70, 72, "", ["PADL"])),
        ("R7", (76, 70, "T", ["R1V", "R1"])), ("R8", (81, 70, "T", ["R1V", "R1"])), ("R9", (86, 70, "T", ["R1V", "R1"])),
        ("R10", (91, 70, "T", ["R05V", "R05"])), ("J18", (96, 70, "", ["PAD"])),
        ("J11", (70, 82, "", ["PADL"])), ("J12", (77, 82, "", ["PADL"])), ("J13", (84, 82, "", ["PADL"])), ("J14", (91, 82, "", ["PADL"])),
        ("J15", (74, 90, "", ["PADL"])), ("J16", (81, 90, "", ["PADL"])), ("J17", (88, 90, "", ["PADL"])), ("J37", (80, 96, "", ["PADL"])),
        ("R140A", (60, 40, "T", ["R1V", "R1"])), ("R140B", (64, 40, "T", ["R1V", "R1"])), ("R141", (68, 40, "T", ["R05V", "R05"])), ("C140", (74, 40, "T", ["CP10"])),
        ("J36", (96, 40, "", ["PAD"])),
        ("J33", (96, 22, "T", ["H3", "H3H"])), ("D11", (88, 20, "T", ["DO35V", "DO35"])), ("D12", (84, 20, "T", ["DO35V", "DO35"])),
        ("R16", (60, 66, "B", ["R1"])), ("R17", (16, 44, "B", ["R1"])), ("D13", (6, 40, "T", ["LED3"])),
    ]
    volt = {"HT_AC1": "AC", "HT_AC2": "AC", "K3_MID": "AC", "HT_K3": "AC", "HT_IN": "AC", "HV_RAW": 510, "C1_MID": 255,
            "B+3": 465, "C2_MID": 232, "HVS1": 310, "HVS2": 155, "HV_SENSE": 2, "HTR_ELEV": 42, "ELEV_MID": 254, "LED_M": 232, "LED_A": 2, "+12V": 12, "RLY3": 12, "RLY4": 12}
    b = _build("zasilacz_hv", "Soloist 88 - zasilacz: wysokie napiecie", 100, 100, fixed, auto, comps, volt)
    b.texts = [(4, 36.5, "SOLOIST 88 ZASILACZ HV", 1.1)]
    return b


# =====================================================================================
# 3. STEROWANIE
# =====================================================================================
def sterowanie():
    g_mcu, g_pwr, g_drv, g_adc, g_in, g_con, g_mh = ("ESP32", "ZASILANIE 12 V / 5 V", "STEROWNIK PRZEKAZNIKOW", "POMIARY ADC",
                                                    "FILTRY WEJSC", "ZLACZA", "OTWORY")
    g_dac = "KOREKTA BIASU (DAC)"
    L = ["3V3", "3V3", None, "DQ", "IR", "ENC_A", "ENC_B", "ENC_SW", "BTN", "DRV6", "DRV7", "SDA", None, None, "SCL",
         "DRV1", "DRV2", "DRV3", "DRV4", "DRV5", "+5V", "GND"]
    Rr = ["GND", None, None, "TRIG_IN"] + [None] * 16 + ["GND", "GND"]
    nets = {"L%d" % (i + 1): n for i, n in enumerate(L)}
    nets.update({"R%d" % (i + 1): n for i, n in enumerate(Rr)})
    comps = [
        ("U1", "ESP32-S3-DevKitC-1", "ESP32S3_DEVKITC", nets, g_mcu, "na listwach zenskich"),
        ("J1", "230V_IN", "CONN_2", ["L_PS", "N_PS"], g_pwr, "zlacze srubowe 230 V: z zasilacz_siec J3 (za F2)"),
        ("PS1", "IRM-15-12", "IRM", {"1": "L_PS", "2": "N_PS", "3": "GND", "4": "+12V"}, g_pwr, "Mean Well IRM-15-12, 12 V / 1,25 A"),
        ("U2", "DC-DC 5V mini", "DCDC4", {"1": "GND", "2": "+12V", "3": "+5V", "4": "GND"}, g_pwr, "mini przetwornica step-down, stale 5 V, min. 1 A; 1 -IN, 2 +IN, 3 OUT+, 4 OUT-"),
        ("C1", "100u/25V", "CP", ["+12V", "GND"], g_pwr, ""),
        ("C2", "100u/16V", "CP", ["+5V", "GND"], g_pwr, ""),
        ("U3", "ULN2803G-S18-R", "ULN2803",
         {"1": "DRV1", "2": "DRV2", "3": "DRV3", "4": "DRV4", "5": "DRV5", "6": "DRV6", "7": "DRV7", "8": "GND",
          "18": "RLY1", "17": "RLY2", "16": "RLY3", "15": "RLY4", "14": "MUTE", "13": "RLY_UL", "12": "RLY_SPK", "11": None,
          "9": "GND", "10": "+12V"}, g_drv, "UTC ULN2803G-S18-R, SOP-18 (7,5 mm) - LCSC C33924"),
        ("J2", "RELAY", "CONN_5", ["+12V", "RLY1", "RLY2", "RLY3", "RLY4"], g_drv, "do plytek zasilacza (piny 1,2,3 -> siec; 1,4,5 -> HV)"),
        ("J3", "MUTE", "CONN_2", ["+12V", "MUTE"], g_drv, "przekaznik MUTE w przedwzmacniaczu"),
        ("J11", "UL_TRIODA", "CONN_4", ["+12V", "RLY_UL", "+12V", "RLY_UL"], g_drv, "1-2 plytka UL kanalu L, 3-4 kanalu P (J3 na plytce UL)"),
        ("J13", "GLOSNIKI", "CONN_2", ["+12V", "RLY_SPK"], g_drv, "cewki przelacznika glosnikow (plytka glosniki J7)"),
        ("J12", "TRIGGER", "CONN_2", ["TRIG_P", "TRIG_N"], "WEJSCIE TRIGGER 12 V", "z gniazda jack 3,5 mm na tylnej sciance (izolowanego od obudowy): 1 koncowka (+12 V), 2 tulejka"),
        ("R35", "1k 1206", "R", ["TRIG_P", "OPTO_A"], "WEJSCIE TRIGGER 12 V", "ok. 10 mA przy 12 V"),
        ("D13", "1N4148W", "D", {"1": "OPTO_A", "2": "TRIG_N"}, "WEJSCIE TRIGGER 12 V", "ochrona przed odwrotna polaryzacja"),
        ("U8", "PC817", "PC817", {"1": "OPTO_A", "2": "TRIG_N", "4": "TRIG_IN", "3": "GND"}, "WEJSCIE TRIGGER 12 V", "transoptor - masa Marantza oddzielona od masy Lampy"),
        ("R36", "10k", "R", ["3V3", "TRIG_IN"], "WEJSCIE TRIGGER 12 V", "podciaganie; TRIG_IN = 0 gdy trigger aktywny"),
        ("C17", "100n", "C", ["TRIG_IN", "GND"], "WEJSCIE TRIGGER 12 V", "filtr zaklocen"),
        ("U4", "ADS1115IDGSR 0x48", "ADS1115",
         {"1": "GND", "2": None, "3": "GND", "4": "IK_L1F", "5": "IK_L2F", "6": "IK_R1F", "7": "IK_R2F", "8": "3V3", "9": "SDA", "10": "SCL"},
         g_adc, "ADDR do GND"),
        ("U5", "ADS1115IDGSR 0x49", "ADS1115",
         {"1": "3V3", "2": None, "3": "GND", "4": "VB_F", "5": "3V3", "6": "HV_F", "7": None, "8": "3V3", "9": "SDA", "10": "SCL"},
         g_adc, "ADDR do VDD"),
        ("C9", "100n", "C", ["3V3", "GND"], g_adc, "przy U4"),
        ("C10", "100n", "C", ["3V3", "GND"], g_adc, "przy U5"),
        ("R9", "4k7", "R", ["3V3", "SDA"], g_adc, "podciaganie I2C"),
        ("R10", "4k7", "R", ["3V3", "SCL"], g_adc, "podciaganie I2C"),
        ("U6", "MCP4728-E/UN", "MCP4728",
         {"1": "3V3", "2": "SCL", "3": "SDA", "4": "GND", "5": None, "6": "DAC_L1", "7": "DAC_L2", "8": "DAC_R1", "9": "DAC_R2", "10": "GND"},
         g_dac, "I2C 0x60, Vref = VDD 3,3 V; LDAC do masy"),
        ("C11", "100n", "C", ["3V3", "GND"], g_dac, "przy U6"),
        ("U7", "LM324DR", "LM324",
         {"3": "DACF_L1", "2": "FB_L1", "1": "OA_L1", "5": "DACF_L2", "6": "FB_L2", "7": "OA_L2",
          "10": "DACF_R1", "9": "FB_R1", "8": "OA_R1", "12": "DACF_R2", "13": "FB_R2", "14": "OA_R2", "4": "+12V", "11": "GND"},
         g_dac, "wzmocnienie x3: 0-3,3 V -> 0-9,9 V"),
        ("C12", "100n", "C", ["+12V", "GND"], g_dac, "przy U7"),
    ]
    for i, n in enumerate(("IK_L1", "IK_L2", "IK_R1", "IK_R2")):
        comps += [("R%d" % (1 + i), "10k", "R", [n, n + "F"], g_in, ""),
                  ("C%d" % (3 + i), "1u", "C", [n + "F", "GND"], g_in, "X7R 50 V"),
                  ("D%d" % (1 + 2 * i), "1N4148W", "D", {"1": n + "F", "2": "GND"}, g_in, "zacisk do masy"),
                  ("D%d" % (2 + 2 * i), "1N4148W", "D", {"1": "3V3", "2": n + "F"}, g_in, "zacisk do 3V3")]
    for i, k in enumerate(("L1", "L2", "R1", "R2")):
        comps += [("R%d" % (11 + i), "10k", "R", ["FB_" + k, "GND"], g_dac, "wzmocnienie"),
                  ("R%d" % (15 + i), "20k", "R", ["OA_" + k, "FB_" + k], g_dac, "wzmocnienie"),
                  ("R%d" % (19 + i), "10k", "R", ["DAC_" + k, "DACF_" + k], g_dac, "filtr RC przed LM324 (10k / 1u = 10 ms)"),
                  ("C%d" % (13 + i), "1u", "C", ["DACF_" + k, "GND"], g_dac, "filtr RC"),
                  ("D%d" % (9 + i), "1N4148W", "D", {"1": "OA_" + k, "2": "GND"}, g_dac, "zacisk wyjscia LM324: bez 12 V nie schodzi ponizej masy"),
                  ("R%d" % (23 + i), "68k", "R", ["OA_" + k, "S_" + k], g_dac, "przesuwnik poziomu (0-9,9 V -> ok. -54...-51 V)"),
                  ("R%d" % (27 + i), "33k", "R", ["S_" + k, "VBIAS"], g_dac, "przesuwnik poziomu, do szyny biasu"),
                  ("R%d" % (31 + i), "1k", "R", ["S_" + k, "BI_" + k], g_dac, "wyjscie do wezla biasu (ochrona przy zwarciu przewodu)")]
    comps += [
        ("R5", "330k 1206", "R", ["VBIAS", "VB_F"], g_in, "pomiar -78 V"),
        ("R6", "10k", "R", ["VB_F", "3V3"], g_in, "przesuniecie do 3V3"),
        ("C7", "1u", "C", ["VB_F", "GND"], g_in, ""),
        ("R7", "10k", "R", ["HV_SENSE", "HV_F"], g_in, ""),
        ("C8", "1u", "C", ["HV_F", "GND"], g_in, ""),
        ("R8", "4k7", "R", ["3V3", "DQ"], g_mcu, "pull-up DS18B20"),
        ("J4", "IK", "CONN_5", ["IK_L1", "IK_L2", "IK_R1", "IK_R2", "GND"], g_con, "z rezystorow 10R przy KT88"),
        ("J5", "SENSE", "CONN_3", ["VBIAS", "HV_SENSE", "GND"], g_con, ""),
        ("J10", "BIAS_KOR", "CONN_4", ["BI_L1", "BI_L2", "BI_R1", "BI_R2"], g_con,
         "korekta biasu: 1 -> TP106 kanal L, 2 -> TP107 kanal L, 3 -> TP206 kanal P, 4 -> TP207 kanal P; przewody skrecone z masa"),
        ("J6", "DS18B20", "CONN_3", ["3V3", "DQ", "GND"], g_con, ""),
        ("J7", "IR", "CONN_3", ["3V3", "IR", "GND"], g_con, "TSOP38238"),
        ("J8", "WYSWIETLACZ", "CONN_4", ["3V3", "GND", "SCL", "SDA"], g_con, "I2C"),
        ("J9", "ENKODER", "CONN_5", ["ENC_A", "ENC_B", "ENC_SW", "BTN", "GND"], g_con, ""),
    ] + [("MH%d" % k, "M3", None, {}, "OTWORY", "") for k in (1, 2, 3, 4)]
    fixed = {"U1": (16, 52, "T", "ESP"), "PS1": (66.5, 23.5, "T", "IRM"), "J1": (84, 5.5, "", "TB2"), "MH1": (4.5, 4.5, "", "MH"), "MH2": (95.5, 4.5, "", "MH"),
             "MH3": (4.5, 95.5, "", "MH"), "MH4": (95.5, 95.5, "", "MH")}
    auto = [
        ("U2", (36, 14, "T", ["DCDC4"])), ("C1", (36, 26, "T", ["CP6"])), ("C2", (36, 34, "T", ["CP6"])),
        ("J2", (40, 4, "T", ["H5H"])), ("J3", (54, 4, "T", ["H2H"])), ("J11", (66, 4, "T", ["H4H"])),
        ("U3", (40, 50, "T", ["SOIC18W"])),
        ("U4", (58, 47, "T", ["MSOP10"])), ("C9", (58, 43, "T", ["C0805"])),
        ("U5", (58, 56, "T", ["MSOP10"])), ("C10", (58, 60, "T", ["C0805"])),
        ("R9", (52, 44, "T", ["R0805V"])), ("R10", (52, 48, "T", ["R0805V"])),
        ("J4", (96, 48, "T", ["H5", "H5H"])), ("J5", (96, 64, "T", ["H3", "H3H"])), ("J10", (96, 84, "T", ["H4", "H4H"])),
        ("J6", (43, 96, "T", ["H3H"])), ("J7", (54, 96, "T", ["H3H"])), ("J8", (66, 96, "T", ["H4H"])), ("J9", (30, 96, "T", ["H5H"])),
        ("U6", (38, 66, "T", ["MSOP10"])), ("C11", (38, 61, "T", ["C0805"])),
        ("J13", (78, 4, "T", ["H2H"])),
        ("U7", (44, 79, "T", ["SOIC14"])), ("C12", (37, 79, "T", ["C0805V"])),
    ]
    for i in range(4):
        x = 70 + 6 * i
        auto += [("R%d" % (1 + i), (x, 43, "T", ["R0805V"])), ("C%d" % (3 + i), (x, 48, "T", ["C0805V"])),
                 ("D%d" % (1 + 2 * i), (x - 1.4, 54, "T", ["SOD123V"])), ("D%d" % (2 + 2 * i), (x + 1.4, 54, "T", ["SOD123V"]))]
    for i in range(4):
        y = 74 + 3.5 * i
        auto += [("R%d" % (11 + i), (51, y, "T", ["R0805"])), ("R%d" % (15 + i), (55.5, y, "T", ["R0805"])),
                 ("R%d" % (19 + i), (60, y, "T", ["R0805"])), ("C%d" % (13 + i), (64.5, y, "T", ["C0805"])),
                 ("D%d" % (9 + i), (69.5, y, "T", ["SOD123"])), ("R%d" % (23 + i), (75.5, y, "T", ["R0805"])),
                 ("R%d" % (27 + i), (81.5, y, "T", ["R0805"])), ("R%d" % (31 + i), (87.5, y, "T", ["R0805"]))]
    auto += [("R5", (74, 62, "T", ["R1206V", "R1206"])), ("R6", (79, 62, "T", ["R0805V"])), ("C7", (83, 62, "T", ["C0805V"])),
             ("R7", (79, 68, "T", ["R0805V"])), ("C8", (83, 68, "T", ["C0805V"])), ("R8", (36, 90, "T", ["R0805V", "R0805"])),
             ("J12", (96, 73.5, "T", ["H2", "H2H"])), ("U8", (89, 64, "T", ["DIP4"])), ("R35", (91, 59, "T", ["R1206", "R1206V"])),
             ("D13", (91, 70.5, "T", ["SOD123", "SOD123V"])), ("R36", (52, 64, "T", ["R0805V", "R0805"])), ("C17", (48, 64, "T", ["C0805V", "C0805"]))]
    volt = {"L_PS": "AC", "N_PS": "AC", "VBIAS": -78, "+12V": 12, "RLY1": 12, "RLY2": 12, "RLY3": 12, "RLY4": 12, "MUTE": 12, "RLY_UL": 12, "RLY_SPK": 12, "TRIG_P": 12, "TRIG_N": 0, "OPTO_A": 1,
            "BI_L1": -50, "BI_L2": -50, "BI_R1": -50, "BI_R2": -50, "S_L1": -52, "S_L2": -52, "S_R1": -52, "S_R2": -52}
    b = _build("sterowanie", "Soloist 88 - plytka sterowania ESP32 (SMD)", 100, 100, fixed, auto, comps, volt)
    b.texts = [(44, 91, "SOLOIST 88 STEROWANIE", 1.1)]
    return b


# =====================================================================================
# 4. UL / TRIODA  (jedna plytka na kanal, montaz na dnie miedzy KT88 kanalu)
# =====================================================================================
def ul():
    g_k, g_c, g_mh = "PRZEKAZNIKI UL/TRIODA", "ZLACZA", "OTWORY"
    comps = [
        ("K1", "G2RL-2-DC12", "RELAY_G2RL", {"1": "+12V", "8": "RLY_UL", "3": "G2_A", "6": "G2_A", "2": "UL_A", "7": "UL_A", "4": "AN_A", "5": "AN_A"},
         g_k, "lampa A (V103/V203): bez zasilania cewki G2 <- odczep UL (tryb UL); zasilona: G2 <- anoda (trioda)"),
        ("K2", "G2RL-2-DC12", "RELAY_G2RL", {"1": "+12V", "8": "RLY_UL", "3": "G2_B", "6": "G2_B", "2": "UL_B", "7": "UL_B", "4": "AN_B", "5": "AN_B"},
         g_k, "lampa B (V104/V204)"),
        ("D1", "1N4148", "D", {"1": "+12V", "2": "RLY_UL"}, g_k, "dioda cewki K1"),
        ("D2", "1N4148", "D", {"1": "+12V", "2": "RLY_UL"}, g_k, "dioda cewki K2"),
        ("J1", "LAMPA_A", "CONN_3", ["AN_A", "UL_A", "G2_A"], g_c,
         "zlacze srubowe 7,62 mm: 1 anoda KT88 A, 2 odczep UL transformatora, 3 do G2 (pin 4) przez R123/R124 270R 2W przy podstawce"),
        ("J2", "LAMPA_B", "CONN_3", ["AN_B", "UL_B", "G2_B"], g_c, "jak J1, lampa B"),
        ("J3", "CEWKI", "CONN_2", ["+12V", "RLY_UL"], g_c, "z plytki sterowania J11 (1-2 kanal L, 3-4 kanal P)"),
    ] + [("MH%d" % k, "M3", None, {}, g_mh, "") for k in (1, 2, 3)]
    fixed = {"K1": (24, 12.5, "T", "G2RL"), "K2": (24, 35.5, "T", "G2RL"),
             "J1": (66, 12.5, "", "TB762_3V"), "J2": (66, 35.5, "", "TB762_3V"),
             "MH1": (4.5, 4.5, "", "MH"), "MH2": (4.5, 43.5, "", "MH"), "MH3": (48, 24, "", "MH")}
    auto = [("J3", (4.5, 24, "", ["TB2V"])), ("D1", (12, 24, "T", ["DO35", "DO35V"])), ("D2", (22, 24, "T", ["DO35", "DO35V"]))]
    volt = {"AN_A": "AC", "UL_A": "AC", "G2_A": "AC", "AN_B": "AC", "UL_B": "AC", "G2_B": "AC", "+12V": 12, "RLY_UL": 12}
    b = _build("ul", "Soloist 88 - przelacznik UL/trioda (x2)", 74, 48, fixed, auto, comps, volt)
    b.texts = [(40, 46, "S88 UL/TRIODA", 1.0)]
    return b


# =====================================================================================
# 5. PRZELACZNIK GLOSNIKOW  (Marantz <-> Lampa), montaz w obudowie trafo pod lewym TG
# =====================================================================================
def glosniki():
    g_k, g_c, g_mh = "PRZEKAZNIKI GLOSNIKOW", "ZLACZA", "OTWORY"
    comps = []
    for k, ch, ref in ((1, "L", "K1"), (2, "R", "K2")):
        comps.append((ref, "G2RL-2-DC12", "RELAY_G2RL",
                      {"1": "+12V", "8": "RLY_SPK", "3": "SPK_%sP" % ch, "6": "SPK_%sN" % ch, "2": "MAR_%sP" % ch, "7": "MAR_%sN" % ch,
                       "4": "TUBE_%sP" % ch, "5": "TUBE_%sN" % ch}, g_k,
                      "kanal %s: bez pradu cewki kolumna <- Marantz (NC), cewka zasilona: kolumna <- Lampa (NO); + i - przelaczane" % ch))
    comps += [
        ("D1", "1N4148", "D", {"1": "+12V", "2": "RLY_SPK"}, g_k, "dioda cewki K1"),
        ("D2", "1N4148", "D", {"1": "+12V", "2": "RLY_SPK"}, g_k, "dioda cewki K2"),
        ("J1", "MARANTZ_L", "CONN_2", ["MAR_LP", "MAR_LN"], g_c, "z wyjscia glosnikowego Marantza, kanal L: 1 +, 2 -"),
        ("J2", "LAMPA_L", "CONN_2", ["TUBE_LP", "TUBE_LN"], g_c, "z wtornego T101: 1 odczep 4 Ohm, 2 COM (masa Lampy)"),
        ("J3", "KOLUMNA_L", "CONN_2", ["SPK_LP", "SPK_LN"], g_c, "do zaciskow kolumny L na tylnej sciance: 1 +, 2 -"),
        ("J4", "MARANTZ_R", "CONN_2", ["MAR_RP", "MAR_RN"], g_c, "z Marantza, kanal R"),
        ("J5", "LAMPA_R", "CONN_2", ["TUBE_RP", "TUBE_RN"], g_c, "z wtornego T201: 1 odczep 4 Ohm, 2 COM"),
        ("J6", "KOLUMNA_R", "CONN_2", ["SPK_RP", "SPK_RN"], g_c, "do zaciskow kolumny R"),
        ("J7", "CEWKI", "CONN_2", ["+12V", "RLY_SPK"], g_c, "z plytki sterowania J13"),
    ] + [("MH%d" % k, "M3", None, {}, g_mh, "") for k in (1, 2, 3)]
    fixed = {"K1": (30, 28, "T", "G2RL"), "K2": (72, 28, "T", "G2RL"),
             "MH1": (4.5, 37.5, "", "MH"), "MH2": (51, 37.5, "", "MH"), "MH3": (95.5, 22, "", "MH")}
    auto = [("J1", (12, 5, "", ["TB2"])), ("J2", (27, 5, "", ["TB2"])), ("J3", (42, 5, "", ["TB2"])),
            ("J4", (58, 5, "", ["TB2"])), ("J5", (73, 5, "", ["TB2"])), ("J6", (88, 5, "", ["TB2"])),
            ("J7", (95.5, 36, "T", ["H2", "H2H"])), ("D1", (12, 38, "T", ["DO35", "DO35V"])), ("D2", (62, 38.5, "T", ["DO35", "DO35V"]))]
    volt = {"+12V": 12, "RLY_SPK": 12}
    b = _build("glosniki", "Soloist 88 - przelacznik glosnikow Marantz / Lampa", 100, 42, fixed, auto, comps, volt)
    b.texts = [(4, 16, "S88 GLOSNIKI", 1.0)]
    return b

VOLT = {
    "kanal": {"B+3": 465, "B+2": 460, "B+1": 290, "ANODE_A": 271, "ANODE_B": 271, "A_EF": 81, "TAIL": 87, "G_A": 81,
              "N_GB": 81, "G_B": 81, "G2_EF": 73, "CC_MID": 150, "STEP": 81, "VBIAS": -78, "BIAS_T": -50, "BIAS_B": -50,
              "BMID_T": -25, "BMID_B": -25, "GRID_T": -50, "GRID_B": -50, "HTR_A": 42, "HTR_B": 42, "Q_S": 2, "RS_MID": 1},
}
BOARDS = [kanal, zasilacz_siec, zasilacz_hv, sterowanie, ul, glosniki]
HV = {"kanal": {"B+3", "B+2", "B+1", "ANODE_A", "ANODE_B", "A_EF", "TAIL", "G_A", "N_GB", "G_B", "G2_EF", "CC_MID", "VBIAS", "BIAS_T", "BIAS_B", "BMID_T", "BMID_B", "GRID_T", "GRID_B"},
      "zasilacz_hv": {"HT_AC1", "HT_AC2", "K3_MID", "HT_K3", "HT_IN", "HV_RAW", "C1_MID", "B+3", "C2_MID", "HVS1", "HVS2", "ELEV_MID", "LED_M"},
      "zasilacz_siec": {"L_SW", "N_SW", "L_K1", "L_TR", "L_TR2", "HT_TR", "HT_F"},
      "sterowanie": {"L_PS", "N_PS"},
      "ul": {"AN_A", "UL_A", "G2_A", "AN_B", "UL_B", "G2_B"},
      "glosniki": set()}
