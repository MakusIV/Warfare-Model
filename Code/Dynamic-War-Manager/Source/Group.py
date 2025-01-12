"""
Class Group
contains DCS Group information
"""

from LoggerClass import Logger
from Asset import Asset
from Context import name, GROUP_CATEGORY
from sympy import Point2D
from typing import Literal, List, Dict

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Group')

class Group:

    def __init__(self, name: str = None, groupId: int = None, units: Dict = None): 
            

        # check input parameters
        check_results =  self.checkParam( name, groupId, units )
        
        if not check_results[1]:
            raise Exception(check_results[2] + ". Object not istantiate.")    
        
        self._name = name # DCS group name - str                  
        self._groupId = groupId # DCS country groupId - int     
        self._units = units # DCS units units category - Dict(type: units)

        self._group_index # DCS country group index
        self._group_modulation # DCS group modulation            
        self._group_task  # DCS group task (CAS, ...) - str
        self._group_radioSet # DCS group radioset - bool
        self._group_uncontrolled  # DCS group uncontrolled - bool
        self._group_taskSelected  # DCS group task selected - bool
        
        self._group_hidden # DCS group hidden - bool
        self._group_x # DCS group x - float
        self._group_y # DCS group y - float
        
        self._group_communication # DCS group communication - bool
        self._group_lateActivation # DCS group lateActivation - bool
        self._group_start_time # DCS group start_time - int
        self._group_frequency # DCS group frequency - float
        self._group_tasks # DCS group tasks - index Dict
        self._group_route # DCS group route - index Dict

        

    
    @property
    def name(self):
        return self._name         
    
    @name.setter
    def name(self, param):

        check_result = self.checkParam(name = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
                
        self._name = param

    @property
    def groupId(self):
        return self._groupId   
    
    @groupId.setter
    def groupId(self, param):

        check_result = self.checkParam(groupId = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._groupId = param 


    @property
    def units(self):
        return self._units

    @units.setter
    def units(self, param):
        
        check_result = self.checkParam(units = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._units = param
    
    def addUnit(self, index, unit: Asset):
        
        if not isinstance(unit, Asset) or not isinstance(index, int) or index < 0 or index in self._units:
            raise Exception("Bad Arg: unit must be a Asset object, index must be an integer greater of 0 and unique")
        
        self._units[index] = unit

    def removeUnit(self, unit: Asset):
        
        if not isinstance(unit, Asset):
            raise Exception("Bad Arg: unit must be an Asset object")
        
        response, index, asset = self.searchUnit(unit = unit)

        if response:
            del self._units[index]
            return True
        else:
            return False

    def searchUnit(self, unit: Asset = None, name: str = None, id: int = None, index: int = None ):
        
        if unit and isinstance(unit, Asset):
            for index, unit_ in self._units.items():
                if unit.id == unit_.id:
                    return True, index, unit

        if name and isinstance(name, str):
            for index, unit in self._units.items():
                if unit.name == name:
                    return True, index, unit

        if id and isinstance(id, int):
            for index, unit in self._units.items():
                if unit.id == id:
                    return True, index, unit

        if index and isinstance(index, int):
            return True, index, self._units[index]

        return False, None, None

        
    
        


    def checkParam(name: str, groupId: int, units: Dict(Asset)) -> bool: # type: ignore
        
        """Return True if type compliance of the parameters is verified"""   
    
        if not isinstance(name, str) or not (name in name):
            return (False, "Bad Arg: shape must be a string from name")
        
        if groupId and not isinstance(groupId, int):
            return (False, "Bad Arg: groupId must be a integer")
            
        if units and not isinstance(units, Dict) or not (isinstance(unit, Asset) for unit in units.values):
            return (False, "Bad Arg: units must be a dict of Asset")   
        
        return (True, "parameters ok")


    

    