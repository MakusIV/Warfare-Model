"""Scenario S30 del motore di sessioni virtuali: il ciclo di campagna (F8, blocco 3).

Prosegue `Test_Session_Scenarios.py` (S1-S9) e gli S10-S29 con la stessa disciplina: si verifica
un comportamento QUALITATIVO o STRUTTURALE, mai un numero calibrato. Le uniche novita' numeriche
sono le STIME di progetto della tabella di turnaround/riparazione (`Context/Context`, §4.4,
sostituite dalla ricerca F8-R) e le posizioni dello scenario dichiarate qui sotto; il test calcola
gli istanti dalle costanti e dal registro, mai scrivendoli a mano.

## S30-CAMPAIGN (`TestS30CampaignSequence`)

Una sequenza di 4 sessioni disgiunte condotte da `Logic/Session_Campaign.run_campaign_session`
(che esegue i processi di campagna fra sessioni, valida l'ordine, esegue `SS.run_session`, applica
le posizioni finali e registra la sessione nel `CampaignLedger`). **Nessun contatto**: nessuna
estrazione RNG, la storia dipende solo da geometria, tempi e costanti di prontezza.

Forze (scelte di dettaglio dell'esecutore, come da §4.4):
  * `Blue-Base` — base aerea Blue (Military `AIR_UNIT`) con un deposito `Structure` 'Farp'
    ('Oil_Tank', il riferimento d'atterraggio) in (0, 0);
  * `Blue-Wing` — 2 F-16C Block 52d 'Strike' parcheggiati sulla base (f0 in (0,0,0), f1 in
    (0,150,0), come i MiG di S22-AIR 'parked'); missione ad anello DEPARTURE (base) ->
    NAV (100 km, 0, 5000 m) -> LAND (base), partenza dal parcheggio (`PARKING_COLD`), alla
    velocita' nominale del registro; carburante del loadout, sopra il minimo G1;
  * `Blue-Mech` — 2 M1A2-Abrams in (0, -20 km) e (0, -19,8 km): `mbt0` in missione 'Movement'
    (POSITIONING, bersaglio POINT sulla destinazione) fino a (10 km, -20 km) alla velocita'
    nominale del registro; `mbt1` senza missione e danneggiato prima della prima sessione
    (`health = 60`, danno anteriore al registro);
  * `Red-Depot` — blocco Red con una struttura a (300 km, 0): nessun sensore utile, nessun contatto.

Sequenza (gli istanti sono calcolati dalle costanti e dal registro, mai scritti a mano):
  1. `S30-CAMPAIGN-1` in `[0, 7200]`: le due missioni. `mbt0` a (10 km, -20 km) in
     `final_positions` e in `asset.position`; F-16C a terra sulla base (`parking_cold`); registro:
     F-16C pronti a `movement_ends + turnaround` (Fighter), `mbt0` a `arrivo + GROUND_TURNAROUND_S`,
     `mbt1` a `7200 + repair_s` (riparazione in corso, salute 60).
  2. Sessione 2 a `t2 = ledger.last_end` (finestra di 2 h). Un ordine con una missione per `mbt0`
     e' RIFIUTATO (`ASSET_NOT_READY`); `ready_assets` a `t2` non da' nessuno dei quattro. Poi
     `S30-CAMPAIGN-2` senza missioni: `final_positions['mbt0']` resta (10 km, -20 km) perche'
     `apply_final_positions` della sessione 1 ha spostato l'asset (posizione ripresa), `mbt1`
     salute 60.
  3. `S30-CAMPAIGN-3` a `t3 = max(ledger.last_end, ledger.ready_at('mbt0'))`: `mbt0` rifornito
     (carburante = pieno) e pronto; missione da (10 km, -20 km) a (20 km, -20 km) costruita DOPO
     la sessione 2 con `F.missions_for` (legge `asset.position`: parte dalla posizione persistita),
     accettata; `mbt1` ancora in riparazione.
  4. `S30-CAMPAIGN-4` a `t4 = max(ledger.last_end, ledger.ready_at('mbt1'))`: `mbt1` riparato
     (salute 100), assente dal registro, impiegabile.

## S30-ABSENT (`TestS30AbsentForce`, difetto 26)

Stesse forze di S30-CAMPAIGN, una sola missione (`mbt0` verso (10 km, -20 km)), tre sessioni:
  1. `S30-ABSENT-1` in `[0, 7200]` con `Blue-Mech`: turnaround di `mbt0`, riparazione di `mbt1`.
  2. `S30-ABSENT-2` SENZA `Blue-Mech`, da `max(last_end, ready_at('mbt0'))`: il record di `mbt1`
     resta identico; `mbt1` resta non impiegabile (`ASSET_NOT_READY`) alla fine della sessione.
     [3b] il record concluso di `mbt0` resta e il rifornimento arriva al ritorno.
  3. `S30-ABSENT-3` di nuovo con `Blue-Mech`, da `max(last_end, ready_at('mbt1'))`: `mbt1` riparato
     (salute 100) e fuori dal registro.
Nessun contatto e nessuna estrazione RNG.

`Scenario_Baseline.UNITS`: in coda `('S30-CAMPAIGN', 'Test_Session_Scenarios_S30',
'TestS30CampaignSequence', None, _single_or_index)`. Quattro esecuzioni nuove
(`S30-CAMPAIGN/S30-CAMPAIGN-1..4`); la fotografia NON e' installata dall'esecutore.
Poi `('S30-ABSENT', 'Test_Session_Scenarios_S30', 'TestS30AbsentForce', None, _single_or_index)`:
tre esecuzioni nuove (`S30-ABSENT/S30-ABSENT-1..3`).
"""

import unittest

from sympy import Point3D

from Code.Dynamic_War_Manager.Source.Asset.Mobile import FUEL_FULL
from Code.Dynamic_War_Manager.Source.Command.Campaign_Types import (
    CampaignLedger,
    SessionRules,
    SessionValidationError,
    ViolationCode,
)
from Code.Dynamic_War_Manager.Source.Command.Mission_Types import (
    Mission,
    MissionAsset,
    MissionWaypoint,
    StartMode,
    Target,
    TargetKind,
    WaypointRole,
    route_waypoints,
)
from Code.Dynamic_War_Manager.Source.Command.Session_Types import SessionOrder
from Code.Dynamic_War_Manager.Source.Context.Campaign_State import CampaignState
from Code.Dynamic_War_Manager.Source.Context.Context import GROUND_TURNAROUND_S, REPAIR_TIME_FULL_S
from Code.Dynamic_War_Manager.Source.Context.Region import Region
from Code.Dynamic_War_Manager.Source.DataType.Edge import Edge
from Code.Dynamic_War_Manager.Source.DataType.Route import Route
from Code.Dynamic_War_Manager.Source.DataType.Waypoint import Waypoint
from Code.Dynamic_War_Manager.Source.Logic import Mission_Adapter as MA
from Code.Dynamic_War_Manager.Source.Logic import Readiness
from Code.Dynamic_War_Manager.Source.Logic import Session_Campaign
from Code.Dynamic_War_Manager.Source.Logic import Session_Validator
from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F

# ── Costanti di scenario (dichiarate di test) ─────────────────────────────────

BASE, WING, MECH, RED = 'Blue-Base', 'Blue-Wing', 'Blue-Mech', 'Red-Depot'
MBT0 = f'{MECH}/mbt0'
MBT1 = f'{MECH}/mbt1'
DEPOT_ID = f'{BASE}/depot0'

S1, S2, S3, S4 = 'S30-CAMPAIGN-1', 'S30-CAMPAIGN-2', 'S30-CAMPAIGN-3', 'S30-CAMPAIGN-4'
A1, A2, A3 = 'S30-ABSENT-1', 'S30-ABSENT-2', 'S30-ABSENT-3'

# Posizioni e quote [m] dello scenario (dichiarate, v. docstring).
BASE_ORIGIN = (0.0, 0.0)
WING_SPACING_M = 150.0                      # separazione fra i due F-16C sul piazzale (come S22-AIR)
NAV_POINT = (100_000.0, 0.0, 5_000.0)
MECH_Y = -20_000.0
MECH_STEP_M = 200.0                         # separazione fra mbt0 e mbt1
FIRST_DEST_X = 10_000.0
SECOND_DEST_X = 20_000.0
RED_ORIGIN = (300_000.0, 0.0)

# Campagna (data/ora di comodo per lo snapshot di CampaignState, non significative per il motore).
SNAPSHOT_DATE, SNAPSHOT_TIME = '2026-05-13', '08:00'


def _air_route(points, speed: float, name: str, reference=None) -> Route:
    """Rotta aerea (x, y, z) con l'ultimo waypoint riferito a `reference` (base d'atterraggio)."""
    waypoints = [Waypoint(name=f'{name}-W{i}', point=Point3D(*point),
                          obj_reference=reference if i == len(points) - 1 else None)
                 for i, point in enumerate(points)]
    edges = {(a.name, b.name): Edge(wpA=a, wpB=b, path_type='air', danger_level=0.0, speed=speed,
                                    name=f'{name}-E{i}')
             for i, (a, b) in enumerate(zip(waypoints, waypoints[1:]))}
    return Route(route_type='air', edges=edges, name=name)


def _loop_mission(wing, depot, cruise_speed: float) -> Mission:
    """Missione ad anello dell'ala: DEPARTURE (base) -> NAV (100 km) -> LAND (base), da parcheggio."""
    route = _air_route([BASE_ORIGIN, NAV_POINT, BASE_ORIGIN], cruise_speed, 'S30-loop', reference=depot)
    waypoints = route_waypoints(route)
    roles = [WaypointRole.DEPARTURE, WaypointRole.NAV, WaypointRole.LAND]
    ids = sorted(asset_id for asset_id, asset in wing.assets.items()
                 if type(asset).__name__ == 'Aircraft')
    # Formazione come S22-AIR 'parked': il gregario a 150 m sulla sinistra del capo.
    members = tuple(MissionAsset(asset_id, 'lead' if index == 0 else 'wingman',
                                 right_m=-WING_SPACING_M * index, loadout='Strike')
                    for index, asset_id in enumerate(ids))
    return Mission(mission_id=f'{WING}:Strike', block_id=WING, domain='air', mission_type='Strike',
                   assets=members, target=F.zone_target(NAV_POINT, 20_000.0), route=route,
                   waypoints=tuple(MissionWaypoint(wp, role) for wp, role in zip(waypoints, roles)),
                   start_time=0.0, start_mode=StartMode.PARKING_COLD)


def _movement_mission(mech, dest_x: float) -> Mission:
    """Missione 'Movement' (POSITIONING) del solo `mbt0` fino a (dest_x, MECH_Y)."""
    target = Target(kind=TargetKind.POINT, position=Point3D(dest_x, MECH_Y, 0.0))
    mission, = F.missions_for(mech, [(dest_x, MECH_Y)], mission_type='Movement', target=target,
                              only=[MBT0])
    return mission


def _mbt1_movement_mission(mech, dest_x: float) -> Mission:
    """Missione 'Movement' (POSITIONING) del solo `mbt1` verso (dest_x, MECH_Y) (offset di formazione di
    `routes_for`): serve solo a provare che l'ordine e' rifiutato (`ASSET_NOT_READY`)."""
    target = Target(kind=TargetKind.POINT, position=Point3D(dest_x, MECH_Y, 0.0))
    mission, = F.missions_for(mech, [(dest_x, MECH_Y)], mission_type='Movement', target=target,
                              only=[MBT1])
    return mission


def _build_forces():
    """Le forze dello scenario (ogni chiamata restituisce istanze nuove e indipendenti)."""
    base = F.build_force(BASE, 'Blue', [], mil_category=F.AIR_UNIT)
    F.add_assets(base, [F.make_structure(base, DEPOT_ID, BASE_ORIGIN, category='Farp',
                                         asset_type='Oil_Tank')])

    wing = F.build_force(WING, 'Blue', [
        F.Unit('aircraft', 'F-16C Block 52d', 2, origin=(*BASE_ORIGIN, 0.0), step=(0.0, WING_SPACING_M),
               prefix='f', loadout='Strike')], mil_category=F.AIR_UNIT)

    mech = F.build_force(MECH, 'Blue', [
        F.Unit('vehicle', 'M1A2-Abrams', 2, origin=(0.0, MECH_Y), step=(0.0, MECH_STEP_M), prefix='mbt')])
    # Danno anteriore al registro: riparazione in corso fin dalla prima sessione.
    mech.assets[MBT1].health = 60

    red = F.build_force(RED, 'Red', [], mil_category=F.AIR_UNIT)
    F.add_assets(red, [F.make_structure(red, f'{RED}/depot0', RED_ORIGIN, category='Farp',
                                        asset_type='Oil_Tank')])

    return base, wing, mech, red


def _assets_map(forces):
    """`{asset_id: asset}` di tutte le forze (stesso criterio di `Session_Campaign._assets_of`)."""
    assets = {}

    for force in forces:
        block = getattr(force, 'block', force)
        for asset_id, asset in (getattr(block, 'assets', None) or {}).items():
            assets[asset_id] = asset

    return assets


def _snapshot_of(forces):
    """Fotografia leggibile dello stato degli asset (posizione, carburante, scorta, salute)."""
    snap = {}

    for asset_id, asset in _assets_map(forces).items():
        position = asset.position
        snap[asset_id] = {
            'position': (float(position.x), float(position.y), float(position.z)),
            'fuel': None if getattr(asset, 'fuel', None) is None else float(asset.fuel),
            'stores': None if getattr(asset, 'stores', None) is None else dict(asset.stores),
            'health': asset.health,
        }

    return snap


def _region_of(forces, name: str = 'S30') -> Region:
    """Una `Region` reale con i blocchi delle forze (per `CampaignState`)."""
    region = Region(name)

    for force in forces:
        region.add_block(force)

    return region


class TestS30CampaignSequence(F.LoggerSilencer, unittest.TestCase):
    """S30-CAMPAIGN: prontezza, posizione persistente e riparazione nel ciclo di campagna (F8)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.rules = SessionRules()
        cls.base, cls.wing, cls.mech, cls.red = _build_forces()
        cls.forces_a = [cls.base, cls.wing, cls.mech]
        cls.forces_b = [cls.red]
        cls.fire_control = F.make_fire_control()

        cls.outcomes = {}
        cls.ledgers = {}
        cls.checkpoints = {}

        ledger = CampaignLedger()
        all_forces = cls.forces_a + cls.forces_b
        cruise = cls.wing.assets[f'{WING}/f0'].speed['nominal']

        # ── Sessione 1: le due missioni ────────────────────────────────────────
        t1_start, t1_end = cls.rules.window(0.0)
        order1 = SessionOrder(S1, t_start=t1_start, t_end=t1_end,
                              missions=(_loop_mission(cls.wing, cls.base.assets[DEPOT_ID], cruise),
                                        _movement_mission(cls.mech, FIRST_DEST_X)))
        outcome1, ledger = Session_Campaign.run_campaign_session(
            ledger, order1, cls.forces_a, cls.forces_b, cls.fire_control)
        cls.outcomes[S1], cls.ledgers[S1] = outcome1, ledger
        cls.checkpoints[S1] = _snapshot_of(all_forces)

        # Snapshot di CampaignState della posizione e del registro alla fine della sessione 1
        # (gli oggetti delle forze continueranno a mutare nelle sessioni successive: lo snapshot
        # li ha gia' copiati nei dizionari).
        cls.cs_after_1 = CampaignState()
        cls.cs_after_1.add_region_snapshot(S1, SNAPSHOT_DATE, SNAPSHOT_TIME, _region_of(all_forces))
        cls.cs_after_1.add_ledger(S1, ledger.to_dict())

        # ── Sessione 2: nessuna missione (posizione ripresa) ───────────────────
        t2 = ledger.last_end
        t2_start, t2_end = cls.rules.window(t2)
        order2 = SessionOrder(S2, t_start=t2_start, t_end=t2_end, missions=())
        outcome2, ledger = Session_Campaign.run_campaign_session(
            ledger, order2, cls.forces_a, cls.forces_b, cls.fire_control)
        cls.outcomes[S2], cls.ledgers[S2] = outcome2, ledger
        cls.checkpoints[S2] = _snapshot_of(all_forces)

        # ── Sessione 3: mbt0 rifornito e di nuovo in missione ────────────────
        t3 = max(ledger.last_end, ledger.ready_at(MBT0))
        t3_start, t3_end = cls.rules.window(t3)
        order3 = SessionOrder(S3, t_start=t3_start, t_end=t3_end,
                              missions=(_movement_mission(cls.mech, SECOND_DEST_X),))
        outcome3, ledger = Session_Campaign.run_campaign_session(
            ledger, order3, cls.forces_a, cls.forces_b, cls.fire_control)
        cls.outcomes[S3], cls.ledgers[S3] = outcome3, ledger
        cls.checkpoints[S3] = _snapshot_of(all_forces)

        # ── Sessione 4: mbt1 riparato ─────────────────────────────────────────
        t4 = max(ledger.last_end, ledger.ready_at(MBT1))
        t4_start, t4_end = cls.rules.window(t4)
        order4 = SessionOrder(S4, t_start=t4_start, t_end=t4_end, missions=())
        outcome4, ledger = Session_Campaign.run_campaign_session(
            ledger, order4, cls.forces_a, cls.forces_b, cls.fire_control)
        cls.outcomes[S4], cls.ledgers[S4] = outcome4, ledger
        cls.checkpoints[S4] = _snapshot_of(all_forces)

    # ── Test ──────────────────────────────────────────────────────────────────

    @staticmethod
    def _assert_point(test, got, want):
        test.assertAlmostEqual(float(got[0]), float(want[0]), delta=1e-6)
        test.assertAlmostEqual(float(got[1]), float(want[1]), delta=1e-6)
        test.assertAlmostEqual(float(got[2]), float(want[2]), delta=1e-6)

    def test_positions_persist(self):
        """La posizione finale della sessione 1 e' registrata e applicata; la sessione 2 la riprende
        (mbt0 fermo a (10 km, -20 km), non tornato a (0, -20 km)); la sessione 3 riparte da li'."""
        self._assert_point(self, self.outcomes[S1].final_positions[MBT0], (FIRST_DEST_X, MECH_Y, 0.0))
        self._assert_point(self, self.checkpoints[S1][MBT0]['position'], (FIRST_DEST_X, MECH_Y, 0.0))
        # Posizione ripresa nella sessione 2 (nessuna missione: resta dove l'aveva lasciato la 1).
        self._assert_point(self, self.outcomes[S2].final_positions[MBT0], (FIRST_DEST_X, MECH_Y, 0.0))
        self._assert_point(self, self.checkpoints[S2][MBT0]['position'], (FIRST_DEST_X, MECH_Y, 0.0))
        # La sessione 3 parte dalla posizione persistita e arriva a (20 km, -20 km).
        self._assert_point(self, self.outcomes[S3].final_positions[MBT0], (SECOND_DEST_X, MECH_Y, 0.0))

    def test_not_ready_asset_is_rejected(self):
        """Un asset in turnaround/riparazione non e' impiegabile: l'ordine e' rifiutato con
        `ASSET_NOT_READY` (precondizione: `ready_at('mbt0') > t2` con le stime di §4.4)."""
        t2 = self.ledgers[S1].last_end
        self.assertGreater(self.ledgers[S1].ready_at(MBT0), t2,
                           "precondizione del piano: con le stime di §4.4 mbt0 non e' pronto a t2; "
                           "se la ricerca F8-R la rendesse falsa va allungata la rotta della sessione 1")

        base, wing, mech, red = _build_forces()
        order = SessionOrder('S30-NOT-READY', t_start=t2, t_end=t2 + self.rules.default_duration_s,
                             missions=(_movement_mission(mech, FIRST_DEST_X),))

        with self.assertRaises(SessionValidationError) as raised:
            Session_Campaign.run_campaign_session(self.ledgers[S1], order, [base, wing, mech], [red],
                                                  F.make_fire_control())

        not_ready = [v for v in raised.exception.violations
                     if v.code is ViolationCode.ASSET_NOT_READY and v.asset_id == MBT0]
        self.assertTrue(not_ready, str(raised.exception))

    def test_aircraft_land_on_base(self):
        """Gli F-16C rientrano e restano a terra sulla base (`parking_cold`): la loro posizione
        finale e' quella di parcheggio di partenza (capo sul riferimento, gregario a 150 m)."""
        for index in (0, 1):
            asset_id = f'{WING}/f{index}'
            self.assertEqual(self.outcomes[S1].postures[asset_id], MA.PARKED_POSTURE, asset_id)
            self._assert_point(self, self.checkpoints[S1][asset_id]['position'],
                               (BASE_ORIGIN[0], -WING_SPACING_M * index, 0.0))

    def test_session1_readiness_records(self):
        """Il registro dopo la sessione 1 segue la regola di §4.4: ogni asset di missione parte dal
        rientro (`movement_ends`) e somma il turnaround (di classe per gli aerei, di terra per
        `mbt0`); `mbt1`, senza missione e gia' danneggiato, parte dalla fine nominale e somma solo
        la riparazione (lineare nel danno)."""
        assets = _assets_map(self.forces_a + self.forces_b)
        ledger, outcome = self.ledgers[S1], self.outcomes[S1]

        for index in (0, 1):
            asset_id = f'{WING}/f{index}'
            record = ledger.readiness[asset_id]
            turnaround, source = Readiness.turnaround_s(assets[asset_id])
            self.assertTrue(source.startswith('class:'), source)
            self.assertAlmostEqual(record.since, outcome.movement_ends[asset_id], delta=1e-6)
            self.assertAlmostEqual(record.turnaround_s, turnaround, delta=1e-6)
            self.assertAlmostEqual(record.ready_at, outcome.movement_ends[asset_id] + turnaround, delta=1e-6)

        record = ledger.readiness[MBT0]
        self.assertAlmostEqual(record.ready_at, outcome.movement_ends[MBT0] + GROUND_TURNAROUND_S, delta=1e-6)

        record = ledger.readiness[MBT1]
        repair = REPAIR_TIME_FULL_S['ground'] * (100 - 60) / 100.0
        self.assertAlmostEqual(record.since, outcome.t_end, delta=1e-6)
        self.assertAlmostEqual(record.repair_s, repair, delta=1e-6)
        self.assertAlmostEqual(record.ready_at, outcome.t_end + repair, delta=1e-6)

    def test_ready_assets(self):
        """`ready_assets` restituisce esattamente gli asset non distrutti e pronti a `t`: nessuno a
        t2; `mbt0` (e gli F-16C gia' atterrati) a t3, ma non `mbt1` ancora in riparazione."""
        assets = _assets_map(self.forces_a + self.forces_b)
        t2 = self.ledgers[S1].last_end
        t3 = max(self.ledgers[S2].last_end, self.ledgers[S2].ready_at(MBT0))

        expected_at = lambda t: tuple(asset_id for asset_id in sorted(assets)
                                      if self.ledgers[S1].is_ready(asset_id, t))
        self.assertEqual(Readiness.ready_assets(self.ledgers[S1], assets, t2), expected_at(t2))
        self.assertEqual(Readiness.ready_assets(self.ledgers[S2], assets, t3), expected_at(t3))
        self.assertIn(MBT0, expected_at(t3))
        self.assertNotIn(MBT1, expected_at(t3))

    def test_repair_in_progress_then_done(self):
        """`mbt1` resta danneggiato (salute 60) e in riparazione dalle sessioni 1 a 3, poi e'
        riparato (salute 100) e tolto dal registro all'inizio della sessione 4."""
        self.assertIn(MBT1, self.ledgers[S1].readiness)
        self.assertGreater(self.ledgers[S3].ready_at(MBT1), self.ledgers[S2].last_end,
                           "precondizione: mbt1 e' ancora in riparazione a t3")

        for stage in (S1, S2, S3):
            self.assertEqual(self.checkpoints[stage][MBT1]['health'], 60, stage)

        self.assertEqual(self.checkpoints[S4][MBT1]['health'], 100)
        self.assertNotIn(MBT1, self.ledgers[S4].readiness)

    def test_turnaround_rearms_and_refuels(self):
        """`mbt0` ha un turnaround previsto (rearm) ed e' rifornito all'inizio della sessione 3: il
        carburante torna al pieno del registro (poi consumato solo dalla rotta della sessione 3)."""
        record = self.ledgers[S1].readiness[MBT0]
        self.assertEqual(record.turnaround_s, GROUND_TURNAROUND_S)
        self.assertTrue(record.rearm)

        consumed_s1 = self.outcomes[S1].fuel_consumed().get(MBT0, 0.0)
        self.assertGreater(consumed_s1, 0.0, "premessa: mbt0 consuma carburante guidando")

        # Dopo la sessione 2 non e' ancora stato rifornito: pieno - consumo della sessione 1.
        self.assertAlmostEqual(self.checkpoints[S2][MBT0]['fuel'], FUEL_FULL - consumed_s1, delta=1e-9)

        # Dopo la sessione 3 e' stato rifornito e ha guidato SOLO la sessione 3 (non il doppio):
        # pieno - consumo della sessione 3, non pieno - consumo 1 - consumo 3.
        consumed_s3 = self.outcomes[S3].fuel_consumed().get(MBT0, 0.0)
        self.assertAlmostEqual(self.checkpoints[S3][MBT0]['fuel'], FUEL_FULL - consumed_s3, delta=1e-9)

        # La scorta per arma e' tornata a quella del registro (id a entrambe le sessioni).
        self.assertEqual(self.checkpoints[S3][MBT0]['stores'], self.checkpoints[S1][MBT0]['stores'])

    def test_sessions_are_disjoint(self):
        """Una sessione che parte prima della fine effettiva della precedente e' rifiutata
        (`SESSION_OVERLAP`)."""
        order = SessionOrder('S30-OVERLAP', t_start=0.0, t_end=self.rules.default_duration_s,
                             missions=())

        with self.assertRaises(SessionValidationError) as raised:
            Session_Validator.check_session(order, self.forces_a, self.forces_b,
                                            ledger=self.ledgers[S1])

        self.assertTrue(any(v.code is ViolationCode.SESSION_OVERLAP for v in raised.exception.violations),
                        str(raised.exception))

    def test_ledger_round_trip(self):
        """Il registro passa per `CampaignState.add_ledger`/`get_ledger` e `from_dict` identico."""
        data = self.cs_after_1.get_ledger(S1)
        self.assertIsNotNone(data)
        self.assertEqual(CampaignLedger.from_dict(data).to_dict(), self.ledgers[S1].to_dict())

    def test_restore_position(self):
        """`CampaignState.restore(..., restore_position=True)` riporta la posizione della sessione 1
        su forze ricostruite da zero."""
        base, wing, mech, red = _build_forces()
        region = _region_of([base, wing, mech, red])

        self.cs_after_1.restore(S1, [region], restore_position=True)

        self._assert_point(self, mech.assets[MBT0].position, (FIRST_DEST_X, MECH_Y, 0.0))


class TestS30AbsentForce(F.LoggerSilencer, unittest.TestCase):
    """S30-ABSENT: una forza assente da una sessione conserva i propri record di prontezza (difetto 26)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.rules = SessionRules()
        cls.base, cls.wing, cls.mech, cls.red = _build_forces()
        with_mech = [cls.base, cls.wing, cls.mech]
        without_mech = [cls.base, cls.wing]
        cls.forces_b = [cls.red]
        cls.fire_control = F.make_fire_control()
        all_forces = with_mech + cls.forces_b

        cls.outcomes, cls.ledgers, cls.checkpoints = {}, {}, {}
        ledger = CampaignLedger()

        # Sessione 1: Blue-Mech presente; mbt0 in missione (turnaround), mbt1 gia' danneggiato (riparazione).
        t1_start, t1_end = cls.rules.window(0.0)
        order1 = SessionOrder(A1, t_start=t1_start, t_end=t1_end,
                              missions=(_movement_mission(cls.mech, FIRST_DEST_X),))
        outcome1, ledger = Session_Campaign.run_campaign_session(
            ledger, order1, with_mech, cls.forces_b, cls.fire_control)
        cls.outcomes[A1], cls.ledgers[A1] = outcome1, ledger
        cls.checkpoints[A1] = _snapshot_of(all_forces)

        # Sessione 2: Blue-Mech ASSENTE, dalla fine del turnaround di mbt0 (processo concluso
        # mentre la forza e' assente); la riparazione di mbt1 e' ancora in corso.
        cls.t2 = max(ledger.last_end, ledger.ready_at(MBT0))
        t2_start, t2_end = cls.rules.window(cls.t2)
        order2 = SessionOrder(A2, t_start=t2_start, t_end=t2_end, missions=())
        outcome2, ledger = Session_Campaign.run_campaign_session(
            ledger, order2, without_mech, cls.forces_b, cls.fire_control)
        cls.outcomes[A2], cls.ledgers[A2] = outcome2, ledger
        cls.checkpoints[A2] = _snapshot_of(all_forces)

        # Sessione 3: Blue-Mech di nuovo presente, alla fine prevista della riparazione di mbt1
        # (senza il suo record, prima della correzione, si ripiega sulla fine della sessione 2).
        ready_mbt1 = ledger.ready_at(MBT1)
        cls.t3 = ledger.last_end if ready_mbt1 is None else max(ledger.last_end, ready_mbt1)
        t3_start, t3_end = cls.rules.window(cls.t3)
        order3 = SessionOrder(A3, t_start=t3_start, t_end=t3_end, missions=())
        outcome3, ledger = Session_Campaign.run_campaign_session(
            ledger, order3, with_mech, cls.forces_b, cls.fire_control)
        cls.outcomes[A3], cls.ledgers[A3] = outcome3, ledger
        cls.checkpoints[A3] = _snapshot_of(all_forces)

    # ── Test ──────────────────────────────────────────────────────────────────

    def test_absent_force_keeps_pending_record(self):
        """Il record di riparazione di `mbt1` attraversa la sessione 2 (forza assente) identico:
        non e' perso, ne' ripartito, ne' esteso."""
        self.assertNotIn(MBT1, self.outcomes[A2].postures)
        self.assertIn(MBT1, self.ledgers[A2].readiness)
        self.assertEqual(self.ledgers[A2].readiness[MBT1], self.ledgers[A1].readiness[MBT1])

    def test_absent_asset_still_not_ready(self):
        """Alla fine della sessione 2 `mbt1` e' ancora in riparazione: un ordine con una sua
        missione e' RIFIUTATO (`ASSET_NOT_READY`)."""
        self.assertGreater(self.ledgers[A1].ready_at(MBT1), self.ledgers[A2].last_end,
                           "precondizione: mbt1 e' ancora in riparazione alla fine della sessione 2 "
                           "con i tempi di Context; se non lo fosse va rivista la sequenza di S30-ABSENT")

        base, wing, mech, red = _build_forces()
        order = SessionOrder('S30-ABSENT-NOT-READY', t_start=self.ledgers[A2].last_end,
                             t_end=self.ledgers[A2].last_end + self.rules.default_duration_s,
                             missions=(_mbt1_movement_mission(mech, FIRST_DEST_X),))

        with self.assertRaises(SessionValidationError) as raised:
            Session_Campaign.run_campaign_session(self.ledgers[A2], order, [base, wing, mech], [red],
                                                  F.make_fire_control())

        not_ready = [v for v in raised.exception.violations
                     if v.code is ViolationCode.ASSET_NOT_READY and v.asset_id == MBT1]
        self.assertTrue(not_ready, str(raised.exception))

    def test_repair_continues_across_absence(self):
        """La sessione 3 parte alla fine della riparazione registrata nella sessione 1 (non
        ripartita), e `mbt1` ne esce riparato e fuori dal registro."""
        self.assertAlmostEqual(self.t3, self.ledgers[A1].ready_at(MBT1), delta=1e-6)
        self.assertEqual(self.checkpoints[A1][MBT1]['health'], 60)
        self.assertEqual(self.checkpoints[A2][MBT1]['health'], 60)
        self.assertEqual(self.checkpoints[A3][MBT1]['health'], 100)
        self.assertNotIn(MBT1, self.ledgers[A3].readiness)

    def test_concluded_process_of_absent_asset(self):
        """Il turnaround di `mbt0` finisce mentre la forza e' assente: il record resta (non e'
        applicato) e il rifornimento arriva al ritorno, nella sessione 3."""
        self.assertLessEqual(self.ledgers[A1].ready_at(MBT0), self.t2 + 1e-9,
                             "precondizione: il turnaround di mbt0 finisce mentre la forza e' assente")
        consumed_1 = self.outcomes[A1].fuel_consumed().get(MBT0, 0.0)
        self.assertGreater(consumed_1, 0.0, "premessa: mbt0 consuma carburante guidando")

        self.assertEqual(self.ledgers[A2].readiness[MBT0], self.ledgers[A1].readiness[MBT0])
        self.assertAlmostEqual(self.checkpoints[A2][MBT0]['fuel'], FUEL_FULL - consumed_1, delta=1e-9)
        self.assertAlmostEqual(self.checkpoints[A3][MBT0]['fuel'], FUEL_FULL, delta=1e-9)
        self.assertNotIn(MBT0, self.ledgers[A3].readiness)


if __name__ == '__main__':
    unittest.main()
