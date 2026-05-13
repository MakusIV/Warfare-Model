"""Tests for Mobile — air_defense_volume() and combat_range().

Setup strategy
--------------
* Aircraft circular-import chain (Aircraft → Aircraft_Data → … → Aircraft) is
  pre-injected as MagicMock in sys.modules so that Mobile can be imported.
* Vehicle_Data and Ground_Weapon_Data (which also pull in Aircraft) are replaced
  with thin fake modules whose internal dicts are mutated per test.
* Ship_Data and Ship_Weapon_Data are imported from the real modules (they have
  no circular dependency) and used with stub instances.
"""

import sys
import types
import unittest
from unittest.mock import MagicMock, patch
from sympy import Point3D

# ── Pre-inject Aircraft circular-import chain ──────────────────────────────
for _m in [
    'Code.Dynamic_War_Manager.Source.Asset.Aircraft',
    'Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data',
    'Code.Dynamic_War_Manager.Source.Asset.Aircraft_Loadouts',
    'Code.Dynamic_War_Manager.Source.Asset.Aircraft_Weapon_Data',
]:
    sys.modules.setdefault(_m, MagicMock())

# ── Fake Vehicle_Data module ───────────────────────────────────────────────
class _FakeVehicleData:
    _registry: dict = {}

_vd_mod = types.ModuleType('Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data')
_vd_mod.Vehicle_Data = _FakeVehicleData
sys.modules['Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data'] = _vd_mod

# ── Fake Ground_Weapon_Data module ─────────────────────────────────────────
# Mutable dict — mutated in setUp/test, cleared between tests.
_FAKE_GW: dict = {}

_gwd_mod = types.ModuleType('Code.Dynamic_War_Manager.Source.Asset.Ground_Weapon_Data')
_gwd_mod.GROUND_WEAPONS = _FAKE_GW
sys.modules['Code.Dynamic_War_Manager.Source.Asset.Ground_Weapon_Data'] = _gwd_mod

# ── Real Ship_Data and Ship_Weapon_Data (safe — no circular deps) ──────────
from Code.Dynamic_War_Manager.Source.Asset.Ship_Data import Ship_Data          # noqa
from Code.Dynamic_War_Manager.Source.Asset.Ship_Weapon_Data import SHIP_WEAPONS  # noqa (real data)

# ── Mobile (importable now that the chain is mocked) ──────────────────────
from Code.Dynamic_War_Manager.Source.Asset.Mobile import Mobile                # noqa
# Cylinder is intentionally NOT imported here: Mobile.py uses a different
# sys.modules path ('Dynamic_War_Manager…' vs 'Code.Dynamic_War_Manager…'),
# so isinstance checks would always fail.  We verify by class name instead.

_MOBILE_LOGGER = 'Code.Dynamic_War_Manager.Source.Asset.Mobile.logger'


# ─────────────────────────────────────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────────────────────────────────────

class _MobileStub:
    """Minimal object that carries Mobile methods as bound methods."""
    air_defense_volume = Mobile.air_defense_volume
    combat_range       = Mobile.combat_range

    def __init__(self, position=None, model=None):
        self._position = position
        self._model = model


class _VehicleRecord:
    """Stub data record whose isinstance(_, Ship_Data) is False."""
    def __init__(self, weapons: dict):
        self.weapons = weapons


def _ship_record(weapons: dict) -> Ship_Data:
    """Build a Ship_Data instance without running __init__ (bypasses the validator)."""
    obj = object.__new__(Ship_Data)
    obj.weapons = weapons
    return obj


def _pos(x: float = 0.0, y: float = 0.0, z: float = 0.0) -> Point3D:
    return Point3D(x, y, z)


def _clean_ship_registry():
    """Remove test-* keys from the real Ship_Data registry."""
    for key in [k for k in Ship_Data._registry if k.startswith('test-')]:
        del Ship_Data._registry[key]


# ─────────────────────────────────────────────────────────────────────────────
# Test classes
# ─────────────────────────────────────────────────────────────────────────────

class TestNoneGuards(unittest.TestCase):
    """air_defense_volume() must return None for invalid / incomplete state."""

    def setUp(self):
        _FakeVehicleData._registry.clear()
        _FAKE_GW.clear()
        _clean_ship_registry()
        self._log = patch(_MOBILE_LOGGER, MagicMock())
        self._log.start()

    def tearDown(self):
        self._log.stop()
        _clean_ship_registry()

    def test_no_position_returns_none(self):
        stub = _MobileStub(position=None, model='any-model')
        self.assertIsNone(stub.air_defense_volume())

    def test_no_model_returns_none(self):
        stub = _MobileStub(position=_pos(), model=None)
        self.assertIsNone(stub.air_defense_volume())

    def test_model_not_in_any_registry_returns_none(self):
        stub = _MobileStub(position=_pos(), model='ghost-model')
        self.assertIsNone(stub.air_defense_volume())

    def test_tank_with_antitank_missiles_no_altitude_data_returns_none(self):
        _FAKE_GW['MISSILES'] = {
            '9K119M': {'range': {'direct': 5000}},  # no min/max_altitude
        }
        _FakeVehicleData._registry['T-90M'] = _VehicleRecord({'MISSILES': [('9K119M', 6)]})
        stub = _MobileStub(position=_pos(), model='T-90M')
        self.assertIsNone(stub.air_defense_volume())

    def test_non_ad_weapon_type_cannons_returns_none(self):
        """CANNONS (not AA_CANNONS) is ignored by the method."""
        _FAKE_GW['CANNONS'] = {
            'M256-120mm': {'range': {'direct': 3000}, 'min_altitude': 0, 'max_altitude': 1000},
        }
        _FakeVehicleData._registry['M1A2'] = _VehicleRecord({'CANNONS': [('M256-120mm', 42)]})
        stub = _MobileStub(position=_pos(), model='M1A2')
        self.assertIsNone(stub.air_defense_volume())


class TestVehicle(unittest.TestCase):
    """Vehicle (Ground) air defense — AAA, SAM Small/Medium/Big, mixed weapons."""

    def setUp(self):
        _FakeVehicleData._registry.clear()
        _FAKE_GW.clear()
        _clean_ship_registry()
        self._log = patch(_MOBILE_LOGGER, MagicMock())
        self._log.start()

    def tearDown(self):
        self._log.stop()
        _clean_ship_registry()

    # ── AAA ──────────────────────────────────────────────────────────────────

    def test_aaa_single_cannon_radius(self):
        _FAKE_GW['AA_CANNONS'] = {
            'AZP-23-23mm': {'range': {'direct': 2500}, 'min_altitude': 0, 'max_altitude': 1500},
        }
        _FakeVehicleData._registry['ZSU-23-4'] = _VehicleRecord(
            {'AA_CANNONS': [('AZP-23-23mm', 2000)]}
        )
        cyl = _MobileStub(position=_pos(), model='ZSU-23-4').air_defense_volume()
        self.assertEqual(type(cyl).__name__, 'Cylinder')
        self.assertEqual(cyl.radius, 2500.0)

    def test_aaa_single_cannon_height(self):
        _FAKE_GW['AA_CANNONS'] = {
            'AZP-23-23mm': {'range': {'direct': 2500}, 'min_altitude': 0, 'max_altitude': 1500},
        }
        _FakeVehicleData._registry['ZSU-23-4'] = _VehicleRecord(
            {'AA_CANNONS': [('AZP-23-23mm', 2000)]}
        )
        cyl = _MobileStub(position=_pos(), model='ZSU-23-4').air_defense_volume()
        self.assertEqual(cyl.height, 1500.0)  # max_alt - min_alt

    def test_aaa_bottom_center_z_offset(self):
        """bottom_center.z = asset.z + min_altitude."""
        _FAKE_GW['AA_CANNONS'] = {
            'AZP-23-23mm': {'range': {'direct': 2500}, 'min_altitude': 0, 'max_altitude': 1500},
        }
        _FakeVehicleData._registry['ZSU-23-4'] = _VehicleRecord(
            {'AA_CANNONS': [('AZP-23-23mm', 2000)]}
        )
        cyl = _MobileStub(position=_pos(0, 0, 300), model='ZSU-23-4').air_defense_volume()
        self.assertAlmostEqual(float(cyl.bottom_center.z), 300.0 + 0.0)

    # ── SAM Medium ────────────────────────────────────────────────────────────

    def test_sam_medium_radius(self):
        _FAKE_GW['MISSILES'] = {
            '9M38-SAM': {'range': {'direct': 35000}, 'min_altitude': 15, 'max_altitude': 22000},
        }
        _FakeVehicleData._registry['9K37-Buk'] = _VehicleRecord(
            {'MISSILES': [('9M38-SAM', 4)]}
        )
        cyl = _MobileStub(position=_pos(), model='9K37-Buk').air_defense_volume()
        self.assertEqual(cyl.radius, 35000.0)

    def test_sam_medium_height(self):
        _FAKE_GW['MISSILES'] = {
            '9M38-SAM': {'range': {'direct': 35000}, 'min_altitude': 15, 'max_altitude': 22000},
        }
        _FakeVehicleData._registry['9K37-Buk'] = _VehicleRecord(
            {'MISSILES': [('9M38-SAM', 4)]}
        )
        cyl = _MobileStub(position=_pos(), model='9K37-Buk').air_defense_volume()
        self.assertEqual(cyl.height, 22000.0 - 15.0)

    def test_sam_medium_bottom_center_z(self):
        _FAKE_GW['MISSILES'] = {
            '9M38-SAM': {'range': {'direct': 35000}, 'min_altitude': 15, 'max_altitude': 22000},
        }
        _FakeVehicleData._registry['9K37-Buk'] = _VehicleRecord(
            {'MISSILES': [('9M38-SAM', 4)]}
        )
        cyl = _MobileStub(position=_pos(0, 0, 500), model='9K37-Buk').air_defense_volume()
        self.assertAlmostEqual(float(cyl.bottom_center.z), 500.0 + 15.0)

    # ── SAM Big ───────────────────────────────────────────────────────────────

    def test_sam_big_radius(self):
        _FAKE_GW['MISSILES'] = {
            '5V55R-SAM': {'range': {'direct': 75000}, 'min_altitude': 25, 'max_altitude': 27000},
        }
        _FakeVehicleData._registry['S-300PS'] = _VehicleRecord(
            {'MISSILES': [('5V55R-SAM', 4)]}
        )
        cyl = _MobileStub(position=_pos(), model='S-300PS').air_defense_volume()
        self.assertEqual(cyl.radius, 75000.0)

    def test_sam_big_height(self):
        _FAKE_GW['MISSILES'] = {
            '5V55R-SAM': {'range': {'direct': 75000}, 'min_altitude': 25, 'max_altitude': 27000},
        }
        _FakeVehicleData._registry['S-300PS'] = _VehicleRecord(
            {'MISSILES': [('5V55R-SAM', 4)]}
        )
        cyl = _MobileStub(position=_pos(), model='S-300PS').air_defense_volume()
        self.assertEqual(cyl.height, 27000.0 - 25.0)

    # ── Mixed weapons (Tunguska: AA cannons + SAM missiles) ──────────────────

    def test_mixed_min_alt_is_minimum_across_weapons(self):
        """min_alt = min(cannon.min_alt=0, missile.min_alt=15) = 0."""
        _FAKE_GW['AA_CANNONS'] = {
            '2A38M-30mm': {'range': {'direct': 4000}, 'min_altitude': 0, 'max_altitude': 3500},
        }
        _FAKE_GW['MISSILES'] = {
            '9M311-SAM': {'range': {'direct': 8000}, 'min_altitude': 15, 'max_altitude': 3500},
        }
        _FakeVehicleData._registry['2K22-Tunguska'] = _VehicleRecord({
            'AA_CANNONS': [('2A38M-30mm', 1904)],
            'MISSILES':   [('9M311-SAM', 8)],
        })
        cyl = _MobileStub(position=_pos(0, 0, 200), model='2K22-Tunguska').air_defense_volume()
        # min_alt = 0 → bottom_center.z = 200 + 0 = 200
        self.assertAlmostEqual(float(cyl.bottom_center.z), 200.0)

    def test_mixed_radius_is_max_range_across_weapons(self):
        """radius = max(cannon.range=4000, missile.range=8000) = 8000."""
        _FAKE_GW['AA_CANNONS'] = {
            '2A38M-30mm': {'range': {'direct': 4000}, 'min_altitude': 0, 'max_altitude': 3500},
        }
        _FAKE_GW['MISSILES'] = {
            '9M311-SAM': {'range': {'direct': 8000}, 'min_altitude': 15, 'max_altitude': 3500},
        }
        _FakeVehicleData._registry['2K22-Tunguska'] = _VehicleRecord({
            'AA_CANNONS': [('2A38M-30mm', 1904)],
            'MISSILES':   [('9M311-SAM', 8)],
        })
        cyl = _MobileStub(position=_pos(), model='2K22-Tunguska').air_defense_volume()
        self.assertEqual(cyl.radius, 8000.0)

    def test_mixed_max_alt_is_max_across_weapons(self):
        """max_alt = max(cannon.max=4000, missile.max=3500) = 4000."""
        _FAKE_GW['AA_CANNONS'] = {
            'S-68-57mm': {'range': {'direct': 4000}, 'min_altitude': 50, 'max_altitude': 4000},
        }
        _FAKE_GW['MISSILES'] = {
            '9M311-SAM': {'range': {'direct': 8000}, 'min_altitude': 15, 'max_altitude': 3500},
        }
        _FakeVehicleData._registry['test-mixed'] = _VehicleRecord({
            'AA_CANNONS': [('S-68-57mm', 300)],
            'MISSILES':   [('9M311-SAM', 8)],
        })
        cyl = _MobileStub(position=_pos(), model='test-mixed').air_defense_volume()
        # min_alt=min(50,15)=15, max_alt=max(4000,3500)=4000 → height=3985
        self.assertEqual(cyl.height, 4000.0 - 15.0)

    def test_position_xy_preserved(self):
        _FAKE_GW['AA_CANNONS'] = {
            'AZP-23-23mm': {'range': {'direct': 2500}, 'min_altitude': 0, 'max_altitude': 1500},
        }
        _FakeVehicleData._registry['ZSU-23-4'] = _VehicleRecord(
            {'AA_CANNONS': [('AZP-23-23mm', 2000)]}
        )
        cyl = _MobileStub(position=_pos(1234.5, 6789.0, 100), model='ZSU-23-4').air_defense_volume()
        self.assertAlmostEqual(float(cyl.bottom_center.x), 1234.5)
        self.assertAlmostEqual(float(cyl.bottom_center.y), 6789.0)

    def test_weapon_without_altitude_data_is_skipped(self):
        """Anti-tank missile (no altitude keys) is ignored; SAM contributes."""
        _FAKE_GW['MISSILES'] = {
            '9K119M':   {'range': {'direct': 5000}},  # no altitude → skip
            '9M38-SAM': {'range': {'direct': 35000}, 'min_altitude': 15, 'max_altitude': 22000},
        }
        _FakeVehicleData._registry['test-mixed-missiles'] = _VehicleRecord(
            {'MISSILES': [('9K119M', 6), ('9M38-SAM', 4)]}
        )
        cyl = _MobileStub(position=_pos(), model='test-mixed-missiles').air_defense_volume()
        self.assertIsNotNone(cyl)
        self.assertEqual(cyl.radius, 35000.0)


class TestShip(unittest.TestCase):
    """Ship air defense — uses real Ship_Data._registry + real SHIP_WEAPONS."""

    def setUp(self):
        _FakeVehicleData._registry.clear()
        _FAKE_GW.clear()
        _clean_ship_registry()
        self._log = patch(_MOBILE_LOGGER, MagicMock())
        self._log.start()

    def tearDown(self):
        self._log.stop()
        _clean_ship_registry()

    def test_rim162_radius(self):
        """RIM-162-ESSM: range 50 km → radius = 50 000 m."""
        Ship_Data._registry['test-destroyer'] = _ship_record(
            {'MISSILES_SAM': [('RIM-162-ESSM', 32)]}
        )
        cyl = _MobileStub(position=_pos(), model='test-destroyer').air_defense_volume()
        self.assertEqual(type(cyl).__name__, 'Cylinder')
        self.assertEqual(cyl.radius, 50_000.0)

    def test_rim162_height(self):
        """RIM-162-ESSM: min_alt=15, max_alt=15000 → height=14985."""
        Ship_Data._registry['test-destroyer'] = _ship_record(
            {'MISSILES_SAM': [('RIM-162-ESSM', 32)]}
        )
        cyl = _MobileStub(position=_pos(), model='test-destroyer').air_defense_volume()
        self.assertEqual(cyl.height, 15000.0 - 15.0)

    def test_ship_bottom_center_z(self):
        """bottom_center.z = ship.z + min_altitude of SAM."""
        Ship_Data._registry['test-destroyer'] = _ship_record(
            {'MISSILES_SAM': [('RIM-162-ESSM', 32)]}
        )
        cyl = _MobileStub(position=_pos(0, 0, 10), model='test-destroyer').air_defense_volume()
        # RIM-162 min_altitude=15 → z = 10 + 15 = 25
        self.assertAlmostEqual(float(cyl.bottom_center.z), 25.0)

    def test_multiple_sam_min_alt_is_minimum(self):
        """Two SAMs: RIM-162 (min=15, range=50km) + RIM-7M (min=15, range=19km)."""
        Ship_Data._registry['test-destroyer-multi'] = _ship_record(
            {'MISSILES_SAM': [('RIM-162-ESSM', 32), ('RIM-7M-Sea-Sparrow', 8)]}
        )
        cyl = _MobileStub(position=_pos(), model='test-destroyer-multi').air_defense_volume()
        self.assertEqual(cyl.radius, 50_000.0)          # max range
        self.assertEqual(cyl.height, 15000.0 - 15.0)   # min=15, max=15000
        self.assertAlmostEqual(float(cyl.bottom_center.z), 15.0)

    def test_s300f_radius_and_height(self):
        """S-300F: range 150 km → 150 000 m radius; min=25, max=27000."""
        Ship_Data._registry['test-kirov'] = _ship_record(
            {'MISSILES_SAM': [('S-300F', 4)]}
        )
        cyl = _MobileStub(position=_pos(), model='test-kirov').air_defense_volume()
        self.assertEqual(cyl.radius, 150_000.0)
        self.assertEqual(cyl.height, 27000.0 - 25.0)

    def test_ship_position_xy_preserved(self):
        Ship_Data._registry['test-frigate'] = _ship_record(
            {'MISSILES_SAM': [('RIM-7M-Sea-Sparrow', 8)]}
        )
        cyl = _MobileStub(position=_pos(555.0, 333.0, 0), model='test-frigate').air_defense_volume()
        self.assertAlmostEqual(float(cyl.bottom_center.x), 555.0)
        self.assertAlmostEqual(float(cyl.bottom_center.y), 333.0)

    def test_non_sam_ship_weapons_ignored(self):
        """MISSILES_ASM weapons on a ship are ignored (not AD)."""
        Ship_Data._registry['test-only-asm'] = _ship_record(
            {'MISSILES_ASM': [('RGM-84-Harpoon', 8)]}
        )
        cyl = _MobileStub(position=_pos(), model='test-only-asm').air_defense_volume()
        self.assertIsNone(cyl)


# ─────────────────────────────────────────────────────────────────────────────
# combat_range() tests
# ─────────────────────────────────────────────────────────────────────────────

class TestCombatRangeNoneGuards(unittest.TestCase):
    """combat_range() must return None for invalid / incomplete state."""

    def setUp(self):
        _FakeVehicleData._registry.clear()
        _FAKE_GW.clear()
        _clean_ship_registry()
        self._log = patch(_MOBILE_LOGGER, MagicMock())
        self._log.start()

    def tearDown(self):
        self._log.stop()
        _clean_ship_registry()

    def test_no_model_returns_none(self):
        stub = _MobileStub(position=_pos(), model=None)
        self.assertIsNone(stub.combat_range())

    def test_model_not_in_any_registry_returns_none(self):
        stub = _MobileStub(position=_pos(), model='ghost-model')
        self.assertIsNone(stub.combat_range())

    def test_aaa_only_returns_none(self):
        """Only AA_CANNONS (air-defense) → no offensive range → None."""
        _FAKE_GW['AA_CANNONS'] = {
            'AZP-23-23mm': {'range': {'direct': 2500}, 'min_altitude': 0, 'max_altitude': 1500},
        }
        _FakeVehicleData._registry['ZSU-23-4'] = _VehicleRecord(
            {'AA_CANNONS': [('AZP-23-23mm', 2000)]}
        )
        self.assertIsNone(_MobileStub(position=_pos(), model='ZSU-23-4').combat_range())

    def test_sam_missile_only_returns_none(self):
        """MISSILES with min_altitude (SAM) are skipped → None."""
        _FAKE_GW['MISSILES'] = {
            '9M38-SAM': {'range': {'direct': 35000}, 'min_altitude': 15, 'max_altitude': 22000},
        }
        _FakeVehicleData._registry['9K37-Buk'] = _VehicleRecord(
            {'MISSILES': [('9M38-SAM', 4)]}
        )
        self.assertIsNone(_MobileStub(position=_pos(), model='9K37-Buk').combat_range())

    def test_ship_sam_only_returns_none(self):
        """Ship with only MISSILES_SAM → no offensive range → None."""
        Ship_Data._registry['test-sam-ship'] = _ship_record(
            {'MISSILES_SAM': [('RIM-162-ESSM', 32)]}
        )
        self.assertIsNone(_MobileStub(position=_pos(), model='test-sam-ship').combat_range())


class TestCombatRangeVehicle(unittest.TestCase):
    """Vehicle ground-attack weapon scenarios."""

    def setUp(self):
        _FakeVehicleData._registry.clear()
        _FAKE_GW.clear()
        _clean_ship_registry()
        self._log = patch(_MOBILE_LOGGER, MagicMock())
        self._log.start()

    def tearDown(self):
        self._log.stop()
        _clean_ship_registry()

    def test_artillery_returns_indirect_range(self):
        """ARTILLERY: max(direct=0, indirect=18500) = 18500."""
        _FAKE_GW['ARTILLERY'] = {
            '2A33-152mm': {'range': {'direct': 0, 'indirect': 18500}},
        }
        _FakeVehicleData._registry['2S3'] = _VehicleRecord(
            {'ARTILLERY': [('2A33-152mm', 40)]}
        )
        self.assertEqual(_MobileStub(position=_pos(), model='2S3').combat_range(), 18500.0)

    def test_cannon_uses_max_of_direct_and_indirect(self):
        """CANNONS: max(direct=2120, indirect=10000) = 10000."""
        _FAKE_GW['CANNONS'] = {
            '2A46M': {'range': {'direct': 2120, 'indirect': 10000}},
        }
        _FakeVehicleData._registry['T-90M'] = _VehicleRecord(
            {'CANNONS': [('2A46M', 42)]}
        )
        self.assertEqual(_MobileStub(position=_pos(), model='T-90M').combat_range(), 10000.0)

    def test_rocket_returns_plain_range(self):
        """ROCKETS: plain range value (metres) returned directly."""
        _FAKE_GW['ROCKETS'] = {
            '122mm-Grad-Rocket': {'range': 20380},
        }
        _FakeVehicleData._registry['BM-21'] = _VehicleRecord(
            {'ROCKETS': [('122mm-Grad-Rocket', 40)]}
        )
        self.assertEqual(_MobileStub(position=_pos(), model='BM-21').combat_range(), 20380.0)

    def test_mortar_returns_indirect_range(self):
        """MORTARS: max(direct=0, indirect=2600) = 2600."""
        _FAKE_GW['MORTARS'] = {
            'M933-60mm': {'range': {'direct': 0, 'indirect': 2600}},
        }
        _FakeVehicleData._registry['Merkava'] = _VehicleRecord(
            {'MORTARS': [('M933-60mm', 30)]}
        )
        self.assertEqual(_MobileStub(position=_pos(), model='Merkava').combat_range(), 2600.0)

    def test_antitank_missile_included(self):
        """MISSILES without min_altitude (anti-tank) → included."""
        _FAKE_GW['MISSILES'] = {
            '9K119M': {'range': {'direct': 5000}},  # no min_altitude
        }
        _FakeVehicleData._registry['T-90M-atgm'] = _VehicleRecord(
            {'MISSILES': [('9K119M', 6)]}
        )
        self.assertEqual(_MobileStub(position=_pos(), model='T-90M-atgm').combat_range(), 5000.0)

    def test_sam_missile_excluded_antitank_included(self):
        """Mixed MISSILES: SAM (has min_altitude) skipped, anti-tank missile used."""
        _FAKE_GW['MISSILES'] = {
            '9M38-SAM': {'range': {'direct': 35000}, 'min_altitude': 15, 'max_altitude': 22000},
            '9K119M':   {'range': {'direct': 5000}},
        }
        _FakeVehicleData._registry['test-mixed'] = _VehicleRecord(
            {'MISSILES': [('9M38-SAM', 4), ('9K119M', 6)]}
        )
        self.assertEqual(_MobileStub(position=_pos(), model='test-mixed').combat_range(), 5000.0)

    def test_multiple_weapon_types_returns_max(self):
        """Artillery (18500) + rockets (70000) → max = 70000."""
        _FAKE_GW['ARTILLERY'] = {
            '2A33-152mm': {'range': {'direct': 0, 'indirect': 18500}},
        }
        _FAKE_GW['ROCKETS'] = {
            '300mm-Smerch-Rocket': {'range': 70000},
        }
        _FakeVehicleData._registry['combined'] = _VehicleRecord({
            'ARTILLERY': [('2A33-152mm', 40)],
            'ROCKETS':   [('300mm-Smerch-Rocket', 12)],
        })
        self.assertEqual(_MobileStub(position=_pos(), model='combined').combat_range(), 70000.0)

    def test_aaa_cannon_and_artillery_returns_only_artillery(self):
        """AA_CANNONS ignored; only ARTILLERY contributes."""
        _FAKE_GW['AA_CANNONS'] = {
            'AZP-23-23mm': {'range': {'direct': 2500}, 'min_altitude': 0, 'max_altitude': 1500},
        }
        _FAKE_GW['ARTILLERY'] = {
            '2A33-152mm': {'range': {'direct': 0, 'indirect': 18500}},
        }
        _FakeVehicleData._registry['test-spg'] = _VehicleRecord({
            'AA_CANNONS': [('AZP-23-23mm', 500)],
            'ARTILLERY':  [('2A33-152mm', 40)],
        })
        self.assertEqual(_MobileStub(position=_pos(), model='test-spg').combat_range(), 18500.0)

    def test_returns_float(self):
        """Return type must be float."""
        _FAKE_GW['ROCKETS'] = {'122mm-Grad-Rocket': {'range': 20380}}
        _FakeVehicleData._registry['BM-21-type'] = _VehicleRecord(
            {'ROCKETS': [('122mm-Grad-Rocket', 40)]}
        )
        result = _MobileStub(position=_pos(), model='BM-21-type').combat_range()
        self.assertIsInstance(result, float)


class TestCombatRangeShip(unittest.TestCase):
    """Ship naval-attack weapon scenarios — ranges in km converted to metres."""

    def setUp(self):
        _FakeVehicleData._registry.clear()
        _FAKE_GW.clear()
        _clean_ship_registry()
        self._log = patch(_MOBILE_LOGGER, MagicMock())
        self._log.start()

    def tearDown(self):
        self._log.stop()
        _clean_ship_registry()

    def test_missiles_asm_range_converted_km_to_m(self):
        """MISSILES_ASM range 280 km → 280 000 m."""
        Ship_Data._registry['test-destroyer'] = _ship_record(
            {'MISSILES_ASM': [('RGM-84-Harpoon', 8)]}
        )
        self.assertEqual(
            _MobileStub(position=_pos(), model='test-destroyer').combat_range(),
            280_000.0
        )

    def test_torpedo_range_converted_km_to_m(self):
        """MISSILES_TORPEDO range 50 km → 50 000 m."""
        Ship_Data._registry['test-sub'] = _ship_record(
            {'MISSILES_TORPEDO': [('Mk-48', 4)]}
        )
        self.assertEqual(
            _MobileStub(position=_pos(), model='test-sub').combat_range(),
            50_000.0
        )

    def test_guns_range_converted_km_to_m(self):
        """GUNS range 24 km → 24 000 m."""
        Ship_Data._registry['test-frigate-gun'] = _ship_record(
            {'GUNS': [('Mk-45-5in', 1)]}
        )
        self.assertEqual(
            _MobileStub(position=_pos(), model='test-frigate-gun').combat_range(),
            24_000.0
        )

    def test_multiple_ship_weapons_returns_max(self):
        """Harpoon (280 km) + Mk-48 torpedo (50 km) + Mk-45 gun (24 km) → 280 000 m."""
        Ship_Data._registry['test-multi'] = _ship_record({
            'MISSILES_ASM':    [('RGM-84-Harpoon', 8)],
            'MISSILES_TORPEDO': [('Mk-48', 4)],
            'GUNS':            [('Mk-45-5in', 1)],
        })
        self.assertEqual(
            _MobileStub(position=_pos(), model='test-multi').combat_range(),
            280_000.0
        )

    def test_ciws_excluded(self):
        """CIWS is not in _SHIP_ATTACK types → ignored → None."""
        Ship_Data._registry['test-ciws-only'] = _ship_record(
            {'CIWS': [('Phalanx', 1)]}
        )
        self.assertIsNone(
            _MobileStub(position=_pos(), model='test-ciws-only').combat_range()
        )

    def test_sam_and_asm_returns_asm_range(self):
        """MISSILES_SAM excluded; MISSILES_ASM contributes → Tomahawk 1600 km."""
        Ship_Data._registry['test-cruiser'] = _ship_record({
            'MISSILES_SAM': [('RIM-156-SM-2ER', 80)],
            'MISSILES_ASM': [('BGM-109-Tomahawk', 122)],
        })
        self.assertEqual(
            _MobileStub(position=_pos(), model='test-cruiser').combat_range(),
            1_600_000.0
        )

    def test_returns_float(self):
        """Return type must be float."""
        Ship_Data._registry['test-destroyer-type'] = _ship_record(
            {'MISSILES_ASM': [('RGM-84-Harpoon', 8)]}
        )
        result = _MobileStub(position=_pos(), model='test-destroyer-type').combat_range()
        self.assertIsInstance(result, float)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--tests-only', action='store_true')
    args, remaining = parser.parse_known_args()
    sys.argv = [sys.argv[0]] + remaining
    unittest.main(verbosity=2)
