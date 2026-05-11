"""
 CLASS State
 
 Rappresenta lo stato di un oggetto di classe Block, di cui è uno dei componenti necessari.
 L'associazione tra State e Block è di 1 a 1.

 ATTRIBUTI:
    _ID: string
    _damage: float [0:1]
    _state_value: string {Active, Inactive, Standby, Destroyed}

"""
from __future__ import annotations

import json
import pathlib
from datetime import date as _date, time as _time
from typing import Any, Dict, List, Optional, Tuple
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.Context.Context import (
    STATE,
     Ground_Action as ag,
    Air_To_Air_Task as a2a,
    Air_To_Ground_Task as atg,
    Sea_Task as asea,
)
from Code.Dynamic_War_Manager.Source.Asset import Asset
from Code.Dynamic_War_Manager.Source.Utility import Utility
from Code.Dynamic_War_Manager.Source.Context.Initial_Context import ASSET_AVAILABILITY

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Campaign_State')


"""
DATA STRUCTURE

_ASSET_AVAILABILITY: Dict[str, Tuple[float, float]] = {   

        'air': {at.FIGHTER.value: {
                    'F-14A Tomcat': 100,
                    'F-14B Tomcat': 100,        
                },
                at.FIGHTER_BOMBER.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,                                
        }, 

        'ground': {
                ag.TANK.value: {
                    'F-14A Tomcat': 100,
                    'F-14B Tomcat': 100,
                    },
                ag.ARMORED.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                },
                
        },

        'sea': {asea.CARRIER.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,                    
                },
                asea.DESTROYER.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,                    
                },                           
            },
}


    blocks_state = {
            "block_name": self.name,
            "block_id": self.id,            
            "side": self.side,                
            "category": self.category,
            "sub_category": self.sub_category,
            "military_category": self.get_military_category() if hasattr(self, 'get_military_category') else None,
            "functionality": self.functionality,
            "description": self.description,
            "position": self.position if report_item_probability['position'] else None,
            "dimension": self.dimension if hasattr(self, 'dimension') and report_item_probability['dimension'] else None,
            'efficiency': self.efficiency if hasattr(self, 'efficiency') and report_item_probability['efficiency'] else None,
            'morale': self.morale if hasattr(self, 'morale') and report_item_probability['morale'] else None,
            'health': self.health if hasattr(self, 'health') and report_item_probability['health'] else None,
            "state": self.state.state_value if self.state and report_item_probability['state'] else None,
            'combat_state': self.combat_state() if hasattr(self, 'combat_state') else None,            
            'intelligence': self.intelligence() if hasattr(self, 'intelligence') else None,            
            'recon_efficiency': self.get_recon_efficiency() if hasattr(self, 'get_recon_efficiency') else None,                      
            'communication_status': _communication.get('status') if _communication and report_item_probability['communication_status'] else None,
            "events": [event.description for event in self.events] if self.events and report_item_probability['events'] else None,
            "assets_state": { asset_id: asset_state_dict  },
            'supply_status': {
                'goods': _supply.get('goods', {}).get('status') if _supply and report_item_probability['supply_status'] else None,
                'energy': _supply.get('energy', {}).get('status') if _supply and report_item_probability['supply_status'] else None,
                'fuel': _supply.get('fuel', {}).get('status') if _supply and report_item_probability['supply_status'] else None,
                'hr': _supply.get('hr', {}).get('status') if _supply and report_item_probability['supply_status'] else None,    
                'hc': _supply.get('hc', {}).get('status') if _supply and report_item_probability['supply_status'] else None,    
                'hs': _supply.get('hs', {}).get('status') if _supply and report_item_probability['supply_status'] else None,    
                'hb': _supply.get('hb', {}).get('status') if _supply and report_item_probability['supply_status'] else None,    
            },            
            'defense_status': {
                'air_defense_volume': self.air_defense_volume() if hasattr(self, 'air_defense_volume') and report_item_probability['defense_status'] else None,
                'air_defense_aaa_range': self.air_defense_aaa_range() if hasattr(self, 'air_defense_aaa_range') and report_item_probability['defense_status'] else None,
                'combat_range': self.combat_range() if hasattr(self, 'combat_range') and report_item_probability['defense_status'] else None,
                'combat_volume': self.combat_volume() if hasattr(self, 'combat_volume') and report_item_probability['defense_status'] else None,
                'air_defense_aaa_volume': self.air_defense_aaa_volume() if hasattr(self, 'air_defense_aaa_volume') and report_item_probability['defense_status'] else None,
            },
        }




    Stores status_report snapshots for every block in every region, indexed by mission.

    La usi per le valutazioni strategiche e tattiche dopo ogni missione, per tenere traccia dell'evoluzione della campagna e per analizzare trend e pattern nei dati storici.

    Internal structure:
        _state: {
            mission_id: {
                "date":    str,    # ISO 8601 "YYYY-MM-DD"
                "time":    str,    # "HH:MM" or "HH:MM:SS"
                "regions": {
                    region_name: {
                        'attack_weight': float,
                        'weight_priority_target': Dict,
                        'blocks': {block_id: status_dict}
                        'routes': {route_id: status_dict}
                        'limes': {limes_id: status_dict}
                    }
                }
            }
        }

      ---
  Context/Campaign_History.py

  Struttura dati interna

  _history[mission_id] → { date, time, regions → { region_name → { block_id →
  status_report } } }                                                           
   
  API Write                                                                     

  ┌────────────────────────────────────────┬────────────────────────────────┐
  │                 Metodo                 │          Descrizione           │
  ├────────────────────────────────────────┼────────────────────────────────┤
  │                                        │ Aggiunge il report di un       │
  │ add_block_snapshot(mission_id, date,   │ singolo blocco; crea la        │
  │ time, region, block_id, report)        │ missione se non esiste; rileva │
  │                                        │  conflitti di data/ora         │
  ├────────────────────────────────────────┼────────────────────────────────┤
  │ add_region_snapshot(mission_id, date,  │ Aggiunge tutti i blocchi di    │
  │ time, region, blocks)                  │ una regione in un colpo        │
  │                                        │ ({block_id: report})           │
  └────────────────────────────────────────┴────────────────────────────────┘

  API Read

  ┌─────────────────────────────────────┬───────────────────────────────────┐
  │               Metodo                │              Ritorna              │
  ├─────────────────────────────────────┼───────────────────────────────────┤
  │ missions                            │ Lista di mission_id in ordine di  │
  │                                     │ inserimento                       │
  ├─────────────────────────────────────┼───────────────────────────────────┤
  │ get_mission(mission_id)             │ Snapshot completo della missione  │
  ├─────────────────────────────────────┼───────────────────────────────────┤
  │ get_region_snapshot(mission_id,     │ {block_id: report} per una        │
  │ region)                             │ regione                           │
  ├─────────────────────────────────────┼───────────────────────────────────┤
  │ get_block_snapshot(mission_id,      │ Report singolo o None             │
  │ region, block_id)                   │                                   │
  ├─────────────────────────────────────┼───────────────────────────────────┤
  │ get_block_history(region, block_id) │ Lista (mission_id, date, time,    │
  │                                     │ report) ordinata cronologicamente │
  ├─────────────────────────────────────┼───────────────────────────────────┤   
  │ get_field_trend(region, block_id,   │ Lista (mission_id, date, time,    │
  │ field)                              │ valore) per analisi trend (es.    │   
  │                                     │ "efficiency", "state")            │   
  └─────────────────────────────────────┴───────────────────────────────────┘
                                                                                
  Persistenza                                               

  ch.save("campaign_history.json")          # serializza su file JSON
  ch2 = CampaignHistory.load("campaign_history.json")  # ricarica      







    



"""



class Campaign_State:

    def __init__(self): 
        
        # property        
        self._last_mission = None
        self._last_mission_date = None
        self._last_mission_time = None
        


        self._last_asset_availability = {'air': {'asset_type': None, 'quantity': None}, 
                                            'ground': {'asset_type': None, 'quantity': None},
                                            'sea': {'asset_type': None, 'quantity': None}}
        
        self._asset_availability = {    'date': None, 
                                        'time':  None, 
                                        'mil_force': {  'air': None,
                                                        'ground': None,
                                                        'sea': None
                                                    }
                                    }
                                                   
        self._global_success_mission_ratio =    {"Red": 
                                                    {"Air": {"Air_To_Air": None, "Air_To_Ground": None, "Air_To_Sea": None},
                                                    "Ground": {ag.ATTACK.value: None, ag.DEFENSE.value: None,ag.MAINTAIN.value: None, ag.RETRAITE.value: None},   
                                                    "Sea": {asea.ATTACK.value: None, asea.DEFENSE.value: None, asea.RETRAIT.value: None},
                                                    },
                                                "Blue": 
                                                    {"Air_To_Air": None, "Air_To_Ground": None, "Air_To_Sea": None},
                                                    "Ground": {ag.ATTACK.value: None, ag.DEFENSE.value: None,ag.MAINTAIN.value: None, ag.RETRAITE.value: None},   
                                                    "Sea": {asea.ATTACK.value: None, asea.DEFENSE.value: None, asea.RETRAIT.value: None},
                                                }                                            
        self._global_damaged_asset_ratio = {"Red": {"Air": None,"Ground": None, "Sea": None},
                                              "Blue": {"Air": None,"Ground": None, "Sea": None},}
        
        
        # stato di tutti i blocchi, indicizzato per missione e regione, con i dati più aggiornati disponibili (snapshot dopo ogni missione)
        self._state: Dict[str, Dict] = {}

 
  
   
  
        

    # le funzionalità specifiche le "inietti" o crei delle specializzazioni (classi derivate)