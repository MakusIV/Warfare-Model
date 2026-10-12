"""Scenario S25 del motore di sessioni virtuali: criteri di fine di attivita' e stato di missione (F6-B1).

Prosegue `Test_Session_Scenarios.py` (S1-S9), `Test_Session_Scenarios_S10_S18.py`, gli S19-S24 con la
stessa disciplina: si verifica un comportamento QUALITATIVO o STRUTTURALE, mai un numero calibrato.

Criterio "Fatto quando" della Fase 6 di `Analysis/Document/Piano_Implementazione_Missione.md`: *un asset
winchester smette di sparare e lo registra come motivo di fine*. Decisioni dell'utente (D2.a/D2.d, F6-B1),
v. `Logic/Session_Simulator`, "Fine di attivita' e stato di missione", e `Logic/Engagement_Resolver`,
"Fine di attivita'":
  * un criterio di stato DICHIARATO in `EndCriteria` chiude l'ATTIVITA' dell'asset senza cambiarne la
    rotta: niente nuove salve offensive (quelle partite arrivano), l'asset prosegue PASSIVO sulla rotta
    pianificata, presente e bersaglio; il motivo e l'istante sono nell'esito per asset;
  * stato di missione con la regola unica DESTROYED > COMPLETED > ABORTED(motivo) > FAILED;
  * un asset distrutto ha postura `destroyed` nell'esito (`F6_DESTROYED_POSTURE`).
Ogni scenario ha due varianti di CONTROLLO: il criterio non dichiarato ('undeclared') e il criterio
dichiarato con l'interruttore `Session_Simulator.F6_END_CRITERIA` spento ('switch_off').

## S25-WIN: winchester (`TestS25Winchester`)

Blue-Sweep: un F-16C 'CAP' a 6000 m da x = -60 km a x = +60 km a 250 m/s (480 s), sensore 'air'
DICHIARATO di 30 km, scorta per arma IMPOSTA `{'AIM-9M': 2, 'M61A1': 500}` (2 missili aria-aria, il
cannone): la fire control gli da' prima l'AIM-9M, poi il cannone (`ShotSpec` di test SENZA effetto,
precisione 0, cosi' i bersagli restano e il tiratore ha sempre bersagli). Red-Package: 3 MiG-29S in
parallelo 10 km a nord, stessa rotta e velocita' (contatto per tutta la rotta); il primo ('fighter',
sensore 'air' di 30 km) lancia salve di test senza effetto contro Blue, gli altri due non sparano.
  * 'winchester': `EndCriteria(winchester=('MISSILES_AAM',))`: due salve (gli AIM-9M), poi nessuna
    (il cannone resta a bordo), motivo WINCHESTER all'istante della seconda; Red continua a lanciargli
    contro; missione ABORTED per munizioni;
  * 'undeclared' / 'switch_off': dopo i due missili il cannone continua; missione COMPLETED.

## S25-DMG: soglia di danno (`TestS25DamageThreshold`)

Blue-Armor: un M1A2 da (-3 km, -1,5 km) a (-3 km, +1,5 km) a 2 m/s (1500 s), sensore 'ground' 4,2 km,
tiro di test SENZA effetto contro Red. Red-Post: 3 BMP-2 intorno a (0, 0), sensore 'ground' 4,2 km, tiro
di test a precisione 1 e capacita' distruttiva 0 (ogni colpo e' un DAMAGE da 1 punto, mai un KILL, 5
colpi a salva) e scorta di 5 unita' ciascuno (una salva): al piu' 15 punti, il carro non e' mai distrutto.
  * 'damage': `EndCriteria(damage_threshold=0.05)`: alla prima salva Red a segno (5 punti) il carro
    chiude l'attivita' (DAMAGE), non spara piu', e' DAMAGED; missione ABORTED per danno;
  * 'undeclared' / 'switch_off': il carro continua a sparare; rotta completata, COMPLETED.

## S25-TGT: bersaglio distrutto (`TestS25TargetDestroyed`)

Blue-Strike: 2 F-16C 'strike' (tabella di riferimento: 'agm' contro le strutture) a 3000 m da x = -40 km a
x = +40 km a 250 m/s, sensore 'ground' 10 km. Red-Depot (il BERSAGLIO GROUP della missione): un
deposito in (0, 1 km); Red-Other: 2 depositi in (2 km, -1 km) e (2,5 km, -1 km). Dottrina senza
disingaggio (erosione e shock a 1) per non far "ritirare" i depositi.
  * 'target': `EndCriteria(target_destroyed=True)`: distrutto il deposito bersaglio, nessun lancio
    successivo (Red-Other non e' piu' attaccato), motivo TARGET_DESTROYED, missione COMPLETED; il
    deposito distrutto ha postura `destroyed`;
  * 'undeclared' / 'switch_off': lo strike continua su Red-Other.

## S25-DUR: durata massima (`TestS25MaxDuration`)

La geometria di S25-WIN con il tiro di riferimento 'fighter' reso SENZA effetto e senza limiti di scorta:
  * 'duration': `EndCriteria(max_duration_s=120)`: nessun lancio Blue dopo 120 s dalla partenza, motivo
    MAX_DURATION a 120 s, fine regolare: COMPLETED;
  * 'undeclared' / 'switch_off': Blue lancia per tutta la rotta.

## S25-POST: postura `destroyed` (`TestS25DestroyedPosture`)

La geometria di S25-WIN con il tiro di riferimento 'fighter' LETALE ('aam') e Red che non spara:
  * 'on': ogni asset distrutto ha postura `destroyed`, gli altri l'etichetta di sempre (`off_scene` a
    fine rotta);
  * 'posture_off' (`F6_DESTROYED_POSTURE` spento): nessuna postura `destroyed`.

Asserzioni: invarianti per replica (istanti, motivi, esiti) e frazioni aggregate con soglie DICHIARATE
(stime di test, non tarate sul risultato; v. sotto).
"""

import dataclasses
import unittest
from unittest.mock import patch

from Code.Dynamic_War_Manager.Source.Command.Mission_Types import (
    AbortReason,
    AssetEndReason,
    AssetState,
    EndCriteria,
    MissionStatus,
)
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic import Mission_Adapter as MA
from Code.Dynamic_War_Manager.Source.Logic import Session_Simulator as SS
from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F

DURATION = 1_800.0
SEEDS_PER_SCENARIO = 8
CONTROLS = ('undeclared', 'switch_off')

# Soglie delle frazioni aggregate sui seed: DICHIARATE di test, non tarate sul risultato (stesse stime di
# S22-S24: il rilevamento e' una estrazione per finestra e osservatore; con finestre lunghe e piu'
# osservatori il tiro e' la regola, 0,5 = "la regola, non l'eccezione").
MIN_FIRING_FRACTION = 0.5

# ── Geometria aria-aria (S25-WIN, S25-DUR, S25-POST) [m, m/s], dichiarata di test ──
SWEEP, PACKAGE = 'Blue-Sweep', 'Red-Package'
AIR_ALTITUDE = 6_000.0
AIR_SPEED = 250.0
AIR_START_X, AIR_END_X = -60_000.0, 60_000.0
PACKAGE_OFFSET_Y = 10_000.0
AIR_SENSOR_RANGE = 30_000.0
# Scorta imposta dello sweep: 2 missili aria-aria e il cannone (valori di test, non un loadout).
SWEEP_STORES = {'AIM-9M': 2, 'M61A1': 500}
# Tiri DICHIARATI di test SENZA effetto (precisione 0): misurano chi lancia e quando.
AAM_SHOT = ER.ShotSpec(accuracy=0.0, destroy_capacity=0.8, rounds=1, weapon='AIM-9M', time_of_flight=20.0,
                       cycle_time=15.0)
GUN_SHOT = ER.ShotSpec(accuracy=0.0, destroy_capacity=0.5, rounds=1, weapon='M61A1', stock_per_round=50,
                       time_of_flight=2.0, cycle_time=10.0)
MARKER_AAM = dataclasses.replace(F.SHOTS['aam'], accuracy=0.0, weapon='test:marker_aam')
MAX_DURATION = 120.0

# ── Geometria terrestre (S25-DMG), dichiarata di test (come S22-S24) ──
ARMOR, POST = 'Blue-Armor', 'Red-Post'
GROUND_SENSOR_RANGE = 4_200.0
ARMOR_START, ARMOR_END = (-3_000.0, -1_500.0), (-3_000.0, 1_500.0)
ARMOR_SPEED = 2.0
RED_PLATOON_HALF_SPAN = 200.0
MARKER_DIRECT = dataclasses.replace(F.SHOTS['direct_fire'], accuracy=0.0, weapon='test:marker_direct')
# Colpo che graffia: sempre a segno, mai un KILL, 1 punto di salute a colpo (MIN_EFFECTIVE_HIT_DAMAGE).
SCRATCH_SHOT = ER.ShotSpec(accuracy=1.0, destroy_capacity=0.0, rounds=5, weapon='test:scratch',
                           time_of_flight=1.5, cycle_time=10.0)
RED_STORES = {'test:scratch_ammo': 5}
DAMAGE_THRESHOLD = 0.05

# ── Geometria dello strike (S25-TGT), dichiarata di test ──
STRIKE, DEPOT, OTHER = 'Blue-Strike', 'Red-Depot', 'Red-Other'
STRIKE_ALTITUDE = 3_000.0
STRIKE_START_X, STRIKE_END_X = -40_000.0, 40_000.0
STRIKE_SENSOR_RANGE = 10_000.0
DEPOT_POSITION = (0.0, 1_000.0)
OTHER_POSITIONS = ((2_000.0, -1_000.0), (2_500.0, -1_000.0))
FIGHT_ON = {'Blue': {'erosion': 1.0, 'shock': 1.0}, 'Red': {'erosion': 1.0, 'shock': 1.0}}


def _seeds(prefix: str, count: int = SEEDS_PER_SCENARIO):
    return [f'{prefix}-{index}' for index in range(count)]


def _launches_by(outcome, prefix: str):
    return [event for event in outcome.ammunition_events if event.asset_id.startswith(prefix + '/')]


def _with_criteria(mission, variant: str, **criteria):
    """Missione con i criteri dichiarati, salvo la variante di controllo 'undeclared'."""
    return mission if variant == 'undeclared' else dataclasses.replace(mission, end_criteria=EndCriteria(**criteria))


def _run(scenario: F.Scenario, session_id: str, variant: str, **kwargs):
    """Esegue lo scenario; 'switch_off' spegne `F6_END_CRITERIA`, 'posture_off' `F6_DESTROYED_POSTURE`."""
    with patch.multiple(SS, F6_END_CRITERIA=SS.F6_END_CRITERIA and variant != 'switch_off',
                        F6_DESTROYED_POSTURE=SS.F6_DESTROYED_POSTURE and variant != 'posture_off'):
        return scenario.run(session_id, **kwargs)


# ── Aria-aria: S25-WIN, S25-DUR, S25-POST ─────────────────────────────────────

def _air_scenario(variant: str, *, blue_shot, red_fires: bool, stores=None, **criteria) -> F.Scenario:
    sweep = F.build_force(SWEEP, 'Blue', [F.Unit('aircraft', 'F-16C Block 52d', 1,
                                                 origin=(AIR_START_X, 0.0, AIR_ALTITUDE), prefix='f',
                                                 sensors={'air': AIR_SENSOR_RANGE})], mil_category=F.AIR_UNIT)

    if stores is not None:
        for asset in sweep.assets.values():
            asset.stores = dict(stores)

    package = F.build_force(PACKAGE, 'Red', [F.Unit('aircraft', 'MiG-29S', 3,
                                                    origin=(AIR_START_X, PACKAGE_OFFSET_Y, AIR_ALTITUDE),
                                                    step=(1_000.0, 0.0), prefix='m',
                                                    sensors={'air': AIR_SENSOR_RANGE})], mil_category=F.AIR_UNIT)
    blue_mission, = F.missions_for(sweep, [(AIR_END_X, 0.0)], mission_type='Fighter_Sweep',
                                   target=F.zone_target((AIR_END_X, 0.0), AIR_SENSOR_RANGE), speed=AIR_SPEED)
    red_mission, = F.missions_for(package, [(AIR_END_X + 1_000.0, PACKAGE_OFFSET_Y)], mission_type='Strike',
                                  target=F.zone_target((AIR_END_X, PACKAGE_OFFSET_Y), 10_000.0), speed=AIR_SPEED)
    escort = f'{PACKAGE}/m0'
    roles = {**{asset_id: 'fighter' for asset_id in sweep.assets},
             **{asset_id: ('fighter' if asset_id == escort and red_fires else 'unarmed') for asset_id in package.assets}}
    overrides = {**{asset_id: {'air': blue_shot} for asset_id in sweep.assets}}

    if red_fires:
        overrides[escort] = {'air': MARKER_AAM}

    return F.Scenario(forces_a=[sweep], forces_b=[package],
                      missions=[_with_criteria(blue_mission, variant, **criteria), red_mission],
                      fire_control=F.make_fire_control(roles=roles, overrides=overrides), duration=DURATION,
                      roles=roles)


class _AirRuns:
    """Base condivisa (NON un TestCase): esecuzioni per variante e seed in `setUpClass`."""

    SEEDS = ()
    VARIANTS = ()
    JET = f'{SWEEP}/f0'
    MISSION = f'{SWEEP}:Fighter_Sweep'

    @classmethod
    def _scenario(cls, variant: str) -> F.Scenario:
        raise NotImplementedError

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                scenario = cls._scenario(variant)
                cls.runs[variant].append((_run(scenario, session_id, variant), scenario))

    def _firing(self, variant: str, after: float = float('-inf')) -> int:
        """Repliche in cui Blue lancia dopo l'istante `after`."""
        return sum(1 for outcome, _ in self.runs[variant]
                   if any(event.time > after for event in _launches_by(outcome, SWEEP)))


class TestS25Winchester(_AirRuns, F.LoggerSilencer, unittest.TestCase):
    """S25-WIN: esaurite le armi della categoria dichiarata l'asset smette di sparare e prosegue passivo."""

    SEEDS = _seeds('S25-WIN')
    VARIANTS = ('winchester',) + CONTROLS

    @classmethod
    def _scenario(cls, variant: str) -> F.Scenario:
        return _air_scenario(variant, blue_shot=(AAM_SHOT, GUN_SHOT), red_fires=True, stores=SWEEP_STORES,
                             winchester=('MISSILES_AAM',))

    def test_two_missiles_then_no_more_launches(self):
        """'winchester': solo i due AIM-9M, mai il cannone; nelle repliche in cui spara due salve la fine
        e' all'istante della seconda; la scorta del cannone resta intera."""
        for outcome, scenario in self.runs['winchester']:
            launches = _launches_by(outcome, SWEEP)
            self.assertTrue(all(event.weapon == 'AIM-9M' for event in launches), outcome.session_id)
            self.assertLessEqual(len(launches), 2, outcome.session_id)
            self.assertEqual(scenario.force(SWEEP).assets[self.JET].stores['M61A1'], SWEEP_STORES['M61A1'])

        fired_both = sum(1 for outcome, _ in self.runs['winchester'] if len(_launches_by(outcome, SWEEP)) == 2)
        self.assertGreaterEqual(fired_both / len(self.SEEDS), MIN_FIRING_FRACTION, fired_both)

    def test_without_the_criterion_the_gun_keeps_firing(self):
        """Controlli: dopo i due missili il cannone continua (scorta residua), nella maggior parte delle
        repliche; le due varianti di controllo sono la stessa storia."""
        for variant in CONTROLS:
            guns = sum(1 for outcome, _ in self.runs[variant]
                       if any(event.weapon == 'M61A1' for event in _launches_by(outcome, SWEEP)))
            self.assertGreaterEqual(guns / len(self.SEEDS), MIN_FIRING_FRACTION, (variant, guns))

        for (undeclared, _), (switch_off, _) in zip(self.runs['undeclared'], self.runs['switch_off']):
            self.assertEqual(undeclared.ammunition_events, switch_off.ammunition_events)

    def test_the_outcome_reports_winchester(self):
        """Esito: WINCHESTER all'istante della seconda salva, missione ABORTED per munizioni; l'aereo
        prosegue passivo fino in fondo (ETA dell'ultimo punto presente). Controlli: COMPLETED."""
        for outcome, _ in self.runs['winchester']:
            launches = _launches_by(outcome, SWEEP)

            if len(launches) < 2:
                continue

            mission = outcome.mission_outcomes[self.MISSION]
            asset = mission.asset_outcomes[self.JET]
            self.assertEqual((mission.status, mission.reason), (MissionStatus.ABORTED, AbortReason.AMMUNITION))
            self.assertEqual((asset.end_reason, asset.end_time), (AssetEndReason.WINCHESTER, launches[-1].time))
            self.assertIsNotNone(mission.actual_etas[-1])

        for variant in CONTROLS:
            for outcome, _ in self.runs[variant]:
                self.assertEqual(outcome.mission_outcomes[self.MISSION].status, MissionStatus.COMPLETED)

    def test_the_passive_aircraft_is_still_a_target(self):
        """Dopo la fine di attivita' la scorta Red continua a lanciare contro l'F-16C (bersaglio)."""
        engaged = 0

        for outcome, _ in self.runs['winchester']:
            launches = _launches_by(outcome, SWEEP)

            if len(launches) == 2:
                end = launches[-1].time
                engaged += any(e.time > end and e.target_id == self.JET for e in outcome.damage_events)

        self.assertGreaterEqual(engaged / len(self.SEEDS), MIN_FIRING_FRACTION, engaged)


class TestS25MaxDuration(_AirRuns, F.LoggerSilencer, unittest.TestCase):
    """S25-DUR: la durata massima chiude l'attivita' a partenza + durata (fine regolare)."""

    SEEDS = _seeds('S25-DUR')
    VARIANTS = ('duration',) + CONTROLS

    @classmethod
    def _scenario(cls, variant: str) -> F.Scenario:
        return _air_scenario(variant, blue_shot=MARKER_AAM, red_fires=False, max_duration_s=MAX_DURATION)

    def test_no_launch_after_the_duration(self):
        for outcome, _ in self.runs['duration']:
            self.assertTrue(all(e.time < MAX_DURATION for e in _launches_by(outcome, SWEEP)), outcome.session_id)

        self.assertGreaterEqual(self._firing('duration') / len(self.SEEDS), MIN_FIRING_FRACTION)

        for variant in CONTROLS:
            late = self._firing(variant, after=MAX_DURATION)
            self.assertGreaterEqual(late / len(self.SEEDS), MIN_FIRING_FRACTION, (variant, late))

    def test_the_outcome_reports_max_duration(self):
        for outcome, _ in self.runs['duration']:
            mission = outcome.mission_outcomes[self.MISSION]
            asset = mission.asset_outcomes[self.JET]
            self.assertEqual(mission.status, MissionStatus.COMPLETED)
            self.assertEqual((asset.end_reason, asset.end_time), (AssetEndReason.MAX_DURATION, MAX_DURATION))

        for variant in CONTROLS:
            for outcome, _ in self.runs[variant]:
                self.assertEqual(outcome.mission_outcomes[self.MISSION].asset_outcomes[self.JET].end_reason,
                                 AssetEndReason.ROUTE_COMPLETED)


class TestS25DestroyedPosture(_AirRuns, F.LoggerSilencer, unittest.TestCase):
    """S25-POST: un asset distrutto ha postura `destroyed` nell'esito (`F6_DESTROYED_POSTURE`)."""

    SEEDS = _seeds('S25-POST')
    VARIANTS = ('on', 'posture_off')

    @classmethod
    def _scenario(cls, variant: str) -> F.Scenario:
        return _air_scenario('undeclared', blue_shot=F.SHOTS['aam'], red_fires=False)

    def test_destroyed_assets_have_the_destroyed_posture(self):
        destroyed_total = 0

        for outcome, scenario in self.runs['on']:
            for asset_id, asset in scenario.force(PACKAGE).assets.items():
                if asset.is_destroyed():
                    destroyed_total += 1
                    self.assertEqual(outcome.postures[asset_id], MA.DESTROYED_POSTURE, outcome.session_id)
                else:
                    self.assertEqual(outcome.postures[asset_id], MA.OFF_SCENE_POSTURE, outcome.session_id)

        self.assertGreater(destroyed_total, 0)

    def test_without_the_switch_no_destroyed_posture(self):
        for outcome, scenario in self.runs['posture_off']:
            self.assertNotIn(MA.DESTROYED_POSTURE, set(outcome.postures.values()), outcome.session_id)

        for (on, _), (off, _) in zip(self.runs['on'], self.runs['posture_off']):
            self.assertEqual(on.damage_events, off.damage_events)


# ── Terra: S25-DMG ────────────────────────────────────────────────────────────

def _damage_scenario(variant: str) -> F.Scenario:
    post = F.build_force(POST, 'Red', [F.Unit('vehicle', 'BMP-2', 3, origin=(0.0, -RED_PLATOON_HALF_SPAN),
                                              step=(0.0, RED_PLATOON_HALF_SPAN), prefix='bmp',
                                              sensors={'ground': GROUND_SENSOR_RANGE})])
    armor = F.build_force(ARMOR, 'Blue', [F.Unit('vehicle', 'M1A2-Abrams', 1, origin=ARMOR_START, prefix='tank',
                                                 sensors={'ground': GROUND_SENSOR_RANGE})])

    for asset in post.assets.values():
        asset.stores = dict(RED_STORES)

    mission, = F.missions_for(armor, [ARMOR_END], mission_type='Attack', target=F.group_target(POST),
                              speed=ARMOR_SPEED)
    overrides = {**{asset_id: {'ground': MARKER_DIRECT} for asset_id in armor.assets},
                 **{asset_id: {'ground': SCRATCH_SHOT} for asset_id in post.assets}}
    return F.Scenario(forces_a=[armor], forces_b=[post],
                      missions=[_with_criteria(mission, variant, damage_threshold=DAMAGE_THRESHOLD)],
                      fire_control=F.make_fire_control(overrides=overrides), duration=DURATION)


class TestS25DamageThreshold(F.LoggerSilencer, unittest.TestCase):
    """S25-DMG: oltre la soglia di danno l'asset chiude l'attivita' (mission kill) senza essere distrutto."""

    SEEDS = _seeds('S25-DMG')
    VARIANTS = ('damage',) + CONTROLS
    TANK = f'{ARMOR}/tank0'
    MISSION = f'{ARMOR}:Attack'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                scenario = _damage_scenario(variant)
                cls.runs[variant].append((_run(scenario, session_id, variant), scenario))

    def _first_hit(self, outcome):
        hits = [e.time for e in outcome.damage_events if e.target_id == self.TANK and e.health_after < e.health_before]
        return min(hits) if hits else None

    def test_the_damaged_tank_stops_firing(self):
        """Dalla prima risoluzione Red a segno il carro non lancia piu' (un lancio nello stesso istante
        precede la risoluzione); nei controlli continua nella maggior parte delle repliche."""
        hit = 0

        for outcome, _ in self.runs['damage']:
            first = self._first_hit(outcome)

            if first is None:
                continue

            hit += 1
            self.assertTrue(all(e.time <= first for e in _launches_by(outcome, ARMOR)), outcome.session_id)

        self.assertGreaterEqual(hit / len(self.SEEDS), MIN_FIRING_FRACTION, hit)

        for variant in CONTROLS:
            late = sum(1 for outcome, _ in self.runs[variant]
                       if self._first_hit(outcome) is not None
                       and any(e.time > self._first_hit(outcome) for e in _launches_by(outcome, ARMOR)))
            self.assertGreaterEqual(late / len(self.SEEDS), MIN_FIRING_FRACTION, (variant, late))

    def test_the_outcome_reports_damage(self):
        """Esito: DAMAGED con motivo DAMAGE alla prima risoluzione a segno, NON distrutto, missione
        ABORTED per danno; controlli: rotta completata, COMPLETED."""
        for outcome, scenario in self.runs['damage']:
            first = self._first_hit(outcome)

            if first is None:
                continue

            mission = outcome.mission_outcomes[self.MISSION]
            asset = mission.asset_outcomes[self.TANK]
            self.assertEqual((mission.status, mission.reason), (MissionStatus.ABORTED, AbortReason.DAMAGE))
            self.assertEqual((asset.state, asset.end_reason, asset.end_time),
                             (AssetState.DAMAGED, AssetEndReason.DAMAGE, first))
            self.assertFalse(scenario.force(ARMOR).assets[self.TANK].is_destroyed())

        for variant in CONTROLS:
            for outcome, _ in self.runs[variant]:
                mission = outcome.mission_outcomes[self.MISSION]
                self.assertEqual(mission.status, MissionStatus.COMPLETED, (variant, outcome.session_id))
                self.assertEqual(mission.asset_outcomes[self.TANK].end_reason, AssetEndReason.ROUTE_COMPLETED)


# ── Strike: S25-TGT ───────────────────────────────────────────────────────────

def _target_scenario(variant: str) -> F.Scenario:
    strike = F.build_force(STRIKE, 'Blue', [F.Unit('aircraft', 'F-16C Block 52d', 2,
                                                   origin=(STRIKE_START_X, 0.0, STRIKE_ALTITUDE), step=(0.0, 500.0),
                                                   prefix='s', sensors={'ground': STRIKE_SENSOR_RANGE})],
                           mil_category=F.AIR_UNIT)
    depot = F.make_force(DEPOT, 'Red', F.AIR_UNIT)
    F.add_assets(depot, [F.make_structure(depot, f'{DEPOT}/depot0', DEPOT_POSITION, category='Farp',
                                          asset_type='Oil_Tank')])
    other = F.make_force(OTHER, 'Red', F.AIR_UNIT)
    F.add_assets(other, [F.make_structure(other, f'{OTHER}/depot{index}', position, category='Farp',
                                          asset_type='Oil_Tank') for index, position in enumerate(OTHER_POSITIONS)])
    mission, = F.missions_for(strike, [(STRIKE_END_X, 0.0)], mission_type='Strike', target=F.group_target(DEPOT),
                              speed=AIR_SPEED)
    roles = {asset_id: 'strike' for asset_id in strike.assets}
    return F.Scenario(forces_a=[strike], forces_b=[depot, other],
                      missions=[_with_criteria(mission, variant, target_destroyed=True)],
                      fire_control=F.make_fire_control(roles=roles), duration=DURATION, roles=roles)


class TestS25TargetDestroyed(F.LoggerSilencer, unittest.TestCase):
    """S25-TGT: distrutto il bersaglio della missione gli asset non ingaggiano altro e la missione e'
    COMPLETED."""

    SEEDS = _seeds('S25-TGT')
    VARIANTS = ('target',) + CONTROLS
    TARGET = f'{DEPOT}/depot0'
    MISSION = f'{STRIKE}:Strike'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                scenario = _target_scenario(variant)
                cls.runs[variant].append((_run(scenario, session_id, variant, thresholds=FIGHT_ON), scenario))

    def _destroyed_at(self, outcome):
        times = [e.time for e in outcome.damage_events if e.target_id == self.TARGET and e.destroyed]
        return min(times) if times else None

    def test_no_launch_after_the_target_is_destroyed(self):
        destroyed = 0

        for outcome, _ in self.runs['target']:
            at = self._destroyed_at(outcome)

            if at is None:
                continue

            destroyed += 1
            self.assertTrue(all(e.time <= at for e in _launches_by(outcome, STRIKE)), outcome.session_id)

        self.assertGreaterEqual(destroyed / len(self.SEEDS), MIN_FIRING_FRACTION, destroyed)

        for variant in CONTROLS:
            later = sum(1 for outcome, _ in self.runs[variant]
                        if self._destroyed_at(outcome) is not None
                        and any(e.time > self._destroyed_at(outcome) for e in _launches_by(outcome, STRIKE)))
            self.assertGreaterEqual(later / len(self.SEEDS), MIN_FIRING_FRACTION, (variant, later))

    def test_the_outcome_reports_target_destroyed(self):
        """Esito: COMPLETED, ogni asset TARGET_DESTROYED all'istante della distruzione; il deposito
        distrutto ha postura `destroyed`. Senza distruzione: FAILED (la rotta non e' l'obiettivo)."""
        for outcome, _ in self.runs['target']:
            at = self._destroyed_at(outcome)
            mission = outcome.mission_outcomes[self.MISSION]

            if at is None:
                self.assertEqual(mission.status, MissionStatus.FAILED, outcome.session_id)
                continue

            self.assertEqual(mission.status, MissionStatus.COMPLETED)
            self.assertEqual(outcome.postures[self.TARGET], MA.DESTROYED_POSTURE)

            for asset in mission.asset_outcomes.values():
                self.assertEqual((asset.end_reason, asset.end_time), (AssetEndReason.TARGET_DESTROYED, at))

        for variant in CONTROLS:
            for outcome, _ in self.runs[variant]:
                mission = outcome.mission_outcomes[self.MISSION]
                self.assertEqual(mission.status, MissionStatus.COMPLETED, (variant, outcome.session_id))
                self.assertEqual({a.end_reason for a in mission.asset_outcomes.values()},
                                 {AssetEndReason.ROUTE_COMPLETED})


if __name__ == '__main__':
    unittest.main()
