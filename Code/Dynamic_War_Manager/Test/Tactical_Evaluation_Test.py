import unittest
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import pandas as pd
from Context import GROUND_ASSET_CATEGORY, GROUND_ACTION

# Importa il metodo da testare evaluateGroundTacticalAction
from Dynamic_War_Manager.Source.Tactical_Evaluation import evaluateGroundTacticalAction, calcRecoAccuracy, calcFightResult, evaluateCombatSuperiority

class TestEvaluateGroundTacticalAction(unittest.TestCase):

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
            
            # DEFENCE Cases
            (1, 1, 1, 0.33, "DEFENCE", 0.35), # gs: EQ, flr: EQ, dyn_inc: EQ, cls: MI
            (0.5, 1, 1, 2.5, "DEFENCE", 0.4), # gs: MI, flr: EQ, dyn_inc: EQ, cls: MS                                       
            
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
        eff_en = 1
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
            GROUND_ASSET_CATEGORY["Tank"]: {"num": 10, "efficiency": 0.8},
            GROUND_ASSET_CATEGORY["Armor"]: {"num": 5, "efficiency": 0.6},
            GROUND_ASSET_CATEGORY["Motorized"]: {"num": 20, "efficiency": 0.7},
            GROUND_ASSET_CATEGORY["Artillery_Semovent"]: {"num": 5, "efficiency": 0.5},
            GROUND_ASSET_CATEGORY["Artillery_Fix"]: {"num": 10, "efficiency": 0.4}
        }
        asset_en = {
            GROUND_ASSET_CATEGORY["Tank"]: {"num": 10, "efficiency": 0.8},
            GROUND_ASSET_CATEGORY["Armor"]: {"num": 5, "efficiency": 0.6},
            GROUND_ASSET_CATEGORY["Motorized"]: {"num": 20, "efficiency": 0.7},
            GROUND_ASSET_CATEGORY["Artillery_Semovent"]: {"num": 5, "efficiency": 0.5},
            GROUND_ASSET_CATEGORY["Artillery_Fix"]: {"num": 10, "efficiency": 0.4}
        }
        result = evaluateCombatSuperiority("Attack", asset_fr, asset_en)
        self.assertEqual(result, 0.5)
        result = evaluateCombatSuperiority("Defence", asset_fr, asset_en)
        self.assertEqual(result, 0.5)
        result = evaluateCombatSuperiority("Maintain", asset_fr, asset_en)
        self.assertEqual(result, 0.5)

        # Test con enemy asset azzerati
        asset_fr = {            
            GROUND_ASSET_CATEGORY["Tank"]: {"num": 200, "efficiency": 0.9},
            GROUND_ASSET_CATEGORY["Armor"]: {"num": 150, "efficiency": 0.77},
            GROUND_ASSET_CATEGORY["Motorized"]: {"num": 150, "efficiency": 0.6},
            GROUND_ASSET_CATEGORY["Artillery_Semovent"]: {"num": 100, "efficiency": 0.5},
            GROUND_ASSET_CATEGORY["Artillery_Fix"]: {"num": 50, "efficiency": 0.4}
            }
        asset_en = {
            GROUND_ASSET_CATEGORY["Tank"]: {"num": 0, "efficiency": 0},
            GROUND_ASSET_CATEGORY["Armor"]: {"num": 0, "efficiency": 0},
            GROUND_ASSET_CATEGORY["Motorized"]: {"num": 0, "efficiency": 0},
            GROUND_ASSET_CATEGORY["Artillery_Semovent"]: {"num": 0, "efficiency": 0},
            GROUND_ASSET_CATEGORY["Artillery_Fix"]: {"num": 0, "efficiency": 0}
        }
        result = evaluateCombatSuperiority("Attack", asset_fr, asset_en)
        self.assertEqual(result, 1)
        result = evaluateCombatSuperiority("Defence", asset_fr, asset_en)
        self.assertEqual(result, 1)
        result = evaluateCombatSuperiority("Maintain", asset_fr, asset_en)
        self.assertEqual(result, 1)

        # Test con friendly asset azzerati
        asset_fr = {            
            GROUND_ASSET_CATEGORY["Tank"]: {"num": 0, "efficiency": 0},
            GROUND_ASSET_CATEGORY["Armor"]: {"num": 0, "efficiency": 0},
            GROUND_ASSET_CATEGORY["Motorized"]: {"num": 0, "efficiency": 0},
            GROUND_ASSET_CATEGORY["Artillery_Semovent"]: {"num": 0, "efficiency": 0},
            GROUND_ASSET_CATEGORY["Artillery_Fix"]: {"num": 0, "efficiency": 0}            
            }
        asset_en = {
            GROUND_ASSET_CATEGORY["Tank"]: {"num": 200, "efficiency": 0.9},
            GROUND_ASSET_CATEGORY["Armor"]: {"num": 150, "efficiency": 0.77},
            GROUND_ASSET_CATEGORY["Motorized"]: {"num": 150, "efficiency": 0.6},
            GROUND_ASSET_CATEGORY["Artillery_Semovent"]: {"num": 100, "efficiency": 0.5},
            GROUND_ASSET_CATEGORY["Artillery_Fix"]: {"num": 50, "efficiency": 0.4}            
        }
        result = evaluateCombatSuperiority("Attack", asset_fr, asset_en)
        self.assertEqual(result, 0)
        result = evaluateCombatSuperiority("Defence", asset_fr, asset_en)
        self.assertEqual(result, 0)
        result = evaluateCombatSuperiority("Maintain", asset_fr, asset_en)
        self.assertEqual(result, 0)
             
        # Test con asset num e efficiency diversi
        asset_fr = {
            GROUND_ASSET_CATEGORY["Tank"]: {"num": 10, "efficiency": 0.7},
            GROUND_ASSET_CATEGORY["Armor"]: {"num": 5, "efficiency": 0.6},
            GROUND_ASSET_CATEGORY["Motorized"]: {"num": 20, "efficiency": 0.5},
            GROUND_ASSET_CATEGORY["Artillery_Semovent"]: {"num": 5, "efficiency": 0.4},
            GROUND_ASSET_CATEGORY["Artillery_Fix"]: {"num": 10, "efficiency": 0.3}
            }
        asset_en = {
            GROUND_ASSET_CATEGORY["Tank"]: {"num": 200, "efficiency": 0.9},
            GROUND_ASSET_CATEGORY["Armor"]: {"num": 150, "efficiency": 0.77},
            GROUND_ASSET_CATEGORY["Motorized"]: {"num": 150, "efficiency": 0.6},
            GROUND_ASSET_CATEGORY["Artillery_Semovent"]: {"num": 100, "efficiency": 0.5},
            GROUND_ASSET_CATEGORY["Artillery_Fix"]: {"num": 50, "efficiency": 0.4}
        }
        result = evaluateCombatSuperiority("Attack", asset_fr, asset_en)
        self.assertAlmostEqual(result, 0.0451, places = 4)
        result = evaluateCombatSuperiority("Defence", asset_fr, asset_en)
        self.assertAlmostEqual(result, 0.0491, places = 4)
        result = evaluateCombatSuperiority("Maintain", asset_fr, asset_en)
        self.assertAlmostEqual(result, 0.0541, places = 4)

        # Test con asset num e efficiency diversi
        asset_fr = {
            GROUND_ASSET_CATEGORY["Tank"]: {"num": 10, "efficiency": 0.7},
            GROUND_ASSET_CATEGORY["Armor"]: {"num": 5, "efficiency": 0.6},
            GROUND_ASSET_CATEGORY["Motorized"]: {"num": 20, "efficiency": 0.5},
            GROUND_ASSET_CATEGORY["Artillery_Semovent"]: {"num": 5, "efficiency": 0.4},
            GROUND_ASSET_CATEGORY["Artillery_Fix"]: {"num": 10, "efficiency": 0.3}
        }
        asset_en = {
            GROUND_ASSET_CATEGORY["Tank"]: {"num": 20, "efficiency": 0.9},
            GROUND_ASSET_CATEGORY["Armor"]: {"num": 15, "efficiency": 0.77},
            GROUND_ASSET_CATEGORY["Motorized"]: {"num": 15, "efficiency": 0.6},
            GROUND_ASSET_CATEGORY["Artillery_Semovent"]: {"num": 10, "efficiency": 0.5},
            GROUND_ASSET_CATEGORY["Artillery_Fix"]: {"num": 5, "efficiency": 0.4}
        }
        result = evaluateCombatSuperiority("Attack", asset_fr, asset_en)
        self.assertAlmostEqual(result, 0.3211, places = 4)
        result = evaluateCombatSuperiority("Defence", asset_fr, asset_en)
        self.assertAlmostEqual(result, 0.3409, places = 4)
        result = evaluateCombatSuperiority("Maintain", asset_fr, asset_en)
        self.assertAlmostEqual(result, 0.3639, places = 4)

        # Test con asset num e efficiency diversi
        asset_fr = {
            GROUND_ASSET_CATEGORY["Tank"]: {"num": 20, "efficiency": 0.9},
            GROUND_ASSET_CATEGORY["Armor"]: {"num": 15, "efficiency": 0.77},
            GROUND_ASSET_CATEGORY["Motorized"]: {"num": 15, "efficiency": 0.6},
            GROUND_ASSET_CATEGORY["Artillery_Semovent"]: {"num": 10, "efficiency": 0.5},
            GROUND_ASSET_CATEGORY["Artillery_Fix"]: {"num": 5, "efficiency": 0.4}
        }
        asset_en = {
            GROUND_ASSET_CATEGORY["Tank"]: {"num": 10, "efficiency": 0.7},
            GROUND_ASSET_CATEGORY["Armor"]: {"num": 5, "efficiency": 0.6},
            GROUND_ASSET_CATEGORY["Motorized"]: {"num": 20, "efficiency": 0.5},
            GROUND_ASSET_CATEGORY["Artillery_Semovent"]: {"num": 5, "efficiency": 0.4},
            GROUND_ASSET_CATEGORY["Artillery_Fix"]: {"num": 10, "efficiency": 0.3}
        }
        result = evaluateCombatSuperiority("Attack", asset_fr, asset_en)
        self.assertAlmostEqual(result, 0.6788, places = 4)
        result = evaluateCombatSuperiority("Defence", asset_fr, asset_en)
        self.assertAlmostEqual(result, 0.6590, places = 4)
        result = evaluateCombatSuperiority("Maintain", asset_fr, asset_en)
        self.assertAlmostEqual(result, 0.6360, places = 4)

        # Test con asset diversi e azione di combattimento non valida
        asset_fr = {
            GROUND_ASSET_CATEGORY["Tank"]: {"num": 20, "efficiency": 0.9},
            GROUND_ASSET_CATEGORY["Armor"]: {"num": 15, "efficiency": 0.77},
            GROUND_ASSET_CATEGORY["Motorized"]: {"num": 15, "efficiency": 0.6},
            GROUND_ASSET_CATEGORY["Artillery_Semovent"]: {"num": 10, "efficiency": 0.5},
            GROUND_ASSET_CATEGORY["Artillery_Fix"]: {"num": 5, "efficiency": 0.4}
        }
        asset_en = {
            GROUND_ASSET_CATEGORY["Tank"]: {"num": 10, "efficiency": 0.7},
            GROUND_ASSET_CATEGORY["Armor"]: {"num": 5, "efficiency": 0.6},
            GROUND_ASSET_CATEGORY["Motorized"]: {"num": 20, "efficiency": 0.5},
            GROUND_ASSET_CATEGORY["Artillery_Semovent"]: {"num": 5, "efficiency": 0.4},
            GROUND_ASSET_CATEGORY["Artillery_Fix"]: {"num": 10, "efficiency": 0.3}
        }
        with self.assertRaises(ValueError):
            evaluateCombatSuperiority("azione_non_valida", asset_fr, asset_en)

        # Test con categoria asset non incluse
        asset_fr = {
            GROUND_ASSET_CATEGORY["Tank"]: {"num": 20, "efficiency": 0.9},
            GROUND_ASSET_CATEGORY["Armor"]: {"num": 15, "efficiency": 0.77},
            GROUND_ASSET_CATEGORY["NOT_INCLUDED"]: {"num": 15, "efficiency": 0.6},
            GROUND_ASSET_CATEGORY["Artillery_Semovent"]: {"num": 10, "efficiency": 0.5},
            GROUND_ASSET_CATEGORY["Artillery_Fix"]: {"num": 5, "efficiency": 0.4}
        }
        asset_en = {
            GROUND_ASSET_CATEGORY["Tank"]: {"num": 10, "efficiency": 0.7},
            GROUND_ASSET_CATEGORY["Armor"]: {"num": 5, "efficiency": 0.6},
            GROUND_ASSET_CATEGORY["Motorized"]: {"num": 20, "efficiency": 0.5},
            GROUND_ASSET_CATEGORY["Artillery_Semovent"]: {"num": 5, "efficiency": 0.4},
            GROUND_ASSET_CATEGORY["Artillery_Fix"]: {"num": 10, "efficiency": 0.3}
        }
        with self.assertRaises(ValueError):
            evaluateCombatSuperiority("azione_non_valida", asset_fr, asset_en)



if __name__ == '__main__':
    unittest.main()