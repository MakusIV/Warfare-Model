---
title: "RJARS — RAND Jamming and Radar Simulation"
type: entity
tags: [combat-simulation, air, surface-to-air, radar, ecm, rand, cross-resolution]
created: 2026-05-27
updated: 2026-05-27
sources: ["[[source-theater-level-campaign-model]]"]
related: ["[[tlc-model]]", "[[rand-corporation]]", "[[cross-resolution-modeling]]", "[[tac-brawler]]", "[[cadem]]", "[[killer-victim-scoreboard]]"]
---

# RJARS — RAND Jamming and Radar Simulation

## Descrizione

RJARS è un modello RAND ad **alta risoluzione** per la simulazione delle interazioni **superficie-aria** (surface-to-air): missili terra-aria (SAM), jamming elettronico, e capacità radar. Fornisce al [[tlc-model]] i dati di efficacia (engagement rates, probabilità di kill) per il combattimento superficie-aria, tramite il meccanismo di [[cross-resolution-modeling]].

## Ruolo nel TLC

RJARS occupa il livello "alta risoluzione" nella catena cross-resolution per la componente surface-to-air:

```
RJARS (alta risoluzione)
    ↓ Genera killer-victim scoreboards
    ↓ Engagement rates per tipo SAM
    ↓ Pk (probability of kill) per scenario
TLC (campagna)
    ↓ Usa questi dati come lookup table
    ↓ per calcolare perdite aeree da SAM
```

## Dati Prodotti per TLC

- **Engagement rates**: quante volte un SAM ingaggia un aereo per missione, per tipo di SAM e scenario
- **Probability of kill (Pk)**: per ogni combinazione di aereo × SAM × ECM × scenario
- **Effetti jamming**: riduzione Pk in presenza di EW (Electronic Warfare)

## Caratteristiche Principali

- **Organizzazione**: RAND Corporation
- **Focus**: radar, SAM, jamming elettronico (ECM/ECCM)
- **Tipo**: modello ad alta risoluzione, non un campaign model
- **Output**: tabelle di efficacia per popolare il TLC

## Relazioni nella Famiglia Cross-Resolution

| Dominio | Modello Alta Risoluzione | Output per TLC |
|---------|--------------------------|----------------|
| Terrestre | [[janus-model]] → [[cadem]] | Killer-victim scoreboards |
| Aria-Aria | [[tac-brawler]] | Exchange ratio, Pk |
| Superficie-Aria | **RJARS** | Eng.Rate + Pk SAM |
| Aria-Terra | JMEM | Pk per tipo target/munizione |

## Applicabilità al Warfare-Model

Il DWM opera su DCS dove la simulazione SAM/radar è già gestita dal motore DCS. RJARS non è quindi direttamente applicabile. Il concetto rilevante è che i dati di efficacia per sistemi SAM in DCS possono essere estratti da log di missione (analogia con killer-victim scoreboards) per calibrare il DWM.

## Relazioni

- Sviluppato da: [[rand-corporation]]
- Fornisce dati a: [[tlc-model]] (via [[cross-resolution-modeling]])
- Stesso livello: [[janus-model]] (terrestre), [[tac-brawler]] (aria-aria)
- Output: [[killer-victim-scoreboard]]

## Fonti

- Menzionato in: [[source-theater-level-campaign-model]] (pp. 37-40 — cross-resolution modeling, surface-to-air)

## Note

Pagina stub. Documentazione tecnica RJARS non disponibile nelle fonti attuali. Classificata o distribuita solo internamente a RAND/DoD.
