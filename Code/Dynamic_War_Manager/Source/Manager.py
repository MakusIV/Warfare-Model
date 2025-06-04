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

class Manager:
    
    def __init__(self, region: str, blocks: Optional[Dict[str, Block]] = None):
        
        self._region = region
        self._blocks = blocks if blocks is not None else {}
        
        # propriety
        self._limes = Limes(region)
        self._assets: Dict[str, Any] = {}  # Placeholder for assets
        self._payloads: Dict[str, Payload] = {}
        
        # Initialize blocks
        self._initialize_blocks()
        
    def _initialize_blocks(self):
        """Initialize the blocks for the region."""
        self._blocks['Military'] = Military(self._region)
        self._blocks['Production'] = Production(self._region)
        self._blocks['Storage'] = Storage(self._region)
        self._blocks['Transport'] = Transport(self._region)
        self._blocks['Urban'] = Urban(self._region)




    
    

    # livello coalizione: Valutazione delle priority strategiche delle regioni

    # livello regione: Valutazione delle priority strategiche dei vari blocchi

    # livello blocco: realizzata : l'erogazione delle risorse nelle LINE considerando le priorità dei CLIENT (Blocks) (il server richiede la valutazione delle priorità utilizzando il suo componente resource manager )

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