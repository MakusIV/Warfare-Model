"""
 MODULE Strategical_Evaluation
 
 Data and methods for strategical evaluation. Used by Lead Command & Control

"""

#from typing import Literal
#VARIABLE = Literal["A", "B, "C"]

from Code.Utility import get_membership_label
import Context
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np



def get_Tactical_Report():
    """ request report to any Mil_Base"""
    """ scorre elenco Mil_Base:
            aggiunge alla lista di report il report corrente. La lista è ordinata per criticità"""
    pass

def evaluate_Tactical_Report(report_list):
    """Evaluate priority of tactical reports and resource request. List ordered by priority."""
    # High probaility of attack (our asset is very weak respect wenemy force)
    # asset is very important 

    pass

def evaluate_Defence_Priority_Zone(infrastructure_list):
    """ Evaluate priority of strategic zone (Production Zone, Transport Line, Storage Zone ecc, Mil_Base) and resource request. List ordered by priority."""
    # High probaility of attack (our asset is very weak respect wenemy force)
    pass

def evaluate_Resource_Request(report):
    pass

def evaluate_Target_Priority(target_list):
    """Evaluate priority of targets and resource request. List ordered by priority """
    pass


def evaluate_ground_tactical_action(ground_superiority, fight_load_ratio, dynamic_increment, combat_load_sustainability): 

    # realizzare un test che visualizzi una tabella con tutte le combinazioni gs, flr, dyn_inc e cls per verificare la coerenza e inserire nuove regole oppure eliminare eventuali sbagliate

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

    output_string = get_membership_label(output_numeric, action)

    return output_string, output_numeric