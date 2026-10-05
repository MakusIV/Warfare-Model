---
name: project-session-2026-10-05-summary
description: "Sessione 2026-10-05 (ProArt P16) CHIUSA, tutto committato e pushato, suite 3929 OK: struttura Missione (decisioni D1-D6/N1-N3, piano F0-F9, F0-F3 + F4a fatte), doc missioni DCS ingerita, manuale DES aggiornato a 533cd1f5; prossimo F4b"
metadata:
  type: project
---

**Macchina**: ProArt P16 (WSL2), branch `analysis/dce-dcs-persistence`. Sessione CHIUSA con tutto
committato e pushato. **Alla ripresa, su qualunque macchina: `git pull` prima di tutto** (python per
macchina: v. [[feedback-venv]]; qui `.direnv/python-3.12/bin/python3`). Suite completa 3929 OK
(7 skipped), ~6 min qui. Fotografia di non regressione degli scenari (292 esecuzioni, ~4 min):
`PYTHONPATH=$PWD/Code:$PWD <python> -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline --compare
Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json` (`--summary` per un riepilogo leggibile).

## STATO DI FATTO
1. **Documentazione missioni DCS** (cartella `Analysis/Document/documentazione missioni dcs/`): estratti in
   `estratti/` (manuale ME pp. 84-357 in 4 parti con figure, foto ME, struttura .miz DCE, missione di prova
   terra/mare `ground_sea_mission.miz`, registri aeroporti e beacon del Caucaso in CSV). Gli originali (PDF,
   foto, .miz) NON sono tracciati per scelta dell'utente. Sintesi: `Analisi_Informazioni_Missione.md`.
   L'utente aveva ragione: veicoli e navi ricevono bersagli espliciti (AttackGroup, FireAtPoint).
2. **Decisioni sulla Missione**: v. [[project-mission-structure-decisions]] (D1-D6, N1-N3, N3.f = B, regola A
   della velocità), documento `Proposta_Struttura_Missione_Decisioni.md`.
3. **Piano** `Piano_Implementazione_Missione.md` (§5 = avanzamento e deviazioni). Fatte F0 (fotografia), F1
   (`Command/Mission_Types.py`), F2 (tassonomia in Context, `AIR_COMBAT_TASK`), F3 (missioni nella porta,
   `Logic/Mission_Adapter.py`, `run_session` senza routes/starts/speeds), F4a (regola A; diff in
   `F4_Differenze_Scenari.md`). Rename `Retrait` → `Retreat` fatto.
4. **Manuale DES** aggiornato al commit `533cd1f5` (F3) con l'agente `des-manual-writer`; diagrammi D1-D29;
   capitolo 10 §9.6 elenca 11 incoerenze documenti/codice. F4a non è ancora nel manuale.

## PROSSIME ATTIVITÀ (in ordine)
1. **F4b**: missione come unità di ingaggio (vista `MissionForce`; `resolve_engagement` accetta qualunque
   oggetto con assets/side/name), `mission_id` negli id d'ingaggio/RNG; diff documentata in
   `F4_Differenze_Scenari.md`, fotografia rigenerata, commit dedicato.
2. **F4c**: postura continua degli asset senza missione (D1.c), stessa procedura.
3. F5-F9 del piano (presenza e attese; fine missione e carburante nel tempo; bersagli e filtro armi A4 + salva su
   area con proposta separata; sessione e campagna con ricerca sui tempi di turnaround; manuale).
4. Piccoli punti aperti dal manuale: docstring obsoleti in `Session_Simulator`; `run_session` non inoltra
   `rwr_catalogue`; manca lo stato di missione "in corso"; etichette con maiuscole incoerenti in
   `evaluateGroundCriticality` (`attack`/`maintain`/`Defense`/`retreat`).
5. Attività precedenti ancora valide (da [[project-session-2026-09-30-summary]]): rotte → modulo mappe
   (`.docx` mappe non letto), residui volumi D-4b/c, D-5 opz.2, D-7, D-8; Fase 0 gerarchia C2; D9 morale;
   bug noti `get_blocks_by_criteria`, `Military.is_helibase` mancante.

## Lezioni della sessione
- Il tool Read non apre il manuale DCS e `pdftoppm` non c'è: rendere le pagine in PNG con pymupdf
  (`~/.claude/skills/pdf-to-markdown/.venv/bin/python3`) e passarle agli agenti; al primo giro gli agenti
  avevano guardato le figure solo a campione.
- Docling perde righe su tabelle lunghe (beacon): usare `page.find_tables()` di pymupdf.
- Agenti in parallelo sullo stesso checkout: dare un CONTRATTO di nomi esatto a chi produce e a chi consuma;
  catturare la fotografia su una copia `git archive` di HEAD con PYTHONPATH sovrascritto (aggira
  [[project-worktree-pythonpath-test-gotcha]]); verificare sempre io suite e confronto prima del commit.
- Quando l'utente contesta una deduzione dal manuale DCS 2020, verificarla su un `.miz` reale: il manuale è
  superato su alcuni punti.
- Un agente interrotto da un limite API si riprende con SendMessage (conserva il contesto): così è stato
  completato il manuale.
