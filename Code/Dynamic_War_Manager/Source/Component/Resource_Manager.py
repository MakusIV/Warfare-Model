"""
Resource_Manager Class (Optimized)

Represents a Block's component for resource management

Main improvements:
- Fixed syntax and logic errors
- Enhanced exception handling
- Optimized calculation methods
- Added comprehensive documentation
- Removed code redundancy
- Improved parameter validation
"""
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union, Tuple
from Code.Dynamic_War_Manager.Source.Utility.Utility import validate_class, setName, setId, mean_point
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload
from dataclasses import dataclass
from collections import defaultdict

if TYPE_CHECKING:
    from Code.Dynamic_War_Manager.Source.Block.Block import Block

# LOGGING
logger = Logger(module_name=__name__, class_name='Resource_Manager')

@dataclass
class Resource_Manager_Params:
    """Data class for Resource Manager parameters for validation"""
    clients: Optional[Dict[str, "Block"]] = None
    server: Optional[Dict[str, "Block"]] = None
    resources_needed: Optional[Payload] = None    
    warehouse: Optional[Payload] = None

class Resource_Manager:
    """
    Manages resources for a Block, including client-server relationships
    and priority-based resource distribution.
    """
    
    # Supported resource parameters
    RESOURCE_PARAMS = ("goods", "energy", "hr", "hc", "hs", "hb")
    
    # Autonomy thresholds for calculating needed resources
    AUTONOMY_THRESHOLDS = {
        (0, 2): 1.0,      # Autonomy < 2: full request
        (2, 3): 0.5,      # Autonomy 2-3: 50% of request
        (3, 5): 0.25,     # Autonomy 3-5: 25% of request
        (5, float('inf')): 0.1  # Autonomy > 5: 10% of request
    }

    def __init__(self, block: "Block", clients: Optional[Dict[str, "Block"]] = None, 
                 server: Optional[Dict[str, "Block"]] = None, warehouse: Optional[Payload] = None):
        """
        Initialize the Resource Manager.
        
        Args:
            block: The Block associated with this resource manager
            clients: Dictionary of clients {id: Block}
            server: Dictionary of servers {id: Block}
            warehouse: Payload representing the resource warehouse
        """
        if block is None:
            raise ValueError("block parameter must be provided")

        # Initial parameter validation
        self._validate_all_params(block=block, clients=clients, server=server, warehouse=warehouse)
        
        # Property initialization
        self._block = block
        self._clients = clients or {}
        self._server = server or {}
        self._warehouse = warehouse or Payload()
        
        # Resource calculation (lazy loading to avoid unnecessary computations)
        self._resources_to_self_consume = None
        self._resources_needed = None
        
    # === BLOCK PROPERTIES ===
    
    @property
    def block(self) -> Optional["Block"]:
        """Get the associated Block"""
        return self._block

    @block.setter
    def block(self, value: Optional["Block"]) -> None:
        """Set the associated Block"""
        self._validate_block_param(value)
        self._block = value
        # Reset cache when block changes
        self._invalidate_resource_cache()

    @property
    def resources_needed(self) -> Payload:
        """Get needed resources (calculated)"""
        if self._resources_needed is None:
            self._resources_needed = self._evaluate_effective_resources_needed()
        return self._resources_needed

    @property
    def resources_to_self_consume(self) -> Payload:
        """Get resources for self-consumption (calculated)"""
        if self._resources_to_self_consume is None:
            self._resources_to_self_consume = self._evaluate_resources_to_self_consume()
        return self._resources_to_self_consume
    
    @property
    def warehouse(self) -> Payload:
        """Get the resource warehouse"""
        return self._warehouse

    @warehouse.setter
    def warehouse(self, value: Payload) -> None:
        """Set the resource warehouse"""
        self._validate_param('warehouse', value, "Payload")
        self._warehouse = value
        # Reset cache when warehouse changes
        self._invalidate_resource_cache()

    # === SERVER MANAGEMENT (this Block as client) ===
    
    @property
    def server(self) -> Dict[str, "Block"]:
        """Get the server dictionary"""
        return self._server.copy()  # Return a copy for safety

    @server.setter
    def server(self, value: Dict[str, "Block"]) -> None:
        """Set the server dictionary"""
        if not isinstance(value, dict):
            raise TypeError("server must be a dictionary")
        
        for server_id, server_block in value.items():
            if not isinstance(server_id, str):
                raise TypeError("Server dictionary keys must be strings")
            if not self._is_valid_block(server_block):
                raise ValueError(f"All values in server must be Block objects, current: {server_block!r}")
        
        self._server = value.copy()

    def list_server_keys(self) -> List[str]:
        """Get list of server IDs"""
        return list(self._server.keys())

    def get_server(self, key: str) -> Optional["Block"]:
        """Get server by ID"""
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        return self._server.get(key)

    def set_server(self, key: str, server: "Block") -> None:
        """Add or update a server"""
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        
        if not self._is_valid_block(server):
            raise TypeError("value must be a Block object")
        
        if not server.has_resource_manager():
            raise ValueError(f"Block {server!r} does not have a resource manager")
        
        # Update bidirectional reference
        self._server[key] = server
        try:
            server.resource_manager.set_client(self.block.id, self.block)
        except Exception as e:
            # Rollback on error
            del self._server[key]
            raise RuntimeError(f"Error setting bidirectional reference: {e}")

    def remove_server(self, key: str) -> None:
        """Remove server by ID"""
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        
        if key not in self._server:
            raise KeyError(f"Block with key '{key}' not found")
        
        deleted_server = self._server[key]
        
        if not deleted_server.has_resource_manager():
            raise RuntimeError(f"Anomaly: client {self.block!r} has reference while server {deleted_server!r} has no resource manager")
        
        # Remove bidirectional reference
        try:
            deleted_server.resource_manager.remove_client(self.block.id)
            del self._server[key]
        except Exception as e:
            raise RuntimeError(f"Error removing bidirectional reference: {e}")

    # === CLIENT MANAGEMENT (this Block as server) ===
    
    @property
    def clients(self) -> Dict[str, "Block"]:
        """Get the client dictionary"""
        return self._clients.copy()  # Return a copy for safety

    @clients.setter
    def clients(self, value: Dict[str, "Block"]) -> None:
        """Set the client dictionary"""
        if not isinstance(value, dict):
            raise TypeError("clients must be a dictionary")
        
        for client_id, client_block in value.items():
            if not isinstance(client_id, str):
                raise TypeError("Client dictionary keys must be strings")
            if not self._is_valid_block(client_block):
                raise ValueError(f"All values in clients must be Block objects, current: {client_block!r}")
        
        self._clients = value.copy()

    def list_client_keys(self) -> List[str]:
        """Get list of client IDs"""
        return list(self._clients.keys())

    def get_client(self, key: str) -> Optional["Block"]:
        """Get client by ID"""
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        return self._clients.get(key)

    def set_client(self, key: str, client: "Block") -> None:
        """Add or update a client (called automatically by set_server)"""
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        
        if not self._is_valid_block(client):
            raise TypeError("value must be a Block object")
        
        client_rm = client.resource_manager
        if not client_rm:
            raise ValueError(f"Anomaly - client {client!r} does not have a resource manager")
        
        # Verify bidirectional reference consistency
        if client_rm.get_server(self.block.id) != self.block:
            raise ValueError(f"Anomaly - server {self.block!r} missing from client {client!r} server list")
        
        self._clients[key] = client

    def remove_client(self, key: str) -> None:
        """Remove client by ID (called automatically by remove_server)"""
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        
        if key not in self._clients:
            raise KeyError(f"Block with key '{key}' not found")

        client = self._clients[key]
        client_rm = client.resource_manager
        
        if not client_rm:
            raise ValueError(f"Anomaly - client {client!r} does not have a resource manager")
        
        # Verify bidirectional reference consistency
        if client_rm.get_server(self.block.id) != self.block:
            raise ValueError(f"Anomaly - server {self.block!r} missing from client {client!r} server list")
        
        del self._clients[key]

    # === RESOURCE OPERATIONS ===
    
    def consume(self) -> bool:
        """
        Consume resources from warehouse based on request.
        
        Returns:
            bool: True if consumption was successful, False otherwise
        """
        try:
            resources_needed = self.resources_to_self_consume
            
            if not resources_needed or not self._warehouse:
                raise ValueError("resources_to_self_consume and warehouse must be set")
            
            if self._warehouse < resources_needed:
                logger.warning(f"Warehouse {self._warehouse!r} insufficient for request {resources_needed!r}")
                return False

            self._warehouse -= resources_needed
            logger.info(f"Consumption completed: {resources_needed!r}")
            
            # Invalidate cache after consumption
            self._invalidate_resource_cache()
            return True
            
        except Exception as e:
            logger.error(f"Error during resource consumption: {e}")
            return False

    def receive(self, payload: Payload) -> bool:
        """
        Receive resources from a server and update warehouse.
        
        Args:
            payload: Resources to receive
            
        Returns:
            bool: True if reception was successful, False otherwise
        """        

        try:            
            self._validate_param("payload", payload, "Payload")

            if not self._warehouse:
                raise ValueError("warehouse must be set before receiving resources")
                
            self._warehouse += payload
            logger.info(f"Received resources: {payload!r}")
            
            # Invalidate cache after reception
            self._invalidate_resource_cache()
            return True
            
        except Exception as e:
            logger.error(f"Error during resource reception: {e}")
            return False

    def delivery(self) -> Dict[str, bool]:
        """
        Distribute resources to clients based on strategic and tactical priority.
        
        Returns:
            Dict[str, bool]: Delivery result for each client
        """
        if not self.resources_to_self_consume or not self.warehouse:
            raise ValueError("Request and warehouse must be set before resource distribution")
        
        try:
            clients_priority = self._evaluate_clients_priority()
            if not clients_priority:
                logger.warning("No clients with valid priority found")
                return {}
            
            delivery_results = {}
            total_priority = sum(clients_priority.values())
            
            # Calculate distribution unit based on warehouse and priorities
            available_resources = self.warehouse.copy()
            
            for client_id, client in self._clients.items():
                if client_id not in clients_priority:
                    logger.warning(f"Client {client_id} has no valid priority")
                    delivery_results[client_id] = False
                    continue
                
                try:
                    client_priority = clients_priority[client_id]
                    client_request = client.resource_manager.resources_needed
                    
                    # Calculate maximum distribution based on priority
                    priority_ratio = client_priority / total_priority
                    max_delivery = available_resources * priority_ratio
                    
                    # Determine actual delivery (minimum between request and maximum distribution)
                    actual_delivery = Payload()
                    for param in self.RESOURCE_PARAMS:
                        setattr(actual_delivery, param, min( getattr(client_request, param), getattr(max_delivery, param) ))
                    
                    # Perform delivery
                    delivery_success = client.resource_manager.receive(actual_delivery)
                    
                    if delivery_success:
                        self._warehouse -= actual_delivery
                        available_resources -= actual_delivery
                        logger.info(f"Successful delivery to client {client_id}: {actual_delivery!r}")
                    else:
                        logger.warning(f"Failed delivery to client {client_id}: {actual_delivery!r}")
                    
                    delivery_results[client_id] = delivery_success
                    
                except Exception as e:
                    logger.error(f"Error in delivery to client {client_id}: {e}")
                    delivery_results[client_id] = False
            
            return delivery_results
            
        except Exception as e:
            logger.error(f"Error during resource distribution: {e}")
            return {}

    # === PRIVATE CALCULATION METHODS ===
    
    def _evaluate_resources_to_self_consume(self) -> Payload:
        """Evaluate resources needed for Block self-consumption"""
        if not self.block or not hasattr(self.block, 'assets'):
            return Payload()
        
        resources = Payload()
        for asset in self.block.assets:
            if hasattr(asset, 'resources_to_self_consume') and asset.resources_to_self_consume:
                resources += asset.resources_to_self_consume
        
        return resources

    def _evaluate_effective_resources_needed(self) -> Payload:
        """Calculate effective resources needed based on autonomy"""
        resources_to_consume = self.resources_to_self_consume
        warehouse = self.warehouse
        
        if not resources_to_consume or not warehouse:
            return Payload()
        
        assessment = Payload()
        autonomy = warehouse.division(resources_to_consume)
        
        for param in self.RESOURCE_PARAMS:
            autonomy_value = getattr(autonomy, param)
            multiplier = self._get_autonomy_multiplier(autonomy_value)
            setattr( assessment, param, getattr(resources_to_consume, param) * multiplier )
        
        return assessment

    def _get_autonomy_multiplier(self, autonomy_value: float) -> float:
        """Get multiplier based on autonomy value"""
        for (min_val, max_val), multiplier in self.AUTONOMY_THRESHOLDS.items():
            if min_val <= autonomy_value < max_val:
                return multiplier
        return 0.1  # Default for very high values

    def _evaluate_clients_priority(self) -> Dict[str, float]:
        """Evaluate relative priority based on Block priority in region"""
        if not self.block or not self.block.region:
            logger.warning("Block or region not set. Cannot evaluate server priority.")
            return {}
        
        clients_priority = {}
        region_blocks_priority = self.block.region.blocks_priority
        
        for client_id, client in self._clients.items():
            priority = region_blocks_priority.get(client.id)
            
            if priority is None:
                logger.warning(f"Client {client.id} not found in region Block list.")
                continue
            
            clients_priority[client_id] = priority
        
        return clients_priority

    def _invalidate_resource_cache(self) -> None:
        """Invalidate resource calculation cache"""
        self._resources_to_self_consume = None
        self._resources_needed = None

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
            'block': self._validate_block_param,
            'clients': lambda x: self._validate_dict_param('clients', x),
            'server': lambda x: self._validate_dict_param('server', x),
            'warehouse': lambda x: self._validate_param('warehouse', x, "Payload"),
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
        return (f"Resource_Manager(block={self.block.id if self.block else None}, "
                f"clients={len(self._clients)}, servers={len(self._server)}, "
                f"warehouse={self._warehouse})")

    def __str__(self) -> str:
        """Readable string representation"""
        return f"Resource Manager for Block {self.block.id if self.block else 'None'}"