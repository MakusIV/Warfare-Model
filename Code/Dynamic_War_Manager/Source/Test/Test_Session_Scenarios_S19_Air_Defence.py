"""S19 — allocazione della difesa aerea fra intercettazione e tiro sul lanciatore (A6).

Scenario persistente della riproduzione di `Analysis/Document/Proposta_Regole_Allocazione_SAM.md`
(§1.1 in origine, §7 per le regole approvate il 2026-09-28): una linea Red di 3 BMP-2 con una
difesa aerea a corto raggio, attaccata da A-10C che lanciano AGM-65D da ~16 km.

Regole verificate (esito QUALITATIVO, non numerico, come chiede il §6 della proposta):
  * **D** (fatta): intercetta solo un'arma che dichiara il task 'Anti_Missile'. Lo Strela-10
    (9M37) non intercetta i Maverick, quindi conserva i missili per gli aerei;
  * **L** (L1 implementata il 2026-09-28, passo 4): un colpo e' intercettabile solo se lanciato da FUORI dal
    volume d'intercettazione V_I dell'intercettore; se il lanciatore era dentro, si spara a lui.
    Il Tor arretrato (lancio a ~15-19 km, fuori dai suoi 12 km) intercetta; col Tor avanzato e
    gli A-10C che attaccano solo i BMP-2, i lanci partono a ~9,5 km dal Tor (dentro) e il Tor
    spara al lanciatore senza intercettare.

Misura del 2026-09-28 (passo 3): nel secondo caso il motore attuale rispetta GIA' la regola per
tempistica, non per costruzione: il lanciatore entra nei 12 km prima che i suoi Maverick
arrivino, e il Tor spende gli 8 missili su di lui. La verifica resta qui come regressione. Il
caso che solo L1 distingue (intercettore con scorta in avanzo e lancio da dentro la zona) non
si ottiene in modo stabile con questa geometria: la portata del Maverick (15 km) supera la zona
del Tor (12 km), quindi un Tor raggiungibile viene attaccato da fuori zona. Va verificato con un
test unitario a geometria controllata del risolutore: Test_Engagement_Resolver.
  TestLauncherInsideInterceptionZone.

Fire control: i registri veri (`Fire_Control.make_registry_fire_control`), ma l'A-10C spara
solo AGM-65D. Con il criterio Pk/costo (A5) sceglierebbe la Mk-82AIR del loadout 'Maverick/Gun
CAS', che non e' intercettabile e renderebbe lo scenario vuoto. Il filtro fa le veci del filtro
per tipo di missione (A4, rimandato all'entita' Mission): missione anticarro con Maverick.

Dottrina: entrambi i lati ad oltranza (`BOTH_HOLD`), per isolare l'allocazione della difesa
dal disingaggio alla prima perdita (difetto noto, §5.3 della proposta).
"""

import unittest

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


def maverick_only_fire_control():
    """Fire control dei registri; per gli aerei restano le sole opzioni AGM-65D (v. docstring)."""
    registry = make_registry_fire_control()

    def fire_control(shooter, target):
        result = registry(shooter, target)

        if result is None or type(shooter).__name__ != 'Aircraft':
            return result

        options = result if isinstance(result, tuple) else (result,)
        options = tuple(spec for spec in options if spec.weapon == MAVERICK)
        return options or None

    return fire_control


def ifv_only(fire_control):
    """Regola d'ingaggio di missione (stand-in di A4): gli aerei attaccano solo i BMP-2."""
    def restricted(shooter, target):
        if type(shooter).__name__ == 'Aircraft' and getattr(target, '_model', None) != 'BMP-2':
            return None

        return fire_control(shooter, target)

    return restricted


def build(defence_model: str, defence_x: float, defence_y: float, attackers: int):
    red = F.build_force('Red-Line', 'Red', [
        F.Unit('vehicle', 'BMP-2', 3, origin=(0.0, 0.0), step=(0.0, 300.0), prefix='ifv', sensors=VISUAL),
        F.Unit('vehicle', defence_model, 1, origin=(defence_x, defence_y), prefix='ad')])
    cas = F.build_force('Blue-CAS', 'Blue', [
        F.Unit('aircraft', 'A-10C Thunderbolt II', attackers, origin=(-40_000.0, 0.0, 3_000.0),
               step=(0.0, 500.0), prefix='cas', loadout='Maverick/Gun CAS')], mil_category=F.AIR_UNIT)
    return red, cas


def run_variant(session_id: str, defence_model: str, defence_x: float, defence_y: float, attackers: int,
                points, targets_ifv_only: bool = False):
    red, cas = build(defence_model, defence_x, defence_y, attackers)
    fire_control = maverick_only_fire_control()

    if targets_ifv_only:
        fire_control = ifv_only(fire_control)

    # Con la rotta di standoff (virata a x = -11 km e ritorno) la formazione TRASLATA di prima
    # non e' un offset nella terna di marcia: ogni A-10C ha una missione propria.
    missions = F.missions_for(cas, points, mission_type='CAS', target=F.group_target('Red-Line'))
    outcome = F.run(session_id, [cas], [red], fire_control, duration=DURATION, missions=missions,
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
        cls.tor_forward = [run_variant(s, '9K331-Tor', TOR_FORWARD_X, 300.0, 4, OVERFLIGHT, targets_ifv_only=True)
                           for s in cls.SEEDS]

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

    def test_rear_tor_intercepts_standoff_launches(self):
        """Tor arretrato: i Maverick partono fuori dai suoi 12 km, sono bersagli legittimi (L1)."""
        self.assertGreater(sum(_interceptions(o, self.AD) for _, _, o in self.tor_rear), 0)

        for _, cas, outcome in self.tor_rear:
            self.assertTrue(all(d > TOR_ZONE_M for d in launch_distances(cas, outcome, TOR_REAR_X, 300.0)))
            for event in outcome.interception_events:
                with self.subTest(asset=event.asset_id):
                    self.assertEqual((event.asset_id, event.weapon), (self.AD, '9M331-SAM'))

    def test_forward_tor_engages_launchers_inside_its_zone(self):
        """Regola L (regressione): lanci da DENTRO i 12 km del Tor -> il Tor spara ai lanciatori e
        non intercetta i Maverick. Oggi vale per tempistica (v. docstring del modulo)."""
        inside = 0

        for red, cas, outcome in self.tor_forward:
            distances = launch_distances(cas, outcome, TOR_FORWARD_X, 300.0)
            inside += sum(1 for d in distances if d < TOR_ZONE_M)
            with self.subTest(session=outcome.session_id if hasattr(outcome, 'session_id') else None):
                self.assertGreater(_rounds_fired(outcome, self.AD), 0)
                self.assertEqual(_interceptions(outcome, self.AD), 0)

        self.assertGreater(inside, 0)      # premessa: almeno un lancio da dentro la zona

if __name__ == '__main__':
    unittest.main()
