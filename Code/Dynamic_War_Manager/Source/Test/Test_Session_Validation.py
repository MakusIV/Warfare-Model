"""FASE 7 del motore di sessioni virtuali — test di DETERMINISMO e di AGNOSTICISMO.

Sono i due test che la roadmap (§8 di
`Analysis/Document/Architettura_esecuzione_sessioni_virtuali_ANALISI.md`) nomina
esplicitamente per la Fase 7, accanto agli scenari di plausibilita' (quelli sono in
`Test_Session_Scenarios.py`). Entrambi girano sulla composizione di S1
(`Scenario_Fixtures.combined_arms_scenario`: forze terrestri meccanizzate/corazzate, CAS,
artiglieria, AAA/VSHORAD), con asset REALI dei registri: e' una composizione a media
complessita' che esercita tutta la catena (scheduler, rilevamento, latenze, salve,
intercettazione, dottrina di disingaggio, danno, munizioni, carburante).

## Determinismo
"Stesso seed -> stesso outcome", verificato campo per campo sul `SessionOutcome` e sullo
stato reale degli asset dopo l'applicazione. Accompagnato dal suo controllo di NON
vacuita': con un `session_id` diverso (quindi un seed diverso) l'esito deve cambiare —
altrimenti l'uguaglianza potrebbe dipendere da un motore che ignora il seed.

## Agnosticismo: perche' NON c'e' un "adapter da rimuovere"
Il vincolo (wiki `decisions/core-simulator-agnostic`, memoria
`feedback_core_simulator_agnostic`) formula il test operativo come "cancellando l'adapter
DCS la campagna deve continuare a girare". Oggi, pero', nell'albero Python
(`Code/Dynamic_War_Manager/Source/`) **non esiste alcun adapter DCS**: l'integrazione con
DCS vive tutta a livello di file `.miz`/Lua, fuori da questo albero. Un test "prima/dopo la
rimozione" non ha quindi nulla da rimuovere. Per lo stato attuale del motore il test di
agnosticismo e' un test di **contratto**, in due parti:

a. **Strutturale** — la catena delle porte (`SessionOrder`, `SessionOutcome`,
   `ForceOutcome`, `DamageEvent`, `AmmunitionEvent`, `InterceptionEvent`, `FuelEvent`) ha
   SOLO campi di tipo
   dominio: id stringa, secondi float, frazioni/interi, booleani, tuple di altri tipi della
   catena; nessun nome di campo del lessico del simulatore; i moduli del motore non
   importano nulla di legato al simulatore (lettori `.miz`/Lua, orologio del simulatore).
   E, sull'esito reale di uno scenario, ogni id presente e' un id di dominio costruito dal
   core (id di forza/asset/sessione), mai un id di missione del simulatore.
b. **Funzionale end-to-end** — l'intera catena gira con dati costruiti SOLO in Python
   (nessun `.miz`, nessun `dcs_unit_data`, nessun riferimento DCS nel setup) e produce un
   `SessionOutcome` valido e COMPLETO (e' il resoconto esatto dello stato applicato agli
   asset); inoltre piu' sessioni consecutive si concatenano sullo stato mutato — una
   mini-campagna senza simulatore, che e' esattamente cio' che il futuro adapter dovra'
   rispettare: produrre lo stesso `SessionOutcome` che qui produce il core da solo.

Quando l'adapter DCS esistera', il test "cancellandolo la campagna gira" diventera'
eseguibile alla lettera; fino ad allora questo e' il suo equivalente verificabile.
"""

import ast
import dataclasses
import inspect
import sys
import typing
import unittest
from collections import abc

from Code.Dynamic_War_Manager.Source.Test import Scenario_Fixtures as F
from Code.Dynamic_War_Manager.Source.Command import Session_Types as ST
from Code.Dynamic_War_Manager.Source.Logic import Contact_Scheduler as CS
from Code.Dynamic_War_Manager.Source.Logic import Damage_Model as DM
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic import Fuel_Model as FM
from Code.Dynamic_War_Manager.Source.Logic import Session_Simulator as SS
from Code.Dynamic_War_Manager.Source.Utility import Session_Rng


# ── DETERMINISMO ──────────────────────────────────────────────────────────────

class TestDeterminism(F.LoggerSilencer, unittest.TestCase):
    """Stesso SessionOrder e forze ricostruite identiche -> SessionOutcome identico."""

    SESSION = 'S7-det-alpha'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.first_scenario = F.combined_arms_scenario()
        cls.first = cls.first_scenario.run(cls.SESSION)
        cls.second_scenario = F.combined_arms_scenario()
        cls.second = cls.second_scenario.run(cls.SESSION)
        cls.other = F.combined_arms_scenario().run('S7-det-beta')

    def test_outcome_is_not_trivial(self):
        """Il confronto ha senso solo se l'esito contiene davvero qualcosa."""
        self.assertGreater(len(self.first.damage_events), 0)
        self.assertGreater(len(self.first.ammunition_events), 0)
        self.assertGreater(len(self.first.fuel_events), 0)
        self.assertGreater(len(self.first.engagement_outcomes), 0)

    def test_rebuilt_forces_have_identical_ids(self):
        """Precondizione: gli id (chiave dell'RNG e dell'ordine) sono stabili."""
        ids = lambda scenario: sorted(a for f in scenario.forces for a in [f.id, *f.assets])  # noqa: E731
        self.assertEqual(ids(self.first_scenario), ids(self.second_scenario))

    def test_same_order_same_outcome_field_by_field(self):
        for name in ('session_id', 't_start', 't_end'):
            self.assertEqual(getattr(self.first, name), getattr(self.second, name), name)

        for name in ('engagement_outcomes', 'damage_events', 'ammunition_events', 'interception_events',
                     'fuel_events'):
            left, right = getattr(self.first, name), getattr(self.second, name)
            self.assertEqual(len(left), len(right), name)

            for index, (a, b) in enumerate(zip(left, right)):
                self.assertEqual(a, b, f'{name}[{index}]')

    def test_same_order_same_outcome_whole_object(self):
        """I campi sono dataclass frozen comparabili: l'intero oggetto e' uguale."""
        self.assertEqual(self.first, self.second)

    def test_same_order_same_applied_state(self):
        """Anche lo stato REALE degli asset dopo l'applicazione coincide."""
        for force_a, force_b in zip(self.first_scenario.forces, self.second_scenario.forces):
            for asset_id in force_a.assets:
                a, b = force_a.assets[asset_id], force_b.assets[asset_id]
                self.assertEqual((a.health, a.ammunition, a.fuel), (b.health, b.ammunition, b.fuel),
                                 asset_id)

    def test_different_seed_changes_the_outcome(self):
        """Controllo di non vacuita': un altro session_id (altro seed) cambia le estrazioni."""
        self.assertNotEqual(self.first.damage_events, self.other.damage_events)
        self.assertGreater(len(self.other.damage_events), 0)

    def test_different_seed_keeps_the_structure(self):
        """Cambia l'esito stocastico, non la struttura deterministica: stesse componenti
        di forze in contatto (dipendono solo dalla geometria, non dal seed)."""
        ids = lambda outcome: [tuple(o.force_id for o in e) for e in outcome.engagement_outcomes]  # noqa: E731
        self.assertEqual(ids(self.first), ids(self.other))


# ── AGNOSTICISMO (a): STRUTTURALE ─────────────────────────────────────────────

# Tipi atomici ammessi alle porte: id/etichette (str), secondi e frazioni (float), interi,
# booleani, None.
_ATOMIC = (str, float, int, bool, type(None))

# Contenitori della catena delle porte: i soli tipi composti ammessi dentro un campo.
_PORT_TYPES = (ST.SessionOrder, ST.SessionOutcome, ER.ForceOutcome, DM.DamageEvent,
               ER.AmmunitionEvent, ER.InterceptionEvent, FM.FuelEvent)

# Lessico del simulatore che non deve comparire in un nome di campo del contratto
# (confronto su nome normalizzato: minuscolo, senza '_').
_SIMULATOR_WORDS = ('dcs', 'miz', 'unitid', 'unitname', 'groupid', 'groupname', 'airdrome',
                    'dictkey', 'missiontime', 'modeltime', 'lua')

# Moduli del motore di sessione (tutta la catena della porta di uscita).
_ENGINE_MODULES = (ST, SS, ER, CS, DM, FM, Session_Rng)

# Import vietati nel core (wiki decisions/core-simulator-agnostic): lettori di file DCS.
_FORBIDDEN_IMPORTS = ('lupa', 'zipfile', 'minizip')


def _type_is_domain(tp) -> bool:
    """True se il tipo annotato e' composto solo di tipi atomici e tipi della catena."""
    if tp in _ATOMIC or tp in _PORT_TYPES:
        return True

    origin = typing.get_origin(tp)
    args = typing.get_args(tp)

    if origin is typing.Union:
        return all(_type_is_domain(arg) for arg in args)

    if origin is tuple:
        return all(_type_is_domain(arg) for arg in args if arg is not Ellipsis)

    if origin in (abc.Mapping, dict):
        return all(_type_is_domain(arg) for arg in args)

    return False


class TestAgnosticContractStructure(unittest.TestCase):
    """Parte (a): il contratto delle porte e' fatto solo di tipi e nomi di dominio."""

    def test_port_fields_are_domain_types(self):
        for port in _PORT_TYPES:
            hints = typing.get_type_hints(port, vars(sys.modules[port.__module__]))

            for field in dataclasses.fields(port):
                with self.subTest(port=port.__name__, field=field.name):
                    self.assertTrue(_type_is_domain(hints[field.name]),
                                    f"{port.__name__}.{field.name}: {hints[field.name]!r}")

    def test_port_field_names_avoid_simulator_vocabulary(self):
        for port in _PORT_TYPES:
            for field in dataclasses.fields(port):
                normalized = field.name.lower().replace('_', '')

                with self.subTest(port=port.__name__, field=field.name):
                    self.assertFalse(any(word in normalized for word in _SIMULATOR_WORDS))

    def test_time_fields_are_seconds_as_float(self):
        """Il tempo alle porte e' in secondi assoluti (float), mai un orologio del simulatore."""
        for port in _PORT_TYPES:
            hints = typing.get_type_hints(port, vars(sys.modules[port.__module__]))

            for field in dataclasses.fields(port):
                if field.name == 'time' or field.name.startswith('t_'):
                    with self.subTest(port=port.__name__, field=field.name):
                        self.assertIn(hints[field.name], (float, typing.Optional[float]))

    def test_engine_modules_import_nothing_simulator_bound(self):
        for module in _ENGINE_MODULES:
            tree = ast.parse(inspect.getsource(module))
            imported = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.append(node.module)

            with self.subTest(module=module.__name__):
                for name in imported:
                    self.assertNotIn(name.split('.')[0], _FORBIDDEN_IMPORTS, name)
                    self.assertNotIn('dcs', name.lower(), name)

    def test_engine_modules_never_read_the_simulator_clock(self):
        for module in _ENGINE_MODULES:
            with self.subTest(module=module.__name__):
                self.assertNotIn('timer.getTime', inspect.getsource(module))


# ── AGNOSTICISMO: ESITO REALE ─────────────────────────────────────────────────

class _OutcomeWalker:
    """Raccoglie (percorso, valore) di ogni foglia di un SessionOutcome."""

    @classmethod
    def leaves(cls, value, path='outcome'):
        if dataclasses.is_dataclass(value) and not isinstance(value, type):
            for field in dataclasses.fields(value):
                yield from cls.leaves(getattr(value, field.name), f'{path}.{field.name}')
        elif isinstance(value, (tuple, list)):
            for index, item in enumerate(value):
                yield from cls.leaves(item, f'{path}[{index}]')
        else:
            yield path, value


class TestAgnosticEndToEnd(F.LoggerSilencer, unittest.TestCase):
    """Parte (b), piu' la verifica degli id sull'esito reale (completa la parte a).

    QUESTO e' il test di agnosticismo per lo stato attuale del motore (v. docstring del
    modulo): l'intera catena gira senza che DCS esista da nessuna parte — asset costruiti
    dai soli registri Python, senza `dcs_unit_data`, rotte `DataType.Route` costruite in
    memoria, seed dal solo `session_id` di dominio — e produce un esito completo.
    """

    SESSIONS = ('S7-agn-1', 'S7-agn-2', 'S7-agn-3')

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.scenario = F.combined_arms_scenario()
        cls.outcome = cls.scenario.run(cls.SESSIONS[0])

        # Mini-campagna: tre sessioni consecutive sulle STESSE forze (lo stato passa solo
        # attraverso gli asset mutati), la seconda e la terza senza rotte (forze ferme).
        # NB: run_session non aggiorna `asset.position` a fine rotta (nessun movimento
        # fisico, v. il suo docstring): nelle sessioni 2-3 le forze ripartono dalle
        # posizioni iniziali. Qui non conta — si verifica la concatenazione dello stato di
        # salute/munizioni/carburante — ma e' un limite per una campagna vera (v. report).
        cls.campaign_scenario = F.combined_arms_scenario()
        cls.campaign = []
        t_start = 0.0

        for index, session_id in enumerate(cls.SESSIONS):
            routes = cls.campaign_scenario.routes if index == 0 else {}
            outcome = F.run(session_id, cls.campaign_scenario.forces_a, cls.campaign_scenario.forces_b,
                            cls.campaign_scenario.fire_control, duration=3_600.0, t_start=t_start,
                            routes=routes)
            cls.campaign.append(outcome)
            t_start = outcome.t_end

    def _domain_ids(self, scenario):
        ids = {force.id for force in scenario.forces}
        ids |= {asset_id for force in scenario.forces for asset_id in force.assets}
        return ids

    def test_no_simulator_module_was_loaded(self):
        """Nessun lettore di file del simulatore e' stato caricato per far girare la catena."""
        for name in ('lupa', 'minizip'):
            self.assertNotIn(name, sys.modules)

    def test_assets_carry_no_simulator_data(self):
        for force in self.scenario.forces:
            for asset_id, asset in force.assets.items():
                self.assertIsInstance(asset.id, str)
                self.assertEqual(asset.id, asset_id)

    def test_every_id_in_the_outcome_is_a_domain_id(self):
        known = self._domain_ids(self.scenario)
        id_fields = ('target_id', 'source_id', 'asset_id', 'force_id')

        for path, value in _OutcomeWalker.leaves(self.outcome):
            self.assertIsInstance(value, _ATOMIC, path)

            if path.rsplit('.', 1)[-1] in id_fields and value is not None:
                self.assertIn(value, known, path)

        self.assertEqual(self.outcome.session_id, self.SESSIONS[0])

    def test_every_time_is_seconds_within_the_session(self):
        for path, value in _OutcomeWalker.leaves(self.outcome):
            leaf = path.rsplit('.', 1)[-1]

            if leaf == 'time' and value is not None:
                self.assertIsInstance(value, float, path)
                self.assertGreaterEqual(value, self.outcome.t_start - CS.TIME_EPS, path)
                self.assertLessEqual(value, self.outcome.t_end + CS.TIME_EPS, path)

    def test_outcome_is_complete(self):
        """Un esito completo: ingaggi, danni, munizioni e carburante tutti presenti."""
        self.assertIsInstance(self.outcome, ST.SessionOutcome)
        self.assertGreater(len(self.outcome.engagement_outcomes), 0)
        self.assertGreater(len(self.outcome.damage_events), 0)
        self.assertGreater(len(self.outcome.ammunition_events), 0)
        moving = set(self.scenario.routes)
        self.assertEqual({event.asset_id for event in self.outcome.fuel_events}, moving)

    def test_outcome_is_the_exact_account_of_the_applied_state(self):
        """Salute finale di ogni asset = ultimo health_after dell'esito (100 se mai colpito)."""
        final = {}

        for event in self.outcome.damage_events:
            final[event.target_id] = event.health_after

        for force in self.scenario.forces:
            for asset_id, asset in force.assets.items():
                self.assertEqual(asset.health, final.get(asset_id, 100), asset_id)

    def test_campaign_of_sessions_runs_without_simulator(self):
        """Tre sessioni in fila: intervalli contigui, stato concatenato, nessun errore."""
        self.assertEqual(len(self.campaign), len(self.SESSIONS))

        for previous, following in zip(self.campaign, self.campaign[1:]):
            self.assertGreaterEqual(following.t_start, previous.t_end - CS.TIME_EPS)

        # Il danno di sessioni successive parte dalla salute lasciata dalle precedenti.
        last = {}
        for outcome in self.campaign:
            for event in outcome.damage_events:
                if event.target_id in last:
                    self.assertEqual(event.health_before, last[event.target_id])
                last[event.target_id] = event.health_after

        for force in self.campaign_scenario.forces:
            for asset_id, asset in force.assets.items():
                self.assertEqual(asset.health, last.get(asset_id, 100), asset_id)



if __name__ == '__main__':
    unittest.main()
