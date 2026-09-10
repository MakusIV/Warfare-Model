---
name: project-region-unattributed-dead-code-removal
description: "OPEN 2026-09-10: Region.py has an uncommitted change (removal of old commented-out calc_combat_power_center block) that Claude did not make and the user has not yet confirmed — needs user attention before it's committed"
metadata: 
  node_type: memory
  type: project
  originSessionId: 26fe0114-6467-43e3-9ec1-1dbee64a03d7
  modified: 2026-09-10T14:38:20.852Z
---

During the 2026-09-10 session (removal of `Block.get_recon_efficiency`, see [[project_block_get_recon_efficiency_removed]]), `Code/Dynamic_War_Manager/Source/Context/Region.py` showed up as modified in `git diff` — a large dead commented-out block (`# old` / old `calc_combat_power_center` implementation, ~35 lines) was removed. This was **not** made by Claude in this session: it was already present in the working tree (file mtime ~3h before the change was noticed, well before any Edit tool call touched that file).

**Status:** left as-is, unstaged, **excluded** from the 2026-09-10 commit for the `get_recon_efficiency` removal. Flagged to the user three times in-session; no response yet on whether to keep, investigate, or discard it.

**How to apply:** before committing anything else in this repo, check `git status` on `Region.py` — if this diff is still sitting there, ask the user whether it's intentional (their own edit/IDE autosave) or should be investigated further, rather than assuming either way.
