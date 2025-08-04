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
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union, Tuple
from sympy import Point, Line, Point2D, Point3D, Line3D, symbols, solve, Eq, sqrt, And
from dataclasses import dataclass
from collections import defaultdict


# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Region')


DEFAULT_ATTACK_WEIGHT = 0.5

DEFAULT_WEIGHT_PRIORITY_TARGET = {  "Ground_Base":   {"attack": {"Ground_Base": 0.7,
                                                                "Naval_Base": 0,
                                                                "Air_Base": 0.1,
                                                                "Logistic": 0.2,
                                                                "Civilian": 0},
                                                    "defence": {"Ground_Base": 0.1,
                                                                "Naval_Base": 0.1,
                                                                "Air_Base": 0.1,
                                                                "Logistic": 0.4,
                                                                "Civilian": 0.3} },
                                    "Air_Base":      {"attack": {"Ground_Base": 0.3,
                                                                "Naval_Base": 0.2,
                                                                "Air_Base": 0.2,
                                                                "Logistic": 0.3,
                                                                "Civilian": 0},
                                                    "defence": {"Ground_Base": 0.3,
                                                                "Naval_Base": 0.1,
                                                                "Air_Base": 0.2,
                                                                "Logistic": 0.3,
                                                                "Civilian": 0} },
                                    "Naval_Base":   {"attack": {"Ground_Base": 0,
                                                                "Naval_Base": 0.5,
                                                                "Air_Base": 0.2,
                                                                "Logistic": 0.3,
                                                                "Civilian": 0},
                                                    "defence": {"Ground_Base": 0.1,
                                                                "Naval_Base": 0.6,
                                                                "Air_Base": 0.1,
                                                                "Logistic": 0.2,
                                                                "Civilian": 0} } }


MILITARY_FORCE = ["ground", "air", "naval"]
ACTION_TASK = {"ground": Context.GROUND_ACTION,
                  "air": Context.AIR_TASK,
                  "ground": Context.NAVAL_TASK}
# NOTA: valuda un preload di Block, Asset, della regioneecc:  

@dataclass
class Region_Params:
    """Data class for Region parameters for validation"""
    name: str
    description: str
    blocks: Optional[List[list]] = None # [priority, block]
    routes: Optional[ Dict[dict]] = None
    limes: Optional[List[Limes]] = None
    

class Region:    

    def __init__(self, name: str, limes: List[Limes] = None, description: Optional[str] = None, blocks: Optional[List[list]] = None, routes: Optional[ Dict[dict]] = None):
            
            
        # Initial parameter validation
        self._validate_all_params(name = name, limes = limes, description = description, blocks = blocks, routes = routes)        

        # propriety
        self._name = name # block name - type str
        self._description = description # block description - type str               
        self._limes = limes # list of limes of the Region - type List[Limes]
        self._routes = routes # ground attack routes
        self._attack_weight = DEFAULT_ATTACK_WEIGHT # coefficient used to calculate the priority of a block considering the attack actions (updating with strategical directory: offensive -> weight= 0.7 -> defence = 1-0-7 = 0.3)
        self._weight_priority_target = DEFAULT_WEIGHT_PRIORITY_TARGET

        # Association   DEVI UTILIZZARE UNA PRIORITY QUEUE. update_blocks_priority ricalcola la priority dei blocchi in base alla loro importanza strategica e ridefinisce il key value per la queue che viene riodinata
        if blocks:
            for block in blocks.values:
                if block.region is not None and block.region != self:
                    raise ValueError(f"Block {block.name} is already associated with another region: {block.region.name}")
                block.region(self)

        self._blocks = blocks # list of Block members of Region - type List[ [priority(float), Block] ]        

        
        # routes dovrebbe essere indicizzato con i blocchi coinvolti: key = (id_block1, id_block_2, ...)
    # methods

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        """Set the name of the Region"""
        self._validate_param('name', value, "str")
        self._name = value
        # Reset cache when block changes
        # self._invalidate_resource_cache()
    
    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        """Set the description of the Region"""
        self._validate_param('description', value, "str")
        self._name = value
        # Reset cache when block changes
        # self._invalidate_resource_cache()

    @property
    def weight(self):
        """get weight: coefficient used to calculate the priority of a block considering the attack actions

        Returns:
            float: weight for calculates priority
        """
        return self._weight

    @weight.setter
    def weight(self, value):
        """Set weight: coefficient used to calculate the priority of a block considering the attack actions"""
        
        self._validate_param('weight', value, "float")
        if 0 > value > 1:
            raise ValueError(f"the weight {value} must be between 0 and 1")
        self._name = value
        # Reset cache when block changes
        # self._invalidate_resource_cache()
    
    @property
    def weight_priority_target(self):
        """get weight_priority_target: list of coefficient used to calculate the priority of a block based on the category it belongs to

        Returns:
            dict: weight for calculates priority
        """
        return self._weight_priority_target

    @weight.setter
    def weight_priority_target(self, value):
        """Set weight_priority_target: list coefficient used to calculate the priority of a block based on the category it belongs to"""
        
        self._validate_param('weight_priority_target', value, "Dict")

        if value.keys() not in Context.MILITARY_CATEGORY:
            raise ValueError(f"value keys {value.keys()!r} not a MILITARY CATEGORY {Context.MILITARY_CATEGORY!r}")
    
        for k,v in value.values():
            if k not in ["attack", "defence"]:
                raise ValueError(f"value keys {k!r} not in [\"attack\", \"defence\"]")
            if v.keys() not in ["Ground_Base", "Naval_Base" ,"Air_Base", "Logistic", "Civilian"]:
                raise ValueError(f"value {v!r} not in [\"Ground_Base\", \"Naval_Base\", \"Air_Base\", \"Logistic\", \"Civilian\"]")
            if not isinstance(v.value(), float):
                raise TypeError(f"weight coefficent must be a float {v.value().__class__.__name__}")

        self._name = value
        # Reset cache when block changes
        # self._invalidate_resource_cache()
    
    @property
    def routes(self):
        """routes getter. dict of Route : {(id_blocks, ....): Route}, (key = list of block's id)
        """
        return self._routes

    @routes.setter
    def routes(self, value):
        """Set the routes dictionary"""
        if not isinstance(value, dict):
            raise TypeError(f"routes must be a dict {value!r}")
        
        for route_item in value:
            if not isinstance(value, list):
                raise TypeError(f"route_item must be a list {route_item!r}")
            if not isinstance(route_item[0], list):
                raise TypeError(f"route list keys must be list of str (id_blocks) {route_item!r}")
            if not self._is_valid_route(route_item[1]):
                raise ValueError(f"All values in routes must be Route objects, current: {route_item[1]!r}")
                    
        self._routes = value    

    def add_route(self, key: str, route: Route):
        """Add a Route to the Region"""
        if not self._is_valid_route(route):
            raise ValueError(f"All values in routes must be Route objects, current: {route!r}")        

        if not isinstance(key, str):
            raise TypeError(f"key {key!r} must be a str")
        
        if not self._validate_route_param():
            pass
           
        self._routes.append([key, route]) # append an route_item with priority value = 0.0        
        logger.info(f"Route added in region {self.name}")

    def get_route(self, block_id: str, block_id_target: Optional[str]):
        """ search routes for a block

        Args:
            block_id (str): block's id

        Returns:
            Tuple[Route]: Returns a tuple of routes that affect the block
        """
        
        if not isinstance(block_id, str):
            raise TypeError("block_id must be a str")
        
        if block_id_target:
            if not isinstance(block_id_target, str):
                raise TypeError("block_id must be a str")
            if block_id == block_id_target:
                raise ValueError(f"block_id_target ({block_id_target}) must be different block_id")
        
        routes = []
        
        for tuple_of_block_id, route in self._routes:
            block_id_found = False
            block_id_target_found = False

            for _block_id in tuple_of_block_id:
                
                if _block_id == block_id:
                    block_id_found = True
                    if block_id_target == True:
                        routes.append(route)
                        continue # to check full list and add more routes or return for speed
                                            
                if _block_id == block_id_target:
                    block_id_target_found = True
                    if block_id == True:
                        routes.append(route)
                        continue #return routes                        
        num_routes = len(routes)

        if num_routes == 0:
            return None
        elif num_routes == 1:
            return routes[0]
        else:
            min_length = int('inf')
            min_route = None
            for route in routes:
                length = route.length()
                if length < min_length:
                    min_length = length
                    min_route = route
        return route

    @property
    def blocks(self):
        return self._blocks

    @blocks.setter
    def blocks(self, value):
        """Set the blocks dictionary"""
    
        if not isinstance(value, list):
            raise TypeError(f"blocks must be a list {value!r}")
        
        for block_item in value:
            if not isinstance(value, list):
                raise TypeError(f"blocks_item must be a list {block_item!r}")
            if not isinstance(block_item[0], float):
                raise TypeError(f"blocks list keys must be floats representing priority {block_item!r}")
            if not self._is_valid_block(block_item[1]):
                raise ValueError(f"All values in blocks must be Block objects, current: {block_item[1]!r}")
            if block_item[1].region is not None and block_item[1].region != self:
                raise ValueError(f"Block {block_item[1].name} is already associated with another region: {block_item[1].region.name}")
            
        
        self._blocks = value        
        # Reset cache when blocks change
        # self._invalidate_resource_cache() # la cache dovrebbe essere costituita dai valori calcolati dai metodi di calcolo della Region.

    def add_block(self, block):
        """Add a Block to the Region"""
        if not self._is_valid_block(block):
            raise ValueError(f"All values in blocks must be Block objects, current: {block!r}")        
        if block.region is not None and block.region != self:
            raise ValueError(f"Block {block.name} is already associated with another region: {block.region.name}")
                
        block.region(self)
        self._blocks.append([0.0, block]) # append an block_item with priority value = 0.0        
        logger.info(f"Block with ID {block.id} added in region {self.name}")


    def get_block_inner_priority_range(self, side: str, category: str, priority_min: float, priority_max: float) -> Optional[list[Block]]:     
        """
        returns a list of block objects that have priorities between the arguments: priority_min and priority_max

        Args:           
            side (str): side of the block
            category (str): category of the block: military, Logistic, Civilian
            priority_min (float): minimum priority
            priority_max (float): maximum priority

        Returns:
            block ( Optional[Block] ): Block object: 
        
        """
        if not isinstance(priority_min, float) or not isinstance(priority_max, float):
            raise TypeError("priority_min and priority_max must be floats")
        if priority_min > priority_max:
            raise ValueError("priority_min must be less than or equal to priority_max")
        block_list = self.get_priority_block_list(side=side, category=category)
        blocks_in_range = [block for block in block_list if priority_min <= block[0] <= priority_max]
        
        if not blocks_in_range:
            logger.warning(f"No blocks found with priority in the range [{priority_min}, {priority_max}]")
            return None
        return [block[1] for block in blocks_in_range]
        

    def get_block_by_id(self, block_id: str) -> Optional[Block]:
        """
        
        :param block_id: ID of the block
        :return: Block object or None if not found
        """
        """
        Return a Block by its ID or None

        Args:                
            block_id (str): ID of the block            

        Returns:
            block ( Optional[Block] ): Block object: 
        
        """
        if not isinstance(block_id, str):
            raise TypeError("block_id must be a string")
        
        for block_item in self._blocks:
            if block_item[1].id == block_id:
                return block_item
        
        logger.warning(f"Block with ID {block_id} not found in region {self.name}")
        return None
    
    def get_block_list(self, side: str, category: Optional[str], block_class: Optional[str]) -> List[Tuple[float, Block]]:
        """
        Return a list of tuples with block priority and Block object

        Args:                
            side (str): side of the block
            category (str): category of the block: military, Logistic, Civilian
            block_class: class of the block: Military, Production, Storage, Transport, Urban                

        Returns:
            block list ( List[Tuple[float, Block]] ): list of tuples with block priority and Block object: 
        
        """
        
        block_list = []
        for block in self._blocks:
            if block.side == side:
                if category:
                    if block.category == category:
                        if block_class:
                            if block.__class__.__name__ == block_class:
                                block_list.append((block[0], block[1]))  # added block only by side, categor and class_block (Production, Storage, ...)
                        else:               
                            block_list.append((block[0], block[1])) # added block by side and category (Logistic, Civilian, Military)
                else:
                    block_list.append((block[0], block[1])) # added block only by side (red, blue)
        
        return block_list
    
    def get_highest_priority_block(self, side: str, quantity: int, category: Optional[str], block_class: Optional[str]) -> List[Tuple[float, Block]]:
        """
        Return a list of quantity tuples with highest priority

        Args:                
            side (str): side of the block
            quantity (int): max number of block in list
            category (str): category of the block: military, Logistic, Civilian
            block_class: class of the block: Military, Production, Storage, Transport, Urban                

        Returns:
            block list ( List[Tuple[float, Block]] ): list of tuples with block priority and Block object: 
        
        """
        if quantity < 1:
            raise ValueError(f"quantity must be bigger of 0")
        
        
        block_count = 0
        block_list = self.get_block_list(side = side, category = category, block_class = block_class)
        block_list = self.sorted_blocks_list(block_list.copy())
             
        return block_list[ :quantity ]
        # ottimizzato: return self.sorted_blocks_list( self.get_block_list(side = side, category = category, block_class = block_class) )[ : quantity ]

    def sorted_blocks_list(self, block_list: List[Tuple[float, Block]]) -> List[Tuple[float, Block]]:
        """
        Return a sorted list of blocks by priority in descending order
        """
        if not isinstance(block_list, list):
            raise TypeError("blocks must be a list") 
        
        return sorted(block_list, key=lambda x: x[0], reverse=True)

    def remove_block(self, block_id: str):
        """
        Remove a Block from the Region by its ID
        :param block_id: ID of the block to remove
        :return: None
        """
        if not isinstance(block_id, str):
            raise TypeError("block_id must be a string")
        
        block_item = self.get_block_by_id(block_id)
        
        if block_item is not None:
            self._blocks.remove( block_item )
            logger.info(f"Block with ID {block_id} added in region {self.name}")
        else:
            logger.warning(f"Block with ID {block_id} not found in region {self.name}")
        return None

    def get_enemy_blocks(self, side: str, category: Optional[str], block_class: Optional[str]) -> List[Tuple[float, Block]]:
        
        """
        Return a list of Blocks of the Region that have the same side as the enemy_side parameter
        :param enemy_side: the side of the enemy
        :return: a list of Blocks
        """
        
        return self.get_block_list(side = Utility.enemySide(side), category=category, block_class=block_class)

    def check_class(self, object):
        """Return True if objects is a Object object otherwise False"""
        return type(object) == type(self)

    def check_class_list(self, objects):
        """Return True if objectsobject is a list of Block object otherwise False"""
        return all(type(obj) == type(self) for obj in objects)

    def check_list_of_objects(self, classType: type, objects: List) -> bool: 
        """ Return True if objects is a list of classType object otherwise False"""
        return isinstance(objects, List) and not all(isinstance(obj, classType) for obj in objects )
     

    def get_blocks(self, blockClass: str, side: str) -> List[Block]:
        """ Return a list of blocks of a specific category and side"""

        if blockClass not in Context.BLOCK_CATEGORY:
            raise ValueError(f"Invalid block category {0}. block category must be: {1}".format(blockClass, Context.BLOCK_CATEGORY))
        
        if blockClass == "Logistic":
            return [block for block in self._blocks if any(isinstance(block, Production), isinstance(block, Storage), isinstance(block, Transport)) and block.side == side]
        
        if blockClass == "Civilian":
            return [block for block in self._blocks if isinstance(block, Urban) and block.side == side]
        
        if blockClass == "Military":
            return [block for block in self._blocks if isinstance(block, Military) and block.side == side]

    def calc_region_strategic_logistic_center(self, side: str) -> Point2D:
        """Calculation of baricenter point of the complessive logistic block's strategic value

        Args:
            side (str): side of blocks

        Returns:
            Point2D: point of the strategic logistic center
        """        
        logistic_blocks = self.get_blocks("Logistic", side)        
        # escludo le Military in quanto tot_RSP è utilizzato per valutare la copertura da richiedere alle Military per la protezione di questi blocchi    
        n = len(logistic_blocks)
        tot_RSP, tp = 0, 0 # tot_RSP: summmatory of strategic Logistic block priority

        for block in logistic_blocks:
            position_2d = Point2D(block.position.x, block.position.y)
            tot_RSP += block.value# utilizza value dovrebbe utilizzare la priority             
            tp += position_2d * block.value # Point2D per uno scalare produce un Point2D con le sue coordinate moltiplicate ognuna per lo scalare
        
        r_SLP = tp / (n * tot_RSP) # r_SLP: region strategic Logistic center position for side blocks
        return r_SLP
    
    def calc_combat_power_center(self, side: str): 
        """ Calculation of baricenter point of the complessive military block's combat power 

        Args:
            side (str): side of blocks
            force (str): type of military force (air, ground, naval)

        Returns:
            Point2D: combat power baricenter
        """                
        blocks_quantity = {}

        for force in MILITARY_FORCE:
            for task in ACTION_TASK[force]:                    
                blocks_quantity[force][task] = 0

        Militarys = self.get_blocks("Military", side)                                
        r_CPP, tot_CP, tp = {}, {}, {} # tot_CP: summmatory of strategic block combat power
        
        for force in MILITARY_FORCE:
            for task in ACTION_TASK[force]:                                    
                for block in Militarys:
                    if ( block.is_Air_Base and force == "air" ) or (block.is_Ground_Base and force == "ground") or ( block.is_navalbase and force == "naval" ):
                        cp = block.combat_power(action = task, military_force = force) # block combat power 
                        tot_CP[force][task] += cp  # sum of block's combat power 
                        tp[force][task] += block.position * cp  # sum of ponderate position block's point
                        blocks_quantity[force][task] += 1 # number of blocks counted
        
        for force in MILITARY_FORCE:
                for task in ACTION_TASK[force]:                    
                    r_CPP[force][task] = tp[force][task] / ( blocks_quantity[force][task] * tot_CP[force][task] ) # r_CPP: region strategic combat power center position for side blocks
        return r_CPP

    def calc_region_warehouse(self):
        """ Return the total resource avalaible in warehouse"""
        # per le hc, hs, hb devi prevedere delle scuole di formazione militare di class Production ed eventualmente category Military
        tot_warehouse = Payload()

        for block in self._blocks:
            tot_warehouse += block[1].resource_manager.warehouse()            
        return tot_warehouse
    
    def calc_region_actual_production(self):
        """ Return the total production resources of the Region"""
        tot_production = Payload()

        for block in self._blocks:
            if isinstance(block[1], Production):
                tot_production += block[1].resource_manager.actual_production()        
        return tot_production

    def calc_region_logistic_production_value(self) -> float:
        """ Return the total production value of the Region"""
        tot_production_production_value = 0.0
        tot_storage_production_value = 0.0      # è prevista per l'achitettura del resource manager che considera produzione, consumo e stoccaggio per qualsiasi blocco indipendentmente dalla sua classe. Non essendo un blocco prduttivo Si presume che in questo caso la priduzione sia nulla.
        tot_transport_production_value = 0.0    # è prevista per l'achitettura del resource manager che considera produzione, consumo e stoccaggio per qualsiasi blocco indipendentmente dalla sua classe. Non essendo un blocco prduttivo Si presume che in questo caso la priduzione sia nulla.
        tor_urban_production_value = 0.0

        for block in self._blocks:
            if isinstance(block[1], Production):
                tot_production_production_value += block[1].resource_manager.production_value()
            elif isinstance(block[1], Storage):
                tot_storage_production_value += block[1].resource_manager.production_value()
            elif isinstance(block[1], Transport):
                tot_transport_production_value += block[1].resource_manager.production_value()
            elif isinstance(block[1], Urban):
                tot_urban_production_value += block[1].resource_manager.production_value()
        tot_production_value = (tot_production_production_value + tot_storage_production_value +
                                tot_transport_production_value + tor_urban_production_value)
        logger.debug(f"Region {self.name} total production value: {tot_production_value}")        
        if tot_production_value == 0.0:
            logger.warning("Total production value is 0, setting all production and storage blocks priority to 0")
            return 0.0        
        return {    "total": tot_production_production_value,
                    "production": tot_production_production_value,
                    "storage": tot_storage_production_value,
                    "transport": tot_transport_production_value,
                    "urban": tor_urban_production_value}
    

    # nota: per i blocchi logistici la priority è utilizzata per l'assegnazione delle risorse di rifornimento e per l'assegnazione delle risorse militari
    # mentre per i blocchi militari la priority è utilizzata solo per l'assegnazione delle risorse di rifornimento
    def update_logistic_blocks_priority(self) -> bool:
        """Update the priority of the Logistic blocks in the Region based on their strategic importance key: production_value"""
        tot_production_value = self.calc_region_logistic_production_value() * MAX_VALUE # MAX_VALUE is a constant defined in Block.py, used to normalize the production value to a range between 0 and 1
        
        if tot_production_value == 0:
            logger.warning("Total production value is 0, setting all production and storage blocks priority to 0")
            return False
        
        for block in self._blocks:

            if block[1].isLogistic(): # isLogistic is a property of Block that returns True if the block is a Production, Storage or Transport block  
                production_value = block[1].resource_manager.production_value()
                
                if production_value > 0:          

                    block_absolute_priority_value =  production_value * block[1].value

                    if isinstance(block[1], Production):
                        # Production blocks priority is based on their production value relative to the total production value of the Region
                        block_priority = block_absolute_priority_value / tot_production_value["production"]                        
                        
                    elif isinstance(block[1], Storage):
                        # Storage blocks priority is based on their production value relative to the total production value of the Region
                        block_priority = block_absolute_priority_value / tot_production_value["storage"]                                              

                    elif isinstance(block[1], Transport):
                        # Transport blocks priority is based on their production value relative to the total production value of the Region
                        block_priority = block_absolute_priority_value / tot_production_value["transport"]                                                                    
                    
                    elif isinstance(block[1], Urban):
                        # Urban blocks priority is based on their production value relative to the total production value of the Region
                        block_priority = block_absolute_priority_value / tot_production_value["urban"]                                            

                    else:
                        continue # if the block is not a Production, Storage, Transport or Urban block, skip it

                    block[0] = block_priority
                    logger.debug(f"Block {block[1].name} priority updated to {block_priority}")             
                
        return True

    def update_military_blocks_priority(self, side: str) -> None:
        """
            calculates the priority of the military blocks stored in blocks. Priority is calculates by evaluating military combat power, the distance from the target, the combat power of the target or the 
            priority assigned in the case of logistical targets.

            Args:                
                side (str): side of the blocks

            Returns:
                
        """   

        def __calc_surface_priority(block: Military, target_block: Block, attack_route: Route, weight: float) -> Optional[float]:   
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
                target_priority, _ = self.get_block_by_id(block.id)
                
                if not target_priority:
                    self.update_logistic_blocks_priority()
                priority = target_priority * range_ratio * weight / time_to_intercept                
                return priority
                
            return None
                
        
        def __calc_air_priority(block: Military, target_block: Block, weight: float) -> Optional[float]:     
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


        # implementare in modo da usarli per orientare la priorità per l'attacco verso blocchi più 
        # vicini al centro della potenza complessiva di combattimento del nemico e quella della difesa 
        # verso blocchipiù vicini al baricentro delle zone produttive

        #friendly_logistic_baricenter = self.calc_region_strategic_logistic_center( side = side )
        #enemy_combat_power_center = self.calc_combat_power_center( side = Utility.enemySide(side) )

        #priority only for military block category
        friendly_blocks = self.get_block_list(side = side, category = "Military")                                
        #target block for all category (military, logistic and civilian)
        enemy_blocks = self.get_block_list(side = Utility.enemySide(side))                                                        
        priority = {"attack": 0.0, "defence": 0.0}
      
        for block_item in friendly_blocks:                   
            military = block_item[1]            
            #setup military block category to select weight index
            block_category = military.get_military_category()            
            
            # calc priority factor for attack                          
            for _, target in enemy_blocks:                     
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
                if military.is_Ground_Base() or military.is_Naval_Base():                    
                    priority["attack"] += __calc_surface_priority(block = military, target_block = target, attack_route = self.get_route(military, target), weight = weight)
                elif military.is_Air_Base():                    
                    priority["attack"] += __calc_air_priority(block = military, target_block = target, weight = weight)

            # calc priority factor for defence
            for _, friendly in friendly_blocks:
                if military == friendly:
                    continue
                #setup target block category to select weight index
                if friendly.is_military():
                    target_category = target.get_military_category()
                elif friendly.is_civilian() or target.is_logistic():
                    friendly_category = target.category              
                else:
                    logger.warning(f"the  block{friendly!r} is not a military base, logistical or civil block; block weight will be set with Civilian value")
                    friendly_category = "Civilian"
                
                # weight selection
                weight = self.weight_priority_target[block_category]["defence"][friendly_category]
                
                if military.is_Ground_Base() or military.is_Naval_Base():
                    priority["defence"] += __calc_surface_priority(block = military, target_block = friendly, attack_route = self.get_route(military, friendly), weight = weight)
                elif military.is_Air_Base():                
                    priority["defence"] += __calc_air_priority(block = military, target_block = friendly, weight = weight)
         
            overall_priority = priority["attack"] * weight + priority["defence"] * (1 - weight)
            #update_block_item = (overall_priority, military)
            #self._blocks.remove(block_item)
            #self._blocks.append(update_block_item)
            block_item[0] = overall_priority
            logger.debug(f"Block {military.name} priority updated to {overall_priority} (attack: {priority['attack']}, defence: {priority['defence']})")

        return
        
                        
    def calc_region_ground_combat_power(self, side: str, action: str):
        """ Return the total combat power of the Region"""
        block_list = [block for block in self.blocks if block.side == side and isinstance(block, Military)]        
        combat_power = 0

        for block in block_list:
            combat_power += block.groundCombatPower(action)

        return combat_power

    def calc_region_storage(self, side: str, type: str):
        """ Return the total storage of the Region"""
        # side.sum( block.storage() )
        pass

    def calc_region_goods_request(self, side: str, category: str|None):
        """ Return the total consumed of the Region"""        
        block_list = None
            
        if category == Context.BLOCK_CATEGORY["Military"]:
            block_list = [block for block in self.blocks if block.side == side and isinstance(block, Military) or block.isMilitary]
        elif category == Context.BLOCK_CATEGORY["Logistic"]:
            block_list = [block for block in self.blocks if block.side == side and block.isLogistic]
        elif category == Context.BLOCK_CATEGORY["Civilian"]:
            block_list = [block for block in self.blocks if block.side == side and isinstance(block, Urban)]        
        elif category in Context.BLOCK_CLASS:
            block_list = [block for block in self.blocks if block.side == side and isinstance(block, category)]        
        elif category == "All":
            block_list = self.blocks
        else:
            raise Exception(f"category {0} must be: {1}".format(category, [Context.BLOCK_CATEGORY, Context.BLOCK_CLASS]))

        tot_request = Payload()

        for block in block_list:
            tot_request.energy += block.rcp.energy
            tot_request.goods += block.rcp.goods
            tot_request.hr += block.rcp.hr
            tot_request.hc += block.rcp.hc
            tot_request.hs += block.rcp.hs
            tot_request.hb += block.rcp.hb

        return tot_request
        

    @property
    def morale(self, side: str):
        morale = 0
        block_list = [block for block in self.blocks if block.side == side]

        for block in block_list:
            morale += block.morale

        return morale / len(self.blocks)

    @property
    def morale_military(self, side: str):
        morale = 0

        block_list = [block for block in self.blocks if block.isMilitary and block.side == side]

        for block in block_list:
            morale += block.morale

        return morale / len(self.blocks)

    


    # === VALIDATION METHODS ===

    def _is_valid_route(self, route: Any) -> bool:
        """Check if an object is a valid Route"""
        return hasattr(route, '__class__') and route.__class__.__name__ == 'Route'

    def _validate_route_param(self, value: Any) -> None:
        """Validate route parameter"""
        if value is not None and not self._is_valid_route(value):
            raise TypeError("block must be None or a Route object")    

        
    def _is_valid_block(self, block: Any) -> bool:
        """Check if an object is a valid Block"""
        return hasattr(block, '__class__') and block.__class__.__name__ == 'Block'    

    def _validate_block_param(self, value: Any) -> None:
        """Validate block parameter"""
        if value is not None and not self._is_valid_block(value):
            raise TypeError("block must be None or a Block object")

    def _validate_all_params(self, **kwargs) -> None:
        """Validate all input parameters"""
        validators = {            
            'name': lambda x: self._validate_param('name', x, "str"),
            'description': lambda x: self._validate_param('description', x, "str"),
            'side': lambda x: self._validate_param('side', x, "str"),
            'blocks': lambda x: self._validate_dict_block_param('blocks', x),
            'limes': lambda x: self._validate_dict_limes_param('limes', x),
            'routes': lambda x: self._validate_dict_route_param('routes', x),
        }
        
        for param, value in kwargs.items():
            if param in validators and value is not None:
                validators[param](value)

    def _validate_dict_block_param(self, param_name: str, value: Any) -> None:
        """Validate dictionary parameters"""
        if not isinstance(value, dict):
            raise TypeError(f"{param_name} must be a dictionary")
        
        for key, block in value.items():
            if not isinstance(key, str):
                raise TypeError(f"{key!r} keys must be strings")
            if not self._is_valid_block(block):
                raise ValueError(f"All values in {param_name} must be Block objects")

    def _validate_dict_route_param(self, param_name: str, value: Any) -> None:
        """Validate dictionary parameters"""
        if not isinstance(value, dict):
            raise TypeError(f"{param_name} must be a dictionary")        
        
        for key, route in value.items():
            if not self._is_valid_route(route):
                raise ValueError(f"All values in {param_name} must be Route objects")
            if not isinstance(key, str):
                raise TypeError(f"{param_name} keys must be strings")
            
            for _, block in self._blocks:
                if any(block.id in key): #one or more blocks are on Route (key = list of block's id)
                    return True
        return False


                
            

    def _validate_param(self, param_name: str, value: Any, expected_type: str) -> bool:
        """Validate a single parameter"""
        if value is not None and hasattr(value, '__class__') and value.__class__.__name__ == expected_type:
            return
        raise TypeError(f"Invalid type for {param_name}. Expected {expected_type}, got {type(value).__name__}")

    def __repr__(self) -> str:
        """String representation of the Resource Manager"""
        return (f"Region(name={self._name}, description={self._description}, side={self._side}",                
                f"blocks={len(self._clients)}, servers={len(self._server)}, "
                f"warehouse={self._warehouse!r})",
                f"limes={self._limes!r})")

    def __str__(self) -> str:
        """Readable string representation"""
        return f"Region {self.name} {self.description} on side {self.side} with {len(self._blocks)} blocks"