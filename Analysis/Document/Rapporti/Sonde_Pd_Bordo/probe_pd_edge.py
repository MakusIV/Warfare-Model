"""Sonda PB (sola lettura, Proposta_Pd_Bordo_Portata.md, blocco 2): interruttore PD_EDGE_RECALIBRATION impostato IN
MEMORIA, cattura completa, confronto con una cattura di riferimento. Nessun file del repository modificato.

uso (dalla root del repo): PYTHONPATH=. <python> probe_pd_edge.py <on|off> <out_dir> [cattura_di_riferimento] [regex]
  riferimento di default: .ai-run/confronto_capture.json (cattura da 1219, interruttore spento)
  uscita: <out_dir>/capture.json, <out_dir>/report.json (changed_list = esito atteso del blocco 3), stdout = riepilogo
  le righe 'WARNING test failed' su stderr sono i test delle unita' con metodi espliciti che falliscono
"""
import json
import logging
import os
import sys
from collections import Counter

logging.disable(logging.CRITICAL)

from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Test import Scenario_Baseline as SB

SWITCH = {'on': True, 'off': False}[sys.argv[1]]
OUT = sys.argv[2]
REF = sys.argv[3] if len(sys.argv) > 3 else '.ai-run/confronto_capture.json'
ONLY = sys.argv[4] if len(sys.argv) > 4 else None
os.makedirs(OUT, exist_ok=True)

ER.PD_EDGE_RECALIBRATION = SWITCH
NEW_EDGE = ER.pd_at_acquisition_range()
OLD_EDGE = ER.PD_AT_ACQUISITION_RANGE

# Spia sulle Detection: esito con la soglia in vigore e quello che la STESSA estrazione avrebbe dato con la soglia di
# prima (effetto di primo ordine: a cascata cambiano anche gli ingaggi e le estrazioni successive).
_inner = ER.resolve_engagement
STATS = Counter()


def spy(*args, **kwargs):
    result = _inner(*args, **kwargs)
    if result is not None:
        for d in result.detections:
            STATS['draws'] += 1
            if d.sensor_range <= 0 or d.distance_cpa > d.sensor_range:
                STATS['out_of_range'] += 1
                continue
            r4 = (d.distance_cpa / d.sensor_range) ** ER.PD_RANGE_EXPONENT
            den = 1.0 - (1.0 - NEW_EDGE) * r4
            factor = d.probability / den if den > 0 else 0.0
            old_detected = d.draw < factor * (1.0 - (1.0 - OLD_EDGE) * r4)
            STATS['in_range'] += 1
            STATS['detected_now'] += int(d.detected)
            STATS['detected_with_old_edge_same_draw'] += int(old_detected)
            STATS['lost'] += int(old_detected and not d.detected)
            STATS['gained'] += int(d.detected and not old_detected)
            band = min(int(r4 ** 0.25 * 10), 9)
            STATS[f'band_{band}_in_range'] += 1
            STATS[f'band_{band}_lost'] += int(old_detected and not d.detected)
    return result


ER.resolve_engagement = spy
current = SB.capture(ONLY, verbose=True)
SB.dump(current, os.path.join(OUT, 'capture.json'))
reference = SB.load(REF)['runs']

changed, unchanged, new = [], [], []
keys_changed, family_changed, family_total, outcome_changed = Counter(), Counter(), Counter(), []
delta = {}
for key, run in sorted(current['runs'].items()):
    family = key.split('/')[0]
    family_total[family] += 1
    if key not in reference:
        new.append(key)
        continue
    ref = reference[key]
    if ref == run:
        unchanged.append(key)
        continue
    changed.append(key)
    family_changed[family] += 1
    keys_changed.update(top for top in set(ref) | set(run) if ref.get(top) != run.get(top))
    if ref['force_outcomes'] != run['force_outcomes']:
        outcome_changed.append(key)
    row = delta.setdefault(family, Counter())
    for count in ('salvos', 'destroyed_events', 'interceptions', 'engagements'):
        row[count + '_before'] += ref['counts'].get(count, 0)
        row[count + '_after'] += run['counts'].get(count, 0)

missing = [] if ONLY else sorted(k for k in reference if k not in current['runs'])
s36_rows = []
for key in sorted(k for k in changed if k.split('/')[0] in SB.DETECTION_UNITS):
    for before, after in zip(reference[key].get('detections', []), current['runs'][key].get('detections', [])):
        # campi DETECTION_FIELDS: 0 osservatore, 1 bersaglio, 2 portata, 3 CPA, 4 Pd, 5 estrazione, 6 rilevato, 7 istante
        s36_rows.append([key, before[0], before[1], before[2], before[3], before[4], after[4], before[5],
                         before[6], after[6], before[7], after[7]])

report = {'switch': SWITCH, 'edge_now': NEW_EDGE, 'edge_before': OLD_EDGE, 'reference': REF,
          'runs': len(current['runs']), 'errors': current['errors'], 'changed': len(changed),
          'unchanged': len(unchanged), 'new': new, 'missing': missing, 'keys_changed': dict(keys_changed),
          'family': {f: [family_changed.get(f, 0), family_total[f]] for f in sorted(family_total)},
          'family_counts': {f: dict(c) for f, c in sorted(delta.items())}, 'outcome_changed': outcome_changed,
          'detections': dict(STATS), 's36_rows': s36_rows, 'changed_list': changed, 'unchanged_list': unchanged}
with open(os.path.join(OUT, 'report.json'), 'w', encoding='utf-8') as handle:
    json.dump(report, handle, indent=1, sort_keys=True)
print(json.dumps({k: v for k, v in report.items() if k not in ('changed_list', 'unchanged_list', 's36_rows')},
                 indent=1, sort_keys=True))
