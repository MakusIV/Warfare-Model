import logging
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
    AIR_TASK,
    Ground_Vehicle_Asset_Type as gat,
    Air_Asset_Type as aat
)
from Code.Dynamic_War_Manager.Source.DataType.State import StateCategory


class TestMilitary(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Sopprime i warning noti del modulo Vehicle_Data relativi a
        # incoerenze nei dati dei veicoli (es. 2K22-Tunguska: AA_CANNONS su SAM_Small).
        # Questi warning sono attesi e non influenzano la correttezza dei test.
        logging.getLogger('Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data').setLevel(logging.ERROR)

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

        # Mock aircraft
        self.mock_aircraft = MagicMock(spec=Aircraft)
        self.mock_aircraft.combat_power = {"air": {"Intercept": 15}}
        self.mock_aircraft.speed = {"nominal": 800, "max": 1000}
        self.mock_aircraft.isTransport = False
        self.mock_aircraft.isAwacs = False
        self.mock_aircraft.isRecon = False
        self.mock_aircraft.isHelicopter = False
        self.mock_aircraft.position = Point2D(800, 0)
        self.mock_aircraft.asset_type = aat.FIGHTER.value
        self.mock_aircraft.state = MagicMock()
        self.mock_aircraft.state.state_value = StateCategory.HEALTHFUL.value

        # Mock vehicle (Tank, Healtful)
        self.mock_vehicle = MagicMock(spec=Vehicle)
        self.mock_vehicle.combat_power = {"ground": {"Attack": 10}}
        self.mock_vehicle.speed = {"off_road": {"nominal": 30, "max": 50}}
        self.mock_vehicle.isTank = True
        self.mock_vehicle.artillery_range = 1000
        self.mock_vehicle.position = Point2D(0, 0)
        self.mock_vehicle.asset_type = gat.TANK.value
        self.mock_vehicle.state = MagicMock()
        self.mock_vehicle.state.state_value = StateCategory.HEALTHFUL.value

        # Mock vehicle danneggiato (Armored, Damaged)
        self.mock_vehicle_damaged = MagicMock(spec=Vehicle)
        self.mock_vehicle_damaged.combat_power = {"ground": {"Attack": 5}}
        self.mock_vehicle_damaged.speed = {"off_road": {"nominal": 25, "max": 40}}
        self.mock_vehicle_damaged.isTank = False
        self.mock_vehicle_damaged.isArmor = True
        self.mock_vehicle_damaged.artillery_range = 0
        self.mock_vehicle_damaged.position = Point2D(100, 0)
        self.mock_vehicle_damaged.asset_type = gat.ARMORED.value
        self.mock_vehicle_damaged.state = MagicMock()
        self.mock_vehicle_damaged.state.state_value = StateCategory.DAMAGED.value

        # Mock ship
        self.mock_ship = MagicMock(spec=Ship)
        self.mock_ship.combat_power = {"sea": {"Attack": 8}}
        self.mock_ship.speed = {"nominal": 30, "max": 35}
        self.mock_ship.isDestroyer = True
        self.mock_ship.artillery_range = 2000
        self.mock_ship.asset_type = None
        self.mock_ship.state = MagicMock()
        self.mock_ship.state.state_value = StateCategory.HEALTHFUL.value

        # Mock recon
        self.mock_recon = MagicMock(spec=Vehicle)
        self.mock_recon.role = "Recon"
        self.mock_recon.efficiency.return_value = 0.75
        self.mock_recon.asset_type = gat.EWR.value
        self.mock_recon.state = MagicMock()
        self.mock_recon.state.state_value = StateCategory.HEALTHFUL.value

    # ------------------------------------------------------------------ #
    # Initialization & Properties                                         #
    # ------------------------------------------------------------------ #

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

    # ------------------------------------------------------------------ #
    # combat_power                                                        #
    # ------------------------------------------------------------------ #

    def test_combat_power_calculations(self):
        """Test combat power calculations."""
        self.groundbase.assets = {"vehicle1": self.mock_vehicle, "vehicle2": self.mock_vehicle}
        combat_power = self.groundbase.combat_power(force="ground", action="Attack")
        self.assertEqual(combat_power['ground']['Attack'], 20)

        self.airbase.assets = {"aircraft1": self.mock_aircraft, "aircraft2": self.mock_aircraft}
        self.assertEqual(self.airbase.combat_power(force="air", action="Intercept")['air']['Intercept'], 30)

        self.navalbase.assets = {"ship1": self.mock_ship, "ship2": self.mock_ship}
        self.assertEqual(self.navalbase.combat_power(force="sea", action="Attack")['sea']['Attack'], 16)

    # ------------------------------------------------------------------ #
    # artillery_in_range                                                  #
    # ------------------------------------------------------------------ #

    def test_artillery_in_range(self):
        """Test artillery range calculations."""
        self.groundbase.assets = {"vehicle1": self.mock_vehicle}
        self.assertIsNotNone(self.groundbase.position)
        self.assertEqual(self.groundbase.position, Point2D(0, 0))

        target_in_range = Point2D(500, 0)
        in_range, info = self.groundbase.artillery_in_range(target_in_range)
        self.assertTrue(in_range)
        self.assertTrue(info["target_within_max_range"])

        target_out_of_range = Point2D(1500, 0)
        in_range, info = self.groundbase.artillery_in_range(target_out_of_range)
        self.assertTrue(in_range)
        self.assertFalse(info["target_within_max_range"])

        self.airbase.assets = {}
        in_range, info = self.airbase.artillery_in_range(target_in_range)
        self.assertFalse(in_range)
        self.assertIsNone(info)

    # ------------------------------------------------------------------ #
    # time_to_direct_line_attack                                          #
    # ------------------------------------------------------------------ #

    def test_time_to_direct_line_attack(self):
        """Test time to attack calculations."""
        self.airbase.assets = {"aircraft1": self.mock_aircraft}
        target = Point2D(1600, 0)

        time_info = self.airbase.time_to_direct_line_attack(target)
        self.assertAlmostEqual(time_info["time"], 1.0)
        self.assertAlmostEqual(time_info["min_time"], 0.8)

        mock_asset = MagicMock(spec=Aircraft)
        mock_asset.position = Point2D(2400, 0)
        time_info = self.airbase.time_to_direct_line_attack(mock_asset)
        self.assertAlmostEqual(time_info["time"], 2.0)

        self.airbase.assets = {}
        self.assertIsNone(self.airbase.time_to_direct_line_attack(target))

    # ------------------------------------------------------------------ #
    # get_recon_efficiency                                                 #
    # ------------------------------------------------------------------ #

    def test_get_recon_efficiency(self):
        """Test reconnaissance efficiency calculation."""
        self.groundbase.assets = {"recon1": self.mock_recon, "recon2": self.mock_recon}
        self.assertEqual(self.groundbase.get_recon_efficiency(), 0.75)

        self.groundbase.assets = {}
        self.assertEqual(self.groundbase.get_recon_efficiency(), 0.0)

    # ------------------------------------------------------------------ #
    # get_asset_list                                                      #
    # ------------------------------------------------------------------ #

    def test_get_asset_list_no_filters(self):
        """Senza filtri restituisce tutti gli asset organizzati per classe e tipo."""
        self.groundbase.assets = {
            "v1": self.mock_vehicle,
            "v2": self.mock_vehicle_damaged,
        }
        result = self.groundbase.get_asset_list()
        self.assertIsInstance(result, dict)
        self.assertIn('Vehicle', result)
        self.assertIn(gat.TANK.value, result['Vehicle'])
        self.assertIn(gat.ARMORED.value, result['Vehicle'])
        self.assertIn(self.mock_vehicle, result['Vehicle'][gat.TANK.value])
        self.assertIn(self.mock_vehicle_damaged, result['Vehicle'][gat.ARMORED.value])

    def test_get_asset_list_filter_by_class(self):
        """Filtro per asset_class: restituisce solo gli asset della classe specificata."""
        self.groundbase.assets = {
            "v1": self.mock_vehicle,
        }
        self.airbase.assets = {
            "a1": self.mock_aircraft,
        }
        # Popola groundbase con sia vehicle che aircraft
        self.groundbase.assets = {
            "v1": self.mock_vehicle,
            "a1": self.mock_aircraft,
        }
        result = self.groundbase.get_asset_list(asset_class='Vehicle')
        self.assertIn('Vehicle', result)
        self.assertNotIn('Aircraft', result)
        self.assertIn(self.mock_vehicle, result['Vehicle'][gat.TANK.value])

    def test_get_asset_list_filter_by_type(self):
        """Filtro per asset_type: restituisce solo gli asset del tipo specificato."""
        self.groundbase.assets = {
            "v1": self.mock_vehicle,           # Tank
            "v2": self.mock_vehicle_damaged,   # Armored
        }
        result = self.groundbase.get_asset_list(asset_type=gat.TANK.value)
        self.assertIn('Vehicle', result)
        self.assertIn(gat.TANK.value, result['Vehicle'])
        self.assertNotIn(gat.ARMORED.value, result.get('Vehicle', {}))
        self.assertIn(self.mock_vehicle, result['Vehicle'][gat.TANK.value])

    def test_get_asset_list_filter_by_state(self):
        """Filtro per asset_state: restituisce solo gli asset nello stato specificato."""
        self.groundbase.assets = {
            "v1": self.mock_vehicle,           # Healtful
            "v2": self.mock_vehicle_damaged,   # Damaged
        }
        result = self.groundbase.get_asset_list(asset_state=StateCategory.HEALTHFUL.value)
        vehicle_types = result.get('Vehicle', {})
        # mock_vehicle è Healtful
        self.assertIn(self.mock_vehicle, vehicle_types.get(gat.TANK.value, []))
        # mock_vehicle_damaged è Damaged, non deve apparire
        all_in_result = [a for assets in vehicle_types.values() for a in assets]
        self.assertNotIn(self.mock_vehicle_damaged, all_in_result)

    def test_get_asset_list_all_filters(self):
        """Tutti i filtri combinati."""
        self.groundbase.assets = {
            "v1": self.mock_vehicle,           # Vehicle, Tank, Healtful
            "v2": self.mock_vehicle_damaged,   # Vehicle, Armored, Damaged
        }
        result = self.groundbase.get_asset_list(
            asset_class='Vehicle',
            asset_type=gat.TANK.value,
            asset_state=StateCategory.HEALTHFUL.value
        )
        self.assertIn('Vehicle', result)
        self.assertIn(self.mock_vehicle, result['Vehicle'][gat.TANK.value])
        all_in_result = [a for assets in result.get('Vehicle', {}).values() for a in assets]
        self.assertNotIn(self.mock_vehicle_damaged, all_in_result)

    def test_get_asset_list_empty_assets(self):
        """Con asset vuoti restituisce dict vuoto."""
        self.groundbase.assets = {}
        result = self.groundbase.get_asset_list()
        self.assertIsInstance(result, dict)
        self.assertEqual(result, {})

    def test_get_asset_list_no_match(self):
        """Nessun asset corrisponde ai filtri: restituisce dict vuoto."""
        self.groundbase.assets = {"v1": self.mock_vehicle}  # Tank, Healtful
        result = self.groundbase.get_asset_list(asset_type=gat.ARMORED.value)
        self.assertIsInstance(result, dict)
        self.assertEqual(result, {})

    def test_get_asset_list_invalid_class(self):
        """asset_class non valido restituisce None."""
        result = self.groundbase.get_asset_list(asset_class='InvalidClass')
        self.assertIsNone(result)

    def test_get_asset_list_invalid_type(self):
        """asset_type non valido restituisce None."""
        result = self.groundbase.get_asset_list(asset_type='InvalidType')
        self.assertIsNone(result)

    def test_get_asset_list_invalid_state(self):
        """asset_state non valido restituisce None."""
        result = self.groundbase.get_asset_list(asset_state='InvalidState')
        self.assertIsNone(result)

    def test_get_asset_list_asset_without_type(self):
        """Asset senza asset_type viene inserito sotto 'Unknown_asset_type'."""
        self.groundbase.assets = {"s1": self.mock_ship}  # mock_ship.asset_type = None
        result = self.groundbase.get_asset_list()
        self.assertIn('Ship', result)
        self.assertIn('Unknown_asset_type', result['Ship'])
        self.assertIn(self.mock_ship, result['Ship']['Unknown_asset_type'])

    def test_get_asset_list_multiple_same_type(self):
        """Più asset dello stesso tipo vengono raggruppati nella stessa lista."""
        mock_vehicle2 = MagicMock(spec=Vehicle)
        mock_vehicle2.asset_type = gat.TANK.value
        mock_vehicle2.state = MagicMock()
        mock_vehicle2.state.state_value = StateCategory.HEALTHFUL.value

        self.groundbase.assets = {
            "v1": self.mock_vehicle,
            "v2": mock_vehicle2,
        }
        result = self.groundbase.get_asset_list(asset_class='Vehicle', asset_type=gat.TANK.value)
        tanks = result['Vehicle'][gat.TANK.value]
        self.assertEqual(len(tanks), 2)
        self.assertIn(self.mock_vehicle, tanks)
        self.assertIn(mock_vehicle2, tanks)

    # ------------------------------------------------------------------ #
    # Placeholder methods                                                  #
    # ------------------------------------------------------------------ #

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
