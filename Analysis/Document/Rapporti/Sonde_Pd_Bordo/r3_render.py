import json, sys
from Code.Dynamic_War_Manager.Source.Test import Scenario_Baseline as SB
base = SB.load('Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json')['runs']
cur = SB.load(sys.argv[1])['runs']
KEYS = [k for k in open(sys.argv[2]).read().split('\n') if k]
out = []
for k in KEYS:
    a, b = base[k], cur[k]
    da, db = SB.run_digest(a), SB.run_digest(b)
    out.append(f'### `{k}`\n')
    out.append(f"Esiti di forza: {a['force_outcomes']} -> {b['force_outcomes']}"
               + ('  **(cambiato)**' if a['force_outcomes'] != b['force_outcomes'] else '  (invariato)'))
    out.append(f"Conteggi: " + ', '.join(f"{n} {a['counts'].get(n,0)}->{b['counts'].get(n,0)}"
               for n in ('salvos','rounds','damage_events','destroyed_events','engagements','interceptions') if a['counts'].get(n,0)!=b['counts'].get(n,0) or n in('salvos','destroyed_events')))
    out.append('\n| Grandezza | Prima | Dopo |\n|---|---|---|')
    for n in db:
        if da.get(n,'-') != db[n]:
            out.append(f'| {n} | {da.get(n,"-")} | {db[n]} |')
    ca = {tuple(map(str, e[:4])): e for e in a['damage_events']}
    cb = {tuple(map(str, e[:4])): e for e in b['damage_events']}
    first = [e for e in a['damage_events']][:0]
    out.append(f"\nEventi di danno: {len(a['damage_events'])} -> {len(b['damage_events'])}; primi 6 dopo:")
    for e in b['damage_events'][:6]:
        out.append(f'  - {e}')
    out.append('')
open(sys.argv[3], 'w').write('\n'.join(out))
