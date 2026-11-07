import os, sys
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
import draw

SCH_CSS = open(os.path.join(D, "sch.css")).read()

def table(head, rows, cls=""):
    h = "".join(f"<th>{c}</th>" for c in head)
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tw"><table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'

changes = table(["Element", "TubeMack 0.8b", "Ta wersja", "Dlaczego"], [
    ["Konfiguracja", "monoblok, własny zasilacz", "stereo, wspólny TR1 400 VA", "jedna obudowa, jeden transformator sieciowy"],
    ["V102 (LTP)", "ECC88", "E88CC / 6922", "184 V między anodą a katodą; ECC88 ma w katalogu 130 V, E88CC 220 V"],
    ["Transformator wyjściowy", "Edcor CXPP100-MS-3.3K", "Toroidy TTG-KT88PP, 4 kΩ", "dostępny w Polsce, wyjście 4 Ω pod Twoje kolumny"],
    ["Sprzężenie zwrotne", "R17 39k (pod Edcora)", "R104 27k z wyjścia 4 Ω", "to samo β przy napięciu niższym o √2; wartość końcową ustala pomiar"],
    ["Kompensacja", "C13 ≈ 82 pF", "C103 120 pF, dobór 68–220 pF", "ta sama stała czasowa przy mniejszym R104; toroid wymaga strojenia od nowa"],
    ["Regulacja biasu", "dzielnik 220k / 50k / 68k", "27k + reostat 50k + 27k na lampę", "zakres −40…−58 V; przerwa w suwaku daje bardziej ujemne napięcie, czyli bezpieczny stan"],
    ["Zasilanie biasu", "60 V AC, R 27k", "65 V AC, R142 1k", "większe obciążenie: 4 lampy, pomiar i korekta (ok. 7 mA)"],
    ["Prostownik HT", "720 V CT, 2 diody", "360 V, mostek UF5408", "jedno uzwojenie, ten sam B+"],
    ["Kondensatory HT", "500 V", "2× 400 V szeregowo lub 550 V", "bez obciążenia przy sieci +10% ≈ 560 V"],
    ["Załączanie", "termistor CL-150", "przekaźniki K1–K4 z ESP32", "opóźnione anody, kontrola biasu przed ich załączeniem"],
    ["Prąd katod", "10 Ω, punkty pomiarowe", "10 Ω 1% + ADS1115", "ciągły pomiar i odcięcie anod przy awarii"],
    ["Ochrona CCS", "—", "D105 Zener 12 V bramka–źródło Q101", "chroni bramkę MOSFET-a przed skokami napięcia przy załączaniu anod"],
    ["Wyjście", "brak obciążenia awaryjnego", "R127 100 Ω 2 W", "transformator nie pracuje z otwartym wtórnym, gdy odepniesz kolumnę"],
    ["Bias – utrzymanie", "ręcznie", "automatyczna korekta z ESP32 (MCP4728 + LM324)", "toroidalny transformator wyjściowy nie lubi różnicy prądów w parze; automat wyrównuje parę w ciszy, potencjometry zostają"],
    ["Tryb pracy KT88", "UL", "UL albo trioda, przekaźnik na każdą lampę", "trioda: ok. 20–25 W, łagodniejsze brzmienie; przełączanie tylko przy wyłączonych anodach"],
    ["Kolumny", "na stałe", "przełącznik Marantz / Lampa + wejście trigger 12 V", "te same kolumny dla amplitunera i Lampy; Marantz SR7013 może sam włączać Lampę"],
])

oppoints = table(["Punkt", "Wartość", "Uwagi"], [
    ["B+3 (CT T101/T201)", "465 V", "po dławiku L1; anody KT88 ≈ 463 V"],
    ["B+2 (LTP)", "460 V", "R130 330 Ω, C130 220 µF; tłumienie tętnień ≈ 46×"],
    ["B+1 (EF86)", "290 V", "R131 68k przy 2,5 mA"],
    ["EF86: katoda / anoda / g2", "0,8 V / 81 V / 73 V", "I<sub>K</sub> ≈ 2,5 mA"],
    ["LTP: katody / anody", "87 V / 271 V", "ogon 14 mA, 7 mA na sekcję, 1,3 W na sekcję (max 1,5 W)"],
    ["Q101 (CCS)", "87 V × 14 mA", "1,2 W, potrzebny mały radiator"],
    ["KT88: siatka", "≈ −45…−52 V", "zależy od egzemplarza; zakres potencjometru −45…−56 V z dołączoną korektą (bez niej −40…−59 V)"],
    ["KT88: prąd katody", "55 mA (0,55 V na 10 Ω)", "w tym 3–5 mA prądu siatki ekranowej; straty anody ≈ 25 W"],
    ["Szyna biasu", "≈ −80 V", "65 V AC, mostek, C–R–C; −71 V przy sieci −10%, −89 V przy +10%"],
    ["Elewacja żarzenia małych lamp", "+42 V", "R140A/B, R141 z B+3; katody LTP mają 87 V"],
    ["Tętnienia na B+3", "≈ 30 mV p-p", "C1 ≈ 13 V p-p, filtr LC ≈ 460×; push-pull dodatkowo je znosi"],
])

tr = table(["Uzwojenie", "Napięcie", "Prąd", "Zasila"], [
    ["Pierwotne", "230 V", "—", "opcjonalnie odczepy 220 / 240 V"],
    ["Ekran elektrostatyczny", "—", "—", "do PE; tłumi zakłócenia z prostownika"],
    ["S1 anodowe", "360 V AC", "0,65 A", "mostek D1–D4, B+ ≈ 465 V; zapas na wariant B; dodatkowy odczep 345 V pozwoli obniżyć B+"],
    ["S2 żarzenie mocy", "6,3 V", "7 A", "4× KT88 (6,4 A)"],
    ["S3 żarzenie sygnałowe", "6,3 V", "3 A", "2× EF86 + 2× E88CC = 1,0 A; z 6N6P (wariant B) 1,9 A; podniesione do +42 V"],
    ["S4 bias", "65 V AC", "50 mA", "szyna ≈ −80 V"],
])

seq = table(["Krok", "Czas", "ESP32 robi", "Warunek przejścia"], [
    ["Czuwanie", "—", "zasila się z PS1, czeka na przycisk lub IR", "polecenie włączenia"],
    ["Sieć", "t = 0", "K1 ON, TR1 przez R_SS", "—"],
    ["Bocznik", "+1,5 s", "K2 ON, zwiera R_SS", "—"],
    ["Kontrola biasu", "+2…5 s", "mierzy szynę biasu", "−68…−92 V; inaczej błąd i K1 OFF"],
    ["Nagrzewanie", "do +45 s", "odlicza na wyświetlaczu", "bias nadal w normie"],
    ["Anody", "+45 s", "K3 ON, prostownik przez R_IN", "—"],
    ["Bocznik R_IN", "+46,5 s", "K4 ON", "—"],
    ["Stabilizacja", "+46…90 s", "czyta I<sub>K</sub> czterech lamp", "każda 35–75 mA, stabilna przez 5 s"],
    ["Gra", "≈ +60 s", "zwalnia MUTE w przedwzmacniaczu", "nadzór ciągły"],
    ["Korekta biasu", "co 30–60 s ciszy", "uśrednia I<sub>K</sub>, zmienia DAC o mały krok", "prądy stabilne, brak sygnału"],
    ["Kolumny na Lampę", "po stabilizacji", "MUTE → RLY_SPK ON → 0,5 s → MUTE OFF", "Lampa gotowa; do tego czasu kolumny grają z Marantza"],
    ["Trigger z Marantza", "12 V na jacku", "włącza Lampę, wybiera wejście pre-out; zanik 12 V = wyłączenie", "—"],
    ["UL / trioda", "na żądanie", "MUTE → K3, K4 OFF → czeka na B+ &lt; 30 V → RLY_UL → anody jak przy starcie", "—"],
    ["Wyłączanie", "—", "MUTE → RLY_SPK OFF (kolumny do Marantza) → 0,5 s → K3, K4 OFF → 3 s → K1, K2 OFF", "—"],
])

prot = table(["Warunek", "Reakcja"], [
    ["Szyna biasu mniej ujemna niż −65 V", "natychmiast MUTE i K3/K4 OFF; żarzenie zostaje, komunikat na ekranie"],
    ["Średni I<sub>K</sub> (1 s) którejkolwiek lampy &gt; 130 mA przez 3 s", "K3/K4 OFF. Utrata biasu daje 200 mA i więcej, a głośna muzyka w klasie AB podnosi średnią do ok. 90–100 mA, więc niższy próg dawałby fałszywe alarmy"],
    ["I<sub>K</sub> &lt; 20 mA przy pozostałych lampach w normie", "ostrzeżenie: brak żarzenia lub zużyta lampa"],
    ["I<sub>K</sub> spoczynkowy &gt; 75 mA (cisza, 5 s)", "K3/K4 OFF. Chroni m.in. przed przerwą przewodu korekty J10: bias wraca wtedy do wartości z samego potencjometru"],
    ["Różnica w parze &gt; 10 mA, oba prądy poniżej 70 mA", "ostrzeżenie: wyreguluj P102/P103 (P202/P203)"],
    ["DAC korekty na końcu zakresu", "ostrzeżenie: lampa do wymiany albo przestaw potencjometr (DAC w połowie)"],
    ["Temperatura &gt; 70 °C / &gt; 80 °C", "ostrzeżenie / wyłączenie anod"],
    ["B+ &gt; 50 V przy wyłączonych anodach (także w czuwaniu)", "ostrzeżenie „HV” na ekranie, dopóki kondensatory się nie rozładują; ponowne załączenie K3 dopiero po spadku B+"],
])

bom_ch = table(["Oznaczenie", "Wartość", "Parametry", "Uwagi"], [
    ["V101", "EF86", "", "lub 6Ж32П; podstawka z ekranem, montaż antymikrofonowy"],
    ["V102", "E88CC", "", "lub 6922, 6N23P-EV; nie zwykła ECC88. 6N6P tylko z wartościami z wariantu B"],
    ["V103, V104", "KT88", "para dobrana", "kwartet dobrany na oba kanały"],
    ["R101", "220k", "0,5 W", ""],
    ["R102, R108, R110, R113", "1k", "0,25 W", "rezystory przy siatkach, lutować przy podstawce"],
    ["R103", "330 Ω", "0,5 W", ""],
    ["R104", "27k*", "0,5 W", "dobór 22–33k na pomiar głębokości NFB"],
    ["R105", "100k", "1 W", ""],
    ["R106", "470k", "0,5 W", ""],
    ["R107", "1,5M", "0,5 W", ""],
    ["R109", "1M", "0,5 W", ""],
    ["R111, R112", "27k", "5 W, 1%", "dobrana para"],
    ["R114", "100 Ω", "0,5 W", ""],
    ["R115, R116", "100k", "0,5 W", "upływ siatek KT88; całość ≈ 120k, dopuszczalne 220k"],
    ["R117, R118", "4k7", "0,5 W", "przy podstawce KT88, pin 5"],
    ["R119–R122", "27k", "0,5 W", ""],
    ["R123, R124", "270 Ω", "2 W", "siatki ekranowe, przy podstawce, pin 4"],
    ["R125, R126", "10 Ω", "1 W, 1%", "równolegle 2× 1N4007 szeregowo (D101–D104) na wypadek przerwy"],
    ["R127", "100 Ω", "2 W", "na zaciskach 4 Ω – COM"],
    ["R130", "330 Ω", "2 W", "gałąź zasilania kanału"],
    ["R131", "68k", "1 W", ""],
    ["P101", "200 Ω", "cermet 0,5 W", "ustawia prąd ogona 14 mA"],
    ["P102, P103", "50k", "cermet, wieloobrotowy", "bias KT88; przed pierwszym startem na maksimum"],
    ["C101", "47 nF", "250 V, PP", "z R101 daje 15 Hz, chroni trafo wyjściowe przed infradźwiękami"],
    ["C102", "47 nF", "400 V, PP", ""],
    ["C103", "120 pF*", "500 V, mika lub C0G", "dobór 68–220 pF na oscyloskopie"],
    ["C104", "0,47 µF", "400 V, PP", ""],
    ["C105, C106", "0,47 µF", "630 V, polipropylen", "sprzęgające do KT88; mały upływ obowiązkowy. Na PCB pola pod obudowę 27,5 mm (WIMA MKP4, Kemet R76) albo kondensator osiowy, raster 52 mm, korpus do 46 × 22 mm"],
    ["C130", "220 µF", "550 V", "lub 2× 470 µF / 400 V szeregowo + 2× 220k"],
    ["C131", "47 µF", "500 V", "przy zimnym EF86 dostaje pełne B+2"],
    ["Q101", "DN2540N5", "TO-220", "radiator ok. 10 K/W"],
    ["D105", "1N4742A", "Zener 12 V, 1 W", "bramka–źródło Q101, katoda do źródła; w normalnej pracy nie przewodzi"],
    ["T101", "TTG-KT88PP", "Toroidy", "4 kΩ, UL 43%, 80 W"],
    ["Opcja", "R128 4k7 + C107 33 pF", "", "sieć schodkowa z anody EF86 do masy, pola na PCB"],
    ["Opcja", "C108 2,7 pF + R129 1,2M", "", "korekcja fazy z anody EF86 do anody V102b, pola na PCB"],
])

bom_common = table(["Oznaczenie", "Wartość", "Parametry", "Uwagi"], [
    ["TR1", "toroid 400 VA", "wg tabeli uzwojeń", "zamówienie w Toroidy.pl, z ekranem"],
    ["L1", "12 H", "400 mA, DCR 66,5 Ω, toroidalny", "Toroidy.pl; izolacja do rdzenia ≥ 1,5 kV; spadek ok. 22 V przy 0,33 A"],
    ["PS1", "Mean Well IRM-15-12", "12 V / 1,25 A, 15 W", "zasilacz czuwania (moduł impulsowy, ok. 52 × 27 × 24 mm) na płytce sterowania, 230 V z zasilacz_siec J3; pobór bez obciążenia < 0,1 W"],
    ["U2 (sterowanie)", "mini przetwornica DC-DC", "stałe 5 V, min. 1 A, 4 piny", "step-down 12 V → 5 V zamiast LM7805; 4 piny w prostokącie 14,2 × 8,2 mm: −IN, +IN, OUT+, OUT−"],
    ["D1–D4", "UF5408", "1000 V, 3 A", "+ 4× 10 nF / 1 kV równolegle (snubbery)"],
    ["C1, C2", "2× 470 µF", "400 V, szeregowo", "balans 4× 150k 1 W (0,43 W każdy); to też rezystory rozładowujące"],
    ["LED HV", "czerwona LED 3 mm, wysokiej sprawności + 2× 220k 1 W", "ok. 1 mA", "na płytce zasilacz_hv; świeci, dopóki B+ > ok. 30–50 V — nie zastępuje miernika"],
    ["R_IN", "100 Ω", "10 W", "ogranicza prąd ładowania C1 przy załączeniu anod do ok. 5 A (przez styki K3)"],
    ["R_SS", "47 Ω", "10 W", "miękki start toroidu"],
    ["K1, K2", "Omron G2RL-2-DC12", "2 styki 8 A / 250 V AC, LCSC C61458", "strona sieciowa; oba styki równolegle"],
    ["K3", "Omron G2RL-2-DC12", "2 styki, łączone szeregowo", "360 V AC na dwóch stykach; izolacja cewka–styki 5 kV"],
    ["K4", "Omron G2RL-2-DC12", "2 styki równolegle", "bocznik R_IN, widzi tylko spadek na rezystorze"],
    ["Płytka głośników", "2× Omron G2RL-2-DC12 + 2× 1N4148", "6 złączy 5,08 mm", "przełącza + i − każdej kolumny między Marantzem a Lampą; pod lewym TG"],
    ["Trigger", "PC817 + 1k + 1N4148W + 10k + 100 nF", "jack 3,5 mm mono, izolowany", "na płytce sterowania; kabel jack–jack do TRIGGER OUT w SR7013"],
    ["Płytki UL (×2)", "2× Omron G2RL-2-DC12 + 2× 1N4148", "złącza śrubowe 7,62 mm", "jeden przekaźnik na KT88; płytka 74 × 48 mm na dnie między lampami kanału"],
    ["4× 100 Ω", "", "1 W", "sztuczne środki uzwojeń żarzenia"],
    ["R140A, R140B, R141, C140", "2× 150k / 30k / 47 µF", "1 W (szeregowo) / 0,5 W / 100 V", "elewacja żarzenia +42 V; dwa rezystory, bo na całości odkłada się 423–468 V"],
    ["D5–D8", "1N4007", "", "prostownik biasu"],
    ["C141, C142", "100 µF", "160 V", "biegun + do masy (szyna ujemna)"],
    ["R142", "1k", "1 W", "było 1,5k – większe obciążenie szyny przez korektę"],
    ["F1", "T2,5A", "5×20 mm, 250 V", "zwłoczny, w gnieździe IEC; miękki start ogranicza udar, więc 2,5 A wystarcza dla toroidu 400 VA (1,74 A)"],
    ["F2", "T500mA", "5×20 mm, 250 V", "zwłoczny, osobno dla PS1 (IRM-15-12) — sprawdź zalecenie w karcie modułu; oprawka na płytce zasilacz_siec"],
    ["F3", "T1A", "5×20 lub 6,3×32 mm, min. 400 V AC", "zwłoczny, w uzwojeniu S1 (360 V); chroni przed pożarem przy przebiciu lampy lub kondensatora; na płytce pola pod oprawkę 5×20 albo 6,3×32, oprawka też min. 400 V"],
    ["SW1", "wyłącznik 2-biegunowy", "250 V, 10 A", "lub gniazdo IEC z wyłącznikiem"],
    ["Sterowanie", "ESP32-S3, 2× ADS1115, ULN2803, MCP4728, LM324", "SMD, montaż w JLCPCB", "+ DS18B20, TSOP38238, wyświetlacz z enkoderem; lista SMD niżej"],
    ["Pomiar biasu", "330k + 10k", "330k na 500 V", "węzeł do ADS1115 #2 A0: −80 V → 0,85 V, 0 V → 3,2 V"],
    ["Pomiar B+ (opcja)", "3× 1M + 15k", "1M na 1600 V", "465 V → 2,3 V; 560 V → 2,8 V"],
])

import csv as _csv
_EXT = {"C37593", "C108207", "C7943"}
_BASIC = {"C17414", "C4328", "C17673", "C28323", "C49678", "C81598", "C17633", "C17513"}
with open(os.path.join(D, "pcb", "Soloist88_PCB", "4_montaz_SMD_JLCPCB", "sterowanie_BOM_JLCPCB.csv"), encoding="utf-8") as _fh:
    _rows = list(_csv.reader(_fh))[1:]
bom_smd = table(["Oznaczenie", "Element", "Obudowa", "LCSC", "Typ"],
                [[r[1].replace(",", ", "), r[0], r[2].split("_")[1] if r[2].startswith(("R_", "C_", "D_")) else r[2].split("_")[0], r[3],
                  "Extended" if r[3] in _EXT else ("Basic" if r[3] in _BASIC else "sprawdź")] for r in _rows])

steps = [
    ("Kontrola przed włączeniem", "Sprawdź ciągłość PE do obudowy, polaryzację elektrolitów i brak zwarć szyn HT do masy. Wszystkie potencjometry biasu ustaw na maksimum, czyli najbardziej ujemne napięcie."),
    ("Zasilacz bez lamp", "Pierwsze włączenie przez żarówkę szeregową 100 W. ESP32 w trybie serwisowym z ręcznym sterowaniem K1–K4. Zmierz napięcia AC uzwojeń i szynę biasu (≈ −80 V). Na pinie 5 każdej podstawki KT88 powinno być ≈ −57 V (potencjometry na maksimum, DAC korekty na zero)."),
    ("HT bez obciążenia", "Bez lamp B+ dojdzie do ≈ 510 V, przy wysokiej sieci do 560 V. Sprawdź, czy rezystory balansujące dzielą napięcie po połowie na C1 i C2. Po wyłączeniu odczekaj kilka minut albo rozładuj kondensatory rezystorem 2 kΩ / 10 W."),
    ("Lampy sygnałowe", "Włóż EF86 i E88CC, bez KT88. Ustaw P101 tak, żeby na R111 i R112 było po ≈ 189 V (7 mA na sekcję). Sprawdź anodę EF86 i katody LTP. Bez KT88 B+ jest wyższe, więc wartości są orientacyjne."),
    ("KT88 i bias", "Włóż KT88, na wyjściu rezystor 4 Ω / 50 W, sprzężenie zwrotne odłączone. Po załączeniu anod obserwuj I<sub>K</sub> na wyświetlaczu; powyżej 80 mA wyłącz. Podnoś prąd każdej lampy stopniowo do 55 mA i skoryguj po 10 minutach."),
    ("Faza sprzężenia zwrotnego", "Bez FB podaj 50 mV / 1 kHz i zmierz wzmocnienie. Po podłączeniu FB wzmocnienie musi spaść mniej więcej pięciokrotnie. Jeśli rośnie albo układ się wzbudza, zamień przewody anod P1 i P2 transformatora wyjściowego."),
    ("Głębokość NFB", "Dobierz R104 tak, żeby różnica wzmocnień wynosiła 14–16 dB. Zapisz czułość dla pełnej mocy."),
    ("Kompensacja", "Prostokąt 1 kHz i 10 kHz kolejno na 4 Ω, na 4 Ω równolegle z 1 µF i bez obciążenia (tylko R127). Dobierz C103, a w razie potrzeby sieć R128/C107, aż przerzut będzie mały i bez dzwonienia. Ten krok wymaga oscyloskopu."),
    ("Pomiary końcowe", "Impedancja wyjściowa (napięcie bez obciążenia i z 4 Ω), charakterystyka 20 Hz – 40 kHz, moc przy początku obcinania."),
    ("Korekta biasu", "Z podłączonym J10 ustaw DAC w połowie zakresu (ok. 1,65 V na wyjściu MCP4728) i dopiero wtedy wyreguluj P102/P103 na 55 mA. Włącz automat, sprawdź po godzinie grania i ciszy, że prądy w parach różnią się o mniej niż 1 mA. Odłącz na chwilę jeden przewód J10 przy wyjętej KT88 i sprawdź alarm."),
    ("Kalibracja ESP32", "Wpisz rzeczywiste wartości rezystorów 10 Ω, napięcie szyny 3,3 V i progi zabezpieczeń. Sprawdź reakcję, odłączając na chwilę bias jednej lampy przy wyjętej KT88."),
]
steps_html = "".join(f"<li><h4>{t}</h4><p>{d}</p></li>" for t, d in steps)

open_q = [
    "Kolory przewodów TTG-KT88PP i faza uzwojeń: sprawdź w karcie producenta przed lutowaniem, faza FB i tak wymaga pomiaru.",
    "R104 i C103 to wartości startowe. Ostateczne ustala pomiar z Twoim egzemplarzem transformatora.",
    "Napięcie B+ zależy od rzeczywistej regulacji TR1. Gdyby wyszło powyżej 480 V, użyj odczepu 345 V.",
    "Dopuszczalna różnica prądów stałych w parze (ΔI) dla TTG-KT88PP – zapytać Toroidy.pl; od niej zależy próg w programie korekty.",
    "Program ESP32: algorytm korekty biasu i sekwencja UL/trioda są opisane, ale jeszcze nienapisane.",
    "Przed zamówieniem płytek: sprawdzić miernikiem wyprowadzenia G2RL-2 (bez zasilania cewki zwarte 3–2 i 6–7) oraz kolejność pinów +V/−V zasilacza IRM-15-12 – oba footprinty biorą to z założeń, nie z rysunku producenta.",
    "Masa gwiazdowa: masa sterowania łączy się z masą wzmacniacza w jednym punkcie – J15 (GND_STAR) na płytce zasilacza HV.",
    "Moc ≈ 45 W na kanał i czułość ≈ 160 mV to szacunki z obliczeń, nie pomiary.",
    "EF86 w połączeniu triodowym nie jest prostą zworką: stopień jest sprzężony bezpośrednio z LTP, więc zmiana trybu przesuwa napięcie anody EF86 i punkt pracy całego odwracacza. Wymaga osobnego przeliczenia R103 i R105.",
]
open_html = "".join(f"<li>{x}</li>" for x in open_q)

html = f"""<title>Soloist 88 Stereo</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=IBM+Plex+Sans+Condensed:wght@500;600;700&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap">
<style>
/* Layout: one reading column of engineering notes; schematics break out to full width and scroll sideways on small screens. */
:root {{
  --paper: #f3f5f6;
  --panel: #e6ecef;
  --ink: #1b2328;
  --muted: #56636c;
  --rule: #cfd8dd;
  --accent: #b5600e;
  --hv: #b3322a;
  --f-display: "IBM Plex Sans Condensed", "Arial Narrow", sans-serif;
  --f-body: "IBM Plex Sans", system-ui, sans-serif;
  --f-mono: "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --paper: #12181c; --panel: #1b2329; --ink: #dbe3e7; --muted: #92a0a9; --rule: #2c373e; --accent: #f0a04b; --hv: #ff7d6e;
    color-scheme: dark;
  }}
}}
:root[data-theme="dark"] {{
  --paper: #12181c; --panel: #1b2329; --ink: #dbe3e7; --muted: #92a0a9; --rule: #2c373e; --accent: #f0a04b; --hv: #ff7d6e;
  color-scheme: dark;
}}
body {{ background: var(--paper); color: var(--ink); font-family: var(--f-body); font-size: 15.5px; line-height: 1.6; }}
.wrap {{ max-width: 1120px; margin: 0 auto; padding-inline: 20px; padding-block: 40px 72px; }}
header {{ border-bottom: 2px solid var(--ink); padding-bottom: 22px; margin-bottom: 8px; display: grid; gap: 10px; }}
.eyebrow {{ font-family: var(--f-mono); font-size: 12px; letter-spacing: .08em; text-transform: uppercase; color: var(--accent); }}
h1 {{ font-family: var(--f-display); font-weight: 700; font-size: clamp(34px, 6vw, 54px); line-height: 1.02; margin: 0; letter-spacing: -.01em; text-wrap: balance; }}
.lede {{ max-width: 68ch; margin: 0; color: var(--muted); }}
.meta {{ font-family: var(--f-mono); font-size: 12.5px; color: var(--muted); display: flex; flex-wrap: wrap; gap: 6px 18px; }}
nav.toc {{ display: flex; flex-wrap: wrap; gap: 4px 16px; font-family: var(--f-mono); font-size: 13px; padding-block: 12px; border-bottom: 1px solid var(--rule); }}
nav.toc a {{ color: var(--ink); text-decoration: none; border-bottom: 1px solid var(--rule); }}
nav.toc a:hover, nav.toc a:focus-visible {{ color: var(--accent); border-color: var(--accent); outline: none; }}
section {{ padding-top: 44px; display: grid; gap: 14px; }}
h2 {{ font-family: var(--f-display); font-weight: 600; font-size: 28px; line-height: 1.15; margin: 0; text-wrap: balance; display: flex; gap: 12px; align-items: baseline; }}
h2 .sn {{ font-family: var(--f-mono); font-size: 14px; color: var(--accent); font-weight: 600; }}
h3 {{ font-family: var(--f-display); font-weight: 600; font-size: 19px; margin: 10px 0 0; }}
p {{ margin: 0; max-width: 72ch; }}
.spec {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); border-top: 1px solid var(--rule); border-left: 1px solid var(--rule); margin: 0; }}
.spec div {{ border-right: 1px solid var(--rule); border-bottom: 1px solid var(--rule); padding: 12px 14px; min-width: 0; }}
.spec dt {{ font-family: var(--f-mono); font-size: 11.5px; text-transform: uppercase; letter-spacing: .07em; color: var(--muted); }}
.spec dd {{ margin: 2px 0 0; font-family: var(--f-display); font-size: 21px; font-weight: 600; font-variant-numeric: tabular-nums; }}
.spec dd small {{ display: block; font-family: var(--f-body); font-size: 13px; font-weight: 400; color: var(--muted); }}
.tw {{ overflow-x: auto; border: 1px solid var(--rule); border-radius: 4px; }}
table {{ border-collapse: collapse; width: 100%; font-size: 14px; font-variant-numeric: tabular-nums; }}
th {{ text-align: left; font-family: var(--f-mono); font-size: 11.5px; font-weight: 600; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); background: var(--panel); padding: 9px 12px; border-bottom: 1px solid var(--rule); white-space: nowrap; }}
td {{ padding: 8px 12px; border-bottom: 1px solid var(--rule); vertical-align: top; }}
tbody tr:last-child td {{ border-bottom: 0; }}
td:first-child {{ font-family: var(--f-mono); font-size: 13px; font-weight: 600; white-space: nowrap; }}
figure {{ margin: 0; display: grid; gap: 8px; }}
.sheet {{ overflow-x: auto; background: var(--paper); border: 1px solid var(--rule); border-radius: 4px; padding: 10px; }}
.sheet svg {{ width: 100%; min-width: 1100px; max-width: none; }}
figcaption {{ font-size: 13.5px; color: var(--muted); max-width: 80ch; }}
.legend {{ display: flex; flex-wrap: wrap; gap: 6px 20px; font-size: 13px; color: var(--muted); }}
.legend b {{ color: var(--hv); font-family: var(--f-mono); }}
.warn {{ border-left: 3px solid var(--hv); padding: 10px 14px; background: var(--panel); max-width: 80ch; font-size: 14.5px; }}
.warn strong {{ color: var(--hv); }}
ol.steps {{ list-style: none; counter-reset: s; margin: 0; padding: 0; display: grid; gap: 0; }}
ol.steps li {{ counter-increment: s; display: grid; grid-template-columns: 44px 1fr; column-gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--rule); }}
ol.steps li::before {{ content: counter(s, decimal-leading-zero); font-family: var(--f-mono); font-weight: 600; color: var(--accent); grid-row: span 2; padding-top: 2px; }}
ol.steps h4 {{ margin: 0; font-family: var(--f-display); font-size: 17px; font-weight: 600; }}
ol.steps p {{ color: var(--ink); font-size: 14.5px; }}
ul.open {{ margin: 0; padding-left: 20px; display: grid; gap: 6px; max-width: 80ch; }}
.credits {{ font-size: 13px; color: var(--muted); border-top: 1px solid var(--rule); padding-top: 16px; margin-top: 44px; max-width: 80ch; }}
sub {{ font-size: .72em; }}
{SCH_CSS}
@media (max-width: 520px) {{ .wrap {{ padding-inline: 16px; }} h2 {{ font-size: 24px; }} }}
</style>

<div class="wrap">
<header>
  <div class="eyebrow">Wzmacniacz lampowy · wersja robocza 0.12 · 05.11.2026</div>
  <h1>Soloist 88 Stereo</h1>
  <p class="lede">Mullard 5-20 na KT88 według schematu TubeMack's Soloist 88 Rev. 0.8b, przerobiony na stereo w jednej obudowie, pod transformatory Toroidy TTG-KT88PP, kolumny 4 Ω i sterowanie z ESP32.</p>
  <div class="meta"><span>EF86 → E88CC (LTP + CCS) → 2× KT88 UL</span><span>klasa AB1, bias stały</span><span>wartości policzone, nie zmierzone</span></div>
</header>
<nav class="toc" aria-label="Spis treści">
  <a href="#zmiany">Zmiany</a><a href="#kanal">Schemat kanału</a><a href="#punkty">Punkty pracy</a><a href="#wariant-b">Wariant 6N6P</a><a href="#zasilacz">Zasilacz</a><a href="#sterowanie">Sterowanie</a><a href="#korekta">Korekta biasu</a><a href="#ul">UL / trioda</a><a href="#glosniki">Kolumny i trigger</a><a href="#bom">Lista elementów</a><a href="#uruchomienie">Uruchomienie</a><a href="#otwarte">Do ustalenia</a>
</nav>

<section>
  <dl class="spec">
    <div><dt>Moc</dt><dd>≈ 2× 45 W<small>na 4 Ω, szacunek</small></dd></div>
    <div><dt>Czułość</dt><dd>≈ 160 mV<small>pełna moc, NFB z wyjścia 4 Ω</small></dd></div>
    <div><dt>Sprzężenie zwrotne</dt><dd>14–16 dB<small>cel; dobór R104</small></dd></div>
    <div><dt>KT88</dt><dd>465 V · 55 mA<small>≈ 25 W strat na lampę</small></dd></div>
  </dl>
  <p class="warn"><strong>Napięcia zabójcze.</strong> B+ to 465 V przy kilkuset µF. Z włożonymi lampami B+ spada w niecałą sekundę. Z wyjętymi lampami kondensatory (razem ok. 470 µF) rozładowują się przez rezystory balansujące, dzielnik pomiarowy, elewację i LED HV ze stałą czasową ok. 35 s, więc poniżej 50 V schodzą dopiero po ok. 1,5 minuty. Czerwona dioda „HV” na płytce zasilacza świeci, dopóki jest niebezpieczne napięcie, ale gaśnie już przy kilkudziesięciu woltach — zawsze sprawdź miernikiem. Pomiary jedną ręką, sondy z zaczepami, sprawdzenie napięcia przed dotknięciem czegokolwiek.</p>
</section>

<section id="zmiany">
  <h2><span class="sn">01</span>Co zmieniłem względem oryginału</h2>
  <p>Topologia i większość wartości pochodzą ze schematu TubeMacka. Zmiany wynikają z pracy w stereo, innego transformatora wyjściowego, wyjścia 4 Ω i dodania nadzoru przez ESP32.</p>
  {changes}
</section>

<section id="kanal">
  <h2><span class="sn">02</span>Schemat kanału</h2>
  <p>Narysowany kanał lewy (oznaczenia 1xx). Kanał prawy jest identyczny, z oznaczeniami 2xx. Lampa V104 jest narysowana odwrócona, jak w oryginale, żeby obie anody trafiały na końce uzwojenia pierwotnego bez krzyżowania.</p>
  <figure>
    <div class="sheet">{draw.amp()}</div>
    <figcaption>
      <span class="legend"><span><b>czerwone</b> napięcia spoczynkowe względem masy</span><span>* wartość do doboru pomiarem</span><span>łuk na przewodzie = skrzyżowanie bez połączenia</span></span>
    </figcaption>
  </figure>
  <h3>Jak to działa</h3>
  <p>EF86 pracuje jako pentoda z dużym wzmocnieniem. Jej anoda jest sprzężona bezpośrednio z siatką V102a, więc w torze do lamp mocy jest tylko jeden kondensator sprzęgający na stronę, co pomaga stabilności na niskich częstotliwościach. Para różnicowa na E88CC odwraca fazę i daje dość napięcia, żeby wysterować KT88. Źródło prądowe Q101 w ogonie wyrównuje amplitudy obu wyjść lepiej niż rezystor. Dioda Zenera D105 ogranicza napięcie bramka–źródło: normalnie jest tam ok. −2 do −3 V i dioda nie przewodzi, a przy skokach napięcia przy załączaniu anod chroni bramkę. Sprzężenie zwrotne z wyjścia 4 Ω wraca przez R104 ∥ C103 do katody EF86.</p>
  <p>Bias każdej KT88 regulujesz osobno. Napięcie z szyny ≈ −80 V dzieli R119, reostat P102 i R121. Jeśli suwak potencjometru straci styk, siatka dostaje pełne napięcie szyny przez R119, czyli lampa się przymyka zamiast przewodzić pełnym prądem. Rezystory 10 Ω w katodach służą do pomiaru prądu przez ESP32.</p>
</section>

<section id="punkty">
  <h2><span class="sn">03</span>Punkty pracy</h2>
  {oppoints}
</section>


<section id="wariant-b">
  <h2><span class="sn">04</span>Wariant B: odwracacz na 6N6P</h2>
  <p>6N6P ma taki sam układ nóżek jak E88CC, ale ponad trzy razy większe dopuszczalne straty anody i znacznie wyższy prąd. Pracuje w ten sposób dalej od swoich granic i lepiej radzi sobie z dużym wysterowaniem siatek KT88 przy pełnej mocy. Nie jest to jednak wymiana lampy w podstawce: trzeba zmienić rezystory anodowe, prąd źródła i radiator.</p>
  <p>Zysk to niższe zniekształcenia stopnia sterującego przy głośnym graniu. Koszt to mniejsze wzmocnienie, a więc płytsze sprzężenie zwrotne i nieco wyższa impedancja wyjściowa. Przy Twoich kolumnach z dołkiem impedancji to realny minus, dlatego wariant A zostaje podstawowy, a B traktuj jako eksperyment do porównania na słuch i w pomiarach.</p>
  <div class="tw"><table class=""><thead><tr><th>Element</th><th>Wariant A: E88CC</th><th>Wariant B: 6N6P</th><th>Uwagi</th></tr></thead><tbody><tr><td>V102</td><td>E88CC / 6922</td><td>6N6P (6Н6П)</td><td>ten sam układ nóżek; żarzenie 0,75 A zamiast 0,3 A</td></tr><tr><td>Prąd ogona</td><td>14 mA</td><td>30 mA (15 mA na sekcję)</td><td></td></tr><tr><td>P101 / R114</td><td>200 Ω / 100 Ω</td><td>100 Ω / 47 Ω</td><td>DN2540 potrzebuje mniejszego R źródła przy 30 mA</td></tr><tr><td>Q101 – straty</td><td>1,2 W</td><td>2,7 W</td><td>radiator ok. 5 K/W</td></tr><tr><td>R111, R112</td><td>27k 5 W</td><td>12k 7 W</td><td>2,7 W w każdym; para dobrana 1%</td></tr><tr><td>Anody / katody V102</td><td>271 V / 87 V</td><td>≈ 274 V / ≈ 89 V</td><td>B+2 spada do ≈ 454 V</td></tr><tr><td>Straty na sekcję</td><td>1,3 W z 1,5 W (86%)</td><td>2,8 W z 4,8 W (58%)</td><td>6N6P pracuje dużo luźniej</td></tr><tr><td>Wzmocnienie na stronę</td><td>≈ 15×</td><td>≈ 9×</td><td>o 4,8 dB mniej wzmocnienia w pętli</td></tr><tr><td>Głębokość NFB</td><td>14–16 dB</td><td>≈ 10–11 dB</td><td>przy tym samym R104; impedancja wyjściowa wzrośnie o ok. 1/3</td></tr><tr><td>B+1 (EF86)</td><td>290 V</td><td>≈ 284 V</td><td>bez zmian w stopniu EF86</td></tr></tbody></table></div>
  <p>Żeby przejście z A na B nie wymagało przeróbek zasilacza, uzwojenie S3 jest już na 3 A, a S1 ma zapas prądowy. Na PCB warto przewidzieć pola dla rezystorów R111/R112 w rozmiarze 7 W i radiator Q101 dobrany od razu pod 2,7 W.</p>
</section>

<section id="zasilacz">
  <h2><span class="sn">05</span>Zasilacz</h2>
  <p>Jeden transformator TR1 dla obu kanałów, tak jak u Onyxa. Żarzenie i bias pojawiają się od razu, a anody dopiero po przekaźniku K3. Przekaźnik przełącza napięcie przemienne przed prostownikiem, dwoma stykami połączonymi szeregowo. Ramka oznacza gałąź powtórzoną dla każdego kanału.</p>
  <figure>
    <div class="sheet">{draw.psu()}</div>
    <figcaption>K1–K4 to przekaźniki sterowane z ESP32. Linie przerywane między stykami oznaczają styki jednego przekaźnika.</figcaption>
  </figure>
  <h3>Specyfikacja TR1 do zamówienia</h3>
  <p>Obliczeniowo ok. 300 VA, licząc z zapasem na wariant B. Zamów 400 VA: mniej się grzeje, ciszej pracuje, a B+ mniej siada przy głośnym graniu.</p>
  {tr}
</section>

<section id="sterowanie">
  <h2><span class="sn">06</span>Sterowanie ESP32</h2>
  <p>ESP32 zasilany z PS1 (Mean Well IRM-15-12) przez przetwornicę 5 V pracuje także w czuwaniu. Steruje przekaźnikami przez ULN2803 i przez dwa przetworniki ADS1115 mierzy prądy czterech KT88, szynę biasu i opcjonalnie B+. Każde wejście pomiaru prądu ma filtr 10k / 1 µF i dwie diody 1N4148W do szyn zasilania przetwornika. Przetwornik MCP4728 z LM324 koryguje bias, a szóste wyjście ULN2803 przełącza przekaźniki UL/trioda. Elementy SMD płytki sterowania montuje JLCPCB, przewlekane lutujesz sam.</p>
  <figure>
    <div class="sheet">{draw.ctl()}</div>
  </figure>
  <h3>Sekwencja</h3>
  {seq}
  <h3>Zabezpieczenia</h3>
  {prot}
</section>

<section id="korekta">
  <h2><span class="sn">07</span>Automatyczna korekta biasu</h2>
  <p>Toroidalny transformator wyjściowy nie ma szczeliny w rdzeniu, więc różnica prądów stałych dwóch KT88 w parze podmagnesowuje rdzeń. Lampy z czasem się rozjeżdżają. ESP32 mierzy już prąd każdej lampy, więc może sam dokręcać bias: w ciszy, małymi krokami, najpierw wyrównując parę, potem dociągając do 55 mA. Potencjometry P102/P103 zostają i ustawiają bias zgrubnie, automat dodaje tylko poprawkę.</p>
  <figure>
    <div class="sheet">{draw.biaskor()}</div>
    <figcaption>Na każdą KT88 jeden kanał przetwornika. Filtr 10k / 1 µF jest przed wzmacniaczem operacyjnym. Przesuwnik 68k / 33k do szyny biasu daje źródło ok. −54…−51 V, bliskie napięciu węzła biasu, więc korekta mało zawęża zakres potencjometru i obciąża szynę tylko ok. 0,9 mA na lampę. Płytki kanałów zostają bez zmian, przewód z J10 lutujesz do punktu pomiarowego TP106/TP107.</figcaption>
  </figure>
  {table(["Parametr", "Wartość", "Uwagi"], [
      ["Zakres korekty", "≈ ±0,7 V na siatce", "≈ ±6 mA prądu KT88; wystarcza na wyrównanie pary i zużycie lamp"],
      ["Zakres potencjometru", "−45…−56 V", "z dołączoną korektą (bez niej −40…−59 V); jeśli lampa potrzebuje bardziej ujemnego, R119/R120 27k → 24k"],
      ["Awaria ESP32 lub LM324", "najwyżej ≈ 0,85 V", "wyjście 0 V lub nasycone 10,5 V – bias nie zbliży się do zera"],
      ["Brak 12 V", "D9–D12", "wyjście LM324 nie schodzi poniżej masy; bias ≈ 0,8 V chłodniej"],
      ["Przerwany przewód J10", "do ≈ 4,5 V cieplej", "przy potencjometrze skręconym do końca; program wyłącza anody przy I<sub>K</sub> &gt; 75 mA w ciszy"],
      ["Kiedy koryguje", "tylko w ciszy", "w klasie AB średni prąd rośnie z sygnałem – korekta przy muzyce rozregulowałaby lampy"],
  ])}
</section>

<section id="ul">
  <h2><span class="sn">08</span>Przełącznik UL / trioda</h2>
  <p>W trybie triodowym siatka ekranowa KT88 dostaje napięcie z anody zamiast z odczepu UL transformatora. Moc spada do ok. 20–25 W na kanał, brzmienie robi się łagodniejsze. Na każdą lampę jest jeden przekaźnik Omron G2RL-2 z oboma stykami równolegle, na osobnej płytce UL (jedna na kanał, na dnie między lampami). Bez prądu w cewce wzmacniacz gra w UL.</p>
  <figure>
    <div class="sheet">{draw.ulsw()}</div>
    <figcaption>Przekaźniki przełączają się tylko przy wyłączonych anodach: w chwili przeskoku styku siatka ekranowa na moment wisi w powietrzu. ESP32 robi to sam: MUTE, K3/K4 OFF, czeka na B+ poniżej 30 V, przełącza, załącza anody jak przy starcie.</figcaption>
  </figure>
</section>

<section id="glosniki">
  <h2><span class="sn">09</span>Przełącznik kolumn i trigger z amplitunera</h2>
  <p>Kolumny są podłączone na stałe do przełącznika w obudowie transformatorów. Na każdy kanał jeden przekaźnik G2RL-2 przełącza oba bieguny kolumny między wyjściem amplitunera Marantz SR7013 a wyjściem 4 Ω Lampy, więc oba wzmacniacze nigdy nie są ze sobą połączone. Bez prądu w cewkach kolumny grają z Marantza – także gdy Lampa jest wyłączona albo coś w niej przestało działać.</p>
  <p>Lampa przejmuje kolumny dopiero po nagrzaniu i ustabilizowaniu biasu, zawsze przy wyciszonym wejściu. Rezystor R127 (100 Ω 2 W) na wtórnym każdego transformatora zostaje, więc lampa nigdy nie pracuje bez obciążenia. Sprzężenie zwrotne jest brane sprzed przekaźnika.</p>
  {table(["Element", "Gdzie", "Uwagi"], [
      ["4 pary zacisków", "tylna ścianka", "górny rząd: z Marantza, dolny: do kolumn; przewody 1,5 mm²"],
      ["Płytka GLOSNIKI 100 × 42 mm", "dno, pod lewym TG", "2× G2RL-2, ścieżki 2 mm; cewki z płytki sterowania (J13)"],
      ["Gniazdo TRIGGER", "tylna ścianka obok IEC", "jack 3,5 mm mono, korpus plastikowy – tulejka nie może dotykać obudowy"],
      ["Transoptor PC817", "płytka sterowania (J12)", "masa Marantza oddzielona od masy Lampy; 12 V z amplitunera włącza Lampę"],
  ])}
</section>

<section id="bom">
  <h2><span class="sn">10</span>Lista elementów</h2>
  <h3>Na kanał (×2)</h3>
  <p>Rezystory metalizowane 1%, jeśli nie podano inaczej. Kanał prawy ma te same wartości z oznaczeniami 2xx.</p>
  {bom_ch}
  <h3>Wspólne</h3>
  {bom_common}
  <h3>Elementy SMD płytki sterowania (montaż JLCPCB)</h3>
  <p>Ten sam zestaw jest w pliku <code>sterowanie_BOM_JLCPCB.csv</code> w paczce płytek. „Extended” to części z jednorazową opłatą za załadowanie podajnika (kilka USD za typ), „Basic” są bez dopłaty. Stan magazynowy sprawdź przy zamówieniu.</p>
  {bom_smd}
</section>

<section id="uruchomienie">
  <h2><span class="sn">11</span>Uruchomienie krok po kroku</h2>
  <ol class="steps">{steps_html}</ol>
</section>

<section id="otwarte">
  <h2><span class="sn">12</span>Do ustalenia</h2>
  <ul class="open">{open_html}</ul>
</section>

<p class="credits">Podstawa: TubeMack's Soloist 88 Amplifier, Rev. 0.8b z 18 marca 2010 (diyAudio). Zasilacz oryginału: boywonder. Poprawki: Johan Potgieter i Eli Duttman. Schemat oryginału: taj. Ta adaptacja nie była jeszcze budowana ani mierzona.</p>
</div>
"""
out = os.path.join(D, "soloist88.html")
open(out, "w").write(html)
print(out, len(html))
