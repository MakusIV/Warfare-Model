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
        return 0

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
    },
        
    'ROCKETS': {}, 

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





