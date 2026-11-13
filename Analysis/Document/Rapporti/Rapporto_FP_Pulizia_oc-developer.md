# Rapporto FP_Pulizia — oc-developer

- **Agente / modello**: `oc-developer` / `openrouter/deepseek/deepseek-v4-pro`
- **Branch**: `ai/oc-fp-pulizia` · **piano eseguito**: `Analysis/Document/Proposta_FP_Pulizia_Interruttore.md`
- **Data**: 2026-11-12

## 1. Esito in una riga

Completato: pulizia dell'interruttore `FP_PER_PASS_DETECTION` in quattro blocchi (A, B, C1, C2), ciascuno
con la suite del modulo verde. Il blocco C2 (soli testi) e' stato completato in **due sessioni**: la prima si
e' interrotta dopo avere applicato le modifiche ai testi (non committate); questa sessione le ha verificate,
eseguito i test mirati, scritto il rapporto e committato.

## 2. File toccati

| File | Cosa e' cambiato |
|---|---|
| `Code/Dynamic_War_Manager/Source/Test/Test_Session_Scenarios_S33.py` | Blocco A: varianti `off`/`cas_off` tolte (13 -> 11 test), nessun patch dell'interruttore, `run_variant` salva `(engagement, pass_rng)` con `deepcopy`. |
| `Code/Dynamic_War_Manager/Source/Test/Scenario_Baseline.py` | Blocco A: unita' S33-PASSES a 2 varianti (`_by_occurrence('on', 'cas_on')`); Blocco C2: docstring senza riferimento alla costante. |
| `Code/Dynamic_War_Manager/Source/Logic/Session_Simulator.py` | Blocco B: `engage` passa sempre `pass_rng` (tolto `if ER.FP_PER_PASS_DETECTION:`), docstring e commento `PASS_EVENT_TAG` aggiornati. |
| `Code/Dynamic_War_Manager/Source/Test/Test_Session_Simulator.py` | Blocco B: classe rinominata `TestPerPassDetectionStream`, tolto il test dello stato spento, liste di chiavi/stream aggiornate (169 test). |
| `Code/Dynamic_War_Manager/Source/Logic/Engagement_Resolver.py` | Blocco C1: costante e ramo "spento" tolti, `ValueError` per direzione a >= 2 passaggi senza `pass_rng`, `_exposure_time` ridotta al ripiego senza tratti, `at` obbligatorio in `_detection_time_of`; Blocco C2: docstring e commenti senza riferimenti all'interruttore. |
| `Code/Dynamic_War_Manager/Source/Test/Test_Engagement_Resolver.py` | Blocco C1: test 1 e 23 tolti, test 2/14 riscritti, classe/docstring aggiornate (373 -> 371 test); Blocco C2: commento "Geometria comune" aggiornato. |
| `Code/Dynamic_War_Manager/Source/Test/Test_Session_Scenarios_S26.py` | Blocco C2: sola docstring (nessun patch dell'interruttore). |
| `Code/Dynamic_War_Manager/Source/Test/Test_Session_Scenarios_S32.py` | Blocco C2: sola docstring (`_exposure_time` -> permanenza del passaggio in `_detect_direction`). |

## 3. Scostamenti dal piano

Nessuno funzionale. Il commento "Geometria comune" in `Test_Engagement_Resolver.py` (~riga 3991) era stato
lasciato dal blocco C1 con i numeri dei vecchi test ("test 14/23 in TestDwellTimeInTheResolver", con 23 tolto e
14 rinominato con altra geometria): il piano (§4.4 punto 16) lo lasciava esplicitamente a C2, ed e' stato
aggiornato in C2 a "e di `test_exposure_without_a_pass_is_zero` in TestDwellTimeInTheResolver".

## 4. Scelte minori prese (§4.9)

- **Blocco A**: aiuto locale comune ai test S33 3 e 9 `_assert_first_passes_draw_from_the_engagement_stream(self, runs)`;
  nomi locali `engagement`/`pass_stream` (coppie della spia) e `streams` (lista ritornata da `run_variant`), `stream`
  per il `deepcopy` locale; testo esatto di docstring e commenti entro il contenuto del piano.
- **Blocco B**: testo esatto e a capo dei commenti e delle docstring entro il contenuto indicato; nessuna nuova
  variabile locale nei test.
- **Blocco C1**: docstring di `TestDetectionPerPass` su due righe (contenuto identico al piano); controllo di
  `pass_rng` in `_detect_passes` subito prima di `count = len(passes)`; variabili locali dei test (`rng`, `pass_rng`,
  `b1`) come da piano.
- **Blocco C2**: testo esatto di docstring e commenti entro il contenuto indicato; aggiornamento del commento
  "Geometria comune" (v. §3).

## 5. Costanti stimate

Nessuna introdotta da questo lavoro.

## 6. Verifiche eseguite (righe lette dagli output, interprete `.direnv/python-3.12/bin/python3`)

Blocco C2 (questa sessione):
- `py_compile` dei sei file (nessun errore).
- `grep -rn "FP_PER_PASS_DETECTION" Code --include=*.py` -> nessuna riga.
- `Test_Engagement_Resolver`: `Ran 371 tests` · `OK`
- `Test_Session_Simulator`: `Ran 169 tests` · `OK`
- `Test_Session_Scenarios_S33`: `Ran 11 tests` · `OK`
- `Test_Session_Scenarios_S26`: `Ran 16 tests` · `OK`
- `Test_Session_Scenarios_S32`: `Ran 6 tests` · `OK`

Blocchi precedenti (dai messaggi di commit, non rieseguiti qui):
- **A**: `Test_Session_Scenarios_S33` `Ran 11 OK`; `Test_Session_Scenarios_S32` `Ran 6 OK`; `Test_Session_Simulator`
  `Ran 170 OK`.
- **B**: `Test_Session_Simulator` `Ran 169 OK`; `Test_Session_Scenarios_S33` `Ran 11 OK`; `Test_Session_Scenarios_S26`
  `Ran 16 OK`; `Test_Session_Rng` `Ran 19 OK`.
- **C1**: `Test_Engagement_Resolver` `Ran 371 OK` (prima `Ran 373 OK`); `Test_Session_Simulator` `Ran 169 OK`;
  `Test_Session_Scenarios_S33` `Ran 11 OK`; `Test_Fire_Control` `Ran 111 OK`; `Test_Aircraft` `Ran 35 OK`;
  `Test_Mission_Adapter` `Ran 142 OK`; `Test_Session_Rng` `Ran 19 OK`; `Test_Session_Types` `Ran 44 OK`;
  `Test_Session_Scenarios_S32` `Ran 6 OK`.

## 7. Limiti noti e dubbi per la sessione principale

- **Suite completa** (`Ran 4914` attesa) e **confronto con la fotografia** (`UNCHANGED (1103)`, `compared 1103 runs:
  10 difference lines`): NON eseguiti dall'esecutore, spettano al principale con `tools/ai/verifica.sh` (§4.6).
- Le **10 `MISSING`** attese (`S33-PASSES/S33-PASSES-{0..4}/{off,cas_off}`): spettano al principale (verifica
  parziale/confronto, §4.6); sono l'esito atteso e non un errore.
- **Installazione della fotografia di 1103 esecuzioni**: solo l'utente (decisione U-3); l'esecutore non tocca
  `Test/baseline/scenario_baseline.json`.
- Il **blocco C2 e' stato completato in due sessioni**: la prima si e' interrotta dopo le modifiche ai testi
  (lasciate nel working tree, non committate); questa sessione le ha verificate e committate.
- Il test di tempo `TestS17HierarchicalScaleSweep.test_every_size_runs_within_a_loose_bound` puo' fallire per
  rumore della macchina, indipendente da questo lavoro.

## 8. Stato git

`git status --short`:
```
 M .claude/memory/project_session_2026_11_07_summary.md
 M Code/Dynamic_War_Manager/Source/Logic/Engagement_Resolver.py
 M Code/Dynamic_War_Manager/Source/Test/Scenario_Baseline.py
 M Code/Dynamic_War_Manager/Source/Test/Test_Engagement_Resolver.py
 M Code/Dynamic_War_Manager/Source/Test/Test_Session_Scenarios_S26.py
 M Code/Dynamic_War_Manager/Source/Test/Test_Session_Scenarios_S32.py
 M Code/Dynamic_War_Manager/Source/Test/Test_Session_Scenarios_S33.py
?? Analysis/WIKI_LLM_SIMULATION/RAW/Logistica/
```
(`.claude/memory/...` e `Analysis/WIKI_LLM_SIMULATION/RAW/Logistica/` non sono di questo lavoro e non sono stati committati.)

`git log --oneline -5`:
```
2c89ca88 Pulizia FP blocco C1: risolutore senza interruttore, ValueError con 2+ passaggi senza pass_rng (371 test)
0a82222b Pulizia FP blocco B: Session_Simulator passa sempre pass_rng (169 test)
90e99572 Pulizia FP blocco A: S33 senza varianti off/cas_off (11 test) e Scenario_Baseline
4b65f345 Proposta: pulizia dell'interruttore FP_PER_PASS_DETECTION (4 blocchi, des-planner)
d216de00 Test S17: limite di tempo da 60 a 120 s (stima, falsi rossi sulla VM osboxes)
```
