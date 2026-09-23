"""FASE 7 del motore di sessioni virtuali — scenari di plausibilita' S1-S9.

Batteria concordata con l'utente (wiki `decisions/soglie-disingaggio-e-attrito-aggregato`,
P3): S1-S5 dai documenti Lanchester, S6-S9 definiti per il progetto. Regola di P3, valida
per ogni scenario: **si prende la composizione delle forze e la domanda che pone, MAI
coefficienti o esiti numerici precalcolati**. Ogni test verifica quindi un comportamento
QUALITATIVO del motore — un evento accade o non accade, un ordine temporale e' rispettato,
un lato perde piu' dell'altro, un campo dell'esito ha la forma attesa — mai un numero.

## Robustezza statistica
Dove la risposta dipende dall'RNG, lo scenario e' ripetuto su piu' `session_id` (quindi
piu' seed, v. `Utility/Session_Rng`) e il confronto e' fatto sugli AGGREGATI delle
repliche, dichiarandolo nel test. Le repliche sono eseguite una sola volta per classe
(`setUpClass`) e condivise fra i metodi di verifica. Tutto e' deterministico: stessi
`session_id`, stessi esiti a ogni esecuzione della suite — un test "fortunato" oggi lo
e' sempre, quindi le soglie qualitative sono state scelte con margine rispetto a quanto
osservato, e le asserzioni confrontano varianti dello stesso scenario (con/senza SEAD,
con/senza SAM, ...) sugli stessi seed.

## Costanti di scenario
Composizioni, geometrie e ShotSpec sono dichiarate nei test o in `Scenario_Fixtures`
(v. la' "fire_control di riferimento" e "Sensori dichiarati"); nessuna viene da una
fonte esterna. Le posizioni sono in metri su un piano locale, i tempi in secondi.

## Dottrina "ad oltranza"
Con la dottrina di default (erosione 0.30, shock 0.20) una formazione di 4 aerei rompe il
contatto alla prima perdita (shock 1/4 = 0.25). Dove la domanda dello scenario richiede
che una forza PROSEGUA sotto il fuoco (S5 multistrato, S6), la si dichiara con una
tabella dottrinale esplicita (`PRESS_ON`: soglie 1.0 = "combattere fino
all'annientamento", ammesso da `Doctrine.validate_disengagement_thresholds` come scelta
dottrinale esplicita) passata a `run_session(thresholds=...)`, non con un ritocco del
motore.
"""

import unittest
from collections import Counter
from unittest.mock import patch

from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Block.Military import Military
from Code.Dynamic_War_Manager.Source.Command.Session_Types import SessionOutcome
from Code.Dynamic_War_Manager.Source.Context import Doctrine
from Code.Dynamic_War_Manager.Source.Logic import Contact_Scheduler as CS
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER

VISUAL = {'ground': F.DECLARED_GROUND_VISUAL_RANGE}

# Dottrina "ad oltranza" per il lato Blue, default per Red (v. docstring del modulo).
PRESS_ON = {
    'Blue': {Doctrine.DISENGAGEMENT_EROSION: 1.0, Doctrine.DISENGAGEMENT_SHOCK: 1.0},
    'Red': dict(Doctrine.DEFAULT_DISENGAGEMENT_THRESHOLDS['Red']),
}


def _seeds(prefix: str, count: int):
    return [f'{prefix}-{index}' for index in range(count)]


def _type_of(forces):
    """`{asset_id: nome della classe}` per le forze date."""
    return {asset_id: type(asset).__name__ for force in forces for asset_id, asset in force.assets.items()}


# ── S1 — COMBINED ARMS CON CAS ────────────────────────────────────────────────

class TestS1CombinedArmsWithCAS(F.LoggerSilencer, unittest.TestCase):
    """S1: A (corazzati + meccanizzati, con CAS) attacca B (meccanizzata + artiglieria +
    AAA/VSHORAD) in difesa.

    Composizione: `Scenario_Fixtures.combined_arms_scenario` — Blue-Armor 3 M1A2 + 2 M2
    Bradley in movimento, Blue-CAS 2 A-10C (ruolo strike); Red-Line 3 BMP-2, 1 2S19-Msta,
    1 ZSU-23-4, 1 9K35 Strela-10, fermi.

    Domanda: l'ingaggio si risolve con perdite su entrambi i lati e l'esito riflette la
    superiorita' di chi la possiede. La superiorita' di A e' data dal CAS: si confronta lo
    stesso scontro CON e SENZA CAS sugli stessi seed. Senza CAS la difesa (che vede prima
    con l'osservazione d'artiglieria e combatte da ferma) deve prevalere; con il CAS deve
    prevalere l'attaccante. Aggregati su 8 repliche.
    """

    SEEDS = _seeds('S1', 8)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.with_cas, cls.without_cas = [], []

        for session_id in cls.SEEDS:
            scenario = F.combined_arms_scenario(with_cas=True)
            cls.with_cas.append((scenario, scenario.run(session_id)))
            scenario = F.combined_arms_scenario(with_cas=False)
            cls.without_cas.append((scenario, scenario.run(session_id)))

    @staticmethod
    def _loss_fractions(runs, force_id):
        lost = committed = 0

        for _, outcome in runs:
            found = F.force_outcome(outcome, force_id)
            lost += found.lost
            committed += found.committed

        return lost / committed

    def test_every_replica_is_one_joint_engagement(self):
        for scenario, outcome in self.with_cas:
            ids = [tuple(o.force_id for o in e) for e in outcome.engagement_outcomes]
            self.assertEqual(ids, [('Blue-Armor', 'Blue-CAS', 'Red-Line')])

    def test_both_sides_take_damage(self):
        """In aggregato entrambi i lati subiscono DamageEvent (non e' un tiro al bersaglio)."""
        for label, runs in (('with CAS', self.with_cas), ('without CAS', self.without_cas)):
            blue = sum(len(F.damage_on(o, [a for f in s.forces_a for a in f.assets])) for s, o in runs)
            red = sum(len(F.damage_on(o, [a for f in s.forces_b for a in f.assets])) for s, o in runs)

            with self.subTest(variant=label):
                self.assertGreater(blue, 0)
                self.assertGreater(red, 0)

    def test_with_cas_the_attacker_prevails(self):
        self.assertGreater(self._loss_fractions(self.with_cas, 'Red-Line'),
                           self._loss_fractions(self.with_cas, 'Blue-Armor'))

    def test_without_cas_the_defence_prevails(self):
        self.assertGreater(self._loss_fractions(self.without_cas, 'Blue-Armor'),
                           self._loss_fractions(self.without_cas, 'Red-Line'))

    def test_cas_shifts_the_outcome_toward_the_attacker(self):
        self.assertGreater(self._loss_fractions(self.with_cas, 'Red-Line'),
                           self._loss_fractions(self.without_cas, 'Red-Line'))
        self.assertLess(self._loss_fractions(self.with_cas, 'Blue-Armor'),
                        self._loss_fractions(self.without_cas, 'Blue-Armor'))

    def test_outcome_labels_are_the_declared_ones(self):
        for _, outcome in self.with_cas + self.without_cas:
            for force in outcome.force_outcomes:
                self.assertIn(force.outcome, ER.FORCE_OUTCOMES)


# ── S2 — SEAD PRELIMINARE ─────────────────────────────────────────────────────

class TestS2PreliminarySEAD(F.LoggerSilencer, unittest.TestCase):
    """S2: una missione SEAD contro il sito SAM PRIMA dell'attacco principale.

    Composizione: Red-SAM 2 9K37 Buk; Red-Target 4 BMP-2 a 3 km dal sito; Blue-Strike
    4 F-16C (loadout 'Strike', ruolo strike: attacca solo il bersaglio, non il SAM);
    Blue-SEAD 4 F-16C (loadout 'SEAD', ruolo sead: solo contro SAM/AAA).

    Due varianti sugli stessi seed:
      * senza SEAD: una sessione, lo strike attraversa la bolla del SAM intatto;
      * con SEAD: sessione 1 SEAD contro il sito, sessione 2 lo strike contro il sito come
        la sessione 1 lo ha lasciato (lo stato passa attraverso gli asset MUTATI da
        run_session: e' anche la verifica che due sessioni si concatenano).

    Domanda: con SEAD riuscito, l'attacco principale subisce meno perdite/danni che senza.
    Aggregati su 8 repliche.
    """

    SEEDS = _seeds('S2', 8)

    @staticmethod
    def _sam_site():
        return F.build_force('Red-SAM', 'Red', [F.Unit('vehicle', '9K37-Buk', 2, origin=(0.0, 0.0),
                                                      step=(0.0, 400.0), prefix='sam')])

    @staticmethod
    def _target():
        return F.build_force('Red-Target', 'Red', [F.Unit('vehicle', 'BMP-2', 4, origin=(3_000.0, 0.0),
                                                         step=(0.0, 300.0), prefix='tgt')])

    @staticmethod
    def _package(force_id, y, loadout, prefix):
        return F.build_force(force_id, 'Blue', [F.Unit('aircraft', 'F-16C Block 52d', 4,
                                                       origin=(-150_000.0, y), step=(0.0, 500.0),
                                                       prefix=prefix, loadout=loadout)],
                             mil_category=F.AIR_UNIT)

    @classmethod
    def _strike(cls, session_id, strike, sam, target):
        fire = F.make_fire_control(roles={asset_id: 'strike' for asset_id in strike.assets})
        return F.run(session_id, [strike], [sam, target], fire, duration=3_600.0,
                     routes=F.routes_for(strike, [(20_000.0, 0.0)]))

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.baseline, cls.sead_runs, cls.after_sead = [], [], []

        for session_id in cls.SEEDS:
            strike = cls._package('Blue-Strike', 0.0, 'Strike', 'str')
            cls.baseline.append((strike, cls._strike(session_id, strike, cls._sam_site(), cls._target())))

            sam, target = cls._sam_site(), cls._target()
            sead = cls._package('Blue-SEAD', 5_000.0, 'SEAD', 'sead')
            fire = F.make_fire_control(roles={asset_id: 'sead' for asset_id in sead.assets})
            cls.sead_runs.append((sam, F.run(f'{session_id}-sead', [sead], [sam], fire, duration=3_600.0,
                                             routes=F.routes_for(sead, [(-20_000.0, 5_000.0)]))))

            strike = cls._package('Blue-Strike', 0.0, 'Strike', 'str')
            cls.after_sead.append((strike, cls._strike(session_id, strike, sam, target)))

    def test_sam_is_a_real_threat_without_sead(self):
        """Premessa non vacua: senza SEAD il sito SAM infligge perdite allo strike."""
        self.assertGreater(sum(F.losses_of(o, 'Blue-Strike') for _, o in self.baseline), 0)

    def test_sead_degrades_the_site(self):
        self.assertGreater(sum(F.losses_of(o, 'Red-SAM') for _, o in self.sead_runs), 0)

    def test_damage_carries_over_to_the_next_session(self):
        """Il sito della sessione 2 e' quello lasciato dalla sessione 1 (asset mutati)."""
        for sam, outcome in self.sead_runs:
            final = {}
            for event in outcome.damage_events:
                final[event.target_id] = event.health_after
            for asset_id, asset in sam.assets.items():
                self.assertEqual(asset.health, final.get(asset_id, 100))

    def test_strike_after_sead_suffers_less(self):
        losses_without = sum(F.losses_of(o, 'Blue-Strike') for _, o in self.baseline)
        losses_with = sum(F.losses_of(o, 'Blue-Strike') for _, o in self.after_sead)
        damage_without = sum(len(F.damage_on(o, F.asset_ids(s))) for s, o in self.baseline)
        damage_with = sum(len(F.damage_on(o, F.asset_ids(s))) for s, o in self.after_sead)
        self.assertLess(losses_with, losses_without)
        self.assertLess(damage_with, damage_without)

    def test_strike_still_hits_its_target_after_sead(self):
        self.assertGreater(sum(F.losses_of(o, 'Red-Target') for _, o in self.after_sead), 0)


# ── S3 — ASIMMETRIA AEREA: STEALTH CONTRO MASSA ───────────────────────────────

class TestS3StealthVersusMass(F.LoggerSilencer, unittest.TestCase):
    """S3: pochi caccia "stealth" contro molti caccia convenzionali.

    Composizione: Blue 4 F-15C contro Red 8 F-15C (STESSO modello, loadout 'Eagle Sweep',
    rotte frontali): l'unica differenza fra le due varianti e' la bassa osservabilita' di
    Blue, resa con `detection_factor` = STEALTH_FACTOR quando il BERSAGLIO e' un aereo Blue
    (il fattore degrada la Pd di chi osserva un bersaglio stealth; e' il punto di aggancio
    gia' presente in resolve_engagement). Nessun modello "stealth" nei registri: usare lo
    stesso modello isola il meccanismo dal resto.

    Domanda: il rapporto di scambio riflette il vantaggio di rilevamento, non solo il
    numero. Senza stealth, 4 contro 8 perde lo scambio; con stealth lo vince, pur essendo
    la meta'. Aggregati su 10 repliche.
    """

    SEEDS = _seeds('S3', 10)
    STEALTH_FACTOR = 0.15   # costante di scenario dichiarata, non calibrata

    @staticmethod
    def _build():
        blue = F.build_force('Blue-Stealth', 'Blue', [F.Unit('aircraft', 'F-15C Eagle', 4, origin=(-100_000.0, 0.0),
                                                             step=(0.0, 1_000.0), prefix='f', loadout='Eagle Sweep')],
                             mil_category=F.AIR_UNIT)
        red = F.build_force('Red-Mass', 'Red', [F.Unit('aircraft', 'F-15C Eagle', 8, origin=(100_000.0, 0.0),
                                                       step=(0.0, 1_000.0), prefix='f', loadout='Eagle Sweep')],
                            mil_category=F.AIR_UNIT)
        routes = F.routes_for(blue, [(100_000.0, 0.0)])
        routes.update(F.routes_for(red, [(-100_000.0, 0.0)]))
        return blue, red, routes

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.control, cls.stealth = [], []

        for session_id in cls.SEEDS:
            for bucket, stealthy in ((cls.control, False), (cls.stealth, True)):
                blue, red, routes = cls._build()
                blue_ids = set(blue.assets)
                factor = (lambda observer, target: cls.STEALTH_FACTOR if target.id in blue_ids else 1.0) \
                    if stealthy else None
                bucket.append(F.run(session_id, [blue], [red], F.make_fire_control(), duration=3_600.0,
                                    routes=routes, detection_factor=factor))

    @staticmethod
    def _totals(outcomes):
        return (sum(F.losses_of(o, 'Blue-Stealth') for o in outcomes),
                sum(F.losses_of(o, 'Red-Mass') for o in outcomes))

    def test_without_stealth_numbers_win(self):
        blue_lost, red_lost = self._totals(self.control)
        self.assertGreater(blue_lost, red_lost)

    def test_with_stealth_detection_advantage_wins(self):
        blue_lost, red_lost = self._totals(self.stealth)
        self.assertGreater(red_lost, blue_lost)

    def test_stealth_improves_the_exchange_ratio(self):
        control_blue, control_red = self._totals(self.control)
        stealth_blue, stealth_red = self._totals(self.stealth)
        # red/blue confrontati per moltiplicazione incrociata (niente divisioni per zero).
        self.assertGreater(stealth_red * control_blue, control_red * stealth_blue)
        self.assertLess(stealth_blue, control_blue)


# ── S4 — SAM COME TERZA COMPONENTE ────────────────────────────────────────────

class TestS4SAMAsThirdComponent(F.LoggerSilencer, unittest.TestCase):
    """S4: scontro terra-terra con un sito SAM che interviene contro il CAS di un lato.

    Composizione: Blue-Armor 4 M1A2 (in avanzata da 12 km) contro Red-Armor 4 T-72B
    (sensori visivi dichiarati), Blue-CAS 2 A-10C (loadout 'Maverick/Gun CAS', ruolo
    strike) in arrivo da 120 km, cosi' che il CAS arrivi PRIMA del contatto terrestre;
    variante con Red-SAM 2 9K37 Buk schierati 40 km avanti alla linea rossa, a coprire
    l'avvicinamento del CAS (il Buk vede il CAS prima che il CAS veda i carri).

    Domanda: il SAM riduce l'efficacia del CAS del lato che lo subisce. Efficacia = danni
    inflitti dal CAS alla forza corazzata rossa; in piu' il CAS subisce perdite solo dove
    c'e' il SAM, e il SAM entra nello STESSO ingaggio dello scontro terrestre (terza forza
    della componente connessa). Aggregati su 8 repliche, stessi seed nelle due varianti.
    """

    SEEDS = _seeds('S4', 8)

    @staticmethod
    def _build(with_sam):
        blue = F.build_force('Blue-Armor', 'Blue', [F.Unit('vehicle', 'M1A2-Abrams', 4, origin=(-12_000.0, 0.0),
                                                           step=(0.0, 300.0), prefix='mbt', sensors=VISUAL)])
        cas = F.build_force('Blue-CAS', 'Blue', [F.Unit('aircraft', 'A-10C Thunderbolt II', 2,
                                                         origin=(-120_000.0, 0.0, 3_000.0), step=(0.0, 500.0),
                                                         prefix='cas', loadout='Maverick/Gun CAS')],
                            mil_category=F.AIR_UNIT)
        red = [F.build_force('Red-Armor', 'Red', [F.Unit('vehicle', 'T-72B', 4, origin=(0.0, 0.0),
                                                          step=(0.0, 300.0), prefix='mbt', sensors=VISUAL)])]

        if with_sam:
            red.append(F.build_force('Red-SAM', 'Red', [F.Unit('vehicle', '9K37-Buk', 2, origin=(-40_000.0, 5_000.0),
                                                               step=(0.0, 400.0), prefix='sam')]))

        routes = F.routes_for(blue, [(-3_000.0, 0.0)])
        routes.update(F.routes_for(cas, [(5_000.0, 0.0)]))
        fire = F.make_fire_control(roles={asset_id: 'strike' for asset_id in cas.assets})
        return [blue, cas], red, routes, fire

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {False: [], True: []}

        for session_id in cls.SEEDS:
            for with_sam in (False, True):
                blue, red, routes, fire = cls._build(with_sam)
                outcome = F.run(session_id, blue, red, fire, duration=3_600.0, routes=routes)
                cls.runs[with_sam].append((blue, red, outcome))

    def _cas_damage_on_armor(self, with_sam):
        total = 0

        for blue, red, outcome in self.runs[with_sam]:
            armor = F.asset_ids(red[0])
            total += sum(1 for e in F.damage_by_source(outcome, F.asset_ids(blue[1])) if e.target_id in armor)

        return total

    def test_premise_cas_is_effective_without_sam(self):
        self.assertGreater(self._cas_damage_on_armor(False), 0)

    def test_sam_reduces_cas_effectiveness(self):
        self.assertLess(self._cas_damage_on_armor(True), self._cas_damage_on_armor(False))

    def test_cas_losses_come_from_the_sam(self):
        self.assertEqual(sum(F.losses_of(o, 'Blue-CAS') for _, _, o in self.runs[False]), 0)
        self.assertGreater(sum(F.losses_of(o, 'Blue-CAS') for _, _, o in self.runs[True]), 0)

    def test_sam_joins_the_same_engagement(self):
        """Il SAM non e' un ingaggio a parte: e' la terza (quarta) forza della componente."""
        for _, _, outcome in self.runs[True]:
            ids = [tuple(o.force_id for o in e) for e in outcome.engagement_outcomes]
            self.assertIn(('Blue-Armor', 'Blue-CAS', 'Red-Armor', 'Red-SAM'), ids)


# ── S5 — INTERDIZIONE PROFONDA CONTRO DIFESA A 3 STRATI ───────────────────────

class TestS5DeepInterdictionThreeLayers(F.LoggerSilencer, unittest.TestCase):
    """S5: missione aerea profonda contro un bersaglio composito dietro 3 strati di difesa.

    Composizione: Blue-Deep 4 F-15E (loadout 'Laser Strike', ruolo strike) su una rotta di
    950 km; lungo la rotta, a distanze tali che le bolle non si sovrappongano:
      * Red-L1-Long   — 1 S-300PS (lungo raggio), a x = 0;
      * Red-L2-Medium — 1 9K37 Buk (medio raggio), a x = 400 km;
      * Red-L3-Point  — 1 2K22 Tunguska + 1 ZSU-23-4 (difesa di punto), sul bersaglio;
      * Red-Target    — 3 BMP-2 + 2 2S19-Msta (bersaglio composito), a x = 600 km.

    Domanda: la missione subisce ingaggi a piu' livelli prima di raggiungere il bersaglio,
    oppure viene fermata prima. Due varianti:
      * dottrina "ad oltranza" (PRESS_ON): gli strati ingaggiano nell'ordine geometrico, e la
        missione o arriva al bersaglio o viene distrutta;
      * dottrina di default: alla prima perdita la formazione rompe il contatto, e da quel
        momento nessuno strato successivo la puo' piu' ingaggiare (forza rotta, v.
        "Forze rotte" in Engagement_Resolver).
    """

    SEEDS = _seeds('S5', 6)
    LAYERS = ('Red-L1-Long', 'Red-L2-Medium', 'Red-L3-Point')

    @staticmethod
    def _build():
        strike = F.build_force('Blue-Deep', 'Blue', [F.Unit('aircraft', 'F-15E Strike Eagle', 4,
                                                            origin=(-300_000.0, 0.0, 6_000.0), step=(0.0, 500.0),
                                                            prefix='str', loadout='Laser Strike')],
                               mil_category=F.AIR_UNIT)
        reds = [
            F.build_force('Red-L1-Long', 'Red', [F.Unit('vehicle', 'S-300PS', 1, origin=(0.0, 20_000.0), prefix='sam')]),
            F.build_force('Red-L2-Medium', 'Red', [F.Unit('vehicle', '9K37-Buk', 1, origin=(400_000.0, 10_000.0),
                                                          prefix='sam')]),
            F.build_force('Red-L3-Point', 'Red', [
                F.Unit('vehicle', '2K22-Tunguska', 1, origin=(600_000.0, 2_000.0), prefix='sam'),
                F.Unit('vehicle', 'ZSU-23-4-Shilka', 1, origin=(600_000.0, -2_000.0), prefix='aaa')]),
            F.build_force('Red-Target', 'Red', [
                F.Unit('vehicle', 'BMP-2', 3, origin=(600_000.0, 0.0), step=(0.0, 200.0), prefix='tgt'),
                F.Unit('vehicle', '2S19-Msta', 2, origin=(600_500.0, 0.0), step=(0.0, 200.0), prefix='art')]),
        ]
        routes = F.routes_for(strike, [(650_000.0, 0.0)])
        fire = F.make_fire_control(roles={asset_id: 'strike' for asset_id in strike.assets})
        return strike, reds, routes, fire

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.press_on, cls.default = [], []

        for session_id in cls.SEEDS:
            for bucket, thresholds in ((cls.press_on, PRESS_ON), (cls.default, None)):
                strike, reds, routes, fire = cls._build()
                outcome = F.run(session_id, [strike], reds, fire, duration=7_200.0, routes=routes,
                                thresholds=thresholds)
                bucket.append((strike, reds, outcome))

    def _layer_first_shots(self, reds, outcome):
        first = F.salvo_shooters(outcome)
        by_force = {force.id: force for force in reds}
        return {layer: min((first[a] for a in by_force[layer].assets if a in first), default=None)
                for layer in self.LAYERS}

    def test_layers_engage_in_geometric_order(self):
        for _, reds, outcome in self.press_on:
            times = [t for t in self._layer_first_shots(reds, outcome).values() if t is not None]
            self.assertEqual(times, sorted(times))
            self.assertGreaterEqual(len(times), 1)

    def test_mission_is_engaged_at_several_layers(self):
        fired = [sum(t is not None for t in self._layer_first_shots(reds, o).values())
                 for _, reds, o in self.press_on]
        self.assertTrue(all(count >= 2 for count in fired), fired)
        self.assertIn(3, fired)

    def test_mission_reaches_the_target_or_is_stopped(self):
        for strike, _, outcome in self.press_on:
            result = F.force_outcome(outcome, 'Blue-Deep')
            reached = any(e.asset_id in strike.assets for e in outcome.ammunition_events)
            self.assertTrue(reached or result.outcome in (ER.DESTROYED, ER.DISENGAGED))

    def test_default_doctrine_stops_the_mission_at_the_first_layer(self):
        for _, reds, outcome in self.default:
            result = F.force_outcome(outcome, 'Blue-Deep')
            shots = self._layer_first_shots(reds, outcome)

            if result.outcome == ER.HELD:
                continue   # nessuna perdita al primo strato: nulla da verificare

            self.assertIsNone(shots['Red-L2-Medium'])
            self.assertIsNone(shots['Red-L3-Point'])
            # Dopo la rottura nessuna forza rossa lancia piu' contro la formazione.
            red_ids = {a for force in reds for a in force.assets}
            late = [e for e in outcome.ammunition_events
                    if e.asset_id in red_ids and e.time > result.time]
            self.assertEqual(late, [])

        self.assertTrue(any(F.force_outcome(o, 'Blue-Deep').outcome != ER.HELD for _, _, o in self.default))


# ── S6 — GRUPPO NAVALE CONTRO DIFESA COSTIERA ─────────────────────────────────

class TestS6CarrierGroupVersusCoastalDefence(F.LoggerSilencer, unittest.TestCase):
    """S6: gruppo da battaglia navale contro un litorale difeso da terra e da mare.

    Composizione: Blue-CSG = CVN-70 + CG-65 + Arleigh Burke IIa in movimento verso costa;
    Blue-AirWing = 4 F/A-18C (loadout 'Strike', multiruolo) diretti sulla costa;
    Red-Coast (Stronghold) = 1 S-300PS + 2 ZSU-23-4 + 3 BMP-2 a terra;
    Red-Flotilla = 2 corvette Molniya a nord lungo la costa.
    Dottrina Blue ad oltranza (PRESS_ON), perche' l'ala deve arrivare sulla costa.

    Domanda (meccanismo, P3): la fusione delle finestre di contatto quando le minacce sono
    sia a terra sia in mare. Si verifica che:
      * lo scheduler produce finestre di dominio misto (aereo-veicolo, aereo-nave,
        nave-nave) e che `run_session` le fonde in UN solo ingaggio con tutte e quattro le
        forze;
      * nella stessa timeline agiscono entrambe le minacce (salve lanciate sia da Ship
        rosse sia da Vehicle rossi) e le navi usano la loro difesa (intercettazioni);
      * i danni cadono su piu' classi di asset.

    Lacuna dei registri (documentata, non aggirata): nessuna nave dichiara un sensore in
    modo 'ground' e nessun sistema costiero un sensore in modo 'sea', quindi NON esistono
    finestre dirette nave-veicolo costiero; il collegamento terra-mare passa dall'ala
    imbarcata. Il test lo registra esplicitamente.
    """

    SEEDS = _seeds('S6', 4)

    @staticmethod
    def _build():
        csg = F.build_force('Blue-CSG', 'Blue', [
            F.Unit('ship', 'CVN-70 Carl Vinson', 1, origin=(-150_000.0, 0.0), prefix='cv'),
            F.Unit('ship', 'CG-65', 1, origin=(-147_000.0, 3_000.0), prefix='cg'),
            F.Unit('ship', 'USS Arleigh Burke IIa', 1, origin=(-147_000.0, -3_000.0), prefix='ddg')],
            mil_category=F.NAVAL_UNIT)
        wing = F.build_force('Blue-AirWing', 'Blue', [F.Unit('aircraft', 'F/A-18C Hornet', 4,
                                                             origin=(-140_000.0, 0.0, 6_000.0), step=(0.0, 800.0),
                                                             prefix='fa', loadout='Strike')],
                             mil_category=F.AIR_UNIT)
        coast = F.build_force('Red-Coast', 'Red', [
            F.Unit('vehicle', 'S-300PS', 1, origin=(30_000.0, 10_000.0), prefix='sam'),
            F.Unit('vehicle', 'ZSU-23-4-Shilka', 2, origin=(0.0, -1_000.0), step=(0.0, 2_000.0), prefix='aaa'),
            F.Unit('vehicle', 'BMP-2', 3, origin=(2_000.0, 0.0), step=(0.0, 400.0), prefix='ifv')],
            mil_category=F.MILITARY_CATEGORY['Ground_Base'][0])
        flotilla = F.build_force('Red-Flotilla', 'Red', [F.Unit('ship', 'FSG 1241.1MP Molniya', 2,
                                                                origin=(0.0, 90_000.0), step=(5_000.0, 0.0),
                                                                prefix='fsg')],
                                 mil_category=F.NAVAL_UNIT)
        routes = F.routes_for(csg, [(-60_000.0, 0.0)])
        routes.update(F.routes_for(wing, [(5_000.0, 0.0)]))
        return [csg, wing], [coast, flotilla], routes

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        blue, red, routes = cls._build()
        cls.windows = CS.schedule_contacts(blue, red, 7_200.0, routes=routes)
        cls.window_types = _type_of(blue + red)
        cls.runs = []

        for session_id in cls.SEEDS:
            blue, red, routes = cls._build()
            outcome = F.run(session_id, blue, red, F.make_fire_control(), duration=7_200.0, routes=routes,
                            thresholds=PRESS_ON)
            cls.runs.append((_type_of(blue + red), outcome))

    def test_scheduler_produces_mixed_domain_windows(self):
        kinds = Counter(tuple(sorted((self.window_types[w.asset_a_id], self.window_types[w.asset_b_id])))
                        for w in self.windows)
        self.assertGreater(kinds[('Aircraft', 'Vehicle')], 0)
        self.assertGreater(kinds[('Aircraft', 'Ship')], 0)
        self.assertGreater(kinds[('Ship', 'Ship')], 0)
        # Lacuna dei registri (v. docstring): nessuna finestra diretta nave-costa.
        self.assertEqual(kinds[('Ship', 'Vehicle')], 0)

    def test_land_and_sea_threats_are_fused_in_one_engagement(self):
        for _, outcome in self.runs:
            ids = [tuple(o.force_id for o in e) for e in outcome.engagement_outcomes]
            self.assertEqual(ids, [('Blue-AirWing', 'Blue-CSG', 'Red-Coast', 'Red-Flotilla')])

    def test_both_threats_act_in_the_same_timeline(self):
        shooters = Counter()

        for types, outcome in self.runs:
            for event in outcome.ammunition_events:
                if event.asset_id.startswith('Red-'):
                    shooters[types[event.asset_id]] += 1

        self.assertGreater(shooters['Ship'], 0)
        self.assertGreater(shooters['Vehicle'], 0)

    def test_ships_defend_themselves(self):
        interceptions = sum(1 for types, o in self.runs for e in o.interception_events
                            if types[e.asset_id] == 'Ship')
        self.assertGreater(interceptions, 0)

    def test_blue_aircraft_are_hit_by_both_land_and_sea_threats(self):
        """La stessa forza (l'ala imbarcata) e' colpita da tiratori terrestri E navali nella
        stessa run: e' la fusione vista dal lato degli effetti."""
        sources = Counter()

        for types, outcome in self.runs:
            for event in outcome.damage_events:
                if types[event.target_id] == 'Aircraft' and event.source_id is not None:
                    sources[types[event.source_id]] += 1

        self.assertGreater(sources['Ship'], 0)
        self.assertGreater(sources['Vehicle'], 0)


# ── S7 — INTERDIZIONE DI UNA LINEA LOGISTICA ──────────────────────────────────

class TestS7LogisticInterdiction(F.LoggerSilencer, unittest.TestCase):
    """S7: attacco aereo contro un bersaglio NON militare con scorta di caccia.

    Rappresentazione del bersaglio (scelta dichiarata): `Transport`/`Storage` non sono
    istanziabili (il loro `__init__` passa 11 argomenti posizionali a `Block.__init__`, che
    ne accetta 10: TypeError) e `Structure` neppure (argomenti posizionali disallineati
    rispetto ad `Asset.__init__`). Il bersaglio e' quindi un `Block` generico con
    `category='Logistic'` — la classe base di Transport/Storage, con la stessa categoria —
    che contiene 4 veicoli MT-LB (trasporto cingolato multiuso, il mezzo del registro piu'
    vicino a un trasporto logistico; nessun camion nei registri). Il blocco NON e' una
    `Military`: nessun `combat_power`, nessuna `salvo_interceptors`, e il fire_control di
    riferimento non da' armi al ruolo 'logistic'.

    Composizione: Red-Depot (logistico, 4 MT-LB fermi); Red-Escort 2 MiG-29S (loadout
    'CAP') in pattugliamento verso ovest; Blue-Interdiction 2 F-16C (loadout 'Strike',
    ruolo strike) + 2 F-15C (loadout 'Eagle Escort', ruolo fighter).

    Domanda: il bersaglio non-militare riceve danni ed eventi corretti anche senza combat
    power proprio; il motore non assume che ogni forza sia una `Military`.
    """

    SEEDS = _seeds('S7', 6)

    @staticmethod
    def _build():
        depot = F.build_force('Red-Depot', 'Red', [F.Unit('vehicle', 'MT-LB', 4, origin=(0.0, 0.0),
                                                          step=(0.0, 150.0), prefix='trk')],
                              category=F.LOGISTIC_CATEGORY)
        escort = F.build_force('Red-Escort', 'Red', [F.Unit('aircraft', 'MiG-29S', 2, origin=(30_000.0, 0.0),
                                                            step=(0.0, 1_000.0), prefix='cap', loadout='CAP')],
                               mil_category=F.AIR_UNIT)
        package = F.build_force('Blue-Interdiction', 'Blue', [
            F.Unit('aircraft', 'F-16C Block 52d', 2, origin=(-150_000.0, 0.0), step=(0.0, 600.0),
                   prefix='str', loadout='Strike'),
            F.Unit('aircraft', 'F-15C Eagle', 2, origin=(-148_000.0, 2_000.0), step=(0.0, 600.0),
                   prefix='esc', loadout='Eagle Escort')], mil_category=F.AIR_UNIT)
        roles = {a: ('strike' if '/str' in a else 'fighter') for a in package.assets}
        routes = F.routes_for(package, [(20_000.0, 0.0)])
        routes.update(F.routes_for(escort, [(-60_000.0, 0.0)]))
        return package, depot, escort, routes, F.make_fire_control(roles=roles)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = []

        for session_id in cls.SEEDS:
            package, depot, escort, routes, fire = cls._build()
            outcome = F.run(session_id, [package], [depot, escort], fire, duration=3_600.0, routes=routes)
            cls.runs.append((depot, outcome))

    def test_target_is_really_not_military(self):
        depot, _ = self.runs[0]
        self.assertIsInstance(depot, Block)
        self.assertNotIsInstance(depot, Military)
        self.assertTrue(depot.is_logistic())
        self.assertFalse(hasattr(depot, 'salvo_interceptors'))

    def test_non_military_target_takes_damage(self):
        self.assertGreater(sum(len(F.damage_on(o, depot.assets)) for depot, o in self.runs), 0)

    def test_non_military_target_never_fires_nor_intercepts(self):
        for depot, outcome in self.runs:
            self.assertEqual([a for a in F.active_assets(outcome) if a in depot.assets], [])

    def test_target_has_a_force_outcome(self):
        for depot, outcome in self.runs:
            found = F.force_outcome(outcome, 'Red-Depot')
            self.assertIsNotNone(found)
            self.assertEqual(found.committed, len(depot.assets))
            self.assertIn(found.outcome, ER.FORCE_OUTCOMES)

    def test_damage_is_applied_to_the_real_logistic_assets(self):
        for depot, outcome in self.runs:
            final = {}
            for event in outcome.damage_events:
                final[event.target_id] = event.health_after
            for asset_id, asset in depot.assets.items():
                self.assertEqual(asset.health, final.get(asset_id, 100))

    def test_escort_and_package_fight_in_the_same_engagement(self):
        for _, outcome in self.runs:
            ids = [tuple(o.force_id for o in e) for e in outcome.engagement_outcomes]
            self.assertEqual(ids, [('Blue-Interdiction', 'Red-Depot', 'Red-Escort')])


# ── S8 — FRONTE MULTIPLO, STRESS DI SCALA ─────────────────────────────────────

class TestS8MultiFrontScale(F.LoggerSilencer, unittest.TestCase):
    """S8: decine di blocchi su piu' fronti. Test di SCALA, non di correttezza tattica.

    Composizione: FRONTS fronti distanti 500 km l'uno dall'altro; su ciascuno PER_SIDE
    blocchi Blue (M1A2) e PER_SIDE blocchi Red (T-72B) da ASSETS asset ciascuno, affrontati
    a coppie a 3.5 km (dentro la portata visiva dichiarata di 4 km), coppie distanziate di
    20 km lungo il fronte. Totale 40 blocchi e 240 asset: abbastanza per esercitare la
    potatura gerarchica di `Contact_Scheduler.block_pair_candidates` (meccanismo C), molto
    sotto il limite dichiarato di 10.000 asset (un test automatico a quella scala sarebbe
    troppo lento).

    Verifiche:
      * la potatura scarta la maggioranza delle coppie di blocchi (tutte quelle fra fronti
        diversi) e le scarta in modo CONSERVATIVO: nessuna coppia di asset scartata avrebbe
        avuto una finestra di contatto;
      * ogni fronte produce i propri ingaggi, disgiunti;
      * la sessione completa entro una soglia LARGA (MAX_SECONDS), per intercettare
        regressioni d'ordine di grandezza, non per misurare prestazioni fini. Il tempo e'
        dominato oggi dalla costruzione di `sympy.Point3D` in
        `Contact_Scheduler.closest_point_of_approach` (v. report di Fase 7).
    """

    FRONTS, PER_SIDE, ASSETS = 5, 4, 6
    MAX_SECONDS = 90.0

    @classmethod
    def _build(cls):
        blue, red = [], []

        for front in range(cls.FRONTS):
            y0 = front * 500_000.0

            for index in range(cls.PER_SIDE):
                x0 = index * 20_000.0
                blue.append(F.build_force(f'Blue-F{front}-B{index}', 'Blue', [
                    F.Unit('vehicle', 'M1A2-Abrams', cls.ASSETS, origin=(x0, y0), step=(150.0, 0.0),
                           prefix='mbt', sensors=VISUAL)]))
                red.append(F.build_force(f'Red-F{front}-B{index}', 'Red', [
                    F.Unit('vehicle', 'T-72B', cls.ASSETS, origin=(x0, y0 + 3_500.0), step=(150.0, 0.0),
                           prefix='mbt', sensors=VISUAL)]))

        return blue, red

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.blue, cls.red = cls._build()
        cls.candidates = CS.block_pair_candidates(cls.blue, cls.red, 3_600.0)
        cls.outcome, cls.seconds = F.timed(F.run, 'S8-scale', cls.blue, cls.red, F.make_fire_control(),
                                           duration=3_600.0)

    @staticmethod
    def _front(force_id):
        return force_id.split('-')[1]

    def test_scale_of_the_scenario(self):
        self.assertEqual(len(self.blue) + len(self.red), 2 * self.FRONTS * self.PER_SIDE)
        self.assertEqual(sum(len(f.assets) for f in self.blue + self.red),
                         2 * self.FRONTS * self.PER_SIDE * self.ASSETS)

    def test_pruning_discards_most_block_pairs(self):
        total = len(self.blue) * len(self.red)
        self.assertLess(len(self.candidates), total / 2)

        for block_a, block_b in self.candidates:
            self.assertEqual(self._front(block_a.id), self._front(block_b.id))

    def test_pruning_is_conservative(self):
        """Nessuna coppia di asset di blocchi scartati avrebbe prodotto una finestra."""
        kept = {(a.id, b.id) for a, b in self.candidates}
        horizon = 3_600.0

        for block_a in self.blue:
            for block_b in self.red:
                if (block_a.id, block_b.id) in kept:
                    continue

                for asset_a in block_a.assets.values():
                    legs_a = CS.static_legs(asset_a.position, 0.0, horizon)

                    for asset_b in block_b.assets.values():
                        legs_b = CS.static_legs(asset_b.position, 0.0, horizon)
                        self.assertEqual(CS.contact_windows(asset_a, legs_a, asset_b, legs_b), [])

    def test_every_front_fights_on_its_own(self):
        fronts = set()

        for engagement in self.outcome.engagement_outcomes:
            engaged = {self._front(o.force_id) for o in engagement}
            self.assertEqual(len(engaged), 1)
            fronts |= engaged

        self.assertEqual(len(fronts), self.FRONTS)

    def test_session_completes_within_a_loose_bound(self):
        self.assertIsInstance(self.outcome, SessionOutcome)
        self.assertLess(self.seconds, self.MAX_SECONDS)


# ── S9 — TARGETING SOTTO FOG-OF-WAR PARZIALE ──────────────────────────────────

class TestS9PartialFogOfWar(F.LoggerSilencer, unittest.TestCase):
    """S9: stessa composizione di S1, con ricognizione del lato Blue incompleta.

    **Gap documentato, non aggirato.** Il fog-of-war del progetto vive in
    `Context/Region`/`Logic/Tactical_Analysis`/`Logic/Tactical_Evaluation`
    (`recon_cp_snapshot`, `use_recon`, policy "non visto -> priorita' bassa") ed e' una
    nozione INFORMATIVA di livello C2: decide le priorita' di targeting a partire da cio'
    che la ricognizione ha confermato. Il motore di sessione (`Session_Simulator`,
    `Engagement_Resolver`) non ha oggi NESSUN aggancio a quel sistema: non riceve uno
    snapshot di ricognizione e non conosce priorita'. Le due nozioni di "visibilita'" che P3
    voleva mettere in tensione (geometrica = nel raggio di un sensore; informativa =
    confermata dal C2) non sono quindi ancora collegate, e un test che le collegasse
    dovrebbe inventare un collegamento che non esiste.

    Cio' che esiste, ed e' il punto di aggancio naturale per il futuro, e' il
    `detection_factor` di `resolve_engagement` (passato da `run_session`): un fattore in
    [0, 1] per coppia (osservatore, bersaglio) che scala la Pd. Qui lo si usa per simulare
    una ricognizione degradata del SOLO lato Blue (i suoi osservatori), confrontando fattore
    1.0 (piena), 0.5 (parziale) e 0.0 (cieca). Il collegamento vero —
    fattore/abilitazione derivati da `recon_cp_snapshot` di `Region` per coppia — resta
    lavoro futuro.

    Domande verificate:
      * il fattore agisce SOLO sugli osservatori a cui e' applicato (Red intatto);
      * degradare la ricognizione riduce la frazione di rilevamenti riusciti del lato Blue;
      * con ricognizione nulla Blue non rileva nulla e quindi non spara, mentre Red combatte.
    """

    SEEDS = _seeds('S9', 6)
    FACTORS = (1.0, 0.5, 0.0)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = {factor: [] for factor in cls.FACTORS}
        original = ER.resolve_engagement

        for factor in cls.FACTORS:
            for session_id in cls.SEEDS:
                scenario = F.combined_arms_scenario()
                blue_ids = frozenset(a for force in scenario.forces_a for a in force.assets)
                degrade = (lambda observer, target, ids=blue_ids, f=factor: f if observer.id in ids else 1.0)
                captured = []

                def spy(*args, **kwargs):
                    result = original(*args, **kwargs)
                    captured.append(result)
                    return result

                # Si cattura l'EngagementResult (che porta le Detection) senza alterarlo.
                with patch.object(ER, 'resolve_engagement', side_effect=spy):
                    outcome = scenario.run(session_id, detection_factor=degrade)

                cls.runs[factor].append((blue_ids, outcome, [r for r in captured if r is not None]))

    def _detection_rate(self, factor, blue_side):
        detected = total = 0

        for blue_ids, _, results in self.runs[factor]:
            for result in results:
                for detection in result.detections:
                    if (detection.observer_id in blue_ids) == blue_side:
                        total += 1
                        detected += detection.detected

        return detected / total if total else 0.0

    def test_degraded_recon_lowers_blue_detection_rate(self):
        self.assertGreater(self._detection_rate(1.0, True), self._detection_rate(0.5, True))
        self.assertGreater(self._detection_rate(0.5, True), 0.0)

    def test_factor_does_not_touch_the_other_side(self):
        """Red resta a piena Pd: con Blue degradato il tasso di rilevamento di Red resta
        sopra quello di Blue (le estrazioni cambiano comunque, perche' lo stream e' unico
        per ingaggio e l'ordine delle estrazioni fa parte del contratto)."""
        for factor in (0.5, 0.0):
            with self.subTest(factor=factor):
                self.assertGreater(self._detection_rate(factor, False), self._detection_rate(factor, True))

    def test_blind_side_never_fires_but_the_other_does(self):
        blue_salvos = red_salvos = 0

        for blue_ids, outcome, _ in self.runs[0.0]:
            for event in outcome.ammunition_events:   # solo salve (tipi distinti dal 2026-09-23)
                if event.asset_id in blue_ids:
                    blue_salvos += 1
                else:
                    red_salvos += 1

        self.assertEqual(blue_salvos, 0)
        self.assertGreater(red_salvos, 0)

    def test_blind_side_inflicts_no_damage(self):
        for blue_ids, outcome, _ in self.runs[0.0]:
            self.assertEqual(F.damage_by_source(outcome, blue_ids), [])


if __name__ == '__main__':
    unittest.main()
