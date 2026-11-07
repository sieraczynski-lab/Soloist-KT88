#!/usr/bin/env python3
"""Wyszukiwanie rezystorów 0805 w bazie JLCPCB (jlcparts) dla drabinki."""
import gzip, json, glob, os, re, sys

D = os.environ.get("JLCPARTS_DATA", "data") + "/"  # folder data/ z gałęzi gh-pages github.com/yaqwsx/jlcparts
lut = json.load(gzip.open(D + "attributes-lut.json.gz"))


def attrs(ids):
    out = {}
    for i in ids:
        name, a = lut[i]
        vals = a.get("values", {})
        if "primary" in a and a["primary"] in vals:
            v = vals[a["primary"]][0]
        elif vals:
            v = next(iter(vals.values()))[0]
        else:
            v = a.get("format")
        out[name] = v
    return out


rows = []
for fn in sorted(glob.glob(D + "browse-components-resistors_chip_resistor_surface_mount__*.jsonl.gz")):
    with gzip.open(fn, "rt") as fh:
        hdr = json.loads(fh.readline())
        for line in fh:
            r = json.loads(line)
            a = attrs(r[hdr["attributes"]])
            pkg = a.get("Package", "")
            if pkg != "0805":
                continue
            rows.append(dict(lcsc=r[hdr["lcsc"]], mfr=r[hdr["mfr"]], desc=r[hdr["description"]],
                             stock=r[hdr["stock"]], price=r[hdr["price"]], a=a))
print("rezystorów 0805:", len(rows), file=sys.stderr)


def tol(r):
    t = r["a"].get("Tolerance")
    return t


def res(r):
    return r["a"].get("Resistance")


def unit_price(r, q=10):
    for p in r["price"] or []:
        if p["qFrom"] <= q and (p["qTo"] is None or q <= p["qTo"]):
            return p["price"]
    return (r["price"] or [{"price": None}])[0]["price"]


if __name__ == "__main__":
    import collections
    tols = collections.Counter(str(tol(r)) for r in rows)
    print(tols.most_common(12))
    ex = [r for r in rows if r["a"].get("Tolerance") not in (None,)][:3]
    for r in ex:
        print(r["lcsc"], r["mfr"], r["a"])
