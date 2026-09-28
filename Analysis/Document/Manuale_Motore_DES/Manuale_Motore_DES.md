# Manuale del motore DES di sessioni virtuali — Warfare-Model

Questo manuale descrive l'architettura e il funzionamento del motore di simulazione a eventi
discreti (DES, *discrete event simulation*) che risolve le **sessioni virtuali** della campagna,
cioè i turni sintetici eseguiti senza un giocatore DCS (e, per costruzione, anche quelli con un
giocatore: il core non distingue i due casi, v. capitolo 1).

**Stato del codice descritto**: HEAD del repository al momento della stesura iniziale,
commit `f61aa2b7` (2026-09-23), branch `analysis/dce-dcs-persistence`; aggiornato una prima volta
al commit `1d0c1127` (2026-09-26) per le tre estensioni descritte più sotto, e una seconda volta al
commit `6754bf1c` (2026-09-27, codice; `d2d06945` per la sola memoria di sessione) per le quattro
estensioni dell'ultimo aggiornamento (v. sotto). `git status` non mostrava, a quella data,
modifiche in corso in `Code/Dynamic_War_Manager/Source/`: quanto descritto qui è quindi il
contenuto dei file così come committati, non uno snapshot di lavoro in corso. Il motore stesso è
**completo**: 7 fasi su 7, come registrato nella wiki di progetto
(`Analysis/WIKI_LLM_SIMULATION/wiki/decisions/virtual-session-engine-des.md`) e nella memoria di
sessione del 2026-09-23; le estensioni successive (selezione arma, nebbia di guerra, scorta per
arma, cannone di bordo, volumi di rilevamento/intercettazione, pianificatore d'attacco) sono lavoro
posteriore alle 7 fasi, sui moduli satellite che le alimentano dall'esterno (fire control,
pianificazione di rotta/attacco), non sul motore in sé.

**Nota di perimetro (aggiornata)**: alla stesura iniziale il manuale documentava il motore senza
la selezione dell'arma dai registri (`fire_control` era sempre iniettata da un chiamante esterno)
e senza il collegamento della nebbia di guerra alla Pd. Entrambe le estensioni sono state
completate senza modificare il contratto del motore (`resolve_engagement`/`ShotSpec` invariati) e
sono ora descritte al capitolo 4, §4.16-4.18: `Logic/Fire_Control.py` (selezione dell'arma dai
registri d'arma reali più il controllo di portata `ShotSpec.max_range`, commit `15350cc5`,
2026-09-24) e `region_recon_detection_factor`/`recon_detection_factor_fn` in
`Logic/Engagement_Resolver.py` (nebbia di guerra come fattore di rilevamento per-lato, commit
`388e6ea3`, 2026-09-25). I relativi limiti noti sono raccolti nel capitolo 9, §9.1.

**Aggiornamento 2026-09-26 (commit `1d0c1127`, "Proposta A")**: il contatore di scorta aggregato
per asset (`Mobile.ammunition`, decisione R3 del 2026-09-23) è stato sostituito come stato
primario dalla scorta **per modello d'arma** (`Mobile._stores`, nuovo modulo
`Asset/Weapon_Stores.py`); `ammunition`/`interceptor_stock` sono ora viste calcolate su di essa,
e la regola del "SAM puro" (`interceptor_shares_ammunition`) è stata eliminata perché non più
necessaria. `Logic/Fire_Control.py` restituisce ora tutte le armi adatte in ordine di
preferenza (criterio Pk/costo, non solo Pk massima) e il risolutore spara con la prima che ha
ancora scorta. Descritto al capitolo 4, §4.4/§4.5/§4.10/§4.16/§4.17/§4.19; capitolo 7 §7.6;
capitolo 9 §9.1.

**Aggiornamento 2026-09-26/27 (commit `4ddbb089`, `8bd69727`, `815dc35f`, `6754bf1c`)**: quattro
estensioni successive alla Proposta A, tutte fuori dal motore in sé (moduli satellite/dati di
registro), qui riassunte e dettagliate nei capitoli indicati:

1. **Finestre di rilascio delle bombe** (`4ddbb089`, dato di registro, nessun codice consumatore
   ancora): campo `release` per 29 bombe su 32 di `Asset/Aircraft_Weapon_Data.py` (quote/velocità
   minime e massime, angolo di picchiata, resistenza aerodinamica, planata o standoff); le tre
   KGBU-2AO/2PTAB/96r restavano senza (D4, chiusa il 2026-09-28: ora KMGU-2AO/2PTAB con dati di rilascio). Prerequisito
   dati delle due estensioni successive. Capitolo 9, §9.1.
2. **Il cannone di bordo diventa un'arma candidata reale** (`8bd69727`, decisione A2): campo `gun`
   di `Asset/Aircraft_Data.py` (37 modelli), `get_aircraft_gun_rounds` per ripartire i colpi del
   loadout fra cannoni di un armamento misto, propria voce di scorta per arma
   (`Aircraft.stores_from_registry`) e candidatura in `Logic/Fire_Control._candidate_weapons`: un
   aereo può ora ingaggiare un bersaglio di superficie col cannone quando non ha altre armi adatte.
   Capitolo 4, §4.16; capitolo 7, §7.6.
3. **Volumi di rilevamento e intercettazione distinti nel pianificatore di rotta** (`815dc35f`):
   `Logic/Air_Route_Manager.py` separa il volume in cui un sito è ancora in grado di intercettare
   (`ThreatAA`, come prima) dal volume in cui il suo sensore vede l'aereo (`DetectionThreat`,
   nuovo, raggio limitato dall'orizzonte radar); `ThreatMode.AVOID_DETECTION` pianifica
   sull'aggiramento del rilevamento, verificando sempre sui volumi dichiarati se questo basti anche
   a evitare l'intercettazione. Capitolo 7, §7.8.
4. **Il pianificatore d'attacco: profilo e quota di sgancio** (`6754bf1c`, Proposta B): nuovo
   modulo `Logic/Weapon_Delivery.py` (balistica di rilascio unica, `plan_attack_profile`,
   `bomb_engagement_estimate`) e nuovo `Command/Attack_Types.py` (`AttackProfile`,
   `ThreatExposure`); il risolutore ne eredita, per le bombe, una gittata e un tempo di caduta
   reali al posto dei valori di ripiego (`Logic/Fire_Control.shot_spec_for`, decisione B6).
   Capitolo 4, §4.20; capitolo 7, §7.9.

I limiti noti introdotti o modificati da queste quattro estensioni sono raccolti al capitolo 9,
§9.1 e §9.3; la batteria di test è cresciuta a **3645 test, OK (skipped=5)** (capitolo 8).

## Convenzioni di questo manuale

- Ogni affermazione su codice è verificata leggendo il file, con riferimento `percorso:riga`
  rispetto alla radice del repository (`Code/Dynamic_War_Manager/Source/...`).
- I diagrammi sono in blocchi ```mermaid```, tenuti piccoli e leggibili: dove un diagramma
  avrebbe avuto decine di nodi è stato spezzato in più diagrammi per strato o per famiglia di
  tipi.
- "STIMA DICHIARATA" (termine che ricorre nel codice) significa: un numero o una forma
  funzionale scelta come punto di partenza plausibile, non calibrata su dati validati, con la
  provenienza dichiarata nel codice stesso. Questo manuale le riporta come tali, senza
  presentarle come dati misurati.
- Dove il manuale e la wiki di progetto (`Analysis/WIKI_LLM_SIMULATION/wiki/decisions/`)
  divergono, prevale il codice; le divergenze trovate sono raccolte nella nota finale del
  capitolo 6.

## Indice dei capitoli

1. [Scopo e motivazioni](02_Scopo_e_Motivazioni.md) — perché un DES a coda eventi e non il tick
   a 1 ms, i quattro strati, i vincoli di progetto non negoziabili.
2. [Lo strato 0: il contratto delle porte](03_Strato0_Contratto_Porte.md) —
   `Command/Session_Types.py`: `SessionOrder`, `SessionOutcome`, `assemble_session_outcome`.
3. [Lo strato 1: lo scheduler dei contatti](04_Strato1_Scheduler_Contatti.md) —
   `Logic/Contact_Scheduler.py`: rotta↔cilindro, CPA/TCPA, potatura gerarchica,
   `ContactWindow`.
4. [Lo strato 2: il risolutore d'ingaggio](05_Strato2_Risolutore_Ingaggio.md) —
   `Logic/Engagement_Resolver.py`: rilevamento, latenze di reazione, salva di Hughes,
   saturazione, disingaggio, ingaggi a N forze; `Logic/Fire_Control.py` (selezione dell'arma dai
   registri e controllo di portata, §4.16-4.17; cannone di bordo candidato, §4.16bis); nebbia di
   guerra come fattore di rilevamento da ricognizione (§4.18); scorta per modello d'arma,
   `Asset/Weapon_Stores.py` (§4.19); gittata e caduta delle bombe dalla balistica di
   `Weapon_Delivery`, §4.20.
5. [Lo strato 3: applicazione dello stato](06_Strato3_Applicazione_Stato.md) —
   `Logic/Damage_Model.py`, `Asset.apply_damage`, `Logic/Fuel_Model.py`,
   `apply_engagement_result`.
6. [L'orchestratore: `Session_Simulator.run_session`](07_Orchestratore_Session_Simulator.md) —
   componenti connesse, coda eventi di sessione, carburante, sessione aperta.
7. [Moduli di supporto trasversali](08_Supporto_Trasversale.md) — `Session_Rng`, `Doctrine`,
   `Reaction_Profile`, le dimensioni militari di `Military`, munizioni/carburante su
   `Mobile`/`Aircraft`, i punti di iniezione meteo (`detection_factor`) e arma
   (`fire_control`); il pianificatore di rotta aerea con volumi di rilevamento e
   intercettazione distinti (§7.8, `Logic/Air_Route_Manager.py`) e il pianificatore d'attacco
   a monte del motore (§7.9, `Logic/Weapon_Delivery.py`, `Command/Attack_Types.py`).
8. [Validazione](09_Validazione.md) — determinismo, test di agnosticismo come test di
   contratto, la batteria di scenari S1-S18.
9. [Limiti noti, punti di estensione e divergenze codice/wiki](10_Limiti_Estensioni_Divergenze.md).

## Elenco dei diagrammi

| # | Diagramma | Tipo mermaid | Capitolo |
|---|---|---|---|
| D1 | Moduli e dipendenze dei quattro strati | `flowchart TD` | 1 |
| D2 | Tipi di dominio — porte di sessione (`SessionOrder`/`SessionOutcome`) | `classDiagram` | 2 |
| D3 | Tipi di dominio — geometria dei contatti (`Contact_Scheduler`) | `classDiagram` | 3 |
| D4 | Tipi di dominio — ingaggio (`Engagement_Resolver`) | `classDiagram` | 4 |
| D5 | Sequenza della coda eventi dentro un ingaggio | `sequenceDiagram` | 4 |
| D6 | Stati di una forza durante un ingaggio | `stateDiagram-v2` | 4 |
| D7 | Stati operativi di un asset (salute) | `stateDiagram-v2` | 5 |
| D8 | Flusso dati di `run_session` | `flowchart TD` | 6 |
| D9 | Coda eventi di sessione (ENGAGEMENT/MOVEMENT) | `sequenceDiagram` | 6 |
| D10 | `Fire_Control`: catena di selezione dell'arma dai registri | `flowchart TD` | 4 |
| D11 | Controllo di portata: rimando `not_before` di un candidato | `sequenceDiagram` | 4 |
| D12 | Nebbia di guerra: composizione del fattore di rilevamento | `flowchart TD` | 4 |
| D13 | Scorta per modello d'arma: dalla fire control al consumo | `flowchart TD` | 4 |
| D14 | Volumi di rilevamento e intercettazione: tipi e modalità del pianificatore di rotta | `classDiagram` | 7 |
| D15 | Il pianificatore d'attacco: da `plan_attack_profile` all'`AttackProfile`, verso DES e DCS | `flowchart TD` | 7 |
