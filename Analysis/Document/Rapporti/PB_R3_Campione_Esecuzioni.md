# PB — R3: campione di 20 esecuzioni in forma completa (interruttore acceso)

Estensione R3 della decisione PB-4 (`Proposta_Pd_Bordo_Portata.md`), scritta dalla sessione principale il 2026-11-20.
**Sola lettura**: `PD_EDGE_RECALIBRATION` impostato in memoria (acceso, Pd al bordo 0,2 = STIMA senza fonte), nessuna
modifica al repository ne' alla fotografia. Prima = fotografia da 1219 installata; dopo = ricattura delle 20 esecuzioni con
l'interruttore acceso (codice `598af98e`). Script in `Sonde_Pd_Bordo/` (`r3_capture.py`, `r3_render.py`, `r3_keys.txt`).
Il rapporto R1 (`PB_Esecuzioni_Cambiate.md`) resta il quadro d'insieme.

**Come e' scelto il campione.** Le 20 esecuzioni NON sono casuali: le ho scelte io, 14 fra le 84 con esito di forza
cambiato (una per famiglia, mescolando terra, aria, mare, SEAD, furtivi) e 6 fra le cambiate senza esito di forza
cambiato (di cui 1 con la sola traiettoria di fine-grana cambiata). Non e' una stima di frequenze: serve a vedere i
meccanismi. Se vuoi altre esecuzioni basta indicarle (`r3_keys.txt`).

## Che cosa si vede (lettura mia, sui 20 casi)

1. **Effetto di primo ordine, pulito.** `S22-E1-0/static`: l'unica salva della fotografia (t = 31 s) non c'e' piu'
   perche' la stessa estrazione di rilevamento, con Pd piu' bassa al bordo, non rileva; il bersaglio non viene ingaggiato e
   l'esito di Blue-Armor passa da `destroyed` a `held`. Nei casi con meno salve (`S4-2`, `S20-1`, `S11-c-dcs`, `S27-DOUBLE`)
   lo stesso meccanismo ritarda o toglie il primo colpo (`first_shot` spostato).
2. **Effetto a cascata: lo scontro si riorganizza.** Un rilevamento perso o ritardato sposta tempi e ordine degli ingaggi,
   e cambiano le estrazioni successive: `S9R-3/unseen` va da 3 a 12 salve (compare un secondo ingaggio), `S11-c-dcs` da 15 a
   7 salve con due forze d'ingaggio in piu' (CAS e CAP), `S7-3` da 1 a 2 ingaggi. Qui il confronto prima/dopo non e' piu'
   "un rilevamento in meno": e' un'altra esecuzione dello stesso scenario.
3. **Il segno dell'esito NON e' sistematico.** Una forza peggiora in `S14-4` (Blue-Bombers: 1 -> 3 perdite, missione
   da `held` a `disengaged`), in `S2-2/baseline` (Blue-Strike 2 -> 4 perdite, esito `destroyed`) e in `S1-1` (Red-Line da
   `held` a `disengaged`); migliora in `S4-2` (Red-Armor da `disengaged/held` a `held/held`), in `S20-1` (Red-Line da
   `disengaged` a `held`, Blue-Armor il contrario) e in `S22-E1-0` (Blue-Armor da `destroyed` a `held`). Il numero di salve
   sale in `S3-0/stealth` (+5), `S16-0` (+4) e `S9R-3` (+9) e scende altrove. Con una Pd piu' bassa ci si aspettano meno
   rilevamenti, ma l'effetto sul risultato dipende dallo scenario: non emerge un lato che guadagna sistematicamente.
4. **Esecuzioni cambiate di poco** (6 su 20 senza esito cambiato): spostamenti di pochi secondi (`S23-CAP-0`: primo colpo
   +3,3 s; `S5-0/press_on`: esito di missione +35 s; `S12-0/prolonged`: solo valori fini) o di 1-2 salve (`S15-0`, `S27-DOUBLE`).
5. **Limite della lettura.** Una sola esecuzione per scenario e per seme: due esecuzioni diverse possono cambiare in modo
   opposto per puro caso di estrazione. Per un giudizio statistico serve guardare le famiglie (R1 §1 e §3: rilevamenti
   persi 1016 su 34631, 2,9 %, guadagnati 0), non un singolo caso.

## Le 20 esecuzioni

Formato: esiti di forza prima -> dopo, conteggi che cambiano, tabella delle grandezze del riepilogo (`run_digest`) che
cambiano, primi 6 eventi di danno della versione con interruttore acceso (campi: istante, tiratore, bersaglio, arma,
esito, salute prima, salute dopo, distrutto).

### `ORC-base/S-test`

Esiti di forza: {'Blue-North': ['held'], 'Blue-South': ['destroyed'], 'Red-East': ['disengaged'], 'Red-West': ['held']} -> {'Blue-North': ['disengaged', 'held'], 'Blue-South': ['destroyed'], 'Red-East': ['disengaged', 'held'], 'Red-West': ['held']}  **(cambiato)**
Conteggi: salvos 6->6, destroyed_events 1->1, engagements 2->3

| Grandezza | Prima | Dopo |
|---|---|---|
| Blue-North.outcome | held | disengaged/held |
| Red-East.outcome | disengaged | disengaged/held |
| M-north.mission_outcome | - | held lost=0 |
| Red-East.mission_outcome | - | held lost=0 |
| first_shot | 80.0 | 80.045041 |
| first_damage | 80.0 | 80.045041 |

Eventi di danno: 6 -> 6; primi 6 dopo:
  - [80.045041, 'bn1', 're2', None, 'damage', 100, 70, False]
  - [80.045041, 're2', 'bn1', None, 'damage', 100, 70, False]
  - [80.125314, 're1', 'bn2', None, 'miss', 100, 100, False]
  - [81.045041, 'bn1', 're2', None, 'damage', 70, 40, False]
  - [81.045041, 're2', 'bn1', None, 'damage', 70, 40, False]
  - [81.897214, 'bs1', 'rw1', None, 'kill', 100, 0, True]

### `S1/S1-1/without_cas`

Esiti di forza: {'Blue-Armor': ['disengaged'], 'Red-Line': ['held']} -> {'Blue-Armor': ['disengaged'], 'Red-Line': ['disengaged']}  **(cambiato)**
Conteggi: salvos 7->7, rounds 13->11, damage_events 13->11, destroyed_events 4->4

| Grandezza | Prima | Dopo |
|---|---|---|
| Red-Line.outcome | held | disengaged |
| Blue-Armor.destroyed | 3 | 2 |
| Red-Line.destroyed | 1 | 2 |
| Red-Line.rounds | 11 | 9 |
| first_shot | 161.925286 | 162.218606 |
| first_damage | 191.925286 | 192.218606 |
| damage_events | 13 | 11 |

Eventi di danno: 13 -> 11; primi 6 dopo:
  - [192.218606, 'Blue-Armor/mbt0', 'Red-Line/art0', 'test:artillery', 'damage', 100, 60, False]
  - [192.218606, 'Blue-Armor/mbt0', 'Red-Line/art0', 'test:artillery', 'damage', 60, 20, False]
  - [192.218606, 'Blue-Armor/mbt0', 'Red-Line/art0', 'test:artillery', 'miss', 20, 20, False]
  - [236.459761, 'Blue-Armor/mbt1', 'Red-Line/art0', 'test:artillery', 'damage', 100, 60, False]
  - [236.459761, 'Blue-Armor/mbt1', 'Red-Line/art0', 'test:artillery', 'miss', 60, 60, False]
  - [236.459761, 'Blue-Armor/mbt1', 'Red-Line/art0', 'test:artillery', 'miss', 60, 60, False]

### `S6/S6-0`

Esiti di forza: {'Blue-AirWing': ['destroyed'], 'Blue-CSG': ['held'], 'Red-Coast': ['disengaged'], 'Red-Flotilla': ['held', 'disengaged']} -> {'Blue-AirWing': ['destroyed'], 'Blue-CSG': ['held'], 'Red-Coast': ['disengaged'], 'Red-Flotilla': ['held', 'destroyed']}  **(cambiato)**
Conteggi: salvos 53->57, rounds 95->99, damage_events 9->11, destroyed_events 6->6, interceptions 80->82

| Grandezza | Prima | Dopo |
|---|---|---|
| Red-Flotilla.outcome | held/disengaged | held/destroyed |
| Red-Flotilla.mission_outcome | disengaged@6006.1 lost=1 | destroyed@6640.9 lost=2 |
| Blue-AirWing.rounds | 2 | 5 |
| Red-Coast.rounds | 4 | 2 |
| Red-Coast.interceptions | 0 | 2 |
| Red-Flotilla.rounds | 5 | 8 |
| first_shot | 107.485103 | 169.825187 |
| first_damage | 122.485103 | 184.825187 |
| damage_events | 9 | 11 |

Eventi di danno: 9 -> 11; primi 6 dopo:
  - [184.825187, 'Blue-AirWing/fa3', 'Red-Coast/sam0', 'test:sam', 'kill', 100, 0, True]
  - [196.16841, 'Red-Coast/ifv0', 'Blue-AirWing/fa1', 'test:agm', 'miss', 100, 100, False]
  - [211.16841, 'Red-Coast/ifv0', 'Blue-AirWing/fa1', 'test:agm', 'damage', 100, 40, False]
  - [211.16841, 'Red-Coast/ifv2', 'Blue-AirWing/fa2', 'test:agm', 'kill', 100, 0, True]
  - [227.501678, 'Blue-AirWing/fa0', 'Red-Flotilla/fsg0', 'test:sam', 'kill', 100, 0, True]
  - [251.501678, 'Blue-AirWing/fa1', 'Red-Flotilla/fsg0', 'test:sam', 'kill', 100, 0, True]

### `S7/S7-3`

Esiti di forza: {'Blue-Interdiction': ['disengaged', 'held'], 'Red-Depot': ['destroyed'], 'Red-Escort': ['destroyed']} -> {'Blue-Interdiction': ['disengaged', 'held', 'held', 'held'], 'Red-Depot': ['destroyed'], 'Red-Escort': ['disengaged', 'held']}  **(cambiato)**
Conteggi: salvos 13->13, damage_events 12->11, destroyed_events 5->4, engagements 1->2

| Grandezza | Prima | Dopo |
|---|---|---|
| Blue-Interdiction.outcome | disengaged/held | disengaged/held/held/held |
| Red-Escort.outcome | destroyed | disengaged/held |
| Blue-Interdiction:Escort.mission_outcome | disengaged@200.6 lost=1 | held lost=0 |
| Red-Escort:CAP.mission_outcome | - | held lost=0 |
| Blue-Interdiction.fuel_used | 0.5784 | 0.5839 |
| Blue-Interdiction.movement_end | 630.0 | 684.8 |
| Red-Depot.destroyed | 3 | 2 |
| Red-Escort.fuel_used | 0.3453 | 0.4105 |
| Red-Escort.movement_end | 352.2 | 684.8 |
| first_shot | 144.054613 | 144.064152 |
| first_damage | 164.054613 | 164.064152 |
| damage_events | 12 | 11 |

Eventi di danno: 12 -> 11; primi 6 dopo:
  - [164.064152, 'Red-Escort/cap0', 'Blue-Interdiction/esc0', 'test:aam', 'miss', 100, 100, False]
  - [167.973353, 'Red-Escort/cap1', 'Blue-Interdiction/esc1', 'test:aam', 'miss', 100, 100, False]
  - [179.064152, 'Red-Escort/cap0', 'Blue-Interdiction/esc0', 'test:aam', 'miss', 100, 100, False]
  - [182.973353, 'Red-Escort/cap1', 'Blue-Interdiction/esc1', 'test:aam', 'miss', 100, 100, False]
  - [200.649756, 'Red-Escort/cap0', 'Blue-Interdiction/esc1', 'test:aam', 'kill', 100, 0, True]
  - [206.594138, 'Blue-Interdiction/esc0', 'Red-Escort/cap1', 'test:aam', 'kill', 100, 0, True]

### `S8/S8-scale`

Esiti di forza: {'Blue-F0-B0': ['disengaged'], 'Blue-F0-B1': ['disengaged'], 'Blue-F0-B2': ['held'], 'Blue-F0-B3': ['held'], 'Blue-F1-B0': ['disengaged'], 'Blue-F1-B1': ['disengaged'], 'Blue-F1-B2': ['held'], 'Blue-F1-B3': ['disengaged'], 'Blue-F2-B0': ['held'], 'Blue-F2-B1': ['disengaged'], 'Blue-F2-B2': ['disengaged'], 'Blue-F2-B3': ['disengaged'], 'Blue-F3-B0': ['disengaged'], 'Blue-F3-B1': ['disengaged'], 'Blue-F3-B2': ['disengaged'], 'Blue-F3-B3': ['disengaged'], 'Blue-F4-B0': ['disengaged'], 'Blue-F4-B1': ['disengaged'], 'Blue-F4-B2': ['disengaged'], 'Blue-F4-B3': ['held'], 'Red-F0-B0': ['disengaged'], 'Red-F0-B1': ['disengaged'], 'Red-F0-B2': ['disengaged'], 'Red-F0-B3': ['disengaged'], 'Red-F1-B0': ['disengaged'], 'Red-F1-B1': ['disengaged'], 'Red-F1-B2': ['disengaged'], 'Red-F1-B3': ['disengaged'], 'Red-F2-B0': ['destroyed'], 'Red-F2-B1': ['disengaged'], 'Red-F2-B2': ['disengaged'], 'Red-F2-B3': ['disengaged'], 'Red-F3-B0': ['held'], 'Red-F3-B1': ['disengaged'], 'Red-F3-B2': ['disengaged'], 'Red-F3-B3': ['disengaged'], 'Red-F4-B0': ['disengaged'], 'Red-F4-B1': ['held'], 'Red-F4-B2': ['held'], 'Red-F4-B3': ['disengaged']} -> {'Blue-F0-B0': ['disengaged'], 'Blue-F0-B1': ['disengaged'], 'Blue-F0-B2': ['held'], 'Blue-F0-B3': ['held'], 'Blue-F1-B0': ['disengaged'], 'Blue-F1-B1': ['disengaged'], 'Blue-F1-B2': ['held'], 'Blue-F1-B3': ['held'], 'Blue-F2-B0': ['held'], 'Blue-F2-B1': ['disengaged'], 'Blue-F2-B2': ['disengaged'], 'Blue-F2-B3': ['disengaged'], 'Blue-F3-B0': ['disengaged'], 'Blue-F3-B1': ['disengaged'], 'Blue-F3-B2': ['disengaged'], 'Blue-F3-B3': ['disengaged'], 'Blue-F4-B0': ['disengaged'], 'Blue-F4-B1': ['disengaged'], 'Blue-F4-B2': ['disengaged'], 'Blue-F4-B3': ['held'], 'Red-F0-B0': ['disengaged'], 'Red-F0-B1': ['held'], 'Red-F0-B2': ['disengaged'], 'Red-F0-B3': ['disengaged'], 'Red-F1-B0': ['disengaged'], 'Red-F1-B1': ['disengaged'], 'Red-F1-B2': ['disengaged'], 'Red-F1-B3': ['disengaged'], 'Red-F2-B0': ['disengaged'], 'Red-F2-B1': ['disengaged'], 'Red-F2-B2': ['disengaged'], 'Red-F2-B3': ['disengaged'], 'Red-F3-B0': ['held'], 'Red-F3-B1': ['disengaged'], 'Red-F3-B2': ['disengaged'], 'Red-F3-B3': ['disengaged'], 'Red-F4-B0': ['disengaged'], 'Red-F4-B1': ['disengaged'], 'Red-F4-B2': ['held'], 'Red-F4-B3': ['disengaged']}  **(cambiato)**
Conteggi: salvos 240->235, rounds 240->235, damage_events 236->227, destroyed_events 63->65

| Grandezza | Prima | Dopo |
|---|---|---|
| Blue-F1-B3.outcome | disengaged | held |
| Red-F0-B1.outcome | disengaged | held |
| Red-F2-B0.outcome | destroyed | disengaged |
| Red-F4-B1.outcome | held | disengaged |
| Blue-F0-B0.destroyed | 1 | 0 |
| Blue-F0-B3.rounds | 6 | 5 |
| Blue-F1-B2.rounds | 6 | 5 |
| Blue-F2-B1.destroyed | 2 | 1 |
| Blue-F3-B3.destroyed | 3 | 4 |
| Blue-F4-B2.destroyed | 2 | 3 |
| Red-F0-B0.destroyed | 1 | 2 |
| Red-F0-B0.rounds | 6 | 5 |
| Red-F0-B1.rounds | 6 | 5 |
| Red-F1-B3.destroyed | 2 | 1 |
| Red-F2-B0.destroyed | 6 | 5 |
| Red-F2-B1.destroyed | 0 | 2 |
| Red-F2-B3.destroyed | 1 | 2 |
| Red-F3-B0.destroyed | 0 | 1 |
| Red-F3-B2.destroyed | 4 | 3 |
| Red-F4-B1.rounds | 6 | 5 |
| damage_events | 236 | 227 |

Eventi di danno: 236 -> 227; primi 6 dopo:
  - [32.5, 'Blue-F0-B0/mbt0', 'Red-F0-B0/mbt1', 'test:direct_fire', 'miss', 100, 100, False]
  - [32.5, 'Blue-F0-B0/mbt3', 'Red-F0-B0/mbt2', 'test:direct_fire', 'damage', 100, 50, False]
  - [32.5, 'Blue-F0-B0/mbt2', 'Red-F0-B0/mbt3', 'test:direct_fire', 'miss', 100, 100, False]
  - [32.5, 'Blue-F0-B0/mbt1', 'Red-F0-B0/mbt4', 'test:direct_fire', 'damage', 100, 50, False]
  - [32.5, 'Blue-F0-B0/mbt4', 'Red-F0-B0/mbt5', 'test:direct_fire', 'damage', 100, 50, False]
  - [32.5, 'Red-F0-B0/mbt0', 'Blue-F0-B0/mbt0', 'test:direct_fire', 'kill', 100, 0, True]

### `S13/S13-2`

Esiti di forza: {'Blue-Strike': ['disengaged', 'held'], 'Red-FARP': ['held', 'held']} -> {'Blue-Strike': ['disengaged', 'disengaged'], 'Red-FARP': ['held', 'held']}  **(cambiato)**
Conteggi: salvos 16->14, rounds 26->20, damage_events 15->17, destroyed_events 4->5

| Grandezza | Prima | Dopo |
|---|---|---|
| Blue-Strike.outcome | disengaged/held | disengaged/disengaged |
| Blue-Strike:Strike.mission_outcome | held lost=0 | disengaged@554.1 lost=1 |
| Blue-Strike.destroyed | 1 | 2 |
| Blue-Strike.rounds | 20 | 12 |
| Blue-Strike.fuel_used | 1.053 | 1.0715 |
| Blue-Strike.movement_end | 1017.8 | 1054.0 |
| Red-FARP.rounds | 6 | 8 |
| damage_events | 15 | 17 |

Eventi di danno: 15 -> 17; primi 6 dopo:
  - [233.245542, 'Red-FARP/fuel0', 'Blue-Strike/str1', 'test:bomb', 'miss', 100, 100, False]
  - [233.245542, 'Red-FARP/fuel0', 'Blue-Strike/str1', 'test:bomb', 'kill', 100, 0, True]
  - [233.649646, 'Red-FARP/sup0', 'Blue-Strike/str3', 'test:bomb', 'damage', 100, 30, False]
  - [233.649646, 'Red-FARP/sup0', 'Blue-Strike/str3', 'test:bomb', 'miss', 30, 30, False]
  - [236.510752, 'Red-FARP/sup0', 'Blue-Strike/str2', 'test:bomb', 'miss', 30, 30, False]
  - [236.510752, 'Red-FARP/sup0', 'Blue-Strike/str2', 'test:bomb', 'miss', 30, 30, False]

### `S14/S14-4`

Esiti di forza: {'Blue-Bombers': ['disengaged', 'held'], 'Red-Plant': ['held', 'held']} -> {'Blue-Bombers': ['disengaged', 'disengaged'], 'Red-Plant': ['held', 'held']}  **(cambiato)**
Conteggi: salvos 14->18, rounds 14->18, damage_events 14->18, destroyed_events 3->5

| Grandezza | Prima | Dopo |
|---|---|---|
| Blue-Bombers.outcome | disengaged/held | disengaged/disengaged |
| Blue-Bombers:Strike.mission_outcome | held lost=0 | disengaged@712.0 lost=1 |
| Blue-Bombers.destroyed | 1 | 3 |
| Blue-Bombers.fuel_used | 1.1507 | 1.0774 |
| Blue-Bombers.movement_end | 1357.9 | 1379.7 |
| Red-Plant.rounds | 6 | 10 |
| first_shot | 368.792467 | 369.550163 |
| first_damage | 378.792467 | 379.550163 |
| damage_events | 14 | 18 |

Eventi di danno: 14 -> 18; primi 6 dopo:
  - [379.550163, 'Red-Plant/hall0', 'Blue-Bombers/bmb3', 'test:agm', 'miss', 100, 100, False]
  - [382.858766, 'Red-Plant/hall0', 'Blue-Bombers/bmb2', 'test:agm', 'damage', 100, 40, False]
  - [383.412652, 'Red-Plant/tank0', 'Blue-Bombers/bmb1', 'test:agm', 'miss', 100, 100, False]
  - [390.594837, 'Red-Plant/tank1', 'Blue-Bombers/bmb0', 'test:agm', 'miss', 100, 100, False]
  - [398.412652, 'Red-Plant/tank0', 'Blue-Bombers/bmb1', 'test:agm', 'miss', 100, 100, False]
  - [405.594837, 'Red-Plant/tank1', 'Blue-Bombers/bmb0', 'test:agm', 'kill', 100, 0, True]

### `S11/S11-c-dcs`

Esiti di forza: {'Blue-Mech': ['disengaged'], 'Red-Battalion': ['disengaged']} -> {'Blue-CAS': ['destroyed'], 'Blue-Mech': ['held'], 'Red-Battalion': ['disengaged'], 'Red-CAP': ['held']}  **(cambiato)**
Conteggi: salvos 15->7, rounds 15->7, damage_events 15->4, destroyed_events 2->2

| Grandezza | Prima | Dopo |
|---|---|---|
| Blue-CAS.outcome | - | destroyed |
| Blue-Mech.outcome | disengaged | held |
| Red-CAP.outcome | - | held |
| Blue-CAS.rounds | 0 | 3 |
| Blue-CAS.fuel_used | 0.0814 | 0.1329 |
| Blue-Mech.destroyed | 1 | 0 |
| Blue-Mech.rounds | 7 | 0 |
| Red-Battalion.rounds | 8 | 0 |
| Red-CAP.rounds | 0 | 4 |
| Red-CAP.fuel_used | 0.1074 | 0.3146 |
| first_shot | 3892.873718 | 3601.5 |
| first_damage | 3894.373718 | 3611.5 |
| damage_events | 15 | 4 |

Eventi di danno: 15 -> 4; primi 6 dopo:
  - [3611.5, 'Red-Battalion/mbt0', 'Blue-CAS/cas1', 'test:agm', 'damage', 100, 40, False]
  - [3641.5, 'Red-Battalion/mbt1', 'Blue-CAS/cas1', 'test:agm', 'miss', 100, 100, False]
  - [3656.5, 'Red-Battalion/mbt1', 'Blue-CAS/cas1', 'test:agm', 'kill', 100, 0, True]
  - [3718.508705, 'Blue-CAS/cas1', 'Red-CAP/cap0', 'test:aam', 'kill', 100, 0, True]

### `S2/S2-2/baseline`

Esiti di forza: {'Blue-Strike': ['disengaged', 'disengaged'], 'Red-SAM': ['held', 'held'], 'Red-Target': ['disengaged', 'held']} -> {'Blue-Strike': ['disengaged', 'destroyed'], 'Red-SAM': ['held', 'held'], 'Red-Target': ['disengaged', 'held']}  **(cambiato)**
Conteggi: salvos 10->12, rounds 10->12, damage_events 9->7, destroyed_events 5->6

| Grandezza | Prima | Dopo |
|---|---|---|
| Blue-Strike.outcome | disengaged/disengaged | disengaged/destroyed |
| Blue-Strike:Strike.mission_outcome | disengaged@340.5 lost=1 | destroyed@354.4 lost=2 |
| Blue-Strike.destroyed | 2 | 4 |
| Blue-Strike.fuel_used | 0.8454 | 0.9401 |
| Red-SAM.rounds | 6 | 8 |
| Red-Target.destroyed | 3 | 2 |
| damage_events | 9 | 7 |

Eventi di danno: 9 -> 7; primi 6 dopo:
  - [229.493961, 'Red-Target/tgt2', 'Blue-Strike/str1', 'test:agm', 'damage', 100, 40, False]
  - [229.495542, 'Red-Target/tgt1', 'Blue-Strike/str0', 'test:agm', 'kill', 100, 0, True]
  - [229.496926, 'Red-Target/tgt2', 'Blue-Strike/str2', 'test:agm', 'kill', 40, 0, True]
  - [298.541763, 'Blue-Strike/str0', 'Red-SAM/sam0', 'test:sam', 'kill', 100, 0, True]
  - [300.341347, 'Blue-Strike/str3', 'Red-SAM/sam1', 'test:sam', 'kill', 100, 0, True]
  - [354.442347, 'Blue-Strike/str1', 'Red-SAM/sam0', 'test:sam', 'kill', 100, 0, True]

### `S3/S3-0/stealth`

Esiti di forza: {'Blue-Stealth': ['disengaged', 'held'], 'Red-Mass': ['disengaged', 'held']} -> {'Blue-Stealth': ['held', 'held'], 'Red-Mass': ['disengaged', 'disengaged']}  **(cambiato)**
Conteggi: salvos 14->19, rounds 14->19, damage_events 11->14, destroyed_events 6->6

| Grandezza | Prima | Dopo |
|---|---|---|
| Blue-Stealth.outcome | disengaged/held | held/held |
| Red-Mass.outcome | disengaged/held | disengaged/disengaged |
| Red-Mass:Fighter_Sweep.mission_outcome | held lost=0 | disengaged@233.4 lost=1 |
| Blue-Stealth.destroyed | 2 | 1 |
| Blue-Stealth.rounds | 8 | 14 |
| Blue-Stealth.fuel_used | 0.6337 | 0.9544 |
| Red-Mass.destroyed | 4 | 5 |
| Red-Mass.rounds | 6 | 5 |
| Red-Mass.fuel_used | 1.1036 | 1.3538 |
| first_shot | 172.928571 | 172.937143 |
| first_damage | 192.928571 | 192.937143 |
| damage_events | 11 | 14 |

Eventi di danno: 11 -> 14; primi 6 dopo:
  - [192.937143, 'Red-Mass/f1', 'Blue-Stealth/f0', 'test:aam', 'miss', 100, 100, False]
  - [192.937143, 'Red-Mass/f2', 'Blue-Stealth/f3', 'test:aam', 'kill', 100, 0, True]
  - [192.962861, 'Red-Mass/f0', 'Blue-Stealth/f2', 'test:aam', 'kill', 100, 0, True]
  - [193.005732, 'Blue-Stealth/f3', 'Red-Mass/f6', 'test:aam', 'miss', 100, 100, False]
  - [193.237421, 'Red-Mass/f7', 'Blue-Stealth/f1', 'test:aam', 'kill', 100, 0, True]
  - [196.908892, 'Blue-Stealth/f0', 'Red-Mass/f2', 'test:aam', 'miss', 100, 100, False]

### `S4/S4-2/with_sam`

Esiti di forza: {'Blue-Armor': ['disengaged'], 'Blue-CAS': ['disengaged', 'destroyed'], 'Red-Armor': ['disengaged', 'held'], 'Red-SAM': ['held', 'held']} -> {'Blue-Armor': ['disengaged'], 'Blue-CAS': ['disengaged', 'destroyed'], 'Red-Armor': ['held', 'held'], 'Red-SAM': ['held', 'held']}  **(cambiato)**
Conteggi: salvos 15->10, rounds 15->10, damage_events 13->9, destroyed_events 3->2

| Grandezza | Prima | Dopo |
|---|---|---|
| Red-Armor.outcome | disengaged/held | held/held |
| Blue-CAS:CAS.mission_outcome | destroyed@599.0 lost=1 | destroyed@598.2 lost=1 |
| Blue-Armor.rounds | 4 | 1 |
| Blue-CAS.fuel_used | 0.3279 | 0.3278 |
| Blue-CAS.movement_end | 1113.7 | 1112.3 |
| Red-Armor.destroyed | 1 | 0 |
| Red-Armor.rounds | 3 | 2 |
| Red-SAM.rounds | 8 | 7 |
| damage_events | 13 | 9 |

Eventi di danno: 13 -> 9; primi 6 dopo:
  - [42.101, 'Blue-CAS/cas0', 'Red-SAM/sam0', 'test:sam', 'miss', 100, 100, False]
  - [54.101, 'Blue-CAS/cas1', 'Red-SAM/sam0', 'test:sam', 'miss', 100, 100, False]
  - [66.101, 'Blue-CAS/cas1', 'Red-SAM/sam0', 'test:sam', 'kill', 100, 0, True]
  - [76.90565, 'Blue-CAS/cas0', 'Red-SAM/sam1', 'test:sam', 'miss', 100, 100, False]
  - [78.101, 'Blue-CAS/cas0', 'Red-SAM/sam0', 'test:sam', 'miss', 100, 100, False]
  - [556.136364, 'Blue-Armor/mbt1', 'Red-Armor/mbt1', 'test:direct_fire', 'damage', 100, 50, False]

### `S20/S20-1/split`

Esiti di forza: {'Blue-Armor': ['held', 'held'], 'Red-Line': ['disengaged']} -> {'Blue-Armor': ['disengaged', 'disengaged'], 'Red-Line': ['held']}  **(cambiato)**
Conteggi: salvos 9->8, rounds 17->14, damage_events 15->14, destroyed_events 2->1

| Grandezza | Prima | Dopo |
|---|---|---|
| Blue-Armor.outcome | held/held | disengaged/disengaged |
| Red-Line.outcome | disengaged | held |
| Blue-Armor:IFV.mission_outcome | held lost=0 | disengaged@310.2 lost=1 |
| Blue-Armor:Tanks.mission_outcome | held lost=1 | disengaged@296.9 lost=2 |
| Blue-Armor.rounds | 3 | 2 |
| Red-Line.destroyed | 1 | 0 |
| Red-Line.rounds | 14 | 12 |
| first_shot | 162.12306 | 186.878427 |
| first_damage | 192.12306 | 216.878427 |
| damage_events | 15 | 14 |

Eventi di danno: 15 -> 14; primi 6 dopo:
  - [216.878427, 'Blue-Armor/mbt0', 'Red-Line/art0', 'test:artillery', 'miss', 100, 100, False]
  - [216.878427, 'Blue-Armor/mbt0', 'Red-Line/art0', 'test:artillery', 'miss', 100, 100, False]
  - [216.878427, 'Blue-Armor/mbt0', 'Red-Line/art0', 'test:artillery', 'miss', 100, 100, False]
  - [256.878427, 'Blue-Armor/mbt2', 'Red-Line/art0', 'test:artillery', 'miss', 100, 100, False]
  - [256.878427, 'Blue-Armor/mbt2', 'Red-Line/art0', 'test:artillery', 'miss', 100, 100, False]
  - [256.878427, 'Blue-Armor/mbt2', 'Red-Line/art0', 'test:artillery', 'miss', 100, 100, False]

### `S22-E1/S22-E1-0/static`

Esiti di forza: {'Blue-Armor': ['destroyed'], 'Red-Post': ['held']} -> {'Blue-Armor': ['held'], 'Red-Post': ['held']}  **(cambiato)**
Conteggi: salvos 1->0, rounds 1->0, damage_events 1->0, destroyed_events 0->0

| Grandezza | Prima | Dopo |
|---|---|---|
| Blue-Armor.outcome | destroyed | held |
| Red-Post.rounds | 1 | 0 |
| first_shot | 31.0 | - |
| first_damage | 32.5 | - |
| damage_events | 1 | 0 |

Eventi di danno: 1 -> 0; primi 6 dopo:

### `S9R/S9R-3/unseen`

Esiti di forza: {'Blue-Armor': ['held'], 'Blue-CAS': ['held'], 'Red-Line': ['disengaged']} -> {'Blue-Armor': ['held'], 'Blue-CAS': ['disengaged', 'held'], 'Red-Line': ['disengaged', 'held']}  **(cambiato)**
Conteggi: salvos 3->12, rounds 3->18, damage_events 3->17, destroyed_events 1->4, engagements 1->2

| Grandezza | Prima | Dopo |
|---|---|---|
| Blue-CAS.outcome | held | disengaged/held |
| Red-Line.outcome | disengaged | disengaged/held |
| Blue-CAS:CAS.mission_outcome | - | held lost=0 |
| Red-Line.mission_outcome | - | held lost=0 |
| Blue-Armor.destroyed | 0 | 2 |
| Blue-Armor.rounds | 0 | 1 |
| Blue-CAS.fuel_used | 0.1329 | 0.1744 |
| Blue-CAS.movement_end | 450.0 | 679.6 |
| Red-Line.destroyed | 1 | 2 |
| Red-Line.rounds | 0 | 14 |
| damage_events | 3 | 17 |

Eventi di danno: 3 -> 17; primi 6 dopo:
  - [11.5, 'Red-Line/ifv0', 'Blue-CAS/cas0', 'test:agm', 'miss', 100, 100, False]
  - [26.5, 'Red-Line/ifv0', 'Blue-CAS/cas0', 'test:agm', 'damage', 100, 40, False]
  - [56.5, 'Red-Line/ifv2', 'Blue-CAS/cas0', 'test:agm', 'kill', 100, 0, True]
  - [191.925286, 'Blue-Armor/mbt1', 'Red-Line/art0', 'test:artillery', 'miss', 100, 100, False]
  - [191.925286, 'Blue-Armor/mbt1', 'Red-Line/art0', 'test:artillery', 'miss', 100, 100, False]
  - [191.925286, 'Blue-Armor/mbt1', 'Red-Line/art0', 'test:artillery', 'kill', 100, 0, True]

### `S12/S12-0/prolonged`

Esiti di forza: {'Blue-Armor': ['held'], 'Blue-CAS': ['destroyed'], 'Red-Line': ['destroyed']} -> {'Blue-Armor': ['held'], 'Blue-CAS': ['destroyed'], 'Red-Line': ['destroyed']}  (invariato)
Conteggi: salvos 13->13, destroyed_events 6->6

| Grandezza | Prima | Dopo |
|---|---|---|

Eventi di danno: 13 -> 13; primi 6 dopo:
  - [11.5, 'Red-Line/art0', 'Blue-CAS/cas0', 'test:agm', 'kill', 100, 0, True]
  - [11.5, 'Red-Line/ifv0', 'Blue-CAS/cas1', 'test:agm', 'miss', 100, 100, False]
  - [26.5, 'Red-Line/ifv0', 'Blue-CAS/cas1', 'test:agm', 'kill', 100, 0, True]
  - [41.5, 'Red-Line/ifv2', 'Blue-CAS/cas0', 'test:agm', 'kill', 100, 0, True]
  - [56.5, 'Red-Line/ifv1', 'Blue-CAS/cas1', 'test:agm', 'damage', 100, 40, False]
  - [274.384051, 'Blue-CAS/cas1', 'Red-Line/aaa0', 'test:aaa', 'miss', 100, 100, False]

### `S15/S15-0/control`

Esiti di forza: {'Blue-Strike': ['held'], 'Red-Stronghold': ['destroyed'], 'Red-Town': ['destroyed']} -> {'Blue-Strike': ['held'], 'Red-Stronghold': ['destroyed'], 'Red-Town': ['destroyed']}  (invariato)
Conteggi: salvos 13->11, rounds 13->11, damage_events 12->11, destroyed_events 7->6

| Grandezza | Prima | Dopo |
|---|---|---|
| Blue-Strike.rounds | 13 | 11 |
| Red-Stronghold.destroyed | 3 | 4 |
| Red-Town.destroyed | 4 | 2 |
| damage_events | 12 | 11 |

Eventi di danno: 12 -> 11; primi 6 dopo:
  - [217.129881, 'Red-Stronghold/aaa0', 'Blue-Strike/str2', 'test:agm', 'kill', 100, 0, True]
  - [218.243763, 'Red-Stronghold/ifv0', 'Blue-Strike/str0', 'test:agm', 'kill', 100, 0, True]
  - [218.244998, 'Red-Stronghold/ifv1', 'Blue-Strike/str1', 'test:agm', 'miss', 100, 100, False]
  - [223.899646, 'Red-Town/bld0', 'Blue-Strike/str3', 'test:agm', 'miss', 100, 100, False]
  - [233.244998, 'Red-Stronghold/ifv1', 'Blue-Strike/str1', 'test:agm', 'miss', 100, 100, False]
  - [238.899646, 'Red-Town/bld0', 'Blue-Strike/str3', 'test:agm', 'damage', 100, 40, False]

### `S16/S16-0`

Esiti di forza: {'Blue-Naval-Strike': ['held'], 'Red-Port': ['destroyed']} -> {'Blue-Naval-Strike': ['held'], 'Red-Port': ['destroyed']}  (invariato)
Conteggi: salvos 38->42, rounds 44->50, damage_events 22->24, destroyed_events 14->16, interceptions 6->11

| Grandezza | Prima | Dopo |
|---|---|---|
| Blue-Naval-Strike.destroyed | 9 | 11 |
| Blue-Naval-Strike.rounds | 23 | 28 |
| Red-Port.rounds | 21 | 22 |
| Red-Port.interceptions | 6 | 11 |
| first_shot | 109.99826 | 110.420452 |
| first_damage | 154.99826 | 155.420452 |
| damage_events | 22 | 24 |

Eventi di danno: 22 -> 24; primi 6 dopo:
  - [155.420452, 'Blue-Naval-Strike/fa8', 'Red-Port/fsg0', 'test:sam', 'kill', 100, 0, True]
  - [155.420452, 'Blue-Naval-Strike/fa13', 'Red-Port/fsg1', 'test:sam', 'miss', 100, 100, False]
  - [155.420452, 'Blue-Naval-Strike/fa13', 'Red-Port/fsg1', 'test:sam', 'kill', 100, 0, True]
  - [155.420452, 'Blue-Naval-Strike/fa15', 'Red-Port/fsg0', 'test:sam', 'kill', 100, 0, True]
  - [185.687151, 'Blue-Naval-Strike/fa7', 'Red-Port/fsg1', 'test:sam', 'miss', 100, 100, False]
  - [185.687151, 'Blue-Naval-Strike/fa7', 'Red-Port/fsg1', 'test:sam', 'kill', 100, 0, True]

### `S23-CAP/S23-CAP-0/during`

Esiti di forza: {'Blue-Bomber': ['destroyed'], 'Red-CAP': ['held']} -> {'Blue-Bomber': ['destroyed'], 'Red-CAP': ['held']}  (invariato)
Conteggi: salvos 3->3, destroyed_events 2->2

| Grandezza | Prima | Dopo |
|---|---|---|
| first_shot | 881.566685 | 884.845593 |
| first_damage | 901.566685 | 904.845593 |

Eventi di danno: 2 -> 2; primi 6 dopo:
  - [904.845593, 'Blue-Bomber/bmb1', 'Red-CAP/cap0', 'test:aam', 'kill', 100, 0, True]
  - [923.41754, 'Blue-Bomber/bmb0', 'Red-CAP/cap1', 'test:aam', 'kill', 100, 0, True]

### `S5/S5-0/press_on`

Esiti di forza: {'Blue-Deep': ['held', 'destroyed'], 'Red-L1-Long': ['held'], 'Red-L2-Medium': ['held'], 'Red-L3-Point': ['held'], 'Red-Target': ['held']} -> {'Blue-Deep': ['held', 'destroyed'], 'Red-L1-Long': ['held'], 'Red-L2-Medium': ['held'], 'Red-L3-Point': ['held'], 'Red-Target': ['held']}  (invariato)
Conteggi: salvos 8->8, destroyed_events 4->4

| Grandezza | Prima | Dopo |
|---|---|---|
| Blue-Deep:Strike.mission_outcome | destroyed@2328.2 lost=2 | destroyed@2363.1 lost=2 |

Eventi di danno: 5 -> 5; primi 6 dopo:
  - [598.903267, 'Blue-Deep/str2', 'Red-L1-Long/sam0', 'test:sam', 'kill', 100, 0, True]
  - [622.903267, 'Blue-Deep/str0', 'Red-L1-Long/sam0', 'test:sam', 'miss', 100, 100, False]
  - [634.903267, 'Blue-Deep/str0', 'Red-L1-Long/sam0', 'test:sam', 'kill', 100, 0, True]
  - [2339.124892, 'Blue-Deep/str1', 'Red-L2-Medium/sam0', 'test:sam', 'kill', 100, 0, True]
  - [2363.124892, 'Blue-Deep/str3', 'Red-L2-Medium/sam0', 'test:sam', 'kill', 100, 0, True]

### `S27-DOUBLE/S27-DOUBLE-0/double`

Esiti di forza: {'Blue-Flight': ['held', 'held'], 'Red-First': ['held'], 'Red-Second': ['held']} -> {'Blue-Flight': ['held', 'held'], 'Red-First': ['held'], 'Red-Second': ['held']}  (invariato)
Conteggi: salvos 48->47, rounds 48->47, damage_events 48->47, destroyed_events 0->0

| Grandezza | Prima | Dopo |
|---|---|---|
| Blue-Flight.movement_end | 1565.4 | 1565.8 |
| Red-First.rounds | 24 | 23 |
| first_shot | 233.244039 | 251.031847 |
| first_damage | 248.244039 | 266.031847 |
| damage_events | 48 | 47 |

Eventi di danno: 48 -> 47; primi 6 dopo:
  - [266.031847, 'Blue-Flight/f0', 'Red-First/ifv0', 'test:marker', 'miss', 100, 100, False]
  - [278.031847, 'Blue-Flight/f0', 'Red-First/ifv0', 'test:marker', 'miss', 100, 100, False]
  - [290.031847, 'Blue-Flight/f0', 'Red-First/ifv0', 'test:marker', 'miss', 100, 100, False]
  - [302.031847, 'Blue-Flight/f0', 'Red-First/ifv0', 'test:marker', 'miss', 100, 100, False]
  - [314.031847, 'Blue-Flight/f0', 'Red-First/ifv0', 'test:marker', 'miss', 100, 100, False]
  - [326.031847, 'Blue-Flight/f0', 'Red-First/ifv0', 'test:marker', 'miss', 100, 100, False]
