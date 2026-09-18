--Moving ships and carriers as airbases
--Initiated by MAIN_NextMission.lua
------------------------------------------------------------------------------------------------------- 
------------------------------------------------------------------------------------------------------- 
-- Miguel Fichier Revision M45
------------------------------------------------------------------------------------------------------- 

-- miguel21 modification M45 : compatible with 2.7.0
-- miguel21 modification  M40 : Pedro Helicopter
-- Miguel21 modification M36.d	(d: add timer) MenuRadio request manual TurnIntoWind
-- Miguel21 modification M33.e.b 	Custom Briefing (e: CVN Manual Freq)
-- DC_NE_Debug02	maximizes the distance between two ship turns
-- DC_NE_Debug01	transforms an angle of more than 90� into 2 WPT of less than 90�
-- debugD staticPos
-- debugC Angle et Bearing des statics sur PA
-- Miguel21 modification M11 : Multiplayer


if not versionDCE then versionDCE = {} end
versionDCE["DC_NavalEnvironment.lua"] = "1.9.13"

-- =====================  Marco implementation ==================================
local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua")
-- NOTE MARCO: prova a caricarlo usando require(".. . .. . .. .ScriptsMod."versionPackageICM..".UTIL_Log.lua")
-- NOTE MARCO: https://forum.defold.com/t/including-a-lua-module-solved/2747/2
log.level = LOGGING_LEVEL
log.outfile = LOG_DIR .. "LOG_DC_NavalEnvironment." .. camp.mission .. ".log" 
local local_debug = true -- local debug   
log.info("Start")
-- =====================  End Marco implementation ==================================


function pedro(GroupName, groupCVN, routeCVN, delta_heading, PaHeading)				
	for coal_name,coal in pairs(oob_ground) do
		for country_n,country in ipairs(coal) do
			if country.helicopter then
				for group_n,group in pairs(country.helicopter.group) do
					for w = 1, #group.units do																		--iterate through all group waypoints
						-- if string.find(dictionary[group.units[w].name], "Pedro_")  then								--find egress waypoint
						if string.find(group.units[w].name, "Pedro_")  then
						
							-- local ShipName = string.gsub(dictionary[group.units[w].name], "Pedro_", "")
							local ShipName = string.gsub(group.units[w].name, "Pedro_", "")
							if ShipName == groupCVN.units[1].name  then
								-- local PedroName = dictionary[group.units[w].name]										--find PedroName in dictionary table									
								local PedroName = group.units[w].name
								
								local bearing_from_leader_BaseMiss = camp["pedro"][ShipName].bearing_from_leader_BaseMiss					-- miguel21 modification M pedro
								local distance_from_leader = camp["pedro"][ShipName].distance_from_leader									-- miguel21 modification M pedro
								
								local bearing_from_leader = bearing_from_leader_BaseMiss											--unit bearing from leader
								bearing_from_leader = bearing_from_leader + delta_heading											--update bearing from leader by change of group heading
								dx = math.cos(math.rad(bearing_from_leader)) * distance_from_leader	--x component from leader
								dy = math.sin(math.rad(bearing_from_leader)) * distance_from_leader	--y component from leader
								
								if not camp["pedro"] then camp["pedro"] = {} end
								if not camp["pedro"][ShipName] then camp["pedro"][ShipName] = {} end
								
								group.x = groupCVN.x + dx
								group.y = groupCVN.y + dy
								
								group.units[w].x = groupCVN.x + dx
								group.units[w].y = groupCVN.y + dy
								group.units[w].alt = 10
								group.units[w].speed = groupCVN.route.points[1].speed
								group.units[w].heading = PaHeading
								
									group.route.points[1] = {
										["type"] = "Turning Point",
										["alt"] = 10,
										["alt_type"] = "RADIO",
										["formation_template"] = "",
										["y"] = routeCVN[1].y + dy,
										["x"] = routeCVN[1].x + dx,
										["name"] = "",
										["ETA_locked"] = true,
										["ETA"] = 0,
										["speed_locked"] = true,
										["speed"] = groupCVN.route.points[1].speed,
										["action"] = "Turning Point",
										["task"] = {
											["id"] = "ComboTask",
											["params"] = {
												["tasks"] = {},
											},
										},
									}
								
								for n = 2, #group.route.points do												--go through route waypoints to assign
									group.route.points[n] = {
										["type"] = "Turning Point",
										["alt"] = 10,
										["alt_type"] = "RADIO",
										["formation_template"] = "",
										["y"] = routeCVN[2].y + dy,
										["x"] = routeCVN[2].x + dx,
										["name"] = "",
										["ETA_locked"] = false,
										["ETA"] = 0,
										["speed_locked"] = true,
										["speed"] = groupCVN.route.points[1].speed,
										["action"] = "Turning Point",
										["task"] = {
											["id"] = "ComboTask",
											["params"] = {
												["tasks"] = {},
											},
										},
									}
								end							
							end
						end
					end
				end
			end
		end
	end
end
--function to check if point is in polygon
function CheckPointInPoly(point, poly)
	local crossings = 0
	for n = 1, #poly - 1 do
		if (poly[n].y < point.y and poly[n + 1].y > point.y) or (poly[n].y > point.y and poly[n + 1].y < point.y) then
			local dx = poly[n + 1].x - poly[n].x
			local dy = poly[n + 1].y - poly[n].y
			local delta_point_y = point.y - poly[n].y
			local delta_point_x = dx / dy * delta_point_y
			if poly[n].x + delta_point_x > point.x then
				crossings = crossings + 1
			end
		end
	end
	if crossings % 2 ~= 0 then
		return true
	else
		return false
	end
end

--function to find random point in polygon
function RandomPointInPoly(poly)	
	local maxx = -9999999
	local minx = 9999999
	local maxy = -9999999
	local miny = 9999999
	for n = 1, #poly do
		if poly[n].x > maxx then
			maxx = poly[n].x
		end
		if poly[n].x < minx then
			minx = poly[n].x
		end
		if poly[n].y > maxy then
			maxy = poly[n].y
		end
		if poly[n].y < miny then
			miny = poly[n].y
		end
	end
	
	poly[#poly + 1] = poly[1]
	
	local newpoint = {}
	
	repeat
		newpoint = {
			x = math.random(minx, maxx),
			y = math.random(miny, maxy)
		}
	until CheckPointInPoly(newpoint, poly) == true
	
	return newpoint
end


--function to assign movement to ship groups
function ShipGroupMovement(GroupName, WPtable, CruiseSpeed, PatrolSpeed, StartTime)
	local MaxLoop = 2																		--Maximum Loop to maximizes the distance between two ship turns (recommended : 2)
	--search for ship group
	for coal_name,coal in pairs(oob_ground) do												--go through sides(red/blue)	
		for country_n,country in ipairs(coal) do											--go through countries
			if country.ship then															--country has ships
				for group_n,group in ipairs(country.ship.group) do							--go through groups
					if GroupName == group.name then											--ship group found
						--determine ship route
						local route = {}																		--local table to build group route
						for n = 1, #WPtable do																	--go through waypoints table passed as function argument
							if type(WPtable[n]) == "string" then												--WP is a single point marked by trigger zone
								if WPtable[n] == "" then														--if the WP string is empty, use the groups initial position
									route[n] = {
										x = group.x,
										y = group.y
									}
								else
									route[n] = Refpoint[WPtable[n]]												--store x-y coordnates of that trigger zone
								end
							elseif type(WPtable[n]) == "table" then												--WP is a polygon marked by multiple trigger zones
								if #WPtable[n] == 2 then														--poly has two points only
									local p1 = Refpoint[WPtable[n][1]]
									local p2 = Refpoint[WPtable[n][2]]
									local dx = p2.x - p1.x
									local dy = p2.y - p1.y
									local rand = math.random(0, 100)
									route[n] = {
										x = p1.x + dx * rand / 100,
										y = p1.y + dy * rand / 100
									}
								elseif #WPtable[n] > 2 then														--poly has more than two points
									local poly = {}																--table to store x-y coordinates of all points of polygon
									for w = 1, #WPtable[n] do
										poly[w] = Refpoint[WPtable[n][w]]
									end

									--get random point within polygon
									-- DC_NE_Debug02	maximizes the distance between two ship turns
									if n >= 2 then
										local distBtw  = {}
										local tabTestWPT = {}
										local maxDistId = 1 										
										for i = 1 , MaxLoop do											
											tabTestWPT[i] = RandomPointInPoly(poly)
											distBtw[i] =  GetDistance(route[n - 1], tabTestWPT[i])										
											if distBtw[i] > distBtw[maxDistId] then 
												maxDistId = i
											end
										end 
										route[n] = tabTestWPT[maxDistId]
									else
										route[n] = RandomPointInPoly(poly)
									end
								end
							end
							
							if #WPtable == 1 and PatrolSpeed and type(WPtable[n]) == "table" then				--patrol after route
								route[n].speed = PatrolSpeed													--set speed to patrol speed
							elseif #WPtable == 1 then
								route[n].speed = 0																--if there is only one waypoint, set speed to 0
							else
								route[n].speed = CruiseSpeed													--store waypoint speed
							end
							
							if n == 1 then
								route[n].time = StartTime														--for first waypoint store time the movement was assigned
							else																				--for subsequent waypoints
								route[n].time = route[n - 1].time + GetDistance(route[n - 1], route[n]) / CruiseSpeed	--calculate time at waypoint based on speed and distance from previous waypoint
							end
						end

						--ship position at current time
						local CurrentTime = (camp.day - 1) * 86400 + camp.time									--total time in seconds since campaign start
						for n = #route, 1, -1 do																--go through route from back to front
							if route[n].time < CurrentTime then													--check if waypoint time is earlier than current time
								if n == #route then																--waypoint is last waypoint
									if PatrolSpeed and type(WPtable[#WPtable]) == "table" then					--patrol after route
										route[n].speed = PatrolSpeed											--set speed to patrol speed
									else
										route[n].speed = 0														--set speed to zero
									end
									route[n].time = CurrentTime
								else
									local TimePassed = CurrentTime - route[n].time								--time since passed last waypoint
									local DistancePassed = TimePassed * route[n].speed							--distance covered since passed last waypoint
									local heading = GetHeading(route[n], route[n + 1])							--heading from last to next waypoint
									route[n].x = route[n].x + math.cos(math.rad(heading)) * DistancePassed		--update last waypoint to position at current time
									route[n].y = route[n].y + math.sin(math.rad(heading)) * DistancePassed		--update last waypoint to position at current time
								end
								for w = n - 1, 1, -1 do															--go throut all waypoints ahead of waypoint at current time
									table.remove(route, w)														--remove these waypoints
								end
								break	
							end
						end

						--patrol zone at end of route
						if PatrolSpeed and PatrolSpeed > 0 then													--if there is a patrol speed assigned, ship should patrol at end of route
							if type(WPtable[#WPtable]) == "table" then											--last WP must have multiple points (poly) in order to have a patrol zone
								while route[#route].time < CurrentTime + camp.mission_duration * 4 do			--repeat as long as last waypoint time is within twice the mission duration
									local nextWP																--next waypoint
									if #WPtable[#WPtable] == 2 then												--poly has two points only, patrol between these two points
										if #route % 2 == 0 then													--even
											nextWP = Refpoint[WPtable[#WPtable][1]]
										else																	--uneven
											nextWP = Refpoint[WPtable[#WPtable][2]]
										end
									elseif #WPtable[#WPtable] > 2 then											--poly has more than two points, patrol in random pattern within this polygon
										local poly = {}															--table to store x-y coordinates of all points of polygon
										for w = 1, #WPtable[#WPtable] do
											poly[w] = Refpoint[WPtable[#WPtable][w]]
										end
										-- nextWP = RandomPointInPoly(poly)										--for next waypoint get random point within polygon
										-- DC_NE_Debug02	maximizes the distance between two ship turns
										local distBtw  = {}
										local tabTestWPT = {}
										local maxDistId = 1 										
										for i = 1 , MaxLoop do											
											tabTestWPT[i] = RandomPointInPoly(poly)
											distBtw[i] =  GetDistance(route[#route], tabTestWPT[i])										
											if distBtw[i] > distBtw[maxDistId] then 
												maxDistId = i
											end
										end
										
										nextWP = tabTestWPT[maxDistId]
									end
									
									
									local nextTime = route[#route].time + GetDistance(route[#route], nextWP) / PatrolSpeed	--time at next waypoint
									
									--DC_NE_Debug01	transforms an angle of more than 90� into 2 WPT of less than 90�
									if #route > 1 then
										local h1 =GetHeading(route[#route-1],route[#route] )
										local h2 =GetHeading(route[#route],nextWP )
										local angle = GetDeltaHeading(h1, h2)
										local bearing = 0
										
										if angle > 90 or angle < -90 then
											if angle > 90 then bearing = h1 + 90
											elseif angle < -90 then bearing = h1 - 90 end
											-- intercalWP = GetOffsetPoint(point, bearing, distance)
											local intercalWP = GetOffsetPoint(route[#route], bearing, 3000)
											
											route[#route + 1] = {
												x = intercalWP.x,
												y = intercalWP.y,
												speed = PatrolSpeed,
												time =  nextTime
											}
										end
									end
									
									
									route[#route + 1] = {
										x = nextWP.x,
										y = nextWP.y,
										speed = PatrolSpeed,
										time =  nextTime
									}
									
									
								end
							end
						end
	
						--group initial position
						group.x = route[1].x
						group.y = route[1].y
						
						--units in group initial position and heading
						local delta_heading = 0												--change of heading between initial leader heading as per base_mission and actual heading at start of route
						local PaHeading = 0
						if route[2] then													--if there is more than one waypoint
							delta_heading = GetHeading(route[1], route[2]) - math.deg(group.units[1].heading)		--difference between heading as per base_mission and actual heading at start of route
							PaHeading = math.rad(GetHeading(route[1], route[2]))
						
						end
						local dx = 0
						local dy = 0
						
						for u = 2, #group.units do											--go through all units in group after the leader
							local bearing_from_leader = GetHeading(group.units[1], group.units[u])		--unit bearing from leader
							bearing_from_leader = bearing_from_leader + delta_heading					--update bearing from leader by change of group heading
							local distance_from_leader = GetDistance(group.units[1], group.units[u])	--unit distance from leader
							dx = math.cos(math.rad(bearing_from_leader)) * distance_from_leader	--x component from leader
							dy = math.sin(math.rad(bearing_from_leader)) * distance_from_leader	--y component from leader
							
							group.units[u].x = route[1].x + dx								--unit initial position relative to leader
							group.units[u].y = route[1].y + dy								--unit initial position relative to leader
							if route[2] then												--if there is more than one waypoint
								group.units[u].heading = PaHeading		--update initial unit heading
							end
						end
						
						
						pedro(GroupName, group, route, delta_heading, PaHeading)
						
						
						--check for linked static units	
						if country.static then												--side has static units	
							for u = 1, #group.units do										--go through all units in group
								for static_n, static in ipairs(country.static.group) do		--go through static groups								
									if static.route.points[1].linkUnit and static.route.points[1].linkUnit == group.units[u].unitId then	--static unit is linked to ship
										local bearing_from_leader = GetHeading(group.units[1], static)				--static bearing from leader
							
										bearing_from_leader = bearing_from_leader + delta_heading					--update bearing from leader by change of group heading
										local distance_from_leader = GetDistance(group.units[1], static)			--unit distance from leader
										local dx = math.cos(math.rad(bearing_from_leader)) * distance_from_leader	--x component from leader
										local dy = math.sin(math.rad(bearing_from_leader)) * distance_from_leader	--y component from leader
										static.x = route[1].x + dx													--new static position
										static.y = route[1].y + dy
										static.units[1].x = static.x
										static.units[1].y = static.y
										static.route.points[1].x = static.x
										static.route.points[1].y = static.y
										-- static.heading = static.units[1].heading + math.rad(delta_heading)			--new static heading
										-- static.units[1].offsets.angle = static.heading							-- l'angle offsets doit rester identique
										static.heading = static.units[1].offsets.angle + PaHeading					-- debugC Angle et Bearing des statics sur PA
										static.units[1].heading = static.heading
									end
								end
							end
						end
						
						group.units[1].x = route[1].x										--leader initial position
						group.units[1].y = route[1].y										--leader initial position
						if route[2] then													--if there is more than one waypoint
							group.units[1].heading = PaHeading			--update initial leader heading
						end
						
						--group route
						group.route.points[1].x = route[1].x
						group.route.points[1].y = route[1].y
						group.route.points[1].speed = route[1].speed
						for n = 2, #route do												--go through route waypoints to assign
							group.route.points[n] = {
								["type"] = "Turning Point",
								["alt"] = 0,
								["alt_type"] = "BARO",
								["formation_template"] = "",
								["y"] = route[n].y,
								["x"] = route[n].x,
								["name"] = "",
								["ETA_locked"] = false,
								["ETA"] = 0,
								["speed_locked"] = true,
								["speed"] = route[n].speed,
								["action"] = "Turning Point",
								["task"] = {
									["id"] = "ComboTask",
									["params"] = {
										["tasks"] = {},
									},
								},
							}
						end
						for n = #group.route.points, #route + 1, -1 do
							group.route.points[n] = nil										--clear the group's route points after the last waypoint (it might inherit from an old route)
						end
						
						
						
						-- pedro(GroupName, group, delta_heading, PaHeading)
						
						
						
						--airbase (carrier) position
						for basename,base in pairs(db_airbases) do							--go through airbases
							for u = 1, #group.units do										--go through units in group
								if base.unitname == group.units[u].name then				--if unit is an airbase (carrier)	
									base.x = group.units[u].x								--update airbase (carrier) position
									base.y = group.units[u].y								--update airbase (carrier) position
								end
							end
						end
					end
				end
			end
		end
	end
end


--go through ship missions and execute them
if camp.ShipMissions == nil then															--storage table for ship missions in camp doesn't exist yet
	camp.ShipMissions = {}																	--create it
end
for GroupName,entry in pairs(camp.ShipMissions) do
	ShipGroupMovement(GroupName, entry.WPtable, entry.CruiseSpeed, entry.PatrolSpeed, entry.StartTime)	--execute ship mission
end


--update aircraft carriers in db_airbase table and enable CarrierIntoWindScript for carrier

for basename,base in pairs(db_airbases) do															--iterate through airbases
	if base.unitname then																			--if airbase is a carrier, find the unit in the OOB Ground
		for coal_name,coal in pairs(oob_ground) do													--go through sides(red/blue)	
			for country_n,country in ipairs(coal) do												--go through countries
				if country.ship then																--country has ships
					for groupn,group in pairs(country.ship.group) do								--group table
						for unitn,unit in pairs(group.units) do										--units table
							if unit.name == base.unitname then										--respective unit found
								base.airdromeId = unit.unitId
								base.x = unit.x
								base.y = unit.y
								base.elevation = 0
								if not base.ATC_frequency then										--Miguel21 modification M33.e 	Custom Briefing (e: CVN Manual Freq)								
									base.ATC_frequency = tostring(unit.frequency / 1000000)			--si ATC_frequency non present dans db_airbases, on prend la freq de base_mission
								else									
									unit.frequency = base.ATC_frequency * 1000000									
								end
								--get carrier TACAN and ICLS
								for taskn,task in ipairs(group.route.points[1].task.params.tasks) do	--go through group tasks in first waypoint
									if task.params then
										if task.params.action then
											if task.params.action.id == "ActivateBeacon" then		--has beacon
												if task.params.action.params.channel and task.params.action.params.modeChannel and task.params.action.params.callsign then						--beacon is TACAN
													base.tacan = task.params.action.params.channel .. task.params.action.params.modeChannel .. " / " .. task.params.action.params.callsign		--store tacan channel and callsign in airbase entry
												end
											elseif task.params.action.id == "ActivateICLS" then		--has ICLS
												base.icls = task.params.action.params.channel		--store ICLS channel in airbase entry
											end
										end
									end
								end
								
								if string.lower(mission_ini.SC_CarrierIntoWind) == "auto" then											-- Miguel21 modification M36.d	(d: add timer) MenuRadio request manual TurnIntoWind
									--add mission trigger to add carrier to CarrierIntoWindScript (turn into wind during flight ops)
									local trig_n = #mission.trig.funcStartup + 1
									mission.trig.funcStartup[trig_n] = 'if mission.trig.conditions[' .. trig_n .. ']() then mission.trig.actions[' .. trig_n .. ']() end'
									mission.trig.flag[trig_n] = true
									mission.trig.conditions[trig_n] = "return(true)"
									mission.trig.actions[trig_n] = 'a_do_script(\\\"CarrierIntoWind(\\\\\\"' .. group.name .. '\\\\\\")\\\"); mission.trig.funcStartup[' .. trig_n .. ']=nil;'
									mission.trigrules[trig_n] = {
										['rules'] = {},
										['eventlist'] = '',
										['comment'] = 'Trigger ' .. trig_n,
										['predicate'] = 'triggerStart',
										['actions'] = {
											[1] = {
												["predicate"] = "a_do_script",
												["text"] = 'CarrierIntoWind(\"' .. group.name .. '\")',
												["KeyDict_text"] = 'CarrierIntoWind(\"' .. group.name .. '\")',
												["ai_task"] = 
												{
													[1] = "",
													[2] = "",
												},
											},
										},
									}
								end
							
							end
						end
					end
				end
			end
		end
	end
end


-- Miguel21 modification M11 : Multiplayer													-- pour donner de la place sur le PA, on supprime, � la demande, les statics pr�sent
function deleteStaticOnCVN(GroupName)

	--search for ship group
	for coal_name,coal in pairs(oob_ground) do												--go through sides(red/blue)	
		for country_n,country in ipairs(coal) do											--go through countries
			if country.ship then															--country has ships
				for group_n,group in ipairs(country.ship.group) do							--go through groups
					if GroupName == group.units[1].name then								--ship group found

						--check for linked static units	
						if country.static then												--side has static units	
							for static_n, _static in ipairs(country.static.group) do		--go through static groups								
								if _static.route.points[1].linkUnit and _static.route.points[1].linkUnit == group.units[1].unitId then	--static unit is linked to ship
									for group_n, _group in ipairs(mission.coalition[coal_name].country[country_n].static.group) do

										if _group.units[1].unitId == _static.units[1].unitId then
											val = table.remove(mission.coalition[coal_name].country[country_n].static.group, group_n)
										end
									
									end

								end
							end
						end
					end
				end
			end
		end
	end
end