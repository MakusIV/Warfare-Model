"""Sonda di sola lettura P-1 di `Proposta_Finestre_Per_Passaggio_Portata_Propria.md` (DOPO il blocco 1).

Accende IN MEMORIA l'interruttore `Engagement_Resolver.FP_PER_PASS_DETECTION` (che esiste solo dopo il blocco 1) e
riesegue `Scenario_Baseline --compare` contro la fotografia, salvando la cattura. Non installa nulla e non scrive
nel repository (solo `<out_dir>`). Serve a sapere QUALI esecuzioni cambiano con la regola accesa, da confrontare
con le righe MULTI della sonda P-0 (le cambiate devono essere un sottoinsieme delle esecuzioni MULTI, salvo quelle
spiegate dalla regola R-INT di FP-5: righe RINT di P-0).

uso (dalla root del repo, PYTHONPATH=.):
    <python> probe_switch_on.py <out_dir> [<regex per --only>]
"""
import sys

from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Test import Scenario_Baseline as SB

OUT = sys.argv[1]
ONLY = sys.argv[2] if len(sys.argv) > 2 else None
BASELINE = 'Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json'

if not hasattr(ER, 'FP_PER_PASS_DETECTION'):
    raise SystemExit('FP_PER_PASS_DETECTION assente: la sonda P-1 si esegue solo dopo il blocco 1')

ER.FP_PER_PASS_DETECTION = True
rc = SB.main(['--compare', BASELINE, '--save', f'{OUT}/capture_on.json', '--quiet']
             + (['--only', ONLY] if ONLY else []))
print('PROBE_RC', rc)
