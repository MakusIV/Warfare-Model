---
name: project-air-priority-target-specific-loadout
description: Design proposal (not implemented) for using Aircraft_Data.combat_score_target_effectiveness() with actually-available loadouts when computing air-base attack priority against a specific target — ready to implement in a future session
metadata: 
  node_type: memory
  type: project
  originSessionId: 68a4bcf0-0d82-4d78-95f3-8034f1d81a8d
  modified: 2026-09-11T18:05:11.612Z
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
3. ~~Dimension vocabulary unification~~ — done, commit `6ab1e6dc`. Remaining: add `WEAPON_TARGET_CLASS_MAP` (target-class collapse, 26 → 12) in `Context.py`; make `get_weapon_score_target` raise on out-of-vocabulary class input instead of silently returning 0.0.
4. `Region._target_profile_from_block`, `_profile_to_weapon_lists`; alias `get_target_report` as `_target_profile_from_report`. Tests: mixed armor+SAM block, empty block, unclassifiable assets.
5. `Aircraft_Data.best_loadout_against_target` + `combat_aggregate_against_target`, with `available_loadouts` filtering. Test: a model with both anti-tank and anti-ship loadouts should rank differently against `Armored` vs `ship` targets.
6. Loadout availability: `Context.LOADOUT_DOCTRINE` + `get_doctrine_loadouts`; `Air_Resources_Assigner.get_available_loadouts`; `Military.weapons_availability` + wrapper. Verify each filter is truly a no-op when its argument is `None`.
7. Integration: `Region._target_affinity`, `_operative_aircraft_by_model`, `target_affinity` param on `_calculate_priority`, wired through `_calc_air_priority`; cache + invalidation. Test: `_calc_surface_priority` and the defense branch must stay bit-identical (default `1.0`).
8. Deferred, decide separately: propagate real `route_length`/`route_speed` into `combat_score_target_effectiveness` (today the range gate is effectively disabled); consider a weighted-distribution variant instead of the `coverage`-truncated list heuristic in step 4.
