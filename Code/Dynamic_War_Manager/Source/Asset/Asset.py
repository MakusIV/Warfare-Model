"""
Asset Class - Optimized Version

Represents unit -> group -> country -> coalition (DCS)
A Block can consist of different groups belonging to different countries of the same coalition
"""
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union, Tuple
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Utility.Utility import validate_class, setName, setId, mean_point
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.DataType.Event import Event
from Code.Dynamic_War_Manager.Source.DataType.Volume import Volume
from Code.Dynamic_War_Manager.Source.DataType.Threat import Threat
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload, PAYLOAD_ATTRIBUTES
from Code.Dynamic_War_Manager.Source.DataType.State import State
from sympy import Point3D
from dataclasses import dataclass

# LOGGING
logger = Logger(module_name=__name__, class_name='Asset')

@dataclass
class AssetParams:
    """Data class for holding asset parameters for validation"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    asset_type: Optional[str] = None
    functionality: Optional[str] = None
    cost: Optional[int] = None
    value: Optional[int] = None # rappresents relative value parameter refer to other asset's block
    resources_assigned: Optional[Payload] = None           # assigned consume payload - resource assigned for autoconsume
    resources_to_self_consume: Optional[Payload] = None           # requested consume payload - resource requeste for autoconsume
    payload: Optional[Payload] = None       # payload -payload resource
    production: Optional[Payload] = None       # payload -asset production resource
    position: Optional[Point3D] = None
    crytical: Optional[bool] = False
    repair_time: Optional[int] = 0
    role: Optional[str] = None
    health: Optional[int] = None # 0 -100

class Asset:
    def __init__(self, block: Block, name: Optional[str] = None, description: Optional[str] = None, 
                 category: Optional[str] = None, asset_type: Optional[str] = None, 
                 functionality: Optional[str] = None, cost: Optional[int] = None,
                 value: Optional[int] = None, resources_assigned: Optional[Payload] = None, 
                 resources_to_self_consume: Optional[Payload] = None, payload: Optional[Payload] = None, 
                 production: Optional[Payload] = None, position: Optional[Point3D] = None, volume: Optional[Volume] = None,
                 crytical: Optional[bool] = False, repair_time: Optional[int] = 0, 
                 role: Optional[str] = None, dcs_unit_data: Optional[Dict[str, Any]] = None):
        
        # Initialize properties
        self._name = name
        self._id = setId(name)
        self._description = description
        self._category = category
        self._asset_type = asset_type
        self._functionality = functionality
        self._health = None
        self._position = position
        self._cost = cost
        self._value = value
        self._payload_perc = None
        self._crytical = crytical
        self._repair_time = repair_time
        self._role = role
        self._dcs_unit_data = None
        self._events = []
        self._state = State()
        self._volume = volume
        self._block = block
        self._threat = None

        # Initialize payloads with defaults if None
        self._resources_assigned = resources_assigned if resources_assigned else Payload(goods=0, energy=0, hr=0, hc=0, hs=0, hb=0)
        self._resources_to_self_consume = resources_to_self_consume if resources_to_self_consume else Payload(goods=0, energy=0, hr=0, hc=0, hs=0, hb=0)
        self._payload = payload if payload else Payload(goods=0, energy=0, hr=0, hc=0, hs=0, hb=0)
        self._production = production if production else Payload(goods=0, energy=0, hr=0, hc=0, hs=0, hb=0)

        # Process DCS data if provided
        if dcs_unit_data:
            self.dcs_unit_data = dcs_unit_data

        # Validate all parameters
        self._validate_all_params(
            block=block, name=name, description=description, category=category,
            asset_type=asset_type, functionality=functionality, cost=cost,
            value=value, resources_assigned=self._resources_assigned, resources_to_self_consume=self._resources_to_self_consume, payload=self._payload,
            production=self._production, position=position, volume=volume, crytical=crytical,
            repair_time=repair_time, role=role, health=self._health,
            state=self._state
        )

    # Property getters and setters
    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, value: Optional[str]) -> None:
        self._validate_param('name', value, str)
        self._name = value

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: Optional[Union[str, int]]) -> None:
        if value:
            self._id = str(value)
        else:
            self._id = setId(self._name)

    @property
    def description(self) -> Optional[str]:
        return self._description

    @description.setter
    def description(self, value: Optional[str]) -> None:
        self._validate_param('description', value, str)
        self._description = value

    @property
    def category(self) -> Optional[str]:
        return self._category

    @category.setter
    def category(self, value: Optional[str]) -> None:
        self._validate_param('category', value, str)
        self._category = value

    @property
    def asset_type(self) -> Optional[str]:
        return self._asset_type

    @asset_type.setter
    def asset_type(self, value: Optional[str]) -> None:
        self._validate_param('asset_type', value, str)
        self._asset_type = value

    @property
    def functionality(self) -> Optional[str]:
        return self._functionality

    @functionality.setter
    def functionality(self, value: Optional[str]) -> None:
        self._validate_param('functionality', value, str)
        self._functionality = value

    @property
    def cost(self) -> Optional[int]:
        return self._cost

    @cost.setter
    def cost(self, value: Optional[int]) -> None:
        self._validate_param('cost', value, int)
        self._cost = value

    @property
    def value(self) -> Optional[int]:
        return self._value

    @value.setter
    def value(self, value: Optional[int]) -> None:
        self._validate_param('value', value, int)
        self._value = value

    @property
    def health(self) -> Optional[int]:
        return self._health

    @health.setter
    def health(self, value: Optional[int]) -> None:
        self._validate_param('health', value, int)
        self._health = value

    @property
    def crytical(self) -> Optional[bool]:
        return self._crytical

    @crytical.setter
    def crytical(self, value: Optional[bool]) -> None:
        self._validate_param('crytical', value, bool)
        self._crytical = value

    @property
    def repair_time(self) -> Optional[int]:
        return self._repair_time

    @repair_time.setter
    def repair_time(self, value: Optional[int]) -> None:
        self._validate_param('repair_time', value, int)
        self._repair_time = value

    @property
    def role(self) -> Optional[str]:
        return self._role

    @role.setter
    def role(self, value: Optional[str]) -> None:
        self._validate_param('role', value, str)
        self._role = value

    @property
    def position(self) -> Optional[Point3D]:
        return self._position

    @position.setter
    def position(self, value: Optional[Point3D]) -> None:
        self._validate_param('position', value, Point3D)
        self._position = value

    @property
    def state(self) -> State:
        return self._state

    @state.setter
    def state(self, value: State) -> None:
        self._validate_param('state', value, State)
        self._state = value

    @property
    def efficiency(self) -> float:
        value = float(self.balance_trade * self._health / 100) if self._health is not None else 0.0
        return value if value < 1 else 1

    @property
    def balance_trade(self) -> float:
        """Returns median value of sum of the acp.item / rcp.item ratio"""
        ratios = []
        
        for item in ['goods', 'energy', 'hr', 'hc', 'hs', 'hb']:
            rcp_val = getattr(self.resources_to_self_consume, item, 0)
            if rcp_val > 0:
                acp_val = getattr(self.resources_assigned, item, 0)
                ratios.append(acp_val / rcp_val)
        
        return sum(ratios) / len(ratios) if ratios else 0.0

    @property
    def resources_assigned(self) -> Payload:
        return self._resources_assigned

    @resources_assigned.setter
    def resources_assigned(self, value: Payload) -> None:
        self._validate_param('resources_assigned', value, Payload)
        self._resources_assigned = value

    @property
    def resources_to_self_consume(self) -> Payload:
        return self._resources_to_self_consume

    @resources_to_self_consume.setter
    def resources_to_self_consume(self, value: Payload) -> None:
        self._validate_param('resources_to_self_consume', value, Payload)
        self._resources_to_self_consume = value

    @property
    def payload(self) -> Payload:
        return self._payload

    @payload.setter
    def payload(self, value: Payload) -> None:
        self._validate_param('payload', value, Payload)
        self._payload = value

    @property
    def production(self) -> Payload:
        """Returns the nominal production of the asset"""
        return self._production

    @production.setter
    def production(self, value: Payload) -> None:
        """Sets the nominal production of the asset"""
        self._validate_param('production', value, Payload)
        self._production = value

    @property
    def volume(self) -> Optional[Volume]:
        return self._volume

    @volume.setter
    def volume(self, value: Optional[Volume]) -> None:
        self._validate_param('volume', value, Volume)
        self._volume = value

    @property
    def threat(self) -> Optional[Threat]:
        return self._threat

    @threat.setter
    def threat(self, value: Optional[Threat]) -> None:
        self._validate_param('threat', value, Threat)
        self._threat = value

    @property
    def block(self) -> Block:
        return self._block

    @block.setter
    def block(self, value: Block) -> None:
        self._validate_param('block', value, Block)
        if value and value.get_asset(self._id) and value.get_asset(self._id).id != self._id:
            raise ValueError("Association Incongruence: Asset id conflict in Block association")
        self._block = value

    @property
    def events(self) -> List[Event]:
        return self._events

    @events.setter
    def events(self, value: List[Event]) -> None:
        if not isinstance(value, list):
            raise ValueError("Events must be a list")
        self._events = value

    @property
    def dcs_unit_data(self) -> Optional[Dict[str, Any]]:
        return self._dcs_unit_data

    @dcs_unit_data.setter
    def dcs_unit_data(self, value: Optional[Dict[str, Any]]) -> None:
        if value is None:
            self._dcs_unit_data = None
            return

        is_valid, message = self._validate_dcs_data(value)
        if not is_valid:
            raise ValueError(message)

        self._dcs_unit_data = value
        self._name = value.get("unit_name")
        self._id = str(value.get("unitId")) if value.get("unitId") else self._id
        if all(k in value for k in ("unit_x", "unit_y", "unit_alt")):
            self._position = Point3D(value["unit_x"], value["unit_y"], value["unit_alt"])
        self._health = value.get("unit_health")

    # Event management methods
    def add_event(self, event: Event) -> None:
        if not isinstance(event, Event):
            raise ValueError("Event must be an Event object")
        self._events.append(event)

    def get_last_event(self) -> Event:
        if not self._events:
            raise IndexError("No events available")
        return self._events[-1]

    def get_event(self, index: int) -> Event:
        if index >= len(self._events) or index < 0:
            raise IndexError("Event index out of range")
        return self._events[index]

    def remove_event(self, event: Event) -> None:
        if event not in self._events:
            raise ValueError("Event not found in events list")
        self._events.remove(event)

    # Consumption methods
    def consume(self) -> Dict[str, Optional[bool]]:
        """Reduce acp of rcp payload quantity"""
        return self._consume(self.resources_to_self_consume)

    def _consume(self, cons: Payload) -> Dict[str, Optional[bool]]:
        """Internal method to reduce acp of cons payload quantity"""
        self._validate_param('cons', cons, Payload)
        
        results = {item: None for item in PAYLOAD_ATTRIBUTES}
        
        for item in results.keys():
            cons_val = getattr(cons, item)
            if cons_val:
                acp_val = getattr(self.resources_assigned, item)
                if acp_val >= cons_val:
                    setattr(self.resources_assigned, item, acp_val - cons_val)
                    results[item] = True
                else:
                    results[item] = False
        
        return results
    

    # l'asset produce nella unità di tempo le risorse definite con self.production. 
    # Tramite self.produce() il Payload viene incrementato ad ogni unità di tempo. 
    # La richiesta delle risorse prodotte è fissata alla produzione nominale dell'asset.
        
    def get_production(self) -> Payload:
        """get resources based on nominal production and stored in asset payload"""
        
        items = ['goods', 'energy', 'hr', 'hc', 'hs', 'hb']

        delivery = Payload()

        for item in PAYLOAD_ATTRIBUTES:
            request_production_item = getattr(self.production, item)

            if request_production_item > 0:
                maximum_production_item = getattr(self.payload, item)

                if maximum_production_item > request_production_item:
                    setattr(delivery, item, request_production_item)
                    setattr(self.payload, item, maximum_production_item - request_production_item)                    
                
                else:
                    setattr(delivery, item, maximum_production_item)
                    setattr(self.payload, item, 0)                    
        
        return delivery

    def produce(self) -> Dict[str, Optional[bool]]:
        """Produce resources based on the production request and asset efficiency. Production is added to the existing payload"""
        results = {item: None for item in PAYLOAD_ATTRIBUTES}

        for item in PAYLOAD_ATTRIBUTES:
            request_production_item = getattr(self.production, item)

            if request_production_item > 0:
                item_produced = request_production_item * self.efficiency
                setattr(self.payload, item, getattr(self.payload, item) + item_produced)
                results[item] = True
            
            else:
                results[item] = False
        return results
                

    # Utility methods
    def is_military(self) -> bool:
        return self.block.isMilitary

    def is_logistic(self) -> bool:
        return self.block.isLogistic

    def is_civilian(self) -> bool:
        return self.block.isCivilian

    def threat_volume(self) -> None:
        """Calculate Threat_Volume from asset Threat_Volume"""
        # Implementation pending
        pass

    # Validation methods
    def _validate_all_params(self, **kwargs) -> None:
        """Validate all input parameters"""
        type_checks = {
            'name': str,
            'description': str,
            'category': str,
            'asset_type': str,
            'functionality': str,
            'cost': int,
            'value': int,
            'position': Point3D,
            'block': Block,
            'volume': Volume,
            'resources_assigned': Payload,
            'resources_to_self_consume': Payload,
            'payload': Payload,
            'production': Payload,
            'repair_time': int,
            'role': str,
            'health': int,
            'crytical': bool,
            'state': State
        }
        
        for param, value in kwargs.items():
            if value is not None and param in type_checks:
                self._validate_param(param, value, type_checks[param])

    def _validate_param(self, param_name: str, value: Any, expected_type: type) -> None:
        """Validate a single parameter"""
        if value is not None and not isinstance(value, expected_type):
            raise TypeError(f"Invalid type for {param_name}. Expected {expected_type.__name__}, got {type(value).__name__}")

    def _validate_dcs_data(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate DCS unit data structure"""
        checks = [
            ("unit_name", str),
            ("unit_type", str),
            ("unitId", int),
            ("unit_frequency", float),
            ("unit_x", float),
            ("unit_y", float),
            ("unit_alt", float),
            ("unit_alt_type", str),
            ("unit_health", int)
        ]
        
        for field, field_type in checks:
            if field in data and not isinstance(data[field], field_type):
                return False, f"Bad Arg: {field} must be a {field_type.__name__}"
        
        return True, "DCS data validation passed"