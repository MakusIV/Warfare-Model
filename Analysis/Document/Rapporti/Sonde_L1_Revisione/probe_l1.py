"""Sonda L1 rivista (sola lettura, Proposta_Revisione_L1_Lanciatore_Bersaglio.md, blocco 4).

Imposta IN MEMORIA Engagement_Resolver.L1_IMMEDIATE_TARGET_RULE, esegue la cattura completa unita' per unita' e registra
le coppie (intercettore, salva) in cui la regola del 2026-09-28 o quella rivista escludono l'intercettazione.
Nessun file del repository modificato.

Uso (dalla root del repo):  PYTHONPATH=. <python> probe_l1.py on|off <out.json>
Poi:  <python> -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline --compare <fotografia> --against <out.json> --summary
"""
import collections
import json
import re
import sys
import time

from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Test import Scenario_Baseline as SB

MODE, OUT = sys.argv[1], sys.argv[2]

if MODE not in ('on', 'off'):
    raise SystemExit('modo: on | off')

ER.L1_IMMEDIATE_TARGET_RULE = MODE == 'on'
CUR = {'label': None}
ROWS = []
COUNTS = collections.Counter()
ORIGINAL = ER._EngagementRun._may_intercept


def spy(self, shadow, salvo):
    first = (shadow.id, salvo.salvo_id) not in self.may_intercept_cache
    verdict = ORIGINAL(self, shadow, salvo)

    if first:
        old = self._may_intercept_volume(shadow, salvo)
        new = self._may_intercept_revised(shadow, salvo)
        COUNTS[(CUR['label'], 'pairs')] += 1

        if not (old and new):
            launch = self._position_at(self.shadows[salvo.shooter_id], salvo.t_launch)
            here = self._position_at(shadow, salvo.t_launch)
            ROWS.append({'unit': CUR['label'], 'interceptor': shadow.id,
                         'interceptor_model': getattr(shadow.asset, '_model', None), 'shooter': salvo.shooter_id,
                         'weapon': salvo.spec.weapon, 'rounds': salvo.rounds, 't_launch': round(salvo.t_launch, 3),
                         'tof': round(salvo.t_impact - salvo.t_launch, 3),
                         'horizontal_m': None if launch is None or here is None else
                         round(((launch[0] - here[0]) ** 2 + (launch[1] - here[1]) ** 2) ** 0.5, 1),
                         'height_m': None if launch is None or here is None else round(launch[2] - here[2], 1),
                         'zones': self._interceptor_envelopes(shadow), 'vi': self._interception_zone(shadow),
                         'immediate_target': self._immediate_target(shadow, salvo),
                         'old_allows': old, 'new_allows': new, 'r_int_ok': self._in_time(shadow, salvo)})

    return verdict


ER._EngagementRun._may_intercept = spy
labels = []

for entry in SB.UNITS:
    if entry[0] not in labels:
        labels.append(entry[0])

runs, errors = {}, {}
started = time.perf_counter()

for label in labels:
    CUR['label'] = label
    snapshot = SB.capture(only='^' + re.escape(label) + '$', verbose=False)
    runs.update(snapshot['runs'])
    errors.update(snapshot['errors'])
    print(f'[{label}] {len(snapshot["runs"])} runs, {time.perf_counter() - started:.0f} s', file=sys.stderr, flush=True)

SB.dump({'meta': {'format': SB.FORMAT_VERSION, 'round_digits': SB.ROUND_DIGITS, 'filter': f'L1 {MODE}'},
         'errors': errors, 'runs': runs}, OUT)

with open(OUT + '.rows.json', 'w') as handle:
    json.dump({'rows': ROWS, 'counts': {f'{k[0]}|{k[1]}': v for k, v in COUNTS.items()}}, handle, default=str)

excluded_old = sum(1 for r in ROWS if not r['old_allows'])
excluded_new = sum(1 for r in ROWS if not r['new_allows'])
print(f'FINE {MODE}: {len(runs)} esecuzioni, {len(errors)} errori, {sum(COUNTS.values())} coppie valutate, '
      f'escluse: regola 2026-09-28 {excluded_old}, regola rivista {excluded_new}', flush=True)
