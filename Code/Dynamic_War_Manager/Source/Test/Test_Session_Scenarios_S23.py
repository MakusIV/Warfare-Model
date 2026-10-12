"""Scenario S23 del motore di sessioni virtuali: attese, ETA bloccate e TOT per missione (F5 passi (c)-(d)).

Prosegue `Test_Session_Scenarios.py` (S1-S9), `Test_Session_Scenarios_S10_S18.py`, gli S19-S22 con la
stessa disciplina: si verifica un comportamento QUALITATIVO o STRUTTURALE, mai un numero calibrato.

Criterio "Fatto quando" della Fase 5 di `Analysis/Document/Piano_Implementazione_Missione.md`: *una CAP
in orbita ha finestre di contatto per tutta la durata dell'attesa*, piu' l'azione WAIT (sosta e
orbita), il TOT di ogni missione e le ETA effettive nell'esito (N2.b/N2.c, deviazione 13). V.
`Logic/Mission_Adapter`, "Attese, ETA bloccate e TOT": un'attesa e' un tratto FERMO nel punto (anche
l'orbita: approssimazione dichiarata, nessun circuito geometrico), le attese entrano nei tratti dati a
scheduler e risolutore, e il `MissionOutcome.actual_etas` riporta gli istanti d'arrivo ai punti dai
tratti, attese comprese. Le attese NON consumano carburante (consumo nel tempo: F6).

Ogni scenario ha una variante di CONTROLLO `waits_off` eseguita con `Mission_Adapter.F5_WAITS`
spento (comportamento precedente alla F5-C): la stessa missione dichiarata, ma nessuna attesa.

## S23-CAP: CAP in orbita (`TestS23CapOrbit`)

Red-CAP: 2 MiG-29S (loadout 'CAP', ruolo 'fighter', sensore 'air' dichiarato di `CAP_SENSOR_RANGE`)
in volo da x = -75 km verso il punto d'orbita O = (0, 0) a 250 m/s (arrivo a `ORBIT_ARRIVAL` = 300 s),
WAIT 'orbit' di `ORBIT_DURATION` = 1500 s, poi rientro verso ovest (x = -150 km, esce di scena).
Blue-Bomber: 2 F-16C che NON sparano (ruolo 'unarmed'), in volo da nord a sud lungo x = 0 a 250 m/s,
passano per O all'istante `CROSSING`. Varianti per seed:
  * 'during': passaggio a t = 1000 s, durante l'orbita: intercettati, e solo durante l'orbita;
  * 'after': passaggio a t = 2200 s, dopo la fine dell'orbita (la CAP e' a 100 km): nessun tiro;
  * 'no_wait': come 'during', ma la missione CAP senza WAIT (passa per O a 300 s e torna indietro):
    nessun contatto, nessun tiro;
  * 'waits_off': come 'during' con `F5_WAITS` spento: uguale a 'no_wait'.
Le finestre di contatto: un osservatore fermo sotto O (sonda dello scheduler, fuori dalla sessione)
ha con la CAP una finestra che copre TUTTA l'orbita.

## S23-HOLD: sosta a terra (`TestS23GroundHold`)

Red-Post: 3 BMP-2 fermi intorno a (0, 0) con sensore 'ground' dichiarato di 4,2 km (come S22).
Blue-Armor: un M1A2 che NON spara, da x = -12 km a W1 = (-4 km, 0) (arrivo a 800 s) e poi verso sud a
(-4 km, -12 km), a 10 m/s. Varianti:
  * 'hold': WAIT 'hold' di `HOLD_DURATION` = 600 s in W1 (riparte a 1400 s, esce dal sensore a ~1548 s,
    arrivo all'ultimo punto a 2600 s);
  * 'no_hold': stessa rotta senza attesa (nel sensore da 780 s a ~948 s);
  * 'waits_off': come 'hold' con `F5_WAITS` spento: uguale a 'no_hold'.
Il carro fermo nella sosta e' un bersaglio (colpi Red durante la sosta), poi riparte (ETA effettive).
Il tiro Red e' DICHIARATO senza effetto (precisione 0, `SUPPRESSIVE_SHOT`): si misura quando il carro
e' ingaggiato, e la distruzione non taglia la sosta.

## S23-TOT: TOT per missione nella stessa Operazione (`TestS23TotPerMission`)

Il TOT e' SPECIFICO DI OGNI MISSIONE, anche fra le missioni della stessa Operazione (decisione
dell'utente del 2026-10-12, che ha rimosso il TOT comune `Operation.tot`). Il caso dell'utente: una
Fighter Sweep sulla zona che anticipa l'arrivo dei bombardieri di un'altra missione sulla stessa zona.
Red-Depot: 3 depositi (`Structure` 'Oil_Tank') intorno a (0, 0), nessuna difesa. Blue-Sweep (2 F-16C
'CAP' a x = -60 km, ruolo 'unarmed': non spara, non ci sono aerei nemici) con una missione
'Fighter_Sweep', e Blue-Strike (2 F-16C 'Strike' a x = -120 km, ruolo 'strike' con lanci DICHIARATI
senza effetto (`MARKER_SHOT`) e sensore 'ground' dichiarato di 10 km) con una missione 'Strike':
entrambe rettilinee NAV -> ATTACK (x = -15 km) -> LAND (x = +40 km, esce di scena) a 250 m/s, nella
stessa Operazione 'Op-Strike' (senza TOT). TOT dello strike `STRIKE_TOT` = 600 s, dello sweep
`STRIKE_TOT - SWEEP_LEAD` = 480 s. Varianti:
  * 'own_tot': partenza a t = 0 per entrambe: ciascuna attende nel punto di partenza (in volo) quanto
    basta per essere sul proprio ATTACK al PROPRIO TOT (sweep 300 s, strike 180 s);
  * 'derived': nessuna partenza dichiarata: partenze derivate all'indietro dal proprio TOT (sweep a
    300 s, strike a 180 s), stessi arrivi;
  * 'waits_off': 'own_tot' con `F5_WAITS` spento: nessuna attesa, arrivi a 180 s e 420 s.

## ETA effettive (tutti gli scenari)

`MissionOutcome.actual_etas` = per punto il primo arrivo fra gli asset non ancora distrutti, dai tratti
(`Mission_Adapter.waypoint_times`, attese comprese), None oltre la fine della sessione.

Asserzioni: invarianti per replica (istanti dei colpi rispetto all'orbita/sosta, ETA esatte) e
frazioni aggregate con soglie DICHIARATE (stime di test, non tarate sul risultato; v. sotto).
"""

import dataclasses
import unittest
from unittest.mock import patch

from Code.Dynamic_War_Manager.Source.Command.Mission_Types import (
    ActionKind,
    Mission,
    MissionAction,
    MissionAsset,
    MissionWaypoint,
    Operation,
    StartMode,
    WaypointRole,
    route_waypoints,
)
from Code.Dynamic_War_Manager.Source.Logic import Contact_Scheduler as CS
from Code.Dynamic_War_Manager.Source.Logic import Mission_Adapter as MA
from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F

DURATION = 3_600.0
SEEDS_PER_SCENARIO = 8

# ── Costanti di S23-CAP [m, m/s, s], dichiarate di test ─────────────────────────
CAP = 'Red-CAP'
BOMBER = 'Blue-Bomber'
# Sensore 'air' dichiarato della CAP: valore DI TEST (non dal registro), scelto perche' la CAP veda
# i bombardieri solo vicino al punto d'orbita (nessun contatto prima dell'arrivo ne' dopo la partenza).
CAP_SENSOR_RANGE = 30_000.0
CAP_ALTITUDE = 6_000.0
BOMBER_ALTITUDE = 5_000.0
AIR_SPEED = 250.0              # sotto il massimo di MiG-29S e F-16C (regola A)
CAP_START_X = -75_000.0
CAP_EXIT_X = -150_000.0
ORBIT_ARRIVAL = -CAP_START_X / AIR_SPEED          # 300 s
ORBIT_DURATION = 1_500.0
ORBIT_END = ORBIT_ARRIVAL + ORBIT_DURATION        # 1800 s
BOMBER_START_Y = 150_000.0
CROSSING = {'during': 1_000.0, 'after': 2_200.0}  # istante di passaggio dei bombardieri per O
# Sonda delle finestre (fuori dalla sessione): osservatore fermo sotto il punto d'orbita.
PROBE_SENSOR_RANGE = 20_000.0

# ── Costanti di S23-HOLD, dichiarate di test (come S22) ─────────────────────────
POST = 'Red-Post'
ARMOR = 'Blue-Armor'
RED_SENSOR_RANGE = 4_200.0
ARMOR_SPEED = 10.0
HOLD_X = -4_000.0
ARMOR_START_X = -12_000.0
ARMOR_END_Y = -12_000.0
HOLD_ARRIVAL = (HOLD_X - ARMOR_START_X) / ARMOR_SPEED     # 800 s
HOLD_DURATION = 600.0
HOLD_END = HOLD_ARRIVAL + HOLD_DURATION                   # 1400 s
ARMOR_ARRIVAL = HOLD_END + (-ARMOR_END_Y) / ARMOR_SPEED   # 2600 s
# Uscita dal sensore Red [s] nelle due geometrie: il BMP piu' a sud e' in y = -200 m, il carro ne
# esce quando |y + 200| supera sqrt(4200^2 - 4000^2) ~ 1281 m.
RED_PLATOON_HALF_SPAN = 200.0
_LATERAL = (RED_SENSOR_RANGE ** 2 - HOLD_X ** 2) ** 0.5 + RED_PLATOON_HALF_SPAN
LEAVE_AFTER_HOLD = HOLD_END + _LATERAL / ARMOR_SPEED          # ~1548 s
LEAVE_WITHOUT_HOLD = HOLD_ARRIVAL + _LATERAL / ARMOR_SPEED    # ~948 s
CONTACT_START = HOLD_ARRIVAL - (RED_SENSOR_RANGE - (-HOLD_X)) / ARMOR_SPEED   # 780 s
# Tiro Red DICHIARATO DI TEST: il 'direct_fire' di riferimento con precisione 0 (nessun colpo a
# segno), per misurare l'ingaggio senza che la distruzione del carro tagli la sosta.
SUPPRESSIVE_SHOT = dataclasses.replace(F.SHOTS['direct_fire'], accuracy=0.0, weapon='test:suppressive')

# ── Costanti di S23-TOT, dichiarate di test ─────────────────────────────────────
DEPOT = 'Red-Depot'
SWEEP, STRIKE = 'Blue-Sweep', 'Blue-Strike'
MISSION_TYPE = {SWEEP: 'Fighter_Sweep', STRIKE: 'Strike'}
LOADOUT = {SWEEP: 'CAP', STRIKE: 'Strike'}
OPERATION = 'Op-Strike'
STRIKE_TOT = 600.0
# Anticipo del TOT dello sweep su quello dello strike [s]: STIMA DI TEST (ordine di grandezza di
# "qualche minuto" del caso dell'utente), non un dato dottrinale tarato.
SWEEP_LEAD = 120.0
TOTS = {SWEEP: STRIKE_TOT - SWEEP_LEAD, STRIKE: STRIKE_TOT}
STRIKE_START_X = {SWEEP: -60_000.0, STRIKE: -120_000.0}
STRIKE_Y = {SWEEP: 0.0, STRIKE: 2_000.0}
ATTACK_X = -15_000.0
EXIT_X = 40_000.0
STRIKE_ALTITUDE = 5_000.0
# Sensore 'ground' dichiarato degli F-16C dello strike: valore DI TEST (non dal registro), sotto la
# distanza fra il punto ATTACK e i depositi (15 km), cosi' che lo strike lanci solo dopo l'ATTACK e
# mai dal punto d'attesa (con il registro gli F-16C vedevano i depositi gia' da 60 km).
STRIKE_SENSOR_RANGE = 10_000.0
# Lancio DICHIARATO DI TEST: l''agm' di riferimento con precisione 0 (nessun colpo a segno).
MARKER_SHOT = dataclasses.replace(F.SHOTS['agm'], accuracy=0.0, weapon='test:marker')

# Soglie delle frazioni aggregate sui seed: DICHIARATE di test, non tarate sul risultato.
#   * S23-CAP 'during', repliche in cui la CAP spara: il rilevamento e' una estrazione per finestra e
#     osservatore (due MiG su due bombardieri), attesa a priori ben sopra 0,5; 0,5 = "il tiro e' la
#     regola, non l'eccezione".
#   * S23-HOLD 'hold', repliche in cui Red spara DURANTE la sosta: stessa stima di S22 (tre
#     osservatori, Pd ~0,59 ciascuno, attesa ~0,93), soglia 0,5.
#   * S23-TOT, repliche in cui lo strike lancia: nessuna difesa, depositi entro il sensore dopo
#     l'ATTACK per ogni replica; 0,5 come sopra (il lancio e' la regola).
MIN_FIRING_FRACTION = 0.5


def _seeds(prefix: str, count: int = SEEDS_PER_SCENARIO):
    return [f'{prefix}-{index}' for index in range(count)]


def _shots_by(outcome, prefix: str):
    return [event for event in outcome.ammunition_events if event.asset_id.startswith(prefix + '/')]


def _wait(mode: str, duration: float) -> MissionAction:
    return MissionAction(kind=ActionKind.WAIT, name=f'Wait_{mode}', wait_mode=mode, wait_duration_s=duration)


def _replan(mission: Mission, roles=None, actions=None, **overrides) -> Mission:
    """Copia della missione con ruoli (lista) e azioni (`{indice: [MissionAction]}`) dei punti dati."""
    waypoints = []

    for index, mw in enumerate(mission.waypoints):
        role = roles[index] if roles is not None else mw.role
        waypoints.append(dataclasses.replace(mw, role=role, actions=tuple((actions or {}).get(index, ()))))

    return dataclasses.replace(mission, waypoints=tuple(waypoints), **overrides)


def _expected_etas(mission: Mission, session_end: float = DURATION):
    """ETA effettive attese dai TRATTI (la regola di `Session_Simulator._mission_outcome`, senza
    distruzioni): per punto il primo arrivo fra gli asset, None oltre la fine della sessione."""
    times = [MA.waypoint_times(movement) for movement in MA.mission_movements(mission, 0.0, ())]
    count = max((len(t) for t in times), default=0)
    etas = []

    for index in range(count):
        reached = [t[index] for t in times if index < len(t) and t[index] <= session_end + CS.TIME_EPS]
        etas.append(min(reached) if reached else None)

    return tuple(etas)


def _waits(enabled: bool):
    """Contesto: `F5_WAITS` com'e' (True) o spento (variante di controllo 'waits_off')."""
    return patch.object(MA, 'F5_WAITS', MA.F5_WAITS and enabled)


class _EtaChecks:
    """Mixin (NON un TestCase): `runs` = {variante: [(scenario, outcome, {mission_id: ETA attese})]}."""

    runs = {}

    def _all(self):
        return [entry for entries in self.runs.values() for entry in entries]

    def test_actual_etas_are_the_leg_instants(self):
        """(d) ETA effettive dell'esito = istanti d'arrivo dai tratti (attese comprese), per ogni
        missione senza asset distrutti; con distruzioni, ogni ETA presente coincide comunque con quella
        dei tratti (il primo arrivo fra gli asset ancora vivi non precede quello di tutti)."""
        for scenario, outcome, expected in self._all():
            destroyed = {e.target_id for e in outcome.damage_events if e.destroyed}

            for mission in scenario.missions:
                etas = expected[mission.mission_id]
                actual = outcome.mission_outcomes[mission.mission_id].actual_etas
                self.assertEqual(len(actual), len(etas), outcome.session_id)

                for got, want in zip(actual, etas):
                    if got is not None:
                        self.assertGreaterEqual(got, want - CS.TIME_EPS, (outcome.session_id, mission.mission_id))

                if not destroyed & {a.asset_id for a in mission.assets}:
                    self.assertEqual(actual, etas, (outcome.session_id, mission.mission_id))


# ── S23-CAP: CAP in orbita ────────────────────────────────────────────────────

def _cap_mission(cap, orbit: bool) -> Mission:
    """CAP da x = -75 km a O = (0, 0) (WAIT 'orbit' se `orbit`) e rientro a x = -150 km."""
    lead, wing = sorted(cap.assets)
    route = F.straight_route([(CAP_START_X, 0.0), (0.0, 0.0), (CAP_EXIT_X, 0.0)], AIR_SPEED, 'cap-route',
                             z=CAP_ALTITUDE)
    roles = [WaypointRole.NAV, WaypointRole.HOLD, WaypointRole.LAND]
    actions = {1: [_wait('orbit', ORBIT_DURATION)]} if orbit else {}
    waypoints = tuple(MissionWaypoint(wp, role, actions=tuple(actions.get(index, ())))
                      for index, (wp, role) in enumerate(zip(route_waypoints(route), roles)))
    # Il gregario a 1 km a sinistra del capo nel primo tratto (la sua posizione iniziale).
    members = (MissionAsset(lead, 'lead', loadout='CAP'), MissionAsset(wing, 'wingman', right_m=-1_000.0, loadout='CAP'))
    return Mission(mission_id=f'{CAP}:CAP', block_id=CAP, domain='air', mission_type='CAP', assets=members,
                   target=F.zone_target((0.0, 0.0), CAP_SENSOR_RANGE), route=route, waypoints=waypoints,
                   start_time=0.0, start_mode=StartMode.AIR)


def _cap_scenario(variant: str) -> F.Scenario:
    cap = F.build_force(CAP, 'Red', [F.Unit('aircraft', 'MiG-29S', 2, origin=(CAP_START_X, 0.0, CAP_ALTITUDE),
                                            step=(0.0, 1_000.0), prefix='cap', loadout='CAP',
                                            sensors={'air': CAP_SENSOR_RANGE})], mil_category=F.AIR_UNIT)
    bomber = F.build_force(BOMBER, 'Blue', [F.Unit('aircraft', 'F-16C Block 52d', 2,
                                                   origin=(0.0, BOMBER_START_Y, BOMBER_ALTITUDE), step=(1_000.0, 0.0),
                                                   prefix='bmb', loadout='Strike')], mil_category=F.AIR_UNIT)
    crossing = CROSSING['after' if variant == 'after' else 'during']
    bomber_mission, = F.missions_for(bomber, [(0.0, -BOMBER_START_Y)], mission_type='Strike',
                                     target=F.zone_target((0.0, -BOMBER_START_Y), 10_000.0), speed=AIR_SPEED)
    bomber_mission = dataclasses.replace(bomber_mission, start_time=crossing - BOMBER_START_Y / AIR_SPEED)
    roles = {**{asset_id: 'fighter' for asset_id in cap.assets}, **{asset_id: 'unarmed' for asset_id in bomber.assets}}
    return F.Scenario(forces_a=[bomber], forces_b=[cap],
                      missions=[bomber_mission, _cap_mission(cap, orbit=variant != 'no_wait')],
                      fire_control=F.make_fire_control(roles=roles), duration=DURATION, roles=roles)


def _run_variant(cls, builder, variant: str, session_id: str):
    """Esegue la variante (con `F5_WAITS` spento se 'waits_off') e registra le ETA attese dai tratti."""
    scenario = builder(variant)

    with _waits(variant != 'waits_off'):
        outcome = scenario.run(session_id, **cls.run_kwargs(scenario))
        expected = {m.mission_id: _expected_etas(m) for m in scenario.missions}

    return scenario, outcome, expected


class TestS23CapOrbit(_EtaChecks, F.LoggerSilencer, unittest.TestCase):
    """S23-CAP: una CAP in orbita intercetta durante l'orbita e solo allora (F5-C, N2.c)."""

    SEEDS = _seeds('S23-CAP')
    VARIANTS = ('during', 'after', 'no_wait', 'waits_off')

    @staticmethod
    def run_kwargs(scenario):
        return {}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                cls.runs[variant].append(_run_variant(cls, _cap_scenario, variant, session_id))

    def test_bombers_never_fire(self):
        for _, outcome, _ in self._all():
            self.assertEqual(_shots_by(outcome, BOMBER), [], outcome.session_id)

    def test_cap_fires_only_during_the_orbit(self):
        """'during': ogni lancio della CAP e' dentro l'orbita (e dentro il passaggio dei bombardieri)."""
        for _, outcome, _ in self.runs['during']:
            for event in _shots_by(outcome, CAP):
                self.assertTrue(ORBIT_ARRIVAL <= event.time <= ORBIT_END, (outcome.session_id, event.time))

    def test_cap_intercepts_in_most_replicas(self):
        pairs = self.runs['during']
        firing = sum(1 for _, outcome, _ in pairs if _shots_by(outcome, CAP))
        self.assertGreaterEqual(firing / len(pairs), MIN_FIRING_FRACTION, firing)

    def test_no_interception_after_the_orbit_or_without_waiting(self):
        """'after' (passaggio dopo l'orbita), 'no_wait' e 'waits_off' (nessuna attesa): nessun tiro,
        nessun danno."""
        for variant in ('after', 'no_wait', 'waits_off'):
            for _, outcome, _ in self.runs[variant]:
                self.assertEqual(_shots_by(outcome, CAP), [], (variant, outcome.session_id))
                self.assertEqual(outcome.damage_events, (), (variant, outcome.session_id))

    def test_orbit_etas(self):
        """ETA effettive della CAP: arrivo in O a 300 s, all'ultimo punto dopo l'orbita (2400 s); senza
        attesa (o con le attese spente) a 900 s."""
        mission_id = f'{CAP}:CAP'
        exit_leg = (-CAP_EXIT_X) / AIR_SPEED

        for variant, last in (('during', ORBIT_END + exit_leg), ('no_wait', ORBIT_ARRIVAL + exit_leg),
                              ('waits_off', ORBIT_ARRIVAL + exit_leg)):
            for _, outcome, _ in self.runs[variant]:
                etas = outcome.mission_outcomes[mission_id].actual_etas
                self.assertAlmostEqual(etas[1], ORBIT_ARRIVAL, delta=1e-6)
                self.assertAlmostEqual(etas[2], last, delta=1e-6)

    def test_contact_windows_cover_the_whole_orbit(self):
        """Il criterio della Fase 5: con i tratti della sessione (`Mission_Adapter.movement_legs`) un
        osservatore fermo sotto il punto d'orbita ha con ogni MiG una finestra che copre TUTTA
        l'orbita; senza attesa la finestra dura solo il passaggio (sonda dello scheduler, nessuna
        sessione eseguita)."""
        for orbit, covers in ((True, True), (False, False)):
            cap = _cap_scenario('during').force(CAP)
            mission = _cap_mission(cap, orbit=orbit)
            probe = F.build_force('Blue-Probe', 'Blue', [F.Unit('vehicle', 'M1A2-Abrams', 1, origin=(0.0, 0.0),
                                                                prefix='obs', sensors={'air': PROBE_SENSOR_RANGE})])
            legs = {m.asset_id: MA.movement_legs(m, 0.0, DURATION) for m in MA.mission_movements(mission)}
            windows = CS.schedule_contacts([probe], [cap], DURATION, legs=legs)

            for asset_id in cap.assets:
                own = [w for w in windows if asset_id in (w.asset_a_id, w.asset_b_id)]
                self.assertTrue(own, asset_id)
                spans = any(w.t_start <= ORBIT_ARRIVAL and w.t_end >= ORBIT_END for w in own)
                self.assertEqual(spans, covers, (orbit, asset_id, [(w.t_start, w.t_end) for w in own]))

    def test_the_orbit_does_not_consume_fuel(self):
        """Limite noto (F6): l'orbita e' un tratto fermo, il consumo e' in distanza: stessa distanza
        con e senza attesa."""
        for (_, with_orbit, _), (_, without, _) in zip(self.runs['during'], self.runs['no_wait']):
            distance = {e.asset_id: e.distance for e in with_orbit.fuel_events if e.asset_id.startswith(CAP)}
            reference = {e.asset_id: e.distance for e in without.fuel_events if e.asset_id.startswith(CAP)}
            self.assertEqual(set(distance), set(reference))

            for asset_id, value in distance.items():
                self.assertAlmostEqual(value, reference[asset_id], delta=1e-6)


# ── S23-HOLD: sosta a terra ───────────────────────────────────────────────────

def _hold_scenario(variant: str) -> F.Scenario:
    post = F.build_force(POST, 'Red', [F.Unit('vehicle', 'BMP-2', 3, origin=(0.0, -200.0), step=(0.0, 200.0),
                                              prefix='bmp', sensors={'ground': RED_SENSOR_RANGE})])
    armor = F.build_force(ARMOR, 'Blue', [F.Unit('vehicle', 'M1A2-Abrams', 1, origin=(ARMOR_START_X, 0.0),
                                                 prefix='tank')])
    mission, = F.missions_for(armor, [(HOLD_X, 0.0), (HOLD_X, ARMOR_END_Y)], mission_type='Attack',
                              target=F.group_target(POST), speed=ARMOR_SPEED)
    actions = {1: [_wait('hold', HOLD_DURATION)]} if variant != 'no_hold' else {}
    roles = {asset_id: 'unarmed' for asset_id in armor.assets}
    # Fuoco Red SENZA effetto (precisione 0): si misura se e quando il carro e' ingaggiato, non se e'
    # distrutto, cosi' sopravvive sempre e la ripartenza dopo la sosta compare nelle ETA effettive.
    overrides = {asset_id: {'ground': SUPPRESSIVE_SHOT} for asset_id in post.assets}
    return F.Scenario(forces_a=[armor], forces_b=[post], missions=[_replan(mission, actions=actions)],
                      fire_control=F.make_fire_control(roles=roles, overrides=overrides), duration=DURATION,
                      roles=roles)


class TestS23GroundHold(_EtaChecks, F.LoggerSilencer, unittest.TestCase):
    """S23-HOLD: un carro in sosta (WAIT 'hold') e' fermo e ingaggiabile, poi riparte (F5-C)."""

    SEEDS = _seeds('S23-HOLD')
    VARIANTS = ('hold', 'no_hold', 'waits_off')

    run_kwargs = staticmethod(TestS23CapOrbit.run_kwargs)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                cls.runs[variant].append(_run_variant(cls, _hold_scenario, variant, session_id))

    def test_blue_never_fires(self):
        for _, outcome, _ in self._all():
            self.assertEqual(_shots_by(outcome, ARMOR), [], outcome.session_id)

    def test_red_fires_only_while_the_tank_is_in_range(self):
        """Ogni colpo Red parte mentre il carro e' nel sensore: fino a ~1548 s con la sosta, fino a
        ~948 s senza (o con le attese spente)."""
        limits = {'hold': LEAVE_AFTER_HOLD, 'no_hold': LEAVE_WITHOUT_HOLD, 'waits_off': LEAVE_WITHOUT_HOLD}

        for variant, entries in self.runs.items():
            for _, outcome, _ in entries:
                for event in _shots_by(outcome, POST):
                    self.assertTrue(CONTACT_START <= event.time <= limits[variant] + 1e-6,
                                    (variant, outcome.session_id, event.time))

    def test_the_halted_tank_is_engaged_during_the_hold(self):
        """Il cuore della sosta: nella maggior parte delle repliche Red spara anche DOPO l'istante in
        cui, senza sosta, il carro sarebbe gia' uscito dal sensore."""
        entries = self.runs['hold']
        late = sum(1 for _, outcome, _ in entries
                   if any(e.time > LEAVE_WITHOUT_HOLD for e in _shots_by(outcome, POST)))
        self.assertGreaterEqual(late / len(entries), MIN_FIRING_FRACTION, late)

    def test_the_tank_leaves_after_the_hold(self):
        """ETA effettive: arrivo in W1 a 800 s, all'ultimo punto a 2600 s (sosta compresa) se il carro
        sopravvive; senza sosta a 2000 s."""
        for variant, last in (('hold', ARMOR_ARRIVAL), ('no_hold', ARMOR_ARRIVAL - HOLD_DURATION),
                              ('waits_off', ARMOR_ARRIVAL - HOLD_DURATION)):
            for _, outcome, _ in self.runs[variant]:
                etas = outcome.mission_outcomes[f'{ARMOR}:Attack'].actual_etas

                if etas[2] is not None:
                    self.assertAlmostEqual(etas[2], last, delta=1e-6)

                if etas[1] is not None:
                    self.assertAlmostEqual(etas[1], HOLD_ARRIVAL, delta=1e-6)


# ── S23-TOT: TOT per missione nella stessa Operazione ─────────────────────────

def _mission_id(force_id: str) -> str:
    return f'{force_id}:{MISSION_TYPE[force_id]}'


def _tot_mission(force, variant: str) -> Mission:
    """NAV -> ATTACK -> LAND con il TOT della forza; partenza a 0, o derivata ('derived')."""
    target = F.group_target(DEPOT) if force.id == STRIKE else F.zone_target((0.0, 0.0), -ATTACK_X)
    mission, = F.missions_for(force, [(ATTACK_X, STRIKE_Y[force.id]), (EXIT_X, STRIKE_Y[force.id])],
                              mission_type=MISSION_TYPE[force.id], target=target, speed=AIR_SPEED)
    roles = [WaypointRole.NAV, WaypointRole.ATTACK, WaypointRole.LAND]
    timing = dict(start_time=None) if variant == 'derived' else {}
    return _replan(mission, roles=roles, operation_id=OPERATION, tot=TOTS[force.id], **timing)


def _tot_scenario(variant: str) -> F.Scenario:
    depot = F.make_force(DEPOT, 'Red')
    F.add_assets(depot, [F.make_structure(depot, f'{DEPOT}/tank{index}', (0.0, 400.0 * (index - 1)), category='Farp',
                                          asset_type='Oil_Tank')
                         for index in range(3)])
    sensors = {SWEEP: None, STRIKE: {'ground': STRIKE_SENSOR_RANGE}}
    blue = [F.build_force(force_id, 'Blue', [F.Unit('aircraft', 'F-16C Block 52d', 2,
                                                    origin=(STRIKE_START_X[force_id], STRIKE_Y[force_id], STRIKE_ALTITUDE),
                                                    step=(0.0, 500.0), prefix='str', loadout=LOADOUT[force_id],
                                                    sensors=sensors[force_id])],
                          mil_category=F.AIR_UNIT)
            for force_id in (SWEEP, STRIKE)]
    roles = {asset_id: ('strike' if force.id == STRIKE else 'unarmed') for force in blue for asset_id in force.assets}
    # Lanci dello strike SENZA effetto (precisione 0): si misura QUANDO lo strike arriva sui depositi.
    overrides = {asset_id: {'structure': MARKER_SHOT} for asset_id in blue[1].assets}
    return F.Scenario(forces_a=blue, forces_b=[depot], missions=[_tot_mission(f, variant) for f in blue],
                      fire_control=F.make_fire_control(roles=roles, overrides=overrides), duration=DURATION,
                      roles=roles)


def _operation():
    """L'Operazione delle due missioni: scopo e appartenenza, NESSUN TOT comune."""
    return (Operation(OPERATION, 'sweep and strike', (_mission_id(SWEEP), _mission_id(STRIKE))),)


def _travel(force_id: str) -> float:
    return (ATTACK_X - STRIKE_START_X[force_id]) / AIR_SPEED


class TestS23TotPerMission(_EtaChecks, F.LoggerSilencer, unittest.TestCase):
    """S23-TOT: due missioni della stessa Operazione raggiungono la zona ciascuna al PROPRIO TOT, lo
    sweep `SWEEP_LEAD` prima dello strike (F5-C, TOT per missione dal 2026-10-12)."""

    SEEDS = _seeds('S23-TOT')
    VARIANTS = ('own_tot', 'derived', 'waits_off')

    @staticmethod
    def run_kwargs(scenario):
        return {'order_kwargs': {'operations': _operation()}}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                cls.runs[variant].append(_run_variant(cls, _tot_scenario, variant, session_id))

    def _attack_eta(self, outcome, force_id):
        return outcome.mission_outcomes[_mission_id(force_id)].actual_etas[1]

    def test_each_mission_reaches_its_own_tot(self):
        """(c) Le ETA effettive dei due ATTACK coincidono ciascuna con il PROPRIO TOT (partenza comune
        o derivata); con le attese spente sono le percorrenze."""
        for variant in ('own_tot', 'derived'):
            for _, outcome, _ in self.runs[variant]:
                for force_id in (SWEEP, STRIKE):
                    self.assertAlmostEqual(self._attack_eta(outcome, force_id), TOTS[force_id], delta=1e-6,
                                           msg=(variant, outcome.session_id, force_id))

        for _, outcome, _ in self.runs['waits_off']:
            for force_id in (SWEEP, STRIKE):
                self.assertAlmostEqual(self._attack_eta(outcome, force_id), _travel(force_id), delta=1e-6)

    def test_the_sweep_precedes_the_strike_by_the_declared_lead(self):
        """Lo sweep e' sulla zona esattamente `SWEEP_LEAD` prima dello strike; con le attese spente lo
        scarto e' la differenza di percorrenza (240 s), non quello pianificato."""
        for variant, lead in (('own_tot', SWEEP_LEAD), ('derived', SWEEP_LEAD),
                              ('waits_off', _travel(STRIKE) - _travel(SWEEP))):
            for _, outcome, _ in self.runs[variant]:
                self.assertAlmostEqual(self._attack_eta(outcome, STRIKE) - self._attack_eta(outcome, SWEEP), lead,
                                       delta=1e-6, msg=(variant, outcome.session_id))

    def test_departures(self):
        """'own_tot' e 'waits_off': partenza a 0 per entrambe (ETA del punto 0 = 0); 'derived':
        partenze derivate all'indietro dal proprio TOT (TOT - percorrenza: 300 s e 180 s)."""
        derived = {force_id: TOTS[force_id] - _travel(force_id) for force_id in (SWEEP, STRIKE)}

        for variant, starts in (('own_tot', {SWEEP: 0.0, STRIKE: 0.0}), ('waits_off', {SWEEP: 0.0, STRIKE: 0.0}),
                                ('derived', derived)):
            for _, outcome, _ in self.runs[variant]:
                for force_id, start in starts.items():
                    self.assertAlmostEqual(outcome.mission_outcomes[_mission_id(force_id)].actual_etas[0], start,
                                           delta=1e-6, msg=(variant, force_id))

    def test_the_strike_fires_only_after_its_own_tot(self):
        """Lo sweep non lancia mai; ogni lancio dello strike e' dopo il suo ATTACK (sensore dichiarato
        sotto la distanza ATTACK-depositi), quindi dopo il TOT dello strike e `SWEEP_LEAD` dopo
        l'arrivo dello sweep; lo strike lancia nella maggior parte delle repliche (soglia dichiarata)."""
        for variant, entries in self.runs.items():
            firing = 0

            for _, outcome, _ in entries:
                self.assertEqual(_shots_by(outcome, SWEEP), [], (variant, outcome.session_id))
                shots = _shots_by(outcome, STRIKE)
                firing += bool(shots)

                for event in shots:
                    self.assertGreaterEqual(event.time, self._attack_eta(outcome, STRIKE) - 1e-6,
                                            (variant, outcome.session_id, event.time))

            self.assertGreaterEqual(firing / len(entries), MIN_FIRING_FRACTION, (variant, firing))


if __name__ == '__main__':
    unittest.main()
