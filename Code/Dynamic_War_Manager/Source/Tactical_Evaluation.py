"""
 MODULE Tactical_Evaluation
 
 Data and methods for tactical evaluatione

"""

#from typing import Literal
#VARIABLE = Literal["A", "B, "C"]

import Utility
import Context
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np

MAX_WORLD_DISTANCE = 1.2e+90
DCS_DATA_DIRECTORY = "E:\Sviluppo\Warfare_Model\Code\Persistence\DCS_Data" # Directory for DCS table: Lua and Python.  att dcs funziona solo in windows quindi path solo per formato windows


#deprecated
Tactical_Rules = {  
    # GS: GROUND SUPERIORITY (combat power ratio), FLR: FIGHT LOAD RATIO (losses ratio), DYN_INC: DYNAMIC INCREMENT (variation losses)
    # CLS: COMBAT LOAD SUSTAINABILITY (Sustained fight ratio)
    # HI: High Inferiority (>4), MI: Medium Inferiority (2-4), EQ: Equilibre (0.9-1.1), MS: Medium Superiority (2-4), HS: High Superiority (> 4)

    # NELLA RICERCA APPENA TROVA LE CONDIZIONI SELEZIONA L'AZIONE, PERTANTO I 

    "RETREAT":  {1:   {"GS":  ("HI", "MI"), "FLR": ("HI", "MI") }, 
                 2:   {"GS":  ("HI", "MI"), "FLR": ("EQ"), "DYN_INC": ("HI","MI") }, 
                 3:   {"GS":  ("HI", "MI"), "FLR": ("EQ"), "DYN_INC": ("EQ"), "CLS": ("EQ", "HI", "MI") },   
                 4:   {"GS":  ("EQ"), "FLR": ("HI", "MI"), "DYN_INC": ("HI","MI"), "CLS": ("HI", "MI", "EQ")  },                                                
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
                 }  

}


def evaluate_ground_superiority(asset_force: dict|None, enemy_asset_force: dict|None) -> bool|str: 
    
    # asset_force = {"n_tanks": int, "n_armors": int, "n_motorized": int, "n_artillery": int}
    kt, ka, km, kar = Context.WEIGHT_FORCE_GROUND_ASSET["tank"], Context.WEIGHT_FORCE_GROUND_ASSET["armor"], Context.WEIGHT_FORCE_GROUND_ASSET["motorized"], Context.WEIGHT_FORCE_GROUND_ASSET["artillery"] 
    ground_force = ( asset_force["tanks"]["n_tanks"] * kt + asset_force["armors"]["n_armors"] * ka + asset_force["motorized"]["n_motorized"] * km + asset_force["artillery"]["n_artillery"] * kar ) / (kt + ka + km + kar)
    enemy_ground_force = ( enemy_asset_force["tanks"]["n_tanks"] * kt + enemy_asset_force["armors"]["n_armors"] * ka + enemy_asset_force["motorized"]["n_motorized"] * km + enemy_asset_force["artillery"]["n_artillery"] * kar ) / (kt + ka + km + kar)
    
    try:
        ground_superiority = ground_force / enemy_ground_force
    except ZeroDivisionError: 
        print("division by zero: enemy_ground_force = 0/n tank: {0}, armor: {1}, motorized: {2}, artillery: {3}".format(enemy_asset_force["tanks"]["n_tanks"],  enemy_asset_force["armors"]["n_armors"], enemy_asset_force["motorized"]["n_motorized"], enemy_asset_force["artillery"]["n_artillery"]) )
        return False, "MAINTAIN"

    pass

    return


def evaluate_ground_tactical_action(ground_superiority: float|str, fight_load_ratio: float|str, dynamic_increment: float|str, combat_load_sustainability: float|str) -> bool|str: 


    # Variabili di input
    gs = ctrl.Antecedent(np.arange(0, 1.1, 0.01), 'gs')  # kd = pointDistance2D / threatRadius Valori continui [0, 1]
    flr = ctrl.Antecedent(np.arange(0, 1.1, 0.01), 'flr')  # kd = pointDistance2D / threatRadius Valori continui [0, 1]
    dyn_inc = ctrl.Antecedent(np.arange(0, 1.1, 0.01), 'dyn_inc')  # kd = pointDistance2D / threatRadius Valori continui [0, 1]
    cls = ctrl.Antecedent(np.arange(0, 1.1, 0.01), 'cls')  # kd = pointDistance2D / threatRadius Valori continui [0, 1]

    # Variabile di output
    action = ctrl.Consequent(np.arange(0, 1.1, 0.01), 'action')  # target trasnsport line priority Valori continui [0, 1]

    # Funzioni di appartenenza
    gs['HI'] = fuzz.trapmf(gs.universe, [0, 0, 1/5, 1/2.7])
    gs['MI'] = fuzz.trapmf(gs.universe, [1/3, 1/2.7, 1/2, 0.95])
    gs['EQ'] = fuzz.trapmf(gs.universe, [0.9, 0.95, 1.05, 1.1])
    gs['MS'] = fuzz.trapmf(gs.universe, [1.05, 2, 2.7, 3])
    gs['HS'] = fuzz.trapmf(gs.universe, [2.7, 5, 10, 10])

    flr['HI'] = fuzz.trapmf(flr.universe, [0, 0, 1/5, 1/3])
    flr['MI'] = fuzz.trapmf(flr.universe, [1/5, 1/3, 1/2, 1])
    flr['EQ'] = fuzz.trimf(flr.universe, [1/2, 1, 2])
    flr['MS'] = fuzz.trapmf(flr.universe, [1, 2, 3, 5])
    flr['HS'] = fuzz.trapmf(flr.universe, [3, 5, 10, 10])

    dyn_inc['HI'] = fuzz.trapmf(dyn_inc.universe, [0, 0, 1/5, 1/2.7])
    dyn_inc['MI'] = fuzz.trapmf(dyn_inc.universe, [1/5, 1/3, 1/2, 1])
    dyn_inc['EQ'] = fuzz.trimf(dyn_inc.universe, [1/2, 1, 2])
    dyn_inc['MS'] = fuzz.trapmf(dyn_inc.universe, [1, 2, 3, 5])
    dyn_inc['HS'] = fuzz.trapmf(dyn_inc.universe, [3, 5, 10, 10])

    cls['HI'] = fuzz.trapmf(cls.universe, [0, 0, 1/5, 1/3])
    cls['MI'] = fuzz.trapmf(cls.universe, [1/5, 1/3, 1/2, 1])
    cls['EQ'] = fuzz.trimf(cls.universe, [1/2, 1, 2])
    cls['MS'] = fuzz.trapmf(cls.universe, [1, 2, 3, 5])
    cls['HS'] = fuzz.trapmf(cls.universe, [3, 5, 10, 10])

    action.automf(names=['RETRAIT', 'DEFENCE', 'MAINTAIN', 'ATTACK'])

    # Definizione delle regole
    rules = [
        # RETRAIT
        ctrl.Rule( (gs['HI'] | gs['MI']) & ( flr['HI'] | flr['MI']), action['RETRAIT']),
        ctrl.Rule( (gs['HI'] | gs['MI']) & flr['EQ'] & ( dyn_inc['HI'] | dyn_inc['MI'] ), action['RETRAIT']),
        ctrl.Rule( (gs['HI'] | gs['MI']) & flr['EQ'] & dyn_inc['EQ'] & ( cls['EQ'] | cls['MI'] | cls['HI'] ), action['RETRAIT']),
        ctrl.Rule(  gs['EQ'] & ( flr['HI'] | flr['MI']) & ( dyn_inc['HI'] | dyn_inc['MI'] ) & ( cls['EQ'] | cls['MI'] | cls['HI'] ), action['RETRAIT']),
        # DEFENCE
        ctrl.Rule( (gs['HI'] | gs['MI']) & flr['EQ'] & ( dyn_inc['HS'] | dyn_inc['MS'] ), action['DEFENCE']),
        ctrl.Rule( (gs['HI'] | gs['MI']) & flr['EQ'] & dyn_inc['EQ'] & ( cls['MS'] | cls['HS'] ), action['DEFENCE']),
        ctrl.Rule( gs['EQ'] & ( flr['HI'] | flr['MI']) & ( dyn_inc['HI'] | dyn_inc['MI'] ) & ( cls['MS'] | cls['HS'] ), action['DEFENCE']),
        ctrl.Rule( gs['EQ'] & flr['EQ'] & ( dyn_inc['EQ'] | dyn_inc['HI'] | dyn_inc['MI'] ) & ( cls['MI'] | cls['HI'] ), action['DEFENCE']),
        # MAINTAIN
        ctrl.Rule( (gs['HI'] | gs['MI']) & ( flr['HS'] | flr['MS']), action['MAINTAIN']),
        ctrl.Rule( gs['EQ'] & ( flr['HS'] | flr['MS']) & ( cls['EQ'] | cls['MS'] | cls['HS'] ), action['MAINTAIN']),
        ctrl.Rule( gs['EQ'] & flr['EQ'] & ( dyn_inc['HS'] | dyn_inc['MS'] ) & ( cls['MI'] | cls['HI'] ), action['MAINTAIN']),
        ctrl.Rule( gs['EQ'] & ( flr['HI'] | flr['MI']) & ( dyn_inc['EQ'] | dyn_inc['HS'] | dyn_inc['MS'] ) & ( cls['MS'] | cls['HS'] ), action['MAINTAIN']),
        ctrl.Rule( gs['MS'] & ( flr['EQ'] | flr['HS'] | flr['MS']) & ( cls['MI'] | cls['HI'] ), action['MAINTAIN']),
        ctrl.Rule( gs['MS'] & ( flr['HI'] | flr['MI']), action['MAINTAIN']),
        ctrl.Rule( gs['HS'] & ( flr['HI'] | flr['MI']) & ( cls['MI'] | cls['HI'] ), action['MAINTAIN']),
        # ATTACK
        ctrl.Rule( (gs['MS'] | gs['EQ']) & ( flr['HS'] | flr['MS']), action['ATTACK']),
        ctrl.Rule( (gs['MS'] | gs['EQ']) & flr['EQ'] & ( cls['MS'] | cls['HS'] ), action['ATTACK']),
        ctrl.Rule( gs['HS'] & ( flr['HS'] | flr['MS'] | flr['EQ']), action['ATTACK']),
        ctrl.Rule( gs['HS'] & ( flr['HI'] | flr['MI']) & ( cls['MS'] | cls['HS'] ), action['ATTACK']),
    ]

    # Aggiunta delle regole al sistema di controllo
    action_ctrl = ctrl.ControlSystem(rules)
    action_sim = ctrl.ControlSystemSimulation(action_ctrl)

    
    # Esempio di input e calcolo
    action_sim.input['gs'] = ground_superiority #0.95
    action_sim.input['flr'] = fight_load_ratio #0.9
    action_sim.input['dyn_inc'] = dynamic_increment #0.9
    action_sim.input['cls'] = combat_load_sustainability #0.9

    # Calcolo dell'output
    action_sim.compute()
    output_numeric = action_sim.output['action']

    output_string = Utility.get_membership_label(output_numeric, action)

    return output_string, output_numeric