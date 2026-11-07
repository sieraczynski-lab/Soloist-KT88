# 7. Źródła sygnału i poziomy

Wzmacniacz ma **czułość ok. 160 mV** na pełną moc (z obliczeń) i **impedancję wejściową 220 kΩ**. Źródła liniowe dają dużo więcej, więc w selektorze (osobny projekt) potrzebna jest regulacja głośności. Stały tłumik nie jest potrzebny.

## Poziomy źródeł

| Źródło | Napięcie przy pełnej skali | Nadmiar | Limit drabinki dla wejścia |
|---|---|---|---|
| WiiM Ultra, CD, DAC (standard) | 2 V | +22 dB | ok. −19 dB |
| Amplituner AV, pre-out (napięcie znamionowe, np. Marantz SR7013) | ok. 1,2 V | +17 dB | ok. −15 dB |
| WiiM z wyjściem ustawionym na 1 V | 1 V | +16 dB | ok. −13 dB |
| Starsze źródła (magnetofon, tuner) | 0,3–0,5 V | +6…+10 dB | ok. −5 dB |

Limit liczy się tak: 20·log(0,16 V / napięcie źródła), plus ok. 3 dB zapasu. Napięcia WiiM Ultra (wyjście ustawiane na 2 / 1 / 0,5 / 0,2 V) pochodzą z forum użytkowników, a pre-out SR7013 z typowych danych Denon/Marantz. Sprawdź je w aplikacji i w instrukcji.

**Dlaczego nie podawać 2 V bez tłumienia:** wzmacniacz obetnie sygnał już przy ok. 1/4 skali głośności. Przy przesterowaniu sprzężenie zwrotne traci kontrolę, a EF86 (bias tylko ok. −0,8 V) wchodzi w prąd siatki. Efekt to bardzo nieprzyjemne zniekształcenia z „przytykaniem” i pełne 45 W prostokątem na kolumnach.

## Zalecenia dla selektora wejść

1. Głośność regulowana **drabinką na przekaźnikach** (Omron G6K-2F-Y, LCSC C47190; wersja bistabilna G6KU-2F-Y jest poza LCSC). Zakres 0…−63 dB co 1 dB (6 przekaźników) albo co 0,5 dB (7 przekaźników). Impedancja 10–20 kΩ.
2. **WiiM: stała głośność** (Fixed Volume), wyjście 2 V albo 1 V. Tłumienie jest wtedy analogowe, a WiiM ma pełną rozdzielczość.
3. **Dla każdego wejścia w ESP32:**
   - poprawka poziomu, żeby głośność była podobna po przełączeniu;
   - maksymalna głośność według tabeli wyżej, żeby żadne źródło nie przesterowało wzmacniacza;
   - po przełączeniu wejścia głośność startuje najwyżej z bezpiecznego poziomu (np. −30 dB).
4. **Marantz SR7013 w kinie domowym:** pre-out FL/FR na wejście Lampy, tryb „bypass” (drabinka na stałym, skalibrowanym poziomie, głośność reguluje amplituner). Razem z [triggerem](03-sterowanie.md#wejście-trigger-12-v) i [przełącznikiem kolumn](03-sterowanie.md#przełącznik-kolumn-marantz--lampa) Lampa włącza się sama z amplitunerem.
5. **Masa:** przekaźniki selektora przełączają tylko gorący przewód. Masy wejść łącz przy gniazdach i jednym przewodem do masy płytki kanału.
