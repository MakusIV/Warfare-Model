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
    resources_needed: Optional[Payload] = None,    
    warehouse: Optional[Payload] = None

class Resource_Manager:
    def __init__(self, block: "Block", clients: Optional[Dict[str, "Block"]] = None, server: Optional[Dict[str, "Block"]] = None,                  
                 warehouse: Optional[Payload] = None):
    
        # Initialize properties
        self._block = block
        self._clients = clients
        self._server = server        
        self._warehouse = warehouse if warehouse else Payload()  # Initialize warehouse with empty payload if not provided
        self._resources_to_self_consume = self._evaluate_resources_to_self_consume() # resources requested based on sum of assets request of this block: used to evaluate consume
        self._resources_needed = self._evaluate_effective_resources_needed()  # effective resources for server's request: evaluation based on asset request and warehouse availability: used to evaluate delivery resources at clients        
        
        # Validate all parameters
        self._validate_all_params(
            block = block, clients = clients, server = server, warehouse = warehouse
        )



    def _evaluate_clients_priority(self) -> Dict[str, float]:
        """Evaluate relative priority based on the sum of block's priority"""
        
        # get from region the block's priority
        region = self.block.region if self.block.region else None
        
        if not region:
            raise ValueError("Block region is not set. Cannot evaluate server priority.")
        clients_priority = {}        
        region_blocks_priority = region.blocks_priority

        # get client's priotity if client is in region block list
        for client in self._clients.values():            
            priority = region_blocks_priority.get(client.id)
            
            if priority is None:
                logger.warning(f"Server {client.id} not found in region block list. Cannot evaluate priority.")
                continue
            else:                
                clients_priority.append(key = client.id, value = priority)
        
        return clients_priority

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
    def resources_needed(self) -> Payload:
        return self._resources_needed

    @property
    def resources_to_self_consume(self) -> Payload:
        return self._request
    
    @property
    def warehouse(self) -> Payload:
        return self._warehouse

    @warehouse.setter
    def warehouse(self, value: Payload) -> None:
        self._validate_param('warehouse', value, Payload)
        self._warehouse = value

        
    def _evaluate_resources_to_self_consume(self) -> Payload:
        """Evaluate asset resources block"""                
        resources = Payload()
        
        for asset  in self.block.assets:            
            resources += asset.resources_to_self_consume if asset.resources_to_self_consume else Payload()
        return resources

    # Server client association
    # NOTE: to avoid cycles client-server associations are managed by the client calls with set_server & remove_server methods

    def consume(self) -> bool:
        """Consume resources from warehouse based on request and warehouse availability"""

        if not self._resources_to_self_consume or not self._warehouse:        
            raise ValueError("resources_to_self_consume and warehouse must be set before consuming resources")
        
        if self._warehouse < self._resources_to_self_consume:
            logger.warning(f"Warehouse {self._warehouse!r} is less than request {self._resources_to_self_consume!r}. Cannot consume resources.")
            return False

        self._warehouse -= self._resources_to_self_consume  # Update warehouse after consuming resources
        return True  # Return True to indicate successful consumption of resources


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
    
    def _evaluate_effective_resources_needed(self) -> Payload:
        """resources needed to request from servers."""
        
        if not self._resources_to_self_consume or not self._warehouse:
            raise ValueError("resources_to_self_consume and warehouse must be set before receiving resources")
        
        assessment = Payload()  # Initialize request payload        
        autonomy = self._warehouse.division(self._resources_to_self_consume) # Calculate autonomy based on warehouse avalability and request
        
        # Determine request priority based on warehouse avalability and request
        param =("goods", "energy", "hr", "hc", "hs", "hb")
        for item in param:
            if autonomy[item] < 2:
                assessment[item] = self._resources_to_self_consume[item]  # If autonomy is less than 2, use full request
            elif 2 <= autonomy[item] < 3:
                assessment[item] = self._resources_to_self_consume[item] * 0.5
            elif 3 <= autonomy[item] < 5:
                assessment[item] = self._resources_to_self_consume[item] * 0.25
            else:
                assessment[item] = self._resources_to_self_consume[item] * 0.1
    
        return assessment  # Return the assessed necessary resources based on request and warehouse

    def receive(self, payload: Payload) -> None:
        """Receive resources from server and update warehouse"""

        if not self._validate_param('payload', payload, Payload):
            raise TypeError("payload must be a Payload object")

        if not self._warehouse:
            raise ValueError("warehouse must be set before receiving resources")
                
        self._warehouse += payload# Update warehouse with received payload

        


    
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
        
        if not cl_rm: # il client non ha il resource manager raise exception
            raise Exception(f"Anomaly - client: {client!r} hasn't a resource manager. Resource client wasn't added")
        if cl_rm.get_server[self.id] != self: #la lista dei server presente nel resource manager del client non ha questo server
            raise Exception(f"Anomaly - missing server: {self!r} in resource manager server list of this client {client!r}")
        
        del self._clients[key]
        # back reference setting only by client call with set_server method

    def delivery(self) -> None:
        """Deliver resources to clients based on their strategic and tactical priority and request"""
        if not self.resources_to_self_consume or not self.warehouse:
            raise ValueError("Request and warehouse must be set before delivery resources")
        
        clients_priority = self._evaluate_clients_priority()  # clients_priority list for delivery based on block's priority: strategic priority
        delivery_unit = self.warehouse.division(self.warehouse, sum(clients_priority.values()) ) # Calculate delivery unit based on warehouse avalaiability and clients' priorities
        
        # Calculate request priority based on clients priorities
        for client in self.clients.values():
            request = client.resource_manager.resources_needed  # Assess necessary resources based on request and warehouse
            max_delivery = delivery_unit * clients_priority[client.id]  # Calculate delivery for each client based on its priority            
            
            param =("goods", "energy", "hr", "hc", "hs", "hb")
            
            for item in param:
                
                if request[item] < max_delivery[item]:  # If request is less than max delivery, use request as delivery
                    delivery = request  # If request is less than max delivery, use request as delivery
                else:
                    delivery[item] = max_delivery[item]  # Otherwise, use max delivery as delivery
                
            receive_result = client.resource_manager.receive(delivery)  # request to server for resources based on request and priority
            
            if receive_result:
                logger.info(f"Delivery successful for client {client.id} with payload {delivery!r}")
                warehouse -= delivery  # Update warehouse after successful delivery
            else:
                logger.info(f"Delivery failed for client {client.id} with payload {delivery!r}")
                

    
        
    # Validation methods
    def _validate_all_params(self, **kwargs) -> None:
        """Validate all input parameters"""
        type_checks = {            
            'block': (type(None)), # accetta solo None durante il runtime, altrimenti genera errore perchè Block non è importata e non deve esserlo: l'utilizzo dei suoi metodi è cmq garantito dall'oggetto importato             
            'clients': Dict[str, Payload],
            'server': Dict[str, Payload],
            'warehouse': Payload,            
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