"""Scenario S34-BAND: quota nel volume d'ingaggio (VA, sfera ∩ fascia nel tempo).

Prosegue S32 (`Test_Session_Scenarios_S32.py`) con la stessa disciplina: si verifica un comportamento
QUALITATIVO o STRUTTURALE (relazioni fra varianti), mai un numero calibrato. Nel piano
(`Analysis/Document/Proposta_Allineamento_Volumi_DES_Pianificatore.md`, blocco 2): con l'interruttore
`Engagement_Resolver.VA_ENGAGEMENT_ALTITUDE_BAND` acceso il volume d'ingaggio dell'arma contraerea e' la
SFERA di portata 3D ∩ FASCIA di quota relativa al tiratore, valutata nel tempo, e la fire control sceglie
l'arma con le quote dell'istante della decisione (VA-2 (d)); un bersaglio fuori fascia all'istante ma che vi
entrera' piu' tardi non esaurisce il candidato: la decisione si rinvia (VA-2.1 (i)). Spento, il filtro di
quota resta STATICO sulla posizione di partenza degli asset.

## S34-BAND (`TestS34AltitudeBand`)

Geometria di S19/S32 (linea Red di 3 BMP-2 e un 9A33-Osa in (1000, -300), 4 A-10C `Maverick/Gun CAS` da
(-40 km, 0, z0) con passo (0, 500), bersaglio ristretto ai BMP-2 (ROE `only_designated`), `BOTH_HOLD`,
fire control dei registri). L'Osa ha il 9M33 (portata 10 km, fascia 25-5000 m relativa) e un radar di 30 km.
QUOTE E POSIZIONI SONO GEOMETRIA DI TEST, non dati tarati: servono a far attraversare all'A-10C la fascia
dell'Osa in tempi diversi, non a riprodurre una tattica reale.

| Variante          | Interruttore | Profilo dell'A-10C                            | Atteso (Osa)                              |
|-------------------|--------------|-----------------------------------------------|-------------------------------------------|
| `level_off/on`    | spento/acceso| quota costante 3000 m                         | salve in fascia, identiche                |
| `climb_off/on`    | spento/acceso| 3000 -> 6000 m (prima della sfera)            | off: salve sopra la fascia; on: nessuna   |
| `descend_off/on`  | spento/acceso| 6000 -> 3000 m (prima del rilevamento)        | off: nessuna; on: salve in fascia         |
| `late_descend_off/on` | spento/acceso | 6000 m fino a 12 km, poi 3000 m           | off: nessuna; on: salve dopo il rinvio    |

8 varianti, 4 seed ciascuna (nomi stabili nella fotografia, nell'ordine; stesso `session_id` per le 8
varianti di un seed).
"""

import sys
import unittest
from unittest.mock import patch

from Code.Dynamic_War_Manager.Source.Command.Mission_Types import MissionRules, Target, TargetKind, TargetProvenance
from Code.Dynamic_War_Manager.Source.Logic import Contact_Scheduler
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic.Fire_Control import make_registry_fire_control
from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F
from Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S10_S18 import BOTH_HOLD
from Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S19_Air_Defence import (
    DURATION, IFV_IDS, MAVERICK, VISUAL)

# Modulo che contiene davvero il risolutore: e' li' che `_EngagementRun.__init__` legge
# VA_ENGAGEMENT_ALTITUDE_BAND una volta (i test lo sostituiscono nel modulo).
ER_MODULE = sys.modules[ER.__name__]

SEEDS_PER_SCENARIO = 4
SEEDS = [f'S34-BAND-{index}' for index in range(SEEDS_PER_SCENARIO)]
OSA = 'Red-Line/ad0'
OSA_POSITION = (1_000.0, -300.0, 0.0)          # l'Osa e' un veicolo fermo a terra (z = 0)

# Dati del 9M33-SAM dal registro (Asset/Ground_Weapon_Data.py, record '9M33-SAM'), usati come lettura di
# geometria nei controlli di fascia e distanza delle salve.
MISSILE = '9M33-SAM'
BAND_MIN_M = 25.0
BAND_MAX_M = 5_000.0
RANGE_3D_M = 10_000.0

# profilo -> (quota di partenza z0 [m], punti della rotta (x, y, z)). Geometria di TEST, non dati.
PROFILES = {
    'level':        (3_000.0, [(20_000.0, 0.0, 3_000.0)]),
    'climb':        (3_000.0, [(-20_000.0, 0.0, 6_000.0), (20_000.0, 0.0, 6_000.0)]),
    'descend':      (6_000.0, [(-20_000.0, 0.0, 3_000.0), (20_000.0, 0.0, 3_000.0)]),
    'late_descend': (6_000.0, [(-12_000.0, 0.0, 6_000.0), (-6_000.0, 0.0, 3_000.0), (20_000.0, 0.0, 3_000.0)]),
}
# variante -> (profilo, VA_ENGAGEMENT_ALTITUDE_BAND)
VARIANT_SPEC = {
    'level_off': ('level', False), 'level_on': ('level', True),
    'climb_off': ('climb', False), 'climb_on': ('climb', True),
    'descend_off': ('descend', False), 'descend_on': ('descend', True),
    'late_descend_off': ('late_descend', False), 'late_descend_on': ('late_descend', True),
}
VARIANTS = tuple(VARIANT_SPEC)


def build(z0: float):
    """Linea Red (3 BMP-2, un 9A33-Osa) e 4 A-10C alla quota di partenza `z0` (come S19, con l'Osa)."""
    red = F.build_force('Red-Line', 'Red', [
        F.Unit('vehicle', 'BMP-2', 3, origin=(0.0, 0.0), step=(0.0, 300.0), prefix='ifv', sensors=VISUAL),
        F.Unit('vehicle', '9A33-Osa', 1, origin=(1_000.0, -300.0), prefix='ad')])
    cas = F.build_force('Blue-CAS', 'Blue', [
        F.Unit('aircraft', 'A-10C Thunderbolt II', 4, origin=(-40_000.0, 0.0, z0),
               step=(0.0, 500.0), prefix='cas', loadout='Maverick/Gun CAS')], mil_category=F.AIR_UNIT)
    return red, cas


def run_variant(session_id: str, variant: str):
    """Una sessione della variante: `(outcome, [EngagementResult, ...], {asset_id: Route})`.

    L'interruttore e' sostituito attorno all'intera esecuzione; i risultati d'ingaggio (salve e
    rilevamenti) sono catturati con una spia che chiama l'originale (come S32); le rotte servono a
    ricavare la quota del bersaglio all'istante di lancio/rilevamento."""
    profile, switch = VARIANT_SPEC[variant]
    z0, points = PROFILES[profile]
    original = ER.resolve_engagement
    captured = []

    def spy(*args, **kwargs):
        result = original(*args, **kwargs)
        captured.append(result)
        return result

    with patch.object(ER_MODULE, 'VA_ENGAGEMENT_ALTITUDE_BAND', switch):
        red, cas = build(z0)
        target = Target(kind=TargetKind.GROUP, target_id='Red-Line', asset_ids=IFV_IDS,
                        provenance=TargetProvenance.OBSERVED, observed_at=0.0)
        missions = F.missions_for(cas, points, mission_type='CAS', target=target, weapons=(MAVERICK,),
                                  rules=MissionRules(roe='only_designated'))
        routes = F.mission_routes(missions)

        with patch.object(ER, 'resolve_engagement', side_effect=spy):
            outcome = F.run(session_id, [cas], [red], make_registry_fire_control(), duration=DURATION,
                            missions=missions, thresholds=BOTH_HOLD)

    return outcome, [result for result in captured if result is not None], routes


def _ammunition(outcome):
    return [(e.asset_id, e.weapon, e.rounds, e.time) for e in outcome.ammunition_events]


def _damage(outcome):
    return [(e.target_id, e.source_id, e.weapon, e.outcome, e.time, e.health_after) for e in outcome.damage_events]


def _detections(results, observer_id):
    return [d for result in results for d in result.detections if d.observer_id == observer_id]


def _salvos(results, shooter_id):
    return [salvo for result in results for salvo in result.salvos if salvo.shooter_id == shooter_id]


def _target_position(routes, target_id, t):
    """Posizione (x, y, z) del bersaglio all'istante `t` dai tratti della sua rotta (None senza rotta)."""
    route = routes.get(target_id)
    if route is None:
        return None
    return Contact_Scheduler.position_on_legs(Contact_Scheduler.route_legs(route), t)


def _relative_altitude(routes, target_id, t):
    """Quota del bersaglio RELATIVA all'Osa all'istante `t` (l'Osa e' ferma a z = 0)."""
    position = _target_position(routes, target_id, t)
    if position is None:
        return None
    return position[2] - OSA_POSITION[2]


def _distance_3d(routes, target_id, t):
    """Distanza 3D [m] fra il bersaglio all'istante `t` e l'Osa."""
    position = _target_position(routes, target_id, t)
    if position is None:
        return None
    return ((position[0] - OSA_POSITION[0]) ** 2
            + (position[1] - OSA_POSITION[1]) ** 2
            + (position[2] - OSA_POSITION[2]) ** 2) ** 0.5


class TestS34AltitudeBand(F.LoggerSilencer, unittest.TestCase):
    """S34-BAND: con l'interruttore acceso l'Osa ingaggia solo dentro la fascia di quota (25-5000 m)."""

    SEEDS = SEEDS
    VARIANTS = VARIANTS

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        # Ciclo esterno sui seed, interno sulle varianti: stesso `session_id` per le 8 varianti di un seed
        # (la fotografia numera le esecuzioni per occorrenza del session_id nell'unita').
        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                cls.runs[variant].append(run_variant(session_id, variant))

    def test_climb_off_osa_fires_above_the_band(self):
        """Spento: il filtro statico (quota di partenza 3000 m) sceglie il 9M33 e l'Osa spara a 6000 m,
        sopra la fascia; ogni salva ha il bersaglio a quota relativa > 5000 m; almeno 3 semi su 4."""
        seeds_with_salvos = 0

        for seed, (outcome, results, routes) in zip(self.SEEDS, self.runs['climb_off']):
            with self.subTest(session=seed):
                osa_salvos = _salvos(results, OSA)
                seeds_with_salvos += 1 if osa_salvos else 0

                for salvo in osa_salvos:
                    altitude = _relative_altitude(routes, salvo.target_id, salvo.t_launch)
                    self.assertGreater(altitude, BAND_MAX_M)

        self.assertGreaterEqual(seeds_with_salvos, 3)

    def test_climb_on_osa_never_fires(self):
        """Acceso: all'istante della decisione l'A-10C e' a 6000 m e sfera ∩ fascia e' vuota: nessuna salva."""
        for seed, (outcome, results, routes) in zip(self.SEEDS, self.runs['climb_on']):
            with self.subTest(session=seed):
                self.assertEqual(_salvos(results, OSA), [])

    def test_level_switch_does_not_change_the_events(self):
        """Sempre in fascia (3000 m): spento e acceso danno gli stessi eventi di munizioni e di danno."""
        for seed, (off, _, _), (on, _, _) in zip(self.SEEDS, self.runs['level_off'], self.runs['level_on']):
            with self.subTest(session=seed):
                self.assertEqual(_ammunition(on), _ammunition(off))
                self.assertEqual(_damage(on), _damage(off))

    def test_descend_off_osa_never_fires(self):
        """Spento: il filtro statico (quota di partenza 6000 m) esclude il 9M33: nessuna salva."""
        for seed, (outcome, results, routes) in zip(self.SEEDS, self.runs['descend_off']):
            with self.subTest(session=seed):
                self.assertEqual(_salvos(results, OSA), [])

    def test_descend_on_osa_fires_in_band(self):
        """Acceso: alla decisione l'A-10C e' gia' sceso in fascia (la discesa finisce prima del
        rilevamento): salve in fascia ed entro la portata; almeno 3 semi su 4."""
        seeds_with_salvos = 0

        for seed, (outcome, results, routes) in zip(self.SEEDS, self.runs['descend_on']):
            with self.subTest(session=seed):
                osa_salvos = _salvos(results, OSA)
                seeds_with_salvos += 1 if osa_salvos else 0

                for salvo in osa_salvos:
                    altitude = _relative_altitude(routes, salvo.target_id, salvo.t_launch)
                    distance = _distance_3d(routes, salvo.target_id, salvo.t_launch)
                    self.assertGreaterEqual(altitude, BAND_MIN_M)
                    self.assertLessEqual(altitude, BAND_MAX_M)
                    self.assertLessEqual(distance, RANGE_3D_M + 1e-6)

        self.assertGreaterEqual(seeds_with_salvos, 3)

    def test_late_descend_off_osa_never_fires(self):
        """Spento: quota di partenza 6000 m esclusa dal filtro statico: nessuna salva."""
        for seed, (outcome, results, routes) in zip(self.SEEDS, self.runs['late_descend_off']):
            with self.subTest(session=seed):
                self.assertEqual(_salvos(results, OSA), [])

    def test_late_descend_on_osa_fires_after_the_deferral(self):
        """Acceso: alla decisione l'A-10C e' a 6000 m (fuori fascia), ma il rinvio VA-2.1 porta il tiro
        all'ingresso in sfera ∩ fascia: salve sotto i 5000 m ed entro la portata; almeno 3 semi su 4."""
        seeds_with_salvos = 0

        for seed, (outcome, results, routes) in zip(self.SEEDS, self.runs['late_descend_on']):
            with self.subTest(session=seed):
                osa_salvos = _salvos(results, OSA)
                seeds_with_salvos += 1 if osa_salvos else 0

                for salvo in osa_salvos:
                    altitude = _relative_altitude(routes, salvo.target_id, salvo.t_launch)
                    distance = _distance_3d(routes, salvo.target_id, salvo.t_launch)
                    self.assertLessEqual(altitude, BAND_MAX_M)
                    self.assertLessEqual(distance, RANGE_3D_M + 1e-6)

        self.assertGreaterEqual(seeds_with_salvos, 3)

    def test_late_descend_on_is_reproducible(self):
        """Determinismo: rieseguire la stessa variante (primo seed) da' gli stessi eventi."""
        rerun = run_variant(self.SEEDS[0], 'late_descend_on')
        self.assertEqual(_ammunition(rerun[0]), _ammunition(self.runs['late_descend_on'][0][0]))
        self.assertEqual(_damage(rerun[0]), _damage(self.runs['late_descend_on'][0][0]))

    def test_level_engagement_stream_is_unchanged_by_the_switch(self):
        """In `level` lo stream dei rilevamenti (osservatore, estrazione, esito) non cambia con
        l'interruttore: spento e acceso hanno gli stessi `Detection`."""
        for seed, (_, off_results, _), (_, on_results, _) in zip(self.SEEDS, self.runs['level_off'],
                                                                 self.runs['level_on']):
            with self.subTest(session=seed):
                off = [(d.observer_id, d.draw, d.detected) for r in off_results for d in r.detections]
                on = [(d.observer_id, d.draw, d.detected) for r in on_results for d in r.detections]
                self.assertEqual(on, off)


if __name__ == '__main__':
    unittest.main()
