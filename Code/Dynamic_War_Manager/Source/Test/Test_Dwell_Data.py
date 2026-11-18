"""Test dei dati D-5 / DW-9 rivista: `dwell_time_s` (periodo di rivisita della funzione di RICERCA) nei registri reali.

Il piano e' in Analysis/Document/Proposta_Dwell_Estensione_DW9.md; le stime e le bande dei valori non verificati
sono in Analysis/Document/Registro_Dwell_Stimati.md. Le costanti di questo file sono la copia per i test dei valori
decisi (DW9-1..DW9-10) e vanno aggiornate insieme al registro e ai dati.

Blocco 1: SAM e AAA con radar (9 record di `Vehicle_Data`). Blocco 2: SAM con TVD e AAA a vista (6 record).
Blocco 3: EWR rimasti (3 record). Blocco 4: navi (22 record con valore, 1 senza). Blocco 5: AWACS (3 record) e test di
completezza del perimetro (SAM/AAA, TVD/vista, EWR, navi, AWACS).
"""
import contextlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from Code.Dynamic_War_Manager.Source.Asset.Mobile import Mobile
from Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data import Vehicle_Data
from Code.Dynamic_War_Manager.Source.Asset.Ship_Data import Ship_Data
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import Aircraft_Data
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Test.Test_EWR_Data import EWR_DWELL_S, EWR_WITHOUT_DWELL

_MOBILE_LOGGER = 'Code.Dynamic_War_Manager.Source.Asset.Mobile.logger'
# Modulo che contiene davvero Mobile (le globali lette dai lettori D-5, es. l'interruttore D4C_VISUAL_SENSOR)
_mobile_module = sys.modules[Mobile.__module__]

# D-5, DW-9 rivista: periodo di rivisita [s] della funzione di ricerca, per (registro, modello, sensore).
SAM_AAA_DWELL_S = {
    'ZSU-23-4-Shilka': 7.3, 'Flakpanzer-Gepard': 1.0, '2K22-Tunguska': 1.82, '9A33-Osa': 1.82,
    'MIM-115-Roland': 1.0, '9K331-Tor': 3.0, '2K12-Kub': 3.5, '9K37-Buk': 9.0, 'S-300PS': 12.0,
}
# Modelli con valore STIMATO [S] (registro Analysis/Document/Registro_Dwell_Stimati.md).
DWELL_ESTIMATED = {'ZSU-23-4-Shilka', '2K22-Tunguska', '9K37-Buk', 'S-300PS'}

# [S] Poe 1974, centrale della banda 1,75-6,0 s; APPROSSIMAZIONE (DW9-6).
VISUAL_DWELL_S = 3.2
TVD_MODELS = ('Strela-1-9P31', 'MIM-72G-Chaparral', '9K35-Strela-10', 'M6-Linebacker')
VISUAL_MODELS = ('ZSU-57-2', 'M163-VADS')
DWELL_ESTIMATED |= set(TVD_MODELS) | set(VISUAL_MODELS)

# EWR rimasti senza valore (blocco 3): stime per confronto [S] (DW9-8).
DWELL_ESTIMATED |= {'FuMG-80-Freya', 'Wassermann', 'AN-FPS-117'}

# I 10 EWR riallineati (blocco 3bis): salvo AMES-Type-80 (interpretazione [S]) sono valori di fonte, non stime.
DWELL_ESTIMATED |= {'AMES-Type-80'}

# Navi (blocco 4): chiavi = `model` del registro `Ship_Data`; valori 5.0 (AN/SPS-49 e analoghi, SPY-1), 7.1 (Fregat-MA
# e analoghi), 10.0 (Top Pair), 2.0 (Type 382, Type 364).
SHIP_DWELL_S = {
    'CVN-70 Carl Vinson': 5.0, 'CVN-71 Theodore Roosevelt': 5.0, 'CVN-72 Abraham Lincoln': 5.0,
    'CVN-73 George Washington': 5.0, 'CVN-74 John C. Stennis': 5.0, 'CVN-75 Harry S. Truman': 5.0,
    'CV-59 USS Forrestal': 5.0, 'CV 1143.5 Admiral Kuznetsov': 7.1, 'USS Arleigh Burke IIa': 5.0,
    'Type 052B Guangzhou-class': 7.1, 'Type 052C': 5.0, 'CG-65': 5.0, 'CGN 1144.2 Piotr Velikiy': 7.1,
    'CG 1164 Moskva': 10.0, 'FFG-46': 5.0, 'FF 1135M Rezky': 7.1, 'FFG 11540 Neustrashimy': 7.1,
    'Type 054A': 2.0, 'FFL 1124.4 Grisha': 7.1, 'FSG 1241.1MP Molniya': 7.1, 'LHA-1 Tarawa': 5.0, 'Type 071': 2.0,
}
# Modelli senza valore e motivo (completo: i 2 EWR senza valore e il sottomarino).
NO_DWELL = {
    'Chain-Home': 'illuminazione continua', 'Mammut': "schiera fissa senza cadenza ne' analogo",
    'Type 093': 'sonar passivo',
}
# Navi con valore STIMATO [S] (10 modelli).
DWELL_ESTIMATED |= {
    'CV-59 USS Forrestal', 'USS Arleigh Burke IIa', 'Type 052B Guangzhou-class', 'Type 052C', 'CG-65',
    'FF 1135M Rezky', 'Type 054A', 'FFL 1124.4 Grisha', 'FSG 1241.1MP Molniya', 'LHA-1 Tarawa',
}

# AWACS (blocco 5): 6 giri/min -> 10 s; l'A-50 e' FONTE DEBOLE [S] (fonte divulgativa unica, coincide con l'E-3A).
AWACS_DWELL_S = {'E-3A Sentry': 10.0, 'E-2D Advanced Hawkeye': 10.0, 'A-50': 10.0}
DWELL_ESTIMATED |= {'A-50'}

# Chiave documentale `search_model` (DW9-2 = A2, tabella di §2.7 della Proposta), per modello.
SEARCH_MODEL = {
    'ZSU-23-4-Shilka': '1RL33 (search mode)', 'Flakpanzer-Gepard': 'MPDR-12', '2K22-Tunguska': '1RL144 Hot Shot',
    '9A33-Osa': 'Land Roll acquisition antenna', 'MIM-115-Roland': 'MPDR-16',
    '9K331-Tor': 'Scrum Half surveillance radar (all-round view)', '2K12-Kub': '1S11', '9K37-Buk': '9S18 Tube Arm',
    'S-300PS': '5N64S Big Bird-B',
    'Strela-1-9P31': 'crew visual search', 'MIM-72G-Chaparral': 'crew visual search',
    '9K35-Strela-10': 'crew visual search', 'M6-Linebacker': 'crew visual search',
    'ZSU-57-2': 'crew visual search', 'M163-VADS': 'crew visual search',
    'FuMG-80-Freya': 'FuMG 80 Freya', 'Wassermann': 'Wassermann', 'AN-FPS-117': 'AN/FPS-117',
    'SCR-270': 'SCR-270', 'P-12-Yenisei': 'P-12', 'P-18-Terek': 'P-18', 'P-37-Mech': 'P-37', '1L13-Nebo-SV': '1L13',
    '55Zh6-Nebo': '55Zh6', 'AN-TPS-43': 'AN/TPS-43', 'AMES-Type-7': 'AMES Type 7', 'AMES-Type-80': 'AMES Type 80',
    'P-14-Lena': 'P-14',
    'CVN-70 Carl Vinson': 'AN/SPS-49', 'CVN-71 Theodore Roosevelt': 'AN/SPS-49', 'CVN-72 Abraham Lincoln': 'AN/SPS-49',
    'CVN-73 George Washington': 'AN/SPS-49', 'CVN-74 John C. Stennis': 'AN/SPS-49',
    'CVN-75 Harry S. Truman': 'AN/SPS-49', 'FFG-46': 'AN/SPS-49',
    'CV-59 USS Forrestal': 'AN/SPS-43', 'LHA-1 Tarawa': 'AN/SPS-52',
    'CV 1143.5 Admiral Kuznetsov': 'Fregat-MA (MR-750)', 'FFG 11540 Neustrashimy': 'Fregat-MA (MR-750)',
    'CGN 1144.2 Piotr Velikiy': 'Fregat-MA (MR-750)', 'CG 1164 Moskva': 'MR-800 Top Pair',
    'USS Arleigh Burke IIa': 'AN/SPY-1D', 'CG-65': 'AN/SPY-1A',
    'Type 052B Guangzhou-class': 'Type 381', 'Type 052C': 'Type 346', 'Type 054A': 'Type 382', 'Type 071': 'Type 364',
    'FF 1135M Rezky': 'Head Net-C (MR-310U)', 'FFL 1124.4 Grisha': 'MR-302 Strut Curve',
    'FSG 1241.1MP Molniya': 'Band Stand (MR-331)',
    'E-3A Sentry': 'AN/APY-2', 'E-2D Advanced Hawkeye': 'AN/APY-9', 'A-50': 'Shmel',
}

# Sensori dizionario di un record (radar, TVD e vista; nei registri che non hanno l'attributo, ignorato).
_SENSOR_ATTRS = ('radar', 'TVD', 'visual')


def _sensor_dicts(record):
    """[(nome attributo, dizionario)] dei sensori-dizionario del record."""
    return [(a, getattr(record, a)) for a in _SENSOR_ATTRS if isinstance(getattr(record, a, None), dict)]


def _dwell_values(record):
    """Valori di `dwell_time_s` dichiarati dai sensori del record (lista vuota se nessuno)."""
    return [d['dwell_time_s'] for _, d in _sensor_dicts(record) if 'dwell_time_s' in d]


class _DwellReader:
    """Lettori D-5 di Mobile su un modello del registro reale (nessun Mobile costruito)."""
    detection_dwell_time = Mobile.detection_dwell_time
    sensor_dwell_time = Mobile.sensor_dwell_time
    _detection_registry_record = Mobile._detection_registry_record
    _sensor_range_km = staticmethod(Mobile._sensor_range_km)
    _sensor_dwell_s = staticmethod(Mobile._sensor_dwell_s)

    def __init__(self, model):
        self._model = model


class TestSamAaaDwell(unittest.TestCase):
    """DW-9 blocco 1: SAM e AAA con radar di ricerca."""

    def setUp(self):
        self._log = patch(_MOBILE_LOGGER, MagicMock())
        self._log.start()

    def tearDown(self):
        self._log.stop()

    def test_radar_dwell_values(self):
        for model, value in SAM_AAA_DWELL_S.items():
            with self.subTest(model=model):
                self.assertEqual(Vehicle_Data._registry[model].radar['dwell_time_s'], value)

    def test_the_dwell_is_read_with_the_acquisition_range(self):
        for model, value in SAM_AAA_DWELL_S.items():
            with self.subTest(model=model):
                reader = _DwellReader(model)
                # Lettura di default: range_type='acquisition_range', quella del motore.
                self.assertEqual(reader.detection_dwell_time('air'), value)
                self.assertEqual(reader.sensor_dwell_time('radar'), value)

        # Buk: il dwell e' quello della ricerca 9S18, a cui si riferisce la portata di acquisizione di 85 km.
        buk = Vehicle_Data._registry['9K37-Buk'].radar
        self.assertEqual(buk['capabilities']['air'][1]['acquisition_range'], 85)


class TestVisualAndTvdDwell(unittest.TestCase):
    """DW-9 blocco 2: SAM con TVD e AAA a vista (stesso valore stimato [S], DW9-6)."""

    def setUp(self):
        self._log = patch(_MOBILE_LOGGER, MagicMock())
        self._log.start()

    def tearDown(self):
        self._log.stop()

    def test_tvd_and_visual_values(self):
        for model in TVD_MODELS:
            with self.subTest(model=model, sensor='TVD'):
                record = Vehicle_Data._registry[model]
                self.assertEqual(record.TVD['dwell_time_s'], VISUAL_DWELL_S)
                self.assertFalse(record.radar)
        for model in VISUAL_MODELS:
            with self.subTest(model=model, sensor='visual'):
                record = Vehicle_Data._registry[model]
                self.assertEqual(record.visual['dwell_time_s'], VISUAL_DWELL_S)
                self.assertFalse(record.radar)

    def test_visual_dwell_follows_the_visual_switch(self):
        self.assertEqual(_DwellReader('ZSU-57-2').detection_dwell_time('air'), VISUAL_DWELL_S)
        with patch.object(_mobile_module, 'D4C_VISUAL_SENSOR', False):
            self.assertIsNone(_DwellReader('ZSU-57-2').detection_dwell_time('air'))


class TestShipDwell(unittest.TestCase):
    """DW-9 blocco 4: navi (ricerca aerea del dizionario `radar`)."""

    def test_ship_radar_dwell_values(self):
        for model, value in SHIP_DWELL_S.items():
            with self.subTest(model=model):
                self.assertEqual(Ship_Data._registry[model].radar['dwell_time_s'], value)

    def test_submarine_has_no_dwell(self):
        self.assertIn('Type 093', NO_DWELL)
        self.assertNotIn('dwell_time_s', Ship_Data._registry['Type 093'].radar)


class TestDwellScope(unittest.TestCase):
    """DW-9 blocco 5: AWACS e completezza del perimetro (nessun record con dwell fuori regola)."""

    def test_awacs_dwell_values(self):
        for model, value in AWACS_DWELL_S.items():
            with self.subTest(model=model):
                self.assertEqual(Aircraft_Data._registry[model].radar['dwell_time_s'], value)

    def test_non_awacs_aircraft_declare_no_dwell(self):
        # Decisione 1 dell'utente: il dwell di ricerca non si dichiara per gli altri aerei, nemmeno nel loro TVD.
        for model, record in Aircraft_Data._registry.items():
            if model in AWACS_DWELL_S:
                continue
            for attr in ('radar', 'TVD'):
                sensor = getattr(record, attr, None)
                if isinstance(sensor, dict):
                    with self.subTest(model=model, sensor=attr):
                        self.assertNotIn('dwell_time_s', sensor)

    def test_every_sensor_in_scope_has_a_value_or_a_reason(self):
        scope = {model for model, record in Vehicle_Data._registry.items() if _sensor_dicts(record)}
        scope |= set(Ship_Data._registry)
        scope |= set(AWACS_DWELL_S)
        expected = {}
        for table in (SAM_AAA_DWELL_S, EWR_DWELL_S, SHIP_DWELL_S, AWACS_DWELL_S):
            expected.update(table)
        for model in TVD_MODELS + VISUAL_MODELS:
            expected[model] = VISUAL_DWELL_S
        registries = (Vehicle_Data._registry, Ship_Data._registry, Aircraft_Data._registry)

        with_value = {}
        for model in scope:
            for registry in registries:
                if model in registry:
                    values = _dwell_values(registry[model])
                    if values:
                        with_value[model] = values
        out_of_rule = sorted(
            [m for m in with_value if m in NO_DWELL]                       # ha un valore ma e' in NO_DWELL
            + [m for m in scope if m not in with_value and m not in NO_DWELL]   # ne' valore ne' motivo
            + [m for m in NO_DWELL if m not in scope])                     # motivo per un modello fuori perimetro
        self.assertEqual(out_of_rule, [], f'modelli fuori regola: {out_of_rule}')
        self.assertTrue(set(EWR_WITHOUT_DWELL) <= set(NO_DWELL))
        self.assertTrue(DWELL_ESTIMATED <= set(with_value), sorted(DWELL_ESTIMATED - set(with_value)))
        self.assertEqual({m: set(v) for m, v in with_value.items()}, {m: {v} for m, v in expected.items()})

    def test_every_dwell_names_its_search_radar(self):
        # DW9-2 = A2: `search_model` e' documentale, ma presente se e solo se c'e' `dwell_time_s`.
        found = {}
        for registry in (Vehicle_Data._registry, Ship_Data._registry, Aircraft_Data._registry):
            for model, record in registry.items():
                for attr, sensor in _sensor_dicts(record):
                    with self.subTest(model=model, sensor=attr):
                        if 'dwell_time_s' in sensor:
                            self.assertIsInstance(sensor.get('search_model'), str)
                            self.assertTrue(sensor['search_model'])
                            found[model] = sensor['search_model']
                        else:
                            self.assertNotIn('search_model', sensor)
        self.assertEqual(found, SEARCH_MODEL)


class TestDwellOfTwoSensorRecord(unittest.TestCase):
    """S36 (W1): il sensore vincente su un record REALE con due sensori a portata aria (F-16C Block 52d: radar e TVD).

    Nessun record dei registri ha due sensori a portata aria E un dwell (gli aerei non dichiarano dwell, DW-9 decisione
    1: `test_non_awacs_aircraft_declare_no_dwell` resta vero perche' i patch sono ripristinati), quindi i dwell sono
    VALORI DI PROVA, non dati. Qui si fissa quale dei due legge il motore."""

    TWO_SENSOR_MODEL = 'F-16C Block 52d'
    TEST_RADAR_DWELL_S = 6.0     # VALORE DI PROVA (non un dato): radar AN/APG-68, portata aria di acquisizione 70 km
    TEST_TVD_DWELL_S = 2.0       # VALORE DI PROVA (non un dato): TVD LITENING, portata aria di acquisizione 110 km

    def setUp(self):
        self._log = patch(_MOBILE_LOGGER, MagicMock())
        self._log.start()

    def tearDown(self):
        self._log.stop()

    def _test_dwells(self):
        """Context manager: dwell di prova su radar e TVD del record (ripristinati all'uscita)."""
        record = Aircraft_Data._registry[self.TWO_SENSOR_MODEL]
        stack = contextlib.ExitStack()
        stack.enter_context(patch.dict(record.radar, {'dwell_time_s': self.TEST_RADAR_DWELL_S}))
        stack.enter_context(patch.dict(record.TVD, {'dwell_time_s': self.TEST_TVD_DWELL_S}))
        return stack

    @staticmethod
    def _acquisition(sensor, mode):
        return sensor['capabilities'][mode][1]['acquisition_range']

    @staticmethod
    def _tracking(sensor, mode):
        return sensor['capabilities'][mode][1]['tracking_range']

    def test_dwell_follows_the_acquisition_winner_of_a_real_record(self):
        """Con la portata di acquisizione vince il TVD (aria 110 contro 70 km, terra 95 contro 55): il dwell letto e'
        il suo (2,0 s), non quello del radar (6,0 s); i patch sono ripristinati all'uscita."""
        record = Aircraft_Data._registry[self.TWO_SENSOR_MODEL]
        self.assertEqual((self._acquisition(record.radar, 'air'), self._acquisition(record.TVD, 'air')), (70, 110))
        self.assertEqual((self._acquisition(record.radar, 'ground'), self._acquisition(record.TVD, 'ground')), (55, 95))

        with self._test_dwells():
            reader = _DwellReader(self.TWO_SENSOR_MODEL)
            self.assertEqual(reader.detection_dwell_time('air'), self.TEST_TVD_DWELL_S)
            self.assertEqual(reader.detection_dwell_time('ground'), self.TEST_TVD_DWELL_S)
            self.assertEqual(reader.sensor_dwell_time('radar'), self.TEST_RADAR_DWELL_S)

        self.assertNotIn('dwell_time_s', record.radar)
        self.assertNotIn('dwell_time_s', record.TVD)

    def test_registry_reader_ignores_the_tracking_winner(self):
        """LIMITE NOTO: con `tracking_range` vincerebbe il radar (aria 150 contro 90 km, dwell 6,0 s), ma
        `registry_dwell_time` (`Logic/Engagement_Resolver.py:1307`) non passa `range_type` e legge sempre il vincitore
        di ACQUISIZIONE (2,0 s). Una sessione con `range_type='tracking_range'` userebbe quindi la portata del radar e il
        dwell del TVD. Il test fissa il comportamento attuale: va cambiato insieme al limite."""
        record = Aircraft_Data._registry[self.TWO_SENSOR_MODEL]
        self.assertEqual((self._tracking(record.radar, 'air'), self._tracking(record.TVD, 'air')), (150, 90))

        with self._test_dwells():
            reader = _DwellReader(self.TWO_SENSOR_MODEL)
            self.assertEqual(reader.detection_dwell_time('air', range_type='tracking_range'), self.TEST_RADAR_DWELL_S)
            self.assertEqual(ER.registry_dwell_time(reader, None, 'air'), self.TEST_TVD_DWELL_S)


if __name__ == '__main__':
    unittest.main()
