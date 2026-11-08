"""Sonda di sola lettura B-1 di `Proposta_Bersagli_Intercettabili_Difesa_Aerea.md` (DOPO il blocco 2).

Accende IN MEMORIA l'interruttore `Engagement_Resolver.BI_AD_TARGET_RULE` (che esiste solo dopo il blocco 2) e
riesegue `Scenario_Baseline --compare` contro la fotografia, salvando la cattura. Non installa nulla e non scrive
nel repository (solo `<out_dir>`). Serve a sapere QUALI esecuzioni cambiano con la regola accesa, da confrontare
con le sei esecuzioni `CHANGED[unmodelled_as_before]` della sonda B-0 (`S19AD/S19-<0..5>/tor_rear`).

Atteso (§5.3.6 della Proposta): cambiano ESATTAMENTE quelle sei esecuzioni e nessun'altra; in ciascuna zero
`InterceptionEvent` del Tor e piu' colpi al danno; le intercettazioni antinave di S6/S16 restano identiche. Le 20
esecuzioni `S32-DWELL` sono NUOVE rispetto alla fotografia versionata (non sono differenze di questa sonda).

Dopo il confronto la sonda legge la cattura e stampa, per ogni esecuzione cambiata, gli eventi di intercettazione e di
danno prima/dopo (righe `B1_CHANGED`), e il controllo sull'insieme atteso (`B1_EXPECTED_SET`, `B1_TOR_ZERO`,
`B1_MORE_DAMAGE`, `B1_ANTISHIP_IDENTICAL`).

uso (dalla root del repo, PYTHONPATH=.):
    <python> probe_switch_on.py <out_dir> [<regex per --only>]
"""
import json
import re
import sys

from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Test import Scenario_Baseline as SB

OUT = sys.argv[1]
ONLY = sys.argv[2] if len(sys.argv) > 2 else None
BASELINE = 'Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json'
EXPECTED = {f'S19AD/S19-{index}/tor_rear' for index in range(6)}

if not hasattr(ER, 'BI_AD_TARGET_RULE'):
    raise SystemExit('BI_AD_TARGET_RULE assente: la sonda B-1 si esegue solo dopo il blocco 2')

ER.BI_AD_TARGET_RULE = True
rc = SB.main(['--compare', BASELINE, '--save', f'{OUT}/capture_on.json', '--quiet', '--summary']
             + (['--only', ONLY] if ONLY else []))
print('PROBE_RC', rc)

baseline = SB.load(BASELINE)['runs']
current = SB.load(f'{OUT}/capture_on.json')['runs']
pattern = re.compile(ONLY) if ONLY else None
changed = sorted(key for key, run in current.items() if key in baseline and run != baseline[key]
                 and (pattern is None or pattern.search(key)))
new = sorted(key for key in current if key not in baseline)
print('B1_CHANGED_KEYS', len(changed))

for key in changed:
    before, after = baseline[key], current[key]
    differing = sorted(name for name in after if after[name] != before.get(name))
    print('B1_CHANGED', key,
          'interception_events', len(before['interception_events']), '->', len(after['interception_events']),
          'damage_events', len(before['damage_events']), '->', len(after['damage_events']),
          'interceptions', json.dumps(before['interceptions'], sort_keys=True), '->',
          json.dumps(after['interceptions'], sort_keys=True), 'differing_keys', differing)

print('B1_NEW_KEYS', len(new), sorted({key.split('/')[0] for key in new}))

if pattern is None:
    print('B1_EXPECTED_SET', 'OK' if set(changed) == EXPECTED else f'DIVERSO: {sorted(set(changed) ^ EXPECTED)}')

tor = 'Red-Line/ad0'
print('B1_TOR_ZERO', all(not [e for e in current[key]['interception_events'] if e[1] == tor]
                         and not current[key]['interceptions'].get(tor) for key in changed))
print('B1_MORE_DAMAGE', all(len(current[key]['damage_events']) > len(baseline[key]['damage_events'])
                            for key in changed))
anti_ship = sorted(key for key in baseline if key.split('/')[0] in ('S6', 'S16') and key in current
                   and baseline[key]['interception_events'])
print('B1_ANTISHIP_RUNS', len(anti_ship),
      'rounds_stopped', sum(sum(e[3] for e in baseline[key]['interception_events']) for key in anti_ship))
print('B1_ANTISHIP_IDENTICAL', all(current[key]['interception_events'] == baseline[key]['interception_events']
                                   and current[key]['interceptions'] == baseline[key]['interceptions']
                                   for key in anti_ship))
