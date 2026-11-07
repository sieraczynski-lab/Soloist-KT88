# 10. Do zrobienia / do sprawdzenia

## Przed zamówieniem płytek

- [ ] **Omron G2RL-2, sprawdź miernikiem jedną sztukę.** Bez zasilania cewki zwarte piny 3–2 i 6–7, po podaniu 12 V na 1–8 zwarte 3–4 i 6–5. Układ otworów jest z biblioteki KiCad, ale funkcji wyprowadzeń (COM w środku rzędu) nie potwierdziłem na rysunku Omron. Dotyczy płytek zasilacz_siec, zasilacz_hv, ul i glosniki.
- [ ] **IRM-15-12:** podmień footprint na LCSC C6394169 i sprawdź kolejność pinów +V/−V.
- [ ] **ESP32-S3-DevKitC-1:** zmierz rozstaw listew (przyjęte 22,86 mm).
- [ ] **ULN2803G-S18-R:** sprawdź, że SOP-18 ma 7,5 mm szerokości i standardowy układ nóżek.
- [ ] **Wydruk 1:1** (PDF z `3_pakiet_awaryjny`): przyłóż podstawki B9A, oprawki bezpieczników i złącza.
- [ ] Zdecyduj o **R119/R120 27k → 20k** (zakres biasu zgodny z danymi GEC, patrz [układ](01-uklad.md#zgodność-z-kartą-kt88-genalex--gec)).

## Zamówienia

- [ ] TR1 z **S2 6,3 V / 8 A**.
- [ ] Toroidy.pl: dopuszczalne ΔI w parze dla TTG-KT88PP, kolory przewodów i faza uzwojeń; czy indukcyjność dławika podana przy prądzie DC.
- [ ] Wymiary transformatorów i dławika do obudowy.
- [ ] Lampy: tani komplet na uruchomienie; ewentualnie Psvane Summit (promocja do 11.11).
- [ ] Części spoza LCSC (lista w [zakupach](08-czesci-i-zakupy.md)).

## Projekt

- [ ] **Program ESP32:** sekwencja, zabezpieczenia, korekta biasu, UL/trioda, przełącznik kolumn, trigger, IR, wyświetlacz.
- [ ] **Selektor wejść z drabinką** (osobna sesja): poziomy i limity z [07](07-zrodla-i-poziomy.md).
- [ ] **Płyta Williamsona od Onyxa:** schemat → porównanie i specyfikacja transformatorów pasujących do obu wersji.
- [ ] Routing płytek: zasilacz_siec, zasilacz_hv, sterowanie, ul, glosniki.
- [ ] Wartości dobierane pomiarem: R104 (NFB), C103 (kompensacja), ewentualnie R128/C107.

## Zakładane, ale niezmierzone

- moc ok. 45 W na kanał, czułość ok. 160 mV;
- B+ zależy od rzeczywistej regulacji TR1. Gdyby wyszło powyżej 480 V, użyj odczepu 345 V.
