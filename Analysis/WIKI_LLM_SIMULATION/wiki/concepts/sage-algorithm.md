---
title: "SAGE — Sequential Analytic Game Evaluation"
type: concept
tags: [adaptive-planning, resource-allocation, optimization, air, warfare-model]
created: 2026-05-27
updated: 2026-05-27
sources: ["[[source-theater-level-campaign-model]]"]
related: ["[[tlc-model]]", "[[campaign-model]]", "[[c2-planner]]", "[[stochastic-simulation]]"]
---

# SAGE — Sequential Analytic Game Evaluation

## Definizione

SAGE è l'algoritmo di **allocazione adattiva delle risorse aeree** del TLC. Permette di determinare automaticamente la strategia ottimale di allocazione di aeromobili, fuochi a lunga gittata ed elicotteri ai tipi di missione, basandosi su obiettivi specificati dall'utente.

> "The Sequential Analytic Game Evaluation (SAGE) algorithm of the C² Planner within TLC was designed to support the development of adaptive strategies for policy analysis." (p. xvi)

## Il Problema che SAGE Risolve

I modelli legacy usano **script di decisione fissi** che non reagiscono alle variazioni tattiche o di equipaggiamento. SAGE sostituisce gli script con un processo iterativo di ottimizzazione che:
- Reagisce dinamicamente allo stato corrente della campagna
- Trova la strategia che massimizza il payoff marginale per le risorse disponibili
- Bilancia obiettivi di attaccante e difensore contemporaneamente

## Come Funziona SAGE

### Input dell'Utente
L'utente specifica una **misura di merito** (measure of merit), ad esempio:
- Target o risorse avversarie distrutte (massimizzare)
- Attrizione propria (minimizzare)
- Force ratio finale (massimizzare)
- Posizione finale delle forze

### Processo Iterativo

```
Iter 0: Allocazione base → run simulazione interna → calcola valore obiettivo
                                                             ↓
Iter 1: Modifica allocazione (target availability + marginal values)
         → run simulazione interna → calcola nuovo valore obiettivo
                                                             ↓
Iter N: Convergenza → strategia ottimale trovata
```

### Simulazione Interna

SAGE contiene una **simulazione di combattimento interna** che:
1. Simula missioni aeree in una giornata tipica di campagna
2. Calcola l'efficacia di ogni tipo di missione rispetto agli obiettivi
3. Usa questa efficacia per aggiustare l'allocazione nella prossima iterazione

### Convergenza

SAGE indica la strategia che massimizza il payoff marginale. Per ogni tipo di missione (attacco forze terrestri, attacco basi aeree, CAP, interdizione, ecc.), SAGE trova la quantità ottimale di risorse da allocare data la situazione corrente.

## Misure di Merito Tipiche

- Aeromobili attaccanti perduti/salvati
- Forze terrestri distrutte (per tipo di target)
- Controllo territorio
- Rapporto di forze alla fine del conflitto

## Integrazione con il C² Planner

SAGE opera all'interno del [[c2-planner]] del TLC:
- Il C² Planner gestisce la pianificazione operativa terrestre (manovre, riserve)
- SAGE gestisce la pianificazione delle risorse aeree
- Interagiscono: il piano aereo SAGE fornisce target availability al C² Planner terrestre e viceversa

## Vantaggi e Limitazioni

| Aspetto | Vantaggio | Limitazione |
|---------|-----------|------------|
| Adattività | Reagisce alle variazioni tattiche | Non simula decisioni umane reali |
| Ottimizzazione | Trova soluzioni migliori degli script | Richiede definizione esplicita degli obiettivi |
| Controllo utente | Utente controlla obiettivi e grado di ottimizzazione | Analista deve essere coinvolto |
| Trasparenza | Risultati motivati dalle metriche | Il processo di ricerca può non essere intuitivo |

> "The limitations of automated algorithms in representing human behavior" (p. 123) — riconosciuto dagli autori

## Applicabilità al Warfare-Model

**Altamente rilevante** per `Air_Resources_Assigner.py` e `Military_Resources_Assigner.py`:

Il problema di SAGE è esattamente quello degli Assigner nel DWM: data la situazione corrente della campagna, come allocare ottimalmente gli aeromobili (o le risorse militari) ai tipi di missione per massimizzare gli obiettivi di campagna?

Possibili applicazioni:
1. **Misura di merito**: `tactical_evaluation_results.csv` già fornisce dati sugli esiti tattici — usarli come funzione obiettivo per SAGE
2. **Iterazione**: implementare un loop di allocazione-simulazione-riallocation nel ciclo di turno del DWM
3. **Target availability**: il DWM traccia già lo stato delle target (Area, Threat, Storage) — input naturale per SAGE

La complessità dell'implementazione completa di SAGE è alta; una versione semplificata (greedy + re-allocazione su feedback) potrebbe essere un buon punto di partenza.
