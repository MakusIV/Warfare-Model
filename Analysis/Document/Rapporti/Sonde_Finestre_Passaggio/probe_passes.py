"""Sonda di sola lettura P-0 di `Proposta_Finestre_Per_Passaggio_Portata_Propria.md` (passo 0, prima di ogni codice).

Conta, nelle esecuzioni della fotografia, le DIREZIONI di rilevamento (osservatore -> bersaglio dentro una
`ContactWindow`) in cui il bersaglio entra PIU' DI UNA VOLTA nel volume di rilevamento PROPRIO dell'osservatore dentro
la stessa finestra: sono le estrazioni che la regola "un'occasione di rilevamento per passaggio" aggiungerebbe.

NON cambia il comportamento del motore:
  * avvolge `_EngagementRun._detect_direction`: chiama l'originale, POI misura i passaggi dai tratti
    (`range_intervals` con la portata propria), senza consumare l'RNG;
  * avvolge `_EngagementRun.run`: dopo l'esito, confronta le salve dell'osservatore con i suoi passaggi;
  * aggiunge al riassunto di ogni esecuzione una voce `probe_passes` (azzerata a ogni `run_session`) e riesegue
    `Scenario_Baseline --compare` con `--ignore probe_passes`: il confronto deve restare quello di oggi
    (nessuna riga DIFF; oggi 20 righe NEW di S32-DWELL, che non e' nella fotografia).
Nessun file del repository viene scritto; l'uscita va in `<out_dir>` (capture.json, stats.json).

Regola dei passaggi (identica a quella del piano, §4.1 punto 3): per la direzione osservatore -> bersaglio, gli
intervalli `(start, end)` di `range_intervals(tratti_oss, tratti_bers, portata_propria)` che toccano la finestra
(`end >= t_start - TIME_EPS` e `start <= t_end + TIME_EPS`), ritagliati a `[lo, hi]` con `lo = max(start, t_start)`,
`hi = max(lo, min(end, t_end))`. Una direzione e' "multi" se ha >= 2 passaggi.

uso (dalla root del repo, PYTHONPATH=.):
    <python> probe_passes.py <out_dir> [<regex per --only>]
"""
import json
import sys
from collections import Counter

from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic import Session_Simulator as SS
from Code.Dynamic_War_Manager.Source.Logic.Contact_Scheduler import (
    TIME_EPS, clamp_legs, closest_point_of_approach, range_intervals)
from Code.Dynamic_War_Manager.Source.Test import Scenario_Baseline as SB

OUT = sys.argv[1]
ONLY = sys.argv[2] if len(sys.argv) > 2 else None
BASELINE = 'Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json'
KEY = 'probe_passes'

COUNTERS = (
    'engagements',                     # run del risolutore nell'esecuzione
    'salvos',                          # salve totali
    'directions',                      # direzioni con estrazione (una Detection)
    'without_legs',                    # direzioni senza tratti (passaggi non calcolabili: una estrazione anche con la regola)
    'multi',                           # direzioni con >= 2 passaggi nel volume proprio
    'multi_outer',                     # ... di cui con portata propria NON minore (atteso 0: controllo di coerenza)
    'extra_draws',                     # estrazioni in piu' con la regola (somma di n - 1)
    'max_passes',                      # massimo n in una direzione
    'cpa_not_in_first',                # multi con il CPA della finestra fuori dal primo passaggio (Pd del primo cambia)
    'multi_detected',                  # multi in cui l'estrazione unica di oggi rileva
    'multi_detected_after_first',      # ... e l'istante di rilevamento cade in un passaggio successivo al primo
    'first_flip_by_distance',          # multi rilevate oggi che col CPA del solo primo passaggio NON lo sarebbero
    'multi_with_salvos',               # multi rilevate con almeno una salva dell'osservatore sul bersaglio nella finestra
    'salvos_after_next_pass_start',    # salve partite dopo l'inizio del passaggio successivo a quello del rilevamento (FP-3)
    'salvos_between_passes',           # salve fra la fine del passaggio del rilevamento e l'inizio del successivo (FP-3 a/b)
    'inner_single_salvos_after_pass',  # osservatore con portata minore, 1 passaggio: salve dopo la fine del passaggio (FP-3 a)
    'rint_last_not_earliest',          # coppie con >= 2 rilevamenti a istanti diversi, l'ultimo != il primo (FP-5, R-INT)
)


def _new_bucket():
    bucket = {name: 0 for name in COUNTERS}
    bucket['hist'] = {}
    bucket['models'] = {}
    return bucket


_state = {'bucket': _new_bucket()}


def _model(asset):
    return str(getattr(asset, '_model', None) or getattr(asset, 'model', None) or type(asset).__name__)


def own_passes(run, window, observer_id, target_id, own_range):
    """Passaggi `(lo, hi, start, end)` del bersaglio nel volume proprio dell'osservatore dentro la finestra; None
    senza tratti."""
    legs_o, legs_t = run.legs.get(observer_id), run.legs.get(target_id)

    if not (legs_o and legs_t):
        return None

    passes = []

    for start, end in range_intervals(legs_o, legs_t, own_range):
        if end >= window.t_start - TIME_EPS and start <= window.t_end + TIME_EPS:
            lo = max(start, window.t_start)
            passes.append((lo, max(lo, min(end, window.t_end)), start, end))

    return passes


def _pass_index(passes, time):
    for index, (lo, hi, _, _) in enumerate(passes):
        if lo - TIME_EPS <= time <= hi + TIME_EPS:
            return index

    return None


_original_detect_direction = ER._EngagementRun._detect_direction


def _detect_direction(self, window, observer, target, own_range, other_range):
    before = len(self.detections)
    _original_detect_direction(self, window, observer, target, own_range, other_range)

    if len(self.detections) == before:
        return  # nessuna estrazione (portata assente, osservatore a terra): niente da misurare

    bucket = _state['bucket']
    bucket['directions'] += 1
    detection = self.detections[-1]
    passes = own_passes(self, window, observer.id, target.id, own_range)

    if passes is None:
        bucket['without_legs'] += 1
        return

    inner = other_range is not None and other_range > 0 and own_range < other_range
    n = len(passes)
    bucket['hist'][str(n)] = bucket['hist'].get(str(n), 0) + 1
    record = {'window': window, 'observer': observer.id, 'target': target.id, 'passes': passes, 'inner': inner,
              'detected_pass': None}

    if detection.detected and detection.time is not None:
        record['detected_pass'] = _pass_index(passes, detection.time)

    self.__dict__.setdefault('_probe_records', []).append(record)

    if n < 2:
        return

    bucket['multi'] += 1
    bucket['extra_draws'] += n - 1
    bucket['max_passes'] = max(bucket['max_passes'], n)

    if not inner:
        bucket['multi_outer'] += 1

    pair = f'{_model(observer.asset)} -> {_model(target.asset)}'
    bucket['models'][pair] = bucket['models'].get(pair, 0) + 1

    if _pass_index(passes, window.t_cpa) != 0:
        bucket['cpa_not_in_first'] += 1

    if detection.detected:
        bucket['multi_detected'] += 1

        if record['detected_pass'] not in (None, 0):
            bucket['multi_detected_after_first'] += 1

    # Pd del PRIMO passaggio con la sua distanza minima; fattore effettivo (meteo, nebbia, D-5) ricavato dalla Detection.
    distance = detection.distance_cpa
    base = ER.detection_probability(distance, own_range) if distance <= own_range else 0.0

    if base > 0.0 and detection.detected:
        factor = min(1.0, detection.probability / base)
        lo, hi = passes[0][0], passes[0][1]
        cpa = closest_point_of_approach(clamp_legs(self.legs[observer.id], lo, hi),
                                        clamp_legs(self.legs[target.id], lo, hi))

        if cpa is not None:
            d1 = max(float(cpa.distance), 0.0)
            p1 = ER.detection_probability(d1, own_range, factor) if d1 <= own_range else 0.0

            if not detection.draw < p1:
                bucket['first_flip_by_distance'] += 1


_original_run = ER._EngagementRun.run


def _run(self):
    result = _original_run(self)
    bucket = _state['bucket']
    bucket['engagements'] += 1
    bucket['salvos'] += len(result.salvos)

    for record in self.__dict__.get('_probe_records', ()):
        window, passes, k = record['window'], record['passes'], record['detected_pass']

        if k is None:
            continue

        mine = [s.t_launch for s in result.salvos
                if s.shooter_id == record['observer'] and s.target_id == record['target']
                and window.t_start - TIME_EPS <= s.t_launch <= window.t_end + TIME_EPS]

        if len(passes) >= 2:
            if mine:
                bucket['multi_with_salvos'] += 1

            if k + 1 < len(passes):
                next_start = passes[k + 1][0]
                bucket['salvos_after_next_pass_start'] += sum(1 for t in mine if t >= next_start - TIME_EPS)
                bucket['salvos_between_passes'] += sum(1 for t in mine
                                                       if passes[k][1] + TIME_EPS < t < next_start - TIME_EPS)
        elif record['inner'] and len(passes) == 1:
            bucket['inner_single_salvos_after_pass'] += sum(1 for t in mine if t > passes[0][1] + TIME_EPS)

    times = {}

    for detection in result.detections:
        if detection.detected and detection.time is not None:
            times.setdefault((detection.observer_id, detection.target_id), []).append(detection.time)

    for values in times.values():
        if len(values) >= 2 and abs(values[-1] - min(values)) > TIME_EPS:
            bucket['rint_last_not_earliest'] += 1

    return result


_original_run_session = SS.run_session


def _run_session(*args, **kwargs):
    _state['bucket'] = _new_bucket()
    return _original_run_session(*args, **kwargs)


_original_summarize = SB.summarize_run


def _summarize_run(order, forces_a, forces_b, kwargs, outcome):
    summary = _original_summarize(order, forces_a, forces_b, kwargs, outcome)
    summary[KEY] = _state['bucket']
    _state['bucket'] = _new_bucket()
    return summary


ER._EngagementRun._detect_direction = _detect_direction
ER._EngagementRun.run = _run
SS.run_session = _run_session
SB.summarize_run = _summarize_run

rc = SB.main(['--compare', BASELINE, '--save', f'{OUT}/capture.json', '--quiet', '--ignore', KEY]
             + (['--only', ONLY] if ONLY else []))
print('PROBE_RC', rc)

with open(f'{OUT}/capture.json', encoding='utf-8') as handle:
    runs = json.load(handle)['runs']

with open(BASELINE, encoding='utf-8') as handle:
    photo = set(json.load(handle).get('runs', {}))

totals, hist, models, by_unit = Counter(), Counter(), Counter(), Counter()
max_passes = 0
rows = {'MULTI': [], 'AFTER_PASS': [], 'RINT': []}

for key in sorted(runs):
    bucket = runs[key].get(KEY)

    if bucket is None:
        continue

    for name in COUNTERS:
        if name != 'max_passes':
            totals[name] += bucket[name]

    max_passes = max(max_passes, bucket['max_passes'])
    hist.update(bucket['hist'])
    models.update(bucket['models'])
    tag = '' if key in photo else ' [NUOVA]'

    if bucket['multi']:
        by_unit[key.split('/', 1)[0]] += 1
        rows['MULTI'].append(f"MULTI {key}{tag}: multi={bucket['multi']} extra={bucket['extra_draws']} "
                             f"max_n={bucket['max_passes']} cpa_not_first={bucket['cpa_not_in_first']} "
                             f"detected={bucket['multi_detected']} after_first={bucket['multi_detected_after_first']} "
                             f"flip_d1={bucket['first_flip_by_distance']} with_salvos={bucket['multi_with_salvos']} "
                             f"salvos_next_pass={bucket['salvos_after_next_pass_start']} "
                             f"salvos_gap={bucket['salvos_between_passes']} salvos={bucket['salvos']}")

    if bucket['inner_single_salvos_after_pass']:
        rows['AFTER_PASS'].append(f"AFTER_PASS {key}{tag}: {bucket['inner_single_salvos_after_pass']}")

    if bucket['rint_last_not_earliest']:
        rows['RINT'].append(f"RINT {key}{tag}: {bucket['rint_last_not_earliest']}")

multi_runs = [line for line in rows['MULTI']]
print(f'RUNS {len(runs)} (in fotografia {sum(k in photo for k in runs)}, nuove {sum(k not in photo for k in runs)})')
print(f"RUNS_WITH_MULTI {len(multi_runs)} (in fotografia {sum('[NUOVA]' not in line for line in multi_runs)})")
print(f"RUNS_WITH_AFTER_PASS {len(rows['AFTER_PASS'])}  RUNS_WITH_RINT {len(rows['RINT'])}")
print('TOTALS', json.dumps(dict(totals), sort_keys=True), 'MAX_PASSES', max_passes)
print('HIST', json.dumps(dict(sorted(hist.items(), key=lambda item: int(item[0])))))
print('UNITS', json.dumps(dict(sorted(by_unit.items()))))
print('MODELS', json.dumps(models.most_common(30)))

for name in ('MULTI', 'AFTER_PASS', 'RINT'):
    for line in rows[name]:
        print(line)

with open(f'{OUT}/stats.json', 'w', encoding='utf-8') as handle:
    json.dump({'totals': dict(totals), 'max_passes': max_passes, 'hist': dict(hist), 'units': dict(by_unit),
               'models': dict(models), 'rows': rows}, handle, indent=1, sort_keys=False)
