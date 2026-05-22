# Warfare-Model Project Memory

## Project Structure
- Root: `/home/marco/Sviluppo/Warfare-Model`
- Main source: `Code/Dynamic_War_Manager/Source/`
- Tests: `Code/Dynamic_War_Manager/Source/Test/`
- PDF output: `out/` (project root)
- Venv: `venv/` (activate with `source venv/bin/activate`)

## Key Modules
- `Asset/Vehicle_Data.py` — Vehicle_Data dataclass, VEHICLE dict, SCORES tuple, get_vehicle_data(), get_vehicle_scores()
- `Asset/Ground_Weapon_Data.py` — GROUND_WEAPONS, get_weapon_score(), get_weapon_score_target()
- `Asset/Aircraft_Data.py`, `Aircraft_Weapon_Data.py`, `Aircraft_Loadouts.py`
- `Context/Context.py` — Ground_Vehicle_Asset_Type enum, BLOCK_ASSET_CATEGORY

## Known Data / Bugs
- `Vehicle_Data.py`: `STAMPA=True` at module level runs table printing + PDF generation on import
- `get_vehicle_scores()` has a validation bug: `if scores and scores not in SCORES` fails for any usable input
- Vehicle model names use hyphens: "M1A2-Abrams", "Leopard-2A6M", "M2-Bradley" (not spaces)
- `Vehicle_Data._registry`: dict {model_str → Vehicle_Data}, populated at module load
- CATEGORY set: {'Tank','Armored','Motorized','Artillery_Fixed','Artillery_Semovent','SAM_Big','SAM_Medium','SAM_Small','EWR','AAA'}

## Test Files Created
- `Test/Test_Vehicle_Data.py` — 117 unit tests + terminal/PDF tables for Vehicle_Data
- `Test/Test_Ground_Weapon_Data.py` — unit tests + PDF tables for Ground_Weapon_Data
- `Test/Test_Aircraft_Weapon_Data.py` — unit tests for Aircraft_Weapon_Data
- `Test/Test_Aircraft_Loadouts.py` — 178 unit tests for Aircraft_Loadouts (incl. Aircraft target type)
- `Test/Test_Aircraft_Data.py` — 189 unit tests + terminal/PDF tables for Aircraft_Data (incl. Aircraft target type)
- `Test/Test_Military_Resources_Assigner.py` — 70 unit tests for Military_Resources_Assigner (all helpers + get_aircraft_mission)

## PDF Output Files (in `out/`)
- `Vehicle_Scores.pdf` — all vehicle scores grouped by category (matplotlib, heatmap colors)
- `vehicle_weapon_score_tables.pdf` — get_normalized_weapon_score() per weapon type × vehicle category
- `vehicle_weapon_score_target_tables.pdf` — get_normalized_weapon_target_effectiveness() per weapon type × category
- `ground_weapon_score_tables.pdf` / `ground_weapon_score_target_tables.pdf` — ground weapon scores
- `weapon_score_tables.pdf` / `weapon_score_target_tables.pdf` — aircraft weapon scores
- `loadout_eval_tables.pdf` / `loadout_target_eff_tables.pdf` — aircraft loadout tables
- `Aircraft_List_Strike_Red.pdf` — get_list_of_aircrafts(Red, Strike, target_dist)
- `Aircraft_List_Strike_Red_FighterBomber.pdf` — idem con role='Fighter_Bomber'

## Aircraft_Data Key Facts
- `combat_score(task, loadout)` — no target info; `combat_score_target_effectiveness(task, loadout, target_type: List, target_dimension: List)` — with target
- `get_normalized_intercept_speed_score(...)` — metodo di Aircraft_Data per scoring intercettazione
- `combat_score_target_effectiveness` is NOT bounded to [0,1] — loadout component alone can exceed 1 (e.g. F-14A Phoenix Fleet Defense returns ~2.6)
- `get_list_of_aircrafts(side, task, target_distribuition, role, route_length, route_speed)` — BUG BLA3: sorting key raises StopIteration per aircraft senza loadout del task (next(iter({})))
- `AIRCRAFT_ROLE = [e.value for e in Air_Asset_Type]` — lista di stringhe
- `Air_Asset_Type.FIGHTER_BOMBER.value = 'Fighter_Bomber'`
- Logger mock per Aircraft_Data richiede anche `Aircraft_Weapon_Data.logger` (ha `logger.debug` non implementato in Logger class)
- `get_weapon_score_target(model, target_type: List, target_dimension: List)` — vuole LISTE, non stringhe

## Military_Resources_Assigner Key Facts
- Module: `Logic/Military_Resources_Assigner.py`
- Public API: `get_aircraft_mission(task, aircraft_availability, mission_requirements, target_data, max_aircraft_for_mission, max_missions, directive)` → `{'fully_compliant': [...], 'derated': [...]}`
- Each entry: `{'aircraft_model': str, 'loadout': str, 'score': float}`, sorted descending by score
- `directive` values: `'performance_high'(1,0)`, `'performance'(0.75,0.25)`, `'balanced'(0.50,0.50)`, `'economy'(0.25,0.75)`, `'economy_high'(0.10,0.90)`
- `_REFERENCE_COST_K = 303_000.0` — normalisation constant for cost factor
- `_reduce_target_data`: with a single target, `weight=1.0` so `qty = round(qty*ratio*2)`; with ratio=0.5 quantity is unchanged (expected)
- `_check_mission_requirements`: `altitude_min` check is `lo_altitude_min <= req_altitude_min`
- Logger paths: `_LOGGER_MRA = "Code.Dynamic_War_Manager.Source.Logic.Military_Resources_Assigner.logger"` + _LOGGER_LO, _LOGGER_AWD, _LOGGER_AD

## Aircraft_Loadouts Key Facts
- `loadout_target_effectiveness_by_distribuition(aircraft, loadout_name, target_dist, route_length, route_speed)` — target_dist è dict {type: {perc_type, perc_dimension: {dim: pct}}}
- `get_aircrafts_quantity(aircraft_model)` e `loadout_cost(aircraft_model, loadout_name)` — disponibili in Aircraft_Loadouts
- Bug corretto: score accumulation usava `score *= perc_dimension` sul totale cumulativo; ora usa `dim_score` locale per ogni (type×dim)
- Bug corretto: `get_weapon_score_target` veniva chiamato con stringhe invece di liste → passare `[target_type]`, `[target_dimension]`
- Tu-160 Strategic Strike ora usa `Kh-101` (6+6); Tu-95MS Strategic Strike usa `Kh-55` (6)
- `Kh-55` e `Kh-101` aggiunti a MISSILES_ASM in `Aircraft_Weapon_Data.py` con efficiency per Soft/Armored/Hard/Structure/Air_Defense/infrastrutture

## Ship_Weapon_Data Key Facts
- `Asset/Ship_Weapon_Data.py` — SHIP_WEAPONS, template efficienza, get_weapon_score(), get_weapon_score_target(), get_weapon_score_target_distribuition()
- Principio scoring: score = accuracy × destroy_capacity; ordine atteso **Soft > Armored > ship > Structure > Hard**
- `accuracy` = specializzazione arma; `destroy_capacity` = fragilità bersaglio una volta colpito
- Template corretti (2026-04-02): ASM subsonic/supersonic/supersonic_heavy + tutti i GUNS + CIWS — vedi `project_ship_weapon_scoring.md`
- Run tests: `python -m unittest discover -s Code/Dynamic_War_Manager/Source/Test -p "Test_Ship_Weapon_Data.py"` (--tests-only NON implementato)

## Target_Status_History Key Facts
- Module: `Context/Target_Status_History.py` — class `TargetStatusHistory`
- Stores `get_recognition_report(region_c2_recon_efficiency=1.0)` snapshots per block per mission
- Represents blocks as military targets (NOT operational state); formerly `Campaign_History.py` / `CampaignHistory`
- `Block.get_status_report()` has been removed — callers use `get_recognition_report(region_c2_recon_efficiency=1.0)` directly
- Test: `Test/Test_Target_Status_History.py` — 44 tests OK

## Campaign_State Key Facts
- Module: `Context/Campaign_State.py` — class `CampaignState`
- Stores full campaign state snapshots (Region, Block, Asset, Route) indexed by mission_id
- Serializes: block class/name/side/priority, State (health, success_ratio), Resource_Manager (warehouse, actual_production, clients_ids, server_ids), all Asset payloads + model + class_name, Route edges (danger_level, speed)
- `restore(mission_id, regions)` applies snapshot to live objects: Region.attack_weight, BlockItem.priority, Block/Asset State.health, Payload fields, Route.Edge danger_level/speed
- Write API: `add_campaign_snapshot(atomic)`, `add_region_snapshot`, `add_block_snapshot` (granular)
- Read API: `get_mission`, `get_region_snapshot`, `get_block_snapshot`, `get_block_history`, `get_field_trend`, `get_asset_history`
- Persistence: `save(path)` / `CampaignState.load(path)` — JSON UTF-8
- Test: `Test/Test_Campaign_State.py` — 78 tests OK (stub objects, no live Asset imports)

## Mobile.py — New Methods (2026-05-22 update)
- `air_defense_volume() → Optional[Cylinder]` — Vehicle: checks AA_CANNONS + MISSILES with min/max_altitude; extra filter: if weapon has `task` field, must contain `'Anti_Air'`; Ship: MISSILES_SAM only; returns Cylinder or None
- `combat_range() → Optional[float]` — Vehicle types: CANNONS/ARTILLERY/MORTARS/ROCKETS/MISSILES/AUTO_CANNONS; Ship: MISSILES_ASM/MISSILES_TORPEDO/GUNS; two exclusion rules: (1) MISSILES with min_altitude (SAM), (2) any weapon whose task list contains `'Anti_Air'`; Ship ranges km→m
- `fire_range` property and getter/setter removed from Mobile (2026-05-22)
- `Ship.py`: added `model: Optional[str] = None` parameter → `self._model = model` (needed for Ship_Data._registry lookup)
- Ground_Weapon_Data: `min_altitude`/`max_altitude` (m AGL) added to all AA_CANNONS and SAM MISSILES; `task` field present on all ground weapons
- Ship_Weapon_Data GUNS: ALL have `task: ['Anti_Air', ...]` → excluded from combat_range; MISSILES_ASM/TORPEDO have no Anti_Air → included
- GROUND_WEAPON_TASK['Anti_Air'] = 'Anti_Air' (string); task field in weapon data is a list of strings

## Military.py — Updated Methods (2026-05-22)
- `_get_artillery_stats()` — now uses `asset.combat_range()` (not `artillery_range` attr); filters by category: Vehicle must be ARTILLERY_FIXED/ARTILLERY_SEMOVENT/TANK; Ship must be CORVETTE/CRUISER/DESTROYER/FRIGATE (all using `.value`); Bug fixed: was using `gat.TANK` / `sat.CORVETTE` etc without `.value` (enum vs string comparison always False)
- `air_defense_volume() → List[Cylinder]` — iterates all assets, filters by validate_class(Vehicle|Ship) + is_operative() + hasattr; calls asset.air_defense_volume(); collects non-None; returns list (empty if none)
- `combat_range() → Optional[Tuple[float,float,float,int]]` — (max_range, med_range, ratio, quantity); iterates all assets once; filters is_operative() + hasattr('combat_range'); excludes None returns; uses numpy.median; returns None if no ranges
- `combat_power()` line 207: guard `if hasattr(asset,'combat_power') and asset.is_operative()` — hasattr skips non-combat assets, is_operative() excludes damaged; mocks must set `is_operative.return_value` explicitly
- `combat_state() → Optional[float]` — formula: `(0.3 * operative_efficiency + 0.7 * c2_efficiency) * ratio_operative`; returns None if no assets; result ∈ [0,1]
- `get_c2_efficiency()`: hasattr(asset,'efficiency') + asset.is_operative() filters; non-operative C2 excluded

## Test Files — Current State (2026-05-22)
- `Test/Test_Block.py` — 95 tests OK
- `Test/Test_Asset.py` — 41 tests OK
- `Test/Test_Region.py` — 50 tests OK
- `Test/Test_Military.py` — 83 tests OK (incl. _get_artillery_stats category filter + combat_range + combat_state + c2_efficiency)
- `Test/Test_Mobile.py` — 54 tests OK (incl. task filter for air_defense_volume + combat_range; AUTO_CANNONS; GUNS Anti_Air exclusion)
- `Test/Test_Target_Status_History.py` — 44 tests OK
- `Test/Test_Campaign_State.py` — 78 tests OK

## Circular Import — Known Issue
- `Aircraft.py → Aircraft_Data → Aircraft_Loadouts → Aircraft_Weapon_Data → Aircraft.py` — unresolved
- Vehicle.py and Ship.py also trigger this chain (via Ground_Weapon_Data → Aircraft)
- **Cannot import Vehicle, Ship, Aircraft directly in any test file**
- Workaround in Test_Military: `_Vehicle = type('Vehicle', (), {})` stub + `mock.__class__ = _Vehicle`
- `validate_class(mock, "Vehicle")` uses MRO name → works with stubs
- `Block.assets` setter validates `isinstance(v, Asset)` → bypass with `block._assets = {...}` in tests

## Key Bug Fixes (2026-05-05)
- `Block.py`: removed unused `Vehicle`/`Ship`/`Aircraft` imports (broke all tests via circular import)
- `Asset.is_critical()`: `isCrytical()` → `isCritical()` (typo in State method name)
- `Military.get_recon_efficiency` and `get_c2_efficiency`: `asset.efficiency()` → `asset.efficiency` (property, not method call)
- `Military.get_recognition_report`: missing `return target_report` added
- `Block.get_recon_efficiency`: missing `return` statement added
- `Block.get_recognition_report`: `self.supply`/`self.communication` wrapped with `getattr(..., None)`

## Region.py — Metric Helper Pattern
- `_get_region_average_metric(side, category, method_name)` — central helper for all 5 metric functions
- Uses `getattr(block, method_name, None)` + `callable()` check → safe for non-existent methods
- `get_recon_reports(side)` calls `get_c2_efficiency` once (not per-block), passes value to each `block.get_recognition_report(c2_value)`

## Dev Environment & Memory Sync
- Two machines: **VM** (`/home/marco/Sviluppo/Warfare-Model`) and **Notebook**
- Git remote: `git@github.com:MakusIV/Warfare-Model.git` (SSH, non HTTPS)
- Memory lives in repo: `Warfare-Model/.claude/memory/` — tracked by git
- On VM: `~/.claude/projects/-home-marco-Sviluppo-Warfare-Model/memory/` → symlink to repo folder
- On Notebook: remote usa **HTTPS** (`https://github.com/MakusIV/Warfare-Model.git`), non SSH — la chiave `id_ed25519` è per uso personale ma ssh-add richiede passphrase interattiva; HTTPS è più pratico
- On Notebook (setup completato 2026-05-13): same symlink created after first `git pull`:
  ```bash
  rm -rf ~/.claude/projects/-home-marco-Sviluppo-Warfare-Model/memory
  ln -s ~/Sviluppo/Warfare-Model/.claude/memory ~/.claude/projects/-home-marco-Sviluppo-Warfare-Model/memory
  ```
- Sync workflow: `git push` at end of VM session → `git pull` on Notebook (and vice versa)

## Project Files
- [Military_Resources_Assigner — stato implementazione](project_mra_state.md) — formula _reduce_target_data, derating_factor, formato tabelle output
- [UML Generation Workflow](project_uml_generation.md) — PlantUML tool, struttura cartelle, tipi diagrammi, stile, moduli già documentati

## Feedback
- [Pattern mixin per test base class](feedback_test_base_class.md) — classi base test NON devono ereditare da unittest.TestCase
- [Usare venv per esecuzione Python](feedback_venv.md) — sempre `venv/bin/python3`, non python3 di sistema

## Test_Mobile.py — Import Strategy (circular import workaround)
- Pre-inject Aircraft chain into sys.modules as MagicMock before any import
- Fake Vehicle_Data module: `_vd_mod.Vehicle_Data = _FakeVehicleData` (class with `_registry = {}`)
- Fake Ground_Weapon_Data module: `_gwd_mod.GROUND_WEAPONS = _FAKE_GW` (mutable dict, mutated per test)
- Real Ship_Data and Ship_Weapon_Data imported directly (no circular deps)
- `_MobileStub`: class with `air_defense_volume = Mobile.air_defense_volume` and `combat_range = Mobile.combat_range`
- `assertIsInstance(cyl, Cylinder)` fails (dual module path) → use `type(cyl).__name__ == 'Cylinder'` instead
- Mock operative assets must set `is_operative.return_value` explicitly (MagicMock default is truthy but not False for damaged)

## Test Patterns
- Logger mock: `patch("Code.Dynamic_War_Manager.Source.Asset.XXX.logger", MagicMock())`
- Per combat score test: mock anche `Aircraft_Weapon_Data.logger` e `Aircraft_Loadouts.logger`
- Se mock serve dopo import: usare `p = patch(...); p.start()` invece di `with patch(...)`
- Menu: interactive (default), `--tests-only`, `--tables-only` flags
- PDF: matplotlib + PdfPages (one page per category), RdYlGn heatmap colormap
- Run tests: `python Code/Dynamic_War_Manager/Source/Test/Test_XXX.py --tests-only`
- `_all_loggers_mocked()` in Test_Aircraft_Data: mocka _LOGGER_PATH, _LOADOUTS_LOGGER_PATH, _GWD_LOGGER_PATH, _AWD_LOGGER_PATH
