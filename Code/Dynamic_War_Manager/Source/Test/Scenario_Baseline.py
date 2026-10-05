"""Fotografia di non regressione degli scenari di sessione (Fase 0 del piano della Missione).

V. `Analysis/Document/Piano_Implementazione_Missione.md`, §0 punto 2 e Fase 0: dalla Fase 3 la
porta di sessione cambia, e servono numeri per dimostrare che a parita' di input il motore
produce la stessa storia. Questo strumento esegue gli scenari di sessione esistenti, riassume
ogni `SessionOutcome` in una forma deterministica e la salva su JSON (`--capture`), oppure la
confronta con una fotografia salvata (`--compare`).

Il nome del file NON comincia con `Test_`: `unittest discover -p "Test_*.py"` non lo esegue.

## Come trova gli scenari: riuso, non duplicazione

Gli scenari NON sono ricostruiti qui. Lo strumento esegue le stesse "unita'" dei test:

* per le classi di scenario (S1-S19, validazione) il loro `setUpClass`, che costruisce le
  forze con `Scenario_Fixtures` ed esegue tutte le repliche/varianti usate dai test;
* per `Test_Session_Simulator` (test dell'orchestratore, nessun `setUpClass`) un elenco
  scelto di METODI di test, eseguiti con `TestCase.run` (setUp/tearDown compresi).

Durante l'esecuzione `Session_Simulator.run_session` e' sostituita da un registratore che
chiama l'originale, poi riassume l'esito E lo stato reale degli asset delle forze passate
(letto subito dopo la chiamata: in S11 e nella mini-campagna di validazione la sessione
successiva muta di nuovo le stesse istanze). Tutti i chiamanti (Scenario_Fixtures.run, S11,
Test_Session_Simulator) passano per l'attributo di modulo `SS.run_session`, quindi il patch
li intercetta tutti. Le asserzioni dei test NON sono eseguite per le classi di scenario
(solo `setUpClass`); per i metodi di Test_Session_Simulator un'asserzione fallita e'
segnalata su stderr ma non impedisce la registrazione.

Le repliche che i metodi di test di scenario rieseguono per verificare la riproducibilita'
(es. S9R `test_reproducible_with_the_same_seed`, la replica di S19 in `setUpClass`) sono
comunque catturate se stanno in `setUpClass`; quelle nei metodi no (sono copie, per
costruzione, di un'esecuzione gia' catturata).

## Nomi stabili

Chiave di un'esecuzione: `<scenario>/<session_id>[/<variante>]`. Molte classi eseguono lo
STESSO `session_id` in piu' varianti (con/senza CAS, soglie diverse, ...); la variante e'
ricavata dall'indice di occorrenza di quel `session_id` nell'unita' (l'ordine delle chiamate
in `setUpClass` e' fisso), tradotto in un nome leggibile dalla tabella `UNITS`. Senza nome
dichiarato si usa `#<n>`. Se un `setUpClass` cambia l'ordine delle varianti, le chiavi
cambiano di conseguenza: va aggiornata la tabella dei nomi.

## Cosa registra (per esecuzione)

`summarize_run`: intervallo della sessione, forze dei due lati e parametri di chiamata
riconoscibili, esiti di forza per ingaggio (HELD/DISENGAGED/DESTROYED con tempi, perdite,
erosione, shock, soglia), stato finale per asset (salute, operativo, distrutto, munizioni,
scorta per arma, intercettori, carburante), munizioni consumate per asset e per arma,
intercettazioni per asset e per arma, eventi di carburante, conteggi (salve, intercettazioni,
danni, distruzioni) e le liste complete degli eventi di danno, munizioni e intercettazione in
ordine d'esito. I float sono arrotondati a `ROUND_DIGITS` decimali (-0.0 normalizzato), le
chiavi sono ordinate: due catture dello stesso codice devono essere identiche byte per byte.

## Parametri di chiamata dopo la F3 (porta delle missioni)

Dalla F3 del piano della Missione `run_session` non ha piu' il parametro `routes`: le rotte
arrivano dalle missioni dell'ordine. Perche' la fotografia della Fase 0 resti confrontabile, la
voce `call.parameters.routes` e' RICOSTRUITA dalle missioni (`Mission_Adapter.mission_routes`:
gli asset che ricevono una rotta), con lo stesso significato di prima; una lista vuota equivale
all'assenza della voce (prima `routes={}` e nessun `routes` producevano due forme diverse dello
stesso fatto, "nessuno si muove"), e il confronto la normalizza cosi' su entrambi i lati.

## Uso (dalla root del repo, con l'interprete della macchina)

    python3 -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline --capture out.json
    python3 -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline \\
        --compare Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json
    # solo alcuni scenari (regex sul nome dell'unita' o sulla chiave):
    python3 -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline --compare <json> --only 'S19'
    # confronto fra due file gia' catturati, senza eseguire nulla:
    python3 -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline --compare <a.json> --against <b.json>

Exit code: 0 se identiche, 1 se ci sono differenze (o errori di unita'), 2 per uso errato.
"""

import argparse
import importlib
import json
import math
import re
import sys
import time
import unittest
from collections import OrderedDict
from typing import Callable, Dict, List, Optional, Sequence, Tuple
from unittest.mock import patch

_TEST = 'Code.Dynamic_War_Manager.Source.Test.'
_SS_MODULE = 'Code.Dynamic_War_Manager.Source.Logic.Session_Simulator'

FORMAT_VERSION = 1
ROUND_DIGITS = 6

# Righe di differenza stampate al massimo per esecuzione in --compare.
MAX_DIFF_LINES_PER_RUN = 20


# ── TABELLA DELLE UNITA' ──────────────────────────────────────────────────────

def _by_occurrence(*names: str) -> Callable:
    """Nome di variante = `names[occorrenza]` (occorrenza del session_id nell'unita')."""
    def label(cls, session_id: str, occurrence: int) -> Optional[str]:
        return names[occurrence] if occurrence < len(names) else f'#{occurrence}'

    return label


def _s2_label(cls, session_id: str, occurrence: int) -> Optional[str]:
    # Per seed: strike di base (S2-k), SEAD (S2-k-sead), strike dopo la SEAD (S2-k di nuovo).
    if session_id.endswith('-sead'):
        return None if occurrence == 0 else f'#{occurrence}'

    return ('baseline', 'after_sead')[occurrence] if occurrence < 2 else f'#{occurrence}'


def _s9_label(cls, session_id: str, occurrence: int) -> Optional[str]:
    return f'detection_factor={cls.FACTORS[occurrence]}' if occurrence < len(cls.FACTORS) else f'#{occurrence}'


def _s9r_label(cls, session_id: str, occurrence: int) -> Optional[str]:
    return cls.VARIANTS[occurrence] if occurrence < len(cls.VARIANTS) else f'#{occurrence}'


def _s17_label(cls, session_id: str, occurrence: int) -> Optional[str]:
    if occurrence < len(cls.SCALE):
        mil_category, k = cls.SCALE[occurrence]
        return f'{mil_category}_k={k}'

    return f'#{occurrence}'


def _single_or_index(cls, session_id: str, occurrence: int) -> Optional[str]:
    return None if occurrence == 0 else f'#{occurrence}'


# (nome scenario, modulo, classe, metodi | None, funzione di nome variante).
# metodi None = si esegue `setUpClass`/`tearDownClass`; altrimenti i metodi di test elencati.
UNITS: Sequence[Tuple[str, str, str, Optional[Tuple[str, ...]], Callable]] = (
    # ── S1-S9 ──
    ('S1', 'Test_Session_Scenarios', 'TestS1CombinedArmsWithCAS', None, _by_occurrence('with_cas', 'without_cas')),
    ('S2', 'Test_Session_Scenarios', 'TestS2PreliminarySEAD', None, _s2_label),
    ('S3', 'Test_Session_Scenarios', 'TestS3StealthVersusMass', None, _by_occurrence('control', 'stealth')),
    ('S4', 'Test_Session_Scenarios', 'TestS4SAMAsThirdComponent', None, _by_occurrence('no_sam', 'with_sam')),
    ('S5', 'Test_Session_Scenarios', 'TestS5DeepInterdictionThreeLayers', None, _by_occurrence('press_on', 'default')),
    ('S6', 'Test_Session_Scenarios', 'TestS6CarrierGroupVersusCoastalDefence', None, _single_or_index),
    ('S7', 'Test_Session_Scenarios', 'TestS7LogisticInterdiction', None, _single_or_index),
    ('S8', 'Test_Session_Scenarios', 'TestS8MultiFrontScale', None, _single_or_index),
    ('S9', 'Test_Session_Scenarios', 'TestS9PartialFogOfWar', None, _s9_label),
    ('S9R', 'Test_Session_Scenarios', 'TestS9RegionReconSnapshot', None, _s9r_label),
    # ── S10-S18 ──
    ('S10', 'Test_Session_Scenarios_S10_S18', 'TestS10DisengagementThreshold', None,
     _by_occurrence('erosion', 'shock', 'control', 'press_on', 'default')),
    ('S11', 'Test_Session_Scenarios_S10_S18', 'TestS11SessionBoundary', None, _single_or_index),
    ('S12', 'Test_Session_Scenarios_S10_S18', 'TestS12C2Decapitation', None, _by_occurrence('c2_strike', 'prolonged')),
    ('S13', 'Test_Session_Scenarios_S10_S18', 'TestS13ForwardFARPInterdiction', None, _single_or_index),
    ('S14', 'Test_Session_Scenarios_S10_S18', 'TestS14StrategicBombingOfProduction', None, _single_or_index),
    ('S15', 'Test_Session_Scenarios_S10_S18', 'TestS15UrbanProximityROEContract', None, _by_occurrence('roe', 'control')),
    ('S16', 'Test_Session_Scenarios_S10_S18', 'TestS16NavalInstallation', None, _single_or_index),
    ('S17', 'Test_Session_Scenarios_S10_S18', 'TestS17HierarchicalScaleSweep', None, _s17_label),
    ('S18', 'Test_Session_Scenarios_S10_S18', 'TestS18TransportNetworkInterdiction', None, _by_occurrence('network', 'far')),
    # ── S19 ──
    ('S19', 'Test_Session_Scenarios_S19', 'TestS19RegistryFireControl', None, _by_occurrence('run', 'replay')),
    ('S19AD', 'Test_Session_Scenarios_S19_Air_Defence', 'TestS19AirDefenceAllocation', None,
     _by_occurrence('strela_overflight_ifv_only', 'strela_standoff', 'tor_rear', 'tor_forward_ifv_only')),
    # ── Validazione (composizione di S1: determinismo e mini-campagna di agnosticismo) ──
    ('VAL-det', 'Test_Session_Validation', 'TestDeterminism', None, _by_occurrence('first', 'second')),
    ('VAL-agn', 'Test_Session_Validation', 'TestAgnosticEndToEnd', None, _by_occurrence('single', 'campaign')),
    # ── Orchestratore (Test_Session_Simulator): scenari minimi con asset Mobile e Pd imposte ──
    ('ORC-base', 'Test_Session_Simulator', 'TestEndToEnd', ('test_declared_interval',), _single_or_index),
    ('ORC-seed', 'Test_Session_Simulator', 'TestSeedDiscipline',
     ('test_different_session_id_changes_the_draws',), _single_or_index),
    ('ORC-nocontact', 'Test_Session_Simulator', 'TestNoContact',
     ('test_far_apart_forces_produce_no_engagement',), _single_or_index),
    ('ORC-twofronts', 'Test_Session_Simulator', 'TestTwoFronts',
     ('test_connected_forces_are_one_engagement', 'test_health_is_chained_within_the_joint_engagement',
      'test_joint_engagement_is_deterministic', 'test_stable_ids_from_the_constructor'),
     _by_occurrence('first', 'second', 'reversed_red')),
    ('ORC-interval', 'Test_Session_Simulator', 'TestSessionInterval',
     ('test_open_session_requires_horizon', 'test_salvos_in_flight_extend_the_outcome'), _single_or_index),
    ('ORC-fuel', 'Test_Session_Simulator', 'TestFuelExhaustion',
     ('test_exhaustion_is_reported_not_simulated',), _single_or_index),
)
# Esclusi di proposito da Test_Session_Simulator: TestInputs (solo chiamate che sollevano),
# TestNoContact.test_nothing_moves_nothing_meets/test_empty_sides (esito vuoto per
# costruzione), i metodi di TestTwoFronts/TestSeedDiscipline che ripetono 'S-fronts'/'S-alpha'
# con uno spy (stessa esecuzione gia' catturata) e test_engagement_uses_the_documented_stream
# (verifica il flusso RNG con un patch, non e' uno scenario).


# ── NORMALIZZAZIONE ───────────────────────────────────────────────────────────

def _num(value):
    """Float arrotondato in modo stabile; -0.0 -> 0.0; nan/inf come stringhe."""
    value = float(value)

    if math.isnan(value) or math.isinf(value):
        return repr(value)

    rounded = round(value, ROUND_DIGITS)
    return 0.0 if rounded == 0 else rounded


def norm(value):
    """Valore JSON deterministico: float arrotondati, dict con chiavi stringa, tuple -> liste."""
    if value is None or isinstance(value, (bool, str)):
        return value

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return _num(value)

    if isinstance(value, dict):
        return {str(key): norm(item) for key, item in value.items()}

    if isinstance(value, (list, tuple)):
        return [norm(item) for item in value]

    if isinstance(value, (set, frozenset)):
        return sorted(norm(item) for item in value)

    # Numeri sympy/numpy e simili.
    try:
        return _num(value)
    except (TypeError, ValueError):
        return repr(value)


def _safe(asset, name):
    try:
        value = getattr(asset, name)
        return value() if callable(value) else value
    except Exception:   # noqa: BLE001 — un attributo assente o non applicabile vale None
        return None


# ── RIASSUNTO DI UN'ESECUZIONE ────────────────────────────────────────────────

def _force_list(forces) -> List:
    return list(forces or [])


def _asset_state(asset) -> Dict:
    return {
        'health': _safe(asset, 'health'),
        'operative': _safe(asset, 'is_operative'),
        'destroyed': _safe(asset, 'is_destroyed'),
        'ammunition': _safe(asset, 'ammunition'),
        'stores': _safe(asset, 'stores'),
        'interceptor_stock': _safe(asset, 'interceptor_stock'),
        'fuel': _safe(asset, 'fuel'),
    }


def _call_parameters(kwargs: Dict, order=None) -> Dict:
    """Parametri di chiamata confrontabili (i callable/oggetti solo come presenza).

    `routes` e' ricostruito dalle missioni di `order` (v. docstring del modulo, F3).
    """
    described = {}
    missions = tuple(getattr(order, 'missions', ()) or ())

    if missions and 'routes' not in kwargs:
        from Code.Dynamic_War_Manager.Source.Logic import Mission_Adapter as MA
        described['routes'] = sorted(MA.mission_routes(missions, order.t_start))

    for key in sorted(kwargs):
        value = kwargs[key]

        if key == 'routes':
            described[key] = sorted(value) if value else []
        elif key == 'thresholds':
            described[key] = value
        elif isinstance(value, (int, float, str, bool)) or value is None:
            described[key] = value
        else:
            described[key] = 'callable' if callable(value) else type(value).__name__

    return described


def summarize_run(order, forces_a, forces_b, kwargs: Dict, outcome) -> Dict:
    """Riassunto deterministico di una chiamata a `run_session` (v. docstring del modulo)."""
    forces = _force_list(forces_a) + _force_list(forces_b)

    engagements = []
    for engagement in outcome.engagement_outcomes:
        engagements.append([{
            'force_id': fo.force_id, 'side': fo.side, 'outcome': fo.outcome, 'time': fo.time,
            'triggers': list(fo.triggers), 'committed': fo.committed, 'lost': fo.lost,
            'erosion': fo.erosion, 'max_shock': fo.max_shock, 'temper': fo.temper,
            'breakpoint': fo.breakpoint, 'morale': fo.morale, 'force_ratio': fo.force_ratio,
            'unanswered_fraction': fo.unanswered_fraction} for fo in engagement])

    force_outcomes: Dict[str, List[str]] = {}
    for engagement in outcome.engagement_outcomes:
        for fo in engagement:
            force_outcomes.setdefault(fo.force_id, []).append(fo.outcome)

    interceptions_by_weapon: Dict[str, Dict[str, int]] = {}
    for event in outcome.interception_events:
        by_weapon = interceptions_by_weapon.setdefault(event.asset_id, {})
        key = str(event.weapon)
        by_weapon[key] = by_weapon.get(key, 0) + event.interceptions

    ammunition_by_weapon = {asset_id: {str(weapon): rounds for weapon, rounds in by_weapon.items()}
                            for asset_id, by_weapon in outcome.ammunition_consumed_by_weapon().items()}

    fuel = {}
    for event in outcome.fuel_events:
        fuel.setdefault(event.asset_id, []).append({
            'time': event.time, 'distance': event.distance, 'distance_covered': event.distance_covered,
            'amount': event.amount, 'fuel_before': event.fuel_before, 'fuel_after': event.fuel_after,
            'exhausted': event.exhausted, 'regime': event.regime})

    summary = {
        'session': {'session_id': outcome.session_id, 't_start': outcome.t_start, 't_end': outcome.t_end,
                    'order_t_start': order.t_start, 'order_t_end': order.t_end,
                    'salvo_window': getattr(order, 'salvo_window', None)},
        'call': {'forces_a': [f.id for f in _force_list(forces_a)],
                 'forces_b': [f.id for f in _force_list(forces_b)],
                 'parameters': _call_parameters(kwargs, order)},
        'force_outcomes': force_outcomes,
        'engagements': engagements,
        'assets': {asset_id: _asset_state(asset)
                   for force in forces for asset_id, asset in (force.assets or {}).items()},
        'ammunition_consumed': ammunition_by_weapon,
        'interceptions': interceptions_by_weapon,
        'fuel': fuel,
        'counts': {
            'engagements': len(outcome.engagement_outcomes),
            'salvos': len(outcome.ammunition_events),
            'rounds': sum(e.rounds for e in outcome.ammunition_events),
            'interception_events': len(outcome.interception_events),
            'interceptions': sum(e.interceptions for e in outcome.interception_events),
            'damage_events': len(outcome.damage_events),
            'destroyed_events': sum(1 for e in outcome.damage_events if e.destroyed),
            'fuel_events': len(outcome.fuel_events),
            'fuel_exhausted': sum(1 for e in outcome.fuel_events if e.exhausted),
        },
        # Liste complete, nell'ordine dell'esito (che fa parte del contratto).
        'damage_events': [[e.time, e.target_id, e.source_id, e.weapon, e.outcome, e.health_before,
                           e.health_after, e.destroyed] for e in outcome.damage_events],
        'ammunition_events': [[e.time, e.asset_id, e.weapon, e.rounds] for e in outcome.ammunition_events],
        'interception_events': [[e.time, e.asset_id, e.weapon, e.interceptions, e.force_id, list(e.salvo_ids)]
                                for e in outcome.interception_events],
    }
    return norm(summary)


# ── REGISTRATORE ──────────────────────────────────────────────────────────────

class _Recorder:
    """Sostituto di `run_session`: chiama l'originale e registra il riassunto."""

    def __init__(self, original: Callable):
        self.original = original
        self.calls: List[Tuple[str, Dict]] = []

    def __call__(self, order, forces_a, forces_b, fire_control, **kwargs):
        forces_a, forces_b = list(forces_a), list(forces_b)
        outcome = self.original(order, forces_a, forces_b, fire_control, **kwargs)
        self.calls.append((order.session_id, summarize_run(order, forces_a, forces_b, kwargs, outcome)))
        return outcome


def _run_unit(module_name: str, class_name: str, methods: Optional[Tuple[str, ...]]) -> List[str]:
    """Esegue un'unita'; restituisce le segnalazioni (test falliti) per stderr."""
    module = importlib.import_module(_TEST + module_name)
    cls = getattr(module, class_name)
    notes = []

    if methods is None:
        try:
            cls.setUpClass()
        except Exception:
            # Un setUpClass interrotto dopo super().setUpClass() lascerebbe attivi i patch
            # dei logger di LoggerSilencer: si prova comunque a chiuderli.
            try:
                cls.tearDownClass()
            except Exception:   # noqa: BLE001
                pass
            raise

        cls.tearDownClass()
        return notes

    for method in methods:
        result = unittest.TestResult()
        cls(method).run(result)

        for test, trace in result.failures + result.errors:
            notes.append(f'{class_name}.{method}: {trace.strip().splitlines()[-1]}')

    return notes


def capture(only: Optional[str] = None, verbose: bool = True) -> Dict:
    """Esegue le unita' (filtrate da `only`) e restituisce la fotografia."""
    from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F

    SS = importlib.import_module(_SS_MODULE)
    pattern = re.compile(only) if only else None
    runs: Dict[str, Dict] = {}
    errors: Dict[str, str] = {}
    logger_patches = F.start_logger_patches()

    if verbose:
        # Quale codice gira davvero (v. memoria project_worktree_pythonpath_test_gotcha).
        print(f'engine: {SS.__file__}', file=sys.stderr)

    try:
        for label, module_name, class_name, methods, variant in UNITS:
            # Senza eseguire l'unita' le sue chiavi non si conoscono: in cattura il filtro e'
            # sul nome dell'unita' (con e senza la '/' che nelle chiavi lo segue).
            if pattern is not None and not (pattern.search(label) or pattern.search(label + '/')):
                continue

            module = importlib.import_module(_TEST + module_name)
            cls = getattr(module, class_name)
            recorder = _Recorder(SS.run_session)
            started = time.perf_counter()

            try:
                with patch.object(SS, 'run_session', recorder):
                    notes = _run_unit(module_name, class_name, methods)
            except Exception as error:   # noqa: BLE001 — un'unita' rotta non ferma le altre
                errors[label] = f'{type(error).__name__}: {error}'
                notes = []

            occurrences: Dict[str, int] = {}

            for session_id, summary in recorder.calls:
                occurrence = occurrences.get(session_id, 0)
                occurrences[session_id] = occurrence + 1
                name = variant(cls, session_id, occurrence)
                key = f'{label}/{session_id}' + (f'/{name}' if name else '')

                if key in runs:
                    raise RuntimeError(f'duplicate scenario key {key!r}: fix the variant names in UNITS')

                runs[key] = summary

            if verbose:
                print(f'[{label}] {len(recorder.calls)} runs in {time.perf_counter() - started:.1f} s',
                      file=sys.stderr)
                for note in notes:
                    print(f'  WARNING test failed: {note}', file=sys.stderr)
    finally:
        F.stop_logger_patches(logger_patches)

    return {'meta': {'format': FORMAT_VERSION, 'round_digits': ROUND_DIGITS, 'filter': only},
            'errors': errors, 'runs': runs}


def dump(snapshot: Dict, path: str) -> None:
    with open(path, 'w', encoding='utf-8') as handle:
        json.dump(snapshot, handle, sort_keys=True, indent=1, ensure_ascii=False)
        handle.write('\n')


def load(path: str) -> Dict:
    with open(path, encoding='utf-8') as handle:
        return json.load(handle)


# ── CONFRONTO ─────────────────────────────────────────────────────────────────

def _flatten(value, prefix: str = '') -> 'OrderedDict[str, object]':
    flat: 'OrderedDict[str, object]' = OrderedDict()

    if isinstance(value, dict):
        if not value:
            flat[prefix] = {}
        for key in sorted(value):
            flat.update(_flatten(value[key], f'{prefix}.{key}' if prefix else str(key)))
    elif isinstance(value, list):
        if not value:
            flat[prefix] = []
        for index, item in enumerate(value):
            flat.update(_flatten(item, f'{prefix}[{index}]'))
    else:
        flat[prefix] = value

    return flat


def _without_empty_routes(run: Dict) -> Dict:
    """Copia del riassunto senza `call.parameters.routes` se vuoto (v. docstring del modulo, F3)."""
    parameters = run.get('call', {}).get('parameters', {})

    if parameters.get('routes', None) != []:
        return run

    parameters = {key: value for key, value in parameters.items() if key != 'routes'}
    return {**run, 'call': {**run['call'], 'parameters': parameters}}


def compare(baseline: Dict, current: Dict, only: Optional[str] = None) -> List[str]:
    """Differenze fra due fotografie, per scenario e chiave. Lista vuota = identiche."""
    pattern = re.compile(only) if only else None
    lines: List[str] = []

    def selected(key: str) -> bool:
        return pattern is None or bool(pattern.search(key))

    for label, error in sorted(current.get('errors', {}).items()):
        if selected(label):
            lines.append(f'ERROR {label}: {error}')

    base_runs = {k: v for k, v in baseline.get('runs', {}).items() if selected(k)}
    cur_runs = {k: v for k, v in current.get('runs', {}).items() if selected(k)}

    for key in sorted(set(base_runs) - set(cur_runs)):
        lines.append(f'MISSING {key}: in the baseline, not in the current capture')

    for key in sorted(set(cur_runs) - set(base_runs)):
        lines.append(f'NEW {key}: in the current capture, not in the baseline')

    for key in sorted(set(base_runs) & set(cur_runs)):
        old_run, new_run = _without_empty_routes(base_runs[key]), _without_empty_routes(cur_runs[key])

        if old_run == new_run:
            continue

        old, new = _flatten(old_run), _flatten(new_run)
        diffs = [path for path in sorted(set(old) | set(new)) if old.get(path, '<absent>') != new.get(path, '<absent>')]
        lines.append(f'DIFF {key}: {len(diffs)} values differ')

        for path in diffs[:MAX_DIFF_LINES_PER_RUN]:
            lines.append(f'    {path}: {old.get(path, "<absent>")!r} -> {new.get(path, "<absent>")!r}')

        if len(diffs) > MAX_DIFF_LINES_PER_RUN:
            lines.append(f'    ... {len(diffs) - MAX_DIFF_LINES_PER_RUN} more')

    return lines


# ── CLI ───────────────────────────────────────────────────────────────────────

def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description='Session scenario regression snapshot (Fase 0).')
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--capture', metavar='OUT_JSON', help='run the scenarios and write the snapshot')
    mode.add_argument('--compare', metavar='BASELINE_JSON', help='run the scenarios and diff against a snapshot')
    parser.add_argument('--against', metavar='CURRENT_JSON',
                        help='with --compare: diff against this file instead of running the scenarios')
    parser.add_argument('--save', metavar='OUT_JSON', help='with --compare: also save the current capture')
    parser.add_argument('--only', metavar='REGEX',
                        help='only units whose name matches (capture), only matching keys (compare)')
    parser.add_argument('--quiet', action='store_true', help='no per-unit progress on stderr')
    args = parser.parse_args(argv)

    started = time.perf_counter()

    if args.capture:
        if args.against or args.save:
            parser.error('--against/--save only with --compare')   # esce con 2

        snapshot = capture(args.only, verbose=not args.quiet)
        dump(snapshot, args.capture)
        print(f'captured {len(snapshot["runs"])} runs, {len(snapshot["errors"])} unit errors, '
              f'{time.perf_counter() - started:.1f} s -> {args.capture}')
        return 1 if snapshot['errors'] else 0

    baseline = load(args.compare)

    if args.against:
        current = load(args.against)
    else:
        current = capture(args.only, verbose=not args.quiet)

        if args.save:
            dump(current, args.save)

    lines = compare(baseline, current, args.only)

    for line in lines:
        print(line)

    compared = len([k for k in current.get('runs', {})
                    if not args.only or re.search(args.only, k)])
    print(f'compared {compared} runs: {"IDENTICAL" if not lines else f"{len(lines)} difference lines"} '
          f'({time.perf_counter() - started:.1f} s)')
    return 0 if not lines else 1


if __name__ == '__main__':
    sys.exit(main())
