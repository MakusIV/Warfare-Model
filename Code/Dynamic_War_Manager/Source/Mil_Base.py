import datetime

from numpy import median
from heapq import heappop, heappush
from Dynamic_War_Manager.Source.Block import Block
import Utility, Sphere, Hemisphere, random
from Dynamic_War_Manager.Source.Strategical_Evaluation import evaluateRecoMissionRatio # cambiare in Scenario_Military_Evaluation
from Dynamic_War_Manager.Source.Tactical_Evaluation import calcRecoAccuracy, evaluateCombatSuperiority, evaluateGroundTacticalAction, evaluateCriticalityGroundEnemy, evaluateCriticalityAirDefence # cambiare in Mil_Zone_Evaluation
from Dynamic_War_Manager.Source.State import State
from LoggerClass import Logger
from Dynamic_War_Manager.Source.Event import Event
from Dynamic_War_Manager.Source.Payload import Payload
from Context import STATE, MIL_BASE_CATEGORY, GROUND_ASSET_CATEGORY, AIR_ASSET_CATEGORY, COMBAT_EFFICACY, GROUND_ACTION
from typing import Literal, List, Dict
from sympy import Point, Line, Point3D, Line3D, Sphere, symbols, solve, Eq, sqrt, And
from Dynamic_War_Manager.Source.Asset import Asset
from Dynamic_War_Manager.Source.Region import Region
from Dynamic_War_Manager.Source.Volume import Volume
from Dynamic_War_Manager.Source.Vehicle import Vehicle


# LOGGING -- 
logger = Logger(module_name = __name__, class_name = 'Mil_Base')

# ASSET
class Mil_Base(Block) :    

    def __init__(self, block: Block, mil_category: str, name: str|None, side: str|None, description: str|None, category: str|None, functionality: str|None, value: int|None, acp: Payload|None, rcp: Payload|None, payload: Payload|None, region: Region|None):   
            
            super().__init__(name, description, side, category, functionality, value, acp, rcp, payload)

            # propriety             
            
    
            # Association    
            
            if not name:
                self._name = Utility.setName('Unnamed_Mil_Base')

            else:
                self._name = "Mil_Base." + name

            self._id = Utility.setId(self._name)

            self._mil_category = mil_category

            # check input parameters            
            check_results =  self.checkParam( mil_category )            
            
            if not check_results[1]:
                raise Exception("Invalid parameters: " +  check_results[2] + ". Object not istantiate.")
                       

    # methods

    @property
    def mil_category(self):
        return self._mil_category
    
    @mil_category.setter
    def mil_category(self, value):
         
        check_result = self.checkParam(name = value)
        
        if not check_result[1]:
            raise Exception(check_result[2])    

        self._mil_category = value
        return True
    
    def checkParam(mil_category: str) -> bool: # type: ignore
        """Return True if type compliance of the parameters is verified"""   
    
        #if not super().checkParam(name, description, side, category, function, value, position, acs, rcs, payload):
            #return False     # non serve dovrebbe essere già verificata nella costruzione di Block

        if not isinstance(mil_category, str) and mil_category not in MIL_BASE_CATEGORY:
            return (False, f"Bad argument: mil_category {0} must be a MIL_CATEGORY string: {1}".format(mil_category, str([cat for cat in MIL_BASE_CATEGORY])))
        
        return True
        
    def groundCombatPower(self, action: str)-> float:

        if action not in GROUND_ACTION:
            raise Exception(f"action {0} must be: {1}".format(action, GROUND_ACTION))            

        ground_combat_pow = 0    
        
        for asset in self.assets:

             if isinstance(asset, Vehicle):
                asset_class = Utility.getClassName(asset) # asset_class = Armored, Tank, Motorized, Artillery_Semovent, Artillery_Fixed
                ground_combat_pow += COMBAT_EFFICACY[action][asset_class] * asset[asset_class]["efficiency"]

        return ground_combat_pow

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
       
        """
        Create a recognition report for the enemy blocks in the region. The report is a dictionary with keys 'attack', 'defence', 'retrait', 'maintain' containing report from asset's recognition info.

        Returns:
            Dict: a dictionary with keys 'attack', 'defence', 'retrait', 'maintain' containing sorted recognition reports from enemy blocks in the region. The reports are sorted by criticality in descending order.
        """
    
        success_Mission_Recon_Ratio = evaluateRecoMissionRatio(self.side, self.region.name) # success of reconnaissance mission
        recon_Asset_Efficiency = self.getReconEfficiency() # efficiency of reconnaissance assets
        asset_Number_Accuracy = calcRecoAccuracy("Number", success_Mission_Recon_Ratio, recon_Asset_Efficiency) # accuracy of recon evaluation of asset number
        asset_Efficiency_Accuracy = calcRecoAccuracy("Efficiency", success_Mission_Recon_Ratio, recon_Asset_Efficiency) # accuracy of recon evaluation of asset efficiency
        enemy_blocks = self.region.getEnemyBlocks(self.getEnemySide()) # get enemy blocks in the region
        report_base = self.getBlockInfo("friendly_request") # get this base report          
        recon_reports = { "id_base": self.id, "name_base": self.name, "attack": (), "defence": (), "retrait": (), "maintain": ()} # dictionary of reports
        report_queue = []    # priority queue (heapq) for managing reports by criticality

        for enmy_block in enemy_blocks:

            report_enemy = enmy_block.getBlockInfo("enemy_request",  asset_Number_Accuracy, asset_Efficiency_Accuracy)            
            
            if self.mil_category in MIL_BASE_CATEGORY["Ground Base"]:

                criticality = evaluateCriticalityGroundEnemy(report_base, report_enemy) # evaluate criticality of enemy report compared to report_base                          
                

            elif self.mil_category in MIL_BASE_CATEGORY["Air Base"]:

                criticality = evaluateCriticalityAirDefence(report_base, report_enemy) # evaluate criticality of enemy report compared to report_base

            else:
                raise Exception( "Bad argument: mil_category {0} must be a MIL_CATEGORY[/'Ground Base/'] or MIL_CATEGORY[/'Air Base/'] string: {1}".format(self.mil_category, str( [cat for cat in [MIL_BASE_CATEGORY["Ground Base"], MIL_BASE_CATEGORY["Air Base"]]]) ))

            heappush(report_queue, (-criticality, report_enemy)) # Use negative criticality for max-heap behavior

        sorted_reports =  [heappop(report_queue)[1] for _ in range(len(report_queue))] # sort reports by criticality
        
        for report in sorted_reports: # create sorted reports dictionary (max criticality at end dictionary)
            action = report["criticality"]["action"]
            recon_reports[action].append(report)

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
                GROUND_ASSET_CATEGORY["SAM Big"]: {"Number": 0, "Efficiency": 0}, 
                GROUND_ASSET_CATEGORY["SAM Med"]: {"Number": 0, "Efficiency": 0},
                GROUND_ASSET_CATEGORY["SAM Small"]: {"Number": 0, "Efficiency": 0},
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

    @property
    def morale(self): # override Block.morale    
        efficiency = self.efficiency
        balance_trade = self.balance_trade
        mission_success_rate = self.mission_success_rate
        return efficiency * balance_trade * mission_success_rate
    