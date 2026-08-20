---
title: "TAC THUNDER — Theater Air Campaign Model (USAF)"
type: entity
tags: [campaign-model, combat-simulation, air, usaf, grid, legacy]
created: 2026-05-27
updated: 2026-05-27
sources: ["[[source-theater-level-campaign-model]]"]
related: ["[[tlc-model]]", "[[tacwar]]", "[[cem-model]]", "[[tac-brawler]]", "[[campaign-model]]", "[[generalized-network]]", "[[piston-network]]"]
---

# TAC THUNDER

## Descrizione

TAC THUNDER è il modello di campagna teatrale dell'USAF (US Air Force), sviluppato da CACI. Usa una struttura a **griglia quadrata** (*square grid*) per la rappresentazione del terreno, che consente interazioni laterali tra forze — a differenza del piston — ma rimane vincolata a celle di dimensione uniforme.

Insieme a [[tacwar]] (Joint Staff) e [[cem-model]] (US Army), rappresenta la generazione di campaign models "legacy" che il TLC tenta di superare.

## Caratteristiche Principali

- **Struttura game board**: griglia quadrata (square grid) — ogni cella ha 4 o 8 direzioni di movimento
- **Linguaggio implementazione**: MODSIM II (CACI) — stesso linguaggio del TLC
- **Focus**: operazioni aeree teatrali USAF
- **Forze**: primariamente aeree, con interazione terra limitata

## Posizione nell'Evoluzione delle Strutture Game Board

```
Piston (TACWAR, CEM)
    ↓ Aggiunge interazioni laterali
Square Grid (TAC THUNDER)   ← qui
    ↓ Aggiunge 6 direzioni di movimento
Hexagonal Grid (IDAHEX)
    ↓ Rimuove vincolo di dimensione uniforme
Generalized Network (TLC)
```

TAC THUNDER è un passo avanti rispetto al piston (permette manovre laterali), ma rimane vincolato alla dimensione uniforme delle celle. La [[generalized-network]] del TLC supera questo limite.

## Limitazioni (rispetto a TLC)

1. **Rigidità della griglia**: celle di dimensione uniforme — non adatte a terreni eterogenei
2. **Nessuna variable-resolution**: risoluzione fissa su tutta la mappa
3. **Struttura C² non adattiva**: usa script fissi di allocazione risorse aeree (vs [[sage-algorithm]])

## Relazioni

- Parte della famiglia: [[campaign-model]] legacy insieme a [[tacwar]], [[cem-model]]
- Superato da: [[tlc-model]] (generalized network + SAGE + CADEM)
- Analogo aereo di: [[tacwar]] (terrestre/joint)
- Linguaggio condiviso: [[modsim-ii]] (CACI)

## Fonti

- Menzionato in: [[source-theater-level-campaign-model]] (pp. 8, 16-18, confronto strutture)

## Note

Dati dettagliati su TAC THUNDER non disponibili nelle fonti attuali — questa è una pagina stub. Da espandere con ingestione di documentazione specifica CACI/USAF.
