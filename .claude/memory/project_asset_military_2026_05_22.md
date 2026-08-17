---
name: project-asset-military-2026-05-22
description: "Mobile.py/Military.py combat_range, air_defense_volume, combat_state methods added 2026-05-22; Region.py metric helper pattern"
metadata: 
  node_type: memory
  type: project
  originSessionId: 54069b25-fc3b-495d-81bb-9efd11133381
  modified: 2026-08-16T16:07:50.743Z
---

## Mobile.py — new methods (2026-05-22)
- `air_defense_volume() → Optional[Cylinder]` — Vehicle: checks AA_CANNONS + MISSILES with min/max_altitude; extra filter: if weapon has `task` field, must contain `'Anti_Air'`; Ship: MISSILES_SAM only; returns Cylinder or None
- `combat_range() → Optional[float]` — Vehicle types: CANNONS/ARTILLERY/MORTARS/ROCKETS/MISSILES/AUTO_CANNONS; Ship: MISSILES_ASM/MISSILES_TORPEDO/GUNS; two exclusion rules: (1) MISSILES with min_altitude (SAM), (2) any weapon whose task list contains `'Anti_Air'`; Ship ranges km→m
- `fire_range` property and getter/setter removed from Mobile (2026-05-22)
- `Ship.py`: added `model: Optional[str] = None` parameter → `self._model = model` (needed for Ship_Data._registry lookup)
- `Ground_Weapon_Data`: `min_altitude`/`max_altitude` (m AGL) added to all AA_CANNONS and SAM MISSILES; `task` field present on all ground weapons
- Ship_Weapon_Data GUNS: ALL have `task: ['Anti_Air', ...]` → excluded from combat_range; MISSILES_ASM/TORPEDO have no Anti_Air → included
- `GROUND_WEAPON_TASK['Anti_Air'] = 'Anti_Air'` (string); `task` field in weapon data is a list of strings

## Military.py — updated methods (2026-05-22)
- `_get_artillery_stats()` — uses `asset.combat_range()` (not `artillery_range` attr); filters by category: Vehicle must be ARTILLERY_FIXED/ARTILLERY_SEMOVENT/TANK; Ship must be CORVETTE/CRUISER/DESTROYER/FRIGATE (all using `.value`); bug fixed: was using `gat.TANK`/`sat.CORVETTE` etc without `.value` (enum vs string comparison always False)
- `air_defense_volume() → List[Cylinder]` — iterates all assets, filters by `validate_class(Vehicle|Ship)` + `is_operative()` + hasattr; calls `asset.air_defense_volume()`; collects non-None; returns list (empty if none)
- `combat_range() → Optional[Tuple[float,float,float,int]]` — (max_range, med_range, ratio, quantity); iterates all assets once; filters `is_operative()` + `hasattr('combat_range')`; excludes None returns; uses `numpy.median`; returns None if no ranges
- `combat_power()`: guard `if hasattr(asset,'combat_power') and asset.is_operative()` — hasattr skips non-combat assets, is_operative() excludes damaged; mocks must set `is_operative.return_value` explicitly
- `combat_state() → Optional[float]` — formula: `(0.3 * operative_efficiency + 0.7 * c2_efficiency) * ratio_operative`; returns None if no assets; result ∈ [0,1]
- `get_c2_efficiency()`: `hasattr(asset,'efficiency')` + `asset.is_operative()` filters; non-operative C2 excluded

## Region.py — metric helper pattern
- `_get_region_average_metric(side, category, method_name)` — central helper for all 5 metric functions
- Uses `getattr(block, method_name, None)` + `callable()` check → safe for non-existent methods
- `get_recon_reports(side)` calls `get_c2_efficiency` once (not per-block), passes value to each `block.get_recognition_report(c2_value)`

## Test counts as of 2026-05-22 (superseded by [[project_module_audit]] for current status)
- `Test_Block.py` — 95 OK, `Test_Asset.py` — 41 OK, `Test_Region.py` — 50 OK
- `Test_Military.py` — 83 OK (incl. _get_artillery_stats category filter + combat_range + combat_state + c2_efficiency)
- `Test_Mobile.py` — 54 OK (incl. task filter for air_defense_volume + combat_range; AUTO_CANNONS; GUNS Anti_Air exclusion)
