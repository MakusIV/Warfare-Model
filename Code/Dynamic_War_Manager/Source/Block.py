from __future__ import annotations
from typing import TYPE_CHECKING
import sys
import os
# Aggiungi il percorso della directory principale del progetto
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from Code import Context, Utility
from numpy import mean
from Code.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.Event import Event
from Code.Dynamic_War_Manager.Source.Payload import Payload
from Code.Context import BLOCK_CATEGORY, SIDE, BLOCK_ASSET_CATEGORY
from typing import List, Dict
from sympy import Point

if TYPE_CHECKING:    
    from Code.Dynamic_War_Manager.Source.Asset import Asset
    from Code.Dynamic_War_Manager.Source.Region import Region

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Block')

# ASSET o BLOCK (non deve essere istanziata: solo le derivate)
class Block:    

    def __init__(self, name: str|None, description: str|None, side: str |None, category: str|None, sub_category: str|None, functionality: str|None, value: int|None, region: "Region"|None):

            # propriety
            self._name: str = name # block name - type str
            self._id = None # id self-assigned - type str
            self._description: str = description # block description - type str
            self._side: str = side # block side - type str
            self._category: str = category # block category - (Civilian, Logistic, Military, All)
            
            self._sub_category: str = sub_category # Road, Railway, Airport, Electric, Power_Plant, Factory, Administrative, Service, Stronghold, Farp ,...
            self._functionality:str = functionality # block functionality - type str
            self._value: int = value # strategical value of block- type int (nota non è riferito al value dei singoli asset ma dovrebbe rappresentare un valore strategico rispetto gli altri blocchi)            
            self._events: List[Event] = [] # block event - list of Block event's    

              
            # Association  
            self._assets: Dict[str, Asset] = {} # assets - component of Block - type list forse è meglio un dict
            self._region = region # block map region - type Region


            if not name:
                self._name = Utility.setName('Unnamed')

            else:
                self._name = name

            self._id = Utility.setId(self._name, None)
           
            if not side:
                side = "Neutral"
            # check input parameters            
            check_results =  self.checkParam( name, description, side, category, sub_category, functionality, value, region )            
            
            if not check_results[1]:
                raise Exception("Invalid parameters: " +  check_results[2] + ". Object not istantiate.")
                       

    # methods
    @property
    def block_class(self):
        return self.__class__.__name__ #(Production, Transport, Storage, Urban, Mil_Base)
  
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, param):

        check_result = self.checkParam(name = param)
        
        if not check_result[1]:
            raise Exception(check_result[2])    

        self._name = param  
        return True
            
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, param):

        check_result = self.checkParam(id = param)
        
        if not check_result[1]:
            raise Exception(check_result[2])    

        
        self._id = str(param)
            
        return True
    
    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, param):

        check_result = self.checkParam(description = param)
        
        if not check_result[1]:
            raise Exception(check_result[2])    

        
        self._description = param       
            
        return True
    
    @property
    def side(self):
        return self._side

    @side.setter
    def side(self, param):
        
        check_result = self.checkParam(side = param)
        
        if not check_result[1]:
            raise Exception(check_result[2])    

        
        self._description = param       
            
        return True

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, param):

        check_result = self.checkParam(category = param)
        
        if not check_result[1]:
            raise Exception(check_result[2])    

        self._category = param

        return True
    
    @property
    def sub_category(self):
        return self._sub_category

    @sub_category.setter
    def sub_category(self, param):

        check_result = self.checkParam(sub_category = param)
        
        if not check_result[1]:
            raise Exception(check_result[2])    

        self._sub_category = param

        return True
    


    @property
    def functionality(self):
        return self._functionality

    @functionality.setter
    def functionality(self, param):

        check_result = self.checkParam(functionality = param)
        
        if not check_result[1]:
            raise Exception(check_result[2])    


        self._functionality = param  
            
        return True
    

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, param):

        check_result = self.checkParam(value = param)
        
        if not check_result[1]:
            raise Exception(check_result[2])    
    
        self._value = param            
        return True


    @property
    def events(self):
        return self._events

    @events.setter
    def events(self, value):
        if isinstance(value, list):
            self._events = value
        else:
            raise ValueError("Il valore deve essere una lista")

    def addEvent(self, event):
        if isinstance(event, Event):
            self._events.append(event)
        else:
            raise ValueError("Il valore deve essere un oggetto di tipo Event")

    def getLastEvent(self):
        if self._events:
            return self._events[-1]
        else:
            raise IndexError("La lista è vuota")

    def getEvent(self, index):
        if index < len(self._events):
            return self._events[index]
        else:
            raise IndexError("Indice fuori range")

    def removeEvent(self, event):
        if event in self._events:
            self._events.remove(event)
        else:
            raise ValueError("L'evento non esiste nella lista")


    @property
    def cost(self) -> int:
        cost = 0

        for asset in self.assets.values():
            cost += asset.cost

        return cost
    
    @cost.setter
    def cost(self, cost):
        raise ValueError("cost not modifiable for Block")
    
    # ma che roba è??
    #ELIMINARE
    def updatePayload(self, destination: str):
        
        req = Payload

        for asset in self.assets:

            if destination == "acp":
                dest = asset.acp
            elif destination == "rcp":
                dest = asset.rcp
            elif destination == "payload":
                dest = asset.payload
            else:
                raise Exception(f"destination {0} mus be a string: acp, or payload".format(destination))

            req.energy += dest.energy
            req.goods += dest.goods
            req.hr += dest.hr
            req.hc += dest.hc
            req.hs += dest.hs
            req.hb += dest.hb

        return req


    
    @property
    def acp(self) -> Payload:
        """Assigned Consume Payload
        Assigned Consume Payload is the payload that the block can consume.
        acp = sum(acp of all assets)

        Returns:
            Payload: object acp
        """      
        # restituisce acp calcolato in base agli assets
        return self.updatePayload(destination = "acp")
        


    @property
    def rcp(self) -> Payload:
         
        """Required Consume Payload
        Required Consume Payload is the payload that the block needs to consume
        rcp = sum(rcp of all assets)
        
        Returns:
            Payload: object rcp
        """        
        # restituisce rcp calcolato in base agli assets
        return self.updatePayload(destination = "rcp")


    @property
    def payload(self) -> Payload:
        """Payload is the payload that the block must manage (transport, trasformation)
        payload = sum(payload of all assets)
        
        Returns:
            Payload: object payload
        """     
        # restituisce payload calcolato in base agli assets
        return self.updatePayload(destination = "payload")

    
    @property
    def state(self):
        state = State
        pre = True
        n_mission = None
        date_mission = None

        for asset in self.assets:                        
            state.damage += asset.state.damage
        
        state.n_mission = n_mission
        state.date_mission = date_mission
        state.damage /= len(self.assets) # la media dovrebbe essere pesata in funzine dell'importanza dell'asset
        return {"name": self._name, "id": self.id, "category": self._category, "role": self._role, "health": self._health, "efficiency": self.efficiency, "balance_trade": self.balance_trade, "position": self._position}



    @property
    def assets(self):
        return self._assets
    
    @assets.setter
    def assets(self, value):
        if isinstance(value, dict) and all(isinstance(asset, Asset) for asset in value.values()):
            self._assets = value
        else:
            raise ValueError("Il valore deve essere un dizionario")


    def listAssetKeys(self) -> list[str]:
        """Restituisce la lista degli identificatori associati."""
        return list(self._assets.keys())


    def getAsset(self, key):
        if key in self._assets:
            return self._assets[key]
        else:
            raise KeyError(f"L'asset {key} non esiste in assets")

    def setAsset(self, key, value):

        from Code.Dynamic_War_Manager.Source.Asset import Asset

        if isinstance(value, Asset):
            self._assets[key] = value
            value.block = self 
        else:
            raise ValueError("Il valore deve essere un Asset")  

    def removeAsset(self, key):
        if key in self._assets:
            self._assets[key].block = None
            del self._assets[key]
        else:
            raise KeyError(f"L'asset {key} non esiste nel dizionario")
  

    @property
    def region(self):
        return self._region

    @region.setter
    def region(self, param: "Region") -> bool:

        check_result = self.checkParam(region = param)
        
        if not check_result[1]:
            raise Exception(check_result[2])    
                
        self._region = param       
            
        return True
    
    
    def __repr__(self):
        """
        Rappresentazione ufficiale dell'oggetto Block.
        Utile per il debugging.
        """
        return (f"Block - name: {self._name!r}, id: {self._id!r}, side: {self._side!r}, category: {self._category!r}, functionality: {self._functionality!r}, value={self._value!r})")

    def __str__(self):
        """
        Rappresentazione leggibile dell'oggetto Block.
        Utile per l'utente finale.
        """
        return (f"Block Information:\n"
                f"  Name: {self._name}\n"
                f"  ID: {self._id}\n"
                f"  Side: {self._side}\n"
                f"  Category: {self._category}\n"
                f"  Functionality: {self._category}\n"
                f"  Value: {self._value}\n"
                f"  Description: {self._description}")
    
    def checkClass(self, object):
        """Return True if objects is a Object object otherwise False"""
        return type(object) == type(self)
        
    def checkClassList(self, objects):
        """Return True if objectsobject is a list of Block object otherwise False"""
        return all(type(obj) == type(self) for obj in objects)


     # vedi il libro
    
    def checkParam(self, name: str = None, description: str = None, side: str = None, category: str = None, sub_category: str = None, function: str = None, value: int = None, region: "Region" = None) -> (bool, str): # type: ignore
        """Return True if type compliance of the parameters is verified"""   
        from Code.Dynamic_War_Manager.Source.Region import Region
        from Code.Dynamic_War_Manager.Source.Asset import Asset      

        if name and not isinstance(name, str):
            return (False, "Bad Arg: name must be a str")
        if description and not isinstance(description, str):
            return (False, "Bad Arg: description must be a str")
        if side and (not isinstance(side, str) or side not in SIDE):
            return (False, "Bad Arg: side must be a str with value: Blue, Red or Neutral")
        if category and not isinstance(category, str) and (category not in [BLOCK_CATEGORY]):                        
            return (False, "Bad Arg: category must be a BLOCK_CATEGORY: {0}".format(bc for bc in BLOCK_CATEGORY))        
        if sub_category and not isinstance(sub_category, str) and (sub_category not in BLOCK_ASSET_CATEGORY[self.block_class].keys()):                        
            return (False, "Bad Arg: category must be a BLOCK_CATEGORY: {0}".format(bc for bc in BLOCK_ASSET_CATEGORY[self.block_class].keys()))        
        if function and not isinstance(function, str):
            return (False, "Bad Arg: function must be a str")
        if value and not isinstance(value, int):
            return (False, "Bad Arg: value must be a float")
        if region and not isinstance(region, Region):
            return (False, "Bad Arg: region must be a Region object")
            
        return (True, "OK")      

    def threatVolume(self):
        """calculate Threat_Volume from asset Threat_Volume"""
        # tv = max(assetThreat_Volume) 
        # return tv
        pass

    @property
    def position(self):
        """calculate center point from assets position"""        
        return Utility.mean_point([asset.position for asset in self.assets.values()]) 
    

    @property
    def morale(self):             
        return Utility.evaluateMorale(State.success_ratio[self], self.efficiency) # mission success ratio recordered for this object
        
    @property
    def efficiency(self):    
        return mean([asset.efficiency for asset in self.assets.values()])

    def getBlockInfo(self, request: str, asset_Number_Accuracy: float, asset_Efficiency_Accuracy: float):    
        """ Defined in each subclass """
        return self.name, self.id
    
    def enemySide(self):
        """
        Determine and return the side that is considered the enemy.
        """
        return Utility.enemySide(self.side)
            
    @property
    def balance_trade(self):        
        """Returns median value of balance ratio (acp/rcp) of the assets

        Returns:
            float: balance trade ratio
        """        
        #balance = 0
        #for asset in self.assets:
        #    balance += asset.balance_trade
        #return balance/len(self.assets)

        return mean([asset.balance_trade for asset in self.assets.values()]) 

        

    def isMilitary(self):
        return (self.category == Context.BLOCK_CLASS["Mil_Base"])
    
    def isLogistic(self):
        return self.category == Context.BLOCK_CLASS["Production"] or self.category == Context.BLOCK_CLASS["Storage"] or self.category == Context.BLOCK_CLASS["Transport"]
    
    def isCivilian(self):
        return self.category == Context.BLOCK_CLASS["Urban"]

