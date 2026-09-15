---
name: project-vehicle-asset-type-category-conflict
description: "Vehicle/Ship/Aircraft category vs asset_type conflict — RESOLVED and IMPLEMENTED 2026-09-15 for all three Mobile asset classes: asset_type now holds the general class (Ground_Vehicle_Asset_Type/Sea_Asset_Type/Air_Asset_Type), category the granular sub-class where one exists; full suite 2465 OK/5 skipped"
metadata:
  node_type: memory
  type: project
  originSessionId: 68a4bcf0-0d82-4d78-95f3-8034f1d81a8d
  modified: 2026-09-15T13:08:18.546Z
---

# category vs asset_type (Vehicle/Ship/Aircraft) — RESOLVED and IMPLEMENTED 2026-09-15

Follows up [[project_priority_calc_combat_power_redesign]] / [[project_air_priority_target_specific_loadout]].
Landed in two steps, same session: first Vehicle + `Military.py:348` (both Vehicle and Ship parts,
after the user asked to extend it and a verification pass found no risk), then the user asked to
check whether `Aircraft.py` had the same `category` vs `asset_type` issue and, if so, normalize all
three Mobile asset classes (Vehicle, Ship, Aircraft) consistently. It did, and the full normalization
is now implemented. Full suite: **2465 tests OK (skipped=5)**, exit code 0, both times — no
regression vs. the pre-change baseline.

## New convention (now live, all three Mobile classes)

- **`asset_type`**: general class — `Ground_Vehicle_Asset_Type` for Vehicle (Tank/Armored/Motorized/
  Artillery_Fixed/Artillery_Semovent/SAM_Big/SAM_Medium/SAM_Small/EWR/AAA), `Sea_Asset_Type` for Ship
  (Carrier/Cruiser/Destroyer/Frigate/Corvette/...), `Air_Asset_Type` for Aircraft (Fighter/
  Fighter_Bomber/Attacker/Bomber/Heavy_Bomber/Awacs/Recon/Transport/Helicopter). Matches what the
  target-classification pipeline (`Block.ASSET_TYPE`, `Context.classify_asset_dimension`,
  `Context.get_target_classification`) already expected for all three.
- **`category`**: granular sub-class where one is actually modeled — currently only Vehicle has one:
  the inner keys of `GROUND_MILITARY_VEHICLE_ASSET[asset_type]` (e.g. `Main_Battle_Tank`,
  `Infantry_Fighting_Vehicle`, `Command_&_Control`, `Scout_&_Recon`, `Howitzer_Big`, ...).
  `isCommandControl` stays on `category` (it always was this vocabulary). **Ship and Aircraft have no
  granular sub-vocabulary in Context.py** — `SEA_MILITARY_CRAFT_ASSET` and `AIR_MILITARY_CRAFT_ASSET`
  are both flat single-level dicts keyed directly by the general class (unlike
  `GROUND_MILITARY_VEHICLE_ASSET`'s nesting) — so `category` is simply unused/free for Ship and
  Aircraft today; nothing invented for it.

## Files changed

- `Asset.py`: `asset_type.setter` now converts an `Enum` to its `.value` (mirrors `category`'s
  setter) — needed since `asset_type` now routinely receives `Ground_Vehicle_Asset_Type`/
  `Sea_Asset_Type` members. **Also** added the same Enum→str conversion in `Asset.__init__` itself
  (`_validate_all_params` is fed from local constructor variables, not through the property
  setters — the setter-only fix was not enough, caught by the first post-fix test run: 11 errors,
  `TypeError: Invalid type for asset_type. Expected str, got Ground_Vehicle_Asset_Type`).
- `Vehicle.py`: `isTank`/`isArmor`/`isMotorized`/`isArtillery_*`/`isSAM_*`/`isAAA`/`isEWR` (not
  `isCommandControl`) now read `self.asset_type`. `set_combat_power` now guards/keys on
  `self.asset_type` (`GROUND_COMBAT_EFFICACY`/`combat_power_from_score`). `loadAssetDataFromContext`
  — **only the Military branch** — now buckets by `self.asset_type` and matches sub-type against
  `self.category` (both the `GROUND_MILITARY_VEHICLE_ASSET` and `AIR_DEFENSE_ASSET` lookups). The
  **Logistic branch is untouched** — it indexes `BLOCK_INFRASTRUCTURE_ASSET` with an unrelated
  vocabulary (`category="Road"`, `asset_type="Truck"`) that has nothing to do with
  `Ground_Vehicle_Asset_Type`; conflating the two would have broken logistic Vehicles. `checkParam`'s
  Military branch swapped the same way (bucket=`asset_type`, match=`category`); its non-Military
  branch (Logistic) also left untouched for the same reason. `checkParam` has zero production call
  sites (grepped) — only exercised by tests, so this part carried no runtime risk.
- `Military.py:348` (`_get_artillery_stats`): **both** the Vehicle part (`asset.category` →
  `asset.asset_type`, checked against `gat.ARTILLERY_FIXED/ARTILLERY_SEMOVENT/TANK`) **and** the Ship
  part (`asset.category` → `asset.asset_type`, checked against `sat.CORVETTE/CRUISER/DESTROYER/
  FRIGATE`) — user extended the fix to Ship after asking for a quick verification; confirmed no
  other code reads `Ship.asset_type` for this purpose and no production call site was at risk.
- `Ship.py`: **full normalization** (not just Military.py:348) — `isDestroyer`/`isCarrier`/
  `isCruiser`/`isFrigate`/`isFastAttackShip`/`isTransport`/`isSubmarine` and `set_combat_power`
  (guard + `SEA_COMBAT_EFFICACY`/`combat_power_from_score` key) now read `self.asset_type`.
  `loadAssetDataFromContext`'s Military branch: bucket key swapped to `self.asset_type`, match
  swapped to `self.category` (see pre-existing-bug note below — this branch doesn't actually work
  either way). `checkParam` needed **no change**: its Military branch already validated
  `asset_type` against `SEA_MILITARY_CRAFT_ASSET.keys()` (flat dict of the general class) — it was
  already following the new convention by accident, unlike Vehicle's (which had the nested-dict
  nuance and needed a real logic swap).
- `Aircraft.py`: same full normalization — `isFighter`/`isFighterBomber`/`isAttacker`/`isBomber`/
  `isHeavyBomber`/`isAwacs`/`isRecon`/`isTransport`/`isHelicopter` and `air_combat_power` (guard +
  `AIR_COMBAT_EFFICACY`/`combat_power_from_score` key) now read `self.asset_type`.
  `loadAssetDataFromContext`'s Military branch swapped the same way as Ship's. `checkParam` needed
  no change (same reason as Ship — `AIR_MILITARY_CRAFT_ASSET.keys()` is already the general class).
- `Context.py` — `classify_asset_dimension`'s **Aircraft branch** (not just comments this time): used
  to read `getattr(asset, 'category', None)` for the small/med/big role-based dimension bucket —
  switched to a dedicated `getattr(asset, 'asset_type', None)` read (kept separate from the
  `asset_category` variable, which the Structure branch still legitimately uses for
  `structure_type` — did not touch that). This was a real functional bug-in-waiting: had this not
  been fixed, `Block.get_recognition_report`/`Region._target_profile_from_block` would have silently
  stopped classifying every Aircraft's dimension the moment `Aircraft.py`'s own `category` stopped
  being populated with the general class. Also updated the `BLOCK_ASSET_CATEGORY['Ground_Military_Vehicle_Asset']`
  generation-loop comments (cosmetic, no data structure changed) from the earlier Vehicle-only pass.
- `Test_Vehicle.py`: every fixture that previously did `category=Ground_Vehicle_Asset_Type.X` /
  `asset_type="<granular>"` now does the reverse (`category="<granular>"`, `asset_type=Ground_Vehicle_Asset_Type.X`).
  `isCommandControl`'s test untouched (still `category="Command_&_Control"`).
- `Test_Ship.py` / `Test_Aircraft.py`: same treatment — every `category=Sea_Asset_Type.X`/
  `category=Air_Asset_Type.X` swapped to `asset_type=`; `test_initialization` in both now asserts
  the fields the opposite way round.
- `Test_Military.py`: `_make_vehicle`/`_make_ship` helpers (used only by the `_get_artillery_stats`/
  `artillery_in_range` tests) renamed their param and now set `.asset_type` instead of `.category`;
  their docstrings updated. The shared `setUp()` mocks (`mock_vehicle`, `mock_vehicle_damaged`,
  `mock_ship`) already set both `.category` and `.asset_type` to the same value defensively, so they
  needed no change and weren't a source of breakage.
- `Test_Context.py` (`TestClassifyAssetDimension`): the three Aircraft dimension tests now drive
  `asset_type` instead of `category`; `test_aircraft_missing_category_returns_none` renamed to
  `test_aircraft_missing_asset_type_returns_none` and now omits `asset_type` instead of `category`.
- `Test_Region.py` (`TestTargetProfileFromBlock`): `test_aircraft_missing_category_skipped` renamed
  to `test_aircraft_missing_asset_type_skipped`, same field-swap; `test_aircraft_dimension_mapping_small_med_big`
  needed no change — it already drove dimension off `asset_type` (its first positional arg), with
  `category` set to the same value defensively, same pattern as `Test_Military.py`'s shared mocks.

## What this does NOT fix (known, explicitly out of scope or pre-existing)

- No live factory constructs a real `Vehicle`/`Ship`/`Aircraft` from `Vehicle_Data.py`/`Ship_Data.py`/
  `Aircraft_Data.py` — those modules' per-model `'category'` field (e.g.
  `VEHICLE['T-90M']['category'] == 'Tank'`) is still not wired to `asset_type` at construction time.
  Vehicle at least has a real granular vocabulary (`GROUND_MILITARY_VEHICLE_ASSET`'s inner keys) that
  a future `category` could be populated from; Ship/Aircraft have none. Building that factory is
  future work, not part of this fix.
- **Newly discovered pre-existing bug, NOT fixed here (out of scope, flagged for future work)**:
  `Ship.loadAssetDataFromContext` and `Aircraft.loadAssetDataFromContext`'s Military branch were
  already structurally broken before this session and still are — they do
  `for k, v in asset_data[self.asset_type]:` (no `.items()`) where `asset_data` is
  `SEA_MILITARY_CRAFT_ASSET`/`AIR_MILITARY_CRAFT_ASSET`, both **flat** dicts (unlike Vehicle's nested
  `GROUND_MILITARY_VEHICLE_ASSET`). `asset_data[self.asset_type]` returns a leaf dict
  (`{'cost': ..., 'value': ..., ...}`), and iterating a dict without `.items()` yields only its keys
  (strings like `'cost'`) — `for k, v in <that>:` would raise `ValueError: too many values to
  unpack` the moment this branch actually ran with a non-empty result. Never caught because — same
  "no live factory" gap above — nothing calls this method with real data outside mocked tests that
  replace `asset_data.__getitem__` wholesale. Only the `self.category`/`self.asset_type` field
  choice was fixed to match the new convention; the flat-vs-nested/`.items()` bug itself was left
  alone as a separate, pre-existing, out-of-scope defect.

## Verification method (for future similar conflicts)

Before implementing, actually grepped/read: `GROUND_COMBAT_EFFICACY`'s keys (confirmed = general
class), `GROUND_MILITARY_VEHICLE_ASSET`'s and `BLOCK_ASSET_CATEGORY`'s generation-loop shape
(outer=general class, inner=granular — confirmed via the loop's own now-corrected comments),
`Block.ASSET_TYPE`/`classify_asset_dimension`'s `valid_asset_types` gate (confirmed asset_type must
be a `Ground_Vehicle_Asset_Type` member), every test fixture that would touch the changed lines
(`Test_Vehicle.py` fully, `Test_Military.py`'s artillery-stats tests and shared mocks), and whether
`checkParam`/the Logistic branch had any production call site (grepped, none). Ran the affected
test files before AND after the source edits to get an exact, predicted failure list, then fixed
tests to match — no surprises other than the `Asset.__init__` Enum-conversion gap, caught immediately
by the first re-run.
