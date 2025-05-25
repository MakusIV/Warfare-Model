from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.Context.Context import STATE
from Code.Dynamic_War_Manager.Source.Utility import Utility

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

    def checkParam(self, goods: int = None, energy: int = None, hr: int = None, hc: int = None, hs: int = None, hb: int = None ):
         
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
                
        
    def sum(self, p1, p2):
         
         if not(p1 and p2) and not(p1.__class__.__name__ == "Payload" and p2.__class__.__name__ == "Payload"):
             raise Exception("p1 and p2 must be Payload object")
         
         return Payload(goods =p1.goods+p2.goods, energy=p1.energy+p2.energy, hr=p1.hr+p2.hr, hc=p1.hc+p2.hc, hs=p1.hs+p2.hs, hb=p1.hb+p2.hb )

    def subtract(self, p1, p2):
         
         if not(p1 and p2) and not(p1.__class__.__name__ == "Payload" and p2.__class__.__name__ == "Payload"):
             raise Exception("p1 and p2 must be Payload object")
         
         return Payload(goods =p1.goods-p2.goods, energy=p1.energy-p2.energy, hr=p1.hr-p2.hr, hc=p1.hc-p2.hc, hs=p1.hs+p2.hs, hb=p1.hb-p2.hb )
    
    def product(self, p1, factor: float):
         
         if not(p1 and factor) and not(p1.__class__.__name__ == "Payload" and isinstance(factor, (int, float))):
             raise Exception("p1 must be Payload object and factor must be a number")
         
         return Payload(goods =p1.goods * factor, energy=p1.energy * factor, hr=p1.hr * factor, hc=p1.hc * factor, hs=p1.hs * factor, hb=p1.hb * factor )
    
    def division(self, p1, div: float):
         
         if not istance(div, (int, float)) or div == 0:
             return None
         
         return self.product(p1, 1/div) 
    

    @property
    def goods(self):
        return self._goods

    @goods.setter
    def goods(self, value):
        self._validate_param('goods', value, float)
        self._goods = value

    @property
    def energy(self):
        return self._energy

    @energy.setter
    def energy(self, value):
        self._validate_param('energy', value, float)
        self._energy = value

    @property
    def hr(self):
        return self._hr

    @hr.setter
    def hr(self, value):
        self._validate_param('hr', value, int)
        self._hr = value

    @property
    def hc(self):
        return self._hc

    @hc.setter
    def hc(self, value):
        self._validate_param('hc', value, int)
        self._hc = value

    @property
    def hs(self):
        return self._hs

    @hs.setter
    def hs(self, value):
        self._validate_param('hs', value, int)
        self._hs = value

    @property
    def hb(self):
        return self._hb

    @hb.setter
    def hb(self, value):
        self._validate_param('hb', value, int)
        self._hb = value

    def _validate_all_params(self, **kwargs) -> None:
        """Validate all input parameters"""
        type_checks = {            
                'goods': float, # accetta solo None durante il runtime, altrimenti genera errore perchè Block non è importata e non deve esserlo: l'utilizzo dei suoi metodi è cmq garantito dall'oggetto importato             
                'energy': float,
                'hr': int,
                'hc': int,
                'hs': int,
                'hb': int,                
            }        
        for param, value in kwargs.items():            
            if value is not None and param in type_checks:                
                    self._validate_param(param, value, type_checks[param])


    def _validate_param(self, param_name: str, value: Any, expected_type: type) -> None:
        """Validate a single parameter"""
        if value is not None and not isinstance(value, expected_type):
            raise TypeError(f"Invalid type for {param_name}. Expected {expected_type.__name__}, got {type(value).__name__}")

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

    def __eq__(self, other):
        if not isinstance(other, Payload):
            return False
        return (self._goods == other._goods and
                self._energy == other._energy and
                self._hr == other._hr and
                self._hc == other._hc and
                self._hs == other._hs and
                self._hb == other._hb)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __lt__(self, other):
        if not isinstance(other, Payload):
            raise TypeError("Operand must be an instance of Payload")
        return (self._goods < other._goods and
                self._energy < other._energy and
                self._hr < other._hr and
                self._hc < other._hc and
                self._hs < other._hs and
                self._hb < other._hb)
    
    def __le__(self, other):
        if not isinstance(other, Payload):
            raise TypeError("Operand must be an instance of Payload")
        return (self._goods <= other._goods and
                self._energy <= other._energy and
                self._hr <= other._hr and
                self._hc <= other._hc and
                self._hs <= other._hs and
                self._hb <= other._hb)
    
    def __ge__(self, other):
        if not isinstance(other, Payload):
            raise TypeError("Operand must be an instance of Payload")
        return (self._goods >= other._goods and
                self._energy >= other._energy and
                self._hr >= other._hr and
                self._hc >= other._hc and
                self._hs >= other._hs and
                self._hb >= other._hb)
    
    def __gt__(self, other):
        if not isinstance(other, Payload):
            raise TypeError("Operand must be an instance of Payload")
        return (self._goods > other._goods and
                self._energy > other._energy and
                self._hr > other._hr and
                self._hc > other._hc and
                self._hs > other._hs and
                self._hb > other._hb)
    
    def __add__(self, other):
        if not isinstance(other, Payload):
            raise TypeError("Operand must be an instance of Payload")
        return Payload(
            goods=self._goods + other._goods,
            energy=self._energy + other._energy,
            hr=self._hr + other._hr,
            hc=self._hc + other._hc,
            hs=self._hs + other._hs,
            hb=self._hb + other._hb
        )
    
    def __sub__(self, other):   
        if not isinstance(other, Payload):
            raise TypeError("Operand must be an instance of Payload")
        return Payload(
            goods=self._goods - other._goods,
            energy=self._energy - other._energy,
            hr=self._hr - other._hr,
            hc=self._hc - other._hc,
            hs=self._hs - other._hs,
            hb=self._hb - other._hb
        )
    
    def __mul__(self, factor: float):   
        if not isinstance(factor, (int, float)):
            raise TypeError("Operand must be a number")
        return Payload(
            goods=self._goods * factor,
            energy=self._energy * factor,
            hr=self._hr * factor,
            hc=self._hc * factor,
            hs=self._hs * factor,
            hb=self._hb * factor
        )
    
    def __truediv__(self, div: float):  
        if not isinstance(div, (int, float)) or div == 0:
            raise ValueError("Operand must be a non-zero number")
        return Payload(
            goods=self._goods / div,
            energy=self._energy / div,
            hr=self._hr / div,
            hc=self._hc / div,
            hs=self._hs / div,
            hb=self._hb / div
        )   

    def __div__(self, other: Payload):
        if not isinstance(other, Payload):
            raise TypeError("Operand must be an instance of Payload")
        return Payload(
            goods=self._goods / other._goods if other._goods != 0 else 0,
            energy=self._energy / other._energy if other._energy != 0 else 0,
            hr=self._hr / other._hr if other._hr != 0 else 0,
            hc=self._hc / other._hc if other._hc != 0 else 0,
            hs=self._hs / other._hs if other._hs != 0 else 0,
            hb=self._hb / other._hb if other._hb != 0 else 0
        )