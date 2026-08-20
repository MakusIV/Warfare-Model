---
title: "MapView — GUI per Reti Generalizzate"
type: entity
tags: [tool, gui, generalized-network, preprocessing, warfare-model]
created: 2026-05-27
updated: 2026-05-27
sources: ["[[source-theater-level-campaign-model]]"]
related: ["[[tlc-model]]", "[[generalized-network]]", "[[rand-corporation]]"]
---

# MapView

## Descrizione

MapView (McDonough, Bailey, Koehler, 1993) è uno strumento GUI sviluppato come parte del progetto TLC per la creazione e il preprocessing interattivo delle reti generalizzate. È descritto nel documento separato *MAPVIEW User's Guide* (MR-160-AF/A, 1993).

## Funzionalità

- Importazione di mappe di sfondo (immagini satellitari, World Data Bank, Defense Mapping Agency, mappe scansionate)
- Disegno interattivo di nodi, archi, regioni e griglie sulla mappa
- Preprocessing automatico: crea nuovi nodi nei punti di intersezione tra archi e regioni (event nodes)
- Partizione di aree in regioni non sovrapposte
- Risoluzione di dati sovrapposti o in conflitto tra regioni

## Importanza per TLC

> "The productive use of a generalized network probably requires a GUI." (p. 21)

La rete generalizzata è sufficientemente complessa da richiedere obbligatoriamente un'interfaccia grafica per la sua costruzione e verifica. La visualizzazione permette di identificare immediatamente problemi come rotte aeree che evitano zone di difesa che non dovrebbero essere evitabili.

## Applicabilità al Warfare-Model

Il DWM ha già una struttura di Region/Area/Route/Waypoint. Un'interfaccia analoga a MapView per visualizzare e modificare la mappa di operazioni DCS sarebbe utile per configurare scenari di campagna dinamica.

## Fonti
- Menzionato in: [[source-theater-level-campaign-model]] (pp. 21, preface)
