# Manuale del motore DES di sessioni virtuali — Warfare-Model

Questo manuale descrive l'architettura e il funzionamento del motore di simulazione a eventi
discreti (DES, *discrete event simulation*) che risolve le **sessioni virtuali** della campagna,
cioè i turni sintetici eseguiti senza un giocatore DCS (e, per costruzione, anche quelli con un
giocatore: il core non distingue i due casi, v. capitolo 1).

**Stato del codice descritto**: HEAD del repository al momento della stesura,
commit `f61aa2b7` (2026-09-23), branch `analysis/dce-dcs-persistence`. `git status` non
mostrava, a quella data, modifiche in corso in `Code/Dynamic_War_Manager/Source/`: quanto
descritto qui è quindi il contenuto dei file così come committati, non uno snapshot di lavoro
in corso. Il motore stesso è **completo**: 7 fasi su 7, come registrato nella wiki di progetto
(`Analysis/WIKI_LLM_SIMULATION/wiki/decisions/virtual-session-engine-des.md`) e nella memoria di
sessione del 2026-09-23.

**Nota di perimetro**: in parallelo a questo manuale, un altro filone di lavoro sta estendendo
`Asset/Ground_Weapon_Data.py`, `Asset/Ship_Weapon_Data.py`, `Context/Context.py` e aggiungendo
`Logic/Fire_Control.py` (selezione dell'arma dai registri, oggi assente — v. §6.1). Questo
manuale **non descrive** quelle estensioni: documenta il motore come si presentava a HEAD prima
di quel lavoro, in cui `fire_control` è sempre una funzione iniettata dal chiamante. Un capitolo
successivo dovrà coprire la selezione dell'arma quando quel lavoro sarà concluso.

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
   saturazione, disingaggio, ingaggi a N forze.
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
