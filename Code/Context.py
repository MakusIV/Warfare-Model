"""
 MODULE Context
 
 Elenco delle variabili di contesto

"""

#from typing import Literal
#VARIABLE = Literal["A", "B, "C"]
from enum import Enum

MAX_WORLD_DISTANCE = 1.2e+90
DCS_DATA_DIRECTORY = "E:\Sviluppo\Warfare_Model\Code\Persistence\DCS_Data" # Directory for DCS table: Lua and Python.  att dcs funziona solo in windows quindi path solo per formato windows


PATH_TYPE = ["onroad", "offroad", "air", "water"]
ROUTE_TYPE = ["ground", "air", "water", "mixed"]

GROUND_ASSET_CATEGORY = {
     
    "Tank": "Tank", 
    "Armor": "Armor", 
    "Motorized": "Motorized", 
    "Artillery_Fix": "Artillery_Fix", 
    "Artillery_Semovent": "Artillery_Semovent",
    "SAM Big": "SAM Big", 
    "SAM Med": "SAM Med",
    "SAM Small": "SAM Small",
    "AAA": "AAA", 
    "EWR": "EWR", 
    "Command_&_Control": "Command_&_Control"
}


AIR_ASSET_CATEGORY = {
     
    "Fighter": "Fighter", 
    "Fighter_Bomber": "Fighter_Bomber", 
    "Attacker": "Attacker", 
    "Bomber": "Bomber", 
    "Heavy_Bomber": "Heavy_Bomber",
    "Awacs": "Awacs", 
    "Recon": "Recon", 
    "Transport": "Transport",
    "Helicopter": "Helicopter"
}

NAVAL_ASSET_CATEGORY = {
     
    "Destroyer": "Destroyer", 
    "Carrier": "Carrier", 
    "Submarine": "Submarine",
    "Transport": "Transport",    
}

STRUCTURE_ASSET_CATEGORY = {
     
    "Bridge": "Bridge", 
    "Hangar": "Hangar",
    "Depot": "Depot",
    "Oil Tank": "Oil Tank",
    "Farm": "Farm",
    "Power Plant": "Power Plant",
    "Station": "Station",
    "Building": "Building",
    "Factory": "Factory",
    "Barrack": "Barrack"
}   

GROUND_ACTION  = {

    "Attack": "Attack",
    "Defence": "Defence",
    "Maintain": "Maintain"
}

AIR_ACTION  = {

    "Escort": "Escort",
    "Sweep": "Sweep",
    "Patrol": "Patrol",
    "Intercept": "Intercept",
    "Strike": "Strike",
    "PinPointStrike": "PinPointStrike",
    "Sead": "Sead",
}


WEIGHT_FORCE_GROUND_ASSET = {

    GROUND_ASSET_CATEGORY["Tank"]: 7,
    GROUND_ASSET_CATEGORY["Armor"]: 5,
    GROUND_ASSET_CATEGORY["Motorized"]: 3,
    GROUND_ASSET_CATEGORY["Artillery_Fix"]: 4,
    GROUND_ASSET_CATEGORY["Artillery_Semovent"]: 7,
}

BLOCK_CATEGORY = {

    "Civilian": "Civilian",
    "Logistic": "Logistic",    
    "Military": "Military",
    "All": "All",
}

BLOCK_CLASS = {

    "Production": "Production",
    "Storage": "Storage",    
    "Transport": "Transport",
    "Mil_Base": "Mil_Base",
    "Urban": "Urban",
    "All": "All",
}

MIL_BASE_CATEGORY = {

    "Ground Base": ("Stronghold",  "Farp", "Regiment", "Battallion", "Company", "Brigade", "Division"),

    "Air Base": {"Airbase", "Heliport"},

    "Naval Base": {"Port", "Shipyard", "Naval Group"},    
    
    "EWR": ("EWR"),   

    "C&C": ("C2", "C4") 
}

GROUND_COMBAT_EFFICACY = {
    GROUND_ACTION["Attack"]: {GROUND_ASSET_CATEGORY["Tank"]: 5, GROUND_ASSET_CATEGORY["Armor"]: 3.5, GROUND_ASSET_CATEGORY["Motorized"]: 2, GROUND_ASSET_CATEGORY["Artillery_Semovent"]: 4, GROUND_ASSET_CATEGORY["Artillery_Fix"]: 3},
    GROUND_ACTION["Defence"]: {GROUND_ASSET_CATEGORY["Tank"]: 4, GROUND_ASSET_CATEGORY["Armor"]: 3.2, GROUND_ASSET_CATEGORY["Motorized"]: 2, GROUND_ASSET_CATEGORY["Artillery_Semovent"]: 3, GROUND_ASSET_CATEGORY["Artillery_Fix"]: 5},
    GROUND_ACTION["Maintain"]: {GROUND_ASSET_CATEGORY["Tank"]: 3, GROUND_ASSET_CATEGORY["Armor"]: 3.7, GROUND_ASSET_CATEGORY["Motorized"]: 4, GROUND_ASSET_CATEGORY["Artillery_Semovent"]: 2, GROUND_ASSET_CATEGORY["Artillery_Fix"]: 3},
    }



STATE = {"Standby": True , "Destroyed": True, "Damaged": True}


AIR_TASK = {
    
    "CAP": "CAP",  
    "Fighter Sweep": "Fighter Sweep"  ,
    "Intercept": "Intercept",
    "Escort": "Escort",
    "Recon": "Recon",
    "CAS": "CAS",
    "Strike": "Strike",
    "Pinpoint Strike": "Pinpoint Strike",
    "SEAD": "SEAD",
} 

AIRCRAFT_TYPE = {# necessario?

    "F-4E": "F-4E",
    "Mig-21": "Mig-21bis",
    "F-14A": "F-14AgM",
    "F-14B": "F-14B4",


}

#[action][asset.type]
AIR_COMBAT_EFFICACY = {
    
    "F-15": {AIR_TASK["CAP"]: 8, AIR_TASK["Fighter Sweep"]: 8, AIR_TASK["Intercept"]: 7, AIR_TASK["Escort"]: 8, AIR_TASK["Recon"]: 5, AIR_TASK["CAS"]: 4, AIR_TASK["Strike"]: 4, AIR_TASK["Pinpoint Strike"]: 4, AIR_TASK["SEAD"]: 2},
    "F-4E": {AIR_TASK["CAP"]: 6, AIR_TASK["Fighter Sweep"]: 6, AIR_TASK["Intercept"]: 6, AIR_TASK["Escort"]: 6, AIR_TASK["Recon"]: 7, AIR_TASK["CAS"]: 8, AIR_TASK["Strike"]: 8, AIR_TASK["Pinpoint Strike"]: 7, AIR_TASK["SEAD"]: 6}

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
    


AIR_DEFENCE_ASSET = {  
    


    "SAM":                  {   "Big": {#Roccaforte: Brigade, 2 Regiment, 6 Battallion (5 Company)
                                    "Command&Control": {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Track_Radar": {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Search_Radar": {"cost": None, "value": VALUE.VERY_HIGH, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Launcher": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Truck": {"cost": None, "value": VALUE.LOW, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Generator": {"cost": None, "value": VALUE.HIGH, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33}                                    
                                },
                                "Medium": {
                                    "Command&Control": {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Track_Radar": {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Search_Radar": {"cost": None, "value": VALUE.VERY_HIGH, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Search&Track_Radar": {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Launcher": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Truck": {"cost": None, "value": VALUE.LOW, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Generator": {"cost": None, "value": VALUE.HIGH, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33}                                    
                                },
                                "Small": {
                                    "SAM": {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},                                    
                                    "Truck": {"cost": None, "value": VALUE.LOW, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},                                    
                                },                                                                                                
                            },
    "EWR":                  {   "EWR": {
                                    "Command&Control": {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},                                    
                                    "Radar": {"cost": None, "value": VALUE.VERY_HIGH, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},                                    
                                    "Truck": {"cost": None, "value": VALUE.LOW, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Generator": {"cost": None, "value": VALUE.HIGH, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33}                                    
                                },                                
                            },

    "AAA":                  {   "AAA": {                                    
                                    "AAA": {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Truck": {"cost": None, "value": VALUE.LOW, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33}                                    
                                },                                
                            },
    
                    
}

VEHICLE_ASSET = {  #Roccaforte: Brigade, 2 Regiment, 6 Battallion (5 Company)
                    "Tank": {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                    "Armored": {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                    "Motorized": {"cost": None, "value": VALUE.VERY_HIGH, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                    "Truck": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                    "Jeep": {"cost": None, "value": VALUE.LOW, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                    "Artillery": {"cost": None, "value": VALUE.HIGH, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33}                                    
                },

BLOCK_ASSET = {  
    
    "Transport":             {  "Road": {
                                    "Bridge": {"cost": None, "value": VALUE.CRITICAL, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Check_Point": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Truck": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },
                                "Railway": {
                                    "Station": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Railway_Interchange": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Train": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },
                                "Port": {
                                    "Port": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Ship_L": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Ship_M": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Ship_B": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },
                                "Airport": {
                                    "Airbase": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Aircraft": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Aircraft_B": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },
                                "Helibase": {
                                    "Helibase": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Helicopter": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Helicopter_B": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },
                                "Electric": {
                                    "Electric_Infrastructure": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },
                                "Fuel_Line": {
                                    "Gas_Infrastructure": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},                                                                
                                    "Petrol_Infrastructure": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                }
                            },                    

    "Production":           {   "Power_Plant": {
                                    "Power_Plant": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Oil_Tank": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Depot": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Building": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },
                                "Factory": {
                                    "Factories": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Oil_Tank": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Depot": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Building": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },
                                "Farm": {
                                    "Farm": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Oil_Tank": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Depot": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Building": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },                                                                                                
                            },

    "Urban":               {   "Administrative": {
                                    "Administrative_Infrastructure": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},                                    
                                    "Building": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },
                                "Civilian": {                                    
                                    "Building": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },
                                "Service": {
                                    "Energy_Infrastructure": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Service_Infrastructure": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Oil_Tank": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Depot": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Building": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },                                                                                                                            
                            },

    "Storage":               {   "Administrative": {
                                    "Administrative_Infrastructure": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},                                    
                                    "Building": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },                                
                                "Service": {
                                    "Energy_Infrastructure": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},                                    
                                    "Oil_Tank": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Depot": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Building": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },                                                                                                                            
                            },

    "Military_Base":        {   "Stronghold": {#Roccaforte: Brigade, 2 Regiment, 6 Battallion (5 Company)
                                    "Command&Control": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Barrack": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Hangar": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Tank_Vehicle": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Armored_Vehicle": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Motorized_Vehicle": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "SAM_Big": AIR_DEFENCE_ASSET["SAM"]["Big"],
                                    "SAM_Medium": AIR_DEFENCE_ASSET["SAM"]["Medium"],
                                    "SAM_Small": AIR_DEFENCE_ASSET["SAM"]["Small"],
                                    "AAA": AIR_DEFENCE_ASSET["AAA"]["AAA"]                                                                        
                                },
                                "Farp": {
                                    "Factories": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Oil_Tank": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Depot": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Building": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },
                                "Airbase": {
                                    "Farm": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Oil_Tank": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Depot": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Building": {"cost": None, "value": VALUE.MEDIUM, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },                                                                                                
                            },

                    
}



