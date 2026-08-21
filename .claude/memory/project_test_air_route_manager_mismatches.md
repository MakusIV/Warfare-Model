---
name: project-test-air-route-manager-mismatches
description: "RESOLVED (2026-08-21) — all mismatches below were fixed in commit 9460733c. Kept as a record of the diagnosis/fix rationale, not an open task."
metadata: 
  node_type: memory
  type: project
  originSessionId: 10d17acb-ff9b-4def-a1c6-03a74b239958
  modified: 2026-08-21T08:43:22.485Z
---

**Status: DONE.** Fixed in commit `9460733c` (2026-08-21): `TestThreatAA`/`TestEdge` repaired, `TestRoutePlanner` rewritten, 4 redundant/dead tests deleted (`TestThreatAA.test_calcMaxLenghtCrossSegment`, `TestEdge.test_calculate_danger`, `TestEdge.test_intersects_threat`, `TestRoutePlanner.test_calcRoute`). Verified: `Test_Air_Route_Manager.py` now 48/48 green; project-wide suite 2317 tests, down to the single pre-existing `Test_Region`/`Military.intelligence()` error (see [[project_module_audit]] point 2, a separate open Fase 2 design decision, not touched by this fix). `GPT_TestModule` (22/22) was left untouched per the user's explicit instruction — its threat-placement scenarios are deliberate algorithm-edge-case coverage, not duplication.

The breakdown below is the diagnosis that drove the fix (kept for reference if this code regresses or the approach needs revisiting) — it no longer describes the current state of the file.

**Context:** part of the remaining-17 test failures from [[project_module_audit]] Fase 1. `Test_Air_Route_Manager.py` has TWO test suites for the same classes (`Edge`, `ThreatAA`, `RoutePlanner`, `Path`, `PathCollection`, `Waypoint`): `GPT_TestModule` (lines ~28-1035, 22/22 pass) and a legacy block (`TestThreatAA`/`TestWaypoint`/`TestEdge`/`TestPath`/`TestPathCollection`/`TestRoutePlanner`, lines ~1076-1848) written against an older API shape.

**Important user correction (2026-08-20):** `GPT_TestModule`'s 22 tests are NOT redundant/deletable — they deliberately place `ThreatAA` (threat cylinders) at specific positions/sizes designed to trigger particular edge-case behaviors of the recursive path-search algorithm. The user previously identified specific critical conditions (related to threat-cylinder position/size) where the path-search algorithm fails, but doesn't remember the exact conditions anymore — do not touch or judge `GPT_TestModule` as duplicate. The legacy block is a separate, real rewrite-or-delete decision (see [[project_module_audit]] point 1) — this memory documents precisely what's broken in it, verified by reading production code and actually running the suite (not guessed from stale notes).

## Verified counts (2026-08-20, actually run via `.direnv/python-3.12/bin/python3 -m unittest ... -v`)
52 tests total in this file → **36 pass, 15 errors, 1 failure**. This file is the sole source of the project's residual 16 errors+1 failure.
- `GPT_TestModule`: 22/22 pass.
- `TestWaypoint` (4/4), `TestPath` (3/3), `TestPathCollection` (4/4): all pass.
- `TestEdge`: 2/4 pass (`test_init`, `test_getSegment3D` pass — **the `Edge` constructor itself has no mismatch**, correcting an earlier, wrong assumption in prior session notes about constructor arg order).
- `TestThreatAA`: 0/4.
- `TestRoutePlanner`: 1/11 pass (only `test_excludeThreat`; 10 broken, not 9 as previously estimated).

## TestThreatAA (production: `ThreatAA`, `Air_Route_Manager.py:32-116`)
- `test_init` (test:1093, prod:40) — **stale expected value**: expects `max_altitude=80`; production computes `cylinder.bottom_center.z + cylinder.height` = 120 with current `Cylinder` geometry (`Cylinder.bottom_center == center`, confirmed in `DataType/Cylinder.py:33`).
- `test_edgeIntersect` (test:1096, prod:43-58) — treats 2nd return value as iterable (`len(...)`); production returns a `Segment3D` (no `__len__`).
- `test_innerPoint` (test:1106, prod:60-64) — passes extra tolerance arg `innerPoint(point, 0.1)`; production signature is `innerPoint(self, point)` only.
- `test_calcMaxLenghtCrossSegment` (test:1115, prod:66) — passes 4 args including a `segment`; production wants only `(aircraft_speed, aircraft_altitude, time_to_inversion)`.

## TestEdge (test:1159-1205)
- `test_calculate_danger` (test:1190) — `Edge.calculate_danger` doesn't exist anywhere in `Code/` (grepped).
- `test_intersects_threat` (test:1200) — `Edge.intersects_threat` doesn't exist; equivalent logic lives on `ThreatAA.edgeIntersect(edge)` (`Air_Route_Manager.py:43`), not on `Edge`.

## TestRoutePlanner (test:1340-1626, production `RoutePlanner` 437-1474) — 10/11 broken
Recurring root cause: **`path_id` and `path_collection` are positionally swapped** in test calls vs. current production signatures (production: `..., n_edge, path_id, path_collection, ...`; test: `..., n_edge, path_collection, path_id, ...`), compounded by newer required params the test never supplies (`aircraft_altitude` in `calcPathWithThreat`, `intersection`/`max_recursion`/`debug` with no defaults in `_handle_threat_crossing`, `aircraft_time_to_inversion` in `calcRoute`).
- `test_calcPathWithoutThreat_no_threat`/`_with_threat` (test:1425-1456, prod:665-683) — swap + missing `change_alt_option` (real traceback: `TypeError: missing 1 required positional argument: 'change_alt_option'`).
- `test_calcPathWithThreat_no_threat`/`_with_crossable_threat`/`_with_uncrossable_threat` (test:1469-1523, prod:751-770) — swap + entirely missing `aircraft_altitude` param, shifting every later arg by one slot.
- `test_handle_threat_crossing` (test:1536-1542, prod:879-901) — swap + missing `aircraft_altitude`, `intersection`, `max_recursion`, `debug` (real traceback confirmed: `TypeError: ... missing 3 required positional arguments: 'intersection', 'max_recursion', and 'debug'`).
- `test_handle_threat_avoidance_altitude_change`/`_go_around` (test:1566-1598, prod:1122-1142) — swap + one extra trailing string arg (`"calcPathWithoutThreat"`) with no matching current param (real traceback confirmed: `TypeError: ... takes 19 positional arguments but 20 were given`). `_altitude_change` variant also patches `MockCylinder.getIntersection` while `setUp` (test:1348) actually constructs a real `Cylinder` — the patch has zero effect on the instance used.
- `test_firstThreatIntersected` (test:1401-1415, prod:604-635) — double issue: mock returns a plain list where production expects an object with `.p1`/`.p2` (→ `AttributeError`); and separately, production now returns a **tuple** `(complete_intersection, first_threat)` while the test treats the result as just `first_threat`.
- `test_calcRoute` (test:1613-1623, prod:447-558) — mocks `RoutePlanner.calcLenghtPath`, a method that **doesn't exist in production** (grepped); also omits `aircraft_time_to_inversion`, a required positional param of `calcRoute`.
- `test_excludeThreat` (test:1369-1385, prod:562-602) — **the only green test** in this block; signature and behavior still match production.

## Four mismatch categories (for scoping a future rewrite)
1. `path_id`/`path_collection` positional order swap — nearly all of `TestRoutePlanner`.
2. New required params the test never passes (`aircraft_altitude`, `intersection`, `max_recursion`, `debug`, `aircraft_time_to_inversion`, `change_alt_option`).
3. Methods/attributes removed or moved (`Edge.intersects_threat`, `Edge.calculate_danger`, `RoutePlanner.calcLenghtPath` — gone; `edgeIntersect` moved from `Edge` to `ThreatAA`).
4. Stale expected values / return shapes (`max_altitude` 80 vs 120, `edgeIntersect` no longer list-like, `firstThreatIntersected` now returns a tuple, `innerPoint`/`calcMaxLenghtCrossSegment` slimmed-down signatures).

**How to apply:** `TestEdge`/`TestThreatAA` are small, targeted fixes (a handful of lines each). `TestRoutePlanner` is the heavy lift — 10 methods, most with more than one overlapping problem. When the user resumes this (their stated intent, not yet scheduled), this file has the concrete per-test fix list; no need to re-derive it from scratch. Do not delete or merge with `GPT_TestModule` — see the correction above.
