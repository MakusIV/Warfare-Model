--To generate a new mission file. Unzips template mission, defines content of next missions and packs a new mission file
--Initiated by Debrief_Master.lua, BAT_FirstMission.lua or BAT_RedoMission.lua
-------------------------------------------------------------------------------------------------------

if not versionDCE then 
	versionDCE = {} 
end

               -- VERSION --

versionDCE["MAIN_NextMission.lua"] = "OB.1.0.0"

---------------------------------------------------------------------------------------------------------
-- Old_Boy rev. OB.1.0.1: implements compute firepower code
-- Old_Boy rev. OB.1.0.0: implements logging code
-- Old_Boy rev. OB.0.0.1: implements logistic code
-- miguel21 modification M47.c keeps the history of the campaign files (c: save debugging information during mission generation)
-- miguel21 modification M40 Pedro
-- miguel21 modification M38.d Check and Help CampaignMaker
-- miguel21 modification M37.d SuperCarrier
-- Miguel21 modification M35.d (d: info log) version ScriptsMod
-- Miguel21 modification M36.d (d: add timer) MenuRadio request manual TurnIntoWind
-- miguel21 modification M34 custom FrequenceRadio
-- Miguel21 modification M29	AddCommandRadioF10 CallTankRefuel
-- Miguel21 modification M26	destroys targets if below a certain value
-- miguel21 modification M18.e despawn (e: option confMod)
-- Miguel21 modification M11 : Multiplayer
-- Miguel21 modification M14 : Versionning
-- Tomsk    modification M09.b	Integration de  Prune Script
-- Miguel21 M05.c : ajout picture Briefing (c: correction path vide)
-- Miguel21 modification M00b	Integration de conf_mod
-- -------------------------------------------------------------------------------------------------------

--if not versionDCE then versionDCE = {} end
--versionDCE["MAIN_NextMission.lua"] = "1.15.38"


local activate_testing_enviroment = ACTIVATE_TESTING_ENVIROMENTS -- false: for running in DCE enviroment (DEBRIEF_Master.lua launched from DEBUG_DebriefMission.bat), true: for running in testing enviroment (DEBRIEF_Master.lua launched from DEBUG_DebriefMissionTesting.bat) --By Old_Boy
inspect = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_inspect.lua")
local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua")
log.activate = false-- select true to activate log
log.level = LOGGING_LEVEL --"traceVeryLow" -- 
log.outfile = LOG_DIR .. "LOG_MAIN_NextMission." .. camp.mission .. ".log"
local local_debug = false -- local debug   
local active_log = false -- select true to activate log
log.info("Start")

if activate_testing_enviroment then
	log.warn("activate testing enviroment")
end

log.info("unpack template mission file")
----- unpack template mission file ----
local minizip = require('minizip')
log.debug("loaded minzip" .. tostring(minizip ~= nil))
local zipFile = minizip.unzOpen("Init/base_mission.miz", 'rb')
log.debug("open Init/base_mission.miz" .. tostring(zipFile ~= nil))
zipFile:unzLocateFile('mission')
local misStr = zipFile:unzReadAllCurrentFile()
local misStrFunc = loadstring(misStr)()
log.debug("unzip and load mission file" .. tostring(misStrFunc ~= nil))
zipFile:unzLocateFile('options')
local optStr = zipFile:unzReadAllCurrentFile()
local optStrFunc = loadstring(optStr)()
log.debug("unzip and load options file" .. tostring(optStrFunc ~= nil))
zipFile:unzLocateFile('warehouses')
local warStr = zipFile:unzReadAllCurrentFile()
local warStrFunc = loadstring(warStr)()
log.debug("unzip and load warehouses file" .. tostring(warStrFunc ~= nil))
zipFile:unzLocateFile('l10n/DEFAULT/dictionary')
local dicStr = zipFile:unzReadAllCurrentFile()
local dicStrFunc = loadstring(dicStr)()
log.debug("unzip and load l10n/DEFAULT/dictionary file" .. tostring(dicStrFunc ~= nil))
zipFile:unzLocateFile('l10n/DEFAULT/mapResource')
local resStr = zipFile:unzReadAllCurrentFile()
local resStrFunc = loadstring(resStr)()
log.debug("unzip and load l10n/DEFAULT/mapResource file" .. tostring(resStrFunc ~= nil))
zipFile:unzClose()

if mission.version < 19 then --19ok 18bad
	log.warning("(MainNM) ATTENTION: BaseMission.miz is too old. (prior to DCS version 2.7.0) try to save it again with the mission editor. Or ask the creator of this campaign to provide an update.")
	--os.execute 'pause'
	--os.exit()
end

NameTheatre =  string.lower(mission.theatre)

---- add trigger to destory scenery objects -----
log.info("add trigger to destory scenery objects. Iterate through destroyed scenery objects")
mission.trig.flag[1] = true
mission.trig.conditions[1] = "return(true)"
mission.trig.actions[1] = ""
mission.trig.funcStartup[1] = "if mission.trig.conditions[1]() then mission.trig.actions[1]() end"
mission.trigrules[1] = {
	["rules"] = {},
	["eventlist"] = "",
	["actions"] = {},
	["comment"] = "Scenery Destruction",
	["predicate"] = "triggerStart",
}

require("Active/oob_scen")
for scen_name,scen in pairs(oob_scen) do												--iterate through destroyed scenery objects
	
	if scen.x and scen.z then														--destroyed scenery object has x and z coordinates
		
		local zones_n = #mission.triggers.zones	+ 1									--trigger zone number
		log.debug("destroyed scenery object has x and z coordinates -> zones_n = " .. zones_n .. ", add trigger zone")
		--add trigger zone
		mission.triggers.zones[zones_n] = {
			["x"] = scen.x,
			["y"] = scen.z,
			["radius"] = 1,
			["zoneId"] = zones_n,
			["color"] = 
			{
				[1] = 1,
				[2] = 1,
				[3] = 1,
				[4] = 0.15,
			},
			["hidden"] = true,
			["name"] = "SceneryDestroyZone" .. #mission.trigrules[1].actions + 1,
		}
		log.trace("mission.triggers.zones[" .. zones_n .. "]:\n" .. inspect(mission.triggers.zones[zones_n]))
		--add trigger
		mission.trig.actions[1] = mission.trig.actions[1] ..  "a_scenery_destruction_zone(" .. zones_n .. ", 100);"
		log.trace("add trigger actions mission.trig.actions[1]:\n" .. mission.trig.actions[1])
		mission.trigrules[1].actions[#mission.trigrules[1].actions + 1] = {
			["ai_task"] = {
				[1] = "",
				[2] = "",
			},
			["predicate"] = "a_scenery_destruction_zone",
			["destruction_level"] = 100,
			["zone"] = zones_n,
		}
		log.trace("add trigger rules mission.trigrules[1].actions[" .. #mission.trigrules[1].actions + 1 .. "]:\n" .. inspect(mission.trigrules[1].actions[#mission.trigrules[1].actions + 1]))
		log.debug("destroyed scenery object has x and z coordinates -> add new scenery destroyed zone: " .. zones_n .. " in mission.triggers.zone[" .. zones_n .. "]")
	end
end


----- prepare triggers to run files in mission -----
local trig_n = 1

local function AddFileTrigger(filename)
	local nameFunction = "function AddFileTrigger(" .. filename .. "): "    
	log.trace("Start " .. nameFunction)
	trig_n = trig_n + 1
	mapResource["ResKey_Action_" .. trig_n] = filename
	mission.trig.funcStartup[trig_n] = 'if mission.trig.conditions[' .. trig_n .. ']() then mission.trig.actions[' .. trig_n .. ']() end'
	mission.trig.flag[trig_n] = true
	mission.trig.conditions[trig_n] = "return(true)"
	-- mission.trig.actions[trig_n] = 'a_do_script_file(getValueResourceByKey("ResKey_Action_' .. trig_n .. '")); mission.trig.funcStartup[' .. trig_n .. ']=nil;'
	mission.trig.actions[trig_n] = 'a_do_script_file(getValueResourceByKey("ResKey_Action_' .. trig_n .. '"));'		-- Miguel21 modification M11 : Multiplayer
	mission.trigrules[trig_n] = {
		['rules'] = {},
		['eventlist'] = '',
		['comment'] = 'Trigger ' .. trig_n,
		['predicate'] = 'triggerStart',
		['actions'] = {
			[1] = {
				['file'] = 'ResKey_Action_' .. trig_n,
				['predicate'] = 'a_do_script_file',
				['ai_task'] = {
					[1] = '',
					[2] = '',
				},
			},
		},
	}
	log.trace("End " .. nameFunction)
end

AddFileTrigger("camp_status.lua")
AddFileTrigger("EventsTracker.lua")
AddFileTrigger("AddCommandRadioF10.lua")												-- Miguel21 Modification M29
AddFileTrigger("GCIdata.lua")
AddFileTrigger("GCIscript.lua")
AddFileTrigger("ARM_Defence_Script.lua")
AddFileTrigger("CustomTasksScript.lua")
AddFileTrigger("CarrierIntoWindScript.lua")
AddFileTrigger("Pedro.lua")																-- miguel21 modification M40 Pedro

----- run scripts to create content of next mission -----
dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Functions.lua")

CheckConfModMaster()																	-- miguel21 modification M38.d Check and Help CampaignMaker


camp.SC_FullPlaneOnDeck = mission_ini.SC_FullPlaneOnDeck								-- miguel21 modification M37.d SuperCarrier
camp.CVN_Vmax = mission_ini.CVN_Vmax													-- miguel21 modification M37.d SuperCarrier
camp.CVN_windDeck = mission_ini.CVN_windDeck											-- miguel21 modification M37.d SuperCarrier
camp.CVN_despawnAfterLanding = mission_ini.CVN_despawnAfterLanding						-- miguel21 modification M18.e despawn (e: option confMod)
camp.SC_CarrierIntoWind = string.lower(mission_ini.SC_CarrierIntoWind)					-- Miguel21 modification M36.d	MenuRadio request manual TurnIntoWind


local verScriptsModPath = "../../../ScriptsMod."..versionPackageICM.."/UTIL_Version.lua"
local TestPath = io.open(verScriptsModPath, "r")

if  TestPath ~= nil then
	io.close(TestPath)
	dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Version.lua")
	camp.ScriptsMod = version_ScriptsMod.ScriptsMod											-- miguel21 modification M37.d SuperCarrier
end

if not camp.path or camp.path == nil then												-- Miguel21 modification M35.d version ScriptsMod
	camp.path = os.getenv('pathSavedGames')												-- Miguel21 modification M35.e version ScriptsMod
	camp.path = string.gsub(camp.path, "\\", "/") 
end

-- Miguel21 modification M35.d (d: info log) version ScriptsMod
camp["versionPackageICM"] = versionPackageICM

if FirstMission then 
	camp["MissionFilename"] =  camp.title.."_first.miz"	
else
	camp["MissionFilename"] =  camp.title.."_ongoing.miz"	
end

dofile("../../../ScriptsMod."..versionPackageICM.."/DC_LoadoutsAssignment.lua") -- define the firepower for targetlist and db_loadouts (verifica se opportuno inserirlo in DC_UpdateTargetList)	

log.info("require: Init/db_firepower.lua, Init/db_loadouts, Init/db_airbases, Active/oob_air, Active/oob_ground, Init/conf_mod, Init/radios_freq_compatible")
require("Init/db_loadouts")
require("Init/db_airbases")
require("Active/oob_air")
require("Active/oob_ground")
require("Init/conf_mod")															-- Miguel21 modification M00 : need option
require("Init/radios_freq_compatible")												-- miguel21 modification M34 custom FrequenceRadio


-- define firepower value for db_loadouts (only first mission)
if FirstMission then -- per sicurezza (verifica se esiste missione 0)
	
	CopyFile("Init/db_loadouts.lua", "Init/db_loadouts_original.lua")	
	defineLoadoutsFirepowerAndCost()
	defineLoadoutsCruiseParameters()
	SaveTabOnPath( "Init/", "db_loadouts", db_loadouts ) -- save new updated db_loadouts     
else
	defineLoadoutsCruiseParameters()
end


-- INSERISCI QUI IL PREPROCESSING: 
-- Blue_task_table, red_task_table dove la key = task (CAP, INTERCEPT,...) e value = tutte le info relative alle unità con quel task (sottotabella unità).
-- ed_rooster con key = lost, ready e damaged e value nome unità
--  red_base_asset con key = base con value le sottotabelle unità con tutti le proprietà relativa a quella unità

-- create table blue_air_task
blue_air_task = {}
local blue_air_units = oob_air.blue
local red_air_units = oob_air.red
local air_task = {"CAP", "Escort", "Fighter Sweep", "Intercept", "Strike", "SEAD", "Anti-ship Strike", "Laser Illumination", "Refueling", "Transport", "Reconnaissance"}
--local entry_task = {}
-- local key_task 

for n = 1, #air_task do 
	log.traceLow("blue_air_task - task: " .. air_task[n])
	blue_air_task[air_task[n]] = {}
	local key_task

	for n_unit = 1, #blue_air_units do
		log.traceLow("blue_air_units[" .. n_unit .. "]: " .. inspect(blue_air_units[n_unit]))

		for task_name, task_value in pairs (blue_air_units[n_unit].tasks) do
			log.traceVeryLow("blue_air_task - task_name: " .. task_name .. ", task_value: " .. tostring(task_value))
			
			if air_task[n] == task_name and task_value then	
				key_task = blue_air_units[n_unit].name .. "/" .. blue_air_units[n_unit].type
				local entry_task = {}
				entry_task[key_task] = { 					 
						name =  blue_air_units[n_unit].name,
						type =  blue_air_units[n_unit].type,
						country =  blue_air_units[n_unit].country,
						base =  blue_air_units[n_unit].base,
						skill =  blue_air_units[n_unit].skill,
						number =  blue_air_units[n_unit].number,
						num_unit =  blue_air_units[n_unit].num_unit,
				}
				table.insert(blue_air_task[air_task[n]], entry_task)
				log.traceLow("blue_air_task - unit added: " .. inspect(blue_air_task[air_task[n]]) )
			end
		end
	end
end
log.trace("preprocessing: created table blue_air_task:\n" .. inspect(blue_air_task))

-- debug code
if Debug.KillGround.flag then

	for side_name,side in pairs(oob_ground) do														--side table(red/blue)											

		if side_name == Debug.KillGround.sideGround then	

			for country_n,country in pairs(side) do														--country table (number array)

				if country.vehicle then																	--if country has vehicles

					for group_n,group in pairs(country.vehicle.group) do								--groups table (number array)

						for unit_n,unit in pairs(group.units) do										--units table (number array)					
							
							if not unit.dead and math.random(1, 100) <= Debug.KillGround.pourcent then
							
								print("MainNT PasseDestroy "..unit.name)
							
									unit.dead = true														--mark unit as dead in oob_ground
									unit.dead_last = true													--mark unit as died in last mission
									-- unit.CheckDay = camp.day  
							end
						end
					end
				end
	
				if country.static then																--if country has static objects	
	
					for group_n,group in pairs(country.static.group) do								--groups table (number array)
	
						for unit_n,unit in pairs(group.units) do									--units table (number array)
	
							if not unit.dead and math.random(1, 100) <= Debug.KillGround.pourcent then			--check if unitId matches initiatorMissionID (string, needs to be converted to number)
								
								print("MainNT PasseDestroy static "..unit.name)
								
								if unit.dead ~= true then											--unit is not yet dead (some static objects that are spawned in a destroyed state are logged dead at mission start, these must be excluded here)
									group.dead = true												--mark group as dead in oob_ground (static objects can be set as group.dead and spawned in a destroyed state)
									group.hidden = true												--hide dead static object
									unit.dead = true												--mark unit as dead in oob_ground (this is for the targetlist)
									unit.dead_last = true
								end
							end
						
						end
					end
				end
				if country.ship then																--if country has ships
					for group_n,group in pairs(country.ship.group) do								--groups table (number array)
						for unit_n,unit in pairs(group.units) do									--units table (number array)
							if not unit.dead and math.random(1, 100) <= Debug.KillGround.pourcent then				--check if unitId matches initiatorMissionID (string, needs to be converted to number)
								
								print("MainNT PasseDestroy ship "..unit.name)
								
								unit.dead = true													--mark unit as dead in oob_ground
								unit.dead_last = true												--mark unit as died in last mission
								unit.CheckDay = camp.day                            -- ajoute la date de destruction    Miguel21 modification M19 : Repair SAM   
								
							end
						
						end
					end
				end
			end
		end
	end
end
require("Active/targetlist")

-- debug code
if Debug.KillGround.flag then
	for side_name,side in pairs(targetlist) do											--iterate through targetlist
		if side_name == Debug.KillGround.sideTarget then
			for target_name,target in pairs(side) do										--iterate through targets
					
				if target.elements and target.elements[1].x then							--if the target has subelements and is a scenery object target (element has x coordinate)
					for element_n,element in pairs(target.elements) do						--iterate through target elements
						if not element.dead and math.random(1, 100) <= Debug.KillGround.pourcent then		
							
							print("MainNT PasseDestroy __SCENERY__ "..element.name)
							
							
							if element.dead then											--element was already dead previously
								element.dead_last = false									--mark element as not died in last mission
							else
								element.dead = true	
							end
						end
					end
				end
			end
		end
	end
end

require("Active/camp_triggers")

dofile("../../../ScriptsMod."..versionPackageICM.."/DC_Refpoints.lua") -- Check all trigger zones on base_mission and store their x-y coordinates for easier use (stored in Refpoint)
dofile("../../../ScriptsMod."..versionPackageICM.."/DC_MissionScore.lua") -- define the mission score and mission goals
dofile("../../../ScriptsMod."..versionPackageICM.."/DC_Time.lua") -- --advance campaign time, set mission time, day, month and year
dofile("../../../ScriptsMod."..versionPackageICM.."/DC_Weather.lua")
dofile("../../../ScriptsMod."..versionPackageICM.."/DC_DestroyTarget.lua")			-- miguel21 Mod26
dofile("../../../ScriptsMod."..versionPackageICM.."/DC_NavalEnvironment.lua")
dofile("../../../ScriptsMod."..versionPackageICM.."/DC_UpdateTargetlist.lua")
dofile("../../../ScriptsMod."..versionPackageICM.."/DC_CheckTriggers.lua")
dofile("../../../ScriptsMod."..versionPackageICM.."/DC_UpdateTargetlist.lua")
dofile("../../../ScriptsMod."..versionPackageICM.."/DC_UpdateOOBGround.lua")

dofile("../../../ScriptsMod."..versionPackageICM.."/DC_Tactical.lua")

dofile("../../../ScriptsMod."..versionPackageICM.."/ATO_ThreatEvaluation.lua")
dofile("../../../ScriptsMod."..versionPackageICM.."/ATO_RouteGenerator.lua")
dofile("../../../ScriptsMod."..versionPackageICM.."/ATO_Generator.lua")
dofile("../../../ScriptsMod."..versionPackageICM.."/ATO_PlayerAssign.lua")
dofile("../../../ScriptsMod."..versionPackageICM.."/ATO_Timing.lua")
dofile("../../../ScriptsMod."..versionPackageICM.."/ATO_FlightPlan.lua")

dofile("../../../ScriptsMod."..versionPackageICM.."/DC_StaticAircraft.lua")
dofile("../../../ScriptsMod."..versionPackageICM.."/DC_Prune.lua")														-- Tomsk modification M09 Integration de  Prune Script
dofile("../../../ScriptsMod."..versionPackageICM.."/DC_Briefing.lua")

dofile("../../../ScriptsMod."..versionPackageICM.."/DC_EndCampaign.lua")

dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Debug.lua")

mission.currentKey = 999999															--not clear how this works but is required for multiplyer clients to be available for selection on mission start

----- convert tables back to strings for insertion into content files -----
local misStr = "mission = " .. TableSerialization(mission, 0)
local optStr = "options = " .. TableSerialization(options, 0)
local warStr = "warehouses = " .. TableSerialization(warehouses, 0)
local dicStr = "dictionary = " .. TableSerialization(dictionary, 0)
local resStr = "mapResource = " .. TableSerialization(mapResource, 0)
local gciStr = "GCI = " .. TableSerialization(GCI, 0)
local cmpStr = "camp = " .. TableSerialization(camp, 0)

----- create temporary content files of new mission file -----
local misFile = io.open("misFile.lua", "w")											--mission
misFile:write(misStr)
misFile:close()

local optFile = io.open("optFile.lua", "w")											--options
optFile:write(optStr)
optFile:close()

local warFile = io.open("warFile.lua", "w")											--warehouses
warFile:write(warStr)
warFile:close()

local dicFile = io.open("dicFile.lua", "w")											--dictionary
dicFile:write(dicStr)
dicFile:close()

local resFile = io.open("resFile.lua", "w")											--mapResource
resFile:write(resStr)
resFile:close()

local gciFile = io.open("GCIdata.lua", "w")											--GCI data file (EWR radars, AWACS, interceptors)
gciFile:write(gciStr)
gciFile:close()

local cmpFile = io.open("Active/camp_status.lua", "w")								--campaign status file
cmpFile:write(cmpStr)
cmpFile:close()


----- create new mission file and add content files -----

local NbMission  = camp.mission

if mission_ini.backupAllMissionFiles and mission_ini.backupAllMissionFiles == true then
	if not FirstMission then
		NbMission = tostring(camp.mission - 1)
	end

	if string.len(NbMission) > 1 then
		NbMission = "__"..NbMission
	else
		NbMission = "__0"..NbMission
	end
else
	
	NbMission = "__Old"
end

if FirstMission then																--is true if script is launched from GenerateFirstMission.lua
	if not (mission_ini.backupAllMissionFiles and mission_ini.backupAllMissionFiles == true) then		
		os.remove("../"..camp.title.."/Debriefing/"..camp.title.."_first"..NbMission..".miz")
	end
	
	os.rename("../"..camp.title.."_first.miz", "../"..camp.title.."/Debriefing/"..camp.title.."_first"..NbMission..".miz")
	 
	miz = minizip.zipCreate("../" .. camp.title .. "_first.miz")					--create the first campaign mission
else																				--is false if script is launched from Debrief_Master.lua
	if not  (mission_ini.backupAllMissionFiles and mission_ini.backupAllMissionFiles == true ) then
		os.remove( "../"..camp.title.."/Debriefing/"..camp.title.."_ongoing"..NbMission..".miz")
	end
	
	os.rename("../"..camp.title.."_ongoing.miz", "../"..camp.title.."/Debriefing/"..camp.title.."_ongoing"..NbMission..".miz")
	
	miz = minizip.zipCreate("../" .. camp.title .. "_ongoing.miz")					--create the ongoing campaign mission
end
miz:zipAddFile("mission", "misFile.lua")
miz:zipAddFile("options", "optFile.lua")
miz:zipAddFile("warehouses", "warFile.lua")
miz:zipAddFile("l10n/DEFAULT/dictionary", "dicFile.lua")
miz:zipAddFile("l10n/DEFAULT/mapResource", "resFile.lua")
miz:zipAddFile("l10n/DEFAULT/EventsTracker.lua", "../../../ScriptsMod."..versionPackageICM.."/Mission Scripts/EventsTracker.lua")
miz:zipAddFile("l10n/DEFAULT/GCIdata.lua", "GCIdata.lua")
miz:zipAddFile("l10n/DEFAULT/GCIscript.lua", "../../../ScriptsMod."..versionPackageICM.."/Mission Scripts/GCIscript.lua")
miz:zipAddFile("l10n/DEFAULT/ARM_Defence_Script.lua", "../../../ScriptsMod."..versionPackageICM.."/Mission Scripts/ARM_Defence_Script.lua")
miz:zipAddFile("l10n/DEFAULT/CustomTasksScript.lua", "../../../ScriptsMod."..versionPackageICM.."/Mission Scripts/CustomTasksScript.lua")
miz:zipAddFile("l10n/DEFAULT/CarrierIntoWindScript.lua", "../../../ScriptsMod."..versionPackageICM.."/Mission Scripts/CarrierIntoWindScript.lua")
miz:zipAddFile("l10n/DEFAULT/AddCommandRadioF10.lua", "../../../ScriptsMod."..versionPackageICM.."/Mission Scripts/AddCommandRadioF10.lua")				-- Miguel21 Modification M29
miz:zipAddFile("l10n/DEFAULT/Pedro.lua", "../../../ScriptsMod."..versionPackageICM.."/Mission Scripts/Pedro.lua")				-- Miguel21 Pedro TEST
miz:zipAddFile("l10n/DEFAULT/camp_status.lua", "Active/camp_status.lua")
miz:zipAddFile("l10n/DEFAULT/debugGenMission.txt", "Debug/debugGenMission.txt")
miz:zipAddFile("l10n/DEFAULT/debugFlight.txt", "Debug/debugFlight.txt")

local BriefingImages = {}
for _i,_filename in ipairs(BriefingImagesB) do	
	findValue = false
	for i,filename in ipairs(BriefingImages) do
		if _filename == filename then findValue = true    break end
	end
	if not findValue then
		table.insert(BriefingImages, _filename)
	end 
end
for _i,_filename in ipairs(BriefingImagesR) do	
	findValue = false
	for i,filename in ipairs(BriefingImages) do
		if _filename == filename then findValue = true  break end
	end
	if not findValue then
		table.insert(BriefingImages, _filename)
	end 
end

for i,filename in ipairs(BriefingImages) do											-- Miguel21 M05.b : ajout picture Briefing + pictures Target
	if type(filename) == "string" and string.len(filename) > 0 then 				-- Miguel21 M05.c : ajout picture Briefing (c: correction path vide)
		miz:zipAddFile("l10n/DEFAULT/" .. filename, "Images/" .. filename)
	end
end

miz:zipAddFile("l10n/DEFAULT/alarme.wav" , "Sounds/alarme.wav")


miz:zipClose()


----- remove temporary content files -----
os.remove("misFile.lua")
os.remove("optFile.lua")
os.remove("warFile.lua")
os.remove("dicFile.lua")
os.remove("resFile.lua")
os.remove("GCIdata.lua")


----- save updated status files  -----
local air_str = "oob_air = " .. TableSerialization(oob_air, 0)								--make a string
if TypeAlias then
	air_str = air_str .. "TypeAlias = " .. TableSerialization(TypeAlias, 0)
end
local airFile = io.open("Active/oob_air.lua", "w")											--open oob air file
airFile:write(air_str)																		--save new data
airFile:close()

local ground_str = "oob_ground = " .. TableSerialization(oob_ground, 0)						--make a string
local groundFile = io.open("Active/oob_ground.lua", "w")									--open oob ground file
groundFile:write(ground_str)																--save new data
groundFile:close()


local tgt_str = "targetlist = " .. TableSerialization(targetlist, 0)						--make a string
local tgtFile = io.open("Active/targetlist.lua", "w")										--open targetlist file
tgtFile:write(tgt_str)																		--save new data
tgtFile:close()

local trigStr = "camp_triggers = " .. TableSerialization(camp_triggers, 0)
local trigFile = io.open("Active/camp_triggers.lua", "w")
trigFile:write(trigStr)
trigFile:close()