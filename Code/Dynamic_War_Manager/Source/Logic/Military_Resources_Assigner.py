"""
 MODULE Military Resources Assigner
 
methods for allocating military resources: aircraft, vehilce, ecc.

"""

#from typing import Literal
#VARIABLE = Literal["A", "B, "C"]

import sys
import os
import random
from __future__ import annotations
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np
from Code.Dynamic_War_Manager.Source.Context.Context import BLOCK_ASSET_CATEGORY, GROUND_ACTION, GROUND_COMBAT_EFFICACY
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Loadouts import AIRCRAFT_LOADOUTS, get_aircrafts_quantity
from dataclasses import dataclass
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import Aircraf_Data
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger


logger = Logger(module_name = __name__, class_name = 'Military_Resources_Assigner').logger


mission_type = 'Strike'

aircraf_availability = [
            {'model': 'F-4E Phantom II', 'Loadout': 'Strike', 'quantity': 10},
            {'model': 'F-15E Strike Eagle', 'Loadout': 'Iron Bomb Strike', 'quantity': 15},
            {'model': 'A-10A Thunderbolt II', 'Loadout': 'Precision Strike', 'quantity': 5},
            {'model': 'B-52H Stratofortress', 'Loadout': 'Heavy Strike Mk-84', 'quantity': 3},
            {'model': 'F-16C Block 52d', 'Loadout': 'Strike', 'quantity': 20},
        ],

mission_requirements = { 
    "cruise": {
                "speed": 850, "reference_altitude": 7000,
                "altitude_max": 12000, "altitude_min": 300,
                "range": 1000,
            },
    "attack": {
                "speed": 950, "reference_altitude": 3000,
                "altitude_max": 8000, "altitude_min": 300,
                "range": 500,
            },
    "usability": "day",
}

target_data = {
                    'Soft':     {   
                                    'big': 3,
                                    'med': 5,
                                    'small': 10
                                },
                    'Armored':  {
                                    'big': 2,
                                    'med': 4,
                                    'small': 10
                                },
                    'Structure':{
                                    'big': 3,
                                    'med': 6,
                                    'small': 12
                                },
            }

max_aircraft_for_mission = 9

max_missions = 2 # se >1 le mssioni vengono inserite in una coda la quale dovrà tenere conto se gli asset sono ancora disponibili

def get_aircraft_for_mission(aircraft_availability, mission_requirements, target_data, max_aircraft_for_mission, max_missions):
    
    candidate_aircraft = []

    # Loadout check: per ogni aereo disponibile, verificare se il loadout soddisfa i requisiti di missione (velocità, altitudine, range). Se sì, aggiungere alla lista dei candidati.
    for aircraft in aircraft_availability:
        loadout = AIRCRAFT_LOADOUTS.get(aircraft['model'], {}).get(aircraft['Loadout'], {})
        if not loadout:
            logger.warning(f"Loadout {aircraft['Loadout']} for model {aircraft['model']} not found in AIRCRAFT_LOADOUTS.")
            continue
        loadout_idoneity = True
        for key in ['cruise', 'attack']:
            if not (loadout[key]['speed'] >= mission_requirements[key]['speed'] and
                loadout[key]['reference_altitude'] >= mission_requirements[[key]]['reference_altitude'] and
                loadout[key]['altitude_max'] >= mission_requirements[[key]]['altitude_max'] and
                loadout[key]['altitude_min'] <= mission_requirements[[key]]['altitude_min'] and 
                loadout[key]['range'] >= mission_requirements[[key]]['range'] ):                
                    loadout_idoneity = False
                    break
        
        if not loadout_idoneity:
            logger.info(f"Aircraft {aircraft['model']} with loadout {aircraft['Loadout']} does not meet mission requirements (cruise or attack params).")
            continue

        if loadout['usability'] != mission_requirements['usability']:
            logger.info(f"Aircraft {aircraft['model']} with loadout {aircraft['Loadout']} does not meet usability requirements.")
            continue

        aircrafts_quantity = get_aircrafts_quantity(aircraft['model'], aircraft['Loadout'], target_data)
        
        # adesso devi valutare le quantità disponibili e il numero di missioni previsto in aircraft_quantity con gli argomenti per determinare gli aerei ed i loadouts da scegliere


        """"
        candidate_aircraft.append({
            'model': aircraft['model'],
            'Loadout': aircraft['Loadout'],
            'quantity': min(aircraft['quantity'], aircrafts_quantity)
        })
    """