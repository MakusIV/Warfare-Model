"""
 MODULE Strategical_Evaluation
 
 Data and methods for strategical evaluation. Used by Lead Command & Control

"""

#from typing import Literal
#VARIABLE = Literal["A", "B, "C"]

from Utility import get_membership_label
from Manager import regions
import Context
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np

from Dynamic_War_Manager.Source import Mil_Base



def getTacticalReport():
    """ request report to any Mil_Base"""
    """ scorre elenco Mil_Base:
            aggiunge alla lista di report il report corrente. La lista è ordinata per criticità"""
    tactical_reports = {} # 

    for region in regions:
        for block in region.blocks:
            
            if isinstance(block, Mil_Base):
                report = block.getTacticalReport()
                tactical_reports[region.name][block.name] = report


    pass

def evaluateTacticalReport(report_list):
    """Evaluate priority of tactical reports and resource request. List ordered by priority."""
    # High probaility of attack (our asset is very weak respect wenemy force)
    # asset is very important 

    pass

def evaluateDefencePriorityZone(infrastructure_list):
    """ Evaluate priority of strategic zone (Production Zone, Transport Line, Storage Zone ecc, Mil_Base) and resource request. List ordered by priority."""
    # High probaility of attack (our asset is very weak respect wenemy force)
    pass

def evaluateResourceRequest(report):
    pass

def evaluateTargetPriority(target_list):
    """Evaluate priority of targets and resource request. List ordered by priority """
    pass

def evaluateRecoMissionRatio(side: str, region_name: str|None ):
    """ evaluate ratio of success of reconnaissance mission"""

    pass