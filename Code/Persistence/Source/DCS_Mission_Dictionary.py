"""
 MODULE Code/I-O-Persistence/Source/Conversion_Lua_Python.py
 
 Functions for file/data structure conversion between LUA and Python


 TEST: OK with Jupiter Notebook

"""
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from typing import Literal
import lupa
from lupa import LuaRuntime
import unicodedata, logging, os
from Persistence.Source.Task import Task
from Persistence.Source.RoutePoint import RoutePoint
from Persistence.Source.Coalition import Coalition
from Persistence.Source.Group import Group
from Persistence.Source.Country import Country
from Code.Dynamic_War_Manager.Source.Context.Context import DCS_DATA_DIRECTORY # Store Lua file table and Python dictionary
import Persistence.Source.DCS_Data_Management as DCS_Data_Management


# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'DCS_Mission_Dictionary')

class DCS_Mission_Dictionary:

    def __init__(self): 
                            
        # check input parameters         
        self._lua_file_path = DCS_DATA_DIRECTORY + "\Mission\mission" # Storage directory for DCS_Dictionary + file name     
        self._output_module_path = DCS_DATA_DIRECTORY + "\Mission" # Storage directory for DCS_Dictionary
        self._table_name = "mission" # Lua table name (mission, ....)
        self._dictionary = DCS_Data_Management.convert_lua_to_python_module_with_code_formatting(self._lua_file_path, self._output_module_path, self._table_name)
        
        # generated object
        self._coalitions = self.getCoalitions(self); # Coalitions objects generated
        self._countries = self.getCountries(self); # Country objects generated
        self._groups = self.getGroups(self); # Group objects generated
        # Route, RoutePoint e Task sono gestiti mediante le associazioni presente nei groups


    """

    Ad ogni missione:

    La tabella LUA viene salvata dal contesto Lua di DCS, il contesto Python crea il dizionario DCS contenente tutte le informazioni della tabella Lua e 
    lo utilizza per creare tutte le classi necessarie per il Dynamic_War_Manager (DWM): Task, Route, RoutePoint, Group, Country. QUeste classi  sono utilizzate per
    il salvataggio delle informazioni di Log e di stato incluse quelle necessarie le analisi strategiche e tattiche.
    Durante l'esecuzione delle attività di competenza, il DWM aggiorna le classi suddette. Concluse le attività, il DWM aggiorna i dati del dizionario DCS, la corrispettiva tabella LUA e
    tutte gli altri file Lua necessari a DCS per lo svolgimento della missione successiva.  


    """

    def getCoalitions(self):
        """Assign coalitions by extracting them from the dictionary"""
        pass

    def getCountries(self):
        """Assign countries by extracting them from the dictionary"""
        pass

    def getGroups(self):
        """Assign groups by extracting them from the dictionary"""
        pass

    def update_Task(task: Task, DCS_Dictionary: dict):
        """ update Task info in DCS Python Dictionary """
        pass

    def create_Task(self):
        """" create class Task from info of DCS Python Dictionary """
        pass

    def update_RoutePoint(routePoint: RoutePoint, DCS_Dictionary: dict):
        """ update RoutePoint info in DCS Python Dictionary """
        pass

    def create_RoutePoint(self):
        """" create class RoutePoint from info of DCS Python Dictionary """
        pass

    def update_Group(group: Group, DCS_Dictionary: dict):
        """ update Group info in DCS Python Dictionary """
        pass

    def create_Group(self):
        """" create class Group from info of DCS Python Dictionary """
        pass

    def update_Country(country: Country, DCS_Dictionary: dict):
        """ update Country info in DCS Python Dictionary """
        pass

    def create_Country(self):
        """" create class Country from info of DCS Python Dictionary """
        pass

    def update_Coalition(coalition: Coalition, DCS_Dictionary: dict):
        """ update Coalition info in DCS Python Dictionary """
        pass

    def create_Coalition(self):
        """" create class Coalition from info of DCS Python Dictionary """
        pass

