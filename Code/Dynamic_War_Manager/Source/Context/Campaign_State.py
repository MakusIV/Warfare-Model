from __future__ import annotations

import json
import pathlib
from datetime import date as _date, time as _time
from typing import Any, Dict, List, Optional, Tuple

from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger

logger = Logger(module_name=__name__, class_name='CampaignState').logger

_PAYLOAD_FIELDS = ('goods', 'energy', 'hr', 'hc', 'hs', 'hb')


class CampaignState:
    """
    Stores full campaign-state snapshots for every region, indexed by mission.

    Each snapshot captures the mutable operational state of all regions,
    blocks (including their State and Resource_Manager components), assets
    (Vehicle / Ship / Aircraft / Structure) and routes.  Use it to analyse
    campaign evolution across missions and to restore a given state on live
    objects.

    Internal structure::

        _state: {
            mission_id: {
                "date":    str,    # ISO 8601 "YYYY-MM-DD"
                "time":    str,    # "HH:MM" or "HH:MM:SS"
                "regions": {
                    region_name: {
                        "attack_weight": float,
                        "weight_priority_target": dict,
                        "routes": {
                            route_key: {
                                "name": str | None,
                                "route_type": str,
                                "edges": {
                                    "<wpA_name>-<wpB_name>": {
                                        "name": str | None,
                                        "path_type": str | None,
                                        "danger_level": float | None,
                                        "speed": float | None,
                                        "wpA_name": str | None,
                                        "wpB_name": str | None
                                    }
                                }
                            }
                        },
                        "blocks": {
                            block_id: {
                                "block_class": str,
                                "name": str,
                                "side": str,
                                "category": str,
                                "sub_category": str,
                                "functionality": str,
                                "value": int,
                                "description": str,
                                "priority": float,
                                "state": {
                                    "health": int,
                                    "state_value": str,
                                    "success_ratio": dict | None
                                },
                                "resource_manager": {
                                    "warehouse": payload_dict,
                                    "actual_production": payload_dict,
                                    "clients_ids": [block_id, ...],
                                    "server_ids":  [block_id, ...]
                                },
                                "assets": {
                                    asset_id: {
                                        "class_name": str,
                                        "model": str | None,
                                        "name": str | None,
                                        "asset_type": str | None,
                                        "category": str | None,
                                        "role": str | None,
                                        "cost": int | None,
                                        "value": int | None,
                                        "crytical": bool,
                                        "repair_time": int,
                                        "functionality": str | None,
                                        "description": str | None,
                                        "position": {"x": float, "y": float, "z": float} | None,
                                        "state": state_dict,
                                        "resources_assigned": payload_dict,
                                        "resources_to_self_consume": payload_dict,
                                        "payload": payload_dict,
                                        "production": payload_dict
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

    Write API
    ---------
    add_campaign_snapshot(mission_id, date, time, regions)  — atomic, full campaign
    add_region_snapshot(mission_id, date, time, region)     — one region at a time
    add_block_snapshot(mission_id, date, time, region_name, block, priority)  — one block

    Read API
    --------
    missions                                            → List[str]
    get_mission(mission_id)                             → Dict
    get_region_snapshot(mission_id, region_name)        → Dict
    get_block_snapshot(mission_id, region_name, block_id) → Optional[Dict]
    get_block_history(region_name, block_id)            → List[(mid, date, time, snap)]
    get_field_trend(region_name, block_id, field)       → List[(mid, date, time, value)]
    get_asset_history(region_name, block_id, asset_id)  → List[(mid, date, time, snap)]

    Restore API
    -----------
    restore(mission_id, regions)   — applies snapshot to live Region / Block / Asset objects

    Persistence
    -----------
    cs.save("campaign.json")
    cs2 = CampaignState.load("campaign.json")
    """

    def __init__(self) -> None:
        self._state: Dict[str, Dict] = {}

    # ------------------------------------------------------------------ #
    # Write API                                                            #
    # ------------------------------------------------------------------ #

    def add_campaign_snapshot(
        self,
        mission_id: str,
        date: str,
        time: str,
        regions: List,
    ) -> None:
        """Register a full campaign snapshot from a list of Region objects.

        Iterates over every region and delegates to add_region_snapshot.
        """
        self._validate_mission_id(mission_id)
        self._validate_date(date)
        self._validate_time(time)
        if not isinstance(regions, list):
            raise TypeError("regions must be a list of Region objects.")
        for region in regions:
            self.add_region_snapshot(mission_id, date, time, region)

    def add_region_snapshot(
        self,
        mission_id: str,
        date: str,
        time: str,
        region,
    ) -> None:
        """Register a snapshot of one Region (all blocks and routes included)."""
        self._validate_mission_id(mission_id)
        self._validate_date(date)
        self._validate_time(time)
        region_name = getattr(region, 'name', None)
        if not isinstance(region_name, str) or not region_name:
            raise ValueError("region.name must be a non-empty string.")

        self._ensure_mission(mission_id, date, time)
        self._state[mission_id]["regions"][region_name] = self._serialize_region(region)
        logger.debug("Region snapshot added: mission=%s region=%s", mission_id, region_name)

    def add_block_snapshot(
        self,
        mission_id: str,
        date: str,
        time: str,
        region_name: str,
        block,
        priority: float = 0.0,
    ) -> None:
        """Register a snapshot for one Block within a region.

        If the region entry does not yet exist in this mission it is created
        with null metadata (attack_weight / weight_priority_target / routes).
        """
        self._validate_mission_id(mission_id)
        self._validate_date(date)
        self._validate_time(time)
        self._validate_str(region_name, "region_name")
        block_id = getattr(block, 'id', None)
        if not isinstance(block_id, str) or not block_id:
            raise ValueError("block.id must be a non-empty string.")
        if not isinstance(priority, (int, float)):
            raise TypeError("priority must be a number.")

        self._ensure_mission(mission_id, date, time)
        regions = self._state[mission_id]["regions"]
        if region_name not in regions:
            regions[region_name] = {
                "attack_weight": None,
                "weight_priority_target": None,
                "routes": {},
                "blocks": {},
            }
        regions[region_name]["blocks"][block_id] = self._serialize_block(block, float(priority))
        logger.debug(
            "Block snapshot added: mission=%s region=%s block=%s",
            mission_id, region_name, block_id,
        )

    # ------------------------------------------------------------------ #
    # Read API                                                             #
    # ------------------------------------------------------------------ #

    @property
    def missions(self) -> List[str]:
        """Mission IDs in insertion order."""
        return list(self._state.keys())

    def get_mission(self, mission_id: str) -> Dict:
        """Return the full snapshot dict for a mission.

        Raises KeyError if mission_id is not registered.
        """
        self._validate_mission_id(mission_id)
        if mission_id not in self._state:
            raise KeyError(f"Mission '{mission_id}' not found in state.")
        return self._state[mission_id]

    def get_region_snapshot(self, mission_id: str, region_name: str) -> Dict:
        """Return the snapshot dict for a region in a mission.

        Returns an empty dict if the region was not recorded.
        """
        self._validate_str(region_name, "region_name")
        return self.get_mission(mission_id)["regions"].get(region_name, {})

    def get_block_snapshot(
        self, mission_id: str, region_name: str, block_id: str
    ) -> Optional[Dict]:
        """Return the state snapshot of a block in a given mission, or None."""
        self._validate_str(block_id, "block_id")
        return self.get_region_snapshot(mission_id, region_name).get("blocks", {}).get(block_id)

    def get_block_history(
        self, region_name: str, block_id: str
    ) -> List[Tuple[str, str, str, Dict]]:
        """All snapshots of a block across missions, sorted by date then time.

        Returns:
            List of (mission_id, date, time, block_snapshot_dict).
        """
        self._validate_str(region_name, "region_name")
        self._validate_str(block_id, "block_id")
        result = [
            (
                mid,
                data["date"],
                data["time"],
                data["regions"].get(region_name, {}).get("blocks", {}).get(block_id),
            )
            for mid, data in self._state.items()
            if data["regions"].get(region_name, {}).get("blocks", {}).get(block_id) is not None
        ]
        result.sort(key=lambda x: (x[1], x[2]))
        return result

    def get_field_trend(
        self, region_name: str, block_id: str, field: str
    ) -> List[Tuple[str, str, str, Any]]:
        """Value of one block-level field across all missions, sorted chronologically.

        Returns:
            List of (mission_id, date, time, field_value).
        """
        if not isinstance(field, str) or not field:
            raise TypeError("field must be a non-empty string.")
        return [
            (mid, d, t, snapshot.get(field))
            for mid, d, t, snapshot in self.get_block_history(region_name, block_id)
        ]

    def get_asset_history(
        self, region_name: str, block_id: str, asset_id: str
    ) -> List[Tuple[str, str, str, Optional[Dict]]]:
        """All snapshots of one asset across missions, sorted chronologically.

        Returns:
            List of (mission_id, date, time, asset_snapshot_dict | None).
        """
        self._validate_str(asset_id, "asset_id")
        return [
            (mid, d, t, (block_snap or {}).get("assets", {}).get(asset_id))
            for mid, d, t, block_snap in self.get_block_history(region_name, block_id)
        ]

    def __len__(self) -> int:
        return len(self._state)

    def __contains__(self, mission_id: str) -> bool:
        return mission_id in self._state

    def __repr__(self) -> str:
        return f"CampaignState(missions={len(self)}, ids={self.missions})"

    # ------------------------------------------------------------------ #
    # Restore API                                                          #
    # ------------------------------------------------------------------ #

    def restore(self, mission_id: str, regions: List) -> None:
        """Apply the saved state for mission_id to a list of live Region objects.

        For each region / block / asset / route found in both the snapshot and
        the live graph the following mutable fields are overwritten:

        * Region: attack_weight, weight_priority_target
        * BlockItem: priority
        * Block.state: health, success_ratio
        * Block.resource_manager: warehouse payload, actual_production payload
        * Asset.state: health, success_ratio
        * Asset payloads: resources_assigned, resources_to_self_consume, payload, production
        * Route.Edge: danger_level, speed

        Objects present in the live graph but absent from the snapshot are left
        untouched.  Objects in the snapshot that cannot be found in the live
        graph are logged as warnings and skipped.
        """
        if not isinstance(regions, list):
            raise TypeError("regions must be a list of Region objects.")
        mission_data = self.get_mission(mission_id)

        for region in regions:
            region_name = getattr(region, 'name', None)
            if not isinstance(region_name, str):
                logger.warning("Skipping region without a string name: %r", region)
                continue
            region_snap = mission_data["regions"].get(region_name)
            if region_snap is None:
                logger.warning(
                    "Region '%s' not in snapshot for mission '%s'. Skipped.",
                    region_name, mission_id,
                )
                continue
            self._restore_region(region, region_snap)

    # ------------------------------------------------------------------ #
    # Persistence                                                          #
    # ------------------------------------------------------------------ #

    def save(self, path: str) -> None:
        """Serialize the full state to a JSON file (UTF-8)."""
        if not isinstance(path, str) or not path:
            raise TypeError("path must be a non-empty string.")
        pathlib.Path(path).write_text(
            json.dumps(self._state, default=str, indent=2), encoding="utf-8"
        )
        logger.info("CampaignState saved to %s (%d missions).", path, len(self))

    @classmethod
    def load(cls, path: str) -> "CampaignState":
        """Load a CampaignState from a JSON file produced by save().

        Returns a new CampaignState instance.
        """
        if not isinstance(path, str) or not path:
            raise TypeError("path must be a non-empty string.")
        instance = cls()
        instance._state = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
        logger.info("CampaignState loaded from %s (%d missions).", path, len(instance))
        return instance

    # ------------------------------------------------------------------ #
    # Serialisation helpers (static)                                       #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _serialize_region(region) -> Dict:
        blocks_dict: Dict[str, Dict] = {}
        for block_item in getattr(region, 'blocks', []):
            block = getattr(block_item, 'block', None)
            priority = getattr(block_item, 'priority', 0.0)
            if block is None:
                continue
            block_id = getattr(block, 'id', None)
            if block_id:
                blocks_dict[block_id] = CampaignState._serialize_block(block, float(priority))

        routes_dict: Dict[str, Dict] = {}
        for route_key, route in getattr(region, '_routes', {}).items():
            routes_dict[route_key] = CampaignState._serialize_route(route)

        return {
            "attack_weight": getattr(region, '_attack_weight', None),
            "weight_priority_target": getattr(region, '_weight_priority_target', None),
            "routes": routes_dict,
            "blocks": blocks_dict,
        }

    @staticmethod
    def _serialize_block(block, priority: float) -> Dict:
        assets_dict: Dict[str, Dict] = {}
        for asset_id, asset in getattr(block, '_assets', {}).items():
            assets_dict[asset_id] = CampaignState._serialize_asset(asset)

        return {
            "block_class": block.__class__.__name__,
            "name": getattr(block, 'name', None),
            "side": getattr(block, 'side', None),
            "category": getattr(block, 'category', None),
            "sub_category": getattr(block, 'sub_category', None),
            "functionality": getattr(block, 'functionality', None),
            "value": getattr(block, 'value', None),
            "description": getattr(block, 'description', None),
            "priority": priority,
            "state": CampaignState._serialize_state(getattr(block, '_state', None)),
            "resource_manager": CampaignState._serialize_resource_manager(
                getattr(block, '_resource_manager', None)
            ),
            "assets": assets_dict,
        }

    @staticmethod
    def _serialize_state(state) -> Optional[Dict]:
        if state is None:
            return None
        return {
            "health": getattr(state, '_health', None),
            "state_value": getattr(state, '_state_value', None),
            "success_ratio": getattr(state, '_success_ratio', None),
        }

    @staticmethod
    def _serialize_resource_manager(rm) -> Optional[Dict]:
        if rm is None:
            return None
        return {
            "warehouse": CampaignState._serialize_payload(getattr(rm, '_warehouse', None)),
            "actual_production": CampaignState._serialize_payload(
                getattr(rm, '_actual_production', None)
            ),
            "clients_ids": list(getattr(rm, '_clients', {}).keys()),
            "server_ids": list(getattr(rm, '_server', {}).keys()),
        }

    @staticmethod
    def _serialize_payload(payload) -> Optional[Dict]:
        if payload is None:
            return None
        return {field: getattr(payload, field, 0) for field in _PAYLOAD_FIELDS}

    @staticmethod
    def _serialize_asset(asset) -> Dict:
        position = getattr(asset, '_position', None)
        pos_dict: Optional[Dict] = None
        if position is not None:
            try:
                pos_dict = {
                    "x": float(position.x),
                    "y": float(position.y),
                    "z": float(position.z) if hasattr(position, 'z') else 0.0,
                }
            except Exception:
                pos_dict = None

        return {
            "class_name": asset.__class__.__name__,
            "model": getattr(asset, 'model', None),
            "name": getattr(asset, 'name', None),
            "asset_type": getattr(asset, 'asset_type', None),
            "category": getattr(asset, 'category', None),
            "role": getattr(asset, 'role', None),
            "cost": getattr(asset, 'cost', None),
            "value": getattr(asset, 'value', None),
            "crytical": getattr(asset, 'crytical', False),
            "repair_time": getattr(asset, 'repair_time', 0),
            "functionality": getattr(asset, 'functionality', None),
            "description": getattr(asset, 'description', None),
            "position": pos_dict,
            "state": CampaignState._serialize_state(getattr(asset, '_state', None)),
            "resources_assigned": CampaignState._serialize_payload(
                getattr(asset, '_resources_assigned', None)
            ),
            "resources_to_self_consume": CampaignState._serialize_payload(
                getattr(asset, '_resources_to_self_consume', None)
            ),
            "payload": CampaignState._serialize_payload(getattr(asset, '_payload', None)),
            "production": CampaignState._serialize_payload(getattr(asset, '_production', None)),
        }

    @staticmethod
    def _serialize_route(route) -> Dict:
        edges_dict: Dict[str, Dict] = {}
        for _edge_key, edge in getattr(route, '_edges', {}).items():
            wpA = getattr(edge, '_wpA', None)
            wpB = getattr(edge, '_wpB', None)
            wpA_name = getattr(wpA, 'name', None) if wpA is not None else None
            wpB_name = getattr(wpB, 'name', None) if wpB is not None else None
            key = f"{wpA_name}-{wpB_name}"
            edges_dict[key] = {
                "name": getattr(edge, '_name', None),
                "path_type": getattr(edge, '_path_type', None),
                "danger_level": getattr(edge, '_danger_level', None),
                "speed": getattr(edge, '_speed', None),
                "wpA_name": wpA_name,
                "wpB_name": wpB_name,
            }
        return {
            "name": getattr(route, '_name', None),
            "route_type": getattr(route, '_route_type', None),
            "edges": edges_dict,
        }

    # ------------------------------------------------------------------ #
    # Restore helpers                                                      #
    # ------------------------------------------------------------------ #

    def _restore_region(self, region, region_snap: Dict) -> None:
        if region_snap.get("attack_weight") is not None:
            try:
                region.attack_weight = float(region_snap["attack_weight"])
            except Exception as exc:
                logger.warning(
                    "Could not restore attack_weight for region '%s': %s", region.name, exc
                )

        if region_snap.get("weight_priority_target") is not None:
            try:
                region.weight_priority_target = region_snap["weight_priority_target"]
            except Exception as exc:
                logger.warning(
                    "Could not restore weight_priority_target for region '%s': %s",
                    region.name, exc,
                )

        for route_key, route_snap in region_snap.get("routes", {}).items():
            live_route = getattr(region, '_routes', {}).get(route_key)
            if live_route is None:
                logger.warning(
                    "Route '%s' not found in live region '%s'. Skipped.", route_key, region.name
                )
                continue
            self._restore_route(live_route, route_snap, region.name)

        blocks_by_id = {
            bi.block.id: bi
            for bi in getattr(region, 'blocks', [])
            if hasattr(bi, 'block') and bi.block is not None
        }

        for block_id, block_snap in region_snap.get("blocks", {}).items():
            block_item = blocks_by_id.get(block_id)
            if block_item is None:
                logger.warning(
                    "Block '%s' not found in live region '%s'. Skipped.", block_id, region.name
                )
                continue
            if block_snap.get("priority") is not None:
                try:
                    block_item.priority = float(block_snap["priority"])
                except Exception as exc:
                    logger.warning(
                        "Could not restore priority for block '%s': %s", block_id, exc
                    )
            self._restore_block(block_item.block, block_snap)

    @staticmethod
    def _restore_block(block, block_snap: Dict) -> None:
        state_snap = block_snap.get("state")
        if state_snap and getattr(block, '_state', None) is not None:
            CampaignState._restore_state(block._state, state_snap, f"block {block.id}")

        rm_snap = block_snap.get("resource_manager")
        if rm_snap and getattr(block, '_resource_manager', None) is not None:
            CampaignState._restore_resource_manager(
                block._resource_manager, rm_snap, f"block {block.id}"
            )

        for asset_id, asset_snap in block_snap.get("assets", {}).items():
            asset = getattr(block, '_assets', {}).get(asset_id)
            if asset is None:
                logger.warning(
                    "Asset '%s' not found in live block '%s'. Skipped.", asset_id, block.id
                )
                continue
            CampaignState._restore_asset(asset, asset_snap)

    @staticmethod
    def _restore_state(state, state_snap: Dict, context: str) -> None:
        health = state_snap.get("health")
        if health is not None:
            try:
                state.health = int(health)
            except Exception as exc:
                logger.warning("Could not restore health for %s: %s", context, exc)

        success_ratio = state_snap.get("success_ratio")
        if success_ratio is not None:
            state._success_ratio = success_ratio

    @staticmethod
    def _restore_resource_manager(rm, rm_snap: Dict, context: str) -> None:
        warehouse_snap = rm_snap.get("warehouse")
        if warehouse_snap is not None and getattr(rm, '_warehouse', None) is not None:
            CampaignState._restore_payload(
                rm._warehouse, warehouse_snap, f"warehouse of {context}"
            )

        prod_snap = rm_snap.get("actual_production")
        if prod_snap is not None and getattr(rm, '_actual_production', None) is not None:
            CampaignState._restore_payload(
                rm._actual_production, prod_snap, f"actual_production of {context}"
            )

    @staticmethod
    def _restore_asset(asset, asset_snap: Dict) -> None:
        state_snap = asset_snap.get("state")
        if state_snap and getattr(asset, '_state', None) is not None:
            CampaignState._restore_state(asset._state, state_snap, f"asset {asset.id}")

        for field in ("resources_assigned", "resources_to_self_consume", "payload", "production"):
            field_snap = asset_snap.get(field)
            payload_obj = getattr(asset, f"_{field}", None)
            if field_snap is not None and payload_obj is not None:
                CampaignState._restore_payload(
                    payload_obj, field_snap, f"{field} of asset {asset.id}"
                )

    @staticmethod
    def _restore_payload(payload, snap: Dict, context: str) -> None:
        for field in _PAYLOAD_FIELDS:
            val = snap.get(field)
            if val is not None:
                try:
                    setattr(payload, field, val)
                except Exception as exc:
                    logger.warning("Could not restore %s.%s: %s", context, field, exc)

    @staticmethod
    def _restore_route(route, route_snap: Dict, region_name: str) -> None:
        for edge_snap in route_snap.get("edges", {}).values():
            wpA_name = edge_snap.get("wpA_name")
            wpB_name = edge_snap.get("wpB_name")

            edge = next(
                (
                    e for e in getattr(route, '_edges', {}).values()
                    if (getattr(getattr(e, '_wpA', None), 'name', None) == wpA_name and
                        getattr(getattr(e, '_wpB', None), 'name', None) == wpB_name)
                ),
                None,
            )
            if edge is None:
                logger.warning(
                    "Edge '%s-%s' not found in route '%s' of region '%s'. Skipped.",
                    wpA_name, wpB_name, route_snap.get("name"), region_name,
                )
                continue

            if edge_snap.get("danger_level") is not None:
                try:
                    edge.danger_level = float(edge_snap["danger_level"])
                except Exception as exc:
                    logger.warning(
                        "Could not restore danger_level for edge '%s-%s': %s",
                        wpA_name, wpB_name, exc,
                    )

            if edge_snap.get("speed") is not None:
                try:
                    edge.speed = float(edge_snap["speed"])
                except Exception as exc:
                    logger.warning(
                        "Could not restore speed for edge '%s-%s': %s",
                        wpA_name, wpB_name, exc,
                    )

    # ------------------------------------------------------------------ #
    # Private helpers                                                      #
    # ------------------------------------------------------------------ #

    def _ensure_mission(self, mission_id: str, date: str, time: str) -> None:
        if mission_id not in self._state:
            self._state[mission_id] = {"date": date, "time": time, "regions": {}}
        else:
            entry = self._state[mission_id]
            if entry["date"] != date or entry["time"] != time:
                raise ValueError(
                    f"Mission '{mission_id}' already registered with "
                    f"date={entry['date']} time={entry['time']}. "
                    f"Conflicting values: date={date} time={time}."
                )

    # ------------------------------------------------------------------ #
    # Validation helpers                                                   #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _validate_mission_id(mission_id: str) -> None:
        if not isinstance(mission_id, str) or not mission_id:
            raise TypeError("mission_id must be a non-empty string.")

    @staticmethod
    def _validate_date(date: str) -> None:
        try:
            _date.fromisoformat(date)
        except (TypeError, ValueError):
            raise ValueError(f"date must be ISO 8601 'YYYY-MM-DD', got: {date!r}.")

    @staticmethod
    def _validate_time(time: str) -> None:
        try:
            _time.fromisoformat(time)
        except (TypeError, ValueError):
            raise ValueError(f"time must be 'HH:MM' or 'HH:MM:SS', got: {time!r}.")

    @staticmethod
    def _validate_str(value: str, name: str) -> None:
        if not isinstance(value, str) or not value:
            raise TypeError(f"{name} must be a non-empty string.")
