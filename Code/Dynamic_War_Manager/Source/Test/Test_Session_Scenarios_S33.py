"""Scenario S33 del motore di sessioni virtuali: rilevamento per passaggio nella portata propria (FP) e D-5.

Prosegue S32 (`Test_Session_Scenarios_S32.py`) con la stessa disciplina: si verifica un comportamento QUALITATIVO o
STRUTTURALE (relazioni fra varianti), mai un numero calibrato. Nel codice (`Analysis/Document/
Proposta_Finestre_Per_Passaggio_Portata_Propria.md`, blocco 2): il risolutore da' UNA occasione di rilevamento per
OGNI passaggio del bersaglio nel volume PROPRIO dell'osservatore (non una sola per finestra); con la D-5
(`D5_DWELL_TIME`) accesa e un `dwell_time_s` dichiarato dal sensore, la Pd di ogni passaggio e' moltiplicata per
`min(1, permanenza / dwell)`.

## S33-PASSES (`TestS33DetectionPerPass`)

S33 prova la configurazione finale: FP (sempre attiva) e D-5 accesa con il dwell della ZSU 2 s [S]. Due varianti,
5 seed ciascuna (nomi stabili nella fotografia, nell'ordine):

| Variante | Geometria | dwell della ZSU (dichiarato) | Cosa prova                                    |
|----------|-----------|------------------------------|-----------------------------------------------|
| `on`     | rientro   | 2 s [S]                      | due passaggi, due estrazioni; FP sola (g = 1) |
| `cas_on` | CAS       | 2 s [S]                      | due passaggi NON contigui; FP sola (g = 1)    |

La ZSU dichiara (`declare_dwell`, modo 'air') un periodo di aggiornamento di 2 s, STIMA [S] dell'utente (2026-11-08:
osservatore umano piu' ottica), non un dato. Con passaggi di 50-67 s il fattore di permanenza e' g = 1 e con uscite di
100-130 s l'unione dei passaggi (FP-10) non unisce: la D-5 non cambia ne' estrazioni ne' Pd; per questo non ci sono
varianti con dwell lunghi. Le varianti `off` e `cas_off` (FP e D-5 spente) sono state tolte con l'interruttore FP
(Proposta_FP_Pulizia_Interruttore.md).
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
# variante -> geometria; in ogni variante D-5 accesa e dwell ZSU_DWELL_S sulla ZSU
VARIANT_SPEC = {
    'on': 'reentry',
    'cas_on': 'cas',
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
# ottica, "predizione" del cervello). NON e' un dato. Dichiarato sulla ZSU (F.declare_dwell, modo 'air') in ogni
# variante: soglia di unione FP-10 (le uscite fra i passaggi sono molto piu' lunghe: nessuna unione) e dwell della
# legge D-5 (passaggi molto piu' lunghi: g = 1).
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
    """Una sessione della variante: `(outcome, [EngagementResult, ...], [(engagement_rng, pass_rng), ...])`.

    La D-5 e' sostituita con True attorno all'intera esecuzione (costruzione delle forze compresa); la FP e' sempre
    attiva (`FP_PER_PASS_DETECTION`, default True) e il dwell della ZSU e' dichiarato in ogni variante. I risultati
    d'ingaggio sono catturati con una spia che chiama l'originale e salva PRIMA dell'esecuzione una copia dello stream
    d'ingaggio (`args[4]`) e dello stream dei passaggi (`pass_rng`, sempre presente). `results` e `streams` sono
    allineati: le sole coppie con risultato non None.
    """
    geometry = VARIANT_SPEC[variant]
    original = ER.resolve_engagement
    captured = []
    streams = []

    def spy(*args, **kwargs):
        engagement = copy.deepcopy(args[4])
        pass_stream = copy.deepcopy(kwargs['pass_rng'])
        result = original(*args, **kwargs)

        if result is not None:
            captured.append(result)
            streams.append((engagement, pass_stream))

        return result

    with patch.object(ER_MODULE, 'D5_DWELL_TIME', True):
        red, cas = build(with_ewr=False) if geometry == 'reentry' else build_cas()

        F.declare_dwell(red.assets[ZSU], {'air': ZSU_DWELL_S})

        route, asset_ids = (REENTRY, IFV_IDS) if geometry == 'reentry' else (CAS_ROUTE, CAS_TARGET_IDS)
        target = Target(kind=TargetKind.GROUP, target_id='Red-Line', asset_ids=asset_ids,
                        provenance=TargetProvenance.OBSERVED, observed_at=0.0)
        missions = F.missions_for(cas, route, mission_type='CAS', target=target, weapons=(MAVERICK,),
                                  rules=MissionRules(roe='only_designated'))

        with patch.object(ER, 'resolve_engagement', side_effect=spy):
            outcome = F.run(session_id, [cas], [red], make_registry_fire_control(), duration=DURATION,
                            missions=missions, thresholds=BOTH_HOLD)

    return outcome, captured, streams


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

        # Ciclo esterno sui seed, interno sulle 2 varianti nell'ordine di VARIANT_SPEC: stesso `session_id` per le 2
        # varianti di un seed (la fotografia numera le esecuzioni per occorrenza del session_id nell'unita').
        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                cls.runs[variant].append(run_variant(session_id, variant))

    # ── geometria di rientro, `on` ─────────────────────────────────────────────────────────────────────────────────

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

    def test_first_passes_draw_from_the_engagement_stream(self):
        """FP-2 (O3): le estrazioni dei primi passaggi sono, nell'ordine delle `Detection`, le prime uscite dello
        stream dell'ingaggio (la fase di rilevamento e' la prima del risolutore, `Engagement_Resolver.py:4277-4278`)."""
        self._assert_first_passes_draw_from_the_engagement_stream(self.runs['on'])

    def test_no_launch_after_the_pass_without_a_new_detection(self):
        """FP-3 (a): ogni salva della ZSU nasce da un rilevamento dello stesso bersaglio nello stesso episodio, prima
        della fine del passaggio."""
        for seed, (_, results, _) in zip(self.SEEDS, self.runs['on']):
            for result in results:
                for salvo in result.salvos:
                    if salvo.shooter_id != ZSU:
                        continue

                    self._assert_launch_covered(seed, result, salvo)

    def test_premise_the_zsu_fires(self):
        """Premessa non vacua: in ogni variante la ZSU spara (somma dei colpi su tutti i semi > 0)."""
        for variant in self.VARIANTS:
            rounds = sum(e.rounds for outcome, _, _ in self.runs[variant] for e in outcome.ammunition_events
                         if e.asset_id == ZSU)

            with self.subTest(variant=variant):
                self.assertGreater(rounds, 0)

    # ── geometria CAS, `cas_on` ────────────────────────────────────────────────────────────────────────────────────

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

    def test_cas_first_passes_draw_from_the_engagement_stream(self):
        """FP-2 (O3), geometria CAS: come il test 3 in `cas_on`."""
        self._assert_first_passes_draw_from_the_engagement_stream(self.runs['cas_on'])

    def test_cas_second_pass_draws_from_the_pass_stream(self):
        """Le estrazioni dei passaggi dal secondo in poi vengono dallo stream separato dei passaggi (`pass_rng`), nel
        loro ordine; ogni A-10C ha almeno un rilevamento nel secondo passaggio."""
        for seed, (_, results, streams) in zip(self.SEEDS, self.runs['cas_on']):
            for result, (_, pass_stream) in zip(results, streams):
                self.assertIsNotNone(pass_stream)

                second = [d.draw for d in result.detections if d.pass_index not in (None, 0)]

                with self.subTest(session=seed):
                    stream = copy.deepcopy(pass_stream)
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

    # ── D-5 ───────────────────────────────────────────────────────────────────────────────────────────────────────────

    def test_d5_reads_the_dwell_and_leaves_the_probability_unchanged(self):
        """La D-5 legge il dwell dichiarato e con g = 1 esatto non cambia la Pd (permanenza >= 2 s); gli altri
        osservatori non dichiarano dwell e nessun campo di permanenza e' valorizzato."""
        for variant in self.VARIANTS:
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

    def test_variant_switches_are_scoped(self):
        """La D-5 e' sostituita soltanto durante la variante e ripristinata anche se l'esecuzione solleva; il dwell e'
        dichiarato sulla ZSU costruita dentro la variante."""
        def probe(*args, **kwargs):
            recorded.append((ER_MODULE.D5_DWELL_TIME,
                             args[2][0].assets[ZSU].detection_dwell_time('air')))
            raise RuntimeError('probe')

        for variant in self.VARIANTS:
            before = ER.D5_DWELL_TIME
            recorded = []

            with self.subTest(variant=variant):
                with self.assertRaises(RuntimeError):
                    with patch.object(F, 'run', side_effect=probe):
                        run_variant('S33-PASSES-0', variant)

                self.assertEqual(recorded, [(True, ZSU_DWELL_S)])
                self.assertEqual(ER.D5_DWELL_TIME, before)

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

    def _assert_first_passes_draw_from_the_engagement_stream(self, runs):
        """Aiuto dei test 3 e 9: in ogni episodio le estrazioni dei primi passaggi sono le prime uscite dello stream
        dell'ingaggio, nell'ordine delle `Detection`."""
        for seed, (_, results, streams) in zip(self.SEEDS, runs):
            for result, (engagement, _) in zip(results, streams):
                first = [d.draw for d in result.detections if d.pass_index in (None, 0)]

                with self.subTest(session=seed):
                    self.assertTrue(first)
                    stream = copy.deepcopy(engagement)
                    self.assertEqual(first, [stream.random() for _ in first])


if __name__ == '__main__':
    unittest.main()