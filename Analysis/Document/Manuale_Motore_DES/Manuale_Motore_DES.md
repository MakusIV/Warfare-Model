# Manuale del motore DES di sessioni virtuali — Warfare-Model

Questo manuale descrive l'architettura e il funzionamento del motore di simulazione a eventi
discreti (DES, *discrete event simulation*) che risolve le **sessioni virtuali** della campagna,
cioè i turni sintetici eseguiti senza un giocatore DCS (e, per costruzione, anche quelli con un
giocatore: il core non distingue i due casi, v. capitolo 1).

> **Aggiornato al commit `533cd1f5`** (2026-10-05, "F3: la Missione attraversa la porta di sessione"),
> branch `analysis/dce-dcs-persistence`. Suite di test a quel commit: **3922 OK (skipped=7)**.
> Il manuale descrive **lo stato di `533cd1f5`**: le fasi F4-F9 del piano di implementazione della
> Missione (F4 la missione come unità d'ingaggio, F5 presenza e attese, F6 fine missione e carburante nel
> tempo, F7 bersagli e filtro armi, F8 sessione e campagna, F9 documentazione) sono **in corso o da fare** e
> non sono descritte come codice (capitolo 9 §9.5). Il checkout principale può contenere lavoro in corso
> sulla F4: **non** è oggetto di questo manuale, che è stato scritto sulla copia esportata di `533cd1f5`.

**Stato del codice descritto, storia degli aggiornamenti.** Stesura iniziale al commit `f61aa2b7`
(2026-09-23); aggiornamenti a `1d0c1127` (2026-09-26), `6754bf1c` (2026-09-27; manuale committato in
`fb914f0e`) e, ora, a `533cd1f5`. Il motore è **completo** nelle sue 7 fasi originali (wiki
`Analysis/WIKI_LLM_SIMULATION/wiki/decisions/virtual-session-engine-des.md`); tutto ciò che è venuto dopo è
estensione: fino al 2026-09-27 sui moduli satellite che lo alimentano dall'esterno (selezione dell'arma,
nebbia di guerra, scorta per arma, cannone di bordo, volumi di rilevamento/intercettazione, pianificatore
d'attacco), dal 2026-09-28 **anche nel risolutore e nella porta di sessione**.

**Aggiornamento 2026-09-28 → 2026-10-05 (da `6754bf1c` a `533cd1f5`)**, in ordine di capitolo:

1. **Strato 0, la Missione** (capitolo 2 §2.2-2.9): `Command/Mission_Types.py` (tipi di dominio di Missione,
   Operazione, esiti), la tassonomia dei tipi di missione in `Context/Context.py` (`Mission_Category`, tipi per
   dominio, `AIR_COMBAT_TASK` e `AIR_SUPPORT_TASK`, `MISSION_TYPE_POSTURES`: postura e tipo di missione su due
   assi distinti), `SessionOrder.missions`/`operations` e `SessionOutcome.mission_outcomes`; rename della
   postura `Retrait` → `Retreat`.
2. **Orchestratore** (capitolo 6 §6.1, §6.10-6.11): `run_session` non ha più `routes`/`starts`/`speeds`
   (una sola strada: le missioni); `Logic/Mission_Adapter.py` ricava rotta, partenza e velocità per asset
   (offset di formazione che ruota con la rotta sulla bisettrice); esito di missione di prima forma;
   secondo flusso RNG per la tempra.
3. **Risolutore d'ingaggio** (capitolo 4 §4.5, §4.7, §4.21-4.26): soglia di rottura stocastica; efficacia
   antiaerea E(N) e pesi di minaccia; RWR per classi e modalità, classificazione SAM, regola R-CLS; difesa dai
   missili A6 (capacità `Anti_Missile`, ordine F, regole L1/L2/L3); dottrina di tiro contro l'overkill;
   intercettazione con traccia del colpo e tempo di reazione (R-INT).
4. **Supporto trasversale** (capitolo 7 §7.2, §7.5-7.7, §7.10-7.12): `Doctrine` (parametri della soglia,
   dottrina di tiro), `salvo_interceptors` con regola D, CIWS, `Asset/Aircraft_Rwr_Data.py`,
   `Context/Air_Defense_Efficacy.py`, armi DCS aggiunte (39), KMGU-2, Tu-95MS.
5. **Validazione** (capitolo 8 §8.6-8.8): S19 e S19AD, migrazione degli scenari alle missioni, lo strumento
   di non regressione `Test/Scenario_Baseline.py` (292 esecuzioni, `--capture`/`--compare`).
6. **Limiti** (capitolo 9): limiti nuovi e superati, stato del piano della Missione (§9.5) e le incoerenze
   trovate fra documenti di progetto e codice (§9.6).

I capitoli 3 (scheduler) e 5 (applicazione dello stato) sono stati **verificati e risultano invariati**
(`Logic/Contact_Scheduler.py`, `Logic/Damage_Model.py`, `Logic/Fuel_Model.py` non cambiano da `6754bf1c`).

**Storia degli aggiornamenti precedenti** (testo conservato per riferimento):

- *Nota di perimetro 2026-09-24/25*: selezione dell'arma dai registri (`Logic/Fire_Control.py`, commit
  `15350cc5`) e nebbia di guerra come fattore di rilevamento (`region_recon_detection_factor`, commit
  `388e6ea3`), capitolo 4 §4.16-4.18.
- *2026-09-26 (`1d0c1127`, "Proposta A")*: la scorta **per modello d'arma** (`Mobile._stores`,
  `Asset/Weapon_Stores.py`) sostituisce il contatore aggregato; la regola del "SAM puro" è eliminata;
  capitolo 4 §4.4/§4.5/§4.10/§4.16/§4.17/§4.19, capitolo 7 §7.6.
- *2026-09-26/27 (`4ddbb089`, `8bd69727`, `815dc35f`, `6754bf1c`)*: finestre di rilascio delle bombe (dato di
  registro), cannone di bordo come arma candidata (capitolo 4 §4.16bis), volumi di rilevamento e
  intercettazione distinti nel pianificatore di rotta (capitolo 7 §7.8), pianificatore d'attacco con quota e
  profilo di sgancio (capitolo 4 §4.20, capitolo 7 §7.9).

## Convenzioni di questo manuale

- Ogni affermazione su codice è verificata leggendo il file, con riferimento `percorso:riga`
  valido per `533cd1f5`. I percorsi sono dati **relativi a `Code/Dynamic_War_Manager/Source/`** (es.
  `Logic/Engagement_Resolver.py:2251` sta per
  `Code/Dynamic_War_Manager/Source/Logic/Engagement_Resolver.py:2251`); dentro una sezione una forma breve
  `` `:riga` `` si riferisce al file nominato nell'intestazione del capitolo o della sezione. I documenti di
  progetto sono citati con il percorso sotto `Analysis/Document/`.
- I diagrammi sono in blocchi ```mermaid```, tenuti piccoli e leggibili: dove un diagramma
  avrebbe avuto decine di nodi è stato spezzato in più diagrammi per strato o per famiglia di
  tipi.
- "STIMA DICHIARATA" (termine che ricorre nel codice) significa: un numero o una forma
  funzionale scelta come punto di partenza plausibile, non calibrata su dati validati, con la
  provenienza dichiarata nel codice stesso. Questo manuale le riporta come tali, senza
  presentarle come dati misurati.
- Dove il manuale e la wiki di progetto (`Analysis/WIKI_LLM_SIMULATION/wiki/decisions/`)
  divergono, prevale il codice; le divergenze trovate sono raccolte nel capitolo 9 (§9.2 per la wiki,
  §9.6 per i documenti di progetto della Missione e delle regole SAM).
- I diagrammi hanno un numero progressivo `D1`-`D29` (elenco in fondo); le didascalie sono nel capitolo
  che li contiene.

## Indice dei capitoli

1. [Scopo e motivazioni](02_Scopo_e_Motivazioni.md) — perché un DES a coda eventi e non il tick
   a 1 ms, i quattro strati, i vincoli di progetto non negoziabili.
2. [Lo strato 0: il contratto delle porte](03_Strato0_Contratto_Porte.md) —
   `Command/Session_Types.py`: `SessionOrder`, `SessionOutcome`, `assemble_session_outcome`; dal
   2026-10-05 le missioni alla porta (`SessionOrder.missions`/`operations`, `mission_outcomes`),
   `Command/Mission_Types.py` (§2.6) e la tassonomia dei tipi di missione di `Context/Context.py` (§2.7).
3. [Lo strato 1: lo scheduler dei contatti](04_Strato1_Scheduler_Contatti.md) —
   `Logic/Contact_Scheduler.py`: rotta↔cilindro, CPA/TCPA, potatura gerarchica,
   `ContactWindow`.
4. [Lo strato 2: il risolutore d'ingaggio](05_Strato2_Risolutore_Ingaggio.md) —
   `Logic/Engagement_Resolver.py`: rilevamento, latenze di reazione, salva di Hughes,
   saturazione, disingaggio, ingaggi a N forze; `Logic/Fire_Control.py` (selezione dell'arma dai
   registri e controllo di portata, §4.16-4.17; cannone di bordo candidato, §4.16bis); nebbia di
   guerra come fattore di rilevamento da ricognizione (§4.18); scorta per modello d'arma,
   `Asset/Weapon_Stores.py` (§4.19); gittata e caduta delle bombe dalla balistica di
   `Weapon_Delivery`, §4.20; **dal 2026-09-28**: soglia di rottura stocastica (§4.7, §4.21), efficacia
   antiaerea E(N) (§4.22), RWR e classi SAM con regola R-CLS (§4.23), difesa dai missili A6 con regole
   D/F/L1/L2/L3 (§4.24), dottrina di tiro contro l'overkill (§4.25), intercettazione con tempo di reazione
   R-INT (§4.26).
5. [Lo strato 3: applicazione dello stato](06_Strato3_Applicazione_Stato.md) —
   `Logic/Damage_Model.py`, `Asset.apply_damage`, `Logic/Fuel_Model.py`,
   `apply_engagement_result` (verificato a `533cd1f5`: invariato).
6. [L'orchestratore: `Session_Simulator.run_session`](07_Orchestratore_Session_Simulator.md) —
   componenti connesse, coda eventi di sessione, carburante, sessione aperta; la nuova firma senza
   `routes`/`starts`/`speeds`, `Logic/Mission_Adapter.py` (§6.10) e l'esito di missione di prima forma
   (§6.11).
7. [Moduli di supporto trasversali](08_Supporto_Trasversale.md) — `Session_Rng`, `Doctrine`,
   `Reaction_Profile`, le dimensioni militari di `Military`, munizioni/carburante su
   `Mobile`/`Aircraft`, i punti di iniezione meteo (`detection_factor`) e arma
   (`fire_control`) e della soglia di rottura (`morale_for`, `enemy_estimate_for`, `fire_doctrine`,
   `rwr_catalogue`); `Doctrine` con parametri della soglia e dottrina di tiro (§7.2);
   `Asset/Aircraft_Rwr_Data.py` (§7.10), `Context/Air_Defense_Efficacy.py` (§7.11), dati di registro
   aggiunti (§7.12); il pianificatore di rotta aerea con volumi di rilevamento e
   intercettazione distinti (§7.8, `Logic/Air_Route_Manager.py`) e il pianificatore d'attacco
   a monte del motore (§7.9, `Logic/Weapon_Delivery.py`, `Command/Attack_Types.py`).
8. [Validazione](09_Validazione.md) — determinismo, test di agnosticismo come test di
   contratto (esteso alle porte della Missione), la batteria di scenari S1-S19 (S19, S19AD), la migrazione
   alle missioni, lo strumento di non regressione `Test/Scenario_Baseline.py` (§8.7), i test aggiunti
   (§8.8).
9. [Limiti noti, punti di estensione e divergenze codice/wiki](10_Limiti_Estensioni_Divergenze.md) —
   limiti nuovi e superati, stato del piano della Missione F0-F9 (§9.5), incoerenze trovate fra documenti di
   progetto e codice (§9.6).

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
| D16 | Modello dei tipi della Missione (`Mission`, `MissionAsset`, `MissionWaypoint`, ...) | `classDiagram` | 2 |
| D17 | Esiti della Missione (`MissionOutcome`, `AssetMissionOutcome`) | `classDiagram` | 2 |
| D18 | I due assi: postura tattica e tipo di missione | `flowchart LR` | 2 |
| D19 | Esito di missione, prima forma | `flowchart TD` | 6 |
| D20 | Pipeline di `Mission_Adapter` | `flowchart TD` | 6 |
| D21 | Offset di formazione ai cambi di direzione | `flowchart TD` | 6 |
| D22 | Composizione della soglia di rottura B(t) | `flowchart TD` | 4 |
| D23 | Minaccia percepita: sistema esatto o classe RWR (R-CLS) | `flowchart TD` | 4 |
| D24 | Allocazione delle intercettazioni per salva (ordine F, L1, R-INT) | `flowchart TD` | 4 |
| D25 | Priorità ai lanciatori: prelazione L3 | `sequenceDiagram` | 4 |
| D26 | Dottrina di tiro: bersagli bloccati, attesa, round-robin | `flowchart TD` | 4 |
| D27 | Regola R-INT: traccia del colpo e tempo di reazione | `flowchart TD` | 4 |
| D28 | `Air_Defense_Efficacy`: profili, dati RWR, funzioni | `classDiagram` | 7 |
| D29 | Fasi F0-F9 del piano della Missione | `flowchart LR` | 9 |

I diagrammi D1, D2, D4, D5, D6, D8 e D9 sono stati **aggiornati** a `533cd1f5` (nuovi tipi, campi e passi);
il D3 (scheduler) e il D7 (stati di salute) sono invariati.

