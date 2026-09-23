---
name: project-virtual-session-engine-design
description: "Analisi delle due strategie proposte per il motore di esecuzione delle sessioni virtuali (tick a 1 ms vs risoluzione probabilistica) e architettura decisa: DES a coda eventi con scheduling analitico dei contatti. Documento in Analysis/Document/Architettura_esecuzione_sessioni_virtuali_ANALISI.md, 2026-09-21."
metadata:
  node_type: memory
  type: project
  originSessionId: 4f24ae57-a1fd-4207-aa69-d0ba0c8c5df1
  modified: 2026-09-23T20:49:22.873Z
---

**Stato 2026-09-22: analisi COMPLETATA e documentata. FASE 1 (cinematica), FASE 2 (percezione),
le 3 QUESTIONI APERTE del §9 e **FASE 3 (`Logic/Contact_Scheduler.py`)** sono CHIUSE, tutto sul
branch `analysis/dce-dcs-persistence` (da pushare). Prossima: FASE 4,
`Logic/Engagement_Resolver.py` + `Context/Reaction_Profile.py`.
V. anche [[project_session_2026_09_21_summary]].**
Documento: `Analysis/Document/Architettura_esecuzione_sessioni_virtuali_ANALISI.md` (525 righe),
a fianco della proposta sorgente dell'utente `Architettura_esecuzione_sessioni_virtuali.txt`.
Entrambi committati (64e490b0).

## Verdetto sulle due strategie proposte dall'utente
- **Strategia 1 (tick da 1 ms, slot per asset)**: non utilizzabile come motore primario.
  2 h × 10.000 asset = 6,687e10 aggiornamenti → 3,2 h al pavimento assoluto di CPython (loop vuoto),
  **74 giorni** a costo Mesa reale (95,7 µs/agente-step), **3,6-21 anni** se il rilevamento è O(N)
  per asset. Inoltre il passo è dimensionato sul missile ipersonico, che il testo stesso esclude
  dalla simulazione a tick. E nessun simulatore entity-level reale lo fa: JTLS è time-stepped ma
  **aggregato** (btg/brigata, Lanchester); JCATS/BRAWLER/AFSIM/ESAMS sono **event-driven**.
  Incongruenza trovata nel testo: `4,21 / 0,1 = 43` usa un divisore che non è né lo slot (1,08e-7 s)
  né il ciclo (1,08e-3 s).
- **Da salvare della Strategia 1**: RIV/VAL/COM/ATT è l'OODA loop e i suoi ordini di grandezza sono
  corretti (Osa 26 s, S-300P 28 s, Tor 5-8 s, pilota 1-2 s, equipaggio carro ~31 s). Vanno conservate
  come **latenze di reazione schedulate come eventi futuri**, non come conteggi di cicli. Decidono
  **chi spara per primo**, che è proprio ciò la cui assenza fa fallire i modelli a rapporto di forze.
- **Strategia 2 (probabilistica)**: direzione giusta, ma **non dice quando e se due forze si
  incontrano** — è il buco più grave. Va colmato analiticamente (CPA/TCPA + intersezione
  rotta↔volume), non con un tick.

## Architettura decisa: DES con scheduling analitico dei contatti
Tempo in **secondi assoluti**, nessun tick globale. Quattro strati:
0. contratto `SessionOrder`/`SessionOutcome` puro dominio;
1. **scheduler dei contatti** (il pezzo mancante): rotta↔cilindro → intervalli temporali via
   `Route.travelTimeToEdge`; CPA/TCPA `t* = −(Δr·Δv)/|Δv|²` fra mobili; potatura gerarchica a
   livello Block prima delle coppie di asset (è ciò che evita l'O(N²));
2. **risolutore d'ingaggio**: Pd → latenza di reazione (chi spara primo) → ROE → Pk da
   `accuracy × destroy_capacity`; **modello a salva di Hughes** per i molti-contro-molti;
3. applicazione stato per-asset → `SessionOutcome` → `Campaign_State` in una passata.
Micro-passo fine (1-5 s) ammesso **solo dentro una finestra attiva**, mai globale.

## Decisioni dell'utente registrate
1. i 10.000 asset sono solo un **limite superiore teorico**;
2. sessione **riproducibile da seed** — e **l'ordine di risoluzione degli eventi fa parte del
   contratto**, salvare il solo seed non basta;
3. perdite e danni **per singolo asset**;
4. budget di calcolo fino a **minuti**.

## Avvertimento da non dimenticare
Lanchester non si valida su dati storici (9 test falliti, Ardenne/Kursk); la regola 3:1 versione RAND
usata da JICM azzecca solo il **19%** su 98 ingaggi storici — peggio del caso. Ricaduta diretta:
`Logic/Tactical_Evaluation.py:251 calcFightResult` è esattamente un modello a rapporto di forze con
coefficienti tabellati a mano → va tenuto come **fallback aggregato**, mai come risolutore primario.
Se servirà un livello aggregato, i coefficienti vanno stimati con un **ATCAL interno** (far girare il
risolutore fine offline), non inventati.

## FASE 1 — cinematica utilizzabile: FATTA 2026-09-21 (suite 2540 -> 2608 test, OK)
Sblocca precondizioni 1 e 2. Committata (3af377c5).
- **Schema canonico `Mobile.speed`, tutto in m/s** (`SPEED_SCHEMA` in testa a `Asset/Mobile.py`):
  `{"nominal", "max", "off_road": {...} (solo Vehicle), "reference_altitude" (solo Aircraft)}`.
  Chiave canonica scelta: **`nominal`**, non `cruise` — `cruise` stava solo nel validatore, che
  non era mai stato eseguito con successo; `nominal` e' cio' che usano default, consumatori e test.
- **Fix del default mutabile**: `speed` nella firma di `Mobile.__init__` era un dict condiviso da
  tutte le istanze; ora `None` + `default_speed_profile()` che costruisce un oggetto nuovo.
- **Fix del setter**: non passa piu' da `checkParam` (che Vehicle/Ship/Aircraft sovrascrivono con
  firme senza `speed`) ma da `Mobile._validate_speed`. `checkParam` e' ora `@staticmethod` (le
  mancava `self`) e valida lo schema canonico.
- **Ponte registry -> istanza**: `Mobile.speed_profile_from_registry()` + `load_speed_from_registry()`,
  chiamati dai costruttori di Vehicle/Ship/Aircraft dopo `_model`. Dispatch **sul registry che
  risponde**, non su `isinstance` (piu' robusto e testabile). Conversioni: km/h, mph, nodi -> m/s
  (`Utility.kmh_2_meters_per_second` e `knots_2_meters_per_second`, nuove); per gli aerei IAS->TAS
  via `Utility.true_air_speed` (che restituisce sempre km/h). Ship: `max` = il piu' alto fra `max`
  e `flank`. Aircraft: `max` = il piu' alto fra `combat` ed `emergency`.
- **`Route.positionAtTime(t, speed=None)`**: la funzione posizione(t), interpolazione lineare
  sull'arco in percorrenza; oltre la durata totale restituisce l'ultimo waypoint; `None` se la
  velocita' non e' definita. Nuovo `Test/Test_Route.py` (20 test), che prima non esisteva.
- **`Military._speed_regime`** sostituisce la coppia `_get_nominal_speed`/`_get_max_speed`:
  None -> 0.0, cosi' i confronti `> 0` a valle non esplodono. `time_to_direct_line_attack` e'
  ora in **secondi** (la docstring diceva "hours" ma nessun calcolo convertiva) e funziona:
  verificato end-to-end, 10 km a 12.5 m/s -> 800 s (prima: divisione per zero).
- **Bug collaterale corretto**: `DataType/Route.py` creava il logger senza `.logger`, quindi ogni
  `logger.warning` sollevava AttributeError. Stesso difetto resta in Edge/Waypoint/Volume/Payload/
  Limes/Area/Threat/Event, dove pero' non ci sono call site.
- **Limite trovato, non risolto**: `Edge` costruisce una `Line2D` dalle proiezioni dei waypoint,
  quindi una salita verticale pura (stessa x,y) non e' rappresentabile — sympy rifiuta.

## FASE 2 — percezione: FATTA 2026-09-22 (suite 2608 -> 2685 test, OK, skipped=5), commit 30a6ee55
Chiude le precondizioni 3 e 4. Nessun file di Fase 1 toccato.
- **`Mobile.detection_range(mode, sensor=None, range_type='acquisition_range')`**
  (`Asset/Mobile.py`, accanto a `combat_range`). I raggi radar/TVD esistevano per ogni modello nei
  tre registry ma nessuna classe li esponeva. Ritorna **metri** (i registry sono in km), come
  `combat_range`/`air_defense_volume`. Costanti nuove in testa al modulo: `DETECTION_MODES`
  (derivata da `ACTION_TASKS`, unica fonte di verita' dei modi), `DETECTION_SENSORS`,
  `DETECTION_RANGE_TYPES`, `DEFAULT_DETECTION_RANGE_TYPE`.
- **Decisione radar+TVD: si compone col MASSIMO**, non con la somma e non col solo radar. La
  domanda dello scheduler e' "a che distanza l'osservatore vede per la prima volta", e la risposta
  e' il sensore che arriva piu' lontano fra quelli funzionanti (non si sommano: guardano lo stesso
  bersaglio). `sensor='radar'|'TVD'` isola un sensore, perche' le degradazioni future (ECM, notte/
  meteo sull'ottico, silenzio radar) colpiscono **un sensore alla volta**.
- **Decisione range_type: default `acquisition_range`** — rilevare e' acquisire; tracking e
  ingaggio sono stadi successivi e piu' corti, ma raggiungibili col parametro perche' serviranno
  alla Fase 4.
- **Gestione dati mancanti**: `None` e mai eccezione. Warning solo quando e' davvero un problema
  (`_model` assente, modello non in nessun registry); **debug** quando il dato e' corretto cosi'
  com'e' (`radar`/`TVD` == False -> un carro non ha radar; `TVD` assente come attributo -> Ship_Data
  non descrive sensori ottici; `capabilities[mode] == (False, {...})` o `(True, {})` -> Ship_Data usa
  questa forma). `ValueError` **solo** per mode/sensor/range_type fuori dominio (errore di
  programmazione, non dato mancante). Helper `Mobile._sensor_range_km` (staticmethod).
- **Fabbrica ThreatAA in `Logic/Air_Route_Manager.py`** (accanto a `ThreatAA` e a `RoutePlanner`),
  **non** come metodo di `Mobile`: ThreatAA e' un tipo dello strato Logic e Asset non deve dipendere
  da Logic. La geometria resta dov'era: `air_defense_volume()` produce il Cylinder, la fabbrica lo
  avvolge. API: `build_threat_aa(asset)`, `threat_reaction_times(asset, has_missiles=True)`,
  `threat_danger_level(radius, max_altitude, reaction_time)`, piu' `_air_defense_weapons(asset)`
  (selezione armi **identica** a `air_defense_volume`: stesso discriminante quote + task Anti_Air).
  Aggiunto anche il logger di modulo, che Air_Route_Manager non aveva.
- **`interception_speed`**: dai dati d'arma reali (`speed` dei SAM, `muzzle_speed` dei cannoni AA),
  **massimo** fra le armi AD (l'intercettore piu' veloce = caso peggiore per chi pianifica).
  `DEFAULT_INTERCEPTION_SPEED_MS = 600.0` come ripiego dichiarato: ThreatAA **divide** per
  interception_speed, quindi non puo' mai valere 0.
- **`min_detection_time`**: `acquire_time_s` della tabella minacce SAM ricercata
  (`Analysis/Document/documentazione_dcs/estratti/sam_threat_table.csv`, ingerita 2026-09-18),
  **trascritta** in `SAM_REACTION_TABLE` per i **9** modelli con corrispondenza nei registry
  (S-300PS 3 s, 9K37-Buk 21, 2K12-Kub 21, 9A33-Osa 19, 9K331-Tor 9, 9K35-Strela-10 2.5,
  Strela-1-9P31 2.5, 2K22-Tunguska 4, MIM-115-Roland 11). Trascritta e **non letta a runtime**: il
  core non deve dipendere da un file di documentazione, e la tabella e' fonte di riferimento
  stabile, non dato di campagna. I 14 sistemi del CSV senza modello nei registry sono omessi.
- **`min_fire_time`**: **non esiste in nessuna fonte del progetto** -> placeholder deterministico
  dichiarato (convenzione `Logic/Meteo_Analysis.py`), ordinato sul `launcher_type` che il CSV
  invece dichiara: `LAUNCH_SEQUENCE_TIME_S` (rampa singola 8 s ... lanciatore cingolato di difesa
  di punto 2 s), `DEFAULT_LAUNCH_SEQUENCE_TIME_S = 5.0`, `GUN_LAUNCH_SEQUENCE_TIME_S = 1.0` (un
  cannone AA non ha sequenza di lancio: resta il brandeggio).
- **Default fuori tabella** (`DEFAULT_ACQUIRE_TIME_S`, per classe: SAM_Big 3, SAM_Medium 16,
  SAM_Small 8, AAA 4; `DEFAULT_ACQUIRE_TIME_FALLBACK_S = 10`): valori presi dalla distribuzione
  della tabella stessa, dichiarati placeholder. Coprono Chaparral, Linebacker, tutte le AAA e
  **tutti i SAM navali** (il CSV copre solo SAM terrestri; la `category` di una nave e' una
  Sea_Asset_Type, che non e' una classe AD -> ripiego).
- **`danger_level`**: non aveva scala canonica in nessun punto del codice (i consumatori —
  `Route.max/min/avg_danger_level`, `Ground_Route_Manager`, `Air_Route_Manager:~1090` — fanno solo
  confronti monotoni). **Fissata a [0, 1]**, come tutti gli altri punteggi normalizzati del
  progetto, combinazione lineare saturata: portata 0.5 (l'evitamento di rotta e' un problema
  geometrico: raggio grande = deviazione grande), quota 0.3 (dice se la minaccia e' scavalcabile),
  reattivita' 0.2 (conta solo se si e' gia' dentro il volume). Riferimenti: raggio 100 km, quota
  25 km, latenza 30 s. Ordine ottenuto sui sistemi reali: S-300PS 0.83 > Buk 0.46 > Kub 0.32 >
  Tor 0.26 > Tunguska 0.24 > Shilka 0.20 > Osa 0.16 > Chaparral 0.19.
- **Pendant a livello Block** (`Block/Military.py`, stesso schema di `air_defense_volume`/
  `combat_range`, import di Logic **locale al metodo**): `Military.air_defense_threats()` ->
  `List[ThreatAA]` degli asset AD operativi; `Military.detection_range(mode, sensor)` ->
  `(max, med, ratio, quantity)` in metri (il max dice fin dove il blocco vede, la mediana quanto
  quella capacita' sia diffusa).
- **Test (+77)**: +27 in `Test_Mobile.py` (dominio argomenti, guardie None, km->m, composizione
  radar/TVD, dispatch fra i tre registry; `_MobileStub` ha ora `detection_range` e
  `staticmethod(Mobile._sensor_range_km)` — ri-decorare e' obbligatorio o diventa metodo
  d'istanza), +12 in `Test_Military.py`, e il nuovo `Test_Threat_AA_Factory.py` (38 test) tenuto
  separato da `Test_Air_Route_Manager.py` perche' verifica il **ponte verso i dati reali** di asset
  e armi (registry e registri d'arma veri, stub d'asset che porta il vero `air_defense_volume`) e
  non la geometria.
- **Cosa resta aperto dopo la Fase 2**: nessuno consuma ancora `detection_range` (lo fara' il
  Contact_Scheduler) e il `RoutePlanner` esistente continua a ricevere minacce costruite a mano —
  collegare `Military.air_defense_threats()` alla pianificazione di rotta reale e' lavoro di
  Fase 3. `min_fire_time` e i default di acquisizione restano stime dichiarate, da sostituire con
  dati reali senza cambiare la forma. I dati sensore hanno incoerenze di sorgente (es. F-14A ha
  `tracking_range` 315 km > `acquisition_range` 185 km): non corrette qui.

## LE 3 QUESTIONI APERTE DEL §9 — CHIUSE 2026-09-22 (suite 2685 -> 2753 test, OK, skipped=5)
Erano le tre decisioni bloccanti per la Fase 3. Tutte e tre **decise**; per ognuna e' stata
implementata la parte a basso rischio che rende la decisione operativa.

### Q1 — Quale modello Route vince: **`DataType.Route/Edge/Waypoint`, confermato**
Dettaglio completo + piano a 5 fasi in [[project_route_model_unification_plan]] (Fase 1 FATTA).
In sintesi: i modelli interni a `Ground_`/`Air_Route_Manager` restano ma **come stato di lavoro
privato** dell'algoritmo di ricerca, mai esposti; la conversione avviene in un solo punto,
l'uscita pubblica del path-finding. Fatto decisivo che ha reso la decisione facile: **nessun
consumatore di produzione** chiama oggi `RoutePlanner.calcRoute` o `find_optimal_path` (solo test
e `Utility/visualizer.py`), mentre tutto l'ecosistema (Region/Military/Tactical_Evaluation/
Command_Types) consuma solo il tipo canonico. Implementato: nuovo `Logic/Route_Adapter.py`
(duck-typed, non importa i due Route Manager -> nessun ciclo), `RoutePlanner.calcCanonicalRoute`,
`NavigationGraph.find_canonical_route`, `Test_Route_Adapter.py` (26 test).
**Blocco tecnico rimosso**: `DataType/Edge` costruiva `Line3D`/`Line2D` nel `__init__` e sympy
rifiuta due punti coincidenti, quindi una **salita verticale pura** — che il pianificatore aereo
produce normalmente — rendeva l'arco non costruibile (limite annotato in Fase 1 e lasciato
aperto). Ora `_buildLine` registra `None` + log, e `minDistance`/`intersectPoint` degradano.
Corretto anche il logger di `DataType/Edge.py` (mancava `.logger`).

### Q2 — Semantica della perdita per-asset: **contratto fissato + `apply_damage` scritta**
Nuovo `Logic/Damage_Model.py` (il contratto e' documentato per esteso nel docstring del modulo,
che e' la fonte di verita'; qui solo i punti da ricordare):
- **`accuracy` = P(colpo a segno), `destroy_capacity` = P(distruzione | colpo a segno)**. Non e'
  un'invenzione: e' la scomposizione in Ph e Pk|h della Pk `accuracy x destroy_capacity` gia'
  usata come principio nei registri d'arma (v. [[project_ship_weapon_scoring]]). Entrambi i campi
  esistono gia' in `Ground_/Ship_/Aircraft_Weapon_Data`, in [0,1], per tipo e taglia del
  bersaglio. **Nessuna costante di taratura nuova.**
- Tre esiti per colpo: `KILL` (p = acc x dc) -> salute a 0; `DAMAGE` (p = acc x (1-dc)) ->
  `-round(100 x dc)` punti, minimo 1; `MISS` -> nulla. **Un colpo puo' uccidere direttamente**,
  nessun pavimento artificiale. L'**accumulo e' emergente** (~1/dc colpi non letali), non un
  parametro. L'unica convenzione dichiarata e' `MIN_EFFECTIVE_HIT_DAMAGE = 1`, senza il quale le
  infrastrutture (dc ~ 0 nei registri) sarebbero indistruttibili per costruzione.
- **Soglia `Destroyed` NON rivista: resta `health <= 15`.** Il residuo e' il relitto, ed e' cio'
  che da' senso a `repair_time`. Scoperta che ha chiuso la questione: **la messa fuori
  combattimento avviene gia' prima** — `State.isOperative()` e' falso sotto il 50% (`Critical`) e
  `Military.combat_power` somma solo gli asset operativi. Quindi "mission kill" (<=50) e
  "distruzione" (<=15) sono **gia' entrambi nel modello**, non c'e' nulla da aggiungere.
- **Nessuna estrazione casuale nel modulo**: `resolve_hit(accuracy, destroy_capacity, draw)` riceve
  il `draw` dal chiamante (RNG di sessione seedato, Fase 0). L'ordine delle soglie (KILL, DAMAGE,
  MISS) **fa parte del contratto**: cambiarlo cambia l'esito a parita' di seed.
- **`DamageEvent`** (dataclass frozen) e' l'atomo del futuro `SessionOutcome`: `time` in secondi
  assoluti, `target_id`/`source_id`/`weapon` di dominio (mai id del simulatore), `outcome`,
  `health_before/delta/after`, `destroyed`, **`provenance`** (`measured`/`derived`/`estimated`,
  come richiesto da [[feedback_core_simulator_agnostic]]).
- **`build_damage_event` (calcola, non muta) separata da `apply_damage_event` (muta)**: serve al
  modello a salva di Hughes della Fase 4, che deve calcolare tutti gli esiti, ordinarli
  deterministicamente e solo poi applicarli.
- **`Asset.apply_damage(health_delta)`** (`Asset/Asset.py`): unico punto in cui la salute cala per
  attrito; il setter `health` resta per inizializzazione e persistenza. Satura a 0, passa dal
  setter di `State.health` che chiama `State.update()`. `TypeError`/`ValueError` solo per
  argomenti fuori dominio (delta positivo = riparazione: non passa di qui, per scelta).
- `Test_Damage_Model.py`, 37 test. **Non deciso qui**: penetrazione contro corazza (manca il campo
  `penetration` nei record d'arma, §9) e riparazione/recupero (materia del ciclo di campagna).

### Q3 — SAM/AAA/EWR nel combat power: **restano a 0, e' la definizione — ma serviva un numero**
- **Il 3 e' confermato intenzionale** e ora **documentato come tale** in `Context/Context.py`
  (commento sopra `GROUND_COMBAT_EFFICACY` + docstring di `combat_power_from_score`), non piu'
  registrato come "bug noto". Motivo: quella tabella misura capacita' di fuoco e manovra
  **terra-terra**, che un sito di difesa aerea non ha; aggiungercelo gonfierebbe la forza di
  superficie del blocco che lo possiede, cioe' produrrebbe un numero falso in cambio di nulla.
- **Ma il problema pratico esiste ed e' stato verificato nel codice**: in
  `Tactical_Evaluation._calculate_priority` un bersaglio con combat power nulla finisce nel ramo
  `if target_cp <= 0` e satura a `combat_power_ratio = 0.1`, **priorita' minima**. Cioe' oggi un C2
  non vedrebbe MAI un sito SAM come bersaglio prioritario — l'opposto della dottrina SEAD.
- **Soluzione decisa: dimensione separata, non voce in piu' nella stessa tabella.** La potenza
  della difesa aerea e' gia' modellata — `air_defense_volume()` -> `build_threat_aa()` ->
  `ThreatAA.danger_level` in [0,1] (Fase 2) — ma mancava un aggregato a livello di blocco.
  Implementata **`Military.air_defense_power()` -> [0, 1]**, aggregazione `1 - prod(1 - d_i)`
  ("almeno una difesa e' efficace"): saturante, monotona nel numero di siti, senza il tetto
  artificiale di un massimo. **NON e' una combat power e non e' confrontabile con quella.**
  +5 test in `Test_Military.py`. Nessuno la consuma ancora (come `detection_range` dopo la Fase 2).
- **Opzione scartata**: proporre una tabella di efficacia SAM/AAA/EWR sulla scala 1-5 di
  `GROUND_COMBAT_EFFICACY`. Sarebbe stata una scelta di **game balance inventata** (nessun dato la
  sostiene) per rendere confrontabili due grandezze che non lo sono.
- **Resta da fare in Fase 4 (SEAD), da confermare con l'utente**: far leggere
  `air_defense_power` alla priorita' di targeting quando l'attaccante e' aereo. E' un cambio di
  comportamento su numeri di campagna, non un'aggiunta: non fatto qui di proposito.

## FASE 3 — scheduler dei contatti: FATTA 2026-09-22 (suite 2762 -> 2858 test, OK, skipped=5)
Nuovo `Logic/Contact_Scheduler.py` + nuovo `Test/Test_Contact_Scheduler.py` (96 test). **Nessun
file esistente toccato**: e' codice nuovo che compone API gia' stabili (Fasi 1-2, Q1-Q3).
E' lo strato 1 dell'architettura DES: calcola **quando**, mai **chi vince** (Fase 4).

### Il tipo su cui poggia tutto: `Leg`
La spezzata di una `DataType.Route` viene scomposta una volta sola in una lista di `Leg`
(`t_start`, `t_end`, `p_start`, `p_end`, `edge_name`) in **tempo assoluto**, e da li' in poi il
modulo non parla piu' di rotte. Tre ragioni, tutte pratiche:
- **cercare contatti significa attraversare la rotta molte volte**: ricalcolare il prefisso dei
  tempi a ogni arco (cioe' chiamare `Route.travelTimeToEdge` in un ciclo) sarebbe quadratico;
- le posizioni sono **terne di float, non `Point3D`**: dentro ai cicli si fanno migliaia di
  prodotti scalari e l'aritmetica esatta di sympy li renderebbe inutilmente costosi. I `Point3D`
  ricompaiono solo sui risultati (`entry_point`, `point_a`, ...), dove il dominio li vuole;
- un asset **fermo** (`static_legs`) e' un `Leg` con `p_start == p_end`: il resto del modulo non
  ha bisogno di sapere che e' fermo, e il caso "rotta contro bersaglio fermo" — che in campagna
  e' il piu' frequente: sito SAM, deposito, base — non richiede una rotta fittizia.
`route_legs` replica esattamente l'accumulo di `Route.travelTimeToEdge`/`positionAtTime` (stesso
ordine di percorrenza, stessa `Edge.calcTravelTime(speed)`); **un test di non-regressione
verifica l'uguaglianza arco per arco**, cosi' i due non possono divergere in silenzio.

### A — rotta contro volume di minaccia (`threat_windows`, `route_threat_windows`)
Geometria **non riscritta**: si chiama `Cylinder.getIntersection(Segment3D, tolerance)` per ogni
arco e si converte in frazioni d'arco -> istanti. `ThreatAA.edgeIntersect` fa la stessa cosa ma
sul modello **interno** di `Air_Route_Manager` (stato di lavoro privato del path-finding), quindi
non e' riusabile: qui si consuma solo `DataType.Route/Edge/Waypoint` — test di non-regressione
della decisione Q1, e il modulo non importa nulla dai due Route Manager (neanche la costante di
tolleranza, ridichiarata come `DEFAULT_INTERSECTION_TOLERANCE = 0.1`).
**Tre casi che `getIntersection` da sola non chiude, chiusi qui** (e ognuno ha il suo test):
1. **arco interamente dentro** il cilindro: nessuna superficie attraversata -> `(False, None)`,
   indistinguibile da "nessuna intersezione". Si disambigua con `Cylinder.innerPoint` sui due
   estremi;
2. **arco con un estremo dentro**: `getIntersection` restituisce il segmento
   intersezione-estremo; l'estremo interno da' comunque la frazione 0 o 1;
3. **tangenza** (un solo punto, nessun estremo interno): `getIntersection` **solleva**
   `ValueError("Intersezione anomala")`. E' un contatto di misura nulla, un dato legittimo e non
   un errore di programmazione -> si cattura, si logga a debug, si scarta l'arco.
Le finestre di archi **consecutivi vengono fuse**: entrare nel volume sull'arco i e uscirne
sull'arco i+2 e' UNA esposizione, non tre. Passaggi separati restano separati.
`ThreatWindow` porta `t_entry`/`t_exit`/`duration`, i punti di ingresso e uscita, `danger_level`
e `threat_id` (che `ThreatAA` non ha: lo fornisce il chiamante, o si prende da `threat.name`).

### B — CPA/TCPA (`closest_point_of_approach`, `range_intervals`, `contact_windows`)
**La scoperta che ha dato forma a questa parte**: `t* = -(Δr·Δv)/|Δv|²` vale per moto relativo
rettilineo uniforme, ma **una rotta e' una spezzata** — applicare la formula "alla rotta intera"
da' un risultato semplicemente sbagliato appena la rotta ha piu' di un arco. Quindi il calcolo si
fa su ogni sottointervallo delimitato dai waypoint **di entrambe** le rotte (`_breakpoints`),
dove per costruzione le due velocita' sono costanti; dentro ognuno la soluzione e' esatta e il
risultato globale e' il minimo dei minimi locali. Un test lo rende esplicito: B va da (0,1000) a
(0,100) e torna a (0,1000) — gli estremi distano entrambi 1000 m, il vero CPA e' 100 m.
- **Caso degenere `|Δv|² ≈ 0`** (fermi, o paralleli alla stessa velocita'): nessuna divisione per
  zero, la distanza e' costante, `CPA.degenerate = True` e `time` e' convenzionalmente l'inizio
  dell'intervallo. La soglia e' `VELOCITY_EPS = 1e-12`.
- **Clamp all'esistenza di entrambi**: ogni calcolo avviene nella sovrapposizione dei due span
  (`legs_span`). Nessuno dei due asset esiste prima della propria partenza o dopo il proprio
  arrivo; se gli span non si sovrappongono il risultato e' `None`, non una distanza qualsiasi.
- **Il CPA da solo non basta allo scheduler**: dice *quanto* si sono avvicinati, non *da quando a
  quando* sono stati a tiro. Per quello serve l'equazione completa `|Δr + Δv s|² = R²`
  (`range_intervals`), risolta sugli stessi sottointervalli e poi fusa. Il risultato puo'
  contenere **piu' intervalli disgiunti**: due rotte che si incrociano piu' volte entrano e
  escono dal raggio piu' volte (test dedicato, due passaggi).

### `ContactWindow` — il contratto verso la Fase 4
E' l'uscita principale del modulo, e la sua forma e' decisa da cosa serve all'`Engagement_Resolver`:
- `[t_start, t_end]` usa la portata **maggiore** fra le due -> e' il primo contatto in assoluto;
  `first_detector` ('a'/'b'/'both') dice chi lo ottiene;
- `[t_mutual_start, t_mutual_end]` usa la portata **minore** -> da quando si vedono entrambi;
  `None` se uno dei due non vede mai l'altro.
**Perche' la distinzione e' esplicita e non un dettaglio**: e' esattamente cio' che decide *chi
spara per primo*, la domanda a cui i modelli a rapporto di forze non sanno rispondere (v.
l'avvertimento su Lanchester in testa a questo documento). Una coppia produce una **lista** di
finestre, non una sola, e ogni finestra porta il proprio `t_cpa`/`distance_cpa` locale.
Le portate si ricavano da `mutual_detection_ranges`, che interroga ognuno **sul dominio
dell'altro** (`detection_mode_for`: Vehicle/Structure -> 'ground', Ship -> 'sea', Aircraft ->
'air', mappa sul nome della classe come `Context.classify_asset_dimension`, per non importare i
registry). Il `range_type` e' un parametro: con `'engagement_range'` la stessa funzione risponde
a "quando sono a tiro" invece che "quando si vedono" — pensato per la Fase 4. Le portate sono
anche **imponibili dal chiamante** (`range_a`/`range_b`): le degradazioni future (disturbo,
meteo, silenzio radar) si applicheranno **fuori** da questo strato, che resta puramente
geometrico.

### C — potatura gerarchica (`block_pair_candidates`, `region_block_pairs`, `block_max_speed`, `block_reach`)
Criterio: si scarta una coppia di blocchi **solo** quando il contatto e' geometricamente
impossibile, cioe' quando
`distanza(centroidi) > (v_max_A + v_max_B) * horizon + portata_A + portata_B + margin`.
Tutto conservativo di proposito, perche' l'unico errore inaccettabile per un filtro e' scartare
una coppia che si sarebbe incontrata:
- `block_max_speed` legge anche il ramo **`off_road`** del profilo canonico (il movimento tattico
  non avviene su strada; il solo regime stradale sottostimerebbe l'inviluppo);
- `block_reach` prende il **massimo** fra `combat_range()[0]`, `detection_range(mode)[0]` su tutti
  i modi e il raggio dei cilindri di `air_defense_threats()` — non la mediana e non la somma:
  basta un singolo sensore o una singola arma a lunga gittata per rendere la coppia non
  scartabile;
- **un blocco senza posizione non viene MAI scartato**: l'assenza di dato non e' prova di
  lontananza. E' [[feedback_no_visibility_low_priority]] applicata al contrario — li' l'ignoto non
  alza la priorita', qui non autorizza a scartare;
- le grandezze aggregate si calcolano **una volta per blocco**, non una per coppia: e' il motivo
  per cui la potatura e' economica;
- accetta indifferentemente `Block`/`Military` o `BlockItem` (`.block`), e **restituisce gli
  oggetti originali** cosi' il chiamante conserva i propri riferimenti;
- `skip_same_side=True` di default (i contatti si cercano fra forze contrapposte).
`region_block_pairs(region, side_a, side_b, horizon, ...)` chiude il giro con
`Region.get_blocks_by_criteria`.

### Orchestrazione: `schedule_contacts`
Mette insieme i tre meccanismi nell'ordine che li rende trattabili: prima C (potatura a livello
blocco), poi B (CPA solo sulle coppie di asset superstiti). Un asset senza rotta in `routes` non
viene ignorato: se ha una posizione, e' trattato come fermo per tutta la finestra. I `Leg` di ogni
asset si calcolano **una volta sola** (cache su `id(asset)`), non una per coppia.
**L'ordinamento del risultato — `(t_start, asset_a_id, asset_b_id)` — fa parte del contratto**, non
e' un dettaglio estetico: e' cio' che rende la sessione riproducibile a parita' di seed (decisione
dell'utente n. 2, "salvare il solo seed non basta"). Lo stesso vale per `route_threat_windows`,
ordinato per `(t_entry, threat_id)`.

### Convenzioni rispettate e cose deliberatamente NON fatte
- **Nessuna sorgente di casualita'**: lo strato e' puramente geometrico e non ne ha avuto bisogno.
  Se un giorno servisse, va passata dal chiamante come il `draw` di `Logic/Damage_Model.py`.
- **Mai eccezioni per dati mancanti**: rotta vuota, arco a velocita' indefinita, asset senza
  posizione, asset senza `detection_range`, minaccia senza cilindro -> lista vuota/`None` + log.
  `ValueError` solo per argomenti fuori dominio (`horizon`/`margin`/`radius` negativi, intervallo
  invertito).
- **Import locali ai metodi** dove servono (`DETECTION_MODES` dentro `block_reach`).
- **Nessun tick, nessun campionamento**: solo soluzioni in forma chiusa.
- **NON e' stato collegato `Military.air_defense_threats()` alla pianificazione di rotta reale**
  (il `RoutePlanner` continua a ricevere minacce costruite a mano nei test). Era elencato come
  parte della Fase 3 ma e' un lavoro diverso — modificare il pianificatore, non lo scheduler — e
  cambia il comportamento di rotte gia' in uso. `route_threat_windows` accetta gia'
  direttamente l'uscita di `air_defense_threats()`, quindi il ponte e' pronto dal lato consumatore.

### Punti aperti che la Fase 4 dovra' confermare
1. **`ContactWindow` non porta `provenance`** (il campo che `DamageEvent` ha per
   [[feedback_core_simulator_agnostic]]): qui e' sempre e solo `derived`, perche' le finestre
   sono calcolate, mai misurate. Se un adapter DCS dovesse un giorno **riportare** contatti
   osservati, il campo servirebbe e andrebbe aggiunto.
2. **`ThreatWindow` non incrocia le latenze di `ThreatAA`** (`min_detection_time`,
   `min_fire_time`): dice quando la rotta e' dentro il volume, non se il difensore fa in tempo a
   reagire. E' deliberato — quello e' il risolutore d'ingaggio — ma va deciso in Fase 4 se il
   confronto `duration vs (min_detection_time + min_fire_time)` vive li' o come helper qui.
3. **Il modo di rilevamento e' per classe, non per stato**: un aereo a terra resta 'air'. Finche'
   non esiste una nozione di "asset a terra" nel modello, non c'e' modo di fare meglio.
4. **La quota conta davvero** (un cilindro di difesa aerea non copre chi lo scavalca) e questo si
   propaga a `Edge`: una salita verticale pura resta un arco senza retta di supporto 2D (limite
   gia' noto dalla Fase 1, degradato ma non risolto). `threat_windows` non ne soffre perche' non
   usa `Edge.minDistance`/`intersectPoint`, ma un consumatore futuro potrebbe.

## Precondizioni bloccanti trovate nel codice (verificate riga per riga)
1. **`Asset/Mobile.py:345`**: `checkParam` definita senza `self` → il setter `speed` (`:97-100`)
   solleva sempre `TypeError`. Default mutabile a `:50`. `_speed` mai popolato dai registry.
   **Senza velocità non c'è posizione(t), quindi nessun contatto calcolabile: è IL blocco.**
2. `Block/Military.py:455-467` → `_get_nominal_speed`/`_get_max_speed` danno 0/None →
   `time_to_direct_line_attack` (`:363`) divide per zero.
3. ~~Nessuna API di raggio di rilevamento~~ **RISOLTA in Fase 2**: `Mobile.detection_range` +
   `Military.detection_range`.
4. ~~`ThreatAA` mai costruito da `Mobile.air_defense_volume()`~~ **RISOLTA in Fase 2**:
   `Air_Route_Manager.build_threat_aa` + `Military.air_defense_threats`.
5. ~~Nessuna `apply_damage`~~ **RISOLTA 2026-09-22 (Q2)**: `Asset.apply_damage` +
   `Logic/Damage_Model.py`. "Destroyed" resta a `health ≤ 15`, per scelta motivata.
6. `random` non seedato a livello di modulo (`Tactical_Evaluation.py:360-361`, `Structure.py:128`,
   `Utility.py:320`, DB armi).
7. ~~**Tre modelli Route/Edge/Waypoint incompatibili**~~ **RISOLTA 2026-09-22 (Q1)**:
   `DataType.Route` confermato unico modello, `Logic/Route_Adapter.py` e' la frontiera;
   `calcCanonicalRoute`/`find_canonical_route` sono le uscite pubbliche.
8. `DataType/Event.py:81-95` rotto (`self._type` mai assegnato), importato da 8 moduli, nessun test.
9. `Tactical_Evaluation.py:532-579 evaluateGroundRouteDangerLevel` rotta su 3 punti (concetto giusto).
10. ~~**SAM/AAA/EWR hanno combat power ≡ 0**~~ **CHIARITA 2026-09-22 (Q3)**: non era una
    precondizione ma una definizione, ora documentata; il numero mancante e'
    `Military.air_defense_power()`, su una scala diversa.
11. `DataType/Threat.py` e `DataType/Volume.py` sono codice morto.

Fondamenta buone già pronte: `Cylinder.innerPoint`/`getIntersection` (404 righe di test),
`Route.travelTimeToEdge`, DB armi con `accuracy × destroy_capacity`, `Combat_Power_Estimation`,
`Tactical_Analysis`, `Military.time2attack`/`combat_range`/`air_defense_volume`.

## Roadmap (7 fasi, nel documento)
0 contratto+RNG → 1 cinematica (sblocca tutto) → 2 percezione → 3 `Logic/Contact_Scheduler.py` →
4 `Logic/Engagement_Resolver.py` + `Context/Reaction_Profile.py` → 5 danno per-asset →
6 `Logic/Session_Simulator.py` → 7 validazione + **test di agnosticismo**.

## PROSSIMO PASSO — FASE 4, `Logic/Engagement_Resolver.py` + `Context/Reaction_Profile.py`
Ha tutto: **quando** avviene il contatto (`Contact_Scheduler.ContactWindow`/`ThreatWindow`, Fase 3),
chi vede per primo (`first_detector` e la distinzione unidirezionale/bidirezionale), quanto durano
le latenze di reazione (`ThreatAA.min_detection_time`/`min_fire_time`, Fase 2), e che forma di dato
produrre (`DamageEvent` + `resolve_hit(accuracy, destroy_capacity, draw)`, Q2).
Da fare: Pd -> latenza di reazione (chi spara primo) -> ROE -> Pk, e **modello a salva di Hughes**
per i molti-contro-molti (`build_damage_event` e' gia' separata da `apply_damage_event` proprio per
questo: calcolare tutti gli esiti, ordinarli deterministicamente, applicarli solo dopo).
**L'RNG di sessione seedato e' della Fase 0 e non esiste ancora**: il risolutore lo consuma, non lo
crea. Da confermare con l'utente i 4 punti aperti in coda alla sezione Fase 3.
**Resta fuori da entrambe le fasi e non e' fatto**: collegare `Military.air_defense_threats()` alla
pianificazione di rotta reale (il `RoutePlanner` riceve ancora minacce costruite a mano nei test).

## I 3 punti lasciati aperti dopo Q1-Q3 — CHIUSI 2026-09-22

1. **SEAD — `air_defense_power()` collegata alla priorita' di targeting: FATTO.**
   `Tactical_Evaluation.calculate_priority`, ramo `target_cp <= 0`: prima saturava sempre a
   `combat_power_ratio = 0.1` per un attaccante (SAM/AAA/EWR = 0 combat power per definizione,
   Q3). Ora, solo quando `is_attack and force_type == 'air'`, legge
   `target_block.air_defense_power()` (se il bersaglio la espone) e mappa `[0,1] -> [0.1, 10.0]`
   linearmente (`0.1 + air_defense_power * 9.9`) — stessa scala degli altri rami della funzione.
   Attaccanti ground/sea restano al floor 0.1 (SEAD e' un compito aereo). Bersaglio senza
   `air_defense_power()` (duck-typing, `getattr(..., None)`) -> floor 0.1 invariato, nessuna
   eccezione. 5 nuovi test in `Test_Tactical_Evaluation.py::TestCalculatePrioritySEAD`.
   Effetto collaterale trovato e corretto: `TestCalculatePriorityTargetAffinity._target` (mock
   `spec=Military`) non configurava `air_defense_power` -> un test esistente con attaccante aereo
   e target a combat power 0 ora chiamava un `MagicMock` non configurato invece di un float,
   rompendo l'aritmetica. Fix: default `air_defense_power.return_value = 0.0` nel fixture
   (comportamento invariato per quel test, che non e' sul SEAD).
2. **`MIN_EFFECTIVE_HIT_DAMAGE = 1` (`Logic/Damage_Model.py`): confermata, nessuna modifica.**
   Resta la costante che garantisce che un colpo a segno abbia sempre un effetto minimo, anche
   contro un bersaglio con `destroy_capacity` quasi nulla (le infrastrutture nei registri) —
   altrimenti l'accumulo di danno sarebbe impossibile per costruzione contro quei bersagli.
3. **`Edge.calcLength()` non distingue per `path_type` (`DataType/Edge.py`): il COMMENTO era il
   bug, corretto — il codice resta invariato.** `calcLength()` chiama
   `Waypoint.distanceFrom(Waypoint)`, che risolve sempre a `Point3D.distance()` (3D), mai
   `self._path_type`. Le posizioni degli asset (anche terrestri) portano gia' una quota reale
   (`Asset._position = Point3D(x, y, unit_alt)`, da `unit_alt` DCS), quindi la distanza 3D e'
   fisicamente sensata anche per il ground — introdurre ora una proiezione 2D per
   `onroad`/`offroad`/`water` avrebbe cambiato silenziosamente lunghezze di rotta e tempi di
   percorrenza gia' in uso (`Route.length`/`travelTime`, `Military.time_to_ground_intercept`), un
   cambio di comportamento a se stante, non un fix. Il commento sopra `self._lenght = ...` ora
   descrive il comportamento reale.

Suite dopo questi 3 fix: 2762 test OK (skipped=5), +5 da 2757 (i test SEAD; gli altri due punti
non aggiungono test).

## FASE 4 — risolutore d'ingaggio: FATTA 2026-09-23 (suite 2858 -> 3002 test, OK)

Implementata da un agente Opus (effort alto, richiesta esplicita dell'utente) con le 3 decisioni
dell'utente del 2026-09-23 come vincoli di design (v. [[project_session_2026_09_23_summary]] per il
riassunto delle decisioni; qui solo l'implementazione). Verificata da questa sessione: suite
completa rieseguita indipendentemente, stesso risultato; letto per intero `Engagement_Resolver.py`
e le sezioni nuove di `Doctrine.py`/`Military.py` — qualita' alta, coerente con le decisioni.

**File nuovi**: `Logic/Engagement_Resolver.py` (1115 righe: `resolve_engagement()` +
`apply_engagement_result()`, coda eventi heapq con tipi LANCIO<IMPATTO<RISOLUZIONE e tie-break
deterministico, stato ombra `_Shadow` che non muta gli asset reali finche' non si applica il
risultato), `Context/Reaction_Profile.py` (311 righe: RIV/VAL/COM/ATT per tipo di sistema, valori
dal documento di architettura §4.2 — Osa 26s, S-300PS 28s, Tor 6.5s, pilota 1.5s, equipaggio carro
31s — profilo di ripiego 31s per classi sconosciute/navi).

**File estesi**: `Context/Doctrine.py` (+123 righe: `DEFAULT_DISENGAGEMENT_THRESHOLDS` erosion 0.30/
shock 0.20 uguali per i 3 lati, `validate_disengagement_thresholds` con vincolo `shock <= erosion`,
`get_disengagement_thresholds`), `Block/Military.py` (+98: `salvo_interceptors()` +
`salvo_interception_capacity()`, R1, deliberatamente separata da `air_defense_power()`),
`Asset/Mobile.py` (+224: `ammunition`/`has_ammunition`/`consume_ammunition`/
`ammunition_from_registry`/`load_ammunition_from_registry`, R3 — contatore per asset, non per arma;
somma `record.weapons` dai registri escludendo `UNIT_COUNTED_WEAPON_TYPES = ('MACHINE_GUNS', 'CIWS')`
dove la quantita' e' n. di armi non di colpi; aerei restano a `None` = non modellata, nessun dato nei
registri), una riga ciascuno in `Vehicle.py`/`Ship.py`/`Aircraft.py` (`load_ammunition_from_registry()`
nel costruttore). Nuovi `Test_Engagement_Resolver.py` (75) e `Test_Reaction_Profile.py` (29), estesi
`Test_Doctrine.py`/`Test_Military.py`/`Test_Mobile.py`.

**Le 3 decisioni del 21/09→23/09 tutte rispettate**: P1 (soglia dottrina di lato, per forza
intera) + R2 (soglia di shock, stessa sede/granularita') → `_check_doctrine`, esito `DISENGAGED`
distinto da `DESTROYED`; R1 (saturazione) → `salvo_interception_capacity`, funzione dedicata non
riuso di `air_defense_power`; R3 (munizioni per asset, rifornimento fuori scope) → `Mobile.ammunition`
senza alcun metodo di ricarica; R4 (congelamento payload) → una salva lanciata (`Salvo`, frozen) non
viene mai riscritta, solo annullata prima del lancio se il bersaglio o il lanciatore sono gia' fuori
combattimento.

**Interprete**: su questa macchina `venv/bin/python3` e' un Python 3.14 senza dipendenze (skfuzzy/
sympy/matplotlib mancanti) — la suite va eseguita con `.direnv/python-3.12/bin/python3`, non con
`venv/bin/python3` come dicono le vecchie note per altre macchine. Verificare l'interprete giusto a
inizio sessione su ogni macchina diversa, non fidarsi della prima nota trovata in memoria.

**11 punti aperti lasciati con l'opzione piu' conservativa dall'agente, NON ancora decisi
dall'utente** (nessuno blocca l'uso del risolutore, ma condizionano la Fase 5/6 e la calibrazione):
1. Selezione arma/Pk dai registri: non fatta, iniettata via `fire_control(shooter, target)`.
2. Ripartizione del fuoco: piu' tiratori possono convergere sullo stesso bersaglio (nessun
   round-robin/coordinamento).
3. `salvo_window` di default 0 (solo impatti simultanei condividono la saturazione) — parametro
   di taratura, non deciso.
4. Ordine dei colpi intercettati: i primi intercettabili in ordine (impatto, salva), non
   proporzionale ne' round-robin.
5. Denominatore di erosione/shock: organico impegnato all'inizio, non forza superstite (scelta
   per coerenza fra le due soglie, non ridiscussa esplicitamente con l'utente).
6. Munizioni aerei: illimitate di default (`None`), non derivate dal loadout assegnato.
7. `ShotSpec.interceptable`: decisa dal chiamante (`fire_control`), nessuna euristica di default.
8. Degradazione Pd da meteo/notte: aggancio presente (`detection_factor`), non collegato a
   `Logic/Meteo_Analysis`.
9. Interpretazione di R4 sul rilancio "shoot-look-shoot": un lancio gia' schedulato ma non ancora
   partito viene annullato (non riscritto) se il bersaglio muore prima del lancio.
10. La variante di P1 "soglia anche come conteggio minimo di una categoria critica" non
    implementata: solo le due soglie in frazione.
11. Possibile conflitto futuro su `Doctrine.py` con `feature/c2-doctrine-per-side-fase-a` (che in
    questo clone non esiste ancora fuso) — da controllare al momento del merge.

**How to apply:** qualunque lavoro sul motore di sessione parte da questo documento, non dal `.txt`
sorgente. Le Fasi 1-4 sono **fatte**: cinematica, percezione, scheduler dei contatti, risolutore
d'ingaggio. Prossimo passo: **Fase 5** (applicazione danno per-asset e consumi in un'unica passata,
assemblaggio `SessionOutcome` — gran parte gia' esiste in `Damage_Model`/`apply_engagement_result`,
manca l'orchestratore) oppure chiudere prima alcuni dei punti aperti sopra se l'utente vuole
calibrare/decidere quelli prima di proseguire.
## FASE 5 — SessionOutcome, RNG di sessione, carburante: FATTA 2026-09-23 (suite 3027 -> 3115 test, OK)

Implementata da un secondo agente Opus (effort alto) nella stessa sessione della Fase 4. Verificata
da questa sessione allo stesso modo: suite riegeguita indipendentemente, stesso numero; letti per
intero `Utility/Session_Rng.py`, `Command/Session_Types.py`, `Logic/Fuel_Model.py` — qualita' alta.

**File nuovi**: `Command/Session_Types.py` (338 righe: `SessionOrder`/`SessionOutcome`, la "Fase 0"
mai fatta finora, chiusa qui insieme alla 5; `assemble_session_outcome` funzione pura che aggrega
piu' `EngagementResult` in un solo esito, ordinamento stabile per tempo, non scrive `Campaign_State`
ne' applica agli asset — quello resta di `Theater_Session_Manager`, non costruito), `Utility/Session_Rng.py`
(113 righe: `session_seed`/`session_rng`, seed = SHA-256 su JSON canonico `[schema, session_id,
mission_id, event_id, counter]` troncato a 64 bit — MAI `hash()` di Python, instabile fra processi;
verificata l'indipendenza fra counter con correlazione di Pearson e χ²), `Logic/Fuel_Model.py`
(165 righe: `FuelEvent` + `build_fuel_event`/`apply_fuel_event`, stessa separazione calcolo/
applicazione di `Damage_Model`).

**File estesi**: `Asset/Mobile.py` (carburante: `fuel`/`has_fuel`/`consume_fuel`/`fuel_autonomy`/
`fuel_for_distance`/`fuel_range_remaining`/`fuel_from_registry`/`load_fuel_from_registry`),
`Asset/Aircraft.py` (`fuel_autonomy` dal loadout assegnato, `fuel_capacity_kg()`; assegnare un
loadout fa il pieno, coerente con la decisione di riarmo gia' presa), `Vehicle.py`/`Ship.py`
(`load_fuel_from_registry()` nel costruttore).

**Decisione di design non nel briefing originale, verificata e confermata dall'utente**: il
carburante e' misurato come **frazione del carico pieno [0,1]**, non kg — Vehicle_Data/Ship_Data
non hanno una capacita' di serbatoio (solo l'autonomia in km/nm), solo gli aerei hanno
`fuel_internal_max`; con un'unica unita' per tutti gli asset i `FuelEvent` restano sommabili.
Consumo = distanza/autonomia per terra/mare; per gli aerei dal range del loadout assegnato con
**fattore 2x dichiarato** (il range e' un raggio d'azione andata+ritorno) — confermato dall'utente.
Navi a propulsione nucleare: carburante `None` (non modellato, il reattore non si esaurisce in una
sessione di ore) — confermato dall'utente. `fuel_efficiency` dei registri NON e' usato: e' un
punteggio adimensionale di selezione asset, non un tasso di consumo (il docstring di Aircraft_Data
che lo chiama "km/l" e' impreciso).

**Ambiguita' lasciate aperte, non bloccanti**: due ingaggi della stessa sessione sullo stesso asset
senza applicare il primo prima del secondo -> `health_before/after` non concatenabili (solo un
warning, i delta restano applicabili in ordine — risolverlo e' compito dell'orchestratore di
Fase 6); nessun `apply_session_outcome` (l'applicazione "in un'unica passata" e' di
`Theater_Session_Manager`, non ancora costruito).

## FASE 7 — validazione: IN CORSO (avviata 2026-09-23)

**Battera scenari estesa da S1-S11 a S1-S18**, su richiesta dell'utente: ha chiesto di valutare
le situazioni piu' significative considerando Block/asset/classificazione del progetto (non solo
i documenti Lanchester). Verificata la classificazione REALE nel codice (`Context.py:451
MILITARY_CATEGORY`: Ground_Base = Stronghold/Farp/Regiment/Battallion/Company/Brigade/Division/
Command_&_Control_C2/C4, Air_Base = Airbase/Heliport, Naval_Base = Port/Shipyard/Naval_Group;
`BLOCK_INFRASTRUCTURE_ASSET` per Transport/Production/Urban/Storage) — **nota**: "Plotone" e
"Avamposto" menzionati dall'utente NON esistono come mil_category distinte nel registro attuale
(Stronghold copre gia' il concetto di "caposaldo/avamposto fortificato"). 7 nuovi scenari proposti
e TUTTI ACCETTATI dall'utente:
- **S12 - Decapitazione C2**: colpo mirato a un nodo `Command_&_Control_C2`/`C4` isolato.
- **S13 - Interdizione FARP**: bersaglio con asset eterogenei (elicotteri+edifici) in un Block.
- **S14 - Bombardamento impianto Production**: `Power_Plant`/`Factory` come bersaglio economico
  fisso, distinto dalla linea logistica mobile di S7.
- **S16 - Installazione navale fissa**: `Port`/`Shipyard` come bersaglio primario (S6 testa la
  difesa costiera, non il porto stesso).
- **S18 - Rete Transport multi-nodo**: estende S7 da convoglio mobile a nodi fissi di rete
  (ponte, interscambio, elettrico) lungo un percorso.
- **S17 - Sweep di scala gerarchica**: uno scenario ripetuto a taglie diverse
  (Company/Battalion/Regiment/Brigade/Division) per verificare coerenza al variare della scala.
- **S15 - Prossimita' Urban (test contrattuale ROE)**: verifica solo che l'architettura non
  impedisca a un `fire_control` esterno di gestire il collaterale — non un modello di danno
  civile vero (il motore non ne ha uno, e' demandato al chiamante).

**Split in 2 dispatch Opus per gestibilita'**: primo agente = harness di scenario condiviso + test
di determinismo + test di agnosticismo (entrambi obbligatori dal roadmap) + scenari S1-S9; secondo
agente (da lanciare dopo aver revisionato il primo, riusando il suo harness) = scenari S10-S18.
**Nota importante data all'agente**: oggi non esiste alcun adapter DCS nel codice Python, quindi
il "test di agnosticismo" non puo' essere un prima/dopo la rimozione — e' un test di CONTRATTO
(struttura + esecuzione end-to-end con soli dati sintetici), spiegato per esteso nel briefing.

**Prima meta' (S1-S9) FATTA e verificata**: harness `Test/Scenario_Fixtures.py` (funzioni
`make_vehicle/make_aircraft/make_ship`, `make_force`, `Unit`/`build_force`, `straight_route`/
`route_for`/`routes_for`, `make_fire_control` con tabella ruolo-vs-ruolo dichiarata come dati di
test non tarati, `Scenario`/`run`), `Test/Test_Session_Validation.py` (19 test: determinismo
verificato campo-per-campo+stato reale degli asset, non vacuo su seed diverso; agnosticismo come
test di CONTRATTO — nessun adapter DCS esiste nel codice Python quindi non c'e' nulla da
"rimuovere": verifica strutturale via `typing.get_type_hints` sui tipi di dominio + AST-check che
i moduli del motore non importino nulla DCS + un run end-to-end con soli dati sintetici),
`Test/Test_Session_Scenarios.py` (42 test, S1-S9). Suite 3168 -> 3229.

**Bug trovati durante la Fase 7 (non corretti dall'agente, come da istruzioni)**, poi triagati con
l'utente:
- **`Block.set_asset` rifiuta Vehicle/Aircraft/Ship** (confrontava `__class__.__name__` con la
  stringa esatta 'Asset') — **FIX APPLICATO DIRETTAMENTE da questa sessione** (non da un agente,
  fix di una riga: `validate_class(asset, 'Asset')` invece del confronto esatto), test aggiunto,
  suite 3229 -> 3230 OK.
- **`Transport`/`Storage`/`Urban`/`Production` (Block) e `Structure` (Asset) hanno costruttori
  rotti da sempre** (stub mai finito, copiato 4 volte per i Block, e per `Structure` un bug piu'
  insidioso: `super().__init__()` con un argomento posizionale mancante che fa slittare
  silenziosamente `position`/`volume`/`crytical`/ecc. di una posizione — mai esploso perche' la
  riga dopo, `super.checkParam(...)` con `super` il tipo builtin non l'istanza, solleva
  `AttributeError` prima che il danno si veda). Nessun rischio di regressione: nessuna di queste
  5 classi e' mai stata istanziata con successo in produzione. **Agente Opus lanciato** per
  riscrivere tutti e 5 i costruttori sul modello di `Military.__init__` (funzionante) e correggere
  anche un bug collaterale di `Structure.loadAssetDataFromContext` (stessa famiglia gia' nota per
  Ship/Aircraft: iterazione su dict senza `.items()`).
- **Dottrina di disingaggio per blocchi non-Military**: S7 ha mostrato che un blocco logistico
  bersaglio finisce `DISENGAGED` (assurdo per un deposito). **Decisione dell'utente**: solo le
  forze `Military` vere possono disingaggiarsi; tutte le altre ottengono `thresholds=None`
  incondizionatamente (gia' significa "combatte fino alla fine" nel codice esistente). Stesso
  agente Opus lanciato per questo fix in `Engagement_Resolver._build_forces` (controllo con
  `validate_class(force, 'Military')`, non un campo stringa `category`).

**FATTO e verificato** (suite 3230 -> 3277 OK, rieseguita indipendentemente): `Transport`/
`Storage`/`Urban`/`Production` riscritte sul modello di `Military.__init__` (keyword args, niente
piu' `block`/`mil_category`/`acp`/`rcp`/`payload`/`checkParam` morti), con validazione opzionale
di `sub_category` contro `Context.BLOCK_INFRASTRUCTURE_ASSET` via una nuova
`Context.validate_infrastructure_sub_category(block_class, sub_category)` condivisa.
`Asset/Structure.py` corretto (mapping keyword corretto verso `Asset.__init__`, `production=None`
non esposto, `checkParam` riscritto — era rotto anche lui, leggeva la tabella sbagliata —
`loadAssetDataFromContext` con `.items()`). **Dottrina non-Military**: nuovo
`Engagement_Resolver._can_disengage(force)` — `True` per `Military` vera, `True` anche per
oggetti duck-typed che non sono affatto un `Block` (preserva i ~100 test esistenti con stub),
`False` per ogni `Block` reale non-Military. Letto il codice, verificato corretto.

**Altri bug pre-esistenti trovati e NON corretti** (fuori perimetro, per una sessione futura):
`Manager.py:38-41` costruisce blocchi con `region` posizionale (finirebbe in `name`) — probabile
codice morto da verificare se ancora usato; `Structure.loadAssetDataFromContext` resta rotto oltre
il fix `.items()` (`t2r` e' una tupla ma `repair_time` vuole un int); `Structure.getBlockInfo` usa
`STRUCTURE_ASSET_CATEGORY` mai definito; `Structure.set_volume_from_physical_characteristics`
chiama `Volume(length=, width=, height=)` con una firma che non corrisponde a quella reale;
`Block.sub_category` setter non applica la nuova validazione (solo il costruttore la fa).

**FASE 7 COMPLETA e verificata 2026-09-23** (suite finale: **3326 test, OK, skipped=5, 0
fallimenti**) — e' l'ultima delle 7 fasi del motore DES. Percorso: un primo agente ha scritto
`Test/Scenario_Fixtures.py` (harness) + `Test_Session_Validation.py` (determinismo + agnosticismo
come test di CONTRATTO — nessun adapter DCS esiste nel codice Python, quindi non c'e' nulla da
"rimuovere": verifica strutturale via `typing.get_type_hints` + AST-check anti-DCS + run end-to-end
con soli dati sintetici) + `Test_Session_Scenarios.py` (S1-S9). Un secondo agente ha scritto
`Test_Session_Scenarios_S10_S18.py` (S10-S18) ma e' stato interrotto da un rate-limit Opus a meta'
— il lavoro pero' era gia' quasi tutto scritto su disco (1099 righe), sono rimasti solo 8
fallimenti nelle asserzioni non ancora rifinite. Un terzo agente li ha diagnosticati e corretti
tutti (dettaglio: 5 erano assunzioni sbagliate sui tempi/soglie del motore reale, 3 erano dovuti a
un problema di plausibilita' nell'intercettazione, v. sotto) — nessun bug del motore corretto in
questa fase, solo harness/asserzioni.

**Finding importante emerso dalla Fase 7, NON un bug**: `Military.salvo_interception_capacity()`
usava lo stesso contatore `Mobile.ammunition` sia per sparare offensivamente sia per intercettare —
per un cannone antiaereo (es. ZSU-23-4, 2000 colpi nel registro) questo rende l'intercettazione di
fatto illimitata (88 missili su 88 intercettati in un test). E' esattamente cio' che R1 della Fase 4
dichiarava come "stima di partenza da ricalibrare", ma l'effetto pratico e' piu' estremo del voluto.
**Decisione dell'utente**: separare ORA la scorta di intercettori da quella offensiva (non ridurre
la Pk, non e' stato chiesto). Agente Opus lanciato: nuovo `Mobile.interceptor_stock` distinto da
`ammunition`, popolato con regola diversa per missili (stesso conteggio gia' corretto) e cannoni
(nuova costante dichiarata `ROUNDS_PER_GUN_INTERCEPT`, es. 50-100 colpi per tentativo, cosi' i 2000
colpi dello ZSU diventano ~20-40 intercettazioni invece di 2000). Impatta anche i test S12-S14/S16
della Fase 7 (scritti attorno al bug), da aggiornare nello stesso lavoro. V. quando torna per
l'esito e i numeri concreti.

**`interceptor_stock` FATTO e verificato** (suite 3326 -> 3352 OK): nuovo contatore `Mobile.
interceptor_stock` distinto da `ammunition`, con `ROUNDS_PER_GUN_INTERCEPT = 100` (STIMA
DICHIARATA, tra le 75-150 di un CIWS e le 150-200 di raffica dello Shilka) per i sistemi a cannone
(Shilka 2000->20, Gepard 680->6, VADS 2100->21), conteggio diretto dei missili per i SAM (Buk 4->4,
S-300 4->4, Osa/Tor/Strela-10 6-8->stesso), somma per il solo sistema misto nei registri
(Tunguska: 8 missili + 1904//100 = 27). Route separati in Engagement_Resolver/apply_engagement_result.

**2 rifiniture ulteriori chieste dall'utente, agente Opus lanciato**:
1. **`InterceptionEvent` dedicato** (non piu' `AmmunitionEvent` con `purpose=PURPOSE_INTERCEPTION`)
   — tocca `Engagement_Resolver.py` (nuovo tipo + `EngagementResult.interception_events`) e
   `Command/Session_Types.py` (`SessionOutcome.interception_events` + `interceptions_consumed()`;
   `ammunition_consumed()` torna a contare SOLO munizioni offensive).
2. **Scorta condivisa per i SAM puri** (solo missile, zero cannone: Buk/S-300/Osa/Tor/Strela-10
   ecc.) — `ammunition` e `interceptor_stock` diventano lo stesso pool fisico (sparare consuma
   anche la capacita' di intercettare e viceversa); i sistemi a cannone puro e il misto Tunguska
   restano con contatori indipendenti come appena implementato, invariati.

**Verifica richiesta dall'utente e fatta 2026-09-23 — CONFERMA la decisione sopra**: l'utente ha
dubitato che un Buk avesse davvero due pool di missili distinti. Controllato `Vehicle_Data.py` per
Buk/S-300PS/9A33-Osa/9K331-Tor/9K35-Strela-10: **tutti** hanno `weapons = {'MISSILES':
[(modello, quantita')]}`, un solo numero per veicolo, documentato nel codice sorgente come
`#{'model': quantity}` — nessuna distinzione offensivo/difensivo nella fonte dati. Per un Buk i 4
missili sono i 4 missili fisici sui binari del TELAR (coerente con la realta': nessuna scorta
extra sul mezzo, le ricariche sono un'altra unita' di batteria non modellata). Conferma che
`ammunition` e' gia' l'inventario fisico totale, non una sotto-allocazione per un ruolo: la scorta
condivisa per i SAM puri non e' solo una scelta di design ragionevole ma la lettura corretta della
fonte dati.

**Nota dell'utente sui dati (2026-09-23, per lavoro futuro sui registri, nessuna azione ora)**:
Buk-M1 e M2 montano 4 missili (coerente col dato attuale in `Vehicle_Data.py`, `'9K37-Buk'` = 4,
nessuna correzione necessaria), la variante Buk-M3 ne monta 6 ma non esiste ancora come voce
separata nel registro (c'e' solo `9K37-Buk` generico, verificato: nessun'altra voce Buk). Se in
futuro si aggiunge una voce Buk-M3, va con 6 missili, non 4.

**`InterceptionEvent` + scorta condivisa SAM: FATTO e verificato** (suite 3352 -> 3369 OK). Nuovo
tipo `InterceptionEvent` (campi: time, asset_id=l'intercettore, interceptions, force_id,
salvo_ids) sostituisce `AmmunitionEvent(purpose=PURPOSE_INTERCEPTION)`; `purpose`/`PURPOSE_SALVO`/
`PURPOSE_INTERCEPTION` rimossi da `AmmunitionEvent` (ora solo munizioni offensive).
`SessionOutcome.interception_events` + `interceptions_consumed()` nuovo, `ammunition_consumed()`
ora conta solo munizioni offensive (comportamento cambiato, documentato). Scorta condivisa per i
SAM puri (Strela-1, Chaparral, Osa, Strela-10, Roland, Tor, Kub, Buk, S-300PS, CVN-70/75,
CV-59) confermata da una verifica sui registri (v. sopra): un asset con missili AD e zero cannoni
AD e la cui `ammunition` coincide esattamente con quei missili condivide `ammunition`/
`interceptor_stock` come UN pool fisico (nuovo flag `Mobile.interceptor_shares_ammunition`).
Restano indipendenti: sistemi a cannone puro (Shilka, VADS, Gepard, ZSU-57-2), il misto Tunguska,
e — scelta conservativa dell'agente, non ancora discussa con l'utente — ogni nave con SAM (perche'
le navi non hanno mai `AA_CANNONS`, quindi il solo criterio "niente cannone" le farebbe tutte
condividere, includendo erroneamente cannoni navali/missili antinave nel pool: serve la terza
condizione "ammunition == solo missili AD" per escluderle) e l'M6-Linebacker (Stinger + cannone
25mm non-AD). **Fix mio diretto**: `Session_Simulator._engaged_assets` non contava piu' le
intercettazioni (ora tipo separato) ai fini del regime carburante — asset che intercetta soltanto
finiva a consumo 'nominal' invece di 'max'. Corretto con un test di regressione dedicato
(`TestEngagedAssetsCountsInterceptions`). Suite finale: **3371 test OK (skipped=5)**.

**FASE 7 CONCLUSA — motore DES COMPLETO (7/7 fasi).** Wiki aggiornata
([[project_route_model_unification_plan]] non serve piu' toccarla per questo). **Prossimo passo
per l'utente**: nessuno obbligatorio. Possibili seguiti gia' annotati altrove in questo file:
selezione arma dai registri per `fire_control` (Fase 4, mai fatta), fog-of-war reale collegato a
`detection_factor` (gap S9), il manualetto Markdown con diagrammi UML (v. sezione dedicata sotto,
da fare a fine sviluppo — che e' ORA, quindi diventa rilevante se l'utente lo chiede).

**How to apply**: il motore DES e' COMPLETO e verificato (3371 test). La sessione ha ancora TUTTO
da committare (nessun commit fatto dopo Fase 6 `a968b549`): Fase 7 intera (S1-S18 + harness +
determinismo/agnosticismo), il fix di 5 classi rotte (Transport/Storage/Urban/Production/
Structure), la dottrina non-Military, il fix di `Block.set_asset`, la ricalibrazione
dell'intercettazione in 3 tempi (interceptor_stock -> InterceptionEvent -> pool condiviso SAM), e
il fix del regime carburante per gli intercettori. Se questa riga non e' stata aggiornata a
"committato", il commit finale non e' ancora avvenuto: farlo prima di qualunque altro lavoro.

## ATTIVITA' REGISTRATA PER LA FINE DELLO SVILUPPO DEL MOTORE DES (richiesta utente 2026-09-23)

**Non fare ora.** Al termine dello sviluppo del motore (dopo la Fase 7, quando l'intero motore DES
e' fatto e validato), produrre un **manualetto in Markdown** che spiega l'architettura del motore
sia a livello generale sia di dettaglio. Deve includere **tutti i diagrammi/grafici utili** (UML e
altri formati) per chiarire architettura e funzionamento — non solo testo. Contenuto minimo atteso,
da ricavare quando si scrive (non fissato ora): i 4 strati (contratto, scheduler contatti,
risolutore d'ingaggio, applicazione stato), il flusso dati fra `Contact_Scheduler` →
`Engagement_Resolver` → `Session_Types`/`Fuel_Model`, i diagrammi di sequenza degli eventi
(coda heapq, tie-break), i diagrammi di classe dei tipi di dominio (`ContactWindow`,
`EngagementResult`, `SessionOutcome`, ecc.), e il perche' delle scelte chiave (DES vs tick, salva di
Hughes, RNG seedato). V. [[project_uml_generation]] per il workflow/tool UML gia' in uso nel
progetto (PlantUML). Da posizionare probabilmente in `Analysis/WIKI_LLM_SIMULATION/wiki/project/`
o come documento a se' in `Analysis/Document/`, da decidere quando si arriva a scriverlo.

**Modello/effort per questo lavoro (richiesta utente 2026-09-23)**: Sonnet, effort **alto**
(scelta fra alto/medio lasciata a chi esegue: alto perche' e' un deliverable one-shot con diagrammi
che devono essere corretti, non solo testo di sintesi — a differenza dello sviluppo di codice, qui
non serve Opus). Non usare un agente Opus per questo task, a differenza delle fasi di implementazione.

## FASE 6 — orchestratore Session_Simulator + ingaggi N-forze: FATTA 2026-09-23 (suite 3115 -> 3168)

Tre agenti Opus (effort alto) in sequenza nella stessa sessione:
1. `Logic/Session_Simulator.py` (522 righe): `run_session(order, forces_a, forces_b, fire_control,
   ...)` mette in fila `Contact_Scheduler.schedule_contacts` (trova tutti i contatti della
   sessione fra insiemi di blocchi) -> raggruppamento -> `Engagement_Resolver.resolve_engagement`
   -> `apply_engagement_result` (danno/munizioni agli asset reali, subito dopo ogni ingaggio) ->
   `Fuel_Model.build/apply_fuel_event` per il movimento (regime 'max' se l'asset ha combattuto,
   altrimenti 'nominal') -> `Session_Types.assemble_session_outcome`. Coda eventi heapq con due
   tipi (ENGAGEMENT < MOVEMENT a parita' d'istante). Suite 3115 -> 3140.
2. **Bug trovato e corretto**: `Block.__init__`/`Military.__init__` generavano sempre un id con
   suffisso casuale (`Utility.setId`) — due forze ricostruite da zero con lo stesso nome (test,
   replay) avrebbero id, quindi seed e ordine di risoluzione, diversi ad ogni esecuzione. Fix additivo
   e retrocompatibile: entrambi i costruttori accettano ora `id: Optional[str] = None` (passthrough,
   comportamento invariato se assente). Fatto e testato da questa sessione direttamente (non da un
   agente): 6 test nuovi in `Test_Block.py`/`Test_Military.py`. Suite 3140 -> 3146. **In campagna
   il caso comune non era a rischio**: `Campaign_State.restore` applica gli snapshot a oggetti
   Block/Region gia' vivi in memoria, non li ricostruisce da zero.
3. **`Engagement_Resolver` esteso a N forze (2+) simultanee**: problema reale trovato e confermato
   dall'utente con un esempio concreto — una forza X in contatto SOVRAPPOSTO con A e con B veniva
   risolta come due ingaggi separati in sequenza (prima tutto (X,A), poi (X,B) leggendo lo stato
   di X gia' consumato dall'intero primo ingaggio, anche per la parte di tempo in cui X stava
   davvero combattendo entrambi insieme): l'ordine di coda decideva chi "arrivava prima" alle
   risorse di X, un artefatto d'implementazione non della fisica. Fix: nuovo parametro
   `extra_forces` su `resolve_engagement` (retrocompatibile, default vuoto); il flag globale
   `contact_broken: bool` sostituito da `broken_forces: set` **per-forza** (una forza che si
   disingaggia smette di ingaggiare/essere ingaggiata — bersaglio DISINGAGGIATO ma vivo non e'
   piu' raggiungibile — senza fermare le altre coppie della run). `Session_Simulator` raggruppa
   le forze per **componenti connesse** (BFS deterministico per id) invece che per coppie: X/A/B
   collegati da almeno una finestra ciascuno sono risolti con UNA chiamata, stato di X in una
   timeline continua. **Verificato dall'agente stesso** con un confronto automatico fra la versione
   nuova e HEAD su 3000 scenari casuali a 2 forze: esito identico in tutti i casi (garanzia di
   non-regressione oltre alla suite). Verificato da questa sessione: letto il codice di
   `broken_forces`/`_on_launch`, confermata la logica. Suite 3146 -> 3168.

**Precondizione dichiarata nel modulo**: gli id di forza devono essere stabili fra le esecuzioni
(v. punto 2) — chi costruisce forze da zero per test/replay deve passare `id=` esplicito.

**Decisioni prese dall'utente durante la Fase 6**: accettato come limite dichiarato (non da
correggere) che una forza disingaggiata resti disponibile per altri ingaggi nella stessa sessione
(nessuna esclusione/ri-instradamento inventati) e che le salve in volo a fine sessione estendano
`t_end` invece di essere troncate.

**How to apply:** qualunque lavoro sul motore di sessione parte da questo documento, non dal `.txt`
sorgente. Le Fasi 1-6 sono **fatte**: cinematica, percezione, scheduler dei contatti, risolutore
d'ingaggio (ora a N forze), contratto SessionOutcome/RNG di sessione/carburante, orchestratore di
sessione. Prossimo passo: **Fase 7** (validazione: scenari S1-S11, test di determinismo, **test di
agnosticismo** — l'unico esplicitamente richiesto dal vincolo simulator-agnostic).
V. [[project_route_model_unification_plan]] per le fasi 2-5 dell'unificazione del modello di rotta,
[[project_c2_hierarchy_design]] per `Command/` (incluso il riarmo post-sessione confermato il
2026-09-23) e [[feedback_core_simulator_agnostic]] per il vincolo che questo motore serve.
