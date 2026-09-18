
--To create the Air Tasking Order
-- Initiated by Main_NextMission.lua
-------------------------------------------------------------------------------------------------------

if not versionDCE then 
	versionDCE = {} 
end

               -- VERSION --

versionDCE["DC_Tactical.lua"] = "OB.1.0.0"

-------------------------------------------------------------------------------------------------------
-- Old_Boy rev. OB.1.0.0: implements Tactical logic for update module config parameter
------------------------------------------------------------------------------------------------------- 


local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua")
local log_level = LOGGING_LEVEL -- 
local function_log_level = log_level --"warn" 
log.activate = false
log.level = log_level 
log.outfile = LOG_DIR .. "LOG_DC_Tactical.lua." .. camp.mission .. ".log" 
local local_debug = false -- local debug   
local active_log = false
local local_test = false
log.debug("Start")

log.info("require: Init/db_firepower.lua, Init/db_loadouts, Init/db_airbases, Active/oob_air, Active/oob_ground, Init/conf_mod, Init/radios_freq_compatible")
--require("Init/db_loadouts")
--require("Init/db_airbases")
require("Active/oob_air")
require("Active/oob_ground")
require("Init/conf_mod")															-- Miguel21 modification M00 : need option

if not FirstMission then
	--require("Active/camp_status")
	require("Active/statistic_data")
end



--[[

-- task
["Strike"] = 0.3,
["Anti-ship Strike"] = 0.1,
["SEAD"] = 0.1,
["Intercept"] = 0.2,
["CAP"] = 0.4,
["Escort"] = 0.3,
["Fighter Sweep"] = 0.2,
["Reconnaissance"] = 0.1,
},

-- role
["Fighter"] = 0.3, 
["Attacker"] = 0.5,  
["Bomber"] = 0.2,  
["Transporter"] = 0.1, 
0["Reco"] = 0.2, 
["Refueler"] = 0.1,  
["AWACS"] = 0.1, 
["Helicopter"] = 0.2, 
]]
-- change loadouts weight score (usa l'istruzione, non ha senso realizzare una funzione)
--[[
--num resource
camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST[task] = val
camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST[role] = val
camp.module_config.ATO_Generator[side].MINIMUM_REQUESTED_AIRCRAFT_FOR_STRIKE = val
camp.module_config.ATO_Generator[side].ESCORT_NUMBER_MULTIPLIER = val
camp.module_config.ATO_Generator[side].MIN_PERCENTAGE_FOR_ESCORT = val
camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_INTERCEPT = val
camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_RECONNAISSANCE = val
camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_STRIKE = val
camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_CAP = val
camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_ESCORT = val
camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_SWEEP = val
camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_OTHER = val
camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_BOMBER = val


-- reduce score weight: 
-- reduce_score = flights_requested - aircraft_assign / math.ceil(target.firepower.max / unit_loadouts[l].firepower) 
-- CAPS: increase factor by one for each flight that is missing  and target firepower == loadout firpower
-- AWACS and Refueling:  increase factor by one for each flight that is missing 
-- Other: reduce_score = 0


camp.module_config.ATO_Generator[side].FACTOR_FOR_REDUCE_SCORE = val

camp.module_config.ATO_Generator[side].MULTIPLIER_TARGET_DISTANCE_FOR_EVALUTATION_UNIT_RANGE_LOADOUT = val
camp.module_config.ATO_Generator[side].MULTIPLIER_TARGET_DISTANCE_FOR_EVALUTATION_COMPUTING_ROUTE = val


-- route threat
camp.module_config.ATO_Generator[side].MIN_TOTAL_AIR_THREAT_FOR_ESCORT_SUPPORT = val
camp.module_config.ATO_Generator[side].MINIMUM_VALUE_OF_AIR_THREAT = val
camp.module_config.ATO_Generator[side].FACTOR_FOR_REDUCTION_AIR_THREAT = val
camp.module_config.ATO_Generator[side].SCORE_INFLUENCE_ROUTE_THREAT = val


--meteo
camp.module_config.ATO_Generator[side].MIN_CLOUD_DENSITY = val
camp.module_config.ATO_Generator[side].MIN_FOG_VISIBILITY = val
camp.module_config.ATO_Generator[side].MIN_CLOUD_EIGHT_ABOVE_AIRBASE = val

-- efficiency manutention
camp.module_config.ATO_Generator[side].UNIT_SERVICEABILITY = val

]]

local RESET_PERIOD = 5 -- number of mission for reset all config param 


-- implement function to modify target priority for change objective tactics: 	
-- devono essere inseriti anche gli altri fattori condizionanti presenti negli altri moduli

-- load module_config_init table, if not exist create one new
local function loadModuleConfigDefault()

	if camp.mission >= MISSION_START_COMMANDER and io.open("Active/module_config_init.lua", "r") then
        require("Active/module_config_init") -- load stored computed_target_efficiency.lua if not first mission campaign and exist table

    elseif camp.mission == 1 then -- initialize new computed_target_efficiency if not exist 	
		os.remove("Active/module_config_init.lua")	
		module_config_init = camp.module_config 
		SaveTabOnPath( "Active/", "module_config_init", module_config_init )       
		require("Active/module_config_init") -- load stored computed_target_efficiency.lua if not first mission campaign and exist table  
    end
end

local function loadReportCommander()
    
	if camp.mission >= MISSION_START_COMMANDER and io.open("Active/report_commander.lua", "r") then
        require("Active/report_commander") -- load stored report_commander.lua if not MISSION_START_COMMANDER mission campaign and exist table

    elseif ( camp.mission < MISSION_START_COMMANDER ) or local_test then -- initialize new report_commander if not exist 	
		report_commander = {} -- table for store report commander directive
		os.remove("Active/report_commander.lua")			
		SaveTabOnPath( "Active/", "report_commander", report_commander )       
		require("Active/report_commander") -- load stored report_commander.lua if not MISSION_START_COMMANDER mission campaign and exist table  
    end
end

-- change aircraft number in relation to the oprations (all, ground, ground attack, groud interdiction, air superiority, air defensive, air offensive)	
local function changeNumberAircraftForTactics(side, perc, operations)

	if operations == "all" then		
		--camp.module_config.ATO_Generator[side].MINIMUM_REQUESTED_AIRCRAFT_FOR_STRIKE = camp.module_config.ATO_Generator[side].MINIMUM_REQUESTED_AIRCRAFT_FOR_STRIKE * ( 1 + perc )
		camp.module_config.ATO_Generator[side].ESCORT_NUMBER_MULTIPLIER = math.ceil(camp.module_config.ATO_Generator[side].ESCORT_NUMBER_MULTIPLIER * ( 1 + perc ))
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_STRIKE = math.ceil(camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_STRIKE * ( 1 + perc ))
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_BOMBER = math.ceil(camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_BOMBER * ( 1 + perc ))
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_RECONNAISSANCE = math.ceil(camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_RECONNAISSANCE * ( 1 + perc ))
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_CAP = math.ceil(camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_CAP * ( 1 + perc ) )
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_ESCORT = math.ceil(camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_ESCORT * ( 1 + perc ))
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_SWEEP = math.ceil(camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_SWEEP * ( 1 + perc ))
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_INTERCEPT = math.ceil(camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_INTERCEPT * ( 1 + perc ))
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_OTHER = math.ceil(camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_OTHER * ( 1 + perc ))
	
	elseif operations == "ground" then		
		--camp.module_config.ATO_Generator[side].MINIMUM_REQUESTED_AIRCRAFT_FOR_STRIKE = camp.module_config.ATO_Generator[side].MINIMUM_REQUESTED_AIRCRAFT_FOR_STRIKE * ( 1 + perc )		
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_STRIKE = math.ceil(camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_STRIKE * ( 1 + perc ))
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_BOMBER = math.ceil(camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_BOMBER * ( 1 + perc ))
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_RECONNAISSANCE = math.ceil(camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_RECONNAISSANCE * ( 1 + perc ))

	elseif operations == "ground attack" then		
		--camp.module_config.ATO_Generator[side].MINIMUM_REQUESTED_AIRCRAFT_FOR_STRIKE = camp.module_config.ATO_Generator[side].MINIMUM_REQUESTED_AIRCRAFT_FOR_STRIKE * ( 1 + perc )		
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_STRIKE = math.ceil(camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_STRIKE * ( 1 + perc )		)
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_RECONNAISSANCE = math.ceil(camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_RECONNAISSANCE * ( 1 + perc )		)
		
	elseif operations == "ground interdiction" then		--non serve è uguale a ground
		--camp.module_config.ATO_Generator[side].MINIMUM_REQUESTED_AIRCRAFT_FOR_STRIKE = camp.module_config.ATO_Generator[side].MINIMUM_REQUESTED_AIRCRAFT_FOR_STRIKE * ( 1 + perc )
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_STRIKE = math.ceil(camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_STRIKE * ( 1 + perc ))
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_BOMBER = math.ceil(camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_BOMBER * ( 1 + perc ))
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_RECONNAISSANCE = math.ceil(camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_RECONNAISSANCE * ( 1 + perc ))		

	elseif operations == "air superiority" then		
		camp.module_config.ATO_Generator[side].ESCORT_NUMBER_MULTIPLIER = math.ceil(camp.module_config.ATO_Generator[side].ESCORT_NUMBER_MULTIPLIER * ( 1 + perc ))		
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_CAP = math.ceil(camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_CAP * ( 1 + perc ) )
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_INTERCEPT = math.ceil(camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_INTERCEPT * ( 1 + perc ))
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_ESCORT = math.ceil(camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_ESCORT * ( 1 + perc ))
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_SWEEP = math.ceil(camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_SWEEP * ( 1 + perc )	)	
		
	elseif operations == "air defensive" then		
		camp.module_config.ATO_Generator[side].ESCORT_NUMBER_MULTIPLIER = math.ceil(camp.module_config.ATO_Generator[side].ESCORT_NUMBER_MULTIPLIER * ( 1 + perc ))		
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_CAP = math.ceil(camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_CAP * ( 1 + perc )) 
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_INTERCEPT = math.ceil(camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_INTERCEPT * ( 1 + perc ))		

	elseif operations == "air offensive" then		
		camp.module_config.ATO_Generator[side].ESCORT_NUMBER_MULTIPLIER = math.ceil(camp.module_config.ATO_Generator[side].ESCORT_NUMBER_MULTIPLIER * ( 1 + perc ))				
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_ESCORT = math.ceil(camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_ESCORT * ( 1 + perc ))
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_SWEEP = math.ceil(camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_SWEEP * ( 1 + perc ))		
	
	elseif operations == "default" then				
		camp.module_config.ATO_Generator[side].ESCORT_NUMBER_MULTIPLIER = module_config_init.ATO_Generator[side].ESCORT_NUMBER_MULTIPLIER
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_CAP = module_config_init.ATO_Generator[side].MAX_AIRCRAFT_FOR_CAP
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_INTERCEPT = module_config_init.ATO_Generator[side].MAX_AIRCRAFT_FOR_INTERCEPT
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_ESCORT = module_config_init.ATO_Generator[side].MAX_AIRCRAFT_FOR_ESCORT
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_SWEEP = module_config_init.ATO_Generator[side].MAX_AIRCRAFT_FOR_SWEEP	
		--camp.module_config.ATO_Generator[side].MINIMUM_REQUESTED_AIRCRAFT_FOR_STRIKE = module_config_init.ATO_Generator[side].MINIMUM_REQUESTED_AIRCRAFT_FOR_STRIKE
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_STRIKE = module_config_init.ATO_Generator[side].MAX_AIRCRAFT_FOR_STRIKE
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_BOMBER = module_config_init.ATO_Generator[side].MAX_AIRCRAFT_FOR_BOMBER
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_RECONNAISSANCE = module_config_init.ATO_Generator[side].MAX_AIRCRAFT_FOR_RECONNAISSANCE
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_OTHER = module_config_init.ATO_Generator[side].MAX_AIRCRAFT_FOR_OTHER		

	elseif operations == "default ground" then		
		camp.module_config.ATO_Generator[side].MINIMUM_REQUESTED_AIRCRAFT_FOR_STRIKE = module_config_init.module_config.ATO_Generator[side].MINIMUM_REQUESTED_AIRCRAFT_FOR_STRIKE
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_STRIKE = module_config_init.ATO_Generator[side].MAX_AIRCRAFT_FOR_STRIKE
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_BOMBER = module_config_init.ATO_Generator[side].MAX_AIRCRAFT_FOR_BOMBER
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_RECONNAISSANCE = module_config_init.ATO_Generator[side].MAX_AIRCRAFT_FOR_RECONNAISSANCE

	elseif operations == "default air" then
		camp.module_config.ATO_Generator[side].ESCORT_NUMBER_MULTIPLIER = module_config_init.ATO_Generator[side].ESCORT_NUMBER_MULTIPLIER
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_CAP = module_config_init.ATO_Generator[side].MAX_AIRCRAFT_FOR_CAP 
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_INTERCEPT = module_config_init.ATO_Generator[side].MAX_AIRCRAFT_FOR_INTERCEPT
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_ESCORT = module_config_init.ATO_Generator[side].MAX_AIRCRAFT_FOR_ESCORT
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_SWEEP = module_config_init.ATO_Generator[side].MAX_AIRCRAFT_FOR_SWEEP		

	else
		log.warn("unknow operations: " .. operations)
	end

	if camp.module_config.ATO_Generator[side].MINIMUM_REQUESTED_AIRCRAFT_FOR_STRIKE > 2 then
		camp.module_config.ATO_Generator[side].MINIMUM_REQUESTED_AIRCRAFT_FOR_STRIKE = 2
	
	elseif camp.module_config.ATO_Generator[side].MINIMUM_REQUESTED_AIRCRAFT_FOR_STRIKE < 1 then
		camp.module_config.ATO_Generator[side].MINIMUM_REQUESTED_AIRCRAFT_FOR_STRIKE = 1
	end

	if camp.module_config.ATO_Generator[side].ESCORT_NUMBER_MULTIPLIER > 3 then
		camp.module_config.ATO_Generator[side].ESCORT_NUMBER_MULTIPLIER = 3
	
	elseif camp.module_config.ATO_Generator[side].ESCORT_NUMBER_MULTIPLIER < 1 then
		camp.module_config.ATO_Generator[side].ESCORT_NUMBER_MULTIPLIER = 1
	end

	if camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_STRIKE > 8 then
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_STRIKE = 8
	
	elseif camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_STRIKE < 1 then
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_STRIKE = 1
	end
	
	if camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_BOMBER > 5 then 
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_BOMBER = 5
	
	elseif camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_BOMBER < 1 then 
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_BOMBER = 1
	end

	if camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_RECONNAISSANCE > 3 then 
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_RECONNAISSANCE = 3
	
	elseif camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_RECONNAISSANCE < 1 then 
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_RECONNAISSANCE = 1
	end

	if camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_CAP > 6 then 
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_CAP = 6
	
	elseif camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_CAP < 1 then 
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_CAP = 1
	end

	if camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_ESCORT > 8 then 
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_ESCORT = 8
	
	elseif camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_ESCORT < 1 then 
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_ESCORT = 1
	end

	if camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_SWEEP > 8 then 
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_SWEEP = 8
	
	elseif camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_SWEEP < 1 then 
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_SWEEP = 1
	end

	if camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_INTERCEPT > 5 then 
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_INTERCEPT = 5
	
	elseif camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_INTERCEPT < 1 then 
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_INTERCEPT = 1
	end
	
	if camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_OTHER > 4 then 
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_OTHER = 4
	
	elseif camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_OTHER < 1 then 
		camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_OTHER = 1
	end
end

-- change cost weight in reation to the opration (air, ground, all)
local function airCostChange(side, operations, perc)

	-- factor cost (loadouts or aircraft) decrease as the cost increases -> perc change WEIGHT of factor cost -> increment oof perc cause bigger influence of low cost policy

	local perc_air, perc_ground	
	
	if operations == "all" then
		perc_air = perc
		perc_ground = perc
	
	elseif operations == "ground" then
		perc_air = 0
		perc_ground = perc

	elseif operations == "air" then
		perc_air = perc
		perc_ground = 0

	elseif operations == "default" then
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST = module_config_init.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST = module_config_init.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST
	
	elseif operations == "default aircraft" then
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST = module_config_init.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST		
		
	elseif operations == "default loadouts" then	
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST = module_config_init.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST
	
	elseif operations == "default air" then				
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Fighter"] = module_config_init.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Fighter"]
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Transporter"] = module_config_init.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Transporter"]
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Refueler"] = module_config_init.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Refueler"]
		-- loadouts				
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["CAP"] = module_config_init.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["CAP"]
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["Fighter Sweep"] = module_config_init.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["Fighter Sweep"]
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["Intercept"] = module_config_init.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["Intercept"]
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["Escort"] = module_config_init.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["Escort"]

	elseif operations == "default ground" then				
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Attacker"] = module_config_init.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Attacker"]
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Bomber"] = module_config_init.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Bomber"]
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Reco"] = module_config_init.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Reco"]
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Helicopter"] = module_config_init.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Helicopter"]
		-- loadouts
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["Strike"] = module_config_init.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["Strike"]
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["Anti-ship Strike"] = module_config_init.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["Anti-ship Strike"]
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["SEAD"] = module_config_init.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["SEAD"]
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["Reconnaissance"] = module_config_init.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["Reconnaissance"]
	
	else
		log.warn("unknow operations: " .. operations)
		operations = "unknow operations"
	end	
	
	if string.sub(operations,1,7) ~= "default" and operations ~= "unknow operations" then
		-- aircraft
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Attacker"] = camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Attacker"] * ( 1 + perc_ground ) -- increment(perc > 0 ) or decrement (perc < 0) cost weight cost for reduce score of expensive aircraft
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Bomber"] = camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Bomber"] * ( 1 + perc_ground )		
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Reco"] = camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Reco"] * ( 1 + perc_ground )		
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Helicopter"] = camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Helicopter"] * ( 1 + perc_ground )		
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Fighter"] = camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Fighter"] * ( 1 + perc_air ) -- increment(perc > 0 ) or decrement (perc < 0) cost weight cost for reduce score of expensive aircraft
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Transporter"] = camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Transporter"] * ( 1 + perc_air )		
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Refueler"] = camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Refueler"] * ( 1 + perc_air )			
		-- loadouts
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["Strike"] = camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["Strike"]  * ( 1 + perc_ground )		
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["Anti-ship Strike"] = camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["Anti-ship Strike"]  * ( 1 + perc_ground )		
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["SEAD"] = camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["SEAD"]  * ( 1 + perc_ground )		
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["Reconnaissance"] = camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["Reconnaissance"]  * ( 1 + perc_ground )					
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["CAP"] = camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["CAP"]  * ( 1 + perc_air )					
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["Fighter Sweep"] = camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["Fighter Sweep"]  * ( 1 + perc_air )					
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["Intercept"] = camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["Intercept"]  * ( 1 + perc_air )					
		camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["Escort"] = camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST["Escort"]  * ( 1 + perc_air )					
	end
end

-- local costs_policy = { "reduction", "high reduction", "increment", "high_increment", "ground_reduction", "ground_increment", "air_reduction", "air_increment" }

-- change cost weight of aircraft and loadout in relation to the cost policy { "reduction", "high reduction", "increment", "high_increment", "ground_reduction", "ground_increment", "air_reduction", "air_increment" }
-- factor cost (loadouts or aircraft) decrease as the cost increases -> perc change WEIGHT of factor cost -> increment oof perc cause bigger influence of low cost policy
local function airCostPolicy(side, cost_policy)
	
	
	if cost_policy == "decrement" then -- decrements use of costly aircraft/loadouts
		airCostChange(side, "all", 3)

	elseif cost_policy == "increment" then -- increments use of costly aircraft/loadouts
		airCostChange(side, "all", 0.3)

	elseif cost_policy == "ground decrement" then -- decrements use of costly aircraft/loadouts
		airCostChange(side, "ground", 3)
	
	elseif cost_policy == "ground increment" then -- increments use of costly aircraft/loadouts
		airCostChange(side, "ground", 0.3)
		
	elseif cost_policy == "air decrement" then -- decrements use of costly aircraft/loadouts
		airCostChange(side, "air", 3)
	
	elseif cost_policy == "air increment" then -- increments use of costly aircraft/loadouts
		airCostChange(side, "air", 0.3)

	elseif cost_policy == "default" then -- reset use of costly aircraft/loadouts
		airCostChange(side, "default", nil)

	elseif cost_policy == "default air" then -- reset use of costly aircraft/loadouts
		airCostChange(side, "default air", nil)
	
	elseif cost_policy == "default ground" then -- reset use of costly aircraft/loadouts
		airCostChange(side, "default ground", nil)

	elseif cost_policy == "default aircraft" then -- reset use of costly aircraft
		airCostChange(side, "default aircraft", nil)

	elseif cost_policy == "default loadouts" then -- reset use of costly loadouts
		airCostChange(side, "default loadouts", nil)
	
	else
		log.warn("unknow cost policy: " .. cost_policy)
	end

end

-- change weight task and/or task attribute for score mission
local function changeWeightScore(side, value, operation)

	if operation == "ground" then
		camp.module_config.SCORE_TASK_FACTOR[side].Strike.Bridge = value		
		camp.module_config.SCORE_TASK_FACTOR[side].Strike.Structure = value
		camp.module_config.SCORE_TASK_FACTOR[side].Strike.armor = value		
		camp.module_config.SCORE_TASK_FACTOR[side].Strike.soft = value
		camp.module_config.SCORE_TASK_FACTOR[side].Strike.hard = value
		camp.module_config.SCORE_TASK_FACTOR[side].Strike["Parked Aircraft"] = value
		camp.module_config.SCORE_TASK_FACTOR[side].Strike.SAM = value
		
	elseif operation == "ground attack" then		
		camp.module_config.SCORE_TASK_FACTOR[side].Strike.armor = value		
		camp.module_config.SCORE_TASK_FACTOR[side].Strike.soft = value
		camp.module_config.SCORE_TASK_FACTOR[side].Strike.hard = value				

	elseif operation == "ground interdiction" then
		camp.module_config.SCORE_TASK_FACTOR[side].Strike.Bridge = value		
		camp.module_config.SCORE_TASK_FACTOR[side].Strike.Structure = value		
		-- camp.module_config.SCORE_TASK_FACTOR[side].Strike["Parked Aircraft"] = value
		camp.module_config.SCORE_TASK_FACTOR[side].Strike.SAM = value	

	elseif operation == "anti-ship" then		
		camp.module_config.SCORE_TASK_FACTOR[side]["Anti-ship Strike"] = value				

	elseif operation == "air superiority" then
		camp.module_config.SCORE_TASK_FACTOR[side].CAP = value		
		camp.module_config.SCORE_TASK_FACTOR[side].Escort = value
		--camp.module_config.SCORE_TASK_FACTOR[side].Intercept = value
		camp.module_config.SCORE_TASK_FACTOR[side]["Fighter Sweep"] = value

	elseif operation == "air defensive" then
		camp.module_config.SCORE_TASK_FACTOR[side].CAP = value		
		--camp.module_config.SCORE_TASK_FACTOR[side].Escort = value
		camp.module_config.SCORE_TASK_FACTOR[side].Intercept = value
		-- camp.module_config.SCORE_TASK_FACTOR[side]["Fighter Sweep"] = value

	elseif operation == "air offensive" then
		--camp.module_config.SCORE_TASK_FACTOR[side].CAP = value		
		camp.module_config.SCORE_TASK_FACTOR[side].Escort = value
		-- camp.module_config.SCORE_TASK_FACTOR[side].Intercept = value
		camp.module_config.SCORE_TASK_FACTOR[side]["Fighter Sweep"] = value

	elseif operation == "default ground" then
		camp.module_config.SCORE_TASK_FACTOR[side].Strike = module_config_init.SCORE_TASK_FACTOR[side].Strike		
		camp.module_config.SCORE_TASK_FACTOR[side].Strike = module_config_init.SCORE_TASK_FACTOR[side]["Anti-ship Strike"]

	elseif operation == "default air" then
		camp.module_config.SCORE_TASK_FACTOR[side].CAP = module_config_init.SCORE_TASK_FACTOR[side].CAP		
		camp.module_config.SCORE_TASK_FACTOR[side].Escort = module_config_init.SCORE_TASK_FACTOR[side].Escort
		camp.module_config.SCORE_TASK_FACTOR[side].Intercept = module_config_init.SCORE_TASK_FACTOR[side].Intercept
		camp.module_config.SCORE_TASK_FACTOR[side]["Fighter Sweep"] = module_config_init.SCORE_TASK_FACTOR[side]["Fighter Sweep"]

	elseif operation == "default anti-ship" then		
		camp.module_config.SCORE_TASK_FACTOR[side]["Anti-ship Strike"] = module_config_init.SCORE_TASK_FACTOR[side]["Anti-ship Strike"]		

	elseif operation == "default" then		
		camp.module_config.SCORE_TASK_FACTOR[side].Strike = module_config_init.SCORE_TASK_FACTOR[side].Strike				
		camp.module_config.SCORE_TASK_FACTOR[side]["Anti-ship Strike"] = module_config_init.SCORE_TASK_FACTOR[side]["Anti-ship Strike"]
		camp.module_config.SCORE_TASK_FACTOR[side].CAP = module_config_init.SCORE_TASK_FACTOR[side].CAP		
		camp.module_config.SCORE_TASK_FACTOR[side].Escort = module_config_init.SCORE_TASK_FACTOR[side].Escort
		camp.module_config.SCORE_TASK_FACTOR[side].Intercept = module_config_init.SCORE_TASK_FACTOR[side].Intercept
		camp.module_config.SCORE_TASK_FACTOR[side]["Fighter Sweep"] = module_config_init.SCORE_TASK_FACTOR[side]["Fighter Sweep"]
		camp.module_config.SCORE_TASK_FACTOR[side]["Anti-ship Strike"] = module_config_init.SCORE_TASK_FACTOR[side]["Anti-ship Strike"]		

	else
		log.warn("unknow operation: " .. operation)
	end

end

-- print target priority table
local function printPriorityTable(text)		
	print( text .. "\n\n" .. inspect( target_priority_default ) )	
end


-- change priority target (targetlist) of the perc(%) value for specific task
local function changePriorityTask(side, task, attribute, class, perc)

	for target_name, target in pairs(targetlist[side]) do

		if target.task == task and ( not attribute ) or ( ( target.attributes and target.attributes[1] and target.attributes[1] == attribute ) and (  ( not class ) or ( class and class == target.class )  )  ) then			
			target.priority = math.ceil( target.priority * ( 1 + perc ) )
			
			if target.priority > 15 then
				target.priority = 15 -- max priority (targetlist_ini -> CAP priority = 20)
			
			elseif target.priority < 1 then
				target.priority = 1 -- min priority (targetlist_ini)
			end

		else
			log.warn("target not found: task: " .. task .. ", attribute: " .. (attribute or "nil") .. ", class: " .. (class or "nil"))
		end
	end
end

-- reset priority target (targetlist) of the perc(%) value for specific task
local function resetPriorityTask(side, task, attribute, class)

	for target_name, target in pairs(targetlist[side]) do

		if target.task == task and ( not attribute ) or ( ( target.attributes and target.attributes[1] and target.attributes[1] == attribute ) and (  ( not class ) or ( class and class == target.class )  )  ) then			
			target.priority = target_priority_default[side][target_name]
			
		elseif task == "all" then
			target.priority = target_priority_default[side][target_name]
		
		elseif task == "air" then

			if target.task == "CAP" or target.task == "Intercept" or target.task == "Fighter Sweep" or target.task == "Escort" or target.task == "AWACS" or target.task == "Refueling" or target.task == "Transport" or target.task == "Recognition" then 
				target.priority = target_priority_default[side][target_name]
			end
		
		elseif task == "ground" then

			if target.task == "Strike" or target.task == "Anti-ship Strike" then 
				target.priority = target_priority_default[side][target_name]
			end
				
		else
			log.warn("target not found: task: " .. task .. ", attribute: " .. (attribute or "nil") .. ", class: " .. (class or "nil"))
		end
	end
end

-- returns table target priority value for specific side
local function getTargetPriority(side)
	local target_priority = {}
			
	for target_name, target in pairs(targetlist[side]) do
		target_priority[target_name] = target.priority
	end
	return target_priority	
end

-- define, save and load priority_default table. priority_default table contains initial target priority value specified in targetlist_init
local function loadPriorityDefault()

	if camp.mission > 1 and io.open("Active/target_priority_default.lua", "r") then
        require("Active/target_priority_default") -- load stored target_priority_default.lua if not first mission campaign and exist table

    else -- initialize new target_priority_default if not exist 
		os.remove("Active/target_priority_default.lua")
        target_priority_default = {} -- table contains target efficiency values: hash table with hash = target and value = firepower med for that target
		
		for side_name, side in pairs(targetlist) do
			target_priority_default[side_name] = {}
				
			--[[for target_name, target in pairs(targetlist[side_name]) do
				target_priority_default[side_name][target_name] = target.priority
			end]]
			target_priority_default[side_name] = getTargetPriority(side_name)
		end		
        SaveTabOnPath( "Active/", "target_priority_default", target_priority_default )         
    end
end



-- normalized tactic directive
local tactics = {
	
	["moderate increment offensive action"] = "moderate increment offensive action",				-- moderate increments actions against enemy army using economic asset
	["increment offensive action"] = "increment offensive action",									-- increments actions against enemy army 
	["significative increment offensive action"] = "significative increment offensive action",		-- significative increments actions against enemy army using expensive asset

	["moderate decrement offensive action"] = "moderate decrement offensive action",				-- moderate decrements actions against enemy army using economic asset
	["decrement offensive action"] = "decrement offensive action",									-- decrements actions against enemy army 
	["significative decrement offensive action"] = "significative decrement offensive action",		-- significative decrements actions against enemy army using expensive asset

	["moderate increment strategic action"] = "moderate increment strategic action", 				-- moderate increments actions against enemy strategic asset (structure, bridge, airbase) using economic asset
	["increment strategic action"] = "increment strategic action", 									-- increments actions against enemy strategic asset (structure, bridge, airbase)
	["significative increment strategic action"] = "significative increment strategic action", 		-- significative increments actions against enemy strategic asset (structure, bridge, airbase) using expensive asset

	["moderate decrement strategic action"] = "moderate decrement strategic action", 				-- moderate decrements actions against enemy strategic asset (structure, bridge, airbase) using economic asset
	["decrement strategic action"] = "decrement strategic action", 									-- decrements actions against enemy strategic asset (structure, bridge, airbase)
	["significative decrement strategic action"] = "significative decrement strategic action", 		-- significative decrements actions against enemy strategic asset (structure, bridge, airbase) using expensive asset

	["moderate increment air superiority"] = "moderate increment air superiority",					-- moderate increment air superiority action (Intercept, Fighter Sweep and Escort task)  using economic asset
	["increment air superiority"] = "increment air superiority",									-- increment air superiority action (Intercept, Fighter Sweep and Escort task)
	["significative increment air superiority"] = "significative increment air superiority",		-- significative increment air superiority action (Intercept, Fighter Sweep and Escort task)  using expensive asset

	["moderate decrement air superiority"] = "moderate decrement air superiority",					-- moderate decrement air superiority action (Intercept, Fighter Sweep and Escort task) using economic asset
	["decrement air superiority"] = "decrement air superiority",									-- decrement air superiority action (Intercept, Fighter Sweep and Escort task)
	["significative decrement air superiority"] = "significative decrement air superiority",		-- significative decrement air superiority action (Intercept, Fighter Sweep and Escort task)  using expensive asset
	
	["moderate increment defensive"] = "moderate increment defensive",								-- moderate increment air to air defensive action (Intercept, Escort) and reduce air to ground action using economic asset
	["increment defensive"] = "increment defensive",												-- increment air to air defensive action (Intercept, Escort) and reduce air to ground action
	["significative increment defensive"] = "significative increment defensive",					-- significative increment air to air defensive action (Intercept, Escort) and reduce air to ground action using expensive6 asset
	
	["moderate decrement defensive"] = "moderate decrement defensive",								-- moderate increment air to air defensive action (Intercept, Escort) and reduce air to ground action using economic asset
	["decrement defensive"] = "decrement defensive",												-- increment air to air defensive action (Intercept, Escort) and reduce air to ground action
	["significative decrement defensive"] = "significative decrement defensive",					-- significative increment air to air defensive action (Intercept, Escort) and reduce air to ground action using expensive6 asset
	

	["increment priority for Anti-ship operations"] = "increment priority for Anti-ship operations",						-- increments mission for Anti-ship Strike task
	["increment priority for SAM strike operations"] = "increment priority for SAM strike operations",						-- increments mission for SAM Strike task
	["increment priority for Army Ground Attack operations"] = "increment priority for Army Ground Attack operations",		-- increments mission for Army Ground Attack task
	["reset priority for all operations"] = "reset priority for all operations",											-- reset priority operations
	["reset priority for SAM operations"] = "reset priority for SAM operations",											-- reset priority operations
	["restore default resource"] = "restore default resource",																-- restore resource config parameters at default value (camp_init)
	["restore global default condition"] = "restore global default condition",												-- restore resource, action and cost config parameters at default value (camp_init)
	["restore air default condition"] = "restore air default condition",													-- restore air resource, action and cost config parameters at default value (camp_init)
}

--changePriorityTask(side, task, attribute, class, perc)
--resetPriorityTask(side, task, attribute, class)

-- normalized tasks and attributes
local task_attribute = { 
	["CAP"] = false,
	["Intercept"] = false,
	["Fighter Sweep"] = false,
	["Escort"] = false,
	["Anti-ship Strike"] = false,
	["Strike"] = {
		["attribute"] = {"Parked Aircraft", "SAM", "soft", "hard", "armor", "Structure", "Bridge", "ship"},
		["class"] = {"static", "airbase", "vehicle", "ship"},
	},
	["Transport"] = true,
	["Refueling"] = true,
	["AWACS"] = true,
}

-- execute function for tactic directive
local function airDirective(side, tactic)

	if tactic == tactics["moderate increment offensive action"] then				-- moderate increments action and resource for offensive task, using economic asset
		changeNumberAircraftForTactics(side, 0.3, "ground attack")					-- increment min, max, requested aircraft for specific task/role		
		changeWeightScore(side, 2, "ground")										-- increments weight score for ground offensive task							
		airCostPolicy(side, "ground decrement")										-- increment use of expensive asset
		changePriorityTask(side, "Strike", "soft", nil, 0.3)						-- increment priority for Strike task and soft attribute
		changePriorityTask(side, "Strike", "armor", nil, 0.3)						-- increment priority for Strike task and armor attribute
		
	elseif tactic == tactics["increment offensive action"] then						-- increments action and resource for offensive task
		changeNumberAircraftForTactics(side, 0.5, "ground attack")					-- increment min, max, requested aircraft for specific task/role		
		changeWeightScore(side, 4, "ground")										-- increments weight score for ground offensive task							
		--airCostPolicy(side, "ground decrement")									-- increment use of expensive asset
		changePriorityTask(side, "Strike", "soft", nil, 0.6)						-- increment priority for Strike task and soft attribute
		changePriorityTask(side, "Strike", "armor", nil, 0.6)						-- increment priority for Strike task and armor attribute

	elseif tactic == tactics["significative increment offensive action"] then		-- increments action, resource and expensive asset for offensive task
		changeNumberAircraftForTactics(side, 1, "ground attack")					-- increment min, max, requested aircraft for specific task/role		
		changeWeightScore(side, 6, "ground")										-- increments weight score for ground offensive task							
		airCostPolicy(side, "ground increment")										-- increment use of expensive asset
		changePriorityTask(side, "Strike", "soft", nil, 1)							-- increment priority for Strike task and soft attribute
		changePriorityTask(side, "Strike", "armor", nil, 1)							-- increment priority for Strike task and armor attribute

	elseif tactic == tactics["moderate decrement offensive action"] then			-- moderate decrements action and resource for offensive task, using economic asset
		changeNumberAircraftForTactics(side, -0.2, "ground attack")					-- decrement min, max, requested aircraft for specific task/role		
		changeWeightScore(side, 0.5, "ground")										-- decrements weight score for ground offensive task							
		airCostPolicy(side, "ground decrement")										-- decrement use of expensive asset
		changePriorityTask(side, "Strike", "soft", nil, -0.2)						-- decrement priority for Strike task and soft attribute
		changePriorityTask(side, "Strike", "armor", nil, -0.2)						-- decrement priority for Strike task and armor attribute
		
	elseif tactic == tactics["decrement offensive action"] then						-- decrements action and resource for offensive task
		changeNumberAircraftForTactics(side, -0.4, "ground attack")					-- decrement min, max, requested aircraft for specific task/role		
		changeWeightScore(side, 0.3, "ground")										-- decrements weight score for ground offensive task							
		airCostPolicy(side, "ground decrement")										-- decrement use of expensive asset
		changePriorityTask(side, "Strike", "soft", nil, -0.4)						-- decrement priority for Strike task and soft attribute
		changePriorityTask(side, "Strike", "armor", nil, -0.4)						-- decrement priority for Strike task and armor attribute

	elseif tactic == tactics["significative decrement offensive action"] then		-- decrements action, resource and expensive asset for offensive task
		changeNumberAircraftForTactics(side, -0.8, "ground attack")					-- decrement min, max, requested aircraft for specific task/role		
		changeWeightScore(side, 0.2, "ground")										-- decrements weight score for ground task							
		airCostPolicy(side, "ground decrement")										-- decrement use of expensive asset
		changePriorityTask(side, "Strike", "soft", nil, -0.6)						-- decrement priority for Strike task and soft attribute
		changePriorityTask(side, "Strike", "armor", nil, -0.6)						-- decrement priority for Strike task and armor attribute

	elseif tactic == tactics["moderate increment offensive strategic action"] then	-- increments action, resource and expensive asset for strategic task			
		changeNumberAircraftForTactics(side, 0.3, "ground interdiction")			-- increment min, max, requested aircraft for specific task/role						
		changeWeightScore(side, 2, "ground interdiction")							-- increments weight score for ground task										
		airCostPolicy(side, "ground decrement")										-- increments use of expensive asset of ground interdiction missions (Bridge, Structure)
		changePriorityTask(side, "Strike", "SAM", nil, 0.2)							-- increment priority for Strike task and SAM attribute
		changePriorityTask(side, "Strike", "Structure", nil, 0.3)					-- increment priority for Strike task and Structure attribute
		changePriorityTask(side, "Strike", "Bridge", nil, 0.3)						-- increment priority for Strike task and Bridge attribute
		changePriorityTask(side, "Strike", "Parked Aircraft", nil, 0.2)				-- increment priority for Strike task and Parked Aircraft attribute

	elseif tactic == tactics["increment offensive strategic action"] then 			-- increments action, resource and expensive asset for strategic task			
		changeNumberAircraftForTactics(side, 0.5, "ground interdiction")			-- increment min, max, requested aircraft for specific task/role						
		changeWeightScore(side, 4, "ground interdiction")							-- increments weight score for ground task										
		--airCostPolicy(side, "ground increment")									-- increments use of expensive asset of ground interdiction missions (Bridge, Structure)
		changePriorityTask(side, "Strike", "SAM", nil, 0.35)						-- increment priority for Strike task and SAM attribute
		changePriorityTask(side, "Strike", "Structure", nil, 0.5)					-- increment priority for Strike task and Structure attribute
		changePriorityTask(side, "Strike", "Bridge", nil, 0.5)						-- increment priority for Strike task and Bridge attribute
		changePriorityTask(side, "Strike", "Parked Aircraft", nil, 0.35)			-- increment priority for Strike task and Parked Aircraft attribute

	elseif tactic == tactics["significative increment offensive strategic action"] then	-- increments action, resource and expensive asset for strategic task			
		changeNumberAircraftForTactics(side, 1, "ground interdiction")				-- increment min, max, requested aircraft for specific task/role						
		changeWeightScore(side, 6, "ground interdiction")							-- increments weight score for ground task										
		airCostPolicy(side, "ground increment")										-- increments use of expensive asset of ground interdiction missions (Bridge, Structure)
		changePriorityTask(side, "Strike", "SAM", nil, 0.5)							-- increment priority for Strike task and SAM attribute
		changePriorityTask(side, "Strike", "Structure", nil, 1)						-- increment priority for Strike task and Structure attribute
		changePriorityTask(side, "Strike", "Bridge", nil, 1)						-- increment priority for Strike task and Bridge attribute
		changePriorityTask(side, "Strike", "Parked Aircraft", nil, 0.5)				-- increment priority for Strike task and Parked Aircraft attribute

	elseif tactic == tactics["moderate decrement offensive strategic action"] then	-- decrements action, resource and expensive asset for strategic task			
		changeNumberAircraftForTactics(side, -0.2, "ground interdiction")			-- decrement min, max, requested aircraft for specific task/role						
		changeWeightScore(side, 0.5, "ground interdiction")							-- decrements weight score for ground task										
		airCostPolicy(side, "ground decrement")										-- decrements use of expensive asset of ground interdiction missions (Bridge, Structure)
		changePriorityTask(side, "Strike", "SAM", nil, -0.15)						-- decrement priority for Strike task and SAM attribute
		changePriorityTask(side, "Strike", "Structure", nil, -0.2)					-- decrement priority for Strike task and Structure attribute
		changePriorityTask(side, "Strike", "Bridge", nil, -0.2)						-- decrement priority for Strike task and Bridge attribute
		changePriorityTask(side, "Strike", "Parked Aircraft", nil, -0.15)			-- decrement priority for Strike task and Parked Aircraft attribute

	elseif tactic == tactics["decrement offensive strategic action"] then 			-- decrements action, resource and expensive asset for strategic task			
		changeNumberAircraftForTactics(side, -0.4, "ground interdiction")			-- decrement min, max, requested aircraft for specific task/role						
		changeWeightScore(side, 0.3, "ground interdiction")							-- decrements weight score for ground task										
		airCostPolicy(side, "ground decrement")										-- decrements use of expensive asset
		changePriorityTask(side, "Strike", "SAM", nil, -0.25)						-- decrement priority for Strike task and SAM attribute
		changePriorityTask(side, "Strike", "Structure", nil, -0.4)					-- decrement priority for Strike task and Structure attribute
		changePriorityTask(side, "Strike", "Bridge", nil, -0.4)						-- decrement priority for Strike task and Bridge attribute
		changePriorityTask(side, "Strike", "Parked Aircraft", nil, -0.25)			-- decrement priority for Strike task and Parked Aircraft attribute

	elseif tactic == tactics["significative decrement offensive strategic action"] then -- decrements action, resource and expensive asset for strategic task			
		changeNumberAircraftForTactics(side, -0.8, "ground interdiction")			-- decrement min, max, requested aircraft for specific task/role						
		changeWeightScore(side, 0.2, "ground interdiction")							-- decrements use of weight score for ground task										
		airCostPolicy(side, "ground decrement")										-- decrements expensive asset of ground interdiction missions (Bridge, Structure)
		changePriorityTask(side, "Strike", "SAM", nil, -0.4)						-- decrement priority for Strike task and SAM attribute
		changePriorityTask(side, "Strike", "Structure", nil, -0.8)					-- decrement priority for Strike task and Structure attribute
		changePriorityTask(side, "Strike", "Bridge", nil, -0.8)						-- decrement priority for Strike task and Bridge attribute
		changePriorityTask(side, "Strike", "Parked Aircraft", nil, -0.4)			-- decrement priority for Strike task and Parked Aircraft attribute								 
		
	elseif tactic == tactics["moderate increment air superiority"] then				-- increment action and resource for air superiority ( task and action )
		changeNumberAircraftForTactics(side, 0.3, "air superiority")				-- increment min, max, requested aircraft for specific task/role								
		changeWeightScore(side, 2, "air superiority")								-- increments weight score for air task										
		airCostPolicy(side, "air decrement")										-- decrements use of expensive asset of air task
		changePriorityTask(side, "Intercept", nil, nil, 0.3)						-- increment priority for Intercept task and
		changePriorityTask(side, "Fighter Sweep", nil, nil, 0.3)					-- increment priority for Fighter Sweep task
		changePriorityTask(side, "Escort", nil, nil, 0.2)							-- increment priority for Escort task

	elseif tactic == tactics["increment air superiority"] then						-- increment action and resource for air superiority ( task and action )
		changeNumberAircraftForTactics(side, 0.5, "air superiority")				-- increment min, max, requested aircraft for specific task/role								
		changeWeightScore(side, 4, "air superiority")								-- increments weight score for air task		
		-- airCostPolicy(side, "air increment")										-- decrements use of expensive asset of air task								
		changePriorityTask(side, "Intercept", nil, nil, 0.4)						-- increment priority for Intercept task and
		changePriorityTask(side, "Fighter Sweep", nil, nil, 0.5)					-- increment priority for Fighter Sweep task
		changePriorityTask(side, "Escort", nil, nil, 0.3)							-- increment priority for Escort task

	elseif tactic == tactics["significative increment air superiority"] then		-- increment action and resource for air superiority ( task and action )
		changeNumberAircraftForTactics(side, 0.8, "air superiority")				-- increment min, max, requested aircraft for specific task/role								
		changeWeightScore(side, 6, "air superiority")								-- increments weight score for air task										
		airCostPolicy(side, "air increment")										-- increments use of expensive asset of air task
		changePriorityTask(side, "Intercept", nil, nil, 0.8)						-- increment priority for Intercept task and
		changePriorityTask(side, "Fighter Sweep", nil, nil, 0.8)					-- increment priority for Fighter Sweep task
		changePriorityTask(side, "Escort", nil, nil, 0.5)							-- increment priority for Escort task

	elseif tactic == tactics["moderate decrement air superiority"] then				-- decrement action and resource for air superiority ( task and action )
		changeNumberAircraftForTactics(side, -0.2, "air superiority")				-- decrement min, max, requested aircraft for specific task/role								
		changeWeightScore(side, 0.5, "air superiority")								-- decrements weight score for air task										
		airCostPolicy(side, "air decrement")										-- decrements use of expensive asset of air task
		changePriorityTask(side, "Intercept", nil, nil, -0.2)						-- decrement priority for Intercept task and
		changePriorityTask(side, "Fighter Sweep", nil, nil, -0.2)					-- decrement priority for Fighter Sweep task
		changePriorityTask(side, "Escort", nil, nil, -0.1)							-- decrement priority for Escort task

	elseif tactic == tactics["decrement air superiority"] then						-- decrement action and resource for air superiority ( task and action )
		changeNumberAircraftForTactics(side, -0.4, "air superiority")				-- decrement min, max, requested aircraft for specific task/role								
		changeWeightScore(side, 0.3, "air superiority")								-- decrements weight score for air task		
		airCostPolicy(side, "air decrement")										-- decrements use of expensive asset of air task								
		changePriorityTask(side, "Intercept", nil, nil, -0.3)						-- decrement priority for Intercept task and
		changePriorityTask(side, "Fighter Sweep", nil, nil, -0.4)					-- decrement priority for Fighter Sweep task
		changePriorityTask(side, "Escort", nil, nil, -0.2)							-- decrement priority for Escort task

	elseif tactic == tactics["significative decrement air superiority"] then		-- decrement action and resource for air superiority ( task and action )
		changeNumberAircraftForTactics(side, -0.6, "air superiority")				-- decrement min, max, requested aircraft for specific task/role								
		changeWeightScore(side, 0.2, "air superiority")								-- decrements weight score for air task										
		airCostPolicy(side, "air decrement")										-- decrements use of expensive asset of air task
		changePriorityTask(side, "Intercept", nil, nil, -0.7)						-- decrement priority for Intercept task
		changePriorityTask(side, "Fighter Sweep", nil, nil, -0.7)					-- decrement priority for Fighter Sweep task
		changePriorityTask(side, "Escort", nil, nil, -0.4)							-- decrement priority for Escort task

	elseif tactic == tactics["moderate increment defensive"] then					-- increment action and resource for air defensive  ( task and action )
		changeNumberAircraftForTactics(side, 0.3, "air defensive")					-- increment min, max, requested aircraft for specific task/role								
		changeNumberAircraftForTactics(side, -0.3, "ground attack")					-- decrement min, max, requested aircraft for specific task/role											
		changeWeightScore(side, 2, "air defensive")									-- increments weight score for air task										
		changeWeightScore(side, 0.5, "ground")										-- decrements weight score for ground task										
		airCostPolicy(side, "ground decrement")										-- decrements use of expensive asset
		changePriorityTask(side, "Intercept", nil, nil, 0.15)						-- increment priority for Intercept task
		changePriorityTask(side, "Fighter Sweep", nil, nil, -0.3)					-- decrement priority for Fighter Sweep task
		changePriorityTask(side, "Escort", nil, nil, 0.2)							-- increment priority for Escort task
		changePriorityTask(side, "Strike", "soft", nil, -0.2)						-- decrement priority for Strike task and soft attribute
		changePriorityTask(side, "Strike", "armor", nil, -0.2)						-- decrement priority for Strike task and armor attribute										 
		changePriorityTask(side, "Strike", "Structure", nil, -0.4)					-- decrement priority for Strike task and Structure attribute
		changePriorityTask(side, "Strike", "Bridge", nil, -0.5)						-- decrement priority for Strike task and Bridge attribute
		changePriorityTask(side, "Strike", "SAM", nil, -0.3)						-- decrement priority for Strike task and SAM attribute
				
	elseif tactic == tactics["increment defensive"] then							-- increment action and resource for air defensive  ( task and action )
		changeNumberAircraftForTactics(side, 0.5, "air defensive")					-- increment min, max, requested aircraft for specific task/role								
		changeNumberAircraftForTactics(side, -0.5, "ground attack")					-- decrement min, max, requested aircraft for specific task/role											
		changeWeightScore(side, 4, "air defensive")									-- increments weight score for air task										
		changeWeightScore(side, 0.3, "ground")										-- decrements weight score for ground task										
		airCostPolicy(side, "air increment")										-- increments use of expensive asset
		airCostPolicy(side, "ground decrement")										-- decrements use of expensive asset
		changePriorityTask(side, "Intercept", nil, nil, 0.3)						-- increment priority for Intercept task
		changePriorityTask(side, "Fighter Sweep", nil, nil, -0.5)					-- decrement priority for Fighter Sweep task
		changePriorityTask(side, "Escort", nil, nil, 0.3)							-- increment priority for Escort task
		changePriorityTask(side, "Strike", "soft", nil, -0.4)						-- decrement priority for Strike task and soft attribute
		changePriorityTask(side, "Strike", "armor", nil, -0.4)						-- decrement priority for Strike task and armor attribute										 
		changePriorityTask(side, "Strike", "Structure", nil, -0.7)					-- decrement priority for Strike task and Structure attribute
		changePriorityTask(side, "Strike", "Bridge", nil, -0.7)						-- decrement priority for Strike task and Bridge attribute
		changePriorityTask(side, "Strike", "SAM", nil, -0.5)						-- decrement priority for Strike task and SAM attribute

	elseif tactic == tactics["significative increment defensive"] then				-- increment action and resource for air defensive  ( task and action )
		changeNumberAircraftForTactics(side, 0.8, "air defensive")					-- increment min, max, requested aircraft for specific task/role								
		changeNumberAircraftForTactics(side, -0.7, "ground attack")					-- decrement min, max, requested aircraft for specific task/role											
		changeWeightScore(side, 6, "air defensive")									-- increments weight score for air task										
		changeWeightScore(side, 0.2, "ground")										-- decrements weight score for ground task										
		airCostPolicy(side, "air increment")										-- increments use of expensive asset
		airCostPolicy(side, "ground decrement")										-- decrements use of expensive asset
		changePriorityTask(side, "Intercept", nil, nil, 0.3)						-- increment priority for Intercept task
		changePriorityTask(side, "Fighter Sweep", nil, nil, -0.5)					-- decrement priority for Fighter Sweep task
		changePriorityTask(side, "Escort", nil, nil, 0.3)							-- increment priority for Escort task
		changePriorityTask(side, "Strike", "soft", nil, -0.4)						-- decrement priority for Strike task and soft attribute
		changePriorityTask(side, "Strike", "armor", nil, -0.4)						-- decrement priority for Strike task and armor attribute										 
		changePriorityTask(side, "Strike", "Structure", nil, -0.7)					-- decrement priority for Strike task and Structure attribute
		changePriorityTask(side, "Strike", "Bridge", nil, -0.7)						-- decrement priority for Strike task and Bridge attribute
		changePriorityTask(side, "Strike", "SAM", nil, -0.5)						-- decrement priority for Strike task and SAM attribute

	elseif tactic == tactics["moderate decrement defensive"] then					-- decrement action and resource for air defensive  ( task and action )
		changeNumberAircraftForTactics(side, -0.2, "air defensive")					-- decrement min, max, requested aircraft for specific task/role								
		changeNumberAircraftForTactics(side, 0.3, "ground attack")					-- increment min, max, requested aircraft for specific task/role											
		changeWeightScore(side, 0.7, "air defensive")								-- decrements weight score for air task										
		changeWeightScore(side, 2, "ground")										-- increments weight score for ground task										
		airCostPolicy(side, "increment")											-- increments use of expensive asset
		changePriorityTask(side, "Intercept", nil, nil, -0.1)						-- decrement priority for Intercept task
		changePriorityTask(side, "Fighter Sweep", nil, nil, 0.15)					-- increment priority for Fighter Sweep task
		changePriorityTask(side, "Escort", nil, nil, -0.1)							-- decrement priority for Escort task
		changePriorityTask(side, "Strike", "soft", nil, 0.1)						-- increment priority for Strike task and soft attribute
		changePriorityTask(side, "Strike", "armor", nil, 0.1)						-- increment priority for Strike task and armor attribute										 
		changePriorityTask(side, "Strike", "Structure", nil, 0.3)					-- increment priority for Strike task and Structure attribute
		changePriorityTask(side, "Strike", "Bridge", nil, 0.4)						-- increment priority for Strike task and Bridge attribute
		changePriorityTask(side, "Strike", "SAM", nil, 0.2)							-- increment priority for Strike task and SAM attribute
				
	elseif tactic == tactics["decrement defensive"] then							-- decrement action and resource for air defensive  ( task and action )
		changeNumberAircraftForTactics(side, -0.3, "air defensive")					-- decrement min, max, requested aircraft for specific task/role								
		changeNumberAircraftForTactics(side, 0.4, "ground attack")					-- increment min, max, requested aircraft for specific task/role											
		changeWeightScore(side, 0.5, "air defensive")								-- decrements weight score for air task										
		changeWeightScore(side, 4, "ground")										-- increments weight score for ground task										
		airCostPolicy(side, "increment")											-- increments use of expensive asset
		changePriorityTask(side, "Intercept", nil, nil, -0.2)						-- decrement priority for Intercept task
		changePriorityTask(side, "Fighter Sweep", nil, nil, 0.2)					-- increment priority for Fighter Sweep task
		changePriorityTask(side, "Escort", nil, nil, -0.2)							-- decrement priority for Escort task
		changePriorityTask(side, "Strike", "soft", nil, 0.2)						-- increment priority for Strike task and soft attribute
		changePriorityTask(side, "Strike", "armor", nil, 0.2)						-- increment priority for Strike task and armor attribute										 
		changePriorityTask(side, "Strike", "Structure", nil, 0.4)					-- increment priority for Strike task and Structure attribute
		changePriorityTask(side, "Strike", "Bridge", nil, 0.4)						-- increment priority for Strike task and Bridge attribute
		changePriorityTask(side, "Strike", "SAM", nil, 0.3)							-- increment priority for Strike task and SAM attribute

	elseif tactic == tactics["significative decrement defensive"] then				-- decrement action and resource for air defensive  ( task and action )
		changeNumberAircraftForTactics(side, -0.4, "air defensive")					-- decrement min, max, requested aircraft for specific task/role								
		changeNumberAircraftForTactics(side, 0.5, "ground attack")					-- increment min, max, requested aircraft for specific task/role											
		changeWeightScore(side, 0.3, "air defensive")								-- decrements weight score for air task										
		changeWeightScore(side, 6, "ground")										-- increments weight score for ground task										
		airCostPolicy(side, "increment")											-- increments use of expensive asset
		changePriorityTask(side, "Intercept", nil, nil, -0.3)						-- decrement priority for Intercept task
		changePriorityTask(side, "Fighter Sweep", nil, nil, 0.3)					-- increment priority for Fighter Sweep task
		changePriorityTask(side, "Escort", nil, nil, -0.3)							-- decrement priority for Escort task
		changePriorityTask(side, "Strike", "soft", nil, 0.3)						-- increment priority for Strike task and soft attribute
		changePriorityTask(side, "Strike", "armor", nil, 0.3)						-- increment priority for Strike task and armor attribute										 
		changePriorityTask(side, "Strike", "Structure", nil, 0.5)					-- increment priority for Strike task and Structure attribute
		changePriorityTask(side, "Strike", "Bridge", nil, 0.5)						-- increment priority for Strike task and Bridge attribute
		changePriorityTask(side, "Strike", "SAM", nil, 0.5)							-- increment priority for Strike task and SAM attribute

	elseif tactic == tactics["increment priority for Anti-ship operations"] then			-- increments mission for Anti-ship Strike task
		changePriorityTask(side, "Anti-ship Strike", nil, nil, 0.5)

	elseif tactic == tactics["increment priority for SAM strike operations"] then			-- increments mission for SAM Strike task
		changePriorityTask(side, "Strike", "SAM", nil, 0.5)

	elseif tactic == tactics["increment priority for Army Ground Attack operations"] then	-- increments mission for Army Ground Attack task
		changePriorityTask(side, "Strike", "soft", nil, 0.5)
		changePriorityTask(side, "Strike", "armor", nil, 0.5)

	elseif tactic == tactics["increment priority for structure attack operations"] then	-- increments mission for Army Ground Attack task
		changePriorityTask(side, "Strike", "Structure", nil, 0.5)

	elseif tactic == tactics["increment priority for bridge attack operations"] then	-- increments mission for Army Ground Attack task
		changePriorityTask(side, "Strike", "Bridge", nil, 0.5)

	elseif tactic == tactics["increment priority for air2air operations"] then	-- increments mission for Army Ground Attack task
		changePriorityTask(side, "Intercept", nil, nil, 0.5)
		changePriorityTask(side, "Fighter Sweep", nil, nil, 0.5)

	elseif tactic == tactics["increment priority for escort operations"] then	-- increments mission for Army Ground Attack task
		changePriorityTask(side, "Escort", nil, nil, 0.5)		

	elseif tactic == tactics["increment priority for transport operations"] then	-- increments mission for Army Ground Attack task
		changePriorityTask(side, "Escort", nil, nil, 0.5)		

	elseif tactic == tactics["reset priority for SAM operations"] then								-- increments mission for Anti-ship Strike task
		resetPriorityTask(side, "Strike", "SAM", nil, nil)
	
	elseif tactic == tactics["reset priority for all operations"] then								-- increments mission for Anti-ship Strike task
		resetPriorityTask(side, "All", nil, nil, nil)

	elseif tactic == tactics["restore default resource"] then								-- restore resource config parameters at default value (camp_init)
		changeNumberAircraftForTactics(side, nil, "default")
		
	elseif tactic == tactics["restore global default condition"] then						-- restore resource, action and cost config parameters at default value (camp_init)
		changeNumberAircraftForTactics(side, nil, "default")
		changeWeightScore(side, nil, "default")	
		airCostPolicy(side, "default")	

	elseif tactic == tactics["restore ground default condition"] then
		changeNumberAircraftForTactics(side, nil, "default ground")
		changeWeightScore(side, 4, "default ground")	
		airCostPolicy(side, "default ground")	

	elseif tactic == tactics["restore air default condition"] then
		changeNumberAircraftForTactics(side, nil, "default air")
		changeWeightScore(side, 4, "default air")	
		airCostPolicy(side, "default air")	

	else
		log.warn("unknow tactic: " .. tactic)
	end
end

-- evaluate statistical data to define the tactical directive_selected to be applied
function commander()

	local directive_selected = {}
	local directive_ordered = {}
	local directive_executed = {}

	local actual_air_winner = statistic_data.global_losses.air.total.winner
	local actual_air_delta_loss_perc = statistic_data.global_losses.air.total.delta_loss_perc -- air losses percentage difference from loser and winner
	local actual_air_delta_cost_loss_perc = statistic_data.global_losses.air.total.delta_loss_cost_perc -- air losses percentage cost difference from loser and winner
	local actual_ground_winner = statistic_data.global_losses.ground.total.winner
	local actual_ground_delta_loss_perc = statistic_data.global_losses.ground.total.delta_loss_perc
	local actual_ship_winner = statistic_data.global_losses.ship.total.winner
	local actual_ship_delta_loss_perc = statistic_data.global_losses.ship.total.delta_loss_perc 
	local air_diff_loss_perc = statistic_data.global_losses.air.total.diff_loss_perc -- variazione tra le missioni delle differenze blue-red delle perdite aeree totali 
	local ground_diff_loss_perc = statistic_data.global_losses.ground.total.diff_loss_perc -- variazione tra le missioni delle differenze blue-red delle perdite terrestri totali
	local min_perc_for_condition = 5
	local max_perc_for_condition = 80
	local checkDifferential = false -- false: directives will be based on delta_loss_perc value (actual campaign delta( blue-red) losses percentage), true: directives will be based on diff_loss_perc value (mission trend of campaign  delta( blue-red) losses percentage )
	local num_report = camp.mission - MISSION_START_COMMANDER + 1

	-- return perc/weight value for changeNumberAircraftForTactics() or changePriorityTask() or changeWeightScore()
	local function value(type, value, sign)

		local p1 = { -- param to compute perc for changeNumberAircraftForTactics()
			inc_min = {min_perc_for_condition, 0.1}, 	--x1, y1
			inc_max = {max_perc_for_condition, 0.5}, 	--x2, y2							
		}

		local w = { -- param to compute perc for changeWeightScore()
			inc_min = {min_perc_for_condition, 1.5},	--x1, y1
			inc_max = {max_perc_for_condition, 6}, 		--x2, y2							
			dec_min = {min_perc_for_condition, 0.75}, 	--x1, y1
			dec_max = {max_perc_for_condition, 0.15}, 	--x2, y2							
		}

		local p2 = { -- param to compute perc for changePriorityTask()
			inc_min = {min_perc_for_condition, 0.1}, 	-- x1,y1
			inc_max = {max_perc_for_condition, 0.8},  	-- x2, y2							
		}

		local ret

		if type == "perc-CNAFT" then
			ret = ( p1.inc_min[2] + (p1.inc_max[2] - p1.inc_min[2]) * (value - p1.inc_min[1]) / (p1.inc_max[1] - p1.inc_min[1]) ) * sign
		
		elseif type == "perc-CPT" then
			ret = ( p2.inc_min[2] + (p2.inc_max[2] - p2.inc_min[2]) * (value - p2.inc_min[1]) /(p2.inc_max[1] - p2.inc_min[1]) ) * sign

		elseif type == "w-CWS" and sign == 1 then
			ret = w.inc_min[2] + (w.inc_max[2] - w.inc_min[2]) * (value - w.inc_min[1]) /(w.inc_max[1] - w.inc_min[1])

		elseif type == "w-CWS" and sign == -1 then
			ret = w.dec_min[2] + (w.dec_max[2] - w.dec_min[2]) * (value - w.dec_min[1]) /(w.dec_max[1] - w.dec_min[1])
		
		else
			print("WARNING unknow type: " .. type .. " or |sign| > 1: " .. ( sign or "nil") )
			log.warn("Unknow type: " .. type .. " or |sign| > 1: " .. ( sign or "nil") )
		end

		return ret
	end
	
	local side = {"red", "blue"}
	loadReportCommander()

	local num_report = camp.mission - MISSION_START_COMMANDER + 1

	local report = {
				
		mission = camp.mission,
		winner = {
			air = actual_air_winner,
			ground = actual_ground_winner,
			ship = actual_ship_winner,
		},		
		directive_executed = {},
		target_priority = {},
		config_module = {},
		
	}

	table.insert(report_commander, num_report, report)

	for i, side_name in ipairs(side) do
		local enemy_side_name = side[ i%2 + 1]
		directive_selected[side_name] = {}
		local air_diff_loss = {
			red = statistic_data.global_losses.air.total.med_loss_perc.red,
			blue = statistic_data.global_losses.air.total.med_loss_perc.blue,
		}
		local ground_diff_loss = {
			red = statistic_data.global_losses.ground.total.med_loss_perc.red,
			blue = statistic_data.global_losses.ground.total.med_loss_perc.blue,
		}
				
		if camp.mission >= MISSION_START_COMMANDER or local_test then 
			
			report_commander[ num_report ].directive_executed[side_name] = {}
			

			if num_report  % RESET_PERIOD  == 0 then --cyclics reset
				changeNumberAircraftForTactics(side_name, nil, "default")								-- reset min, max, requested aircraft 
				changeWeightScore(side_name, nil, "default")										-- reset weight score 				
				airCostPolicy(side_name, "default")													-- reset use of expensive asset
				resetPriorityTask(side_name, "all", nil, nil)						-- decrement priority for Strike task and soft attribute
				directive_executed = {
					side = side_name,					
					directives = {"mission: " .. camp.mission .. ", num_report: " .. num_report .. "reset period: " .. RESET_PERIOD .. "cyclic reset"}
				}


			else							
				--  -= {}								
				local loss_value_perc = false
				local percCNAFT
				local percCPT
				local w_inc_CWS
				local w_dec_CWS
				print( "air_diff_loss[enemy_side_name]: " .. air_diff_loss[enemy_side_name] ..", actual_air_delta_cost_loss_perc: " .. actual_air_delta_cost_loss_perc )

				if checkDifferential and air_diff_loss[enemy_side_name] > min_perc_for_condition then
					loss_value_perc = air_diff_loss[enemy_side_name]
					
				elseif actual_air_delta_cost_loss_perc > min_perc_for_condition then
					loss_value_perc = actual_air_delta_cost_loss_perc

					if loss_value_perc > max_perc_for_condition then
						loss_value_perc = max_perc_for_condition 
					end
				end

				if loss_value_perc then -- exist condition to modify config parameter

					percCNAFT = value("perc-CNAFT", loss_value_perc, 1)																		
					percCPT = value("perc-CPT", loss_value_perc, 1)																		
					w_inc_CWS = value("w-CWS", loss_value_perc, 1)	
					w_dec_CWS = value("w-CWS", loss_value_perc, -1)	
					
					print( "loss_value_perc: " .. loss_value_perc .. ", percCNAFT: " .. percCNAFT .. ", percCPT: " .. percCPT .. ", w_inc_CWS: " .. w_inc_CWS .. ", w_dec_CWS: " .. w_dec_CWS )
					print ( "actual_air_winner: " .. actual_air_winner .. ", actual_ground_winner: " .. actual_ground_winner )

					directive_executed = {
						side = side_name,
						percVarNumMaxAircraft = percCNAFT,
						percVarPriorityTask = percCPT,
						percVarDecWeight = w_dec_CWS,
						percVarIncWeight = w_inc_CWS,						
						directives = {}
					}
					

					if actual_air_winner == side_name then -- side_name is actual air winner

						-- directive for side_name like winner in air and ground 
						if actual_ground_winner == side_name then -- side_name is actual air winner and also actual ground winner: side_name is a complete winner (air and ground)																											
							changeNumberAircraftForTactics(side_name, -percCNAFT, "air superiority")			-- decrement min, max, requested aircraft for ground task/role		
							changeWeightScore(side_name, w_dec_CWS, "air offensive")							-- decrement weight score for air offensive task							
							changeWeightScore(side_name, w_dec_CWS, "ground")									-- decrements weight score for ground offensive task							
							airCostPolicy(side_name, "decrement")												-- decrement use of expensive asset
							changePriorityTask(side_name, "Strike", "soft", nil, -percCPT)						-- decrement priority for Strike task and soft attribute
							changePriorityTask(side_name, "Strike", "armor", nil, -percCPT)						-- decrement priority for Strike task and armor attribute																										
							changePriorityTask(side_name, "Intercept", nil, nil, -percCPT)						-- decrement priority for Intercept task
							changePriorityTask(side_name, "Fighter Sweep", nil, nil, -percCPT)					-- decrement priority for Fighter Sweep task
							changePriorityTask(side_name, "Escort", nil, nil, -percCPT)							-- decrement priority for Escort task									
							changePriorityTask(side_name, "Strike", "Structure", nil, percCPT)					-- increment priority for Strike task and Structure attribute
							changePriorityTask(side_name, "Strike", "Bridge", nil, percCPT)						-- increment priority for Strike task and Bridge attribute
							--changePriorityTask(side_name, "Strike", "SAM", nil, percCPT)						-- increment priority for Strike task and SAM attribute
							directive_executed.directives = {																
								"decrement min, max, requested aircraft for ground task/role",
								"decrement weight score for air offensive task",
								"decrements weight score for ground task",
								"decrement use of expensive asset",
								"decrement priority for Strike task and soft attribute",
								"decrement priority for Strike task and armor attribute",																										
								"decrement priority for Intercept task",
								"decrement priority for Fighter Sweep task",
								"decrement priority for Escort task",					
								"increment priority for Strike task and Structure attribute",
								"increment priority for Strike task and Bridge attribute",														
							}
							print("directive for side_name like winner in air and ground:\n" .. inspect(directive_executed))

						-- directive for side_name like winner in air and loser in ground 
						elseif actual_ground_winner == enemy_side_name then-- side_name is actual air winner and enemy_side_name is actual ground winner: side_name is air winner but ground loser
							changeNumberAircraftForTactics(side_name, -percCNAFT, "air superiority")			-- decrement min, max, requested aircraft for air superiority task/role		
							changeNumberAircraftForTactics(side_name, percCNAFT, "ground")						-- increment min, max, requested aircraft for ground task/role		
							changeWeightScore(side_name, w_dec_CWS, "air offensive")							-- decrement weight score for air offensive task							
							changeWeightScore(side_name, w_inc_CWS, "ground")									-- increments weight score for ground offensive task							
							airCostPolicy(side_name, "air decrement")											-- decrement use of expensive a2a asset
							airCostPolicy(side_name, "ground increment")										-- increment use of expensive a2g asset
							changePriorityTask(side_name, "Strike", "soft", nil, percCPT)						-- increment priority for Strike task and soft attribute
							changePriorityTask(side_name, "Strike", "armor", nil, percCPT)						-- increment priority for Strike task and armor attribute																										
							changePriorityTask(side_name, "Intercept", nil, nil, -percCPT)						-- decrement priority for Intercept task
							changePriorityTask(side_name, "Fighter Sweep", nil, nil, -percCPT)					-- decrement priority for Fighter Sweep task							
							changePriorityTask(side_name, "Strike", "Structure", nil, percCPT)					-- increment priority for Strike task and Structure attribute
							changePriorityTask(side_name, "Strike", "Bridge", nil, percCPT)						-- increment priority for Strike task and Bridge attribute
							changePriorityTask(side_name, "Strike", "SAM", nil, -percCPT)						-- decrement priority for Strike task and SAM attribute
							directive_executed.directives = {																
								"decrement min, max, requested aircraft for air superiority task/role",
								"increment min, max, requested aircraft for ground task/role",
								"decrement weight score for air offensive task",
								"increments weight score for ground task",
								"decrement use of expensive a2a asset",
								"increment use of expensive a2g asset",
								"increment priority for Strike task and soft attribute",
								"increment priority for Strike task and armor attribute",																										
								"decrement priority for Intercept task",
								"decrement priority for Fighter Sweep task",											
								"increment priority for Strike task and Structure attribute",
								"increment priority for Strike task and Bridge attribute",
								"decrement priority for Strike task and SAM attribute",								
							}
							print("directive for side_name like winner in air and loser in ground :\n" .. inspect(directive_executed))

						-- directive for side_name like winner in air and tie in ground 
						else -- side_name is actual air winner and actual ground winner is tie: side name is air winner but ground winner is tie
							--changeNumberAircraftForTactics(side, -percCNAFT, "air superiority")				-- decrement min, max, requested aircraft for ground task/role		
							changeNumberAircraftForTactics(side_name, percCNAFT, "ground")						-- increment min, max, requested aircraft for ground task/role		
							changeWeightScore(side_name, w_dec_CWS, "air offensive")							-- decrement weight score for air offensive task							
							changeWeightScore(side_name, w_inc_CWS, "ground")									-- increments weight score for ground offensive task							
							airCostPolicy(side_name, "air decrement")											-- decrement use of expensive asset
							airCostPolicy(side_name, "ground increment")										-- decrement use of expensive asset
							changePriorityTask(side_name, "Strike", "soft", nil, percCPT)						-- increment priority for Strike task and soft attribute
							changePriorityTask(side_name, "Strike", "armor", nil, percCPT)						-- increment priority for Strike task and armor attribute																										
							changePriorityTask(side_name, "Intercept", nil, nil, percCPT)						-- increment priority for Intercept task
							changePriorityTask(side_name, "Fighter Sweep", nil, nil, -percCPT)					-- decrement priority for Fighter Sweep task
							--changePriorityTask(side_name, "Escort", nil, nil, -percCPT)						-- decrement priority for Escort task									
							changePriorityTask(side_name, "Strike", "Structure", nil, percCPT)					-- increment priority for Strike task and Structure attribute
							changePriorityTask(side_name, "Strike", "Bridge", nil, percCPT)						-- increment priority for Strike task and Bridge attribute
							changePriorityTask(side_name, "Strike", "SAM", nil, percCPT)						-- increment priority for Strike task and SAM attribute
							directive_executed.directives = {																								
								"increment min, max, requested aircraft for ground task/role",
								"decrement weight score for air offensive task",
								"increments weight score for ground task",
								"decrement use of expensive a2a asset",
								"increment use of expensive a2g asset",
								"increment priority for Strike task and soft attribute",
								"increment priority for Strike task and armor attribute",																										
								"increment priority for Intercept task",
								"decrement priority for Fighter Sweep task",											
								"increment priority for Strike task and Structure attribute",
								"increment priority for Strike task and Bridge attribute",
								"increment priority for Strike task and SAM attribute",								
							}
							print("directive for side_name like winner in air and tie in ground:\n" .. inspect(directive_executed))


						end
					
					--air loser (side_name) directive	
					elseif actual_air_winner == enemy_side_name then   -- enemy_side_name is actual air winner: side_name is air loser
						
						-- directive for side_name like loser in air and ground 
						if actual_ground_winner == enemy_side_name then -- enemy_side_name is actual air winner and also also ground winner: side_name is a complete loser (air and ground)
							changeNumberAircraftForTactics(side_name, percCNAFT, "air superiority")				-- increment min, max, requested aircraft for ground task/role		
							changeNumberAircraftForTactics(side_name, percCNAFT, "ground")						-- increment min, max, requested aircraft for ground task/role		
							changeWeightScore(side_name, w_inc_CWS, "air defensive")							-- increment weight score for air offensive task							
							changeWeightScore(side_name, w_inc_CWS, "ground")									-- increments weight score for ground offensive task							
							airCostPolicy(side_name, "air increment")											-- increment use of expensive asset
							airCostPolicy(side_name, "ground increment")										-- increment use of expensive asset
							changePriorityTask(side_name, "Strike", "soft", nil, percCPT)						-- increment priority for Strike task and soft attribute
							changePriorityTask(side_name, "Strike", "armor", nil, percCPT)						-- increment priority for Strike task and armor attribute																										
							changePriorityTask(side_name, "Intercept", nil, nil, percCPT)						-- increment priority for Intercept task
							changePriorityTask(side_name, "Fighter Sweep", nil, nil, percCPT)					-- increment priority for Fighter Sweep task
							changePriorityTask(side_name, "Escort", nil, nil, percCPT)							-- increment priority for Escort task									
							changePriorityTask(side_name, "Strike", "Structure", nil, -percCPT)					-- decrement priority for Strike task and Structure attribute
							changePriorityTask(side_name, "Strike", "Bridge", nil, -percCPT)					-- decrement priority for Strike task and Bridge attribute
							changePriorityTask(side_name, "Strike", "SAM", nil, percCPT)						-- increment priority for Strike task and SAM attribute
							directive_executed.directives = {											
								"increment min, max, requested aircraft for air superiority task/role",													
								"increment min, max, requested aircraft for ground task/role",
								"increment weight score for air offensive task",
								"increments weight score for ground offensive task",
								"increment use of expensive a2a asset",
								"increment use of expensive a2g asset",
								"increment priority for Strike task and soft attribute",
								"increment priority for Strike task and armor attribute",																										
								"increment priority for Intercept task",
								"increment priority for Fighter Sweep task",											
								"increment priority for Escort task",											
								"decrement priority for Strike task and Structure attribute",
								"decrement priority for Strike task and Bridge attribute",
								"increment priority for Strike task and SAM attribute",								
							}
							print("directive for side_name like loser in air and ground:\n" .. inspect(directive_executed))

						
						-- directive for side_name like loser in air and winner in ground 
						elseif actual_ground_winner == side_name then -- enemy_side_name is actual air winner and side_name is actual ground winner: side_name is air loser but is ground winner
							changeNumberAircraftForTactics(side_name, percCNAFT, "air defensive")				-- increment min, max, requested aircraft for ground task/role		
							changeNumberAircraftForTactics(side_name, -percCNAFT, "ground")						-- decrement min, max, requested aircraft for ground task/role		
							changeWeightScore(side_name, w_inc_CWS, "air defensive")							-- increment weight score for air offensive task							
							changeWeightScore(side_name, w_dec_CWS, "ground")									-- decrements weight score for ground offensive task							
							airCostPolicy(side_name, "air increment")											-- increment use of expensive asset
							airCostPolicy(side_name, "ground decrement")										-- decrement use of expensive asset
							changePriorityTask(side_name, "Strike", "soft", nil, -percCPT)						-- decrement priority for Strike task and soft attribute
							changePriorityTask(side_name, "Strike", "armor", nil, -percCPT)						-- decrement priority for Strike task and armor attribute																										
							changePriorityTask(side_name, "Intercept", nil, nil, percCPT)						-- increment priority for Intercept task
							changePriorityTask(side_name, "Fighter Sweep", nil, nil, -percCPT)					-- decrement priority for Fighter Sweep task
							changePriorityTask(side_name, "Escort", nil, nil, percCPT)							-- increment priority for Escort task									
							changePriorityTask(side_name, "Strike", "Structure", nil, percCPT)					-- increment priority for Strike task and Structure attribute
							changePriorityTask(side_name, "Strike", "Bridge", nil, percCPT)						-- increment priority for Strike task and Bridge attribute
							changePriorityTask(side_name, "Strike", "SAM", nil, -percCPT)						-- decrement priority for Strike task and SAM attribute
							directive_executed.directives = {											
								"increment min, max, requested aircraft for air defensive task/role",													
								"decrement min, max, requested aircraft for ground task/role",
								"increment weight score for air defensive task",
								"decrements weight score for ground task",
								"increment use of expensive a2a asset",
								"decrement use of expensive a2g asset",
								"decrement priority for Strike task and soft attribute",
								"decrement priority for Strike task and armor attribute",																										
								"increment priority for Intercept task",
								"decrement priority for Fighter Sweep task",											
								"increment priority for Escort task",											
								"increment priority for Strike task and Structure attribute",
								"increment priority for Strike task and Bridge attribute",
								"decrement priority for Strike task and SAM attribute",								
							}
							print("directive for side_name like loser in air and winner in ground:\n" .. inspect(directive_executed))
					
						-- directive for side_name like loser in air and tie in ground 
						else -- enemy_side_name is actual air winner and actual ground winner is tie: side_name is air loser but is tie on ground winner
							changeNumberAircraftForTactics(side_name, percCNAFT, "air defensive")				-- increment min, max, requested aircraft for ground task/role		
							changeNumberAircraftForTactics(side_name, percCNAFT, "ground")						-- increment min, max, requested aircraft for ground task/role		
							changeWeightScore(side_name, w_inc_CWS, "air defensive")							-- increment weight score for air defensive task							
							changeWeightScore(side_name, w_inc_CWS, "ground")									-- increments weight score for ground offensive task							
							airCostPolicy(side_name, "air increment")											-- increment use of expensive asset
							airCostPolicy(side_name, "ground increment")										-- increment use of expensive asset
							changePriorityTask(side_name, "Strike", "soft", nil, percCPT)						-- increment priority for Strike task and soft attribute
							changePriorityTask(side_name, "Strike", "armor", nil, percCPT)						-- increment priority for Strike task and armor attribute																										
							changePriorityTask(side_name, "Intercept", nil, nil, percCPT)						-- increment priority for Intercept task
							changePriorityTask(side_name, "Fighter Sweep", nil, nil, percCPT)					-- increment priority for Fighter Sweep task
							changePriorityTask(side_name, "Escort", nil, nil, percCPT)							-- increment priority for Escort task									
							changePriorityTask(side_name, "Strike", "Structure", nil, percCPT)					-- increment priority for Strike task and Structure attribute
							changePriorityTask(side_name, "Strike", "Bridge", nil, -percCPT)					-- decrement priority for Strike task and Bridge attribute
							changePriorityTask(side_name, "Strike", "SAM", nil, -percCPT)						-- decrement priority for Strike task and SAM attribute
							directive_executed.directives = {											
								"increment min, max, requested aircraft for air defensive task/role",													
								"increment min, max, requested aircraft for ground task/role",
								"increment weight score for air defensive task",
								"increments weight score for ground task",
								"increment use of expensive a2a asset",
								"increment use of expensive a2g asset",
								"increment priority for Strike task and soft attribute",
								"increment priority for Strike task and armor attribute",																										
								"increment priority for Intercept task",
								"increment priority for Fighter Sweep task",											
								"increment priority for Escort task",											
								"increment priority for Strike task and Structure attribute",
								"decrement priority for Strike task and Bridge attribute",
								"decrement priority for Strike task and SAM attribute",								
							}
							print("directive for side_name like loser in air and tie in ground:\n" .. inspect(directive_executed))
						end
					
					-- tie (side_name) directive
					else  -- actual air winner is tie: side_name is tie in air winner

						-- directive for side_name like ground winner
						if actual_ground_winner == side_name then -- side_name is tie in air war and also actual ground winner: directive for side_name like ground winner
							changeNumberAircraftForTactics(side_name, percCNAFT, "air offensive")				-- increment min, max, requested aircraft for ground task/role		
							changeNumberAircraftForTactics(side_name, -percCNAFT, "ground")						-- decrement min, max, requested aircraft for ground task/role		
							changeWeightScore(side_name, w_inc_CWS, "air offensive")							-- increment weight score for air offensive task							
							changeWeightScore(side_name, w_inc_CWS, "ground")									-- increments weight score for ground offensive task							
							airCostPolicy(side_name, "air increment")											-- increment use of expensive asset
							airCostPolicy(side_name, "ground decrement")										-- decrement use of expensive asset
							changePriorityTask(side_name, "Strike", "soft", nil, -percCPT)						-- decrement priority for Strike task and soft attribute
							changePriorityTask(side_name, "Strike", "armor", nil, -percCPT)						-- decrement priority for Strike task and armor attribute																										
							--changePriorityTask(side_name, "Intercept", nil, nil, percCPT)						-- increment priority for Intercept task
							changePriorityTask(side_name, "Fighter Sweep", nil, nil, percCPT)					-- increment priority for Fighter Sweep task
							--changePriorityTask(side_name, "Escort", nil, nil, percCPT)						-- increment priority for Escort task									
							changePriorityTask(side_name, "Strike", "Structure", nil, percCPT)					-- increment priority for Strike task and Structure attribute
							changePriorityTask(side_name, "Strike", "Bridge", nil, -percCPT)					-- decrement priority for Strike task and Bridge attribute
							changePriorityTask(side_name, "Strike", "SAM", nil, -percCPT)						-- decrement priority for Strike task and SAM attribute
							directive_executed.directives = {											
								"increment min, max, requested aircraft for air offensivee task/role",													
								"decrement min, max, requested aircraft for ground task/role",
								"increment weight score for air offensive task",
								"increments weight score for ground task",
								"increment use of expensive a2a asset",
								"decrement use of expensive a2g asset",
								"decrement priority for Strike task and soft attribute",
								"decrement priority for Strike task and armor attribute",																																		
								"increment priority for Fighter Sweep task",																			
								"increment priority for Strike task and Structure attribute",
								"decrement priority for Strike task and Bridge attribute",
								"decrement priority for Strike task and SAM attribute",								
							}
							print("directive for side_name like ground winner:\n" .. inspect(directive_executed))
					
						-- directive for side_name like ground loser
						elseif actual_ground_winner == enemy_side_name then-- side_name is tie in air war and is loser in ground war: directive for side_name like ground loser
							changeNumberAircraftForTactics(side_name, percCNAFT, "air offensive")				-- increment min, max, requested aircraft for ground task/role		
							changeNumberAircraftForTactics(side_name, percCNAFT, "ground")						-- increment min, max, requested aircraft for ground task/role		
							changeWeightScore(side_name, w_inc_CWS, "air offensive")							-- increment weight score for air offensive task							
							changeWeightScore(side_name, w_inc_CWS, "ground")									-- increments weight score for ground offensive task							
							airCostPolicy(side_name, "air increment")											-- increment use of expensive asset
							airCostPolicy(side_name, "ground increment")										-- decrement use of expensive asset
							changePriorityTask(side_name, "Strike", "soft", nil, percCPT)						-- increment priority for Strike task and soft attribute
							changePriorityTask(side_name, "Strike", "armor", nil, percCPT)						-- increment priority for Strike task and armor attribute																										
							--changePriorityTask(side_name, "Intercept", nil, nil, percCPT)						-- increment priority for Intercept task
							--changePriorityTask(side_name, "Fighter Sweep", nil, nil, percCPT)					-- increment priority for Fighter Sweep task
							--changePriorityTask(side_name, "Escort", nil, nil, percCPT)						-- increment priority for Escort task									
							changePriorityTask(side_name, "Strike", "Structure", nil, percCPT)					-- increment priority for Strike task and Structure attribute
							changePriorityTask(side_name, "Strike", "Bridge", nil, percCPT)						-- increment priority for Strike task and Bridge attribute
							changePriorityTask(side_name, "Strike", "SAM", nil, -percCPT)						-- decrement priority for Strike task and SAM attribute
							directive_executed.directives = {											
								"increment min, max, requested aircraft for air offensivee task/role",													
								"increment min, max, requested aircraft for ground task/role",
								"increment weight score for air offensive task",
								"increments weight score for ground task",
								"increment use of expensive a2a asset",
								"increment use of expensive a2g asset",
								"increment priority for Strike task and soft attribute",
								"increment priority for Strike task and armor attribute",																																										
								"increment priority for Strike task and Structure attribute",
								"increment priority for Strike task and Bridge attribute",
								"decrement priority for Strike task and SAM attribute",								
							}
							print("directive for side_name like ground loser:\n" .. inspect(directive_executed))
						
						-- directive for total tie
						else -- side_name is tie in air and ground war: directive side_name and enemy_side_name for complete tie and break for side_name loop
							local directives =  {
								air = { "air offensive", "air defensive", "air superiority"},
								ground = { "ground offensive", "ground defensive", "ground interdiction"},
							}
							local priority =  {
								air_task = { "Intercept", "Fighter Sweep", "CAP", "Escort"},
								ground_attribute = { "soft", "Structure", "Bridge", "SAM"},
							}

							local delta_value = 1 + math.random(30)/100
							local percCNAFT_Air = percCNAFT * delta_value
							delta_value = 1 + math.random(30)/100
							local percCNAFT_Ground = percCNAFT * delta_value
							delta_value = 1 + math.random(30)/100
							local percCPT_Air = percCPT * delta_value
							delta_value = 1 + math.random(30)/100
							local percCPT_Ground = percCPT * delta_value
							delta_value = 1 + math.random(30)/100
							local w_incCWS_ = w_inc_CWS * delta_value

							local dir_air = directives[math.random(1, #directives.air)]
							local dir_ground = directives[math.random(1, #directives.ground)]

							local air_task = priority.air_task[math.random(1, #priority.air_task)]
							local ground_attribute = priority.ground_task[math.random(1, #priority.ground_task)]

							changeNumberAircraftForTactics(side_name, percCNAFT_Air, dir_air)					-- increment min, max, requested aircraft for air task/role		
							changeNumberAircraftForTactics(side_name, percCNAFT_Ground, dir_ground)				-- increment min, max, requested aircraft for ground task/role		
							changeWeightScore(side_name, w_incCWS_, dir_air)									-- increment weight score for air offensive task							
							changeWeightScore(side_name, w_incCWS_, dir_ground)									-- increments weight score for ground offensive task														
							changePriorityTask(side_name, air_task, nil, nil, percCPT_Air)						-- increment priority for Strike task and soft attribute
							changePriorityTask(side_name, "Strike", ground_attribute, nil, percCPT_Ground)		-- increment priority for Strike task and armor attribute	
							directive_executed.directives = {											
								"increment min, max( + " .. percCNAFT_Air ..  " ) , requested aircraft for " .. dir_air .. " task/role",													
								"increment min, max( + " .. percCNAFT_Ground ..  " ) , requested aircraft for " .. dir_ground .. " task/role",
								"increment weight score( + " ..  w_incCWS_ ..  " ) for " .. dir_air .. " task",
								"increments weight score( + " ..  w_incCWS_ ..  " ) for " .. dir_ground .. " task",								
								"increment priority( + " .. percCPT_Air ..  " ) for " ..  air_task .. " task and soft attribute",
								"increment priority( + " .. percCPT_Ground ..  " ) for Strike task and " .. ground_attribute .." attribute",																																																		
							}																									
							print("directive for total tie:\n" .. inspect(directive_executed))
						end
					end				
				else
					print("nothing directive execute: air_diff_loss[enemy_side_name] and actual_air_delta_cost_loss_perc are lesser of limit: " ..  min_perc_for_condition)
				end
			end				
		
			report_commander[ num_report ].directive_executed[side_name] = directive_executed.directives -- store directive in report				
			report_commander[ num_report ].target_priority[side_name] = getTargetPriority(side_name)
			report_commander[ num_report ].config_module = camp.module_config 			
		end
	end	
	os.remove("Active/report_commander.lua")		
	SaveTabOnPath( "Active/", "report_commander", report_commander )       
	return directive_ordered
end

-- PREPROCESSING
loadModuleConfigDefault()
loadPriorityDefault()


-- TESTING (very little)
if local_test then
	local testChangeNumberAircraftForTacticsFlg = false
	local testAirCostChangeFlg = false
	local testAirdirective_executedFlg = false
	local testCommander = true
	
	
	printPriorityTable("default value")

	if testChangeNumberAircraftForTacticsFlg then --side, perc, operations		
		changeNumberAircraftForTactics("blue", 30, "all")
		print("change - camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_STRIKE: " .. camp.module_config.ATO_Generator["blue"].MAX_AIRCRAFT_FOR_STRIKE)
		--printPriorityTable("changeNumberAircraftForTactics('blue', 30, 'all')")
		changeNumberAircraftForTactics("blue", nil, "default")
		print("reset - camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_STRIKE: " .. camp.module_config.ATO_Generator["blue"].MAX_AIRCRAFT_FOR_STRIKE)		
				
	end

	if testAirCostChangeFlg then --side, perc, operations
		airCostChange("blue", "all", 30)
		print("change - camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST: " .. inspect(camp.module_config.ATO_Generator["blue"].WEIGHT_SCORE_FOR_AIRCRAFT_COST))
		print("change - camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST: " .. inspect(camp.module_config.ATO_Generator["blue"].WEIGHT_SCORE_FOR_LOADOUT_COST))
		airCostChange("blue", "default", nil)
		print("reset - camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST: " .. inspect(camp.module_config.ATO_Generator["blue"].WEIGHT_SCORE_FOR_AIRCRAFT_COST))
		print("reset - camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST: " .. inspect(camp.module_config.ATO_Generator["blue"].WEIGHT_SCORE_FOR_LOADOUT_COST))				

	end

	if testAirdirective_executedFlg then --side, perc, operations		
		print("init - camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_STRIKE: " .. camp.module_config.ATO_Generator["blue"].MAX_AIRCRAFT_FOR_STRIKE)
		print("init - camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_SWEEP: " .. camp.module_config.ATO_Generator["blue"].MAX_AIRCRAFT_FOR_SWEEP )
		print("init - camp.module_config.SCORE_TASK_FACTOR[side].Strike.Bridge: " .. camp.module_config.SCORE_TASK_FACTOR["blue"].Strike.Bridge )
		print("init - camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST['Attacker']: " .. camp.module_config.ATO_Generator["blue"].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Attacker"] )
		print("init - camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST['Fighter']: " .. camp.module_config.ATO_Generator["blue"].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Fighter"] )			
		airdirective_executed("blue", "increment offensive strategic action and resource")		
		print("change - camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_STRIKE: " .. camp.module_config.ATO_Generator["blue"].MAX_AIRCRAFT_FOR_STRIKE)
		print("change - camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_SWEEP: " .. camp.module_config.ATO_Generator["blue"].MAX_AIRCRAFT_FOR_SWEEP )
		print("change - camp.module_config.SCORE_TASK_FACTOR[side].Strike.Bridge: " .. camp.module_config.SCORE_TASK_FACTOR["blue"].Strike.Bridge )
		print("change - camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST['Attacker']: " .. camp.module_config.ATO_Generator["blue"].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Attacker"] )
		print("change - camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST['Fighter']: " .. camp.module_config.ATO_Generator["blue"].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Fighter"] )			
		airdirective_executed("blue", "restore global default condition")
		print("reset - camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_STRIKE: " .. camp.module_config.ATO_Generator["blue"].MAX_AIRCRAFT_FOR_STRIKE)
		print("reset - camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_SWEEP: " .. camp.module_config.ATO_Generator["blue"].MAX_AIRCRAFT_FOR_SWEEP )
		print("reset - camp.module_config.SCORE_TASK_FACTOR[side].Strike.Bridge: " .. camp.module_config.SCORE_TASK_FACTOR["blue"].Strike.Bridge )
		print("reset - camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST['Attacker']: " .. camp.module_config.ATO_Generator["blue"].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Attacker"] )
		print("reset - camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST['Fighter']: " .. camp.module_config.ATO_Generator["blue"].WEIGHT_SCORE_FOR_AIRCRAFT_COST["Fighter"] )			

		print("init -  targetlist.blue['203 SA-2 Site A-3'].priority: " .. targetlist.blue["203 SA-2 Site A-3"].priority )
		airdirective_executed("blue", "increment priority for SAM strike operations")
		print("change -  targetlist.blue['203 SA-2 Site A-3'].priority: " .. targetlist.blue["203 SA-2 Site A-3"].priority )
		airdirective_executed("blue", "reset priority for SAM operations")
		print("reset -  targetlist.blue['203 SA-2 Site A-3'].priority: " .. targetlist.blue["203 SA-2 Site A-3"].priority )
	end

	if testCommander then
		
		local directive_executed = commander()
		print("-- test commander() -- ")
		print("directive_executed: \n" .. inspect(directive_executed) .. "\n\n")
		print("report_commander.directive_executed: \n" .. inspect(report_commander[-3].directive_executed) .. "\n\n")
		print("\n\n-- end test commander() -- ")		
	end

elseif not FirstMission then
		commander()
end

--[[

module_config[module_name] = getModuleConfig(module_name)
saveModuleConfig( module_config[module_name] )




implementare modulo tattico per blue e red per elaborazione configurazione parametri moduli,

funzioni: 
evalStatusGround()
 - evalStatusGroundVehicle()
 - evalStatusGroundShip()
 - evalStatusGroundLogistic(): Plant & Line
 - evalStatusGroundStatic()

valuta:
aumentare/rinforzare l'esecuzione di missioni GA (supporto truppe): 
se 

rinforzare il supporto ESCORT: 
se le perdite di bomber/attacker dovute ai fighter è significativo: valuta i rapporti k_blue(red) = perdite bomber/ perdite fighter blue e red,   INCR= k_blue / k_red, 

rinforzare il supporto SEAD: 
se le perdite di bomber/attacker dovute ai ASM radar è significativo

aumentare/rinforzare l'esecuzione di missioni CAP, Intercept, Fighter Sweep : 
se il danno dei vehicle/Logistic/Static è significativo rispetto al totale dei ve
il modulo deve fornire un report preciso per la scelta dei blue mentre deve essere aleatorio per quelle dei red. L'aleatorietà deve dipendere dalle capacxità di intelligenze (recom ground, air, economy ec


]]