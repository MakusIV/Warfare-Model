"""Scenario S29 del motore di sessioni virtuali: fuoco su posizione (F7b).

Prosegue `Test_Session_Scenarios.py` (S1-S9) e gli S10-S28 con la stessa disciplina: si verifica un comportamento
QUALITATIVO o STRUTTURALE, mai un numero calibrato. Nel codice (decisione 15 dell'utente del 2026-10-20,
`Analysis/Document/Proposta_F7_Bersagli_Filtro_Armi.md` §6): una missione di terra con bersaglio POINT e l'azione
`Fire_At_Point` spara sulla posizione STIMATA del bersaglio (N3.e) anche se nessuno e' stato rilevato lassu'
(`Logic/Area_Fire`, evento di sessione AREA_FIRE, interruttore `Session_Simulator.F7_AREA_FIRE`): "il punto dove i blu
erano" colpisce solo chi c'e' ancora.

## S29-AREA (`TestS29AreaFire`)

Red-Art: 1 2S19-Msta (152 mm, 50 colpi) in (-15 km, 0), missione `Fire_Support` con un breve tratto DEPARTURE (-15 km, 0) ->
OBJECTIVE (-14,5 km, 0) e, sull'OBJECTIVE, `Fire_At_Point` di 40 colpi con avvio AT_TIME a 600 s, sul bersaglio POINT in
(0, 0) con provenienza ESTIMATED (`estimated_at` = -1800 s, `uncertainty_m` = 200 m): e' dove stava Blue-Col mezz'ora
prima della sessione. Nessuno ha rilevato nessuno (i registri non dichiarano sensori di terra per carri e artiglieria):
l'unico fuoco e' quello su posizione. Blue-Stay (2 BMP-2) e' fermo nel punto; Blue-Col (4 BMP-2) vi era, e:
  * 'stale': dalla partenza si sposta di 3 km verso est e vi resta: all'impatto (600 s piu' il tempo di volo) e' a 3 km dal
    punto, fuori dal disco di dispersione (raggio 200 m);
  * 'on_target': non ha missione, resta nel punto stimato;
  * 'switch_off': come 'stale' con `F7_AREA_FIRE` spento (premessa: senza l'evento nessuno e' colpito).
4 seed per variante (nomi stabili nella fotografia, nell'ordine). Le costanti d'impatto (dispersione, raggio letale) sono
STIME dichiarate in `Logic/Area_Fire`: qui si verificano solo effetti qualitativi, aggregando sui seed dove l'esito e'
casuale (con 40 colpi nel disco di 200 m e un raggio letale di 38 m un mezzo al centro e' colpito in media ~1,4 volte).
"""

import unittest
from unittest.mock import patch

from sympy import Point3D

from Code.Dynamic_War_Manager.Source.Command.Mission_Types import (
    FIRE_AT_POINT_ACTION,
    ActionKind,
    MissionAction,
    StartCondition,
    Target,
    TargetKind,
    TargetProvenance,
)
from Code.Dynamic_War_Manager.Source.Logic import Session_Simulator as SS
from Code.Dynamic_War_Manager.Source.Logic.Fire_Control import make_registry_fire_control
from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F

SEEDS_PER_SCENARIO = 4
AREA_DURATION = 1_200.0
FIRE_TIME = 600.0
ROUNDS = 40
AIM = (0.0, 0.0)
VARIANTS = ('stale', 'on_target', 'switch_off')
SHOOTER = 'Red-Art/art0'


def _seeds(prefix: str, count: int = SEEDS_PER_SCENARIO):
    return [f'{prefix}-{index}' for index in range(count)]


def _hits(outcome, prefix: str):
    """I `DamageEvent` dell'esito sui bersagli il cui id comincia per `prefix`."""
    return [event for event in outcome.damage_events if event.target_id.startswith(prefix)]


def _area_run(session_id: str, variant: str, rounds: int = ROUNDS):
    art = F.build_force('Red-Art', 'Red', [F.Unit('vehicle', '2S19-Msta', 1, origin=(-15_000.0, 0.0), prefix='art')])
    stay = F.build_force('Blue-Stay', 'Blue', [F.Unit('vehicle', 'BMP-2', 2, origin=(0.0, 0.0), step=(0.0, 80.0),
                                                    prefix='ifv')])
    col = F.build_force('Blue-Col', 'Blue', [F.Unit('vehicle', 'BMP-2', 4, origin=(0.0, -100.0), step=(0.0, -50.0),
                                                  prefix='ifv')])
    target = Target(kind=TargetKind.POINT, position=Point3D(AIM[0], AIM[1], 0.0),
                    provenance=TargetProvenance.ESTIMATED, estimated_at=-1_800.0, uncertainty_m=200.0)
    fire = MissionAction(kind=ActionKind.TASK, name=FIRE_AT_POINT_ACTION, params={'rounds': rounds},
                         start=StartCondition.at_time(FIRE_TIME))
    missions = F.missions_for(art, [(-14_500.0, 0.0)], mission_type='Fire_Support', target=target,
                              actions={1: [fire]})

    if variant != 'on_target':
        missions += F.missions_for(col, [(3_000.0, -100.0)], mission_type='Movement',
                                   target=F.zone_target((3_000.0, 0.0), 500.0))

    with patch.object(SS, 'F7_AREA_FIRE', variant != 'switch_off'):
        return F.run(session_id, [art], [stay, col], make_registry_fire_control(), duration=AREA_DURATION,
                     missions=missions)


class TestS29AreaFire(F.LoggerSilencer, unittest.TestCase):
    """S29-AREA: il fuoco su posizione colpisce chi e' nel disco di dispersione all'impatto, non chi c'era."""

    SEEDS = _seeds('S29-AREA')
    VARIANTS = VARIANTS

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                cls.runs[variant].append(_area_run(session_id, variant))

    def test_switch_off_nobody_is_hit_premise(self):
        """Premessa: senza l'evento nessuno e' colpito e la scorta non si consuma (nessun contatto, nessun ingaggio)."""
        for outcome in self.runs['switch_off']:
            with self.subTest(session=outcome.session_id):
                self.assertEqual(outcome.damage_events, ())
                self.assertEqual(outcome.ammunition_events, ())
                self.assertEqual(outcome.engagement_outcomes, ())

    def test_stale_hits_the_units_staying_at_the_point_and_misses_the_ones_that_left(self):
        for outcome in self.runs['stale']:
            with self.subTest(session=outcome.session_id):
                self.assertEqual(_hits(outcome, 'Blue-Col'), [])

        self.assertGreater(sum(len(_hits(outcome, 'Blue-Stay')) for outcome in self.runs['stale']), 0)

    def test_on_target_hits_the_column_still_at_the_point(self):
        self.assertGreater(sum(len(_hits(outcome, 'Blue-Col')) for outcome in self.runs['on_target']), 0)

    def test_the_event_carries_the_declared_instants_and_the_whole_salvo(self):
        """Munizioni a `t_fire` (l'azione AT_TIME 600 s, dopo l'arrivo al waypoint), danni all'impatto, 40 colpi pagati
        alla scorta, nessuna salva ne' forza d'ingaggio fuori dall'evento."""
        for outcome in self.runs['stale']:
            with self.subTest(session=outcome.session_id):
                self.assertEqual(len(outcome.ammunition_events), 1)
                ammunition = outcome.ammunition_events[0]
                self.assertEqual((ammunition.time, ammunition.asset_id, ammunition.weapon, ammunition.rounds),
                                 (FIRE_TIME, SHOOTER, '2A64-152mm', ROUNDS))
                # Tutti i danni allo stesso istante d'impatto, dopo il tiro (ci puo' essere nessun colpo a segno).
                impacts = {event.time for event in outcome.damage_events}
                self.assertLessEqual(len(impacts), 1)
                self.assertTrue(all(impact > FIRE_TIME for impact in impacts))
                self.assertTrue(all(event.source_id == SHOOTER and event.weapon == '2A64-152mm'
                                    for event in outcome.damage_events))
                self.assertEqual(outcome.engagement_outcomes, ((),))

    def test_the_shooter_stock_is_consumed(self):
        """La scorta dell'artiglieria cala dei colpi sparati: lo stato reale dell'asset e' stato mutato."""
        art = F.build_force('Red-Art', 'Red', [F.Unit('vehicle', '2S19-Msta', 1, origin=(-15_000.0, 0.0), prefix='art')])
        before = art.assets[SHOOTER].stock_of('2A64-152mm')
        stay = F.build_force('Blue-Stay', 'Blue', [F.Unit('vehicle', 'BMP-2', 1, origin=(0.0, 0.0), prefix='ifv')])
        target = Target(kind=TargetKind.POINT, position=Point3D(0.0, 0.0, 0.0))
        fire = MissionAction(kind=ActionKind.TASK, name=FIRE_AT_POINT_ACTION, params={'rounds': 7})
        missions = F.missions_for(art, [(-14_500.0, 0.0)], mission_type='Fire_Support', target=target,
                                  actions={1: [fire]})
        F.run('S29-STOCK', [art], [stay], make_registry_fire_control(), duration=AREA_DURATION, missions=missions)
        self.assertEqual(art.assets[SHOOTER].stock_of('2A64-152mm'), before - 7)

    def test_a_replay_with_the_same_session_id_is_identical(self):
        first = _area_run('S29-AREA-0', 'stale')
        second = _area_run('S29-AREA-0', 'stale')
        self.assertEqual(first.damage_events, second.damage_events)
        self.assertEqual(first.ammunition_events, second.ammunition_events)

    def test_the_session_seed_changes_the_impacts(self):
        """Stesso scenario, session_id diverso: gli impatti (stream di `Session_Rng` per missione ed evento)
        cambiano; non e' un test del numero ma dell'uso dello stream."""
        outcomes = [outcome for outcome in self.runs['on_target']]
        signatures = {tuple((event.target_id, event.outcome) for event in outcome.damage_events) for outcome in outcomes}
        self.assertGreater(len(signatures), 1)


if __name__ == '__main__':
    unittest.main()
