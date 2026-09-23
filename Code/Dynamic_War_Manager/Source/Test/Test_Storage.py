"""Tests per Block/Storage.py — costruibilita' del blocco infrastrutturale Storage.

Il costruttore storico passava a Block.__init__ argomenti posizionali non corrispondenti
(acp/rcp/payload, mai esistiti su Block) e chiamava un checkParam inesistente: la classe
non era mai istanziabile. Questi test fissano la firma riallineata a Block/Military
(keyword arguments, prefisso del nome, passthrough dell'id) e la validazione della
sotto-categoria contro Context.BLOCK_INFRASTRUCTURE_ASSET['Storage'].
"""

import unittest

from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Block.Military import Military
from Code.Dynamic_War_Manager.Source.Block.Storage import Storage
from Code.Dynamic_War_Manager.Source.Context.Context import BLOCK_INFRASTRUCTURE_ASSET


class TestStorageConstruction(unittest.TestCase):

    def setUp(self):
        self.block = Storage(name="Alpha", description="Test Storage", side="Red", category="Logistic",
                         sub_category="Service", functionality="Supply", value=7)

    def test_is_a_non_military_block(self):
        self.assertIsInstance(self.block, Block)
        self.assertNotIsInstance(self.block, Military)
        self.assertEqual(self.block.block_class, "Storage")

    def test_fields_are_assigned(self):
        self.assertEqual(self.block.name, "Storage.Alpha")
        self.assertEqual(self.block.description, "Test Storage")
        self.assertEqual(self.block.side, "Red")
        self.assertEqual(self.block.category, "Logistic")
        self.assertEqual(self.block.sub_category, "Service")
        self.assertEqual(self.block.functionality, "Supply")
        self.assertEqual(self.block.value, 7)

    def test_default_construction(self):
        """Senza argomenti: nome 'Unnamed_Storage_#nnnn', id generato, sotto-categoria vuota."""
        block = Storage()
        self.assertTrue(block.name.startswith("Unnamed_Storage"))
        self.assertIsInstance(block.id, str)
        self.assertTrue(block.id)
        self.assertEqual(block.sub_category, "")

    def test_constructor_id_explicit(self):
        """Un id esplicito e' usato cosi' com'e' (non sovrascritto da un setId casuale)."""
        first = Storage(name="Same", id="storage_42")
        second = Storage(name="Same", id="storage_42")
        self.assertEqual(first.id, "storage_42")
        self.assertEqual(first.id, second.id)

    def test_constructor_id_default_still_random(self):
        self.assertNotEqual(Storage(name="Same").id, Storage(name="Same").id)

    def test_every_declared_sub_category_is_accepted(self):
        for sub_category in BLOCK_INFRASTRUCTURE_ASSET["Storage"]:
            with self.subTest(sub_category=sub_category):
                self.assertEqual(Storage(sub_category=sub_category).sub_category, sub_category)

    def test_invalid_sub_category_raises(self):
        with self.assertRaises(ValueError):
            Storage(sub_category="Railway")

    def test_block_validation_still_applies(self):
        with self.assertRaises(ValueError):
            Storage(side="Purple")


if __name__ == '__main__':
    unittest.main()
