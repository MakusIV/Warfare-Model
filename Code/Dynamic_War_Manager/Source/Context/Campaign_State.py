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
from Code.Dynamic_War_Manager.Source.Context.Initial_Context import _ASSET_AVAILABILITY

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Campaign_State')

class Campaign_State:

    def __init__(self): 
        
        # property        
        self._current_mission = None
        self._current_date = None
        self._current_time = None
        self._date_mission = None
        self._current_asset_availability = {'air': {'asset_type': None, 'quantity': None}, 
                                            'ground': {'asset_type': None, 'quantity': None},
                                            'sea': {'asset_type': None, 'quantity': None}}
        
        self._asset_availability = {    'date': None, 
                                        'time':  None, 
                                        'mil_force': {  'air': None,
                                                        'ground': None,
                                                        'sea': None
                                                    }
                                    }
                                                   
        self._global_success_mission_ratio = {"Red": {"Air": None,"Ground": None, "Sea": None},
                                              "Blue": {"Air": None,"Ground": None, "Sea": None},}
        self._global_damaged_asset_ratio = {"Red": {"Air": None,"Ground": None, "Sea": None},
                                              "Blue": {"Air": None,"Ground": None, "Sea": None},}
        
        

 
  
   
  
        

    # le funzionalità specifiche le "inietti" o crei delle specializzazioni (classi derivate)