from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union, Tuple


# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'State')



"""
 CLASS Payload
 
 Rappresenta il tipo di dato payload utilizzato in alcune proprietà e metodi della classe Block

"""


class Payload:
    def __init__(self, goods: Optional[int] = 0, energy: Optional[int] = 0, hr: Optional[int] = 0, hc: Optional[int] = 0, hs: Optional[int] = 0, hb: Optional[int] = 0 ):
        self._goods = goods # int food, component ecc
        self._energy = energy # int fuel, power ecc
        self._hr = hr # human resource: civil worker int
        self._hc = hc # human resource: military commander int
        self._hs = hs # human resource: military specialist int
        self._hb = hb # human resource: military soldier int

        # Validate all parameters at once
        self._validate_all_params(goods=goods, energy=energy, hr=hr, hc=hc, hs=hs, hb=hb)

    

    @property
    def goods(self):
        return self._goods

    @goods.setter
    def goods(self, value):
        self._validate_param('goods', value, (int, float))
        self._goods = value

    @property
    def energy(self):
        return self._energy

    @energy.setter
    def energy(self, value):
        self._validate_param('energy', value, (int, float))
        self._energy = value

    @property
    def hr(self):
        return self._hr

    @hr.setter
    def hr(self, value):
        self._validate_param('hr', value, (int, float))
        self._hr = value

    @property
    def hc(self):
        return self._hc

    @hc.setter
    def hc(self, value):
        self._validate_param('hc', value, (int, float))
        self._hc = value

    @property
    def hs(self):
        return self._hs

    @hs.setter
    def hs(self, value):
        self._validate_param('hs', value, (int, float))
        self._hs = value

    @property
    def hb(self):
        return self._hb

    @hb.setter
    def hb(self, value):
        self._validate_param('hb', value, (int, float))
        self._hb = value

    def _validate_all_params(self, **kwargs) -> None:
        """Validate all input parameters"""
        type_checks = {            
                'goods': (int, float), # accetta solo None durante il runtime, altrimenti genera errore perchè Block non è importata e non deve esserlo: l'utilizzo dei suoi metodi è cmq garantito dall'oggetto importato             
                'energy': (int, float),
                'hr': (int, float),
                'hc': (int, float),
                'hs': (int, float),
                'hb': (int, float),                
            }        
        for param, value in kwargs.items():            
            if value is not None and param in type_checks:                
                    self._validate_param(param, value, type_checks[param])


    def _validate_param(self, param_name: str, value: Any, expected_type: type) -> None:
        """Validate a single parameter"""
        if value is not None and not isinstance(value, expected_type):
            raise TypeError(f"Invalid type for {param_name}. Expected {expected_type!r}, got {type(value).__name__}")

    def _validate_payload_class(self, value: 'Payload') -> bool:
        """Validate that the other object is an instance of Payload"""
        if value is not None and hasattr(value, '__class__') and value.__class__.__name__ == 'Payload':
            return True
        return False

 
        
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
        if not self._validate_payload_class(other):
            return False
        return (self._goods == other.goods and
                self._energy == other.energy and
                self._hr == other.hr and
                self._hc == other.hc and
                self._hs == other.hs and
                self._hb == other.hb)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __lt__(self, other):
        if not self._validate_payload_class(other):
            raise TypeError("Operand must be an instance of Payload")
        return (self._goods < other.goods and
                self._energy < other.energy and
                self._hr < other.hr and
                self._hc < other.hc and
                self._hs < other.hs and
                self._hb < other.hb)
    
    def __le__(self, other):
        if not self._validate_payload_class(other):
            raise TypeError("Operand must be an instance of Payload")
        return (self._goods <= other.goods and
                self._energy <= other.energy and
                self._hr <= other.hr and
                self._hc <= other.hc and
                self._hs <= other.hs and
                self._hb <= other.hb)
    
    def __ge__(self, other):
        if not self._validate_payload_class(other):
            raise TypeError("Operand must be an instance of Payload")
        return (self._goods >= other.goods and
                self._energy >= other.energy and
                self._hr >= other.hr and
                self._hc >= other.hc and
                self._hs >= other.hs and
                self._hb >= other.hb)
    
    def __gt__(self, other):
        if not self._validate_payload_class(other):
            raise TypeError("Operand must be an instance of Payload")
        return (self._goods > other.goods and
                self._energy > other.energy and
                self._hr > other.hr and
                self._hc > other.hc and
                self._hs > other.hs and
                self._hb > other.hb)
    
    def __add__(self, other):
        if not self._validate_payload_class(other):
            raise TypeError("Operand must be an instance of Payload")
        return Payload(
            goods=self._goods + other.goods,
            energy=self._energy + other.energy,
            hr=self._hr + other.hr,
            hc=self._hc + other.hc,
            hs=self._hs + other.hs,
            hb=self._hb + other.hb
        )
    
    def __sub__(self, other):   
        if not self._validate_payload_class(other):
            raise TypeError("Operand must be an instance of Payload")
        return Payload(
            goods=self._goods - other.goods,
            energy=self._energy - other.energy,
            hr=self._hr - other.hr,
            hc=self._hc - other.hc,
            hs=self._hs - other.hs,
            hb=self._hb - other.hb
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

    def division(self, other):
        if not self._validate_payload_class(other):
            raise TypeError("Operand must be an instance of Payload")
        return Payload(
            goods=self._goods / other.goods if other.goods != 0 else 0,
            energy=self._energy / other.energy if other.energy != 0 else 0,
            hr=self._hr / other.hr if other.hr != 0 else 0,
            hc=self._hc / other.hc if other.hc != 0 else 0,
            hs=self._hs / other.hs if other.hs != 0 else 0,
            hb=self._hb / other.hb if other.hb != 0 else 0
        )