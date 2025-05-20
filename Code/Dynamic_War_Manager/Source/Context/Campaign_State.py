"""
 CLASS State
 
 Rappresenta lo stato di un oggetto di classe Block, di cui è uno dei componenti necessari.
 L'associazione tra State e Block è di 1 a 1.

 ATTRIBUTI:
    _ID: string
    _damage: float [0:1]
    _state_value: string {Active, Inactive, Standby, Destroyed}

"""

from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.Context.Context import STATE
from Code.Dynamic_War_Manager.Source.Asset import Asset
from Code.Dynamic_War_Manager.Source.Utility import Utility

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Campaign_State')

class Campaign_State:

    def __init__(self, n_mission: int|None, date_mission: str|None): 
        
        # property        
        self._n_mission = n_mission
        self._date_mission = date_mission
        self._global_success_mission_ratio = {"Red": {"Air": None,"Groud": None, "Sea": None},
                                              "Blue": {"Air": None,"Groud": None, "Sea": None},}
        self._global_damaged_asset_ratio = {"Red": {"Air": None,"Groud": None, "Sea": None},
                                              "Blue": {"Air": None,"Groud": None, "Sea": None},}
        
        

    @property        
    def n_mission(self):
        return self._n_missiona
    
    @n_mission.setter
    def n_mission(self, n_mission):
        
        if not isinstance(n_mission, int):
            raise TypeError("type not valid, int type expected")
        
        self._n_mission = n_mission



    @property        
    def date_mission(self):
        return self._date_missiona
    
    @date_mission.setter
    def data_mission(self, date_mission):
        
        if not isinstance(date_mission, str):
            raise TypeError("type not valid, str type expected")
        
        self._date_mission = date_mission


  

  
   
  
        

    # le funzionalità specifiche le "inietti" o crei delle specializzazioni (classi derivate)