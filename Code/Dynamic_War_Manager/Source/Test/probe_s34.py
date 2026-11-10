"""Sonda di geometria di S34-BAND eseguibile con `python3 -m unittest` (nome senza `Test_`:
non e' scoperto dalla suite). Stampa i numeri della regola di fermata di §4.2.1 della
Proposta_Allineamento_Volumi_DES_Pianificatore.md e li verifica con asserzioni.

Controparte eseguibile dello script `Analysis/Document/Rapporti/Sonde_Allineamento_Volumi/probe_s34.py`
(che e' il documento della sonda, da eseguire con l'interprete della macchina come `probe_altitude.py`).
"""
import unittest

from Code.Dynamic_War_Manager.Source.Context import Reaction_Profile as RP
from Code.Dynamic_War_Manager.Source.Test import Test_Session_Scenarios_S34 as S34

OSA_REACTION_TOTAL_S = RP.REACTION_PROFILES['9A33-Osa'].total


class TestS34GeometryProbe(unittest.TestCase):
    """Regola di fermata §4.2.1: geometria dei profili di S34 (numeri dichiarati di test)."""

    def test_probe_geometry(self):
        # 1. climb_off: salve dell'Osa sopra i 5000 m in >= 3 semi su 4.
        seeds_with_salvos = 0
        print('== climb_off ==')
        for seed in S34.SEEDS:
            _, results, routes = S34.run_variant(seed, 'climb_off')
            salvoes = S34._salvos(results, S34.OSA)
            altitudes = [S34._relative_altitude(routes, s.target_id, s.t_launch) for s in salvoes]
            seeds_with_salvos += 1 if salvoes else 0
            print(f'  {seed}: salve={len(salvoes)} altitudini_rel={altitudes}')
        print(f'  semi con salve: {seeds_with_salvos}/4')
        self.assertGreaterEqual(seeds_with_salvos, 3)

        # 2. descend_on: NESSUN rilevamento dell'Osa sopra i 5000 m.
        detections_above = 0
        print('== descend_on ==')
        for seed in S34.SEEDS:
            _, results, routes = S34.run_variant(seed, 'descend_on')
            detections = [d for d in S34._detections(results, S34.OSA) if d.detected and d.time is not None]
            above = [(d.target_id, round(d.time, 2),
                      round(S34._relative_altitude(routes, d.target_id, d.time), 1))
                     for d in detections
                     if S34._relative_altitude(routes, d.target_id, d.time) > S34.BAND_MAX_M]
            detections_above += 1 if above else 0
            print(f'  {seed}: rilevamenti={len(detections)} sopra_5000={above}')
        print(f'  semi con rilevamento sopra 5000 m: {detections_above}/4')
        self.assertEqual(detections_above, 0)

        # 3. late_descend_on: almeno un rinvio (decisione con A-10C sopra 5000 m) per >= 3 semi su 4.
        seeds_with_deferral = 0
        print('== late_descend_on ==')
        for seed in S34.SEEDS:
            _, results, routes = S34.run_variant(seed, 'late_descend_on')
            detections = [d for d in S34._detections(results, S34.OSA) if d.detected and d.time is not None]
            salvoes = S34._salvos(results, S34.OSA)
            above = [round(S34._relative_altitude(routes, d.target_id, d.time + OSA_REACTION_TOTAL_S), 1)
                     for d in detections
                     if S34._relative_altitude(routes, d.target_id, d.time + OSA_REACTION_TOTAL_S) > S34.BAND_MAX_M]
            seeds_with_deferral += 1 if above else 0
            print(f'  {seed}: decisioni_sopra_5000={above} salve={len(salvoes)}')
        print(f'  semi con almeno una decisione sopra 5000 m: {seeds_with_deferral}/4')
        self.assertGreaterEqual(seeds_with_deferral, 3)


if __name__ == '__main__':
    unittest.main()
