---
name: project-atlante-diagrammi-manuale-des
description: "Atlante dei diagrammi del manuale DES a livelli L0-L4: pilota fatto (D57-D66), estensione a tutto il core in tre attivita' consecutive A->B->C, A interrotta per limite d'uso; come riprendere"
metadata:
  node_type: memory
  type: project
  originSessionId: 0468db0e-19b3-43df-a060-d82baa1e794b
  modified: 2026-10-30T14:15:18.784Z
---

## Richiesta dell'utente (2026-10-29)
Integrare nel manuale DES diagrammi (UML e simili) a livelli progressivi: classi, strutture dati, metodi, chiamate, interazione fra moduli. Scelte confermate: Mermaid soltanto (niente Java/PlantUML/Node su ProArt: **nessun renderer, la sintassi la verifica l'utente in Obsidian**), perimetro = TUTTO il core DES, classDiagram selettivi + tabella completa con `:riga`, atlante come capitolo nuovo (nessuna colonna "Livello" nell'Elenco: riscriverebbe 56 righe), pilota gradito (densita' D58-D60 e D64-D66 accettabile), correzione della nota di D1 (fatta, `02_Scopo_e_Motivazioni.md`).

## Scala dei livelli
L0 contesto, L1 architettura (grafo reale degli import), L2 moduli (classi/API + tabella completa), L3 interazione (sequenze), L4 algoritmo (i D1-D56 esistenti, intatti). Il pilota ha assegnato i livelli per TIPO di mermaid (grossolano): da riclassificare a mano D8 (->L3), D20 (L2/L3), D18 (tassonomia), e mettere in "Piano e validazione" (fuori scala) D29, D55, D56.

## Stato (pushato su origin a 79bab4e2 il 2026-10-29)
- `9d4f208c` pilota: `Manuale_Motore_DES/11_Atlante_Diagrammi.md` (capitolo 10, D57-D66) + `_strumenti/inventario.py` (ast, sola lettura: `--dipendenze`, `--chiamate`, `--controlla`; poi `--tabella` e `--copertura`, commit successivo).
- **Parte A COMPLETA e committata (42ffb851, locale, 2026-10-30)**: `11a_Atlante_Risolutore.md`, 1442 righe, D67-D87 (D88-D89 non usati), copertura 0 mancanti sui 3 moduli. Completata con des-manual-writer (~225k token per la seconda meta'). Spunti da indagare (sezione «Limiti e domande» del file): metodi `ammunition_consumed*`/`interceptions_consumed` duplicati fra `EngagementResult` e `SessionOutcome` (nel core solo i secondi); `apply_engagement_result` incrementa `ammunition_events`/`interception_events` anche se l'asset non ha il metodo di consumo; `_domain_id` replicato in 3 moduli.
- **Parte B COMPLETA (4fe1225f)**: `11b_Atlante_Missione_Carburante.md`, 1408 righe, D90-D109. Spunti: campi di Mission_Types validati e mai letti (emcon, threat_reaction, alarm_state, activation_event, altitude_reference, formation, priority); AbortReason.THREAT/SUPPORT_MISSING e AssetEndReason.THREAT/MISSION_ABORTED mai prodotti; `EPISODE_GAP = DISENGAGE_TIME`; `_base_options` non usa `asset_id`.
- **Parte C COMPLETA (255f5bc4)**: `11c_Atlante_Porte_Campagna.md`, 1205 righe, D110-D129. Spunti in §10C.10: rami morti del validatore (`no readiness record`), provenienza del turnaround persa in `ReadyRecord`, `SessionOutcome.__post_init__` normalizza meno di `SessionOrder`, `_domain_id`/`_TIME_EPS` replicati.
- **Valutazione dei «Limiti e domande» FATTA (2026-10-30)**: pulizia a comportamento invariato eseguita da des-developer, verificata (suite 4710 OK skipped=7, confronto 989 identiche), commit `191b7d37` (import/param inutilizzati, 4 docstring, commento `target_destroyed`). Decisioni dell'utente: `target_destroyed` su POINT/AREA solo documentato; rimandati: provenienza turnaround in `ReadyRecord` (cambia formato persistito), unicita' `session_id` nel ledger, normalizzazione `SessionOutcome` (rischio fotografia), consolidamento `_domain_id`/`_TIME_EPS`. Esiti scritti nelle sezioni «Limiti e domande» (11a, 11b §10B.5, 11c §10C.10). Branch `ai/cc-limiti-atlante` e `ai/cc-difetto26` cancellati. I `:riga` dei manuali sono di `f009eb43`: `191b7d37` sposta di 3-4 righe i simboli successivi in Fuel_Model/Engagement_Resolver/Damage_Model/Mission_Types (nota nei file).
- **Integrazione FATTA (2026-10-30, commit locale, non pushato)**: Elenco e Indice di `Manuale_Motore_DES.md` (127 righe D), §10.2bis in `11_Atlante_Diagrammi.md`, `AS`->`AST` come id di partecipante nei Mermaid (parola chiave). Nessun renderer: sintassi da controllare in Obsidian. Resta: push (lo fa l'utente), eventuale indagine sugli spunti sopra.
- **Da fare in sequenza (una alla volta, mai in parallelo: richiesta dell'utente per il consumo)**: B = `11b_Atlante_Missione_Carburante.md` (Mission_Types, Fuel_Model, Area_Fire; D90-D109), C = `11c_Atlante_Porte_Campagna.md` (Session_Types, Campaign_Types, Readiness, Session_Validator, Session_Campaign, Damage_Model, Session_Rng + "Mappa dei dati"; D110-D129). Prompt degli agenti: vedi sessione 2026-10-29 (des-manual-writer, modello = pilota). Dopo ciascuna: verifica a campione, `--copertura`, commit locale.
- Integrazione finale (dopo A-C): righe D67+ nell'Elenco e nell'Indice di `Manuale_Motore_DES.md`, tabella-atlante del capitolo 10 (§10.2) con la riclassificazione, aggiornamento "Aggiornato al commit".

## Cose non ovvie
- Il pilota ha trovato che D1 mescola frecce di flusso dei dati e di import (MA importa ER e FC a `Mission_Adapter.py:332-333`).
- Con `G4_EPISODES` acceso (default) la coda `heapq` non ordina gli ingaggi (lista `pending`); `heapq` serve solo al passo finale del carburante.
- Fatto da indagare se l'utente vuole: `_mission_outcome` e' calcolato (`Session_Simulator.py:3098`) prima che l'aereo perso per carburante sia portato a salute 0 (`:3110-3120`); non verificato se sia un difetto (riceve `fuel_ends`).
- Consumo: un agente di pilota ~280k token; A da sola e' il blocco piu' grande (222 simboli).

## Altri sospesi della sessione 2026-10-29
Push fatto dall utente con `! git push` (il classificatore dei permessi blocca il push dell agente); ricerche D-4b/D-4c fatte e committate (`2b6a2c3a`), Proposta unica con decisioni da scrivere dopo il controllo delle fonti deboli; vedi [[project-session-2026-10-29-difetto26-summary]].
