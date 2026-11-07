"""BOM do zamowienia czesci (LCSC) - osobny plik XLSX na kazda plytke + elementy poza plytkami."""
import os, sys
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
import boards, jlc
from pcbgen import FOOT
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

# value -> (opis, obudowa/raster, producent, MPN, LCSC, uwagi)
# LCSC wpisany tylko tam, gdzie numer zostal sprawdzony (25.10.2026). Pusty = wyszukaj po MPN
# w LCSC BOM Tool albo kup w TME / sklepie lampowym (kolumna Uwagi).
R = lambda d, pkg, mpn, lc, note="": (d, pkg, "", mpn, lc, note)
RES05 = "osiowy, raster 12,7 mm"
RES1 = "osiowy, raster 15,24 mm"
CAT = {
    # ---------- rezystory male (0,25-0,5 W, 1%) ----------
    "100R": R("Rezystor 100 Ohm 0,5 W 1%", RES05, "MFR50SFTE52-100R", "C173138"),
    "1k": R("Rezystor 1 kOhm 0,5 W 1% 300 V", RES05, "MF1/2W-1KΩ±1% T", "C119418"),
    "4k7 (opcja)": R("Rezystor 4,7 kOhm 0,5 W 1% 300 V", RES05, "RN 1/2WS 4K7 F T/B A1", "C433513"),
    "15k": R("Rezystor 15 kOhm 0,5 W 1% 350 V", RES05, "MF1/2W-15K±1%-XT52", "C601895"),
    "27k": R("Rezystor 27 kOhm 0,25 W 1% (wystarczy: najwyzej 0,03 W)", RES05, "MFR-25FTE52-27K", "C172994",
             "27k 0,5 W 1% nie ma na stanie - 0,25 W wystarcza (siec biasu, max 78 V)"),
    "27k*": R("Rezystor 27 kOhm 0,25 W 1% (R104, NFB)", RES05, "MFR-25FTE52-27K", "C172994",
              "wartosc startowa; do doboru dokup 22k, 24k, 30k, 33k (seria MFR-25FTE52)"),
    "30k": R("Rezystor 30 kOhm 0,5 W 1%", RES05, "MF1/2WS-30KΩ±1% T", "C129921"),
    "100k": R("Rezystor 100 kOhm 0,5 W 1% 300 V", RES05, "RN 1/2WS 100K F T/B A1", "C433530"),
    "220k": R("Rezystor 220 kOhm 0,25 W 1% (wejscie)", RES05, "MFR-25FTE52-220K", "C172984"),
    "330R": R("Rezystor 330 Ohm 0,5 W 1%", RES05, "MFR0S2F3300A20", "C58577"),
    "470k": R("Rezystor 470 kOhm 0,5 W 1% 300 V (ok. 220 V na rezystorze)", RES05, "MF1/2W-470KΩ±1% T", "C119452"),
    "1M": R("Rezystor 1 MOhm 0,5 W 1% 300 V", RES05, "RN 1/2WS 1M F T/B A1", "C433529"),
    "1M2 (opcja)": R("Rezystor 1,2 MOhm 0,25 W 1% (opcja)", RES05, "MF0W4FF1204A50", "C20625224"),
    "1M5": R("Rezystor 1,5 MOhm 0,25 W 1% 250 V (73 V na rezystorze)", RES05, "MFR0W4F1504A50", "C122938"),
    # ---------- rezystory 1 W ----------
    "100k 1W": R("Rezystor 100 kOhm 1 W 1% 350 V", RES1, "MFR01SF1003A10", "C85019"),
    "68k 1W": R("Rezystor 68 kOhm 1 W 1%", RES1, "MF01SFF6802A10", "C20625257"),
    "100R 1W": R("Rezystor 100 Ohm 1 W 1% 350 V", RES1, "MF1W-100Ω±1% T", "C119469"),
    "1k 1W": R("Rezystor 1 kOhm 1 W 1%", RES1, "MFR1WSFTE52-1K", "C172926"),
    "150k 1W": R("Rezystor 150 kOhm 1 W 1%", RES1 + ", korpus 4,5 x 11,5", "MF1W-150KΩ±1% T", "C119513"),
    "220k 1W": R("Rezystor 220 kOhm 1 W 1% 350 V", RES1, "MFR01SF2203A10", "C82511"),
    "1M 1600V": R("Rezystor 1 MOhm 1 W 5%, 4 kV (dzielnik pomiaru B+)", RES1, "RCR60CT52A105J", "C782212",
                  "Vishay VR37 brak na stanie; ten ma 4 kV - pomiar i tak kalibrujesz w programie"),
    # ---------- rezystory mocy ----------
    "330R 2W": R("Rezystor 330 Ohm 2 W 1% 500 V", "osiowy, raster 20,32 mm", "MFR02SF3300A10", "C58731"),
    "27k 5W": R("Rezystor 27 kOhm 5 W 1% (anody LTP, para)", "osiowy, raster 35,56 mm, korpus do 30 x 9", "", "",
                "BRAK W LCSC - TME (np. rezystor metalizowany 5 W 1%); pola zmieszcza tez 7 W"),
    "47R 10W": R("Rezystor drutowy 10 W 47 Ohm (R_SS)", "osiowy 9 x 36,5 mm w polach 55,88 mm", "EWWR0010J47R0T9", "C349125",
                 "malo na stanie (25 szt.) - zamow od razu; alternatywa: cementowy SQP 10 W z TME"),
    "100R 10W": R("Rezystor drutowy 10 W 100 Ohm (R_IN)", "osiowy 9 x 36,5 mm w polach 55,88 mm", "EWWR0010J100RT9", "C349082"),
    # ---------- potencjometry ----------
    "200R": R("Potencjometr wieloobrotowy 200 Ohm", "Bourns 3296W", "3296W-1-201LF", "C83685"),
    "50k": R("Potencjometr wieloobrotowy 50 kOhm", "Bourns 3296W", "3296W-1-503LF", "C83686"),
    # ---------- polprzewodniki ----------
    "1N4007": R("Dioda 1N4007 1000 V 1 A", "DO-41", "1N4007G", "C2457"),
    "1N4148": R("Dioda 1N4148", "DO-35", "1N4148", "C402212"),
    "1N4742A 12V": R("Dioda Zenera 12 V 1 W", "DO-41", "1N4742A", "C140853"),
    "UF5408": R("Dioda szybka UF5408 1000 V 3 A", "DO-201AD", "UF5408", "C424502"),
    "DN2540N5": R("MOSFET z kanalem zubozanym 400 V, TO-220", "TO-220", "DN2540N5-G", "",
                  "BRAK W LCSC (jest tylko TO-92 / SOT-89 - za male na 1,2 W) - TME / Mouser"),
    "LED HV czerwona": R("LED 3 mm czerwona", "3 mm, raster 2,54", "204-10SURD/S530-A3-L", "C99771", "swieci juz przy ok. 1 mA"),
    "G2RL-2-DC12": R("Przekaznik Omron G2RL-2 12 V DPDT 8 A", "29 x 12,7 mm", "G2RL-2-DC12", "C61458",
                     "przed zamowieniem plytek sprawdz piny (CZYTAJ_MNIE)"),
    # ---------- kondensatory elektrolityczne ----------
    "220u/550V": R("Kondensator elektrolityczny 220 uF 550 V snap-in", "D35 x 50, raster 10 mm", "TLS550V220M35*50", "C347031",
                   "malo na stanie (17 szt.) - zamow od razu; alternatywa TME: Kemet ALC70A221DC550"),
    "47u/500V": R("Kondensator elektrolityczny 47 uF 500 V 105 C", "radialny D18 x 32, raster 7,5", "ECH2HM470M32OTZO", "C882083"),
    "470u/400V": R("Kondensator elektrolityczny 470 uF 450 V snap-in (450 V zamiast 400 V)", "D30 x 50, raster 10 mm", "KN471M45030*50A", "C513378",
                   "470 uF/400 V w D30 brak na stanie; wysokosc 50 mm - sprawdz z obudowa (krotszy: LSG450M477S353S1AA C47325526, 30 x 35)"),
    "100u/160V": R("Kondensator elektrolityczny 100 uF 160 V", "radialny D12,5 x 20, raster 5", "EGW2CM101W20OT", "C106374"),
    "47u/100V": R("Kondensator elektrolityczny 47 uF 100 V", "radialny D10 x 13, raster 5", "ERS1KM470G13OT", "C383038"),
    "100u/25V": R("Kondensator elektrolityczny 100 uF 25 V", "radialny D6,3 x 11, raster 2,5", "ERS1EM101E11OT", "C112509"),
    "100u/16V": R("Kondensator elektrolityczny 100 uF 25 V", "radialny D6,3 x 11, raster 2,5", "ERS1EM101E11OT", "C112509"),
    # ---------- kondensatory foliowe / ceramiczne ----------
    "0,47u/630V": R("Kondensator polipropylenowy MKP 0,47 uF 630 V (sprzeganie KT88)", "raster 27,5", "MMKP474J2J2701", "C557511",
                    "audiofilsko: WIMA MKP4 / Mundorf z TME lub osiowy poza plytka"),
    "470n/400V": R("Kondensator polipropylenowy 0,47 uF 630 V", "raster 22,5", "C322J474J90C000", "C401319"),
    "47n/400V": R("Kondensator polipropylenowy 47 nF 630 V", "raster 15", "MMK473J2JD3KN158G2", "C504240"),
    "47n/250V": R("Kondensator polipropylenowy 47 nF 630 V (wejscie)", "raster 10", "KP473J2J1001", "C390076"),
    "120p*": R("Kondensator ceramiczny SL 100 pF 1 kV (start dla C103)", "raster 5", "CC45SL3AD101JYVNA", "C342396",
               "120 pF HV przewlekanego brak; zacznij od 100 pF. Do doboru lepszy mikowy 68-220 pF z TME"),
    "33p (opcja)": R("Kondensator ceramiczny SL 33 pF 1 kV (opcja)", "raster 5", "N06S1B330KQ0T0S0N0", "C366798"),
    "2p7 (opcja)": R("Kondensator 2,7 pF 500 V (opcja)", "raster 5", "", "", "brak w LCSC - tylko jesli potrzebna korekcja fazy (TME)"),
    "10n/1kV": R("Kondensator polipropylenowy 10 nF 1 kV (snubbery mostka)", "raster 10", "MMKP103J3A1001", "C484936"),
    # ---------- zabezpieczenia ----------
    "T500mA 250V": R("Oprawka bezpiecznika 5x20 do druku, zamknieta (PTF-77) + bezpiecznik T500mA 5x20", "raster 22,5 mm",
                     "PTF-77 + 0218.500MXP", "C717030 + C142727", "dwie pozycje do koszyka: oprawka i bezpiecznik zwloczny"),
    "T1A 500V": R("Oprawka 5x20 lub 6,3x32 do druku min. 400 V AC + bezpiecznik T1A min. 400 V AC", "raster 22,5 (5x20) / 30 (6,3x32)", "", "",
                  "BRAK W LCSC (oprawki i bezpieczniki maja 250 V) - TME: ceramiczny zwloczny 500 V AC i oprawka na to napiecie"),
    # ---------- moduly ----------
    "PC817": R("Transoptor PC817 (wejscie trigger)", "DIP-4", "PC817X2NSZ9F", "C96006"),
    "IRM-15-12": R("Zasilacz Mean Well IRM-15-12 (12 V / 1,25 A)", "52,4 x 27,2 x 24 mm", "IRM-15-12", "C6394169"),
    "DC-DC 5V mini": R("Mini przetwornica 12 V -> 5 V, min. 1 A, 4 piny", "14,17 x 8,24 mm", "", "", "Twoj wybrany modul"),
    "ESP32-S3-DevKitC-1": R("Modul ESP32-S3-DevKitC-1 (N8R8 lub N16R8)", "2 x 22 piny", "ESP32-S3-DevKitC-1", "", "Botland / Kamami / TME"),
    "EF86": R("Podstawka B9A (noval) do druku, ceramiczna", "noval PCB", "", "", "BRAK W LCSC - sklep lampowy (np. TubeTown); lampa osobno"),
    "E88CC": R("Podstawka B9A (noval) do druku, ceramiczna", "noval PCB", "", "", "BRAK W LCSC - sklep lampowy; lampa E88CC / 6922 osobno"),
}
TERM = {"TerminalBlock_1x02_P5.08": ("Zlacze srubowe 2-pin 5,08 mm", "KEFA", "KF128-5.08-2P-AA", "C474952"),
        "TerminalBlock_1x03_P5.08": ("Zlacze srubowe 3-pin 5,08 mm", "KEFA", "KF128-5.08-3P-AA", "C474953"),
        "TerminalBlock_1x02_P7.62": ("Zlacze srubowe 2-pin 7,62 mm, 450 V", "KEFA", "KF7.62-2P", "C707824"),
        "TerminalBlock_1x03_P7.62": ("Zlacze srubowe 3-pin 7,62 mm, 450 V", "KEFA", "KF7.62-3P", "C707825")}

COUNT = {"kanal": 2, "ul": 2, "glosniki": 1}

STOCK = {}
try:
    import pickle
    for r in pickle.load(open("/home/claude/bomtool/db.pkl", "rb")):
        STOCK[r[0]] = r[3]
except Exception:
    pass


def stock(lc):
    if not lc:
        return ""
    vals = [STOCK.get(x.strip()) for x in lc.split("+")]
    return " + ".join("?" if v is None else str(v) for v in vals)


def rows_for(b):
    groups = {}
    extra = []
    hdr_m, hdr_r = 0, 0
    for c in b.comps:
        f = FOOT[c.fp].name.replace("_V", "")
        if f in ("MountingHole_M3", "TestPoint_2", "WirePad_3.5", "WirePad_4.5"):
            continue
        if jlc.is_smd(c):
            continue                       # montaz SMD w JLCPCB
        if f.startswith("PinHeader"):
            n = int(f.split("1x")[1][:2])
            if f.endswith("_H"):
                hdr_r += n
            else:
                hdr_m += n
            continue
        if f.startswith("TerminalBlock"):
            d, m, mpn, lc = TERM[f]
            key = (d, "", m, mpn, lc, "")
        else:
            info = CAT.get(c.value)
            if info is None:
                raise KeyError((b.name, c.ref, c.value, f))
            key = info
        groups.setdefault(key, []).append(c.ref)
    out = []
    for key, refs in groups.items():
        out.append((refs, key))
    if hdr_m:
        out.append(([f"listwy proste ({hdr_m} pin)"], ("Listwa kolkowa prosta 1x40, 2,54 mm (do ciecia)", "2,54 mm", "", "2.54-1*40P", "C2337", f"potrzeba {hdr_m} pinow + wtyki")))
    if hdr_r:
        out.append(([f"listwy katowe ({hdr_r} pin)"], ("Listwa kolkowa katowa 1x40, 2,54 mm (do ciecia)", "2,54 mm", "", "2.54-1*40P (katowa)", "C74252", f"potrzeba {hdr_r} pinow + wtyki")))
    if b.name == "sterowanie":
        out.append((["U1 (2 x 22 piny)"], ("Listwa zenska 1x20 2,54 mm", "2,54 mm", "Cancome", "B-2200S20P-A120", "C124410", "2 szt. (+ 1x2 ponizej = 22 piny na strone)")))
        out.append((["U1 (2 x 22 piny)"], ("Listwa zenska 1x2 2,54 mm", "2,54 mm", "Cancome", "B-2200S02P-A120", "C124411", "2 szt.")))
    return out


def natkey(r):
    import re
    m = re.match(r"([A-Za-z]+)(\d+)([A-Z]?)", r)
    return (m.group(1), int(m.group(2)), m.group(3)) if m else (r, 0, "")


HEAD = ["Lp", "Oznaczenia", "Ilosc na plytke", "Liczba plytek", "Ilosc razem", "Opis / parametry", "Obudowa / raster",
        "Producent", "MPN", "LCSC", "Stan mag. (25.10)", "Uwagi / gdzie kupic"]


def write_xlsx(path, title, rows, nboards):
    wb = Workbook(); ws = wb.active; ws.title = "BOM"
    ws.append([title]); ws["A1"].font = Font(bold=True, size=13)
    ws.append(["Czesci wybrane z czesci DOSTEPNYCH na magazynie wg bazy katalogu JLCPCB/LCSC z 25.10.2026 (kolumna Stan). "
               "Wiersze na pomaranczowo = brak w LCSC, kup w TME / sklepie lampowym. Minimalne ilosci sprawdz w koszyku."])
    ws.append([])
    ws.append(HEAD)
    for c in ws[4]:
        c.font = Font(bold=True); c.fill = PatternFill("solid", fgColor="DDE4E8")
    rows = sorted(rows, key=lambda r: natkey(r[0][0]))
    for i, (refs, (desc, pkg, mfr, mpn, lc, note)) in enumerate(rows, 1):
        refs_s = ", ".join(sorted(refs, key=natkey)) if refs and refs[0][0].isalpha() and refs[0][1:2].isdigit() else ", ".join(refs)
        n = len(refs) if not refs[0].startswith(("listwy", "U1 (")) else 1
        if refs[0].startswith("U1 ("):
            n = 2
        ws.append([i, refs_s, n, nboards, n * nboards, desc, pkg, mfr, mpn, lc, stock(lc), note])
        if not lc:
            for c in ws[ws.max_row]:
                c.fill = PatternFill("solid", fgColor="FBE3D6")
    widths = [4, 28, 9, 8, 9, 52, 30, 10, 26, 18, 12, 60]
    for k, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(k)].width = w
    for row in ws.iter_rows(min_row=5):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "A5"
    wb.save(path)


OFF = [  # elementy poza plytkami
    (["R117, R118 (x2 kanaly)"], 4, ("Rezystor 4,7 kOhm 0,5 W 1% - przy podstawce KT88, pin 5", "osiowy", "", "RN 1/2WS 4K7 F T/B A1", "C433513", "")),
    (["R123, R124 (x2)"], 4, ("Rezystor 270 Ohm 2 W - siatka ekranowa, przy podstawce, pin 4", "osiowy", "", "MO2WS-270Ω±5%-6T63", "C479464", "malo na stanie (ok. 300)")),
    (["R125, R126 (x2)"], 4, ("Rezystor 10 Ohm 1 W 1% - katoda KT88 (pomiar pradu)", "osiowy", "", "MFR01SF100JA10", "C58689", "")),
    (["D101-D104 (x2)"], 8, ("Dioda 1N4007 - zabezpieczenie rezystora katodowego", "DO-41", "", "1N4007G", "C2457", "")),
    (["R127 (x2)"], 2, ("Rezystor 100 Ohm 2 W - obciazenie awaryjne na zaciskach", "osiowy", "", "MFR02SF1000A10", "C58717", "")),
    (["V103, V104 (x2)"], 4, ("Podstawka octal ceramiczna do KT88 (montaz na szpilkach)", "octal", "", "", "", "BRAK W LCSC - sklep lampowy; sprawdz rozstaw otworow (obudowa: 50 mm)")),
    (["F1"], 1, ("Gniazdo IEC C14 z oprawka bezpiecznika (+ ew. wylacznik)", "", "", "", "", "TME")),
    (["zaciski glosnikowe"], 8, ("Zacisk glosnikowy (4 pary: 2 x KOLUMNA, 2 x Z MARANTZA)", "panelowy, otwor 9 mm", "", "", "", "TME / sklep audio; izolowane od obudowy")),
    (["gniazdo TRIGGER"], 1, ("Gniazdo jack 3,5 mm MONO panelowe, korpus plastikowy (izolowane od obudowy)", "otwor 6 mm", "", "", "", "TME; tulejka NIE moze dotykac obudowy")),
    (["kabel TRIGGER"], 1, ("Kabel jack 3,5 mm mono - jack 3,5 mm mono", "", "", "", "", "do wyjscia TRIGGER OUT w Marantz SR7013")),
    (["F1 wkladka"], 2, ("Bezpiecznik zwloczny T2,5A 5x20 (1 + zapas)", "5x20", "", "021802.5MXP", "C142705", "")),
    (["F2 zapas"], 1, ("Bezpiecznik zwloczny T500mA 5x20 (zapas)", "5x20", "", "0218.500MXP", "C142727", "")),
]


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    for fn in boards.BOARDS:
        b = fn()
        n = COUNT.get(b.name, 1)
        title = f"Soloist 88 - BOM plytki {b.name} (x{n}) - elementy przewlekane" + (" (SMD montuje JLCPCB - osobny plik)" if b.name == "sterowanie" else "")
        write_xlsx(os.path.join(outdir, f"{b.name}_BOM_LCSC.xlsx"), title, rows_for(b), n)
    wb_rows = [(r, (d)) for r, q, d in OFF]
    wb = Workbook(); ws = wb.active; ws.title = "BOM"
    ws.append(["Soloist 88 - elementy poza plytkami (przy podstawkach KT88, obudowa) - wybrane, bez transformatorow"])
    ws["A1"].font = Font(bold=True, size=13)
    ws.append([]); ws.append(["Lp", "Oznaczenia", "Ilosc razem", "Opis / parametry", "Obudowa", "Producent", "MPN", "LCSC", "Stan mag. (25.10)", "Uwagi"])
    for c in ws[3]:
        c.font = Font(bold=True); c.fill = PatternFill("solid", fgColor="DDE4E8")
    for i, (refs, q, (desc, pkg, mfr, mpn, lc, note)) in enumerate(OFF, 1):
        ws.append([i, ", ".join(refs), q, desc, pkg, mfr, mpn, lc, stock(lc), note])
    for k, w in enumerate([4, 24, 10, 60, 12, 10, 22, 10, 12, 50], 1):
        ws.column_dimensions[get_column_letter(k)].width = w
    wb.save(os.path.join(outdir, "poza_plytkami_BOM.xlsx"))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(D, "BOM_LCSC"))
