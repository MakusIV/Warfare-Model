"""
Class Country
contains DCS Country information
"""

from LoggerClass import Logger
from Context import name, GROUP_CATEGORY
from sympy import Point2D
from typing import Literal, List, Dict

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Country')

class Country:

    def __init__(self, name: str = None, id: int = None, groups: Dict = None): 
            

        # check input parameters
        check_results =  self.checkParam( name, id, groups )
        
        if not check_results[1]:
            raise Exception(check_results[2] + ". Object not istantiate.")    
        
        self._name = name # DCS country name - str                  
        self._id = id # DCS country id - int     
        self._groups = groups # DCS group group category - Dict(type: Group)

        

    
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
    def id(self):
        return self._id   
    
    @id.setter
    def id(self, param):

        check_result = self.checkParam(id = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._id = param 


    @property
    def groups(self):
        return self._groups

    @groups.setter
    def groups(self, param):
        
        check_result = self.checkParam(groups = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._groups = param

    def searchGroup(self, group: Group = None, category: str = None, name: str = None, groupId: str = None, index: int = None):
        
        if group and isinstance(group, Group):
            for index, group_ in self._groups[group.category].items():
                if group.groupId == group_.groupId:
                    return True, group.category, index, group    

        if name and isinstance(name, str):            
            if category and isinstance(category, str) and category in GROUP_CATEGORY:
                for index, group in self._groups[category].items():
                    if group.name == name:
                        return True, category, index, group    
            else:
                for category in GROUP_CATEGORY:
                    for index, group in self._groups[category].items():
                        if group.name == name:
                            return True, category, index, group

        if groupId and isinstance(groupId, int):
            if category and isinstance(category, str) and category in GROUP_CATEGORY:
                for index, group in self._groups[category].items():
                    if group.groupId == groupId:
                        return True, category, index, group    
            else:
                for category in GROUP_CATEGORY:
                    for index, group in self._groups[category].items():
                        if group.groupId == groupId:
                            return True, category, index, group    
                        
        if index and isinstance(index, int):
            if category and isinstance(category, str) and category in GROUP_CATEGORY:
                return True, category, index, self._groups[category][index]

        return False, None, None, None
    
    def addGroup(self, category, index, group: Group):
        
        if not isinstance(group, Group) or not (category in GROUP_CATEGORY) or not isinstance(index, int) or index < 0 or index in self._units:
            raise Exception("Bad Arg: group must be a Group object, category must be a string from GROUP_CATEGORY and index must be an integer greater of 0 and unique")
        
        self._groups[category][index] = group

    def removeGroup(self, group: Group):
        
        if not isinstance(group, Group):
            raise Exception("Bad Arg: group must be a Group object")
        
        response, category, index, group = self.searchGroup(group = group, category = group.category)

        if response:
            del self._groups[category][index]
            return True
        else:
            return False

    
        


    def checkParam(name: str, id: Point2D, nav_points: Dict(Point2D), group_category: Dict(group)) -> bool: # type: ignore
        
        """Return True if type compliance of the parameters is verified"""   
    
        if not isinstance(name, str) or not (name in name):
            return (False, "Bad Arg: shape must be a string from name")
        
        if id and not isinstance(id, Point2D):
            return (False, "Bad Arg: id must be a Point2D")
        
        if nav_points and not isinstance(nav_points, Dict) or not (isinstance(nav_point, Point2D) for nav_point in nav_points.values):
            return (False, "Bad Arg: nav_points must be a dict of Point2D") 

        if group_category and isinstance(group_category, Dict):
            if all ( category in GROUP_CATEGORY for category in group_category.keys() ):
                for index, group in group_category.values:
                    if not (isinstance(group, Group): 
                        return (False, "Bad Arg: group must be a dict of Group")   
            else:
                return (False, "Bad Arg: group_category must be a dict with keys from GROUP_CATEGORY") 
        else:
            return (False, "Bad Arg: group_category must be a dict")
        
        return (True, "parameters ok")


    

    