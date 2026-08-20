---
title: "Historical Conflict Simulation — Simulazione di Conflitti Storici"
type: concept
tags: [historical, wargame, academic, methodology, sabin, anti-hindsight]
created: 2026-05-27
updated: 2026-05-27
sources: ["[[source-simulation-techniques-past-conflicts]]"]
related: ["[[philip-sabin]]", "[[wargaming]]", "[[comparative-dynamic-modelling]]", "[[anti-hindsight]]", "[[stochastic-simulation]]", "[[campaign-model]]"]
---

# Historical Conflict Simulation

## Definizione

La **simulazione di conflitti storici** è l'uso di tecniche di simulazione e wargaming per studiare, analizzare e comprendere battaglie e campagne del passato. Si distingue dalla simulazione operativa/predittiva (es. TLC) per il fatto che l'esito è noto: il valore sta nel comprendere *perché* l'esito è avvenuto e *quanto era contingente*.

> "The great strength of gaming over other forms of simulation is that it is not just an analysis tool, but also a teaching tool, an engagement tool and a research tool all rolled into one." (Sabin, 2008)

## Obiettivi

| Obiettivo | Descrizione |
|-----------|-------------|
| **Comprensione** | Capire le dinamiche e la logica del conflitto passato |
| **Anti-hindsight** | Rendere di nuovo incerto ciò che sappiamo essere accaduto — vedi [[anti-hindsight]] |
| **Validazione storiografica** | Testare ipotesi ricostruttive tramite [[comparative-dynamic-modelling]] |
| **Didattica** | Insegnare storia militare in modo esperienziale |
| **Ricerca** | Risolvere controversie su battaglie mal documentate |

## Approcci Principali

### 1. Wargame Manuale (Sabin)
- Mappa fisica, contatori, dado
- Accessibile, adatto all'aula
- Usato per battaglie dell'antichità (Maratona, Canne, Zama)
- Vedi: [[wargaming]], [[comparative-dynamic-modelling]]

### 2. Simulazione Computerizzata Storica
- Engine di simulazione applicato a dati storici
- Più veloce per large-scale analysis
- Esempio: use di campaign models per re-fight battaglie WWII

### 3. Approccio Ibrido (Semi-computerizzato)
- Computer per calcoli, decisioni umane
- Bilancia velocità e agency

## Contributo Metodologico al Dominio

La simulazione storica ha contribuito al dominio della simulazione bellica con:

1. **Rigorosa calibrazione**: i modelli devono riprodurre esiti noti — disciplina metodologica
2. **Focus sull'incertezza**: l'esito noto non deve rendere la simulazione deterministica — il percorso verso quell'esito era incerto
3. **Comparative dynamic modelling**: metodologia sistematica per validare ipotesi con variazione di assunzioni
4. **Anti-hindsight**: concetto trasferibile ai modelli operativi per mantenere l'incertezza degli esiti

## Applicabilità al Warfare-Model

La prospettiva storica di Sabin è direttamente applicabile alla **validazione e calibrazione del DWM**:

1. Le **sessioni DCS passate** sono il "dato storico" — esiti noti
2. Il DWM deve **riprodurre quegli esiti** quando applicato con i parametri corretti
3. La metodologia [[comparative-dynamic-modelling]] fornisce il framework: variare i parametri DWM e verificare quale configurazione riproduce gli esiti storici delle sessioni passate

Il file `tactical_evaluation_results.csv` è il "corpus storico" da cui calibrare il DWM — esattamente come Sabin usa le fonti antiche per calibrare il suo modello di Lost Battles.

## Differenza con Simulazione Operativa/Predittiva

| Aspetto | Simulazione Storica | Simulazione Operativa |
|---------|--------------------|-----------------------|
| Esito | Noto | Da predire |
| Scopo primario | Comprensione/validazione | Analisi/predizione |
| Dati | Fonti storiche | Dati sperimentali, modelli alta risoluzione |
| Validazione | Coerenza con fonti | Replication di risultati empirici |
| Incertezza | Nell'interpretazione | Nella realizzazione stocastica |

## Fonti

- Menzionato in: [[source-simulation-techniques-past-conflicts]] (passim — tema centrale del documento)
