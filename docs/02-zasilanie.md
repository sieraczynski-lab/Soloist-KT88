# 2. Zasilanie i transformatory

![Schemat zasilacza](img/schemat_zasilacz.png)

## TR1: toroid sieciowy 400 VA (Toroidy.pl)

| Uzwojenie | Napięcie | Prąd | Do czego |
|---|---|---|---|
| Pierwotne | 230 V | | z ekranem elektrostatycznym |
| S1 anodowe | 360 V AC | 0,65 A | mostek UF5408, B+ ok. 465 V; opcjonalny odczep 345 V, gdyby B+ wyszło powyżej 480 V |
| S2 żarzenie mocy | 6,3 V | **8 A** (zalecane zamiast 7 A) | 4× KT88 = 6,4 A; 4× KT120 = 7,2–7,8 A |
| S3 żarzenie sygnałowe | 6,3 V | 3 A | 2× EF86 + 2× E88CC = 1 A, podniesione do +42 V |
| S4 bias | 65 V AC | 50 mA | szyna biasu ok. −80 V |

**S2 na 8 A:** różnica w cenie jest pomijalna, a później można włożyć KT120 bez wymiany transformatora. Przy KT88 żarzenie wyjdzie ok. 6,4–6,5 V, co mieści się w tolerancji (±10%).

W obudowie toroid sieciowy i dławik leżą jeden na drugim, ze środkami zalanymi żywicą.

### Zamówienie TR1 w konfiguratorze Toroidy.pl

Toroidy.pl nawijają transformator dedykowany według własnych parametrów. Do konfiguratora:

| Uzwojenie | Napięcie (pod obciążeniem) | Prąd | Uwagi |
|---|---|---|---|
| Pierwotne | 230 V | – | **ekran elektrostatyczny** z osobnym wyprowadzeniem do PE |
| S1 anodowe | **360 V + odczep 345 V** | 0,65 A | mostek UF5408 → B+ ok. 465 V |
| S2 żarzenie KT88 | 6,3 V | 8 A | zapas na KT120 |
| S3 żarzenie sygnałowe | 6,3 V | 3 A | zapas na 6CG7 (1,6 A), patrz [warianty lamp](12-warianty-lamp.md) |
| S4 bias | 65 V | 50 mA | szyna ok. −80 V |

Moc 400 VA. Obciążenie znamionowe wychodzi ok. 310 VA (S1 234 VA, S2 50 VA, S3 19 VA, S4 3 VA).

Przed zamówieniem:

1. **Zmierz napięcie sieci w domu.** W Polsce często jest 235–245 V, a nie 230 V. Przy 240 V S1 da ok. 375 V i B+ wyjdzie ok. 485 V. Wtedy użyj odczepu 345 V.
2. **Zapytaj o napięcia bez obciążenia.** Producent podaje napięcia przy obciążeniu znamionowym, a bez obciążenia toroid 400 VA daje kilka procent więcej. Na tej podstawie sprawdź zapas C1/C2 (2× 400 V szeregowo) przy wysokim napięciu sieci; szacunek to ok. 560 V.
3. **Obniżona indukcja (wersja „audio”)**, jeśli konfigurator ją oferuje. Mniej buczenia mechanicznego, mniejsze pole rozproszenia (obok są toroidalne TG) i mniejszy prąd załączenia. Kosztem jest większy rozmiar.
4. **Wymiary.** Model obudowy zakłada TR1 ⌀130 × 65 mm na dławiku ⌀105 × 55 mm, wysokość komory do Z 156. Przy obniżonej indukcji 400 VA może wyjść większy, więc poproś o wymiary przed zamówieniem.
5. **Izolacja.** S1 względem pozostałych uzwojeń i rdzenia z próbą co najmniej 2–3 kV. Wyprowadzenia S1 i odczepu 345 V w izolacji wysokonapięciowej, wyraźnie oznaczone.
6. **Wyprowadzenia** długości 30–40 cm, z opisanymi kolorami lub etykietami. Zapytać o fazę uzwojeń.
7. **Montaż:** środek zalany żywicą i komplet podkładek gumowych. Śruba przez TR1 i dławik nie może łączyć się z obudową z obu stron (zwój zwarty).
8. **Bezpiecznik termiczny** w uzwojeniu jako opcja. F1 i F3 już są, więc nie jest konieczny.

W tym samym zamówieniu: dławik L1 i 2× TTG-KT88PP (pytania w [do zrobienia](10-do-zrobienia.md#zamówienia)).

## Dławik L1

Toroidalny **12 H / 400 mA, DCR 66,5 Ω** (Toroidy.pl). Przy ok. 0,33 A spadek na nim to ok. 22 V. Do sprawdzenia u producenta: czy indukcyjność jest podana przy prądzie stałym.

## Przekaźniki i miękki start

| Przekaźnik | Funkcja |
|---|---|
| K1 | sieć do TR1 przez R_SS (47 Ω 10 W) |
| K2 (+1,5 s) | zwiera R_SS |
| K3 (+45 s) | 360 V AC do mostka, dwa styki szeregowo, przez R_IN |
| K4 (+1,5 s) | zwiera R_IN (100 Ω 10 W) |

Wszystkie to **Omron G2RL-2-DC12** (LCSC C61458). K1, K2 i K4 mają oba styki równolegle.

R_IN zmieniony z 47 na **100 Ω**: udar ładowania C1 przez styki K3 wynosi teraz ok. 5 A zamiast 11 A, przy przekaźniku na 8 A.

## Szyna biasu

65 V AC → mostek 1N4007 → C141 100 µF → **R142 1k** → C142 100 µF, co daje ok. **−80 V** przy obciążeniu ok. 7,3 mA (4 sieci biasu, pomiar i automatyczna korekta). Przy sieci −10% wychodzi −71 V, przy +10% −89 V.

R142 zmieniony z 1k5 na 1k, bo korekta biasu dodatkowo obciąża szynę (ok. 0,9 mA na lampę).

## Zabezpieczenia

| | Wartość | Gdzie | Uwagi |
|---|---|---|---|
| F1 | T2,5A 5×20 | gniazdo IEC | zwłoczny |
| F2 | T500mA 5×20 | zasilacz_siec | osobno dla IRM-15-12 (standby) |
| F3 | T1A, **min. 400 V AC** | zasilacz_siec, w uzwojeniu S1 | oprawka też min. 400 V; w LCSC brak, więc TME |
| LED HV | D13 + 2× 220k | zasilacz_hv | świeci, dopóki na kondensatorach jest napięcie |
| Rezystory upływowe | R3–R6 150k 1 W | zasilacz_hv | rozładowanie i wyrównanie napięć C1/C2 |
| R127 | 100 Ω 2 W | wtórne każdego TG | transformator nigdy nie pracuje bez obciążenia |

Odstęp 230 V / HV od strony 12 V na płytkach: **≥ 6 mm**. Na płytce sterowania strefa 230 V (IRM-15-12) ma ≥ 7,9 mm.

## Masa

Masa gwiazdowa w **J15 (GND_STAR) na płytce zasilacza HV**. Każda płytka ma do niej osobny przewód 1 mm². Masa sterowania łączy się z masą wzmacniacza tylko tam.

## Żarzenie

- **KT88:** S2, sztuczny środek R11/R12 do masy. Przewody 1–1,5 mm², skręcone parami, przy samym dnie.
- **EF86/E88CC:** S3, sztuczny środek R13/R14 podniesiony do +42 V (dzielnik R140A/B + R141 z B+3, C140 47 µF).
