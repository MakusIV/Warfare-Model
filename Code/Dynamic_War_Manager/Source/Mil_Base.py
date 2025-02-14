from Dynamic_War_Manager.Source.Block import Block
import Utility, Sphere, Hemisphere, random
from Dynamic_War_Manager.Source.Strategical_Evaluation import evaluateRecoMissionRatio # cambiare in Scenario_Military_Evaluation
from Dynamic_War_Manager.Source.Tactical_Evaluation import calcRecoAccuracy # cambiare in Zone_Military_Evaluation
from Dynamic_War_Manager.Source.State import State
from LoggerClass import Logger
from Dynamic_War_Manager.Source.Event import Event
from Dynamic_War_Manager.Source.Payload import Payload
from Context import STATE, MIL_CATEGORY, GROUND_ASSET_CATEGORY
from typing import Literal, List, Dict
from sympy import Point, Line, Point3D, Line3D, Sphere, symbols, solve, Eq, sqrt, And
from Dynamic_War_Manager.Source.Asset import Asset
from Dynamic_War_Manager.Source.Region import Region
from Dynamic_War_Manager.Source.Volume import Volume


# LOGGING -- 
logger = Logger(module_name = __name__, class_name = 'Mil_Base')

# ASSET
class Mil_Base(Block) :    

    def __init__(self, block: Block, name: str|None, side: str|None, description: str|None, category: str|None, functionality: str|None, value: int|None, acp: Payload|None, rcp: Payload|None, payload: Payload|None, region: Region|None):   
            
            super().__init__(name, description, side, category, functionality, value, acp, rcp, payload)

            # propriety             
            
    
            # Association    
            
            if not name:
                self._name = Utility.setName('Unnamed_Mil_Base')

            else:
                self._name = "Mil_Base." + name

            self._id = Utility.setId(self._name)
                       

    # methods

    

    def checkParam(name: str, description: str, side: str, category: Literal, function: str, value: int, position: Point, acs: Payload, rcs: Payload, payload: Payload, position: Point, volume: Volume, threat: Threat, crytical: bool, repair_time: int) -> bool: # type: ignore
        """Return True if type compliance of the parameters is verified"""   
    
        if not super().checkParam(name, description, side, category, function, value, position, acs, rcs, payload):
            return False     
        
        return True
    
    
    def efficiency(self): # sostituisce operational()
        """calculate efficiency from asset state, rcp, acp, .."""
        # efficiency = state * acp / rcp
        # return efficiency
        pass
        

    def airDefence(self):
        """calculate air defense Volume from asset air defense volume"""
        # adsVolume = asset.air_defense from asset in self.assets 
        # adMax = max(adsVolume.range for adsVolume in adsVolume)
        # return adsVolume, adMax
        pass

    def combatRange(self, type: str = Artillery, height: int = 0):
        """calculate combat range from asset position"""    
        # return combatVolume(type=type).range(height=height)         
        pass

    

    def defenseAARange(self, height: int = 0):
        """calculate combat range from assets"""    
        # return defenceAAVolume().range(height=height)         
        pass

    def combatVolume(self, type: str = Artillery):
        """calculate combat volume from asset"""
        # distinguere tra arty, mech, motorized, 
        pass
    
    def defenceAAVolume(self):
        """return defense volume from asset"""    
        pass


    def position(self):
        """calculate position from asset position"""
        # ap = median(assetPosition) 
        # return ap
        pass


    def morale(self): # sostituisce operational()
        """calculate morale from region's members"""
        # morale = median(block.morale for block in blocks)
        # return morale
        pass
        

    def intelligence(self):
        """calculate intelligence level"""
        # intelligence_level = median(asset.efficiency for asset in assets.recognitor())
        # return intelligence_level
        pass
    
    def recognition(self):
        """calculate recognition report"""
        # f(intelligenze, evaluate neightroom, front)
        # return Dict{evaluate.enemy.asset.position, evaluate.enemy.asset.category, evaluate.enemy.asset.class, evaluate.enemy.asset.type, evaluate.enemy.asset.status, evaluate.enemy.asset.qty, evaluate.enemy.asset.efficiency}
        pass
    

    def asset_status(self):
        """report info on any mil-base assets category (aircraft, vehicle, supply, ...)"""
        # as = .... 
        # return as
        pass

    def threat_volume(self):
        """calculate Threat_Volume from asset Threat_Volume"""
        # tv = max(assetThreat_Volume) 
        # return tv
        pass

    def front(self):
        """calculate"""
        # ap = median(assetPosition) 
        # return ap
        pass

    def combat_state(self):
        """calculate front from state of assets"""

    
    def getRecon(self) -> Dict:
        """Return a List of enemy asset near this block with detailed info: qty, type, efficiency, range, status resupply:
        e.g.:
        [1]:
            name_group: xxxx
            type: Armor Brigade
            comand&control: n, efficiency
            tank: n, efficiency
            armor: n, efficiency
            motorized: n, efficiency
            artillery: n, efficiency
            sam: n, efficiency, class: low
            aaa: n, efficiency
            storage: n, efficiency
            supply line: n, efficiency
            combat_range: x 
            distance: y # calcolata in base a roads (lì'offroads può essere considerato solo per brevissime distanze)
            estimated_running_time: (hour, mission) #

        
        """
        success_Mission_Recon_Ratio = evaluateRecoMissionRatio(self.side, self.region.name)
        recon_Asset_Efficiency = self.getReconEfficiency()
        asset_Number_Accuracy = calcRecoAccuracy("Number", success_Mission_Recon_Ratio, recon_Asset_Efficiency)
        asset_Efficiency_Accuracy = calcRecoAccuracy("Efficiency", success_Mission_Recon_Ratio, recon_Asset_Efficiency)
        enemy_bases = self.region.front.getEnemyBases()
        
        for enemy_base in enemy_bases:
            recon_info = enemy_base.getBaseInfo("enemy_request", asset_Number_Accuracy, asset_Efficiency_Accuracy)
            # evaluate force ratio self/enemy
            # elaborate recon_Report

        pass

    def getBaseInfo(self, request: str, asset_Number_Accuracy: float, asset_Efficiency_Accuracy: float):    

        report = {
            "Name": self.name + datetime.now(),
            "Area": None,
            "Military Category": self.category,
            
            
            "Asset": {"Tank": 0, "Armor": 0, "Motorized": 0, "Artillery": 0, "SAM": 0, "AAA": 0, "Fighter": 0, "Fighter_Bomber": 0, "Attacker": 0, "Bomber": 0, "Heavy_Bomber": 0, "Awacs": 0, "Recon": 0, "Transport": 0, "Command_&_Control": 0},
                  
                  
                  }

        for asset in self.assets:        
            category = asset.category # Tank, Armor, Motorized, Artillery, SAM, AAA, Fighter, Fighter_Bomber, Attacker, Bomber, Heavy_Bomber, Awacs, Recon, Transport, Command_&_Control            
            efficiency = asset.efficiency
            report["Asset"][category]["Number"] += 1
            report["Asset"][category]["Efficiency"] += efficiency

        

        for category in GROUND_ASSET_CATEGORY:

            if request == "enemy_request":                                
                efficiency_error = random.choice([-1, 1]) * random.uniform(0, asset_Efficiency_Accuracy)
                number_error = random.choice([-1, 1]) * random.uniform(0, asset_Number_Accuracy)
                report["Asset"][category]["Efficiency"] = report["Asset"]["Efficiency"] * (1 + efficiency_error) / report["Asset"]["Number"]
                report["Asset"][category]["Number"] = report["Asset"]["Number"] * (1 + number_error)

        

            

    def getTacticalReport(self, intelligence_level) -> Dict:
        """Return a tactical report of the
         in base  a intelligence_level"""
