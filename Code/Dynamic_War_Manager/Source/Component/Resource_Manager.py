"""
Resource_Manager Class

Represents a Block's component for resource management

"""
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union, Tuple
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Utility.Utility import validate_class, setName, setId, mean_point
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.DataType.Event import Event
from Code.Dynamic_War_Manager.Source.DataType.Volume import Volume
from Code.Dynamic_War_Manager.Source.DataType.Threat import Threat
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload
from Code.Dynamic_War_Manager.Source.DataType.State import State
from sympy import Point3D
from dataclasses import dataclass

# LOGGING
logger = Logger(module_name=__name__, class_name='Resource_Manager')

@dataclass
class Resource_Manager_Params:
    """Data class for holding Resource Manager parameters for validation"""
    clients: Optional[Dict[Block, Any]] = None, 
    server: Optional[Dict[Block, Any]] = None,
    request_for_consume: Optional[Payload] = None, 
    assigned_for_consume: Optional[Payload] = None, 
    request: Optional[Payload] = None, 
    storage: Optional[Payload] = None

class Resource_Manager:
    def __init__(self, block: Block, 
                 clients: Optional[Dict[Block, Any]] = None, server: Optional[Dict[Block, Any]] = None,
                 request_for_consume: Optional[Payload] = None, assigned_for_consume: Optional[Payload] = None, 
                 request: Optional[Payload] = None, storage: Optional[Payload] = None):
    
        # Initialize properties
        self._block = block
        self._clients = clients
        self._server = server
        self._request_for_consume = request_for_consume
        self._assigned_for_consume = assigned_for_consume
        self._request = request
        self._storage = storage
        

        # Validate all parameters
        self._validate_all_params(
            block=block, clients=clients, server=server, request_for_consume=request_for_consume,
            assigned_for_consume=assigned_for_consume, request=request, storage=storage
        )

    
    @property
    def request_for_consume(self) -> Payload:
        return self._request_for_consume

    @request_for_consume.setter
    def request_for_consume(self, value: Payload) -> None:
        self._validate_param('request_for_consume', value, Payload)
        self._request_for_consume = value

    @property
    def assigned_for_consume(self) -> Payload:
        return self._assigned_for_consume

    @assigned_for_consume.setter
    def assigned_for_consume(self, value: Payload) -> None:
        self._validate_param('assigned_for_consume', value, Payload)
        self._assigned_for_consume = value

    @property
    def storage(self) -> Payload:
        return self._storage

    @storage.setter
    def storage(self, value: Payload) -> None:
        self._validate_param('storage', value, Payload)
        self._storage = value

    # {block, priority, ....}˘ o lascio solo block (semplificando parecchio) e calcolo ls priority in runtime per l'assegnazione pesata dellem risorse?}
    @property
    def clients(self) -> Dict[str, "Block"]:# {block, priority, ....}˘ o lascio solo block (semplificando parecchio) e calcolo ls priority in runtime per l'assegnazione pesata dellem risorse?}
        """Get clients dictionary"""
        return self._clients

    @clients.setter
    def clients(self, value: Dict[str, "Block"]) -> None:
        """Set clients dictionary"""
        if not isinstance(value, dict):
            raise TypeError("clients must be a dictionary")        
        if not all(validate_class(client, "Block") for client in value.values()):
            raise ValueError(f"All values in clients must be Block objects, actual{value!r}")
        self._clients = value


    def list_client_keys(self) -> List[str]:
        """Get list of client IDs"""
        return list(self._clients.keys())

    def get_client(self, key: str) -> Optional["Block"]:
        """Get client by ID"""
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        return self._clients.get(key)

    def set_client(self, key: str, client: "Block") -> None:
        """Add or update client"""
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        if not hasattr(client, '__class__') or client.__class__.__name__ != 'Block':
            raise TypeError("value must be an Block object")
        self._clients[key] = client
        client.block = self  # Set back-reference

    def remove_client(self, key: str) -> None:
        """Remove client by ID"""
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        if key not in self._clients:
            raise KeyError(f"Block with key '{key}' not found")
        del self._clients[key]

    
    # Consumption methods
    def consume(self) -> Dict[str, Optional[bool]]:
        """Reduce acp of rcp payload quantity"""
        return self._consume(self.rcp)

    def _consume(self, cons: Payload) -> Dict[str, Optional[bool]]:
        """Internal method to reduce acp of cons payload quantity"""
        self._validate_param('cons', cons, Payload)
        
        results = {item: None for item in ['goods', 'energy', 'hr', 'hc', 'hs', 'hb']}
        
        for item in results.keys():
            cons_val = getattr(cons, item)
            if cons_val:
                acp_val = getattr(self.acp, item)
                if acp_val >= cons_val:
                    setattr(self.acp, item, acp_val - cons_val)
                    results[item] = True
                else:
                    results[item] = False
        
    

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
            'acp': Payload,
            'rcp': Payload,
            'payload': Payload,
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