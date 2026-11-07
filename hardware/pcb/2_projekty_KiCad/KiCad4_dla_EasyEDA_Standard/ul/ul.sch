EESchema Schematic File Version 2
LIBS:soloist88
EELAYER 25 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title "Soloist 88 - przelacznik UL/trioda (x2)"
Date ""
Rev "0.4"
Comp ""
Comment1 "Soloist 88 Stereo"
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L CONNR_3 J1
U 1 1 5A91B54A
P 1500 2500
F 0 "J1" H 1400 2210 50  0000 L CNN
F 1 "LAMPA_A" H 1400 2290 50  0000 L CNN
F 2 "soloist88:TerminalBlock_1x03_P7.62_V" H 1500 2500 50  0001 C CNN
F 3 "" H 1500 2500 50  0001 C CNN
	1    1500 2500
	1    0    0    -1  
$EndComp
$Comp
L RELAY_G2RL K1
U 1 1 538A840B
P 4000 2600
F 0 "K1" H 3750 2090 50  0000 L CNN
F 1 "G2RL-2-DC12" H 3750 2170 50  0000 L CNN
F 2 "soloist88:Relay_DPDT_Omron_G2RL" H 4000 2600 50  0001 C CNN
F 3 "" H 4000 2600 50  0001 C CNN
F 4 "LCSC" H 4000 2600 50  0001 C CNN "Supplier"
F 5 "C61458" H 4000 2600 50  0001 C CNN "Supplier Part"
	1    4000 2600
	1    0    0    -1  
$EndComp
$Comp
L CONNR_3 J2
U 1 1 5398E4F0
P 1500 4600
F 0 "J2" H 1400 4310 50  0000 L CNN
F 1 "LAMPA_B" H 1400 4390 50  0000 L CNN
F 2 "soloist88:TerminalBlock_1x03_P7.62_V" H 1500 4600 50  0001 C CNN
F 3 "" H 1500 4600 50  0001 C CNN
	1    1500 4600
	1    0    0    -1  
$EndComp
$Comp
L RELAY_G2RL K2
U 1 1 5A83D5B1
P 4000 4700
F 0 "K2" H 3750 4190 50  0000 L CNN
F 1 "G2RL-2-DC12" H 3750 4270 50  0000 L CNN
F 2 "soloist88:Relay_DPDT_Omron_G2RL" H 4000 4700 50  0001 C CNN
F 3 "" H 4000 4700 50  0001 C CNN
F 4 "LCSC" H 4000 4700 50  0001 C CNN "Supplier"
F 5 "C61458" H 4000 4700 50  0001 C CNN "Supplier Part"
	1    4000 4700
	1    0    0    -1  
$EndComp
$Comp
L CONNR_2 J3
U 1 1 549FD466
P 1500 6400
F 0 "J3" H 1400 6160 50  0000 L CNN
F 1 "CEWKI" H 1400 6240 50  0000 L CNN
F 2 "soloist88:TerminalBlock_1x02_P5.08_V" H 1500 6400 50  0001 C CNN
F 3 "" H 1500 6400 50  0001 C CNN
	1    1500 6400
	1    0    0    -1  
$EndComp
$Comp
L D_V D1
U 1 1 541298C4
P 3000 6400
F 0 "D1" H 3070 6380 50  0000 L CNN
F 1 "1N4148" H 3070 6460 50  0000 L CNN
F 2 "soloist88:D_DO-35_P7.62_V" H 3000 6400 50  0001 C CNN
F 3 "" H 3000 6400 50  0001 C CNN
	1    3000 6400
	1    0    0    -1  
$EndComp
$Comp
L D_V D2
U 1 1 5D1BC97E
P 3600 6400
F 0 "D2" H 3670 6380 50  0000 L CNN
F 1 "1N4148" H 3670 6460 50  0000 L CNN
F 2 "soloist88:D_DO-35_P7.62" H 3600 6400 50  0001 C CNN
F 3 "" H 3600 6400 50  0001 C CNN
	1    3600 6400
	1    0    0    -1  
$EndComp
Wire Wire Line
	3000 6100 3000 6250
Wire Wire Line
	3000 6100 3300 6100
Wire Wire Line
	3300 6100 3600 6100
Wire Wire Line
	3600 6100 3600 6250
Wire Wire Line
	3000 6550 3000 6700
Wire Wire Line
	3000 6700 3300 6700
Wire Wire Line
	3300 6700 3600 6700
Wire Wire Line
	3600 6550 3600 6700
Wire Wire Line
	3300 6000 3300 6100
Wire Wire Line
	3300 6700 3300 6800
Wire Wire Line
	1800 2400 1900 2400
Wire Wire Line
	1800 2500 1900 2500
Wire Wire Line
	1800 2600 1900 2600
Wire Wire Line
	3500 2400 3600 2400
Wire Wire Line
	3500 2500 3600 2500
Wire Wire Line
	4400 2300 4500 2300
Wire Wire Line
	4400 2400 4500 2400
Wire Wire Line
	4400 2500 4500 2500
Wire Wire Line
	4400 2700 4500 2700
Wire Wire Line
	4400 2800 4500 2800
Wire Wire Line
	4400 2900 4500 2900
Wire Wire Line
	1800 4500 1900 4500
Wire Wire Line
	1800 4600 1900 4600
Wire Wire Line
	1800 4700 1900 4700
Wire Wire Line
	3500 4500 3600 4500
Wire Wire Line
	3500 4600 3600 4600
Wire Wire Line
	4400 4400 4500 4400
Wire Wire Line
	4400 4500 4500 4500
Wire Wire Line
	4400 4600 4500 4600
Wire Wire Line
	4400 4800 4500 4800
Wire Wire Line
	4400 4900 4500 4900
Wire Wire Line
	4400 5000 4500 5000
Wire Wire Line
	1800 6350 1900 6350
Wire Wire Line
	1800 6450 1900 6450
Connection ~ 3300 6100
Connection ~ 3300 6700
Text Label 3300 6000 1    50   ~ 0
+12V
Text Label 3300 6800 3    50   ~ 0
RLY_UL
Text Label 1900 2400 0    50   ~ 0
AN_A
Text Label 1900 2500 0    50   ~ 0
UL_A
Text Label 1900 2600 0    50   ~ 0
G2_A
Text Label 3500 2400 2    50   ~ 0
+12V
Text Label 3500 2500 2    50   ~ 0
RLY_UL
Text Label 4500 2300 0    50   ~ 0
G2_A
Text Label 4500 2400 0    50   ~ 0
UL_A
Text Label 4500 2500 0    50   ~ 0
AN_A
Text Label 4500 2700 0    50   ~ 0
G2_A
Text Label 4500 2800 0    50   ~ 0
UL_A
Text Label 4500 2900 0    50   ~ 0
AN_A
Text Label 1900 4500 0    50   ~ 0
AN_B
Text Label 1900 4600 0    50   ~ 0
UL_B
Text Label 1900 4700 0    50   ~ 0
G2_B
Text Label 3500 4500 2    50   ~ 0
+12V
Text Label 3500 4600 2    50   ~ 0
RLY_UL
Text Label 4500 4400 0    50   ~ 0
G2_B
Text Label 4500 4500 0    50   ~ 0
UL_B
Text Label 4500 4600 0    50   ~ 0
AN_B
Text Label 4500 4800 0    50   ~ 0
G2_B
Text Label 4500 4900 0    50   ~ 0
UL_B
Text Label 4500 5000 0    50   ~ 0
AN_B
Text Label 1900 6350 0    50   ~ 0
+12V
Text Label 1900 6450 0    50   ~ 0
RLY_UL
Text Notes 800 1300 0    60   ~ 16
Przelacznik UL / trioda - jedna plytka na kanal (2 x KT88)
Text Notes 800 1420 0    60   ~ 16
Cewka bez zasilania: G2 <- odczep UL (normalnie). Cewka zasilona: G2 <- anoda (trioda).
Text Notes 800 1540 0    60   ~ 16
PRZELACZAC TYLKO PRZY WYLACZONYM B+ (ESP32: K3/K4 off, czekaj na B+ < 30 V, przelacz, start).
Text Notes 800 1660 0    60   ~ 16
Rezystor siatki ekranowej R123/R124 (270R 2W) zostaje przy nozce 4 podstawki KT88.
Text Notes 5200 2300 0    60   ~ 16
G2RL-2: oba styki rownolegle
Text Notes 800 7300 0    60   ~ 16
J3: z plytki sterowania J11 (+12 V, RLY_UL)
$EndSCHEMATC
