"""Scenario S22 del motore di sessioni virtuali: presenza fuori dalla rotta (F5 passo (b)).

Prosegue `Test_Session_Scenarios.py` (S1-S9), `Test_Session_Scenarios_S10_S18.py`, gli S19, S20 e S21
con la stessa disciplina: si verifica un comportamento QUALITATIVO o STRUTTURALE, mai un numero
calibrato.

Criterio "Fatto quando" della Fase 5 di `Analysis/Document/Piano_Implementazione_Missione.md`: *gli
esperimenti E1 ed E3 dell'analisi del 26/09 danno presenza continua (il carro fermo a 4 km resta
ingaggiabile)*. Decisioni dell'utente (D1.a/b, deviazione 13): un asset di missione NON sparisce
fuori dalla sua rotta (v. `Logic/Mission_Adapter`, "Presenza prima della partenza e dopo la fine"):
  * unita' terrestri e navali presenti FERME prima della partenza e dopo la fine, in `Defense`;
  * aerei che non partono in volo A TERRA fino al decollo (bersagli di superficie passivi);
  * aerei a terra dopo la fine SOLO se l'ultimo punto e' LAND su una base vera, altrimenti escono
    di scena all'arrivo (fino al rientro della F6).
Prima della F5-B (`Analisi_Modello_Missione_Sessione.md` §3, P3) un asset con rotta esisteva solo
fra la partenza e l'arrivo: in E1 il carro arrivato a 4 km dal nemico spariva.

## S22-E1: missione terrestre finita (`TestS22E1FinishedMissionStaysEngageable`)

Red-Post: un plotone di 3 BMP-2 fermi intorno a (0, 0), nessuna missione, sensore 'ground'
dichiarato di `RED_SENSOR_RANGE` (4,2 km). Blue-Armor: un M1A2 che NON spara (ruolo 'unarmed',
assente dalla tabella di fuoco: si misura solo se e' un bersaglio). Due varianti per seed:
  * 'finished': missione da x = -12 km a x = -4 km a 10 m/s (arrivo a t = 800 s), poi fermo;
  * 'static': lo stesso M1A2 senza missione, fermo a x = -4 km per tutta la sessione (E2 dell'analisi:
    il riferimento di un asset sempre presente).
Il contatto comincia quando Blue entra nel raggio del sensore Red (x = -4,2 km, t = 780 s): prima
della F5-B la finestra durava 20 s, meno del tempo di rilevamento e reazione del BMP-2 (il primo
colpo arriva ~30 s dopo l'inizio di una finestra, misura del 2026-10-12): NESSUN colpo era possibile.
Ora la finestra dura fino alla fine della sessione. Il rilevamento e' UNA estrazione per finestra e
osservatore (Pd ~0,59 a 4 km con questa portata, `Engagement_Resolver.detection_probability`): con
tre osservatori il carro e' visto in ~93% delle repliche, in quelle restanti nessuno spara (in
entrambe le varianti), per questo l'asserzione e' una frazione di repliche.

## S22-E3: partenza ritardata (`TestS22E3LateDepartureIsPresent`)

Stesse forze; l'M1A2 e' a x = -4 km (dentro il sensore Red) e parte a t = 1000 s verso x = -12 km
(ripiegamento, arrivo a t = 1800 s; esce dal sensore a t = 1020 s). Prima della F5-B esisteva solo
da t = 1000 s (finestra di 20 s: nessun colpo possibile); ora e' presente e colpibile da t = 0.
Variante 'not_departed': partenza oltre la fine della sessione (presente, fermo, per tutta la
sessione: postura `Defense`, D1.b).

## S22-AIR: aerei a terra prima del decollo e dopo l'atterraggio (`TestS22AircraftOnTheGround`)

Red-Airbase (Military 'Airbase'): 2 MiG-29S (loadout 'CAP') e un deposito carburante (`Structure`
'Oil_Tank', il riferimento della base per l'atterraggio). Blue-Strike: 2 F-16C 'Strike' in sorvolo
della base a 3000 m (da x = -60 km a x = +20 km, ruolo 'strike': 'agm' contro 'parked', nessun tiro
contro il deposito per `overrides`, cosi' gli unici bersagli possibili sono gli aerei a terra).
Varianti per seed:
  * 'parked': missione Red di intercettazione che parte dal PARCHEGGIO (quota 0) a t = `TAKEOFF`,
    dopo il passaggio dello strike: i MiG sono a terra durante l'attacco, quindi colpiti;
  * 'airborne': stessa missione, ma lo strike parte a t = `LATE_STRIKE` (dopo il decollo dei MiG,
    che sono gia' usciti di scena: rotta senza atterraggio su una base vera): nessun bersaglio;
  * 'landed': i MiG arrivano IN VOLO da est e atterrano sulla base (ultimo punto LAND che riferisce il
    deposito, `Mission_Adapter.lands_on_air_base`, a ~240 s); lo strike parte a t = `LATE_STRIKE`:
    di nuovo a terra, colpiti;
  * 'no_base': come 'landed', ma l'ultimo punto LAND non riferisce una base ed e' a 30 km dalla
    base (fuori dalla sua area): escono di scena all'arrivo, lo strike (a t = `LATE_STRIKE`) non
    trova bersagli;
  * 'base_area': come 'landed', ma l'ultimo punto LAND NON riferisce la base: e' nella sua AREA
    (1,9 km dal deposito, entro `Mission_Adapter.AIR_BASE_AREA_RADIUS_M`): a terra, colpiti.
I MiG in volo non incontrano mai lo strike (geometria e tempi separati): la variante misura solo lo
stato a terra/in volo, non un combattimento aereo.

Asserzioni robuste: invarianti per replica (chi spara, a chi, quando rispetto agli istanti di
partenza/arrivo/decollo/atterraggio, postura nell'esito) e, per la distruzione, frazioni aggregate
sui seed con soglie DICHIARATE (stime di test, non tarate sul risultato; v. sotto).
"""

import unittest

from sympy import Point3D

from Code.Dynamic_War_Manager.Source.Command.Mission_Types import (
    Mission,
    MissionAsset,
    MissionWaypoint,
    StartMode,
    WaypointRole,
    route_waypoints,
)
from Code.Dynamic_War_Manager.Source.DataType.Edge import Edge
from Code.Dynamic_War_Manager.Source.DataType.Route import Route
from Code.Dynamic_War_Manager.Source.DataType.Waypoint import Waypoint
from Code.Dynamic_War_Manager.Source.Logic import Mission_Adapter as MA
from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F

POST = 'Red-Post'
ARMOR = 'Blue-Armor'
BASE = 'Red-Airbase'
STRIKE = 'Blue-Strike'
DURATION = 3_600.0

# Sensore 'ground' dichiarato dei BMP-2 Red [m]: valore DI TEST (non dal registro), poco oltre i
# 4 km dell'esperimento E1, cosi' che il contatto cominci solo 20 s prima dell'arrivo di Blue.
RED_SENSOR_RANGE = 4_200.0
RED_PLATOON = 3
# Velocita' di marcia di Blue [m/s]: dichiarata di test, sotto il massimo dell'M1A2 (regola A).
ARMOR_SPEED = 10.0
FAR_X, NEAR_X = -12_000.0, -4_000.0
ARRIVAL = (NEAR_X - FAR_X) / ARMOR_SPEED          # E1: arrivo a x = -4 km, 800 s
DEPARTURE = 1_000.0                                # E3: partenza da x = -4 km

# Tempi di S22-AIR [s], dichiarati di test: decollo dei MiG dopo il passaggio dello strike (sorvolo
# della base a ~225 s); strike tardivo dopo il decollo e l'uscita di scena dei MiG ('airborne') o dopo
# il loro atterraggio ('landed', 'no_base'), cosi' che MiG in volo e strike non si incontrino mai.
TAKEOFF = 900.0
LATE_STRIKE = 1_500.0
FLIGHT_ALTITUDE = 3_000.0
STRIKE_ROUTE = [(20_000.0, 0.0)]
MIG_SPEED = 250.0       # dichiarata di test, sotto il massimo del MiG-29S (regola A)

# Soglie delle frazioni aggregate sui seed: DICHIARATE di test, non tarate sul risultato. Il
# requisito e' qualitativo (l'asset presente e' un bersaglio): basta che ingaggio e colpi siano la
# regola e non l'eccezione.
#   * S22-E1/E3, repliche in cui Red spara al carro: attesa a priori ~0,93 (v. docstring); 0,5 sta
#     ~5 deviazioni standard sotto su 8 seed (0,09). Misura del 2026-10-12: E1 8/8 in entrambe le
#     varianti, E3 7/8 in entrambe.
#   * S22-AIR, MiG colpiti (danneggiati o distrutti) da uno strike che li vede a terra: misura del
#     2026-10-12 16/16 in 'parked' e in 'landed' (distrutti 9/16: la distruzione NON e' asserita,
#     due F-16C lanciano 2-3 missili per passaggio).
MIN_ENGAGED_FRACTION = 0.5
MIN_HIT_FRACTION = 0.5


def _seeds(prefix: str, count: int):
    return [f'{prefix}-{index}' for index in range(count)]


def _shots_by(outcome, prefix: str):
    return [event for event in outcome.ammunition_events if event.asset_id.startswith(prefix + '/')]


def _hit(outcome, asset_ids):
    """Asset di `asset_ids` danneggiati o distrutti nella sessione."""
    wanted = set(asset_ids)
    return {event.target_id for event in outcome.damage_events
            if event.target_id in wanted and (event.destroyed or (event.health_before or 0) > (event.health_after or 0))}


# ── S22-E1 / S22-E3: unita' terrestre presente fuori dalla rotta ──────────────

def _ground_scenario(*, blue_origin_x: float, points=None, start_time: float = 0.0) -> F.Scenario:
    """BMP-2 Red fermo in (0, 0) + M1A2 Blue che non spara. `points` None = Blue senza missione."""
    post = F.build_force(POST, 'Red', [F.Unit('vehicle', 'BMP-2', RED_PLATOON, origin=(0.0, -200.0), step=(0.0, 200.0),
                                              prefix='bmp', sensors={'ground': RED_SENSOR_RANGE})])
    armor = F.build_force(ARMOR, 'Blue', [F.Unit('vehicle', 'M1A2-Abrams', 1, origin=(blue_origin_x, 0.0),
                                                 prefix='tank')])
    roles = {asset_id: 'unarmed' for asset_id in armor.assets}
    missions = []

    if points is not None:
        mission, = F.missions_for(armor, points, mission_type='Attack', target=F.group_target(POST),
                                  speed=ARMOR_SPEED)
        missions = [_with_start(mission, start_time)]

    return F.Scenario(forces_a=[armor], forces_b=[post], missions=missions,
                      fire_control=F.make_fire_control(roles=roles), duration=DURATION, roles=roles)


def _with_start(mission: Mission, start_time: float) -> Mission:
    return Mission(mission_id=mission.mission_id, block_id=mission.block_id, domain=mission.domain,
                   mission_type=mission.mission_type, target=mission.target, assets=mission.assets,
                   route=mission.route, waypoints=mission.waypoints, start_time=start_time,
                   start_mode=mission.start_mode)


def _tank(scenario):
    return next(iter(scenario.force(ARMOR).assets))


class _GroundChecks:
    """Mixin (NON un TestCase): `runs` = {variante: [(scenario, outcome)]}."""

    runs = {}

    def _all(self):
        return [pair for pairs in self.runs.values() for pair in pairs]

    def test_blue_never_fires(self):
        for _, outcome in self._all():
            self.assertEqual(_shots_by(outcome, ARMOR), [], outcome.session_id)

    def test_red_hits_only_the_tank(self):
        for scenario, outcome in self._all():
            self.assertLessEqual({event.target_id for event in outcome.damage_events}, {_tank(scenario)},
                                 outcome.session_id)

    def test_the_tank_is_engaged_in_most_replicas(self):
        """In ogni variante Red spara al carro nella maggior parte delle repliche (frazione)."""
        for variant, pairs in self.runs.items():
            engaged = sum(1 for _, outcome in pairs if _shots_by(outcome, POST))
            self.assertGreaterEqual(engaged / len(pairs), MIN_ENGAGED_FRACTION, variant)


class TestS22E1FinishedMissionStaysEngageable(_GroundChecks, F.LoggerSilencer, unittest.TestCase):
    """S22-E1: un carro arrivato a 4 km dal nemico resta un bersaglio (F5-B, D1.a)."""

    SEEDS = _seeds('S22-E1', 8)
    VARIANTS = ('finished', 'static')

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                if variant == 'finished':
                    scenario = _ground_scenario(blue_origin_x=FAR_X, points=[(NEAR_X, 0.0)])
                else:
                    scenario = _ground_scenario(blue_origin_x=NEAR_X)

                cls.runs[variant].append((scenario, scenario.run(session_id)))

    def test_red_fires_only_after_the_arrival(self):
        """Il cuore di E1: ogni colpo Red parte DOPO l'arrivo del carro (prima della F5-B la finestra
        finiva all'arrivo, 20 s dopo il contatto: nessun colpo), e la maggior parte delle repliche ne
        ha (`test_the_tank_is_engaged_in_most_replicas`)."""
        for _, outcome in self.runs['finished']:
            self.assertTrue(all(e.time > ARRIVAL for e in _shots_by(outcome, POST)), outcome.session_id)

    def test_finished_is_engaged_like_the_static_reference(self):
        """Il carro arrivato e' un bersaglio come quello sempre fermo (E2): frazioni di repliche
        ingaggiate entro due repliche l'una dall'altra (margine dichiarato, 8 seed)."""
        engaged = {variant: sum(1 for _, outcome in pairs if _shots_by(outcome, POST))
                   for variant, pairs in self.runs.items()}
        self.assertLessEqual(abs(engaged['finished'] - engaged['static']), 2, engaged)

    def test_final_posture_is_defense(self):
        for scenario, outcome in self._all():
            self.assertEqual(outcome.postures[_tank(scenario)], MA.GROUND_DEFENSE_POSTURE, outcome.session_id)
            self.assertEqual(outcome.postures[next(iter(scenario.force(POST).assets))], MA.GROUND_DEFENSE_POSTURE)


class TestS22E3LateDepartureIsPresent(_GroundChecks, F.LoggerSilencer, unittest.TestCase):
    """S22-E3: un carro che parte tardi e' presente (e colpibile) prima di partire (F5-B, D1.b)."""

    SEEDS = _seeds('S22-E3', 8)
    VARIANTS = ('late', 'not_departed')

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                start = DEPARTURE if variant == 'late' else DURATION + 600.0
                scenario = _ground_scenario(blue_origin_x=NEAR_X, points=[(FAR_X, 0.0)], start_time=start)
                cls.runs[variant].append((scenario, scenario.run(session_id)))

    def test_red_fires_before_the_departure(self):
        """Il cuore di E3: ogni colpo Red parte PRIMA della partenza del carro (prima della F5-B non
        esisteva prima di partire, e la finestra di 20 s dopo la partenza non permetteva colpi)."""
        for _, outcome in self.runs['late']:
            self.assertTrue(all(e.time < DEPARTURE for e in _shots_by(outcome, POST)), outcome.session_id)

    def test_final_postures(self):
        """Missione finita (arrivo a 1800 s) o non ancora partita: `Defense` in entrambi i casi."""
        for scenario, outcome in self._all():
            self.assertEqual(outcome.postures[_tank(scenario)], MA.GROUND_DEFENSE_POSTURE, outcome.session_id)


# ── S22-AIR: aerei a terra prima del decollo e dopo l'atterraggio ─────────────

def _air_route(points, speed: float, name: str, reference=None) -> Route:
    """Rotta aerea (x, y, z) con l'ultimo waypoint riferito a `reference` (base d'atterraggio)."""
    waypoints = [Waypoint(name=f'{name}-W{i}', point=Point3D(*point),
                          obj_reference=reference if i == len(points) - 1 else None)
                 for i, point in enumerate(points)]
    edges = {(a.name, b.name): Edge(wpA=a, wpB=b, path_type='air', danger_level=0.0, speed=speed, name=f'{name}-E{i}')
             for i, (a, b) in enumerate(zip(waypoints, waypoints[1:]))}
    return Route(route_type='air', edges=edges, name=name)


def _mig_mission(base, route: Route, start_time: float, start_mode: StartMode) -> Mission:
    waypoints = route_waypoints(route)
    first = WaypointRole.NAV if start_mode is StartMode.AIR else WaypointRole.DEPARTURE
    roles = [first] + [WaypointRole.NAV] * (len(waypoints) - 2) + [WaypointRole.LAND]
    mig_ids = sorted(asset_id for asset_id, asset in base.assets.items() if type(asset).__name__ == 'Aircraft')
    # La coppia vola in formazione: il gregario a 150 m sulla sinistra del capo (offset di formazione
    # = la sua posizione sul piazzale rispetto al capo, rotta verso est).
    members = tuple(MissionAsset(asset_id, 'lead' if index == 0 else 'wingman', right_m=-150.0 * index,
                                 loadout='CAP')
                    for index, asset_id in enumerate(mig_ids))
    return Mission(mission_id=f'{BASE}:CAP', block_id=BASE, domain='air', mission_type='CAP', assets=members,
                   target=F.zone_target((60_000.0, 0.0), 20_000.0), route=route,
                   waypoints=tuple(MissionWaypoint(wp, role) for wp, role in zip(waypoints, roles)),
                   start_time=start_time, start_mode=start_mode)


def _air_scenario(variant: str) -> F.Scenario:
    """S22-AIR ricostruito da zero (gli asset vengono mutati da run_session), v. docstring."""
    base = F.build_force(BASE, 'Red', [], mil_category=F.AIR_UNIT)
    landed = variant in ('landed', 'no_base', 'base_area')
    origin = (60_000.0, 0.0, FLIGHT_ALTITUDE) if landed else (0.0, 0.0, 0.0)
    migs = [F.make_aircraft(base, f'{BASE}/mig{index}', 'MiG-29S', (origin[0], origin[1] + 150.0 * index, origin[2]),
                            loadout='CAP')
            for index in range(2)]
    depot = F.make_structure(base, f'{BASE}/fuel0', (0.0, -400.0), category='Farp', asset_type='Oil_Tank')
    F.add_assets(base, migs + [depot])

    if landed:
        reference = depot if variant == 'landed' else None
        # Punto d'atterraggio: sulla base ('landed'), nella sua area senza riferimento ('base_area'),
        # a 30 km dalla base ('no_base').
        land_x, land_y = {'landed': (0.0, 0.0), 'base_area': (0.0, 1_500.0), 'no_base': (30_000.0, 0.0)}[variant]
        route = _air_route([(60_000.0, 0.0, FLIGHT_ALTITUDE), (land_x + 5_000.0, land_y, 500.0), (land_x, land_y, 0.0)],
                           MIG_SPEED, 'mig-in', reference)
        mission = _mig_mission(base, route, 0.0, StartMode.AIR)
    else:
        route = _air_route([(0.0, 0.0, 0.0), (5_000.0, 0.0, 500.0), (60_000.0, 0.0, FLIGHT_ALTITUDE)],
                           MIG_SPEED, 'mig-out')
        mission = _mig_mission(base, route, TAKEOFF, StartMode.PARKING_COLD)

    strike = F.build_force(STRIKE, 'Blue', [
        F.Unit('aircraft', 'F-16C Block 52d', 2, origin=(-60_000.0, 0.0, FLIGHT_ALTITUDE), step=(0.0, 500.0),
               prefix='str', loadout='Strike')], mil_category=F.AIR_UNIT)
    strike_mission, = F.missions_for(strike, STRIKE_ROUTE, mission_type='Strike', target=F.group_target(BASE))
    strike_mission = _with_start(strike_mission, 0.0 if variant == 'parked' else LATE_STRIKE)
    roles = {asset_id: 'strike' for asset_id in strike.assets}
    # Il deposito non e' un bersaglio dello strike: gli unici bersagli possibili sono gli aerei a terra.
    overrides = {asset_id: {'structure': None} for asset_id in strike.assets}
    return F.Scenario(forces_a=[strike], forces_b=[base], missions=[strike_mission, mission],
                      fire_control=F.make_fire_control(roles=roles, overrides=overrides), duration=DURATION,
                      roles=roles)


def _mig_ids(scenario):
    return {asset_id for asset_id, asset in scenario.force(BASE).assets.items() if type(asset).__name__ == 'Aircraft'}


def _landing_time(scenario) -> float:
    mission = next(m for m in scenario.missions if m.block_id == BASE)
    return MA.waypoint_times(MA.mission_movements(mission)[0])[-1]


class TestS22AircraftOnTheGround(F.LoggerSilencer, unittest.TestCase):
    """S22-AIR: aerei di missione a terra prima del decollo e dopo l'atterraggio su una base vera."""

    SEEDS = _seeds('S22-AIR', 8)
    VARIANTS = ('parked', 'airborne', 'landed', 'no_base', 'base_area')

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                scenario = _air_scenario(variant)
                cls.runs[variant].append((scenario, scenario.run(session_id)))

    def _all(self):
        return [pair for pairs in self.runs.values() for pair in pairs]

    def test_the_migs_never_fire_nor_intercept(self):
        for scenario, outcome in self._all():
            migs = _mig_ids(scenario)
            self.assertEqual([e for e in outcome.ammunition_events if e.asset_id in migs], [], outcome.session_id)
            self.assertEqual([e for e in outcome.interception_events if e.asset_id in migs], [], outcome.session_id)

    def test_parked_before_takeoff_they_are_hit_only_while_on_the_ground(self):
        """'parked': colpiti dall'arma aria-suolo dello strike, e i colpi partono prima del decollo."""
        hit = total = 0

        for scenario, outcome in self.runs['parked']:
            migs = _mig_ids(scenario)
            on_migs = [e for e in outcome.damage_events if e.target_id in migs]
            self.assertTrue(on_migs, outcome.session_id)
            self.assertEqual({e.weapon for e in on_migs}, {F.SHOTS['agm'].weapon}, outcome.session_id)
            strikers = set(scenario.force(STRIKE).assets)
            self.assertTrue(all(e.time < TAKEOFF for e in outcome.ammunition_events if e.asset_id in strikers),
                            outcome.session_id)
            hit += len(_hit(outcome, migs))
            total += len(migs)

        self.assertGreaterEqual(hit / total, MIN_HIT_FRACTION)

    def test_after_takeoff_they_are_no_longer_surface_targets(self):
        """'airborne' (strike dopo il decollo) e 'no_base' (nessun atterraggio vero): lo strike non
        spara, nessun danno."""
        for variant in ('airborne', 'no_base'):
            for scenario, outcome in self.runs[variant]:
                strikers = set(scenario.force(STRIKE).assets)
                self.assertEqual([e for e in outcome.ammunition_events if e.asset_id in strikers], [],
                                 outcome.session_id)
                self.assertEqual(outcome.damage_events, (), outcome.session_id)

    def test_landed_on_a_real_base_they_are_hit_again(self):
        """'landed' e 'base_area': colpiti, e solo dopo l'atterraggio."""
        hit = total = 0

        for scenario, outcome in self.runs['landed'] + self.runs['base_area']:
            migs = _mig_ids(scenario)
            landing = _landing_time(scenario)
            on_migs = [e for e in outcome.damage_events if e.target_id in migs]
            self.assertTrue(on_migs, outcome.session_id)
            self.assertTrue(all(e.time >= landing for e in on_migs), outcome.session_id)
            hit += len(_hit(outcome, migs))
            total += len(migs)

        self.assertGreaterEqual(hit / total, MIN_HIT_FRACTION)

    def test_final_postures(self):
        expected = {'parked': MA.OFF_SCENE_POSTURE, 'airborne': MA.OFF_SCENE_POSTURE,
                    'landed': MA.PARKED_POSTURE, 'no_base': MA.OFF_SCENE_POSTURE,
                    'base_area': MA.PARKED_POSTURE}

        for variant, pairs in self.runs.items():
            for scenario, outcome in pairs:
                for mig in _mig_ids(scenario):
                    self.assertEqual(outcome.postures[mig], expected[variant], outcome.session_id)

                self.assertEqual(outcome.postures[f'{BASE}/fuel0'], MA.GROUND_DEFENSE_POSTURE)


if __name__ == '__main__':
    unittest.main()
