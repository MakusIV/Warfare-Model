from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Dict, List, Literal, Tuple, Union
from heapq import heappop, heappush
from numpy import median
from sympy import Point3D, Point2D
from Code.Dynamic_War_Manager.Source.Utility.Utility import validate_class, setName, setId, mean_point
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.DataType.Event import Event
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.Context.Context import (
    GROUND_ACTION, 
    AIR_TASK,
    NAVAL_TASK,
    MILITARY_CATEGORY,    
)
if TYPE_CHECKING:
    from Code.Dynamic_War_Manager.Source.Context.Region import Region
    from Code.Dynamic_War_Manager.Source.Asset.Vehicle import Vehicle
    from Code.Dynamic_War_Manager.Source.Asset.Aircraft import Aircraft
    from Code.Dynamic_War_Manager.Source.Asset.Ship import Ship
    from Code.Dynamic_War_Manager.Source.Asset.Asset import Asset
    

logger = Logger(module_name=__name__, class_name='Military')

class Military(Block):
    """Military class representing specialized combat Block with combat capabilities."""
    
    def __init__(
        self,
        mil_category: str,
        name: Optional[str] = None,
        side: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        sub_category: Optional[str] = None,
        functionality: Optional[str] = None,
        value: Optional[int] = None,
        region: Optional["Region"] = None
    ) -> None:
        """
        Initialize a Military instance.
        
        Args:
            mil_category: Military category (from Military_CATEGORY)
            name: Base name
            side: Base side (Blue/Red/Neutral)
            description: Base description
            category: Base category
            sub_category: Base sub-category
            functionality: Base functionality
            value: Strategic value
            region: Associated region
        """
        super().__init__(
            name=f"Military.{name}" if name else setName('Unnamed_Military'),
            description=description,
            side=side,
            category=category,
            sub_category=sub_category,
            functionality=functionality,
            value=value,
            region=region
        )
        
        self._mil_category = mil_category
        self._validate_mil_category(mil_category)

    #region Properties
    @property
    def mil_category(self) -> str:
        """Get military category."""
        return self._mil_category

    @mil_category.setter
    def mil_category(self, value: str) -> None:
        """Set military category after validation."""
        self._validate_mil_category(value)
        self._mil_category = value
    #endregion

    #region Validation Methods
    def _validate_mil_category(self, category: str) -> None:
        """Validate military category against allowed values."""
        cat = []                    
        for b in MILITARY_CATEGORY.values():
            for c in b:
                cat.append(c)

        if not isinstance(category, str) or category not in cat: #[MILITARY_CATEGORY["Air_Base"], MILITARY_CATEGORY["Naval_Base"], MILITARY_CATEGORY["Ground_Base"]]::   
            valid_categories = ", ".join(cat)
            raise ValueError(
                f"Invalid mil_category: {category}. Must be one of: {valid_categories}"
            )
    #endregion

    def combat_power(self, action: str, military_force: str) -> float:
        """
        Calculate total combat power for specified action and military force.
        
        Args:
            action: action type (from GROUND_ACTION, AIR_TASK and NAVAL_TASK)
            military_force: air, naval or ground
            
        Returns:
            Total combat power of applicable assets
        """
        if not isinstance(action, str):
            raise TypeError(f"Invalid type - action: {action.__class.__.__name__}. Must be str class")
        if not isinstance(military_force, str) or military_force not in ["air", "ground", "naval"]:
            raise TypeError(f"Invalid type - military_force: {action.__class.__.__name__}. Must be str class")
        
        if military_force == "ground":
            action_list = GROUND_ACTION
            asset_type = "Vehicle"
        elif military_force == "air": 
            action_list = AIR_TASK
            asset_type = "Aircraft"
        elif military_force == "naval": 
            action_list = NAVAL_TASK
            asset_type = "Ship"

        if action not in action_list:
            valid_actions = ", ".join(action_list)
            raise ValueError(f"Invalid action: {action}. Must be one of: {valid_actions}")
        
        return sum(
            asset.combat_power() # in mobile 
            for asset in self.assets.values() 
            if validate_class(asset, asset_type) and hasattr(asset, 'combat_power')
        )

    
    #region Base Type Checks
    def is_airbase(self) -> bool:
        """Check if base is an airbase."""
        return self._mil_category in MILITARY_CATEGORY["Air_Base"]

    def is_groundbase(self) -> bool:
        """Check if base is a ground base."""
        return self._mil_category in MILITARY_CATEGORY["Ground_Base"]

    def is_navalgroup(self) -> bool:
        """Check if base is a naval group."""
        return self._mil_category in MILITARY_CATEGORY["Naval_Base"]
    #endregion

    #region Range Calculations
    def artillery_in_range(
        self, 
        target_point: Union[Point2D, Point3D]
    ) -> Tuple[bool, Optional[dict]]:
        """
        Check if target is within artillery range.
        
        Args:
            target_point: Target position (Point2D or Point3D)
            
        Returns:
            Tuple of (in_range, range_info) where:
            - in_range: True if target is in range of any artillery
            - range_info: Dictionary with range details if in range
        """
        if not isinstance(target_point, (Point2D, Point3D)):
            raise TypeError("Target must be Point2D or Point3D")
        
        position = self.position

        if position:
            target_distance = target_point.distance(self.position)
            has_artillery, max_range, med_range, ratio, quantity = self._get_artillery_stats()

            if not has_artillery:
                return False, None
        else: 
            return False, None
            
        result = {
            "target_within_max_range": max_range >= target_distance,
            "target_within_med_range": med_range >= target_distance,
            "max_range_ratio": max_range / target_distance if max_range > 0 else 0,
            "med_range_ratio": med_range / target_distance if med_range > 0 else 0,
            "artillery_quantity": quantity,
        }
        
        return True, result

    def _get_artillery_stats(self) -> Tuple[bool, float, float, float, int]:
        """
        Calculate artillery statistics for the military unit.
        
        Returns:
            Tuple containing:
            - has_artillery: Boolean indicating if any artillery exists
            - max_range: Maximum range of all artillery
            - med_range: Median range of all artillery
            - ratio: Median to max range ratio
            - quantity: Number of artillery assets
        """
        range_values = [
            asset.artillery_range 
            for asset in self.assets.values() 
            if ( validate_class(asset, "Vehicle") or validate_class(asset, "Ship") ) and hasattr(asset, 'artillery_range')            
        ]
        
        if not range_values:
            return False, 0.0, 0.0, 0.0, 0
            
        max_range = max(range_values)
        med_range = median(range_values)
        ratio = med_range / max_range if max_range > 0 else 0
        quantity = len(range_values)
        
        return True, max_range, med_range, ratio, quantity
    #endregion

    #region Time Calculations
    def time_to_direct_line_attack(
        self, 
        target: Union[Point2D, Point3D, Asset, Block]
    ) -> Optional[Dict[str, float]]:
        """
        Calculate estimated time to reach target with direct line path.
        
        Args:
            target: Target position or object with position
            
        Returns:
            Dictionary with time estimates in hours or None if unreachable
        """
        distance = self._get_target_distance(target)
        if distance is None:
            return None
            
        max_speed, med_speed, _ = self._get_attack_speeds()
        if max_speed is None:
            return None
            
        return {
            "time": distance / med_speed if med_speed > 0 else float('inf'),
            "min_time": distance / max_speed if max_speed > 0 else float('inf')
        }

    def _get_target_distance(self, target: Union[Point2D, Point3D, Asset, Block]) -> Optional[float]:
        """Calculate distance to target."""
        if self.position: 
            if isinstance(target, (Point2D, Point3D)):
                return target.distance(self.position)
            elif hasattr(target, 'position') and target.position != None and isinstance(target.position, (Point2D, Point3D)):
                return target.position.distance(self.position)
        return None

    def _get_attack_speeds(self) -> Tuple[Optional[float], Optional[float], int]:
        """
        Get speed statistics for attack-capable assets.
        
        Returns:
            Tuple containing:
            - max_speed: Average maximum speed of attack assets
            - med_speed: Average nominal speed of attack assets
            - quantity: Number of attack-capable assets
        """
        speed_values = []
        max_speed_values = []
        
        for asset in self.assets.values():
            if self._is_attack_asset(asset):
                speed_values.append(self._get_nominal_speed(asset))
                max_speed_values.append(self._get_max_speed(asset))
        
        if not speed_values:
            return None, None, 0
            
        return (
            sum(max_speed_values) / len(max_speed_values),
            sum(speed_values) / len(speed_values),
            len(speed_values)
        )

    def _is_attack_asset(self, asset: Union[Vehicle, Aircraft, Ship]) -> bool:
        """Check if asset is attack-capable based on military category."""
        if self.is_groundbase() and validate_class(asset, "Vehicle"):
            return asset.isTank or asset.isArmor or asset.isMotorized
        elif self.is_airbase() and validate_class(asset, "Aircraft"):
            return not (asset.isTransport or asset.isAwacs or asset.isRecon or asset.isHelicopter)
        elif self.is_helibase() and validate_class(asset, "Aircraft"):
            return asset.isHelicopter
        elif self.is_navalgroup() and validate_class(asset, "Ship"):
            return (asset.isCarrier or asset.isDestroyer or asset.isFrigate or 
                    asset.isCruiser or asset.isFastAttackShip or asset.isSubmarine)
        return False

    def _get_nominal_speed(self, asset: Union[Vehicle, Aircraft, Ship]) -> float:
        """Get nominal speed of asset based on type."""
        if validate_class(asset, "Vehicle"):
            return asset.speed.get("off_road", {}).get("nominal", 0)
        return asset.speed.get("nominal", 0)

    def _get_max_speed(self, asset: Union[Vehicle, Aircraft, Ship]) -> float:
        """Get maximum speed of asset based on type."""
        if validate_class(asset, "Vehicle"):
            return asset.speed.get("off_road", {}).get("max", 0)
        return asset.speed.get("max", 0)
    #endregion

    #region Reconnaissance Methods
    def get_recon_efficiency(self) -> float:
        """
        Calculate median efficiency of reconnaissance assets.
        
        Returns:
            Median efficiency of recon assets or 0.0 if none exist
        """
        recognitors = [
            asset for asset in self.assets.values() 
            if hasattr(asset, 'role') and asset.role == "Recon"
        ]
        #eff = [asset.efficiency for asset in recognitors] if recognitors else 0.0
        return median(
            [asset.efficiency() for asset in recognitors]
        ) if recognitors else 0.0
    #endregion

    #region Placeholder Methods for Future Implementation
    def air_defense(self) -> None:
        """Calculate air defense volume (to be implemented)."""
        pass

    def combat_range(self, type: str = "Artillery", height: int = 0) -> None:
        """Calculate combat range (to be implemented)."""
        pass

    def defense_aa_range(self, height: int = 0) -> None:
        """Calculate AA defense range (to be implemented)."""
        pass

    def combat_volume(self, type: str = "Artillery") -> None:
        """Calculate combat volume (to be implemented)."""
        pass

    def defense_aa_volume(self) -> None:
        """Calculate AA defense volume (to be implemented)."""
        pass

    def intelligence(self) -> None:
        """Calculate intelligence level (to be implemented)."""
        pass

    def threat_volume(self) -> None:
        """Calculate threat volume (to be implemented)."""
        pass

    def front(self) -> None:
        """Calculate front position (to be implemented)."""
        pass

    def combat_state(self) -> None:
        """Calculate combat state (to be implemented)."""
        pass
    #endregion