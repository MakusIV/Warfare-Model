import unittest
from unittest.mock import MagicMock, patch
from sympy import Point2D
from numpy import median

from Code.Dynamic_War_Manager.Source.Block.Military import Military
from Code.Dynamic_War_Manager.Source.Asset.Asset import Asset
from Code.Dynamic_War_Manager.Source.Asset.Aircraft import Aircraft
from Code.Dynamic_War_Manager.Source.Asset.Vehicle import Vehicle
from Code.Dynamic_War_Manager.Source.Asset.Ship import Ship
from Code.Dynamic_War_Manager.Source.Context.Context import (
    MILITARY_CATEGORY,
    GROUND_ACTION,
    AIR_TASK
)

class TestMilitary(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.airbase = Military(
            mil_category=MILITARY_CATEGORY["Air_Base"][1],
            name="Test Airbase",
            side="Blue"
        )
        self.groundbase = Military(
            mil_category=MILITARY_CATEGORY["Ground_Base"][1],
            name="Test Groundbase",
            side="Red"
        )
        self.navalbase = Military(
            mil_category=MILITARY_CATEGORY["Naval_Base"][1],
            name="Test Navalbase",
            side="Blue"
        )
        
        # Mock assets
        self.mock_aircraft = MagicMock(spec=Aircraft)
        self.mock_aircraft.combat_power = {"air": {"Intercept": 15}}
        self.mock_aircraft.speed = {"nominal": 800, "max": 1000}
        self.mock_aircraft.isTransport = False
        self.mock_aircraft.isAwacs = False
        self.mock_aircraft.isRecon = False
        self.mock_aircraft.isHelicopter = False
        self.mock_aircraft.position = Point2D(800,0)
        
        self.mock_vehicle = MagicMock(spec=Vehicle)
        self.mock_vehicle.combat_power = {"ground": {"Attack": 10}}
        self.mock_vehicle.speed = {"off_road": {"nominal": 30, "max": 50}}
        self.mock_vehicle.isTank = True
        self.mock_vehicle.artillery_range = 1000
        self.mock_vehicle.position = Point2D(0,0)        
        
        self.mock_ship = MagicMock(spec=Ship)
        self.mock_ship.combat_power = {"sea": {"Attack": 8}}
        self.mock_ship.speed = {"nominal": 30, "max": 35}
        self.mock_ship.isDestroyer = True
        self.mock_ship.artillery_range = 2000        
        
        self.mock_recon = MagicMock(spec=Vehicle)
        self.mock_recon.role = "Recon"
        self.mock_recon.efficiency.return_value = 0.75        

    def test_initialization(self):
        """Test Military initialization."""
        self.assertEqual(self.airbase.mil_category, MILITARY_CATEGORY["Air_Base"][1])
        self.assertEqual(self.groundbase.mil_category, MILITARY_CATEGORY["Ground_Base"][1])
        self.assertEqual(self.navalbase.mil_category, MILITARY_CATEGORY["Naval_Base"][1])
        
        with self.assertRaises(ValueError):
            Military(mil_category="Invalid Category")

    def test_mil_category_property(self):
        """Test military category property."""
        self.airbase.mil_category = MILITARY_CATEGORY["Ground_Base"][1]
        self.assertEqual(self.airbase.mil_category, MILITARY_CATEGORY["Ground_Base"][1])
        self.airbase.mil_category = MILITARY_CATEGORY["Air_Base"][1]
        
        with self.assertRaises(ValueError):
            self.airbase.mil_category = "Invalid Category"

    def test_base_type_checks(self):
        """Test base type checking methods."""
        self.assertTrue(self.airbase.is_Air_Base())
        self.assertFalse(self.airbase.is_Ground_Base())
        self.assertFalse(self.airbase.is_Naval_Base())
        
        self.assertTrue(self.groundbase.is_Ground_Base())
        self.assertFalse(self.groundbase.is_Air_Base())
        self.assertFalse(self.groundbase.is_Naval_Base())
        
        self.assertTrue(self.navalbase.is_Naval_Base())
        self.assertFalse(self.navalbase.is_Air_Base())
        self.assertFalse(self.navalbase.is_Ground_Base())

    def test_combat_power_calculations(self):
        """Test combat power calculations."""
        # Test ground combat power
        self.groundbase.assets = {"vehicle1": self.mock_vehicle, "vehicle2": self.mock_vehicle}
        combat_power = self.groundbase.combat_power(force="ground", action="Attack")
        self.assertEqual(combat_power['ground']['Attack'], 20)
             
        # Test air combat power
        self.airbase.assets = {"aircraft1": self.mock_aircraft, "aircraft2": self.mock_aircraft}
        self.assertEqual(self.airbase.combat_power(force="air", action="Intercept")['air']['Intercept'], 30)
        
        # Test naval combat power
        self.navalbase.assets = {"ship1": self.mock_ship, "ship2": self.mock_ship}
        self.assertEqual(self.navalbase.combat_power(force="sea", action="Attack")['sea']['Attack'], 16)
        
    def test_artillery_in_range(self):
        """Test artillery range calculations."""        
        self.groundbase.assets = {"vehicle1": self.mock_vehicle}
        self.assertIsNotNone(self.groundbase.position)
        self.assertEqual(self.groundbase.position, Point2D(0,0))
        
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
        self.airbase.assets = {"aircraft1": self.mock_aircraft}
        target = Point2D(1600, 0)
        
        time_info = self.airbase.time_to_direct_line_attack(target)
        self.assertAlmostEqual(time_info["time"], 1.0)  # 800 km / 800 km/h = 1 hour
        self.assertAlmostEqual(time_info["min_time"], 0.8)  # 800 km / 1000 km/h = 0.8 hours
        
        # Test with asset that has position
        mock_asset = MagicMock(spec=Aircraft)
        mock_asset.position = Point2D(2400, 0)
        time_info = self.airbase.time_to_direct_line_attack(mock_asset)
        self.assertAlmostEqual(time_info["time"], 2.0)
        
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
            self.airbase.combat_state()
        except Exception as e:
            self.fail(f"Placeholder method raised exception: {e}")

if __name__ == "__main__":
    unittest.main()