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

    def checkParam(self, goods: int|None, energy: int|None, hr: int|None, hc: int|None, hs: int|None, hb: int|None ):
         
        if goods and not isinstance(goods, int):
            return (False, "Bad Arg: goods must be a int")
        if energy and not isinstance(energy, int):
            return (False, "Bad Arg: energy must be a int")
        if hr and not isinstance(hr, int):
            return (False, "Bad Arg: hr must be a int")
        if hc and not isinstance(hc, int):
            return (False, "Bad Arg: hc must be a int")
        if hs and not isinstance(hs, int):
            return (False, "Bad Arg: hs must be a int")
        if hb and not isinstance(hb, int):
            return (False, "Bad Arg: hb must be a int")
        return (True, "OK")
                
        
    @property
    def goods(self):
        return self._goods

    @goods.setter
    def goods(self, value):
        check_result = self.checkParam(value)
        if not check_result[1]:
            raise Exception(check_result[2])
        self._goods = value
        return True

    @property
    def energy(self):
        return self._energy

    @energy.setter
    def energy(self, value):
        check_result = self.checkParam(value)
        if not check_result[1]:
            raise Exception(check_result[2])
        self._energy = value
        return True

    @property
    def hr(self):
        return self._hr

    @hr.setter
    def hr(self, value):
        check_result = self.checkParam(value)
        if not check_result[1]:
            raise Exception(check_result[2])
        self._hr = value
        return True

    @property
    def hc(self):
        return self._hc

    @hc.setter
    def hc(self, value):
        check_result = self.checkParam(value)
        if not check_result[1]:
            raise Exception(check_result[2])
        self._hc = value
        return True

    @property
    def hs(self):
        return self._hs

    @hs.setter
    def hs(self, value):
        check_result = self.checkParam(value)
        if not check_result[1]:
            raise Exception(check_result[2])
        self._hs = value
        return True

    @property
    def hb(self):
        return self._hb

    @hb.setter
    def hb(self, value):
        check_result = self.checkParam(value)
        if not check_result[1]:
            raise Exception(check_result[2])
        self._hb = value
        return True

   
    def getStatus(self, type: str):

        if type == 'goods':
            return self._goods
        elif type == 'energy':
            return self._energy
        elif type == 'hr':
            return self._hr
        elif type == 'hc':
            return self._hc
        elif type == 'hs':
            return self._hs
        elif type == 'hb':
            return self._hb
        
    def __repr__(self):
        return (f"goods: {self._goods!r}, energy: {self._energy!r}, hr: {self._hr!r}, hr: {self._hr!r}, hc: {self._hc!r}, hs: {self._hs!r}, hb: {self._hb!r}")
    
    def __str__(self):
        return (f"payload:\n"
                f"goods: {self._goods!r}\n"
                f"energy: {self._energy!r}\n"
                f"hr: {self._hr!r}\n"
                f"hc: {self._hc!r}\n"
                f"hs: {self._hs!r}\n"
                f"hb: {self._hb!r}")