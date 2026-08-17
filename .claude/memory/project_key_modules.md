---
name: project-key-modules
description: "Project root/paths, core Asset data modules overview, known Vehicle_Data bugs, PDF output inventory"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 54069b25-fc3b-495d-81bb-9efd11133381
  modified: 2026-08-16T16:07:09.788Z
---

## Project structure
- Root: `/home/marco/Sviluppo/Warfare-Model`
- Main source: `Code/Dynamic_War_Manager/Source/`
- Tests: `Code/Dynamic_War_Manager/Source/Test/`
- PDF output: `out/` (project root)
- Venv: see [[project_dev_environment]] (differs per machine)

## Key modules
- `Asset/Vehicle_Data.py` — `Vehicle_Data` dataclass, `VEHICLE` dict, `SCORES` tuple, `get_vehicle_data()`, `get_vehicle_scores()`
- `Asset/Ground_Weapon_Data.py` — `GROUND_WEAPONS`, `get_weapon_score()`, `get_weapon_score_target()`
- `Asset/Aircraft_Data.py`, `Aircraft_Weapon_Data.py`, `Aircraft_Loadouts.py` — see [[project_aircraft_data_facts]]
- `Context/Context.py` — `Ground_Vehicle_Asset_Type` enum, `BLOCK_ASSET_CATEGORY`

## Known data/bugs — Vehicle_Data.py
- `STAMPA=True` at module level runs table printing + PDF generation on import
- `get_vehicle_scores()` validation bug: `if scores and scores not in SCORES` fails for any usable input
- Vehicle model names use hyphens: "M1A2-Abrams", "Leopard-2A6M", "M2-Bradley" (not spaces)
- `Vehicle_Data._registry`: dict {model_str → Vehicle_Data}, populated at module load
- CATEGORY set: {'Tank','Armored','Motorized','Artillery_Fixed','Artillery_Semovent','SAM_Big','SAM_Medium','SAM_Small','EWR','AAA'}

## Test files inventory (as of 2026-06-28, see [[project_module_audit]] for current status)
- `Test_Vehicle_Data.py` — 117 tests + terminal/PDF tables
- `Test_Ground_Weapon_Data.py` — unit tests + PDF tables
- `Test_Aircraft_Weapon_Data.py` — unit tests
- `Test_Aircraft_Loadouts.py` — 178 tests (incl. Aircraft target type)
- `Test_Aircraft_Data.py` — 189 tests + terminal/PDF tables (incl. Aircraft target type)
- `Test_Military_Resources_Assigner.py` (now `Test_Air_Resources_Assigner.py`) — 70 tests, see [[project_mra_state]]

## PDF output files (in `out/`)
- `Vehicle_Scores.pdf` — all vehicle scores grouped by category (matplotlib, heatmap colors)
- `vehicle_weapon_score_tables.pdf` / `vehicle_weapon_score_target_tables.pdf` — weapon score(_target) per weapon type × vehicle category
- `ground_weapon_score_tables.pdf` / `ground_weapon_score_target_tables.pdf` — ground weapon scores
- `weapon_score_tables.pdf` / `weapon_score_target_tables.pdf` — aircraft weapon scores
- `loadout_eval_tables.pdf` / `loadout_target_eff_tables.pdf` — aircraft loadout tables
- `Aircraft_List_Strike_Red.pdf` / `Aircraft_List_Strike_Red_FighterBomber.pdf` — `get_list_of_aircrafts(Red, Strike, target_dist[, role])`
