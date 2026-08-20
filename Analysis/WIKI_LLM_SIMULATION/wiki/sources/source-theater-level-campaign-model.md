---
title: "The Theater-Level Campaign Model"
type: source
tags: [campaign-model, tlc, rand, air, ground, joint, cross-resolution, sage, cadem]
created: 2026-05-27
updated: 2026-05-27
file: RAW/The Theater-Level Campaign Model.pdf
authors: [Richard J. Hillestad, Louis Moore]
year: 1994
institution: RAND Corporation
report_number: MR-388-AF/A
sponsors: [US Air Force, US Army]
related: ["[[tlc-model]]", "[[cadem]]", "[[sage-algorithm]]", "[[generalized-network]]", "[[cross-resolution-modeling]]"]
---

# The Theater-Level Campaign Model

## Riepilogo Esecutivo

Rapporto RAND (MR-388-AF/A) che descrive il modello TLC (Theater-Level Campaign), prototipo di ricerca per una nuova generazione di modelli di analisi del combattimento a livello teatrale. Il documento presenta soluzioni a quattro sfide fondamentali della modellazione di campagna militare nel contesto post-Guerra Fredda: flessibilità strutturale, cross-resolution modeling, rappresentazione delle manovre e allocazione adattiva delle risorse. Non è un manuale d'uso ma una documentazione delle lezioni apprese nel processo di design.

## Contributi Principali

1. **Rete Generalizzata (Generalized Network)**: game board flessibile che supera le strutture rigide piston/griglia, supporta variable-resolution e operazioni non-lineari
2. **Strutture Software Flessibili**: simulazione event-stepped con MODSIM II, approccio stocastico (Monte Carlo) per processi intrinsecamente casuali
3. **Cross-Resolution Modeling**: collegamento formale con modelli ad alta risoluzione (JANUS, TAC BRAWLER, JMEM, RJARS) tramite CADEM per attrito terrestre
4. **C² Planner**: pianificatore operativo per manovre terrestri su reti generalizzate, valuta probabilità di successo e alloca riserve
5. **Algoritmo SAGE**: (Sequential Analytic Game Evaluation) allocazione adattiva delle risorse aeree basata su ottimizzazione iterativa degli obiettivi

## Entità Menzionate

- [[tlc-model]] — il modello principale descritto
- [[rand-corporation]] — istituzione che ha sviluppato TLC
- [[janus-model]] — modello terrestre ad alta risoluzione usato come fonte per CADEM
- [[tac-brawler]] — modello aria-aria ad alta risoluzione (RAND)
- [[tac-thunder]] — modello teatro aereo USAF (CACI), basato su griglia
- [[tacwar]] — modello teatro Joint Staff, basato su piston
- [[cem-model]] — Concepts Evaluation Model (CAA), aria-terra aggregato
- [[jicm-model]] — Joint Integrated Combat Model (RAND), conflitto globale
- [[rsas]] — RAND Strategy Assessment System
- [[mapview]] — GUI per preprocessing della rete generalizzata
- [[modsim-ii]] — linguaggio di simulazione usato per TLC (CACI)
- [[eadsim]] — Enemy Air Defense Simulation (dati SAM)
- [[rjars]] — RAND Jamming and Radar Simulation (dati superficie-aria)
- [[jmem]] — Joint Munitions Effectiveness Manual (dati aria-terra)
- [[tac-sage]] — predecessore RAND per ottimizzazione allocazione aerea
- [[idahex]] — modello wargaming esagonale (Institute of Defense Analysis)

## Concetti Chiave Trattati

- [[campaign-model]] — definizione, tassonomia, livelli (engineering → engagement → mission → campaign)
- [[generalized-network]] — struttura game board flessibile, nodi/archi/regioni/griglie
- [[piston-network]] — struttura legacy NATO-Patto di Varsavia (TACWAR, CEM)
- [[cross-resolution-modeling]] — collegamento tra modelli a diversa risoluzione
- [[cadem]] — Calibrated Differential Equation Methodology (attrito terrestre)
- [[event-driven-simulation]] — gestione del tempo: event-step vs time-step
- [[stochastic-simulation]] — simulazione stocastica vs deterministica in warfare models
- [[sage-algorithm]] — Sequential Analytic Game Evaluation (allocazione adattiva)
- [[variable-resolution-modeling]] — capacità di cambiare il livello di dettaglio
- [[nonlinear-combat]] — combattimento non-lineare post-Guerra Fredda
- [[killer-victim-scoreboard]] — tabelle di efficacia combattimento da modelli ad alta risoluzione
- [[c2-planner]] — pianificatore C² per manovre terrestri

## Citazioni Rilevanti

> "The campaign model shows the big picture in terms of the total forces involved, including the joint actions of army, air, and naval forces, as well as the play of coalition forces." (p. 3-4)

> "We designed and coded the Theater-Level Campaign (TLC) model for RAND's Project AIR FORCE and the Arroyo Center to improve analysis of theater-level joint-force issues in the post–Cold War era." (Preface)

> "It is our belief that simulating adaptive resource allocation is a key element to understanding the importance of information and command and control systems." (Summary, p. xvii)

> "We recommend that any campaign model be developed with a limited goal for use and range of applications and that multiple models be developed to broaden the range." (Summary, p. xviii)

> "An important thread in this report is that many of the model innovations we suggest add a greater burden or reliance on the analyst." (Summary, p. xviii)

## Tassonomia dei Modelli di Difesa (dal documento)

```
Engineering model → Engagement model → Mission model → Campaign model → Global model (JICM)
```

Ulteriori dimensioni di classificazione:
- **Temporale**: time-step vs event-step
- **Stocastica**: deterministic vs stochastic (Monte Carlo)
- **Struttura software**: object-oriented vs process-oriented vs structured
- **Distribuzione**: single-processor vs distributed
- **Risoluzione**: fixed vs variable vs selectable

## Lacune e Contraddizioni

- Il documento riconosce esplicitamente che la cross-resolution modeling non è risolta in modo definitivo: le aggregazioni attuali sono approssimate e prive di basi matematiche rigorose
- Il CADEM richiede dati da modelli ad alta risoluzione che sono costosi e time-consuming da generare
- La variable-resolution implica un numero di combinazioni di interazione esponenzialmente crescente (20 miliardi per 10 oggetti x 2 risoluzioni)
- L'algoritmo SAGE è descritto come una soluzione parziale: i limiti degli algoritmi automatici nel rappresentare il comportamento umano sono esplicitamente riconosciuti

## Applicabilità al Warfare-Model

**Alta rilevanza** — questo documento è fondamentale per il progetto. Connessioni dirette:

1. **Rete Generalizzata → Route/Waypoint in DWM**: il concetto di nodi, archi e regioni è analogo alla struttura Route/RoutePoint/Area già presente nel Warfare-Model. La gestione di reti separate per entità diverse (aereo, navale, terrestre) mappa direttamente sull'architettura esistente.

2. **Allocazione Adattiva (SAGE) → Air_Resources_Assigner/Military_Resources_Assigner**: il problema risolto da SAGE (allocare missioni aeree in modo ottimale rispetto agli obiettivi di campagna) è esattamente il problema che i moduli Assigner del DWM cercano di risolvere. SAGE usa ottimizzazione iterativa su misure di merito — approccio da considerare.

3. **Stochastic vs Deterministic**: il documento argomenta convincentemente a favore della simulazione stocastica anche a livello di campagna. Il DWM attuale ha componenti deterministici che potrebbero beneficiare di un approccio Monte Carlo per la valutazione degli esiti tattici (già presente nei `tactical_evaluation_results`).

4. **C² Planner → Manager.py**: il concetto di pianificatore che valuta piani operativi e alloca riserve dinamicamente è il cuore del Dynamic War Manager. La struttura "valuta probabilità di successo → alloca riserve → pianifica interdizione" è un riferimento diretto.

5. **CADEM per attrito terrestre**: se il DWM deve simulare perdite terrestri in modo realistico, CADEM o un suo equivalente semplificato (differential equations + killer-victim data) sarebbe il riferimento metodologico corretto.
