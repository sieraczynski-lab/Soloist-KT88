import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model
from zrender import render
allp = model.parts + model.ref
out = os.path.dirname(os.path.abspath(__file__))
render(allp, os.path.join(out, "widok_przod.png"), azim=-62, elev=24, title="Soloist 88 - obudowa (propozycja v0.1)")
render(allp, os.path.join(out, "widok_tyl.png"), azim=118, elev=26, title="Widok z tylu")
render(allp, os.path.join(out, "widok_wnetrze.png"), azim=-58, elev=38, title="Wnetrze (bez pokrywy, drewna i dachu trafo)",
       skip=("AL_pokrywa", "DREWNO", "AL_trafo_dach", "SS_", "REF_pret", "REF_nakretka", "REF_galka", "REF_przycisk", "REF_LED", "REF_wyswietl"))
render(model.parts, os.path.join(out, "widok_czesci.png"), azim=-62, elev=24, title="Same czesci do wykonania")
