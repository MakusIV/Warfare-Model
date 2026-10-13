"""Scenario S26 del motore di sessioni virtuali: bingo a priori e bingo in volo con rientro (F6-B2).

Prosegue `Test_Session_Scenarios.py` (S1-S9), `Test_Session_Scenarios_S10_S18.py`, gli S19-S25 con la
stessa disciplina: si verifica un comportamento QUALITATIVO o STRUTTURALE, mai un numero calibrato.

Decisione 14 dell'utente (2026-10-12, deviazione 14 del Piano), passo F6-B2, v. `Logic/Session_Simulator`,
"Bingo", `Logic/Fuel_Model`, "Bingo", e `Logic/Mission_Adapter`, "Bingo a priori":
  * **a priori** (validatore di pianificazione `Mission_Adapter.check_mission_bingo`): una missione aerea
    che non rientra con la riserva (`Fuel_Model.BINGO_RESERVE`) alla base idonea piu' vicina e' RIFIUTATA
    con un motivo esplicito; senza base idonea del lato e' rifiutata; con `EndCriteria.bingo` False non e'
    controllata;
  * **in volo** (`Session_Simulator.F6_BINGO`): l'aereo che arriva al bingo torna in linea retta alla base
    del lato piu' vicina, smette di lanciare, atterra e resta a terra; esito BINGO, missione ABORTED(BINGO);
  * senza base idonea o con `bingo` False valgono le regole della F6-A (a secco: planata o perdita).
Il validatore e l'esecutore usano lo stesso criterio (`Fuel_Model.bingo_point`): la missione rifiutata a
priori e' esattamente quella che in sessione torna al bingo.

## S26-BINGO (`TestS26Bingo`)

Blue-Flight: un F-16C 'Strike' (ruolo 'unarmed', autonomia di crociera del registro col loadout 'Strike')
in volo a 5000 m da (10 km, 0) verso (310 km, 0) a 250 m/s (1200 s). Blue-Base: base aerea (Military
'Airbase') con un deposito in (0, 0). Red-Site: un BMP-2 in (260 km, 0) con sensore 'air' DICHIARATO di
40 km e tiro DICHIARATO senza effetto (precisione 0) contro gli aerei: misura se e quando l'F-16C passa
nel suo raggio, senza che una distruzione lo tolga di scena. Varianti per seed:
  * 'bingo': carburante `BINGO_FUEL` = 0,3 del pieno: bingo a ~162 km (t ~608 s), rientro sulla base,
    atterraggio a ~1215 s con la riserva a bordo; Red non lo vede mai; il validatore rifiuta la missione;
  * 'none': pieno: nessun bingo, rotta completata, Red spara nella maggior parte delle repliche; il
    validatore accetta;
  * 'switch_off': come 'bingo' con `F6_BINGO` spento: rotta completata (il carburante basta per la sola
    andata), Red spara come in 'none' (il comportamento di prima);
  * 'no_base': carburante `DRY_FUEL` = 0,15 e nessuna base Blue: nessun bingo possibile, l'aereo si esaurisce
    a ~245,5 km e, senza base raggiungibile in planata, e' perso (F6-A); il validatore rifiuta (nessuna base);
  * 'bingo_off': carburante `DRY_FUEL` con la base, ma la missione dichiara `EndCriteria(bingo=False)`:
    nessun rientro, esaurimento e perdita come 'no_base' (base a ~245 km, oltre il raggio di planata); il
    validatore non la controlla.

Asserzioni: invarianti per replica (istanti, punti, esiti, eventi) e frazioni aggregate con soglie
DICHIARATE (stime di test, non tarate sul risultato; v. sotto).
"""

import dataclasses
import math
import unittest
from unittest.mock import patch

from Code.Dynamic_War_Manager.Source.Command.Mission_Types import (
    AbortReason,
    AssetEndReason,
    AssetState,
    EndCriteria,
    MissionStatus,
)
from Code.Dynamic_War_Manager.Source.Logic import Contact_Scheduler as CS
from Code.Dynamic_War_Manager.Source.Logic import Fuel_Model as FM
from Code.Dynamic_War_Manager.Source.Logic import Mission_Adapter as MA
from Code.Dynamic_War_Manager.Source.Logic import Session_Simulator as SS
from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F

DURATION = 3_600.0
SEEDS_PER_SCENARIO = 8

# ── Costanti di S26-BINGO [m, m/s, s], dichiarate di test (come S24) ──────────────
FLIGHT, BASE, SITE = 'Blue-Flight', 'Blue-Base', 'Red-Site'
FLIGHT_ALTITUDE = 5_000.0
AIR_SPEED = 250.0
FLIGHT_START, FLIGHT_END = (10_000.0, 0.0), (310_000.0, 0.0)
BASE_POSITION = (0.0, 0.0)
SITE_POSITION = (260_000.0, 0.0)
SITE_SENSOR_RANGE = 40_000.0
# Carburante dell'F-16C [frazione del pieno]: valori di test, non dati. 0,3 basta per l'andata (300 km) ma
# non per l'andata e il rientro con la riserva; 0,15 non basta nemmeno per l'andata.
BINGO_FUEL = 0.3
DRY_FUEL = 0.15
MARKER_SHOT = dataclasses.replace(F.SHOTS['sam'], accuracy=0.0, weapon='test:marker')

# Soglia delle frazioni aggregate sui seed: DICHIARATA di test, non tarata sul risultato (stessa stima di
# S22-S25: il rilevamento e' un'estrazione per finestra e osservatore, 0,5 = "la regola, non l'eccezione").
MIN_FIRING_FRACTION = 0.5


def _seeds(prefix: str, count: int = SEEDS_PER_SCENARIO):
    return [f'{prefix}-{index}' for index in range(count)]


def _shots_by(outcome, prefix: str):
    return [event for event in outcome.ammunition_events if event.asset_id.startswith(prefix + '/')]


def _scenario(variant: str) -> F.Scenario:
    flight = F.build_force(FLIGHT, 'Blue', [F.Unit('aircraft', 'F-16C Block 52d', 1,
                                                   origin=(*FLIGHT_START, FLIGHT_ALTITUDE), prefix='f',
                                                   loadout='Strike')], mil_category=F.AIR_UNIT)
    fuel = {'bingo': BINGO_FUEL, 'none': 1.0, 'switch_off': BINGO_FUEL, 'no_base': DRY_FUEL, 'bingo_off': DRY_FUEL}

    for asset in flight.assets.values():
        asset.fuel = fuel[variant]

    mission, = F.missions_for(flight, [FLIGHT_END], mission_type='Strike',
                              target=F.zone_target(FLIGHT_END, 10_000.0), speed=AIR_SPEED)

    if variant == 'bingo_off':
        mission = dataclasses.replace(mission, end_criteria=EndCriteria(bingo=False))

    site = F.build_force(SITE, 'Red', [F.Unit('vehicle', 'BMP-2', 1, origin=SITE_POSITION, prefix='ifv',
                                              sensors={'air': SITE_SENSOR_RANGE})])
    blue = [flight]

    if variant != 'no_base':
        base = F.make_force(BASE, 'Blue', F.AIR_UNIT)
        F.add_assets(base, [F.make_structure(base, f'{BASE}/depot0', BASE_POSITION, category='Farp',
                                             asset_type='Oil_Tank')])
        blue.append(base)

    roles = {asset_id: 'unarmed' for asset_id in flight.assets}
    # Tiro Red SENZA effetto, solo contro aerei in volo: si misura se l'F-16C entra nel raggio del sensore.
    overrides = {asset_id: {'air': MARKER_SHOT} for asset_id in site.assets}
    return F.Scenario(forces_a=blue, forces_b=[site], missions=[mission],
                      fire_control=F.make_fire_control(roles=roles, overrides=overrides), duration=DURATION,
                      roles=roles)


def _validate(scenario: F.Scenario):
    """Il validatore di pianificazione sulla missione dello scenario NON ancora eseguito: (esito, errore)."""
    mission, = scenario.missions
    bases = MA.air_base_points(scenario.forces_a, 'Blue')

    try:
        return MA.check_mission_bingo(mission, scenario.force(FLIGHT).assets, bases), None
    except ValueError as error:
        return None, error


def _run(scenario: F.Scenario, session_id: str, bingo: bool = True):
    """Esegue lo scenario registrando i tratti dati allo scheduler e il programma degli aerei a terra."""
    with patch.object(SS, 'F6_BINGO', SS.F6_BINGO and bingo), \
            patch.object(CS, 'schedule_contacts', wraps=CS.schedule_contacts) as scheduler:
        outcome = scenario.run(session_id)

    return outcome, scheduler.call_args.kwargs['legs'], scheduler.call_args.kwargs['grounded']


def _expected_bingo(jet, fuel: float):
    """(istante, punto, atterraggio) del bingo attesi, ricavati QUI per bisezione sull'equazione del bingo
    (residuo in metri di crociera - riserva = distanza 3D dalla base a quota 0), indipendente dalla formula
    chiusa di `Fuel_Model.bingo_point`; atterraggio alla crociera dell'asset."""
    autonomy = jet.fuel_autonomy()
    base = (*BASE_POSITION, 0.0)

    def gap(u):
        point = (FLIGHT_START[0] + u, FLIGHT_START[1], FLIGHT_ALTITUDE)
        return (fuel - FM.BINGO_RESERVE) * autonomy - u - math.dist(point, base)

    lo, hi = 0.0, FLIGHT_END[0] - FLIGHT_START[0]

    for _ in range(200):
        middle = 0.5 * (lo + hi)
        lo, hi = (middle, hi) if gap(middle) > 0.0 else (lo, middle)

    point = (FLIGHT_START[0] + hi, FLIGHT_START[1], FLIGHT_ALTITUDE)
    time = hi / AIR_SPEED
    return time, point, time + math.dist(point, base) / FM.cruise_speed(jet)


class TestS26Bingo(F.LoggerSilencer, unittest.TestCase):
    """S26-BINGO: rientro al bingo in volo, bingo a priori nel validatore, controlli senza bingo (F6-B2)."""

    SEEDS = _seeds('S26-BINGO')
    VARIANTS = ('bingo', 'none', 'switch_off', 'no_base', 'bingo_off')
    JET = f'{FLIGHT}/f0'
    MISSION = f'{FLIGHT}:Strike'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}
        cls.validations = {variant: _validate(_scenario(variant)) for variant in cls.VARIANTS}

        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                scenario = _scenario(variant)
                outcome, legs, grounded = _run(scenario, session_id, bingo=variant != 'switch_off')
                cls.runs[variant].append((outcome, legs, grounded, scenario.force(FLIGHT).assets[cls.JET]))

    def _bingo(self):
        return _expected_bingo(_scenario('bingo').force(FLIGHT).assets[self.JET], BINGO_FUEL)

    def test_the_validator_rejects_what_does_not_return_with_the_reserve(self):
        """A priori: 'bingo' (0,3) rifiutata con il motivo, 'none' (pieno) accettata con margine >= 0,
        'no_base' rifiutata per mancanza di una base idonea, 'bingo_off' non controllata."""
        margins, error = self.validations['bingo']
        self.assertIsNone(margins)
        self.assertIn(f"{self.JET!r} does not return with the fuel reserve", str(error))

        margins, error = self.validations['none']
        self.assertIsNone(error)
        self.assertGreaterEqual(margins[self.JET], 0.0)

        _, error = self.validations['no_base']
        self.assertIn('no suitable air base', str(error))
        self.assertEqual(self.validations['bingo_off'], (None, None))

    def test_rejected_a_priori_is_exactly_bingo_in_flight(self):
        """Stesso criterio: il bingo che il validatore annuncia (`Fuel_Model.bingo_point` sui tratti della
        missione intera) e' quello eseguito in sessione; dove il validatore accetta, nessun bingo."""
        scenario = _scenario('bingo')
        mission, = scenario.missions
        jet = scenario.force(FLIGHT).assets[self.JET]
        movement, = MA.mission_movements(mission)
        planned = FM.bingo_point(jet, MA.airborne_legs(movement), MA.air_base_points(scenario.forces_a, 'Blue'))

        for outcome, _, _, _ in self.runs['bingo']:
            self.assertAlmostEqual(outcome.mission_outcomes[self.MISSION].asset_outcomes[self.JET].end_time,
                                   planned.time, delta=1e-6)

        for outcome, _, _, _ in self.runs['none']:
            self.assertNotEqual(outcome.mission_outcomes[self.MISSION].asset_outcomes[self.JET].end_reason,
                                AssetEndReason.BINGO)

    def test_at_bingo_the_aircraft_returns_to_the_base(self):
        """Tratti dati allo scheduler: rotta fino al bingo, rientro in linea retta sulla base (a quota 0)
        alla crociera, poi fermo a terra sulla base fino a fine sessione (programma a terra
        dall'atterraggio)."""
        t_bingo, point, t_land = self._bingo()
        landing = (*BASE_POSITION, 0.0)

        for _, legs, grounded, _ in self.runs['bingo']:
            outbound, back, parked = legs[self.JET]
            self.assertAlmostEqual(outbound.t_end, t_bingo, delta=1e-3)

            for got, want in zip(back.p_start, point):
                self.assertAlmostEqual(got, want, delta=1e-3)

            self.assertEqual(back.p_end, landing)
            self.assertAlmostEqual(back.t_end, t_land, delta=1e-3)
            self.assertEqual((parked.p_start, parked.p_end, parked.t_end), (landing, landing, DURATION))
            self.assertEqual(len(grounded.intervals(self.JET)), 1)
            self.assertAlmostEqual(grounded.intervals(self.JET)[0][0], t_land, delta=1e-3)

    def test_after_bingo_the_threat_ahead_is_never_met(self):
        """Il sito Red e' oltre il punto di bingo: con il rientro non spara mai; senza bingo (pieno, o
        interruttore spento) l'F-16C gli passa sopra e Red spara nella maggior parte delle repliche."""
        for outcome, _, _, _ in self.runs['bingo']:
            self.assertEqual(_shots_by(outcome, SITE), [], outcome.session_id)

        for variant in ('none', 'switch_off'):
            firing = sum(1 for outcome, _, _, _ in self.runs[variant] if _shots_by(outcome, SITE))
            self.assertGreaterEqual(firing / len(self.runs[variant]), MIN_FIRING_FRACTION, (variant, firing))

    def test_bingo_outcome_is_aborted_with_the_reserve_on_board(self):
        """Esito: asset OPERATIONAL con motivo BINGO all'istante del bingo, missione ABORTED(BINGO), postura
        a terra, punto finale non raggiunto; il rientro consuma fino alla riserva (alla crociera), due
        FuelEvent (andata fino al bingo, rientro)."""
        t_bingo, _, _ = self._bingo()

        for outcome, _, _, jet in self.runs['bingo']:
            mission = outcome.mission_outcomes[self.MISSION]
            asset = mission.asset_outcomes[self.JET]
            self.assertEqual((mission.status, mission.reason), (MissionStatus.ABORTED, AbortReason.BINGO))
            self.assertEqual((asset.state, asset.end_reason), (AssetState.OPERATIONAL, AssetEndReason.BINGO))
            self.assertAlmostEqual(asset.end_time, t_bingo, delta=1e-3)
            self.assertEqual(mission.actual_etas, (0.0, None))
            self.assertEqual(outcome.postures[self.JET], MA.PARKED_POSTURE)
            self.assertFalse(jet.is_destroyed())
            outbound, back = [e for e in outcome.fuel_events if e.asset_id == self.JET]
            self.assertFalse(back.exhausted)
            self.assertAlmostEqual(jet.fuel, FM.BINGO_RESERVE, delta=1e-9)

    def test_without_bingo_the_route_is_completed(self):
        """'none' e 'switch_off': rotta completata (COMPLETED, ROUTE_COMPLETED), aereo fuori scena alla fine
        della rotta come prima; con lo 0,3 la sola andata non esaurisce il carburante."""
        for variant in ('none', 'switch_off'):
            for outcome, legs, _, jet in self.runs[variant]:
                mission = outcome.mission_outcomes[self.MISSION]
                self.assertEqual(mission.status, MissionStatus.COMPLETED, variant)
                self.assertEqual(mission.asset_outcomes[self.JET].end_reason, AssetEndReason.ROUTE_COMPLETED)
                self.assertAlmostEqual(legs[self.JET][-1].t_end, (FLIGHT_END[0] - FLIGHT_START[0]) / AIR_SPEED,
                                       delta=1e-6)
                self.assertGreater(jet.fuel, 0.0)

    def test_without_a_base_or_with_bingo_off_the_aircraft_runs_dry(self):
        """'no_base' e 'bingo_off': nessun rientro; esaurimento a 235,5 km dalla partenza (0,15 del pieno
        alla crociera), senza base raggiungibile in planata: perso (DESTROYED, FUEL_EXHAUSTED), missione
        DESTROYED, nessun tratto dopo l'esaurimento (regole della F6-A)."""
        jet = _scenario('no_base').force(FLIGHT).assets[self.JET]
        t_dry = DRY_FUEL * jet.fuel_autonomy() / AIR_SPEED

        for variant in ('no_base', 'bingo_off'):
            for outcome, legs, grounded, jet in self.runs[variant]:
                mission = outcome.mission_outcomes[self.MISSION]
                asset = mission.asset_outcomes[self.JET]
                self.assertEqual(mission.status, MissionStatus.DESTROYED, variant)
                self.assertEqual((asset.state, asset.end_reason), (AssetState.DESTROYED, AssetEndReason.FUEL_EXHAUSTED))
                self.assertAlmostEqual(asset.end_time, t_dry, delta=1e-3)
                self.assertAlmostEqual(legs[self.JET][-1].t_end, t_dry, delta=1e-3)
                self.assertTrue(jet.is_destroyed())
                self.assertFalse(grounded.ever(self.JET))
                self.assertEqual(outcome.postures[self.JET], MA.DESTROYED_POSTURE)


if __name__ == '__main__':
    unittest.main()
