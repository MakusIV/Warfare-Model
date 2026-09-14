---
name: project-vehicle-asset-type-category-conflict
description: "Confirmed conflict for ground Vehicle: 'category' and 'asset_type' are both overloaded with incompatible vocabularies across Vehicle.py/Military.py vs. the target-classification pipeline; user wants asset_type to hold the general classes but asked for deeper analysis before implementing a fix"
metadata:
  node_type: memory
  type: project
  originSessionId: 68a4bcf0-0d82-4d78-95f3-8034f1d81a8d
  modified: 2026-09-14T14:49:07.645Z
---

# Vehicle.category vs Vehicle.asset_type — confirmed conflict, fix not yet implemented

Raised by the user 2026-09-14, verified against real code (not assumed) in the same session as
[[project_priority_calc_combat_power_redesign]] / [[project_air_priority_target_specific_loadout]].
**Not implemented** — user explicitly said "Dobbiamo analizzare in modo più approfondito il
codice e valutare meglio la soluzione da adottare" when asked to confirm scope. Read this memory
in full before touching `Vehicle.py`/`Military.py` on this topic again.

## The user's framing

For ground Vehicles, `asset_type` and `dimension` (big/med/small) should be sufficient for
priority evaluations, because those evaluations run mostly on `combat_score`, which already
factors in asset_type + quantity + dimension. The general classes ('Tank', 'Armored', 'Motorized',
'SAM_Big', 'SAM_Medium', 'SAM_Small', 'Artillery_Fixed', 'Artillery_Semovent', 'EWR', 'AAA' —
`Context.Ground_Vehicle_Asset_Type`) should live in `asset_type`.

## What's actually in the code (verified, both directions are broken today)

- **`asset_type` holding the general classes is already the convention the target-classification
  pipeline expects**: `Block.ASSET_TYPE` (`GROUND_ASSET_TYPE + AIR_ASSET_TYPE + SEA_ASSET_TYPE`) is
  built directly from `Ground_Vehicle_Asset_Type` values, and `Context.get_target_classification`/
  `TARGET_CLASSIFICATION` are called with `asset.asset_type` throughout `Region._target_profile_from_block`,
  `Region.get_target_report`, `Block.get_recognition_report` (now unified via
  `Context.classify_asset_dimension`, see [[project_air_priority_target_specific_loadout]]).
- **But `Vehicle.py`'s own combat-power/classification code reads `self.category` for exactly this
  vocabulary instead**: `isTank/isArmor/isMotorized/isArtillery_*/isSAM_*/isAAA/isEWR/isCommandControl`
  properties (`Vehicle.py:251-292`) all compare `self.category` against `Ground_Vehicle_Asset_Type`
  values. Worse: **`Vehicle.set_combat_power`** (`Vehicle.py:298-356`, the real path that produces
  the combat_power the whole redesign is about) keys `GROUND_COMBAT_EFFICACY[act]` and
  `combat_power_from_score(category=self.category, ...)` on **`self.category`**, not `asset_type`.
  `Military.py:348` has the same pattern (`asset.category in [gat.ARTILLERY_FIXED.value, ...]`).
- **Meanwhile `asset_type` is ALSO used for a second, unrelated vocabulary**: `Vehicle.loadAssetDataFromContext`
  (`Vehicle.py:76-139`) uses `self.category` as a coarse bucket key into `GROUND_MILITARY_VEHICLE_ASSET`
  (example in the code's own comment: `category = "Armor"`) and `self.asset_type` as the granular
  subtype key inside that bucket (`asset_type = "Infantry_Fighting_Vehicle"`, `"Track_Radar"`, etc.)
  — this has nothing to do with `Ground_Vehicle_Asset_Type`'s Tank/Armored/... vocabulary.

So today, general classes are read from **both** fields depending on which code path you're in, and
`asset_type` separately carries a second, incompatible granular vocabulary in the data-lookup path.
This is not a coherence question to settle going forward — it's already inconsistent in the
existing code, in both directions, right now.

## What a fix would touch (identified, not yet decided/implemented)

1. `Vehicle.py:253-292` (`isTank` family) and `Vehicle.py:342-344` (`set_combat_power`'s
   `GROUND_COMBAT_EFFICACY`/`combat_power_from_score` call) — switch from `self.category` to
   `self.asset_type`.
2. `Military.py:348` — same switch for the ground/naval high-value-asset check.
3. Decide what `category` becomes once it's no longer double-booked: does it stay only the
   `loadAssetDataFromContext` bucket key ('Armor', 'Road', ...), or does something else change
   there too? `loadAssetDataFromContext`'s own comment example uses `'Armor'` (singular, umbrella)
   which doesn't even match `Ground_Vehicle_Asset_Type.ARMORED.value` (`'Armored'`) — worth
   checking whether `GROUND_MILITARY_VEHICLE_ASSET`'s real keys match that comment or have already
   drifted too.
4. No live factory currently constructs real `Vehicle` objects from `Vehicle_Data`/`VEHICLE` data
   outside tests (grepped, confirmed) — so there's no single call site to check for how
   `asset_type`/`category` actually get populated end-to-end today; this fix is somewhat
   speculative until that construction path exists or is found.
5. User asked only about ground Vehicle; `Ship.py` has the analogous pattern for `sat.CORVETTE`
   etc. in `Military.py:348` but was explicitly out of scope for this round — ask before extending.

## Next session

Do the deeper code analysis the user asked for before proposing a concrete fix: trace where (if
anywhere) real `Vehicle.category`/`asset_type` values actually get set today (construction path,
if one exists, or test fixtures as the closest proxy), and confirm `GROUND_MILITARY_VEHICLE_ASSET`'s
real category keys before assuming `'Armor'` is accurate.
