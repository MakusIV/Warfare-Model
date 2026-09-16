import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import pandas as pd
import sys
import os
from sympy import Point2D
# Aggiungi il percorso della directory principale del progetto
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from Code.Dynamic_War_Manager.Source.Context.Context import BLOCK_ASSET_CATEGORY, VALUE, GROUND_MILITARY_VEHICLE_ASSET, GROUND_ACTION
from Code.Dynamic_War_Manager.Source.Context import Context
from Code.Dynamic_War_Manager.Source.Context.Context import (
    Ground_Vehicle_Asset_Type as gat,
    Air_Asset_Type as aat,
)
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Block.Military import Military
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import Aircraft_Data
from Code.Dynamic_War_Manager.Source.Logic import Tactical_Analysis
from Code.Dynamic_War_Manager.Source.Logic import Tactical_Evaluation
# Importa il metodo da testare evaluateGroundTacticalAction
from Code.Dynamic_War_Manager.Source.Logic.Tactical_Evaluation import (
    evaluateGroundTacticalAction, calcRecoAccuracy, calcFightResult, evaluateCombatSuperiority,
    target_affinity, select_weight, calculate_priority, calc_surface_priority, calc_air_priority,
)


def _make_combat_power_side_effect(value, task=None):
    """Mimics Military.combat_power's (force, action) contract: float if both `force` and
    `action` given, Dict[task, float] if only `force` given. If `task` is given, only that
    task carries `value` (every other task is 0.0) -- mirrors an asset whose combat power is
    concentrated on a single posture."""
    def _side_effect(force=None, action=None):
        if force and action:
            return value if task is None or action == task else 0.0
        if force:
            return {t: (value if task is None or t == task else 0.0) for t in Context.ACTION_TASKS[force]}
        return {f: {t: value for t in Context.ACTION_TASKS[f]} for f in Context.MILITARY_FORCES}
    return _side_effect

# Lightweight class stubs used only to set mock.__class__ for classification-loop dispatch,
# mirroring Test_Region.py/Test_Military.py -- Vehicle/Ship/Aircraft cannot be imported directly
# because they trigger a pre-existing circular import in the Aircraft->Aircraft_Weapon_Data chain.
_Aircraft = type('Aircraft', (), {})

print("\nPYTHONPATH during execution:")
print("\n".join(sys.path))

class TestEvaluateGroundTacticalAction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Metodo eseguito una volta prima di tutti i test.
        Esegue il codice necessario dal modulo Context.        
        """
        """
        # Caratteristiche degli asset delle diversè unità Military: Corazzate, Meccanizzate, Motorizzate e Artiglieria
        GROUND_MILITARY_VEHICLE_ASSET = {
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
       
        # Esegui il codice necessario dal modulo Context
        BLOCK_ASSET_CATEGORY = {
            "Block_Infrastructure_Asset": {},
            "Ground_Military_Vehicle_Asset": {},
            "Air_defense_Asset_Category": {},
            "Naval_Military_Craft_Asset": {},
            "AIR_MILITARY_CRAFT_ASSET": {}
        }
        """
        """
        # Generate GROUND_MILITARY_VEHICLE_ASSET (ASSET TYPE)
        k = "Ground_Military_Vehicle_Asset"

        for k1, v1 in GROUND_Military_VEHICLE_ASSET.items():
            BLOCK_ASSET_CATEGORY[k][k1] = {} # asset Category

            for k2, v2 in v1.items():
                BLOCK_ASSET_CATEGORY[k][k1][k2] = k2  # asset type
                
                print("Context setup completed.")
        """

    def testCalcRecoNumberAccuracy(self):
        # Test con valori di input validi
        recon_mission_success_ratio = 0.65
        recon_asset_efficiency = 0.70
        expected_result = 0.95  # calcolato manualmente sostituisce con string
        self.assertAlmostEqual(calcRecoAccuracy("Number", recon_mission_success_ratio, recon_asset_efficiency)[1], expected_result, delta=0.03)
        self.assertEqual(calcRecoAccuracy("Number", recon_mission_success_ratio, recon_asset_efficiency)[0], "MAX")

         # Test con valori di input validi
        recon_mission_success_ratio = 0.37
        recon_asset_efficiency = 0.45
        expected_result = 0.83  # calcolato manualmente
        self.assertAlmostEqual(calcRecoAccuracy("Number", recon_mission_success_ratio, recon_asset_efficiency)[1], expected_result, delta=0.03)
        self.assertEqual(calcRecoAccuracy("Number", recon_mission_success_ratio, recon_asset_efficiency)[0], "M")

         # Test con valori di input validi
        recon_mission_success_ratio = 0.2
        recon_asset_efficiency = 0.25
        expected_result = 0.72  # calcolato manualmente
        self.assertAlmostEqual(calcRecoAccuracy("Number", recon_mission_success_ratio, recon_asset_efficiency)[1], expected_result, delta=0.03)
        self.assertEqual(calcRecoAccuracy("Number", recon_mission_success_ratio, recon_asset_efficiency)[0], "L")

        # Test con valori di input estremi
        recon_mission_success_ratio = 0.0
        recon_asset_efficiency = 0.0
        expected_result = 0.73
        self.assertAlmostEqual(calcRecoAccuracy("Number", recon_mission_success_ratio, recon_asset_efficiency)[1], expected_result, delta=0.03)
        self.assertEqual(calcRecoAccuracy("Number", recon_mission_success_ratio, recon_asset_efficiency)[0], "L")

        recon_mission_success_ratio = 1.0
        recon_asset_efficiency = 1.0
        expected_result = 0.96
        self.assertAlmostEqual(calcRecoAccuracy("Number", recon_mission_success_ratio, recon_asset_efficiency)[1], expected_result, delta=0.03)
        self.assertEqual(calcRecoAccuracy("Number", recon_mission_success_ratio, recon_asset_efficiency)[0], "MAX")

        # Test con valori di input non validi
        recon_mission_success_ratio = -1.0
        recon_asset_efficiency = 0.5
        with self.assertRaises(ValueError):
            calcRecoAccuracy("Number", recon_mission_success_ratio, recon_asset_efficiency)

        recon_mission_success_ratio = 0.5
        recon_asset_efficiency = -1.0
        with self.assertRaises(ValueError):
            calcRecoAccuracy("Number", recon_mission_success_ratio, recon_asset_efficiency)


    def testCalcRecoEfficiencyAccuracy(self):
        # Test con valori di input validi
        recon_mission_success_ratio = 0.65
        recon_asset_efficiency = 0.75
        expected_result = 0.95  # calcolato manualmente sostituisce con string
        self.assertAlmostEqual(calcRecoAccuracy("Efficiency", recon_mission_success_ratio, recon_asset_efficiency)[1], expected_result, delta=0.03)
        self.assertEqual(calcRecoAccuracy("Efficiency", recon_mission_success_ratio, recon_asset_efficiency)[0], "MAX")


        # Test con valori di input validi
        recon_mission_success_ratio = 0.37
        recon_asset_efficiency = 0.45
        expected_result = 0.74  # calcolato manualmente
        self.assertAlmostEqual(calcRecoAccuracy("Efficiency", recon_mission_success_ratio, recon_asset_efficiency)[1], expected_result, delta=0.03)
        self.assertEqual(calcRecoAccuracy("Efficiency", recon_mission_success_ratio, recon_asset_efficiency)[0], "M")

        # Test con valori di input validi
        recon_mission_success_ratio = 0.2
        recon_asset_efficiency = 0.25
        expected_result = 0.55  # calcolato manualmente
        self.assertAlmostEqual(calcRecoAccuracy("Efficiency", recon_mission_success_ratio, recon_asset_efficiency)[1], expected_result, delta=0.03)
        self.assertEqual(calcRecoAccuracy("Efficiency", recon_mission_success_ratio, recon_asset_efficiency)[0], "L")

        # Test con valori di input estremi
        recon_mission_success_ratio = 0.0
        recon_asset_efficiency = 0.0
        expected_result = 0.54
        self.assertAlmostEqual(calcRecoAccuracy("Efficiency", recon_mission_success_ratio, recon_asset_efficiency)[1], expected_result, delta=0.03)
        self.assertEqual(calcRecoAccuracy("Efficiency", recon_mission_success_ratio, recon_asset_efficiency)[0], "L")

        recon_mission_success_ratio = 1.0
        recon_asset_efficiency = 1.0
        expected_result = 0.96
        self.assertAlmostEqual(calcRecoAccuracy("Efficiency", recon_mission_success_ratio, recon_asset_efficiency)[1], expected_result, delta=0.03)
        self.assertEqual(calcRecoAccuracy("Efficiency", recon_mission_success_ratio, recon_asset_efficiency)[0], "MAX")

        # Test con valori di input non validi
        recon_mission_success_ratio = -1.0
        recon_asset_efficiency = 0.5
        with self.assertRaises(ValueError):
            calcRecoAccuracy("Efficiency", recon_mission_success_ratio, recon_asset_efficiency)

        recon_mission_success_ratio = 0.5
        recon_asset_efficiency = -1.0
        with self.assertRaises(ValueError):
            calcRecoAccuracy("Efficiency", recon_mission_success_ratio, recon_asset_efficiency)



    def testEvaluateGroundTacticalAction(self):
        
        # attiva tabella risultati
        table_results = True
        
        # Variabili di input
        # gs = gf / gf_enemy;  gf = Tank*kt + Armor*ka + Motorized*km + Artillery*kar / (kt + ka + km + kar); gs > 1 vantaggio
        # flr = co / co_enemy; co = loss_asset or flt = media(co)/media(co_enemy) if sco = dev_std (co) <<; flr < 1 vantaggio
        # dyn_inc = flr / media(flr); dyn_inc >> 1 combat success increment 
        # cls = ( asset_stored + asset_production - co ) / ( enemy_asset_stored + enemy_asset_production + enemy_co ) or ( asset_stored + media(asset_production) - media(co) ) / ( enemy_asset_stored + media(enemy_asset_production) + media(enemy_co) ) if dev_std (co) and dev_std (co_enemy)<< 1; cls > 1 vantaggio
        
        # gs > 1 -> vantaggio                       HI: 0.1, MI: 0.5, EQ: 1, MS: 2.5, HS: 5
        # flr < 1 -> vantaggio                      HI: 5, MI: 2.5, EQ: 1, MS: 0.37, HS: 0.1
        # dyn_inc < 1 -> combat success increment   HI: 5, MI: 2.5, EQ: 1, MS: 0.35, HS: 0.1
        # cls > 1 -> vantaggio                      HI: 0.1, MI: 0.35, EQ: 1, MS: 2.5, HS: 5

        test_cases = [
            # RETRAIT Cases
            (0.1, 5, 5, 0.1, "RETRAIT", 0.1), # gs: HI, flr: HI, dyn_inc: HI, cls: HI
            (1, 5, 5, 0.1, "RETRAIT", 0.1), #  gs: EQ, flr: HI, dyn_inc: HI, cls: HI
            (0.5, 2.5, 2.5, 0.1, "RETRAIT", 0.15), # gs: MI, flr: MI, dyn_inc: HI, cls: HI
            (0.1, 1, 1, 0.35, "RETRAIT", 0.2), # gs: HI, flr: EQ, dyn_inc: EQ, cls: MI
            (1, 2.5, 2.5, 1, "RETRAIT", 0.2), # gs: EQ, flr: MI, dyn_inc: MI, cls: EQ
            (0.5, 2.5, 2.5, 5, "RETRAIT", 0.2), # gs: MI, flr: MI, dyn_inc: MI, cls: HS
            (0.5, 1, 1, 0.35, "RETRAIT", 0.2), # gs: MI, flr: EQ, dyn_inc: EQ, cls: MI           
            (0.5, 2.5, 2.5, 0.35, "RETRAIT", 0.1), # gs: MI, flr: MI, dyn_inc: MI, cls: MI
            (0.1, 2.5, 2.5, 0.1, "RETRAIT", 0.1), # gs: HI, flr: MI, dyn_inc: MI, cls: MI
            
            # DEFENSE Cases
            (1, 1, 1, 0.33, "DEFENSE", 0.35), # gs: EQ, flr: EQ, dyn_inc: EQ, cls: MI
            (0.5, 1, 1, 2.5, "DEFENSE", 0.4), # gs: MI, flr: EQ, dyn_inc: EQ, cls: MS                                       
            
            # MAINTAIN Cases                        
            (2.5, 1, 1, 0.33, "MAINTAIN", 0.7), # gs: MS, flr: EQ, dyn_inc: EQ, cls: MI            
            (0.5, 0.37, 0.35, 0.35, "MAINTAIN", 0.6), # gs: MI, flr: MS, dyn_inc: MS, cls: MI
            (1, 0.37, 0.35, 1, "MAINTAIN", 0.7), # gs: EQ, flr: MS, dyn_inc: MS, cls: EQ            
            (1, 1, 0.35, 0.35, "MAINTAIN", 0.7), # gs: EQ, flr: EQ, dyn_inc: MS, cls: MI
                        

            # ATTACK Cases
            (5, 0.1, 0.1, 5, "ATTACK", 0.9), # gs: HS, flr: HS, dyn_inc: HS, cls: HS
            (2.5, 0.1, 0.1, 2.5, "ATTACK", 0.85), # gs: MS, flr: HS, dyn_inc: HS, cls: MS
            (5, 0.37, 0.35, 1, "ATTACK", 0.88), # gs: HS, flr: MS, dyn_inc: MS, cls: EQ
            (2.5, 0.37, 0.35, 5, "ATTACK", 0.82), # gs: MS, flr: MS, dyn_inc: MS, cls: HS   
            (1, 0.37, 0.35, 0.35, "ATTACK", 0.80), # gs: EQ, flr: MS, dyn_inc: MS, cls: MI         
            (2.5, 0.37, 0.35, 1, "ATTACK", 0.88), # gs: MS, flr: MS, dyn_inc: MS, cls: EQ
            (1, 0.37, 0.35, 2.5, "ATTACK", 0.8), # gs: EQ, flr: MS, dyn_inc: MS, cls: MS
            (5, 1, 1, 0.35, "ATTACK", 0.88), # gs: HS, flr: EQ, dyn_inc: EQ, cls: MI
            (2.5, 0.1, 0.1, 1, "ATTACK", 0.88), # gs: MS, flr: HS, dyn_inc: HS, cls: EQ
            
            # (5, 0.37, 0.35, 5, "ATTACK", 1.0), # gs: HS, flr: MS, dyn_inc: MS, cls: HS
        ]
        
        for gs, flr, dyn_inc, cls, expected_string, expected_numeric in test_cases:
            output_string, output_numeric = evaluateGroundTacticalAction(gs, flr, dyn_inc, cls)
            self.assertAlmostEqual(output_numeric, expected_numeric, delta=0.1, msg=f"gs: {gs}, flr: {flr}, dyn_inc: {dyn_inc}, cls: {cls}")
            self.assertEqual(output_string, expected_string, msg=f"gs: {gs}, flr: {flr}, dyn_inc: {dyn_inc}, cls: {cls}")


                
        if table_results:

            ground_superiority_values = [0.3, 0.9, 1.4] #[0.3, 0.9, 1.4, 3] #[0.0, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9, 1.0, 1.1, 1.5, 2, 3, 5, 10]  #np.arange( 0.1, 3.0, 0.3 )
            fight_load_ratio_values = [0.3, 0.9, 1.4] #[0.0, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9, 1.0, 1.1, 1.5, 2, 3, 5, 10]  #np.arange( 0.1, 3.0, 0.3 )
            dynamic_increment_values = [0.3, 0.9, 1.4] #[0.0, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9, 1.0, 1.1, 1.5, 2, 3, 5, 10]  #np.arange( 0.1, 3.0, 0.3 )
            combat_load_sustainability_values = [0.3, 0.9, 1.4] #[0.0, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9, 1.0, 1.1, 1.5, 2, 3, 5, 10]  #np.arange( 0.1, 3.0, 0.3 )


            # Crea una lista per memorizzare i risultati
            results = []

            # Itera su tutte le combinazioni di input
            for gs in ground_superiority_values:
                for flr in fight_load_ratio_values:
                    for dyn_inc in dynamic_increment_values:
                        for cls in combat_load_sustainability_values:
                            # Esegui il metodo con la combinazione corrente di input
                            output_string, output_numeric = evaluateGroundTacticalAction(gs, flr, dyn_inc, cls)
                            
                            # Aggiungi il risultato alla lista
                            results.append({
                                'gs': gs,
                                'flr': flr,
                                'dyn_inc': dyn_inc,
                                'cls': cls,
                                'output_string': output_string,
                                'output_numeric': output_numeric
                            })

            # Disabilita il troncamento delle righe e delle colonne
            pd.set_option('display.max_rows', None)  # Visualizza tutte le righe
            pd.set_option('display.max_columns', None)  # Visualizza tutte le colonne
            pd.set_option('display.width', None)  # Disabilita il wrapping del testo
            pd.set_option('display.max_colwidth', None)  # Visualizza tutto il contenuto delle celle


            # Crea un DataFrame con i risultati
            results_df = pd.DataFrame(results)

            results_df.to_csv('tactical_evaluation_results.csv', index=False)

            # Visualizza la tabella con i risultati
            print(results_df)

            # Verifica che i risultati siano coerenti con le aspettative
            for result in results:
                self.assertIsInstance(result['output_string'], str)
                self.assertIsInstance(result['output_numeric'], float)
                self.assertTrue(0 <= result['output_numeric'] <= 10)


    def testCalcFightResult(self):
        # Test con valori di input validi
        n_fr = 10
        n_en = 5
        eff_fr = 0.8
        eff_en = 0.6
        result = calcFightResult(n_fr, n_en, eff_fr, eff_en)        
        self.assertLessEqual(result, 1)

        # Test con valori di input estremi
        n_fr = 100
        n_en = 101
        eff_fr = 0.75
        eff_en = 0.76
        result = calcFightResult(n_fr, n_en, eff_fr, eff_en)
        self.assertAlmostEqual(result, 1, delta = 0.5)

        n_fr = 120
        n_en = 1
        eff_fr = 1.0
        eff_en = 1.0
        result = calcFightResult(n_fr, n_en, eff_fr, eff_en)
        self.assertLess(result, 0.3)

        n_fr = 1
        n_en = 150
        eff_fr = 1.0
        eff_en = 1.0
        result = calcFightResult(n_fr, n_en, eff_fr, eff_en)
        self.assertGreater(result, 4)

        n_fr = 10
        n_en = 10
        eff_fr = 0.7
        eff_en = 0.3
        result = calcFightResult(n_fr, n_en, eff_fr, eff_en)
        self.assertLess(result, 1)

        n_fr = 10
        n_en = 10
        eff_fr = 0.3
        eff_en = 0.7
        result = calcFightResult(n_fr, n_en, eff_fr, eff_en)
        self.assertGreater(result, 1)

        n_fr = 10
        n_en = 10
        eff_fr = 0.5
        eff_en = 0.6
        result = calcFightResult(n_fr, n_en, eff_fr, eff_en)
        self.assertAlmostEqual(result, 1, delta = 0.5)# non è detto che la variazione sia contenuta tra 0.3 e 1.7: può anche essere superore e/o inferiore

        n_fr = 18
        n_en = 20
        eff_fr = 0.8
        eff_en = 0.8
        result = calcFightResult(n_fr, n_en, eff_fr, eff_en)
        self.assertAlmostEqual(result, 1, delta = 3)# 2.38 troppo

        n_fr = 132
        n_en = 13
        eff_fr = 0.4
        eff_en = 1.0
        result = calcFightResult(n_fr, n_en, eff_fr, eff_en)
        self.assertLess(result, 1)

        # Test con valori di input non validi
        n_fr = -1
        n_en = 5
        eff_fr = 0.8
        eff_en = 0.6
        with self.assertRaises(ValueError):
            calcFightResult(n_fr, n_en, eff_fr, eff_en)

        n_fr = 10
        n_en = -1
        eff_fr = 0.8
        eff_en = 0.6
        with self.assertRaises(ValueError):
            calcFightResult(n_fr, n_en, eff_fr, eff_en)

        n_fr = 10
        n_en = 5
        eff_fr = -1.0
        eff_en = 0.6
        with self.assertRaises(ValueError):
            calcFightResult(n_fr, n_en, eff_fr, eff_en)

        n_fr = 10
        n_en = 5
        eff_fr = 0.8
        eff_en = -1.0
        with self.assertRaises(ValueError):
            calcFightResult(n_fr, n_en, eff_fr, eff_en)



    def test_evaluateCombatSuperiority(self):

        # Test con asset uguali
        asset_fr = {
            "Tank": {"num": 10, "combat_power": {"Attack": 0.8, "Defense": 0.8, "Maintain": 0.8}},
            "Armored": {"num": 5, "combat_power": {"Attack": 0.6, "Defense": 0.6, "Maintain": 0.6}},
            "Motorized": {"num": 20, "combat_power": {"Attack": 0.7, "Defense": 0.7, "Maintain": 0.7}},
            "Artillery_Semovent": {"num": 5, "combat_power": {"Attack": 0.5, "Defense": 0.5, "Maintain": 0.5}},
            "Artillery_Fixed": {"num": 10, "combat_power": {"Attack": 0.4, "Defense": 0.4, "Maintain": 0.4}},            
        }
        asset_en = {
            "Tank": {"num": 10, "combat_power": {"Attack": 0.8, "Defense": 0.8, "Maintain": 0.8}},
            "Armored": {"num": 5, "combat_power": {"Attack": 0.6, "Defense": 0.6, "Maintain": 0.6}},
            "Motorized": {"num": 20, "combat_power": {"Attack": 0.7, "Defense": 0.7, "Maintain": 0.7}},
            "Artillery_Semovent": {"num": 5, "combat_power": {"Attack": 0.5, "Defense": 0.5, "Maintain": 0.5}},
            "Artillery_Fixed": {"num": 10, "combat_power": {"Attack": 0.4, "Defense": 0.4, "Maintain": 0.4}},            
        }
        result = evaluateCombatSuperiority("Attack", asset_fr, asset_en)
        self.assertAlmostEqual(result, 0.5, delta = 0.1)
        result = evaluateCombatSuperiority("Defense", asset_fr, asset_en)
        self.assertAlmostEqual(result, 0.5, delta = 0.1)
        result = evaluateCombatSuperiority("Maintain", asset_fr, asset_en)
        self.assertAlmostEqual(result, 0.5, delta = 0.1)

        # Test con enemy asset azzerati
        asset_fr = {            
            "Tank": {"num": 200, "combat_power": {"Attack": 0.9, "Defense": 0.9, "Maintain": 0.9}},
            "Armored": {"num": 150, "combat_power": {"Attack": 0.77, "Defense": 0.77, "Maintain": 0.77}},
            "Motorized": {"num": 150, "combat_power": {"Attack": 0.6, "Defense": 0.6, "Maintain": 0.6}},
            "Artillery_Semovent": {"num": 100, "combat_power": {"Attack": 0.5, "Defense": 0.5, "Maintain": 0.5}},
            "Artillery_Fixed": {"num": 50, "combat_power": {"Attack": 0.4, "Defense": 0.4, "Maintain": 0.4}},
            }
        asset_en = {
            "Tank": {"num": 0, "combat_power": {"Attack": 0, "Defense": 0, "Maintain": 0}},
            "Armored": {"num": 0, "combat_power": {"Attack": 0, "Defense": 0, "Maintain": 0}},
            "Motorized": {"num": 0, "combat_power": {"Attack": 0, "Defense": 0, "Maintain": 0}},
            "Artillery_Semovent": {"num": 0, "combat_power": {"Attack": 0, "Defense": 0, "Maintain": 0}},
            "Artillery_Fixed": {"num": 0, "combat_power": {"Attack": 0, "Defense": 0, "Maintain": 0}},
        }
        result = evaluateCombatSuperiority("Attack", asset_fr, asset_en)
        self.assertEqual(result, 1)
        result = evaluateCombatSuperiority("Defense", asset_fr, asset_en)
        self.assertEqual(result, 1)
        result = evaluateCombatSuperiority("Maintain", asset_fr, asset_en)
        self.assertEqual(result, 1)

        # Test con friendly asset azzerati
        asset_fr = {            
            "Tank": {"num": 0, "combat_power": {"Attack": 0, "Defense": 0, "Maintain": 0}},
            "Armored": {"num": 0, "combat_power": {"Attack": 0, "Defense": 0, "Maintain": 0}},
            "Motorized": {"num": 0, "combat_power": {"Attack": 0, "Defense": 0, "Maintain": 0}},
            "Artillery_Semovent": {"num": 0, "combat_power": {"Attack": 0, "Defense": 0, "Maintain": 0}},
            "Artillery_Fixed": {"num": 0, "combat_power": {"Attack": 0, "Defense": 0, "Maintain": 0}},
            }
        asset_en = {
            "Tank": {"num": 200, "combat_power": {"Attack": 0.9, "Defense": 0.9, "Maintain": 0.9}},
            "Armored": {"num": 150, "combat_power": {"Attack": 0.77, "Defense": 0.77, "Maintain": 0.77}},
            "Motorized": {"num": 150, "combat_power": {"Attack": 0.6, "Defense": 0.6, "Maintain": 0.6}},
            "Artillery_Semovent": {"num": 100, "combat_power": {"Attack": 0.5, "Defense": 0.5, "Maintain": 0.5}},
            "Artillery_Fixed": {"num": 50, "combat_power": {"Attack": 0.4, "Defense": 0.4, "Maintain": 0.4}},
        }
        result = evaluateCombatSuperiority("Attack", asset_fr, asset_en)
        self.assertEqual(result, 0)
        result = evaluateCombatSuperiority("Defense", asset_fr, asset_en)
        self.assertEqual(result, 0)
        result = evaluateCombatSuperiority("Maintain", asset_fr, asset_en)
        self.assertEqual(result, 0)
             
        # Test con asset num e efficiency diversi
        asset_fr = {
            "Tank": {"num": 10, "combat_power": {"Attack": 0.7, "Defense": 0.7, "Maintain": 0.7}},
            "Armored": {"num": 5, "combat_power": {"Attack": 0.6, "Defense": 0.6, "Maintain": 0.6}},
            "Motorized": {"num": 20, "combat_power": {"Attack": 0.5, "Defense": 0.5, "Maintain": 0.5}},
            "Artillery_Semovent": {"num": 5, "combat_power": {"Attack": 0.4, "Defense": 0.4, "Maintain": 0.4}},
            "Artillery_Fixed": {"num": 10, "combat_power": {"Attack": 0.3, "Defense": 0.3, "Maintain": 0.3}},
            }
        asset_en = {
            "Tank": {"num": 200, "combat_power": {"Attack": 0.9, "Defense": 0.9, "Maintain": 0.9}},
            "Armored": {"num": 150, "combat_power": {"Attack": 0.77, "Defense": 0.77, "Maintain": 0.77}},
            "Motorized": {"num": 150, "combat_power": {"Attack": 0.6, "Defense": 0.6, "Maintain": 0.6}},
            "Artillery_Semovent": {"num": 100, "combat_power": {"Attack": 0.5, "Defense": 0.5, "Maintain": 0.5}},
            "Artillery_Fixed": {"num": 50, "combat_power": {"Attack": 0.4, "Defense": 0.4, "Maintain": 0.4}},
        }
        result = evaluateCombatSuperiority("Attack", asset_fr, asset_en)
        self.assertAlmostEqual(result, 0.05, delta = 0.005)
        result = evaluateCombatSuperiority("Defense", asset_fr, asset_en)
        self.assertAlmostEqual(result, 0.05, delta = 0.005)
        result = evaluateCombatSuperiority("Maintain", asset_fr, asset_en)
        self.assertAlmostEqual(result, 0.05, delta = 0.005)

        # Test con asset num e efficiency diversi
        asset_fr = {
            "Tank": {"num": 10, "combat_power": {"Attack": 0.7, "Defense": 0.7, "Maintain": 0.7}},
            "Armored": {"num": 5, "combat_power": {"Attack": 0.6, "Defense": 0.6, "Maintain": 0.6}},
            "Motorized": {"num": 20, "combat_power": {"Attack": 0.5, "Defense": 0.5, "Maintain": 0.5}},
            "Artillery_Semovent": {"num": 5, "combat_power": {"Attack": 0.4, "Defense": 0.4, "Maintain": 0.4}},
            "Artillery_Fixed": {"num": 10, "combat_power": {"Attack": 0.3, "Defense": 0.3, "Maintain": 0.3}},
        }
        asset_en = {
            "Tank": {"num": 20, "combat_power": {"Attack": 0.9, "Defense": 0.9, "Maintain": 0.9}},
            "Armored": {"num": 15, "combat_power": {"Attack": 0.77, "Defense": 0.77, "Maintain": 0.77}},
            "Motorized": {"num": 15, "combat_power": {"Attack": 0.6, "Defense": 0.6, "Maintain": 0.6}},
            "Artillery_Semovent": {"num": 10, "combat_power": {"Attack": 0.5, "Defense": 0.5, "Maintain": 0.5}},
            "Artillery_Fixed": {"num": 5, "combat_power": {"Attack": 0.4, "Defense": 0.4, "Maintain": 0.4}},
        }
        result = evaluateCombatSuperiority("Attack", asset_fr, asset_en)
        self.assertAlmostEqual(result, 0.33, delta = 0.05)
        result = evaluateCombatSuperiority("Defense", asset_fr, asset_en)
        self.assertAlmostEqual(result, 0.33, delta = 0.05)
        result = evaluateCombatSuperiority("Maintain", asset_fr, asset_en)
        self.assertAlmostEqual(result, 0.33, delta = 0.05)

        # Test con asset num e efficiency diversi
        asset_fr = {
            "Tank": {"num": 20, "combat_power": {"Attack": 0.9, "Defense": 0.9, "Maintain": 0.9}},
            "Armored": {"num": 15, "combat_power": {"Attack": 0.77, "Defense": 0.77, "Maintain": 0.77}},
            "Motorized": {"num": 15, "combat_power": {"Attack": 0.6, "Defense": 0.6, "Maintain": 0.6}},
            "Artillery_Semovent": {"num": 10, "combat_power": {"Attack": 0.5, "Defense": 0.5, "Maintain": 0.5}},
            "Artillery_Fixed": {"num": 5, "combat_power": {"Attack": 0.4, "Defense": 0.4, "Maintain": 0.4}},
        }
        asset_en = {
            "Tank": {"num": 10, "combat_power": {"Attack": 0.7, "Defense": 0.7, "Maintain": 0.7}},
            "Armored": {"num": 5, "combat_power": {"Attack": 0.6, "Defense": 0.6, "Maintain": 0.6}},
            "Motorized": {"num": 20, "combat_power": {"Attack": 0.5, "Defense": 0.5, "Maintain": 0.5}},
            "Artillery_Semovent": {"num": 5, "combat_power": {"Attack": 0.4, "Defense": 0.4, "Maintain": 0.4}},
            "Artillery_Fixed": {"num": 10, "combat_power": {"Attack": 0.3, "Defense": 0.3, "Maintain": 0.3}},
        }
        result = evaluateCombatSuperiority("Attack", asset_fr, asset_en)
        self.assertAlmostEqual(result, 0.64, delta = 0.05)
        result = evaluateCombatSuperiority("Defense", asset_fr, asset_en)
        self.assertAlmostEqual(result, 0.63, delta = 0.05)
        result = evaluateCombatSuperiority("Maintain", asset_fr, asset_en)
        self.assertAlmostEqual(result, 0.63, delta = 0.05)

        # Test con asset diversi e azione di combattimento non valida
        asset_fr = {
            "Tank": {"num": 20, "combat_power": {"Attack": 0.9, "Defense": 0.9, "Maintain": 0.9}},
            "Armored": {"num": 15, "combat_power": {"Attack": 0.77, "Defense": 0.77, "Maintain": 0.77}},
            "Motorized": {"num": 15, "combat_power": {"Attack": 0.6, "Defense": 0.6, "Maintain": 0.6}},
            "Artillery_Semovent": {"num": 10, "combat_power": {"Attack": 0.5, "Defense": 0.5, "Maintain": 0.5}},
            "Artillery_Fixed": {"num": 5, "combat_power": {"Attack": 0.4, "Defense": 0.4, "Maintain": 0.4}},
        }
        asset_en = {
            "Tank": {"num": 10, "combat_power": {"Attack": 0.7, "Defense": 0.7, "Maintain": 0.7}},
            "Armored": {"num": 5, "combat_power": {"Attack": 0.6, "Defense": 0.6, "Maintain": 0.6}},
            "Motorized": {"num": 20, "combat_power": {"Attack": 0.5, "Defense": 0.5, "Maintain": 0.5}},
            "Artillery_Semovent": {"num": 5, "combat_power": {"Attack": 0.4, "Defense": 0.4, "Maintain": 0.4}},
            "Artillery_Fixed": {"num": 10, "combat_power": {"Attack": 0.3, "Defense": 0.3, "Maintain": 0.3}},
        }
        with self.assertRaises(ValueError):
            evaluateCombatSuperiority("azione_non_valida", asset_fr, asset_en)

        # Test con categoria asset non incluse
        asset_fr = {
            "Tank": {"num": 20, "combat_power": {"Attack": 0.9, "Defense": 0.9, "Maintain": 0.9}},
            "Armored": {"num": 15, "combat_power": {"Attack": 0.77, "Defense": 0.77, "Maintain": 0.77}},
            "Motorized": {"num": 15, "combat_power": {"Attack": 0.6, "Defense": 0.6, "Maintain": 0.6}},
            "Artillery_Semovent": {"num": 10, "combat_power": {"Attack": 0.5, "Defense": 0.5, "Maintain": 0.5}},
            "Artillery_Fixed": {"num": 5, "combat_power": {"Attack": 0.4, "Defense": 0.4, "Maintain": 0.4}},
        }
        asset_en = {
            "Tank": {"num": 10, "combat_power": {"Attack": 0.7, "Defense": 0.7, "Maintain": 0.7}},
            "Armored": {"num": 5, "combat_power": {"Attack": 0.6, "Defense": 0.6, "Maintain": 0.6}},
            "NOT_INCLUDED": {"num": 20, "combat_power": {"Attack": 0.5, "Defense": 0.5, "Maintain": 0.5}},
            "Artillery_Semovent": {"num": 5, "combat_power": {"Attack": 0.4, "Defense": 0.4, "Maintain": 0.4}},
            "Artillery_Fixed": {"num": 10, "combat_power": {"Attack": 0.3, "Defense": 0.3, "Maintain": 0.3}},
        }
        with self.assertRaises(ValueError):
            evaluateCombatSuperiority("azione_non_valida", asset_fr, asset_en)

# test_evaluateCriticality


class TestTargetAffinity(unittest.TestCase):
    """Unit tests for Tactical_Evaluation.target_affinity()."""

    def setUp(self):
        self.airbase = Military(
            mil_category=Context.MILITARY_CATEGORY["Air_Base"][1], name="AB", side="Blue"
        )
        self.groundbase = Military(
            mil_category=Context.MILITARY_CATEGORY["Ground_Base"][1], name="GB", side="Blue"
        )
        self.target = Block(
            name="Target", description="", side="Red", category="Military",
            sub_category="Base", functionality="Attack", value=5,
        )
        self.target._assets = {}

    @staticmethod
    def _mock_aircraft(model):
        m = MagicMock()
        m.__class__ = _Aircraft
        m.model = model
        m.asset_type = aat.FIGHTER.value
        m.is_operative.return_value = True
        return m

    def test_same_side_returns_neutral(self):
        friendly = Block(
            name="Friendly", description="", side="Blue", category="Military",
            sub_category="Base", functionality="Attack", value=5,
        )
        self.assertEqual(target_affinity(self.airbase, friendly), 1.0)

    def test_non_air_base_returns_neutral(self):
        self.assertEqual(target_affinity(self.groundbase, self.target), 1.0)

    def test_empty_target_profile_returns_neutral(self):
        """target senza asset -> target_profile_from_block restituisce {} -> neutro."""
        self.assertEqual(target_affinity(self.airbase, self.target), 1.0)

    def test_no_operative_aircraft_returns_neutral(self):
        self.airbase._assets = {}
        with patch.object(Tactical_Analysis, 'target_profile_from_block', return_value={'Armored': {'big': 1}}):
            self.assertEqual(target_affinity(self.airbase, self.target), 1.0)

    def test_weighted_generic_score_zero_returns_neutral(self):
        self.airbase._assets = {'a1': self._mock_aircraft('F-14A Tomcat')}
        with patch.object(Tactical_Analysis, 'target_profile_from_block', return_value={'Armored': {'big': 1}}), \
             patch.object(Aircraft_Data, 'combat_aggregate', return_value=(0.0, {})), \
             patch.object(Aircraft_Data, 'combat_aggregate_against_target', return_value=(0.0, {})):
            self.assertEqual(target_affinity(self.airbase, self.target), 1.0)

    def test_ratio_computed_within_bounds(self):
        self.airbase._assets = {'a1': self._mock_aircraft('F-14A Tomcat')}
        with patch.object(Tactical_Analysis, 'target_profile_from_block', return_value={'Armored': {'big': 1}}), \
             patch.object(Aircraft_Data, 'combat_aggregate', return_value=(2.0, {})), \
             patch.object(Aircraft_Data, 'combat_aggregate_against_target', return_value=(3.0, {})):
            result = target_affinity(self.airbase, self.target)
        self.assertAlmostEqual(result, 1.5)

    def test_ratio_clipped_to_max(self):
        self.airbase._assets = {'a1': self._mock_aircraft('F-14A Tomcat')}
        with patch.object(Tactical_Analysis, 'target_profile_from_block', return_value={'Armored': {'big': 1}}), \
             patch.object(Aircraft_Data, 'combat_aggregate', return_value=(1.0, {})), \
             patch.object(Aircraft_Data, 'combat_aggregate_against_target', return_value=(100.0, {})):
            result = target_affinity(self.airbase, self.target)
        self.assertEqual(result, 2.0)

    def test_ratio_clipped_to_min(self):
        self.airbase._assets = {'a1': self._mock_aircraft('F-14A Tomcat')}
        with patch.object(Tactical_Analysis, 'target_profile_from_block', return_value={'Armored': {'big': 1}}), \
             patch.object(Aircraft_Data, 'combat_aggregate', return_value=(10.0, {})), \
             patch.object(Aircraft_Data, 'combat_aggregate_against_target', return_value=(0.01, {})):
            result = target_affinity(self.airbase, self.target)
        self.assertEqual(result, 0.25)

    def test_weighted_by_aircraft_count(self):
        """Due modelli con conteggi diversi: la media è pesata per numero di velivoli, non per modello."""
        self.airbase._assets = {
            'a1': self._mock_aircraft('F-14A Tomcat'),
            'a2': self._mock_aircraft('F-14A Tomcat'),
            'a3': self._mock_aircraft('F-16CM Block 50'),
        }

        def fake_generic(self_ac):
            return (1.0, {}) if self_ac.model == 'F-14A Tomcat' else (2.0, {})

        def fake_target(self_ac, *args, **kwargs):
            return (2.0, {}) if self_ac.model == 'F-14A Tomcat' else (2.0, {})

        with patch.object(Tactical_Analysis, 'target_profile_from_block', return_value={'Armored': {'big': 1}}), \
             patch.object(Aircraft_Data, 'combat_aggregate', new=fake_generic), \
             patch.object(Aircraft_Data, 'combat_aggregate_against_target', new=fake_target):
            result = target_affinity(self.airbase, self.target)
        # weighted_generic = 2*1.0 + 1*2.0 = 4.0 ; weighted_target = 2*2.0 + 1*2.0 = 6.0 -> 1.5
        self.assertAlmostEqual(result, 1.5)


class TestCalculatePriorityTargetAffinity(unittest.TestCase):
    """Unit tests for the target_affinity parameter of Tactical_Evaluation.calculate_priority()."""

    @staticmethod
    def _military_block(side, category, cp_task, cp_value):
        m = MagicMock(spec=Military)
        m.side = side
        m.get_military_category.return_value = category
        m.combat_power.side_effect = _make_combat_power_side_effect(cp_value, cp_task)
        return m

    @staticmethod
    def _target(side, value, is_military=False, is_logistic=False, is_civilian=False,
                category=None, cp_task=None, cp_value=None):
        t = MagicMock(spec=Military)
        t.side = side
        t.value = value
        t.is_military.return_value = is_military
        t.is_logistic.return_value = is_logistic
        t.is_civilian.return_value = is_civilian
        if is_military:
            t.get_military_category.return_value = category
            t.combat_power.side_effect = _make_combat_power_side_effect(cp_value, cp_task)
        return t

    def test_default_target_affinity_is_neutral(self):
        block = self._military_block('Blue', 'Air_Base', 'CAP', 10.0)
        target = self._target('Red', 5, is_military=True, category='Ground_Base',
                               cp_task='Attack', cp_value=4.0)
        result_default = calculate_priority(
            block=block, target_block=target, weight=2.0, time_to_intercept=5.0, range_ratio=1.0
        )
        result_explicit = calculate_priority(
            block=block, target_block=target, weight=2.0, time_to_intercept=5.0, range_ratio=1.0,
            target_affinity=1.0,
        )
        self.assertEqual(result_default, result_explicit)

    def test_target_affinity_scales_military_branch(self):
        block = self._military_block('Blue', 'Air_Base', 'CAP', 10.0)
        target = self._target('Red', 5, is_military=True, category='Ground_Base',
                               cp_task='Attack', cp_value=4.0)
        base = calculate_priority(
            block=block, target_block=target, weight=2.0, time_to_intercept=5.0, range_ratio=1.0
        )
        scaled = calculate_priority(
            block=block, target_block=target, weight=2.0, time_to_intercept=5.0, range_ratio=1.0,
            target_affinity=2.0,
        )
        self.assertAlmostEqual(scaled, base * 2.0)

    def test_target_affinity_scales_logistic_branch(self):
        block = self._military_block('Blue', 'Air_Base', 'CAP', 10.0)
        target = self._target('Red', 5, is_logistic=True)
        base = calculate_priority(
            block=block, target_block=target, weight=2.0, time_to_intercept=5.0, range_ratio=1.0,
            target_priority=3.0,
        )
        scaled = calculate_priority(
            block=block, target_block=target, weight=2.0, time_to_intercept=5.0, range_ratio=1.0,
            target_priority=3.0, target_affinity=2.0,
        )
        self.assertAlmostEqual(scaled, base * 2.0)

    def test_target_affinity_scales_civilian_branch(self):
        block = self._military_block('Blue', 'Air_Base', 'CAP', 10.0)
        target = self._target('Red', 5, is_civilian=True)
        base = calculate_priority(
            block=block, target_block=target, weight=2.0, time_to_intercept=5.0, range_ratio=1.0
        )
        scaled = calculate_priority(
            block=block, target_block=target, weight=2.0, time_to_intercept=5.0, range_ratio=1.0,
            target_affinity=2.0,
        )
        self.assertAlmostEqual(scaled, base * 2.0)


class TestCalcAirPriorityTargetAffinity(unittest.TestCase):
    """Unit tests confirming Tactical_Evaluation.calc_air_priority() wires target_affinity through."""

    def test_calc_air_priority_uses_target_affinity(self):
        block = MagicMock(spec=Military)
        block.position = Point2D(0, 0)
        block.side = 'Blue'
        block.get_military_category.return_value = 'Air_Base'
        block.combat_power.side_effect = _make_combat_power_side_effect(10.0, 'CAP')
        block.time2attack.return_value = 5.0

        target = MagicMock(spec=Military)
        target.position = Point2D(10, 10)
        target.side = 'Red'
        target.id = 'target1'
        target.value = 5
        target.is_military.return_value = True
        target.is_logistic.return_value = False
        target.is_civilian.return_value = False
        target.get_military_category.return_value = 'Ground_Base'
        target.combat_power.side_effect = _make_combat_power_side_effect(4.0, 'Defense')

        with patch.object(Tactical_Evaluation, 'target_affinity', return_value=1.0) as mock_affinity:
            result_neutral = calc_air_priority(block, (0.0, target), weight=2.0)
            mock_affinity.assert_called_once_with(block, target)

        with patch.object(Tactical_Evaluation, 'target_affinity', return_value=2.0):
            result_scaled = calc_air_priority(block, (0.0, target), weight=2.0)

        self.assertAlmostEqual(result_scaled, result_neutral * 2.0)


class TestCalcSurfacePriorityUnaffectedByAffinity(unittest.TestCase):
    """Regression: Tactical_Evaluation.calc_surface_priority() must never consult target_affinity —
    the design keeps the defense/surface branch bit-identical to before item 7."""

    def test_calc_surface_priority_never_calls_target_affinity(self):
        block = MagicMock(spec=Military)
        block.position = Point2D(0, 0)
        block.side = 'Blue'
        block.get_military_category.return_value = 'Ground_Base'
        block.combat_power.side_effect = _make_combat_power_side_effect(10.0, 'Attack')
        block.time2attack.return_value = 5.0
        block.artillery_in_range.return_value = {'target_within_med_range': False, 'med_range_ratio': 1.0}

        target = MagicMock(spec=Military)
        target.position = Point2D(10, 10)
        target.side = 'Red'
        target.value = 5
        target.is_military.return_value = True
        target.is_logistic.return_value = False
        target.is_civilian.return_value = False
        target.get_military_category.return_value = 'Ground_Base'
        target.combat_power.side_effect = _make_combat_power_side_effect(4.0, 'Defense')

        with patch.object(Tactical_Evaluation, 'target_affinity') as mock_affinity:
            result = calc_surface_priority(block, (0.0, target), None, 2.0)
        mock_affinity.assert_not_called()
        self.assertGreater(result, 0.0)


class TestCalculatePriorityActionRoles(unittest.TestCase):
    """Fase 2: Tactical_Evaluation.calculate_priority() seleziona Attack/Defense(+Maintain) per side."""

    def _military(self, side, category, **combat_power_kwargs):
        m = MagicMock(spec=Military)
        m.side = side
        m.get_military_category.return_value = category
        m.combat_power.side_effect = _make_combat_power_side_effect(**combat_power_kwargs)
        m.value = 5
        m.is_military.return_value = True
        m.is_logistic.return_value = False
        m.is_civilian.return_value = False
        return m

    def _call(self, block, target):
        return calculate_priority(
            block=block, target_block=target, weight=1.0, time_to_intercept=5.0, range_ratio=1.0
        )

    def test_attack_branch_uses_own_attack_and_target_defense_maintain_max_for_ground(self):
        """Ramo attacco (side diversi), ground vs ground: proprio='Attack', bersaglio=max(Defense,Maintain)."""
        block = self._military('Blue', 'Ground_Base', value=10.0, task='Attack')
        # Il bersaglio vale meno in Defense che in Maintain: deve vincere Maintain.
        target = self._military('Red', 'Ground_Base', value=1.0)
        target.combat_power.side_effect = lambda force=None, action=None: (
            {'Defense': 2.0, 'Maintain': 6.0}.get(action, 0.0) if action else {}
        )
        self._call(block, target)
        target.combat_power.assert_any_call(force='ground', action='Defense')
        target.combat_power.assert_any_call(force='ground', action='Maintain')
        block.combat_power.assert_called_with(force='ground', action='Attack')

    def test_attack_branch_sea_uses_only_defense_no_maintain(self):
        """Ramo attacco, sea vs sea: SEA_TASK non ha 'Maintain', il bersaglio usa solo 'Defense'."""
        block = self._military('Blue', 'Naval_Base', value=10.0, task='Attack')
        target = self._military('Red', 'Naval_Base', value=4.0, task='Defense')
        self._call(block, target)
        target.combat_power.assert_called_once_with(force='sea', action='Defense')

    def test_defense_branch_uses_defense_for_both_sides(self):
        """Ramo difesa (stesso side): sia il blocco proprio sia l'alleato protetto usano 'Defense'."""
        block = self._military('Blue', 'Ground_Base', value=10.0, task='Defense')
        target = self._military('Blue', 'Ground_Base', value=4.0, task='Defense')
        self._call(block, target)
        block.combat_power.assert_called_with(force='ground', action='Defense')
        target.combat_power.assert_called_once_with(force='ground', action='Defense')

    def test_air_target_ignores_action_in_attack_branch(self):
        """Bersaglio 'air' nel ramo attacco: nessuna azione passata (AIR_COMBAT_EFFICACY piatta)."""
        block = self._military('Blue', 'Ground_Base', value=10.0, task='Attack')
        target = self._military('Red', 'Air_Base', value=3.0)
        self._call(block, target)
        target.combat_power.assert_called_once_with(force='air')


class TestCalculatePriorityUseReconSnapshot(unittest.TestCase):
    """Fase 5/6: Tactical_Evaluation.calculate_priority(recon_cp_snapshot=...) -- sostituzione del
    target_cp del ramo attacco con lo snapshot di ricognizione."""

    def _military_mock(self, side, category, cp_value=10.0, block_id='mock'):
        m = MagicMock(spec=Military)
        m.side = side
        m.id = block_id
        m.get_military_category.return_value = category
        m.combat_power.side_effect = _make_combat_power_side_effect(cp_value)
        m.value = 5
        m.is_military.return_value = True
        m.is_logistic.return_value = False
        m.is_civilian.return_value = False
        return m

    def _call(self, block, target, recon_cp_snapshot=None):
        return calculate_priority(
            block=block, target_block=target, weight=1.0, time_to_intercept=5.0, range_ratio=1.0,
            recon_cp_snapshot=recon_cp_snapshot,
        )

    def test_attack_branch_uses_snapshot_value_when_present(self):
        block = self._military_mock('Blue', 'Ground_Base', cp_value=10.0)
        target = self._military_mock('Red', 'Ground_Base', cp_value=4.0, block_id='enemy1')

        with patch.object(Tactical_Analysis, 'representative_combat_power', wraps=Tactical_Analysis.representative_combat_power) as mock_rcp:
            result_recon = self._call(block, target, recon_cp_snapshot={'enemy1': 99.0})
            # la combat power del bersaglio non deve mai passare da representative_combat_power
            # quando recon_cp_snapshot è dato e il ramo è attacco: solo il blocco proprio la usa.
            for call in mock_rcp.call_args_list:
                self.assertIsNot(call.args[0] if call.args else call.kwargs.get('block'), target)

        result_ground_truth = self._call(block, target, recon_cp_snapshot=None)
        self.assertNotEqual(result_recon, result_ground_truth)

    def test_attack_branch_snapshot_miss_yields_low_priority_ratio(self):
        """Un bersaglio nemico assente dallo snapshot (non osservato in questo sweep) vale
        target_cp=0.0 -- non "ground-truth di ripiego" -- che produce il ratio basso 0.1
        (policy no-visibility, v. feedback_no_visibility_low_priority)."""
        block = self._military_mock('Blue', 'Ground_Base', cp_value=10.0)
        target = self._military_mock('Red', 'Ground_Base', cp_value=4.0, block_id='unseen_enemy')

        result = self._call(block, target, recon_cp_snapshot={})  # sweep completato, non osservato
        expected = (target.value * 0.1 * 1.0 * 1.0 * 1.0) / 5.0
        self.assertAlmostEqual(result, expected)

    def test_defense_branch_ignores_snapshot_even_when_present(self):
        """Ramo difesa (stesso side): il bersaglio è un alleato, sempre ground-truth anche se
        viene passato un recon_cp_snapshot che conterrebbe un valore diverso per quell'id."""
        block = self._military_mock('Blue', 'Ground_Base', cp_value=10.0)
        ally = self._military_mock('Blue', 'Ground_Base', cp_value=4.0, block_id='ally1')

        result_with_snapshot = self._call(block, ally, recon_cp_snapshot={'ally1': 999.0})  # mai consultato
        result_no_snapshot = self._call(block, ally, recon_cp_snapshot=None)
        self.assertAlmostEqual(result_with_snapshot, result_no_snapshot)


if __name__ == '__main__':

    unittest.main()