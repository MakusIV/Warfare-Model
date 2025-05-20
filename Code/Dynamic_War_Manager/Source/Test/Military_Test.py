import unittest
from unittest.mock import MagicMock, patch
from sympy import Point2D
from numpy import median

from Military import Military
from Context import (
    MILITARY_CATEGORY,
    GROUND_ACTION,
    AIR_TASK
)

class TestMilitary(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.airbase = Military(
            mil_category=MILITARY_CATEGORY["Air Base"],
            name="Test Airbase",
            side="Blue"
        )
        self.groundbase = Military(
            mil_category=MILITARY_CATEGORY["Ground Base"],
            name="Test Groundbase",
            side="Red"
        )
        self.navalbase = Military(
            mil_category=MILITARY_CATEGORY["Naval Base"],
            name="Test Navalbase",
            side="Blue"
        )
        
        # Mock assets
        self.mock_aircraft = MagicMock()
        self.mock_aircraft.combat_power = 10
        self.mock_aircraft.speed = {"nominal": 800, "max": 1000}
        self.mock_aircraft.isTransport = False
        self.mock_aircraft.isAwacs = False
        self.mock_aircraft.isRecon = False
        self.mock_aircraft.isHelicopter = False
        
        self.mock_vehicle = MagicMock()
        self.mock_vehicle.combat_power = 5
        self.mock_vehicle.speed = {"off_road": {"nominal": 30, "max": 50}}
        self.mock_vehicle.isTank = True
        self.mock_vehicle.artillery_range = 1000
        
        self.mock_ship = MagicMock()
        self.mock_ship.combat_power = 8
        self.mock_ship.speed = {"nominal": 30, "max": 35}
        self.mock_ship.isDestroyer = True
        self.mock_ship.artillery_range = 2000
        
        self.mock_recon = MagicMock()
        self.mock_recon.role = "Recon"
        self.mock_recon.get_efficiency.return_value = 0.75

    def test_initialization(self):
        """Test Military initialization."""
        self.assertEqual(self.airbase.mil_category, MILITARY_CATEGORY["Air Base"])
        self.assertEqual(self.groundbase.mil_category, MILITARY_CATEGORY["Ground Base"])
        self.assertEqual(self.navalbase.mil_category, MILITARY_CATEGORY["Naval Base"])
        
        with self.assertRaises(ValueError):
            Military(mil_category="Invalid Category")

    def test_mil_category_property(self):
        """Test military category property."""
        self.airbase.mil_category = MILITARY_CATEGORY["Ground Base"]
        self.assertEqual(self.airbase.mil_category, MILITARY_CATEGORY["Ground Base"])
        
        with self.assertRaises(ValueError):
            self.airbase.mil_category = "Invalid Category"

    def test_base_type_checks(self):
        """Test base type checking methods."""
        self.assertTrue(self.airbase.is_airbase())
        self.assertFalse(self.airbase.is_groundbase())
        self.assertFalse(self.airbase.is_navalgroup())
        
        self.assertTrue(self.groundbase.is_groundbase())
        self.assertFalse(self.groundbase.is_airbase())
        self.assertFalse(self.groundbase.is_navalgroup())
        
        self.assertTrue(self.navalbase.is_navalgroup())
        self.assertFalse(self.navalbase.is_airbase())
        self.assertFalse(self.navalbase.is_groundbase())

    def test_combat_power_calculations(self):
        """Test combat power calculations."""
        # Test ground combat power
        self.groundbase.assets = {"vehicle1": self.mock_vehicle, "vehicle2": self.mock_vehicle}
        self.assertEqual(self.groundbase.ground_combat_power("Attack"), 10)
        
        with self.assertRaises(ValueError):
            self.groundbase.ground_combat_power("Invalid Action")
            
        # Test air combat power
        self.airbase.assets = {"aircraft1": self.mock_aircraft, "aircraft2": self.mock_aircraft}
        self.assertEqual(self.airbase.air_combat_power("CAP"), 20)
        
        with self.assertRaises(ValueError):
            self.airbase.air_combat_power("Invalid Task")

    def test_artillery_in_range(self):
        """Test artillery range calculations."""
        self.groundbase.position = Point2D(0, 0)
        self.groundbase.assets = {"vehicle1": self.mock_vehicle}
        
        # Target within range
        target_in_range = Point2D(500, 0)
        in_range, info = self.groundbase.artillery_in_range(target_in_range)
        self.assertTrue(in_range)
        self.assertTrue(info["target_within_max_range"])
        
        # Target out of range
        target_out_of_range = Point2D(1500, 0)
        in_range, info = self.groundbase.artillery_in_range(target_out_of_range)
        self.assertTrue(in_range)  # Still has artillery, just not in range
        self.assertFalse(info["target_within_max_range"])
        
        # No artillery case
        self.airbase.assets = {}
        in_range, info = self.airbase.artillery_in_range(target_in_range)
        self.assertFalse(in_range)
        self.assertIsNone(info)

    def test_time_to_direct_line_attack(self):
        """Test time to attack calculations."""
        self.airbase.position = Point2D(0, 0)
        self.airbase.assets = {"aircraft1": self.mock_aircraft}
        target = Point2D(800, 0)
        
        time_info = self.airbase.time_to_direct_line_attack(target)
        self.assertAlmostEqual(time_info["time"], 1.0)  # 800 km / 800 km/h = 1 hour
        self.assertAlmostEqual(time_info["min_time"], 0.8)  # 800 km / 1000 km/h = 0.8 hours
        
        # Test with asset that has position
        mock_asset = MagicMock()
        mock_asset.position = Point2D(800, 0)
        time_info = self.airbase.time_to_direct_line_attack(mock_asset)
        self.assertAlmostEqual(time_info["time"], 1.0)
        
        # Test no attack assets case
        self.airbase.assets = {}
        self.assertIsNone(self.airbase.time_to_direct_line_attack(target))

    def test_get_recon_efficiency(self):
        """Test reconnaissance efficiency calculation."""
        self.groundbase.assets = {"recon1": self.mock_recon, "recon2": self.mock_recon}
        self.assertEqual(self.groundbase.get_recon_efficiency(), 0.75)
        
        # No recon assets case
        self.groundbase.assets = {}
        self.assertEqual(self.groundbase.get_recon_efficiency(), 0.0)

    def test_placeholder_methods(self):
        """Test placeholder methods don't raise exceptions."""
        try:
            self.airbase.air_defense()
            self.airbase.combat_range()
            self.airbase.defense_aa_range()
            self.airbase.combat_volume()
            self.airbase.defense_aa_volume()
            self.airbase.intelligence()
            self.airbase.threat_volume()
            self.airbase.front()
            self.airbase.combat_state()
        except Exception as e:
            self.fail(f"Placeholder method raised exception: {e}")

if __name__ == "__main__":
    unittest.main()