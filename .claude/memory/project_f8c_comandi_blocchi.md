---
name: project-f8c-comandi-blocchi
description: "F8c divisa in 3 blocchi per oc-developer (V4 Pro 0813, Baidu, steps 180): testi esatti dei comandi `oc run --command esegui`, branch, verifiche attese dopo ciascun blocco; da usare nella prossima sessione"
metadata:
  node_type: memory
  type: project
  originSessionId: 1d3b4d7d-48a4-4011-92a5-5c4578c21791
  modified: 2026-10-23T09:25:12.749Z
---

Premessa (2026-10-22): F8a e F8b fatte e verificate (v. [[project-opencode-costi-misurati]], [[project-session-2026-10-22-summary]]).
F8c e' il passo piu' grande: si divide in 3 blocchi, ciascuno con branch `ai/oc-f8c<N>` creato dalla sessione principale da `analysis/dce-dcs-persistence`
(`git switch -c ai/oc-f8c1`), sessione OpenCode NUOVA (contesto piccolo), verifica e merge prima del blocco successivo. I testi dei comandi li
definisce la sessione principale (l'utente li incolla): sotto i testi esatti. Righe di `Proposta_F8_Sessione_Campagna.md` valide al 2026-10-22
(controllare con `grep -n '^####' ...` se il file cambia). Modello e fornitore: da `.opencode/agents/oc-developer.md` (V4 Pro 0813, `order` baidu).

**STATO (2026-10-23, ProArt)**: blocco 1 FATTO e verificato (merge `87aa7dea`, branch `ai/oc-f8c1`, V4 Pro 0813 confermato da `oc export`, costo
dichiarato ~0,17 $; `Readiness.py` 343 righe aderente al piano, 276 test mirati OK rieseguiti dalla sessione principale; nessuna suite, motore
invariato). Nota: i comandi `oc run` vanno lanciati DAL REPO (da `~` dà "Unexpected server error": agenti/comandi di progetto non trovati).
BLOCCO 2 FATTO e verificato (merge sul branch di lavoro, 2026-10-23: 62 chiamate tutte StreamLake, 0,4785 $ reali; suite 4691, skipped 7, 1 fallimento INTERMITTENTE preesistente `Test_Tactical_Evaluation.testCalcFightResult`: `calcFightResult` usa `random` globale, ~0,68% per esecuzione, modulo non toccato, 32 OK rieseguito; da sistemare a parte con una decisione dell'utente: seme fisso o delta piu' largo). Resta il blocco 3 (S30; atteso 982 IDENTICHE + 4 NUOVE, fotografia NON installata senza approvazione). La config globale `ai-multimodel` e' indietro (whitelist senza 0813, niente `order` Baidu): da allineare se l'utente vuole.

**Blocco 1 — tabelle in `Context` e `Logic/Readiness.py`** (righe 701-795; vincoli comuni 916-935; test `Test_Readiness.py` e `Test_Context.py` dalle righe 880-898):
```bash
oc run --command esegui "Analysis/Document/Proposta_F8_Sessione_Campagna.md, LIMITATAMENTE al BLOCCO 1 di F8c: tabelle in Context.py e Logic/Readiness.py (§4.4, righe 701-795; vincoli comuni §4.6, righe 916-935; dei test solo Test_Readiness.py e Test_Context.py, righe 880-898). F8a e F8b sono gia' nel branch (Campaign_Types.py, Session_Validator.py, SessionOutcome con movement_ends e final_positions): non riscriverle. NON fare Session_Campaign.py, Campaign_State.py ne' lo scenario S30 (blocchi 2 e 3). Esegui SOLO i test mirati (Test_Readiness, Test_Context, Test_Campaign_Types). NON eseguire suite ne' confronto: li lancia la sessione principale. Scrivi subito dopo il primo blocco verde il rapporto Rapporto_F8c1_oc-developer.md e committa WIP; alla fine commit senza prefisso. git add dei soli file toccati, MAI 'git add -A' o 'git add .' (c'e' un file non tuo: Untitled 1.odt). Regola dei due fallimenti e disciplina dei costi del tuo agente."
```
Esito atteso: test mirati verdi; nessun cambio di motore. Verifica principale: solo i test mirati + `Test_Context` (nessuna suite).

**Blocco 2 — `Logic/Session_Campaign.py` e `Context/Campaign_State.py`** (righe 796-832; test `Test_Session_Campaign.py` e `Test_Campaign_State.py`, righe 880-898):
```bash
oc run --command esegui "Analysis/Document/Proposta_F8_Sessione_Campagna.md, LIMITATAMENTE al BLOCCO 2 di F8c: Logic/Session_Campaign.py (apply_final_positions, run_campaign_session) e Context/Campaign_State.py (restore_position, add_ledger/get_ledger) (§4.4, righe 796-832; test solo Test_Session_Campaign.py e Test_Campaign_State.py, righe 880-898). Il blocco 1 (Context tabelle, Readiness.py) e F8a/F8b sono gia' nel branch: non riscriverli. run_session va chiamata come attributo del modulo (SS.run_session), mai importata per nome. NON fare lo scenario S30 (blocco 3). Esegui SOLO i test mirati (Test_Session_Campaign, Test_Campaign_State, Test_Readiness). NON eseguire suite ne' confronto. Rapporto Rapporto_F8c2_oc-developer.md subito dopo il primo blocco verde, commit WIP, commit finale senza prefisso. git add mirato, MAI 'git add -A' o 'git add .' (file non tuo: Untitled 1.odt). Regola dei due fallimenti e disciplina dei costi del tuo agente."
```
Verifica principale: SUITE (22 min VM) perche' si tocca `Campaign_State` (confronto non necessario: `run_session` invariata).

**Blocco 3 — scenario S30-CAMPAIGN, `Scenario_Baseline.UNITS`, docstring** (righe 833-879; documenti da aggiornare solo i docstring di §4.8, righe 948-961):
```bash
oc run --command esegui "Analysis/Document/Proposta_F8_Sessione_Campagna.md, LIMITATAMENTE al BLOCCO 3 di F8c: scenario S30-CAMPAIGN in Test/Test_Session_Scenarios_S30.py con la sequenza a 4 sessioni e i test elencati (§4.4, righe 833-879), la riga in Scenario_Baseline.UNITS, e i soli ritocchi di docstring/commento di §4.8 (righe 948-961: Session_Types 'Cosa NON c'e'', Mission_Adapter, S11 in Test_Session_Scenarios_S10_S18.py, mini-campagna in Test_Session_Validation.py: solo testo). I blocchi 1 e 2 e F8a/F8b sono gia' nel branch. NON installare la fotografia (Test/baseline/scenario_baseline.json): la installa la sessione principale. Esegui SOLO i test mirati (Test_Session_Scenarios_S30 e quelli dei file di cui ritocchi il docstring). NON eseguire suite ne' confronto. Rapporto Rapporto_F8c3_oc-developer.md subito dopo il primo blocco verde, commit WIP, commit finale senza prefisso. Le scelte di dettaglio dello scenario (posizioni esatte, helper) sono tue: elencale nel rapporto. git add mirato, MAI 'git add -A' o 'git add .'. Regola dei due fallimenti e disciplina dei costi del tuo agente."
```
Verifica principale: SUITE + CONFRONTO; atteso 982 IDENTICHE + 4 NUOVE (`S30-CAMPAIGN/S30-CAMPAIGN-1..4`); la fotografia NON va installata (986) senza approvazione dell'utente.
Dopo il blocco 3: F6-B3 (una riga di docstring in `Test_Session_Scenarios_S24.py:357`, la fa la sessione principale), `F4_Differenze_Scenari.md` sezione F8, tabella §5 del Piano (F8b, F8c), deviazione 25.
Ricordare: far girare suite/confronto con lo script `verifica_seq.sh` in background (una notifica a fine): `bash tools/ai/verifica.sh suite start`, poi ciclo `wait` fino a ESITO, poi `confronto`; MAI in parallelo.
