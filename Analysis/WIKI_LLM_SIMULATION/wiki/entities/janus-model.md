---
title: "JANUS — Modello di Combattimento Terrestre ad Alta Risoluzione"
type: entity
tags: [ground, combat-simulation, high-resolution, wargame]
created: 2026-05-27
updated: 2026-05-27
sources: ["[[source-theater-level-campaign-model]]"]
related: ["[[tlc-model]]", "[[cadem]]", "[[cross-resolution-modeling]]", "[[killer-victim-scoreboard]]"]
---

# JANUS

## Descrizione

JANUS è un modello di combattimento terrestre ad alta risoluzione citato nel documento come fonte primaria per i dati di attrito terrestre del TLC. Simula il combattimento a livello di singolo veicolo/soldato su una griglia a risoluzione elevata.

## Caratteristiche Principali

- **Risoluzione**: alta — entità individuali (veicoli, soldati)
- **Dominio**: combattimento terrestre (close combat)
- **Struttura**: griglia regolare (quadrata)
- **Temporale**: time-stepped con passi molto piccoli
- **Output chiave per TLC**: killer-victim scoreboards per CADEM

## Limitazioni nel Contesto dei Campaign Models

- La griglia è troppo piccola e ad alta risoluzione per rappresentare efficientemente le operazioni di aeromobili ad ala fissa (risolto rappresentando gli aerei su un modello separato e rendendoli visibili a JANUS solo per gli attacchi aria-terra)
- Scala temporale: simula ore di combattimento ravvicinato, non giorni/mesi come un modello di campagna

## Relazioni con TLC/Cross-Resolution

Nel processo TLC, JANUS genera killer-victim scoreboards che vengono poi:
1. Calibrati → parametri CADEM
2. Estesi per situazioni non presenti nei dati
3. Usati per calcolare attrito terrestre nella simulazione di campagna

Vedi [[cadem]] per il processo completo.

## Fonti
- Menzionato in: [[source-theater-level-campaign-model]] (pp. 63, 17)
