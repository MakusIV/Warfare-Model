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
    Air_Asset_Type as aat,
    Asset_Role
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
        self.mock_aircraft.is_operative.return_value = True
        self.mock_aircraft.speed = {"nominal": 800, "max": 1000}
        self.mock_aircraft.isTransport = False
        self.mock_aircraft.isAwacs = False
        self.mock_aircraft.isRecon = False
        self.mock_aircraft.isHelicopter = False
        self.mock_aircraft.position = Point2D(800, 0)
        self.mock_aircraft.asset_type = aat.FIGHTER.value
        self.mock_aircraft.state = MagicMock()
        self.mock_aircraft.state.state_value = StateCategory.HEALTHFUL.value

        # Mock vehicle (Tank, Healthful)
        self.mock_vehicle = MagicMock()
        self.mock_vehicle.__class__ = _Vehicle
        self.mock_vehicle.combat_power = {"ground": {"Attack": 10}}
        self.mock_vehicle.is_operative.return_value = True
        self.mock_vehicle.speed = {"off_road": {"nominal": 30, "max": 50}}
        self.mock_vehicle.isTank = True
        self.mock_vehicle.artillery_range = 1000
        self.mock_vehicle.position = Point2D(0, 0)
        self.mock_vehicle.asset_type = gat.TANK.value
        self.mock_vehicle.state = MagicMock()
        self.mock_vehicle.state.state_value = StateCategory.HEALTHFUL.value

        # Mock vehicle danneggiato (Armored, Damaged) — is_operative() → False
        self.mock_vehicle_damaged = MagicMock()
        self.mock_vehicle_damaged.__class__ = _Vehicle
        self.mock_vehicle_damaged.combat_power = {"ground": {"Attack": 5}}
        self.mock_vehicle_damaged.is_operative.return_value = False
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
        self.mock_ship.is_operative.return_value = True
        self.mock_ship.speed = {"nominal": 30, "max": 35}
        self.mock_ship.isDestroyer = True
        self.mock_ship.artillery_range = 2000
        self.mock_ship.asset_type = None
        self.mock_ship.state = MagicMock()
        self.mock_ship.state.state_value = StateCategory.HEALTHFUL.value

        # Mock recon asset — efficiency è una property, si accede senza ()
        self.mock_recon = MagicMock()
        self.mock_recon.role = Asset_Role.RECONNAISSANCE.value
        self.mock_recon.efficiency = 0.75
        self.mock_recon.asset_type = gat.EWR.value
        self.mock_recon.state = MagicMock()
        self.mock_recon.state.state_value = StateCategory.HEALTHFUL.value

        # Mock c2 asset (operative)
        self.mock_c2 = MagicMock()
        self.mock_c2.role = Asset_Role.C2.value
        self.mock_c2.efficiency = 0.8
        self.mock_c2.is_operative.return_value = True
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
        """All operative assets contribute their combat_power."""
        self.groundbase._assets = {"vehicle1": self.mock_vehicle, "vehicle2": self.mock_vehicle}
        combat_power = self.groundbase.combat_power(force="ground", action="Attack")
        self.assertEqual(combat_power['ground']['Attack'], 20)  # 10 + 10

        self.airbase._assets = {"aircraft1": self.mock_aircraft, "aircraft2": self.mock_aircraft}
        self.assertEqual(self.airbase.combat_power(force="air", action="Intercept")['air']['Intercept'], 30)  # 15 + 15

        self.navalbase._assets = {"ship1": self.mock_ship, "ship2": self.mock_ship}
        self.assertEqual(self.navalbase.combat_power(force="sea", action="Attack")['sea']['Attack'], 16)  # 8 + 8

    def test_combat_power_excludes_non_operative_assets(self):
        """Non-operative assets (is_operative()=False) must be excluded from the sum."""
        # mock_vehicle: is_operative=True, cp=10
        # mock_vehicle_damaged: is_operative=False, cp=5 → must NOT contribute
        self.groundbase._assets = {
            'v1': self.mock_vehicle,
            'v2': self.mock_vehicle_damaged,
        }
        result = self.groundbase.combat_power(force='ground', action='Attack')
        self.assertEqual(result['ground']['Attack'], 10)  # only operative vehicle

    def test_combat_power_all_non_operative_returns_zero(self):
        """When all assets are non-operative the result is 0.0."""
        self.groundbase._assets = {
            'v1': self.mock_vehicle_damaged,
            'v2': self.mock_vehicle_damaged,
        }
        result = self.groundbase.combat_power(force='ground', action='Attack')
        self.assertEqual(result['ground']['Attack'], 0.0)

    # ------------------------------------------------------------------ #
    # combat_range                                                        #
    # ------------------------------------------------------------------ #

    def test_combat_range_no_assets_returns_none(self):
        """No assets → None."""
        self.groundbase._assets = {}
        self.assertIsNone(self.groundbase.combat_range())

    def test_combat_range_all_non_operative_returns_none(self):
        """All assets non-operative → None."""
        self.mock_vehicle_damaged.combat_range.return_value = 18500.0
        self.groundbase._assets = {'v1': self.mock_vehicle_damaged}
        self.assertIsNone(self.groundbase.combat_range())

    def test_combat_range_asset_returns_none_excluded(self):
        """Operative asset whose combat_range() returns None (no weapons) → excluded."""
        self.mock_vehicle.combat_range.return_value = None
        self.groundbase._assets = {'v1': self.mock_vehicle}
        self.assertIsNone(self.groundbase.combat_range())

    def test_combat_range_single_asset_max_equals_value(self):
        """Single operative asset: max_range equals asset's range."""
        self.mock_vehicle.combat_range.return_value = 35000.0
        self.groundbase._assets = {'v1': self.mock_vehicle}
        result = self.groundbase.combat_range()
        self.assertIsNotNone(result)
        max_r, med_r, ratio, qty = result
        self.assertEqual(max_r, 35000.0)

    def test_combat_range_single_asset_med_equals_max(self):
        """Single asset: median equals max, ratio equals 1.0."""
        self.mock_vehicle.combat_range.return_value = 35000.0
        self.groundbase._assets = {'v1': self.mock_vehicle}
        max_r, med_r, ratio, qty = self.groundbase.combat_range()
        self.assertEqual(med_r, 35000.0)
        self.assertAlmostEqual(ratio, 1.0)

    def test_combat_range_single_asset_quantity_one(self):
        """Single operative asset → quantity == 1."""
        self.mock_vehicle.combat_range.return_value = 20000.0
        self.groundbase._assets = {'v1': self.mock_vehicle}
        _, _, _, qty = self.groundbase.combat_range()
        self.assertEqual(qty, 1)

    def test_combat_range_multiple_assets_max_range(self):
        """max_range is the maximum across all operative assets."""
        self.mock_vehicle.combat_range.return_value = 20000.0
        self.mock_ship.combat_range.return_value    = 280000.0
        self.groundbase._assets = {'v1': self.mock_vehicle, 's1': self.mock_ship}
        max_r, _, _, _ = self.groundbase.combat_range()
        self.assertEqual(max_r, 280000.0)

    def test_combat_range_multiple_assets_median(self):
        """med_range is the median of ranges from operative assets."""
        self.mock_vehicle.combat_range.return_value = 20000.0
        self.mock_ship.combat_range.return_value    = 280000.0
        self.groundbase._assets = {'v1': self.mock_vehicle, 's1': self.mock_ship}
        _, med_r, _, _ = self.groundbase.combat_range()
        self.assertAlmostEqual(med_r, (20000.0 + 280000.0) / 2)

    def test_combat_range_multiple_assets_ratio(self):
        """ratio == med_range / max_range."""
        self.mock_vehicle.combat_range.return_value = 20000.0
        self.mock_ship.combat_range.return_value    = 280000.0
        self.groundbase._assets = {'v1': self.mock_vehicle, 's1': self.mock_ship}
        max_r, med_r, ratio, _ = self.groundbase.combat_range()
        self.assertAlmostEqual(ratio, med_r / max_r)

    def test_combat_range_multiple_assets_quantity(self):
        """quantity counts only operative assets that returned a range."""
        self.mock_vehicle.combat_range.return_value = 20000.0
        self.mock_ship.combat_range.return_value    = 280000.0
        self.groundbase._assets = {'v1': self.mock_vehicle, 's1': self.mock_ship}
        _, _, _, qty = self.groundbase.combat_range()
        self.assertEqual(qty, 2)

    def test_combat_range_excludes_non_operative(self):
        """Non-operative assets are excluded; quantity counts only operative ones."""
        self.mock_vehicle.combat_range.return_value         = 20000.0
        self.mock_vehicle_damaged.combat_range.return_value = 50000.0  # damaged → excluded
        self.groundbase._assets = {
            'v1': self.mock_vehicle,
            'v2': self.mock_vehicle_damaged,
        }
        max_r, med_r, ratio, qty = self.groundbase.combat_range()
        self.assertEqual(max_r, 20000.0)
        self.assertEqual(qty, 1)

    def test_combat_range_returns_tuple_of_correct_types(self):
        """Return value is a tuple (float, float, float, int)."""
        self.mock_vehicle.combat_range.return_value = 18500.0
        self.groundbase._assets = {'v1': self.mock_vehicle}
        result = self.groundbase.combat_range()
        max_r, med_r, ratio, qty = result
        self.assertIsInstance(max_r, float)
        self.assertIsInstance(med_r, float)
        self.assertIsInstance(ratio, float)
        self.assertIsInstance(qty, int)

    def test_combat_range_asset_without_method_skipped(self):
        """Assets that lack combat_range (hasattr guard) are skipped safely."""
        mock_no_cr = MagicMock(spec=['is_operative'])
        mock_no_cr.__class__ = _Vehicle
        mock_no_cr.is_operative.return_value = True

        self.groundbase._assets = {'v1': mock_no_cr}
        self.assertIsNone(self.groundbase.combat_range())

    # ------------------------------------------------------------------ #
    # air_defense_volume                                                  #
    # ------------------------------------------------------------------ #

    def test_air_defense_volume_empty_block(self):
        """No assets → empty list."""
        self.groundbase._assets = {}
        self.assertEqual(self.groundbase.air_defense_volume(), [])

    def test_air_defense_volume_returns_list_always(self):
        """Return value is always a list, even when no AD assets are present."""
        self.groundbase._assets = {}
        result = self.groundbase.air_defense_volume()
        self.assertIsInstance(result, list)

    def test_air_defense_volume_single_operative_vehicle(self):
        """Operative Vehicle with AD weapons → one Cylinder in the list."""
        fake_cyl = MagicMock()
        self.mock_vehicle.air_defense_volume.return_value = fake_cyl

        self.groundbase._assets = {'v1': self.mock_vehicle}
        result = self.groundbase.air_defense_volume()

        self.assertEqual(len(result), 1)
        self.assertIs(result[0], fake_cyl)

    def test_air_defense_volume_single_operative_ship(self):
        """Operative Ship with AD weapons → one Cylinder in the list."""
        fake_cyl = MagicMock()
        self.mock_ship.air_defense_volume.return_value = fake_cyl

        self.navalbase._assets = {'s1': self.mock_ship}
        result = self.navalbase.air_defense_volume()

        self.assertEqual(len(result), 1)
        self.assertIs(result[0], fake_cyl)

    def test_air_defense_volume_excludes_non_operative_asset(self):
        """Non-operative (damaged) assets are excluded even if they have AD weapons."""
        fake_cyl = MagicMock()
        self.mock_vehicle_damaged.air_defense_volume.return_value = fake_cyl
        # mock_vehicle_damaged.is_operative() → False (set in setUp)

        self.groundbase._assets = {'v1': self.mock_vehicle_damaged}
        result = self.groundbase.air_defense_volume()

        self.assertEqual(result, [])

    def test_air_defense_volume_excludes_aircraft(self):
        """Aircraft are not Vehicle/Ship → ignored."""
        self.mock_aircraft.air_defense_volume.return_value = MagicMock()

        self.airbase._assets = {'a1': self.mock_aircraft}
        result = self.airbase.air_defense_volume()

        self.assertEqual(result, [])

    def test_air_defense_volume_excludes_non_ad_asset(self):
        """Operative Vehicle without AD weapons (air_defense_volume returns None) → excluded."""
        self.mock_vehicle.air_defense_volume.return_value = None

        self.groundbase._assets = {'v1': self.mock_vehicle}
        result = self.groundbase.air_defense_volume()

        self.assertEqual(result, [])

    def test_air_defense_volume_multiple_operative_ad_assets(self):
        """Multiple operative AD assets → one Cylinder per asset."""
        cyl_v = MagicMock()
        cyl_s = MagicMock()
        self.mock_vehicle.air_defense_volume.return_value = cyl_v
        self.mock_ship.air_defense_volume.return_value = cyl_s

        self.groundbase._assets = {'v1': self.mock_vehicle, 's1': self.mock_ship}
        result = self.groundbase.air_defense_volume()

        self.assertEqual(len(result), 2)
        self.assertIn(cyl_v, result)
        self.assertIn(cyl_s, result)

    def test_air_defense_volume_mixed_operative_and_damaged(self):
        """Only operative AD assets contribute; damaged ones are excluded."""
        cyl_v = MagicMock()
        self.mock_vehicle.air_defense_volume.return_value = cyl_v
        self.mock_vehicle_damaged.air_defense_volume.return_value = MagicMock()
        # mock_vehicle_damaged.is_operative() → False

        self.groundbase._assets = {
            'v1': self.mock_vehicle,
            'v2': self.mock_vehicle_damaged,
        }
        result = self.groundbase.air_defense_volume()

        self.assertEqual(len(result), 1)
        self.assertIs(result[0], cyl_v)

    def test_air_defense_volume_asset_without_method_skipped(self):
        """Assets that lack air_defense_volume (hasattr guard) are skipped safely."""
        mock_no_adv = MagicMock(spec=['is_operative'])
        mock_no_adv.__class__ = _Vehicle
        mock_no_adv.is_operative.return_value = True

        self.groundbase._assets = {'v1': mock_no_adv}
        result = self.groundbase.air_defense_volume()
        self.assertEqual(result, [])

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
        recon_a.role = Asset_Role.RECONNAISSANCE.value
        recon_a.efficiency = 0.6
        recon_b = MagicMock()
        recon_b.role = Asset_Role.RECONNAISSANCE.value
        recon_b.efficiency = 0.9
        self.groundbase._assets ={"r1": recon_a, "r2": recon_b}
        self.assertAlmostEqual(self.groundbase.get_recon_efficiency(), median([0.6, 0.9]))

    def test_get_recon_efficiency_mixed_roles(self):
        """Only assets with role='Recon' contribute to the result."""
        non_recon = MagicMock()
        non_recon.role = Asset_Role.C2.value
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
        non_c2.role = Asset_Role.RECONNAISSANCE.value
        non_c2.efficiency = 0.9
        self.groundbase._assets ={"a1": non_c2}
        self.assertEqual(self.groundbase.get_c2_efficiency(), 0.0)

    def test_get_c2_efficiency_single_asset(self):
        """Returns the efficiency of the single c2 asset."""
        self.groundbase._assets ={"c2_1": self.mock_c2}
        self.assertAlmostEqual(self.groundbase.get_c2_efficiency(), 0.8)

    def test_get_c2_efficiency_multiple_assets_returns_median(self):
        """Returns the median efficiency across multiple operative c2 assets."""
        c2_a = MagicMock()
        c2_a.role = Asset_Role.C2.value
        c2_a.efficiency = 0.5
        c2_a.is_operative.return_value = True
        c2_b = MagicMock()
        c2_b.role = Asset_Role.C2.value
        c2_b.efficiency = 0.9
        c2_b.is_operative.return_value = True
        self.groundbase._assets ={"c1": c2_a, "c2": c2_b}
        self.assertAlmostEqual(self.groundbase.get_c2_efficiency(), median([0.5, 0.9]))

    def test_get_c2_efficiency_mixed_roles(self):
        """Only assets with role='c2' contribute to the result."""
        recon = MagicMock()
        recon.role = Asset_Role.RECONNAISSANCE.value
        recon.efficiency = 0.1
        self.groundbase._assets ={"c2_1": self.mock_c2, "recon": recon}
        self.assertAlmostEqual(self.groundbase.get_c2_efficiency(), 0.8)

    def test_get_c2_efficiency_excludes_non_operative(self):
        """Non-operative C2 asset is excluded; only operative one counts."""
        operative_c2 = MagicMock()
        operative_c2.role = Asset_Role.C2.value
        operative_c2.efficiency = 0.6
        operative_c2.is_operative.return_value = True

        non_operative_c2 = MagicMock()
        non_operative_c2.role = Asset_Role.C2.value
        non_operative_c2.efficiency = 0.95
        non_operative_c2.is_operative.return_value = False

        self.groundbase._assets = {"c1": operative_c2, "c2": non_operative_c2}
        self.assertAlmostEqual(self.groundbase.get_c2_efficiency(), 0.6)

    def test_get_c2_efficiency_all_non_operative_returns_zero(self):
        """All C2 assets non-operative → 0.0."""
        non_op = MagicMock()
        non_op.role = Asset_Role.C2.value
        non_op.efficiency = 0.9
        non_op.is_operative.return_value = False

        self.groundbase._assets = {"c1": non_op}
        self.assertEqual(self.groundbase.get_c2_efficiency(), 0.0)

    def test_get_c2_efficiency_without_efficiency_attr_excluded(self):
        """C2 asset without 'efficiency' attribute is excluded (hasattr guard)."""
        no_eff = MagicMock(spec=['role', 'is_operative'])
        no_eff.role = Asset_Role.C2.value
        no_eff.is_operative.return_value = True

        self.groundbase._assets = {"c1": no_eff}
        self.assertEqual(self.groundbase.get_c2_efficiency(), 0.0)

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
    # combat_state                                                        #
    # ------------------------------------------------------------------ #

    def _make_asset(self, is_operative=True, efficiency=0.8, role="other"):
        """Helper: build a minimal mock asset for combat_state tests."""
        mock = MagicMock()
        mock.is_operative.return_value = is_operative
        mock.efficiency = efficiency
        mock.role = role
        return mock

    def test_combat_state_no_assets_returns_none(self):
        """No assets → None."""
        self.groundbase._assets = {}
        self.assertIsNone(self.groundbase.combat_state())

    def test_combat_state_all_operative_full_efficiency(self):
        """All at max: operative_efficiency=1.0, c2_efficiency=1.0, ratio=1.0 → 1.0."""
        c2 = self._make_asset(is_operative=True, efficiency=1.0, role=Asset_Role.C2.value)
        self.groundbase._assets = {"c1": c2}
        self.assertAlmostEqual(self.groundbase.combat_state(), 1.0)

    def test_combat_state_no_operative_returns_zero(self):
        """All assets non-operative → ratio=0 → combat_state=0.0."""
        a1 = self._make_asset(is_operative=False, efficiency=0.9, role=Asset_Role.C2.value)
        a2 = self._make_asset(is_operative=False, efficiency=0.7, role="other")
        self.groundbase._assets = {"a1": a1, "a2": a2}
        self.assertAlmostEqual(self.groundbase.combat_state(), 0.0)

    def test_combat_state_formula_numerical(self):
        """Verify formula numerically with controlled inputs.

        Setup:
          - asset1: operative C2, efficiency=0.6
          - asset2: non-operative other, efficiency=0.4
        Expected:
          operative_efficiency = mean([0.6]) = 0.6  (only operative)
          c2_efficiency        = median([0.6]) = 0.6  (only operative C2)
          ratio_operative      = 1 / 2 = 0.5
          result = (0.3*0.6 + 0.7*0.6) * 0.5 = 0.6 * 0.5 = 0.3
        """
        a1 = self._make_asset(is_operative=True,  efficiency=0.6, role=Asset_Role.C2.value)
        a2 = self._make_asset(is_operative=False, efficiency=0.4, role="other")
        self.groundbase._assets = {"a1": a1, "a2": a2}
        expected = (0.3 * 0.6 + 0.7 * 0.6) * 0.5
        self.assertAlmostEqual(self.groundbase.combat_state(), expected, places=9)

    def test_combat_state_formula_mixed_assets(self):
        """Three assets: 2 operative (1 C2), 1 non-operative.

        Setup:
          - a1: operative C2, efficiency=0.8
          - a2: operative non-C2, efficiency=0.5
          - a3: non-operative C2, efficiency=0.9
        Expected:
          operative_efficiency = mean([0.8, 0.5]) = 0.65
          c2_efficiency        = median([0.8]) = 0.8  (a3 excluded: non-operative)
          ratio_operative      = 2 / 3
          result = (0.3*0.65 + 0.7*0.8) * (2/3)
                 = (0.195 + 0.56) * 0.6667
                 = 0.755 * 0.6667 ≈ 0.5033
        """
        a1 = self._make_asset(is_operative=True,  efficiency=0.8, role=Asset_Role.C2.value)
        a2 = self._make_asset(is_operative=True,  efficiency=0.5, role="other")
        a3 = self._make_asset(is_operative=False, efficiency=0.9, role=Asset_Role.C2.value)
        self.groundbase._assets = {"a1": a1, "a2": a2, "a3": a3}
        expected = (0.3 * ((0.8 + 0.5) / 2) + 0.7 * 0.8) * (2 / 3)
        self.assertAlmostEqual(self.groundbase.combat_state(), expected, places=9)

    def test_combat_state_no_c2_only_efficiency_contributes(self):
        """No C2 assets → c2_efficiency=0, only the 0.3*efficiency term survives.

        Setup: 1 operative non-C2 asset, efficiency=0.5, ratio=1.0
        Expected = (0.3*0.5 + 0.7*0.0) * 1.0 = 0.15
        """
        a1 = self._make_asset(is_operative=True, efficiency=0.5, role="other")
        self.groundbase._assets = {"a1": a1}
        self.assertAlmostEqual(self.groundbase.combat_state(), 0.15)

    def test_combat_state_only_non_operative_c2(self):
        """Non-operative C2 → c2_efficiency=0; operative non-C2 assets still count."""
        a1 = self._make_asset(is_operative=True,  efficiency=0.5, role="other")
        a2 = self._make_asset(is_operative=False, efficiency=0.9, role=Asset_Role.C2.value)
        self.groundbase._assets = {"a1": a1, "a2": a2}
        # operative_efficiency = 0.5, c2_efficiency = 0.0, ratio = 1/2
        expected = (0.3 * 0.5 + 0.7 * 0.0) * 0.5
        self.assertAlmostEqual(self.groundbase.combat_state(), expected, places=9)

    def test_combat_state_result_bounded_0_to_1(self):
        """Result is always within [0, 1]."""
        a1 = self._make_asset(is_operative=True, efficiency=1.0, role=Asset_Role.C2.value)
        a2 = self._make_asset(is_operative=True, efficiency=1.0, role="other")
        self.groundbase._assets = {"a1": a1, "a2": a2}
        result = self.groundbase.combat_state()
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)

    def test_combat_state_single_operative_asset(self):
        """Single operative non-C2 asset: ratio=1, c2=0, result=0.3*efficiency."""
        a1 = self._make_asset(is_operative=True, efficiency=0.7, role="other")
        self.groundbase._assets = {"a1": a1}
        self.assertAlmostEqual(self.groundbase.combat_state(), 0.3 * 0.7)

    def test_combat_state_returns_float_when_assets_present(self):
        """Return type is float (not None) when assets exist."""
        a1 = self._make_asset(is_operative=True, efficiency=0.5, role=Asset_Role.C2.value)
        self.groundbase._assets = {"a1": a1}
        result = self.groundbase.combat_state()
        self.assertIsInstance(result, float)

    # ------------------------------------------------------------------ #
    # Smoke test for formerly-placeholder methods                         #
    # ------------------------------------------------------------------ #

    def test_non_raising_methods(self):
        """air_defense_volume and combat_range must not raise on empty block."""
        try:
            self.airbase.air_defense_volume()
            self.airbase.combat_range()
        except Exception as e:
            self.fail(f"Method raised unexpected exception: {e}")

    def test_combat_power_skips_asset_without_combat_power(self):
        """Assets without a combat_power attribute are silently skipped (hasattr guard)."""
        # spec=['is_operative'] → hasattr(mock, 'combat_power') returns False
        mock_no_cp = MagicMock(spec=['is_operative'])
        mock_no_cp.is_operative.return_value = True

        self.groundbase._assets = {
            'v1': self.mock_vehicle,  # has combat_power={'ground': {'Attack': 10}}
            'v2': mock_no_cp,         # no combat_power → must be skipped
        }
        result = self.groundbase.combat_power(force='ground', action='Attack')
        # Only mock_vehicle contributes; mock_no_cp must not cause AttributeError
        self.assertEqual(result['ground']['Attack'], 10)


if __name__ == "__main__":
    unittest.main()
