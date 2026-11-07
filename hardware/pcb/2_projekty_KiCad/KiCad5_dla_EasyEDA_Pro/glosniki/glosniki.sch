EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title "Soloist 88 - przelacznik glosnikow Marantz / Lampa"
Date ""
Rev "0.4"
Comp ""
Comment1 "Soloist 88 Stereo"
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L soloist88:RELAY_G2RL K1
U 1 1 538A840B
P 4200 2600
F 0 "K1" H 3950 2090 50  0000 L CNN
F 1 "G2RL-2-DC12" H 3950 2170 50  0000 L CNN
F 2 "soloist88:Relay_DPDT_Omron_G2RL" H 4200 2600 50  0001 C CNN
F 3 "~" H 4200 2600 50  0001 C CNN
F 4 "LCSC" H 4200 2600 50  0001 C CNN "Supplier"
F 5 "C61458" H 4200 2600 50  0001 C CNN "Supplier Part"
	1    4200 2600
	1    0    0    -1  
$EndComp
$Comp
L soloist88:CONNR_2 J1
U 1 1 5A91B54A
P 1500 2150
F 0 "J1" H 1400 1910 50  0000 L CNN
F 1 "MARANTZ_L" H 1400 1990 50  0000 L CNN
F 2 "soloist88:TerminalBlock_1x02_P5.08" H 1500 2150 50  0001 C CNN
F 3 "~" H 1500 2150 50  0001 C CNN
	1    1500 2150
	1    0    0    -1  
$EndComp
$Comp
L soloist88:CONNR_2 J2
U 1 1 5398E4F0
P 1500 3050
F 0 "J2" H 1400 2810 50  0000 L CNN
F 1 "LAMPA_L" H 1400 2890 50  0000 L CNN
F 2 "soloist88:TerminalBlock_1x02_P5.08" H 1500 3050 50  0001 C CNN
F 3 "~" H 1500 3050 50  0001 C CNN
	1    1500 3050
	1    0    0    -1  
$EndComp
$Comp
L soloist88:CONN_2 J3
U 1 1 549FD466
P 6800 2550
F 0 "J3" H 6650 2310 50  0000 L CNN
F 1 "KOLUMNA_L" H 6650 2390 50  0000 L CNN
F 2 "soloist88:TerminalBlock_1x02_P5.08" H 6800 2550 50  0001 C CNN
F 3 "~" H 6800 2550 50  0001 C CNN
	1    6800 2550
	1    0    0    -1  
$EndComp
$Comp
L soloist88:RELAY_G2RL K2
U 1 1 5A83D5B1
P 4200 5300
F 0 "K2" H 3950 4790 50  0000 L CNN
F 1 "G2RL-2-DC12" H 3950 4870 50  0000 L CNN
F 2 "soloist88:Relay_DPDT_Omron_G2RL" H 4200 5300 50  0001 C CNN
F 3 "~" H 4200 5300 50  0001 C CNN
F 4 "LCSC" H 4200 5300 50  0001 C CNN "Supplier"
F 5 "C61458" H 4200 5300 50  0001 C CNN "Supplier Part"
	1    4200 5300
	1    0    0    -1  
$EndComp
$Comp
L soloist88:CONNR_2 J4
U 1 1 5AFB41C5
P 1500 4850
F 0 "J4" H 1400 4610 50  0000 L CNN
F 1 "MARANTZ_R" H 1400 4690 50  0000 L CNN
F 2 "soloist88:TerminalBlock_1x02_P5.08" H 1500 4850 50  0001 C CNN
F 3 "~" H 1500 4850 50  0001 C CNN
	1    1500 4850
	1    0    0    -1  
$EndComp
$Comp
L soloist88:CONNR_2 J5
U 1 1 5DFC7153
P 1500 5750
F 0 "J5" H 1400 5510 50  0000 L CNN
F 1 "LAMPA_R" H 1400 5590 50  0000 L CNN
F 2 "soloist88:TerminalBlock_1x02_P5.08" H 1500 5750 50  0001 C CNN
F 3 "~" H 1500 5750 50  0001 C CNN
	1    1500 5750
	1    0    0    -1  
$EndComp
$Comp
L soloist88:CONN_2 J6
U 1 1 54F520E9
P 6800 5250
F 0 "J6" H 6650 5010 50  0000 L CNN
F 1 "KOLUMNA_R" H 6650 5090 50  0000 L CNN
F 2 "soloist88:TerminalBlock_1x02_P5.08" H 6800 5250 50  0001 C CNN
F 3 "~" H 6800 5250 50  0001 C CNN
	1    6800 5250
	1    0    0    -1  
$EndComp
$Comp
L soloist88:CONNR_2 J7
U 1 1 53F2107F
P 1500 7200
F 0 "J7" H 1400 6960 50  0000 L CNN
F 1 "CEWKI" H 1400 7040 50  0000 L CNN
F 2 "soloist88:PinHeader_1x02_P2.54" H 1500 7200 50  0001 C CNN
F 3 "~" H 1500 7200 50  0001 C CNN
	1    1500 7200
	1    0    0    -1  
$EndComp
$Comp
L soloist88:D_V D1
U 1 1 541298C4
P 3000 7200
F 0 "D1" H 3070 7180 50  0000 L CNN
F 1 "1N4148" H 3070 7260 50  0000 L CNN
F 2 "soloist88:D_DO-35_P7.62" H 3000 7200 50  0001 C CNN
F 3 "~" H 3000 7200 50  0001 C CNN
	1    3000 7200
	1    0    0    -1  
$EndComp
$Comp
L soloist88:D_V D2
U 1 1 5D1BC97E
P 3600 7200
F 0 "D2" H 3670 7180 50  0000 L CNN
F 1 "1N4148" H 3670 7260 50  0000 L CNN
F 2 "soloist88:D_DO-35_P7.62" H 3600 7200 50  0001 C CNN
F 3 "~" H 3600 7200 50  0001 C CNN
	1    3600 7200
	1    0    0    -1  
$EndComp
Wire Wire Line
	3000 6900 3000 7050
Wire Wire Line
	3000 6900 3300 6900
Wire Wire Line
	3300 6900 3600 6900
Wire Wire Line
	3600 6900 3600 7050
Wire Wire Line
	3000 7350 3000 7500
Wire Wire Line
	3000 7500 3300 7500
Wire Wire Line
	3300 7500 3600 7500
Wire Wire Line
	3600 7350 3600 7500
Wire Wire Line
	3300 6800 3300 6900
Wire Wire Line
	3300 7500 3300 7600
Wire Wire Line
	3700 2400 3800 2400
Wire Wire Line
	3700 2500 3800 2500
Wire Wire Line
	4600 2300 4700 2300
Wire Wire Line
	4600 2400 4700 2400
Wire Wire Line
	4600 2500 4700 2500
Wire Wire Line
	4600 2700 4700 2700
Wire Wire Line
	4600 2800 4700 2800
Wire Wire Line
	4600 2900 4700 2900
Wire Wire Line
	1800 2100 1900 2100
Wire Wire Line
	1800 2200 1900 2200
Wire Wire Line
	1800 3000 1900 3000
Wire Wire Line
	1800 3100 1900 3100
Wire Wire Line
	6400 2500 6500 2500
Wire Wire Line
	6400 2600 6500 2600
Wire Wire Line
	3700 5100 3800 5100
Wire Wire Line
	3700 5200 3800 5200
Wire Wire Line
	4600 5000 4700 5000
Wire Wire Line
	4600 5100 4700 5100
Wire Wire Line
	4600 5200 4700 5200
Wire Wire Line
	4600 5400 4700 5400
Wire Wire Line
	4600 5500 4700 5500
Wire Wire Line
	4600 5600 4700 5600
Wire Wire Line
	1800 4800 1900 4800
Wire Wire Line
	1800 4900 1900 4900
Wire Wire Line
	1800 5700 1900 5700
Wire Wire Line
	1800 5800 1900 5800
Wire Wire Line
	6400 5200 6500 5200
Wire Wire Line
	6400 5300 6500 5300
Wire Wire Line
	1800 7150 1900 7150
Wire Wire Line
	1800 7250 1900 7250
Connection ~ 3300 6900
Connection ~ 3300 7500
Text Label 3300 6800 1    50   ~ 0
+12V
Text Label 3300 7600 3    50   ~ 0
RLY_SPK
Text Label 3700 2400 2    50   ~ 0
+12V
Text Label 3700 2500 2    50   ~ 0
RLY_SPK
Text Label 4700 2300 0    50   ~ 0
SPK_LP
Text Label 4700 2400 0    50   ~ 0
MAR_LP
Text Label 4700 2500 0    50   ~ 0
TUBE_LP
Text Label 4700 2700 0    50   ~ 0
SPK_LN
Text Label 4700 2800 0    50   ~ 0
MAR_LN
Text Label 4700 2900 0    50   ~ 0
TUBE_LN
Text Label 1900 2100 0    50   ~ 0
MAR_LP
Text Label 1900 2200 0    50   ~ 0
MAR_LN
Text Label 1900 3000 0    50   ~ 0
TUBE_LP
Text Label 1900 3100 0    50   ~ 0
TUBE_LN
Text Label 6400 2500 2    50   ~ 0
SPK_LP
Text Label 6400 2600 2    50   ~ 0
SPK_LN
Text Label 3700 5100 2    50   ~ 0
+12V
Text Label 3700 5200 2    50   ~ 0
RLY_SPK
Text Label 4700 5000 0    50   ~ 0
SPK_RP
Text Label 4700 5100 0    50   ~ 0
MAR_RP
Text Label 4700 5200 0    50   ~ 0
TUBE_RP
Text Label 4700 5400 0    50   ~ 0
SPK_RN
Text Label 4700 5500 0    50   ~ 0
MAR_RN
Text Label 4700 5600 0    50   ~ 0
TUBE_RN
Text Label 1900 4800 0    50   ~ 0
MAR_RP
Text Label 1900 4900 0    50   ~ 0
MAR_RN
Text Label 1900 5700 0    50   ~ 0
TUBE_RP
Text Label 1900 5800 0    50   ~ 0
TUBE_RN
Text Label 6400 5200 2    50   ~ 0
SPK_RP
Text Label 6400 5300 2    50   ~ 0
SPK_RN
Text Label 1900 7150 0    50   ~ 0
+12V
Text Label 1900 7250 0    50   ~ 0
RLY_SPK
Text Notes 800 1300 0    60   ~ 16
Przelacznik glosnikow Marantz / Lampa - plytka w obudowie trafo (pod lewym TG)
Text Notes 800 1420 0    60   ~ 16
Cewki bez pradu: kolumny <- Marantz (NC). Lampa gotowa (ESP32, DRV7): kolumny <- Lampa (NO).
Text Notes 800 1540 0    60   ~ 16
Przelaczane oba bieguny - wyjscia Marantza i Lampy nigdy nie sa ze soba polaczone.
Text Notes 800 1660 0    60   ~ 16
ESP32 przelacza tylko przy MUTE; R127 (100R 2W) zostaje na wtornym kazdego TG.
Text Notes 800 7900 0    60   ~ 16
J7: z plytki sterowania J13 (+12 V, RLY_SPK)
$EndSCHEMATC
