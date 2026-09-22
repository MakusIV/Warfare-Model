# Log delle Operazioni Wiki

## [2026-09-22] aggiornamento | Batteria di validazione Fase 7 estesa da S1-S5 a S1-S11

Su richiesta esplicita dell'utente ("ulteriori scenari di test oltre S1-S5"). I 5 scenari
ereditati da [[source-lanchester-scenari-ai]] coprono solo terra/aria a due parti, ingaggio
singolo, forze già in contatto — non toccano il dominio navale, i bersagli economici/logistici,
la scala (10.000 asset), il fog-of-war, la soglia di disingaggio proposta in P1 (nessuna fonte
la implementava), né il confine sessione-DCS/sessione-sintetica.

**6 nuovi scenari definiti per questa sessione** (non derivati da alcuna fonte esterna) in
[[soglie-disingaggio-e-attrito-aggregato]] § P3, ciascuno mirato a un meccanismo specifico del
motore non esercitato da S1-S5: S6 gruppo navale vs difesa costiera, S7 interdizione di linea
logistica (bersaglio `Production`/`Storage`/`Transport`, non `Military`), S8 fronte multiplo /
stress di scala (verifica la potatura gerarchica del `Contact_Scheduler`), S9 targeting sotto
fog-of-war parziale (`recon_cp_snapshot`), S10 regressione mirata sulla soglia di disingaggio
(test di non-regressione di P1 stessa), S11 confine sessione DCS/sintetica (test end-to-end del
contratto `SessionOrder`/`SessionOutcome`, l'unico esplicitamente richiesto dalla roadmap
originale per la Fase 7).

Aggiunto un quinto punto aperto: S6-S11 sono una proposta di partenza di questa sessione, non
ancora confermata come batteria ufficiale.

---

## [2026-09-22] ingestione | Modelli Lanchester e scenari applicati (9 `.docx`, `RAW/Lanchester/`)

**Fonte**: 9 file `.docx` (+ uno `.zip` ridondante, ignorato). Letti integralmente. Verificato nel
testo che **non sono 9 fonti indipendenti** ma i turni di **una sola sessione conversazionale** con
un assistente AI: ogni documento si chiude con la domanda che titola il successivo, e `…CAS(1).docx`
è la ri-emissione della sola tabella finale di `si introduci una missione SEAD preliminare.docx`
(numeri identici). Da qui la scelta di **una sola pagina `sources/`**, con tabella per-documento.

**Esito della valutazione**: **negativo sulla matematica, parzialmente positivo sulla struttura.**
Il doc 04 è l'unico a carattere bibliografico (Bracken generalizzato, legge 1.5, KDB/Dupuy,
eterogeneo vettoriale, Peterson, Helmbold, SINDy, fattore informativo $\mu$) ma con **citazioni che
sono nomi di dominio nudi**, non verificabili. Gli altri otto sono esercizi numerici con
coefficienti dichiarati «ipotizzati», risolti con **un singolo passo di Eulero a $\Delta t = 1$
giorno**. **Nessuna equazione a salva (Hughes) in tutto il set**: nessuna sovrapposizione con lo
strato 2 previsto.

**Difetti specifici trovati** (dettaglio in [[lanchester-vs-motore-des]] § 3): attrito indipendente
dalla numerosità della forza che lo subisce (doc 06: 8,5 velivoli persi su 20 presenti); output
frazionario e aggregato, incompatibile col vincolo «perdite per singolo asset»; determinismo senza
varianza; **il confronto SEAD/non-SEAD del doc 06 è un artefatto del cambio di ordine di risoluzione
fra le due simulazioni**, non un effetto del SEAD — dimostrazione involontaria del vincolo #2 di
[[virtual-session-engine-des]]; il doc 02 dichiara legge lineare/quadratica e poi calcola tutto a
fuoco mirato; il doc 05 afferma «4-5 caccia abbattuti» dove i suoi stessi coefficienti danno 0,9.

**Falso allarme risolto**: il doc 04 chiama «validazione» il fit Ardenne/Kursk che il progetto
registra come «9 test falliti». **Non è una contraddizione** — entrambi dicono che le leggi
classiche non tengono; il doc chiama validazione un fit a posteriori con due parametri liberi.
L'avvertimento metodologico di [[virtual-session-engine-des]] **resta invariato** e non è stato
toccato.

**Verifica strato 1 vs strato 2**: confermata l'ipotesi, e più nettamente. Nei 9 documenti **non
compare una sola coordinata, velocità, rotta, portata o tempo di contatto**: il contatto è assunto a
$t=0$. Lo scheduler dei contatti (Fase 3, in lavorazione da un altro agente) **non è toccato**.
Corollario registrato: la sequenza di fasi che i documenti cablano a mano
(MR-SAM → SHORAD → AAA) è esattamente ciò che lo strato 1 produce dalla geometria — argomento *a
favore* dell'architettura già scelta.

**Pagine create (4)**:
- `wiki/sources/source-lanchester-scenari-ai.md`
- `wiki/concepts/lanchester-models.md` — colma la lacuna dichiarata in `overview.md` («Fonti sui
  modelli Lanchester»), almeno come tassonomia
- `wiki/analyses/lanchester-vs-motore-des.md` — **prima pagina `analyses/` del wiki**
- `wiki/decisions/soglie-disingaggio-e-attrito-aggregato.md` — **`status: proposed`**, richiede
  decisione dell'utente

**Pagine aggiornate (3)**: `index.md`, `log.md`, `overview.md`.

**Nessun file di codice toccato.** Analisi e ingestione soltanto.

---

## [2026-09-22] aggiornamento | Chiusi i 3 punti aperti dopo Q1-Q3 (SEAD, MIN_EFFECTIVE_HIT_DAMAGE, Edge.calcLength) + bug intersectPoint

**SEAD collegato** (commit `efb93cab`): `Tactical_Evaluation.calculate_priority` legge
`Military.air_defense_power()` del bersaglio quando l'attaccante è aereo e il target ha combat
power 0 — prima saturava sempre al floor 0.1, quindi un C2 aereo non avrebbe mai visto un sito
SAM come bersaglio prioritario. Mappatura lineare `[0,1]→[0.1,10.0]`, stessa scala degli altri
rami. Attaccanti ground/sea invariati. Trovato e corretto un fixture di test rotto dal nuovo call
site (`TestCalculatePriorityTargetAffinity._target`, mock `spec=Military` senza
`air_defense_power` configurato).

**`MIN_EFFECTIVE_HIT_DAMAGE`**: confermata, nessuna modifica.

**`Edge.calcLength()`**: il commento era il bug (dichiarava una distinzione 2D/3D per
`path_type` mai implementata), corretto il commento, codice invariato — le posizioni asset
hanno già quota reale anche a terra, la 3D è la scelta fisicamente corretta.

**Bug trovato per strada, corretto separatamente** (commit `5a87ebb2`, prima di questi 3 punti):
`Edge.intersectPoint(Line2D)` intersecava la retta 3D dell'edge invece della sua proiezione 2D
— falso negativo silenzioso per ogni edge non a quota zero. Zero chiamanti in produzione oggi
(dormiente), nuovo `Test_Edge.py` (prima nessuna copertura).

**3 pagine `wiki/decisions/`/`wiki/project/` aggiornate**: [[virtual-session-engine-des]],
[[route-model-unification]], [[block]] — le note "da confermare con l'utente" sostituite con
l'esito reale.

---

> **Registro cronologico** in sola aggiunta di tutte le operazioni sul wiki.
> Formato voci: `## [YYYY-MM-DD] tipo | Descrizione`
>
> Tipi: `ingestione` | `query` | `health-check` | `aggiornamento` | `setup`
>
> **Ricerca rapida** (da terminale):
> ```bash
> grep "^## \[" wiki/log.md | tail -10    # ultime 10 voci
> grep "ingestione" wiki/log.md            # tutte le ingestioni
> grep "query" wiki/log.md                 # tutte le query
> ```

---

## [2026-09-22] aggiornamento | Sync motore sessioni virtuali (DES): 2 nuove decisioni + 3 pagine project aggiornate

**Applicazione della regola "SYNC EVOLUZIONE PROGETTO"**, su richiesta esplicita dell'utente
("allinea i contenuti del wiki con le decisioni sul sistema di simulazione virtuale"), mentre due
subagent lavoravano in parallelo su `analysis/dce-dcs-persistence` (Fase 2 appena chiusa, e le 3
questioni aperte pre-Fase 3 in corso). Colma un buco reale: tutto il lavoro del 2026-09-18/21 su
quel branch (mai mergiato in `main`) non era mai arrivato al wiki.

**2 nuove pagine `wiki/decisions/`**:
- [[virtual-session-engine-des]] — verdetto sulle due strategie proposte dall'utente (tick 1ms
  scartato: 74 giorni di calcolo proiettati; probabilistica incompleta: non dice quando due forze
  si incontrano), architettura DES a coda eventi scelta, roadmap a 7 fasi, stato Fase 1
  (cinematica, `3af377c5`) e Fase 2 (percezione/`ThreatAA`, `30a6ee55`) — entrambe fatte e
  pushate, non ancora su `main`.
- [[core-simulator-agnostic]] — il vincolo architetturale dichiarato dall'utente il 2026-09-18
  (core indifferente al simulatore, DCE come controesempio negativo analizzato in dettaglio),
  contratto `SessionOrder`/`SessionOutcome`, ordine di lavoro imposto (contratto → resolver
  sintetico → campagna senza simulatore → solo dopo l'adapter DCS).

**3 pagine `wiki/project/` aggiornate** (non solo aggiunte — anche bug ormai risolti spostati
dalla sezione "confermati" a "risolti"): [[asset-base]] (schema `SPEED_SCHEMA`/`Mobile.speed` in
m/s, `detection_range`, e soprattutto il bug storico `Mobile.checkParam` senza `self` — confermato
ancora presente il 2026-09-18 — ora marcato risolto dalla Fase 1), [[block]] (nuovi
`Military.air_defense_threats()`/`detection_range()`), [[logic-routing]] (fabbrica
`build_threat_aa()`, e nota esplicita che la triplicazione `Route`/`Edge`/`Waypoint` — già nota
dal 2026-08-21 — è ora una precondizione bloccante per il `Contact_Scheduler`).

**Pagina esistente annotata, non riscritta**: [[datatype-route-edge-waypoint]] — aggiunta una nota
che segnala la rivalutazione in corso (sessione parallela al 2026-09-22) della scelta "Air resta
separato da `DataType.Route`", senza presumerne l'esito.

**Deliberatamente non fatto in questa sessione**: le 3 questioni aperte pre-Fase 3 (modello
`Route` vincente, semantica della perdita per-asset, SAM/AAA/EWR nel combat power) sono in
lavorazione in una sessione parallela sullo stesso branch — il wiki le registra come "in corso"
in [[virtual-session-engine-des]] e [[logic-routing]], da aggiornare con l'esito reale a lavoro
concluso, per non contraddire una decisione ancora da prendere.

---

## [2026-09-22] aggiornamento | Riconciliazione: le 3 questioni pre-Fase 3 sono state chiuse

**Seguito diretto della voce precedente**: la sessione parallela ha completato le 3 decisioni
mentre questa sessione scriveva il wiki. Riconciliazione fatta leggendo i 4 commit reali
(`6c421579`/`f1f5b7d4`/`64538f16`/`27d53e56`) e le memorie che li accompagnano, non i placeholder
"in corso" scritti prima.

**1 nuova pagina `wiki/decisions/`**: [[route-model-unification]] — `DataType.Route` confermato
unico modello di dominio anche per l'aria (non solo ground come deciso in agosto); le classi
locali di `Air_`/`Ground_Route_Manager` restano come stato di lavoro privato della ricerca;
nuovo `Logic/Route_Adapter.py` alla frontiera pubblica; piano a 5 fasi, Fase 1 fatta. Il blocco
tecnico reale era un bug in `DataType/Edge.py` (segmenti degeneri non costruibili con sympy per
una salita verticale pura), non una difficoltà architetturale.

**[[datatype-route-edge-waypoint]] marcata `superseded`** (era `accepted` con nota provvisoria
"in rivalutazione") → `superseded_by: [[route-model-unification]]`, come da convenzione ADR di
questo wiki.

**[[virtual-session-engine-des]] aggiornata** con l'esito reale delle 3 questioni: Q1 v. sopra;
Q2 (perdita per-asset) → nuovo `Logic/Damage_Model.py` + `Asset.apply_damage()`, contratto
Ph×Pk|h da `accuracy`/`destroy_capacity` già nei registri arma, soglia `Destroyed ≤ 15`
confermata invariata; Q3 (SAM/AAA/EWR) → combat power 0 confermato intenzionale, nuova
dimensione separata `Military.air_defense_power()` (non una tabella di efficacia inventata,
scartata deliberatamente dal subagent che ha fatto il lavoro).

**3 pagine `wiki/project/` aggiornate di conseguenza**: [[logic-routing]] (`Route_Adapter.py`,
correzione della frase "Air resta deliberatamente sulle sue classi locali", ormai imprecisa),
[[asset-base]] (`Asset.apply_damage`), [[block]] (`Military.air_defense_power`).

**Verifica indipendente** (non solo lettura del report del subagent): suite riesguita per
intero, **2753 test, 1 fallimento non riproducibile** (`testCalcFightResult`, isolato e
rieseguito 8/8 volte in verde) — dovuto a `random.uniform` non seedato in
`Tactical_Evaluation.calcFightResult`, file **non toccato** dai 4 commit in esame; non è una
regressione, è il gap già tracciato in [[virtual-session-engine-des]] ("random non seedato a
livello di modulo").

**3 punti restano da confermare con l'utente prima della Fase 4** (segnalati esplicitamente dal
subagent, non decisi unilateralmente): collegare `air_defense_power` alla priorità di targeting
SEAD (cambio di game balance); la costante `MIN_EFFECTIVE_HIT_DAMAGE = 1` in `Damage_Model.py`
(altrimenti le infrastrutture, `destroy_capacity ≈ 0`, sarebbero indistruttibili per
costruzione); se il bug in `Edge.calcLength()` (non distingue per `path_type` nonostante il
commento) sia il codice o il commento a dover cambiare.

---

## [2026-09-18] aggiornamento | TASK 2 (Fase A) implementato: RegionInfoReport / Meteo_Analysis / limes

**Prima applicazione della regola "SYNC EVOLUZIONE PROGETTO"** aggiunta a `CLAUDE.md` nella stessa giornata: implementazione di codice, non solo documentazione, quindi wiki aggiornato nella stessa sessione invece di aspettare.

**Codice consegnato** (v. [[c2-hierarchy-design]] per il dettaglio completo): property pubblica `Region.limes` (sola lettura); nuovo `Logic/Meteo_Analysis.py` (placeholder meteo deterministico, shape identica a `mission_requirements['usability']` di `Air_Resources_Assigner`); `Region.get_meteorological_reports` agganciato al nuovo modulo (firma cresciuta con `date`/`time`); nuovo package `Command/` con `Command_Types.py::RegionInfoReport`; nuovo `Region.build_info_report(side, date, time)` che lo assembla da metodi `Region` già testati. Suite completa: 2540 test OK (skipped=5), +21 rispetto a prima (2519).

**Pagine wiki aggiornate**: [[c2-hierarchy-design]] (TASK 2 da "non iniziato" a "fatto"), [[context-state]] (rimossi i riferimenti a `limes`/`get_meteorological_reports` come stub), nuova [[command]] per il package appena nato.

**Bug trovato e non corretto (fuori scope)**: `Payload.__eq__` considera "diversi" due `Payload` entrambi a zero — [[datatype]] afferma erroneamente che gli operatori di confronto di `Payload` sono "completi"; correzione della pagina rimandata a una prossima sessione dedicata.

---

## [2026-09-18] aggiornamento | Unificazione struttura di progetto + decisioni architetturali nel wiki

**Motivazione**: `Analysis/Modules/00-11_*.md` (audit del 2026-08-16) era ormai stale di un mese di refactoring attivo; le decisioni architetturali vivevano solo in `.claude/memory/project_*.md`, non nel wiki. L'utente ha chiesto di unificare teoria + struttura di progetto + decisioni in un unico posto, con la regola che ogni evoluzione futura del progetto vada anche documentata qui (vedi `CLAUDE.md` §5 "SYNC EVOLUZIONE PROGETTO", aggiunto in questa stessa operazione).

**Schema esteso**: aggiunte due nuove categorie di pagina a `CLAUDE.md` — `wiki/project/` (stato attuale di un sottosistema, verificato contro il codice reale) e `wiki/decisions/` (log ADR-style delle decisioni architetturali, distillato dalle memorie `project_*`/`feedback_*`).

**12 pagine `wiki/project/` create** (una per sottosistema, verificate contro codice+test reali, non copiate dall'audit): [[asset-air]], [[asset-ground-naval]], [[asset-base]], [[context-foundation]], [[context-state]], [[block]], [[component]], [[logic-routing]], [[logic-decision]], [[datatype]], [[utility-manager]], [[testing-conventions]] (nuova, nessun equivalente nell'audit).

**8 pagine `wiki/decisions/` create**: [[region-tactical-strategic-refactor]], [[combat-power-priority-redesign]], [[datatype-route-edge-waypoint]], [[air-priority-target-specific-loadout]], [[asset-type-vs-category]], [[c2-hierarchy-design]], [[campaign-temporal-model]] (superseded), [[module-audit-2026-08-16]] (superseded, storica).

**Drift significativo scoperto rispetto all'audit del 2026-08-16** (ogni pagina `project/` lo documenta in dettaglio): diversi bug che l'audit segnalava come bloccanti sono ora risolti (import circolare Aircraft, `Military.get_military_category()`, `Edge`/`Waypoint` non istanziabili, `asea.FAST_ATTACK`, `Test_Air_Route_Manager` 26 errori→48/48 OK), mentre altri restano aperti e sono ora tracciati esplicitamente (`Ship`/`Aircraft.loadAssetDataFromContext` senza `.items()`, `Military._is_attack_asset()`→`is_helibase()` inesistente, `Production`/`Storage`/`Transport`/`Urban` stub, `Ground_Route_Manager` non produce ancora `DataType.Route`, `Coalition.py` non ancora eliminato nonostante l'approvazione).

**Pagina esistente corretta**: `wiki/concepts/c2-planner.md` aggiornata — riferimenti obsoleti a `Manager.py` e `Military_Resources_Assigner.py` sostituiti con lo stato attuale e link a [[c2-hierarchy-design]].

**`wiki/overview.md` e `wiki/index.md` aggiornati** per puntare alle nuove sezioni come fonte di verità corrente.

**`Analysis/Modules/00-11_*.md` NON eliminati** (decisione utente): restano come istantanea storica, con banner in testa che rimanda alla pagina `wiki/project/` corrispondente.

**Metodo**: 6 subagent paralleli hanno letto il codice sorgente reale ed eseguito le suite di test pertinenti (non solo letto testo), verificando ogni claim invece di copiare l'audit vecchio. Bug di frontmatter YAML introdotti da alcuni agenti (liste di wikilink malformate) e link a pagine inesistenti (titoli invece di nomi-file kebab-case) sono stati trovati e corretti in fase di consolidamento.

---

## [2026-05-27] aggiornamento | Creazione stub ad alta priorità (13 pagine)

**Entità create (7)**:
- `wiki/entities/tac-thunder.md` — Theater Air Campaign Model USAF (griglia quadrata)
- `wiki/entities/cem-model.md` — Concepts Evaluation Model US Army (CAA), predecessore CADEM
- `wiki/entities/jicm-model.md` — Joint Integrated Contingency Model RAND (scope globale)
- `wiki/entities/rsas.md` — RAND Strategy Assessment System (predecessore TLC)
- `wiki/entities/modsim-ii.md` — Linguaggio di simulazione OOP CACI
- `wiki/entities/rjars.md` — RAND Jamming and Radar Simulation (dati superficie-aria)
- `wiki/entities/tac-sage.md` — Predecessore USAF dell'algoritmo SAGE

**Concetti creati (6)**:
- `wiki/concepts/piston-network.md` — Struttura game board lineare legacy
- `wiki/concepts/killer-victim-scoreboard.md` — Tabelle di efficacia cross-resolution
- `wiki/concepts/c2-planner.md` — Pianificatore C² del TLC (integra SAGE + manovre)
- `wiki/concepts/variable-resolution-modeling.md` — Variazione dinamica del livello di dettaglio
- `wiki/concepts/nonlinear-combat.md` — Combattimento non-lineare post-Guerra Fredda
- `wiki/concepts/historical-conflict-simulation.md` — Simulazione conflitti storici (Sabin)

**Index aggiornato**: entità 7→14, concetti 9→15; nuova sezione "Strutture Spaziali"

**Link rotti risolti**: da 26 a 11 (rimangono solo pagine a bassa priorità ≤2 refs)

---

## [2026-05-27] health-check | Prima verifica integrità wiki

**Fix applicati automaticamente (2)**:
1. Rinomina file sorgenti: aggiunto prefisso `source-` per allineare nomi file ai wikilink usati in tutto il wiki (`source-theater-level-campaign-model.md`, `source-simulation-techniques-past-conflicts.md`)
2. Pulizia anomalia `[[generalized-network]]` in `index.md`: rimosso doppione nella sezione "da creare" con nota contraddittoria

**Link rotti rilevati (26 wikilink senza pagina)**:
- Entità ad alta priorità (5+ ref): `[[tac-thunder]]`(8), `[[cem-model]]`(6), `[[jicm-model]]`(6), `[[rsas]]`(5), `[[modsim-ii]]`(5), `[[rjars]]`(5), `[[tac-sage]]`(4)
- Concetti ad alta priorità (3+ ref): `[[c2-planner]]`(5), `[[killer-victim-scoreboard]]`(5), `[[historical-conflict-simulation]]`(5), `[[piston-network]]`(5), `[[variable-resolution-modeling]]`(4), `[[nonlinear-combat]]`(3)
- Entità/concetti a bassa priorità (1-2 ref): `[[anti-hindsight]]`, `[[british-doae]]`, `[[kings-college-london]]`, `[[lost-battles]]`, `[[eadsim]]`, `[[apex-model]]`, `[[clausewitz]]`, `[[simulating-war]]`, `[[jmem]]`, `[[manual-simulation]]`, `[[idahex]]`

**Pagine orfane** (0 link in entrata): `source-theater-level-campaign-model`, `source-simulation-techniques-past-conflicts` — normale, sono le radici del grafo

**Contraddizioni**: nessuna contraddizione tra fonti — Sabin e Hillestad/Moore sono prospettive complementari (confermato)

**Stato frontmatter**: tutti i 19 file hanno frontmatter YAML completo ✓

**Raccomandazione priorità creazione stub**: `[[piston-network]]`, `[[c2-planner]]`, `[[killer-victim-scoreboard]]`, `[[tac-thunder]]` — massimo impatto sul grafo di link

---

## [2026-05-27] ingestione | Simulation Techniques in the Modelling of Past Conflicts (Sabin, KCL, 2008)

**File**: `RAW/simulationtechniquesinthemodellingofpastconflicts.doc` (951 parole, workshop HEA Warwick)

**Pagine create** (5 totali):
- `wiki/sources/simulation-techniques-past-conflicts.md`
- `wiki/entities/philip-sabin.md`
- `wiki/concepts/wargaming.md`
- `wiki/concepts/comparative-dynamic-modelling.md`

**Contributi principali**:
- 3 ruoli delle simulazioni: coinvolgimento, anti-hindsight, comprensione sistemica
- Wargaming come "contesa dialettica" (Clausewitz)
- Comparative dynamic modelling: validazione per variazione di assunzioni
- Argomento manuale vs computerizzato — accessibilità e bilanciamento

**Nessuna contraddizione** con fonte TLC — prospettive complementari (storico/accademico vs operativo/tecnico)

**Applicabilità al Warfare-Model**:
- Anti-hindsight → rinforza argomento per simulazione stocastica DWM
- Comparative dynamic modelling → metodologia per calibrazione e validazione DWM con `tactical_evaluation_results.csv`
- Clausewitz dialettica → fondamento concettuale del modulo avversario DWM

---

## [2026-05-27] ingestione | The Theater-Level Campaign Model (Hillestad & Moore, RAND, 1994)

**File**: `RAW/The Theater-Level Campaign Model.pdf` (MR-388-AF/A)

**Pagine lette**: frontmatter + pp. 1-42 (Cap. 1-3) + pp. 58-77 (Cap. 4)

**Pagine create** (12 totali):
- `wiki/sources/theater-level-campaign-model.md`
- `wiki/entities/tlc-model.md`
- `wiki/entities/rand-corporation.md`
- `wiki/entities/janus-model.md`
- `wiki/entities/tac-brawler.md`
- `wiki/entities/tacwar.md`
- `wiki/entities/mapview.md`
- `wiki/concepts/campaign-model.md`
- `wiki/concepts/generalized-network.md`
- `wiki/concepts/cadem.md`
- `wiki/concepts/sage-algorithm.md`
- `wiki/concepts/cross-resolution-modeling.md`
- `wiki/concepts/event-driven-simulation.md`
- `wiki/concepts/stochastic-simulation.md`

**Entità referenziate non ancora paginati**: tac-thunder, cem-model, jicm-model, rsas, modsim-ii, rjars, eadsim, british-doae, c2-planner, piston-network, killer-victim-scoreboard, variable-resolution-modeling, nonlinear-combat

**Applicabilità al Warfare-Model — sintesi**:
- Generalized Network → Route/Area/Region DWM (struttura analoga)
- SAGE → Air_Resources_Assigner / Military_Resources_Assigner (stesso problema)
- CADEM → calibrazione attrito da `tactical_evaluation_results.csv`
- Stochastic simulation → già presente (parzialmente) nel DWM
- C² Planner → Manager.py logica di pianificazione campagna

---

## [2026-05-27] setup | Inizializzazione del Wiki LLM

**Operazione**: Creazione della struttura iniziale del wiki.

**Azioni eseguite**:
- Creato `CLAUDE.md` con schema completo del wiki
- Creata struttura cartelle: `wiki/`, `wiki/entities/`, `wiki/concepts/`, `wiki/sources/`, `wiki/analyses/`, `wiki/assets/`
- Creato `wiki/index.md` (catalogo contenuti)
- Creato `wiki/log.md` (questo file)
- Creato `wiki/overview.md` (panoramica del dominio)
- Configurato `.obsidian/` per visualizzazione ottimale

**Fonti RAW disponibili per ingestione**:
1. `The Theater-Level Campaign Model.pdf`
2. `simulationtechniquesinthemodellingofpastconflicts.doc`

**Prossimi passi suggeriti**:
- Ingesta le due fonti RAW esistenti
- Configura Obsidian Web Clipper per aggiungere fonti da browser
