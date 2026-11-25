"""Suite completa con L1_IMMEDIATE_TARGET_RULE acceso IN MEMORIA (sola lettura); elenca i test falliti.

Uso (dalla root del repo):  PYTHONPATH=. <python> suite_l1_on.py
"""
import unittest

from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER

ER.L1_IMMEDIATE_TARGET_RULE = True
suite = unittest.defaultTestLoader.discover('Code/Dynamic_War_Manager/Source/Test', pattern='Test_*.py')
result = unittest.TextTestRunner(verbosity=1).run(suite)
print('FALLITI:')

for test, _ in result.failures + result.errors:
    print(' ', test.id())
