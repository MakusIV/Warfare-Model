---
name: project-campaign-persistence
description: Target_Status_History and Campaign_State module facts — snapshot/persistence layer for campaign state
metadata: 
  node_type: memory
  type: project
  originSessionId: 54069b25-fc3b-495d-81bb-9efd11133381
  modified: 2026-08-16T16:07:34.129Z
---

## Target_Status_History
- Module: `Context/Target_Status_History.py` — class `TargetStatusHistory`
- Stores `get_recognition_report(region_c2_recon_efficiency=1.0)` snapshots per block per mission
- Represents blocks as military targets (NOT operational state); formerly `Campaign_History.py` / `CampaignHistory`
- `Block.get_status_report()` has been removed — callers use `get_recognition_report(region_c2_recon_efficiency=1.0)` directly
- Test: `Test_Target_Status_History.py` — 44 tests OK (confirmed 2026-08-16 after import-path fix, see [[project_module_audit]])

## Campaign_State
- Module: `Context/Campaign_State.py` — class `CampaignState`
- Stores full campaign state snapshots (Region, Block, Asset, Route) indexed by mission_id
- Serializes: block class/name/side/priority, State (health, success_ratio), Resource_Manager (warehouse, actual_production, clients_ids, server_ids), all Asset payloads + model + class_name, Route edges (danger_level, speed)
- `restore(mission_id, regions)` applies snapshot to live objects: Region.attack_weight, BlockItem.priority, Block/Asset State.health, Payload fields, Route.Edge danger_level/speed
- Write API: `add_campaign_snapshot(atomic)`, `add_region_snapshot`, `add_block_snapshot` (granular)
- Read API: `get_mission`, `get_region_snapshot`, `get_block_snapshot`, `get_block_history`, `get_field_trend`, `get_asset_history`
- Persistence: `save(path)` / `CampaignState.load(path)` — JSON UTF-8
- Test: `Test_Campaign_State.py` — 78 tests OK (stub objects, no live Asset imports; confirmed 2026-08-16 after import-path fix)

**Do not confuse with** `Context/Rinomina_Campaign_State.py`, an older/different `Campaign_State` class reserved by the user for future reuse — see [[project_rinomina_campaign_state]].
