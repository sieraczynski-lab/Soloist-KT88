# Generator płytki selektora

Pliki w [`hardware/selektor/`](../../hardware/selektor/) powstały z jednej listy elementów w `gen.py`. Te skrypty są niezależne od generatorów reszty wzmacniacza (`src/pcb/`). Dzięki temu schemat, PCB, BOM-y i eksport do EasyEDA mają zawsze identyczną netlistę, a całość da się sprawdzić bez KiCada.

> **Uwaga:** generator służy do budowy projektu (schemat, rozmieszczenie, BOM). Po rozpoczęciu trasowania ścieżek w KiCadzie źródłem prawdy są pliki w `hardware/selektor/kicad/`. Ponowne uruchomienie `gen.py` nadpisze `.kicad_pcb` razem ze ścieżkami. Zmiany po trasowaniu rób w KiCadzie.

## Wymagania

- Python 3.9+ z `numpy` i `matplotlib` (`pip install numpy matplotlib`)
- Klon oficjalnej biblioteki footprintów KiCad (używane są `Relay_SMD`, `Resistor_SMD`, `Capacitor_SMD`, `Connector_JST`, `Package_SO`, `Jumper`, `MountingHole`):
  ```bash
  git clone --depth 1 --filter=blob:none --sparse https://github.com/KiCad/kicad-footprints.git
  cd kicad-footprints && git sparse-checkout set Relay_SMD.pretty Resistor_SMD.pretty Capacitor_SMD.pretty \
      Connector_JST.pretty Package_SO.pretty Jumper.pretty MountingHole.pretty
  export KICAD_FOOTPRINT_DIR=$PWD
  ```

## Skrypty

| Skrypt | Co robi |
|---|---|
| `gen.py` | Generuje `hardware/selektor/kicad/`: `.kicad_pro`, `.kicad_sch`, `.kicad_pcb`, bibliotekę symboli `TubeSel.kicad_sym`, `BOM.csv`, `JLCPCB_BOM.csv`, `LCSC_zamowienie.csv`. Footprint modułu DC-DC jest ręcznie napisany w `hardware/selektor/kicad/TubeSel.pretty/` i nie jest generowany. |
| `verify.py` | Niezależna weryfikacja `hardware/selektor/kicad/`: składnia, netlista odtworzona z geometrii schematu vs pady PCB, kolizje courtyardów, symulacja drabinki dla 64 kodów. |
| `gen_k5.py` | Eksport do formatu KiCad 5.1 w `hardware/selektor/kicad5-easyeda/` (import do EasyEDA Pro), z kompletem symboli i footprintów. |
| `verify_k5.py` | Porównanie netlisty eksportu KiCad 5 z PCB i z wersją KiCad 8. |
| `render.py` | Podglądy do `docs/img/selektor_plytka.png` i `docs/img/selektor_schemat.png`. |
| `jlc_res.py` | Wyszukiwanie rezystorów 0805 w bazie JLCPCB z projektu [jlcparts](https://github.com/yaqwsx/jlcparts) (ścieżka do folderu `data/` w zmiennej `JLCPARTS_DATA`). Użyte do doboru wartości drabinki z magazynu. |

## Typowe użycie

```bash
cd src/selektor
python3 gen.py && python3 verify.py
python3 gen_k5.py && python3 verify_k5.py
python3 render.py
```

`verify.py` kończy się `WSZYSTKO OK` lub listą błędów (kod wyjścia 1).

## Gdzie co zmienić w `gen.py`

- `LADDER`: wartości drabinki (dB, Rs, Rp); `LCSC_01`, `LCSC_1`, `LCSC_OTHER`: numery LCSC.
- Sekcje `# --- Wejścia i selektor`, `# --- Drabinka`, `# --- Mute`, `# --- Sterowanie`: lista elementów z sieciami, pozycją na schemacie i na PCB.
- `BW, BH`: wymiary płytki (limit 100 × 100 mm jest sprawdzany).
- `REV`: wersja na schemacie i sitodruku.
