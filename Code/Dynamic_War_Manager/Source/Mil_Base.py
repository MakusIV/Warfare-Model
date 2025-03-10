import datetime

from numpy import median
from Dynamic_War_Manager.Source.Block import Block
import Utility, Sphere, Hemisphere, random
from Dynamic_War_Manager.Source.Strategical_Evaluation import evaluateRecoMissionRatio # cambiare in Scenario_Military_Evaluation
from Dynamic_War_Manager.Source.Tactical_Evaluation import calcRecoAccuracy, evaluateCombatSuperiority, evaluateGroundTacticalAction, evaluateCriticality # cambiare in Mil_Zone_Evaluation
from Dynamic_War_Manager.Source.State import State
from LoggerClass import Logger
from Dynamic_War_Manager.Source.Event import Event
from Dynamic_War_Manager.Source.Payload import Payload
from Context import STATE, MIL_CATEGORY, GROUND_ASSET_CATEGORY, AIR_ASSET_CATEGORY
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

    

    def checkParam(name: str, description: str, side: str, category: Literal, function: str, value: int, position: Point, acs: Payload, rcs: Payload, payload: Payload, volume: Volume, threat: Threat, crytical: bool, repair_time: int) -> bool: # type: ignore
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
    

    def assetStatus(self):
        """report info on any mil-base assets category (aircraft, vehicle, supply, ...)"""
        # as = .... 
        # return as
        pass

    def threatVolume(self):
        """calculate Threat_Volume from asset Threat_Volume"""
        # tv = max(assetThreat_Volume) 
        # return tv
        pass

    def front(self):
        """calculate"""
        # ap = median(assetPosition) 
        # return ap
        pass

    def combatState(self):
        """calculate front from state of assets"""

    
    def getRecon(self) -> Dict:
        """Return a List of recon report of enemy asset near this block with detailed info: qty, type, efficiency, range, status resupply:
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
        enemy_blocks = self.region.getEnemyBlocks(self.getEnemySide())
        report_base = self.getBlockInfo("friendly_request")          
        recon_reports = { "attack": (), "defence": () }
        
        for enmy_block in enemy_blocks:

            report_enemy = enmy_block.getBlockInfo("enemy_request",  asset_Number_Accuracy, asset_Efficiency_Accuracy)            
            criticality = evaluateCriticality(report_base, report_enemy)                                    
            i = 0
            previous_reports = recon_reports[criticality["action"]]

            while i < len(previous_reports):# prima posizone index = 0
                            
                if criticality["value"] == previous_reports[i].criticality["value"]: 
                    recon_reports[criticality["action"]].insert( i, report_enemy )# verifica se scala i successivi
                    break
                elif criticality["value"] < previous_reports[i].criticality["value"] and criticality["value"] <= previous_reports[i].criticality["value"]: 
                    recon_reports[criticality["action"]].insert( i + 1, report_enemy )# verifica se scala i successivi
                    break
                i += 1
            
        return recon_reports
               

    def getBlockInfo(self, request: str, asset_Number_Accuracy: float, asset_Efficiency_Accuracy: float):    
        """ Return a List of enemy asset near this block with detailed info: qty, type, efficiency, range, status resupply. Override Block.getBlockInfo()"""

        report = {
            "reporter name": self.side + "_" + self.name + "_" + self.state.n_mission + "_" + self.state.date_mission,
            "radius area": 0.0,
            "center area": 0.0,
            "military category": self.category, 
            "air distance": 0.0,
            "on road ground distance": 0.0,
            "off road ground distance": 0.0,
            "artillery range": 0.0,
            "combat range": 0.0,
            "AA range": 0.0,
            "AA height": 0.0,
            "criticality": { "action": None, "value": 0 }, # action = ["attack", "defence"], value int [1-100]              
            "asset": {
                GROUND_ASSET_CATEGORY["Tank"]: {"Number": 0, "Efficiency": 0},
                GROUND_ASSET_CATEGORY["Armor"]: {"Number": 0, "Efficiency": 0},
                GROUND_ASSET_CATEGORY["Motorized"]: {"Number": 0, "Efficiency": 0}, 
                GROUND_ASSET_CATEGORY["Artillery_Fix"]: {"Number": 0, "Efficiency": 0}, 
                GROUND_ASSET_CATEGORY["Artillery_Semovent"]: {"Number": 0, "Efficiency": 0}, 
                GROUND_ASSET_CATEGORY["Command_&_Control"]: {"Number": 0, "Efficiency": 0}, 
                GROUND_ASSET_CATEGORY["SAM"]: {"Number": 0, "Efficiency": 0}, 
                GROUND_ASSET_CATEGORY["AAA"]: {"Number": 0, "Efficiency": 0},                    
                GROUND_ASSET_CATEGORY["EWR"]: {"Number": 0, "Efficiency": 0}, 
                AIR_ASSET_CATEGORY["Fighter"]: {"Number": 0, "Efficiency": 0}, 
                AIR_ASSET_CATEGORY["Fighter_Bomber"]: {"Number": 0, "Efficiency": 0}, 
                AIR_ASSET_CATEGORY["Attacker"]: {"Number": 0, "Efficiency": 0}, 
                AIR_ASSET_CATEGORY["Bomber"]: {"Number": 0, "Efficiency": 0}, 
                AIR_ASSET_CATEGORY["Heavy_Bomber"]: {"Number": 0, "Efficiency": 0}, 
                AIR_ASSET_CATEGORY["Awacs"]: {"Number": 0, "Efficiency": 0}, 
                AIR_ASSET_CATEGORY["Recon"]: {"Number": 0, "Efficiency": 0}, 
                AIR_ASSET_CATEGORY["Transport"]: {"Number": 0, "Efficiency": 0}, 
                AIR_ASSET_CATEGORY["Helicopter"]: {"Number": 0, "Efficiency": 0},                                                
            }
        }
        
        # calculate total number and efficiency for each assets category: Tank, Armor, Motorized, ...
        for asset in self.assets:        
            category = asset.category # Tank, Armor, Motorized, Artillery, SAM, AAA, Fighter, Fighter_Bomber, Attacker, Bomber, Heavy_Bomber, Awacs, Recon, Transport, Command_&_Control            
            efficiency = asset.getEfficiency()
            report["asset"][category]["Number"] += 1
            report["asset"][category]["Efficiency"] += efficiency

        
        # update efficiency and number for each category of asset
        for category in GROUND_ASSET_CATEGORY:
 
            if request == "enemy_request": # if it's an enemy request update efficiency and number with random error                                
                efficiency_error = random.choice([-1, 1]) * random.uniform(0, asset_Efficiency_Accuracy)
                number_error = random.choice([-1, 1]) * random.uniform(0, asset_Number_Accuracy)
                report["asset"][category]["Efficiency"] = report["asset"]["Efficiency"] * (1 + efficiency_error) / report["asset"]["Number"]
                report["asset"][category]["Number"] = report["asset"]["Number"] * (1 + number_error)
                    
        return report
            

    def getReconEfficiency(self):
        """Return the efficiency of the reconnaissance assets"""

        recognitors = [asset for asset in self.assets if asset.role == "Recon"]
        efficiency = median(asset.getEfficiency("hr_mil") for asset in recognitors)
        return efficiency
