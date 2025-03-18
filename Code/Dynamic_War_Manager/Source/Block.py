from __future__ import annotations
from typing import TYPE_CHECKING

from Code import Context
from numpy import median
import Utility, Sphere, Hemisphere
from Dynamic_War_Manager.Source.State import State
from LoggerClass import Logger
from Dynamic_War_Manager.Source.Event import Event
from Dynamic_War_Manager.Source.Payload import Payload
from Context import STATE, BLOCK_CATEGORY, SIDE
from typing import Literal, List, Dict
from sympy import Point, Line, Point3D, Line3D, symbols, solve, Eq, sqrt, And



if TYPE_CHECKING:    
    from Dynamic_War_Manager.Source.Asset import Asset
    from Dynamic_War_Manager.Source.Region import Region
    from Dynamic_War_Manager.Source.Mil_Base import Mil_Base
    from Dynamic_War_Manager.Source.Production import Production
    from Dynamic_War_Manager.Source.Storage import Storage
    from Dynamic_War_Manager.Source.Transport import Transport
    from Dynamic_War_Manager.Source.Urban import Urban

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Block')

# ASSET o BLOCK
class Block:    

    def __init__(self, name: str|None, description: str|None, side: str |None, category: str|None, functionality: str|None, value: int|None, region: Region|None):

            # propriety
            self._name = name # block name - type str
            self._id = None # id self-assigned - type str
            self._description = description # block description - type str
            self._side = side # block side - type str
            self._category = category # block category - type Literal 
            self._functionality = functionality # block functionality - type str
            self._value = value # block value - type int             
            self._events = List[Event] = [] # block event - list of Block event's          

              
            # Association  
            self._assets = Dict[str, Asset] = {} # assets - component of Block - type list forse è meglio un dict
            self._region = region # block map region - type Region


            if not name:
                self._name = Utility.setName('Unnamed_Block')

            else:
                self._name = "Block." + name

            self._id = Utility.setId(self._name)
           
            if not side:
                side = "Neutral"
            # check input parameters            
            check_results =  self.checkParam( name, description, side, category, functionality, value, region )            
            
            if not check_results[1]:
                raise Exception("Invalid parameters: " +  check_results[2] + ". Object not istantiate.")
                       

    # methods
  
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
        
        check_result = self.checkParam(description = param)
        
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

        for asset in self.assets:
            cost += asset.cost

        return cost
    
    @cost.setter
    def cost(self, cost):
        raise ValueError("cost not modifiable for Block")
    

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
        # restituisce acp calcolato in base agli assets
        return self.updatePayload(destination = "acp")
        


    @property
    def rcp(self) -> Payload:
        # restituisce rcp calcolato in base agli assets
        return self.updatePayload(destination = "rcp")


        check_result = self.checkParam(rcp = param)
        
        if not check_result[1]:
            raise Exception(check_result[2])    
        else:
            self._rcp = param           
            # payload.parent = self NO si crea un riferimento circolare in cui i due metodi setter delle classi associate si richiamano tra loro con loop ricorsivamente
            # L'assegnazione del link di payload a Block è demandata unicamente al setter di payload

        return True
    


    @property
    def payload(self) -> Payload:
        # restituisce payload calcolato in base agli assets
        return self.updatePayload(destination = "payload")

    

        check_result = self.checkParam(payload = param)
        
        if not check_result[1]:
            raise Exception(check_result[2])    
        else:
            self._payload = param             
            # payload.parent = self NO si crea un riferimento circolare in cui i due metodi setter delle classi associate si richiamano tra loro con loop ricorsivamente
            # L'assegnazione del link di payload a Block è demandata unicamente al setter di payload

        return True
    @property
    def state(self):

        state = State
        pre = True
        n_mission = None
        date_mission = None

        for asset in self.assets:
            
            if pre:
                n_mission = asset.state.n_mmission
                date_mission = asset.date_mission
                pre = False
            else:
                if n_mission != asset.state.n_mmission:
                    raise Exception(f"asset {0} {1} has different state.n_mission {2} from previous asset: {3}".format(asset.id, asset.name, asset.state.n_mmission, n_mission))
                if date_mission != asset.state.date_mmission:
                    raise Exception(f"asset {0} {1} has different state.date_mission {2} from previous asset: {3}".format(asset.id, asset.name, asset.state.date_mmission, date_mission))

            state.damage += asset.state.damage
        
        state.n_mission = n_mission
        state.date_mission = date_mission
        state.damage /= len(self.assets) # la media dovrebbe essere pesata in funzine dell'importanza dell'asset

        return state



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
    def region(self, param: Region) -> bool:

        check_result = self.checkParam(region = param)
        
        if not check_result[1]:
            raise Exception(check_result[2])    
        
        self._region = param       
            
        return True


    def toString(self):
        return 'Name: {0}  -  Id: {1} - value: {2} \n description: {3}\n category: {4}\n'.format(self.name, self.id, self.value, self.description, self.category)
    
    def checkClass(self, object):
        """Return True if objects is a Object object otherwise False"""
        return type(object) == type(self)
        
    def checkClassList(self, objects):
        """Return True if objectsobject is a list of Block object otherwise False"""
        return all(type(obj) == type(self) for obj in objects)


     # vedi il libro
    
    def checkParam(self, name: str, description: str, side: str, category: Literal, function: str, value: int, position: Point, acp: Payload, rcp: Payload, payload: Payload, region: Region) -> bool: # type: ignore
        """Return True if type compliance of the parameters is verified"""   
                   
        if name and not isinstance(name, str):
            return (False, "Bad Arg: name must be a str")
        if description and not isinstance(description, str):
            return (False, "Bad Arg: description must be a str")
        if side and (not isinstance(side, str) or side not in SIDE):
            return (False, "Bad Arg: side must be a str with value: Blue, Red or Neutral")
        if category and (not isinstance(category, Literal) or category not in [BLOCK_CATEGORY]):                        
            return (False, "Bad Arg: category must be a Literal.CATEGORY or Literal.MIL_CATEGORY")        
        if function and not isinstance(function, str):
            return (False, "Bad Arg: function must be a str")
        if value and not isinstance(value, int):
            return (False, "Bad Arg: value must be a int")
        if position and not isinstance(position, Point):
            return (False, "Bad Arg: position must be a Point object")
        if region and not isinstance(region, Region):
            return (False, "Bad Arg: region must be a Region object")
            
        return (True, "OK")

    def getEfficiency(self): # sostituisce operational()
        """calculate efficiency from asset state, rcp, acp, .."""
        efficiency = median(asset.getEfficiency() for asset in self.assets) 
        return efficiency
          
    def assetStatus(self):
        """calculate Asset_Status from asset Asset_Status"""
        # as = median(Asset_Status) 
        # return as
        pass

    def threatVolume(self):
        """calculate Threat_Volume from asset Threat_Volume"""
        # tv = max(assetThreat_Volume) 
        # return tv
        pass

    @property
    def position(self):
        """calculate center point from assets position"""        
        return median(asset.position for asset in self.assets) 
    
    @property
    def morale(self):     
        return median(asset.morale for asset in self.assets)
        
    def efficiency(self):    
        return median(asset.efficiency for asset in self.assets)

    def getBlockInfo(self, request: str, asset_Number_Accuracy: float, asset_Efficiency_Accuracy: float):    
        """ Defined in each subclass """
        return self.name, self.id
    
    def enemySide(self):
        """
        Determine and return the side that is considered the enemy.
        """
        return Utility.enemySide(self.side)
            

    def balance_trade(self):        

        goods = None, energy = None, hr = None, hc = None, hs = None, hb = None
        self.loadRcp # update rcp value        
        
        if self.rcp.goods > 0:
            goods = self.acp.goods / self.rcp.goods
        
        if self.rcp.energy > 0:
            energy = self.acp.energy / self.rcp.energy

        if self.rcp.hr > 0:
            hr = self.acp.hr / self.rcp.hr

        if self.rcp.hc > 0:
            hc = self.acp.hc / self.rcp.hc

        if self.rcp.hs > 0:
            hs = self.acp.hs / self.rcp.hs

        if self.rcp.hb > 0:
            hb = self.acp.hb / self.rcp.hb

        variables =  [goods, energy, hr, hc, hs, hb]

        balances = [v for v in variables if v is not None]        
        balance = sum(balances) / len(balances)

        return balance

    def isMilitary(self):
        return (self.category == "Military") or isinstance(self, Mil_Base)
    
    def isLogistic(self):
        return any[isinstance(self, Context.BLOCK_CLASS["Production"]), isinstance(self, Context.BLOCK_CLASS["Storage"]), isinstance(self, Context.BLOCK_CLASS["Transport"])]
    
    def isCivilian(self):
        return isinstance(self, Urban)
        
