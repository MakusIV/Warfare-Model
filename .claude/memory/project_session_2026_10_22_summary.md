---
name: project-session-2026-10-22-summary
description: "Sessione 2026-10-22 osboxes CHIUSA e pushata: F8a e F8b fatte e verificate (suite 4640, fotografia 982 identiche), costi reali OpenRouter misurati (Azure 3 $ vs Baidu 0,16 $), fornitori fissati in opencode.json, V4 Pro 0813, steps 180; prossimo F8c in 3 blocchi sul ProArt"
metadata:
  type: project
---
- **Fatto e verificato dalla sessione principale** (suite + confronto in background, `verifica_seq.sh`): **F8a** (merge `c1182d8a`: `Campaign_Types.py`,
  `Session_Validator.py`, `mission_planned_end`, `session_blocks`, warning E4; suite 4619) e **F8b** (merge `33698fb4`: `IN_PROGRESS` con
  `F8_IN_PROGRESS`=True, `OperationOutcome`, `final_positions`/`movement_ends`/`operation_outcomes`; suite **4640** OK skipped 7, confronto
  **982 IDENTICHE**). Piano della Missione aggiornato (righe F8a, F8b). Fotografia NON reinstallata (resta 982; S30 la portera' a 986 solo
  con l'approvazione dell'utente).
- **Esecutori**: `oc-developer` (OpenCode). F8a: 2 sessioni, la prima interrotta dal limite della chiave (3 $) dopo un ciclo a vuoto e un
  `IndentationError`; la seconda ha chiuso (`e593bc9a`). F8b: 120/120 passi, codice e test completi ma niente rapporto/commit: li ha
  completati la sessione principale (rapporto con avviso di interruzione in `Rapporto_F8b_oc-developer.md`).
- **Costi e fornitori**: v. [[project-opencode-costi-misurati]] e `Analysis/Document/Rapporti/Costi_Deleghe.md` (registro). Sintesi: OpenRouter
  sceglie UN fornitore per sessione (sticky) anche caro (F8a: Azure 3,09 $ + Relace 0,98 $); con `order` in `opencode.json` (Baidu) F8b e'
  costata 0,155 $. Provider Sort del workspace impostato dall'utente su Price. Chiave osboxes a 10 $.
- **Modelli**: planner/developer/debugger passati a `deepseek/deepseek-v4-pro-0813` (commit `6c0b021e`); `steps` oc-developer = **180** e
  regola "rapporto subito + commit WIP a ogni blocco verde" (`.opencode/agents/oc-developer.md`).
- **Il lavoro riprende sul ProArt** (utente, 2026-10-22): `git pull`; `opencode.json` e agenti viaggiano con git (whitelist e `order` sono nel
  file di progetto); la chiave OpenRouter del ProArt e' `opencode-proart` (limite da controllare: la guida dice 5 $, speso ~0,2 $ il 21/10);
  suite ~10 min, confronto ~8: i `wait` consumano meno passi. Verificare nei Logs che il fornitore sia Baidu.
- **Prossimo**: F8c in 3 blocchi con i comandi esatti in [[project-f8c-comandi-blocchi]] (branch `ai/oc-f8c1..3`, verifica dopo ciascuno);
  poi F6-B3 (una riga di docstring `Test_Session_Scenarios_S24.py:357`), `F4_Differenze_Scenari.md` sezione F8, deviazione 25 del Piano;
  F8-R (ricerca tempi di turnaround, serve una sessione Claude col web: nessun agente OpenCode ha accesso al web); F9 (manuale DES).
  Da aggiornare nel repo `ai-multimodel` (dell'utente): guida con prezzi e fornitori reali, whitelist, 0813.
- **Idee/aperte**: `limit.context` per far compattare OpenCode prima (da provare); `Default Provider Sort`=Price non sostituisce `order`;
  logistica (F8d) non realizzata per scelta; dubbio memoria TASK 2 C2 (v. [[project-session-2026-10-21-summary]]).
