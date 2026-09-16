"""
MODULE Strategical_Evaluation

Data and methods for strategical evaluation. Used by Lead Command & Control.

Livello strategico: aggrega su più regioni e su un intero lato (side); non contiene calcoli su
singole coppie blocco/bersaglio -- quelli sono nel livello tattico, v.
Logic/Tactical_Analysis.py (analisi/raccolta informazioni) e Logic/Tactical_Evaluation.py
(scoring). Gli stub sotto sollevano NotImplementedError: documentano l'architettura voluta
(in particolare l'aggregazione multi-regione) ma non sono ancora implementati.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger

if TYPE_CHECKING:
    from Code.Dynamic_War_Manager.Source.Block.Block import Block
    from Code.Dynamic_War_Manager.Source.Context.Region import Region


# Logger setup
    # CRITICAL 	50
    # ERROR 	40
    # WARNING 	30
    # INFO 	20
    # DEBUG 	10
    # NOTSET 	0
logger = Logger(module_name=__name__, class_name='Strategical_Evaluation').logger


def evaluateTacticalReport(report_list: dict) -> dict:
    """Evaluate priority of tactical reports and resource request. List ordered by priority."""
    raise NotImplementedError("evaluateTacticalReport non ancora implementata")


def evaluateDefensePriorityZone(strategic_priority_list: dict) -> dict:  # defense_priority_list
    """Evaluate priority of strategic zone (Production Zone, Transport Line, Storage Zone ecc, Military) and resource request. List ordered by priority.

    strategic_infrastructure_list: block (name (id), position, area), type (production, transport, storage, Military, urban), importance (VH, H, M, L, VL) sorted by importance
    """
    raise NotImplementedError("evaluateDefensePriorityZone non ancora implementata")


def definePriorityPatrolZone(defense_priority_list, fighter_zone_cover) -> dict:
    """Define the priority patrol zone list for fighter aircrafts.
    Define patrol zone as set of near block covered by single patrol mission.
    """
    raise NotImplementedError("definePriorityPatrolZone non ancora implementata")


def evaluateResourceRequest(report):
    raise NotImplementedError("evaluateResourceRequest non ancora implementata")


def evaluateTargetPriority(target_list: list):
    """Evaluate priority of targets and resource request. List ordered by priority."""
    raise NotImplementedError("evaluateTargetPriority non ancora implementata")


def evaluateTotalProduction(type: str, side: str):  # type: goods, energy, human resource
    """Somma la produzione totale di un lato su più regioni (aggregazione di teatro) --
    v. Region.calc_total_production per il calcolo su una singola regione."""
    raise NotImplementedError("evaluateTotalProduction non ancora implementata")


def evaluateStrategicPriority(block: Block):
    raise NotImplementedError("evaluateStrategicPriority non ancora implementata")


def evaluateTotalTransport(type: str, side: str):  # type: goods, energy, human resource
    raise NotImplementedError("evaluateTotalTransport non ancora implementata")


def evaluateLogisticLineTransport(type: str, trans_from_request, trans_to_request):  # type: goods, energy, human resource
    raise NotImplementedError("evaluateLogisticLineTransport non ancora implementata")


def evaluateTotalStorage(type: str, side: str):  # type: goods, energy, human resource
    """Somma lo stoccaggio totale di un lato su più regioni (aggregazione di teatro) --
    v. Region.calc_total_warehouse per il calcolo su una singola regione."""
    raise NotImplementedError("evaluateTotalStorage non ancora implementata")


def calcCombatPowerCentrum(side: str, region: Region):
    """Centro di potenza di combattimento di un lato aggregato su più regioni --
    v. Region.calc_combat_power_center per il calcolo su una singola regione."""
    raise NotImplementedError("calcCombatPowerCentrum non ancora implementata")
