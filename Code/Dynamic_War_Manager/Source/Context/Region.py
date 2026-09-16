from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union, Tuple
from dataclasses import dataclass
from functools import lru_cache
from enum import Enum


# Assuming these imports exist in your codebase
from Code.Dynamic_War_Manager.Source.Context import Context
from Code.Dynamic_War_Manager.Source.Context import Doctrine
from Code.Dynamic_War_Manager.Source.Logic import Tactical_Analysis
from Code.Dynamic_War_Manager.Source.Utility import Utility
from Code.Dynamic_War_Manager.Source.Block.Block import Block, MAX_VALUE
from Code.Dynamic_War_Manager.Source.Block.Military import Military
from Code.Dynamic_War_Manager.Source.Block.Production import Production
from Code.Dynamic_War_Manager.Source.Block.Storage import Storage
from Code.Dynamic_War_Manager.Source.Block.Transport import Transport
from Code.Dynamic_War_Manager.Source.Block.Urban import Urban
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import Aircraft_Data
from Code.Dynamic_War_Manager.Source.DataType.Limes import Limes
from Code.Dynamic_War_Manager.Source.DataType.Route import Route
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from sympy import Point2D
from numpy import clip



# CONSTANTS
DEFAULT_ATTACK_WEIGHT = 0.5
"""
MILITARY_FORCES = ["ground", "air", "sea"]
ACTION_TASKS = {
    "ground": Context.GROUND_ACTION,
    "air": Context.AIR_TASK,
    "sea": Context.SEA_TASK
}
"""

# Logger setup
    # CRITICAL 	50
    # ERROR 	40
    # WARNING 	30
    # INFO 	20
    # DEBUG 	10
    # NOTSET 	0
logger = Logger(module_name=__name__, set_consolle_log_level = 10, set_file_log_level=30, class_name="Region").logger


class BlockCategory(Enum):
    MILITARY = "Military"
    LOGISTIC = "Logistic"
    CIVILIAN = "Civilian"


# Shape shared by both "target classification" producers in Logic.Tactical_Analysis:
# get_target_report (fog-of-war, built from a recon report) and target_profile_from_block
# (ground truth, built directly from a block's real assets). {classification: {'big'|'med'|'small': count}}.
TargetProfile = Dict[str, Dict[str, int]]

# Bound per Region._target_affinity: fattore moltiplicativo, non sostitutivo, applicato al ramo
# attacco di _calculate_priority (v. quel metodo) — resta vicino a 1.0 (neutro) invece di poter
# dominare il resto del calcolo di priorità.
_AFFINITY_MIN, _AFFINITY_MAX = 0.25, 2.0


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
        self._weight_priority_target = Doctrine.DEFAULT_WEIGHT_PRIORITY_TARGET.copy()   # Copia per evitare modifiche involontarie
        
        # Inizializza i blocchi con associazione corretta. 
        # Utilizziamo un dizionario per un accesso O(1) per ID.
        self._blocks: Dict[str, BlockItem] = {}
        if blocks:
            for block_item in blocks:
                self._add_block_item(block_item)
        
        # Initialize routes
        self._routes: Dict[str, Route] = routes or {}

        # Snapshot di combat power stimata via ricognizione (fog-of-war), costruito una volta per
        # sweep da update_military_priorities(use_recon=True) e consultato da _calculate_priority.
        # Valido SOLO dentro lo sweep che lo ha costruito (v. _build_recon_cp_snapshot); None quando
        # use_recon=False o fuori da uno sweep.
        self._recon_cp_snapshot: Optional[Dict[str, float]] = None

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
        Doctrine.validate_weight_priority_target(value)
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
                              block_class: Optional[type] = None,
                              mil_category: Optional[str] = None) -> List[BlockItem]:
        """
        Get blocks filtered by criteria. Cached for performance.

        Args:
            side: Filter by side (e.g., 'red', 'blue')
            category: Filter by category ('Military', 'Logistic', 'Civilian')
            block_class: Filter by block class type
            mil_category: Filter by Military.mil_category (e.g. 'Regiment', 'Airbase')

        Returns:
            List of matching BlockItem objects
        """
        if mil_category is not None:
            valid_mil_categories = {c for tup in Context.MILITARY_CATEGORY.values() for c in tup}
            if mil_category not in valid_mil_categories:
                raise ValueError(
                    f"Invalid mil_category: {mil_category}. Must be one of: {', '.join(valid_mil_categories)}"
                )

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

            # Filter by military category
            if mil_category and not (isinstance(block, Military) and block.mil_category == mil_category):
                continue

            result.append(block_item)

        return result


    def get_sorted_priority_blocks(self, count: int, side: str, sort_by: str = "highest",
                                   category: Optional[str] = None,
                                   mil_category: Optional[str] = None) -> List[BlockItem]:
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
        blocks = self.get_blocks_by_criteria(side=side, category=category, mil_category=mil_category)
        blocks.sort(key=lambda x: x.priority, reverse = sort_by) # Ordina in base alla priorità

        return blocks[:count]

    def get_normalized_priority_blocks(self, count: int, side: str, sort_by: str = "highest",
                                   category: Optional[str] = None,
                                   mil_category: Optional[str] = None) -> List[BlockItem]:

        blocks = self.get_sorted_priority_blocks(count=len(self.blocks), side=side, sort_by=sort_by,
                                                   category=category, mil_category=mil_category)
        normalized_blocks = []

        # Un solo blocco nel gruppo: nessun range su cui normalizzare, la priorità resta quella del blocco.
        if len(blocks) == 1:
            return [BlockItem(priority=blocks[0].priority, block=blocks[0].block)][:count]

        min = blocks[-1].priority
        delta = blocks[0].priority - min

        if sort_by == 'lowest':
            delta = -delta
            min = blocks[0].priority

        for blockItem in blocks:
            normalized_blocks.append( BlockItem(priority = (blockItem.priority - min)/delta, block = blockItem.block) )

        return normalized_blocks[:count]

    def get_priority_lists_by_mil_category(self, side: str, sort_by: str = "highest") -> Dict[str, List[BlockItem]]:
        """
        Split the priority list for a side into one sorted list per Military.mil_category
        actually present on that side. Categories with no blocks are omitted.
        """
        if not Utility.check_side(side):
            raise ValueError(f"Invalid side: {side!r}")

        military_blocks = self.get_blocks_by_criteria(side=side, category=BlockCategory.MILITARY.value)
        present = {block_item.block.mil_category for block_item in military_blocks}

        ordered_categories = [c for tup in Context.MILITARY_CATEGORY.values() for c in tup]

        result: Dict[str, List[BlockItem]] = {}
        for cat in ordered_categories:
            if cat not in present:
                continue
            result[cat] = self.get_sorted_priority_blocks(count=len(self.blocks), side=side,
                                                            sort_by=sort_by, mil_category=cat)

        return result

    
    # ************************************  API *************************************
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
        
        return matching_routes
        
    def get_shortest_route(self, block_id: str, target_block_id: str) -> Optional[Route]:
        """Get the shortest route between two blocks."""
        matching_routes = self.get_route(block_id, target_block_id)

        if not matching_routes:
            return None
        if len(matching_routes) == 1:
            return matching_routes[0]
        return min(matching_routes, key=lambda r: r.length())
    
    def get_safest_route(self, block_id: str, target_block_id: str) -> Optional[Route]:
        """Get the route with lesser danger level between two blocks."""
        matching_routes = self.get_route(block_id, target_block_id)     

        if not matching_routes:
            return None
        
        # Usare min con un'espressione lambda per la chiave
        return min(matching_routes, key=lambda r: r.max_danger_level())

    def get_shortest_and_safest_route(self, block_id: str, target_block_id: str) -> Optional[Route]:
        """Get the shortest route with lesser danger level between two blocks."""
        matching_routes = self.get_route(block_id, target_block_id)     

        if not matching_routes:
            return None
        
        # Usare min con un'espressione lambda per la chiave
        return min(matching_routes, key=lambda r: (r.min_danger_level(), r.length()))
    
    # STRATEGIC CALCULATIONS

    @lru_cache(maxsize = 3) # side ha solo tre valori possibili, quindi Caching maxsize=3 è sufficiente per memorizzare i risultati per entrambi i lati
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

    @lru_cache(maxsize=3) # side ha solo tre valori possibili, quindi Caching maxsize=3 è sufficiente per memorizzare i risultati per entrambi i lati
    def calc_combat_power_center(self, side: str) -> Dict[str, Dict[str, Point2D]]:
        """Calculate combat power center for each force and task."""
        # verifica se  i risultati coincidono con quelli attesi con la logica del vecchio metodo(sopra)
        if not Utility.check_side(side):
            raise ValueError(f"Invalid side: {side!r}")               
        military_blocks = self.get_blocks_by_criteria(side=side, category=BlockCategory.MILITARY.value)
        
        result = {force: {task: Point2D(0, 0) for task in Context.ACTION_TASKS[force]} 
                for force in Context.MILITARY_FORCES}
        counts = {force: {task: 0 for task in Context.ACTION_TASKS[force]} 
                for force in Context.MILITARY_FORCES}
        
        for block_item in military_blocks:
            block = block_item.block
            for force in Context.MILITARY_FORCES:
                if ((block.is_Air_Base() and force == "air") or
                    (block.is_Ground_Base() and force == "ground") or
                    (block.is_Naval_Base() and force == "sea")):

                    for task in Context.ACTION_TASKS[force]:
                        cp = block.combat_power(force=force, action=task)
                        if cp > 0 and block.position is not None:
                            result[force][task] += block.position * cp
                            counts[force][task] += cp
        
        # Normalize results
        for force in Context.MILITARY_FORCES:
            for task in Context.ACTION_TASKS[force]:
                if counts[force][task] > 0:
                    result[force][task] /= counts[force][task]
        
        return result
    
    @lru_cache(maxsize=3) # Caching per un solo risultato, probabilmente chiamato spesso
    def calc_total_warehouse(self, side: str) -> Payload:
        """Calculate total warehouse resources."""
        if not Utility.check_side(side):
            raise ValueError(f"Invalid side: {side!r}")
        
        total = Payload()
        blocks = self.get_blocks_by_criteria(side=side)
        
        for block_item in blocks:
            if hasattr(block_item.block, 'resource_manager'):
                rm = block_item.block.resource_manager
                if rm is not None and hasattr(rm, 'warehouse'):
                    warehouse = rm.warehouse
                    if isinstance(warehouse, Payload):
                        total += warehouse
                    else:
                        print(f"Warning: Invalid warehouse type in {block_item.block.id} - {type(warehouse)}")
        
        return total
    
    @lru_cache(maxsize=3) # Caching per un solo risultato
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
    
    @lru_cache(maxsize=3) # Caching per un solo risultato
    def calc_production_values(self, side: str) -> Dict[str, float]:
        """Calculate production values by block type."""
        if not Utility.check_side(side):
            raise ValueError(f"Invalid side: {side!r}")

        blocks = self.get_blocks_by_criteria(side=side) # Filtra una volta    
        values = {"production": 0.0, "storage": 0.0, "transport": 0.0, "urban": 0.0, "military": 0.0, "total": 0.0}
        
        for block_item in blocks:
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
        production_values = self.calc_production_values(side = side)
        
        for k, v in production_values.items():
            production_values[k] = v * MAX_VALUE # MAX_VALUE is a constant defined in Block.py, # Maximum value for block's strategic weight parameter


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
    
    def update_military_priorities(self, side: str, use_recon: bool = False) -> None:
        """Update priorities for military blocks.

        use_recon: se True, la combat power dei bersagli NEMICI nel ramo attacco viene stimata via
        ricognizione (fog-of-war, v. Combat_Power_Estimation) invece che letta a piena visibilità;
        il blocco proprio e i bersagli del ramo difesa (alleati) restano SEMPRE ground-truth. Lo
        sweep di ricognizione (get_recon_reports) viene eseguito una sola volta per questa chiamata,
        mai per singola coppia blocco/bersaglio (v. _build_recon_cp_snapshot).
        """
        if not Utility.check_side(side):
            raise ValueError(f"Invalid side: {side!r}")

        if side == 'Neutral':
            # Guard: 'Neutral' non partecipa al conflitto, non è mai un osservatore di prima classe
            # nel ciclo di priorità. Senza questo guard, enemySide('Neutral') degenera in 'Neutral'
            # (auto-osservazione) e un blocco Neutral calcolerebbe una "priorità di attacco" verso
            # se stesso -- bug preesistente indipendente da questa fase, chiuso qui.
            logger.warning(f"update_military_priorities: side='Neutral' non è un lato belligerante, no-op (region {self.name}).")
            return

        friendly_blocks = self.get_blocks_by_criteria(side=side, category=BlockCategory.MILITARY.value)
        enemy_blocks = self.get_blocks_by_criteria(side=Utility.enemySide(side))

        try:
            if use_recon:
                recon_reports = self.get_recon_reports(Utility.enemySide(side))
                self._recon_cp_snapshot = Tactical_Analysis.build_recon_cp_snapshot(recon_reports)
                self._invalidate_caches("priority")

            for block_item in friendly_blocks:
                military_block = block_item.block

                if not isinstance(military_block, Military):
                    continue

                # I calcoli di priorità sono ora memorizzati nella cache
                # Definisco le tuple prima di passarle come parametri perchè: ogni tuple(...) crea una nuova tupla → invalida la cache ogni volta.
                # È importante riutilizzare una tupla generata una sola volta.
                enemy_blocks_tuple = self._get_tuple_hashable_block_item(block_items=enemy_blocks)
                friendly_blocks_tuple = self._get_tuple_hashable_block_item(block_items=friendly_blocks)
                attack_priority = self._calc_attack_priority(military_block, enemy_blocks_tuple, use_recon) # tuple per cache
                defense_priority = self._calc_defense_priority(military_block, friendly_blocks_tuple) # tuple per cache

                # Combined priority based on attack weight
                # Il significato della formula è il seguente: se la priorità di difendere un target nemico è più alta rispetto quella di attacco la priorità del blocco è quella di difendere invece di atttaccare
                overall_priority = (attack_priority * self._attack_weight +
                                  defense_priority * (1 - self._attack_weight))

                if block_item.priority != overall_priority: # Aggiorna solo se diverso
                    block_item.priority = overall_priority
                    logger.debug(f"Updated military priority for {military_block.name}: {overall_priority}")
                    self._invalidate_caches() # Invalidate solo se c'è stato un cambiamento effettivo
        finally:
            if use_recon:
                # Lo snapshot è valido solo dentro questo sweep (v. attributo in __init__).
                self._recon_cp_snapshot = None
                self._invalidate_caches("priority")

    def run_resource_management_cycle(self, side: str) -> None:
        """Run a resource management cycle for the region."""
        if not Utility.check_side(side):
            raise ValueError(f"Invalid side: {side!r}")
        
        # Calcola le priorità logistiche prima di eseguire il ciclo di produzione
        if self.update_logistic_priorities(side=side):
            logger.info(f"Logistic priorities updated for side {side} in region {self.name}")
        
        # Aggiorna le priorità militari dopo aver aggiornato quelle logistiche
        self.update_military_priorities(side=side)
        logger.info(f"Military priorities updated for side {side} in region {self.name}")

        for block_item in self._blocks.values():
            block = block_item.block
            
            if hasattr(block, 'resource_manager'):
                # Esegui il ciclo di produzione per ogni blocco con un resource manager
                result = block.resource_manager.run_resource_management_cycle()
                self._invalidate_caches()
                logger.debug(f"Resource management cycle run for {block.name} in region {self.name}. Result cyce: {result!r}")    



    # DEVI IMPLEMENTARE IN ACTUAL_CONTEXT LA REGISTRAZIONE DELLE MISSIONI DI SUCCESSO PER OGNI BLOCCO, IN MODO DA POTER CALCOLARE LA MORALE 
    # IN BASE AL NUMERO DI MISSIONI DI SUCCESSO E MISSIONI TOTALI.
    # Considera che nel blocco il morale viene calcolato in base al morale degli asset. 
    # Il morale degli asset viene calcolato in base al numero di missioni di successo e missioni totali 
    # per quel blocco (definiti nel componente State associato all'asset), quindi è importante che questa logica sia implementata correttamente 
    # nei blocchi militari, e che i dati sulle missioni siano registrati in Actual_Context in modo accurato.
    

    def get_block_morale(self, block_id: str) -> Optional[float]:
        """Calculate the morale of a specific block."""
        block_item = self.get_block_by_id(block_id)
        
        if not block_item:
            logger.warning(f"Block with ID {block_id} not found in region {self.name}")
            return None
        
        block = block_item.block
        if hasattr(block, 'morale'):
            morale = block.morale()
            if isinstance(morale, (int, float)):
                return morale
            else:
                logger.warning(f"Invalid morale value for block {block.name}: {morale!r}")
                return None
        else:
            logger.warning(f"Block {block.name} does not have a morale method")
            return None

    def _get_region_average_metric(self, side: str, category: str, method_name: str) -> float:
        """Average a block-level metric across all blocks of a given category and side."""
        if not Utility.check_side(side):
            raise ValueError(f"Invalid side: {side!r}")

        blocks = self.get_blocks_by_criteria(side=side, category=category)
        if not blocks:
            return 0.0

        total = 0.0
        count = 0
        for block_item in blocks:
            method = getattr(block_item.block, method_name, None)
            if callable(method):
                value = method()
                if isinstance(value, (int, float)):
                    total += value
                    count += 1

        return total / count if count > 0 else 0.0

    def get_region_morale(self, side: str) -> float:
        """Calculate the region's morale for a side."""
        return self._get_region_average_metric(side, BlockCategory.MILITARY.value, 'morale')

    def get_region_recon_efficiency(self, side: str) -> float:
        """Calculate the region's reconnaissance efficiency for a side."""
        return self._get_region_average_metric(side, BlockCategory.MILITARY.value, 'get_recon_efficiency')

    def get_region_resource_efficiency(self, side: str) -> float:
        """Calculate the region's resource efficiency for a side."""
        return self._get_region_average_metric(side, BlockCategory.LOGISTIC.value, 'resource_efficiency')

    def get_c2_efficiency(self, side: str) -> float:
        """Calculate the region's command and control efficiency for a side."""
        return self._get_region_average_metric(side, BlockCategory.MILITARY.value, 'get_c2_efficiency')

    def get_recon_reports(self, side: str) -> List[Dict]:
        """Get reconnaissance reports for all blocks of a side."""
        if not Utility.check_side(side):
            raise ValueError(f"Invalid side: {side!r}")

        military_blocks = self.get_blocks_by_criteria(side=side, category=BlockCategory.MILITARY.value)
        # C2 usato per la ricognizione è quello dell'osservatore (il lato nemico rispetto a `side`),
        # non quello del lato osservato — per side=='Neutral' degenera in auto-osservazione (vedi Q7).
        region_c2_recon_efficiency = self.get_c2_efficiency(side=Utility.enemySide(side))
        recon_reports = []

        for block_item in military_blocks:
            block = block_item.block
            report = block.get_recognition_report(region_c2_recon_efficiency)
            if isinstance(report, dict):
                recon_reports.append(report)
            else:
                logger.warning(f"Invalid recon report for block {block.name}: {report!r}")

        return recon_reports

    def get_meteorological_reports(self, side: str) -> List[Dict]:
        """Get meteorological reports for all blocks of a side."""
        if not Utility.check_side(side):
            raise ValueError(f"Invalid side: {side!r}")

        region_c2_recon_efficiency = self.get_c2_efficiency(side=side)
        meteorological_reports = []

        # implementare il sistema di elaborazione del meteo (vedi quanto fatto da MBot)
        pass

        return meteorological_reports

    # ************************************  END API *************************************


    # Valutare una funzione che costruice la matrice dei collegamenti tra blocchi, in modo da poterla utilizzare nei calcoli di priorità militare, in modo da evitare di dover iterare su tutte le rotte ogni volta.

    # HELPER METHODS
    def _get_tuple_hashable_block_item(self, block_items: List[BlockItem]):
        # crea una tupla di coppie (priority, block) evitando di utilizzare la classe BlockItem non hashable in quanto dataclass
        tuple_priority_and_block = ()
        for block_item in block_items:
            item = (block_item.priority, block_item.block)
            tuple_priority_and_block += (item,)

        return tuple_priority_and_block

    def _is_logistic_block(self, block: Block) -> bool:
        """Check if a block is a logistic block."""
        return isinstance(block, (Production, Storage, Transport, Urban))
    
    
    @lru_cache(maxsize=256) # Aggiunta cache per questo calcolo
    def _calc_attack_priority(self, military_block: Military, enemy_blocks: Tuple[(float, Block), ...], use_recon: bool = False) -> float:

        """Calculates the attack priority of a military block (air, ground or sea) by evaluating its combat power,
        the distance from the target, the combat power of the target or the priority assigned
        in the case of logistical targets."""

        priority = 0.0
        # Assicurati che military_block.get_military_category() ritorni una chiave valida
        block_category = military_block.get_military_category()
        if block_category not in self._weight_priority_target:
            logger.warning(f"Military block category '{block_category}' not found in weight_priority_target. Using default attack weight.")
            return 0.0

        for enemy_item in enemy_blocks:
            target = enemy_item[1]
            weight = self._select_weight(target_block=target, task="attack", block_category=block_category) # Seleziona il peso per il blocco target

            # priority summatory
            if military_block.is_Ground_Base() or military_block.is_Naval_Base():
                route = self.get_shortest_route(military_block.id, target.id)
                calc_result = self._calc_surface_priority(block=military_block, target_item=enemy_item, attack_route=route, weight=weight, use_recon=use_recon)
                if calc_result is not None: # Verifica se il risultato è valido
                    priority += calc_result
            elif military_block.is_Air_Base():
                calc_result = self._calc_air_priority(block=military_block, target_block=target, weight=weight, use_recon=use_recon)
                if calc_result is not None: # Verifica se il risultato è valido
                    priority += calc_result

        return priority
    
    
    @lru_cache(maxsize=256) # Aggiunta cache per questo calcolo
    def _calc_defense_priority(self, military_block: Military, friendly_blocks: Tuple[(float, Block), ...]) -> float:
        
        """Calculates the defense priority of a military block (air, ground or sea) by evaluating its combat power, 
        the distance from the target, the combat power of the target or the priority assigned 
        in the case of logistical targets."""

        priority = 0.0
        block_category = military_block.get_military_category()
        if block_category not in self._weight_priority_target:
            logger.warning(f"Military block category '{block_category}' not found in weight_priority_target. Using default defense weight.")
            return 0.0

        for friendly_item in friendly_blocks:
            friendly = friendly_item[1]
            if friendly.id == military_block.id: # Evita di calcolare la priorità con se stesso
                continue

            # weight selection
            weight = self._select_weight(target_block=friendly, task="defense", block_category=block_category) # Seleziona il peso per il blocco target

            # use_recon=False sempre: il ramo difesa valuta alleati, i cui dati sono per definizione
            # a piena visibilità (ground-truth) -- non riceve mai use_recon come parametro proprio.
            if military_block.is_Ground_Base() or military_block.is_Naval_Base():
                route = self.get_shortest_route(military_block.id, friendly.id)
                calc_result = self._calc_surface_priority(block=military_block, target_item=friendly_item, attack_route=route, weight=weight, use_recon=False)
                if calc_result is not None:
                    priority += calc_result
            elif military_block.is_Air_Base():
                calc_result = self._calc_air_priority(block=military_block, target_block=friendly, weight=weight, use_recon=False)
                if calc_result is not None:
                    priority += calc_result

        return priority

    # non necessario utilizzare la cache in quanto sono già stati decorati i metodi superiori _calc_attack_priority e _calc_defense_priority
    @lru_cache(maxsize=256) # Aggiunta cache per questo calcolo
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
    force_type: Optional[str] = None,
    target_affinity: float = 1.0,
    use_recon: bool = False
    ) -> float:
        """Calculate generic priority for a military block towards a target. Considers combat power, time to intercept, range ratio, and weight.

        target_affinity: fattore moltiplicativo opzionale (default 1.0 = neutro, nessun effetto)
        che modula la priorità in base a quanto bene i loadout disponibili del blocco (se aereo)
        rendono contro la composizione reale del target — v. _target_affinity, che restituisce
        sempre 1.0 per il ramo difesa/blocchi non aerei, così _calc_surface_priority (che non lo
        passa mai) resta bit-identico.

        use_recon: se True E si tratta del ramo attacco (bersaglio nemico), la combat power del
        bersaglio viene letta dallo snapshot di ricognizione (self._recon_cp_snapshot, costruito
        una volta per sweep da _build_recon_cp_snapshot) invece che dal ground-truth. Un bersaglio
        assente dallo snapshot (non osservato in questo ciclo) vale 0.0 -- non "ground-truth di
        ripiego" -- che attraverso il gate sotto produce la policy "non visto -> priorità bassa"
        senza bisogno di logica dedicata. Il blocco proprio e il ramo difesa (bersagli alleati)
        restano SEMPRE ground-truth, indipendentemente da use_recon.
        """
        # force_type: se non passato esplicitamente (solo _calc_air_priority lo fa oggi), derivalo dalla
        # categoria militare del blocco.
        force_type = force_type or Context.MILITARY_CATEGORY_TO_FORCE.get(block.get_military_category())
        # Selezione azione: lati diversi -> il blocco attacca (postura 'Attack'); stesso lato -> il
        # blocco difende/protegge (postura 'Defense'). Per 'air' l'azione è ignorata per costruzione
        # (v. _representative_combat_power). Il confronto sui side è generico (vale per bersagli
        # militari, logistici e civili), coerente con il ramo attacco/difesa usato più sotto per i
        # soli bersagli militari.
        is_attack = block.side != target_block.side
        own_action = None if force_type == 'air' else ('Attack' if is_attack else 'Defense')
        combat_power = Tactical_Analysis.representative_combat_power(block, force_type, own_action)
        if not combat_power or combat_power <= 0:
            return 0.0

        time_to_intercept = time_to_intercept or float('inf')
        if time_to_intercept < 1:
            time_to_intercept = 1.0

        target_value = target_block.value or 1.0 # value from 1 to 10

        if target_block.is_military():
            target_force_type = Context.MILITARY_CATEGORY_TO_FORCE.get(target_block.get_military_category())
            if use_recon and is_attack:
                # Fog-of-war: il bersaglio è nemico e il chiamante ha chiesto la stima via
                # ricognizione. Vale per qualunque force_type (anche 'air'), a differenza del
                # ramo ground-truth sotto dove 'air' è gestito nel ramo "difesa" per la sua azione
                # singola -- qui la selezione azione è già stata risolta una volta per sweep in
                # _build_recon_cp_snapshot, non va rifatta qui.
                target_cp = (self._recon_cp_snapshot or {}).get(target_block.id, 0.0)
            elif target_force_type == 'air' or not is_attack:
                # ramo difesa (bersaglio = alleato protetto): quanto regge da solo -> 'Defense'.
                # 'air': azione ignorata per costruzione. Sempre ground-truth (alleato = dati noti).
                target_action = None if target_force_type == 'air' else 'Defense'
                target_cp = Tactical_Analysis.representative_combat_power(target_block, target_force_type, target_action)
            else:
                # ramo attacco: il bersaglio nemico può opporre 'Defense' o rimanere in 'Maintain' —
                # si usa il più alto dei due (convenzione già in uso in
                # Tactical_Evaluation.evaluateCombatSuperiority per il ramo Attack). 'sea' non ha un
                # task 'Maintain' (v. Context.SEA_TASK), quindi si riduce a 'Defense'.
                target_defense_cp = Tactical_Analysis.representative_combat_power(target_block, target_force_type, 'Defense')
                if target_force_type == 'ground':
                    target_maintain_cp = Tactical_Analysis.representative_combat_power(target_block, target_force_type, 'Maintain')
                    target_cp = max(target_defense_cp, target_maintain_cp)
                else:
                    target_cp = target_defense_cp
            #combat_power_ratio = max(0.1, min(target_cp / combat_power, 10.0))
            #in caso di attack, una cb_pow del target superiore rispetto al blocco in esame comporta una priorità più alta, mentre in caso di defense, una cb_pow del target superiore rispetto al blocco in esame comporta una priorità più bassa.
            if target_cp <= 0: # target senza combat power nota: evita ZeroDivisionError, satura al bound corrispondente
                combat_power_ratio = 10.0 if not is_attack else 0.1
            elif not is_attack: # defense
                combat_power_ratio = clip(combat_power / target_cp, 0.1, 10.0)
            else: # attack
                combat_power_ratio = clip(target_cp / combat_power, 0.1, 10.0)
            return (target_value * combat_power_ratio * range_ratio * weight * target_affinity) / time_to_intercept

        elif target_block.is_logistic():
            target_priority = target_priority or 0.0
            return (target_priority * range_ratio * weight * target_affinity) / time_to_intercept

        elif target_block.is_civilian():
            return (target_value * range_ratio * weight * target_affinity) / time_to_intercept

        return 0.0

    @lru_cache(maxsize=256) # Aggiunta cache per questo calcolo
    def _calc_surface_priority(
        self,
        block: Military,
        target_item: Tuple[float, Block],
        attack_route: Optional[Route],
        weight: float,
        use_recon: bool = False) -> float:

        """
        Calculates the priority of a military block (ground or sea) by evaluating its combat power,
        the distance from the target, the combat power of the target or the priority assigned
        in the case of logistical targets.

        Args:
            block (Military): block to calculates priority
            target_item (BlockItem): target BlockItem of the block
            attack_route (Optional[Route]): intercept route to target_block
            weight (float): assigned weight for calculates priority
            use_recon (bool): se True, la combat power del bersaglio (se nemico) viene dallo
                snapshot di ricognizione invece che dal ground-truth -- v. _calculate_priority

        Returns:
            priority (float): priority value of the block, returns 0.0 if not applicable
        """
        target_block = target_item[1]

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
            target_priority=target_item[0],
            use_recon=use_recon
        )

    @lru_cache(maxsize=256)
    def _target_affinity(self, block: Military, target_block: Block) -> float:
        """Fattore moltiplicativo [_AFFINITY_MIN, _AFFINITY_MAX] che modula la priorità di attacco
        in base a quanto bene i loadout disponibili della flotta aerea di block rendono contro la
        composizione reale (ground truth, Tactical_Analysis.target_profile_from_block) di target_block, rispetto
        alla potenza di combattimento generica (target-agnostica) della stessa flotta.

        Restituisce 1.0 (neutro, nessun effetto su _calculate_priority) se: target amico (ramo
        difesa — l'affinità di targeting non ha senso quando non si sta scegliendo un'arma per
        colpire il bersaglio), block non è una base aerea, il profilo del target è vuoto/
        non classificabile, o la flotta non ha aeromobili operativi.
        """
        if block.side == target_block.side:
            return 1.0
        if not block.is_Air_Base():
            return 1.0

        profile = Tactical_Analysis.target_profile_from_block(target_block)
        if not profile:
            return 1.0

        target_distribution = Tactical_Analysis.profile_to_weapon_distribution(profile)
        if not target_distribution:
            return 1.0

        aircraft_by_model = Tactical_Analysis.operative_aircraft_by_model(block)
        if not aircraft_by_model:
            return 1.0

        weighted_target_score = 0.0
        weighted_generic_score = 0.0

        for model, aircraft_list in aircraft_by_model.items():
            count = len(aircraft_list)
            if count == 0:
                continue

            aircraft_data = Aircraft_Data._registry.get(model)
            if aircraft_data is None:
                continue

            available_loadouts_by_task = {
                task: block.get_available_loadouts(model, task=task) for task in Context.AIR_TASK
            }
            target_score, _ = aircraft_data.combat_aggregate_against_target(
                target_distribution, available_loadouts_by_task=available_loadouts_by_task
            )
            generic_score, _ = aircraft_data.combat_aggregate()

            weighted_target_score += target_score * count
            weighted_generic_score += generic_score * count

        if weighted_generic_score <= 0:
            return 1.0

        return clip(weighted_target_score / weighted_generic_score, _AFFINITY_MIN, _AFFINITY_MAX)

    # non necessario utilizzare la cache in quanto sono già stati decorati i metodi superiori _calc_attack_priority e _calc_defense_priority
    @lru_cache(maxsize=256) # Aggiunta cache per questo calcolo
    def _calc_air_priority(self, block: Military, target_block: Block, weight: float, use_recon: bool = False) -> float:

        """Calculates the priority of an air military block by evaluating its combat power,
        the distance from the target, the combat power of the target or the priority assigned
        in the case of logistical targets.

        Args:
            block (Military): block to calculates priority
            target_block (Block): target of the block
            weight (float): assigned weight for calculates priority
            use_recon (bool): se True, la combat power del bersaglio (se nemico) viene dallo
                snapshot di ricognizione invece che dal ground-truth -- v. _calculate_priority

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
            force_type="air",
            target_affinity=self._target_affinity(block, target_block),
            use_recon=use_recon
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
            self._calc_surface_priority.cache_clear()
            self._calc_air_priority.cache_clear()
            self._target_affinity.cache_clear()

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
    
    def __repr__(self) -> str:
        """String representation of the Region."""
        return (f"Region(name='{self._name}', description='{self._description}', "
                f"blocks={len(self._blocks)}, routes={len(self._routes)})")
    
    def __str__(self) -> str:
        """Readable string representation."""
        return f"Region '{self.name}' with {len(self._blocks)} blocks"