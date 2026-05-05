import logging
import unittest
from unittest.mock import MagicMock, patch
from sympy import Point2D
from numpy import median

from Code.Dynamic_War_Manager.Source.Block.Military import Military
from Code.Dynamic_War_Manager.Source.Context.Context import (
    MILITARY_CATEGORY,
    GROUND_ACTION,
    AIR_TASK,
    Ground_Vehicle_Asset_Type as gat,
    Air_Asset_Type as aat
)
from Code.Dynamic_War_Manager.Source.DataType.State import StateCategory

# Lightweight class stubs used only to set mock.__class__ for name/MRO checks.
# Vehicle/Ship/Aircraft cannot be imported directly because they trigger a
# pre-existing circular import in the Aircraft→Aircraft_Weapon_Data chain.
_Vehicle  = type('Vehicle',  (), {})
_Ship     = type('Ship',     (), {})
_Aircraft = type('Aircraft', (), {})


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

        # Mock aircraft — __class__ set to stub so validate_class/get_asset_list work
        self.mock_aircraft = MagicMock()
        self.mock_aircraft.__class__ = _Aircraft
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
        self.mock_vehicle = MagicMock()
        self.mock_vehicle.__class__ = _Vehicle
        self.mock_vehicle.combat_power = {"ground": {"Attack": 10}}
        self.mock_vehicle.speed = {"off_road": {"nominal": 30, "max": 50}}
        self.mock_vehicle.isTank = True
        self.mock_vehicle.artillery_range = 1000
        self.mock_vehicle.position = Point2D(0, 0)
        self.mock_vehicle.asset_type = gat.TANK.value
        self.mock_vehicle.state = MagicMock()
        self.mock_vehicle.state.state_value = StateCategory.HEALTHFUL.value

        # Mock vehicle danneggiato (Armored, Damaged)
        self.mock_vehicle_damaged = MagicMock()
        self.mock_vehicle_damaged.__class__ = _Vehicle
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
        self.mock_ship = MagicMock()
        self.mock_ship.__class__ = _Ship
        self.mock_ship.combat_power = {"sea": {"Attack": 8}}
        self.mock_ship.speed = {"nominal": 30, "max": 35}
        self.mock_ship.isDestroyer = True
        self.mock_ship.artillery_range = 2000
        self.mock_ship.asset_type = None
        self.mock_ship.state = MagicMock()
        self.mock_ship.state.state_value = StateCategory.HEALTHFUL.value

        # Mock recon asset — efficiency è una property, si accede senza ()
        self.mock_recon = MagicMock()
        self.mock_recon.role = "Recon"
        self.mock_recon.efficiency = 0.75
        self.mock_recon.asset_type = gat.EWR.value
        self.mock_recon.state = MagicMock()
        self.mock_recon.state.state_value = StateCategory.HEALTHFUL.value

        # Mock c2 asset
        self.mock_c2 = MagicMock()
        self.mock_c2.role = "c2"
        self.mock_c2.efficiency = 0.8
        self.mock_c2.state = MagicMock()
        self.mock_c2.state.state_value = StateCategory.HEALTHFUL.value

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
        self.groundbase._assets ={"vehicle1": self.mock_vehicle, "vehicle2": self.mock_vehicle}
        combat_power = self.groundbase.combat_power(force="ground", action="Attack")
        self.assertEqual(combat_power['ground']['Attack'], 20)

        self.airbase._assets ={"aircraft1": self.mock_aircraft, "aircraft2": self.mock_aircraft}
        self.assertEqual(self.airbase.combat_power(force="air", action="Intercept")['air']['Intercept'], 30)

        self.navalbase._assets ={"ship1": self.mock_ship, "ship2": self.mock_ship}
        self.assertEqual(self.navalbase.combat_power(force="sea", action="Attack")['sea']['Attack'], 16)

    # ------------------------------------------------------------------ #
    # artillery_in_range                                                  #
    # ------------------------------------------------------------------ #

    def test_artillery_in_range(self):
        """Test artillery range calculations."""
        self.groundbase._assets ={"vehicle1": self.mock_vehicle}
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

        self.airbase._assets ={}
        in_range, info = self.airbase.artillery_in_range(target_in_range)
        self.assertFalse(in_range)
        self.assertIsNone(info)

    # ------------------------------------------------------------------ #
    # time_to_direct_line_attack                                          #
    # ------------------------------------------------------------------ #

    def test_time_to_direct_line_attack(self):
        """Test time to attack calculations."""
        self.airbase._assets ={"aircraft1": self.mock_aircraft}
        target = Point2D(1600, 0)

        time_info = self.airbase.time_to_direct_line_attack(target)
        self.assertAlmostEqual(time_info["time"], 1.0)
        self.assertAlmostEqual(time_info["min_time"], 0.8)

        mock_asset = MagicMock()
        mock_asset.__class__ = _Aircraft
        mock_asset.position = Point2D(2400, 0)
        time_info = self.airbase.time_to_direct_line_attack(mock_asset)
        self.assertAlmostEqual(time_info["time"], 2.0)

        self.airbase._assets ={}
        self.assertIsNone(self.airbase.time_to_direct_line_attack(target))

    # ------------------------------------------------------------------ #
    # get_recon_efficiency                                                 #
    # ------------------------------------------------------------------ #

    def test_get_recon_efficiency_no_assets(self):
        """Returns 0.0 when there are no assets."""
        self.groundbase._assets ={}
        self.assertEqual(self.groundbase.get_recon_efficiency(), 0.0)

    def test_get_recon_efficiency_no_recon_role(self):
        """Returns 0.0 when no asset has role='Recon'."""
        non_recon = MagicMock()
        non_recon.role = "other"
        non_recon.efficiency = 0.9
        self.groundbase._assets ={"a1": non_recon}
        self.assertEqual(self.groundbase.get_recon_efficiency(), 0.0)

    def test_get_recon_efficiency_single_asset(self):
        """Returns the efficiency of the single recon asset."""
        self.groundbase._assets ={"recon1": self.mock_recon}
        self.assertAlmostEqual(self.groundbase.get_recon_efficiency(), 0.75)

    def test_get_recon_efficiency_multiple_assets_returns_median(self):
        """Returns the median efficiency across multiple recon assets."""
        recon_a = MagicMock()
        recon_a.role = "Recon"
        recon_a.efficiency = 0.6
        recon_b = MagicMock()
        recon_b.role = "Recon"
        recon_b.efficiency = 0.9
        self.groundbase._assets ={"r1": recon_a, "r2": recon_b}
        self.assertAlmostEqual(self.groundbase.get_recon_efficiency(), median([0.6, 0.9]))

    def test_get_recon_efficiency_mixed_roles(self):
        """Only assets with role='Recon' contribute to the result."""
        non_recon = MagicMock()
        non_recon.role = "c2"
        non_recon.efficiency = 0.1
        self.groundbase._assets ={"recon1": self.mock_recon, "other": non_recon}
        self.assertAlmostEqual(self.groundbase.get_recon_efficiency(), 0.75)

    # ------------------------------------------------------------------ #
    # get_c2_efficiency                                                    #
    # ------------------------------------------------------------------ #

    def test_get_c2_efficiency_no_assets(self):
        """Returns 0.0 when there are no assets."""
        self.groundbase._assets ={}
        self.assertEqual(self.groundbase.get_c2_efficiency(), 0.0)

    def test_get_c2_efficiency_no_c2_role(self):
        """Returns 0.0 when no asset has role='c2'."""
        non_c2 = MagicMock()
        non_c2.role = "Recon"
        non_c2.efficiency = 0.9
        self.groundbase._assets ={"a1": non_c2}
        self.assertEqual(self.groundbase.get_c2_efficiency(), 0.0)

    def test_get_c2_efficiency_single_asset(self):
        """Returns the efficiency of the single c2 asset."""
        self.groundbase._assets ={"c2_1": self.mock_c2}
        self.assertAlmostEqual(self.groundbase.get_c2_efficiency(), 0.8)

    def test_get_c2_efficiency_multiple_assets_returns_median(self):
        """Returns the median efficiency across multiple c2 assets."""
        c2_a = MagicMock()
        c2_a.role = "c2"
        c2_a.efficiency = 0.5
        c2_b = MagicMock()
        c2_b.role = "c2"
        c2_b.efficiency = 0.9
        self.groundbase._assets ={"c1": c2_a, "c2": c2_b}
        self.assertAlmostEqual(self.groundbase.get_c2_efficiency(), median([0.5, 0.9]))

    def test_get_c2_efficiency_mixed_roles(self):
        """Only assets with role='c2' contribute to the result."""
        recon = MagicMock()
        recon.role = "Recon"
        recon.efficiency = 0.1
        self.groundbase._assets ={"c2_1": self.mock_c2, "recon": recon}
        self.assertAlmostEqual(self.groundbase.get_c2_efficiency(), 0.8)

    # ------------------------------------------------------------------ #
    # get_recognition_report                                               #
    # ------------------------------------------------------------------ #

    _BLOCK_REPORT_PATH = 'Code.Dynamic_War_Manager.Source.Block.Block.Block.get_recognition_report'

    def test_get_recognition_report_calls_state_update(self):
        """state.update() is called before delegating to super."""
        with patch(self._BLOCK_REPORT_PATH, return_value={}):
            with patch.object(self.airbase, '_state') as mock_state:
                mock_state.__bool__ = lambda s: True
                self.airbase.get_recognition_report()
                mock_state.update.assert_called_once()

    def test_get_recognition_report_forwards_param_to_super(self):
        """The region_c2_recon_efficiency argument is forwarded to Block.get_recognition_report."""
        with patch(self._BLOCK_REPORT_PATH, return_value={}) as mock_super:
            self.airbase.get_recognition_report(region_c2_recon_efficiency=0.65)
            mock_super.assert_called_once_with(0.65)

    def test_get_recognition_report_default_param_is_none(self):
        """Calling without argument forwards None to super."""
        with patch(self._BLOCK_REPORT_PATH, return_value={}) as mock_super:
            self.airbase.get_recognition_report()
            mock_super.assert_called_once_with(None)

    def test_get_recognition_report_returns_super_result(self):
        """The return value is whatever Block.get_recognition_report returns."""
        expected = {"position": None, "state": "Healtful"}
        with patch(self._BLOCK_REPORT_PATH, return_value=expected):
            result = self.airbase.get_recognition_report()
            self.assertIs(result, expected)

    # ------------------------------------------------------------------ #
    # get_asset_list                                                      #
    # ------------------------------------------------------------------ #

    def test_get_asset_list_no_filters(self):
        """Senza filtri restituisce tutti gli asset organizzati per classe e tipo."""
        self.groundbase._assets ={
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
        self.groundbase._assets ={
            "v1": self.mock_vehicle,
        }
        self.airbase._assets ={
            "a1": self.mock_aircraft,
        }
        # Popola groundbase con sia vehicle che aircraft
        self.groundbase._assets ={
            "v1": self.mock_vehicle,
            "a1": self.mock_aircraft,
        }
        result = self.groundbase.get_asset_list(asset_class='Vehicle')
        self.assertIn('Vehicle', result)
        self.assertNotIn('Aircraft', result)
        self.assertIn(self.mock_vehicle, result['Vehicle'][gat.TANK.value])

    def test_get_asset_list_filter_by_type(self):
        """Filtro per asset_type: restituisce solo gli asset del tipo specificato."""
        self.groundbase._assets ={
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
        self.groundbase._assets ={
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
        self.groundbase._assets ={
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
        self.groundbase._assets ={}
        result = self.groundbase.get_asset_list()
        self.assertIsInstance(result, dict)
        self.assertEqual(result, {})

    def test_get_asset_list_no_match(self):
        """Nessun asset corrisponde ai filtri: restituisce dict vuoto."""
        self.groundbase._assets ={"v1": self.mock_vehicle}  # Tank, Healtful
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
        self.groundbase._assets ={"s1": self.mock_ship}  # mock_ship.asset_type = None
        result = self.groundbase.get_asset_list()
        self.assertIn('Ship', result)
        self.assertIn('Unknown_asset_type', result['Ship'])
        self.assertIn(self.mock_ship, result['Ship']['Unknown_asset_type'])

    def test_get_asset_list_multiple_same_type(self):
        """Più asset dello stesso tipo vengono raggruppati nella stessa lista."""
        mock_vehicle2 = MagicMock()
        mock_vehicle2.__class__ = _Vehicle
        mock_vehicle2.asset_type = gat.TANK.value
        mock_vehicle2.state = MagicMock()
        mock_vehicle2.state.state_value = StateCategory.HEALTHFUL.value

        self.groundbase._assets ={
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
