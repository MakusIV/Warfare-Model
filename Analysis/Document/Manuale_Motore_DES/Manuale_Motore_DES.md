# Manuale del motore DES di sessioni virtuali — Warfare-Model

Questo manuale descrive l'architettura e il funzionamento del motore di simulazione a eventi
discreti (DES, *discrete event simulation*) che risolve le **sessioni virtuali** della campagna,
cioè i turni sintetici eseguiti senza un giocatore DCS (e, per costruzione, anche quelli con un
giocatore: il core non distingue i due casi, v. capitolo 1).

**Stato del codice descritto**: HEAD del repository al momento della stesura iniziale,
commit `f61aa2b7` (2026-09-23), branch `analysis/dce-dcs-persistence`; aggiornato al commit
`1d0c1127` (2026-09-26) per le tre estensioni descritte più sotto. `git status` non mostrava, a
quella data, modifiche in corso in `Code/Dynamic_War_Manager/Source/`: quanto descritto qui è
quindi il contenuto dei file così come committati, non uno snapshot di lavoro in corso. Il motore
stesso è **completo**: 7 fasi su 7, come registrato nella wiki di progetto
(`Analysis/WIKI_LLM_SIMULATION/wiki/decisions/virtual-session-engine-des.md`) e nella memoria di
sessione del 2026-09-23.

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
   registri e controllo di portata, §4.16-4.17); nebbia di guerra come fattore di rilevamento da
   ricognizione (§4.18); scorta per modello d'arma, `Asset/Weapon_Stores.py` (§4.19).
5. [Lo strato 3: applicazione dello stato](06_Strato3_Applicazione_Stato.md) —
   `Logic/Damage_Model.py`, `Asset.apply_damage`, `Logic/Fuel_Model.py`,
   `apply_engagement_result`.
6. [L'orchestratore: `Session_Simulator.run_session`](07_Orchestratore_Session_Simulator.md) —
   componenti connesse, coda eventi di sessione, carburante, sessione aperta.
7. [Moduli di supporto trasversali](08_Supporto_Trasversale.md) — `Session_Rng`, `Doctrine`,
   `Reaction_Profile`, le dimensioni militari di `Military`, munizioni/carburante su
   `Mobile`/`Aircraft`, i punti di iniezione meteo (`detection_factor`) e arma
   (`fire_control`).
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
