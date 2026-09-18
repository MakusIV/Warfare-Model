"""
MODULE Command_Types

Tipi dato condivisi dal package `Command/` -- la gerarchia C2 (v. project memory
project_c2_hierarchy_design.md / wiki/decisions/c2-hierarchy-design.md). `Command/` è stateful
(C2_Manager, C2_Region_Manager, Theater_Session_Manager, Session/Session_Mission_Planner -- non
ancora costruiti), distinto dal `Logic/` stateless.

`RegionInfoReport` è il primo pezzo concreto: lo snapshot "(*) INFO" di pag.3 del PDF sorgente
(Analysis/Document/Prospetto:Moduli.Analisi.e.Decisioni.pdf) di cui un C2_Region_Manager ha
bisogno per il proprio ciclo analizza/pianifica. È assemblato interamente da metodi pubblici già
esistenti e testati di `Region` (v. `Region.build_info_report`) -- questo modulo definisce solo
la forma dei dati, nessuna logica di calcolo.

Import di `Region`/`BlockItem` solo sotto `TYPE_CHECKING`: a runtime non serve (gli annotation
sono stringhe grazie a `from __future__ import annotations`), il che evita completamente il ciclo
di import con `Context.Region` (che a sua volta importa `RegionInfoReport` da qui).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date as _date, time as _time
from typing import TYPE_CHECKING, Dict, List, Optional

from sympy import Point2D

from Code.Dynamic_War_Manager.Source.DataType.Route import Route
from Code.Dynamic_War_Manager.Source.DataType.Limes import Limes
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload

if TYPE_CHECKING:
    from Code.Dynamic_War_Manager.Source.Context.Region import BlockItem


@dataclass
class RegionInfoReport:
    """Snapshot di tutto ciò che il C2 di un side deve sapere su UNA Region, per pag.3 del PDF
    sorgente ("(*) INFO": priority, meteo, block/asset state, route, limes, logistic center,
    combat power center, warehouse, production, morale). Costruito da
    `Region.build_info_report(side, date, time)` -- questa dataclass non calcola nulla da sola.
    """
    region_name: str
    side: str
    date: _date
    time: _time
    priority: Dict[str, List['BlockItem']]
    meteo: List[Dict]
    block_state: List[Dict]
    routes: Dict[str, Route]
    limes: List[Limes]
    logistic_center: Optional[Point2D]
    combat_power_center: Dict[str, Dict[str, Point2D]]
    warehouse: Payload
    production: Payload
    morale: float
