from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union, Tuple
from dataclasses import dataclass
from collections import defaultdict
import logging
from functools import lru_cache
from enum import Enum

# Assuming these imports exist in your codebase
from Code.Dynamic_War_Manager.Source.Context import Context
from Code.Dynamic_War_Manager.Source.Utility import Utility
from Code.Dynamic_War_Manager.Source.Block.Block import Block, MAX_VALUE, MIN_VALUE
from Code.Dynamic_War_Manager.Source.Block.Military import Military
from Code.Dynamic_War_Manager.Source.Block.Production import Production
from Code.Dynamic_War_Manager.Source.Block.Storage import Storage
from Code.Dynamic_War_Manager.Source.Block.Transport import Transport
from Code.Dynamic_War_Manager.Source.Block.Urban import Urban
from Code.Dynamic_War_Manager.Source.DataType.Limes import Limes
from Code.Dynamic_War_Manager.Source.DataType.Route import Route
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from sympy import Point2D

# CONSTANTS
DEFAULT_ATTACK_WEIGHT = 0.5
MILITARY_FORCES = ["ground", "air", "naval"]
ACTION_TASKS = {
    "ground": Context.GROUND_ACTION,
    "air": Context.AIR_TASK,
    "naval": Context.NAVAL_TASK
}

DEFAULT_WEIGHT_PRIORITY_TARGET = {
    "Ground_Base": {
        "attack": {"Ground_Base": 0.7, "Naval_Base": 0.0, "Air_Base": 0.1, "Logistic": 0.2, "Civilian": 0.0},
        "defence": {"Ground_Base": 0.1, "Naval_Base": 0.1, "Air_Base": 0.1, "Logistic": 0.4, "Civilian": 0.3}
    },
    "Air_Base": {
        "attack": {"Ground_Base": 0.3, "Naval_Base": 0.2, "Air_Base": 0.2, "Logistic": 0.3, "Civilian": 0.0},
        "defence": {"Ground_Base": 0.3, "Naval_Base": 0.1, "Air_Base": 0.2, "Logistic": 0.3, "Civilian": 0.0}
    },
    "Naval_Base": {
        "attack": {"Ground_Base": 0.0, "Naval_Base": 0.5, "Air_Base": 0.2, "Logistic": 0.3, "Civilian": 0.0},
        "defence": {"Ground_Base": 0.1, "Naval_Base": 0.6, "Air_Base": 0.1, "Logistic": 0.2, "Civilian": 0.0}
    }
}

# LOGGING
logger = Logger(module_name=__name__, class_name='Region')


class BlockCategory(Enum):
    MILITARY = "Military"
    LOGISTIC = "Logistic"
    CIVILIAN = "Civilian"


@dataclass
class BlockItem:
    """Represents a block with its priority in the region"""
    priority: float
    block: Block
    
    def __post_init__(self):
        if not isinstance(self.priority, (int, float)):
            raise TypeError("Priority must be a number")
        if self.priority < 0:
            raise ValueError("Priority must be non-negative")


@dataclass
class RegionParams:
    """Data class for Region parameters validation"""
    name: str
    description: str = ""
    blocks: Optional[List[BlockItem]] = None
    routes: Optional[Dict[str, Route]] = None
    limes: Optional[List[Limes]] = None


class Region:
    """
    Optimized Region class for managing military operations.
    
    This class manages blocks, routes, and strategic calculations for a region
    in a military simulation system.
    """
    
    def __init__(self, name: str, limes: Optional[List[Limes]] = None, 
                 description: Optional[str] = None, blocks: Optional[List[BlockItem]] = None,
                 routes: Optional[Dict[str, Route]] = None):
        """
        Initialize a Region with validation and proper data structures.
        
        Args:
            name: Region name
            limes: List of boundary lines
            description: Region description
            blocks: List of BlockItem objects
            routes: Dictionary mapping route keys to Route objects
        """
        self._validate_init_params(name, limes, description, blocks, routes)
        
        self._name = name
        self._description = description or ""
        self._limes = limes or []
        self._attack_weight = DEFAULT_ATTACK_WEIGHT
        self._weight_priority_target = DEFAULT_WEIGHT_PRIORITY_TARGET.copy()
        
        # Initialize blocks with proper association
        self._blocks: List[BlockItem] = []
        if blocks:
            for block_item in blocks:
                self._add_block_item(block_item)
        
        # Initialize routes
        self._routes: Dict[str, Route] = routes or {}
        
        # Cache for expensive calculations
        self._cache = {}
        self._cache_valid = False
    
    # PROPERTIES
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str):
        self._validate_string_param('name', value)
        self._name = value
        self._invalidate_cache()
    
    @property
    def description(self) -> str:
        return self._description
    
    @description.setter
    def description(self, value: str):
        self._validate_string_param('description', value)
        self._description = value
    
    @property
    def attack_weight(self) -> float:
        return self._attack_weight
    
    @attack_weight.setter
    def attack_weight(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("Attack weight must be a number")
        if not 0 <= value <= 1:
            raise ValueError("Attack weight must be between 0 and 1")
        self._attack_weight = float(value)
        self._invalidate_cache()
    
    @property
    def weight_priority_target(self) -> Dict:
        return self._weight_priority_target.copy()
    
    @weight_priority_target.setter
    def weight_priority_target(self, value: Dict):
        self._validate_weight_priority_target(value)
        self._weight_priority_target = value.copy()
        self._invalidate_cache()
    
    @property
    def blocks(self) -> List[BlockItem]:
        return self._blocks.copy()
    
    @property
    def routes(self) -> Dict[str, Route]:
        return self._routes.copy()
    
    # BLOCK MANAGEMENT
    def add_block(self, block: Block, priority: float = 0.0) -> None:
        """Add a block to the region with specified priority."""
        if not isinstance(block, Block):
            raise TypeError("Block must be a Block instance")
        
        if block.region is not None and block.region != self:
            raise ValueError(f"Block {block.name} is already associated with another region")
        
        block_item = BlockItem(priority=priority, block=block)
        self._add_block_item(block_item)
        logger.info(f"Block {block.name} added to region {self.name}")
    
    def _add_block_item(self, block_item: BlockItem) -> None:
        """Internal method to add a block item with validation."""
        if not isinstance(block_item, BlockItem):
            raise TypeError("Expected BlockItem instance")
        
        # Check if block already exists
        if any(item.block.id == block_item.block.id for item in self._blocks):
            raise ValueError(f"Block {block_item.block.name} already exists in region")
        
        # Associate block with region
        block_item.block.region = self
        self._blocks.append(block_item)
        self._invalidate_cache()
    
    def remove_block(self, block_id: str) -> bool:
        """Remove a block from the region by ID."""
        if not isinstance(block_id, str):
            raise TypeError("Block ID must be a string")
        
        for i, block_item in enumerate(self._blocks):
            if block_item.block.id == block_id:
                # Clear block association
                block_item.block.region = None
                self._blocks.pop(i)
                self._invalidate_cache()
                logger.info(f"Block {block_id} removed from region {self.name}")
                return True
        
        logger.warning(f"Block {block_id} not found in region {self.name}")
        return False
    
    def get_block_by_id(self, block_id: str) -> Optional[BlockItem]:
        """Get a block item by its ID."""
        if not isinstance(block_id, str):
            raise TypeError("Block ID must be a string")
        
        for block_item in self._blocks:
            if block_item.block.id == block_id:
                return block_item
        
        return None
    
    def get_blocks_by_criteria(self, side: Optional[str] = None, 
                              category: Optional[str] = None,
                              block_class: Optional[type] = None) -> List[BlockItem]:
        """
        Get blocks filtered by criteria.
        
        Args:
            side: Filter by side (e.g., 'red', 'blue')
            category: Filter by category ('Military', 'Logistic', 'Civilian')
            block_class: Filter by block class type
        
        Returns:
            List of matching BlockItem objects
        """
        result = []
        
        for block_item in self._blocks:
            block = block_item.block
            
            # Filter by side
            if side and hasattr(block, 'side') and block.side != side:
                continue
            
            # Filter by category
            if category and not self._block_matches_category(block, category):
                continue
            
            # Filter by class
            if block_class and not isinstance(block, block_class):
                continue
            
            result.append(block_item)
        
        return result
    
    def get_highest_priority_blocks(self, count: int, side: Optional[str] = None,
                                   category: Optional[str] = None) -> List[BlockItem]:
        """Get the highest priority blocks matching criteria."""
        if count < 1:
            raise ValueError("Count must be positive")
        
        blocks = self.get_blocks_by_criteria(side=side, category=category)
        blocks.sort(key=lambda x: x.priority, reverse=True)
        
        return blocks[:count]
    
    def get_blocks_in_priority_range(self, min_priority: float, max_priority: float,
                                   side: Optional[str] = None,
                                   category: Optional[str] = None) -> List[BlockItem]:
        """Get blocks within a priority range."""
        if min_priority > max_priority:
            raise ValueError("Min priority must be <= max priority")
        
        blocks = self.get_blocks_by_criteria(side=side, category=category)
        
        return [block_item for block_item in blocks 
                if min_priority <= block_item.priority <= max_priority]
    
    # ROUTE MANAGEMENT
    def add_route(self, key: str, route: Route) -> None:
        """Add a route to the region."""
        if not isinstance(key, str):
            raise TypeError("Route key must be a string")
        if not isinstance(route, Route):
            raise TypeError("Route must be a Route instance")
        
        self._routes[key] = route
        logger.info(f"Route {key} added to region {self.name}")
    
    def get_route(self, block_id: str, target_block_id: Optional[str] = None) -> Optional[Route]:
        """Get route between blocks."""
        if not isinstance(block_id, str):
            raise TypeError("Block ID must be a string")
        
        if target_block_id and not isinstance(target_block_id, str):
            raise TypeError("Target block ID must be a string")
        
        if target_block_id == block_id:
            raise ValueError("Target block ID must be different from source block ID")
        
        # Find routes that include both blocks
        matching_routes = []
        
        for key, route in self._routes.items():
            # Parse key to extract block IDs (assuming comma-separated format)
            block_ids = [bid.strip() for bid in key.split(',')]
            
            if block_id in block_ids:
                if target_block_id is None or target_block_id in block_ids:
                    matching_routes.append(route)
        
        if not matching_routes:
            return None
        
        # Return shortest route if multiple matches
        if len(matching_routes) == 1:
            return matching_routes[0]
        
        return min(matching_routes, key=lambda r: r.length())
    
    # STRATEGIC CALCULATIONS
    
    # da fare:
    # def calc_military_production(self, side: str) -> List[hc, hs, hb]
    # da utilizzare per il calcolo dei livelli di abilità (skill) e nelle capacità di combattimento


    @lru_cache(maxsize = 128)
    def calc_strategic_logistic_center(self, side: str) -> Optional[Point2D]:
        """Calculate the strategic logistic center for a side."""
        logistic_blocks = self.get_blocks_by_criteria(side = side, category = "Logistic")
        
        if not logistic_blocks:
            return None
        
        total_priority = 0
        weighted_position = None               
        
        for block_item in logistic_blocks:
            block = block_item.block
            priority = block_item.priority
            if hasattr(block, 'position') and priority > 0.0:
                position = Point2D(block.position.x, block.position.y)            
                total_priority += priority
                if not weighted_position:
                    weighted_position = position * priority
                else:
                    weighted_position += position * priority
        
        if total_priority == 0:
            return None
        
        return weighted_position / total_priority

    def calc_combat_power_center(self, side: str): 
        """ Calculation of baricenter point of the complessive military block's combat power 

        Args:
            side (str): side of blocks
            force (str): type of military force (air, ground, naval)

        Returns:
            Point2D: combat power baricenter
        """                
        blocks_quantity = {}

        for force in MILITARY_FORCES:
            for task in ACTION_TASKS[force]:                    
                blocks_quantity[force][task] = 0

        Militarys = self.get_blocks("Military", side)                                
        r_CPP, tot_CP, tp = {}, {}, {} # tot_CP: summmatory of strategic block combat power
        
        for force in MILITARY_FORCES:
            for task in ACTION_TASKS[force]:                                    
                for block in Militarys:
                    if ( block.is_Air_Base and force == "air" ) or (block.is_Ground_Base and force == "ground") or ( block.is_navalbase and force == "naval" ):
                        cp = block.combat_power(action = task, military_force = force) # block combat power 
                        tot_CP[force][task] += cp  # sum of block's combat power 
                        tp[force][task] += block.position * cp  # sum of ponderate position block's point
                        blocks_quantity[force][task] += 1 # number of blocks counted
        
        for force in MILITARY_FORCES:
                for task in ACTION_TASKS[force]:                    
                    r_CPP[force][task] = tp[force][task] / ( blocks_quantity[force][task] * tot_CP[force][task] ) # r_CPP: region strategic combat power center position for side blocks
        return r_CPP
    
    def calc_total_warehouse(self) -> Payload:
        """Calculate total warehouse resources."""
        total = Payload()
        
        for block_item in self._blocks:
            if hasattr(block_item.block, 'resource_manager'):
                total += block_item.block.resource_manager.warehouse()
        
        return total
    
    def calc_total_production(self) -> Payload:
        """Calculate total production resources."""
        total = Payload()
        
        for block_item in self._blocks:
            if isinstance(block_item.block, Production):
                total += block_item.block.resource_manager.actual_production()
        
        return total
    
    def calc_production_values(self) -> Dict[str, float]:
        """Calculate production values by block type."""
        values = {"production": 0.0, "storage": 0.0, "transport": 0.0, "urban": 0.0}
        
        for block_item in self._blocks:
            block = block_item.block
            if hasattr(block, 'resource_manager'):
                production_value = block.resource_manager.production_value()
                
                if isinstance(block, Production):
                    values["production"] += production_value
                elif isinstance(block, Storage):
                    values["storage"] += production_value
                elif isinstance(block, Transport):
                    values["transport"] += production_value
                elif isinstance(block, Urban):
                    values["urban"] += production_value
        
        values["total"] = sum(values.values())
        return values
    
    # PRIORITY UPDATES
    def update_logistic_priorities(self) -> bool:
        """Update priorities for logistic blocks based on production values."""
        production_values = self.calc_production_values()
        
        if production_values["total"] == 0:
            logger.warning("No production value found, setting logistic priorities to 0")
            return False
        
        for block_item in self._blocks:
            block = block_item.block
            
            if self._is_logistic_block(block):
                block_production_value = block.resource_manager.production_value()
                
                if block_production_value > 0:
                    # Calculate relative priority based on block type
                    if isinstance(block, Production):
                        denominator = production_values["production"]
                    elif isinstance(block, Storage):
                        denominator = production_values["storage"]
                    elif isinstance(block, Transport):
                        denominator = production_values["transport"]
                    elif isinstance(block, Urban):
                        denominator = production_values["urban"]
                    else:
                        continue
                    
                    if denominator > 0:
                        absolute_priority = block_production_value * block.value
                        block_item.priority = absolute_priority / denominator
                        logger.debug(f"Updated priority for {block.name}: {block_item.priority}")
        
        self._invalidate_cache()
        return True
    
    def update_military_priorities(self, side: str) -> None:
        """Update priorities for military blocks."""
        if not isinstance(side, str):
            raise TypeError("Side must be a string")
        
        friendly_blocks = self.get_blocks_by_criteria(side=side, category="Military")
        enemy_blocks = self.get_blocks_by_criteria(side=Utility.enemySide(side))
        
        for block_item in friendly_blocks:
            military_block = block_item.block
            
            if not isinstance(military_block, Military):
                continue
            
            attack_priority = self._calc_attack_priority(military_block, enemy_blocks)
            defense_priority = self._calc_defense_priority(military_block, friendly_blocks)
            
            # Combined priority based on attack weight
            overall_priority = (attack_priority * self._attack_weight + 
                              defense_priority * (1 - self._attack_weight))
            
            block_item.priority = overall_priority
            logger.debug(f"Updated military priority for {military_block.name}: {overall_priority}")
        
        self._invalidate_cache()
    
    # HELPER METHODS
    def _block_matches_category(self, block: Block, category: str) -> bool:
        """Check if a block matches the specified category."""
        if category == "Military":
            return isinstance(block, Military)
        elif category == "Logistic":
            return isinstance(block, (Production, Storage, Transport))
        elif category == "Civilian":
            return isinstance(block, Urban)
        else:
            return hasattr(block, 'category') and block.category == category
    
    def _is_logistic_block(self, block: Block) -> bool:
        """Check if a block is a logistic block."""
        return isinstance(block, (Production, Storage, Transport))
    
    def _calc_attack_priority(self, military_block: Military, enemy_blocks: List[BlockItem]) -> float:
        """Calculate attack priority for a military block."""
        # Simplified calculation - should be expanded based on requirements
        priority = 0.0
        block_category = military_block.get_military_category()

        
        for enemy_item in enemy_blocks:
            target = enemy_item.block
            #setup target block category to select weight index
            if target.is_military():
                target_category = target.get_military_category()
            elif target.is_civilian() or target.is_logistic():
                target_category = target.category              
            else:
                logger.warning(f"the  block{target!r} is not a military base, logistical or civil block; block weight will be set with Civilian value")
                target_category = "Civilian"
            
            # weight selection
            weight = self.weight_priority_target[block_category]["attack"][target_category]
            
            
            # priority summatory
            if military_block.is_Ground_Base() or military_block.is_Naval_Base():                    
                priority += self._calc_surface_priority(block = military_block, target_item = enemy_item, attack_route = self.get_route(military_block, target), weight = weight)
            elif military_block.is_Air_Base():                    
                priority += self._calc_air_priority(block = military_block, target_block = target, weight = weight)

        
        return priority
    
    def _calc_defense_priority(self, military_block: Military, friendly_blocks: List[BlockItem]) -> float:
        """Calculate defense priority for a military block."""
        # Simplified calculation - should be expanded based on requirements
        priority = 0.0
        block_category = military_block.get_military_category()
        
        for friendly_item in friendly_blocks:
            if friendly_item.block != military_block:
                friendly = friendly_item.block  
                #setup target block category to select weight index
                if friendly.is_military():
                    friendly_category =friendly.get_military_category()
                elif friendly.is_civilian() or friendly.is_logistic():
                    friendly_category = friendly.category              
                else:
                    logger.warning(f"the  block{friendly!r} is not a military base, logistical or civil block; block weight will be set with Civilian value")
                    friendly_category = "Civilian"
                
                # weight selection
                weight = self.weight_priority_target[block_category]["defence"][friendly_category]
                
                if military_block.is_Ground_Base() or military_block.is_Naval_Base():
                    priority += self._calc_surface_priority(block = military_block, target_item = friendly_item, attack_route = self.get_route(military, friendly), weight = weight)
                elif military_block.is_Air_Base():                
                    priority += self._calc_air_priority(block = military_block, target_block = friendly, weight = weight)
        
        return priority
    

    def _calc_surface_priority(self, block: Military, target_item: BlockItem, attack_route: Route, weight: float) -> Optional[float]:   
        """getBlocks
        calculates the priority of a military block (ground or naval) by evaluating its combat power, the distance from the target, the combat power of the target or the 
        priority assigned in the case of logistical targets.

        Args:                
            block (Military): block to calculates priority
            target_block (Block): target of the block
            attack_route (Route): intercept route to target_block
            weight (float): assigned weight for calulates priority

        Returns:
            priority (float): priority value of the block
        """    
        
        combat_power = block.combat_power()
        target_block = target_item.block

        if not combat_power:
            return None

        if block.is_Ground_Base or block.is_Naval_Base:            
            arty_combat_range = block.artillery_in_range( target_block.position )                        
        if block.is_Ground_Base:
            time_to_intercept = block.time2attack( route = attack_route )   
        elif block.is_Naval_Base:
            time_to_intercept = block.time2attack( target = target_block.position )   
        if time_to_intercept < 1: # second
                time_to_intercept = 1                
        if not arty_combat_range["target_within_med_range"] and not time_to_intercept or time_to_intercept == float('inf'):
            return None # not exist route to intercept and target is outer range 
        
        target_default_strategic_value = target_block.value

        if not target_default_strategic_value:
                target_default_strategic_value = 1
        
        if arty_combat_range["target_within_med_range"]: # combat_range > distance to target -> combat_range_ratio > 1
            range_ratio = arty_combat_range["med_range_ratio"]
        else:
            range_ratio = 1
        
        if target_block.is_military:
            target_combat_power = target_block.combat_power()                            

            if combat_power > 0.0:
                combat_power_ratio = target_combat_power / combat_power
                if combat_power_ratio > 10.0:
                    combat_power_ratio = 10.0
                if combat_power_ratio < 0.1:
                    combat_power_ratio = 0.1                                    
            priority = target_default_strategic_value * combat_power_ratio * range_ratio * weight / time_to_intercept
            return priority
        
        if target_block.is_logistic:                
            target_priority = target_item.priority
            
            if not target_priority:
                self.update_logistic_blocks_priority()
            priority = target_priority * range_ratio * weight / time_to_intercept                
            return priority
            
        return None
            
    
    def _calc_air_priority(self, block: Military, target_block: Block, weight: float) -> Optional[float]:     
        """
        calculates the priority of a military block (ground or naval) by evaluating its combat power, the distance from the target, the combat power of the target or the 
        priority assigned in the case of logistical targets.

        Args:                
            block (Military): block to calculates priority
            target_block (Block): target of the block                
            weight (float): assigned weight for calculates priority

        Returns:
            priority (float): priority value of the block
        """                            
        combat_power = block.combat_power()
        
        if not combat_power:
            return None
        
        time_to_intercept = block.time2attack( target = target_block.position )   

        if time_to_intercept < 1: # second
            time_to_intercept = 1                
        
        target_default_strategic_value = target_block.value

        if not target_default_strategic_value:
            target_default_strategic_value = 1            
        
        if target_block.is_military:
            target_combat_power = target_block.combat_power( military_force = "ground" )        
            
            if combat_power > 0.0:
                combat_power_ratio = target_combat_power / combat_power
                if combat_power_ratio > 10.0:
                    combat_power_ratio = 10.0
                if combat_power_ratio < 0.1:
                    combat_power_ratio = 0.1                                    
            priority = target_default_strategic_value * combat_power_ratio * weight / time_to_intercept
            return priority
        
        if target_block.is_logistic:                
            target_priority, _ = self.get_block_by_id(block.id)
            
            if not target_priority:
                self.update_logistic_blocks_priority()
            priority = target_priority * weight / time_to_intercept                
            return priority
            
        return None                    


    
    def _invalidate_cache(self) -> None:
        """Invalidate calculation cache."""
        self._cache.clear()
        self._cache_valid = False
    
    # VALIDATION METHODS
    def _validate_init_params(self, name: str, limes: Optional[List[Limes]], 
                            description: Optional[str], blocks: Optional[List[BlockItem]],
                            routes: Optional[Dict[str, Route]]) -> None:
        """Validate initialization parameters."""
        if not isinstance(name, str) or not name:
            raise ValueError("Name must be a non-empty string")
        
        if limes is not None and not isinstance(limes, list):
            raise TypeError("Limes must be a list")
        
        if description is not None and not isinstance(description, str):
            raise TypeError("Description must be a string")
        
        if blocks is not None:
            if not isinstance(blocks, list):
                raise TypeError("Blocks must be a list")
            for block_item in blocks:
                if not isinstance(block_item, BlockItem):
                    raise TypeError("All blocks must be BlockItem instances")
        
        if routes is not None:
            if not isinstance(routes, dict):
                raise TypeError("Routes must be a dictionary")
            for key, route in routes.items():
                if not isinstance(key, str):
                    raise TypeError("Route keys must be strings")
                if not isinstance(route, Route):
                    raise TypeError("Route values must be Route instances")
    
    def _validate_string_param(self, param_name: str, value: str) -> None:
        """Validate string parameter."""
        if not isinstance(value, str):
            raise TypeError(f"{param_name} must be a string")
    
    def _validate_weight_priority_target(self, value: Dict) -> None:
        """Validate weight priority target structure."""
        if not isinstance(value, dict):
            raise TypeError("Weight priority target must be a dictionary")
        
        # Add more specific validation based on expected structure
        for category, weights in value.items():
            if not isinstance(weights, dict):
                raise TypeError(f"Weights for {category} must be a dictionary")
            
            if 'attack' not in weights or 'defence' not in weights:
                raise ValueError(f"Category {category} must have 'attack' and 'defence' keys")
    
    def __repr__(self) -> str:
        """String representation of the Region."""
        return (f"Region(name='{self._name}', description='{self._description}', "
                f"blocks={len(self._blocks)}, routes={len(self._routes)})")
    
    def __str__(self) -> str:
        """Readable string representation."""
        return f"Region '{self.name}' with {len(self._blocks)} blocks"