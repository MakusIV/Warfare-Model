---
title: "C² Planner — Pianificatore di Comando e Controllo del TLC"
type: concept
tags: [c2, planning, campaign-model, adaptive, tlc, air, ground]
created: 2026-05-27
updated: 2026-05-27
sources: ["[[source-theater-level-campaign-model]]"]
related: ["[[sage-algorithm]]", "[[tlc-model]]", "[[campaign-model]]", "[[generalized-network]]", "[[stochastic-simulation]]"]
---

# C² Planner — Pianificatore C²

## Definizione

Il **C² Planner** (Command and Control Planner) è il modulo del [[tlc-model]] responsabile della pianificazione operativa adattiva. Integra la pianificazione delle manovre terrestri (spostamento delle forze, uso delle riserve) con l'allocazione delle risorse aeree tramite l'algoritmo [[sage-algorithm]].

> "The Sequential Analytic Game Evaluation (SAGE) algorithm of the C² Planner within TLC was designed to support the development of adaptive strategies for policy analysis." (p. xvi)

## Componenti del C² Planner

```
C² Planner
├── Pianificatore Terrestre
│   ├── Controllo manovre (avanzata, difesa, ritiro)
│   ├── Gestione riserve
│   └── Scelta rotte (su generalized-network)
│
└── Allocatore Risorse Aeree (SAGE)
    ├── Aeromobili → tipi di missione
    ├── Fuochi a lunga gittata → target
    └── Elicotteri → supporto fuoco / trasporto
```

## Perché un C² Planner Adattivo

I modelli legacy ([[tacwar]], [[cem-model]]) usano **script fissi** per le decisioni operative: regole hard-coded che non cambiano al variare della situazione tattica. Questo impedisce di valutare il valore di sistemi C⁴I: se le decisioni non sono sensibili alle informazioni, il valore dell'informazione è zero per definizione.

Un C² Planner adattivo come quello del TLC:
1. Legge lo stato corrente della campagna (posizioni, forze, perdite)
2. Ottimizza l'allocazione delle risorse in risposta
3. Permette quindi di misurare quanto vale avere informazioni migliori (C⁴I)

## Interazione SAGE ↔ C² Planner

```
C² Planner
    │
    ├─ 1. Analizza stato campagna
    │      (posizioni forze, disponibilità aerei, target attivi)
    │
    ├─ 2. Chiama SAGE per allocazione risorse aeree
    │      → SAGE restituisce piano ottimale
    │
    ├─ 3. Integra piano aereo con piano manovre terrestri
    │
    └─ 4. Emette ordini → simulazione esegue un time step
```

## Applicabilità al Warfare-Model

`Manager.py` nel DWM è funzionalmente il C² Planner del sistema:
- Coordina `Air_Resources_Assigner.py` (≈ SAGE per la componente aerea)
- Coordina `Military_Resources_Assigner.py` (≈ pianificatore terrestre/navale)
- Dovrebbe essere **adattivo**: reagire allo stato della campagna, non seguire script fissi

**Implicazione di design**: il Manager.py deve leggere lo stato corrente e prendere decisioni ottimizzate — non eseguire una sequenza prefissata. Questo è il gap principale tra l'architettura attuale e il modello TLC.

## Differenza con Script Fissi

| Approccio | Caratteristiche | Limitazioni |
|-----------|----------------|-------------|
| Script fisso | Pre-pianificato, deterministico | Non reagisce a variazioni; non misura valore C⁴I |
| **C² Planner adattivo** | Ottimizza in real-time | Richiede funzione obiettivo; computazionalmente costoso |
| Ibrido | Script + override adattivi | Trade-off pratico per sistemi in sviluppo |

## Fonti

- Menzionato in: [[source-theater-level-campaign-model]] (pp. xvi, 60-65 — architettura TLC, SAGE integration)
