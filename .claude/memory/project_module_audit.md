---
name: project-module-audit
description: Completed module audit (2026-08-16) — where to find it and what to do next
metadata: 
  node_type: memory
  type: project
  originSessionId: 54069b25-fc3b-495d-81bb-9efd11133381
  modified: 2026-08-17T09:21:29.279Z
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

## Remaining 17 (16 errors + 1 fail) — genuinely deeper, not mechanical

1. **`Test_Air_Route_Manager.py`: `TestEdge`(2)/`TestThreatAA`(3+1 fail)/`TestRoutePlanner`(9) — a stale, duplicate legacy test suite.** The file has TWO test suites for the same `Edge`/`ThreatAA`/`RoutePlanner`/`Path`/`PathCollection` classes: `GPT_TestModule` (lines ~27-1035, passes 22/22, matches the current API) and a second block from line ~1076 to EOF (`TestThreatAA`/`TestWaypoint`/`TestEdge`/`TestPath`/`TestPathCollection`/`TestRoutePlanner`) written against an older/incompatible shape of the same API — wrong positional-arg order (`n_edge, path_id, path_collection` vs test's `n_edge, path_collection, path_id`), missing `time_to_inversion`/`change_alt_option` args on `calcPathWithoutThreat`/`calcPathWithThreat`/`_handle_threat_crossing`/`_handle_threat_avoidance`, and two methods the test expects (`Edge.intersects_threat`, `Edge.calculate_danger`) that don't exist on production `Edge` at all (that logic lives on `ThreatAA.edgeIntersect` instead). `TestWaypoint`/`TestPath`/`TestPathCollection` in this second block are now fully fixed (see above) since those only needed constructor-arg fixes; the remaining 14+1 need either a careful signature-by-signature rewrite or deleting the block as pure duplication of `GPT_TestModule`. **Needs a user decision before touching further** — this is real effort, not a 1-line fix.
2. **`Test_Region.test_get_region_intelligence_efficiency_returns_mean`** — not a bug, it's open design decision #5 from `00_Sintesi.md`: `Military.intelligence()` was deliberately left commented out in favor of `get_c2_efficiency()`, but `Region.py` and this one test still assume it exists. Leave until the user decides to implement or delete it.

## Next session — first task

The user was asked how to proceed on the remaining 17 (point 1 above, `Test_Air_Route_Manager.py`'s stale duplicate suite) and chose to stop and defer the decision — **start the next session by asking which of these 3 options the user wants**, unless they've already said so at the top of the new conversation:
- **Rewrite**: go through `TestEdge`(2)/`TestThreatAA`(3+1 fail)/`TestRoutePlanner`(9) signature-by-signature to match the current `RoutePlanner`/`Edge`/`ThreatAA` API (real effort — positional-arg order differs, some params are altogether missing from the test calls, and 2 test methods expect production methods that don't exist at all: `Edge.intersects_threat`/`Edge.calculate_danger`).
- **Delete**: drop the whole stale block (`TestThreatAA`/`TestWaypoint`/`TestEdge`/`TestPath`/`TestPathCollection`/`TestRoutePlanner`, lines ~1076-EOF) since `GPT_TestModule` in the same file already covers the same classes correctly (22/22) — would lose `TestWaypoint`/`TestPath`/`TestPathCollection`'s now-passing coverage too unless first confirmed as pure duplicates of what `GPT_TestModule` already checks.
- **Stop and verify first**: hold before any further change; let the user (re-)review what's already been committed, optionally re-run the suite themselves, before deciding.

Point 2 (`Test_Region` / `Military.intelligence()`) is a separate, already-understood open design decision (#5 in Fase 2's list) — no action needed until the user tackles Fase 2 generally.

## Fase 2 — still not started

The 9 open design decisions in `00_Sintesi.md` (fate of `Structure.py`, Production/Storage/Transport/Urban rewrite, which Route/Edge/Waypoint implementation is canonical — see point 1 above, `Threat`/`Sphere`/`Hemisphere`/`Volume` vs `Cylinder`, `Military.intelligence()` — see point 2 above, `Manager.py` vs `Scenario_Manager`/`CommandControl` as the real DWM entry point, `Coalition.py`, `Classi.py`, `visualizer.py`) are all still open and untouched.
