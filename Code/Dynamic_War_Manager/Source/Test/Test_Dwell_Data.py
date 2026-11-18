"""Test dei dati D-5 / DW-9 rivista: `dwell_time_s` (periodo di rivisita della funzione di RICERCA) nei registri reali.

Il piano e' in Analysis/Document/Proposta_Dwell_Estensione_DW9.md; le stime e le bande dei valori non verificati
sono in Analysis/Document/Registro_Dwell_Stimati.md. Le costanti di questo file sono la copia per i test dei valori
decisi (DW9-1..DW9-10) e vanno aggiornate insieme al registro e ai dati.

Blocco 1: SAM e AAA con radar (9 record di `Vehicle_Data`). Blocco 2: SAM con TVD e AAA a vista (6 record).
Blocco 3: EWR rimasti (3 record). I blocchi successivi estendono le costanti.
"""
import sys
import unittest
from unittest.mock import MagicMock, patch

from Code.Dynamic_War_Manager.Source.Asset.Mobile import Mobile
from Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data import Vehicle_Data
from Code.Dynamic_War_Manager.Source.Asset.Ship_Data import Ship_Data  # noqa: F401 (registro caricato per Mobile)
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import Aircraft_Data  # noqa: F401

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


if __name__ == '__main__':
    unittest.main()
