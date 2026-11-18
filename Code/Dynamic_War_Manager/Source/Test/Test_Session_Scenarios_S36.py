"""Scenari S36 del motore di sessioni virtuali: permanenza BREVE nel volume con i dwell reali dei registri (D-5, DW-9).

Prosegue S32 (`Test_Session_Scenarios_S32.py`) e S33 con la stessa disciplina: si verifica un comportamento QUALITATIVO o
STRUTTURALE (relazioni fra varianti), mai un numero calibrato. Con `Engagement_Resolver.D5_DWELL_TIME` acceso (default dopo
la DW-9) la Pd di un rilevamento e' moltiplicata per `g = min(1, permanenza / dwell)` (`dwell_factor`), dove `dwell` e'
il `dwell_time_s` letto dal REGISTRO (`registry_dwell_time`, sensore con la portata di acquisizione maggiore). Gli
scenari di S32 usano dwell di prova lunghi (30 e 600 s); qui i bersagli restano nel volume dell'osservatore MENO del
periodo di rivisita dichiarato dal registro (`Proposta_Scenari_S34_Permanenza_Breve.md`; la serie si chiama S36 perche'
S34 e S35 sono gia' occupati).

## Nessuna salva e' possibile (premessa strutturale)

Un tiratore lancia solo se `istante del rilevamento + reazione <= fine del passaggio` (FP-3 (a)); con `g < 1` il passaggio
dura meno del dwell, quindi serve `reazione < dwell`. Nei registri il tempo di reazione supera il dwell per ogni tiratore
(ZSU-57-2: reazione 5,1 s, dwell 3,2 s; Strela-10 5,6 contro 3,2 s; Tor 6,5 contro 3,0 s; Buk 27,1 contro 9,0 s; S-300PS
28,0 contro 12,0 s; unica eccezione la Shilka, 5,1 contro 7,3 s, ma a ~20 km, oltre la portata del cannone). Quindi in
queste serie non c'e' MAI una salva, in nessuna variante: la legge si legge sulle `Detection` (permanenza, dwell, Pd,
estrazione, istante), che la fotografia registra per le sole unita' S36 (voce `detections`, `Scenario_Baseline.
DETECTION_UNITS`). Gli osservatori sono armati solo per costruzione: i bersagli (A-10C) sono in `weapon_hold`.

## Le unita' (4 seed ciascuna; stesso `session_id` per le varianti di un seed; nomi stabili nella fotografia)

| Unita'         | Leva                                    | Varianti                                            |
|----------------|-----------------------------------------|-----------------------------------------------------|
| `S36-GRAZE`    | A, passaggio radente (ZSU-57-2)         | `off`, `on`, `band_min`, `band_max`                 |
| `S36-CUT`      | B, taglio alla fine della sessione      | `off`, `on`                                         |
| `S36-PASSES`   | unione FP-10 di due passaggi brevi      | `join_off`, `join_on`, `split_off`, `split_on`      |
| `S36-FAMILIES` | sei famiglie di sensori + AWACS (leva C)| una per famiglia, g = 0,5                           |
| `S36-BAND`     | estremi della banda di incertezza       | le famiglie con dwell `min` e `max`                 |

Questo modulo contiene gli aiuti comuni, le cinque unita' (`TestS36Graze`, `TestS36WindowCut`, `TestS36PassJoin`,
`TestS36Families`, `TestS36Band`) e i test dello strumento (`TestS36BaselineDetections`, fuori da `UNITS`).

## Costanti: che cosa e' dato e che cosa e' geometria di test

- Portata, dwell e velocita' sono COPIE dei registri (ZSU-57-2: 6 km, 3,2 s; A-10C: `speed['nominal']` 155,556 m/s),
  controllate da un test di premessa; il dwell della ZSU e' una STIMA [S] dichiarata (DW9-6), non un dato tarato.
- Scostamenti laterali, quote, durate e origini sono GEOMETRIA DI TEST, non dati.
- Gli estremi della banda della vista (1,75 e 6,0 s) sono VALORI DI PROVA presi dalla banda di incertezza dichiarata
  (`Proposta_Dwell_Estensione_DW9.md` §2.1-§2.4), non dati: si dichiarano con `F.declare_dwell` sull'istanza.
"""

import math
import sys
import unittest
from unittest.mock import patch

from Code.Dynamic_War_Manager.Source.Command.Mission_Types import MissionRules
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic.Fire_Control import make_registry_fire_control
from Code.Dynamic_War_Manager.Source.Test import Scenario_Baseline as SB
from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F
from Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S10_S18 import BOTH_HOLD

# Modulo che contiene davvero il risolutore: e' li' che `Session_Simulator.engage` legge D5_DWELL_TIME a ogni chiamata.
ER_MODULE = sys.modules[ER.__name__]

SEEDS_PER_SCENARIO = 4
DURATION = 600.0                          # durata delle sessioni [s], geometria di test
A10 = 'A-10C Thunderbolt II'
A10_LOADOUT = 'Maverick/Gun CAS'
A10_SPEED = 155.55555555555554            # speed['nominal'] del registro [m/s] (copia, test di premessa)
TARGET_Z = 3_000.0                        # quota degli A-10C [m], geometria di test
OBSERVER = 'Red-Line/obs0'                # osservatore a terra o in mare (prefisso 'obs')
ZSU = 'ZSU-57-2'
ZSU_RANGE = 6_000.0                       # portata aria (vista) del registro [m] (copia)
ZSU_DWELL = 3.2                           # dwell_time_s della vista del registro [s] (copia; STIMA [S] DW9-6)
HORIZONTAL_RADIUS = math.sqrt(ZSU_RANGE ** 2 - TARGET_Z ** 2)   # 5196,152 m a 3000 m di quota [C]
HOLD = MissionRules(roe='weapon_hold')    # gli A-10C non sparano: si isola il rilevamento


# ── aiuti comuni ────────────────────────────────────────────────────────────────────────────────────────────────────

def lateral_offset(sensor_range: float, height_difference: float, relative_speed: float, exposure_s: float) -> float:
    """Scostamento laterale [m] della retta del bersaglio dal centro dell'osservatore perche' la permanenza nella sfera
    di raggio `sensor_range` valga `exposure_s`.

    La corda nella sfera e' `L = relative_speed * exposure_s`; con `dz = height_difference` la distanza dal centro del
    punto medio della corda e' `h`, con `h^2 + dz^2 + (L / 2)^2 = sensor_range^2`, cioe'
    `h = sqrt(R^2 - dz^2 - (v * tau / 2)^2)`.
    """
    return math.sqrt(sensor_range ** 2 - height_difference ** 2 - (relative_speed * exposure_s / 2.0) ** 2)


def run_variant(session_id: str, build, switch: bool):
    """Una sessione di una variante: `(outcome, [EngagementResult, ...])`.

    L'interruttore `D5_DWELL_TIME` e' sostituito attorno a costruzione ed esecuzione (come S32); `build()` restituisce
    `(forces_a, forces_b, missions, duration)`. I risultati d'ingaggio sono catturati con una spia che chiama l'originale
    e non estrae nulla (come S9).
    """
    original = ER.resolve_engagement
    captured = []

    def spy(*args, **kwargs):
        result = original(*args, **kwargs)
        captured.append(result)
        return result

    with patch.object(ER_MODULE, 'D5_DWELL_TIME', switch):
        forces_a, forces_b, missions, duration = build()

        with patch.object(ER, 'resolve_engagement', side_effect=spy):
            outcome = F.run(session_id, forces_a, forces_b, make_registry_fire_control(), duration=duration,
                            missions=missions, thresholds=BOTH_HOLD)

    return outcome, [result for result in captured if result is not None]


def detections_of(results, observer_id: str, target_id=None) -> list:
    """Le `Detection` dell'osservatore (e del bersaglio, se dato), nell'ordine dei risultati d'ingaggio."""
    return [d for result in results for d in result.detections
            if d.observer_id == observer_id and (target_id is None or d.target_id == target_id)]


def expected_probability(detection) -> float:
    """Pd attesa dalla legge D-5 sui campi della `Detection` (vale solo con `exposure_s` non None)."""
    return ER.detection_probability(detection.distance_cpa, detection.sensor_range,
                                    ER.dwell_factor(detection.exposure_s, detection.dwell_time_s))


def previous_probability(detection) -> float:
    """Pd della legge di prima (sola distanza, senza permanenza), ricalcolata dai campi della `Detection`."""
    if detection.distance_cpa <= detection.sensor_range:
        return ER.detection_probability(detection.distance_cpa, detection.sensor_range)

    return 0.0


# ── S36-GRAZE ───────────────────────────────────────────────────────────────────────────────────────────────────────

GRAZE_SEEDS = [f'S36-GRAZE-{index}' for index in range(SEEDS_PER_SCENARIO)]
GRAZE_FACTORS = (('casA', 0.5), ('casB', 0.9), ('casC', 1.1), ('casD', 2.0))   # g con il dwell del registro
GRAZE_EXPOSURE = {prefix: g * ZSU_DWELL for prefix, g in GRAZE_FACTORS}        # 1,6 / 2,88 / 3,52 / 6,4 s [C]
GRAZE_OFFSET = {prefix: lateral_offset(ZSU_RANGE, TARGET_Z, A10_SPEED, exposure)
                for prefix, exposure in GRAZE_EXPOSURE.items()}
#   = 5194,662 / 5191,322 / 5188,935 / 5172,255 m [C, V]
# variante -> (interruttore D5_DWELL_TIME, dwell dichiarato sulla ZSU [s] | None = registro)
GRAZE_VARIANTS = {'off': (False, None), 'on': (True, None), 'band_min': (True, 1.75), 'band_max': (True, 6.0)}
#   1,75 e 6,0 = estremi della banda di incertezza del dwell della vista, VALORI DI PROVA (non dati)
GRAZE_DWELL = {'off': None, 'on': ZSU_DWELL, 'band_min': 1.75, 'band_max': 6.0}   # dwell atteso nella Detection
VARIANTS = tuple(GRAZE_VARIANTS)


def build_graze(declared_dwell):
    """Costruttore (per `run_variant`) di S36-GRAZE: la ZSU-57-2 e 4 A-10C che le passano accanto con scostamenti
    diversi, dentro la sfera di 6 km a 3000 m di quota, ognuno per `g * 3,2 s`. `declared_dwell` None = dwell del
    registro; altrimenti dwell dichiarato di prova sulla vista (`air`)."""
    def build():
        red = F.build_force('Red-Line', 'Red', [F.Unit('vehicle', ZSU, 1, origin=(0.0, 0.0), prefix='obs')])

        if declared_dwell is not None:
            F.declare_dwell(red.assets[OBSERVER], {'air': declared_dwell})

        blue = F.build_force('Blue-CAS', 'Blue', [
            F.Unit('aircraft', A10, 1, origin=(-40_000.0, GRAZE_OFFSET[prefix], TARGET_Z), prefix=prefix,
                   loadout=A10_LOADOUT) for prefix, _ in GRAZE_FACTORS], mil_category=F.AIR_UNIT)
        # Ogni A-10C va a (40 km, proprio scostamento): `missions_for` ne deriva le missioni (una per A-10C).
        missions = F.missions_for(blue, [(40_000.0, GRAZE_OFFSET['casA'])], mission_type='CAS',
                                  target=F.group_target('Red-Line'), rules=HOLD)
        return [blue], [red], missions, DURATION

    return build


class TestS36Graze(F.LoggerSilencer, unittest.TestCase):
    """S36-GRAZE: passaggio radente nella sfera della ZSU-57-2; la permanenza e' piu' breve del dwell del registro
    (g = 0,5 e 0,9), uguale a quella della legge di prima (g = 1,1 e 2,0), e gli estremi della banda del dwell la
    allargano o la stringono."""

    SEEDS = GRAZE_SEEDS
    VARIANTS = VARIANTS

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        # Ciclo esterno sui seed, interno sulle varianti: stesso `session_id` per le 4 varianti di un seed
        # (la fotografia numera le esecuzioni per occorrenza del session_id nell'unita').
        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                switch, declared = GRAZE_VARIANTS[variant]
                cls.runs[variant].append(run_variant(session_id, build_graze(declared), switch))

    def _detection(self, variant, index, prefix):
        """L'unica `Detection` della ZSU sull'A-10C `prefix` nella sessione `index` della variante."""
        _, results = self.runs[variant][index]
        found = detections_of(results, OBSERVER, f'Blue-CAS/{prefix}0')
        self.assertEqual(len(found), 1, (variant, index, prefix))
        return found[0]

    def _each(self, variants):
        """`(seed, indice, prefisso, variante)` per ogni seed, A-10C e variante data."""
        for index, seed in enumerate(self.SEEDS):
            for prefix, _ in GRAZE_FACTORS:
                for variant in variants:
                    yield seed, index, prefix, variant

    def test_premise_registry_values(self):
        """Le copie dei registri valgono ancora (la ZSU-57-2 e l'A-10C costruiti dalla fixture)."""
        red = F.build_force('Red-Line', 'Red', [F.Unit('vehicle', ZSU, 1, origin=(0.0, 0.0), prefix='obs')])
        blue = F.build_force('Blue-CAS', 'Blue', [
            F.Unit('aircraft', A10, 1, origin=(0.0, 0.0, TARGET_Z), prefix='cas', loadout=A10_LOADOUT)],
            mil_category=F.AIR_UNIT)

        self.assertEqual(red.assets[OBSERVER].detection_range('air'), ZSU_RANGE)
        self.assertEqual(red.assets[OBSERVER].detection_dwell_time('air'), ZSU_DWELL)
        self.assertAlmostEqual(blue.assets['Blue-CAS/cas0'].speed['nominal'], A10_SPEED, places=9)

    def test_premise_no_salvo(self):
        """Il passaggio e' piu' breve della reazione della ZSU (5,1 s) e gli A-10C sono in `weapon_hold`: nessuna salva
        in nessuna variante e seme."""
        for variant in self.VARIANTS:
            for seed, (outcome, _) in zip(self.SEEDS, self.runs[variant]):
                with self.subTest(variant=variant, session=seed):
                    self.assertEqual(len(outcome.ammunition_events), 0)

    def test_exposure_is_the_chord_time(self):
        """Con la legge accesa la permanenza e' il tempo della corda, `g * 3,2 s`, e il dwell e' quello dichiarato."""
        for seed, index, prefix, variant in self._each(('on', 'band_min', 'band_max')):
            with self.subTest(session=seed, variant=variant, target=prefix):
                detection = self._detection(variant, index, prefix)
                self.assertIsNone(detection.pass_index)
                self.assertAlmostEqual(detection.exposure_s, GRAZE_EXPOSURE[prefix], places=6)
                self.assertEqual(detection.dwell_time_s, GRAZE_DWELL[variant])

    def test_probability_is_scaled_by_the_dwell_factor(self):
        """`Pd` = legge D-5 ricalcolata dai campi = `min(1, permanenza / dwell) * Pd` di `off` (stesso seme e A-10C)."""
        for seed, index, prefix, variant in self._each(('on', 'band_min', 'band_max')):
            with self.subTest(session=seed, variant=variant, target=prefix):
                detection = self._detection(variant, index, prefix)
                reference = self._detection('off', index, prefix)
                g = min(1.0, detection.exposure_s / detection.dwell_time_s)
                self.assertAlmostEqual(detection.probability, expected_probability(detection), places=12)
                self.assertAlmostEqual(detection.probability, g * reference.probability, places=12)

    def test_same_draws_and_no_extra_detection(self):
        """Stesse estrazioni a interruttore acceso e spento, stessa distanza al massimo avvicinamento, e la legge non
        aggiunge rilevamenti: un rilevamento acceso lo e' anche spento."""
        lost = 0

        for seed, index, prefix, variant in self._each(('on', 'band_min', 'band_max')):
            with self.subTest(session=seed, variant=variant, target=prefix):
                detection = self._detection(variant, index, prefix)
                reference = self._detection('off', index, prefix)
                self.assertEqual(detection.draw, reference.draw)
                self.assertEqual(detection.distance_cpa, reference.distance_cpa)

                if detection.detected:
                    self.assertTrue(reference.detected)

                if variant == 'band_max' and reference.detected and not detection.detected:
                    lost += 1

        # Premessa non vacua: la riduzione di Pd toglie davvero qualche rilevamento (P-11, seme 0: casB0).
        self.assertGreater(lost, 0)

    def test_factor_one_reproduces_the_previous_law(self):
        """Permanenza >= dwell: g = 1, quindi la Pd, l'esito e l'istante sono ESATTAMENTE quelli di `off`."""
        cases = [(seed, index, prefix, variant) for seed, index, prefix, variant in self._each(('on',))
                 if prefix in ('casC', 'casD')]
        # In `band_max` (dwell 6,0 s) g = 1 solo per casD (6,4 s).
        cases += [(seed, index, prefix, variant) for seed, index, prefix, variant in self._each(('band_max',))
                  if prefix == 'casD']

        for seed, index, prefix, variant in cases:
            with self.subTest(session=seed, variant=variant, target=prefix):
                detection = self._detection(variant, index, prefix)
                reference = self._detection('off', index, prefix)
                self.assertEqual(detection.probability, reference.probability)
                self.assertEqual(detection.detected, reference.detected)
                self.assertEqual(detection.time, reference.time)

    def test_band_orders_the_probability(self):
        """Dwell piu' corto, Pd piu' alta: `p(band_min) >= p(on) >= p(band_max)` e i rilevati di `band_max` sono un
        sottoinsieme di quelli di `on`, che sono un sottoinsieme di quelli di `band_min`."""
        for index, seed in enumerate(self.SEEDS):
            for prefix, _ in GRAZE_FACTORS:
                with self.subTest(session=seed, target=prefix):
                    p_min, p_on, p_max = (self._detection(v, index, prefix) for v in ('band_min', 'on', 'band_max'))
                    self.assertGreaterEqual(p_min.probability, p_on.probability)
                    self.assertGreaterEqual(p_on.probability, p_max.probability)

                    if p_max.detected:
                        self.assertTrue(p_on.detected)

                    if p_on.detected:
                        self.assertTrue(p_min.detected)

    def test_switch_off_leaves_no_dwell_fields(self):
        """Spento, nessuna `Detection` porta permanenza o dwell; in tutte le varianti i rilevamenti fatti dagli A-10C
        (osservatori senza dwell nei registri) non li portano mai."""
        for index, seed in enumerate(self.SEEDS):
            with self.subTest(session=seed, variant='off'):
                _, results = self.runs['off'][index]

                for detection in detections_of(results, OBSERVER):
                    self.assertIsNone(detection.exposure_s)
                    self.assertIsNone(detection.dwell_time_s)

        for variant in self.VARIANTS:
            for seed, (_, results) in zip(self.SEEDS, self.runs[variant]):
                with self.subTest(session=seed, variant=variant):
                    for detection in (d for result in results for d in result.detections
                                      if d.observer_id != OBSERVER):
                        self.assertIsNone(detection.dwell_time_s)

    def test_variant_switch_is_scoped(self):
        """La D-5 e' sostituita soltanto durante la variante e ripristinata anche se l'esecuzione solleva; il dwell
        dichiarato e' sulla ZSU costruita dentro la variante (come S33)."""
        def probe(*args, **kwargs):
            recorded.append((ER_MODULE.D5_DWELL_TIME, args[2][0].assets[OBSERVER].detection_dwell_time('air')))
            raise RuntimeError('probe')

        for variant, (switch, declared) in GRAZE_VARIANTS.items():
            before = ER.D5_DWELL_TIME
            recorded = []

            with self.subTest(variant=variant):
                with self.assertRaises(RuntimeError):
                    with patch.object(F, 'run', side_effect=probe):
                        run_variant('S36-GRAZE-0', build_graze(declared), switch)

                self.assertEqual(recorded, [(switch, ZSU_DWELL if declared is None else declared)])
                self.assertEqual(ER.D5_DWELL_TIME, before)


# ── S36-CUT ─────────────────────────────────────────────────────────────────────────────────────────────────────────

CUT_SEEDS = [f'S36-CUT-{index}' for index in range(SEEDS_PER_SCENARIO)]
CUT_DURATION = 120.0                                        # durata della sessione [s], geometria di test
CUT_LEFT = (('casA', 1.0), ('casB', 3.0), ('casC', 10.0))   # secondi di sessione rimasti all'ingresso nella sfera
CUT_ORIGIN_X = {prefix: -(HORIZONTAL_RADIUS + (CUT_DURATION - left) * A10_SPEED) for prefix, left in CUT_LEFT}
#   = -23707,264 / -23396,152 / -22307,264 m [C]
CUT_VARIANTS = {'off': False, 'on': True}                   # variante -> interruttore D5_DWELL_TIME
CUT_VARIANT_NAMES = tuple(CUT_VARIANTS)


def build_cut():
    """Costruttore (per `run_variant`) di S36-CUT: la ZSU-57-2 (dwell del registro) e 3 A-10C che entrano nella sfera
    1, 3 e 10 s prima della fine della sessione di 120 s: la sessione taglia la permanenza (leva B)."""
    red = F.build_force('Red-Line', 'Red', [F.Unit('vehicle', ZSU, 1, origin=(0.0, 0.0), prefix='obs')])
    blue = F.build_force('Blue-CAS', 'Blue', [
        F.Unit('aircraft', A10, 1, origin=(CUT_ORIGIN_X[prefix], 0.0, TARGET_Z), prefix=prefix,
               loadout=A10_LOADOUT) for prefix, _ in CUT_LEFT], mil_category=F.AIR_UNIT)
    # Ogni A-10C vola 80 km verso +x dal proprio punto d'ingresso: `missions_for` ne deriva le missioni (una per A-10C).
    missions = F.missions_for(blue, [(CUT_ORIGIN_X['casA'] + 80_000.0, 0.0)], mission_type='CAS',
                              target=F.group_target('Red-Line'), rules=HOLD)
    return [blue], [red], missions, CUT_DURATION


class TestS36WindowCut(F.LoggerSilencer, unittest.TestCase):
    """S36-CUT: la sessione finisce mentre l'A-10C e' ancora nella sfera della ZSU-57-2: la permanenza e' il tempo
    rimasto (1 / 3 / 10 s) e la Pd cala di `min(1, k / 3,2)` rispetto alla legge di prima."""

    SEEDS = CUT_SEEDS
    VARIANTS = CUT_VARIANT_NAMES

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        # Ciclo esterno sui seed, interno sulle varianti (stesso `session_id` per le varianti di un seed).
        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                cls.runs[variant].append(run_variant(session_id, build_cut, CUT_VARIANTS[variant]))

    def _detection(self, variant, index, prefix):
        """L'unica `Detection` della ZSU sull'A-10C `prefix` nella sessione `index` della variante."""
        _, results = self.runs[variant][index]
        found = detections_of(results, OBSERVER, f'Blue-CAS/{prefix}0')
        self.assertEqual(len(found), 1, (variant, index, prefix))
        return found[0]

    def _each(self, variants):
        """`(seed, indice, prefisso, secondi rimasti, variante)` per ogni seed, A-10C e variante data."""
        for index, seed in enumerate(self.SEEDS):
            for prefix, left in CUT_LEFT:
                for variant in variants:
                    yield seed, index, prefix, left, variant

    def test_exposure_is_the_time_left_in_the_session(self):
        """Con la legge accesa la permanenza e' il tempo rimasto alla sessione e il dwell e' quello del registro."""
        for seed, index, prefix, left, variant in self._each(('on',)):
            with self.subTest(session=seed, variant=variant, target=prefix):
                detection = self._detection(variant, index, prefix)
                self.assertAlmostEqual(detection.exposure_s, left, places=6)
                self.assertEqual(detection.dwell_time_s, ZSU_DWELL)

    def test_probability_is_scaled_by_the_dwell_factor(self):
        """`Pd` acceso = `min(1, k / 3,2) * Pd` spento = legge D-5 ricalcolata dai campi; stretta per `casA` e `casB`,
        uguale per `casC` (10 s >= 3,2 s)."""
        for seed, index, prefix, left, variant in self._each(('on',)):
            with self.subTest(session=seed, variant=variant, target=prefix):
                detection = self._detection(variant, index, prefix)
                reference = self._detection('off', index, prefix)
                self.assertAlmostEqual(detection.probability, min(1.0, left / ZSU_DWELL) * reference.probability,
                                       places=12)
                self.assertAlmostEqual(detection.probability, expected_probability(detection), places=12)

                if prefix == 'casC':
                    self.assertEqual(detection.probability, reference.probability)
                else:
                    self.assertLess(detection.probability, reference.probability)

    def test_same_draws_and_no_extra_detection(self):
        """Stesse estrazioni e stessa distanza a interruttore acceso e spento; la legge non aggiunge rilevamenti."""
        for seed, index, prefix, left, variant in self._each(('on',)):
            with self.subTest(session=seed, variant=variant, target=prefix):
                detection = self._detection(variant, index, prefix)
                reference = self._detection('off', index, prefix)
                self.assertEqual(detection.draw, reference.draw)
                self.assertEqual(detection.distance_cpa, reference.distance_cpa)

                if detection.detected:
                    self.assertTrue(reference.detected)

    def test_detection_is_never_earlier(self):
        """Con `g < 1` il raggio estratto (`detection_radius`) e' minore: un rilevamento che avviene comunque non
        puo' essere piu' precoce di quello della legge di prima."""
        later = 0

        for seed, index, prefix, left, variant in self._each(('on',)):
            with self.subTest(session=seed, variant=variant, target=prefix):
                detection = self._detection(variant, index, prefix)
                reference = self._detection('off', index, prefix)

                if detection.detected and reference.detected:
                    self.assertGreaterEqual(detection.time, reference.time)

                    if detection.time > reference.time:
                        later += 1

        # Premessa non vacua: almeno un rilevamento viene davvero posticipato (P-4/P-16: seme 0, casB0).
        self.assertGreater(later, 0)

    def test_premise_no_salvo(self):
        """La permanenza e' piu' breve della reazione della ZSU (5,1 s) o i bersagli sono in `weapon_hold`: nessuna
        salva in nessuna variante e seme."""
        for variant in self.VARIANTS:
            for seed, (outcome, _) in zip(self.SEEDS, self.runs[variant]):
                with self.subTest(variant=variant, session=seed):
                    self.assertEqual(len(outcome.ammunition_events), 0)


# ── S36-PASSES ──────────────────────────────────────────────────────────────────────────────────────────────────────

PASS_SEEDS = [f'S36-PASSES-{index}' for index in range(SEEDS_PER_SCENARIO)]
PASS_S = 1.0                                               # durata di ciascun passaggio [s], geometria di test
PASS_HALF_CHORD = A10_SPEED * PASS_S / 2                   # 77,778 m
PASS_OFFSET = math.sqrt(HORIZONTAL_RADIUS ** 2 - PASS_HALF_CHORD ** 2)   # 5195,570 m [C]
PASS_GAP = {'join': 1.0, 'split': 5.0}                     # uscita fra i due passaggi [s]: <= e > dwell 3,2 s
# variante -> (uscita, interruttore D5_DWELL_TIME)
PASS_VARIANTS = {'join_off': ('join', False), 'join_on': ('join', True),
                 'split_off': ('split', False), 'split_on': ('split', True)}
PASS_VARIANT_NAMES = tuple(PASS_VARIANTS)
PASS_TARGET = 'Blue-CAS/cas0'


def build_passes(gap: str):
    """Costruttore (per `run_variant`) di S36-PASSES: la ZSU-57-2 e un A-10C che attraversa la sfera due volte con una
    corda di 1 s ciascuna, sulla stessa retta, separate da un'uscita di `PASS_GAP[gap]` secondi (andata oltre la
    corda, inversione fuori dalla sfera, ritorno: come il `REENTRY` di S33)."""
    def build():
        red = F.build_force('Red-Line', 'Red', [F.Unit('vehicle', ZSU, 1, origin=(0.0, 0.0), prefix='obs')])
        blue = F.build_force('Blue-CAS', 'Blue', [
            F.Unit('aircraft', A10, 1, origin=(-20_000.0, PASS_OFFSET, TARGET_Z), prefix='cas',
                   loadout=A10_LOADOUT)], mil_category=F.AIR_UNIT)
        turn = PASS_HALF_CHORD + A10_SPEED * PASS_GAP[gap] / 2.0     # 155,556 m (join) / 466,667 m (split) [C]
        missions = F.missions_for(blue, [(turn, PASS_OFFSET), (-20_000.0, PASS_OFFSET)], mission_type='CAS',
                                  target=F.group_target('Red-Line'), rules=HOLD)
        return [blue], [red], missions, DURATION

    return build


class TestS36PassJoin(F.LoggerSilencer, unittest.TestCase):
    """S36-PASSES: due passaggi di 1 s nella sfera della ZSU-57-2 con il dwell del registro (3,2 s): se l'uscita e'
    di 1 s (<= dwell) l'unione FP-10 li fa UNO solo, di permanenza uguale all'arco totale (uscita compresa); se e' di
    5 s (> dwell) restano due, ognuno con la propria permanenza."""

    SEEDS = PASS_SEEDS
    VARIANTS = PASS_VARIANT_NAMES

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        # Ciclo esterno sui seed, interno sulle varianti (stesso `session_id` per le varianti di un seed).
        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                gap, switch = PASS_VARIANTS[variant]
                cls.runs[variant].append(run_variant(session_id, build_passes(gap), switch))

    def _detections(self, variant, index):
        """Le `Detection` della ZSU sull'A-10C nella sessione `index` della variante."""
        _, results = self.runs[variant][index]
        return detections_of(results, OBSERVER, PASS_TARGET)

    def test_premise_two_one_second_passes(self):
        """Spento ci sono DUE passaggi da 1 s e l'uscita fra l'uno e l'altro vale 1 s (join) o 5 s (split)."""
        for variant in ('join_off', 'split_off'):
            for index, seed in enumerate(self.SEEDS):
                with self.subTest(session=seed, variant=variant):
                    found = self._detections(variant, index)
                    self.assertEqual(len(found), 2)
                    self.assertEqual([d.pass_index for d in found], [0, 1])
                    self.assertEqual([d.pass_count for d in found], [2, 2])

                    for detection in found:
                        self.assertAlmostEqual(detection.pass_end - detection.pass_start, PASS_S, places=6)

                    self.assertAlmostEqual(found[1].pass_start - found[0].pass_end,
                                           PASS_GAP[PASS_VARIANTS[variant][0]], places=6)

    def test_join_on_merges_the_passes_over_the_exit(self):
        """Acceso con uscita di 1 s: UNA `Detection`, la cui permanenza e' l'arco con l'uscita (3,0 s), non la somma
        dei due passaggi (2,0 s); g = 3,0 / 3,2."""
        for index, seed in enumerate(self.SEEDS):
            with self.subTest(session=seed):
                found = self._detections('join_on', index)
                self.assertEqual(len(found), 1)
                detection = found[0]
                self.assertIsNone(detection.pass_index)
                self.assertAlmostEqual(detection.exposure_s, 2 * PASS_S + PASS_GAP['join'], places=6)
                self.assertEqual(detection.dwell_time_s, ZSU_DWELL)
                self.assertAlmostEqual(detection.probability, expected_probability(detection), places=12)

    def test_split_on_scales_each_pass(self):
        """Acceso con uscita di 5 s (> dwell): nessuna unione, due `Detection` da 1,0 s ciascuna, g = 1,0 / 3,2."""
        for index, seed in enumerate(self.SEEDS):
            with self.subTest(session=seed):
                found = self._detections('split_on', index)
                self.assertEqual(len(found), 2)
                self.assertEqual([d.pass_index for d in found], [0, 1])

                for detection in found:
                    self.assertAlmostEqual(detection.exposure_s, PASS_S, places=6)
                    self.assertEqual(detection.dwell_time_s, ZSU_DWELL)
                    self.assertAlmostEqual(detection.probability, expected_probability(detection), places=12)

    def test_draw_streams_are_shared(self):
        """La `draw` del primo rilevamento e' la stessa nelle 4 varianti (stream dell'ingaggio); quella del secondo
        passaggio e' la stessa in `join_off`, `split_off` e `split_on` (stream `pass_rng`)."""
        for index, seed in enumerate(self.SEEDS):
            with self.subTest(session=seed):
                firsts = {variant: self._detections(variant, index)[0].draw for variant in self.VARIANTS}
                self.assertEqual(len(set(firsts.values())), 1, firsts)
                seconds = {variant: self._detections(variant, index)[1].draw
                           for variant in ('join_off', 'split_off', 'split_on')}
                self.assertEqual(len(set(seconds.values())), 1, seconds)

    def test_merge_removes_the_second_draw(self):
        """L'unione toglie la seconda estrazione (`join_on`: 1 contro 2 di `join_off`); nessuna salva in nessuna
        variante."""
        for index, seed in enumerate(self.SEEDS):
            with self.subTest(session=seed):
                self.assertEqual(len(self._detections('join_on', index)), 1)
                self.assertEqual(len(self._detections('join_off', index)), 2)

        for variant in self.VARIANTS:
            for seed, (outcome, _) in zip(self.SEEDS, self.runs[variant]):
                with self.subTest(variant=variant, session=seed):
                    self.assertEqual(len(outcome.ammunition_events), 0)


# ── famiglie di sensori (S36-FAMILIES, S36-BAND) ────────────────────────────────────────────────────────────────────

# nome: (tipo, modello, portata aria di acquisizione [m], dwell del registro [s], mil_category)
# Portate e dwell sono copie dei registri (test di premessa); i dwell sono STIME [S] salvo dove indicato (Registro_Dwell_Stimati.md).
GROUND_FAMILIES = {
    'strela10': ('vehicle', '9K35-Strela-10', 10_000.0, 3.2, F.GROUND_UNIT),   # TVD, STIMA [S] DW9-6
    'tor':      ('vehicle', '9K331-Tor', 25_000.0, 3.0, F.GROUND_UNIT),        # FONTE
    'buk':      ('vehicle', '9K37-Buk', 85_000.0, 9.0, F.GROUND_UNIT),         # FONTE NON VERIFICATA [S]
    's300':     ('vehicle', 'S-300PS', 150_000.0, 12.0, F.GROUND_UNIT),        # STIMA PER CONFRONTO [S]
    'p37':      ('vehicle', 'P-37-Mech', 280_000.0, 14.1, F.GROUND_UNIT),      # FONTE, valore centrale
    'ffg46':    ('ship', 'FFG-46', 350_000.0, 5.0, F.NAVAL_UNIT),              # SPS-49, FONTE
}
E3A = 'E-3A Sentry'
E3A_RANGE = 400_000.0                    # portata aria (acquisizione) del registro [m] (copia)
E3A_DWELL = 10.0                         # dwell_time_s del registro [s] (copia; STIMA [S])
E3A_Z = 9_000.0                          # quota dell'AWACS [m], geometria di test
E3A_SPEED = 208.33333333333331           # speed['nominal'] del registro [m/s] (copia, test di premessa)
MIG = 'MiG-29S'
MIG_SPEED = 255.55555555555554           # speed['nominal'] del registro [m/s] (copia, test di premessa)
FAMILY_EXPOSURE_RATIO = 0.5              # permanenza = meta' del dwell (g = 0,5), geometria di test
FAMILY_TARGET = 'Blue-CAS/cas0'          # bersaglio delle famiglie a terra/mare
AWACS_OBSERVER = 'Blue-AEW/obs0'         # osservatore della leva C
AWACS_TARGET = 'Red-Air/tgt0'            # bersaglio della leva C


def build_ground_family(name: str, declared_dwell=None):
    """Costruttore (per `run_variant`) di una famiglia a terra o in mare: l'osservatore reale a `(0, 0)` e un A-10C a
    3000 m che gli passa accanto con la permanenza nel volume pari a meta' del dwell del REGISTRO (g = 0,5), anche se
    `declared_dwell` (valore di prova della banda, `F.declare_dwell` sull'istanza) sostituisce il dwell letto."""
    kind, model, sensor_range, dwell, mil_category = GROUND_FAMILIES[name]

    def build():
        red = F.build_force('Red-Line', 'Red', [F.Unit(kind, model, 1, origin=(0.0, 0.0), prefix='obs')],
                            mil_category=mil_category)

        if declared_dwell is not None:
            F.declare_dwell(red.assets[OBSERVER], {'air': declared_dwell})

        offset = lateral_offset(sensor_range, TARGET_Z, A10_SPEED, dwell * FAMILY_EXPOSURE_RATIO)
        blue = F.build_force('Blue-CAS', 'Blue', [
            F.Unit('aircraft', A10, 1, origin=(-20_000.0, offset, TARGET_Z), prefix='cas', loadout=A10_LOADOUT)],
            mil_category=F.AIR_UNIT)
        missions = F.missions_for(blue, [(20_000.0, offset)], mission_type='CAS', target=F.group_target('Red-Line'),
                                  rules=HOLD)
        return [blue], [red], missions, DURATION

    return build


def build_awacs():
    """Costruttore (per `run_variant`) della leva C: l'E-3A (osservatore mobile, 208,3 m/s verso +x a 9000 m) e un
    MiG-29S che gli viene incontro (255,6 m/s verso -x a 3000 m) con una permanenza di meta' del dwell (5 s) nella
    sfera di 400 km. Senza missione un aereo e' a terra e non osserva: l'E-3A ha una missione AWACS."""
    x0 = (E3A_SPEED + MIG_SPEED) * 200.0         # il MiG parte da 92777,778 m: l'incontro e' a t = 200 s [C]
    offset = lateral_offset(E3A_RANGE, E3A_Z - TARGET_Z, E3A_SPEED + MIG_SPEED, E3A_DWELL * FAMILY_EXPOSURE_RATIO)
    blue = F.build_force('Blue-AEW', 'Blue', [F.Unit('aircraft', E3A, 1, origin=(0.0, 0.0, E3A_Z), prefix='obs')],
                         mil_category=F.AIR_UNIT)
    missions = F.missions_for(blue, [(E3A_SPEED * 600.0, 0.0)], mission_type='AWACS',
                              target=F.zone_target((E3A_SPEED * 300.0, 0.0, E3A_Z), 50_000.0))
    red = F.build_force('Red-Air', 'Red', [F.Unit('aircraft', MIG, 1, origin=(x0, offset, TARGET_Z), prefix='tgt')],
                        mil_category=F.AIR_UNIT)
    missions += F.missions_for(red, [(x0 - MIG_SPEED * 600.0, offset)], mission_type='Fighter_Sweep',
                               target=F.group_target('Blue-AEW'), rules=HOLD)
    return [blue], [red], missions, DURATION


# ── S36-FAMILIES ────────────────────────────────────────────────────────────────────────────────────────────────────

FAMILY_SEEDS = [f'S36-FAMILIES-{index}' for index in range(SEEDS_PER_SCENARIO)]
FAMILY_VARIANTS = ('strela10', 'tor', 'buk', 's300', 'p37', 'ffg46', 'e3a')   # tutte con D-5 accesa e dwell del registro
FAMILY_OBSERVER = {**{name: OBSERVER for name in GROUND_FAMILIES}, 'e3a': AWACS_OBSERVER}
FAMILY_TARGETS = {**{name: FAMILY_TARGET for name in GROUND_FAMILIES}, 'e3a': AWACS_TARGET}
FAMILY_RANGE = {**{name: spec[2] for name, spec in GROUND_FAMILIES.items()}, 'e3a': E3A_RANGE}
FAMILY_DWELL = {**{name: spec[3] for name, spec in GROUND_FAMILIES.items()}, 'e3a': E3A_DWELL}


def build_family(name: str):
    """Costruttore di una variante di S36-FAMILIES (dwell del registro): `build_awacs` per `e3a`."""
    return build_awacs if name == 'e3a' else build_ground_family(name)


class TestS36Families(F.LoggerSilencer, unittest.TestCase):
    """S36-FAMILIES: per ogni famiglia di sensori (visivo/TVD, SAM, radar di ricerca, nave, AWACS in moto) un bersaglio
    resta nel volume per meta' del dwell del REGISTRO: la Pd e' la meta' di quella della legge di prima.

    Nessuna salva: per Strela-10 (reazione 5,6 s contro dwell 3,2 s), Tor (6,5 contro 3,0), Buk (27,1 contro 9,0) e
    S-300PS (28,0 contro 12,0) la reazione e' maggiore del dwell, quindi un passaggio piu' breve del dwell non puo'
    finire in una salva; gli altri osservatori sono radar di ricerca, navi e AWACS in `weapon_hold`/senza armi
    contro aerei a quella distanza."""

    SEEDS = FAMILY_SEEDS
    VARIANTS = FAMILY_VARIANTS

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        # Ciclo esterno sui seed, interno sulle varianti (stesso `session_id` per le varianti di un seed).
        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                cls.runs[variant].append(run_variant(session_id, build_family(variant), True))

    def _detection(self, variant, index):
        """L'unica `Detection` dell'osservatore della famiglia sul bersaglio nella sessione `index`."""
        _, results = self.runs[variant][index]
        found = detections_of(results, FAMILY_OBSERVER[variant], FAMILY_TARGETS[variant])
        self.assertEqual(len(found), 1, (variant, index))
        return found[0]

    def _each(self):
        """`(seed, indice, variante)` per ogni seed e famiglia."""
        for index, seed in enumerate(self.SEEDS):
            for variant in self.VARIANTS:
                yield seed, index, variant

    def test_premise_registry_values(self):
        """Le copie dei registri valgono ancora: portata e dwell aria di ogni osservatore reale, velocita' nominali."""
        for name, (kind, model, sensor_range, dwell, mil_category) in GROUND_FAMILIES.items():
            with self.subTest(family=name):
                force = F.build_force('Red-Line', 'Red', [F.Unit(kind, model, 1, origin=(0.0, 0.0), prefix='obs')],
                                      mil_category=mil_category)
                self.assertEqual(force.assets[OBSERVER].detection_range('air'), sensor_range)
                self.assertEqual(force.assets[OBSERVER].detection_dwell_time('air'), dwell)

        with self.subTest(family='e3a'):
            awacs = F.build_force('Blue-AEW', 'Blue', [F.Unit('aircraft', E3A, 1, origin=(0.0, 0.0, E3A_Z),
                                                              prefix='obs')], mil_category=F.AIR_UNIT)
            fighter = F.build_force('Red-Air', 'Red', [F.Unit('aircraft', MIG, 1, origin=(0.0, 0.0, TARGET_Z),
                                                              prefix='tgt')], mil_category=F.AIR_UNIT)
            attacker = F.build_force('Blue-CAS', 'Blue', [F.Unit('aircraft', A10, 1, origin=(0.0, 0.0, TARGET_Z),
                                                                 prefix='cas', loadout=A10_LOADOUT)],
                                     mil_category=F.AIR_UNIT)
            self.assertEqual(awacs.assets[AWACS_OBSERVER].detection_range('air'), E3A_RANGE)
            self.assertEqual(awacs.assets[AWACS_OBSERVER].detection_dwell_time('air'), E3A_DWELL)
            self.assertAlmostEqual(awacs.assets[AWACS_OBSERVER].speed['nominal'], E3A_SPEED, places=9)
            self.assertAlmostEqual(fighter.assets[AWACS_TARGET].speed['nominal'], MIG_SPEED, places=9)
            self.assertAlmostEqual(attacker.assets[FAMILY_TARGET].speed['nominal'], A10_SPEED, places=9)

    def test_exposure_is_half_the_dwell(self):
        """La permanenza e' meta' del dwell del registro (g = 0,5); il dwell e la portata sono quelli del registro."""
        for seed, index, variant in self._each():
            with self.subTest(session=seed, family=variant):
                detection = self._detection(variant, index)
                self.assertAlmostEqual(detection.exposure_s, FAMILY_DWELL[variant] * FAMILY_EXPOSURE_RATIO, places=6)
                self.assertEqual(detection.dwell_time_s, FAMILY_DWELL[variant])
                self.assertEqual(detection.sensor_range, FAMILY_RANGE[variant])

    def test_probability_is_half_the_previous_law(self):
        """`Pd` = legge D-5 ricalcolata dai campi = meta' della Pd della legge di prima; il bersaglio entra nella sfera
        (la Pd di prima e' positiva)."""
        for seed, index, variant in self._each():
            with self.subTest(session=seed, family=variant):
                detection = self._detection(variant, index)
                self.assertGreater(previous_probability(detection), 0.0)
                self.assertAlmostEqual(detection.probability, expected_probability(detection), places=12)
                # La permanenza esce dalla corda con un errore di arrotondamento che cresce con la portata (fino a
                # 1,2e-8 s per la FFG-46 a 350 km), quindi g = 0,5 vale a ~7 cifre, non a 12: tolleranza come quella
                # della permanenza (places=6). `expected_probability` (sopra) usa gli stessi campi ed e' esatta.
                self.assertAlmostEqual(detection.probability, FAMILY_EXPOSURE_RATIO * previous_probability(detection),
                                       places=6)

    def test_no_salvo_on_a_pass_shorter_than_the_dwell(self):
        """Nessuna salva in nessuna famiglia e seme: il tempo di reazione di ogni tiratore supera il suo dwell (v. il
        docstring della classe e quello del modulo)."""
        for variant in self.VARIANTS:
            for seed, (outcome, _) in zip(self.SEEDS, self.runs[variant]):
                with self.subTest(family=variant, session=seed):
                    self.assertEqual(len(outcome.ammunition_events), 0)

    def test_targets_read_no_dwell(self):
        """Gli aerei bersaglio (A-10C, MiG-29S) osservano a loro volta senza dwell nei registri: nelle loro `Detection`
        permanenza e dwell sono None."""
        for seed, index, variant in self._each():
            with self.subTest(session=seed, family=variant):
                _, results = self.runs[variant][index]

                for detection in detections_of(results, FAMILY_TARGETS[variant]):
                    self.assertIsNone(detection.dwell_time_s)
                    self.assertIsNone(detection.exposure_s)


# ── S36-BAND ────────────────────────────────────────────────────────────────────────────────────────────────────────

BAND_SEEDS = [f'S36-BAND-{index}' for index in range(SEEDS_PER_SCENARIO)]
# Estremi della banda di incertezza [s] dichiarata con il valore del registro (Proposta_Dwell_Estensione_DW9.md §2.1-§2.4;
# Rapporti/Sonde_Dwell_D5/probe_dw9.py, VALUES): VALORI DI PROVA, non dati. `tor_max`, `s300_max` e `ffg46_min`
# coincidono con il valore del registro: tenuti per regolarita'.
BAND = {'strela10': (1.75, 6.0), 'tor': (1.0, 3.0), 'buk': (4.3, 20.0), 's300': (5.0, 12.0),
        'p37': (10.0, 20.0), 'ffg46': (5.0, 10.0)}
BAND_VARIANTS = ('strela10_min', 'strela10_max', 'tor_min', 'tor_max', 'buk_min', 'buk_max',
                 's300_min', 's300_max', 'p37_min', 'p37_max', 'ffg46_min', 'ffg46_max')


def band_value(variant: str):
    """`(famiglia, dwell dichiarato [s])` di una variante di S36-BAND (`<famiglia>_min` o `<famiglia>_max`)."""
    name, extreme = variant.rsplit('_', 1)
    return name, BAND[name][0 if extreme == 'min' else 1]


class TestS36Band(F.LoggerSilencer, unittest.TestCase):
    """S36-BAND: stessa geometria delle sei famiglie a terra/mare (permanenza = meta' del dwell del REGISTRO), con il
    dwell dichiarato agli estremi `min` e `max` della banda di incertezza (valori di prova): dwell piu' corto, Pd piu'
    alta."""

    SEEDS = BAND_SEEDS
    VARIANTS = BAND_VARIANTS

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        # Ciclo esterno sui seed, interno sulle varianti (stesso `session_id` per le varianti di un seed).
        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                name, value = band_value(variant)
                cls.runs[variant].append(run_variant(session_id, build_ground_family(name, value), True))

    def _detection(self, variant, index):
        """L'unica `Detection` dell'osservatore sul bersaglio nella sessione `index` della variante."""
        _, results = self.runs[variant][index]
        found = detections_of(results, OBSERVER, FAMILY_TARGET)
        self.assertEqual(len(found), 1, (variant, index))
        return found[0]

    def _each(self):
        """`(seed, indice, variante)` per ogni seed e variante."""
        for index, seed in enumerate(self.SEEDS):
            for variant in self.VARIANTS:
                yield seed, index, variant

    def test_declared_dwell_is_read(self):
        """Il dwell della `Detection` e' quello dichiarato; la permanenza resta meta' del dwell del registro."""
        for seed, index, variant in self._each():
            with self.subTest(session=seed, variant=variant):
                name, value = band_value(variant)
                detection = self._detection(variant, index)
                self.assertEqual(detection.dwell_time_s, value)
                self.assertAlmostEqual(detection.exposure_s, GROUND_FAMILIES[name][3] * FAMILY_EXPOSURE_RATIO,
                                       places=6)

    def test_probability_is_monotone_in_the_dwell(self):
        """`Pd` = legge D-5 ricalcolata dai campi; per famiglia e seme `p(min) >= p_registro >= p(max)`, con
        `p_registro` calcolata sulla stessa `Detection` con il dwell del registro."""
        for index, seed in enumerate(self.SEEDS):
            for name in GROUND_FAMILIES:
                with self.subTest(session=seed, family=name):
                    low, high = self._detection(f'{name}_min', index), self._detection(f'{name}_max', index)
                    registry = ER.detection_probability(
                        low.distance_cpa, low.sensor_range, ER.dwell_factor(low.exposure_s, GROUND_FAMILIES[name][3]))

                    for detection in (low, high):
                        self.assertAlmostEqual(detection.probability, expected_probability(detection), places=12)

                    self.assertGreaterEqual(low.probability + 1e-12, registry)
                    self.assertGreaterEqual(registry + 1e-12, high.probability)

    def test_detected_with_max_is_subset_of_min(self):
        """Stessa estrazione fra `_min` e `_max` dello stesso seme; rilevato con il dwell piu' lungo implica rilevato
        con il piu' corto."""
        for index, seed in enumerate(self.SEEDS):
            for name in GROUND_FAMILIES:
                with self.subTest(session=seed, family=name):
                    low, high = self._detection(f'{name}_min', index), self._detection(f'{name}_max', index)
                    self.assertEqual(low.draw, high.draw)

                    if high.detected:
                        self.assertTrue(low.detected)


# ── test dello strumento ────────────────────────────────────────────────────────────────────────────────────────────

class TestS36BaselineDetections(unittest.TestCase):
    """La voce `detections` della fotografia (`Scenario_Baseline`): solo per le unita' S36, non per le altre. Non e' in
    `UNITS` (`capture` silenzia da se' i logger)."""

    def test_detection_units_are_the_s36_tail(self):
        """`DETECTION_UNITS` sono le cinque unita' S36, le ultime di `UNITS`: nessuna unita' precedente registra le
        `Detection`."""
        tail = ['S36-GRAZE', 'S36-CUT', 'S36-PASSES', 'S36-FAMILIES', 'S36-BAND']
        self.assertEqual(SB.DETECTION_UNITS, frozenset(tail))
        self.assertEqual([unit[0] for unit in SB.UNITS[-5:]], tail)

    def test_capture_records_the_detections_voice(self):
        """`capture` di S36-CUT: 8 esecuzioni, ognuna con la voce `detections` a righe di `DETECTION_FIELDS`; nelle
        `/on` le righe della ZSU portano il dwell del registro (3,2 s), nelle `/off` None."""
        snapshot = SB.capture(only='^S36-CUT$', verbose=False)
        self.assertEqual(snapshot['errors'], {})
        self.assertEqual(len(snapshot['runs']), 8)
        dwell_index = SB.DETECTION_FIELDS.index('dwell_time_s')

        for key, run in snapshot['runs'].items():
            with self.subTest(run=key):
                self.assertIn('detections', run)

                for row in run['detections']:
                    self.assertEqual(len(row), len(SB.DETECTION_FIELDS))

                zsu_rows = [row for row in run['detections'] if row[0] == OBSERVER]
                self.assertTrue(zsu_rows)

                for row in zsu_rows:
                    self.assertEqual(row[dwell_index], ZSU_DWELL if key.endswith('/on') else None)


if __name__ == '__main__':
    unittest.main()
