"""Scenario S28 del motore di sessioni virtuali: regole d'ingaggio di missione (F7a).

Prosegue `Test_Session_Scenarios.py` (S1-S9), gli S10-S27 con la stessa disciplina: si verifica un comportamento
QUALITATIVO o STRUTTURALE, mai un numero calibrato. Nel codice (decisioni dell'utente del 2026-10-18,
`Analysis/Document/Proposta_F7_Bersagli_Filtro_Armi.md`): la missione decide CHI si ingaggia (bersaglio designato e
ROE, strato T nel risolutore, `Engagement_Resolver.TargetRules`) e CON CHE ARMA (armi designate, strato T; politica
d'armi per tipo di missione, strato W, involucro della fire control `Fire_Control.restrict_by_policy`). Fire control
dei registri veri (`make_registry_fire_control`) e dottrina ad oltranza (`BOTH_HOLD`, per isolare le regole dal
disingaggio alla prima perdita) ovunque; 4 seed per variante. Le premesse sono verificate con la variante
"spenta" o "libera" dello stesso scenario, cosi' ogni asserzione negativa non e' vacua.

## S28-ROE (`TestS28RulesOfEngagement`)

Blue-Flight: 2 F-16C Block 52d 'Strike' (Mk-83, Mk-82, AIM-9M) a 3000 m da (-40 km, 0) all'ATTACK (14 km, 0) e
ritorno a (-40 km, 0) lungo la stessa rotta (waypoint ATTACK = indice 1). Red-Column (3 BMP-2) in (0, 0), sulla
rotta all'andata e al ritorno, e Red-Depot (3 BMP-2) in (12 km, 0), poco prima del punto ATTACK; sensore visivo
dichiarato dei BMP-2 (come S19). Bersaglio della missione: GROUP 'Red-Depot'. Varianti (nomi stabili nella fotografia,
nell'ordine):
  * 'free': ROE di default (`weapon_free`): la colonna e' un'opportunita' e viene bombardata gia' all'andata
    (premessa);
  * 'priority': `priority_designated` con arma designata Mk-82 (correzione dell'utente del 2026-10-18): all'andata
    il volo SORVOLA la colonna senza sparare (nessun tiro sulle opportunita' di superficie in avvicinamento) e
    bombarda il deposito con la sola Mk-82; passato il punto ATTACK (sui tratti reali) e al ritorno bombarda la
    colonna con le armi residue (Mk-83: la Mk-82, riservata, resta esclusa);
  * 'only': `only_designated`: nessuna salva sulla colonna ne' all'andata ne' al ritorno, almeno una sul deposito;
  * 'hold': `weapon_hold`: nessuna salva offensiva;
  * 'rules_off': come 'only' con `F7_TARGET_RULES` spento: identica a 'free', evento per evento.

## S28-CLASS (`TestS28WeaponPolicyByMissionType`)

Politica d'armi per tipo di missione (`Context.MISSION_WEAPON_POLICY`), con la variante `*_off` = `F7_WEAPON_POLICY`
spento (il comportamento di prima):
  * 'cap_low' / 'cap_low_off': 2 F-15C 'Eagle Sweep' in CAP a 300 m sopra 3 BMP-2. Con la politica il CAP non
    mitraglia il suolo; senza, il cannone di bordo spara ai BMP-2 (premessa);
  * 'sead' / 'sead_off': 2 F-16C 'SEAD' (AGM-88) a 500 m contro Red-AD (2 BMP-2 e uno Strela-10). Con la politica
    solo l'AGM-88 e solo sul SAM; senza, il cannone spara anche ai BMP-2 (premessa). Lo Strela-10 e non un SAM a
    radar come il Tor: il Tor abbatte la formazione prima che il cannone possa sparare (premessa non ottenibile);
  * 'self_defence' / 'self_defence_off': un F-16C 'Strike' e un A-10C 'Maverick/Gun CAS' (entrambi con
    `self_escort_capability` True: l'A-10C ha l'AIM-9M, dato corretto con la decisione 8 della F7) incrociano 2 MiG-29S
    'CAP'. Con la politica entrambi si difendono con l'AIM-9M (autodifesa aria-aria dei tipi aria-suolo); senza, anche
    l'A-10C spara ai MiG (premessa). Il caso negativo (loadout senza capacita' di autodifesa = nessuna opzione
    aria-aria) e' provato con un loadout di test nei test unitari (Test_Fire_Control, Test_Mission_Adapter). Sensore
    'air' dell'A-10C e dei MiG DICHIARATO di test (valori sotto): col sensore del registro i MiG sparerebbero per
    primi da 30 km e abbatterebbero i Blu prima della portata dell'AIM-9M.

## S28-ZONE (`TestS28ZoneDesignation`)

Designazione geometrica: 1 F-15C 'Eagle Sweep' in CAP con bersaglio ZONE di raggio 20 km in (0, 0), su una rotta a
y = 8 km; Red-In (un MiG-29S) parte dentro la zona e la attraversa a y = -5 km, Red-Out (un MiG-29S) passa a y =
24 km, sempre fuori zona ma a portata dell'AIM-9M (16 km dalla rotta). 'zone_free': salve su entrambi (premessa);
'zone_only' (`only_designated`): nessuna salva su Red-Out, almeno una su Red-In. Limite verificato: la designazione e'
valutata alla PRIMA decisione del tiratore sulla coppia, quindi Red-In deve essere in zona gia' alla partenza (un
bersaglio che entra in zona dopo la prima valutazione e' scartato per quella finestra: v. docstring di
`Engagement_Resolver`, "Regole di bersaglio di missione (F7a)").
"""

import unittest
from unittest.mock import patch

from Code.Dynamic_War_Manager.Source.Command.Mission_Types import MissionRules
from Code.Dynamic_War_Manager.Source.Logic import Session_Simulator as SS
from Code.Dynamic_War_Manager.Source.Logic.Fire_Control import make_registry_fire_control
from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F
from Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S10_S18 import BOTH_HOLD

SEEDS_PER_SCENARIO = 4
VISUAL = {'ground': F.DECLARED_GROUND_VISUAL_RANGE}
# Sensori 'air' DICHIARATI di test [m] (valori di test, non dati): v. docstring.
MIG_AIR_SENSOR = 8_000.0
CAS_AIR_SENSOR = 30_000.0


def _seeds(prefix: str, count: int = SEEDS_PER_SCENARIO):
    return [f'{prefix}-{index}' for index in range(count)]


def _blue_salvos(salvos, prefix: str):
    """Le salve di `salvo.shooter_id` che comincia per `prefix` (il lato Blu, o un blocco)."""
    return [salvo for salvo in salvos if salvo.shooter_id.startswith(prefix)]


def _on(salvos, target_prefix: str, weapon=None):
    return [salvo for salvo in salvos if salvo.target_id.startswith(target_prefix)
            and (weapon is None or salvo.spec.weapon == weapon)]


def _run(session_id, blue, red, missions, duration, switches=(True, True)):
    """`(outcome, salve)` con gli interruttori `(F7_WEAPON_POLICY, F7_TARGET_RULES)`."""
    weapon_policy, target_rules = switches

    with patch.object(SS, 'F7_WEAPON_POLICY', weapon_policy), patch.object(SS, 'F7_TARGET_RULES', target_rules):
        return F.run_with_salvos(session_id, blue, red, make_registry_fire_control(), duration=duration,
                                 missions=missions, thresholds=BOTH_HOLD)


# ── S28-ROE ────────────────────────────────────────────────────────────────────

ROE_DURATION = 3_600.0
ROE_START = (-40_000.0, 0.0)
ROE_ATTACK_POINT = (14_000.0, 0.0)
# Variante -> (ROE, armi designate, (F7_WEAPON_POLICY, F7_TARGET_RULES)). Ordine stabile nella fotografia.
ROE_VARIANTS = {
    'free': (None, (), (True, True)),
    'priority': ('priority_designated', ('Mk-82',), (True, True)),
    'only': ('only_designated', (), (True, True)),
    'hold': ('weapon_hold', (), (True, True)),
    'rules_off': ('only_designated', (), (True, False)),
}


def _roe_run(session_id: str, variant: str):
    roe, weapons, switches = ROE_VARIANTS[variant]
    flight = F.build_force('Blue-Flight', 'Blue', [
        F.Unit('aircraft', 'F-16C Block 52d', 2, origin=(-40_000.0, 0.0, 3_000.0), step=(0.0, 500.0), prefix='f',
               loadout='Strike')], mil_category=F.AIR_UNIT)
    column = F.build_force('Red-Column', 'Red', [
        F.Unit('vehicle', 'BMP-2', 3, origin=(0.0, 0.0), step=(0.0, 300.0), prefix='ifv', sensors=VISUAL)])
    depot = F.build_force('Red-Depot', 'Red', [
        F.Unit('vehicle', 'BMP-2', 3, origin=(12_000.0, 0.0), step=(0.0, 300.0), prefix='ifv', sensors=VISUAL)])
    rules = MissionRules(roe=roe) if roe else None
    missions = F.missions_for(flight, [ROE_ATTACK_POINT, ROE_START], mission_type='Strike',
                              target=F.group_target('Red-Depot'), weapons=weapons, rules=rules, attack_waypoint=1)
    outcome, salvos = _run(session_id, [flight], [column, depot], missions, ROE_DURATION, switches)
    return outcome, salvos


class TestS28RulesOfEngagement(F.LoggerSilencer, unittest.TestCase):
    """S28-ROE: il bersaglio designato e la ROE decidono contro chi si spara; le armi designate con che arma."""

    SEEDS = _seeds('S28-ROE')
    VARIANTS = tuple(ROE_VARIANTS)
    PASS_TIME = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                cls.runs[variant].append(_roe_run(session_id, variant))

        # Istante di arrivo sul punto ATTACK: velocita' di crociera nominale dell'F-16C (la rotta e' rettilinea e
        # le missioni volano alla velocita' del mezzo piu' lento, regola A).
        flight = F.build_force('Blue-Flight', 'Blue', [
            F.Unit('aircraft', 'F-16C Block 52d', 1, origin=(-40_000.0, 0.0, 3_000.0), prefix='f',
                   loadout='Strike')], mil_category=F.AIR_UNIT)
        speed = F.routes_for(flight, [ROE_ATTACK_POINT])['Blue-Flight/f0'].edges
        cls.PASS_TIME = (ROE_ATTACK_POINT[0] - ROE_START[0]) / float(next(iter(speed.values())).speed)

    def test_free_bombs_the_column_as_an_opportunity(self):
        """Premessa non vacua: senza regole la colonna (non designata) e' bombardata."""
        for outcome, salvos in self.runs['free']:
            with self.subTest(session=outcome.session_id):
                self.assertTrue(_on(_blue_salvos(salvos, 'Blue-Flight'), 'Red-Column'))
                self.assertTrue(_on(_blue_salvos(salvos, 'Blue-Flight'), 'Red-Depot'))

    def test_only_designated_never_fires_at_the_column(self):
        for outcome, salvos in self.runs['only']:
            with self.subTest(session=outcome.session_id):
                blue = _blue_salvos(salvos, 'Blue-Flight')
                self.assertEqual(_on(blue, 'Red-Column'), [])
                self.assertTrue(_on(blue, 'Red-Depot'))

    def test_free_bombs_the_column_while_approaching_premise(self):
        for outcome, salvos in self.runs['free']:
            with self.subTest(session=outcome.session_id):
                column = _on(_blue_salvos(salvos, 'Blue-Flight'), 'Red-Column')
                self.assertTrue(any(salvo.t_launch < self.PASS_TIME for salvo in column))

    def test_priority_overflies_the_column_on_the_way_in_and_bombs_it_on_the_way_out(self):
        for outcome, salvos in self.runs['priority']:
            with self.subTest(session=outcome.session_id):
                blue = _blue_salvos(salvos, 'Blue-Flight')
                column = _on(blue, 'Red-Column')
                # andata: sorvolo senza tiro (nessuna arma consumata sulla colonna prima del punto ATTACK)
                self.assertTrue(all(salvo.t_launch >= self.PASS_TIME for salvo in column))
                # il deposito, designato, e' bombardato all'andata con la sola arma designata
                depot = _on(blue, 'Red-Depot')
                self.assertTrue(depot)
                self.assertEqual({salvo.spec.weapon for salvo in depot}, {'Mk-82'})
                self.assertTrue(all(salvo.t_launch < self.PASS_TIME for salvo in depot))
                # ritorno: la colonna e' bombardata con le armi residue, la Mk-82 riservata resta esclusa
                self.assertTrue(column)
                self.assertEqual(_on(blue, 'Red-Column', 'Mk-82'), [])

    def test_weapon_hold_fires_nothing(self):
        for outcome, salvos in self.runs['hold']:
            with self.subTest(session=outcome.session_id):
                self.assertEqual(_blue_salvos(salvos, 'Blue-Flight'), [])
                self.assertEqual([e for e in outcome.ammunition_events if e.asset_id.startswith('Blue-Flight')], [])

    def test_switch_off_is_the_free_session_event_by_event(self):
        for (free, _), (off, _) in zip(self.runs['free'], self.runs['rules_off']):
            with self.subTest(session=free.session_id):
                self.assertEqual(off.ammunition_events, free.ammunition_events)
                self.assertEqual(off.damage_events, free.damage_events)
                self.assertEqual(off.interception_events, free.interception_events)
                self.assertEqual(off.fuel_events, free.fuel_events)


# ── S28-CLASS ──────────────────────────────────────────────────────────────────

CLASS_DURATION = 1_800.0
CLASS_VARIANTS = ('cap_low', 'cap_low_off', 'sead', 'sead_off', 'self_defence', 'self_defence_off')


def _class_run(session_id: str, variant: str):
    policy = not variant.endswith('_off')
    kind = variant[:-4] if variant.endswith('_off') else variant

    if kind == 'cap_low':
        cap = F.build_force('Blue-CAP', 'Blue', [
            F.Unit('aircraft', 'F-15C Eagle', 2, origin=(-20_000.0, 0.0, 300.0), step=(0.0, 400.0), prefix='f',
                   loadout='Eagle Sweep')], mil_category=F.AIR_UNIT)
        red = F.build_force('Red-Line', 'Red', [
            F.Unit('vehicle', 'BMP-2', 3, origin=(0.0, 0.0), step=(0.0, 300.0), prefix='ifv', sensors=VISUAL)])
        missions = F.missions_for(cap, [(20_000.0, 0.0)], mission_type='CAP', target=F.zone_target((0.0, 0.0), 10_000.0))
        blue, reds = [cap], [red]
    elif kind == 'sead':
        flight = F.build_force('Blue-SEAD', 'Blue', [
            F.Unit('aircraft', 'F-16C Block 52d', 2, origin=(-40_000.0, 0.0, 500.0), step=(0.0, 500.0), prefix='f',
                   loadout='SEAD')], mil_category=F.AIR_UNIT)
        red = F.build_force('Red-AD', 'Red', [
            F.Unit('vehicle', 'BMP-2', 2, origin=(0.0, 0.0), step=(0.0, 300.0), prefix='ifv', sensors=VISUAL),
            F.Unit('vehicle', '9K35-Strela-10', 1, origin=(500.0, 600.0), prefix='sam')])
        missions = F.missions_for(flight, [(30_000.0, 0.0)], mission_type='SEAD', target=F.group_target('Red-AD'))
        blue, reds = [flight], [red]
    else:
        strike = F.build_force('Blue-Strike', 'Blue', [
            F.Unit('aircraft', 'F-16C Block 52d', 1, origin=(-40_000.0, 0.0, 5_000.0), prefix='f',
                   loadout='Strike')], mil_category=F.AIR_UNIT)
        cas = F.build_force('Blue-CAS', 'Blue', [
            F.Unit('aircraft', 'A-10C Thunderbolt II', 1, origin=(-40_000.0, 3_000.0, 5_000.0), prefix='a',
                   loadout='Maverick/Gun CAS', sensors={'air': CAS_AIR_SENSOR})], mil_category=F.AIR_UNIT)
        migs = F.build_force('Red-CAP', 'Red', [
            F.Unit('aircraft', 'MiG-29S', 2, origin=(40_000.0, 500.0, 5_000.0), step=(0.0, 1_500.0), prefix='m',
                   loadout='CAP', sensors={'air': MIG_AIR_SENSOR})], mil_category=F.AIR_UNIT)
        missions = F.missions_for(strike, [(40_000.0, 0.0)], mission_type='Strike',
                                  target=F.zone_target((40_000.0, 0.0), 5_000.0))
        missions += F.missions_for(cas, [(40_000.0, 3_000.0)], mission_type='CAS',
                                   target=F.zone_target((40_000.0, 3_000.0), 5_000.0))
        missions += F.missions_for(migs, [(-40_000.0, 500.0)], mission_type='CAP',
                                   target=F.zone_target((-40_000.0, 500.0), 5_000.0))
        blue, reds = [strike, cas], [migs]

    return _run(session_id, blue, reds, missions, CLASS_DURATION, (policy, True))


class TestS28WeaponPolicyByMissionType(F.LoggerSilencer, unittest.TestCase):
    """S28-CLASS: la politica d'armi del tipo di missione toglie le opzioni che il tipo non ammette contro la
    classe del bersaglio; la variante `*_off` (`F7_WEAPON_POLICY` spento) e' il comportamento di prima."""

    SEEDS = _seeds('S28-CLASS')
    VARIANTS = CLASS_VARIANTS

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                cls.runs[variant].append(_class_run(session_id, variant))

    def test_cap_off_strafes_the_ground_premise(self):
        for outcome, salvos in self.runs['cap_low_off']:
            with self.subTest(session=outcome.session_id):
                self.assertTrue(_on(_blue_salvos(salvos, 'Blue-CAP'), 'Red-Line', 'M61A1'))

    def test_cap_does_not_fire_at_the_ground(self):
        for outcome, salvos in self.runs['cap_low']:
            with self.subTest(session=outcome.session_id):
                self.assertEqual(_blue_salvos(salvos, 'Blue-CAP'), [])

    def test_sead_off_fires_at_the_ifvs_premise(self):
        for outcome, salvos in self.runs['sead_off']:
            with self.subTest(session=outcome.session_id):
                self.assertTrue(_on(_blue_salvos(salvos, 'Blue-SEAD'), 'Red-AD/ifv'))

    def test_sead_fires_only_at_the_air_defence_and_only_sead_weapons(self):
        for outcome, salvos in self.runs['sead']:
            with self.subTest(session=outcome.session_id):
                blue = _blue_salvos(salvos, 'Blue-SEAD')
                self.assertEqual(_on(blue, 'Red-AD/ifv'), [])
                self.assertTrue(_on(blue, 'Red-AD/sam'))
                self.assertEqual({salvo.spec.weapon for salvo in blue}, {'AGM-88'})

    def test_self_defence_off_the_cas_aircraft_fires_at_the_migs_premise(self):
        fired = sum(len(_on(_blue_salvos(salvos, 'Blue-CAS'), 'Red-CAP')) for _, salvos in self.runs['self_defence_off'])
        self.assertGreater(fired, 0)

    def test_self_defence_both_aircraft_defend_themselves_with_the_aam(self):
        """Caso positivo: F-16C e A-10C (autodifesa dichiarata nel loadout) sparano l'AIM-9M ai MiG."""
        runs = self.runs['self_defence']

        for prefix in ('Blue-Strike', 'Blue-CAS'):
            with self.subTest(aircraft=prefix):
                aam = sum(len(_on(_blue_salvos(salvos, prefix), 'Red-CAP', 'AIM-9M')) for _, salvos in runs)
                self.assertGreater(aam, 0)

        for outcome, salvos in runs:
            with self.subTest(session=outcome.session_id):
                self.assertTrue(all(salvo.target_id.startswith('Red-CAP')
                                    for salvo in _blue_salvos(salvos, 'Blue-')))


# ── S28-ZONE ───────────────────────────────────────────────────────────────────

ZONE_DURATION = 1_800.0
ZONE_VARIANTS = ('zone_only', 'zone_free')


def _zone_run(session_id: str, variant: str):
    cap = F.build_force('Blue-CAP', 'Blue', [
        F.Unit('aircraft', 'F-15C Eagle', 1, origin=(-40_000.0, 8_000.0, 5_000.0), prefix='f',
               loadout='Eagle Sweep')], mil_category=F.AIR_UNIT)
    inside = F.build_force('Red-In', 'Red', [
        F.Unit('aircraft', 'MiG-29S', 1, origin=(15_000.0, -5_000.0, 5_000.0), prefix='m', loadout='CAP',
               sensors={'air': MIG_AIR_SENSOR})], mil_category=F.AIR_UNIT)
    outside = F.build_force('Red-Out', 'Red', [
        F.Unit('aircraft', 'MiG-29S', 1, origin=(30_000.0, 24_000.0, 5_000.0), prefix='m', loadout='CAP',
               sensors={'air': MIG_AIR_SENSOR})], mil_category=F.AIR_UNIT)
    rules = MissionRules(roe='only_designated') if variant == 'zone_only' else None
    missions = F.missions_for(cap, [(40_000.0, 8_000.0)], mission_type='CAP',
                              target=F.zone_target((0.0, 0.0), 20_000.0), rules=rules)
    missions += F.missions_for(inside, [(-40_000.0, -5_000.0)], mission_type='CAP',
                               target=F.zone_target((-40_000.0, -5_000.0), 5_000.0))
    missions += F.missions_for(outside, [(-40_000.0, 24_000.0)], mission_type='CAP',
                               target=F.zone_target((-40_000.0, 24_000.0), 5_000.0))
    return _run(session_id, [cap], [inside, outside], missions, ZONE_DURATION)


class TestS28ZoneDesignation(F.LoggerSilencer, unittest.TestCase):
    """S28-ZONE: bersaglio ZONE = designazione geometrica; con `only_designated` si spara solo a chi e' in zona."""

    SEEDS = _seeds('S28-ZONE')
    VARIANTS = ZONE_VARIANTS

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                cls.runs[variant].append(_zone_run(session_id, variant))

    def test_free_fires_at_both_premise(self):
        for outcome, salvos in self.runs['zone_free']:
            with self.subTest(session=outcome.session_id):
                blue = _blue_salvos(salvos, 'Blue-CAP')
                self.assertTrue(_on(blue, 'Red-In'))
                self.assertTrue(_on(blue, 'Red-Out'))

    def test_only_designated_fires_only_at_the_aircraft_in_the_zone(self):
        for outcome, salvos in self.runs['zone_only']:
            with self.subTest(session=outcome.session_id):
                blue = _blue_salvos(salvos, 'Blue-CAP')
                self.assertEqual(_on(blue, 'Red-Out'), [])
                self.assertTrue(_on(blue, 'Red-In'))


if __name__ == '__main__':
    unittest.main()
