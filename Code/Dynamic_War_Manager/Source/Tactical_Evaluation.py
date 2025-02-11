"""
 MODULE Tactical_Evaluation
 
 Data and methods for tactical evaluation. Used by Mil_Base

"""

#from typing import Literal
#VARIABLE = Literal["A", "B, "C"]

from Utility import get_membership_label
import Context
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np



def evaluate_ground_superiority(asset_force, enemy_asset_force): 
    
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


def evaluate_ground_tactical_action(ground_superiority, fight_load_ratio, dynamic_increment, combat_load_sustainability): 

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
    action = ctrl.Consequent(np.arange(0, 1.1, 0.01), 'action')  # action Valori continui [0, 1]

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

    action.automf(names=['RETRAIT', 'DEFENCE', 'MAINTAIN', 'ATTACK'])

    # Definizione delle regole
    rules = [
        # RETRAIT
        ctrl.Rule( ( gs['HI'] | gs['MI']) & ( flr['HI'] | flr['MI'] ), action['RETRAIT'] ),
        ctrl.Rule( ( gs['HI'] | gs['MI'] ) & flr['EQ'] & ( dyn_inc['HI'] | dyn_inc['MI'] ), action['RETRAIT'] ),
        ctrl.Rule( ( gs['HI'] | gs['MI'] ) & flr['EQ'] & dyn_inc['EQ'] & ( cls['EQ'] | cls['MI'] | cls['HI'] ), action['RETRAIT'] ),
        ctrl.Rule( ( gs['HI'] | gs['MI'] | gs['EQ'] ) & ( flr['HI'] | flr['MI']) & ( dyn_inc['HI'] | dyn_inc['MI'] ) & ( cls['EQ'] | cls['MI'] | cls['HI'] ), action['RETRAIT'] ),
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
        ctrl.Rule( (gs['HS'] | gs['MS'] | gs['EQ']) & ( flr['HS'] | flr['MS']), action['ATTACK']), # puoi sostituirlo con un not !(gs['HI'] | gs['MI'])
        ctrl.Rule( (gs['HS'] | gs['MS'] | gs['EQ']) & ( flr['EQ'] | flr['MS'] | flr['HS'] ) & ( cls['MS'] | cls['HS'] ), action['ATTACK']),
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



def calc_Reco_Accuracy(recon_mission_success_ratio: float, recon_asset_efficiency: float):
    """
    Calculate accuracy of recognitions using Fuzzy Logic

    input param:     
    recon_mission_success_ratio (rmsr): level of success of recognition mission: 1/3 ok, 1/5 low  - float, 
    recon_asset_efficiency (rae): efficiency of intelligence and recongition asset 0.7 ok, 0.4 low - float, 
    
    return (string): ['L', 'M', 'H', 'VH'], (float): [0, 1] 

    TEST:
    """

    if recon_mission_success_ratio <= 0 or recon_asset_efficiency <= 0:
        raise ValueError("Input values must be positive and non-zero.")
        

    # Variabili di input
    rmsr = ctrl.Antecedent(np.arange(0, 1.1, 0.01), 'rmsr')  # rmsr Valori continui [0, 1]
    rae = ctrl.Antecedent(np.arange(0, 1.1, 0.01), 'rae')  # rae Valori continui [0, 1]

    # Variabile di output
    accuracy = ctrl.Consequent(np.arange(0.7, 1.1, 0.005), 'accuracy')  # accuracy of asset number evaluation  Valori continui [0, 1] max 30% error 
    accuracy_eff = ctrl.Consequent(np.arange(0.5, 1.1, 0.005), 'accuracy_eff')  # accuracy of asset efficiency evaluation  Valori continui [0, 1] max 50% errore

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
    accuracy_num_value = accuracy_sim.output['accuracy']
    accuracy_eff_value = accuracy_sim.output['accuracy_eff']
    
    accuracy_num_string = get_membership_label(accuracy_num_value, accuracy)
    accuracy_eff_string = get_membership_label(accuracy_eff_value, accuracy_eff)

    return accuracy_num_string, accuracy_num_value, accuracy_eff_string, accuracy_eff_value
    #print("Valore numerico di accuracy_num:", accuracy_num_value)
    #print("Valore stringa di accuracy_num:", accuracy_num_string)


