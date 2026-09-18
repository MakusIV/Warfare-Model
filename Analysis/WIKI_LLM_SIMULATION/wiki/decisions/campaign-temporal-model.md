---
title: "Modello temporale di campagna: sessioni DCS vs. sessioni sintetiche"
type: decision
tags: [temporal-model, dcs, synthetic-session, turn-structure]
created: 2026-09-08
updated: 2026-09-18
status: superseded
superseded_by: ["[[c2-hierarchy-design]]"]
affects: ["[[context-state]]"]
related: ["[[philip-sabin]]", "[[wargaming]]"]
---

## Contesto
Il Dynamic War Manager deve generare gli eventi di campagna (ingaggi, perdite, esiti missione) combinando due fonti eterogenee: le sessioni DCS giocate da umani in tempo reale, e il resto della campagna che DCS — per limiti hardware/computazionali del motore — non può mai rappresentare per intero contemporaneamente. Serviva una regola per distinguere e ricombinare queste due fonti, e una struttura a turni per la parte sintetica.

## Decisione (framing originale, 2026-09-08)
Due categorie di sorgente evento, gestite diversamente:

1. **Eventi di sessione DCS** (tempo reale, giocati da umani): una sessione DCS è un insieme di missioni (asset coinvolti, rotte, ruoli, target); gli eventi che ne derivano sono il risultato di scontri reali in tempo reale. Vincolo hardware: una sessione DCS può coinvolgere solo una piccola frazione degli asset che una campagna reale avrebbe attivi contemporaneamente.
2. **Eventi di sessione sintetica**: per compensare il limite sopra, un generatore sintetico produce il volume/tipo di eventi che si verificherebbero con il numero realistico (pieno) di asset coinvolti, per l'unità di tempo considerata. Flusso: acquisisci i risultati della sessione DCS → esegui il simulatore sintetico per l'unità di tempo → combina i due risultati con pesi (peso ai risultati attribuibili ai giocatori umani vs. all'output sintetico).

**Bozza utente (trovata 2026-09-09)** in `Analysis/Document/Appunti struttura turno evento simulato` (non creata dall'assistente): il turno della fazione attiva (Blue) si divide in **pianificazione/reazione** + **esecuzione**; la fazione in attesa (Red) reagisce agli eventi generati durante il turno di Blue invece di restare "congelata" fino al proprio turno — ricalca la tecnica Igo-Ugo a "metà turno sovrapposte" di [[philip-sabin]] (fonte: *Modelling Time in Wargames*, mai salvata su disco — solo riassunto in `reference_philip_sabin_simulating_war`, da ri-scaricare se si riprende questo filone in dettaglio).

## Motivazione
Senza questa distinzione, il modello avrebbe dovuto scegliere fra scala realistica (impossibile per l'hardware DCS) o fedeltà solo alla piccola sessione umana (non rappresentativo di una campagna reale). La separazione in due pipeline permette di avere entrambe le proprietà, pesate.

## Conseguenze — RISOLTO E SUPERATO da [[c2-hierarchy-design]] (2026-09-17)
La domanda aperta centrale di questa decisione — "che struttura a turni ha il lato sintetico?" — è stata risolta il 2026-09-17: l'unità di turno del lato sintetico **è la sessione stessa** (non un impulso/turno astratto). L'esecuzione è **interlacciata e guidata dal giocatore** (le sessioni virtuali girano negli intervalli prima/dopo le sessioni DCS reali, scarto di 1-2 ore, non 1-20h come una lettura preliminare del PDF sorgente aveva erroneamente indicato), col ciclo C2 (analizza→pianifica→esegui) che gira prima e dopo ogni singola sessione. Il dettaglio completo, inclusi i punti ancora aperti (meccanica di negoziazione, fusione delle sessioni tra i due side), vive in [[c2-hierarchy-design]], che va considerata autorevole su questo tema.

Questa pagina resta per il framing originale DCS-vs-sintetico e per la bozza Igo-Ugo Blue/Red, che restano contesto storico rilevante — non ancora formalmente riconciliata con il modello C2, ma coerente con esso.

## Fonti
- [[project_campaign_temporal_model_dcs_vs_synthetic]] (memoria di origine)
- [[project_c2_hierarchy_design]] (decisione che supera questa)
