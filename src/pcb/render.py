import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from boards import BOARDS, HV
from playwright.sync_api import sync_playwright

CSS = """
svg{background:#fff}
.board{fill:#f4f7f2;stroke:#1d2a1f;stroke-width:.35}
.zone{fill:none;stroke:#b5600e;stroke-width:.3;stroke-dasharray:2 1.2}
.zl{font-size:2.1px;fill:#b5600e}
.body{fill:rgba(255,255,255,.55);stroke:#3a4a3c;stroke-width:.3}
.body.bot{fill:none;stroke:#2f62b8;stroke-width:.3;stroke-dasharray:1.2 .8}
.ref.bot{fill:#2f62b8}
.pad{fill:#c9a24a;stroke:#7a5c17;stroke-width:.12}
.pad.hv{fill:#d9573f;stroke:#7c2414}
.hole{fill:#fff;stroke:#1d2a1f;stroke-width:.25}
.ref{font-size:2.2px;fill:#1d2a1f;font-weight:600}
.lab{font-size:1.9px;fill:#36503a}
.title{font-size:3px;fill:#1d2a1f;font-weight:700}
"""

def render(outdir, pdf=False):
    os.makedirs(outdir, exist_ok=True)
    res = []
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for fn in BOARDS:
            b = fn()
            svg = b.svg(hv_nets=HV[b.name])
            html = "<html><head><style>@page{margin:0}body{margin:0}%s</style></head><body>%s</body></html>" % (CSS, svg)
            hp = os.path.join(outdir, b.name + "_rozmieszczenie.html")
            open(hp, "w").write(html)
            open(os.path.join(outdir, b.name + "_rozmieszczenie.svg"), "w").write(svg.replace("<svg ", "<svg ", 1).replace(">", "><style>%s</style>" % CSS, 1))
            pg = br.new_page(device_scale_factor=1)
            pg.goto("file://" + hp)
            w = (b.w + 12) * 6
            pg.set_viewport_size({"width": int(w), "height": int((b.h + 12) * 6)})
            pg.evaluate("document.querySelector('svg').setAttribute('width','%dpx');document.querySelector('svg').setAttribute('height','%dpx')" % (w, (b.h + 12) * 6))
            png = os.path.join(outdir, b.name + "_rozmieszczenie.png")
            pg.screenshot(path=png, full_page=True)
            if pdf:
                pg2 = br.new_page()
                pg2.goto("file://" + hp)
                pg2.pdf(path=os.path.join(outdir, b.name + "_rozmieszczenie_1do1.pdf"), width="%.1fmm" % (b.w + 12), height="%.1fmm" % (b.h + 12),
                        print_background=True)
            res.append(png)
        br.close()
    return res

if __name__ == "__main__":
    print(render(sys.argv[1], pdf=len(sys.argv) > 2))
