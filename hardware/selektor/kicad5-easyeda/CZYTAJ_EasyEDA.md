# Import do EasyEDA Pro

Ten folder zawiera projekt selektora (TubeSel) zapisany w formacie **KiCad 5.1**, który EasyEDA Pro importuje bezpośrednio.
Wszystkie symbole (`TubeSel.lib`) i footprinty (`TubeSel.pretty`) są w środku, więc projekt nie zależy od bibliotek KiCada.
Pliki generuje skrypt `src/selektor/gen_k5.py` z tych samych danych co wersja KiCad 8 (netlista jest identyczna, sprawdza to `src/selektor/verify_k5.py`).

## Jak zaimportować
1. Spakuj **zawartość tego folderu** do pliku zip (pliki mają leżeć w głównym katalogu archiwum).
2. W EasyEDA Pro wybierz import projektu KiCad (Plik → Import → KiCad lub z ekranu startowego) i wskaż ten zip, bez rozpakowywania.
3. Po imporcie zapisz projekt w natywnym formacie EasyEDA (Eksport → .epro).

Dlaczego KiCad 5.1, a nie natywny `.epro`: format `.epro` nie jest publicznie opisany, a import KiCad 5.1 jest oficjalnie wspierany przez EasyEDA Pro.

## Co sprawdzić po imporcie
- **Strefy miedzi:** EasyEDA buduje je od nowa. Są po dwie na każdej warstwie: GND (audio, cała płytka) i DGND (dolny pas pod układami scalonymi, wyższy priorytet). Sprawdź, czy DGND nie zlała się z GND.
- **Footprinty:** szczególnie przekaźniki G6K-2F-Y (pin 1 = +12 V) i moduł DC-DC (rozstaw 14,17 × 8,24 mm).
- **Netlista:** 74 sieci, 73 elementy. Etykiety sieci na schemacie (np. BUS_L, A1_L, COIL5) łączą elementy po nazwie.
- Narożniki obrysu są proste (w wersji KiCad 8 zaokrąglone), można je zaokrąglić w EasyEDA.
- Modele 3D wskazują na biblioteki KiCada i w EasyEDA nie będą widoczne.

Pełny opis układu: [`docs/11-selektor.md`](../../../docs/11-selektor.md).

Footprinty w `TubeSel.pretty` (poza modułem DC-DC) pochodzą z oficjalnej biblioteki KiCad (https://github.com/KiCad/kicad-footprints, licencja CC-BY-SA 4.0 z wyjątkiem dla projektów).
