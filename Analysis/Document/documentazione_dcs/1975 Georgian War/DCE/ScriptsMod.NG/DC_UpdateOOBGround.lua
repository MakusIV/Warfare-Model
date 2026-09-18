--To put vehicles and ships from ground OOB into next mission
--Initiated by MAIN_NextMission.lua
-------------------------------------------------------------------------------------------------------

-------------------------------------------------------------------------------------------------------

if not versionDCE then 
	versionDCE = {} 
end

               -- VERSION --

versionDCE["DC_UpdateOOBGround.lua"] = "OB.1.0.0"

--------------------------------------------------------------------------------------------------------- Old_Boy rev. OB1: implements logging code and little(very) optimization
-- Old_Boy rev. OB.1.0.0: implements logging code and (very) little optimization

-- =====================  Marco implementation ==================================
local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua")
-- NOTE MARCO: prova a caricarlo usando require(".. . .. . .. .ScriptsMod."versionPackageICM..".UTIL_Log.lua")
-- NOTE MARCO: https://forum.defold.com/t/including-a-lua-module-solved/2747/2
log.level = LOGGING_LEVEL
log.outfile = LOG_DIR .. "LOG_DC_UpdateOOBGround." .. camp.mission .. ".log" 
local local_debug = true -- local debug   
log.info("Start")
-- =====================  End Marco implementation ==================================


local function createStaticDeadGroup(k1, country, group_type)
	local nameFunction = " function createStaticDeadGroup(k1, country, group_type): "    
	log.debug("Start " .. nameFunction)
	-- country = v2, group_type = ship or vehicle
	local country_asset -- country.vehicle or country.ship

	if group_type == "ship" then
		country_asset = country.ship

	elseif group_type == "vehicle" then
		country_asset = country.vehicle
		
	else
		log.warning("anomaly ....")
	end

	log.trace(k1 .. ".country: " .. country.name .. " has " .. group_type .. ". Search into groups")
	local n = 1
	local nEnd = #country_asset.group
	
	repeat																					--groups table (number array)
		local m = 1
		local mEnd = #country_asset.group[n].units
		
		repeat																				--units table (number array)	
			
			if country_asset.group[n].units[m].dead then
				log.trace(group_type .. ".group[" .. n .. "].units[" .. m .. "] is dead.")

				if group_type == "vehicle" then
					if country.static == nil then													--country table has no other static objects
						log.trace("country table has not static objects. Create static.group for this group")
						v2.static = {															--create static objects table
							group = {}															--create group subtable
						}
					end
					
					local dead_static_group = {													--define dead static group to replace dead unit 
						["heading"] = country_asset.group[n].units[m].heading,						--set static group heading according to dead unit
						["route"] = {
							["points"] = 
							{
								[1] = 
								{
									["alt"] = 0,
									["type"] = "",
									["name"] = "",
									["y"] = country_asset.group[n].units[m].y,
									["speed"] = 0,
									["x"] = country_asset.group[n].units[m].x,
									["formation_template"] = "",
									["action"] = "",
								},
							},
						},
						["groupId"] = GenerateID(),
						["hidden"] = true,
						["units"] = {
							[1] = {
								["category"] = "Unarmed",
								["canCargo"] = false,
								["type"] = country_asset.group[n].units[m].type,
								["unitId"] = GenerateID(),
								["y"] = country_asset.group[n].units[m].y,
								["x"] = country_asset.group[n].units[m].x,
								["name"] = country_asset.group[n].units[m].name,
								["heading"] = country_asset.group[n].units[m].heading,
							},
						},
						["y"] = country_asset.group[n].units[m].y,
						["x"] = country_asset.group[n].units[m].x,
						["name"] = "Dead Static " .. country_asset.group[n].units[m].name,
						["dead"] = true,
					}
					table.insert(country.static.group, dead_static_group)							--add group to static table
					log.trace("created dead_static_group and add in static.group table")
				end
				
				if #country_asset.group[n].units == 1 then										--if group has only one unit
					table.remove(country_asset.group, n)											--remove group of dead unit from group table
					n = n - 1
					nEnd = nEnd - 1
					log.trace("group has only one unit, remove group of dead unit from group table, n = " .. n .. ", mEnd = " .. nEnd)
				
				else
					table.remove(country_asset.group[n].units, m)									--remove dead unit from units table

					if group_type == "vehicle" then
						country_asset.group[n].route.points[1].x = country_asset.group[n].units[1].x	--update group position to position of first units
						country_asset.group[n].route.points[1].y = country_asset.group[n].units[1].y	--update group position to position of first units						
					end
					m = m - 1
					mEnd = mEnd - 1
					log.trace("group have units, remove dead unit from units table and update group position to position of first units x =" .. country_asset.group[n].units[1].x .. ", y = " .. country_asset.group[n].units[1].y .. ", m = " .. m .. ", mEnd = " .. mEnd)
				end
			end
			m = m + 1
		until m > mEnd
		n = n + 1
	until n > nEnd
	log.debug("End " .. nameFunction)
end




--M33.f frequence des F.ARP selon db_airbase
--Iterate group's item of oob_ground for search FARP items (heliport) and assign ATC Frequency
log.info("Iterate group's item of oob_ground for search FARP items (heliport) and assign ATC Frequency")

for coal_name,coal in pairs(oob_ground) do												--go through sides(red/blue)	

	for country_n,country in ipairs(coal) do											--go through countries

		if country.static then															--country has ships

			for group_n,group in ipairs(country.static.group) do						--go through groups

				for n = 1, #group.units do												--ship group found
					
					if group.units[n].type == 'FARP' then
					end
					
					if group.units[n].type == 'FARP' and db_airbases[group.units[n].name] and db_airbases[group.units[n].name].ATC_frequency then
						group.units[n].heliport_frequency = db_airbases[group.units[n].name].ATC_frequency
						log.trace("group.units[".. n .. "]: " .. group.units[n].name .. " is FARP type and exist in db_airbases. Assign group.units[n].heliport_frequency = " .. group.units[n].heliport_frequency)
					end
				end
			end
		end
	end
end


mission.coalition.blue.country = deepcopy(oob_ground.blue)											--copy blue oob into mission
mission.coalition.red.country = deepcopy(oob_ground.red)											--copy red oob into mission

--iterate through all vehicles and ships to remove those marked as dead during previous debriefings (static objects need not be removed, as these are spawned in a destroyed state)
log.info("iterate through all vehicles and ships to remove those marked as dead during previous debriefings (static objects need not be removed, as these are spawned in a destroyed state)")
for k1,v1 in pairs(mission.coalition) do															--side table(red/blue)	

	for k2,v2 in pairs(v1.country) do																--country table (number array)

		if v2.vehicle then																			--if country has vehicles
			createStaticDeadGroup(k1, v2, "vehicle")
			--[[log.trace(k1 .. "country: " .. v2.name .. " has vehicle. Search into groups")
			local n = 1
			local nEnd = #v2.vehicle.group
			
			repeat																					--groups table (number array)
				local m = 1
				local mEnd = #v2.vehicle.group[n].units
			
				repeat																				--units table (number array)
			
					if v2.vehicle.group[n].units[m].dead then
						log.trace("vehicle.group[" .. n .. "].units[" .. m .. "] is dead.")
						--dead units are replaced by dead static objects
			
						if v2.static == nil then													--country table has no other static objects
							log.trace("country table has not static objects. Create static.group for this group")
							v2.static = {															--create static objects table
								group = {}															--create group subtable
							}
						end
						
						local dead_static_group = {													--define dead static group to replace dead unit 
							["heading"] = v2.vehicle.group[n].units[m].heading,						--set static group heading according to dead unit
							["route"] = {
								["points"] = 
								{
									[1] = 
									{
										["alt"] = 0,
										["type"] = "",
										["name"] = "",
										["y"] = v2.vehicle.group[n].units[m].y,
										["speed"] = 0,
										["x"] = v2.vehicle.group[n].units[m].x,
										["formation_template"] = "",
										["action"] = "",
									},
								},
							},
							["groupId"] = GenerateID(),
							["hidden"] = true,
							["units"] = {
								[1] = {
									["category"] = "Unarmed",
									["canCargo"] = false,
									["type"] = v2.vehicle.group[n].units[m].type,
									["unitId"] = GenerateID(),
									["y"] = v2.vehicle.group[n].units[m].y,
									["x"] = v2.vehicle.group[n].units[m].x,
									["name"] = v2.vehicle.group[n].units[m].name,
									["heading"] = v2.vehicle.group[n].units[m].heading,
								},
							},
							["y"] = v2.vehicle.group[n].units[m].y,
							["x"] = v2.vehicle.group[n].units[m].x,
							["name"] = "Dead Static " .. v2.vehicle.group[n].units[m].name,
							["dead"] = true,
						}
						table.insert(v2.static.group, dead_static_group)							--add group to static table
						log.trace("created dead_static_group and add in static.group table")
						
						--remove dead unit from vehicle table
						if #v2.vehicle.group[n].units == 1 then										--if group has only one unit
							table.remove(v2.vehicle.group, n)										--remove group of dead unit from group table
							n = n - 1
							nEnd = nEnd - 1
							log.trace("group has only one unit, remove group of dead unit from group table, n = " .. n .. ", mEnd = " .. nEnd)
						else
							table.remove(v2.vehicle.group[n].units, m)								--remove dead unit from units table
							v2.vehicle.group[n].route.points[1].x = v2.vehicle.group[n].units[1].x	--update group position to position of first units
							v2.vehicle.group[n].route.points[1].y = v2.vehicle.group[n].units[1].y	--update group position to position of first units
							m = m - 1
							mEnd = mEnd - 1
							log.trace("group have units, remove dead unit from units table and update group position to position of first units x =" .. v2.vehicle.group[n].units[1].x .. ", y = " .. v2.vehicle.group[n].units[1].y .. ", m = " .. m .. ", mEnd = " .. mEnd)
						end
					end
					m = m + 1
				until m > mEnd
				n = n + 1
			until n > nEnd]]
		end

		if v2.ship then																				--if country has ships			
			createStaticDeadGroup(k1, v2, "ship")
			--[[log.trace(k1 .. "country: " .. v2.name .. " has ship. Search into groups")
			local n = 1
			local nEnd = #v2.ship.group
			
			repeat																					--groups table (number array)
				local m = 1
				local mEnd = #v2.ship.group[n].units
				
				repeat																				--units table (number array)	
					
					if v2.ship.group[n].units[m].dead then
						log.trace("ship.group[" .. n .. "].units[" .. m .. "] is dead.")
						
						if #v2.ship.group[n].units == 1 then										--if group has only one unit
							table.remove(v2.ship.group, n)											--remove group of dead unit from group table
							n = n - 1
							nEnd = nEnd - 1
							log.trace("group has only one unit, remove group of dead unit from group table, n = " .. n .. ", mEnd = " .. nEnd)
						else
							table.remove(v2.ship.group[n].units, m)									--remove dead unit from units table
							m = m - 1
							mEnd = mEnd - 1
							log.trace("group have units, remove dead unit from units table and update group position to position of first units x =" .. v2.vehicle.group[n].units[1].x .. ", y = " .. v2.vehicle.group[n].units[1].y .. ", m = " .. m .. ", mEnd = " .. mEnd)
						end
					end
					m = m + 1
				until m > mEnd
				n = n + 1
			until n > nEnd]]
		end
	end
end




--disable carriers as air bases if they are damaged, destroyed or do not have a 100% probability
log.debug("disable carriers as air bases if they are damaged, destroyed or do not have a 100% probability")
for basename,base in pairs(db_airbases) do															--iterate through airbases

	if base.unitname then																			--if airbase is a carrier, find the unit in the OOB Ground

		for coal_name,coal in pairs(oob_ground) do													--go through sides(red/blue)	

			for country_n,country in ipairs(coal) do												--go through countries

				if country.ship then																--country has ships

					for groupn,group in pairs(country.ship.group) do								--group table

						for unitn,unit in pairs(group.units) do										--units table

							if unit.name == base.unitname then										--respective unit found
								log.trace("ship unit.name: " .. unit.name .. " exist in db_airbase -> ship unit is carrier")

								if unit.dead or (camp.ShipHealth and camp.ShipHealth[unit.name] and camp.ShipHealth[unit.name] < 66) or (group.probability and group.probability < 1) then	 --unit is dead, damaged or its group has a probability that is not 100%
									base.x = nil													--remove base coordinates to prevent sortie generation from this abse
									base.y = nil
									log.trace("ship unit is dead, damaged or its group has a probability = " .. group.probability .. " that is not 100%, remove base coordinates to prevent sortie generation from this abse")
								end
							end
						end
					end
				end
			end
		end
	end
end
