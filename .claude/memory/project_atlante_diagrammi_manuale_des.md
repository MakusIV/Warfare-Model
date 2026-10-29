---
name: project-atlante-diagrammi-manuale-des
description: "Atlante dei diagrammi del manuale DES a livelli L0-L4: pilota fatto (D57-D66), estensione a tutto il core in tre attivita' consecutive A->B->C, A interrotta per limite d'uso; come riprendere"
metadata:
  type: project
---
## Richiesta dell'utente (2026-10-29)
Integrare nel manuale DES diagrammi (UML e simili) a livelli progressivi: classi, strutture dati, metodi, chiamate, interazione fra moduli. Scelte confermate: Mermaid soltanto (niente Java/PlantUML/Node su ProArt: **nessun renderer, la sintassi la verifica l'utente in Obsidian**), perimetro = TUTTO il core DES, classDiagram selettivi + tabella completa con `:riga`, atlante come capitolo nuovo (nessuna colonna "Livello" nell'Elenco: riscriverebbe 56 righe), pilota gradito (densita' D58-D60 e D64-D66 accettabile), correzione della nota di D1 (fatta, `02_Scopo_e_Motivazioni.md`).

## Scala dei livelli
L0 contesto, L1 architettura (grafo reale degli import), L2 moduli (classi/API + tabella completa), L3 interazione (sequenze), L4 algoritmo (i D1-D56 esistenti, intatti). Il pilota ha assegnato i livelli per TIPO di mermaid (grossolano): da riclassificare a mano D8 (->L3), D20 (L2/L3), D18 (tassonomia), e mettere in "Piano e validazione" (fuori scala) D29, D55, D56.

## Stato (commit locali, NON pushati)
- `9d4f208c` pilota: `Manuale_Motore_DES/11_Atlante_Diagrammi.md` (capitolo 10, D57-D66) + `_strumenti/inventario.py` (ast, sola lettura: `--dipendenze`, `--chiamate`, `--controlla`; poi `--tabella` e `--copertura`, commit successivo).
- **Parte A interrotta** (limite d'uso 87%/5h): `11a_Atlante_Risolutore.md` NON committato, 899 righe, 14 diagrammi: `Contact_Scheduler` (D67-D70) e `Fire_Control` (D71-D75) completi con tabelle; `Engagement_Resolver` (D76-D80) a meta' (tabella completa e rapporto finale mancanti). Da verificare e completare o rifare; numeri D riservati: A = D67-D89.
- **Da fare in sequenza (una alla volta, mai in parallelo: richiesta dell'utente per il consumo)**: A (completare), B = `11b_Atlante_Missione_Carburante.md` (Mission_Types, Fuel_Model, Area_Fire; D90-D109), C = `11c_Atlante_Porte_Campagna.md` (Session_Types, Campaign_Types, Readiness, Session_Validator, Session_Campaign, Damage_Model, Session_Rng + "Mappa dei dati"; D110-D129). Prompt degli agenti: vedi sessione 2026-10-29 (des-manual-writer, modello = pilota). Dopo ciascuna: verifica a campione, `--copertura`, commit locale.
- Integrazione finale (dopo A-C): righe D67+ nell'Elenco e nell'Indice di `Manuale_Motore_DES.md`, tabella-atlante del capitolo 10 (§10.2) con la riclassificazione, aggiornamento "Aggiornato al commit".

## Cose non ovvie
- Il pilota ha trovato che D1 mescola frecce di flusso dei dati e di import (MA importa ER e FC a `Mission_Adapter.py:332-333`).
- Con `G4_EPISODES` acceso (default) la coda `heapq` non ordina gli ingaggi (lista `pending`); `heapq` serve solo al passo finale del carburante.
- Fatto da indagare se l'utente vuole: `_mission_outcome` e' calcolato (`Session_Simulator.py:3098`) prima che l'aereo perso per carburante sia portato a salute 0 (`:3110-3120`); non verificato se sia un difetto (riceve `fuel_ends`).
- Consumo: un agente di pilota ~280k token; A da sola e' il blocco piu' grande (222 simboli).

## Altri sospesi della sessione 2026-10-29
Push di 11 commit bloccato dal classificatore dei permessi (l'utente lo fa con `! git push origin analysis/dce-dcs-persistence` o aggiungendo una regola); ricerche D-4b/D-4c fatte e committate (`2b6a2c3a`), Proposta unica con decisioni da scrivere dopo il controllo delle fonti deboli; vedi [[project-session-2026-10-29-difetto26-summary]].
