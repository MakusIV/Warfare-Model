--To create fresh status files when a new campaign is started
--Initiated by EventsTracker.lua running from within DCS if the mission was a first campaign mission
--Initated by BAT_FirstMission.lua if a campaign is reset manually
------------------------------------------------------------------------------------------------------- 
-- Miguel Fichier Revision  M45
-------------------------------------------------------------------------------------------------------


-- miguel21 modification M45 : compatible with 2.7.0
-- miguel21 modification M40 : Pedro Helicopter
-- Miguel21 modification M35 version ScriptsMod
-- miguel21 modification M34 custom FrequenceRadio

if not versionDCE then versionDCE = {} end
versionDCE["UTIL_ResetCampaign.lua"] = "1.4.4"

-- =====================  Marco implementation ==================================
local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua")
-- NOTE MARCO: prova a caricarlo usando require(".. . .. . .. .ScriptsMod."versionPackageICM..".UTIL_Log.lua")
-- NOTE MARCO: https://forum.defold.com/t/including-a-lua-module-solved/2747/2
log.level = LOGGING_LEVEL
log.outfile = LOG_DIR .. "LOG_UTIL_ResetCampaign." .. camp.mission .. ".log" 
local local_debug = true -- local debug   
log.info("Start")
-- =====================  End Marco implementation ==================================


----- random seed -----
math.randomseed(tonumber(tostring(os.time()):reverse():sub(1,6)))
math.random(); math.random(); math.random()


dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Functions.lua")

require("Init/radios_freq_compatible")																-- miguel21 modification M34 custom FrequenceRadio

if FirstMission then																				--if the script is called by BAT_FirstMission.lua, then FirstMission is true and camp_status is reset to init. When called by DEBRIEF_Master.lua, block is skipped and camp_camp status carried over in mission is used.
	require("Init/camp_init")
	local camp_str = "camp = " .. TableSerialization(camp, 0)										--make a string of campaign initial status table
	local campFile = io.open("Active/camp_status.lua", "w")											--open campaign status file
	camp.versionPackageICM = tostring(versionPackageICM)											-- Miguel21 modification M35 version ScriptsMod -- ajoute la version du script dans camp_status pour utilisation en fin de mission
	campFile:write(camp_str)																		--write initial status
	campFile:close()
end

require("Init/oob_air_init")																		--run initial oob air
for side,unit in pairs(oob_air) do																	----update oob_air to add roster and score table
	for n = 1, #unit do	
		unit[n].roster = {
			ready = unit[n].number,																	--number of airframes ready for operations
			lost = 0,																				--number of airframes lost
			damaged = 0																				--number of airframes damaged
		}
		unit[n].score = {
			kills_air = 0,																			--air kills
			kills_ground = 0,																		--ground kills
			kills_ship = 0																			--ship kills
		}
	end
end
local air_str = "oob_air = " .. TableSerialization(oob_air, 0)										--make a string
local airFile = io.open("Active/oob_air.lua", "w")													--open oob air file
airFile:write(air_str)																				--write initial data
airFile:close()

require("Init/targetlist_init")																		--run initial targetlist
local tgt_str = "targetlist = " .. TableSerialization(targetlist, 0)								--make a string
local tgtFile = io.open("Active/targetlist.lua", "w")												--open targetlist file
tgtFile:write(tgt_str)																				--write initial data
tgtFile:close()

local ground_str = "oob_ground = {}"
local groundFile = io.open("Active/oob_ground.lua", "w")											--open oob ground file
groundFile:write(ground_str)																		--write initial data
groundFile:close()

local scen_str = "oob_scen = {}"
local scenFile = io.open("Active/oob_scen.lua", "w")												--open clientstats file
scenFile:write(scen_str)																			--write initial file
scenFile:close()

local client_str = "clientstats = {}"
local clientFile = io.open("Active/clientstats.lua", "w")											--open clientstats file
clientFile:write(client_str)																		--write initial file
clientFile:close()

require("Init/camp_triggers_init")																	--open campaign trigger file
local trigStr = "camp_triggers = " .. TableSerialization(camp_triggers, 0)							--write
local trigFile = io.open("Active/camp_triggers.lua", "w")
trigFile:write(trigStr)
trigFile:close()


--create new oob_ground (requires extraction of data of init mission)
do
	--unpack template mission file
	local minizip = require('minizip')
	local zipFile = minizip.unzOpen("Init/base_mission.miz", 'rb')

	zipFile:unzLocateFile('mission')
	local misStr = zipFile:unzReadAllCurrentFile()
	local misStrFunc = loadstring(misStr)()

	zipFile:unzLocateFile('l10n/DEFAULT/dictionary')
	local dicStr = zipFile:unzReadAllCurrentFile()
	local dicStrFunc = loadstring(dicStr)()

	zipFile:unzClose()

	
	oob_ground = {}
	oob_ground["blue"] = deepcopy(mission.coalition.blue.country)											--copy mission data
	oob_ground["red"] = deepcopy(mission.coalition.red.country)												--copy mission data

	--store group and unit names in oob_ground instead of pointers to dict table
	for side_name, side in pairs(oob_ground) do																--iterate through sides
		for country_n, country in pairs(side) do															--iterate through countries
			if country.vehicle then																			--country has vehicles
				for g = 1, #country.vehicle.group do														--iterate through vehicle groups
					-- local groupname = dictionary[country.vehicle.group[g].name]								--find groupname in dictionary table			
					local groupname = country.vehicle.group[g].name											--M45	
					country.vehicle.group[g].name = groupname												--give group the actual groupname instead of the pointer to the dictionary table
					for u = 1, #country.vehicle.group[g].units do											--iterate through units
						-- local unitname = dictionary[country.vehicle.group[g].units[u].name]					--find unitname in dictionary table
						local unitname = country.vehicle.group[g].units[u].name								--M45	
						country.vehicle.group[g].units[u].name = unitname									--give unit the actual unitname instead of the pointer to the dictionary table
					end
				end
			end
			if country.ship then																			--country has ships
				for g = 1, #country.ship.group do															--iterate through ship groups
					-- local groupname = dictionary[country.ship.group[g].name]								--find groupname in dictionary table
					local groupname = country.ship.group[g].name								--M45
					country.ship.group[g].name = groupname													--give group the actual groupname instead of the pointer to the dictionary table
					for u = 1, #country.ship.group[g].units do												--iterate through units
						-- local unitname = dictionary[country.ship.group[g].units[u].name]					--find unitname in dictionary table
						local unitname = country.ship.group[g].units[u].name								--M45
						country.ship.group[g].units[u].name = unitname										--give unit the actual unitname instead of the pointer to the dictionary table
					end
				end
			end
			if country.static then																			--country has static objects
				for g = 1, #country.static.group do															--iterate through static groups
					-- local groupname = dictionary[country.static.group[g].name]								--find groupname in dictionary table			
					local groupname = country.static.group[g].name								--M45
					country.static.group[g].name = groupname												--give group the actual groupname instead of the pointer to the dictionary table
					for u = 1, #country.static.group[g].units do											--iterate through units
						-- local unitname = dictionary[country.static.group[g].units[u].name]					--find unitname in dictionary table
						local unitname = country.static.group[g].units[u].name								--M45
						country.static.group[g].units[u].name = unitname									--give unit the actual unitname instead of the pointer to the dictionary table
					end
				end
			end
		end
	
	-- miguel21 modification  M40 : Pedro Helicopter
	local function campTablePedro(groupCVN)
		for coal_name,coal in pairs(oob_ground) do
			for country_n,country in ipairs(coal) do
				if country.helicopter then
					for group_n,group in pairs(country.helicopter.group) do
						for w = 1, #group.units do																						--iterate through all group waypoints
							
							-- if string.find(dictionary[group.units[w].name], "Pedro_")  then											--find egress waypoint
								-- local ShipName = string.gsub(dictionary[group.units[w].name], "Pedro_", "")	
							--M45
							if string.find(group.units[w].name, "Pedro_")  then															--find egress waypoint
								local ShipName = string.gsub(group.units[w].name, "Pedro_", "")	
								if ShipName == groupCVN.units[1].name  then
									-- local PedroName = dictionary[group.units[w].name]												--find PedroName in dictionary table	
									local PedroName = group.units[w].name																--M45
									local bearing_from_leader_BaseMiss = GetHeading(groupCVN.units[1], group.units[w])					--unit bearing from leader
									local distance_from_leader = GetDistance(groupCVN.units[1], group.units[w])							--unit distance from leader

									if not camp["pedro"] then camp["pedro"] = {} end
									if not camp["pedro"][ShipName] then camp["pedro"][ShipName] = {} end
									camp["pedro"][ShipName].bearing_from_leader_BaseMiss = bearing_from_leader_BaseMiss					-- miguel21 modification M pedro
									camp["pedro"][ShipName].distance_from_leader = distance_from_leader									-- miguel21 modification M pedro
								end
							end
						end
					end
				end
			end
		-- _affiche(TabPedro, "TabPedro")
		end
	end
	
	for coal_name,coal in pairs(oob_ground) do												--go through sides(red/blue)	
		for country_n,country in ipairs(coal) do											--go through countries
			if country.ship then															--country has ships
				for group_n,group in ipairs(country.ship.group) do							--go through groups
					-- print("UTIL_RC group.units[1].type "..group.units[1].type)
					if string.find(group.units[1].type, "CVN") or string.find(group.units[1].type, "LHA") or string.find(group.units[1].type, "Stennis")   then 
						campTablePedro(group)
					end						
				end
			end
		end
	end
	
end

	
	--save oob_ground status file
	local ground_str = "oob_ground = " .. TableSerialization(oob_ground, 0)								--make a string
	local groundFile = io.open("Active/oob_ground.lua", "w")											--open oob ground file
	groundFile:write(ground_str)																		--write initial data
	groundFile:close()
end