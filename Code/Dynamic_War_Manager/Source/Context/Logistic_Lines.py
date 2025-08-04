from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union, Tuple
from dataclasses import dataclass, field

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
logger = Logger(module_name=__name__, set_consolle_log_level = 10, set_file_log_level=30, class_name="Region").logger


@dataclass
class Log_Line:
    """Represents a logistic line that connect two blocks"""
    name: str
    id: str # composto dall'id del server+id client + name + hash , per velocizzare ricerche fornendo id server e client
    transport_line: Transport
    server: Block
    client: Block
    resource_from_server_to_client: Payload
    bidirectional: bool
    resource_from_client_to_server: Payload
    state: State

class Logistic_Lines:

    def __init__(self, **args):
        #costruisce la classe con un DCS data seT
        self._lines: Dict[str: Log_Line] = args["lines"]
        pass


    def get_line(self, **args):

        if args.search == "by id":
            pass
        elif args.search == "by block":
            pass
        elif args.search == "by transport":
            pass

    def set_line(self, line: Log_Line):
        pass

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

    

