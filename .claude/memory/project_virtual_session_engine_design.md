---
name: project-virtual-session-engine-design
description: "Analisi delle due strategie proposte per il motore di esecuzione delle sessioni virtuali (tick a 1 ms vs risoluzione probabilistica) e architettura decisa: DES a coda eventi con scheduling analitico dei contatti. Documento in Analysis/Document/Architettura_esecuzione_sessioni_virtuali_ANALISI.md, 2026-09-21."
metadata:
  type: project
---

**Stato 2026-09-22: analisi COMPLETATA e documentata. FASE 1 (cinematica) e FASE 2 (percezione) FATTE
e committate sul branch `analysis/dce-dcs-persistence` (Fase 1: 3af377c5, Fase 2: 30a6ee55, da
pushare). Prossima: FASE 3, `Logic/Contact_Scheduler.py` — ma prima vanno chiuse le 3 questioni
aperte del §9 del documento (modello `Route` unico fra i tre incompatibili, semantica della perdita
per-asset, se SAM/AAA/EWR entrino nelle tabelle di combat power), v. anche
[[project_session_2026_09_21_summary]].**
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
5. Nessuna `apply_damage`: solo `asset.health = int` (`Asset/Asset.py:207-210`); "Destroyed" già a
   `health ≤ 15` (`DataType/State.py:178-198`).
6. `random` non seedato a livello di modulo (`Tactical_Evaluation.py:360-361`, `Structure.py:128`,
   `Utility.py:320`, DB armi).
7. **Tre modelli Route/Edge/Waypoint incompatibili**; `Air_Route_Manager` (l'unico generatore maturo)
   non produce `DataType.Route`, che è l'unico tipo che l'ecosistema consuma.
8. `DataType/Event.py:81-95` rotto (`self._type` mai assegnato), importato da 8 moduli, nessun test.
9. `Tactical_Evaluation.py:532-579 evaluateGroundRouteDangerLevel` rotta su 3 punti (concetto giusto).
10. **SAM/AAA/EWR hanno combat power ≡ 0** per costruzione (`Context/Context.py:502-507`).
11. `DataType/Threat.py` e `DataType/Volume.py` sono codice morto.

Fondamenta buone già pronte: `Cylinder.innerPoint`/`getIntersection` (404 righe di test),
`Route.travelTimeToEdge`, DB armi con `accuracy × destroy_capacity`, `Combat_Power_Estimation`,
`Tactical_Analysis`, `Military.time2attack`/`combat_range`/`air_defense_volume`.

## Roadmap (7 fasi, nel documento)
0 contratto+RNG → 1 cinematica (sblocca tutto) → 2 percezione → 3 `Logic/Contact_Scheduler.py` →
4 `Logic/Engagement_Resolver.py` + `Context/Reaction_Profile.py` → 5 danno per-asset →
6 `Logic/Session_Simulator.py` → 7 validazione + **test di agnosticismo**.

**How to apply:** qualunque lavoro sul motore di sessione parte da questo documento, non dal `.txt`
sorgente. Le Fasi 1 e 2 (correzioni a codice esistente, senza le quali lo Strato 1 non è scrivibile)
sono **fatte**: si riparte dalla Fase 3, dopo aver chiuso le 3 questioni aperte. V. [[project_c2_hierarchy_design]] per `Command/` e
[[feedback_core_simulator_agnostic]] per il vincolo che questo motore serve.
