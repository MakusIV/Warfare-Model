"""Sonda di sola lettura B-0 di `Proposta_Bersagli_Intercettabili_Difesa_Aerea.md` (prima di ogni codice).

Conta, nelle esecuzioni della fotografia, i colpi INTERCETTABILI (`ShotSpec.interceptable`) arrivati su forze con
intercettori e i colpi FERMATI (intercettati), per arma/categoria del registro, classe del lanciatore, classe del
bersaglio e classe dell'intercettore (Vehicle = terrestre, Ship = navale). Poi stima quante esecuzioni cambierebbero
con la regola nuova (bersagli intercettabili solo balistici/cruise o, contro difese navali, antinave di dimensione
compatibile) in alcune varianti di classificazione (v. `_keep`).

NON cambia il comportamento del motore:
  * avvolge `_EngagementRun._on_resolve`: chiama l'originale con un profilatore (`sys.setprofile`) che legge le
    variabili locali della funzione al suo ritorno (`ordered`, `stopped`, `available`, `interceptors`), senza
    modificarle; poi ricostruisce l'attribuzione colpo -> intercettore ripercorrendo il ciclo di allocazione con le
    cache GIA' riempite dal motore (`may_intercept_cache`, `in_time_cache`), senza chiamare nulla che estragga
    numeri casuali; controlla che la ricostruzione dia gli stessi `stopped` del motore (contatore `replay_mismatch`);
  * aggiunge al riassunto di ogni esecuzione una voce `probe_intercepts` (azzerata a ogni `run_session`) e riesegue
    `Scenario_Baseline --compare` con `--ignore probe_intercepts`: il confronto deve restare quello di oggi
    (nessuna riga DIFF; oggi 20 righe NEW di S32-DWELL, che non e' nella fotografia).
Nessun file del repository viene scritto; l'uscita va in `<out_dir>` (capture.json, stats.json).

Perche' "esecuzione cambiata" = "almeno un colpo ESCLUSO dalla regola e' stato fermato": la fotografia
(`Scenario_Baseline.summarize_run`) registra eventi di intercettazione, danni, munizioni e scorte, NON
`SalvoResolution.interceptable_rounds`. Una salva che diventa non intercettabile senza aver preso capacita' non cambia
l'allocazione delle altre (il ciclo di `_on_resolve` non tocca `used` se non prende colpi) ne' nessuna estrazione.
Se invece ha preso capacita', cambiano gli eventi di intercettazione (registrati) e i colpi che arrivano al danno.

uso (dalla root del repo, PYTHONPATH=.):
    <python> probe_intercepts.py <out_dir> [<regex per --only>]
"""
import json
import sys
from collections import Counter

from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic import Fire_Control as FC
from Code.Dynamic_War_Manager.Source.Logic import Session_Simulator as SS
from Code.Dynamic_War_Manager.Source.Test import Scenario_Baseline as SB

OUT = sys.argv[1]
ONLY = sys.argv[2] if len(sys.argv) > 2 else None
BASELINE = 'Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json'
KEY = 'probe_intercepts'

_DOMAIN_OF_CLASS = {'Aircraft': 'air', 'Vehicle': 'ground', 'Ship': 'sea'}


def _new_bucket():
    return {'resolutions': 0, 'resolutions_with_interceptors': 0, 'interceptable_rounds': 0,
            'interceptable_rounds_facing_interceptors': 0, 'stopped_rounds': 0, 'replay_mismatch': 0,
            'facing': {}, 'stopped': {}, 'rint_paths': {}}


_state = {'bucket': _new_bucket()}


def _cls(asset):
    return type(asset).__name__


def _air_type(asset):
    value = getattr(asset, 'asset_type', None)
    return str(value) if value is not None else '-'


def _weapon_key(run, salvo):
    """'classe_lanciatore(tipo)|categoria|arma|classe_bersaglio'."""
    shooter = run.shadows[salvo.shooter_id].asset
    target = run.shadows[salvo.target_id].asset
    shooter_cls = _cls(shooter)
    domain = _DOMAIN_OF_CLASS.get(shooter_cls)
    weapon = salvo.spec.weapon
    category = FC.weapon_category(domain, weapon) if domain else None
    label = f'{shooter_cls}({_air_type(shooter)})' if shooter_cls == 'Aircraft' else shooter_cls
    return f'{label}|{category}|{weapon}|{_cls(target)}'


def _model(asset):
    return str(getattr(asset, '_model', None) or getattr(asset, 'model', None) or '-')


_original_on_resolve = ER._EngagementRun._on_resolve
_CODE = _original_on_resolve.__code__


def _on_resolve(self, time, force_id):
    captured = {}

    def profiler(frame, event, arg):
        if event == 'return' and frame.f_code is _CODE:
            captured.update(frame.f_locals)

    previous = sys.getprofile()
    sys.setprofile(profiler)

    try:
        result = _original_on_resolve(self, time, force_id)
    finally:
        sys.setprofile(previous)

    if 'stopped' not in captured:
        return result   # gruppo vuoto: uscita anticipata, nessuna risoluzione

    bucket = _state['bucket']
    ordered, stopped = captured['ordered'], captured['stopped']
    available, interceptors = captured['available'], captured['interceptors']
    bucket['resolutions'] += 1

    if interceptors:
        bucket['resolutions_with_interceptors'] += 1

    # Ricostruzione dell'allocazione (stesso ciclo del motore, cache gia' riempite: nessuna chiamata nuova).
    used, replay = {}, {}

    for salvo in ordered:
        if not salvo.spec.interceptable:
            continue

        key = _weapon_key(self, salvo)
        bucket['interceptable_rounds'] += salvo.rounds

        if interceptors:
            bucket['interceptable_rounds_facing_interceptors'] += salvo.rounds
            bucket['facing'][key] = bucket['facing'].get(key, 0) + salvo.rounds

        left = salvo.rounds

        for shadow, _ in interceptors:
            if left <= 0:
                break

            free = available.get(shadow.id, 0) - used.get(shadow.id, 0)

            if free <= 0:
                continue

            pair = (shadow.id, salvo.salvo_id)
            may = self.may_intercept_cache.get(pair)

            if may is None:
                bucket['replay_mismatch'] += 1
                break

            if not may:
                continue

            in_time = self.in_time_cache.get(pair)

            if in_time is None:
                bucket['replay_mismatch'] += 1
                break

            seen = self._detection_time_of(shadow.id, salvo.shooter_id)
            path = 'seen' if seen is not None and seen <= salvo.t_launch + ER.TIME_EPS else 'geometry'
            rkey = f'{key}|{path}|{"ok" if in_time else "late"}'
            bucket['rint_paths'][rkey] = bucket['rint_paths'].get(rkey, 0) + 1

            if not in_time:
                continue

            take = min(free, left)
            used[shadow.id] = used.get(shadow.id, 0) + take
            left -= take
            skey = f'{key}|{_cls(shadow.asset)}:{_model(shadow.asset)}'
            bucket['stopped'][skey] = bucket['stopped'].get(skey, 0) + take

        if left < salvo.rounds:
            replay[salvo.salvo_id] = salvo.rounds - left

    if replay != stopped:
        bucket['replay_mismatch'] += 1

    bucket['stopped_rounds'] += sum(stopped.values())
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


ER._EngagementRun._on_resolve = _on_resolve
SS.run_session = _run_session
SB.summarize_run = _summarize_run

rc = SB.main(['--compare', BASELINE, '--save', f'{OUT}/capture.json', '--quiet', '--ignore', KEY]
             + (['--only', ONLY] if ONLY else []))
print('PROBE_RC', rc)

# ── Classificazione della regola nuova (varianti della Proposta, §3) ───────────────────────────────────────────────
# Missili aria-superficie del registro trattati come CRUISE strategici (lanciati da bombardieri): STIMA di
# classificazione [S] della Proposta, da confermare con la decisione BI-2 e la ricerca dati.
CRUISE_AIR = {'Kh-55', 'Kh-101', 'Kh-555', 'Kh-65', 'KD-20'}
# Missili aria-superficie a solo task Anti_Ship (antinave dedicati): candidati A2S contro difese NAVALI.
ANTI_SHIP_AIR = {'RB-15F', 'AGM-84A', 'Kormoran', 'RB-04E', 'Sea Eagle', 'RB-15', 'Kh-22N', 'Kh-31A', 'Kh-35',
                 'Kh-41'}
# Armi di test della tabella di riferimento (Scenario_Fixtures.SHOTS) per ruolo.
TEST_A2S = {'test:anti_ship'}


def _keep(key_parts, interceptor_cls, test_policy):
    """True se, con la regola nuova, il colpo resta intercettabile da quell'intercettore."""
    shooter, category, weapon, target = key_parts
    shooter_cls = shooter.split('(')[0]

    if weapon is None or weapon == 'None' or str(weapon).startswith('test:') or category == 'None':
        if test_policy == 'unmodelled_as_before':
            return True
        # 'by_role': ruolo della tabella di test (agm, arm = A2G esclusi; anti_ship = A2S contro navali)
        return weapon in TEST_A2S and interceptor_cls == 'Ship'

    if shooter_cls == 'Ship' and category == 'MISSILES_ASM':
        return True   # antinave/cruise navali (Harpoon, Tomahawk, ...): tutti di classe cruise
    if shooter_cls == 'Aircraft' and category == 'MISSILES_ASM':
        if weapon in CRUISE_AIR:
            return True
        return weapon in ANTI_SHIP_AIR and interceptor_cls == 'Ship'
    return False      # ATGM, SAM, AAM, ASM tattici/ARM, bombe guidate, razzi


with open(f'{OUT}/capture.json', encoding='utf-8') as handle:
    runs = json.load(handle)['runs']

with open(BASELINE, encoding='utf-8') as handle:
    photo = set(json.load(handle).get('runs', {}))

totals = Counter()
facing_all, stopped_all, rint_all = Counter(), Counter(), Counter()
changed = {'unmodelled_as_before': [], 'by_role': []}
runs_with_stops = []
units_with_stops = Counter()

for key in sorted(runs):
    bucket = runs[key].get(KEY)

    if bucket is None:
        continue

    for name in ('resolutions', 'resolutions_with_interceptors', 'interceptable_rounds',
                 'interceptable_rounds_facing_interceptors', 'stopped_rounds', 'replay_mismatch'):
        totals[name] += bucket[name]

    facing_all.update(bucket['facing'])
    stopped_all.update(bucket['stopped'])
    rint_all.update(bucket['rint_paths'])
    tag = '' if key in photo else ' [NUOVA]'

    if bucket['stopped_rounds']:
        runs_with_stops.append(key)
        units_with_stops[key.split('/', 1)[0]] += 1

    for policy in changed:
        excluded = 0

        for skey, rounds in bucket['stopped'].items():
            parts = skey.split('|')
            interceptor_cls = parts[4].split(':')[0]

            if not _keep(parts[:4], interceptor_cls, policy):
                excluded += rounds

        if excluded:
            changed[policy].append((key + tag, excluded, bucket['stopped_rounds']))

print(f'RUNS {len(runs)} (in fotografia {sum(k in photo for k in runs)}, nuove {sum(k not in photo for k in runs)})')
print('TOTALS', json.dumps(dict(totals), sort_keys=True))
print(f'RUNS_WITH_STOPS {len(runs_with_stops)} (in fotografia {sum(k in photo for k in runs_with_stops)})')
print('UNITS_WITH_STOPS', json.dumps(dict(sorted(units_with_stops.items()))))

for policy, rows in changed.items():
    in_photo = sum(1 for row in rows if '[NUOVA]' not in row[0])
    by_unit = Counter(row[0].split('/', 1)[0] for row in rows)
    print(f'CHANGED[{policy}] {len(rows)} (in fotografia {in_photo}) UNITS {json.dumps(dict(sorted(by_unit.items())))}')

for skey, rounds in sorted(stopped_all.items(), key=lambda item: -item[1]):
    print(f'STOPPED {rounds} {skey}')

for fkey, rounds in sorted(facing_all.items(), key=lambda item: -item[1]):
    print(f'FACING {rounds} {fkey}')

for rkey, count in sorted(rint_all.items(), key=lambda item: -item[1]):
    print(f'RINT {count} {rkey}')

for policy, rows in changed.items():
    for name, excluded, total in rows:
        print(f'CHANGED[{policy}] {name}: excluded_stopped={excluded} stopped={total}')

with open(f'{OUT}/stats.json', 'w', encoding='utf-8') as handle:
    json.dump({'totals': dict(totals), 'units_with_stops': dict(units_with_stops),
               'stopped': dict(stopped_all), 'facing': dict(facing_all), 'rint_paths': dict(rint_all),
               'changed': {policy: rows for policy, rows in changed.items()}}, handle, indent=1)
