---
name: project-wiki-llm-simulation-merge
description: WIKI_LLM_SIMULATION (separate Karpathy-style LLM wiki project) merged into Analysis/WIKI_LLM_SIMULATION/ inside Warfare-Model (2026-08-20)
metadata: 
  node_type: memory
  type: project
  originSessionId: 10d17acb-ff9b-4def-a1c6-03a74b239958
  modified: 2026-08-20T10:03:47.812Z
---

**Decision (2026-08-20):** the user concluded `WIKI_LLM_SIMULATION` (a standalone project implementing Andrej Karpathy's "LLM-maintained wiki" pattern — see its `Istruzioni/Wiki_LLM.txt`) doesn't make sense kept separate from Warfare-Model, since its whole purpose is supporting research for Warfare-Model. Chose simple move now (physically relocate the folder as-is into `Analysis/`, which is already the Warfare-Model Obsidian vault — see [[project_analysis_symlink_decision]]), integrate/reorganize content into the rest of `Analysis/` incrementally later rather than all at once.

**What was done:**
- Copied current-state snapshot (no git history — old repo's commits were explicitly not preserved, per user's choice) from `WIKI_LLM_SIMULATION` (which lived at `/mnt/c/Users/marco/Sviluppo/WIKI_LLM_SIMULATION`, symlinked into WSL2 at `~/Sviluppo/WIKI_LLM_SIMULATION` — same physical-location pattern as the rejected "Option A" for Analysis/Obsidian itself) into `Warfare-Model/Analysis/WIKI_LLM_SIMULATION/`, committed as `9f62e0bb`.
- Excluded the old project's own `.obsidian/` deliberately: inspected its 5 files (`app.json`, `appearance.json`, `core-plugins.json`, `graph.json`, `workspace.json`) and confirmed none of it is anything Claude reads/needs — pure Obsidian UI/workspace state (theme, enabled core plugins, graph-view tag/path coloring, pane layout). Everything Claude actually operates on for the Karpathy-wiki workflow is plain tracked files: `CLAUDE.md` (schema/instructions), `wiki/index.md`, `wiki/log.md`, `wiki/entities/`, `wiki/concepts/`, `wiki/sources/`, `wiki/analyses/` — all copied intact. Copy verified byte-identical via `diff -rq` before committing.
- Removed the local symlink `~/Sviluppo/WIKI_LLM_SIMULATION` and deleted the real Windows-side folder `/mnt/c/Users/marco/Sviluppo/WIKI_LLM_SIMULATION`.
- **GitHub repo `MakusIV/WIKI_LLM_SIMULATION` deleted (2026-08-20).** `gh repo delete` from this session failed: the authenticated `gh` token lacks the `delete_repo` scope (has `gist`, `read:org`, `repo` only), and granting it requires an interactive OAuth flow (`gh auth refresh -h github.com -s delete_repo`) that this environment's Bash tool can't drive (no TTY — same class of limitation as the `sudo` issue noted in [[project_analysis_symlink_decision]]). User deleted it manually via the GitHub web UI instead. Confirmed gone via `gh repo view MakusIV/WIKI_LLM_SIMULATION` → "Could not resolve to a Repository". The move is now fully complete on all fronts (local copy, old symlink, old Windows folder, old GitHub repo).

**How to apply:** `Analysis/WIKI_LLM_SIMULATION/` is now the canonical location for this content — a subfolder inside the same vault as `Analysis/Modules/`, `Analysis/Document/`, etc., not yet reorganized into that taxonomy. Content: `wiki/concepts/` (14 pages on simulation methodology — wargaming, event-driven sim, stochastic sim, etc.), `wiki/entities/` (13 pages — campaign models like JICM/CEM/TLC/TACWAR, RAND Corporation, Philip Sabin), `wiki/sources/` (2 ingested RAW sources), plus `RAW/` (the 2 original source docs, immutable per the Karpathy workflow), `CLAUDE.md` (the wiki's own operating schema — still valid, describes `ingesta`/`query`/`health check` workflows scoped to this subfolder). Future ingestions of new sources into this wiki should continue following that `CLAUDE.md`'s workflow, now just at the new path.
