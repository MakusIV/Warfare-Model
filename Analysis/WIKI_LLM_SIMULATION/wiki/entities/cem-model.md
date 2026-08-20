---
title: "CEM — Concepts Evaluation Model (US Army CAA)"
type: entity
tags: [campaign-model, ground, army, piston-network, legacy]
created: 2026-05-27
updated: 2026-05-27
sources: ["[[source-theater-level-campaign-model]]"]
related: ["[[tlc-model]]", "[[tacwar]]", "[[tac-thunder]]", "[[campaign-model]]", "[[piston-network]]", "[[cadem]]"]
---

# CEM — Concepts Evaluation Model

## Descrizione

CEM (Concepts Evaluation Model) è il modello di campagna dell'US Army, sviluppato dal **Center for Army Analysis (CAA)**. Come [[tacwar]], usa una struttura a **piston** e un sistema di attrito aggregato per tipo di arma. Rappresenta la componente terrestre nella famiglia di campaign models legacy dell'esercito americano.

## Caratteristiche Principali

- **Organizzazione**: US Army / Center for Army Analysis (CAA)
- **Struttura game board**: piston (bande parallele, fronte lineare)
- **Focus**: operazioni terrestri (US Army), con supporto aereo aggregato
- **Attrito**: basato su equazioni differenziali etro­genee calibrate su scoreboards (predecessore di [[cadem]])
- **Nota**: CAA ha sviluppato ATCAL (Attrition Calibration), base metodologica su cui RAND ha costruito [[cadem]]

## Relazione con CADEM

Il CEM usa una metodologia di attrito chiamata **ATCAL** (Attrition Calibration) sviluppata dal CAA. RAND ha esteso ATCAL in [[cadem]] per produrre una versione più flessibile e eterogenea. Il CEM è quindi la radice da cui discende la metodologia di attrito del TLC.

## Posizione nel Panorama dei Campaign Models

| Modello | Organizzazione | Struttura | Focus |
|---------|---------------|-----------|-------|
| [[tacwar]] | Joint Staff | Piston | Joint |
| **CEM** | US Army (CAA) | Piston | Ground |
| [[tac-thunder]] | USAF (CACI) | Square Grid | Air |
| [[tlc-model]] | RAND | Gen. Network | Joint |

## Limitazioni (rispetto a TLC)

- Struttura piston: nessuna manovra laterale, accerchiamento, breakthrough
- Attrito aggregato (ATCAL vs CADEM eterogeneo)
- Script di decisione non adattativi

## Relazioni

- Struttura analoga: [[tacwar]] (Joint), [[tac-thunder]] (USAF)
- Evoluzione metodologia attrito: ATCAL (CEM) → [[cadem]] (TLC)
- Superato da: [[tlc-model]]

## Fonti

- Menzionato in: [[source-theater-level-campaign-model]] (pp. 8, 14 — confronto modelli)

## Note

Pagina stub. Informazioni limitate alle menzioni nel documento TLC. Da espandere con documentazione CAA diretta.
