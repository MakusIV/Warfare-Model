"""
Class Task
contains DCS Task information

Coalition -> Country -> Group -> Route -> Point -> Task -> params -> Tasks
Coalition -> Country -> Group -> Tasks

"""

from LoggerClass import Logger
from Persistence.Source.Country import Country
from Context import SIDE
from sympy import Point2D
from typing import Literal, List, Dict

# LOGGING -- 
logger = Logger(module_name = __name__, class_name = 'Task')

class Task:

    def __init__(self, params: Dict = None, number: int = None, auto: bool = None, id: str = None, enabled: bool = None): 
            

        # check input parameters
        check_results =  self.checkParam( params, number, auto, id, enabled )
        
        if not check_results[1]:
            raise Exception(check_results[2] + ". Object not istantiate.")    
        
                
        self._number = number # DCS task number  - int
        self._auto = auto # DCS task bool - booelan
        self._id = id # DCS task id - str (e.g. 'WrappedAction')
        self._enabled = enabled # DCS task enabled - bool        
        
        # params.action: Dict 
        # params.action.id: str, params.action.params: Dict
        # params.action.params.name, params.action.params.value,
        self._params = params # DCS point task - Dict: {'action': Dict: {'id': str, params': Dict: {'value': int , 'name': str } } } 
        
        # params.action.params = ['number': int, 'callnameFlag': bool, 'callname': str, 'power': int, 'modulation': int, 'frequency': int]
        # non lo inserisco in quanto probabilmente ci sono campi aggiuntivi in relazione al tipo di object: vehicle, plane ed al tipo di missione

    
    @property
    def params(self):
        return self._params         
    
    @params.setter
    def params(self, param):

        check_result = self.checkParam(params = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
                
        self._params = param        
        return

    def toString(self):
        s1 = "number: " + str(self._number) + ", auto: " + str(self._auto) + ", id: " + str(self._id) + ", enabled: " + str(self._enabled)
        
        for key_action, value_action in self._params.items(): # action

            if key_action == 'action':
                s2 = "action:\n id: " + value_action.id
                s3 = " "

                for key, value in value_action.params.items(): # params
                    s3 = s3 + key + ": " + str(value) + ", "

                s2 = s2 + s3

            else:
                s2 = key_action + ": " + str(value_action)  
                
        return s1 + '\n' + s2
    
    def checkParam(params: Dict = None, number: int = None, auto: bool = None, id: str = None, enabled: bool = None) -> bool: # type: ignore
        
        """Return True if type compliance of the parameters is verified"""   
    
          
        if id and not isinstance(id, str):
            return (False, "Bad Arg: id must be a str")
        
        if auto and not isinstance(auto, bool):
            return (False, "Bad Arg: auto must be a bool")        
        
        if enabled and not isinstance(enabled, bool):
            return (False, "Bad Arg: enabled must be a bool")
        
        if number and not isinstance(number, int):
            return (False, "Bad Arg: number must be a int")
        
        # Dict: {'action': Dict: {'id': str, params': Dict: {'value': int , 'name': str, 'variantIndex': int, 'formationIndex': int } } }  nota: variantIndex e formationIndex sono opzionali
        if params and not isinstance(params, Dict) or not params.keys()=='action' or not isinstance(params.action, Dict) or not all (keys in params.action.keys() for keys in ['id', 'params'] ) or not isinstance(params.action.params, Dict): 
            return (False, "Bad Arg: params must be a Dict: {'action': Dict: {'id': str, params': Dict: {'value': int , 'name': str, 'variantIndex': int, 'formationIndex': int } } }  note: variantIndex e formationIndex are optional")
        
        return (True, "parameters ok")


    

    