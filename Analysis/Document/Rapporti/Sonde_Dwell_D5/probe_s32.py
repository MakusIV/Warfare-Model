"""Sonda S-3 (sola lettura): prova in memoria la geometria proposta per S32-DWELL (5 varianti x 4 semi).
La legge e' quella delle sonde S-1/S-2; il dwell si legge da un attributo di sonda dell'istanza (ZSU) o, per il
P-18, dal valore di fonte 6 s. Nulla e' scritto nel repository."""
from unittest.mock import patch

from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic.Contact_Scheduler import TIME_EPS, range_intervals
from Code.Dynamic_War_Manager.Source.Context import Air_Defense_Efficacy as ADE
from Code.Dynamic_War_Manager.Source.Command.Mission_Types import MissionRules, Target, TargetKind, TargetProvenance
from Code.Dynamic_War_Manager.Source.Logic.Fire_Control import make_registry_fire_control
from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F
from Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S10_S18 import BOTH_HOLD
from Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S19_Air_Defence import (
    DURATION, IFV_IDS, MAVERICK, OVERFLIGHT, VISUAL)

SWITCH = {'on': False}


def exposure(run, window, oid, tid, own, other):
    lo, lt = run.legs.get(oid), run.legs.get(tid)
    if lo and lt:
        tot = 0.0
        for s, e in range_intervals(lo, lt, own):
            if e < window.t_start - TIME_EPS or s > window.t_end + TIME_EPS:
                continue
            tot += max(0.0, min(e, window.t_end) - s)
        return tot
    if other is None or own >= other:
        return max(0.0, window.t_end - window.t_start)
    if window.t_mutual_start is not None and window.t_mutual_end is not None:
        return max(0.0, window.t_mutual_end - window.t_mutual_start)
    return 0.0


def _detect_direction(self, window, observer, target, own_range, other_range):
    if own_range is None or own_range <= 0:
        return
    if self._grounded_in(observer.id, window):
        return
    factor = 1.0
    if self.detection_factor is not None:
        factor = ER._check_factor(self.detection_factor(observer.asset, target.asset))
    dwell = exp = None
    if SWITCH['on']:
        dwell = getattr(observer.asset, '_probe_dwell', None)
        if dwell is None and getattr(observer.asset, '_model', None) == 'P-18-Terek':
            dwell = 6.0
        if dwell:
            exp = exposure(self, window, observer.id, target.id, own_range, other_range)
            factor = factor * min(1.0, exp / dwell)
    draw = self._draw()
    distance = max(float(window.distance_cpa), 0.0)
    probability = ER.detection_probability(distance, own_range, factor) if distance <= own_range else 0.0
    detected = draw < probability
    time = None
    if detected:
        radius = ER.detection_radius(draw, own_range, factor)
        time = self._detection_time(window, observer.id, target.id, own_range, other_range, radius)
        self._perceive(observer.force_id, target.id, time)
        ident = self.identified_by.setdefault(self.domain_of[observer.force_id], {})
        ident[target.id] = min(ident.get(target.id, time), time)
        if not self._grounded_in(target.id, window) \
                and ADE.rwr_perception(target.asset, observer.asset) == ADE.PERCEIVED_AT_DETECTION:
            self._perceive_rwr(target, observer, time)
        t_ready = time + self._profile(observer.id).total
        if t_ready <= window.t_end + TIME_EPS:
            self.candidates.setdefault(observer.id, []).append(
                ER._Candidate(t_ready=t_ready, target_id=target.id, t_end=window.t_end,
                              t_cpa=float(window.t_cpa), distance_cpa=distance))
    d = ER.Detection(observer_id=observer.id, target_id=target.id, sensor_range=float(own_range),
                     distance_cpa=distance, probability=probability, draw=draw, detected=detected, time=time)
    object.__setattr__(d, '_exp', exp)
    object.__setattr__(d, '_dwell', dwell)
    self.detections.append(d)


ER._EngagementRun._detect_direction = _detect_direction

SPEC = {'off': (None, False, False), 'long': (30.0, True, False), 'short': (600.0, True, False),
        'ewr_off': (None, False, True), 'ewr_on': (None, True, True)}
ZSU, EWR = 'Red-Line/ad0', 'Red-Line/ewr0'


def run(session_id, variant):
    dwell, switch, with_ewr = SPEC[variant]
    units = [F.Unit('vehicle', 'BMP-2', 3, origin=(0.0, 0.0), step=(0.0, 300.0), prefix='ifv', sensors=VISUAL),
             F.Unit('vehicle', 'ZSU-57-2', 1, origin=(1_000.0, -300.0), prefix='ad')]
    if with_ewr:
        units.append(F.Unit('vehicle', 'P-18-Terek', 1, origin=(30_000.0, 0.0), prefix='ewr'))
    red = F.build_force('Red-Line', 'Red', units)
    cas = F.build_force('Blue-CAS', 'Blue', [
        F.Unit('aircraft', 'A-10C Thunderbolt II', 4, origin=(-40_000.0, 0.0, 3_000.0),
               step=(0.0, 500.0), prefix='cas', loadout='Maverick/Gun CAS')], mil_category=F.AIR_UNIT)
    if dwell is not None:
        red.assets[ZSU]._probe_dwell = dwell
    target = Target(kind=TargetKind.GROUP, target_id='Red-Line', asset_ids=IFV_IDS,
                    provenance=TargetProvenance.OBSERVED, observed_at=0.0)
    missions = F.missions_for(cas, OVERFLIGHT, mission_type='CAS', target=target, weapons=(MAVERICK,),
                              rules=MissionRules(roe='only_designated'))
    captured = []
    original = ER.resolve_engagement

    def spy(*a, **k):
        r = original(*a, **k)
        captured.append(r)
        return r

    SWITCH['on'] = switch
    with patch.object(ER, 'resolve_engagement', side_effect=spy):
        outcome = F.run(session_id, [cas], [red], make_registry_fire_control(), duration=DURATION,
                        missions=missions, thresholds=BOTH_HOLD)
    SWITCH['on'] = False
    return outcome, [r for r in captured if r is not None]


res = {}
for k in range(4):
    sid = f'S32-DWELL-{k}'
    for v in SPEC:
        res[(k, v)] = run(sid, v)

def ammo(o):
    return [(e.asset_id, e.weapon, e.rounds, round(e.time, 6)) for e in o.ammunition_events]

def dets(results, obs, first_only=False):
    rs = results[:1] if first_only else results
    return [d for r in rs for d in r.detections if d.observer_id == obs]

for k in range(4):
    o_off, r_off = res[(k, 'off')]
    o_long, r_long = res[(k, 'long')]
    o_short, r_short = res[(k, 'short')]
    o_eoff, r_eoff = res[(k, 'ewr_off')]
    o_eon, r_eon = res[(k, 'ewr_on')]
    zsu_rounds_off = sum(e.rounds for e in o_off.ammunition_events if e.asset_id == ZSU)
    zsu_rounds_short = sum(e.rounds for e in o_short.ammunition_events if e.asset_id == ZSU)
    print(f'seed {k}: episodes off={len(r_off)} long={len(r_long)} short={len(r_short)}')
    print('  long==off ammo', ammo(o_long) == ammo(o_off), ' ewr_on==ewr_off ammo', ammo(o_eon) == ammo(o_eoff))
    print('  ZSU rounds off/short', zsu_rounds_off, zsu_rounds_short)
    dl = dets(r_long, ZSU)
    print('  long ZSU exposures', sorted(round(d._exp, 1) for d in dl if d._exp is not None))
    s_off = {(d.observer_id, d.target_id) for d in dets(r_off, ZSU, True) if d.detected}
    s_short = {(d.observer_id, d.target_id) for d in dets(r_short, ZSU, True) if d.detected}
    print('  first-episode ZSU detected off/short', len(s_off), len(s_short), 'subset', s_short <= s_off)
    print('  total ZSU detected off/short', sum(d.detected for d in dets(r_off, ZSU)),
          sum(d.detected for d in dets(r_short, ZSU)))
    ds = dets(r_short, ZSU)
    print('  short bound ok', all(d._exp is not None and d._exp < 600 and d.probability <= d._exp / 600 + 1e-12 for d in ds),
          'exposures', sorted(round(d._exp, 1) for d in ds))
    de = dets(r_eon, EWR)
    print('  ewr_on P-18 exposures min', min((d._exp for d in de), default=None), 'n', len(de),
          'prob equal', [d.probability for d in de] == [d.probability for d in dets(r_eoff, EWR)])
