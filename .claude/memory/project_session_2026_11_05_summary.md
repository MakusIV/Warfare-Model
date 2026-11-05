---
name: project-session-2026-11-05-summary
description: "Sessione 2026-11-05 osboxes: documenti D-4b/D-4c, commenti Air_Route_Manager, sospetto _mission_outcome smentito, blocco C siti fissi EWR fatto (suite 4757, fotografia 1009); prossime attivita'"
metadata:
  type: project
---

## Stato di fatto (branch `analysis/dce-dcs-persistence`, sessione su osboxes, NON ancora pushata oltre `2bc0f6bb`: 6 commit avanti)
- Documenti D-4b/D-4c (F4, Piano, Proposta Volumi §9, memoria): commit `421cf999`.
- Commenti obsoleti di `Air_Route_Manager.py` corretti da des-developer: `ed8d0fa3` (solo testo).
- **Sospetto su `_mission_outcome` SMENTITO** con sonda: l'esito dell'aereo perso per carburante viene da `fuel_ends`, non dalla salute (S24 Ran 5 OK; caso misto = DESTROYED/FUEL_EXHAUSTED + COMPLETED). Non e' un difetto.
- **Blocco C (siti fissi EWR)**: des-planner (Opus high) ha scritto `Proposta_Dati_Sensori_EWR_Siti_Fissi.md` (`3594dda1`, `7264b028`), des-developer l'ha eseguita (`efa8f353`). Dettagli in [[project-sensori-d4b-d4c]]. Suite 4757 OK, confronto 1009 identiche (verificati dalla sessione principale su osboxes: suite ~1150 s, confronto ~1000 s).
- Manuale DES aggiornato al blocco C (`e2770929`).
- Branch `ai/oc-f8a`, `ai/oc-f8b` cancellati (gia' uniti).

## Prossime attivita' (in ordine)
1. ~~Manuale DES per il blocco C~~ **FATTO**, des-manual-writer, commit `e2770929` (cap. 3, 7, 8, 9, note d'atlante; chiuse le voci 28 e 29 di §9.6; `:riga` di `Vehicle_Data.py` e `Air_Route_Manager.py` ricalcolati). Verificato dalla sessione principale: perimetro, numeri, campione di `file:riga`.
2. **Verifica nell'editor DCS**: lo script DCE `ATO_ThreatEvaluation.lua:1182-1276` riconosce anche "FPS-117" (decisione dell'utente, non eseguibile da me).
3. Spunti aperti: D-5 opzione 2 (`dwell_time_s`, cambia la legge di `Engagement_Resolver.detection_probability`, va pianificata con des-planner), D-7 seconda parte (reti EWR->SAM, Fase 0 C2), D-8, curva portata-quota degli EWR, immobilita' imposta dal motore (C-4, regola nuova con interruttore); F8d logistica; limiti rimandati dell'atlante; lacune di test (`MISSION_SPEED`, `MISSION_START_INVALID` positivo, `final_positions` di un aereo uscito di scena).
4. Pulizie piccole: test dal nome ingannevole `test_ewr_in_a_session_detects_and_never_fires` (asserisce solo che l'EWR non spara; il test gemello dei siti fissi ha lo stesso nome); controllare nel Piano se P11-P14 del difetto 26 sono fatti.

## Cose non ovvie
- Su osboxes non c'e' venv: i test girano con il `python3` di sistema; `Test_Air_Route_Manager` ~200 s, suite ~20 min, confronto ~17 min.
- `des-planner`/`des-developer` possono notificare "completato" mentre una loro sonda in background gira ancora (suite del planner ~28 min): controllare con `pgrep -af probe_suite|unittest|verifica` prima di lanciare altre verifiche (mai in parallelo).
- Il planner ha rinominato le sue sonde in S-1..S-5 per non confonderle con le decisioni C-0..C-4.
- La memoria vive in `.claude/memory/` del repo: scriverci sporca il working tree, quindi mai mentre un esecutore lavora.
- des-manual-writer ha usato un `python3` inline da Bash per una sostituzione (gia' notato il 2026-11-04): i permessi non bloccano il caso, da controllare con `opencode debug agent` solo se interessa irrigidirli.
