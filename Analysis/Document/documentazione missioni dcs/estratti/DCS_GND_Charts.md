# DCS — Carte aeroportuali della mappa del Caucaso (DCS_GND_Charts.pdf)

Fonte: `DCS_GND_Charts.pdf`, 34 pagine, "Aerodrome Charts" rev 3.6.0 del 03.05.2013 (10th Gunfighters / Aries,
per DCS A-10C e FC3). Conversione con la skill `pdf-to-markdown` in modalità veloce (pymupdf4llm): la modalità
Docling produceva testo frammentato perché le carte sono disegni vettoriali con etichette sparse.

**Attenzione alla data**: il documento è del 2013. La mappa del Caucaso di DCS è stata aggiornata più volte da allora
(aeroporti e parcheggi). I dati vanno quindi confrontati con quelli letti dal gioco o dal `.miz` (per esempio
`warehouses`, `airports`), che restano la fonte primaria per un registro.

Note sui dati:
- le prue di pista sono date sia magnetiche sia vere (`°T`), con la declinazione magnetica del modulo A-10C (±1°);
- la quota è quella delle testate pista (min..max se le due testate differiscono), in metri;
- i nomi delle taxiway sono stati rivisti dagli autori e **non coincidono** con le designazioni in gioco (p. 3);
- l'indice (p. 4) riporta tra parentesi, accanto al canale TACAN, una frequenza (es. Kobuleti "67X KBL (134.00MHz)")
  di significato non chiaro dal testo: è stata omessa;
- parcheggi e shelter (pp. 13, 16, 20-21 e le singole carte) sono solo grafici: il testo estratto riporta soltanto le
  etichette (P1, S1, ...), non coordinate utilizzabili.

## Registro strutturato (pp. 4-6 e pagine dei singoli aeroporti)

Versione tabellare: `DCS_Aeroporti_Caucaso.csv`.

| N | Aeroporto | ICAO | Nazione | ARP lat | ARP lon | TWR [MHz] | TACAN | ILS [MHz] | Piste [m] (lungh. x largh.) | Quota [m] | Prue mag/vere | Pag. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Kobuleti | UG5X | Georgia | 41°55.797'N | 041°51.809'E | 133.000 | 67X KBL | 07: 111.50 | 07-25 2400x60 | 18 | 07: 064°/070°T; 25: 244°/250°T | 9 |
| 2 | Gudauta | UG23 | Georgia (Abkhazia) | 43°06.856'N | 040°34.187'E | 130.000 |  |  | 15-33 2500x60 | 21 | 15: 145°/151°T; 33: 325°/331°T | 10 |
| 3 | Tbilisi-Soganlug | UG24 | Georgia | 41°38.970'N | 044°56.304'E | 139.000 |  |  | 13-31 2475x80 | 447..459 | 13: 126°/132°T; 31: 306°/312°T | 11 |
| 4 | Vaziani | UG27 | Georgia | 41°37.743'N | 045°01.632'E | 140.000 | 22X VAS | 13: 108.75; 31: 108.75 | 13-31 2485x62 | 451..460 | 13: 129°/135°T; 31: 309°/315°T | 12 |
| 5 | Kutaisi-Kopitnari | UGKO | Georgia | 42°10.657'N | 042°28.874'E | 134.000 | 44X KTS | 08: 109.75 | 08-26 2500x60 | 45 | 08: 068°/074°T; 26: 248°/254°T | 14 |
| 6 | Senaki-Kolkhi | UGKS | Georgia | 42°14.454'N | 042°02.861'E | 132.000 | 31X TSK | 09: 108.90 | 09-27 2375x50 | 11..12 | 09: 088°/094°T; 27: 268°/274°T | 15 |
| 7 | Batumi | UGSB | Georgia | 41°36.562'N | 041°36.034'E | 131.000 | 16X BTM | 13: 110.30 | 13-31 2455x60 | 10 | 13: 120°/126°T; 31: 300°/306°T | 17 |
| 8 | Sukhumi-Babushara | UGSS | Georgia (Abkhazia) | 42°51.677'N | 041°07.474'E | 129.000 |  |  | 12-30 3540x60 | 6..12 | 12: 110°/116°T; 30: 290°/296°T | 18 |
| 9 | Tbilisi-Lochini | UGTB | Georgia | 41°40.095'N | 044°57.283'E | 138.000 |  | 13R: 110.30; 31L: 108.90 | 13R-31L 2920x45 | 465..477 | 13R: 122°/128°T; 31L: 302°/308°T | 19 |
| 10 | Anapa-Vityazevo | URKA | Russia | 45°00.298'N | 037°20.870'E | 121.000 |  |  | 04-22 2900x60 | 45 | 04: 036°/042°T; 22: 216°/222°T | 22 |
| 11 | Gelendzhik | URKG | Russia | 44°34.364'N | 038°00.684'E | 126.000 |  |  | 04-22 1800x60 | 25 | 04: 034°/040°T; 22: 214°/220°T | 23 |
| 12 | Maykop-Khanskaya | URKH | Russia | 44°40.874'N | 040°02.112'E | 125.000 |  |  | 04-22 3200x60 | 180 | 04: 032°/038°T; 22: 212°/218°T | 24 |
| 13 | Krasnodar-Pashkovsky | URKK | Russia | 45°02.276'N | 039°11.282'E | 128.000 |  |  | 05L-23R 2265x60; 05R-23L 3100x60 | 34 | 05: 041°/047°T; 23: 221°/227°T | 25 |
| 14 | Krasnodar-Center | URKL | Russia | 45°05.216'N | 038°56.415'E | 122.000 |  |  | 09-27 2500x60 | 30 | 09: 081°/087°T; 27: 261°/267°T | 26 |
| 15 | Novorossiysk | URKN | Russia | 44°40.084'N | 037°46.694'E | 123.000 |  |  | 04-22 1800x60 | 40 | 04: 036°/042°T; 22: 216°/222°T | 27 |
| 16 | Krymsk | URKW | Russia | 44°58.073'N | 037°59.697'E | 124.000 |  |  | 04-22 2600x60 | 20 | 04: 033°/039°T; 22: 213°/219°T | 28 |
| 17 | Mineralnye Vody | URMM | Russia | 44°13.672'N | 043°04.870'E | 135.000 |  | 12: 111.70; 30: 109.30 | 12-30 4070x60 | 320 | 12: 109°/115°T; 30: 289°/295°T | 29 |
| 18 | Nalchik | URMN | Russia | 43°30.842'N | 043°38.193'E | 136.000 |  | 24: 110.50 | 06-24 2300x60 | 430 | 06: 049°/055°T; 24: 229°/235°T | 30 |
| 19 | Beslan | URMO | Russia | 43°12.342'N | 044°36.346'E | 141.000 |  | 10: 110.50 | 10-28 3015x50 | 540 | 10: 087°/093°T; 28: 267°/273°T | 31 |
| 20 | Sochi-Adler | URSS | Russia | 43°26.669'N | 039°56.489'E | 127.000 |  | 06: 111.10 | 06-24 3100x60; 02-20 2200x60 | 30 | 06: 056°/062°T; 24: 236°/242°T; 02: 019°/025°T; 20: 199°/205°T | 32 |
| 21 | Mozdok | XRMF | Russia | 43°47.504'N | 044°35.981'E | 137.000 |  |  | 08-26 3120x70 | 152..155 | 08: 076°/082°T; 26: 256°/262°T | 34 |

Frequenze comuni a tutti gli aeroporti (dal registro dei beacon, `DCS World List of all available Beacons EN.md`):
257.80 MHz UHF e 122.10 MHz VHF (torre, frequenze combinate aggiuntive), 123.30 MHz (GCA), 344.00 MHz (GCA Search),
385.40 MHz (GCA Final; Kobuleti 385.00).

---

## Conversione integrale (pymupdf4llm)

CON 

# DCS<sup>digital combat simulator</sup> 

## AERODROME CHARTS 



<!-- Start of picture text -->
Consistent with Version 1.2.4<br>ELEV<br>www.10thGunfighters.de<br>www.ariescon.com 98 [ft]<br>30 [m]<br>rev 3.6.0<br>03.05.2013 © dp Fire Station 1<br>Maintenance<br>I<br>Area J<br>J<br>M P3<br>I<br>H<br>G<br>TWR<br>-4 M F<br>G<br>E CON<br>Terminal<br>A-10C D ASR<br>M J<br>PEM<br>& Flaming Cliffs 3 C<br>B<br>M P1<br>3100 x 60[m] / 10170 x 197[ft]<br>XX<br>X<br>APRON 1<br>19-41<br>APRON 21-18 X<br>SHELTERS<br>X<br>X<br>205°T<br>2200 x 60[m] / 7220 x 197[ft]<br>199°<br>X<br>X<br>20<br><!-- End of picture text -->

**J** 

**A** 

ELEV **98** [ft] **30** [m] 



ELEV 

**98** [ft] 

Cargo 

**30** [m] 

Fuel Depot 

Store 

- 02 - 

## TABLE OF CONTENT 

```
Page
```

- 1 Cover 

- 2 Table of Content 

- 3 General Information 

- 4 Aerodrome Index 

- 5 Aerodrome Ground Charts Overview Georgia 

- 6 Aerodrome Ground Charts Overview Russia 

- 7 General Map 

- 8 Aerodrome Ground Charts Legend 

```
Georgian Aerodrome Ground Charts
```

```
Russian Aerodrome Ground Charts
```

- 9 01 - UG5X Kobuleti 

- 10 02 - UG23 Gudauta 11 03 - UG24 Tbilisi - Soganlug 12 04 - UG27 Vaziani 13 04 - UG27 Vaziani ACFT Parking Positions 14 05 - UGKO Kutaisi - Kopitnari 15 06 - UGKS Senaki - Kolkhi 16 06 - UGKS Senaki - Kolkhi ACFT Parking Positions 17 07 - UGSB Batumi 18 08 - UGSS Sukhumi - Babushara 19 09 - UGTB Tbilisi - Lochini 20 09 - UGTB Tbilisi - Lochini ACFT Parking Positions 1/2 21 09 - UGTB Tbilisi - Lochini ACFT Parking Positions 2/2 22 10 - URKA Anapa - Vityazevo 23 11 - URKG Gelendzhik 24 12 - URKH Maykop - Khanskaya 25 13 - URKK Krasnodar - Pashkovsky 26 14 - URKL Krasnodar - Center 27 15 - URKN Novorossiysk 28 16 - URKW Krymsk 29 17 - URMM Mineralnye Vody 30 18 - URMN Nalchik 31 19 - URMO Beslan 32 20 - URSS Sochi - Adler 33 Intentionally Left Blank 34 21 - XRMF Mozdok 

```
rev 3.6.0 - 03.05.2013 © dp - www.10thGunfighters.de - www.ariescon.com
```

- 03 - 

### GENERAL INFORMATION 

`General information` All included ground charts are based on Eagle Dynamics DCS combat flight simulator. This package supports the A-10C & FC3 modules. The Aries Wings ATC software will also contain these charts. Real life aviation procedures were adapted to fit the needs of a flight simulation. Certain rules differ from the real world. Therefore the following charts are intended for use within the simulation only. Visual approach and departure procedures can be found in a separate chart package. `Technical information` - The magnetic variation contained in the DCS A-10C module was taken on the maps with a tolerance of ± 1°. - All tracks are given to magnetic & true north. - All directions and positions correspond to the CDU of the A-10C. - Some runway designations were also adjusted to meet the mentioned variation. The taxiway names have also been revised and do not match the in game TWY designations. This was done to achieve a greater realism and to enable the support for human controlled ATC procedures. `Software source citation` Lock On Flaming Cliffs by Eagle Dynamics `& version number` (GND Charts Version 2.0, 2007) Lock On Flaming Cliffs 2 & DCS BS by Eagle Dynamics (GND Charts Version 2.1, 2.5, 2008/09) DCS A-10C Warthog by Eagle Dynamics (GND Charts Version 3.0, 3.5, 2011/12) DCS A-10C Warthog & FC3 by Eagle Dynamics (GND Charts Version 3.6, 2013) `Procedures and symbology` Amt für Flugsicherung der Bundeswehr, CENOR, various civilian and military `source citation` sources, v 10th Gunfighters, v JaBoG32 `Author` Schleudersitz `Contributors` Asgard, Balu, Bosshog, Chrissi, Laud, Leto, Theoretic, v JaBoG32 `(in alphabetical order) Copyright` dp This project is non-commercial and therefore may not be used commercially by third parties. This document may be used and distributed free of charge. It may be offered for download without further consent of the owner. 

Any alterations of the document are subject to permission of the author. 

```
rev 3.6.0 - 03.05.2013 © dp - www.10thGunfighters.de - www.ariescon.com
```

- 04 - 

## AERODROME INDEX 

```
Georgian Aerodromes
```

|No.|Aerodrome|Location<br>indicator|ARP|TWR|TACAN||RWY|ILS|
|---|---|---|---|---|---|---|---|---|
|**01**|Kobuleti|UG5X|41°55.797`N041°51.809`E|133.000MHz|67X"KBL"|(134.00MHz)|**07**|111.50MHz|
|**02**|Gudauta|UG23|43°06.856`N040°34.187`E|130.000MHz|||||
|**03**|Tbilisi-Soganlug|UG24|41°38.970`N 044°56.304`E|139.000MHz|||||
|**04**|Vaziani|UG27|41°37.743`N 045°01.632`E|140.000MHz|22X"VAS"|(108.50MHz)|**13**|108.75MHz|
||||||||**31**|108.75MHz|
|**05**|Kutaisi-Kopitnari|UGKO|42°10.657`N 042°28.874`E|134.000MHz|44X"KTS"|(110.70MHz)|**08**|109.75MHz|
|**06**|Senaki-Kolkhi|UGKS|42°14.454`N 042°02.861`E|132.000MHz|31X"TSK"|(109.40MHz)|**09**|108.90MHz|
|**07**|Batumi|UGSB|41°36.562`N 041°36.034`E|131.000MHz|16X"BTM"|<br>(135.90MHz)|**13**|110.30MHz|
|**08**|Sukhumi-Babushara|UGSS|42°51.677`N041°07.474`E|129.000MHz|||||
|**09**|Tbilisi-Lochini|UGTB|41°40.095`N 044°57.283`E|138.000MHz|||**13R**|110.30MHz|
||||||||**31L**|108.90MHz|



```
Russian Aerodromes
```

|No.|Aerodrome|Location<br>indicator|ARP|TWR|TACAN|RWY|ILS|
|---|---|---|---|---|---|---|---|
|**10**|Anapa-Vityazevo|URKA|45°00.298`N 037°20.870`E|121.000MHz||||
|**11**|Gelendzhik|URKG|44°34.364`N 038°00.684`E|126.000MHz||||
|**12**|Maykop-Khanskaya|URKH|44°40.874`N 040°02.112`E|125.000MHz||||
|**13**|Krasnodar-Pashkovsky|URKK|45°02.276`N 039°11.282`E|128.000MHz||||
|**14**|Krasnodar-Center|URKL|45°05.216`N 038°56.415`E|122.000MHz||||
|**15**|Novorossiysk|URKN|44°40.084`N 037°46.694`E|123.000MHz||||
|**16**|Krymsk|URKW|44°58.073`N 037°59.697`E|124.000MHz||||
|**17**|MineralnyeVody|URMM|44°13.672`N 043°04.870`E|135.000MHz||**12**|111.70MHz|
|||||||**30**|109.30MHz|
|**18**|Nalchik|URMN|43°30.842`N 043°38.193`E|136.000MHz||**24**|110.50MHz|
|**19**|Beslan|URMO|43°12.342`N 044°36.346`E|141.000MHz||**10**|110.50MHz|
|**20**|Sochi-Adler|URSS|43°26.669`N 039°56.489`E|127.000MHz||**06**|111.10MHz|
|**21**|Mozdok|XRMF|43°47.504`N 044°35.981`E|137.000MHz||||



```
rev 3.6.0 - 03.05.2013 © dp - www.10thGunfighters.de - www.ariescon.com
```

- 05 - 

### AERODROME GROUND CHARTS OVERVIEW GEORGIA 



<!-- Start of picture text -->
KOBULETI (UG5X) GUDAUTA (UG23) TBILISI - SOGANLUG (UG24) VAZIANI (UG27)<br>RWY 07-25 : 2400x60[m] 7870x197[ft] RWY 15-33 : 2500x60[m] 8200x197[ft] RWY 13-31 : 2475x80[m] 8120x262[ft] RWY 13-31 : 2485x62[m] 8150x203[ft]<br>1 2 3 4<br>KUTAISI - KOPITNARI (UGKO) SENAKI - KOLKHI (UGKS) BATUMI (UGSB) SUKHUMI - BABUSHARA (UGSS)<br>RWY 08-26 : 2500x60[m] 8200x197[ft] RWY 09-27 : 2375x50[m] 7790x164[ft] RWY 13-31 : 2455x60[m] 8050x197[ft] RWY 12-30 : 3540x60[m] 11610x197[ft]<br>5 6 7 8<br>TBILISI - LOCHINI (UGTB)<br>RWY 13R-31L : 2920x45[m] 9580x150[ft]<br>9<br><!-- End of picture text -->

```
rev 3.6.0 - 03.05.2013 © dp - www.10thGunfighters.de - www.ariescon.com
```

- 06 - 

### AERODROME GROUND CHARTS OVERVIEW RUSSIA 



<!-- Start of picture text -->
ANAPA - VITYAZEVO (URKA) GELENDZHIK (URKG) MAYKOP - KHANSKAYA (URKH) KRASNODAR - PASHKOVSKY (URKK)<br>RWY 04-22 : 2900x60[m]  9510x197[ft] RWY 04-22 : 1800x60[m] 5905x197[ft] RWY 04-22 : 3200x60[m] 10495x197[ft] RWY 05L-23R : 2265x60[m] 7430x197[ft]<br>RWY 05R-23L : 3100x60[m] 10170x197[ft]<br>10 11 12 13<br>KRASNODAR - CENTER (URKL) NOVOROSSIYSK (URKN) KRYMSK (URKW) MINERALNYE VODY (URMM)<br>RWY 09-27 : 2500x60[m] 8200x197[ft] RWY 04-22 : 1800x60[m] 5905x197[ft] RWY 04-22 : 2600x60[m] 8530x197[ft] RWY 12-30 : 4070x60[m] 13350x197[ft]<br>14 15 16 17<br>NALCHIK (URMN) BESLAN (URMO) SOCHI - ADLER (URSS) MOZDOK (XRMF)<br>RWY 06-24 : 2300x60[m] 7545x197[ft] RWY 10-28 : 3015x50[m] 9890x164[ft] RWY 06-24 : 3100x60[m] 10170x197[ft] RWY 08-26 : 3120x70[m] 10235x230[ft]<br>RWY 02-20 : 2200x60[m] 7220x197[ft]<br>18 19 20 21<br><!-- End of picture text -->

```
rev 3.6.0 - 03.05.2013 © dp - www.10thGunfighters.de - www.ariescon.com
```



<!-- Start of picture text -->
- 07 -<br>GENERAL MAP  1 : 3 000 000<br>A  Z E  R  -<br>B  A  I  J  A N<br> Vaziani04. UG27<br> Beslan19. URMO<br> Tbilisi Lochini09. UGTB -<br> Mozdok21. XRMF<br>A   N  I  A R  M  E<br>S  O U H T<br> O HN R T A L A I A N O  S  S  I A E T<br>O  S  S  I A E T -<br> Nalchik18. URMN<br> Tbilisi Soganlug03. UG24 -<br> OG G  I  A  E   R<br> Mineralnye Vody17. URMM<br>Kutaisi City  Flaming Cliffs Flight Simulator A-10C 3General for DCS Warthog Map &<br>Kutaisi West<br> Kutaisi Kopitnari05. UGKO -<br>A J A A R<br> Kobuleti01. UG5X<br> Batumi07. UGSB<br> U  R  K   YT  E<br>  U  S  S  I  AR<br> Sukhumi Babushara08. UGSS -<br>A K H A I A B Z<br>  Senaki Kolkhi06. UGKS - Kobuleti Muhaestate<br> Gudauta02. UG23<br>N<br> Maykop - Khanskaya12. URKH<br> Sochi Adler20. URSS -<br>  K     S  CB  L  A   A E<br> Pashkovsky Krasnodar13. URKK -<br>[km] [nm]<br>100<br>50<br> Krasnodar Center14. URKL -<br>75<br> Gelendzhik URKG11.<br> Krymsk16. URKW 50<br>25<br>25<br> Novorossiysk15. URKN Legend Military Aerodrome  (Military Joint User)Civil Aerodrome Civil Aerodrome Airfield Airfield closed 0 0<br> - Vityazevo10. URKA Anapa<br>S   A E O  F   O A  V Z<br> www.10thGunfighters.de www.ariescon.comrev 3.6.0 03.05.2013 dp © -<br><!-- End of picture text -->

**GENERAL MAP 1 : 3 000 000** 

- 08 - 

##### TERPS 

##### AERODROME CHART 

##### AERODROME NAME 



<!-- Start of picture text -->
Category A Aircraft - Final Approach Speed -> less than 91 kt (168 km/h)<br>Category B Aircraft - Final Approach Speed -> 91 - 120 kt (168 - 222 km/h)<br>Category C Aircraft - Final Approach Speed -> 121 - 140 kt (224 - 259 km/h)<br>Category D Aircraft - Final Approach Speed -> 141 - 165 kt (261 - 305 km/h)<br>Category E Aircraft - Final Approach Speed -> 166 - 210 kt (307 - 389 km/h)<br>Built-up Area<br>Railway tracks ELEV<br>Power transmission line 112 [ft] 1312x492`CWY<br>34 [m] 400x150m<br>45° 03.00 Fire 45° 03.00<br>Runway Designator EL E V Threshold Station 1<br>(letter "L" for left "C" for center or "R" 112 [ft] Elevation, MSL J<br>for right - are used for parall el Terminal  runway s) 34 [m] Taxiway APRON 1<br>Letters &- or Numbers<br>TWR<br>Tower Fire<br>C N<br>CWY Station 2<br>ARP Fire 1148x492`<br>Aerodrome Station A 350x150m TWR APRON 2 TWY<br>D<br>Reference Point Maintenance N I Taxiway<br>B Area<br>G<br>H<br>A<br>ASR D L ASR<br>Apron & Ramp<br>45° 02.00 W Letters &- or Numbers N ASR 45° 02.00<br>F Aerodrome<br>APRON 3<br>A Runway Surveillance Radar<br>E N<br>Fire Road Fire Runway dimensions<br>Station W PSN THR (RWY) Station 3 in meters and feet.<br>Position Threshold Cargo<br>ELEV Runway Store<br>112 [ft] ELEV Track (TN)<br>Fuel 34 [m] -- Middle Outer Marker Marker TrackRunway (MN) 112 [ft]<br>34 [m]<br>Depot - Inner Marker<br>CWY CWY Geographic Grid<br>RWY Runway 1312x492`400x150m Clearway in degrees and minutes<br>SWY<br>TORA Take Off Run Available<br>TODA 45° 01.00 Take Off Distance Available Stopway 45° 01.00<br>ASDA Accelerate Stop Distance Available<br>LDA Landing Distance Available<br>PSN THR Position Threshold<br>ALS Approach Lighting Systems<br>Magnetic TN<br>CLG Ceiling Variation or<br>MN<br>DA Decision Altitude Water Declination<br>HAT Height above Touchdown Zone Elevation<br>MDA Minimum Descent Altitude TN = True North<br>VIS/RVR Visual Range/Runway Visual Range MN = Magnetic North<br>PAR 05LRWY - 23R A BCAT C D E 312  - 0.8 200 (200-0.8/1.6)MINIMA  GS 3° ARP ELEV Scale 1:33`000<br>45° 02.153`  N 112 [ft] 0 200 400 600 800 1000 [m]<br>SRA 05L - 23R A B C D E 462  - 1.2 350 (350-1.2/1.6)<br>039° 11.481`  E 34 [m] 0 1000 2000 3000 [ft]<br>RWY TORA TODA ASDA LDA PSN THR ALS<br>Precision Approach Radar<br>DA  - VIS HAT (CLG-VIS/ALS VIS) Glide Slope<br>(Precision Approach)<br>Surveillance Radar Approach<br>(Non-Precision Approach)<br>Tower Radar Final - Precision TACAN ILS<br>APRON<br>WEST<br>APRON A<br>X<br>221°<br>221°<br>7430 x 197[ft]<br>3100 x 60[m]<br>041° 10170 x 197[ft]<br>041°<br>227°T<br>227°T<br>2265 x 60[m]<br>047°T<br>047°T<br>05L<br>05R<br>X<br>VAR 6° E(2010)<br>X<br>X<br>039° 11.00 039° 12.00 039° 13.00 039° 14.00<br>039° 11.00 039° 12.00 039° 13.00 039° 14.00<br>23L<br>23R<br>X<br>X<br>X<br><!-- End of picture text -->

**AERODROME CHART** 

**AERODROME CHART LEGEND** 

GND 01 

- 09 - 

##### TERPS 



<!-- Start of picture text -->
AERODROME CHART KOBULETI (UG5X)<br>Coordinates:<br>P1 41°55.717` N 041°51.232` E Holding Position N<br>41° 56.50 P2 41°55.665` N 041°51.249` E Holding Position C 41° 56. 5 0<br>P3 41°55.867` N 041°52.345` E Holding Position B<br>P4 41°56.032` N 041°52.547` E Intersection TWY N / P<br>Cargo<br>Store<br>Additional Combined Frequencies:<br>UHF 344.000 GCA Search<br>Fire Station<br>UHF 385.400 GCA Final<br>VHF 123.300 GCA Maintenance<br>ELEV<br>UHF 257.800 Tower Area<br>59 [ft]<br>VHF 122.100 Tower<br>P 18 [m]<br>N32 N E<br>N34 P4<br>N36<br>41° 56.00 N N38 N31 41° 56.00<br>N33 A<br>N39 N35 A30<br>N37 ASR<br>N41<br>N40 UG5X P3 B A<br>N42 CH67X S<br>TWR<br>S26 A29<br>S S28<br>N<br>ELEV S24 S23 S25<br>59 [ft] S S22<br>18 [m] P1<br>C<br>P2<br>41° 55.50 S S 41° 55.50<br>Fuel Depot<br>TN<br>41° 55.00 MN<br>RWY CAT MINIMA<br>ARP ELEV Scale 1:18`000<br>PAR 07 - 25 A B C D E 259  - 0.8 200 (200-0.8/1.6) GS 3°<br>41° 55.797`  N 59 [ft] 0 200 400 600 [m]<br>SRA 07 - 25 A B C D E 409  - 1.2 350 (350-1.2/1.6)<br>041° 51.809`  E 18 [m] 0 500 1000 1500 2000 [ft]<br>RWY TORA TODA ASDA LDA PSN THR ALS<br>07 7870 [ft] 2400 [m] 7870 [ft] 2400 [m] 7870 [ft] 2400 [m] 7870 [ft] 2400 [m] 41°55.640`N  041°50.975`E<br>25 7870 [ft] 2400 [m] 7870 [ft] 2400 [m] 7870 [ft] 2400 [m] 7870 [ft] 2400 [m] 41°55.952`N   041°52.642`E<br>Tower Radar Final - Precision TACAN ILS RWY 07<br>133.000 MHz 67X "KBL" 111.50 MHz<br>APRON SOUTH<br>244° X<br>250°T<br>2400 x 60[m] / 7870 x 197[ft]<br>064° 1-21<br>070°T<br>S27<br>VAR 6° E<br>X<br>X<br>07<br>(2010)<br>041° 51.00 041° 51.50 041° 52.00 041° 52.50<br> Flaming Cliffs Flight Simulator A-10C 3Ground Chart for Warthog DCS &<br>041° 51.00 041° 51.50 041° 52.00 041° 52.50<br> www.10thGunfighters.de www.ariescon.comrev 3.6.0 03.05.2013 dp © -<br>25<br><!-- End of picture text -->

**KOBULETI (UG5X)** 

**AERODROME CHART** 

GND 02 02 



<!-- Start of picture text -->
- 10 - 10 - -<br><!-- End of picture text -->



<!-- Start of picture text -->
TERPS GND 02 02 - 10 - 10 - -<br>AERODROME CHART GUDAUTA (UG23)<br>Coordinates:<br>P1 43°07.028` N 040°33.843` E Intersection TWY A / X<br>43° 07.50 43° 07.50<br>P2 43°07.181` N 040°34.031` E Holding Position D<br>P3 43°06.250` N 040°34.509` E Holding Position E<br>ELEV A<br>69 [ft]<br>Parking Positions Shelters next TWY X<br>21 [m]<br>11 20 23 26<br>12 21 24 27<br>B 13 22 25<br>28<br>A P2<br>Fire C 16 15 19 18 31 30<br>Station 14 17 29<br>North D<br>Cargo<br>43° 07.00 Store P1 43° 07.00<br>W<br>X<br>ASR<br>A<br>TWR<br>PEM<br>A W<br>Maintenance<br>Area<br>Y<br>43° 06.50 43° 06.50<br>CON<br>ASP<br>A<br>Z ELEV<br>B  L  A  C  K      S  E  A W<br>P3 69 [ft]<br>21 [m]<br>E<br>CWY<br>Additional Combined Frequencies: 1148x492`<br>350x150m<br>UHF 344.000 GCA Search<br>Fire<br>UHF 385.400 GCA Final<br>Station<br>VHF 123.300 GCA South<br>43° 06.00 43° 06.00<br>UHF 257.800 Tower TN<br>VHF 122.100 Tower MN<br>RWY CAT MINIMA<br>ARP ELEV Scale 1:18`000<br>PAR 15 - 33 A B C D E 269  - 0.8 200 (200-0.8/1.6) GS 3°<br>43° 06.856`  N 69 [ft] 0 200 400 600 [m]<br>SRA 15 - 33 A B C D E 419  - 1.2 350 (350-1.2/1.6)<br>040° 34.187`  E 21 [m] 0 500 1000 1500 2000 [ft]<br>RWY TORA TODA ASDA LDA PSN THR ALS<br>15 8200 [ft] 2500 [m] 9350 [ft] 2580 [m] 8200 [ft] 2500 [m] 8200 [ft] 2500 [m] 43°07.468`N  040°33.817`E<br>33 8200 [ft] 2500 [m] 8200 [ft] 2500 [m] 8200 [ft] 2500 [m] 8200 [ft] 2500 [m] 43°06.242`N  040°34.555`E<br>Tower Radar Final - Precision TACAN ILS<br>130.000 MHz<br>X<br>X<br>1-10<br>APRON 1<br>33<br>APRON 2<br>145°<br>325°<br>331°T<br>151°T<br>2500 x 60[m]<br>8200 x 197[ft]<br>VAR 6° E(2010)<br>040° 33.50 040° 34.00 040° 34.50 040° 35.00<br> Flaming Cliffs Flight Simulator A-10C 3Ground Chart for Warthog DCS &<br>040° 33.50 040° 34.00 040° 34.50 040° 35.00<br> www.10thGunfighters.de www.ariescon.comrev 3.6.0 03.05.2013 dp © -<br>15<br>X<br>X<br><!-- End of picture text -->

**GUDAUTA (UG23)** 

**AERODROME CHART** 

GND 03 

- 11 - 

##### TERPS 



<!-- Start of picture text -->
AERODROME CHART TBILISI - SOGANLUG (UG24)<br>Coordinates:<br>P1 41°39.142` N 044°55.983` E Intersection TWY B / E<br>41° 40.00 P2 41°38.819` N 044°56.292` E Intersection TWY D / E 41° 40.00<br>ELEV<br>1504 [ft]<br>459 [m]<br>41° 39.50 41° 39.50<br>A1<br>A2<br>APRON<br>1<br>A E<br>Terminal<br>B P1<br>E<br>41° 39.00 C 41° 39.00<br>APRON<br>2<br>ASR<br>P2 D<br>TWR<br>APRON E<br>3<br>1<br>41° 38.50 41° 38.50<br>E<br>ELEV 820x492CWY `<br>1466 [ft] 250x150m<br>447 [m]<br>TN<br>41° 38.00<br>MN<br>RWY CAT MINIMA<br>ARP ELEV Scale 1:25`000<br>PAR 13 A B C D E 1704  - 0.8 200 (200-0.8/1.6) GS 3°<br>31 A B C D E 1664  - 0.8 200 (200-0.8/1.6) GS 3° 41° 38.970`  N 1473 [ft] 0 200 400 600 800 [m]<br>SRA 13 A B C D E 1854  - 1.2 350 (350-1.2/1.6)<br>31 A B C D E 1814  - 1.2 350 (350-1.2/1.6) 044° 56.304`  E 449 [m] 0 1000 2000 [ft]<br>RWY TORA TODA ASDA LDA PSN THR ALS<br>13 8120 [ft] 2475 [m] 8940 [ft] 2725 [m] 8120 [ft] 2475 [m] 8120 [ft] 2475 [m] 41°39.475`N  044°55.742`E E<br>31 8120 [ft] 2475 [m] 8120 [ft] 2475 [m] 8120 [ft] 2475 [m] 8120 [ft] 2475 [m] 41°38.464`N  044°56.866`E<br>Tower Radar Final - Precision TACAN ILS<br>139.000 MHz<br>5<br>Tbilisi Lochini<br>126°<br>132°T<br>X<br>2475 x 80[m] / 8120 x 262[ft]<br>306°<br>312°T<br>X 2-3-4<br>X<br>31<br>VAR 6° E(2010)<br>044° 55.00 044° 55.50 044° 56.00 044° 56.50 044° 57.00 044° 57.50<br> Flaming Cliffs Flight Simulator A-10C 3Ground Chart for Warthog DCS &<br>044° 55.00 044° 55.50 044° 56.00 044° 56.50 044° 57.00<br> www.10thGunfighters.de www.ariescon.comrev 3.6.0 03.05.2013 dp © -<br>X<br>13<br>X<br>X<br><!-- End of picture text -->

**TBILISI - SOGANLUG (UG24)** 

**AERODROME CHART** 

GND 04 

- 12 - 

TERPS 

AERODROME CHART 



<!-- Start of picture text -->
VAZIANI (UG27)<br><!-- End of picture text -->



<!-- Start of picture text -->
L4<br>41° 38.50 L2 41° 38.50<br>L<br>L<br>N L3<br>RAMP 1<br>L1<br>N<br>A<br>ELEV S P1<br>1509 [ft] N<br>460 [m]<br>B<br>N<br>S<br>41° 38.00 C N 41° 38.00<br>K<br>C P2 J<br>RAMP 4<br>H1 H2<br>UG27 Fire<br>G<br>CH22X Station<br>P4<br>S N<br>G<br>D I<br>D N<br>P3<br>Additional Combined Frequencies:<br>41° 37.50 UHF 344.000 GCA Search RAMP 2 41° 37.50<br>S<br>UHF 385.400 GCA Final<br>Maintenance<br>VHF 123.300 GCA<br>Area<br>UHF 257.800 Tower<br>E<br>VHF 122.100 Tower<br>RAMP 3<br>Coordinates:<br>P1 41°38.269` N 045°01.415` E Intersection TWY B / N<br>ELEV<br>P2 41°37.944` N 045°01.620` E Intersection TWY C / S<br>1478 [ft]<br>P3 41°37.557` N 045°02.002` E Intersection TWY D / S 451 [m]<br>TN<br>P4 41°37.672` N 045°02.289` E Intersection TWY G / H1 SWY<br>115`35m MN<br>41° 37.00<br>RWY CAT MINIMA<br>ARP ELEV Scale 1:18`000<br>PAR 13 A B C D E 1709  - 0.8 200 (200-0.8/1.6) GS 3°<br>31 A B C D E 1678  - 0.8 200 (200-0.8/1.6) GS 3° 41° 37.743`  N 1492 [ft] 0 200 400 600 [m]<br>SRA 13 A B C D E 1859  - 1.2 350 (350-1.2/1.6)<br>31 A B C D E 1828  - 1.2 350 (350-1.2/1.6) 045° 01.632`  E 455 [m] 0 500 1000 1500 2000 [ft]<br>RWY TORA TODA ASDA LDA PSN THR ALS<br>13 8150 [ft] 2485 [m] 8150 [ft] 2485 [m] 8265 [ft] 2520 [m] 8150 [ft] 2485 [m] 41°38.275`N  045°01.108`E<br>31 8150 [ft] 2485 [m] 8150 [ft] 2485 [m] 8150 [ft] 2485 [m] 8150 [ft] 2485 [m] 41°37.215`N  045°02.153`E E<br>Tower Radar Final - Precision TACAN ILS RWY 13 ILS RWY 31<br>140.000 MHz 22X "VAS" 108.75 MHz 108.75 MHz<br>X<br>X<br>X<br>X<br>X<br>X<br>X<br>X<br>2485 x 62[m]<br>31<br>129°<br>135°T<br>309°<br>315°T<br>8150 x 203[ft] X<br>X<br>X<br>X<br>X<br>X<br>VAR 6° E(2010)<br>X<br>X<br>045° 01.00 045° 01.50 045° 02.00 045° 02.50<br> Flaming Cliffs Flight Simulator A-10C 3Ground Chart for Warthog DCS &<br>TWR<br>045° 01.00 045° 01.50 045° 02.00 045° 02.50<br> www.10thGunfighters.de www.ariescon.comrev 3.6.0 03.05.2013 dp © -<br>13<br><!-- End of picture text -->

**VAZIANI (UG27)** 

**AERODROME CHART** 

GND 04 

- 13 - 

AIRCRAFT PARKING POSITIONS 

##### VAZIANI (UG27) 



<!-- Start of picture text -->
25<br>26<br>21<br>24<br>41° 38.50 22 23 41° 38.50<br>20<br>19<br>30 27<br>14 18 29<br>15 PEM<br>RAMP 1 13 17 28<br>12<br>11 16<br>10<br>33<br>CON 31 35<br>37<br>32<br>34 39 41<br>36 42 47 49 50<br>38 51<br>41° 38.00 40 45 41° 38.00<br>52<br>44 46 48 53<br>43 54 56 58<br>60 RAMP 4<br>57 CON<br>55 61<br>91<br>59 62 80<br>65<br>63 90<br>64 87 89<br>67 66 8281 88<br>PEM 68 69 86<br>83<br>92 85<br>70<br>84<br>71<br>CON 72 76<br>73 77 TWR<br>41° 37.50 75 41° 37.50<br>74 RAMP 2<br>CON<br>RAMP 3<br>Legend:<br>- ASP: Asphalt<br>- BIT: Bitumenous Asphalt or Tarmac<br>- BRI: Bricks (no longer in use, covered with Asphalt or Concrete now)<br>- CLA: Clay<br>- COM: Composite<br>- CON: Concrete 41° 37.00<br>- COP: Composite<br>- GRS: Grass or earth not graded or rolled<br>- COR: Coral (Coral reef structures)<br>- GRE: Graded or rolled earth, Grass on graded earth<br>- GVL: Gravel<br>- LAT: Laterite<br>- ICE: Ice<br>- MAC: Macadam<br>- PEM: Partially Concrete, Asphalt or Bitumen-bound Macadam TN<br>- PER: Permanent Surface, Details unknown MN<br>- PSP: Marsden Matting (Derived from Pierced/Perforated Steel Planking)<br>- SAN: Sand<br>- SNO: Snow<br>41° 36.50<br>- U: Unknown Surface<br>Tower Scale 1:18`000 0 200 400 600 [m]<br>140.000 MHz 0 500 1000 1500 2000 [ft]<br>X<br>5-6-7-8-9<br>1 - 2 - 3 - 4<br>31<br>78-79<br>VAR 6° E(2010)<br>045° 01.00 045° 01.50 045° 02.00 045° 02.50<br> Flaming Cliffs Flight Simulator A-10C 3Ground Chart for Warthog DCS &<br> www.10thGunfighters.de www.ariescon.comrev 3.6.0 03.05.2013 dp © -<br>045° 02.00 045° 02.50<br>13<br><!-- End of picture text -->



<!-- Start of picture text -->
AIRCRAFT PARKING POSITIONS<br><!-- End of picture text -->

**VAZIANI (UG27)** 

GND 05 

- 14 - 

TERPS 

##### AERODROME CHART 

##### KUTAISI - KOPITNARI (UGKO) 



<!-- Start of picture text -->
42° 11.50 Coordinates: Additional C o m bined Frequencies: 42° 11.50<br>P1 42°10.747` N 042°29.353` E Holding Position C UHF 344.000 GCA Search<br>P2 42°10.623` N 042°28.381` E Holding Positio n  B UHF 385.400 GCA Final<br>P3 42°10.754` N 042°27.950` E I n tersection TWY A / N VHF 123.300 GCA<br>P4 42°10.339` N 042°28.043` E Intersection TWY S / W UHF 257.800 Tower<br>VHF 122.100 Tower<br>N<br>Maintenance<br>Area N<br>N<br>Fire<br>Station<br>42° 11.00 ELEV 42° 11.00<br>R 148 [ft]<br>D 45 [m]<br>ASR C<br>N N<br>TWR P1<br>UGKO<br>A CH44X E<br>P3<br>B<br>P2 S<br>A<br>42° 10.50 42° 10.50<br>S<br>ELEV W<br>148 [ft]<br>45 [m]<br>P4<br>Cargo Fuel Depot<br>Store<br>W<br>42° 10.00 42° 10.00<br>TN<br>MN<br>RWY CAT MINIMA<br>ARP ELEV Scale 1:18`000<br>PAR 08 - 26 A B C D E 348  - 0.8 200 (200-0.8/1.6) GS 3°<br>42° 10.657`  N 148 [ft] 0 200 400 600 [m]<br>SRA 08 - 26 A B C D E 498  - 1.2 350 (350-1.2/1.6)<br>042° 28.874`  E 45 [m] 0 500 1000 1500 2000 [ft]<br>RWY TORA TODA ASDA LDA PSN THR ALS<br>08 8200 [ft] 2500 [m] 8200 [ft] 2500 [ft] 8200 [ft] 2500 [m] 8200 [ft] 2500 [m] 42°10.544`N  042°27.988`E<br>26 8200 [ft] 2500 [m] 8200 [ft] 2500 [ft] 8200 [ft] 2500 [m] 8200 [ft] 2500 [m] 42°10.768`N   042°29.759`E<br>Tower Radar Final - Precision TACAN ILS RWY 08<br>134.000 MHz 44X "KTS" 109.75 MHz<br>N47<br>N48<br>N43 N45<br>N44 N46<br>RAMP<br>248°<br>RAMP<br>068°<br>RAMP<br>N41 N51<br>N37<br>1-12<br>N42 N52<br>N38<br>N26<br>N24<br>254°T<br>N25 EAST<br>N23<br>2500 x 60[m] / 8200 x 197 [ft]<br>074°T<br>N53<br>N39 N49<br>NORTH<br>N54<br>N40 N50<br>N35<br>N34 N36<br>N22<br>N27<br>SOUTH<br>N32<br>N30<br>N28<br>N33<br>N31<br>N29<br>N 56<br>N 57<br>N 55<br>RAMP<br>W 17<br>WEST<br>13-16<br>N 58<br>W 18<br>W 19<br>VAR 6° E(2010)<br>XX<br>X<br>X<br>08<br>W 21<br>W 20<br>042° 28.00 042° 28.50 042° 29.00 042° 29.50 042° 30.00<br> Flaming Cliffs Flight Simulator A-10C 3Ground Chart for Warthog DCS &<br>042° 28.00 042° 28.50 042° 29.00 042° 29.50<br> www.10thGunfighters.de www.ariescon.comrev 3.6.0 03.05.2013 dp © -<br>26<br>X<br>X<br>X<br>X<br><!-- End of picture text -->

**KUTAISI - KOPITNARI (UGKO)** 

**AERODROME CHART** 

GND 06 

- 15 - 

TERPS 

##### AERODROME CHART 

##### SENAKI - KOLKHI (UGKS) 



<!-- Start of picture text -->
42° 15.50 42° 15.50<br>Additional Combined Frequencies:<br>UHF 344.000 GCA Search<br>Fuel Depot UHF 385.400 GCA Final<br>VHF 123.300 GCA<br>UHF 257.800 Tower<br>VHF 122.100 Tower<br>C<br>42° 15.00 42° 15.00<br>TWR<br>C Fire<br>BIT Station 2<br>B<br>G<br>C<br>F A<br>N<br>N N D<br>Fire F1 P3<br>Station 1 F<br>A B CON UGKS<br>42° 14.50 CH31X C D 42° 14.50<br>P1<br>P2 N<br>ELEV<br>BIT<br>36 [ft]<br>ASR<br>11 [m]<br>ELEV<br>39 [ft]<br>12 [m]<br>Coordinates:<br>P1 42°14.453` N 042°03.088` E Holding Position C<br>P2 42°14.404` N 042°03.419` E Holding Position D<br>42° 14.00 P3 42°14.674` N 042°02.464` E Intersection TWY B / N 42° 14.00<br>TN<br>MN<br>Cargo<br>Store<br>RWY CAT MINIMA<br>ARP ELEV Scale 1:18`000<br>PAR 09 A B C D E 236  - 0.8 200 (200-0.8/1.6) GS 3°<br>27 A B C D E 239  - 0.8 200 (200-0.8/1.6) GS 3° 42° 14.454`  N 43 [ft] 0 200 400 600 [m]<br>SRA 09 A B C D E 386  - 1.2 350 (350-1.2/1.6)<br>27 A B C D E 389  - 1.2 350 (350-1.2/1.6) 042° 02.861`  E 13 [m] 0 500 1000 1500 2000 [ft]<br>RWY TORA TODA ASDA LDA PSN THR ALS<br>09 7790 [ft] 2375 [m] 7790 [ft] 2375 [m] 7790 [ft] 2375 [m] 7790 [ft] 2375 [m] 42°14.573`N   042°02.024`E E<br>27 7790 [ft] 2375 [m] 7790 [ft] 2375 [m] 7790 [ft] 2375 [m] 7790 [ft] 2375 [m] 42°14.336`N   042°03.695`E<br>Tower Radar Final - Precision TACAN ILS RWY 09<br>132.000 MHz 31X "TSK" 108.90 MHz<br>7790 x 164 [ft]<br>2<br>088°<br>2375 x 50 [m]<br>094°T<br>268°<br>274°T<br>RAMP<br>RAMP 1<br>X<br>X<br>X X<br>VAR 6° E(2010)<br>27<br>042° 02.00 042° 02.50 042° 03.00 042° 03.50<br> Flaming Cliffs Flight Simulator A-10C 3Ground Chart for Warthog DCS &<br>042° 02.00 042° 02.50 042° 03.00 042° 03.50<br> www.10thGunfighters.de www.ariescon.comrev 3.6.0 03.05.2013 dp © -<br>09<br>X<br><!-- End of picture text -->

**SENAKI - KOLKHI (UGKS)** 

**AERODROME CHART** 

GND 06 

- 16 - 

##### AIRCRAFT PARKING POSITIONS 

##### SENAKI - KOLKHI (UGKS) 



<!-- Start of picture text -->
42° 15.50 42° 15.50<br>42° 15.00 42° 15.00<br>TWR<br>21<br>20 42<br>43<br>44<br>11 12 18 40<br>10 41 39<br>9 13 14 25 26 4546 47 34<br>8 7 30 27 3821 33 48 50 52 55 57 60<br>31<br>6<br>BIT 29 61<br>49 53 59<br>42° 14.50 51 54 56 58 42° 14.50<br>Legend:<br>- ASP: Asphalt<br>- BIT: Bitumenous Asphalt or Tarmac<br>- BRI: Bricks (no longer in use, covered with Asphalt or Concrete now) 42° 14.00<br>- CLA: Clay<br>- COM: Composite<br>- CON: Concrete<br>- COP: Composite<br>- GRS: Grass or earth not graded or rolled<br>- COR: Coral (Coral reef structures)<br>- GRE: Graded or rolled earth, Grass on graded earth<br>- GVL: Gravel<br>- LAT: Laterite<br>- ICE: Ice<br>- MAC: Macadam<br>- PEM: Partially Concrete, Asphalt or Bitumen-bound Macadam TN<br>- PER: Permanent Surface, Details unknown MN 42° 13.50<br>- PSP: Marsden Matting (Derived from Pierced/Perforated Steel Planking)<br>- SAN: Sand<br>- SNO: Snow<br>- U: Unknown Surface<br>Tower Scale 1:18`000 0 200 400 600 [m]<br>132.000 MHz 0 500 1000 1500 2000 [ft]<br>28<br>BIT<br>BIT<br>CON<br>CON<br>CON<br>UGKS<br>CH31X<br>RAMP 2<br>1 - 2 - 3 - 4 - 5<br>23<br>19<br>17<br>15 16 32<br>RAMP 1<br>22<br>24<br>X<br>35<br>36<br>VAR 6° E(2010)<br>27<br>042° 02.00 042° 02.50 042° 03.00 042° 03.50<br> Flaming Cliffs Flight Simulator A-10C 3Ground Chart for Warthog DCS &<br> www.10thGunfighters.de www.ariescon.comrev 3.6.0 03.05.2013 dp © -<br>042° 03.00 042° 03.50<br>09<br>X<br>X<br>X<br><!-- End of picture text -->

**SENAKI - KOLKHI (UGKS)** 

**AIRCRAFT PARKING POSITIONS** 

GND 07 

- 17 - 

##### TERPS 

##### AERODROME CHART 

##### BATUMI (UGSB) 



<!-- Start of picture text -->
41° 37.50 41° 37.50<br>B  L  A  C  K<br>S  E  A<br>ELEV<br>W 33 [ft]<br>Stop Bar 10 [m]<br>W1<br>41° 37.00 P 41° 37.00<br>Fire<br>3.0°<br>Station 1<br>Hangar 1<br>W O Maintenance<br>Stop Bar Area<br>W2 P<br>N1<br>N2<br>W A<br>TWR Fire<br>UGSB<br>APRON 2 Station 2<br>CH16X P3<br>B W ASP<br>Terminal<br>41° 36.50 41° 36.50<br>PEM CON<br>Attention: W C Fire<br>During active ATC a special clearance<br>is required to cross Stop Bar. P2 Station 3<br>P1<br>D<br>Coordinates:<br>P1 41°36.226` N 041°36.613` E Holding Position D<br>W E ELEV<br>P2 41°36.307` N 041°36.488` E Holding Position C<br>33 [ft]<br>P3 41°36.640` N 041°36.132` E Intersection TWY B / W S2 S1 10 [m]<br>Hangar 2<br>Hangar 3<br>41° 36.00 41° 36.00<br>TN<br>MN<br>RWY CAT MINIMA<br>ARP ELEV Scale 1:18`000<br>PAR 13 A B C D E 233  - 0.8 200 (200-0.8/1.6) GS 3°<br>41° 36.562`  N 33 [ft] 0 200 400 600 [m]<br>SRA 13 - 31 A B C D E 383  - 1.2 350 (350-1.2/1.6)<br>041° 36.034`  E 10 [m] 0 500 1000 1500 2000 [ft]<br>RWY TORA TODA ASDA LDA PSN THR ALS<br>13 8050 [ft] 2455 [m] 8050 [ft] 2455 [m] 8050 [ft] 2455 [m] 8050 [ft] 2455 [m] 41°36.995`N  041°35.378`E X<br>31 8050 [ft] 2455 [m] 8050 [ft] 2455 [m] 8050 [ft] 2455 [m] 8050 [ft] 2455 [m] 41°36.127`N  041°36.694`E<br>Tower Radar Final - Precision TACAN ILS RWY 13<br>131.000 MHz 16X "BTM" 110.30 MHz<br>126°T X<br>2455 x 60[m] / 8050 x 197[ft]<br>306°T<br>120°<br>PAPRON 1-10  1<br>300°<br>31<br>X<br>X<br>VAR 6° E(2010)<br>041° 35.00 041° 35.50 041° 36.00 041° 36.50 041° 37.00<br> Flaming Cliffs Flight Simulator A-10C 3Ground Chart for Warthog DCS &<br>041° 35.00 041° 35.50 041° 36.00 041° 36.50 041° 37.00<br> www.10thGunfighters.de www.ariescon.comrev 3.6.0 03.05.2013 dp © -<br>13<br>X<br><!-- End of picture text -->

**BATUMI (UGSB)** 

**AERODROME CHART** 

GND 08 

- 18 - 

TERPS 

##### AERODROME CHART 



<!-- Start of picture text -->
SUKHUMI - BABUSHARA (UGSS)<br><!-- End of picture text -->



<!-- Start of picture text -->
42° 52.50 42° 52.50<br>Non - Standard<br>APP Lights<br>ASP<br>Terminal APRON 1<br>P1 N APRON 2<br>A<br>P2<br>P B<br>3.0°<br>42° 52.00 Y N 42° 52.00<br>SWY<br>230`70m ELEV PEM<br>CWY 20 [ft]<br>1312x492` GRE<br>400x150m 6 [m]<br>N<br>P3 C<br>CON<br>ASR D SWY<br>P4 279`85m<br>42° 51.50 N CWY 42° 51.50<br>656x492`<br>200x150m<br>Additional Combined Frequencies:<br>UHF 344.000 GCA Search<br>ELEV<br>UHF 385.400 GCA Final<br>40 [ft]<br>42° 51.00 VHF 123.300 GCA 12 [m] 42° 51.00<br>UHF 257.800 Tower<br>VHF 122.100 Tower<br>B  L  A  C  K<br>Coordinates:<br>S  E  A P1 42°52.230` N 041°06.358` E Holding Position A<br>P2 42°52.203` N 041°06.697` E Intersection TWY N / B<br>P3 42°51.655` N 041°07.600` E Holding Position C TN<br>P4 42°51.494` N 041°07.957` E Holding Position D MN<br>42° 50.50<br>RWY CAT MINIMA<br>PAR 12 A B C D E 220  - 0.8 200 (200-0.8/1.6) GS 3° ARP ELEV Scale 1:25`000<br>30 A B C D E 240  - 0.8 200 (200-0.8/1.6) GS 3° 42° 51.677`  N 30 [ft] 0 200 400 600 800 [m]<br>SRA 12 A B C D E 370  - 1.2 350 (350-1.2/1.6)<br>30 A B C D E 390  - 1.2 350 (350-1.2/1.6) 041° 07.474`  E 9 [m] 0 1000 2000 [ft]<br>RWY TORA TODA ASDA LDA PSN THR ALS<br>12 11610 [ft] 3540 [m] 12270 [ft] 3740 [m] 11890 [ft] 3625 [m] 11610 [ft] 3540 [m] 42°52.179`N  041°06.383`E<br>30 11610 [ft] 3540 [m] 12920 [ft] 3940 [m] 11840 [ft] 3610 [m] 11610 [ft] 3540 [m] 42°51.172`N  041°08.570`E X<br>Tower Radar Final - Precision TACAN ILS<br>129.000 MHz<br>RAMP 1<br>APRON 3<br>116°T<br>3540 x 60[m] / 11610 x 197[ft]<br>296°T<br>110°<br>290°<br>X<br>30<br>VAR 6° E(2010)<br>X<br>041° 06.00 041° 06.50 041° 07.00 041° 07.50 041° 08.00 041° 08.50 041° 09.00<br>TWR<br> Flaming Cliffs Flight Simulator A-10C 3Ground Chart for Warthog DCS &<br>041° 06.00 041° 06.50 041° 07.00 041° 07.50 041° 08.00 041° 08.50<br> www.10thGunfighters.de www.ariescon.comrev 3.6.0 03.05.2013 dp © -<br>12<br><!-- End of picture text -->

**SUKHUMI - BABUSHARA (UGSS)** 

**AERODROME CHART** 

GND 09 

##### TERPS 

##### AERODROME CHART 



<!-- Start of picture text -->
- 19 -<br><!-- End of picture text -->

##### TBILISI - LOCHINI (UGTB) 



<!-- Start of picture text -->
41° 41.50 41° 41.50<br>41° 41.00 41° 41.00<br>Maintenance<br>Area X1 Helipad<br>APRON 5 D North<br>X2 APRON 2<br>656x492CWY ` H X3 TWR<br>200x150m H<br>H H D C Termi nal<br>SWY B 1 Ter minal<br>197`60m<br>41° 40.50 N H 2 41° 40.50<br>Fire<br>ELEV<br>Station<br>1565 [ft] Terminal<br>477 [m] P B F 3<br>3.0° A<br>Fuel C<br>ASR Station<br>A<br>N APRON 4<br>E<br>41° 40.00 41° 40.00<br>SR<br>N Isolated aircraft stand,<br>washing and engine<br>For turns on RWY 13R/31L acft with a nosewheel turning run-up area<br>radius in excess of 49`/15m are restricted to turn on<br>threshold only.<br>E<br>During winter conditions Follow-me assistance mandatory. P<br>3.0° SWY<br>Since the width of TWY C is not enough and TWY shoulders 197`60m<br>are not paved, large aircraft with wingspan up to<br>41° 39.50 167`/51m shall taxi using inboard engines. Large aircraft 41° 39.50<br>with  w ing span exceeding 167`/51m shall perform taxiing ELEV<br>on RWY 31R/L, Follow-me mandatory. 1526 [ft]<br>465 [m]<br>TN<br>MN<br>41° 39.00<br>RWY CAT MINIMA<br>ARP ELEV Scale 1:25`000<br>PAR 13R A B C D E 1765  - 0.8 200 (200-0.8/1.6) GS 3°<br>31L A B C D E 1725  - 0.8 200 (200-0.8/1.6) GS 3° 41° 40.095`  N 1539 [ft] 0 200 400 600 800 [m]<br>SRA 13R A B C D E 1915  - 1.2 350 (350-1.2/1.6)<br>31L A B C D E 1875  - 1.2 350 (350-1.2/1.6) 044° 57.283`  E 469 [m] 0 1000 2000 [ft]<br>RWY TORA TODA ASDA LDA PSN THR ALS<br>13R 9580 [ft] 2920 [m] 9580 [ft] 2920 [m] 9775 [ft] 2980 [m] 9580 [ft] 2920 [m] 41°40.654`N  044°56.565`E<br>31L 9580 [ft] 2920 [m] 10230 [ft] 3120 [m] 9775 [ft] 2980 [m] 9580 [ft] 2920 [m] 41°39.537`N  044°58.003`E X<br>Tower Radar Final - Precision TACAN ILS RWY 13R ILS RWY 31L<br>138.000 MHz 110.30 MHz 108.90 MHz<br>APRON 1<br>APRON 3<br>308°T<br>122°<br>128°T<br>2920 x 45[m]/ 9580 x 150[ft]<br>302°<br>Tbilisi Soganlug<br>31L<br>X<br>X<br>VAR 6° E(2010)<br>044° 56.00 044° 56.50 044° 57.00 044° 57.50 044° 58.00 044° 58.50<br> Flaming Cliffs Flight Simulator A-10C 3Ground Chart for Warthog DCS &<br>044° 56.00 044° 56.50 044° 57.00 044° 57.50 044° 58.00 044° 58.50<br> www.10thGunfighters.de www.ariescon.comrev 3.6.0 03.05.2013 dp © -<br>13R<br><!-- End of picture text -->

**TBILISI - LOCHINI (UGTB)** 

**AERODROME CHART** 



<!-- Start of picture text -->
GND 09 - 20 -<br>AIRCRAFT PARKING POSITIONS  -  Part 1/2 TBILISI - LOCHINI (UGTB)<br>APRON  1<br>C<br>F<br>F1<br>F<br>馬<br>C<br>A<br>C<br>A<br>N<br>TN<br>MN<br>Tower Scale 1:5`000 0 50 100 150 [m]<br>138.000 MHz 0 250 500 [ft]<br>51<br>50<br>49 05<br>04 Terminal 1<br>03 06<br>02<br>01 09 11<br>08 12<br>Terminal 2<br>46 10 14 16<br>45<br>13<br>44 42 15 19 21<br>43<br>18 22<br>48<br>20 24 26<br>23<br>25 29 31<br>28 32<br>30 34 36<br>37<br>35 39<br>38<br>07<br>47<br>17<br>27<br>33<br>APRON  2<br>APRON  3<br>VAR 6° E(2010)<br> Flaming Cliffs Flight Simulator A-10C 3Ground Chart for Warthog DCS &<br> www.10thGunfighters.de www.ariescon.comrev 3.6.0 03.05.2013 dp © -<br><!-- End of picture text -->



<!-- Start of picture text -->
AIRCRAFT PARKING POSITIONS  -  Part 1/2<br><!-- End of picture text -->



<!-- Start of picture text -->
TBILISI - LOCHINI (UGTB)<br><!-- End of picture text -->

GND 09 

- 21 - 

AIRCRAFT PARKING POSITIONS  -  Part 2/2 

TBILISI - LOCHINI (UGTB) 

H 



<!-- Start of picture text -->
Maintenance<br>Helipad<br>Area<br>North<br>X1<br>APRON  5<br>D<br>X2<br>X3<br>H<br>H<br>H<br>H<br>D<br>C<br>B<br>B<br>N<br>TN<br>MN<br>Tower Scale 1:5`000 0 50 100 150 [m]<br>138.000 MHz 0 250 500 [ft]<br>63<br>67<br>69<br>68<br>64<br>65<br>66<br>73<br>52<br>72<br>53<br>71<br>54<br>70<br>74<br>55<br>78<br>56<br>77<br>57<br>58<br>X<br>VAR 6° E(2010)<br> Flaming Cliffs Flight Simulator A-10C 3Ground Chart for Warthog DCS &<br> www.10thGunfighters.de www.ariescon.comrev 3.6.0 03.05.2013 dp © -<br><!-- End of picture text -->



<!-- Start of picture text -->
AIRCRAFT PARKING POSITIONS  -  Part 2/2<br><!-- End of picture text -->

**TBILISI - LOCHINI (UGTB)** 

GND 10 

- 22 - 

TERPS 

##### AERODROME CHART 

##### ANAPA - VITYAZEVO (URKA) 



<!-- Start of picture text -->
Parking Positions Shelters next Parking Positions Shelters next<br>45° 01.50 TWY W1 - W3 TWY E, E1, E2 45° 01.50<br>77<br>75<br>76<br>78<br>74<br>80<br>73<br>69<br>71<br>72<br>65 67 68 ELEV<br>70<br>66 148 [ft]<br>45 [m]<br>45° 01.00 45° 01.00<br>Fuel Depot<br>D<br>Fire<br>Station 1 E E2<br>N<br>M P3<br>45° 00.50 MaintenanceArea N StationFire  2 E1 E 45° 00.50<br>P2 Fire<br>Fire Station E<br>W3 Station W East<br>C ASR Cargo<br>N<br>W Store<br>M<br>W<br>P1<br>W1<br>W<br>B<br>45° 00.00 W2 45° 00.00<br>M<br>Additional Combined Frequencies:<br>A UHF 344.000 GCA Search<br>ELEV UHF 385.400 GCA Final<br>148 [ft] VHF 123.300 GCA<br>45 [m] UHF 257.800 Tower<br>VHF 122.100 Tower<br>44° 59.50 Coordinates: 44° 59.50<br>P1 45°00.181` N 037°20.388` E Intersection TWY B / M<br>P2 45°00.477` N 037°20.800` E Intersection TWY M / N TN<br>P3 45°00.615` N 037°21.887` E Intersection TWY E / E1 MN<br>RWY CAT MINIMA<br>ARP ELEV Scale 1:25`000<br>PAR 04 - 22 A B C D E 348  - 0.8 200 (200-0.8/1.6) GS 3°<br>45° 00.298`  N 148 [ft] 0 200 400 600 800 [m]<br>SRA 04 - 22 A B C D E 498  - 1.2 350 (350-1.2/1.6)<br>037° 20.870`  E 45 [m] 0 1000 2000 [ft]<br>RWY TORA TODA ASDA LDA PSN THR ALS<br>04 9510 [ft] 2900 [m] 9510 [ft] 2900 [m] 9510 [ft] 2900 [m] 9510 [ft] 2900 [m] 44°59.741`N  037°20.099`E<br>22 9510 [ft] 2900 [m] 9510 [ft] 2900 [m] 9510 [ft] 2900 [m] 9510 [ft] 2900 [m] 45°00.853`N  037°21.642`E<br>Tower Radar Final - Precision TACAN ILS<br>121.000 MHz<br>42<br>46 41<br>44 4348<br>47<br>45<br>49<br>52<br>50 51 5553<br>58<br>56<br>54<br>57<br>61<br>59 60<br>62 63<br>64<br>83<br>91<br>81<br>82<br>92<br>90.<br>APRON<br>79<br>EAST<br>33-40<br>04<br>84<br>85<br>86<br>89<br>87 88<br>APRON 1<br>222°T<br>25-32<br>APRON 2<br>2900 x 60[m]<br>9510 x 197[ft]<br>042°T<br>216°<br>1-24<br>036°<br>VAR 6° E(2010)<br>XX<br>037° 19.50 037° 20.00 037° 20.50 037° 21.00 037° 21.50 037° 22.00 037° 22.50<br>TWR<br> Flaming Cliffs Flight Simulator A-10C 3Ground Chart for Warthog DCS &<br>037° 19.50 037° 20.00 037° 20.50 037° 21.00 037° 21.50 037° 22.00<br> www.10thGunfighters.de www.ariescon.comrev 3.6.0 03.05.2013 dp © -<br>X<br>X<br>22<br><!-- End of picture text -->

**ANAPA - VITYAZEVO (URKA)** 

**AERODROME CHART** 

- 23 - 

GND 11 

##### TERPS 



<!-- Start of picture text -->
AERODROME CHART GELENDZHIK (URKG)<br>Coordinates:<br>P1 44°34.558` N 038°00.827` E Apron North, TWY M/N<br>P2 44°34.242` N 038°00.407` E Apron South, TWY M/S<br>44° 35.00 44° 35.00<br>ELEV<br>82 [ft]<br>Non - Standard<br>25 [m]<br>APP Lights<br>Fire Station<br>North<br>M<br>Maintenance APRON<br>Area NORTH P1<br>44° 34.50 44° 34.50<br>W<br>M<br>TWR<br>APRON M<br>ASR<br>SOUTH<br>Fire Station<br>South<br>P2 Fuel Depot<br>ELEV M<br>Cargo<br>82 [ft]<br>Store<br>25 [m]<br>44° 34.00 44° 34.00<br>B  L  A  C  K      S  E  A TN<br>MN<br>RWY CAT MINIMA<br>ARP ELEV Scale 1:18`000<br>PAR 04 A B C D E 282  - 0.8 200 (200-0.8/1.6) GS 3°<br>44° 34.364`  N 82 [ft] 0 200 400 600 [m]<br>SRA 04 - 22 A B C D E 432  - 1.2 350 (350-1.2/1.6)<br>038° 00.684`  E 25 [m] 0 500 1000 1500 2000 [ft]<br>RWY TORA TODA ASDA LDA PSN THR ALS<br>04 5905 [ft] 1800 [m] 5905 [ft] 1800 [m] 5905 [ft] 1800 [m] 5905 [ft] 1800 [m] 44°34.014`N  038°00.219`E<br>22 5905 [ft] 1800 [m] 5905 [ft] 1800 [m] 5905 [ft] 1800 [m] 5905 [ft] 1800 [m] 44°34.715`N  038°01.149`E<br>Tower Radar Final - Precision TACAN ILS<br>126.000 MHz<br>04<br>X<br>214°<br>11-13 220°T<br>X<br>1-10<br>5905 x 197[ft]<br>034°<br>040°T<br>1800 x 60[m]<br>VAR 6° E(2010)<br>038° 00.00 038° 00.50 038° 01.00 038° 01.50<br> Flaming Cliffs Flight Simulator A-10C 3Ground Chart for Warthog DCS &<br>038° 00.00 038° 00.50 038° 01.00 038° 01.50<br> www.10thGunfighters.de www.ariescon.comrev 3.6.0 03.05.2013 dp © -<br>22<br><!-- End of picture text -->

#### **GELENDZHIK (URKG)** 

**AERODROME CHART** 

GND 12 

- 24 - 

TERPS 

AERODROME CHART 

##### MAYKOP - KHANSKAYA (URKH) 



<!-- Start of picture text -->
ELEV<br>591 [ft]<br>Coordinates:<br>180 [m]<br>P1 44°40.493` N 040°01.646` E Holding Position B<br>P2 44°41.012` N 040°02.350` E Holding Position C<br>44° 41.50 P3 44°41.265` N 040°02.694` E Holding Position D 44° 41.50<br>E<br>Additional Combined Frequencies: Fuel Depot<br>UHF 344.000 GCA Search<br>UHF 385.400 GCA Final E<br>P3<br>VHF 123.300 GCA<br>UHF 257.800 Tower<br>D<br>VHF 122.100 Tower<br>V56<br>V57<br>URKH<br>no freq. V V55<br>P2 V54 Fire<br>44° 41.00 44° 41.00<br>Station<br>ASR C V North<br>V53<br>X<br>V<br>V25<br>V24<br>TWR<br>V22 M<br>Cargo<br>Store<br>V20 V V23<br>44° 40.50 V18 44° 40.50<br>P1<br>B V21 Maintenance<br>V Area<br>ELEV V19<br>591 [ft] V17<br>V<br>180 [m] V6 APRON 2<br>Fire<br>A Station<br>South<br>V<br>TN<br>MN<br>44° 40.00 Terminal<br>RWY CAT MINIMA<br>ARP ELEV Scale 1:18`000<br>PAR 04 - 22 A B C D E 791  - 0.8 200 (200-0.8/1.6) GS 3°<br>44° 40.874`  N 591 [ft] 0 200 400 600 [m]<br>SRA 04 - 22 A B C D E 941  - 1.2 350 (350-1.2/1.6)<br>040° 02.112`  E 180 [m] 0 500 1000 1500 2000 [ft]<br>RWY TORA TODA ASDA LDA PSN THR ALS<br>04 10495 [ft] 3200 [m] 10495 [ft] 3200 [m] 10495 [ft] 3200 [m] 10495 [ft] 3200 [m] 44°40.257`N  040°01.276`E<br>22 10495 [ft] 3200 [m] 10495 [ft] 3200 [m] 10495 [ft] 3200 [m] 10495 [ft] 3200 [m] 44°41.494`N   040°02.946`E<br>Tower Radar Final - Precision TACAN ILS<br>125.000 MHz<br>41-52<br>APRON 4<br>1-5<br>APRON 1<br>X<br>X<br>04<br>212°<br>218°T<br>3200 x 60[m] / 10495 x 197[ft]<br>038°T<br>032°<br>26-40<br>APRON 3<br>VAR 6° E(2010)<br>7-16<br>040° 03.50 040° 02.00 040° 02.50 040° 03.00<br> Flaming Cliffs Flight Simulator A-10C 3Ground Chart for Warthog DCS &<br>040° 03.50 040° 02.00 040° 02.50 040° 03.00<br> www.10thGunfighters.de www.ariescon.comrev 3.6.0 03.05.2013 dp © -<br>22<br><!-- End of picture text -->

**MAYKOP - KHANSKAYA (URKH)** 

**AERODROME CHART** 

GND 13 

- 25 - 

TERPS 

AERODROME CHART 

##### KRASNODAR - PASHKOVSKY (URKK) 



<!-- Start of picture text -->
Coordinates:<br>P1 45°02.579` N 039°09.212` E Intersection TWY A / B<br>P2 45°02.180` N 039°08.387` E Intersection TWY A / W<br>P3 45°02.027` N 039°10.663` E Intersection TWY F / N<br>P4 45°02.352` N 039°11.238` E Intersection TWY H / N ELEV<br>112 [ft] 1312x492`CWY<br>34 [m] 400x150m<br>Fire<br>EL E V Station 1<br>45° 03.00 J 45° 03.00<br>112 [ft]<br>Terminal 34 [m] APRON 1<br>CWY<br>1148x492` Fire<br>C 350x150m N<br>Station 2<br>Fire<br>Station A<br>TWR APRON 2<br>D<br>P1 Maintenance N I<br>B Area<br>G<br>P4 H<br>A<br>ASR D L ASR<br>W N<br>P3<br>45° 02.00 P2 F 45° 02.00<br>APRON 3<br>A<br>E N<br>Fire Fire<br>Station W Station 3<br>Cargo<br>ELEV Store<br>112 [ft]<br>ELEV<br>34 [m]<br>Fuel 112 [ft]<br>Depot 34 [m]<br>CWY<br>1312x492`<br>400x150m<br>45° 01.00 45° 01.00<br>TN<br>MN<br>RWY CAT MINIMA<br>ARP ELEV Scale 1:33`000<br>PAR 05L - 23R A B C D E 312  - 0.8 200 (200-0.8/1.6) GS 3°<br>05R - 23L A B C D E 312  - 0.8 200 (200-0.8/1.6) GS 3° 45° 02.276`  N 112 [ft] 0 200 400 600 800 1000 [m]<br>SRA 05L - 23R A B C D E 462  - 1.2 350 (350-1.2/1.6)<br>05R - 23L A B C D E 462  - 1.2 350 (350-1.2/1.6) 039° 11.282`  E 34 [m] 0 1000 2000 3000 [ft]<br>RWY TORA TODA ASDA LDA PSN THR ALS<br>05L 7430 [ft] 2265 [m] 8580 [ft] 2615 [m] 7430 [ft] 2265 [m] 7430 [ft] 2265 [m] 45°01.991`N  039°08.464`E<br>23R 7430 [ft] 2265 [m] 7430 [ft] 2265 [m] 7430 [ft] 2265 [m] 7430 [ft] 2265 [m] 45°02.749`N  039°09.800`E<br>05R 10170 [ft] 3100 [m] 11480 [ft] 3500 [m] 10170 [ft] 3100 [m] 10170 [ft] 3100 [m] 45°01.757`N  039°10.367`E<br>23L 10170 [ft] 3100 [m] 11480 [ft] 3500 [m] 10170 [ft] 3100 [m] 10170 [ft] 3100 [m] 45°02.794`N  039°12.198`E<br>Tower Radar Final - Precision TACAN ILS<br>128.000 MHz<br>APRON<br>WEST<br>APRON A<br>X<br>14-19<br>221°<br>221° 7-13<br>7430 x 197[ft]<br>3100 x 60[m]<br>041° 1-6 10170 x 197[ft]<br>041°<br>227°T<br>227°T<br>2265 x 60[m]<br>047°T<br>047°T<br>05L<br>05R<br>X<br>VAR 6° E(2010)<br>X<br>X<br>039° 09.00 039° 10.00 039° 11.00 039° 12.00<br> Flaming Cliffs Flight Simulator A-10C 3Ground Chart for Warthog DCS &<br>039° 09.00 039° 10.00 039° 11.00 039° 12.00<br> www.10thGunfighters.de www.ariescon.comrev 3.6.0 03.05.2013 dp © -<br>23L<br>23R<br>X<br>X<br>X<br><!-- End of picture text -->

**KRASNODAR - PASHKOVSKY (URKK)** 

**AERODROME CHART** 

- 26 - 

GND 14 

##### TERPS 



<!-- Start of picture text -->
AERODROME CHART KRASNODAR - CENTER (URKL)<br>Coordinates:<br>P1 45°05.201` N 038°55.753` E Holding Position B<br>P2 45°05.024` N 038°56.233` E Intersection TWY A / F<br>P3 45°05.011` N 038°57.069` E Intersection TWY A / D<br>45° 06.00 P4 45°05.180` N 038°57.059` E Holding Position C 45° 06.00<br>P5 45°05.172` N 038°57.715` E Holding Position F<br>Attention:<br>Non - Standard Approach Lights RWY 27.<br>Lights end 3300 ft East of Touchdown Zone!<br>Fuel Depot<br>Cargo SWY = TWY F<br>Store CWY 1377` 420m<br>45° 05.50 820x492` 45° 05.50<br>250x150m ELEV<br>Non - Standard<br>98 [ft]<br>ELEV ASR 30 [m] Approach Lights<br>98 [ft]<br>30 [m]<br>P4 P5<br>P1 C D E F<br>A B A<br>A P2 A P3<br>45° 05.00 Fire Fire 45° 05.00<br>A F RAMP 2 D Station 2 F Station F<br>Fire RAMP 3 E<br>Station 1 TWR<br>F<br>F D<br>Parking Positions Shelters next TWY E & F<br>F<br>36<br>26 37<br>24<br>38<br>45° 04.50 2925 27 3 9 40 45° 04.50<br>28<br>35 41<br>42 33 32 30 Additional Combined Frequencies:<br>45 34 31 UHF 344.000 GCA Search<br>48<br>51 UHF 385.400 GCA Final<br>54<br>43 44 VHF 123.300 GCA<br>46 47<br>49 50 UHF 257.800 Tower<br>55 5652 53 VHF 122.100 Tower TN MN<br>45° 04.00<br>RWY CAT MINIMA<br>ARP ELEV Scale 1:25`000<br>PAR 09 - 27 A B C D E 298  - 0.8 200 (200-0.8/1.6) GS 3°<br>45° 05.216`  N 98 [ft] 0 200 400 600 800 [m]<br>SRA 09 - 27 A B C D E 448  - 1.2 350 (350-1.2/1.6)<br>038° 56.415`  E 30 [m] 0 1000 2000 [ft]<br>RWY TORA TODA ASDA LDA PSN THR ALS<br>09 8200 [ft] 2500 [m] 8200 [ft] 2500 [m] 9580 [ft] 2920 [m] 8200 [ft] 2500 [m] 45°05.231`N  038°55.467`E<br>27 8200 [ft] 2500 [m] 9020 [ft] 2750 [m] 8200 [ft] 2500 [m] 8200 [ft] 2500 [m] 45°05.202`N  038°57.362`E<br>27 (via TWY F) 9580 [ft] 2920 [m] 10400 [ft] 3170 [m] 9580 [ft] 2920 [m] 8200 [ft] 2500 [m]<br>Tower Radar Final - Precision TACAN ILS<br>122.000 MHz<br>267°T<br>2500 x 60 [m] / 8200 x 197 [ft]<br>087°T<br>1-17<br>RAMP 1<br>261°<br>081°<br>18-23<br>X<br>VAR 6° E(2010)<br>09<br>038° 55.00 038° 55.50 038° 56.00 038° 56.50 038° 57.00 038° 57.50 038° 58.00<br> Flaming Cliffs Flight Simulator A-10C 3Ground Chart for Warthog DCS &<br>038° 55.00 038° 55.50 038° 56.00 038° 56.50 038° 57.00 038° 57.50<br> www.10thGunfighters.de www.ariescon.comrev 3.6.0 03.05.2013 dp © -<br>27<br>X<br><!-- End of picture text -->

**KRASNODAR - CENTER (URKL)** 

**AERODROME CHART** 

- 27 - 

GND 15 

##### TERPS 

##### AERODROME CHART 

##### NOVOROSSIYSK (URKN) 



<!-- Start of picture text -->
44° 41.00 44° 41.00<br>Coordinates:<br>P1 44°40.268` N 037°46.709` E Intersection TWY T / N2<br>P2 44°40.121` N 037°46.542` E Intersection TWY T / N1<br>P3 44°40.379` N 037°47.052` E Holding Position B<br>APRON Fire<br>Maintenance NORTH Station North<br>Area<br>44° 40.50 T 44° 40.50<br>Fuel Depot A<br>M T P3 ELEV<br>B 131 [ft]<br>40 [m]<br>N2<br>TWR<br>P1<br>N1 T<br>Fire P2 Cargo<br>Station South Store<br>ASR<br>44° 40.00 44° 40.00<br>APRON<br>SOUTH<br>T<br>Parking Positions Shelters next TWY N1 & N2<br>ELEV<br>26 37<br>13140 [m][ft] C 21 25 27 29 31 36 38<br>20<br>19 23 30 34 35<br>24<br>18 22 32 33<br>17 28<br>44° 39.50 Additional Combined Frequencies: 44° 39.50<br>UHF 344.000 GCA Search<br>UHF 385.400 GCA Final<br>VHF 123.300 GCA<br>B  L  A  C  K      S  E  A<br>UHF 257.800 Tower<br>TN<br>VHF 122.100 Tower MN<br>RWY CAT MINIMA<br>ARP ELEV Scale 1:18`000<br>PAR 04 A B C D E 331  - 0.8 200 (200-0.8/1.6) GS 3°<br>44° 40.084`  N 131 [ft] 0 200 400 600 [m]<br>SRA 04 - 22 A B C D E 481  - 1.2 350 (350-1.2/1.6)<br>037° 46.694`  E 40 [m] 0 500 1000 1500 2000 [ft]<br>RWY TORA TODA ASDA LDA PSN THR ALS<br>04 5905 [ft] 1800 [m] 5905 [ft] 1800 [m] 5905 [ft] 1800 [m] 5905 [ft] 1800 [m] 44°39.744`N  037°46.213`E<br>22 5905 [ft] 1800 [m] 5905 [ft] 1800 [m] 5905 [ft] 1800 [m] 5905 [ft] 1800 [m] 44°40.424`N  037°47.176`E<br>Tower Radar Final - Precision TACAN ILS<br>123.000 MHz<br>X<br>9-16<br>X<br>04<br>222°T<br>1800 x 60[m]<br>5905 x 197[ft]<br>042°T<br>216°<br>036°<br>1-8<br>VAR 6° E(2010)<br>037° 46.00 037° 46.50 037° 47.00 037° 47.50<br> Flaming Cliffs Flight Simulator A-10C 3Ground Chart for Warthog DCS &<br>037° 46.00 037° 46.50 037° 47.00 037° 47.50<br> www.10thGunfighters.de www.ariescon.comrev 3.6.0 03.05.2013 dp © -<br>X<br>22<br><!-- End of picture text -->

#### **AERODROME CHART** 

#### **NOVOROSSIYSK (URKN)** 

- 28 - 

GND 16 

TERPS 

AERODROME CHART 

##### KRYMSK (URKW) 



<!-- Start of picture text -->
Fuel Depot<br>Coordinates:<br>P1 44°57.648` N 037°59.190` E Holding Position A<br>ELEV<br>P2 44°57.766` N 037°59.590` E Intersection TWY B / D<br>66 [ft]<br>P3 44°58.177` N 038°00.129` E Intersection TWY C / D<br>20 [m]<br>P4 44°58.469` N 038°00.272` E Holding Position D<br>Parking Positions Shelters next TWY C & D APRON 2<br>44° 58.50 44° 58.50<br>P4 Fire<br>50 49 53 D Station 2<br>52<br>47 48 51<br>46 D<br>44 43 45 F<br>42<br>C<br>Maintenance<br>P3<br>Area<br>ASR<br>D<br>TWR<br>44° 58.00 44° 58.00<br>C<br>G<br>D<br>40<br>C 41 39<br>B<br>P2 36<br>35<br>D<br>B<br>ELEV P1<br>A<br>66 [ft]<br>C<br>20 [m]<br>Additional Combined Frequencies:<br>44° 57.50 A UHF 344.000 GCA Search 44° 57.50<br>Fire 23 26 UHF 385.400 GCA Final<br>Station 1 25 VHF 123.300 GCA<br>C 20 21 58 24 UHF 257.800 Tower<br>VHF 122.100 Tower<br>19<br>18 TN<br>16 17 MN<br>Cargo<br>Store<br>RWY CAT MINIMA<br>ARP ELEV Scale 1:18`000<br>PAR 04 - 22 A B C D E 266  - 0.8 200 (200-0.8/1.6) GS 3°<br>44° 58.073`  N 66 [ft] 0 200 400 600 [m]<br>SRA 04 - 22 A B C D E 416  - 1.2 350 (350-1.2/1.6)<br>037° 59.697`  E 20 [m] 0 500 1000 1500 2000 [ft]<br>RWY TORA TODA ASDA LDA PSN THR ALS<br>04 8530 [ft] 2600 [m] 8530 [ft] 2600 [m] 8530 [ft] 2600 [m] 8530 [ft] 2600 [m] 44°57.562`N  037°59.026`E<br>22 8530 [ft] 2600 [m] 8530 [ft] 2600 [m] 8530 [ft] 2600 [m] 8530 [ft] 2600 [m] 44°58.584`N  038°00.369`E<br>Tower Radar Final - Precision TACAN ILS<br>124.000 MHz<br>31<br>27<br>54-57<br>X<br>1-8<br>37<br>32<br>04<br>X<br>219°T X<br>2600 x 60[m] / 8530 x 197[ft]<br>033°<br>039°T<br>11<br>X<br>213°<br>38<br>30<br>29<br>28<br>10<br>APRON 1 09<br>12<br>13<br>14<br>15<br>VAR 6° E(2010)<br>33<br>34<br>037° 59.00 037° 59.50 038° 00.00 038° 00.50<br> Flaming Cliffs Flight Simulator A-10C 3Ground Chart for Warthog DCS &<br>037° 59.00 037° 59.50 038° 00.00 038° 00.50<br> www.10thGunfighters.de www.ariescon.comrev 3.6.0 03.05.2013 dp © -<br>22<br><!-- End of picture text -->

**KRYMSK (URKW)** 

**AERODROME CHART** 

- 29 - 

GND 17 

##### TERPS 



<!-- Start of picture text -->
AERODROME CHART MINERALNYE VODY (URMM)<br>44° 14.00 44° 14.00<br>44° 13.50 44° 13.50<br>ELEV<br>1050 [ft]<br>320 [m]<br>CWY A<br>44° 13.00 1312x492` 44° 13.00<br>400x150m<br>ASR<br>A SR<br>B<br>P1<br>A<br>C P2 Maintenance<br>Area<br>44° 13.50 44° 13.50<br>A P3<br>N<br>D<br>A P5<br>E<br>P4<br>Terminal<br>E1<br>A<br>TWR ELEV<br>44° 13.00 44° 13.00<br>1050 [ft]<br>Fire Station 320 [m]<br>Coordinates:<br>P1 44°13.767` N 043°04.255` E Intersection TWY A / B 1312x492`CWY<br>P2 44°13.609` N 043°04.937` E Holding Position C 400x150m<br>P3 44°13.420` N 043°05.351` E Holding Position D<br>P4 44°13.167` N 043°05.556` E Apron 1 East, TWY A TN<br>P5 44°13.139` N 043°06.107` E Holding Position N MN<br>44° 12.50<br>RWY CAT MINIMA<br>ARP ELEV Scale 1:25`000<br>PAR 12 - 30 A B C D E 1250  - 0.8 200 (200-0.8/1.6) GS 3°<br>44° 13.672`  N 1050 [ft] 0 200 400 600 800 [m]<br>SRA 12 - 30 A B C D E 1400  - 1.2 350 (350-1.2/1.6)<br>043° 04.870`  E 320 [m] 0 1000 2000 [ft]<br>RWY TORA TODA ASDA LDA PSN THR ALS<br>12 13350 [ft] 4070 [m] 14660 [ft] 4470 [m] 13350 [ft] 4070 [m] 13350 [ft] 4070 [m] 44°14.254`N  043°03.591`E<br>30 13350 [ft] 4070 [m] 14660 [ft] 4470 [m] 13350 [ft] 4070 [m] 13350 [ft] 4070 [m] 44°13.089`N  043°06.148`E<br>Tower Radar Final - Precision TACAN ILS RWY 12 ILS RWY 30<br>135.000 MHz 111.70 MHz 109.30 MHz<br>X<br>109°<br>289°<br>115°T<br>1-28<br>APRON 1 295°T X<br>X<br>4070 x 60[m] / 13350 x 197[ft]<br>30<br>VAR 6° E(2010)<br>043° 03.50 043° 04.00 043° 04.50 043° 05.00 043° 05.50 043° 06.00<br> Flaming Cliffs Flight Simulator A-10C 3Ground Chart for Warthog DCS &<br>043° 03.50 043° 04.00 043° 04.50 043° 05.00 043° 05.50 043° 06.00<br> www.10thGunfighters.de www.ariescon.comrev 3.6.0 03.05.2013 dp © -<br>12<br>X<br>X<br>X<br>X<br><!-- End of picture text -->

#### **MINERALNYE VODY (URMM)** 

**AERODROME CHART** 

GND 18 

- 30 - 

TERPS 

AERODROME CHART 

##### NALCHIK (URMN) 



<!-- Start of picture text -->
CWY<br>43° 31.50 984x492` 43° 31.50<br>300x150m<br>ELEV<br>1411 [ft]<br>430 [m]<br>Cargo<br>Store<br>TWR<br>43° 31.00 43° 31.00<br>Fuel Depot ASR Fire<br>Station<br>APRON 2<br>A<br>B APRON 1<br>P2 E<br>A<br>43° 30.50 P1 43° 30.50<br>Maintenance<br>Terminal Area<br>ELEV<br>1411 [ft]<br>430 [m]<br>Coordinates:<br>P1 43°30.538` N 043°37.547` E Holding Position A<br>P2 43°30.677` N 043°37.840` E Holding Position B<br>TN<br>MN<br>43° 30.00<br>RWY CAT MINIMA<br>ARP ELEV Scale 1:18`000<br>PAR 06 - 24 A B C D E 1610  - 0.8 200 (200-0.8/1.6) GS 3°<br>43° 30.842`  N 1411 [ft] 0 200 400 600 [m]<br>SRA 06 - 24 A B C D E 1760  - 1.2 350 (350-1.2/1.6)<br>043° 38.193`  E 430 [m] 0 500 1000 1500 2000 [ft]<br>RWY TORA TODA ASDA LDA PSN THR ALS<br>06 7545 [ft] 2300 [m] 8530 [ft] 2600 [m] 7545 [ft] 2300 [m] 7545 [ft] 2300 [m] 43°30.562`N  043°37.443`E<br>24 7545 [ft] 2300 [m] 7545 [ft] 2300 [m] 7545 [ft] 2300 [m] 7545 [ft] 2300 [m] 43°31.122`N  043°38.943`E<br>Tower Radar Final - Precision TACAN ILS RWY 24<br>136.000 MHz 110.50 MHz<br>235°T<br>X<br>2300 x 60[m] / 7545 x 197[ft]<br>055°T<br>229°<br>049° 1-15<br>06<br>VAR 6° E(2010)<br>043° 37.50 043° 38.00 043° 38.50 043° 39.00<br> Flaming Cliffs Flight Simulator A-10C 3Ground Chart for Warthog DCS &<br>043° 37.50 043° 38.00 043° 38.50 043° 39.00<br> www.10thGunfighters.de www.ariescon.comrev 3.6.0 03.05.2013 dp © -<br>24<br>X<br>X<br>X<br>X<br><!-- End of picture text -->

**NALCHIK (URMN)** 

**AERODROME CHART** 



<!-- Start of picture text -->
TERPS GND 19 - 31 -<br>AERODROME CHART BESLAN (URMO)<br>43° 13.50 43° 13.50<br>Coordinates:<br>P1 43°12.323` N 044°36.262` E Holding Position W<br>43° 13.00 P2 43°12.255` N 044°36.712` E Holding Position E 43° 13.00<br>ELEV<br>1772 [ft]<br>ELEV<br>540 [m]<br>1772 [ft]<br>43° 12.50 43° 12.50<br>540 [m]<br>P1<br>P2<br>SWY<br>180`55m<br>CWY<br>1148x492` SWY<br>350x150m 180`55m<br>CWY<br>1148x492`<br>43° 12.00 350x150m 43° 12.00<br>43° 11.50 43° 11.50<br>TN<br>MN<br>RWY CAT MINIMA<br>ARP ELEV Scale 1:25`000<br>PAR 10 - 28 A B C D E 1971  - 0.8 200 (200-0.8/1.6) GS 3°<br>43° 12.342`  N 1772 [ft] 0 200 400 600 800 [m]<br>SRA 10 - 28 A B C D E 2121  - 1.2 350 (350-1.2/1.6)<br>044° 36.346`  E 540 [m] 0 1000 2000 [ft]<br>RWY TORA TODA ASDA LDA PSN THR ALS<br>10 9890 [ft] 3015 [m] 11040 [ft] 3365 [m] 10070 [ft] 3070 [m] 9890 [ft] 3015 [m] 43°12.501`N  044°35.275`E E<br>28 9890 [ft] 3015 [m] 11040 [ft] 3365 [m] 10070 [ft] 3070 [m] 9890 [ft] 3015 [m] 43°12.182`N  044°37.416`E<br>Tower Radar Final - Precision TACAN ILS RWY 10<br>141.000 MHz 110.50 MHz<br>W<br>087°<br>093°T<br>3015 x 50 [m] / 9890 x 164 [ft] 267°<br>273°T<br>E<br>Terminal 1-15<br>ASR<br>Maintenance<br>Area<br>APRON<br>SOUTH<br>Fire Station<br>TWR<br>VAR 6° E(2010)<br>X X<br>28<br>044° 35.00 044° 35.50 044° 36.00 044° 36.50 044° 37.00 044° 37.50<br> Flaming Cliffs Flight Simulator A-10C 3Ground Chart for Warthog DCS &<br>044° 35.00 044° 35.50 044° 36.00 044° 36.50 044° 37.00 044° 37.50<br> www.10thGunfighters.de www.ariescon.comrev 3.6.0 03.05.2013 dp © -<br>10<br><!-- End of picture text -->

#### **AERODROME CHART** 

**BESLAN (URMO)** 

GND 20 

##### TERPS 

##### AERODROME CHART 



<!-- Start of picture text -->
- 32 -<br><!-- End of picture text -->

##### SOCHI - ADLER (URSS) 



<!-- Start of picture text -->
Coordinates: Additional Combined Frequencies:<br>P1 43°26.427` N 039°55.624` E Holding Position B UHF 344.000 GCA Search<br>P2 43°26.610` N 039°56.207` E Holding Position D UHF 385.400 GCA Final<br>43° 27.50 43° 27.50<br>P3 43°26.926` N 039°57.216` E Holding Position I VHF 123.300 GCA<br>P4 43°26.849` N 039°57.503` E Shelters TWY J UHF 257.800 Tower<br>VHF 122.100 Tower<br>Parking Positions Shelters next TWY J ELEV<br>98 [ft]<br>ELEV<br>67 64 61 58 55 52 49 46 43 30 [m] 98 [ft]<br>Fire Station 1<br>30 [m]<br>Maintenance<br>I<br>68 65 62 59 56 53 50 47 44 Area J<br>66 63 60 57 54 51 48 45 42 J<br>J<br>43° 27.00 M P3 43° 27.00<br>I<br>Fire<br>H Station 3<br>P4<br>G<br>J<br>TWR<br>M F<br>G<br>E CON<br>Terminal<br>P2<br>Fire D ASR<br>Station 2 M J<br>43° 26.50 PEM 43° 26.50<br>C<br>B<br>M P1<br>A<br>ELEV<br>ELEV 98 [ft]<br>98 [ft] 30 [m]<br>Cargo<br>30 [m]<br>Store Fuel Depot<br>TN<br>43° 26.00<br>MN<br>RWY CAT MINIMA<br>ARP ELEV Scale 1:18`000<br>PAR 06 A B C D E 298  - 0.8 200 (200-0.8/1.6) GS 3°<br>02 A B C D E 298  - 0.8 200 (200-0.8/1.6) GS 3° 43° 26.669`  N 98 [ft] 0 200 400 600 [m]<br>SRA 06 - 24 A B C D E 448  - 1.2 350 (350-1.2/1.6)<br>02 - 20 A B C D E 448  - 1.2 350 (350-1.2/1.6) 039° 56.489`  E 30 [m] 0 500 1000 1500 2000 [ft]<br>RWY TORA TODA ASDA LDA PSN THR ALS<br>06 10170 [ft] 3100 [m] 10170 [ft] 3100 [m] 10170 [ft] 3100 [m] 10170 [ft] 3100 [m] 43°26.337`N   039°55.432`E<br>24 10170 [ft] 3100 [m] 10170 [ft] 3100 [m] 10170 [ft] 3100 [m] 10170 [ft] 3100 [m] 43°26.997`N  039°57.540`E<br>02 7220 [ft] 2200 [m] 7220 [ft] 2200 [m] 7220 [ft] 2200 [m] 7220 [ft] 2200 [m] 43°26.149`N   039°56.642`E<br>20 7220 [ft] 2200 [m] 7220 [ft] 2200 [m] 7220 [ft] 2200 [m] 7220 [ft] 2200 [m] 43°27.167`N  039°57.459`E<br>Tower Radar Final - Precision TACAN ILS RWY 06<br>127.000 MHz 111.10 MHz<br>02<br>236°<br>242°T<br>3100 x 60[m] / 10170 x 197[ft]<br>XX<br>X<br>056°<br>062°T<br>APRON 1<br>19-41<br>APRON 21-18 X<br>SHELTERS<br>X<br>X<br>06<br>205°T<br>2200 x 60[m] / 7220 x 197[ft]<br>025°T<br>199°<br>019°<br>VAR 6° E(2010)<br>039° 55.50 039° 56.00 039° 56.50 039° 57.00 039° 57.50<br> Flaming Cliffs Flight Simulator A-10C 3Ground Chart for Warthog DCS &<br>039° 55.50 039° 56.00 039° 56.50 039° 57.00<br> www.10thGunfighters.de www.ariescon.comrev 3.6.0 03.05.2013 dp © -<br>24<br>X<br>X<br>20<br><!-- End of picture text -->

#### **AERODROME CHART** 

**SOCHI - ADLER (URSS)** 

- 33 - 

GND 21 

- 34 - 

TERPS 

##### AERODROME CHART 

##### MOZDOK (XRMF) 



<!-- Start of picture text -->
Coordinates:<br>43° 48.50 P1 43°47.384` N 044°34.846` E Intersection TWY A / S 43° 48.50<br>P2 43°47.464` N 044°35.476` E Holding Position B<br>P3 43°47.374` N 044°35.845` E Intersection TWY A / C<br>P4 43°47.365` N 044°36.870` E Intersection TWY A / D<br>P5 43°47.250` N 044°37.017` E Ramp 2 East, TWY E<br>Additional Combined Frequencies:<br>UHF 344.000 GCA Search<br>UHF 385.400 GCA Final<br>CWY<br>43° 48.00 VHF 123.300 GCA 1312x492` 43° 48.00<br>400x150m<br>UHF 257.800 Tower<br>ELEV<br>VHF 122.100 Tower<br>SWY 499 [ft]<br>1361`415m<br>152 [m]<br>CWY<br>2132x492`<br>650x150m<br>ELEV<br>509 [ft]<br>43° 47.50 155 [m] D BRI E 43° 47.50<br>P4 A Last Chance<br>C<br>P2 B P3 A D P5 E<br>A A C CON E 25 Fuel<br>B<br>A P1 E M Station 1<br>PEM<br>G TWR<br>Last Chance<br>Maintenance<br>S<br>43° 47.00 RAMP 1 Area 43° 47.00<br>S<br>RAMP<br>SOUTH 43° 46.50<br>Fuel<br>Station 2 TN<br>MN<br>RWY CAT MINIMA<br>ARP ELEV Scale 1:25`000<br>PAR 08 - 26 A B C D E 708  - 0.8 200 (200-0.8/1.6) GS 3°<br>43° 47.504`  N 509 [ft] 0 200 400 600 800 [m]<br>SRA 08 - 26 A B C D E 858  - 1.2 350 (350-1.2/1.6)<br>044° 35.981`  E 155 [m] 0 1000 2000 [ft]<br>RWY TORA TODA ASDA LDA PSN THR ALS<br>08 10235 [ft] 3120 [m] 11545 [ft] 3520 [m] 10235 [ft] 3120 [m] 10235 [ft] 3120 [m] 43°47.514`N  044°34.984`E E<br>26 10235 [ft] 3120 [m] 12365 [ft] 3770 [m] 11595 [ft] 3535 [m] 10235 [ft] 3120 [m] 43°47.495`N  044°37.279`E<br>Tower Radar Final - Precision TACAN ILS<br>137.000 MHz<br>23<br>30 29 28<br>256°<br>262°T<br>3120 x 70 [m] / 10235 x 230 [ft]<br>082°T<br>1-22<br>31<br>X RAMP 2<br>076°<br>24<br>39 37 35<br>38 36<br>X<br>X<br>X<br>X<br>27<br>26<br>32<br>33<br>34<br>VAR 6° E(2010)<br>X<br>08<br>044° 34.50 044° 35.00 044° 35.50 044° 36.00 044° 36.50 044° 37.00<br> Flaming Cliffs Flight Simulator A-10C 3Ground Chart for Warthog DCS &<br>044° 34.50 044° 35.00 044° 35.50 044° 36.00 044° 36.50 044° 37.00<br> www.10thGunfighters.de www.ariescon.comrev 3.6.0 03.05.2013 dp © -<br>26<br><!-- End of picture text -->



<!-- Start of picture text -->
MOZDOK (XRMF)<br><!-- End of picture text -->

**AERODROME CHART** 

