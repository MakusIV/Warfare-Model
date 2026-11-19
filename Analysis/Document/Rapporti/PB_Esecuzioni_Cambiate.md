# PB — Esecuzioni cambiate con l'interruttore acceso (blocco 2, formato R1)

Rapporto del blocco 2 della `Proposta_Pd_Bordo_Portata.md` (decisione PB-4 = R1), scritto dalla sessione principale il
2026-11-19 sul ProArt. **Sola lettura**: interruttore `PD_EDGE_RECALIBRATION` impostato in memoria (acceso, Pd al
bordo 0,2 = STIMA senza fonte, decisione PB-2), nessuna modifica al repository ne' alla fotografia. Codice `598af98e`
(blocco 1, interruttore spento di default), riferimento = fotografia da 1219 (`fdb78b86`). Script, `report_on.json` e
l'elenco delle esecuzioni cambiate in `Rapporti/Sonde_Pd_Bordo/` (v. `LEGGIMI.md`).

**Controllo della sonda:** con l'interruttore spento su `S36-GRAZE|S23`, 96 esecuzioni, 0 cambiate.

**Sintesi.** 752 esecuzioni su 1219 cambiano (467 identiche); 84 hanno l'esito di forza cambiato; le salve delle
esecuzioni cambiate scendono da 23979 a 19983 e le distruzioni da 1513 a 1476; a parita' di estrazione si perdono 1016
rilevamenti su 34631 in portata (2,9 %), nessuno si guadagna (la nuova Pd e' sempre <= alla vecchia). I numeri
coincidono con le stime della Proposta (§1.7). Come leggerlo: per famiglie (§1), poi i 84 casi dove cambia il
risultato dello scontro (§2); la causa e' unica e leggibile (soglia di rilevamento piu' bassa), l'effetto a cascata
cambia ingaggi e estrazioni successive.

## 1. Esecuzioni cambiate per famiglia di scenari

Interruttore `PD_EDGE_RECALIBRATION` acceso in memoria, Pd al bordo 0.2 (prima 0.5). Riferimento: fotografia da 1219. Esecuzioni: 1219; **cambiate 752**, invariate 467, nuove 0, mancanti 0, errori 0.

Voci del riassunto che cambiano (numero di esecuzioni): `damage_events` 608, `ammunition_events` 577, `assets` 463, `fuel` 434, `engagements` 412, `counts` 374, `ammunition_consumed` 369, `postures` 246, `detections` 116, `force_outcomes` 84, `actual_etas` 39, `interception_events` 17, `interceptions` 15, `session` 10.

| Famiglia | Cambiate / totali | Esito di forza cambiato | Salve prima -> dopo | Distruzioni prima -> dopo |
|---|---|---|---|---|
| ORC-base | 1 / 1 | 1 | 6 -> 6 | 1 -> 1 |
| ORC-fuel | 0 / 1 | 0 | 0 -> 0 | 0 -> 0 |
| ORC-interval | 2 / 2 | 1 | 28 -> 30 | 6 -> 7 |
| ORC-nocontact | 0 / 1 | 0 | 0 -> 0 | 0 -> 0 |
| ORC-seed | 2 / 2 | 2 | 11 -> 10 | 4 -> 4 |
| ORC-twofronts | 10 / 10 | 5 | 75 -> 54 | 14 -> 4 |
| S1 | 14 / 16 | 4 | 78 -> 75 | 27 -> 24 |
| S10 | 10 / 30 | 0 | 83 -> 75 | 35 -> 33 |
| S11 | 6 / 6 | 2 | 65 -> 41 | 18 -> 15 |
| S12 | 12 / 12 | 2 | 145 -> 129 | 47 -> 46 |
| S13 | 6 / 6 | 2 | 138 -> 147 | 34 -> 34 |
| S14 | 6 / 6 | 1 | 163 -> 163 | 28 -> 30 |
| S15 | 12 / 12 | 0 | 133 -> 123 | 55 -> 53 |
| S16 | 4 / 4 | 0 | 160 -> 184 | 52 -> 55 |
| S17 | 15 / 15 | 4 | 357 -> 359 | 109 -> 112 |
| S18 | 8 / 8 | 2 | 108 -> 99 | 42 -> 47 |
| S19 | 1 / 4 | 0 | 6 -> 6 | 2 -> 2 |
| S19AD | 6 / 24 | 0 | 38 -> 39 | 26 -> 26 |
| S2 | 24 / 24 | 12 | 181 -> 184 | 62 -> 57 |
| S20 | 12 / 12 | 5 | 75 -> 67 | 21 -> 17 |
| S21 | 14 / 16 | 4 | 229 -> 223 | 49 -> 45 |
| S21R | 3 / 6 | 0 | 31 -> 30 | 21 -> 21 |
| S22-AIR | 3 / 40 | 0 | 9 -> 9 | 3 -> 3 |
| S22-E1 | 11 / 16 | 6 | 20 -> 11 | 7 -> 4 |
| S22-E3 | 10 / 16 | 4 | 22 -> 6 | 10 -> 2 |
| S23-CAP | 8 / 32 | 1 | 40 -> 39 | 15 -> 16 |
| S23-HOLD | 21 / 24 | 0 | 1332 -> 372 | 0 -> 0 |
| S23-TOT | 24 / 24 | 0 | 240 -> 228 | 0 -> 0 |
| S24-E5 | 22 / 32 | 0 | 14198 -> 11482 | 0 -> 0 |
| S24-GLIDE | 0 / 32 | 0 | 0 -> 0 | 0 -> 0 |
| S24-ORBIT | 12 / 24 | 0 | 40 -> 40 | 15 -> 15 |
| S25-DMG | 21 / 24 | 0 | 643 -> 640 | 0 -> 0 |
| S25-DUR | 0 / 24 | 0 | 0 -> 0 | 0 -> 0 |
| S25-POST | 0 / 16 | 0 | 0 -> 0 | 0 -> 0 |
| S25-TGT | 23 / 24 | 2 | 105 -> 106 | 49 -> 49 |
| S25-WIN | 0 / 24 | 0 | 0 -> 0 | 0 -> 0 |
| S26-BINGO | 49 / 96 | 0 | 1117 -> 1075 | 0 -> 0 |
| S27-DOUBLE | 40 / 40 | 0 | 1836 -> 1766 | 0 -> 0 |
| S28-CLASS | 2 / 24 | 0 | 16 -> 16 | 4 -> 4 |
| S28-ROE | 0 / 20 | 0 | 0 -> 0 | 0 -> 0 |
| S28-ZONE | 0 / 8 | 0 | 0 -> 0 | 0 -> 0 |
| S29-AREA | 0 / 12 | 0 | 0 -> 0 | 0 -> 0 |
| S3 | 40 / 40 | 10 | 717 -> 671 | 240 -> 233 |
| S30-ABSENT | 0 / 3 | 0 | 0 -> 0 | 0 -> 0 |
| S30-CAMPAIGN | 0 / 4 | 0 | 0 -> 0 | 0 -> 0 |
| S31-VISUAL | 0 / 20 | 0 | 0 -> 0 | 0 -> 0 |
| S32-DWELL | 8 / 20 | 0 | 48 -> 46 | 26 -> 26 |
| S33-PASSES | 6 / 10 | 0 | 45 -> 43 | 19 -> 19 |
| S34-BAND | 9 / 32 | 0 | 54 -> 54 | 54 -> 54 |
| S35-ADTGT | 6 / 32 | 1 | 33 -> 31 | 21 -> 22 |
| S36-BAND | 48 / 48 | 0 | 0 -> 0 | 0 -> 0 |
| S36-CUT | 8 / 8 | 0 | 0 -> 0 | 0 -> 0 |
| S36-FAMILIES | 28 / 28 | 0 | 0 -> 0 | 0 -> 0 |
| S36-GRAZE | 16 / 16 | 0 | 0 -> 0 | 0 -> 0 |
| S36-PASSES | 16 / 16 | 0 | 0 -> 0 | 0 -> 0 |
| S4 | 15 / 16 | 5 | 131 -> 116 | 34 -> 31 |
| S5 | 87 / 96 | 0 | 516 -> 517 | 202 -> 201 |
| S6 | 4 / 4 | 3 | 203 -> 158 | 21 -> 19 |
| S7 | 6 / 6 | 1 | 83 -> 82 | 29 -> 29 |
| S8 | 1 / 1 | 1 | 240 -> 235 | 63 -> 65 |
| S9 | 15 / 18 | 1 | 106 -> 101 | 22 -> 20 |
| S9R | 21 / 24 | 2 | 67 -> 87 | 22 -> 27 |
| VAL-agn | 2 / 4 | 0 | 4 -> 4 | 4 -> 4 |
| VAL-det | 2 / 3 | 0 | 4 -> 4 | 0 -> 0 |
| **Totale** | **752 / 1219** | **84** | **23979 -> 19983** | **1513 -> 1476** |

Salve e distruzioni sono sommate sulle sole esecuzioni cambiate (le invariate hanno gli stessi valori).

## 2. Esecuzioni con esito di forza cambiato

84 esecuzioni (`force_outcomes` diverso dalla fotografia):

- `ORC-base/S-test`
- `ORC-interval/S-open`
- `ORC-seed/S-alpha`
- `ORC-seed/S-beta`
- `ORC-twofronts/S-f1/first`
- `ORC-twofronts/S-f2/first`
- `ORC-twofronts/S-f3/first`
- `ORC-twofronts/S-stable/first`
- `ORC-twofronts/S-stable/second`
- `S1/S1-1/without_cas`
- `S1/S1-3/without_cas`
- `S1/S1-5/without_cas`
- `S1/S1-6/without_cas`
- `S11/S11-c-dcs`
- `S11/S11-c-synthetic`
- `S12/S12-1/prolonged`
- `S12/S12-2/c2_strike`
- `S13/S13-2`
- `S13/S13-3`
- `S14/S14-4`
- `S17/S17-0/Company_k=1`
- `S17/S17-0/Division_k=6`
- `S17/S17-1/Battallion_k=2`
- `S17/S17-2/Battallion_k=2`
- `S18/S18-2/network`
- `S18/S18-5/network`
- `S2/S2-0-sead`
- `S2/S2-1-sead`
- `S2/S2-1/after_sead`
- `S2/S2-2/baseline`
- `S2/S2-3/baseline`
- `S2/S2-4/baseline`
- `S2/S2-5-sead`
- `S2/S2-5/after_sead`
- `S2/S2-6-sead`
- `S2/S2-6/after_sead`
- `S2/S2-6/baseline`
- `S2/S2-7-sead`
- `S20/S20-1/split`
- `S20/S20-2/split`
- `S20/S20-4/single`
- `S20/S20-4/split`
- `S20/S20-5/split`
- `S21/S21-0/parked`
- `S21/S21-4/control`
- `S21/S21-4/parked`
- `S21/S21-5/control`
- `S22-E1/S22-E1-0/finished`
- `S22-E1/S22-E1-0/static`
- `S22-E1/S22-E1-1/finished`
- `S22-E1/S22-E1-1/static`
- `S22-E1/S22-E1-4/static`
- `S22-E1/S22-E1-6/finished`
- `S22-E3/S22-E3-1/late`
- `S22-E3/S22-E3-1/not_departed`
- `S22-E3/S22-E3-6/late`
- `S22-E3/S22-E3-6/not_departed`
- `S23-CAP/S23-CAP-7/during`
- `S25-TGT/S25-TGT-4/target`
- `S25-TGT/S25-TGT-5/target`
- `S3/S3-0/control`
- `S3/S3-0/stealth`
- `S3/S3-1/stealth`
- `S3/S3-12/control`
- `S3/S3-15/control`
- `S3/S3-16/control`
- `S3/S3-18/control`
- `S3/S3-4/control`
- `S3/S3-7/control`
- `S3/S3-9/control`
- `S35-ADTGT/S35-ADTGT-2/naval_maverick_on`
- `S4/S4-2/with_sam`
- `S4/S4-3/with_sam`
- `S4/S4-5/with_sam`
- `S4/S4-6/with_sam`
- `S4/S4-7/with_sam`
- `S6/S6-0`
- `S6/S6-2`
- `S6/S6-3`
- `S7/S7-3`
- `S8/S8-scale`
- `S9/S9-2/detection_factor=0.0`
- `S9R/S9R-3/recon`
- `S9R/S9R-3/unseen`

## 3. Rilevamenti a parita' di estrazione (spia sulle `Detection`)

Estrazioni di rilevamento: 35619 (fuori portata 988, in portata 34631). Rilevati ora 30450; con la soglia vecchia e la STESSA estrazione sarebbero stati 31466. **Persi 1016** (2.9 % delle estrazioni in portata), **guadagnati 0**. E' l'effetto di primo ordine: a cascata cambiano anche gli ingaggi e le estrazioni successive.

| Fascia di distanza (d/R) | Estrazioni in portata | Rilevamenti persi |
|---|---|---|
| 0.0-0.1 | 14904 | 0 |
| 0.1-0.2 | 5462 | 0 |
| 0.2-0.3 | 1846 | 0 |
| 0.3-0.4 | 3631 | 7 |
| 0.4-0.5 | 1165 | 16 |
| 0.5-0.6 | 1008 | 37 |
| 0.6-0.7 | 577 | 28 |
| 0.7-0.8 | 2896 | 294 |
| 0.8-0.9 | 1806 | 325 |
| 0.9-1.0 | 1336 | 309 |

## 4. Unita' S36: `Detection` prima / dopo

| Unita' | `Detection` | Pd cambiata | Rilevato prima | Rilevato dopo | Rilevamenti persi | Guadagnati |
|---|---|---|---|---|---|---|
| S36-BAND | 88 | 64 | 29 | 23 | 6 | 0 |
| S36-CUT | 48 | 48 | 42 | 36 | 6 | 0 |
| S36-FAMILIES | 52 | 36 | 10 | 8 | 2 | 0 |
| S36-GRAZE | 128 | 128 | 91 | 76 | 15 | 0 |
| S36-PASSES | 44 | 44 | 28 | 23 | 5 | 0 |

Righe con esito di rilevamento o istante diversi (le altre hanno solo la Pd cambiata). Colonne: portata [m], CPA [m], Pd prima -> dopo, estrazione, rilevato prima -> dopo, istante prima -> dopo [s].

| Esecuzione | Osservatore -> bersaglio | R | CPA | Pd | Estr. | Rilevato | Istante |
|---|---|---|---|---|---|---|---|
| `S36-BAND/S36-BAND-0/buk_min` | Red-Line/obs0 -> Blue-CAS/cas0 | 85000 | 84999 | 0.5000 -> 0.2000 | 0.4665 | True -> False | 126.3 -> - |
| `S36-BAND/S36-BAND-0/s300_min` | Red-Line/obs0 -> Blue-CAS/cas0 | 150000 | 149999 | 0.5000 -> 0.2000 | 0.4665 | True -> False | 125.6 -> - |
| `S36-BAND/S36-BAND-0/tor_min` | Red-Line/obs0 -> Blue-CAS/cas0 | 25000 | 25000 | 0.5000 -> 0.2000 | 0.4665 | True -> False | 127.8 -> - |
| `S36-BAND/S36-BAND-3/buk_max` | Red-Line/obs0 -> Blue-CAS/cas0 | 85000 | 84999 | 0.1125 -> 0.0450 | 0.0725 | True -> False | 126.3 -> - |
| `S36-BAND/S36-BAND-3/p37_max` | Red-Line/obs0 -> Blue-CAS/cas0 | 280000 | 279999 | 0.1763 -> 0.0705 | 0.0725 | True -> False | 125.0 -> - |
| `S36-BAND/S36-BAND-3/strela10_max` | Red-Line/obs0 -> Blue-CAS/cas0 | 10000 | 9999 | 0.1334 -> 0.0534 | 0.0725 | True -> False | 127.8 -> - |
| `S36-CUT/S36-CUT-0/off` | Red-Line/obs0 -> Blue-CAS/casB0 | 6000 | 5601 | 0.6204 -> 0.3926 | 0.5493 | True -> False | 118.1 -> - |
| `S36-CUT/S36-CUT-0/on` | Red-Line/obs0 -> Blue-CAS/casA0 | 6000 | 5866 | 0.1698 -> 0.0841 | 0.1066 | True -> False | 119.0 -> - |
| `S36-CUT/S36-CUT-0/on` | Red-Line/obs0 -> Blue-CAS/casB0 | 6000 | 5601 | 0.5816 -> 0.3681 | 0.5493 | True -> False | 119.1 -> - |
| `S36-CUT/S36-CUT-1/off` | Red-Line/obs0 -> Blue-CAS/casC0 | 6000 | 4717 | 0.8089 -> 0.6943 | 0.6996 | True -> False | 115.5 -> - |
| `S36-CUT/S36-CUT-1/on` | Red-Line/obs0 -> Blue-CAS/casC0 | 6000 | 4717 | 0.8089 -> 0.6943 | 0.6996 | True -> False | 115.5 -> - |
| `S36-CUT/S36-CUT-2/off` | Red-Line/obs0 -> Blue-CAS/casC0 | 6000 | 4717 | 0.8089 -> 0.6943 | 0.2431 | True -> True | 110.0 -> 110.6 |
| `S36-CUT/S36-CUT-2/on` | Red-Line/obs0 -> Blue-CAS/casA0 | 6000 | 5866 | 0.1698 -> 0.0841 | 0.1338 | True -> False | 119.0 -> - |
| `S36-CUT/S36-CUT-2/on` | Red-Line/obs0 -> Blue-CAS/casC0 | 6000 | 4717 | 0.8089 -> 0.6943 | 0.2431 | True -> True | 110.0 -> 110.6 |
| `S36-CUT/S36-CUT-3/off` | Red-Line/obs0 -> Blue-CAS/casB0 | 6000 | 5601 | 0.6204 -> 0.3926 | 0.3164 | True -> True | 117.0 -> 118.7 |
| `S36-CUT/S36-CUT-3/off` | Red-Line/obs0 -> Blue-CAS/casC0 | 6000 | 4717 | 0.8089 -> 0.6943 | 0.4447 | True -> True | 110.0 -> 113.9 |
| `S36-CUT/S36-CUT-3/on` | Red-Line/obs0 -> Blue-CAS/casB0 | 6000 | 5601 | 0.5816 -> 0.3681 | 0.3164 | True -> True | 117.0 -> 119.1 |
| `S36-CUT/S36-CUT-3/on` | Red-Line/obs0 -> Blue-CAS/casC0 | 6000 | 4717 | 0.8089 -> 0.6943 | 0.4447 | True -> True | 110.0 -> 113.9 |
| `S36-FAMILIES/S36-FAMILIES-2/e3a` | Blue-AEW/obs0 -> Red-Air/tgt0 | 400000 | 399998 | 0.2500 -> 0.1000 | 0.2189 | True -> False | 197.5 -> - |
| `S36-FAMILIES/S36-FAMILIES-3/e3a` | Blue-AEW/obs0 -> Red-Air/tgt0 | 400000 | 399998 | 0.2500 -> 0.1000 | 0.1870 | True -> False | 197.5 -> - |
| `S36-GRAZE/S36-GRAZE-0/band_max` | Blue-CAS/casA0 -> Red-Line/obs0 | 80000 | 5999 | 1.0000 -> 1.0000 | 0.9636 | True -> True | 0.0 -> 22.7 |
| `S36-GRAZE/S36-GRAZE-0/band_min` | Blue-CAS/casA0 -> Red-Line/obs0 | 80000 | 5999 | 1.0000 -> 1.0000 | 0.9636 | True -> True | 0.0 -> 22.7 |
| `S36-GRAZE/S36-GRAZE-0/band_min` | Red-Line/obs0 -> Blue-CAS/casB0 | 6000 | 5996 | 0.5014 -> 0.2022 | 0.4328 | True -> False | 255.7 -> - |
| `S36-GRAZE/S36-GRAZE-0/off` | Blue-CAS/casA0 -> Red-Line/obs0 | 80000 | 5999 | 1.0000 -> 1.0000 | 0.9636 | True -> True | 0.0 -> 22.7 |
| `S36-GRAZE/S36-GRAZE-0/off` | Red-Line/obs0 -> Blue-CAS/casB0 | 6000 | 5996 | 0.5014 -> 0.2022 | 0.4328 | True -> False | 255.7 -> - |
| `S36-GRAZE/S36-GRAZE-0/on` | Blue-CAS/casA0 -> Red-Line/obs0 | 80000 | 5999 | 1.0000 -> 1.0000 | 0.9636 | True -> True | 0.0 -> 22.7 |
| `S36-GRAZE/S36-GRAZE-0/on` | Red-Line/obs0 -> Blue-CAS/casB0 | 6000 | 5996 | 0.4513 -> 0.1820 | 0.4328 | True -> False | 255.7 -> - |
| `S36-GRAZE/S36-GRAZE-1/band_min` | Red-Line/obs0 -> Blue-CAS/casA0 | 6000 | 5999 | 0.4575 -> 0.1835 | 0.3786 | True -> False | 256.3 -> - |
| `S36-GRAZE/S36-GRAZE-1/band_min` | Red-Line/obs0 -> Blue-CAS/casB0 | 6000 | 5996 | 0.5014 -> 0.2022 | 0.3283 | True -> False | 255.7 -> - |
| `S36-GRAZE/S36-GRAZE-1/off` | Red-Line/obs0 -> Blue-CAS/casA0 | 6000 | 5999 | 0.5004 -> 0.2007 | 0.3786 | True -> False | 256.3 -> - |
| `S36-GRAZE/S36-GRAZE-1/off` | Red-Line/obs0 -> Blue-CAS/casB0 | 6000 | 5996 | 0.5014 -> 0.2022 | 0.3283 | True -> False | 255.7 -> - |
| `S36-GRAZE/S36-GRAZE-1/on` | Red-Line/obs0 -> Blue-CAS/casB0 | 6000 | 5996 | 0.4513 -> 0.1820 | 0.3283 | True -> False | 255.7 -> - |
| `S36-GRAZE/S36-GRAZE-2/band_min` | Red-Line/obs0 -> Blue-CAS/casC0 | 6000 | 5994 | 0.5021 -> 0.2033 | 0.4541 | True -> False | 255.4 -> - |
| `S36-GRAZE/S36-GRAZE-2/off` | Red-Line/obs0 -> Blue-CAS/casC0 | 6000 | 5994 | 0.5021 -> 0.2033 | 0.4541 | True -> False | 255.4 -> - |
| `S36-GRAZE/S36-GRAZE-2/on` | Red-Line/obs0 -> Blue-CAS/casC0 | 6000 | 5994 | 0.5021 -> 0.2033 | 0.4541 | True -> False | 255.4 -> - |
| `S36-GRAZE/S36-GRAZE-3/band_max` | Red-Line/obs0 -> Blue-CAS/casD0 | 6000 | 5979 | 0.5069 -> 0.2110 | 0.2862 | True -> False | 253.9 -> - |
| `S36-GRAZE/S36-GRAZE-3/band_min` | Red-Line/obs0 -> Blue-CAS/casD0 | 6000 | 5979 | 0.5069 -> 0.2110 | 0.2862 | True -> False | 253.9 -> - |
| `S36-GRAZE/S36-GRAZE-3/off` | Red-Line/obs0 -> Blue-CAS/casD0 | 6000 | 5979 | 0.5069 -> 0.2110 | 0.2862 | True -> False | 253.9 -> - |
| `S36-GRAZE/S36-GRAZE-3/on` | Red-Line/obs0 -> Blue-CAS/casD0 | 6000 | 5979 | 0.5069 -> 0.2110 | 0.2862 | True -> False | 253.9 -> - |
| `S36-PASSES/S36-PASSES-1/join_off` | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999 | 0.5002 -> 0.2003 | 0.2296 | True -> False | 128.1 -> - |
| `S36-PASSES/S36-PASSES-1/join_on` | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999 | 0.4689 -> 0.1878 | 0.2296 | True -> False | 128.1 -> - |
| `S36-PASSES/S36-PASSES-1/split_off` | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999 | 0.5002 -> 0.2003 | 0.2296 | True -> False | 128.1 -> - |
| `S36-PASSES/S36-PASSES-3/join_off` | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999 | 0.5002 -> 0.2003 | 0.2950 | True -> False | 130.1 -> - |
| `S36-PASSES/S36-PASSES-3/split_off` | Red-Line/obs0 -> Blue-CAS/cas0 | 6000 | 5999 | 0.5002 -> 0.2003 | 0.2950 | True -> False | 134.1 -> - |


## 5. Test che falliscono con l'interruttore acceso (suite completa)

Suite completa con l'interruttore acceso in memoria (`suite_pd_edge.py on`): `Ran 4973, failures 10, errors 0, skipped 7`. I fallimenti sono
**10**, esattamente quelli previsti dalla Proposta (§3 PB-6 e T1-1):

| Test | Esito | Trattamento deciso (PB-6) |
|---|---|---|
| `TestPdEdgeRecalibration.test_switch_is_off_by_default` | `True is not False` | atteso, per costruzione (prova il default spento) |
| `Test_Session_Simulator.TestEndToEnd` (6 test) e `TestPresenceAndPostures.test_postures_of_every_asset_in_the_outcome` | cambia l'esito degli ingaggi del fronte nord | (A) interruttore fissato spento nella classe base del file |
| `Test_Session_Scenarios_S23.TestS23GroundHold.test_the_halted_tank_is_engaged_during_the_hold` | `0,375 >= 0,5` non vale (3 su 8) | (A) interruttore fissato spento |
| `Test_Session_Scenarios_S36.TestS36Graze.test_same_draws_and_no_extra_detection` | `0 > 0`: nessun rilevamento perso per la D-5 | (B) premessa riscritta: "almeno una `Detection` con `probability < reference.probability`" |

Elenco grezzo in `Sonde_Pd_Bordo/suite_on_falliti.txt`. Con l'interruttore spento la suite e' quella del blocco 1
(`Ran 4973`, OK). L'elenco coincide con quello di PB-6: la decisione non va riaperta.

## 6. Esito atteso del blocco 3 (accensione)

Con `PD_EDGE_RECALIBRATION = True` come default e i test di PB-6 sistemati, il confronto con la fotografia da 1219
deve dare **752 CHANGED** (esattamente `Sonde_Pd_Bordo/changed_list_on.txt`) e **467 identiche**, 0 NEW, 0 MISSING.
Attenzione alle unita' `ORC-*` (17 esecuzioni nella fotografia, **15 cambiate** nella sonda, tutte nell'elenco): sono
costruite dalle classi di `Test_Session_Simulator`, dove PB-6 (A) fissa l'interruttore **spento**. Nel confronto del
blocco 3 quelle esecuzioni potrebbero quindi risultare identiche e non cambiate (rischio R-4 della Proposta): quante
dipende da come `Scenario_Baseline` le costruisce, e **non e' verificato qui**. Per questo l'elenco `changed_list_on.txt`
e' un massimo: dopo la sistemazione dei test (blocco 3) va rifatta la sonda per avere l'elenco atteso esatto, e le
differenze rispetto a 752 devono essere solo `ORC-*`.
