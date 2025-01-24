"""
Class Coalition
contains DCS Coalition information
"""

from LoggerClass import Logger
from Persistence.Source.Country import Country
from Context import SIDE
from sympy import Point2D
from typing import Literal, List, Dict

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Coalition')

class Coalition:

    def __init__(self, side: str = None, bullseye: Point2D = None, nav_points: Dict = None, countries: Dict = None): 
            

        # check input parameters
        check_results =  self.checkParam( side, bullseye, nav_points )
        
        if not check_results[1]:
            raise Exception(check_results[2] + ". Object not istantiate.")    
        
        

        self._side # DCS coalition side - str  (red, blue, neutral)
        self._bullseye # DCS coalition bullseye - Point2D
        self._nav_points # DCS coalition nav_points - Dict(index: Point2D) )            
        self._countries # DCS coalition countries - Dict("name": Country)

    
    @property
    def side(self):
        return self._side         
    
    @side.setter
    def side(self, param):

        check_result = self.checkParam(side = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
                
        self._side = param

    @property
    def bullseye(self):
        return self._bullseye   
    
    @bullseye.setter
    def bullseye(self, param):

        check_result = self.checkParam(bullseye = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._bullseye = param 

    @property
    def nav_points(self):
        return self._nav_points   
        
    @nav_points.setter
    def nav_points(self, param):
        
        check_result = self.checkParam(nav_points = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._nav_points = param

    @property
    def countries(self):
        return self._countries

    @countries.setter
    def countries(self, param):
        
        check_result = self.checkParam(countries = param)

        if not check_result[1]:
            raise Exception(check_result[2]) 
        
        self._countries = param

    def addCountry(self, index: int, country: Country):
        
        if not isinstance(country, Country) or not isinstance(index, int) or index < 0 or index in self._units:
            raise Exception("Bad Arg: country must be a Country object and index must be an integer greater of 0 and unique")
        
        self._countries[index] = country

    def removeCountry(self, country: Country):
        
        if not isinstance(country, Country):
            raise Exception("Bad Arg: country must be a Country object")

        response, index, country = self.searchCountry(country = country)

        if response:
            del self._countries[index]
            return True
        else:
            return False

    def searchCountry(self, country: Country = None, name: str = None, id: int = None, index: int = None) -> bool:

        if country and isinstance(country, Country):
            for index, country in self._countries.items():
                if country.id == country.id:
                    return True, index, country

        if name and isinstance(name, str):
            for index, country in self._countries.items():
                if country.name == name:
                    return True, index, country

        if id and isinstance(id, int):
            for index, country in self._countries.items():
                if country.id == id:
                    return True, index, country

        if index and isinstance(index, int):
            return True, index, self._countries[index]

        return False    

    
    def checkParam(side: str, bullseye: Point2D, nav_points: Dict(Point2D), countries: Dict(Country)) -> bool: # type: ignore
        
        """Return True if type compliance of the parameters is verified"""   
    
        if not isinstance(side, str) or not (side in SIDE):
            return (False, "Bad Arg: shape must be a string from SIDE")
        
        if bullseye and not isinstance(bullseye, Point2D):
            return (False, "Bad Arg: bullseye must be a Point2D")
        
        if nav_points and not isinstance(nav_points, Dict) or not (isinstance(nav_point, Point2D) for nav_point in nav_points.values):
            return (False, "Bad Arg: nav_points must be a dict of Point2D") 

        if countries and not isinstance(countries, Dict) or not (isinstance(country, Point2D) for country in countries.values):
            return (False, "Bad Arg: nav_points must be a dict of Country")   
        
        return (True, "parameters ok")


    

    