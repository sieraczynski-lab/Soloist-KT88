import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import draw
from playwright.sync_api import sync_playwright

CSS = open(os.path.join(os.path.dirname(__file__), "sch.css")).read()
D = os.path.dirname(__file__)
for name, fn in (("amp", draw.amp), ("psu", draw.psu), ("ctl", draw.ctl), ("bk", draw.biaskor), ("ul", draw.ulsw)):
    html = f"<html><head><style>:root{{--paper:#f4f6f7;--ink:#1d252b;--muted:#5d6a73;--rule:#d3dadf;--accent:#b8640f;--hv:#b4332a;--panel:#e9eef0}}body{{background:var(--paper);margin:0}}{CSS}</style></head><body>{fn()}</body></html>"
    p = os.path.join(D, f"pv_{name}.html")
    open(p, "w").write(html)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1660, "height": 900})
        pg.goto("file://" + p)
        pg.locator("svg").screenshot(path=os.path.join(D, f"pv_{name}.png"))
        b.close()
print("done")
