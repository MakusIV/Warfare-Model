"""Tests per Block/Urban.py — costruibilita' del blocco infrastrutturale Urban.

Il costruttore storico passava a Block.__init__ argomenti posizionali non corrispondenti
(acp/rcp/payload, mai esistiti su Block) e chiamava un checkParam inesistente: la classe
non era mai istanziabile. Questi test fissano la firma riallineata a Block/Military
(keyword arguments, prefisso del nome, passthrough dell'id) e la validazione della
sotto-categoria contro Context.BLOCK_INFRASTRUCTURE_ASSET['Urban'].
"""

import unittest

from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Block.Military import Military
from Code.Dynamic_War_Manager.Source.Block.Urban import Urban
from Code.Dynamic_War_Manager.Source.Context.Context import BLOCK_INFRASTRUCTURE_ASSET


class TestUrbanConstruction(unittest.TestCase):

    def setUp(self):
        self.block = Urban(name="Alpha", description="Test Urban", side="Red", category="Civilian",
                         sub_category="Civilian", functionality="Supply", value=7)

    def test_is_a_non_military_block(self):
        self.assertIsInstance(self.block, Block)
        self.assertNotIsInstance(self.block, Military)
        self.assertEqual(self.block.block_class, "Urban")

    def test_fields_are_assigned(self):
        self.assertEqual(self.block.name, "Urban.Alpha")
        self.assertEqual(self.block.description, "Test Urban")
        self.assertEqual(self.block.side, "Red")
        self.assertEqual(self.block.category, "Civilian")
        self.assertEqual(self.block.sub_category, "Civilian")
        self.assertEqual(self.block.functionality, "Supply")
        self.assertEqual(self.block.value, 7)

    def test_default_construction(self):
        """Senza argomenti: nome 'Unnamed_Urban_#nnnn', id generato, sotto-categoria vuota."""
        block = Urban()
        self.assertTrue(block.name.startswith("Unnamed_Urban"))
        self.assertIsInstance(block.id, str)
        self.assertTrue(block.id)
        self.assertEqual(block.sub_category, "")

    def test_constructor_id_explicit(self):
        """Un id esplicito e' usato cosi' com'e' (non sovrascritto da un setId casuale)."""
        first = Urban(name="Same", id="urban_42")
        second = Urban(name="Same", id="urban_42")
        self.assertEqual(first.id, "urban_42")
        self.assertEqual(first.id, second.id)

    def test_constructor_id_default_still_random(self):
        self.assertNotEqual(Urban(name="Same").id, Urban(name="Same").id)

    def test_every_declared_sub_category_is_accepted(self):
        for sub_category in BLOCK_INFRASTRUCTURE_ASSET["Urban"]:
            with self.subTest(sub_category=sub_category):
                self.assertEqual(Urban(sub_category=sub_category).sub_category, sub_category)

    def test_invalid_sub_category_raises(self):
        with self.assertRaises(ValueError):
            Urban(sub_category="Factory")

    def test_block_validation_still_applies(self):
        with self.assertRaises(ValueError):
            Urban(side="Purple")


if __name__ == '__main__':
    unittest.main()
