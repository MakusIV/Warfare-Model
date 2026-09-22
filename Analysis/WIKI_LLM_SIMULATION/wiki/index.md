# Wiki Index — Modelli di Simulazione Bellica

> **Catalogo completo dei contenuti wiki.** Aggiornato da Claude ad ogni ingestione, query o modifica.
> Ultimo aggiornamento: 2026-09-22

---

## Panoramica Rapida

| Categoria | Pagine | Ultima modifica |
|-----------|--------|-----------------|
| Fonti (Sources) | 4 | 2026-09-22 |
| Entità (Entities) | 15 | 2026-09-22 |
| Concetti (Concepts) | 17 | 2026-09-22 |
| Analisi (Analyses) | 3 | 2026-09-22 |
| Struttura di progetto (Project) | 13 | 2026-09-22 |
| Decisioni architetturali (Decisions) | 14 | 2026-09-22 |

---

## Pagine Speciali

| Pagina | Descrizione |
|--------|-------------|
| [[overview]] | Panoramica del dominio e stato attuale della conoscenza |
| [[index]] | Questo file — catalogo dei contenuti |
| [[log]] | Registro cronologico delle operazioni |

---

## Fonti (Sources)

| Pagina | Titolo | Autori | Anno | Tag Principali |
|--------|--------|--------|------|----------------|
| [[source-theater-level-campaign-model]] | The Theater-Level Campaign Model | Hillestad, Moore (RAND) | 1994 | campaign-model, TLC, SAGE, CADEM, joint |
| [[source-simulation-techniques-past-conflicts]] | Simulation Techniques in the Modelling of Past Conflicts | Sabin (King's College London) | 2008 | wargame, historical, manual-simulation, anti-hindsight |
| [[source-lanchester-scenari-ai]] | Modelli Lanchester e scenari applicati — sessione conversazionale con assistente AI (9 `.docx`) | assistente AI non identificato | 2026 | lanchester, attrition, scenario, **low-confidence** |
| [[source-hughes-salvo-event-driven]] | Modello event-driven a salva di Hughes — sessione conversazionale con assistente AI (6 `.docx` + `edit.pdf`) | assistente AI non identificato | 2026 | hughes, salvo-combat-model, discrete-event, **medium-confidence** |

---

## Entità (Entities)

### Modelli e Sistemi di Simulazione

| Pagina | Descrizione |
|--------|-------------|
| [[tlc-model]] | Theater-Level Campaign Model — prototipo RAND per prossima generazione campaign models |
| [[janus-model]] | Modello terrestre ad alta risoluzione (Army) — fonte dati per CADEM |
| [[tac-brawler]] | Modello aria-aria ad alta risoluzione — fonte dati per attrito aereo TLC |
| [[rjars]] | RAND Jamming and Radar Simulation — dati superficie-aria per TLC |
| [[tacwar]] | Modello campagna teatrale Joint Staff — struttura piston legacy |
| [[cem-model]] | Concepts Evaluation Model (US Army CAA) — struttura piston, predecessore CADEM |
| [[tac-thunder]] | Theater Air Campaign Model USAF (CACI) — griglia quadrata, legacy |
| [[jicm-model]] | Joint Integrated Contingency Model RAND — scope globale/strategico |
| [[rsas]] | RAND Strategy Assessment System — predecessore diretto del TLC |
| [[tac-sage]] | Predecessore USAF dell'algoritmo SAGE — ottimizzazione allocazione aerea |

### Organizzazioni e Istituzioni

| Pagina | Descrizione |
|--------|-------------|
| [[rand-corporation]] | RAND Corporation — sviluppatore TLC e famiglia di modelli correlati |

### Autori e Ricercatori

| Pagina | Descrizione |
|--------|-------------|
| [[philip-sabin]] | Prof. Philip Sabin, King's College London — wargaming accademico e historical simulation |
| [[wayne-hughes]] | Capt. Wayne P. Hughes, *Fleet Tactics* — autore del modello a salva (salvo combat model) |

### Tool e Software

| Pagina | Descrizione |
|--------|-------------|
| [[mapview]] | GUI RAND per preprocessing reti generalizzate |
| [[modsim-ii]] | Linguaggio di simulazione OOP CACI — usato per TLC e TAC THUNDER |

### Entità referenziate (non ancora paginate)
*Menzionate con wikilink ma privi di pagina dedicata — bassa priorità:*
- `[[eadsim]]` — Enemy Air Defense Simulation · 2 refs
- `[[british-doae]]` — British Defence Operations Analysis Establishment · 2 refs
- `[[kings-college-london]]` — King's College London, dipartimento War Studies · 2 refs
- `[[lost-battles]]` — libro Sabin (2007) sulle battaglie dell'antichità · 2 refs
- `[[apex-model]]` — modello RAND alternativo (menzionato TLC) · 2 refs
- `[[clausewitz]]` — Carl von Clausewitz, teoria della guerra · 1 ref
- `[[simulating-war]]` — libro Sabin (2012) su design di simulazioni · 1 ref
- `[[idahex]]` — modello griglia esagonale Idaho (menzionato TLC) · 1 ref

*Nomi emersi da [[source-lanchester-scenari-ai]] — **piste bibliografiche da verificare**, la fonte
non fornisce citazioni utilizzabili; non creare pagine prima di aver trovato una fonte primaria:*
- `Jerome Bracken` — forma generalizzata $R^qG^p$, calibrazione Ardenne/Kursk
- `Dupuy Institute` / `KDB` — Kursk Database, test delle equazioni sulle sole *contact forces*
- `Helmbold` — Lanchester con rapporto di forze, postura e soglie di ritirata
- `Peterson` — modello logaritmico per l'attrito non da combattimento
- `STORM`, `JAAM` — attribuzione della fonte a Lanchester matriciale **non verificata e sospetta**

---

## Concetti (Concepts)

### Paradigmi di Simulazione

| Pagina | Descrizione |
|--------|-------------|
| [[event-driven-simulation]] | Event-step vs time-step — gestione del tempo nelle simulazioni di campagna |
| [[stochastic-simulation]] | Simulazione stocastica (Monte Carlo) vs deterministica — argomenti a favore |

### Strutture Spaziali e Rappresentazione del Terreno

| Pagina | Descrizione |
|--------|-------------|
| [[generalized-network]] | Struttura game board flessibile del TLC — nodi, archi, regioni, griglie |
| [[piston-network]] | Struttura lineare legacy (TACWAR, CEM) — bande parallele, fronte rigido |
| [[variable-resolution-modeling]] | Variazione dinamica del livello di dettaglio in un singolo modello |
| [[nonlinear-combat]] | Combattimento non-lineare post-Guerra Fredda — manovre, envelopment, deep attack |

### Metodologie di Modellazione dei Conflitti

| Pagina | Descrizione |
|--------|-------------|
| [[campaign-model]] | Definizione, tassonomia e caratteristiche dei modelli di campagna militare |
| [[cross-resolution-modeling]] | Collegamento tra modelli a diversa risoluzione — problemi e approcci |
| [[cadem]] | Calibrated Differential Equation Methodology — attrito terrestre eterogeneo |
| [[killer-victim-scoreboard]] | Tabelle di efficacia dal combattimento ad alta risoluzione — input per CADEM |
| [[sage-algorithm]] | Sequential Analytic Game Evaluation — allocazione adattiva risorse aeree |
| [[c2-planner]] | Pianificatore di Comando e Controllo del TLC — integra SAGE e manovre terrestri |
| [[wargaming]] | Gioco di guerra come strumento di analisi, formazione e ricerca storica |
| [[comparative-dynamic-modelling]] | Metodo Sabin per risolvere controversie storiche tramite simulazione |
| [[historical-conflict-simulation]] | Simulazione di conflitti storici — obiettivi, approcci, metodologia anti-hindsight |
| [[lanchester-models]] | Famiglia Lanchester — leggi classiche, Bracken, eterogeneo, soglie Helmbold, SINDy; stato di validazione (negativo) |
| [[salvo-combat-model]] | Modello a salva di Hughes — impulsi discreti, saturazione difensiva; risolutore scelto per la Fase 4 |

### Concetti referenziati (non ancora paginati)
*Menzionati con wikilink ma privi di pagina dedicata — bassa priorità:*
- `[[anti-hindsight]]` — tecnica per ridurre l'hindsight bias · 2 refs
- `[[jmem]]` — Joint Munitions Effectiveness Manual (dati A-G) · 1 ref
- `[[manual-simulation]]` — simulazione manuale (wargame senza computer) · 1 ref

---

## Analisi (Analyses)

| Pagina | Domanda | Esito |
|--------|---------|-------|
| [[lanchester-vs-motore-des]] | I 9 documenti Lanchester superano lo scetticismo già documentato, e cosa cambia nel motore di sessioni virtuali? | Negativo sulla matematica; utile su scenari di test, soglie di disingaggio, forma del fallback aggregato. **Zero impatto sullo strato 1** |
| [[llm-locale-nel-motore-des]] | Un LLM locale (7-27B quantizzato su RTX 3090) può valutare le condizioni dei passi event-driven? | 4 letture valutate: **per evento 9,2 giorni/sessione** (vs 0,86 s in forma chiusa) e **per decisione dottrinale** respinte (budget + riproducibilità: Qwen2.5-7B ha il **17,6%** di risposte identiche a temp. 0); **debrief narrativo** e **uso offline** passano. Reperto collaterale: `closest_point_of_approach` costa **2.450×** il necessario |
| [[hughes-salvo-vs-engagement-resolver]] | La fonte su Hughes supera lo scetticismo dovuto e cosa cambia in `Logic/Engagement_Resolver.py` (Fase 4)? | D1 solida, colma la lacuna; D2-D7 utili come catalogo di meccanismi, non come formule. **4 meccanismi adottabili** (saturazione difensiva, shock da salva, congelamento payload, anti-overkill), **1 precondizione nuova** (munizioni per asset), **1 punto architetturale** (re-scheduling dopo spostamento, tocca lo strato 1) |

---

## Struttura di Progetto (`wiki/project/`)

*Stato attuale del codice Warfare-Model, sottosistema per sottosistema — verificato contro il codice reale, non contro l'audit storico. Sostituisce `Analysis/Modules/00-11_*.md` (2026-08-16, ora solo istantanea storica) come fonte di verità corrente.*

| Pagina | Sottosistema | Sostituisce |
|--------|--------------|-------------|
| [[asset-air]] | Asset — Aviazione | `Analysis/Modules/01_Asset_Air.md` |
| [[asset-ground-naval]] | Asset — Terrestri e Navali | `Analysis/Modules/02_Asset_Ground_Naval.md` |
| [[asset-base]] | Asset — Classi Base | `Analysis/Modules/03_Asset_Base.md` |
| [[context-foundation]] | Context — Fondamenta e Dati Iniziali | `Analysis/Modules/04_Context_Foundation.md` |
| [[context-state]] | Context — Stato Operativo e Persistenza | `Analysis/Modules/05_Context_State.md` |
| [[block]] | Block — Unità Economico-Militari | `Analysis/Modules/06_Block.md` |
| [[logic-routing]] | Logic — Pianificazione Rotte | `Analysis/Modules/07_Logic_Routing.md` |
| [[logic-decision]] | Logic — Decisione Tattica e Strategica | `Analysis/Modules/08_Logic_Decision.md` |
| [[component]] | Component — Gestione Risorse | `Analysis/Modules/09_Component.md` |
| [[datatype]] | DataType — Tipi Dato di Base | `Analysis/Modules/10_DataType.md` |
| [[utility-manager]] | Utility e Manager (nucleo/entry point) | `Analysis/Modules/11_Utility_Manager.md` |
| [[testing-conventions]] | Convenzioni di testing | *(nuova, nessun equivalente nell'audit)* |
| [[command]] | Command (gerarchia C2, `RegionInfoReport`) | *(nuova, package nato 2026-09-18)* |

---

## Decisioni Architetturali (`wiki/decisions/`)

*Log in stile ADR delle decisioni architetturali adottate nel progetto — contesto, decisione, motivazione, conseguenze. Distillato dalle memorie di progetto (`.claude/memory/project_*.md`), non le sostituisce (la memoria resta la fonte per il processo/quando/perché operativo).*

| Pagina | Stato | Riguarda |
|--------|-------|----------|
| [[region-tactical-strategic-refactor]] | accepted | Estrazione tattica/strategica da `Region.py` in `Tactical_Analysis.py`/`Tactical_Evaluation.py`/`Doctrine.py` |
| [[combat-power-priority-redesign]] | accepted | Combat power reale per Vehicle/Ship/Aircraft + fog-of-war/recon |
| [[datatype-route-edge-waypoint]] | superseded → [[route-model-unification]] | `Route`/`Edge`/`Waypoint`: `DataType` canonico per il lato terrestre (framing originale) |
| [[air-priority-target-specific-loadout]] | accepted | Priorità aerea target-specific via miglior loadout disponibile |
| [[asset-type-vs-category]] | accepted | `asset_type` vs `category` in Vehicle/Ship/Aircraft |
| [[c2-hierarchy-design]] | accepted | Gerarchia C2 a due livelli, indirizzo strategico, modello sessioni, `Theater_Session_Manager` |
| [[campaign-temporal-model]] | superseded → [[c2-hierarchy-design]] | Modello temporale sessioni DCS vs. sintetiche (framing originale) |
| [[module-audit-2026-08-16]] | superseded → `wiki/project/*` | Audit dei moduli, origine di `Analysis/Modules/00-11_*.md` |
| [[virtual-session-engine-des]] | accepted | Motore DES a coda eventi per le sessioni virtuali; roadmap 7 fasi, Fase 1-2 fatte, 3 questioni pre-Fase 3 chiuse |
| [[core-simulator-agnostic]] | accepted | Vincolo: core Python indifferente al simulatore, DCS solo adapter |
| [[route-model-unification]] | accepted | `DataType.Route` confermato unico modello anche per l'aria; piano a 5 fasi, Fase 1 fatta |
| [[soglie-disingaggio-e-attrito-aggregato]] | **proposed** | Soglie di disingaggio come esito di prima classe; forma-bersaglio del fallback aggregato; scenari S1-S11 di validazione (S6-S11 nuovi: navale, logistico, scala, fog-of-war, disingaggio, confine DCS/sintetico) — **richiede decisione dell'utente** |
| [[llm-locale-ruolo-e-confini]] | **proposed** | Regola generale «niente componenti non riproducibili sulla traiettoria di stato»; LLM per evento e per decisione dottrinale a runtime respinti; debrief narrativo a valle e authoring offline ammessi con confini espliciti — **richiede decisione dell'utente** |
| [[risolutore-ingaggio-salva-fase4]] | **proposed** | Termini del modello a salva di Hughes da adottare in `Logic/Engagement_Resolver.py`: saturazione difensiva per-salva, soglia di shock (estende P1), scorte munizioni per asset (precondizione nuova), congelamento payload all'istante di fuoco — **richiede decisione dell'utente** |

---

## Tag Index

### Per dominio
- `#campaign-model` — [[tlc-model]], [[tacwar]], [[cem-model]], [[jicm-model]]
- `#combat-simulation` — [[janus-model]], [[tac-brawler]], [[tac-thunder]]
- `#cross-resolution` — [[cross-resolution-modeling]], [[cadem]]
- `#agent-based` — (nessuna ancora)
- `#discrete-event` — [[event-driven-simulation]], [[tlc-model]]
- `#monte-carlo` — [[stochastic-simulation]], [[cadem]], [[tlc-model]]

### Per componente militare
- `#air` — [[tac-brawler]], [[tac-thunder]], [[sage-algorithm]]
- `#naval` — [[salvo-combat-model]], [[wayne-hughes]]
- `#ground` — [[janus-model]], [[cadem]], [[tacwar]]
- `#joint` — [[tlc-model]], [[campaign-model]]

### Per progetto
- `#warfare-model` — [[tlc-model]], [[generalized-network]], [[sage-algorithm]], [[cadem]]
- `#dwm` — (da taggare esplicitamente nelle pagine)
