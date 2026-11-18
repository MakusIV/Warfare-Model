"""Sonda S-5 (accensione di D5_DWELL_TIME sul codice committato, nessun valore iniettato). Derivata da S-4.

S-4 (sola lettura, Proposta_Dwell_Estensione_DW9.md): D-5 accesa e dwell scritti IN MEMORIA nei registri
(valori raccomandati o estremi delle bande di incertezza); confronto con la fotografia. Nessun file del repository
modificato.

Nessun valore iniettato: legge i dwell committati nei registri. Registra per ogni chiamata con g < 1 lo scenario,
la distanza CPA, la portata e la Pd che ci sarebbe stata senza dwell (g_detail.json).

uso: PYTHONPATH=. <python> probe_dw9_on.py <out_dir> [regex --only]
"""
import json
import logging
import sys
from collections import Counter

logging.disable(logging.CRITICAL)

from Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data import Vehicle_Data as V
from Code.Dynamic_War_Manager.Source.Asset.Ship_Data import Ship_Data as S
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import Aircraft_Data as A
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Test import Scenario_Baseline as SB

VISTA = (3.2, 1.75, 6.0)            # (raccomandato, minimo, massimo) della banda [s]
SPS49 = (5.0, 5.0, 10.0)
FREGAT = (7.1, 5.0, 10.0)
HEAD_NET = (7.1, 5.0, 10.0)
SPY1 = (5.0, 5.0, 60.0)
# famiglia -> {(registro, modello, sensore): (raccomandato, minimo, massimo)}; banda assente = tre valori uguali
ER.D5_DWELL_TIME = True   # S32 'off'/'ewr_off' lo rimettono a False con patch.object attorno alla loro esecuzione

reads = Counter()
reduced = Counter()
original_reader = ER.registry_dwell_time
original_factor = ER.dwell_factor


def reader(observer, target, mode):
    value = original_reader(observer, target, mode)
    reads[(getattr(observer, '_model', None), value)] += 1
    return value


CUR = ['?']
orig_unit = SB._run_unit


def run_unit(module_name, class_name, methods):
    CUR[0] = f'{module_name.rsplit(".", 1)[-1]}.{class_name}'
    return orig_unit(module_name, class_name, methods)


SB._run_unit = run_unit
detail = []


def factor(exposure_s, dwell_time_s):
    g = original_factor(exposure_s, dwell_time_s)
    if g < 1.0:
        reduced[(dwell_time_s, round(g, 3))] += 1
        f = sys._getframe(1).f_locals
        try:
            distance = max(float(f['window'].distance_cpa), 0.0)
            rng = f['own_range']
            pd0 = ER.detection_probability(distance, rng, f['factor']) if distance <= rng else 0.0
        except Exception as exc:
            distance = rng = pd0 = repr(exc)
        detail.append({'unit': CUR[0], 'observer': getattr(f.get('observer', None).asset, '_model', None) if f.get('observer') else None,
                       'dwell': dwell_time_s, 'g': round(g, 3), 'exposure': exposure_s, 'distance_cpa': distance,
                       'own_range': rng, 'pd_without_dwell': pd0})
    return g


ER.registry_dwell_time = reader
ER.dwell_factor = factor

OUT = sys.argv[1]
argv = ['--compare', 'Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json',
        '--save', f'{OUT}/capture.json', '--quiet']
if len(sys.argv) > 2:
    argv += ['--only', sys.argv[2]]
rc = SB.main(argv)
stats = {'pass': 'committed',
         'reads': {f'{m} | {v}': n for (m, v), n in sorted(reads.items(), key=str)},
         'g_below_1': {f'dwell {d} g {g}': n for (d, g), n in sorted(reduced.items(), key=str)}}
with open(f'{OUT}/stats.json', 'w') as fh:
    json.dump(stats, fh, indent=1)
json.dump(detail, open(f'{OUT}/g_detail.json', 'w'), indent=1)
print('PROBE_RC', rc)
print(json.dumps(stats, indent=1))
