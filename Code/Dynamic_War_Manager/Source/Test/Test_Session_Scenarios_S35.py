"""Scenario S35 del motore di sessioni virtuali: quali colpi una difesa aerea puo' considerare bersagli (BI).

Riproduzione di `Analysis/Document/Proposta_Bersagli_Intercettabili_Difesa_Aerea.md` (blocco 3, decisioni BI-1..BI-12
del 2026-11-07 e P-1..P-7 del 2026-11-08). Con l'interruttore `Engagement_Resolver.BI_AD_TARGET_RULE` acceso un
intercettore ferma un colpo solo se il suo dominio ('land' | 'naval') e' fra gli `intercept_domains` della ShotSpec
(dichiarati dalla fire control dei registri); spento, nessun filtro, come prima. Esito QUALITATIVO (relazioni fra
varianti), mai un numero calibrato.

## S35-ADTGT (`TestS35AirDefenceTargets`)

Quattro geometrie, ciascuna con l'interruttore spento (`_off`) e acceso (`_on`), 4 seed (nomi stabili nella fotografia,
nell'ordine; stesso `session_id` per le 8 varianti di un seed). Fire control dei registri, `BOTH_HOLD`, 1800 s.

  * `land_tactical`: 4 A-10C con AGM-65D contro 3 BMP-2 e un Tor arretrato (V_I 12 km), la variante `tor_rear` di
    S19AD. Acceso: il Tor non ferma piu' i Maverick (classe 'tactical').
  * `land_cruise`: 2 Su-34 'Anti-Ship' con Kh-59 designato (missione Strike) contro un deposito `Oil_Tank` e un Buk a
    1 km (V_I 35 km). Il cruise resta bersaglio delle difese terrestri: acceso = spento.
  * `naval`: 2 F/A-18C 'Anti-Ship' con AGM-84A (missione Anti_Ship) contro una FF 1135M Rezky (V_I 12 km, AK-630 con
    task 'Anti_Missile'). L'antinave resta bersaglio delle difese navali: acceso = spento.
  * `naval_maverick`: 2 A-10C con AGM-65D designato (missione CAS, sensore `sea` dichiarato di test) contro la stessa
    Rezky. Acceso: la nave non ferma piu' i Maverick (`ad_detectable` fisso False).

La Rezky e non l'Arleigh Burke (decisione P-1 del 2026-11-08): con il V_I di 240 km del Burke la regola L1 vieta ogni
intercettazione dei lanci da aereo. Il sensore `sea` di 20 km dell'A-10C e' un VALORE DI TEST [S] (P-2), non un dato:
senza, l'A-10C non rileva la nave e non lancia.
"""

import unittest
from unittest.mock import patch

from Code.Dynamic_War_Manager.Source.Command.Mission_Types import MissionRules, Target, TargetKind, TargetProvenance
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic.Fire_Control import make_registry_fire_control
from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F
from Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S10_S18 import BOTH_HOLD
from Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S19_Air_Defence import (
    DURATION, MAVERICK, OVERFLIGHT, TOR_REAR_X, run_variant as s19_run_variant)

SEEDS_PER_SCENARIO = 4
SEEDS = [f'S35-ADTGT-{index}' for index in range(SEEDS_PER_SCENARIO)]
# variante -> (geometria, interruttore BI_AD_TARGET_RULE); l'ordine e' quello dei nomi nella riga di Scenario_Baseline.
VARIANT_SPEC = {
    'land_tactical_off': ('land_tactical', False),
    'land_tactical_on': ('land_tactical', True),
    'land_cruise_off': ('land_cruise', False),
    'land_cruise_on': ('land_cruise', True),
    'naval_off': ('naval', False),
    'naval_on': ('naval', True),
    'naval_maverick_off': ('naval_maverick', False),
    'naval_maverick_on': ('naval_maverick', True),
}
VARIANTS = tuple(VARIANT_SPEC)

KH59 = 'Kh-59'
HARPOON = 'AGM-84A'
TOR = 'Red-Line/ad0'            # Tor di S19AD (`build`, prefisso 'ad')
DEPOT_TANK = 'Red-Depot/tank0'
BUK = 'Red-Depot/sam0'
SHIP_MODEL = 'FF 1135M Rezky'   # V_I 12 km (SA-N-4), intercettore AK-630 (task 'Anti_Missile')
SHIP = 'Red-Navy/ff0'
SHIP_X = 60_000.0

# Sensore marittimo DICHIARATO DI TEST dell'A-10C [m]: VALORE DI TEST [S], non un dato del registro (che non ne ha);
# serve solo a far rilevare la nave entro la portata del Maverick (15 km). Non entra in nessuna asserzione.
DECLARED_SEA_RANGE_M = 20_000.0

# land_cruise: 2 Su-34 a 6000 m da x = -150 km, virata a x = -60 km e ritorno (lancio dei Kh-59 a ~90 km dal Buk,
# fuori dai suoi 35 km).
CRUISE_ORIGIN = (-150_000.0, 0.0, 6_000.0)
CRUISE_POINTS = [(-60_000.0, 0.0), (-150_000.0, 0.0)]
# naval / naval_maverick: partenza a x = -40 km, 3000 m, sorvolo della nave fino a x = +80 km.
NAVAL_ORIGIN = (-40_000.0, 0.0, 3_000.0)
NAVAL_POINTS = [(SHIP_X + 20_000.0, 0.0)]


def build_land_cruise(session_id: str):
    """`land_cruise`: Su-34 con Kh-59 contro un deposito difeso da un Buk della stessa forza.

    Bersaglio ristretto al deposito (`Target.asset_ids`) con ROE `only_designated`: i Su-34 non attaccano il Buk.
    Restituisce `(deposito, attaccanti, outcome)`.
    """
    depot = F.make_force('Red-Depot', 'Red')
    F.add_assets(depot, [
        F.make_structure(depot, DEPOT_TANK, (0.0, 0.0), category='Farp', asset_type='Oil_Tank'),
        F.make_vehicle(depot, BUK, '9K37-Buk', (1_000.0, 0.0))])
    strike = F.build_force('Blue-STR', 'Blue', [
        F.Unit('aircraft', 'Su-34', 2, origin=CRUISE_ORIGIN, step=(0.0, 500.0), prefix='str',
               loadout='Anti-Ship')], mil_category=F.AIR_UNIT)
    target = Target(kind=TargetKind.GROUP, target_id='Red-Depot', asset_ids=(DEPOT_TANK,),
                    provenance=TargetProvenance.OBSERVED, observed_at=0.0)
    missions = F.missions_for(strike, CRUISE_POINTS, mission_type='Strike', target=target, weapons=(KH59,),
                              rules=MissionRules(roe='only_designated'))
    outcome = F.run(session_id, [strike], [depot], make_registry_fire_control(), duration=DURATION,
                    missions=missions, thresholds=BOTH_HOLD)
    return depot, strike, outcome


def build_naval(session_id: str, weapon: str):
    """`naval` (`weapon` = AGM-84A: 2 F/A-18C, missione Anti_Ship) o `naval_maverick` (`weapon` = AGM-65D: 2 A-10C
    con sensore `sea` dichiarato di test, missione CAS, arma designata) contro la Rezky. Restituisce
    `(nave, attaccanti, outcome)`."""
    navy = F.build_force('Red-Navy', 'Red', [
        F.Unit('ship', SHIP_MODEL, 1, origin=(SHIP_X, 0.0), prefix='ff')], mil_category=F.NAVAL_UNIT)

    if weapon == HARPOON:
        attackers = F.build_force('Blue-AS', 'Blue', [
            F.Unit('aircraft', 'F/A-18C Hornet', 2, origin=NAVAL_ORIGIN, step=(0.0, 500.0), prefix='as',
                   loadout='Anti-Ship')], mil_category=F.AIR_UNIT)
        missions = F.missions_for(attackers, NAVAL_POINTS, mission_type='Anti_Ship',
                                  target=F.group_target('Red-Navy'))
    else:
        attackers = F.build_force('Blue-CAS', 'Blue', [
            F.Unit('aircraft', 'A-10C Thunderbolt II', 2, origin=NAVAL_ORIGIN, step=(0.0, 500.0), prefix='cas',
                   loadout='Maverick/Gun CAS', sensors={'sea': DECLARED_SEA_RANGE_M})], mil_category=F.AIR_UNIT)
        missions = F.missions_for(attackers, NAVAL_POINTS, mission_type='CAS', target=F.group_target('Red-Navy'),
                                  weapons=(MAVERICK,))

    outcome = F.run(session_id, [attackers], [navy], make_registry_fire_control(), duration=DURATION,
                    missions=missions, thresholds=BOTH_HOLD)
    return navy, attackers, outcome


def run_variant(session_id: str, variant: str):
    """Una sessione della variante: `(blocco difeso, attaccanti, outcome)`. L'interruttore e' sostituito attorno
    all'intera esecuzione (il run lo copia alla costruzione, `_EngagementRun.__init__`)."""
    geometry, switch = VARIANT_SPEC[variant]

    with patch.object(ER, 'BI_AD_TARGET_RULE', switch):
        if geometry == 'land_tactical':
            return s19_run_variant(session_id, '9K331-Tor', TOR_REAR_X, 300.0, 4, OVERFLIGHT)

        if geometry == 'land_cruise':
            return build_land_cruise(session_id)

        return build_naval(session_id, HARPOON if geometry == 'naval' else MAVERICK)


def _interceptions(outcome, asset_id: str) -> int:
    return sum(e.interceptions for e in outcome.interception_events if e.asset_id == asset_id)


def _launched(outcome, weapon: str) -> int:
    return sum(e.rounds for e in outcome.ammunition_events if e.weapon == weapon)


def _events(outcome):
    """Munizioni, danni e intercettazioni con i loro istanti: la storia confrontata fra varianti e repliche."""
    return ([(e.time, e.asset_id, e.weapon, e.rounds) for e in outcome.ammunition_events],
            [(e.time, e.target_id, e.source_id, e.weapon, e.outcome, e.health_after) for e in outcome.damage_events],
            [(e.time, e.asset_id, e.interceptions, e.force_id, e.weapon) for e in outcome.interception_events])


class TestS35AirDefenceTargets(F.LoggerSilencer, unittest.TestCase):
    """S35-ADTGT: con la regola BI accesa una difesa ferma solo i colpi del proprio dominio."""

    SEEDS = SEEDS
    VARIANTS = VARIANTS

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {variant: [] for variant in cls.VARIANTS}

        # Ciclo esterno sui seed, interno sulle varianti: stesso `session_id` per le 8 varianti di un seed
        # (la fotografia numera le esecuzioni per occorrenza del session_id nell'unita'). Nessun'altra sessione qui.
        for session_id in cls.SEEDS:
            for variant in cls.VARIANTS:
                cls.runs[variant].append(run_variant(session_id, variant))

    def _outcomes(self, variant: str):
        return [outcome for _, _, outcome in self.runs[variant]]

    # ── premesse non vacue (P-4 (b)) ──

    def test_premise_mavericks_are_launched(self):
        """Premessa: gli AGM-65D sono lanciati in ogni variante che li usa (totale sui seed)."""
        for variant in ('land_tactical_off', 'land_tactical_on', 'naval_maverick_off', 'naval_maverick_on'):
            with self.subTest(variant=variant):
                self.assertGreater(sum(_launched(o, MAVERICK) for o in self._outcomes(variant)), 0)

    def test_premise_kh59_are_launched(self):
        """Premessa: i Kh-59 sono lanciati in `land_cruise_off/_on` (totale sui seed)."""
        for variant in ('land_cruise_off', 'land_cruise_on'):
            with self.subTest(variant=variant):
                self.assertGreater(sum(_launched(o, KH59) for o in self._outcomes(variant)), 0)

    def test_premise_harpoons_are_launched(self):
        """Premessa: gli AGM-84A sono lanciati in `naval_off/_on` (totale sui seed)."""
        for variant in ('naval_off', 'naval_on'):
            with self.subTest(variant=variant):
                self.assertGreater(sum(_launched(o, HARPOON) for o in self._outcomes(variant)), 0)

    # ── asserzioni 1-12 ──

    def test_land_tactical_on_the_tor_never_intercepts(self):
        """1. Acceso: il Tor (difesa terrestre) non ferma gli AGM-65D (classe 'tactical'), in ogni seed."""
        for seed, outcome in zip(self.SEEDS, self._outcomes('land_tactical_on')):
            with self.subTest(session=seed):
                self.assertEqual(_interceptions(outcome, TOR), 0)

    def test_land_tactical_on_launches_fewer_mavericks(self):
        """2. Acceso si lanciano MENO AGM-65D che spento, per seed (nessuno e' piu' fermato: ne servono meno)."""
        for seed, off, on in zip(self.SEEDS, self._outcomes('land_tactical_off'), self._outcomes('land_tactical_on')):
            with self.subTest(session=seed):
                self.assertLess(_launched(on, MAVERICK), _launched(off, MAVERICK))

    def test_land_tactical_off_the_tor_intercepts(self):
        """3. Spento: il Tor ferma AGM-65D (comportamento precedente, come S19AD `tor_rear`), in ogni seed."""
        for seed, outcome in zip(self.SEEDS, self._outcomes('land_tactical_off')):
            with self.subTest(session=seed):
                self.assertGreater(_interceptions(outcome, TOR), 0)

    def test_land_cruise_on_the_buk_intercepts_the_kh59(self):
        """4. Acceso: il Buk ferma i Kh-59 (classe 'cruise', bersaglio di ogni difesa), in ogni seed."""
        for seed, outcome in zip(self.SEEDS, self._outcomes('land_cruise_on')):
            with self.subTest(session=seed):
                self.assertGreater(_interceptions(outcome, BUK), 0)

    def test_land_cruise_switch_changes_nothing(self):
        """5. Il cruise e' ammesso in entrambi gli stati: stessa storia (munizioni, danni, intercettazioni),
        per seed."""
        for seed, off, on in zip(self.SEEDS, self._outcomes('land_cruise_off'), self._outcomes('land_cruise_on')):
            with self.subTest(session=seed):
                self.assertEqual(_events(on), _events(off))

    def test_naval_on_the_ship_intercepts_the_harpoons(self):
        """6. Acceso: la Rezky ferma gli AGM-84A (classe 'anti_ship', bersaglio navale), in ogni seed."""
        for seed, outcome in zip(self.SEEDS, self._outcomes('naval_on')):
            with self.subTest(session=seed):
                self.assertGreater(_interceptions(outcome, SHIP), 0)

    def test_naval_switch_changes_nothing(self):
        """7. L'antinave e' ammesso in entrambi gli stati: stessa storia, per seed."""
        for seed, off, on in zip(self.SEEDS, self._outcomes('naval_off'), self._outcomes('naval_on')):
            with self.subTest(session=seed):
                self.assertEqual(_events(on), _events(off))

    def test_naval_maverick_on_the_ship_never_intercepts(self):
        """8. Acceso: la nave non ferma gli AGM-65D (Maverick fisso `ad_detectable` False, BI-6), in ogni seed."""
        for seed, outcome in zip(self.SEEDS, self._outcomes('naval_maverick_on')):
            with self.subTest(session=seed):
                self.assertEqual(_interceptions(outcome, SHIP), 0)

    def test_naval_maverick_on_hits_reach_the_ship(self):
        """9. Acceso: almeno un AGM-65D arriva al danno sulla nave (totale sui seed)."""
        hits = sum(1 for outcome in self._outcomes('naval_maverick_on') for e in outcome.damage_events
                   if e.target_id == SHIP and e.weapon == MAVERICK)
        self.assertGreater(hits, 0)

    def test_naval_maverick_off_the_ship_intercepts(self):
        """10. Spento: la nave ferma AGM-65D (comportamento precedente: e' la differenza che la variante mostra),
        totale sui seed."""
        self.assertGreater(sum(_interceptions(o, SHIP) for o in self._outcomes('naval_maverick_off')), 0)

    def test_on_variants_with_excluded_shots_have_no_interception_event(self):
        """11. Nelle varianti accese in cui tutte le salve offensive hanno domini vuoti nessun InterceptionEvent
        (come TestS19AdTargetRule), per seed."""
        for variant in ('land_tactical_on', 'naval_maverick_on'):
            for seed, outcome in zip(self.SEEDS, self._outcomes(variant)):
                with self.subTest(variant=variant, session=seed):
                    self.assertEqual(outcome.interception_events, ())

    def test_runs_are_deterministic(self):
        """12. Determinismo: ogni variante di ogni seed, rieseguita, ripete la stessa storia. In un metodo di test,
        non in `setUpClass`: la fotografia esegue solo `setUpClass` e non deve vedere le repliche."""
        for index, seed in enumerate(self.SEEDS):
            for variant in self.VARIANTS:
                with self.subTest(variant=variant, session=seed):
                    _, _, replica = run_variant(seed, variant)
                    self.assertEqual(_events(replica), _events(self.runs[variant][index][2]))


if __name__ == '__main__':
    unittest.main()
