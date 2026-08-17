---
name: military-resources-assigner-stato-implementazione
description: "Stato attuale di get_aircraft_mission e funzionalità correlate, inclusi fix recenti"
metadata: 
  node_type: memory
  type: project
  originSessionId: 54069b25-fc3b-495d-81bb-9efd11133381
  modified: 2026-08-16T16:06:50.899Z
---

**Stato al 2026-03-14:** Implementazione completa e stabile.

**Funzionalità di get_aircraft_mission:**
- Filtra aerei per requisiti performance (`_check_mission_requirements`) e usability
- Calcola `reduction_ratio_missions` se `missions_needed > max_missions`
- `_reduce_target_data`: interpolazione lineare ponderata per priorità (Opzione A):
  `multiplier = reduction_ratio + weight * (1.0 - reduction_ratio)`
  con guard esplicite per `ratio <= 0` (azzera tutto) e `ratio >= 1` (no modifica)
- Entry result include: `aircraft_model`, `loadout`, `score`, `aircraft_per_mission`, `missions_needed`, `derating_factor`
- `derating_factor = 1.0 - reduction_ratio_missions` (0.0 = fully compliant, >0 = derated)
- `aircraft_per_mission` usa divisione ceiling: `(total + missions - 1) // missions`

**Tabelle output:**
- Terminale (W=130): colonne Aircraft, Loadout, Score, AC/Miss, Missions, Derating
- PDF: stesse colonne, Derating colorata con `plt.cm.RdYlGn(1.0 - derating_factor)`
- Titolo include info disponibilità aerei (modello e quantità)

**Why:** Dopo fix bug formula quadratica che aumentava quantità target ad alta priorità.
**How to apply:** Se si modificano formule di riduzione, mantenere la logica di interpolazione lineare e i guard per ratio 0/1.

## Rinominato in Air_Resources_Assigner.py
Il modulo `Logic/Military_Resources_Assigner.py` è stato rinominato `Logic/Air_Resources_Assigner.py` (i nomi di funzioni/costanti sotto restano validi sotto il nuovo nome file).

**Public API:** `get_aircraft_mission(task, aircraft_availability, mission_requirements, target_data, max_aircraft_for_mission, max_missions, directive)` → `{'fully_compliant': [...], 'derated': [...]}`. Ogni entry: `{'aircraft_model': str, 'loadout': str, 'score': float}`, ordinata per score decrescente.

**directive values:** `'performance_high'(1,0)`, `'performance'(0.75,0.25)`, `'balanced'(0.50,0.50)`, `'economy'(0.25,0.75)`, `'economy_high'(0.10,0.90)`

- `_REFERENCE_COST_K = 303_000.0` — costante di normalizzazione per il fattore costo
- `_reduce_target_data`: con un solo target, `weight=1.0` → `qty = round(qty*ratio*2)`; con ratio=0.5 la quantità resta invariata (atteso)
- `_check_mission_requirements`: check `altitude_min` è `lo_altitude_min <= req_altitude_min`
- Logger paths: `_LOGGER_MRA = "Code.Dynamic_War_Manager.Source.Logic.Air_Resources_Assigner.logger"` + `_LOGGER_LO`, `_LOGGER_AWD`, `_LOGGER_AD`

**Bug import risolto (2026-08-16):** `Air_Resources_Assigner.py` importava una classe `Campaign_State` morta e mai usata da `Context/Rinomina_Campaign_State.py` con un path rotto (`from Dynamic_War_Manager....` invece di `Code.Dynamic_War_Manager....`) — questo rendeva il modulo e `Test_Air_Resources_Assigner.py` non importabili. Rimosso l'import morto; vedi [[project_module_audit]] per il quadro completo. Nota: `Rinomina_Campaign_State.py` NON va cancellato, vedi [[project_rinomina_campaign_state]].
