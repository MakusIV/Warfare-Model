---
title: "Piston Network — Struttura Game Board Lineare Legacy"
type: concept
tags: [game-board, spatial-representation, legacy, campaign-model, nato]
created: 2026-05-27
updated: 2026-05-27
sources: ["[[source-theater-level-campaign-model]]"]
related: ["[[generalized-network]]", "[[tlc-model]]", "[[tacwar]]", "[[cem-model]]", "[[campaign-model]]", "[[nonlinear-combat]]", "[[variable-resolution-modeling]]"]
---

# Piston Network — Struttura a Piston

## Definizione

La struttura a **piston** (o *piston network*) è la rappresentazione spaziale usata nei modelli di campagna di prima generazione (TACWAR, CEM). Divide il teatro operativo in **bande parallele** orientate perpendicolarmente alla direzione principale di avanzata, con movimento strettamente frontale (fronte lineare che avanza o arretra come un pistone).

## Caratteristiche Strutturali

```
NATO                  Patto di Varsavia
  │   banda 1   │   banda 2   │   banda 3   │
  └──────────────────────────────────────────┘
                   ← / →  fronte
```

- **Bande parallele**: ogni banda è una zona di terreno omogenea
- **Movimento unidirezionale**: le forze si spostano solo perpendicolarmente al fronte
- **Nessuna manovra laterale**: impossibile accerchiamento, breakthrough a settori laterali
- **Aggregazione**: tutte le forze in una banda sono aggregate in un unico "score"

## Origini Storiche

La struttura a piston riflette il contesto strategico della **Guerra Fredda NATO-Patto di Varsavia**: un conflitto previsto come sfondamento lineare lungo le pianure dell'Europa centrale, senza manovre ampie o operazioni non lineari. Era una rappresentazione ragionevole per quel contesto specifico.

## Limitazioni Strutturali

| Limitazione | Impatto sul Modello |
|-------------|---------------------|
| Nessuna manovra laterale | Non può rappresentare accerchiamento, envelopment, exploitation |
| Fronte rigido | Non rappresenta rotte di sfondamento, corridoi di avanzata multipli |
| Aggregazione forze | Perde le relazioni tra tipi di arma |
| Inadatto a scenari post-GF | Conflitti regionali richiedono geometrie non lineari |

## Evoluzione verso Strutture più Flessibili

```
Piston (TACWAR, CEM)       ← questa pagina
    ↓ Aggiunge interazioni laterali
Square Grid (TAC THUNDER)
    ↓ Aggiunge 6 direzioni di movimento
Hexagonal Grid (IDAHEX)
    ↓ Rimuove vincolo di dimensione uniforme
Generalized Network (TLC)  ← soluzione al problema
```

La [[generalized-network]] del TLC supera tutte queste limitazioni mantenendo la flessibilità strutturale necessaria per scenari post-Guerra Fredda.

## Relazione con Combattimento Non-Lineare

La struttura a piston è intrinsecamente incompatibile con il [[nonlinear-combat]]: operazioni come quelle del Golfo (1991) o dei conflitti regionali moderni richiedono rotte di avanzata multiple, manovre di aggiramento e combattimento su fronti discontinui — impossibili da rappresentare con bande parallele.

## Applicabilità al Warfare-Model

Il DWM **non deve** usare una struttura a piston. Le missioni DCS si svolgono in scenari con geometrie complesse (mar Nero, Caucaso, Golfo Persico) che richiedono almeno una struttura a rete libera analoga alla [[generalized-network]]. Le classi `Route`, `Area`, `Region` del DWM corrispondono ai componenti della rete generalizzata TLC — non ai piston.

## Fonti

- Menzionato in: [[source-theater-level-campaign-model]] (pp. 14-18 — confronto strutture game board)
