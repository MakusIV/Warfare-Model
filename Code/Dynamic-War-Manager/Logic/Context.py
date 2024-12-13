"""
 MODULE Context
 
 Elenco delle variabili di contesto

"""
from enum import Enum

class STATE(Enum):
    Active = 1
    Inactive = 2
    Standby = 3
    Destroyed = 4
    
class SHAPE3D(Enum):
    Cylinder = 1
    Cube = 2
    Sphere = 3
    SemiSphere = 4
    Pyramid = 5
    Cone = 6
    Trunc_Cone = 7

class SHAPE2D(Enum):
    Circonference = 1
    Square = 2
    Hexagon = 3

class VALUE(Enum):
    Critical = 1
    Very_High = 2
    High = 3
    Medium = 4
    Low = 5
    Very_Low = 6
    


AIR_DEFENCE_ASSET = {  
    


    "SAM":                  {   "Big": {#Roccaforte: Brigade, 2 Regiment, 6 Battallion (5 Company)
                                    "Command&Control": {"cost": None, "value": VALUE.Critical, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Track_Radar": {"cost": None, "value": VALUE.Critical, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Search_Radar": {"cost": None, "value": VALUE.Very_High, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Launcher": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Truck": {"cost": None, "value": VALUE.Low, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Generator": {"cost": None, "value": VALUE.High, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33}                                    
                                },
                                "Medium": {
                                    "Command&Control": {"cost": None, "value": VALUE.Critical, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Track_Radar": {"cost": None, "value": VALUE.Critical, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Search_Radar": {"cost": None, "value": VALUE.Very_High, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Search&Track_Radar": {"cost": None, "value": VALUE.Critical, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Launcher": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Truck": {"cost": None, "value": VALUE.Low, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Generator": {"cost": None, "value": VALUE.High, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33}                                    
                                },
                                "Small": {
                                    "SAM": {"cost": None, "value": VALUE.Critical, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},                                    
                                    "Truck": {"cost": None, "value": VALUE.Low, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},                                    
                                },                                                                                                
                            },
    "EWR":                  {   "EWR": {
                                    "Command&Control": {"cost": None, "value": VALUE.Critical, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},                                    
                                    "Radar": {"cost": None, "value": VALUE.Very_High, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},                                    
                                    "Truck": {"cost": None, "value": VALUE.Low, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Generator": {"cost": None, "value": VALUE.High, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33}                                    
                                },                                
                            },

    "AAA":                  {   "AAA": {                                    
                                    "AAA": {"cost": None, "value": VALUE.Critical, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Truck": {"cost": None, "value": VALUE.Low, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33}                                    
                                },                                
                            },
    
                    
}

VEHICLE_ASSET = {  
    


    "Vehicle":               {   "Vehicle": {#Roccaforte: Brigade, 2 Regiment, 6 Battallion (5 Company)
                                    "Tank": {"cost": None, "value": VALUE.Critical, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Armored": {"cost": None, "value": VALUE.Critical, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Motorized": {"cost": None, "value": VALUE.Very_High, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Truck": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Jeep": {"cost": None, "value": VALUE.Low, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Artillery": {"cost": None, "value": VALUE.High, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33}                                    
                                },
                                "M": {
                                    "Command&Control": {"cost": None, "value": VALUE.Critical, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Track_Radar": {"cost": None, "value": VALUE.Critical, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Search_Radar": {"cost": None, "value": VALUE.Very_High, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Search&Track_Radar": {"cost": None, "value": VALUE.Critical, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Launcher": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Truck": {"cost": None, "value": VALUE.Low, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Generator": {"cost": None, "value": VALUE.High, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33}                                    
                                },
                                "Small": {
                                    "SAM": {"cost": None, "value": VALUE.Critical, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},                                    
                                    "Truck": {"cost": None, "value": VALUE.Low, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},                                    
                                },                                                                                                
                            },
    "EWR":                  {   "EWR": {
                                    "Command&Control": {"cost": None, "value": VALUE.Critical, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},                                    
                                    "Radar": {"cost": None, "value": VALUE.Very_High, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},                                    
                                    "Truck": {"cost": None, "value": VALUE.Low, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Generator": {"cost": None, "value": VALUE.High, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33}                                    
                                },                                
                            },

    "AAA":                  {   "AAA": {                                    
                                    "AAA": {"cost": None, "value": VALUE.Critical, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Truck": {"cost": None, "value": VALUE.Low, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33}                                    
                                },                                
                            },
    
                    
}



BLOCK_ASSET = {  
    
    "Transport":             {  "Road": {
                                    "Bridge": {"cost": None, "value": VALUE.Critical, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Check_Point": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Truck": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },
                                "Railway": {
                                    "Station": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Railway_Interchange": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Train": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },
                                "Port": {
                                    "Port": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Ship_L": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Ship_M": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Ship_B": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },
                                "Airport": {
                                    "Airbase": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Aircraft": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Aircraft_B": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },
                                "Helibase": {
                                    "Helibase": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Helicopter": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Helicopter_B": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },
                                "Electric": {
                                    "Electric_Infrastructure": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },
                                "Fuel_Line": {
                                    "Gas_Infrastructure": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},                                                                
                                    "Petrol_Infrastructure": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                }
                            },                    

    "Production":           {   "Power_Plant": {
                                    "Power_Plant": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Oil_Tank": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Depot": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Building": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },
                                "Factory": {
                                    "Factories": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Oil_Tank": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Depot": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Building": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },
                                "Farm": {
                                    "Farm": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Oil_Tank": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Depot": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Building": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },                                                                                                
                            },

    "Urban":               {   "Administrative": {
                                    "Administrative_Infrastructure": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},                                    
                                    "Building": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },
                                "Civilian": {                                    
                                    "Building": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },
                                "Service": {
                                    "Energy_Infrastructure": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Service_Infrastructure": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Oil_Tank": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Depot": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Building": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },                                                                                                                            
                            },

    "Storage":               {   "Administrative": {
                                    "Administrative_Infrastructure": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},                                    
                                    "Building": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },                                
                                "Service": {
                                    "Energy_Infrastructure": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},                                    
                                    "Oil_Tank": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Depot": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Building": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },                                                                                                                            
                            },

    "Military_Base":        {   "Stronghold": {#Roccaforte: Brigade, 2 Regiment, 6 Battallion (5 Company)
                                    "Command&Control": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Barrack": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Hangar": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Tank_Vehicle": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Armored_Vehicle": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Motorized_Vehicle": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "SAM_Big": AIR_DEFENCE_ASSET.SAM.Big,
                                    "SAM_Medium": AIR_DEFENCE_ASSET.SAM.Medium,
                                    "SAM_Small": AIR_DEFENCE_ASSET.SAM.Small,
                                    "AAA": AIR_DEFENCE_ASSET.AAA.AAA                                                                        
                                },
                                "Farp": {
                                    "Factories": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Oil_Tank": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Depot": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Building": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },
                                "Airbase": {
                                    "Farm": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Oil_Tank": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Depot": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33},
                                    "Building": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 0, "hs": 0, "hb": 6, "h": None, "g": 1, "e": None}, "payload%": 33}
                                },                                                                                                
                            },

                    
}



