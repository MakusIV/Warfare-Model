---
name: project-worktree-pythonpath-test-gotcha
description: "Running the test suite inside a linked git worktree (.claude/worktrees/...) produces false test failures on this project, because absolute imports resolve through PYTHONPATH back to the main checkout instead of the worktree. Discovered 2026-09-18."
metadata:
  node_type: memory
  type: project
  originSessionId: e3d24744-9f42-483d-baad-7eb621d37d49
  modified: 2026-09-18T08:02:42.970Z
---

**Symptom:** a test that should pass given the actual code on disk in a worktree fails instead, with an error that matches the *old*, pre-edit logic (old log message format, old exception type) — as if the edited file were never loaded. Adding a `print()` at the top of the edited function shows nothing in the test output, even though the function is definitely reached (the log line for the exception it raises does appear).

**Root cause:** this codebase uses absolute imports everywhere, e.g. `from Code.Dynamic_War_Manager.Source.Context.Campaign_State import CampaignState` (see [[project_key_modules]]/module layout), alongside plain relative-style imports like `from Context.Campaign_State import CampaignState` used inside the `Source/` tree itself. The shell's `PYTHONPATH` (set to `/home/marco/Sviluppo/Warfare-Model/Code:/home/marco/Sviluppo/Warfare-Model`, i.e. the **main checkout**, not any worktree) means Python can resolve the same physical module under **two different dotted names** — `Context.Campaign_State` (found via cwd, inside whichever worktree you're running from) and `Code.Dynamic_War_Manager.Source.Context.Campaign_State` (found via `PYTHONPATH`, always the **main checkout**, regardless of which worktree's tests you're actually running). These become two separate entries in `sys.modules`, each with its own class objects, and whichever one some *other* already-imported module reached for first is the one that ends up bound where you don't expect it — so a test running inside a worktree can end up exercising the **main checkout's stale code** instead of the worktree's edits, silently.

**How to confirm:** check the logger name in a WARNING/ERROR log line raised by the suspect code — a fully-qualified name like `Code.Dynamic_War_Manager.Source.Context.Campaign_State` (vs. the short `Context.Campaign_State`) is the tell. Or just diff the two files (`<worktree>/Code/.../X.py` vs `/home/marco/Sviluppo/Warfare-Model/Code/.../X.py`) — if they differ and the test behaves like the main-checkout version, this is it.

**How to apply:** don't trust a failing (or passing) test run launched from inside `.claude/worktrees/<agent>/...` on this project as ground truth. Either (a) apply/copy the worktree's changes onto a branch in the **main checkout** (`/home/marco/Sviluppo/Warfare-Model`, where `PYTHONPATH` and cwd agree) and run the suite there, or (b) override `PYTHONPATH` to point at the worktree before running tests inside it. Option (a) is what was actually done to unblock [[project_c2_hierarchy_design]] TASK 1 on 2026-09-18: extracted the worktree's diff with `git diff`, applied it with `git apply` on a fresh branch in the main checkout, then ran the full suite there (2519 OK).

**How to apply more generally:** this same trap would hit *any* future cloud/local agent work left in a `.claude/worktrees/*` directory on this repo, on any of the 3 machines — the absolute-import + hardcoded-`PYTHONPATH` combination is a project-wide characteristic, not specific to one module.
