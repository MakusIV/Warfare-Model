"""Tests for Campaign_State.CampaignState."""
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

from Code.Dynamic_War_Manager.Source.Context.Campaign_State import CampaignState


# ---------------------------------------------------------------------------
# Stub helpers — lightweight stand-ins for live objects
# ---------------------------------------------------------------------------

class _StateStub:
    """Minimal State-like object with mutable health."""
    def __init__(self, health: int = 100, state_value: str = "Healtful", success_ratio=None):
        self._health = health
        self._state_value = state_value
        self._success_ratio = success_ratio

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, value):
        self._health = int(value)


class _PayloadStub:
    """Minimal Payload-like object with numeric fields."""
    def __init__(self, goods=0, energy=0, hr=0, hc=0, hs=0, hb=0):
        self.goods = goods
        self.energy = energy
        self.hr = hr
        self.hc = hc
        self.hs = hs
        self.hb = hb


class _WaypointStub:
    def __init__(self, name: str):
        self.name = name


class _EdgeStub:
    def __init__(self, wpA_name: str, wpB_name: str,
                 danger_level: float = 0.0, speed: float = 60.0,
                 path_type: str = "onroad", name: str | None = None):
        self._wpA = _WaypointStub(wpA_name)
        self._wpB = _WaypointStub(wpB_name)
        self._name = name or f"{wpA_name}-{wpB_name}"
        self._path_type = path_type
        self._danger_level = danger_level
        self._speed = speed

    @property
    def danger_level(self):
        return self._danger_level

    @danger_level.setter
    def danger_level(self, value):
        self._danger_level = float(value)

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        self._speed = float(value)


class _RouteStub:
    def __init__(self, name: str, route_type: str = "ground"):
        self._name = name
        self._route_type = route_type
        self._edges: dict = {}

    def add_edge(self, wpA_name: str, wpB_name: str, **kwargs):
        edge = _EdgeStub(wpA_name, wpB_name, **kwargs)
        self._edges[(wpA_name, wpB_name)] = edge
        return edge


class _ResourceManagerStub:
    def __init__(self):
        self._warehouse = _PayloadStub(goods=100, energy=50)
        self._actual_production = _PayloadStub(goods=10)
        self._clients: dict = {}
        self._server: dict = {}


class _AssetStub:
    def __init__(self, asset_id: str, name: str,
                 class_name: str = "Vehicle", model: str = "M1A2-Abrams"):
        self._id = asset_id
        self._class_name = class_name
        self._model = model
        self._name = name
        self._asset_type = "Tank"
        self._category = "Tank"
        self._role = None
        self._cost = 6_200_000
        self._value = 8
        self._crytical = False
        self._repair_time = 0
        self._functionality = None
        self._description = None
        self._position = None
        self._state = _StateStub(health=90)
        self._resources_assigned = _PayloadStub(goods=5, energy=10)
        self._resources_to_self_consume = _PayloadStub(goods=5, energy=10)
        self._payload = _PayloadStub()
        self._production = _PayloadStub()

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def model(self):
        return self._model

    @property
    def asset_type(self):
        return self._asset_type

    @property
    def category(self):
        return self._category

    @property
    def role(self):
        return self._role

    @property
    def cost(self):
        return self._cost

    @property
    def value(self):
        return self._value

    @property
    def crytical(self):
        return self._crytical

    @property
    def repair_time(self):
        return self._repair_time

    @property
    def functionality(self):
        return self._functionality

    @property
    def description(self):
        return self._description

    @property
    def __class__(self):
        # Return a proxy so __class__.__name__ == self._class_name
        return _ClassName(self._class_name)


class _ClassName:
    """Proxy so that asset.__class__.__name__ returns a custom string."""
    def __init__(self, name: str):
        self.__name__ = name


class _BlockStub:
    def __init__(self, block_id: str, name: str, side: str = "Red",
                 category: str = "Military"):
        self._id = block_id
        self._name = name
        self._side = side
        self._category = category
        self._sub_category = ""
        self._functionality = ""
        self._value = 5
        self._description = ""
        self._state = _StateStub(health=85)
        self._resource_manager = _ResourceManagerStub()
        self._assets: dict = {}
        # Make __class__.__name__ == "Military" for block_class field
        self._block_class = "Military"

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def side(self):
        return self._side

    @property
    def category(self):
        return self._category

    @property
    def sub_category(self):
        return self._sub_category

    @property
    def functionality(self):
        return self._functionality

    @property
    def value(self):
        return self._value

    @property
    def description(self):
        return self._description

    @property
    def __class__(self):
        return _ClassName(self._block_class)

    def add_asset(self, asset: _AssetStub):
        self._assets[asset.id] = asset


class _BlockItemStub:
    def __init__(self, block: _BlockStub, priority: float = 0.5):
        self.block = block
        self.priority = priority


class _RegionStub:
    def __init__(self, name: str, attack_weight: float = 0.5):
        self._name = name
        self._attack_weight = attack_weight
        self._weight_priority_target = {"Ground_Base": {"attack": {}, "defense": {}}}
        self._blocks_items: list = []
        self._routes: dict = {}

    @property
    def name(self):
        return self._name

    @property
    def blocks(self):
        return self._blocks_items

    @property
    def attack_weight(self):
        return self._attack_weight

    @attack_weight.setter
    def attack_weight(self, value):
        self._attack_weight = float(value)

    @property
    def weight_priority_target(self):
        return self._weight_priority_target

    @weight_priority_target.setter
    def weight_priority_target(self, value):
        self._weight_priority_target = value

    def add_block(self, block: _BlockStub, priority: float = 0.5):
        bi = _BlockItemStub(block, priority)
        self._blocks_items.append(bi)
        return bi

    def add_route(self, key: str, route: _RouteStub):
        self._routes[key] = route


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_region_with_block() -> tuple:
    """Return (region, block, asset) fully wired together."""
    block = _BlockStub("BLK_001", "Alpha Base")
    asset = _AssetStub("ASS_001", "Tank Alpha")
    block.add_asset(asset)
    region = _RegionStub("Donbas")
    region.add_block(block, priority=0.75)
    return region, block, asset


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCampaignStateInit(unittest.TestCase):

    def test_empty_state_on_init(self):
        cs = CampaignState()
        self.assertEqual(len(cs), 0)
        self.assertEqual(cs.missions, [])


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class TestCampaignStateValidation(unittest.TestCase):

    def setUp(self):
        self.cs = CampaignState()
        self.block = _BlockStub("B1", "Base")
        self.M = "M001"
        self.D = "2026-05-13"
        self.T = "08:00"
        self.R = "North"

    def test_invalid_mission_id_type_raises(self):
        with self.assertRaises(TypeError):
            self.cs.add_block_snapshot(123, self.D, self.T, self.R, self.block)

    def test_empty_mission_id_raises(self):
        with self.assertRaises(TypeError):
            self.cs.add_block_snapshot("", self.D, self.T, self.R, self.block)

    def test_invalid_date_format_raises(self):
        with self.assertRaises(ValueError):
            self.cs.add_block_snapshot(self.M, "13/05/2026", self.T, self.R, self.block)

    def test_invalid_time_format_raises(self):
        with self.assertRaises(ValueError):
            self.cs.add_block_snapshot(self.M, self.D, "8h00", self.R, self.block)

    def test_empty_region_name_raises(self):
        with self.assertRaises(TypeError):
            self.cs.add_block_snapshot(self.M, self.D, self.T, "", self.block)

    def test_block_without_id_raises(self):
        bad_block = types.SimpleNamespace()  # no .id attribute
        with self.assertRaises((ValueError, AttributeError)):
            self.cs.add_block_snapshot(self.M, self.D, self.T, self.R, bad_block)

    def test_conflicting_date_raises(self):
        self.cs.add_block_snapshot(self.M, self.D, self.T, self.R, self.block)
        with self.assertRaises(ValueError):
            self.cs.add_block_snapshot(self.M, "2026-05-14", self.T, self.R, self.block)

    def test_conflicting_time_raises(self):
        self.cs.add_block_snapshot(self.M, self.D, self.T, self.R, self.block)
        with self.assertRaises(ValueError):
            self.cs.add_block_snapshot(self.M, self.D, "09:00", self.R, self.block)

    def test_invalid_priority_type_raises(self):
        with self.assertRaises(TypeError):
            self.cs.add_block_snapshot(self.M, self.D, self.T, self.R, self.block, priority="high")

    def test_add_campaign_snapshot_invalid_regions_type_raises(self):
        region = _RegionStub("North")
        with self.assertRaises(TypeError):
            self.cs.add_campaign_snapshot(self.M, self.D, self.T, region)  # not a list

    def test_get_mission_invalid_id_type_raises(self):
        with self.assertRaises(TypeError):
            self.cs.get_mission(42)

    def test_get_field_trend_empty_field_raises(self):
        with self.assertRaises(TypeError):
            self.cs.get_field_trend("North", "B1", "")

    def test_get_field_trend_invalid_field_type_raises(self):
        with self.assertRaises(TypeError):
            self.cs.get_field_trend("North", "B1", 99)


# ---------------------------------------------------------------------------
# Write API
# ---------------------------------------------------------------------------

class TestCampaignStateWriteAPI(unittest.TestCase):

    def setUp(self):
        self.cs = CampaignState()
        self.region, self.block, self.asset = _make_region_with_block()
        self.M = "M001"
        self.D = "2026-05-13"
        self.T = "08:00"

    def test_add_block_snapshot_creates_mission(self):
        self.cs.add_block_snapshot(self.M, self.D, self.T, "North", self.block)
        self.assertIn(self.M, self.cs)

    def test_add_block_snapshot_stores_block(self):
        self.cs.add_block_snapshot(self.M, self.D, self.T, "North", self.block, priority=0.75)
        snap = self.cs.get_block_snapshot(self.M, "North", "BLK_001")
        self.assertIsNotNone(snap)
        self.assertEqual(snap["priority"], 0.75)

    def test_add_block_snapshot_creates_region_entry_if_missing(self):
        self.cs.add_block_snapshot(self.M, self.D, self.T, "South", self.block)
        region_snap = self.cs.get_region_snapshot(self.M, "South")
        self.assertIn("blocks", region_snap)

    def test_add_block_snapshot_same_mission_different_blocks(self):
        b2 = _BlockStub("BLK_002", "Beta Base")
        self.cs.add_block_snapshot(self.M, self.D, self.T, "North", self.block)
        self.cs.add_block_snapshot(self.M, self.D, self.T, "North", b2)
        self.assertIsNotNone(self.cs.get_block_snapshot(self.M, "North", "BLK_001"))
        self.assertIsNotNone(self.cs.get_block_snapshot(self.M, "North", "BLK_002"))

    def test_add_block_snapshot_overwrites_same_block(self):
        self.cs.add_block_snapshot(self.M, self.D, self.T, "North", self.block, priority=0.5)
        self.cs.add_block_snapshot(self.M, self.D, self.T, "North", self.block, priority=0.9)
        snap = self.cs.get_block_snapshot(self.M, "North", "BLK_001")
        self.assertAlmostEqual(snap["priority"], 0.9)

    def test_add_region_snapshot_stores_all_blocks(self):
        b2 = _BlockStub("BLK_002", "Beta")
        self.region.add_block(b2, priority=0.3)
        self.cs.add_region_snapshot(self.M, self.D, self.T, self.region)
        self.assertIsNotNone(self.cs.get_block_snapshot(self.M, "Donbas", "BLK_001"))
        self.assertIsNotNone(self.cs.get_block_snapshot(self.M, "Donbas", "BLK_002"))

    def test_add_region_snapshot_stores_attack_weight(self):
        self.cs.add_region_snapshot(self.M, self.D, self.T, self.region)
        region_snap = self.cs.get_region_snapshot(self.M, "Donbas")
        self.assertEqual(region_snap["attack_weight"], 0.5)

    def test_add_campaign_snapshot_stores_all_regions(self):
        r2 = _RegionStub("Crimea")
        r2.add_block(_BlockStub("BLK_099", "Crimea Base"))
        self.cs.add_campaign_snapshot(self.M, self.D, self.T, [self.region, r2])
        self.assertIsNotNone(self.cs.get_region_snapshot(self.M, "Donbas"))
        self.assertIsNotNone(self.cs.get_region_snapshot(self.M, "Crimea"))

    def test_add_region_snapshot_same_mission_twice_different_date_raises(self):
        self.cs.add_region_snapshot(self.M, self.D, self.T, self.region)
        with self.assertRaises(ValueError):
            self.cs.add_region_snapshot(self.M, "2026-06-01", self.T, self.region)


# ---------------------------------------------------------------------------
# Read API
# ---------------------------------------------------------------------------

class TestCampaignStateReadAPI(unittest.TestCase):

    def setUp(self):
        self.cs = CampaignState()
        self.region, self.block, self.asset = _make_region_with_block()
        self.M1 = "M001"
        self.M2 = "M002"
        self.D1 = "2026-05-13"
        self.D2 = "2026-05-14"
        self.T = "08:00"

    def _add_m1(self):
        self.cs.add_region_snapshot(self.M1, self.D1, self.T, self.region)

    def _add_m2(self):
        self.cs.add_region_snapshot(self.M2, self.D2, self.T, self.region)

    def test_missions_empty_initially(self):
        self.assertEqual(self.cs.missions, [])

    def test_missions_insertion_order(self):
        self._add_m1()
        self._add_m2()
        self.assertEqual(self.cs.missions, [self.M1, self.M2])

    def test_len_empty(self):
        self.assertEqual(len(self.cs), 0)

    def test_len_after_insert(self):
        self._add_m1()
        self.assertEqual(len(self.cs), 1)

    def test_len_after_two_missions(self):
        self._add_m1()
        self._add_m2()
        self.assertEqual(len(self.cs), 2)

    def test_contains_true(self):
        self._add_m1()
        self.assertIn(self.M1, self.cs)

    def test_contains_false(self):
        self.assertNotIn("GHOST", self.cs)

    def test_get_mission_returns_metadata(self):
        self._add_m1()
        m = self.cs.get_mission(self.M1)
        self.assertEqual(m["date"], self.D1)
        self.assertEqual(m["time"], self.T)
        self.assertIn("regions", m)

    def test_get_mission_missing_raises(self):
        with self.assertRaises(KeyError):
            self.cs.get_mission("NONEXISTENT")

    def test_get_region_snapshot_found(self):
        self._add_m1()
        snap = self.cs.get_region_snapshot(self.M1, "Donbas")
        self.assertIn("blocks", snap)

    def test_get_region_snapshot_missing_returns_empty_dict(self):
        self._add_m1()
        snap = self.cs.get_region_snapshot(self.M1, "GHOST_REGION")
        self.assertEqual(snap, {})

    def test_get_block_snapshot_found(self):
        self._add_m1()
        snap = self.cs.get_block_snapshot(self.M1, "Donbas", "BLK_001")
        self.assertIsNotNone(snap)
        self.assertEqual(snap["name"], "Alpha Base")

    def test_get_block_snapshot_missing_block_returns_none(self):
        self._add_m1()
        snap = self.cs.get_block_snapshot(self.M1, "Donbas", "GHOST_BLOCK")
        self.assertIsNone(snap)

    def test_get_block_snapshot_missing_region_returns_none(self):
        self._add_m1()
        snap = self.cs.get_block_snapshot(self.M1, "GHOST", "BLK_001")
        self.assertIsNone(snap)

    def test_get_block_history_sorted_chronologically(self):
        self._add_m2()   # insert later mission first
        self._add_m1()
        history = self.cs.get_block_history("Donbas", "BLK_001")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0][0], self.M1)  # earlier date first
        self.assertEqual(history[1][0], self.M2)

    def test_get_block_history_empty_when_block_absent(self):
        self._add_m1()
        history = self.cs.get_block_history("Donbas", "NO_SUCH_BLOCK")
        self.assertEqual(history, [])

    def test_get_field_trend_extracts_priority(self):
        self._add_m1()
        self._add_m2()
        trend = self.cs.get_field_trend("Donbas", "BLK_001", "priority")
        values = [v for _, _, _, v in trend]
        self.assertEqual(len(values), 2)
        self.assertAlmostEqual(values[0], 0.75)

    def test_get_field_trend_missing_field_returns_none(self):
        self._add_m1()
        trend = self.cs.get_field_trend("Donbas", "BLK_001", "nonexistent")
        self.assertIsNone(trend[0][3])

    def test_get_asset_history_found(self):
        self._add_m1()
        self._add_m2()
        history = self.cs.get_asset_history("Donbas", "BLK_001", "ASS_001")
        self.assertEqual(len(history), 2)
        _, _, _, asset_snap = history[0]
        self.assertIsNotNone(asset_snap)
        self.assertEqual(asset_snap["name"], "Tank Alpha")

    def test_get_asset_history_missing_asset_returns_none_entries(self):
        self._add_m1()
        history = self.cs.get_asset_history("Donbas", "BLK_001", "NO_SUCH_ASSET")
        _, _, _, snap = history[0]
        self.assertIsNone(snap)

    def test_repr_contains_mission_count(self):
        self._add_m1()
        r = repr(self.cs)
        self.assertIn("1", r)
        self.assertIn(self.M1, r)


# ---------------------------------------------------------------------------
# Serialisation content
# ---------------------------------------------------------------------------

class TestCampaignStateSerialisationContent(unittest.TestCase):

    def setUp(self):
        self.cs = CampaignState()
        self.region, self.block, self.asset = _make_region_with_block()
        self.M = "M001"
        self.cs.add_region_snapshot(self.M, "2026-05-13", "08:00", self.region)
        self.block_snap = self.cs.get_block_snapshot(self.M, "Donbas", "BLK_001")
        self.asset_snap = self.block_snap["assets"].get("ASS_001") if self.block_snap else None

    def test_block_snapshot_has_required_fields(self):
        required = {
            "block_class", "name", "side", "category", "sub_category",
            "functionality", "value", "description", "priority",
            "state", "resource_manager", "assets",
        }
        self.assertTrue(required.issubset(set(self.block_snap.keys())))

    def test_block_class_name_stored(self):
        self.assertEqual(self.block_snap["block_class"], "Military")

    def test_block_priority_stored(self):
        self.assertAlmostEqual(self.block_snap["priority"], 0.75)

    def test_state_serialised_correctly(self):
        state_snap = self.block_snap["state"]
        self.assertIsNotNone(state_snap)
        self.assertEqual(state_snap["health"], 85)
        self.assertIn("state_value", state_snap)
        self.assertIn("success_ratio", state_snap)

    def test_resource_manager_has_warehouse(self):
        rm_snap = self.block_snap["resource_manager"]
        self.assertIsNotNone(rm_snap)
        self.assertIn("warehouse", rm_snap)
        self.assertEqual(rm_snap["warehouse"]["goods"], 100)
        self.assertEqual(rm_snap["warehouse"]["energy"], 50)

    def test_resource_manager_has_clients_and_server_ids(self):
        rm_snap = self.block_snap["resource_manager"]
        self.assertIn("clients_ids", rm_snap)
        self.assertIn("server_ids", rm_snap)
        self.assertIsInstance(rm_snap["clients_ids"], list)

    def test_asset_snapshot_has_required_fields(self):
        self.assertIsNotNone(self.asset_snap)
        required = {
            "class_name", "model", "name", "asset_type", "category",
            "state", "resources_assigned", "resources_to_self_consume",
            "payload", "production",
        }
        self.assertTrue(required.issubset(set(self.asset_snap.keys())))

    def test_asset_model_stored(self):
        self.assertEqual(self.asset_snap["model"], "M1A2-Abrams")

    def test_asset_state_health_stored(self):
        self.assertEqual(self.asset_snap["state"]["health"], 90)

    def test_asset_resources_assigned_payload_stored(self):
        ra = self.asset_snap["resources_assigned"]
        self.assertIsNotNone(ra)
        self.assertEqual(ra["goods"], 5)
        self.assertEqual(ra["energy"], 10)

    def test_region_snapshot_has_routes(self):
        region_snap = self.cs.get_region_snapshot(self.M, "Donbas")
        self.assertIn("routes", region_snap)

    def test_region_snapshot_routes_include_edges(self):
        route = _RouteStub("Route_A")
        edge = route.add_edge("WpA", "WpB", danger_level=0.4, speed=55.0)
        self.region.add_route("BLK_001,BLK_002", route)
        cs2 = CampaignState()
        cs2.add_region_snapshot("M002", "2026-05-13", "08:00", self.region)
        region_snap = cs2.get_region_snapshot("M002", "Donbas")
        route_snap = region_snap["routes"].get("BLK_001,BLK_002")
        self.assertIsNotNone(route_snap)
        self.assertIn("edges", route_snap)
        edge_snap = route_snap["edges"].get("WpA-WpB")
        self.assertIsNotNone(edge_snap)
        self.assertAlmostEqual(edge_snap["danger_level"], 0.4)
        self.assertAlmostEqual(edge_snap["speed"], 55.0)

    def test_asset_position_none_when_not_set(self):
        self.assertIsNone(self.asset_snap["position"])

    def test_asset_position_serialised_when_set(self):
        pos_mock = types.SimpleNamespace(x=10.0, y=20.0, z=100.0)
        self.asset._position = pos_mock
        cs2 = CampaignState()
        cs2.add_region_snapshot("M003", "2026-05-13", "08:00", self.region)
        snap2 = cs2.get_block_snapshot("M003", "Donbas", "BLK_001")
        pos = snap2["assets"]["ASS_001"]["position"]
        self.assertIsNotNone(pos)
        self.assertAlmostEqual(pos["x"], 10.0)
        self.assertAlmostEqual(pos["y"], 20.0)
        self.assertAlmostEqual(pos["z"], 100.0)


# ---------------------------------------------------------------------------
# Restore API
# ---------------------------------------------------------------------------

class TestCampaignStateRestoreAPI(unittest.TestCase):

    def setUp(self):
        self.region, self.block, self.asset = _make_region_with_block()
        route = _RouteStub("Route_Alpha")
        self.edge = route.add_edge("WpA", "WpB", danger_level=0.2, speed=80.0)
        self.region.add_route("BLK_001,BLK_099", route)

        self.cs = CampaignState()
        self.M = "M001"
        self.cs.add_region_snapshot(self.M, "2026-05-13", "08:00", self.region)

    def _mutate_then_restore(self):
        """Simulate damage after snapshot, then restore and return region list."""
        self.block._state._health = 30          # simulate damage
        self.asset._state._health = 20
        self.block._resource_manager._warehouse.goods = 0
        self.asset._resources_assigned.goods = 0
        self.edge._danger_level = 0.9
        self.cs.restore(self.M, [self.region])

    def test_restore_block_state_health(self):
        self._mutate_then_restore()
        self.assertEqual(self.block._state._health, 85)

    def test_restore_asset_state_health(self):
        self._mutate_then_restore()
        self.assertEqual(self.asset._state._health, 90)

    def test_restore_block_warehouse_goods(self):
        self._mutate_then_restore()
        self.assertEqual(self.block._resource_manager._warehouse.goods, 100)

    def test_restore_asset_resources_assigned_goods(self):
        self._mutate_then_restore()
        self.assertEqual(self.asset._resources_assigned.goods, 5)

    def test_restore_route_edge_danger_level(self):
        self._mutate_then_restore()
        self.assertAlmostEqual(self.edge._danger_level, 0.2)

    def test_restore_route_edge_speed(self):
        self._mutate_then_restore()
        self.assertAlmostEqual(self.edge._speed, 80.0)

    def test_restore_block_priority(self):
        block_item = self.region.blocks[0]
        block_item.priority = 0.0   # simulate change
        self.cs.restore(self.M, [self.region])
        self.assertAlmostEqual(block_item.priority, 0.75)

    def test_restore_region_attack_weight(self):
        self.region._attack_weight = 0.9
        self.cs.restore(self.M, [self.region])
        self.assertAlmostEqual(self.region._attack_weight, 0.5)

    def test_restore_missing_region_skips_gracefully(self):
        other_region = _RegionStub("NonExistent")
        try:
            self.cs.restore(self.M, [other_region])
        except Exception as exc:
            self.fail(f"restore raised unexpectedly: {exc}")

    def test_restore_missing_block_skips_gracefully(self):
        ghost_block = _BlockStub("GHOST_BLK", "Ghost")
        ghost_bi = _BlockItemStub(ghost_block, 0.0)
        self.region._blocks_items.append(ghost_bi)
        try:
            self.cs.restore(self.M, [self.region])
        except Exception as exc:
            self.fail(f"restore raised unexpectedly: {exc}")

    def test_restore_missing_asset_skips_gracefully(self):
        ghost_asset = _AssetStub("GHOST_ASS", "Ghost Asset")
        self.block._assets["GHOST_ASS"] = ghost_asset
        try:
            self.cs.restore(self.M, [self.region])
        except Exception as exc:
            self.fail(f"restore raised unexpectedly: {exc}")

    def test_restore_invalid_regions_type_raises(self):
        with self.assertRaises(TypeError):
            self.cs.restore(self.M, self.region)   # not a list

    def test_restore_missing_mission_raises(self):
        with self.assertRaises(KeyError):
            self.cs.restore("NONEXISTENT", [self.region])

    def test_restore_state_success_ratio(self):
        self.block._state._success_ratio = {"task_a": {"success_count": 3, "total_count": 5}}
        cs2 = CampaignState()
        cs2.add_region_snapshot("M_SR", "2026-05-13", "09:00", self.region)
        self.block._state._success_ratio = None
        cs2.restore("M_SR", [self.region])
        self.assertEqual(
            self.block._state._success_ratio,
            {"task_a": {"success_count": 3, "total_count": 5}},
        )


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

class TestCampaignStatePersistence(unittest.TestCase):

    def setUp(self):
        self.region, self.block, self.asset = _make_region_with_block()
        self.cs = CampaignState()
        self.M = "M001"
        self.cs.add_region_snapshot(self.M, "2026-05-13", "08:00", self.region)

    def test_save_creates_valid_json(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            self.cs.save(path)
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            self.assertIn(self.M, data)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_load_restores_full_state(self):
        region2, block2, _ = _make_region_with_block()
        self.cs.add_region_snapshot("M002", "2026-05-14", "08:00", region2)
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            self.cs.save(path)
            loaded = CampaignState.load(path)
            self.assertEqual(len(loaded), 2)
            self.assertIsNotNone(loaded.get_block_snapshot("M001", "Donbas", "BLK_001"))
            self.assertIsNotNone(loaded.get_block_snapshot("M002", "Donbas", "BLK_001"))
        finally:
            Path(path).unlink(missing_ok=True)

    def test_save_roundtrip_preserves_block_health(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            self.cs.save(path)
            loaded = CampaignState.load(path)
            snap = loaded.get_block_snapshot(self.M, "Donbas", "BLK_001")
            self.assertEqual(snap["state"]["health"], 85)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_save_roundtrip_preserves_asset_model(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            self.cs.save(path)
            loaded = CampaignState.load(path)
            snap = loaded.get_block_snapshot(self.M, "Donbas", "BLK_001")
            self.assertEqual(snap["assets"]["ASS_001"]["model"], "M1A2-Abrams")
        finally:
            Path(path).unlink(missing_ok=True)

    def test_save_invalid_path_raises(self):
        with self.assertRaises(TypeError):
            self.cs.save(None)

    def test_load_invalid_path_raises(self):
        with self.assertRaises(TypeError):
            CampaignState.load(42)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
