---
title: "Command"
type: project-module
tags: [package-python, command-control, c2, dwm, architecture]
created: 2026-09-18
updated: 2026-09-25
code_paths: [Code/Dynamic_War_Manager/Source/Command/]
related_decisions: ["[[c2-hierarchy-design]]", "[[gerarchia-unita-militari]]"]
related: ["[[context-state]]", "[[logic-decision]]"]
---

## Scopo

`Command/` è il nuovo package (stateful, distinto dal `Logic/` stateless) che ospiterà la gerarchia
C2 a due livelli concordata in [[c2-hierarchy-design]]: `C2_Manager` (globale, uno per side),
`C2_Region_Manager` (regionale, uno per coppia side/region), `Theater_Session_Manager` (arbitro di
campagna sopra entrambi i side), `Session`/`Session_Mission_Planner`. **Nessuno di questi esiste
ancora** — il package è nato il 2026-09-18 con un solo file, `Command_Types.py`, i tipi dato
condivisi che il resto del package userà una volta costruito.

## File inclusi

| File | Righe | Contenuto |
|---|---|---|
| `Command_Types.py` | ~50 | `RegionInfoReport` (dataclass) |
| `__init__.py` | 0 | Vuoto, per convenzione (v. `Asset/`, `Block/`, `Component/__init__.py`) |

## Stato attuale

### `RegionInfoReport` — implementato (TASK 2 / Fase A, 2026-09-18)

Snapshot "(*) INFO" di pag. 3 del PDF sorgente (`Analysis/Document/Prospetto:Moduli.Analisi.e.Decisioni.pdf`):
priority, meteo, block/asset state, route, limes, logistic center, combat power center,
warehouse, production, morale. Campi:

```python
@dataclass
class RegionInfoReport:
    region_name: str
    side: str
    date: date
    time: time
    priority: Dict[str, List[BlockItem]]
    meteo: List[Dict]
    block_state: List[Dict]
    routes: Dict[str, Route]
    limes: List[Limes]
    logistic_center: Optional[Point2D]
    combat_power_center: Dict[str, Dict[str, Point2D]]
    warehouse: Payload
    production: Payload
    morale: float
```

Costruito da `Region.build_info_report(side, date, time) -> RegionInfoReport` (in
[[context-state]]), puro orchestratore: assembla i campi da metodi `Region` già esistenti e
testati (`get_priority_lists_by_mil_category`, `get_meteorological_reports`, `get_recon_reports`,
`routes`, `limes`, `calc_strategic_logistic_center`, `calc_combat_power_center`,
`calc_total_warehouse`, `calc_total_production`, `get_region_morale`) — nessun calcolo proprio.

**Scelta di import**: `Command_Types.py` importa `Region`/`BlockItem` solo sotto `TYPE_CHECKING`
(gli annotation sono stringhe grazie a `from __future__ import annotations`), perché `Region.py`
importa `RegionInfoReport` a livello di modulo — senza questo accorgimento sarebbe un ciclo
di import diretto. `Region.py` può quindi importare `Command.Command_Types` in testa al file
senza problemi, a differenza del pattern di lazy-import-dentro-funzione usato altrove nel
progetto per rompere cicli (v. [[testing-conventions]] per il workaround usato invece per
Aircraft/Vehicle/Ship).

### Non ancora costruito

`C2_Manager.py`, `C2_Region_Manager.py`, `Theater_Session_Manager.py`, `Session.py`,
`Session_Mission_Planner.py` — tutto il resto della gerarchia C2 descritta in
[[c2-hierarchy-design]]. Moduli correlati altrettanto non ancora costruiti in altri package:
`Context/Theater.py`, `Logic/Strategical_Analysis.py`, `Logic/Session_Simulator.py`.

**Proposta 2026-09-25, non ancora decisa** (v. [[gerarchia-unita-militari]]): due file aggiuntivi
in questo package, `Formation.py` (livello intermedio ricorsivo fra `Military` e il C2 regionale,
livello storico Corpo/Divisione/Brigata come attributo, non sottoclasse) e `C2_Node.py` (base
comune per `C2_Manager`/`C2_Region_Manager`/`Formation`, protocollo proponi/approva generico). Se
accettata, va progettata **insieme** a `C2_Manager.py`/`C2_Region_Manager.py`, non dopo.

## Copertura test

`Test_Command_Types.py` (2 test): verifica che `RegionInfoReport` mantenga tutti i campi passati
al costruttore e che sia una dataclass pura (nessun metodo proprio oltre a quelli generati).

## Decisioni architetturali rilevanti

- [[c2-hierarchy-design]] — design della gerarchia C2 e layout del package, di cui questo è il
  primo pezzo concreto
