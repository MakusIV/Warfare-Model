# Log delle Operazioni Wiki

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
