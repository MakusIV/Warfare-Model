import unittest
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import pandas as pd

# Importa il metodo da testare
from Dynamic_War_Manager.Source.Tactical_Evaluation import evaluate_ground_tactical_action

class TestEvaluateGroundTacticalAction(unittest.TestCase):

    def test_evaluate_ground_tactical_action(self):
        # Definisci i valori di input da testare
        ground_superiority_values = [0.3, 0.9, 1.4, 3] #[0.0, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9, 1.0, 1.1, 1.5, 2, 3, 5, 10]  #np.arange( 0.1, 3.0, 0.3 )
        fight_load_ratio_values = [0.3, 0.9, 1.4, 3] #[0.0, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9, 1.0, 1.1, 1.5, 2, 3, 5, 10]  #np.arange( 0.1, 3.0, 0.3 )
        dynamic_increment_values = [0.3, 0.9, 1.4, 3] #[0.0, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9, 1.0, 1.1, 1.5, 2, 3, 5, 10]  #np.arange( 0.1, 3.0, 0.3 )
        combat_load_sustainability_values = [0.3, 0.9, 1.4, 3] #[0.0, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9, 1.0, 1.1, 1.5, 2, 3, 5, 10]  #np.arange( 0.1, 3.0, 0.3 )

        # Crea una lista per memorizzare i risultati
        results = []

        # Itera su tutte le combinazioni di input
        for gs in ground_superiority_values:
            for flr in fight_load_ratio_values:
                for dyn_inc in dynamic_increment_values:
                    for cls in combat_load_sustainability_values:
                        # Esegui il metodo con la combinazione corrente di input
                        output_string, output_numeric = evaluate_ground_tactical_action(gs, flr, dyn_inc, cls)
                        
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

if __name__ == '__main__':
    unittest.main()