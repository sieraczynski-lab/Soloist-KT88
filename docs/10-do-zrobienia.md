# 10. Do zrobienia / do sprawdzenia

## Przed zamówieniem płytek

- [ ] **Omron G2RL-2, sprawdź miernikiem jedną sztukę.** Bez zasilania cewki zwarte piny 3–2 i 6–7, po podaniu 12 V na 1–8 zwarte 3–4 i 6–5. Układ otworów jest z biblioteki KiCad, ale funkcji wyprowadzeń (COM w środku rzędu) nie potwierdziłem na rysunku Omron. Dotyczy płytek zasilacz_siec, zasilacz_hv, ul i glosniki.
- [ ] **IRM-15-12:** podmień footprint na LCSC C6394169 i sprawdź kolejność pinów +V/−V.
- [ ] **ESP32-S3-DevKitC-1:** zmierz rozstaw listew (przyjęte 22,86 mm).
- [ ] **ULN2803G-S18-R:** sprawdź, że SOP-18 ma 7,5 mm szerokości i standardowy układ nóżek.
- [ ] **Wydruk 1:1** (PDF z `3_pakiet_awaryjny`): przyłóż podstawki B9A, oprawki bezpieczników i złącza.
- [ ] Zdecyduj o **R119/R120 27k → 20k** (zakres biasu zgodny z danymi GEC, patrz [układ](01-uklad.md#zgodność-z-kartą-kt88-genalex--gec)).

## Zamówienia

- [ ] TR1 z **S2 6,3 V / 8 A**. Specyfikacja do konfiguratora w [zasilaniu](02-zasilanie.md#zamówienie-tr1-w-konfiguratorze-toroidypl).
- [ ] Zmierz napięcie sieci w domu (wybór odczepu 345 / 360 V).
- [ ] Toroidy.pl: napięcia TR1 bez obciążenia, wymiary TR1 (zwłaszcza przy obniżonej indukcji), próba izolacji S1, faza uzwojeń.
- [ ] Toroidy.pl: czy da się dodać odczep 2 Ω w TTG-KT88PP (do porównania na słuch z kolumnami 4 Ω).
- [ ] Toroidy.pl: dopuszczalne ΔI w parze dla TTG-KT88PP, kolory przewodów i faza uzwojeń; czy indukcyjność dławika podana przy prądzie DC.
- [ ] Wymiary transformatorów i dławika do obudowy.
- [ ] Lampy: tani komplet na uruchomienie; ewentualnie Psvane Summit (promocja do 11.11).
- [ ] Części spoza LCSC (lista w [zakupach](08-czesci-i-zakupy.md)).

## Projekt

- [ ] **Program ESP32:** sekwencja, zabezpieczenia, korekta biasu, UL/trioda, przełącznik kolumn, trigger, IR, wyświetlacz.
- [x] **Selektor wejść z drabinką**: projekt v0.5, [11](11-selektor.md). Limity poziomów z [07](07-zrodla-i-poziomy.md).
- [ ] **Selektor:** routing, DRC/ERC, pomiar modułu DC-DC; reszta w [11, rozdz. 18](11-selektor.md#18-otwarte-punkty).
- [ ] **Sterowanie ↔ selektor:** złącze dla selektora (12 V, I²C, MUTE) na płytce sterowania i decyzja, czy MUTE (GPIO14, J3) ma sterować K11 selektora ([11, rozdz. 7.5](11-selektor.md#75-integracja-z-płytką-sterowania)).
- [ ] **Płyta Williamsona od Onyxa:** schemat → porównanie i specyfikacja transformatorów pasujących do obu wersji.
- [ ] Routing płytek: zasilacz_siec, zasilacz_hv, sterowanie, ul, glosniki.
- [ ] Wartości dobierane pomiarem: R104 (NFB), C103 (kompensacja), ewentualnie R128/C107.

## Zakładane, ale niezmierzone

- moc ok. 45 W na kanał, czułość ok. 160 mV;
- B+ zależy od rzeczywistej regulacji TR1. Gdyby wyszło powyżej 480 V, użyj odczepu 345 V.
