---
title: "Cross-Resolution Modeling — Collegamento tra Modelli a Diversa Risoluzione"
type: concept
tags: [cross-resolution, aggregation, campaign-model, methodology]
created: 2026-05-27
updated: 2026-05-27
sources: ["[[source-theater-level-campaign-model]]"]
related: ["[[tlc-model]]", "[[cadem]]", "[[janus-model]]", "[[tac-brawler]]", "[[variable-resolution-modeling]]", "[[campaign-model]]"]
---

# Cross-Resolution Modeling

## Definizione

Il **cross-resolution modeling** è il processo di collegamento tra modelli a diversa risoluzione per fornire dati di efficacia al modello di campagna. I valori per superficie-aria, aria-a-superficie, aria-aria e forze terra-terra devono generalmente provenire da modelli più dettagliati.

**Distinzione importante** con la variable-resolution:
- *Variable-resolution*: un singolo modello che può cambiare il livello di dettaglio internamente
- *Cross-resolution*: collegamento tra modelli **separati** a livelli di risoluzione diversi

## Perché è Necessario

I modelli di campagna non possono simulare i fenomeni di combattimento al livello di dettaglio necessario per valutare la reale efficacia dei sistemi d'arma. Quindi:

1. **Dati storici inadeguati**: non hanno la situazione o granularità giusta
2. **Test su range**: troppo specifici, non coprono il range di situazioni della campagna
3. **Fenomeni terrain-dipendenti**: devono essere modellati ad alta risoluzione (es. acquisizione del target)
4. **Valutazione nuovi sistemi**: non esistono dati storici, bisogna simularli

## Architettura del Processo

```
Modelli Alta Risoluzione          Processo di Aggregazione    Modello Campagna
────────────────────────────       ────────────────────────    ─────────────────
JANUS (terrestre)              →   CADEM (calibration)     →   TLC Ground
TAC BRAWLER (aria-aria)        →   Exchange Tables + Pk    →   TLC Air-to-Air  
JMEM (aria-terra)              →   Damage Tables           →   TLC Air-to-Ground
RJARS (superficie-aria)        →   Eng.Rate + Pk per SAM   →   TLC Surface-to-Air
```

## Il Problema della Consistenza

> "Most current approaches to aggregation, while appearing to be logical, have no good scientific or mathematical basis and cannot be expected to provide consistency across the different levels of aggregation, except within very loose bounds." (p. xv)

**Perché è difficile**:

1. **Mapping low→high è molti-a-molti**: una situazione nel modello di campagna (es. "10 aerei F-16 vs 5 MiG-29") mappa in un **range di situazioni** nel modello ad alta risoluzione (geometrie iniziali, altitudini, training, regole di engagement, ...) — tutte consistenti con la descrizione aggregata

2. **Stochastic output range**: il modello ad alta risoluzione produce una distribuzione di risultati. Il modello di campagna deve stare in quella distribuzione, non solo su un valore medio.

3. **Scale temporali diverse**: un modello aria-aria simula minuti; un modello di campagna simula giorni. Le perdite orarie di un modello tattico sono enormi per un modello di campagna se applicate direttamente.

4. **Aggregazione irreversibile**: una volta aggregati i dati, le relazioni tra tipi di arma sono perse e non recuperabili.

## Approcci all'Attrito nel Modello di Campagna

| Approccio | Metodo | Pro | Contro |
|-----------|--------|-----|--------|
| **Scoring** (TACWAR) | Aggregazione in score Lanchester | Semplice, veloce | Perde relazioni tra armi |
| **Eterogeneo** (TLC/CADEM) | Killer-victim scoreboards + ODE | Fisicamente motivato | Costoso in dati |
| **Pk diretto** | Probabilità di kill per engagement | Semplice per aria | Non scala facilmente |
| **Tabelle lookup** | Situazione → perdite | Veloce | Richiede ampi dataset |

## Osservazioni RAND sulla Cross-Resolution

1. La dipendenza da modelli ad alta risoluzione aumenta significativamente il costo dell'analisi
2. Sono necessari più test degli approcci di cross-coupling — la comunità di difesa non ne fa abbastanza
3. Lo sviluppo dei dati deve essere organizzato a livello DoD, non per organizzazione singola
4. Consistent aggregation può funzionare, ma richiede ricerca dedicata con il modello ad alta risoluzione

## Applicabilità al Warfare-Model

Nel DWM, la cross-resolution si manifesta come:
- **Risultati di missioni DCS** (engagement level) → **stato della campagna** (campaign level)
- Il file `tactical_evaluation_results.csv` rappresenta già output di livello "missione" aggregati a livello campagna
- Il `Resource_Manager.py` esegue una forma di aggregazione quando converte esiti di missioni in variazioni dello stato della campagna

**Gap**: non è chiaro se esista un meccanismo formale di calibrazione degli esiti DCS (equivalente a CADEM/killer-victim scoreboards) nel DWM. Questo è un'area di miglioramento potenziale.
