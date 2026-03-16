"""
 MODULE DA VEDERE SE MANTENERE O INSERIRE LE INFO IN INITAL_CONTEXT

methods for allocating military resources: aircraft, vehicle, ecc.

"""

from __future__ import annotations  # must be the very first statement

import copy
from typing import Dict, List, Optional, Tuple

from Code.Dynamic_War_Manager.Source.Context.Context import (
    AIR_TASK, 
    AIR_TO_AIR_TASK, 
    AIR_TO_GROUND_TASK, 
    Air_Asset_Type as at, 
    Ground_Vehicle_Asset_Type as ag,
    Sea_Asset_Type as asea
)
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Loadouts import (
    AIRCRAFT_LOADOUTS,
    get_aircrafts_quantity,
    loadout_cost,
)
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import Aircraft_Data
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger


logger = Logger(module_name=__name__, class_name='Initial_Context').logger


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------



_ASSET_AVAILABILITY: Dict[str, Tuple[float, float]] = {   
        'air': {at.FIGHTER.value: {
                    'F-14A Tomcat': 100,
                    'F-14B Tomcat': 100,
                    'F-15C Eagle': 100,
                },
                at.FIGHTER_BOMBER.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                },
                at.ATTACKER.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                }, 
                at.BOMBER.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                }, 
                at.HEAVY_BOMBER.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                }, 
                at.RECON.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                }, 
                at.AWACS.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                }, 
                at.TRANSPORT.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                }, 
                at.HELICOPTER.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                },
        }, 
        'ground': {
                ag.TANK.value: {
                    'F-14A Tomcat': 100,
                    'F-14B Tomcat': 100,
                    'F-15C Eagle': 100,
                    },
                ag.ARMORED.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                },
                ag.MOTORIZED.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                },
                ag.ARTILLERY_FIXED.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                },
                ag.ARTILLERY_SEMOVENT.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                },
                ag.SAM_BIG.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,                    
                },
                ag.SAM_MEDIUM.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100                   
                },
                ag.SAM_SMALL.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100                    
                },
                ag.AAA.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100                    
                },
                ag.EWR.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100                    
                },
        },
        'sea': {asea.CARRIER.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                    
                },
                asea.DESTROYER.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                    
                },
                asea.CRUISER.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                    
                },
                asea.FRIGATE.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                    
                },
                asea.FAST_ATTACK.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                    
                },
                asea.SUBMARINE.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                    
                },
                asea.AMPHIBIOUS_ASSAULT_SHIP.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                    
                },
                asea.TRANSPORT.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                    
                },
                asea.CIVILIAN.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                    
                },                
            },
}

_REFERENCE_COST_K: float = 303_000.0