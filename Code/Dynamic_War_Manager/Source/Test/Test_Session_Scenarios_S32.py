"""Scenario S32 del motore di sessioni virtuali: Pd dipendente dalla permanenza nel volume (D-5, `dwell_time_s`).

Prosegue S31 (`Test_Session_Scenarios_S31.py`) con la stessa disciplina: si verifica un comportamento QUALITATIVO o
STRUTTURALE (relazioni fra varianti), mai un numero calibrato. Nel codice (`Analysis/Document/
Proposta_Dwell_Time_Rilevamento.md`, blocco A): con l'interruttore `Engagement_Resolver.D5_DWELL_TIME` acceso,
`Session_Simulator` passa al risolutore il lettore `registry_dwell_time`; per un osservatore che dichiara un periodo di
rivisita (`dwell_time_s` del sensore) la Pd e' moltiplicata per `min(1, permanenza / dwell)` (`dwell_factor`), dove la
permanenza e' il tempo del bersaglio nella portata propria dell'osservatore (`_EngagementRun._exposure_time`). Spento,
la legge e' quella di sola distanza di prima.

## S32-DWELL (`TestS32DwellTime`)

Geometria di S31 'zsu' (linea Red di 3 BMP-2 con sensore dichiarato visivo a terra (4 km) in (0, 0), una ZSU-57-2 in
(1000, -300), 4 A-10C `Maverick/Gun CAS` da (-40 km, 0) a 3000 m con rotta di sorvolo, bersaglio ristretto ai BMP-2
(ROE `only_designated`), `BOTH_HOLD`). Cinque varianti, 4 seed ciascuna (nomi stabili nella fotografia, nell'ordine;
stesso `session_id` per le 5 varianti di un seed):

| Variante  | Interruttore | dwell della ZSU (dichiarato di test) | Con P-18 | Cosa prova                                    |
|-----------|--------------|--------------------------------------|----------|-----------------------------------------------|
| `off`     | spento       | -                                    | no       | riferimento (legge di sola distanza)          |
| `long`    | acceso       | 30 s (permanenza 62-67 s: `g` = 1)   | no       | riduzione esatta alla legge di prima          |
| `short`   | acceso       | 600 s (`g` ~0,10-0,11)               | no       | Pd ridotta: rilevamenti della ZSU in meno     |
| `ewr_off` | spento       | -                                    | si'      | riferimento con EWR                           |
| `ewr_on`  | acceso       | - (P-18: dato di fonte 6 s)          | si'      | con permanenza di minuti nulla cambia         |

30 s e 600 s sono periodi di rivisita DICHIARATI DI TEST sulla ZSU-57-2, non dati: il visivo non ha dati di scansione;
il P-18 usa il dato di fonte del registro (6 s).
"""

import sys
import unittest
from unittest.mock import patch

from Code.Dynamic_War_Manager.Source.Command.Mission_Types import MissionRules, Target, TargetKind, TargetProvenance
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic.Fire_Control import make_registry_fire_control
from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F
from Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S10_S18 import BOTH_HOLD
from Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S19_Air_Defence import (
    DURATION, IFV_IDS, MAVERICK, OVERFLIGHT, VISUAL)

# Modulo che contiene davvero il risolutore: e' li' che `Session_Simulator.engage` legge D5_DWELL_TIME a ogni chiamata.
ER_MODULE = sys.modules[ER.__name__]

SEEDS_PER_SCENARIO = 4
SEEDS = [f'S32-DWELL-{index}' for index in range(SEEDS_PER_SCENARIO)]
# variante -> (dwell dichiarato di test sulla ZSU [s] | None, interruttore D5_DWELL_TIME, con P-18)
VARIANT_SPEC = {
    'off': (None, False, False),
    'long': (30.0, True, False),
    'short': (600.0, True, False),
    'ewr_off': (None, False, True),
    'ewr_on': (None, True, True),
}
VARIANTS = tuple(VARIANT_SPEC)
ZSU = 'Red-Line/ad0'
EWR = 'Red-Line/ewr0'
ZSU_POSITION = (1_000.0, -300.0)
EWR_POSITION = (30_000.0, 0.0)

# Periodi di rivisita DICHIARATI DI TEST [s] sulla ZSU-57-2 (NON dati: v. docstring del modulo).
LONG_DWELL_S = 30.0
SHORT_DWELL_S = 600.0
EWR_SOURCE_DWELL_S = 6.0     # dato di fonte del registro (P-18-Terek, 10 giri/min)


def build(with_ewr: bool):
    """Linea Red (3 BMP-2, la ZSU-57-2 ed eventualmente un P-18-Terek) e 4 A-10C a 3000 m (come S31 'zsu')."""
    units = [
        F.Unit('vehicle', 'BMP-2', 3, origin=(0.0, 0.0), step=(0.0, 300.0), prefix='ifv', sensors=VISUAL),
        F.Unit('vehicle', 'ZSU-57-2', 1, origin=ZSU_POSITION, prefix='ad')]

    if with_ewr:
        units.append(F.Unit('vehicle', 'P-18-Terek', 1, origin=EWR_POSITION, prefix='ewr'))

    red = F.build_force('Red-Line', 'Red', units)
    cas = F.build_force('Blue-CAS', 'Blue', [
        F.Unit('aircraft', 'A-10C Thunderbolt II', 4, origin=(-40_000.0, 0.0, 3_000.0),
               step=(0.0, 500.0), prefix='cas', loadout='Maverick/Gun CAS')], mil_category=F.AIR_UNIT)
    return red, cas


def run_variant(session_id: str, variant: str):
    """Una sessione della variante: `(outcome, [EngagementResult, ...])`. L'interruttore e' sostituito attorno
    all'intera esecuzione; i risultati d'ingaggio sono catturati con una spia che chiama l'originale (come S9)."""
    dwell, switch, with_ewr = VARIANT_SPEC[variant]
    original = ER.resolve_engagement
    captured = []

    def spy(*args, **kwargs):
        result = original(*args, **kwargs)
        captured.append(result)
        return result

    with patch.object(ER_MODULE, 'D5_DWELL_TIME', switch):
        red, cas = build(with_ewr)

        if dwell is not None:
            F.declare_dwell(red.assets[ZSU], {'air': dwell})

        target = Target(kind=TargetKind.GROUP, target_id='Red-Line', asset_ids=IFV_IDS,
                        provenance=TargetProvenance.OBSERVED, observed_at=0.0)
        missions = F.missions_for(cas, OVERFLIGHT, mission_type='CAS', target=target, weapons=(MAVERICK,),
                                  rules=MissionRules(roe='only_designated'))

        with patch.object(ER, 'resolve_engagement', side_effect=spy):
            outcome = F.run(session_id, [cas], [red], make_registry_fire_control(), duration=DURATION,
                            missions=missions, thresholds=BOTH_HOLD)

    return outcome, [result for result in captured if result is not None]


def _ammunition(outcome):
    return [(e.asset_id, e.weapon, e.rounds, e.time) for e in outcome.ammunition_events]


def _damage(outcome):
    return [(e.target_id, e.source_id, e.weapon, e.outcome, e.time, e.health_after) for e in outcome.damage_events]


def _detections(results, observer_id):
    return [d for result in results for d in result.detections if d.observer_id == observer_id]


class TestS32DwellTime(F.LoggerSilencer, unittest.TestCase):
    """S32-DWELL: la permanenza nel volume riduce la Pd solo se il sensore dichiara un periodo di rivisita."""

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
                cls.runs[variant].append(run_variant(session_id, variant))

    def test_premise_the_zsu_fires_with_the_previous_law(self):
        """Premessa non vacua: in `off` la ZSU spara in almeno un seed."""
        rounds = sum(e.rounds for outcome, _ in self.runs['off'] for e in outcome.ammunition_events
                     if e.asset_id == ZSU)
        self.assertGreater(rounds, 0)

    def test_long_dwell_reproduces_the_previous_law(self):
        """Permanenza >= periodo: g = 1, quindi stessi eventi di `off` (munizioni e danni, con istanti)."""
        for seed, (off, _), (long, results) in zip(self.SEEDS, self.runs['off'], self.runs['long']):
            with self.subTest(session=seed):
                self.assertEqual(_ammunition(long), _ammunition(off))
                self.assertEqual(_damage(long), _damage(off))

                zsu = _detections(results, ZSU)
                self.assertTrue(zsu)

                for detection in zsu:
                    self.assertEqual(detection.dwell_time_s, LONG_DWELL_S)
                    self.assertGreaterEqual(detection.exposure_s, LONG_DWELL_S)

    def test_short_dwell_never_adds_a_detection(self):
        """Nel PRIMO episodio (stesse finestre e stesso stream nelle due varianti, quindi stessa estrazione per
        direzione) i rilevamenti della ZSU in `short` sono un sottoinsieme di quelli di `off`. Gli episodi
        successivi possono avere finestre diverse (esiti diversi del primo): non si confrontano."""
        for seed, (_, off), (_, short) in zip(self.SEEDS, self.runs['off'], self.runs['short']):
            with self.subTest(session=seed):
                self.assertTrue(off and short)
                detected_off = {(d.observer_id, d.target_id) for d in _detections(off[:1], ZSU) if d.detected}
                detected_short = {(d.observer_id, d.target_id) for d in _detections(short[:1], ZSU) if d.detected}
                self.assertLessEqual(detected_short, detected_off)

    def test_short_dwell_reduces_the_aaa_detections(self):
        """Totale sui seed dei rilevamenti della ZSU: `short` < `off` (stretto)."""
        def total(variant):
            return sum(d.detected for _, results in self.runs[variant] for d in _detections(results, ZSU))

        self.assertLess(total('short'), total('off'))

    def test_short_dwell_probability_is_bounded_by_the_exposure(self):
        for seed, (_, results) in zip(self.SEEDS, self.runs['short']):
            with self.subTest(variant='short', session=seed):
                zsu = _detections(results, ZSU)
                self.assertTrue(zsu)

                for detection in zsu:
                    self.assertEqual(detection.dwell_time_s, SHORT_DWELL_S)
                    self.assertLess(detection.exposure_s, SHORT_DWELL_S)
                    self.assertLessEqual(detection.probability, detection.exposure_s / SHORT_DWELL_S + 1e-12)

        for seed, (_, results) in zip(self.SEEDS, self.runs['off']):
            with self.subTest(variant='off', session=seed):
                for detection in _detections(results, ZSU):
                    self.assertIsNone(detection.dwell_time_s)
                    self.assertIsNone(detection.exposure_s)

    def test_ewr_source_dwell_changes_nothing_at_medium_altitude(self):
        """Con il dato di fonte del P-18 (6 s) e una permanenza di minuti, g = 1: stessi eventi e stessa Pd."""
        for seed, (off, off_results), (on, on_results) in zip(self.SEEDS, self.runs['ewr_off'], self.runs['ewr_on']):
            with self.subTest(session=seed):
                self.assertEqual(_ammunition(on), _ammunition(off))

                ewr_off = _detections(off_results, EWR)
                ewr_on = _detections(on_results, EWR)
                self.assertTrue(ewr_on)
                self.assertEqual(len(ewr_on), len(ewr_off))

                for detection, reference in zip(ewr_on, ewr_off):
                    self.assertEqual(detection.dwell_time_s, EWR_SOURCE_DWELL_S)
                    self.assertGreaterEqual(detection.exposure_s, EWR_SOURCE_DWELL_S)
                    self.assertEqual(detection.probability, reference.probability)


if __name__ == '__main__':
    unittest.main()
