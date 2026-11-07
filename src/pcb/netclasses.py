# Klasy sieci (net classes) dla EasyEDA - miedz 1 oz (szerokosci z zapasem)
# (klasa, szerokosc mm, odstep mm, odstep specjalny, sieci, uwagi)
import csv, os

CLASSES = {
    "kanal": [
        ("HV", 0.6, 2.5, "", "B+3 B+2", "460-465 V, kilkanascie mA"),
        ("ANODA", 0.5, 1.25, "2,5 do HV i BIAS", "B+1 ANODE_A ANODE_B", "270-290 V; 1,25 mm = IPC-2221 do 300 V, miesci sie miedzy nozkami podstawki"),
        ("HV_MID", 0.4, 1.0, "2,5 do BIAS", "A_EF TAIL G_A G_B N_GB G2_EF CC_MID STEP", "73-150 V"),
        ("BIAS", 0.4, 1.0, "3,0 do HV/ANODA", "VBIAS BIAS_T BIAS_B BMID_T BMID_B GRID_T GRID_B", "-25...-78 V; GRID_T/B krotko, z dala od anod"),
        ("ZARZENIE", 1.0, 0.5, "", "HTR_A HTR_B", "ok. 0,6 A, +42 V; parami obok siebie"),
        ("CZULE", 0.4, 0.3, "", "IN IN2 G1_EF K_EF FB", "wejscie i NFB: krotko, przy masie, z dala od HV i zarzenia"),
        ("GND", 1.0, 0.3, "", "GND", "albo wylewka w strefie wejscia"),
    ],
    "zasilacz_siec": [
        ("SIEC_230", 2.0, 3.0, "6,0 do CEWKI", "L_SW L_K1 L_TR N_SW L_TR2", "ok. 1,8 A + udar; izolacja wzmocniona do 12 V"),
        ("HT_AC", 1.5, 3.0, "6,0 do CEWKI", "HT_TR HT_F", "uzwojenie S1 360 V przez F3"),
        ("BIAS_AC", 0.5, 1.0, "", "B_AC1 B_AC2 VB_RAW VBIAS", "+-92 V, kilka mA"),
        ("ZARZENIE_3", 2.0, 0.5, "", "H3_A H3_B", "S3 rozdzielane na 2 kanaly, ok. 1,2 A"),
        ("ZARZENIE_2", 0.5, 0.5, "", "H2_A H2_B", "tylko R11/R12; 3,0 mm jesli 6,4 A KT88 idzie przez plytke"),
        ("ELEW", 0.5, 0.5, "", "HTR_ELEV", "+42 V, prad znikomy"),
        ("CEWKI", 0.5, 0.3, "6,0 do SIEC_230/HT_AC", "+12V RLY1 RLY2", "ok. 50 mA na cewke"),
        ("GND", 1.0, 0.3, "", "GND", ""),
    ],
    "zasilacz_hv": [
        ("HT_AC", 1.5, 3.0, "6,0 do CEWKI", "HT_AC1 HT_AC2 HT_K3 K3_MID HT_IN", "360 V AC (510 V szczyt), impulsy ladowania C1"),
        ("HV_DC", 1.5, 3.0, "6,0 do CEWKI", "HV_RAW B+3", "465-510 V; HV_RAW = petla ladowania, B+3 ok. 0,35 A"),
        ("HV_MID", 0.6, 2.0, "", "C1_MID C2_MID HVS1 HVS2 ELEV_MID LED_M", "155-255 V, srodki baterii, dzielnik pomiarowy, srodek R140A/B"),
        ("POMIAR", 0.4, 0.5, "3,0 do HV_DC/HT_AC", "HV_SENSE HTR_ELEV", "HV_SENSE ok. 2 V do ADS1115"),
        ("CEWKI", 0.5, 0.3, "6,0 do HT_AC/HV_DC", "+12V RLY3 RLY4", "strona sterowania K3/K4"),
        ("GND_LAD", 2.0, 0.3, "", "GND", "powrot petli ladowania; gwiazda J15"),
    ],
    "sterowanie": [
        ("SIEC_230", 0.8, 3.0, "6,0 do wszystkich innych", "L_PS N_PS", "230 V do PS1 (IRM-15-12), ok. 0,1 A; tylko miedzy J1 a PS1"),
        ("WE_BIAS", 0.4, 1.5, "", "VBIAS", "-78 V wchodzi na plytke; krotko, z dala od 3V3/ESP32"),
        ("ZASIL", 0.8, 0.3, "", "+12V +5V", "cewki 8 przekaznikow (ok. 0,3 A) + przetwornica 5 V"),
        ("ANALOG", 0.3, 0.3, "", "IK_L1F IK_L2F IK_R1F IK_R2F VB_F HV_F", "wejscia ADS1115; z dala od ESP32 i DRV/RLY"),
        ("KOREKTA", 0.3, 0.3, "", "DAC_L1 DAC_L2 DAC_R1 DAC_R2 DACF_L1 DACF_L2 DACF_R1 DACF_R2 FB_L1 FB_L2 FB_R1 FB_R2 OA_L1 OA_L2 OA_R1 OA_R2",
         "DAC -> LM324 -> filtr RC; krotko, z dala od ESP32 i przetwornicy"),
        ("BIAS_KOR", 0.3, 1.5, "", "S_L1 S_L2 S_R1 S_R2 BI_L1 BI_L2 BI_R1 BI_R2", "ok. -50 V: przesuwnik R23-R30 i wyjscia R31-R34 do J10; krotko"),
        ("GND", 1.0, 0.3, "", "GND", "wylewka obustronna"),
    ],
    "glosniki": [
        ("GLOSNIK", 2.0, 0.5, "", "MAR_LP MAR_LN MAR_RP MAR_RN TUBE_LP TUBE_LN TUBE_RP TUBE_RN SPK_LP SPK_LN SPK_RP SPK_RN",
         "do ok. 5 A skutecznie (Marantz 100 W / 4 Ohm); sciezki obustronnie lub szerzej, jesli sie zmiesci"),
        ("CEWKI", 0.5, 0.3, "", "+12V RLY_SPK", "2 x 33 mA"),
    ],
    "ul": [
        ("UL_HV", 0.8, 2.5, "6,0 do CEWKI", "AN_A UL_A G2_A AN_B UL_B G2_B",
         "ok. 465 V DC + sygnal (anoda do ok. 850 V szczyt); bez wylewki masy"),
        ("CEWKI", 0.5, 0.3, "6,0 do UL_HV", "+12V RLY_UL", "cewki 2 x 33 mA"),
    ],
}
DEFAULT = (0.4, 0.3)


def check(board):
    nets = set(board.nets())
    for cl in CLASSES[board.name]:
        for n in cl[4].split():
            assert n in nets, (board.name, cl[0], n)


def write_csv(board, dirpath):
    check(board)
    p = os.path.join(dirpath, board.name + "_klasy_sieci.csv")
    with open(p, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["Klasa", "Szerokosc [mm]", "Odstep [mm]", "Odstep do innych klas", "Sieci", "Uwagi"])
        for k, tw, cl, sp, nets, note in CLASSES[board.name]:
            w.writerow([k, str(tw).replace(".", ","), str(cl).replace(".", ","), sp, nets, note])
        w.writerow(["Default", "0,4", "0,3", "", "(pozostale sieci)", ""])
