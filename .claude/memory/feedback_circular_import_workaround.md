---
name: feedback-circular-import-workaround
description: How to write tests around the unresolved Aircraft/Vehicle/Ship circular import — stub classes and sys.modules pre-injection patterns
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 54069b25-fc3b-495d-81bb-9efd11133381
  modified: 2026-08-16T16:08:04.039Z
---

**Unresolved circular import:** `Aircraft.py → Aircraft_Data → Aircraft_Loadouts → Aircraft_Weapon_Data → Aircraft.py`. `Vehicle.py` and `Ship.py` also trigger this chain (via `Ground_Weapon_Data → Aircraft`). Root cause and fix options are tracked in [[project_module_audit]] (Asset-Air subsystem).

**Why this matters for testing:** `Vehicle`, `Ship`, `Aircraft` cannot be imported directly in any test file — the import will fail or deadlock partway through initialization.

**How to apply — two validated workaround patterns:**

1. **Stub classes** (used in `Test_Military.py`): create `_Vehicle = type('Vehicle', (), {})` at module level, then `mock.__class__ = _Vehicle` on mocks. `validate_class(mock, "Vehicle")` uses MRO name → works with stubs. Also: `Block.assets` setter validates `isinstance(v, Asset)` → bypass with `block._assets = {...}` directly in tests rather than `block.assets = {...}`.

2. **sys.modules pre-injection** (used in `Test_Mobile.py`, more thorough): pre-inject the whole Aircraft import chain into `sys.modules` as `MagicMock` *before* any real import runs. Fake `Vehicle_Data` module: `_vd_mod.Vehicle_Data = _FakeVehicleData` (class with `_registry = {}`). Fake `Ground_Weapon_Data` module: `_gwd_mod.GROUND_WEAPONS = _FAKE_GW` (mutable dict, mutated per test). Real `Ship_Data`/`Ship_Weapon_Data` can be imported directly (no circular deps there). Build a `_MobileStub` class with `air_defense_volume = Mobile.air_defense_volume` and `combat_range = Mobile.combat_range` bound onto it. `assertIsInstance(cyl, Cylinder)` fails under this setup (dual module path) — use `type(cyl).__name__ == 'Cylinder'` instead.

Both patterns mean the "passing" test suites for these classes never actually exercise the real, fully-imported module chain — see [[project_module_audit]] for what this hid (an unrelated import-path bug went undetected for a long time).
