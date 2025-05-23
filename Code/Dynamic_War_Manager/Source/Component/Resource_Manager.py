"""
Resource_Manager Class

Represents a Block's component for resource management

"""
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union, Tuple
from Code.Dynamic_War_Manager.Source.Utility.Utility import validate_class, setName, setId, mean_point
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.DataType.Event import Event
from Code.Dynamic_War_Manager.Source.DataType.Volume import Volume
from Code.Dynamic_War_Manager.Source.DataType.Threat import Threat
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload
from Code.Dynamic_War_Manager.Source.DataType.State import State
from sympy import Point3D
from dataclasses import dataclass

if TYPE_CHECKING:
    from Code.Dynamic_War_Manager.Source.Block.Block import Block

# LOGGING
logger = Logger(module_name=__name__, class_name='Resource_Manager')

@dataclass
class Resource_Manager_Params:
    """Data class for holding Resource Manager parameters for validation"""
    clients: Optional[Dict[str, "Block"]] = None, 
    server: Optional[Dict[str, "Block"]] = None,
    request_for_consume: Optional[Payload] = None, 
    assigned_for_consume: Optional[Payload] = None, 
    request: Optional[Payload] = None, 
    storage: Optional[Payload] = None

class Resource_Manager:
    def __init__(self, block: "Block", 
                 clients: Optional[Dict[str, "Block"]] = None, server: Optional[Dict[str, "Block"]] = None,
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

    # Block property
    @property
    def block(self) -> Optional["Block"]:
        """Get associated block"""
        return self._block

    @block.setter
    def block(self, value: Optional["Block"]) -> None:
        """Set associated block"""
        self._validate_params(block=value)
        self._region = value

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

    @property
    def request(self) -> Payload:
        return self._request

    @request.setter
    def request(self, value: Payload) -> None:
        self._validate_param('request', value, Payload)
        self._request = value

    def evaluate_request(self):
        request = Payload()
        
        for asset  in self.block.assets:
            request = request.sum(request, asset.requested_for_consume)
        return request

    # Server client association
    # NOTE: to avoid cycles client-server associations are managed by the client calls with set_server & remove_server methods


    # SERVER MANAGEMENT: This section seeing this Block like a client of all server enlisted
    @property
    def server(self) -> Dict[str, "Block"]:# {block, priority, ....}˘ o lascio solo block (semplificando parecchio) e calcolo ls priority in runtime per l'assegnazione pesata dellem risorse?}
        """Get server dictionary"""
        return self._server

    @server.setter
    def server(self, value: Dict[str, "Block"]) -> None:
        """Set server dictionary"""
        if not isinstance(value, dict):
            raise TypeError("server must be a dictionary")        
        if not all(validate_class(client, "Block") for client in value.values()):
            raise ValueError(f"All values in server must be Block objects, actual{value!r}")
        self._server = value

    def list_server_keys(self) -> List[str]:
        """Get list of server IDs"""
        return list(self._server.keys())

    def get_server(self, key: str) -> Optional["Block"]:
        """Get server by ID"""
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        return self._server.get(key)

    def set_server(self, key: str, server: "Block") -> None:
        """Add or update server"""
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        if not hasattr(server, '__class__') or server.__class__.__name__ != 'Block':
            raise TypeError("value must be an Block object")
        if server.has_resource_manager():
            self._server[key] = server
            server.resource_manager.set_client(self.id, self)  # Set back-reference (back reference setting only by client call with set_server method)
        else:
            raise Exception(f"block: {server!r} hasn't resource manager. Resource server wasn't added")

    def remove_server(self, key: str) -> None:
        """Remove client by ID"""
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        if key not in self._server:
            raise KeyError(f"Block with key '{key}' not found")
        deleted_server = self._server[key]
        if deleted_server.has_resource_manager():
            deleted_server.resource_manager.remove_client(deleted_server.id) # Delete back-reference (back reference setting only by client call with set_server method)
            del self._server[key]
        else:
            raise Exception(f"Anomaly: this client: {self.block!r} has a reference in its resource manager while the server: {deleted_server!r} does not have its own resource manager. Resource server wasn't added")
    
    def receive(self) -> None:

        for server in self.server:
            payload = server.resource_manager.delivery(self.request)
            self.put_in_storage(payload)


    
    # CLIENT MANAGEMENT: This section seeing this Block like a server of all client enlisted
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
        cl_rm = client.resource_manager

        if not cl_rm: # il client non ha il resource manager
            raise Exception(f"Anomaly - client: {client!r} hasn't a resource manager. Resource client wasn't added")
        if cl_rm.get_server[self.id] != self: #la lista dei server presente nel resource manager del client non ha questo server
            raise Exception(f"Anomaly - missing server: {self!r} in resource manager server list of this client {client!r}")
        
        self._clients[key] = client
        # back reference setting only by client call with set_server method

    def remove_client(self, key: str) -> None:
        """Remove client by ID"""
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        if key not in self._clients:
            raise KeyError(f"Block with key '{key}' not found")          

        client = self._clients[key]
        cl_rm = client.resource_manager
        
        if not cl_rm: # il client non ha il resource manager
            raise Exception(f"Anomaly - client: {client!r} hasn't a resource manager. Resource client wasn't added")
        if cl_rm.get_server[self.id] != self: #la lista dei server presente nel resource manager del client non ha questo server
            raise Exception(f"Anomaly - missing server: {self!r} in resource manager server list of this client {client!r}")
        
        del self._clients[key]
        # back reference setting only by client call with set_server method

    def delivery(self, payload: Payload, priority: Optional[Union[str, int, float]]) -> None:
        pass
        
        

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
            'block': (type(None)), # accetta solo None durante il runtime, altrimenti genera errore perchè Block non è importata e non deve esserlo: l'utilizzo dei suoi metodi è cmq garantito dall'oggetto importato             
            'request_for_consume': Payload,
            'assigned_for_consume': Payload,
            'request': Payload,
            'storage': Payload,            
        }
        
        for param, value in kwargs.items():            
            if value is not None and param in type_checks:
                if param == 'block':
                    if not (value is None or getattr(value, '__class__', {}).__name__ == 'Block'):
                        raise TypeError(f"{param} must be None or a Block object")
                    continue
                else:
                    self._validate_param(param, value, type_checks[param])

    def _validate_param(self, param_name: str, value: Any, expected_type: type) -> None:
        """Validate a single parameter"""
        if value is not None and not isinstance(value, expected_type):
            raise TypeError(f"Invalid type for {param_name}. Expected {expected_type.__name__}, got {type(value).__name__}")

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