# Warfare-Model Project Memory

## Start here
- [Session recap 2026-08-26 — read this first](project_session_2026_08_26_summary.md) — ProArt P16 verified sync with VM: pulled LoggerClass cwd fix + git-sync hook (5a417765), full suite reconfirmed 2315 tests/OK (skipped=5)/0 errors. Verification-only session, no new work. Natural next step is still Fase 3.
- [Session recap 2026-08-21](project_session_2026_08_21_summary.md) — WIKI merge, Test_Air_Route_Manager fully fixed, Fase 2 (all 9 design decisions) closed, DataType.Route/Edge/Waypoint made to actually work end-to-end.

## Project & environment
- [Key modules & paths](project_key_modules.md) — root/paths, Vehicle_Data/Ground_Weapon_Data overview, known bugs, PDF/test inventory
- [Dev environment & machines](project_dev_environment.md) — 3 machines, git remote, memory sync workflow; SessionStart hook (2026-08-25) reports if local is behind origin, no auto-pull
- [Python venv per machine](feedback_venv.md) — always use the machine-specific interpreter path, never bare `python3`

## Module audit (completed 2026-08-16) — Fase 1 fully done 2026-08-21
- [Module audit — read this first for project status](project_module_audit.md) — ALL 17 remaining test errors resolved 2026-08-21; suite is 2315 tests/0 errors/0 failures; Fase 2 now 8 of 9 design decisions open (was 9)
- [Test_Air_Route_Manager mismatches — RESOLVED](project_test_air_route_manager_mismatches.md) — fixed 2026-08-21 (commit 9460733c); 48/48 green
- [Fase 2 design decisions — ALL CLOSED](project_fase2_design_decisions.md) — 2026-08-21: 7 resolved-and-actioned (#1,2,3,4,5,8,9), 2 explicitly deferred (#6,#7). #3 (Route/Edge/Waypoint canonical: DataType wins for ground) required fixing ~10 mechanical bugs across Waypoint/Edge/Route/Military/Tactical_Evaluation to actually make DataType.Route constructible — verified end-to-end with real objects, full suite still 2315/0/0. 00_Sintesi.md updated in place with status markers. Ground_Route_Manager.py still needs to actually produce DataType.Route objects (Fase 3, not started).
- [LoggerClass/Utility.py cwd bug — FIXED 2026-08-25](project_loggerclass_cwd_fix.md) — was: resolved log dir as `os.getcwd()/logs`, crashed if cwd != repo root. Now anchored to `__file__`, pushed (9a7342a1). Also fixed, machine-local to `osboxes` only (not checked on VM/Notebook/ProArt P16): numpy2/matplotlib ABI conflict, and stale apt `python3-matplotlib`/`python-matplotlib-data` shadowing `mpl_toolkits`/Axes3D (both resolved).

## Standing reminders (no action needed unless relevant)
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
