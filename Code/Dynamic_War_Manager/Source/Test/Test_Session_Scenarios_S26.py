"""Scenario S26 del motore di sessioni virtuali: bingo a priori e bingo in volo con rientro (F6-B2, F6-B2bis, G2),
consumo in ingaggio (G3).

Prosegue `Test_Session_Scenarios.py` (S1-S9), `Test_Session_Scenarios_S10_S18.py`, gli S19-S25 con la
stessa disciplina: si verifica un comportamento QUALITATIVO o STRUTTURALE, mai un numero calibrato.

Decisione 14 dell'utente (2026-10-12, deviazione 14 del Piano), passo F6-B2, rifatto dalla F6-B2bis e dal G2
(decisioni dell'utente del 2026-10-15), v. `Logic/Session_Simulator`, "Bingo", `Logic/Fuel_Model`, "Bingo" e
"Soglia di bingo e albero di decisione", e `Logic/Mission_Adapter`, "Bingo a priori":
  * **G2** (`Session_Simulator.F6_BINGO_DISENGAGE_RESERVE`, attivo): bingo se il carburante e' sotto la rotta
    intera + la riserva di disimpegno (`Fuel_Model.disengagement_reserve`); con consumo deterministico la
    soglia scatta alla partenza o mai. Combattimento: interrompe e va alla candidata piu' vicina (qui, partito
    in volo, il diretto alla base del lato); trasferimento ('Transport'): continua se il carburante basta a
    concludere, altrimenti torna; esito BINGO / ABORTED(BINGO); il validatore (`check_mission_bingo`) rifiuta
    esattamente le missioni che vanno in bingo;
  * **F6-B2bis** (G2 spento, `F6_BINGO_REVERSE_ROUTE` acceso): bingo quando il residuo e' 1,2 x il ritorno
    lungo la rotta a ritroso, a meta' rotta;
  * **F6-B2** (G2 e ritroso spenti): rientro rettilineo con la riserva `Fuel_Model.BINGO_RESERVE`;
  * senza base, o con `bingo` False, valgono le regole della F6-A (a secco: planata o perdita, con l'equipaggio
    recuperato).

## S26-BINGO (`TestS26Bingo`)

Blue-Flight: un F-16C 'Strike' (ruolo 'unarmed', autonomia di crociera del registro col loadout 'Strike':
1570 km, 'max' 1140 km, crociera 266,7 m/s, riserva di disimpegno ~0,085 del pieno) in volo a 5000 m da
(10 km, 0) verso (310 km, 0) a 250 m/s (1200 s): rotta 0,191 del pieno alla crociera (0,263 al regime di
combattimento), soglia del G2 ~0,276. Blue-Base: base aerea (Military 'Airbase') con un deposito in (0, 0), a
~11,2 km (3D) dal punto di comparsa e a 10 km dalla rotta (non e' una base alternativa). Red-Site: un BMP-2 in
(260 km, 0) con sensore 'air' DICHIARATO di 40 km e tiro DICHIARATO senza effetto (precisione 0) contro gli
aerei: misura se e quando l'F-16C passa nel suo raggio. Varianti per seed (le prime sei con i nomi di prima,
le nuove in coda):
  * 'bingo' (G2, `G2_FUEL` 0,27, sotto la soglia): bingo alla partenza, l'aereo scende subito sulla base
    (~11,2 km, ~42 s), Red non spara mai; il validatore rifiuta;
  * 'none': pieno, nessun bingo, rotta completata, Red spara nella maggior parte delle repliche;
  * 'switch_off' (`F6_BINGO` spento, `BINGO_FUEL` 0,28): rotta completata (anche al regime di combattimento),
    Red spara come in 'none';
  * 'no_base' (`DRY_FUEL` 0,15, nessuna base Blue): in bingo ma senza base a cui tornare: si esaurisce a ~235,5
    km e, senza base raggiungibile in planata, e' perso con l'equipaggio recuperato (F6-A); il validatore rifiuta;
  * 'bingo_off' (`DRY_FUEL` con la base, `EndCriteria(bingo=False)`): nessun controllo, perdita come 'no_base';
    il validatore non la controlla;
  * 'reverse_off' (`BINGO_FUEL`, G2 e `F6_BINGO_REVERSE_ROUTE` spenti): la F6-B2, bingo rettilineo con la
    riserva 0,1 a x ~146,3 km (t ~545 s), atterraggio a ~1094 s;
  * 'reserve_off' (`BINGO_FUEL`, G2 spento): la F6-B2bis, bingo a x ~203,7 km (t ~775 s), ritroso fino al
    punto di comparsa e discesa sulla base, atterraggio a ~1543 s (con 0,28 l'aereo e' SOPRA la soglia del G2);
  * 'transfer_continue' (G2, 'Transport', `G2_FUEL`): sotto la soglia ma con carburante per la rotta: continua,
    rotta completata consumando la riserva;
  * 'transfer_return' (G2, 'Transport', `DRY_FUEL`, sotto la rotta): ritroso fino al punto di comparsa (lunghezza
    zero alla partenza) e diretto alla base, come 'bingo';
  * 'engagement_fuel_off' (G3 spento, pieno): come 'none' con la regola della F6-A (tutto il movimento al regime
    di combattimento se Red spara).

G3 (`Session_Simulator.G3_ENGAGEMENT_FUEL`, attivo): dove Red spara, l'F-16C (bersaglio delle salve marcatrici)
consuma la riserva di disimpegno (~0,085) all'istante del primo lancio, e il movimento resta alla crociera; in
'transfer_continue' (0,27, sotto la soglia) quel consumo esaurisce il contatore poco prima della fine della rotta,
che e' completata lo stesso (nessun ri-scheduling fino al G4).

Asserzioni: invarianti per replica (istanti, punti, esiti, eventi) e frazioni aggregate con soglie
DICHIARATE (stime di test, non tarate sul risultato; v. sotto). Istanti e punti attesi del rientro a meta' rotta
sono ricavati nel test per bisezione sull'equazione del bingo, indipendentemente dalle formule chiuse di
`Fuel_Model`; la soglia del G2 e' ricalcolata nel test dalla rotta e dalla riserva dell'asset.
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
# Carburante dell'F-16C [frazione del pieno]: valori di test, non dati, verificati nel test
# (`test_declared_fuels`) contro la rotta e la riserva ricalcolate dal registro.
#   * 0,28: basta per l'andata (300 km) anche al regime di combattimento (0,263, 'switch_off', dove Red spara),
#     non tiene 1,2 volte il ritorno a ritroso (F6-B2bis) ne' il rientro rettilineo con la riserva (F6-B2), ma
#     e' SOPRA la soglia del G2 (~0,276): serve alle varianti a G2 spento;
#   * 0,27: sotto la soglia del G2 ma sopra la rotta anche al regime di combattimento ('bingo',
#     'transfer_continue');
#   * 0,15: non basta nemmeno per la rotta alla crociera (0,191).
BINGO_FUEL = 0.28
G2_FUEL = 0.27
DRY_FUEL = 0.15
MARKER_SHOT = dataclasses.replace(F.SHOTS['sam'], accuracy=0.0, weapon='test:marker')

# Soglia delle frazioni aggregate sui seed: DICHIARATA di test, non tarata sul risultato (stessa stima di
# S22-S25: il rilevamento e' un'estrazione per finestra e osservatore, 0,5 = "la regola, non l'eccezione").
MIN_FIRING_FRACTION = 0.5

# Variante -> (carburante, tipo di missione, base Blue, bingo dichiarato, F6_BINGO, F6_BINGO_REVERSE_ROUTE,
# F6_BINGO_DISENGAGE_RESERVE, G3_ENGAGEMENT_FUEL). Le prime sei con i nomi e l'ordine di prima (nomi stabili
# nella fotografia).
VARIANTS = {
    'bingo': (G2_FUEL, 'Strike', True, True, True, True, True, True),
    'none': (1.0, 'Strike', True, True, True, True, True, True),
    'switch_off': (BINGO_FUEL, 'Strike', True, True, False, True, True, True),
    'no_base': (DRY_FUEL, 'Strike', False, True, True, True, True, True),
    'bingo_off': (DRY_FUEL, 'Strike', True, False, True, True, True, True),
    'reverse_off': (BINGO_FUEL, 'Strike', True, True, True, False, False, True),
    'reserve_off': (BINGO_FUEL, 'Strike', True, True, True, True, False, True),
    'transfer_continue': (G2_FUEL, 'Transport', True, True, True, True, True, True),
    'transfer_return': (DRY_FUEL, 'Transport', True, True, True, True, True, True),
    'engagement_fuel_off': (1.0, 'Strike', True, True, True, True, True, False),
}


def _seeds(prefix: str, count: int = SEEDS_PER_SCENARIO):
    return [f'{prefix}-{index}' for index in range(count)]


def _shots_by(outcome, prefix: str):
    return [event for event in outcome.ammunition_events if event.asset_id.startswith(prefix + '/')]


def _mission_id(variant: str) -> str:
    return f'{FLIGHT}:{VARIANTS[variant][1]}'


def _scenario(variant: str) -> F.Scenario:
    fuel, mission_type, with_base, bingo, _, _, _, _ = VARIANTS[variant]
    flight = F.build_force(FLIGHT, 'Blue', [F.Unit('aircraft', 'F-16C Block 52d', 1,
                                                   origin=(*FLIGHT_START, FLIGHT_ALTITUDE), prefix='f',
                                                   loadout='Strike')], mil_category=F.AIR_UNIT)

    for asset in flight.assets.values():
        asset.fuel = fuel

    mission, = F.missions_for(flight, [FLIGHT_END], mission_type=mission_type,
                              target=F.zone_target(FLIGHT_END, 10_000.0), speed=AIR_SPEED)

    if not bingo:
        mission = dataclasses.replace(mission, end_criteria=EndCriteria(bingo=False))

    site = F.build_force(SITE, 'Red', [F.Unit('vehicle', 'BMP-2', 1, origin=SITE_POSITION, prefix='ifv',
                                              sensors={'air': SITE_SENSOR_RANGE})])
    blue = [flight]

    if with_base:
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


def _validate(scenario: F.Scenario, variant: str):
    """Il validatore di pianificazione sulla missione dello scenario NON ancora eseguito, con la regola della
    variante (gli stessi interruttori dell'esecutore): (esito, errore)."""
    _, _, _, _, _, reverse, reserve, _ = VARIANTS[variant]
    mission, = scenario.missions
    bases = MA.air_base_points(scenario.forces_a, 'Blue')

    try:
        return MA.check_mission_bingo(mission, scenario.force(FLIGHT).assets, bases, reverse_route=reverse,
                                      disengage_reserve=reserve), None
    except ValueError as error:
        return None, error


def _run(scenario: F.Scenario, session_id: str, variant: str):
    """Esegue lo scenario con gli interruttori della variante, registrando i tratti dati allo scheduler e il
    programma degli aerei a terra."""
    _, _, _, _, bingo, reverse, reserve, engagement_fuel = VARIANTS[variant]

    with patch.object(SS, 'F6_BINGO', SS.F6_BINGO and bingo), \
            patch.object(SS, 'F6_BINGO_REVERSE_ROUTE', SS.F6_BINGO_REVERSE_ROUTE and reverse), \
            patch.object(SS, 'F6_BINGO_DISENGAGE_RESERVE', SS.F6_BINGO_DISENGAGE_RESERVE and reserve), \
            patch.object(SS, 'G3_ENGAGEMENT_FUEL', SS.G3_ENGAGEMENT_FUEL and engagement_fuel), \
            patch.object(CS, 'schedule_contacts', wraps=CS.schedule_contacts) as scheduler:
        outcome = scenario.run(session_id)

    return outcome, scheduler.call_args.kwargs['legs'], scheduler.call_args.kwargs['grounded']


def _bisect(gap):
    """Lo zero di `gap` (decrescente) sui metri percorsi lungo la rotta, per bisezione."""
    lo, hi = 0.0, FLIGHT_END[0] - FLIGHT_START[0]

    for _ in range(200):
        middle = 0.5 * (lo + hi)
        lo, hi = (middle, hi) if gap(middle) > 0.0 else (lo, middle)

    return hi


def _spawn_and_base():
    return (*FLIGHT_START, FLIGHT_ALTITUDE), (*BASE_POSITION, 0.0)


def _expected_bingo(jet, fuel: float):
    """F6-B2bis: (istante, punto, atterraggio, lunghezza del ritorno) attesi, ricavati QUI per bisezione
    sull'equazione del bingo (residuo in metri di crociera = fattore x (metri percorsi + tratto diretto dal
    punto di comparsa alla base a quota 0)); atterraggio alla crociera dell'asset."""
    autonomy = jet.fuel_autonomy()
    spawn, base = _spawn_and_base()
    direct = math.dist(spawn, base)
    u = _bisect(lambda u: fuel * autonomy - u - FM.BINGO_RETURN_FACTOR * (u + direct))
    point = (FLIGHT_START[0] + u, FLIGHT_START[1], FLIGHT_ALTITUDE)
    time = u / AIR_SPEED
    return time, point, time + (u + direct) / FM.cruise_speed(jet), u + direct


def _expected_straight_bingo(jet, fuel: float):
    """F6-B2 (G2 e `F6_BINGO_REVERSE_ROUTE` spenti): (istante, punto, atterraggio) attesi per bisezione
    sull'equazione del bingo rettilineo (residuo in metri di crociera - riserva = distanza 3D dalla base a
    quota 0)."""
    autonomy = jet.fuel_autonomy()
    _, base = _spawn_and_base()

    def gap(u):
        point = (FLIGHT_START[0] + u, FLIGHT_START[1], FLIGHT_ALTITUDE)
        return (fuel - FM.BINGO_RESERVE) * autonomy - u - math.dist(point, base)

    u = _bisect(gap)
    point = (FLIGHT_START[0] + u, FLIGHT_START[1], FLIGHT_ALTITUDE)
    time = u / AIR_SPEED
    return time, point, time + math.dist(point, base) / FM.cruise_speed(jet)


class TestS26Bingo(F.LoggerSilencer, unittest.TestCase):
    """S26-BINGO: soglia del G2 e albero di decisione (combattimento e trasferimento), rientri della F6-B2bis e
    della F6-B2 a interruttori spenti, bingo a priori nel validatore, controlli senza bingo."""

    SEEDS = _seeds('S26-BINGO')
    # Le prime sei con i nomi e l'ordine di prima, le nuove (F6-B2bis: 'reverse_off'; G2: le tre seguenti; G3:
    # 'engagement_fuel_off') in coda: i nomi delle varianti nella fotografia restano stabili.
    VARIANTS = tuple(VARIANTS)
    JET = f'{FLIGHT}/f0'
    # Varianti in cui l'aereo va in bingo e rientra, e quelle che lo fanno alla partenza (G2).
    RETURNING = ('bingo', 'reverse_off', 'reserve_off', 'transfer_return')
    AT_START = ('bingo', 'transfer_return')

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}
        cls.validations = {variant: _validate(_scenario(variant), variant) for variant in cls.VARIANTS}

        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                scenario = _scenario(variant)
                outcome, legs, grounded = _run(scenario, session_id, variant)
                cls.runs[variant].append((outcome, legs, grounded, scenario.force(FLIGHT).assets[cls.JET]))

    def _jet(self, variant='bingo'):
        return _scenario(variant).force(FLIGHT).assets[self.JET]

    def _mission(self, outcome, variant):
        return outcome.mission_outcomes[_mission_id(variant)]

    def _threshold(self):
        """(rotta alla crociera, rotta al regime di combattimento, soglia del G2), ricalcolate dal registro."""
        scenario = _scenario('bingo')
        mission, = scenario.missions
        jet = scenario.force(FLIGHT).assets[self.JET]
        movement, = MA.mission_movements(mission)
        route = MA.route_fuel_demand(jet, MA.airborne_legs(movement))
        combat = jet.fuel_for_distance(FLIGHT_END[0] - FLIGHT_START[0], 'max')
        return route, combat, route + FM.disengagement_reserve(jet)

    def test_declared_fuels(self):
        """I carburanti di test stanno dove dichiarato: 0,15 < rotta < rotta di combattimento < 0,27 < soglia del
        G2 < 0,28."""
        route, combat, threshold = self._threshold()
        self.assertLess(DRY_FUEL, route)
        self.assertLess(route, combat)
        self.assertLess(combat, G2_FUEL)
        self.assertLess(G2_FUEL, threshold)
        self.assertLess(threshold, BINGO_FUEL)

    def test_the_validator_rejects_what_would_reach_bingo(self):
        """A priori, con la regola di ogni variante: 'bingo', 'transfer_continue' (sotto il minimo anche se poi
        continua), 'transfer_return' e 'no_base' rifiutate dal G2 con soglia e decisione; 'none' accettata con
        margine >= 0; 'bingo_off' non controllata; 'reserve_off' rifiutata con la regola della F6-B2bis,
        'reverse_off' con quella della F6-B2 (riserva)."""
        for variant, decision in (('bingo', "decides 'departure'"), ('transfer_continue', 'continues on its route'),
                                  ('transfer_return', "decides 'departure'"), ('no_base', "decides 'no_base'")):
            margins, error = self.validations[variant]
            self.assertIsNone(margins, variant)
            self.assertIn(f"{self.JET!r} starts under the bingo threshold", str(error))
            self.assertIn(decision, str(error))

        margins, error = self.validations['none']
        self.assertIsNone(error)
        self.assertGreaterEqual(margins[self.JET], 0.0)
        self.assertEqual(self.validations['bingo_off'], (None, None))
        _, error = self.validations['reserve_off']
        self.assertIn(f"{self.JET!r} does not keep the bingo fuel", str(error))
        _, error = self.validations['reverse_off']
        self.assertIn(f"{self.JET!r} does not return with the fuel reserve", str(error))

    def test_rejected_a_priori_is_exactly_bingo_in_flight(self):
        """Stesso criterio: il bingo che il validatore annuncia (G2: `mission_bingo_decision`; a G2 spento
        `Fuel_Model.bingo_point` con la regola della missione o senza) e' quello eseguito in sessione; dove il
        validatore accetta, nessun bingo."""
        planned = {}

        for variant in self.RETURNING:
            scenario = _scenario(variant)
            mission, = scenario.missions
            jet = scenario.force(FLIGHT).assets[self.JET]
            movement, = MA.mission_movements(mission)
            legs, bases = MA.airborne_legs(movement), MA.air_base_points(scenario.forces_a, 'Blue')

            if variant in self.AT_START:
                planned[variant] = MA.mission_bingo_decision(mission, movement, jet, bases)
            elif variant == 'reserve_off':
                planned[variant] = FM.bingo_point(jet, legs, bases, rule=MA.bingo_return_rule(mission))
            else:
                planned[variant] = FM.bingo_point(jet, legs, bases)

        for variant, bingo in planned.items():
            self.assertIn(f't={bingo.time:.1f} s', str(self.validations[variant][1]))

            for outcome, _, _, _ in self.runs[variant]:
                self.assertAlmostEqual(self._mission(outcome, variant).asset_outcomes[self.JET].end_time,
                                       bingo.time, delta=1e-6)

        for outcome, _, _, _ in self.runs['none']:
            self.assertNotEqual(self._mission(outcome, 'none').asset_outcomes[self.JET].end_reason,
                                AssetEndReason.BINGO)

    def test_under_the_threshold_the_aircraft_descends_at_once_on_the_base(self):
        """G2, 'bingo' (combattimento) e 'transfer_return' (trasferimento che non puo' concludere): bingo alla
        partenza; dal punto di comparsa (ritroso di lunghezza zero) il tratto diretto sulla base alla crociera,
        poi a terra fino a fine sessione. Nessun tratto della rotta pianificata."""
        spawn, landing = _spawn_and_base()
        t_land = math.dist(spawn, landing) / FM.cruise_speed(self._jet())

        for variant in self.AT_START:
            for _, legs, grounded, _ in self.runs[variant]:
                descent, parked = legs[self.JET]
                self.assertEqual((descent.t_start, descent.p_start, descent.p_end), (0.0, spawn, landing), variant)
                self.assertAlmostEqual(descent.t_end, t_land, delta=1e-6)
                self.assertEqual((parked.p_start, parked.p_end, parked.t_end), (landing, landing, DURATION))
                self.assertEqual(len(grounded.intervals(self.JET)), 1)
                self.assertAlmostEqual(grounded.intervals(self.JET)[0][0], t_land, delta=1e-6)

    def test_reserve_off_retraces_the_route_to_the_base(self):
        """G2 spento ('reserve_off', la F6-B2bis): rotta fino al bingo, ritroso in quota fino al punto di comparsa,
        discesa sulla base (a quota 0) con il tratto diretto, alla crociera; poi fermo a terra sulla base."""
        t_bingo, point, t_land, _ = _expected_bingo(self._jet(), BINGO_FUEL)
        spawn, landing = _spawn_and_base()

        for _, legs, grounded, _ in self.runs['reserve_off']:
            outbound, back, descent, parked = legs[self.JET]
            self.assertAlmostEqual(outbound.t_end, t_bingo, delta=1e-3)

            for got, want in zip(back.p_start, point):
                self.assertAlmostEqual(got, want, delta=1e-3)

            self.assertEqual((back.p_end, descent.p_start, descent.p_end), (spawn, spawn, landing))
            self.assertAlmostEqual(descent.t_end, t_land, delta=1e-3)
            self.assertEqual((parked.p_start, parked.p_end, parked.t_end), (landing, landing, DURATION))
            self.assertAlmostEqual(grounded.intervals(self.JET)[0][0], t_land, delta=1e-3)

    def test_reverse_route_off_is_the_straight_return(self):
        """'reverse_off': la F6-B2 com'era, rientro in linea retta dal punto di bingo alla base (a quota 0)
        con la riserva: bingo prima che con il ritroso (la riserva fissa di 0,1 pesa piu' del 20% del
        ritorno su questa rotta)."""
        t_bingo, point, t_land = _expected_straight_bingo(self._jet(), BINGO_FUEL)
        landing = (*BASE_POSITION, 0.0)

        for _, legs, _, _ in self.runs['reverse_off']:
            outbound, back, parked = legs[self.JET]
            self.assertAlmostEqual(outbound.t_end, t_bingo, delta=1e-3)

            for got, want in zip(back.p_start, point):
                self.assertAlmostEqual(got, want, delta=1e-3)

            self.assertEqual(back.p_end, landing)
            self.assertAlmostEqual(back.t_end, t_land, delta=1e-3)
            self.assertEqual((parked.p_start, parked.p_end), (landing, landing))

        self.assertLess(t_bingo, _expected_bingo(self._jet(), BINGO_FUEL)[0])

    def test_after_bingo_the_threat_ahead_is_never_met(self):
        """Il sito Red e' oltre il punto di bingo con ogni regola: con il rientro non spara mai; senza bingo (pieno,
        o interruttore spento) l'F-16C gli passa sopra e Red spara nella maggior parte delle repliche."""
        for variant in self.RETURNING:
            for outcome, _, _, _ in self.runs[variant]:
                self.assertEqual(_shots_by(outcome, SITE), [], (variant, outcome.session_id))

        for variant in ('none', 'switch_off'):
            firing = sum(1 for outcome, _, _, _ in self.runs[variant] if _shots_by(outcome, SITE))
            self.assertGreaterEqual(firing / len(self.runs[variant]), MIN_FIRING_FRACTION, (variant, firing))

    def test_bingo_outcome_is_aborted_with_the_return_on_board(self):
        """Esito: asset OPERATIONAL con motivo BINGO all'istante del bingo, missione ABORTED(BINGO), postura a terra,
        punto finale non raggiunto; il rientro consuma alla crociera: G2 (un FuelEvent, la discesa) lascia a bordo il
        carburante di partenza meno la discesa; F6-B2bis il 20% del ritorno (andata e due tratti di rientro); F6-B2
        la riserva (andata e rientro)."""
        jet = self._jet()
        spawn, landing = _spawn_and_base()
        descent = math.dist(spawn, landing) / jet.fuel_autonomy()
        t_bingo, _, _, length = _expected_bingo(jet, BINGO_FUEL)
        left = {'bingo': G2_FUEL - descent, 'transfer_return': DRY_FUEL - descent,
                'reserve_off': (FM.BINGO_RETURN_FACTOR - 1.0) * length / jet.fuel_autonomy(),
                'reverse_off': FM.BINGO_RESERVE}
        events = {'bingo': 1, 'transfer_return': 1, 'reserve_off': 3, 'reverse_off': 2}
        times = {'bingo': 0.0, 'transfer_return': 0.0, 'reserve_off': t_bingo,
                 'reverse_off': _expected_straight_bingo(jet, BINGO_FUEL)[0]}

        for variant in self.RETURNING:
            for outcome, _, _, jet in self.runs[variant]:
                mission = self._mission(outcome, variant)
                asset = mission.asset_outcomes[self.JET]
                self.assertEqual((mission.status, mission.reason), (MissionStatus.ABORTED, AbortReason.BINGO))
                self.assertEqual((asset.state, asset.end_reason), (AssetState.OPERATIONAL, AssetEndReason.BINGO))
                self.assertIsNone(asset.crew_recovered)
                self.assertAlmostEqual(asset.end_time, times[variant], delta=1e-3)
                self.assertEqual(mission.actual_etas, (0.0, None))
                self.assertEqual(outcome.postures[self.JET], MA.PARKED_POSTURE)
                self.assertFalse(jet.is_destroyed())
                fuel_events = [e for e in outcome.fuel_events if e.asset_id == self.JET]
                self.assertEqual(len(fuel_events), events[variant], variant)
                self.assertFalse(any(event.exhausted for event in fuel_events))
                self.assertAlmostEqual(jet.fuel, left[variant], delta=1e-9)

    def test_without_bingo_the_route_is_completed(self):
        """'none', 'switch_off', 'engagement_fuel_off' e 'transfer_continue' (trasferimento sotto la soglia del G2
        che CONTINUA, nessun aborto): rotta completata (COMPLETED, ROUTE_COMPLETED), aereo fuori scena alla fine
        della rotta come prima. Con 0,28 ('switch_off') la sola andata + un consumo d'ingaggio (G3) stanno sotto la
        soglia del G2 e non esauriscono il carburante. 'transfer_continue' (0,27, sotto la soglia) consuma la
        riserva: se Red spara, il consumo d'ingaggio la esaurisce e il contatore arriva a ZERO poco prima della
        fine della rotta (evento del tratto `exhausted`), ma la rotta e' completata lo stesso: il movimento e'
        calcolato a monte alla crociera e non e' ricalcolato dopo l'ingaggio (limite noto del G3, ri-scheduling
        nel G4); se Red non spara, carburante residuo positivo."""
        for variant in ('none', 'switch_off', 'engagement_fuel_off', 'transfer_continue'):
            for outcome, legs, _, jet in self.runs[variant]:
                mission = self._mission(outcome, variant)
                self.assertEqual(mission.status, MissionStatus.COMPLETED, variant)
                self.assertEqual(mission.asset_outcomes[self.JET].end_reason, AssetEndReason.ROUTE_COMPLETED)
                self.assertAlmostEqual(legs[self.JET][-1].t_end, (FLIGHT_END[0] - FLIGHT_START[0]) / AIR_SPEED,
                                       delta=1e-6)
                exhausted = [event for event in outcome.fuel_events if event.exhausted]

                if variant == 'transfer_continue' and _shots_by(outcome, SITE):
                    self.assertEqual(jet.fuel, 0.0)
                    self.assertEqual([event.regime for event in exhausted], [SS.CRUISE_REGIME])
                    self.assertLess(exhausted[0].distance_covered, exhausted[0].distance)
                    continue

                self.assertGreater(jet.fuel, 0.0, variant)
                self.assertEqual(exhausted, [], variant)

    def test_engagement_fuel(self):
        """G3: con il pieno ('none') il movimento e' alla crociera e, se Red spara, l'F-16C (bersaglio delle salve)
        consuma in piu' la riserva di disimpegno all'istante del primo lancio contro di lui, con un evento
        istantaneo prima del tratto; se Red non spara, nessun consumo d'ingaggio. 'engagement_fuel_off' (G3 spento):
        la regola della F6-A, tutto il movimento al regime di combattimento se Red spara."""
        route, combat, _ = self._threshold()
        charge = FM.engagement_fuel(self._jet())
        fired = {}

        for variant in ('none', 'engagement_fuel_off'):
            for outcome, _, _, jet in self.runs[variant]:
                shots = _shots_by(outcome, SITE)
                fired[variant] = fired.get(variant, 0) + bool(shots)
                events = [event for event in outcome.fuel_events if event.asset_id == self.JET]

                if variant == 'engagement_fuel_off':
                    self.assertEqual([e.regime for e in events], [SS.COMBAT_REGIME if shots else SS.CRUISE_REGIME])
                    self.assertAlmostEqual(jet.fuel, 1.0 - (combat if shots else route), delta=1e-9)
                elif shots:
                    self.assertEqual([e.regime for e in events], [FM.ENGAGEMENT_REGIME, SS.CRUISE_REGIME])
                    self.assertAlmostEqual(events[0].time, min(event.time for event in shots), delta=1e-9)
                    self.assertAlmostEqual(events[0].amount, charge, delta=1e-12)
                    self.assertAlmostEqual(jet.fuel, 1.0 - route - charge, delta=1e-9)
                else:
                    self.assertEqual([e.regime for e in events], [SS.CRUISE_REGIME])
                    self.assertAlmostEqual(jet.fuel, 1.0 - route, delta=1e-9)

        # Stesso seed, stessa sessione: il G3 cambia solo il carburante, non chi spara.
        self.assertEqual(fired['none'], fired['engagement_fuel_off'])
        self.assertGreater(fired['none'], 0)

    def test_without_a_base_or_with_bingo_off_the_aircraft_runs_dry(self):
        """'no_base' (in bingo ma senza base a cui tornare) e 'bingo_off': nessun rientro; esaurimento a 235,5 km
        dalla partenza (0,15 del pieno alla crociera), senza base raggiungibile in planata: perso (DESTROYED,
        FUEL_EXHAUSTED) con l'equipaggio recuperato, missione DESTROYED, nessun tratto dopo l'esaurimento (regole
        della F6-A)."""
        jet = _scenario('no_base').force(FLIGHT).assets[self.JET]
        t_dry = DRY_FUEL * jet.fuel_autonomy() / AIR_SPEED

        for variant in ('no_base', 'bingo_off'):
            for outcome, legs, grounded, jet in self.runs[variant]:
                mission = self._mission(outcome, variant)
                asset = mission.asset_outcomes[self.JET]
                self.assertEqual(mission.status, MissionStatus.DESTROYED, variant)
                self.assertEqual((asset.state, asset.end_reason, asset.crew_recovered),
                                 (AssetState.DESTROYED, AssetEndReason.FUEL_EXHAUSTED, True))
                self.assertAlmostEqual(asset.end_time, t_dry, delta=1e-3)
                self.assertAlmostEqual(legs[self.JET][-1].t_end, t_dry, delta=1e-3)
                self.assertTrue(jet.is_destroyed())
                self.assertFalse(grounded.ever(self.JET))
                self.assertEqual(outcome.postures[self.JET], MA.DESTROYED_POSTURE)


if __name__ == '__main__':
    unittest.main()
