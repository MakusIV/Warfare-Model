---
name: project-rinomina-campaign-state
description: "Rinomina_Campaign_State.py is reserved for future reuse, NOT dead code — do not delete it"
metadata: 
  node_type: memory
  type: project
  originSessionId: 54069b25-fc3b-495d-81bb-9efd11133381
  modified: 2026-08-16T16:05:34.883Z
---

`Code/Dynamic_War_Manager/Source/Context/Rinomina_Campaign_State.py` defines an old pre-rename `class Campaign_State` (structurally different from the current `CampaignState` in `Context/Campaign_State.py` — old one tracks `_last_mission`, `_asset_availability`, `_global_success_mission_ratio`, `_global_damaged_asset_ratio`, `_state` snapshot dict).

It looks like dead code (not imported anywhere after the only reference — a stale, unused import in `Logic/Air_Resources_Assigner.py` — was removed on 2026-08-16) and shares the same "leftover from pre-refactor path reorg" profile as `Region old.py`, `Military copy.py`, `Resource_Manager old.py`, `Hemisphere2.py` (all deleted 2026-08-16).

**Why it's different: the user explicitly said (2026-08-16) they intend to reuse this module later, by renaming it** — do not delete or treat as cleanup fodder. Its future purpose/target name was not specified yet.

**How to apply:** during the per-subsystem module audit/documentation pass ([[project_module_audit]]), flag this file as "reserved for future use, pending rename" rather than "candidate for deletion." Ask the user before touching it again.
