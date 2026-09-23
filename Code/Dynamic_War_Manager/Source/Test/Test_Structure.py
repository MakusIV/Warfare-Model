"""Tests per Asset/Structure.py — costruibilita' e assegnazione corretta dei campi.

Il costruttore storico aveva due bug:
* passava 17 argomenti POSIZIONALI ad Asset.__init__, che ne ha 18 (manca `production`):
  ogni valore da `position` in poi slittava silenziosamente sul parametro successivo
  (position -> production, volume -> position, crytical -> volume, ...). Corruzione
  silenziosa, non un crash: il test piu' importante qui e' che position/volume/crytical/
  repair_time/role finiscano nei campi giusti;
* chiamava `super.checkParam(...)` sul builtin `super` (AttributeError): la classe non era
  mai istanziabile.
In piu' checkParam leggeva BLOCK_ASSET_CATEGORY[block_class] (chiavi di primo livello
sbagliate: KeyError per ogni blocco reale) e loadAssetDataFromContext iterava un dict
senza .items().
"""

import unittest
from unittest.mock import patch

from sympy import Point2D, Point3D

from Code.Dynamic_War_Manager.Source.Asset.Structure import Structure
from Code.Dynamic_War_Manager.Source.Block.Production import Production
from Code.Dynamic_War_Manager.Source.Block.Transport import Transport
from Code.Dynamic_War_Manager.Source.Context.Context import SHAPE2D, SHAPE3D
from Code.Dynamic_War_Manager.Source.DataType.Area import Area
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload
from Code.Dynamic_War_Manager.Source.DataType.Volume import Volume

_STRUCTURE_LOGGER = 'Code.Dynamic_War_Manager.Source.Asset.Structure.logger'


class TestStructureConstruction(unittest.TestCase):

    def setUp(self):
        self.block = Transport(name='Railhead', side='Red', category='Logistic',
                               sub_category='Railway', id='railhead')
        self.position = Point3D(1200, -350, 15)
        self.volume = Volume(area_base=Area(shape=SHAPE2D.CIRCLE, radius=4.0, center=Point2D(0, 0)),
                             volume_shape=SHAPE3D.CYLINDER)
        self.acp = Payload(goods=5, energy=2, hr=1, hc=0, hs=0, hb=0)
        self.rcp = Payload(goods=1, energy=1, hr=0, hc=0, hs=0, hb=3)
        self.payload = Payload(goods=9, energy=0, hr=0, hc=0, hs=0, hb=0)

        self.structure = Structure(block=self.block, name='Bridge-1', description='Rail bridge',
                                   category='Railway', asset_type='Bridge', functionality='Crossing',
                                   cost=1000, value=8, acp=self.acp, rcp=self.rcp, payload=self.payload,
                                   position=self.position, volume=self.volume, crytical=True,
                                   repair_time=5, role='Infrastructure',
                                   physical_characteristics={'length': 120, 'width': 8, 'height': 12})

    def test_base_fields(self):
        s = self.structure
        self.assertIs(s.block, self.block)
        self.assertEqual(s.name, 'Bridge-1')
        self.assertEqual(s.description, 'Rail bridge')
        self.assertEqual(s.category, 'Railway')
        self.assertEqual(s.asset_type, 'Bridge')
        self.assertEqual(s.functionality, 'Crossing')
        self.assertEqual(s.cost, 1000)
        self.assertEqual(s.value, 8)

    def test_fields_after_the_old_shift_point_are_not_shifted(self):
        """Non-regressione del bug silenzioso: position/volume/crytical/repair_time/role
        nei loro campi, e production NON riceve la position."""
        s = self.structure
        self.assertEqual(s.position, self.position)
        self.assertIs(s.volume, self.volume)
        self.assertIs(s.crytical, True)
        self.assertEqual(s.repair_time, 5)
        self.assertEqual(s.role, 'Infrastructure')
        self.assertIsInstance(s.production, Payload)
        self.assertEqual(s.production.goods, 0)

    def test_acp_rcp_map_to_asset_resources(self):
        self.assertIs(self.structure.resources_assigned, self.acp)
        self.assertIs(self.structure.resources_to_self_consume, self.rcp)
        self.assertIs(self.structure.payload, self.payload)

    def test_physical_characteristics(self):
        self.assertEqual(self.structure.physical_characteristics['length'], 120)
        self.assertIsNone(Structure(block=self.block, category='Railway').physical_characteristics)

    def test_minimal_construction(self):
        """Solo il blocco: nome di default, nessun asset_type (dato mancante, non errore)."""
        s = Structure(block=self.block)
        self.assertTrue(s.name.startswith('Unnamed_Structure'))
        self.assertIsNone(s.asset_type)
        self.assertIsNone(s.position)

    def test_asset_type_table_follows_the_owner_block_class(self):
        farm = Production(name='Kolkhoz', side='Red', sub_category='Farm')
        s = Structure(block=farm, category='Farm', asset_type='Farm')
        self.assertEqual(s.asset_type, 'Farm')

    def test_invalid_asset_type_raises(self):
        with self.assertRaises(ValueError):
            Structure(block=self.block, category='Railway', asset_type='Runway')

    def test_asset_type_without_infrastructure_table_is_logged_not_raised(self):
        """Categoria fuori tabella: asset_type non validabile -> warning, oggetto costruito."""
        with patch(_STRUCTURE_LOGGER) as mock_logger:
            s = Structure(block=self.block, category='Unknown', asset_type='Bridge')
        self.assertEqual(s.asset_type, 'Bridge')
        mock_logger.warning.assert_called()

    def test_check_param_returns_tuple(self):
        self.assertEqual(self.structure.checkParam('Station'), (True, 'OK'))
        self.assertFalse(self.structure.checkParam(None)[0])


class TestStructureLoadAssetDataFromContext(unittest.TestCase):

    def test_iterates_items_of_the_category_table(self):
        """Prima iterava le chiavi (stringhe) spacchettandole in (k, v): ValueError.
        Con un asset_type assente dalla tabella ora scorre le voci e restituisce False."""
        block = Transport(name='Railhead', sub_category='Railway')
        s = Structure(block=block, category='Railway')
        self.assertFalse(s.loadAssetDataFromContext())


if __name__ == '__main__':
    unittest.main()
