from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union, Tuple
from dataclasses import dataclass, field
from functools import lru_cache

from Code.Dynamic_War_Manager.Source.Context import Context
from Code.Dynamic_War_Manager.Source.Utility import Utility
from Code.Dynamic_War_Manager.Source.Block.Transport import Transport
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload
from Code.Dynamic_War_Manager.Source.DataType.State import State
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger

# Logger setup
    # CRITICAL 	50
    # ERROR 	40
    # WARNING 	30
    # INFO 	20
    # DEBUG 	10
    # NOTSET 	0
logger = Logger(module_name=__name__, set_consolle_log_level = 10, set_file_log_level = 30, class_name="Logistic_Lines").logger


@dataclass
class Logistic_Line:
    """Represents a logistic line that connect two blocks"""
    id: str # composto dall'id del server+id client + name + hash , per velocizzare ricerche fornendo id server e client
    side: str
    name: str    
    transport_line: Transport
    server: Block
    client: Block
    bidirectional: bool
    state: State

class Logistic_Lines:

    def __init__(self):
        #costruisce la classe con un DCS data seT
        self._logistic_lines: Dict[str: Logistic_Line]# id: str # composto: side + id server+id client + name + hash , per velocizzare ricerche fornendo id server e client        


    def get_line(self, **args):

        if args.search == "by id":
            pass
        elif args.search == "by block":
            pass
        elif args.search == "by transport":
            pass

    def set_line(self, side: str, name: str, transport_line: Transport, server: Block, client: Block):

        if not Utility.check_side(side):
            raise ValueError(f"Invalid side: {side!r}")

        if not isinstance(transport_line, Transport):
            raise TypeError(f"transport_line must be a Transport, got:{transport_line.__class__.__name__}")
        
        if not isinstance(server, Block):
            raise TypeError(f"server must be a Block, got:{server.__class__.__name__}")
        
        if not isinstance(client, Block):
            raise TypeError(f"client must be a Block, got:{client.__class__.__name__}")

        id = "side:"+side+".transport_line_id:"+transport_line.id+".server_id:"+server.id+".client_id:"+client.id+".name:"+name
        lgs_line = Logistic_Line(id=id, transport_line=transport_line, server=server, client=client)
        self._add_logistic_line(lgs_line=lgs_line)

    def _add_logistic_line(self, lgs_line: Logistic_Line):         
        """Internal method to add a line item with validation."""
        if not isinstance(lgs_line, Logistic_Line):
            raise TypeError(f"Expected Log_Line instance, got {type(lgs_line).__name__}")
        
        # Check if block already exists using dictionary key check
        if lgs_line.id in self._lines:
            raise ValueError(f"line {lgs_line.id} already exists in region")
        
        # add to dictionary
        self._logistic_lines[lgs_line.id] = lgs_line # Aggiunto al dizionario        
        self._invalidate_caches()
    
    def remove_logistic_line(self, lgs_line_id: str) -> bool:
        """Remove a lgs_line from the Logistic_Lines by ID."""
        if not isinstance(lgs_line_id, str):
            raise TypeError(f"lgs_line ID must be a string, got {type(lgs_line_id).__name__}")
        
        lgs_line = self._blocks.pop(lgs_line_id, None) # Accesso O(1)
        if lgs_line:            
            self._invalidate_caches()
            logger.info(f"lgs_line {lgs_line_id} removed")
            return True
        
        logger.warning(f"lgs_line {lgs_line_id} not found")
        return False
    
    def get_logistic_line_by_id(self, lgs_line_id: str) -> Optional[Logistic_Line]:
        """Get a lgs_line item by its ID."""
        if not isinstance(lgs_line_id, str):
            raise TypeError(f"lgs_line ID must be a string, got {type(lgs_line_id).__name__}")
        
        return self._logistic_lines.get(lgs_line_id) # Accesso O(1)

    @lru_cache(maxsize=64)
    def get_logistic_line_by_criteria(self, side: Optional[str] = None, 
                              transport_line_id: Optional[str] = None,
                              server_id: Optional[str] = None,
                              client_id: Optional[str] = None,
                              name: Optional[str] = None) -> List[Logistic_Line]:
        """
        Get logistic lines filtered by criteria. Cached for performance.
        
        Args:
            side: Filter by side (e.g., 'red', 'blue')
            transport_line_id: Filter by transport_line id
            server_id: Filter by server id
            client_id: Filter by client id
            name: Filter by name
        
        Returns:
            List of matching Logistic_Line objects
        """
        if not isinstance(side, str):
            raise TypeError(f"Expected str instance, got {type(side).__name__}")
    
        if not isinstance(transport_line_id, str):
            raise TypeError(f"Expected str instance, got {type(transport_line_id).__name__}")
        
        if not isinstance(server_id, str):
            raise TypeError(f"Expected str instance, got {type(server_id).__name__}")
        
        if not isinstance(client_id, str):
            raise TypeError(f"Expected str instance, got {type(client_id).__name__}")
        
        if not isinstance(name, str):
            raise TypeError(f"Expected str instance, got {type(name).__name__}")
        
        result = []
        
        for lgs_line in self._logistic_lines.values(): # Itera sui valori del dizionario
            
            # Filter by side
            if side and lgs_line.side != side:
                continue
                        
            if transport_line_id and lgs_line.transport_line.id != transport_line_id:
                continue

            if server_id and lgs_line.server.id != server_id:
                continue

            if client_id and lgs_line.client.id != client_id:
                continue
                
            if name and lgs_line.name != client_id:
                continue
            
            result.append(lgs_line)
        
        return result
    


    def setup_blocks_resource_manager(self):
        
        for line in self._lines:
            server = line.server
            client = line.client
            transport = line.transport

            # nota: negli update del resource_manager, prima deve essere effettuata la produzione e lo storage come out, poi i transport ed infine chi riceve
            client.set_server(id = transport.id, server = transport)# la funzione client.set_server effettua la back reference per il server 
            transport.set_server(id = server.id, server = server)

            # nota: dovresti controllare che i payload di ricezione e di inoltro siano diversi. il client non può inviare le stesse cose che richiede
            if line.bidirectional:
                server.set_server(id = transport.id, server = transport)
                transport.set_server(id = client.id, server = client)


    # CACHING METHODS (nota: la granularizzazione delle invalidazioni non serve in qaunto qualsisasi nmodifica di blocks o route, redo o blue, comporta la variazione di tutte le priority e conseguentemente di tutti i stategical center)
    def _invalidate_caches(self, cache_type: Optional[str] = None) -> None:
        """Invalidate specific caches based on type."""
        if cache_type is None or cache_type == "logistic_lines":
            self.get_logistic_line_by_criteria.cache_clear()
        
        
        logger.debug(f"Caches for Logistic_Lines invalidated ({cache_type or 'all'}).")

