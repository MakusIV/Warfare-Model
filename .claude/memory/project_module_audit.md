---
name: project-module-audit
description: Completed module audit (2026-08-16) — where to find it and what to do next
metadata: 
  node_type: memory
  type: project
  originSessionId: 54069b25-fc3b-495d-81bb-9efd11133381
  modified: 2026-08-21T09:54:07.915Z
---

**What happened:** After a ~7 week pause, the user asked for a first phase of deep, per-subsystem analysis before planning further development ("development had been a scatti, no unified view"). Result: 11 subsystem docs in `Analysis/Modules/01_...md`–`11_...md` (Italian, one per logical subsystem, not per file — ~57 files grouped into 11 areas), each produced by a parallel subagent that read the real source and executed the real test suite (not just static reading), plus a consolidated synthesis at **`Analysis/Modules/00_Sintesi.md`**.

**How to apply:** `00_Sintesi.md` is the authoritative, current starting point for anything about project/module status — read it first, not this memory note or older per-module memory bullets, which may be stale relative to it. It contains: a leverage-ranked list of mechanical fixes (cheap, near-zero risk, unblock the most code), 9 open design decisions that need the user's input before further work, and a 4-phase roadmap.

**Headline finding:** most passing unit tests never construct real objects — they mock/stub around construction — so the codebase is less mature than the test-pass-rate suggests. Almost nothing instantiates with default params today (`Mobile.checkParam` bug alone blocks every `Vehicle`/`Ship`/`Aircraft`). The Logic/ decision pipeline (`Scenario_Manager`/`Strategical_Evaluation`/`Tactical_Evaluation`/`Air_Resources_Assigner`) isn't wired together and 3 of its 4 modules aren't even importable. The Lua↔DCS exchange layer described in `Analysis/Document/WM_Software_Structure.pdf` doesn't exist in code at all (zero occurrences of `mission_param`/`mission_result`) — that and the decision pipeline are net-new engineering, not bugfixing.

**Triage/cleanup done alongside the audit (2026-08-16):** deleted 5 pre-refactor dead files (`Region old.py`, `Military copy.py`, `Resource_Manager old.py`, `Hemisphere2.py`, plus `Rinomina_Campaign_State.py` which was then **restored** — see [[project_rinomina_campaign_state]], not dead, reserved for future reuse). Left `Coalition.py` alone on user request (same dead-file profile, undecided). Fixed a project-wide import-path bug (`from Dynamic_War_Manager.Source...` missing the `Code.` prefix) across 12 files — this was masking real bugs from ever surfacing because the tests that exercise those classes dodge real imports via mocking (see [[feedback_circular_import_workaround]]).

## Fase 1 — DONE (2026-08-17, session 3)

The user chose Fase 1. All items from `00_Sintesi.md`'s leverage-ranked table applied and verified:
- #1/#2 dead `Aircraft` imports removed from `Aircraft_Weapon_Data.py:5` and `Ground_Weapon_Data.py:5` — this alone broke the Aircraft↔Aircraft_Data↔Aircraft_Loadouts↔Aircraft_Weapon_Data circular import that was blocking Asset-Air + half of Asset-Ground-Naval.
- #3 `Sea_Asset_Type.FAST_ATTACK` → `.CORVETTE` fixed in both `Initial_Context.py:101` and `Actual_Context.py:70`.
- #5 `Logger(..., class_name='')` fixed in `Tactical_Evaluation.py:42` (→ `'Tactical_Evaluation'`) and `Strategical_Evaluation.py:28` (→ `'Strategical_Evaluation'`).
- #6 `GROUND_Military_VEHICLE_ASSET` → `GROUND_MILITARY_VEHICLE_ASSET` typo fixed in `Strategical_Evaluation.py:17`.
- New (not in the original table, surfaced only after #1/#2 unblocked deeper imports): `Tactical_Evaluation.py:583` used `Block` as a type hint with no import at all (`NameError` at module load) — added `from Code.Dynamic_War_Manager.Source.Block.Block import Block`.
- `requirements.txt` was missing `tabulate` (used for real by `Vehicle_Data.py:4709`, a genuine dependency gap, not dead code) — added to requirements.txt and installed in the venv.

**Bonus fix, unplanned but critical:** `Test_Mobile.py` pre-injected fake `sys.modules` entries for `Vehicle_Data`/`Ground_Weapon_Data`/the Aircraft chain **at module import time** (top-level code) instead of scoped to its own test run. Since `unittest discover` imports every `Test_*.py` file during collection *before* running any test, this silently poisoned `sys.modules` for the entire test session — corrupting unrelated files like `Test_Ground_Weapon_Data.py` and `Test_Aircraft_Data.py` (which passed 100% in isolation but errored under `discover`). Fixed by moving the fake-module registration into `setUpModule()`/`tearDownModule()` using `patch.dict(sys.modules, ...)`, scoping it to just Test_Mobile's own run. Confirmed Mobile itself no longer needs any of the fakes to import (Vehicle_Data/Ground_Weapon_Data are resolved lazily inside its methods, not at module level) — the Aircraft-chain part of the old workaround was dropped entirely as dead weight.
Also fixed 2 test-vs-production mismatches surfaced by the unblocking: `Test_Resource_Manager.MockBlock` was missing `.name` (added); `Test_Aircraft_Weapon_Data.TestIsWeaponIntroduced` asserted `is_weapon_introduced(unknown_model, year)` returns `False`, but production code deliberately returns `True` for unknown weapons (documented in an inline comment) — test renamed/fixed to match the documented intent instead of changing production behavior.
`Test_Air_Route_Manager.py`'s `TestEdge`/`TestPath`/`TestPathCollection`/`TestThreatAA` classes (not `GPT_TestModule`, which is separate and already 22/22) had `Edge(...)`/`ThreatAA(...)` constructor calls missing positional args (`order_position`, `min_detection_time`) — fixed 12 call sites; unblocked `TestWaypoint`, `TestPath`, `TestPathCollection` fully and 2/4 of `TestEdge`.

**Net result:** full suite went from 1088 tests collected / 47 errors (with several files failing to import at all, undercounting real test methods) to **2321 tests collected / 16 errors + 1 failure** (run via `python3 -m unittest discover -s Code/Dynamic_War_Manager/Source/Test -p "Test_*.py"`).

## Remaining 17 (16 errors + 1 fail) — ALL RESOLVED as of 2026-08-21

**Both points below are now fixed.** Project-wide suite: **2315 tests, 0 errors, 0 failures** (commits `9460733c`, `7a5fa679`).

1. ~~**`Test_Air_Route_Manager.py`: `TestEdge`(2)/`TestThreatAA`(3+1 fail)/`TestRoutePlanner`(9) — a stale, duplicate legacy test suite.**~~ RESOLVED 2026-08-21 (commit `9460733c`) — see [[project_test_air_route_manager_mismatches]] for the full diagnosis/fix.
2. ~~**`Test_Region.test_get_region_intelligence_efficiency_returns_mean`**~~ RESOLVED 2026-08-21 (commit `7a5fa679`) — this was open design decision #5 below. **User confirmed the decision**: `Military.get_c2_efficiency()` is the sole command/intelligence metric; `Military.intelligence()` stays unimplemented (commented out). Deleted `Region.get_region_intelligence_efficiency()` (no production callers — `Region.get_c2_efficiency()` was already the one production code uses, via `get_recon_reports`) and its 2 tests.

## Fase 2 — 8 of 9 design decisions still open

Design decision #5 (`Military.intelligence()`) is now resolved, see point 2 above. The remaining 8 open design decisions in `00_Sintesi.md` (fate of `Structure.py`, Production/Storage/Transport/Urban rewrite, which Route/Edge/Waypoint implementation is canonical — see point 1 above, `Threat`/`Sphere`/`Hemisphere`/`Volume` vs `Cylinder`, `Manager.py` vs `Scenario_Manager`/`CommandControl` as the real DWM entry point, `Coalition.py`, `Classi.py`, `visualizer.py`) are all still open and untouched.
