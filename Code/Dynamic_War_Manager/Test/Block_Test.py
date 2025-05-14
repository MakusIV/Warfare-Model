import unittest
from unittest.mock import Mock, MagicMock
from sympy import Point
from Code.Dynamic_War_Manager.Source.Block import Block
from Code.Dynamic_War_Manager.Source.Event import Event
from Code.Dynamic_War_Manager.Source.Payload import Payload
from Code.Context import SIDE, BLOCK_CATEGORY
from typing import TYPE_CHECKING
from Code.Dynamic_War_Manager.Source.Region import Region
from Code.Dynamic_War_Manager.Source.Asset import Asset
# Forza TYPE_CHECKING a True per eseguire le importazioni condizionali
#TYPE_CHECKING = True

#if TYPE_CHECKING:
#    from Code.Dynamic_War_Manager.Source.Asset import Asset
   

class TestBlock(unittest.TestCase):
    def setUp(self):
        # Creazione di un mock per Region
        self.mock_region = Region(name = "Test Region", description="nothong", blocks =  None, limes = None)  #Mock(spec = Region)
        #self.mock_region.name = "Test Region"
        
        
        
        # Creazione di un mock per Event
        self.mock_event = Event("event 1") #Mock(spec=Event)
        #self.mock_event.name = "Test Event"
        
        # Creazione di un'istanza di Block per i test
        self.block = Block(
            name="Test Block",
            description="Test Description",
            side="Blue",
            category="Military",
            sub_category="Stronghold",
            functionality="Defense",
            value=100.0,
            region=self.mock_region
        )
        
        # Creazione di un mock per Asset
        self.mock_asset = Asset(self.block, name = "Test Asset", cost=100) #Mock(spec=Asset)
        #self.mock_asset.name = "Test Asset"
        #self.mock_asset.cost = 100
        #self.mock_asset.efficiency = 0.8 è calcolato
        #self.mock_asset.balance_trade = 1.2è calcolato
        self.mock_asset.position = Point(0, 0, 0)

        # Configurazione dei mock per i payload
        self.mock_payload = Payload() #Mock(spec=Payload)
        self.mock_payload.energy = 10
        self.mock_payload.goods = 5
        self.mock_payload.hr = 3
        self.mock_payload.hc = 2
        self.mock_payload.hs = 1
        self.mock_payload.hb = 0
        
        self.mock_asset.acp = self.mock_payload
        self.mock_asset.rcp = self.mock_payload
        self.mock_asset.payload = self.mock_payload

    def test_initialization(self):
        self.assertEqual(self.block.name, "Block.Test Block")
        self.assertIsNotNone(self.block.id)
        self.assertEqual(self.block.description, "Test Description")
        self.assertEqual(self.block.side, "Blue")
        self.assertEqual(self.block.category, "Military")
        self.assertEqual(self.block.sub_category, "Stronghold")
        self.assertEqual(self.block.functionality, "Defense")
        self.assertEqual(self.block.cost, 100.0)
        self.assertEqual(self.block.region, self.mock_region)
        
    def test_initialization_with_defaults(self):
        block = Block(
            name=None,
            description=None,
            side=None,
            category=None,
            sub_category=None,
            functionality=None,
            value=None,
            region=None
        )
        self.assertTrue(block.name.startswith("Unnamed"))
        self.assertEqual(block.side, "Neutral")
        
    def test_property_setters(self):
        self.block.name = "New Name"
        self.assertEqual(self.block.name, "New Name")
        
        self.block.description = "New Description"
        self.assertEqual(self.block.description, "New Description")
        
        self.block.side = "Red"
        self.assertEqual(self.block.side, "Red")
        
        self.block.category = "Logistic"
        self.assertEqual(self.block.category, "Logistic")
        
        self.block.sub_category = "Airport"
        self.assertEqual(self.block.sub_category, "Airport")
        
        self.block.functionality = "Transport"
        self.assertEqual(self.block.functionality, "Transport")
        
        self.block.value = 200.0
        self.assertEqual(self.block.value, 200.0)
        
    def test_invalid_property_setters(self):
        with self.assertRaises(Exception):
            self.block.side = "Invalid Side"
            
        with self.assertRaises(Exception):
            self.block.category = "Invalid Category"
            
        with self.assertRaises(Exception):
            self.block.value = "Not a float"
            
    def test_assets_management(self):
        # Test aggiunta asset
        self.block.setAsset("asset1", self.mock_asset)
        self.assertIn("asset1", self.block.assets)
        self.assertEqual(self.block.assets["asset1"], self.mock_asset)
        
        # Test lista chiavi
        self.assertEqual(self.block.listAssetKeys(), ["asset1"])
        
        # Test get asset
        self.assertEqual(self.block.getAsset("asset1"), self.mock_asset)
        
        # Test rimozione asset
        self.block.removeAsset("asset1")
        self.assertNotIn("asset1", self.block.assets)
        
    def test_events_management(self):
        # Test aggiunta evento
        self.block.addEvent(self.mock_event)
        self.assertEqual(len(self.block.events), 1)
        
        # Test get ultimo evento
        last_event = self.block.getLastEvent()
        self.assertEqual(last_event, self.mock_event)
        
        # Test get evento per indice
        event = self.block.getEvent(0)
        self.assertEqual(event, self.mock_event)
        
        # Test rimozione evento
        self.block.removeEvent(self.mock_event)
        self.assertEqual(len(self.block.events), 0)
        
    def test_cost_property(self):
        self.block.setAsset("asset1", self.mock_asset)
        self.block.setAsset("asset2", self.mock_asset)
        self.assertEqual(self.block.cost, 200)
        
    def test_position_property(self):
        self.block.setAsset("asset1", self.mock_asset)
        self.block.setAsset("asset2", self.mock_asset)
        position = self.block.position
        self.assertEqual(position, Point(0, 0))
        
    def test_efficiency_property(self):
        self.block.setAsset("asset1", self.mock_asset)
        self.block.setAsset("asset2", self.mock_asset)
        self.assertEqual(self.block.efficiency, 0.8)
        
    def test_balance_trade_property(self):
        self.block.setAsset("asset1", self.mock_asset)
        self.block.setAsset("asset2", self.mock_asset)
        self.assertEqual(self.block.balance_trade, 1.2)
        
    def test_isMilitary(self):
        self.assertTrue(self.block.isMilitary())
        self.block.category = "Civilian"
        self.assertFalse(self.block.isMilitary())
        
    def test_isLogistic(self):
        self.block.category = "Production"
        self.assertTrue(self.block.isLogistic())
        self.block.category = "Storage"
        self.assertTrue(self.block.isLogistic())
        self.block.category = "Transport"
        self.assertTrue(self.block.isLogistic())
        self.block.category = "Military"
        self.assertFalse(self.block.isLogistic())
        
    def test_isCivilian(self):
        self.block.category = "Urban"
        self.assertTrue(self.block.isCivilian())
        self.block.category = "Military"
        self.assertFalse(self.block.isCivilian())
        
    def test_toString(self):
        string = self.block.toString()
        self.assertIn("Test Block", string)
        self.assertIn("Test Description", string)
        self.assertIn("Military", string)
        
    def test_repr(self):
        repr_str = repr(self.block)
        self.assertIn("Test Block", repr_str)
        self.assertIn("Blue", repr_str)
        self.assertIn("Military", repr_str)
        
    def test_str(self):
        str_rep = str(self.block)
        self.assertIn("Block Information", str_rep)
        self.assertIn("Test Block", str_rep)
        self.assertIn("Blue", str_rep)
        
    def test_checkParam(self):
        # Test con parametri validi
        result, message = self.block.checkParam(
            name="Valid",
            description="Valid",
            side="Blue",
            category="Military",
            sub_category="Stronghold",
            function="Defense",
            value=100.0,
            position=Point(0, 0),
            acp=self.mock_payload,
            rcp=self.mock_payload,
            payload=self.mock_payload,
            region=self.mock_region
        )
        self.assertTrue(result)
        self.assertEqual(message, "OK")
        
        # Test con parametri non validi
        result, message = self.block.checkParam(side="Invalid")
        self.assertFalse(result)
        self.assertIn("Bad Arg: side must be a str with value", message)

if __name__ == '__main__':
    unittest.main()