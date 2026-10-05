# Struttura del file `.miz` — schema dei dati di missione DCS

Analisi empirica di una missione reale generata da DCE (Dynamic Campaign Engine, campagna
"1975 Georgian War", prima missione, `sortie = "1975 Georgian War - 1"`), file
`Analysis/Document/documentazione missioni dcs/1975 Georgian War_first.miz` (6,7 MB zippato).
Tutti i numeri di questo documento sono stati misurati caricando le tabelle Lua con `lupa`
(Lua 5.4 in Python) e percorrendole con script di analisi; **non** sono letti dalla
documentazione. Dove una informazione viene da conoscenza generale di DCS e non dal file, lo
dico esplicitamente ("non verificato nel file").

Scopo: sapere quali informazioni Warfare-Model deve produrre per generare un `.miz`, quali sono
"stato del mondo" e quali si possono lasciare di default.

Collegamenti con la documentazione già esistente (non ripetuta qui):
- `Analysis/Document/documentazione_dcs/ANALISI_DCE.md` — §4 (formato `.miz`), §3 (stato di
  campagna `camp`/`oob_air`/`targetlist`), A.4/A.5 (warehouse e weather, riferimento da pydcs).
- `Analysis/Document/documentazione_dcs/COMPRENSIONE_PERSISTENZA_DCS.md` — persistenza e
  modello temporale di DCS.

Convenzione di notazione: le chiavi sono scritte come nel file Lua (`['chiave'] = valore`);
`[]` indica una tabella indicizzata da interi 1..N (array Lua); `n=` è il numero di occorrenze.

---

## 0. Correzioni rispetto a quanto già scritto in `ANALISI_DCE.md`

Il confronto con questo file reale smentisce o precisa quattro punti di `ANALISI_DCE.md` §4:

| Punto | `ANALISI_DCE.md` | Questo file |
|---|---|---|
| `mission.version` | 22 (template) / 23 (test mission) | **19** (la `.miz` è stata prodotta a partire da un template/Mission Editor più vecchio, "compatible with 2.7.0" nei commenti degli script) |
| entry `theatre` nello zip | presente, testo semplice `Caucasus` | **assente**: il teatro è solo la chiave `mission['theatre'] = 'Caucasus'` |
| uso del dizionario `DictKey_*` | "nomi di gruppo/unità quasi sempre chiavi" | in questa `.miz` i nomi sono **stringhe in chiaro** dentro `mission`; l'unico riferimento `DictKey_` rimasto in `mission` è `descriptionRedTask`. Il `dictionary` contiene 1183 voci (587 `UnitName`, 367 `WptName`, 225 `GroupName`, 4 descrizioni) ma sono residui dell'editor: non sono necessarie per far girare la missione |
| inventario warehouse | possibile `aircrafts`/`weapons` per tipo | in questa `.miz` **tutte** le tabelle `aircrafts`/`weapons` sono vuote e tutto è `unlimited*=true` (v. §5.1): DCE tiene l'inventario fuori da DCS (`camp.aircraft_availability`) |

---

## 1. Contenuto dell'archivio

Zip di 20 entry (6.706.921 byte decompressi):

| Entry | Byte | Natura | Contenuto |
|---|---:|---|---|
| `mission` | 3.641.302 | Lua eseguibile, globale `mission = {...}` | tutta la missione (v. §2-§6) |
| `options` | 11.458 | Lua, globale `options` | opzioni di difficoltà/giocatore/plugin (v. §5.2) |
| `warehouses` | 35.552 | Lua, globale `warehouses` | magazzini di 21 aeroporti + 36 FARP/navi (v. §5.1) |
| `l10n/DEFAULT/dictionary` | 50.552 | Lua, globale `dictionary` | mappa `DictKey_*` → stringa (1183 voci, in gran parte inutilizzate) |
| `l10n/DEFAULT/mapResource` | 686 | Lua, globale `mapResource` | mappa `ResKey_*` → nome file (12 voci: 9 script + 3 immagini di briefing) |
| `l10n/DEFAULT/EventsTracker.lua` | 19.967 | script DCE | cattura eventi → debrief (v. §7) |
| `l10n/DEFAULT/GCIdata.lua` | 3.794 | dati DCE | tabella `GCI` (EWR e intercettori pronti) |
| `l10n/DEFAULT/GCIscript.lua` | 21.362 | script DCE | GCI: EWR rileva, lancia intercettori |
| `l10n/DEFAULT/ARM_Defence_Script.lua` | 3.505 | script DCE | radar si spengono se rilevano un missile anti-radiazione |
| `l10n/DEFAULT/CustomTasksScript.lua` | 43.792 | script DCE | funzioni di attacco AI custom chiamate dai waypoint |
| `l10n/DEFAULT/CarrierIntoWindScript.lua` | 17.090 | script DCE | portaerei in prua al vento |
| `l10n/DEFAULT/AddCommandRadioF10.lua` | 42.674 | script DCE | comandi F10 per il giocatore (RTB, rifornimento, CAP) |
| `l10n/DEFAULT/Pedro.lua` | 17.640 | script DCE | elicottero SAR "Pedro" tiene la posizione vicino alla portaerei |
| `l10n/DEFAULT/camp_status.lua` | 36.822 | dati DCE, globale `camp` | fotografia dello stato di campagna (v. §7) |
| `l10n/DEFAULT/debugGenMission.txt` | 71.692 | log di testo | traccia della generazione ATO (v. §7) |
| `l10n/DEFAULT/debugFlight.txt` | 33.741 | log di testo | una riga per ogni pack generato |
| `l10n/DEFAULT/Newspaper_FirstNight_blue.jpg`, `_red.jpg`, `FrontlineCaucasus.png` | ~140 KB, ~150 KB, ~790 KB | immagini | immagini di briefing |
| `l10n/DEFAULT/alarme.wav` | 1.574.436 | audio | suono d'allarme |

Osservazioni:
- Il `.miz` è davvero uno zip; `mission`, `options`, `warehouses`, `dictionary`, `mapResource`
  sono **sorgente Lua** che assegna una sola globale e contiene solo tabelle letterali
  (chiavi tra apici singoli `['...']`, indici `[n]`, stringhe, numeri, booleani). Nessuna
  funzione, quindi un parser Lua minimale basta.
- Il file `mission` pesa 3,6 MB perché è serializzato con tabulazioni e ha molte ripetizioni
  (ogni waypoint di ogni gruppo aereo ha `task`, `properties`, ecc.).
- Gli script DCE (§7) sono "payload": non fanno parte dello schema di missione di DCS, ma sono
  aggiunti per DCE e agganciati tramite `mapResource` + `trig` + `trigrules`.

---

## 2. Albero di primo livello di `mission`

Tutte le chiavi di `mission` (27), con tipo, valore osservato e significato:

| Chiave | Tipo | Valore / dimensione osservata | Significato |
|---|---|---|---|
| `version` | int | `19` | numero di schema del file di missione |
| `theatre` | str | `'Caucasus'` | mappa |
| `date` | tabella | `{Day=13, Month=9, Year=1975}` | data di inizio (v. §5.3) |
| `start_time` | int | `17476` | ora di inizio, **secondi dalla mezzanotte** (= 04:51:16, coerente col briefing "04:51") |
| `sortie` | str | `'1975 Georgian War - 1'` | nome missione |
| `descriptionText` | str | testo | briefing generale (in chiaro) |
| `descriptionBlueTask` | str | testo | briefing blu: contiene l'ATO "Air Tasking Order: Sorties / Mission / TOT" |
| `descriptionRedTask` | str | `'DictKey_descriptionRedTask_2'` | briefing rosso (unico riferimento `DictKey_` rimasto) |
| `descriptionNeutralsTask` | str | `''` | briefing neutrali |
| `pictureFileNameB` / `R` / `N` | array | 2 / 2 / 0 | immagini di briefing (`ResKey_BriefingImage_*`) per blu/rosso/neutrali |
| `coalition` | tabella | chiavi `blue`, `red`, `neutrals` | **tutto il contenuto della missione** (v. §3) |
| `coalitions` | tabella | `blue` (20 id), `red` (11 id), `neutrals` (54 id) | assegnazione dei 85 country id alle coalizioni (solo ids) |
| `weather` | tabella | 16 chiavi | meteo (v. §5.3) |
| `trig` | tabella | `actions`(180), `conditions`(180), `flag`(180), `func`(170), `funcStartup`(10), `custom`, `customStartup`, `events` | rappresentazione eseguibile dei trigger (v. §5.4) |
| `trigrules` | tabella | 180 voci | rappresentazione dei trigger per il Mission Editor (v. §5.4) |
| `triggers` | tabella | `{zones}` con 36 zone | trigger zones (v. §5.4) |
| `goals` | tabella | 1 voce | obiettivi / punteggio (v. §5.5) |
| `result` | tabella | `total`, `offline`, `blue`, `red` | condizioni di fine missione (v. §5.5) |
| `failures` | tabella | 268 voci, tutte `enable=false` | guasti programmati per aeromobili (v. §5.6) |
| `forcedOptions` | tabella | 13 chiavi | opzioni imposte ai giocatori (v. §5.6) |
| `groundControl` | tabella | `roles` + `isPilotControlVehicles` | ruoli Combined Arms (v. §5.6) |
| `map` | tabella | `centerX`, `centerY`, `zoom` | vista iniziale del Mission Editor (v. §5.6) |
| `requiredModules` | tabella | vuota | moduli richiesti per aprire la missione |
| `maxDictId` | int | `2166` | ultimo id usato per le chiavi di `dictionary` |
| `currentKey` | int | `999999` | contatore chiavi dell'editor (valore forzato da DCE, v. `ANALISI_DCE.md` §4.2) |

(`pictureFileNameB/R/N` sono 3 chiavi raggruppate in una riga.)

Tutto il contenuto "di gioco" sta quindi in `coalition`; il resto è contorno
(meteo, tempo, trigger, opzioni).

---

## 3. Schema coalizione → paese → categoria → gruppo → unità

### 3.1 Struttura ad albero

```
mission['coalition'][side]            side in {'blue','red','neutrals'}
    ['name']        str               = nome del lato
    ['bullseye']    {x, y}            punto di riferimento (metri)
    ['nav_points']  {}                punti di navigazione (vuoto in questa missione)
    ['country'][i]  i = 1..N          NB: indice sequenziale, NON il country id
        ['id']      int               country id DCS (es. 0 Russia, 2 USA, 16 Georgia)
        ['name']    str               'Russia', 'USA', ...
        ['plane'|'helicopter'|'vehicle'|'ship'|'static']  (opzionali, solo se il paese ne ha)
            ['group'][j]
                ... campi di gruppo ...
                ['units'][k]
                    ... campi di unità ...
```

Il lato `neutrals` ha `country = {}` (nessun paese schierato) e `bullseye = {x=100, y=100}`
(valore di default).

### 3.2 Paesi presenti e contenuto

Conteggi `gruppi/unità` per paese e categoria (misurati):

| Lato | Paese (id) | plane | helicopter | vehicle | ship | static |
|---|---|---|---|---|---|---|
| blue | Georgia (16) | 11/21 | — | 9/36 | 1/10 | 34/34 |
| blue | USA (2) | 55/93 | 3/3 | 35/199 | 3/21 | 63/63 |
| blue | Sweden (46) | 11/19 | — | 1/1 | — | — |
| blue | France (5) | — | — | 1/1 | — | — |
| blue | UK (4) | — | — | 1/1 | — | — |
| blue | Germany (6) | — | — | — | — | 12/12 |
| red | Russia (0) | 91/150 | 2/2 | 63/314 | 2/28 | 165/165 |
| neutrals | (nessuno) | — | — | — | — | — |

Osservazione: il paese è l'attributo che determina il livery e l'insieme di tipi ammessi
(la Svezia compare solo perché fornisce gli AJS37; i paesi "vuoti" France/UK/Germany servono
solo per far comparire pochi oggetti con la nazionalità giusta). I paesi neutrali elencati in
`coalitions['neutrals']` (54 id) non hanno alcun gruppo.

### 3.3 Aerei (`plane`) e elicotteri (`helicopter`)

Stesso schema per le due categorie; le differenze sono in coda. Dati: 168 gruppi plane
(283 unità), 5 gruppi helicopter (5 unità).

**Campi di gruppo**

| Chiave | Tipo | Unità | Valori osservati | Significato |
|---|---|---|---|---|
| `groupId` | int | — | univoco (100005 ... , 419 per elicotteri) | id del gruppo; i gruppi generati da DCE partono da 100000 |
| `name` | str | — | `'Pack 14 - GA 4rd AS - Strike 1'` | convenzione DCE `Pack <n> - <squadriglia> - <ruolo> <k>` |
| `task` | str | — | v. §4.1 (12 valori) | ruolo/task di gruppo mostrato dall'editor |
| `taskSelected` | bool | — | `true` ×168 | il task è stato scelto esplicitamente |
| `x`, `y` | float | m | `x` in [-355.692 ; 12.693], `y` in [368.948 ; 905.626] | posizione di partenza (v. coordinate in §6.4) |
| `start_time` | float | s da inizio missione | `1` ×124, valori fino a 3966 | istante di attivazione del gruppo |
| `hidden` | bool | — | true ×91, false ×77 | nascosto sulla mappa/pianificatore |
| `lateActivation` | bool | — | true ×43, false ×100 (assente ×25) | il gruppo esiste ma non è attivo finché un trigger `a_activate_group` lo attiva |
| `TrigActivate` | bool | — | `true` ×43 | marcatore, coincide con `lateActivation=true` |
| `uncontrolled` | bool | — | true ×123, false ×45 | partenza a terra a motori spenti, in attesa di comando `Start` (via `a_set_ai_task`) |
| `communication` | bool | — | `true` ×168 | radio attiva |
| `radioSet` | bool | — | `true` ×168 (heli: false) | |
| `frequency` | float | MHz | 131 valori distinti (es. 259,05; 336,025) | frequenza radio di gruppo |
| `modulation` | int | enum | `0` ×168 | 0 = AM |
| `tasks` | array | — | 123 gruppi hanno 1 voce `WrappedAction` con azione `Start` | azioni di gruppo: comando di avvio per i gruppi `uncontrolled` |
| `route.points` | array | — | v. sotto | rotta |
| `units` | array | — | v. sotto | unità |

Il `task` di un gruppo è solo un'etichetta per l'editor: il comportamento reale è dato dai
task nei waypoint (v. sotto).

**Campi di waypoint (`route.points[]`)** — n=1495 punti per i plane

| Chiave | Tipo | Unità | Valori osservati | Significato |
|---|---|---|---|---|
| `x`, `y` | float | m | coordinate mappa | posizione |
| `alt` | float | m | 110 valori (7500 ×221, 4000 ×128, 3000 ×127, 6096 ×109, ...) | quota |
| `alt_type` | str | enum | `'BARO'` ×1438, `'RADIO'` ×57 | `BARO` = sul livello del mare (QNH), `RADIO` = dal suolo/mare |
| `speed` | float | m/s | 32 valori (200 ×385, 250 ×268, 215,83, 150, ...) | velocità. 250 m/s = 900 km/h |
| `speed_locked` | bool | — | true ×424, false ×1071 | la velocità è bloccata (l'editor non la ricalcola dall'ETA) |
| `ETA` | float | s da inizio missione | 401 valori distinti, fino a 52.494 | istante di arrivo previsto |
| `ETA_locked` | bool | — | true ×1239, false ×256 | l'ETA è bloccata (guida il calcolo) |
| `type` | str | enum | `'Turning Point'` ×1234, `'Land'` ×160, `'TakeOffParking'` ×100, `'TakeOffParkingHot'` ×1 | tipo di waypoint (v. §4.2) |
| `action` | str | enum | `'Turning Point'` ×1112, `'Landing'` ×160, `'Fly Over Point'` ×122, `'From Parking Area'` ×100, `'From Parking Area Hot'` ×1 | azione del waypoint (v. §4.2) |
| `name` | str | — | `'Nav'`, `'IP'`, `'Split'`, `'Land'`, `'Join'`, `'Departure'`, `'Egress'`, `'AI Descend Helper'`, `'Attack'`, `'Station'`, `'Spawn'`, `'Intercept'`, `'Sweep'` | nome del waypoint (convenzione DCE) |
| `briefing_name` | str | — | 12 valori (come `name`, ma `AI Descend Helper` appare come `IP`) | nome mostrato nel briefing |
| `formation_template` | str | — | `''` ×1495 | formazione predefinita (non usata) |
| `airdromeId` | int | id aeroporto | 13 valori distinti (32, 26, 16, 27, 22, ...) n=255 | aeroporto di decollo/atterraggio (solo punti `TakeOff*`/`Land`) |
| `helipadId`, `linkUnit` | int | id unità | 830, 831 (n=26) | atterraggio/decollo su unità mobile (portaerei/LHA) |
| `properties` | tabella | — | `{angle=0, scale=0, steer=2, vangle=0, vnav=1}` costanti ×1495 | parametri di navigazione dell'editor (invariati) |
| `task` | tabella | — | sempre `{id='ComboTask', params={tasks=[...]}}` | compiti eseguiti al waypoint (v. sotto) |

Nota: la quota `alt` dei punti `TakeOffParking`/`Land` è la quota barometrica del campo
(es. 1369,4 m), non zero.

**Compiti al waypoint (`route.points[].task.params.tasks[]`)** — n=1615 per i plane

Ogni elemento ha `enabled` (bool), `auto` (bool), `number` (int, ordine 1..38), `id` (str) e
`params`. Distribuzione di `id` (aerei+elicotteri, v. anche §4.3):

| `id` | n | `enabled` | Significato e parametri |
|---|---:|---|---|
| `WrappedAction` | 920 (+12 heli) | true | contiene `params.action = {id, params}`: Option, Script, SwitchWaypoint, ActivateBeacon, DeactivateBeacon (v. §4.4) |
| `AttackMapObject` | 316 | **sempre false** | attacco a oggetto di mappa: `x`, `y`, `weaponType`, `expend`, `attackQty`, `attackQtyLimit`, `altitude`, `altitudeEnabled`, `direction`, `directionEnabled`, `groupAttack` |
| `AttackGroup` | 272 (+2 heli) | false ×271, true ×3 | attacco a gruppo: `groupId`, `weaponType`, `expend` |
| `ControlledTask` | 104 | true | task con condizione di fine: `params.task = {id,params}` + `params.stopCondition = {time \| lastWaypoint}` (86 con stopCondition) |
| `EngageTargets` | 3 | true | ingaggio bersagli, diretto: `targetTypes`, `priority` |
| `Orbit` / `EngageTargets` / `EngageTargetsInZone` / `Tanker` / `AWACS` | dentro `ControlledTask.params.task` (41/44/9/6/4) | | `Orbit`: `pattern` (`Race-Track` ×29, `Circle` ×12), `altitude`, `speed`; `EngageTargets`: `targetTypes`, `noTargetTypes`, `maxDist`, `maxDistEnabled`, `value`; `EngageTargetsInZone`: `x`, `y`, `zoneRadius` (50000 m), `targetTypes` |

**Scoperta importante (task di attacco disabilitati)**: i task editor `AttackMapObject` e
`AttackGroup` sono presenti ma **disabilitati** (587 su 590 sono `enabled=false`); l'attacco
effettivo è eseguito dagli script `CustomTasksScript.lua` tramite una `WrappedAction`
di tipo `Script` abilitata (v. §4.4 e §7). I task editor servono come "documentazione" e per
riportare coordinate/armi.

**Campi di unità (`units[]`)** — n=283 per i plane

| Chiave | Tipo | Unità | Valori osservati | Significato |
|---|---|---|---|---|
| `unitId` | int | — | univoco (100000...) | id unità |
| `name` | str | — | `'<nome gruppo>-<k>'` | nome unità |
| `type` | str | — | 20 tipi (F-4E ×44, MiG-27K ×35, MiG-21Bis ×30, Su-24M ×22, L-39A ×21, AJS37 ×19, S-3B ×18, Su-17M4 ×18, F-14A-135-GR ×13, MiG-25PD ×13, MiG-23MLD ×11, MiG-19P ×10, Tu-22M3 ×7, B-52H ×5, F-5E-3 ×5, S-3B Tanker ×4, E-3A ×2, KC-135 ×2, A-50 ×2, An-26B ×2) | tipo DCS (nome interno) |
| `x`, `y` | float | m | | posizione (parcheggio o inizio rotta) |
| `alt` | float | m | 93 valori; 0 ×8 | quota di partenza (quota campo se a terra) |
| `alt_type` | str | enum | `BARO` ×195, `RADIO` ×88 | |
| `speed` | float | m/s | 17 valori (140 ×66, 150 ×55, 161,875 ×44, ...) | velocità di partenza (1 se a terra) |
| `heading` | float | rad | `0` ×283 | prua (0 = nord) |
| `psi` | float | rad | `0` ×283 (heli: -0,054) | |
| `skill` | str | enum | `High` ×127, `Good` ×102, `Average` ×37, `Excellent` ×16, `Client` ×1 | livello AI (`Client` = slot giocatore) |
| `onboard_num` | str | — | 110 valori, es. `'053'` | numero di fiancata |
| `livery_id` | str | — | 8 valori (`''` ×221, `'af standard'`, `'vf-101 dark'`, ...) | livrea |
| `callsign` | tabella o int | — | `{1,2,3,name='Enfield51'}` (n=133) oppure intero (es. 101) | nominativo radio |
| `hardpoint_racks` | bool | — | `true` ×283 | |
| `payload` | tabella | — | v. sotto | carico |
| `Radio` | array | — | n=1 (solo il giocatore) | 2 radio con `channels[]` (frequenze MHz) |
| `AddPropAircraft` | tabella | — | n=23, chiavi specifiche del modello (TACAN, ILS, LGB1..., ecc.) | proprietà aggiuntive per tipo aereo |

`payload`:

| Chiave | Tipo | Unità | Osservato | Significato |
|---|---|---|---|---|
| `fuel` | str o int | **kg** | 19 valori (`2280`, `'4864'`, `'4500'`, `'11700'`, ...) | carburante interno (nota: stringa o intero, v. §6.5) |
| `flare` | int | pezzi | 11 valori (0, 30, 36, 60, 64, 96, 192...) | flare |
| `chaff` | int | pezzi | 13 valori (0, 30, 48, 60, 64, 96, 105, 140) | chaff |
| `gun` | int | % | 100 ×279, 0 ×4 | munizioni cannone, percentuale |
| `pylons` | tabella indicizzata per numero di pilone | — | 1599 voci in 283 unità | ogni voce `{CLSID='{...}', num=<pilone>}` |
| `pylons[].CLSID` | str | — | 53 valori distinti (es. `'{AIM_54A_Mk60}'`, `'{R-3R}'`, `'{7B4B122D-...}'`) | identificatore DCS dell'armamento/serbatoio sul pilone |

**Differenze degli elicotteri**: nelle unità compaiono `parking`, `parking_id` (id del
parcheggio assegnato sulla piattaforma/FARP) e `ropeLength` (m, per carico appeso);
`alt_type = 'RADIO'` su tutti i punti (20 su 20), `radioSet = false`; `task` di gruppo
`Transport` ×3, `CAS` ×2. Tipi: SH-60B ×3 (elicottero SAR "Pedro" legato alla portaerei) e
Mi-24V ×2.

### 3.4 Veicoli terrestri (`vehicle`)

110 gruppi, 552 unità, **tutti con un solo waypoint** (v. §6.2).

**Campi di gruppo**

| Chiave | Tipo | Unità | Osservato | Significato |
|---|---|---|---|---|
| `groupId` | int | — | univoco (380, 382, ...) | |
| `name` | str | — | `'EWR-1'`, `'Tbilisi Defenses'`, `'11 1st Artillery Division/1.Btry'` | |
| `task` | str | — | `'Ground Nothing'` ×90, `'Pas de sol'` ×10 (assente ×10) | etichetta (`Pas de sol` è un valore francese residuo dell'editor/localizzazione) |
| `taskSelected` | bool | — | true ×100 | |
| `x`, `y` | float | m | | |
| `start_time` | int | s | `0` ×110 | |
| `hidden` | bool | — | true ×63, false ×47 | |
| `visible` | bool | — | `false` ×110 | |
| `uncontrollable` | bool | — | `false` (n=45) | |
| `tasks` | tabella | — | vuota ×110 | |
| `route.points` | array | — | **1 punto per gruppo** | |
| `route.spans` | array | — | n=110 (20 con 2 punti-segmento `{x,y}`; gli altri vuoti) | tracciato stradale (usato per i gruppi vicino a ponti) |
| `units` | array | — | v. sotto | |

**Waypoint (unico)**

| Chiave | Tipo | Unità | Osservato | Significato |
|---|---|---|---|---|
| `x`, `y` | float | m | | uguali alla posizione del gruppo |
| `alt` | int | m | 90 valori | quota del terreno |
| `alt_type` | str | | `BARO` ×110 | |
| `type` | str | | `Turning Point` ×110 | |
| `action` | str | | `Off Road` ×110 | (alternativa non osservata: `On Road`, `Cone`, `Vee`... non verificato nel file) |
| `speed` | float | m/s | `0` ×66, `5.5556` ×34 (=20 km/h), `4` ×10 | velocità: per un solo waypoint non ha effetto |
| `speed_locked`, `ETA_locked` | bool | | true | |
| `ETA` | int | s | `0` | |
| `name`, `formation_template` | str | | `''` | |
| `task` | tabella | | `ComboTask` con 50 task totali: `WrappedAction` 44 (`EPLRS` ×32, `SetFrequency` ×6, `SetCallsign` ×6), `EWR` ×6 | `EPLRS` = datalink (`groupId`, `value=true`); `SetFrequency` (`frequency` in **Hz**, `modulation`, `power`); `EWR` = designa il gruppo come radar di allarme |

**Unità**

| Chiave | Tipo | Unità | Osservato | Significato |
|---|---|---|---|---|
| `unitId` | int | — | univoco | |
| `name` | str | — | `'Unit #267'`, `'<gruppo>-<k>'` | |
| `type` | str | — | 50 tipi (v. §6.2) | |
| `x`, `y` | float | m | | |
| `heading` | float | rad | 116 valori (0..6,28) | |
| `skill` | str | enum | `Average` ×319, `Good` ×178, `High` ×55 | |
| `playerCanDrive` | bool | | true ×292, false ×260 | |
| `transportable` | tabella | | `{randomTransportable=false}` ×552 | |
| `AddPropVehicle` | tabella | | `{Branches=false}` (n=7) | |

### 3.5 Navi (`ship`)

6 gruppi, 59 unità, **rotte con più waypoint** (25 punti in totale; 2-7 per gruppo).

| Chiave | Tipo | Unità | Osservato | Significato |
|---|---|---|---|---|
| gruppo: `groupId`, `name`, `x`, `y`, `start_time` (0), `hidden`, `visible` (false), `uncontrollable` (false), `tasks` (vuota) | | | `NATO Convoy 1`, `LHA-Group`, `TF-74`, `TF-71`, `Russian Convoy 1`, `Russian Convoy 2` | |
| `route.points[]` | array | | 25 punti | |
| punto: `type` | str | | `Turning Point` ×25 | |
| punto: `action` | str | | `Turning Point` ×25 | |
| punto: `speed` | float | **m/s** | `8` ×13, `5` ×12 | 8 m/s ≈ 15,5 nodi; 5 m/s ≈ 9,7 nodi |
| punto: `alt` | int | m | 0 | |
| punto: `ETA` | int | s | `0` | |
| punto: `task` | tabella | | 6 `WrappedAction`: `ActivateBeacon` ×3 (`AA`, `bearing`, `callsign`, `channel`, `frequency` Hz, `modeChannel='X'`, `system=3`, `type`, `unitId`) e `ActivateICLS` ×3 (`channel`, `type=131584`, `unitId`) | TACAN e ICLS delle portaerei/LHA |
| unità: `type` | str | | 12 tipi: ELNYA ×12, Dry-cargo ship-1 ×10, PERRY ×9, Dry-cargo ship-2 ×6, ALBATROS ×5, MOLNIYA ×5, USS_Arleigh_Burke_IIa ×3, TICONDEROG ×3, HandyWind ×3, LHA_Tarawa, Stennis, CVN_71 | |
| unità: `frequency` (Hz, 127500000 ×56) e `modulation` | | | | radio |
| unità: `heading` | float | rad | | |
| unità: `skill` | str | | `Average` ×56, `High` ×3 | |
| unità: `livery_id` | str | | 15 valori | |
| unità: `transportable` | | | | |

Le rotte delle navi sono "circuiti di pattugliamento" definiti da punti che corrispondono a
trigger zones omonime (`Indy 1-1..1-4`, `Indy 3-1..3-4`, `Convoy 1-1..`, `NATO convoy 1-1..`);
`camp_status.lua` li registra in `camp.ShipMissions[nome].WPtable` con `PatrolSpeed`,
`CruiseSpeed` e `StartTime` (v. §7).

### 3.6 Statici (`static`)

274 gruppi, 274 unità, **un solo oggetto per gruppo**, un solo punto con valori vuoti.

| Chiave | Tipo | Unità | Osservato | Significato |
|---|---|---|---|---|
| gruppo: `groupId` | int | | | |
| gruppo: `name` | str | | `'AMBROLAURI FARP LN41'`, `'SUPPLY PLANT DAPNARI KM76-10'` | |
| gruppo: `x`, `y`, `heading` | float | m, m, rad | | |
| gruppo: `dead` | bool | | `false` ×274 | oggetto già distrutto all'avvio (qui mai) |
| gruppo: `hidden` | bool | | true ×165, false ×4 (assente ×105) | |
| gruppo: `hiddenOnMFD`, `hiddenOnPlanner` | bool | | `false` (n=1, n=2) | |
| gruppo: `route.points[1]` | | | `{x, y, alt=0, speed=0, action='', type='', name='', formation_template=''}` | punto "fantasma" |
| unità: `unitId`, `name`, `x`, `y`, `heading` | | | | |
| unità: `type` | str | | 48 tipi (`Container brown` ×34, `Barracks 2` ×24, `iso_container` ×20, `Chemical tank A` ×16, `GAZ-3308` ×14, `ATZ-10` ×12, `FARP Tent`, `FARP`, UH-1H, Mi-8MT, Mi-24V...) | tipo oggetto |
| unità: `category` | str | enum | `Fortifications` ×136, `Unarmed` ×53, `Cargos` ×35, `Helicopters` ×24, `Warehouses` ×9, `Air Defence` ×7, `Heliports` ×6, `Armor` ×4 | classe dell'oggetto statico |
| unità: `shape_name` | str | | 24 valori (`konteiner_brown`, `kazarma2`, ...), n=185 | modello 3D |
| unità: `rate` | int/str | | 9 valori (100 ×97, 3, 20, 50, 5, `'20'`, `'30'`, 7) | "valore" dell'oggetto (peso di punteggio nell'editor) |
| unità: `mass` | int | kg | 4500, 2400, 1500 (n=35) | massa del cargo |
| unità: `canCargo` | bool | | true ×34 (n=35) | trasportabile come carico appeso |
| unità: `livery_id` | str | | 11 valori, n=37 (solo statici-velivoli) | |
| unità: `heliport_callsign_id`, `heliport_frequency` (str, MHz), `heliport_modulation` | | | n=6, `'128.5'`, `'245.000'`, ... | dati dei FARP/eliporti |

Gli statici includono: 24 velivoli parcheggiati (UH-1H ×7, Mi-8MT ×7, Mi-24V ×7, Mi-24P ×3),
4 FARP e 2 `SINGLE_HELIPAD`, 9 magazzini/serbatoi, 7 radar/posti di comando di difesa aerea,
4 mezzi corazzati, 136 fortificazioni, 53 mezzi non armati e 35 cargo. I FARP sono gli
oggetti che hanno un magazzino nel file `warehouses` (v. §5.1).

---

## 4. Cataloghi enumerati osservati

### 4.1 Task di gruppo (`group.task`)

| Categoria | Valori (conteggio) |
|---|---|
| plane (168) | `CAS` 52, `Ground Attack` 45, `Escort` 13, `Pinpoint Strike` 12, `SEAD` 10, `CAP` 9, `Intercept` 8, `Refueling` 6, `Fighter Sweep` 4, `AWACS` 4, `Antiship Strike` 3, `Transport` 2 |
| helicopter (5) | `Transport` 3, `CAS` 2 |
| vehicle (110) | `Ground Nothing` 90, `Pas de sol` 10, assente 10 |
| ship, static | assente |

### 4.2 Waypoint

| Campo | Valori osservati (per categoria) |
|---|---|
| `type` | plane: `Turning Point`, `Land`, `TakeOffParking`, `TakeOffParkingHot`; heli: `Turning Point`, `TakeOffParking`, `Land`; vehicle/ship: `Turning Point`; static: `''` |
| `action` | plane: `Turning Point`, `Landing`, `Fly Over Point`, `From Parking Area`, `From Parking Area Hot`; heli: come plane meno `Hot`; vehicle: `Off Road`; ship: `Turning Point`; static: `''` |
| `alt_type` | `BARO`, `RADIO` |
| `name` (convenzione DCE) | `Departure`, `Join`, `Nav`, `IP`, `AI Descend Helper`, `Attack`, `Egress`, `Split`, `Land`, `Spawn`, `Station`, `Intercept`, `Sweep` |
| profilo tipico di un pack d'attacco (10 punti, 85 gruppi) | `Departure` → `Join` → `Nav` → `AI Descend Helper` → `IP` → `Attack` (`Fly Over Point`) → `Egress` → `Nav` → `Split` → `Land` |

Altri valori noti di DCS non osservati in questo file (da conoscenza generale, non verificati
nel file): `type` `TakeOff`, `TakeOffGround`, `LandingReFuAr`, `On Road`, `Cone`, `Vee`,
`Rank`, ...

### 4.3 Task nei waypoint (`task.id`) e azioni

| Livello | Valori osservati |
|---|---|
| `task.id` del waypoint | sempre `ComboTask` (1495/1495 plane; 110/110 vehicle; 25/25 ship) |
| elementi di `ComboTask.params.tasks[].id` | `WrappedAction`, `AttackMapObject`, `AttackGroup`, `ControlledTask`, `EngageTargets` (aerei); `WrappedAction`, `EWR` (veicoli); `WrappedAction` (navi) |
| `ControlledTask.params.task.id` | `EngageTargets` 44, `Orbit` 41, `EngageTargetsInZone` 9, `Tanker` 6, `AWACS` 4 |
| `ControlledTask.params.stopCondition` | `lastWaypoint` (int, indice) ×45, `time` (float, s) ×41 |
| `WrappedAction.params.action.id` | aerei: `Option` 572, `Script` 326, `SwitchWaypoint` 10, `ActivateBeacon` 6, `DeactivateBeacon` 6; veicoli: `EPLRS` 32, `SetFrequency` 6, `SetCallsign` 6; navi: `ActivateBeacon` 3, `ActivateICLS` 3; gruppi: `Start` (123) |

### 4.4 Opzioni di waypoint (`Option`) e script

`Option` ha `params = {name=<id opzione>, value=<valore>}`. Coppie osservate:

| `name` | `value` | n | Significato (id: DCS AI Option, non verificato nel file) |
|---|---|---:|---|
| 1 | 2 | 168 | `REACTION_ON_THREAT` = `EVADE_FIRE` |
| 5 | 458753 (con `formationIndex=7`, `variantIndex=1`) | 160 | `FORMATION` (formazione codificata come numero) |
| 15 | true / false | 122 / 122 | `PROHIBIT_JETT` (vietato sganciare carichi/serbatoi) attivato in partenza, disattivato a `Egress` |

Funzioni Lua chiamate dalle `WrappedAction` `Script` (campo `params.command`, n=326 plane):

| Funzione | n | Argomenti | Cosa fa (da `CustomTasksScript.lua`) |
|---|---:|---|---|
| `CustomRejoin(flight)` | 112 | nome del volo | ricongiunge il volo dopo l'attacco |
| `OrbitPosition(flight, alt, speed, untilTime)` | 88 | quota m, velocità m/s, istante s | attende in orbita fino a un istante (sincronizzazione TOT) |
| `CustomMapObjectAttack(flight, {{x,y}}, expend, weaponType, attackType, attackAlt)` | 56 | | bombardamento di oggetti di mappa |
| `CustomGroupAttack(flight, groupName, expend, weaponType, attackType, attackAlt)` | 35 | | attacco a gruppo terrestre |
| `CustomSearchThenEngage(flight, radius, targetType)` | 17 | | ricerca e ingaggio (sweep) |
| `CustomStaticAttack(flight, {nomi statici}, ...)` | 14 | | attacco a statici per nome |
| `CustomAirbaseAttack(flight, {x,y}, ...)` | 4 | | attacco a una pista |

Valori dei parametri delle funzioni: `expend` ∈ {`All`, `Auto`}; `attackType` ∈ {`Dive`};
`weaponType` è una maschera di bit di DCS (`2032` ×493, `4161536` ×70, `30720` ×25);
`targetTypes`/`noTargetTypes` ∈ {`Air`, `SAM TR`, `Cruise missiles`, `Ships`, `Antiship Missiles`,
`AA Missiles`, `AG Missiles`, `SA Missiles`}; `pattern` ∈ {`Race-Track`, `Circle`}.

### 4.5 Altri enumerati

| Campo | Valori |
|---|---|
| `skill` (unit) | `Average`, `Good`, `High`, `Excellent`, `Client` (plane); `Average`, `Good`, `High` (vehicle, ship, heli) |
| partenza | non c'è un campo "start type" esplicito: è determinata da `route.points[1].type/action` (`TakeOffParking`/`From Parking Area` = freddo a terra, `TakeOffParkingHot`/`From Parking Area Hot` = caldo, `Turning Point` = già in volo) più `uncontrolled` e `lateActivation` (v. §6.3) |
| `modulation` | 0 (AM); da conoscenza generale 1 = FM, non osservato per i plane |
| `coalition` in `warehouses` | `'RED'`, `'BLUE'` (aeroporti, maiuscolo) e `'blue'`, `'red'` (FARP, minuscolo) — incoerenza da tenere presente |
| `trigrules.predicate` | `triggerStart`, `triggerOnce` |
| `trigrules.rules.predicate` | `c_time_after`, `c_flag_is_true` |
| `trigrules.actions.predicate` | `a_set_ai_task`, `a_activate_group`, `a_do_script_file` |
| `forcedOptions.optionsView` | `optview_all` |
| `weather.clouds.preset` | `Preset4` |

---

## 5. Warehouses, weather, options, trigger, goals

### 5.1 `warehouses`

Due tabelle: `airports` (21 voci, indice = id aeroporto 12..32 del Caucaso) e `warehouses`
(36 voci, indice = `unitId` di FARP/nave/oggetto con magazzino, es. 1201, 635).

Struttura identica per le due (chiavi osservate, 17 per voce):

| Chiave | Tipo | Valore osservato | Significato |
|---|---|---|---|
| `coalition` | str | `'RED'`/`'BLUE'` (aeroporti: 12 / 9); `'red'`/`'blue'` (36 FARP: 6 / 30) | proprietario |
| `unlimitedFuel` | bool | `true` ×57 | carburante illimitato |
| `unlimitedMunitions` | bool | `true` ×57 | munizioni illimitate |
| `unlimitedAircrafts` | bool | `true` ×57 | velivoli illimitati |
| `jet_fuel`, `gasoline`, `diesel`, `methanol_mixture` | `{InitFuel=<int>}` | `{InitFuel=100}` ×57 | scorta iniziale per tipo di carburante (unità: percentuale/tonnellate, non verificato; valore di default dell'editor) |
| `OperatingLevel_Air`, `OperatingLevel_Fuel`, `OperatingLevel_Eqp` | int | `10` ×57 | livello operativo (0-10) |
| `size` | int | `100` | dimensione del magazzino |
| `speed` | float | `16.666666` | velocità di rifornimento |
| `periodicity` | int | `30` | periodo di rifornimento (minuti) |
| `suppliers` | tabella | vuota ×57 | magazzini fornitori (catena logistica) |
| `aircrafts` | tabella | vuota ×57 | `{tipo = {initialAmount, wsType}}` quando popolata |
| `weapons` | tabella | vuota ×57 | `{...}` quando popolata |

Conclusione: in questa `.miz` il sistema warehouse di DCS non è usato (tutto illimitato e
vuoto, valori di default). Le scorte reali di aerei e munizioni vivono nel modello DCE
(`camp.aircraft_availability`, v. §7) e vengono tradotte in numero di gruppi generati.

### 5.2 `options`

Tabella con 7 sezioni: `playerName` (str, `'New callsign'`), `difficulty`, `views`,
`miscellaneous`, `sound`, `VR`, `plugins`. Le chiavi sono preferenze del client DCS, non
della missione, tranne `difficulty` (impostazioni di realismo).

`difficulty` (28 chiavi, valori osservati): `easyRadar=false`, `easyFlight=false`,
`easyCommunication=false`, `immortal=false`, `fuel=false`, `weapons=false`, `radio=false`,
`padlock=true`, `map=true`, `labels=3`, `birds=0`, `geffect='realistic'`, `units='metric'`,
`optionsView='optview_all'`, `iconsTheme='nato'`, `avionicsLanguage='english'`,
`permitCrash=false`, `wakeTurbulence=false`, `RBDAI=true`, `reports=true`, `tips=true`,
`userMarks=true`, `externalViews=true`, `spectatorExternalViews=true`, `cockpitVisualRM=false`,
`cockpitStatusBarAllowed=false`, `miniHUD=false`, `hideStick=false`, `setGlobal=true`,
`unrestrictedSATNAV=false`, `userSnapView=true`, `controlsIndicator=true`, `autoTrimmer=false`.

`plugins`: una sotto-tabella per ogni modulo installato (Mi-8MTV2, A-10C_2, F-14, F/A-18C,
FC3, ecc.) con le opzioni specifiche del modulo. `miscellaneous`: `Coordinate_Display =
'Lat Long'`, `f10_awacs=true`, `collect_stat=true`, ecc. **Nessuno di questi campi dipende
dallo stato del mondo**: va copiato dal template.

### 5.3 `weather`, `date`, `start_time`

`date = {Day=13, Month=9, Year=1975}`; `start_time = 17476` (04:51:16, secondi dalla
mezzanotte). Il tempo di missione è `start_time` + secondi trascorsi.

`weather` (16 chiavi, valori osservati):

| Chiave | Tipo | Unità | Valore | Significato |
|---|---|---|---|---|
| `name` | str | | `'Winter, clean sky'` | etichetta del preset (incoerente con la data: settembre) |
| `type_weather` | int | enum | `0` | 0 = meteo statico/classico (non osservato altro) |
| `atmosphere_type` | int | enum | `0` | 0 = atmosfera normale |
| `season.temperature` | int | °C | `8` | temperatura al suolo |
| `qnh` | int | **mmHg** | `774` | pressione al livello del mare |
| `wind.atGround / at2000 / at8000` | `{speed, dir}` | m/s, gradi | `{3,217}`, `{2.4,217}`, `{7.5,217}` | vento a 3 quote (0, 2000, 8000 m); la direzione è in gradi (convenzione DCS: da conoscenza generale è la direzione verso cui soffia; non verificato nel file) |
| `turbulence` | `{atGround, at2000, at8000}` | | `9, 8, 7` | turbolenza per quota |
| `groundTurbulence` | int | | `0` | |
| `clouds` | `{base, density, thickness, iprecptns, preset}` | m, 0-10, m, enum | `base=2150`, `density=0`, `thickness=0`, `iprecptns=0`, `preset='Preset4'` | nuvole; `preset` volumetrico e campi classici coesistono |
| `visibility.distance` | int | m | `80000` | visibilità |
| `enable_fog`, `fog.{thickness,visibility}` | bool, m | | `false`, `0`, `25` | nebbia |
| `enable_dust`, `dust_density` | bool, int | | `false`, `0` | polvere |
| `cyclones` | array | | vuota | cicloni |
| `modifiedTime` | bool | | `true` | |

Il meteo è **statico** (una sola fotografia). DCE lo gestisce con un modello a zone
(`camp.weather = {zone, zoneNext, zoneStart, zoneEnd, zoneTemp, zoneNextTemp, refTemp,
pHigh, pLow}`, es. `zone='high'`, `refTemp=20`) e riscrive `weather` ad ogni missione;
`camp.dawn=21600` (06:00) e `camp.dusk=65700` (18:15) sono alba e tramonto in secondi dalla
mezzanotte.

### 5.4 `trig`, `trigrules`, `triggers`

**Tre strutture da tenere sincronizzate** (v. `ANALISI_DCE.md` §4.2):

| Tabella | n | Ruolo |
|---|---:|---|
| `trig.conditions[n]` | 180 | stringa Lua `return(...)`: `return(true)` per gli avvii, `return(c_time_after(2272.47) )` per le attivazioni temporizzate |
| `trig.actions[n]` | 180 | stringa Lua: `a_do_script_file(getValueResourceByKey("ResKey_Action_n"));`, `a_activate_group(<groupId>); mission.trig.func[n]=nil;`, `a_set_ai_task(<groupId>, 1); mission.trig.func[n]=nil;` |
| `trig.func[n]` | 170 | `if mission.trig.conditions[n]() then mission.trig.actions[n]() end`, eseguito periodicamente (trigger "once") |
| `trig.funcStartup[n]` | 10 | come `func` ma eseguito all'avvio (trigger 1-10) |
| `trig.flag[n]` | 180 | `true` ×180: trigger abilitato all'inizio |
| `trigrules[n]` | 180 | forma per l'editor: `{predicate, comment, eventlist='', rules{...}, actions{...}}` |

Composizione dei 180 trigger: 10 `triggerStart` (n.1 "Scenery Destruction", con `actions` vuoto =
nessuno scenario da distruggere; n.2-10 avviano i 9 script DCE) e 170 `triggerOnce`:
125 `a_set_ai_task` (avvio dei gruppi `uncontrolled`; parametri `set_ai_task = {1=<groupId>,
2=1}`; 1 = indice del task "Start" del gruppo) e 45 `a_activate_group` (attivazione dei
gruppi `lateActivation`, parametro `group=<groupId>`). Ogni regola ha una condizione
`c_time_after` (163 volte, `seconds` s da inizio missione) o `c_flag_is_true` (7 volte).

**Conseguenza per il modello**: tutta la tempistica dei voli è espressa con ~170 trigger a
tempo (secondi dall'inizio missione), non con eventi di gioco. Un generatore deve calcolare
per ogni gruppo l'istante di attivazione/avvio.

`triggers.zones` (36 zone): tutte `type=0` (cerchio), `hidden=true`, `radius=4.8768` m
(≈ 16 piedi), `color={1=0,2=0.50196,3=1,4=0.14902}` (RGBA 0..1), `x`, `y` (m), `zoneId`
(165...), `name`, `properties={}`. Nomi: `Indy 1-1..` (12, punti di pattugliamento delle
portaerei), `Convoy` (8) e `NATO convoy` (4) (punti dei convogli navali), 12 zone di
orbita (`CAP Tbilissi`, `CAP Kutaisi`, `CAP Mozdok`, `CAP Beslan`, `CAP Mineralnye-Vody`,
`CAP Nalchik`, `CAP Center`, `AWACS`, `AWACS-RED`, `CAP-AWACS`, `Tanker Track West`,
`Tanker Track East KC`). Le zone non hanno funzione di trigger: sono **segnaposto di
coordinate**.

### 5.5 `goals`, `result`

- `goals`: 1 voce `{side='OFFLINE', predicate='score', score=51, comment='Assign Mission Score',
  rules={1={predicate='c_time_after', seconds=2, coalitionlist='red', zone='', percent=100}}}`.
- `result`: `{total=0, offline={conditions={1='return(c_time_after(2) )'}, actions={1=
  'a_set_mission_result(51)'}, func={...}}, blue={}, red={}}` — la missione "termina con
  punteggio 51 dopo 2 secondi" in modalità offline: serve solo a far restituire un risultato
  all'editor; la vera logica di successo è in DCE fuori da DCS.

### 5.6 Altre chiavi

- `failures`: 268 voci `{id, enable=false, prob=100, mm=0, hh=0, mmint=1}` (guasti
  programmabili per modello, es. `Failure_Elec_RightTransformerRectifier`, `AIRBRAKE`,
  `HUDDISPLAY`, `RWR_FAILURE_MBE`). **Tutti disattivati.**
- `forcedOptions` (13 chiavi): `optionsView='optview_all'`, `labels=0`, `birds=50`,
  `miniHUD=false`, `userMarks=true`, `padlock=false`, `RBDAI=true`, `wakeTurbulence=true`,
  `permitCrash=true`, `cockpitStatusBarAllowed=false`, `civTraffic=''`, `externalViews=true`,
  `cockpitVisualRM=true`.
- `groundControl`: `roles.{instructor,observer,forward_observer,artillery_commander}.{neutrals,
  blue,red}` (0/1 slot; solo `observer.blue=1`) e `isPilotControlVehicles=false`.
- `map`: `{centerX=-203603.6, centerY=841325.1, zoom=494572}` — centro e zoom della vista
  dell'editor (metri).
- `coalitions`: mappa lato → lista di country id (blue 20, red 11, neutrals 54).

---

## 6. Statistiche

### 6.1 Conteggi per coalizione e categoria (gruppi / unità)

| Categoria | blue | red | totale |
|---|---|---|---|
| plane | 77 / 133 | 91 / 150 | 168 / 283 |
| helicopter | 3 / 3 | 2 / 2 | 5 / 5 |
| vehicle | 47 / 238 | 63 / 314 | 110 / 552 |
| ship | 4 / 31 | 2 / 28 | 6 / 59 |
| static | 109 / 109 | 165 / 165 | 274 / 274 |
| **totale** | **240 / 514** | **323 / 659** | **563 / 1173** |

Per gli aerei: 67 pack (`Pack 1..67`), 168 gruppi (un pack = 1-4 gruppi: scorta + attaccanti
+ SEAD...), 36 squadriglie diverse (VS-22 ×12 gruppi, 790.IAP ×8, 1./135.IAP ×8, ...);
gruppi con 1 unità ×98, 2 ×40, 3 ×15, 4 ×15. Per task e lato: blue — CAS 27, Ground Attack
24, Pinpoint Strike 8, Refueling 6, Fighter Sweep 3, Escort 3, Antiship Strike 3, AWACS 2,
Intercept 1; red — CAS 25, Ground Attack 21, Escort 10, SEAD 10, CAP 9, Intercept 7,
Pinpoint Strike 4, AWACS 2, Transport 2, Fighter Sweep 1.

### 6.2 Numero di waypoint per categoria — veicoli fermi o con rotte?

| Categoria | gruppi | min | media | max | distribuzione |
|---|---:|---:|---:|---:|---|
| plane | 168 | 1 | 8,9 | 14 | 10 punti ×85, 6 ×19, 9 ×10, 7 ×10, 13 ×9, 1 ×8 |
| helicopter | 5 | 2 | 4,0 | 7 | 2 ×3, 7 ×2 |
| **vehicle** | **110** | **1** | **1,0** | **1** | **1 punto ×110** |
| ship | 6 | 2 | 4,2 | 7 | 4 ×4, 2 ×1, 7 ×1 |
| static | 274 | 1 | 1,0 | 1 | 1 punto ×274 (vuoto) |

**Conferma e precisazione sui veicoli.** I 110 gruppi di veicoli hanno **tutti un solo
waypoint** (`action='Off Road'`, `speed` 0 nel 60%, 5,56 m/s nel 31%, 4 m/s nel 9%: valori
irrilevanti con un solo punto): nessun veicolo ha una rotta. Per questo la parte "nessuna
rotta" è confermata. **Ma "solo difesa aerea" è vero solo in parte.** Classificando i 552
veicoli per tipo (classificazione mia, v. nota):

| Classe | blue | red | totale | Esempi |
|---|---:|---:|---:|---|
| difesa aerea e supporto (SAM, AAA, radar EWR/SR/TR, posti comando) | 189 | 248 | **437** (79%) | ZU-23 ×86, Vulcan ×61, ZSU-23-4 ×35, Strela-1 ×33, S_75M ×29, Roland ×30, Rapier ×36, Hawk ×13, Patriot ×13, Osa ×13, Kub ×12, S-125, EWR 1L13, p-19, SNR_75V |
| artiglieria e lanciarazzi | 28 | 28 | **56** (10%) | MLRS ×28, Uragan_BM-27 ×18, SAU Akatsia ×6, Grad_FDDM ×4 |
| logistica (camion, cisterne) | 10 | 17 | **27** (5%) | M 818, ZiL-131 APA-80, Ural-4320-31, ATZ-10, Ural-375 |
| fanteria e leggeri | 11 | 21 | **32** (6%) | Infantry AK ×19, M1043 HMMWV ×10, Hummer, BTR-80, Tigr |

Nota: ho incluso nella classe "difesa aerea e supporto" anche `SKP-11` (post comando) e
`Ural-375 PBU` (comando); sono mezzi di supporto alla difesa aerea. I gruppi sono 84
interamente di difesa aerea (36 blue + 48 red), 4 di sola artiglieria (red) e il resto
misti (es. "Artillery Division/Btry" con batteria + AAA di scorta).

Fatto notevole: i gruppi di artiglieria (MLRS, Uragan, ecc.) sono presenti **ma immobili e
senza task di fuoco**: `task='Ground Nothing'`. In questa missione il fronte terrestre non è
simulato in DCS: i veicoli sono difese puntiformi di basi, ponti, FARP e siti SAM (nomi
come `Tbilisi Defenses`, `Bridge Supply Line Gori - Tbilisi`, `Hawk Site Kutaisi`).

Le **navi** invece **si muovono**: 6 gruppi con rotte a 2-7 punti (convogli e
portaerei), velocità 5-8 m/s.

### 6.3 Modi di avvio dei gruppi aerei

Combinazioni `(hidden, lateActivation, uncontrolled)` dei 168 gruppi plane:

| hidden | lateActivation | uncontrolled | n | Interpretazione |
|---|---|---|---:|---|
| true | false | true | 63 | pack a terra, nascosti, avviati con `a_set_ai_task(Start)` |
| false | false | true | 37 | idem, visibili (pack del lato blu) |
| false | true | true | 23 | a terra, ad attivazione ritardata e avvio a comando |
| true | (assente) | false | 14 | partenza immediata (incluso intercettori/AWACS in volo) |
| true | true | false | 14 | in volo, ad attivazione ritardata (`a_activate_group`) |
| false | (assente) | false | 11 | partenza immediata |
| false | true | false | 6 | in volo, attivazione ritardata |

Primo waypoint dei plane: `TakeOffParking` ×100, `Turning Point` ×67 (partenza in volo, es.
scorte dei caccia e AWACS/tanker "Spawn" ×15), `TakeOffParkingHot` ×1 (il giocatore, F-14A su
portaerei). Gli 8 gruppi plane con un solo waypoint sono tutti `Intercept`: 7 intercettori rossi GCI (`Pack 3,4,5,7,8,9,10`, a terra, `uncontrolled`, avviati da `GCIscript.lua` via flag) e il pack 1 del giocatore (F-14A in partenza a caldo dalla portaerei).

### 6.4 Sistema di coordinate e unità di misura

Verificato sui dati:

| Grandezza | Unità | Evidenza |
|---|---|---|
| `x`, `y` | metri, coordinate della mappa DCS: **`x` verso nord, `y` verso est** | Batumi: `x=-355.692`, `y=617.270`; Tbilisi/Vaziani: `y≈903.150`. Nessuna latitudine/longitudine nel file. |
| `alt` | metri | piste a 1064-1979 m (quote reali dei campi del Caucaso), crociera 4000-9096 m |
| `alt_type` | `BARO` = quota sul livello del mare, `RADIO` = sul terreno | 57 punti `RADIO` (voli bassi, elicotteri) |
| `speed` | **m/s** | 250 m/s = 900 km/h per jet; 5,5556 m/s = 20 km/h per veicoli; 8 m/s = 15,5 nodi per navi |
| `heading`, `psi` | radianti (0 = nord) | valori tra 0 e 6,283 |
| `ETA`, `start_time` (gruppo), `stopCondition.time`, `c_time_after.seconds` | **secondi dall'inizio missione** (relativi a `mission.start_time`) | trigger 12: `c_time_after(2272.47)` = `start_time` del gruppo 100010 = ETA primo waypoint |
| `mission.start_time` | secondi dalla mezzanotte | 17476 = 04:51:16 = ora del briefing |
| `date` | giorno/mese/anno interi | `{Day=13, Month=9, Year=1975}` |
| `payload.fuel` | kg | 2280-11700 per i tipi osservati |
| `payload.gun` | percento | 100 |
| `frequency` di gruppo/unità aerea | MHz | 259,05 |
| `frequency` nei task (`SetFrequency`, `ActivateBeacon`) e unità navali | **Hz** | `382325000`, `127500000` |
| `weather.qnh` | mmHg | 774 |
| `weather.wind.speed` | m/s | 3; 7,5 |
| `season.temperature` | °C | 8 |
| `visibility.distance`, `clouds.base` | m | 80000; 2150 |
| trigger zone `radius` | m | 4,8768 |

### 6.5 Trappole di tipo (per un generatore Python)

- `payload.fuel` è **intero in alcune unità e stringa in altre** (`2280` e `'4864'`);
  `payload.pylons` è indicizzato dal numero di pilone e **`rate` degli statici** è intero o
  stringa (`100`, `'20'`).
- `callsign` è un **intero** oppure una **tabella** `{1,2,3,name}` a seconda dell'unità.
- `x`, `y` possono essere intero o float (`-277587` oppure `-355692.3067714`).
- Gli array Lua indicizzati da 1 possono avere **lacune** (`pylons[7]` ma non `[3]`).
- Le tabelle vuote (`['tasks'] = {}`) si usano sia per "lista vuota" sia per "oggetto vuoto".
- `coalition` è `'RED'/'BLUE'` negli aeroporti e `'red'/'blue'` in `warehouses` per FARP.
- `country[i]` ha indice sequenziale: il country id sta in `country[i].id`.

---

## 7. Gli script DCE e come generano la missione

### 7.1 Cosa fa ogni script (aggiunto da DCE sotto `l10n/DEFAULT/`)

| File | Ruolo (2-3 righe) | Aggancio |
|---|---|---|
| `camp_status.lua` | Globale `camp`: fotografia dello stato di campagna al momento della generazione (v. §7.3). Letta dagli altri script a runtime (`camp.CVN_Vmax`, `camp.mission_duration`, ...). | trigger 2 |
| `EventsTracker.lua` | `EventHandler:onEvent` registra a runtime gli eventi di gioco (distruzioni di statici, atterraggi, perdite) e li scrive su disco a fine missione (richiede `os`/`io` de-sanitizzati) → è l'unico canale di uscita. v. `ANALISI_DCE.md` §2.2. | trigger 3 |
| `AddCommandRadioF10.lua` | Aggiunge i comandi del menù radio F10 per il giocatore: RTB del pack, rifornimento di emergenza con S-3B, richiesta CAP, bullseye, ritiro aereo (`RemovePlane`, `AirRetreat`, `bingo`, `RequestCAP`, `ReFueling`). | trigger 4 |
| `GCIdata.lua` | Globale `GCI`: flag 507, tabelle `EWR` e `Interceptor[side].base[<base>].{ready,ready15,ready30,ready_n,...}` con gli intercettori pronti (nome volo, `airdromeId`, `range`, `flag`, `tot_from`, `tot_to`). | trigger 5 |
| `GCIscript.lua` | Controllo a terra: `GCI_Cycle()` ogni ciclo legge i radar EWR, individua i bersagli e avvia gli intercettori di `GCIdata` (via flag). | trigger 6 |
| `ARM_Defence_Script.lua` | I radar hanno una probabilità di rilevare un missile anti-radiazione in arrivo e si spengono (`ALARM_STATE`) per auto-protezione. | trigger 7 |
| `CustomTasksScript.lua` | Funzioni `CustomGroupAttack`, `CustomStaticAttack`, `CustomMapObjectAttack`, `CustomAirbaseAttack`, `CustomRejoin`, `CustomSearchThenEngage`, `OrbitPosition`, `CustomFlareAttack`, `CustomLaserDesignation` richiamate dai waypoint: sostituiscono i task di attacco editor (disabilitati) e creano i task `Bombing`/`AttackUnit` a runtime con quota e tipo di attacco. | trigger 8 |
| `CarrierIntoWindScript.lua` | `TurnIntoWind` / `ResumeRoute` / `CarrierIntoWind`: porta le portaerei in prua al vento per le operazioni di volo e poi riprende la rotta (parametri `camp.CVN_Vmax=10`, `camp.CVN_windDeck=9`). | trigger 9 |
| `Pedro.lua` | Mantiene l'elicottero di salvataggio "Pedro" (SH-60B) vicino alla portaerei nonostante i cambi di rotta (`camp.pedro[nave] = {bearing_from_leader_BaseMiss, distance_from_leader}`). | trigger 10 |

Tutti gli script sono "iniettati" con il meccanismo `mapResource` + `trig` + `trigrules`
descritto in `ANALISI_DCE.md` §4.2: per ogni script i trigger n.2-10 (`triggerStart`,
condizione `return(true)`, azione `a_do_script_file`).

### 7.2 `debugGenMission.txt` e `debugFlight.txt` — come nasce l'ATO

- `debugFlight.txt` ha una riga per ogni pack generato, nel formato
  `Pack: <n> Nb <numero velivoli> <tipo> <nome volo> <base di partenza> <obiettivo> ETA <s>
  StartT: <s> EtaWPT: <s> // <skill> Type: <tipo primo waypoint> [SOL/VOL decale_A <s>]`.
  Es.: `Pack: 2 Nb 3 F-4E Pack 2 - VMFA-151 - Strike 1 Batumi 203 SA-2 Site A-3 ETA 2407`.
  170 righe `Pack:` in `debugGenMission.txt` (una per gruppo).
- `debugGenMission.txt` aggiunge per ogni gruppo la sequenza delle decisioni dell'algoritmo
  `AtoFP` (ATO Flight Plan): `passe AA [ETA] > 0`, `passe BB unitname+FARP`, `passe 1B
  activate_group_time_after`, `passe 1C Start_set_ai_task`, `spawnOair AIR from: si
  multijoueur, les Flight AI commencent en vol`, `modify_activate_group_time` (con il numero
  del trigger toccato), "SUR PISTE DUR" (decollo da pista). In fondo c'è la sezione del
  giocatore: `startup_time_player: 00:15`, `NowTime: 04:51`, "CVN-71 Theodore Roosevelt
  Takeoff time on the platform at ... 04:49 - Pack 1 - 1 F-14A-135-GR - VF-101 - Intercept 1 -
  Player".
- L'algoritmo calcola per ogni pack: base di partenza, obiettivo (TOT) e ETA di ogni punto;
  poi sceglie il modo di avvio (da parcheggio con `a_set_ai_task`, oppure in volo con
  `a_activate_group`), sincronizza con le funzioni `OrbitPosition` e aggiorna
  `trig.conditions[n]` con il tempo di attivazione.

### 7.3 `camp_status.lua` — lo stato di campagna

Tabella `camp` (~1875 righe). Chiavi di primo livello osservate:

| Chiave | Tipo | Valore osservato | Significato |
|---|---|---|---|
| `title`, `version`, `MissionFilename`, `ScriptsMod`, `versionPackageICM`, `debug`, `path` | str/bool | `'1975 Georgian War'`, `'V0.1'`, `'1975 Georgian War_first.miz'`, `'20.47.105'`, `'NG'`, `false`, percorso `Saved Games/DCS.openbeta_server/` | metadati |
| `mission`, `day`, `variation` | int | 1, 1, 4 | contatore missione, giorno di campagna, variante |
| `date` | `{day, month, year}` | 13/9/1975 | data corrente |
| `time` | int | 17476 | ora di inizio (s dalla mezzanotte) |
| `mission_duration` | int | **5400** (1,5 h) | durata massima |
| `startup` | int | 900 | s tra l'inizio e l'avvio del giocatore |
| `idle_time_min` / `max` | int | 10800 / 14400 | intervallo di tempo morto tra le missioni (s) |
| `dawn`, `dusk` | int | 21600 / 65700 | alba/tramonto (s dalla mezzanotte) |
| `weather` | `{zone, zoneNext, zoneStart, zoneEnd, zoneTemp, zoneNextTemp, refTemp, pHigh, pLow}` | `high`, `19`, `20`... | stato del modello meteo di DCE |
| `units` | str | `'metric'` | |
| `CVN_Vmax`, `CVN_windDeck`, `CVN_despawnAfterLanding`, `SC_CarrierIntoWind` | | 10, 9, true, `'man'` | parametri portaerei |
| `radio` | `{blue, red}` | bande `UHF` 225-390/399, `VHF` 108-173, `FM` 20-59,97 | piano frequenze per lato |
| `pedro` | | 3 portaerei | posizione relativa dell'elicottero SAR |
| `ShipMissions` | `{nome gruppo = {StartTime, PatrolSpeed, CruiseSpeed, WPtable={{zone...}}}}` | 6 gruppi | rotte navali |
| `aircraft_availability` | `{squadriglia = {assigned, available, unassigned, unavailable[], serviceable, ready, ...}}` | 59 squadriglie | **inventario aerei** (cosa è disponibile/assegnato/in riparazione, con i tempi di rientro in servizio in secondi dalla mezzanotte, es. 75076) |
| `player` | | `pack`, `flight`, `tgt_side`, `role`, `airbase`, `unitname`, `target`, ... | scheda del giocatore e del suo pack (include una copia completa del gruppo e dei waypoint) |
| `MultiPlayer`, `BaseAirStart`, `flag` | | vuote | |

Il blocco `player.target` mostra come DCE rappresenta un obiettivo:
`{TitleName='CVN-71 Theodore Roosevelt Alert', task='Intercept', base='CVN-71 ...',
priority=7, radius=250000, firepower={min=2,max=2}, attributes={}, ATO=true}`.

Il resto dello stato (oob_air, targetlist, ecc.) è descritto in `ANALISI_DCE.md` §3.

---

## 8. Rilevanza per Warfare-Model

### 8.1 Cosa deve produrre il nostro modello per generare un `.miz`

L'insieme **minimo** di dati per una missione giocabile è ristretto; quasi tutto il peso del
file (i 3,6 MB) è boilerplate ripetuto. Per ogni elemento indico il campo del file e se lo
deve decidere il modello (M), derivarlo da un catalogo (C) o lasciarlo di default (D).

| Dato | Campi | Origine |
|---|---|---|
| Teatro, data, ora | `theatre`, `date`, `start_time` | M (dal tempo di campagna/simulazione) |
| Meteo | `weather.{temperature, qnh, wind, clouds, visibility, fog, ...}` | M (serve un modello meteo → `Meteo_Analysis.py`); tutti gli altri campi di `weather` D |
| Coalizioni e paesi | `coalition[side].country[].{id,name}`, `coalitions` | C (dal catalogo dei paesi) |
| **Aerei: gruppo** | `name`, `task`, `x,y`, `start_time`, `uncontrolled`, `lateActivation`, `hidden`, `frequency`, `groupId` | M (`task` = tipo di missione; `start_time`/modo di avvio = decisione di pianificazione) |
| **Aerei: rotta** | `points[]` con `x,y,alt,alt_type,speed,type,action,ETA,airdromeId,name` | M (calcolata dal Route Manager; la lista di `name` dei punti è convenzione) |
| **Aerei: task ai waypoint** | `ControlledTask(Orbit/EngageTargets/...)`, `WrappedAction(Option)`, `Script(Custom*)` con bersaglio, `expend`, `weaponType`, `attackType`, `attackAlt` | M (bersaglio e armamento da usare) + C (funzioni Lua da un set fisso) |
| **Aerei: unità** | `type`, `skill`, `payload.{fuel,pylons[CLSID],flare,chaff,gun}`, `livery_id`, `onboard_num`, `callsign`, posizione | M (tipo, numero, skill, carico) + C (CLSID dal catalogo armi; carburante in kg) + D (`psi`, `heading`, `hardpoint_racks`, `livery_id=''`) |
| Elicotteri | come aerei con `alt_type='RADIO'` | M |
| **Veicoli** | gruppo con 1 punto (posizione) + unità `type`, `skill` | M (posizione, tipo, numero) + D (tutto il resto, rotta fittizia a un punto, `task='Ground Nothing'`) |
| **Navi** | rotta con 2-7 punti, velocità m/s, eventuali `ActivateBeacon`/`ActivateICLS` per le portaerei | M (rotte), C (TACAN/ICLS) |
| **Statici** | un oggetto per gruppo, `type`, `category`, `shape_name`, posizione, `heading` | M (cosa c'è e dove) + C (shape_name dal catalogo) |
| Trigger | 1 trigger a tempo per gruppo (`c_time_after` + `a_set_ai_task` o `a_activate_group`) | M (tempo) + D (forma del trigger) |
| Briefing | `sortie`, `descriptionText/BlueTask/RedTask`, ATO | M (testo) |
| Warehouse | 1 voce per aeroporto/FARP | D (tutto illimitato) oppure M se si vuole simulare la scarsità (dipende dalle scelte di §8.3) |
| Obiettivi/punteggio | `goals`, `result` | D (valore fisso) o M se si vogliono obiettivi reali |

### 8.2 Cosa è "stato del mondo" (va nella persistenza del nostro modello)

È ciò che cambia da missione a missione e che quindi **non può essere un default**:

1. **Posizioni e identità** di ogni asset, statico o mobile (i 563 gruppi/1173 unità di
   questa missione sono la rappresentazione per-unità del nostro stato di mondo).
   La corrispondenza è col nostro `Asset`/`Military`: per ogni asset servono `type` DCS,
   coordinate (x nord, y est in metri), `heading` (rad), `skill`.
2. **Disponibilità degli aerei per squadriglia** (59 squadriglie in `aircraft_availability`):
   assegnati, disponibili, in manutenzione con istante di ritorno in servizio. È il vero
   inventario: il file `warehouses` di DCS è vuoto/illimitato.
3. **Rotte e velocità delle navi** (nostro `DataType.Route/Waypoint`) con tempi di
   partenza.
4. **ATO**: l'elenco pack → obiettivo → TOT → base → squadriglia → composizione/armamento
   (il blocco "Air Tasking Order: Sorties Mission TOT" del briefing).
5. **Tempo**: data, ora di inizio, durata massima (5400 s), tempo morto (10800-14400 s),
   alba/tramonto.
6. **Meteo** al momento dell'inizio.
7. **Stato di danno** degli oggetti (veicoli, statici, scenario distrutto): oggi DCE lo
   scrive nella `.miz` rigenerando i gruppi con le sole unità superstiti e
   distruggendo lo scenario via trigger zone (`a_scenery_destruction_zone`, qui assente).
8. **Frequenze e callsign** per lato (piano radio in `camp.radio`).

### 8.3 Cosa si può lasciare di default

- Tutto `options`, `forcedOptions`, `failures` (tutti off), `groundControl`, `map`.
- `warehouses` (21 aeroporti + 36 FARP): copiare il template e mettere `unlimited*=true`,
  `OperatingLevel_*=10`, `InitFuel=100`, a meno che si voglia simulare rifornimento reale.
- Le 36 zone di trigger: servono solo come segnaposto di coordinate per le rotte
  navali/orbite.
- Proprietà di waypoint costanti: `properties={angle=0, scale=0, steer=2, vangle=0, vnav=1}`,
  `formation_template=''`, `ETA_locked`/`speed_locked` (regole d'uso fisse),
  `modulation=0`, `communication=true`, `psi=0`.
- `dictionary` e `mapResource` (a parte le righe che puntano agli script).
- Per i veicoli: nessuna rotta, un solo punto `Off Road` con `speed=0`.
- `tasks` dei gruppi (a parte `Start` per quelli `uncontrolled`).

### 8.4 Implicazioni di progetto

1. **Il fronte terrestre non è simulato in DCS** in questa missione: i veicoli sono difese
   puntiformi (tutti a un solo waypoint, 79% difesa aerea/supporto). Questo coincide con il
   confine del nostro modello: la "guerra terrestre" resta nel DES/Python e DCS riceve solo
   una fotografia statica dei dispositivi di difesa. Se in futuro si volessero colonne in
   movimento, andrebbe esteso il generatore con rotte a più punti (`On Road`/`Off Road`) per
   i veicoli — oggi non c'è alcun esempio nel file di come DCE le scriva.
2. **Il cuore da generare sono i pack aerei**: ~9 waypoint con profilo standard
   (`Departure/Join/Nav/IP/Attack/Egress/Split/Land`) più task `Script` custom. Il nostro
   `Route_Adapter`/`calcCanonicalRoute` produce già la geometria; mancano il profilo dei
   nomi/azioni, `ETA` per punto e i task finali.
3. **I task di attacco "veri" sono Lua custom, non task editor**: per generare missioni
   equivalenti serve (a) scrivere `WrappedAction`/`Script` con le chiamate `Custom*` e
   (b) includere `CustomTasksScript.lua`, oppure usare i task editor standard
   (`AttackGroup`/`AttackMapObject` abilitati) e perdere il controllo fine di quota e tipo
   di attacco. Decisione da prendere (coerente col vincolo "core indipendente dal simulatore, adapter DCS per ultimo").
4. **La temporizzazione è a trigger a tempo**: per ogni gruppo occorre calcolare i secondi
   dall'inizio della missione. Il DES di Warfare-Model ha già i tempi: servono mappati sul
   tempo di missione DCS, tenendo conto di `start_time` (s dalla mezzanotte) e `startup` del
   giocatore (900 s).
5. **Carichi**: servono i **CLSID** DCS (53 distinti qui) e il carburante in kg come
   stringa/intero; il nostro catalogo armi (`Aircraft_Loadouts`, `Weapon_Stores`) dovrà
   avere questo campo per ogni armamento disponibile sul pilone.
6. **Identità**: `groupId`/`unitId` devono restare stabili tra missioni per far
   corrispondere le perdite del debrief alle nostre entità (v. `COMPRENSIONE_PERSISTENZA_DCS.md`
   §1.5). In questa missione i gruppi generati da DCE hanno `groupId` ≥ 100000, quelli
   dell'editor sono < 1000.
7. **Versione**: la `.miz` analizzata ha `version=19` (DCS 2.7). Con DCS più recenti il file
   dichiara 22-23; i campi sono additivi, ma il generatore deve scegliere la versione di
   schema di destinazione (v. `ANALISI_DCE.md` §4.1 per pydcs).
8. **Scala**: 563 gruppi e 1173 unità danno 3,6 MB. Una generazione "completa" dal nostro
   modello va fatta da template + serializzatore Lua (le tabelle sono letterali), non
   scrivendo il file a mano.

### 8.5 Domande aperte da verificare

- Come scrive DCE un gruppo di veicoli **con rotta reale** (colonna): non è in questo
  campione. Serve un'altra `.miz` della stessa campagna dopo qualche giorno di gioco.
- Valore dei campi non decodificati: `weaponType` (maschere 2032, 4161536, 30720; sono
  maschere di `Weapon.flag` di DCS, ma non le ho decodificate), `type=131584` e `type=4`
  nelle azioni TACAN/ICLS, `formationIndex`/`variantIndex`.
- `periodicity`, `speed`, `size` dei warehouse: sono i default di DCS, non c'è prova in
  questo file del loro effetto con `unlimited*=false`.
- Mapping `airdromeId` → nome campo: nel file compaiono solo gli id (13, 16, 20, 22-29, 31,
  32 nei waypoint dei plane); i nomi vanno ricavati da `debugGenMission.txt` o dal catalogo
  del Caucaso (non verificato).
