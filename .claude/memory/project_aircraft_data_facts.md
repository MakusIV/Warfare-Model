---
name: project-aircraft-data-facts
description: "Aircraft_Data and Aircraft_Loadouts API facts, scoring quirks, known bugs, logger mocking requirements"
metadata: 
  node_type: memory
  type: project
  originSessionId: 54069b25-fc3b-495d-81bb-9efd11133381
  modified: 2026-08-16T16:07:22.480Z
---

## Aircraft_Data
- `combat_score(task, loadout)` — no target info; `combat_score_target_effectiveness(task, loadout, target_type: List, target_dimension: List)` — with target
- `get_normalized_intercept_speed_score(...)` — scoring per intercettazione
- `combat_score_target_effectiveness` is NOT bounded to [0,1] — loadout component alone can exceed 1 (e.g. F-14A Phoenix Fleet Defense returns ~2.6)
- `get_list_of_aircrafts(side, task, target_distribuition, role, route_length, route_speed)` — **BUG BLA3**: sorting key raises `StopIteration` for aircraft senza loadout del task (`next(iter({}))`)
- `AIRCRAFT_ROLE = [e.value for e in Air_Asset_Type]` — lista di stringhe; `Air_Asset_Type.FIGHTER_BOMBER.value = 'Fighter_Bomber'`
- Logger mock per Aircraft_Data richiede anche `Aircraft_Weapon_Data.logger` (ha `logger.debug` non implementato in Logger class)
- `get_weapon_score_target(model, target_type: List, target_dimension: List)` — vuole LISTE, non stringhe

## Aircraft_Loadouts
- `loadout_target_effectiveness_by_distribuition(aircraft, loadout_name, target_dist, route_length, route_speed)` — `target_dist` è dict `{type: {perc_type, perc_dimension: {dim: pct}}}`
- `get_aircrafts_quantity(aircraft_model)` e `loadout_cost(aircraft_model, loadout_name)` — disponibili in Aircraft_Loadouts
- Bug corretto: score accumulation usava `score *= perc_dimension` sul totale cumulativo; ora usa `dim_score` locale per ogni (type×dim)
- Bug corretto: `get_weapon_score_target` veniva chiamato con stringhe invece di liste → passare `[target_type]`, `[target_dimension]`
- Tu-160 Strategic Strike usa `Kh-101` (6+6); Tu-95MS Strategic Strike usa `Kh-55` (6)
- `Kh-55`/`Kh-101` aggiunti a `MISSILES_ASM` in `Aircraft_Weapon_Data.py` con efficiency per Soft/Armored/Hard/Structure/Air_Defense/infrastrutture

**Circular import note:** questi tre moduli + `Aircraft.py` formano un ciclo non risolto — vedi [[feedback_circular_import_workaround]].
