---
title: "Simulation Techniques in the Modelling of Past Conflicts"
type: source
tags: [wargame, historical, simulation, academic, manual-simulation, comparative-dynamic-modelling]
created: 2026-05-27
updated: 2026-05-27
file: RAW/simulationtechniquesinthemodellingofpastconflicts.doc
authors: [Philip Sabin]
year: 2008
institution: King's College London
venue: "Higher Education Academy Workshop, University of Warwick"
related: ["[[philip-sabin]]", "[[wargaming]]", "[[comparative-dynamic-modelling]]", "[[historical-conflict-simulation]]"]
---

# Simulation Techniques in the Modelling of Past Conflicts

## Riepilogo Esecutivo

Breve articolo (951 parole) del Prof. Philip Sabin (King's College London) presentato a un workshop dell'Higher Education Academy all'Università di Warwick, dicembre 2008. Descrive l'approccio dell'autore all'uso di simulazioni e wargame nella didattica e nella ricerca accademica sui conflitti storici. Sostiene il valore metodologico delle simulazioni manuali e introduce il concetto di "comparative dynamic modelling" applicato alle battaglie dell'antichità.

## Contributi Principali

1. **Tre ruoli delle simulazioni** nell'insegnamento e nella ricerca storica (coinvolgimento, anti-hindsight, comprensione sistemica)
2. **Argomento anti-hindsight**: le simulazioni riducono il problema della conoscenza retrospettiva, ricordano la natura contingente e incerta degli eventi
3. **Simulations manuali vs computerizzate**: le manuali sono spesso più accessibili ed efficaci; la chiave è il bilanciamento
4. **Comparative Dynamic Modelling**: metodologia per risolvere controversie storiche attraverso la rielaborazione simulata delle battaglie
5. **War as dialectical contest** (Clausewitz): guerra e giochi condividono la struttura di contesa dialettica tra volontà opposte

## Entità Menzionate

- [[philip-sabin]] — autore, professore King's College London
- [[kings-college-london]] — istituzione dell'autore
- [[clausewitz]] — citato: "In the whole range of human activities, war most closely resembles a game of cards"
- [[lost-battles]] — libro di Sabin: approccio simulation-based alle battaglie dell'antichità
- [[simulating-war]] — libro successivo di Sabin (annunciato nel 2008)

## Concetti Chiave Trattati

- [[wargaming]] — gioco di guerra come strumento di analisi e didattica
- [[historical-conflict-simulation]] — simulazione di conflitti storici per fini accademici
- [[comparative-dynamic-modelling]] — metodologia Sabin per battaglie dell'antichità
- [[anti-hindsight]] — capacità delle simulazioni di ridurre il bias della conoscenza retrospettiva
- [[manual-simulation]] — simulazioni non-computerizzate; accessibilità e rigore metodologico

## Citazioni Rilevanti

> "Simulations and games complement more traditional forms of teaching and scholarship in three principal ways. First, they involve users more vividly than does mere passive absorption... Second, they reduce the hindsight problem... Third, they require modellers to develop a logical, comprehensive and wide-ranging understanding of what happened and why."

> "War and games are both dialectical strategic contests between opposing wills, each struggling to prevail." (riferimento a Clausewitz)

> "Clausewitz said that 'In the whole range of human activities, war most closely resembles a game of cards'."

> "Manual simulation techniques are often more accessible and effective. The key is to strike an appropriate balance between intellectual and technological innovation."

> "[Simulations] require modellers to develop a logical, comprehensive and wide-ranging understanding of what happened and why, and so they can often highlight neglected questions and provide a more robust basis for comparative analysis."

## Lacune e Note Contestuali

- Il documento è molto breve (1 pagina) — è un abstract/riassunto per workshop, non un articolo accademico completo
- I riferimenti numerati (1-8) sono presenti nel testo ma le note bibliografiche non sono incluse nel documento
- La trattazione è prevalentemente qualitativa; non contiene modelli matematici o architetture tecniche
- Rappresenta una prospettiva **complementare e opposta** rispetto al TLC di Hillestad & Moore: dove TLC è operativo/computerizzato/RAND, Sabin è storico/manuale/accademico
- Per approfondimenti: cercare i libri "Lost Battles" (Sabin, 2007) e "Simulating War" (Sabin, 2012)

## Contraddizioni con Altre Fonti

**Nessuna contraddizione sostanziale** con [[source-theater-level-campaign-model]] — le due fonti operano su domini diversi (storico-accademico vs operativo-militare), ma si completano:

| Aspetto | Sabin (2008) | Hillestad & Moore (1994) |
|---------|-------------|--------------------------|
| Scopo | Didattica e ricerca storica | Analisi operativa di difesa |
| Metodo | Manuale + semi-computerizzato | Computerizzato (event-step, Monte Carlo) |
| Temporalità | Conflitti passati (antichità–WWII) | Scenari futuri / planning |
| Utenti | Studenti, storici | Analisti, pianificatori militari |
| Valore anti-hindsight | Centrale | Implicito (scenario flexibility) |

## Applicabilità al Warfare-Model

**Applicabilità indiretta ma significativa**:

1. **Anti-hindsight nel DWM**: il DWM dovrebbe presentare gli esiti come incerti (stocastici), non deterministici. L'argomento di Sabin rafforza la tesi stocastica già emersa da TLC: se anche le simulazioni storiche servono a ricordare la contingenza degli eventi, tanto più un simulatore di campagna operativo dovrebbe farlo.

2. **Wargaming come validazione**: Sabin suggerisce che lo sviluppo di una simulazione "richiede di sviluppare una comprensione logica, comprensiva e ampia di cosa è accaduto e perché". Applicare questa metodologia al design del DWM — prima di implementare, "simulare manualmente" lo scenario per capire le dinamiche — potrebbe evidenziare lacune nel modello.

3. **Dialettica degli avversari**: il framework "guerra come contesa dialettica tra volontà opposte" è il fondamento concettuale dell'algoritmo SAGE (ottimizzazione due-lati) e di qualsiasi logica di assegnazione adattiva nel DWM.

4. **Lost Battles come riferimento metodologico**: il metodo di "comparative dynamic modelling" di Sabin — rielaborare battaglie con diverse ipotesi per risolvere controversie — è applicabile alla calibrazione del DWM: rielaborare missioni DCS note con diverse parametrizzazioni per validare il modello.
