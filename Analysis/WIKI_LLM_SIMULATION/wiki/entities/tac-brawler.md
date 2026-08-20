---
title: "TAC BRAWLER — Modello Aria-Aria ad Alta Risoluzione"
type: entity
tags: [air, combat-simulation, high-resolution, air-to-air]
created: 2026-05-27
updated: 2026-05-27
sources: ["[[source-theater-level-campaign-model]]"]
related: ["[[tlc-model]]", "[[cross-resolution-modeling]]", "[[tac-thunder]]", "[[killer-victim-scoreboard]]"]
---

# TAC BRAWLER

## Descrizione

TAC BRAWLER (Decision-Science Applications, 1988) è un modello ad alta risoluzione per simulazioni di combattimento aria-aria. Simula engagements uno-contro-uno, uno-contro-molti e molti-contro-molti tra aeromobili.

## Ruolo nel TLC (Cross-Resolution)

TLC usa TAC BRAWLER come sorgente primaria per i parametri di attrito aria-aria:
- Genera **exchange tables** per specifiche composizioni di forze
- Fornisce **probabilità di kill (Pk)** per tipo di aeromobile vs tipo di aeromobile
- I risultati vengono scalati per forze di dimensioni diverse con funzioni di scaling empiriche
- Sono effettuati draw Monte Carlo (Bernoulli trials) su ogni aeromobile per determinare le perdite effettive

## Processo di Aggregazione

```
TAC BRAWLER (alta risoluzione)
    → Brawler Exchange Tables
    → Aircraft Equivalence Factors
    → Allocation Process
    → Monte Carlo draw per aircraft
    → Losses + Weapon Expenditures
```

## Nota

TAC THUNDER (Air Force) usa invece parametri "tuned" da TAC BRAWLER che non sono compatibili con gli exchange tables di TACWAR o TLC — esempio concreto del problema di cross-resolution.

## Fonti
- Menzionato in: [[source-theater-level-campaign-model]] (pp. 60, 63, 74)
