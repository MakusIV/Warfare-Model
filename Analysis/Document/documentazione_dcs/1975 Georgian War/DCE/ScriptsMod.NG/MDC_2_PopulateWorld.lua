--MiG-21 Dynamic Campaign: Guardians of the Caucasus by Marc "MBot" Marbot
--This file does the campaign bookkeeping (repair and reinforcements) at the start of a mission, spawns ground units and destroys killed static objects.
--v1.1 21.02.2015
------------------------------------------------------------------------------------------------------------------------------
-- =====================  Marco implementation ==================================
local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua")
-- NOTE MARCO: prova a caricarlo usando require(".. . .. . .. .ScriptsMod."versionPackageICM..".UTIL_Log.lua")
-- NOTE MARCO: https://forum.defold.com/t/including-a-lua-module-solved/2747/2
log.level = LOGGING_LEVEL
log.outfile = LOG_DIR .. "LOG_MDC_2_populateWorld." .. camp.mission .. ".log" 
local local_debug = true -- local debug   
log.info("Start")
-- =====================  End Marco implementation ==================================



do
-----------------------------------------------------------------------------------------------------------------
--Load campaign status
-----------------------------------------------------------------------------------------------------------------

	local LoadCampaignData = loadfile("MDC_campaign_results.lua")								--load campaign status file; if it doesn't exist loadfile returns nil

	if LoadCampaignData ~= nil then																--if results file exists (mission 2 or more)
		MDC_data = LoadCampaignData()															--overwrite MDC_data with campaign status from results file
	end																							--otherwise initial MDC_data for campaign start is used (mission 1)

if MDC_data.camp.outcome == "ongoing" then
-----------------------------------------------------------------------------------------------------------------
--Reset current mission losses stats
-----------------------------------------------------------------------------------------------------------------
	
	for n = 1, #MDC_data.oob.blue.squadron do													--resets the squadron stats counters for the current mission
		MDC_data.oob.blue.squadron[n].currentDestroyed = 0
		MDC_data.oob.blue.squadron[n].currentDamaged = 0
		MDC_data.oob.blue.squadron[n].currentRepaired = 0
		MDC_data.oob.blue.squadron[n].currentReplace = 0
		MDC_data.oob.blue.squadron[n].currentKills = 0
	end
	for n = 1, #MDC_data.oob.red.squadron do
		MDC_data.oob.red.squadron[n].currentDestroyed = 0
		MDC_data.oob.red.squadron[n].currentDamaged = 0
		MDC_data.oob.red.squadron[n].currentRepaired = 0
		MDC_data.oob.red.squadron[n].currentReplace = 0
		MDC_data.oob.red.squadron[n].currentKills = 0
	end
	
	for n = 1, #MDC_data.oob.red.SAM do
		MDC_data.oob.red.SAM[n].currentDestroyed = 0											--reset the SAM losses counters for current mission
		MDC_data.oob.red.SAM[n].currentKills = 0												--reset kill counter for current mission
	end
	
	for n = 1, #MDC_data.oob.red.infrastructure do												--reset the infrastructure losses counters for current mission
		MDC_data.oob.red.infrastructure[n].currentDestroyed = 0
	end
	
	for n = 1, #MDC_data.clientstats do
		MDC_data.clientstats[n].currentMissions = 0
		MDC_data.clientstats[n].currentKills = 0
		MDC_data.clientstats[n].currentCrash = 0
		MDC_data.clientstats[n].currentEject = 0
		MDC_data.clientstats[n].currentDead = 0
	end
	
-----------------------------------------------------------------------------------------------------------------
--Calculate campaign aircraft repairs/replacements
-----------------------------------------------------------------------------------------------------------------

	for n = 1, #MDC_data.oob.blue.squadron do
		--blue deactivate squadrons destroyed during last mission
		if MDC_data.oob.blue.squadron[n].squadronDestroyed == 1 then
			MDC_data.oob.blue.squadron[n].active = 0
		end
	
		--blue repair aicraft
		for r = MDC_data.oob.blue.squadron[n].damaged, 1, -1 do									--Go through all damaged aircraft
			local dice = math.random(1,5)														--20% chance per aircraft that it is repaired for next mission													
			if dice == 1 then
				MDC_data.oob.blue.squadron[n].damaged = MDC_data.oob.blue.squadron[n].damaged - 1
				MDC_data.oob.blue.squadron[n].ready = MDC_data.oob.blue.squadron[n].ready + 1
				MDC_data.oob.blue.squadron[n].currentRepaired = MDC_data.oob.blue.squadron[n].currentRepaired + 1
			end
		end
	end
		
	for n = 1, #MDC_data.oob.red.squadron do
		--red repair
		for r = MDC_data.oob.red.squadron[n].damaged, 1, -1 do									--Go through all damaged aircraft
			local dice = math.random(1,5)														--20% chance per aircraft that it is repaired for next mission													
			if dice == 1 then
				MDC_data.oob.red.squadron[n].damaged = MDC_data.oob.red.squadron[n].damaged - 1
				MDC_data.oob.red.squadron[n].ready = MDC_data.oob.red.squadron[n].ready + 1
				MDC_data.oob.red.squadron[n].currentRepaired = MDC_data.oob.red.squadron[n].currentRepaired + 1
			end
		end
		--red replacements
		if MDC_data.oob.red.squadron[n].ready < 24 then
			local dice = math.random(1,3)														--20% chance per mission that MiG-21 squadron receives reinforcement aircraft
			if dice == 1 then
				local repl = math.random(1,4)													--Between 1 and 4 aircraft
				MDC_data.oob.red.squadron[n].ready = MDC_data.oob.red.squadron[n].ready + repl
				MDC_data.oob.red.squadron[n].currentReplace = repl
			end
		end
	end
	
	--blue reinforcement squadrons
	local blue_losses = 0																	--When blue losses reach a certain level, reinforcement squadrons from the USA are activated
	for n = 1, #MDC_data.oob.blue.squadron do
		blue_losses = blue_losses + MDC_data.oob.blue.squadron[n].destroyed					--Count blue losses
	end
	blue_reinforce1 = false
	blue_reinforce2 = false
	local falcon_activate = math.random(50, 70)												--Sets the threshold of blue losses that releases the F-16 reinforcements
	local eagle_activate = math.random(90, 110)												--Sets the threshold of blue losses that releases the F-15 reinforcements
	if blue_losses > falcon_activate and MDC_data.oob.blue.squadron[9].active == 0 and MDC_data.oob.blue.squadron[9].ready + MDC_data.oob.blue.squadron[9].damaged > 2 then
		MDC_data.oob.blue.squadron[9].active = 1											--Activate F-16 unit
		blue_reinforce1 = true
	elseif blue_losses > eagle_activate and MDC_data.oob.blue.squadron[10].active == 0 and MDC_data.oob.blue.squadron[10].ready + MDC_data.oob.blue.squadron[10].damaged > 2 then
		MDC_data.oob.blue.squadron[10].active = 1											--Activate F-15 unit
		blue_reinforce2 = true
	end

-----------------------------------------------------------------------------------------------------------------
--Runway damage
-----------------------------------------------------------------------------------------------------------------
	
	MDC_data.oob.red.airbase.vaziani.currentDestroyed = 0
	MDC_data.oob.red.airbase.vaziani.currentRepair = 0
	
	if MDC_data.oob.red.airbase.vaziani.destroyed == 1 then
		if (MDC_data.camp.date.day * 24 + MDC_data.camp.time) > MDC_data.oob.red.airbase.vaziani.repairtime then
			MDC_data.oob.red.airbase.vaziani.destroyed = 0
			MDC_data.oob.red.airbase.vaziani.currentRepair = 1
		end
	end
	
	local function SpawnRepairTroops()														--Spawn repair troops
		local RepairGroup = {
			["visible"] = false,
			["taskSelected"] = true,
			["route"] = 
			{
				["spans"] = 
				{
				}, -- end of ["spans"]
				["points"] = 
				{
					[1] = 
					{
						["alt"] = 455,
						["type"] = "Turning Point",
						["ETA"] = 0,
						["alt_type"] = "BARO",
						["formation_template"] = "",
						["y"] = 903154.85714286,
						["x"] = -319083.42857143,
						["ETA_locked"] = true,
						["speed"] = 5.5555555555556,
						["action"] = "Off Road",
						["task"] = 
						{
							["id"] = "ComboTask",
							["params"] = 
							{
								["tasks"] = 
								{
								}, -- end of ["tasks"]
							}, -- end of ["params"]
						}, -- end of ["task"]
						["speed_locked"] = true,
					}, -- end of [1]
				}, -- end of ["points"]
			}, -- end of ["route"]
			["groupId"] = 2,
			["tasks"] = 
			{
			}, -- end of ["tasks"]
			["hidden"] = false,
			["units"] = 
			{
				[1] = 
				{
					["y"] = 903154.85714286,
					["type"] = "Ural-375",
					["name"] = "Repair #1",
					["unitId"] = 2,
					["heading"] = 2.4260076602721,
					["playerCanDrive"] = true,
					["skill"] = "Average",
					["x"] = -319083.42857143,
				}, -- end of [1]
				[2] = 
				{
					["y"] = 903165.14285714,
					["type"] = "Ural-375",
					["name"] = "Repair #2",
					["unitId"] = 3,
					["heading"] = 1.9722220547536,
					["playerCanDrive"] = true,
					["skill"] = "Average",
					["x"] = -319076.28571429,
				}, -- end of [2]
				[3] = 
				{
					["y"] = 903174.57142857,
					["type"] = "Ural-375",
					["name"] = "Repair #3",
					["unitId"] = 4,
					["heading"] = 2.4958208303519,
					["playerCanDrive"] = true,
					["skill"] = "Average",
					["x"] = -319070.28571429,
				}, -- end of [3]
				[4] = 
				{
					["y"] = 903171.42857143,
					["type"] = "GAZ-66",
					["name"] = "Repair #4",
					["unitId"] = 5,
					["heading"] = 0.05235987755983,
					["playerCanDrive"] = true,
					["skill"] = "Average",
					["x"] = -319050.85714286,
				}, -- end of [4]
				[5] = 
				{
					["y"] = 903124,
					["type"] = "Ural ATsP-6",
					["name"] = "Repair #5",
					["unitId"] = 6,
					["heading"] = 3.996803987067,
					["playerCanDrive"] = true,
					["skill"] = "Average",
					["x"] = -319070,
				}, -- end of [5]
				[6] = 
				{
					["y"] = 903152,
					["type"] = "UAZ-469",
					["name"] = "Repair #6",
					["unitId"] = 7,
					["heading"] = 5.6025068989018,
					["playerCanDrive"] = true,
					["skill"] = "Average",
					["x"] = -319047.71428571,
				}, -- end of [6]
				[7] = 
				{
					["y"] = 903170.57142857,
					["type"] = "Ural-4320 APA-5D",
					["name"] = "Repair #7",
					["unitId"] = 8,
					["heading"] = 0.78539816339745,
					["playerCanDrive"] = true,
					["skill"] = "Average",
					["x"] = -319043.14285714,
				}, -- end of [7]
				[8] = 
				{
					["y"] = 903156.57142856,
					["type"] = "Infantry AK",
					["name"] = "Repair #8",
					["unitId"] = 9,
					["heading"] = 5.6199601914217,
					["playerCanDrive"] = true,
					["skill"] = "Average",
					["x"] = -319077.71428572,
				}, -- end of [8]
				[9] = 
				{
					["y"] = 903167.71428571,
					["type"] = "Infantry AK",
					["name"] = "Repair #9",
					["unitId"] = 10,
					["heading"] = 5.6374134839417,
					["playerCanDrive"] = true,
					["skill"] = "Average",
					["x"] = -319071.14285715,
				}, -- end of [9]
				[10] = 
				{
					["y"] = 903160.85714285,
					["type"] = "Infantry AK",
					["name"] = "Repair #10",
					["unitId"] = 11,
					["heading"] = 3.6128315516283,
					["playerCanDrive"] = true,
					["skill"] = "Average",
					["x"] = -319050.85714286,
				}, -- end of [10]
			}, -- end of ["units"]
			["y"] = 903154.85714286,
			["x"] = -319083.42857143,
			["name"] = "RepairTeam",
			["start_time"] = 0,
			["task"] = "Ground Nothing",
		}
		coalition.addGroup(country.id.RUSSIA, Group.Category.GROUND, RepairGroup)
	end
	
	if MDC_data.oob.red.airbase.vaziani.destroyed == 1 then									--Damage runway
		local RunwayCrater1 = trigger.misc.getZone("RunwayCrater1")
		local RunwayCrater2 = trigger.misc.getZone("RunwayCrater2")
		local RunwayCrater3 = trigger.misc.getZone("RunwayCrater3")
		trigger.action.explosion(RunwayCrater1.point, 3000)
		trigger.action.explosion(RunwayCrater2.point, 3000)
		trigger.action.explosion(RunwayCrater3.point, 3000)
		timer.scheduleFunction(SpawnRepairTroops, nil, timer.getTime() + 1)
	end
	
-----------------------------------------------------------------------------------------------------------------
--Destroy the static objects that are dead
-----------------------------------------------------------------------------------------------------------------

	for n = 1, #MDC_data.deadStatics do
		trigger.action.explosion(MDC_data.deadStatics[n], 1000)
	end

-----------------------------------------------------------------------------------------------------------------
--Evaluate SAM threat
-----------------------------------------------------------------------------------------------------------------	

	samthreat = {}																				--Table storing the threat areas of known red SAMS (for use in mission generating)
	
	for n = 1, #MDC_data.oob.red.SAM do
		if MDC_data.oob.red.SAM[n].status == "operational" then
			local t = {
				x = MDC_data.oob.red.SAM[n].point.x,
				y = MDC_data.oob.red.SAM[n].point.y,
				range = 18000,
			}
			table.insert(samthreat, t)
		end
	end

-----------------------------------------------------------------------------------------------------------------
--Repair SAM radar (each mission there is a chance that a destroyed radar is repaired. This happens after generating the samthreat table, so blue is unaware of a repaired SAM site)
-----------------------------------------------------------------------------------------------------------------
	
	for n = 1, #MDC_data.oob.red.SAM do																--Go through all red SAM batteries
		if MDC_data.oob.red.SAM[n].status == "disabled" then										--Check for disabled batteries (destroyed batteries are ignored)
			local TR = 1																			--Assume tracking radar is intact until checked if dead below
			local SR = 1																			--Assuming search radar is intact until checked if dead below
			for u = 1, #MDC_data.oob.red.SAM[n].units do											--Go through all subunits of SAM battery
				if MDC_data.oob.red.SAM[n].units[u].unittable["type"] == "snr s-125 tr" then		--Check for TR
					if MDC_data.oob.red.SAM[n].units[u].dead == 1 then								--If TR is dead	
						local dice = math.random(1,10)												--roll dice to see  if it is repaired		
						if dice == 1 then															--10% chance to repair destroyed radar per mission
							MDC_data.oob.red.SAM[n].units[u].dead = 0								--Make TR alive
						else
							TR = 0																	--If TR is found dead and not repaired, set variable to 0
						end
					end
				elseif MDC_data.oob.red.SAM[n].units[u].unittable["type"] == "p-19 s-125 sr" then	--Same for SR as for TR above
					if MDC_data.oob.red.SAM[n].units[u].dead == 1 then
						local dice = math.random(1,10)
						if dice == 1 then															--10% chance to repair/replace destroyed radar per mission
							MDC_data.oob.red.SAM[n].units[u].dead = 0
						else
							SR = 0
						end
					end
				end
			end
			if TR == 1 and SR == 1 then																--If both TR and SR are ok (either repaired or not dead at all)
				MDC_data.oob.red.SAM[n].status = "operational (repaired)"							--Set status of battery to operational (repaired)
			end
		end
	end

-----------------------------------------------------------------------------------------------------------------
--Spawn SAMs
-----------------------------------------------------------------------------------------------------------------

	for n = 1, #MDC_data.oob.red.SAM do																--Go through all red SAM batteries
		local unitstable = {}
		for u = 1, #MDC_data.oob.red.SAM[n].units do												--Go through all subunits of SAM battery
			if MDC_data.oob.red.SAM[n].units[u].dead == 0 then										--Check if unit is still alive
				table.insert(unitstable, MDC_data.oob.red.SAM[n].units[u].unittable)				--If alive, inert to unitstable for spawning
			end
		end
		if #unitstable > 0 then
			local group = {
				["visible"] = false,
				["route"] = {
					["spans"] = {},
					["points"] = {
						[1] = {
							["alt"] = 0,
							["type"] = "Turning Point",
							["ETA"] = 0,
							["alt_type"] = "BARO",
							["formation_template"] = "",
							["y"] = MDC_data.oob.red.SAM[n].point.y,
							["x"] = MDC_data.oob.red.SAM[n].point.x,
							["ETA_locked"] = true,
							["speed"] = 0,
							["action"] = "Off Road",
							["task"] = {
								["id"] = "ComboTask",
								["params"] = {
									["tasks"] = {},
								},
							},
							["speed_locked"] = true,
						},
					},
				},
				["groupId"] = unitstable[1]["unitId"],													--Take unit id of first unit if group as group id
				["tasks"] = {},
				["hidden"] = false,
				["units"] = unitstable,
				["y"] = MDC_data.oob.red.SAM[n].point.y,
				["x"] = MDC_data.oob.red.SAM[n].point.x,
				["name"] = MDC_data.oob.red.SAM[n].name,
				["start_time"] = 0,
			}
			
			coalition.addGroup(country.id.RUSSIA, Group.Category.GROUND, group)							--Spawn SAM battery
		end
	end
	
-----------------------------------------------------------------------------------------------------------------
--Set initial campaign weather
-----------------------------------------------------------------------------------------------------------------

	function addWeatherZone()																		--function to add the next weather zone
		MDC_data.weather.zone[2] = {}
		MDC_data.weather.zone[2].endtime = MDC_data.weather.zone[1].endtime + math.random(48, 120)
		if MDC_data.weather.zone[1].type == "high" or MDC_data.weather.zone[1].type == "init" then
			local dice = math.random(1,8)
			if dice <= 2 then
				MDC_data.weather.zone[2].type = "high"
				MDC_data.weather.zone[2].temp = math.random(21, 28)
			elseif dice > 2 and dice <= 5 then
				MDC_data.weather.zone[2].type = "warm sector"
				MDC_data.weather.zone[2].temp = math.random(13, 20)
			elseif dice > 5 and dice <= 8 then
				MDC_data.weather.zone[2].type = "cold sector"
				MDC_data.weather.zone[2].temp = math.random(5, 12)
			end
		elseif MDC_data.weather.zone[1].type == "warm sector" then
			local dice = math.random(1,4)
			if dice == 1 then
				MDC_data.weather.zone[2].type = "high"
				MDC_data.weather.zone[2].temp = math.random(21, 28)
			else
				MDC_data.weather.zone[2].type = "cold sector"
				MDC_data.weather.zone[2].temp = math.random(5, 12)
			end
		elseif MDC_data.weather.zone[1].type == "cold sector" then
			local dice = math.random(1,4)
			if dice == 1 then
				MDC_data.weather.zone[2].type = "high"
				MDC_data.weather.zone[2].temp = math.random(21, 28)
			else
				MDC_data.weather.zone[2].type = "warm sector"
				MDC_data.weather.zone[2].temp = math.random(13, 20)
			end
		end
	end

	if MDC_data.camp.mission == 1 then																--if it is the first mission of the campaign, set the initial weather
		MDC_data.weather.zone = {
			[1] = {
				type = "init",																		--weather zone is a high pressure area
				endtime = 2,																		--time of end of zone (in hours after campaign start)
				temp = 15																			--temperature in zone
			}
		}
		addWeatherZone()																			--add next weather zone
	end

-----------------------------------------------------------------------------------------------------------------
else
	trigger.action.outText("Previous campaign concluded. Delete file 'MDC_campaign_results.lua' in DCS World folder to start a new campaign.", 999)
end
end