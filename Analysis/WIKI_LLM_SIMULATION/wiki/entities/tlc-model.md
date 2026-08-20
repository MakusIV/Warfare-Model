---
title: "TLC — Theater-Level Campaign Model"
type: entity
tags: [campaign-model, rand, joint, air, ground, naval, event-driven, stochastic, warfare-model]
created: 2026-05-27
updated: 2026-05-27
sources: ["[[source-theater-level-campaign-model]]"]
related: ["[[rand-corporation]]", "[[generalized-network]]", "[[cadem]]", "[[sage-algorithm]]", "[[c2-planner]]", "[[mapview]]", "[[modsim-ii]]"]
---

# TLC — Theater-Level Campaign Model

## Descrizione

Il Theater-Level Campaign Model (TLC) è un prototipo di ricerca RAND sviluppato a metà anni '90 per la prossima generazione di modelli di analisi del combattimento a livello teatro. È un modello di simulazione event-stepped, stocastico, orientato agli oggetti, progettato per analisi di campagna militare a livello operativo/teatrale nel contesto post-Guerra Fredda.

**Non è un modello operativo "da produzione"**: è un banco di prova per soluzioni innovative ai problemi delle prossima generazione di modelli di campagna.

## Caratteristiche Principali

### Game Board: Rete Generalizzata
- Struttura di nodi, archi, regioni e griglie liberamente definibili
- Supera la struttura piston (lineare NATO-Patto di Varsavia) e la griglia regolare
- Reti separate per entità diverse (aerei, forze terrestri, ecc.)
- Preprocessing via GUI ([[mapview]]) per efficienza computazionale
- Supporta variable-resolution: bassa (poche regioni) o alta (molti nodi) nello stesso modello

### Gestione del Tempo: Event-Step
- Implementato in MODSIM II (linguaggio CACI, event-step oriented)
- Avanza al prossimo evento invece di iterare passi fissi
- Più efficiente per simulazioni con lunghi periodi di inattività
- Permette steps molto piccoli quando molti eventi accadono simultaneamente

### Struttura Stocastica: Monte Carlo
- Processi casuali simulati con numeri casuali (Bernoulli trials per kill/survival)
- Necessita di multiple run per stime statistiche
- Argomento centrale: la simulazione deterministica di sistemi stocastici introduce errori sistematici non eliminabili

### Cross-Resolution Modeling
Input da modelli ad alta risoluzione:
| Dominio | Modello Alta Risoluzione | Dati Estratti |
|---------|--------------------------|---------------|
| Terrestre | [[janus-model]] | Killer-victim scoreboards → [[cadem]] |
| Aria-Aria | [[tac-brawler]] | Exchange tables + Pk |
| Aria-Terra | JMEM | Hits-to-kill, damage tables |
| Superficie-Aria | [[rjars]] | Engagement rates, Pk per tipo SAM |

### C² Planner
- Pianifica manovre operative terrestri su rete generalizzata
- Valuta probabilità di successo per diversi piani di manovra
- Alloca riserve per massimizzare probabilità degli obiettivi prioritari
- Pianifica per attaccante, difensore, o entrambi

### Algoritmo SAGE (Sequential Analytic Game Evaluation)
- Allocazione adattiva di risorse aeree (aerei, fuochi a lunga gittata, elicotteri) a tipi di missione
- L'utente specifica una misura di merito (es. massimizza attrito avversario, minimizza il proprio)
- Ricerca iterativa della strategia ottimale
- Vedi [[sage-algorithm]] per dettagli

## Relazioni

- Sviluppato da: [[rand-corporation]]
- Sponsorizzato da: US Air Force (Project AIR FORCE), US Army (Arroyo Center)
- Autori principali: Richard J. Hillestad, Louis Moore
- Contributo chiave: John Owen ([[british-doae]])
- Linguaggio: [[modsim-ii]] (CACI)
- GUI: [[mapview]]
- Predecessore RAND: [[rsas]], [[apex-model]], [[tac-sage]]
- Modelli legacy che TLC supera: [[tacwar]], [[cem-model]], [[tac-thunder]]
- Modelli comparabili: [[jicm-model]] (global scope), [[janus-model]] (high-res ground)

## Note e Limitazioni Riconosciute dagli Autori

1. **Non risolve definitivamente la cross-resolution**: le aggregazioni sono approssimate
2. **Costo dei dati**: dipende da modelli ad alta risoluzione che richiedono risorse significative
3. **Combinatoria della variable-resolution**: 10 oggetti × 2 risoluzioni = 20 miliardi di interazioni potenziali
4. **SAGE non simula pienamente il comportamento umano**: limiti degli algoritmi automatici
5. **Raccomandazione**: modelli con scopo limitato e specifico, non modelli generalissimi

## Applicabilità al Warfare-Model

**Diretta e alta**. TLC affronta esattamente i problemi del Warfare-Model DCS:
- La rete generalizzata → Route/Area/Region nel DWM
- SAGE → Air_Resources_Assigner + Military_Resources_Assigner  
- C² Planner → Manager.py logica di pianificazione campagna
- Stochastic simulation → tactical_evaluation_results (già stocastico)
- Cross-resolution → integrazione con modelli di engagement DCS

Vedi [[source-theater-level-campaign-model#Applicabilità al Warfare-Model]] per dettagli.
