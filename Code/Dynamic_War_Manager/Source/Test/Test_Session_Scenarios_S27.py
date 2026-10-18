"""Scenario S27 del motore di sessioni virtuali: doppio ingaggio dello stesso aereo nella stessa sessione (G5 del
nuovo modello di bingo, chiusura del piano G1-G5).

Prosegue `Test_Session_Scenarios.py` (S1-S9), `Test_Session_Scenarios_S10_S18.py`, gli S19-S26 con la
stessa disciplina: si verifica un comportamento QUALITATIVO o STRUTTURALE, mai un numero calibrato.

Il nuovo modello di bingo (G1-G4, decisioni dell'utente del 2026-10-15/17, v. `Logic/Session_Simulator`, "Episodi
d'ingaggio (G4a)" e "Ri-pianificazione dopo l'episodio (G4b)", e `Logic/Fuel_Model`, "Soglia di bingo e albero di
decisione" e "Consumo in ingaggio") nel caso che il G4 ha reso possibile: DUE episodi d'ingaggio dello stesso aereo,
separati da piu' di `Session_Simulator.EPISODE_GAP` (300 s). Prima del G4a l'ingaggio era la componente connessa di
forze dell'intera sessione: un solo consumo d'ingaggio (G3) per sessione e nessuna decisione "dopo l'ingaggio".
Qui:
  * due consumi d'ingaggio (G3, la riserva di disimpegno a ogni episodio, `Fuel_Model.engagement_fuel`) per lo
    stesso aereo nella stessa sessione, all'istante del primo lancio contro di lui in ciascun episodio;
  * ri-pianificazione (G4b) alla fine di CIASCUN episodio con il residuo analitico: dopo il primo il residuo resta
    sopra la soglia (resto della rotta + riserva) e l'aereo prosegue; dopo il secondo e' sotto: bingo, regola di
    combattimento, rientro sulla base alternativa lungo la rotta (piu' breve del ritroso, che ripasserebbe sopra
    entrambe le minacce);
  * il trasferimento ('Transport') nella stessa situazione CONTINUA (il residuo basta per concludere la rotta,
    consumando la riserva);
  * controprova degli interruttori: `G4_REPLAN` spento (due consumi, nessun bingo), `G4_EPISODES` spento (la
    componente connessa: un solo consumo, il limite di prima), `G3_ENGAGEMENT_FUEL` spento (nessun consumo
    d'ingaggio, la regola 'max' della F6-A, nessuna ri-pianificazione per il bingo).

## S27-DOUBLE (`TestS27DoubleEngagement`)

Blue-Flight: un F-16C 'Strike' (ruolo 'unarmed', autonomia di crociera del registro col loadout 'Strike': 1570 km,
'max' 1140 km, consumo d'ingaggio = riserva di disimpegno ~0,0852 del pieno) in volo a 5000 m da (10 km, 0) verso
(510 km, 0) a 250 m/s (2000 s): rotta 0,318 del pieno alla crociera (0,439 al regime di combattimento). Sensore
'ground' dell'F-16C DICHIARATO di 20 km (come S26 'post_engagement_bingo': col radar del registro le finestre sui
due siti sarebbero piu' lunghe). Red-First (BMP-2 in (100 km, 0)) e Red-Second (BMP-2 in (300 km, 0)), sensore 'air'
DICHIARATO di 40 km e tiro DICHIARATO senza effetto (precisione 0, lo stesso marcatore di S26) contro gli aerei: le
finestre sono ~[160, 520] s e ~[1000, 1320] s, separate da ~480 s (> `EPISODE_GAP`): due episodi. Blue-Base: base
aerea (deposito) in (0, 0), a 10 km dalla rotta (la base di partenza del ritroso). Blue-Alternate: base aerea in
(400 km, 2 km), entro `Fuel_Model.ALTERNATE_BASE_MAX_OFFSET` dalla rotta, oltre il raggio di Red-Second (60 km dopo
la fine della sua finestra). Carburante di partenza `DOUBLE_FUEL` 0,53 (v. sotto). Varianti per seed (nomi stabili
nella fotografia, nell'ordine):
  * 'double' (modello finale): se entrambi i siti sparano, due consumi d'ingaggio; dopo il primo episodio nessun
    bingo (residuo >= resto + riserva); dopo il secondo BINGO, ABORTED(BINGO), rientro lungo la rotta sulla base
    alternativa (~60 km + discesa) e a terra. Se spara un solo sito, un consumo e nessun bingo (rotta completata);
  * 'transfer' (missione 'Transport', stesso carburante): dopo il secondo episodio e' sotto la soglia ma il residuo
    basta per la rotta: CONTINUA, rotta completata con il residuo = partenza - rotta - due consumi (> 0);
  * 'replan_off' (`G4_REPLAN` spento): due consumi, nessuna ri-pianificazione, rotta completata con lo stesso
    residuo del trasferimento;
  * 'episodes_off' (`G4_EPISODES` spento, quindi nemmeno il G4b): un solo ingaggio per la componente connessa, un
    solo consumo d'ingaggio (il limite "uno per sessione" che il G4 risolve), rotta completata;
  * 'engagement_fuel_off' (`G3_ENGAGEMENT_FUEL` spento): nessun consumo d'ingaggio, tutto il movimento al regime
    di combattimento se un sito spara (F6-A), nessun bingo, rotta completata.

Asserzioni: invarianti per replica (consumi, istanti, decisioni, esiti, carburante finale ricalcolato qui dalla
rotta e dai consumi) condizionate a quali siti hanno sparato nella replica (il rilevamento e' un'estrazione per
finestra), e una frazione aggregata con soglia DICHIARATA (stima di test, non tarata sul risultato). Le decisioni
della ri-pianificazione sono lette da uno spia su `Mission_Adapter.mission_bingo_decision` (le chiamate con
`time`, cioe' quelle dopo un episodio).
"""

import dataclasses
import math
import unittest
from unittest.mock import patch

from Code.Dynamic_War_Manager.Source.Command.Mission_Types import (
    AbortReason,
    AssetEndReason,
    AssetState,
    MissionStatus,
)
from Code.Dynamic_War_Manager.Source.Logic import Contact_Scheduler as CS
from Code.Dynamic_War_Manager.Source.Logic import Fuel_Model as FM
from Code.Dynamic_War_Manager.Source.Logic import Mission_Adapter as MA
from Code.Dynamic_War_Manager.Source.Logic import Session_Simulator as SS
from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F

DURATION = 3_600.0
SEEDS_PER_SCENARIO = 8

# ── Costanti di S27-DOUBLE [m, m/s, s], dichiarate di test (come S24-S26) ──────────────
FLIGHT, BASE, ALTERNATE_BASE = 'Blue-Flight', 'Blue-Base', 'Blue-Alternate'
FIRST_SITE, SECOND_SITE = 'Red-First', 'Red-Second'
FLIGHT_ALTITUDE = 5_000.0
AIR_SPEED = 250.0
FLIGHT_START, FLIGHT_END = (10_000.0, 0.0), (510_000.0, 0.0)
BASE_POSITION = (0.0, 0.0)
FIRST_SITE_POSITION = (100_000.0, 0.0)
SECOND_SITE_POSITION = (300_000.0, 0.0)
ALTERNATE_BASE_POSITION = (400_000.0, 2_000.0)
SITE_SENSOR_RANGE = 40_000.0
# Sensore 'ground' DICHIARATO dell'F-16C (valore di test, non un dato), lo stesso di S26 'post_engagement_bingo':
# le finestre sono quelle del sensore 'air' dei siti.
JET_GROUND_SENSOR = 20_000.0
# Carburante dell'F-16C [frazione del pieno]: valore di test, non un dato, verificato nel test (`test_declared_fuels`)
# contro la rotta e il consumo d'ingaggio ricalcolati dal registro. Con il solo movimento alla crociera residuo e
# resto della rotta calano insieme, quindi dopo k consumi d'ingaggio c (= riserva di disimpegno) l'aereo e' in bingo
# se e solo se carburante < rotta + (k + 1) c, ovunque sia lungo la rotta: 0,53 sta fra rotta + 2c (~0,489, sopra
# la soglia dopo il primo episodio) e rotta + 3c (~0,574, sotto dopo il secondo), con margine ~0,04 da entrambe le
# parti; basta anche per la rotta intera al regime di combattimento (~0,439, 'engagement_fuel_off').
DOUBLE_FUEL = 0.53
MARKER_SHOT = dataclasses.replace(F.SHOTS['sam'], accuracy=0.0, weapon='test:marker')

# Soglia della frazione aggregata sui seed: DICHIARATA di test, non tarata sul risultato (stessa stima di S22-S26:
# il rilevamento e' un'estrazione per finestra e osservatore, 0,5 = "la regola, non l'eccezione").
MIN_FIRING_FRACTION = 0.5

# Variante -> (tipo di missione, G4_EPISODES, G4_REPLAN, G3_ENGAGEMENT_FUEL). Ordine stabile nella fotografia.
VARIANTS = {
    'double': ('Strike', True, True, True),
    'transfer': ('Transport', True, True, True),
    'replan_off': ('Strike', True, False, True),
    'episodes_off': ('Strike', False, True, True),
    'engagement_fuel_off': ('Strike', True, True, False),
}


def _seeds(prefix: str, count: int = SEEDS_PER_SCENARIO):
    return [f'{prefix}-{index}' for index in range(count)]


def _shots_by(outcome, prefix: str):
    return [event for event in outcome.ammunition_events if event.asset_id.startswith(prefix + '/')]


def _mission_id(variant: str) -> str:
    return f'{FLIGHT}:{VARIANTS[variant][0]}'


def _scenario(variant: str) -> F.Scenario:
    mission_type = VARIANTS[variant][0]
    flight = F.build_force(FLIGHT, 'Blue', [F.Unit('aircraft', 'F-16C Block 52d', 1,
                                                   origin=(*FLIGHT_START, FLIGHT_ALTITUDE), prefix='f',
                                                   loadout='Strike', sensors={'ground': JET_GROUND_SENSOR})],
                           mil_category=F.AIR_UNIT)

    for asset in flight.assets.values():
        asset.fuel = DOUBLE_FUEL

    mission, = F.missions_for(flight, [FLIGHT_END], mission_type=mission_type,
                              target=F.zone_target(FLIGHT_END, 10_000.0), speed=AIR_SPEED)
    sites = [F.build_force(name, 'Red', [F.Unit('vehicle', 'BMP-2', 1, origin=position, prefix='ifv',
                                                sensors={'air': SITE_SENSOR_RANGE})])
             for name, position in ((FIRST_SITE, FIRST_SITE_POSITION), (SECOND_SITE, SECOND_SITE_POSITION))]
    blue = [flight]

    for name, position in ((BASE, BASE_POSITION), (ALTERNATE_BASE, ALTERNATE_BASE_POSITION)):
        base = F.make_force(name, 'Blue', F.AIR_UNIT)
        F.add_assets(base, [F.make_structure(base, f'{name}/depot0', position, category='Farp',
                                             asset_type='Oil_Tank')])
        blue.append(base)

    roles = {asset_id: 'unarmed' for asset_id in flight.assets}
    # Tiro Red SENZA effetto, solo contro aerei in volo: si misura se e quando l'F-16C entra nel raggio del sensore.
    overrides = {asset_id: {'air': MARKER_SHOT} for site in sites for asset_id in site.assets}
    return F.Scenario(forces_a=blue, forces_b=sites, missions=[mission],
                      fire_control=F.make_fire_control(roles=roles, overrides=overrides), duration=DURATION,
                      roles=roles)


def _run(scenario: F.Scenario, session_id: str, variant: str):
    """Esegue lo scenario con gli interruttori della variante, registrando i tratti dati allo scheduler e le
    decisioni di bingo della ri-pianificazione (le chiamate a `mission_bingo_decision` con `time`: (istante,
    residuo, decisione))."""
    _, episodes, replan, engagement_fuel = VARIANTS[variant]
    decisions = []
    original = MA.mission_bingo_decision

    def spy(*args, **kwargs):
        decision = original(*args, **kwargs)

        if kwargs.get('time') is not None:
            decisions.append((kwargs['time'], kwargs.get('fuel'), decision))

        return decision

    with patch.object(SS, 'G4_EPISODES', SS.G4_EPISODES and episodes), \
            patch.object(SS, 'G4_REPLAN', SS.G4_REPLAN and replan), \
            patch.object(SS, 'G3_ENGAGEMENT_FUEL', SS.G3_ENGAGEMENT_FUEL and engagement_fuel), \
            patch.object(MA, 'mission_bingo_decision', spy), \
            patch.object(CS, 'schedule_contacts', wraps=CS.schedule_contacts) as scheduler:
        outcome = scenario.run(session_id)

    # Il primo scheduling (la ri-pianificazione lo riesegue sulle sole coppie degli aerei ri-pianificati).
    return outcome, scheduler.call_args_list[0].kwargs['legs'], scheduler.call_args_list[0].kwargs['grounded'], \
        decisions


class TestS27DoubleEngagement(F.LoggerSilencer, unittest.TestCase):
    """S27-DOUBLE: due episodi d'ingaggio dello stesso aereo, due consumi d'ingaggio, ri-pianificazione dopo ciascuno,
    bingo solo dopo il secondo (combattimento) o continuazione (trasferimento); controprova degli interruttori G3/G4."""

    SEEDS = _seeds('S27-DOUBLE')
    VARIANTS = tuple(VARIANTS)
    JET = f'{FLIGHT}/f0'
    # Varianti in cui il jet completa la rotta qualunque cosa accada.
    COMPLETING = ('transfer', 'replan_off', 'episodes_off', 'engagement_fuel_off')

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                scenario = _scenario(variant)
                outcome, legs, grounded, decisions = _run(scenario, session_id, variant)
                cls.runs[variant].append((outcome, legs, grounded, decisions,
                                          scenario.force(FLIGHT).assets[cls.JET]))

    def _jet(self, variant='double'):
        return _scenario(variant).force(FLIGHT).assets[self.JET]

    def _mission(self, outcome, variant):
        return outcome.mission_outcomes[_mission_id(variant)]

    def _route(self):
        """(rotta alla crociera, rotta al regime di combattimento, consumo d'ingaggio), ricalcolati dal registro."""
        scenario = _scenario('double')
        mission, = scenario.missions
        jet = scenario.force(FLIGHT).assets[self.JET]
        movement, = MA.mission_movements(mission)
        route = MA.route_fuel_demand(jet, MA.airborne_legs(movement))
        combat = jet.fuel_for_distance(FLIGHT_END[0] - FLIGHT_START[0], 'max')
        return route, combat, FM.engagement_fuel(jet)

    def _charges(self, outcome):
        return [event for event in outcome.fuel_events
                if event.asset_id == self.JET and event.regime == FM.ENGAGEMENT_REGIME]

    def _fired(self, outcome):
        """Siti che hanno sparato nella replica, nell'ordine lungo la rotta."""
        return tuple(site for site in (FIRST_SITE, SECOND_SITE) if _shots_by(outcome, site))

    def test_declared_fuels(self):
        """Il carburante di test sta dove dichiarato: rotta + 2c <= 0,53 < rotta + 3c (c = consumo d'ingaggio =
        riserva di disimpegno) e la rotta al regime di combattimento ci sta; la geometria dichiarata separa le due
        finestre dei siti di piu' di `EPISODE_GAP`."""
        route, combat, charge = self._route()
        self.assertAlmostEqual(charge, FM.disengagement_reserve(self._jet()), delta=1e-12)
        self.assertLessEqual(route + 2.0 * charge, DOUBLE_FUEL)
        self.assertLess(DOUBLE_FUEL, route + 3.0 * charge)
        self.assertLess(combat, DOUBLE_FUEL)
        first_out = (FIRST_SITE_POSITION[0] + SITE_SENSOR_RANGE - FLIGHT_START[0]) / AIR_SPEED
        second_in = (SECOND_SITE_POSITION[0] - SITE_SENSOR_RANGE - FLIGHT_START[0]) / AIR_SPEED
        self.assertGreater(second_in - first_out, SS.EPISODE_GAP)
        # La base alternativa e' entro l'offset dalla rotta e oltre il raggio di Red-Second.
        self.assertLessEqual(abs(ALTERNATE_BASE_POSITION[1]), FM.ALTERNATE_BASE_MAX_OFFSET)
        self.assertGreater(ALTERNATE_BASE_POSITION[0] - SECOND_SITE_POSITION[0], SITE_SENSOR_RANGE)

    def test_both_sites_fire_in_most_replicas(self):
        """Il caso del G5 (due episodi con fuoco) e' la regola, non l'eccezione, nella variante finale."""
        both = sum(1 for outcome, *_ in self.runs['double'] if len(self._fired(outcome)) == 2)
        self.assertGreaterEqual(both / len(self.runs['double']), MIN_FIRING_FRACTION, both)

    def test_two_episodes_two_engagement_charges(self):
        """G3 + G4a ('double', 'transfer', 'replan_off'): un consumo d'ingaggio per ogni sito che spara, ciascuno
        all'istante del primo lancio di quel sito (episodi distinti), di quantita' c; due episodi d'ingaggio con la
        forza del jet quando sparano entrambi."""
        charge = FM.engagement_fuel(self._jet())

        for variant in ('double', 'transfer', 'replan_off'):
            for outcome, *_ in self.runs[variant]:
                fired = self._fired(outcome)
                charges = self._charges(outcome)
                self.assertEqual(len(charges), len(fired), (variant, outcome.session_id))

                for event, site in zip(charges, fired):
                    self.assertAlmostEqual(event.time, min(e.time for e in _shots_by(outcome, site)), delta=1e-9)
                    self.assertAlmostEqual(event.amount, charge, delta=1e-12)

                engagements = [forces for forces in outcome.engagement_outcomes
                               if any(force.force_id == _mission_id(variant) for force in forces)]
                self.assertEqual(len(engagements), len(fired), (variant, outcome.session_id))

    def test_replanned_after_each_episode(self):
        """G4b ('double'): una decisione di bingo alla fine di ogni episodio con consumo; il residuo passato e'
        quello analitico (partenza - crociera fino all'istante - consumi fino all'istante). Dopo il primo: nessun
        bingo (residuo >= resto + riserva, ricalcolato qui); dopo il secondo: bingo, base alternativa."""
        jet = self._jet()
        rate = 1.0 / jet.fuel_autonomy()
        charge, reserve = FM.engagement_fuel(jet), FM.disengagement_reserve(jet)
        t_route = (FLIGHT_END[0] - FLIGHT_START[0]) / AIR_SPEED

        for outcome, _, _, decisions, _ in self.runs['double']:
            fired = self._fired(outcome)
            self.assertEqual(len(decisions), len(fired), outcome.session_id)

            for k, (time, residual, decision) in enumerate(decisions, start=1):
                self.assertAlmostEqual(residual, DOUBLE_FUEL - AIR_SPEED * time * rate - k * charge, delta=1e-9)
                rest = AIR_SPEED * (t_route - time) * rate

                if k == 2:
                    self.assertLess(residual, rest + reserve)
                    self.assertEqual(decision.action, FM.BINGO_ALTERNATE)
                    self.assertEqual(decision.base[:2], ALTERNATE_BASE_POSITION)
                else:
                    self.assertGreaterEqual(residual, rest + reserve)
                    self.assertIsNone(decision)

    def test_bingo_after_the_second_episode_lands_on_the_alternate_base(self):
        """'double' con entrambi i siti: BINGO alla fine del SECONDO episodio (dopo l'ultimo lancio di Red-Second),
        ABORTED(BINGO), rotta fino a x = 400 km e discesa sulla base alternativa, a terra; carburante finale =
        partenza - due consumi - (rotta fino a x = 400 km + discesa) alla crociera. Con un solo sito che spara:
        nessun bingo, rotta completata con un consumo."""
        jet = self._jet()
        charge, rate = FM.engagement_fuel(jet), 1.0 / jet.fuel_autonomy()
        route, _, _ = self._route()
        landing = (*ALTERNATE_BASE_POSITION, 0.0)
        flown = (ALTERNATE_BASE_POSITION[0] - FLIGHT_START[0]) + math.dist((ALTERNATE_BASE_POSITION[0], 0.0,
                                                                           FLIGHT_ALTITUDE), landing)

        for outcome, legs, grounded, decisions, jet in self.runs['double']:
            mission = self._mission(outcome, 'double')
            asset = mission.asset_outcomes[self.JET]
            fired = self._fired(outcome)

            if len(fired) < 2:
                self.assertEqual(mission.status, MissionStatus.COMPLETED, outcome.session_id)
                self.assertAlmostEqual(jet.fuel, DOUBLE_FUEL - route - len(fired) * charge, delta=1e-9)
                continue

            self.assertEqual((mission.status, mission.reason), (MissionStatus.ABORTED, AbortReason.BINGO))
            self.assertEqual((asset.state, asset.end_reason), (AssetState.OPERATIONAL, AssetEndReason.BINGO))
            self.assertGreater(asset.end_time, max(e.time for e in _shots_by(outcome, SECOND_SITE)))
            self.assertAlmostEqual(asset.end_time, decisions[-1][0], delta=1e-6)
            self.assertEqual(outcome.postures[self.JET], MA.PARKED_POSTURE)
            self.assertFalse(jet.is_destroyed())
            self.assertEqual([event for event in outcome.fuel_events if event.exhausted], [])
            self.assertAlmostEqual(jet.fuel, DOUBLE_FUEL - 2.0 * charge - flown * rate, delta=1e-9)

    def test_transfer_continues_after_the_second_episode(self):
        """'transfer' ('Transport', stesso carburante): sotto la soglia dopo il secondo episodio ma il residuo basta
        per la rotta: CONTINUA (`BINGO_CONTINUE`, nessun rientro), rotta completata, carburante finale = partenza -
        rotta - consumi."""
        route, _, charge = self._route()

        for outcome, _, _, decisions, jet in self.runs['transfer']:
            fired = self._fired(outcome)
            mission = self._mission(outcome, 'transfer')
            self.assertEqual(mission.status, MissionStatus.COMPLETED, outcome.session_id)
            self.assertEqual(mission.asset_outcomes[self.JET].end_reason, AssetEndReason.ROUTE_COMPLETED)
            self.assertEqual(len(decisions), len(fired))

            if len(fired) == 2:
                self.assertIsNone(decisions[0][2])
                self.assertEqual(decisions[1][2].action, FM.BINGO_CONTINUE)

            self.assertAlmostEqual(jet.fuel, DOUBLE_FUEL - route - len(fired) * charge, delta=1e-9)
            self.assertGreater(jet.fuel, 0.0)

    def test_switches_off(self):
        """Controprova degli interruttori, rotta sempre completata e nessuna decisione dopo l'episodio (salvo
        'transfer', sopra): 'replan_off' (G4b spento) un consumo per sito che spara e nessun bingo; 'episodes_off'
        (G4a spento) UN SOLO consumo per la componente connessa anche se sparano entrambi (il limite di prima);
        'engagement_fuel_off' (G3 spento) nessun consumo d'ingaggio, movimento al regime 'max' se un sito spara."""
        route, combat, charge = self._route()

        for variant in ('replan_off', 'episodes_off', 'engagement_fuel_off'):
            for outcome, _, _, decisions, jet in self.runs[variant]:
                fired = self._fired(outcome)
                mission = self._mission(outcome, variant)
                self.assertEqual(mission.status, MissionStatus.COMPLETED, (variant, outcome.session_id))
                self.assertEqual(mission.asset_outcomes[self.JET].end_reason, AssetEndReason.ROUTE_COMPLETED)
                self.assertEqual(decisions, [], variant)

                if variant == 'replan_off':
                    expected = DOUBLE_FUEL - route - len(fired) * charge
                    self.assertEqual(len(self._charges(outcome)), len(fired))
                elif variant == 'episodes_off':
                    expected = DOUBLE_FUEL - route - (charge if fired else 0.0)
                    self.assertEqual(len(self._charges(outcome)), 1 if fired else 0)
                    self.assertLessEqual(len(outcome.engagement_outcomes), 1)
                else:
                    expected = DOUBLE_FUEL - (combat if fired else route)
                    self.assertEqual(self._charges(outcome), [])

                self.assertAlmostEqual(jet.fuel, expected, delta=1e-9)

    def test_switches_do_not_change_who_fires(self):
        """Stesso seed: gli interruttori G3/G4b non cambiano chi spara (il bingo arriva dopo l'ultimo lancio di
        Red-Second): 'double', 'transfer', 'replan_off' ed 'engagement_fuel_off' hanno gli stessi siti che sparano."""
        for index in range(len(self.SEEDS)):
            fired = {variant: self._fired(self.runs[variant][index][0])
                     for variant in ('double', 'transfer', 'replan_off', 'engagement_fuel_off')}
            self.assertEqual(len(set(fired.values())), 1, (self.SEEDS[index], fired))


if __name__ == '__main__':
    unittest.main()
