# 8. Części i zakupy

## BOM-y

- [`hardware/pcb/5_BOM_czesci_LCSC/`](../hardware/pcb/5_BOM_czesci_LCSC/): jeden plik XLSX na płytkę. Ilości uwzględniają 2 płytki kanału i 2 płytki UL. Jest też kolumna ze stanem magazynowym.
- `poza_plytkami_BOM.xlsx`: elementy przy podstawkach KT88 i w obudowie, bez transformatorów.
- [`hardware/pcb/4_montaz_SMD_JLCPCB/sterowanie_BOM_JLCPCB.csv`](../hardware/pcb/4_montaz_SMD_JLCPCB/): montaż SMD.

**Dostępność:** numery LCSC wybrałem spośród części dostępnych na magazynie według bazy katalogu JLCPCB/LCSC ([jlcparts](https://github.com/yaqwsx/jlcparts)) z 25.10.2026. Wiersze pomarańczowe to części, których nie ma w LCSC.

### Czego nie ma w LCSC (TME / sklep lampowy)

- **DN2540N5-G w TO-220** (w LCSC tylko TO-92 i SOT-89, za małe na 1,2 W);
- **rezystory 27k 5 W** (R111/R112);
- **podstawki B9A i octal** (sklep lampowy, np. TubeTown);
- **oprawka i bezpiecznik F3 na min. 400 V AC**;
- C108 2,7 pF (opcja), kondensator mikowy do doboru C103;
- moduł ESP32-S3-DevKitC-1, przetwornica 5 V, gniazdo IEC, zaciski głośnikowe, gniazdo jack.

### Zamiany wymuszone dostępnością (footprinty bez zmian)

- C1A–C2B: 470 µF / **450 V** ⌀30 × 50 (470 µF / 400 V ⌀30 brak na stanie);
- rezystory 27k, 220k, 1M2, 1M5 w wersji 0,25 W (wystarczy, bo pracują przy małym napięciu i mocy);
- R7–R9 (pomiar B+): 1 MΩ 1 W 4 kV zamiast Vishay VR37;
- C103: na start 100 pF SL 1 kV, docelowo mikowy;
- R_SS / R_IN: rezystory drutowe 10 W 9 × 36,5 mm (nóżki odgiąć w polach 55,88 mm).

**Mało na stanie, zamów od razu:** C130 220 µF / 550 V (17 szt.), R_SS 47 Ω 10 W (25 szt.).

## Przekaźniki

Wszędzie **Omron G2RL-2-DC12** (DPDT 8 A / 250 V AC, izolacja cewka–styki 5 kV, LCSC C61458): K1–K4, 4× UL/trioda, 2× kolumny, razem 10 szt. Cewka nie ma biegunowości („No coil polarity”). Kierunek wymusza tylko dioda gasząca (katoda do +12 V).

Do selektora i drabinki głośności (osobny projekt): **G6K-2F-Y** (sygnałowy, złocone styki). Nie nadaje się do UL/trioda (125 V AC).

ULN2803: **ULN2803G-S18-R** (UTC, LCSC C33924), tańszy od TI. Sprawdź, że obudowa SOP-18 ma 7,5 mm szerokości.

## Lampy

| | Uwagi |
|---|---|
| **JJ / Tung-Sol KT88** | na pierwsze uruchomienie i jako zapas |
| **Psvane Summit KT88** | 42 W / 8 W, żarzenie 1,6 A, pasuje bez zmian. Klasa Genalex Gold Lion. Brać dopasowaną czwórkę z pomiarami, sprawdzić wysokość i warunki reklamacji. W układzie z 14–16 dB sprzężenia zwrotnego różnice brzmienia między dobrymi KT88 są małe. |
| **KT120** | 60 W strat, żarzenie 1,7–1,95 A, wyższa (do 144 mm). Mocy w tym układzie prawie nie przybędzie (ogranicza zasilacz i transformator), za to lampa pracuje „na luzie”. Wymaga **S2 8 A** i wyższej osłony (zrobione w v0.4). Do sprawdzenia w karcie KT120: dopuszczalna rezystancja w obwodzie siatki (u nas ok. 120 kΩ; w razie czego R115/R116 → 82k). |

## Przewody (silikonowe)

| Oznaczenie | Napięcie | Do czego |
|---|---|---|
| **UL3239** 3 kV, AWG 20 (0,5 mm²) | wysokonapięciowy | anody KT88, odczepy UL, G2, B+, HT 360 V, dławik |
| **UL3135** 600 V, AWG 16 (1,3 mm²) | | żarzenie KT88, głośniki |
| **UL3135** 600 V, AWG 20 (0,5 mm²) | | bias, żarzenie małych lamp, 230 V do IRM |
| **UL3135** 600 V, AWG 24 (0,2 mm²) | | sterowanie, pomiary, J10, J4 |
| SiF / SIHF 0,75–1 mm² | 300/500 V | sieć 230 V |
| żółto-zielony 1–1,5 mm² | | PE |
| ekranowana skrętka 2 × 0,25 mm² | | sygnał wejściowy (nie silikon) |

Kolory: czerwony = B+, pomarańczowy = anody, żółty = UL/G2, niebieski = bias, czarny = masa, biały/szary = żarzenie. Na przejściach przez blachę dawaj przelotki, bo izolacja silikonowa jest miękka.

## Transformatory (Toroidy.pl)

- **TR1:** 400 VA, S2 zamówić na **8 A** (patrz [zasilanie](02-zasilanie.md)).
- **L1:** 12 H / 400 mA / 66,5 Ω.
- **TG:** TTG-KT88PP 4 kΩ UL. Zapytać o dopuszczalną różnicę prądów stałych w parze (ΔI).
