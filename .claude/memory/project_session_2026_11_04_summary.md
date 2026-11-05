---
name: project-session-2026-11-04-summary
description: "Sessione 2026-11-04 ProArt CHIUSA: Proposta D-4b/D-4c scritta, decisioni prese, blocchi A (des-developer) e B (oc-developer) fatti e verificati, manuale DES aggiornato; suite 4742, fotografia 1009; prossime attivita'"
metadata:
  type: project
---

## Stato di fatto (branch `analysis/dce-dcs-persistence`, pushato a fine sessione)
- **Proposta** `Analysis/Document/Proposta_Dati_Sensori_EWR_Visivo.md` (des-planner, commit `cb980bf8`): 17 decisioni prese una per una, tutte come raccomandato tranne la 12 (reliability radar EWR = stima generica 45/4). Dettaglio in [[project-sensori-d4b-d4c]].
- **Blocco A (D-4c, sensore visivo ZSU-57-2/M163)**: des-developer, commit `37816355`; campo `visual`, `Mobile.D4C_VISUAL_SENSOR` default True, scenario S31-VISUAL; fotografia installata a 1009.
- **Blocco B (D-4b, 8 EWR)**: oc-developer (V4 Pro 0813 su StreamLake, costo reale 0,678 $ dal CSV), commit `cbc75634`; G2 = EWR fuori dal combat score globale; reliability 45/4 non cambia nessuna esecuzione.
- Verifiche rifatte dalla sessione principale su entrambi: suite `Ran 4742`, OK skipped=7; confronto 1009 identiche (0 cambiate, 0 nuove).
- **Manuale DES** aggiornato (des-manual-writer, commit `6dee967b`): cap. 3, 7, 8 (nuova §8.13), 9, nota nell'atlante. Suite/confronto non rieseguiti dall'agente, numeri verificati da me.
- Decisione: **niente upgrade di OpenCode alla 2.x finche' e' beta** ([[feedback-opencode-no-upgrade-beta]]); ProArt resta su 1.19.5.

## Prossime attivita' (in ordine)
1. ~~Documenti rimasti alla sessione principale~~ **FATTI 2026-11-05 (osboxes)**, commit `421cf999`: sezione "D-4c e D-4b" in `F4_Differenze_Scenari.md`, riga nel Piano, nota nella Proposta Volumi §9, nota in [[project-detection-interception-volumes]].
2. ~~Commenti obsoleti in `Air_Route_Manager.py`~~ **FATTI 2026-11-05**, des-developer, commit `ed8d0fa3` (solo testo; verificato diff, `Test_Threat_AA_Factory` Ran 58 OK; suite e confronto non rieseguiti, non necessari). Non ancora pushati (branch avanti di 2 commit su origin).
3. ~~Blocco C (siti fissi EWR)~~ **FATTO 2026-11-05**, commit `efa8f353` (v. [[project-session-2026-11-05-summary]]).
4. **Verifica nell'editor DCS**: lo script DCE `ATO_ThreatEvaluation.lua:1182-1276` riconosce anche "FPS-117", contro la ricerca che dava assenti gli EWR occidentali.
5. **Spunti dalle sessioni precedenti ancora aperti**: D-5 opzione 2 (`dwell_time_s`, cambia la legge del motore), D-7 seconda parte (reti EWR->SAM, Fase 0 C2), D-8; limiti rimandati dell'atlante (provenienza turnaround in `ReadyRecord`, unicita' `session_id` nel ledger, normalizzazione `SessionOutcome`, consolidamento `_domain_id`/`_TIME_EPS`); lacune di test (`MISSION_SPEED`, `MISSION_START_INVALID` positivo, `final_positions` di un aereo uscito di scena); F8d logistica. (Il sospetto sul difetto `_mission_outcome` e' stato SMENTITO il 2026-11-05: l'esito dell'aereo perso per carburante viene da `fuel_ends` (`crashed_at`), non dalla salute; sonda aereo perso + aereo superstite = DESTROYED/FUEL_EXHAUSTED + COMPLETED, salute 0; `Test_Session_Scenarios_S24.TestS24DryAircraft` Ran 5 OK.)
6. **Punto da sciogliere**: la memoria dell'atlante dava P11-P14 del difetto 26 come "prossimo", quella del 2026-10-29 come fatti: controllare nel Piano (righe F4/F8) prima di rifarli.
7. Dopo l'ultimo punto: se serve, correggere il test dal nome ingannevole `test_ewr_in_a_session_detects_and_never_fires` (asserisce solo che l'EWR non spara).

## Cose non ovvie
- Una sola macchina/checkout per volta: niente esecutori in parallelo (un branch, `.ai-run/` condiviso); la cartella di memoria coincide con `.claude/memory/` del repo, quindi scriverci mentre un esecutore lavora sporca il suo working tree.
- La somma dei `cost` di `oc export` conta piu' volte (2,03 $ contro 0,678 $ reali): usare TUI o CSV Activity.
- Il rapporto di oc-developer cita per errore `deepseek-v4-pro`: il modello effettivo e' `deepseek-v4-pro-0813` (da `oc export` -> `modelID`).
- des-manual-writer ha usato un heredoc `python3` da Bash (permessi: `python3 -c` risulta chiuso): controllare `.claude/agents/des-manual-writer.md` e `opencode debug agent` se si vuole capire perche' passa.
- Dalla TUI di `oc` l'avvio rigenera il routing dei fornitori (cache 30 min); il file `routing.local.json` era di 12 giorni prima.
- Per riprendere su un'altra macchina: `git pull`, controllare che il hook SessionStart segnali l'allineamento, venv della macchina (mai `python3` nudo), e `bash tools/ai/verifica.sh suite start` (~10 min ProArt, ~21 osboxes).
