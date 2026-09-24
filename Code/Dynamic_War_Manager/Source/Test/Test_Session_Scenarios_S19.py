"""Scenario S19 del motore di sessioni virtuali: sessione con la fire control DEI REGISTRI (B2).

Prosegue `Test_Session_Scenarios.py` (S1-S9) e `Test_Session_Scenarios_S10_S18.py` con la
stessa disciplina: si verifica un comportamento QUALITATIVO o STRUTTURALE, mai un numero
calibrato. Differenza: al posto della tabella a ruoli di test (`make_fire_control`, che
resta invariata per gli altri scenari) qui `run_session` riceve
`Logic/Fire_Control.make_registry_fire_control()`, cioe' armi e Pk scelte dai registri
(Ground_Weapon_Data / loadout aerei) con le righe aeree B1 (STIME non tarate).

Composizione (scelta perche' il fuoco antiaereo sia davvero esercitato: una formazione che
attacca il suolo con armi intercettabili farebbe consumare ai SAM puri tutti i missili in
intercettazioni, e il fuoco AA non partirebbe mai — comportamento del motore, non della
fire control):
  * Blue-Transit, in transito a 3000 m verso est sopra la difesa rossa, senza armi
    aria-suolo: 2 A-10C senza loadout (attacker corazzato -> 'Aircraft_Attacker'),
    2 F-16C 'CAP' (solo aria-aria -> 'Aircraft'), 1 B-52H senza loadout ('Aircraft_Heavy');
  * Red-AD: 1 9K37-Buk (LORAD), 1 9K35-Strela-10 (SHORAD IR), 1 ZSU-23-4 Shilka (cannoni
    AZP-23, quota massima 1500 m nel registro) e 2 BMP-2 con sensore visivo dichiarato.

Domande:
  * la sessione e' riproducibile: stesso session_id (quindi stesso seed), scenario
    ricostruito identico -> esito identico evento per evento;
  * ogni colpo e' attribuito a un'arma reale del registro del tiratore;
  * sugli aerei arrivano solo armi con righe aeree; sui bersagli di superficie mai un SAM
    o un AAM;
  * il filtro di quota agisce dentro la sessione: il cannone AZP-23 dello Shilka (tetto
    1500 m) non colpisce mai aerei a 3000 m;
  * la sessione produce effettivamente fuoco (aggregato sui seed);
  * controllo di portata (ShotSpec.max_range, 2026-09-24): ogni salva che colpisce un aereo
    e' partita con il bersaglio entro la portata dell'arma. Effetto osservato
    sull'introduzione del controllo: prima il Buk lanciava sul primo aereo rilevato (a
    decine di km, spesso il B-52, il piu' visibile), ora aspetta l'ingresso nei 35 km del
    9M38 e ingaggia per primi i velivoli che vi entrano; le verifiche qualitative di S19
    non cambiano esito.
"""

import unittest

from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F
from Code.Dynamic_War_Manager.Source.Context import Doctrine
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Weapon_Data import AIR_WEAPONS
from Code.Dynamic_War_Manager.Source.Asset.Ground_Weapon_Data import GROUND_WEAPONS
from Code.Dynamic_War_Manager.Source.Context.Context import AIR_TARGET_CLASS_AIRCRAFT
from Code.Dynamic_War_Manager.Source.Logic import Contact_Scheduler as CS
from Code.Dynamic_War_Manager.Source.Logic import Fire_Control as FC

VISUAL = {'ground': F.DECLARED_GROUND_VISUAL_RANGE}
FLIGHT_ALTITUDE = 3_000.0
DURATION = 3_600.0

# Entrambi i lati ad oltranza (come BOTH_HOLD di S10-S18): senza, la difesa rossa si
# disingaggia alla prima perdita e il fuoco antiaereo non viene mai esercitato.
_HOLD = {Doctrine.DISENGAGEMENT_EROSION: 1.0, Doctrine.DISENGAGEMENT_SHOCK: 1.0}
BOTH_HOLD = {'Blue': dict(_HOLD), 'Red': dict(_HOLD)}


def _build():
    """Scenario S19 ricostruito da zero (gli asset vengono mutati da run_session)."""
    blue = F.build_force('Blue-Transit', 'Blue', [
        F.Unit('aircraft', 'A-10C Thunderbolt II', 2, origin=(-60_000.0, 0.0, FLIGHT_ALTITUDE), step=(0.0, 500.0),
               prefix='cas'),
        F.Unit('aircraft', 'F-16C Block 52d', 2, origin=(-61_000.0, 1_500.0, FLIGHT_ALTITUDE), step=(0.0, 500.0),
               prefix='ftr', loadout='CAP'),
        F.Unit('aircraft', 'B-52H Stratofortress', 1, origin=(-62_000.0, -1_500.0, FLIGHT_ALTITUDE), prefix='bmb')],
        mil_category=F.AIR_UNIT)
    red = F.build_force('Red-AD', 'Red', [
        F.Unit('vehicle', '9K37-Buk', 1, origin=(3_000.0, 500.0), prefix='lorad'),
        F.Unit('vehicle', '9K35-Strela-10', 1, origin=(500.0, -300.0), prefix='shorad'),
        F.Unit('vehicle', 'ZSU-23-4-Shilka', 1, origin=(500.0, 600.0), prefix='aaa'),
        F.Unit('vehicle', 'BMP-2', 2, origin=(0.0, 0.0), step=(0.0, 300.0), prefix='ifv', sensors=VISUAL)])
    routes = F.routes_for(blue, [(20_000.0, 0.0)])
    return blue, red, routes


def _run(session_id):
    blue, red, routes = _build()
    outcome = F.run(session_id, [blue], [red], FC.make_registry_fire_control(), duration=DURATION, routes=routes,
                    thresholds=BOTH_HOLD)
    return blue, red, outcome


def _signature(outcome):
    """Rappresentazione confrontabile degli eventi dell'esito (ordine incluso)."""
    return (tuple((e.time, e.target_id, e.source_id, e.weapon, e.outcome, e.health_after) for e in outcome.damage_events),
            tuple((e.asset_id, getattr(e, 'time', None)) for e in outcome.ammunition_events))


def _air_capable(weapon_model):
    """True se il modello d'arma ha una riga aerea nel proprio template."""
    for db in (GROUND_WEAPONS, AIR_WEAPONS):
        for weapons in db.values():
            if weapon_model in weapons:
                return AIR_TARGET_CLASS_AIRCRAFT in (weapons[weapon_model].get('efficiency') or {})
    return False


class TestS19RegistryFireControl(F.LoggerSilencer, unittest.TestCase):

    SEEDS = [f'S19-{index}' for index in range(3)]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = [_run(session_id) for session_id in cls.SEEDS]
        cls.replay = _run(cls.SEEDS[0])

    def test_same_seed_same_outcome(self):
        self.assertEqual(_signature(self.runs[0][2]), _signature(self.replay[2]))

    def test_air_defence_fires_at_aircraft(self):
        hits = sum(len(F.damage_on(outcome, blue.assets)) for blue, _, outcome in self.runs)
        self.assertGreater(hits, 0)

    def test_every_hit_uses_a_registry_weapon_of_the_shooter(self):
        for blue, red, outcome in self.runs:
            assets = {**blue.assets, **red.assets}
            for event in outcome.damage_events:
                shooter = assets[event.source_id]
                candidates = {w.model for w in FC._candidate_weapons(FC._shooter_key(shooter))}
                self.assertIn(event.weapon, candidates)

    def test_aircraft_only_hit_by_air_capable_weapons(self):
        for blue, _, outcome in self.runs:
            for event in F.damage_on(outcome, blue.assets):
                self.assertTrue(_air_capable(event.weapon), event.weapon)

    def test_surface_never_hit_by_sam_or_aam(self):
        for _, red, outcome in self.runs:
            for event in F.damage_on(outcome, red.assets):
                self.assertNotIn(event.weapon, AIR_WEAPONS['MISSILES_AAM'])
                weapon = GROUND_WEAPONS['MISSILES'].get(event.weapon, {})
                self.assertNotIn('min_altitude', weapon)

    def test_hits_on_aircraft_launched_within_weapon_range(self):
        """Distanza 3D tiratore-bersaglio al lancio (impatto - tempo di volo) <= max_range.

        Le posizioni sono ricostruite dalle stesse rotte dello scenario (geometria
        deterministica, ricostruita da `_build`); il tempo di volo e la portata vengono
        dalla ShotSpec della fire control dei registri, pura.
        """
        fire_control = FC.make_registry_fire_control()

        for blue, red, outcome in self.runs:
            _, _, routes = _build()
            checked = 0

            for event in F.damage_on(outcome, blue.assets):
                shooter, target = red.assets[event.source_id], blue.assets[event.target_id]
                spec = fire_control(shooter, target)
                t_launch = event.time - spec.time_of_flight
                p_target = CS.position_on_legs(CS.route_legs(routes[target.id], t0=0.0), t_launch)
                p_shooter = (float(shooter.position.x), float(shooter.position.y), float(shooter.position.z))
                distance = sum((a - b) ** 2 for a, b in zip(p_target, p_shooter)) ** 0.5
                self.assertLessEqual(distance, spec.max_range + 1.0, (event.source_id, event.weapon))
                checked += 1

            self.assertGreater(checked, 0)

    def test_altitude_filter_in_session(self):
        """AZP-23 (tetto 1500 m) non colpisce mai aerei a 3000 m."""
        self.assertGreater(FLIGHT_ALTITUDE, GROUND_WEAPONS['AA_CANNONS']['AZP-23-23mm']['max_altitude'])
        for blue, _, outcome in self.runs:
            weapons = {event.weapon for event in F.damage_on(outcome, blue.assets)}
            self.assertNotIn('AZP-23-23mm', weapons)


if __name__ == '__main__':
    unittest.main()
