"""Sonda S-4 (sola lettura, Proposta_Dwell_Estensione_DW9.md): D-5 accesa e dwell scritti IN MEMORIA nei registri
(valori raccomandati o estremi delle bande di incertezza); confronto con la fotografia. Nessun file del repository
modificato.

uso: <python> probe_dw9.py <rec|min|max> <famiglie> <out_dir> [regex --only]
  famiglie = 'all' oppure elenco separato da virgole fra: sam_aaa, tvd_vista, ewr, navi, awacs
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
VALUES = {
    'sam_aaa': {(V, 'ZSU-23-4-Shilka', 'radar'): (7.3, 3.0, 18.0), (V, 'Flakpanzer-Gepard', 'radar'): (1.0, 1.0, 1.0),
                (V, '2K22-Tunguska', 'radar'): (1.82, 1.0, 4.0), (V, '9A33-Osa', 'radar'): (1.82, 1.82, 1.82),
                (V, 'MIM-115-Roland', 'radar'): (1.0, 1.0, 1.0), (V, '9K331-Tor', 'radar'): (3.0, 1.0, 3.0),
                (V, '2K12-Kub', 'radar'): (3.5, 3.0, 4.0), (V, '9K37-Buk', 'radar'): (9.0, 4.3, 20.0),
                (V, 'S-300PS', 'radar'): (12.0, 5.0, 12.0)},
    'tvd_vista': {(V, m, s): VISTA for m, s in (('Strela-1-9P31', 'TVD'), ('MIM-72G-Chaparral', 'TVD'),
                                               ('9K35-Strela-10', 'TVD'), ('M6-Linebacker', 'TVD'),
                                               ('ZSU-57-2', 'visual'), ('M163-VADS', 'visual'))},
    'ewr': {(V, 'FuMG-80-Freya', 'radar'): (60.0, 30.0, 60.0), (V, 'Wassermann', 'radar'): (60.0, 30.0, 60.0),
            (V, 'AN-FPS-117', 'radar'): (10.0, 10.0, 10.0),
            # i 10 EWR del contratto precedente, riallineati (DW9-10, §2.3bis)
            (V, 'SCR-270', 'radar'): (60.0, 60.0, 60.0), (V, 'P-12-Yenisei', 'radar'): (6.0, 6.0, 30.0),
            (V, 'P-18-Terek', 'radar'): (6.0, 6.0, 6.0), (V, 'P-37-Mech', 'radar'): (14.1, 10.0, 20.0),
            (V, '1L13-Nebo-SV', 'radar'): (14.1, 10.0, 20.0), (V, '55Zh6-Nebo', 'radar'): (10.0, 10.0, 10.0),
            (V, 'AN-TPS-43', 'radar'): (10.0, 10.0, 10.0), (V, 'AMES-Type-7', 'radar'): (30.0, 7.5, 120.0),
            (V, 'AMES-Type-80', 'radar'): (15.0, 10.0, 15.0), (V, 'P-14-Lena', 'radar'): (17.3, 10.0, 30.0)},
    'navi': {(S, m, 'radar'): v for m, v in (
        ('CVN-70 Carl Vinson', SPS49), ('CVN-71 Theodore Roosevelt', SPS49), ('CVN-72 Abraham Lincoln', SPS49),
        ('CVN-73 George Washington', SPS49), ('CVN-74 John C. Stennis', SPS49), ('CVN-75 Harry S. Truman', SPS49),
        ('CV-59 USS Forrestal', SPS49), ('CV 1143.5 Admiral Kuznetsov', FREGAT), ('USS Arleigh Burke IIa', SPY1),
        ('Type 052B Guangzhou-class', FREGAT), ('Type 052C', SPY1), ('CG-65', SPY1),
        ('CGN 1144.2 Piotr Velikiy', (7.1, 5.0, 20.0)), ('CG 1164 Moskva', (10.0, 5.0, 20.0)), ('FFG-46', SPS49),
        ('FF 1135M Rezky', HEAD_NET), ('FFG 11540 Neustrashimy', FREGAT), ('Type 054A', (2.0, 2.0, 10.0)),
        ('FFL 1124.4 Grisha', HEAD_NET), ('FSG 1241.1MP Molniya', HEAD_NET), ('LHA-1 Tarawa', SPS49),
        ('Type 071', (2.0, 2.0, 2.0)))},   # Type 093: nessun valore
    'awacs': {(A, m, 'radar'): (10.0, 10.0, 10.0) for m in ('E-3A Sentry', 'E-2D Advanced Hawkeye', 'A-50')},
}

PASS = {'rec': 0, 'min': 1, 'max': 2}[sys.argv[1]]
chosen = list(VALUES) if sys.argv[2] == 'all' else sys.argv[2].split(',')
OUT = sys.argv[3]

for family in chosen:
    for (registry, model, sensor), triple in VALUES[family].items():
        getattr(registry._registry[model], sensor)['dwell_time_s'] = triple[PASS]   # solo in memoria

ER.D5_DWELL_TIME = True   # S32 'off'/'ewr_off' lo rimettono a False con patch.object attorno alla loro esecuzione

reads = Counter()
reduced = Counter()
original_reader = ER.registry_dwell_time
original_factor = ER.dwell_factor


def reader(observer, target, mode):
    value = original_reader(observer, target, mode)
    reads[(getattr(observer, '_model', None), value)] += 1
    return value


def factor(exposure_s, dwell_time_s):
    g = original_factor(exposure_s, dwell_time_s)
    if g < 1.0:
        reduced[(dwell_time_s, round(g, 3))] += 1
    return g


ER.registry_dwell_time = reader
ER.dwell_factor = factor

argv = ['--compare', 'Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json',
        '--save', f'{OUT}/capture.json', '--quiet']
if len(sys.argv) > 4:
    argv += ['--only', sys.argv[4]]
rc = SB.main(argv)
stats = {'pass': sys.argv[1], 'families': chosen,
         'reads': {f'{m} | {v}': n for (m, v), n in sorted(reads.items(), key=str)},
         'g_below_1': {f'dwell {d} g {g}': n for (d, g), n in sorted(reduced.items(), key=str)}}
with open(f'{OUT}/stats.json', 'w') as fh:
    json.dump(stats, fh, indent=1)
print('PROBE_RC', rc)
print(json.dumps(stats, indent=1))
