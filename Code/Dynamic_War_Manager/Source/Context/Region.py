from Code.Dynamic_War_Manager.Source.Context import Context
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Block.Military import Military
from Code.Dynamic_War_Manager.Source.Block.Production import Production
from Code.Dynamic_War_Manager.Source.Block.Storage import Storage
from Code.Dynamic_War_Manager.Source.Block.Transport import Transport
from Code.Dynamic_War_Manager.Source.Block.Urban import Urban
from Code.Dynamic_War_Manager.Source.DataType.Limes import Limes
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union, Tuple
from sympy import Point, Line, Point2D, Point3D, Line3D, symbols, solve, Eq, sqrt, And

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Region')

# NOTA: valuda un preload di Block, Asset, della regioneecc:  

class Region:    

    def __init__(self, name: str, description: str, side: str, blocks: List[Block] = None, limes: List[Limes]=None):
            
        
        # check input parameters
        check_results = self.checkParam( name, description, blocks, limes )
        
        if not check_results:
            raise TypeError("Invalid parameters: " +  check_results[2] + ". Object not istantiate.")
            

        # propriety
        self._name = name # block name - type str
        self._description = description # block description - type str  
        self._side = side # side of the Region - type str, must be: Blue, Red or Neutral            
        self._limes = limes # list of limes of the Region - type List[Limes]

        # Association             
        if blocks:
            for block in blocks:
                block.region(self)

        self._blocks = blocks # list of Block members of Region - type List[Block]
                    
        self._blocks_priority = {} # dicr of Block priority of the Region - type Dict{id: Block}
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
    def blocks_priority(self):
        return self._blocks_priority

    @blocks_priority.setter
    def blocks_priority(self, value):
        
        self._blocks_priority = value

    @property
    def blocks(self):
        return self._blocks

    @blocks.setter
    def blocks(self, value):
        """Set the blocks dictionary"""
        if not isinstance(value, dict):
            raise TypeError("blocks must be a dictionary")
        
        for server_id, block in value.items():
            if not isinstance(server_id, str):
                raise TypeError("blocks dictionary keys must be strings")
            if not self._is_valid_block(block):
                raise ValueError(f"All values in blocks must be Block objects, current: {block!r}")
        
        self._blocks = value.copy()

    def addBlock(self, block):
        if isinstance(block, Block):
            block.region(self)
            self._blocks.append(block)
        else:
            raise ValueError("Il valore deve essere un oggetto di tipo Block")

    def getLastBlock(self):
        if self._blocks:
            return self._blocks[-1]
        else:
            raise IndexError("La lista è vuota")

    def getBlock(self, index):
        if index < len(self._blocks):
            return self.blocks[index]
        else:
            raise IndexError("Indice fuori range")

    def removeBlock(self, block):
        if isinstance(block , Block) and block in self._blocks and block.region == self:
            block.region(None)
            self._blocks.remove(block)
        else:
            raise ValueError("Il blocco non esiste nella lista")

    # deprecated: Region has a specific side, so this method is not needed
    def getEnemyBlocks(self, enemy_side: str):
        
        """
        Return a list of Blocks of the Region that have the same side as the enemy_side parameter
        :param enemy_side: the side of the enemy
        :return: a list of Blocks
        """
        enemy_blocks = [block for block in self._blocks if block.side == enemy_side]
        return enemy_blocks

    def checkClass(self, object):
        """Return True if objects is a Object object otherwise False"""
        return type(object) == type(self)

    def checkClassList(self, objects):
        """Return True if objectsobject is a list of Block object otherwise False"""
        return all(type(obj) == type(self) for obj in objects)

    def checkListOfObjects(self, classType: type, objects: List) -> bool: 
        """ Return True if objects is a list of classType object otherwise False"""
        return isinstance(objects, List) and not all(isinstance(obj, classType) for obj in objects )
     
    def block_status(self, blockCategory: str):
        """report info on specific block type(Mil, Urban, Production, Storage, Transport)"""
        # as = .... 
        # return as
        pass

    def getBlocks(self, blockCategory: str, side: str) -> List[Block]:
        """ Return a list of blocks of a specific category and side"""

        if blockCategory not in Context.BLOCK_CATEGORY:
            raise ValueError(f"Invalid block category {0}. block category must be: {1}".format(blockCategory, Context.BLOCK_CATEGORY))
        
        if blockCategory == "Logistic":
            return [block for block in self._blocks if any(isinstance(block, Production), isinstance(block, Storage), isinstance(block, Transport)) and block.side == side]
        
        if blockCategory == "Civilian":
            return [block for block in self._blocks if isinstance(block, Urban) and block.side == side]
        
        if blockCategory == "Military":
            return [block for block in self._blocks if isinstance(block, Military) and block.side == side]

    def calcRegionStrategicLogisticCenter(self, side: str) -> Point2D:
        
        logistic_blocks = self.getBlocks("Logistic", side)
        
        # escludo le Military in quanto tot_RSP è utilizzato per valutare la copertura da richiedere alle Military per la protezione di questi blocchi    
        n = len(logistic_blocks)
        tot_RSP, tp = 0, 0 # tot_RSP: summmatory of strategic logistic block priority

        for block in logistic_blocks:
            position_2d = Point2D(block.position.x, block.position.y)
            tot_RSP += block.value             
            tp += position_2d * block.value # Point2D per uno scalare produce un Point2D con le sue coordinate moltiplicate ognuna per lo scalare
        
        r_SLP = tp / (n * tot_RSP) # r_SLP: region strategic logistic center position for side blocks
        return r_SLP
    
    def calcRegionCombatPowerCenter(self, side: str): 
        
        Militarys = self.getBlocks("Military", side)
                
        n = len(Militarys)
        tot_CP, tp = 0, 0 # tot_CP: summmatory of strategic block combat power

        for block in Militarys:
            tot_CP += block.combat_power
            tp += block.position * block.combat_power 
        
        r_CPP = tp / (n * tot_CP) # r_CPP: region strategic combat power center position for side blocks
        return r_CPP

    def calcRegionProduction(self):
        """ Return the total production of a specific type of goods, energy, human resource"""
        # per le hc, hs, hb devi prevedere delle scuole di formazione militare di class Production ed eventualmente category Military
        tot_production = Payload()

        for block in self._blocks:
            tot_production += block.payload
            
        return tot_production

    def calcRegionGroundCombatPower(self, side: str, action: str):
        """ Return the total combat power of the Region"""
        block_list = [block for block in self.blocks if block.side == side and isinstance(block, Military)]        
        combat_power = 0

        for block in block_list:
            combat_power += block.groundCombatPower(action)

        return combat_power

    def calcRegionStorage(self, side: str, type: str):
        """ Return the total storage of the Region"""
        # side.sum( block.storage() )
        pass

    def calcRegionGoodsRequest(self, side: str, category: str|None):
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
        

    def calcRegionTotalTransport(self, side: str, type: str):
        """ Return the total transport of the Region"""
        # side.sum( block.transport() )
        pass

    @property
    def morale(self, side: str):
        morale = 0
        block_list = [block for block in self.blocks if block.side == side]

        for block in block_list:
            morale += block.morale

        return morale / len(self.blocks)

    @property
    def moraleMilitary(self, side: str):
        morale = 0

        block_list = [block for block in self.blocks if block.isMilitary and block.side == side]

        for block in block_list:
            morale += block.morale

        return morale / len(self.blocks)

    def evaluate_blocks_priority(self, side: str):
        """Evaluate the priority of the blocks of the Region"""
        # side: Red, Blue, Neutral
        # return a list of blocks ordered by priority
        block_list = [block for block in self.blocks if block.side == side]
        # IN BASE ALL'IMPORTANZA STRATEGICA DEI BLOCCHI, VALUTA LA PRIORITA' DEI BLOCCO E RITORNA UNA LISTA ORDINATA PER PRIORITA'
        # ANALISI MILITARY: da determinare in base alla vicinanza/protezione dei blocchi Military rispetto agli urban e in base alla situazione tattico strategica rispetto ai blocchi nemici
        #ANALISI LOGISTIC: non serve in quanto questa deriva dall'analisi militare e civile
        #ANALISI CIVILIAN: da asegnare in modo statico inbase all'importanza dell'Urban
        # la priority deve essere un float che va da 0 a 1, dove 0 è la priorità più bassa e 1 è la priorità più alta
        # NOTA: per ora non implemento la priorità dei blocchi, ma solo la loro presenza
        # block_list.sort(key=lambda x: x.priority, reverse=True)

        # return block_dict # Dictionary{block_id: relative_priority}
        pass

    def block_priority(self, block_id: str) -> Optional[float]:
        """Return the priority of a block"""
        if block_id in self._blocks_priority:
            return self._blocks_priority[block_id]
        


     # === VALIDATION METHODS ===
    
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
            'blocks': lambda x: self._validate_dict_param('clients', x),
            'limes': lambda x: self._validate_dict_param('limes', x),
        }
        
        for param, value in kwargs.items():
            if param in validators and value is not None:
                validators[param](value)

    def _validate_dict_param(self, param_name: str, value: Any) -> None:
        """Validate dictionary parameters"""
        if not isinstance(value, dict):
            raise TypeError(f"{param_name} must be a dictionary")
        
        for key, block in value.items():
            if not isinstance(key, str):
                raise TypeError(f"{param_name} keys must be strings")
            if not self._is_valid_block(block):
                raise ValueError(f"All values in {param_name} must be Block objects")

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