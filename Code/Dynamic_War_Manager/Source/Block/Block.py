from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union
from numpy import mean
from sympy import Point
from dataclasses import dataclass
from Code.Dynamic_War_Manager.Source.Component.Resource_Manager import Resource_Manager
from Code.Dynamic_War_Manager.Source.Utility.Utility import validate_class, setName, setId, mean_point, evaluateMorale, enemySide
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.DataType.Event import Event
from Code.Dynamic_War_Manager.Source.DataType.State import State
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload
from Code.Dynamic_War_Manager.Source.Context.Context import BLOCK_CATEGORY, SIDE

if TYPE_CHECKING:
    from Code.Dynamic_War_Manager.Source.Asset.Asset import Asset
    from Code.Dynamic_War_Manager.Source.Context.Region import Region

# LOGGING
# Logger setup
    # CRITICAL 	50
    # ERROR 	40
    # WARNING 	30
    # INFO 	20
    # DEBUG 	10
    # NOTSET 	0
logger = Logger(module_name=__name__, class_name='Block')

# Constants
MAX_VALUE = 10  # Maximum value for block's strategic weight parameter
MIN_VALUE = 1   # Minimum value for block's strategic weight parameter  

@dataclass
class BlockParams:
    """Data class for holding block parameters for validation"""
    name: Optional[str] = None
    description: Optional[str] = None
    side: Optional[str] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    functionality: Optional[str] = None
    value: Optional[int] = None
    region: Optional["Region"] = None    

class Block:
    """
    Represents a logistic or territorial block in a simulation game.
    
    A block contains and manages resources (Assets) and can be classified
    as military, logistic, or civilian.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        side: Optional[str] = None,
        category: Optional[str] = None,
        sub_category: Optional[str] = None,
        functionality: Optional[str] = None,
        value: Optional[int] = None,
        region: Optional[Union["Region", None]] = None
    ):
        """
        Initialize a new block.

        Args:
            name: Block name
            description: Block description
            side: Block side (e.g., "Blue", "Red", "Neutral")
            category: Block category (e.g., "Civilian", "Logistic", "Military")
            sub_category: Block sub-category (e.g., "Road", "Railway")
            functionality: Block functionality
            value: Strategic value of the block
            region: Region the block belongs to
            resource_manager: Resource Manager of the block

        Raises:
            ValueError: If parameters are invalid
        """
        # Block properties
        self._name = name if name else setName('Unnamed')
        self._id = setId(self._name, None)
        self._description = description or ""
        self._side = side or "Neutral"
        self._category = category or ""
        self._sub_category = sub_category or ""
        self._functionality = functionality or ""
        self._value = value or MIN_VALUE # rappresents strategic weight parameter for calculus of the block's strategic value.  Assigned from campaign maker. default value is 1
        self._events = []
        self._assets = {}
        self._region = region
        self._state = State("Block", self._id)
        self._resource_manager = Resource_Manager(block = self)

        # Validate parameters
        self._validate_params(
            name=name,
            description=description,
            side=side,
            category=category,
            sub_category=sub_category,
            functionality=functionality,
            value=value, # rappresents weight parameter for calculus of the block's strategic value.  Assigned from campaign maker. default value is 1 max value = 10
            region=region
        )

    def _validate_params(self, **kwargs) -> None:
        """
        Validate block parameters.

        Args:
            kwargs: Parameters to validate

        Raises:
            TypeError: If parameter has invalid type
            ValueError: If parameter has invalid value
        """
        type_checks = {
            'name': str,
            'description': str,
            'side': str,
            'category': str,
            'sub_category': str,
            'functionality': str,
            'value': int,
            'region': (type(None)), # accetta solo None durante il runtime, altrimenti genera errore perchè Region non è importata e non deve esserlo: l'utilizzo dei suoi metodi è cmq garantito dall'oggetto importato 
            'state': State,
            'resource_manager': Resource_Manager
        }


        for param, value in kwargs.items():
            if value is not None and param in type_checks:
                expected_type = type_checks[param]
                # Controllo speciale per Region
                if param == 'region':
                    if not (value is None or getattr(value, '__class__', {}).__name__ == 'Region'):
                        raise TypeError(f"region must be None or a Region object. Current type: {type(value).__name__}")
                    continue
                if not isinstance(value, expected_type):
                    raise TypeError(f"{param} must be {expected_type.__name__}")

        # Additional value checks
        if 'side' in kwargs and kwargs['side'] and kwargs['side'] not in SIDE:
            raise ValueError(f"side must be one of: {', '.join(SIDE)}")
        
        if 'category' in kwargs and kwargs['category'] and kwargs['category'] not in BLOCK_CATEGORY:
            raise ValueError(f"category must be one of: {', '.join(BLOCK_CATEGORY)}")
        
        if 'value' in kwargs and kwargs['value'] is not None:
            if not isinstance(kwargs['value'], int):
                raise TypeError(f"value must be an integer. Current type: {type(kwargs['value']).__name__}")
            if kwargs['value'] < MIN_VALUE or kwargs['value'] > MAX_VALUE:
                raise ValueError(f"value must be between {MIN_VALUE} and {MAX_VALUE}. Current value: {kwargs['value']}")

    # Property getters and setters
    @property
    def resource_manager(self) -> Resource_Manager:
        """Get block resource_manager"""
        return self._resource_manager

    @resource_manager.setter
    def resource_manager(self, value: Resource_Manager) -> None:
        """Set block resource_manager"""
        self._validate_params(resource_manager=value)
        self._resource_manager = value

    @property
    def state(self) -> State:
        """Get block state"""
        return self._state

    @state.setter
    def state(self, value: State) -> None:
        """Set block state"""
        self._validate_params(state=value)
        self._state = value

    @property
    def block_class(self) -> str:
        """Get block class name"""
        return self.__class__.__name__

    @property
    def name(self) -> str:
        """Get block name"""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set block name"""
        self._validate_params(name=value)
        self._name = value

    @property
    def id(self) -> str:
        """Get block ID"""
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        """Set block ID"""
        if not isinstance(value, str):
            raise TypeError("id must be a string")
        self._id = value

    @property
    def description(self) -> str:
        """Get block description"""
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        """Set block description"""
        self._validate_params(description=value)
        self._description = value

    @property
    def side(self) -> str:
        """Get block side"""
        return self._side

    @side.setter
    def side(self, value: str) -> None:
        """Set block side"""
        self._validate_params(side=value)
        self._side = value

    @property
    def category(self) -> str:
        """Get block category"""
        return self._category

    @category.setter
    def category(self, value: str) -> None:
        """Set block category"""
        self._validate_params(category=value)
        self._category = value

    @property
    def sub_category(self) -> str:
        """Get block sub-category"""
        return self._sub_category

    @sub_category.setter
    def sub_category(self, value: str) -> None:
        """Set block sub-category"""
        self._validate_params(sub_category=value)
        self._sub_category = value

    @property
    def functionality(self) -> str:
        """Get block functionality"""
        return self._functionality

    @functionality.setter
    def functionality(self, value: str) -> None:
        """Set block functionality"""
        self._validate_params(functionality=value)
        self._functionality = value

    @property
    def value(self) -> int:
        """Get block value (int). Represents the level of strategic importance assigned by the campaign creator"""
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        """Set block value (int). Represents the level of strategic importance assigned by the campaign creator"""
        self._validate_params(value=value)
        self._value = value

    # Event management methods
    @property
    def events(self) -> List[Event]:
        """Get block events list"""
        return self._events

    @events.setter
    def events(self, value: List[Event]) -> None:
        """Set block events list"""
        if not isinstance(value, list):
            raise TypeError("events must be a list")
        if not all(isinstance(event, Event) for event in value):
            raise ValueError("All items in events must be Event objects")
        self._events = value

    def add_event(self, event: Event) -> None:
        """Add event to block"""
        if not isinstance(event, Event):
            raise TypeError("event must be an Event object")
        self._events.append(event)

    def get_last_event(self) -> Event:
        """Get most recent event"""
        if not self._events:
            raise IndexError("Events list is empty")
        return self._events[-1]

    def get_event(self, index: int) -> Event:
        """Get event by index"""
        if not isinstance(index, int):
            raise TypeError("index must be an integer")
        if index < 0 or index >= len(self._events):
            raise IndexError("Index out of events list range")
        return self._events[index]

    def remove_event(self, event: Event) -> None:
        """Remove event from block"""
        if not isinstance(event, Event):
            raise TypeError("event must be an Event object")
        if event not in self._events:
            raise ValueError("Event not found in events list")
        self._events.remove(event)

    # Asset management methods
    @property
    def cost(self) -> int:
        """Get total cost of all assets"""
        return sum(asset.cost for asset in self._assets.values() if asset.cost is not None)

    @property
    def assets(self) -> Dict[str, "Asset"]:
        """Get assets dictionary"""
        return self._assets

    @assets.setter
    def assets(self, value: Dict[str, "Asset"]) -> None:
        """Set assets dictionary"""
        if not isinstance(value, dict):
            raise TypeError("assets must be a dictionary")        
        if not all(validate_class(asset, "Asset") for asset in value.values()):
            raise ValueError(f"All values in assets must be Asset objects, actual{value!r}")
        self._assets = value


    def list_asset_keys(self) -> List[str]:
        """Get list of asset IDs"""
        return list(self._assets.keys())

    def get_asset(self, key: str) -> Optional["Asset"]:
        """Get asset by ID"""
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        return self._assets.get(key)

    def set_asset(self, key: str, asset: "Asset") -> None:
        """Add or update asset"""
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        if not hasattr(asset, '__class__') or asset.__class__.__name__ != 'Asset':
            raise TypeError("value must be an Asset object")
        self._assets[key] = asset
        asset.block = self  # Set back-reference

    def remove_asset(self, key: str) -> None:
        """Remove asset by ID"""
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        if key not in self._assets:
            raise KeyError(f"Asset with key '{key}' not found")
        del self._assets[key]

    # Region property
    @property
    def region(self) -> Optional["Region"]:
        """Get associated region"""
        return self._region

    @region.setter
    def region(self, value: Optional["Region"]) -> None:
        """Set associated region"""
        self._validate_params(region=value)
        self._region = value

    # Utility methods
    def __repr__(self) -> str:
        """Official string representation"""
        return (f"Block(name={self._name!r}, id={self._id!r}, side={self._side!r}, "
                f"category={self._category!r}, value={self._value!r})")

    def __str__(self) -> str:
        """User-friendly string representation"""
        return (f"Block {self._name} (ID: {self._id})\n"
                f"Side: {self._side}, Category: {self._category}\n"
                f"Value: {self._value}, Assets: {len(self._assets)}")

    def is_instance(self, obj: Any) -> bool:
        """Check if object is a Block instance"""
        return isinstance(obj, Block)

    def check_instance_list(self, objs: List[Any]) -> bool:
        """Check if all objects in list are Block instances"""
        return all(isinstance(obj, Block) for obj in objs) if isinstance(objs, list) else False

    @property
    def position(self) -> Optional[Point]:
        """Calculate centroid from asset positions"""
        if not self._assets:
            return None
        positions = [asset.position for asset in self._assets.values() if asset.position is not None]
        return mean_point(positions) if positions else None

    @property
    def morale(self) -> float:
        """Evaluate block morale"""
        return evaluateMorale(State.success_ratio[self], self.efficiency)

    @property
    def efficiency(self) -> float:
        """Calculate average asset efficiency"""
        if not self._assets:
            return 0.0
        efficiencies = [asset.efficiency for asset in self._assets.values()]
        return mean(efficiencies) if efficiencies else 0.0

    @property
    def balance_trade(self) -> float:
        """Calculate average asset trade balance"""
        if not self._assets:
            return 0.0
        balances = [asset.balance_trade for asset in self._assets.values()]
        return mean(balances) if balances else 0.0

    def is_military(self) -> bool:
        """Check if block is military"""
        return self._category == BLOCK_CATEGORY["Military"]

    def is_logistic(self) -> bool:
        """Check if block is logistic"""
        return self._category == BLOCK_CATEGORY["Logistic"]

    def is_civilian(self) -> bool:
        """Check if block is civilian"""
        return self._category == BLOCK_CATEGORY["Civilian"]
    
    def has_resource_manager(self):
        return self._resource_manager is not None

    @DeprecationWarning
    def enemy_side(self) -> str:
        """Determine enemy side"""
        return enemySide(self._side)
    
    def is_enemy(self, side: str):            
            return self._side == self.enemy_side(side)