"""
 MODULE Tactical_Evaluation
 
 Data and methods for tactical evaluation. Used by Military

"""

#from typing import Literal
#VARIABLE = Literal["A", "B, "C"]

import sys
import os
from Code.Dynamic_War_Manager.Source.Utility.Utility import get_membership_label
import random
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np
from Code.Dynamic_War_Manager.Source.Context.Context import BLOCK_ASSET_CATEGORY, GROUND_ACTION, GROUND_COMBAT_EFFICACY
from Code.Dynamic_War_Manager.Source.DataType.Waypoint import Waypoint
from Code.Dynamic_War_Manager.Source.DataType.Edge import Edge
from Code.Dynamic_War_Manager.Source.DataType.Route import Route

print("\nPYTHONPATH during execution:")
print("\n".join(sys.path))



#from __future__ import annotations
#from typing import TYPE_CHECKING
#if TYPE_CHECKING:
    #from Dynamic_War_Manager.Source.Military import Military


LOW_LIMIT_DAMAGE = 0.35 # limite minimo sotto il quale le valutazioni di calcFihtResult() restituiscono 1 (parity)ù
DELTA_PERC_LIMIT = 0.05 # variazione percentuale casuale applicata ai limiti per il calcolo del damage (min_perc_en, min_perc_fr, max_perc_en, max_perc_fr)

def evaluateGroundTacticalAction(ground_superiority, fight_load_ratio, dynamic_increment, combat_load_sustainability): 
    """
    Evaluate and determine the best tactical action based on input parameters.

    This function uses fuzzy logic to assess the ground superiority, fight load ratio, 
    dynamic increment, and combat load sustainability to determine the most suitable 
    tactical action. The output is a string label and a numeric value representing the 
    suggested action.

    Parameters:
    ground_superiority (float): Ratio of friendly ground force effectiveness to enemy ground force. 
                                Values > 1 indicate an advantage.
    fight_load_ratio (float):   Ratio of combat losses to enemy losses. Values < 1 indicate an advantage.
    dynamic_increment (float):  Ratio of fight load ratio to its mean. Values >> 1 indicate a combat success increment.
    combat_load_sustainability (float): Ratio of stored and produced assets to enemy's 
                                        corresponding values. Values > 1 indicate an advantage.

    Returns:
    tuple: A string indicating the suggested action ('RETRAIT', 'DEFENSE', 'MAINTAIN', 'ATTACK') 
           and a numeric value representing the action's strength.
    """

    # realizzare un test che visualizzi una tabella con tutte le combinazioni gs, flr, dyn_inc e cls per verificare la coerenza e inserire nuove regole oppure eliminare eventuali sbagliate

    # Variabili di input
    # gs = gf / gf_enemy;  gf = Tank*kt + Armor*ka + Motorized*km + Artillery*kar / (kt + ka + km + kar); gs > 1 vantaggio
    # flr = co / co_enemy; co = loss_asset or flt = media(co)/media(co_enemy) if sco = dev_std (co) <<; flr < 1 vantaggio
    # dyn_inc = flr / media(flr); dyn_inc >> 1 combat success increment 
    # cls = ( asset_stored + asset_production - co ) / ( enemy_asset_stored + enemy_asset_production + enemy_co ) or ( asset_stored + media(asset_production) - media(co) ) / ( enemy_asset_stored + media(enemy_asset_production) + media(enemy_co) ) if dev_std (co) and dev_std (co_enemy)<< 1; cls > 1 vantaggio
    

    gs = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'gs')  # gs = gf / gf_enemy;  gf = Tank*kt + Armor*ka + Motorized*km + Artillery*kar / (kt + ka + km + kar); gs > 1 vantaggio
    flr = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'flr')  # flr = co / co_enemy; co = loss_asset or flt = media(co)/media(co_enemy) if sco = dev_std (co) <<; flr < 1 vantaggio
    dyn_inc = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'dyn_inc')  # dyn_inc = flr / media(flr); dyn_inc >> 1 combat success increment 
    cls = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'cls')  # cls = ( asset_stored + asset_production - co ) / ( enemy_asset_stored + enemy_asset_production + enemy_co ) or ( asset_stored + media(asset_production) - media(co) ) / ( enemy_asset_stored + media(enemy_asset_production) + media(enemy_co) ) if dev_std (co) and dev_std (co_enemy)<< 1; cls > 1 vantaggio
    

    # Variabile di output
    action = ctrl.Consequent(np.arange(0, 1.01, 0.01), 'action')  # action Valori continui [0, 1]

    # Funzioni di appartenenza
    gs['HI'] = fuzz.trapmf(gs.universe, [0, 0, 1/5, 1/2.7])
    gs['MI'] = fuzz.trapmf(gs.universe, [1/3, 1/2.7, 1/2, 0.95])
    gs['EQ'] = fuzz.trapmf(gs.universe, [0.9, 0.95, 1.05, 1.1])
    gs['MS'] = fuzz.trapmf(gs.universe, [1.05, 2, 2.7, 3])
    gs['HS'] = fuzz.trapmf(gs.universe, [2.7, 5, 10, 10])

    flr['HS'] = fuzz.trapmf(flr.universe, [0, 0, 1/5, 1/3])
    flr['MS'] = fuzz.trapmf(flr.universe, [1/5, 1/3, 1/2, 1])
    flr['EQ'] = fuzz.trimf(flr.universe, [1/2, 1, 2])
    flr['MI'] = fuzz.trapmf(flr.universe, [1, 2, 3, 5])
    flr['HI'] = fuzz.trapmf(flr.universe, [3, 5, 10, 10])

    dyn_inc['HS'] = fuzz.trapmf(dyn_inc.universe, [0, 0, 1/5, 1/2.7])
    dyn_inc['MS'] = fuzz.trapmf(dyn_inc.universe, [1/5, 1/3, 1/2, 1])
    dyn_inc['EQ'] = fuzz.trimf(dyn_inc.universe, [1/2, 1, 2])
    dyn_inc['MI'] = fuzz.trapmf(dyn_inc.universe, [1, 2, 3, 5])
    dyn_inc['HI'] = fuzz.trapmf(dyn_inc.universe, [3, 5, 10, 10])

    cls['HI'] = fuzz.trapmf(cls.universe, [0, 0, 1/5, 1/3])
    cls['MI'] = fuzz.trapmf(cls.universe, [1/5, 1/3, 1/2, 1])
    cls['EQ'] = fuzz.trimf(cls.universe, [1/2, 1, 2])
    cls['MS'] = fuzz.trapmf(cls.universe, [1, 2, 3, 5])
    cls['HS'] = fuzz.trapmf(cls.universe, [3, 5, 10, 10])

    action.automf(names=['RETRAIT', 'DEFENSE', 'MAINTAIN', 'ATTACK'])

    # Definizione delle regole
    rules = [
        # RETRAIT
        ctrl.Rule( ( gs['HI'] | gs['MI']) & ( flr['HI'] | flr['MI'] ), action['RETRAIT'] ),
        ctrl.Rule( ( gs['HI'] | gs['MI'] ) & flr['EQ'] & ( dyn_inc['HI'] | dyn_inc['MI'] ), action['RETRAIT'] ),
        ctrl.Rule( ( gs['HI'] | gs['MI'] ) & flr['EQ'] & dyn_inc['EQ'] & ( cls['EQ'] | cls['MI'] | cls['HI'] ), action['RETRAIT'] ),
        ctrl.Rule( ( gs['HI'] | gs['MI'] | gs['EQ'] ) & ( flr['HI'] | flr['MI']) & ( dyn_inc['HI'] | dyn_inc['MI'] ) & ( cls['EQ'] | cls['MI'] | cls['HI'] ), action['RETRAIT'] ),
        # DEFENSE
        ctrl.Rule( (gs['HI'] | gs['MI']) & flr['EQ'] & ( dyn_inc['HS'] | dyn_inc['MS'] ), action['DEFENSE']),
        ctrl.Rule( (gs['HI'] | gs['MI']) & flr['EQ'] & dyn_inc['EQ'] & ( cls['MS'] | cls['HS'] ), action['DEFENSE']),
        ctrl.Rule( gs['EQ'] & ( flr['HI'] | flr['MI']) & ( dyn_inc['HI'] | dyn_inc['MI'] ) & ( cls['MS'] | cls['HS'] ), action['DEFENSE']),
        ctrl.Rule( gs['EQ'] & flr['EQ'] & ( dyn_inc['EQ'] | dyn_inc['HI'] | dyn_inc['MI'] ) & ( cls['MI'] | cls['HI'] ), action['DEFENSE']),
        # MAINTAIN
        ctrl.Rule( (gs['HI'] | gs['MI']) & ( flr['HS'] | flr['MS']), action['MAINTAIN']),
        ctrl.Rule( gs['EQ'] & ( flr['HS'] | flr['MS']) & ( cls['EQ'] ), action['MAINTAIN']),
        ctrl.Rule( gs['EQ'] & flr['EQ'] & ( dyn_inc['HS'] | dyn_inc['MS'] ) & ( cls['EQ'] | cls['MI'] | cls['HI'] ), action['MAINTAIN']),
        ctrl.Rule( gs['EQ'] & ( flr['HI'] | flr['MI']) & ( dyn_inc['EQ'] | dyn_inc['HS'] | dyn_inc['MS'] ) & ( cls['MS'] | cls['HS'] ), action['MAINTAIN']),
        ctrl.Rule( gs['MS'] & ( flr['EQ'] | flr['HS'] | flr['MS']) & ( cls['MI'] | cls['HI'] ), action['MAINTAIN']),
        ctrl.Rule( gs['MS'] & ( flr['HI'] | flr['MI']), action['MAINTAIN']),
        ctrl.Rule( gs['HS'] & ( flr['HI'] | flr['MI']) & ( cls['MI'] | cls['HI'] ), action['MAINTAIN']),
        # ATTACK    
        ctrl.Rule( gs['EQ'] & ( flr['HS'] | flr['MS']) & ( cls['MS'] | cls['HS'] ), action['ATTACK']),
        ctrl.Rule( (gs['HS'] | gs['MS'] | gs['EQ']) & ( flr['HS'] | flr['MS']), action['ATTACK']), # puoi sostituirlo con un not !(gs['HI'] | gs['MI'])
        ctrl.Rule( (gs['HS'] | gs['MS'] | gs['EQ']) & ( flr['EQ'] ) & ( cls['MS'] | cls['HS'] ), action['ATTACK']),
        ctrl.Rule( (gs['HS'] | gs['MS'] | gs['EQ']) & ( flr['EQ'] ) & cls['EQ'] & ( dyn_inc['MS'] | dyn_inc['HS'] ), action['ATTACK']),
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

    output_string = get_membership_label(output_numeric, action)

    return output_string, output_numeric

def calcRecoAccuracy(parameter: str, recon_mission_success_ratio: float, recon_asset_efficiency: float):
    """
    Calculate accuracy of asset recognitions using Fuzzy Logic.
    if parameter == "Number" asset number accuracy is calculated, if "Efficiency" asset efficiency accuracy is calculated.

    input param:     
    recon_mission_success_ratio (rmsr): level of success of recognition mission: 1/3 ok, 1/5 low  - float, 
    recon_asset_efficiency (rae): efficiency of intelligence and recongition asset 0.7 ok, 0.4 low - float, 
    
    return (string): ['L', 'M', 'H', 'VH'], (float): [0, 1] 

    TEST:
    """

    if recon_mission_success_ratio < 0 or recon_asset_efficiency < 0:
        raise ValueError("Input values must be positive.")
        
    if parameter not in ["Number", "Efficiency"]:
        raise ValueError("Parameter must be 'Number' or 'Efficiency'")

    if recon_mission_success_ratio > 1:
        recon_mission_success_ratio = 1

    if recon_asset_efficiency > 1:
        recon_asset_efficiency = 1

    min = 0.5 # max error for asset efficiency calculation is 50%

    if parameter == "Number":
        min = 0.7 # max error for asset number calculation is 30%
    

    # Variabili di input
    rmsr = ctrl.Antecedent(np.arange(0, 1.001, 0.01), 'rmsr')  # rmsr Valori continui [0, 1]
    rae = ctrl.Antecedent(np.arange(0, 1.001, 0.01), 'rae')  # rae Valori continui [0, 1]

    # Variabile di output
    accuracy = ctrl.Consequent(np.arange(min, 1.001, 0.005), 'accuracy')  # accuracy of asset number evaluation  Valori continui [0, 1] max 30% error     

    # Funzioni di appartenenza
    rmsr['L'] = fuzz.trapmf(rmsr.universe, [0, 0, 0.25, 0.3])
    rmsr['M'] = fuzz.trapmf(rmsr.universe, [0.25, 0.35, 0.4, 0.5])
    rmsr['H'] = fuzz.trapmf(rmsr.universe, [0.35, 0.4, 1, 1])
    
    rae['L'] = fuzz.trapmf(rae.universe, [0, 0, 0.25, 0.35])
    rae['M'] = fuzz.trapmf(rae.universe, [0.3, 0.4, 0.5, 0.65])
    rae['H'] = fuzz.trapmf(rae.universe, [0.5, 0.65, 1, 1])
    

    accuracy.automf(names=['L', 'M', 'H', 'MAX'])

    # Definizione delle regole
    rules = [        
        
        ctrl.Rule(rmsr['H'] & rae['H'], accuracy['MAX']),
        ctrl.Rule(rmsr['M'] & rae['H'], accuracy['H']),
        ctrl.Rule(rmsr['L'] & rae['H'], accuracy['M']),

        ctrl.Rule(rmsr['H'] & rae['M'], accuracy['H']),
        ctrl.Rule(rmsr['M'] & rae['M'], accuracy['M']),
        ctrl.Rule(rmsr['L'] & rae['M'], accuracy['L']),

        ctrl.Rule(rmsr['H'] & rae['L'], accuracy['M']),                    
        ctrl.Rule(rmsr['M'] & rae['L'], accuracy['L']),
        ctrl.Rule(rmsr['L'] & rae['L'], accuracy['L']),
    ]


    # Aggiunta delle regole al sistema di controllo
    accuracy_ctrl = ctrl.ControlSystem(rules)
    accuracy_sim = ctrl.ControlSystemSimulation(accuracy_ctrl)

    # Esempio di input e calcolo
    accuracy_sim.input['rmsr'] = recon_mission_success_ratio #0.95
    accuracy_sim.input['rae'] = recon_asset_efficiency #0.9

    # Calcolo dell'output
    accuracy_sim.compute()
    accuracy_value = accuracy_sim.output['accuracy']    
    
    accuracy_string = get_membership_label(accuracy_value, accuracy)

    return accuracy_string, accuracy_value
    #print("Valore numerico di accuracy:", accuracy_value)
    #print("Valore stringa di accuracy:", accuracy_string)

def calcFightResult(n_fr: int, n_en: int, eff_fr: float, eff_en: float) -> float:
    

    """
    Calculate the result of a fight between two forces given the number of forces, number of enemy, efficiency of forces and efficiency of enemy.
    Use: for ground virtual mission simulation

    Parameters
    ----------
    n_fr : int 
        Number of forces.
    n_en : int
        Number of enemy.
    eff_fr : float [0:1]
        Efficiency of forces.
    eff_en : float (0:1]
        Efficiency of enemy.

    Returns
    -------
    float
        The result of the fight. The result is a float number between 0 and infinity.
        - 0 means absolute friendly victory (minimal losses).
        - 0.5 means friendly victory.
        - 1 means parity (equal losses).
        - 2 means enemy victory.
        - From 10 to infinity means absolute enemy victory (minimal losses).

    Raises
    ------
    ValueError
        If n_fr or n_en are not positive integer numbers or if eff_en or eff_fr are not positive float numbers.

    """
    if not isinstance(n_fr, int) or n_fr <= 0:
        raise ValueError("n_fr: {0} must be an integer number greater of 0".format(n_fr))
    
    if not isinstance(n_en, int) or n_en <= 0:
        raise ValueError("n_en: {0} must be an integer number greater of 0".format(n_en))
    
    if not isinstance(eff_en, float) or not isinstance(eff_fr, float) or eff_en < 0 or eff_fr < 0:
        raise ValueError("eff_en: {0}, eff_er: {1} must be positive float number".format(eff_en, eff_fr))

    num_ratio = n_fr / n_en
    eff_ratio = ( eff_fr  + 0.0001 )/ ( eff_en  + 0.0001 )

    if num_ratio > 0.98 and num_ratio < 1.02 and eff_ratio > 0.98 and eff_ratio < 1.02:
        return 1 # parity

    k_ratio = ( [ 4, 10, 0.2 ], [ 3, 1.9, 0.5 ], [ 2, 1.5, 0.66 ], [ 1, 1, 1 ] )

    if num_ratio > 4: 
        k_fr = 10
        k_en = 0.2
    
    elif num_ratio < 0.25: 
        k_fr = 0.2
        k_en = 10
        
    else:
        i = 0

        while i < len(k_ratio):
            
            if num_ratio == k_ratio[i][0]:
                k_fr = k_ratio[i][1]
                k_en = k_ratio[i][2]
                break
            
            if num_ratio < k_ratio[i][0] and num_ratio > k_ratio[i+1][0]:
                k_fr = k_ratio[i][1] + (num_ratio - k_ratio[i][0]) * (k_ratio[i+1][1] - k_ratio[i][1]) / (k_ratio[i+1][0] - k_ratio[i][0])
                k_en = k_ratio[i][2] + (num_ratio - k_ratio[i][0]) * (k_ratio[i+1][2] - k_ratio[i][2]) / (k_ratio[i+1][0] - k_ratio[i][0])
                break

            if num_ratio > ( 1 / k_ratio[i][0] ) and num_ratio < ( 1 / k_ratio[i+1][0] ):
                k_fr = k_ratio[i][1] + (num_ratio - k_ratio[i][0]) * (k_ratio[i+1][1] - k_ratio[i][1]) / (k_ratio[i+1][0] - k_ratio[i][0])
                k_en = k_ratio[i][2] + (num_ratio - k_ratio[i][0]) * (k_ratio[i+1][2] - k_ratio[i][2]) / (k_ratio[i+1][0] - k_ratio[i][0])

                break
            i += 1

    min_perc_fr = ( 1 - eff_fr * k_fr ) * random.uniform( 1 - DELTA_PERC_LIMIT, 1 + DELTA_PERC_LIMIT ) # eff_fr = [0:1], k_fr = [0.2:10] --> min_perc_fr = [-9:0]
    max_perc_fr = ( eff_en * k_en ) * random.uniform( 1 - DELTA_PERC_LIMIT, 1 + DELTA_PERC_LIMIT ) #    "       "     "         "    --> max_perc_fr = [0: 10]

    # min_perc_fr, max_per_fr = [0: 1] and min_perc_fr <= max_per_fr
    if min_perc_fr < 0: min_perc_fr = 0 
    if max_perc_fr < 0: max_perc_fr = 0
    if max_perc_fr > 1: max_perc_fr = 1
    if min_perc_fr > 1: min_perc_fr = 1     
    if max_perc_fr < min_perc_fr: max_perc_fr = min_perc_fr
    
    
    min_perc_en = ( 1 - eff_en * k_en) * random.uniform( 1 - DELTA_PERC_LIMIT, 1 + DELTA_PERC_LIMIT )
    max_perc_en = ( eff_fr * k_fr ) * random.uniform( 1 - DELTA_PERC_LIMIT, 1 + DELTA_PERC_LIMIT )

    # verifica se è disponibile una funzione che limita tra 0 ed 1 i valori di una variabile, verifica anche se ne esiste una anche che normalizza (es: sigmoide) e che consente di definire le cifre decimali
    if min_perc_en < 0: min_perc_en = 0
    if min_perc_en > 1: min_perc_en = 1
    if max_perc_en > 1: max_perc_en = 1
    if max_perc_en < 0: max_perc_en = 0
    if max_perc_en < min_perc_en: max_perc_en = min_perc_en
    
    damage_fr = random.uniform(min_perc_fr, max_perc_fr)
    damage_en = random.uniform(min_perc_en, max_perc_en)

    if damage_fr < LOW_LIMIT_DAMAGE and damage_en < LOW_LIMIT_DAMAGE: 
        result = 1 # parity
    else:        
        result = damage_fr / damage_en 
        # result = [0:n) 
        # result = [0:0.1] -> absolute friendly victory (minimal losses).
        # result = 0.5     -> friendly victory
        # result = 1       -> parity (equal losses)
        # result = 2       -> enemy victory  
        # result = [10:n] -> absolute enemy victory (minimal losses).

    return result

def evaluateCombatSuperiority(action: str, asset_fr: dict, asset_en: dict) -> float:      
    """
    Evaluate the combat superiority of two forces given the ground assets and the action performed.

    Parameters
    ----------
    action : str
        The action performed. Must be a string included in GROUND_ACTION.
    asset_fr : dict
        The assets of the first force. Must be an dictionary with keys included in GROUND_ASSET_CATEGORY.
    asset_en : dict
        The assets of the second force. Must be an dictionary with keys included in GROUND_ASSET_CATEGORY.
    
    example:

    asset_fr = {
            "Tank": {"num": 20, "combat_power": {"Attack": 0.9, "Defense": 0.9, "Maintain": 0.9}},
            "Armored": {"num": 15, "combat_power": {"Attack": 0.77, "Defense": 0.77, "Maintain": 0.77}},
            ......
        }
        asset_en = {
            "Tank": {"num": 10, "combat_power": {"Attack": 0.7, "Defense": 0.7, "Maintain": 0.7}},
            "Armored": {"num": 5, "combat_power": {"Attack": 0.6, "Defense": 0.6, "Maintain": 0.6}},
            ......       
        }
    
    Returns
    -------
    float
        The combat superiority of the first force. The result is a float number between 0 and 1.
        - 0 means absolute enemy victory (minimal losses).
        - 0.5 means parity (equal losses).
        - 1 means absolute friendly victory (minimal losses).
        
        The combat superiority classes are as follows:
        - VH = ( 0.7 - 1 ]
        - H =  ( 0.55 - 0.7 ]
        - M =  ( 0.45 - 0.55 ]
        - L =  (0.45 - 0.3]
        - VL = (0.3 - 0]

    Raises
    ------
    ValueError
        If action is not a string included in GROUND_ACTION or if asset_fr or asset_en are not dictionaries with keys included in GROUND_ASSET_CATEGORY.

        
    format 
    """
    if not isinstance(asset_fr, dict): 
        raise ValueError("asset_fr: must be an dictionary")
    
    if not all(k in BLOCK_ASSET_CATEGORY["Ground_Military_Vehicle_Asset"].keys() for k in asset_fr):
        raise ValueError("asset_fr.keys must be included in GROUND_ASSET_CATEGORY")

    if not all(isinstance(v, dict) for v in asset_fr.values()):    
        raise ValueError("asset_fr.values must be an dictionary")
    
    if not isinstance(asset_en, dict): 
        raise ValueError("asset_en: must be an dictionary")
    
    if not all(k in BLOCK_ASSET_CATEGORY["Ground_Military_Vehicle_Asset"].keys() for k in asset_en):
        raise ValueError("asset_en.keys must be included in GROUND_ASSET_CATEGORY")

    if not all(isinstance(v, dict) for v in asset_en.values()):    
        raise ValueError("asset_en.values must be an dictionary")    
    
    if not isinstance(action, str) or action not in GROUND_ACTION.keys():
        raise ValueError( "action: {0} {1} must be a string included in GROUND_ACTION".format( action, type(action) ) )  
    
    combat_pow_fr = 0    
    combat_pow_en = 0
    combat_pow_en_alt = 0

    
    for cat in BLOCK_ASSET_CATEGORY["Ground_Military_Vehicle_Asset"].keys():
        
        if action == GROUND_ACTION["Attack"]:            
            #combat_pow_en += GROUND_COMBAT_EFFICACY[GROUND_ACTION["Defense"]][cat] * asset_en[cat]["num"] * asset_en[cat]["efficiency"]
            combat_pow_en += asset_en[cat]["num"] * asset_en[cat]["combat_power"]["Defense"]
            #combat_pow_en_alt += GROUND_COMBAT_EFFICACY[GROUND_ACTION["Maintain"]][cat] * asset_en[cat]["num"] * asset_en[cat]["efficiency"]
            combat_pow_en_alt += asset_en[cat]["num"] * asset_en[cat]["combat_power"]["Maintain"]

        elif action == GROUND_ACTION["Defense"] or action == GROUND_ACTION["Maintain"]:
            #combat_pow_en += GROUND_COMBAT_EFFICACY[GROUND_ACTION["Attack"]][cat] * asset_en[cat]["num"] * asset_en[cat]["efficiency"]            
            combat_pow_en += asset_en[cat]["num"] * asset_en[cat]["combat_power"]["Attack"]            

        #combat_pow_fr += GROUND_COMBAT_EFFICACY[action][cat] * asset_fr[cat]["num"] * asset_fr[cat]["efficiency"]
        combat_pow_fr += asset_fr[cat]["num"] * asset_fr[cat]["combat_power"][action]

    if combat_pow_en < combat_pow_en_alt:
        combat_pow_en = combat_pow_en_alt
    
    combat_superiority = combat_pow_fr / ( combat_pow_en + combat_pow_fr )
    return combat_superiority
# da testare
def evaluateCriticalityGroundEnemy(report_base: dict, report_enemy: dict) -> float:   

    """
    Evaluate the criticality of two forces given the ground assets and the action performed.

    Parameters
    ----------
    report_base : dict
        The assets of the first force. Must be an dictionary with keys included in GROUND_ASSET_CATEGORY.
    report_enemy : dict
        The assets of the second force. Must be an dictionary with keys included in GROUND_ASSET_CATEGORY.

    Returns
    -------
    float
        The criticality of the first force. The result is a float number between 0 and 100.
        - 0 means absolute enemy victory (minimal losses).
        - 100 means absolute friendly victory (minimal losses).

    Raises
    ------
    ValueError
        If action is not a string included in GROUND_ACTION or if asset_fr or asset_en are not dictionaries with keys included in GROUND_ASSET_CATEGORY.

    """

    #devi estrarre dai report asset_fr e asset_enmy
    # devi classificare

    attack_superiority = evaluateCombatSuperiority(GROUND_ACTION["Attack"], report_base, report_enemy)
    defense_superiority = evaluateCombatSuperiority(GROUND_ACTION["Defense"], report_base, report_enemy)
    maintain_superiority = evaluateCombatSuperiority(GROUND_ACTION["Maintain"], report_base, report_enemy)

    criticality = { "action": None, "value": 0 }
        

    if attack_superiority > 0.55:
        criticality["action"] = "attack"
        criticality[ "value" ] = int (attack_superiority * 100 )        

    elif maintain_superiority > 0.45 and maintain_superiority > defense_superiority:
        criticality["action"] = "maintain"
        criticality[ "value" ] = int ( maintain_superiority * 100 )
        
    elif defense_superiority > 0.40:
        criticality["action"] = "Defense"
        criticality[ "value" ] = int ( defense_superiority * 100 )
    
    else:
        criticality["action"] = "retrait"
        criticality[ "value" ] = int ( defense_superiority * 100 )
    
    return criticality

    
    def evaluateCriticalityAirdefense(report_base: dict, report_enemy: dict) -> float: 

        # evaluate enemy air Defense for an possible air attack
        pass
    
# da testare    
def evaluateGroundRouteDangerLevel(enemy_bases: list, route: Route, ground_speed: float, tot_time_route: float) -> dict:
    """
    Evaluate the danger level of a ground route based on enemy bases and route characteristics.
    This function calculates the danger level of a ground route based on the enemy bases and the route characteristics.
    It takes into account the air attack, ground attack, and artillery range of the enemy bases along the route.    
    The danger levels are calculated based on the travel time of the route and the efficiency of the enemy bases.
    The function also considers the time it takes for the enemy bases to attack the route and the travel time of the route.
    The function uses the travel time of the route and the efficiency of the enemy bases to calculate the danger levels.
    The function returns a tuple with tree danger values: air attack, ground attack, and artillery.

    Args:
        enemy_bases (list): _list of enemy bases along the route_
        route (Route): _route object containing the waypoints and edges_
        ground_speed (float): _speed of the ground vehicle_
        tot_time_route (float): _total time of the route_

    Returns:
        tuple(float, float, float): _tuple with three danger values: air attack, ground attack, and artillery_
    """    
    # waypoints
    air_danger, ground_intercept_danger, artillery_danger = 0, 0, 0
    n_waypoints = len(route.waypoints)
    i = 0
    route_travel_time = route.travelTime
    danger = dict
    danger = {"air_attack": list, "ground_attack": list, "artillery_range": list}

    for k, v_edge in Route.edges:
        travel_time = v_edge.calcTravelTime()

        for k_base, v_base in enemy_bases:
            attack_time = v_base.time2attack(v_edge) # air base -> flight time, gorund base -> time to intercept
            danger_level = travel_time * v_base.efficiency/ attack_time
            
            if v_base.is_airbase and attack_time < 0.5 * route_travel_time:                    
                danger["air_attack"].append(danger_level)
                
            if v_base.is_groundbase and attack_time < 0.7 * route_travel_time:
                danger["ground_attack"].append(danger_level)                
                artilleryInRange, in_range_level = v_base.artilleryInRange(v_edge)

                if artilleryInRange:
                    danger["artillery_range"].append(in_range_level)                    

    danger_level_air_attack = np.mean(danger["air_attack"]) * max(danger["air_attack"])# mean * max:  (2, 0.1, 0.2) -> 0.8 * 2 =1.6,  (0.8, 0.8, 0.8) -> 0.8 * 0.8 = 0.64
    danger_level_ground_attack = np.mean(danger["ground_attack"]) * max(danger["ground_attack"])
    danger_level_artillery_range = np.mean(danger["artillery_range"]) * max(danger["artillery_range"])

    return danger_level_air_attack, danger_level_ground_attack, danger_level_artillery_range
                    



    



