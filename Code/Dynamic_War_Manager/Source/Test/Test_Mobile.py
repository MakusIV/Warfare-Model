"""Tests for Mobile — air_defense_volume() and combat_range().

Setup strategy
--------------
* Mobile itself imports cleanly now (no circular-import blocker), so it is
  imported directly from the real module.
* Vehicle_Data and Ground_Weapon_Data are resolved lazily *inside*
  Mobile.air_defense_volume()/combat_range() (function-local imports), so
  they can be swapped for thin fake modules whose internal dicts are mutated
  per test. That swap is installed in setUpModule()/removed in
  tearDownModule() — scoped to this module's own test run — instead of at
  import time, so it can never leak into other test files collected by
  `unittest discover` in the same process (see [[feedback_circular_import_workaround]]
  for the leakage this used to cause).
* Ship_Data and Ship_Weapon_Data are imported from the real modules (they have
  no circular dependency) and used with stub instances.
"""

import sys
import types
import unittest
from unittest.mock import MagicMock, patch
from sympy import Point3D

# ── Real Mobile, Ship_Data and Ship_Weapon_Data (all import cleanly) ───────
from Code.Dynamic_War_Manager.Source.Asset.Mobile import (                    # noqa
    Mobile, default_speed_profile, SPEED_REGIME_KEYS, SPEED_PROFILE_KEYS,
    DETECTION_MODES, DETECTION_SENSORS, DETECTION_RANGE_TYPES)
from Code.Dynamic_War_Manager.Source.Asset.Ship_Data import Ship_Data          # noqa
from Code.Dynamic_War_Manager.Source.Asset.Ship_Weapon_Data import SHIP_WEAPONS  # noqa (real data)
# Cylinder is intentionally NOT imported here: Mobile.py uses a different
# sys.modules path ('Dynamic_War_Manager…' vs 'Code.Dynamic_War_Manager…'),
# so isinstance checks would always fail.  We verify by class name instead.

_MOBILE_LOGGER = 'Code.Dynamic_War_Manager.Source.Asset.Mobile.logger'

_VD_MODULE_NAME = 'Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data'
_GWD_MODULE_NAME = 'Code.Dynamic_War_Manager.Source.Asset.Ground_Weapon_Data'
_AD_MODULE_NAME = 'Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data'


# ── Fake Vehicle_Data module ───────────────────────────────────────────────
class _FakeVehicleData:
    _registry: dict = {}

_vd_mod = types.ModuleType(_VD_MODULE_NAME)
_vd_mod.Vehicle_Data = _FakeVehicleData

# ── Fake Ground_Weapon_Data module ─────────────────────────────────────────
# Mutable dict — mutated in setUp/test, cleared between tests.
_FAKE_GW: dict = {}

_gwd_mod = types.ModuleType(_GWD_MODULE_NAME)
_gwd_mod.GROUND_WEAPONS = _FAKE_GW

# ── Fake Aircraft_Data module ──────────────────────────────────────────────
# Serve a speed_profile_from_registry(), che interroga anche il registry aerei.
# Falsificarlo evita di importare il modulo reale (lento e molto verboso) e rende
# deterministico il dispatch fra i tre registry.
class _FakeAircraftData:
    _registry: dict = {}

_ad_mod = types.ModuleType(_AD_MODULE_NAME)
_ad_mod.Aircraft_Data = _FakeAircraftData

_sys_modules_patcher = patch.dict(sys.modules, {
    _VD_MODULE_NAME: _vd_mod,
    _GWD_MODULE_NAME: _gwd_mod,
    _AD_MODULE_NAME: _ad_mod,
})


def setUpModule():
    """Install the fakes only for the duration of this module's own test run."""
    _sys_modules_patcher.start()


def tearDownModule():
    """Remove the fakes immediately so other test files never see them."""
    _sys_modules_patcher.stop()


# ─────────────────────────────────────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────────────────────────────────────

class _MobileStub:
    """Minimal object that carries Mobile methods as bound methods."""
    air_defense_volume = Mobile.air_defense_volume
    combat_range       = Mobile.combat_range
    detection_range    = Mobile.detection_range
    # _sensor_range_km e' una @staticmethod su Mobile: va ri-decorata qui, altrimenti
    # assegnarla nel corpo della classe la trasformerebbe in un metodo d'istanza.
    _sensor_range_km   = staticmethod(Mobile._sensor_range_km)

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

    def test_adv_task_with_anti_air_included(self):
        """Weapon WITH altitude data AND task=['Anti_Air'] is included."""
        _FAKE_GW['AA_CANNONS'] = {
            'test-aa-gun': {
                'range': {'direct': 3000}, 'min_altitude': 0, 'max_altitude': 2000,
                'task': ['Anti_Air'],
            },
        }
        _FakeVehicleData._registry['test-aa-vehicle'] = _VehicleRecord(
            {'AA_CANNONS': [('test-aa-gun', 1)]}
        )
        cyl = _MobileStub(position=_pos(), model='test-aa-vehicle').air_defense_volume()
        self.assertIsNotNone(cyl)
        self.assertEqual(cyl.radius, 3000.0)

    def test_adv_task_without_anti_air_excluded(self):
        """Weapon WITH altitude data but task=['Anti_Tank'] (no Anti_Air) is excluded."""
        _FAKE_GW['MISSILES'] = {
            'test-atgm': {
                'range': {'direct': 5000}, 'min_altitude': 0, 'max_altitude': 1000,
                'task': ['Anti_Tank'],
            },
        }
        _FakeVehicleData._registry['test-atgm-vehicle'] = _VehicleRecord(
            {'MISSILES': [('test-atgm', 1)]}
        )
        cyl = _MobileStub(position=_pos(), model='test-atgm-vehicle').air_defense_volume()
        self.assertIsNone(cyl)

    def test_adv_no_task_field_backward_compatible(self):
        """Weapon with altitude data but NO task field is included (backward compat)."""
        _FAKE_GW['AA_CANNONS'] = {
            'test-notask': {'range': {'direct': 2000}, 'min_altitude': 0, 'max_altitude': 1500},
        }
        _FakeVehicleData._registry['test-notask-vehicle'] = _VehicleRecord(
            {'AA_CANNONS': [('test-notask', 1)]}
        )
        cyl = _MobileStub(position=_pos(), model='test-notask-vehicle').air_defense_volume()
        self.assertIsNotNone(cyl)
        self.assertEqual(cyl.radius, 2000.0)


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

    def test_auto_cannons_included(self):
        """AUTO_CANNONS type is included in _GROUND_ATTACK → range returned."""
        _FAKE_GW['AUTO_CANNONS'] = {
            'M242-Bushmaster': {'range': {'direct': 3000, 'indirect': 0}},
        }
        _FakeVehicleData._registry['M2-Bradley'] = _VehicleRecord(
            {'AUTO_CANNONS': [('M242-Bushmaster', 900)]}
        )
        self.assertEqual(
            _MobileStub(position=_pos(), model='M2-Bradley').combat_range(),
            3000.0
        )

    def test_weapon_with_anti_air_task_excluded_from_combat_range(self):
        """Weapon whose task list contains Anti_Air is excluded even in ground types."""
        _FAKE_GW['CANNONS'] = {
            'test-aa-gun': {'range': {'direct': 5000}, 'task': ['Anti_Air']},
        }
        _FakeVehicleData._registry['test-aa-vehicle'] = _VehicleRecord(
            {'CANNONS': [('test-aa-gun', 1)]}
        )
        self.assertIsNone(
            _MobileStub(position=_pos(), model='test-aa-vehicle').combat_range()
        )

    def test_weapon_with_non_anti_air_task_included(self):
        """Weapon whose task list does NOT contain Anti_Air is not excluded."""
        _FAKE_GW['CANNONS'] = {
            'test-tank-gun': {'range': {'direct': 3000}, 'task': ['Anti_Tank', 'Infantry_Support']},
        }
        _FakeVehicleData._registry['test-tank'] = _VehicleRecord(
            {'CANNONS': [('test-tank-gun', 1)]}
        )
        self.assertEqual(
            _MobileStub(position=_pos(), model='test-tank').combat_range(),
            3000.0
        )

    def test_weapon_without_task_field_included(self):
        """Weapon without a task field is not excluded by the task filter."""
        _FAKE_GW['ARTILLERY'] = {
            'test-howitzer': {'range': {'direct': 0, 'indirect': 15000}},
        }
        _FakeVehicleData._registry['test-arty'] = _VehicleRecord(
            {'ARTILLERY': [('test-howitzer', 1)]}
        )
        self.assertEqual(
            _MobileStub(position=_pos(), model='test-arty').combat_range(),
            15000.0
        )


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

    def test_guns_with_anti_air_task_excluded(self):
        """Real Mk-45-5in has task=['Anti_Air',...] → excluded from combat_range → None."""
        Ship_Data._registry['test-frigate-gun'] = _ship_record(
            {'GUNS': [('Mk-45-5in', 1)]}
        )
        self.assertIsNone(
            _MobileStub(position=_pos(), model='test-frigate-gun').combat_range()
        )

    def test_guns_range_converted_km_to_m(self):
        """GUNS without Anti_Air task: range 24 km → 24 000 m (km→m conversion)."""
        from Code.Dynamic_War_Manager.Source.Asset.Ship_Weapon_Data import SHIP_WEAPONS as _SW
        _SW['GUNS']['_test_gun_no_aa'] = {'range': 24}  # no task key → not excluded
        try:
            Ship_Data._registry['test-frigate-gun-noaa'] = _ship_record(
                {'GUNS': [('_test_gun_no_aa', 1)]}
            )
            self.assertEqual(
                _MobileStub(position=_pos(), model='test-frigate-gun-noaa').combat_range(),
                24_000.0
            )
        finally:
            del _SW['GUNS']['_test_gun_no_aa']

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


# ─────────────────────────────────────────────────────────────────────────────
# Profilo di velocita' canonico (Fase 1 del motore di sessione)
# ─────────────────────────────────────────────────────────────────────────────

class _SpeedStub(Mobile):
    """Mobile costruito senza __init__, per esercitare i soli metodi di velocita'."""

    def __init__(self, model=None, speed=None):   # noqa: D107  (bypassa Mobile.__init__)
        self._model = model
        self._speed = default_speed_profile() if speed is None else speed


class _Record:
    """Record di registry minimale: conta solo speed_data."""

    def __init__(self, speed_data):
        self.speed_data = speed_data


def _clean_ship_speed_registry():
    for key in [k for k in Ship_Data._registry if k.startswith('test-speed-')]:
        del Ship_Data._registry[key]


class TestSpeedSchema(unittest.TestCase):
    """default_speed_profile() e _validate_speed()."""

    def test_default_profile_has_canonical_keys(self):
        self.assertEqual(set(default_speed_profile()), set(SPEED_REGIME_KEYS))

    def test_default_profile_with_off_road(self):
        profile = default_speed_profile(off_road=True)
        self.assertEqual(set(profile["off_road"]), set(SPEED_REGIME_KEYS))

    def test_default_profile_is_a_fresh_object(self):
        """Regressione: il default era un dict mutabile nella firma di Mobile.__init__,
        quindi condiviso da tutte le istanze — scriverci sopra contaminava ogni asset."""
        first = default_speed_profile(off_road=True)
        second = default_speed_profile(off_road=True)
        first["nominal"] = 10.0
        first["off_road"]["max"] = 5.0

        self.assertIsNone(second["nominal"])
        self.assertIsNone(second["off_road"]["max"])
        self.assertIsNot(first["off_road"], second["off_road"])

    def test_validate_accepts_full_profile(self):
        profile = {"nominal": 10.0, "max": 20, "off_road": {"nominal": 5.0, "max": 5.0},
                   "reference_altitude": 10000.0}
        self.assertTrue(Mobile._validate_speed(profile)[0])

    def test_validate_accepts_none_values(self):
        self.assertTrue(Mobile._validate_speed({"nominal": None, "max": None})[0])

    def test_validate_accepts_empty_dict(self):
        self.assertTrue(Mobile._validate_speed({})[0])

    def test_validate_rejects_non_dict(self):
        ok, msg = Mobile._validate_speed(12.0)
        self.assertFalse(ok)
        self.assertIn("must be a dict", msg)

    def test_validate_rejects_unknown_key(self):
        ok, msg = Mobile._validate_speed({"cruise": 10.0})
        self.assertFalse(ok)
        self.assertIn("cruise", msg)

    def test_validate_rejects_negative_speed(self):
        self.assertFalse(Mobile._validate_speed({"nominal": -1.0})[0])

    def test_validate_rejects_bool(self):
        """bool e' sottoclasse di int: True non e' una velocita'."""
        self.assertFalse(Mobile._validate_speed({"nominal": True})[0])

    def test_validate_rejects_string(self):
        self.assertFalse(Mobile._validate_speed({"max": "fast"})[0])

    def test_validate_rejects_bad_off_road_type(self):
        ok, msg = Mobile._validate_speed({"off_road": 10.0})
        self.assertFalse(ok)
        self.assertIn("off_road", msg)

    def test_validate_rejects_bad_off_road_key(self):
        self.assertFalse(Mobile._validate_speed({"off_road": {"flank": 3.0}})[0])

    def test_validate_rejects_bad_off_road_value(self):
        self.assertFalse(Mobile._validate_speed({"off_road": {"nominal": -2.0}})[0])

    def test_validate_accepts_none_off_road(self):
        self.assertTrue(Mobile._validate_speed({"off_road": None})[0])

    def test_profile_keys_include_regime_keys(self):
        self.assertTrue(set(SPEED_REGIME_KEYS).issubset(set(SPEED_PROFILE_KEYS)))


class TestSpeedSetter(unittest.TestCase):
    """Il setter di speed, che prima era inutilizzabile."""

    def test_setter_assigns_valid_profile(self):
        """Regressione: il setter chiamava self.checkParam(speed=...), ma Vehicle, Ship e
        Aircraft sovrascrivono checkParam con firme che non accettano 'speed' — e
        Mobile.checkParam era per giunta dichiarata senza self. Ogni assegnazione
        sollevava TypeError."""
        stub = _SpeedStub()
        stub.speed = {"nominal": 12.5, "max": 16.5}

        self.assertEqual(stub.speed["nominal"], 12.5)

    def test_setter_rejects_invalid_profile(self):
        stub = _SpeedStub()

        with self.assertRaises(ValueError):
            stub.speed = {"cruise": 12.5}

    def test_checkparam_is_static_and_validates_speed(self):
        self.assertTrue(Mobile.checkParam(speed={"nominal": 1.0})[0])
        self.assertFalse(Mobile.checkParam(speed={"nope": 1.0})[0])

    def test_checkparam_validates_fire_range(self):
        self.assertTrue(Mobile.checkParam(fire_range=100.0)[0])
        self.assertFalse(Mobile.checkParam(fire_range="far")[0])

    def test_checkparam_accepts_no_argument(self):
        self.assertTrue(Mobile.checkParam()[0])


class TestSpeedProfileFromRegistry(unittest.TestCase):
    """Il ponte registry -> profilo canonico, con le conversioni di unita'."""

    def setUp(self):
        _FakeVehicleData._registry.clear()
        _FakeAircraftData._registry.clear()
        _clean_ship_speed_registry()
        self._log = patch(_MOBILE_LOGGER, MagicMock())
        self._log.start()

    def tearDown(self):
        self._log.stop()
        _FakeVehicleData._registry.clear()
        _FakeAircraftData._registry.clear()
        _clean_ship_speed_registry()

    # ── veicoli: km/h e mph → m/s ────────────────────────────────────────────
    def test_vehicle_metric_conversion(self):
        _FakeVehicleData._registry['t90'] = _Record({
            'sustained': {'metric': 'metric', 'speed': 45},
            'max':       {'metric': 'metric', 'speed': 60},
            'off_road':  {'metric': 'metric', 'speed': 45},
        })
        profile = _SpeedStub(model='t90').speed_profile_from_registry()

        self.assertAlmostEqual(profile['nominal'], 12.5)        # 45 km/h
        self.assertAlmostEqual(profile['max'], 60 / 3.6)        # 60 km/h
        self.assertAlmostEqual(profile['off_road']['nominal'], 12.5)

    def test_vehicle_off_road_regimes_coincide(self):
        """I dati hanno un solo regime fuoristrada: nominal e max off-road coincidono."""
        _FakeVehicleData._registry['v'] = _Record({
            'sustained': {'metric': 'metric', 'speed': 50},
            'max':       {'metric': 'metric', 'speed': 60},
            'off_road':  {'metric': 'metric', 'speed': 30},
        })
        profile = _SpeedStub(model='v').speed_profile_from_registry()

        self.assertEqual(profile['off_road']['nominal'], profile['off_road']['max'])

    def test_vehicle_imperial_conversion(self):
        _FakeVehicleData._registry['v'] = _Record({
            'sustained': {'metric': 'imperial', 'speed': 100},
            'max':       {'metric': 'imperial', 'speed': 120},
        })
        profile = _SpeedStub(model='v').speed_profile_from_registry()

        self.assertAlmostEqual(profile['nominal'], 100 * 0.44704)

    def test_vehicle_missing_regime_is_none(self):
        _FakeVehicleData._registry['v'] = _Record({'sustained': {'metric': 'metric', 'speed': 40}})
        profile = _SpeedStub(model='v').speed_profile_from_registry()

        self.assertIsNone(profile['max'])
        self.assertIsNone(profile['off_road']['nominal'])

    def test_vehicle_unknown_metric_raises(self):
        _FakeVehicleData._registry['v'] = _Record({'sustained': {'metric': 'furlongs', 'speed': 40}})

        with self.assertRaises(ValueError):
            _SpeedStub(model='v').speed_profile_from_registry()

    # ── navi: nodi → m/s, e max = flank ──────────────────────────────────────
    def test_ship_knots_conversion(self):
        Ship_Data._registry['test-speed-cv'] = _Record({
            'sustained': {'metric': 'nautical', 'speed': 28},
            'max':       {'metric': 'nautical', 'speed': 30},
            'flank':     {'metric': 'nautical', 'speed': 32},
        })
        profile = _SpeedStub(model='test-speed-cv').speed_profile_from_registry()

        self.assertAlmostEqual(profile['nominal'], 28 * 0.514444)

    def test_ship_max_is_the_flank_regime(self):
        """flank e' il regime di punta: ignorarlo sottostimerebbe la velocita' massima."""
        Ship_Data._registry['test-speed-cv'] = _Record({
            'sustained': {'metric': 'nautical', 'speed': 28},
            'max':       {'metric': 'nautical', 'speed': 30},
            'flank':     {'metric': 'nautical', 'speed': 32},
        })
        profile = _SpeedStub(model='test-speed-cv').speed_profile_from_registry()

        self.assertAlmostEqual(profile['max'], 32 * 0.514444)

    def test_ship_without_flank_falls_back_to_max(self):
        Ship_Data._registry['test-speed-s'] = _Record({
            'sustained': {'metric': 'nautical', 'speed': 20},
            'max':       {'metric': 'nautical', 'speed': 25},
        })
        profile = _SpeedStub(model='test-speed-s').speed_profile_from_registry()

        self.assertAlmostEqual(profile['max'], 25 * 0.514444)

    def test_ship_has_no_off_road_branch(self):
        Ship_Data._registry['test-speed-s'] = _Record({'sustained': {'metric': 'nautical', 'speed': 20}})
        profile = _SpeedStub(model='test-speed-s').speed_profile_from_registry()

        self.assertNotIn('off_road', profile)

    # ── aerei: TAS/IAS, quota di riferimento ─────────────────────────────────
    def test_aircraft_true_airspeed_conversion(self):
        _FakeAircraftData._registry['f14'] = _Record({
            'sustained': {'metric': 'metric', 'type_speed': 'true_airspeed',
                          'airspeed': 1000, 'altitude': 10000},
            'combat':    {'metric': 'metric', 'type_speed': 'true_airspeed',
                          'airspeed': 2485, 'altitude': 15200},
        })
        profile = _SpeedStub(model='f14').speed_profile_from_registry()

        self.assertAlmostEqual(profile['nominal'], 1000 / 3.6)
        self.assertAlmostEqual(profile['max'], 2485 / 3.6)

    def test_aircraft_reference_altitude_is_the_sustained_one(self):
        _FakeAircraftData._registry['f14'] = _Record({
            'sustained': {'metric': 'metric', 'type_speed': 'true_airspeed',
                          'airspeed': 1000, 'altitude': 10000},
        })
        profile = _SpeedStub(model='f14').speed_profile_from_registry()

        self.assertEqual(profile['reference_altitude'], 10000.0)

    def test_aircraft_max_is_the_highest_of_combat_and_emergency(self):
        _FakeAircraftData._registry['a'] = _Record({
            'sustained':  {'metric': 'metric', 'type_speed': 'true_airspeed',
                           'airspeed': 900, 'altitude': 9000},
            'combat':     {'metric': 'metric', 'type_speed': 'true_airspeed',
                           'airspeed': 1800, 'altitude': 12000},
            'emergency':  {'metric': 'metric', 'type_speed': 'true_airspeed',
                           'airspeed': 2100, 'altitude': 12000},
        })
        profile = _SpeedStub(model='a').speed_profile_from_registry()

        self.assertAlmostEqual(profile['max'], 2100 / 3.6)

    def test_aircraft_indicated_airspeed_is_converted_to_true(self):
        """IAS < TAS in quota: il profilo deve riportare la velocita' vera, piu' alta."""
        _FakeAircraftData._registry['a'] = _Record({
            'sustained': {'metric': 'metric', 'type_speed': 'indicated_airspeed',
                          'airspeed': 800, 'altitude': 10000},
        })
        profile = _SpeedStub(model='a').speed_profile_from_registry()

        self.assertGreater(profile['nominal'], 800 / 3.6)

    def test_aircraft_invalid_type_speed_raises(self):
        _FakeAircraftData._registry['a'] = _Record({
            'sustained': {'metric': 'metric', 'type_speed': 'guessed',
                          'airspeed': 800, 'altitude': 10000},
        })

        with self.assertRaises(ValueError):
            _SpeedStub(model='a').speed_profile_from_registry()

    # ── guardie ──────────────────────────────────────────────────────────────
    def test_no_model_returns_none(self):
        self.assertIsNone(_SpeedStub(model=None).speed_profile_from_registry())

    def test_unknown_model_returns_none(self):
        self.assertIsNone(_SpeedStub(model='nessuno').speed_profile_from_registry())

    def test_record_without_speed_data_returns_none(self):
        _FakeVehicleData._registry['v'] = _Record({})
        self.assertIsNone(_SpeedStub(model='v').speed_profile_from_registry())


class TestLoadSpeedFromRegistry(unittest.TestCase):
    """load_speed_from_registry(): assegna il profilo, o lascia il default."""

    def setUp(self):
        _FakeVehicleData._registry.clear()
        _FakeAircraftData._registry.clear()
        self._log = patch(_MOBILE_LOGGER, MagicMock())
        self._log.start()

    def tearDown(self):
        self._log.stop()
        _FakeVehicleData._registry.clear()
        _FakeAircraftData._registry.clear()

    def test_loads_and_assigns(self):
        _FakeVehicleData._registry['v'] = _Record({'sustained': {'metric': 'metric', 'speed': 36}})
        stub = _SpeedStub(model='v')

        self.assertTrue(stub.load_speed_from_registry())
        self.assertAlmostEqual(stub.speed['nominal'], 10.0)

    def test_unknown_model_keeps_default_and_returns_false(self):
        """Un modello sconosciuto non deve impedire la costruzione dell'asset."""
        stub = _SpeedStub(model='ignoto')

        self.assertFalse(stub.load_speed_from_registry())
        self.assertIsNone(stub.speed['nominal'])

    def test_loaded_profile_passes_its_own_validator(self):
        _FakeVehicleData._registry['v'] = _Record({
            'sustained': {'metric': 'metric', 'speed': 45},
            'max':       {'metric': 'metric', 'speed': 60},
            'off_road':  {'metric': 'metric', 'speed': 30},
        })
        stub = _SpeedStub(model='v')
        stub.load_speed_from_registry()

        self.assertTrue(Mobile._validate_speed(stub.speed)[0])


# ─────────────────────────────────────────────────────────────────────────────
# detection_range() tests
# ─────────────────────────────────────────────────────────────────────────────

def _caps(air=None, ground=None, sea=None):
    """capabilities dict nella forma dei registry: {mode: (bool, {range_type: km})}."""
    def _entry(value):
        if value is None:
            return (False, {'tracking_range': 0, 'acquisition_range': 0,
                            'engagement_range': 0, 'multi_target_capacity': 0})
        return value
    return {'air': _entry(air), 'ground': _entry(ground), 'sea': _entry(sea)}


def _sensor(air=None, ground=None, sea=None, model='sensor'):
    return {'model': model, 'capabilities': _caps(air, ground, sea)}


class _SensorRecord:
    """Record di registry con i soli campi sensore letti da detection_range()."""
    def __init__(self, radar=False, TVD=False):
        self.radar = radar
        self.TVD = TVD


class TestDetectionRangeArgumentDomain(unittest.TestCase):
    """Argomenti fuori dominio = errore di programmazione → ValueError, non None."""

    def setUp(self):
        _FakeVehicleData._registry.clear()
        _FakeVehicleData._registry['v'] = _SensorRecord(
            radar=_sensor(air=(True, {'acquisition_range': 50})))
        self._log = patch(_MOBILE_LOGGER, MagicMock())
        self._log.start()

    def tearDown(self):
        self._log.stop()
        _FakeVehicleData._registry.clear()

    def test_bad_mode_raises(self):
        with self.assertRaises(ValueError):
            _MobileStub(model='v').detection_range('underwater')

    def test_bad_sensor_raises(self):
        with self.assertRaises(ValueError):
            _MobileStub(model='v').detection_range('air', sensor='sonar')

    def test_bad_range_type_raises(self):
        with self.assertRaises(ValueError):
            _MobileStub(model='v').detection_range('air', range_type='multi_target_capacity')

    def test_valid_modes_are_the_registry_modes(self):
        """DETECTION_MODES viene da ACTION_TASKS: e' la stessa lista dei registry."""
        self.assertEqual(set(DETECTION_MODES), {'air', 'ground', 'sea'})


class TestDetectionRangeNoneGuards(unittest.TestCase):
    """Dati mancanti → None e mai eccezione: l'asset resta interrogabile."""

    def setUp(self):
        _FakeVehicleData._registry.clear()
        _FakeAircraftData._registry.clear()
        _clean_ship_registry()
        self._logger = MagicMock()
        self._log = patch(_MOBILE_LOGGER, self._logger)
        self._log.start()

    def tearDown(self):
        self._log.stop()
        _FakeVehicleData._registry.clear()
        _FakeAircraftData._registry.clear()
        _clean_ship_registry()

    def test_model_not_set(self):
        self.assertIsNone(_MobileStub().detection_range('air'))
        self._logger.warning.assert_called()

    def test_unknown_model(self):
        self.assertIsNone(_MobileStub(model='ignoto').detection_range('air'))
        self._logger.warning.assert_called()

    def test_no_sensors_at_all_is_not_a_warning(self):
        """radar/TVD == False e' un dato corretto (un carro): debug, non warning."""
        _FakeVehicleData._registry['tank'] = _SensorRecord(radar=False, TVD=False)

        self.assertIsNone(_MobileStub(model='tank').detection_range('air'))
        self._logger.warning.assert_not_called()

    def test_sensor_none_instead_of_false(self):
        _FakeVehicleData._registry['v'] = _SensorRecord(radar=None, TVD=None)
        self.assertIsNone(_MobileStub(model='v').detection_range('air'))

    def test_capability_flag_false(self):
        _FakeVehicleData._registry['v'] = _SensorRecord(
            radar=_sensor(air=(False, {'acquisition_range': 200})))
        self.assertIsNone(_MobileStub(model='v').detection_range('air'))

    def test_capability_dict_empty(self):
        """Ship_Data usa (False, {}) / (True, {}) per i modi non coperti."""
        _FakeVehicleData._registry['v'] = _SensorRecord(radar=_sensor(air=(True, {})))
        self.assertIsNone(_MobileStub(model='v').detection_range('air'))

    def test_zero_range_is_none(self):
        _FakeVehicleData._registry['v'] = _SensorRecord(
            radar=_sensor(air=(True, {'acquisition_range': 0})))
        self.assertIsNone(_MobileStub(model='v').detection_range('air'))

    def test_malformed_capability_is_discarded(self):
        _FakeVehicleData._registry['v'] = _SensorRecord(
            radar={'model': 'x', 'capabilities': {'air': 'broken', 'ground': (), 'sea': None}})
        self.assertIsNone(_MobileStub(model='v').detection_range('air'))
        self.assertIsNone(_MobileStub(model='v').detection_range('ground'))
        self.assertIsNone(_MobileStub(model='v').detection_range('sea'))

    def test_missing_capabilities_key(self):
        _FakeVehicleData._registry['v'] = _SensorRecord(radar={'model': 'x'})
        self.assertIsNone(_MobileStub(model='v').detection_range('air'))

    def test_boolean_range_value_is_not_a_number(self):
        _FakeVehicleData._registry['v'] = _SensorRecord(
            radar=_sensor(air=(True, {'acquisition_range': True})))
        self.assertIsNone(_MobileStub(model='v').detection_range('air'))

    def test_requested_range_type_absent(self):
        _FakeVehicleData._registry['v'] = _SensorRecord(
            radar=_sensor(air=(True, {'acquisition_range': 100})))
        self.assertIsNone(_MobileStub(model='v').detection_range('air', range_type='engagement_range'))


class TestDetectionRangeValues(unittest.TestCase):
    """Valori, unita' di misura e composizione radar+TVD."""

    def setUp(self):
        _FakeVehicleData._registry.clear()
        _FakeAircraftData._registry.clear()
        _clean_ship_registry()
        self._log = patch(_MOBILE_LOGGER, MagicMock())
        self._log.start()

    def tearDown(self):
        self._log.stop()
        _FakeVehicleData._registry.clear()
        _FakeAircraftData._registry.clear()
        _clean_ship_registry()

    def test_km_converted_to_metres(self):
        _FakeVehicleData._registry['v'] = _SensorRecord(
            radar=_sensor(air=(True, {'acquisition_range': 30})))
        self.assertAlmostEqual(_MobileStub(model='v').detection_range('air'), 30_000.0)

    def test_acquisition_is_the_default_range_type(self):
        _FakeVehicleData._registry['v'] = _SensorRecord(
            radar=_sensor(air=(True, {'acquisition_range': 30, 'tracking_range': 20,
                                      'engagement_range': 10})))
        stub = _MobileStub(model='v')
        self.assertAlmostEqual(stub.detection_range('air'), 30_000.0)
        self.assertAlmostEqual(stub.detection_range('air', range_type='tracking_range'), 20_000.0)
        self.assertAlmostEqual(stub.detection_range('air', range_type='engagement_range'), 10_000.0)

    def test_mode_selects_its_own_capability(self):
        _FakeVehicleData._registry['v'] = _SensorRecord(
            radar=_sensor(air=(True, {'acquisition_range': 100}),
                          ground=(True, {'acquisition_range': 40})))
        stub = _MobileStub(model='v')
        self.assertAlmostEqual(stub.detection_range('air'), 100_000.0)
        self.assertAlmostEqual(stub.detection_range('ground'), 40_000.0)
        self.assertIsNone(stub.detection_range('sea'))

    def test_radar_and_TVD_composed_with_max(self):
        """Il default e' il sensore che arriva piu' lontano, non la somma."""
        _FakeVehicleData._registry['v'] = _SensorRecord(
            radar=_sensor(air=(True, {'acquisition_range': 60})),
            TVD=_sensor(air=(True, {'acquisition_range': 12})))
        self.assertAlmostEqual(_MobileStub(model='v').detection_range('air'), 60_000.0)

    def test_TVD_wins_when_longer(self):
        _FakeVehicleData._registry['v'] = _SensorRecord(
            radar=_sensor(air=(True, {'acquisition_range': 5})),
            TVD=_sensor(air=(True, {'acquisition_range': 9})))
        self.assertAlmostEqual(_MobileStub(model='v').detection_range('air'), 9_000.0)

    def test_sensor_isolates_a_single_sensor(self):
        _FakeVehicleData._registry['v'] = _SensorRecord(
            radar=_sensor(air=(True, {'acquisition_range': 60})),
            TVD=_sensor(air=(True, {'acquisition_range': 12})))
        stub = _MobileStub(model='v')
        self.assertAlmostEqual(stub.detection_range('air', sensor='radar'), 60_000.0)
        self.assertAlmostEqual(stub.detection_range('air', sensor='TVD'), 12_000.0)

    def test_isolated_sensor_absent_returns_none(self):
        _FakeVehicleData._registry['v'] = _SensorRecord(
            radar=_sensor(air=(True, {'acquisition_range': 60})))
        self.assertIsNone(_MobileStub(model='v').detection_range('air', sensor='TVD'))

    def test_TVD_only_asset(self):
        _FakeVehicleData._registry['v'] = _SensorRecord(
            radar=False, TVD=_sensor(ground=(True, {'acquisition_range': 4})))
        self.assertAlmostEqual(_MobileStub(model='v').detection_range('ground'), 4_000.0)

    def test_ship_registry_dispatch(self):
        """Ship_Data non descrive il TVD: l'attributo manca e non deve rompere nulla."""
        record = object.__new__(Ship_Data)
        record.radar = _sensor(air=(True, {'acquisition_range': 450}),
                               sea=(True, {'acquisition_range': 80}))
        Ship_Data._registry['test-carrier-sensors'] = record

        stub = _MobileStub(model='test-carrier-sensors')
        self.assertFalse(hasattr(record, 'TVD'))
        self.assertAlmostEqual(stub.detection_range('air'), 450_000.0)
        self.assertAlmostEqual(stub.detection_range('sea'), 80_000.0)

    def test_aircraft_registry_dispatch(self):
        _FakeAircraftData._registry['a'] = _SensorRecord(
            radar=_sensor(air=(True, {'acquisition_range': 65})),
            TVD=_sensor(air=(True, {'acquisition_range': 130})))
        self.assertAlmostEqual(_MobileStub(model='a').detection_range('air'), 130_000.0)

    def test_vehicle_registry_wins_over_the_others_on_same_key(self):
        """Stesso dispatch di speed_profile_from_registry: primo registry che risponde."""
        _FakeVehicleData._registry['dup'] = _SensorRecord(
            radar=_sensor(air=(True, {'acquisition_range': 10})))
        _FakeAircraftData._registry['dup'] = _SensorRecord(
            radar=_sensor(air=(True, {'acquisition_range': 999})))
        self.assertAlmostEqual(_MobileStub(model='dup').detection_range('air'), 10_000.0)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--tests-only', action='store_true')
    args, remaining = parser.parse_known_args()
    sys.argv = [sys.argv[0]] + remaining
    unittest.main(verbosity=2)
