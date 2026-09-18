---
name: project-c2-hierarchy-design
description: "Core architecture decision: two-level C2 (global C2_Manager per side + regional C2_Region_Manager per side/region) driving analysis/planning/targeting, session-based DCS-vs-synthetic execution model, and the 'indirizzo strategico' (per-region Attack/Maintain/Defense/Retreat orientation). Source: user's PDF Analysis/Document/Prospetto:Moduli.Analisi.e.Decisioni.pdf (pag.1-5), analyzed 2026-09-17."
metadata: 
  node_type: memory
  type: project
  originSessionId: 75641a65-377f-4984-9a07-06c50099c3cb
  modified: 2026-09-18T08:02:25.478Z
---

**Status (2026-09-18): design agreed and unchanged. TASK 1 (per-side doctrine fix) DONE, verified, committed & pushed on branch `feature/c2-doctrine-per-side-fase-a`. TASK 2 (Fase A: RegionInfoReport/Meteo_Analysis/limes) NOT started.** User uploaded `Analysis/Document/Prospetto:Moduli.Analisi.e.Decisioni.pdf` (pag.1-5) describing a C2 hierarchy; an Opus-effort-high subagent analyzed it against the current codebase and produced an implementation proposal, then the user corrected/answered open questions in the same 2026-09-17 session. This memory records the **agreed design**, superseding the raw subagent proposal on every point the user corrected.

## TASK 1 (per-side doctrine fix) — DONE 2026-09-18, resumable on any machine
The remote cloud agent handed the work on 2026-09-17 never pushed anything (no PR, no remote branch — `gh pr list` came back empty, and the branch didn't exist on origin either). Its process had died mid-work, but its edits survived uncommitted in a local git worktree at `.claude/worktrees/agent-a3441fac4736db9bb` on the `osboxes` machine. Recovered 2026-09-18: extracted the diff (`Context/Region.py`, `Context/Campaign_State.py`, `Test/Test_Campaign_State.py` — exactly the per-side scope described below, nothing from TASK 2), applied it on a fresh `feature/c2-doctrine-per-side-fase-a` branch off `main` in the **main checkout** (not the worktree — see [[project_worktree_pythonpath_test_gotcha]] for why testing must happen there), ran the full suite: **2519 tests, OK (skipped=5), real exit code 0**. Committed and pushed to origin.

**If you're on a different machine and this branch isn't visible yet:** `git fetch origin` then `git checkout feature/c2-doctrine-per-side-fase-a` (or `git pull` if already checked out elsewhere). No PR was opened (`gh` isn't installed on `osboxes`) — either install `gh` and open one, or open it manually via the GitHub web UI, or just keep building TASK 2 on top of this branch and open one PR for both at the end.

Implementation actually delivered:
1. **Per-side targeting doctrine fix**: `Region._attack_weight`/`_weight_priority_target` changed from scalar to `Dict[str, ...]` keyed by `'Blue'`/`'Red'`; the plain `attack_weight`/`weight_priority_target` properties replaced by `get_attack_weight(side)`/`set_attack_weight(side, value)`/`get_weight_priority_target(side)`/`set_weight_priority_target(side, value)` (a property can't take a `side` arg) plus a `_validate_belligerent_side` guard. `update_military_priorities` indexes by the existing `side` parameter. `Campaign_State.py` serialize/restore + schema docstring updated to per-side dicts (no back-compat shim for old scalar-format snapshots — none exist in production). `Test_Campaign_State.py`'s `_RegionStub` mock and affected tests updated to match. No other production callers referenced the old scalar property (checked via grep), so this is a clean, complete migration.

## TASK 2 (Fase A) — scope, not started
2. **Fase A**: public `Region.limes` property (was private-only); new placeholder `Logic/Meteo_Analysis.py` (deterministic stub, explicitly not random, shaped to match `Air_Resources_Assigner`'s `mission_requirements['usability']`) wired into the previously-empty `Region.get_meteorological_reports`; new `Command/` package with `Command_Types.py::RegionInfoReport` dataclass; new `Region.build_info_report(side) -> RegionInfoReport` assembling it from existing tested `Region` methods. New tests for all of it.

**Lesson learned for handing work to a remote/cloud agent on this project:** it has no memory access and works from an inline briefing only, and (as this episode showed) its process can die mid-task with work never pushed — always check the actual git remote state (`git fetch` + `git branch -a` + `git log`) rather than trusting a PR description or a prior session's assumption that it finished. If nothing appears on origin, check for an abandoned local worktree under `.claude/worktrees/` before redoing the work from scratch.

## Hierarchy
- **`C2_Manager`** (global): one per side (2 total for a 2-belligerent conflict) = "lo stato maggiore", responsible for the whole conflict area for that side.
- **`C2_Region_Manager`** (regional): one per (side, region) pair = 2×N for N regions.
- Both levels share the same 5-function shape: analyze state → strategic/tactical evaluation → define indirizzo strategico → select targets → plan air/ground/sea missions.
- **Targeting protocol**: regional C2 proposes a targeting list to the global C2; global C2 approves, cancels, or modifies it (a modification-*request*-back-to-regional loop is a possible refinement, explicitly left "da valutare" — not decided).

## "Indirizzo strategico" (strategic orientation) — now concretely scoped
Per-region, per-domain (air/ground/sea) orientation toward **Attack / Maintain / Defense / Retreat**, driven by: morale, loss statistics by asset type/role, production/reserve state, etc. This is the same concept already flagged in [[feedback_combat_power_action_selection]] as "a per-action priority vector feeding a later tactical decision layer" — that memory's open idea is now confirmed as the PDF's "indirizzo strategico", and the two should be implemented together.

## Session model (DCS vs. synthetic) — resolves/updates [[project_campaign_temporal_model_dcs_vs_synthetic]]
- **Discriminant DCS/virtual session**: presence/absence of one or more human-player slots (binary, operational — not asset count).
- **Asset/mission scale**: virtual sessions carry far more missions/assets than DCS sessions, purely for DCS-engine computational reasons (limited by the host PC), not a fixed 3:6 session-count ratio treated as load-bearing.
- **Time offset between DCS and virtual sessions is 1-2 hours** (correction — the subagent's initial read of "1-20h" from the PDF was wrong, confirmed by user).
- **Execution is interleaved and player-driven, not a pre-baked calendar**: after the player finishes a DCS mission and exits, the main campaign module runs, asks the player whether to end-early any remaining missions scheduled for that game-day, then checks whether synthetic/virtual sessions are due (before the player's next session, or after their last one for the period) and executes them via the simulation module. After each virtual session, all state info is updated before proceeding (to the next player session, or to run another virtual session). **This replaces the earlier idea of a fixed `Session_Mission_Planner.build_session_calendar()` schedule with an event-driven scheduler keyed off real play-session boundaries.**
- **C2 cycle runs before AND after every single session** (analyze → plan → execute → analyze → ...), not once per campaign time-unit.
- **Sessions are shared between sides** (one session contains both belligerents' missions, matching how the actual DCS game session works). An optional encoding/hiding of enemy-side info inside a shared session (fog-of-war at the session-data level) is explicitly deferred to a later version.

## Confirmed cleanup (user approved, item 6)
- Delete `Context/Coalition.py` (doesn't compile, unused) — no salvage needed.
- Delete `Logic/Scenario_Manager.py`'s `CommandControl` class, but **first extract its docstring** (it already lists air/ground/sea operation levels + goods/energy/human-resource levels — likely the literal content of "indirizzo strategico") into wherever `StrategicOrder`/strategic-doctrine data ends up living.
- Rename or eliminate `Manager.py` to free up the `C2_Manager` name (it's currently a broken 106-line stub wrongly identified in the wiki as "the C² Planner").
- `Analysis/WIKI_LLM_SIMULATION/wiki/concepts/c2-planner.md` needs updating: it references `Manager.py` as the C² Planner and `Military_Resources_Assigner.py` (renamed to `Air_Resources_Assigner.py` long ago) — both stale.

## Proposed module layout (from the subagent's analysis, not yet built)
New `Command/` package (stateful, distinct from stateless `Logic/`): `C2_Region_Manager.py`, `C2_Manager.py`, `Session_Mission_Planner.py`, `Session.py`, `Command_Types.py`. Plus `Context/Theater.py`, `Logic/Strategical_Analysis.py` (facts, pendant to `Tactical_Analysis.py`), `Logic/Meteo_Analysis.py`, `Logic/Session_Simulator.py`. `Strategical_Evaluation.py` (currently all-stub) keeps only the true scoring functions; 4 of its 11 stubs (`evaluateTotalProduction/Transport/Storage`, `calcCombatPowerCentrum`) are facts and belong in the new `Strategical_Analysis.py` instead.

**Low-risk starting point (unblocked by any open question)**: build `RegionInfoReport` — the PDF's pag.3 `(*) INFO` list (priority, meteo, block/asset state, route, limes, logistic center, combat power center, warehouse, production, morale) maps almost 1:1 to `Region` methods that already exist and are tested. Only gaps: `Meteo_Analysis` (today `Region.get_meteorological_reports` is an empty shell) and a public `limes` property.

**Known architecture conflict to fix before C2 implementation**: `Region._attack_weight`/`_weight_priority_target` (targeting doctrine) are currently per-Region, not per-side — two opposing C2s acting on the same region would clobber each other's doctrine. Must become side-keyed first.

## Not yet decided
- Exact negotiation-loop mechanics for the global C2 modifying/rejecting a regional proposal.
- Where session-shared-but-side-owned missions get merged into one physical DCS/virtual session (a campaign-level arbiter above both sides' C2_Manager, per subagent's hypothesis — not confirmed by user yet).
- `Campaign_State`'s `mission_id`-keyed persistence vs. the new session-as-turn-unit vocabulary — proposed additive fix (add session-level keying, don't rename) not yet confirmed.

**How to apply:** any future work building `Command/`, `Strategical_Evaluation.py`, `Session_Mission_Planner`, or revisiting the DCS/synthetic temporal model must start from this memory, not from the raw PDF or the superseded subagent draft. See also [[project_region_tactical_refactor_plan]] for the tactical-layer foundation this builds on.
