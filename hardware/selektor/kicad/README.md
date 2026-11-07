# TubeSel v0.5: selektor 4 wejść + drabinka przekaźnikowa 63 dB + sterownik I²C

Projekt KiCad 8 (otwiera się też w KiCad 9 i nowszych).

## Zawartość
- `tube_selector.kicad_pro`: projekt (klasy sieci Audio 0,4 mm / Coil 0,3 mm)
- `tube_selector.kicad_sch`: schemat (A3)
- `tube_selector.kicad_pcb`: płytka 96 × 74 mm, 2 warstwy, elementy rozmieszczone, strefy mas na obu warstwach, **bez ścieżek**
- `TubeSel.kicad_sym` + `sym-lib-table`: biblioteka symboli projektu
- `TubeSel.pretty` + `fp-lib-table`: footprint modułu DC-DC
- `BOM.csv`: lista elementów z numerami LCSC (separator `;`)
- `JLCPCB_BOM.csv`: BOM w formacie JLCPCB do zamówienia montażu (tylko elementy SMD)
- `LCSC_zamowienie.csv`: komplet elementów do samodzielnego montażu (2 płytki + zapas, ze złączami JST) do wgrania w narzędziu BOM na lcsc.com
- Podgląd schematu i rozmieszczenia: [`docs/img/selektor_*.png`](../../../docs/img/)
- Pełna dokumentacja: [`docs/11-selektor.md`](../../../docs/11-selektor.md)
- Pliki projektu wygenerował skrypt `src/selektor/gen.py`. **Po rozpoczęciu trasowania w KiCadzie źródłem prawdy są pliki KiCad.** Ponowne uruchomienie generatora (`src/selektor/gen.py`) nadpisze ścieżki (zobacz [`src/selektor/README.md`](../../../src/selektor/README.md)).

## Układ
- **Selektor K1–K4:** COM = wejście, NO = wspólna szyna, NC = 1 kΩ do masy.
- **Drabinka K5–K10:** bity 1/2/4/8/16/32 dB, impedancja ok. 10 kΩ (9,6–10,8 kΩ), rezystory cienkowarstwowe 0,1% w wartościach dostępnych w JLCPCB/LCSC. Cewka ON = stopień tłumi. Błąd tłumienia ≤ 0,21 dB dla wszystkich 64 kodów (symulacja); kanały L i R mają identyczne wartości.

| Bit | Rs | Rp |
|---|---|---|
| −1 dB | 1,10k | 80,6k |
| −2 dB | 2,00k | 32,4k |
| −4 dB | 3,75k | 17,4k |
| −8 dB | 6,20k | 6,81k |
| −16 dB | 9,10k | 2,00k |
| −32 dB | 10,0k | 270R |
- **R33/R34 10 kΩ:** terminator, wymagany do poprawnych tłumień.
- **K11 mute (fail-safe):** bez prądu cewki wyjście jest zwarte do masy. Dźwięk dopiero po załączeniu K11.
- **Sterownik:** U1 MCP23017 (I²C) → U2, U3 ULN2803 (UTC ULN2803G-S18-R, LCSC C33924; dowolny ULN2803 w SOIC-18 300 mil pasuje) → cewki. Diody gaszące są w ULN2803 (COM → +12 V).

| Wyjście MCP23017 | Przekaźnik | Funkcja |
|---|---|---|
| GPA0–GPA3 | K1–K4 | wejście 1–4 |
| GPA4–GPA7 | K5–K8 | −1, −2, −4, −8 dB |
| GPB0–GPB1 | K9–K10 | −16, −32 dB |
| GPB2 | K11 | mute (H = dźwięk) |
| GPB3–GPB7 | — | wolne |

Wyjście w stanie H = cewka załączona.

- **Zasilanie:** płytka potrzebuje tylko +12 V. 3,3 V dla MCP23017 i pull-upów I²C daje moduł DC-DC U4 (wersja 3,3 V; pinout 1 −IN, 2 +IN, 3 OUT+, 4 OUT−; rozstaw 14,17 × 8,24 mm). Pobór z 3,3 V to kilka mA.
- **J6 (JST XH 6p) do ESP32:** 1 +12 V, 2 DGND, 3 n/c, 4 SDA, 5 SCL, 6 DGND. Pin 3 celowo nie jest podłączony: nie łącz 3,3 V z ESP32 z 3,3 V tej płytki (dwa źródła napięcia).
- **Adres I²C:** SJ1–SJ3 otwarte = **0x20**. Zwarcie SJn ustawia bit An (0x20–0x27). Jeśli na tej samej magistrali jest drugi MCP23017 (np. od przekaźników biasu), ustaw tu inny adres.
- **Pull-upy I²C 4,7 kΩ (R36, R37)** są na płytce. Jeśli ESP32 też ma swoje, nic się nie stanie.

## Masy
- **GND (audio)** i **DGND (cyfrowa)** to osobne sieci i osobne strefy miedzi. DGND zajmuje dolny pas płytki pod układami scalonymi.
- **R41 (0 Ω, domyślnie nie montować)** łączy je w jednym punkcie. Zostaw puste, jeśli masa ESP32 łączy się z masą wzmacniacza w gwieździe gdzie indziej (tak jest najlepiej). Zmontuj tylko wtedy, gdy DGND nie ma innego połączenia z masą wzmacniacza.
- **R35 (0 Ω, DNP)** łączy masę audio z obudową przez MH1.

## Do sprawdzenia przed zamówieniem
1. **Biegunowość cewki G6K-2F-Y: potwierdzona.** Pin 1 = +12 V, pin 8 = do ULN2803. Przy lutowaniu ustaw znacznik pinu 1 na obudowie przekaźnika zgodnie ze znacznikiem na sitodruku; odwrotnie wlutowany polaryzowany przekaźnik nie zadziała.
2. Kolejność pinów kabli audio na J1–J5 (sitodruk „R G L”).
3. **Footprint modułu DC-DC** odwzorowałem ze zrzutu ekranu: otwory 1,0 mm, pady 2,2 mm, obrys 17,6 × 12,2 mm. Zmierz suwmiarką swój moduł (średnicę pinów i obrys) albo podmień footprint na własny.
4. Moduł DC-DC przy obciążeniu kilku mA zwykle pracuje w trybie impulsowym (burst). Jeśli w głośnikach pojawi się cichy szum lub „ćwierkanie”, pomoże dławik/ferryt w linii +3V3 albo zastąpienie modułu stabilizatorem 78L33.

## Kroki w KiCadzie
1. Otwórz `tube_selector.kicad_pro`.
2. Schemat: Inspect → Electrical Rules Checker.
3. PCB: Tools → Update PCB from Schematic (powinno nie wykryć zmian), poprowadź ścieżki (ręcznie lub wtyczką Freerouting), naciśnij **B** (wypełnienie stref) i uruchom DRC.

## Wskazówki do trasowania
- Tor audio na warstwie TOP, krótko; BOTTOM w części audio w miarę możliwości jako ciągła masa.
- Linie cewek (ULN → przekaźniki) i +12 V prowadź z dala od wejść, najlepiej prostopadle do ścieżek audio.
- Żadna ścieżka cyfrowa (SDA, SCL, DRV) nie powinna wchodzić w część audio.
- Kanały L (pady po prawej stronie przekaźników) i R (po lewej) rozdzielaj masą.

## Sterowanie
Zmiana głośności: najpierw ZAŁĄCZ nowe bity, odczekaj ~5 ms, potem WYŁĄCZ zbędne. Przejście zawsze idzie przez stan cichszy.
Po starcie MCP23017 ma wszystkie piny jako wejścia, więc wszystkie przekaźniki są wyłączone: wejście 1 niewybrane, tłumienie 0 dB i **mute aktywny**. Odblokowanie dźwięku następuje dopiero, gdy firmware ustawi wejście, głośność i GPB2 = 1.

## Montaż w JLCPCB
- `JLCPCB_BOM.csv` zawiera wszystkie elementy SMD z numerami LCSC (stan magazynu sprawdzony 22.10.2026). Plik pozycji (CPL) wygeneruj w KiCadzie po poprowadzeniu ścieżek: File → Fabrication Outputs → Component Placement (.pos), format CSV, jednostki mm.
- Złącza JST (J1–J6) i moduł DC-DC (U4) są przewlekane, więc najprościej przylutować je samemu.
- R35 i R41 (0 Ω, opcjonalne) są poza BOM-em JLCPCB.
- **Przed zatwierdzeniem zamówienia sprawdź w podglądzie JLCPCB orientację każdego przekaźnika i układu scalonego** (znacznik pinu 1). Obrócony G6K nie zadziała.
