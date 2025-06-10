"""
 MODULE Context
 
 Elenco delle variabili di contesto

"""

#from typing import Literal
#VARIABLE = Literal["A", "B, "C"]
from enum import Enum

MAX_WORLD_DISTANCE = float('inf')
DCS_DATA_DIRECTORY = "E:\Sviluppo\Warfare_Model\Code\Persistence\DCS_Data" # Directory for DCS table: Lua and Python.  att dcs funziona solo in windows quindi path solo per formato windows
DEBUG = True

PATH_TYPE = ["onroad", "offroad", "air", "water"]
ROUTE_TYPE = ["ground", "air", "water", "mixed"]

# Peso per il calcolo del valore complessivo di una produzione (Resource_Manager.production value)
PRODUCTION_WEIGHT = {
    "goods": 6,
    "energy": 8,
    "hr": 1,
    "hc": 10,
    "hs": 6,
    "hb": 3,
}


GROUND_ACTION  = {

    "Attack":   "Attack",
    "Defence":  "Defence",
    "Maintain": "Maintain",
    "Retrait":  "Retrait" 
}

AIR_TASK = {
    
    "CAP": "CAP",  
    "Fighter_Sweep": "Fighter_Sweep"  ,
    "Intercept": "Intercept",
    "Escort": "Escort",
    "Recon": "Recon",
    "CAS": "CAS",
    "Strike": "Strike",
    "Pinpoint_Strike": "Pinpoint_Strike",
    "SEAD": "SEAD",
} 

NAVAL_TASK  = {

    "Attack":   "Attack",    
    "Retrait":  "Retrait" 
}


BLOCK_CATEGORY = {

    "Civilian": "Civilian",
    "Logistic": "Logistic",    
    "Military": "Military",
    "All":      "All",
}

"""    
Divisione:        Brigate e/o Reggimenti - 10-20k men

Brigata:           2 Reggimenti - 3600 men

Reggimento:  3 Battaglioni -1800 men

Battaglione:   4 Compagnie - 600 men

Compagnia:    150 men
"""


MILITARY_CATEGORY = {

    "Ground_Base": ("Stronghold",  "Farp", "Regiment", "Battallion", "Company", "Brigade", "Division", "Command_&_Control_C2", "Command_&_Control_C4"),

    "Air_Base": ("Airbase", "Heliport"),

    "Naval_Base": ("Port", "Shipyard", "Naval_Group"),     
    
}


# Peso per il calcolo della combat power  in Tactical_Evaluation Module
# dovresti integrare per artillery con il caliro: Artillery_Fix.Howitzer_Big, Artillery_Fix.Howitzer_Small, Artillery_Semovent.Self_Propelled_Big, ........
WEIGHT_FORCE_GROUND_ASSET = {

    "Tank": 7,
    "Armored": 5,
    "Motorized": 3,
    "Artillery_Fixed": 4,
    "Artillery_Semovent": 7,
}

# Parametri per il calcolo della combat power  in Tactical_Evaluation Module
GROUND_COMBAT_EFFICACY = {
    GROUND_ACTION["Attack"]: {"Tank": 5, "Armored": 3.5, "Motorized": 2, "Artillery_Semovent": 4, "Artillery_Fixed": 3},
    GROUND_ACTION["Defence"]: {"Tank": 4, "Armored": 3.2, "Motorized": 2, "Artillery_Semovent": 3, "Artillery_Fixed": 5},
    GROUND_ACTION["Maintain"]: {"Tank": 3, "Armored": 3.7, "Motorized": 4, "Artillery_Semovent": 2, "Artillery_Fixed": 3},    
}

STATE = {"Operational": True, "Not_Operational": True , "Destroyed": True, "Critical": True, "Damaged": True}



AIRCRAFT_TYPE = {# necessario?

    "F-4E": "F-4E",
    "Mig-21": "Mig-21bis",
    "F-14A": "F-14AgM",
    "F-14B": "F-14B4",
}

#[action][asset.type]
AIR_COMBAT_EFFICACY = {
    
    "F-15": {AIR_TASK["CAP"]: 8, AIR_TASK["Fighter_Sweep"]: 8, AIR_TASK["Intercept"]: 7, AIR_TASK["Escort"]: 8, AIR_TASK["Recon"]: 5, AIR_TASK["CAS"]: 4, AIR_TASK["Strike"]: 4, AIR_TASK["Pinpoint_Strike"]: 4, AIR_TASK["SEAD"]: 2},
    "F-4E": {AIR_TASK["CAP"]: 6, AIR_TASK["Fighter_Sweep"]: 6, AIR_TASK["Intercept"]: 6, AIR_TASK["Escort"]: 6, AIR_TASK["Recon"]: 7, AIR_TASK["CAS"]: 8, AIR_TASK["Strike"]: 8, AIR_TASK["Pinpoint_Strike"]: 7, AIR_TASK["SEAD"]: 6}

}


class SHAPE3D(Enum): 
    CYLINDER = "Cylinder" 
    CUBE = "Cube"
    SPHERE = "Sphere"
    SEMISPHERE = "SemiSphere"
    CONE = "Cone"
    TRUNC_CONE = "Trunc_Cone"
    PRISM = "Prism"
    SOLID = "Solid"


class SHAPE2D(Enum): 
    CIRCLE = "Circle"
    SQUARE = "Square"
    HEXAGON = "Hexagon"

class VALUE(Enum): 
    CRITICAL ="Critical"
    VERY_HIGH = "Very_High"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    VERY_LOW = "Very_Low"

class FOOD_CATEGORY(Enum):
    GOODS = "Goods"
    ENERGY = "Energy"
    GOODS_AND_ENERGY = "Goods & Energy"

class COUNTRY(Enum): 
    GERMANY = "Germany"
    FRANCE = "France"
    BRITAIN = "Britain"
    USA = "USA"
    RUSSIA = "Russia"
    CHINA = "China"
    INDIA = "India"
    JAPAN = "Japan"
    KOREA = "Korea"
    GEORGIA = "Georgia"
    TURKEY = "Turkey"
    GREECE = "Greece"
    VIETNAM = "Vietnam"
    AUSTRALIA = "Australia"
    BRAZIL = "Brazil"
    CANADA = "Canada"

class SKILL(Enum): 
    AVERAGE = "Average"
    GOOD = "Good"
    HIGH = "High"
    EXCELLENT = "Excellent"
    

class GROUP_CATEGORY(Enum): 
    HELICOPTER = "helicopter"
    PLANE = "plane"
    VEHICLE = "vehicle"
    STATIC = "static"

SIDE = ["Blue", "Red", "Neutral"]

AREA_FOR_VOLUME = {  
    SHAPE2D.CIRCLE : {SHAPE3D.CYLINDER, SHAPE3D.SPHERE, SHAPE3D.SEMISPHERE, SHAPE3D.CONE, SHAPE3D.TRUNC_CONE, SHAPE3D.SOLID},
    SHAPE2D.SQUARE : {SHAPE3D.CUBE},
    SHAPE2D.HEXAGON : {SHAPE3D.PRISM}
}

# key: asset type
AIR_Military_CRAFT_ASSET = {
    "Fighter":          {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
    "Fighter_Bomber":   {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
    "Attacker":         {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
    "Bomber":           {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
    "Heavy_Bomber":     {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
    "Awacs":            {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
    "Recon":            {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
    "Transport":        {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
    "Helicopter":       {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},  
}

 # Asset:                   STRUCTURE_ASSET_CATEGORY, GROUND_ASSET_CATEGORY, AIR_ASSET_CATEGORY, BLOCK_ASSET, BLOCK_ASSET_CATEGORY
 # Tactical_Evaluation:     GROUND_ASSET_CATEGORY, GROUND_ACTION, GROUND_COMBAT_EFFICACY
 # Strategical_Evaluation:  Military_CATEGORY

#GROUND_ASSET_CATEGORY, AIR_ASSET_CATEGORY, STRUCTURE_ASSET_CATEGORY]
# key1+key2: asset category, key3: asset type
AIR_DEFENCE_ASSET = {  
    
    "SAM":                  {   "Big": {#Roccaforte: Brigade, 2 Regiment, 6 Battallion (5 Company)
                                    "Command_&_Control": {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Track_Radar": {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Search_Radar": {"cost": None, "value": VALUE.VERY_HIGH, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Launcher": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Truck": {"cost": None, "value": VALUE.LOW, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Generator": {"cost": None, "value": VALUE.HIGH, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33}                                    
                                },
                                "Medium": {
                                    "Command_&_Control": {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Track_Radar": {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Search_Radar": {"cost": None, "value": VALUE.VERY_HIGH, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Search_&_Track_Radar": {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Launcher": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Truck": {"cost": None, "value": VALUE.LOW, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Generator": {"cost": None, "value": VALUE.HIGH, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33}                                    
                                },
                                "Small": {
                                    "SAM": {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},                                    
                                    "Truck": {"cost": None, "value": VALUE.LOW, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},                                    
                                },                                                                                                
                                "Manpad": {
                                    "Manpad": {"cost": None, "value": VALUE.CRITICAL, "t2r":1, "rcp": {"hc": 0, "hs": 0, "hb": 1, "hr": None, "goods": 1, "energy": None}, "payload%": 33},                                                                        
                                },                                                                                                
                            },
    "EWR":                  {   "EWR": {
                                    "Command_&_Control": {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},                                    
                                    "Radar": {"cost": None, "value": VALUE.VERY_HIGH, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},                                    
                                    "Truck": {"cost": None, "value": VALUE.LOW, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Generator": {"cost": None, "value": VALUE.HIGH, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33}                                    
                                },                                
                            },

    "AAA":                  {   "AAA": {                                    
                                    "AAA": {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Truck": {"cost": None, "value": VALUE.LOW, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33}                                    
                                },                                
                            },
}    
                    


# Caratteristiche degli asset delle diversè unità Military: Corazzate, Meccanizzate, Motorizzate e Artiglieria
# key1: asset category, key2: asset type
GROUND_Military_VEHICLE_ASSET = {
    # Corazzata 
    "Tank":     {   "Command_&_Control":                {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},     
                    "Tank":                             {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                    "Main_Battle_Tank":                 {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},     
                    "Infantry_Fighting_Vehicle":        {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                    "Scout_&_Recon":                    {"cost": None, "value": VALUE.LOW, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                    "Truck_Supply":                     {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33}},
    # Meccanizzata
    "Armored":    { "Command_&_Control":                {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},     
                    "Armored_Personal_Carrier":         {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                    "Infantry_Fighting_Vehicle":        {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                    "Scout_&_Recon":                    {"cost": None, "value": VALUE.LOW, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                    "Truck_Supply":                     {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},                    
                    "Self_Propelled_ATGM":              {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                    "Self_Propelled_Gun":               {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33}    },
    # Motorizzata
    "Motorized": {  "Command_&_Control":                {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},     
                    "Armored_Personal_Carrier":         {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                    "Infantry_Fighting_Vehicle":        {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                    "Truck_Supply":                     {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},                                        
                    "Scout_&_Recon":                    {"cost": None, "value": VALUE.LOW, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                    "Self_Propelled_ATGM":              {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                    "Self_Propelled_Gun":               {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33} },
    # Artiglieria fissa
    "Artillery_Fixed": {  "Command_&_Control":          {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                    "Howitzer_Big":                     {"cost": None, "value": VALUE.HIGH, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                    "Howitzer_Medium":                  {"cost": None, "value": VALUE.HIGH, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                    "Howitzer_Small":                   {"cost": None, "value": VALUE.HIGH, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                    "Mortar":                           {"cost": None, "value": VALUE.HIGH, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},                    
                    "Truck_Supply":                     {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                    "Scout_&_Recon":                    {"cost": None, "value": VALUE.LOW, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33} },
    # Artiglieria semovent
    "Artillery_Semovent": {  "Command_&_Control":       {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},                    
                    "Mortar":                           {"cost": None, "value": VALUE.HIGH, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                    "Multiple_Rocket_Launcher":         {"cost": None, "value": VALUE.HIGH, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                    "Self_Propelled_Artillery_Big":     {"cost": None, "value": VALUE.HIGH, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                    "Self_Propelled_Artillery_Medium":  {"cost": None, "value": VALUE.HIGH, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                    "Self_Propelled_Artillery_Small":   {"cost": None, "value": VALUE.HIGH, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                    "Truck_Supply":                     {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                    "Scout_&_Recon":                    {"cost": None, "value": VALUE.LOW, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33} }
}

# key: asset type
NAVAL_Military_CRAFT_ASSET = {
     
    "Carrier":          {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},      
    "Destroyer":        {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},     
    "Cruiser":          {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},     
    "Frigate":          {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},     
    "Fast_Attack":      {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},    
    "Submarine":        {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},     
    "Transport":        {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},     
    "Civilian":         {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},     

}


# key1:   Block Class, key2: Asset Category, key 3: Asset type
# INFRASTRUCTURE BLOCK ASSET
BLOCK_INFRASTRUCTURE_ASSET = {  
    
    "Transport":             {  "Road": {
                                    "Bridge": {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Check_Point": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Truck": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33}
                                },
                                "Railway": {
                                    "Station": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Railway_Interchange": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Train": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33}
                                },
                                "Port": {
                                    "Port": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Ship_L": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Ship_M": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Ship_B": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33}
                                },
                                "Airport": {
                                    "Airbase": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Aircraft": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Aircraft_B": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33}
                                },
                                "Helibase": {
                                    "Helibase": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Helicopter": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Helicopter_B": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33}
                                },
                                "Electric": {
                                    "Electric_Infrastructure": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33}
                                },
                                "Fuel_Line": {
                                    "Gas_Infrastructure": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},                                                                
                                    "Petrol_Infrastructure": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                }
                            },                    

    "Production":           {   "Power_Plant": {
                                    "Power_Plant": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Oil_Tank": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Depot": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Building": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33}
                                },
                                "Factory": {
                                    "Factory": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Oil_Tank": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Depot": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Building": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33}
                                },
                                "Farm": {
                                    "Farm": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Oil_Tank": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Depot": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Building": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33}
                                },                                                                                                
                            },

    "Urban":               {   "Administrative": {
                                    "Administrative_Infrastructure": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},                                    
                                    "Building": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33}
                                },
                                "Civilian": {                                    
                                    "Building": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33}
                                },
                                "Service": {
                                    "Energy_Infrastructure": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Service_Infrastructure": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Oil_Tank": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Depot": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Building": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33}
                                },                                                                                                                            
                            },

    "Storage":              {   "Administrative": {
                                    "Administrative_Infrastructure": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},                                    
                                    "Building": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33}
                                },                                
                                "Service": {
                                    "Energy_Infrastructure": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},                                    
                                    "Oil_Tank": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Depot": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Building": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33}
                                },                                                                                                                            
                            },

    "Military":             {   "Stronghold": {#Roccaforte: Brigade, 2 Regiment, 6 Battallion (5 Company)
                                    "Command_&_Control": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Barrack": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Hangar": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Depot": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                                        
                                },
                                "Farp": {
                                    "Command_&_Control": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},                                    
                                    "Oil_Tank": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Depot": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Barrack": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Building": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33}
                                },
                                "Airbase": {
                                    "Command_&_Control": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Hangar": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Oil_Tank": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Depot": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Building": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Barrack": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},                                                                      
                                },
                                 "Port": {
                                    "Command_&_Control": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Hangar": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Oil_Tank": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Depot": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Building": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Barrack": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},                                                                      
                                },
                                "Shipyard": {
                                    "Command_&_Control": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Hangar": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Oil_Tank": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Depot": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Building": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Barrack": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},                                                                      
                                },
                                "Air_Defence": {#Roccaforte: Brigade, 2 Regiment, 6 Battallion (5 Company)
                                    "Command_&_Control": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},
                                    "Barrack": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "hr": None, "goods": 1, "energy": None}, "payload%": 33},                                    
                                    "Depot": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "hr": None, "goods": 1, "energy": None}, "payload%": 33},                                                                                                    
                                },                                                                                                
                            },

                    
}

BLOCK_ASSET_CATEGORY = {
    "Block_Infrastructure_Asset": {},
    "Ground_Military_Vehicle_Asset": {},
    "Air_Defence_Asset_Category": {},
    "Naval_Military_Craft_Asset": {},
    "Air_Military_Craft_Asset": {}
}



# Generate AIR DEFENCE ASSET CATEGORY AND SUB CATEGORY(ASSET TYPE)
k = "Block_Infrastructure_Asset"

for k1, v1 in BLOCK_INFRASTRUCTURE_ASSET.items():
    BLOCK_ASSET_CATEGORY[k][k1] = {} # Block Class

    for k2, v2 in v1.items():
        BLOCK_ASSET_CATEGORY[k][k1][k2] = {}  # asset Category       
        
        for k3, v3 in v2.items():
            BLOCK_ASSET_CATEGORY[k][k1][k2][k3] = k3 # asset type 

# Generate GROUND_Military_VEHICLE_ASSET (ASSET TYPE)
k = "Ground_Military_Vehicle_Asset"

for k1, v1 in GROUND_Military_VEHICLE_ASSET.items():
    BLOCK_ASSET_CATEGORY[k][k1] = {} # asset Category

    for k2, v2 in v1.items():
        BLOCK_ASSET_CATEGORY[k][k1][k2] = k2  # asset type
        
        

 #Generate AIR DEFENCE ASSET CATEGORY AND SUB CATEGORY(ASSET TYPE)
k = "Air_Defence_Asset_Category"

for k1, v1 in AIR_DEFENCE_ASSET.items():

    for k2, v2 in v1.items():

        if k1 != k2:
            cat = k1 + "_" + k2
            
        else:
            cat = k1        
        BLOCK_ASSET_CATEGORY[k][cat] = {} #asset Category

        for k3, v3 in v2.items():            
            BLOCK_ASSET_CATEGORY[k][cat][k3] = k3 # asset type


# Generate AIR_Military_CRAFT_ASSET
k = "Air_Military_Craft_Asset"
#BLOCK_ASSET_CATEGORY[k] = {}

for k1, v1 in AIR_Military_CRAFT_ASSET.items():
    BLOCK_ASSET_CATEGORY[k][k1] = k1  # asset type
    


# Generate NAVAL_Military_CRAFT_ASSET
k = "Naval_Military_Craft_Asset"
BLOCK_ASSET_CATEGORY[k] = {}

for k1, v1 in NAVAL_Military_CRAFT_ASSET.items():
    BLOCK_ASSET_CATEGORY[k][k1] = k1  # asset type


# verifica 
if DEBUG:
    
    for k, v in BLOCK_ASSET_CATEGORY.items():

        print(f"k: {k}\n:")
        
        for k1, v1 in v.items():

            if k in ["Air_Military_Craft_Asset", "Naval_Military_Craft_Asset"]:
                print(f"BLOCK_ASSET_CATEGORY[{k}][{k1}] = {BLOCK_ASSET_CATEGORY[k][k1]}") # asset type 
            
            else:

                for k2, v2 in v1.items():

                    if k in ["Air_Defence_Asset_Category", "Ground_Military_Vehicle_Asset"]:
                        print(f"BLOCK_ASSET_CATEGORY[{k}][{k1}][{k2}] = {BLOCK_ASSET_CATEGORY[k][k1][k2]}") # asset type 

                    else:
                                    
                        for k3, v3 in v2.items():
                            print(f"BLOCK_ASSET_CATEGORY[{k}][{k1}][{k2}][{k3}] = {BLOCK_ASSET_CATEGORY[k][k1][k2][k3]}") # asset type 

