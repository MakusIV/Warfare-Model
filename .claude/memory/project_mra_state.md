---
name: Military_Resources_Assigner - stato implementazione
description: Stato attuale di get_aircraft_mission e funzionalità correlate, inclusi fix recenti
type: project
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
