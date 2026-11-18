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

Questo modulo contiene gli aiuti comuni e `S36-GRAZE` (blocco 2 della Proposta): le altre unita' lo estendono.

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


if __name__ == '__main__':
    unittest.main()
