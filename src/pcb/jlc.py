"""Numery czesci LCSC/JLCPCB (sprawdzone 25.10.2026) i BOM w formacie JLCPCB."""
import csv, os
from pcbgen import FOOT

# (wartosc, footprint) -> (opis / MPN, LCSC)
PARTS = {
    ("ULN2803G-S18-R", "SOIC-18W_7.5x11.6mm_P1.27mm"): ("ULN2803G-S18-R (UTC)", "C33924"),
    ("ADS1115IDGSR 0x48", "MSOP-10_3x3mm_P0.5mm"): ("ADS1115IDGSR", "C37593"),
    ("ADS1115IDGSR 0x49", "MSOP-10_3x3mm_P0.5mm"): ("ADS1115IDGSR", "C37593"),
    ("MCP4728-E/UN", "MSOP-10_3x3mm_P0.5mm"): ("MCP4728-E/UN", "C108207"),
    ("LM324DR", "SOIC-14_3.9x8.7mm_P1.27mm"): ("LM324DR", "C7943"),
    ("10k", "R_0805_2012Metric"): ("10k 1% 0805", "C17414"),
    ("20k", "R_0805_2012Metric"): ("20k 1% 0805", "C4328"),
    ("4k7", "R_0805_2012Metric"): ("4,7k 1% 0805", "C17673"),
    ("1k 1206", "R_1206_3216Metric"): ("1k 1% 1206", "C4410"),
    ("330k 1206", "R_1206_3216Metric"): ("330k 1% 1206 (1206W4F3303T5E)", "C17929"),
    ("68k", "R_0805_2012Metric"): ("68k 1% 0805", "C17801"),
    ("33k", "R_0805_2012Metric"): ("33k 1% 0805", "C17633"),
    ("1k", "R_0805_2012Metric"): ("1k 1% 0805", "C17513"),
    ("1u", "C_0805_2012Metric"): ("1uF 50V X7R 0805", "C28323"),
    ("100n", "C_0805_2012Metric"): ("100nF 50V X7R 0805", "C49678"),
    ("1N4148W", "D_SOD-123"): ("1N4148W SOD-123", "C81598"),
    ("G2RL-2-DC12", "Relay_DPDT_Omron_G2RL"): ("Omron G2RL-2-DC12", "C61458"),
}


def lookup(c):
    n = FOOT[c.fp].name
    if n.endswith("_V"):
        n = n[:-2]
    return PARTS.get((c.value, n), ("", ""))


def is_smd(c):
    f = FOOT[c.fp]
    return bool(f.pads) and all(p["drill"] == 0 for p in f.pads)


def write_bom(board, dirpath):
    """BOM do montazu SMD w JLCPCB (tylko elementy SMD). Zwraca liczbe pozycji."""
    groups = {}
    for c in board.comps:
        if not is_smd(c):
            continue
        desc, lcsc = lookup(c)
        fp = FOOT[c.fp].name
        key = (desc or c.value, fp[:-2] if fp.endswith("_V") else fp, lcsc)
        groups.setdefault(key, []).append(c.ref)
    if not groups:
        return 0
    p = os.path.join(dirpath, board.name + "_BOM_JLCPCB.csv")
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for (desc, fp, lcsc), refs in sorted(groups.items(), key=lambda kv: kv[1][0]):
            refs.sort(key=lambda r: (r.rstrip("0123456789"), int(r[len(r.rstrip("0123456789")):] or 0)))
            w.writerow([desc, ",".join(refs), fp, lcsc])
    return len(groups)
