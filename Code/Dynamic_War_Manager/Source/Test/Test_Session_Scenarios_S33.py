"""Scenario S33 del motore di sessioni virtuali: rilevamento per passaggio nella portata propria (FP) e D-5.

Prosegue S32 (`Test_Session_Scenarios_S32.py`) con la stessa disciplina: si verifica un comportamento QUALITATIVO o
STRUTTURALE (relazioni fra varianti), mai un numero calibrato. Nel codice (`Analysis/Document/
Proposta_Finestre_Per_Passaggio_Portata_Propria.md`, blocco 2): con l'interruttore
`Engagement_Resolver.FP_PER_PASS_DETECTION` acceso il risolutore da' UNA occasione di rilevamento per OGNI passaggio
del bersaglio nel volume PROPRIO dell'osservatore (non una sola per finestra); con la D-5
(`D5_DWELL_TIME`) accesa e un `dwell_time_s` dichiarato dal sensore, la Pd di ogni passaggio e' moltiplicata per
`min(1, permanenza / dwell)`. Spenti, la legge e' quella di sola distanza di prima.

## S33-PASSES (`TestS33DetectionPerPass`)

Due geometrie (rientro e CAS), ciascuna con lo stato precedente (FP e D-5 spente, nessun dwell dichiarato) e la
configurazione finale (FP e D-5 accese, dwell della ZSU dichiarato). Quattro varianti, 5 seed ciascuna (nomi stabili
nella fotografia, nell'ordine; stesso `session_id` per le 4 varianti di un seed):

| Variante  | Geometria | FP + D-5 | dwell della ZSU (dichiarato) | Cosa prova                                             |
|-----------|-----------|----------|------------------------------|--------------------------------------------------------|
| `off`     | rientro   | spente   | -                            | riferimento: una sola estrazione per finestra          |
| `on`      | rientro   | accese   | 2 s [S]                      | due passaggi, due estrazioni; FP sola (g = 1)          |
| `cas_off` | CAS       | spente   | -                            | riferimento nella geometria CAS a piu' virate          |
| `cas_on`  | CAS       | accese   | 2 s [S]                      | due passaggi NON contigui; FP sola (g = 1)             |

Le varianti `off` e `cas_off` sono lo stato precedente: FP e D-5 spente, nessun dwell dichiarato. Le varianti `on` e
`cas_on` sono la configurazione finale: FP e D-5 accese, e la ZSU dichiara (`declare_dwell`, modo 'air') un periodo di
aggiornamento di 2 s, STIMA [S] dell'utente (2026-11-08: osservatore umano piu' ottica), non un dato. Con passaggi di
50-67 s il fattore di permanenza e' g = 1 e con uscite di 100-130 s l'unione dei passaggi (FP-10) non unisce: la D-5
non cambia ne' estrazioni ne' Pd; per questo non ci sono varianti con dwell lunghi.
"""

import copy
import math
import sys
import unittest
from unittest.mock import patch

from Code.Dynamic_War_Manager.Source.Command.Mission_Types import MissionRules, Target, TargetKind, TargetProvenance
from Code.Dynamic_War_Manager.Source.Logic import Contact_Scheduler as CS
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic.Fire_Control import make_registry_fire_control
from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F
from Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S10_S18 import BOTH_HOLD
from Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S19_Air_Defence import (
    DURATION, IFV_IDS, MAVERICK, VISUAL)
from Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S32 import (
    ER_MODULE, ZSU, ZSU_POSITION, build)

SEEDS = [f'S33-PASSES-{index}' for index in range(5)]
# variante -> (geometria, interruttori FP_PER_PASS_DETECTION e D5_DWELL_TIME, con il dwell ZSU_DWELL_S sulla ZSU)
VARIANT_SPEC = {
    'off': ('reentry', False),
    'on': ('reentry', True),
    'cas_off': ('cas', False),
    'cas_on': ('cas', True),
}
VARIANTS = tuple(VARIANT_SPEC)
CAS_IDS = tuple(f'Blue-CAS/cas{index}' for index in range(4))
# Andata sulla linea Red, uscita a 14 km, ritorno, uscita: due passaggi nei 6 km della ZSU (visivo, quota 3000 m),
# sempre entro gli 80 km dell'A-10C contro bersagli a terra (una sola finestra per coppia A-10C/ZSU).
REENTRY = [(0.0, 0.0), (-14_000.0, 0.0), (0.0, 0.0), (-30_000.0, 0.0)]
# CAS: tre BMP-2 attaccati in sequenza lungo la rotta; A e C dentro i 6 km della ZSU, B fuori (13 km). Punto sopra A,
# proseguimento fino a B, virata e ritorno sopra C, uscita a ovest: due passaggi NON contigui nel volume della ZSU,
# sempre entro gli 80 km dell'A-10C (una sola finestra per coppia A-10C/ZSU).
CAS_TARGETS = {'ifvA': (0.0, 0.0), 'ifvB': (14_000.0, 0.0), 'ifvC': (2_000.0, -3_000.0)}
CAS_TARGET_IDS = tuple(f'Red-Line/{prefix}0' for prefix in CAS_TARGETS)
CAS_ROUTE = [CAS_TARGETS['ifvA'], CAS_TARGETS['ifvB'], CAS_TARGETS['ifvC'], (-30_000.0, -3_000.0)]
ZSU_VISUAL_RANGE_M = 6_000.0     # portata del registro della ZSU-57-2 contro bersagli aerei (§1.4), per i test di premessa
A10_GROUND_RANGE_M = 80_000.0    # portata del registro dell'A-10C contro bersagli a terra (§1.4)
# STIMA [S] dell'utente (2026-11-08): periodo di aggiornamento della traccia della ZSU-57-2 (osservatore umano piu'
# ottica, "predizione" del cervello). NON e' un dato. Dichiarato sulla ZSU (F.declare_dwell, modo 'air') solo nelle
# varianti con FP e D-5 accese: soglia di unione FP-10 (le uscite fra i passaggi sono molto piu' lunghe: nessuna unione)
# e dwell della legge D-5 (passaggi molto piu' lunghi: g = 1).
ZSU_DWELL_S = 2.0


def build_cas():
    """Linea Red (3 BMP-2 singoli sui bersagli CAS e la ZSU-57-2) e 4 A-10C a 3000 m (come S32 `build`)."""
    red = F.build_force('Red-Line', 'Red', [
        F.Unit('vehicle', 'BMP-2', 1, origin=CAS_TARGETS[prefix], prefix=prefix, sensors=VISUAL)
        for prefix in ('ifvA', 'ifvB', 'ifvC')] + [
        F.Unit('vehicle', 'ZSU-57-2', 1, origin=ZSU_POSITION, prefix='ad')])
    cas = F.build_force('Blue-CAS', 'Blue', [
        F.Unit('aircraft', 'A-10C Thunderbolt II', 4, origin=(-40_000.0, 0.0, 3_000.0),
               step=(0.0, 500.0), prefix='cas', loadout='Maverick/Gun CAS')], mil_category=F.AIR_UNIT)
    return red, cas


def run_variant(session_id: str, variant: str):
    """Una sessione della variante: `(outcome, [EngagementResult, ...], [pass_rng, ...])`.

    Gli interruttori FP e D-5 sono sostituiti INSIEME attorno all'intera esecuzione (costruzione delle forze compresa);
    i risultati d'ingaggio sono catturati con una spia che chiama l'originale e salva una copia dello stream dei
    passaggi (`pass_rng`) PRIMA dell'esecuzione (None se assente). `results` e `pass_streams` sono allineati: le sole
    coppie con risultato non None.
    """
    geometry, switch = VARIANT_SPEC[variant]
    original = ER.resolve_engagement
    captured = []
    pass_streams = []

    def spy(*args, **kwargs):
        stream = copy.deepcopy(kwargs.get('pass_rng'))
        result = original(*args, **kwargs)

        if result is not None:
            captured.append(result)
            pass_streams.append(stream)

        return result

    with patch.object(ER_MODULE, 'FP_PER_PASS_DETECTION', switch), \
            patch.object(ER_MODULE, 'D5_DWELL_TIME', switch):
        red, cas = build(with_ewr=False) if geometry == 'reentry' else build_cas()

        if switch:
            F.declare_dwell(red.assets[ZSU], {'air': ZSU_DWELL_S})

        route, asset_ids = (REENTRY, IFV_IDS) if geometry == 'reentry' else (CAS_ROUTE, CAS_TARGET_IDS)
        target = Target(kind=TargetKind.GROUP, target_id='Red-Line', asset_ids=asset_ids,
                        provenance=TargetProvenance.OBSERVED, observed_at=0.0)
        missions = F.missions_for(cas, route, mission_type='CAS', target=target, weapons=(MAVERICK,),
                                  rules=MissionRules(roe='only_designated'))

        with patch.object(ER, 'resolve_engagement', side_effect=spy):
            outcome = F.run(session_id, [cas], [red], make_registry_fire_control(), duration=DURATION,
                            missions=missions, thresholds=BOTH_HOLD)

    return outcome, captured, pass_streams


def _zsu(results, cas=None):
    """Le `Detection` della ZSU (su `cas` se dato) di tutti i risultati."""
    return [d for result in results for d in result.detections
            if d.observer_id == ZSU and (cas is None or d.target_id == cas)]


def _first_zsu(results, cas):
    """Le `Detection` della ZSU su `cas` nel PRIMO risultato che ne contiene almeno una (vuoto se nessuno)."""
    for result in results:
        detections = [d for d in result.detections if d.observer_id == ZSU and d.target_id == cas]

        if detections:
            return detections

    return []


class TestS33DetectionPerPass(F.LoggerSilencer, unittest.TestCase):
    """S33-PASSES: un'occasione di rilevamento per passaggio nel volume proprio della ZSU-57-2 (FP + D-5)."""

    SEEDS = SEEDS
    VARIANTS = VARIANTS

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        # Ciclo esterno sui seed, interno sulle 4 varianti nell'ordine di VARIANT_SPEC: stesso `session_id` per le 4
        # varianti di un seed (la fotografia numera le esecuzioni per occorrenza del session_id nell'unita').
        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                cls.runs[variant].append(run_variant(session_id, variant))

    # ── geometria di rientro, `off` / `on` ─────────────────────────────────────────────────────────────────────────

    def test_premise_two_passes_per_aircraft(self):
        """In `on` ogni A-10C attraversa due volte il volume della ZSU: esattamente 2 rilevamenti, `pass_index` 0 e 1,
        `pass_count` 2, il dwell letto e l'unione FP-10 valutata e NON applicata (l'uscita supera il dwell)."""
        for seed, (_, results, _) in zip(self.SEEDS, self.runs['on']):
            for cas in CAS_IDS:
                detections = _zsu(results, cas)

                with self.subTest(session=seed, aircraft=cas):
                    self.assertEqual(len(detections), 2)
                    self.assertEqual({d.pass_index for d in detections}, {0, 1})
                    self.assertTrue(all(d.pass_count == 2 for d in detections))
                    self.assertTrue(all(d.dwell_time_s == ZSU_DWELL_S for d in detections))

                    by_index = {d.pass_index: d for d in detections}
                    self.assertGreater(by_index[1].pass_start - by_index[0].pass_end, ZSU_DWELL_S)

    def test_switch_off_one_draw_per_window(self):
        """In `off` una sola estrazione per finestra e direzione: esattamente 1 rilevamento della ZSU per A-10C, con
        `pass_index` None."""
        for seed, (_, results, _) in zip(self.SEEDS, self.runs['off']):
            for cas in CAS_IDS:
                detections = _zsu(results, cas)

                with self.subTest(session=seed, aircraft=cas):
                    self.assertEqual(len(detections), 1)
                    self.assertIsNone(detections[0].pass_index)

    def test_the_engagement_stream_is_unchanged(self):
        """Nel PRIMO episodio il flusso d'ingaggio estrae le stesse uscite con FP acceso: la regola non cambia l'ordine
        ne' il contenuto delle estrazioni esistenti."""
        for seed, (_, off, _), (_, on, _) in zip(self.SEEDS, self.runs['off'], self.runs['on']):
            with self.subTest(session=seed):
                self.assertTrue(off and on)
                self.assertEqual([d.draw for d in off[0].detections],
                                 [d.draw for d in on[0].detections if d.pass_index in (None, 0)])

    def test_no_launch_after_the_pass_without_a_new_detection(self):
        """FP-3 (a): ogni salva della ZSU nasce da un rilevamento dello stesso bersaglio nello stesso episodio, prima
        della fine del passaggio."""
        for seed, (_, results, _) in zip(self.SEEDS, self.runs['on']):
            for result in results:
                for salvo in result.salvos:
                    if salvo.shooter_id != ZSU:
                        continue

                    self._assert_launch_covered(seed, result, salvo)

    def test_premise_the_zsu_fires_without_the_switch(self):
        """Premessa non vacua: in `off` la ZSU spara in almeno un seed."""
        rounds = sum(e.rounds for outcome, _, _ in self.runs['off'] for e in outcome.ammunition_events
                     if e.asset_id == ZSU)
        self.assertGreater(rounds, 0)

    # ── geometria CAS, `cas_off` / `cas_on` ────────────────────────────────────────────────────────────────────────

    def test_cas_premise_geometry(self):
        """Le premesse geometriche della CAS (senza sessione): bersagli A e C entro la portata visiva della ZSU, B
        fuori; portate reciproche attese; partenza e virate degli A-10C entro la portata a terra."""
        red, cas = build_cas()
        zsu = red.assets[ZSU]

        self.assertLess(self._hdist(zsu, red.assets['Red-Line/ifvA0']), ZSU_VISUAL_RANGE_M)
        self.assertLess(self._hdist(zsu, red.assets['Red-Line/ifvC0']), ZSU_VISUAL_RANGE_M)
        self.assertGreater(self._hdist(zsu, red.assets['Red-Line/ifvB0']), ZSU_VISUAL_RANGE_M)

        self.assertEqual(CS.mutual_detection_ranges(zsu, cas.assets['Blue-CAS/cas0']),
                         (ZSU_VISUAL_RANGE_M, A10_GROUND_RANGE_M))

        for index, asset_id in enumerate(CAS_IDS):
            aircraft = cas.assets[asset_id]

            with self.subTest(aircraft=asset_id):
                self.assertLess(self._hdist(zsu, aircraft), A10_GROUND_RANGE_M)

                for px, py in CAS_ROUTE:
                    dy = py + 500.0 * index
                    self.assertLess(math.hypot(px - zsu.position.x, dy - zsu.position.y), A10_GROUND_RANGE_M)

    def test_cas_premise_two_separate_passes_per_aircraft(self):
        """In `cas_on` ogni A-10C fa due passaggi NON contigui nel volume della ZSU: esattamente 2 rilevamenti nel
        primo episodio che li contiene, con una pausa > 60 s (soglia del test, non un dato) fra i due."""
        for seed, (_, results, _) in zip(self.SEEDS, self.runs['cas_on']):
            for cas in CAS_IDS:
                detections = _first_zsu(results, cas)

                with self.subTest(session=seed, aircraft=cas):
                    self.assertEqual(len(detections), 2)
                    self.assertEqual({d.pass_index for d in detections}, {0, 1})
                    self.assertTrue(all(d.pass_count == 2 for d in detections))
                    self.assertTrue(all(d.distance_cpa < ZSU_VISUAL_RANGE_M for d in detections))
                    self.assertTrue(all(d.dwell_time_s == ZSU_DWELL_S for d in detections))

                    by_index = {d.pass_index: d for d in detections}
                    self.assertGreater(by_index[1].pass_start - by_index[0].pass_end, 60.0)

    def test_cas_switch_off_one_draw_per_aircraft(self):
        """In `cas_off` una sola estrazione per finestra: 1 rilevamento della ZSU per A-10C nel primo episodio, con
        `pass_index` None."""
        for seed, (_, results, _) in zip(self.SEEDS, self.runs['cas_off']):
            for cas in CAS_IDS:
                detections = _first_zsu(results, cas)

                with self.subTest(session=seed, aircraft=cas):
                    self.assertEqual(len(detections), 1)
                    self.assertIsNone(detections[0].pass_index)

    def test_cas_first_pass_keeps_the_engagement_stream(self):
        """Nel PRIMO episodio le estrazioni del flusso d'ingaggio sono le stesse con FP acceso."""
        for seed, (_, cas_off, _), (_, cas_on, _) in zip(self.SEEDS, self.runs['cas_off'], self.runs['cas_on']):
            with self.subTest(session=seed):
                self.assertTrue(cas_off and cas_on)
                self.assertEqual([d.draw for d in cas_off[0].detections],
                                 [d.draw for d in cas_on[0].detections if d.pass_index in (None, 0)])

    def test_cas_second_pass_draws_from_the_pass_stream(self):
        """Le estrazioni dei passaggi dal secondo in poi vengono dallo stream separato dei passaggi (`pass_rng`), nel
        loro ordine; ogni A-10C ha almeno un rilevamento nel secondo passaggio."""
        for seed, (_, results, streams) in zip(self.SEEDS, self.runs['cas_on']):
            for result, stream in zip(results, streams):
                if stream is None:
                    continue

                second = [d.draw for d in result.detections if d.pass_index not in (None, 0)]

                with self.subTest(session=seed):
                    self.assertEqual(second, [stream.random() for _ in range(len(second))])

            for cas in CAS_IDS:
                with self.subTest(session=seed, aircraft=cas):
                    self.assertTrue(any(d.pass_index == 1 for d in _zsu(results, cas)))

    def test_cas_no_launch_after_the_pass_without_a_new_detection(self):
        """FP-3 (a), geometria CAS: come il test 4 in `cas_on`."""
        for seed, (_, results, _) in zip(self.SEEDS, self.runs['cas_on']):
            for result in results:
                for salvo in result.salvos:
                    if salvo.shooter_id != ZSU:
                        continue

                    self._assert_launch_covered(seed, result, salvo)

    # ── D-5 nelle varianti accese ───────────────────────────────────────────────────────────────────────────────────

    def test_d5_reads_the_dwell_and_leaves_the_probability_unchanged(self):
        """La D-5 legge il dwell dichiarato e con g = 1 esatto non cambia la Pd (permanenza >= 2 s); gli altri
        osservatori non dichiarano dwell, e a D-5 spenta nessun campo di permanenza e' valorizzato."""
        for variant in ('on', 'cas_on'):
            for seed, (_, results, _) in zip(self.SEEDS, self.runs[variant]):
                zsu = [d for d in _zsu(results) if d.distance_cpa < ZSU_VISUAL_RANGE_M]

                with self.subTest(variant=variant, session=seed):
                    self.assertTrue(zsu)  # premessa non vacua: almeno una direzione in portata

                for detection in zsu:
                    with self.subTest(variant=variant, session=seed, target=detection.target_id):
                        self.assertEqual(detection.dwell_time_s, ZSU_DWELL_S)
                        self.assertGreaterEqual(detection.exposure_s, ZSU_DWELL_S)
                        self.assertEqual(ER.dwell_factor(detection.exposure_s, detection.dwell_time_s), 1.0)

                for result in results:
                    for detection in result.detections:
                        if detection.observer_id == ZSU:
                            continue

                        with self.subTest(variant=variant, session=seed, observer=detection.observer_id):
                            self.assertIsNone(detection.dwell_time_s)
                            self.assertIsNone(detection.exposure_s)

        for variant in ('off', 'cas_off'):
            for seed, (_, results, _) in zip(self.SEEDS, self.runs[variant]):
                for result in results:
                    for detection in result.detections:
                        with self.subTest(variant=variant, session=seed, observer=detection.observer_id):
                            self.assertIsNone(detection.dwell_time_s)
                            self.assertIsNone(detection.exposure_s)

    def test_variant_switches_are_scoped(self):
        """Gli interruttori FP e D-5 sono sostituiti soltanto durante la variante e ripristinati anche se l'esecuzione
        solleva; il dwell e' dichiarato sulla ZSU costruita dentro la variante (e solo con FP e D-5 accese)."""
        def probe(*args, **kwargs):
            recorded.append((ER_MODULE.FP_PER_PASS_DETECTION,
                             ER_MODULE.D5_DWELL_TIME,
                             args[2][0].assets[ZSU].detection_dwell_time('air')))
            raise RuntimeError('probe')

        expected = {
            'off': (False, False, None),
            'on': (True, True, ZSU_DWELL_S),
            'cas_off': (False, False, None),
            'cas_on': (True, True, ZSU_DWELL_S),
        }

        for variant in self.VARIANTS:
            before = (ER.FP_PER_PASS_DETECTION, ER.D5_DWELL_TIME)
            recorded = []

            with self.subTest(variant=variant):
                with self.assertRaises(RuntimeError):
                    with patch.object(F, 'run', side_effect=probe):
                        run_variant('S33-PASSES-0', variant)

                self.assertEqual(recorded, [expected[variant]])
                self.assertEqual((ER.FP_PER_PASS_DETECTION, ER.D5_DWELL_TIME), before)

    # ── aiuti ───────────────────────────────────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _hdist(a, b):
        """Distanza orizzontale [m] fra due asset (su `position.x`/`position.y`)."""
        return math.hypot(a.position.x - b.position.x, a.position.y - b.position.y)

    def _assert_launch_covered(self, seed, result, salvo):
        covering = [d for d in result.detections
                    if d.observer_id == ZSU and d.target_id == salvo.target_id and d.detected
                    and d.time is not None and d.time <= salvo.t_launch + 1e-9
                    and salvo.t_launch <= d.pass_end + 1e-6]

        self.assertTrue(covering, f'seed {seed}: la salva della ZSU su {salvo.target_id} '
                                  f'a t={salvo.t_launch} non ha un rilevamento che la copra')


if __name__ == '__main__':
    unittest.main()