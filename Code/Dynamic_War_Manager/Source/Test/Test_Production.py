"""Tests per Block/Production.py — costruibilita' del blocco infrastrutturale Production.

Il costruttore storico passava a Block.__init__ argomenti posizionali non corrispondenti
(acp/rcp/payload, mai esistiti su Block) e chiamava un checkParam inesistente: la classe
non era mai istanziabile. Questi test fissano la firma riallineata a Block/Military
(keyword arguments, prefisso del nome, passthrough dell'id) e la validazione della
sotto-categoria contro Context.BLOCK_INFRASTRUCTURE_ASSET['Production'].
"""

import unittest

from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Block.Military import Military
from Code.Dynamic_War_Manager.Source.Block.Production import Production
from Code.Dynamic_War_Manager.Source.Context.Context import BLOCK_INFRASTRUCTURE_ASSET


class TestProductionConstruction(unittest.TestCase):

    def setUp(self):
        self.block = Production(name="Alpha", description="Test Production", side="Red", category="Civilian",
                         sub_category="Factory", functionality="Supply", value=7)

    def test_is_a_non_military_block(self):
        self.assertIsInstance(self.block, Block)
        self.assertNotIsInstance(self.block, Military)
        self.assertEqual(self.block.block_class, "Production")

    def test_fields_are_assigned(self):
        self.assertEqual(self.block.name, "Production.Alpha")
        self.assertEqual(self.block.description, "Test Production")
        self.assertEqual(self.block.side, "Red")
        self.assertEqual(self.block.category, "Civilian")
        self.assertEqual(self.block.sub_category, "Factory")
        self.assertEqual(self.block.functionality, "Supply")
        self.assertEqual(self.block.value, 7)

    def test_default_construction(self):
        """Senza argomenti: nome 'Unnamed_Production_#nnnn', id generato, sotto-categoria vuota."""
        block = Production()
        self.assertTrue(block.name.startswith("Unnamed_Production"))
        self.assertIsInstance(block.id, str)
        self.assertTrue(block.id)
        self.assertEqual(block.sub_category, "")

    def test_constructor_id_explicit(self):
        """Un id esplicito e' usato cosi' com'e' (non sovrascritto da un setId casuale)."""
        first = Production(name="Same", id="production_42")
        second = Production(name="Same", id="production_42")
        self.assertEqual(first.id, "production_42")
        self.assertEqual(first.id, second.id)

    def test_constructor_id_default_still_random(self):
        self.assertNotEqual(Production(name="Same").id, Production(name="Same").id)

    def test_every_declared_sub_category_is_accepted(self):
        for sub_category in BLOCK_INFRASTRUCTURE_ASSET["Production"]:
            with self.subTest(sub_category=sub_category):
                self.assertEqual(Production(sub_category=sub_category).sub_category, sub_category)

    def test_invalid_sub_category_raises(self):
        with self.assertRaises(ValueError):
            Production(sub_category="Road")

    def test_block_validation_still_applies(self):
        with self.assertRaises(ValueError):
            Production(side="Purple")


if __name__ == '__main__':
    unittest.main()
