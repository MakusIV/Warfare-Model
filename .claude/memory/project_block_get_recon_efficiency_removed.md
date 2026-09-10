---
name: project-block-get-recon-efficiency-removed
description: "RESOLVED 2026-09-10: Block.get_recon_efficiency() removed as redundant with Military.get_recon_efficiency() (polymorphism already made Block's version dead code for Military instances); Test_Block.py updated; full suite 2311/OK"
metadata: 
  node_type: memory
  type: project
  originSessionId: 26fe0114-6467-43e3-9ec1-1dbee64a03d7
  modified: 2026-09-10T14:38:13.098Z
---

**User request (2026-09-10):** `Block.get_recon_efficiency()` looked redundant with `Military.get_recon_efficiency()` and should be evaluated for removal.

**Finding:** the two implementations differed (Block: filtered by `asset.category == "Reconnaissance"`, mean; Military: filtered by `asset.role == Asset_Role.RECONNAISSANCE.value`, median), but since `Military(Block)` and Python resolves `self.get_recon_efficiency()` by the instance's runtime type, `Block.get_recognition_report()`'s internal call already resolved to `Military`'s override for every `Military` instance — Block's version was fully shadowed dead code for the only production path that mattered (`Region.get_region_recon_efficiency` only ever queries `BlockCategory.MILITARY` blocks). Block itself had a self-left TODO comment already flagging this (`#Nota: è iimplementata in Military: da togliere!?`).

**Only behavior change:** non-Military `Block` subclasses (`Production`, `Storage`, `Urban`, `Transport` — none of which have Reconnaissance-category assets, none queried by `get_region_recon_efficiency`) now get `recon_efficiency: None` in `get_recognition_report()` instead of a fake `0.0`.

**Action taken:** removed `get_recon_efficiency()` from `Block.py`; removed 4 dedicated tests and updated 1 assertion (`None` instead of `0.0`) in `Test_Block.py`. `Military.py`, `Region.py` unchanged (not needed). `Rinomina_Campaign_State.py:54` reference is docstring-only, no action needed (see [[project_rinomina_campaign_state]]).

**Verification:** full suite `python3 -m unittest discover -s Code/Dynamic_War_Manager/Source/Test -p "Test_*.py"` → 2311 tests, OK (skipped=5). Was 2315 before (2315-4=2311, matches expected test removal exactly).

**How to apply:** if similar "duplicate method on base vs. subclass" questions come up (Block vs. Military/other subclasses), check polymorphic dispatch first — a base-class method called only through `self.` inside another base-class method is often already fully shadowed by a subclass override and safe to delete, provided no other subclass genuinely needs the base behavior.
