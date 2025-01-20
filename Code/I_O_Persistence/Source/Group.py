"""
Class Group
contains DCS Group information
"""

from Code.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.Asset import Asset
from Code.I_O_Persistence.Source.Route import Route
from Context import name, GROUP_CATEGORY
from Task import Task
from sympy import Point2D
from typing import Literal, List, Dict

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Group')

class Group:

    def __init__(self, name: str = None, groupId: int = None, units: Dict = None, modulation: int = None, task: str = None, radioSet: bool = None, uncontrolled: bool = None, taskSelected: bool = None, hidden: bool = None, communication: bool = None, lateActivation: bool = None, start_time: int = None, frequency: float = None, x: float = None, y: float = None, tasks: Task = None, route: Route = None):             

        # check input parameters
        check_results =  self.checkParam( name, groupId, units )
        
        if not check_results[1]:
            raise Exception(check_results[2] + ". Object not istantiate.")    
        
        self._name = name # DCS group name - str                  
        self._groupId = groupId # DCS country groupId - int     
        self._units = units # DCS units units category - Dict(type: units)

        self._modulation = modulation # DCS group modulation - int           
        self._task = task  # DCS group task (CAS, ...) - str
        self._radioSet = radioSet # DCS group radioset - bool
        self._uncontrolled = uncontrolled  # DCS group uncontrolled - bool
        self._taskSelected = taskSelected  # DCS group task selected - bool        
        self._hidden = hidden # DCS group hidden - bool
        self._communication = communication # DCS group communication - bool
        self._lateActivation = lateActivation # DCS group lateActivation - bool
        self._start_time = start_time # DCS group start_time - int
        self._frequency = frequency # DCS group frequency - float

        self._x = x # DCS group x - float
        self._y = y # DCS group y - float
        
        self._tasks = tasks # DCS group tasks - index Dict
        self._route = route # DCS group route - index Dict

        

    
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
    def modulation(self):
        return self._modulation

    @modulation.setter
    def modulation(self, param):
        
        check_result = self.checkParam(modulation = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._modulation = param

    
    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, param):
        
        check_result = self.checkParam(task = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._task = param

    @property
    def radioSet(self):
        return self._radioSet

    @radioSet.setter
    def radioSet(self, param):
        
        check_result = self.checkParam(radioSet = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._radioSet = param

    @property
    def uncontrolled(self):
        return self._uncontrolled

    @uncontrolled.setter
    def uncontrolled(self, param):
        
        check_result = self.checkParam(uncontrolled = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._uncontrolled = param

    @property
    def taskSelected(self):
        return self._taskSelected

    @taskSelected.setter
    def taskSelected(self, param):
        
        check_result = self.checkParam(taskSelected = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._taskSelected = param

    @property
    def hidden(self):
        return self._hidden

    @hidden.setter
    def hidden(self, param):
        
        check_result = self.checkParam(hidden = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._hidden = param

    @property
    def communication(self):
        return self._communication

    @communication.setter
    def communication(self, param):
        
        check_result = self.checkParam(communication = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._communication = param

    @property
    def lateActivation(self):
        return self._lateActivation

    @lateActivation.setter
    def lateActivation(self, param):
        
        check_result = self.checkParam(lateActivation = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._lateActivation = param

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, param):
        
        check_result = self.checkParam(start_time = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._start_time = param

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, param):
        
        check_result = self.checkParam(frequency = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._frequency = param

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, param):
        
        check_result = self.checkParam(x = param)        

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._x = param 


    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, param):
        
        check_result = self.checkParam(y = param)            

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._y = param

    @property
    def tasks(self):
        return self._task

    @tasks.setter
    def tasks(self, param):
        
        check_result = self.checkParam(units = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._tasks = param


    def addTask(self, task, index):

        if not isinstance(task, Task) or not isinstance(index, int) or index < 0 or index in self._tasks:
            raise Exception("Bad Arg: task must be a Task object, index must be an integer greater of 0 and unique")
        
        self._units[index] = task

    def removeTask(self, task):
        
        if not isinstance(task, Task):
            raise Exception("Bad Arg: task must be an Task object")
        
        response, index, asset = self.searchUnit(task = task)

        if response:
            del self._tasks[index]
            return True
        else:
            return False


    def searchTask(self, task: Task = None, name: str = None, id: str = None, index: int = None ):
        
        if task and isinstance(task, Task):
            for index, task_ in self._tasks.items():
                if task.id == task_.id:
                    return True, index, task

        if name and isinstance(name, str):
            for index, task_ in self._tasks.items():
                if task.name == name:
                    return True, index, task

        if id and isinstance(id, str):
            for index, task_ in self._tasks.items():
                if task.id == id:
                    return True, index, unit

        if index and isinstance(index, int):
            return True, index, self._tasks[index]

        return False, None, None


    @property
    def route(self):
        return self._task

    @route.setter
    def route(self, param):
        
        check_result = self.checkParam(units = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._route = param



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

        
    
        


    def checkParam(name: str, groupId: int, units: Dict(Asset), modulation: int = None, task: str = None, radioSet: bool = None, uncontrolled: bool = None, taskSelected: bool = None, hidden: bool = None, communication: bool = None, lateActivation: bool = None, start_time: int = None, frequency: float = None, x: float = None, y: float = None, tasks: Task = None, route: Route = None) -> bool: # type: ignore
        
        """Return True if type compliance of the parameters is verified"""   
    
        if not isinstance(name, str) or not (name in name):
            return (False, "Bad Arg: shape must be a string from name")
        
        if groupId and not isinstance(groupId, int):
            return (False, "Bad Arg: groupId must be a integer")
            
        if units and not isinstance(units, Dict) or not (isinstance(unit, Asset) for unit in units.values):
            return (False, "Bad Arg: units must be a dict of Asset") 

        if modulation and not isinstance(modulation, int):
            return (False, "Bad Arg: modulation must be a integer")
        
        if task and not isinstance(task, str):
            return (False, "Bad Arg: task must be a string")
        
        if radioSet and not isinstance(radioSet, bool):
            return (False, "Bad Arg: radioSet must be a boolean")
        
        if uncontrolled and not isinstance(uncontrolled, bool):
            return (False, "Bad Arg: uncontrolled must be a boolean")
        
        if taskSelected and not isinstance(taskSelected, bool):
            return (False, "Bad Arg: taskSelected must be a boolean")
        
        if hidden and not isinstance(hidden, bool):
            return (False, "Bad Arg: hidden must be a boolean")
        
        if communication and not isinstance(communication, bool):
            return (False, "Bad Arg: communication must be a boolean")

        if lateActivation and not isinstance(lateActivation, bool):
            return (False, "Bad Arg: lateActivation must be a boolean")
        
        if start_time and not isinstance(start_time, int):
            return (False, "Bad Arg: start_time must be a integer")
        
        if frequency and not isinstance(frequency, float):
            return (False, "Bad Arg: frequency must be a float")
        
        if x and not isinstance(x, float):
            return (False, "Bad Arg: x must be a float")
        
        if y and not isinstance(y, float):
            return (False, "Bad Arg: y must be a float")
        
        if tasks and not isinstance(tasks, Task):
            return (False, "Bad Arg: tasks must be a Task object")
        
        if route and not isinstance(route, Route):
            return (False, "Bad Arg: route must be a Route object") 
        
        return (True, "parameters ok")


    

    