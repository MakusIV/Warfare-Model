---
title: "TACWAR — Theater Campaign Wargame Model"
type: entity
tags: [campaign-model, wargame, piston-network, joint, legacy]
created: 2026-05-27
updated: 2026-05-27
sources: ["[[source-theater-level-campaign-model]]"]
related: ["[[tlc-model]]", "[[piston-network]]", "[[cem-model]]", "[[tac-thunder]]", "[[campaign-model]]"]
---

# TACWAR

## Descrizione

TACWAR (US Army, 1994a) è il modello di campagna teatrale principale dello Joint Staff degli USA. Modello aggregato che usa una struttura a piston per rappresentare le operazioni terrestri e il combattimento aereo in maniera semplificata.

## Caratteristiche

- **Struttura**: piston (bande parallele, movimento lineare)
- **Attrito terrestre**: basato su equazioni Lanchester con parametri ottenuti da eigenvalori delle equazioni eterogene (Anderson, Hampton, Turley 1980)
- **Aria**: rappresentazione aggregata per time-step
- **Decisioni**: script non adattativi di ordini o semplici regole di codice
- **Usato da**: Joint Staff USA per valutare la struttura delle forze nelle contingenze regionali

## Limitazioni (identificate nel documento TLC)

1. Struttura piston non permette manovre laterali, accerchiamento, breakthrough
2. Modello decisionale non reattivo: non si adatta alle variazioni tattiche/equipaggiamento
3. Aggregazione completa delle forze in un unico "score" perde le relazioni tra tipi di arma
4. Ottimizzato per scenario NATO-Patto di Varsavia, difficile da adattare a scenari post-Guerra Fredda

## Relazioni

- Struttura analoga: [[cem-model]] (US Army), [[tac-thunder]] (USAF)
- Supera: [[tlc-model]] tenta di superare queste limitazioni
- Vedi: [[piston-network]] per comprensione della struttura

## Fonti
- Menzionato in: [[source-theater-level-campaign-model]] (pp. 8, 14, 65)
