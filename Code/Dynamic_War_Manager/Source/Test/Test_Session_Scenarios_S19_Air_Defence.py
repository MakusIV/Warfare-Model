"""S19 — allocazione della difesa aerea fra intercettazione e tiro sul lanciatore (A6).

Scenario persistente della riproduzione di `Analysis/Document/Proposta_Regole_Allocazione_SAM.md`
(§1.1 in origine, §7 per le regole approvate il 2026-09-28): una linea Red di 3 BMP-2 con una
difesa aerea a corto raggio, attaccata da A-10C che lanciano AGM-65D da ~16 km.

Regole verificate (esito QUALITATIVO, non numerico, come chiede il §6 della proposta):
  * **D** (fatta): intercetta solo un'arma che dichiara il task 'Anti_Missile'. Lo Strela-10
    (9M37) non intercetta i Maverick, quindi conserva i missili per gli aerei;
  * **L** (L1 implementata il 2026-09-28, passo 4; rivista il 2026-11-24, accesa il 2026-11-25): un colpo e'
    intercettabile salvo che il lanciatore sia un bersaglio immediato dell'intercettore, cioe' il lancio parte
    da DENTRO la zona di una sua arma intercettrice e il lanciatore e' rilevato all'istante del lancio e a portata
    di un'arma con scorta: in quel caso si spara a lui e i suoi colpi non si intercettano. Un lanciatore dentro la
    zona ma non ancora rilevato non e' un bersaglio: i suoi colpi si intercettano (v. TestS19AdL1ImmediateTarget).
    La regola del 2026-09-28 (interruttore L1_IMMEDIATE_TARGET_RULE spento) escludeva ogni lancio da dentro il V_I.
    Il Tor arretrato (lancio a ~15-19 km, fuori dai suoi 12 km) intercetta; col Tor avanzato e
    gli A-10C che attaccano solo i BMP-2, i lanci partono a ~9,5 km dal Tor (dentro): il Tor spara
    ai lanciatori e intercetta solo i colpi di quelli che non aveva ancora rilevato al lancio.

Misura del 2026-09-28 (passo 3): nel secondo caso il motore rispettava GIA' la regola per
tempistica, non per costruzione: il lanciatore entra nei 12 km prima che i suoi Maverick
arrivino, e il Tor spende gli 8 missili su di lui. Con la regola rivista l'unico seme in cui cambia l'esito
e' `S19-4` (`cas1` lancia prima di essere rilevato: il Tor intercetta 2 colpi); la verifica resta qui come
regressione. Il caso a geometria controllata (intercettore con scorta in avanzo e lancio da dentro la zona) e'
nei test unitari del risolutore: Test_Engagement_Resolver.TestL1ImmediateTarget (regola rivista) e
TestLauncherInsideInterceptionZone (regola del 2026-09-28).

Fire control: i registri veri (`Fire_Control.make_registry_fire_control`), senza filtri di test. Con il
criterio Pk/costo (A5) l'A-10C sceglierebbe la Mk-82AIR del loadout 'Maverick/Gun CAS', che non e'
intercettabile e renderebbe lo scenario vuoto: dalla F7a (regole d'ingaggio di missione, decisioni dell'utente
del 2026-10-18) lo scenario dichiara cio' che prima facevano due filtri di test:
  * missione CAS anticarro con Maverick: `MissionAsset.weapons=('AGM-65D',)` (arma designata: sul bersaglio
    designato solo quella), con bersaglio GROUP 'Red-Line' (tutto il blocco);
  * le varianti `_ifv_only` (gli aerei attaccano solo i BMP-2): bersaglio GROUP 'Red-Line' ristretto ai 3 BMP-2
    (`Target.asset_ids`) e ROE `only_designated`, al posto dello stand-in `ifv_only`.
La storia degli ingaggi e' identica a quella dei filtri (fotografia `Scenario_Baseline`, 24 esecuzioni).

Dottrina: entrambi i lati ad oltranza (`BOTH_HOLD`), per isolare l'allocazione della difesa
dal disingaggio alla prima perdita (difetto noto, §5.3 della proposta).
"""

import unittest
from unittest.mock import patch

from Code.Dynamic_War_Manager.Source.Command.Mission_Types import MissionRules, Target, TargetKind, TargetProvenance
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic.Fire_Control import make_registry_fire_control
from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F
from Code.Dynamic_War_Manager.Source.Test.Test_Session_Scenarios_S10_S18 import BOTH_HOLD


VISUAL = {'ground': F.DECLARED_GROUND_VISUAL_RANGE}
MAVERICK = 'AGM-65D'
DURATION = 1_800.0

# Rotte degli A-10C (quota 3000 m, partenza a x = -40 km): sorvolo della linea Red fino a
# x = +20 km, oppure standoff (virata a x = -11 km, mai sotto i 5 km dello Strela-10).
OVERFLIGHT = [(20_000.0, 0.0)]
STANDOFF = [(-11_000.0, 0.0), (-40_000.0, 0.0)]

# Posizioni del Tor rispetto alla linea (BMP-2 a x = 0).
TOR_FORWARD_X = -5_000.0   # con gli A-10C sui soli BMP-2 il lancio parte a ~9,5 km: DENTRO i 12 km
TOR_REAR_X = 3_000.0       # lancio a ~15-19 km dal Tor: FUORI
TOR_ZONE_M = 12_000.0      # portata del 9M331 nel registro (range['direct'])


def _seeds(prefix: str, count: int):
    return [f'{prefix}-{index}' for index in range(count)]


IFV_IDS = tuple(f'Red-Line/ifv{index}' for index in range(3))


def build(defence_model: str, defence_x: float, defence_y: float, attackers: int):
    red = F.build_force('Red-Line', 'Red', [
        F.Unit('vehicle', 'BMP-2', 3, origin=(0.0, 0.0), step=(0.0, 300.0), prefix='ifv', sensors=VISUAL),
        F.Unit('vehicle', defence_model, 1, origin=(defence_x, defence_y), prefix='ad')])
    cas = F.build_force('Blue-CAS', 'Blue', [
        F.Unit('aircraft', 'A-10C Thunderbolt II', attackers, origin=(-40_000.0, 0.0, 3_000.0),
               step=(0.0, 500.0), prefix='cas', loadout='Maverick/Gun CAS')], mil_category=F.AIR_UNIT)
    return red, cas


def run_variant(session_id: str, defence_model: str, defence_x: float, defence_y: float, attackers: int,
                points, targets_ifv_only: bool = False, runner=F.run):
    """Una sessione della variante; `runner` e' `F.run` (default) o `F.run_with_salvos` (esito + salve)."""
    red, cas = build(defence_model, defence_x, defence_y, attackers)
    fire_control = make_registry_fire_control()

    if targets_ifv_only:
        target = Target(kind=TargetKind.GROUP, target_id='Red-Line', asset_ids=IFV_IDS,
                        provenance=TargetProvenance.OBSERVED, observed_at=0.0)
        rules = MissionRules(roe='only_designated')
    else:
        target, rules = F.group_target('Red-Line'), None

    # Con la rotta di standoff (virata a x = -11 km e ritorno) la formazione TRASLATA di prima
    # non e' un offset nella terna di marcia: ogni A-10C ha una missione propria.
    missions = F.missions_for(cas, points, mission_type='CAS', target=target, weapons=(MAVERICK,), rules=rules)
    outcome = runner(session_id, [cas], [red], fire_control, duration=DURATION, missions=missions,
                     thresholds=BOTH_HOLD)
    return red, cas, outcome


def launch_distances(cas, outcome, defence_x: float, defence_y: float):
    """Distanza orizzontale [m] fra ogni lancio di Maverick e la difesa: sulla rotta rettilinea
    di sorvolo l'A-10C e' a x = x0 + v t (velocita' nominale del registro, y costante)."""
    distances = []

    for event in outcome.ammunition_events:
        if event.weapon != MAVERICK:
            continue

        aircraft = cas.assets[event.asset_id]
        x = float(aircraft.position.x) + aircraft.speed['nominal'] * event.time
        distances.append(((x - defence_x) ** 2 + (float(aircraft.position.y) - defence_y) ** 2) ** 0.5)

    return distances


def _interceptions(outcome, asset_id: str) -> int:
    return sum(e.interceptions for e in outcome.interception_events if e.asset_id == asset_id)


def _rounds_fired(outcome, asset_id: str) -> int:
    return sum(e.rounds for e in outcome.ammunition_events if e.asset_id == asset_id)


class TestS19AirDefenceAllocation(F.LoggerSilencer, unittest.TestCase):

    SEEDS = _seeds('S19', 6)
    AD = 'Red-Line/ad0'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Dal 2026-09-29 (dottrina di tiro, Proposta_Overkill_Tiro.md) gli A-10C non sprecano piu'
        # Maverick sui BMP gia' condannati e con la stessa dotazione distruggono anche lo Strela,
        # da fuori dei suoi 5 km, prima che spari: il caso d'origine (lo Strela conserva i
        # missili per gli aerei) richiede che gli aerei attacchino solo i BMP, come nella
        # variante con il Tor avanzato.
        cls.strela_overflight = [run_variant(s, '9K35-Strela-10', 1_000.0, -300.0, 4, OVERFLIGHT,
                                             targets_ifv_only=True)[::2]
                                 for s in cls.SEEDS]
        cls.strela_standoff = [run_variant(s, '9K35-Strela-10', 1_000.0, -300.0, 4, STANDOFF)[::2]
                               for s in cls.SEEDS]
        cls.tor_rear = [run_variant(s, '9K331-Tor', TOR_REAR_X, 300.0, 4, OVERFLIGHT) for s in cls.SEEDS]
        # Come per S16: si catturano i risultati del risolutore (salve, rilevamenti, intercettazioni) senza alterarli.
        cls.tor_forward = []
        cls.tor_forward_results = []
        original = ER.resolve_engagement

        for s in cls.SEEDS:
            captured = []

            def spy(*args, **kwargs):
                result = original(*args, **kwargs)

                if result is not None:
                    captured.append(result)

                return result

            with patch.object(ER, 'resolve_engagement', side_effect=spy):
                cls.tor_forward.append(run_variant(s, '9K331-Tor', TOR_FORWARD_X, 300.0, 4, OVERFLIGHT,
                                                   targets_ifv_only=True))

            cls.tor_forward_results.append(captured)

    def test_mavericks_are_launched(self):
        """Premessa non vacua: in ogni variante gli A-10C lanciano Maverick."""
        for label, runs in (('strela overflight', self.strela_overflight), ('strela standoff', self.strela_standoff),
                            ('tor rear', [(r, o) for r, _, o in self.tor_rear]), ('tor forward', [(r, o) for r, _, o in self.tor_forward])):
            with self.subTest(variant=label):
                launched = sum(e.rounds for _, o in runs for e in o.ammunition_events if e.weapon == MAVERICK)
                self.assertGreater(launched, 0)

    def test_strela_never_intercepts(self):
        """Regola D: il 9M37 non ha il task 'Anti_Missile'."""
        for label, runs in (('overflight', self.strela_overflight), ('standoff', self.strela_standoff)):
            with self.subTest(variant=label):
                self.assertEqual(sum(_interceptions(o, self.AD) for _, o in runs), 0)

    def test_strela_saves_its_missiles_for_the_aircraft(self):
        """Il caso d'origine della proposta: con il sorvolo lo Strela spara agli A-10C e ne
        abbatte, invece di aver speso tutto sui Maverick diretti ai BMP."""
        fired = sum(_rounds_fired(o, self.AD) for _, o in self.strela_overflight)
        blue_losses = sum(F.losses_of(o, 'Blue-CAS') for _, o in self.strela_overflight)
        self.assertGreater(fired, 0)
        self.assertGreater(blue_losses, 0)

    def test_strela_keeps_its_missiles_in_standoff(self):
        """In standoff gli A-10C non entrano mai nei 5 km: lo Strela non spara e non intercetta."""
        for red, outcome in self.strela_standoff:
            with self.subTest(session=outcome.session_id if hasattr(outcome, 'session_id') else None):
                self.assertEqual(_rounds_fired(outcome, self.AD), 0)
                strela = red.assets[self.AD]
                self.assertEqual(strela.stock_of('9M37-SAM'), strela.stores_from_registry()['9M37-SAM'])

    def test_standoff_missions_share_the_fire(self):
        """Dominio di coordinamento (decisione 6 dell'utente, 2026-10-11): i 4 A-10C sono 4 missioni
        dello STESSO blocco, quindi la saturazione e la ripartizione contano le salve di tutte. Come
        in F4a (forza = blocco): 8-10 Maverick e la linea Red distrutta con lo Strela. In F4b, senza dominio, se ne lanciavano 16 e lo Strela restava."""
        for red, outcome in self.strela_standoff:
            with self.subTest(session=outcome.session_id if hasattr(outcome, 'session_id') else None):
                launched = sum(e.rounds for e in outcome.ammunition_events if e.weapon == MAVERICK)
                self.assertGreaterEqual(launched, 8)
                self.assertLessEqual(launched, 10)
                self.assertEqual(F.force_outcome(outcome, 'Red-Line').outcome, 'destroyed')
                self.assertTrue(red.assets[self.AD].is_destroyed())

    def test_rear_tor_intercepts_standoff_launches(self):
        """Tor arretrato: i Maverick partono fuori dai suoi 12 km, sono bersagli legittimi (L1)."""
        self.assertGreater(sum(_interceptions(o, self.AD) for _, _, o in self.tor_rear), 0)

        for _, cas, outcome in self.tor_rear:
            self.assertTrue(all(d > TOR_ZONE_M for d in launch_distances(cas, outcome, TOR_REAR_X, 300.0)))
            for event in outcome.interception_events:
                with self.subTest(asset=event.asset_id):
                    self.assertEqual((event.asset_id, event.weapon), (self.AD, '9M331-SAM'))

    def test_forward_tor_engages_launchers_and_intercepts_only_unseen_ones(self):
        """Regola L (rivista il 2026-11-24): lanci da DENTRO i 12 km del Tor; il Tor spara ai lanciatori in ogni
        seme e intercetta solo colpi di lanciatori che non aveva rilevato al lancio (bersaglio immediato = rilevato
        e a portata)."""
        inside = 0

        for (red, cas, outcome), results in zip(self.tor_forward, self.tor_forward_results):
            distances = launch_distances(cas, outcome, TOR_FORWARD_X, 300.0)
            inside += sum(1 for d in distances if d < TOR_ZONE_M)

            with self.subTest(session=outcome.session_id if hasattr(outcome, 'session_id') else None):
                self.assertGreater(_rounds_fired(outcome, self.AD), 0)

                for result in results:
                    salvo_of = {s.salvo_id: s for s in result.salvos}

                    for event in result.interception_events:
                        if event.asset_id != self.AD:
                            continue

                        # almeno una salva fermata ha un lanciatore NON rilevato dal Tor fino al lancio
                        unseen = [salvo_id for salvo_id in event.salvo_ids
                                  if not any(d.observer_id == self.AD and d.detected
                                             and d.target_id == salvo_of[salvo_id].shooter_id
                                             and d.time <= salvo_of[salvo_id].t_launch + 1e-9
                                             for d in result.detections)]
                        self.assertTrue(unseen, event)

        self.assertGreater(inside, 0)      # premessa: almeno un lancio da dentro la zona


class TestS19MissionRulesReplaceTheTestFilters(F.LoggerSilencer, unittest.TestCase):
    """F7a: le regole d'ingaggio di missione fanno cio' che facevano i filtri di test."""

    AD = 'Red-Line/ad0'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # (sessione, difesa, x, y, rotta, solo BMP-2): una per tipo di variante. NON in `Scenario_Baseline`
        # (i metodi di test non sono eseguiti dalla fotografia).
        cls.runs = {
            'ifv_only': run_variant('S19-rules', '9K35-Strela-10', 1_000.0, -300.0, 4, OVERFLIGHT,
                                    targets_ifv_only=True, runner=F.run_with_salvos),
            'whole_line': run_variant('S19-rules', '9K35-Strela-10', 1_000.0, -300.0, 4, STANDOFF,
                                      runner=F.run_with_salvos),
        }

    def test_aircraft_launch_only_the_designated_weapon(self):
        """Premessa non vacua (salve degli A-10C) e nessuna arma diversa dal Maverick, in entrambe le varianti."""
        for label, (_, cas, (_, salvos)) in self.runs.items():
            with self.subTest(variant=label):
                fired = [salvo for salvo in salvos if salvo.shooter_id in cas.assets]
                self.assertTrue(fired)
                self.assertEqual({salvo.spec.weapon for salvo in fired}, {MAVERICK})

    def test_ifv_only_variant_never_fires_at_the_air_defence(self):
        """`only_designated` su 3 BMP-2: nessuna salva degli A-10C sulla difesa aerea, e sui BMP si'."""
        _, cas, (_, salvos) = self.runs['ifv_only']
        targets = {salvo.target_id for salvo in salvos if salvo.shooter_id in cas.assets}
        self.assertNotIn(self.AD, targets)
        self.assertTrue(targets & set(IFV_IDS))

    def test_whole_line_variant_may_target_the_air_defence(self):
        """Controprova: con tutta la linea designata (ROE di default) la difesa aerea e' ingaggiabile."""
        _, cas, (_, salvos) = self.runs['whole_line']
        self.assertIn(self.AD, {salvo.target_id for salvo in salvos if salvo.shooter_id in cas.assets})


class TestS19AdTargetRule(F.LoggerSilencer, unittest.TestCase):
    """BI (blocco 2, Proposta_Bersagli_Intercettabili_Difesa_Aerea.md): con la fire control dei registri e
    `BI_AD_TARGET_RULE` acceso il Tor non ferma piu' i Maverick (classe 'tactical', `ad_detectable` False: non sono
    bersagli di una difesa terrestre); spento li ferma come prima. Variante del Tor arretrato di S19AD, stessa sessione
    della fotografia (`S19-0`); NON in `Scenario_Baseline` (i metodi di test non sono eseguiti dalla fotografia)."""

    AD = 'Red-Line/ad0'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.off = run_variant('S19-0', '9K331-Tor', TOR_REAR_X, 300.0, 4, OVERFLIGHT)
        with patch.object(ER, 'BI_AD_TARGET_RULE', True):
            cls.on = run_variant('S19-0', '9K331-Tor', TOR_REAR_X, 300.0, 4, OVERFLIGHT)

    def test_switch_off_the_tor_intercepts_mavericks(self):
        self.assertGreater(_interceptions(self.off[2], self.AD), 0)

    def test_switch_on_the_tor_never_intercepts_mavericks(self):
        _, cas, outcome = self.on
        self.assertGreater(sum(e.rounds for e in outcome.ammunition_events if e.weapon == MAVERICK), 0)  # premessa
        self.assertEqual(_interceptions(outcome, self.AD), 0)
        self.assertEqual(outcome.interception_events, ())


class TestS19AdL1ImmediateTarget(F.LoggerSilencer, unittest.TestCase):
    """L1 rivista (Proposta_Revisione_L1_Lanciatore_Bersaglio.md) sul Tor avanzato, seme `S19-4`: l'unico caso della
    fotografia in cui la regola cambia l'esito. L'A-10C `cas1` lancia AGM-65D a ~9,7 e ~9,5 km dal Tor (dentro i 12 km
    del 9M331) a ~163 e ~164 s, PRIMA che il Tor lo rilevi (~184 s): misure della sonda della Proposta. Spento (regola
    del 2026-09-28): il Tor non ferma quei colpi. Acceso: il lanciatore non e' un bersaglio immediato del Tor, che li
    intercetta. Stessa sessione della fotografia; NON in `Scenario_Baseline` (i metodi di test non sono eseguiti dalla
    fotografia)."""

    AD = 'Red-Line/ad0'
    LAUNCHER = 'Blue-CAS/cas1'
    SEED = 'S19-4'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.off = cls._run(False)
        cls.on = cls._run(True)

    @classmethod
    def _run(cls, switch):
        """`(outcome, [EngagementResult, ...])` del Tor avanzato con l'interruttore `switch`."""
        results = []
        original = ER.resolve_engagement

        def spy(*args, **kwargs):
            result = original(*args, **kwargs)

            if result is not None:
                results.append(result)

            return result

        with patch.object(ER, 'L1_IMMEDIATE_TARGET_RULE', switch), \
                patch.object(ER, 'resolve_engagement', side_effect=spy):
            _, _, outcome = run_variant(cls.SEED, '9K331-Tor', TOR_FORWARD_X, 300.0, 4, OVERFLIGHT,
                                        targets_ifv_only=True)

        return outcome, results

    def test_premise_the_launcher_fires_before_the_tor_sees_it(self):
        for label, (_, results) in (('off', self.off), ('on', self.on)):
            with self.subTest(switch=label):
                launches = [s.t_launch for r in results for s in r.salvos
                            if s.shooter_id == self.LAUNCHER and s.spec.weapon == MAVERICK]
                seen = [d.time for r in results for d in r.detections
                        if d.observer_id == self.AD and d.target_id == self.LAUNCHER and d.detected]
                self.assertTrue(launches)
                self.assertTrue(not seen or min(seen) > min(launches))

    def test_switch_off_the_tor_does_not_intercept(self):
        self.assertEqual(_interceptions(self.off[0], self.AD), 0)

    def test_switch_on_the_tor_intercepts_the_unseen_launcher(self):
        outcome, results = self.on
        self.assertGreater(_interceptions(outcome, self.AD), 0)

        for result in results:
            shooter_of = {s.salvo_id: s.shooter_id for s in result.salvos}

            for event in result.interception_events:
                if event.asset_id == self.AD:
                    with self.subTest(time=event.time):
                        self.assertTrue(any(shooter_of.get(salvo_id) == self.LAUNCHER for salvo_id in event.salvo_ids))

    def test_switch_on_the_tor_still_fires_at_the_launchers(self):
        self.assertGreater(_rounds_fired(self.on[0], self.AD), 0)


if __name__ == '__main__':
    unittest.main()
