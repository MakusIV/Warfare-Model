---
title: "Comparative Dynamic Modelling — Metodo Sabin per Conflitti Storici"
type: concept
tags: [wargame, historical, methodology, comparative, validation]
created: 2026-05-27
updated: 2026-05-27
sources: ["[[source-simulation-techniques-past-conflicts]]"]
related: ["[[philip-sabin]]", "[[wargaming]]", "[[historical-conflict-simulation]]", "[[stochastic-simulation]]", "[[cross-resolution-modeling]]"]
---

# Comparative Dynamic Modelling

## Definizione

Il **Comparative Dynamic Modelling** è la metodologia sviluppata da Philip Sabin nel libro *Lost Battles* (2007) per risolvere controversie storiche sui conflitti dell'antichità (battaglie greche, romane, cartaginesi) attraverso la rielaborazione simulata con diverse ipotesi ricostruttive.

> "[Lost Battles] develops a radical new simulation-based approach of 'comparative dynamic modelling' to help resolve the intractable scholarly controversies over the ill-documented battles of antiquity. Instead of simply being presented with yet another set of personal 'hunches' about what occurred, readers can actually refight the battles for themselves, and experiment with different reconstructions and assumptions in order to gain a greater insight." (Sabin, 2008)

## Principio Metodologico

Quando le fonti storiche sono ambigue, frammentarie o contraddittorie, invece di proporre un'interpretazione soggettiva ("una serie di intuizioni personali"), si costruisce un modello dinamico che:

1. **Cattura le dinamiche essenziali** del tipo di conflitto (fanteria pesante, cavalleria, terreno)
2. **Permette di variare le assunzioni** ricostruttive incerte (forza, disposizione, tattiche)
3. **Testa quale combinazione di assunzioni** produce esiti coerenti con le fonti storiche
4. **Compara dinamicamente** diverse ipotesi sulla stessa struttura di simulazione

## Applicazione: Lost Battles

Battaglie dell'antichità (Maratona, Canne, Zama, ecc.) in cui le fonti danno numeri, schieramenti e descrizioni spesso contraddittori. Il modello di Sabin:
- È **manuale** (mappa, contatori, dado) per accessibilità
- Ha **parametri calibrabili** (dimensioni degli eserciti, qualità delle unità)
- Permette di "rielaborare" la battaglia con diversi parametri
- Se un'ipotesi storiografica produce esiti sistematicamente inconsistenti con le fonti, viene falsificata

## Rilevanza Metodologica Generale

Il comparative dynamic modelling di Sabin è un'applicazione specifica di un principio generale della validazione dei modelli di simulazione:

**"Variare le assunzioni e osservare se gli esiti rimangono coerenti con i dati noti"**

Questo principio è identico a:
- La **sensitivity analysis** dei campaign models (TLC: quanto cambiano i risultati se si variano i parametri di attrito?)
- La **calibration** di CADEM (adattare i parametri del modello affinché riproducano i killer-victim scoreboards)
- La **validazione** di qualsiasi modello di simulazione rispetto a dati storici o sperimentali

## Contraddizioni/Complementarità con Approcci Computazionali

| Aspetto | Comparative Dynamic Modelling | Campaign Model Computerizzato |
|---------|-------------------------------|-------------------------------|
| Dati di partenza | Fonti storiche ambigue | Dati alta risoluzione (JANUS, TAC BRAWLER) |
| Incertezza | Nelle assunzioni ricostruttive | Nella realizzazione stocastica |
| Validazione | Coerenza con fonti storiche | Replication di risultati empirici |
| Scopo | Comprensione retrospettiva | Predizione prospettica |

## Applicabilità al Warfare-Model

Il metodo di Sabin suggerisce un approccio sistematico alla **validazione e calibrazione del DWM**:

1. **Selezionare missioni DCS note** con esiti documentati (log delle sessioni di gioco)
2. **Costruire un "banco di prova" comparativo**: rielaborare quelle missioni con diverse parametrizzazioni del DWM
3. **Verificare quale configurazione riproduce gli esiti storici** delle sessioni passate
4. **Usare questo come calibrazione** dei parametri del modello (analogia con Lost Battles)

Questo è esattamente l'uso del file `tactical_evaluation_results.csv` come fonte di "dati storici" per calibrare il DWM — un approccio da formalizzare.

Vedi anche: [[cross-resolution-modeling]] (lo stesso problema di coerenza tra livelli di risoluzione diversi)
