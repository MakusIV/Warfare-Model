"""Scenario S20 del motore di sessioni virtuali: due missioni dello stesso blocco (F4b).

Prosegue `Test_Session_Scenarios.py` (S1-S9), `Test_Session_Scenarios_S10_S18.py` e gli S19 con la
stessa disciplina: si verifica un comportamento QUALITATIVO o STRUTTURALE, mai un numero calibrato.

Criterio "Fatto quando" della F4b di `Analysis/Document/Piano_Implementazione_Missione.md`: *un
nuovo scenario con due missioni dello stesso blocco mostra disingaggi indipendenti*. Dalla F4b la
missione e' l'unita' d'ingaggio (D3.e, vista `Logic/Mission_Adapter.MissionForce`); la decisione
dell'utente (2026-10-08) e' che missioni dello stesso blocco ingaggino e disingaggino SEPARATAMENTE,
senza un'Operazione che le leghi.

Composizione: quella di S1 senza CAS (`combined_arms_scenario(with_cas=False)`): Blue-Armor (3
M1A2-Abrams + 2 M2-Bradley) attacca da ovest la linea ferma Red-Line (3 BMP-2, obice 2S19-Msta,
Shilka, Strela-10), fire control a ruoli di test. Due varianti per seed, stessa geometria:
  * 'split': il blocco in DUE missioni d'attacco sulla stessa rotta, 'Blue-Armor:Tanks' (i 3 carri)
    e 'Blue-Armor:IFV' (i 2 Bradley);
  * 'single': gli stessi asset in UNA missione ('Blue-Armor:Attack', come S1).

Domande:
  * nella variante 'split' il blocco combatte come due forze d'ingaggio, ciascuna con il proprio
    `ForceOutcome` (impegnati, perdite, esito), nello stesso ingaggio con Red-Line;
  * una forza rotta (DISENGAGED/DESTROYED) non lancia piu' nuove salve, in entrambe le varianti;
  * il disingaggio di una missione NON trascina l'altra: in almeno un seed una missione si rompe e
    gli asset dell'altra sparano ancora dopo quell'istante; con una sola missione, invece, dopo la
    rottura nessun asset del blocco spara piu' (si rompono insieme).
"""

import unittest

from Code.Dynamic_War_Manager.Source.Logic import Contact_Scheduler as CS
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F

BLOCK = 'Blue-Armor'
TANKS = f'{BLOCK}:Tanks'
IFV = f'{BLOCK}:IFV'
SINGLE = f'{BLOCK}:Attack'
TARGET = 'Red-Line'
OBJECTIVE = [(2_000.0, 0.0)]   # stesso obiettivo di S1 (combined_arms_scenario)


def _seeds(prefix, count):
    return [f'{prefix}-{index}' for index in range(count)]


def _build(split: bool) -> F.Scenario:
    """Scenario ricostruito da zero (gli asset vengono mutati da run_session)."""
    scenario = F.combined_arms_scenario(with_cas=False)

    if split:
        blue = scenario.force(BLOCK)
        tanks = [asset_id for asset_id in blue.assets if '/mbt' in asset_id]
        ifvs = [asset_id for asset_id in blue.assets if '/ifv' in asset_id]
        scenario.missions = (F.missions_for(blue, OBJECTIVE, mission_type='Attack', only=tanks, name=TANKS,
                                            target=F.group_target(TARGET))
                             + F.missions_for(blue, OBJECTIVE, mission_type='Attack', only=ifvs, name=IFV,
                                              target=F.group_target(TARGET)))

    return scenario


def _broken(force_outcome) -> bool:
    return force_outcome.outcome in (ER.DISENGAGED, ER.DESTROYED)


def _launches(outcome, asset_ids):
    wanted = set(asset_ids)
    return [event.time for event in outcome.ammunition_events if event.asset_id in wanted]


class TestS20TwoMissionsOfOneBlock(F.LoggerSilencer, unittest.TestCase):
    """S20: due missioni dello stesso blocco ingaggiano e disingaggiano separatamente (F4b)."""

    SEEDS = _seeds('S20', 6)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.split, cls.single = [], []

        for session_id in cls.SEEDS:
            for split, runs in ((True, cls.split), (False, cls.single)):
                scenario = _build(split)
                runs.append((scenario, scenario.run(session_id)))

    def _mission_assets(self, scenario, mission_id):
        return next(m for m in scenario.missions if m.mission_id == mission_id).asset_ids

    def test_split_block_fights_as_two_engagement_forces(self):
        for scenario, outcome in self.split:
            found = {o.force_id: o for o in outcome.outcomes_of_block(BLOCK)}
            self.assertEqual(sorted(found), sorted([IFV, TANKS]))
            self.assertEqual((found[TANKS].committed, found[IFV].committed), (3, 2))
            self.assertTrue(all(o.block_id == BLOCK for o in found.values()))
            # Stesso ingaggio (componente connessa) con la linea rossa: forze distinte, non ingaggi distinti.
            self.assertIn((IFV, TANKS, TARGET), [tuple(o.force_id for o in e) for e in outcome.engagement_outcomes])

    def test_single_mission_is_one_engagement_force(self):
        for _, outcome in self.single:
            self.assertEqual([o.force_id for o in outcome.outcomes_of_block(BLOCK)], [SINGLE])

    def test_a_broken_force_launches_no_new_salvo(self):
        for runs in (self.split, self.single):
            for scenario, outcome in runs:
                for force in outcome.outcomes_of_block(BLOCK):
                    if not _broken(force):
                        continue

                    late = [t for t in _launches(outcome, self._mission_assets(scenario, force.force_id))
                            if t > force.time + CS.TIME_EPS]
                    self.assertEqual(late, [], f'{outcome.session_id} {force.force_id}')

    def test_missions_break_independently(self):
        """In almeno un seed una missione si rompe e l'altra spara ancora dopo quell'istante."""
        independent = []

        for scenario, outcome in self.split:
            found = {o.force_id: o for o in outcome.outcomes_of_block(BLOCK)}

            for broken_id, other_id in ((TANKS, IFV), (IFV, TANKS)):
                broken = found[broken_id]

                if not _broken(broken):
                    continue

                later = [t for t in _launches(outcome, self._mission_assets(scenario, other_id))
                         if t > broken.time + CS.TIME_EPS]

                if later:
                    independent.append((outcome.session_id, broken_id, broken.time, min(later)))

        self.assertGreater(len(independent), 0)

    def test_missions_of_one_block_can_end_differently(self):
        differ = [outcome.session_id for _, outcome in self.split
                  if len({(o.outcome, o.time) for o in outcome.outcomes_of_block(BLOCK)}) == 2]
        self.assertGreater(len(differ), 0)

    def test_single_mission_block_stops_firing_together(self):
        """Contrasto: con UNA missione la rottura ferma tutti gli asset del blocco."""
        broken_runs = 0

        for scenario, outcome in self.single:
            force = outcome.outcomes_of_block(BLOCK)[0]

            if not _broken(force):
                continue

            broken_runs += 1
            blue = scenario.force(BLOCK).assets
            self.assertEqual([t for t in _launches(outcome, blue) if t > force.time + CS.TIME_EPS], [],
                             outcome.session_id)

        self.assertGreater(broken_runs, 0)


if __name__ == '__main__':
    unittest.main()
