# 12. Warianty lamp (opcjonalne)

Podstawowa wersja to **EF86 + E88CC + KT88** i płytka kanału jest pod nią poprowadzona. Wszystko poniżej to opcje do porównania albo na wypadek problemów z dostępnością. Żadna nie wymaga zmian w PCB, zmieniają się co najwyżej wartości elementów.

Wartości są policzone z modelu lampy (prawo 3/2 dopasowane do danych katalogowych), nie zmierzone. Po każdej zmianie: punkty pracy według [uruchomienia](06-uruchomienie.md), potem faza i głębokość sprzężenia zwrotnego i prostokąt.

## EF86 (V101): zamienniki bez zmian wartości

| Lampa | Uwagi |
|---|---|
| **6Ж32П (6Zh32P)** | radziecki bezpośredni odpowiednik, tani, łatwo dostępny |
| **JJ EF806S** | nowa produkcja, solidna konstrukcja, mało mikrofonuje |
| Electro-Harmonix EF86 | nowa produkcja |
| NOS Mullard / Telefunken / Siemens | drogie; różnice głównie w szumie i mikrofonowaniu |

Słaby punkt EF86 to **szum i mikrofonowanie**:

- kup 3–4 sztuki i wybierz najcichszą: przy podkręconej głośności, bez sygnału, postukaj ołówkiem w bańkę; dobra lampa prawie nie dzwoni,
- podstawka z ekranem i silikonowy pierścień tłumiący na bańkę,
- EF86 jak najdalej od TR1, dławika i TG, bo ich drgania przenoszą się na lampę.

## E88CC (V102, LTP): opcje

### A. E88CC z mniejszym obciążeniem (zalecane)

Obecnie E88CC traci ok. 1,3 W na sekcję przy dopuszczalnych 1,5 W (87%). E88CC to lampa z siatką ramkową i w takich warunkach żyje krócej.

| | Obecnie | Wariant A |
|---|---|---|
| Prąd ogona (P101) | 14 mA | **12 mA** |
| R111, R112 | 27k 5 W | **33k 5 W** (1,2 W strat) |
| Anody | ok. 271 V | ok. 262 V |
| Uak | ok. 184 V | ok. 175 V |
| Strata na sekcję | ok. 1,3 W (87%) | **ok. 1,05 W (70%)** |
| Q101 | ok. 1,2 W | ok. 1,05 W |

Wzmocnienie LTP praktycznie się nie zmienia (obciążenie AC 33k ∥ ok. 127k zamiast 27k ∥ 127k). Do pełnego wysterowania KT88 (ok. 50 V szczytowo) potrzeba ok. 2 mA zmiany prądu na sekcję, więc 6 mA spoczynkowo wystarcza z zapasem. Sprawdź, że zakres P101 obejmuje 12 mA.

Zamienniki E88CC bez zmian: **6922, 6N23P-EV (6Н23П-ЕВ)**. Nie zwykła ECC88 / 6DJ8 (katalogowo ok. 130 V Uak).

### B. 6CG7 zamiast E88CC

6CG7 to nowalowy odpowiednik 6SN7. Ma **ten sam układ nóżek co E88CC** (1–8 identycznie, nóżka 9 niepodłączona, w E88CC to ekran), więc wchodzi do tej samej podstawki. Zapas mocy anody jest kilkukrotny (r-type.org podaje 5 W), a Ua max 300 V.

| | Wariant B (6CG7) |
|---|---|
| Prąd ogona (P101) | **16 mA** (8 mA na sekcję) |
| R111, R112 | 27k 5 W, bez zmian |
| Anody / katody | ok. 244 V / ok. 85 V |
| Uak | ok. 159 V |
| Strata na sekcję | ok. 1,27 W |
| Q101 | ok. 1,4 W (radiator 10 K/W wystarcza) |
| Żarzenie S3 | 2× EF86 + 2× 6CG7 = **1,6 A** (S3 ma 3 A) |
| Wzmocnienie LTP | ok. **5,7 dB mniej** (μ ok. 20 zamiast ok. 33) |

Bo wzmocnienie spada, przy tym samym R104 sprzężenie zwrotne zmaleje z 14–16 dB do ok. 10–11 dB. Żeby je zachować, **R104 ok. 14k** (zamiast 27k) i **C103 ok. 220 pF** na start (ta sama stała czasowa), potem dobór na oscyloskopie. Czułość wyjdzie ok. **300 mV**, co przy źródłach 2 V i drabince głośności nie przeszkadza.

**Nie wkładaj ECC82 / 12AU7 / 6N1P zamiast E88CC bez sprawdzenia karty.** W ECC82 nóżka 9 to odczep środkowy żarzenia, a nie ekran; przy żarzeniu podniesionym do +42 V może to narobić szkód. 6FQ7 ma inny kod podstawy (9LP) niż 6CG7 (9AJ), więc przed użyciem sprawdź nóżkę 9 w karcie.

## Głębsze sprzężenie zwrotne (z dowolnym wariantem)

Czułość ok. 160 mV przy źródłach 2 V oznacza ok. 20 dB nadmiaru wzmocnienia, który drabinka głośności i tak zjada. Część tego zapasu można zamienić na sprzężenie zwrotne:

| | Obecnie | Opcja |
|---|---|---|
| NFB | 14–16 dB | **ok. 20 dB** |
| R104 (z E88CC) | 27k | **ok. 14k** |
| C103 | 120 pF | **ok. 220 pF** na start |
| Czułość | ok. 160 mV | ok. 290 mV |

Korzyści: niższa impedancja wyjściowa (mniejszy wpływ dołka 2,5 Ω przy 160 Hz w kolumnach), mniej szumu i mikrofonowania EF86, mniejsze zniekształcenia. Warunek: stabilność potwierdzona prostokątem 1 i 10 kHz na 4 Ω, na 4 Ω ∥ 1 µF i bez obciążenia (tylko R127). Jeśli pojawi się dzwonienie, którego C103 nie usuwa, wróć do mniejszej głębokości albo użyj opcjonalnej sieci R128/C107.

Wartości to szacunek: rzeczywista głębokość zależy od wzmocnienia bez pętli, które trzeba zmierzyć (krok „Głębokość NFB” w uruchomieniu).

## KT88 (V103, V104): zamienniki

| Lampa | Uwagi |
|---|---|
| **KT120** | opisana w [częściach](08-czesci-i-zakupy.md#lampy); wymaga S2 8 A i wyższej osłony (jest w v0.4) |
| **6550 / 6550A** | ten sam cokół i żarzenie 1,6 A; punkt pracy 465 V / 55 mA mieści się w danych 6550A; bias trzeba ustawić od nowa |
| **KT150** | duża bańka i większe żarzenie (sprawdź w karcie, ok. 1,75 A na lampę, czyli ok. 7 A z S2 8 A); sprawdź wysokość i średnicę względem osłony |

Przy każdej zamianie: potencjometry biasu na maksimum przed pierwszym włączeniem, korekta ESP32 do ponownej kalibracji.
