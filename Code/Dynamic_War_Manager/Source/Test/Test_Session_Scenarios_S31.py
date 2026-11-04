"""Scenario S31 del motore di sessioni virtuali: sensore visivo di ripiego di ZSU-57-2 e M163-VADS (D-4c).

Prosegue S19AD (`Test_Session_Scenarios_S19_Air_Defence.py`) con la stessa disciplina: si verifica un comportamento
QUALITATIVO o STRUTTURALE, mai un numero calibrato. Nel codice (`Analysis/Document/Proposta_Dati_Sensori_EWR_Visivo.md`,
blocco A): i due mezzi hanno `radar` e `TVD` False; prima della D-4c `detection_range` era None e il DES non li faceva
mai sparare a un aereo (`_detect_direction` esce prima dell'estrazione se l'osservatore non ha portata). Ora il campo
`visual` del registro (scoperta a occhio dell'equipaggio, `acquisition_range` aria 6 km: STIMA, confidenza bassa) entra in
`Mobile.detection_range` come terzo sensore, dietro l'interruttore `Mobile.D4C_VISUAL_SENSOR`.

## S31-VISUAL (`TestS31VisualSensor`)

Geometria di S19AD: linea Red di 3 BMP-2 con sensore dichiarato visivo a terra (4 km) in (0, 0), una difesa aerea in
(1000, -300), 4 A-10C `Maverick/Gun CAS` da (-40 km, 0) con rotta di sorvolo, bersaglio ristretto ai 3 BMP-2 (ROE
`only_designated`), `BOTH_HOLD`. Cinque varianti, 4 seed ciascuna (nomi stabili nella fotografia, nell'ordine; stesso
`session_id` per le 5 varianti di un seed):
  * 'zsu': ZSU-57-2, A-10C a 3000 m, interruttore acceso: la ZSU vede a 6 km e spara (cannone da 57 mm, quota fino a
    4000 m);
  * 'zsu_off': come 'zsu' con `D4C_VISUAL_SENSOR` spento (premessa: il comportamento precedente, nessun colpo);
  * 'vads_low': M163-VADS, A-10C a 500 m, interruttore acceso: il Vulcan da 20 mm (quota fino a 1000 m) spara;
  * 'vads_low_off': come 'vads_low' con l'interruttore spento (nessun colpo);
  * 'vads_high': M163-VADS, A-10C a 3000 m, interruttore acceso: il sensore vede a 6 km ma l'arma arriva a 1000 m di
    quota, quindi nessun colpo. Rilevamento NON e' intercettazione.

`TestS31VisualSensorRanges` e' unitaria (nessuna sessione) e NON sta nella fotografia.
"""

import sys
import unittest
from unittest.mock import patch

from Code.Dynamic_War_Manager.Source.Asset.Mobile import Mobile
from Code.Dynamic_War_Manager.Source.Command.Mission_Types import MissionRules, Target, TargetKind, TargetProvenance
from Code.Dynamic_War_Manager.Source.Logic import Contact_Scheduler
from Code.Dynamic_War_Manager.Source.Logic.Fire_Control import make_registry_fire_control
from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F
from Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S10_S18 import BOTH_HOLD
from Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S19_Air_Defence import (
    DURATION, IFV_IDS, MAVERICK, OVERFLIGHT, VISUAL)

# Modulo che contiene davvero Mobile: e' li' che `detection_range` legge D4C_VISUAL_SENSOR a ogni chiamata.
MOBILE_MODULE = sys.modules[Mobile.__module__]

SEEDS_PER_SCENARIO = 4
SEEDS = [f'S31-VISUAL-{index}' for index in range(SEEDS_PER_SCENARIO)]
# variante -> (modello della difesa, quota degli A-10C [m], interruttore D4C_VISUAL_SENSOR)
VARIANT_SPEC = {
    'zsu': ('ZSU-57-2', 3_000.0, True),
    'zsu_off': ('ZSU-57-2', 3_000.0, False),
    'vads_low': ('M163-VADS', 500.0, True),
    'vads_low_off': ('M163-VADS', 500.0, False),
    'vads_high': ('M163-VADS', 3_000.0, True),
}
VARIANTS = tuple(VARIANT_SPEC)
DEFENCE = 'Red-Line/ad0'
DEFENCE_POSITION = (1_000.0, -300.0)


def build(defence_model: str, altitude: float):
    """Linea Red (3 BMP-2 + la difesa) e 4 A-10C a quota `altitude`: come `S19.build`, con la quota variabile."""
    red = F.build_force('Red-Line', 'Red', [
        F.Unit('vehicle', 'BMP-2', 3, origin=(0.0, 0.0), step=(0.0, 300.0), prefix='ifv', sensors=VISUAL),
        F.Unit('vehicle', defence_model, 1, origin=DEFENCE_POSITION, prefix='ad')])
    cas = F.build_force('Blue-CAS', 'Blue', [
        F.Unit('aircraft', 'A-10C Thunderbolt II', 4, origin=(-40_000.0, 0.0, altitude),
               step=(0.0, 500.0), prefix='cas', loadout='Maverick/Gun CAS')], mil_category=F.AIR_UNIT)
    return red, cas


def run_variant(session_id: str, variant: str):
    """Una sessione della variante: `(red, cas, outcome)`. L'interruttore e' sostituito attorno all'intera esecuzione."""
    defence_model, altitude, switch = VARIANT_SPEC[variant]

    with patch.object(MOBILE_MODULE, 'D4C_VISUAL_SENSOR', switch):
        red, cas = build(defence_model, altitude)
        target = Target(kind=TargetKind.GROUP, target_id='Red-Line', asset_ids=IFV_IDS,
                        provenance=TargetProvenance.OBSERVED, observed_at=0.0)
        missions = F.missions_for(cas, OVERFLIGHT, mission_type='CAS', target=target, weapons=(MAVERICK,),
                                  rules=MissionRules(roe='only_designated'))
        outcome = F.run(session_id, [cas], [red], make_registry_fire_control(), duration=DURATION,
                        missions=missions, thresholds=BOTH_HOLD)

    return red, cas, outcome


def _defence_events(outcome):
    return [event for event in outcome.ammunition_events if event.asset_id == DEFENCE]


def _defence_rounds(outcome) -> int:
    return sum(event.rounds for event in _defence_events(outcome))


class TestS31VisualSensorRanges(F.LoggerSilencer, unittest.TestCase):
    """Unitaria, fuori dalla fotografia: la portata con cui la ZSU-57-2 vede un A-10C."""

    def test_mutual_detection_ranges_with_the_visual_sensor(self):
        red = F.build_force('Red-Line', 'Red', [F.Unit('vehicle', 'ZSU-57-2', 1, origin=DEFENCE_POSITION, prefix='ad')])
        cas = F.build_force('Blue-CAS', 'Blue', [
            F.Unit('aircraft', 'A-10C Thunderbolt II', 1, origin=(-40_000.0, 0.0, 3_000.0), prefix='cas',
                   loadout='Maverick/Gun CAS')], mil_category=F.AIR_UNIT)
        zsu, a10 = red.assets[DEFENCE], cas.assets['Blue-CAS/cas0']

        self.assertEqual(Contact_Scheduler.mutual_detection_ranges(zsu, a10)[0], 6_000.0)

        with patch.object(MOBILE_MODULE, 'D4C_VISUAL_SENSOR', False):
            self.assertIsNone(Contact_Scheduler.mutual_detection_ranges(zsu, a10)[0])


class TestS31VisualSensor(F.LoggerSilencer, unittest.TestCase):
    """S31-VISUAL: il sensore visivo fa sparare ZSU-57-2 e M163-VADS agli aerei, entro la portata dell'arma."""

    SEEDS = SEEDS
    VARIANTS = VARIANTS

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        # Ciclo esterno sui seed, interno sulle varianti: stesso `session_id` per le 5 varianti di un seed
        # (la fotografia numera le esecuzioni per occorrenza del session_id nell'unita').
        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                cls.runs[variant].append(run_variant(session_id, variant)[2])

    def test_mavericks_are_launched(self):
        """Premessa non vacua: in ogni variante e seme gli A-10C lanciano Maverick."""
        for variant in self.VARIANTS:
            for seed, outcome in zip(self.SEEDS, self.runs[variant]):
                with self.subTest(variant=variant, session=seed):
                    launched = sum(e.rounds for e in outcome.ammunition_events if e.weapon == MAVERICK)
                    self.assertGreater(launched, 0)

    def test_without_the_visual_sensor_the_aaa_never_fires(self):
        """Comportamento precedente (interruttore spento): senza portata propria la difesa non spara mai."""
        for variant in ('zsu_off', 'vads_low_off'):
            for seed, outcome in zip(self.SEEDS, self.runs[variant]):
                with self.subTest(variant=variant, session=seed):
                    self.assertEqual(_defence_rounds(outcome), 0)

    def test_zsu_with_the_visual_sensor_fires(self):
        events = [e for outcome in self.runs['zsu'] for e in _defence_events(outcome)]
        self.assertGreater(sum(e.rounds for e in events), 0)
        self.assertEqual({e.weapon for e in events}, {'S-68-57mm'})

    def test_vads_with_the_visual_sensor_fires_at_low_altitude(self):
        events = [e for outcome in self.runs['vads_low'] for e in _defence_events(outcome)]
        self.assertGreater(sum(e.rounds for e in events), 0)
        self.assertEqual({e.weapon for e in events}, {'M61-Vulcan-20mm'})

    def test_vads_sees_but_cannot_reach_aircraft_at_3000_m(self):
        """Il sensore vede a 6 km, l'arma arriva a 1000 m di quota: rilevamento != intercettazione."""
        for seed, outcome in zip(self.SEEDS, self.runs['vads_high']):
            with self.subTest(session=seed):
                self.assertEqual(_defence_rounds(outcome), 0)


if __name__ == '__main__':
    unittest.main()
