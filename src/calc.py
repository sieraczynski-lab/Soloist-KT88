import math
p = print
# --- KT88 operating point ---
Bp = 465.0; Iq = 0.055; Rpri_half = 65.5/2; Rk = 10
Va = Bp - Iq*Rpri_half; Vk = Iq*Rk
p("KT88 Va=%.1f Vk=%.2f Pa=%.1f W" % (Va, Vk, (Va-Vk)*Iq))
Pout = 45; RL=4
p("Vout full power 4ohm: %.2f Vrms" % math.sqrt(Pout*RL))

# --- bias network per tube: -Vb -> Ra -> N -> (P + Rb) -> GND, N -> Rg -> grid
Vb=80; Ra=27e3; Rb=27e3; P=50e3
for pv in (0, 25e3, 50e3):
    print("bias P=%.0fk: %.1f V" % (pv/1e3, -Vb*(pv+Rb)/(Ra+pv+Rb)))
Ib_max = Vb/(Ra+Rb); p("bias current/tube max %.2f mA, 4 tubes %.1f mA" % (Ib_max*1e3, 4*Ib_max*1e3))
Rth = Ra*(P+Rb)/(Ra+P+Rb); p("grid DC resistance worst %.0f k" % ((Rth+100e3)/1e3))
p("coupling fc 0.47uF: %.2f Hz" % (1/(2*math.pi*0.47e-6*(Rth+100e3))))

# bias supply: 65VAC bridge, C-R-C, load
Vpk = 65*math.sqrt(2) - 1.4; Il = 4*Ib_max + 0.03e-3 + 0.25e-3
for R in (1.5e3, 2.2e3):
    p("bias rail with R5=%.1fk: ~%.1f V (load %.1f mA)" % (R/1e3, Vpk - 3 - Il*R, Il*1e3))

# ADC offset divider for bias rail: +3.3 via R1 to node, R2 to rail
R1=10e3; R2=330e3
for v in (-90, -80, -70, -60, 0):
    vn = (3.3*R2 + v*R1)/(R1+R2)
    p("bias %4d V -> ADC %.3f V" % (v, vn))

# cathode sense via 10 ohm
for i in (0.03, 0.055, 0.08, 0.12):
    p("Ik %3.0f mA -> %.3f V" % (i*1e3, i*10))

# --- LTP E88CC ---
Itail=0.014; Rl=27e3; Bltp=460; Vg=81; Vk_ltp = Vg+6
Va_l = Bltp - Itail/2*Rl
p("LTP Va=%.0f Vak=%.0f Pa=%.2f W/section" % (Va_l, Va_l-Vk_ltp, (Va_l-Vk_ltp)*Itail/2))
p("CCS dissipation %.2f W" % (Vk_ltp*Itail))

# --- EF86 ---
Ik_ef = 0.82/330; p("EF86 Ik=%.2f mA" % (Ik_ef*1e3))
# EF86 node: from ECC88 B+ 460 via R2 68k, load EF86 2.5mA
p("EF86 B+ = %.0f V" % (460 - 68e3*Ik_ef))
p("heater elevation 270k/27k from 460: %.1f V" % (460*27/297))

# --- NFB ---
beta8 = 330/(39e3+330); p("orig beta=%.5f gain=%.0f" % (beta8, 1/beta8))
R17 = 39e3/math.sqrt(2); p("R17 for 4ohm tap ~ %.0f" % R17)
beta4 = 330/(27e3+330); p("beta 27k=%.5f closed gain=%.1f, sens for 45W/4R=%.0f mV" % (beta4, 1/beta4, math.sqrt(45*4)*beta4*1e3))
p("C13 for same tau: %.0f pF" % (39e3*82e-12/27e3*1e12))
p("input HPF 47nF/220k: %.1f Hz" % (1/(2*math.pi*47e-9*220e3)))

# --- PSU ---
Vac=360; Ihtdc=0.30
p("HT peak %.0f V, +10%% mains unloaded %.0f V" % (Vac*1.414, Vac*1.1*1.414))
C1 = 235e-6
p("C1 ripple p-p %.1f V" % (Ihtdc/(100*C1)))
XL = 2*math.pi*100*5; XC = 1/(2*math.pi*100*235e-6)
p("LC atten %.0f -> ripple KT88 B+ %.0f mVpp" % (XL/XC, Ihtdc/(100*C1)/(XL/XC)*1e3))
p("LC resonance %.1f Hz" % (1/(2*math.pi*math.sqrt(5*235e-6))))
XC3 = 1/(2*math.pi*100*220e-6)
p("RC 330R/220u atten %.0f" % (330/XC3))
p("bleed 2x220k at 470V: %.2f mA, %.2f W each, tau %.0f s" % (470/440e3*1e3, (235)**2/220e3, 440e3*235e-6))
VA = 360*0.6 + 6.3*7 + 6.3*2 + 65*0.05
p("transformer VA %.0f" % VA)
