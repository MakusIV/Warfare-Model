import unittest
from typing import Any
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload  # Replace with actual import path

class TestPayload(unittest.TestCase):
    def setUp(self):
        """Initialize test payloads"""
        self.payload1 = Payload(goods=100, energy=50, hr=10, hc=5, hs=3, hb=20)
        self.payload2 = Payload(goods=50, energy=25, hr=5, hc=2, hs=1, hb=10)
        self.payload_empty = Payload()
        self.payload_partial = Payload(goods=75, hr=8)

    def test_initialization(self):
        """Test initialization with different parameters"""
        # Test full initialization
        self.assertEqual(self.payload1.goods, 100)
        self.assertEqual(self.payload1.energy, 50)
        self.assertEqual(self.payload1.hr, 10)
        self.assertEqual(self.payload1.hc, 5)
        self.assertEqual(self.payload1.hs, 3)
        self.assertEqual(self.payload1.hb, 20)

        # Test empty initialization
        self.assertEqual(self.payload_empty.goods, 0)
        self.assertEqual(self.payload_empty.energy, 0)
        self.assertEqual(self.payload_empty.hr, 0)
        self.assertEqual(self.payload_empty.hc, 0)
        self.assertEqual(self.payload_empty.hs, 0)
        self.assertEqual(self.payload_empty.hb, 0)

        # Test partial initialization
        self.assertEqual(self.payload_partial.goods, 75)
        self.assertEqual(self.payload_partial.hr, 8)
        self.assertEqual(self.payload_partial.energy, 0)  # Default value

    def test_type_validation(self):
        """Test type validation for all properties"""
        # Test valid types
        self.payload1.goods = 150.0  # float accepted for goods
        self.payload1.hr = 15  # int accepted for hr
        
        # Test invalid types
        with self.assertRaises(TypeError):
            self.payload1.goods = "invalid"  # string not accepted
            
        with self.assertRaises(TypeError):
            self.payload1.hr = "invalid"  # string not accepted for hr

    def test_representation(self):
        """Test string representation methods"""
        self.assertIn("goods: 100", str(self.payload1))
        self.assertIn("energy: 50", repr(self.payload1))

    def test_comparison_operators(self):
        """Test comparison operators (==, !=, <, <=, >, >=)"""
        # Equality tests
        payload_copy = Payload(goods=100, energy=50, hr=10, hc=5, hs=3, hb=20)
        self.assertEqual(self.payload1, payload_copy)
        self.assertNotEqual(self.payload1, self.payload2)
        
        # Less than/greater than tests
        self.assertTrue(self.payload2 < self.payload1)
        self.assertTrue(self.payload1 > self.payload2)
        self.assertTrue(self.payload2 <= self.payload1)
        self.assertTrue(self.payload1 >= self.payload2)
        
        # Test with non-Payload object
        with self.assertRaises(TypeError):
            _ = self.payload1 < "not a payload"

    def test_arithmetic_operations(self):
        """Test arithmetic operations (+, -, *, /)"""
        # Addition
        result_add = self.payload1 + self.payload2
        self.assertEqual(result_add.goods, 150)
        self.assertEqual(result_add.hr, 15)
        
        # Subtraction
        result_sub = self.payload1 - self.payload2
        self.assertEqual(result_sub.goods, 50)
        self.assertEqual(result_sub.hr, 5)
        
        # Multiplication
        result_mul = self.payload1 * 2
        self.assertEqual(result_mul.goods, 200)
        self.assertEqual(result_mul.hr, 20)
        
        # Division with scalar
        result_div = self.payload1 / 2
        self.assertEqual(result_div.goods, 50)
        self.assertEqual(result_div.hr, 5)

        # Division with Payload
        result_sub = self.payload1.division(self.payload2)
        self.assertEqual(result_sub.goods, 2)
        self.assertEqual(result_sub.hr, 2)
        self.assertEqual(result_sub.hc, 2.5)
        
        # Division by zero
        with self.assertRaises(ValueError):
            _ = self.payload1 / 0

    def test_property_setters(self):
        """Test property setters with valid and invalid values"""
        # Test valid property setting
        self.payload1.goods = 200.5
        self.assertEqual(self.payload1.goods, 200.5)
        
        self.payload1.hr = 15
        self.assertEqual(self.payload1.hr, 15)
        
        # Test invalid property setting
        with self.assertRaises(TypeError):
            self.payload1.energy = "invalid"
            
        with self.assertRaises(TypeError):
            self.payload1.hc = "invalid"

    def test_none_values(self):
        """Test handling of None values"""
        # Test initialization with None
        payload_none = Payload(goods=None, hr=None)
        self.assertIsNone(payload_none.goods)
        self.assertIsNone(payload_none.hr)
        
        # Test setting to None
        self.payload1.goods = None
        self.assertIsNone(self.payload1.goods)

if __name__ == '__main__':
    unittest.main()