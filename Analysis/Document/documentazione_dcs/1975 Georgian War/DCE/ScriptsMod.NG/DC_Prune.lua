--
-- Auteur: Tomsk
-- https://forums.eagle.ru/showpost.php?p=3525106&postcount=753
-- Pruning can improve the performance of the mission by removing units that are very unlikely to participate in it.
--
-- In particular this varies depending on.
--		- Whether the unit is an anti-air unit (of various types) or not.
--		- How close any flight passes to the unit when that flight is flying along the waypoints.
--		- Whether that unit is close to any 'Target' or 'Attack' waypoint 
--

-------------------------------------------------------------------------------------------------------
-- Miguel Fichier Revision debug05
-------------------------------------------------------------------------------------------------------
-- Miguel21 debug05 prune category tag
-- Miguel21 debug04.b : Static Plane Bug + Heli
-- Miguel21 M23 : Désactive USN Mod
-- Miguel21 M21 : Ajout Convoy (interdit à Prune de les Pruner..)
-- Miguel21 debug03 : Package avion supprimé par bug
-- Miguel21 Z02.a : DontPrunSAM et prend en compte la position des intercepteur qui n'ont qu'un seul waypoint
-- Miguel21 M16.d : SpawnAir, & insert pos far target 
-- Miguel21 debug02 : FARP bug
-- Miguel21 debug01 : helicopter bug
-------------------------------------------------------------------------------------------------------

-- =====================  Marco implementation ==================================
local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua")
-- NOTE MARCO: prova a caricarlo usando require(".. . .. . .. .ScriptsMod."versionPackageICM..".UTIL_Log.lua")
-- NOTE MARCO: https://forum.defold.com/t/including-a-lua-module-solved/2747/2
log.level = LOGGING_LEVEL
log.outfile = LOG_DIR .. "LOG_DC_Prune." .. camp.mission .. ".log" 
local local_debug = true -- local debug   
log.info("Start")
-- =====================  End Marco implementation ==================================


cibleTrouve = {}

local pruneAggressiveness = mission_ini.PruneAggressiveness

local pruneStatic = mission_ini.PruneStatic

-- work out which side has 'players'
local function findPlayerSide()
	for side,units in pairs(oob_air) do
		for ui,unit in pairs(units) do
			if unit.player then return side end 
		end 
	end 
	return nil
end

local playerSide = findPlayerSide()


-- Miguel21 M16 : SpawnAir, & insert pos far target 
-- array de tous les groups vehicle pour rechercher ceux qui seront des targets designés afin de les protéger de Prune
local function GroundGroupId()
	local allGroundGroupId = {}
	for side, ncountry in pairs(oob_ground ) do
		for nc, country in pairs(ncountry ) do
			if country["vehicle"] then
				for vi,vehicle in pairs(country) do
					if 	type(vehicle) == "table" then									
						for gi,ngroup in pairs(vehicle["group"]) do
							if ngroup["groupId"] then
								allGroundGroupId[ngroup["groupId"]] = {}
								allGroundGroupId[ngroup["groupId"]].x = ngroup["x"]
								allGroundGroupId[ngroup["groupId"]].y = ngroup["y"]
								allGroundGroupId[ngroup["groupId"]].name = ngroup["name"]
							end
						end 
					end
				end
			end
		end
	end 
	return allGroundGroupId
end

-- given a unit return the anti-air type of an unit: SHORT, MEDIUM, LONG, IR, AAA or NONE.
local function unitAntiAirType(unit)
	-- List reduced from https://forums.eagle.ru/showthread.php?t=174971
	local types = { 
		["2S6 Tunguska"]="MEDIUM",	-- 12km
		["Tor 9A331"]="MEDIUM",		-- 12km
		["Strela-10M3"]="IR",		-- 5km
		["Strela-1 9P31"]="IR",		-- 5km
		["SA-8 Osa LD 9T217"]="SHORT",	-- 7km
		["Gepard"]="AAA",				-- 5km
		["SA-18 Igla manpad"]="IR",		-- 5km
		["Igla manpad INS"]="IR",		-- 5km
		["SA-18 Igla-S manpad"]="IR",	-- 5km
		["Vulcan"]="AAA",				-- 2.5km
		["M48 Chaparral"]="IR",			-- 9km
		["M6 Linebacker"]="IR",  		-- 8km
		["M1097 Avenger"]="IR",			-- 7km
		["Stinger manpad GRG"]="IR",	-- 8km
		["Stinger manpad dsr"]="IR",	-- 8km
		["Stinger manpad"]="IR",		-- 8km
		["ZSU-23-4 Shilka"]="SHORT",			-- 2.5km
		["ZU-23 Emplacement Closed"]="AAA",		-- 2.0km
		["ZU-23 Emplacement"]="AAA",			-- 2.0km
		["ZU-23 Closed Insurgent"]="AAA",		-- 2.0km
		["Ural-375 ZU-23 Insurgent"]="AAA",		-- 2.0km
		["ZU-23 Insurgent"]="AAA",				-- 2.0km
		["Ural-375 ZU-23"]="AAA",				-- 2.0km
		["1L13 EWR"]="LONG",					-- EWR: 200km
		["Kub 1S91 str"]="MEDIUM",				-- 25.0 km
		["S-300PS 40B6M tr"]="LONG",			-- 100km
		["S-300PS 40B6MD sr"]="LONG",			-- 100km
		["55G6 EWR"]="LONG",					-- 200km
		["S-300PS 64H6E sr"]="LONG",			-- 100km
		["SA-11 Buk SR 9S18M1"]="LONG",			-- 100km
		["Dog Ear radar"]="SHORT",				-- 5km
		["Hawk tr"]="LONG",						-- 50km
		["Hawk sr"]="LONG",						-- 50km
		["Patriot str"]="LONG",					-- 150km
		["Hawk cwar"]="LONG",					-- 50km
		["p-19 s-125 sr"]="MEDIUM",				-- 35km
		["Roland Radar"]="SHORT",				-- 8km
		["snr s-125 tr"]="MEDIUM",				-- 35km
	}
	local got = types[unit.type]
	return (got or "NONE")
end

local function stringStarts(str, start)
	str = string.lower(str)
	start = string.lower(start)
	if str == nil then
		return false
	else
	-- print(" str: "..str.." |start:"..start.." ||subLen: "..string.sub(str,1,string.len(start)))
		return string.sub(str,1,string.len(start)) == start
	end
end

-- iterate through all consecutive pairs of waypoints
function waypointPairs(wps, f)
	local wi = 1
	while (wps[wi]) do
		local wp = wps[wi]
		local nextWi = wi + 1 
		local found = false 
		while (wps[nextWi]) do
			local np = wps[nextWi]
			if (np.x ~= wp.x) or (np.y ~= wp.y) then
				found = true
				wi = nextWi
				f(wp, np)
				break
			end				
			nextWi = nextWi + 1
		end
	 -- Miguel21 Z02 : SAM ajoute un waypoint sur les intercepteurs (qui n'ont qu'un seul waypoint) pour éviter de supprimer les unité proche
-- TODO fonction a déplacer dans ATO_FlightPlan
		if wi <= 1 and wps[1].name == "Intercept" then
			np = wps[1]
			np.x = wp.x + 5000
			np.y = wp.y + 5000
			found = true
			f(wp, np)
			-- print("PruneIntercepteurIntercept"..np.x)
			break
		end
		if not found then return end
	end 
end 

-- decides whether the given ground unit (which is on side 'unitSide') should be kept or not
local function keepGroundUnit(unit, unitSide, allWaypoints, allGroundGroupId, category)
	if pruneStatic and (category == 'plane' or category == 'helicopter') and stringStarts(unit.name, 'Static') then
		-- print("DC_P_T  Prune static planes "..unit.name )
		return false -- Prune static planes
	elseif  (category == 'plane' or category == 'helicopter') and not string.find(unit.name,"Static") then
		-- print("DC_P_T  keep plane and helicopter: "..unit.name )
		return true -- keep plane and helicopter
	elseif  stringStarts(unit.name,"Pack") and not string.find(unit.name,"Static") then
		-- print("DC_P_T  Pack keep plane and helicopter: "..unit.name )
		return true -- keep plane and helicopter
	elseif  string.find(string.lower(unit.name),"convo") then
		-- print("DC_P_ keep Convoy")
		return true -- keep Convoy
	end 
	local aaType = unitAntiAirType(unit)
	
	-- Miguel21 debug02 : FARP bug
	if unit.type == "FARP" then
		return true
	end
	-- Miguel21 Z02 : SAM
	if stringStarts(unit.name, 'DontPrune') and mission_ini.ForcedPruneSam == false then
	-- print("DC_P_ DontPrune")
		return true
	end
	if  (unit.type == "DECKCREW" or  stringStarts(unit.type,"MD_3") )and not mission_ini.Keep_USNdeckCrew then
		-- print("DC_P_PruneUSnCrew "..unit.type)
		return false -- prune USN crew -- si Keep_USNdeckCrew est en False dans conf_mod -- Miguel Modisication M23
	end

	-- decides which aircraft waypoints we want to check against, we really don't care if enemy planes fly over enemy defenses.
	local otherSide = (unitSide == "blue") and "red" or "blue"
	local checkSides = unitSide == playerSide and { unitSide, otherSide } or { otherSide }	-- if unit is same side as player check both, else just check enemy
	
	-- for other types of unit it depends on distance to waypoints 
	local closestWP     = 100000000
	local closestTarget = 100000000	
	for csi,side in pairs(checkSides) do 
		for wpi,wps in pairs(allWaypoints[side]) do 
			waypointPairs(wps, function (wp1, wp2) 
				-- calculate the distance between the unit and the closest point along the two waypoints		
				local dist = GetTangentDistance(wp1, wp2, unit)
				closestWP = math.min(closestWP, dist)		
				 
				-- if this is a 'target' waypoint then record that distance as well
				if wp1.name == 'Target' or wp1.name == 'Attack' then
					local dist = GetDistance(wp1, unit)
					closestTarget = math.min(closestTarget, dist)				
				end 
				if wp2.name == 'Target' or wp2.name == 'Attack' then 
					local dist = GetDistance(wp2, unit)
					closestTarget = math.min(closestTarget, dist)				
				end 
				
				-- les cibles identifiées par idgroup seront Gardées (Keep) 
				if wp1.task.id == "ComboTask" then
					if wp1.task.params.tasks then
						for ti=1 , #wp1.task.params.tasks do
							if wp1.task.params.tasks[ti] then
								if wp1.task.params.tasks[ti].id == 'AttackGroup' then
									if wp1.task.params.tasks[ti].params then
										if wp1.task.params.tasks[ti].params.groupId then
											targetGroupId =  wp1.task.params.tasks[ti].params.groupId
											if allGroundGroupId[targetGroupId] then
		-- print("DC_P_P Keep cibles identifiées par idgroup seront Gardées "..targetGroupId.." Unit "..unit.name)	
												cibleTrouve[targetGroupId] = allGroundGroupId[targetGroupId].name
												local dist = GetDistance(allGroundGroupId[targetGroupId], unit)
												closestTarget = math.min(closestTarget, dist)
											end
										end
									end
								end
							end
						end
					end
				end
			end)
		end
	end
	
	-- depending on the closest distance (and unit type) decide if we want to keep this unit
	local range = { 
		["LONG"] = 400000.0, ["MEDIUM"] = 80000, ["SHORT"] = 30000, 
		["AAA"] = 15000.0, ["IR"] = 20000.0, ["NONE"] = 10000.0 
	}
	local rfactor = math.min(math.max(pruneAggressiveness, 0), 3)
	local keep = closestWP*rfactor <= range[aaType] or closestTarget*rfactor <= 25000
	
	-- print("DC_P_P Unit " .. unit.type .. " unit.name" .. unit.name .. " closestWP " .. closestWP .. " closestTarget " .. 
			-- closestTarget .. " Keep = " .. (keep and "KEEP" or "PRUNE"))
	
	-- if  unit.category and  keep == false then
		-- print("DC_P_P UnitCat " .. unit.category.." " ..unit.type .. " " .. unit.name .. " closestWP " .. closestWP .. " closestTarget " .. 
				-- closestTarget .. " Keep = " .. (keep and "KEEP" or "PRUNE"))
	-- elseif  keep == false then
		-- print("DC_P_P Unit "..unit.type .. " " .. unit.name .. " closestWP " .. closestWP .. " closestTarget " .. 
				-- closestTarget .. " Keep = " .. (keep and "KEEP" or "PRUNE"))
	-- end
	return keep
end 

-- decides whether the given air unit should be kept or not
local function keepAirUnit(unit, side)
-- print( tostring( not pruneStatic or not string.find(unit.name, 'Static')))
	return not pruneStatic or not string.find(unit.name, 'Static')
end

-- Get all the waypoints for all (flying) units for all countries
local function getAllWaypoints()
	local allWaypoints = {}
	for si, side in pairs(mission.coalition) do 
		local sideWaypoints = {}
		for ci, country in pairs(side.country) do
			if country.plane then 
				for gi, grp in pairs(country.plane.group) do
					table.insert(sideWaypoints, grp.route.points)				
				end
			end 
			if country.helicopter then
--				for gi, grp in pairs(country.plane.helicopter) do
				for gi, grp in pairs(country.helicopter.group) do       -- Miguel21 debug01 : helicopter bug
					table.insert(sideWaypoints, grp.route.points)				
				end
			end 
		end
		allWaypoints[si] = sideWaypoints
	end
	return allWaypoints
end

-- Get all the ground units in the mission that could be pruned
local function pruneUnits(groundFun, airFun)
	local totalPruned = 0
	local totalKept = 0

	-- prune all the units in a given group (e.g. 'vehicle' or 'static')
	local pruneInGroup = function (container, side, fun, category)
		if container and container.group and container then
			local newGroup = {}
			for gi, grp in pairs(container.group) do 			
				if grp.units then 	
					-- either the whole group survives (if any unit in it survives), or the whole group is removed.
					local saved = false
					for ui, unit in pairs(grp.units) do	
						-- unit['category'] = category
						saved = saved or fun(unit, side, category)
					end
					if not saved then
						totalPruned = totalPruned + #grp.units
						for ui, unit in pairs(grp.units) do
	-- print("DC_P_P elague: "..unit.name)
						end
					else 
						totalKept = totalKept + #grp.units
						table.insert(newGroup, grp)
					end
				end
			end
			container.group = newGroup
		end 
	end 

-- Miguel21 M16.d :
-- Obligé de passer les Aéronefs static avec "groudFun" pour les enlever en fonction de la distance.
	for si, side in pairs(mission.coalition) do 
		for ci, country in pairs(side.country) do
			pruneInGroup(country.vehicle, si, groundFun, "vehicle")			
			pruneInGroup(country.plane, si, groundFun, "plane")			-- plus efficace que pruneInGroup(country.plane, si, airFun, "Planes")
			pruneInGroup(country.static, si, groundFun, "static")
			pruneInGroup(country.helicopter, si, groundFun, "helicopter")
		end
	end	
	print("Pruned " .. totalPruned .. ", kept " .. totalKept)
end

local function prune()

	local allGroundGroupId = GroundGroupId()
	-- get the waypoints for all air units in the mission.
	local allWaypoints = getAllWaypoints()
	
	-- prune the required ground and air units 
	pruneUnits(
		function (unit, side, category) return keepGroundUnit(unit, side, allWaypoints, allGroundGroupId, category) end
		,
		function (unit, side, category) return keepAirUnit(unit, side, category) end 
	)
end

function NbPlane()
	local Count = {
					NbPlane = 0,
					NbPlaneStatic = 0,
					
					NbHeli = 0,
					NbHeliStatic = 0,
				}

	for side, _coalition in pairs(mission.coalition) do
		for ci, country in pairs(mission.coalition[side].country) do 	
			if country.plane then
				if country.plane.group then
					for gi = 1, #country.plane.group do	
						for ui = 1, #country.plane.group[gi].units do
							local testName = string.lower(country.plane.group[gi].units[ui].name)
							if  string.find(testName,"static")  then
								Count.NbPlaneStatic = Count.NbPlaneStatic +  1
							else  
								Count.NbPlane = Count.NbPlane +  1
							end
						end
					end
				end
			end
		end
	end
	
	for side, _coalition in pairs(mission.coalition) do
		for ci, country in pairs(mission.coalition[side].country) do 
			if country.helicopter then
				if country.helicopter.group then
					for gi = 1, #country.helicopter.group do	
						for ui = 1, #country.helicopter.group[gi].units do
							local testName = string.lower(country.helicopter.group[gi].units[ui].name)
							if  string.find(testName,"static")  then
								Count.NbHeliStatic = Count.NbHeliStatic +  1
							else  
								Count.NbHeli = Count.NbHeli +  1
							end
						end
					end
				end
			end
		end
	end
	
	return Count
end


-- Tomsk modification V9 Integration de  Prune Script
if mission_ini.PruneScript == true then 

	_Count = NbPlane()
	print ("Number of plane Before Prune: ".._Count.NbPlane.." PlaneStatic: ".._Count.NbPlaneStatic.." Nb Helic: ".._Count.NbHeli.." HeliStatic ".._Count.NbHeliStatic)

	prune()
	
	
	_Count = NbPlane()
	print ("Number of plane After Prune: ".._Count.NbPlane.." PlaneStatic: ".._Count.NbPlaneStatic.." Nb Helic: ".._Count.NbHeli.." HeliStatic ".._Count.NbHeliStatic)
	
	
end



if cibleTrouve then
	-- print("(TEST DC_Prune) Numero des cibles trouvées et normalement préservées de Prune: ")
	for i, cible in pairs(cibleTrouve) do 
		if cible  then
			-- print(i.." DC_P_P cibleTrouve Keep "..cible)
		end
	end
end
