"""
 MODULE Context
 
 Elenco delle variabili di contesto

"""

from typing import Literal

MAX_WORLD_DISTANCE = 1.2e+90
STATE: Literal["Active", "Inactive", "Standby", "Destroyed"]
SHAPE3D: Literal["Cylinder", "Cube", "Sphere", "SemiSphere", "Cone", "Trunc_Cone", "Prism", "Solid"]
SHAPE2D: Literal["Circle", "Square", "Hexagon"]
VALUE: Literal["Critical", "Very_High", "High", "Medium", "Low", "Very_Low"]
CATEGORY: Literal["Goods", "Energy", "Goods & Energy"]
MIL_CATEGORY: Literal["Airbase", "Port", "Stronghold", "Farp", "Regiment", "Battallion", "Brigade", "Company", "EWR"]
COUNTRY: Literal["Germany", "France", "Britain", "USA", "Russia", "China", "India", "Japan", "Korea", "Georgia", "Turkey", "Greece", "Vietnam", "Australia", "Brazil", "Canada"]
SKILL: Literal["Average", "Good", "High", "Excellent"]
TASK: Literal["CAS", "PATROL"]

AREA_FOR_VOLUME = {  
    SHAPE2D.Circle : {SHAPE3D.Cylinder, SHAPE3D.Sphere, SHAPE3D.SemiSphere, SHAPE3D.Cone, SHAPE3D.Trunc_Cone, SHAPE3D.Solid},
    SHAPE2D.Square : {SHAPE3D.Cube},
    SHAPE2D.Hexagon: {SHAPE3D.Prism}
}
    


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

VEHICLE_ASSET = {  #Roccaforte: Brigade, 2 Regiment, 6 Battallion (5 Company)
                    "Tank": {"cost": None, "value": VALUE.Critical, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                    "Armored": {"cost": None, "value": VALUE.Critical, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                    "Motorized": {"cost": None, "value": VALUE.Very_High, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                    "Truck": {"cost": None, "value": VALUE.Medium, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                    "Jeep": {"cost": None, "value": VALUE.Low, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33},
                    "Artillery": {"cost": None, "value": VALUE.High, "t2r":7, "rcp": {"hc": 1, "hs": 4, "hb": 3, "h": None, "g": 1, "e": None}, "payload%": 33}                                    
                },

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



