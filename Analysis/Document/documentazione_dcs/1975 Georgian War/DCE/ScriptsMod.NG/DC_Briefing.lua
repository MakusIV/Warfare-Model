--To create the briefing for the next mission
--Initiated by MAIN_NextMission.lua
------------------------------------------------------------------------------------------------------- 

-- Miguel Fichier Revision M33.g
------------------------------------------------------------------------------------------------------- 
-- correctif add Mig21 Channel 00

-- Miguel21 modification M41.b 	Sratchpad written in the Sratchpad file, if this modul is installed
-- miguel21 modification M34.l  custom FrequenceRadio (l: bug (number expected, got string))(k: utilise les indicatifs WEST pour EWR)(i  3 frequency bands)
-- Miguel21 modification M33.g 	Custom Briefing (g: divert without freq)(f: divert CVN)(e: divers) (d: Divert)(c: Alignement du txt)(onBoardNum)
-- Miguel21 modification M27 	MovedBullseye
								-- Miguel21 modification M17.c Option F-14B
-- Miguel21 Modification M15.d info catapulte/pont dans briefing
-- Miguel21 modification M11B. : Multiplayer--briefing								
-- Miguel21 M07.h : EWR toujours affiché dans le briefing
-- Miguel21 M06.b : helicoptere playable
-- Miguel21 M05.b : ajout picture Briefing + pictures Target
-- Miguel21 M04.e : ajout d'une troisieme radio

if not versionDCE then versionDCE = {} end
versionDCE["DC_Briefing.lua"] = "1.12.49"

-- =====================  Marco implementation ==================================
local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua")
-- NOTE MARCO: prova a caricarlo usando require(".. . .. . .. .ScriptsMod."versionPackageICM..".UTIL_Log.lua")
-- NOTE MARCO: https://forum.defold.com/t/including-a-lua-module-solved/2747/2
log.level = LOGGING_LEVEL
log.outfile = LOG_DIR .. "LOG_DC_Briefing." .. camp.mission .. ".log" 
local local_debug = true -- local debug   
log.info("Start")
-- =====================  End Marco implementation ==================================


local function FreqCapability(TestFreq, RadioPlane, Nradio)
	local waves  = ""
	
	if type(TestFreq) ~= "number" then
		return false
	end
	
	if TestFreq >= 225 then
		waves = "UHF" 
	elseif TestFreq >= 100 and TestFreq < 225 then
		waves = "VHF" 
	elseif TestFreq >= 30 and TestFreq < 100 then
		waves = "FM"
	else
		print()
		print("********************ATTENTION******************")
		print("***************Note for the Campaign Maker*****")
		print("Problem with frequency UFF? VHF? FM? "..tostring(TestFreq))
		_affiche(RadioPlane, "RadioPlane")
		print("********************ATTENTION******************")
		print()
		os.execute 'pause'
	end 

	if RadioPlane[Nradio] and RadioPlane[Nradio][waves] and (TestFreq > RadioPlane[Nradio][waves].min and TestFreq < RadioPlane[Nradio][waves].max)	 then		
		return true
	else 
		return false
	end
end

local target_picture = {}

-- local target_picture = {
	-- "blue",
	-- "red",
-- }

----- Mission Title -----
mission.sortie = camp.title .. " - " .. camp.mission


--Order of Battle
do
	local s = "Order of Battle:\\n\\n"																--make lists of the air order of battle for all sides
	
	--air units
	for side_name,side in pairs(oob_air) do															--iterate through sides in oob_air
		if side_name == "blue" then
			s = s .. "Blue Air Units:\\n"															--side header
		else
			s = s .. "Red Air Units:\\n"															--side header
		end
	
		--define list entries
		local entries = {
			[1] = {
				header = "Unit",
				values = {},
			},
			[2] = {
				header = "Type",
				values = {},
			},
			[3] = {
				header = "Base",
				values = {},
			},
			[4] = {
				header = "Lst",
				values = {},
			},
			[5] = {
				header = "Dm",
				values = {},
			},
			[6] = {
				header = "Rdy",
				values = {},
			},
		}
	
		--add list values
		for unit_n,unit in ipairs(side) do															--iterate through units
			if unit.inactive ~= true then															--unit is active
				table.insert(entries[1].values, unit.name)											--unit name
				table.insert(entries[2].values, ReplaceTypeName(unit.type))							--unit type
				table.insert(entries[3].values, unit.base)											--unit base
				table.insert(entries[4].values, unit.roster.lost)									--unit lost aircraft
				table.insert(entries[5].values, unit.roster.damaged)								--unit damaged aircraft
				table.insert(entries[6].values, unit.roster.ready)									--unit ready aircraft
			end
		end
		
		--determine maximum string length for each entry
		for e = 1, #entries do																		--iterate through entries
			entries[e].str_length = string.len(entries[e].header)									--store string length of header for this entry
			for n = 1, #entries[e].values do														--iterate through values of this entry
				local l = string.len(tostring(entries[e].values[n]))								--get string length of value of this entry
				if l > entries[e].str_length then													--if the string length is larger than the previous
					entries[e].str_length = l														--make it the new length (find the largest)
				end
			end
		end
		
		--build the list header
		for e = 1, #entries do																		--iterate through entries
			s = s .. entries[e].header																--add header
			if e < #entries then																	--if this is not the last header, add spaces to the next header	
				local space = entries[e].str_length + 3 - string.len(entries[e].header)				--calculate number of spaces that need to be added for alignement (string length of largest entry of same type + 3 - length of current entry = number of spaces)
				for m = 1, space * 1.5 do															
					s = s .. " "																	--add 1.5 spaces for every missing letter
				end
			end
		end
		s = s .. "\\n"
	
		--build the list		
		for n = 1, #entries[1].values do															--iterate through number of values (number of units)
			for e = 1, #entries do																	--iterate through entries
				s = s .. entries[e].values[n]														--add value to list
				if e < #entries then																--if this is not the last header, add spaces to the next header	
					local space = entries[e].str_length + 3 - string.len(tostring(entries[e].values[n]))	--calculate number of spaces that need to be added for alignement (string length of largest entry of same type + 3 - length of current entry = number of spaces)
					for m = 1, space * 1.5 do													
						s = s .. " "																--add 1.5 spaces for every missing letter
					end
				end
			end
			s = s .. "\\n"																			--make a new line after each unit
		end
		
		--add oob description text (reinforcements and repairs)
		if PlayerFlight and camp.player.side == side_name then										--only do it for player side
			if side_name == "blue" then
				if briefing_oob_text_blue ~= "" then
					s = s .. "\\n" .. briefing_oob_text_blue .. "\\n"
				else
					s = s .. "\\n\\n"
				end
			elseif side_name == "red" then
				if briefing_oob_text_red ~= "" then
					s = s .. "\\n" .. briefing_oob_text_red .. "\\n"
				else
					s = s .. "\\n\\n"
				end
			end
		else
			s = s .. "\\n\\n"																		--make a new line after each side
		end
	end
	
	
	--ground targets
	for side_name,side in pairs(targetlist) do														--iterate through sides in targetlist
		if side_name == "blue" then																	--owner of the target is the opposite of targetlist side
			s = s .. "Red Ground Assets:\\n"														--side header
		else
			s = s .. "Blue Ground Assets:\\n"														--side header
		end
		
		local sort_table = {}																		--array to sort the targetlist
		for k,v in pairs(side) do
			table.insert(sort_table, k)																--insert key into sort table
		end
		table.sort(sort_table)																		--sort the table
		for i, v in ipairs(sort_table) do															--iterate through sort table
			if side[v].inactive ~= true then														--target is active
				if side[v].alive then																--target is a ground target
					if side[v].hidden == nil or side[v].hidden == false then						--target is not hidden
						s = s .. "- " .. v .. " (" .. math.ceil(side[v].alive) .. "%)\\n"			--add target name and alive percentage
						if side[v].expand then														--target elements should be displayed expanded
							if side[v].elements then												--target has elements
								local max_strl = 0
								for e = 1, #side[v].elements do										--iterate through elements
									local strl = string.len(side[v].elements[e].name)				--get elements name stringh lenght
									if strl > max_strl then
										max_strl = strl												--find longest string name
									end
								end
								for e = 1, #side[v].elements do										--iterate through elements
									local space = max_strl - string.len(side[v].elements[e].name) + 5
									s = s .. "   - " .. side[v].elements[e].name					--list each element
									for m = 1, space do													
										s = s .. " "												--add one space for every missing letter
									end
									if camp.ShipHealth and camp.ShipHealth[side[v].elements[e].name] then		--ship has a health entry
										if camp.ShipHealth[side[v].elements[e].name] == 0 then					--ship is sunk
											s = s .. "(sunk)"
										elseif camp.ShipHealth[side[v].elements[e].name] < 33 then				--ship has less than 33% health
											s = s .. "(heavy damage)"
										elseif camp.ShipHealth[side[v].elements[e].name] < 66 then				--ship has less than 66% health
											s = s .. "(moderate damage)"
										elseif camp.ShipHealth[side[v].elements[e].name] < 100 then				--ship has less than 100% health
											s = s .. "(light damage)"
										end
									end
									s = s .. "\\n"									
								end
							end
						end
					end
				end
			end
		end
		s = s .. "\\n\\n"																			--make a new line after each side
	end
	
	
	--Assign briefing text to mission file
	if briefing_text_playable ~= "" and PlayerFlight then											--there is briefing text which is only added if the mission is actually playable
		if briefing_text == "" then																	--there was no briefing text for this mission instance yet
			briefing_status = briefing_status .. FormatDate(camp.date.day, camp.date.month, camp.date.year) .. ", " .. FormatTime(camp.time, "hh:mm") .. ":\\n\\n"		--add date and time header
		end
		briefing_status = briefing_status .. briefing_text_playable									--add briefing text 
	end
	mission.descriptionText = briefing_status .. "\\n" .. s
end


-- Miguel21 modification M11B. : Multiplayer
local briefing = { 
				  ["blue"] = "",
					["red"] = "",
				  }

	--	pack.main[1].route[1].eta
	
	-- table.sort(ATO["blue"], function(a,b) return a.main[1].route[1].eta > b.main[1].route[1].eta  end)
	-- table.sort(ATO["red"], function(a,b) return a.main[1].route[1].eta > b.main[1].route[1].eta  end)

-- for sideName,side in pairs(oob_air) do																-- Miguel21 modification M11B. : Multiplayer--briefing			

for sideName, pack in pairs(ATO) do																		--iterate through sides in ATO
	for p = 1, #pack do																					--iterate through packages in sides
		for role,flight in pairs(pack[p]) do															--iterate through roles in package (main, SEAD, escort)		
			for f = 1, #flight do
				if flight[f].player or flight[f].client then				
					local Tplayer = {}
					if flight[f].client then	
						Tplayer = camp.client[flight[f].IdClient]					
					elseif flight[f].player then	
						Tplayer = camp.player
					end		
					
					--Air Tasking Order
					-- if flight[f].player or flight[f].client then	--TODO doublon ligne a supprimer 
				
					player_target_name = Tplayer.pack[Tplayer.role][Tplayer.flight].target_name		-- tag confirmant que la mission sera créee, evite les doublons d'image

					local s = "Air Tasking Order:\\n"
					
					--define list entries
					local entries = {
						[1] = {
							header = "Sorties",
							values = {},
						},
						[2] = {
							header = "Mission",
							values = {},
						},
						[3] = {
							header = "TOT",
							values = {},
						},
					}
					
					--sum together packages package sortie numbers
					local ATOList = {}
					for pack_n,pack in pairs(ATO[Tplayer.side]) do												--go through ATO on player side
						
						--package time on target
						local tot = FormatTime(camp.time + pack.main[1].route[1].eta, "hh:mm:ss")				--time on target (use first wapoint if no Target or Station WP is found below)
						for wp_n,wp in pairs(pack.main[1].route) do												--iterate through waypoints of first main flight
							if wp.id == "Target" or wp.id == "Station" then										--if wp is target or station
								tot = FormatTime(camp.time + wp.eta, "hh:mm:ss")								--make this the time on target			
							end
						end
						
						--package sortie number
						local sortie_n = 0																		--number of aircraft (sorties) in package
						for role,flight in pairs(pack) do														--iterate through roles in package
							for n = 1, #flight do																--iterate through flights in role
								sortie_n = sortie_n + flight[n].number											--count number of aircraft
							end
						end
						
						if #ATOList == 0 then																	--ATOList is still empty
							ATOList[#ATOList + 1] = {
								target_name = pack.main[1].target_name,
								sortie_n = sortie_n,
								tot = tot,
							}
						else																					--ATOList has content
							for a = 1, #ATOList do																--go through ATOList to see if there is already a package entered with same target
								if pack.main[1].target_name == ATOList[a].target_name then						--find packages with same target to combine them 
									ATOList[a].sortie_n = ATOList[a].sortie_n + sortie_n
									break
								end
								if a == #ATOList then															--no package with same target was found in ATOList
									ATOList[#ATOList + 1] = {
										target_name = pack.main[1].target_name,
										sortie_n = sortie_n,
										tot = tot,
									}
								end
							end
						end
					end
					
					--add list values
					for pack_n,pack in pairs(ATOList) do														--iterate through packages
						table.insert(entries[1].values, pack.sortie_n)											--number of sorties in package
						table.insert(entries[2].values, pack.target_name)										--package target
						table.insert(entries[3].values, pack.tot)												--package time on target
					end
					
					--determine maximum string length for each entry
					for e = 1, #entries do																		--iterate through entries
						entries[e].str_length = string.len(entries[e].header) + 1									--store string length of header for this entry
						for n = 1, #entries[e].values do														--iterate through values of this entry
							local l = string.len(tostring(entries[e].values[n])) + 1 								--get string length of value of this entry
							if l > entries[e].str_length then													--if the string length is larger than the previous
								entries[e].str_length = l														--make it the new length (find the largest)
							end
						end
					end
					
					--build the list header
					for e = 1, #entries do																		--iterate through entries
						s = s .. entries[e].header																--add header
						if e < #entries then																	--if this is not the last header, add spaces to the next header	
							local space = entries[e].str_length + 0 - string.len(entries[e].header)				--calculate number of spaces that need to be added for alignement (string length of largest entry of same type + 3 - length of current entry = number of spaces)
							for m = 1, space * 1.0 do															
								s = s .. " "																	--add 1.5 spaces for every missing letter
							end
						end
					end
					s = s .. "\\n"

					--build the list		
					for n = 1, #entries[1].values do															--iterate through number of values (number of units)
						for e = 1, #entries do																	--iterate through entries
							s = s .. entries[e].values[n]														--add value to list
							if e < #entries then																--if this is not the last header, add spaces to the next header	
								local space = entries[e].str_length + 0 - string.len(tostring(entries[e].values[n]))	--calculate number of spaces that need to be added for alignement (string length of largest entry of same type + 3 - length of current entry = number of spaces)
								for m = 1, space * 1.0 do													
									s = s .. " "																--add 1.5 spaces for every missing letter
								end
							end
						end
						s = s .. "\\n"																			--make a new line after each unit
					end
					
					--Assign briefing text to mission file
					-- mission.descriptionText = mission.descriptionText .. s
					
					briefing[sideName] = briefing[sideName] .. s .. "\\n\\n"
					-- end


					----- Task Briefing -----
				
					--Mission overview					
					-- if flight[f].player or (flight[f].client ) then		
		
						local squad = Tplayer.pack[Tplayer.role][Tplayer.flight].name
						local target_name = Tplayer.pack[Tplayer.role][Tplayer.flight].target_name									--get the target of the player flight
						local player_task = Tplayer.pack[Tplayer.role][Tplayer.flight].task											--get the task of the player flight
						local target = Tplayer.pack[Tplayer.role][Tplayer.flight].target											--get target table
						local time_start = FormatTime(camp.time + Tplayer.waypoints[1].ETA, "hh:mm")								--player spawn time
						local time_launch
						
						local s = "\\n\\n\\n\\n".."\\n"
						local sBrief = "_________________________________________ BRIEFING Part: _______________________________________\\n"
						s = s..sBrief
						local sName = " "..tostring(flight[f].type).." "..squad.." "..player_task.." "
						local space = string.len(tostring(sBrief)) - string.len(tostring(sName))									--calculate number of spaces that need 
						for n = 1, (space / 2)-1  do														
							s = s .. "_"																
						end	
						s = s..sName
						for n = 1, (space / 2)-1  do														
							s = s .. "_"																
						end	
						s = s.."\\n"	
						s = s.."________________________________________________________________________________________________\\n"
						s = s.."\\n"
			
						if not target_picture[sideName] then target_picture[sideName] = {} end
						target_picture[sideName] = Tplayer.pack[Tplayer.role][Tplayer.flight].target.picture						--get the target picture MIGUEL21 Miguel21 M05
					
						if Tplayer.waypoints[2] then
							time_launch = FormatTime(camp.time + Tplayer.waypoints[2].ETA , "hh:mm")								--player take off time
						end

						local time_target = FormatTime(camp.time + Tplayer.waypoints[Tplayer.tgt_wp].ETA, "hh:mm")					--player time on target
						
						--CAP
						if player_task == "CAP" then
							local time_station = FormatTime(camp.time + Tplayer.waypoints[Tplayer.tgt_wp + 1].ETA, "hh:mm")			--player time to leave stations (for CAP, AWACS and Refueling)
							s = s .. "You are tasked to perform a Combat Air Patrol " .. target.text .. " from " .. time_target .. " to " .. time_station .. ". Engage all hostile aircraft threatening friendly forces in your CAP area.\\n"
						
						--Intercept
						elseif player_task == "Intercept" then
							
							local airbase = Tplayer.pack[Tplayer.role][Tplayer.flight].base

							if Tplayer.tgt_pack then	 --ATO[Tplayer.tgt_side][Tplayer.tgt_pack]
								
								local tgt_heading = GetHeading(Tplayer.waypoints[1], ATO[Tplayer.tgt_side][Tplayer.tgt_pack].main[1].route[1])
								local tgt_distance = GetDistance(Tplayer.waypoints[1], ATO[Tplayer.tgt_side][Tplayer.tgt_pack].main[1].route[1])
								local tgt_n = 0
								for role, flight in pairs (ATO[Tplayer.tgt_side][Tplayer.tgt_pack]) do
									for n = 1, #flight do
										tgt_n = tgt_n + flight[n].number
									end
								end
								if tgt_n == 1 then
									s = s .. "You are assigned to ground alert intercept duty at " .. airbase .. ". Early warning radar has detected " .. tgt_n .. " target inbound to your sector at " .. math.floor(tgt_heading) .. "°/" .. FormatDistance(tgt_distance) .. ". Launch imediately for interception.\\n"
								else
									s = s .. "You are assigned to ground alert intercept duty at " .. airbase .. ". Early warning radar has detected " .. tgt_n .. " targets inbound to your sector at " .. math.floor(tgt_heading) .. "°/" .. FormatDistance(tgt_distance) .. ". Launch imediately for interception.\\n"
								end
						else
								s = s .. "You are assigned to ground alert intercept duty at " .. airbase .. " Wait for the GCI to scramble you..."
						
						end
						--Fighter Sweep
						elseif player_task == "Fighter Sweep" then
							s = s .. "You are tasked to perform a Fighter Sweep " .. target.text .. ". Your Time On Target is " .. time_target .. ".\\n"
						
						--Airbase Strike
						elseif player_task == "Strike" and target.class == "airbase" then
							s = s .. "You are tasked to strike " .. target.name .. " which hosts the " .. target.unit.name .. " equipped with " .. ReplaceTypeName(target.unit.type) .. ". Attack any parked aircraft on the airbase. Your Time On Target is " .. time_target .. "."
							if target.LaserCode then
								s = s .. " Target designation laser code " .. target.LaserCode .. "."
							end
							s = s .. "\\n"
						
						--Strike
						elseif player_task == "Strike" then
							s = s .. "You are tasked to strike " .. target_name .. " with a Time On Target of " .. time_target .. "."
							if target.LaserCode then
								s = s .. " Target designation laser code " .. target.LaserCode .. "."
							end
							s = s .. "\\n"
							
						--Anti-ship Strike
						elseif player_task == "Anti-ship Strike" then
							s = s .. "You are tasked to strike " .. target_name .. " with a Time On Target of " .. time_target .. "."
							if target.LaserCode then
								s = s .. " Target designation laser code " .. target.LaserCode .. "."
							end
							s = s .. "\\n"
							
						--Escort
						elseif player_task == "Escort" then
							if target.class == "airbase" then
								s = s .. "Escort a strike mission against " .. target.name .. ". Engage all hostile aircraft posing a threat to the strike package. "
								--s = s .. "Man your aircraft at " .. time_start .. " and prepare to launch at " .. time_launch .. ". Your Time on Target is " .. time_target .. ". Good Luck."
							elseif target.task == "Strike" or target.task == "Anti-ship Strike" then 
								s = s .. "Escort a strike mission against the " .. target_name .. ". Engage all hostile aircraft posing a threat to the strike package. "
								--s = s .. "Man your aircraft at " .. time_start .. " and prepare to launch at " .. time_launch .. ". Your Time on Target is " .. time_target .. ". Good Luck."
							elseif target.task == "Reconnaissance" then
								s = s .. "Escort a recon mission " .. target.text .. ". Engage all hostile aircraft posing a threat to the recon element. "
								--s = s .. "Man your aircraft at " .. time_start .. " and prepare to launch at " .. time_launch .. ". Your Time on Target is " .. time_target .. ". Good Luck."
							end
							s = s .. "\\n"
						
						--SEAD
						elseif player_task == "SEAD" then
							if target.class == "airbase" then
								s = s .. "Provide SEAD escort for a strike mission against " .. target.name .. ". Engage all hostile air defense systems posing a threat to the strike package. "
								--s = s .. "Man your aircraft at " .. time_start .. " and prepare to launch at " .. time_launch .. ". Your Time on Target is " .. time_target .. ". Good Luck."
							elseif target.task == "Strike" or target.task == "Anti-ship Strike" then 
								s = s .. "Provide SEAD escort for a strike mission against the " .. target_name .. ". Engage all hostile air defense systems posing a threat to the strike package. "
								--s = s .. "Man your aircraft at " .. time_start .. " and prepare to launch at " .. time_launch .. ". Your Time on Target is " .. time_target .. ". Good Luck."
							elseif target.task == "Reconnaissance" then
								s = s .. "Provide SEAD escort for a recon mission " .. target.text .. ". Engage all hostile air defense systems posing a threat to the recon element. "
								--s = s .. "Man your aircraft at " .. time_start .. " and prepare to launch at " .. time_launch .. ". Your Time on Target is " .. time_target .. ". Good Luck."
							end
							s = s .. "\\n"
						
						--Escort Jammer
						elseif player_task == "Escort Jammer" then
							if target.class == "airbase" then
								s = s .. "Provide jammer escort for a strike mission against " .. target.name .. ". "
								--s = s .. "Man your aircraft at " .. time_start .. " and prepare to launch at " .. time_launch .. ". Your Time on Target is " .. time_target .. ". Good Luck."
							elseif target.task == "Strike" or target.task == "Anti-ship Strike" then 
								s = s .. "Provide jammer escort for a strike mission against the " .. target_name .. ". "
								--s = s .. "Man your aircraft at " .. time_start .. " and prepare to launch at " .. time_launch .. ". Your Time on Target is " .. time_target .. ". Good Luck."
							elseif target.task == "Reconnaissance" then
								s = s .. "Provide jammer escort for a recon mission " .. target.text .. ". "
								--s = s .. "Man your aircraft at " .. time_start .. " and prepare to launch at " .. time_launch .. ". Your Time on Target is " .. time_target .. ". Good Luck."
							end
							s = s .. "\\n"
							
						--Flare Illumination
						elseif player_task == "Flare Illumination" then
							if target.class == "airbase" then
								s = s .. "Provide battlefield flare illumination for a strike mission against " .. target.name .. ". "
								--s = s .. "Man your aircraft at " .. time_start .. " and prepare to launch at " .. time_launch .. ". Your Time on Target is " .. time_target .. ". Good Luck."
							elseif target.task == "Strike" or target.task == "Anti-ship Strike" then 
								s = s .. "Provide battlefield flare illumination for a strike mission against the " .. target_name .. ". "
								--s = s .. "Man your aircraft at " .. time_start .. " and prepare to launch at " .. time_launch .. ". Your Time on Target is " .. time_target .. ". Good Luck."
							elseif target.task == "Reconnaissance" then
								s = s .. "Provide battlefield flare illumination for a recon mission " .. target.text .. ". "
								--s = s .. "Man your aircraft at " .. time_start .. " and prepare to launch at " .. time_launch .. ". Your Time on Target is " .. time_target .. ". Good Luck."
							end
							s = s .. "\\n"
							
						--Laser Illumination
						elseif player_task == "Laser Illumination" then
							if target.class == "airbase" then
								s = s .. "Provide target laser designation for a strike mission against " .. target.name .. ". "
								s = s .. "Set your laser designator to code " .. target.LaserCode .. ". "
								--s = s .. "Man your aircraft at " .. time_start .. " and prepare to launch at " .. time_launch .. ". Your Time on Target is " .. time_target .. ". Good Luck."
							elseif target.task == "Strike" or target.task == "Anti-ship Strike" then 
								s = s .. "Provide target laser designation for a strike mission against the " .. target_name .. ". "
								s = s .. "Set your laser designator to code " .. target.LaserCode .. ". "
								--s = s .. "Man your aircraft at " .. time_start .. " and prepare to launch at " .. time_launch .. ". Your Time on Target is " .. time_target .. ". Good Luck."
							elseif target.task == "Reconnaissance" then
								s = s .. "Provide target laser designation for a recon mission " .. target.text .. ". "
								s = s .. "Set your laser designator to code " .. target.LaserCode .. ". "
								--s = s .. "Man your aircraft at " .. time_start .. " and prepare to launch at " .. time_launch .. ". Your Time on Target is " .. time_target .. ". Good Luck."
							end
							s = s .. "\\n"
						
						--Reconnaissance
						elseif player_task == "Reconnaissance" then
							s = s .. "You are tasked to perform reconnaissance " .. target.text .. ". Your Time On Target is " .. time_target .. ".\\n"
						
						--AWACS
						elseif player_task == "AWACS" then
							local time_station = FormatTime(camp.time + Tplayer.waypoints[Tplayer.tgt_wp + 1].ETA, "hh:mm")		--player time to leave stations (for CAP, AWACS and Refueling)
							s = s .. "You are tasked to perform a AWACS patrol " .. target.text .. " from " .. time_target .. " to " .. time_station .. ".\\n"
							
						--Refueling
						elseif player_task == "Refueling" then
							local time_station = FormatTime(camp.time + Tplayer.waypoints[Tplayer.tgt_wp + 1].ETA, "hh:mm")		--player time to leave stations (for CAP, AWACS and Refueling)
							s = s .. "You are tasked to perform tanker support " .. target.text .. " from " .. time_target .. " to " .. time_station .. ". Provide fuel to friendly aircraft in your patrol area.\\n"
						
						--Transport
						elseif player_task == "Transport" then
							s = s .. "Fly a transport mission from " .. target.base .. " to " .. target.destination .. ".\\n"
							
						--Nothing/Ferry
						elseif player_task == "Nothing" then
							s = s .. "Ferry flight from " .. target.base .. " to " .. target.destination .. ".\\n"
							
						end
						
						if targetlist[Tplayer.side][target_name].elements then									--if the target is a scenery, vehicle or ship target
							s = s .. "\\nTarget:\\n" .. target_name .. " (" .. math.ceil(targetlist[Tplayer.side][target_name].alive) .. "%)\\n"		--Target name and percentage of alive sub-elements 
							for e = 1, #targetlist[Tplayer.side][target_name].elements do						--list all target elements
								local ename = targetlist[Tplayer.side][target_name].elements[e].name			--element name
								local i = string.find(ename, "#")													--position of # in string
								if i then
									ename = string.sub(ename, 0, i - 1) 											--only display part of element name before #
								end
								s = s .. "- " .. ename
								if targetlist[Tplayer.side][target_name].elements[e].dead == true then			--if the target element is destroyed
									s = s .. " (destroyed)\\n"														--mark as destroyed and make new line
								else
									s = s .. "\\n"																	--make new line
								end
							end
						end
						-- Miguel21 modification M11B. : Multiplayer--briefing pour chaque camp 16 X briefing[sideName]
						briefing[sideName] = briefing[sideName] .. s .. "\\n\\n"									--add mission overview string to briefing string
					-- end


					--Package overview
					-- if PlayerFlight and Tplayer.side == sideName then																			--if the mission has a player flight
					-- if flight[f].player or flight[f].client then
						local s = "Package:\\n"																		--make a list of the details of all flights in the player package
						
						local entries = {																			--list entries that are making up the package overview
							[1] = {
								lookup = "task",																	--lookup in the ATO flight table
								header = "Task",																	--name which should be displayer in the list header
								str_length = 4,																		--string length of largest entry of this type (default the string length of the header)
							},
							[2] = {
								lookup = "number",
								header = "Num",
								str_length = 3,
							},
							[3] = {
								lookup = "type",
								header = "Type",
								str_length = 4,
							},
							[4] = {
								lookup = "base",
								header = "Base",
								str_length = 4,
							},
							[5] = {
								lookup = "callsign",
								header = "Callsign",
								str_length = 8,
							},
							[6] = {
								lookup = "player",
								header = "",
								str_length = 0,
							},
						}

						--collect the maximum string length of each entry in the list
						for role_name,role in pairs(Tplayer.pack) do											--iterate through roles in the player package
							for flight_n,flight in pairs(role) do													--iterate through the flights in all roles
								for e = 1, #entries do																--iterate through all entries
									local value = ReplaceTypeName(flight[entries[e].lookup])
									local l = string.len(tostring(value))	 + 3										--get the string length of the current entry for this flight
									if l > entries[e].str_length then												--if the string length is larger than the previous
										entries[e].str_length = l													--make it the new length (find the largest)
									end
								end
							end
						end
						
						--build the list header
						for e = 1, #entries do																		--iterate through all entries
							s = s .. entries[e].header																--add entry of this flight to list
							if e ~= #entries then																	--if this is not the last entry of the flight, add spaces to the next entry	
								local space = entries[e].str_length + 0 - string.len(tostring(entries[e].header))	--calculate number of spaces that need to be added for alignement (string length of largest entry of same type + 3 - length of current entry = number of spaces)
								for n = 1, space * 1.0 do															
									s = s .. " "																	--add 1.5 spaces for every missing letter
								end
							end
						end
						s = s .. "\\n"
						
						--build the overview list with the entries of all flights
						for role_name,role in pairs(Tplayer.pack) do											--iterate through roles in the player package	
							for flight_n,_flight in pairs(role) do													--iterate through flights in all roles
								for e = 1, #entries do																--iterate through all entries
									if type(_flight[entries[e].lookup]) == "string" or type(_flight[entries[e].lookup]) == "number" then	--entry is a string or number
										local value = ReplaceTypeName(_flight[entries[e].lookup])
										s = s .. value																--add entry of this flight to list
										if e ~= #entries then																			--if this is not the last entry of the flight, add spaces to the next entry	
											local space = entries[e].str_length + 0 - string.len(tostring(value))	--calculate number of spaces that need to be added for alignement (string length of largest entry of same type + 3 - length of current entry = number of spaces)
											for n = 1, space * 1.0 do													
												s = s .. " "														--add 1.5 spaces for every missing letter
											end
										end
									elseif _flight[entries[e].lookup] then											--entry is true (player marking)
										local client = ""
										if flight[f].player then client = "player" end
										if flight[f].client then client = "client" end
										s = s .. "("..client..")"															--add player flight marking
									end
								end
								s = s .. "\\n"																		--make a new line after each flight
							end
						end
						briefing[sideName] = briefing[sideName] .. s .. "\\n\\n"														--add package overview string to briefing string



					--Flight overview
					-- Miguel21 modification M33 	Custom Briefing (onBoardNum)

					local s = "Flight:\\n"																		--make a list of the details of all flights in the player package
						s = s.."CallSign    Designated aircraft number \\n"	
					
					for role_name,role in pairs(Tplayer.pack) do												--iterate through roles in the player package	
						for flight_n,_flight in pairs(role) do													--iterate through flights in all roles
							if _flight.units	 then
								for u=1 , #_flight.units do
									if type(_flight.units[u].callsign) == "table" then
										s = s.. tostring(_flight.units[u].callsign.name).."       "..tostring(_flight.units[u].onboard_num).. "\\n"
									else
										s = s.. tostring(_flight.units[u].callsign) .."       "..tostring(_flight.units[u].onboard_num).. "\\n"
									end
								end
							end
						end
					end
					briefing[sideName] = briefing[sideName] .. s .. "\\n\\n"




					-- Miguel21 modification M27 	MovedBullseye
					if brief[sideName] then
						local s = "Bullseye:\\n"
						s = s.." bullseye Name " .. brief[sideName].bullseye.name
						if brief[sideName]["bullseye"]["gps"] then
							s = s.." " .. brief[sideName]["bullseye"]["gps"].." \\n"
						end
						s = s.." \\n"
						briefing[sideName] = briefing[sideName] .. s .. "\\n\\n"
					end

					--Navigation overview
					local s = "Flightplan:\\n"																	--make a list with details of the player waypoints
					
					local entries = {																			--list entries that are making up the navigaion overview
						[1] = {
							lookup = "number",																	--lookup in the player.waypoints table
							header = "WP",																		--name which should be displayer in the list header
							str_length = 2,																		--string length of largest entry of this type (default the string length of the header)
						},
						[2] = {
							lookup = "briefing_name",
							header = "Descr",
							str_length = 5,
						},
						[3] = {
							lookup = "alt",
							header = "Altitute",
							str_length = 8,
						},
						[4] = {
							lookup = "speed",
							header = "Speed",
							str_length = 5,
						},
						[5] = {
							lookup = "ETA",
							header = "ETA",
							str_length = 3,
						},
					}
					
					--collect the maximum string length of each entry in the list	
					for w = 1, #Tplayer.waypoints do														--iterate through the waypoints
						for e = 1, #entries do																	--iterate through all entries
							local entry																			--lookup of entry e of WP w
							if entries[e].lookup == "number" then
								entry = w - 1																	--waypoint number, starts with 0
							elseif entries[e].lookup == "ETA" then
								entry = FormatTime(camp.time + Tplayer.waypoints[w][entries[e].lookup], "hh:mm:ss")	--format the time in the hh:mm:ss format
							elseif entries[e].lookup == "alt" then
								entry = FormatAlt(Tplayer.waypoints[w][entries[e].lookup])					--format altitude in meters or feet
							elseif entries[e].lookup == "speed" then
								entry = FormatSpeed(Tplayer.waypoints[w][entries[e].lookup])				--format speed in kph or kts
							else
								entry = Tplayer.waypoints[w][entries[e].lookup]								--no special formating
							end
							local l = string.len(tostring(entry)) + 3 												--get the string length
							if l > entries[e].str_length then													--if the string length is larger than the previous
								entries[e].str_length = l														--make it the new length (find the largest)
							end
						end
					end
						
					--build the list header
					for e = 1, #entries do																		--iterate through all entries
						s = s .. entries[e].header																--add entry of this waypoint to list
						if e ~= #entries then																	--if this is not the last entry of the waypoints, add spaces to the next entry	
							local space = entries[e].str_length + 0 - string.len(tostring(entries[e].header))	--calculate number of spaces that need to be added for alignement (string length of largest entry of same type + 3 - length of current entry = number of spaces)
							for n = 1, space * 1.0 do															
								s = s .. " "																	--add 1.5 spaces for every missing letter
							end
						end
					end
					s = s .. "\\n"
					
					--build the overview list with the entries of all waypoints
					local WP_num = 0																			--waypoint number, starts with 0
					for w = 1, #Tplayer.waypoints do														--iterate through all waypoints
						if Tplayer.waypoints[w].briefing_name ~= "Taxi" then								--do not list taxi waypoint in overview
							for e = 1, #entries do																--iterate through all entries
								local entry
								if entries[e].lookup == "number" then
									entry = WP_num
									WP_num = WP_num + 1
								elseif entries[e].lookup == "ETA" then
									entry = FormatTime(camp.time + Tplayer.waypoints[w][entries[e].lookup], "hh:mm:ss")	--format the time in the hh:mm:ss format
								elseif entries[e].lookup == "alt" then
									entry = FormatAlt(Tplayer.waypoints[w][entries[e].lookup])				--format altitude in meters or feet
								elseif entries[e].lookup == "speed" then
									entry = FormatSpeed(Tplayer.waypoints[w][entries[e].lookup])			--format speed in kph or kts
								else
									entry = Tplayer.waypoints[w][entries[e].lookup]							--no special formating
								end
								s = s .. entry
								if e ~= #entries then															--if this is not the last entry of the waypoint, add spaces to the next entry	
									local space = entries[e].str_length + 0 - string.len(tostring(entry))		--calculate number of spaces that need to be added for alignement (string length of largest entry of same type + 3 - length of current entry = number of spaces)
									for n = 1, space * 1.0 do														
										s = s .. " "															--add 1.5 spaces for every missing letter
									end
								end
							end
							s = s .. "\\n"																		--make a new line after each waypoint
						end
					end
					briefing[sideName] = briefing[sideName] .. s .. "\\n\\n"														--add navigation overview string to briefing string

					
					local refuelable = true
					--flight[f].helicopter
					for side_name,side in pairs(oob_air) do	
						for n,unit in pairs(side) do
							if unit.name == Tplayer.pack[Tplayer.role][Tplayer.flight].name and (unit.helicopter or unit.refuelable == false)  then
								refuelable = false
							end
						end
					end

					--Radio navigation
						
					local s = "Radio Navigation:\\n"
					s = s .."Base: ".. Tplayer.pack[Tplayer.role][Tplayer.flight].base
					--homebase TACAN
					if db_airbases[Tplayer.pack[Tplayer.role][Tplayer.flight].base].TACAN then
						s = s .. " TACAN: " .. db_airbases[Tplayer.pack[Tplayer.role][Tplayer.flight].base].TACAN 
					end	
					if db_airbases[Tplayer.pack[Tplayer.role][Tplayer.flight].base].tacan then
						s = s .. " TACAN: " .. db_airbases[Tplayer.pack[Tplayer.role][Tplayer.flight].base].tacan 
					end	
					if db_airbases[Tplayer.pack[Tplayer.role][Tplayer.flight].base].VOR then										--M33.d02
						s = s .. " VOR: " .. db_airbases[Tplayer.pack[Tplayer.role][Tplayer.flight].base].VOR 
					end	
					if db_airbases[Tplayer.pack[Tplayer.role][Tplayer.flight].base].NDB then
						s = s .. " NDB: " .. db_airbases[Tplayer.pack[Tplayer.role][Tplayer.flight].base].NDB 
					end	
					if db_airbases[Tplayer.pack[Tplayer.role][Tplayer.flight].base].ILS then
						s = s .. " ILS: " .. db_airbases[Tplayer.pack[Tplayer.role][Tplayer.flight].base].ILS 
					end	
					--carrier ICLS
					if db_airbases[Tplayer.pack[Tplayer.role][Tplayer.flight].base].icls then
						s = s .. " ICLS: Channel " .. db_airbases[Tplayer.pack[Tplayer.role][Tplayer.flight].base].icls
					end
					s = s .. "\\n"
					
					--Divert BASE	M33.d				
					if Tplayer.pack[Tplayer.role][Tplayer.flight].divert then 	
						for Divert, _base in pairs(Tplayer.pack[Tplayer.role][Tplayer.flight].divert) do							
							if Divert ~= Tplayer.pack[Tplayer.role][Tplayer.flight].base then	
								s = s .."Divert: ".. _base							
								--Divert TACAN
								if db_airbases[_base].TACAN then
									s = s .. " TACAN: " .. db_airbases[_base].TACAN 
								end	
								--Divert TACAN
								if db_airbases[_base].tacan then
									s = s .. " TACAN: " .. db_airbases[_base].tacan 
								end	
								--Divert VOR
								if db_airbases[_base].VOR then
									s = s .. " VOR: " .. db_airbases[_base].VOR 
								end						
								--Divert NDB
								if db_airbases[_base].NDB then
									s = s.. " NDB: " .. db_airbases[_base].NDB 
								end									
								--Divert ILS
								if db_airbases[_base].ILS then
									s = s.. " ILS: " .. db_airbases[_base].ILS 
								end	
								--Divert ils
								if db_airbases[_base].ils then
									s = s.. " ILS: " .. db_airbases[_base].ils 
								end	
								--Divert icls
								if db_airbases[_base].icls then
									s = s.. " ICLS: Channel " .. db_airbases[_base].icls 
								end									
								s = s.. "\\n"
							end
						end
					end
					
					--tanker TACAN
					if refuelable then	
						for pack_n,pack in pairs(ATO[Tplayer.side]) do																		--iterate through packages in player side
							for role_name,role in pairs(pack) do																				--iterate through roles in package
								if role[1] and role[1].task == "Refueling" then																	--if first flight is tanker
									if role[1].tacan then																						--tanker has a tacan channel
										s = s .. "Tanker " .. role[1].callsign .. ", TACAN " .. role[1].tacan .. "Y / TKR\\n"					--add TACAN informaion
									end
								end
							end
						end
					end
					briefing[sideName] = briefing[sideName] .. s ..  "\\n\\n"


					--Communication
					local s = "Communication:\\n"																		--overview of relevant comms frequencies
					local MC = 0
					if  flight[f].type == "MiG-21Bis" then			-- add Mig21 Channel 00
						MC = -1										-- MC ModChannel
					end
					
					for u = 1, #Tplayer.group["units"] do
						for n = 1, #camp.radio[sideName] do																		--do it for all the radios
							if 	frequency[flight[f].type] then
								for ir=1, #frequency[flight[f].type].radio do	
									if frequency[flight[f].type].radio[ir].nbCanal > 0 then
										if ir == n then
											-- frequency[flight[f].type].radio[i]
											if not Tplayer.group["units"][u]["Radio"] then Tplayer.group["units"][u]["Radio"] = {} end
											Tplayer.group["units"][u]["Radio"][n] = {
												["channels"] = {},
											}
										end
									end							
								end
							end
						end
					end						
	
					local AWACS_freq = {}																				--table to store AWACS frequencies
					local tanker_freq = {}																				--table to store tanker frequencies
					local EWR_freq = {}																					--table to store EWR frequencies
					local EWR_freqT = {}
					local CAP_freq = {}
					local ATC_Divert_freq = {}
					local All_freq = {}
					
					for pack_n,pack in pairs(ATO[Tplayer.side]) do														--iterate through packages in player side
						for role_name,role in pairs(pack) do															--iterate through roles in package													--iterate through the flights in role
							if role[1] and role[1].task == "AWACS" then													--if first flight is AWACS
								AWACS_freq[role[1].callsign] = role[1].frequency										--store callsign and frequency
							elseif role[1] and role[1].task == "Refueling" then											--if first flight is tanker
								tanker_freq[role[1].callsign] = role[1].frequency										--store callsign and frequency
							elseif role[1] and role[1].task == "CAP" then												--if first flight is tanker
								CAP_freq[role[1].callsign] = role[1].frequency											--store callsign and frequency
							elseif role[1]  and  string.find(role[1].task,"Strike") then								--and  string.find(role[1].task,"Strike")
					
								if not All_freq[role[1].callsign] then All_freq[role[1].callsign] = {} end
								
								if not All_freq[role[1].callsign].freq then All_freq[role[1].callsign].freq = role[1].frequency end
								if not All_freq[role[1].callsign].task then All_freq[role[1].callsign].task = role[1].task end

							end
						end
					end

					local tempEWR = ewr[Tplayer.side]
					
					-- miguel21 modification M34.g change freq EWR + custom FrequenceRadio (g: utilise les indicatifs WEST pour EWR)
					local ComparePossible = true
					for z=1, #tempEWR do
						if type(tempEWR[z].callsign) ~= "number" then
							ComparePossible = false
						end
					end
					
					if ComparePossible then																				--sort by name, if name is a number
						table.sort(tempEWR, function(a,b) return a.callsign < b.callsign  end)
					end

					
					-- for ewr_n,ewr in ipairs(tempEWR) do																--iterate through EWR on player side
						-- if ewr.frequency and ewr.callsign then														--if EWR has a freqency and callsign
							-- --   Miguel21 modification EWR M07.g
							-- if not EWR_freq[ewr.callsign] then
								-- EWR_freq[ewr.callsign] = {}
							-- end
							-- EWR_freq[ewr.callsign]["freq"] = ewr.frequency											--store callsign and frequency
							-- EWR_freq[ewr.callsign]["callsign"] = ewr.callsign	
						-- end
					-- end
					
					EWR_freq = {}
					for ewr_n,ewr in ipairs(tempEWR) do																	--iterate through EWR on player side
						if ewr.frequency and ewr.callsign then															--if EWR has a freqency and callsign
							--   Miguel21 modification EWR M07.g
							EWR_freqT = {}
							EWR_freqT[ewr.callsign] = {}

							EWR_freqT[ewr.callsign]["freq"] = ewr.frequency												--store callsign and frequency
							EWR_freqT[ewr.callsign]["callsign"] = ewr.callsign	
						
							EWR_freq[#EWR_freq+1] = EWR_freqT
						end
					end

					
					--Divert BASE	M33.d				
					if Tplayer.pack[Tplayer.role][Tplayer.flight].divert then 	
						for Divert, _base in pairs(Tplayer.pack[Tplayer.role][Tplayer.flight].divert) do														
							if Divert ~= Tplayer.pack[Tplayer.role][Tplayer.flight].base then
								ATC_Divert_freq[Divert] = db_airbases[_base].ATC_frequency
							end
						end
					end
					
					-- frequency[flight[f].type].radio[1].nbCanal					
					--reprend sous une forme plus simple les butées des radios
					local _radio = {}
					local radioP = {}
					
					if not frequency[flight[f].type] then							
						radioP[1] = {
							VHF = {
								min = 118,
								max = 173,
							},
							nbCanal = 0,
						}
					else
						for i=1, #frequency[flight[f].type].radio do
							radioP[i] = frequency[flight[f].type].radio[i]
						end							
					end

					--build list
					local s = "Communication:\\n"	
					local entries = {}
					local entry = {name = "", call = "", freq = "",radio = ""}
					local  u = 1
						-- miguel21 modification M34.i  3 frequency bands
						
					--PACKAGE_freq
					entry = {name = "", call = "", freq = "",radio = ""}
					if Tplayer.EWR_freq and Tplayer.EWR_call then																--if the player is on intercept
						if camp.radio[sideName][2] then																			--player has a second radio
							entry["name"] = "Package: "
							entry["call"] = ""
							-- entry["freq"] = Tplayer.group.frequency .. " MHz"
							entry["freq"] = string.format("%07.3f", Tplayer.group.frequency).. " MHz"
						else																									--player has only one radio
							entry["name"] = "GCI: "
							entry["call"] = Tplayer.EWR_call
							-- entry["freq"] = Tplayer.group.frequency .. " MHz"
							entry["freq"] = string.format("%07.3f", Tplayer.group.frequency).. " MHz"
						end
					else	
						entry["name"] = "Package: "
						entry["call"] = ""
						entry["freq"] = string.format("%07.3f", Tplayer.group.frequency).. " MHz"
					end									
					if radioP[1].nbCanal > 0 and FreqCapability(Tplayer.group.frequency, radioP, 1)	 then
						table.insert(Tplayer.group["units"][u]["Radio"][1]["channels"], tonumber(Tplayer.group.frequency))		--insert frequency to radio channel table
						entry["radio"] = "Radio 1 / Channel " .. #Tplayer.group["units"][u]["Radio"][1]["channels"] + MC
					end
					if entry.name ~= "" then
						entries[#entries+1] = entry
					end
						
						
					--ATC_freq
					entry = {name = "", call = "", freq = "",radio = ""}
					local ATC_freq = tonumber(db_airbases[Tplayer.pack[Tplayer.role][Tplayer.flight].base].ATC_frequency)									
					entry["name"] = "ATC: "
					entry["call"] = Tplayer.pack[Tplayer.role][Tplayer.flight].base
					entry["freq"] = string.format("%07.3f", ATC_freq).. " MHz"
					
					if camp.radio[sideName][2] and radioP[2] and radioP[2].nbCanal > 0 and FreqCapability(ATC_freq, radioP, 2) then																				--player has a second radio
						table.insert(Tplayer.group["units"][u]["Radio"][2]["channels"], ATC_freq)								--insert frequency to radio 2 channel table																-- Miguel21 M04.c : ajout d'une troisieme radio
						entry["radio"] = "Radio 2 / Channel " .. #Tplayer.group["units"][u]["Radio"][2]["channels"]						
						if camp.radio[sideName][3] and radioP[3] and radioP[3].nbCanal > 0 and FreqCapability(ATC_freq, radioP, 3) then
							table.insert(Tplayer.group["units"][u]["Radio"][3]["channels"], ATC_freq)							--insert frequency to radio 3 channel table
							entry["radio"] = " & Radio 3 / Channel " .. #Tplayer.group["units"][u]["Radio"][3]["channels"]
						end					
					elseif radioP[1].nbCanal > 0 and FreqCapability(ATC_freq, radioP, 1) then
						table.insert(Tplayer.group["units"][u]["Radio"][1]["channels"], ATC_freq)								--insert frequency to radio 1 channel table
						entry["radio"] = "Radio 1 / Channel " .. #Tplayer.group["units"][u]["Radio"][1]["channels"] + MC							
					end
					if entry.name ~= "" then
						entries[#entries+1] = entry
					end
					
					
					--AWACS_freq					
					for call,freq in pairs(AWACS_freq) do
						entry = {name = "", call = "", freq = "",radio = ""}
						local freqAWACS = tonumber(freq)
						entry["name"] = "AWACS: "
						entry["call"] = call
						entry["freq"] = string.format("%07.3f", freqAWACS).. " MHz"
						
						if camp.radio[sideName][2] and radioP[2] and radioP[2].nbCanal > 0 and FreqCapability(freqAWACS, radioP, 2) then
							table.insert(Tplayer.group["units"][u]["Radio"][2]["channels"], freqAWACS)							--insert freqAWACSuency to radio 2 channel table
							entry["radio"] = "Radio 2 / Channel " .. #Tplayer.group["units"][u]["Radio"][2]["channels"]									
							if camp.radio[sideName][3] and radioP[3] and radioP[3].nbCanal > 0 and FreqCapability(freqAWACS, radioP, 3) then
								table.insert(Tplayer.group["units"][u]["Radio"][3]["channels"], freqAWACS)						--insert frequency to radio 3 channel table
								entry["radio"] = "Radio 3 / Channel " .. #Tplayer.group["units"][u]["Radio"][3]["channels"]
							end
						elseif radioP[1].nbCanal > 0 and FreqCapability(freqAWACS, radioP, 1) then
							table.insert(Tplayer.group["units"][u]["Radio"][1]["channels"], freqAWACS)							--insert frequency to radio 1 channel table
							entry["radio"] = "Radio 1 / Channel " .. #Tplayer.group["units"][u]["Radio"][1]["channels"]  + MC
						end
						
						if entry.name ~= "" then
							entries[#entries+1] = entry
						end					
					end

					
					
					
					--EWR_freq
					for ni,EWR_freq_ in ipairs(EWR_freq) do
						for call,freq in pairs(EWR_freq_) do
							entry = {name = "", call = "", freq = "",radio = ""}
							local freqEWR = tonumber(freq.freq)
							entry["name"] = "EWR: "
							entry["call"] = call
							entry["freq"] = string.format("%07.3f", freqEWR).. " MHz"
							
							-- miguel21 modification M34.h																				--player has a second radio -- Miguel21 modification EWR M07.g
							if camp.radio[sideName][2] and radioP[2] and radioP[2].nbCanal > 0 and FreqCapability(freqEWR, radioP, 2) then	
								table.insert(Tplayer.group["units"][u]["Radio"][2]["channels"], freqEWR)								--insert frequency to radio 2 channel table -- Miguel21 modification EWR M07.g
								entry["radio"] = "Radio 2 / Channel " .. #Tplayer.group["units"][u]["Radio"][2]["channels"]							
								if camp.radio[sideName][3] and radioP[3] and radioP[3].nbCanal > 0 and FreqCapability(freqEWR, radioP, 3) then	
									table.insert(Tplayer.group["units"][u]["Radio"][3]["channels"], freqEWR)							--insert frequency to radio 3 channel table -- Miguel21 M04.c : ajout d'une troisieme radio
									entry["radio"] = "Radio 3 / Channel " .. #Tplayer.group["units"][u]["Radio"][3]["channels"]
								end
							elseif radioP[1].nbCanal > 0 and FreqCapability(freqEWR, radioP, 1) then
								table.insert(Tplayer.group["units"][u]["Radio"][1]["channels"], freqEWR)								--insert frequency to radio 1 channel table
								entry["radio"] = "Radio 1 / Channel " .. #Tplayer.group["units"][u]["Radio"][1]["channels"]  + MC
							end
							if entry.name ~= "" then
								entries[#entries+1] = entry
							end						
						end
					end

					--tanker_freq												
					if refuelable then 	
						for call,freq in pairs(tanker_freq) do
							entry = {name = "", call = "", freq = "",radio = ""}
							local freqTanker = tonumber(freq)
							entry["name"] = "Tanker: "
							entry["call"] = call
							entry["freq"] = string.format("%07.3f", freqTanker).. " MHz"
							
							if Tplayer.group["units"][u]["Radio"] and #Tplayer.group["units"][u]["Radio"][1]["channels"] < radioP[1].nbCanal and radioP[1].nbCanal > 0 and FreqCapability(freqTanker, radioP, 1) then
								if camp.radio[sideName][2] and radioP[2]  then
									table.insert(Tplayer.group["units"][u]["Radio"][2]["channels"], freqTanker)					--insert frequency to radio 2 channel table
									entry["radio"] = "Radio 2 / Channel " .. #Tplayer.group["units"][u]["Radio"][2]["channels"] 								
									if camp.radio[sideName][3] and radioP[3] then
										table.insert(Tplayer.group["units"][u]["Radio"][3]["channels"], freqTanker)				--insert frequency to radio 3 channel table
										entry["radio"] = "Radio 3 / Channel " .. #Tplayer.group["units"][u]["Radio"][3]["channels"]
									end
								else																							--player has only one radio
									table.insert(Tplayer.group["units"][u]["Radio"][1]["channels"], freqTanker)					--insert frequency to radio 1 channel table
									entry["radio"] = "Radio 1 / Channel " .. #Tplayer.group["units"][u]["Radio"][1]["channels"] + MC
								end
							end
							if entry.name ~= "" then
								entries[#entries+1] = entry
							end	
						end	
					end
					
					
					--CAP_freq
					for call,freq in pairs(CAP_freq) do
						entry = {name = "", call = "", freq = "",radio = ""}																												--CAP_freq frequency
						local freqCAP = tonumber(freq)
						entry["name"] = "CAP: "
						entry["call"] = call
						entry["freq"] = string.format("%07.3f", freqCAP).. " MHz"
							
						if  Tplayer.group["units"][u]["Radio"] and #Tplayer.group["units"][u]["Radio"][1]["channels"] < radioP[1].nbCanal and radioP[1].nbCanal > 0 and FreqCapability(freqCAP, radioP, 1) then
							table.insert(Tplayer.group["units"][u]["Radio"][1]["channels"], freqCAP)															--insert frequency to radio 1 channel table
							entry["radio"] = "Radio 1 / Channel " .. #Tplayer.group["units"][u]["Radio"][1]["channels"]	+ MC 
							
							if camp.radio[sideName][3] and radioP[3] and #Tplayer.group["units"][u]["Radio"][3]["channels"] < radioP[3].nbCanal and FreqCapability(freqCAP, radioP, 3) then
								table.insert(Tplayer.group["units"][u]["Radio"][3]["channels"], freqCAP)														--insert frequency to radio 3 channel table
								entry["radio"] = "Radio 1 / Channel " .. #Tplayer.group["units"][u]["Radio"][3]["channels"]	
							end
						elseif camp.radio[sideName][2] and radioP[2] and radioP[2].nbCanal > 0 and #Tplayer.group["units"][u]["Radio"][2]["channels"] < radioP[2].nbCanal and FreqCapability(freqCAP, radioP, 2) then
							table.insert(Tplayer.group["units"][u]["Radio"][2]["channels"], freqCAP)															--insert frequency to radio 1 channel table
							entry["radio"] = "Radio 2 / Channel " .. #Tplayer.group["units"][u]["Radio"][2]["channels"]
						end
						if entry.name ~= "" then
							entries[#entries+1] = entry
						end	
					end					
					
					--ATC_Divert_freq
					for call,freq in pairs(ATC_Divert_freq) do
						
						entry = {name = "", call = "", freq = "",radio = ""}
						local ATC_freq = tonumber(freq)	
							
						if ATC_freq and ATC_freq ~= nil then 
							entry["name"] = "Divert: "
							entry["call"] = call
							entry["freq"] = string.format("%07.3f", ATC_freq).. " MHz"
							
							if camp.radio[sideName][2] and radioP[2] and radioP[2].nbCanal > 0 and #Tplayer.group["units"][u]["Radio"][2]["channels"] < radioP[2].nbCanal and FreqCapability(ATC_freq, radioP, 2) then				--player has a second radio										
								table.insert(Tplayer.group["units"][u]["Radio"][2]["channels"], ATC_freq)													--insert frequency to radio 2 channel table
								entry["radio"] = "Radio 2 / Channel " .. #Tplayer.group["units"][u]["Radio"][2]["channels"]
								
								if camp.radio[sideName][3] and radioP[3] and radioP[3].nbCanal > 0 and FreqCapability(ATC_freq, radioP, 3)	 then
									table.insert(Tplayer.group["units"][u]["Radio"][3]["channels"], ATC_freq)												--insert frequency to radio 3 channel table
									entry["radio"] = "Radio 3 / Channel " .. #Tplayer.group["units"][u]["Radio"][3]["channels"]
								end																																--player has only one radio
							elseif Tplayer.group["units"][u]["Radio"] and  #Tplayer.group["units"][u]["Radio"][1]["channels"] < radioP[1].nbCanal and radioP[1].nbCanal > 0 and FreqCapability(ATC_freq, radioP, 1) then																																		--player has only one radio
								table.insert(Tplayer.group["units"][u]["Radio"][1]["channels"], ATC_freq)													--insert frequency to radio 1 channel table
								entry["radio"] = "Radio 1 / Channel " .. #Tplayer.group["units"][u]["Radio"][1]["channels"]  + MC
							end
							if entry.name ~= "" then
								entries[#entries+1] = entry
							end
						end
					end
					
					--All_freq
					for call,freq in pairs(All_freq) do						
						entry = {name = "", call = "", freq = "",radio = ""}																		--All frequency
						local freqALL = tonumber(freq.freq)
						entry["name"] = freq.task..": "
						entry["call"] = call
						entry["freq"] = freqALL.. " MHz"
						entry["freq"] = string.format("%07.3f", freqALL).. " MHz"
						
						if camp.radio[sideName][2] and radioP[2] and radioP[2].nbCanal > 0 and #Tplayer.group["units"][u]["Radio"][2]["channels"] < radioP[2].nbCanal and FreqCapability(freqALL, radioP, 2) then				--player has a second radio										
							table.insert(Tplayer.group["units"][u]["Radio"][2]["channels"], freqALL)													--insert frequency to radio 2 channel table
							entry["radio"] = "Radio 2 / Channel " .. #Tplayer.group["units"][u]["Radio"][2]["channels"]
							
							if camp.radio[sideName][3] and radioP[3] and radioP[3].nbCanal > 0 and FreqCapability(freqALL, radioP, 3)	 then
								table.insert(Tplayer.group["units"][u]["Radio"][3]["channels"], freqALL)												--insert frequency to radio 3 channel table
								entry["radio"] = "Radio 3 / Channel " .. #Tplayer.group["units"][u]["Radio"][3]["channels"]
							end																																--player has only one radio
						elseif Tplayer.group["units"][u]["Radio"] and  #Tplayer.group["units"][u]["Radio"][1]["channels"] < radioP[1].nbCanal and radioP[1].nbCanal > 0 and FreqCapability(freqALL, radioP, 1) then																																		--player has only one radio
							table.insert(Tplayer.group["units"][u]["Radio"][1]["channels"], freqALL)													--insert frequency to radio 1 channel table
							entry["radio"] = "Radio 1 / Channel " .. #Tplayer.group["units"][u]["Radio"][1]["channels"]  + MC
						end
						if entry.name ~= "" then
							entries[#entries+1] = entry
						end	
					end

					s = s .."\\n"

					local struct = {																			--list entries that are making up the navigaion overview
						[1] = {
							lookup = "name",																	--lookup in the player.waypoints table
							header = "Name",																		--name which should be displayer in the list header
							str_length = 4,																		--string length of largest entry of this type (default the string length of the header)
						},
						[2] = {
							lookup = "call",
							header = "Call",
							str_length = 4,
						},
						[3] = {
							lookup = "freq",
							header = "Freq",
							str_length = 4,
						},
						[4] = {
							lookup = "radio",
							header = "Radio",
							str_length = 5,
						},
					}
					
					local TabHeader = {}
					for t = 1, #struct do
						for e = 1, #entries do																		--iterate through all entries
							for header, value in pairs(entries[e]) do															--if this is not the last entry of the waypoint, add spaces to the next entry	
								if header == struct[t].lookup then
									local str_length =  string.len(tostring(value)) + 3		--calculate number of spaces that need to be added for alignement (string length of largest entry of same type + 3 - length of current entry = number of spaces)
									if not  TabHeader[header] then TabHeader[header] = str_length end										
									if str_length > TabHeader[header] then
										-- print("DC_B passe 05 Header "..header)
										TabHeader[header] = str_length
									end
								end
							end
						end
					end

					--build the list header
					for e = 1, #entries do	
						for t = 1, #struct do																		--iterate through all entries							
							local entry
							if struct[t].lookup == "name" then
								entry = entries[e][struct[t].lookup]
							elseif struct[t].lookup == "call" then 
								entry = entries[e][struct[t].lookup]								
							elseif struct[t].lookup == "freq" then 
								entry = entries[e][struct[t].lookup]	
							elseif struct[t].lookup == "radio" then 
								entry = entries[e][struct[t].lookup]
							end
							s = s .. tostring(entry)
							local space = TabHeader[struct[t].lookup] + 0 - string.len(tostring(entry))				--calculate number of spaces that need to be added for alignement (string length of largest entry of same type + 3 - length of current entry = number of spaces)
							for n = 1, space * 1.0 do														
								s = s .. " "																		--add 1.5 spaces for every missing letter
							end								
						end
						s = s .. "\\n"
						ScratchpadCom = s
					end						
					briefing[sideName] = briefing[sideName] .. s .. "\\n\\n"

					-- Miguel21 Modification M15 info catapulte/pont dans briefing	
					local tabNam = {}	
					s = ""
					if placePA then
						for side , pPA in pairs(placePA) do
							if sideName == side then																	--if camp.player.side == side then
								for base , Tmn in pairs(pPA) do
									if base == Tplayer.pack[Tplayer.role][Tplayer.flight].base then 
										s = s..tostring(base).." Takeoff time on the platform at ...\\n"
										for sec, name in pairsByKeys(Tmn) do
											if tabNam[name] ~= true then
												catTime = camp.time + sec 
												s = s.." "..FormatTime(catTime, "hh:mm").. " - "..tostring(name).."\\n"
												tabNam[name] = true
											end
										end
									end
								end
							end
						end

					briefing[sideName] = briefing[sideName] .. s .. "\\n\\n"



-- local Scratchpad = StringToTxt(s)

-- local camp_str = Scratchpad
-- local campFile = io.open("Debug/briefing_DC_B.txt", "w")										--open targetlist file
-- campFile:write(camp_str)																		--save new data
-- campFile:close()

					end
					
					
					
					--Meteo
					local s = "Meteo:\\n"																				--overview of Weather
					
					local remain = math.ceil((camp.weather.zoneEnd - ((camp.day - 1) * 86400 + camp.time)) / 3600)		--hours until end of weather zone
					local duration = math.ceil((camp.weather.zoneEnd - camp.weather.zoneStart) / 3600)					--duration of the weather zone in hours
					local passed = 100 / duration * remain																--percentage of zone passage
					
					if camp.weather.zone == "high" then
						if mission.weather["enable_fog"] == false then
							s = s .. "Good flying weather due to influence of a high pressure system in theater of operations"
							if remain < 6 then
								s = s .. ". Change of general weather situation imminent. "
							elseif remain < 25 then
								s = s .. ", expected to remain in effect for next " .. remain .. " hours. "
							elseif remain < 48 then
								s = s .. ", expected to remain dominant for another day. "
							else
								s = s .. ", expected to remain dominant for next " .. math.floor(remain / 24) .. " days. "
							end
						else
							s = s .. "Ground fog conditions. "
						end
						
					elseif camp.weather.zone == "low front cold" then
						s = s .. "Low pressure system dominating theater of operations. Currently poor flying weather due to passage of cold front. Weather improvement expected within next " .. remain .. " hours. "
						
					elseif camp.weather.zone == "low front warm" then
						s = s .. "Low pressure system dominating theater of operations. "
						if passed < 50 then
							s = s .. "Currently increasingly poor flying weather due to the passage of warm front. Expected to clear up after " .. remain .. " hours. "
						else
							s = s .. "Weather expected to deteriorate within next " .. remain .. " hours due to approach of warm front. "
						end
						
					elseif camp.weather.zone == "low sector cold" then
						s = s .. "Low pressure system dominating theater of operations. Currently fair flying weather in cold sector"
						if remain < 6 then
							s = s .. ". Change of general weather situation imminent. "
						elseif remain < 25 then
							s = s .. ", expected to remain in effect for next " .. remain .. " hours. "
						elseif remain < 48 then
							s = s .. ", expected to remain stable for another day. "
						else
							s = s .. ", expected to remain stable for next " .. math.floor(remain / 24) .. " days. "
						end
						
					elseif camp.weather.zone == "low sector warm" then
						s = s .. "Low pressure system dominating theater of operations. Currently fair flying weather in warm sector"
						if remain < 6 then
							s = s .. ". Change of general weather situation imminent. "
						elseif remain < 25 then
							s = s .. ", expected to remain in effect for next " .. remain .. " hours. "
						elseif remain < 48 then
							s = s .. ", expected to remain stable for another day. "
						else
							s = s .. ", expected to remain stable for next " .. math.floor(remain / 24) .. " days. "
						end
						
					end
					
					briefing[sideName] = briefing[sideName] .. s .. "\\n\\n" .. METAR


					--Assign briefing text to mission file
					if sideName == "blue" then
						mission.descriptionBlueTask = briefing[sideName]
					else
						mission.descriptionRedTask = briefing[sideName]
					end

					-- Miguel21 modification M41.b 	Sratchpad written in the Sratchpad file, if this modul is installed
					local ScratchpadPath = "../../../../../../Config/ScratchpadConfig.lua"
					-- local ScratchpadPath = "../../../../../../Config/ScratchpadConfig.lua"
					local TestPath = io.open(ScratchpadPath, "r")
-- print("DC_B ScratchpadPath "..tostring(ScratchpadPath))
-- print("DC_B TestPath "..tostring(TestPath))
				
					-- Miguel21 modification M41 	Scratchpad written in the Sratchpad file, if this modul is installed
					if mission_ini.WrittenOnScratchpadMod and TestPath ~= nil then 
						io.close(TestPath)
						local ScratBriefTXT = StringToTxtBrief(briefing[sideName])
						dofile(ScratchpadPath)
						local ScratFil = io.open(ScratchpadPath, "w")
						config.content = ScratBriefTXT
						local ScratConfig = "config = " .. TableSerialization(config, 0)
						ScratFil:write(ScratConfig)
						ScratFil:close()
					end
				end
			end
		end
	end
end




-- ajoute les images permanentes du briefing

for side, file in pairs(pictureBrief) do
	if side == "blue" then 			
		for nb, filename in ipairs(file) do	
			table.insert(BriefingImagesB, filename)
		end
	elseif side == "red" then
		for nb, filename in ipairs(file) do
			table.insert(BriefingImagesR, filename)
		end
	end
end

 -- ajoute les images du target selectionné
if target_picture["blue"] then
	for TP_n, target_picture in ipairs(target_picture.blue) do
		filename = target_picture    
		table.insert(BriefingImagesB, filename)
	end
elseif target_picture["red"] then
	for TP_n, target_picture in ipairs(target_picture.red) do
		filename = target_picture    
		table.insert(BriefingImagesR, filename)
	end
end
	
for n = 1, #BriefingImagesB do
	mapResource["ResKey_BriefingImage_" .. BriefingImagesB[n]] = BriefingImagesB[n]     --define key in mapResource file
	table.insert(mission.pictureFileNameB, "ResKey_BriefingImage_" .. BriefingImagesB[n])  --add picture to blue briefing
end

for n = 1, #BriefingImagesR do
	mapResource["ResKey_BriefingImage_" .. BriefingImagesR[n]] = BriefingImagesR[n]     --define key in mapResource file
	table.insert(mission.pictureFileNameR, "ResKey_BriefingImage_" .. BriefingImagesR[n])  --add picture to red briefing
end


-- local Scratchpad = StringToTxt(mission.descriptionBlueTask)
-- local camp_str = Scratchpad
-- local campFile = io.open("Debug/briefingBlue_DC_B.txt", "w")										--open targetlist file
-- campFile:write(camp_str)																		--save new data
-- campFile:close()


-- local Scratchpad = StringToTxt(mission.descriptionRedTask)
-- local camp_str = Scratchpad
-- local campFile = io.open("Debug/briefingRed_DC_R.txt", "w")										--open targetlist file
-- campFile:write(camp_str)																		--save new data
-- campFile:close()


-- print("DC B descriptionBlueTask2 "..mission.descriptionBlueTask)
-- print()
-- print()
-- print("DC B descriptionRedTask2 "..mission.descriptionRedTask)

-- _affiche(mission.pictureFileNameB, "DC B mission.pictureFileNameB")
-- print()
-- print()
-- _affiche(mission.pictureFileNameR, "DC B mission.pictureFileNameR")

