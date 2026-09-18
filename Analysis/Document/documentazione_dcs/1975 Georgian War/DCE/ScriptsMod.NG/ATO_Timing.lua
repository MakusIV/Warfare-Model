--To define Time on target for all packages and ETA for all aircraft waypoints
--Initiated by Main_NextMission.lua
------------------------------------------------------------------------------------------------------- 
-- Miguel Fichier Revision  ATO_T_Debug03
------------------------------------------------------------------------------------------------------- 

-- ATO_T_Debug03 speed trop faible pour les escort : = flight[f].loadout.vCruise / 4 * 3
-- ATO_T_Debug02 Spawn before Departure 
-- ATO_T_Debug01 vCruise by default 
-- Miguel21 modification M17.b Option F-14B
-- Miguel21 modification M11.j : Multiplayer
-- Miguel21 modification M06.e : helicoptere playable

-- =====================  Marco implementation ==================================
local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua")
-- NOTE MARCO: prova a caricarlo usando require(".. . .. . .. .ScriptsMod."versionPackageICM..".UTIL_Log.lua")
-- NOTE MARCO: https://forum.defold.com/t/including-a-lua-module-solved/2747/2
log.level = LOGGING_LEVEL
log.outfile = LOG_DIR .. "LOG_ATO_Timing." .. camp.mission .. ".log" 
local local_debug = true -- local debug   
log.info("Start")
-- =====================  End Marco implementation ==================================


local TOTtable = {}																								--table to store target TOT

for side, pack in pairs(ATO) do	

	local pack_n = {}																							--table to store all package numbers. Numbe sequence needs to be adjusted to do timingh for player package ahead of all other packages
	local tabPackPrioritaire = 1																				--table pour prioriser les packages clients
	local tabPackStudied = {}
	
	for n = 1, #pack do
		if PlayerFlight and side == camp.player.side and n == camp.player.pack_n then							--if p is the player package number
			table.insert(pack_n, 1, n)																			--insert at start of table
			tabPackStudied[n] = true
		elseif PlayerFlight and camp.client then
			for i=2, Multi.NbGroup do	
				if side == camp.client[i].side and n == camp.client[i].pack_n and not tabPackStudied[n] then
					table.insert(pack_n, tabPackPrioritaire+1, n)
					tabPackPrioritaire = tabPackPrioritaire+1																			--insert at the end of table
					tabPackStudied[n] = true
				elseif  not tabPackStudied[n] then																								--if p is not th eplayer package number
					table.insert(pack_n, n)																				--insert at the end of table
					tabPackStudied[n] = true
				end
			end	
		
		elseif  not tabPackStudied[n] then																								--if p is not th eplayer package number
			table.insert(pack_n, n)																				--insert at the end of table
			tabPackStudied[n] = true
		end
	end

	-- for n = 1, #pack do
		-- if PlayerFlight and camp.client then																				-- Miguel21 modification M11.j : Multiplayer
			-- for i=2, Multi.NbGroup do	
				-- if side == camp.client[i].side and n == camp.client[i].pack_n and not tabPackStudied[n] then
					-- table.insert(pack_n, tabPackPrioritaire+1, n)
					-- tabPackPrioritaire = tabPackPrioritaire+1																			--insert at the end of table
					-- tabPackStudied[n] = true
				-- end
			-- end																				--insert at the end of table
		-- end
	-- end
-- _affiche(pack_n, "ATO_T pack_nB")

	for k,p in ipairs(pack_n) do																				--iterate through package numbers (player package always comes first)
		
		local player_start_shift = 0																			--waypoint time shift to start player at mission start
	
		local tot 																								--set time on target in seconds after mission start
		
		if pack[p].main[1].tot then																				--package already has a tot (target package for player intercept)
			tot = pack[p].main[1].tot																			--set package tot
			TOTtable[pack[p].main[1].target_name] = tot															--store TOT for target
		elseif TOTtable[pack[p].main[1].target_name] then														--target already has a TOT assigned from another package
			if pack[p].main[1].loadout.standoff == nil or pack[p].main[1].loadout.standoff <= 15000 then		--if package overflies the target, add 15 seconds tot interval between multi-packages
				TOTtable[pack[p].main[1].target_name] = TOTtable[pack[p].main[1].target_name] + 15 
			end
			tot = TOTtable[pack[p].main[1].target_name]															--give this package the same TOT
			local earliest = pack[p].main[1].tot_from + 600														--earliest TOT is 10 minutes after tot_from to make sure it is at least 10 minutes after mission start
			if pack[p].main[1].loadout.standoff then															--for strikes 
				earliest = earliest + pack[p].main[1].loadout.standoff / pack[p].main[1].loadout.vAttack		--earliest TOT to make sure that aircraft always spawn 10 minutes ahead of IP at mission start
			end
			local latest = pack[p].main[1].tot_to																--latest TOT
			if tot < earliest then																				--if this tot is too early for this package
				tot = earliest																					--give package the earliest possible tot
			elseif tot > latest	then																			--if this tot is too late for this package
				tot = pack[p].latest																			--give package the latest possible tot
			end
			if earliest > latest then																			--if there is no valid TOT
				tot = earliest
			end
		else
			local earliest = pack[p].main[1].tot_from + 600														--earliest TOT is 10 minutes after tot_from to make sure it is at least 10 minutes after mission start
			if pack[p].main[1].loadout.standoff then															--for strikes 
				earliest = earliest + pack[p].main[1].loadout.standoff / pack[p].main[1].loadout.vAttack		--earliest TOT to make sure that aircraft always spawn 10 minutes ahead of IP at mission start
			end
			local latest = pack[p].main[1].tot_to																--latest TOT
			if earliest > latest then																			--if there is no valid TOT
				tot = earliest
			else
				tot = math.random(earliest, latest)																--set random tot
			end
			TOTtable[pack[p].main[1].target_name] = tot															--store TOT for target
		end
		
		local vCruise = pack[p].main[1].loadout.vCruise															--set package cruise speed
		local vAttack = pack[p].main[1].loadout.vAttack															--set package attack speed
		
		local target_wp = 1																						--local variable to store the target waypoint number
		local partial_station = 0																				--local variable to hold time that an orbiting flight is already on station at mission start
		
		for role,flight in pairs(pack[p]) do																	--iterate through roles in package (main, SEAD, escort)
			
			--flight route offset within package (lateral and ETA)
			for f = 1, #flight do																				--iterate through flights in roles	
				flight[f].eta_offset = 0																		--ETA delay in seconds for longitudinal flight separation
				if flight[f].task ~= "CAP" and flight[f].task ~= "AWACS" and flight[f].task ~= "Refueling" and flight[f].task ~= "Intercept" and flight[f].task ~= "Transport" then	--not any of these tasks, as these do not operate with simultaneous flights on the same route
					
					local tSeparation = 8																		--basic separation between flights in seconds at cruise speed
					local separation = tSeparation * vCruise													--basic separation between flights in meters
					local offset																				--lateral offset of flight route in meters from route of lead flight
					
					if role == "main" then
						if math.floor((f - 1) / 3) == (f - 1) / 3 then											--flight 1, 4, 7...
							offset = 0
							flight[f].eta_offset = tSeparation * ((f - 1) / 3 * 2)								--ETA delay in seconds for longitudinal flight separation
						elseif math.floor((f - 2) / 3) == (f - 2) / 3 then										--flight 2, 5, 8...
							offset = separation																	--to the right side of lead flight
							flight[f].eta_offset = tSeparation * ((f - 2) / 3 * 2 + 1)							--ETA delay in seconds for longitudinal flight separation
						elseif math.floor((f - 3) / 3) == (f - 3) / 3 then										--flight 3, 6, 9...
							offset = separation * -1															--to the left side of lead flight
							flight[f].eta_offset = tSeparation * ((f - 3) / 3 * 2 + 1)							--ETA delay in seconds for longitudinal flight separation
						end
					elseif role == "SEAD" then
						offset = separation / 2																	--all SEAD routes are offset slightly to the right
						if math.floor((f - 1) / 3) == (f - 1) / 3 then											--flight 1, 4, 7...
							flight[f].eta_offset = -60 + tSeparation * ((f - 1) / 3)							--ETA delay in seconds for longitudinal flight separation
						elseif math.floor((f - 2) / 3) == (f - 2) / 3 then										--flight 2, 5, 8...
							offset = offset - separation														--to the left side of lead flight
							flight[f].eta_offset = -60 + tSeparation * ((f - 2) / 3)							--ETA delay in seconds for longitudinal flight separation
						elseif math.floor((f - 3) / 3) == (f - 3) / 3 then										--flight 3, 6, 9...
							offset = offset + separation														--to the right side of lead flight
							flight[f].eta_offset = -60 + tSeparation * ((f - 3) / 3)							--ETA delay in seconds for longitudinal flight separation
						end
					elseif role == "Escort" then
						offset = separation / -2																--all escort routes are offset slightly to the left
						if math.floor((f - 1) / 4) == (f - 1) / 4 then											--flight 1, 5, 9...
							flight[f].eta_offset = -90 + tSeparation * ((f - 1) / 4)							--ETA delay in seconds for longitudinal flight separation
						elseif math.floor((f - 2) / 4) == (f - 2) / 4 then										--flight 2, 6, 10...
							offset = offset + separation * (3 + ((f - 2) / 4))									--to the right side of lead flight
							flight[f].eta_offset = tSeparation * ((f - 2) / 4)									--ETA delay in seconds for longitudinal flight separation
						elseif math.floor((f - 3) / 4) == (f - 3) / 4 then										--flight 3, 7, 11...
							offset = offset - separation * (3 + ((f - 3) / 4))									--to the left side of lead flight
							flight[f].eta_offset = tSeparation * ((f - 3) / 4)									--ETA delay in seconds for longitudinal flight separation
						elseif math.floor((f - 4) / 4) == (f - 4) / 4 then										--flight 4, 8, 12...
							flight[f].eta_offset = -240 + tSeparation * ((f - 4) / 4)							--ETA delay in seconds for longitudinal flight separation
						end
					elseif role == "Escort Jammer" then
						offset = 0
						flight[f].eta_offset = tSeparation														--escort jammer flies in the center of strike package
					elseif role == "Flare Illumination" then
						offset = 0
						flight[f].eta_offset = -120																--flare illumination flies 2 minutes ahead
					elseif role == "Laser Illumination" then
						offset = 0
						flight[f].eta_offset = tSeparation * 3													--laser illumination flies slightly behind strike package
					end
					
					for w = 3, #flight[f].route - 1 do															--iterate through all waypoints that require lateral offset (taxi, departure and landing WP exluded)			
						if flight[f].route[w].id ~= "Target" then												--Target WP does not need lateral offset
							local inbound_heading = GetHeading(pack[p].main[1].route[w - 1], pack[p].main[1].route[w])		--inbound heading to WP of lead flight
							local outbound_heading = GetHeading(pack[p].main[1].route[w], pack[p].main[1].route[w + 1])		--outbound heading from WP of lead flight
							local delta_heading = GetDeltaHeading(inbound_heading, outbound_heading)			--amount of heading change at WP
							
							if delta_heading < 66 and delta_heading > -66 then									--if heading change is small, flights stay at the present side of lead flight (check turn)
								local alpha = inbound_heading + 90 + (delta_heading / 2)
								local dist = offset / math.cos(math.rad(delta_heading / 2))
								local offset_WP = GetOffsetPoint(flight[f].route[w], alpha, dist)
								flight[f].route[w].x = offset_WP.x
								flight[f].route[w].y = offset_WP.y
							else																				--if heading change is big, flights switch side from lead flight (tactical turn and cross turn)
								local alpha = outbound_heading - 90 + ((180 - delta_heading) / 2)
								local dist = offset / math.cos(math.rad((180 - delta_heading) / 2))
								local offset_WP = GetOffsetPoint(flight[f].route[w], alpha, dist)
								flight[f].route[w].x = offset_WP.x
								flight[f].route[w].y = offset_WP.y
								offset = offset * -1															--switch side
							end
						end
					end
				end
			end
			
			for f = 1, #flight do																					--iterate through flights in roles
			
				--flight TOT for packages continously covering a station
				if flight[f].task == "CAP" or flight[f].task == "AWACS" or flight[f].task == "Refueling" then		--flight is part of a package that continously covers a station
					local available_station_coverage = #flight * flight[f].loadout.tStation							--total time that station can be covered
					local required_station_coverage = flight[f].tot_to - flight[f].tot_from	+ flight[f].loadout.tStation	--total time that station must be covered
					local station_uncovered = required_station_coverage - available_station_coverage				--total time that station is uncovered
					
					if station_uncovered <= 0 then																	--station can be covered continously
						if f == 1 then																				--for first flight in package
							partial_station = math.random(0, flight[f].loadout.tStation)													--set time that first flight was already on station at mission start
							if camp.time + flight[f].tot_from - partial_station < camp.dawn and flight[f].loadout.night == false then		--if before dawn and not night capable
								partial_station = camp.time - camp.dawn																		--make partial_station to match dawn
							elseif camp.time + flight[f].tot_from - partial_station < camp.dusk and flight[f].loadout.day == false then		--if before dusk and not day capable
								partial_station = camp.time - camp.dusk																		--make partial_station to match dusk
							end
						end
						
						tot = flight[f].tot_from + (f - 1) * flight[f].loadout.tStation + 1							--flight TOT (+1 second so that first flight spanwns at mission start a little ahead of station)
						tot = tot - partial_station																	--remove time that the first flight was already on station at mission start
					else																							--station cannot be covered continously
						if f == 1 then																				--for first flight in package
							local from = flight[f].tot_from - flight[f].loadout.tStation							--first possible station start
							local to = flight[f].tot_to / #flight - flight[f].loadout.tStation						--last possible station start
							if from <= to then
								tot = math.random(from, to) + 1
							else
								tot = from + 1
							end
							if tot < 0 then																			--if tot is before mission start
								partial_station = tot * -1															--time on station until mission start
							else																					--tot after mission start
								partial_station = 0																	--time already on station is zero
							end
						else
							tot = tot + flight[f].tot_to / #flight
						end
					end
				end
				
				--flight TOT for interceptors
				if flight[f].task == "Intercept" then
					flight[f].route[1].eta = 0									--interceptors only have one waypoint and start at mission start (but idle until activated by EWR)
				end
				
				--find target WP
				local eta = tot + flight[f].eta_offset							--Make ETA at target the TOT plus ETA offset for flight tSeparation within package
				for w = 1, #flight[f].route do									--iterate through all waypoints of flight
					if flight[f].route[w].id == "Target" or flight[f].route[w].id == "Station" or flight[f].route[w].id == "Sweep" then	--if target WP is found (target or orbit start)
						flight[f].route[w].eta = eta							--set ETA for target WP
						target_wp = w											--store target WP number
						if flight[f].player then								--if this is the player flight
							camp.player.tgt_wp = w								--store the target wp for the player
						elseif flight[f].client then								--if this is the player flight
							camp.client[flight[f].IdClient].tgt_wp = w								--store the target wp for the player
						end
						break
					end
				end
				
				--flight TOT for ferry flight (Nothing task)
				if flight[f].task == "Nothing" then
					flight[f].route[#flight[f].route].eta = eta					--set ETA for target WP (desitination WP)
					target_wp = #flight[f].route								--store target WP number (destination WP)
					if flight[f].player then									--if this is the player flight
						camp.player.tgt_wp = #flight[f].route					--store the target wp for the player
					end
				end
				
				--set WP ETAs going forward from target to landing
				local speed
				for w = target_wp + 1, #flight[f].route  do						--iterate through flight waypoints from target foward
					speed = vCruise												-- ATO_T_Debug01 vCruise by default 
					if flight[f].route[w].id == "Station" then					--if WP is the end point of an orbit station
						eta = flight[f].route[w - 1].eta + flight[f].loadout.tStation	--WP ETA is orbit start WP ETA plus on station time
						if eta > camp.dawn and flight[f].loadout.day == false then	--if ETA after dawn and not day capable
							eta = camp.dawn										--make dawn the orbit end ETA
						elseif eta > camp.dusk and flight[f].loadout.night == false then	--if ETA after dusk and not night capable
							eta = camp.dusk										--make dusk the orbit end ETA
						end
						flight[f].route[w].eta = eta							--set ETA at waypoint
					else
						if flight[f].route[w].id == "Egress" then
							speed = vAttack										--egress from target is at attack seed
						else
							speed = vCruise										--everything else is at cruise speed
						end
						if pack[p].main[1].loadout.standoff and pack[p].main[1].loadout.standoff > 15000 and flight[f].route[w].id == "Egress" then		--if the package has a standoff from target bigger than 15 km, proceed from attack point directly to egress
							local tgt_ap_dist = GetDistance(flight[f].route[target_wp], flight[f].route[target_wp - 1])		--distance from target to attack point
							local ap_eta = eta - tgt_ap_dist / speed			--eta at attack point
							local ap_egress_dist = GetDistance(flight[f].route[target_wp - 1], flight[f].route[target_wp + 1])	--distance from attack point to egress point
							eta = ap_eta + ap_egress_dist / speed				--calculate ETA at egress
						else
							local leg = GetDistance(flight[f].route[w - 1], flight[f].route[w])	--measure lenght of the next route leg
							eta = eta + leg / speed								--calculate ETA at next waypoint
						end
						flight[f].route[w].eta = eta							--set ETA at waypoint
					end
				end
				
				--set WP ETAs going backwards from target to take off
				local start_up_time = 300										--default 5 minutes for AI start up, taxi and form-up
				if db_airbases[flight[f].base].startup then						--if there is a specific value defined for that airbase, use this instead
					start_up_time = db_airbases[flight[f].base].startup
				end
				if flight[f].player == true or flight[f].client then								--for player flight
					if mission_ini.startup_time_player then							--if player value defined in camp -- Miguel21 modification M17.b Option F-14B, changement du temps avant start, possible � chaque mission plutot qu'au demarrage de la campagne
						start_up_time = mission_ini.startup_time_player				--use this value instead
					elseif camp.startup then										--if player value defined in camp
						start_up_time = camp.startup							--time for player start-up
					else
						start_up_time = start_up_time + 300						--if player start-up is undefined, add 5 minutes as default
					end
				end
				
				eta = tot + flight[f].eta_offset								--reset target WP ETA
				for w = target_wp, 2, -1 do										--iterate through flight waypoints from target backwards
					speed = vCruise												-- ATO_T_Debug01 vCruise by default 
					if flight[f].route[w].id == "Attack" or flight[f].route[w].id == "Target" then	--WP is target point or attack point
						speed = vAttack											--ingress to target is at attack seed
					elseif (flight[f].route[w].id == "Join") and not flight[f].helicopter then					--WP is join point --M06.c and not flight[f].helicopter
						speed = vCruise / 4 * 3									--speed to Join Point is 3/4 of cruise speed to allow for the climb
					elseif (flight[f].route[w].id == "Join") and  flight[f].helicopter then          -- Miguel21 modification M06.e : helicoptere playable
						speed = vCruise 
					end

					if speed < flight[f].loadout.vCruise / 4 * 3 then
						-- print("AtoRG passe speed < flight[f]..vCruise "..tostring(speed).." < ".. flight[f].loadout.vCruise / 4 * 3 )
						speed = flight[f].loadout.vCruise / 4 * 3
						-- print("AtoRG result: "..tostring(speed).." ==? ".. flight[f].loadout.vCruise / 4 * 3 )
					end
					
					local leg = GetDistance(flight[f].route[w], flight[f].route[w - 1])	--measure lenght of the previous route leg
					eta = eta - leg / speed										--calcualte ETA at previous waypoint
					if w - 1 == 1 then											--WP is first WP
						eta = eta - start_up_time								--subtract time for start up
					end
					
					flight[f].route[w - 1].eta = eta							--set ETA at previous waypoint
					
					if flight[f].player == true and w - 1 == 1 then				--for player flight and first waypoint
						player_start_shift = 0 - eta							--time shift to start player at mission start
					elseif flight[f].client == true and w - 1 == 1 then				--for player flight and first waypoint
						player_start_shift = 0 - eta							--time shift to start player at mission start
					end
				end
				
				--set WP ETAs for transport tasks
				if flight[f].task == "Transport" then
					eta = math.random(flight[f].tot_from + 600, flight[f].tot_to)	--make destination ETA for each transport flight in package random
					flight[f].route[#flight[f].route].eta = eta					--set ETA at destination waypoint
					for w = #flight[f].route, 2, -1 do							--iterate through flight waypoints from destination backwards
						local leg = GetDistance(flight[f].route[w], flight[f].route[w - 1])	--measure lenght of the previous route leg
						eta = eta - leg / vCruise								--calcualte ETA at previous waypoint
						if w - 1 == 1 then										--WP is first WP
							eta = eta - start_up_time							--subtract time for start up
						end
						
						flight[f].route[w - 1].eta = eta						--set ETA at previous waypoint
						
						if flight[f].player == true and w - 1 == 1 then			--for player flight and first waypoint
							player_start_shift = 0 - eta						--time shift to start player at mission start
						end
					end
				end
			end
		end
		
		TOTtable[pack[p].main[1].target_name] = TOTtable[pack[p].main[1].target_name] + player_start_shift	--adjust stored TOT of target for player shift
		
		for role,flight in pairs(pack[p]) do													--iterate through roles in package (main, SEAD, escort)
			for f = 1, #flight do																--iterate through all flights
				for w = 1, #flight[f].route do													--iterate through all waypoints
					if flight[f].route[w].id == "Station" and flight[f].route[w].eta + player_start_shift < 0 then		--Start or end of a station would be shifted before mission start
						flight[f].route[w].eta = 1												--adjust WP eta to mission start
					else
						flight[f].route[w].eta = flight[f].route[w].eta + player_start_shift	--adjust WP eta by time difference for player to start at mission start
					end
				end

				--Air starts
				local airstart = false															--if TOT causes a take off before mission start, flight becomes air start and this variable gets the number of the spawn WP
				
				--ATO_T_Debug02		for w = target_wp - 1, 1, -1 do	 		
				for w = target_wp - 1, 2, -1 do													--iterate through waypoints backwards
					if flight[f].route[w].eta < 0 then											--ETA before mission start
						--find flight position at mission start and make it a WP
						local h = GetHeading(flight[f].route[w + 1], flight[f].route[w])		--heading from last WP with positive ETA
						local speed
						if flight[f].route[w].id == "IP" then
							speed = vAttack
						else
							speed = vCruise
						end
						
						if speed < flight[f].loadout.vCruise / 4 * 3 then
							-- print("AtoRG passe speed < flight[f]..vCruise "..tostring(speed).." < ".. flight[f].loadout.vCruise / 4 * 3 )
							speed = flight[f].loadout.vCruise / 4 * 3
							-- print("AtoRG result: "..tostring(speed).." ==? ".. flight[f].loadout.vCruise / 4 * 3 )
						end
						
						local dist = flight[f].route[w + 1].eta * speed							--distance covered from mission start to first positive ETA
						if dist > GetDistance(flight[f].route[w], flight[f].route[w + 1]) then	--if distance is ahead of WP (caused by extra minutes at take off WP), keep spawn point over take off point but adjust id and alt for air spawn
							flight[f].route[w].id = "Spawn"
							flight[f].route[w].alt = flight[f].route[w + 1].alt
							flight[f].route[w].eta = 0											--ETA of WP is at mission start
						else																	--else move the spawn point to new location
							flight[f].route[w] = {
								x = flight[f].route[w + 1].x + math.cos(math.rad(h)) * dist,
								y = flight[f].route[w + 1].y + math.sin(math.rad(h)) * dist,
								eta = 0,														--ETA of WP is at mission start
								id = "Spawn",													--WP is spawn point
								alt = flight[f].route[w + 1].alt
							}
						end
						airstart = w															--store the number of the spawn WP (WPs ahead will be removed)
						break
					end
				end
			
				--remove WPs ahead of spawn WP
				local flight_tgt_wp = target_wp													--local copy of the target waypoint number for this flight only
				if airstart then																--if the flight is an air start
					for w = airstart - 1, 1, -1 do												--iterate through all the WPs from airstart WP to first WP
						table.remove(flight[f].route, w)										--remove all WPs ahead of spwan WP
						flight_tgt_wp = flight_tgt_wp - 1										--adjust flight target_wp
					end
				end
				
				--remove target and attack WP for escort tasks
				if flight[f].task == "Escort" then
					table.remove(flight[f].route, flight_tgt_wp)								--remove target WP from route
					if flight[f].route[flight_tgt_wp - 1].id ~= "Spawn" then
						table.remove(flight[f].route, flight_tgt_wp - 1)						--remove attack WP from route
					end
					if flight[f].player then													--if this is the player flight
						camp.player.tgt_wp = camp.player.tgt_wp - 2								--update the target WP (IP for Escort and SEAD)
					elseif flight[f].client then													--if this is the player flight
						camp.client[flight[f].IdClient].tgt_wp = camp.client[flight[f].IdClient].tgt_wp - 2								--update the target WP (IP for Escort and SEAD)
					end
				end
				if flight[f].task == "SEAD" or flight[f].task == "Escort Jammer" then
					table.remove(flight[f].route, flight_tgt_wp)								--remove target WP from route
					if flight[f].player then													--if this is the player flight
						camp.player.tgt_wp = camp.player.tgt_wp - 1								--update the target WP (IP for Escort and SEAD)
					end
				end
			end
		end
	end
end

-- local camp_str = "ATO_ATO_Timing = " .. TableSerialization(ATO, 0)						--make a string
-- local campFile = io.open("Debug/ATO_ATO_Timing.lua", "w")										--open targetlist file
-- campFile:write(camp_str)																		--save new data
-- campFile:close()