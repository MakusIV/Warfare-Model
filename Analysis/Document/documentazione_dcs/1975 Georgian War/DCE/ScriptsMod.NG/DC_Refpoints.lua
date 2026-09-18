--For easy reference to x-y coordinates, create Refpoints from trigger zones in base_mission
--Initiated by MAIN_NextMission.lua
-------------------------------------------------------------------------------------------------------

if not versionDCE then 
	versionDCE = {} 
end

               -- VERSION --

versionDCE["DC_Refpoints.lua"] = "OB.1.0.0"

---------------------------------------------------------------------------------------------------------
-- Old_Boy rev. OB.1.0.0: implements logging code

local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua")
-- NOTE MARCO: prova a caricarlo usando require(".. . .. . .. .ScriptsMod."versionPackageICM..".UTIL_Log.lua")
-- NOTE MARCO: https://forum.defold.com/t/including-a-lua-module-solved/2747/2
log.level = LOGGING_LEVEL
log.outfile = LOG_DIR .. "LOG_DC_Refpoints." .. camp.mission .. ".log" 
local local_debug = true -- local debug   
log.info("Start")


--Check all trigger zones on base_mission and store their x-y coordinates for easier use (stored in Refpoint )
log.info("Check all trigger zones on base_mission and store their x-y coordinates for easier use (stored in Refpoint )")
Refpoint = {}														--table to store x-y coordinates of trigger zones as reference points

for zone_n,zone in ipairs(mission.triggers.zones) do				--iterate throug trigger zones in mission
	Refpoint[zone.name] = {											--store x-y coordinates in Refpoint array
		x = zone.x,
		y = zone.y
	}
end
log.trace("Refpoint tab:\n" .. inspect(Refpoint))