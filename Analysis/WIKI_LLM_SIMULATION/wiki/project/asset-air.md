---
title: "Asset — Aviazione"
type: project-module
tags: [package-python, warfare-model, dwm, architecture, asset, air]
created: 2026-09-18
updated: 2026-09-18
code_paths: [Code/Dynamic_War_Manager/Source/Asset/Aircraft.py, Code/Dynamic_War_Manager/Source/Asset/Aircraft_Data.py, Code/Dynamic_War_Manager/Source/Asset/Aircraft_Loadouts.py, Code/Dynamic_War_Manager/Source/Asset/Aircraft_Weapon_Data.py]
related_decisions: ["[[asset-type-vs-category]]", "[[combat-power-priority-redesign]]"]
related: ["[[asset-base]]", "[[asset-ground-naval]]"]
---

## Scopo

Il sottosistema Asset-Air modella i velivoli militari del Dynamic War Manager: dati tecnico/prestazionali (`Aircraft_Data`), loadout installabili e loro valutazione contro un target (`Aircraft_Loadouts`), catalogo armi aria-aria/aria-suolo (`Aircraft_Weapon_Data`), e la classe applicativa `Aircraft` (sottoclasse di `Mobile`, vedi [[asset-base]]). Alimenta gli algoritmi di assegnazione missione (`Air_Resources_Assigner`) e, tramite `Aircraft.air_combat_power()`, il calcolo di combat power per priorità strategiche/tattiche (`Region`/`Military`).

Questa pagina supersede, per lo stato attuale, `Analysis/Modules/01_Asset_Air.md` (audit one-shot del 2026-08-16, oggi in larga parte superato — vedi §Note, il drift è sostanziale).

## File e classi principali

| File | Righe | Contenuto principale |
|---|---|---|
| `Code/Dynamic_War_Manager/Source/Asset/Aircraft.py` | 223 | `class Aircraft(Mobile)` |
| `Code/Dynamic_War_Manager/Source/Asset/Aircraft_Data.py` | 3689 | `class Aircraft_Data` (registry), `AIRCRAFT`/`AIRCRAFT_PHYSICAL_CHARACTERISTICS`/`AIRCRAFT_TASK_BEST_SCORES` (dict punteggi), `get_aircraft_data/get_aircraft_scores/get_aircraft_combat_score/get_aircraft_physical_characteristics/get_aircraft_best_scores_per_task` |
| `Code/Dynamic_War_Manager/Source/Asset/Aircraft_Loadouts.py` | 4042 | `AIRCRAFT_LOADOUTS` (dati), `loadout_eval`, `loadout_target_effectiveness(_by_distribuition)`, `get_aircrafts_quantity`, `loadout_cost`, ecc. |
| `Code/Dynamic_War_Manager/Source/Asset/Aircraft_Weapon_Data.py` | 8142 | `AIR_WEAPONS` (dati), `WEAPON_PARAM`, `get_weapon_score(_target)`, `get_weapon_efficiency`, `is_weapon_introduced`, `get_weapon_cost` |

Test (eseguiti realmente il 2026-09-18, `unittest discover`): `Test_Aircraft.py` **10 test — OK**, `Test_Aircraft_Data.py` **230 test — OK (skipped=2)**, `Test_Aircraft_Loadouts.py` **178 test — OK**, `Test_Aircraft_Weapon_Data.py` **268 test — OK**. Totale 686 test, tutti verdi.

## Stato attuale

### Il ciclo di import è stato rotto — cambiamento più rilevante rispetto all'audit

L'audit 2026-08-16 documentava un import circolare bloccante (`Aircraft → Aircraft_Data → Aircraft_Loadouts → Aircraft_Weapon_Data → Aircraft`) che rendeva **l'intero sottosistema non importabile** in un processo Python pulito e i tre file di test falliti già in fase di import. Verificato oggi che **non è più così**:
- `Aircraft_Weapon_Data.py` non importa più `Aircraft` (l'import morto identificato dall'audit è stato rimosso).
- `Ground_Weapon_Data.py` (sottosistema terrestre, vedi [[asset-ground-naval]]) non importa più `Aircraft` — stessa causa, stessa correzione.
- `Aircraft.py` importa oggi `Aircraft_Data` in modo non circolare (`get_aircraft_data, get_aircraft_scores, get_aircraft_combat_score, get_aircraft_physical_characteristics`) e **usa** effettivamente questi simboli (a differenza di prima, quando l'import era morto).
- Risultato: tutti e quattro i file si importano puliti, tutti i test dedicati passano con esecuzione reale (non solo mock), l'intera suite Asset del progetto è verde (coerente con `[[project_fase2_recon_combat_power_plan]]`, 2516 test OK al 2026-09-16).

### Combat power aggregato e action-based (Fase 2, confermato in codice)

- `Aircraft_Data.combat_aggregate()` (riga 839): somma, per ogni `AIR_TASK`, il miglior `combat_score()` tra i loadout disponibili per quel task — usa sempre `combat_score()` (mai `combat_score_target_effectiveness()`, per costruzione indipendente dal bersaglio). `_build_combat_aggregates()` normalizza con compressione logaritmica (`log1p`) prima del min-max, popolando `AIRCRAFT[model]['combat aggregate']` (float in [0,1]) e `AIRCRAFT_TASK_BEST_SCORES[model]`.
- `get_aircraft_combat_score(model)` espone questo valore — equivalente aereo di `VEHICLE[model]['combat score']['global_score']`/`SHIP[model][...]`.
- `Aircraft.air_combat_power()` (nuovo rispetto all'audit): combina `get_aircraft_combat_score` con `Context.combat_power_from_score`/`AIR_COMBAT_EFFICACY` pesato per `self.asset_type` ed `efficiency`. `Aircraft.set_combat_power()` replica **lo stesso valore aggregato** su tutti i task di `ACTION_TASKS['air']` (i task aria — CAP/Intercept/Strike/... — sono ruoli di missione non mutuamente esclusivi, non posture tattiche come Attack/Defense di Vehicle/Ship: sommarli produrrebbe doppio conteggio). Comportamento verificato con test dedicati (`Test_Aircraft.py::test_set_combat_power_replicates_same_value_across_all_tasks`).
- `Aircraft_Data.best_loadout_against_target()`/`combat_aggregate_against_target()` (nuovi): equivalenti target-aware di `combat_aggregate()`, usano `combat_score_target_effectiveness_by_distribution` (nome in inglese corretto) pesando ogni combinazione (classificazione, dimensione) per la sua quota reale — a differenza del percorso legacy `loadout_target_effectiveness_by_distribuition` (nome con il typo italiano storico "distribuition", ancora in uso in `get_list_of_aircrafts`). **I due percorsi (nuovo `_distribution`/legacy `_distribuition`) coesistono nel codice attuale**, non unificati.

### Dimensione fisica per-modello (Fase 3-bis, confermato in codice)

`Aircraft_Data.__init__` richiede oggi `length/width/height` (metri, interi positivi, validati) oltre a `weight`; costruisce `self.physical_characteristics` (mirror di Vehicle/Ship). Popolato con **dati reali** per tutti i 66 modelli (ricerca web, commento inline `# metri...; ricerca 2026-09-16` su ciascuna riga dati). Tenuto in un dict globale separato `AIRCRAFT_PHYSICAL_CHARACTERISTICS` (non dentro `AIRCRAFT`, per non rompere l'assunzione "tutto float" del loop di stampa a fine file). `Aircraft.get_physical_characteristics()` (nuovo, mirror di `Ship.get_physical_characteristics()`) delega a `get_aircraft_physical_characteristics(model)`. Prima di questa fase, `Context.classify_asset_dimension` derivava la dimensione dell'Aircraft puramente da `asset_type` — oggi usa la stessa catena fisica di Vehicle/Ship/Structure.

Il campo `users` (per il filtro combat-power-estimation per-side, `[[combat-power-priority-redesign]]`) era già presente su `Aircraft_Data` prima di questa sessione (parametro obbligatorio del costruttore, non opzionale come su Vehicle/Ship).

### Bug confermati ancora presenti (letti nel codice HEAD, verificati anche a runtime dove indicato)

1. **`get_list_of_aircrafts` — `StopIteration` non gestita, invariato dall'audit** (`Aircraft_Data.py:1058`): la riga di `return sorted(...)` ricalcola il ranking da zero con `key=lambda x: x.combat_score(task, loadout=next(iter(self.get_loadouts(x.model, task))))` — se `get_loadouts` ritorna un dict vuoto per un velivolo senza loadout per quel `task`, `next(iter({}))` solleva `StopIteration`, non catturata (non è un frame di generatore, PEP 479 non si applica). Il loop precedente (righe 1029-1057), che pure calcola `aircraft_list['score']`/`['aircraft']` gestendo correttamente il caso "nessun loadout" con un `continue`, **non alimenta il valore di ritorno effettivo** — stesso "loop morto" già segnalato nell'audit 2026-08-16, tuttora presente. Corrisponde al fatto noto di memoria "BUG BLA3".
2. **`from venv import logger`** (`Aircraft_Loadouts.py:31`): ancora presente, invariato — non è il `Logger` di progetto ma il logger stdlib di `venv`; le chiamate `logger.info/warning` nel file non passano dalla configurazione di logging del progetto.
3. **Getter/setter morti in `Aircraft_Data`** (`engine`, `roles`, `cost`, `model`, `made`, righe ~94-116): definiti come metodi senza `@property`, permanentemente irraggiungibili perché mascherati dagli attributi di istanza omonimi assegnati in `__init__`. Invariato dall'audit, nessun impatto noto (mai chiamati come funzioni altrove).
4. **Print massivo su stdout ad ogni import** (`Aircraft_Data.py:3680-3683`, blocco `#TEST`): ancora presente, non protetto da alcun flag (a differenza di `Vehicle_Data.STAMPA = False`). Verificato con esecuzione reale: l'import stampa centinaia di righe (`"{model} {name}: {score:.2f}"` per ogni voce di `AIRCRAFT`).
5. **`Aircraft.loadAssetDataFromContext()`/`checkParam()` — bug pre-esistente, non corretto, fuori scope della normalizzazione `asset_type`/`category` del 2026-09-15** (`Aircraft.py:63-93`): `self.block.isMilitary()`/`isLogistic()` non esistono su `Block` (che espone solo `is_military()`/`is_logistic()` snake_case, vedi [[asset-base]]) → `AttributeError` certo se mai invocato con un `Block` reale; anche correggendo questo, `for k, v in asset_data[self.asset_type]:` itera un `dict` **flat** senza `.items()` (`AIR_MILITARY_CRAFT_ASSET` non è annidato come `GROUND_MILITARY_VEHICLE_ASSET`) → fallirebbe comunque nello spacchettamento. **Nessun test lo esercita** (`Test_Aircraft.py` non copre questi due metodi): bug dormiente, confermato ancora presente dalla memoria `[[project_vehicle_asset_type_category_conflict]]`.

### Bug storici confermati risolti (drift positivo rispetto all'audit)

- **`get_aircraft_scores()`**: la validazione rotta (`scores in SCORES` sempre falsa/crash con default `None`) è stata sostituita dal pattern corretto (`invalid = [s for s in scores if s not in SCORES]`, default `scores=None` → tutte le score) — identico al fix già presente in `Ship_Data.get_ship_scores`.
- **`combat_score_target_effectiveness` non normalizzato**: il fatto noto (F-14A Phoenix ~2.6, oltre [0,1]) riguarda ancora `combat_score_eval`/`combat_score_target_effectiveness` (score "grezzo" usato per la scelta del loadout, mai preteso in [0,1] per design — v. `get_normalized_combat_score_target_effectiveness` per la versione normalizzata) — non è un bug, è distinto dal nuovo `combat_aggregate()` (quello sì normalizzato in [0,1] con compressione log).
- Nessuna traccia residua dell'import morto `Aircraft.py:4 → get_aircraft_data/get_aircraft_scores` non usati: oggi entrambi sono effettivamente usati (`get_aircraft_combat_score`, `get_aircraft_physical_characteristics` aggiunti all'import).

## Decisioni architetturali rilevanti

- [[asset-type-vs-category]] — `Aircraft.asset_type` = classe generale (`Air_Asset_Type`); `Aircraft` non ha una `category` granulare propria (a differenza di Vehicle). Nota: `Aircraft_Data.category` (il campo sul *modello* nel registro, non sull'istanza `Aircraft`) è invece una **lista** di `Air_Asset_Type` — un modello può comparire in più bucket (es. F-16A in `Fighter` e `Fighter_Bomber`); le proprietà booleane `isFighter`/`isBomber`/... su `Aircraft` leggono `self.asset_type` (singolo valore, dell'istanza), non `Aircraft_Data.category` (lista, del modello) — i due livelli non vanno confusi.
- [[combat-power-priority-redesign]] — `air_combat_power()`/`combat_aggregate()`/campo `users` sono i pezzi Aircraft di questa redesign (Fase 2/3-bis/4 di `[[project_fase2_recon_combat_power_plan]]`); `Context/Combat_Power_Estimation.py` (fuori da questo sottosistema) li consuma per la stima fog-of-war.

## Note

- **Drift maggiore rispetto all'audit 2026-08-16**: quell'audit descriveva il sottosistema come **non importabile in nessuna combinazione** e tutti i test bloccati all'import (0 test eseguibili su 655 metodi `test_*` presenti nel sorgente). Oggi il ciclo è rotto, tutti i 686 test attuali passano con esecuzione reale. Il numero di test è cresciuto (686 vs le 655 stimate) sia per correzioni sia per l'aggiunta di `Test_Aircraft.py` (10 test, prima inesistente) e nuovi test per `combat_aggregate`/`air_combat_power`/dimensione fisica.
- Fatti da `[[project_aircraft_data_facts]]` confermati tuttora validi: `get_weapon_score_target`/liste obbligatorie (non stringhe), `AIRCRAFT_ROLE = [e.value for e in Air_Asset_Type]`, logger mocking per i test di `Aircraft_Weapon_Data`.
- La normalizzazione `asset_type`/`category` (2026-09-15, [[project_vehicle_asset_type_category_conflict]]) ha toccato `Aircraft.py` (proprietà booleane, `air_combat_power`, `loadAssetDataFromContext`) e `Context.classify_asset_dimension` (il ramo Aircraft leggeva erroneamente `category` invece di `asset_type` — corretto, poi reso obsoleto dalla dimensione fisica di Fase 3-bis che rimpiazza del tutto quel ramo).
