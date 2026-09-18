--To add unused ready aircraft as uncontrolled static aircraft to mission
--Initiated by Main_NextMission.lua
------------------------------------------------------------------------------------------------------- 

------------------------------------------------------------------------------------------------------- 
-- Miguel Fichier Revision M43 +DC_SA_correction01.b
------------------------------------------------------------------------------------------------------- 

-- DC_SA_correction01.b Static disparaissent au bout de 3mn (b: nb de static en fonction de la place restante)
-- miguel21 modification M43 assignation des numeros de parking du type C08 

-- =====================  Marco implementation ==================================
local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua")
-- NOTE MARCO: prova a caricarlo usando require(".. . .. . .. .ScriptsMod."versionPackageICM..".UTIL_Log.lua")
-- NOTE MARCO: https://forum.defold.com/t/including-a-lua-module-solved/2747/2
log.level = LOGGING_LEVEL
log.outfile = LOG_DIR .. "LOG_DC_StaticAircraft." .. camp.mission .. ".log" 
local local_debug = true -- local debug   
log.info("Start")
-- =====================  End Marco implementation ==================================

--Count all aircraft assigned in ATO
local count = {}

for side_name, side in pairs(ATO) do										--Iterate through sides in ATO
	for pack_n, pack in pairs(side) do										--Iterate through packages
		for role_name, role in pairs(pack) do								--Iterate throug roles
			for flight_n, flight in pairs(role) do							--Iterate through flights
				if count[flight.name] then									--Unit already has a count entry
					count[flight.name] = count[flight.name] + flight.number	--Sum number
				else														--Unit has no count entry
					count[flight.name] = flight.number						--Create count entry
				end
			end
		end
	end
end


--Function to add a number of uncontrolled aircraft per unit to mission
local function AddUncontrolledAircraft(side, unit, number, parkingId, base)
			
	-- print("DcSA Passe base "..tostring(base).." : ") 
	for u = 1, number do													--Repeat for each unasisgned aircraft
		
		local group = {														--Define group to spawn
			['frequency'] = 124,
			['taskSelected'] = true,
			['modulation'] = 0,
			['groupId'] = GenerateID(),
			['tasks'] = {},
			['route'] = {
				['points'] = {
					[1] = {
						["name"] = "Static",
						["alt"] = 0,		--1490
						["type"] = "TakeOffParking",
						["action"] = "From Parking Area",
						["airdromeId"] = db_airbases[unit.base].airdromeId,
						["alt_type"] = "BARO",
						["formation_template"] = "",
						["properties"] = 
						{
							["vnav"] = 1,
							["scale"] = 0,
							["angle"] = 0,
							["vangle"] = 0,
							["steer"] = 2,
						},
						["ETA"] = 0,
						["y"] = db_airbases[unit.base].y,
						["x"] = db_airbases[unit.base].x,
						["speed"] = 0,														--138.88888888889,
						["ETA_locked"] = true,
						["task"] = 
						{
							["id"] = "ComboTask",
							["params"] = 
							{
								["tasks"] = {}
							},
						},
						["speed_locked"] = true,
					},
				},
			},
			['hidden'] = true,
			['units'] = {
				[1] = {
					["alt"] = 0,														--1490
					["heading"] = 0,
					["callsign"] = "123",
					["psi"] = 0,
					["livery_id"] = unit.livery,
					["type"] = unit.type,
					["y"] = db_airbases[unit.base].y,
					["x"] = db_airbases[unit.base].x,
					["name"] = "Static " .. unit.name .. " " .. u .. "-1",
					["payload"] = {
						["pylons"] = {},
						["fuel"] = 0,
						["flare"] = 0,
						["chaff"] = 0,
						["gun"] = 0,
					},
					["AddPropAircraft"] = 
						{
					},
					["speed"] = 0,															--138.88888888889
					["unitId"] = GenerateID(),
					["alt_type"] = "BARO",
					["skill"] = unit.skill,
					["hardpoint_racks"] = true,
					--["parking"] = 1,
					
				},
			},
			['radioSet'] = false,
			['name'] = "Static " .. unit.name .. " " .. u,
			['communication'] = true,
			['x'] = db_airbases[unit.base].x,
			['y'] = db_airbases[unit.base].y,
			['start_time'] = 1,																--0
			['task'] = "Nothing",															--intercept
			-- ['uncontrolled'] = true,
		}

		if parkingId then					
			local findParkId = GetParkingId( parkingId, base)						
			if findParkId then
			-- print("DcSA Passe parking_id "..tostring(findParkId).." "..unit.type)
				group.units[1]["parking_id"] = findParkId
			end	
		else
			-- print("DcSA Passe StaticAircrast ".." "..unit.type)
		end
		
		if unit.sidenumber and unit.sidenumber[1] and unit.sidenumber[2] then											--squadron has sidenumbers defined
			group.units[1]["onboard_num"] = GetSidenumber(unit.name, unit.sidenumber[1], unit.sidenumber[2])			--get new sidenumber
		else																											--squadron has no sidenumbers defined
			group.units[1]["onboard_num"] = "0" .. math.random(1, 99)													--us a random number
		end
		
		--multiple skins for aircraft
		if type(group.units[1]["livery_id"]) == "table" then															--if skin is a table
			group.units[1]["livery_id"] = group.units[1]["livery_id"][math.random(1, #group.units[1]["livery_id"])]		--chose a random skin from table
		end
		
		--add group to mission
		for c = 1, #mission.coalition[side].country do
			if mission.coalition[side].country[c].name == unit.country then
				if unit.helicopter ~= true then
					if mission.coalition[side].country[c].plane == nil then
						mission.coalition[side].country[c].plane = {
							group = {}
						}
					end
					table.insert(mission.coalition[side].country[c].plane.group, group)
				else
					if mission.coalition[side].country[c].helicopter == nil then
						mission.coalition[side].country[c].helicopter = {
							group = {}
						}
					end
					table.insert(mission.coalition[side].country[c].helicopter.group, group)
				end
			end
		end
	end
end


--Count unassigned aircraft and add them to mission as idle at airbase
for side,unit in pairs(oob_air) do												--Iterate through sides in oob_air
	for n = 1, #unit do															--iterate through units
		if unit[n].inactive ~= true then										--unit is active
			if db_airbases[unit[n].base] and db_airbases[unit[n].base].airdromeId then		--check if airbase exists and has an id (aircraft at "virtual" airfields, such as reserves, are not placed in mission as static aircraft)
				if db_airbases[unit[n].base].unitname == nil then				--airbases with unitnames (carriers) do not get static aircraft
					local unassigned											--number of unassigned aircraft
					for unit_name, assigned in pairs(count) do					--Iterate through count table
						if unit[n].name == unit_name then						--Unit found
							unassigned = unit[n].roster.ready - assigned		--Number of unassigned aircaft is ready aircraft - assigned aircraft
							break												--End count iteration
						end
					end
					if unassigned == nil then									--If unassigned is still nil (unit has no aircraft in ATO)
						unassigned = unit[n].roster.ready						--All ready aircraft are unassigned
					end
					if unassigned > 12 then										--if more than 12
						unassigned = 12 + math.floor((unassigned - 12) * 0.5)	--amount above 12 is halfed
					end
					
					
					--TabLPark[flight[f].base][timmingParking]
					-- cherche le nombre maximum d avion en meme tps sur la base
					-- pour trouver le nb de place disponible pour les avions static
					if db_airbases[unit[n].base].LimitedParkNb and TabLPark[unit[n].base] then
						local nb = 0
						-- print("DcSA unit[n].base "..unit[n].base)
						for mn , value in pairs(TabLPark[unit[n].base]) do
							-- print("DcSA mn "..mn)
							-- _affiche(value, "value")
							if type(value) == "number" and value > nb then
								nb = value
							end					
						end
						
						local NbParkPossible  = db_airbases[unit[n].base].LimitedParkNb - nb
						if unassigned > NbParkPossible then
							unassigned = NbParkPossible
						end
					end
					
					AddUncontrolledAircraft(side, unit[n], unassigned, unit[n].parking_id, unit[n].base)			--Add uncontrolled aircraft for this unit
				end
			end
		end
	end
end


--remove static aircraft that are linked to a carrier that is dead/not in mission
for side_name,side in pairs(mission.coalition) do											--side table(red/blue)
	for country_n,country in pairs(side.country) do											--country table (number array)
		if country.static then																--if country has static objects
			for n = #country.static.group, 1, -1 do											--iterate through static groups backwards
				local linkUnit = country.static.group[n].route.points[1].linkUnit			--ID of unit to which static is linked
				if linkUnit then															--if static is linked to a unit
					for _c,c in pairs(side.country) do										--country table (number array)
						if c.ship then														--country has ships
							for _g,g in pairs(c.ship.group) do								--groups table (number array)
								for _u,u in pairs(g.units) do								--units table (number array)
									if u.unitId == linkUnit then							--ship that static is linked to is found
										if (g.probability and g.probability < 1) or u.dead then		--ship is dead or not in mission
											table.remove(country.static.group, group_n)		--remove group of static unit from mission
										end
										break
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