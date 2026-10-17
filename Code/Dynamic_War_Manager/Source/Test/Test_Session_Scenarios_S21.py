"""Scenario S21 del motore di sessioni virtuali: attacco a una base con aerei parcheggiati (F4c).

Prosegue `Test_Session_Scenarios.py` (S1-S9), `Test_Session_Scenarios_S10_S18.py`, gli S19 e S20 con
la stessa disciplina: si verifica un comportamento QUALITATIVO o STRUTTURALE, mai un numero
calibrato.

Criterio "Fatto quando" della Fase 4 di `Analysis/Document/Piano_Implementazione_Missione.md`: *un
nuovo scenario con aerei parcheggiati mostra che sono colpibili*. Postura continua degli asset
senza missione (D1.c), decisioni dell'utente del 2026-10-11: un AEREO senza missione e' a terra,
bersaglio di SUPERFICIE passivo (colpibile da armi aria-suolo, mai ingaggiato come minaccia aerea,
non spara mai); le unita' terrestri senza missione sono in difesa con il tiro di prima (v.
`Logic/Mission_Adapter.continuous_posture`).

## S21: tabella a ruoli (`TestS21ParkedAircraftStrike`)

* Red-Airbase (Military 'Airbase', NESSUNA missione, composizione mista): 4 MiG-29S sul piazzale
  (quota 0, loadout 'CAP': R-27ER, R-73 e cannone, che userebbero se fossero in volo), un 9K35
  Strela-10 (SAM) e uno ZSU-23-4 Shilka (AAA) a difesa;
* Blue-Strike: 4 F-16C (loadout 'Strike'), ruolo 'strike', missione Strike che sorvola la base da
  ovest (quota 3000 m, da x = -60 km a x = +20 km);
* fire control a ruoli di riferimento (`Scenario_Fixtures.make_fire_control`): 'strike' contro
  'parked' = 'agm', come contro una struttura; 'sam'/'aaa' solo contro 'air'.
Due varianti per seed, stessa geometria: 'parked' (con i MiG-29S) e 'control' (la base senza
aerei: solo le difese).

Domande:
  * gli aerei parcheggiati sono colpiti e distrutti, solo dalle armi aria-suolo dello strike;
  * non sparano mai, non intercettano mai (nessun consumo di scorta);
  * le difese sparano solo agli aerei Blue in volo (il SAM non tratta i MiG come aerei);
  * la base non disingaggia per la perdita dei suoi aerei (non possono ritirarsi: l'erosione
    della dottrina conta solo le difese), resta HELD o DESTROYED;
  * senza aerei a terra (controllo) lo strike non ha bersagli che puo' ingaggiare: nessuna salva.

## S21R: fire control dai registri (`TestS21RParkedAircraftRegistry`)

Stessa base, divisa in due blocchi senza missioni: Red-Apron (4 MiG-29S, solo aerei a terra: un
blocco di soli bersagli passivi) e Red-AD (Strela-10 + Shilka). Blue-CAS: 2 A-10C 'Maverick/Gun
CAS' in missione CAS sullo stesso percorso, fire control dei registri
(`Logic/Fire_Control.make_registry_fire_control`, chiave di superficie 'Soft' per gli aerei a
terra). Domande: i MiG-29S sono colpiti con armi aria-suolo o cannone (mai l'AIM-9M), non sparano
mai, Red-Apron non disingaggia, le difese sparano solo agli A-10C.

Asserzioni robuste: invarianti per replica (nessun colpo dai parcheggiati, armi, bersagli delle
difese, esiti di forza) e, per la distruzione, una frazione aggregata sui seed con soglia
dichiarata (`MIN_DESTROYED_FRACTION`, v. sotto), mai un evento raro.
"""

import unittest

from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Weapon_Data import AIR_WEAPONS
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic.Fire_Control import make_registry_fire_control
from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F

BASE = 'Red-Airbase'
APRON = 'Red-Apron'
AIR_DEFENCE = 'Red-AD'
STRIKE = 'Blue-Strike'
CAS = 'Blue-CAS'
DURATION = 1_800.0
FLIGHT_ALTITUDE = 3_000.0
ROUTE = [(20_000.0, 0.0)]   # sorvolo della base (x = 0) fino a x = +20 km

# Soglia della frazione di aerei parcheggiati distrutti, aggregata sui seed. Valore DICHIARATO di
# test, non tarato. Misura del 2026-10-11: S21 21/32 (0,66; per seed 3, 2, 3, 3, 3, 3, 1, 3 su 4),
# S21R 23/24 (0,96). La soglia sta sotto il valore misurato di circa due deviazioni standard della
# frazione su 32 aerei (0,08), per non dipendere da un seed.
MIN_DESTROYED_FRACTION = 0.5


def _seeds(prefix: str, count: int):
    return [f'{prefix}-{index}' for index in range(count)]


def _parked_unit():
    return F.Unit('aircraft', 'MiG-29S', 4, origin=(0.0, 0.0, 0.0), step=(0.0, 150.0), prefix='mig', loadout='CAP')


def _defence_units():
    return [F.Unit('vehicle', '9K35-Strela-10', 1, origin=(500.0, -300.0), prefix='sam'),
            F.Unit('vehicle', 'ZSU-23-4-Shilka', 1, origin=(500.0, 900.0), prefix='aaa')]


def _parked_ids(forces):
    return {asset_id for force in forces for asset_id, asset in force.assets.items()
            if type(asset).__name__ == 'Aircraft' and force.side == 'Red'}


def _build(with_parked: bool):
    """S21 ricostruito da zero (gli asset vengono mutati da run_session)."""
    units = ([_parked_unit()] if with_parked else []) + _defence_units()
    base = F.build_force(BASE, 'Red', units, mil_category=F.AIR_UNIT)
    strike = F.build_force(STRIKE, 'Blue', [
        F.Unit('aircraft', 'F-16C Block 52d', 4, origin=(-60_000.0, 0.0, FLIGHT_ALTITUDE), step=(0.0, 500.0),
               prefix='str', loadout='Strike')], mil_category=F.AIR_UNIT)
    missions = F.missions_for(strike, ROUTE, mission_type='Strike', target=F.group_target(BASE))
    roles = {asset_id: 'strike' for asset_id in strike.assets}
    return F.Scenario(forces_a=[strike], forces_b=[base], missions=missions,
                      fire_control=F.make_fire_control(roles=roles), duration=DURATION, roles=roles)


def _build_registry():
    """S21R ricostruito da zero: base in due blocchi, A-10C, fire control dei registri."""
    apron = F.build_force(APRON, 'Red', [_parked_unit()], mil_category=F.AIR_UNIT)
    defence = F.build_force(AIR_DEFENCE, 'Red', _defence_units(), mil_category=F.AIR_UNIT)
    cas = F.build_force(CAS, 'Blue', [
        F.Unit('aircraft', 'A-10C Thunderbolt II', 2, origin=(-60_000.0, 0.0, FLIGHT_ALTITUDE), step=(0.0, 500.0),
               prefix='cas', loadout='Maverick/Gun CAS')], mil_category=F.AIR_UNIT)
    missions = F.missions_for(cas, ROUTE, mission_type='CAS', target=F.group_target(APRON))
    return F.Scenario(forces_a=[cas], forces_b=[apron, defence], missions=missions,
                      fire_control=make_registry_fire_control(), duration=DURATION)


def _destroyed(outcome, asset_ids):
    wanted = set(asset_ids)
    return {event.target_id for event in outcome.damage_events if event.destroyed and event.target_id in wanted}


class _ParkedChecks:
    """Mixin (NON un TestCase): verifiche comuni alle due classi. `runs` = [(scenario, outcome)]."""

    runs = ()

    def _parked(self, scenario):
        return _parked_ids(scenario.forces)

    def test_parked_aircraft_never_fire_nor_intercept(self):
        for scenario, outcome in self.runs:
            parked = self._parked(scenario)
            self.assertEqual([e for e in outcome.ammunition_events if e.asset_id in parked], [], outcome.session_id)
            self.assertEqual([e for e in outcome.interception_events if e.asset_id in parked], [],
                             outcome.session_id)
            self.assertEqual([e for e in outcome.damage_events if e.source_id in parked], [], outcome.session_id)

    def test_parked_aircraft_are_hit_and_destroyed(self):
        destroyed = total = 0

        for scenario, outcome in self.runs:
            parked = self._parked(scenario)
            destroyed += len(_destroyed(outcome, parked))
            total += len(parked)

        self.assertGreaterEqual(destroyed / total, MIN_DESTROYED_FRACTION)

    def test_air_defence_fires_only_at_airborne_attackers(self):
        for scenario, outcome in self.runs:
            red = {asset_id for force in scenario.forces_b for asset_id in force.assets}
            blue = {asset_id for force in scenario.forces_a for asset_id in force.assets}
            targets = {e.target_id for e in outcome.damage_events if e.source_id in red}
            self.assertLessEqual(targets, blue, outcome.session_id)


class TestS21ParkedAircraftStrike(_ParkedChecks, F.LoggerSilencer, unittest.TestCase):
    """S21: strike con la tabella a ruoli su una base con aerei parcheggiati (F4c)."""

    SEEDS = _seeds('S21', 8)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs, cls.control = [], []

        for session_id in cls.SEEDS:
            for with_parked, bucket in ((True, cls.runs), (False, cls.control)):
                scenario = _build(with_parked)
                bucket.append((scenario, scenario.run(session_id)))

    def test_parked_aircraft_are_hit_only_by_the_strike_air_to_ground_weapon(self):
        for scenario, outcome in self.runs:
            parked = self._parked(scenario)
            sources = {(e.source_id.split('/')[0], e.weapon) for e in outcome.damage_events if e.target_id in parked}
            self.assertTrue(sources, outcome.session_id)
            self.assertEqual(sources, {(STRIKE, F.SHOTS['agm'].weapon)}, outcome.session_id)

    def test_the_base_does_not_disengage_for_its_parked_aircraft(self):
        # Ogni episodio: dal G4b (uscita di scena, `Session_Simulator.G4_OFF_SCENE_EXIT`) lo strike disingaggiato
        # (partenza in volo, nessuna base Blue) puo' ripassare sulla base a ritroso, in un episodio successivo.
        for _, outcome in self.runs + self.control:
            for base in outcome.outcomes_of(BASE):
                self.assertIn(base.outcome, (ER.HELD, ER.DESTROYED), outcome.session_id)

    def test_without_parked_aircraft_the_strike_has_nothing_to_engage(self):
        """Controllo: la stessa missione contro la base senza aerei non spara; con gli aerei si'."""
        for (scenario, outcome), (control_scenario, control) in zip(self.runs, self.control):
            strikers = set(scenario.force(STRIKE).assets)
            self.assertTrue([e for e in outcome.ammunition_events if e.asset_id in strikers], outcome.session_id)
            self.assertEqual([e for e in control.ammunition_events if e.asset_id in strikers], [],
                             control.session_id)


class TestS21RParkedAircraftRegistry(_ParkedChecks, F.LoggerSilencer, unittest.TestCase):
    """S21R: CAS con la fire control dei registri su un piazzale di soli aerei (F4c)."""

    SEEDS = _seeds('S21R', 6)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = []

        for session_id in cls.SEEDS:
            scenario = _build_registry()
            cls.runs.append((scenario, scenario.run(session_id)))

    def test_parked_aircraft_are_never_hit_by_air_to_air_missiles(self):
        for scenario, outcome in self.runs:
            parked = self._parked(scenario)
            weapons = {e.weapon for e in outcome.damage_events if e.target_id in parked}
            self.assertTrue(weapons, outcome.session_id)
            self.assertFalse(weapons & set(AIR_WEAPONS['MISSILES_AAM']), outcome.session_id)

    def test_an_apron_of_parked_aircraft_never_disengages(self):
        for _, outcome in self.runs:
            apron = F.force_outcome(outcome, APRON)
            self.assertIsNotNone(apron, outcome.session_id)
            self.assertIn(apron.outcome, (ER.HELD, ER.DESTROYED), outcome.session_id)


if __name__ == '__main__':
    unittest.main()
