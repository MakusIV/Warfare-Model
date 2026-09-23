"""Tests per Block/Transport.py — costruibilita' del blocco infrastrutturale Transport.

Il costruttore storico passava a Block.__init__ argomenti posizionali non corrispondenti
(acp/rcp/payload, mai esistiti su Block) e chiamava un checkParam inesistente: la classe
non era mai istanziabile. Questi test fissano la firma riallineata a Block/Military
(keyword arguments, prefisso del nome, passthrough dell'id) e la validazione della
sotto-categoria contro Context.BLOCK_INFRASTRUCTURE_ASSET['Transport'].
"""

import unittest

from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Block.Military import Military
from Code.Dynamic_War_Manager.Source.Block.Transport import Transport
from Code.Dynamic_War_Manager.Source.Context.Context import BLOCK_INFRASTRUCTURE_ASSET


class TestTransportConstruction(unittest.TestCase):

    def setUp(self):
        self.block = Transport(name="Alpha", description="Test Transport", side="Red", category="Logistic",
                         sub_category="Railway", functionality="Supply", value=7)

    def test_is_a_non_military_block(self):
        self.assertIsInstance(self.block, Block)
        self.assertNotIsInstance(self.block, Military)
        self.assertEqual(self.block.block_class, "Transport")

    def test_fields_are_assigned(self):
        self.assertEqual(self.block.name, "Transport.Alpha")
        self.assertEqual(self.block.description, "Test Transport")
        self.assertEqual(self.block.side, "Red")
        self.assertEqual(self.block.category, "Logistic")
        self.assertEqual(self.block.sub_category, "Railway")
        self.assertEqual(self.block.functionality, "Supply")
        self.assertEqual(self.block.value, 7)

    def test_default_construction(self):
        """Senza argomenti: nome 'Unnamed_Transport_#nnnn', id generato, sotto-categoria vuota."""
        block = Transport()
        self.assertTrue(block.name.startswith("Unnamed_Transport"))
        self.assertIsInstance(block.id, str)
        self.assertTrue(block.id)
        self.assertEqual(block.sub_category, "")

    def test_constructor_id_explicit(self):
        """Un id esplicito e' usato cosi' com'e' (non sovrascritto da un setId casuale)."""
        first = Transport(name="Same", id="transport_42")
        second = Transport(name="Same", id="transport_42")
        self.assertEqual(first.id, "transport_42")
        self.assertEqual(first.id, second.id)

    def test_constructor_id_default_still_random(self):
        self.assertNotEqual(Transport(name="Same").id, Transport(name="Same").id)

    def test_every_declared_sub_category_is_accepted(self):
        for sub_category in BLOCK_INFRASTRUCTURE_ASSET["Transport"]:
            with self.subTest(sub_category=sub_category):
                self.assertEqual(Transport(sub_category=sub_category).sub_category, sub_category)

    def test_invalid_sub_category_raises(self):
        with self.assertRaises(ValueError):
            Transport(sub_category="Farm")

    def test_block_validation_still_applies(self):
        with self.assertRaises(ValueError):
            Transport(side="Purple")


if __name__ == '__main__':
    unittest.main()
