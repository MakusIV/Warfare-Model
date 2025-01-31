"""
 MODULE Context
 
 Elenco delle variabili di contesto

"""

#from typing import Literal
#VARIABLE = Literal["A", "B, "C"]
from enum import Enum

MAX_WORLD_DISTANCE = 1.2e+90
DCS_DATA_DIRECTORY = "E:\Sviluppo\Warfare_Model\Code\Persistence\DCS_Data" # Directory for DCS table: Lua and Python.  att dcs funziona solo in windows quindi path solo per formato windows



rules = [
        ctrl.Rule( (GS['HS'] | GS['MS']) & p_e['VH'], t_p_p['VH']),
        ctrl.Rule(t_p['VH'] & p_e['H'], t_p_p['VH']),
        ctrl.Rule(t_p['VH'] & p_e['M'], t_p_p['H']),
        ctrl.Rule(t_p['VH'] & p_e['L'], t_p_p['M']),
        ctrl.Rule(t_p['H'] & p_e['VH'], t_p_p['VH']),
        ctrl.Rule(t_p['H'] & p_e['H'], t_p_p['H']),
        ctrl.Rule(t_p['H'] & p_e['M'], t_p_p['M']),
        ctrl.Rule(t_p['H'] & p_e['L'], t_p_p['M']),
        ctrl.Rule(t_p['M'] & p_e['VH'], t_p_p['H']),
        ctrl.Rule(t_p['M'] & p_e['H'], t_p_p['M']),
        ctrl.Rule(t_p['M'] & p_e['M'], t_p_p['M']),
        ctrl.Rule(t_p['M'] & p_e['L'], t_p_p['L']),
        ctrl.Rule(t_p['L'] & p_e['VH'], t_p_p['M']),
        ctrl.Rule(t_p['L'] & p_e['H'], t_p_p['M']),
        ctrl.Rule(t_p['L'] & p_e['M'], t_p_p['L']),
        ctrl.Rule(t_p['L'] & p_e['L'], t_p_p['L']),        
    ]




AIR_DEFENCE_ASSET = {  
    


    "RETRAIT":                  {1:   {"GS": ("HI", "MI"), { 
                                            {"FLR": ("HI", "MI")}, {"FLR": "EQ", "DYN_INC": ("HI", "MI")}}},
                                 2:   {"GS": "EQ", "FLR": ("HI", "MI")},
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



