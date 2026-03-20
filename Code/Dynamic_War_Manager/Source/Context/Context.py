'''
 MODULE Context
 
 Elenco delle variabili di contesto

'''

#from typing import Literal
#VARIABLE = Literal['A', 'B, 'C']
from enum import Enum
from typing import Dict, List, Tuple

MAX_WORLD_DISTANCE = float('inf')
DCS_DATA_DIRECTORY = 'E:\\Sviluppo\Warfare_Model\\Code\\Persistence\\DCS_Data' # Directory for DCS table: Lua and Python.  att dcs funziona solo in windows quindi path solo per formato windows
DEBUG = False

COALITIONS = {
    'Blue': ['USA', 'Germany', 'France', 'Britain', 'Italy', 'Turkey', 'Greece', 'Georgia', 'Australia', 'Canada'],
    'Red': ['Russia', 'China', 'North_Korea', 'Iran', 'Syria'],
    'Neutral': ['India', 'Japan', 'Vietnam', 'Brazil']
}



PATH_TYPE = ['onroad', 'offroad', 'air', 'water']
ROUTE_TYPE = ['ground', 'air', 'water', 'mixed']

# Peso per il calcolo del valore complessivo di una produzione (Resource_Manager.production value)
PRODUCTION_WEIGHT = {
    'goods': 6,
    'energy': 8,
    'hr': 1,
    'hc': 10,
    'hs': 6,
    'hb': 3,
}


GROUND_ACTION  = {
    'Attack':   'Attack',
    'Defense':  'Defense',
    'Maintain': 'Maintain',
    'Retrait':  'Retrait' 
}

GROUND_WEAPON_TASK = {
    'Anti_Tank': 'Anti_Tank',
    'Anti_Air':  'Anti_Air',
    'Artillery': 'Artillery',
    'Infantry_Support': 'Infantry_Support'
}

AIR_TO_AIR_TASK = {
    
    'CAP': 'CAP',  
    'Fighter_Sweep': 'Fighter_Sweep'  ,
    'Intercept': 'Intercept',
    'Escort': 'Escort',
    'Recon': 'Recon',    
} 
AIR_TO_GROUND_TASK = {
    'CAS': 'CAS',
    'Strike': 'Strike', # coincidono con Ground Attack
    'Pinpoint_Strike': 'Pinpoint_Strike',
    'SEAD': 'SEAD',
    'Anti_Ship': 'Anti_Ship'
} 

AIR_TASK = AIR_TO_AIR_TASK | AIR_TO_GROUND_TASK

"""
AIR_TASK = {
    
    'CAP': 'CAP',  
    'Fighter_Sweep': 'Fighter_Sweep'  ,
    'Intercept': 'Intercept',
    'Escort': 'Escort',
    'Recon': 'Recon',
    'CAS': 'CAS',
    'Strike': 'Strike', # coincidono con Ground Attack
    'Pinpoint_Strike': 'Pinpoint_Strike',
    'SEAD': 'SEAD',
    'Anti_Ship': 'Anti_Ship'
} 
"""
SEA_TASK  = {

    'Attack':   'Attack', 
    'Defense':  'Defense',   
    'Retrait':  'Retrait' 
}

MILITARY_FORCES = ['ground', 'air', 'sea']

ACTION_TASKS = {
    'ground': GROUND_ACTION,
    'air': AIR_TASK,
    'sea': SEA_TASK
}

BLOCK_CATEGORY = {

    'Civilian': 'Civilian',
    'Logistic': 'Logistic',    
    'Military': 'Military',
    'All':      'All',
}

'''    
Divisione:      Brigate e/o Reggimenti - 10-20k men

Brigata:        2 Reggimenti - 3600 men

Reggimento:     3 Battaglioni -1800 men

Battaglione:    4 Compagnie - 600 men

Compagnia:      150 men
'''


MILITARY_CATEGORY = {

    'Ground_Base': ('Stronghold',  'Farp', 'Regiment', 'Battallion', 'Company', 'Brigade', 'Division', 'Command_&_Control_C2', 'Command_&_Control_C4'),

    'Air_Base': ('Airbase', 'Heliport'),

    'Naval_Base': ('Port', 'Shipyard', 'Naval_Group'),     
    
}

class Ground_Vehicle_Asset_Type(Enum):
    TANK = 'Tank'
    ARMORED = 'Armored'
    MOTORIZED = 'Motorized'
    ARTILLERY_FIXED = 'Artillery_Fixed'
    ARTILLERY_SEMOVENT = 'Artillery_Semovent'
    SAM_BIG = 'SAM_Big'
    SAM_MEDIUM = 'SAM_Medium'
    SAM_SMALL = 'SAM_Small'
    EWR = 'EWR'
    AAA = 'AAA'

ag = Ground_Vehicle_Asset_Type

# Peso per il calcolo della combat power  in Tactical_Evaluation Module
WEIGHT_FORCE_GROUND_ASSET = {

    ag.TANK: 7,
    ag.ARMORED: 5,   
    ag.MOTORIZED: 3,
    ag.ARTILLERY_FIXED: 4,
    ag.ARTILLERY_SEMOVENT: 7,
}

# Parametri per il calcolo della combat power degli asset da combattimento. 
# Sono considerati  pesi di bilanciamento per i calcoli della combat_power utilizzati per confrontare classi di veicoli diversi in una determinata azione
# Utilizzata in Tactical_Evaluation Modul e nel calcolo della combat_power Vehicle
# NOTA: Questo calcolo si basa sul valore di efficacia attibuito alla classificazione definita nel Context: tank, armor, ..
# Fatto (?): è opportuno rivederlo nell'ottica di una valutazione più accurata: attribuire una efficacia nell'attacco di una forza tank superiore rispetto ad una armor potrebbe essere erroneo,
# Fatto(?): Probabilmente è più opportuno valutare le capacità e prestazioni dello specifico veicolo in relazione all'azione da eseguire (attacco, difesa).         
# Max value = 5, min value = 1
# NOTA: Probabilmente dovrebbe essore più specifiche: Rapid_Retrait, Tactical_Retrait, , Fire_Saturation (per artillery, Tank) 
GROUND_COMBAT_EFFICACY = {
    GROUND_ACTION['Attack']: {'Tank': 5, 'Armored': 3.5, 'Motorized': 2, 'Artillery_Semovent': 4, 'Artillery_Fixed': 3},
    GROUND_ACTION['Defense']: {'Tank': 4, 'Armored': 3.5, 'Motorized': 2, 'Artillery_Semovent': 3, 'Artillery_Fixed': 5},
    GROUND_ACTION['Maintain']: {'Tank': 3, 'Armored': 3.7, 'Motorized': 4, 'Artillery_Semovent': 2, 'Artillery_Fixed': 3},    
    GROUND_ACTION['Retrait']: {'Tank': 3, 'Armored': 3.7, 'Motorized': 3, 'Artillery_Semovent': 2, 'Artillery_Fixed': 1},    
}


MAX_AIRCRAFT_TYPE_FOR_MISSION = 8 # massimo numero di aerei per una stessa tipologia per una missione, altrimenti si rischia di avere un numero eccessivo di aerei per una stessa tipologia, con conseguente distorsione dello score totale

STATE = {'Operational': True, 'Not_Operational': True , 'Destroyed': True, 'Critical': True, 'Damaged': True}



AIRCRAFT_TYPE = {# necessario?

    'F-4E': 'F-4E',
    'Mig-21': 'Mig-21bis',
    'F-14A': 'F-14AgM',
    'F-14B': 'F-14B4',
}

#[action][asset.type]
AIR_COMBAT_EFFICACY = {
    
    'F-15': {AIR_TASK['CAP']: 8, AIR_TASK['Fighter_Sweep']: 8, AIR_TASK['Intercept']: 7, AIR_TASK['Escort']: 8, AIR_TASK['Recon']: 5, AIR_TASK['CAS']: 4, AIR_TASK['Strike']: 4, AIR_TASK['Pinpoint_Strike']: 4, AIR_TASK['SEAD']: 2},
    'F-4E': {AIR_TASK['CAP']: 6, AIR_TASK['Fighter_Sweep']: 6, AIR_TASK['Intercept']: 6, AIR_TASK['Escort']: 6, AIR_TASK['Recon']: 7, AIR_TASK['CAS']: 8, AIR_TASK['Strike']: 8, AIR_TASK['Pinpoint_Strike']: 7, AIR_TASK['SEAD']: 6}

}


class SHAPE3D(Enum): 
    CYLINDER = 'Cylinder' 
    CUBE = 'Cube'
    SPHERE = 'Sphere'
    SEMISPHERE = 'SemiSphere'
    CONE = 'Cone'
    TRUNC_CONE = 'Trunc_Cone'
    PRISM = 'Prism'
    SOLID = 'Solid'


class SHAPE2D(Enum): 
    CIRCLE = 'Circle'
    SQUARE = 'Square'
    HEXAGON = 'Hexagon'

class VALUE(Enum): 
    CRITICAL ='Critical'
    VERY_HIGH = 'Very_High'
    HIGH = 'High'
    MEDIUM = 'Medium'
    LOW = 'Low'
    VERY_LOW = 'Very_Low'

class FOOD_CATEGORY(Enum):
    GOODS = 'Goods'
    ENERGY = 'Energy'
    GOODS_AND_ENERGY = 'Goods & Energy'

class COUNTRY(Enum): 
    GERMANY = 'Germany'
    FRANCE = 'France'
    BRITAIN = 'Britain'
    USA = 'USA'
    RUSSIA = 'Russia'
    CHINA = 'China'
    INDIA = 'India'
    JAPAN = 'Japan'
    KOREA = 'Korea'
    GEORGIA = 'Georgia'
    TURKEY = 'Turkey'
    GREECE = 'Greece'
    VIETNAM = 'Vietnam'
    AUSTRALIA = 'Australia'
    BRAZIL = 'Brazil'
    CANADA = 'Canada'

class SKILL(Enum): 
    AVERAGE = 'Average'
    GOOD = 'Good'
    HIGH = 'High'
    EXCELLENT = 'Excellent'
    

class GROUP_CATEGORY(Enum): 
    HELICOPTER = 'helicopter'
    PLANE = 'plane'
    VEHICLE = 'vehicle'
    STATIC = 'static'

SIDE = ['Blue', 'Red', 'Neutral']

AREA_FOR_VOLUME = {  
    SHAPE2D.CIRCLE : {SHAPE3D.CYLINDER, SHAPE3D.SPHERE, SHAPE3D.SEMISPHERE, SHAPE3D.CONE, SHAPE3D.TRUNC_CONE, SHAPE3D.SOLID},
    SHAPE2D.SQUARE : {SHAPE3D.CUBE},
    SHAPE2D.HEXAGON : {SHAPE3D.PRISM}
}

class Parked_Asset_Type(Enum):
    Transport_Aircraft = 'Parked_Transport_Aircraft'
    Transport_Aircraft_Big = 'Parked_Transport_Aircraft_Big'
    Transport_Helicopter = 'Parked_Transport_Helicopter'
    Transport_Helicopter_Big = 'Parked_Transport_Helicopter_Big'
    Aircraft_Fighter = 'Parked_Aircraft_Fighter'
    Aircraft_Fighter_Bomber = 'Parked_Aircraft_Fighter_Bomber'
    Aircraft_Bomber = 'Parked_Aircraft_Bomber'
    Helicopter = 'Parked_Helicopter'
    Helicopter_Big = 'Parked_Helicopter_Big'
    Transport_Ship_Large = 'Parked_Transport_Ship_Large'
    Transport_Ship_Medium = 'Parked_Transport_Ship_Medium'
    Transport_Ship_Small = 'Parked_Transport_Ship_Small'
    Tank = 'Parked_Tank'
    Armored_Vehicle = 'Parked_Armored_Vehicle'
    Motorized_Vehicle = 'Parked_Motorized_Vehicle'
    Train = 'Parked_Train'
    Truck = 'Parked_Truck'
    Generic_Vehicle = 'Parked_Generic_Vehicle'

class Air_Asset_Type(Enum):
    FIGHTER = 'Fighter'
    FIGHTER_BOMBER = 'Fighter_Bomber'
    ATTACKER = 'Attacker'
    BOMBER = 'Bomber'
    HEAVY_BOMBER = 'Heavy_Bomber'
    AWACS = 'Awacs'
    RECON = 'Recon'
    TRANSPORT = 'Transport'
    HELICOPTER = 'Helicopter'

# key: asset type
AIR_MILITARY_CRAFT_ASSET = {
    Air_Asset_Type.FIGHTER.value:          {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
    Air_Asset_Type.FIGHTER_BOMBER.value:   {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
    Air_Asset_Type.ATTACKER.value:         {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
    Air_Asset_Type.BOMBER.value:           {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
    Air_Asset_Type.HEAVY_BOMBER.value:     {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
    Air_Asset_Type.AWACS.value:            {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
    Air_Asset_Type.RECON.value:            {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
    Air_Asset_Type.TRANSPORT.value:        {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
    Air_Asset_Type.HELICOPTER.value:       {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},  
}

 # Asset:                   STRUCTURE_ASSET_CATEGORY, GROUND_ASSET_CATEGORY, AIR_ASSET_CATEGORY, BLOCK_ASSET, BLOCK_ASSET_CATEGORY
 # Tactical_Evaluation:     GROUND_ASSET_CATEGORY, GROUND_ACTION, GROUND_COMBAT_EFFICACY
 # Strategical_Evaluation:  Military_CATEGORY

#GROUND_ASSET_CATEGORY, AIR_ASSET_CATEGORY, STRUCTURE_ASSET_CATEGORY]
# key1+key2: asset category, key3: asset type


AIR_DEFENSE_ASSET = {  
    
    'SAM':                  {   'Big': {#Roccaforte: Brigade, 2 Regiment, 6 Battallion (5 Company)
                                    'Command_&_Control': {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    'Track_Radar': {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    'Search_Radar': {'cost': None, 'value': VALUE.VERY_HIGH, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    'Launcher': {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    'Truck': {'cost': None, 'value': VALUE.LOW, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    'Generator': {'cost': None, 'value': VALUE.HIGH, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33}                                    
                                },
                                'Medium': {
                                    'Command_&_Control': {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    'Track_Radar': {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    'Search_Radar': {'cost': None, 'value': VALUE.VERY_HIGH, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    'Search_&_Track_Radar': {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    'Launcher': {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    'Truck': {'cost': None, 'value': VALUE.LOW, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    'Generator': {'cost': None, 'value': VALUE.HIGH, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33}                                    
                                },
                                'Small': {
                                    'SAM': {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},                                    
                                    'Truck': {'cost': None, 'value': VALUE.LOW, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},                                    
                                },                                                                                                
                                'Manpad': {
                                    'Manpad': {'cost': None, 'value': VALUE.CRITICAL, 't2r':1, 'rcp': {'hc': 0, 'hs': 0, 'hb': 1, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},                                                                        
                                },                                                                                                
                            },
    'EWR':                  {   'EWR': {
                                    'Command_&_Control': {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},                                    
                                    'Radar': {'cost': None, 'value': VALUE.VERY_HIGH, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},                                    
                                    'Truck': {'cost': None, 'value': VALUE.LOW, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    'Generator': {'cost': None, 'value': VALUE.HIGH, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33}                                    
                                },                                
                            },

    'AAA':                  {   'AAA': {                                    
                                    'AAA': {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    'Truck': {'cost': None, 'value': VALUE.LOW, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33}                                    
                                },                                
                            },
}    
                    

# Caratteristiche degli asset delle diversè unità Military: Corazzate, Meccanizzate, Motorizzate e Artiglieria
# key1: asset category, key2: asset type
GROUND_MILITARY_VEHICLE_ASSET = {
    # Corazzata 
    ag.TANK.value:{ 'Command_&_Control':                {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},     
                    'Tank':                             {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                    'Main_Battle_Tank':                 {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},     
                    'Infantry_Fighting_Vehicle':        {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                    'Scout_&_Recon':                    {'cost': None, 'value': VALUE.LOW, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                    'Truck_Supply':                     {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33}},
    # Meccanizzata
    ag.ARMORED.value:{ 'Command_&_Control':             {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},     
                    'Armored_Personal_Carrier':         {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                    'Infantry_Fighting_Vehicle':        {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                    'Scout_&_Recon':                    {'cost': None, 'value': VALUE.LOW, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                    'Truck_Supply':                     {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},                    
                    'Self_Propelled_ATGM':              {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                    'Self_Propelled_Gun':               {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33}    },
    # Motorizzata
    ag.MOTORIZED.value:{'Command_&_Control':            {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},     
                    'Armored_Personal_Carrier':         {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                    'Infantry_Fighting_Vehicle':        {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                    'Truck_Supply':                     {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},                                        
                    'Scout_&_Recon':                    {'cost': None, 'value': VALUE.LOW, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                    'Self_Propelled_ATGM':              {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                    'Self_Propelled_Gun':               {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33} },
    # Artiglieria fissa
    ag.ARTILLERY_FIXED.value:{'Command_&_Control':      {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                    'Howitzer_Big':                     {'cost': None, 'value': VALUE.HIGH, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                    'Howitzer_Medium':                  {'cost': None, 'value': VALUE.HIGH, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                    'Howitzer_Small':                   {'cost': None, 'value': VALUE.HIGH, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                    'Mortar':                           {'cost': None, 'value': VALUE.HIGH, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},                    
                    'Truck_Supply':                     {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                    'Scout_&_Recon':                    {'cost': None, 'value': VALUE.LOW, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33} },
    # Artiglieria semovent
    ag.ARTILLERY_SEMOVENT.value:{'Command_&_Control':   {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},                    
                    'Mortar':                           {'cost': None, 'value': VALUE.HIGH, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                    'Multiple_Rocket_Launcher':         {'cost': None, 'value': VALUE.HIGH, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                    'Self_Propelled_Artillery_Big':     {'cost': None, 'value': VALUE.HIGH, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                    'Self_Propelled_Artillery_Medium':  {'cost': None, 'value': VALUE.HIGH, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                    'Self_Propelled_Artillery_Small':   {'cost': None, 'value': VALUE.HIGH, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                    'Truck_Supply':                     {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                    'Scout_&_Recon':                    {'cost': None, 'value': VALUE.LOW, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33} }
}

class Sea_Asset_Type(Enum):
    CARRIER = 'Carrier'
    DESTROYER = 'Destroyer'
    CRUISER = 'Cruiser'
    FRIGATE = 'Frigate'
    FAST_ATTACK = 'Fast_Attack'
    SUBMARINE = 'Submarine'
    AMPHIBIOUS_ASSAULT_SHIP = 'Amphibious_Assault_Ship'
    TRANSPORT = 'Transport'
    CIVILIAN = 'Civilian'

asea = Sea_Asset_Type


# key: asset type
SEA_MILITARY_CRAFT_ASSET = {
     
    asea.CARRIER.value:                  {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},      
    asea.DESTROYER.value:                {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},     
    asea.CRUISER.value:                  {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},     
    asea.FRIGATE.value:                  {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},     
    asea.FAST_ATTACK.value:              {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},    
    asea.SUBMARINE.value:                {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},     
    asea.AMPHIBIOUS_ASSAULT_SHIP.value:  {'cost': None, 'value': VALUE.LOW, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},     
    asea.TRANSPORT.value:                {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},     
    asea.CIVILIAN.value:                 {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},     

}



"""
| Tipo di arma / Configurazione                                              | Effetto principale                              | Meccanismo / Caratteristica                                                                                                                                    | Tipo di obiettivo idoneo                                                                                                                                                                   |
| -------------------------------------------------------------------------- | ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Bomba bunker‑buster / deep‑penetration (penetration bomb)                  | Penetration (penetrazione fisica)               | Struttura robusta, spesso con coda stabilizzatrice, detonazione a tempo ritardato dopo l’impatto e la penetrazione nel terreno o nel calcestruzzo. wikipedia+1 | Bunker sotterranei, command‑and‑control in profondità, centri di comando in montagna, silos, tunnel, hangar rinforzati in calcestruzzo massiccio, infrastrutture sotterranee.              |
| Missile anti‑bunker / earth‑penetrating (EPW)                              | Penetration + blast sotterraneo                 | Testata progettata per perforare roccia/terreno prima dell’esplosione; effetto combinato di onda d’urto e frantumazione della roccia circostante. wikipedia+1  | Obiettivi corazzati interrati, bunker profondi, nodi di comando in roccia, infrastrutture strategiche nascoste.                                                                            |
| Bomba a frammentazione (HE fragmentation / general‑purpose)                | Fragmentation (scheggiamento)                   | Guscio metallico che si frammenta, diffondendo schegge ad alta velocità su un’area ampia. wikipedia+1                                                          | Edifici non rinforzati, serbatoi carburante esterni, hangar leggeri, parchi veicoli, aree di raduno di truppe, magazzini di materiale logistico.                                           |
| Bomba a frammentazione + submunizioni (cluster / cassette)                 | Fragmentation + area effect                     | Dispensa piccoli sub‑proiettili o bombe a frammentazione che saturano un’area ampia. wikipedia​                                                                | Zone di truppe a cielo aperto, colonne di veicoli, aree di parcheggio, formazioni di fanteria disperse.                                                                                    |
| Razzo a frammentazione (rocket HE / fragmentation)                         | Fragmentation localizzata                       | Effetto simile a una bomba HE ma con minore quantità di esplosivo e traiettoria curva, più sensibile a dispersione. wikipedia+1                                | Target di piccole/medie dimensioni: postazioni di mortaio, mitragliatrici, veicoli non corazzati, aree di supporto ravvicinato.                                                            |
| Bomba ad alta esplosività (HE – blast / overpressure)                      | Blast / Overpressure (onda d’urto)              | Grande esplosivo, forte onda d’urto che distrugge strutture, vetrate, interni di edifici. wikipedia​                                                           | Edifici portanti, infrastrutture industriali, stazioni di pompaggio, nodi di raffinazione, costruzioni massicce non corazzate.                                                             |
| Missile da crociera (cruise missile – HE / blast)                          | Blast / Overpressure su obiettivo puntiforme    | Volandato a lunga distanza, impatto ad alta velocità, forte onda d’urto e pressione interna. wikipedia​                                                        | Ponti, nodi ferroviari, impianti elettrici, grandi stazioni di rifornimento, stazioni radar fisse, infrastrutture critiche localizzate.                                                    |
| Bomba incendiaria / bomba a fuoco liquido (incendiary / fire‑bomb)         | Thermal / Fire (incendiario)                    | Rilascia sostanze infiammabili (napalm, termite, gel) che bruciano a lungo e propagano incendi. wikipedia​                                                     | Serbatoi carburante esterni, depositi di munizioni, hangar con velivoli, magazzini di materiali infiammabili, aree di stoccaggio combustibile.                                             |
| Missile / bomba termobarica (thermobaric)                                  | Thermal + Blast in spazi confinati              | Esplosione in due fasi che consuma ossigeno e genera lunga onda d’urto, estremamente efficace in spazi chiusi. wikipedia​                                      | Caverne, tunnel superficiali, bunker poco profondi, trincee, aree di truppe ravvicinate in urban centers o canyon.                                                                         |
| Missile guidato di precisione (cruise, balistico tattico, ALCM)            | Precision + Blast / Overpressure                | Estrema accuratezza, capacità di attaccare obiettivi a grande distanza con minima dispersione. wikipedia​                                                      | Comandi nemici lontani, infrastrutture critiche, radar, stazioni C2, base aerea di retroguardia, impianti strategici sensibili.                                                            |
| Bomba guidata (JDAM, Paveway, ecc.)                                        | Precision + Blast / Penetration o Fragmentation | Aggiunge una guida GPS / laser a una bomba inerziale, permettendo di scegliere tra testate HE, fragmentation o bunker‑buster. wikipedia​                       | Obiettivi puntuali in area urbana sensibile, singoli edifici, bunker selezionato, hangar, infrastrutture critiche localizzate, senza saturare grandi aree.                                 |
| Missile cinetico / bomba cinetica (hypervelocity rod / kinetic penetrator) | Kinetic Impact (impatto puro)                   | Massa pesante che colpisce ad altissima velocità, distruggendo per energia cinetica senza esplosivo. wikipedia​                                                | Obiettivi molto protetti dove si vuole evitare esplosione e ridurre collateral damage: strutture strategiche coperte, nodi di comando profondi, infrastrutture critiche in aree sensibili. |
| Razzo non guidato (unguided rocket – HE o fragmentation)                   | Blast / Fragmentation dispersi                  | Bassa precisione, ma buona potenza per area; usato in contesti ravvicinati o dove il costo è un fattore critico. wikipedia+1                                   | Obiettivi di massa meno protetti: basi di appoggio, aree di parcheggio, postazioni di supporto, formazioni di fanteria esposte.                                                            |
| Bombardamenti a tappeto (carpet bombing – HE + fragmentation)              | Area effect complessivo (blast + fragmentation) | Scarica di molte bombe HE o fragmentation su un’area ampia per saturazione. wikipedia​                                                                         | Zone industriali ampie, basi aeree estese, aree di concentrazione truppe, aree logisticamente dense dove la precisione non è prioritaria.                                                  |
"""

class Weapon_Power_Effect(Enum):
    PENETRATION = 'Penetration'
    FRAGMENTATION = 'Fragmentation'
    HIGH_EXPLOSIVE = 'High_Explosive'
    CLUSTER = 'Cluster'
    THERMOBARIC = 'Thermobaric'
    THERMAL = 'Thermal'
    BLAST = 'Blast'
    KINETIC = 'Kinetic'

class Weapon_Area_Effect(Enum):
    PRECISION = 'Precision'
    WIDE = 'Wide'
    LOCALIZED = 'Localized'
    INTERNAL = 'Internal'

class Logistic_Asset_Type(Enum):
    BRIDGE = 'Bridge'
    CHECK_POINT = 'Check_Point'
    STATION = 'Station'
    RAILWAY_INTERCHANGE = 'Railway_Interchange'
    #PORT = 'Port'
    DOCK = 'Port'
    #AIRBASE = 'Airbase'
    RUNWAY = 'Runway'
    #HELIBASE = 'Helibase'
    HELI_PLATFORM = 'Heli_Platform'
    ELECTRIC_INFRASTRUCTURE = 'Electric_Infrastructure'
    GAS_INFRASTRUCTURE = 'Gas_Infrastructure'
    PETROL_INFRASTRUCTURE = 'Petrol_Infrastructure'
    POWER_PLANT = 'Power_Plant'
    OIL_TANK = 'Oil_Tank'
    DEPOT = 'Depot'
    BUILDING = 'Building'
    FACTORY = 'Factory'
    FARM = 'Farm'
    ADMINISTRATIVE_INFRASTRUCTURE = 'Administrative_Infrastructure'
    ENERGY_INFRASTRUCTURE = 'Energy_Infrastructure'
    SERVICE_INFRASTRUCTURE = 'Service_Infrastructure'
    COMMAND_AND_CONTROL = 'Command_&_Control'
    BARRACK = 'Barrack'
    HANGAR = 'Hangar'
    BUNKER = 'Bunker'



"""                                                                                                         

    LOGICA DI ASSEGNAZIONE

  ┌─────────────────────────┬───────────┬─────────────────────────┬─────────────────────────────────────┐   
  │        Categoria        │ precision │          power          │                Asset                │   
  ├─────────────────────────┼───────────┼─────────────────────────┼─────────────────────────────────────┤   
  │                         │           │                         │ Bridge, Railway_Interchange,        │   
  │ Strutturali duri        │ PRECISION │ KINETIC, HIGH_EXPLOSIVE │ Airbase, Port, Helibase,            │   
  │                         │           │                         │ Power_Plant                         │   
  ├─────────────────────────┼───────────┼─────────────────────────┼─────────────────────────────────────┤ 
  │                         │           │ PENETRATION             │                                     │   
  │ Bunkerizzati/rinforzati │ PRECISION │ (+HIGH_EXPLOSIVE per    │ Bunker, Command_&_Control, Hangar   │   
  │                         │           │ Hangar)                 │                                     │   
  ├─────────────────────────┼───────────┼─────────────────────────┼─────────────────────────────────────┤   
  │ Non rinforzati          │ LOCALIZED │ BLAST, FRAGMENTATION    │ Station, Depot, Building, Barrack,  │   
  │                         │           │                         │ Farm, infrastrutture varie          │   
  ├─────────────────────────┼───────────┼─────────────────────────┼─────────────────────────────────────┤   
  │ Infiammabili            │ LOCALIZED │ BLAST, THERMAL          │ Gas_Infrastructure,                 │   
  │                         │           │                         │ Petrol_Infrastructure, Oil_Tank     │   
  └─────────────────────────┴───────────┴─────────────────────────┴─────────────────────────────────────┘   
                                                                                                        """

lat = Logistic_Asset_Type
wpe = Weapon_Power_Effect
wae = Weapon_Area_Effect

WEAPON_PARAM_ASSIGNATION_FOR_ASSET_TYPE = {

    # --- PRECISION + KINETIC/HIGH_EXPLOSIVE: obiettivi strutturali duri ---
    lat.BRIDGE:                        {'precision': [wae.PRECISION],  'power': [wpe.BLAST, wpe.KINETIC, wpe.HIGH_EXPLOSIVE]},
    lat.RAILWAY_INTERCHANGE:           {'precision': [wae.PRECISION],  'power': [wpe.KINETIC, wpe.HIGH_EXPLOSIVE]},
    lat.DOCK:                          {'precision': [wae.PRECISION],  'power': [wpe.BLAST, wpe.HIGH_EXPLOSIVE]},
    lat.RUNWAY:                        {'precision': [wae.PRECISION],  'power': [wpe.KINETIC, wpe.HIGH_EXPLOSIVE]},
    lat.HELI_PLATFORM:                 {'precision': [wae.PRECISION],  'power': [wpe.HIGH_EXPLOSIVE]},
    lat.POWER_PLANT:                   {'precision': [wae.PRECISION],  'power': [wpe.BLAST, wpe.HIGH_EXPLOSIVE]},

    # --- PRECISION + PENETRATION: obiettivi bunkerizzati/rinforzati ---
    lat.BUNKER:                        {'precision': [wae.PRECISION],  'power': [wpe.PENETRATION]},
    lat.COMMAND_AND_CONTROL:           {'precision': [wae.PRECISION],  'power': [wpe.PENETRATION]},
    lat.HANGAR:                        {'precision': [wae.PRECISION],  'power': [wpe.PENETRATION, wpe.HIGH_EXPLOSIVE]},

    # --- LOCALIZED + BLAST/FRAGMENTATION: strutture non rinforzate ---
    lat.CHECK_POINT:                   {'precision': [wae.LOCALIZED],  'power': [wpe.BLAST, wpe.KINETIC, wpe.HIGH_EXPLOSIVE]},
    lat.STATION:                       {'precision': [wae.LOCALIZED],  'power': [wpe.BLAST, wpe.FRAGMENTATION]},
    lat.ELECTRIC_INFRASTRUCTURE:       {'precision': [wae.LOCALIZED],  'power': [wpe.BLAST, wpe.FRAGMENTATION]},
    lat.ENERGY_INFRASTRUCTURE:         {'precision': [wae.LOCALIZED],  'power': [wpe.BLAST, wpe.FRAGMENTATION]},
    lat.ADMINISTRATIVE_INFRASTRUCTURE: {'precision': [wae.LOCALIZED],  'power': [wpe.BLAST, wpe.FRAGMENTATION]},
    lat.SERVICE_INFRASTRUCTURE:        {'precision': [wae.LOCALIZED],  'power': [wpe.BLAST, wpe.FRAGMENTATION]},
    lat.DEPOT:                         {'precision': [wae.LOCALIZED],  'power': [wpe.BLAST, wpe.FRAGMENTATION]},
    lat.BARRACK:                       {'precision': [wae.LOCALIZED],  'power': [wpe.BLAST, wpe.FRAGMENTATION]},
    lat.BUILDING:                      {'precision': [wae.LOCALIZED],  'power': [wpe.BLAST, wpe.FRAGMENTATION]},
    lat.FACTORY:                       {'precision': [wae.LOCALIZED],  'power': [wpe.BLAST, wpe.HIGH_EXPLOSIVE]},
    lat.FARM:                          {'precision': [wae.LOCALIZED],  'power': [wpe.BLAST, wpe.FRAGMENTATION]},

    # --- LOCALIZED + THERMAL: infrastrutture con materiali infiammabili ---
    lat.GAS_INFRASTRUCTURE:            {'precision': [wae.LOCALIZED],  'power': [wpe.BLAST, wpe.THERMAL]},
    lat.PETROL_INFRASTRUCTURE:         {'precision': [wae.LOCALIZED],  'power': [wpe.BLAST, wpe.THERMAL]},
    lat.OIL_TANK:                      {'precision': [wae.LOCALIZED],  'power': [wpe.BLAST, wpe.THERMAL]},

}

def get_weapons_param_for_asset_type(asset_type: str) -> Dict:

    if asset_type not in WEAPON_PARAM_ASSIGNATION_FOR_ASSET_TYPE.keys():
        return None
    return WEAPON_PARAM_ASSIGNATION_FOR_ASSET_TYPE[asset_type]


# key1:   Block Class, key2: Asset Category, key 3: Asset type
# INFRASTRUCTURE BLOCK ASSET
BLOCK_INFRASTRUCTURE_ASSET = {  
    
    'Transport':             {  'Road': {
                                    lat.BRIDGE.value: {'cost': None, 'value': VALUE.CRITICAL, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.CHECK_POINT.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Truck.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33}
                                },
                                'Railway': {
                                    lat.STATION.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.RAILWAY_INTERCHANGE.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Train.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33}
                                },
                                'Port': {
                                    lat.DOCK.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Transport_Ship_Large.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Transport_Ship_Medium.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Transport_Ship_Small.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33}
                                },
                                'Airport': {
                                    lat.RUNWAY.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Aircraft_Fighter.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Aircraft_Fighter_Bomber.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Aircraft_Bomber.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33}
                                },
                                'Helibase': {
                                    lat.HELI_PLATFORM.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Transport_Helicopter.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Transport_Helicopter_Big.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33}
                                },
                                'Electric': {
                                    lat.ELECTRIC_INFRASTRUCTURE.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33}
                                },
                                'Fuel_Line': {
                                    lat.GAS_INFRASTRUCTURE.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.PETROL_INFRASTRUCTURE.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Truck.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33}
                                }
                            },                    

    'Production':           {   'Power_Plant': {
                                    lat.POWER_PLANT.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.OIL_TANK.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.DEPOT.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.BUILDING.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33}
                                },
                                'Factory': {
                                    lat.FACTORY.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.OIL_TANK.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.DEPOT.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.BUILDING.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33}
                                },
                                'Farm': {
                                    lat.FARM.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.OIL_TANK.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.DEPOT.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.BUILDING.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33}
                                },
                            },

    'Urban':               {   'Administrative': {
                                    lat.ADMINISTRATIVE_INFRASTRUCTURE.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.BUILDING.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33}
                                },
                                'Civilian': {
                                    lat.BUILDING.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33}
                                },
                                'Service': {
                                    lat.ENERGY_INFRASTRUCTURE.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.SERVICE_INFRASTRUCTURE.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.OIL_TANK.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.DEPOT.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.BUILDING.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Truck.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Generic_Vehicle.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33}
                                },
                            },

    'Storage':              {   'Administrative': {
                                    lat.ADMINISTRATIVE_INFRASTRUCTURE.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.BUILDING.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Generic_Vehicle.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                },
                                'Service': {
                                    lat.ENERGY_INFRASTRUCTURE.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.OIL_TANK.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.DEPOT.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.BUILDING.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Generic_Vehicle.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Truck.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                },
                            },

    'Military':             {   'Stronghold': {#Roccaforte: Brigade, 2 Regiment, 6 Battallion (5 Company)
                                    lat.COMMAND_AND_CONTROL.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.BARRACK.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.HANGAR.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.DEPOT.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Generic_Vehicle.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Truck.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Tank.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Armored_Vehicle.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33}
                                },
                                'Farp': {
                                    lat.COMMAND_AND_CONTROL.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.OIL_TANK.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.DEPOT.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.BARRACK.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.BUILDING.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Helicopter.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Helicopter_Big.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Generic_Vehicle.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Truck.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},                                    
                                    Parked_Asset_Type.Tank.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Armored_Vehicle.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33}                                                                                             
                                },
                                'Airbase': {
                                    lat.RUNWAY.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.COMMAND_AND_CONTROL.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.HANGAR.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.OIL_TANK.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.DEPOT.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.BUILDING.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.BARRACK.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Transport_Aircraft.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Transport_Aircraft_Big.value: {'cost': None, 'value': VALUE.HIGH, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Aircraft_Fighter.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Aircraft_Fighter_Bomber.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Aircraft_Bomber.value: {'cost': None, 'value': VALUE.HIGH, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Helicopter.value: {'cost': None, 'value': VALUE.LOW, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Helicopter_Big.value: {'cost': None, 'value': VALUE.LOW, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Generic_Vehicle.value: {'cost': None, 'value': VALUE.LOW, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},                                    
                                    Parked_Asset_Type.Truck.value: {'cost': None, 'value': VALUE.LOW, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},                                    
                                    Parked_Asset_Type.Tank.value: {'cost': None, 'value': VALUE.LOW, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Armored_Vehicle.value: {'cost': None, 'value': VALUE.LOW, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33}                                                                                             
                                },
                                'Helibase': {
                                    lat.HELI_PLATFORM.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.COMMAND_AND_CONTROL.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.HANGAR.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.OIL_TANK.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.DEPOT.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.BUILDING.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.BARRACK.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},                                    
                                    Parked_Asset_Type.Helicopter.value: {'cost': None, 'value': VALUE.LOW, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Helicopter_Big.value: {'cost': None, 'value': VALUE.LOW, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Generic_Vehicle.value: {'cost': None, 'value': VALUE.LOW, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},                                    
                                    Parked_Asset_Type.Truck.value: {'cost': None, 'value': VALUE.LOW, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},                                    
                                    Parked_Asset_Type.Tank.value: {'cost': None, 'value': VALUE.LOW, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Armored_Vehicle.value: {'cost': None, 'value': VALUE.LOW, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33}                                                                                             
                                },
                                'Port': {
                                    lat.DOCK.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.COMMAND_AND_CONTROL.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.HANGAR.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.OIL_TANK.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.DEPOT.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.BUILDING.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.BARRACK.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Transport_Ship_Large.value: {'cost': None, 'value': VALUE.HIGH, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Transport_Ship_Medium.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Transport_Ship_Small.value: {'cost': None, 'value': VALUE.LOW, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Generic_Vehicle.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},                                    
                                    Parked_Asset_Type.Truck.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},                                    

                                },
                                'Shipyard': {
                                    lat.COMMAND_AND_CONTROL.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.HANGAR.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.OIL_TANK.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.DEPOT.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.BUILDING.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.BARRACK.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Generic_Vehicle.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Truck.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                },
                                'Air_defense': {#Roccaforte: Brigade, 2 Regiment, 6 Battallion (5 Company)
                                    lat.COMMAND_AND_CONTROL.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.BARRACK.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 1, 'hs': 4, 'hb': 3, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    lat.DEPOT.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},
                                    Parked_Asset_Type.Generic_Vehicle.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},                                    
                                    Parked_Asset_Type.Truck.value: {'cost': None, 'value': VALUE.MEDIUM, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33},                                    
                                    Parked_Asset_Type.Armored_Vehicle.value: {'cost': None, 'value': VALUE.LOW, 't2r':7, 'rcp': {'hc': 0, 'hs': 0, 'hb': 6, 'hr': None, 'goods': 1, 'energy': None}, 'payload%': 33}                                                                                             
                                },                                                                                                
                            },

                    
}

class Target_Class_Name(Enum):
    SOFT = 'Soft'
    ARMORED = 'Armored'
    HARD = 'Hard'
    STRUCTURE = 'Structure'
    AIR_DEFENSE = 'Air_Defense'
    AIRBASE = 'Airbase'
    HELIBASE = 'Helibase'   
    PORT = 'Port'
    SHIPYARD = 'Shipyard'
    FARP = 'Farp'
    STRONGHOLD = 'Stronghold'
    SHIP = 'ship'
    AIRCRAFT = 'Aircraft'
    GENERIC = 'Generic'


tc = Target_Class_Name

TARGET_CLASSIFICATION = {
    tc.SOFT.value:          [   Parked_Asset_Type.Transport_Aircraft.value, 
                                Parked_Asset_Type.Transport_Aircraft_Big.value,
                                Parked_Asset_Type.Transport_Helicopter.value,
                                Parked_Asset_Type.Transport_Helicopter_Big.value,
                                Parked_Asset_Type.Motorized_Vehicle.value, 
                                Parked_Asset_Type.Truck.value,
                                Parked_Asset_Type.Generic_Vehicle.value,
                                Parked_Asset_Type.Aircraft_Bomber.value,
                                Parked_Asset_Type.Aircraft_Fighter.value,
                                Parked_Asset_Type.Aircraft_Fighter_Bomber.value, # Transport, Helicopter, Aircraft
                                Parked_Asset_Type.Helicopter.value,
                                Parked_Asset_Type.Helicopter_Big.value,
                                Ground_Vehicle_Asset_Type.MOTORIZED.value, 
                                Ground_Vehicle_Asset_Type.ARTILLERY_FIXED.value,                        
                                Ground_Vehicle_Asset_Type.EWR.value

                            ], # Motorized, Infantry
    tc.ARMORED.value:       [   Ground_Vehicle_Asset_Type.ARMORED.value, 
                                Ground_Vehicle_Asset_Type.TANK.value, 
                                Ground_Vehicle_Asset_Type.AAA.value, 
                                Ground_Vehicle_Asset_Type.ARTILLERY_SEMOVENT.value,                    
                            ], # Tank, Armored Vehicle
    tc.HARD.value:          [   lat.BRIDGE.value, lat.BUNKER.value, lat.HANGAR.value, lat.DEPOT.value ],
    tc.STRUCTURE.value:     [   lat.BUILDING.value, lat.OIL_TANK.value, lat.RAILWAY_INTERCHANGE.value, lat.POWER_PLANT.value, lat.FACTORY.value, lat.GAS_INFRASTRUCTURE.value, lat.PETROL_INFRASTRUCTURE.value, lat.ADMINISTRATIVE_INFRASTRUCTURE.value, lat.ENERGY_INFRASTRUCTURE.value, lat.SERVICE_INFRASTRUCTURE.value], # Building, Factory, Depot, ...
    tc.AIR_DEFENSE.value:   [   Ground_Vehicle_Asset_Type.SAM_MEDIUM.value,
                                Ground_Vehicle_Asset_Type.SAM_SMALL.value,
                                Ground_Vehicle_Asset_Type.SAM_BIG.value,
                                Ground_Vehicle_Asset_Type.AAA.value
                            ],
    tc.AIRBASE.value:      [   BLOCK_INFRASTRUCTURE_ASSET['Military']['Airbase'].keys()],
    tc.HELIBASE.value:     [   BLOCK_INFRASTRUCTURE_ASSET['Military']['Helibase'].keys()],
    tc.PORT.value:         [   BLOCK_INFRASTRUCTURE_ASSET['Military']['Port'].keys()],
    tc.SHIPYARD.value:     [   BLOCK_INFRASTRUCTURE_ASSET['Military']['Shipyard'].keys()],
    tc.FARP.value:         [   BLOCK_INFRASTRUCTURE_ASSET['Military']['Farp'].keys()],
    tc.STRONGHOLD.value:   [   BLOCK_INFRASTRUCTURE_ASSET['Military']['Stronghold'].keys()],
    tc.SHIP.value:         [   Parked_Asset_Type.Transport_Ship_Large.value,
                            Parked_Asset_Type.Transport_Ship_Medium.value,
                            Parked_Asset_Type.Transport_Ship_Small.value,
                            SEA_MILITARY_CRAFT_ASSET.keys()                        
                        ],
    #'SAM':                 [   Ground_Vehicle_Asset_Type.SAM_MEDIUM.value,
    #                           Ground_Vehicle_Asset_Type.SAM_SMALL.value,
    #                           Ground_Vehicle_Asset_Type.SAM_BIG.value,
    #                           Ground_Vehicle_Asset_Type.AAA.value,
    #                           Ground_Vehicle_Asset_Type.EWR.value
    #                       ],
    tc.AIRCRAFT.value:     [   Air_Asset_Type.FIGHTER.value, # for air to air targeting
                                Air_Asset_Type.ATTACKER.value,
                                Air_Asset_Type.BOMBER.value,
                                Air_Asset_Type.AWACS.value,
                                Air_Asset_Type.FIGHTER_BOMBER.value,
                                Air_Asset_Type.HEAVY_BOMBER.value,
                                Air_Asset_Type.BOMBER.value,
                                Air_Asset_Type.HELICOPTER.value,
                                Air_Asset_Type.RECON.value,
                                Air_Asset_Type.TRANSPORT.value
                            ],
    tc.GENERIC.value:   [   BLOCK_INFRASTRUCTURE_ASSET['Military']['Stronghold'].keys()], # solo per gestire eventuali target sconosciuti
}


BLOCK_ASSET_CATEGORY = {
    'Block_Infrastructure_Asset': {},
    'Ground_Military_Vehicle_Asset': {},
    'Air_Defense_Asset': {},
    'Naval_Military_Craft_Asset': {},
    'AIR_MILITARY_CRAFT_ASSET': {}
}



################################## Methods ######################################################

# SBAGLIATA ******************
def get_target_classification(asset_type: str) -> str:
    """ Returns target_class of asset_type ( from TARGET_CLASSIFICATION )

    Args:
        asset_type (str): asset type ( Parked_Asset_Type.Truck.value, 'Tank')

    Returns:
        str: target classification (Aircraft, Airbase, ...)


        NON VA BENE IN QUANTO PER TARGET COMPLESSI (AIRBASE, PORT) I SINGOLI COMPONENTI NON HANNO NOME UNIVOCO_ Hangar è presente sia in Farp, Airbase Helibase ecc.

    """

    for target_classification, target_list in TARGET_CLASSIFICATION:

        for target_type in target_list:

            if asset_type == target_type:
                return target_classification
            
    return None

# SBAGLIATA ******************
def get_block_class_and_asset_category(asset_type: str) -> str:

    """_summary_

    Returns:
        _type_: _description_


    NON VA BENE IN QUANTO PER BLOCCHI COMPLESSI (AIRBASE, PORT) I SINGOLI COMPONENTI NON HANNO NOME UNIVOCO_ Hangar è presente sia in Farp, Airbase Helibase ecc.

    """

    for block_class, block_componets in BLOCK_INFRASTRUCTURE_ASSET:

        for asset_category, asset_items in block_componets:

            if asset_category == asset_type:
                return block_class, asset_category
            
    return None


def get_block_infrastructure_components(block_class: str, asset_category: str) -> List:
    """Returns name list of blocks components ( from BLOCK_INFRASTRUCTURE_ASSET )

    Args:
        block_class (str): class name of block (Transport, Production, Military, ....)
        asset_category (str): category name of blocks component (Road, Farm, Farp)    

    Returns:
        List: name list of blocks components
    """
    if block_class not in BLOCK_INFRASTRUCTURE_ASSET.keys():
        return None
        #raise ValueError(f"unknow block_class: {block_class}")
    
    if asset_category not in BLOCK_INFRASTRUCTURE_ASSET[block_class].keys():
        return None
        #raise ValueError(f"unknow asset_category: {asset_category}")
    
    block_asset_components = []

    for asset_type, asset_value in BLOCK_INFRASTRUCTURE_ASSET[block_class][asset_category].items():
        block_asset_components.append(asset_type)

    return block_asset_components



# DEPRECATED (prima vedi di sostituire BLOCK_ASSET_CATEGORY)


# Generate AIR DEFENSE ASSET CATEGORY AND SUB CATEGORY(ASSET TYPE)
k = 'Block_Infrastructure_Asset'

for k1, v1 in BLOCK_INFRASTRUCTURE_ASSET.items():
    BLOCK_ASSET_CATEGORY[k][k1] = {} # Block Class

    for k2, v2 in v1.items():
        BLOCK_ASSET_CATEGORY[k][k1][k2] = {}  # asset Category       
        
        for k3, v3 in v2.items():
            BLOCK_ASSET_CATEGORY[k][k1][k2][k3] = k3 # asset type 

# Generate GROUND_MILITARY_VEHICLE_ASSET (ASSET TYPE)
k = 'Ground_Military_Vehicle_Asset'

for k1, v1 in GROUND_MILITARY_VEHICLE_ASSET.items():
    BLOCK_ASSET_CATEGORY[k][k1] = {} # asset Category

    for k2, v2 in v1.items():
        BLOCK_ASSET_CATEGORY[k][k1][k2] = k2  # asset type
        
        

 #Generate AIR DEFENSE ASSET CATEGORY AND SUB CATEGORY(ASSET TYPE)
k = 'Air_Defense_Asset'

for k1, v1 in AIR_DEFENSE_ASSET.items():

    for k2, v2 in v1.items():

        if k1 != k2:
            cat = k1 + '_' + k2
            
        else:
            cat = k1        
        BLOCK_ASSET_CATEGORY[k][cat] = {} #asset Category

        for k3, v3 in v2.items():            
            BLOCK_ASSET_CATEGORY[k][cat][k3] = k3 # asset typShipe


# Generate AIR_MILITARY_CRAFT_ASSET
k = 'AIR_MILITARY_CRAFT_ASSET'
#BLOCK_ASSET_CATEGORY[k] = {}

for k1, v1 in AIR_MILITARY_CRAFT_ASSET.items():
    BLOCK_ASSET_CATEGORY[k][k1] = k1  # asset type
    


# Generate SEA_MILITARY_CRAFT_ASSET
k = 'Naval_Military_Craft_Asset'
BLOCK_ASSET_CATEGORY[k] = {}

for k1, v1 in SEA_MILITARY_CRAFT_ASSET.items():
    BLOCK_ASSET_CATEGORY[k][k1] = k1  # asset type


# verifica 
if DEBUG:
    
    for k, v in BLOCK_ASSET_CATEGORY.items():

        print(f'k: {k}\n:')
        
        for k1, v1 in v.items():

            if k in ['AIR_MILITARY_CRAFT_ASSET', 'Naval_Military_Craft_Asset']:
                print(f'BLOCK_ASSET_CATEGORY[{k}][{k1}] = {BLOCK_ASSET_CATEGORY[k][k1]}') # asset type 
            
            else:

                for k2, v2 in v1.items():

                    if k in ['Air_Defense_Asset', 'Ground_Military_Vehicle_Asset']:
                        print(f'BLOCK_ASSET_CATEGORY[{k}][{k1}][{k2}] = {BLOCK_ASSET_CATEGORY[k][k1][k2]}') # asset type 

                    else:
                                    
                        for k3, v3 in v2.items():
                            print(f'BLOCK_ASSET_CATEGORY[{k}][{k1}][{k2}][{k3}] = {BLOCK_ASSET_CATEGORY[k][k1][k2][k3]}') # asset type 

