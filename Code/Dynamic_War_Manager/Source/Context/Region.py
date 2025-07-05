from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union, Tuple
from dataclasses import dataclass, field
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
from numpy import clip



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
        "defense": {"Ground_Base": 0.1, "Naval_Base": 0.1, "Air_Base": 0.1, "Logistic": 0.4, "Civilian": 0.3}
    },
    "Air_Base": {
        "attack": {"Ground_Base": 0.3, "Naval_Base": 0.2, "Air_Base": 0.2, "Logistic": 0.3, "Civilian": 0.0},
        "defense": {"Ground_Base": 0.3, "Naval_Base": 0.1, "Air_Base": 0.2, "Logistic": 0.3, "Civilian": 0.0}
    },
    "Naval_Base": {
        "attack": {"Ground_Base": 0.0, "Naval_Base": 0.5, "Air_Base": 0.2, "Logistic": 0.3, "Civilian": 0.0},
        "defense": {"Ground_Base": 0.1, "Naval_Base": 0.6, "Air_Base": 0.1, "Logistic": 0.2, "Civilian": 0.0}
    }
}

# Logger setup
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
        self._attack_weight = DEFAULT_ATTACK_WEIGHT  # Copia per evitare modifiche involontarie        
        self._weight_priority_target = DEFAULT_WEIGHT_PRIORITY_TARGET.copy()   # Copia per evitare modifiche involontarie
        
        # Inizializza i blocchi con associazione corretta. 
        # Utilizziamo un dizionario per un accesso O(1) per ID.
        self._blocks: Dict[str, BlockItem] = {}
        if blocks:
            for block_item in blocks:
                self._add_block_item(block_item)
        
        # Initialize routes
        self._routes: Dict[str, Route] = routes or {}
        
        # Non è più necessaria una cache manuale con l'uso di @lru_cache sui metodi
        # self._cache = {} 
        # self._cache_valid = False 
    
    # PROPERTIES
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str):
        if not isinstance(value, str) or not value: # Validazione inline per setter
            raise ValueError(f"Name must be a non-empty string, got {type(value).__name__}")
        self._name = value
        self._invalidate_caches() # Invalidare tutte le cache lru
    
    @property
    def description(self) -> str:
        return self._description
    
    @description.setter
    def description(self, value: str):
        if not isinstance(value, str):
            raise TypeError(f"Description must be a string, got {type(value).__name__}")
        self._description = value
    
    @property
    def attack_weight(self) -> float:
        return self._attack_weight
    
    @attack_weight.setter
    def attack_weight(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError(f"Attack weight must be a number, got {type(value).__name__}")
        if not 0 <= value <= 1:
            raise ValueError(f"Attack weight must be between 0 and 1, got {value}")
        self._attack_weight = float(value)
        self._invalidate_caches()
    
    @property
    def weight_priority_target(self) -> Dict:
        return self._weight_priority_target.copy()
    
    @weight_priority_target.setter
    def weight_priority_target(self, value: Dict):
        self._validate_weight_priority_target(value)
        self._weight_priority_target = value.copy()
        self._invalidate_caches()
    
    @property
    def blocks(self) -> List[BlockItem]:
        # Restituisce una lista dei valori del dizionario
        return list(self._blocks.values()) 
    
    @property
    def routes(self) -> Dict[str, Route]:
        return self._routes.copy()
    
    # BLOCK MANAGEMENT
    def add_block(self, block: Block, priority: float = 0.0) -> None:
        """Add a block to the region with specified priority."""
        if not isinstance(block, Block):
            raise TypeError(f"Block must be a Block instance, got {type(block).__name__}")
        
        if block.region is not None and block.region != self:
            raise ValueError(f"Block {block.name} is already associated with another region")
        
        block_item = BlockItem(priority=priority, block=block)
        self._add_block_item(block_item) # la cache viene invalidata in _add_block_item
        logger.info(f"Block {block.name} added to region {self.name}")        
    
    def _add_block_item(self, block_item: BlockItem) -> None:
        """Internal method to add a block item with validation."""
        if not isinstance(block_item, BlockItem):
            raise TypeError(f"Expected BlockItem instance, got {type(block_item).__name__}")
        
        # Check if block already exists using dictionary key check
        if block_item.block.id in self._blocks:
            raise ValueError(f"Block {block_item.block.name} already exists in region")
        
        # Associate block with region and add to dictionary
        block_item.block.region = self
        self._blocks[block_item.block.id] = block_item # Aggiunto al dizionario
        self._invalidate_caches()# Invalidate caches after adding a block_iem : inutule invalidare selettivamente in quanto qualsiasi nuova route, block cambia priority e coseguentemente logistic e military center
    
    def remove_block(self, block_id: str) -> bool:
        """Remove a block from the region by ID."""
        if not isinstance(block_id, str):
            raise TypeError(f"Block ID must be a string, got {type(block_id).__name__}")
        
        block_item = self._blocks.pop(block_id, None) # Accesso O(1)
        if block_item:
            # Clear block association
            block_item.block.region = None
            self._invalidate_caches()
            logger.info(f"Block {block_id} removed from region {self.name}")
            return True
        
        logger.warning(f"Block {block_id} not found in region {self.name}")
        return False
    
    def get_block_by_id(self, block_id: str) -> Optional[BlockItem]:
        """Get a block item by its ID."""
        if not isinstance(block_id, str):
            raise TypeError(f"Block ID must be a string, got {type(block_id).__name__}")
        
        return self._blocks.get(block_id) # Accesso O(1)
    
    @lru_cache(maxsize=128)
    def get_blocks_by_criteria(self, side: Optional[str] = None, 
                              category: Optional[str] = None,
                              block_class: Optional[type] = None) -> List[BlockItem]:
        """
        Get blocks filtered by criteria. Cached for performance.
        
        Args:
            side: Filter by side (e.g., 'red', 'blue')
            category: Filter by category ('Military', 'Logistic', 'Civilian')
            block_class: Filter by block class type
        
        Returns:
            List of matching BlockItem objects
        """
        if not Utility.check_side(side):
            raise ValueError(f"Invalid side: {side!r}")

        result = []
        
        for block_item in self._blocks.values(): # Itera sui valori del dizionario
            block = block_item.block
            
            # Filter by side
            if side and hasattr(block, 'side') and block.side != side:
                continue
            
            # Filter by category - Uso diretto di BlockCategory Enum per robustezza
            if category:
                if category == BlockCategory.MILITARY.value and not isinstance(block, Military):
                    continue
                elif category == BlockCategory.LOGISTIC.value and not isinstance(block, (Production, Storage, Transport)):
                    continue
                elif category == BlockCategory.CIVILIAN.value and not isinstance(block, Urban):
                    continue
                # Se la categoria è un'altra stringa, si basa sull'attributo 'category' del blocco
                elif block.category != category:
                    continue
            
            # Filter by class
            if block_class and not isinstance(block, block_class):
                continue
            
            result.append(block_item)
        
        return result
    

    def get_sorted_priority_blocks(self, count: int, side: str, sort_by: str = "highest",
                                   category: Optional[str] = None) -> List[BlockItem]:
        """Get the sorted priority blocks matching criteria. if sort_by is 'lowest', returns the lowest priority blocks. if 'highest', returns the highest priority blocks."""
        if not Utility.check_side(side):
            raise ValueError(f"Invalid side: {side!r}")
        if not isinstance(count, int):
            raise TypeError(f"Count must be an integer, got {type(count).__name__}")
        
        if count < 1:
            raise ValueError("Count must be positive")
        
        if sort_by not in ["highest", "lowest"]:
            raise ValueError("sort_by must be 'highest' or 'lowest'")
        
        if sort_by == "lowest":
            sort_by = False
        else:
            sort_by = True

        # get_blocks_by_criteria è ora memorizzato nella cache
        blocks = self.get_blocks_by_criteria(side=side, category=category)
        blocks.sort(key=lambda x: x.priority, reverse = sort_by) # Ordina in base alla priorità
        
        return blocks[:count]
    
    
    # ROUTE MANAGEMENT
    def add_route(self, key: str, route: Route) -> None:
        """Add a route to the region."""
        if not isinstance(key, str):
            raise TypeError(f"Route key must be a string, got {type(key).__name__}")
        if not isinstance(route, Route):
            raise TypeError(f"Route must be a Route instance, got {type(route).__name__}")
        
        self._routes[key] = route
        logger.info(f"Route {key} added to region {self.name}")
        # Invalidate caches after adding a route: inutule invalidare selettivamente in quanto qualsiasi nuova route, block cambia priority e coseguentemente logistic e military center
        self._invalidate_caches()
    
    @lru_cache(maxsize=128)
    def get_route(self, block_id: str, target_block_id: Optional[str] = None) -> Optional[Route]:
        """
        Get route between blocks. Cached for performance.
        
        Args:
            block_id: ID of the source block.
            target_block_id: ID of the target block (optional). If None, finds any route involving block_id.
        Returns:
            The shortest matching Route object, or None if no route found.
        """
        if not isinstance(block_id, str):
            raise TypeError(f"Block ID must be a string, got {type(block_id).__name__}")
        
        if target_block_id is not None:
            if not isinstance(target_block_id, str):
                raise TypeError(f"Target block ID must be a string, got {type(target_block_id).__name__}")
            if target_block_id == block_id:
                raise ValueError("Target block ID must be different from source block ID")


        if target_block_id:
            if not isinstance(target_block_id, str):
                raise TypeError("Target block ID must be a string")
            if target_block_id == block_id:
                raise ValueError("Target block ID must be different from source block ID")
        
        matching_routes = []
        
        for key, route in self._routes.items():
            # Assumendo un formato chiave come "blockA_id,blockB_id" o "blockA_id-blockB_id"
            # Ho aggiornato la logica per essere più robusta a diversi delimitatori
            # o semplicemente verificare se entrambi gli ID sono presenti nella chiave.
            
            # Una soluzione più robusta potrebbe essere memorizzare le rotte con chiavi strutturate
            # ad esempio, una tupla (ID_blocco1, ID_blocco2)
            # Per ora, si assume che la chiave sia una stringa che include entrambi gli ID.
            
            # Per generalizzare la ricerca, si può creare un set di IDs dalla chiave
            key_ids = set(k.strip() for k in key.replace(',', ' ').replace('-', ' ').split())

            if block_id in key_ids:
                if target_block_id is None or target_block_id in key_ids:
                    matching_routes.append(route)
        
        if not matching_routes:
            return None
        
        # Return shortest route if multiple matches
        if len(matching_routes) == 1:
            return matching_routes[0]
        
        # Usare min con un'espressione lambda per la chiave
        return min(matching_routes, key=lambda r: r.length())
    
    # STRATEGIC CALCULATIONS

    @lru_cache(maxsize = 128)
    def calc_strategic_logistic_center(self, side: str) -> Optional[Point2D]:
        """
        Calculate the strategic logistic center for a side. Cached for performance.
        """
        if not Utility.check_side(side):
            raise ValueError(f"Invalid side: {side!r}")
        
        logistic_blocks = self.get_blocks_by_criteria(side = side, category = BlockCategory.LOGISTIC.value)
        
        if not logistic_blocks:
            return None
        
        total_priority = 0.0
        weighted_position_x = 0.0
        weighted_position_y = 0.0
        
        for block_item in logistic_blocks:
            block = block_item.block
            priority = block_item.priority
            if hasattr(block, 'position') and block.position is not None and priority > 0.0:
                weighted_position_x += block.position.x * priority
                weighted_position_y += block.position.y * priority
                total_priority += priority
        
        if total_priority == 0.0:
            return None
        
        return Point2D(weighted_position_x / total_priority, weighted_position_y / total_priority)

    """
    @lru_cache(maxsize = 128) # Aggiunta cache
    def calc_combat_power_center(self, side: str): 
        Calculation of baricenter point of the complessive military block's combat power 


        Args:
            side (str): side of blocks
            force (str): type of military force (air, ground, naval)

        Returns:
            Point2D: combat power baricenter
         
        if not Utility.check_side(side):
            raise ValueError(f"Invalid side: {side!r}")               
        blocks_quantity = {force: {task: 0 for task in ACTION_TASKS[force]} for force in MILITARY_FORCES}

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
        return r_CPP"""

    @lru_cache(maxsize=128)
    def calc_combat_power_center(self, side: str) -> Dict[str, Dict[str, Point2D]]:
        """Calculate combat power center for each force and task."""
        # verifica se  i risultati coincidono con quelli attesi con la logica del vecchio metodo(sopra)
        if not Utility.check_side(side):
            raise ValueError(f"Invalid side: {side!r}")               
        blocks_quantity = {force: {task: 0 for task in ACTION_TASKS[force]} for force in MILITARY_FORCES}
        military_blocks = self.get_blocks_by_criteria(side=side, category=BlockCategory.MILITARY.value)
        
        result = {force: {task: Point2D(0, 0) for task in ACTION_TASKS[force]} 
                for force in MILITARY_FORCES}
        counts = {force: {task: 0 for task in ACTION_TASKS[force]} 
                for force in MILITARY_FORCES}
        
        for block_item in military_blocks:
            block = block_item.block
            for force in MILITARY_FORCES:
                if ((block.is_Air_Base and force == "air") or 
                    (block.is_Ground_Base and force == "ground") or 
                    (block.is_Naval_Base and force == "naval")):
                    
                    for task in ACTION_TASKS[force]:
                        cp = block.combat_power(action=task, military_force=force)
                        if cp > 0:
                            result[force][task] += block.position * cp
                            counts[force][task] += cp
        
        # Normalize results
        for force in MILITARY_FORCES:
            for task in ACTION_TASKS[force]:
                if counts[force][task] > 0:
                    result[force][task] /= counts[force][task]
        
        return result
    
    @lru_cache(maxsize=1) # Caching per un solo risultato, probabilmente chiamato spesso
    def calc_total_warehouse(self, side: str) -> Payload:
        """Calculate total warehouse resources."""
        if not Utility.check_side(side):
            raise ValueError(f"Invalid side: {side!r}")
        
        blocks = self.get_blocks_by_criteria(side=side) # Filtra una volta    
        total = Payload()
        
        for block_item in blocks.values():
            if hasattr(block_item.block, 'resource_manager'):
                total += block_item.block.resource_manager.warehouse()
        
        return total
    
    @lru_cache(maxsize=1) # Caching per un solo risultato
    def calc_total_production(self, side: str) -> Payload:
        """Calculate total production resources."""

        if not Utility.check_side(side):
            raise ValueError(f"Invalid side: {side!r}")
        blocks = self.get_blocks_by_criteria(side=side) # Filtra una volta    
        total = Payload()
        
        for block_item in self._blocks.values():
            if isinstance(block_item.block, Production):
                total += block_item.block.resource_manager.actual_production()
        
        return total
    
    @lru_cache(maxsize=1) # Caching per un solo risultato
    def calc_production_values(self, side: str) -> Dict[str, float]:
        """Calculate production values by block type."""
        if not Utility.check_side(side):
            raise ValueError(f"Invalid side: {side!r}")

        blocks = self.get_blocks_by_criteria(side=side) # Filtra una volta    
        values = {"production": 0.0, "storage": 0.0, "transport": 0.0, "urban": 0.0, "military": 0.0, "total": 0.0}
        
        for block_item in blocks.values():
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
                elif isinstance(block, Military):
                    values["military"] += production_value # dovrebbero essere prevalentemente hc, hs e hb
                values["total"] += production_value # Aggiunto qui per chiarezza
        
        return values
    
    # PRIORITY UPDATES
    def update_logistic_priorities(self, side: str) -> bool:
        """Update priorities for logistic blocks based on production values."""

        if not Utility.check_side(side):
            raise ValueError(f"Invalid side: {side!r}")
        # Chiamata a metodo con cache
        production_values = self.calc_production_values(side = side) * MAX_VALUE # MAX_VALUE is a constant defined in Block.py, # Maximum value for block's strategic weight parameter
        
        if production_values["total"] == 0:
            logger.warning("No production value found, setting logistic priorities to 0")
            # Imposta priorità a 0 per blocchi logistici
            for block_item in self._blocks.values():
                if self._is_logistic_block(block_item.block):
                    block_item.priority = 0.0
            self._invalidate_caches()
            return False
        
        updated = False
        for block_item in self._blocks.values():
            block = block_item.block
            
            if self._is_logistic_block(block):
                block_production_value = block.resource_manager.production_value()
                
                if block_production_value > 0:
                    denominator = 0.0
                    if isinstance(block, Production):
                        denominator = production_values["production"]
                    elif isinstance(block, Storage):
                        denominator = production_values["storage"]
                    elif isinstance(block, Transport):
                        denominator = production_values["transport"]
                    elif isinstance(block, Urban): # Gli Urban blocks non sono logistic, ma la logica era presente
                        denominator = production_values["urban"]
                    
                    if denominator > 0:
                        absolute_priority = block_production_value * block.value
                        new_priority = absolute_priority / denominator
                        if block_item.priority != new_priority: # Aggiorna solo se diverso
                            block_item.priority = new_priority
                            updated = True
                            logger.debug(f"Updated priority for {block.name}: {block_item.priority}")
                    else: # Se il denominatore è 0 ma la produzione del blocco è > 0, imposta una priorità base o 0
                        block_item.priority = 0.0
                        updated = True
                        logger.debug(f"Set priority to 0 for {block.name} due to zero denominator.")
                        
                elif block_item.priority != 0.0: # Se la produzione del blocco è 0, imposta priorità a 0
                    block_item.priority = 0.0
                    updated = True
                    logger.debug(f"Set priority to 0 for {block.name} due to zero production value.")
        
        if updated:
            self._invalidate_caches()
        return updated
    
    def update_military_priorities(self, side: str) -> None:
        """Update priorities for military blocks."""
        if not Utility.check_side(side):
            raise ValueError(f"Invalid side: {side!r}")

        if not isinstance(side, str):
            raise TypeError("Side must be a string")
        
        friendly_blocks = self.get_blocks_by_criteria(side=side, category=BlockCategory.MILITARY.value)
        enemy_blocks = self.get_blocks_by_criteria(side=Utility.enemySide(side))
        
        for block_item in friendly_blocks:
            military_block = block_item.block
            
            if not isinstance(military_block, Military):
                continue
            
            # I calcoli di priorità sono ora memorizzati nella cache
            # Definisco le tuple prima di passarle come parametri perchè: ogni tuple(...) crea una nuova tupla → invalida la cache ogni volta. 
            # È importante riutilizzare una tupla generata una sola volta.
            enemy_blocks_tuple = tuple(enemy_blocks) 
            friendly_blocks_tuple = tuple(friendly_blocks)
            attack_priority = self._calc_attack_priority(military_block, enemy_blocks_tuple) # tuple per cache
            defense_priority = self._calc_defense_priority(military_block, friendly_blocks_tuple) # tuple per cache
            
            # Combined priority based on attack weight
            overall_priority = (attack_priority * self._attack_weight + 
                              defense_priority * (1 - self._attack_weight))
            
            if block_item.priority != overall_priority: # Aggiorna solo se diverso
                block_item.priority = overall_priority
                logger.debug(f"Updated military priority for {military_block.name}: {overall_priority}")
                self._invalidate_caches() # Invalidate solo se c'è stato un cambiamento effettivo
        
    # HELPER METHODS
    
    def _is_logistic_block(self, block: Block) -> bool:
        """Check if a block is a logistic block."""
        return isinstance(block, (Production, Storage, Transport))

    
    @lru_cache(maxsize=256) # Aggiunta cache per questo calcolo
    def _calc_attack_priority(self, military_block: Military, enemy_blocks: Tuple[BlockItem, ...]) -> float:
        """Calculate attack priority for a military block."""
        priority = 0.0
        # Assicurati che military_block.get_military_category() ritorni una chiave valida
        block_category = military_block.get_military_category() 
        if block_category not in self._weight_priority_target:
            logger.warning(f"Military block category '{block_category}' not found in weight_priority_target. Using default attack weight.")
            return 0.0

        for enemy_item in enemy_blocks:
            target = enemy_item.block            
            weight = self._select_weight(target_block=target, task="attack", block_category=block_category) # Seleziona il peso per il blocco target
            
            # priority summatory
            if military_block.is_Ground_Base() or military_block.is_Naval_Base():                    
                route = self.get_route(military_block.id, target.id) # get_route è ora memorizzato nella cache
                calc_result = self._calc_surface_priority(block=military_block, target_item=enemy_item, attack_route=route, weight=weight)
                if calc_result is not None: # Verifica se il risultato è valido
                    priority += calc_result
            elif military_block.is_Air_Base():                    
                calc_result = self._calc_air_priority(block=military_block, target_block=target, weight=weight)
                if calc_result is not None: # Verifica se il risultato è valido
                    priority += calc_result
        
        return priority
    

    @lru_cache(maxsize=256) # Aggiunta cache per questo calcolo
    def _calc_defense_priority(self, military_block: Military, friendly_blocks: Tuple[BlockItem, ...]) -> float:
        """Calculate defense priority for a military block."""
        priority = 0.0
        block_category = military_block.get_military_category()
        if block_category not in self._weight_priority_target:
            logger.warning(f"Military block category '{block_category}' not found in weight_priority_target. Using default defense weight.")
            return 0.0
        
        for friendly_item in friendly_blocks:
            friendly = friendly_item.block  
            if friendly.id == military_block.id: # Evita di calcolare la priorità con se stesso
                continue

            # weight selection
            weight = self._select_weight(target_block=friendly, task="defense", block_category=block_category) # Seleziona il peso per il blocco target
            
            if military_block.is_Ground_Base() or military_block.is_Naval_Base():
                route = self.get_route(military_block.id, friendly.id) # get_route è ora memorizzato nella cache
                calc_result = self._calc_surface_priority(block=military_block, target_item=friendly_item, attack_route=route, weight=weight)
                if calc_result is not None:
                    priority += calc_result
            elif military_block.is_Air_Base():                
                calc_result = self._calc_air_priority(block=military_block, target_block=friendly, weight=weight)
                if calc_result is not None:
                    priority += calc_result
        
        return priority

    
    # non necessario utilizzare la cache in quanto sono già stati decorati i metodi superiori _calc_attack_priority e _calc_defense_priority
    def _select_weight(self, target_block: Block, task: str, block_category: str) -> float:
        """        Select the weight for a block based on its category."""
        if task not in self._weight_priority_target[block_category]:
            logger.warning(f"Task '{task}' not found in weight_priority_target for block category '{block_category}'. Using default weight of 0.0.")
            return 0.0
        
        #setup target block category to select weight index
        target_category = ""
        if target_block.is_military():
            target_category = target_block.get_military_category()
        elif target_block.is_logistic():
            target_category = BlockCategory.LOGISTIC.value
        elif target_block.is_civilian():
            target_category = BlockCategory.CIVILIAN.value
        else:
            logger.warning(f"The block {target_block.name!r} is not a military base, logistical or civil block; block weight will be set with Civilian value.")
            target_category = BlockCategory.CIVILIAN.value
        
        # weight selection
        return self._weight_priority_target[block_category][task].get(target_category, 0.0) # Uso .get per default 0.0
        


    # non necessario utilizzare la cache in quanto sono già stati decorati i metodi superiori _calc_attack_priority e _calc_defense_priority
    def _calculate_priority(
    self,
    block: Military,
    target_block: Block,
    weight: float,
    time_to_intercept: Optional[float],
    range_ratio: float,
    target_priority: Optional[float] = None,
    force_type: Optional[str] = None
) -> float:
        """Calculate generic priority for a military block towards a target."""
        combat_power = block.combat_power(military_force=force_type)
        if not combat_power or combat_power <= 0:
            return 0.0

        time_to_intercept = time_to_intercept or float('inf')
        if time_to_intercept < 1:
            time_to_intercept = 1.0

        target_value = target_block.value or 1.0
        
        if target_block.is_military():
            target_cp = target_block.combat_power()
            #combat_power_ratio = max(0.1, min(target_cp / combat_power, 10.0))
            combat_power_ratio = clip(target_cp / combat_power, 0.1, 10.0)
            return (target_value * combat_power_ratio * range_ratio * weight) / time_to_intercept
        
        elif target_block.is_logistic():
            target_priority = target_priority or 0.0
            return (target_priority * range_ratio * weight) / time_to_intercept
        
        elif target_block.is_civilian():
            return (target_value * range_ratio * weight) / time_to_intercept
        
        return 0.0



    # non necessario utilizzare la cache in quanto sono già stati decorati i metodi superiori _calc_attack_priority e _calc_defense_priority
    def _calc_surface_priority(self, block: Military, target_item: BlockItem,
                            attack_route: Optional[Route], weight: float) -> float:
        
        """
        Calculates the priority of a military block (ground or naval) by evaluating its combat power, 
        the distance from the target, the combat power of the target or the priority assigned 
        in the case of logistical targets.

        Args:                
            block (Military): block to calculates priority
            target_item (BlockItem): target BlockItem of the block
            attack_route (Optional[Route]): intercept route to target_block
            weight (float): assigned weight for calculates priority

        Returns:
            priority (float): priority value of the block, returns 0.0 if not applicable
        """
        target_block = target_item.block

        # Calcola tempo di intercetto
        if attack_route:
            tti = block.time2attack(route=attack_route)
        elif target_block.position and block.position:
            tti = block.time2attack(target=target_block.position)
        else:
            return 0.0

        # Calcola ratio di range
        if target_block.position:
            range_info = block.artillery_in_range(target_block.position)
        else:
            range_info = {"target_within_med_range": False, "med_range_ratio": 1.0}

        if not range_info["target_within_med_range"] and tti == float('inf'):
            return 0.0

        range_ratio = range_info["med_range_ratio"] if range_info["target_within_med_range"] else 1.0

        return self._calculate_priority(
            block=block,
            target_block=target_block,
            weight=weight,
            time_to_intercept=tti,
            range_ratio=range_ratio,
            target_priority=target_item.priority
        )


    # non necessario utilizzare la cache in quanto sono già stati decorati i metodi superiori _calc_attack_priority e _calc_defense_priority
    def _calc_air_priority(self, block: Military, target_block: Block, weight: float) -> float:

        """Calculates the priority of an air military block by evaluating its combat power, 
        the distance from the target, the combat power of the target or the priority assigned 
        in the case of logistical targets.

        Args:                
            block (Military): block to calculates priority
            target_block (Block): target of the block                
            weight (float): assigned weight for calculates priority

        Returns:
            priority (float): priority value of the block, returns 0.0 if not applicable"""
        
        if not block.position or not target_block.position:
            return 0.0

        tti = block.time2attack(target=target_block.position)
        return self._calculate_priority(
            block=block,
            target_block=target_block,
            weight=weight,
            time_to_intercept=tti,
            range_ratio=1.0,
            target_priority=self.get_block_by_id(target_block.id).priority if self.get_block_by_id(target_block.id) else 0.0,
            force_type="air"
        )



    """ superata
    def _calc_surface_priority(self, block: Military, target_item: BlockItem, attack_route: Optional[Route], weight: float) -> float:   
        
        Calculates the priority of a military block (ground or naval) by evaluating its combat power, 
        the distance from the target, the combat power of the target or the priority assigned 
        in the case of logistical targets.

        Args:                
            block (Military): block to calculates priority
            target_item (BlockItem): target BlockItem of the block
            attack_route (Optional[Route]): intercept route to target_block
            weight (float): assigned weight for calculates priority

        Returns:
            priority (float): priority value of the block, returns 0.0 if not applicable
            
        
        combat_power = block.combat_power()
        target_block = target_item.block

        if not combat_power or combat_power <= 0: # Combat power deve essere positivo
            return 0.0

        arty_combat_range_info = {"target_within_med_range": False, "med_range_ratio": 1.0}
        if block.is_Ground_Base() or block.is_Naval_Base():            
            if target_block.position: # Assicurati che target_block.position esista
                arty_combat_range_info = block.artillery_in_range(target_block.position)                        
        
        time_to_intercept = float('inf')
        if attack_route: # Usa la route se disponibile
            time_to_intercept = block.time2attack(route=attack_route)
        elif target_block.position and block.position: # Altrimenti usa la distanza tra le posizioni
            time_to_intercept = block.time2attack(target=target_block.position)

        if time_to_intercept < 1: # Second
                time_to_intercept = 1.0 # Evita divisione per zero e valori molto piccoli
        
        if not arty_combat_range_info["target_within_med_range"] and time_to_intercept == float('inf'):
            return 0.0 # No route to intercept and target is out of range 
        
        target_default_strategic_value = target_block.value if target_block.value else 1.0

        range_ratio = arty_combat_range_info["med_range_ratio"] if arty_combat_range_info["target_within_med_range"] else 1.0
        
        priority = 0.0
        if target_block.is_military():
            target_combat_power = target_block.combat_power()                            

            if combat_power > 0.0:
                combat_power_ratio = target_combat_power / combat_power if combat_power > 0 else 0.0
                combat_power_ratio = max(0.1, min(combat_power_ratio, 10.0)) # Clamping values
                                
            priority = (target_default_strategic_value * combat_power_ratio * range_ratio * weight) / time_to_intercept
            
        elif target_block.is_logistic():                
            # Assicurati che la priorità logistica sia aggiornata per il target.
            # Qui si usa la priorità di BlockItem.
            target_priority = target_item.priority
            
            # Se la priorità logistica non è stata aggiornata, potrebbe essere necessario farlo.
            # Tuttavia, il metodo update_logistic_priorities è chiamato esternamente.
            # Per evitare ricorsioni, assumiamo che le priorità siano aggiornate.
            # In un ambiente reale, potresti voler gestire questo caso esplicitamente
            # es: if target_priority is None or target_priority == 0.0: self.update_logistic_priorities()
            
            priority = (target_priority * range_ratio * weight) / time_to_intercept                
            
        elif target_block.is_civilian():
            # I blocchi civili potrebbero avere una priorità calcolata diversamente o un valore fisso.
            # Per ora, usiamo il loro valore strategico di default.
            priority = (target_default_strategic_value * range_ratio * weight) / time_to_intercept

        return priority
    """
        
    """ superata
    def _calc_air_priority(self, block: Military, target_block: Block, weight: float) -> float:     
        
        Calculates the priority of an air military block by evaluating its combat power, 
        the distance from the target, the combat power of the target or the priority assigned 
        in the case of logistical targets.

        Args:                
            block (Military): block to calculates priority
            target_block (Block): target of the block                
            weight (float): assigned weight for calculates priority

        Returns:
            priority (float): priority value of the block, returns 0.0 if not applicable
                                    
        combat_power = block.combat_power()
        
        if not combat_power or combat_power <= 0: # Combat power deve essere positivo
            return 0.0
        
        time_to_intercept = float('inf')
        if target_block.position and block.position: # Assicurati che le posizioni esistano
            time_to_intercept = block.time2attack(target=target_block.position)   

        if time_to_intercept < 1: # Second
            time_to_intercept = 1.0 # Evita divisione per zero e valori molto piccoli
        
        target_default_strategic_value = target_block.value if target_block.value else 1.0
        
        priority = 0.0
        if target_block.is_military():
            target_combat_power = target_block.combat_power(military_force="ground") # Forse "ground" è specifico, considera un parametro dinamico
            
            if combat_power > 0.0:
                combat_power_ratio = target_combat_power / combat_power if combat_power > 0 else 0.0
                combat_power_ratio = max(0.1, min(combat_power_ratio, 10.0)) # Clamping values
                                
            priority = (target_default_strategic_value * combat_power_ratio * weight) / time_to_intercept
        
        elif target_block.is_logistic():                
            # Recupera BlockItem per accedere alla priorità logistica
            target_item = self.get_block_by_id(target_block.id)
            if target_item:
                target_priority = target_item.priority
            else:
                target_priority = 0.0 # Se il blocco non è nella regione (dovrebbe esserlo)
            
            priority = (target_priority * weight) / time_to_intercept                
            
        elif target_block.is_civilian():
            priority = (target_default_strategic_value * weight) / time_to_intercept
            
        return priority                    
    
        """
    
    # CACHING METHODS (nota: la granularizzazione delle invalidazioni non serve in qaunto qualsisasi nmodifica di blocks o route, redo o blue, comporta la variazione di tutte le priority e conseguentemente di tutti i stategical center)
    def _invalidate_caches(self, cache_type: Optional[str] = None) -> None:
        """Invalidate specific caches based on type."""
        if cache_type is None or cache_type == "blocks":
            self.get_blocks_by_criteria.cache_clear()
        if cache_type is None or cache_type == "routes":
            self.get_route.cache_clear()
        if cache_type is None or cache_type == "strategic centers":
            self.calc_strategic_logistic_center.cache_clear()
            self.calc_combat_power_center.cache_clear()
        if cache_type is None or cache_type == "logistic resources":
            self.calc_total_warehouse.cache_clear()
            self.calc_total_production.cache_clear()
            self.calc_production_values.cache_clear()
        if cache_type is None or cache_type == "priority":
            self._calc_attack_priority.cache_clear()
            self._calc_defense_priority.cache_clear()
        
        logger.debug(f"Caches for Region {self.name} invalidated ({cache_type or 'all'}).")

    # VALIDATION METHODS (mantenuti quasi invariati, con piccole migliorie)
    def _validate_init_params(self, name: str, limes: Optional[List[Limes]], 
                            description: Optional[str], blocks: Optional[List[BlockItem]],
                            routes: Optional[Dict[str, Route]]) -> None:
        """Validate initialization parameters."""
        if not isinstance(name, str) or not name:
            raise ValueError("Name must be a non-empty string")
        
        if limes is not None and not isinstance(limes, list):
            raise TypeError("Limes must be a list")
        # Puoi aggiungere validazioni per gli elementi della lista limes se Limes ha un tipo specifico
        
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
    
    # Questo metodo helper è stato integrato direttamente nei setter dove era usato.
    # def _validate_string_param(self, param_name: str, value: str) -> None:
    #     """Validate string parameter."""
    #     if not isinstance(value, str):
    #         raise TypeError(f"{param_name} must be a string")
    
    def _validate_weight_priority_target(self, value: Dict) -> None:
        """Validate weight priority target structure."""
        if not isinstance(value, dict):
            raise TypeError("Weight priority target must be a dictionary")
        
        # Add more specific validation based on expected structure
        for category, weights in value.items():
            if not isinstance(weights, dict):
                raise TypeError(f"Weights for {category} must be a dictionary")
            
            if 'attack' not in weights or 'defense' not in weights:
                raise ValueError(f"Category {category} must have 'attack' and 'defense' keys")
            
            # Ulteriore validazione dei sottodizionari attack/defense
            for action_type in ['attack', 'defense']:
                if not isinstance(weights[action_type], dict):
                    raise TypeError(f"'{action_type}' weights for {category} must be a dictionary")
                for target_cat, weight_val in weights[action_type].items():
                    if not isinstance(target_cat, str):
                        raise TypeError(f"Target category '{target_cat}' in {action_type} for {category} must be a string.")
                    if not isinstance(weight_val, (int, float)) or not (0 <= weight_val <= 1):
                        raise ValueError(f"Weight value '{weight_val}' for target")
                    

    def __repr__(self) -> str:
        """String representation of the Region."""
        return (f"Region(name='{self._name}', description='{self._description}', "
                f"blocks={len(self._blocks)}, routes={len(self._routes)})")
    
    def __str__(self) -> str:
        """Readable string representation."""
        return f"Region '{self.name}' with {len(self._blocks)} blocks"