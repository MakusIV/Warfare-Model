# Warfare-Model Project Memory

## Start here
- [Fase 2 (fog-of-war combat power) — 6-phase plan, ALL 7 Qs RESOLVED, Fase 1+2+3-bis IMPLEMENTED 2026-09-16](project_fase2_recon_combat_power_plan.md) — C2 observer fix, action-based combat power selection, AND real physical dimensions for all 65 Aircraft models (replacing role-based dimension) all done & tested (2476 OK); Fase 3 (Combat_Power_Estimation.py) onward not yet implemented
- [Session recap 2026-09-14](project_session_2026_09_14_summary.md) — producer-duplication refactor + get_target_report no-visibility fix shipped & pushed (commit 3fe680c4, 2465 tests OK); asset_type/category conflict and no-visibility-priority policy decided but not implemented, see linked memories
- [Region/Military combat-power & priority-calc redesign — IN PROGRESS](project_priority_calc_combat_power_redesign.md) — 2026-09-11: Fase 0+1 done (full suite 2332 OK/5 skipped) — Vehicle/Ship/Aircraft combat power all working for real; mil_category priority-list split implemented 2026-09-14 (commit 3fe680c4); Fase 2 plan ready, see the dedicated memory above
- [Air priority: target-specific loadout selection — COMPLETE, committed & pushed](project_air_priority_target_specific_loadout.md) — items 3-7+8 committed/pushed 2026-09-12; 2026-09-14 added producer-duplication fix (shared `Context.classify_asset_dimension`) + `get_target_report` no-visibility fix, full suite 2465 OK, committed & pushed (3fe680c4)
- [Vehicle/Ship/Aircraft asset_type vs category — RESOLVED & IMPLEMENTED 2026-09-15](project_vehicle_asset_type_category_conflict.md) — normalized all 3 Mobile asset classes: asset_type=general class (Ground/Sea/Air_Asset_Type), category=granular sub-class (only exists for Vehicle); also fixed Context.classify_asset_dimension's Aircraft branch (was reading category); found but did NOT fix a pre-existing unrelated bug in Ship/Aircraft.loadAssetDataFromContext (flat dict + missing .items()); full suite 2465 OK/5 skipped, committed & pushed 3e94d468
- [No-visibility → LOW priority (not high)](feedback_no_visibility_low_priority.md) — 2026-09-14 design decision, reverses the naive "unknown = high risk" framing; applies to future Fase 2 target_cp estimate only, `_target_affinity` stays neutral
- [Combat-power action-selection guidance](feedback_combat_power_action_selection.md) — use 'Attack' task specifically for attack-priority ratio, not sum/avg; user wants a per-action priority vector eventually (Attack/Defense/Maintain/Retrait) feeding a later tactical decision layer
- [Block.get_recon_efficiency removed — 2026-09-10](project_block_get_recon_efficiency_removed.md) — was dead code shadowed by Military's override; Test_Block.py updated; full suite 2311/OK (skipped=5)
- [Region.py unattributed dead-code removal — RESOLVED](project_region_unattributed_dead_code_removal.md) — was the user's own live editor autosave, confirmed 2026-09-10, committed 74065590
- [Session recap 2026-09-08 — read this first](project_session_2026_09_08_summary.md) — Sabin/wargaming research saved, memory-vs-wiki boundary + transfer procedure defined, core DCS-vs-synthetic-events campaign architecture recorded. No code changes. Next: design the synthetic-events turn structure.
- [Session recap 2026-08-26](project_session_2026_08_26_summary.md) — ProArt P16 verified sync with VM: pulled LoggerClass cwd fix + git-sync hook (5a417765), full suite reconfirmed 2315 tests/OK (skipped=5)/0 errors. Verification-only session, no new work.
- [Session recap 2026-08-21](project_session_2026_08_21_summary.md) — WIKI merge, Test_Air_Route_Manager fully fixed, Fase 2 (all 9 design decisions) closed, DataType.Route/Edge/Waypoint made to actually work end-to-end.

## Campaign temporal model (core architecture, design in progress)
- [DCS sessions vs. synthetic sessions — read before any turn/time-structure work](project_campaign_temporal_model_dcs_vs_synthetic.md) — event generation splits into real-time DCS game events (small asset subset, HW-limited) + synthetic-generator events (extrapolated to realistic campaign-scale asset count), combined with weights per time unit; turn structure for the synthetic side still undefined — next design topic

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

## External references
- [WIKI_LLM_SIMULATION — also consult for conceptual/design questions](reference_wiki_llm_simulation.md) — standing pointer to Analysis/WIKI_LLM_SIMULATION (conceptual simulation-theory wiki), complementary to (not above) project memory; wiki never references this project's memory back
- [Philip Sabin (KCL) wargame-design theory](reference_philip_sabin_simulating_war.md) — Force/Space/Time/Command framework, Igo-Ugo turn-design rationale; interim copy, slim to a pointer once merged into the wiki at Fase 3

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
