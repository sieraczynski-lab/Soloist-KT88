# 11. Selektor wejść i przekaźnikowa regulacja głośności (TubeSel)

Płytka `selektor`: przełączanie 4 wejść stereo, regulacja głośności drabinką przekaźnikową 0–63 dB co 1 dB i wyciszanie (mute) typu fail-safe. Sterowanie po I²C z ESP32-S3 płytki [`sterowanie`](03-sterowanie.md), który odpowiada też za bias, sekwencję włączania i pomiary.

Wersja płytki: **v0.5** (schemat gotowy, elementy rozmieszczone, **ścieżki do poprowadzenia**).

| Gdzie | Co |
|---|---|
| [`hardware/selektor/kicad/`](../hardware/selektor/kicad/) | projekt KiCad 8/9, BOM-y (`BOM.csv`, `JLCPCB_BOM.csv`, `LCSC_zamowienie.csv`) |
| [`hardware/selektor/kicad5-easyeda/`](../hardware/selektor/kicad5-easyeda/) | ten sam projekt w KiCad 5.1 do importu w EasyEDA Pro |
| [`src/selektor/`](../src/selektor/) | generator i weryfikacja (Python) |

Selektor powstał w osobnej sesji niż reszta wzmacniacza. Punkty styku z płytką sterowania są opisane w [7.5](#75-integracja-z-płytką-sterowania).

---

## Spis treści

1. [Założenia](#1-założenia)
2. [Decyzje projektowe](#2-decyzje-projektowe)
3. [Schemat blokowy](#3-schemat-blokowy)
4. [Selektor wejść](#4-selektor-wejść)
5. [Drabinka głośności](#5-drabinka-głośności)
6. [Mute](#6-mute)
7. [Sterowanie: MCP23017 + ULN2803](#7-sterowanie-mcp23017--uln2803)
8. [Zasilanie](#8-zasilanie)
9. [Masy, ekranowanie i montaż we wzmacniaczu](#9-masy-ekranowanie-i-montaż-we-wzmacniaczu)
10. [Dopasowanie poziomów do wzmacniacza (EF86)](#10-dopasowanie-poziomów-do-wzmacniacza-ef86)
11. [Firmware ESP32](#11-firmware-esp32)
12. [Przekaźniki Omron G6K-2F-Y](#12-przekaźniki-omron-g6k-2f-y)
13. [Płytka PCB](#13-płytka-pcb)
14. [Zamawianie: JLCPCB i LCSC](#14-zamawianie-jlcpcb-i-lcsc)
15. [Montaż ręczny i uruchomienie](#15-montaż-ręczny-i-uruchomienie)
16. [Import do EasyEDA Pro](#16-import-do-easyeda-pro)
17. [Weryfikacja projektu](#17-weryfikacja-projektu)
18. [Otwarte punkty](#18-otwarte-punkty)
19. [Historia wersji](#19-historia-wersji)
20. [Źródła](#20-źródła)

---

## 1. Założenia

| Parametr | Wartość |
|---|---|
| Wejścia | 4 × stereo, poziom liniowy (RCA na tylnej ściance, kablem ekranowanym do płytki) |
| Regulacja głośności | pasywna drabinka przekaźnikowa, 6 bitów: 0–63 dB, krok 1 dB |
| Impedancja wejściowa | ok. 10 kΩ, stała niezależnie od ustawienia (9,6–10,8 kΩ) |
| Wyciszenie | przekaźnik zwierający wyjście do masy, aktywny bez zasilania (fail-safe) |
| Sterowanie | I²C (MCP23017), adres 0x20–0x27 ustawiany zworkami |
| Zasilanie | tylko +12 V (cewki przekaźników); 3,3 V z modułu DC-DC na płytce |
| Płytka | 96 × 74 mm (limit 100 × 100 mm), 2 warstwy, SMD jednostronnie |
| Źródła | DAC / streamer ok. 2 V (Raspberry Pi + ES9038Q2M, WiiM Ultra), pre-out Marantz SR7013 ok. 1,2 V, starsze źródła 0,3–1 V (rozdz. 10) |
| Wzmacniacz | stopień wejściowy EF86, pełna moc ok. 45 W / 4 Ω przy ok. 160 mV (dobierana R104), wejście 220 kΩ |
| Obsługa | pilot IR + enkoder (wejście, głośność); EQ i barwa w aplikacji/RPi |

## 2. Decyzje projektowe

### 2.1 Przekaźniki zamiast scalaków

Styk przekaźnika sygnałowego ma praktycznie zerowe zniekształcenia, daje pełną separację i nie ogranicza amplitudy sygnału. Przy lampowym torze to najczystsze rozwiązanie. Rozważane alternatywy scalone:

| Układ | Funkcja | Dlaczego nie |
|---|---|---|
| CD4052 / CD4053 | multiplekser analogowy | przeciętne parametry, ograniczony zakres napięć |
| ADG1409, ADG1208, DG409/DG411 | precyzyjne multipleksery CMOS | dobre przy ±12–15 V, ale wymagają zasilania symetrycznego; rezystancja włączenia zależy od sygnału |
| NJW1194 / NJW1195 | selektor + głośność (+ barwa) | bardzo dobre, ale niskonapięciowe zasilanie symetryczne i niepewna dostępność |
| PT2314, TDA7439, TDA7318 | procesory audio I²C | poprawne, nie audiofilskie |
| PGA2311, MUSES72323 | sama głośność, najwyższa półka | osobne czyste zasilanie symetryczne |
| Rohm BD37534 / BD37033 | selektor + głośność + barwa | półprzewodnik w torze; zasilanie 8–10 V |

Przekaźniki mocy (np. Songle SRD-05VDC z gotowych modułów) **nie nadają się**: przy sygnałach rzędu mV ich styki utleniają się i zaczynają trzeszczeć (*dry switching*). Potrzebne są przekaźniki sygnałowe ze złoconymi stykami: Omron G6K/G6S/G6H, Panasonic TQ2/TX2, Axicom IM, a w ostateczności G5V-2.

### 2.2 Bez EQ i barwy we wzmacniaczu

EQ, korekcja barwy i pomieszczenia są robione cyfrowo w źródle (w Raspberry Pi np. **CamillaDSP**, wbudowany w moOde Audio; w WiiM w aplikacji). Analogowy procesor (NJW1194, ADAU1701) z przekaźnikiem bypass byłby duplikacją kosztów, a ADAU1701 dodałby przetwarzanie A/C–C/A do lampowego toru. We wzmacniaczu zostaje czysty tor: selektor → drabinka → lampy.

**Ważne:** w DAC-u / streamerze głośność ustaw na stałe na 0 dB (WiiM: Fixed Volume), a reguluj tylko drabinką. Dwie regulacje głośności tylko by przeszkadzały, a cyfrowe ściszanie traci rozdzielczość.

### 2.3 Drabinka zamiast potencjometru

Pasywny tłumik przekaźnikowy typu series-shunt o stałej impedancji: brak półprzewodnika w torze, brak dodatkowego zasilania, identyczne kanały (rezystory 0,1%), łatwe sterowanie liczbą 0–63.

### 2.4 Krok 1 dB, nie 0,5 dB

Rozważano dodatkowy bit 0,5 dB. Odrzucony, bo:
- 1 dB to granica słyszalności przy kręceniu, odbierana jako płynna regulacja;
- przy rezystorach dostępnych w magazynie JLCPCB rzeczywiste kroki 1 dB mają 0,69–1,17 dB; bit 0,5 dB dałby nierówne kroki ok. 0,2–0,8 dB;
- kosztuje przekaźnik, 2 nowe wartości rezystorów (ok. 6 USD opłat w JLCPCB) i więcej klikania.

Wolny pin na bit 0,5 dB jest (GPB3), więc można go dodać w przyszłej wersji. Więcej daje wygodne sterowanie w firmware (rozdz. 11).

### 2.5 Sterowanie I²C na płytce

MCP23017 i dwa ULN2803 są na płytce selektora: do ESP32 idzie jeden kabel 6-żyłowy (12 V, masa, I²C). Sam MCP23017 nie wysteruje cewek 12 V (wyjścia 3,3 V), a sam ULN2803 ma tylko 8 kanałów, przy 11 cewkach.

### 2.6 Platforma firmware: pioarduino zamiast ESPHome

ESPHome wystarczyłby do samego selektora, ale wzmacniacz potrzebuje pilnowania biasu i wysokiego napięcia, sekwencji włączania i ścisłego timingu przekaźników (rozdz. [3](03-sterowanie.md)). Rekomendacja: **pioarduino** (społecznościowa kontynuacja PlatformIO dla ESP32 z Arduino Core 3.x / ESP-IDF 5.x; wspiera ESP32-S3). Szczegóły w rozdz. 11.

## 3. Schemat blokowy

```
 IN1 ─┐                                                               ┌─► do siatki EF86
 IN2 ─┤  K1..K4          K5   K6   K7   K8   K9   K10      K11       │   (C101 47 nF, R101 220 kΩ)
 IN3 ─┼─[selektor]─BUS─[-1]─[-2]─[-4]─[-8]─[-16]─[-32]─OUT─[mute]──J5┘
 IN4 ─┘   NC: 1k→GND                         R33/R34 10k→GND  (OFF = zwarcie do GND)
            ▲                ▲ cewki 12 V (pin 1 = +12 V)        ▲
            └────────── U2, U3: ULN2803 (diody w środku) ─────────┘
                                  ▲ DRV1..DRV11
                         U1: MCP23017 (I²C 0x20, 3,3 V)
                                  ▲ SDA/SCL
   J6 (JST XH 6p): +12V, DGND, n/c, SDA, SCL, DGND ──► płytka sterowania (ESP32-S3)
   U4: moduł DC-DC 12 V → 3,3 V
```

## 4. Selektor wejść

- Jeden przekaźnik DPDT na wejście: jedna sekcja kanał L, druga kanał R.
- Połączenia styków: **COM = wejście**, **NO = wspólna szyna BUS**, **NC = rezystor 1 kΩ do masy**.
- Wejście niewybrane jest obciążone 1 kΩ, co poprawia przesłuch i rozładowuje pojemności kabla. Źródło nigdy nie jest zwierane do masy.
- Nigdy nie załączaj dwóch wejść naraz. Firmware najpierw wyłącza wszystkie, potem włącza wybrane (rozdz. 11).

## 5. Drabinka głośności

### 5.1 Zasada działania stopnia

Jeden przekaźnik DPDT na bit, jedna sekcja na kanał. Każda sekcja to jeden styk przełączny:

```
 WE ──┬──[ Rs ]──┬── WY (do następnego stopnia)
      │          │
      └── NC     COM
                 │
          NO ──[ Rp ]── masa
```

- **Cewka wyłączona:** NC zwiera Rs, Rp wisi w powietrzu, stopień przepuszcza bez tłumienia.
- **Cewka włączona:** Rs jest w szeregu, Rp idzie do masy, stopień tłumi o swoją wartość dB.

Każdy stopień obciążony impedancją Z sam przedstawia impedancję Z, więc kolejność stopni nie ma znaczenia, a źródło zawsze widzi ok. 10 kΩ.

### 5.2 Wartości (v0.4 i nowsze)

Dobrane z rezystorów cienkowarstwowych **0,1%, 0805**, dostępnych w magazynie JLCPCB/LCSC (stan z 22.10.2026, każda wartość ≥ 500 szt.). Optymalizacja łączna dla wszystkich 64 kodów:

| Bit | Przekaźnik | Rs | Rp | LCSC Rs | LCSC Rp |
|---|---|---|---|---|---|
| −1 dB | K5 | 1,10 kΩ | 80,6 kΩ | C473284 | C728657 |
| −2 dB | K6 | 2,00 kΩ | 32,4 kΩ | C479096 | C149970 |
| −4 dB | K7 | 3,75 kΩ | 17,4 kΩ | C374641 | C47115938 |
| −8 dB | K8 | 6,20 kΩ | 6,81 kΩ | C326695 | C728655 |
| −16 dB | K9 | 9,10 kΩ | 2,00 kΩ | C21571502 | C479096 |
| −32 dB | K10 | 10,0 kΩ | 270 Ω | C110775 | C351587 |
| terminator | R33, R34 | 10,0 kΩ do masy | | C110775 | |

- **Terminator 10 kΩ na wyjściu jest wymagany.** Bez niego tłumienia się nie zgadzają.
- Błąd tłumienia: **≤ 0,205 dB** dla wszystkich 64 kodów (bez obciążenia), **≤ 0,26 dB** z wejściem wzmacniacza 220 kΩ. Rzeczywiste kroki: 0,69–1,17 dB. Niesłyszalne przy kroku 1 dB.
- **Balans L/R** nie zależy od doboru wartości: oba kanały mają identyczne rezystory, dobrane z dokładnością 0,1%.
- Impedancja wejściowa: 9,6–10,8 kΩ. Impedancja wyjściowa: najwyżej ok. 3,2 kΩ.
- Wartości 2,00 kΩ i 10,0 kΩ występują w dwóch miejscach (10,0 kΩ także jako terminator), więc jest tylko **11 unikalnych rezystorów 0,1%** (mniej opłat w JLCPCB).

**Historia doboru wartości:** v0.1 zakładało szereg E96 (błąd do 0,18 dB), potem E192 (błąd 0,016 dB), ale tych wartości w 0,1% nie było w JLCPCB. Obecne wartości to kompromis: wszystko z magazynu, błąd ≤ 0,21 dB.

### 5.3 Przełączanie bez skoków głośności

Przy zmianie np. z 31 na 32 dB zmienia się 6 bitów naraz. Gdyby przekaźniki puściły w złej kolejności, przez kilka ms byłoby głośno. Reguła:

> **Najpierw ZAŁĄCZ bity, które mają się włączyć, odczekaj ok. 5 ms, dopiero potem WYŁĄCZ te, które mają zgasnąć.**

Przejście idzie wtedy zawsze przez stan cichszy. G6K przełącza w ok. 3 ms.

## 6. Mute

- Przekaźnik **K11**: obie sekcje w spoczynku (NC) zwierają wyjście L i R do masy.
- **Cewka bez prądu = cisza.** Dźwięk jest dopiero po załączeniu K11 (GPB2 = 1).
- Przy starcie, zaniku 12 V, resecie lub zawieszeniu ESP32 wzmacniacz milczy.
- ESP32 trzyma mute, dopóki lampy się nie nagrzeją i bias nie będzie w normie, oraz włącza go przy wyłączaniu i przy wykryciu błędu (np. odjazd biasu).

> Uwaga: w przykładzie ESPHome z początku projektu mute działał odwrotnie (włączony przekaźnik = cisza). W sprzęcie v0.2+ obowiązuje logika fail-safe opisana powyżej.

## 7. Sterowanie: MCP23017 + ULN2803

### 7.1 Przypisanie wyjść

| Wyjście MCP23017 | ULN | Przekaźnik | Funkcja |
|---|---|---|---|
| GPA0–GPA3 | U2 IN1–4 | K1–K4 | wejście 1–4 |
| GPA4 | U2 IN5 | K5 | −1 dB |
| GPA5 | U2 IN6 | K6 | −2 dB |
| GPA6 | U2 IN7 | K7 | −4 dB |
| GPA7 | U2 IN8 | K8 | −8 dB |
| GPB0 | U3 IN1 | K9 | −16 dB |
| GPB1 | U3 IN2 | K10 | −32 dB |
| GPB2 | U3 IN3 | K11 | mute (1 = dźwięk) |
| GPB3–GPB7 | — | — | wolne (wejścia U3 IN4–8 do masy) |

Stan wysoki na wyjściu = cewka załączona. Kod głośności `n` (0–63) to tłumienie `n` dB: bity 0–3 kodu → GPA4–GPA7, bity 4–5 → GPB0–GPB1.

W nowszych egzemplarzach MCP23017 piny GPA7 i GPB7 działają tylko jako wyjścia, co tu nie przeszkadza.

### 7.2 I²C

- Adres: **SJ1–SJ3 otwarte = 0x20**. Zwarcie SJn ustawia bit An (0x20–0x27). Na magistrali płytki sterowania są już ADS1115 (0x48, 0x49), MCP4728 (0x60) i wyświetlacz I²C, więc 0x20 nie koliduje.
- Pull-upy **4,7 kΩ (R36, R37)** do 3,3 V płytki. Płytka sterowania ma swoje 4,7 kΩ (R9, R10); razem wychodzi ok. 2,35 kΩ, co jest w porządku dla 100–400 kHz.
- Kabel do ok. 30–50 cm przy 100 kHz działa bez problemu. Przy dłuższym kablu lub zakłóceniach pomogą rezystory szeregowe ok. 100 Ω na SDA/SCL po stronie ESP32.
- RESET MCP23017 jest na stałe podłączony do 3,3 V (wiszący powodowałby losowe resety).

### 7.3 Złącze J6 (JST XH 6p)

| Pin | Sygnał |
|---|---|
| 1 | +12 V |
| 2 | DGND |
| 3 | **niepodłączony** |
| 4 | SDA |
| 5 | SCL |
| 6 | DGND |

Pin 3 celowo nie jest podłączony: **nie łącz 3,3 V z ESP32 z 3,3 V tej płytki** (dwa źródła napięcia walczyłyby ze sobą). Masa ESP32 musi być wspólna z DGND. Pin 3 jest kandydatem na linię MUTE z płytki sterowania (7.5).

### 7.4 ULN2803

- **U2, U3: UTC ULN2803G-S18-R** (LCSC C33924, SOP-18 300 mil). Pasuje każdy ULN2803 w SOIC-18 szerokim (300 mil; norma JEDEC MS-013 przewiduje SOIC-18 z rastrem 1,27 mm tylko w tej szerokości). Pierwotnie ULN2803ADWR od TI, wymieniony ze względu na cenę (ok. 6 USD wobec 0,29 USD).
- **COM → +12 V**: wbudowane diody gaszą przepięcia cewek, więc nie ma osobnych diod (były w v0.1).
- Wejścia z rezystorem 2,7 kΩ wysterowane 3,3 V dają prąd bazy wystarczający dla cewek ok. 9 mA (ULN2803 wytrzymuje do 500 mA na kanał).
- Prąd cewek: 11 × ok. 9 mA, czyli do ok. 100 mA przy wszystkich włączonych.

### 7.5 Integracja z płytką sterowania

Płytka [`sterowanie`](03-sterowanie.md) (v0.23) powstała niezależnie od selektora. Stan na dziś i propozycje:

1. **Brak złącza dla selektora.** Sterowanie ma I²C tylko na złączu wyświetlacza J8 (3V3, GND, SCL, SDA), a +12 V na złączach przekaźników. Propozycja: dodać na płytce sterowania złącze JST XH 6p zgodne z J6 selektora (1 +12 V, 2 GND, 3 MUTE, 4 SDA, 5 SCL, 6 GND). Do tego czasu kabel można złożyć z J8 (SDA, SCL, GND) i +12 V z J3/J13.
2. **Wyjście MUTE (ULN kanał 5, GPIO14, złącze J3 „przekaźnik MUTE w przedwzmacniaczu”)** jest przewidziane właśnie dla selektora. Dwie możliwości:
   - **(a) obecnie, bez zmian w płytkach:** K11 sterowany przez MCP23017 (GPB2). J3 na sterowaniu zostaje wolne.
   - **(b) propozycja do decyzji:** w selektorze połączyć J6 pin 3 z linią COIL11 (cewka K11). Wtedy K11 może załączyć zarówno MCP23017, jak i ULN płytki sterowania (wyjścia z otwartym kolektorem, połączone równolegle). Firmware zostawia GPB2 = 0, a dźwięk włącza GPIO14. Zaleta: przy resecie lub zawieszeniu ESP32 GPIO14 puszcza, ULN się wyłącza i **wyjście od razu się wycisza**. W wariancie (a) MCP23017 trzyma ostatni stan wyjść, dopóki ma zasilanie, więc zawieszony ESP32 nie wyciszy wzmacniacza.
   - Uwaga na nazewnictwo: w tym układzie **aktywne wyjście ULN = dźwięk** (cewka K11 załączona = brak zwarcia do masy). W firmware sygnał MUTE z [3](03-sterowanie.md) musi więc być odwrócony: „MUTE aktywny” = GPIO14 w stanie niskim.
3. **Budżet 12 V:** selektor pobiera do ok. 100 mA (wszystkie przekaźniki) + kilka mA na 3,3 V. Zasilacz IRM-15-12 ma 1,25 A; sprawdź sumę z resztą przekaźników wzmacniacza.

## 8. Zasilanie

- Do płytki dochodzi **tylko +12 V** (z zasilacza wzmacniacza, osobna linia, nie z 3,3 V).
- **U4: miniaturowy moduł DC-DC 12 V → 3,3 V** (wersja ze stałym wyjściem 3,3 V). Pinout: 1 −IN, 2 +IN, 3 OUT+, 4 OUT−. Rozstaw wyprowadzeń 14,17 × 8,24 mm (557,9 × 324,4 mil). Pobór z 3,3 V: kilka mA (MCP23017 + pull-upy).
- Footprint modułu (`TubeSel:DCDC_Mini_4pin_14.17x8.24mm`) odwzorowano ze zrzutu: otwory 1,0 mm, pady 2,2 mm, obrys 17,6 × 12,2 mm. **Do zmierzenia suwmiarką przed zamówieniem płytek.**
- C3 10 µF + C2 100 nF na +12 V, C4 10 µF + C1 100 nF na 3,3 V.
- Przy tak małym obciążeniu moduł pracuje zwykle impulsowo (burst), czasem w paśmie akustycznym. Moduł siedzi na DGND, z dala od toru audio. Gdyby było słychać „ćwierkanie”: ferryt w linii 3,3 V albo stabilizator 78L33 zamiast modułu.

## 9. Masy, ekranowanie i montaż we wzmacniaczu

### 9.1 Masy na płytce

- **GND (audio)** i **DGND (cyfrowa)** to osobne sieci i osobne strefy miedzi. DGND zajmuje dolny pas pod układami scalonymi i ma wyższy priorytet strefy.
- Prąd cewek wraca przez ULN2803 do DGND, nie przez masę audio.
- **R41 (0 Ω, domyślnie niemontowany)** łączy GND z DGND w jednym punkcie. Zostaw pusty, jeśli masa ESP32 łączy się z masą wzmacniacza w gwieździe gdzie indziej (zalecane). Montuj tylko wtedy, gdy DGND nie ma innego połączenia z masą wzmacniacza.
- **R35 (0 Ω, niemontowany)** łączy masę audio z obudową przez otwór MH1. Montuj tylko, jeśli masa nie jest łączona z obudową w innym miejscu.

### 9.2 Ekranowanie modułu pod lampami

Płytka będzie pod lampami stopnia wejściowego. Zalecenia:

1. **Obudowa:** zamknięte pudełko aluminiowe (np. odlewane Hammond 1590) przykręcone do chassis. Ekranuje pola elektryczne od przewodów anodowych (kilkaset V) i zakłócenia cyfrowe. Masę obudowy łącz z masą sygnałową **w jednym punkcie**, przy gnieździe wejściowym.
2. **Pole magnetyczne** od transformatora i dławików: aluminium go nie zatrzymuje. Pomaga odległość i ustawienie (rdzenie prostopadle do płytki), w ostateczności blacha stalowa lub mu-metal.
3. **Żarzenie:** przewody żarzenia lamp wejściowych skręcaj ciasno i prowadź z dala od płytki. Dla stopnia wejściowego najlepiej żarzenie DC.
4. **Przewody wchodzące do obudowy:** zasilanie i I²C przez filtry (koraliki ferrytowe + kondensatory), sygnał audio przewodem ekranowanym z ekranem podłączonym z jednej strony.
5. **Ciepło:** montuj moduł pod chassis, nie bezpośrednio przy podstawkach. Elektrolity i scalaki na 105 °C.
6. **PCB:** 2 warstwy z możliwie pełną masą na spodzie w części audio, kanały L i R rozdzielone masą.

### 9.3 ESP32 we wzmacniaczu

- ESP32 potrafi „siać” do toru audio: trzymaj moduł z dala od ścieżek sygnałowych, daj mu osobne zasilanie, masę cyfrową łącz z analogową w jednym punkcie (gwiazda).
- **Metalowe chassis tłumi WiFi i Bluetooth.** Płytka sterowania używa ESP32-S3-DevKitC-1. Do sterowania z telefonu lepsza jest wersja z gniazdem antenowym (moduł ESP32-S3-WROOM-1U z U.FL, np. DevKitC-1U) i antena wyprowadzona na zewnątrz, np. przez tylną ściankę. Inaczej łączność będzie zawodna.

## 10. Dopasowanie poziomów do wzmacniacza (EF86)

Dane wzmacniacza ([rozdz. 1](01-uklad.md), [7](07-zrodla-i-poziomy.md)): pełna moc ok. 45 W / 4 Ω przy ok. **160 mV** na wejściu (wartość policzona, dobierana R104, do potwierdzenia pomiarem), impedancja wejściowa **220 kΩ** (R101), filtr ok. 15 Hz (C101 47 nF) chroniący transformator przed infradźwiękami.

### 10.1 Poziomy źródeł

- **2 V RMS** przy pełnym wysterowaniu to norma dla odtwarzaczy CD, przyjęta przez większość DAC-ów. Moduły ES9038Q2M dają zwykle ok. 2 V, niektóre więcej (sprawdzić w opisie modułu).
- Starsze źródła analogowe (magnetofon, tuner, przedwzmacniacz gramofonowy): zwykle 0,3–1 V.

### 10.2 Potrzebne tłumienie

| Źródło | Pełna moc (45 W) | ok. 1 W (głośno w pokoju) | ok. 0,1 W (cicho) |
|---|---|---|---|
| 1 V | 16 dB | 32 dB | 42 dB |
| 2 V (DAC, CD) | 22 dB | 38 dB | 48 dB |
| 2,5 V | 24 dB | 40 dB | 50 dB |

Przy codziennym słuchaniu drabinka pracuje w zakresie ok. 30–50 dB z dostępnych 0–63 dB: zapas na każde rozsądne źródło.

### 10.3 Współpraca z wejściem

- 220 kΩ równolegle z terminatorem 10 kΩ: błąd tłumienia rośnie z 0,20 do 0,26 dB. Bez zmian w projekcie.
- Impedancja wyjściowa drabinki ≤ ok. 3,2 kΩ. EF86 (pentoda) ma małą pojemność Millera, pasmo w górze nie ucierpi; filtr 47 nF / 220 kΩ zostaje praktycznie bez zmian (ok. 15 Hz).
- C101 odcina też ewentualną składową stałą z DAC-a.

### 10.4 Zalecenia

1. **Programowy limit głośności dla każdego wejścia:** przy źródle 2 V tłumienie poniżej ok. 22 dB to już przesterowanie wzmacniacza. Limity z [rozdz. 7](07-zrodla-i-poziomy.md): ok. −19 dB dla 2 V, ok. −15 dB dla pre-outu Marantza (1,2 V), ok. −13 dB dla 1 V, ok. −5 dB dla starszych źródeł. Tam też: poprawka poziomu na wejście, start po przełączeniu wejścia najwyżej z bezpiecznego poziomu (np. −30 dB) i tryb „bypass” dla kina domowego (drabinka na stałym, skalibrowanym poziomie, głośność reguluje amplituner).
2. **Czułość 160 mV jest wysoka** (wzmocnienie ok. 84×, 38 dB). Przy źródle 2 V ok. 22 dB wzmocnienia zawsze „marnuje się” w drabince, a drabinka nie tłumi szumu stopnia EF86. Przy skutecznych kolumnach (> ok. 92 dB) szum może być słyszalny z bliska. Do rozważenia w projekcie wzmacniacza: podniesienie czułości do ok. 0,5–0,8 V głębszym sprzężeniem zwrotnym (zwykle mniejsze zniekształcenia i niższa impedancja wyjściowa), **po sprawdzeniu stabilności pętli z transformatorem**. Drabinka zadziała dobrze w obu przypadkach.

## 11. Firmware ESP32

### 11.1 Platforma

Program ESP32 wzmacniacza nie jest jeszcze napisany ([rozdz. 10](10-do-zrobienia.md)). Poniżej rekomendacje z projektowania selektora.

**pioarduino**: społecznościowy fork platformy espressif32 dla PlatformIO, powstały po sporze Espressif–PlatformIO przy wydaniu Arduino Core 3.0. Oficjalna platforma PlatformIO nie wspiera nowszych wersji core i nowych układów (C6, H2, C5, P4). Ten sam workflow w VS Code, zmiana jednej linii:

```ini
[env:esp32]
platform = https://github.com/pioarduino/platform-espressif32/releases/download/stable/platform-espressif32.zip
board = esp32-s3-devkitc-1
framework = arduino
; opcjonalnie: framework = arduino, espidf
```

### 11.2 Architektura (FreeRTOS)

| Zadanie | Priorytet | Zakres |
|---|---|---|
| Zabezpieczenia | najwyższy | bias, napięcia, timeouty, watchdog |
| Przekaźniki | wysoki | selektor, drabinka, mute; **jedna kolejka komend**, żeby enkoder, pilot i aplikacja sobie nie przeszkadzały |
| Wejścia | średni | enkoder (sprzętowy licznik **PCNT**, bez gubienia kroków), pilot IR (moduł **RMT**, odbiornik TSOP) |
| WiFi | najniższy | serwer WWW/WebSocket do aplikacji, opcjonalnie MQTT do Home Assistant |

- Pomiary biasu: **zewnętrzny przetwornik ADS1115** (I²C), tak jak na płytce sterowania. Wbudowany ADC ESP32 jest nieliniowy i zaszumiony.
- **Zabezpieczenia krytyczne także sprzętowo** (bezpieczniki, ewentualnie komparator odcinający anodowe). ESP32 może się zawiesić. Progi i reakcje programowe: [rozdz. 3](03-sterowanie.md#zabezpieczenia-programowe).

### 11.3 Sekwencje

**Start:** po resecie MCP23017 ma wszystkie piny jako wejścia, więc wszystkie przekaźniki są wyłączone: żadne wejście nie jest wybrane, **drabinka stoi na 0 dB (pełna głośność)**, mute aktywny. Kolejność w firmware:
1. Skonfiguruj piny jako wyjścia z mute = 0.
2. Ustaw tłumienie (np. ostatnie zapamiętane, nie mniejsze niż limit z 10.4) i wejście.
3. Poczekaj, aż lampy się nagrzeją i bias będzie w normie (sekwencja w [rozdz. 3](03-sterowanie.md#sekwencja-włączania)).
4. Zdejmij mute (GPB2 = 1). Opcjonalnie płynne narastanie głośności od cichej do zapamiętanej przez ok. 1 s.

**Zmiana wejścia:** mute (GPB2 = 0) → ok. 50 ms → wyłącz wszystkie K1–K4 → włącz wybrany → ok. 100 ms → zdejmij mute.

**Zmiana głośności:** najpierw załącz nowe bity, ok. 5 ms, potem wyłącz zbędne (rozdz. 5.3).

**Wyłączanie / błąd:** natychmiast mute.

### 11.4 Wygoda obsługi

- Enkoder z przyspieszeniem: powoli co 1 dB, szybko co 3–4 dB.
- Programowy limit maksymalnej głośności (minimalnego tłumienia).
- Ostatnie wejście i głośność zapamiętane w **NVS**.
- Pilot IR, enkoder obrotowy, ewentualnie mały OLED.

### 11.5 ESPHome (alternatywa)

Na początku projektu powstał przykład konfiguracji ESPHome (komponent `mcp23017`, `select` z listą wejść, automatyczny mute). Działa dla samego selektora, ale do całego wzmacniacza wybrano własny firmware (rozdz. 2.6). Przy ewentualnym użyciu pamiętaj o odwróconej logice mute z rozdz. 6.

## 12. Przekaźniki Omron G6K-2F-Y

| Parametr | Wartość |
|---|---|
| Typ | sygnałowy, DPDT, SMD (gull-wing), seria Y (ulepszona) |
| Cewka | 12 V DC, 1315 Ω, ok. 9 mA, **polaryzowana** |
| Czas zadziałania | ok. 3 ms |
| Styki | złocone, do sygnałów na poziomie mV/µA; 1 A / 30 V DC, 0,3 A / 125 V AC |
| Wymiary | ok. 10 × 6,5 mm |

**Biegunowość cewki potwierdzona:** pin 1 = +12 V, pin 8 = wyjście ULN2803. Na płytce przekaźniki są obrócone o 180°, więc pin 1 wypada w prawym dolnym rogu footprintu. Odwrotnie wlutowany przekaźnik nie zadziała.

### 12.1 Zakup

- **Najpewniej: LCSC C397192 (G6K-2F-Y-TR DC12)**, oryginał na taśmie, ok. 1,18 USD/szt., ok. 21 tys. szt. na stanie (10.2026). Przy montażu w JLCPCB to jedyna opcja. Uwaga: **C47190 to wersja DC5** (cewka 5 V, 237 Ω), nie pasuje do zasilania 12 V.
- **Allegro (likwidacja magazynu UR, sprzedaż z taśmy):** napis „China” na obudowie nie świadczy o podróbce (Omron produkuje też w Chinach). Taśma SMD to dobry znak, etykieta szpuli z numerem partii praktycznie potwierdza oryginał. Kupuj z zapasem 2–3 szt. i testuj od razu po odbiorze.

### 12.2 Test po zakupie

1. Rezystancja cewki: ok. **1315 Ω ±10%**.
2. Napięcie zadziałania: podnoś powoli z zasilacza, przekaźnik musi pewnie kliknąć **najpóźniej przy 9,6 V**. Przy odwrotnej polaryzacji nie zadziała.
3. Rezystancja zwartego styku: ułamek oma.
4. Wygląd: ostry nadruk, złocone nóżki, wszystkie sztuki identyczne.
5. Lutowność: jedna sztuka na próbę, cyna powinna ładnie rozpływać się po nóżkach (stare zapasy SMD mogą mieć utlenione wyprowadzenia).

## 13. Płytka PCB

| Parametr | Wartość |
|---|---|
| Wymiary | 96 × 74 mm, narożniki r = 2 mm, 4 otwory M3 |
| Warstwy | 2; strefy GND (cała płytka) i DGND (dolny pas, priorytet 1) na obu warstwach |
| Elementy | SMD jednostronnie: rezystory i kondensatory 0805/1206, SOIC-28W, SOIC-18W, G6K-2F-Y; przewlekane: JST XH, moduł DC-DC |
| Klasy sieci | Audio: ścieżka 0,4 mm, odstęp 0,3 mm; Coil: 0,3 mm / 0,25 mm; Default: 0,3 mm / 0,2 mm |
| Złącza audio | J1–J4 wejścia, J5 wyjście: JST XH 3p, kolejność pinów L / GND / R (sitodruk „R G L”) |

Rozmieszczenie: rząd złączy wejściowych i wyjścia u góry, pod nimi przekaźniki selektora i mute, środkowy rząd to drabinka (K5–K10 z rezystorami), dolny pas to część cyfrowa (DC-DC, J6, MCP23017, ULN2803).

![Rozmieszczenie](img/selektor_plytka.png)

Podgląd schematu: [`img/selektor_schemat.png`](img/selektor_schemat.png).

### 13.1 Trasowanie (do zrobienia)

- Tor audio na TOP, krótko; BOTTOM w części audio możliwie jako ciągła masa.
- Linie cewek (ULN → przekaźniki) i +12 V z dala od wejść, najlepiej prostopadle do ścieżek audio.
- Żadna ścieżka cyfrowa (SDA, SCL, DRV) nie wchodzi w część audio.
- Kanały L (pady po prawej stronie przekaźników) i R (po lewej) rozdzielone masą.
- Można użyć wtyczki Freerouting. Potem **B** (wypełnienie stref) i DRC.

## 14. Zamawianie: JLCPCB i LCSC

### 14.1 Montaż w JLCPCB (PCBA)

Montaż SMD w JLCPCB jest powtarzalny przy typowych elementach (lutowanie rozpływowe, inspekcja AOI). Problemy wynikają zwykle z projektu, najczęściej z obróconych elementów w pliku CPL.

Opłaty (wariant Economic, stan z 10.2026):
- **Basic:** szpule założone na stałe, bez opłaty za załadowanie.
- **Preferred Extended:** w Economic bez opłaty.
- **Extended:** ok. **3,07 USD za każdy unikalny numer elementu, raz na zamówienie**.
- Opłata startowa ok. 8 USD (Standard: 25 USD), szablon ok. 1,50 USD, lutowanie ok. 0,0017 USD za punkt.
- Montowanych płytek może być od 2 do 5; gołych PCB zawsze co najmniej 5.

Ten projekt (sprawdzone w bazie JLCPCB): **14 unikalnych elementów Extended** (G6K, MCP23017, ULN2803 UTC i 11 rezystorów 0,1%) → ok. 43 USD opłat. Pozostałe 5 pozycji (rezystory 1%, kondensatory) to Basic.

| Pozycja | 2 płytki | 5 płytek |
|---|---|---|
| Opłata startowa + szablon | 9,50 USD | 9,50 USD |
| Załadowanie Extended (14 × 3,07) | 43 USD | 43 USD |
| Lutowanie (ok. 240 punktów/płytkę) | 0,80 USD | 2 USD |
| Elementy | ok. 32 USD | ok. 72 USD |
| **Razem (bez PCB, wysyłki i cła)** | **ok. 85 USD** | **ok. 127 USD** |
| **Na płytkę** | **ok. 43 USD** | **ok. 25 USD** |

Pliki: `hardware/selektor/kicad/JLCPCB_BOM.csv` (BOM z numerami LCSC). Plik pozycji (CPL) do wygenerowania w KiCadzie po trasowaniu: File → Fabrication Outputs → Component Placement (.pos), CSV, mm. Złącza JST i moduł DC-DC lutuje się samemu. R35, R41 są poza BOM-em.

**Przed zatwierdzeniem zamówienia sprawdź w podglądzie JLCPCB orientację każdego przekaźnika i układu scalonego.**

### 14.2 Decyzja: montaż samodzielny

Przy 1–2 płytkach własne lutowanie jest tańsze (odpadają opłaty ok. 53 USD). Plan:
- **Płytki + szablon** z JLCPCB (szablon bez ramy, 0,12 mm).
- **Elementy z LCSC** (ten sam magazyn co JLCPCB, te same numery C…).

### 14.3 Zamówienie w LCSC

- Plik **`hardware/selektor/kicad/LCSC_zamowienie.csv`**: komplet na **2 płytki z zapasem** (przekaźniki +2, scalaki +1, drobne +5) plus złącza JST XH (B3B-XH-A, B6B-XH-A), wtyki (XHP-3, XHP-6) i piny do zaciskania (SXH-001T-P0.6). Kolumna „Qty per board” pozwala przeliczyć na inną liczbę płytek.
- Wgrywanie: lcsc.com → **RFQ/BOM** → Upload a BOM File → przypisz kolumny **LCSC Part Number** i **Quantity** → Create BOM → dodaj do koszyka.
- LCSC może podnieść ilości do swojej wielokrotności (np. ULN2803 po 5 szt.).
- Nie ma w pliku: modułu DC-DC (jest już kupiony) i złącza po stronie ESP32 na kablu sterującym.
- **Łączenie wysyłki z JLCPCB:** przy kasie w LCSC można dołączyć zamówienie z JLCPCB (to samo konto i waluta; w JLCPCB trzeba podać adres magazynu LCSC w Hongkongu, którego potem nie da się zmienić). Gdy zamówienie LCSC jest już złożone: support@lcsc.com.
- VAT przy małych zamówieniach do UE LCSC zwykle nalicza przy kasie (sprawdzić w podsumowaniu).
- Do zaciskania pinów XH potrzebna jest zaciskarka do złączy 2,5 mm; alternatywnie gotowe kable XH z zaciśniętymi pinami.

## 15. Montaż ręczny i uruchomienie

### 15.1 Materiały

- Pasta: najłatwiej **Sn63/Pb37** (ok. 183 °C); SAC305 też dobra, wymaga wyższej temperatury. **Bez pasty niskotemperaturowej z bizmutem** (kruche luty).
- Zapasowe płytki jako ramka wokół lutowanej, żeby szablon leżał płasko.

### 15.2 Lutowanie

1. Pasta jednym pociągnięciem szpachelki, szablon zdjąć pionowo.
2. Elementy pęsetą: najpierw rezystory i kondensatory, potem SOIC, na końcu przekaźniki. **Znacznik pinu 1 każdego przekaźnika i układu zgodnie z sitodrukiem.**
3. Płyta grzewcza lub gorące powietrze. G6K-2F-Y nadaje się do lutowania rozpływowego; trzymać się profilu z noty Omron, nie grzać dłużej niż trzeba.
4. Kontrola pod lupą (głównie nóżki SOIC); mostki: grot + topnik + plecionka.
5. Na końcu grotem: złącza JST i moduł DC-DC.

### 15.3 Uruchomienie

1. 12 V z zasilacza z ograniczeniem prądu ok. 200 mA. Bez załączonych przekaźników pobór kilka mA.
2. 3,3 V na wyjściu modułu DC-DC.
3. ESP32 + skan I²C: MCP23017 pod **0x20**.
4. Przekaźniki po kolei: kliknięcie i ok. 9 mA więcej na każdy.
5. Drabinka: sygnał 1 kHz na wejście, pomiar tłumienia dla kilku kodów multimetrem AC.

## 16. Import do EasyEDA Pro

Folder `hardware/selektor/kicad5-easyeda/` zawiera projekt w formacie **KiCad 5.1** z kompletem bibliotek. Spakuj jego zawartość do zip i zaimportuj w EasyEDA Pro jako projekt KiCad. Szczegóły i lista kontrolna: [`CZYTAJ_EasyEDA.md`](../hardware/selektor/kicad5-easyeda/CZYTAJ_EasyEDA.md).

## 17. Weryfikacja projektu

Skrypty w `src/selektor/` (opis w [`src/selektor/README.md`](../src/selektor/README.md)) sprawdzają projekt bez uruchamiania KiCada:

- składnia plików KiCad (S-expression);
- **netlista odtworzona z geometrii schematu** (piny, przewody, etykiety) porównana 1:1 z padami PCB: 74 sieci zgodne;
- zgodność pinów symboli z padami footprintów;
- kolizje courtyardów (0) i odległość padów od krawędzi;
- **symulacja drabinki** (analiza węzłowa) dla 64 kodów, obu kanałów: błąd ≤ 0,205 dB, Zin 9,64–10,77 kΩ, L = R;
- prześledzenie każdego wyjścia MCP23017 przez ULN2803 do właściwej cewki;
- eksport KiCad 5: netlista schematu i PCB zgodna z wersją KiCad 8;
- każdy numer LCSC rezystora sprawdzony z bazą JLCPCB (wartość, tolerancja 0,1%, obudowa 0805).

**Nie zostało sprawdzone** (brak KiCada w środowisku generowania): ERC i DRC w samym KiCadzie. Do uruchomienia przed zamówieniem.

## 18. Otwarte punkty

- [ ] Poprowadzić ścieżki, wypełnić strefy, DRC i ERC w KiCadzie.
- [ ] Zmierzyć moduł DC-DC (średnica pinów, obrys) i potwierdzić footprint.
- [ ] Potwierdzić kolejność pinów kabli audio (L / GND / R) z gniazdami RCA.
- [ ] Zmierzyć czułość wzmacniacza (zakładane ok. 160 mV) i poziom wyjściowy modułu DAC; ustawić limit głośności w firmware.
- [ ] Złącze dla selektora na płytce sterowania (7.5, pkt 1).
- [ ] Decyzja: MUTE z płytki sterowania przez J6 pin 3 (7.5, pkt 2b).
- [ ] Sprawdzić budżet prądowy 12 V z IRM-15-12 (7.5, pkt 3).
- [ ] Przetestować przekaźniki po zakupie (rozdz. 12.2).
- [ ] Wygenerować CPL (tylko przy montażu w JLCPCB).
- [ ] Program testowy ESP32 do uruchomienia płytki (skan I²C, przekaźniki po kolei, kod drabinki z portu szeregowego).
- [ ] Rozważyć w projekcie wzmacniacza czułość 0,5–0,8 V (rozdz. 10.4).
- [ ] Program ESP32: obsługa selektora (rozdz. 11) jako część programu wzmacniacza.

## 19. Historia wersji

| Wersja | Zmiany |
|---|---|
| v0.1 | Schemat i rozmieszczenie: 4 wejścia, drabinka 6 bit (E96/E192), mute fail-safe, 11 diod gaszących, złącze IDC 2×7 z liniami cewek. 96 × 68 mm. |
| v0.2 | MCP23017 + 2× ULN2803A na płytce, złącze JST XH 6p, osobna masa DGND, zworki adresu I²C, usunięte diody. 96 × 74 mm. |
| v0.3 | Zasilanie tylko 12 V, moduł DC-DC 3,3 V na płytce, pin 3 J6 niepodłączony; biegunowość cewek potwierdzona. |
| v0.4 | Wartości drabinki z rezystorów 0,1% dostępnych w JLCPCB/LCSC, numery LCSC, `JLCPCB_BOM.csv`, `LCSC_zamowienie.csv`. |
| v0.5 | ULN2803 TI → UTC ULN2803G-S18-R (koszt). |

## 20. Źródła

- [Omron G6K, nota katalogowa (Farnell)](https://www.farnell.com/datasheets/2340399.pdf)
- [element14: G6K-2F-Y DC12, dane cewki](https://nz.element14.com/omron/g6k-2fy-dc12/relay-signal-dpdt-30vdc-1a/dp/4446240)
- [LCSC: G6K-2F-Y DC12](https://www.lcsc.com/product-image/C397194.html)
- [LCSC: UTC ULN2803G-S18-R (C33924)](https://www.lcsc.com/product-detail/C33924.html), [nota UTC ULN2803](https://static.chipdip.ru/lib/321/DOC040321892.pdf)
- [JLCPCB: TC0525B1002T5E, przykład rezystora 0,1%](https://jlcpcb.com/partdetail/56893-TC0525B1002T5E/C55866)
- [JLCPCB: cennik montażu PCBA](https://api.jlcpcb.com/help/article/pcb-assembly-price)
- [JLCPCB: jak obniżyć koszt montażu prototypu](https://jlcpcb.com/blog/reduce-pcb-assembly-cost-prototype)
- [JLCPCB: konwersja plików do EasyEDA Pro](https://jlcpcb.com/de/help/article/eda-file-conversion-jlcpcb-easyeda-pro-guide)
- [EasyEDA Pro: import KiCad](https://prodocs.easyeda.com/en/import-export/import-kicad/)
- [LCSC: BOM List, instrukcja](https://fat.lcsc.com/faqs/online-services/bom-list)
- [LCSC: łączenie zamówień LCSC i JLCPCB](https://fat.lcsc.com/faqs/ordering-quotation/combine-lcsc-jlcpcb-orders)
- [jlcparts: baza elementów JLCPCB](https://github.com/yaqwsx/jlcparts)
- [KiCad: biblioteki footprintów](https://github.com/KiCad/kicad-footprints) i [symboli](https://github.com/KiCad/kicad-symbols)
- [pioarduino: platforma ESP32 dla PlatformIO](https://github.com/pioarduino/platform-espressif32)
