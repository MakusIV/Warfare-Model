---
name: project-session-2026-10-23-summary
description: "Sessione 2026-10-23 ProArt: F8c completa (3 blocchi oc-developer), fotografia 986, suite 4701; routing dei fornitori per costo in ai-multimodel (bin/oc), template di progetto, guida riscritta; costi reali F8c 0,48+0,28 $"
metadata:
  type: project
---
- **Fatto e verificato** (suite 4701 OK skipped 7; confronto 986 IDENTICHE; fotografia installata a **986** con l'approvazione dell'utente, commit `3fb25089`):
  F8c blocchi 1-3 (merge `87aa7dea`, `6d3497bc`, `398ae3ef`), S30-CAMPAIGN a 10 test (2 aggiunti dalla sessione principale: `ready_at` e posizione degli
  aerei), docstring S24 (F6-B3 chiusa), Piano (F8c, deviazione 25) e `F4_Differenze_Scenari.md` sezione F8, `testCalcFightResult` con seme fisso.
- **Costi reali** (Costi_Deleghe.md): F8c1 1,40 $ (Baidu a prezzo pieno), F8c2 0,4785 $ (StreamLake), F8c3 0,2789 $ (Baidu a prezzo ridotto). Prezzi e fornitori:
  v. [[project-opencode-costi-misurati]].
- **ai-multimodel** (pushato, commit fino a `2631689`): `bin/oc` rigenera ogni 30 min `~/.local/share/opencode/routing.local.json` (costo effettivo, tolleranza
  50%, fp4 solo in coda) e lo passa con `OPENCODE_CONFIG`; `scripts/nuovo_progetto.py` + `templates/codice/` (sei agenti, comandi, hook, verifica.sh);
  catalogo/whitelist con 0813; `docs/Guida_Uso_Agenti.md` riscritta come procedura; `01_verifica_opencode.sh` = 14 controlli. Warfare-Model non ha piu' il blocco
  `provider` in `opencode.json`. Da provare sulla VM osboxes (Python 3.10) dopo `git pull`.
- **F8-R**: ricerca fatta (`Analysis/Document/Ricerca_Turnaround_Riparazione.md`, 14 ricerche, 1 sola fonte verificata sulla pagina); proposti 6 cambi (Fighter/Fighter_Bomber/Attacker/default 10800, Bomber 16200, Awacs 43200), il resto resta STIMA; IN ATTESA di approvazione D1-D5 prima del commit di dati su Context.
- **Aperti**: F8-R (solo l'approvazione), F9 (manuale DES), F8d logistica (non fatta per scelta), dubbio memoria TASK 2 C2, `limit.context` OpenCode,
  provare `bin/oc` e `prezzi_fornitori.py` sulla VM, dopo i primi usi valutare la qualita' dei fornitori non provati (StreamLake unknown, Sail fp4).
- **Regole emerse**: `oc` si lancia dal repo (da `~` "Unexpected server error"); il compito lungo in `.ai-run/compito_<tema>.txt` e `oc run --command esegui "$(cat ...)" 2>&1 | tee .ai-run/<tema>_oc.log`;
  la sessione principale non tocca il working tree mentre l'esecutore lavora; verificare sempre fornitore/costo dal CSV Activity.
