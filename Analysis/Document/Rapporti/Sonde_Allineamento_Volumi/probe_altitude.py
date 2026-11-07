"""Sonde di sola lettura V-0, V-1 e V-2 di `Proposta_Allineamento_Volumi_DES_Pianificatore.md`.

Domanda: nel DES un tiro contraereo parte con il bersaglio FUORI dalla fascia di quota dell'arma
(sopra `max_altitude` o sotto `min_altitude`, quota RELATIVA al tiratore, come in
`Fire_Control.in_altitude_envelope` e `Mobile.air_defense_volume`)? E quante coppie
tiratore -> bersaglio aereo il filtro di quota STATICO della fire control dei registri (quota di
partenza `asset.position.z`) esclude o ammette in modo diverso da un filtro valutato nel tempo sui tratti?

NON cambia il comportamento del motore:
  * avvolge `_EngagementRun.run`: chiama l'originale, POI misura salve e candidati dai tratti
    (`position_on_legs`), senza consumare l'RNG e senza chiamare la fire control iniettata;
  * aggiunge al riassunto di ogni esecuzione una voce `probe_altitude` e riesegue
    `Scenario_Baseline --compare` con `--ignore probe_altitude`: il confronto deve restare quello di oggi.
V-1 (stesso script): avvolge anche `_first_with_stock` (ricorda l'ultima ShotSpec scelta per tiratore) e
`_range_entry` (chiama l'originale, poi ricalcola l'istante con sfera ∩ fascia dell'arma del registro e conta le
differenze `entry_differs`): e' la previsione dell'interruttore VA_ENGAGEMENT_ALTITUDE_BAND acceso (piano §4.1),
comprese le chiamate di `_in_range_at` (precedenze L2, designati, reazione).
V-2 (stesso script, scelte dell'utente del 2026-11-07 VA-2 (d) e VA-3 (b)): avvolge anche `_call_fire_control`
(chiama l'originale, poi ricalcola con `Fire_Control.rank_weapons` le armi adatte alla quota di partenza e alla quota
all'istante dai tratti e confronta: `fc_air_differs`, rinvii `fc_air_defer`, bombardieri `fc_bomb_alt_differs`;
chiavi di memoizzazione distinte `fc_keys_*`); in `_range_entry` conta anche le armi d'aereo con il tetto assoluto
`max_height` (`entry_differs_air`). Le righe `SWITCH` elencano le esecuzioni che l'interruttore acceso potrebbe cambiare.
Nessun file del repository viene scritto; l'uscita va in `<out_dir>` (capture.json, stats.json).

uso (dalla root del repo, PYTHONPATH=.):
    <python> probe_altitude.py <out_dir> [<regex per --only>]
"""
import json
import math
import sys
from collections import Counter

from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic import Fire_Control as FC
from Code.Dynamic_War_Manager.Source.Logic import Session_Simulator as SS
from Code.Dynamic_War_Manager.Source.Logic.Contact_Scheduler import TIME_EPS, legs_span, position_on_legs
from Code.Dynamic_War_Manager.Source.Test import Scenario_Baseline as SB

OUT = sys.argv[1]
ONLY = sys.argv[2] if len(sys.argv) > 2 else None
BASELINE = 'Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json'
KEY = 'probe_altitude'
SAMPLES = 40

COUNTERS = (
    'engagements',
    'salvos',                        # salve totali
    'salvos_air',                    # salve contro un aereo in volo all'istante di lancio
    'salvos_air_no_legs',            # ... senza tratti di uno dei due (quota non ricostruibile)
    'salvos_air_registry_weapon',    # ... con un'arma del registro (spec.weapon = modello del registro)
    'sw_with_band',                  # ... arma con min/max_altitude (o max_height per le armi d'aereo)
    'sw_above_max',                  # ... bersaglio SOPRA la quota massima dell'arma al lancio
    'sw_below_min',                  # ... bersaglio SOTTO la quota minima dell'arma al lancio
    'sw_static_differs',             # ... quota relativa al lancio diversa (> 1 m) da quella di partenza
    'salvos_air_test_weapon',        # salve contro aerei con ShotSpec di test ('test:...')
    'cyl_available',                 # salve contro aerei di un tiratore con cilindro del pianificatore
    'cyl_above',                     # ... bersaglio sopra il tetto del cilindro (pianificatore: "sicuro")
    'cyl_below',                     # ... bersaglio sotto la base del cilindro
    'cyl_outside_radius',            # ... distanza orizzontale > raggio del cilindro
    'cand_air_registry',             # candidati (osservatore con fire control dei registri) su un aereo
    'cand_static_excluded',          # ... il filtro statico esclude ogni arma (quota di partenza)
    'cand_static_excluded_dyn_ok',   # ... ma in qualche istante della finestra sfera + fascia sarebbero soddisfatte
    'cand_static_ok_dyn_never',      # ... il filtro statico ammette, la sfera e' raggiunta, ma mai dentro la fascia
    'entry_checks_band',             # chiamate a _range_entry su bersaglio aereo con arma del registro dotata di fascia
    'entry_differs',                 # ... in cui l'istante con sfera ∩ fascia differisce da quello di oggi (sola sfera)
    'entry_none_with_band',          # ... di cui: oggi un istante, con la fascia nessuno (candidato esaurito)
    'entry_later_with_band',         # ... di cui: con la fascia un istante piu' tardo (tiro rimandato)
    'entry_checks_air_ceiling',      # V-2: chiamate a _range_entry con arma d'aereo dotata di max_height (VA-3 (b))
    'entry_differs_air',             # ... istante diverso con sfera ∩ (z bersaglio <= max_height)
    'fc_calls_alt',                  # V-2: chiamate alla fire control dei registri in cui conta la quota (aereo o bombardiere)
    'fc_calls_no_legs',              # ... senza tratti (VA-2 (d) non applicabile: quota di partenza come oggi)
    'fc_keys_static',                # chiavi di memoizzazione distinte con la quota di partenza (per esecuzione)
    'fc_keys_dynamic',               # ... con la quota all'istante (costo della memoizzazione con VA-2 (d))
    'fc_air_differs',                # contro un aereo: armi adatte (in ordine) diverse fra quota di partenza e quota all'istante
    'fc_air_defer',                  # ... nessuna arma adatta all'istante ma almeno una senza filtro di quota (rinvio VA-2.1)
    'fc_air_defer_static_ok',        # ... di cui oggi (quota di partenza) adatta: il rinvio sostituirebbe un tiro di oggi
    'fc_air_defer_entry',            # ... di cui con un ingresso ESATTO in sfera ∩ fascia (o tetto) dopo l'istante, fino alla fine dei tratti
    'fc_bomb_alt_differs',           # bombardiere: quota relativa di sgancio diversa (> 1e-6 m) fra partenza e istante
)


def _new_bucket():
    bucket = {name: 0 for name in COUNTERS}
    bucket['models_above'] = {}
    bucket['models_below'] = {}
    bucket['fc'] = {}
    bucket['models_cyl_above'] = {}
    bucket['models_cyl_outside'] = {}
    bucket['_keys_s'] = set()
    bucket['_keys_d'] = set()
    return bucket


_state = {'bucket': _new_bucket()}
_weapon_cache = {}


def _model(asset):
    return str(getattr(asset, '_model', None) or type(asset).__name__)


def _is_air(asset):
    return type(asset).__name__ == 'Aircraft'


def _weapons_of(asset):
    key = FC._shooter_key(asset)

    if key is None:
        return ()

    if key not in _weapon_cache:
        _weapon_cache[key] = FC._candidate_weapons(key)

    return _weapon_cache[key]


def _registry_weapon(asset, name):
    for weapon in _weapons_of(asset):
        if weapon.model == name:
            return weapon

    return None


def _band_status(weapon, zs, zt):
    """'above' | 'below' | 'in' | None (nessuna fascia dichiarata)."""
    if weapon.domain == 'air':
        if weapon.max_height_m is None:
            return None
        return 'above' if zt > weapon.max_height_m else 'in'

    if weapon.min_alt is None or weapon.max_alt is None:
        return None

    rel = zt - zs

    if rel > weapon.max_alt:
        return 'above'

    if rel < weapon.min_alt:
        return 'below'

    return 'in'


def _cylinder(asset):
    try:
        return asset.air_defense_volume()
    except Exception:   # noqa: BLE001
        return None


def _sample_times(lo, hi):
    if hi <= lo:
        return [lo]
    return [lo + (hi - lo) * k / (SAMPLES - 1) for k in range(SAMPLES)]


def _fc_name(fc, depth=0):
    """Nome della fire control; attraversa gli involucri (restrict_by_policy) cercando la base nelle chiusure."""
    name = getattr(fc, '__qualname__', type(fc).__name__)

    if 'make_registry_fire_control' in name or depth > 3:
        return name

    for cell in getattr(fc, '__closure__', None) or ():
        try:
            inner = cell.cell_contents
        except ValueError:
            continue

        if callable(inner) and hasattr(inner, '__qualname__'):
            inner_name = _fc_name(inner, depth + 1)

            if 'make_registry_fire_control' in inner_name:
                return name + ' > ' + inner_name

    return name


from Code.Dynamic_War_Manager.Source.Logic import Contact_Scheduler as CS


def band_intervals(legs_a, legs_b, z_min, z_max, relative=True):
    """Intervalli in cui z_b - z_a (relative) o z_b (assoluta) e' in [z_min, z_max] (moto lineare fra i breakpoint)."""
    overlap = CS._overlap(legs_a, legs_b)

    if overlap is None:
        return []

    lo, hi = overlap
    points = CS._breakpoints(legs_a, legs_b, lo, hi)
    found = []

    def dz(t):
        return position_on_legs(legs_b, t)[2] - (position_on_legs(legs_a, t)[2] if relative else 0.0)

    if len(points) == 1:
        return [(points[0], points[0])] if z_min <= dz(points[0]) <= z_max else []

    for u, v in zip(points, points[1:]):
        d0, d1 = dz(u), dz(v)
        slope = (d1 - d0) / (v - u) if v > u else 0.0

        if abs(slope) < 1e-12:
            if z_min <= d0 <= z_max:
                found.append((u, v))
            continue

        t_a = u + (z_min - d0) / slope
        t_b = u + (z_max - d0) / slope
        s1, s2 = max(min(t_a, t_b), u), min(max(t_a, t_b), v)

        if s2 >= s1:
            found.append((s1, s2))

    return CS._merge_intervals(found)


def intersect(a, b):
    out, i, j = [], 0, 0

    while i < len(a) and j < len(b):
        lo, hi = max(a[i][0], b[j][0]), min(a[i][1], b[j][1])

        if hi >= lo - TIME_EPS:
            out.append((lo, max(lo, hi)))

        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1

    return out


_original_first_with_stock = ER._EngagementRun._first_with_stock


def _first_with_stock(self, shooter, result):
    choice = _original_first_with_stock(self, shooter, result)
    self.__dict__.setdefault('_probe_last_spec', {})[shooter.id] = choice[0] if choice else None
    return choice


_original_range_entry = ER._EngagementRun._range_entry


def _range_entry(self, shooter_id, candidate, max_range, t_from):
    entry = _original_range_entry(self, shooter_id, candidate, max_range, t_from)
    spec = self.__dict__.get('_probe_last_spec', {}).get(shooter_id)
    shooter, target = self.shadows.get(shooter_id), self.shadows.get(candidate.target_id)

    if spec is None or shooter is None or target is None or not _is_air(target.asset) \
            or (spec.weapon or '').startswith('test:') or self.grounded.at(target.id, t_from):
        return entry

    weapon = _registry_weapon(shooter.asset, spec.weapon)

    if weapon is None:
        return entry

    air = weapon.domain == 'air'

    if air and weapon.max_height_m is None:
        return entry

    if not air and (weapon.min_alt is None or weapon.max_alt is None):
        return entry

    legs_s, legs_t = self.legs.get(shooter_id), self.legs.get(candidate.target_id)

    if not (legs_s and legs_t):
        return entry

    b = _state['bucket']
    b['entry_checks_air_ceiling' if air else 'entry_checks_band'] += 1
    spheres = CS.range_intervals(legs_s, legs_t, float(max_range))

    if air:
        both = intersect(spheres, band_intervals(legs_s, legs_t, float('-inf'), weapon.max_height_m, relative=False))
    else:
        both = intersect(spheres, band_intervals(legs_s, legs_t, weapon.min_alt, weapon.max_alt))
    t_until = candidate.t_end + TIME_EPS
    band_entry = None

    for start, end in both:
        if end < t_from - TIME_EPS:
            continue
        e = max(start, t_from)
        band_entry = e if e <= t_until else None
        break

    if entry is None and band_entry is None:
        return entry

    if entry is None or band_entry is None or abs(entry - band_entry) > 1e-6:
        b['entry_differs_air' if air else 'entry_differs'] += 1

        if band_entry is None:
            b['entry_none_with_band'] += 1
        elif entry is not None and band_entry > entry:
            b['entry_later_with_band'] += 1

    return entry


_original_call_fc = ER._EngagementRun._call_fire_control


def _models(ranked):
    return tuple(w.model for w, _, _ in ranked)


def _call_fire_control(self, shooter, target, time):
    result = _original_call_fc(self, shooter, target, time)

    if 'make_registry_fire_control' not in _fc_name(self.fire_control):
        return result

    grounded = self.grounded.at(target.id, time)
    t_key = FC.target_key(target.asset, grounded=grounded)
    weapons = _weapons_of(shooter.asset)

    if t_key is None or not weapons:
        return result

    keys, dimension, is_air = t_key
    bomber = not is_air and _is_air(shooter.asset)

    if not (is_air or bomber):
        return result

    b = _state['bucket']
    b['fc_calls_alt'] += 1
    legs_s, legs_t = self.legs.get(shooter.id), self.legs.get(target.id)
    ps = position_on_legs(legs_s, time) if legs_s else None
    pt = position_on_legs(legs_t, time) if legs_t else None

    if ps is None or pt is None:
        b['fc_calls_no_legs'] += 1
        return result

    zs0, zt0 = FC._z(shooter.asset), FC._z(target.asset)
    zs, zt = float(ps[2]), float(pt[2])
    skey = FC._shooter_key(shooter.asset)
    b['_keys_s'].add((skey, keys, dimension, is_air, zs0, zt0))
    b['_keys_d'].add((skey, keys, dimension, is_air, zs, zt))

    if is_air:
        static = _models(FC.rank_weapons(weapons, keys, dimension, True, zs0, zt0, True))
        dynamic = _models(FC.rank_weapons(weapons, keys, dimension, True, zs, zt, True))

        if static != dynamic:
            b['fc_air_differs'] += 1

        unfiltered = FC.rank_weapons(weapons, keys, dimension, True, None, None, True)

        if not dynamic and unfiltered:
            b['fc_air_defer'] += 1

            for weapon, _, _ in unfiltered:
                if weapon.air_range_m is None:
                    continue
                spheres = CS.range_intervals(legs_s, legs_t, weapon.air_range_m)
                if weapon.domain == 'air':
                    if weapon.max_height_m is not None:
                        spheres = intersect(spheres, band_intervals(legs_s, legs_t, float('-inf'), weapon.max_height_m, relative=False))
                elif weapon.min_alt is not None and weapon.max_alt is not None:
                    spheres = intersect(spheres, band_intervals(legs_s, legs_t, weapon.min_alt, weapon.max_alt))
                if any(end >= time - TIME_EPS for _, end in spheres):
                    b['fc_air_defer_entry'] += 1
                    break

            if static:
                b['fc_air_defer_static_ok'] += 1
    elif zs0 is not None and zt0 is not None and abs((zs - zt) - (zs0 - zt0)) > 1e-6:
        b['fc_bomb_alt_differs'] += 1

    return result


ER._EngagementRun._call_fire_control = _call_fire_control
ER._EngagementRun._first_with_stock = _first_with_stock
ER._EngagementRun._range_entry = _range_entry

_original_run = ER._EngagementRun.run


def _run(self):
    result = _original_run(self)
    b = _state['bucket']
    b['engagements'] += 1
    b['salvos'] += len(result.salvos)
    fc_name = _fc_name(self.fire_control)
    registry_fc = 'make_registry_fire_control' in fc_name
    b['fc'][fc_name] = b['fc'].get(fc_name, 0) + 1

    for salvo in result.salvos:
        shooter = self.shadows.get(salvo.shooter_id)
        target = self.shadows.get(salvo.target_id)

        if shooter is None or target is None or not _is_air(target.asset):
            continue

        if self.grounded.at(salvo.target_id, salvo.t_launch):
            continue

        b['salvos_air'] += 1
        legs_s, legs_t = self.legs.get(salvo.shooter_id), self.legs.get(salvo.target_id)
        ps = position_on_legs(legs_s, salvo.t_launch) if legs_s else None
        pt = position_on_legs(legs_t, salvo.t_launch) if legs_t else None

        if ps is None or pt is None:
            b['salvos_air_no_legs'] += 1
            continue

        zs, zt = ps[2], pt[2]
        name = salvo.spec.weapon or ''

        if name.startswith('test:'):
            b['salvos_air_test_weapon'] += 1

        weapon = None if name.startswith('test:') else _registry_weapon(shooter.asset, name)

        if weapon is not None:
            b['salvos_air_registry_weapon'] += 1
            status = _band_status(weapon, zs, zt)

            if status is not None:
                b['sw_with_band'] += 1
                zs0, zt0 = FC._z(shooter.asset), FC._z(target.asset)

                if zs0 is not None and zt0 is not None and abs((zt - zs) - (zt0 - zs0)) > 1.0:
                    b['sw_static_differs'] += 1

                if status == 'above':
                    b['sw_above_max'] += 1
                    pair = f'{_model(shooter.asset)}:{name}'
                    b['models_above'][pair] = b['models_above'].get(pair, 0) + 1
                elif status == 'below':
                    b['sw_below_min'] += 1
                    pair = f'{_model(shooter.asset)}:{name}'
                    b['models_below'][pair] = b['models_below'].get(pair, 0) + 1

        if not _is_air(shooter.asset):
            cyl = _cylinder(shooter.asset)

            if cyl is not None:
                b['cyl_available'] += 1
                base = zs + (float(cyl.bottom_center.z) - float(shooter.asset.position.z))
                top = base + float(cyl.height)
                dh = math.hypot(pt[0] - ps[0], pt[1] - ps[1])

                pair = f'{_model(shooter.asset)}:{name}'

                if zt > top + 1e-6:
                    b['cyl_above'] += 1
                    b['models_cyl_above'][pair] = b['models_cyl_above'].get(pair, 0) + 1
                elif zt < base - 1e-6:
                    b['cyl_below'] += 1

                if dh > float(cyl.radius) + 1e-6:
                    b['cyl_outside_radius'] += 1
                    b['models_cyl_outside'][pair] = b['models_cyl_outside'].get(pair, 0) + 1

    if registry_fc:
        for observer_id, candidates in self.candidates.items():
            observer = self.shadows.get(observer_id)

            if observer is None:
                continue

            for candidate in candidates:
                target = self.shadows.get(candidate.target_id)

                if target is None or not _is_air(target.asset) or self.grounded.at(target.id, candidate.t_ready):
                    continue

                t_key = FC.target_key(target.asset)
                weapons = _weapons_of(observer.asset)

                if t_key is None or not weapons:
                    continue

                keys, dimension, is_air = t_key

                if not is_air:
                    continue

                unfiltered = FC.rank_weapons(weapons, keys, dimension, True, None, None, False)

                if not unfiltered:
                    continue

                b['cand_air_registry'] += 1
                static = FC.rank_weapons(weapons, keys, dimension, True, FC._z(observer.asset),
                                         FC._z(target.asset), True)
                legs_o, legs_t = self.legs.get(observer_id), self.legs.get(candidate.target_id)

                if not (legs_o and legs_t):
                    continue

                span_o, span_t = legs_span(legs_o), legs_span(legs_t)
                hi = min(candidate.t_end, span_o[1], span_t[1])
                lo = min(max(candidate.t_ready, span_o[0], span_t[0]), hi)
                sphere_hit = band_hit = False
                static_models = {w.model for w, _, _ in static}

                for t in _sample_times(lo, hi):
                    po, pt = position_on_legs(legs_o, t), position_on_legs(legs_t, t)

                    if po is None or pt is None:
                        continue

                    d = math.dist(po, pt)

                    for weapon, _, _ in unfiltered:
                        reach = weapon.air_range_m
                        in_sphere = reach is None or d <= reach + 1e-6

                        if in_sphere and weapon.model in static_models:
                            sphere_hit = True

                        if in_sphere and FC.in_altitude_envelope(weapon, po[2], pt[2]):
                            band_hit = True

                if not static:
                    b['cand_static_excluded'] += 1

                    if band_hit:
                        b['cand_static_excluded_dyn_ok'] += 1
                elif sphere_hit and not band_hit:
                    b['cand_static_ok_dyn_never'] += 1

    return result


_original_run_session = SS.run_session


def _run_session(*args, **kwargs):
    _state['bucket'] = _new_bucket()
    return _original_run_session(*args, **kwargs)


_original_summarize = SB.summarize_run


def _summarize_run(order, forces_a, forces_b, kwargs, outcome):
    summary = _original_summarize(order, forces_a, forces_b, kwargs, outcome)
    bucket = _state['bucket']
    bucket['fc_keys_static'] = len(bucket.pop('_keys_s'))
    bucket['fc_keys_dynamic'] = len(bucket.pop('_keys_d'))
    summary[KEY] = bucket
    _state['bucket'] = _new_bucket()
    return summary


ER._EngagementRun.run = _run
SS.run_session = _run_session
SB.summarize_run = _summarize_run

rc = SB.main(['--compare', BASELINE, '--save', f'{OUT}/capture.json', '--quiet', '--ignore', KEY]
             + (['--only', ONLY] if ONLY else []))
print('PROBE_RC', rc)

with open(f'{OUT}/capture.json', encoding='utf-8') as handle:
    runs = json.load(handle)['runs']

with open(BASELINE, encoding='utf-8') as handle:
    photo = set(json.load(handle).get('runs', {}))

totals, above, below, fcs, units = Counter(), Counter(), Counter(), Counter(), Counter()
cyl_above_models, cyl_outside_models, cyl_units = Counter(), Counter(), Counter()
rows = []

for key in sorted(runs):
    bucket = runs[key].get(KEY)

    if bucket is None:
        continue

    for name in COUNTERS:
        totals[name] += bucket[name]

    above.update(bucket['models_above'])
    below.update(bucket['models_below'])
    fcs.update(bucket['fc'])
    cyl_above_models.update(bucket['models_cyl_above'])
    cyl_outside_models.update(bucket['models_cyl_outside'])

    if bucket['cyl_above'] or bucket['cyl_outside_radius']:
        cyl_units[key.split('/', 1)[0]] += 1
    flagged = (bucket['sw_above_max'] + bucket['sw_below_min'] + bucket['cyl_above'] + bucket['cyl_below']
               + bucket['cand_static_excluded_dyn_ok'] + bucket['cand_static_ok_dyn_never'] + bucket['entry_differs']
               + bucket['entry_differs_air'] + bucket['fc_air_differs'] + bucket['fc_air_defer']
               + bucket['fc_bomb_alt_differs'])
    if bucket['entry_differs'] + bucket['entry_differs_air'] + bucket['fc_air_differs'] + bucket['fc_air_defer'] \
            + bucket['fc_bomb_alt_differs']:
        rows.append(f"SWITCH {key}: entry={bucket['entry_differs']} entry_air={bucket['entry_differs_air']} "
                    f"fc_air={bucket['fc_air_differs']} defer={bucket['fc_air_defer']} "
                    f"defer_static_ok={bucket['fc_air_defer_static_ok']} bomb={bucket['fc_bomb_alt_differs']}")

    if flagged:
        units[key.split('/', 1)[0]] += 1
        tag = '' if key in photo else ' [NUOVA]'
        rows.append(f"OUT {key}{tag}: " + ' '.join(f'{n}={bucket[n]}' for n in (
            'salvos_air', 'sw_above_max', 'sw_below_min', 'cyl_above', 'cyl_below',
            'cand_static_excluded_dyn_ok', 'cand_static_ok_dyn_never', 'entry_checks_band', 'entry_differs',
            'entry_none_with_band', 'entry_later_with_band', 'entry_checks_air_ceiling', 'entry_differs_air', 'fc_calls_alt', 'fc_air_differs', 'fc_air_defer', 'fc_bomb_alt_differs', 'fc_keys_static', 'fc_keys_dynamic')))

print(f'RUNS {len(runs)} (in fotografia {sum(k in photo for k in runs)}, nuove {sum(k not in photo for k in runs)})')
print(f"RUNS_SWITCH {sum(r.startswith('SWITCH') for r in rows)}")
print(f'RUNS_FLAGGED {sum(r.startswith("OUT") for r in rows)} (in fotografia {sum(r.startswith("OUT") and "[NUOVA]" not in r for r in rows)})')
print('TOTALS', json.dumps(dict(totals), sort_keys=True))
print('FIRE_CONTROLS', json.dumps(dict(fcs), sort_keys=True))
print('ABOVE', json.dumps(above.most_common(30)))
print('BELOW', json.dumps(below.most_common(30)))
print('UNITS', json.dumps(dict(sorted(units.items()))))
print('CYL_ABOVE_MODELS', json.dumps(cyl_above_models.most_common(30)))
print('CYL_OUTSIDE_MODELS', json.dumps(cyl_outside_models.most_common(30)))
print('CYL_UNITS', json.dumps(dict(sorted(cyl_units.items()))))

for line in rows:
    print(line)

with open(f'{OUT}/stats.json', 'w', encoding='utf-8') as handle:
    json.dump({'totals': dict(totals), 'above': dict(above), 'below': dict(below), 'fire_controls': dict(fcs),
               'units': dict(units), 'rows': rows}, handle, indent=1, sort_keys=True)
