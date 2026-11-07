# 6. Uruchomienie krok po kroku

> ⚠️ Wysokie napięcie. Pracuj jedną ręką, rozładowuj kondensatory (rezystor 2 kΩ / 10 W), ufaj LED HV, ale sprawdzaj miernikiem.

Na pierwsze uruchomienie użyj **taniego kompletu KT88** (np. JJ). Droższe lampy (np. Psvane) wkładaj dopiero do sprawdzonego wzmacniacza.

1. **Kontrola przed włączeniem.** Ciągłość PE do obudowy, polaryzacja elektrolitów, brak zwarć szyn HT do masy. Wszystkie potencjometry biasu na maksimum, czyli najbardziej ujemne napięcie.
2. **Zasilacz bez lamp.** Pierwsze włączenie przez żarówkę szeregową 100 W. ESP32 w trybie serwisowym z ręcznym sterowaniem K1–K4. Zmierz napięcia uzwojeń i szynę biasu (ok. −80 V). Na pinie 5 każdej podstawki KT88 ok. −57 V (potencjometry na maksimum, DAC korekty na zero).
3. **HT bez obciążenia.** Bez lamp B+ dojdzie do ok. 510 V, a przy wysokiej sieci do 560 V. Sprawdź, czy C1 i C2 dzielą napięcie po połowie. Po wyłączeniu odczekaj albo rozładuj kondensatory.
4. **Lampy sygnałowe.** Włóż EF86 i E88CC, bez KT88. Ustaw P101 tak, żeby na R111/R112 było po ok. 189 V (7 mA na sekcję).
5. **KT88 i bias.** Włóż KT88, na wyjściu rezystor 4 Ω / 50 W, sprzężenie zwrotne odłączone. Obserwuj I<sub>K</sub> i wyłącz powyżej 80 mA. Stopniowo ustaw 55 mA na każdą lampę, po 10 minutach skoryguj.
6. **Faza sprzężenia zwrotnego.** Bez FB podaj 50 mV / 1 kHz i zmierz wzmocnienie. Po podłączeniu FB wzmocnienie musi spaść mniej więcej pięciokrotnie. Jeśli rośnie albo układ się wzbudza, zamień przewody anod transformatora.
7. **Głębokość NFB.** Dobierz R104 tak, żeby różnica wzmocnień wynosiła 14–16 dB. Zapisz czułość.
8. **Kompensacja (oscyloskop).** Prostokąt 1 kHz i 10 kHz na 4 Ω, na 4 Ω równolegle z 1 µF i bez obciążenia (tylko R127). Dobierz C103 (start 100 pF, docelowo mikowy 68–220 pF) i ewentualnie R128/C107.
9. **Pomiary końcowe.** Impedancja wyjściowa, charakterystyka 20 Hz – 40 kHz, moc przy początku obcinania. Pełną moc sinusem mierz krótko, bo zasilacz jest liczony na ok. 45 W ciągłej mocy.
10. **Korekta biasu.** Z podłączonym J10 ustaw DAC w połowie (ok. 1,65 V) i dopiero wtedy wyreguluj P102/P103 na 55 mA. Włącz automat. Po godzinie grania i ciszy prądy w parze powinny różnić się o mniej niż 1 mA. Przy wyjętej KT88 odłącz na chwilę przewód J10 i sprawdź alarm.
11. **UL / trioda.** Przełącz na triodę (przy wyłączonym B+) i powtórz kontrolę prostokątem.
12. **Kalibracja ESP32.** Wpisz rzeczywiste wartości rezystorów 10 Ω, napięcie 3,3 V i progi zabezpieczeń.
13. **Przełącznik kolumn i trigger.** Sprawdź, że bez zasilania Lampy kolumny grają z Marantza, a Lampa przejmuje je dopiero po stabilizacji. Potem sprawdź trigger z SR7013.

## Płyta używana (np. od Onyxa)

Jeśli płyta długo leżała, kondensatory elektrolityczne formuj stopniowo (autotransformator albo żarówka, powoli). Sprawdź bias przed włożeniem KT88. Pierwszy start bez kolumn, na rezystorze obciążenia.
