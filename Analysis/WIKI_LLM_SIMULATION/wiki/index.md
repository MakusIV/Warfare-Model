# Wiki Index — Modelli di Simulazione Bellica

> **Catalogo completo dei contenuti wiki.** Aggiornato da Claude ad ogni ingestione, query o modifica.
> Ultimo aggiornamento: 2026-05-27

---

## Panoramica Rapida

| Categoria | Pagine | Ultima modifica |
|-----------|--------|-----------------|
| Fonti (Sources) | 2 | 2026-05-27 |
| Entità (Entities) | 14 | 2026-05-27 |
| Concetti (Concepts) | 15 | 2026-05-27 |
| Analisi (Analyses) | 0 | — |

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

### Concetti referenziati (non ancora paginati)
*Menzionati con wikilink ma privi di pagina dedicata — bassa priorità:*
- `[[anti-hindsight]]` — tecnica per ridurre l'hindsight bias · 2 refs
- `[[jmem]]` — Joint Munitions Effectiveness Manual (dati A-G) · 1 ref
- `[[manual-simulation]]` — simulazione manuale (wargame senza computer) · 1 ref

---

## Analisi (Analyses)

*Nessuna analisi ancora. Vengono create in risposta a query complesse.*

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
- `#naval` — (nessuna ancora — espandere)
- `#ground` — [[janus-model]], [[cadem]], [[tacwar]]
- `#joint` — [[tlc-model]], [[campaign-model]]

### Per progetto
- `#warfare-model` — [[tlc-model]], [[generalized-network]], [[sage-algorithm]], [[cadem]]
- `#dwm` — (da taggare esplicitamente nelle pagine)
