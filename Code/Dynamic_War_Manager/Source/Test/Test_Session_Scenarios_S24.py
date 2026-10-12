"""Scenario S24 del motore di sessioni virtuali: il carburante vincola movimento e contatti (F6-A).

Prosegue `Test_Session_Scenarios.py` (S1-S9), `Test_Session_Scenarios_S10_S18.py`, gli S19-S23 con la
stessa disciplina: si verifica un comportamento QUALITATIVO o STRUTTURALE, mai un numero calibrato.

Criterio "Fatto quando" della Fase 6 di `Analysis/Document/Piano_Implementazione_Missione.md`:
*l'esperimento E5 (carro a secco) non ingaggia piu' oltre il punto di esaurimento*. Decisioni
dell'utente del 2026-10-12 (deviazione 14 del piano, F6-A), v. `Logic/Session_Simulator`,
"Carburante", e `Logic/Fuel_Model`, "Consumo per tratto e nel tempo":
  * un `FuelEvent` per TRATTO; le attese e le orbite consumano NEL TEMPO alla crociera;
  * l'esaurimento e' calcolato A MONTE e i tratti oltre il punto di esaurimento non esistono per
    scheduler e risolutore;
  * terra/mare a secco: fermi nel punto, presenti e bersagli fino a fine sessione (motivo
    FUEL_EXHAUSTED, missione ABORTED per carburante);
  * aereo a secco in volo: planata sulla base del proprio lato piu' vicina entro quota x
    `Fuel_Model.GLIDE_RATIO` (a terra sulla base, ABORTED), altrimenti perso (DESTROYED, motivo
    FUEL_EXHAUSTED).
Ogni scenario ha una variante di CONTROLLO con l'interruttore spento (`Session_Simulator.
F6_FUEL_CONSTRAINT` o `F6_FUEL_PER_LEG`): torna il comportamento di prima.

## S24-E5: carro a secco (`TestS24DryTank`)

Esperimento E5 dell'analisi del 26/09 (`Analisi_Modello_Missione_Sessione.md` §3): un M1A2 con
`fuel = DRY_FUEL` = 0,002 del pieno (autonomia del registro 426 km: ~852 m) su una rotta di 7 km a
10 m/s; si esaurisce a `EXHAUSTION_TIME` = 85,2 s. Red-Post: 3 BMP-2 fermi intorno a (0, 0) con
sensore 'ground' dichiarato di 4,2 km (come S22/S23), tiro DICHIARATO senza effetto (precisione 0) per
misurare QUANDO e DOVE il carro e' ingaggiato senza che la distruzione lo tolga di scena. Il carro non
spara (ruolo 'unarmed'). Varianti per seed:
  * 'far': rotta lungo x da -7,5 km a -0,5 km: il carro si ferma a x = -6,65 km, fuori dal sensore
    Red: NESSUN colpo (prima della F6-A Red sparava al carro che "secondo il carburante" era fermo);
  * 'far_off': come 'far' con `F6_FUEL_CONSTRAINT` spento: il carro prosegue ed e' ingaggiato oltre il
    punto di esaurimento (il comportamento di prima, E5);
  * 'near': rotta lungo y da (-3 km, -3,5 km) a (-3 km, +3,5 km): il carro si ferma a y = -2,65 km,
    ~3,9 km dal BMP piu' vicino, e ci resta fino a fine sessione: Red spara anche dopo l'istante
    `NEAR_LEAVE` in cui, senza vincolo, il carro sarebbe gia' uscito dal sensore;
  * 'near_off': come 'near' con il vincolo spento: nessun colpo dopo `NEAR_LEAVE`.

## S24-GLIDE: aereo a secco in volo (`TestS24DryAircraft`)

Blue-Flight: un F-16C 'Strike' (ruolo 'unarmed') a 5000 m da x = -100 km verso x = +100 km a 250 m/s,
con carburante per 50 km (`AIR_FUEL_RANGE`): si esaurisce a 200 s in (-50 km, 0, 5000 m); raggio di
planata 5000 x 10 = 50 km. Blue-Base / Red-Base: base aerea (Military 'Airbase') con un deposito
(`Structure` 'Oil_Tank'). Red-Strike: 2 F-16C 'Strike' (ruolo 'strike', lanci DICHIARATI senza effetto
contro gli aerei a terra, nessun tiro contro il deposito) che sorvolano il punto della base da sud a
nord, sopra la base a ~840 s (dopo l'atterraggio in planata). Varianti per seed:
  * 'glide': base Blue a (-50 km, +20 km), 20 km dal punto di esaurimento: planata e atterraggio
    (~277 s), a terra sulla base, bersaglio dello strike Red; esito ABORTED per carburante;
  * 'no_base': base Blue a (-50 km, +60 km), oltre il raggio di planata: aereo perso (DESTROYED,
    motivo FUEL_EXHAUSTED), nessun colpo Red;
  * 'enemy_base': base RED a (-50 km, +20 km): non e' una base idonea (solo il proprio lato): perso;
  * 'off': come 'glide' con il vincolo spento: l'aereo prosegue a secco fino a x = +100 km ed esce di
    scena (FuelEvent esaurito come prima), nessun colpo Red.

## S24-ORBIT: esaurimento durante l'orbita (`TestS24OrbitExhaustion`)

Red-CAP: un MiG-29S 'CAP' (ruolo 'fighter', sensore 'air' dichiarato di 30 km, come S23) da x = -75 km
a O = (0, 0) a 250 m/s (arrivo a 300 s), WAIT 'orbit' di 1500 s, poi rientro a x = -150 km. L'orbita
consuma alla crociera del MiG (`Fuel_Model.cruise_speed`, ~255,6 m/s). Blue-Bomber: 2 F-16C che NON
sparano passano per O a `LATE_CROSSING` = 1400 s, durante l'orbita pianificata. Varianti per seed:
  * 'dry': carburante per l'avvicinamento e META' orbita: si esaurisce a 1050 s in O (6000 m, nessuna
    base): perso a 1050 s, NESSUN tiro sui bombardieri; due FuelEvent (avvicinamento, orbita esaurita);
  * 'full': pieno: tre FuelEvent per tratto (avvicinamento, orbita ferma alla crociera, rientro) e la
    CAP spara sui bombardieri nella maggior parte delle repliche;
  * 'per_leg_off': 'dry' con `F6_FUEL_PER_LEG` spento: l'orbita non consuma (come la F5-C), nessun
    esaurimento, un solo FuelEvent per asset, la CAP spara come in 'full'.

Asserzioni: invarianti per replica (istanti, punti, esiti, eventi) e frazioni aggregate con soglie
DICHIARATE (stime di test, non tarate sul risultato; v. sotto).
"""

import dataclasses
import math
import unittest
from unittest.mock import patch

from Code.Dynamic_War_Manager.Source.Command.Mission_Types import (
    AbortReason,
    ActionKind,
    AssetEndReason,
    AssetState,
    Mission,
    MissionAction,
    MissionAsset,
    MissionStatus,
    MissionWaypoint,
    StartMode,
    WaypointRole,
    route_waypoints,
)
from Code.Dynamic_War_Manager.Source.Logic import Contact_Scheduler as CS
from Code.Dynamic_War_Manager.Source.Logic import Fuel_Model as FM
from Code.Dynamic_War_Manager.Source.Logic import Mission_Adapter as MA
from Code.Dynamic_War_Manager.Source.Logic import Session_Simulator as SS
from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F

DURATION = 3_600.0
SEEDS_PER_SCENARIO = 8

# ── Costanti di S24-E5 [m, m/s, s], dichiarate di test (come S22/S23) ──────────
POST = 'Red-Post'
ARMOR = 'Blue-Armor'
RED_SENSOR_RANGE = 4_200.0
ARMOR_SPEED = 10.0
# Carburante del carro: il valore dell'esperimento E5 (frazione del pieno), non un dato.
DRY_FUEL = 0.002
ROUTE_LENGTH = 7_000.0
FAR_START, FAR_END = (-7_500.0, 0.0), (-500.0, 0.0)
NEAR_START, NEAR_END = (-3_000.0, -3_500.0), (-3_000.0, 3_500.0)
RED_PLATOON_HALF_SPAN = 200.0
# Istante [s] in cui il carro 'near' SENZA vincolo esce dal sensore del BMP piu' a nord (0, 200):
# y = 200 + sqrt(4200^2 - 3000^2) ~ 3139 m, cioe' (3139 + 3500) / 10 ~ 664 s.
NEAR_LEAVE = (RED_PLATOON_HALF_SPAN + math.sqrt(RED_SENSOR_RANGE ** 2 - NEAR_START[0] ** 2) - NEAR_START[1]) / ARMOR_SPEED
SUPPRESSIVE_SHOT = dataclasses.replace(F.SHOTS['direct_fire'], accuracy=0.0, weapon='test:suppressive')

# ── Costanti di S24-GLIDE, dichiarate di test ───────────────────────────────────
FLIGHT, BLUE_BASE, RED_BASE, RED_STRIKE = 'Blue-Flight', 'Blue-Base', 'Red-Base', 'Red-Strike'
FLIGHT_ALTITUDE = 5_000.0
AIR_SPEED = 250.0
FLIGHT_START_X, FLIGHT_END_X = -100_000.0, 100_000.0
# Distanza [m] percorribile col carburante dato all'F-16C: valore di test, non un dato.
AIR_FUEL_RANGE = 50_000.0
AIR_EXHAUSTION_TIME = AIR_FUEL_RANGE / AIR_SPEED                    # 200 s
AIR_EXHAUSTION_POINT = (FLIGHT_START_X + AIR_FUEL_RANGE, 0.0, FLIGHT_ALTITUDE)
BASE_POSITION = {'glide': (-50_000.0, 20_000.0), 'no_base': (-50_000.0, 60_000.0),
                 'enemy_base': (-50_000.0, 20_000.0), 'off': (-50_000.0, 20_000.0)}
STRIKE_START = 600.0
STRIKE_ALTITUDE = 3_000.0
STRIKE_LEG = 60_000.0          # lo strike parte 60 km a sud della base
MARKER_SHOT = dataclasses.replace(F.SHOTS['agm'], accuracy=0.0, weapon='test:marker')

# ── Costanti di S24-ORBIT, dichiarate di test (come S23-CAP) ────────────────────
CAP, BOMBER = 'Red-CAP', 'Blue-Bomber'
CAP_SENSOR_RANGE = 30_000.0
CAP_ALTITUDE = 6_000.0
BOMBER_ALTITUDE = 5_000.0
CAP_START_X, CAP_EXIT_X = -75_000.0, -150_000.0
ORBIT_ARRIVAL = -CAP_START_X / AIR_SPEED          # 300 s
ORBIT_DURATION = 1_500.0
ORBIT_EXHAUSTION = ORBIT_ARRIVAL + ORBIT_DURATION / 2.0   # 1050 s: carburante per meta' orbita
LATE_CROSSING = 1_400.0
BOMBER_START_Y = 150_000.0

# Soglie delle frazioni aggregate sui seed: DICHIARATE di test, non tarate sul risultato (stesse stime
# di S22/S23: il rilevamento e' una estrazione per finestra e osservatore; con piu' osservatori o una
# finestra lunga il tiro e' la regola, 0,5 = "la regola, non l'eccezione").
MIN_FIRING_FRACTION = 0.5


def _seeds(prefix: str, count: int = SEEDS_PER_SCENARIO):
    return [f'{prefix}-{index}' for index in range(count)]


def _shots_by(outcome, prefix: str):
    return [event for event in outcome.ammunition_events if event.asset_id.startswith(prefix + '/')]


def _switches(constraint: bool = True, per_leg: bool = True):
    """Contesto: interruttori F6-A com'erano (True) o spenti (varianti di controllo)."""
    return patch.multiple(SS, F6_FUEL_CONSTRAINT=SS.F6_FUEL_CONSTRAINT and constraint,
                          F6_FUEL_PER_LEG=SS.F6_FUEL_PER_LEG and per_leg)


def _run(scenario: F.Scenario, session_id: str, **switches):
    """Esegue lo scenario registrando i tratti dati allo scheduler e il programma degli aerei a terra."""
    with _switches(**switches), patch.object(CS, 'schedule_contacts', wraps=CS.schedule_contacts) as scheduler:
        outcome = scenario.run(session_id)

    return outcome, scheduler.call_args.kwargs['legs'], scheduler.call_args.kwargs['grounded']


# ── S24-E5: carro a secco ─────────────────────────────────────────────────────

def _tank_scenario(variant: str) -> F.Scenario:
    near = variant.startswith('near')
    start, end = (NEAR_START, NEAR_END) if near else (FAR_START, FAR_END)
    post = F.build_force(POST, 'Red', [F.Unit('vehicle', 'BMP-2', 3, origin=(0.0, -RED_PLATOON_HALF_SPAN),
                                              step=(0.0, RED_PLATOON_HALF_SPAN), prefix='bmp',
                                              sensors={'ground': RED_SENSOR_RANGE})])
    armor = F.build_force(ARMOR, 'Blue', [F.Unit('vehicle', 'M1A2-Abrams', 1, origin=start, prefix='tank')])

    for asset in armor.assets.values():
        asset.fuel = DRY_FUEL

    mission, = F.missions_for(armor, [end], mission_type='Attack', target=F.group_target(POST), speed=ARMOR_SPEED)
    roles = {asset_id: 'unarmed' for asset_id in armor.assets}
    overrides = {asset_id: {'ground': SUPPRESSIVE_SHOT} for asset_id in post.assets}
    return F.Scenario(forces_a=[armor], forces_b=[post], missions=[mission],
                      fire_control=F.make_fire_control(roles=roles, overrides=overrides), duration=DURATION,
                      roles=roles)


def _tank_exhaustion(variant: str):
    """(istante, punto) d'esaurimento attesi: 852 m dalla partenza lungo la rotta, a 85,2 s."""
    start, end = (NEAR_START, NEAR_END) if variant.startswith('near') else (FAR_START, FAR_END)
    covered = DRY_FUEL * 426_000.0
    fraction = covered / ROUTE_LENGTH
    point = (start[0] + fraction * (end[0] - start[0]), start[1] + fraction * (end[1] - start[1]), 0.0)
    return covered / ARMOR_SPEED, point


class TestS24DryTank(F.LoggerSilencer, unittest.TestCase):
    """S24-E5: il carro a secco si ferma nel punto di esaurimento e resta un bersaglio li' (F6-A)."""

    SEEDS = _seeds('S24-E5')
    VARIANTS = ('far', 'far_off', 'near', 'near_off')
    TANK = f'{ARMOR}/tank0'
    MISSION = f'{ARMOR}:Attack'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                cls.runs[variant].append(_run(_tank_scenario(variant), session_id,
                                              constraint=not variant.endswith('_off')))

    def test_the_autonomy_of_the_experiment(self):
        """Il dato del registro su cui poggia E5: 426 km di autonomia dell'M1A2 (0,002 -> 852 m)."""
        tank = _tank_scenario('far').force(ARMOR).assets[self.TANK]
        self.assertAlmostEqual(tank.fuel_autonomy(), 426_000.0)

    def test_no_engagement_beyond_the_exhaustion_point(self):
        """Il criterio della Fase 6: fermo a 6,65 km dai BMP (fuori dal sensore) il carro non e' mai
        ingaggiato; con il vincolo spento Red spara al carro OLTRE il punto di esaurimento (E5)."""
        exhaustion, _ = _tank_exhaustion('far')

        for outcome, _, _ in self.runs['far']:
            self.assertEqual(_shots_by(outcome, POST), [], outcome.session_id)

        firing = 0

        for outcome, _, _ in self.runs['far_off']:
            shots = _shots_by(outcome, POST)
            firing += bool(shots)
            self.assertTrue(all(event.time > exhaustion for event in shots), outcome.session_id)

        self.assertGreaterEqual(firing / len(self.runs['far_off']), MIN_FIRING_FRACTION, firing)

    def test_the_legs_end_at_the_exhaustion_point(self):
        """Tratti dati allo scheduler: movimento fino al punto di esaurimento, poi FERMI nel punto fino
        alla fine della sessione; con il vincolo spento arrivano all'ultimo punto."""
        for variant in ('far', 'near'):
            exhaustion, point = _tank_exhaustion(variant)

            for _, legs, _ in self.runs[variant]:
                tank = legs[self.TANK]
                self.assertAlmostEqual(tank[0].t_end, exhaustion, delta=1e-6)
                self.assertEqual(len(tank), 2)
                self.assertEqual(tank[1].p_start, tank[1].p_end)
                self.assertAlmostEqual(tank[1].t_end, DURATION)

                for got, want in zip(tank[1].p_start, point):
                    self.assertAlmostEqual(got, want, delta=1e-6)

            for _, legs, _ in self.runs[variant + '_off']:
                self.assertAlmostEqual(legs[self.TANK][0].t_end, ROUTE_LENGTH / ARMOR_SPEED, delta=1e-6)

    def test_the_halted_tank_stays_a_target(self):
        """'near': il carro fermo a ~3,9 km resta nel sensore per tutta la sessione: Red spara anche dopo
        `NEAR_LEAVE` nella maggior parte delle repliche; con il vincolo spento mai dopo `NEAR_LEAVE`."""
        late = sum(1 for outcome, _, _ in self.runs['near']
                   if any(event.time > NEAR_LEAVE for event in _shots_by(outcome, POST)))
        self.assertGreaterEqual(late / len(self.runs['near']), MIN_FIRING_FRACTION, late)

        for outcome, _, _ in self.runs['near_off']:
            for event in _shots_by(outcome, POST):
                self.assertLessEqual(event.time, NEAR_LEAVE + 1e-6, outcome.session_id)

    def test_the_outcome_reports_fuel(self):
        """Esito: carro NON distrutto, motivo FUEL_EXHAUSTED all'istante di esaurimento, missione
        ABORTED per carburante, postura `Defense`; un FuelEvent esaurito su 852 m; con il vincolo spento
        la rotta e' completata (FuelEvent esaurito, come prima)."""
        for variant in ('far', 'near'):
            exhaustion, _ = _tank_exhaustion(variant)

            for outcome, _, _ in self.runs[variant]:
                mission = outcome.mission_outcomes[self.MISSION]
                tank = mission.asset_outcomes[self.TANK]
                self.assertEqual((mission.status, mission.reason), (MissionStatus.ABORTED, AbortReason.FUEL))
                self.assertEqual((tank.state, tank.end_reason), (AssetState.OPERATIONAL, AssetEndReason.FUEL_EXHAUSTED))
                self.assertAlmostEqual(tank.end_time, exhaustion, delta=1e-6)
                self.assertEqual(outcome.postures[self.TANK], MA.GROUND_DEFENSE_POSTURE)
                self.assertFalse(any(e.destroyed for e in outcome.damage_events))
                event, = outcome.fuel_events
                self.assertTrue(event.exhausted)
                self.assertAlmostEqual(event.distance_covered, DRY_FUEL * 426_000.0, delta=1e-3)
                self.assertEqual(mission.actual_etas[1], None)

            for outcome, _, _ in self.runs[variant + '_off']:
                mission = outcome.mission_outcomes[self.MISSION]
                self.assertEqual(mission.status, MissionStatus.COMPLETED)
                self.assertEqual(mission.asset_outcomes[self.TANK].end_reason, AssetEndReason.ROUTE_COMPLETED)
                event, = outcome.fuel_events
                self.assertTrue(event.exhausted)
                self.assertLess(event.distance_covered, event.distance)


# ── S24-GLIDE: aereo a secco in volo ──────────────────────────────────────────

def _glide_scenario(variant: str) -> F.Scenario:
    flight = F.build_force(FLIGHT, 'Blue', [F.Unit('aircraft', 'F-16C Block 52d', 1,
                                                   origin=(FLIGHT_START_X, 0.0, FLIGHT_ALTITUDE), prefix='f',
                                                   loadout='Strike')], mil_category=F.AIR_UNIT)

    for asset in flight.assets.values():
        asset.fuel = AIR_FUEL_RANGE / asset.fuel_autonomy()

    mission, = F.missions_for(flight, [(FLIGHT_END_X, 0.0)], mission_type='Strike',
                              target=F.zone_target((FLIGHT_END_X, 0.0), 10_000.0), speed=AIR_SPEED)
    base_id, side = (RED_BASE, 'Red') if variant == 'enemy_base' else (BLUE_BASE, 'Blue')
    base = F.make_force(base_id, side, F.AIR_UNIT)
    bx, by = BASE_POSITION[variant]
    F.add_assets(base, [F.make_structure(base, f'{base_id}/depot0', (bx, by), category='Farp', asset_type='Oil_Tank')])
    # Lo strike Red sorvola il punto della base 'glide' da sud a nord (sopra la base a ~840 s).
    gx, gy = BASE_POSITION['glide']
    strike = F.build_force(RED_STRIKE, 'Red', [F.Unit('aircraft', 'F-16C Block 52d', 2,
                                                      origin=(gx, gy - STRIKE_LEG, STRIKE_ALTITUDE), step=(500.0, 0.0),
                                                      prefix='str', loadout='Strike')], mil_category=F.AIR_UNIT)
    strike_mission, = F.missions_for(strike, [(gx, gy + STRIKE_LEG)], mission_type='Strike',
                                     target=F.zone_target((gx, gy), 10_000.0), speed=AIR_SPEED)
    strike_mission = dataclasses.replace(strike_mission, start_time=STRIKE_START)
    roles = {**{asset_id: 'unarmed' for asset_id in flight.assets}, **{asset_id: 'strike' for asset_id in strike.assets}}
    # Lanci Red SENZA effetto e solo contro aerei a terra: si misura se l'aereo atterrato e' un bersaglio.
    overrides = {asset_id: {'structure': None, 'parked': MARKER_SHOT} for asset_id in strike.assets}
    blue = [flight] + ([base] if side == 'Blue' else [])
    red = [strike] + ([base] if side == 'Red' else [])
    return F.Scenario(forces_a=blue, forces_b=red, missions=[mission, strike_mission],
                      fire_control=F.make_fire_control(roles=roles, overrides=overrides), duration=DURATION,
                      roles=roles)


def _landing(variant: str):
    """(punto, istante) d'atterraggio attesi: la base a quota 0, alla crociera dell'F-16C."""
    bx, by = BASE_POSITION[variant]
    landing = (bx, by, 0.0)
    flight = _glide_scenario(variant).force(FLIGHT)
    speed = FM.cruise_speed(next(iter(flight.assets.values())))
    return landing, AIR_EXHAUSTION_TIME + math.dist(AIR_EXHAUSTION_POINT, landing) / speed


class TestS24DryAircraft(F.LoggerSilencer, unittest.TestCase):
    """S24-GLIDE: un aereo a secco in volo plana sulla base raggiungibile o e' perso (F6-A)."""

    SEEDS = _seeds('S24-GLIDE')
    VARIANTS = ('glide', 'no_base', 'enemy_base', 'off')
    JET = f'{FLIGHT}/f0'
    MISSION = f'{FLIGHT}:Strike'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                scenario = _glide_scenario(variant)
                outcome, legs, grounded = _run(scenario, session_id, constraint=variant != 'off')
                cls.runs[variant].append((outcome, legs, grounded, scenario.force(FLIGHT).assets[cls.JET]))

    def test_the_glide_lands_on_the_base(self):
        """'glide': tratti fino all'esaurimento (200 s), planata in linea retta sulla base, poi fermo a
        terra sulla base fino a fine sessione (programma a terra dall'atterraggio)."""
        landing, t_land = _landing('glide')

        for _, legs, grounded, _ in self.runs['glide']:
            jet = legs[self.JET]
            self.assertAlmostEqual(jet[0].t_end, AIR_EXHAUSTION_TIME, delta=1e-6)
            glide, parked = jet[-2], jet[-1]

            for got, want in zip(glide.p_start, AIR_EXHAUSTION_POINT):
                self.assertAlmostEqual(got, want, delta=1e-6)

            self.assertEqual(glide.p_end, landing)
            self.assertAlmostEqual(glide.t_end, t_land, delta=1e-6)
            self.assertEqual((parked.p_start, parked.p_end, parked.t_end), (landing, landing, DURATION))
            self.assertEqual(grounded.intervals(self.JET), ((t_land, float('inf')),))

    def test_the_landed_aircraft_is_a_target(self):
        """Lo strike Red, sopra la base dopo l'atterraggio, lancia sull'aereo a terra nella maggior parte
        delle repliche e solo dopo l'atterraggio; nelle altre varianti l'aereo non c'e' e Red non lancia."""
        _, t_land = _landing('glide')
        firing = 0

        for outcome, _, _, _ in self.runs['glide']:
            shots = _shots_by(outcome, RED_STRIKE)
            firing += bool(shots)
            self.assertTrue(all(event.time >= t_land for event in shots), outcome.session_id)

        self.assertGreaterEqual(firing / len(self.runs['glide']), MIN_FIRING_FRACTION, firing)

        for variant in ('no_base', 'enemy_base', 'off'):
            for outcome, _, _, _ in self.runs[variant]:
                self.assertEqual(_shots_by(outcome, RED_STRIKE), [], (variant, outcome.session_id))

    def test_glide_outcome_is_aborted(self):
        """'glide': asset non distrutto, motivo FUEL_EXHAUSTED a 200 s, missione ABORTED per carburante,
        postura a terra."""
        for outcome, _, _, jet in self.runs['glide']:
            mission = outcome.mission_outcomes[self.MISSION]
            asset = mission.asset_outcomes[self.JET]
            self.assertEqual((mission.status, mission.reason), (MissionStatus.ABORTED, AbortReason.FUEL))
            self.assertEqual((asset.state, asset.end_reason), (AssetState.OPERATIONAL, AssetEndReason.FUEL_EXHAUSTED))
            self.assertAlmostEqual(asset.end_time, AIR_EXHAUSTION_TIME, delta=1e-6)
            self.assertEqual(outcome.postures[self.JET], MA.PARKED_POSTURE)
            self.assertFalse(jet.is_destroyed())
            self.assertEqual(jet.fuel, 0.0)

    def test_without_a_reachable_own_base_the_aircraft_is_lost(self):
        """'no_base' (base oltre il raggio di planata) e 'enemy_base' (base del nemico): l'aereo e'
        perso all'esaurimento: DESTROYED con motivo FUEL_EXHAUSTED, salute a 0, nessun DamageEvent,
        missione DESTROYED, nessun tratto dopo i 200 s, postura `destroyed` (F6-B1)."""
        for variant in ('no_base', 'enemy_base'):
            for outcome, legs, grounded, jet in self.runs[variant]:
                mission = outcome.mission_outcomes[self.MISSION]
                asset = mission.asset_outcomes[self.JET]
                self.assertEqual(mission.status, MissionStatus.DESTROYED, variant)
                self.assertEqual((asset.state, asset.end_reason), (AssetState.DESTROYED, AssetEndReason.FUEL_EXHAUSTED))
                self.assertAlmostEqual(asset.end_time, AIR_EXHAUSTION_TIME, delta=1e-6)
                self.assertTrue(jet.is_destroyed())
                self.assertEqual(jet.health, 0)
                self.assertEqual([e for e in outcome.damage_events if e.target_id == self.JET], [])
                self.assertAlmostEqual(legs[self.JET][-1].t_end, AIR_EXHAUSTION_TIME, delta=1e-6)
                # F6-B1: postura `destroyed` (con `F6_DESTROYED_POSTURE` spento: `off_scene`).
                self.assertEqual(outcome.postures[self.JET], MA.DESTROYED_POSTURE)
                self.assertFalse(grounded.ever(self.JET))

    def test_without_the_constraint_the_aircraft_flies_on_dry(self):
        """'off': il comportamento di prima: l'aereo completa la rotta a secco, un FuelEvent esaurito a
        50 km sui 200 km del tratto, nessuna distruzione."""
        for outcome, legs, _, jet in self.runs['off']:
            self.assertAlmostEqual(legs[self.JET][-1].t_end, (FLIGHT_END_X - FLIGHT_START_X) / AIR_SPEED, delta=1e-6)
            self.assertEqual(outcome.mission_outcomes[self.MISSION].status, MissionStatus.COMPLETED)
            event, = [e for e in outcome.fuel_events if e.asset_id == self.JET]
            self.assertTrue(event.exhausted)
            self.assertAlmostEqual(event.distance_covered, AIR_FUEL_RANGE, delta=1e-3)
            self.assertFalse(jet.is_destroyed())


# ── S24-ORBIT: esaurimento durante l'orbita ───────────────────────────────────

def _wait(mode: str, duration: float) -> MissionAction:
    return MissionAction(kind=ActionKind.WAIT, name=f'Wait_{mode}', wait_mode=mode, wait_duration_s=duration)


def _cap_mission(cap) -> Mission:
    """CAP da x = -75 km a O = (0, 0), WAIT 'orbit', rientro a x = -150 km (come S23-CAP, un aereo)."""
    lead, = sorted(cap.assets)
    route = F.straight_route([(CAP_START_X, 0.0), (0.0, 0.0), (CAP_EXIT_X, 0.0)], AIR_SPEED, 'cap-route',
                             z=CAP_ALTITUDE)
    roles = [WaypointRole.NAV, WaypointRole.HOLD, WaypointRole.LAND]
    actions = {1: [_wait('orbit', ORBIT_DURATION)]}
    waypoints = tuple(MissionWaypoint(wp, role, actions=tuple(actions.get(index, ())))
                      for index, (wp, role) in enumerate(zip(route_waypoints(route), roles)))
    return Mission(mission_id=f'{CAP}:CAP', block_id=CAP, domain='air', mission_type='CAP',
                   assets=(MissionAsset(lead, 'lead', loadout='CAP'),),
                   target=F.zone_target((0.0, 0.0), CAP_SENSOR_RANGE), route=route, waypoints=waypoints,
                   start_time=0.0, start_mode=StartMode.AIR)


def _dry_cap_fuel(mig) -> float:
    """Carburante per l'avvicinamento (75 km) e meta' orbita alla crociera: esaurimento a 1050 s."""
    return (-CAP_START_X + FM.cruise_speed(mig) * ORBIT_DURATION / 2.0) / mig.fuel_autonomy()


def _orbit_scenario(variant: str) -> F.Scenario:
    cap = F.build_force(CAP, 'Red', [F.Unit('aircraft', 'MiG-29S', 1, origin=(CAP_START_X, 0.0, CAP_ALTITUDE),
                                            prefix='cap', loadout='CAP', sensors={'air': CAP_SENSOR_RANGE})],
                        mil_category=F.AIR_UNIT)

    if variant != 'full':
        for asset in cap.assets.values():
            asset.fuel = _dry_cap_fuel(asset)

    bomber = F.build_force(BOMBER, 'Blue', [F.Unit('aircraft', 'F-16C Block 52d', 2,
                                                   origin=(0.0, BOMBER_START_Y, BOMBER_ALTITUDE), step=(1_000.0, 0.0),
                                                   prefix='bmb', loadout='Strike')], mil_category=F.AIR_UNIT)
    bomber_mission, = F.missions_for(bomber, [(0.0, -BOMBER_START_Y)], mission_type='Strike',
                                     target=F.zone_target((0.0, -BOMBER_START_Y), 10_000.0), speed=AIR_SPEED)
    bomber_mission = dataclasses.replace(bomber_mission, start_time=LATE_CROSSING - BOMBER_START_Y / AIR_SPEED)
    roles = {**{asset_id: 'fighter' for asset_id in cap.assets}, **{asset_id: 'unarmed' for asset_id in bomber.assets}}
    return F.Scenario(forces_a=[bomber], forces_b=[cap], missions=[bomber_mission, _cap_mission(cap)],
                      fire_control=F.make_fire_control(roles=roles), duration=DURATION, roles=roles)


class TestS24OrbitExhaustion(F.LoggerSilencer, unittest.TestCase):
    """S24-ORBIT: l'orbita consuma nel tempo e porta all'esaurimento durante l'attesa (F6-A)."""

    SEEDS = _seeds('S24-ORBIT')
    VARIANTS = ('dry', 'full', 'per_leg_off')
    MIG = f'{CAP}/cap0'
    MISSION = f'{CAP}:CAP'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                scenario = _orbit_scenario(variant)
                outcome, legs, _ = _run(scenario, session_id, per_leg=variant != 'per_leg_off')
                cls.runs[variant].append((outcome, legs, scenario.force(CAP).assets[cls.MIG]))

    def _mig_events(self, outcome):
        return [event for event in outcome.fuel_events if event.asset_id == self.MIG]

    def test_fuel_events_are_per_leg(self):
        """'full': tre FuelEvent (avvicinamento, orbita FERMA, rientro); l'orbita consuma 1500 s alla
        crociera del MiG (al regime di crociera anche se la CAP ha combattuto). 'per_leg_off': uno solo,
        sulla distanza della sola rotta (225 km), senza consumo dell'orbita. (Al regime di combattimento
        della contabilita' quell'evento puo' risultare esaurito anche se a crociera il carburante basta:
        limite noto della F6-A, il vincolo del movimento e' calcolato a monte alla crociera.)"""
        for outcome, _, mig in self.runs['full']:
            approach, orbit, exit_leg = self._mig_events(outcome)
            self.assertEqual([e.stationary for e in (approach, orbit, exit_leg)], [False, True, False])
            self.assertAlmostEqual(orbit.duration, ORBIT_DURATION, delta=1e-6)
            self.assertEqual((orbit.distance, orbit.regime), (0.0, FM.HOLD_REGIME))
            expected = FM.cruise_speed(mig) * ORBIT_DURATION / mig.fuel_autonomy()
            self.assertAlmostEqual(orbit.amount, expected, delta=1e-12)
            self.assertAlmostEqual(orbit.fuel_before, approach.fuel_after, delta=1e-12)

        for outcome, legs, _ in self.runs['per_leg_off']:
            event, = self._mig_events(outcome)
            self.assertAlmostEqual(event.distance, -CAP_START_X - CAP_EXIT_X, delta=1e-3)
            self.assertAlmostEqual(legs[self.MIG][-1].t_end, ORBIT_ARRIVAL + ORBIT_DURATION - CAP_EXIT_X / AIR_SPEED,
                                   delta=1e-6)

    def test_the_orbit_runs_the_tank_dry(self):
        """'dry': due FuelEvent, l'orbita esaurita a meta' (750 s di 1500); il MiG e' perso in O a 1050 s
        (6000 m, nessuna base), tratti finiti li'."""
        for outcome, legs, mig in self.runs['dry']:
            approach, orbit = self._mig_events(outcome)
            self.assertFalse(approach.exhausted)
            self.assertTrue(orbit.exhausted and orbit.stationary)
            self.assertAlmostEqual(orbit.duration_covered, ORBIT_DURATION / 2.0, delta=1e-3)
            self.assertAlmostEqual(legs[self.MIG][-1].t_end, ORBIT_EXHAUSTION, delta=1e-3)
            asset = outcome.mission_outcomes[self.MISSION].asset_outcomes[self.MIG]
            self.assertEqual((asset.state, asset.end_reason), (AssetState.DESTROYED, AssetEndReason.FUEL_EXHAUSTED))
            self.assertAlmostEqual(asset.end_time, ORBIT_EXHAUSTION, delta=1e-3)
            self.assertTrue(mig.is_destroyed())

    def test_no_interception_after_the_exhaustion(self):
        """I bombardieri passano per O a 1400 s, durante l'orbita PIANIFICATA ma dopo l'esaurimento: in
        'dry' la CAP non c'e' piu' e non spara; con il pieno, o senza consumo nell'orbita, spara nella
        maggior parte delle repliche."""
        for outcome, _, _ in self.runs['dry']:
            self.assertEqual(_shots_by(outcome, CAP), [], outcome.session_id)

        for variant in ('full', 'per_leg_off'):
            firing = sum(1 for outcome, _, _ in self.runs[variant] if _shots_by(outcome, CAP))
            self.assertGreaterEqual(firing / len(self.runs[variant]), MIN_FIRING_FRACTION, (variant, firing))


if __name__ == '__main__':
    unittest.main()
