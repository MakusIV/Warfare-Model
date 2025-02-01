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
    # GS: GROUND SUPERIORITY (combat power ratio), FLR: FIGHT LOAD RATIO (losses ratio), DYN_INC: DYNAMIC INCREMENT (variation losses)
    # CLS: COMBAT LOAD SUSTAINABILITY (Sustained fight ratio)

    # NELLA RICERCA APPENA TROVA LE CONDIZIONI SELEZIONA L'AZIONE, PERTANTO I 

    "RETREAT":  {1:   {"GS":  ("HI", "MI"), "FLR": ("HI", "MI") }, 
                 2:   {"GS":  ("HI", "MI"), "FLR": ("EQ"), "DYN_INC": ("HI","MI") }, 
                 3:   {"GS":  ("HI", "MI"), "FLR": ("EQ"), "DYN_INC": ("EQ"), "CLS": ("EQ", "HI", "MI") },                                                   
                 }, 

    "DEFENCE":  {1:   {"GS":  ("HI", "MI"), "FLR": ("EQ"), "DYN_INC": ("HS","MS") }, 
                 2:   {"GS":  ("HI", "MI"), "FLR": ("EQ"), "DYN_INC": ("EQ"), "CLS": ("HS", "MS") },
                 3:   {"GS":  ("EQ"), "FLR": ("EQ"), "DYN_INC": ("HI","MI", "EQ"), "CLS": ("HI", "MI") },                                                   
                 6:   {"GS":  ("EQ"), "FLR": ("HI", "MI"), "DYN_INC": ("HI","MI"), "CLS": ("HS", "MS")  },                                                   
                 }, 

    "MAINTAIN": {1:   {"GS":  ("HI", "MI"), "FLR": ("HS", "MS") },                                                                                     
                 3:   {"GS":  ("EQ"), "FLR": ("HS","MS"), "CLS": ("HS", "MS", "EQ") },                                                   
                 4:   {"GS":  ("EQ"), "FLR": ("EQ"), "DYN_INC": ("HS","MS"), "CLS": ("HI", "MI")  },                                                                    
                 6:   {"GS":  ("EQ"), "FLR": ("HI", "MI"), "DYN_INC": ("HS","MS", "EQ"), "CLS": ("HS", "MS")  },                                                   
                 7:   {"GS":  ("MS"), "FLR": ("HS", "MS", "EQ"), "CLS": ("HI", "MI")}, 
                 8:   {"GS":  ("MS"), "FLR": ("HI", "MI")}, 
                 9:   {"GS":  ("HS"), "FLR": ("HI", "MI"), "CLS": ("HI", "MI")},
                 }, 

    "ATTACK":   {1:   {"GS":  ("MS", "EQ"), "FLR": ("HS", "MS")},                                   
                 1:   {"GS":  ("MS", "EQ"), "FLR": ("EQ"), "CLS": ("HS", "MS")},                                   
                 4:   {"GS":  ("HS"), "FLR": ("HS", "MS", "EQ")},
                 5:   {"GS":  ("HS"), "FLR": ("HI", "MI"), "CLS": ("HS", "MS")},                                  
                 },  

}
