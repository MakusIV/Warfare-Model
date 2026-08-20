---
title: "MODSIM II — Linguaggio di Simulazione ad Oggetti (CACI)"
type: entity
tags: [simulation-language, event-driven-simulation, oop, tool, caci]
created: 2026-05-27
updated: 2026-05-27
sources: ["[[source-theater-level-campaign-model]]"]
related: ["[[tlc-model]]", "[[tac-thunder]]", "[[event-driven-simulation]]", "[[stochastic-simulation]]"]
---

# MODSIM II

## Descrizione

MODSIM II è un **linguaggio di programmazione orientato agli oggetti** specializzato per la simulazione a eventi discreti, sviluppato da **CACI Products Company**. È il linguaggio in cui il [[tlc-model]] è implementato. Supporta nativamente il paradigma event-step (event-driven simulation).

## Caratteristiche Principali

- **Tipo**: linguaggio di simulazione OOP (Object-Oriented Programming)
- **Sviluppatore**: CACI Products Company
- **Paradigma**: event-step (event-driven) — non time-step
- **Struttura**: classi e oggetti per entità della simulazione (unità, archi, nodi, eventi)
- **Vantaggi**: efficienza event-step, strutture OOP naturali per modelli complessi

## Perché MODSIM II per TLC

Hillestad & Moore scelgono MODSIM II per il TLC per due ragioni principali:

1. **Paradigma event-step**: perfetto per simulazioni di campagna in cui gli eventi (contatti, combattimenti, spostamenti) sono sparsi nel tempo — vedi [[event-driven-simulation]]
2. **OOP naturale**: le entità militari (forze, aerei, unità) si mappano naturalmente su classi OOP; le interazioni su metodi

> "The TLC model is implemented in MODSIM II, a compiled object-oriented simulation language from CACI Products Company." (p. xvi)

## Relazione con TAC THUNDER

MODSIM II è usato sia per [[tlc-model]] che per [[tac-thunder]] — entrambi sviluppati da/per RAND e CACI. Questo indica un ecosistema condiviso di tooling tra i due modelli.

## Applicabilità al Warfare-Model

Il DWM è implementato in Python — non usa MODSIM II. Tuttavia il **paradigma event-step** che MODSIM II supporta è applicabile: Python permette di implementare event-driven simulation con librerie come `heapq` (priority queue per eventi) o `simpy`. Il design pattern di MODSIM II (classi per entità, eventi schedulati) è il riferimento concettuale.

## Relazioni

- Usato in: [[tlc-model]], [[tac-thunder]]
- Paradigma: [[event-driven-simulation]]
- Alternativa moderna: SimPy (Python), AnyLogic

## Fonti

- Menzionato in: [[source-theater-level-campaign-model]] (p. xvi, pp. 28-30 — architettura software TLC)

## Note

Pagina stub. Documentazione tecnica MODSIM II non disponibile nelle fonti attuali. CACI non la distribuisce pubblicamente.
