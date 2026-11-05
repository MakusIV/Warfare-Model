"""Sonda di sola lettura D-5 opzione 2 (dwell_time_s). Accende IN MEMORIA la legge
Pd = g * Pd(d_cpa), g = min(1, esposizione/dwell), sostituendo _EngagementRun._detect_direction,
e riesegue Scenario_Baseline --compare contro la fotografia, senza installare nulla.

uso: python3 probe_dwell.py <modo> <out_dir>
  modo = 'source'          dwell solo per i 10 EWR con giri/min di fonte (nessuno nella fotografia)
       = 'uniform:<s>'     dwell <s> per OGNI osservatore con portata (sensibilita')
In ogni modo registra, per ogni estrazione di rilevamento, l'esposizione e la decisione
controfattuale per una serie di dwell ipotetici (senza cambiare l'esito).
"""
import json
import sys
from collections import Counter, defaultdict

from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic.Contact_Scheduler import TIME_EPS, range_intervals
from Code.Dynamic_War_Manager.Source.Context import Air_Defense_Efficacy as ADE
from Code.Dynamic_War_Manager.Source.Test import Scenario_Baseline as SB

MODE = sys.argv[1]
OUT = sys.argv[2]

SOURCE_DWELL = {  # 60 / giri al minuto (regola: rotazione piu' veloce dell'intervallo di fonte)
    'SCR-270': 60.0, 'P-12-Yenisei': 6.0, 'P-18-Terek': 6.0, 'P-37-Mech': 10.0, '1L13-Nebo-SV': 10.0,
    '55Zh6-Nebo': 10.0, 'AN-TPS-43': 10.0, 'AMES-Type-7': 7.5, 'AMES-Type-80': 10.0, 'P-14-Lena': 10.0,
}
COUNTERFACTUAL = (2.0, 6.0, 10.0, 30.0, 60.0, 120.0)

stats = {'directions': 0, 'with_legs': 0, 'without_legs': 0, 'dwell_applied': 0, 'g_below_1': 0,
         'flipped_actual': 0, 'models_with_dwell': Counter(),
         'cf': {str(t): {'g_below_1': 0, 'flipped': 0, 'detected_old': 0, 'detected_new': 0} for t in COUNTERFACTUAL},
         'exposure_hist': Counter()}


def dwell_for(observer_asset, own_range):
    if MODE == 'source':
        return SOURCE_DWELL.get(getattr(observer_asset, '_model', None))
    if MODE.startswith('uniform:'):
        return float(MODE.split(':', 1)[1])
    raise SystemExit(f'modo sconosciuto {MODE}')


def exposure(run, window, observer_id, target_id, own_range, other_range):
    legs_o, legs_t = run.legs.get(observer_id), run.legs.get(target_id)
    if legs_o and legs_t:
        stats['with_legs'] += 1
        total = 0.0
        for start, end in range_intervals(legs_o, legs_t, own_range):
            if end < window.t_start - TIME_EPS or start > window.t_end + TIME_EPS:
                continue
            total += max(0.0, min(end, window.t_end) - start)
        return total
    stats['without_legs'] += 1
    if other_range is None or own_range >= other_range:
        return max(0.0, window.t_end - window.t_start)
    if window.t_mutual_start is not None and window.t_mutual_end is not None:
        return max(0.0, window.t_mutual_end - window.t_mutual_start)
    return 0.0


def g_of(exp, dwell):
    if dwell is None or dwell <= 0:
        return 1.0
    return min(1.0, max(0.0, exp) / dwell)


def bucket(exp):
    for edge in (1, 2, 6, 10, 30, 60, 120, 300, 600, 1800):
        if exp < edge:
            return f'<{edge}'
    return '>=1800'


def _detect_direction(self, window, observer, target, own_range, other_range):
    if own_range is None or own_range <= 0:
        return
    if self._grounded_in(observer.id, window):
        return
    factor = 1.0
    if self.detection_factor is not None:
        factor = ER._check_factor(self.detection_factor(observer.asset, target.asset))

    distance = max(float(window.distance_cpa), 0.0)
    exp = exposure(self, window, observer.id, target.id, own_range, other_range)
    stats['directions'] += 1
    stats['exposure_hist'][bucket(exp)] += 1
    dwell = dwell_for(observer.asset, own_range)
    g = g_of(exp, dwell)
    if dwell is not None and dwell > 0:
        stats['dwell_applied'] += 1
        stats['models_with_dwell'][getattr(observer.asset, '_model', None)] += 1
        if g < 1.0:
            stats['g_below_1'] += 1

    draw = self._draw()
    p_old = ER.detection_probability(distance, own_range, factor) if distance <= own_range else 0.0
    for t in COUNTERFACTUAL:
        gc = g_of(exp, t)
        p_cf = ER.detection_probability(distance, own_range, factor * gc) if distance <= own_range else 0.0
        c = stats['cf'][str(t)]
        c['g_below_1'] += gc < 1.0
        c['detected_old'] += draw < p_old
        c['detected_new'] += draw < p_cf
        c['flipped'] += (draw < p_old) and not (draw < p_cf)

    eff = factor * g
    probability = ER.detection_probability(distance, own_range, eff) if distance <= own_range else 0.0
    detected = draw < probability
    if (draw < p_old) and not detected:
        stats['flipped_actual'] += 1
    time = None
    if detected:
        radius = ER.detection_radius(draw, own_range, eff)
        time = self._detection_time(window, observer.id, target.id, own_range, other_range, radius)
        self._perceive(observer.force_id, target.id, time)
        identified = self.identified_by.setdefault(self.domain_of[observer.force_id], {})
        identified[target.id] = min(identified.get(target.id, time), time)
        if not self._grounded_in(target.id, window) \
                and ADE.rwr_perception(target.asset, observer.asset) == ADE.PERCEIVED_AT_DETECTION:
            self._perceive_rwr(target, observer, time)
        t_ready = time + self._profile(observer.id).total
        if t_ready <= window.t_end + TIME_EPS:
            self.candidates.setdefault(observer.id, []).append(
                ER._Candidate(t_ready=t_ready, target_id=target.id, t_end=window.t_end,
                              t_cpa=float(window.t_cpa), distance_cpa=distance))
    self.detections.append(ER.Detection(observer_id=observer.id, target_id=target.id,
                                        sensor_range=float(own_range), distance_cpa=distance,
                                        probability=probability, draw=draw, detected=detected, time=time))


ER._EngagementRun._detect_direction = _detect_direction

rc = SB.main(['--compare', 'Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json',
              '--save', f'{OUT}/capture.json', '--quiet'] + (['--only', sys.argv[3]] if len(sys.argv) > 3 else []))
stats['models_with_dwell'] = dict(stats['models_with_dwell'])
stats['exposure_hist'] = dict(stats['exposure_hist'])
with open(f'{OUT}/stats.json', 'w') as fh:
    json.dump(stats, fh, indent=1, sort_keys=True)
print('PROBE_RC', rc)
print(json.dumps(stats, indent=1, sort_keys=True))
