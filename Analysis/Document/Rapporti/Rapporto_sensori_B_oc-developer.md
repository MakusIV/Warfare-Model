# Rapporto sensori B (D-4b, radar EWR) — oc-developer

- **Agente / modello**: `oc-developer` / `openrouter/deepseek/deepseek-v4-pro`
- **Branch**: `ai/oc-sensori-b` · **piano eseguito**: `Analysis/Document/Proposta_Dati_Sensori_EWR_Visivo.md` (§4 Blocco B, sezioni B.1-B.5, decisioni 6-17 di §3.1)
- **Data**: 2026-11-04

## 1. Esito in una riga
Completato, nessuno scostamento dal piano. Suite 4742 OK (skipped 7); confronto 1009 esecuzioni tutte identiche, 0 cambiate, 0 nuove.

## 2. File toccati
| File | Cosa e' cambiato |
|---|---|
| `Code/Dynamic_War_Manager/Source/Asset/Vehicle_Data.py` | costante `GLOBAL_COMBAT_SCORE_EXCLUDED_CATEGORIES`; `get_normalized_combat_score` (G2: esclusione EWR dalla popolazione globale + saturazione in [0,1] nel solo caso globale); funzione `_ewr_support_fields`; 8 record EWR (`SCR270_data`, `FuMG80_Freya_data`, `P12_Yenisei_data`, `P18_Terek_data`, `P37_Mech_data`, `Nebo_SV_1L13_data`, `Nebo_55Zh6_data`, `AN_TPS43_data`) e la loro registrazione in coda dopo `S300PS_data` |
| `Code/Dynamic_War_Manager/Source/Test/Test_EWR_Data.py` (nuovo) | classi `TestEWRRecords` (test 1-8), `TestEWRDoNotShiftTheCombatScores` (test 9-11), `TestEWRAsAssets` (test 12-15) |

La fotografia `Test/baseline/scenario_baseline.json` NON e' toccata.

## 3. Scostamenti dal piano
Nessuno.

## 4. Scelte minori prese
- Costanti del test in cima a `Test_EWR_Data.py`: `EWR_MODELS` (modello → km), `MULTI_TARGET`, `ACQUISITION_PROFILES`, `REFERENCE_QUOTAS`, invece di dizionari sparsi nei singoli test.
- Test 9: il record estremo `test-ewr-extreme` e' una `copy.deepcopy(P18_Terek_data)` con `acquisition_range` 10000 e `multi_target_capacity` 100, modificando `data['radar']['capabilities']['air'][1][...]`; rimosso in `finally`.
- Test 13: gli asset EWR sono costruiti con `F.make_vehicle` e aggiunti alla forza con `F.add_assets` (necessario: `make_vehicle` non inserisce l'asset in `force.assets`, e `air_detection_threats`/`air_defense_threats` scorrono `force.assets`).
- Test 15: sessione con `make_registry_fire_control()`, rotta CAS con bersaglio `F.group_target('Red-EWR')`, `duration=1800`, `thresholds=BOTH_HOLD` (importato da `Test_Session_Scenarios_S10_S18`), come la sonda E-4; nessuna asserzione sul numero di Maverick lanciati, solo "la sessione termina e l'EWR non spara mai".
- Nessuna unita' nuova in `Scenario_Baseline.py` (il blocco B non prevede fotografia nuova).

## 5. Costanti stimate
- `reliability` dei radar `{'mtbf': 45, 'mttr': 4}`: STIMA [S] generica del registro (decisione 12, scelta dell'utente, diversa dalla raccomandazione di ometterla); dichiarata nei commenti dei record. I dati di fonte (P-18 MTBF 140 h, 55Zh6 MTBCF >250 h) restano SOLO nel commento.
- Campi non-sensore in `_ewr_support_fields` (dimensioni, costo, autonomia, velocita', comunicazioni): TUTTI STIME DI SCHEMA [S], dichiarate nella docstring della funzione e nei commenti; nessun dato di fonte.
- `reliability` del `communication` `{'mtbf': 45, 'mttr': 3}`: [S] come i "generic comm model" del registro; non piu' necessaria a evitare la lista vuota di `_reliability_eval` (il radar ora ha `reliability`), resta per coerenza di schema.
- Altezza d'antenna EWR 20 m per i 7 record senza `antenna_height`: costante esistente `SENSOR_HEIGHT_EWR_M`; solo SCR-270 ha `antenna_height` 16,8 [D] da fonte.

## 6. Verifiche eseguite
- Test singoli: `Test_EWR_Data` Ran 15 OK; `Test_Vehicle_Data` + `Test_Air_Defense_Efficacy` + `Test_Combat_Power_Estimation` Ran 223 OK.
- Suite (`bash tools/ai/verifica.sh suite`): `ESITO suite: exit code 0 · interprete .direnv/python-3.12/bin/python3` · `Ran 4742 tests in 566.669s` · `OK (skipped=7)`. Atteso dal piano: 4742, OK, skipped 7. Coincide.
- Confronto (`bash tools/ai/verifica.sh confronto`): `ESITO confronto: exit code 0` · `UNCHANGED (1009)` · `compared 1009 runs: IDENTICAL (476.0 s)`. Atteso dal piano: 1009 tutte identiche, 0 cambiate, 0 nuove. Coincide (la reliability dei radar e l'esclusione EWR dal combat score non cambiano nessuna esecuzione).

## 7. Limiti noti e dubbi per la sessione principale
- Il DES non ha orizzonte radar: un EWR con R alla quota di crociera vede nel DES un aereo radente a tutta portata (limite §5.2.1 del piano); la curva di fonte e' conservata in `acquisition_profile` per la futura opzione (c).
- Gli RWR non identificano gli EWR (`sam_category` None): il flag `ewr` di `Aircraft_Rwr_Data` resta inutilizzato (limite §5.2.7).
- Con il blocco B si spostano gli score globali radar/weapon/reliability/availability dei record esistenti; oggi nessun consumatore (§1.4, §5.2.8). Il solo combat score globale resta invariato per costruzione (G2).
- Nessun cueing EWR→SAM (D-7 fuori scope).

## 8. Stato git
```
 M Code/Dynamic_War_Manager/Source/Asset/Vehicle_Data.py
?? Code/Dynamic_War_Manager/Source/Test/Test_EWR_Data.py
?? Analysis/Document/Rapporti/Rapporto_sensori_B_oc-developer.md
```
Ultimo commit del branch: `77143de5`; il blocco A e' il commit `37816355`.
