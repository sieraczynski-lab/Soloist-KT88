# Generatory

Wszystkie pliki w `hardware/` i `site/` powstają z tych skryptów (Python 3, bez bibliotek CAD).

| Plik | Co robi |
|---|---|
| `pcb/boards.py` | definicja wszystkich płytek: elementy, sieci, rozmieszczenie (stałe i automatyczne) |
| `pcb/pcbgen.py` | footprinty, symbole, zapis `.kicad_pcb`, rysunki SVG/PDF |
| `pcb/sch_kanal.py`, `pcb/sch_psu.py`, `pcb/schwired.py` | schematy KiCad z kontrolą zgodności z płytką |
| `pcb/netclasses.py` | klasy sieci (szerokości / odstępy) |
| `pcb/jlc.py`, `pcb/bom_lcsc.py` | BOM do montażu SMD w JLCPCB i BOM-y części LCSC |
| `pcb/check.py`, `pcb/hvcheck.py` | kontrola kolizji i odstępów wysokiego napięcia |
| `pcb/export.py` | buduje całą paczkę `Soloist88_PCB` (+ zip) |
| `case/model.py` | parametryczny model obudowy |
| `case/stepw.py` | zapis STEP (ADVANCED_BREP) |
| `case/export_pkg.py` | STEP, DXF, lista części, widoki → `Soloist88_obudowa_vX` |
| `case/chkstep.py`, `case/chk2d.py` | walidacja brył i konturów |
| `calc.py` | obliczenia punktów pracy |
| `build.py`, `draw.py`, `sch.py`, `sch.css` | strona projektu (`soloist88.html`) ze schematami SVG |
| `preview.py` | podglądy schematów strony do PNG (Playwright) |

## Użycie

```bash
cd src/pcb && python3 check.py && python3 hvcheck.py kanal zasilacz_siec zasilacz_hv sterowanie ul glosniki
python3 sch_psu.py            # kontrola schematów zasilaczy, sterowania, UL i głośników
python3 export.py             # -> src/pcb/Soloist88_PCB + zip
cd ../case && python3 export_pkg.py    # -> src/case/Soloist88_obudowa_v0.4 + zip
cd .. && python3 build.py     # -> src/soloist88.html (wymaga paczki PCB, bo czyta BOM SMD)
```

Wynik kopiujesz do `hardware/` i `site/`.

Zależności: `numpy`, `matplotlib` (widoki), `openpyxl` (BOM XLSX), `reportlab` lub odpowiednik użyty w `pcbgen.py` do PDF, `playwright` (tylko `preview.py`). `bom_lcsc.py` opcjonalnie czyta lokalną bazę stanów (`/home/claude/bomtool/db.pkl`, zbudowaną z [jlcparts](https://github.com/yaqwsx/jlcparts)); bez niej kolumna stanu jest pusta.
