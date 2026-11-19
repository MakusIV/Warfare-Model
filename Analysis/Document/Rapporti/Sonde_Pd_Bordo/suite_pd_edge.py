"""Sonda PB (sola lettura): suite completa con PD_EDGE_RECALIBRATION impostato IN MEMORIA; elenca i test falliti.
uso (dalla root del repo): PYTHONPATH=. <python> suite_pd_edge.py <on|off>"""
import os
import sys
import unittest

from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER

ER.PD_EDGE_RECALIBRATION = {'on': True, 'off': False}[sys.argv[1]]
suite = unittest.defaultTestLoader.discover('Code/Dynamic_War_Manager/Source/Test', pattern='Test_*.py')

with open(os.devnull, 'w') as sink:
    result = unittest.TextTestRunner(verbosity=0, stream=sink).run(suite)

print(f'Ran {result.testsRun}, failures {len(result.failures)}, errors {len(result.errors)}, '
      f'skipped {len(result.skipped)}')
for test, trace in result.failures + result.errors:
    print('FAIL', test.id(), '|', trace.strip().splitlines()[-1][:300])
