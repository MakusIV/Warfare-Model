---
name: project-session-2026-10-13-summary
description: "Sessione 2026-10-13 (osboxes) CHIUSA: F6-B2 (bingo a priori + in volo) fatta, committata 6b1b7225 e pushata, suite 4224 OK; PENDENTI per l'utente: installazione baseline fotografia (+40 S26) e decisione S24-GLIDE; ripresa su ProArt P16"
metadata:
  node_type: memory
  type: project
  originSessionId: 72c24bcb-7eaf-4ade-9253-229c6c9710eb
  modified: 2026-10-13T13:51:46.399Z
---

**STATO AL 2026-10-13 (chiusura su osboxes, ripresa su ASUS ProArt P16)**: HEAD `6b1b7225` (F6-B2) su
`analysis/dce-dcs-persistence`, pushato. Suite 4224 OK (7 skipped), verificata da me. Ripresa: `git pull`, poi
interprete venv di QUELLA macchina (`.direnv/python-3.12/bin/python3`, v. [[feedback-venv]]). Suite ~17 min su osboxes
(8 su ProArt), confronto fotografia ~6 min, mai in parallelo. Su osboxes il venv non c'era: si usava `/usr/bin/python3`.

## F6-B2 FATTA (agente des-developer Opus medium, verificata da me)
- `Fuel_Model.BINGO_RESERVE = 0.10` del carico pieno (STIMA, unica per tutti gli aerei), `bingo_point`, `nearest_base`,
  `return_margin`. Validatore a priori `Mission_Adapter.check_mission_bingo` (ValueError con motivo; NON chiamato da
  `run_session`: strumento del pianificatore/validatore F8). Bingo in volo con interruttore `Session_Simulator.F6_BINGO`:
  rientro in linea retta 3D alla base amica piu' vicina, niente piu' salve, asset BINGO, missione ABORTED con
  `AbortReason.BINGO`. `EndCriteria.bingo=False` = nessun controllo e nessun rientro. Scenario S26 (40 esecuzioni, 7 test).
- `S24-GLIDE` dichiara `bingo=False` (altrimenti cambierebbero 24 esecuzioni: glide, no_base, off).
- Documentato in `F4_Differenze_Scenari.md` («F6 passo B2») e Piano §5 (deviazione 15).

## DA APPROVARE / CONTROLLARE DALL'UTENTE (riproporre ALL'INIZIO della prossima sessione)
1. **Installare la fotografia aggiornata**: `Test/baseline/scenario_baseline.json` NON e' stata aggiornata (il classificatore dei
   permessi ha negato la `cp` sovrascrivente). Va rigenerata con `Scenario_Baseline --capture` (762 esecuzioni = 722 invariate
   + 40 nuove S26-BINGO) e sostituita, poi commit. Il confronto atteso: 722 identiche e 40 differenze = solo nuove S26. La
   cattura di osboxes era in /tmp (non disponibile su ProArt). Il riepilogo `--summary` non elenca le 40: verificare che
   siano tutte S26 (`--only S26`).
2. **Decisione su S24-GLIDE col bingo di default** (fase F6-B3): raccomandazione = bingo di default; costo: accettare 24
   esecuzioni (`glide` postura parking_cold->destroyed, `no_base` istante evento 200->187,5 s, `off` off_scene->parking_cold)
   e riscrivere i test S24-GLIDE.
3. **Conferma scelte dell'agente**: validatore fuori da `run_session`; dal bingo l'aereo smette di sparare; base idonea =
   qualunque base amica; rientro rettilineo a quota 0; riserva 0,10 unica (STIMA).
4. Il file `Analysis/Document/Untitled 1.odt` non tracciato non e' del progetto (lasciato fuori dal commit).

## ATTIVITA' DA SVOLGERE (ordine)
1. Punti 1-2 qui sopra (fotografia, poi F6-B3 = S24-GLIDE con bingo di default; validatore a priori nel futuro validatore F8 e nel
   pianificatore C2; limiti: idoneita' base per tipo, riserva unica, bingo alla crociera, quota di rientro).
2. **F7** = filtro armi/bersagli per missione (A4) + salva su area (POINT/AREA per `target_destroyed`): PRIMA proposta separata
   all'utente (domanda Q3), poi implementazione.
3. **F8** = validatore di sessione, prontezza (turnaround, ricerca dedicata), posizione persistente (D1.d).
4. **F9** = manuale DES (`des-manual-writer`, Sonnet high): togliere «TOT comune» in `03_Strato0_Contratto_Porte.md` (:269, :283) e
   `10_Limiti_Estensioni_Divergenze.md` (:248, :596); documentare F5/F6 (presenza, postura, WAIT, ETA, carburante per tratto,
   criteri di fine attivita', stato missione unico, postura destroyed, bingo).
5. Rimandati dall'utente: raffinamento orbita e zone CAP DCE (deve rivedere codice DCE e .miz). Opzionale: test instabile
   `testCalcFightResult` (random non seminato).
6. Arretrato: Fase 0 gerarchia C2, rotte->modulo mappe, residui volumi, D9 morale, bug noti (v. [[project-session-2026-10-11-summary]]).

Procedura per ogni passo: brief a `des-developer` (proporre agente/modello/sforzo e attendere conferma), interruttore dedicato,
fotografia invariata finche' l'utente non accetta i cambi; io verifico (suite + `--compare`), poi AskUserQuestion, poi installo
baseline, aggiorno Piano §5 e memoria, commit e push. Un agente puo' risultare «in esecuzione» nella barra dopo il completamento:
controllare con ListAgents.
