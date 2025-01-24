from LoggerClass import Logger
from Context import STATE
import Utility

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'State')



"""
 CLASS Payload
 
 Rappresenta il tipo di dato payload utilizzato in alcune proprietà e metodi della classe Block

"""


class Payload:
    def __init__(self, goods: int = 0, energy: int = 0, hr: int = 0, hc: int = 0, hs: int = 0, hb: int = 0 ):
        self._goods = goods # int 
        self._energy = energy # int
        self._hr = hr # human resource: civil worker int
        self._hc = hc # human resource: military commander int
        self._hs = hs # human resource: military specialist int
        self._hb = hb # human resource: military soldier int

        # association
        
        



   