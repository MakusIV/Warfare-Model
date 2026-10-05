# Informazioni necessarie per definire una missione (aerea, terrestre, navale)

**Stato**: ANALISI (2026-10-05, aggiornata con la missione di prova terra/mare e con le decisioni di `Proposta_Struttura_Missione_Decisioni.md`), primo passo della struttura `Mission` (attività A4 / P1 di
`Analisi_Modello_Missione_Sessione.md`). Nessun file di codice modificato.
**Scopo**: stabilire quali dati compongono una missione nel modello di Warfare-Model. Il modello deve
poterla eseguire nel motore DES sintetico e, in un secondo momento, esportarla verso DCS senza perdere
informazioni. Vale il vincolo simulator-agnostic: le informazioni sono di **dominio**. DCS serve come
banco di prova per capire quali informazioni servono davvero, non come formato da copiare.
**Uso di questo documento** (indicazione dell'utente, 2026-10-05): le informazioni DCS sono uno **spunto**
per individuare i dati necessari a definire le missioni, indipendentemente dalla struttura DCS. Verranno
riusate per i moduli di conversione/interfaccia fra il nucleo e i simulatori (DCS per primo) solo
**dopo** aver definito l'intera struttura del DES (territorio e mappe, sessioni, missioni) e completato
il motore.

**Fonti** (estratti in `Analysis/Document/documentazione missioni dcs/estratti/`):

| Sigla | Fonte | Estratto |
|---|---|---|
| **[M p.N]** | `DCS_User_Manual_EN_2020.pdf`, capitolo Mission Editor pp. 84-357 (testo e figure) | `Manuale_ME_parte1_pp084-174.md`, `..._parte2_pp175-247.md`, `..._parte3_pp248-286.md`, `..._parte4_pp287-357.md` |
| **[F]** | 22 foto del Mission Editor sulla missione `1975 Georgian War_first.miz` | `Foto_Mission_Editor.md` |
| **[Z]** | `1975 Georgian War_first.miz`: missione reale generata da DCE, analizzata con `lupa` | `Struttura_File_MIZ.md` |
| **[R]** | `DCS_GND_Charts.pdf` (aeroporti) e `DCS World List of all available Beacons EN.pdf` (radioaiuti) | `DCS_GND_Charts.md` + `DCS_Aeroporti_Caucaso.csv`, `DCS World List of all available Beacons EN.md` + `DCS_Beacons_Caucaso.csv` |
| **[C]** | codice del repository, verificato leggendolo | — |
| **[T]** | `ground_sea_mission.miz`: missione di prova dell'utente con carri, artiglieria e navi che attaccano | `Struttura_Missione_Terra_Mare.md` |
| **[I]** | mia inferenza o conoscenza generale, **non verificata** sulle fonti | — |

---

## 0. Sintesi

1. **Una "missione" DCS non è la nostra Missione.** In DCS la *missione* è l'intero file `.miz`, cioè
   la nostra **Sessione**. Ciò che noi chiamiamo Missione corrisponde in DCS a un **gruppo** (1-4 aerei;
   1-99 veicoli o navi [M p.287]) con una rotta, un task e una lista di azioni. Un'operazione composta,
   come strike + scorta + SEAD sullo stesso bersaglio, è in DCE un **pack** di più gruppi coordinati
   dallo stesso TOT [Z §7.2]. Il modello distingue quindi tre livelli, con la terminologia del
   documento originale dell'utente (decisione D3, `Proposta_Struttura_Missione_Decisioni.md`):
   **Sessione ⊃ Operazione (facoltativa: missioni di blocchi diversi con uno scopo comune) ⊃
   Missione (asset di un solo blocco, ruoli, direttive, una rotta di riferimento)**. La Missione
   corrisponde al gruppo DCS, l'Operazione al pack DCE.
2. **Struttura comune ai tre domini.** In tutti e tre i domini una missione si descrive con gli stessi
   cinque blocchi:
   - **chi**: composizione della missione;
   - **quando**: istante di inizio e modo di attivazione;
   - **dove**: rotta temporizzata;
   - **cosa fare e come**: azioni ai waypoint e regole di comportamento;
   - **con cosa**: carico, ma solo per gli aerei.

   Cambia il contenuto di ogni blocco, non la forma. Lo confermano il pannello gruppo, il pannello
   waypoint e l'editor delle azioni, uguali per le tre categorie salvo i campi specifici [M parte 4 §A].
3. **Il comportamento in DCS sta nelle azioni ai waypoint.** Il task del gruppo (CAP, CAS, Strike...)
   è **solo un filtro** sulle azioni e sui carichi ammessi [M p.221]. Ciò che il gruppo fa davvero è
   la lista ordinata di azioni di ogni waypoint, di quattro tipi:
   - Perform Task;
   - Start Enroute Task;
   - Perform Command;
   - Set Option.

   Ogni azione ha priorità, condizione di avvio e condizione di arresto. Si eseguono con le regole
   "Task prima di Enroute" e "un solo Task alla volta"; il Task sospeso va in pila [M parte 2 §6.1].
   Per il nostro modello: la Missione deve portare **azioni con condizioni**, non solo un tipo.
4. **Bersagli espliciti in tutti e tre i domini** (verificato sulla missione di prova [T]).
   - **Aria**: attacca *quel* bersaglio con *quell'*arma da *quella* direzione e quota.
   - **Terra e mare**: un gruppo può ricevere un bersaglio esplicito. I tipi sono due:
     - `AttackGroup` su un gruppo nemico (carri contro carri, navi contro navi), con gli stessi
       parametri del task aereo;
     - `FireAtPoint` su un punto o un'area (artiglieria, carri, navi contro un bersaglio a terra).

     In assenza di bersaglio il gruppo ingaggia ciò che entra in portata, secondo ROE e Alarm State.

   Il manuale del 2020 documentava per i veicoli solo Fire at Point e Hold: su questo punto è
   superato. La supposizione dell'utente era corretta. Ne segue che la missione terrestre e navale
   porta **sia** intenzione e regole **sia** bersagli espliciti opzionali (§4, §5).
5. **Il campione DCE conferma il ricordo dell'utente, con una precisazione.** Nel `.miz` i 110 gruppi
   di veicoli hanno **un solo waypoint**: sono fermi e senza task di fuoco. Però solo il 79% delle unità
   è difesa aerea o supporto: il 10% è artiglieria ferma, il resto logistica e fanteria [Z §6, §8.4].
   Le 6 navi invece si muovono (2-7 waypoint). Il fronte terrestre DCE non è simulato in DCS: resta
   nel motore esterno. È lo stesso confine del nostro DES.
6. **Munizioni e carburante sono dati di missione solo per gli aerei.**
   - **Aerei**: il carico, il carburante % e chaff/flare si decidono per missione.
   - **Veicoli e navi**: le munizioni sono fisse per tipo. Il pannello "Ammo" sceglie solo la livrea.
     Il rifornimento è una regola di mondo: un supply vehicle entro 200 m è un magazzino illimitato,
     con tempi di ricarica in secondi per arma [M pp.316-325].

   La nostra `Weapon_Stores` per modello d'arma copre già la parte di asset.
7. **I criteri di fine missione esistono in DCS e sono quelli della decisione 2.**
   - Le opzioni `RTB on Bingo Fuel` (default ON) e `RTB on out of ammo` (winchester per categoria
     d'arma) [M parte 3].
   - La condizione di arresto per durata, flag o ultimo waypoint.
   - L'aborto per minaccia (`Reaction to Threat = Allow Abort Mission`).
   - Il waypoint `Land`.
8. **Le informazioni di sessione non stanno nella Missione.** Data e ora, meteo, coalizioni,
   bullseye, zone, magazzini e basi, obiettivi a punteggio e trigger vanno nella Sessione o nello
   stato di campagna.
9. **Registri della mappa (Caucaso).** Dai due PDF ho ricavato:
   - un registro di 21 aeroporti: ICAO, ARP, quota, piste con dimensioni e prue magnetiche e vere,
     torre, TACAN, ILS;
   - un registro di 214 radioaiuti.

   Sono la base per un registro `Airbase`. Manca la chiave di collegamento a DCS (`airdromeId`), che
   nessuna delle fonti dà (§9).

---

## 1. Modello concettuale (aggiornato con le decisioni D3 e N2 del 2026-10-05)

```
Sessione (= file .miz in DCS)
 ├─ dati di sessione: finestra temporale, data/ora, meteo, coalizioni, zone, bullseye, obiettivi
 ├─ stato di mondo in ingresso: asset e posizioni, basi e magazzini, danni (da Campaign_State)
 ├─ Postura continua  (asset senza missione: SAM, EWR, depositi, statici)  -> §7
 └─ Operazione [facoltativa]  (scopo comune, TOT comune, regola d'esito)
     └─ Missione [1..n]  (asset di UN blocco; = gruppo DCS: un volo, una colonna, una formazione navale)
         ├─ intestazione: id, dominio, tipo, obiettivo/bersaglio, priorità, TOT/finestra, criteri di fine
         ├─ composizione: asset_id, tipo, ruolo per asset, offset di formazione, esperienza/skill
         ├─ avvio: istante, modo (pista/parcheggio freddo/caldo/in volo/a terra), attivazione
         ├─ rotta di riferimento (geometrica, DataType.Route) + MissionWaypoint per punto:
         │    ETA pianificata, ruolo del punto, tipo di quota, azioni (anche "attendi")
         ├─ azioni per waypoint: compito / regola / comando, con priorità e condizioni pre-calcolabili
         ├─ regole: ROE, reazione alla minaccia, EMCON, formazione, RTB bingo/winchester
         └─ carico (solo aria): arma per stazione, carburante %, contromisure
```

Corrispondenze con il codice esistente [C]:

| Blocco | Già nel progetto | Cosa manca |
|---|---|---|
| Rotta | `DataType.Route/Edge/Waypoint` (rotta canonica); `Edge.path_type` = `onroad`/`offroad`/`air`/`water`, `Edge.speed` | ETA per waypoint, tipo di quota (MSL/AGL), **ruolo del punto** (decollo, IP, attacco, atterraggio...): `Waypoint` ha solo `point`, `name`, `reference`. Decisione N2.a: nuovo tipo `MissionWaypoint` che contiene un `Waypoint` |
| Profilo d'attacco | `Command/Attack_Types.AttackProfile` (IP, punto di sgancio, uscita, azimut, quota e velocità di sgancio, arma, quantità) | è già "un attributo della futura `Mission`" (docstring) |
| Carico | `Aircraft.assigned_loadout`, `Weapon_Stores` (scorta per modello d'arma), `Fuel_Model` | carburante iniziale come scelta di missione; codici di stazione |
| Tipo di missione | `Context.Air_To_Air_Task` / `Air_To_Ground_Task` (CAP, Fighter_Sweep, Intercept, Escort, Recon, CAS, Strike, Pinpoint_Strike, SEAD, Anti_Ship), `Ground_Action`, `Sea_Task` | supporto (AWACS, Tanker, Transport), compiti terrestri reali (§5) |
| Regole | `Doctrine.DEFAULT_FIRE_DOCTRINE`, soglia di rottura, posture | ROE, EMCON, reazione alla minaccia per missione |
| Contenitore | **nessuno**: la missione vive solo come `routes`/`starts`/`speeds` di `run_session`, e `SessionOrder` non la trasporta (P1) | l'entità `Mission` stessa |

---

## 2. Informazioni comuni ai tre domini

Ogni riga dice cosa serve, perché serve e dove DCS lo esprime. **Obbl.** = senza questo dato la
missione non è definita.

### 2.1 Intestazione della Missione

| Informazione | Obbl. | Note | In DCS |
|---|---|---|---|
| `mission_id` | sì | stabile fra pianificazione, sessione ed esito; serve anche a `Session_Rng` (slot `mission_id` già previsto) | nessun equivalente: DCE usa il numero di pack e il nome del gruppo [Z] |
| dominio | sì | aria, terra, mare | categoria del gruppo |
| tipo di missione | sì | vincola carichi, azioni e criteri di fine | `task` del gruppo (filtro) [M p.221] |
| obiettivo/bersaglio | sì, salvo trasferimenti | id di dominio: asset, gruppo, punto, zona o infrastruttura | parametro dei Perform Task (Attack Group/Unit/Map Object, Bombing...) [M parte 2] |
| TOT o finestra sull'obiettivo | sì per attacco/supporto | sincronizza le missioni di un'Operazione | DCE: ETA del punto `Attack` più attesa `OrbitPosition(..., untilTime)` [Z §4.4] |
| priorità | sì | serve a scegliere fra missioni e risorse | DCE: `target.priority` [Z §7.3] |
| criteri di fine | sì | (a) geometrici: ultimo waypoint, atterraggio; (b) a tempo: durata, tempo sulla stazione; (c) di stato: bingo, winchester, bersaglio distrutto, aborto per minaccia o danno | Land waypoint; stop condition `DUR`/`LAST WPT`/flag; opzioni RTB [M parte 2-3] |
| coalizione/lato | sì | | `country` → coalizione [M p.87] |

### 2.2 Composizione della missione (gruppo)

| Informazione | Obbl. | Note | In DCS |
|---|---|---|---|
| `mission_id` (gruppo), nome | sì | univoco nella sessione; deve restare stabile per ricondurre le perdite del debrief alle entità | `groupId`/`unitId`, `name` [Z §8.4 p.6] |
| tipo di asset e numero | sì | aria 1-4 per gruppo; terra/mare 1-99 [M p.287] | `type` per unità |
| asset_id delle unità | sì | collegamento a `Asset` e alle scorte | `unitId`, `name` |
| esperienza (skill) | sì | Average/Good/High/Excellent/Random; "Veteran" e "Trained" appaiono nelle foto (moduli recenti) [F] | `skill` per unità |
| posizione e prua iniziali | sì per terra/mare/statici | aria: dalla base di partenza | `x`, `y` (m, x verso nord), `heading` (rad) [Z] |
| probabilità di presenza | no | "spawn" casuale | campo `%` della CONDITION del gruppo (default 100) [M parte 2, F] |

### 2.3 Avvio e attivazione

| Informazione | Obbl. | Note | In DCS |
|---|---|---|---|
| istante di inizio | sì | secondi dall'inizio della sessione (convenzione di `SessionOrder`) | = ETA del primo waypoint (con lock) [M parte 2]; `start_time` in s dall'inizio missione [Z] |
| modo di attivazione | sì | presente dall'inizio; attivato a un istante; attivato da un evento (rinforzo, reazione) | `lateActivation` + trigger `TIME MORE` → `GROUP ACTIVATE`, oppure `uncontrolled` + `AI TASK Start` [Z §4.3, F]; in alternativa ETA a +100 giorni |

### 2.4 Rotta temporizzata

| Informazione | Obbl. | Note | In DCS |
|---|---|---|---|
| sequenza di waypoint (posizione) | sì | già in `DataType.Route` | `route.points[]` con `x`, `y` |
| quota e riferimento | aria | MSL o AGL. Terra e mare: non regolabile, segue il terreno o il mare [M parte 4 §A] | `alt`, `alt_type` = `BARO`/`RADIO` |
| velocità per tratto | sì | velocità al suolo del tratto che **termina** nel waypoint. Unità di dominio km/h, come il ME; DCS interno m/s | `speed` (m/s), `speed_locked` |
| ETA per waypoint | sì | **manca oggi** nel nostro `Waypoint`. Il DES la calcola; deve diventare un dato della missione. In ogni terna distanza/velocità/tempo, due grandezze determinano la terza; serve almeno un ETA bloccato [M pp.180-188] | `ETA`, `ETA_locked` |
| ruolo del punto | sì | decollo, raduno, navigazione, IP, attacco, uscita, separazione, atterraggio, stazione, orbita | `type`/`action` più nomi DCE `Departure/Join/Nav/IP/Attack/Egress/Split/Land/Station` [Z §4.2] |
| modo di movimento | terra | fuori strada / su strada / formazione (§5) | `action` = `Off Road`, `On Road`, `Cone`... [M parte 4] |

### 2.5 Azioni e regole

| Informazione | Obbl. | Note | In DCS |
|---|---|---|---|
| azioni per waypoint, ordinate | sì | tipo (Task / Enroute / Comando / Opzione), parametri, priorità (0 = massima), abilitata | `ComboTask.params.tasks[]` [Z §4.3] |
| condizione di avvio di un'azione | no | OR di: tempo > t, flag, probabilità, predicato | `CONDITION...` [M parte 2, F] |
| condizione di arresto | no (solo Task/Enroute) | tempo > t, flag, predicato, **durata**, ultimo waypoint | `STOP CONDITION...` (+ `DUR`) [F]; `ControlledTask.stopCondition` [Z] |
| azioni scatenate da eventi | no | indipendenti dalla rotta, con priorità superiore | Triggered Actions + trigger `AI TASK PUSH/SET` [M parte 2] |
| ROE | sì | aria 5 livelli: Weapon Free, Priority Designated, Only Designated (default), Return Fire, Weapon Hold [M pp.276-277]; terra e mare 3 livelli [M parte 4] | opzione ROE |

Una conseguenza per il DES. Le azioni con condizioni (orbita fino a un istante, attesa di un flag,
arresto dopo una durata) sono l'equivalente DCS della **R4 seconda parte** (ri-pianificazione), oggi
rimandata. Le condizioni calcolabili prima della sessione (tempo, durata, ultimo waypoint) si
modellano senza re-scheduling. Quelle sullo stato (flag, bersaglio distrutto) no. È la stessa linea di
demarcazione della decisione 2.

---

## 3. Missione aerea (e elicotteri)

Oltre ai dati comuni (§2):

### 3.1 Composizione e avvio

| Informazione | Obbl. | Note / valori | Fonte |
|---|---|---|---|
| tipo di missione | sì | DCS ha 16 task di gruppo: Nothing, AFAC, Anti-ship Strike, AWACS, CAP, CAS, Escort, Fighter Sweep, Ground Attack, Intercept, Pinpoint Strike, Reconnaissance, Refueling, Runway Attack, SEAD, Transport. Ai nostri 10 tipi mancano almeno AWACS, Tanker, Transport, Runway Attack, AFAC | [M parte 2], [C] `Context.py:378-391` |
| base di partenza e di arrivo | sì, salvo avvio in volo | aeroporto, FARP o portaerei | `airdromeId`/`helipadId`/`linkUnit` nel primo e nell'ultimo waypoint [Z] |
| modo di avvio | sì | pista; parcheggio a motori spenti; parcheggio a motori accesi; da terra (elicotteri, FARP); in volo | tipo del WP1: `TakeOffParking`, `TakeOffParkingHot`, `Turning Point` per il volo [Z §4.5] |
| `uncontrolled` | no | presente sul parcheggio ma inattivo fino al comando `Start`. **È il modo per avere aerei parcheggiati colpibili** (P3 della decisione 1) | [M parte 2, F, Z] |
| ruoli di formazione | no | capo formazione e gregari; formazione e variante | opzione Formation [F] |

### 3.2 Rotta tipo

Il profilo misurato su 85 pack d'attacco DCE è `Departure → Join → Nav → AI Descend Helper → IP →
Attack (Fly Over Point) → Egress → Nav → Split → Land`, con circa 9-10 punti [Z §4.2]. Il nostro
`AttackProfile` copre già il tratto `IP → sgancio → uscita` e, con `full_route`, base → IP e uscita →
base [C]. Mancano i punti di raduno e separazione, l'ETA per punto e il ruolo del punto.

### 3.3 Compito sull'obiettivo (Perform Task / Enroute)

| Informazione | Note | Fonte |
|---|---|---|
| bersaglio | gruppo, unità, statico, oggetto di mappa (coordinate), pista, zona | Attack Group/Unit/Map Object, Bombing, Bombing Runway [M parte 2] |
| arma autorizzata | categoria ad albero: Unguided > Cannon/Rockets/Bombs; Guided; ATGM... In DCS è una maschera di bit (`weaponType` 2032, 4161536, 30720 nel campione) | [M parte 3, Z §4.4] |
| quantità per passaggio | `expend`/REL QTY: nelle figure Auto, Two, All; menu disattivato con WEAPON = Auto. Gli altri valori DCS (One, Four, Quarter, Half) [I] | [M parte 2], [Z]: `expend` ∈ {All, Auto} |
| numero massimo di attacchi | MAX ATTACK QTY | [M parte 2] |
| attacco di gruppo | GROUP ATTACK (tutto il volo sullo stesso bersaglio) | [M parte 2] |
| direzione di attacco | DIRECTION FROM (azimut): è `AttackProfile.run_in_azimuth_deg` | [M parte 2], [C] |
| quota di attacco | ALTITUDE ABOVE: è `AttackProfile.release_altitude_m` | [M parte 2], [C] |
| modo di rilascio | livello, picchiata (DCE: `attackType = Dive`), loft: `AttackProfile.release_mode` | [Z], [C] |
| ricerca e ingaggio | Search Then Engage (+ in Zone / Group / Unit): categorie di bersaglio, distanza di ingaggio dalla rotta (km), raggio di zona (m), priorità | [M parte 3] |
| orbita / stazione | Orbit: cerchio o race-track, quota, velocità, lunghezza; si chiude al bingo | [M parte 2] |
| scorta | Escort: gruppo scortato, posizione relativa (distanza/quota/intervallo in m), ultimo waypoint, distanza minaccia-scortato che fa scattare l'ingaggio (km), tipi di minaccia | [M p.237] |
| supporto | AWACS, Tanker (task automatici del task di gruppo), Refueling (al carburante critico va al tanker amico più vicino, rifornisce e riprende la rotta) | [M pp.245-246, parte 3], [Z] |

### 3.4 Regole di comportamento (Set Option)

| Regola | Valori principali (default DCS) | Uso nel nostro modello |
|---|---|---|
| ROE | Weapon Free, Priority Designated, Only Designated (default), Return Fire, Weapon Hold | postura di fuoco della missione; "designated" = solo il bersaglio dell'azione |
| Reaction to Threat | No Reaction, Passive Defence, Evade Fire, Evasive Vertical Maneuver, **Allow Abort Mission** (default), Horizontal AAA Fire Evade | aborto per minaccia = criterio di fine (decisione 2) |
| Radar Using, ECM Using, Silence, Restrict Afterburner, Chaff-Flare Using | EMCON e firma emessa | volumi di rilevamento, AVOID_DETECTION, RWR |
| AA Missile attack ranges | Max range, No escape zone, Half way, By threat estimate (default), Random | regola di lancio di `Engagement_Resolver` |
| RTB on Bingo Fuel | ON (default) | criterio di fine "bingo" |
| RTB on out of ammo | per categoria d'arma (default nessuna) | criterio di fine "winchester" |
| Restrict A/A, A/G attack, Restrict Jettison | vincoli di ruolo | filtro armi per missione (A4) |

### 3.5 Carico (solo aria)

| Informazione | Note | Fonte |
|---|---|---|
| arma per stazione | DCS usa i codici CLSID: 53 distinti nel campione | [Z §8.4 p.5], [F] |
| carburante interno % | DCS lo converte in kg (`payload.fuel`); peso totale ≤ massimo | [F]: 5489 kg carburante, 448 kg armi, MAX 20000 kg |
| chaff/flare | quantità, con cartucce condivise | [M parte 2] |
| munizioni cannone % | | [M parte 2] |
| livrea, proprietà specifiche del modulo | solo esportazione (§10) | [F] |

Il carico va derivato dalla scorta per modello d'arma (`Weapon_Stores`, decremento all'assegnazione)
e da `Aircraft_Loadouts`. Per l'esportazione servirà il campo CLSID per ogni arma del catalogo.

---

## 4. Missione navale

Oltre ai dati comuni (§2):

| Informazione | Obbl. | Note | Fonte |
|---|---|---|---|
| tipo di missione | sì | i nostri `Sea_Task` sono Attack/Defense/Retrait; in DCS il gruppo navale non ha task di gruppo | [C], [M parte 4] |
| rotta | sì | solo waypoint "Turning Point", velocità in km/h nel ME (m/s nel file); la velocità del gruppo è limitata dalla nave più lenta | [M parte 4 §A], [Z]: 2-7 punti, 5-8 m/s |
| compito | no | `AttackGroup` su un gruppo navale (verificato: 4 REZKY contro 3 Arleigh Burke, a 4,5 km) e `FireAtPoint` su un punto a terra (verificato: tiro a 8 km su un bersaglio fisso). Parametri: arma, quantità, numero di attacchi, direzione; punto, raggio, colpi. Nessun Enroute Task | [M parte 4], [T] |
| ROE | sì | 3 livelli | [M parte 4] |
| Alarm State | sì | Auto / Green / Red. Red = sensori e armi pronti; Green = basso profilo | [M parte 4] |
| radioaiuti di bordo | portaerei | TACAN e ICLS (`ActivateBeacon`/`ActivateICLS`) | [Z §4.3] |
| operazioni di volo | portaerei | prua al vento durante decolli e appontaggi (DCE `CarrierIntoWind`) | [Z §7.1] |
| fornitori | no | relazione Suppliers (gruppo navale ← navi o aeroporti), senza raggi né quantità | [M pp.294-295] |
| frequenza radio | no | default 127,5 MHz AM | [M parte 4] |

Osservazione: in DCE le rotte navali sono **stato di campagna** (`camp.ShipMissions` con StartTime,
PatrolSpeed, CruiseSpeed e tabella dei waypoint) e non vengono ri-pianificate a ogni missione [Z
§7.3]. Una missione navale è spesso un **pattugliamento persistente** fra sessioni: va capito se
supera la regola "una missione per sessione" (decisione 4).

---

## 5. Missione terrestre

Oltre ai dati comuni (§2):

| Informazione | Obbl. | Note | Fonte |
|---|---|---|---|
| tipo di missione | sì | i nostri `Ground_Action`: Attack / Defense / Maintain / Retrait. In DCS non esiste un task di gruppo con significato: nel campione è `Ground Nothing` | [C], [Z §4.1] |
| rotta | sì se in movimento | il **tipo di waypoint fonde movimento e formazione**: Off Road, On Road, Line Abreast, Cone, Vee, Diamond, Echelon L/R, Custom. Distanza minima di 500 m fra gruppi sulla stessa strada | [M parte 4] |
| velocità per tratto | sì | km/h, limitata dal mezzo più lento; la quota non esiste | [M parte 4] |
| rete stradale | se On Road | dato di mappa (modulo mappe futuro); `Edge.path_type` già distingue `onroad`/`offroad` | [C] |
| bersaglio esplicito | no | **`AttackGroup`** su un gruppo (verificato: 4 T-90M contro il gruppo carri blu) e **`FireAtPoint`** su un punto o un'area (verificato per artiglieria trainata e semovente e per i carri). Parametri di Fire at Point: punto, raggio in m, limite di colpi, arma, raggio di controbatteria (campo nuovo, non nel manuale 2020) | [T], [M parte 4] |
| altri compiti | no | Hold, Go to Waypoint (cicli), Embark to Transport (solo fanteria, "work in progress"), FAC / FAC Engage Group (designazione) | [M parte 4] |
| ROE | sì | 3 livelli | [M parte 4] |
| Alarm State | sì | Auto / Green / Red | [M parte 4] |
| reazione al fuoco | no | Disperse Under Fire (secondi; 600 s nell'esempio) | [M parte 4] |
| ingaggio di armi aeree | difesa aerea | Engage Air Weapons: intercetta missili e bombe; corrisponde alla nostra regola D `Anti_Missile` | [M parte 4], [C] |
| schieramento | difesa aerea | template di unità complete (es. batteria Hawk) e "Stop and deploy to template" | [M parte 4], [M parte 1] |
| rifornimento munizioni | no (regola di mondo) | supply vehicle entro 200 m = magazzino illimitato; tempi di ricarica per arma (es. S-300PS 7200 s, Patriot 3600 s, Shilka 20 s) | [M pp.316-325] |

Osservazioni (dalla missione di prova [T], al livello di dominio):
- La missione terrestre porta **intenzione e regole** (avanzare, difendere, tenere, ritirarsi; ROE,
  allerta) e **bersagli espliciti opzionali** (gruppo, unità, punto o area). Senza bersaglio il
  gruppo ingaggia ciò che entra in portata: il nostro DES lo fa già (contatti analitici più
  `Engagement_Resolver` con dottrina di tiro).
- Il compito è legato a un waypoint: **posizione di tiro** = waypoint, **istante** = sua ETA. Per il
  fuoco indiretto è l'analogo dell'`AttackProfile` aereo e va verificato contro la gittata dell'arma.
  Nel campione: 14,1 km per il 2S3, 9,9 km per l'M2A1-105.
- Un **bersaglio di posizione invecchia**. L'artiglieria rossa colpisce il punto dove i blu erano
  all'inizio, e in quell'istante i blu sono già a 1,4-4,6 km. La missione deve registrare **su quale
  conoscenza** è stato scelto il bersaglio (asset osservato o posizione stimata, con istante), in
  coerenza con la nebbia di guerra (C).
- **L'ordine delle azioni** al waypoint è un dato: "tira e poi fermati", "fermati e poi attacca".

---

## 6. Elicotteri: differenze rispetto ai velivoli ad ala fissa

- Compiti esclusivi: Cargo Transportation, Embarking, Disembarking, Ground Escort, Land (con
  atterraggio in un punto qualsiasi) [M parte 2].
- Avvio da terra o da FARP; quota tipicamente `RADIO` (AGL) [Z].
- Il FARP è un oggetto statico (categoria Heliport) con callsign e frequenza. I veicoli di servizio
  entro 150 m abilitano rifornimento, riarmo e riparazione; la riparazione avviene 3 minuti dopo
  l'arresto dei rotori [M pp.313-314].

---

## 7. Asset senza missione: la postura continua

SAM, EWR, artiglieria ferma, depositi e infrastrutture non hanno una missione. Hanno una **postura**
valida per tutta la sessione: P7 di `Analisi_Modello_Missione_Sessione.md`. In DCS sono gruppi a un
solo waypoint (veicoli) oppure statici [Z].

| Informazione | Note | Fonte |
|---|---|---|
| posizione e prua | | [Z] |
| ROE, Alarm State | EMCON del sito: radar acceso o spento | [M parte 4] |
| EWR | il gruppo radar porta l'enroute task `EWR` | [Z §4.3] |
| statico | un oggetto per gruppo, flag `dead` (versione distrutta), nessuna azione. È il canale per infrastrutture, depositi, FARP e il loro stato | [M parte 4] |
| catena C2 | DCE la simula fuori dal modello di missione (`GCIscript` legge gli EWR e lancia gli intercettori pronti) | [Z §7.1] |

Il GCI di DCE mostra una cosa: l'**intercettazione su allarme** (aerei pronti a 5/15/30 minuti) è una
postura che diventa missione al verificarsi di un evento. Il nostro modello dovrà rappresentarla come
una missione con attivazione a evento (§2.3).

---

## 8. Dati di sessione (non della Missione)

| Informazione | Note | Fonte |
|---|---|---|
| teatro | Caucasus, Nevada, Normandy, Persian Gulf... | [M p.88], [Z] |
| data e ora di inizio | `start_time` in s dalla mezzanotte; alba e tramonto derivati | [Z §5, §7.3] |
| durata | DCE: 5400 s per missione, tempo morto fra missioni 10800-14400 s | [Z §7.3]: dato utile per la decisione 4 |
| meteo | statico: temperatura; una fascia di nubi (base 300-5000 m, densità 0-10, precipitazione); QNH in mmHg; vento a 10/500/2000/8000 m; turbolenza; nebbia; polvere. Dinamico: sistemi barici. **Uniforme su tutta la mappa** | [M pp.112-116]: uscita naturale di `Meteo_Analysis.py` |
| coalizioni | paesi assegnati a rosso e blu; gli altri non partecipano | [M p.87] |
| bullseye | uno per coalizione | [M p.349] |
| zone | solo circolari (raggio in m), anche ancorate a un'unità | [M parte 4] |
| obiettivi a punteggio | soglie fallimento ≤ 49, pareggio = 50, successo ≥ 51; stesso catalogo di condizioni dei trigger | [M p.171]: un solo modello di "Condizione" può servire obiettivi, trigger ed esito sintetico |
| magazzini e basi | per base: coalizione, aerei per tipo, carburante per tipo (t), armi per categoria, catena di rifornimento (velocità, periodicità, dimensione). DCE però li lascia **illimitati** e tiene l'inventario fuori (`camp.aircraft_availability`) | [M pp.99-105], [Z §5.1, §7.3] |
| cattura di basi | per presenza di unità terrestri entro 2000 m | [M parte 1] |
| briefing / ATO | testo per coalizione; DCE ci scrive l'ATO (sortite e TOT) | [F], [Z] |

---

## 9. Registri della mappa (Caucaso)

Ricavati da [R]:

- **`DCS_Aeroporti_Caucaso.csv`** (21 aeroporti). Per ognuno:
  - ICAO e nome;
  - ARP in gradi e primi decimali;
  - frequenza della torre, TACAN, ILS per testata;
  - piste con lunghezza e larghezza in m;
  - quota delle testate in m;
  - prue magnetiche e vere;
  - pagina della carta.
- **`DCS_Beacons_Caucaso.csv`** (214 radioaiuti di 67 località): tipo, frequenza o canale, banda,
  callsign, nazione, coordinate, note.

Campi proposti per un registro `Airbase` del modello:

| Campo | Da | Note |
|---|---|---|
| id di dominio, nome, ICAO | [R] | |
| posizione ARP, quota | [R] | da convertire nel sistema di coordinate del modello |
| piste: designazione, lunghezza, larghezza, prua | [R] | vincolo: lunghezza minima di decollo per tipo di aereo (dato di asset, oggi assente) |
| frequenze, TACAN, ILS | [R] | serve solo all'esportazione e al briefing |
| tipo | [M parte 1] | aeroporto di 1a/2a classe, FARP, portaerei |
| coalizione proprietaria | stato di campagna | cambia con la cattura |
| capacità di parcheggio e shelter | **manca** | le carte riportano solo le etichette (P1, S1...) |
| `airdromeId` DCS | **manca** | il `.miz` usa solo id numerici (13, 16, 20, 22-29, 31, 32); servirà una tabella id → ICAO (es. da `debugGenMission.txt` di DCE o da pydcs) |

Attenzione: le carte sono del **2013** (rev 3.6.0). Il Caucaso di DCS è cambiato da allora. Per i
dati che DCS usa davvero, la fonte primaria è il gioco stesso (o un `.miz` recente).

---

## 10. Cosa non serve al modello (solo interfaccia o solo esportazione)

- **Solo interfaccia**: colori, icone, pulsanti di editing, layer della mappa, kneeboard, riepilogo
  della rotta (valori derivati), cockpit trigger, messaggi, suoni, marcatori F10, helper gate.
- **Solo esportazione DCS** (il motore sintetico li ignora; l'adapter DCS dovrà generarli):
  - callsign, frequenze, tail number, nomi pilota;
  - livrea e proprietà specifiche del modulo;
  - Initial Point dell'A-10C, INU Fix Point, preset radio;
  - avarie (solo giocatore);
  - `dictionary`/`mapResource`;
  - versione dello schema `.miz` (19 nel campione, 22-23 nelle versioni recenti).
- **Trucchi di scenario, non dottrina**: Invisible, Immortal (utile solo per i test), Smoke, Run
  Script.

---

## 11. Conseguenze per le 6 decisioni aperte

Le decisioni sono in `Analisi_Modello_Missione_Sessione.md` §6. Qui riporto **cosa dicono le fonti**,
non una decisione.

| # | Decisione | Cosa aggiungono le fonti |
|---|---|---|
| 1 | Presenza a fine missione (P3) | DCS distingue già "inattivo ma presente": aerei `uncontrolled` sul parcheggio e statici. In DCE le unità terrestri restano ferme all'ultimo (unico) punto. Gli aerei dopo `Land` tornano al parcheggio [I: comportamento DCS non verificato sulle fonti; DCE ha l'opzione `CVN_despawnAfterLanding` solo per le portaerei]. Argomento a favore di "resta presente come bersaglio fermo". |
| 2 | Criteri di fine missione (P2) | DCS li ha tutti: geometrici (Land, ultimo waypoint), a tempo (DUR, TIME MORE), di stato (bingo, winchester, aborto per minaccia, flag). Quelli a tempo e geometrici sono calcolabili prima; quelli di stato sono **regole dell'IA eseguite durante la sessione**. Per l'adapter DCS basta dichiararli; il DES sintetico li deve simulare (R4 seconda parte). |
| 3 | Unità della missione (P6) | DCS e DCE separano **pacchetto** (pack: obiettivo e TOT comuni) e **gruppo** (rotta, task, fine). **Deciso (D3)**: Operazione = pacchetto, Missione = gruppo di asset di un blocco; fine e aborto per missione, con eccezioni individuali. |
| 4 | Durata e sovrapposizione delle sessioni (P5) | DCE: 5400 s di missione più 10800-14400 s di tempo morto, cioè finestre disgiunte; le rotte navali persistono fra sessioni come stato. È un riferimento concreto per la durata di una sessione virtuale. |
| 5 | Rifornimento in volo (P4) | DCS: il tanker è una missione (gruppo) con task `Tanker` (6 gruppi `Refueling` nel campione), il ricevente ha un Perform Task `Refueling`. È un evento interno alla missione che **dipende da un'altra missione** (dipendenza fra missioni). |
| 6 | Turnaround e numero di sortite | DCE tiene `aircraft_availability` per squadriglia: assegnati, disponibili, in manutenzione con istante di rientro in servizio. È un **pool di prontezza con tempi**; i magazzini DCS restano illimitati. Argomento a favore dell'opzione "pool di prontezza". |

### Decisioni nuove emerse da questa analisi

- **N1. Esecuzione degli attacchi nell'adapter DCS.** Task nativi DCS (Attack Group, Bombing...)
  oppure funzioni Lua come DCE (`CustomGroupAttack`, `OrbitPosition`...)? DCE disabilita 587 task
  nativi su 590 e usa script per controllare quota e tipo di attacco [Z §4.3, §8.4 p.3]. È una scelta
  dell'adapter, non del core: si può rimandare.
- **N2. Ruolo del waypoint nel tipo `Waypoint`.** Aggiungere a `DataType.Waypoint` (o a una sua
  estensione di missione) il ruolo, l'ETA e il tipo di quota. Oppure tenerli nella Missione come
  tabella parallela alla rotta: è la soluzione scelta per `AttackProfile`, "attributo della Mission,
  non della rotta".
- **N3. Tassonomia dei tipi di missione.** Aggiungere ai `Context` i tipi di supporto (AWACS, Tanker,
  Transport, AFAC, Runway Attack). Per la terra, definire i compiti in termini di intenzione
  (avanzare, difendere, tenere, ritirarsi, fuoco indiretto).

---

## 12. Lacune e incertezze delle fonti

- **Veicoli e navi con rotte e bersagli**: RISOLTO con la missione di prova dell'utente [T]
  (`Struttura_Missione_Terra_Mare.md`). Restano non decodificate le maschere `weaponType` di veicoli
  e navi (52613349374, 805339120, 56908316670) e il significato di `counterbattaryRadius` [I].
- **Discrepanze del manuale** (segnalate negli estratti):
  - velocità delle condizioni di trigger in m/s nel testo e km/h nelle figure;
  - descrizioni di Emission ON/OFF scambiate;
  - formato della data (`hh:mm:ss/giorno` nel testo, giorno/mese/anno nelle figure);
  - BUILDINGS nella Map Options;
  - "six categories" di statici ma dodici elencate.
- **Non documentati nel manuale**:
  - unità di DIRECTION FROM (gradi, presunta);
  - significato del checkbox INITIAL;
  - elenchi completi di RTB on out of ammo e dei bersagli di Radio usage (figure tagliate);
  - default reali di molti campi (le figure mostrano esempi).
- **Maschere `weaponType`** (2032, 4161536, 30720) non decodificate. Servono per tradurre la
  categoria d'arma della missione nel formato DCS.
- **Valori misurati sul `.miz` ma non decodificati**: `formationIndex`/`variantIndex` e i codici di
  opzione (`name` 1, 5, 15: interpretazione [I]).
- **Foto**: nessun menu a tendina aperto. Le foto danno i valori selezionati, non gli elenchi delle
  opzioni. Per gli elenchi fa fede il manuale.
- **Manuale del 2020**: i task e le opzioni aggiunti dopo (es. skill "Veteran"/"Trained" viste nelle
  foto) non sono documentati.
