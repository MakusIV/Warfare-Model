---
title: "Killer-Victim Scoreboard — Tabelle di Efficacia dal Combattimento ad Alta Risoluzione"
type: concept
tags: [cross-resolution, attrition, data, calibration, combat-simulation]
created: 2026-05-27
updated: 2026-05-27
sources: ["[[source-theater-level-campaign-model]]"]
related: ["[[cadem]]", "[[cross-resolution-modeling]]", "[[janus-model]]", "[[tac-brawler]]", "[[rjars]]", "[[tlc-model]]", "[[stochastic-simulation]]", "[[comparative-dynamic-modelling]]"]
---

# Killer-Victim Scoreboard

## Definizione

Un **killer-victim scoreboard** (KVS) è una tabella di efficacia del combattimento generata da modelli ad alta risoluzione. Registra, per ogni scenario simulato, quante unità di ogni tipo ("vittime") sono state distrutte da ogni tipo di unità sparante ("killer"). È il meccanismo di trasferimento dati dal livello tattico al livello di campagna nel framework di [[cross-resolution-modeling]].

## Struttura di un KVS

```
Scenario S1, Run #42:
┌─────────────┬──────────┬──────────┬────────┬──────────┐
│ Killer\Vittime│  Tank    │  APC     │  Art.  │  Helo    │
├─────────────┼──────────┼──────────┼────────┼──────────┤
│ Tank        │   12     │    8     │   3    │    0     │
│ APC         │    2     │    5     │   1    │    0     │
│ Artillery   │    4     │    6     │   2    │    2     │
│ ATGM        │    7     │    3     │   0    │    1     │
└─────────────┴──────────┴──────────┴────────┴──────────┘
```

Ogni cella `[i,j]` = numero di unità tipo `j` distrutte da tipo `i` nella simulazione.

## Come Viene Usato in CADEM

Il processo di calibrazione [[cadem]] usa i KVS come input principale:

```
1. Modello alta risoluzione (JANUS) → genera N KVS per scenario S
2. CADEM Calibration              → stima matrice di attrito A(S)
                                    tale che dX_i = -Σ_j A_ij · X_j · dt
3. CADEM Extension                → adatta A(S) a sistemi non nell'input
4. CADEM Selection                → seleziona A per la situazione corrente
5. TLC Attrition Step             → usa A per calcolare perdite nel time step
```

## Uso Stocastico

CADEM può usare i KVS in modo stocastico: invece di usare la **media** degli N run come tabella di attrito, sceglie **casualmente** un run specifico (campionamento Monte Carlo). Questo propaga l'incertezza intrinseca del combattimento nell'attrito di campagna.

Questo è esattamente il motivo per cui il mean equivalence fallacy (vedi [[stochastic-simulation]]) si applica anche all'attrito: la varianza nei KVS è informazione, non rumore.

## Fonti di KVS nel Framework TLC

| Dominio | Modello | Tipo di KVS |
|---------|---------|-------------|
| Terra-Terra | [[janus-model]] | Perdite per tipo di arma |
| Aria-Aria | [[tac-brawler]] | Exchange ratio, Pk per scenario |
| Superficie-Aria | [[rjars]] | Engagement rate, Pk SAM |
| Aria-Terra | JMEM | Pk per tipo munizione × target |

## Analogia con il Warfare-Model

I **log di missione DCS** con `tactical_evaluation_results.csv` sono i killer-victim scoreboards del DWM:
- Ogni missione completata genera dati su perdite per tipo (aereo, SAM, veicolo)
- Questi dati possono essere aggregati in matrici di efficacia per tipo di missione × scenario
- La calibrazione del DWM (metodo [[comparative-dynamic-modelling]]) usa esattamente questa logica

**Azione concreta**: strutturare `tactical_evaluation_results.csv` come un KVS per permettere calibrazione sistematica del DWM.

## Costo e Limitazioni

- Generare KVS è costoso: richiede decine/centinaia di run del modello ad alta risoluzione per ogni scenario
- I KVS sono dipendenti dallo scenario: non generalizzano facilmente a situazioni non testate
- L'estensione a nuovi sistemi d'arma richiede giudizio esperto (vedi [[cadem]])

## Fonti

- Menzionato in: [[source-theater-level-campaign-model]] (pp. 32-42 — CADEM methodology)
