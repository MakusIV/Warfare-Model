"""Scenario S26 del motore di sessioni virtuali: il BINGO nel modello finale (G1-G4 del nuovo modello di bingo),
con le varianti di controprova degli interruttori.

Prosegue `Test_Session_Scenarios.py` (S1-S9), `Test_Session_Scenarios_S10_S18.py`, gli S19-S25 con la
stessa disciplina: si verifica un comportamento QUALITATIVO o STRUTTURALE, mai un numero calibrato. Il caso di
due episodi d'ingaggio dello stesso aereo con bingo dopo il secondo e' in S27 (`Test_Session_Scenarios_S27.py`).

## Il modello finale

Decisioni dell'utente del 2026-10-15/17 (deviazioni 17-21 del Piano), v. `Logic/Session_Simulator`, "Bingo",
"Episodi d'ingaggio (G4a)", "Ri-pianificazione dopo l'episodio (G4b)", `Logic/Fuel_Model`, "Soglia di bingo e
albero di decisione" e "Consumo in ingaggio", e `Logic/Mission_Adapter`, "Bingo a priori":
  * **riserva di disimpegno** (G1, `Fuel_Model.disengagement_reserve`): 5 minuti (`Fuel_Model.DISENGAGE_TIME`) alla
    massima spinta militare;
  * **soglia e albero di decisione** (G2, `Session_Simulator.F6_BINGO_DISENGAGE_RESERVE`): bingo se il carburante
    e' sotto il resto della rotta + la riserva. Combattimento: interrompe e va alla candidata raggiungibile piu'
    vicina in percorso (base di partenza a ritroso, qui partito in volo: ritroso fino al punto di comparsa e poi
    diretto alla base del lato; o base alternativa entro 3 km dalla rotta); trasferimento ('Transport'): continua
    se il carburante basta a concludere, altrimenti torna. Esito BINGO / ABORTED(BINGO); il validatore
    (`check_mission_bingo`) rifiuta esattamente le missioni che partono in bingo. Con il solo consumo di movimento
    la soglia scatta alla partenza o mai;
  * **consumo d'ingaggio** (G3, `Session_Simulator.G3_ENGAGEMENT_FUEL`): dove Red spara, l'F-16C (bersaglio delle
    salve marcatrici) consuma la riserva di disimpegno (~0,085) all'istante del primo lancio dell'episodio, e il
    movimento resta alla crociera;
  * **episodi e ri-pianificazione** (G4a `G4_EPISODES`, G4b `G4_REPLAN`): finestre separate da piu' di
    `EPISODE_GAP` sono episodi distinti; alla fine di ogni episodio l'aereo che vi ha consumato e' ri-pianificato
    col residuo analitico: soglia e albero del G2 (qui le basi alternative contano davvero), oppure, a residuo
    zero, le regole della F6-A dal punto di fine episodio;
  * senza base, o con `EndCriteria.bingo` False, valgono le regole della F6-A (a secco: planata o perdita, con
    l'equipaggio recuperato).

## S26-BINGO (`TestS26Bingo`)

Blue-Flight: un F-16C 'Strike' (ruolo 'unarmed', autonomia di crociera del registro col loadout 'Strike':
1570 km, 'max' 1140 km, crociera 266,7 m/s, riserva di disimpegno ~0,085 del pieno) in volo a 5000 m da
(10 km, 0) verso (310 km, 0) a 250 m/s (1200 s): rotta 0,191 del pieno alla crociera (0,263 al regime di
combattimento), soglia del G2 ~0,276. Blue-Base: base aerea (Military 'Airbase') con un deposito in (0, 0), a
~11,2 km (3D) dal punto di comparsa e a 10 km dalla rotta (non e' una base alternativa). Red-Site: un BMP-2 in
(260 km, 0) con sensore 'air' DICHIARATO di 40 km e tiro DICHIARATO senza effetto (precisione 0) contro gli
aerei: misura se e quando l'F-16C passa nel suo raggio.

Le varianti per seed sono nell'ordine in cui sono state introdotte (F6-B2 -> G4b): l'ordine e i nomi sono le
chiavi della fotografia (`Scenario_Baseline`) e NON cambiano. Divise per ruolo (`FINAL_MODEL`, `SWITCH_CHECKS`):

**Modello finale** (tutti gli interruttori accesi):
  * 'none': pieno, nessun bingo, rotta completata; Red spara nella maggior parte delle repliche e l'F-16C consuma
    un'unica volta la riserva di disimpegno (G3);
  * 'bingo' (combattimento, `G2_FUEL` 0,27, sotto la soglia): bingo alla partenza, l'aereo scende subito sulla
    base (~11,2 km, ~42 s), Red non spara mai; il validatore rifiuta;
  * 'transfer_return' ('Transport', `DRY_FUEL` 0,15, sotto la rotta): ritroso fino al punto di comparsa
    (lunghezza zero alla partenza) e diretto alla base, come 'bingo';
  * 'transfer_continue' ('Transport', `G2_FUEL`): sotto la soglia ma con carburante per la rotta: continua. Se Red
    spara, il consumo d'ingaggio rende il residuo insufficiente: l'episodio con Red-Site dura fino all'ultimo
    impatto (~1211 s), oltre la fine della rotta (1200 s); la decisione del G4b e' alla fine dei tratti dell'aereo
    con residuo zero (esaurito in ingaggio, analiticamente a ~1162 s): regole della F6-A dal punto finale, nessuna
    base entro la planata (50 km da 5000 m), perso con l'equipaggio recuperato;
  * 'no_base' (`DRY_FUEL`, nessuna base Blue): in bingo ma senza base a cui tornare: si esaurisce a ~235,5 km e,
    senza base raggiungibile in planata, e' perso con l'equipaggio recuperato (F6-A); il validatore rifiuta;
  * 'bingo_off' (`DRY_FUEL` con la base, `EndCriteria(bingo=False)`, criterio della missione, non un
    interruttore): nessun controllo, perdita come 'no_base'; il validatore non la controlla;
  * 'post_engagement_bingo' (`BINGO_FUEL` 0,28, SOPRA la soglia alla partenza): un secondo sito Red-Near (BMP-2 in
    (100 km, 0), stesso sensore e stesso tiro marcatore) e una base Blue ALTERNATIVA sulla rotta in (180 km,
    2 km); sensore 'ground' dell'F-16C DICHIARATO di 20 km (`NEAR_JET_GROUND_SENSOR`), cosi' che le finestre dei
    due siti siano due episodi (G4a). Dopo l'episodio con Red-Near (consumo d'ingaggio) l'aereo e' sotto il resto
    della rotta + la riserva: bingo alla fine dell'episodio (G4b), regola di combattimento, la base alternativa
    (lungo la rotta fino a x = 180 km, poi discesa: ~42 km) batte il ritroso (~145 km); Red-Site non e' mai
    incontrato.

**Controprova degli interruttori** (un interruttore spento ciascuna; le regole "storiche" restano eseguibili e
devono restare quelle di prima):
  * 'switch_off' (`F6_BINGO` spento, `BINGO_FUEL`): nessun bingo, rotta completata (anche al regime di
    combattimento), Red spara come in 'none';
  * 'reverse_off' (`F6_BINGO_DISENGAGE_RESERVE` e `F6_BINGO_REVERSE_ROUTE` spenti, `BINGO_FUEL`): la regola della
    F6-B2, bingo rettilineo con la riserva fissa 0,1 a x ~146,3 km (t ~545 s), atterraggio a ~1094 s;
  * 'reserve_off' (`F6_BINGO_DISENGAGE_RESERVE` spento, `BINGO_FUEL`): la regola della F6-B2bis, bingo quando il
    residuo e' 1,2 x il ritorno a ritroso, a x ~203,7 km (t ~775 s), ritroso fino al punto di comparsa e discesa
    sulla base, atterraggio a ~1543 s (con 0,28 l'aereo e' SOPRA la soglia del G2);
  * 'engagement_fuel_off' (`G3_ENGAGEMENT_FUEL` spento, pieno): la regola della F6-A, tutto il movimento al regime
    di combattimento se Red spara, nessun consumo d'ingaggio;
  * 'replan_off' (`G4_REPLAN` spento, lo scenario di 'post_engagement_bingo'): nessuna ri-pianificazione, l'aereo
    prosegue, incontra Red-Site, consuma due volte e il contatore arriva a zero con la rotta completata (il limite
    del G3 prima del G4b).

Asserzioni: invarianti per replica (istanti, punti, esiti, eventi) e frazioni aggregate con soglie
DICHIARATE (stime di test, non tarate sul risultato; v. sotto). Istanti e punti attesi dei rientri a meta' rotta
delle regole storiche sono ricavati nel test per bisezione sull'equazione del bingo, indipendentemente dalle
formule chiuse di `Fuel_Model`; la soglia del G2 e' ricalcolata nel test dalla rotta e dalla riserva dell'asset.
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

# G4b (ri-pianificazione dopo l'episodio): un secondo sito Red PRIMA, a meta' strada fra la partenza e Red-Site, e
# una base aerea Blue ALTERNATIVA sulla rotta fra i due (entro `Fuel_Model.ALTERNATE_BASE_MAX_OFFSET`), solo nelle
# varianti 'post_engagement_bingo' e 'replan_off'.
NEAR_SITE, ALTERNATE_BASE = 'Red-Near', 'Blue-Alternate'
NEAR_SITE_POSITION = (100_000.0, 0.0)
ALTERNATE_BASE_POSITION = (180_000.0, 2_000.0)
# Sensore 'ground' DICHIARATO dell'F-16C in quelle due varianti (valore di test, non un dato): col radar del
# registro (~95 km sul BMP-2) le finestre dei due siti sarebbero separate da meno di `EPISODE_GAP` e formerebbero un
# solo episodio; con 20 km le finestre sono quelle del sensore 'air' dei siti (40 km): Red-Near ~[201, 519] s,
# Red-Site da ~841 s, due episodi.
NEAR_JET_GROUND_SENSOR = 20_000.0

# Variante -> (carburante, tipo di missione, base Blue, bingo dichiarato, F6_BINGO, F6_BINGO_REVERSE_ROUTE,
# F6_BINGO_DISENGAGE_RESERVE, G3_ENGAGEMENT_FUEL, sito vicino + base alternativa (G4b), G4_REPLAN). Ordine =
# ordine d'introduzione (F6-B2, F6-B2bis, G2, G3, G4b): nomi e ordine sono le chiavi della fotografia e NON
# cambiano. Il ruolo di ciascuna (modello finale o controprova di un interruttore) e' in `TestS26Bingo.FINAL_MODEL`
# e `TestS26Bingo.SWITCH_CHECKS`.
VARIANTS = {
    'bingo': (G2_FUEL, 'Strike', True, True, True, True, True, True, False, True),
    'none': (1.0, 'Strike', True, True, True, True, True, True, False, True),
    'switch_off': (BINGO_FUEL, 'Strike', True, True, False, True, True, True, False, True),
    'no_base': (DRY_FUEL, 'Strike', False, True, True, True, True, True, False, True),
    'bingo_off': (DRY_FUEL, 'Strike', True, False, True, True, True, True, False, True),
    'reverse_off': (BINGO_FUEL, 'Strike', True, True, True, False, False, True, False, True),
    'reserve_off': (BINGO_FUEL, 'Strike', True, True, True, True, False, True, False, True),
    'transfer_continue': (G2_FUEL, 'Transport', True, True, True, True, True, True, False, True),
    'transfer_return': (DRY_FUEL, 'Transport', True, True, True, True, True, True, False, True),
    'engagement_fuel_off': (1.0, 'Strike', True, True, True, True, True, False, False, True),
    'post_engagement_bingo': (BINGO_FUEL, 'Strike', True, True, True, True, True, True, True, True),
    'replan_off': (BINGO_FUEL, 'Strike', True, True, True, True, True, True, True, False),
}


def _seeds(prefix: str, count: int = SEEDS_PER_SCENARIO):
    return [f'{prefix}-{index}' for index in range(count)]


def _shots_by(outcome, prefix: str):
    return [event for event in outcome.ammunition_events if event.asset_id.startswith(prefix + '/')]


def _mission_id(variant: str) -> str:
    return f'{FLIGHT}:{VARIANTS[variant][1]}'


def _scenario(variant: str) -> F.Scenario:
    fuel, mission_type, with_base, bingo, _, _, _, _, near, _ = VARIANTS[variant]
    flight = F.build_force(FLIGHT, 'Blue', [F.Unit('aircraft', 'F-16C Block 52d', 1,
                                                   origin=(*FLIGHT_START, FLIGHT_ALTITUDE), prefix='f',
                                                   loadout='Strike',
                                                   sensors={'ground': NEAR_JET_GROUND_SENSOR} if near else None)],
                           mil_category=F.AIR_UNIT)

    for asset in flight.assets.values():
        asset.fuel = fuel

    mission, = F.missions_for(flight, [FLIGHT_END], mission_type=mission_type,
                              target=F.zone_target(FLIGHT_END, 10_000.0), speed=AIR_SPEED)

    if not bingo:
        mission = dataclasses.replace(mission, end_criteria=EndCriteria(bingo=False))

    sites = [F.build_force(SITE, 'Red', [F.Unit('vehicle', 'BMP-2', 1, origin=SITE_POSITION, prefix='ifv',
                                                sensors={'air': SITE_SENSOR_RANGE})])]
    blue = [flight]
    bases = [(BASE, BASE_POSITION)] if with_base else []

    if near:
        sites.insert(0, F.build_force(NEAR_SITE, 'Red', [F.Unit('vehicle', 'BMP-2', 1, origin=NEAR_SITE_POSITION,
                                                                prefix='ifv', sensors={'air': SITE_SENSOR_RANGE})]))
        bases.append((ALTERNATE_BASE, ALTERNATE_BASE_POSITION))

    for name, position in bases:
        base = F.make_force(name, 'Blue', F.AIR_UNIT)
        F.add_assets(base, [F.make_structure(base, f'{name}/depot0', position, category='Farp',
                                             asset_type='Oil_Tank')])
        blue.append(base)

    roles = {asset_id: 'unarmed' for asset_id in flight.assets}
    # Tiro Red SENZA effetto, solo contro aerei in volo: si misura se l'F-16C entra nel raggio del sensore.
    overrides = {asset_id: {'air': MARKER_SHOT} for site in sites for asset_id in site.assets}
    return F.Scenario(forces_a=blue, forces_b=sites, missions=[mission],
                      fire_control=F.make_fire_control(roles=roles, overrides=overrides), duration=DURATION,
                      roles=roles)


def _validate(scenario: F.Scenario, variant: str):
    """Il validatore di pianificazione sulla missione dello scenario NON ancora eseguito, con la regola della
    variante (gli stessi interruttori dell'esecutore): (esito, errore)."""
    _, _, _, _, _, reverse, reserve, _, _, _ = VARIANTS[variant]
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
    _, _, _, _, bingo, reverse, reserve, engagement_fuel, _, replan = VARIANTS[variant]

    with patch.object(SS, 'F6_BINGO', SS.F6_BINGO and bingo), \
            patch.object(SS, 'F6_BINGO_REVERSE_ROUTE', SS.F6_BINGO_REVERSE_ROUTE and reverse), \
            patch.object(SS, 'F6_BINGO_DISENGAGE_RESERVE', SS.F6_BINGO_DISENGAGE_RESERVE and reserve), \
            patch.object(SS, 'G3_ENGAGEMENT_FUEL', SS.G3_ENGAGEMENT_FUEL and engagement_fuel), \
            patch.object(SS, 'G4_REPLAN', SS.G4_REPLAN and replan), \
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
    """S26-BINGO: il bingo del modello finale (soglia del G2 e albero di decisione per combattimento e trasferimento,
    bingo a priori nel validatore, consumo d'ingaggio del G3, bingo dopo l'episodio del G4b, regole della F6-A senza
    base o senza bingo) e la controprova degli interruttori (le regole storiche F6-B2 e F6-B2bis, la F6-A senza
    consumo d'ingaggio, il G3 senza ri-pianificazione)."""

    SEEDS = _seeds('S26-BINGO')
    # Ordine d'esecuzione = ordine d'introduzione (chiavi della fotografia, stabili); il ruolo di ogni variante e' in
    # `FINAL_MODEL` / `SWITCH_CHECKS`.
    VARIANTS = tuple(VARIANTS)
    JET = f'{FLIGHT}/f0'
    FINAL_MODEL = ('none', 'bingo', 'transfer_return', 'transfer_continue', 'no_base', 'bingo_off',
                   'post_engagement_bingo')
    # Variante di controprova -> interruttore spento (la regola che ne risulta).
    SWITCH_CHECKS = {
        'switch_off': 'F6_BINGO',                       # nessun bingo
        'reverse_off': 'F6_BINGO_REVERSE_ROUTE',        # F6-B2 (con il G2 spento): rettilineo, riserva fissa
        'reserve_off': 'F6_BINGO_DISENGAGE_RESERVE',    # F6-B2bis: ritroso con il fattore 1,2
        'engagement_fuel_off': 'G3_ENGAGEMENT_FUEL',    # F6-A: movimento al regime 'max' dopo l'ingaggio
        'replan_off': 'G4_REPLAN',                      # G3 senza ri-pianificazione dopo l'episodio
    }
    # Modello finale: bingo alla partenza con rientro (G2).
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

    def _assert_bingo_time(self, variant, bingo):
        """Il bingo annunciato a priori dal validatore e' quello eseguito in sessione, in ogni replica."""
        self.assertIn(f't={bingo.time:.1f} s', str(self.validations[variant][1]))

        for outcome, _, _, _ in self.runs[variant]:
            self.assertAlmostEqual(self._mission(outcome, variant).asset_outcomes[self.JET].end_time,
                                   bingo.time, delta=1e-6)

    def _assert_bingo_outcome(self, variant, time, left, events):
        """Esito di un rientro per bingo: asset OPERATIONAL con motivo BINGO all'istante `time`, missione
        ABORTED(BINGO), postura a terra, punto finale non raggiunto, `events` FuelEvent senza esaurimento e `left`
        carburante a bordo; Red-Site, oltre il punto di bingo, non spara mai."""
        for outcome, _, _, jet in self.runs[variant]:
            mission = self._mission(outcome, variant)
            asset = mission.asset_outcomes[self.JET]
            self.assertEqual((mission.status, mission.reason), (MissionStatus.ABORTED, AbortReason.BINGO))
            self.assertEqual((asset.state, asset.end_reason), (AssetState.OPERATIONAL, AssetEndReason.BINGO))
            self.assertIsNone(asset.crew_recovered)
            self.assertAlmostEqual(asset.end_time, time, delta=1e-3)
            self.assertEqual(mission.actual_etas, (0.0, None))
            self.assertEqual(outcome.postures[self.JET], MA.PARKED_POSTURE)
            self.assertFalse(jet.is_destroyed())
            fuel_events = [e for e in outcome.fuel_events if e.asset_id == self.JET]
            self.assertEqual(len(fuel_events), events, variant)
            self.assertFalse(any(event.exhausted for event in fuel_events))
            self.assertAlmostEqual(jet.fuel, left, delta=1e-9)
            self.assertEqual(_shots_by(outcome, SITE), [], (variant, outcome.session_id))

    def _assert_route_completed(self, variant):
        for outcome, legs, _, jet in self.runs[variant]:
            mission = self._mission(outcome, variant)
            self.assertEqual(mission.status, MissionStatus.COMPLETED, variant)
            self.assertEqual(mission.asset_outcomes[self.JET].end_reason, AssetEndReason.ROUTE_COMPLETED)
            self.assertAlmostEqual(legs[self.JET][-1].t_end, (FLIGHT_END[0] - FLIGHT_START[0]) / AIR_SPEED,
                                   delta=1e-6)
            self.assertGreater(jet.fuel, 0.0, variant)
            self.assertEqual([event for event in outcome.fuel_events if event.exhausted], [], variant)

    def _firing(self, variant):
        return sum(1 for outcome, _, _, _ in self.runs[variant] if _shots_by(outcome, SITE))

    # ── Dati di test ──────────────────────────────────────────────────────────────

    def test_variants_split_into_final_model_and_switch_checks(self):
        """Ogni variante e' del modello finale o di controprova (una sola delle due); le varianti di controprova
        spengono ciascuna un interruttore del motore che, di default, e' acceso."""
        self.assertEqual(set(self.FINAL_MODEL) | set(self.SWITCH_CHECKS), set(self.VARIANTS))
        self.assertFalse(set(self.FINAL_MODEL) & set(self.SWITCH_CHECKS))

        for variant in self.FINAL_MODEL:
            self.assertTrue(all(VARIANTS[variant][4:8]) and VARIANTS[variant][9], variant)

        # Posizione dell'interruttore nella tupla della variante.
        index = {'F6_BINGO': 4, 'F6_BINGO_REVERSE_ROUTE': 5, 'F6_BINGO_DISENGAGE_RESERVE': 6, 'G3_ENGAGEMENT_FUEL': 7,
                 'G4_REPLAN': 9}

        for variant, switch in self.SWITCH_CHECKS.items():
            self.assertIs(getattr(SS, switch), True, switch)
            self.assertFalse(VARIANTS[variant][index[switch]], variant)

    def test_declared_fuels(self):
        """I carburanti di test stanno dove dichiarato: 0,15 < rotta < rotta di combattimento < 0,27 < soglia del
        G2 < 0,28."""
        route, combat, threshold = self._threshold()
        self.assertLess(DRY_FUEL, route)
        self.assertLess(route, combat)
        self.assertLess(combat, G2_FUEL)
        self.assertLess(G2_FUEL, threshold)
        self.assertLess(threshold, BINGO_FUEL)

    # ── Modello finale ────────────────────────────────────────────────────────────

    def test_the_validator_rejects_what_would_reach_bingo(self):
        """A priori (G2): 'bingo', 'transfer_continue' (sotto il minimo anche se poi continua), 'transfer_return' e
        'no_base' rifiutate con soglia e decisione; 'none' accettata con margine >= 0; 'bingo_off' non
        controllata."""
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

    def test_rejected_a_priori_is_exactly_bingo_in_flight(self):
        """Stesso criterio (G2): il bingo che il validatore annuncia (`mission_bingo_decision`) e' quello eseguito in
        sessione; dove il validatore accetta ('none'), nessun bingo."""
        for variant in self.AT_START:
            scenario = _scenario(variant)
            mission, = scenario.missions
            movement, = MA.mission_movements(mission)
            self._assert_bingo_time(variant, MA.mission_bingo_decision(
                mission, movement, scenario.force(FLIGHT).assets[self.JET],
                MA.air_base_points(scenario.forces_a, 'Blue')))

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

    def test_bingo_at_departure_is_aborted_with_the_descent_on_board(self):
        """'bingo' e 'transfer_return': esito BINGO all'istante 0, ABORTED(BINGO), a terra sulla base, un FuelEvent
        (la discesa), a bordo il carburante di partenza meno la discesa; Red-Site non spara mai."""
        jet = self._jet()
        spawn, landing = _spawn_and_base()
        descent = math.dist(spawn, landing) / jet.fuel_autonomy()

        for variant, start in (('bingo', G2_FUEL), ('transfer_return', DRY_FUEL)):
            self._assert_bingo_outcome(variant, 0.0, start - descent, 1)

    def test_without_bingo_the_route_is_completed_and_red_fires(self):
        """'none': rotta completata (COMPLETED, ROUTE_COMPLETED), aereo fuori scena alla fine della rotta; l'F-16C
        passa sopra Red-Site, che spara nella maggior parte delle repliche."""
        self._assert_route_completed('none')
        self.assertGreaterEqual(self._firing('none') / len(self.runs['none']), MIN_FIRING_FRACTION)

    def test_engagement_fuel(self):
        """G3 ('none'): il movimento e' alla crociera e, se Red spara, l'F-16C (bersaglio delle salve) consuma in
        piu' la riserva di disimpegno all'istante del primo lancio contro di lui, con un evento istantaneo prima del
        tratto; se Red non spara, nessun consumo d'ingaggio."""
        route, _, _ = self._threshold()
        charge = FM.engagement_fuel(self._jet())

        for outcome, _, _, jet in self.runs['none']:
            shots = _shots_by(outcome, SITE)
            events = [event for event in outcome.fuel_events if event.asset_id == self.JET]

            if shots:
                self.assertEqual([e.regime for e in events], [FM.ENGAGEMENT_REGIME, SS.CRUISE_REGIME])
                self.assertAlmostEqual(events[0].time, min(event.time for event in shots), delta=1e-9)
                self.assertAlmostEqual(events[0].amount, charge, delta=1e-12)
                self.assertAlmostEqual(jet.fuel, 1.0 - route - charge, delta=1e-9)
            else:
                self.assertEqual([e.regime for e in events], [SS.CRUISE_REGIME])
                self.assertAlmostEqual(jet.fuel, 1.0 - route, delta=1e-9)

    def test_transfer_continue_runs_dry_after_the_engagement(self):
        """'transfer_continue' (trasferimento sotto la soglia del G2 che alla partenza CONTINUA): se Red spara, il
        consumo d'ingaggio consuma la riserva e il residuo non basta piu' per la rotta. G4b: l'episodio dura oltre
        la fine della rotta, la decisione e' alla fine dei tratti dell'aereo con residuo zero (esaurito in
        ingaggio): regole della F6-A dal punto finale, nessuna base in planata, perso con l'equipaggio recuperato
        (DESTROYED, FUEL_EXHAUSTED a fine rotta), missione DESTROYED. Se Red non spara, la rotta e' completata con
        carburante positivo."""
        t_route = (FLIGHT_END[0] - FLIGHT_START[0]) / AIR_SPEED

        for outcome, legs, _, jet in self.runs['transfer_continue']:
            mission = self._mission(outcome, 'transfer_continue')
            asset = mission.asset_outcomes[self.JET]

            if not _shots_by(outcome, SITE):
                self.assertEqual(mission.status, MissionStatus.COMPLETED)
                self.assertGreater(jet.fuel, 0.0)
                continue

            self.assertEqual(mission.status, MissionStatus.DESTROYED)
            self.assertEqual((asset.state, asset.end_reason, asset.crew_recovered),
                             (AssetState.DESTROYED, AssetEndReason.FUEL_EXHAUSTED, True))
            self.assertAlmostEqual(asset.end_time, t_route, delta=1e-6)
            self.assertAlmostEqual(legs[self.JET][-1].t_end, t_route, delta=1e-6)
            self.assertEqual(jet.fuel, 0.0)
            self.assertTrue(jet.is_destroyed())
            self.assertEqual(outcome.postures[self.JET], MA.DESTROYED_POSTURE)

    def test_post_engagement_bingo_lands_on_the_alternate_base(self):
        """'post_engagement_bingo' (G4b): sopra la soglia alla partenza (nessun bingo al G2); dopo l'episodio con
        Red-Near il residuo analitico (partenza - crociera fino a fine episodio - consumo d'ingaggio) e' sotto il
        resto della rotta + la riserva: BINGO a fine episodio, ABORTED(BINGO), rientro sulla base ALTERNATIVA lungo
        la rotta (piu' breve del ritroso), a terra; Red-Site, piu' avanti, non spara mai. Carburante finale =
        partenza - consumo d'ingaggio - (rotta fino a x = 180 km + discesa sulla base) alla crociera."""
        jet = _scenario('post_engagement_bingo').force(FLIGHT).assets[self.JET]
        charge = FM.engagement_fuel(jet)
        rate = 1.0 / jet.fuel_autonomy()
        landing = (*ALTERNATE_BASE_POSITION, 0.0)
        flown = (ALTERNATE_BASE_POSITION[0] - FLIGHT_START[0]) + math.dist((ALTERNATE_BASE_POSITION[0], 0.0,
                                                                           FLIGHT_ALTITUDE), landing)
        t_route = (FLIGHT_END[0] - FLIGHT_START[0]) / AIR_SPEED
        reserve = FM.disengagement_reserve(jet)

        for outcome, legs, grounded, jet in self.runs['post_engagement_bingo']:
            near = _shots_by(outcome, NEAR_SITE)
            self.assertGreater(len(near), 0)
            self.assertEqual(_shots_by(outcome, SITE), [])
            mission = self._mission(outcome, 'post_engagement_bingo')
            asset = mission.asset_outcomes[self.JET]
            self.assertEqual((mission.status, mission.reason), (MissionStatus.ABORTED, AbortReason.BINGO))
            self.assertEqual((asset.state, asset.end_reason), (AssetState.OPERATIONAL, AssetEndReason.BINGO))
            self.assertGreater(asset.end_time, max(event.time for event in near))
            # Alla decisione: residuo sotto la soglia (resto della rotta + riserva), ricalcolata qui.
            residual = BINGO_FUEL - charge - AIR_SPEED * asset.end_time * rate
            rest = AIR_SPEED * (t_route - asset.end_time) * rate
            self.assertLess(residual, rest + reserve)
            self.assertGreater(residual, rest)
            *_, descent, parked = legs[self.JET]
            self.assertEqual((descent.p_end, parked.p_start, parked.p_end), (landing, landing, landing))
            self.assertTrue(grounded.at(self.JET, parked.t_start + 1.0))
            self.assertEqual(outcome.postures[self.JET], MA.PARKED_POSTURE)
            self.assertAlmostEqual(jet.fuel, BINGO_FUEL - charge - flown * rate, delta=1e-9)

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

    # ── Controprova degli interruttori ───────────────────────────────────────────

    def test_switch_off_flies_the_whole_route(self):
        """'switch_off' (`F6_BINGO` spento, 0,28): nessun bingo, rotta completata; la sola andata + un consumo
        d'ingaggio (G3) non esauriscono il carburante; Red spara come in 'none'."""
        self._assert_route_completed('switch_off')
        self.assertGreaterEqual(self._firing('switch_off') / len(self.runs['switch_off']), MIN_FIRING_FRACTION)

    def test_reverse_off_is_the_straight_return_of_f6_b2(self):
        """'reverse_off' (G2 e `F6_BINGO_REVERSE_ROUTE` spenti): la F6-B2 com'era. Il validatore rifiuta con la
        regola della riserva e annuncia il bingo eseguito (`Fuel_Model.bingo_point` senza regola); rientro in linea
        retta dal punto di bingo alla base (a quota 0) con la riserva, prima che con il ritroso (la riserva fissa di
        0,1 pesa piu' del 20% del ritorno su questa rotta); esito BINGO con la riserva a bordo (andata e rientro)."""
        jet = self._jet()
        _, error = self.validations['reverse_off']
        self.assertIn(f"{self.JET!r} does not return with the fuel reserve", str(error))
        scenario = _scenario('reverse_off')
        movement, = MA.mission_movements(scenario.missions[0])
        self._assert_bingo_time('reverse_off', FM.bingo_point(
            scenario.force(FLIGHT).assets[self.JET], MA.airborne_legs(movement),
            MA.air_base_points(scenario.forces_a, 'Blue')))

        t_bingo, point, t_land = _expected_straight_bingo(jet, BINGO_FUEL)
        landing = (*BASE_POSITION, 0.0)

        for _, legs, _, _ in self.runs['reverse_off']:
            outbound, back, parked = legs[self.JET]
            self.assertAlmostEqual(outbound.t_end, t_bingo, delta=1e-3)

            for got, want in zip(back.p_start, point):
                self.assertAlmostEqual(got, want, delta=1e-3)

            self.assertEqual(back.p_end, landing)
            self.assertAlmostEqual(back.t_end, t_land, delta=1e-3)
            self.assertEqual((parked.p_start, parked.p_end), (landing, landing))

        self.assertLess(t_bingo, _expected_bingo(jet, BINGO_FUEL)[0])
        self._assert_bingo_outcome('reverse_off', t_bingo, FM.BINGO_RESERVE, 2)

    def test_reserve_off_retraces_the_route_as_in_f6_b2bis(self):
        """'reserve_off' (G2 spento): la F6-B2bis com'era. Il validatore rifiuta con la regola 1,2 e annuncia il
        bingo eseguito (`Fuel_Model.bingo_point` con la regola della missione); rotta fino al bingo, ritroso in quota
        fino al punto di comparsa, discesa sulla base (a quota 0) con il tratto diretto, alla crociera, poi fermo a
        terra; esito BINGO con il 20% del ritorno a bordo (andata e due tratti di rientro)."""
        jet = self._jet()
        _, error = self.validations['reserve_off']
        self.assertIn(f"{self.JET!r} does not keep the bingo fuel", str(error))
        scenario = _scenario('reserve_off')
        mission, = scenario.missions
        movement, = MA.mission_movements(mission)
        self._assert_bingo_time('reserve_off', FM.bingo_point(
            scenario.force(FLIGHT).assets[self.JET], MA.airborne_legs(movement),
            MA.air_base_points(scenario.forces_a, 'Blue'), rule=MA.bingo_return_rule(mission)))

        t_bingo, point, t_land, length = _expected_bingo(jet, BINGO_FUEL)
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

        self._assert_bingo_outcome('reserve_off', t_bingo,
                                   (FM.BINGO_RETURN_FACTOR - 1.0) * length / jet.fuel_autonomy(), 3)

    def test_engagement_fuel_off_is_the_max_regime_of_f6_a(self):
        """'engagement_fuel_off' (G3 spento, pieno): la regola della F6-A, tutto il movimento al regime di
        combattimento se Red spara, nessun consumo d'ingaggio; rotta completata. Stesso seed, stessa sessione: il G3
        cambia solo il carburante, non chi spara."""
        route, combat, _ = self._threshold()
        self._assert_route_completed('engagement_fuel_off')

        for outcome, _, _, jet in self.runs['engagement_fuel_off']:
            shots = _shots_by(outcome, SITE)
            events = [event for event in outcome.fuel_events if event.asset_id == self.JET]
            self.assertEqual([e.regime for e in events], [SS.COMBAT_REGIME if shots else SS.CRUISE_REGIME])
            self.assertAlmostEqual(jet.fuel, 1.0 - (combat if shots else route), delta=1e-9)

        self.assertEqual(self._firing('none'), self._firing('engagement_fuel_off'))
        self.assertGreater(self._firing('none'), 0)

    def test_replan_off_flies_on_to_the_second_site(self):
        """'replan_off' (G4b spento, lo scenario di 'post_engagement_bingo'): nessuna ri-pianificazione, l'aereo
        prosegue, Red-Site spara, due consumi d'ingaggio, rotta completata con il contatore a zero (il limite del
        G3)."""
        for outcome, legs, _, jet in self.runs['replan_off']:
            self.assertGreater(len(_shots_by(outcome, NEAR_SITE)), 0)
            self.assertGreater(len(_shots_by(outcome, SITE)), 0)
            mission = self._mission(outcome, 'replan_off')
            self.assertEqual(mission.status, MissionStatus.COMPLETED)
            self.assertEqual([e.regime for e in outcome.fuel_events if e.asset_id == self.JET].count(
                FM.ENGAGEMENT_REGIME), 2)
            self.assertEqual(jet.fuel, 0.0)


if __name__ == '__main__':
    unittest.main()
