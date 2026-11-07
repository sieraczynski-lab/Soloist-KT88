import os, sys, shutil, zipfile
import sch_kanal, sch_psu, netclasses, jlc, bom_lcsc
from pcbgen import SYM
WIRED = {"kanal": sch_kanal.build, "zasilacz_siec": sch_psu.build_siec, "zasilacz_hv": sch_psu.build_hv, "sterowanie": sch_psu.build_ctl, "ul": sch_psu.build_ul, "glosniki": sch_psu.build_glosniki}

def write_lib_syms(path, names, prefix=""):
    o = ["EESchema-LIBRARY Version 2.4" if prefix else "EESchema-LIBRARY Version 2.3", "#encoding utf-8"]
    for u in names:
        t = SYM[u].lib_text()
        if prefix:
            t = t.replace("# %s\n" % u, "# %s%s\n" % (prefix, u), 1).replace("DEF %s " % u, "DEF %s%s " % (prefix, u), 1).replace('F1 "%s"' % u, 'F1 "%s%s"' % (prefix, u), 1)
        o.append(t)
    o += ["#", "#End Library", ""]
    open(path, "w").write("\n".join(o))

D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
from boards import BOARDS
from render import render

OUT = os.path.join(D, "Soloist88_PCB")
LIB = "soloist88"

PRO = """update=
version=1
last_client=eeschema
[eeschema]
version=1
LibDir=
[eeschema/libraries]
LibName1={lib}
[pcbnew]
version=1
"""

README = open(os.path.join(D, "README.txt"), encoding="utf-8").read()

def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    imp = os.path.join(OUT, "1_import_EasyEDA"); os.makedirs(imp)
    kic = os.path.join(OUT, "2_projekty_KiCad", "KiCad4_dla_EasyEDA_Standard"); os.makedirs(kic)
    kic5 = os.path.join(OUT, "2_projekty_KiCad", "KiCad5_dla_EasyEDA_Pro"); os.makedirs(kic5)
    pak = os.path.join(OUT, "3_pakiet_awaryjny"); os.makedirs(pak)
    jl = os.path.join(OUT, "4_montaz_SMD_JLCPCB"); os.makedirs(jl)
    for fn in BOARDS:
        b = fn()
        pd = os.path.join(kic, b.name); os.makedirs(pd)
        sch = os.path.join(pd, b.name + ".sch")
        lib = os.path.join(pd, LIB + ".lib")
        cache = os.path.join(pd, b.name + "-cache.lib")
        pcb = os.path.join(pd, b.name + ".kicad_pcb")
        S = WIRED[b.name]()
        errs = S.verify()
        assert not errs, (b.name, errs)
        S.write(sch, LIB, v5=False)
        write_lib_syms(lib, S.used_symbols())
        shutil.copy(lib, cache)
        b.write_pcb(pcb, LIB)
        open(os.path.join(pd, b.name + ".pro"), "w").write(PRO.format(lib=LIB))
        with zipfile.ZipFile(os.path.join(imp, b.name + "_Standard_schemat.zip"), "w", zipfile.ZIP_DEFLATED) as z:
            for p in (sch, lib, cache, os.path.join(pd, b.name + ".pro")):
                z.write(p, os.path.basename(p))
        with zipfile.ZipFile(os.path.join(imp, b.name + "_Standard_pcb.zip"), "w", zipfile.ZIP_DEFLATED) as z:
            z.write(pcb, os.path.basename(pcb))
        # KiCad 5.1 project for EasyEDA Pro
        p5 = os.path.join(kic5, b.name); os.makedirs(p5)
        S = WIRED[b.name]()
        S.write(os.path.join(p5, b.name + ".sch"), LIB, v5=True)
        write_lib_syms(os.path.join(p5, LIB + ".lib"), S.used_symbols())
        write_lib_syms(os.path.join(p5, b.name + "-cache.lib"), S.used_symbols(), prefix=LIB + "_")
        b.write_pcb(os.path.join(p5, b.name + ".kicad_pcb"), LIB, v5=True)
        open(os.path.join(p5, b.name + ".pro"), "w").write(PRO.format(lib=LIB))
        open(os.path.join(p5, "sym-lib-table"), "w").write(
            '(sym_lib_table\n  (lib (name %s)(type Legacy)(uri ${KIPRJMOD}/%s.lib)(options "")(descr "Soloist 88"))\n)\n' % (LIB, LIB))
        open(os.path.join(p5, "fp-lib-table"), "w").write("(fp_lib_table\n)\n")
        with zipfile.ZipFile(os.path.join(imp, b.name + "_EasyEDA_Pro.zip"), "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(os.listdir(p5)):
                z.write(os.path.join(p5, f), f)
        b.write_csv(pak)
        netclasses.write_csv(b, pak)
        jlc.write_bom(b, jl)
    bom_lcsc.main(os.path.join(OUT, "5_BOM_czesci_LCSC"))
    render(pak, pdf=True)
    for f in os.listdir(pak):
        if f.endswith(".html"):
            os.remove(os.path.join(pak, f))
    open(os.path.join(OUT, "CZYTAJ_MNIE.txt"), "w", encoding="utf-8").write(README)
    zp = os.path.join(D, "Soloist88_PCB_v0.23.zip")
    if os.path.exists(zp):
        os.remove(zp)
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(OUT):
            for f in sorted(files):
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, D))
    print(zp)

if __name__ == "__main__":
    main()
