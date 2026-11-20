import logging, sys
logging.disable(logging.CRITICAL)
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Test import Scenario_Baseline as SB
ER.PD_EDGE_RECALIBRATION = True
cur = SB.capture(r'^(ORC-base|S1|S6|S7|S8|S13|S14|S11|S2|S3|S4|S20|S22-E1|S9R|S12|S15|S16|S23-CAP|S5|S27-DOUBLE)$', verbose=True)
SB.dump(cur, sys.argv[1])
print('done', len(cur['runs']), cur['errors'])
