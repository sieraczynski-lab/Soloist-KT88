# Selektor wejść + przekaźnikowa regulacja głośności (TubeSel)

Płytka wzmacniacza Soloist 88: **4 wejścia stereo**, **drabinka przekaźnikowa 0–63 dB co 1 dB** (stała impedancja ok. 10 kΩ, rezystory 0,1%), **mute fail-safe**. Przekaźniki sygnałowe Omron G6K-2F-Y, sterowanie po I²C (MCP23017 + 2× ULN2803) z ESP32-S3 płytki sterowania, zasilanie tylko 12 V.

Status: **v0.5**: schemat gotowy, elementy rozmieszczone, ścieżki do poprowadzenia.

![Rozmieszczenie elementów](../../docs/img/selektor_plytka.png)

## Struktura

| Folder | Zawartość |
|---|---|
| [`docs/11-selektor.md`](../../docs/11-selektor.md) | **Pełna dokumentacja**: decyzje projektowe, drabinka, sterowanie, integracja z płytką sterowania, masy i ekranowanie, dopasowanie do EF86, firmware, zakupy, montaż, otwarte punkty |
| [`kicad/`](kicad/) | Projekt KiCad 8/9 + BOM-y (`BOM.csv`, `JLCPCB_BOM.csv`, `LCSC_zamowienie.csv`) |
| [`kicad5-easyeda/`](kicad5-easyeda/) | Ten sam projekt w formacie KiCad 5.1 do importu w EasyEDA Pro |
| [`src/selektor/`](../../src/selektor/) | Skrypty generujące i weryfikujące projekt (Python) |

## Najważniejsze w skrócie

- Przypisanie MCP23017: GPA0–3 = wejścia 1–4, GPA4–GPB1 = bity −1…−32 dB, GPB2 = mute (1 = dźwięk). Adres 0x20 (zworki SJ1–SJ3).
- J6 do ESP32 (JST XH 6p): +12 V, DGND, n/c, SDA, SCL, DGND.
- Zmiana głośności: najpierw załącz nowe bity, ok. 5 ms, potem wyłącz zbędne.
- Po starcie drabinka stoi na 0 dB (pełna głośność) przy aktywnym mute: ustaw głośność przed zdjęciem mute.
- Limity głośności dla każdego wejścia: [docs/07](../../docs/07-zrodla-i-poziomy.md) (ok. −19 dB dla źródła 2 V).
- Do decyzji: MUTE z płytki sterowania przez J6 pin 3 ([11, rozdz. 7.5](../../docs/11-selektor.md#75-integracja-z-płytką-sterowania)).
