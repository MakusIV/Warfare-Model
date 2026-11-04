# Rapporto sensori A (D-4c, sensore visivo) — des-developer

- **Agente / modello**: `des-developer` / Claude Sonnet 5.5
- **Branch**: `ai/cc-sensori-a` · **piano eseguito**: `Analysis/Document/Proposta_Dati_Sensori_EWR_Visivo.md` (§4 Blocco A, decisioni 1-5 di §3.1)
- **Data**: 2026-11-04

## 1. Esito in una riga
Completato, nessuno scostamento dal piano. Suite 4727 OK (skipped 7); confronto 989 identiche + 20 nuove, 0 cambiate.

## 2. File toccati
| File | Cosa e' cambiato |
|---|---|
| `Code/Dynamic_War_Manager/Source/Asset/Vehicle_Data.py` | argomento `visual: Optional[Dict] = None` (ultimo) e `self.visual`; campo `visual` nei record `ZSU-57-2` e `M163-VADS` (commenti di fonte/stima come in A.1) |
| `Code/Dynamic_War_Manager/Source/Asset/Mobile.py` | commento di schema, `VISUAL_SENSOR`, `DETECTION_SENSORS = ("radar", "TVD", "visual")`, interruttore `D4C_VISUAL_SENSOR = True`, filtro in `detection_range` (letto a ogni chiamata), docstring |
| `Code/Dynamic_War_Manager/Source/Logic/Air_Route_Manager.py` | `EFFECTIVE_EARTH_RADIUS_FACTOR['visual'] = 1.0` + commento, ciclo `('radar', 'TVD', 'visual')` senza import di Mobile, docstring di `DetectionThreat` e `build_detection_threat` |
| `Code/Dynamic_War_Manager/Source/Test/Test_Mobile.py` | `_SensorRecord(visual=None)`, `Mobile_module`, classe `TestDetectionRangeVisualSensor` (test 1-5) |
| `Code/Dynamic_War_Manager/Source/Test/Test_Vehicle_Data.py` | classe `TestVisualSensorRecords` (test 6-9), import `copy` e `MTLB_data` |
| `Code/Dynamic_War_Manager/Source/Test/Test_Threat_AA_Factory.py` | test 10 sostituisce `test_systems_without_sensor_data_give_none`; test 11, 12 |
| `Code/Dynamic_War_Manager/Source/Test/Test_Session_Scenarios_S31.py` (nuovo) | `TestS31VisualSensorRanges` (13, fuori dalla fotografia) e `TestS31VisualSensor` (14-18) |
| `Code/Dynamic_War_Manager/Source/Test/Scenario_Baseline.py` | unita' `S31-VISUAL` in coda a `UNITS` e paragrafo "Sensore visivo dopo la D-4c" nel docstring |

La fotografia `Test/baseline/scenario_baseline.json` NON e' toccata.

## 3. Scostamenti dal piano
Nessuno.

## 4. Scelte minori prese
- In `Test_Mobile.py` e `Test_Threat_AA_Factory.py` il modulo dell'interruttore si ottiene con `sys.modules[Mobile.__module__]`, per patchare il modulo che contiene davvero `detection_range` (anche se Mobile e' raggiunto da un percorso di import diverso).
- `Test_Session_Scenarios_S31.py` ha un `build` e un `run_variant` locali (il piano prevede il `build` locale con la quota; `run_variant` locale perche' quello di S19AD chiama il suo `build`); da S19AD importa solo `DURATION, IFV_IDS, MAVERICK, OVERFLIGHT, VISUAL`. L'interruttore e' sostituito attorno a costruzione delle forze e sessione.
- Struttura: costanti `VARIANT_SPEC` (modello, quota, interruttore), helper `_defence_events` / `_defence_rounds` (colpi dell'asset `Red-Line/ad0`); i `subTest` usano il seme della lista, non `outcome.session_id`.
- Test 12: `DETECTION_SENSORS` importato in testa a `Test_Threat_AA_Factory.py` (il piano scrive `Mobile.DETECTION_SENSORS`, stessa cosa).
- Test 6-9: `_VISUAL_MODELS` come dizionario modello -> (tracking, engagement); test 9 con `copy.deepcopy(MTLB_data)`.

## 5. Costanti stimate
- `acquisition_range` aria 6 km di `visual` per ZSU-57-2 e M163-VADS: STIMA, confidenza bassa (Howell/DC-3 in scala, intervallo plausibile 3-8 km), dichiarata come stima nei commenti dei record.
- `EFFECTIVE_EARTH_RADIUS_FACTOR['visual'] = 1.0`: STIMA DICHIARATA nel commento (linea di vista geometrica come il TVD); con 6 km l'orizzonte non limita mai.
- `tracking_range` 5.5 / 5 e `engagement_range` 4 / 1.2: dati di fonte (confidenza media) come da piano; `multi_target_capacity` 1: dedotto.
- `D4C_VISUAL_SENSOR = True`: scelta di progetto (decisione 4).

## 6. Verifiche eseguite
- Test singoli: `Test_Mobile` Ran 208 OK; `Test_Vehicle_Data` Ran 168 OK; `Test_Threat_AA_Factory` Ran 58 OK; `Test_Session_Scenarios_S31` Ran 6 OK.
- Suite (`bash tools/ai/verifica.sh suite`): `ESITO suite: exit code 0 · interprete .direnv/python-3.12/bin/python3` · `Ran 4727 tests in 555.693s` · `OK (skipped=7)`. Atteso dal piano: 4727, OK, skipped 7. Coincide.
- Confronto (`confronto`): `UNCHANGED (989)`, `compared 1009 runs: 20 difference lines` (exit code 1 perche' le 20 nuove contano come differenze). Controllo diretto delle chiavi di `.ai-run/confronto_capture.json` contro la fotografia: 989 chiavi della fotografia tutte presenti e identiche (0 cambiate, 0 scomparse), 20 chiavi nuove, tutte `S31-VISUAL/S31-VISUAL-<0..3>/<zsu|zsu_off|vads_low|vads_low_off|vads_high>`. Coincide con l'atteso.
- Sonda S31 (sola lettura, fuori dalla fotografia), colpi della difesa sui 4 semi / perdite Blue: `zsu` [150,150,150,150] / 0; `zsu_off` 0; `vads_low` [700,650,700,700] / [0,1,1,0]; `vads_low_off` 0; `vads_high` 0. Diversi dai valori orientativi di E-3 (550 colpi e 1 perdita; 2650 e 2 perdite), ma le asserzioni 14-18 sono qualitative e passano.

## 7. Limiti noti e dubbi per la sessione principale
- Il confronto esce con exit code 1 per le 20 esecuzioni nuove: atteso, la fotografia non e' stata installata.
- Il sensore visivo non modella notte e meteo (limite dichiarato nei commenti dei record).
- Il test del piano `test_visual_does_not_enter_the_scores` verifica solo `_TVD_eval`/`_radar_eval` di ZSU e M163; la non-modifica del combat score del registro e' garantita dal fatto che le funzioni di score non leggono `visual`.
- I valori di E-3 (colpi/perdite) non sono riprodotti esattamente da S31 (geometria con 3 BMP-2 e `only_designated`, non quella emulata nella sonda): nessun ritocco fatto, come da piano.

## 8. Stato git
```
 M Code/Dynamic_War_Manager/Source/Asset/Mobile.py
 M Code/Dynamic_War_Manager/Source/Asset/Vehicle_Data.py
 M Code/Dynamic_War_Manager/Source/Logic/Air_Route_Manager.py
 M Code/Dynamic_War_Manager/Source/Test/Scenario_Baseline.py
 M Code/Dynamic_War_Manager/Source/Test/Test_Mobile.py
 M Code/Dynamic_War_Manager/Source/Test/Test_Threat_AA_Factory.py
 M Code/Dynamic_War_Manager/Source/Test/Test_Vehicle_Data.py
?? Code/Dynamic_War_Manager/Source/Test/Test_Session_Scenarios_S31.py
?? Analysis/Document/Rapporti/Rapporto_sensori_A_des-developer.md
```
Nessun commit (lo fa la sessione principale); `git stash list` vuota; ultimo commit del branch: `cb980bf8`.
