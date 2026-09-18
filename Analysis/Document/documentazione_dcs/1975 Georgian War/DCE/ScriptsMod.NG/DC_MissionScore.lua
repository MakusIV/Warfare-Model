--To to define how the next mission will be scored
--Mission score determines if after mission conclusion the campaign stage increases, decreases or stays the same (stages used by the the DCS campaign system)
--For DCE campaigns, the first mission must always advance in stage (have a score of >50), all subsequent missions must always stay in stage (have a score of 50)
--Initiated by MAIN_NextMission.lua
-------------------------------------------------------------------------------------------------------

if not versionDCE then 
	versionDCE = {} 
end

               -- VERSION --

versionDCE["DC_MissionScore.lua"] = "OB.1.0.0"

---------------------------------------------------------------------------------------------------------
-- Old_Boy rev. OB.1.0.0: implements logging code


local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua")
-- NOTE MARCO: prova a caricarlo usando require(".. . .. . .. .ScriptsMod."versionPackageICM..".UTIL_Log.lua")
-- NOTE MARCO: https://forum.defold.com/t/including-a-lua-module-solved/2747/2
log.level = LOGGING_LEVEL
log.outfile = LOG_DIR .. "LOG_DC_MissionScore." .. camp.mission .. ".log" 
local local_debug = true -- local debug   
log.info("Start")



--define the mission score
log.info("define the mission score and mission goals")
do
	local mscore
	if FirstMission then									--the mission is the first campaign mission
		mscore = 51											--mission is scored 51 (proceed to next campaign stage)
	else													--not first campaign mission
		mscore = 50											--mission is scored 50 (stay in campaign stage)
	end

	local goals = {
		["rules"] = {
			[1] = {
				["coalitionlist"] = "red",
                ["zone"] = "",
                ["percent"] = 100,
                ["predicate"] = "c_time_after",
                ["seconds"] = 2,
			},
		},
		["score"] = mscore,
		["side"] = "OFFLINE",
		["predicate"] = "score",
		["comment"] = "Assign Mission Score",
	}
	table.insert(mission["goals"], goals)
	log.trace("mission goals:\n" .. inspect(mission["goals"]))

	local result = {
		["conditions"] = {
			[1] = "return(c_time_after(2) )",
		},
		["actions"] = {
			[1] = "a_set_mission_result(" .. mscore .. ")",
		},
		["func"] = {
			[1] = "if mission.result.offline.conditions[1]() then mission.result.offline.actions[1]() end",
		},
	}
	mission["result"]["offline"] = result
	log.trace("mission ['result']['offline']:\n" .. inspect(result))
end