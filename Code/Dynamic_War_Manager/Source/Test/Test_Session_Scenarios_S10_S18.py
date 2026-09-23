"""FASE 7 del motore di sessioni virtuali — scenari di plausibilita' S10-S18 (seconda meta').

Prosegue `Test_Session_Scenarios.py` (S1-S9) con la stessa disciplina (wiki
`decisions/soglie-disingaggio-e-attrito-aggregato`, P3): **si prende la composizione delle
forze e la domanda che pone, MAI coefficienti o esiti numerici precalcolati**. Ogni test
verifica un comportamento QUALITATIVO o STRUTTURALE del motore — un esito ha l'etichetta
attesa, un evento accade o non accade, un campo dell'esito ha la forma attesa, una
grandezza cresce con la scala — mai un numero calibrato.

S10 e S11 completano la batteria "ufficiale" S1-S11 di P3 (soglia di disingaggio; confine
sessione DCS/sessione sintetica). S12-S18 sono stati aggiunti per esercitare i blocchi non
militari resi costruibili il 2026-09-23 (`Production`, `Transport`, `Storage`, `Urban`,
`Structure`), i bersagli fissi ad alto valore di una `Military` (C2, FARP, porto) e la
scala gerarchica.

## Robustezza statistica
Come in S1-S9: dove la risposta dipende dall'RNG lo scenario e' ripetuto su piu'
`session_id` (quindi piu' seed) e il confronto e' sugli AGGREGATI; le repliche girano una
volta per classe (`setUpClass`). Tutto e' deterministico: le soglie qualitative sono state
scelte con margine rispetto a quanto osservato.

## Bersagli fissi: `Structure`
Un edificio/ponte/bunker e' una `Structure` reale (`Scenario_Fixtures.make_structure`),
classificata dal `fire_control` di riferimento nel ruolo 'structure' (o 'logistic' se il
blocco e' logistico) e rilevata dai sensori nel modo 'ground' (v.
`Contact_Scheduler.DETECTION_MODE_BY_CLASS`). Una Structure non ha sensori ne' armi: non
spara, non intercetta, non vede — e' solo un bersaglio.

## Dottrina delle installazioni fisse
La regola "solo le `Military` si disingaggiano" (Engagement_Resolver, §6) tratta come
forza manovrabile ANCHE una `Military` che rappresenta un'installazione fissa (bunker C2,
FARP, porto): con la dottrina di default rompe il contatto alla prima perdita
significativa. Dove la domanda dello scenario richiede che l'installazione resti sotto il
fuoco (S13, S16) lo si dichiara con una tabella dottrinale esplicita per il lato Red
(`RED_HOLDS`), come S5/S6 fanno per Blue. V. il report di Fase 7 per la raccomandazione.

## Intercettazione (R1) contro installazioni con difesa aerea organica — finding di Fase 7
Nella prima stesura di Fase 7 la scorta di intercettazione era `Mobile.ammunition`, un
conteggio di COLPI: con capacita' = somma dei canali e Pk = 1 per canale, una `Military`
con anche un solo ZSU-23-4 (2000 colpi da 23 mm nel registro) intercettava TUTTI i colpi
intercettabili di un'incursione non saturante, indefinitamente — nelle prime stesure di
S12/S13/S16 ogni 'agm'/'arm' e' stato fermato (fino a 88 su 88).

RISOLTO alla radice dalla ricalibrazione della Fase 4 (2026-09-23): la scorta di
intercettazione e' ora un contatore distinto, `Mobile.interceptor_stock` (1 per missile AD,
colpi // ROUNDS_PER_GUN_INTERCEPT per i cannoni AD: Shilka 20, Strela-10 8, Molniya 16),
e un'intercettazione non consuma piu' `ammunition`. La difesa si esaurisce e il surplus
arriva a segno: S16 verifica di nuovo i danni su navi e strutture.

Due rifiniture successive dello stesso giorno: (1) le intercettazioni sono un tipo
d'evento a parte, `ER.InterceptionEvent` in `SessionOutcome.interception_events`
(`interceptions_consumed()`), e `ammunition_events`/`ammunition_consumed()` contano ora le
sole salve offensive; (2) per i SAM puri (qui il 9K35-Strela-10 di S11/S13) munizioni e
intercettori sono lo STESSO pool (Mobile.interceptor_shares_ammunition): S11 lo verifica
sul confine di sessione. Shilka (cannone puro) e Molniya (SAM + cannoni + antinave)
restano a contatori indipendenti.

S12/S13 continuano a usare l'arma che il loadout porta davvero — bombe (`SHOTS['bomb']`,
non intercettabili: F-16C 'Strike' = Mk-82/Mk-83, F-15E 'Laser Strike' = GBU-12) —
tramite STRIKE_BOMB_TABLE. Non e' piu' un aggiramento dell'intercettazione inesauribile
(con gli 'agm' intercettabili ora 28 colpi su ~34 vengono fermati e il resto arriva a
segno), ma resta la scelta fedele al loadout, e le verifiche di S12/S13 sono tarate su di
essa: lasciata invariata.

## Costanti di scenario
Composizioni, geometrie e ShotSpec sono dichiarate qui o in `Scenario_Fixtures`; nessuna
viene da una fonte esterna. Posizioni in metri su un piano locale, tempi in secondi
assoluti.
"""

import math
import unittest
from collections import Counter
from unittest.mock import patch

from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Block.Military import Military
from Code.Dynamic_War_Manager.Source.Block.Production import Production
from Code.Dynamic_War_Manager.Source.Block.Transport import Transport
from Code.Dynamic_War_Manager.Source.Block.Urban import Urban
from Code.Dynamic_War_Manager.Source.Asset.Structure import Structure
from Code.Dynamic_War_Manager.Source.Command.Session_Types import SessionOrder, SessionOutcome
from Code.Dynamic_War_Manager.Source.Context import Doctrine
from Code.Dynamic_War_Manager.Source.Context.Context import MILITARY_CATEGORY
from Code.Dynamic_War_Manager.Source.Logic import Contact_Scheduler as CS
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic import Session_Simulator as SS

VISUAL = {'ground': F.DECLARED_GROUND_VISUAL_RANGE}

_HOLD = {Doctrine.DISENGAGEMENT_EROSION: 1.0, Doctrine.DISENGAGEMENT_SHOCK: 1.0}

# Installazione fissa rossa che resta sotto il fuoco (v. docstring del modulo).
RED_HOLDS = {
    'Blue': dict(Doctrine.DEFAULT_DISENGAGEMENT_THRESHOLDS['Blue']),
    'Red': dict(_HOLD),
}

# Entrambi i lati ad oltranza: uno scambio che non si interrompe alla prima perdita.
BOTH_HOLD = {'Blue': dict(_HOLD), 'Red': dict(_HOLD)}

# Tabella di fuoco per le missioni di bombardamento (v. "Intercettazione" nel docstring):
# il ruolo 'strike' sgancia bombe non intercettabili (`SHOTS['bomb']`, l'arma dei loadout
# 'Strike'/'Laser Strike') sui bersagli di superficie non-AD; tutto il resto come nella
# tabella di riferimento.
STRIKE_BOMB_TABLE = {
    **F.REFERENCE_FIRE_TABLE,
    **{('strike', target): F.SHOTS['bomb'] for target in ('ground', 'artillery', 'logistic', 'structure')},
}

GROUND_BASE = MILITARY_CATEGORY['Ground_Base']
NAVAL_BASE = MILITARY_CATEGORY['Naval_Base']


def _seeds(prefix: str, count: int):
    return [f'{prefix}-{index}' for index in range(count)]


def _engagement_ids(outcome):
    return [tuple(o.force_id for o in e) for e in outcome.engagement_outcomes]


def _salvos_by(outcome, asset_ids):
    """AmmunitionEvent (dal 2026-09-23: solo salve offensive) degli asset `asset_ids`."""
    wanted = set(asset_ids)
    return [e for e in outcome.ammunition_events if e.asset_id in wanted]


def _type_of(forces):
    return {asset_id: type(asset).__name__ for force in forces for asset_id, asset in force.assets.items()}


def _strike_roles(force, role='strike'):
    return {asset_id: role for asset_id in force.assets}


# ── S10 — REGRESSIONE SULLA SOGLIA DI DISINGAGGIO ─────────────────────────────

class TestS10DisengagementThreshold(F.LoggerSilencer, unittest.TestCase):
    """S10: una forza supera la soglia dottrinale a meta' di un ingaggio gia' in corso.

    Scenario minimo costruito apposta, NON tattico. Red-Column 10 BMP-2 fermi, Blue-Gun
    M1A2 fermi a 3 km (dentro la portata visiva dichiarata di 4 km). Il `fire_control`
    arma SOLO i carri Blue (tabella vuota + override per id): Red non risponde, cosi' le
    perdite di Red sono l'unica variabile e l'esito dipende solo dalla dottrina.

    Casi (dottrina di default, `Doctrine.DEFAULT_DISENGAGEMENT_THRESHOLDS`: erosione 0.30,
    shock 0.20 per entrambi i lati):
      * EROSIONE — 1 solo tiratore: ogni salva costa a Red al massimo 1 mezzo su 10 (0.10,
        sotto lo shock), quindi la soglia che scatta e' l'erosione, a ingaggio gia' in
        corso (dopo salve che non l'hanno fatta scattare). Domanda: esito DISENGAGED, non
        annientamento, e nessun colpo parte piu' contro Red dopo la rottura.
      * SHOCK — 4 tiratori che aprono il fuoco nello stesso istante: una sola salva puo'
        costare >= 2 mezzi su 10. Domanda: esiste almeno una replica in cui scatta lo SHOCK
        da solo, con l'erosione finale ancora sotto 0.30 (le due soglie sono davvero
        indipendenti).
      * CONTROLLO (HELD) — 1 tiratore con 2 soli colpi (munizioni impostate sull'asset):
        al massimo 2 perdite su 10, sotto entrambe le soglie. Domanda: nessun
        disingaggio, esito HELD.
      * AD OLTRANZA — come EROSIONE ma con Red a soglie 1.0: la stessa pressione NON si
        ferma alla soglia. E' il controllo di non vacuita': e' la soglia, non la
        composizione, a fermare il combattimento nel caso EROSIONE. Domanda: nessun
        disingaggio, perdite ben oltre la soglia di erosione e oltre quelle del caso
        EROSIONE sullo stesso seed. NON si chiede l'annientamento (DESTROYED): le forze
        sono ferme, quindi c'e' una sola finestra di contatto per coppia e una sola
        estrazione di rilevamento (Pd ~0.8 a 3 km su 4 km di portata); un BMP-2 non
        rilevato non e' mai ingaggiato e l'esito osservato e' HELD con perdite = mezzi
        rilevati (7-9 su 10). E' il comportamento dichiarato del risolutore (§1 del suo
        docstring), non un limite della dottrina.

    Nota sul docstring di P3 ("la forza superstite rientra nello scheduler dei contatti su
    una nuova rotta"): il ri-instradamento dopo un disingaggio NON e' implementato (R4,
    seconda parte, rimandato al livello C2/campagna); qui si verifica solo la segnalazione
    DISENGAGED nell'esito, che e' cio' che il motore fa.
    """

    SEEDS = _seeds('S10', 6)
    RED_SIZE = 10

    @classmethod
    def _build(cls, shooters=1, ammunition=None):
        blue = F.build_force('Blue-Gun', 'Blue', [F.Unit('vehicle', 'M1A2-Abrams', shooters, origin=(0.0, -3_000.0),
                                                         step=(150.0, 0.0), prefix='mbt', sensors=VISUAL)])
        red = F.build_force('Red-Column', 'Red', [F.Unit('vehicle', 'BMP-2', cls.RED_SIZE, origin=(-900.0, 0.0),
                                                         step=(200.0, 0.0), prefix='ifv', sensors=VISUAL)])

        if ammunition is not None:
            for asset in blue.assets.values():
                asset.ammunition = ammunition

        fire = F.make_fire_control({}, overrides={a: {'ground': F.SHOTS['direct_fire']} for a in blue.assets})
        return blue, red, fire

    @classmethod
    def _run(cls, session_id, *, shooters=1, ammunition=None, thresholds=None):
        blue, red, fire = cls._build(shooters, ammunition)
        return blue, red, F.run(session_id, [blue], [red], fire, duration=3_600.0, thresholds=thresholds)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.erosion = [cls._run(s) for s in cls.SEEDS]
        cls.shock = [cls._run(s, shooters=4) for s in cls.SEEDS]
        cls.control = [cls._run(s, ammunition=2) for s in cls.SEEDS]
        cls.press_on = [cls._run(s, thresholds=RED_HOLDS) for s in cls.SEEDS]

    def test_erosion_threshold_gives_disengaged_not_annihilation(self):
        erosion = Doctrine.DEFAULT_DISENGAGEMENT_THRESHOLDS['Red'][Doctrine.DISENGAGEMENT_EROSION]

        for _, _, outcome in self.erosion:
            red = F.force_outcome(outcome, 'Red-Column')
            self.assertEqual(red.outcome, ER.DISENGAGED)
            self.assertEqual(red.triggers, (ER.TRIGGER_EROSION,))
            self.assertLess(red.lost, red.committed)
            self.assertGreaterEqual(red.erosion, erosion)

    def test_erosion_triggers_mid_engagement(self):
        """Prima della rottura ci sono gia' state salve andate a segno (o a vuoto) che NON
        l'hanno fatta scattare: la soglia scatta dentro un ingaggio in corso."""
        for _, red, outcome in self.erosion:
            result = F.force_outcome(outcome, 'Red-Column')
            before = [e for e in F.damage_on(outcome, red.assets) if e.time < result.time - CS.TIME_EPS]
            self.assertGreater(len(before), 0)

    def test_no_fire_against_a_disengaged_force(self):
        for blue, _, outcome in self.erosion + self.shock:
            result = F.force_outcome(outcome, 'Red-Column')
            late = [e for e in _salvos_by(outcome, blue.assets) if e.time > result.time + CS.TIME_EPS]
            self.assertEqual(late, [])

    def test_shock_threshold_can_trigger_alone(self):
        erosion = Doctrine.DEFAULT_DISENGAGEMENT_THRESHOLDS['Red'][Doctrine.DISENGAGEMENT_EROSION]
        shock_only = []

        for _, _, outcome in self.shock:
            red = F.force_outcome(outcome, 'Red-Column')
            self.assertEqual(red.outcome, ER.DISENGAGED)
            self.assertIn(ER.TRIGGER_SHOCK, red.triggers)

            if red.triggers == (ER.TRIGGER_SHOCK,):
                shock_only.append(red)
                self.assertLess(red.erosion, erosion)

        self.assertGreater(len(shock_only), 0)

    def test_losses_below_threshold_hold(self):
        for blue, _, outcome in self.control:
            red = F.force_outcome(outcome, 'Red-Column')
            self.assertEqual(red.outcome, ER.HELD)
            self.assertIsNone(red.time)
            self.assertLessEqual(len(_salvos_by(outcome, blue.assets)), 2)

    def test_without_threshold_the_same_pressure_goes_beyond_it(self):
        """Ad oltranza: nessuna rottura, perdite oltre la soglia e oltre il caso EROSIONE.

        Non si chiede DESTROYED: v. docstring della classe (bersagli mai rilevati)."""
        erosion = Doctrine.DEFAULT_DISENGAGEMENT_THRESHOLDS['Red'][Doctrine.DISENGAGEMENT_EROSION]

        for (_, _, stopped), (_, _, outcome) in zip(self.erosion, self.press_on):
            red = F.force_outcome(outcome, 'Red-Column')
            self.assertIn(red.outcome, (ER.HELD, ER.DESTROYED))
            self.assertNotIn(ER.TRIGGER_EROSION, red.triggers)
            self.assertNotIn(ER.TRIGGER_SHOCK, red.triggers)
            self.assertGreater(red.erosion, erosion)
            self.assertGreater(red.lost, F.force_outcome(stopped, 'Red-Column').lost)


# ── S11 — CONFINE SESSIONE "SINTETICA" / SESSIONE "DCS" ───────────────────────

class TestS11SessionBoundary(F.LoggerSilencer, unittest.TestCase):
    """S11: il confine fra due sessioni consecutive non perde stato.

    **Non e' un test di combattimento**: e' il test end-to-end del contratto
    `SessionOrder`/`SessionOutcome`. Una prima sessione ("sintetica") risolve un ingaggio;
    una SECONDA `SessionOrder`, costruita da zero, fa girare la sessione successiva
    ("DCS") sulle STESSE istanze di forza, con lo stato reale gia' mutato dalla prima.

    La distinzione DCS/sintetica e' **puramente concettuale a questo livello**: il core
    Python non sa e non deve sapere quale simulatore esegue una sessione (wiki
    `decisions/core-simulator-agnostic`: "cancellando l'adapter DCS la campagna deve
    continuare a funzionare"; nessun adapter DCS esiste oggi in `Source/`, v.
    Test_Session_Validation). Le due sessioni sono quindi due chiamate identiche nella
    forma a `run_session`; il test verifica anche che `SessionOrder` non abbia alcun campo
    che dica "che tipo di sessione" sia. Quando l'adapter DCS esistera', la seconda
    sessione sara' eseguita da lui e dovra' leggere lo stesso stato e produrre un
    `SessionOutcome` della stessa forma.

    Composizione (realistica, non minimale): Blue-Mech 3 M1A2 + 3 M2 Bradley in avanzata,
    Blue-CAS 2 A-10C ('Maverick/Gun CAS', ruolo strike); Red-Battalion 3 T-72B + 3 BMP-2 +
    1 2S19-Msta + 1 ZSU-23-4 + 1 9K35 Strela-10, in difesa; Red-CAP 2 MiG-29S ('CAP') in
    pattugliamento. Entrambe le sessioni hanno rotte (quindi consumo di carburante).

    Domanda: "il confine fra sessioni non perde stato". Verifiche:
      * dopo la sessione 1 lo stato reale (salute, munizioni, carburante, intercettori) e'
        esattamente quello iniziale piu' gli eventi dell'esito 1 (l'esito e' il resoconto
        completo); munizioni e intercettori sono contatori distinti (ricalibrazione
        2026-09-23): le salve consumano i primi, le intercettazioni i secondi;
      * nella sessione 2 ogni primo DamageEvent parte dalla salute lasciata dalla
        sessione 1, ogni primo FuelEvent dal carburante lasciato dalla sessione 1;
      * gli asset fuori combattimento dopo la sessione 1 non combattono nella 2 (non
        sparano e non sono contati fra gli impegnati di ForceOutcome.committed);
      * le munizioni e gli intercettori consumati nella 2 partono dalle scorte residue della 1;
      * gli intervalli delle due sessioni sono contigui.

    **Limite noto, non verificato qui** (v. Test_Session_Validation e il docstring di
    `run_session`): `asset.position` NON e' aggiornata a fine rotta, quindi la sessione 2
    riparte dalle posizioni iniziali. La posizione e' fra i campi che P3 cita per S11:
    resta lavoro futuro dell'orchestratore/C2.
    """

    SEEDS = ('S11-a', 'S11-b', 'S11-c')
    DURATION = 3_600.0

    @staticmethod
    def _build():
        blue = F.build_force('Blue-Mech', 'Blue', [
            F.Unit('vehicle', 'M1A2-Abrams', 3, origin=(-8_000.0, 0.0), step=(0.0, 300.0), prefix='mbt',
                   sensors=VISUAL),
            F.Unit('vehicle', 'M2-Bradley', 3, origin=(-8_300.0, 150.0), step=(0.0, 300.0), prefix='ifv',
                   sensors=VISUAL)])
        cas = F.build_force('Blue-CAS', 'Blue', [F.Unit('aircraft', 'A-10C Thunderbolt II', 2,
                                                        origin=(-60_000.0, 0.0, 3_000.0), step=(0.0, 500.0),
                                                        prefix='cas', loadout='Maverick/Gun CAS')],
                            mil_category=F.AIR_UNIT)
        red = F.build_force('Red-Battalion', 'Red', [
            F.Unit('vehicle', 'T-72B', 3, origin=(0.0, 0.0), step=(0.0, 300.0), prefix='mbt', sensors=VISUAL),
            F.Unit('vehicle', 'BMP-2', 3, origin=(300.0, 150.0), step=(0.0, 300.0), prefix='ifv', sensors=VISUAL),
            F.Unit('vehicle', '2S19-Msta', 1, origin=(6_000.0, 300.0), prefix='art',
                   sensors={'ground': F.DECLARED_ARTILLERY_OBSERVATION_RANGE}),
            F.Unit('vehicle', 'ZSU-23-4-Shilka', 1, origin=(1_000.0, 600.0), prefix='aaa'),
            F.Unit('vehicle', '9K35-Strela-10', 1, origin=(1_000.0, -300.0), prefix='sam')],
            mil_category=GROUND_BASE[3])   # 'Battallion'
        cap = F.build_force('Red-CAP', 'Red', [F.Unit('aircraft', 'MiG-29S', 2, origin=(40_000.0, 0.0, 6_000.0),
                                                      step=(0.0, 1_000.0), prefix='cap', loadout='CAP')],
                            mil_category=F.AIR_UNIT)
        roles = _strike_roles(cas)
        return [blue, cas], [red, cap], F.make_fire_control(roles=roles)

    @staticmethod
    def _routes(forces_a, forces_b):
        blue, cas = forces_a
        _, cap = forces_b
        routes = F.routes_for(blue, [(2_000.0, 0.0)])
        routes.update(F.routes_for(cas, [(10_000.0, 0.0)]))
        routes.update(F.routes_for(cap, [(-30_000.0, 0.0)]))
        return routes

    @staticmethod
    def _snapshot(forces):
        # Indici: 0 salute, 1 munizioni, 2 carburante, 3 intercettori, 4 SAM puro (pool
        # unico munizioni/intercettori, Mobile.interceptor_shares_ammunition).
        return {asset_id: (asset.health, asset.ammunition, asset.fuel,
                           getattr(asset, 'interceptor_stock', None),
                           bool(getattr(asset, 'interceptor_shares_ammunition', False)))
                for force in forces for asset_id, asset in force.assets.items()}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = []

        for seed in cls.SEEDS:
            forces_a, forces_b, fire = cls._build()
            forces = forces_a + forces_b
            initial = cls._snapshot(forces)

            # Sessione 1, "sintetica".
            order_1 = SessionOrder(f'{seed}-synthetic', t_start=0.0, t_end=cls.DURATION,
                                   force_ids=tuple(sorted(f.id for f in forces)))
            outcome_1 = SS.run_session(order_1, forces_a, forces_b, fire, routes=cls._routes(forces_a, forces_b))
            after_1 = cls._snapshot(forces)
            operative_after_1 = {a for f in forces for a, asset in f.assets.items() if asset.is_operative()}

            # Sessione 2, "DCS": un SessionOrder nuovo, stesse istanze, stato gia' mutato.
            order_2 = SessionOrder(f'{seed}-dcs', t_start=outcome_1.t_end, t_end=outcome_1.t_end + cls.DURATION,
                                   force_ids=tuple(sorted(f.id for f in forces)))
            outcome_2 = SS.run_session(order_2, forces_a, forces_b, fire, routes=cls._routes(forces_a, forces_b))
            after_2 = cls._snapshot(forces)

            cls.runs.append({'forces': forces, 'initial': initial, 'after_1': after_1, 'after_2': after_2,
                             'operative_after_1': operative_after_1, 'outcome_1': outcome_1,
                             'outcome_2': outcome_2, 'order_2': order_2})

    # ── premesse ──

    def test_first_session_leaves_state_to_carry(self):
        """Premessa non vacua: la sessione 1 lascia danni, consumi di munizioni e carburante."""
        for run in self.runs:
            outcome = run['outcome_1']
            self.assertGreater(len(outcome.damage_events), 0)
            self.assertGreater(len(outcome.ammunition_events), 0)
            self.assertGreater(len(outcome.fuel_events), 0)

        self.assertTrue(any(len(run['operative_after_1']) < len(run['initial']) for run in self.runs))

    def test_session_order_does_not_know_the_simulator(self):
        """Nessun campo di SessionOrder dice se la sessione e' DCS o sintetica."""
        import dataclasses
        names = {field.name.lower() for field in dataclasses.fields(SessionOrder)}
        for word in ('dcs', 'simulator', 'synthetic', 'kind', 'mode', 'source'):
            self.assertFalse(any(word in name for name in names), word)

    # ── stato alla fine della sessione 1 = iniziale + esito 1 ──

    def test_state_after_first_session_is_initial_plus_outcome(self):
        for run in self.runs:
            outcome = run['outcome_1']
            final_health = {}
            for event in outcome.damage_events:
                final_health[event.target_id] = event.health_after
            ammo = outcome.ammunition_consumed()
            intercepts = outcome.interceptions_consumed()
            fuel = outcome.fuel_consumed()

            for asset_id, (health, stock, level, interceptors, shares) in run['initial'].items():
                with self.subTest(asset=asset_id):
                    after = run['after_1'][asset_id]
                    self.assertEqual(after[0], final_health.get(asset_id, health))
                    if shares:
                        # SAM puro: salve e intercettazioni scalano lo stesso pool di missili.
                        if stock is not None:
                            spent = ammo.get(asset_id, 0) + intercepts.get(asset_id, 0)
                            self.assertEqual(after[1], max(stock - spent, 0))
                        self.assertEqual(after[3], after[1])
                    else:
                        if stock is not None:
                            self.assertEqual(after[1], max(stock - ammo.get(asset_id, 0), 0))
                        if interceptors is not None:
                            self.assertEqual(after[3], max(interceptors - intercepts.get(asset_id, 0), 0))
                    if level is not None:
                        self.assertAlmostEqual(after[2], level - fuel.get(asset_id, 0.0), places=9)

    # ── la sessione 2 parte dallo stato lasciato dalla 1 ──

    def test_second_session_is_contiguous(self):
        for run in self.runs:
            self.assertGreaterEqual(run['outcome_2'].t_start, run['outcome_1'].t_end - CS.TIME_EPS)
            self.assertEqual(run['order_2'].t_start, run['outcome_1'].t_end)

    def test_damage_in_second_session_starts_from_carried_health(self):
        checked = 0

        for run in self.runs:
            seen = set()
            for event in run['outcome_2'].damage_events:
                if event.target_id not in seen:
                    seen.add(event.target_id)
                    self.assertEqual(event.health_before, run['after_1'][event.target_id][0], event.target_id)
                    checked += 1

        self.assertGreater(checked, 0)

    def test_fuel_in_second_session_starts_from_carried_fuel(self):
        checked = 0

        for run in self.runs:
            for event in run['outcome_2'].fuel_events:
                self.assertAlmostEqual(event.fuel_before, run['after_1'][event.asset_id][2], places=9)
                checked += 1

        self.assertGreater(checked, 0)

    def test_ammunition_in_second_session_draws_on_the_residual_stock(self):
        for run in self.runs:
            fired = run['outcome_2'].ammunition_consumed()
            intercepts = run['outcome_2'].interceptions_consumed()

            for asset_id in set(fired) | set(intercepts):
                shares = run['initial'][asset_id][4]
                # Salve -> ammunition (indice 1), intercettazioni -> interceptor_stock (3):
                # ciascuna scorta risponde solo del proprio consumo; per un SAM puro il pool
                # e' unico (indice 1) e risponde di entrambi.
                if shares:
                    draws = ((1, fired.get(asset_id, 0) + intercepts.get(asset_id, 0)),)
                else:
                    draws = ((1, fired.get(asset_id, 0)), (3, intercepts.get(asset_id, 0)))

                for index, rounds in draws:
                    residual = run['after_1'][asset_id][index]
                    with self.subTest(asset=asset_id, index=index):
                        if residual is not None:
                            self.assertLessEqual(rounds, residual)
                            self.assertEqual(run['after_2'][asset_id][index], residual - rounds)

    def test_interceptions_never_draw_on_the_offensive_ammunition(self):
        """Asset NON SAM puri che hanno solo intercettato nella sessione 1: munizioni invariate."""
        checked = 0

        for run in self.runs:
            fired = run['outcome_1'].ammunition_consumed()
            intercepts = run['outcome_1'].interceptions_consumed()

            for asset_id in set(intercepts) - set(fired):
                if run['initial'][asset_id][4]:
                    continue
                with self.subTest(asset=asset_id):
                    self.assertEqual(run['after_1'][asset_id][1], run['initial'][asset_id][1])
                    checked += 1

        if checked == 0:
            self.skipTest('no non-pure-SAM asset intercepted without also firing in these seeds')

    def test_pure_sam_interceptions_draw_on_its_missiles(self):
        """SAM puro (qui il 9K35-Strela-10): ogni intercettazione e' un missile in meno per
        sparare, e la sua scorta di intercettori resta sempre uguale alle munizioni."""
        checked = 0

        for run in self.runs:
            fired = run['outcome_1'].ammunition_consumed()
            intercepts = run['outcome_1'].interceptions_consumed()

            for asset_id, (_, stock, _, _, shares) in run['initial'].items():
                if not shares or stock is None:
                    continue
                with self.subTest(asset=asset_id):
                    after = run['after_1'][asset_id]
                    self.assertEqual(after[3], after[1])
                    spent = fired.get(asset_id, 0) + intercepts.get(asset_id, 0)
                    self.assertEqual(after[1], stock - spent)
                    if intercepts.get(asset_id, 0) > 0:
                        checked += 1

        if checked == 0:
            self.skipTest('no pure SAM intercepted in these seeds')

    def test_assets_out_of_action_after_first_session_do_not_fight_in_the_second(self):
        for run in self.runs:
            out = set(run['initial']) - run['operative_after_1']
            # Ne' salve ne' intercettazioni (tipi distinti dal 2026-09-23).
            self.assertEqual(F.active_assets(run['outcome_2']) & out, set())

    def test_committed_in_second_session_counts_only_survivors(self):
        for run in self.runs:
            for result in run['outcome_2'].force_outcomes:
                force = next(f for f in run['forces'] if f.id == result.force_id)
                survivors = sum(1 for a in force.assets if a in run['operative_after_1'])
                self.assertEqual(result.committed, survivors, result.force_id)


# ── S12 — DECAPITAZIONE DI UN NODO C2 ─────────────────────────────────────────

class TestS12C2Decapitation(F.LoggerSilencer, unittest.TestCase):
    """S12: colpo mirato contro un nodo C2 isolato con presidio minimo.

    Composizione: Red-C2 = `Military` con mil_category 'Command_&_Control_C2' — 1 bunker
    comando (`Structure`, tabella 'Stronghold'/'Command_&_Control': v. nota) + 1 BTR-80
    (veicolo comando) + presidio 1 ZSU-23-4 (AAA) + 1 9K35 Strela-10 (SHORAD); Blue-Strike
    2 F-15E ('Laser Strike', ruolo strike: solo bersagli non-AD) + Blue-SEAD 2 F-16C
    ('SEAD', ruolo sead) come scorta di soppressione; Red-Far = un battaglione a 250 km,
    fuori da ogni portata (controllo dell'isolamento).

    Nota sulla tabella: `BLOCK_INFRASTRUCTURE_ASSET['Military']` non ha una sotto-tabella
    per 'Command_&_Control_C2'/'C4' (solo Stronghold/Farp/Airbase/Helibase/Port/Shipyard/
    Air_Defense): il bunker usa la voce 'Command_&_Control' della tabella 'Stronghold', la
    piu' vicina. Lacuna del Context segnalata nel report.

    Armi: lo strike sgancia le GBU-12 del suo loadout (`STRIKE_BOMB_TABLE`, non
    intercettabili); la SEAD resta con gli 'arm' di riferimento (intercettabili). Nella
    prima stesura, con la scorta di intercettazione presa da `ammunition`, gli 'agm' della
    tabella di riferimento erano tutti intercettati e il bunker non veniva MAI colpito;
    con la scorta di intercettori distinta (ZSU 20 + Strela-10 8) la difesa si esaurisce,
    v. "Intercettazione" nel docstring del modulo.

    Domanda: un bersaglio singolo, isolato, ad alto valore riceve danno e l'ingaggio si
    chiude rapidamente — un colpo mirato, non uno scambio prolungato. Verifiche: un solo
    ingaggio, fra le sole forze coinvolte; il bunker e' colpito (aggregato); pochi
    DamageEvent per replica (limite largo MAX_DAMAGE_EVENTS); durata dell'attivita' di
    fuoco breve rispetto alla sessione (MAX_FIRE_SPAN) e, seed per seed, piu' breve di uno
    scambio davvero prolungato: la composizione di S1 con ENTRAMBI i lati ad oltranza
    (`BOTH_HOLD`). Con la dottrina di default S1 non e' prolungato — Red-Line rompe il
    contatto dopo ~2 perdite in 160-190 s — e non puo' fare da riferimento.
    """

    SEEDS = _seeds('S12', 6)
    MAX_DAMAGE_EVENTS = 15        # limite largo, "pochi, non decine"
    MAX_FIRE_SPAN = 900.0         # [s] su una sessione di 3600 s

    @staticmethod
    def _build():
        c2 = F.make_force('Red-C2', 'Red', GROUND_BASE[7])   # 'Command_&_Control_C2'
        bunker = F.make_structure(c2, 'Red-C2/bunker', (0.0, 0.0), category='Stronghold',
                                  asset_type='Command_&_Control')
        F.add_assets(c2, [bunker,
                          F.make_vehicle(c2, 'Red-C2/cmd0', 'BTR-80', (150.0, 0.0)),
                          F.make_vehicle(c2, 'Red-C2/aaa0', 'ZSU-23-4-Shilka', (400.0, 300.0)),
                          F.make_vehicle(c2, 'Red-C2/sam0', '9K35-Strela-10', (-400.0, -300.0))])
        far = F.build_force('Red-Far', 'Red', [F.Unit('vehicle', 'BMP-2', 4, origin=(0.0, 250_000.0), prefix='ifv',
                                                      sensors=VISUAL)], mil_category=GROUND_BASE[3])
        strike = F.build_force('Blue-Strike', 'Blue', [F.Unit('aircraft', 'F-15E Strike Eagle', 2,
                                                              origin=(-150_000.0, 0.0, 6_000.0), step=(0.0, 500.0),
                                                              prefix='str', loadout='Laser Strike')],
                               mil_category=F.AIR_UNIT)
        sead = F.build_force('Blue-SEAD', 'Blue', [F.Unit('aircraft', 'F-16C Block 52d', 2,
                                                          origin=(-148_000.0, 2_000.0, 6_000.0), step=(0.0, 500.0),
                                                          prefix='sead', loadout='SEAD')],
                             mil_category=F.AIR_UNIT)
        roles = dict(_strike_roles(strike), **_strike_roles(sead, 'sead'))
        routes = F.routes_for(strike, [(20_000.0, 0.0)])
        routes.update(F.routes_for(sead, [(20_000.0, 2_000.0)]))
        return [strike, sead], [c2, far], routes, F.make_fire_control(STRIKE_BOMB_TABLE, roles=roles)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = []
        cls.prolonged = []

        for session_id in cls.SEEDS:
            blue, red, routes, fire = cls._build()
            cls.runs.append((blue, red, F.run(session_id, blue, red, fire, duration=3_600.0, routes=routes)))
            cls.prolonged.append(F.combined_arms_scenario().run(session_id, thresholds=BOTH_HOLD))

    @staticmethod
    def _fire_span(outcome):
        times = [e.time for e in outcome.damage_events + outcome.ammunition_events]
        return max(times) - min(times)

    def test_one_engagement_the_distant_force_stays_out(self):
        for _, _, outcome in self.runs:
            self.assertEqual(_engagement_ids(outcome), [('Blue-SEAD', 'Blue-Strike', 'Red-C2')])
            self.assertEqual(F.force_outcome(outcome, 'Red-Far'), None)

    def test_the_command_bunker_is_hit(self):
        hits = sum(len(F.damage_on(o, ['Red-C2/bunker'])) for _, _, o in self.runs)
        self.assertGreater(hits, 0)

    def test_only_a_few_damage_events(self):
        for _, _, outcome in self.runs:
            self.assertGreater(len(outcome.damage_events), 0)
            self.assertLessEqual(len(outcome.damage_events), self.MAX_DAMAGE_EVENTS)

    def test_fire_is_concentrated_in_time(self):
        for _, _, outcome in self.runs:
            self.assertLess(self._fire_span(outcome), self.MAX_FIRE_SPAN)

    def test_a_targeted_strike_is_shorter_than_a_prolonged_exchange(self):
        """Stessi seed: la durata del fuoco del colpo mirato e' minore di quella dello
        scambio prolungato (e, in aggregato, anche il numero di DamageEvent)."""
        for (_, _, strike), prolonged in zip(self.runs, self.prolonged):
            self.assertLess(self._fire_span(strike), self._fire_span(prolonged))

        self.assertLess(sum(len(o.damage_events) for _, _, o in self.runs),
                        sum(len(o.damage_events) for o in self.prolonged))


# ── S13 — INTERDIZIONE DI UN FARP AVANZATO ────────────────────────────────────

class TestS13ForwardFARPInterdiction(F.LoggerSilencer, unittest.TestCase):
    """S13: missione aerea contro un FARP, cioe' un Block dalla composizione eterogenea.

    Composizione: Red-FARP = `Military` 'Farp' con asset di tre classi e cinque ruoli:
      * 2 piazzole elicottero con elicottero parcheggiato + 1 serbatoio carburante
        (`Structure`, tabella 'Farp': 'Parked_Helicopter', 'Oil_Tank') — nei registri non
        esiste alcun modello di elicottero (Aircraft_Data), quindi gli elicotteri a terra
        sono rappresentati come strutture parcheggiate, come fa la tabella del Context;
      * 1 MT-LB di supporto (ruolo 'ground', nessuna arma contro aerei);
      * 1 ZSU-23-4 (AAA) + 1 9K35 Strela-10 (SAM).
    Blue-Strike 4 F-16C ('Strike', ruolo strike: bombardano le strutture e il mezzo di
    supporto, non la difesa) con le Mk-82/Mk-83 del loadout (`STRIKE_BOMB_TABLE`, non
    intercettabili). Red a soglie 1.0 (`RED_HOLDS`: un FARP non ripiega, v. docstring del
    modulo).

    Perche' non multiruolo con gli 'agm' di riferimento (prima stesura): con la scorta di
    intercettazione presa da `ammunition` tutti gli 'agm' (80-88 per replica) erano
    intercettati da ZSU+Strela e nessun asset del FARP riceveva danno — problema risolto
    dalla scorta di intercettori distinta (v. "Intercettazione" nel docstring del modulo:
    ora ZSU+Strela ne fermano 28, il resto arriva a segno), ma le bombe restano l'arma
    fedele al loadout 'Strike'; e con le bombe su TUTTO il
    blocco, sganciate alla portata dei sensori (95 km, il fire_control di test non ha
    inviluppo d'arma), la difesa era distrutta prima di vedere gli aerei e non sparava mai.
    Col ruolo strike la difesa sopravvive, vede l'incursione al passaggio e spara.

    Domanda: il motore gestisce un Block con asset di tipi e ruoli diversi senza assumere
    che abbiano lo stesso ruolo. Verifiche: solo AAA/SAM sparano e solo loro sono
    intercettori (`Military.salvo_interceptors`); strutture e MT-LB non sparano mai; i
    danni cadono su piu' classi di asset (Structure e Vehicle) dello stesso Block; tutti
    gli asset (strutture comprese) sono contati fra gli impegnati.
    """

    SEEDS = _seeds('S13', 6)

    @staticmethod
    def _build():
        farp = F.make_force('Red-FARP', 'Red', GROUND_BASE[1])   # 'Farp'
        F.add_assets(farp, [
            F.make_structure(farp, 'Red-FARP/pad0', (0.0, 0.0), category='Farp', asset_type='Parked_Helicopter'),
            F.make_structure(farp, 'Red-FARP/pad1', (150.0, 0.0), category='Farp', asset_type='Parked_Helicopter'),
            F.make_structure(farp, 'Red-FARP/fuel0', (0.0, 200.0), category='Farp', asset_type='Oil_Tank'),
            F.make_vehicle(farp, 'Red-FARP/sup0', 'MT-LB', (100.0, 250.0)),
            F.make_vehicle(farp, 'Red-FARP/aaa0', 'ZSU-23-4-Shilka', (500.0, 300.0)),
            F.make_vehicle(farp, 'Red-FARP/sam0', '9K35-Strela-10', (-500.0, -300.0))])
        strike = F.build_force('Blue-Strike', 'Blue', [F.Unit('aircraft', 'F-16C Block 52d', 4,
                                                              origin=(-150_000.0, 0.0), step=(0.0, 500.0),
                                                              prefix='str', loadout='Strike')],
                               mil_category=F.AIR_UNIT)
        return strike, farp, F.routes_for(strike, [(20_000.0, 0.0)])

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        strike, farp, _ = cls._build()
        cls.interceptors = sorted(asset.id for asset, _ in farp.salvo_interceptors())
        cls.types = _type_of([strike, farp])
        cls.roles = {a: F.role_of(asset) for a, asset in farp.assets.items()}
        cls.runs = []

        for session_id in cls.SEEDS:
            strike, farp, routes = cls._build()
            fire = F.make_fire_control(STRIKE_BOMB_TABLE, roles=_strike_roles(strike))
            outcome = F.run(session_id, [strike], [farp], fire, duration=3_600.0, routes=routes,
                            thresholds=RED_HOLDS)
            cls.runs.append((farp, outcome))

    def test_the_block_is_really_heterogeneous(self):
        self.assertEqual(set(self.roles.values()), {'structure', 'ground', 'aaa', 'sam'})
        self.assertEqual({self.types[a] for a in self.roles}, {'Structure', 'Vehicle'})

    def test_only_air_defence_assets_are_interceptors(self):
        self.assertEqual(self.interceptors, ['Red-FARP/aaa0', 'Red-FARP/sam0'])

    def test_real_constructors_load_a_distinct_interceptor_stock(self):
        """Vehicle.__init__ carica interceptor_stock dal registro: per lo Shilka (solo
        cannone AA) un contatore distinto, molto minore dei colpi; per lo Strela-10 (SAM
        puro, solo missili 9M37) lo stesso pool delle munizioni (decisione 2026-09-23);
        nessuna scorta per chi non ha armi AD."""
        _, farp, _ = self._build()
        aaa, sam, support = (farp.assets[a] for a in ('Red-FARP/aaa0', 'Red-FARP/sam0', 'Red-FARP/sup0'))

        for asset in (aaa, sam):
            self.assertEqual(asset.interceptor_stock, asset.interceptor_stock_from_registry())
            self.assertGreater(asset.interceptor_stock, 0)
        self.assertLess(aaa.interceptor_stock * 10, aaa.ammunition)
        self.assertIsNone(support.interceptor_stock)
        self.assertFalse(aaa.interceptor_shares_ammunition)
        self.assertTrue(sam.interceptor_shares_ammunition)
        self.assertEqual(sam.interceptor_stock, sam.ammunition)
        sam.consume_ammunition(1)
        self.assertEqual(sam.interceptor_stock, sam.ammunition)

    def test_only_air_defence_assets_shoot(self):
        """Ne' salve ne' intercettazioni da asset senza armi AD."""
        shooters = set()

        for farp, outcome in self.runs:
            shooters |= {a for a in F.active_assets(outcome) if a in farp.assets}

        self.assertTrue(shooters)
        self.assertLessEqual(shooters, {'Red-FARP/aaa0', 'Red-FARP/sam0'})

    def test_damage_falls_on_several_asset_classes_of_the_same_block(self):
        classes = Counter()

        for farp, outcome in self.runs:
            for event in F.damage_on(outcome, farp.assets):
                classes[self.types[event.target_id]] += 1

        self.assertGreater(classes['Structure'], 0)
        self.assertGreater(classes['Vehicle'], 0)

    def test_every_asset_is_committed(self):
        for farp, outcome in self.runs:
            self.assertEqual(F.force_outcome(outcome, 'Red-FARP').committed, len(farp.assets))


# ── S14 — BOMBARDAMENTO STRATEGICO DI UN IMPIANTO PRODUCTION ──────────────────

class TestS14StrategicBombingOfProduction(F.LoggerSilencer, unittest.TestCase):
    """S14: bombardamento di una centrale elettrica (`Production` reale, non `Military`).

    Composizione: Red-Plant = `Production` sub_category 'Power_Plant' (categoria di blocco
    'Logistic') con 1 sala macchine ('Power_Plant'), 2 serbatoi ('Oil_Tank'), 1 sottostazione
    ('Electric_Infrastructure') — `Structure` reali — e difesa organica di 2 ZSU-23-4.
    Blue-Bombers 4 F-15E ('Iron Bomb Strike', ruolo strike).

    Il `fire_control` di riferimento classifica come 'logistic' (bersaglio, mai tiratore)
    ogni asset NON di difesa aerea di un blocco logistico; la difesa organica resta 'aaa'
    sia come tiratore sia come bersaglio (`Scenario_Fixtures.role_of`). Nella prima stesura
    restava 'logistic' come bersaglio: i bombardieri 'strike' (per definizione non-AD) la
    distruggevano da 100 km, prima che potesse vederli (~6 km), e non sparava mai.

    Domanda (come S7, ma con un `Production` vero invece del `Block` di ripiego): il motore
    tratta correttamente un bersaglio economico fisso senza combat power proprio.
    Verifiche: il blocco non e' una Military (niente combat_power ne' salvo_interceptors);
    le strutture ricevono danno applicato agli asset reali; la difesa organica spara ma non
    intercetta (l'intercettazione e' solo delle Military); **l'impianto non si disingaggia
    mai** anche quando le perdite superano le soglie della dottrina di default
    (`Engagement_Resolver._can_disengage`): esito HELD o DESTROYED.
    """

    SEEDS = _seeds('S14', 6)
    STRUCTURES = ('Red-Plant/hall0', 'Red-Plant/tank0', 'Red-Plant/tank1', 'Red-Plant/sub0')
    AAA = ('Red-Plant/aaa0', 'Red-Plant/aaa1')

    @classmethod
    def _build(cls):
        plant = F.make_infrastructure('Production', 'Red-Plant', 'Red', 'Power_Plant')
        F.add_assets(plant, [
            F.make_structure(plant, 'Red-Plant/hall0', (0.0, 0.0), category='Power_Plant', asset_type='Power_Plant'),
            F.make_structure(plant, 'Red-Plant/tank0', (250.0, 100.0), category='Power_Plant', asset_type='Oil_Tank'),
            F.make_structure(plant, 'Red-Plant/tank1', (250.0, -100.0), category='Power_Plant', asset_type='Oil_Tank'),
            F.make_structure(plant, 'Red-Plant/sub0', (-200.0, 0.0), category='Power_Plant',
                             asset_type='Electric_Infrastructure'),
            F.make_vehicle(plant, 'Red-Plant/aaa0', 'ZSU-23-4-Shilka', (600.0, 400.0)),
            F.make_vehicle(plant, 'Red-Plant/aaa1', 'ZSU-23-4-Shilka', (-600.0, -400.0))])
        bombers = F.build_force('Blue-Bombers', 'Blue', [F.Unit('aircraft', 'F-15E Strike Eagle', 4,
                                                                origin=(-200_000.0, 0.0, 6_000.0), step=(0.0, 500.0),
                                                                prefix='bmb', loadout='Iron Bomb Strike')],
                                mil_category=F.AIR_UNIT)
        return bombers, plant, F.routes_for(bombers, [(20_000.0, 0.0)]), \
            F.make_fire_control(roles=_strike_roles(bombers))

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = []

        for session_id in cls.SEEDS:
            bombers, plant, routes, fire = cls._build()
            cls.runs.append((bombers, plant, F.run(session_id, [bombers], [plant], fire, duration=3_600.0,
                                                   routes=routes)))

    def test_target_is_a_real_production_block_not_military(self):
        _, plant, _ = self.runs[0]
        self.assertIsInstance(plant, Production)
        self.assertNotIsInstance(plant, Military)
        self.assertEqual(plant.sub_category, 'Power_Plant')
        self.assertFalse(hasattr(plant, 'salvo_interceptors'))
        self.assertFalse(hasattr(plant, 'combat_power'))

    def test_structures_take_damage_applied_to_the_real_assets(self):
        hits = 0

        for _, plant, outcome in self.runs:
            final = {}
            for event in outcome.damage_events:
                final[event.target_id] = event.health_after
            for asset_id, asset in plant.assets.items():
                self.assertEqual(asset.health, final.get(asset_id, 100), asset_id)
            hits += len(F.damage_on(outcome, self.STRUCTURES))

        self.assertGreater(hits, 0)

    def test_organic_defence_fires_but_never_intercepts(self):
        salvos = 0

        for _, plant, outcome in self.runs:
            own = [e for e in outcome.ammunition_events if e.asset_id in plant.assets]
            self.assertEqual(F.interceptions_by(outcome, plant.assets), [])
            self.assertTrue(all(e.asset_id in self.AAA for e in own))
            salvos += len(own)

        self.assertGreater(salvos, 0)

    def test_the_plant_never_disengages(self):
        erosion = Doctrine.DEFAULT_DISENGAGEMENT_THRESHOLDS['Red'][Doctrine.DISENGAGEMENT_EROSION]
        beyond = 0

        for _, _, outcome in self.runs:
            result = F.force_outcome(outcome, 'Red-Plant')
            self.assertIn(result.outcome, (ER.HELD, ER.DESTROYED))

            if result.erosion >= erosion:
                beyond += 1

        # Non vacuo: in qualche replica le perdite superano la soglia di erosione di default.
        self.assertGreater(beyond, 0)


# ── S15 — PROSSIMITA' CON UN BLOCCO URBAN (CONTRATTO ROE) ─────────────────────

def _roe_military_only(base_fire_control):
    """`fire_control` di scenario con una ROE di non-ingaggio selettiva.

    Delega a `base_fire_control` SOLO se il bersaglio appartiene a una `Military`; per ogni
    altro bersaglio (qui: gli edifici dell'`Urban` adiacente) restituisce None, cioe' "non
    ingaggia" — la semantica ROE gia' prevista da `resolve_engagement`. Semplificazione
    dichiarata: la politica guarda il blocco del bersaglio, non la distanza da altri blocchi.
    """
    def fire_control(shooter, target):
        if not isinstance(getattr(target, 'block', None), Military):
            return None
        return base_fire_control(shooter, target)

    return fire_control


class TestS15UrbanProximityROEContract(F.LoggerSilencer, unittest.TestCase):
    """S15: una `Military` accanto a un'area urbana — test di CONTRATTO, non di modello.

    **Cosa dimostra e cosa no.** Il motore NON ha un modello di danno collaterale (e non
    deve averlo: la scelta di cosa colpire e' demandata al `fire_control` iniettato dal
    chiamante). Questo scenario dimostra solo l'ESTENSIBILITA' del contratto: un
    `fire_control` esterno puo' implementare una politica di non-ingaggio selettiva
    (`_roe_military_only`) e l'architettura del risolutore la rispetta. Non misura, non
    stima e non modella danni collaterali.

    Composizione: Red-Stronghold = `Military` 'Stronghold' con 3 BMP-2 + 1 ZSU-23-4; a
    1.5 km Red-Town = `Urban` 'Civilian' con 4 edifici (`Structure` 'Building'). Blue-Strike
    4 F-16C ('Strike', multiruolo). Red a soglie 1.0 (il caposaldo tiene), cosi' l'attacco
    prosegue abbastanza da poter scegliere fra i due blocchi.

    Varianti sugli stessi seed:
      * ROE: `_roe_military_only(fire_control di riferimento)`;
      * CONTROLLO: il fire_control di riferimento, senza ROE — gli edifici sono bersagli
        'structure' ingaggiabili. Serve a mostrare che, nella ROE, e' la politica (non la
        geometria o i sensori) a tenere la citta' fuori dal fuoco.

    Verifiche: con la ROE l'Urban e' nello stesso ingaggio (e' geometricamente in
    contatto) ma non riceve MAI un DamageEvent, mentre il caposaldo si'; senza ROE la
    citta' viene colpita.
    """

    SEEDS = _seeds('S15', 6)

    @staticmethod
    def _build():
        stronghold = F.build_force('Red-Stronghold', 'Red', [
            F.Unit('vehicle', 'BMP-2', 3, origin=(0.0, 0.0), step=(0.0, 250.0), prefix='ifv'),
            F.Unit('vehicle', 'ZSU-23-4-Shilka', 1, origin=(-300.0, 250.0), prefix='aaa')],
            mil_category=GROUND_BASE[0])   # 'Stronghold'
        town = F.make_infrastructure('Urban', 'Red-Town', 'Red', 'Civilian')
        F.add_assets(town, [F.make_structure(town, f'Red-Town/bld{i}', (1_500.0 + 150.0 * i, 250.0),
                                             category='Civilian', asset_type='Building') for i in range(4)])
        strike = F.build_force('Blue-Strike', 'Blue', [F.Unit('aircraft', 'F-16C Block 52d', 4,
                                                              origin=(-150_000.0, 0.0), step=(0.0, 500.0),
                                                              prefix='str', loadout='Strike')],
                               mil_category=F.AIR_UNIT)
        return strike, stronghold, town, F.routes_for(strike, [(20_000.0, 0.0)])

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.roe, cls.control = [], []

        for session_id in cls.SEEDS:
            for bucket, fire in ((cls.roe, _roe_military_only(F.make_fire_control())),
                                 (cls.control, F.make_fire_control())):
                strike, stronghold, town, routes = cls._build()
                outcome = F.run(session_id, [strike], [stronghold, town], fire, duration=3_600.0, routes=routes,
                                thresholds=RED_HOLDS)
                bucket.append((stronghold, town, outcome))

    def test_town_is_a_real_urban_block_in_the_same_engagement(self):
        for _, town, outcome in self.roe:
            self.assertIsInstance(town, Urban)
            self.assertIn(('Blue-Strike', 'Red-Stronghold', 'Red-Town'), _engagement_ids(outcome))

    def test_with_roe_the_town_never_takes_damage(self):
        for _, town, outcome in self.roe:
            self.assertEqual(F.damage_on(outcome, town.assets), [])
            self.assertTrue(all(asset.health == 100 for asset in town.assets.values()))
            result = F.force_outcome(outcome, 'Red-Town')
            self.assertEqual((result.lost, result.outcome), (0, ER.HELD))

    def test_with_roe_the_military_block_is_still_hit(self):
        self.assertGreater(sum(len(F.damage_on(o, s.assets)) for s, _, o in self.roe), 0)

    def test_without_roe_the_town_is_hit(self):
        """Controllo: e' la ROE, non la geometria, a tenere la citta' fuori dal fuoco."""
        self.assertGreater(sum(len(F.damage_on(o, t.assets)) for _, t, o in self.control), 0)


# ── S16 — INSTALLAZIONE NAVALE FISSA (PORTO) ──────────────────────────────────

class TestS16NavalInstallation(F.LoggerSilencer, unittest.TestCase):
    """S16: missione aeronavale contro un porto militare con navi ormeggiate.

    Composizione: Red-Port = `Military` 'Port' con 2 corvette FSG 1241.1MP Molniya
    ormeggiate (`Ship` senza rotta, quindi ferme), 1 banchina ('Dock') + 1 deposito
    carburante ('Oil_Tank') (`Structure`, tabella 'Port') e difesa costiera minima 1
    ZSU-23-4. Blue-Naval-Strike 4 F/A-18C ('Anti-Ship', multiruolo: arpioni 'asm' sulle
    navi, 'agm' sul resto, tutti intercettabili).

    Condizioni dell'incursione (dichiarate, necessarie perche' la domanda sia esercitata):
      * ENTRAMBI i lati ad oltranza (`BOTH_HOLD`), come l'ala di S6: con la dottrina di
        default Blue rompeva il contatto alla prima perdita (~125 s) senza aver mai
        sparato;
      * penetrazione a bassa quota (LOW_LEVEL_FACTOR, via `detection_factor` sui sensori
        rossi contro gli aerei Blue, come la bassa osservabilita' di S3): il radar di
        scoperta aerea delle Molniya (130 km) supera i sensori dell'F/A-18 (80 km mare,
        95 km suolo), e senza il fattore l'incursione era distrutta prima di rilevare
        qualunque bersaglio;
      * incursione coordinata (SALVO_WINDOW: gli impatti entro la finestra formano un
        unico evento-salva, il concetto di salva di Hughes): con `salvo_window` = 0 ogni
        impatto isolato e' assorbito dal primo intercettore in ordine di id (lo ZSU) e le
        navi non intercettano mai.

    Distinto da S6 (gruppo navale in movimento contro difesa costiera): qui il bersaglio
    primario e' l'installazione fissa, e le navi sono parte di essa. Domanda: il motore
    gestisce un bersaglio fisso con asset navali STATICI nello stesso Block di
    un'installazione navale. Verifiche: le navi non si muovono (nessun FuelEvent,
    posizione invariata) ma combattono (sparano e intercettano); il Block e' un solo
    ingaggio; navi e strutture del porto sono entrambe bersagli delle salve Blue, e ogni
    colpo in arrivo sul Block e' intercettato oppure raggiunge il modello di danno (nessun
    colpo perso); le strutture non sparano; i danni cadono sia sulle navi sia sulle
    strutture (aggregato); nessun asset intercetta piu' di quanto la sua scorta di
    intercettori consenta, e l'incursione arriva a esaurirla.

    Storia: nella prima stesura di Fase 7 la verifica "danni su navi e strutture" era
    stata tolta, perche' la scorta di intercettazione era `ammunition` (Shilka: 2000 colpi,
    Molniya: 320 unita' fra missili e colpi da 76 mm) e il porto assorbiva l'intera
    incursione. Con la scorta di intercettori distinta (ricalibrazione 2026-09-23, v.
    Mobile.ROUNDS_PER_GUN_INTERCEPT: Molniya 16 SA-N-4, Shilka 20) le corvette esauriscono
    gli intercettori a meta' incursione e il surplus raggiunge il porto: la verifica e'
    ripristinata.
    """

    SEEDS = _seeds('S16', 4)
    SHIPS = ('Red-Port/fsg0', 'Red-Port/fsg1')
    STRUCTURES = ('Red-Port/dock0', 'Red-Port/fuel0')
    LOW_LEVEL_FACTOR = 0.3   # costante di scenario dichiarata, non calibrata
    SALVO_WINDOW = 30.0      # [s], costante di scenario dichiarata

    @staticmethod
    def _build():
        port = F.make_force('Red-Port', 'Red', NAVAL_BASE[0])   # 'Port'
        F.add_assets(port, [
            F.make_ship(port, 'Red-Port/fsg0', 'FSG 1241.1MP Molniya', (0.0, 0.0)),
            F.make_ship(port, 'Red-Port/fsg1', 'FSG 1241.1MP Molniya', (0.0, 400.0)),
            F.make_structure(port, 'Red-Port/dock0', (300.0, 200.0), category='Port', asset_type='Dock'),
            F.make_structure(port, 'Red-Port/fuel0', (600.0, 200.0), category='Port', asset_type='Oil_Tank'),
            F.make_vehicle(port, 'Red-Port/aaa0', 'ZSU-23-4-Shilka', (800.0, -200.0))])
        strike = F.build_force('Blue-Naval-Strike', 'Blue', [F.Unit('aircraft', 'F/A-18C Hornet', 4,
                                                                    origin=(-150_000.0, 0.0, 6_000.0),
                                                                    step=(0.0, 800.0), prefix='fa',
                                                                    loadout='Anti-Ship')],
                               mil_category=F.AIR_UNIT)
        return strike, port, F.routes_for(strike, [(10_000.0, 0.0)])

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs = []

        original = ER.resolve_engagement

        for session_id in cls.SEEDS:
            strike, port, routes = cls._build()
            positions = {a: asset.position for a, asset in port.assets.items()}
            blue_ids = frozenset(strike.assets)
            low_level = (lambda observer, target, ids=blue_ids: cls.LOW_LEVEL_FACTOR if target.id in ids else 1.0)
            captured = []

            def spy(*args, **kwargs):
                result = original(*args, **kwargs)
                captured.append(result)
                return result

            # Si cattura l'EngagementResult (salve e risoluzioni) senza alterarlo, come S9.
            with patch.object(ER, 'resolve_engagement', side_effect=spy):
                outcome = F.run(session_id, [strike], [port], F.make_fire_control(), duration=3_600.0,
                                routes=routes, thresholds=BOTH_HOLD, detection_factor=low_level,
                                order_kwargs={'salvo_window': cls.SALVO_WINDOW})

            cls.runs.append((port, positions, outcome, [r for r in captured if r is not None]))

    def test_one_engagement_with_the_installation(self):
        for _, _, outcome, _ in self.runs:
            self.assertEqual(_engagement_ids(outcome), [('Blue-Naval-Strike', 'Red-Port')])

    def test_moored_ships_do_not_move(self):
        for port, positions, outcome, _ in self.runs:
            self.assertEqual([e for e in outcome.fuel_events if e.asset_id in port.assets], [])
            for asset_id in self.SHIPS:
                self.assertEqual(port.assets[asset_id].position, positions[asset_id])

    def test_moored_ships_still_fight(self):
        """Le navi ormeggiate sparano (AmmunitionEvent) e intercettano (InterceptionEvent)."""
        salvos = interceptions = 0

        for _, _, outcome, _ in self.runs:
            salvos += len(_salvos_by(outcome, self.SHIPS))
            interceptions += len(F.interceptions_by(outcome, self.SHIPS))

        self.assertGreater(salvos, 0)
        self.assertGreater(interceptions, 0)

    def test_interception_events_match_the_resolutions(self):
        """Gli InterceptionEvent catturati dallo spy sono il resoconto esatto delle
        risoluzioni: per ogni evento-salva sul porto, somma delle intercettazioni per asset
        = `SalvoResolution.intercepted`, con lo stesso istante e le stesse salve; e cio'
        che arriva nel SessionOutcome e' esattamente l'unione degli eventi degli ingaggi."""
        for _, _, outcome, results in self.runs:
            for result in results:
                for resolution in result.resolutions:
                    events = [e for e in result.interception_events
                              if e.time == resolution.time and e.force_id == resolution.force_id]
                    self.assertEqual(sum(e.interceptions for e in events), resolution.intercepted)
                    self.assertTrue(all(e.salvo_ids == resolution.salvo_ids for e in events))

            self.assertEqual(sorted(outcome.interception_events, key=lambda e: (e.time, e.asset_id)),
                             sorted((e for r in results for e in r.interception_events),
                                    key=lambda e: (e.time, e.asset_id)))
            # Le intercettazioni non sono munizioni offensive (cambio del 2026-09-23).
            self.assertTrue(all(isinstance(e, ER.AmmunitionEvent) for e in outcome.ammunition_events))

    def test_ships_and_structures_are_targeted_and_every_round_is_accounted_for(self):
        """Navi e strutture dello stesso Block sono entrambe bersagli delle salve Blue
        (aggregato), e sul Block misto (navi, strutture, AAA) nessun colpo si perde: colpi
        in arrivo = intercettati + DamageEvent sul porto + colpi su relitti. Non vacuo: il
        porto e' davvero sotto il fuoco e intercetta. (Sostituisce "danni su navi e
        strutture": v. docstring della classe.)"""
        targets = Counter()
        incoming = intercepted = 0

        for port, _, outcome, results in self.runs:
            for result in results:
                for salvo in result.salvos:
                    if salvo.target_id in self.SHIPS:
                        targets['ship'] += 1
                    elif salvo.target_id in self.STRUCTURES:
                        targets['structure'] += 1

            resolutions = [r for result in results for r in result.resolutions if r.force_id == 'Red-Port']
            rounds = sum(r.rounds for r in resolutions)
            stopped = sum(r.intercepted for r in resolutions)
            wasted = sum(r.wasted for r in resolutions)
            self.assertEqual(rounds, stopped + len(F.damage_on(outcome, port.assets)) + wasted)
            incoming += rounds
            intercepted += stopped

        self.assertGreater(targets['ship'], 0)
        self.assertGreater(targets['structure'], 0)
        self.assertGreater(incoming, 0)
        self.assertGreater(intercepted, 0)

    def test_structures_never_shoot(self):
        for _, _, outcome, _ in self.runs:
            self.assertEqual([e for e in outcome.ammunition_events if e.asset_id in self.STRUCTURES], [])

    def test_damage_falls_on_both_ships_and_structures(self):
        """Aggregato sulle repliche: la difesa del porto non e' piu' inesauribile."""
        ships = sum(len(F.damage_on(outcome, self.SHIPS)) for _, _, outcome, _ in self.runs)
        structures = sum(len(F.damage_on(outcome, self.STRUCTURES)) for _, _, outcome, _ in self.runs)

        self.assertGreater(ships, 0)
        self.assertGreater(structures, 0)

    def test_interceptions_are_bounded_by_the_interceptor_stock(self):
        """Ogni asset intercetta al piu' la propria scorta iniziale (dal registro), e in
        aggregato l'incursione la esaurisce su almeno un asset."""
        exhausted = 0

        for port, _, outcome, _ in self.runs:
            initial = {a: asset.interceptor_stock_from_registry() for a, asset in port.assets.items()
                       if hasattr(asset, 'interceptor_stock_from_registry')}
            used = outcome.interceptions_consumed()

            for asset_id, count in used.items():
                with self.subTest(asset=asset_id):
                    self.assertIsNotNone(initial[asset_id])
                    self.assertLessEqual(count, initial[asset_id])
                    self.assertEqual(port.assets[asset_id].interceptor_stock, initial[asset_id] - count)

            exhausted += sum(1 for a in used if port.assets[a].interceptor_stock == 0)

        self.assertGreater(exhausted, 0)


# ── S17 — SWEEP DI SCALA GERARCHICA ───────────────────────────────────────────

class TestS17HierarchicalScaleSweep(F.LoggerSilencer, unittest.TestCase):
    """S17: la composizione di S1 (senza CAS) ripetuta a taglie gerarchiche crescenti.

    **Non e' uno scenario narrativo**: e' una parametrizzazione. Per ogni `mil_category`
    della scala (Company, Battallion, Regiment, Brigade, Division — chiavi di
    `MILITARY_CATEGORY['Ground_Base']`) si costruisce lo scontro Blue-Armor (carri + IFV)
    contro Red-Line (IFV + artiglieria + AAA + SHORAD) con il numero di asset per Block
    scalato da SCALE (moltiplicatore dichiarato di test: 1, 2, 3, 4, 6 — NON organici
    dottrinali reali, solo taglie crescenti). Le formazioni restano in fila con passo fisso,
    quindi il fronte si allunga con la taglia.

    Verifiche per ciascuna taglia: la sessione si risolve senza errori con un solo ingaggio
    e un esito per ciascuna delle due forze; il tempo d'esecuzione resta sotto una soglia
    LARGA (MAX_SECONDS, per intercettare regressioni d'ordine di grandezza). Proprieta'
    monotone con la scala (strutturali, non coefficienti): il numero di finestre di
    contatto (sola geometria, deterministico) cresce strettamente; gli asset impegnati
    crescono; il numero ASSOLUTO di DamageEvent, aggregato su piu' seed, cresce fra la
    taglia minima e quella massima (non si verifica il rapporto, ne' la monotonia stretta
    fra taglie adiacenti, che l'RNG e il disingaggio possono invertire).
    """

    SCALE = (('Company', 1), ('Battallion', 2), ('Regiment', 3), ('Brigade', 4), ('Division', 6))
    SEEDS = _seeds('S17', 3)
    MAX_SECONDS = 60.0

    @staticmethod
    def _build(mil_category, k):
        blue = F.build_force('Blue-Armor', 'Blue', [
            F.Unit('vehicle', 'M1A2-Abrams', 3 * k, origin=(-8_000.0, 0.0), step=(0.0, 300.0), prefix='mbt',
                   sensors=VISUAL),
            F.Unit('vehicle', 'M2-Bradley', 2 * k, origin=(-8_300.0, 150.0), step=(0.0, 300.0), prefix='ifv',
                   sensors=VISUAL)], mil_category=mil_category)
        red = F.build_force('Red-Line', 'Red', [
            F.Unit('vehicle', 'BMP-2', 3 * k, origin=(0.0, 0.0), step=(0.0, 300.0), prefix='ifv', sensors=VISUAL),
            F.Unit('vehicle', '2S19-Msta', k, origin=(6_000.0, 300.0), step=(0.0, 300.0), prefix='art',
                   sensors={'ground': F.DECLARED_ARTILLERY_OBSERVATION_RANGE}),
            F.Unit('vehicle', 'ZSU-23-4-Shilka', k, origin=(1_000.0, 600.0), step=(0.0, 300.0), prefix='aaa'),
            F.Unit('vehicle', '9K35-Strela-10', k, origin=(1_000.0, -300.0), step=(0.0, 300.0), prefix='sam')],
            mil_category=mil_category)
        return blue, red, F.routes_for(blue, [(2_000.0, 0.0)])

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.results = {}

        for mil_category, k in cls.SCALE:
            blue, red, routes = cls._build(mil_category, k)
            windows = CS.schedule_contacts([blue], [red], 3_600.0, routes=routes)
            runs = []

            for session_id in cls.SEEDS:
                blue, red, routes = cls._build(mil_category, k)
                outcome, seconds = F.timed(F.run, session_id, [blue], [red], F.make_fire_control(),
                                           duration=3_600.0, routes=routes)
                runs.append((blue, red, outcome, seconds))

            cls.results[mil_category] = {'k': k, 'windows': len(windows), 'runs': runs}

    def test_scale_uses_the_hierarchical_categories(self):
        for mil_category, _ in self.SCALE:
            self.assertIn(mil_category, GROUND_BASE)
            blue, red, _, _ = self.results[mil_category]['runs'][0]
            self.assertEqual((blue.mil_category, red.mil_category), (mil_category, mil_category))

    def test_every_size_resolves_into_one_engagement(self):
        for mil_category, _ in self.SCALE:
            for blue, red, outcome, _ in self.results[mil_category]['runs']:
                with self.subTest(size=mil_category):
                    self.assertIsInstance(outcome, SessionOutcome)
                    self.assertEqual(_engagement_ids(outcome), [('Blue-Armor', 'Red-Line')])
                    for force in (blue, red):
                        result = F.force_outcome(outcome, force.id)
                        self.assertEqual(result.committed, len(force.assets))
                        self.assertIn(result.outcome, ER.FORCE_OUTCOMES)

    def test_every_size_runs_within_a_loose_bound(self):
        for mil_category, _ in self.SCALE:
            for *_, seconds in self.results[mil_category]['runs']:
                self.assertLess(seconds, self.MAX_SECONDS, mil_category)

    def test_contact_windows_grow_strictly_with_size(self):
        counts = [self.results[mil_category]['windows'] for mil_category, _ in self.SCALE]
        self.assertEqual(counts, sorted(set(counts)))

    def test_absolute_damage_grows_from_smallest_to_largest(self):
        damage = {mil_category: sum(len(o.damage_events) for _, _, o, _ in self.results[mil_category]['runs'])
                  for mil_category, _ in self.SCALE}
        smallest, largest = self.SCALE[0][0], self.SCALE[-1][0]
        self.assertGreater(damage[largest], damage[smallest])


# ── S18 — INTERDIZIONE DI UNA RETE TRANSPORT MULTI-NODO ───────────────────────

class TestS18TransportNetworkInterdiction(F.LoggerSilencer, unittest.TestCase):
    """S18: una missione aerea scortata contro PIU' nodi fissi di una rete di trasporto.

    Composizione — tre `Transport` reali distinti, lungo una rotta est-ovest, a 25 km l'uno
    dall'altro (non un convoglio mobile come S7):
      * Red-Rail (sub_category 'Railway'): 1 ponte ferroviario + 1 interscambio;
      * Red-Grid (sub_category 'Electric'): 2 tralicci/sottostazioni ('Electric_Infrastructure');
      * Red-Road (sub_category 'Road'): 1 ponte stradale + 1 posto di blocco ('Check_Point');
    Red-CAP 2 MiG-29S ('CAP') in pattugliamento sulla rete; Blue-Package 4 F-16C
    ('Strike', ruolo strike) + 2 F-15C ('Eagle Escort', ruolo fighter), un'unica formazione
    che sorvola i tre nodi in sequenza.

    Scelta della geometria (documentata): i nodi sono abbastanza vicini perche' LA STESSA
    formazione Blue sia in contatto con tutti e tre (e con la CAP) nella stessa sessione,
    quindi la clusterizzazione a componenti connesse di `Session_Simulator` deve fonderli
    in UN solo ingaggio a cinque forze, con un esito per ciascun nodo. Una variante di
    controllo mette due nodi a 600 km l'uno dall'altro, ciascuno con la propria coppia di
    strike: devono diventare due ingaggi separati.

    Domanda: il motore gestisce PIU' forze bersaglio non-Military distinte nella stessa
    sessione. Verifiche: un solo ingaggio con tutte le forze; ogni nodo ha il proprio
    ForceOutcome e riceve danno (aggregato); nessun nodo si disingaggia (non-Military);
    i danni a ciascun nodo arrivano nell'ordine geometrico della rotta (primo colpo sul
    nodo piu' vicino prima); nella variante lontana, due ingaggi disgiunti.
    """

    SEEDS = _seeds('S18', 6)
    NODES = ('Red-Rail', 'Red-Grid', 'Red-Road')

    @staticmethod
    def _nodes(x_rail, x_grid, x_road):
        rail = F.make_infrastructure('Transport', 'Red-Rail', 'Red', 'Railway')
        F.add_assets(rail, [
            F.make_structure(rail, 'Red-Rail/bridge0', (x_rail, 0.0), category='Railway', asset_type='Bridge'),
            F.make_structure(rail, 'Red-Rail/xchg0', (x_rail + 300.0, 200.0), category='Railway',
                             asset_type='Railway_Interchange')])
        grid = F.make_infrastructure('Transport', 'Red-Grid', 'Red', 'Electric')
        F.add_assets(grid, [F.make_structure(grid, f'Red-Grid/pylon{i}', (x_grid + 300.0 * i, -200.0),
                                             category='Electric', asset_type='Electric_Infrastructure')
                            for i in range(2)])
        road = F.make_infrastructure('Transport', 'Red-Road', 'Red', 'Road')
        F.add_assets(road, [
            F.make_structure(road, 'Red-Road/bridge0', (x_road, 0.0), category='Road', asset_type='Bridge'),
            F.make_structure(road, 'Red-Road/check0', (x_road + 300.0, 150.0), category='Road',
                             asset_type='Check_Point')])
        return rail, grid, road

    @classmethod
    def _build(cls):
        rail, grid, road = cls._nodes(0.0, 25_000.0, 50_000.0)
        cap = F.build_force('Red-CAP', 'Red', [F.Unit('aircraft', 'MiG-29S', 2, origin=(60_000.0, 0.0),
                                                      step=(0.0, 1_000.0), prefix='cap', loadout='CAP')],
                            mil_category=F.AIR_UNIT)
        package = F.build_force('Blue-Package', 'Blue', [
            F.Unit('aircraft', 'F-16C Block 52d', 4, origin=(-150_000.0, 0.0), step=(0.0, 500.0), prefix='str',
                   loadout='Strike'),
            F.Unit('aircraft', 'F-15C Eagle', 2, origin=(-148_000.0, 2_000.0), step=(0.0, 600.0), prefix='esc',
                   loadout='Eagle Escort')], mil_category=F.AIR_UNIT)
        roles = {a: ('strike' if '/str' in a else 'fighter') for a in package.assets}
        routes = F.routes_for(package, [(80_000.0, 0.0)])
        routes.update(F.routes_for(cap, [(-20_000.0, 0.0)]))
        return package, [rail, grid, road, cap], routes, F.make_fire_control(roles=roles)

    @classmethod
    def _build_far(cls):
        rail, _, road = cls._nodes(0.0, 0.0, 600_000.0)
        west = F.build_force('Blue-West', 'Blue', [F.Unit('aircraft', 'F-16C Block 52d', 2, origin=(-150_000.0, 0.0),
                                                          step=(0.0, 500.0), prefix='str', loadout='Strike')],
                             mil_category=F.AIR_UNIT)
        east = F.build_force('Blue-East', 'Blue', [F.Unit('aircraft', 'F-16C Block 52d', 2, origin=(450_000.0, 0.0),
                                                          step=(0.0, 500.0), prefix='str', loadout='Strike')],
                             mil_category=F.AIR_UNIT)
        roles = dict(_strike_roles(west), **_strike_roles(east))
        routes = F.routes_for(west, [(20_000.0, 0.0)])
        routes.update(F.routes_for(east, [(620_000.0, 0.0)]))
        return [west, east], [rail, road], routes, F.make_fire_control(roles=roles)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.runs, cls.far_runs = [], []

        for session_id in cls.SEEDS:
            package, reds, routes, fire = cls._build()
            cls.runs.append((reds, F.run(session_id, [package], reds, fire, duration=3_600.0, routes=routes)))

        for session_id in cls.SEEDS[:2]:
            blues, reds, routes, fire = cls._build_far()
            cls.far_runs.append(F.run(session_id, blues, reds, fire, duration=3_600.0, routes=routes))

    def test_nodes_are_distinct_real_transport_blocks(self):
        reds, _ = self.runs[0]
        nodes = reds[:3]
        self.assertTrue(all(isinstance(node, Transport) and not isinstance(node, Military) for node in nodes))
        self.assertEqual([node.sub_category for node in nodes], ['Railway', 'Electric', 'Road'])

    def test_all_nodes_are_fused_in_one_engagement(self):
        for _, outcome in self.runs:
            self.assertEqual(_engagement_ids(outcome),
                             [('Blue-Package', 'Red-CAP', 'Red-Grid', 'Red-Rail', 'Red-Road')])

    def test_every_node_has_its_own_outcome_and_never_disengages(self):
        for reds, outcome in self.runs:
            for node in reds[:3]:
                result = F.force_outcome(outcome, node.id)
                self.assertIsNotNone(result, node.id)
                self.assertEqual(result.committed, len(node.assets))
                self.assertIn(result.outcome, (ER.HELD, ER.DESTROYED))

    def test_every_node_is_hit(self):
        for index, name in enumerate(self.NODES):
            hits = sum(len(F.damage_on(o, reds[index].assets)) for reds, o in self.runs)
            self.assertGreater(hits, 0, name)

    def test_nodes_are_hit_in_route_order(self):
        """Il primo colpo su ciascun nodo segue l'ordine lungo la rotta (ovest -> est)."""
        for reds, outcome in self.runs:
            firsts = []
            for node in reds[:3]:
                times = [e.time for e in F.damage_on(outcome, node.assets)]
                if times:
                    firsts.append(min(times))
            self.assertEqual(firsts, sorted(firsts))

    def test_distant_nodes_give_separate_engagements(self):
        for outcome in self.far_runs:
            self.assertEqual(sorted(_engagement_ids(outcome)), [('Blue-East', 'Red-Road'), ('Blue-West', 'Red-Rail')])


if __name__ == '__main__':
    unittest.main()
