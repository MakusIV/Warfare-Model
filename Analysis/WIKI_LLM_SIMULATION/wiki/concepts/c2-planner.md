---
title: "C² Planner — Pianificatore di Comando e Controllo del TLC"
type: concept
tags: [c2, planning, campaign-model, adaptive, tlc, air, ground]
created: 2026-05-27
updated: 2026-09-18
sources: ["[[source-theater-level-campaign-model]]"]
related: ["[[sage-algorithm]]", "[[tlc-model]]", "[[campaign-model]]", "[[generalized-network]]", "[[stochastic-simulation]]", "[[c2-hierarchy-design]]"]
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

**Aggiornamento 2026-09-18 — vedi [[c2-hierarchy-design]] per il design attuale, questa sezione è storica.** Il vecchio riferimento a `Manager.py` come "il C² Planner del sistema" è superato: `Manager.py` (root di `Source/`) è uno stub rotto di 106 righe, mai stato funzionante, e ora è destinato a essere rinominato/eliminato per liberare il nome `C2_Manager`. `Military_Resources_Assigner.py` è stato rinominato in `Air_Resources_Assigner.py` da tempo (il vecchio nome non esiste più nel codice).

Il pattern C² Planner adattivo resta comunque il riferimento concettuale corretto per la gerarchia C2 a due livelli ora concordata (`C2_Manager` globale + `C2_Region_Manager` regionale, non ancora costruiti — vedi [[c2-hierarchy-design]]):
- `Air_Resources_Assigner.py` (≈ SAGE per la componente aerea) resta il candidato per l'allocazione risorse aeree.
- Manca ancora un pianificatore terrestre/navale equivalente esplicito.
- Il principio **adattivo** (leggere lo stato corrente e ottimizzare, non seguire script fissi) è esattamente ciò che il design del nuovo `C2_Manager`/`C2_Region_Manager` intende realizzare tramite il ciclo analizza→pianifica→esegui descritto in [[c2-hierarchy-design]].

**Implicazione di design**: il gap principale tra l'architettura attuale e il modello TLC non è più "il Manager.py deve diventare adattivo" (quel file è da eliminare), ma "il nuovo `Command/` package deve implementare questo pattern da zero" — nessun codice di questo package esiste ancora oggi.

## Differenza con Script Fissi

| Approccio | Caratteristiche | Limitazioni |
|-----------|----------------|-------------|
| Script fisso | Pre-pianificato, deterministico | Non reagisce a variazioni; non misura valore C⁴I |
| **C² Planner adattivo** | Ottimizza in real-time | Richiede funzione obiettivo; computazionalmente costoso |
| Ibrido | Script + override adattivi | Trade-off pratico per sistemi in sviluppo |

## Fonti

- Menzionato in: [[source-theater-level-campaign-model]] (pp. xvi, 60-65 — architettura TLC, SAGE integration)
