# Rapporto PB blocco 1 — des-developer

- **Agente / modello**: `des-developer` / Claude Sonnet 5.5
- **Branch**: `ai/des-pd-bordo` · **piano eseguito**: `Analysis/Document/Proposta_Pd_Bordo_Portata.md` (§4.1 e test di §4.4: T1, T2, T3, T4; blocco 1 solo)
- **Data**: 2026-11-19

## 1. Esito in una riga
Completato, nessuno scostamento dal piano. Interruttore `PD_EDGE_RECALIBRATION` SPENTO di default; confronto con la fotografia da 1219: 1219 IDENTICHE (atteso).

## 2. File toccati
| File | Cosa e' cambiato |
|---|---|
| `Code/Dynamic_War_Manager/Source/Logic/Engagement_Resolver.py` | costanti `PD_EDGE_RECALIBRATION = False` e `PD_AT_ACQUISITION_RANGE_RECALIBRATED = 0.2` (STIMA) dopo `PD_AT_ACQUISITION_RANGE` (0.5 invariato, commento aggiornato); nuova funzione `pd_at_acquisition_range()` prima di `detection_probability`; `detection_probability` e `detection_radius` leggono `edge = pd_at_acquisition_range()`; docstring di `detection_probability`, `detection_radius`, `weather_detection_factor` e del modulo (punto 1 della catena) |
| `Code/Dynamic_War_Manager/Source/Test/Test_Engagement_Resolver.py` | T1: nuova classe `TestPdEdgeRecalibration` (10 test); T2: 8 test/docstring riscritti per leggere `ER.pd_at_acquisition_range()` o `ER.detection_probability(3000.0, 5000.0)` al posto di 0,5 / 0,9352 |
| `Code/Dynamic_War_Manager/Source/Test/Test_Air_Route_Manager.py` | T2 (commento e asserzione di `test_detection_metrics_hand_computed`); T3: `test_pd_edge_switch_follows_the_des_law` in `TestDetectionMetricsWithDwell` |
| `Code/Dynamic_War_Manager/Source/Test/Test_Session_Scenarios_S36.py` | T4: nuova classe `TestPdEdgeOnGraze` con `test_same_draws_lower_pd_and_no_new_detection` (fuori da `UNITS`) |
| `Analysis/Document/Rapporti/Rapporto_PB_blocco1_des-developer.md` | questo rapporto |

Non toccati: `Test/baseline/`, `Scenario_Baseline.py`, `Session_Simulator`, `Air_Route_Manager`, file del manuale.

## 3. Scostamenti dal piano
Nessuno. Il codice reale corrispondeva al piano (righe, firme, usi di `PD_AT_ACQUISITION_RANGE` solo in `Engagement_Resolver.py` e nei 2 test indicati). Numero di test nuovi: vedi sotto, il totale coincide con quello atteso (12).

## 4. Scelte minori prese
- Nomi T1: i 10 metodi seguono nomi e ordine della tabella di §4.4. Totale test nuovi = 10 + 1 + 1 = 12, verificato dalla suite (4961 -> 4973).
- Helper statico `_switch(value)` nella classe T1 (wrapper di `patch.object(ER, 'PD_EDGE_RECALIBRATION', value)`).
- Test 6 (T1): un'estrazione "fra v e 0,5" = `(v + 0.5) / 2`, come suggerito dal piano; il confronto fra stati e' dentro lo stesso test con stato spento esplicito.
- Test 7 (T1): la seconda asserzione usa `detection_radius(0.5 * (0.5 * v), 1000.0, factor=0.5) == 1000.0` (estrazione pari a meta' di `factor * v`).
- Test 8 (T1): ciclo con `subTest` sui tre valori non validi (1.0, -0.1, True), con interruttore acceso e costante ricalibrata sostituita.
- Test 9 e 10 (T1): un'esecuzione per stato in un ciclo `('off', False), ('on', True)`; le due `_Force` si ricostruiscono a ogni giro. In test 10 il raggio atteso e' letto dentro lo stato corrispondente.
- In `detection_radius` `edge` e' letto subito dopo `_check_factor` e prima del confronto `draw >= factor` (come indicato dal piano: "dopo `factor = _check_factor(...)`"); in `detection_probability` e' letto dopo il ritorno anticipato per `distance > sensor_range` (la funzione d'accesso non e' chiamata in quel caso).
- Docstring di `detection_radius`: aggiunta una frase che cita `pd_at_acquisition_range()` (il piano chiedeva "docstring come sopra").
- T4: asserzione aggiuntiva `assertIsNotNone(new.exposure_s)` (premessa che la legge D-5 sia applicata) e controllo `new.time >= old.time - 1e-9` solo se entrambi rilevati.
- Data nel commento della costante (decisione PB-2): `2026-11-19`.

## 5. Costanti stimate
- `PD_AT_ACQUISITION_RANGE_RECALIBRATED = 0.2` in `Logic/Engagement_Resolver.py`: STIMA DICHIARATA (decisione PB-2 dell'utente), nessuna fonte; centro dell'intervallo 0,1-0,3 indicato dall'utente. Dichiarata come stima nel commento del codice.
- `PD_AT_ACQUISITION_RANGE = 0.5`: invariata, gia' stima dichiarata (commento aggiornato con "senza fonte verificata").
- Nei test nessuna costante a mano nuova: i valori attesi si leggono da `ER`.

## 6. Verifiche eseguite
Interprete: `.direnv/python-3.12/bin/python3` (ProArt, stampato da `verifica.sh`).
- Test parziali, uno per volta:
  - `Test_Engagement_Resolver`: `Ran 381 tests` · `OK`
  - `Test_Air_Route_Manager`: `Ran 87 tests` · `OK`
  - `Test_Threat_AA_Factory`: `Ran 66 tests` · `OK`
  - `Test_Session_Scenarios_S36`: `Ran 30 tests` · `OK`
- Suite completa (`verifica.sh suite`): `Ran 4973 tests in 605.390s` · `OK (skipped=7)` · exit code 0 (4961 + 12 nuovi, come atteso).
- Confronto con la fotografia (`verifica.sh confronto`): `UNCHANGED (1219)` · `compared 1219 runs: IDENTICAL (513.8 s)` · exit code 0; `grep -E '^(CHANGED|NEW|MISSING)' .ai-run/confronto.log` = 0 righe. Esito atteso dal piano (§4.6, interruttore spento, fotografia da 1219): 1219 IDENTICHE, 0 CHANGED/NEW/MISSING. Coincide.
- Controllo extra (non nel piano, sola lettura, fuori dalla suite): S36-GRAZE con interruttore acceso, `casD0` seme `S36-GRAZE-0`: Pd 0,507 -> 0,211 (come nell'esempio di PB-1).

## 7. Limiti noti e dubbi per la sessione principale
- Interruttore SPENTO: nessun test di scenario del blocco 3 e' stato toccato (PB-6 e' del blocco 3); i 9 test di scenario che falliscono con l'interruttore acceso restano da trattare li'.
- Il confronto non esercita la metrica del pianificatore (R-5 del piano).
- Nessuna sonda con interruttore acceso e' stata eseguita (blocco 2, della sessione principale).
- Documenti di §4.7 (`F4_Differenze_Scenari.md`, `Piano_Implementazione_Missione.md`, manuale) non aggiornati: non erano nel perimetro di questo task (blocco 1 codice e test).

## 8. Stato git
Prima del commit: 4 file modificati (i 4 sopra) piu' il rapporto; `?? Analysis/WIKI_LLM_SIMULATION/RAW/Logistica/` e' preesistente e non e' mio. `git stash list` vuota. Il commit di questo rapporto e' sul branch `ai/des-pd-bordo` (v. sotto per l'hash).
