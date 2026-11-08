"""Sonda di sola lettura P-1 di `Proposta_Finestre_Per_Passaggio_Portata_Propria.md` (DOPO il blocco 1 della FP).

Accende IN MEMORIA l'interruttore `Engagement_Resolver.FP_PER_PASS_DETECTION` (che esiste solo dopo il blocco 1) e
riesegue `Scenario_Baseline --compare` contro la fotografia, salvando la cattura (`<out_dir>/capture_on.json`). Non
installa nulla e non scrive nel repository (solo `<out_dir>`). Serve a sapere QUALI esecuzioni cambiano con la regola
accesa.

Atteso (Proposta §4.3, riscritta il 2026-11-08 con FP-3 (a), FP-5 (d), FP-6 (a), FP-10 (c); confermato dall'utente
la sera del 2026-11-08): esecuzioni della fotografia cambiate AL PIU' le 44 `AFTER_PASS` di P-0 PIU' le eventuali
`RINT_D`. Attesa NON misurata: P-0 ha contato le `AFTER_PASS` ma non quali cambieranno, e non ha contato le `RINT_D`;
i numeri veri sono quelli di questa sonda. In dettaglio:
  * le esecuzioni della fotografia cambiate (righe `DIFF`) per FP-3 (a) sono fra le 44 righe `AFTER_PASS` della
    sonda P-0 (salve di un osservatore con portata minore partite dopo la fine dell'unico passaggio).
    `MULTI` e `RINT` di P-0 sono vuote; FP-6 e FP-10 agiscono solo con la D-5 accesa, spenta in tutta la fotografia;
  * IN PIU', possibili cambiate dovute a FP-5 (d) (R-INT: il lancio e' "visto" solo con un rilevamento nel passaggio
    che contiene il lancio), che P-0 NON ha misurato: questa sonda le conta (righe `RINT_D`, decisioni R-INT in cui
    "visto" cambia rispetto alla regola precedente). Una cambiata che non e' ne' `AFTER_PASS` ne' `RINT_D` va
    diagnosticata.
S33-PASSES (se presente) fissa da se' gli interruttori FP e D-5 in ogni variante: l'accensione globale qui non la cambia.
Conta inoltre i passaggi di durata ZERO (rotte tangenti al volume proprio: `range_intervals` tiene gli intervalli con
s1 == s2) e quelli ridotti a durata zero dal ritaglio alla finestra (righe `ZERO`, totali in `ZERO_PASSES`).

NON cambia il comportamento del motore oltre all'interruttore: avvolge `_EngagementRun._own_passes` e
`_EngagementRun._in_time` chiamando l'originale e misurando dopo, senza consumare l'RNG; aggiunge al riassunto di ogni
esecuzione la voce `probe_fp_on` (azzerata a ogni `run_session`) esclusa dal confronto con `--ignore probe_fp_on`.

uso (dalla root del repo, PYTHONPATH=.):
    <python> probe_switch_on.py <out_dir> [<regex per --only>]
"""
import json
import sys
from collections import Counter

from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic import Session_Simulator as SS
from Code.Dynamic_War_Manager.Source.Logic.Contact_Scheduler import TIME_EPS
from Code.Dynamic_War_Manager.Source.Test import Scenario_Baseline as SB

OUT = sys.argv[1]
ONLY = sys.argv[2] if len(sys.argv) > 2 else None
BASELINE = 'Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json'
KEY = 'probe_fp_on'

for name in ('FP_PER_PASS_DETECTION',):
    if not hasattr(ER, name):
        raise SystemExit(f'{name} assente: la sonda P-1 si esegue solo dopo il blocco 1 della FP')

for name in ('_own_passes', '_in_time', '_detection_time_of'):
    if not hasattr(ER._EngagementRun, name):
        raise SystemExit(f'_EngagementRun.{name} assente: il blocco 1 della FP non corrisponde al piano')

COUNTERS = (
    'passes',               # passaggi restituiti da _own_passes, dopo l'unione FP-10 (nella fotografia la D-5 e' spenta:
                            # nessuna unione; puo' agire solo nelle nuove con la D-5 accesa, S32 e S33 `on`/`cas_on`)
    'passes_zero',          # ... di durata zero (end - start <= TIME_EPS: rotta tangente al volume proprio)
    'passes_zero_clipped',  # ... non nulli, ma ridotti a durata zero dal ritaglio alla finestra (hi - lo <= TIME_EPS)
    'rint_checks',          # decisioni R-INT (`_in_time`) valutate per la prima volta (coppia intercettore, salva)
    'rint_seen_changed',    # ... in cui "lancio visto" con FP-5 (d) differisce dalla regola precedente (ultimo in lista)
)


def _new_bucket():
    return {name: 0 for name in COUNTERS}


_state = {'bucket': _new_bucket()}

_original_own_passes = ER._EngagementRun._own_passes


def _own_passes(self, *args, **kwargs):
    passes = _original_own_passes(self, *args, **kwargs)

    if passes is not None:
        bucket = _state['bucket']
        bucket['passes'] += len(passes)

        for lo, hi, start, end in passes:
            if end - start <= TIME_EPS:
                bucket['passes_zero'] += 1
            elif hi - lo <= TIME_EPS:
                bucket['passes_zero_clipped'] += 1

    return passes


_original_in_time = ER._EngagementRun._in_time


def _in_time(self, shadow, salvo):
    fresh = (shadow.id, salvo.salvo_id) not in self.in_time_cache
    result = _original_in_time(self, shadow, salvo)

    if fresh:
        bucket = _state['bucket']
        bucket['rint_checks'] += 1
        # Regola precedente: l'ULTIMO rilevamento della coppia in ordine di lista (dizionario sovrascritto).
        last = None

        for detection in self.detections:
            if detection.detected and detection.time is not None \
                    and detection.observer_id == shadow.id and detection.target_id == salvo.shooter_id:
                last = detection.time

        new = self._detection_time_of(shadow.id, salvo.shooter_id, salvo.t_launch)
        seen_old = last is not None and last <= salvo.t_launch + TIME_EPS
        seen_new = new is not None and new <= salvo.t_launch + TIME_EPS

        if seen_old != seen_new:
            bucket['rint_seen_changed'] += 1

    return result


_original_run_session = SS.run_session


def _run_session(*args, **kwargs):
    _state['bucket'] = _new_bucket()
    return _original_run_session(*args, **kwargs)


_original_summarize = SB.summarize_run


def _summarize_run(order, forces_a, forces_b, kwargs, outcome):
    summary = _original_summarize(order, forces_a, forces_b, kwargs, outcome)
    summary[KEY] = _state['bucket']
    _state['bucket'] = _new_bucket()
    return summary


ER.FP_PER_PASS_DETECTION = True
ER._EngagementRun._own_passes = _own_passes
ER._EngagementRun._in_time = _in_time
SS.run_session = _run_session
SB.summarize_run = _summarize_run

rc = SB.main(['--compare', BASELINE, '--save', f'{OUT}/capture_on.json', '--quiet', '--ignore', KEY]
             + (['--only', ONLY] if ONLY else []))
print('PROBE_RC', rc)

with open(f'{OUT}/capture_on.json', encoding='utf-8') as handle:
    runs = json.load(handle)['runs']

with open(BASELINE, encoding='utf-8') as handle:
    photo = set(json.load(handle).get('runs', {}))

totals = Counter()
rows = {'ZERO': [], 'RINT_D': []}

for key in sorted(runs):
    bucket = runs[key].get(KEY)

    if bucket is None:
        continue

    totals.update(bucket)
    tag = '' if key in photo else ' [NUOVA]'

    if bucket['passes_zero'] or bucket['passes_zero_clipped']:
        rows['ZERO'].append(f"ZERO {key}{tag}: zero={bucket['passes_zero']} "
                            f"zero_clipped={bucket['passes_zero_clipped']} passes={bucket['passes']}")

    if bucket['rint_seen_changed']:
        rows['RINT_D'].append(f"RINT_D {key}{tag}: {bucket['rint_seen_changed']} su {bucket['rint_checks']}")

print(f'RUNS {len(runs)} (in fotografia {sum(k in photo for k in runs)}, nuove {sum(k not in photo for k in runs)})')
print(f"RUNS_WITH_ZERO_PASSES {len(rows['ZERO'])} (in fotografia {sum('[NUOVA]' not in r for r in rows['ZERO'])})")
print(f"RUNS_WITH_RINT_D {len(rows['RINT_D'])} (in fotografia {sum('[NUOVA]' not in r for r in rows['RINT_D'])})")
print('ZERO_PASSES', json.dumps(dict(totals), sort_keys=True))

for name in ('ZERO', 'RINT_D'):
    for line in rows[name]:
        print(line)

with open(f'{OUT}/stats_on.json', 'w', encoding='utf-8') as handle:
    json.dump({'totals': dict(totals), 'rows': rows}, handle, indent=1, sort_keys=False)
