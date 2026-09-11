---
name: project-priority-calc-combat-power-redesign
description: "Multi-session redesign of Region/Military combat-power and priority calculation (fog-of-war from recon reports); Fase 0 (bug fixes) complete 2026-09-11, Fase 1/2 (Ship/Aircraft combat power, EnemyTargetSnapshot) not started"
metadata: 
  node_type: memory
  type: project
  originSessionId: 68a4bcf0-0d82-4d78-95f3-8034f1d81a8d
  modified: 2026-09-11T15:39:15.212Z
---

# Region/Military priority calc & combat power redesign

Started 2026-09-11. Original trigger: user noticed `Region._calculate_priority()` called `Military.combat_power()` with wrong args, and that priority calc uses full ground-truth info about enemy blocks instead of the probabilistic recon-report data (`Region.get_recon_reports()` / `Block.get_recognition_report()`), unlike the rest of the reporting system.

## Two-pass analysis (Opus, high effort — both done via background Agent)

**v1** (first pass): proposed `EnemyTargetSnapshot` frozen dataclass with two factories — `_snapshot_from_report` (fog-of-war, for enemy blocks) and `_snapshot_from_block` (ground-truth, for friendly/defense). Flagged that `Region.get_recon_reports(side)` has an inverted-looking semantic (uses the OBSERVED side's own C2 efficiency, not the observer's) — confirmed via `Test_Region.py:676-687`, fix is a one-line change (`Utility.enemySide(side)` on the efficiency lookup) **plus** adopting the convention that `side` names the *observed* side, not the observer. No other callers exist in the repo, so this is a safe pending change (not yet applied — still open, low priority since no current caller).

**v2** (second pass, after user pushback): corrected v1's proposal to estimate fog-of-war combat power from a hand-authored table — user pointed out Vehicle.py already has a real per-model scoring system (`Vehicle_Data.get_vehicle_scores` → `'combat score'['global_score']`), and it should be reused/calibrated, not reinvented; also flagged Ship/Aircraft need the same treatment (Aircraft is loadout-dependent, harder). v2 found the recon report can only reveal `(asset_type, dimension)` buckets (never the model), so fog-of-war estimation must be a **calibrated aggregate** (median of real per-model combat power within each bucket, via a shared `combat_power_from_score()` formula), never a duplicate hand-tuned table. Recommended: extract the Vehicle formula into a shared pure function first (done in Fase 0), then Phase 2 builds `build_estimated_combat_power_table(force, action)` from it. For aircraft: use **max** (not average) of `combat_score(task, loadout)` over available loadouts per model/task — the loadout-best-case unifies "reference loadout" and "aggregate over loadouts" into one thing; a per-asset `current_loadout` field is deferred (would need `Air_Resources_Assigner` to assign it).

## Fase 0 — DONE 2026-09-11 (bug fixes, no new features)

Full suite 2316 tests / 2315 OK / 0 failures / 5 skipped after. Fixed, in order:
- **B0**: `VEHICLE_SIZE_CATEGORY`/`SHIP_SIZE_CATEGORY` keys normalized to `Big`/`Medium`/`Small` (were lowercase, inconsistent with Structure/Aircraft) — `Context.py`.
- **B1**: `Vehicle.set_combat_power` read `['global score']` (space) but `Vehicle_Data.VEHICLE[model]['combat score']` only has `'global_score'`/`'category_score'` (underscore) → KeyError on every real Vehicle construction, masked by `Test_Vehicle.py`'s mock using the same wrong key. Fixed; extracted formula into `Context.combat_power_from_score(category, score, efficacy_table, efficiency, ...)`, shared for future Ship/Aircraft reuse and for Phase 2's fog-of-war calibration.
- **B2**: `VEHICLE[model]`/`SHIP[model]` never exposed `physical_characteristics`/`category` → `Vehicle.get_physical_characteristics()`/`Ship.get_physical_characteristics()` always returned `None` → **no Vehicle or Ship ever appeared in `asset_summary`** of a recon report (only Structure/Aircraft did). Fixed by adding both keys in the population loop.
- **B3**: `Military.combat_power` rewritten to mirror `Mobile.combat_power(force, action)`'s contract (float if both given, Dict otherwise) — was subscripting `asset.combat_power[force][action]` (a method, not a dict → would TypeError), returning the whole nested dict instead of a float, and not actually filtering by force.
- **B4**: the 3 broken call sites in `Region.py` (`calc_combat_power_center`, `_calculate_priority`) aligned to the fixed signature.

**Bugs found beyond the checklist, also fixed in Fase 0:**
- `Vehicle_Data.get_vehicle_scores`'s validation (`if scores and scores not in SCORES`) was checking whether the *whole* `scores` argument was itself a member of `SCORES` — always false for any list/tuple, including the default `SCORES` itself. **Every real (non-mocked) call — including the one in `Vehicle.__init__` — always raised `ValueError`.** No real Vehicle could ever be constructed before this fix. Already flagged as a known bug in `Test_Vehicle_Data.py`'s old docstring ("DATA BUG... funzione è inutilizzabile") — tests were asserting the broken behavior; rewritten to assert correct behavior, mirroring `Ship_Data.get_ship_scores` (which was already correct).
- `SCORES` declared `'radar score air'` but `VEHICLE[model]` never computed it (only `'radar score'`/`'radar score ground'`) — added.
- `Region.calc_combat_power_center`: `block.is_Air_Base`/`is_Ground_Base`/`is_Naval_Base` used **without parentheses** (always-truthy bound-method reference → the force-matching filter never actually filtered). Fixed; also added a `block.position is not None` guard (was an unguarded `None * float`).
- `_calculate_priority`: added a zero-division guard for `target_cp <= 0`.

## Open design question — combat power action for `_calculate_priority`'s ratio (deferred, see below)

`_calculate_priority` needs a `Military.combat_power(force, action)` value to compute the attack/defense ratio, but the call chain (`_calc_attack_priority` → `_calc_surface_priority`/`_calc_air_priority` → `_calculate_priority`) never threads a specific action through — only `force` is derivable (from `get_military_category()`). Fase 0 stand-in: sum combat power across **all** tasks of the block's force. User feedback 2026-09-11 (see [[feedback_combat_power_action_selection]]) says this is wrong — read that memory before touching this again.

## Urban classification — RESOLVED, was intentional

`Region._is_logistic_block()` was found mid-session with `Urban` added to the `isinstance(block, (Production, Storage, Transport, ...))` tuple — an unattributed diff (same pattern as the prior resolved incident, see [[project_region_unattributed_dead_code_removal]]). **Confirmed by user 2026-09-11: intentional, their own edit.** Rationale: Urban blocks produce human resources (`hr`) and affect morale, so they are legitimately a logistic/strategic target — explicit Douhet (strategic bombing theory) framing from the user. `Test_Region.py::test_update_logistic_priorities` updated accordingly (gave `mock_urban.resource_manager.production_value` a harmless 0 return) — full suite green (2316/2315 OK/5 skipped) as of 2026-09-11.

## Next steps (not started)
- Apply the `get_recon_reports` one-line semantic fix (v1 finding above) when a real caller needs it.
- Fase 1: Ship `set_combat_power` (+ new `SEA_COMBAT_EFFICACY` table — doesn't exist yet) and Aircraft `set_combat_power` (max-over-loadouts table).
- Fase 2: `EnemyTargetSnapshot`, `build_estimated_combat_power_table`, `update_military_priorities(side, use_recon=True)`.
- Resolve the action-selection design question per [[feedback_combat_power_action_selection]] before touching `_calculate_priority` again.
