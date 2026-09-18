---
title: "Audit dei moduli del progetto (origine, 2026-08-16)"
type: decision
tags: [dwm, audit, history, project-status]
created: 2026-08-16
updated: 2026-09-18
status: superseded
affects: []
related: []
---

## Contesto

Dopo una pausa di sviluppo di circa 7 settimane, l'utente ha richiesto una prima fase di analisi approfondita per-sottosistema prima di pianificare ulteriore sviluppo, motivata dal fatto che lo sviluppo fino a quel punto era proceduto "a scatti, senza una visione unificata". Non esisteva alcuna mappa aggiornata di quali sottosistemi funzionassero davvero, quali fossero stub, e quali bug bloccassero la costruzione reale degli oggetti principali del dominio.

## Decisione (evento storico, non scelta architetturale forward-looking)

Sono stati lanciati 11 subagent paralleli, ciascuno incaricato di leggere il codice sorgente reale ed **eseguire la suite di test reale** (non solo lettura statica) per un'area logica del progetto (~57 file raggruppati in 11 aree). L'output: 11 documenti `Analysis/Modules/01_...md`–`11_...md` (in italiano), più una sintesi consolidata in `Analysis/Modules/00_Sintesi.md` contenente un elenco di fix meccanici a basso rischio ordinati per leva, 9 decisioni di design aperte che richiedevano risposta dell'utente prima di procedere, e una roadmap in 4 fasi.

**Rilievo principale dell'audit**: la maggior parte dei test unitari che risultavano "passati" non costruiva mai oggetti reali — mock/stub aggiravano la costruzione — quindi il codebase era meno maturo di quanto il tasso di successo dei test suggerisse. Quasi nulla si istanziava con parametri di default (un solo bug in `Mobile.checkParam` bloccava la costruzione di ogni `Vehicle`/`Ship`/`Aircraft`). La pipeline decisionale in `Logic/` (`Scenario_Manager`/`Strategical_Evaluation`/`Tactical_Evaluation`/`Air_Resources_Assigner`) non era collegata e 3 dei suoi 4 moduli non erano nemmeno importabili. Lo strato di scambio Lua↔DCS descritto in `Analysis/Document/WM_Software_Structure.pdf` risultava del tutto assente dal codice (zero occorrenze di `mission_param`/`mission_result`).

Contestualmente all'audit sono stati eliminati 5 file morti pre-refactoring (`Region old.py`, `Military copy.py`, `Resource_Manager old.py`, `Hemisphere2.py`; `Rinomina_Campaign_State.py` era stato eliminato per errore e poi ripristinato, riservato per riuso futuro) e corretto un bug di import path a livello di progetto (`from Dynamic_War_Manager.Source...` mancante del prefisso `Code.`) su 12 file, che mascherava bug reali dietro test che aggiravano gli import veri via mock.

## Motivazione

Un audit per-sottosistema con esecuzione reale della suite (non solo lettura) è stato scelto per superare esattamente il problema che l'audit stesso ha poi confermato: la copertura di test apparente non rifletteva la maturità reale del codice. Solo eseguendo davvero i test e tentando costruzioni reali di oggetti si potevano distinguere bug mascherati da mock da funzionalità genuinamente solida.

## Conseguenze

Questo audit ha prodotto due fasi di lavoro successive, entrambe concluse:
- **Fase 1** (fix meccanici a leva, 2026-08-17/21): tutti applicati e verificati, suite passata da 1088 test raccolti/47 errori a 2321 raccolti/16 errori+1 fallimento, poi a **2315 test / 0 errori / 0 fallimenti** (commit `9460733c`, `7a5fa679`).
- **Fase 2** (9 decisioni di design): tutte chiuse — 7 risolte e attuate, 2 esplicitamente rimandate. Si veda [[datatype-route-edge-waypoint]] per il dettaglio della decisione #3 (Route/Edge/Waypoint), la più rilevante architetturalmente dell'insieme.

**Stato attuale di questa pagina: superata (`status: superseded`).** I documenti `Analysis/Modules/00_Sintesi.md` e `01_...md`–`11_...md` restano nel repository come **istantanea storica non aggiornata** dello stato del codice al 2026-08-16 — utili per capire da dove è partito il lavoro successivo, ma non affidabili come descrizione dello stato attuale di alcun sottosistema (molti dei bug e degli stub che descrivono sono stati corretti o sostituiti nelle sessioni successive, si vedano le altre pagine di questa cartella `decisions/`). Le pagine `wiki/project/*` — scritte e mantenute da questo stesso processo di documentazione, in sessioni parallele a questa — sono ora la fonte di verità corrente per la struttura e lo stato di ciascun sottosistema del codice. Chi cerca lo stato *attuale* di un modulo deve consultare `wiki/project/`, non `Analysis/Modules/`.

## Fonti

- [[project_module_audit]] (memoria di origine)
- [[project_fase2_design_decisions]] (le 9 decisioni prodotte da questo audit, si veda anche [[datatype-route-edge-waypoint]])
- Pagine `wiki/project/*` (fonte di verità corrente per lo stato dei sottosistemi — categoria, non elencata singolarmente qui)
