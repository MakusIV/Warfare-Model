from functools import lru_cache
import sys
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union, Tuple
from Code.Dynamic_War_Manager.Source.Asset.Aircraft import Aircraft
from Code.Dynamic_War_Manager.Source.Utility import Utility
from Code.Dynamic_War_Manager.Source.Context.Context import AIR_TASK, GROUND_WEAPON_TASK #GROUND_ACTION, ACTION_TASKS,
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.Utility.Utility import true_air_speed, indicated_air_speed, true_air_speed_at_new_altitude
from sympy import Point3D
from dataclasses import dataclass

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Aircraft_Data').logger



# mtbf, mttr
'''
Calibro in pollici	Calibro in millimetri	Uso tipico
.22	5,56	Mitragliatrici leggere, fucili
.30/.308	7,62	Mitragliatrici medie, fucili
.36	9,14	Armi corte e alcune mitragliatrici legger
.50	12,7	Mitragliatrici pesanti (calibro .50)


Calibro (mm)	Calibro (pollici)	Esempi di mitragliatrici	Note
12,7 × 99 mm	.50 BMG (0.50)	Browning M2 (USA), FN M2	Il più diffuso calibro HMG occidentale
12,7 × 108 mm	~0.50	DShK, NSV (ex URSS)	Calibro sovietico equivalente al .50 BMG
14,5 × 114 mm	~0.57	KPV (Russia)	Calibro più grande, elevata potenza'''

# HE: Esplosivo, HEAT: High Explosive Anti Tank (carica cava), 2HEAT: carica a cava doppia, AP: 'Armour Piercing', APFSDS = AP a energia cinetica 

WEAPON_PARAM = {

    'CANNONS':          {'caliber': 0.3/300, # coeff / max value
                        'muzzle_speed': 0.15/1000, 
                        'fire_rate': 0.25/10,
                        'range': 0.1/3000,
                        'ammo_type': 0.2, # coefficente utilizzato per valuatare il peso del munizionamento nel calcolo del punteggio dell'arma
                        },

    'MISSILES':         {'caliber': 0.2/300, 
                        'warhead': 0.4/250,
                        'range': 0.2/4000,
                        'ammo_type': 0.2,
                        },

    'ROCKETS':         {'caliber': 0.2/240, 
                        'warhead': 0.4/150,
                        'range': 0.2/300,
                        'ammo_type': 0.2,
                        },

    'MORTARS':          {'caliber': 0.35/155, # coeff / max value
                        'fire_rate': 0.25/20,
                        'range': 0.2/10000,
                        'ammo_type': 0.2,
                        },

    'ARTILLERY':        {'caliber': 0.3/300, # coeff / max value (same structure as CANNONS)
                        'muzzle_speed': 0.15/1000,
                        'fire_rate': 0.25/10,
                        'range': 0.1/70000,
                        'ammo_type': 0.2,
                        },

    'MACHINE_GUNS':     {'caliber': 0.4/9.14, # coeff / max value (caliber in mm 9.14-> 0.36 "  nato
                        'fire_rate': 0.4/500,
                        'range': 0.2/1000,
                        },

    'BOMBS':            {'tnt': 0.7/2000,
                        'accuracy': 0.3/1,

                        },

}

AMMO_PARAM = {
    'HE': 0.2,
    'HEAT': 0.4,
    'AP': 0.2,
    '2HEAT': 0.9,
    'APFSDS': 0.6,
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

#@dataclass
#Class Weapon_Data:

def get_cannon_score(model: str) -> float:
    """
    returns cannon score

    'model': '2A46M',
    "start_service": 1974,
    "end_service": int('inf'),
    'reload': 'Automatic', # Semi_Automatic, Manual
    'caliber': 125, # mm
    'muzzle_speed': 1750, # m/s 
    'fire_rate': 8, # shot per minute
    'range': {'direct': 2120, 'indirect': 10000 }, # m
    'ammo_type': ['HEAT', 'HE', 'APFSDS'],

    Args:
        model (str): cannon model 

    Returns:
        float: cannon score
    """
    if not isinstance(model, str):
        raise TypeError(f"model is not str, got {type(model).__name__}")
    

    weapon_name = 'CANNONS'
    weapon = GROUND_WEAPONS[weapon_name][model]

    if not weapon:
        logger.warning(f"weapon {weapon_name} {model} unknow")
        return 0.0

    weapon_power = 0.0

    for param_name, coeff_value in WEAPON_PARAM[weapon_name].items():
        
        if param_name == 'range':
            weapon_power += ( weapon[param_name]['direct'] * 0.7 + weapon[param_name]['indirect'] * 0.3 ) * coeff_value
        
        elif param_name == 'ammo_type':
            max = min(AMMO_PARAM.values())

            for ammo_type in weapon[param_name]:
                found = AMMO_PARAM.get(ammo_type)
                if found and max < found:
                    max = found

            weapon_power += max * coeff_value

        else:
            weapon_power +=  weapon[param_name] * coeff_value

    return weapon_power 

def get_missiles_score(model: str) -> float:
    
    '''9K119M ': { # AT-11 Sniper
            'model': '9K119M',
            "start_service": 1974,
            "end_service": int('inf'),
            'guide': 'Laser', # Semi_Automatic, Manual
            'caliber': 125, # mm
            'warhead': 4.5, # kg
            'speed': 1300, # m/s             
            'range': 4500, # m
            'ammo_type': ['2HEAT'],'''
    
    if not isinstance(model, str):
        raise TypeError(f"model is not str, got {type(model).__name__}")    

    weapon_name = 'MISSILES'
    weapon = GROUND_WEAPONS[weapon_name].get(model)#
   

    if not weapon:
        logger.warning(f"weapon {weapon_name} {model} unknow")
        return 0.0

    weapon_power = 0.0


    for param_name, coeff_value in WEAPON_PARAM[weapon_name].items():

        if param_name == 'range':
            weapon_power += ( weapon[param_name]['direct'] * 0.7 + weapon[param_name]['indirect'] * 0.3 ) * coeff_value
        
        elif param_name == 'ammo_type':
            max = min(AMMO_PARAM.values())

            for ammo_type in weapon[param_name]:
                found = AMMO_PARAM.get(ammo_type)

                if found and max < found:
                    max = found

            weapon_power += max * coeff_value

        else:
            weapon_power +=  weapon[param_name] * coeff_value

    return weapon_power 

def get_machine_gun_score(model: str) -> float:
    """
    returns machine_gun score

    'PKT-7.62': {
            'model': 'PKT-7.62',
            "start_service": 1992,
            "end_service": 3000,            
            'caliber': 7.62, # mm
            'fire_rate': 700, # shot per minute
            'range': {'direct': 1200, 'indirect': None }, # m
        

    Args:
        model (str): machine gun model 

    Returns:
        float: machine gun score
    """
    if not isinstance(model, str):
        raise TypeError(f"model is not str, got {type(model).__name__}")
    

    weapon_name = 'MACHINE_GUNS'
    weapon = GROUND_WEAPONS[weapon_name][model]

    if not weapon:
        logger.warning(f"weapon {weapon_name} {model} unknow")
        return 0.0

    weapon_power = 0.0

    for param_name, coeff_value in WEAPON_PARAM[weapon_name].items():
        
        if param_name == 'range':
            weapon_power += ( weapon[param_name]['direct'] * 0.7 + weapon[param_name]['indirect'] * 0.3 ) * coeff_value

        else:
            weapon_power +=  weapon[param_name] * coeff_value

    return weapon_power

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
    weapon = GROUND_WEAPONS[weapon_name].get(model)

    if not weapon:
        logger.warning(f"weapon {weapon_name} {model} unknow")
        return 0.0

    weapon_power = 0.0

    for param_name, coeff_value in WEAPON_PARAM[weapon_name].items():

        if param_name == 'range':
            weapon_power += ( weapon[param_name]['direct'] * 0.7 + weapon[param_name]['indirect'] * 0.3 ) * coeff_value

        elif param_name == 'ammo_type':
            max = min(AMMO_PARAM.values())

            for ammo_type in weapon[param_name]:
                found = AMMO_PARAM.get(ammo_type)

                if found and max < found:
                    max = found

            weapon_power += max * coeff_value

        else:
            weapon_power +=  weapon[param_name] * coeff_value

    return weapon_power

def get_mortars_score(model: str) -> float:
    """
    returns mortar score (same logic as get_cannon_score, without muzzle_speed)

    Args:
        model (str): mortar model

    Returns:
        float: mortar score
    """
    if not isinstance(model, str):
        raise TypeError(f"model is not str, got {type(model).__name__}")

    weapon_name = 'MORTARS'
    weapon = GROUND_WEAPONS[weapon_name].get(model)

    if not weapon:
        logger.warning(f"weapon {weapon_name} {model} unknow")
        return 0.0

    weapon_power = 0.0

    for param_name, coeff_value in WEAPON_PARAM[weapon_name].items():

        if param_name == 'range':
            weapon_power += ( weapon[param_name]['direct'] * 0.7 + weapon[param_name]['indirect'] * 0.3 ) * coeff_value

        elif param_name == 'ammo_type':
            max = min(AMMO_PARAM.values())

            for ammo_type in weapon[param_name]:
                found = AMMO_PARAM.get(ammo_type)
                if found and max < found:
                    max = found

            weapon_power += max * coeff_value

        else:
            weapon_power +=  weapon[param_name] * coeff_value

    return weapon_power

def get_artillery_score(model: str) -> float:
    """
    returns artillery score (same logic as get_cannon_score)

    Args:
        model (str): artillery model

    Returns:
        float: artillery score
    """
    if not isinstance(model, str):
        raise TypeError(f"model is not str, got {type(model).__name__}")

    weapon_name = 'ARTILLERY'
    weapon = GROUND_WEAPONS[weapon_name].get(model)

    if not weapon:
        logger.warning(f"weapon {weapon_name} {model} unknow")
        return 0.0

    weapon_power = 0.0

    for param_name, coeff_value in WEAPON_PARAM[weapon_name].items():

        if param_name == 'range':
            weapon_power += ( weapon[param_name]['direct'] * 0.7 + weapon[param_name]['indirect'] * 0.3 ) * coeff_value

        elif param_name == 'ammo_type':
            max = min(AMMO_PARAM.values())

            for ammo_type in weapon[param_name]:
                found = AMMO_PARAM.get(ammo_type)
                if found and max < found:
                    max = found

            weapon_power += max * coeff_value

        else:
            weapon_power +=  weapon[param_name] * coeff_value

    return weapon_power

def get_weapon_score(weapon_type: str, weapon_model: str):

    if not weapon_type:
        raise TypeError(f"weapon_type must be a str")
    elif not isinstance(weapon_type, str) or weapon_type not in GROUND_WEAPONS.keys():
        raise ValueError(f"weapon_type must be a str with value included in {GROUND_WEAPONS.keys()}. Got {type(weapon_type).__name__} {weapon_type}")

    if not weapon_model or not isinstance(weapon_model, str):
        raise TypeError(f"weapon_model must be a str")
    
    if weapon_type == 'CANNONS':
        return get_cannon_score(model=weapon_model)
        
    elif weapon_type == 'MISSILES':
        return get_missiles_score(model=weapon_model)

    elif weapon_type == 'ROCKETS':
        return get_rockets_score(model=weapon_model)

    elif weapon_type == 'MORTARS':
        return get_mortars_score(model=weapon_model)

    elif weapon_type == 'ARTILLERY':
        return get_artillery_score(model=weapon_model)

    elif weapon_type == 'MACHINE_GUNS':
        return get_machine_gun_score(model=weapon_model)

    elif weapon_type == 'define':
        return 0
    
    else:
        logger.warning(f"weapon_type unknow, got {weapon_type}")
        return 0


GROUND_WEAPONS = {
    'CANNONS': {
        # combat_power cb = caliber *  
        '2A46M': {
            'model': '2A46M',
            'users': ['Russia', 'India', 'China', 'Egypt', 'Syria', 'Algeria', 'Iraq', 'Libya', 'Vietnam'],
            'start_service': 1974,
            'end_service': 3000,
            'cost': 500, # k$
            'reload': 'Automatic', # Semi_Automatic, Manual non dovrebbe servire in quanto incorporato nel fire_rate
            'caliber': 125, # mm
            'muzzle_speed': 1750, # m/s 
            'fire_rate': 8, # shot per minute
            'range': {'direct': 2120, 'indirect': 10000 }, # m
            'ammo_type': ['HEAT', 'HE', 'APFSDS'],    
            'task': [GROUND_WEAPON_TASK['Anti_Tank'], GROUND_WEAPON_TASK['Infantry_Support']],      
            'perc_efficiency_variability': 0.1,
            'efficiency': {
                "Soft": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.4},
                    "med": {"accuracy": 0.9, "destroy_capacity": 0.45},
                    "small": {"accuracy": 0.8, "destroy_capacity": 0.5},                    
                },
                "Armored": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.95},
                    "med": {"accuracy": 0.75, "destroy_capacity": 1},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1},                    
                },                
                "Hard": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.35},
                    "med": {"accuracy": 0.9, "destroy_capacity": 0.4},
                    "small": {"accuracy": 0.8, "destroy_capacity": 0.45},                    
                },
                "Structure": {
                    "big": {"accuracy": 1, "destroy_capacity": 0.001},
                    "med": {"accuracy": 0.9, "destroy_capacity": 0.01},
                    "small": {"accuracy": 0.8, "destroy_capacity": 0.1},                    
                },
                "Air_Defense": {
                    "big": {"accuracy": 0.85, "destroy_capacity": 0.95},
                    "med": {"accuracy": 0.75, "destroy_capacity": 1},
                    "small": {"accuracy": 0.7, "destroy_capacity": 1},                    
                },
                "Airbase": {
                    "big": {"accuracy": 0.9, "destroy_capacity": sys.float_info.min},
                    "med": {"accuracy": 0.9, "destroy_capacity": sys.float_info.min},
                    "small": {"accuracy": 0.9, "destroy_capacity": 10E-9},                    
                },
                "ship": {
                    "big": {"accuracy": 0.7, "destroy_capacity": 0.42},
                    "med": {"accuracy": 0.5, "destroy_capacity": 0.5},
                    "small": {"accuracy": 0.3, "destroy_capacity": 0.5},                    
                },
                
                
                "Parked Aircraft": {
                    "med": {"accuracy": 0.93, "destroy_capacity": 1},
                    "small": {"accuracy": 0.83, "destroy_capacity": 1},
                }                
            }
            
        }, 
        '2A20': {  # T-62
            'model': '2A20',
            "start_service": 1957,
            "end_service": 3000,
            'reload': 'Automatic', # Semi_Automatic, Manual non dovrebbe servire in quanto incorporato nel fire_rate
            'caliber': 73, # 115?? mm
            'muzzle_speed': 665, # m/s (HEAT) 
            'fire_rate': 8, # shot per minute
            'range': {'direct': 1300, 'indirect': 4500 }, # m
            'ammo_type': ['HEAT', 'HE'],            
        }, 
        'U-5TS "Molot"': {  # T-62
            'model': 'U-5TS "Molot"',
            "start_service": 1953,
            "end_service": 3000,
            'reload': 'Automatic', # Semi_Automatic, Manual non dovrebbe servire in quanto incorporato nel fire_rate
            'caliber': 76, # 115?? mm
            'muzzle_speed': 600, # m/s (HEAT) 
            'fire_rate': 8, # shot per minute
            'range': {'direct': 1300, 'indirect': 4500 },
        },
        '2A42': {
            'model': '2A42',
            "start_service": 1980,
            "end_service": 3000,
            'reload': 'Automatic', # Semi_Automatic, Manual non dovrebbe servire in quanto incorporato nel fire_rate
            'caliber': 30, # mm
            'muzzle_speed': 960, # m/s 
            'fire_rate': 300, # shot per minute
            'range': {'direct': 4000, 'indirect': 0 }, # m
            'ammo_type': ['HE', 'APFSDS'],
        },
        '2A46M-5': {
            'model': '2A46M-5',
            "start_service": 2001,
            "end_service": 3000,
            'reload': 'Automatic', # Semi_Automatic, Manual non dovrebbe servire in quanto incorporato nel fire_rate
            'caliber': 125, # mm    
            'muzzle_speed': 1780, # m/s 
            'fire_rate': 10, # shot per minute
            'range': {'direct': 2200, 'indirect': 10000 }, # m
            'ammo_type': ['HEAT', 'HE', 'APFSDS'],  
        },
        '2A46': {
            'model': '2A46',
            "start_service": 1966,
            "end_service": 3000,
            'reload': 'Automatic', # Semi_Automatic, Manual non dovrebbe servire in quanto incorporato nel fire_rate
            'caliber': 125, # mm
            'muzzle_speed': 1780, # m/s 
            'fire_rate': 8, # shot per minute
            'range': {'direct': 2120, 'indirect': 10000 }, # m
            'ammo_type': ['HEAT', 'HE', 'APFSDS'],  
        },
        '2A61': {
            'model': '2A61',
            "start_service": 1976,
            "end_service": 3000,
            'reload': 'Automatic', # Semi_Automatic, Manual non dovrebbe servire in quanto incorporato nel fire_rate
            'caliber': 125, # mm
            'muzzle_speed': 840, # m/s 
            'fire_rate': 14, # shot per minute
            'range': {'direct': 1700, 'indirect': 15000 }, # m
            'ammo_type': ['HE', 'APFSDS'],  
        },
        '2A64': {
            'model': '2A64',
            "start_service": 1976,
            "end_service": 3000,
            'reload': 'Automatic', # Semi_Automatic, Manual non dovrebbe servire in quanto incorporato nel fire_rate
            'caliber': 152, # mm
            'muzzle_speed': 850, # m/s 
            'fire_rate': 6, # shot per minute
            'range': {'direct': 1800, 'indirect': 24000 }, # m
            'ammo_type': ['HEAT', 'HE', 'APFSDS'],  
        },
        '2A70': {
            'model': '2A70',
            "start_service": 1980,
            "end_service": 3000,
            'reload': 'Automatic', # Semi_Automatic, Manual non dovrebbe servire in quanto incorporato nel fire_rate
            'caliber': 100, # mm
            'muzzle_speed': 250, # m/s 
            'fire_rate': 4, # shot per minute
            'range': {'direct': 1700, 'indirect': 4000 }, # m
            'ammo_type': ['HE'],  
        },
        'APV-23': {
            'model': 'APV-23',
            "start_service": 1960,
            "end_service": 3000,
            'reload': 'Automatic', # Semi_Automatic, Manual non dovrebbe servire in quanto incorporato nel fire_rate
            'caliber': 23, # mm
            'muzzle_speed': 970, # m/s 
            'fire_rate': 400, # shot per minute
            'range': {'direct': 2000, 'indirect': 0 }, # m
            'ammo_type': ['HE', 'APFSDS'],
        },
        'M68A1': {
            'model': 'M68A1',
            "start_service": 1959,
            "end_service": 3000,
            'reload': 'Automatic', # Semi_Automatic, Manual non dovrebbe servire in quanto incorporato nel fire_rate
            'caliber': 105, # mm
            'muzzle_speed': 1470, # m/s 
            'fire_rate': 10, # shot per minute
            'range': {'direct': 2100, 'indirect': 8000 }, # m
            'ammo_type': ['HEAT', 'HE', 'APFSDS'],            
        },
        'M242 Bushmaster': {
            'model': 'M242 Bushmaster',
            "start_service": 1981,
            "end_service": 3000,
            'reload': 'Automatic', # Semi_Automatic, Manual non dovrebbe servire in quanto incorporato nel fire_rate
            'caliber': 25, # mm
            'muzzle_speed': 1100, # m/s 
            'fire_rate': 200, # shot per minute
            'range': {'direct': 3000, 'indirect': 0 }, # m
            'ammo_type': ['HE', 'APFSDS'],

        },
        'M230 Chain Gun': {
            'model': 'M230 Chain Gun',  
            "start_service": 1987,
            "end_service": 3000,          
            'reload': 'Automatic', # Semi_Automatic, Manual non dovrebbe servire in quanto incorporato nel fire_rate
            'caliber': 30, # mm
            'muzzle_speed': 805, # m/s 
            'fire_rate': 625, # shot per minute
            'range': {'direct': 1500, 'indirect': 0 }, # m
            'ammo_type': ['HE', 'APFSDS'],  
        },
        'M256': {
            'model': 'M256',
            "start_service": 1985,
            "end_service": 3000,
            'reload': 'Automatic', # Semi_Automatic, Manual non dovrebbe servire in quanto incorporato nel fire_rate
            'caliber': 120, # mm
            'muzzle_speed': 1750, # m/s 
            'fire_rate': 6, # shot per minute
            'range': {'direct': 2100, 'indirect': 8000 }, # m
            'ammo_type': ['HEAT', 'HE', 'APFSDS'],  
        },
        'M255': {
            'model': 'M255',
            "start_service": 1985,
            "end_service": 3000,
            'reload': 'Automatic', # Semi_Automatic, Manual non dovrebbe servire in quanto incorporato nel fire_rate
            'caliber': 120, # mm
            'muzzle_speed': 1030, # m/s 
            'fire_rate': 6, # shot per minute
            'range': {'direct': 2100, 'indirect': 8000 }, # m
            'ammo_type': ['HEAT', 'HE'],    
        },
        'D30': {
            'model': 'D30',
            "start_service": 1963, 
            "end_service": 3000,
            'reload': 'Automatic', # Semi_Automatic, Manual non dovrebbe servire in quanto incorporato nel fire_rate
            'caliber': 122, # mm
            'muzzle_speed': 850, # m/s 
            'fire_rate': 15, # shot per minute
            'range': {'direct': 12000, 'indirect': 12000 }, # m
            'ammo_type': ['HE', 'AP'],    
        },
        'D-10T': { # T-55
            'model': 'D-10T',
            "start_service": 1946,
            "end_service": 3000,
            'reload': 'Automatic', # Semi_Automatic, Manual non dovrebbe servire in quanto incorporato nel fire_rate
            'caliber': 100, # mm
            'muzzle_speed': 895, # m/s
            'fire_rate': 5, # shot per minute
            'range': {'direct': 2000, 'indirect': 8000 }, # m
            'ammo_type': ['HEAT', 'HE', 'APFSDS'],
        },
        # --- MBT Cannons ---
        '2A28 Grom': { # BMP-1 (MBT variant)
            'model': '2A28 Grom',
            "start_service": 1966,
            "end_service": 3000,
            'reload': 'Automatic',
            'caliber': 73, # mm - low-pressure smoothbore
            'muzzle_speed': 665, # m/s (PG-15V HEAT round)
            'fire_rate': 8, # shot per minute
            'range': {'direct': 1300, 'indirect': 4400 }, # m
            'ammo_type': ['HEAT', 'HE'],
        },
        'D-10T2S-100mm': { # T-55A - stabilized variant of D-10T
            'model': 'D-10T2S-100mm',
            "start_service": 1963,
            "end_service": 3000,
            'reload': 'Automatic',
            'caliber': 100, # mm
            'muzzle_speed': 895, # m/s (BR-412D AP)
            'fire_rate': 7, # shot per minute
            'range': {'direct': 2000, 'indirect': 16000 }, # m
            'ammo_type': ['HEAT', 'HE', 'APFSDS', 'AP'],
        },
        'L11A5-120mm': { # Chieftain
            'model': 'L11A5-120mm',
            "start_service": 1966,
            "end_service": 3000,
            'reload': 'Automatic',
            'caliber': 120, # mm - rifled
            'muzzle_speed': 1534, # m/s (L23A1 APFSDS)
            'fire_rate': 6, # shot per minute
            'range': {'direct': 2500, 'indirect': 9000 }, # m
            'ammo_type': ['HEAT', 'HE', 'APFSDS'],
        },
        'L7A3-105mm': { # Leopard 1
            'model': 'L7A3-105mm',
            "start_service": 1965,
            "end_service": 3000,
            'reload': 'Automatic',
            'caliber': 105, # mm - rifled (Rheinmetall variant of Royal Ordnance L7)
            'muzzle_speed': 1501, # m/s (DM63 APFSDS)
            'fire_rate': 10, # shot per minute
            'range': {'direct': 2500, 'indirect': 10000 }, # m
            'ammo_type': ['HEAT', 'HE', 'APFSDS', 'AP'],
        },
        'M68-105mm': { # M60 Patton
            'model': 'M68-105mm',
            "start_service": 1959,
            "end_service": 3000,
            'reload': 'Automatic',
            'caliber': 105, # mm - rifled (US variant of L7)
            'muzzle_speed': 1470, # m/s (M735 APFSDS)
            'fire_rate': 10, # shot per minute
            'range': {'direct': 2500, 'indirect': 10000 }, # m
            'ammo_type': ['HEAT', 'HE', 'APFSDS', 'AP'],
        },
        'Rheinmetall-120mm-L44': { # Leopard 2A4
            'model': 'Rheinmetall-120mm-L44',
            "start_service": 1979,
            "end_service": 3000,
            'reload': 'Automatic',
            'caliber': 120, # mm - smoothbore (Rh-120 L/44)
            'muzzle_speed': 1750, # m/s (DM53 APFSDS)
            'fire_rate': 6, # shot per minute
            'range': {'direct': 3000, 'indirect': 8000 }, # m
            'ammo_type': ['HEAT', 'HE', 'APFSDS'],
        },
        'Rheinmetall-120mm-L55': { # Leopard 2A6
            'model': 'Rheinmetall-120mm-L55',
            "start_service": 2001,
            "end_service": 3000,
            'reload': 'Automatic',
            'caliber': 120, # mm - smoothbore (Rh-120 L/55, longer barrel)
            'muzzle_speed': 1800, # m/s (DM63 APFSDS)
            'fire_rate': 6, # shot per minute
            'range': {'direct': 3500, 'indirect': 8000 }, # m
            'ammo_type': ['HEAT', 'HE', 'APFSDS'],
        },
        'M256-120mm': { # M1A1/M1A2 Abrams
            'model': 'M256-120mm',
            "start_service": 1985,
            "end_service": 3000,
            'reload': 'Automatic',
            'caliber': 120, # mm - smoothbore (US variant of Rh-120 L/44)
            'muzzle_speed': 1750, # m/s (M829A3 APFSDS)
            'fire_rate': 6, # shot per minute
            'range': {'direct': 2100, 'indirect': 8000 }, # m
            'ammo_type': ['HEAT', 'HE', 'APFSDS'],
        },
        'CN120-26-120mm': { # Leclerc
            'model': 'CN120-26-120mm',
            "start_service": 1992,
            "end_service": 3000,
            'reload': 'Automatic', # autoloader (bustle-mounted, 22 rounds)
            'caliber': 120, # mm - smoothbore (GIAT CN120-26, L/52)
            'muzzle_speed': 1790, # m/s (OFL 120 F2 APFSDS)
            'fire_rate': 12, # shot per minute (autoloader)
            'range': {'direct': 3000, 'indirect': 8000 }, # m
            'ammo_type': ['HEAT', 'HE', 'APFSDS'],
        },
        'L30A1-120mm': { # Challenger 2
            'model': 'L30A1-120mm',
            "start_service": 1994,
            "end_service": 3000,
            'reload': 'Automatic',
            'caliber': 120, # mm - rifled (CHARM gun)
            'muzzle_speed': 1534, # m/s (L27A1 CHARM 3 APFSDS)
            'fire_rate': 6, # shot per minute
            'range': {'direct': 3000, 'indirect': 8000 }, # m
            'ammo_type': ['HEAT', 'HE', 'APFSDS'],
        },
        'MG251-120mm': { # Merkava Mk3/Mk4
            'model': 'MG251-120mm',
            "start_service": 1989,
            "end_service": 3000,
            'reload': 'Automatic', # semi-automatic assisted loading
            'caliber': 120, # mm - smoothbore (IMI 120mm)
            'muzzle_speed': 1750, # m/s (IMI M338 APFSDS)
            'fire_rate': 8, # shot per minute
            'range': {'direct': 2200, 'indirect': 8000 }, # m
            'ammo_type': ['HEAT', 'HE', 'APFSDS'],
        },
        'Type-59-100mm': { # Type 59
            'model': 'Type-59-100mm',
            "start_service": 1959,
            "end_service": 3000,
            'reload': 'Automatic',
            'caliber': 100, # mm - rifled (Chinese copy of D-10T)
            'muzzle_speed': 895, # m/s (AP round)
            'fire_rate': 4, # shot per minute
            'range': {'direct': 1800, 'indirect': 8000 }, # m
            'ammo_type': ['HEAT', 'HE', 'AP', 'APFSDS'],
        },
        '2A46M-125mm': { # T-72B3, T-80U (same as 2A46M)
            'model': '2A46M-125mm',
            "start_service": 1974,
            "end_service": 3000,
            'reload': 'Automatic', # carousel autoloader
            'caliber': 125, # mm - smoothbore
            'muzzle_speed': 1750, # m/s (3BM42 Mango APFSDS)
            'fire_rate': 8, # shot per minute
            'range': {'direct': 2120, 'indirect': 10000 }, # m
            'ammo_type': ['HEAT', 'HE', 'APFSDS'],
        },
        '2A46M5-125mm': { # T-90A (same as 2A46M-5)
            'model': '2A46M5-125mm',
            "start_service": 2001,
            "end_service": 3000,
            'reload': 'Automatic', # carousel autoloader
            'caliber': 125, # mm - smoothbore (improved barrel)
            'muzzle_speed': 1780, # m/s (3BM59/3BM60 Svinets APFSDS)
            'fire_rate': 10, # shot per minute
            'range': {'direct': 2200, 'indirect': 10000 }, # m
            'ammo_type': ['HEAT', 'HE', 'APFSDS'],
        },
        'ZPT-98-125mm': { # Type 99
            'model': 'ZPT-98-125mm',
            "start_service": 1998,
            "end_service": 3000,
            'reload': 'Automatic', # carousel autoloader
            'caliber': 125, # mm - smoothbore (Chinese, derived from 2A46 family, L/50)
            'muzzle_speed': 1780, # m/s (DTW-125 APFSDS)
            'fire_rate': 8, # shot per minute
            'range': {'direct': 2200, 'indirect': 10000 }, # m
            'ammo_type': ['HEAT', 'HE', 'APFSDS'],
        },
        # --- IFV/APC Autocannons ---
        'MK-20-Rh-202-20mm': { # Marder IFV
            'model': 'MK-20-Rh-202-20mm',
            "start_service": 1968,
            "end_service": 3000,
            'reload': 'Automatic',
            'caliber': 20, # mm (20x139mm)
            'muzzle_speed': 1100, # m/s (APDS)
            'fire_rate': 880, # shot per minute
            'range': {'direct': 2000, 'indirect': 0 }, # m
            'ammo_type': ['HE', 'AP'],
        },
        '2A42-30mm': { # BMP-2 (same as 2A42)
            'model': '2A42-30mm',
            "start_service": 1980,
            "end_service": 3000,
            'reload': 'Automatic',
            'caliber': 30, # mm (30x165mm)
            'muzzle_speed': 960, # m/s
            'fire_rate': 300, # shot per minute
            'range': {'direct': 4000, 'indirect': 0 }, # m
            'ammo_type': ['HE', 'APFSDS'],
        },
        '2A28-Grom-73mm': { # BMP-1 IFV
            'model': '2A28-Grom-73mm',
            "start_service": 1966,
            "end_service": 3000,
            'reload': 'Automatic',
            'caliber': 73, # mm - low-pressure smoothbore
            'muzzle_speed': 665, # m/s (PG-15V HEAT round)
            'fire_rate': 8, # shot per minute
            'range': {'direct': 1300, 'indirect': 4400 }, # m
            'ammo_type': ['HEAT', 'HE'],
        },
        'M242-Bushmaster-25mm': { # M2 Bradley, LAV-25 (same as M242 Bushmaster)
            'model': 'M242-Bushmaster-25mm',
            "start_service": 1981,
            "end_service": 3000,
            'reload': 'Automatic',
            'caliber': 25, # mm (25x137mm NATO)
            'muzzle_speed': 1100, # m/s (M919 APFSDS-T)
            'fire_rate': 200, # shot per minute
            'range': {'direct': 3000, 'indirect': 0 }, # m
            'ammo_type': ['HE', 'APFSDS'],
        },
        '2A70-100mm': { # BMP-3 (same as 2A70)
            'model': '2A70-100mm',
            "start_service": 1980,
            "end_service": 3000,
            'reload': 'Automatic',
            'caliber': 100, # mm - low-pressure rifled
            'muzzle_speed': 250, # m/s
            'fire_rate': 4, # shot per minute
            'range': {'direct': 1700, 'indirect': 4000 }, # m
            'ammo_type': ['HE'],
        },
        '2A72-30mm': { # BMP-3, BTR-82A
            'model': '2A72-30mm',
            "start_service": 1986,
            "end_service": 3000,
            'reload': 'Automatic',
            'caliber': 30, # mm (30x165mm, single-barrel, simpler than 2A42)
            'muzzle_speed': 960, # m/s (AP-T)
            'fire_rate': 330, # shot per minute
            'range': {'direct': 4000, 'indirect': 0 }, # m
            'ammo_type': ['HE', 'AP'],
        },
        'ZPT-99-30mm': { # ZBD-04 (Chinese 30mm autocannon)
            'model': 'ZPT-99-30mm',
            "start_service": 1999,
            "end_service": 3000,
            'reload': 'Automatic',
            'caliber': 30, # mm (30mm, dual-feed)
            'muzzle_speed': 960, # m/s
            'fire_rate': 350, # shot per minute
            'range': {'direct': 3500, 'indirect': 0 }, # m
            'ammo_type': ['HE', 'AP'],
        },
        'L21A1-RARDEN-30mm': { # Warrior IFV
            'model': 'L21A1-RARDEN-30mm',
            "start_service": 1974,
            "end_service": 3000,
            'reload': 'Automatic', # semi-automatic (3-round clips)
            'caliber': 30, # mm (30x170mm)
            'muzzle_speed': 1175, # m/s (L14A3 APDS)
            'fire_rate': 90, # shot per minute
            'range': {'direct': 1500, 'indirect': 0 }, # m
            'ammo_type': ['HE', 'AP', 'APFSDS'],
        },
        'M242-25mm': { # LAV-AD (same as M242 Bushmaster)
            'model': 'M242-25mm',
            "start_service": 1981,
            "end_service": 3000,
            'reload': 'Automatic',
            'caliber': 25, # mm (25x137mm NATO)
            'muzzle_speed': 1100, # m/s (M919 APFSDS-T)
            'fire_rate': 200, # shot per minute
            'range': {'direct': 3000, 'indirect': 0 }, # m
            'ammo_type': ['HE', 'APFSDS'],
        },
        # --- AA/SPAAG Cannons ---
        'S-68-57mm': { # ZSU-57-2 (twin 57mm)
            'model': 'S-68-57mm',
            "start_service": 1950,
            "end_service": 3000,
            'reload': 'Automatic',
            'caliber': 57, # mm (57x348mmSR, twin mount)
            'muzzle_speed': 1000, # m/s
            'fire_rate': 240, # shot per minute (combined twin barrels, 120 each)
            'range': {'direct': 4000, 'indirect': 12000 }, # m
            'ammo_type': ['HE', 'AP'],
        },
        'AZP-23-23mm': { # ZSU-23-4 Shilka (quad 23mm)
            'model': 'AZP-23-23mm',
            "start_service": 1960,
            "end_service": 3000,
            'reload': 'Automatic',
            'caliber': 23, # mm (23x152mmB, quad mount)
            'muzzle_speed': 970, # m/s
            'fire_rate': 3400, # shot per minute (combined quad barrels, ~850 each)
            'range': {'direct': 2500, 'indirect': 0 }, # m
            'ammo_type': ['HE', 'AP'],
        },
        'M61-Vulcan-20mm': { # M163 VADS
            'model': 'M61-Vulcan-20mm',
            "start_service": 1959,
            "end_service": 3000,
            'reload': 'Automatic',
            'caliber': 20, # mm (20x102mm NATO, 6-barrel rotary)
            'muzzle_speed': 1030, # m/s (M56 HEI)
            'fire_rate': 3000, # shot per minute (M163 VADS configuration)
            'range': {'direct': 1200, 'indirect': 0 }, # m
            'ammo_type': ['HE', 'AP'],
        },
        'Oerlikon-KDA-35mm': { # Gepard SPAAG (twin 35mm)
            'model': 'Oerlikon-KDA-35mm',
            "start_service": 1959,
            "end_service": 3000,
            'reload': 'Automatic',
            'caliber': 35, # mm (35x228mm, twin mount)
            'muzzle_speed': 1175, # m/s (APDS-T)
            'fire_rate': 1100, # shot per minute (combined twin barrels, 550 each)
            'range': {'direct': 4000, 'indirect': 0 }, # m
            'ammo_type': ['HE', 'AP'],
        },
        '2A38M-30mm': { # Tunguska 2K22 (dual 30mm)
            'model': '2A38M-30mm',
            "start_service": 1982,
            "end_service": 3000,
            'reload': 'Automatic',
            'caliber': 30, # mm (30x165mm, twin barrels)
            'muzzle_speed': 960, # m/s
            'fire_rate': 5000, # shot per minute (combined twin barrels, 2500 each)
            'range': {'direct': 4000, 'indirect': 0 }, # m
            'ammo_type': ['HE', 'AP'],
        },
    },
    'MISSILES': {
        '9K119M': { # AT-11 Sniper
            'model': '9K119M',
            "start_service": 1984,
            "end_service": 3000,
            'guide': 'Laser', # 
            'caliber': 125, # mm
            'warhead': 4.5, # kg
            'speed': 390, # m/s             
            'range': {'direct': 4500, 'indirect': 0 }, # m
            'ammo_type': ['2HEAT'],            
        }, 
        '99K120': { # AT-11 Sniper
            'model': '9K119M',
            "start_service": 1974,
            "end_service": 3000,
            'guide': 'Laser', # 
            'caliber': 125, # mm
            'warhead': 4.5, # kg
            'speed': 300, # m/s             
            'range': {'direct': 4000, 'indirect': 0 }, # m
            'ammo_type': ['HEAT'],            
        }, 
        '9M14 Malyutka': { # AT-3 Sagger
            'model': '9M14 Malyutka',
            "start_service": 1965,
            "end_service": None,
            'guide': 'SACLOS', # SACLOS: Semi-Automatic Command to Line Of Sight
            'caliber': 125, # mm
            'warhead': 3, # kg
            'speed': 115, # m/s             
            'range': {'direct': 3000, 'indirect': 0 }, # m
            'ammo_type': ['HEAT'],            
        }, 
        '9M113 Konkurs': { # AT-5 Spandrel
            'model': '9M113 Konkurs',
            "start_service": 1974,
            "end_service": 3000,
            'guide': 'SACLOS', # SACLOS: Semi-Automatic Command to Line Of Sight
            'caliber': 135, # mm
            'warhead': 4.6, # kg
            'speed': 208, # m/s             
            'range': {'direct': 4000, 'indirect': 0 }, # m
            'ammo_type': ['HEAT'],            
        },
        '9M35 Kornet': { # AT-14 Spriggan
            'model': '9M35 Kornet',
            "start_service": 1998,
            "end_service": 3000,
            'guide': 'Laser', # SACLOS: Semi-Automatic Command to Line Of Sight
            'caliber': 152, # mm
            'warhead': 7, # kg
            'speed': 300, # m/s             
            'range': {'direct': 5500, 'indirect': 0 }, # m
            'ammo_type': ['HEAT', '2HEAT'],            
        },
        '9M37M': { # AT-15 Springer
            'model': '9M37M',
            "start_service": 2010,
            "end_service": 3000,        
            'guide': 'Fire_and_Forget', # SACLOS: Semi-Automatic Command to Line Of Sight
            'caliber': 152, # mm
            'warhead': 7, # kg
            'speed': 400, # m/s             
            'range': {'direct': 7000, 'indirect': 0 }, # m
            'ammo_type': ['HEAT', '2HEAT'],
        },
        '9M331': { # AT-15 Springer
            'model': '9M331',
            "start_service": 2010,
            "end_service": 3000,        
            'guide': 'Fire_and_Forget', # SACLOS: Semi-Automatic Command to Line Of Sight
            'caliber': 152, # mm
            'warhead': 7, # kg
            'speed': 400, # m/s             
            'range': {'direct': 7000, 'indirect': 0 }, # m
            'ammo_type': ['HEAT', '2HEAT'],
        }, 
        'TOW-2': { # BGM-71 TOW
            'model': 'TOW-2',
            "start_service": 1970,
            "end_service": 3000,
            'guide': 'SACLOS', # SACLOS: Semi-Automatic Command to Line Of Sight
            'caliber': 152, # mm
            'warhead': 4.5, # kg
            'speed': 278, # m/s
            'range': {'direct': 3750, 'indirect': 0 }, # m
            'ammo_type': ['HEAT'],
        },
        # --- ATGMs referenced with dash naming ---
        '9M119-Refleks': { # AT-11 Sniper (original)
            'model': '9M119-Refleks',
            "start_service": 1985,
            "end_service": 3000,
            'guide': 'Laser',
            'caliber': 125, # mm
            'warhead': 4.5, # kg
            'speed': 370, # m/s
            'range': {'direct': 4000, 'indirect': 0 }, # m
            'ammo_type': ['HEAT'],
        },
        '9M119M-Refleks-M': { # AT-11 Sniper (improved, tandem warhead)
            'model': '9M119M-Refleks-M',
            "start_service": 1992,
            "end_service": 3000,
            'guide': 'Laser',
            'caliber': 125, # mm
            'warhead': 4.5, # kg
            'speed': 390, # m/s
            'range': {'direct': 5000, 'indirect': 0 }, # m
            'ammo_type': ['2HEAT'],
        },
        '9M113-Konkurs': { # AT-5 Spandrel (dash naming variant)
            'model': '9M113-Konkurs',
            "start_service": 1974,
            "end_service": 3000,
            'guide': 'SACLOS',
            'caliber': 135, # mm
            'warhead': 4.6, # kg
            'speed': 208, # m/s
            'range': {'direct': 4000, 'indirect': 0 }, # m
            'ammo_type': ['HEAT'],
        },
        '9M14-Malyutka': { # AT-3 Sagger (dash naming variant)
            'model': '9M14-Malyutka',
            "start_service": 1965,
            "end_service": 3000,
            'guide': 'SACLOS',
            'caliber': 125, # mm
            'warhead': 3, # kg
            'speed': 115, # m/s
            'range': {'direct': 3000, 'indirect': 0 }, # m
            'ammo_type': ['HEAT'],
        },
        'BGM-71-TOW': { # BGM-71 TOW (alternate key)
            'model': 'BGM-71-TOW',
            "start_service": 1970,
            "end_service": 3000,
            'guide': 'SACLOS',
            'caliber': 152, # mm
            'warhead': 3.9, # kg
            'speed': 278, # m/s
            'range': {'direct': 3750, 'indirect': 0 }, # m
            'ammo_type': ['HEAT'],
        },
        'MILAN': { # MILAN 2 ATGM (French/German)
            'model': 'MILAN',
            "start_service": 1972,
            "end_service": 3000,
            'guide': 'SACLOS',
            'caliber': 115, # mm
            'warhead': 2.4, # kg
            'speed': 200, # m/s
            'range': {'direct': 2000, 'indirect': 0 }, # m
            'ammo_type': ['HEAT'],
        },
        'HJ-73C': { # Red Arrow 73C (Chinese ATGM based on AT-3)
            'model': 'HJ-73C',
            "start_service": 1985,
            "end_service": 3000,
            'guide': 'SACLOS',
            'caliber': 120, # mm
            'warhead': 2.5, # kg
            'speed': 120, # m/s
            'range': {'direct': 3000, 'indirect': 0 }, # m
            'ammo_type': ['HEAT'],
        },
        # --- Surface-to-Air Missiles ---
        '9M311-SAM': { # SA-19 Grison (Tunguska SAM)
            'model': '9M311-SAM',
            "start_service": 1982,
            "end_service": 3000,
            'guide': 'Radio_Command',
            'caliber': 76, # mm
            'warhead': 9, # kg
            'speed': 900, # m/s
            'range': {'direct': 8000, 'indirect': 0 }, # m
            'ammo_type': ['HE', 'FRAG'],
        },
        '9M31-SAM': { # SA-9 Gaskin (Strela-1)
            'model': '9M31-SAM',
            "start_service": 1968,
            "end_service": 3000,
            'guide': 'IR',
            'caliber': 120, # mm
            'warhead': 3, # kg
            'speed': 430, # m/s
            'range': {'direct': 4200, 'indirect': 0 }, # m
            'ammo_type': ['HE', 'FRAG'],
        },
        'MIM-72-SAM': { # MIM-72 Chaparral
            'model': 'MIM-72-SAM',
            "start_service": 1969,
            "end_service": 3000,
            'guide': 'IR',
            'caliber': 127, # mm
            'warhead': 11, # kg
            'speed': 760, # m/s
            'range': {'direct': 9000, 'indirect': 0 }, # m
            'ammo_type': ['HE', 'FRAG'],
        },
        '9M33-SAM': { # SA-8 Gecko (Osa)
            'model': '9M33-SAM',
            "start_service": 1971,
            "end_service": 3000,
            'guide': 'Radio_Command',
            'caliber': 210, # mm
            'warhead': 19, # kg
            'speed': 500, # m/s
            'range': {'direct': 10000, 'indirect': 0 }, # m
            'ammo_type': ['HE', 'FRAG'],
        },
        '9M37-SAM': { # SA-13 Gopher (Strela-10)
            'model': '9M37-SAM',
            "start_service": 1976,
            "end_service": 3000,
            'guide': 'IR',
            'caliber': 120, # mm
            'warhead': 3, # kg
            'speed': 517, # m/s
            'range': {'direct': 5000, 'indirect': 0 }, # m
            'ammo_type': ['HE', 'FRAG'],
        },
        'Roland-SAM': { # Roland (French/German SAM)
            'model': 'Roland-SAM',
            "start_service": 1977,
            "end_service": 3000,
            'guide': 'SACLOS',
            'caliber': 160, # mm
            'warhead': 6.5, # kg
            'speed': 500, # m/s
            'range': {'direct': 6300, 'indirect': 0 }, # m
            'ammo_type': ['HE', 'FRAG'],
        },
        '9M331-SAM': { # SA-15 Gauntlet (Tor)
            'model': '9M331-SAM',
            "start_service": 1986,
            "end_service": 3000,
            'guide': 'Radio_Command',
            'caliber': 235, # mm
            'warhead': 15, # kg
            'speed': 850, # m/s
            'range': {'direct': 12000, 'indirect': 0 }, # m
            'ammo_type': ['HE', 'FRAG'],
        },
        'FIM-92-Stinger': { # FIM-92 Stinger MANPADS
            'model': 'FIM-92-Stinger',
            "start_service": 1981,
            "end_service": 3000,
            'guide': 'IR',
            'caliber': 70, # mm
            'warhead': 3, # kg
            'speed': 750, # m/s
            'range': {'direct': 4800, 'indirect': 0 }, # m
            'ammo_type': ['HE', 'FRAG'],
        },
        '3M9-SAM': { # SA-6 Gainful (Kub)
            'model': '3M9-SAM',
            "start_service": 1967,
            "end_service": 3000,
            'guide': 'SARH',
            'caliber': 330, # mm
            'warhead': 59, # kg
            'speed': 600, # m/s
            'range': {'direct': 24000, 'indirect': 0 }, # m
            'ammo_type': ['HE', 'FRAG'],
        },
        '9M38-SAM': { # SA-11 Gadfly (Buk)
            'model': '9M38-SAM',
            "start_service": 1979,
            "end_service": 3000,
            'guide': 'SARH',
            'caliber': 400, # mm
            'warhead': 70, # kg
            'speed': 850, # m/s
            'range': {'direct': 35000, 'indirect': 0 }, # m
            'ammo_type': ['HE', 'FRAG'],
        },
        '5V55R-SAM': { # SA-10 Grumble (S-300PS)
            'model': '5V55R-SAM',
            "start_service": 1982,
            "end_service": 3000,
            'guide': 'SARH',
            'caliber': 508, # mm
            'warhead': 133, # kg
            'speed': 1700, # m/s
            'range': {'direct': 75000, 'indirect': 0 }, # m
            'ammo_type': ['HE', 'FRAG'],
        },
    },
        
    'ROCKETS': {},

    'MORTARS': {
        'M933-60mm': { # Merkava internal mortar (Soltam 60mm)
            'model': 'M933-60mm',
            "start_service": 1989,
            "end_service": 3000,
            'caliber': 60, # mm
            'fire_rate': 18, # shot per minute
            'range': {'direct': 0, 'indirect': 2600 }, # m - mortar, indirect fire only
            'ammo_type': ['HE'],
        },
    },

    'ARTILLERY': {
        # --- Tube Artillery ---
        '2A33-152mm': { # 2S3 Akatsiya
            'model': '2A33-152mm',
            "start_service": 1971,
            "end_service": 3000,
            'caliber': 152, # mm
            'muzzle_speed': 655, # m/s
            'fire_rate': 4, # shot per minute
            'range': {'direct': 0, 'indirect': 18500 }, # m
            'ammo_type': ['HE'],
        },
        '2A31-122mm': { # 2S1 Gvozdika
            'model': '2A31-122mm',
            "start_service": 1971,
            "end_service": 3000,
            'caliber': 122, # mm
            'muzzle_speed': 690, # m/s
            'fire_rate': 5, # shot per minute
            'range': {'direct': 0, 'indirect': 15300 }, # m
            'ammo_type': ['HE'],
        },
        '2A51-120mm': { # 2S9 Nona (gun-mortar)
            'model': '2A51-120mm',
            "start_service": 1981,
            "end_service": 3000,
            'caliber': 120, # mm
            'muzzle_speed': 367, # m/s
            'fire_rate': 8, # shot per minute
            'range': {'direct': 1000, 'indirect': 8850 }, # m
            'ammo_type': ['HE', 'HEAT'],
        },
        '2A64-152mm': { # 2S19 Msta
            'model': '2A64-152mm',
            "start_service": 1989,
            "end_service": 3000,
            'caliber': 152, # mm
            'muzzle_speed': 810, # m/s
            'fire_rate': 8, # shot per minute
            'range': {'direct': 0, 'indirect': 24700 }, # m
            'ammo_type': ['HE'],
        },
        'Dana-152mm': { # Dana SpGH (Czech)
            'model': 'Dana-152mm',
            "start_service": 1977,
            "end_service": 3000,
            'caliber': 152, # mm
            'muzzle_speed': 690, # m/s
            'fire_rate': 4, # shot per minute
            'range': {'direct': 0, 'indirect': 18700 }, # m
            'ammo_type': ['HE'],
        },
        'M284-155mm': { # M109 Paladin
            'model': 'M284-155mm',
            "start_service": 1992,
            "end_service": 3000,
            'caliber': 155, # mm (M284 cannon on M109A6 Paladin)
            'muzzle_speed': 827, # m/s
            'fire_rate': 4, # shot per minute
            'range': {'direct': 0, 'indirect': 24000 }, # m
            'ammo_type': ['HE'],
        },
        'PL-45-155mm': { # PLZ-05 (Chinese)
            'model': 'PL-45-155mm',
            "start_service": 2005,
            "end_service": 3000,
            'caliber': 155, # mm (52 calibre barrel)
            'muzzle_speed': 897, # m/s
            'fire_rate': 8, # shot per minute
            'range': {'direct': 0, 'indirect': 39000 }, # m
            'ammo_type': ['HE'],
        },
        'Firtina-155mm': { # T-155 Firtina (Turkish)
            'model': 'Firtina-155mm',
            "start_service": 2002,
            "end_service": 3000,
            'caliber': 155, # mm (52 calibre barrel, based on K9 Thunder)
            'muzzle_speed': 897, # m/s
            'fire_rate': 6, # shot per minute
            'range': {'direct': 0, 'indirect': 40000 }, # m
            'ammo_type': ['HE'],
        },
        # --- MLRS / Rocket Artillery ---
        '122mm-Grad-Rocket': { # BM-21 Grad
            'model': '122mm-Grad-Rocket',
            "start_service": 1963,
            "end_service": 3000,
            'caliber': 122, # mm
            'muzzle_speed': 0, # N/A - rocket propelled
            'fire_rate': 2, # ripple fire, full salvo (40 rockets) in ~20 seconds
            'range': {'direct': 0, 'indirect': 20380 }, # m
            'ammo_type': ['HE'],
        },
        '220mm-Uragan-Rocket': { # BM-27 Uragan
            'model': '220mm-Uragan-Rocket',
            "start_service": 1975,
            "end_service": 3000,
            'caliber': 220, # mm
            'muzzle_speed': 0, # N/A - rocket propelled
            'fire_rate': 1, # full salvo (16 rockets) in ~20 seconds
            'range': {'direct': 0, 'indirect': 35800 }, # m
            'ammo_type': ['HE'],
        },
        '300mm-Smerch-Rocket': { # BM-30 Smerch
            'model': '300mm-Smerch-Rocket',
            "start_service": 1987,
            "end_service": 3000,
            'caliber': 300, # mm
            'muzzle_speed': 0, # N/A - rocket propelled
            'fire_rate': 1, # full salvo (12 rockets) in ~38 seconds
            'range': {'direct': 0, 'indirect': 70000 }, # m
            'ammo_type': ['HE'],
        },
        '227mm-MLRS-Rocket': { # M270 MLRS
            'model': '227mm-MLRS-Rocket',
            "start_service": 1983,
            "end_service": 3000,
            'caliber': 227, # mm
            'muzzle_speed': 0, # N/A - rocket propelled
            'fire_rate': 1, # full salvo (12 rockets) in ~60 seconds
            'range': {'direct': 0, 'indirect': 32000 }, # m
            'ammo_type': ['HE'],
        },
    },

    'MACHINE_GUNS': {
        'PKT-7.62': {
            'model': 'PKT-7.62',
            "start_service": 1992,
            "end_service": 3000,            
            'caliber': 7.62, # mm
            'fire_rate': 700, # shot per minute
            'range': {'direct': 1200, 'indirect': 0 }, # m
        }, 
        'Kord-12.7': {
            'model': 'Kord-12.7',
            "start_service": 1992,
            "end_service": 3000,            
            'caliber': 12.7, # mm
            'fire_rate': 750, # shot per minute
            'range': {'direct': 2000, 'indirect': 0 }, # m
        }, 
        'NSVT-12.7': {
            'model': 'Kord-12.7',
            "start_service": 1992,
            "end_service": 3000,            
            'caliber': 12.7, # mm
            'fire_rate': 800, # shot per minute
            'range': {'direct': 2000, 'indirect': 0 }, # m
        }, 
        'M2HB-12.7': {
            'model': 'M2HB-12.7',
            "start_service": 1933,
            "end_service": 3000,            
            'caliber': 12.7, # mm
            'fire_rate': 600, # shot per minute
            'range': {'direct': 1800, 'indirect': 0 }, # m
        },
        'M240-7.62': {
            'model': 'M240-7.62',
            "start_service": 1977,
            "end_service": 3000,            
            'caliber': 7.62, # mm
            'fire_rate': 650, # shot per minute
            'range': {'direct': 1100, 'indirect': 0 }, # m
        },
        'KPVT-14.5': {
            'model': 'KPVT-14.5',
            "start_service": 1949,
            "end_service": 3000,            
            'caliber': 14.5, # mm
            'fire_rate': 600, # shot per minute
            'range': {'direct': 2000, 'indirect': 0 }, # m
        },
        'DShK-12.7': { # T-55
            'model': 'DShK-12.7',
            "start_service": 1938,
            "end_service": 3000,
            'caliber': 12.7, # mm
            'fire_rate': 600, # shot per minute
            'range': {'direct': 2000, 'indirect': 0 }, # m
        },
        # --- British MGs ---
        'L8A1-7.62': { # Chieftain coaxial
            'model': 'L8A1-7.62',
            "start_service": 1966,
            "end_service": 3000,
            'caliber': 7.62, # mm - coaxial variant of L7A2 GPMG
            'fire_rate': 750, # shot per minute
            'range': {'direct': 1200, 'indirect': 0 }, # m
        },
        'L37A1-7.62': { # Chieftain commander's MG
            'model': 'L37A1-7.62',
            "start_service": 1966,
            "end_service": 3000,
            'caliber': 7.62, # mm - pintle-mounted GPMG variant
            'fire_rate': 750, # shot per minute
            'range': {'direct': 1100, 'indirect': 0 }, # m
        },
        'L37A2-7.62': { # Challenger 2 commander's MG
            'model': 'L37A2-7.62',
            "start_service": 1994,
            "end_service": 3000,
            'caliber': 7.62, # mm - improved L37A1
            'fire_rate': 750, # shot per minute
            'range': {'direct': 1100, 'indirect': 0 }, # m
        },
        'L94A1-7.62': { # Challenger 2, Warrior - Hughes 7.62mm chain gun
            'model': 'L94A1-7.62',
            "start_service": 1987,
            "end_service": 3000,
            'caliber': 7.62, # mm - EX-34 chain gun
            'fire_rate': 550, # shot per minute
            'range': {'direct': 1100, 'indirect': 0 }, # m
        },
        # --- German MGs ---
        'MG3-7.62': { # Leopard 1, Leopard 2, Marder
            'model': 'MG3-7.62',
            "start_service": 1968,
            "end_service": 3000,
            'caliber': 7.62, # mm - Rheinmetall MG3 GPMG
            'fire_rate': 1200, # shot per minute
            'range': {'direct': 1200, 'indirect': 0 }, # m
        },
        'MG34-7.92': { # WW2/early Cold War vehicles
            'model': 'MG34-7.92',
            "start_service": 1936,
            "end_service": 3000,
            'caliber': 7.92, # mm (7.92x57mm Mauser)
            'fire_rate': 900, # shot per minute
            'range': {'direct': 1000, 'indirect': 0 }, # m
        },
        # --- US MGs ---
        'M240C-7.62': { # M2 Bradley coaxial variant
            'model': 'M240C-7.62',
            "start_service": 1977,
            "end_service": 3000,
            'caliber': 7.62, # mm - coaxial variant of M240
            'fire_rate': 650, # shot per minute
            'range': {'direct': 1100, 'indirect': 0 }, # m
        },
        'M1919-7.62': { # M48 Patton, older US vehicles
            'model': 'M1919-7.62',
            "start_service": 1919,
            "end_service": 3000,
            'caliber': 7.62, # mm - Browning M1919 .30 cal
            'fire_rate': 500, # shot per minute
            'range': {'direct': 900, 'indirect': 0 }, # m
        },
        # --- Belgian MGs ---
        'FN MAG-7.62': { # Merkava, many NATO vehicles
            'model': 'FN MAG-7.62',
            "start_service": 1958,
            "end_service": 3000,
            'caliber': 7.62, # mm - FN Herstal MAG GPMG
            'fire_rate': 650, # shot per minute
            'range': {'direct': 1200, 'indirect': 0 }, # m
        },
        # --- French MGs ---
        'ANF1-7.62': { # Leclerc
            'model': 'ANF1-7.62',
            "start_service": 1979,
            "end_service": 3000,
            'caliber': 7.62, # mm - AA-NF1 7.62mm MG
            'fire_rate': 900, # shot per minute
            'range': {'direct': 600, 'indirect': 0 }, # m
        },
        'M693-12.7': { # Leclerc coaxial 12.7mm
            'model': 'M693-12.7',
            "start_service": 1992,
            "end_service": 3000,
            'caliber': 12.7, # mm
            'fire_rate': 550, # shot per minute
            'range': {'direct': 1500, 'indirect': 0 }, # m
        },
        # --- Russian MGs ---
        'PKM-7.62': { # infantry / pintle mount
            'model': 'PKM-7.62',
            "start_service": 1969,
            "end_service": 3000,
            'caliber': 7.62, # mm - Kalashnikov PKM GPMG
            'fire_rate': 650, # shot per minute
            'range': {'direct': 1000, 'indirect': 0 }, # m
        },
        'PKTM-7.62': { # BTR-82A - modernized coaxial
            'model': 'PKTM-7.62',
            "start_service": 1998,
            "end_service": 3000,
            'caliber': 7.62, # mm - modernized PKT
            'fire_rate': 750, # shot per minute
            'range': {'direct': 1200, 'indirect': 0 }, # m
        },
        # --- Chinese MGs ---
        'Type-59T-7.62': { # Type 59 coaxial
            'model': 'Type-59T-7.62',
            "start_service": 1959,
            "end_service": 3000,
            'caliber': 7.62, # mm - Chinese copy of SGMT
            'fire_rate': 600, # shot per minute
            'range': {'direct': 800, 'indirect': 0 }, # m
        },
        'Type-86-7.62': { # Type 99, ZBD-04 coaxial
            'model': 'Type-86-7.62',
            "start_service": 1986,
            "end_service": 3000,
            'caliber': 7.62, # mm - Chinese 7.62mm coaxial MG
            'fire_rate': 700, # shot per minute
            'range': {'direct': 1000, 'indirect': 0 }, # m
        },
        'QJC88-12.7': { # Type 99 commander's MG
            'model': 'QJC88-12.7',
            "start_service": 1988,
            "end_service": 3000,
            'caliber': 12.7, # mm - W85/QJC88 HMG
            'fire_rate': 650, # shot per minute
            'range': {'direct': 1500, 'indirect': 0 }, # m
        },
        # --- South Korean MGs ---
        'K6-12.7': { # K1/K2 tank commander's MG
            'model': 'K6-12.7',
            "start_service": 1984,
            "end_service": 3000,
            'caliber': 12.7, # mm - licensed M2HB variant
            'fire_rate': 550, # shot per minute
            'range': {'direct': 1500, 'indirect': 0 }, # m
        },

    },

    'FLAME_TRHOWERS': {},

    'GRENADE_LAUNCHERS': {
        'AGS-17': {
            'model': 'AGS-17',
            "start_service": 1971,
            "end_service": 3000,            
            'caliber': 30, # mm
            'fire_rate': 400, # shot per minute
            'TNT_equivalent': 0.25, # kg
            'range': {'direct': 1700, 'indirect': 0 }, # m
        },
    },
} 





