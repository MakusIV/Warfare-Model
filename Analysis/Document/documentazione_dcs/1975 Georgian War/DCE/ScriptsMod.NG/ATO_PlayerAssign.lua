--To assign the player to a flight in the ATO
--Initiated by Main_NextMission.lua
------------------------------------------------------------------------------------------------------- 
-- Miguel Fichier Revision  A01
------------------------------------------------------------------------------------------------------- 

-- adjustment A01 : robust form 
-- ATO_PA_Debug01 supprime la table camp.player qui garde par erreur celle du dossier Active
-- Miguel21 modification M33 	Custom Briefing (TargetName)
-- Mod Zarbas Z01 Select Task possible
-- Miguel21 modification M11.l : Multiplayer

-- =====================  Marco implementation ==================================
local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua")
-- NOTE MARCO: prova a caricarlo usando require(".. . .. . .. .ScriptsMod."versionPackageICM..".UTIL_Log.lua")
-- NOTE MARCO: https://forum.defold.com/t/including-a-lua-module-solved/2747/2
log.level = LOGGING_LEVEL
log.outfile = LOG_DIR .. "LOG_ATO_PlayerAssign." .. camp.mission .. ".log" 
local local_debug = true -- local debug   
log.info("Start")
-- =====================  End Marco implementation ==================================


local playable = {}																		--local table to store playable flights
local tab_boublon = {}																	-- multiplayable tag
selectMultiPackage = false
PlayerFlight = false

camp.player = nil
camp.client = nil

AllCoopPossible = false

if not camp.MultiPlayer then camp.MultiPlayer = {} end
if not camp.MultiPlayer["pack_n"] then camp.MultiPlayer["pack_n"] = {} end

for side, pack in pairs(ATO) do															--iterate through sides in ATO
	for p = 1, #pack do																	--iterate through packages in sides
		for role,flight in pairs(pack[p]) do											--iterate through roles in package (main, SEAD, escort)
			for f = 1, #flight do														--iterate through flights in roles
				if flight[f].playable == true then										--if flight is playable by player
					if flight[f].tot_from == 0 then										--flight is allowed to fly at mission start
						TrackPlayability(flight[f].playable, "ATO")						--track playabilty criterium has been met
						if flight[f].task == "Intercept" then							--if the task is intercept, check if there is an enemy strike with target in range of player interceptor
							local enemy = "blue"
							if side == "blue" then
								enemy = "red"
							end
							for enemy_pack_n, enemy_pack in pairs(ATO[enemy]) do							--iterate through enemy packages
								if enemy_pack.main[1].tot_from == 0 then									--enemy package is allowed to fly at mission start
									for wp_n, wp in pairs(enemy_pack.main[1].route) do						--iterate through waypoints of first enemy main flight
										if wp.id == "Attack" then											--waypoint is an attack waypoint (ignore target as enemy package might do a standoff attack)
											local dist = GetDistance(wp, flight[f].route[1])				--measure distance from interceptor base to target
											if dist <= flight[f].target.radius then							--target is in range for interception
												unitname_ = flight[f].type.." Pack " .. p .. " - " .. flight[f].name .. " - " .. flight[f].task .. " " .. f .. "-" .. 1
												if not tab_boublon[unitname_] then
													TrackPlayability(flight[f].playable, "hostiles")			--track playabilty criterium has been met
													
													playable[#playable + 1] = {									--add flight to playable table
														side = side,
														pack = p,
														role = role,
														flight = f,
														base = flight[f].base,
														unitname = unitname_,
														target_side = enemy,
														target_pack = enemy_pack_n,
														type = flight[f].type
													}
													tab_boublon[unitname_] = true	
													break														--stop wp loop
												end
											end
										end
									end
								end
							end
						elseif flight[f].task == "CAP" then													--if the task is CAP, check if enemy aircraft will enter the CAP area when player is on station
							if (f == 1 and (#flight - 1) * flight[f].loadout.tStation < flight[f].tot_to - flight[f].tot_from) or (f == 2 and (#flight - 1) * flight[f].loadout.tStation >= flight[f].tot_to - flight[f].tot_from) then	--allow only the first or second flight (relief on station) in package to be playable
								local enemy = "blue"
								if side == "blue" then
									enemy = "red"
								end
								for enemy_pack_n, enemy_pack in pairs(ATO[enemy]) do						--iterate through enemy packages
									local stoploop = false
									for w = 1, #enemy_pack.main[1].route - 1 do								--iterate through waypoints of first enemy main flight
										if (enemy_pack.main[1].route[w].id ~= "Target" and enemy_pack.main[1].route[w + 1].id ~= "Target") or enemy_pack.main[1].loadout.standoff == nil or enemy_pack.main[1].loadout.standoff <= 15000 then		--Ignore target WP for aircraft with standoff > 15 km
											local dist = GetTangentDistance(enemy_pack.main[1].route[w], enemy_pack.main[1].route[w + 1], flight[f].target)		--get closest distance from CAP station to route between WP w and WP w+1						
											if dist <= flight[f].target.radius then							--route segement is in range of CAP station
												TrackPlayability(flight[f].playable, "hostiles")			--track playabilty criterium has been met
												playable[#playable + 1] = {									--add flight to playable table
													side = side,
													pack = p,
													role = role,
													flight = f,
													base = flight[f].base,
													unitname = flight[f].type.." Pack " .. p .. " - " .. flight[f].name .. " - " .. flight[f].task .. " " .. f .. "-" .. 1,
													target_side = enemy,
													target_pack = enemy_pack_n,
													type = flight[f].type
												}
												stoploop = true
												break														--stop WP loop
											end
										end
									end
									if stoploop then
										break																--stop enemy packages loop
									end
								end
							end
						else
							playable[#playable + 1] = {														--add flight to playable table
								side = side,
								pack = p,
								role = role,
								flight = f,
								base = flight[f].base,
								unitname = flight[f].type.." Pack " .. p .. " - " .. flight[f].name .. " - " .. flight[f].task .. " " .. f .. "-" .. 1,
								target_name = flight[f].target_name,										-- Miguel21 modification M33 	Custom Briefing (TargetName)
								type = flight[f].type
							}
						end
					end
				elseif Multi.NbGroup >= 1 then																-- Miguel21 modification M11.j : Multiplayer
					local stoploop = false
					for k=1, Multi.NbGroup do
						if Multi.Group[k].PlaneType == flight[f].type  and not stoploop then								--flight is allowed to fly at mission start --flight[f].tot_from <=180 and
							playable[#playable + 1] = {														--add flight to playable table
								side = side,
								pack = p,
								role = role,
								flight = f,
								base = flight[f].base,
								unitname = flight[f].type.." Pack " .. p .. " - " .. flight[f].name .. " - " .. flight[f].task .. " " .. f .. "-" .. 1,
								target_name = flight[f].target_name,
								type = flight[f].type
							}
							stoploop = true
						end
					end
				end
			end
		end
	end
end

local r	
local TaskRefused = false

print()

if Multi.Group then
	for i = 1, #Multi.Group do
		Multi.Group[i].counted = nil
	end
end 

if #playable > 0 then
	local playability_Multi = {}
	for i=1, #playable do															--check si un group à trouver son avion
		for k=1, Multi.NbGroup do
			if playable[i].type ==  Multi.Group[k].PlaneType and not Multi.Group[k].counted and not playable[i].counted then 
				playability_Multi[k] = 1
				Multi.Group[k].counted = true
				playable[i].counted = true
			end
		end
	end

	local sum = 0
	for i=1, #playability_Multi do													--fait la sum des groupes ayant trouvé son avion
		if playability_Multi[i] then
			sum = sum + playability_Multi[i]
		end
	end
	if sum == Multi.NbGroup then													--si la sum des group multi correspon à la sum de group avionné, alors c'est bon
		AllCoopPossible = true
	end
end

if #playable > 0 and AllCoopPossible then																--there are playable flights

	if SinglePlayer and AllCoopPossible then														-- if solo flight
		-- Mod Zarbas Z01 Select Task possible
		----------------
		
		local tabIndex = {}
		repeat
			print("\n\n Day or Night? : "..daytime)														-- info day or not
			print("\n\nAvailable tasks:")
			for index = 1, #playable do
				io.write(index.." - "..playable[index].base.." - "..playable[index].unitname )
				if playable[index].target_name ~= nil then  io.write(" - "..playable[index].target_name) end
				io.write("\n")
				tabIndex[index] = true
			end
			print("r - random task")
			print("s - skip mission")
			tabIndex["s"] = true
			tabIndex["S"] = true
			tabIndex["r"] = true
			tabIndex["R"] = true
			if #playable == 1 then 
				print("Please select your task (1-r-s): ")
			else 
				print("Please select your task (1-"..(#playable).."-r-s): ")			
			end
			r = io.read()
			
			if r ~= "" and string.byte(r) <= 57 then				-- adjustment A01 : robust form 
				r = tonumber(r)										-- si inférieur à 57 ASCII, c'est inférieur au chiffre 9, donc c'est un chiffre
			end 				

			if not tabIndex[r] then
				print("\nInvalid entry.\n")
				badEntry = true
			end
		until tabIndex[r]
		
		if type(r) == "string" then 
			if string.lower(r) == "r" then
				r = math.random(1, #playable)
			elseif string.lower(r) == "s" then
				TaskRefused = true
				r = math.random(1, #playable)	
			end
		end 

		ATO[playable[r].side][playable[r].pack][playable[r].role][playable[r].flight].player = true		--mark ATO entry as player flight
		
		camp.player = {
			side = playable[r].side,
			pack_n = playable[r].pack,
			role = playable[r].role,
			flight = playable[r].flight,
			unitname = playable[r].unitname,
			target = ATO[playable[r].side][playable[r].pack][playable[r].role][playable[r].flight].target,
			tgt_side = playable[r].target_side,
			tgt_pack = playable[r].target_pack,
			tgt_wp = 1,
			airbase = playable[r].base,
		}
		
		------------------
	elseif AllCoopPossible then	--si le multiplayerF1 est demandé
		
		print(" -------------------------------------------------------> Note: Your plane Flight wishes: ")
		for k=1,  Multi.NbGroup do
			print(" -------------------------------------------------------> "..Multi.Group[k].NbPlane.." "..Multi.Group[k].PlaneType.." ("..Multi.Group[k].side..") "..Multi.Group[k].task)
		end
		io.write( "\n")
		
		local tabSelect = {}																		--table pour afficher * devant chaque selection
		local badEntry = false
		for k=1, Multi.NbGroup do																	-- si le multiplayer est demande
			local tabIndex = {}																	--table pour afficher uniquement les choix possibles
			
			repeat
				print("\n\nAvailable tasks Flight: "..k)
				for index = 1, #playable do
					local Nindex = " "
					if tabSelect[index] then
						Nindex = "*"
					elseif Multi.Group[k].PlaneType == playable[index].type then
						Nindex = index 
						tabIndex[index] = true
					else
						Nindex = " "
					end
					
					io.write(Nindex.." -  Pack : "..playable[index].pack.." - "..playable[index].base.." - "..playable[index].unitname )
					if playable[index].target_name ~= nil then  io.write(" - "..playable[index].target_name) end
					io.write("\n")

				end
				
				print("s - skip mission")
				tabIndex["s"] = true
				tabIndex["S"] = true
				if badEntry then print("\n\WARNING, your previous choice was wrong. Do it again: ") end
				print("Please select your task (1-"..(#playable).."): ")

				r = io.read()
				
				if r ~= "" and string.byte(r) <= 57 then				-- adjustment A01 : robust form 
					r = tonumber(r)										-- si inférieur à 57 ASCII, c'est inférieur au chiffre 9, donc c'est un chiffre
				end 										
				
				if not tabIndex[r] then
					print("\nInvalid entry.\n")
					badEntry = true
				else
					tabSelect[r] = true
					badEntry = false
				end	
				
			until tabIndex[r]
		
			if playable[r] then print("Selected: "..playable[r].unitname) end
			
			if type(r) == "string" then 
				if string.lower(r) == "r" then
					r = math.random(1, #playable)
				elseif string.lower(r) == "s" then
					TaskRefused = true
					r = math.random(1, #playable)	
				end
			end 
			
			-- if not camp.MultiPlayer then camp.MultiPlayer = {} end
			-- if not camp.MultiPlayer.pack_n then camp.MultiPlayer.pack_n = {} end

			if TaskRefused then
			elseif k == 1 then
				ATO[playable[r].side][playable[r].pack][playable[r].role][playable[r].flight].player = true
				ATO[playable[r].side][playable[r].pack][playable[r].role][playable[r].flight].NbPlaneClient = Multi.Group[k].NbPlane
				camp.player = {
					side = playable[r].side,
					pack_n = playable[r].pack,
					role = playable[r].role,
					flight = playable[r].flight,
					unitname = playable[r].unitname,
					target = ATO[playable[r].side][playable[r].pack][playable[r].role][playable[r].flight].target,
					tgt_side = playable[r].target_side,
					tgt_pack = playable[r].target_pack,
					tgt_wp = 1,
					airbase = playable[r].base,
				}
			else	

				ATO[playable[r].side][playable[r].pack][playable[r].role][playable[r].flight].client = true
				ATO[playable[r].side][playable[r].pack][playable[r].role][playable[r].flight].IdClient = k
				ATO[playable[r].side][playable[r].pack][playable[r].role][playable[r].flight].NbPlaneClient = Multi.Group[k].NbPlane
				if not camp.client then camp.client = {} end
				camp.client[k] = {
					side = playable[r].side,
					pack_n = playable[r].pack,
					role = playable[r].role,
					flight = playable[r].flight,
					unitname = playable[r].unitname,
					target = ATO[playable[r].side][playable[r].pack][playable[r].role][playable[r].flight].target,
					tgt_side = playable[r].target_side,
					tgt_pack = playable[r].target_pack,
					tgt_wp = 1,
					airbase = playable[r].base,
				}
				camp.MultiPlayer.pack_n[playable[r].pack] = true
			end
		end
	end
	

	if TaskRefused == true then
		PlayerFlight = false																--set true to end mission generation loop
	elseif AllCoopPossible then
		PlayerFlight = true																	--set true to end mission generation loop
	end

	if not TaskRefused then
		--for intercept task, modify target package spawn to enter EWR coverage at mission start
		if ATO[playable[r].side][playable[r].pack][playable[r].role][playable[r].flight].task == "Intercept" and ATO[playable[r].target_side] then		--player task is intercept -- Miguel21 modification M11.j : Multiplayer
			local pack = ATO[playable[r].target_side][playable[r].target_pack]											--pointer to target package
			
			--find point where target package enters EWR coverage
			for w = 1, #pack.main[1].route - 1 do																		--iterate through waypoints of first main flight
			
				if (pack.main[1].route[w].id ~= "Target" and pack.main[1].route[w + 1].id ~= "Target") or pack.main[1].loadout.standoff == nil or pack.main[1].loadout.standoff <= 15000 then				--Ignore target WP for aircraft with standoff > 15 km
					
					local base_route_distance = GetTangentDistance(pack.main[1].route[w], pack.main[1].route[w + 1], ATO[playable[r].side][playable[r].pack][playable[r].role][playable[r].flight].route[1])	--get closest distance from interceptor base to route between WP w and WP w+1
					if base_route_distance <= ATO[playable[r].side][playable[r].pack][playable[r].role][playable[r].flight].target.radius then		--route segement is in range of interceptor
								
						local detected = false
						local distance = 100000000																				--distance from WP w to point where EWR coverage is entered
						local heading = GetHeading(pack.main[1].route[w], pack.main[1].route[w + 1])							--heading between WP w and WP w+1
						
						for e = 1, #ewr[playable[r].side] do																	--iterate through all ewr/awacs
							local radar_route_distance = GetTangentDistance(pack.main[1].route[w], pack.main[1].route[w + 1], ewr[playable[r].side][e])		--get closest distance from radar to route between WP w and WP w+1
							if radar_route_distance < ewr[playable[r].side][e].range then										--if route passes radar range circle
								local p1_ewr_heading = GetHeading(pack.main[1].route[w], ewr[playable[r].side][e])				--heading from p1 to radar
								local alpha = math.abs(heading - p1_ewr_heading)												--angle beteen route and p1-ewr
								if alpha > 180 then
									alpha = math.abs(alpha - 360)
								end						
								local p1_ewr = GetDistance(pack.main[1].route[w], ewr[playable[r].side][e])						--distance between p1 and ewr
								local p1_p90ewr = math.cos(math.rad(alpha)) * p1_ewr											--distance between p1 and point on route perpendicular to ewr
								local p90ewr_ewr = p1_ewr * math.sin(math.rad(alpha))											--distance between ewr and point on route perpendicular to ewr
								local p90t_pC = math.sqrt(math.pow(ewr[playable[r].side][e].range, 2) - math.pow(p90ewr_ewr, 2))	--distance between point on route perpendiculat to ewr and point on route intersecting ewr circle
								local p1_pC = p1_p90ewr - p90t_pC																--distance from p1 to point on route intersecting ewr circle
								
								local p1_base = GetDistance(pack.main[1].route[w], ATO[playable[r].side][playable[r].pack][playable[r].role][playable[r].flight].route[1])	--distance between p1 and interceptor base
								local p1_p90base = math.cos(math.rad(alpha)) * p1_base											--distance between p1 and point on route perpendicular to base
								local p90base_base = p1_base * math.sin(math.rad(alpha))										--distance between base and point on route perpendicular to base
								local p90b_pB = math.sqrt(math.pow(ATO[playable[r].side][playable[r].pack][playable[r].role][playable[r].flight].target.radius, 2) - math.pow(p90base_base, 2))	--distance between point on route perpendiculat to base and point on route intersecting base circle
								local p1_pB = p1_p90base - p90b_pB																--distance from p1 to point on route intersecting base circle
								
								if p1_pC <= 0 then																				--if point on route intersecting ewr circle is ahead of p1
									distance = 0																				--p1 is already within a ewr circle
									camp.player.EWR_freq = ewr[playable[r].side][e].frequency									--store frequency of EWR station (stores nil for AWACS)
									camp.player.EWR_call = ewr[playable[r].side][e].callsign									--store callsign of EWR station (stores nil for AWACS)
								elseif p1_pC < distance then
									distance = p1_pC																			--find the shortest distance to all ewr circles (this is the point on route where first EWR area is entered)
									camp.player.EWR_freq = ewr[playable[r].side][e].frequency									--store frequency of EWR station (stores nil for AWACS)
									camp.player.EWR_call = ewr[playable[r].side][e].callsign									--store callsign of EWR station (stores nil for AWACS)
								end
								if distance < p1_pB then
									distance = p1_pB
								end
								detected = true																					--route entered EWR coverage
							end					
						end
					
						if detected then																						--route entered EWR coverage
							
							--set package TOT
							local route_time = 0
							for n = w, #pack.main[1].route - 1 do																--iterate through waypoints again, starting from current WP
								local leg_speed																					--speed on route leg
								if pack.main[1].route[n].id == "IP" or pack.main[1].route[n].id == "Attack" then
									leg_speed = pack.main[1].loadout.vAttack													--attack speed
								else
									leg_speed = pack.main[1].loadout.vCruise													--cruise speed
								end
								local leg_time = GetDistance(pack.main[1].route[n], pack.main[1].route[n + 1]) / leg_speed		--time of flight for route leg
								route_time = route_time + leg_time																--collect complete route time
								if pack.main[1].route[n].id == "Attack" then													--continue until last leg to target
									break																						--stop second route loop
								end
							end
							
							local speed
							if pack.main[1].route[w].id == "IP" or pack.main[1].route[w].id == "Attack" then
								speed = pack.main[1].loadout.vAttack															--attack speed
							else
								speed = pack.main[1].loadout.vCruise															--cruise speed
							end
							route_time = route_time - distance / speed															--subtract time of flight for undetected part on detection route leg
							
							pack.main[1].tot = route_time																		--set package TOT for spawn at mission start when entering EWR detection area
							
							break																								--stop first route loop
						end
					end
				end
			end
		end
	end
end

-- local camp_str = "camp_ATO_PA = " .. TableSerialization(camp, 0)						--make a string
-- local campFile = io.open("Debug/camp_ATO_PA.lua", "w")										--open targetlist file
-- campFile:write(camp_str)																		--save new data
-- campFile:close()


-- local camp_str = "ATO_ATO_PA = " .. TableSerialization(ATO, 0)						--make a string
-- local campFile = io.open("Debug/ATO_ATO_PA.lua", "w")										--open targetlist file
-- campFile:write(camp_str)																		--save new data
-- campFile:close()