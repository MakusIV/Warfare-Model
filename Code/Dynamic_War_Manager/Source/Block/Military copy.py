from __future__ import annotations
import random
from typing import TYPE_CHECKING, Optional, Dict, List, Literal, Tuple, Union
from heapq import heappop, heappush
from numpy import median
from sympy import Point3D, Point2D

if TYPE_CHECKING:
    from .Region import Region
    from .Vehicle import Vehicle
    from .Aircraft import Aircraft
    from .Ship import Ship
    from .Asset import Asset

from .Block import Block
from .Event import Event
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.Context.Context import (
    STATE, 
    GROUND_COMBAT_EFFICACY, 
    GROUND_ACTION, 
    AIR_TASK,
    MILITARY_CATEGORY,
    GROUND_ASSET_CATEGORY
)

# LOGGING
logger = Logger(module_name=__name__, class_name='Military')

class Military(Block):
    """Military class representing specialized combat Block"""
    
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
    ):
        """
        Initialize a Military
        
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
            name=f"Military.{name}" if name else Utility.setName('Unnamed_Military'),
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

    # Property getters and setters
    @property
    def mil_category(self) -> str:
        """Get military category"""
        return self._mil_category

    @mil_category.setter
    def mil_category(self, value: str) -> None:
        """Set military category"""
        self._validate_mil_category(value)
        self._mil_category = value

    def _validate_mil_category(self, category: str) -> None:
        """Validate military category"""
        if not isinstance(category, str) or category not in MILITARY_CATEGORY.values():
            valid_categories = ", ".join(MILITARY_CATEGORY.values())
            raise ValueError(
                f"Invalid mil_category: {category}. Must be one of: {valid_categories}"
            )

    # Combat capabilities
    def ground_combat_power(self, action: str) -> float:
        """Calculate total ground combat power for specified action"""
        if action not in GROUND_ACTION:
            valid_actions = ", ".join(GROUND_ACTION)
            raise ValueError(f"Invalid action: {action}. Must be one of: {valid_actions}")
        
        return sum(
            asset.combat_power 
            for asset in self.assets.values() 
            if hasattr(asset, 'combat_power') and isinstance(asset, Vehicle)
        )

    def air_combat_power(self, task: str) -> float:
        """Calculate total air combat power for specified task"""
        if task not in AIR_TASK:
            valid_tasks = ", ".join(AIR_TASK)
            raise ValueError(f"Invalid task: {task}. Must be one of: {valid_tasks}")
        
        return sum(
            asset.combat_power 
            for asset in self.assets.values() 
            if hasattr(asset, 'combat_power') and isinstance(asset, Aircraft)
        )

    # Base type checks
    def is_airbase(self) -> bool:
        """Check if base is an airbase"""
        return self._mil_category == Military_CATEGORY["Air Base"]

    def is_groundbase(self) -> bool:
        """Check if base is a ground base"""
        return self._mil_category == Military_CATEGORY["Ground Base"]

    def is_navalgroup(self) -> bool:
        """Check if base is a naval group"""
        return self._mil_category == Military_CATEGORY["Naval Base"]

    # Range calculations
    def artillery_in_range(
        self, 
        target_point: Union[Point2D, Point3D]
    ) -> Tuple[bool, Optional[dict]]:
        """
        Check if target is within artillery range
        
        Args:
            target: Target position (Point or Edge)
            
        Returns:
            Tuple of (in_range, range_level) where:
            - in_range: True if target is in range
            - range_level: Ratio of max_range/target_distance
        """
        if not isinstance(target_point, (Point2D, Point3D)):
            raise TypeError("Target must be Point, Point3D")
            
        target_distance = self._calculate_target_distance(target_point)
        artillery_asset, max_range, med_range, ratio, artillery_asset_quantity = self._get_artillery_range()        

        if artillery_asset:
            result = {
                "target within max range": [False, None],
                "target within med range": [False, None],
                "med/max ratio": ratio,
                "artillery quantity": artillery_asset_quantity,
            }            
            if max_range > target_distance:
                result["target within max range"] = [True, max_range / target_distance] # invertire il ratio?
            if med_range > target_distance:
                result["target within max range"] = [True, med_range / target_distance] # invertire il ratio?
            
            return True, result
        return False, None

    def _calculate_direct_line_target_distance(self, target: Union[Point2D, Point3D, Asset, Block]) -> Optional['float']: # forse non serve, puoi utilizzare
        """Calculate distance to target"""
        if isinstance(target, (Point2D, Point3D)):
            return target.distance(self.position)

        if target.position and isinstance(target, (Point2D, Point3D)):
            return target.position.distance(self.position)

        return None

    def _get_artillery_range(self) -> Tuple[bool, Optional[float], Optional[float], Optional[float], Optional[float]]:
        """Get max, med artillery range, med/max ratio and quantity of all artillery assets"""
        max_range = 0.0
        med_range = 0.0
        range_values = []

        for asset in self.assets.values():
            if (isinstance(asset, (Vehicle, Ship)) and hasattr(asset, 'artillery_range')):
                max_range = max(max_range, asset.artillery_range)
                range_values.append(asset.artillery_range)

        artillery_quantity = len(range_values)
        
        if artillery_quantity > 0:
            med_range = sum(range_values)/artillery_quantity
            return True, max_range, med_range, med_range/max_range, artillery_quantity
        
        return False, None, None, None, None


    # Time calculations
    # Nota: il tempo è calcolato in base ad una distanza in "linea d'aria", quindi va bene solo per asset tipo Aircraft o Ship. In mobile deve essere Override
    def time_to_direct_line_attack(self, target: Union[Point2D, Point3D, Asset, Block]) -> Optional[dict]:
        """
        Calculate estimated time to reach target with direct line path
        
        Args:
            target_position: Target position
            
        Returns:
            dict with time value (med and max) in hours to reach target or infinity if unreachable
        """
        if not isinstance(target, (Point2D, Point3D, Asset, Block)):
            raise TypeError("Target must be Point, Point3D, Asset or Block")
            
        distance = self._calculate_direct_line_target_distance(target)
        max_speed, med_speed, asset_quantity = self._get_attack_speed()

        if max_speed:
            result = {"time": None, "min_time": None}
            result["time"] = distance / med_speed if med_speed > 0 else None
            result["min_time"] = distance / max_speed if max_speed > 0 else None
            return result
        return None

    def _get_attack_speed(self) -> Optional[Tuple]:
        """Get speed of attack-capable assets"""
        med_speed = 0.0
        speed_values = []
        max_speed_values = []
        min_speed = float('inf')
        
        for asset in self.assets.values():
            if self.mil_category in MILITARY_CATEGORY["Ground_Base"] and isinstance(asset, Vehicle) and (asset.isTank or asset.isArmor or asset.isMotorized):
                speed_values.append(asset.speed["off_road"]["nominal"])
                max_speed_values.append(asset.speed["off_road"]["max"])                

            elif self.mil_category == "Airbase" and isinstance(asset, Aircraft) and not (asset.isTransport or asset.isAwacs or asset.isRecon or asset.isHelicopter):
                speed_values.append(asset.speed["nominal"])
                max_speed_values.append(asset.speed["max"])

            elif self.mil_category == "Heliport" and isinstance(asset, Aircraft) and not asset.isHelicopter:
                speed_values.append(asset.speed["nominal"])
                max_speed_values.append(asset.speed["max"])

            elif self.mil_categoryin MILITARY_CATEGORY["Naval_Base"] and isinstance(asset, Ship) and (asset.isCarrier or asset.isDestroyer or asset.isFrigate or asset.isCruiser or asset.isFastAttackShip or asset.isSubamrine):
                speed_values.append(asset.speed["nominal"])
                max_speed_values.append(asset.speed["max"])
        
        asset_quantity = len(speed_values)

        if asset_quantity > 0:
            med_speed = sum(speed_values)/asset_quantity
            max_speed = sum(max_speed_values)/asset_quantity            
            return max_speed, med_speed, asset_quantity

        return None

    # Reconnaissance methods
    def get_recon_efficiency(self) -> float:
        """Calculate median efficiency of reconnaissance assets"""
        recognitors = [
            asset for asset in self.assets.values() 
            if hasattr(asset, 'role') and asset.role == "Recon"
        ]
        return median(
            [asset.get_efficiency("hr_mil") for asset in recognitors]
        ) if recognitors else 0.0

    # Placeholder methods for future implementation
    def air_defense(self) -> None:
        """Calculate air defense volume (to be implemented)"""
        pass

    def combat_range(self, type: str = "Artillery", height: int = 0) -> None:
        """Calculate combat range (to be implemented)"""
        pass

    def defense_aa_range(self, height: int = 0) -> None:
        """Calculate AA defense range (to be implemented)"""
        pass

    def combat_volume(self, type: str = "Artillery") -> None:
        """Calculate combat volume (to be implemented)"""
        pass

    def defense_aa_volume(self) -> None:
        """Calculate AA defense volume (to be implemented)"""
        pass

    def intelligence(self) -> None:
        """Calculate intelligence level (to be implemented)"""
        pass

    def threat_volume(self) -> None:
        """Calculate threat volume (to be implemented)"""
        pass

    def front(self) -> None:
        """Calculate front position (to be implemented)"""
        pass

    def combat_state(self) -> None:
        """Calculate combat state (to be implemented)"""
        pass