# 9. Historia decyzji i poprawek

Zapis najważniejszych ustaleń, łącznie z błędami, które zostały znalezione i poprawione.

## Konfiguracja

- **Stereo w jednej obudowie, jeden toroid sieciowy 400 VA** zamiast dwóch monobloków TubeMack.
- **KT88 zamiast EL34**, bias stały z osobną regulacją każdej lampy, pomiar prądu katody (10 Ω 1%).
- **Źródło prądowe DN2540** w ogonie LTP.
- **DAC zewnętrzny** (WiiM / RPi), we wzmacniaczu tylko wejścia RCA. RPi nie jest w obudowie.
- **Transformatory wyjściowe toroidalne** (Toroidy.pl). Toroid jest wrażliwy na różnicę prądów stałych w parze, stąd automatyczna korekta biasu.
- **Dławik toroidalny 12 H / 400 mA** (wariant 300 mA miał 29 Ω, 10 H / 500 mA miał 66,5 Ω).

## Zasilanie i bezpieczeństwo

- R140 (270k 1 W przy 423 V) rozbity na 2× 150k 1 W, a R141 zmieniony na 30k.
- Bezpieczniki: F1 T2,5A w IEC, F2 T500mA dla IRM, F3 T1A min. 400 V AC w S1. Oprawka F3 pod 5×20 albo 6,3×32.
- LED HV (2× 220k) i rezystory upływowe 150k. Bleeder przełączany przekaźnikiem nie zmieścił się na płytce.
- IRM-15-12 przeniesiony z zasilacz_siec na płytkę sterowania (strefa 230 V ≥ 7,9 mm).
- Złącza śrubowe 5,08 / 7,62 mm na zasilacz_siec.

## Płytki

- Klasy sieci zapisane w plikach KiCad, przechodzą do EasyEDA Pro. Klasa HV 2,5 mm kolidowała przy podstawce noval, więc anody dostały klasę ANODA 1,25 mm (IPC-2221 do 300 V).
- Płytka kanału: lampy maksymalnie oddalone na brzegach, wszystkie kondensatory na spodzie, C105/C106 w oryginalnym footprincie. Po routingu w EasyEDA (v0.21) już się nie zmienia.
- Wspólne identyfikatory schematu i płytki (crc32 oznaczenia), żeby „Update PCB” działało.
- **v0.22:**
  - przekaźniki Omron G2RL-2 z footprintem z biblioteki KiCad, wcześniej przybliżonym;
  - płytka sterowania w SMD;
  - automatyczna korekta biasu;
  - płytki UL/trioda.
- **v0.23:** płytka przełącznika kolumn i wejście trigger.

## Selektor wejść (osobna sesja, 10–11.2026)

- **Przekaźniki zamiast scalaków** (CD4052, ADG14xx, NJW1194, PGA2311, TDA7439): brak półprzewodnika w torze. Przekaźniki mocy odrzucone (*dry switching*), wybrany sygnałowy Omron G6K-2F-Y DC12.
- **Bez EQ we wzmacniaczu**: korekcja cyfrowo w źródle; analogowy procesor z bypassem byłby duplikacją.
- **Drabinka series-shunt 10 kΩ, 6 bitów co 1 dB**; krok 0,5 dB odrzucony (nierówne kroki przy dostępnych rezystorach, więcej klikania).
- **Mute fail-safe**: K11 bez prądu zwiera wyjście do masy.
- **v0.2:** MCP23017 + 2× ULN2803 na płytce selektora (sam MCP nie wysteruje 12 V, sam ULN ma 8 kanałów przy 11 cewkach); osobna masa DGND.
- **v0.3:** tylko 12 V, 3,3 V z mini przetwornicy na płytce.
- **v0.4:** wartości drabinki przeliczone na rezystory 0,1% dostępne w JLCPCB/LCSC (wcześniejsze E192 nie były dostępne); błąd ≤ 0,21 dB.
- **v0.5:** ULN2803ADWR (TI, ok. 6 USD) → UTC ULN2803G-S18-R (0,29 USD), jak na płytce sterowania.
- Poprawka dokumentacji: w [07](07-zrodla-i-poziomy.md) był numer LCSC C47190, czyli G6K-2F-Y **DC5**; dla 12 V właściwy jest C397192.

## Błędy znalezione przy przeglądzie (25.10.2026)

1. **Korekta biasu obciążała szynę biasu ok. 10 mA**: szyna spadłaby do ok. −71 V i odpalał alarm. Poprawka: przesuwnik 68k/33k z wyjściem 1k (ok. 0,9 mA na lampę) i R142 1k5 → 1k.
2. **Dioda zaciskowa przewodziła przy małych wartościach DAC.** Filtr RC przeniesiony przed LM324, dioda na wyjście.
3. **Udar ładowania C1 przez K3 ok. 11 A** (przekaźnik 8 A). R_IN 47 → 100 Ω.
4. Pierwsza wersja korekty (sam rezystor 47k do 0–10 V) przesuwała bias o ok. 14 V. Zastąpiona przesuwnikiem poziomu przed publikacją v0.22.
5. Dokumentacja: dławik 5 H zamiast 12 H, rezystor siatki ekranowej podany jako 100 Ω zamiast R123/R124 270 Ω 2 W, opis masy gwiazdowej.

## Obudowa

- v0.1–0.2: bryły fasetowe, w Fusion widoczne jako siatka. v0.3: dokładne B-rep (ADVANCED_BREP).
- Transformatory głośnikowe podniesione o 35 mm, pod nimi stalowe profile na przewody wejściowe.
- Ekran aluminiowy nad płytką sterowania.
- v0.4: zaciski Marantz / kolumny, gniazdo trigger, osłona lamp +15 mm (KT120).

## Rozważane, ale odłożone

- **Pełna klasa A:** niemożliwa przy 465 V (ok. 46 W strat na lampę).
- **Tryb „gorący AB” 65 mA:** możliwy programowo, mały zysk.
- **EF86 w triodzie:** wymaga przeliczenia R103/R105, bo stopień jest sprzężony bezpośrednio z LTP.
- **Automatyczne rozmieszczenie w EasyEDA:** słabe, pozycje dobierane ręcznie.
