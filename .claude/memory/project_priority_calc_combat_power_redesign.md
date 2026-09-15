---
name: project-priority-calc-combat-power-redesign
description: "Multi-session redesign of Region/Military combat-power and priority calculation (fog-of-war from recon reports); Fase 0 (bug fixes) complete 2026-09-11, Fase 1/2 (Ship/Aircraft combat power, EnemyTargetSnapshot) not started"
metadata: 
  node_type: memory
  type: project
  originSessionId: 68a4bcf0-0d82-4d78-95f3-8034f1d81a8d
  modified: 2026-09-15T16:39:02.130Z
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

## Fase 1 — DONE 2026-09-11 (Ship + Aircraft combat power)

Full suite 2331 tests / OK / 0 failures / 5 skipped after (2323 after Ship alone, +8 Aircraft tests).

**Ship** (straightforward, same pattern as Vehicle):
- New `SEA_COMBAT_EFFICACY` table in `Context.py` (Attack/Defense/Retrait × 9 ship categories, first-pass values, documented rationale in the table's comment).
- `Ship.set_combat_power()` added, mirrors `Vehicle.set_combat_power` via `combat_power_from_score`. Removed the dead `combatPower` property stub.
- New `Test_Ship.py` (didn't exist before) — 7 tests, includes a direct numeric check against `combat_power_from_score`.
- **Bug found and fixed, blocking ALL real (non-mocked) Ship AND Aircraft construction**: `Ship.__init__`/`Aircraft.__init__` did `self.speed = {"nominal": None, "max": None}`, which goes through `Mobile.speed`'s property setter → calls `self.checkParam(speed=...)` → neither `Ship.checkParam` nor `Aircraft.checkParam` accept a `speed` kwarg → `TypeError` on every real instantiation. `Mobile.__init__` already sets the exact same placeholder as `self._speed` directly (default `speed` param), so the reassignment was redundant — removed it in both files (Vehicle never had this bug: it uses a private `_speed_off_road` dict instead of touching `self.speed`).

**Aircraft** (needed a dedicated Opus-high-effort analysis — user overrode my first-pass proposal with real constraints, see below):
- User feedback (verbatim reasoning, now implemented): air tasks (CAP, Intercept, Strike, SEAD, ...) are mission *roles*, not mutually-exclusive tactical postures like ground/sea's Attack/Defense/Retrait — a CAP loadout serves both offense and defense simultaneously. So instead of Vehicle/Ship's per-action combat power, aircraft get **one aggregate value** (best loadout per role, summed), replicated across all `ACTION_TASKS['air']` keys to satisfy `Mobile.combat_power(force, action)`'s existing contract without changing it. User also specified: use `Aircraft_Data.combat_score()` (target-independent), never `combat_score_target_effectiveness()` (target-specific) — this is the ground-truth/planning value, not a report-time evaluation against a known target.
- `Aircraft_Data.combat_aggregate()`: for each task in `AIR_TASK`, takes `max(combat_score(task, loadout) for loadout in get_loadouts(model, task))` — `get_loadouts` already returns `{}` for tasks the model has no loadout for, so role-relevance comes for free from the loadout DB, no hand-written role→task map needed. Sums the per-task maxima.
- `_build_combat_aggregates()`: normalizes with **log1p before min-max**, not plain min-max — measured raw sums span ~0 to ~362 (bomber outliers dominated by loadout quantity), a linear min-max would compress 63 of 65 registry models under 0.05. Populates `AIRCRAFT[model]['combat aggregate']` and a separate `AIRCRAFT_TASK_BEST_SCORES[model]` (kept out of `AIRCRAFT[model]` itself to not break its flat-float convention, unlike Vehicle/Ship's nested `{'global_score':...}` shape).
- New `AIR_COMBAT_EFFICACY`: replaced the old broken one (2 hardcoded models, indexed by model not role, never imported where read) with a flat `{role: efficacy}` table (Fighter 5.0 down to Transport 1.0) — no per-action nesting, since aircraft don't have per-action combat power.
- `Aircraft.set_combat_power()`/`air_combat_power()` added (Aircraft had literally no working combat power before — the `combatPower` property was dead: wrong signature, unimported name). Aircraft also got a `model` constructor param it never had.
- **New universal fix**: added `Asset.model` read-only property (`getattr(self, '_model', None)`) to the base class — `Block.get_recognition_report` does `getattr(asset, 'model', None)` and **raises** if `None`, but no class exposed a public `model`, only `_model`. This blocked recon-report `asset_summary` population for Vehicle/Ship/Aircraft alike (found via an end-to-end smoke test in Fase 0, deferred at the time, now fixed for good).
- **Bug fixed**: `Block.py:640` referenced `aat.TANKER.value` — `TANKER` doesn't exist on `Air_Asset_Type` → `AttributeError` the moment an Aircraft asset reached that branch.
- **Bug fixed**: `Region._calculate_priority`'s Fase-0 "sum across all tasks" stand-in (see open question below) would 10x-inflate air combat power now that all 10 air tasks carry the identical value. Extracted `Region._representative_combat_power(block, force)`: sums for ground/sea (still the Fase-0 stand-in, unchanged), takes a single task for air (they're all equal, summing would be wrong twice over).
- New `Test_Aircraft.py` — 8 tests, includes uniform-across-tasks check and a Fighter-vs-Transport ordering check.
- Also fixed en route (`Aircraft_Data.py`): `get_aircraft_scores` had the exact same "whole-argument-membership" validation bug as Vehicle's old B1-adjacent bug (`get_vehicle_scores`, fixed in Fase 0) — every default call crashed. Fixed the same way.

## Open design question — combat power action for `_calculate_priority`'s ratio (still deferred for ground/sea)

Unchanged from Fase 0 for ground/sea: `_representative_combat_power` still sums across all tasks as a stand-in. User wants the `'Attack'` task specifically there (see [[feedback_combat_power_action_selection]]) — not yet implemented, read that memory before touching `_calculate_priority`/`_representative_combat_power` again. Air is no longer affected by this question (it now has a single well-defined aggregate, not a per-task breakdown to choose from).

## Feature — priority lists split by mil_category — IMPLEMENTED 2026-09-14 (commit 3fe680c4)

User request 2026-09-11: split the flat priority list into separate lists per military block type/echelon (air base, ground base, stronghold, company, battalion, regiment, division, etc.), "per effettuare valutazioni strategiche più accurate distinguendo le diverse forze militari utilizzabili" — comparing a lone Company's priority against an entire Division's on the same scale isn't tactically meaningful; the consumer (mission assignment) needs to pick among forces of comparable scale/role separately.

**No new data model needed**: `Military.mil_category` already holds exactly this taxonomy (`Context.MILITARY_CATEGORY`):
```python
MILITARY_CATEGORY = {
    'Ground_Base': ('Stronghold', 'Farp', 'Regiment', 'Battallion', 'Company', 'Brigade', 'Division', 'Command_&_Control_C2', 'Command_&_Control_C4'),
    'Air_Base': ('Airbase', 'Heliport'),
    'Naval_Base': ('Port', 'Shipyard', 'Naval_Group'),
}
```
The gap is purely in the query layer: `Region.get_blocks_by_criteria(side, category, block_class)` (used by `get_sorted_priority_blocks`/`get_normalized_priority_blocks`) filters `category` against `BlockCategory` (Military/Logistic/Civilian) or the block's generic `.category`, never against `Military.mil_category` — there's currently no way to ask "just the Battallions."

**Design decided with the user (AskUserQuestion, 2026-09-11)**:
1. **Extend `get_blocks_by_criteria`** with a new `mil_category: Optional[str] = None` parameter (validate against the flattened values of `Context.MILITARY_CATEGORY`), filtering `isinstance(block, Military) and block.mil_category == mil_category`. This flows through to `get_sorted_priority_blocks`/`get_normalized_priority_blocks` for free (they already forward `category` — add `mil_category` alongside it) — so `region.get_sorted_priority_blocks(count=10, side="Red", category="Military", mil_category="Battallion")` becomes possible per-list.
2. **Add a grouped helper** `get_priority_lists_by_mil_category(self, side: str, sort_by: str = "highest") -> Dict[str, List[BlockItem]]` that returns one sorted list per `mil_category` actually present in the region for that side (skip empty ones), built on top of (1) rather than duplicating the sort logic.
3. Remember `_invalidate_caches()` iterates cached methods by name (`Region.py` ~line 1170s) — if `get_blocks_by_criteria`'s cache key shape changes (new param), no code change needed there since `cache_clear()` clears the whole method regardless of signature, but double check nothing else calls `get_blocks_by_criteria` positionally (grep before changing the signature — adding the new param at the end, with a default, should be safe either way).

**Timing**: implemented 2026-09-14 (commit `3fe680c4`), alongside unrelated fixes from that
session — see [[project_session_2026_09_14_summary]].

## Next steps (not started)
- **2026-09-15: full Fase 2 implementation plan ready, see [[project_fase2_recon_combat_power_plan]] — read that file in full before touching this area.** It supersedes the bullet points below (`EnemyTargetSnapshot` turned out to already be functionally replaced by the existing `TargetProfile`/`get_target_report` pipeline — though that pipeline itself turned out to be UNUSABLE for combat-power estimation, too lossy via `Context.TARGET_CLASSIFICATION`; a new `Combat_Power_Estimation.py` module is planned instead). The `get_recon_reports` one-line fix and the action-selection question below are both folded into that plan's Fase 1/Fase 2. 7 open design questions block implementation start.
- Also newly found while planning Fase 2 (2026-09-15), pre-existing, NOT fixed, unrelated to the above: `Context.get_target_classification` returns the first matching key in `TARGET_CLASSIFICATION`'s dict order, so `AAA` always resolves to `'Armored'`, never `'Air_Defense'` (both lists contain it); separately `tc.AIRCRAFT` collapses all nine `Air_Asset_Type` values into one bucket. Flag for a future separate fix, not in scope of Fase 2.
- Consider whether `Vehicle`/`Ship` should also get the `air_combat_power()`-style single-aggregate treatment reconsidered — no, not needed, their per-action breakdown is real and wanted (Attack/Defense/Maintain/Retrait are genuine mutually-exclusive postures); this was Aircraft-specific.
- ~~Separate open thread (2026-09-14): [[project_vehicle_asset_type_category_conflict]]~~ — RESOLVED & IMPLEMENTED 2026-09-15 for all three Mobile classes (Vehicle/Ship/Aircraft), see that memory.
