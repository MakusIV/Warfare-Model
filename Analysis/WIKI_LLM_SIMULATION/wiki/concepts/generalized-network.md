---
title: "Generalized Network — Rete Generalizzata per Campaign Models"
type: concept
tags: [generalized-network, game-board, spatial-representation, variable-resolution, warfare-model]
created: 2026-05-27
updated: 2026-05-27
sources: ["[[source-theater-level-campaign-model]]"]
related: ["[[tlc-model]]", "[[campaign-model]]", "[[mapview]]", "[[piston-network]]", "[[variable-resolution-modeling]]"]
---

# Generalized Network — Rete Generalizzata

## Definizione

La Rete Generalizzata è la struttura "game board" sviluppata nel TLC che supera le limitazioni delle strutture a piston e griglia regolare. Combina reti libere ("free-form") con regioni libere ("free-form regions") per rappresentare il terreno e le aree operative con flessibilità variabile.

> "The 'generalized network' structure developed during our research with the TLC model eliminates the need for equal-size regions and regularity, yet maintains the efficiency of the network structure." (p. 18)

## Componenti della Struttura

### 1. Nodi (Nodes)
- Punti sulla rete (basi aeree, obiettivi strategici, posizioni di forze)
- Possono essere "event nodes" creati in preprocessing all'intersezione con regioni

### 2. Archi (Arcs)
- Connessioni tra nodi = percorsi possibili di movimento
- Più archi tra stesso paio di nodi = percorsi alternativi
- Ogni arco appartiene alle regioni che attraversa (riceve attributi di terreno, minaccia, ecc.)

### 3. Regioni (Regions)
Aree libere (poligoni, cerchi, linee) che rappresentano:
- **Terreno**: tipo, trafficabilità, visibilità, foresta
- **Rilevamento**: zone di copertura SAM (raggi circolari), zone radar
- **C²**: settori di controllo aereo, zone di responsabilità
- **Meteo**: generatori meteo per regione
- **Confini**: paesi, aree urbane

Le regioni possono sovrapporsi (es. rilevamento e terreno) o essere contigue (comandi e controllo).

### 4. Griglie (Grids)
- Suddividono archi o regioni in segmenti/sub-regioni di uguale lunghezza
- Scopo principale: **localizzare le interazioni di rilevamento** tra oggetti
- Una griglia segmentata su archi permette rilevamento tra oggetti nello stesso sub-arco
- Griglia rettangolare su regioni per rilevamento tra tipi di entità diverse

### 5. Reti Multiple
- **Reti separate per tipi di entità diversi**: rete aerea (air network) + rete terrestre (ground movement network)
- Le reti condividono alcune regioni per rappresentare interazioni (es. aircraft attaccano ground units)
- Aggiungere/modificare una rete non disturba le altre

## Evoluzione Storica delle Strutture Game Board

```
Piston (TACWAR, CEM)
    ↓ Aggiunge interazioni laterali
Square Grid (TAC THUNDER)
    ↓ Aggiunge 6 direzioni di movimento  
Hexagonal Grid (IDAHEX)
    ↓ Rimuove vincolo di dimensione uniforme
Generalized Network (TLC)
```

| Struttura | Flessibilità | Overhead | Risoluzione Variabile |
|-----------|-------------|---------|----------------------|
| Piston | Minima | Minimo | No |
| Square Grid | Bassa | Basso | Limitata |
| Hexagonal | Media | Medio | Limitata |
| **Generalized** | **Alta** | **Alto** | **Sì** |

## Preprocessing e Event Nodes

Il preprocessing (eseguito da [[mapview]]) determina:
- Intersezioni tra reti, griglie e regioni
- Crea "event nodes" in questi punti di intersezione
- Gli event nodes triggerano eventi (rilevamento, cambio terrain, ecc.) al passaggio di entità

**Vantaggio**: il preprocessing avviene una sola volta per multiple run Monte Carlo o variazioni dello scenario.

## Variable Resolution

La stessa rete può essere usata a diversi livelli di risoluzione semplicemente cambiando il numero di nodi e archi:
- **Bassa risoluzione**: pochi nodi, regioni grandi → analisi rapide
- **Alta risoluzione**: molti nodi, regioni piccole → analisi dettagliate

Esempi di scelte di risoluzione variabile in TLC:
- SAM: risoluzione low (semplice fattore attrito per regione) o high (layout SAM dettagliato, SEAD dinamico)
- Terreno: grandi poligoni aggregati o piccoli poligoni dettagliati
- Forze aeree: generate per regione vs per base aerea specifica vs per squadriglia

## Routing su Rete Generalizzata

- **Algoritmi shortest-path** per determinare percorsi ottimali (distanza, tempo, probabilità di rilevamento minima)
- Percorso "least threatening": minimizza prodotto cumulativo delle probabilità di non-rilevamento (log-sum trick)
- Preprocessing permette lookup istantaneo durante la simulazione
- Possibile "volare fuori dalla rete" verso target specifici con penalità di tempo calcolata

## Applicabilità al Warfare-Model

**Struttura quasi identica** alla Route/Area/Region del DWM:
- `Route` + `RoutePoint` ≈ archi + nodi della rete generalizzata
- `Area`/`Region` ≈ regioni (terreno, C², rilevamento)
- `Limes` ≈ confini tra aree operative (regioni C²)
- Reti separate per `Aircraft`, `Ship`, `Vehicle` ≈ reti multiple per tipi di entità

**Gap identificato**: il DWM non sembra avere un meccanismo di preprocessing equivalente a MapView + event nodes. I routing e rilevamenti sembrano calcolati dinamicamente. Considerare l'adozione del concetto di event nodes pre-calcolati per efficienza.
