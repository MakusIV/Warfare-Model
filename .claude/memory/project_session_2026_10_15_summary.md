---
name: project-session-2026-10-15-summary
description: "Sessione 2026-10-15 (osboxes) CHIUSA: bingo rifatto (F6-B2bis, G1, G2 committati e pushati), suite 4298 OK; G2 committato SENZA confronto con la fotografia ne' approvazione utente: alla ripresa --compare, revisione differenze, installazione baseline; poi G3, G4, G5"
metadata:
  node_type: memory
  type: project
  originSessionId: 1e331bbd-207a-4b3c-b85b-2e41ee3532b4
  modified: 2026-10-15T16:46:23.008Z
---

**STATO AL 2026-10-15 (chiusura su osboxes)**: branch `analysis/dce-dcs-persistence`, tutto pushato. Ripresa: `git pull`, poi l'interprete
della macchina (osboxes `/usr/bin/python3`; ProArt `.direnv/python-3.12/bin/python3`, v. [[feedback-venv]]). Su osboxes la suite dura circa
16-20 minuti, il confronto circa 13-15: MAI in parallelo.

## Fatto in sessione (dettagli in [[project-bingo-reverse-route-decision]])
1. **F6-B2bis** `96942ca7`: rientro lungo la rotta a ritroso, fabbisogno 1,2 x ritorno, anello = via piu' breve, partenza in volo =
   ritroso + base vicina. Fotografia installata: 770 esecuzioni.
2. **Nuovo modello di bingo** proposto dall'utente: riserva = 5 minuti di disimpegno; albero per tipo di missione. Piano G0-G5 approvato.
3. **G1** `c1c0f576`: `DISENGAGE_TIME` 300 s, `disengagement_reserve` (consumo `emergency` del registro in kg/h = spinta MILITARE,
   strada A), validatore `check_mission_fuel`. Fotografia identica.
4. **G2** (commit di chiusura, "da approvare"): `Fuel_Model.bingo_decision` (funzione generale per G4), soglia = resto della rotta +
   riserva, albero trasferimento (TRANSPORT: continua / ritroso / base piu' vicina / F6-A) e combattimento (interrompe; candidata piu'
   vicina fra base di partenza e basi entro `ALTERNATE_BASE_MAX_OFFSET` 3000 m dalla rotta). Altri elementi:
   - interruttore `F6_BINGO_DISENGAGE_RESERVE`; con G2 acceso `F6_BINGO_REVERSE_ROUTE` non e' piu' letto;
   - `check_mission_bingo(disengage_reserve=True)`;
   - `AssetMissionOutcome.crew_recovered`, che non entra nella fotografia;
   - S26 rifatto: 9 varianti, 72 esecuzioni (carburante `G2_FUEL` 0,27, nuove varianti 'reserve_off', 'transfer_continue'...);
   - Piano §5 deviazione 18, `F4_Differenze_Scenari.md` sezione G2.
   **Suite 4298 OK (7 skipped)**, eseguita dall'agente. Il **confronto con la fotografia NON e' stato eseguito**: l'utente ha chiesto di
   chiudere. L'agente e' stato fermato prima di consegnare il rapporto finale, quindi le scelte dove il brief lasciava margine vanno lette
   nel Piano (dev. 18) e in `F4_Differenze` (sezione G2).

## AGGIORNAMENTO 2026-10-16 (osboxes)
Punti 1 e 2 FATTI: `--compare` ripetuto (794: 762 identiche, 8 cambiate S26 'bingo', 24 nuove; 'reserve_off' identiche alle vecchie
'bingo'), G2 e scelte dell'agente approvati dall'utente, fotografia installata (794), commit `e5465b31` pushato. Prossimo: G3.

## DA FARE ALLA RIPRESA (in ordine)
1. **Verifica G2**: `--compare` con la baseline installata (770). Atteso: differenze su S26 (72 esecuzioni contro 48: varianti cambiate o
   nuove). Ogni altra differenza va spiegata, perche' un aereo di altri scenari sotto il nuovo minimo ora non decolla. Leggere la
   deviazione 18 e la sezione G2 di `F4_Differenze`. Mostrare tutto all'utente (scelte dell'agente + differenze) e chiedere approvazione.
2. **Installare la fotografia** (`--capture` in scratchpad, verifica con `--against`, copia) e fare commit.
3. **G3**: consumo di 5 minuti alla massima spinta militare a ogni ingaggio dell'aereo, nell'istante dell'ingaggio, al posto della
   sovrastima "tutto il movimento a 'max' se ha combattuto". `des-developer` Opus medium.
4. **G4**: ri-scheduling dopo l'ingaggio. Dopo ogni ingaggio richiamare `bingo_decision`, cancellare le finestre future dell'aereo e
   ricalcolarle; e' il limite noto P2/R4 di `Session_Simulator`. Prima l'analisi dell'architettura; proposta Opus effort high.
5. **G5**: S27 (trasferimento, anello con base alternativa, due intercettazioni), manuale.
6. Ancora aperti:
   - F6-B3 (S24-GLIDE con bingo di default, da rivalutare col G2);
   - conferma "validatore fuori da `run_session`";
   - F7 (filtro armi A4 + salva su area, prima proposta separata), F8, F9 (manuale: togliere "TOT comune" in 03 e 10, documentare F5/F6/G);
   - arretrato: correzione del registro `emergency`/`time`, test instabile `testCalcFightResult`, Fase 0 C2, rotte -> mappe.
