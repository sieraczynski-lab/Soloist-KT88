import sys, re, os
from playwright.sync_api import sync_playwright

def render(sch, lib, out, scale=8):
    L = open(lib).read()
    syms = {}
    for m in re.finditer(r'DEF (\S+) .*?\nDRAW\n(.*?)ENDDRAW', L, re.S):
        syms[m.group(1)] = m.group(2).splitlines()
    T = open(sch).read().splitlines()
    m = re.search(r'\$Descr \S+ (\d+) (\d+)', "\n".join(T)); W, H = int(m.group(1)), int(m.group(2))
    o = []
    i = 0
    def X(x): return x
    while i < len(T):
        l = T[i]
        if l.startswith('L '):
            _, sname, ref = l.split()
            sname = sname.split(':')[-1]
            x, y = map(int, T[i + 2].split()[1:3])
            val = re.search(r'F 1 "([^"]*)" H (-?\d+) (-?\d+)', "\n".join(T[i:i + 8]))
            rf = re.search(r'F 0 "([^"]*)" H (-?\d+) (-?\d+)', "\n".join(T[i:i + 8]))
            for d in syms.get(sname, []):
                p = d.split()
                if p[0] == 'S':
                    a, b, c, e = map(int, p[1:5])
                    o.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="#822" stroke-width="10"/>' %
                             (x + min(a, c), y - max(b, e), abs(c - a), abs(e - b), "#fff6d8" if p[-1] == 'f' else "none"))
                elif p[0] == 'P':
                    n = int(p[1]); pts = list(map(int, p[5:5 + 2 * n]))
                    s = " ".join("%d,%d" % (x + pts[k], y - pts[k + 1]) for k in range(0, len(pts), 2))
                    o.append('<polyline points="%s" fill="%s" stroke="#822" stroke-width="10"/>' % (s, "#822" if p[-1] == 'F' else "none"))
                elif p[0] == 'C':
                    o.append('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="#822" stroke-width="10"/>' % (x + int(p[1]), y - int(p[2]), int(p[3])))
                elif p[0] == 'X':
                    px, py, ln, ori = int(p[3]), int(p[4]), int(p[5]), p[6]
                    dx, dy = {'U': (0, ln), 'D': (0, -ln), 'L': (-ln, 0), 'R': (ln, 0)}[ori]
                    o.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#822" stroke-width="10"/>' % (x + px, y - py, x + px + dx, y - py - dy))
                    if p[1] != '~' and sname not in ('POT',):
                        o.append('<text x="%d" y="%d" font-size="42" fill="#822" text-anchor="middle">%s</text>' % (x + px + dx * 1.6, y - py - dy * 1.6 + 15, p[1]))
            if rf:
                o.append('<text x="%s" y="%s" font-size="50" fill="#068">%s</text>' % (rf.group(2), rf.group(3), rf.group(1)))
            if val:
                o.append('<text x="%s" y="%s" font-size="50" fill="#068">%s</text>' % (val.group(2), val.group(3), val.group(1)))
        if l.startswith('Wire Wire Line'):
            a, b, c, d = map(int, T[i + 1].split())
            o.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#070" stroke-width="10"/>' % (a, b, c, d))
        if l.startswith('Connection'):
            a, b = map(int, l.split()[2:4])
            o.append('<circle cx="%d" cy="%d" r="22" fill="#070"/>' % (a, b))
        if l.startswith('NoConn'):
            a, b = map(int, l.split()[2:4])
            o.append('<text x="%d" y="%d" font-size="60" fill="#00f" text-anchor="middle">x</text>' % (a, b + 20))
        if l.startswith('Text Label') or l.startswith('Text Notes'):
            p = l.split(); x, y, ori = int(p[2]), int(p[3]), int(p[4])
            sz = 50 if 'Label' in l else int(p[5])
            col = '#a40' if 'Label' in l else '#555'
            t = T[i + 1]
            if ori in (0, 2):
                o.append('<text x="%d" y="%d" font-size="%d" text-anchor="%s" fill="%s">%s</text>' % (x, y - 8, sz, 'end' if ori == 2 else 'start', col, t))
            else:
                rot = -90 if ori == 1 else 90
                o.append('<text x="%d" y="%d" font-size="%d" fill="%s" transform="rotate(%d %d %d)" dy="-8">%s</text>' % (x, y, sz, col, rot, x, y, t))
        i += 1
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" style="background:#fff;font-family:monospace">%s</svg>' % (W, H, W // scale, H // scale, ''.join(o))
    hp = out + '.html'
    open(hp, 'w').write('<html><body style="margin:0">' + svg + '</body></html>')
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={'width': W // scale, 'height': H // scale})
        pg.goto('file://' + os.path.abspath(hp)); pg.screenshot(path=out); b.close()
    os.remove(hp)

if __name__ == "__main__":
    render(*sys.argv[1:4], scale=int(sys.argv[4]) if len(sys.argv) > 4 else 8)
