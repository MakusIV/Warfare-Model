# Rapporto FP blocco 2 — oc-developer

- **Agente / modello**: `oc-developer` / `openrouter/deepseek/deepseek-v4-pro-0813`
- **Branch**: `ai/oc-fp` · **piano eseguito**: `Analysis/Document/Proposta_Finestre_Per_Passaggio_Portata_Propria.md` (§4.2, blocco 2)
- **Data**: 2026-11-11

## 1. Esito in una riga
Completato: scenario S33-PASSES (13 test, 20 esecuzioni nuove) e riga/`UNITS` + docstring in `Scenario_Baseline.py`,
come da §4.2. Tutti i test mirati verdi.

## 2. File toccati
| File | Cosa e' cambiato |
|---|---|
| `Code/Dynamic_War_Manager/Source/Test/Test_Session_Scenarios_S33.py` | NUOVO: classe `TestS33DetectionPerPass` (13 test), costanti, `build_cas`, `run_variant`, aiuti `_zsu`/`_first_zsu`. |
| `Code/Dynamic_War_Manager/Source/Test/Scenario_Baseline.py` | In coda a `UNITS` (dopo `S34-BAND`) la tupla `S33-PASSES`; nuova sezione docstring "## Rilevamento per passaggio dopo la FP" fra VA e "## Uso". |

Il motore (`Logic/`), `Session_Simulator.py`, `Test_Session_Scenarios_S32.py`, la Proposta e il manuale NON sono
stati toccati (blocco 1 gia' mergiato).

## 3. Scostamenti dal piano
Nessuno. Tutte le asserzioni di §4.2.1 riprodotte alla lettera (nomi, ordine, semi, soglie, tolleranze). Premesse del
test 12 (g = 1) e dei test 1/7 (due passaggi) confermate senza bisogno di interventi sulla rotta o su `ZSU_DWELL_S`.

## 4. Scelte minori prese (§4.6)
- `run_variant` restituisce la terna `(outcome, results, pass_streams)` (non la coppia di S32): `results` e
  `pass_streams` liste allineate delle sole coppie con risultato non None; lo snapshot `copy.deepcopy(kwargs.get('pass_rng'))`
  si prende PRIMA della chiamata all'originale.
- `_zsu` / `_first_zsu` come funzioni di modulo (non metodi): `_first_zsu(results, cas)` restituisce le `Detection` della
  ZSU su `cas` nel primo `EngagementResult` che ne contiene almeno una (lista vuota se nessuno).
- `probe` del test 13 e' una closure locale che registra la terna `(FP_PER_PASS_DETECTION, D5_DWELL_TIME,
  detection_dwell_time('air') della ZSU)` e solleva `RuntimeError`.
- `_assert_launch_covered(seed, result, salvo)` condivisa dai test 4 e 11; `_hdist(a, b)` (distanza orizzontale su
  `position.x`/`position.y`) per il test 6; il punto di partenza degli A-10C si legge da `asset.position`, i punti di
  `CAS_ROUTE` si traslano con `dy = 500 * indice` come prescritto.

## 5. Costanti stimate
- `ZSU_DWELL_S = 2.0` (s): STIMA [S] dell'utente (2026-11-08, osservatore umano piu' ottica), NON un dato; dichiarata
  come tale nel commento del codice e nel docstring del modulo. La soglia `> 60.0` del test 7 e' una soglia del test,
  dichiarata nel docstring della funzione.

## 6. Verifiche eseguite
- `Test_Session_Scenarios_S33` (dalla root, `.direnv/python-3.12/bin/python3 -m unittest ...`):
  `Ran 13 tests` · `OK` (10.458 s).
- `Test_Session_Scenarios_S32` (modulo vicino, sola lettura): `Ran 6 tests` · `OK` (5.987 s).
- `Test_Session_Simulator` (modulo vicino, sola lettura): `Ran 170 tests` · `OK` (5.002 s).

Non eseguiti da me (spettano alla sessione principale): la suite completa e il confronto con la fotografia
(`bash tools/ai/verifica.sh`), l'esecuzione delle 20 esecuzioni nuove nella fotografia (`Scenario_Baseline`) e la
cattura di base.

## 7. Limiti noti e dubbi per la sessione principale
- `ZSU_DWELL_S` resta una stima, non un dato tarato (come prescritto dal piano).
- La fotografia e' la verifica numerica attesa dal §4.2.4 (suite `Ran B_FP + 43`, confronto `104 difference lines`
  di cui 20 nuove S33-PASSES): da confermare da parte del principale.

## 8. Stato git
```
 M Code/Dynamic_War_Manager/Source/Test/Scenario_Baseline.py
?? Code/Dynamic_War_Manager/Source/Test/Test_Session_Scenarios_S33.py
```
(gli altri file non tracciati in `Analysis/WIKI_LLM_SIMULATION/RAW/Logistica/` non sono di mia competenza e non sono
stati aggiunti.)