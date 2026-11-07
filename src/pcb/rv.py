import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boards
from render import CSS
from playwright.sync_api import sync_playwright
names = sys.argv[1:]
with sync_playwright() as pw:
    br = pw.chromium.launch()
    for n in names:
        b = getattr(boards, n)()
        svg = b.svg(hv_nets=boards.HV.get(b.name, set()))
        k = 9
        html = "<html><head><style>body{margin:0}%s</style></head><body>%s</body></html>" % (CSS, svg)
        p = os.path.abspath("rv_%s.html" % n); open(p, "w").write(html)
        pg = br.new_page(viewport={"width": int((b.w + 12) * k), "height": int((b.h + 12) * k)})
        pg.goto("file://" + p)
        pg.evaluate("document.querySelector('svg').setAttribute('width','%dpx');document.querySelector('svg').setAttribute('height','%dpx')" % ((b.w + 12) * k, (b.h + 12) * k))
        pg.screenshot(path="rv_%s.png" % n)
    br.close()
