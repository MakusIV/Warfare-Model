---
name: project-air-priority-target-specific-loadout
description: Design proposal for using Aircraft_Data.combat_score_target_effectiveness() with actually-available loadouts when computing air-base attack priority against a specific target. Checklist items 3-7 done 2026-09-12, plus the weighted-distribution half of item 8 (coverage heuristic replaced); route_length/route_speed propagation explicitly deferred by the user, not implemented. Feature complete and committed.
metadata: 
  node_type: memory
  type: project
  originSessionId: 68a4bcf0-0d82-4d78-95f3-8034f1d81a8d
  modified: 2026-09-14T16:37:13.793Z
---

# Target-specific air combat priority via best-available-loadout — design proposal

Requested by the user 2026-09-11, analyzed via background Opus agent (high effort). **Not implemented** — this is a ready-to-execute design for a future session. See [[project_priority_calc_combat_power_redesign]] for the broader combat-power/priority-calc redesign this extends (Fase 0+1 already done and committed).

## The idea (user's own framing)

`Aircraft.air_combat_power()` (Fase 1, already shipped) is deliberately target-independent — it's the generic combat power used in `Military.combat_power` for overall force comparison. But when `Region._calc_air_priority` computes the priority of an air base attacking a *specific* target, it should instead ask "what's the best loadout this air base actually has available against *this* target" — using `Aircraft_Data.combat_score_target_effectiveness()` (target-aware) instead of `combat_score()` (target-agnostic), filtered to loadouts that are actually available per dedicated availability dictionaries (a new concept — nothing like it existed before this analysis, though the *pieces* to build it turned out to already exist, see below).

## Two blocking bugs found while analyzing this — already fixed, see commit b38bab1f

Not part of this feature, found along the way, fixed immediately in the same session:
1. `Military.get_military_category()` always returned `"Naval_Base"` (missing parens on `is_Air_Base`/`is_Ground_Base`/`is_Naval_Base`, three plain `if`s so the last always won). No test called the real method. This broke `_calculate_priority`/`_representative_combat_power`'s force lookup for every ground/air block since Fase 0.
2. `Context.TARGET_CLASSIFICATION` had `dict_keys(...)` as an unexpanded single list element for 7 classifications (Airbase, Helibase, Port, Shipyard, Farp, Stronghold, Generic) — they could never be matched by `get_target_classification`. Fixed with `*...keys()`.

Both fixed and committed before this design work; full suite 2332/OK/5 skipped.

## Key findings (verified against real code, not assumed)

- **`_calc_air_priority` has no notion of "task" at all** — confirmed, it's a structural gap shared with the still-open `feedback_combat_power_action_selection` question, but independent of it (that one is about `Military.combat_power(force, action)`; this is about `combat_score_target_effectiveness`, a different call). Recommendation: don't introduce a task parameter — maximize over all tasks with available loadouts (see design below), leave task selection to mission assignment.
- **"Available loadouts" is NOT a new concept — it already exists, unused**: `Logic/Air_Resources_Assigner.py` has `_loadout_availability`, `get_loadouts_availability`, `_reduction_weapons_availability`, `_increase_weapons_availability`, all operating on a `{weapon_type: {weapon_name: qty}}` structure — but **grepping the whole non-test source finds no producer of that structure and no caller of these functions**. The stock/inventory side needs to be *connected*, not invented. `Payload` (goods/energy/hr/hc/hs/hb) has no munitions concept; `Block.supply` doesn't exist as real code (only in a docstring example) — the live attribute is `warehouse`.
- ~~Three incompatible dimension vocabularies~~ — **UNIFIED, commit `6ab1e6dc` (2026-09-11)**: everything now uses the lowercase-abbreviated `big/med/small` (`Context.DIMENSION_CLASSES`, matching what was already the dominant convention across 7 files in the weapon-efficacy subsystem). `_get_weapon_param_from_target` now validates `target_dim` against `DIMENSION_CLASSES` directly instead of a separate hardcoded set, so the two can't drift apart again. Fixed a live bug found while verifying feasibility: `Air_Resources_Assigner._create_ground_mission_task_table` documented and used lowercase `target_data` but fed it into `get_task_from_target`, which validated against the old capitalized set → `ValueError` on every real call. `to_weapon_target_keys`/`WEAPON_DIMENSION_MAP` etc. from the design below are no longer needed for the *dimension* half of the adapter — only the target-*class* collapse (next point) is still needed.
- **Weapon efficiency tables cover 12 target classes, not 7** (corrected by direct enumeration of the real dicts, the original "7" estimate was wrong): `Soft, Armored, Hard, Structure, Air_Defense, Airbase, Port, Shipyard, Farp, Stronghold, ship, Aircraft`. Coverage varies per weapon (e.g. only Aircraft_Weapon_Data's weapons cover `Aircraft`). Still missing entirely (14 classes, `.get()` always → 0.0): `Administrative, Airport, Civilian, Electric, Factory, Farm, Fuel_Line, Generic, Helibase, Heliport, Power_Plant, Railway, Road, Service` — almost all the "Logistic Asset Category" half of `Target_Class_Name`. A collapse/fallback map (`WEAPON_TARGET_CLASS_MAP` in the design below) is still needed for these.
- `combat_score_target_effectiveness` doesn't propagate `route_length`/`route_speed` (always defaults `0.0`/`1.0`) — the range gate is effectively disabled; distance only enters via `time_to_intercept` elsewhere in the pipeline. Flagged as a follow-up, not blocking.
- Existing precedent to align with: `Air_Resources_Assigner.py:898` already calls `combat_score_target_effectiveness(task, loadout_name, target_types, target_dims)` with **lists**, not the weighted-distribution variant (`loadout_target_effectiveness_by_distribuition`, which loses radar/TVD/avionics/speed scoring because it bypasses `combat_score_eval`). Recommendation: follow that precedent (lists), but only include target (class, dimension) pairs covering most of the target's actual composition — `get_weapon_score_target` *averages* across all listed combos including absent ones, so a long tail dilutes the score.

## Proposed design (function signatures, ready to implement)

**1. Target profile derivation** (`Context/Region.py`) — two producers, one format, so Fase 2's `EnemyTargetSnapshot` can swap the producer later without touching consumers:
```python
TargetProfile = Dict[str, Dict[str, int]]   # {classification: {'big'|'med'|'small': count}} — dimension
                                             # vocabulary now unified (commit 6ab1e6dc), no adapter needed
                                             # for this half anymore.

def _target_profile_from_block(self, target_block: Block) -> TargetProfile:
    """Ground-truth profile from the block's real assets (classify each operative asset with
    Context.get_target_classification(asset.asset_type) + Context.get_dimension, no detection
    probability — same logic as Block.get_recognition_report minus the recon-report randomness,
    which would make this non-deterministic and break @lru_cache)."""

def _target_profile_from_report(self, report: Dict) -> Optional[TargetProfile]:
    """Alias for the already-implemented get_target_report — same format, recon-report source."""

@staticmethod
def _profile_to_weapon_lists(profile: TargetProfile, coverage: float = 0.85) -> Tuple[List[str], List[str]]:
    """Converts to the (target_type list, target_dimension list) combat_score_target_effectiveness
    expects. Dimension strings pass through unchanged (unified vocabulary); target_type classification
    strings still need collapsing to the 12 classes the weapon efficiency tables actually cover, via a
    new Context.WEAPON_TARGET_CLASS_MAP (see below) — Context.get_target_classification's output
    (any of the 26 Target_Class_Name values) is not guaranteed to be one of those 12.
    Includes only (class, dimension) pairs covering `coverage` of total count, since
    get_weapon_score_target averages across all listed combos — a long tail dilutes the score."""
```
New `Context.py` adapter still needed: `WEAPON_TARGET_CLASS_MAP` (collapses `Target_Class_Name`'s ~26 values down to the 12 the weapon efficiency tables actually cover — `Soft, Armored, Hard, Structure, Air_Defense, Airbase, Port, Shipyard, Farp, Stronghold, ship, Aircraft` — with a sane fallback, e.g. `Structure`, for the 14 uncovered Logistic classes). No dimension adapter needed anymore (unified). Also consider making `get_weapon_score_target` raise on an out-of-vocabulary *class* instead of silently returning 0.0, matching what `to_weapon_target_keys` would have done — same rationale, smaller surface now that only the class side remains.

**2. Best loadout against a target** (`Asset/Aircraft_Data.py`, next to `combat_aggregate`):
```python
def best_loadout_against_target(self, task: str, target_type: List[str], target_dimension: List[str],
                                available_loadouts: Optional[Iterable[str]] = None) -> Tuple[Optional[str], float]:
    """Best (name, score) among get_loadouts(self.model, task) ∩ available_loadouts (None = no filter),
    scored with combat_score_target_effectiveness. (None, 0.0) if nothing available/eligible."""

def combat_aggregate_against_target(self, target_type: List[str], target_dimension: List[str],
                                    tasks: Optional[Iterable[str]] = None,
                                    available_loadouts_by_task: Optional[Dict[str, List[str]]] = None
                                    ) -> Tuple[float, Dict[str, Tuple[Optional[str], float]]]:
    """Analog of combat_aggregate() but MAX over tasks, not sum — against one target, what matters is
    the single best way to hit it, not how many ways exist (that's what the generic aggregate is for)."""
```

**3. Loadout availability — three orthogonal filters, applied in cascade** (static → volatile):

| Level | Granularity | Source | Status |
|---|---|---|---|
| L1 year | model × loadout | `loadout_year_compatibility` | exists (`Aircraft_Loadouts.py`) |
| L2 doctrine | model × loadout, per side | `Context.LOADOUT_DOCTRINE` | to create |
| L3 stock | block × loadout | `_loadout_availability` (exists, unused) + `Military.weapons_availability` | function exists, data source to create |

```python
# Context.py — new
LOADOUT_DOCTRINE: Dict[str, Dict[str, Dict[str, List[str]]]] = {
    '*':   {'F-4E Phantom II': {'denied': ['Nuclear Strike']}},
    'red': {'F-16C Block 52d': {'allowed': []}, 'MiG-29A': {'denied': ['R-77 CAP']}},
}
def get_doctrine_loadouts(model: str, side: Optional[str] = None) -> Optional[List[str]]:
    """Whitelist for (model, side) or None = unrestricted. 'allowed' wins over 'denied' if both present."""

# Logic/Air_Resources_Assigner.py — new (NOT Aircraft_Loadouts.py, keep that a dependency-free data module)
def get_available_loadouts(model: str, task: Optional[str] = None, *, year: Optional[int] = None,
                           side: Optional[str] = None, weapons_availability: Optional[Dict[str, Dict[str, int]]] = None,
                           min_units: int = 1) -> List[str]:
    """Cascades: year compat -> doctrine -> stock (_loadout_availability >= min_units). Each filter is
    skipped (not "denies everything") when its argument is None — priority calc must still work on
    blocks without modeled stock."""

# Block/Military.py — new
@property
def weapons_availability(self) -> Dict[str, Dict[str, int]]:
    """{weapon_type: {weapon_name: qty}} — deliberately separate from resource_manager.warehouse
    (Payload models continuous fungible resources; munitions are discrete per-weapon-model counts).
    The bridge to logistics (goods -> munitions via resupply) is out of scope here."""
def get_available_loadouts(self, model: str, task: Optional[str] = None, year: Optional[int] = None) -> List[str]:
    """Delegates to Air_Resources_Assigner.get_available_loadouts with self.side/weapons_availability."""
```

**4. Integration — multiplier, not replacement** (`Region.py`): the `target_cp / combat_power` ratio in `_calculate_priority` is homogeneous (both sides from `_representative_combat_power`, same scale, same `[0.1, 10.0]` clip) — replacing the numerator with a `combat_score_target_effectiveness` value (different, unnormalized scale) would break the ratio. Also `_calc_air_priority` serves *defense* too, where "effectiveness against the target" is meaningless (the target is a friendly block, not a target to hit). So: a multiplicative **affinity factor**, applied only on the attack branch (`block.side != target_block.side`):
```python
_AFFINITY_MIN, _AFFINITY_MAX = 0.25, 2.0

def _target_affinity(self, block: Military, target_block: Block) -> float:
    """1.0 (neutral) if: friendly target (defense branch), empty target profile, no available loadouts,
    or block isn't air. Otherwise: ratio of the air fleet's target-specific score to its generic
    reference score, weighted by aircraft count per model, clipped to [_AFFINITY_MIN, _AFFINITY_MAX] —
    dimensionless, independent of combat_score's absolute scale."""

def _operative_aircraft_by_model(self, block: Military) -> Dict[str, List]:
    """{model: [operative Aircraft]} via block.get_asset_list(asset_class='Aircraft')."""
```
`_calc_air_priority` passes `target_affinity=self._target_affinity(block, target_block)` through to `_calculate_priority`, which multiplies it into the final attack-branch return (default `1.0` keeps `_calc_surface_priority`/the defense branch bit-identical). `_target_affinity` needs `@lru_cache` + hooking into `_invalidate_caches` alongside `_calc_attack_priority`/`_calc_defense_priority`.

## Implementation checklist for the future session (ordered)

1. ~~Fix `Military.get_military_category()`~~ — **done**, commit `b38bab1f`.
2. ~~Fix `Context.TARGET_CLASSIFICATION`~~ — **done**, commit `b38bab1f`.
3. ~~Dimension vocabulary unification~~ — done, commit `6ab1e6dc`. ~~Target-class collapse (26 → 12) + raise-on-invalid~~ — **done 2026-09-12**: `Context.WEAPON_TARGET_CLASS_MAP` + `get_weapon_target_class()` added (Context.py, right after `get_target_classification`); identity for the 12 covered classes, `Helibase/Airport/Heliport → Airbase`, `Generic` + the 9 remaining Logistic classes → `Structure`. `get_weapon_score_target` (+ `get_weapon_score_target_distribuition` sibling) in all 3 `*_Weapon_Data.py` files now normalizes `t_type` through `get_weapon_target_class` (raises `ValueError` for a genuinely unrecognized string, e.g. typo) and raises `ValueError` for `t_dim not in DIMENSION_CLASSES` — replacing the old silent skip-and-continue-to-0.0 behavior. Key finding during implementation: this fixes a real latent bug in the already-tested-but-unwired `Air_Resources_Assigner._create_ground_mission_task_table` pipeline, which normalizes unknown targets to `'Generic'` by design (`test_unknown_type_mapped_to_generic`) — `'Generic'`/`'Helibase'` were valid `TARGET_CLASSIFICATION` keys so they never hit the old `continue` branch, but no weapon table covered them, so they silently scored 0.0; now they correctly collapse to `Structure`/`Airbase` before the efficiency lookup. `Aircraft_Weapon_Data.get_weapon_efficiency` (a separate, similarly-shaped function) was deliberately left untouched — out of scope. All ~14 pre-existing "returns 0.0 for invalid class" unit tests across `Test_Ground_Weapon_Data.py`, `Test_Aircraft_Weapon_Data.py`, `Test_Ship_Weapon_Data.py`, `Test_Vehicle_Data.py` were rewritten to expect `ValueError`; new tests added in `Test_Context.py::TestWeaponTargetClassMap` and a `Generic→Structure` parity test per weapon-data file. Full suite: 2343 tests OK (skipped=5).
4. **DONE 2026-09-12** (same session as item 3): `Region._target_profile_from_block`, `Region._profile_to_weapon_lists`, `Region._target_profile_from_report` implemented in `Context/Region.py` (right after `get_target_report`), plus a `TargetProfile = Dict[str, Dict[str, int]]` type alias and one added line in `_invalidate_caches` (`self._target_profile_from_block.cache_clear()` under the `"priority"` branch). `_target_profile_from_block` is `@lru_cache`d (safe — deterministic, no randomness, same pattern as `_calc_air_priority`) and replicates `Block.get_recognition_report`'s classification loop (Block.py:601-679) directly against a block's real assets, with all recon-probability gating removed — only `is_operative()` assets are counted. `_profile_to_weapon_lists` is a `@staticmethod`; important correction made during implementation to the original design wording: `combat_score_target_effectiveness`'s consumer chain (`Air_Resources_Assigner._extract_target_lists` → `get_weapon_score_target`) treats the two lists as a **full cross-product**, not index-aligned pairs — so the coverage algorithm merges `(weapon_class, dimension)` pairs (after collapsing via `Context.get_weapon_target_class`) by combined count, takes them in descending order until cumulative coverage ≥ `coverage` (default 0.85), then returns the deduplicated classes/dimensions among the selected pairs (same shape as the real `Air_Resources_Assigner.py:898` precedent). `_target_profile_from_report` is a thin wrapper delegating to `get_target_report` (no method-aliasing idiom exists elsewhere in this codebase, so a real method was used instead of `_target_profile_from_report = get_target_report`, to stay independently mockable). Also required extending `Region.py`'s existing `Block.Block` import to pull in `ASSET_TYPE` — zero new circular-import risk (already-imported module, plain list constant). 27 new tests added to `Test_Region.py` (`TestTargetProfileFromBlock`, `TestProfileToWeaponLists`, `TestTargetProfileFromReport`), reusing the `Test_Military.py` MagicMock/stub-class pattern (`_Vehicle`/`_Ship`/`_Aircraft` = `type(...)` stubs to dodge the Aircraft→Aircraft_Weapon_Data circular import) for a real mixed armor+SAM integration test (verified real numbers: Tank `{length:9,width:3.5,height:2.5,weight:48}`→`big`/`Armored`; SAM_Small `{length:5,width:2.5,height:2,weight:18}`→`small`/`Air_Defense`). Full suite after item 4: 2370 tests OK (skipped=5), 0 errors/failures.
5-6. **DONE 2026-09-12** (same session, immediately after item 4): `Aircraft_Data.best_loadout_against_target`/`combat_aggregate_against_target` (item 5) + the loadout-availability cascade (item 6) — `Context.LOADOUT_DOCTRINE`/`get_doctrine_loadouts`, `Air_Resources_Assigner.get_available_loadouts`, `Military.weapons_availability`/`get_available_loadouts`. Two corrections made to the original design during implementation:
   - `Air_Resources_Assigner.py` imports `Block.Military` **at module level** (confirmed by reading the file) → `Military.get_available_loadouts` imports `Air_Resources_Assigner.get_available_loadouts` **locally inside the method body**, never at module level (would deadlock the circular import).
   - `Context.get_doctrine_loadouts(model, side)` returns the **raw** doctrine rule (`{'allowed': [...]}` or `{'denied': [...]}` or `None`), NOT a pre-resolved allowlist as the original design sketch implied — resolving `'denied'` into a concrete allowlist needs the model's full loadout set, which lives in `Aircraft_Loadouts.py`, and `Context.py` must never import from `Aircraft_Loadouts.py` (which already imports FROM `Context.py` — circular). The actual set-intersection/subtraction happens in `Air_Resources_Assigner.get_available_loadouts`, which has the candidate list in hand. `LOADOUT_DOCTRINE` ships **empty** (`{}`) — the original design's example entry cited a `"Nuclear Strike"` loadout that doesn't actually exist for `F-4E Phantom II` in `AIRCRAFT_LOADOUTS`.
   - `best_loadout_against_target` seeds its max-search with the **first real candidate's score**, not a `0.0` sentinel — avoids a subtle bug present in the existing `get_list_of_aircrafts` precedent (strict `>` comparison against a `0.0` seed silently drops every candidate if all of them score exactly `0.0`).
   - `Military._weapons_availability` defaults to `None` (not `{}`) in `__init__` — `None` means "stock not modelled, skip the L3 filter"; `{}` means "stock modelled and explicitly empty, every loadout fails the filter" — these are deliberately different and both are tested explicitly.
   - Munitions stock (`weapons_availability`) is a **genuinely new** piece of live state — confirmed via grep that no `Block`/`Military`/`Storage` attribute like it existed before, and `Resource_Manager.warehouse` (`Payload`) has no munitions fields, only goods/energy/manpower.
   36 new tests added across `Test_Context.py::TestLoadoutDoctrine` (6), `Test_Aircraft_Data.py::TestBestLoadoutAgainstTarget`/`TestCombatAggregateAgainstTarget` (12, including a zero-sentinel regression test), `Test_Air_Resources_Assigner.py::TestGetAvailableLoadouts` (16), `Test_Military.py` (6, in the existing `TestMilitary` class). Full suite after 5-6: 2411 tests OK (skipped=5), 0 errors/failures.
7. **DONE 2026-09-12** (same session, immediately after items 5-6): integration into `Region._calc_air_priority`/`_calculate_priority` — the point where items 4-6 actually start affecting real priority numbers instead of just existing as callable, tested, unused code. Implemented exactly per the original design ("multiplier, not replacement"):
   - `_calculate_priority` gained a `target_affinity: float = 1.0` parameter, multiplied into all three return branches (military/logistic/civilian). Default `1.0` is a true no-op — `_calc_surface_priority` never passes it, so that branch and the whole ground/naval path are provably bit-identical (locked in by a new regression test, `TestCalcSurfacePriorityUnaffectedByAffinity`, that patches `_target_affinity` and asserts it's never called from `_calc_surface_priority`).
   - New `Region._target_affinity(block, target_block) -> float` (`@lru_cache`d, added to `_invalidate_caches` under `"priority"` alongside `_target_profile_from_block`): returns neutral `1.0` whenever affinity doesn't apply (same-side/defense target, `block` not an `Air_Base`, empty/unclassifiable target profile, or no operative aircraft) — otherwise computes, per aircraft model present in the block (weighted by aircraft count), the ratio of `Aircraft_Data.combat_aggregate_against_target(...)` (target-specific, using item 5-6's per-task `get_available_loadouts` cascade) to `Aircraft_Data.combat_aggregate()` (generic, target-agnostic), sums both weighted by count, takes the overall ratio, and clips to `[_AFFINITY_MIN, _AFFINITY_MAX] = [0.25, 2.0]` (new module-level constants in `Region.py`, next to `TargetProfile`).
   - New `Region._operative_aircraft_by_model(block) -> Dict[str, List]` helper: groups a block's real, operative `Aircraft` assets by `.model` (NOT by `.asset_type`/role, which is what `Military.get_asset_list` groups by — this needed its own flatten-and-regroup pass over `get_asset_list(asset_class='Aircraft')`'s results).
   - `_calc_air_priority` now computes `target_affinity=self._target_affinity(block, target_block)` and passes it through to `_calculate_priority` — this is the only call site that ever sets a non-default `target_affinity`.
   - Required a new top-level import in `Region.py`: `from Asset.Aircraft_Data import Aircraft_Data` (for `Aircraft_Data._registry` lookups by model name) — verified safe, no circular import (`Aircraft_Data.py` only imports from `Context.Context`/`Aircraft_Loadouts`/`Utility`, nothing that chains back to `Region`/`Block`).
   - One test bug caught and fixed during implementation: a test used the aircraft name `'F-16C Block 50'`, which doesn't exist in the real registry (`AIRCRAFT_LOADOUTS`/`Aircraft_Data._registry` — the real names are `'F-16A Fighting Falcon'`, `'F-16A MLU'`, `'F-16C Block 52d'`, `'F-16CM Block 50'`); `Aircraft_Data._registry.get(model)` silently returning `None` for a typo'd name and being skipped by `_target_affinity`'s `continue` made the test's expected weighted ratio wrong in a way that produced a plausible-looking (but incorrect) result — worth remembering that a typo'd aircraft model name fails silently here, not loudly, which can mask itself as "the math is just different than expected" rather than "the test data is wrong."
   21 new tests added to `Test_Region.py` (`TestOperativeAircraftByModel`, `TestTargetAffinity` — including weighted-average, both clip-bound, and cache-invalidation cases — `TestCalculatePriorityTargetAffinity`, `TestCalcAirPriorityTargetAffinity`, `TestCalcSurfacePriorityUnaffectedByAffinity`). Full suite: **2432 tests OK (skipped=5)**, 0 errors/failures.
   **Not yet committed** — working tree now has Region.py/Context.py/Aircraft_Data.py/Air_Resources_Assigner.py/Military.py + their 5 test files pending (items 4 through 7 all bundled together, uncommitted), user has not been asked about a commit yet across this entire multi-item run.
4. `Region._target_profile_from_block`, `_profile_to_weapon_lists`; alias `get_target_report` as `_target_profile_from_report`. Tests: mixed armor+SAM block, empty block, unclassifiable assets.
5. `Aircraft_Data.best_loadout_against_target` + `combat_aggregate_against_target`, with `available_loadouts` filtering. Test: a model with both anti-tank and anti-ship loadouts should rank differently against `Armored` vs `ship` targets.
6. Loadout availability: `Context.LOADOUT_DOCTRINE` + `get_doctrine_loadouts`; `Air_Resources_Assigner.get_available_loadouts`; `Military.weapons_availability` + wrapper. Verify each filter is truly a no-op when its argument is `None`.
7. Integration: `Region._target_affinity`, `_operative_aircraft_by_model`, `target_affinity` param on `_calculate_priority`, wired through `_calc_air_priority`; cache + invalidation. Test: `_calc_surface_priority` and the defense branch must stay bit-identical (default `1.0`).
8. Deferred, decide separately: propagate real `route_length`/`route_speed` into `combat_score_target_effectiveness` (today the range gate is effectively disabled); consider a weighted-distribution variant instead of the `coverage`-truncated list heuristic in step 4.

## Item 8 (2026-09-12) — split in two, only one half implemented

The user clarified explicitly: **route_length/route_speed propagation is deferred indefinitely**,
not just "for now" — today (and for the foreseeable future) priority is driven only by vehicle
speed and distance-to-target (`time_to_intercept`); weapon range is NOT modeled in the priority
calc at all, and this is an intentional simplification, not a gap to close soon. Do not revisit
this without the user raising it again.

The **weighted-distribution half was implemented and committed**:
- `Region._profile_to_weapon_lists` (coverage-truncation heuristic, `coverage=0.85` cutoff) was
  **removed** and replaced by `Region._profile_to_weapon_distribution(profile) -> Dict[str, Dict]`,
  producing `{classification: {'perc_type': float, 'perc_dimension': {dim: float}}}` — every
  classification/dimension in the profile now contributes to the score weighted by its real share,
  instead of some being dropped once a coverage threshold was already met. No pre-collapsing
  through `Context.get_weapon_target_class` is needed (proved mathematically equivalent whether or
  not classes that collapse onto the same weapon-table class are merged beforehand, since
  `get_weapon_score_target` already normalizes internally) — this simplified the implementation
  relative to the removed heuristic.
- `Aircraft_Data` gained: `_loadout_target_effectiveness_by_distribution` (wraps
  `Aircraft_Loadouts.loadout_target_effectiveness_by_distribuition`, already imported),
  `combat_score_target_effectiveness_by_distribution(task, loadout, target_distribution)`, and
  `combat_score_eval` gained an optional `target_distribution` param (takes precedence over
  `target_type`/`target_dimension` when given) — **all other score components (radar/TVD/engine/
  avionics/speed) are preserved intact**, only the loadout-vs-target sub-component switches
  formula. This is deliberately more faithful than the pre-existing `get_list_of_aircrafts` usage
  of the distribution variant, which bypasses `combat_score_eval` entirely and loses those
  components — flagged in the original design analysis, not fixed here (out of scope, unrelated
  pre-existing code, and appears to call a non-existent method name `ac.loadout_target_effectiveness_by_distribuition(task=..., ...)` — a latent bug, untouched).
- `Aircraft_Data.best_loadout_against_target`/`combat_aggregate_against_target` (item 5) now take
  a single `target_distribution: Dict` parameter instead of `(target_type: List, target_dimension:
  List)` — these methods are exclusive to this session's design chain (no other pre-existing
  caller), so the signature change is safe. The pre-existing list-based
  `combat_score_target_effectiveness` (used by `Air_Resources_Assigner.get_aircraft_mission` at
  line ~898) was left completely untouched.
- `Region._target_affinity` (item 7) updated to call `_profile_to_weapon_distribution` and pass a
  single `target_distribution` arg to `combat_aggregate_against_target`.
- Tests: `Test_Region.py::TestProfileToWeaponLists` replaced by `TestProfileToWeaponDistribution`
  (12 tests, no more coverage-boundary tests, added proportionality/sum-to-1 tests); new
  `Test_Aircraft_Data.py::TestCombatScoreTargetEffectivenessByDistributionAircraft` (8 tests,
  mirrors the existing list-based test class); `TestBestLoadoutAgainstTarget`/
  `TestCombatAggregateAgainstTarget` updated in place to use distributions.
- Full suite: **2439 tests OK (skipped=5)**, 0 errors/failures.
- **Committed and pushed**, commit `ed4d74d5` — this was the explicit final instruction for this
  session (items 4-8, the entire target-specific air-priority design, landed in one continuous run).

## Diagnostic table for _target_affinity (2026-09-12, same session)

Added `print_target_affinity_scenarios()` to `Test/Test_Region.py`, gated by a module-level
`STAMPA_TARGET_AFFINITY = False` flag (same pattern as `Vehicle_Data.py`'s `STAMPA` flag — inert
by default, doesn't run under `unittest discover`). Builds a fixed attacking fleet (Military
Air_Base, side='Blue', with mocked F-14A Tomcat + F-16CM Block 50 aircraft assets) and computes
`Region._target_affinity`/`_calculate_priority` (civilian-branch target, value=5/weight=2/tti=2 so
base_priority without affinity = 5.0, isolating the multiplicative effect) across 4 target
composition scenarios: 100% Armored (3 Tank), 100% Air_Defense (3 SAM_Small), mixed
Armored+Air_Defense (2+2), 100% Aircraft (3 parked fighters). Prints via `tabulate`.

Real output when run (sanity-checked, makes sense): the three ground-target scenarios all clip to
the affinity floor `0.25` (a pure-fighter fleet has no competitive CAS/SEAD loadouts, so its
target-specific score is far below its generic reference score); the air-target scenario scores
higher at `0.482` (CAP/Intercept is what F-14/F-16 are actually good at) — directionally correct,
though the ground-scenario floor-clipping means the real underlying ratios (all <0.25) aren't
distinguishable from each other in this particular fleet composition.

**User will ask in a future session to extend this with additional/different scenarios** — when
that happens, re-read `print_target_affinity_scenarios()` in `Test/Test_Region.py` first (scope
was deliberately narrowed to `_target_affinity` only, per user's explicit choice among three
options offered — NOT `_calc_surface_priority`/Ground_Base/Naval_Base attackers, NOT
logistic/civilian branches in general — confirm whether that scope still holds before adding
scenarios that fall outside it).

## Next session

The target-specific air-priority design (items 3-7 + the distribution half of item 8) is complete,
tested, and shipped. Nothing left open on this specific thread except the explicitly-deferred
route_length/route_speed question (do not re-raise proactively) and the diagnostic-table extension
noted above (user-initiated, wait for them to raise it). Other threads still available:
- **Independent thread**: per-`mil_category` priority list split — **implemented** 2026-09-14
  (uncommitted, see below), design was decided in [[project_priority_calc_combat_power_redesign]].
- **Independent thread**: Fase 2 fog-of-war `EnemyTargetSnapshot` — see
  [[project_priority_calc_combat_power_redesign]], not started.

## 2026-09-14 session — producer duplication resolved (Solution A) + no-visibility fix

Continuation after an accidental session close; user resumed with 4 numbered points, only 2
resulted in code changes (the other 2 — Vehicle asset_type/category coherence, and where the
no-visibility policy applies — are recorded separately, see [[project_vehicle_asset_type_category_conflict]]
and [[feedback_no_visibility_low_priority]]).

**Producer duplication (the "two producers, one format" note in item 1 above) — resolved.**
`Region._target_profile_from_block` was reimplementing the exact same asset→(classification,
dimension) classification rule already living in `Block.get_recognition_report`
(Vehicle/Ship/Structure via physical characteristics + `get_dimension`; Aircraft via
`Air_Asset_Type` category → small/med/big). User was offered two solutions (extract a shared pure
classification function vs. have the ground-truth producer call `get_recognition_report(efficiency=1.0)`
and reuse `get_target_report`) and picked **the shared-function extraction** — the reuse-via-full-
visibility-report alternative was rejected for two reasons surfaced during analysis: it would
invoke `get_recognition_report`'s side effect (`self.state.update()`) purely to compute a query,
and `calcProbability(1.0)` isn't a mathematically guaranteed `True` (rare `random.uniform(0,1) == 1.0`
edge), which would have undermined `_target_profile_from_block`'s `@lru_cache` purity guarantee.

Implemented: `Context.classify_asset_dimension(asset, valid_asset_types=None)` (`Context.py`, right
after `get_dimension`) — single source of truth for the per-asset classification rule, returns the
dimension bucket or `None` (covers unrecognized class, missing physical characteristics/category,
or an out-of-vocabulary `asset_type` when `valid_asset_types` is passed). Both
`Block.get_recognition_report` (passes `valid_asset_types=ASSET_TYPE`) and
`Region._target_profile_from_block` (same) now call it instead of maintaining their own copies —
removed ~30 duplicated lines from each. `Block.py`'s `Context` import swapped `get_dimension` for
`classify_asset_dimension` (no longer called directly there). New direct unit tests in
`Test_Context.py::TestClassifyAssetDimension` (10 tests); existing `Test_Region.py::TestTargetProfileFromBlock`
tests (mixed armor+SAM, damaged excluded, unclassifiable skipped, aircraft dimension mapping) serve
as the integration check and all still pass unchanged.

**`get_target_report` no-visibility fix (item 4/point 3 from the user's list) — implemented.**
`Region.get_target_report` (`Region.py`, right after the mil_category priority-list helpers) had a
falsy-check bug: `if not _operative: return None` only catches a genuinely empty/absent operative
dict. But `Block.get_recognition_report` always populates `asset_summary['operative'][asset_type][dimension]`
skeleton keys (initialized to 0) for every real asset in a block *regardless* of whether the
report's detection-probability gate passed — only the increment is gated. So when the gate fails,
`_operative` is a **non-empty dict of real keys, all zero counts** — previously this slipped past
the falsy check and got returned as if it were valid "target has zero assets of these types" data,
which is backwards (it's actually "we don't know," not "we know it's empty"). Fixed by checking the
**raw** total count in `_operative` (summed across all asset_type/dimension entries, before the
classification grouping loop) and returning `None` when it's zero — deliberately checked on the
raw dict, not on the built `target_classification_report`, so it doesn't get confused with the
different, pre-existing case where real nonzero-count asset_types exist but none of them map to a
known `TARGET_CLASSIFICATION` entry (that case correctly keeps returning `{}`, unchanged — see
`test_all_unclassifiable_returns_empty_dict`). 3 new tests added to
`Test_Region.py::TestGetTargetClassificationReport`. Since `_target_profile_from_report` just
delegates to `get_target_report`, this fix flows through automatically; `_target_affinity`'s
existing empty-profile → neutral `1.0` handling required no change (see
[[feedback_no_visibility_low_priority]] for why that's correct and deliberate).

Full suite after both fixes: **2465 tests OK (skipped=5)**, 0 errors/failures. **Committed and
pushed**, commit `3fe680c4` — bundled together with the mil_category priority-list split
(`get_blocks_by_criteria`/`get_sorted_priority_blocks`/`get_normalized_priority_blocks`/
`get_priority_lists_by_mil_category`), which had been sitting uncommitted in `Region.py`/
`Test_Region.py` since the prior, accidentally-closed session and got swept into this same commit.
