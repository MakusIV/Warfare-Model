import General
from LoggerClass import Logger

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Threat')


class Threat:
    
    # non puoi utilizzare un riferimento ad un obj in quanto ti crea l'errore per riferimento circolare (Object import General import AI import Threat import Object [java non ha questo problema])
    # quindi devi definire qui tutte le caatteristiche necessarie della Threat per essere elaborata dalla AI

    def __init__( self, level,  name = None, id = None  ):

        
        if not( level ):
                raise Exception("Invalid parameters! Threat not istantiate.")

        self._name = None
        self._id = None

        if not name:
            self._name = General.setName('Threat_Name')
        else:
            self._name = name

        if not id:
            self._id = General.setId('Threat_ID')
        else:
            self._id = id

        self._level = level
        self._obj = obj
        
                        
            


    def setId(self, id = None):

        if not id:
            return False
        else:
            self.id = id        
            
        return True


    def setName(self, name):

        if not name:
            return False
        else:
            self.name = name

        return True