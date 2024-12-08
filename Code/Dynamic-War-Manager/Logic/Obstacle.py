 # non puoi utilizzare un riferimento ad un obj in quanto ti crea l'errore per riferimento circolare (Object import General import AI import Threat import Object [java non ha questo problema])
 # quindi devi definire qui tutte le caatteristiche necessarie della Threat per essere elaborata dalla AI

from State import State
from LoggerClass import Logger

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Obstacle')

class Obstacle:

    def __init__(self, coord, type = 'WATER_STONE', name = 'Stone', dimension = [1, 1, 1]  ):

            
            self._type = type #WATER_STONE, ENERGY_FIELD, ......
            # La water stone rappresenta un volume d'acqua fermo o mobile che non può essere attraversato                 
           