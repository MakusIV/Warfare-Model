from functools import lru_cache
import sys
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union, Tuple
from Code.Dynamic_War_Manager.Source.Context import Context 
from Code.Dynamic_War_Manager.Source.Asset.Aircraft import Aircraft
from Code.Dynamic_War_Manager.Source.Utility import Utility
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.Utility.Utility import true_air_speed, indicated_air_speed, true_air_speed_at_new_altitude
from sympy import Point3D
from dataclasses import dataclass

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Aircraft_Data')

AIRCRAFT_ROLE = Context.AIR_MILITARY_CRAFT_ASSET.keys()
AIRCRAFT_TASK = Context.AIR_TASK

_INFRA_MIN = sys.float_info.min  # shorthand for near-zero infrastructure dc

# Usato in get_<weapon_type>_score
WEAPON_PARAM = {

    'CANNONS':          {'caliber':         7 / ( 27 * 29 ), # coeff / max value (max ~30mm, BMP-3)
                        'muzzle_speed':     7 / ( 800 * 29 ), # 800 m/s
                        'fire_rate':        8 / ( 300 * 29 ), # 300 rpm 
                        'range':            5 / ( 3000 * 29 ), # 3000
                        'ammo_type':        2 /  ( 29 ),
                        },

    'MISSILES_AAM_RAD': {'warhead':         3 / ( 250 * 36 ), # in kg, ref ~250 kg (AIM-54C)
                        'range':            5 / ( 100 * 36 ), # in km, ref ~50000 m (AIM-54C)
                        'semiactive_range': 7 / ( 15 * 36 ), # in km, ref ~15000 m (AIM-54C)
                        'active_range':     9 / ( 8 * 36 ),  # in km, ref ~8000 m (AIM-54C)                      
                        'max_speed':        9 / ( 3 * 36 ), # in mach 
                        'max_height':       3 / ( 30 * 36 ), # max ~30 km
                        },
    'MISSILES_AAM_INF': {'warhead':         5 / ( 250 * 21 ), # in kg, ref ~250 kg (AIM-54C)
                        'range':            5 / ( 5 * 21 ), # in km, ref ~50000 m (AIM-54C)                        
                        'max_speed':        9 / ( 3 * 21 ), # in mach 
                        'max_height':       2 / ( 30 * 21 ), # max ~30 km
                        },
    
    'MISSILES_ASM':     {'warhead':         7 / ( 150 * 21 ), # in kg, ref 50 kg 
                        'range':            9 / ( 15 * 21 ), # in km, ref 15 km 
                        'max_speed':        5 / ( 300 * 21 ), # in m/s, ref ~300 m/s
                        },

    'ROCKETS':         {'caliber':          3 / ( 125 * 20 ), #in mm, ref 125 mm,  peso: 7/( riferimento: 240 * sommatoria pesi: 3+3+4+3+7=20)
                        'warhead':          3 / ( 5 * 20 ),  # in kg, ref 5 kg  caliber + warhead insieme pesano 6
                        'range':            4 / ( 10 * 20 ), # in km, ref 10 km
                        'warhead_type':     3 / ( 20 ),
                        'speed':            7 / ( 600 * 20 ), # ref 600 m/s
                        },
    
    'MACHINE_GUNS':     {'caliber':         6 / ( 9.14 * 17 ), # coeff / max value (caliber in mm 9.14-> 0.36 "  nato
                        'fire_rate':        9 / ( 500 * 17 ),
                        'range':            2 / ( 1000 * 17 ),
                        },

    'BOMBS':            {'warhead':         1 / 500, # in kg, ref ~500 kg (GBU-43/B MOAB),
                         'weight':          1 / 500} # per le cluster alternativo a warhead non avendo un dato specifico sul peso della testata, ref ~500 kg (GBU-43/B MOAB)

}

# HE: Esplosivo, HEAT: High Explosive Anti Tank (carica cava), 2HEAT: carica a cava doppia, AP: 'Armour Piercing', APFSDS = AP a energia cinetica 
# Usato in get_cannon_score e get_missile_score
WARHEAD_TYPE_PARAM = {
    'HE': 0.2,
    'HEAT': 0.4,
    'AP': 0.2,
    '2HEAT': 0.9,
    'APFSDS': 0.6,
    'FRAG': 0.3
}

# Efficacia di ogni tipo di munizione per tipo di bersaglio (scala 0..1).
# Usato in calc_weapon_efficiency per calcolare l'ammo_factor.
# Per ogni arma si seleziona la munizione migliore disponibile contro il target.
WARHEAD_TYPE_TARGET_EFFECTIVENESS = {
    #                Soft  Armrd Hard  Struc AirDf Airbas Port  Shipy Farp  Strng ship
    'HE':     {'Soft': 1.0,  'Armored': 0.15, 'Hard': 0.5,  'Structure': 0.8,
               'Air_Defense': 0.5,  'Airbase': 0.6, 'Port': 0.6, 'Shipyard': 0.6,
               'Farp': 0.6, 'Stronghold': 0.5, 'ship': 0.4},
    'HEAT':   {'Soft': 0.6,  'Armored': 0.85, 'Hard': 0.6,  'Structure': 0.4,
               'Air_Defense': 0.75, 'Airbase': 0.3, 'Port': 0.3, 'Shipyard': 0.3,
               'Farp': 0.3, 'Stronghold': 0.35, 'ship': 0.65},
    '2HEAT':  {'Soft': 0.6,  'Armored': 1.0,  'Hard': 0.7,  'Structure': 0.45,
               'Air_Defense': 0.85, 'Airbase': 0.35, 'Port': 0.35, 'Shipyard': 0.35,
               'Farp': 0.35, 'Stronghold': 0.4, 'ship': 0.75},
    'AP':     {'Soft': 0.35, 'Armored': 0.7,  'Hard': 0.55, 'Structure': 0.3,
               'Air_Defense': 0.6,  'Airbase': 0.2, 'Port': 0.2, 'Shipyard': 0.2,
               'Farp': 0.2, 'Stronghold': 0.25, 'ship': 0.5},
    'APFSDS': {'Soft': 0.4,  'Armored': 1.0,  'Hard': 0.65, 'Structure': 0.25,
               'Air_Defense': 0.85, 'Airbase': 0.2, 'Port': 0.2, 'Shipyard': 0.2,
               'Farp': 0.2, 'Stronghold': 0.25, 'ship': 0.6},
    'FRAG':   {'Soft': 0.9,  'Armored': 0.05, 'Hard': 0.2,  'Structure': 0.5,
               'Air_Defense': 0.3,  'Airbase': 0.4, 'Port': 0.4, 'Shipyard': 0.4,
               'Farp': 0.4, 'Stronghold': 0.35, 'ship': 0.2},
}

GUIDE_PARAM = {

}
'''
RELOAD_PARAM = {

    'Automatic': 1,
    'Semi_Automatic': 0.7,
    'Manual': 0.4
}
'''


def get_missiles_score(model: str) -> float:
    """
    Returns an effectiveness score for a missile, based on its key parameters and the weights defined in WEAPON_PARAM.

    Restituisce un punteggio di efficacia per un missile, basato sui suoi parametri chiave e sui pesi definiti in WEAPON_PARAM.
    
    :param model: model of missile / il modello del missile da valutare
    :type model: str
    :return: missile's score / punteggio di efficacia del missile, calcolato come somma pesata dei suoi parametri chiave
    :rtype: float
    """
    
    if not isinstance(model, str):
        raise TypeError(f"model is not str, got {type(model).__name__}")    

    weapon_name = 'MISSILES_AAM'    
    weapon = AIR_WEAPONS[weapon_name].get(model)#

    if not weapon:
        weapon_name = 'MISSILES_ASM'
        weapon = AIR_WEAPONS[weapon_name].get(model)#

    else:
        if weapon.get('seeker') == 'radar':
            weapon_name = 'MISSILES_AAM_RAD'
        elif weapon.get('seeker') == 'infrared':
            weapon_name = 'MISSILES_AAM_INF'
    
    if not weapon:
        logger.warning(f"weapon {model} unknow")
        return 0.0


    weapon_power = 0.0

    for param_name, coeff_value in WEAPON_PARAM[weapon_name].items():
        weapon_power +=  weapon[param_name] * coeff_value

    return weapon_power 

def get_bombs_score(model: str) -> float:
    """
    Returns an effectiveness score for a bomb, based on its key parameters and the weights defined in WEAPON_PARAM.

    Restituisce un punteggio di efficacia per una bomba, basato sui suoi parametri chiave e sui pesi definiti in WEAPON_PARAM.
    
    :param model: model of bomb / il modello della bomba da valutare
    :type model: str
    :return: bomb's score / punteggio di efficacia della bomba, calcolato come somma pesata dei suoi parametri chiave
    :rtype: float
    """
    
    if not isinstance(model, str):
        raise TypeError(f"model is not str, got {type(model).__name__}")    
    weapon_name = 'BOMBS'    
    weapon = AIR_WEAPONS[weapon_name].get(model)#
    
    if not weapon:
        logger.warning(f"weapon {model} unknow")
        return 0.0
    bomb_type = weapon.get('type', 'type_not_specified')

    if bomb_type != 'type_not_specified':
        logger.warning(f"weapon_type {model} - type_not_specified")
        return 0.0
    small_structure_efficiency_param = weapon.get('efficiency').get('Structure').get('small')    
    accuracy = small_structure_efficiency_param.get('accuracy', 0.5)
    destroy_capacity = small_structure_efficiency_param.get('destroy_capacity', 0.5)
    weapon_power = 0.0

    if bomb_type == 'Bombs':
        precision_factor = 1.0
        damage_factor = 1.0
        
    elif bomb_type == 'Guided Bombs':
        precision_factor = 1.2
        damage_factor = 1.0
        
    elif bomb_type == 'Cluster_bombs':
        precision_factor = 0.8
        damage_factor = 1.3    
    
    for param_name, coeff_value in WEAPON_PARAM[weapon_name].items():
        param_value = weapon.get(param_name, 0.0)        
        weapon_power +=  param_value * coeff_value
    return weapon_power * accuracy * destroy_capacity * precision_factor * damage_factor

def get_rockets_score(model: str) -> float:
    """
    returns rocket score (same logic as get_missiles_score)

    Args:
        model (str): rocket model

    Returns:
        float: rocket score
    """
    if not isinstance(model, str):
        raise TypeError(f"model is not str, got {type(model).__name__}")

    weapon_name = 'ROCKETS'
    weapon = AIR_WEAPONS[weapon_name].get(model)

    if not weapon:
        logger.warning(f"weapon {weapon_name} {model} unknow")
        return 0.0

    weapon_power = 0.0

    for param_name, coeff_value in WEAPON_PARAM[weapon_name].items():

        if param_name == 'warhead_type':
            
            warhead_type = weapon.get(param_name, 'unknown')

            if warhead_type == 'unknown':
                logger.warning(f"weapon {weapon_name} {model} weapon_warhead_type unknow")
                warhead_value = 0.5  # default value for unknown warhead type
            else:
                warhead_value = WARHEAD_TYPE_PARAM.get(warhead_type)  # default 0.5 if warhead type is unknown

            weapon_power += warhead_value * coeff_value

        else:
            weapon_power +=  weapon[param_name] * coeff_value

    return weapon_power

AIR_WEAPONS = {
   
    'MISSILES_AAM': {
        "AIM-54A-MK47": {
            "type": "AAM",
            "model": "AIM-54A-MK47",
            "users": ["USA", "Iran"],
            "seeker": "radar",
            "task": ["A2A"],
            "start_service": 1974,
            "end_service": 2004,
            "cost": 400,
            "warhead": 61,
            "reliability": 0.8,
            "range": 160,
            "semiactive_range": 130,
            "active_range": 18,
            "max_height": 24.8,
            "max_speed": 3.8,
            "manouvrability": 0.6,
            "accuracy": 0.75
        },
        "AIM-54A-MK60": {
            "type": "AAM",
            "model": "AIM-54A-MK60",
            "users": ["USA", "Iran"],
            "seeker": "radar",
            "task": ["A2A"],
            "start_service": 1975,
            "end_service": 2004,
            "cost": 400,
            "warhead": 61,
            "reliability": 0.8,
            "range": 160,
            "semiactive_range": 130,
            "active_range": 18,
            "max_height": 24.8,
            "max_speed": 3.8,
            "manouvrability": 0.6,
            "accuracy": 0.75
        },
        "AIM-54C-MK47": {
            "type": "AAM",
            "model": "AIM-54C-MK47",
            "users": ["USA", "Iran"],
            "seeker": "radar",
            "task": ["A2A"],
            "start_service": 1982,
            "end_service": 2004,
            "cost": 477,
            "warhead": 61,
            "reliability": 0.8,
            "range": 160,
            "semiactive_range": 148,
            "active_range": 18,
            "max_height": 24.8,
            "max_speed": 4.5,
            "manouvrability": 0.73,
            "accuracy": 0.8
        },
        "AIM-54C-MK60": {
            "type": "AAM",
            "model": "AIM-54C-MK60",
            "users": ["USA", "Iran"],
            "seeker": "radar",
            "task": ["A2A"],
            "start_service": 1982,
            "end_service": 2004,
            "cost": 477,
            "warhead": 61,
            "reliability": 0.8,
            "range": 160,
            "semiactive_range": 148,
            "active_range": 18,
            "max_height": 24.8,
            "max_speed": 4.5,
            "manouvrability": 0.73,
            "accuracy": 0.8
        },
        "AIM-7E": {
            "type": "AAM",
            "model": "AIM-7E",
            "users": ["USA", "UK", "Germany", "Italy", "Japan", "Turkey", "Greece", "Israel", "South Korea", "Taiwan"],
            "seeker": "radar",
            "task": ["A2A"],
            "start_service": 1970,
            "end_service": None,
            "cost": 125,
            "warhead": 40,
            "reliability": 0.8,
            "range": 45,
            "semiactive_range": 45,
            "active_range": None,
            "max_height": 18,
            "max_speed": 3,
            "manouvrability": 0.6,
            "accuracy": 0.6
        },
        "AIM-7F": {
            "type": "AAM",
            "model": "AIM-7F",
            "users": ["USA", "UK", "Germany", "Italy", "Japan", "Turkey", "Greece", "Israel", "South Korea", "Taiwan"],
            "seeker": "radar",
            "task": ["A2A"],
            "start_service": 1975,
            "end_service": None,
            "cost": 130,
            "warhead": 40,
            "reliability": 0.8,
            "range": 70,
            "semiactive_range": 70,
            "active_range": None,
            "max_height": 18,
            "max_speed": 3,
            "manouvrability": 0.6,
            "accuracy": 0.65
        },
        "AIM-7M": {
            "type": "AAM",
            "model": "AIM-7M",
            "users": ["USA", "UK", "Germany", "Italy", "Japan", "Turkey", "Greece", "Israel", "South Korea", "Taiwan", "Saudi Arabia"],
            "seeker": "radar",
            "task": ["A2A"],
            "start_service": 1982,
            "end_service": None,
            "cost": 150,
            "warhead": 40,
            "reliability": 0.8,
            "range": 70,
            "semiactive_range": 70,
            "active_range": None,
            "max_height": 18,
            "max_speed": 3,
            "manouvrability": 0.65,
            "accuracy": 0.7
        },
        "AIM-7MH": {
            "type": "AAM",
            "model": "AIM-7MH",
            "users": ["USA", "UK", "Germany", "Italy", "Japan", "Turkey", "Greece", "Israel", "South Korea", "Taiwan", "Saudi Arabia"],
            "seeker": "radar",
            "task": ["A2A"],
            "start_service": 1985,
            "end_service": None,
            "cost": 160,
            "warhead": 40,
            "reliability": 0.8,
            "range": 70,
            "semiactive_range": 70,
            "active_range": None,
            "max_height": 18,
            "max_speed": 3,
            "manouvrability": 0.66,
            "accuracy": 0.72
        },
        "AIM-7P": {
            "type": "AAM",
            "model": "AIM-7P",
            "users": ["USA", "UK", "Germany", "Italy", "Japan", "Turkey", "Greece", "Israel", "South Korea", "Taiwan", "Saudi Arabia"],
            "seeker": "radar",
            "task": ["A2A"],
            "start_service": 1987,
            "end_service": None,
            "cost": 170,
            "warhead": 40,
            "reliability": 0.8,
            "range": 70,
            "semiactive_range": 70,
            "active_range": None,
            "max_height": 18,
            "max_speed": 3,
            "manouvrability": 0.7,
            "accuracy": 0.75
        },
        "AIM-9B": {
            "type": "AAM",
            "model": "AIM-9B",
            "users": ["USA", "UK", "Germany", "France", "Italy", "Japan", "Turkey", "Greece", "Israel", "Taiwan", "South Korea"],
            "seeker": "infrared",
            "task": ["A2A"],
            "start_service": 1956,
            "end_service": None,
            "cost": 60,
            "warhead": 4.5,
            "reliability": 0.5,
            "range": 4.6,
            "max_height": 18,
            "max_speed": 1.7,
            "manouvrability": 0.5,
            "accuracy": 0.45
        },
        "AIM-9P": {
            "type": "AAM",
            "model": "AIM-9P",
            "users": ["USA", "UK", "Germany", "Italy", "Japan", "Turkey", "Greece", "Israel", "Taiwan", "South Korea", "Indonesia", "Pakistan"],
            "seeker": "infrared",
            "task": ["A2A"],
            "start_service": 1975,
            "end_service": None,
            "cost": 70,
            "warhead": 4.5,
            "reliability": 0.6,
            "range": 18.5,
            "max_height": 18,
            "max_speed": 2,
            "manouvrability": 0.5,
            "accuracy": 0.55
        },
        "AIM-9P5": {
            "type": "AAM",
            "model": "AIM-9P5",
            "users": ["USA", "Germany", "Italy", "Turkey", "Greece", "Israel", "Taiwan", "South Korea", "Indonesia"],
            "seeker": "infrared",
            "task": ["A2A"],
            "start_service": 1975,
            "end_service": None,
            "cost": 73,
            "warhead": 4.5,
            "reliability": 0.6,
            "range": 18.5,
            "max_height": 18,
            "max_speed": 2,
            "manouvrability": 0.6,
            "accuracy": 0.58
        },
        "AIM-9L": {
            "type": "AAM",
            "model": "AIM-9L",
            "users": ["USA", "UK", "Germany", "Italy", "Japan", "Turkey", "Greece", "Israel", "Taiwan", "South Korea", "Saudi Arabia", "Australia"],
            "seeker": "infrared",
            "task": ["A2A"],
            "start_service": 1975,
            "end_service": None,
            "cost": 75,
            "warhead": 9.4,
            "reliability": 0.6,
            "range": 18.5,
            "max_height": 18,
            "max_speed": 2.5,
            "manouvrability": 0.7,
            "accuracy": 0.7
        },
        "AIM-9M": {
            "type": "AAM",
            "model": "AIM-9M",
            "users": ["USA", "UK", "Germany", "Italy", "Japan", "Turkey", "Greece", "Israel", "Taiwan", "South Korea", "Saudi Arabia", "Australia"],
            "seeker": "infrared",
            "task": ["A2A"],
            "start_service": 1982,
            "end_service": None,
            "cost": 80,
            "warhead": 9.4,
            "reliability": 0.6,
            "range": 18.5,
            "max_height": 18,
            "max_speed": 2.5,
            "manouvrability": 0.7,
            "accuracy": 0.75
        },
        "AIM-9X": {
            "type": "AAM",
            "model": "AIM-9X",
            "users": ["USA", "UK", "Germany", "Italy", "Japan", "Turkey", "Greece", "Israel", "Taiwan", "South Korea", "Saudi Arabia", "Australia", "Poland"],
            "seeker": "infrared",
            "task": ["A2A"],
            "start_service": 2003,
            "end_service": None,
            "cost": 100,
            "warhead": 9.4,
            "reliability": 0.6,
            "range": 37,
            "max_height": 25,
            "max_speed": 2.9,
            "manouvrability": 0.9,
            "accuracy": 0.9
        },
        "R-550": {
            "type": "AAM",
            "model": "R-550",
            "users": ["France", "Argentina", "Brazil", "Chile", "Ecuador", "Egypt", "India", "Iraq", "Kuwait", "Pakistan", "Peru", "Qatar", "UAE"],
            "seeker": "infrared",
            "task": ["A2A"],
            "start_service": 1975,
            "end_service": None,
            "cost": 27.5,
            "warhead": 12.5,
            "reliability": 0.6,
            "range": 10,
            "max_height": 18,
            "max_speed": 2.8,
            "manouvrability": 0.6,
            "accuracy": 0.65
        },
        "R-530IR": {
            "type": "AAM",
            "model": "R-530IR",
            "users": ["France", "Argentina", "Australia", "Brazil", "Israel", "Pakistan", "South Africa", "Spain"],
            "seeker": "infrared",
            "task": ["A2A"],
            "start_service": 1975,
            "end_service": None,
            "cost": 157,
            "warhead": 27,
            "reliability": 0.6,
            "range": 18,
            "max_height": 18,
            "max_speed": 3,
            "manouvrability": 0.6,
            "accuracy": 0.55
        },
        "R-530EM": {
            "type": "AAM",
            "model": "R-530EM",
            "users": ["France", "Argentina", "Australia", "Brazil", "Israel", "Pakistan", "South Africa", "Spain"],
            "seeker": "radar",
            "task": ["A2A"],
            "start_service": 1975,
            "end_service": None,
            "cost": 157,
            "warhead": 27,
            "reliability": 0.7,
            "range": 40,
            "semiactive_range": 40,
            "max_height": 20,
            "max_speed": 4,
            "manouvrability": 0.7,
            "accuracy": 0.6
        },
        "RB-24": {
            "type": "AAM",
            "model": "RB-24",
            "users": ["Sweden"],
            "seeker": "infrared",
            "task": ["A2A"],
            "start_service": 1956,
            "end_service": None,
            "cost": 60,
            "warhead": 4.5,
            "reliability": 0.5,
            "range": 4.6,
            "max_height": 18,
            "max_speed": 1.7,
            "manouvrability": 0.5,
            "accuracy": 0.45
        },
        "RB-24J": {
            "type": "AAM",
            "model": "RB-24J",
            "users": ["Sweden"],
            "seeker": "infrared",
            "task": ["A2A"],
            "start_service": 1975,
            "end_service": None,
            "cost": 75,
            "warhead": 4.5,
            "reliability": 0.6,
            "range": 18.5,
            "max_height": 18,
            "max_speed": 2,
            "manouvrability": 0.6,
            "accuracy": 0.6
        },
        "RB-74": {
            "type": "AAM",
            "model": "RB-74",
            "users": ["Sweden"],
            "seeker": "infrared",
            "task": ["A2A"],
            "start_service": 1975,
            "end_service": None,
            "cost": 73,
            "warhead": 9.4,
            "reliability": 0.6,
            "range": 18.5,
            "max_height": 18,
            "max_speed": 2.5,
            "manouvrability": 0.7,
            "accuracy": 0.7
        },   
        # red
        "R-13M": {
            "type": "AAM",
            "model": "R-13M",
            "users": ["USSR", "Russia", "Poland", "East Germany", "Czechoslovakia", "Cuba", "North Korea", "Vietnam", "Syria", "Egypt", "Iraq", "India"],
            "seeker": "infrared",
            "task": ["A2A"],
            "start_service": 1974,
            "end_service": None,
            "cost": 70,  # k$
            "warhead": 5.5,  # kg
            "reliability": 0.6,
            "range": 15,  # km
            "max_height": 20,  # km
            "max_speed": 2.7,  # mach
            "manouvrability": 0.8,
            "accuracy": 0.55
        },            
        "R-13M1": {
            "type": "AAM",
            "model": "R-13M1",
            "users": ["USSR", "Russia", "Poland", "East Germany", "Czechoslovakia", "Cuba", "North Korea", "Vietnam", "Syria", "Egypt", "Iraq", "India"],
            "seeker": "infrared",
            "task": ["A2A"],
            "start_service": 1975,  # 1976
            "end_service": None,
            "cost": 77,  # k$
            "warhead": 5.5,  # kg
            "reliability": 0.6,
            "range": 17,  # km
            "max_height": 20,  # km
            "max_speed": 2.4,  # mach
            "manouvrability": 0.8,
            "accuracy": 0.58
        },
        "R-60": {
            "type": "AAM",
            "model": "R-60",
            "users": ["USSR", "Russia", "Poland", "East Germany", "Czechoslovakia", "Cuba", "North Korea", "Vietnam", "Syria", "Egypt", "Iraq", "India", "Libya", "Algeria"],
            "seeker": "infrared",
            "task": ["A2A"],
            "start_service": 1974,
            "end_service": None,
            "cost": 50,  # k$
            "warhead": 3,  # kg
            "reliability": 0.6,
            "range": 8,  # km
            "max_height": 20,  # km
            "max_speed": 2.7,  # mach
            "manouvrability": 0.7,
            "accuracy": 0.6
        },
        "R-60M": {
            "type": "AAM",
            "model": "R-60M",
            "users": ["USSR", "Russia", "Poland", "East Germany", "Czechoslovakia", "Cuba", "North Korea", "Vietnam", "Syria", "Egypt", "Iraq", "India", "Libya", "Algeria"],
            "seeker": "infrared",
            "task": ["A2A"],
            "start_service": 1974,  # 1982?
            "end_service": None,
            "cost": 60,  # k$
            "warhead": 3.5,  # kg
            "reliability": 0.6,
            "range": 8,  # km
            "max_height": 20,  # km
            "max_speed": 2.7,  # mach
            "manouvrability": 0.7,
            "accuracy": 0.65
        },
        "R-73": {
            "type": "AAM",
            "model": "R-73",
            "users": ["USSR", "Russia", "India", "China", "Malaysia", "Algeria", "Syria", "Iran", "North Korea", "Vietnam", "Cuba"],
            "seeker": "infrared",
            "task": ["A2A"],
            "start_service": 1984,
            "end_service": None,
            "cost": 90,  # k$
            "warhead": 7.4,  # kg
            "reliability": 0.8,
            "range": 30,  # km
            "max_height": 20,  # km
            "max_speed": 2.7,  # mach
            "manouvrability": 0.85,
            "accuracy": 0.85
        },
        "R-3S": {  # aka K-13A
            "type": "AAM",
            "model": "R-3S",
            "users": ["USSR", "Russia", "China", "Poland", "East Germany", "Czechoslovakia", "Cuba", "North Korea", "Vietnam", "Syria", "Egypt", "Iraq", "India", "Libya", "Algeria"],
            "seeker": "infrared",
            "task": ["A2A"],
            "start_service": 1960,
            "end_service": None,
            "cost": 30,  # k$
            "warhead": 8.8,  # kg
            "reliability": 0.6,
            "range": 8,  # km
            "max_height": 20,  # km
            "max_speed": 2.85,  # mach
            "manouvrability": 0.7,
            "accuracy": 0.45
        },
        "R-3R": {
            "type": "AAM",
            "model": "R-3R",
            "users": ["USSR", "Russia", "Poland", "East Germany", "Czechoslovakia", "Cuba", "North Korea", "Vietnam", "Syria", "Egypt", "Iraq", "India"],
            "seeker": "radar",
            "task": ["A2A"],
            "start_service": 1966,
            "end_service": None,
            "cost": 30,  # k$
            "warhead": 8.8,  # kg
            "reliability": 0.6,
            "range": 8,  # km
            "semiactive_range": 8,  # km
            "max_height": 20,  # km
            "max_speed": 2.85,  # mach
            "manouvrability": 0.7,
            "accuracy": 0.5
        },            
        "R-24R": {
            "type": "AAM",
            "model": "R-24R",
            "users": ["USSR", "Russia", "India", "Syria", "Libya", "Iraq", "Algeria"],
            "seeker": "radar",
            "task": ["A2A"],
            "start_service": 1975,
            "end_service": 1992,
            "cost": 125,  # k$
            "warhead": 35,  # kg
            "reliability": 0.6,
            "range": 50,  # km
            "semiactive_range": 50,  # km
            "max_height": 25,  # km
            "max_speed": 3.42,  # mach
            "manouvrability": 0.7,
            "accuracy": 0.65
        },            
        "R-24T": {
            "type": "AAM",
            "model": "R-24T",
            "users": ["USSR", "Russia", "India", "Syria", "Libya", "Iraq", "Algeria"],
            "seeker": "infrared",
            "task": ["A2A"],
            "start_service": 1975,
            "end_service": 1992,
            "cost": 125,  # k$
            "warhead": 35,  # kg
            "reliability": 0.6,
            "range": 15,  # km
            "max_height": 25,  # km
            "max_speed": 3.42,  # mach
            "manouvrability": 0.7,
            "accuracy": 0.6
        },            
        "R-40R": {
            "type": "AAM",
            "model": "R-40R",
            "users": ["USSR", "Russia", "Syria", "Libya", "Iraq", "Algeria", "North Korea"],
            "seeker": "radar",
            "task": ["A2A"],
            "start_service": 1972,
            "end_service": None,
            "cost": 200,  # k$
            "warhead": 70,  # kg
            "reliability": 0.6,
            "range": 50,  # km
            "semiactive_range": 50,  # km
            "max_height": 25,  # km
            "max_speed": 4.5,  # mach
            "manouvrability": 0.7,
            "accuracy": 0.6
        },            
        "R-40T": {
            "type": "AAM",
            "model": "R-40T",
            "users": ["USSR", "Russia", "Syria", "Libya", "Iraq", "Algeria", "North Korea"],
            "seeker": "infrared",
            "task": ["A2A"],
            "start_service": 1972,
            "end_service": None,
            "cost": 180,  # k$
            "warhead": 70,  # kg
            "reliability": 0.6,
            "range": 30,  # km
            "max_height": 25,  # km
            "max_speed": 4.5,  # mach
            "manouvrability": 0.7,
            "accuracy": 0.55
        },            
        "R-27R": {
            "type": "AAM",
            "model": "R-27R",
            "users": ["USSR", "Russia", "Ukraine", "India", "China", "Malaysia", "Algeria", "Syria", "Iran", "Vietnam"],
            "seeker": "radar",
            "task": ["A2A"],
            "start_service": 1983,
            "end_service": None,
            "cost": 230,  # k$
            "warhead": 39,  # kg
            "reliability": 0.6,
            "range": 50,  # km
            "semiactive_range": 50,  # km
            "max_height": 25,  # km
            "max_speed": 4.5,  # mach
            "manouvrability": 0.7,
            "accuracy": 0.7
        },
        "R-27T": {
            "type": "AAM",
            "model": "R-27T",
            "users": ["USSR", "Russia", "Ukraine", "India", "China", "Malaysia", "Algeria", "Syria", "Iran", "Vietnam"],
            "seeker": "infrared",
            "task": ["A2A"],
            "start_service": 1984,
            "end_service": None,
            "cost": 230,  # k$
            "warhead": 39,  # kg
            "reliability": 0.6,
            "range": 40,  # km
            "max_height": 25,  # km
            "max_speed": 4.5,  # mach
            "manouvrability": 0.7,
            "accuracy": 0.65
        },            
        "R-27ER": {
            "type": "AAM",
            "model": "R-27ER",
            "users": ["USSR", "Russia", "Ukraine", "India", "China", "Malaysia", "Algeria", "Syria", "Iran", "Vietnam"],
            "seeker": "radar",
            "task": ["A2A"],
            "start_service": 1983,
            "end_service": None,
            "cost": 230,  # k$
            "warhead": 39,  # kg
            "reliability": 0.6,
            "range": 120,  # km
            "semiactive_range": 50,  # km
            "max_height": 25,  # km
            "max_speed": 4.5,  # mach
            "manouvrability": 0.7,
            "accuracy": 0.72
        },           
        "R-27ET": {
            "type": "AAM",
            "model": "R-27ET",
            "users": ["USSR", "Russia", "Ukraine", "India", "China", "Malaysia", "Algeria", "Syria", "Iran", "Vietnam"],
            "seeker": "infrared",
            "task": ["A2A"],
            "start_service": 1984,
            "end_service": None,
            "cost": 230,  # k$
            "warhead": 39,  # kg
            "reliability": 0.6,
            "range": 130,  # km
            "max_height": 25,  # km
            "max_speed": 4.5,  # mach
            "manouvrability": 0.7,
            "accuracy": 0.68
        },
        
    },  
    'MISSILES_ASM': {
        "RB-05A": {
            "type": "ASM",
            "model": "RB-05A",
            "users": ["Sweden"],
            "seeker": "electro-optical",
            "task": ["Anti-ship Strike", "Strike", "SEAD"],
            "start_service": 1972,
            "end_service": 2005,
            "cost": 180,
            "warhead": 160,
            "reliability": 0.5,
            "range": 9,
            "speed": 340, # m/s
            "max_height": 18,
            "max_speed": 1,
            "manouvrability": 0.4,
            "perc_efficiency_variability": 0.2,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 0.9},
                    "med": {"accuracy": 0.75, "destroy_capacity": 1},
                    "small": {"accuracy": 0.65, "destroy_capacity": 1},
                },
                "Armored": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 0.8},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.9},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1},
                },
                "Hard": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 0.3},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.35},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.4},
                },
                "Structure": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 0.005},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.02},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.1},
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 0.8},
                    "med": {"accuracy": 0.75, "destroy_capacity": 0.9},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1},
                },
                "Airbase": {
                    "big": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1e-8},
                },
                "ship": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 0.6},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.8},
                    "small": {"accuracy": 0.5, "destroy_capacity": 1},
                },
            }
        },
        "RB-15F": {
            "type": "ASM",
            "model": "RB-15F",
            "users": ["Sweden"],
            "task": ["Anti-ship Strike"],
            "start_service": 1985,
            "end_service": None,
            "cost": 720,
            "warhead": 200,  # kg
            "range": 75,
            "speed": 306, # m/s
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "ship": {
                    "big": {
                        "accuracy": 1,
                        "destroy_capacity": 0.6
                    },
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.8
                    },
                    "small": {
                        "accuracy": 1,
                        "destroy_capacity": 1
                    }
                }
            }
        },
        "AGM-45": {
            "type": "ASM",
            "model": "AGM-45",
            "users": ["USA", "Israel", "UK"],
            "task": ["SEAD"],
            "start_service": 1966,
            "end_service": 1992,
            "cost": 32,
            "warhead": 66,
            "range": 10,
            "speed": 680, # m/s
            "perc_efficiency_variability": 0.2,
            "efficiency": {
                "Air_Defense": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.7},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.8},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1}
                }
            }
        },
        "AGM-84A": {
            "type": "ASM",
            "model": "AGM-84A",
            "users": ["USA", "UK", "Germany", "Denmark", "Australia", "Japan", "South Korea", "Taiwan", "Egypt", "Saudi Arabia"],
            "task": ["Anti-ship Strike"],
            "start_service": 1970,
            "end_service": None,
            "cost": 720,
            "warhead": 221,
            "range": 50,
            "speed": 240, # m/s
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "ship": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.6},
                    "med": {"accuracy": 1, "destroy_capacity": 0.8},
                    "small": {"accuracy": 1, "destroy_capacity": 1}
                }
            }
        },
        "AGM-88": {
            "type": "ASM",
            "model": "AGM-88",
            "users": ["USA", "Germany", "Italy", "Spain", "Greece", "Turkey", "Israel", "Australia", "South Korea", "Taiwan"],
            "task": ["SEAD"],
            "start_service": 1985,
            "end_service": None,
            "cost": 200,
            "warhead": 66,  # kg - WDU-21/B blast-fragmentation
            "range": 80,
            "speed": 680, # m/s
            "perc_efficiency_variability": 0.2,
            "efficiency": {
                "Air_Defense": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 0.77},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.88},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1}
                }
            }
        },
        "Kormoran": {
            "type": "ASM",
            "model": "Kormoran",
            "users": ["Germany", "Italy"],
            "task": ["Anti-ship Strike"],
            "start_service": 1973,
            "end_service": None,
            "cost": 200,
            "warhead": 165,
            "range": 30,
            "speed": 313, # m/s
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "ship": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.45},
                    "med": {"accuracy": 1, "destroy_capacity": 0.7},
                    "small": {"accuracy": 1, "destroy_capacity": 1}
                }
            }
        },
        "RB-05E": {
            "type": "ASM",
            "model": "RB-05E",
            "users": ["Sweden"],
            "task": ["Anti-ship Strike", "Strike", "SEAD"],
            "start_service": 1972,
            "end_service": 2005,
            "cost": 300,
            "warhead": 160,
            "range": 9,
            "speed": 340, # m/s
            "perc_efficiency_variability": 0.2,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 0.9},
                    "med": {"accuracy": 0.75, "destroy_capacity": 1},
                    "small": {"accuracy": 0.65, "destroy_capacity": 1},
                },
                "Armored": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 0.8},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.9},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1},
                },
                "Hard": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 0.3},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.35},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.4},
                },
                "Structure": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 0.005},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.02},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.1},
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 0.8},
                    "med": {"accuracy": 0.75, "destroy_capacity": 0.9},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1},
                },
                "Airbase": {
                    "big": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1e-8},
                },
                "ship": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 0.6},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.8},
                    "small": {"accuracy": 0.5, "destroy_capacity": 1},
                },
            }
        },
        "RB-04E": {
            "type": "ASM",
            "model": "RB-04E",
            "users": ["Sweden"],
            "task": ["Anti-ship Strike"],
            "start_service": 1975,
            "end_service": 2000,
            "cost": 700,
            "warhead": 300,
            "range": 32,
            "speed": 306, # m/s
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "ship": {
                    "big": {"accuracy": 0.9, "destroy_capacity": 0.8},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.9},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1}
                }
            }
        },
        "Sea Eagle": {
            "type": "ASM",
            "model": "Sea Eagle",
            "users": ["UK", "India", "Saudi Arabia"],
            "task": ["Anti-ship Strike"],
            "start_service": 1985,
            "end_service": None,
            "cost": 700,
            "warhead": 230,
            "range": 100,
            "speed": 315, # m/s
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "ship": {
                    "big": {"accuracy": 0.9, "destroy_capacity": 0.6},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.7},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.8}
                }
            }
        },
        "RB-75T": {
            "type": "ASM",
            "model": "RB-75T",
            "users": ["Sweden"],
            "task": ["Anti-ship Strike", "Strike", "SEAD"],
            "start_service": 1972,
            "end_service": None,
            "cost": 160,
            "warhead": 57,  # kg - WDU-20/B shaped-charge
            "range": 15,
            "speed": 320, # m/s
            "perc_efficiency_variability": 0.05,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 1},
                    "med": {"accuracy": 0.8, "destroy_capacity": 1},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1},
                },
                "Armored": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 0.8},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.9},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1},
                },
                "Hard": {
                    "big": {"accuracy": 0.9, "destroy_capacity": 0.15},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.2},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.25},
                },
                "Structure": {
                    "big": {"accuracy": 0.9, "destroy_capacity": 0.002},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.01},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.05},
                },
                "Air_Defense": {
                    "big": {"accuracy": 1, "destroy_capacity": 1},
                    "med": {"accuracy": 1, "destroy_capacity": 1},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1},
                },
                "Airbase": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "ship": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.6},
                    "med": {"accuracy": 1, "destroy_capacity": 0.8},
                    "small": {"accuracy": 1, "destroy_capacity": 1},
                },
            }
        },
        "RB-15": {
            "type": "ASM",
            "model": "RB-15",
            "users": ["Sweden", "Finland", "Croatia"],
            "task": ["Anti-ship Strike"],
            "start_service": 1989,
            "end_service": None,
            "cost": 350,
            "warhead": 200,
            "range": 70,
            "speed": 306, # m/s
            "perc_efficiency_variability": 0.05,
            "efficiency": {
                "ship": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.6},
                    "med": {"accuracy": 1, "destroy_capacity": 0.8},
                    "small": {"accuracy": 1, "destroy_capacity": 1}
                }
            }
        },
        "AGM-65D": {
            "type": "ASM",
            "model": "AGM-65D",
            "users": ["USA", "UK", "Germany", "Italy", "Spain", "Greece", "Turkey", "Israel", "Egypt", "South Korea", "Taiwan"],
            "task": ["Anti-ship Strike", "Strike", "SEAD"],
            "start_service": 1986,
            "end_service": None,
            "cost": 160,
            "warhead": 57,  # kg - WDU-20/B shaped-charge
            "range": 15,
            "speed": 320, # m/s
            "perc_efficiency_variability": 0.05,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 1},
                    "med": {"accuracy": 0.85, "destroy_capacity": 1},
                    "small": {"accuracy": 0.75, "destroy_capacity": 1},
                },
                "Armored": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.8},
                    "med": {"accuracy": 0.85, "destroy_capacity": 0.9},
                    "small": {"accuracy": 0.75, "destroy_capacity": 1},
                },
                "Hard": {
                    "big": {"accuracy": 0.9, "destroy_capacity": 0.15},
                    "med": {"accuracy": 0.85, "destroy_capacity": 0.2},
                    "small": {"accuracy": 0.75, "destroy_capacity": 0.25},
                },
                "Structure": {
                    "big": {"accuracy": 0.9, "destroy_capacity": 0.002},
                    "med": {"accuracy": 0.85, "destroy_capacity": 0.01},
                    "small": {"accuracy": 0.75, "destroy_capacity": 0.05},
                },
                "Air_Defense": {
                    "big": {"accuracy": 1, "destroy_capacity": 1},
                    "med": {"accuracy": 1, "destroy_capacity": 1},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1},
                },
                "Airbase": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "ship": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.6},
                    "med": {"accuracy": 1, "destroy_capacity": 0.8},
                    "small": {"accuracy": 1, "destroy_capacity": 1},
                },
            }
        },
        "AGM-65K": {
            "type": "ASM",
            "model": "AGM-65K",
            "users": ["USA", "South Korea", "Taiwan"],
            "task": ["Anti-ship Strike", "Strike", "SEAD"],
            "start_service": 1970,
            "end_service": None,
            "cost": 160,
            "warhead": 136,  # kg - WDU-24/B penetrating blast-fragmentation
            "range": 15,
            "speed": 320, # m/s
            "perc_efficiency_variability": 0.05,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 1},
                    "med": {"accuracy": 0.8, "destroy_capacity": 1},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1},
                },
                "Armored": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 0.8},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.9},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1},
                },
                "Hard": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.15},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.2},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.25},
                },
                "Structure": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.002},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.01},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.05},
                },
                "Air_Defense": {
                    "big": {"accuracy": 1, "destroy_capacity": 1},
                    "med": {"accuracy": 1, "destroy_capacity": 1},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1},
                },
                "Airbase": {
                    "big": {"accuracy": 0.85, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.85, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.85, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.85, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.85, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.85, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.85, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.85, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.85, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.85, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.85, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.85, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.85, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.85, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.85, "destroy_capacity": 1e-8},
                },
                "ship": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.6},
                    "med": {"accuracy": 1, "destroy_capacity": 0.8},
                    "small": {"accuracy": 1, "destroy_capacity": 1},
                },
            }
        },
        "AGM-114": {
            "type": "ASM",
            "model": "AGM-114",
            "users": ["USA", "UK", "Germany", "France", "Italy", "Israel", "Saudi Arabia", "UAE", "Japan", "South Korea", "Australia"],
            "task": ["Strike", "SEAD", "Anti-ship Strike"],
            "start_service": 1984,
            "end_service": None,
            "cost": 80,
            "warhead": 9,
            "range": 8,
            "speed": 425, # m/s
            "perc_efficiency_variability": 0.05,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.5},
                    "med": {"accuracy": 1, "destroy_capacity": 0.6},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.7},
                },
                "Armored": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.4},
                    "med": {"accuracy": 1, "destroy_capacity": 0.5},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.6},
                },
                "Hard": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.1},
                    "med": {"accuracy": 0.95, "destroy_capacity": 0.15},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.2},
                },
                "Structure": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.001},
                    "med": {"accuracy": 0.95, "destroy_capacity": 0.005},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.02},
                },
                "Air_Defense": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.6},
                    "med": {"accuracy": 1, "destroy_capacity": 0.7},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.8},
                },
                "Airbase": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "ship": {
                    "big": {"accuracy": 0.95, "destroy_capacity": 0.1},
                    "med": {"accuracy": 0.9, "destroy_capacity": 0.2},
                    "small": {"accuracy": 0.85, "destroy_capacity": 0.3},
                },
            }
        },
        "BGM-71D": {
            "type": "ASM",
            "model": "BGM-71D",
            "users": ["USA", "UK", "Germany", "Italy", "Turkey", "Greece", "Israel", "Egypt", "Saudi Arabia", "Iran", "Pakistan"],
            "task": ["Strike", "SEAD"],
            "start_service": 1970,
            "end_service": None,
            "cost": 12,
            "warhead": 6.14,
            "range": 3,
            "speed": 278, # m/s
            "perc_efficiency_variability": 0.05,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 1, "destroy_capacity": 1},
                    "med": {"accuracy": 1, "destroy_capacity": 1},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1},
                },
                "Armored": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.8},
                    "med": {"accuracy": 1, "destroy_capacity": 0.9},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1},
                },
                "Hard": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.08},
                    "med": {"accuracy": 0.95, "destroy_capacity": 0.12},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.15},
                },
                "Structure": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.001},
                    "med": {"accuracy": 0.95, "destroy_capacity": 0.003},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.01},
                },
                "Air_Defense": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.8},
                    "med": {"accuracy": 1, "destroy_capacity": 0.9},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1},
                },
                "Airbase": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
            }
        },
        # red

        "9M120-F": {
        "type": "ASM",
        "model": "9M120-F",
        "users": ["Russia", "Belarus", "Kazakhstan", "Algeria"],
        "task": ["Strike", "Anti-ship Strike"],
        "start_service": 1980,
        "end_service": None,
        "cost": 50,  # k$
        "warhead": 7.4,  # kg
        "range": 6,  # Km
        "speed": 550, # m/s
        "perc_efficiency_variability": 0.1,
        "efficiency": {
            "Soft": {
                "big": {"accuracy": 0.8, "destroy_capacity": 0.4},
                "med": {"accuracy": 0.7, "destroy_capacity": 0.5},
                "small": {"accuracy": 0.6, "destroy_capacity": 0.6},
            },
            "Armored": {
                "big": {"accuracy": 0.8, "destroy_capacity": 0.1},
                "med": {"accuracy": 0.7, "destroy_capacity": 0.2},
                "small": {"accuracy": 0.6, "destroy_capacity": 0.3},
            },
            "Hard": {
                "big": {"accuracy": 0.7, "destroy_capacity": 0.08},
                "med": {"accuracy": 0.6, "destroy_capacity": 0.12},
                "small": {"accuracy": 0.6, "destroy_capacity": 0.15},
            },
            "Structure": {
                "big": {"accuracy": 0.7, "destroy_capacity": 0.001},
                "med": {"accuracy": 0.6, "destroy_capacity": 0.003},
                "small": {"accuracy": 0.6, "destroy_capacity": 0.01},
            },
            "Airbase": {
                "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
            },
            "Port": {
                "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
            },
            "Shipyard": {
                "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
            },
            "Farp": {
                "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
            },
            "Stronghold": {
                "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
            },
            "ship": {
                "med": {"accuracy": 0.8, "destroy_capacity": 0.1},
                "small": {"accuracy": 0.7, "destroy_capacity": 0.15},
            },
        },
    },            
        "9M120": {
            "type": "ASM",
            "model": "9M120",
            "users": ["Russia", "Belarus", "Kazakhstan", "Algeria", "Syria"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1980,
            "end_service": None,
            "cost": 50,  # k$
            "warhead": 7.4,  # kg
            "range": 6,  # Km
            "speed": 550, # m/s
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 0.4},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.5},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.6},
                },
                "Armored": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 0.35},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.45},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.55},
                },
                "Hard": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.08},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.12},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.15},
                },
                "Structure": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.001},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.003},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.01},
                },
                "Airbase": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "ship": {
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.1},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.15},
                },
            },
        },
        "9M114": {
            "type": "ASM",
            "model": "9M114",
            "users": ["USSR", "Russia", "India", "Syria", "Iraq", "Libya", "Algeria"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1975,
            "end_service": None,
            "cost": 35,  # k$
            "warhead": 5,  # kg
            "range": 7,  # Km
            "speed": 530, # m/s
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.4},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.5},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.6},
                },
                "Armored": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.3},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.4},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.6},
                },
                "Hard": {
                    "big": {"accuracy": 0.6, "destroy_capacity": 0.06},
                    "med": {"accuracy": 0.5, "destroy_capacity": 0.1},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.12},
                },
                "Structure": {
                    "big": {"accuracy": 0.6, "destroy_capacity": 0.001},
                    "med": {"accuracy": 0.5, "destroy_capacity": 0.002},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.008},
                },
                "Airbase": {
                    "big": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.5, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.5, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.5, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.5, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.5, "destroy_capacity": 1e-8},
                },
                "ship": {
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.1},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.15},
                },
            },
        },
        "Hot-3": {
            "type": "ASM",
            "model": "Hot-3",
            "users": ["France", "Germany", "Egypt", "Iraq", "Saudi Arabia", "UAE", "Syria"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1978,
            "end_service": None,
            "cost": 35,  # k$
            "warhead": 6,  # kg
            "range": 4,  # Km
            "speed": 260, # m/s
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.9, "destroy_capacity": 0.6},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.7},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.9},
                },
                "Armored": {
                    "big": {"accuracy": 0.9, "destroy_capacity": 0.45},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.6},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.8},
                },
                "Hard": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 0.08},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.12},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.15},
                },
                "Structure": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 0.001},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.003},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.01},
                },
                "Airbase": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "ship": {
                    "med": {"accuracy": 0.85, "destroy_capacity": 0.15},
                    "small": {"accuracy": 0.8, "destroy_capacity": 0.2},
                },
            },
        },
        "Mistral": {
            "type": "ASM",
            "model": "Mistral",
            "users": ["France", "Belgium", "Brazil", "Chile", "Cyprus", "Egypt", "Finland", "Indonesia", "South Korea", "Norway", "Singapore"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1985,
            "end_service": None,
            "cost": 40,  # k$
            "warhead": 3,  # kg
            "range": 6,  # Km
            "speed": 930, # m/s
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.9, "destroy_capacity": 0.3},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.37},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.4},
                },
                "Armored": {
                    "big": {"accuracy": 0.9, "destroy_capacity": 0.25},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.3},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.4},
                },
                "Hard": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 0.04},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.06},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.08},
                },
                "Structure": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 0.0005},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.001},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.005},
                },
                "Airbase": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "ship": {
                    "small": {"accuracy": 0.8, "destroy_capacity": 0.1},
                },
            },
        },                    
        "Kh-22N": {  # radar antiship
            "type": "ASM",
            "model": "Kh-22N",
            "users": ["USSR", "Russia", "Ukraine"],
            "task": ["Anti-ship Strike"],
            "start_service": 1967,
            "end_service": None,
            "cost": 1000,  # k$
            "warhead": 1000,  # kg
            "range": 330,
            "speed": 1190, # m/s
            "perc_efficiency_variability": 0.05,  # efficiecy variability 0-1 (100%)
            "efficiency": {
                "ship": {  # mobile target
                    "big": {
                        "accuracy": 1,
                        "destroy_capacity": 1,
                    },
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 1,
                    },
                    "small": {
                        "accuracy": 0.95,
                        "destroy_capacity": 1,
                    }
                },
            },
        },            
        "Kh-58": {  # antiradiation
            "type": "ASM",
            "model": "Kh-58",
            "users": ["USSR", "Russia", "India", "Syria", "Libya", "Iraq", "Algeria"],
            "task": ["SEAD"],
            "start_service": 1975,  # 1978 --1982 vers. U
            "end_service": None,
            "cost": 700,  # k$
            "warhead": 149,  # kg
            "range": 250,
            "speed": 1190, # m/s
            "perc_efficiency_variability": 0.2,  # efficiecy variability(0-1): firepower_max = firepower_max * ( 1 + perc_efficiency_variability )
            "efficiency": {
                "Air_Defense": {
                    "big": {
                        "accuracy": 0.7,
                        "destroy_capacity": 0.9,
                    },
                    "med": {
                        "accuracy": 0.7,
                        "destroy_capacity": 1,
                    },
                    "small": {
                        "accuracy": 0.6,
                        "destroy_capacity": 1,
                    }
                },
            },
        },            
        "Kh-66": {  # radar beam-riding
            "type": "ASM",
            "model": "Kh-66",
            "users": ["USSR", "Russia", "Syria", "Libya", "Iraq", "Egypt"],
            "task": ["Anti-ship Strike", "Strike", "SEAD"],
            "start_service": 1967,
            "end_service": None,
            "cost": 200,  # k$
            "warhead": 111,  # kg
            "range": 10,  # Km
            "speed": 600, # m/s
            "perc_efficiency_variability": 0.05,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 1},
                    "med": {"accuracy": 0.7, "destroy_capacity": 1},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1},
                },
                "Armored": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 0.8},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.9},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1},
                },
                "Hard": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 0.25},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.3},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.35},
                },
                "Structure": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.15},
                    "med": {"accuracy": 1, "destroy_capacity": 0.22},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.53},
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 0.8},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.9},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1},
                },
                "Airbase": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1e-8},
                },
                "Bridge": {
                    "med": {"accuracy": 1, "destroy_capacity": 0.22},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.33},
                },
                "ship": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.7},
                    "med": {"accuracy": 1, "destroy_capacity": 0.8},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1},
                },
            },
        },            
        "Kh-59": {  # TV guided, vers. M -> 1990
            "type": "ASM",
            "model": "Kh-59",
            "users": ["USSR", "Russia", "India", "China", "Algeria"],
            "task": ["Anti-ship Strike", "Strike", "SEAD"],
            "start_service": 1980,
            "end_service": None,
            "cost": 600,  # k$
            "warhead": 148,  # kg
            "range": 90,  # Km
            "speed": 310, # m/s
            "perc_efficiency_variability": 0.05,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.9},
                    "med": {"accuracy": 1, "destroy_capacity": 0.95},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1},
                },
                "Armored": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.65},
                    "med": {"accuracy": 1, "destroy_capacity": 0.7},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.75},
                },
                "Hard": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.5},
                    "med": {"accuracy": 1, "destroy_capacity": 0.6},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.7},
                },
                "Structure": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.3},
                    "med": {"accuracy": 1, "destroy_capacity": 0.4},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.7},
                },
                "Air_Defense": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.7},
                    "med": {"accuracy": 1, "destroy_capacity": 0.75},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.8},
                },
                "Airbase": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Bridge": {
                    "med": {"accuracy": 1, "destroy_capacity": 0.3},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.5},
                },
                "ship": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.4},
                    "med": {"accuracy": 1, "destroy_capacity": 0.6},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.8},
                },
            },
        },        
        "Kh-25ML": {  # laser guided
            "type": "ASM",
            "model": "Kh-25ML",
            "users": ["USSR", "Russia", "India", "Syria", "Iraq", "Libya", "Algeria", "Vietnam"],
            "task": ["Anti-ship Strike", "Strike", "SEAD"],
            "start_service": 1975,
            "end_service": None,
            "cost": 160,  # k$
            "warhead": 90,  # kg
            "range": 11,  # Km
            "speed": 870, # m/s
            "perc_efficiency_variability": 0.05,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.8},
                    "med": {"accuracy": 1, "destroy_capacity": 0.85},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.95},
                },
                "Armored": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.65},
                    "med": {"accuracy": 1, "destroy_capacity": 0.7},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.75},
                },
                "Hard": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.3},
                    "med": {"accuracy": 1, "destroy_capacity": 0.35},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.4},
                },
                "Structure": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.15},
                    "med": {"accuracy": 1, "destroy_capacity": 0.22},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.53},
                },
                "Air_Defense": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.7},
                    "med": {"accuracy": 1, "destroy_capacity": 0.75},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.8},
                },
                "Airbase": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Bridge": {
                    "med": {"accuracy": 1, "destroy_capacity": 0.22},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.33},
                },
                "ship": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.22},
                    "med": {"accuracy": 1, "destroy_capacity": 0.27},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.35},
                },
            },
        },
        "Kh-25MR": {  # radar guided
            "type": "ASM",
            "model": "Kh-25MR",
            "users": ["USSR", "Russia", "India", "Syria", "Iraq", "Libya", "Algeria"],
            "task": ["Anti-ship Strike", "Strike", "SEAD"],
            "start_service": 1975,
            "end_service": None,
            "cost": 160,  # k$
            "warhead": 140,  # kg
            "range": 11,  # Km
            "speed": 870, # m/s
            "perc_efficiency_variability": 0.05,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.95},
                    "med": {"accuracy": 1, "destroy_capacity": 1},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1},
                },
                "Armored": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.9},
                    "med": {"accuracy": 1, "destroy_capacity": 1},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1},
                },
                "Hard": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.45},
                    "med": {"accuracy": 1, "destroy_capacity": 0.55},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.65},
                },
                "Structure": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.22},
                    "med": {"accuracy": 1, "destroy_capacity": 0.35},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.78},
                },
                "Air_Defense": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.9},
                    "med": {"accuracy": 1, "destroy_capacity": 1},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1},
                },
                "Airbase": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Bridge": {
                    "med": {"accuracy": 1, "destroy_capacity": 0.35},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.45},
                },
                "ship": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.33},
                    "med": {"accuracy": 1, "destroy_capacity": 0.44},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.52},
                },
            },
        },
        "Kh-25MPU": {  # antiradiation
            "type": "ASM",
            "model": "Kh-25MPU",
            "users": ["USSR", "Russia", "India", "Syria"],
            "task": ["SEAD"],
            "start_service": 1975,  # 1978 --1982 vers. U
            "end_service": None,
            "cost": 300,  # k$
            "warhead": 90,  # kg
            "range": 30,  # Km
            "speed": 870, # m/s
            "perc_efficiency_variability": 0.1,  # efficiency variability(0-1): firepower_max = firepower_max * (1 + perc_efficiency_variability)
            "efficiency": {
                "Air_Defense": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 0.83,
                        "destroy_capacity": 0.7,
                    },
                    "med": {
                        "accuracy": 0.83,
                        "destroy_capacity": 0.75,
                    },
                    "small": {
                        "accuracy": 0.75,
                        "destroy_capacity": 0.8,
                    }
                },
            },
        },
        "Kh-25MP": {  # antiradiation
            "type": "ASM",
            "model": "Kh-25MP",
            "users": ["USSR", "Russia", "India", "Syria", "Iraq", "Libya"],
            "task": ["SEAD"],
            "start_service": 1975,  # 1978 --1982 vers. U
            "end_service": None,
            "cost": 200,  # k$
            "warhead": 90,  # kg
            "range": 18,  # Km
            "speed": 870, # m/s
            "perc_efficiency_variability": 0.2,  # efficiency variability(0-1): firepower_max = firepower_max * (1 + perc_efficiency_variability)
            "efficiency": {
                "Air_Defense": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 0.7,
                        "destroy_capacity": 0.7,
                    },
                    "med": {
                        "accuracy": 0.7,
                        "destroy_capacity": 0.75,
                    },
                    "small": {
                        "accuracy": 0.6,
                        "destroy_capacity": 0.8,
                    }
                },
            },
        },
        "Kh-29L": {  # laser guided
            "type": "ASM",
            "model": "Kh-29L",
            "users": ["USSR", "Russia", "India", "China", "Syria", "Algeria"],
            "task": ["Anti-ship Strike", "Strike", "SEAD"],
            "start_service": 1980,
            "end_service": None,
            "cost": 160,  # k$
            "warhead": 320,  # kg
            "range": 10,  # Km
            "speed": 900, # m/s
            "perc_efficiency_variability": 0.05,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 1, "destroy_capacity": 1},
                    "med": {"accuracy": 1, "destroy_capacity": 1},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1},
                },
                "Armored": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.9},
                    "med": {"accuracy": 1, "destroy_capacity": 1},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1},
                },
                "Hard": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.7},
                    "med": {"accuracy": 1, "destroy_capacity": 0.8},
                    "small": {"accuracy": 0.95, "destroy_capacity": 0.9},
                },
                "Structure": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.55},
                    "med": {"accuracy": 1, "destroy_capacity": 0.7},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1},
                },
                "Air_Defense": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.95},
                    "med": {"accuracy": 1, "destroy_capacity": 1},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1},
                },
                "Airbase": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Bridge": {
                    "med": {"accuracy": 1, "destroy_capacity": 0.5},
                    "small": {"accuracy": 0.95, "destroy_capacity": 0.95},
                },
                "ship": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.9},
                    "med": {"accuracy": 1, "destroy_capacity": 1},
                },
            },
        },
        "Kh-29T": {  # TV guided
            "type": "ASM",
            "model": "Kh-29T",
            "users": ["USSR", "Russia", "India", "China", "Syria", "Algeria"],
            "task": ["Anti-ship Strike", "Strike", "SEAD"],
            "start_service": 1980,
            "end_service": None,
            "cost": 160,  # k$
            "warhead": 320,  # kg
            "range": 12,  # Km
            "speed": 900, # m/s
            "perc_efficiency_variability": 0.05,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 1, "destroy_capacity": 1},
                    "med": {"accuracy": 1, "destroy_capacity": 1},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1},
                },
                "Armored": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.9},
                    "med": {"accuracy": 1, "destroy_capacity": 1},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1},
                },
                "Hard": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.7},
                    "med": {"accuracy": 1, "destroy_capacity": 0.8},
                    "small": {"accuracy": 0.95, "destroy_capacity": 0.9},
                },
                "Structure": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.55},
                    "med": {"accuracy": 1, "destroy_capacity": 0.7},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1},
                },
                "Air_Defense": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.95},
                    "med": {"accuracy": 1, "destroy_capacity": 1},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1},
                },
                "Airbase": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Bridge": {
                    "med": {"accuracy": 1, "destroy_capacity": 0.5},
                    "small": {"accuracy": 0.95, "destroy_capacity": 0.95},
                },
                "ship": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.9},
                    "med": {"accuracy": 1, "destroy_capacity": 1},
                },
            },
        },
    
    },       
    'BOMBS': {
        "Mk-84": {
            "type": "Bombs",
            "model": "Mk-84",
            "users": ["USA", "UK", "Germany", "Italy", "France", "Spain", "Turkey", "Greece", "Israel", "Egypt", "Saudi Arabia", "Australia", "South Korea", "Japan", "Pakistan", "Iran"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1954,
            "end_service": None,
            "cost": 4.4,
            "warhead": 429,
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.8},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.85},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.95},
                },
                "Armored": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.95},
                    "med": {"accuracy": 0.8, "destroy_capacity": 1},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1},
                },
                "Hard": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.65},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.7},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.8},
                },
                "Structure": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.8},
                    "med": {"accuracy": 0.9, "destroy_capacity": 0.9},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1},
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.95},
                    "med": {"accuracy": 0.8, "destroy_capacity": 1},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1},
                },
                "Airbase": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Bridge": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.7},
                    "med": {"accuracy": 0.9, "destroy_capacity": 0.8},
                    "small": {"accuracy": 0.8, "destroy_capacity": 0.9},
                },
                "ship": {
                    "big": {"accuracy": 0.5, "destroy_capacity": 0.85},
                    "med": {"accuracy": 0.4, "destroy_capacity": 1},
                    "small": {"accuracy": 0.2, "destroy_capacity": 1},
                },
            }
        },
        "Mk-83": {
            "type": "Bombs",
            "model": "Mk-83",
            "users": ["USA", "UK", "Germany", "Italy", "France", "Spain", "Turkey", "Greece", "Israel", "Egypt", "Saudi Arabia", "Australia", "South Korea", "Japan", "Pakistan"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1954,
            "end_service": None,
            "cost": 3.3,
            "warhead": 202,
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.9},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.95},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1},
                },
                "Armored": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.95},
                    "med": {"accuracy": 0.75, "destroy_capacity": 1},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1},
                },
                "Hard": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.35},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.4},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.45},
                },
                "Structure": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.4},
                    "med": {"accuracy": 0.9, "destroy_capacity": 0.45},
                    "small": {"accuracy": 0.8, "destroy_capacity": 0.5},
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.95},
                    "med": {"accuracy": 0.75, "destroy_capacity": 1},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1},
                },
                "Airbase": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Bridge": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.35},
                    "med": {"accuracy": 0.9, "destroy_capacity": 0.4},
                    "small": {"accuracy": 0.8, "destroy_capacity": 0.45},
                },
                "ship": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.42},
                    "med": {"accuracy": 0.5, "destroy_capacity": 0.5},
                    "small": {"accuracy": 0.3, "destroy_capacity": 0.5},
                },
            }
        },
        "Mk-82": {
            "type": "Bombs",
            "model": "Mk-82",
            "users": ["USA", "UK", "Germany", "Italy", "France", "Spain", "Turkey", "Greece", "Israel", "Egypt", "Saudi Arabia", "Australia", "South Korea", "Japan", "Pakistan"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1954,
            "end_service": None,
            "cost": 2.7,
            "warhead": 92,
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.8},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.85},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.95},
                },
                "Armored": {
                    "big": {"accuracy": 0.9, "destroy_capacity": 0.39},
                    "med": {"accuracy": 0.85, "destroy_capacity": 0.44},
                    "small": {"accuracy": 0.75, "destroy_capacity": 0.49},
                },
                "Hard": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.18},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.22},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.26},
                },
                "Structure": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.13},
                    "med": {"accuracy": 0.9, "destroy_capacity": 0.21},
                    "small": {"accuracy": 0.8, "destroy_capacity": 0.52},
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.9, "destroy_capacity": 0.69},
                    "med": {"accuracy": 0.85, "destroy_capacity": 0.74},
                    "small": {"accuracy": 0.75, "destroy_capacity": 0.79},
                },
                "Airbase": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Bridge": {
                    "med": {"accuracy": 0.9, "destroy_capacity": 0.21},
                    "small": {"accuracy": 0.8, "destroy_capacity": 0.31},
                },
                "ship": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.21},
                    "med": {"accuracy": 0.5, "destroy_capacity": 0.25},
                    "small": {"accuracy": 0.3, "destroy_capacity": 0.33},
                },
            }
        },
        "Mk-82AIR": {
            "type": "Bombs",
            "model": "Mk-82AIR",
            "users": ["USA", "UK", "Italy", "Israel", "South Korea", "Australia"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1965,
            "end_service": None,
            "cost": 4,
            "warhead": 92,
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.8},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.85},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.95},
                },
                "Armored": {
                    "big": {"accuracy": 0.9, "destroy_capacity": 0.39},
                    "med": {"accuracy": 0.85, "destroy_capacity": 0.44},
                    "small": {"accuracy": 0.75, "destroy_capacity": 0.49},
                },
                "Hard": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.18},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.22},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.26},
                },
                "Structure": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.13},
                    "med": {"accuracy": 0.9, "destroy_capacity": 0.21},
                    "small": {"accuracy": 0.8, "destroy_capacity": 0.52},
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.9, "destroy_capacity": 0.69},
                    "med": {"accuracy": 0.85, "destroy_capacity": 0.74},
                    "small": {"accuracy": 0.75, "destroy_capacity": 0.79},
                },
                "Airbase": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Bridge": {
                    "med": {"accuracy": 0.9, "destroy_capacity": 0.21},
                    "small": {"accuracy": 0.8, "destroy_capacity": 0.31},
                },
                "ship": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.21},
                    "med": {"accuracy": 0.5, "destroy_capacity": 0.25},
                    "small": {"accuracy": 0.3, "destroy_capacity": 0.33},
                },
            }
        },
        "GBU-10": {
            "type": "Guided bombs",
            "model": "GBU-10",
            "users": ["USA", "UK", "Germany", "Italy", "France", "Israel", "Saudi Arabia", "Australia", "South Korea", "Turkey"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1980,
            "end_service": None,
            "cost": 27,
            "warhead": 428,
            "perc_efficiency_variability": 0.05,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 1, "destroy_capacity": 1},
                    "med": {"accuracy": 0.95, "destroy_capacity": 1},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1},
                },
                "Armored": {
                    "big": {"accuracy": 1, "destroy_capacity": 1},
                    "med": {"accuracy": 0.95, "destroy_capacity": 1},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1},
                },
                "Hard": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.7},
                    "med": {"accuracy": 0.95, "destroy_capacity": 0.8},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.9},
                },
                "Structure": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.8},
                    "med": {"accuracy": 1, "destroy_capacity": 0.9},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1},
                },
                "Air_Defense": {
                    "big": {"accuracy": 1, "destroy_capacity": 1},
                    "med": {"accuracy": 0.95, "destroy_capacity": 1},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1},
                },
                "Airbase": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Bridge": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.7},
                    "med": {"accuracy": 1, "destroy_capacity": 0.8},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.9},
                },
                "ship": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.85},
                    "med": {"accuracy": 0.6, "destroy_capacity": 1},
                    "small": {"accuracy": 0.4, "destroy_capacity": 1},
                },
            }
        },
        "GBU-16": {
            "type": "Guided bombs",
            "model": "GBU-16",
            "users": ["USA", "UK", "Germany", "Italy", "France", "Israel", "Saudi Arabia", "Australia", "South Korea", "Turkey"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1970,
            "end_service": None,
            "cost": 25,
            "warhead": 202,
            "perc_efficiency_variability": 0.05,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.95, "destroy_capacity": 0.95},
                    "med": {"accuracy": 0.9, "destroy_capacity": 1},
                    "small": {"accuracy": 0.85, "destroy_capacity": 1},
                },
                "Armored": {
                    "big": {"accuracy": 0.95, "destroy_capacity": 0.85},
                    "med": {"accuracy": 0.9, "destroy_capacity": 0.95},
                    "small": {"accuracy": 0.85, "destroy_capacity": 1},
                },
                "Hard": {
                    "big": {"accuracy": 0.95, "destroy_capacity": 0.35},
                    "med": {"accuracy": 0.9, "destroy_capacity": 0.4},
                    "small": {"accuracy": 0.85, "destroy_capacity": 0.45},
                },
                "Structure": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.4},
                    "med": {"accuracy": 1, "destroy_capacity": 0.45},
                    "small": {"accuracy": 0.95, "destroy_capacity": 0.5},
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.95, "destroy_capacity": 0.95},
                    "med": {"accuracy": 0.9, "destroy_capacity": 1},
                    "small": {"accuracy": 0.85, "destroy_capacity": 1},
                },
                "Airbase": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Bridge": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.35},
                    "med": {"accuracy": 1, "destroy_capacity": 0.4},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.45},
                },
                "ship": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 0.42},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.5},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.5},
                },
            }
        },
        "GBU-12": {
            "type": "Guided bombs",
            "model": "GBU-12",
            "users": ["USA", "UK", "Germany", "Italy", "France", "Israel", "Saudi Arabia", "Australia", "South Korea", "Turkey", "Denmark", "Norway"],
            "task": ["Strike"],
            "start_service": 1970,
            "end_service": None,
            "cost": 22,
            "warhead": 90,
            "perc_efficiency_variability": 0.05,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.95, "destroy_capacity": 0.8},
                    "med": {"accuracy": 0.9, "destroy_capacity": 0.85},
                    "small": {"accuracy": 0.85, "destroy_capacity": 0.95},
                },
                "Armored": {
                    "big": {"accuracy": 0.95, "destroy_capacity": 0.6},
                    "med": {"accuracy": 0.9, "destroy_capacity": 0.7},
                    "small": {"accuracy": 0.85, "destroy_capacity": 0.8},
                },
                "Hard": {
                    "big": {"accuracy": 0.95, "destroy_capacity": 0.15},
                    "med": {"accuracy": 0.9, "destroy_capacity": 0.2},
                    "small": {"accuracy": 0.85, "destroy_capacity": 0.25},
                },
                "Structure": {
                    "med": {"accuracy": 1, "destroy_capacity": 0.21},
                    "small": {"accuracy": 0.95, "destroy_capacity": 0.25},
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.95, "destroy_capacity": 0.7},
                    "med": {"accuracy": 0.9, "destroy_capacity": 0.75},
                    "small": {"accuracy": 0.85, "destroy_capacity": 0.8},
                },
                "Airbase": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Bridge": {
                    "med": {"accuracy": 0.95, "destroy_capacity": 0.21},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.25},
                },
                "ship": {
                    "big": {"accuracy": 0.8, "destroy_capacity": 0.21},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.25},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.25},
                },
            }
        },        
        "GBU-24": {  # Paveway III
            "type": "Guided bombs",
            "model": "GBU-24",
            "users": ["USA", "UK", "Germany", "France", "Italy", "Israel", "Saudi Arabia", "Australia", "South Korea"],
            "task": ["Strike"],
            "start_service": 1983,
            "end_service": None,
            "cost": 55,
            "warhead": 429,
            "perc_efficiency_variability": 0.05,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 1, "destroy_capacity": 1},
                    "med": {"accuracy": 0.95, "destroy_capacity": 1},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1},
                },
                "Armored": {
                    "big": {"accuracy": 1, "destroy_capacity": 1},
                    "med": {"accuracy": 0.95, "destroy_capacity": 1},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1},
                },
                "Hard": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.7},
                    "med": {"accuracy": 0.95, "destroy_capacity": 0.8},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.9},
                },
                "Structure": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.8},
                    "med": {"accuracy": 0.95, "destroy_capacity": 0.9},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1},
                },
                "Air_Defense": {
                    "big": {"accuracy": 1, "destroy_capacity": 1},
                    "med": {"accuracy": 0.95, "destroy_capacity": 1},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1},
                },
                "Airbase": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Bridge": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.7},
                    "med": {"accuracy": 0.95, "destroy_capacity": 0.8},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.9},
                },
                "ship": {
                    "big": {"accuracy": 0.5, "destroy_capacity": 0.85},
                    "med": {"accuracy": 0.4, "destroy_capacity": 1},
                    "small": {"accuracy": 0.2, "destroy_capacity": 1},
                },
            },
        },
        "GBU-27": {  # bunker buster
            "type": "Guided bombs",
            "model": "GBU-27",
            "users": ["USA", "UK", "Israel", "Saudi Arabia"],
            "task": ["Strike"],
            "start_service": 1985,
            "end_service": None,
            "cost": 55,
            "warhead": 429,
            "perc_efficiency_variability": 0.05,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 1, "destroy_capacity": 1},
                    "med": {"accuracy": 0.95, "destroy_capacity": 1},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1},
                },
                "Armored": {
                    "big": {"accuracy": 1, "destroy_capacity": 1},
                    "med": {"accuracy": 0.95, "destroy_capacity": 1},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1},
                },
                "Hard": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.85},
                    "med": {"accuracy": 0.95, "destroy_capacity": 0.9},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.95},
                },
                "Structure": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.8},
                    "med": {"accuracy": 0.95, "destroy_capacity": 0.9},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1},
                },
                "Air_Defense": {
                    "big": {"accuracy": 1, "destroy_capacity": 1},
                    "med": {"accuracy": 0.95, "destroy_capacity": 1},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1},
                },
                "Airbase": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.95, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.95, "destroy_capacity": 1e-8},
                },
                "Bridge": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.7},
                    "med": {"accuracy": 0.95, "destroy_capacity": 0.8},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.9},
                },
                "ship": {
                    "big": {"accuracy": 0.5, "destroy_capacity": 0.85},
                    "med": {"accuracy": 0.4, "destroy_capacity": 1},
                    "small": {"accuracy": 0.2, "destroy_capacity": 1},
                },
            },
        },
        "Mk-20": {  # aka CBU-100 anti-armor cluster
            "type": "Cluster bombs",
            "model": "Mk-20",
            "users": ["USA", "Israel", "South Korea", "Saudi Arabia"],
            "task": ["Strike"],
            "start_service": 1970,
            "end_service": None,
            "cost": 15,  # k$
            "weight": 222,  # kg
            "perc_efficiency_variability": 0.1,  # percentage of efficiency variability 0-1 (100%)
            "efficiency": {
                "Air_Defense": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 0.75,  # 1 max, 0.1 min ( hit success percentage )
                        "destroy_capacity": 2,  # element destroyed (single hit), 0.1 min ( element destroy capacity )
                    },
                    "med": {
                        "accuracy": 0.7,
                        "destroy_capacity": 5,
                    },
                    "small": {
                        "accuracy": 0.65,
                        "destroy_capacity": 7,
                    }
                },
                "Soft": {  # mobile target(artillery group)
                    "big": {
                        "accuracy": 0.75,
                        "destroy_capacity": 3,
                    },
                    "med": {
                        "accuracy": 0.7,
                        "destroy_capacity": 5,
                    },
                    "small": {
                        "accuracy": 0.65,
                        "destroy_capacity": 7,
                    }
                },
                "Armored": {  # mobile target armor
                    "big": {
                        "accuracy": 0.75,
                        "destroy_capacity": 3,
                    },
                    "med": {
                        "accuracy": 0.7,
                        "destroy_capacity": 5,
                    },
                    "small": {
                        "accuracy": 0.65,
                        "destroy_capacity": 7,
                    }
                },
            },
        },
        "BLG66": {  # aka Belouga cluster soft target
            "type": "Cluster bombs",
            "model": "BLG66",
            "users": ["France", "Chile", "Iraq", "Nigeria", "Pakistan", "Saudi Arabia"],
            "task": ["Strike"],
            "start_service": 1980,
            "end_service": None,
            "cost": 15,  # k$
            "weight": 305,  # kg
            "perc_efficiency_variability": 0.1,  # percentage of efficiency variability 0-1 (100%)
            "efficiency": {
                "Air_Defense": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 0.75,  # 1 max, 0.1 min ( hit success percentage )
                        "destroy_capacity": 2.1,  # element destroyed (single hit), 0.1 min ( element destroy capacity )
                    },
                    "med": {
                        "accuracy": 0.7,
                        "destroy_capacity": 3.2,
                    },
                    "small": {
                        "accuracy": 0.65,
                        "destroy_capacity": 4.5,
                    }
                },
                "Soft": {  # mobile target(artillery group)
                    "big": {
                        "accuracy": 0.7,
                        "destroy_capacity": 2.7,
                    },
                    "med": {
                        "accuracy": 0.6,
                        "destroy_capacity": 4.5,
                    },
                    "small": {
                        "accuracy": 0.5,
                        "destroy_capacity": 6.5,
                    }
                },
                "Armored": {  # anti-armor capability
                    "big": {
                        "accuracy": 0.75,  # 1 max, 0.1 min ( hit success percentage )
                        "destroy_capacity": 1,  # element destroyed (single hit), 0.1 min ( element destroy capacity )
                    },
                    "med": {
                        "accuracy": 0.7,
                        "destroy_capacity": 1.5,
                    },
                    "small": {
                        "accuracy": 0.65,
                        "destroy_capacity": 2,
                    }
                },
            },
        },
        "CBU-52B": {  # aka cluster soft target
            "type": "Cluster bombs",
            "model": "CBU-52B",
            "users": ["USA", "Israel", "South Korea"],
            "task": ["Strike"],
            "start_service": 1970,
            "end_service": None,
            "cost": 17,  # k$
            "weight": 347,  # kg
            "perc_efficiency_variability": 0.1,  # percentage of efficiency variability 0-1 (100%)
            "efficiency": {
                "Air_Defense": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 0.75,  # 1 max, 0.1 min ( hit success percentage )
                        "destroy_capacity": 2.5,  # element destroyed (single hit), 0.1 min ( element destroy capacity )
                    },
                    "med": {
                        "accuracy": 0.7,
                        "destroy_capacity": 3.7,
                    },
                    "small": {
                        "accuracy": 0.65,
                        "destroy_capacity": 5,
                    }
                },
                "Soft": {  # mobile target(artillery group)
                    "big": {
                        "accuracy": 0.7,
                        "destroy_capacity": 3,
                    },
                    "med": {
                        "accuracy": 0.6,
                        "destroy_capacity": 5,
                    },
                    "small": {
                        "accuracy": 0.5,
                        "destroy_capacity": 7,
                    }
                },
                "Armored": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 1},
                    "med": {"accuracy": 0.6, "destroy_capacity": 1.5},
                    "small": {"accuracy": 0.5, "destroy_capacity": 2},
                },
            },
        },
        "BK-90MJ1": {  # aka DWS 39 Mjölner MJ1 soft target, mj2 anti-armor, mj1+2 both, cluster bomb
            "type": "Cluster bombs",
            "model": "BK-90MJ1",
            "users": ["Sweden"],
            "task": ["Strike"],
            "start_service": 1990,
            "end_service": None,
            "cost": 15,  # k$
            "weight": None,  # kg
            "perc_efficiency_variability": 0.1,  # percentage of efficiency variability 0-1 (100%)
            "efficiency": {
                "Air_Defense": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 0.7,  # 1 max, 0.1 min ( hit success percentage )
                        "destroy_capacity": 2,  # element destroyed (single hit), 0.1 min ( element destroy capacity )
                    },
                    "med": {
                        "accuracy": 0.6,
                        "destroy_capacity": 3,
                    },
                    "small": {
                        "accuracy": 0.5,
                        "destroy_capacity": 4,
                    }
                },
                "Armored": {  # anti-armor capability
                    "big": {
                        "accuracy": 0.7,  # 1 max, 0.1 min ( hit success percentage )
                        "destroy_capacity": 2,  # element destroyed (single hit), 0.1 min ( element destroy capacity )
                    },
                    "med": {
                        "accuracy": 0.6,
                        "destroy_capacity": 3,
                    },
                    "small": {
                        "accuracy": 0.5,
                        "destroy_capacity": 4,
                    }
                },
                "Soft": {  # mobile target(artillery group)
                    "big": {
                        "accuracy": 0.7,
                        "destroy_capacity": 3,
                    },
                    "med": {
                        "accuracy": 0.6,
                        "destroy_capacity": 5,
                    },
                    "small": {
                        "accuracy": 0.5,
                        "destroy_capacity": 7,
                    }
                },
            },
        },
        "BK-90MJ1-2": {  # aka DWS 39 Mjölner MJ1 soft target, mj2 anti-armor, mj1+2 both, cluster bomb
            "type": "Cluster bombs",
            "model": "BK-90MJ1-2",
            "users": ["Sweden"],
            "task": ["Strike"],
            "start_service": 1990,
            "end_service": None,
            "cost": 15,  # k$
            "weight": None,  # kg
            "perc_efficiency_variability": 0.1,  # percentage of efficiency variability 0-1 (100%)
            "efficiency": {
                "Air_Defense": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 0.7,  # 1 max, 0.1 min ( hit success percentage )
                        "destroy_capacity": 2,  # element destroyed (single hit), 0.1 min ( element destroy capacity )
                    },
                    "med": {
                        "accuracy": 0.6,
                        "destroy_capacity": 3,
                    },
                    "small": {
                        "accuracy": 0.5,
                        "destroy_capacity": 4,
                    }
                },
                "Armored": {  # anti-armor capability
                    "big": {
                        "accuracy": 0.7,  # 1 max, 0.1 min ( hit success percentage )
                        "destroy_capacity": 3,  # element destroyed (single hit), 0.1 min ( element destroy capacity )
                    },
                    "med": {
                        "accuracy": 0.6,
                        "destroy_capacity": 4,
                    },
                    "small": {
                        "accuracy": 0.5,
                        "destroy_capacity": 5,
                    }
                },
                "Soft": {  # mobile target(artillery group)
                    "big": {
                        "accuracy": 0.7,
                        "destroy_capacity": 3,
                    },
                    "med": {
                        "accuracy": 0.6,
                        "destroy_capacity": 5,
                    },
                    "small": {
                        "accuracy": 0.5,
                        "destroy_capacity": 7,
                    }
                },
            },
        },
        "BK-90MJ2": {  # aka DWS 39 Mjölner MJ1 soft target, mj2 anti-armor, mj1+2 both, cluster bomb
            "type": "Cluster bombs",
            "model": "BK-90MJ2",
            "users": ["Sweden"],
            "task": ["Strike"],
            "start_service": 1990,
            "end_service": None,
            "cost": 15,  # k$
            "weight": None,  # kg
            "perc_efficiency_variability": 0.1,  # percentage of efficiency variability 0-1 (100%)
            "efficiency": {
                "Air_Defense": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 0.7,  # 1 max, 0.1 min ( hit success percentage )
                        "destroy_capacity": 2,  # element destroyed (single hit), 0.1 min ( element destroy capacity )
                    },
                    "med": {
                        "accuracy": 0.6,
                        "destroy_capacity": 3,
                    },
                    "small": {
                        "accuracy": 0.5,
                        "destroy_capacity": 4,
                    }
                },
                "Armored": {  # anti-armor capability
                    "big": {
                        "accuracy": 0.7,  # 1 max, 0.1 min ( hit success percentage )
                        "destroy_capacity": 3,  # element destroyed (single hit), 0.1 min ( element destroy capacity )
                    },
                    "med": {
                        "accuracy": 0.6,
                        "destroy_capacity": 4,
                    },
                    "small": {
                        "accuracy": 0.5,
                        "destroy_capacity": 5,
                    }
                },
                "Soft": {  # mobile target(artillery group)
                    "big": {
                        "accuracy": 0.7,
                        "destroy_capacity": 3,
                    },
                    "med": {
                        "accuracy": 0.6,
                        "destroy_capacity": 5,
                    },
                    "small": {
                        "accuracy": 0.5,
                        "destroy_capacity": 7,
                    }
                },
            },
        },
        "M/71": {  # HE Fragmentation bombs for AJS37 Viggen
            "type": "Bombs",
            "model": "M/71",
            "users": ["Sweden"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1970,
            "end_service": None,
            "cost": 2,  # k$
            "warhead": 40,  # kg
            "perc_efficiency_variability": 0.1,  # percentage of efficiency variability 0-1 (100%)
            "efficiency": {
                "Structure": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.08},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.15},
                },
                "ship": {  # mobile target
                    "big": {
                        "accuracy": 0.7,
                        "destroy_capacity": 0.07,
                    },
                    "med": {
                        "accuracy": 0.5,
                        "destroy_capacity": 0.12,
                    },
                    "small": {
                        "accuracy": 0.3,
                        "destroy_capacity": 0.25,
                    }
                },
                "Soft": {  # mobile target(artillery group)
                    "big": {
                        "accuracy": 0.8,
                        "destroy_capacity": 0.9,
                    },
                    "med": {
                        "accuracy": 0.8,
                        "destroy_capacity": 1,
                    },
                    "small": {
                        "accuracy": 0.7,
                        "destroy_capacity": 1,
                    }
                },
                "Armored": {  # mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    "big": {
                        "accuracy": 0.8,
                        "destroy_capacity": 0.2,
                    },
                    "med": {
                        "accuracy": 0.8,
                        "destroy_capacity": 0.4,
                    },
                    "small": {
                        "accuracy": 0.7,
                        "destroy_capacity": 0.5,
                    }
                },
                "Hard": {
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.05},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.1},
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.9, "destroy_capacity": 0.2},
                    "med": {"accuracy": 0.85, "destroy_capacity": 0.25},
                    "small": {"accuracy": 0.75, "destroy_capacity": 0.35},
                },
                "Airbase": {
                    "big": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.75, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.75, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.75, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.75, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.75, "destroy_capacity": 1e-8},
                },
            },
        },
        "SAMP-400LD": {  # SAMP-21 400 kg (Mk-83)
            "type": "Bombs",
            "model": "SAMP-400LD",
            "users": ["France", "Greece"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1950,
            "end_service": None,
            "cost": 3.3,  # k$
            "warhead": 202,  # kg
            "perc_efficiency_variability": 0.1,  # percentage of efficiency variability 0-1 (100%)
            "efficiency": {
                "Structure": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 1,  # 1 max, 0.1 min ( hit success percentage )
                        "destroy_capacity": 0.4,  # 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )
                    },
                    "med": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.45,
                    },
                    "small": {
                        "accuracy": 0.8,
                        "destroy_capacity": 0.5,
                    }
                },
                "Bridge": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 1,
                        "destroy_capacity": 0.35,
                    },
                    "med": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.4,
                    },
                    "small": {
                        "accuracy": 0.8,
                        "destroy_capacity": 0.45,
                    }
                },
                "ship": {  # mobile target
                    "big": {
                        "accuracy": 0.7,
                        "destroy_capacity": 0.42,
                    },
                    "med": {
                        "accuracy": 0.5,
                        "destroy_capacity": 0.5,
                    },
                    "small": {
                        "accuracy": 0.3,
                        "destroy_capacity": 0.5,
                    }
                },
                "Soft": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "med": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.95,
                    },
                    "small": {
                        "accuracy": 0.9,
                        "destroy_capacity": 1,
                    }
                },
                "Armored": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.85},
                    "med": {"accuracy": 0.75, "destroy_capacity": 0.9},
                    "small": {"accuracy": 0.65, "destroy_capacity": 1},
                },
                "Hard": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.35},
                    "med": {"accuracy": 0.75, "destroy_capacity": 0.45},
                    "small": {"accuracy": 0.65, "destroy_capacity": 0.55},
                },
                "Air_Defense": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "med": {
                        "accuracy": 0.85,
                        "destroy_capacity": 0.75,
                    },
                    "small": {
                        "accuracy": 0.75,
                        "destroy_capacity": 0.9,
                    }
                },
                "Airbase": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
            },
        },
        "SAMP-250HD": {  # SAMP-19 250 kg (Mk-82)
            "type": "Bombs",
            "model": "SAMP-250HD",
            "users": ["France", "Greece"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1950,
            "end_service": None,
            "cost": 2.7,  # k$
            "warhead": 92,  # kg
            "perc_efficiency_variability": 0.1,  # percentage of efficiency variability 0-1 (100%)
            "efficiency": {
                "Structure": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "med": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.21,
                    },
                    "small": {
                        "accuracy": 0.8,
                        "destroy_capacity": 0.52,
                    }
                },
                "Bridge": {
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.15},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.25},
                },
                "ship": {  # mobile target
                    "big": {
                        "accuracy": 0.7,
                        "destroy_capacity": 0.21,
                    },
                    "med": {
                        "accuracy": 0.5,
                        "destroy_capacity": 0.25,
                    },
                    "small": {
                        "accuracy": 0.3,
                        "destroy_capacity": 0.25,
                    }
                },
                "Soft": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "med": {
                        "accuracy": 0.8,
                        "destroy_capacity": 0.7,
                    },
                    "small": {
                        "accuracy": 0.7,
                        "destroy_capacity": 0.8,
                    }
                },
                "Armored": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.6},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.65},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.7},
                },
                "Hard": {
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.2},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.3},
                },
                "Air_Defense": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "med": {
                        "accuracy": 0.8,
                        "destroy_capacity": 0.65,
                    },
                    "small": {
                        "accuracy": 0.7,
                        "destroy_capacity": 0.8,
                    }
                },
                "Airbase": {
                    "big": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.75, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.75, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.75, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.75, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.75, "destroy_capacity": 1e-8},
                },
            },
        },

        # red
        "FAB-1500M54": {
            "type": "Bombs",
            "model": "FAB-1500M54",
            "users": ["USSR", "Russia"],
            "task": ["Strike"],
            "start_service": 1962,
            "end_service": None,
            "cost": 6,  # k$
            "warhead": 667,  # kg
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 1},
                    "med": {"accuracy": 0.75, "destroy_capacity": 1},
                    "small": {"accuracy": 0.65, "destroy_capacity": 1},
                },
                "Armored": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 1},
                    "med": {"accuracy": 0.75, "destroy_capacity": 1},
                    "small": {"accuracy": 0.65, "destroy_capacity": 1},
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 1},
                    "med": {"accuracy": 0.75, "destroy_capacity": 1},
                    "small": {"accuracy": 0.65, "destroy_capacity": 1},
                },
                "Hard": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.7},
                    "med": {"accuracy": 0.75, "destroy_capacity": 0.8},
                    "small": {"accuracy": 0.65, "destroy_capacity": 0.85},
                },
                "Structure": {
                    "big": {
                        "accuracy": 1,
                        "destroy_capacity": 0.88
                    },
                    "med": {
                        "accuracy": 0.9,
                        "destroy_capacity": 1
                    },
                    "small": {
                        "accuracy": 0.8,
                        "destroy_capacity": 1
                    }
                },
                "Bridge": {
                    "big": {
                        "accuracy": 1,
                        "destroy_capacity": 0.9
                    },
                    "med": {
                        "accuracy": 0.9,
                        "destroy_capacity": 1
                    },
                    "small": {
                        "accuracy": 0.8,
                        "destroy_capacity": 1
                    }
                },
                "ship": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.85},
                    "med": {"accuracy": 0.5, "destroy_capacity": 1},
                    "small": {"accuracy": 0.3, "destroy_capacity": 1},
                },
                "Airbase": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
            }
        },            
        "FAB-500M62": {
            "type": "Bombs",
            "model": "FAB-500M62",
            "users": ["USSR", "Russia", "India", "Syria", "Iraq", "Libya", "Algeria", "North Korea"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1962,
            "end_service": None,
            "cost": 3.3,  # k$
            "warhead": 201,  # kg
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Structure": {
                    "big": {
                        "accuracy": 1,
                        "destroy_capacity": 0.4
                    },
                    "med": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.45
                    },
                    "small": {
                        "accuracy": 0.8,
                        "destroy_capacity": 0.5
                    }
                },
                "Bridge": {
                    "big": {
                        "accuracy": 1,
                        "destroy_capacity": 0.35
                    },
                    "med": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.4
                    },
                    "small": {
                        "accuracy": 0.8,
                        "destroy_capacity": 0.45
                    }
                },
                "ship": {
                    "big": {
                        "accuracy": 0.7,
                        "destroy_capacity": 0.42
                    },
                    "med": {
                        "accuracy": 0.5,
                        "destroy_capacity": 0.5
                    },
                    "small": {
                        "accuracy": 0.3,
                        "destroy_capacity": 0.5
                    }
                },
                "Soft": {
                    "big": {
                        "accuracy": 0.85,
                        "destroy_capacity": 1
                    },
                    "med": {
                        "accuracy": 0.75,
                        "destroy_capacity": 1
                    },
                    "small": {
                        "accuracy": 0.65,
                        "destroy_capacity": 1
                    }
                },
                "Armored": {
                    "big": {
                        "accuracy": 0.85,
                        "destroy_capacity": 0.8
                    },
                    "med": {
                        "accuracy": 0.75,
                        "destroy_capacity": 0.9
                    },
                    "small": {
                        "accuracy": 0.7,
                        "destroy_capacity": 1
                    }
                },
                "Air_Defense": {
                    "big": {
                        "accuracy": 0.85,
                        "destroy_capacity": 0.95
                    },
                    "med": {
                        "accuracy": 0.75,
                        "destroy_capacity": 1
                    },
                    "small": {
                        "accuracy": 0.7,
                        "destroy_capacity": 1
                    }
                },
                "Hard": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.35},
                    "med": {"accuracy": 0.75, "destroy_capacity": 0.45},
                    "small": {"accuracy": 0.65, "destroy_capacity": 0.55},
                },
                "Airbase": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
            }
        },            
        "FAB-250M54": {
            "type": "Bombs",
            "model": "FAB-250M54",
            "users": ["USSR", "Russia", "India", "Syria", "Iraq", "Libya", "Algeria", "North Korea"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1962,
            "end_service": None,
            "cost": 2.7,  # k$
            "warhead": 94,  # kg
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Structure": {
                    "big": {
                        "accuracy": 1,
                        "destroy_capacity": 0.15
                    },
                    "med": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.22
                    },
                    "small": {
                        "accuracy": 0.8,
                        "destroy_capacity": 0.53
                    }
                },
                "Bridge": {
                    "med": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.22
                    },
                    "small": {
                        "accuracy": 0.8,
                        "destroy_capacity": 0.33
                    }
                },
                "ship": {
                    "big": {
                        "accuracy": 0.7,
                        "destroy_capacity": 0.22
                    },
                    "med": {
                        "accuracy": 0.5,
                        "destroy_capacity": 0.27
                    },
                    "small": {
                        "accuracy": 0.3,
                        "destroy_capacity": 0.35
                    }
                },
                "Soft": {
                    "med": {
                        "accuracy": 0.8,
                        "destroy_capacity": 0.85
                    },
                    "small": {
                        "accuracy": 0.7,
                        "destroy_capacity": 0.95
                    }
                },
                "Armored": {
                    "big": {
                        "accuracy": 0.85,
                        "destroy_capacity": 0.65
                    },
                    "med": {
                        "accuracy": 0.8,
                        "destroy_capacity": 0.7
                    },
                    "small": {
                        "accuracy": 0.7,
                        "destroy_capacity": 0.75
                    }
                },
                "Air_Defense": {
                    "big": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.7
                    },
                    "med": {
                        "accuracy": 0.85,
                        "destroy_capacity": 0.75
                    },
                    "small": {
                        "accuracy": 0.75,
                        "destroy_capacity": 0.8
                    }
                },
                "Hard": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.15},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.2},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.3},
                },
                "Airbase": {
                    "big": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.75, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.75, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.75, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.75, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.75, "destroy_capacity": 1e-8},
                },
            }
        },        
        "FAB-100": {
            "type": "Bombs",
            "model": "FAB-100",
            "users": ["USSR", "Russia", "India", "Syria", "Iraq", "North Korea"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1962,
            "end_service": None,
            "cost": 1.5,  # k$
            "warhead": 39,  # kg
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Structure": {
                    "med": {"accuracy": 0.9, "destroy_capacity": 0.1},
                    "small": {"accuracy": 0.8, "destroy_capacity": 0.20}
                },
                "ship": {
                    "med": {"accuracy": 0.5, "destroy_capacity": 0.1},
                    "small": {"accuracy": 0.3, "destroy_capacity": 0.2}
                },
                "Soft": {
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.4},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.5}
                },
                "Armored": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.2},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.25},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.35}
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.9, "destroy_capacity": 0.25},
                    "med": {"accuracy": 0.85, "destroy_capacity": 0.3},
                    "small": {"accuracy": 0.75, "destroy_capacity": 0.4}
                },
                "Hard": {
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.05},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.1},
                },
                "Bridge": {
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.1},
                },
                "Airbase": {
                    "big": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.75, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.75, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.75, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.75, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.75, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.75, "destroy_capacity": 1e-8},
                },
            },
        },
        "FAB-50": {
            "type": "Bombs",
            "model": "FAB-50",
            "users": ["USSR", "Russia", "North Korea"],
            "task": ["Strike"],
            "start_service": 1950,
            "end_service": None,
            "cost": 1,  # k$
            "warhead": 20,  # kg
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Soft": {
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.2},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.25}
                },
                "Armored": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.08},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.12},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.17}
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.9, "destroy_capacity": 0.12},
                    "med": {"accuracy": 0.85, "destroy_capacity": 0.15},
                    "small": {"accuracy": 0.75, "destroy_capacity": 0.2}
                },
                "Hard": {
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.05},
                },
                "Structure": {
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.08},
                },
                "Airbase": {
                    "big": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1e-8},
                },
            },
        },
        "RBK-250AO": {
            "type": "Cluster bombs",
            "model": "RBK-250AO",
            "users": ["USSR", "Russia", "India", "Syria", "Iraq", "Libya", "Algeria"],
            "task": ["Strike"],
            "start_service": 1970,
            "end_service": None,
            "cost": 16,  # k$
            "weight": 250,  # kg
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Air_Defense": {
                    "big": {"accuracy": 0.75, "destroy_capacity": 2},
                    "med": {"accuracy": 0.7, "destroy_capacity": 3},
                    "small": {"accuracy": 0.65, "destroy_capacity": 4}
                },
                "Soft": {
                    "big": {"accuracy": 0.75, "destroy_capacity": 3.2},
                    "med": {"accuracy": 0.7, "destroy_capacity": 4.3},
                    "small": {"accuracy": 0.65, "destroy_capacity": 7.5}
                },
            },
        },
        "RBK-500AO": {
            "type": "Cluster bombs",
            "model": "RBK-500AO",
            "users": ["USSR", "Russia", "India", "Syria", "Iraq", "Libya"],
            "task": ["Strike"],
            "start_service": 1970,
            "end_service": None,
            "cost": 17,  # k$
            "weight": 500,  # kg
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Air_Defense": {
                    "big": {"accuracy": 0.75, "destroy_capacity": 3},
                    "med": {"accuracy": 0.7, "destroy_capacity": 4},
                    "small": {"accuracy": 0.65, "destroy_capacity": 5}
                },
                "Soft": {
                    "big": {"accuracy": 0.75, "destroy_capacity": 4},
                    "med": {"accuracy": 0.7, "destroy_capacity": 6},
                    "small": {"accuracy": 0.65, "destroy_capacity": 8}
                },
            },
        },
        "RBK-500PTAB": {
            "type": "Cluster bombs",
            "model": "RBK-500PTAB",
            "users": ["USSR", "Russia", "India", "Syria", "Iraq"],
            "task": ["Strike"],
            "start_service": 1970,
            "end_service": None,
            "cost": 20,  # k$
            "weight": 500,  # kg
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Air_Defense": {
                    "big": {"accuracy": 0.75, "destroy_capacity": 3},
                    "med": {"accuracy": 0.7, "destroy_capacity": 4},
                    "small": {"accuracy": 0.65, "destroy_capacity": 5}
                },
                "Soft": {
                    "big": {"accuracy": 0.75, "destroy_capacity": 4},
                    "med": {"accuracy": 0.7, "destroy_capacity": 6},
                    "small": {"accuracy": 0.65, "destroy_capacity": 8}
                },
                "Armored": {
                    "big": {"accuracy": 0.75, "destroy_capacity": 3.2},
                    "med": {"accuracy": 0.8, "destroy_capacity": 4.3},
                    "small": {"accuracy": 0.7, "destroy_capacity": 6}
                },
            },
        },
        "BetAB-500": {
            "type": "Bombs",
            "model": "BetAB-500",
            "users": ["USSR", "Russia", "India", "Syria"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1962,
            "end_service": None,
            "cost": 2.7,  # k$
            "warhead": 92,  # kg
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Structure": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.15},
                    "med": {"accuracy": 0.9, "destroy_capacity": 0.22},
                    "small": {"accuracy": 0.8, "destroy_capacity": 0.53}
                },
                "Bridge": {
                    "med": {"accuracy": 0.9, "destroy_capacity": 0.22},
                    "small": {"accuracy": 0.8, "destroy_capacity": 0.33}
                },
                "ship": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.22},
                    "med": {"accuracy": 0.5, "destroy_capacity": 0.27},
                    "small": {"accuracy": 0.3, "destroy_capacity": 0.35}
                },
                "Soft": {
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.85},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.95}
                },
                "Armored": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.65},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.7},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.75}
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.9, "destroy_capacity": 0.7},
                    "med": {"accuracy": 0.85, "destroy_capacity": 0.75},
                    "small": {"accuracy": 0.75, "destroy_capacity": 0.8}
                },
                "Hard": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.45},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.55},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.65},
                },
                "Airbase": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-8},
                },
            },
        },
        "KAB-500L": {  # laser bomb (FAB-500 with laser guide)
            "type": "Guided bombs",
            "model": "KAB-500L",
            "users": ["USSR", "Russia", "India"],
            "task": ["Strike"],
            "start_service": 1975,
            "end_service": None,
            "cost": 25,  # k$
            "warhead": 201,  # kg
            "perc_efficiency_variability": 0.05,  # percentage of efficiecy variability 0-1 (100%)
            "efficiency": {
                "Structure": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 1,  # 1 max, 0.1 min ( hit success percentage )
                        "destroy_capacity": 0.4,  # 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )
                    },
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.45,
                    },
                    "small": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.5,
                    }
                },
                "Bridge": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 1,
                        "destroy_capacity": 0.35,
                    },
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.4,
                    },
                    "small": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.45,
                    }
                },
                "Soft": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 0.85,
                        "destroy_capacity": 1,
                    },
                    "med": {
                        "accuracy": 0.75,
                        "destroy_capacity": 1,
                    },
                    "small": {
                        "accuracy": 0.65,
                        "destroy_capacity": 1,
                    }
                },
                "Armored": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 0.85,
                        "destroy_capacity": 0.8,
                    },
                    "med": {
                        "accuracy": 0.75,
                        "destroy_capacity": 0.9,
                    },
                    "small": {
                        "accuracy": 0.7,
                        "destroy_capacity": 1,
                    }
                },
                "Air_Defense": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 0.85,
                        "destroy_capacity": 0.95,
                    },
                    "med": {
                        "accuracy": 0.75,
                        "destroy_capacity": 1,
                    },
                    "small": {
                        "accuracy": 0.7,
                        "destroy_capacity": 1,
                    }
                },
                "Hard": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.35},
                    "med": {"accuracy": 1, "destroy_capacity": 0.45},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.55},
                },
                "ship": {
                    "big": {"accuracy": 0.5, "destroy_capacity": 0.42},
                    "med": {"accuracy": 0.4, "destroy_capacity": 0.5},
                    "small": {"accuracy": 0.2, "destroy_capacity": 0.5},
                },
                "Airbase": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
            },
        },            
        "KAB-500Kr": {  # tv-guided bomb fire&forget (FAB-500)
            "type": "Guided bombs",
            "model": "KAB-500Kr",
            "users": ["USSR", "Russia", "India"],
            "task": ["Strike"],
            "start_service": 1980,
            "end_service": None,
            "cost": 23,  # k$
            "warhead": 201,  # kg
            "perc_efficiency_variability": 0.05,  # percentage of efficiecy variability 0-1 (100%)
            "efficiency": {
                "Structure": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 1,  # 1 max, 0.1 min ( hit success percentage )
                        "destroy_capacity": 0.4,  # 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )
                    },
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.45,
                    },
                    "small": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.5,
                    }
                },
                "Bridge": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 1,
                        "destroy_capacity": 0.35,
                    },
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.4,
                    },
                    "small": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.45,
                    }
                },
                "Soft": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 0.85,
                        "destroy_capacity": 1,
                    },
                    "med": {
                        "accuracy": 0.75,
                        "destroy_capacity": 1,
                    },
                    "small": {
                        "accuracy": 0.65,
                        "destroy_capacity": 1,
                    }
                },
                "Armored": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 0.85,
                        "destroy_capacity": 0.8,
                    },
                    "med": {
                        "accuracy": 0.75,
                        "destroy_capacity": 0.9,
                    },
                    "small": {
                        "accuracy": 0.7,
                        "destroy_capacity": 1,
                    }
                },
                "Air_Defense": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 0.85,
                        "destroy_capacity": 0.95,
                    },
                    "med": {
                        "accuracy": 0.75,
                        "destroy_capacity": 1,
                    },
                    "small": {
                        "accuracy": 0.7,
                        "destroy_capacity": 1,
                    }
                },
                "Hard": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.35},
                    "med": {"accuracy": 1, "destroy_capacity": 0.45},
                    "small": {"accuracy": 0.9, "destroy_capacity": 0.55},
                },
                "ship": {
                    "big": {"accuracy": 0.5, "destroy_capacity": 0.42},
                    "med": {"accuracy": 0.4, "destroy_capacity": 0.5},
                    "small": {"accuracy": 0.2, "destroy_capacity": 0.5},
                },
                "Airbase": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.9, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                },
            },
        },            
        "KGBU-2AO": {  # cluster bomb soft target
            "type": "Cluster bombs",
            "model": "KGBU-2AO",
            "users": ["USSR", "Russia"],
            "task": ["Strike"],
            "start_service": 1970,
            "end_service": None,
            "cost": 12,  # k$
            "weight": 250,  # ??--kg
            "perc_efficiency_variability": 0.1,  # percentage of efficiecy variability 0-1 (100%)
            "efficiency": {
                "Air_Defense": {  # non Anti-tank but antenna, launcher gear and PSU system are like soft units
                    "big": {
                        "accuracy": 0.75,  # 1 max, 0.1 min ( hit success percentage )
                        "destroy_capacity": 2,  # element destroyed (single hit), 0.1 min ( element destroy capacity )
                    },
                    "med": {
                        "accuracy": 0.7,
                        "destroy_capacity": 3,
                    },
                    "small": {
                        "accuracy": 0.65,
                        "destroy_capacity": 4,
                    }
                },
                "Soft": {  # mobile target(artillery group)
                    "big": {
                        "accuracy": 0.75,
                        "destroy_capacity": 3.2,
                    },
                    "med": {
                        "accuracy": 0.7,
                        "destroy_capacity": 4.3,
                    },
                    "small": {
                        "accuracy": 0.65,
                        "destroy_capacity": 7.5,
                    }
                },
            },
        },            
        "KGBU-2PTAB": {  # cluster bomb armor target
            "type": "Cluster bombs",
            "model": "KGBU-2PTAB",
            "users": ["USSR", "Russia"],
            "task": ["Strike"],
            "start_service": 1970,
            "end_service": None,
            "cost": 16,  # k$
            "weight": 250,  # ??--kg
            "perc_efficiency_variability": 0.1,  # percentage of efficiecy variability 0-1 (100%)
            "efficiency": {
                "Air_Defense": {  # non Anti-tank but antenna, launcher gear and PSU system are like soft units
                    "big": {
                        "accuracy": 0.75,  # 1 max, 0.1 min ( hit success percentage )
                        "destroy_capacity": 2,  # element destroyed (single hit), 0.1 min ( element destroy capacity )
                    },
                    "med": {
                        "accuracy": 0.7,
                        "destroy_capacity": 3,
                    },
                    "small": {
                        "accuracy": 0.65,
                        "destroy_capacity": 4,
                    }
                },
                "Soft": {  # mobile target(artillery group)
                    "big": {
                        "accuracy": 0.75,
                        "destroy_capacity": 3.2,
                    },
                    "med": {
                        "accuracy": 0.7,
                        "destroy_capacity": 4.3,
                    },
                    "small": {
                        "accuracy": 0.65,
                        "destroy_capacity": 7.5,
                    }
                },
                "Armored": {
                    "big": {
                        "accuracy": 0.75,
                        "destroy_capacity": 3.2,
                    },
                    "med": {
                        "accuracy": 0.8,
                        "destroy_capacity": 4.3,
                    },
                    "small": {
                        "accuracy": 0.7,
                        "destroy_capacity": 7,
                    }
                },
            },
        },            
        "KGBU-96r": {  # ?? cluster bomb soft target VERIFY
            "type": "Cluster bombs",
            "model": "KGBU-96r",
            "users": ["USSR", "Russia"],
            "task": ["Strike"],
            "start_service": 1970,
            "end_service": None,
            "cost": 12,  # k$
            "weight": 250,  # ??--kg
            "perc_efficiency_variability": 0.1,  # percentage of efficiecy variability 0-1 (100%)
            "efficiency": {
                "Air_Defense": {  # non Anti-tank but antenna, launcher gear and PSU system are like soft units
                    "big": {
                        "accuracy": 0.75,  # 1 max, 0.1 min ( hit success percentage )
                        "destroy_capacity": 2,  # element destroyed (single hit), 0.1 min ( element destroy capacity )
                    },
                    "med": {
                        "accuracy": 0.7,
                        "destroy_capacity": 3,
                    },
                    "small": {
                        "accuracy": 0.65,
                        "destroy_capacity": 4,
                    }
                },
                "Soft": {  # mobile target(artillery group)
                    "big": {
                        "accuracy": 0.75,
                        "destroy_capacity": 3.2,
                    },
                    "med": {
                        "accuracy": 0.7,
                        "destroy_capacity": 4.3,
                    },
                    "small": {
                        "accuracy": 0.65,
                        "destroy_capacity": 7.5,
                    }
                },
            },
        },        
    },
    'ROCKETS': {   
        "Zuni-Mk71": {  # Rockets 127 mm HE
            "type": "Rockets",
            "model": "Zuni-Mk71",
            "users": ["USA"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1956,
            "end_service": None,
            "cost": 0.4,  # k$
            "caliber": 127,  # mm
            "warhead": 6.8,  # kg
            "warhead_type": "HE",
            "range": 8,  # Km
            "speed": 722, # m/s
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.4},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.5},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.6},
                },
                "Armored": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.3},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.4},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.6},
                },
                "Hard": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.08},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.1},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.12},
                },
                "Structure": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.003},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.01},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.15},
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.4},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.5},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.6},
                },
                "Airbase": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "ship": {
                    "big": {"accuracy": 0.5, "destroy_capacity": 0.1},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.12},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.12},
                },
            },
        },
        "Hydra-70MK5": {  # Rockets 70 mm Mk-5 HEAT hard target
            "type": "Rockets",
            "model": "Hydra-70MK5",
            "users": ["USA", "Israel", "Turkey", "South Korea"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1956,
            "end_service": None,
            "cost": 2.8,  # k$
            "caliber": 70,  # mm
            "warhead": 4.0,  # kg (M247 HEDP warhead = 8.8 lb)
            "warhead_type": "HEAT",
            "range": 8,  # Km
            "speed": 739, # m/s
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.3},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.4},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.6},
                },
                "Armored": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.2},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.3},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.4},
                },
                "Hard": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.1},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.12},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.15},
                },
                "Structure": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.003},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.01},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.15},
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.3},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.4},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.5},
                },
                "Airbase": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "ship": {
                    "big": {"accuracy": 0.5, "destroy_capacity": 0.08},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.1},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.15},
                },
            },
        },
        "Hydra-70MK1": {  # Rockets 70 mm Mk-1 HE soft target
            "type": "Rockets",
            "model": "Hydra-70MK1",
            "users": ["USA", "Israel", "Turkey", "South Korea"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1956,
            "end_service": None,
            "cost": 2.8,  # k$
            "caliber": 70,  # mm
            "warhead": 3.9,  # kg (M151 HE warhead = 8.7 lb)
            "warhead_type": "HE",
            "range": 8,  # Km
            "speed": 739, # m/s
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.3},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.4},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.6},
                },
                "Armored": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.1},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.15},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.2},
                },
                "Hard": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.04},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.06},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.08},
                },
                "Structure": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.002},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.005},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.08},
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.3},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.4},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.5},
                },
                "Airbase": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "ship": {
                    "big": {"accuracy": 0.5, "destroy_capacity": 0.06},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.08},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.1},
                },
            },
        },
        "SNEB-256": {  # Rockets 68 mm HE-FRAG
            "type": "Rockets",
            "model": "SNEB-256",
            "users": ["France"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1955,
            "end_service": None,
            "cost": 2.5,  # k$
            "caliber": 68,  # mm
            "warhead": 3.0,  # kg (Type 26P frag warhead)
            "warhead_type": "FRAG",
            "range": 8,  # Km
            "speed": 600, # m/s
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.3},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.4},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.5},
                },
                "Armored": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.2},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.3},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.4},
                },
                "Hard": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.06},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.08},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.1},
                },
                "Structure": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.002},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.008},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.15},
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.3},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.4},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.5},
                },
                "Airbase": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "ship": {
                    "big": {"accuracy": 0.5, "destroy_capacity": 0.08},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.12},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.2},
                },
            },
        },
        "SNEB-253": {  # Rockets 68 mm HE, aka Matra F1
            "type": "Rockets",
            "model": "SNEB-253",
            "users": ["France"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1955,
            "end_service": None,
            "cost": 1.7,  # k$
            "caliber": 68,  # mm
            "warhead": 1.8,  # kg (Type 23 HEAT warhead)
            "warhead_type": "HE",
            "range": 8,  # Km
            "speed": 600, # m/s
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.3},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.4},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.5},
                },
                "Armored": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.1},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.2},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.3},
                },
                "Hard": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.03},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.05},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.07},
                },
                "Structure": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.001},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.004},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.07},
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.25},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.35},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.45},
                },
                "Airbase": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "ship": {
                    "big": {"accuracy": 0.4, "destroy_capacity": 0.05},
                    "med": {"accuracy": 0.5, "destroy_capacity": 0.06},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.08},
                },
            },
        },           
        "S-5 M": {  # Rockets 57 mm HE-FRAG
            "type": "Rockets",
            "model": "S-5 M",
            "users": ["USSR", "Russia", "India", "Syria", "Iraq", "Libya", "Algeria", "Egypt"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1960,
            "end_service": None,
            "cost": 0.4,
            "caliber": 57,  # mm
            "warhead": 0.8,  # kg (S-5M warhead = 815g)
            "warhead_type": "FRAG",
            "range": 4,
            "speed": 586, # m/s
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.3},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.4},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.6},
                },
                "Armored": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.2},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.3},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.4},
                },
                "Hard": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.04},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.06},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.08},
                },
                "Structure": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.001},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.005},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.05},
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.25},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.35},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.5},
                },
                "Airbase": {
                    "big": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.5, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.5, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.5, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.5, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.5, "destroy_capacity": 1e-8},
                },
                "ship": {
                    "big": {"accuracy": 0.4, "destroy_capacity": 0.06},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.1},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.15},
                },
            },
        },          
        "S-5 KO": {  # Rockets 57 mm HEAT
            "type": "Rockets",
            "model": "S-5 KO",
            "users": ["USSR", "Russia", "India", "Syria", "Iraq", "Libya", "Algeria"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1973,
            "end_service": None,
            "cost": 0.8,
            "caliber": 57,  # mm
            "warhead": 1.36,  # kg (S-5KO HEAT warhead)
            "warhead_type": "HEAT",
            "range": 4,
            "speed": 586, # m/s
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.3},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.4},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.6},
                },
                "Armored": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.25},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.35},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.5},
                },
                "Hard": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.06},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.08},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.1},
                },
                "Structure": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.001},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.005},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.05},
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.25},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.35},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.5},
                },
                "Airbase": {
                    "big": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.5, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.5, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.5, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.5, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.5, "destroy_capacity": 1e-8},
                },
                "ship": {
                    "big": {"accuracy": 0.4, "destroy_capacity": 0.06},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.1},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.15},
                },
            },
        },         
        "S-8 OFP2": {  # Rockets 80 mm HE-FRAG
            "type": "Rockets",
            "model": "S-8 OFP2",
            "users": ["USSR", "Russia", "India", "Syria"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1973,
            "end_service": None,
            "cost": 0.6,
            "caliber": 80,  # mm
            "warhead": 3.6,  # kg (S-8 HE-frag warhead)
            "warhead_type": "FRAG",
            "range": 4,
            "speed": 610, # m/s
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.3},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.4},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.6},
                },
                "Armored": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.15},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.25},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.35},
                },
                "Hard": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.05},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.07},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.09},
                },
                "Structure": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.002},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.006},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.06},
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.3},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.4},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.5},
                },
                "Airbase": {
                    "big": {"accuracy": 0.55, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.55, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.55, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.55, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.55, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.55, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.55, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.55, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.55, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.55, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.55, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.55, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.55, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.55, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.55, "destroy_capacity": 1e-8},
                },
                "ship": {
                    "big": {"accuracy": 0.45, "destroy_capacity": 0.06},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.08},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.1},
                },
            },
        },           
        "S-8 KOM": {  # Rockets 80 mm HEAT
            "type": "Rockets",
            "model": "S-8 KOM",
            "users": ["USSR", "Russia", "India", "Syria"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1973,
            "end_service": None,
            "cost": 1,
            "caliber": 80,  # mm
            "warhead": 3.6,  # kg (S-8KOM HEAT warhead)
            "warhead_type": "HEAT",
            "range": 4,
            "speed": 610, # m/s
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.3},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.4},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.6},
                },
                "Armored": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.25},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.35},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.5},
                },
                "Hard": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.07},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.09},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.12},
                },
                "Structure": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.002},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.006},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.06},
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.3},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.4},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.5},
                },
                "Airbase": {
                    "big": {"accuracy": 0.55, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.55, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.55, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.55, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.55, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.55, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.55, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.55, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.55, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.55, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.55, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.55, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.55, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.55, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.55, "destroy_capacity": 1e-8},
                },
                "ship": {
                    "big": {"accuracy": 0.45, "destroy_capacity": 0.07},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.1},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.15},
                },
            },
        },           
        "S-13": {  # Rockets 122 mm
            "type": "Rockets",
            "model": "S-13",
            "users": ["USSR", "Russia", "India"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1973,
            "end_service": None,
            "cost": 0.8,
            "caliber": 122,  # mm
            "warhead": 21,  # kg (penetrating warhead)
            "warhead_type": "AP",
            "range": 3,
            "speed": 650, # m/s
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.1},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.13},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.15},
                },
                "Armored": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.08},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.1},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.12},
                },
                "Hard": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.06},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.08},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.1},
                },
                "Structure": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.002},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.008},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.08},
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.1},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.13},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.15},
                },
                "Airbase": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Port": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Farp": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.6, "destroy_capacity": 1e-8},
                },
                "ship": {
                    "big": {"accuracy": 0.4, "destroy_capacity": 0.05},
                    "med": {"accuracy": 0.5, "destroy_capacity": 0.08},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.1},
                },
            },
        },
        "S-25L": {  # Rockets 340 mm laser-guided, hard target (antitank), 250OFM, Launcher O-25 (qty: 1)
            "type": "Rockets",
            "model": "S-25L",
            "users": ["USSR", "Russia"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1975,
            "end_service": None,
            "cost": 2.8,  # k$
            "caliber": 340,  # mm
            "warhead": 150,  # kg (S-25-OFM warhead)
            "warhead_type": "HE",
            "range": 7,  # Km
            "speed": 530, # m/s
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.8},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.9},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1},
                },
                "Armored": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.4},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.6},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.8},
                },
                "Hard": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.25},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.3},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.35},
                },
                "Structure": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.004},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.015},
                    "small": {"accuracy": 0.7, "destroy_capacity": 0.08},
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.8},
                    "med": {"accuracy": 0.8, "destroy_capacity": 0.9},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1},
                },
                "Airbase": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-7},
                },
                "Port": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-7},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-7},
                },
                "Farp": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-7},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.8, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.8, "destroy_capacity": 1e-7},
                },
                "ship": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.3},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.4},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.5},
                },
            },
        },
        "S-24": {  # (Vers. A/B) Rockets 240 mm HE, launcher: PU-12-40U (qty: 1), APU-7D, APU-68U
            "type": "Rockets",
            "model": "S-24",
            "users": ["USSR", "Russia", "India", "Syria", "Iraq", "Libya"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1960,
            "end_service": None,
            "cost": 1.5,  # k$
            "caliber": 240,  # mm
            "warhead": 123,  # kg (blast-frag warhead; 25.5 kg explosive filler)
            "warhead_type": "HE",
            "range": 3,  # Km
            "speed": 420, # m/s
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.8},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.9},
                    "small": {"accuracy": 0.5, "destroy_capacity": 1},
                },
                "Armored": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.2},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.3},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.4},
                },
                "Hard": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.15},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.2},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.25},
                },
                "Structure": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.003},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.012},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.07},
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.7},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.85},
                    "small": {"accuracy": 0.5, "destroy_capacity": 1},
                },
                "Airbase": {
                    "big": {"accuracy": 0.65, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.65, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.65, "destroy_capacity": 1e-7},
                },
                "Port": {
                    "big": {"accuracy": 0.65, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.65, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.65, "destroy_capacity": 1e-7},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.65, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.65, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.65, "destroy_capacity": 1e-7},
                },
                "Farp": {
                    "big": {"accuracy": 0.65, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.65, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.65, "destroy_capacity": 1e-7},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.65, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.65, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.65, "destroy_capacity": 1e-7},
                },
                "ship": {
                    "big": {"accuracy": 0.5, "destroy_capacity": 0.2},
                    "med": {"accuracy": 0.7, "destroy_capacity": 0.3},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.4},
                },
            },
        },        
    },
    'CANNONS': {
        "UPK-23": {  # 23 mm gun pod
            "type": "Rockets",
            "model": "UPK-23",
            "users": ["USSR", "Russia", "India", "Syria", "Iraq", "Libya", "Algeria"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1972,
            "end_service": None,
            "cost": None,  # k$
            "caliber": 23,  # mm
            "warhead": None,  # kg
            "warhead_type": "AP",
            "range": 2,  # Km
            "speed": 715, # m/s (muzzle velocity)
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.1},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.2},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.4},
                },
                "Armored": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.05},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.1},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.2},
                },
                "Hard": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.01},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.02},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.03},
                },
                "Structure": {
                    "big": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.001},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.01},
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.1},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.2},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.35},
                },
                "Airbase": {
                    "big": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                },
                "Port": {
                    "big": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                },
                "Farp": {
                    "big": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                },
                "ship": {
                    "big": {"accuracy": 0.3, "destroy_capacity": 0.02},
                    "med": {"accuracy": 0.5, "destroy_capacity": 0.08},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.15},
                },
            },
        },    
        "Gsh-23L": {  # 23 mm twin-barrel autocannon
            "type": "Rockets",
            "model": "Gsh-23L",
            "users": ["USSR", "Russia", "India", "Syria", "Iraq"],
            "task": ["Strike"],
            "start_service": 1972,
            "end_service": None,
            "cost": None,
            "caliber": 23,  # mm
            "warhead": None,
            "warhead_type": "AP",
            "range": 2,
            "speed": 715, # m/s (muzzle velocity)
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Soft": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.1},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.2},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.4},
                },
                "Armored": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.05},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.1},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.2},
                },
                "Hard": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.01},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.02},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.03},
                },
                "Structure": {
                    "big": {"accuracy": 0.7, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.001},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.01},
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.1},
                    "med": {"accuracy": 0.6, "destroy_capacity": 0.2},
                    "small": {"accuracy": 0.5, "destroy_capacity": 0.35},
                },
                "Airbase": {
                    "big": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                },
                "Port": {
                    "big": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                },
                "Shipyard": {
                    "big": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                },
                "Farp": {
                    "big": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                },
                "Stronghold": {
                    "big": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "med": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                    "small": {"accuracy": 0.5, "destroy_capacity": _INFRA_MIN},
                },
                "ship": {
                    "big": {"accuracy": 0.3, "destroy_capacity": 0.02},
                    "med": {"accuracy": 0.5, "destroy_capacity": 0.08},
                    "small": {"accuracy": 0.6, "destroy_capacity": 0.15},
                },
            },
        },        
    }
}






