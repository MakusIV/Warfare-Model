---
name: project-fase2-design-decisions
description: "Fase 2 design decisions from 00_Sintesi.md's 9-item list — user's answers, verified against code, as they come in (started 2026-08-21)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 10d17acb-ff9b-4def-a1c6-03a74b239958
  modified: 2026-08-21T11:07:35.894Z
---

Context: [[project_module_audit]] Fase 1 is fully done (2315 tests, 0 errors). Fase 2 is the 9 open design decisions listed in `Analysis/Modules/00_Sintesi.md` under "Decisioni di design che servono da te prima di poter procedere" — explicitly scoped as "conversazione con te, non codice" (their outcome shapes Fase 3's actual rewrite work, not itself implementation). The user is answering them incrementally across messages; this memory accumulates the answers as they land.

**How to apply:** once all 9 are answered, fold the resolutions into `Analysis/Modules/00_Sintesi.md` itself (append resolution notes to each numbered item, don't rewrite the original findings) so the doc doesn't drift from what's actually decided — not done yet, waiting for the full set. Until then, this memory is the source of truth for what's been decided.

## Decision 1 — `Structure.py`: stay in roadmap?
**Answer (2026-08-21): YES, stays in roadmap — needs to be developed** (not deprecated). Currently not instantiable (`Structure.py:46,55` — misaligned positional args to `super().__init__()`, `super.checkParam` missing parens), zero test coverage, no concrete subclass uses it today. Scope of what `Structure` should actually represent wasn't specified yet — that's Fase 3 design work when it's actually tackled, not decided here.

## Decision 2 — `Production`/`Storage`/`Transport`/`Urban.py`: rewrite following `Military.py`?
**Answer (2026-08-21): YES, rewrite following Military.py's pattern**, with a specific logistics model spec from the user (verified against current code, matches exactly):
- Core mechanism: `Resource_Manager` (`Code/.../Component/Resource_Manager.py`), a component every `Block` owns (`Block.py:107` — `self._resource_manager = Resource_Manager(block=self)`, constructed unconditionally in `Block.__init__`).
- Resources are represented by the `Payload` data class (`DataType/Payload.py`) — fields `goods`, `energy`, `hr`, `hc`, `hs`, `hb` (confirmed in `Payload.__init__`). `hs`/`hc`/`hb` are the specialized military-resource fields the user referred to.
- `Military`, `Production`, `Storage`, `Transport`, `Urban` all derive from `Block`, so all inherit `Resource_Manager` as a component (confirmed: `Production`/`Storage`/`Transport`/`Urban` all declare `class X(Block):`).
- Each `Block` has its own internal consumption (`resources_to_self_consume`, a `Payload`, lazily evaluated) and its own storage (`warehouse`, a `Payload`) for resources produced internally (`actual_production`) and/or received from other Blocks.
- Via `Resource_Manager`, a `Block` becomes a client/server network node: `server`/`clients` are `Dict[str, Block]`; exchange happens through `receive(payload)` (adds to warehouse) and a request/distribute mechanism that draws from `warehouse` (confirmed methods exist: `receive`, a "consume resources from warehouse based on request" method, a distribution method that computes delivery from `warehouse.copy()`).
- Role split per the user: `Military` — combat Block, may produce specialized military resources (`hs`/`hc`/`hb`); `Production` — dedicated to resource production; `Transport` — dedicated to resource transport; `Urban` — urban context, primarily human-resource (`hr`) production. Each still has its own internal consumption and storage capacity regardless of role.

**Concrete gap found while verifying (not yet raised by the user, flag for Fase 3):** `Military.__init__` (`Block/Military.py:52`) takes `(mil_category, name, side, description, category, sub_category, functionality, value, region)` and calls `super().__init__(...)` directly — no `block` param. `Production`/`Storage`/`Transport`/`Urban.__init__` (all four, same shape) instead take `(block: Block, mil_category, name, side, description, category, sub_category, functionality, value, acp, rcp, payload, region)` — a redundant leading `block: Block` param that makes no sense once the class already inherits `Block` (likely a leftover from a pre-refactor composition-based design, same vintage as other stale-since-refactor code found in the audit), plus `acp`/`rcp`/`payload` params `Military` doesn't have at all. "Rewrite following Military.py" therefore means an actual constructor rewrite to drop the stray `block` param and align with Military's shape, not just filling in stub method bodies.

## Decision 3 — Route/Edge/Waypoint: which implementation is canonical?
**Answer (2026-08-21, user flagged uncertainty — "se non ricordo male... ma potrei sbagliarmi"):**
- **Air side: keep `Air_Route_Manager.py`'s own local `Route`/`Edge`/`Waypoint` classes as-is** — it works (22/22 in `GPT_TestModule`, see [[project_test_air_route_manager_mismatches]]), no change.
- **Ground side: `Ground_Route_Manager.py` needs the equivalent developed.** User's recollection was that it currently only has a Dijkstra algorithm, and suspected `Tactical_Evaluation.py` already uses `DataType.Edge`/`DataType.Waypoint` in some functions, suggesting those might be the right base for Ground instead of new local classes.

**Verified against code (corrects the recollection on both points):**
1. `Ground_Route_Manager.py` already has its own local `Waypoint`/`Edge`/`NavigationGraph` classes (lines 10-71+), not just a bare Dijkstra function — simpler than Air's (2D/3D distance + road-slope logic, no threat-avoidance recursion). Spotted in passing: `Edge.__repr__` references `self.slope`, which is never set as an attribute anywhere in the class (would `AttributeError` if `__repr__` is ever called) — a Fase 1/4-style mechanical bug, not touched, just noted for whenever this file is worked on.
2. `Tactical_Evaluation.py` imports `DataType.Waypoint`/`DataType.Edge` (lines 20-21) but **never actually uses them anywhere else in the file** — no instantiation, not even used as a type hint elsewhere. Dead imports, same pattern as other dead imports found in Fase 1 — not real, working usage. This matches `00_Sintesi.md` decision #3's own finding that `DataType.Edge` is "rotta e mai istanziata" (`Edge.py:32-33`, `self.calcLenght(self)` typo — wrong method name plus a stray `self` arg).

**Net effect:** there is currently no real, working consumer of `DataType.Edge`/`Waypoint` anywhere in the codebase — so choosing them as Ground's canonical base isn't backed by existing functional usage the way the user recalled. **Not yet finalized** — the user should decide, with this correction in hand, between: (a) give `Ground_Route_Manager.py` its own local classes too (mirroring the "keep what works" philosophy already applied to Air), or (b) migrate/fix `DataType.Edge`/`Waypoint` and make both Air and Ground (and `Tactical_Evaluation`, if it ever needs one) converge on those instead. Recommendation if asked: (a), for the same reason Air's local classes were kept — they'd be new, working code instead of resurrecting a broken, currently-unused one.

## Decision 4 — Threat geometry: `Cylinder` vs `Threat`/`Sphere`/`Hemisphere`/`Volume`
**Answer (2026-08-21): `Cylinder` is confirmed as the model to use now.** Matches `00_Sintesi.md`'s own finding that `Cylinder` already "won" in practice (`Mobile.air_defense_volume()`, `Air_Route_Manager.ThreatAA` both use only `Cylinder`; `Threat` is structurally broken/never instantiated, `Volume`'s signature was never aligned to its real callers). User confirms real-world AA threat geometry is more complex than a cylinder, but treats a more accurate geometric model as a **future upgrade**, not part of the current work. `Threat`/`Sphere`/`Hemisphere`/`Volume` are effectively deprecated for now (not deleted yet — that's a separate cleanup decision, not raised here).

## Decision 5 — `Military.intelligence()` / `Region.get_region_intelligence_efficiency()`
**"Superato"** — already resolved in a prior part of this same session, before Fase 2 started: `Region.get_region_intelligence_efficiency()` and its 2 tests deleted (commit `7a5fa679`), `Military.get_c2_efficiency()` confirmed as the sole metric. See [[project_module_audit]].

## Decisions 6-9 — not yet answered
Still open: #6 (`Manager.py` vs `Scenario_Manager.CommandControl` — real DWM orchestrator), #7 (`Coalition.py`), #8 (`Classi.py`), #9 (`visualizer.py`). Wording is in `Analysis/Modules/00_Sintesi.md` lines 70-73.
