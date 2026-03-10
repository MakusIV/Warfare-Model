"""
 MODULE Military Resources Assigner
 
methods for allocating military resources: aircraft, vehilce, ecc.

"""

#from typing import Literal
#VARIABLE = Literal["A", "B, "C"]

import sys
import os
import random
import copy
from __future__ import annotations
from typing import Dict, List, Optional
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np
from Code.Dynamic_War_Manager.Source.Context.Context import BLOCK_ASSET_CATEGORY, GROUND_ACTION, GROUND_COMBAT_EFFICACY
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Loadouts import AIRCRAFT_LOADOUTS, get_aircrafts_quantity, loadout_eval
from dataclasses import dataclass
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import Aircraft_Data
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger


logger = Logger(module_name = __name__, class_name = 'Military_Resources_Assigner').logger


mission_type = 'Strike'

aircraf_availability = [
            {'model': 'F-4E Phantom II', 'loadout': 'Strike', 'quantity': 10},
            {'model': 'F-15E Strike Eagle', 'loadout': 'Iron Bomb Strike', 'quantity': 15},
            {'model': 'A-10A Thunderbolt II', 'loadout': 'Precision Strike', 'quantity': 5},
            {'model': 'B-52H Stratofortress', 'loadout': 'Heavy Strike Mk-84', 'quantity': 3},
            {'model': 'F-16C Block 52d', 'loadout': 'Strike', 'quantity': 20},
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
                                    'big': {'quantity': 3, 'priority': 5},
                                    'med': {'quantity': 5, 'priority': 6},
                                    'small': {'quantity': 10, 'priority': 6}
                                },
                    'Armored':  {
                                    'big': {'quantity': 2, 'priority': 3},
                                    'med': {'quantity': 4, 'priority': 3},
                                    'small': {'quantity': 5, 'priority': 5}
                                },
                    'Structure':{
                                    'big': {'quantity': 3, 'priority': 10},
                                    'med': {'quantity': 6, 'priority': 7},
                                    'small': {'quantity': 12, 'priority': 7}
                                },
            }

max_aircraft_for_mission = 9
max_missions = 2 # se >1 le mssioni vengono inserite in una coda la quale dovrà tenere conto se gli asset sono ancora disponibili

aircrafts = Aircraft_Data()

def get_aircraft_for_mission(aircraft_availability: Dict, mission_requirements: Dict, target_data: Dict, max_aircraft_for_mission: int, max_missions: int) -> Dict:
   
    # liste degli aerei con loadout idoneo: 
    # fully_compliant: i target sono serviti con numero aerei e numero missioni sono conformi alle richieste. 
    # derated: i target non possono essere serviti con numero aerei e numero missioni richieste: derating del target
    avalaible_aircraft_list = {'fully_compliant':[], 'derated':[]} 
    
    # Loadout check: per ogni aereo disponibile, verificare se il loadout soddisfa i requisiti di missione (velocità, altitudine, range). Se sì, aggiungere alla lista dei candidati.
    for aircraft in aircraft_availability:
        reduction_ratio_for_aircraft_number = 1
        reduction_ratio_for_mission_number = 1
        loadout_idoneity = False

        if aircraf_availability < max_aircraft_for_mission:
            logger.warning(f"availability of {aircraft['model']}: {aircraft['quantity']} is lower of requested max_aircraft_for_mission({max_aircraft_for_mission}. assigned to max_aircraft_for_mission: {aircraft['quantity']} )")
            mission_derating_for_aircraft_number = aircraf_availability / max_aircraft_for_mission
            max_aircraft_for_mission = aircraft['quantity']            
        
        loadout = AIRCRAFT_LOADOUTS.get(aircraft['model'], {}).get(aircraft['loadout'], {})
        
        if not loadout:
            logger.warning(f"loadout {aircraft['loadout']} for model {aircraft['model']} not found in AIRCRAFT_LOADOUTS.")
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
            logger.info(f"Aircraft {aircraft['model']} with loadout {aircraft['loadout']} does not meet mission requirements (cruise or attack params).")
            continue

        if loadout['usability'] != mission_requirements['usability']:
            logger.info(f"Aircraft {aircraft['model']} with loadout {aircraft['loadout']} does not meet usability requirements.")
            continue
        aircrafts_quantity = get_aircrafts_quantity(model = aircraft['model'], loadout = aircraft['loadout'], target_data = target_data, year = None, max_aircraft_for_mission = max_aircraft_for_mission)
        calculated_missions = aircrafts_quantity['missions_needed']
        calculated_aircraft = aircrafts_quantity['total']

        if max_missions > calculated_missions:
            # il numero di missioni calcolato è superiore a quello consentito nella richiesta
            # quindi devi ridefinire target_data, riducendo gli obiettivi in funzione delle loro priorità
            reduction_ratio_for_mission_number = calculated_missions / max_missions # coefficente di riduzione da applicare al numero di aerei richiesto per singolo target            
            target_data_priority_weight = sum( # sommatoria delle priorità applicate a tutti i target
                                        dim_data['priority']
                                        for _, category_data in target_data.items()
                                        for _, dim_data in category_data.items()
                                        )
            updated_target_data = copy.deepcopy(target_data)

            for _, category_data in updated_target_data.items():
                for _, dim_data in category_data.items():
                    updated_target_data['quantity'] *=  reduction_ratio_for_mission_number * updated_target_data['priority'] / target_data_priority_weight
        # ricalcola le quantità in base alle nuove richieste sui target
        aircrafts_quantity = get_aircrafts_quantity(model = aircraft['model'], loadout = aircraft['loadout'], target_data = updated_target_data, year = None, max_aircraft_for_mission = max_aircraft_for_mission)
        calculated_missions = aircrafts_quantity['missions_needed']

        if max_missions > calculated_missions:
            logger.error(f"Error in function logic{calculated_missions}")
            raise ValueError(f"Error in function logic{calculated_missions}")
        
        else:# inserisce l'aereo, il loadout e lo score di questo in una lista                
            # criteri di scelta:    performance -> scegli in base allo score dell'aereo e del loadout
            #                       economy -> sceglie in base 

            aircrafts.combat_score_eval()            
            #swa = 0.6 # score_weight_for_aircraft
            #swl = 0.4 # score_weight_for_loadout            
            #score = loadout_eval(aircraft_name=aircraft['model'], loadout_name=aircraft['loadout']) * swl + 

            if reduction_ratio_for_aircraft_number == 1 and reduction_ratio_for_mission_number == 1:                
                score = loadout_eval(aircraft_name=aircraft['model'], loadout_name=aircraft['loadout']) * reduction_ratio_for_aircraft_number * reduction_ratio_for_mission_number                
                avalaible_aircraft_list['fully_compliant'].extend


            score = loadout_eval(aircraft_name=aircraft['model'], loadout_name=aircraft['loadout']) * reduction_ratio_for_aircraft_number * reduction_ratio_for_mission_number                
            avalaible_aircraft_list['derated'].extend({'aircraft_model': aircraft['model'], 'loadout': aircraft['loadout'], 'score': score})


    return avalaible_aircraft.sort(key = lambda x: x['score'], reverse=True)


        


        """
        target_data = {
                    'Soft':     {   
                                    'big': {'quantity': 3, 'priority': 1},
                                    'med': {'quantity': 5, 'priority': 2},
                                    'small': {'quantity': 10, 'priority': 2}
                                },
                    'Armored':  {
                                    'big': {'quantity': 2, 'priority': 1},
                                    'med': {'quantity': 4, 'priority': 1},
                                    'small': {'quantity': 5, 'priority': 2}
                                },
                    'Structure':{
                                    'big': {'quantity': 3, 'priority': 8},
                                    'med': {'quantity': 6, 'priority': 10},
                                    'small': {'quantity': 12, 'priority': 10}
                                },
            }
        """


        """"
        candidate_aircraft.append({
            'model': aircraft['model'],
            'Loadout': aircraft['Loadout'],
            'quantity': min(aircraft['quantity'], aircrafts_quantity)
        })
        """