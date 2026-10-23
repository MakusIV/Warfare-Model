# Rapporto F8c1 — oc-developer

- **Agente / modello**: `oc-developer` / `openrouter/deepseek/deepseek-v4-pro-0813`
- **Branch**: `ai/oc-f8c1` · **piano eseguito**: `Analysis/Document/Proposta_F8_Sessione_Campagna.md`
- **Compito**: BLOCCO 1 di F8c — tabelle in `Context.py` e `Logic/Readiness.py` (§4.4, righe 701-795; vincoli comuni §4.6, righe 916-935; dei test solo `Test_Readiness.py` e `Test_Context.py`, righe 880-898).
- **Data**: 2026-10-23

## 1. Esito in una riga
Completato: blocco 1 di F8c implementato, test mirati verdi (276 test: `Test_Readiness`, `Test_Context`, `Test_Campaign_Types`). Blocchi 2 e 3 (Session_Campaign, Campaign_State, S30) NON realizzati, come da compito; suite e confronto NON eseguiti (li lancia la sessione principale).

## 2. File toccati

| File | Cosa e' cambiato |
|---|---|
| `Code/Dynamic_War_Manager/Source/Context/Context.py` | Aggiunte le 5 tabelle di prontezza dopo `AIR_MILITARY_CRAFT_ASSET`: `AIR_TURNAROUND_S`, `AIR_TURNAROUND_DEFAULT_S`, `GROUND_TURNAROUND_S`, `SEA_TURNAROUND_S`, `REPAIR_TIME_FULL_S` (STIME, §4.4). |
| `Code/Dynamic_War_Manager/Source/Logic/Readiness.py` | NUOVO: `asset_domain`, `turnaround_class`, `turnaround_s`, `repair_s`, `readiness_after_session`, `record_session`, `apply_campaign_processes`, `_rearm_and_refuel`, `ready_assets` (piu' gli helper privati `_class_value`, `_mission_assets`, `_asset_outcomes`, `_last_damage_times`, `_domain_id`). |
| `Code/Dynamic_War_Manager/Source/Test/Test_Readiness.py` | NUOVO: 32 test per le funzioni di `Readiness` (domini, classi, turnaround, riparazione, `readiness_after_session` sui casi 1-6 della regola, `record_session`, `apply_campaign_processes` con riarmo/rifornimento/idempotenza, `ready_assets`). |
| `Code/Dynamic_War_Manager/Source/Test/Test_Context.py` | Aggiunto import delle 5 tabelle e classe `TestReadinessTables` (3 test: copertura di `AIR_TURNAROUND_S`, valori > 0, chiavi di `REPAIR_TIME_FULL_S`). |

## 3. Scostamenti dal piano
Nessuno. Le firme e la regola di `readiness_after_session` seguono §4.4 riga-per-riga; F8a (`Campaign_Types.py`, `Session_Validator.py`) e F8b (`SessionOutcome` con `movement_ends`/`final_positions`) erano gia' nel branch e non sono stati riscritti. Fatto solo il blocco 1 richiesto.

## 4. Scelte minori prese
- **Asset reali nei test**: `Test_Readiness` usa `Scenario_Fixtures` (`make_aircraft`/`make_ship`/`make_vehicle`) con modelli gia' usati altrove (`F-16C Block 52d`, `BMP-2`, `USS Arleigh Burke IIa`); `asset_domain` e' cosi' provato su classi reali (`Aircraft`/`Ship`/`Vehicle`), coerentemente con `validate_class`.
- **Ramo "enum" di `turnaround_class`**: il setter `Asset.asset_type` converte l'enum in stringa, quindi per provare il ramo `.value` il test assegna `_asset_type` direttamente (bypass del setter). Documentato nel test.
- **`repair_s` con salute non leggibile** (None): dentro `readiness_after_session` viene trattata come "nessuna riparazione" (`repair = 0.0`); il piano non specificava questo caso.
- **Tolleranza `_TIME_EPS`**: importata una costante locale `1e-9` invece di importare `Contact_Scheduler.TIME_EPS` (il piano §4.6 non la elenca fra gli import di `Readiness`; evita di tirare dentro `Logic/Contact_Scheduler`).
- **`Aircraft_Data` import locale** dentro `turnaround_class`, come suggerito dal piano (memoria `feedback_circular_import_workaround`).
- **Classi base dei test** senza `unittest.TestCase`: `_Base` nei test usa `F.start_logger_patches()` (che salta i moduli senza `logger`, es. `Context.Doctrine`) piu' un patch dedicato di `Logic.Readiness.logger` per le asserzioni sui warning.

## 5. Costanti stimate
Tutte le 5 tabelle di `Context/Context.py` sono **STIME DI PROGETTO** (ordini di grandezza), dichiarate come tali nel commento della tabella e nei docstring di `Readiness` (da sostituire con la ricerca F8-R): `AIR_TURNAROUND_S` (7200-28800 s per classe), `AIR_TURNAROUND_DEFAULT_S` 9000 s, `GROUND_TURNAROUND_S` 21600 s, `SEA_TURNAROUND_S` 43200 s, `REPAIR_TIME_FULL_S` 86400/86400/259200 s per aria/terra/mare. Nessun'altra costante nuova.

## 6. Verifiche eseguite (solo test mirati, come da compito)
Non eseguiti `verifica.sh suite` ne' `confronto` (istruzione esplicita del compito: li lancia la sessione principale). Test mirati, interprete `python3`:

- `python3 -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Readiness` → `Ran 32 tests ... OK`
- `python3 -m unittest Code.Dynamic_War_Manager.Source.Test.Test_Context Code.Dynamic_War_Manager.Source.Test.Test_Campaign_Types` → `Ran 244 tests ... OK`
- conjunto dei tre → `Ran 276 tests ... OK`

Atteso dal piano per il blocco 1 (§4.4/§4.6): funzioni di prontezza pure + tabella `Context`; nessun cambio del motore (`run_session` intatto), quindi nessun effetto sulla fotografia (verifica della sola fotografia: non pertinente al blocco 1, che non tocca l'esecutore).

## 7. Limiti noti e dubbi per la sessione principale
- Il blocco 1 e' isolato: `Readiness` non ha ancora chiamanti di produzione (`Session_Campaign` e `Campaign_State` arrivano con i blocchi 2/3). Le funzioni sono esercitate solo dai test.
- `repair_s`/`turnaround_s` dipendono dalle classi reali degli asset (`validate_class`): un asset costruito con uno stub generico che non si chiami `Aircraft`/`Ship` ricade in "ground" (comportamento speculare a `continuous_posture`).
- Rumore di log residuo in `Test_Readiness` (WARNING di `Asset.Aircraft_Weapon_Data` durante la costruzione dell'aereo con loadout): pre-esistente, non silenziato da `Scenario_Fixtures.LOGGER_TARGETS`, non tocca gli esiti.

## 8. Stato git
```
 M Code/Dynamic_War_Manager/Source/Context/Context.py
 M Code/Dynamic_War_Manager/Source/Test/Test_Context.py
?? Code/Dynamic_War_Manager/Source/Logic/Readiness.py
?? Code/Dynamic_War_Manager/Source/Test/Test_Readiness.py
?? Analysis/Document/Rapporti/Rapporto_F8c1_oc-developer.md
```
Nota: presenti in working tree anche `Analysis/Document/.Proposta_F8_Sessione_Campagna.md.swp` (swap file di un editor) e `Untitled 1.odt` (file non mio): **NON** aggiunti al commit (mai `git add -A`/`git add .`).