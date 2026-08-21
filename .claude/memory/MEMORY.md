# Warfare-Model Project Memory

## Project & environment
- [Key modules & paths](project_key_modules.md) — root/paths, Vehicle_Data/Ground_Weapon_Data overview, known bugs, PDF/test inventory
- [Dev environment & machines](project_dev_environment.md) — 3 machines, git remote, memory sync workflow
- [Python venv per machine](feedback_venv.md) — always use the machine-specific interpreter path, never bare `python3`

## Module audit (completed 2026-08-16) — Fase 1 fully done 2026-08-21
- [Module audit — read this first for project status](project_module_audit.md) — ALL 17 remaining test errors resolved 2026-08-21; suite is 2315 tests/0 errors/0 failures; Fase 2 now 8 of 9 design decisions open (was 9)
- [Test_Air_Route_Manager mismatches — RESOLVED](project_test_air_route_manager_mismatches.md) — fixed 2026-08-21 (commit 9460733c); 48/48 green
- [Fase 2 design decisions — IN PROGRESS](project_fase2_design_decisions.md) — user answering the 9 open decisions from 00_Sintesi.md incrementally; 1-5 answered 2026-08-21 (verified against code, one correction on decision 3), 6-9 still open

## Next session — first task
- [Analysis/ Obsidian decision — RESOLVED](project_analysis_symlink_decision.md) — Option C chosen: Obsidian installed natively on ProArt P16 (WSL2); still needs installing on VM/Notebook too
- [WIKI_LLM_SIMULATION merged into Analysis/](project_wiki_llm_simulation_merge.md) — moved 2026-08-20, fully complete (old GitHub repo deleted, confirmed)
- [Rinomina_Campaign_State.py — reserved, do not delete](project_rinomina_campaign_state.md) — looks dead but user will reuse/rename it later

## Subsystem facts
- [Aircraft_Data / Aircraft_Loadouts facts](project_aircraft_data_facts.md) — API, scoring quirks, known bugs (BUG BLA3), logger mocking
- [Ship_Weapon_Data scoring](project_ship_weapon_scoring.md) — accuracy×destroy_capacity principle, corrected templates
- [Air_Resources_Assigner (ex Military_Resources_Assigner)](project_mra_state.md) — get_aircraft_mission, directive weights, derating formula
- [Campaign_State & Target_Status_History](project_campaign_persistence.md) — snapshot/persistence API facts
- [Mobile/Military 2026-05-22 update](project_asset_military_2026_05_22.md) — combat_range, air_defense_volume, combat_state, Region metric helper pattern
- [2026-05-05 refactor session](project_session_2026_05_05.md) — Block/Asset/Military/Region bug fixes, circular import discovery
- [UML generation workflow](project_uml_generation.md) — PlantUML tool, folder structure, diagram types already documented

## Feedback (how to work in this repo)
- [Test base class pattern](feedback_test_base_class.md) — test base classes must NOT inherit from unittest.TestCase
- [Circular import workaround](feedback_circular_import_workaround.md) — stub-class and sys.modules pre-injection patterns for Aircraft/Vehicle/Ship
- [Test patterns & conventions](feedback_test_patterns.md) — logger mocking, patch timing, CLI flags, import-path convention
