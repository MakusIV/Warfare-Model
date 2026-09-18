--To run the campaign triggers. Evaluate trigger conditions, run trigger actions and append briefing text
--Initiated by MAIN_NextMission.lua
------------------------------------------------------------------------------------------------------- 
-- Miguel Fichier Revision  M40
------------------------------------------------------------------------------------------------------- 

-- Miguel21 modification M40 : Template Active GroundGroup moving front
-- Miguel21 modification M19.f : RepairGround
-- Miguel21 modification M11 : Multiplayer

if not versionDCE then versionDCE = {} end
versionDCE["DC_CheckTriggers.lua"] = "1.3.6"

-- =====================  Marco implementation ==================================
local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua")
-- NOTE MARCO: prova a caricarlo usando require(".. . .. . .. .ScriptsMod."versionPackageICM..".UTIL_Log.lua")
-- NOTE MARCO: https://forum.defold.com/t/including-a-lua-module-solved/2747/2
log.level = LOGGING_LEVEL
log.outfile = LOG_DIR .. "LOG_DC_CheckTriggers." .. camp.mission .. ".log" 
local local_debug = true -- local debug   
log.info("Start")
-- =====================  End Marco implementation ==================================


BriefingImagesB = {}                                         --reset stockImage
BriefingImagesR = {}                                         --reset stockImage

----- campaign flags -----
if camp.flag == nil then
	camp.flag = {}
end
local old_flag = deepcopy(camp.flag)												--copy campaign flags, so that modifications of flags do not affect condition of subsequent campaign triggers in same mission


----- functions to return campaign information to build trigger conditions -----
Return = {}

	--return the time of day in seconds
	function Return.Time()
		return camp.time
	end
	
	--return day of month
	function Return.Day()
		return camp.date.day
	end
	
	--return month as number
	function Return.Month()
		return camp.date.month
	end
	
	--return year
	function Return.Year()
		return camp.date.year
	end
	
	--return mission number
	function Return.Mission()
		return camp.mission
	end
	
	--return campagn flag
	function Return.CampFlag(arg)
		return old_flag[arg]													--return old_flag (unmodified by other campaign trigger in same mission)
	end
	
	--return if air unit is active
	function Return.AirUnitActive(name)
		for side_name,side in pairs(oob_air) do									--iterate through sides in oob_air
			for unit_n,unit in pairs(side) do									--iterate through units in side
				if unit.name == name then										--unit found
					if unit.inactive == true then
						return false
					else
						return true
					end
				end
			end
		end
	end
	
	--return number of ready aircraft for an air unit
	function Return.AirUnitReady(name)
		for side_name,side in pairs(oob_air) do									--iterate through sides in oob_air
			for unit_n,unit in pairs(side) do									--iterate through units in side
				if unit.name == name then										--unit found
					return unit.roster.ready									--return number of ready aircraft
				end
			end
		end
	end
	
	--return number of ready + damaged aircraft for an air unit
	function Return.AirUnitAlive(name)
		for side_name,side in pairs(oob_air) do									--iterate through sides in oob_air
			for unit_n,unit in pairs(side) do									--iterate through units in side
				if unit.name == name then										--unit found
					return unit.roster.ready + unit.roster.damaged				--return number of ready and damaged aircraft
				end
			end
		end
	end
	
	--return air unit base
	function Return.AirUnitBase(name)
		for side_name,side in pairs(oob_air) do									--iterate through sides in oob_air
			for unit_n,unit in pairs(side) do									--iterate through units in side
				if unit.name == name then										--unit found
					return unit.base											--return base
				end
			end
		end
	end
	
	--return air unit player
	function Return.AirUnitPlayer(name)
		for side_name,side in pairs(oob_air) do									--iterate through sides in oob_air
			for unit_n,unit in pairs(side) do									--iterate through units in side
				if unit.name == name then										--unit found
					return unit.player											--return player
				end
			end
		end
	end
	
	--return alive percentage of target
	function Return.TargetAlive(targetname)
		for side_name,side in pairs(targetlist) do								--iterate through sides in targetlist
			for target_name,target in pairs(side) do							--iterate through targets in side
				if target_name == targetname then								--target found
					return target.alive											--return alive percentage of target
				end
			end
		end
	end
	
	--return vehicle/ship units dead
	function Return.UnitDead(unitname)
		for sidename,side in pairs(oob_ground) do								--iterate through sides in ground OOB
			for c = 1, #side do													--iterate through countries in side
				for typename,typetable in pairs(side[c]) do						--iterate through country table content
					if typename == "vehicle" or typename == "ship" then			--for vehciles or ships
						for group_n,group in pairs(typetable.group) do			--iterate through groups
							for unit_n,unit in pairs(group.units) do			--iterate through units
								if unit.name == unitname then					--unit found
									if unit.dead then							--unit is dead
										return true								--return true
									end
								end
							end
						end
					end
				end
			end
		end
		return false
	end
	
	--return vehicle/ship group hidden status
	function Return.GroupHidden(groupname)
		for sidename,side in pairs(oob_ground) do								--iterate through sides in ground OOB
			for c = 1, #side do													--iterate through countries in side
				for typename,typetable in pairs(side[c]) do						--iterate through country table content
					if typename == "vehicle" or typename == "ship" then			--for vehciles or ships
						for group_n,group in pairs(typetable.group) do			--iterate through groups
							if group.name == groupname then						--group is found
								return group.hidden								--return group hiden status
							end
						end
					end
				end
			end
		end
	end
	
	--return vehicle/ship group probability status
	function Return.GroupProbability(groupname)
		for sidename,side in pairs(oob_ground) do								--iterate through sides in ground OOB
			for c = 1, #side do													--iterate through countries in side
				for typename,typetable in pairs(side[c]) do						--iterate through country table content
					if typename == "vehicle" or typename == "ship" then			--for vehciles or ships
						for group_n,group in pairs(typetable.group) do			--iterate through groups
							if group.name == groupname then						--group is found
								local prob = group.probability
								if prob == nil then								--if the value is nil
									prob = 1									--then probability of spawn is 1
								end
								return prob										--return group probability of spawn value
							end
						end
					end
				end
			end
		end
	end
	
	--return boolean whether ship group is in polygon
	function Return.ShipGroupInPoly(GroupName, PolyZonesTable)
		for coal_name,coal in pairs(oob_ground) do												--go through sides(red/blue)	
			for country_n,country in ipairs(coal) do											--go through countries
				if country.ship then															--country has ships
					for group_n,group in ipairs(country.ship.group) do							--go through groups
						if group.name == GroupName then											--group found
							local point = {														--local table to store group position
								x = group.x,
								y = group.y
							}
							if #PolyZonesTable == 1 then										--if polygon has just one point
								if point.x == Refpoint[PolyZonesTable[1]].x and point.y == Refpoint[PolyZonesTable[1]].y then		--group is exactly on point
									return true
								else
									return false
								end
							elseif #PolyZonesTable == 2 then									--if polygon has two points
								local p1 = Refpoint[PolyZonesTable[1]]
								local p2 = Refpoint[PolyZonesTable[2]]
								if (point.x >= p1.x and point.x <= p2.x) or (point.x >= p2.x and point.x <= p1.x) then		--point.x is between x-component of p1 and p2
									if (point.y >= p1.y and point.y <= p2.y) or (point.y >= p2.y and point.y <= p1.y) then	--point.y is between y-component of p1 and p2
										local dx = p2.x - p1.x
										local dy = p2.y - p1.y
										if math.floor(dx / (point.x - p1.x) * 1000) == math.floor(dy / (point.y - p1.y) * 1000) then		--point is on line defined by p1 and p2
											return true
										else
											return false
										end
									end
								end					
							else																--if polygon has more than two points
								local poly = {}													--table to store x-y coordinates of all points of polygon
								for n = 1, #PolyZonesTable do
									poly[n] = Refpoint[PolyZonesTable[n]]
								end
								return CheckPointInPoly(point, poly)							--checks if point is in polygon, returns true or false
							end
						end
					end
				end
			end
		end
	end


----- functions to buld trigger actions -----
Action = {}

	--tactical directive action
	function Action.TacticalDirective(side, tactic) 
		airDirective(side, tactic) -- DC_Tactical
	end
	
	--void action
	function Action.None()
	end
	
	--add briefing text
	function Action.Text(arg, clear)
		if clear then
			briefing_status = ""												--clear briefing text from previous mission instances
			briefing_text = briefing_text .. arg .. "\\n\\n"					--add trigger text to briefing text of this mission instance with double new line
		else
			briefing_text = briefing_text .. arg .. "\\n\\n"					--add trigger text to briefing text of this mission instance with double new line
		end
	end
	
	--add briefing text
	function Action.TextPlayMission(arg)
		briefing_text_playable = briefing_text_playable .. arg .. "\\n\\n"		--add trigger text to briefing text of this mission only if it is playable
	end
	
	--add briefing picture
	function Action.AddImage(filename, side)
		if side == "blue"  then
			table.insert(BriefingImagesB, filename)									--add filename to briefing images table, will be added to mission file when this gets created
		elseif side == "red"  then
			table.insert(BriefingImagesR, filename)
		elseif side == "all" or side == "" or side == nil then
			table.insert(BriefingImagesB, filename)
			table.insert(BriefingImagesR, filename)
		end
	end
	
	--set campagn flag to value
	function Action.SetCampFlag(n, value)
		camp.flag[n] = value
	end
	
	--add or subtract to campaign flag
	function Action.AddCampFlag(n, add)
		camp.flag[n] = camp.flag[n] + add
	end
	
	--end campaign
	function Action.CampaignEnd(arg)
		EndCampaign = arg
	end
	
	--set target active/inactive
	function Action.TargetActive(targetName, state)
		for sidename, side in pairs(targetlist) do
			for tname, target in pairs(side) do
				if tname == targetName then
					if state == true then										--state argument is true
						target.inactive = false									--make inactive false
					elseif state == false then									--state argument is false
						target.inactive = true									--make inactive true
					end
				end
			end
		end
	end
	
	--set target priority
	function Action.TargetPriority(targetName, priority)
		for sidename, side in pairs(targetlist) do
			for tname, target in pairs(side) do
				if tname == targetName then
					target.priority = priority
					break
				end
			end
		end
	end
	
	--set unit active/inactive
	function Action.AirUnitActive(unitName, state)
		for side_name,side in pairs(oob_air) do									--iterate through sides in oob_air
			for unit_n,unit in pairs(side) do									--iterate through units in side
				if unit.name == unitName then									--unit found
					if state == true then										--state argument is true
						unit.inactive = false									--make inactive false
					elseif state == false then									--state argument is false
						unit.inactive = true									--make inactive true
					end
				end
			end
		end
	end
	
	--set unit base
	function Action.AirUnitBase(unitName, baseName)
		for side_name,side in pairs(oob_air) do									--iterate through sides in oob_air
			for unit_n,unit in pairs(side) do									--iterate through units in side
				if unit.name == unitName then									--unit found
					unit.base = baseName										--set new airbase for unit
				end
			end
		end
	end
	
	--set unit playable
	function Action.AirUnitPlayer(unitName, state)
		for side_name,side in pairs(oob_air) do									--iterate through sides in oob_air
			for unit_n,unit in pairs(side) do									--iterate through units in side
				if unit.name == unitName then									--unit found
					unit.player = state											--set new playable state for unit
				end
			end
		end
	end
	
	--send reinforcement aircraft from one unit to another
	function Action.AirUnitReinforce(sourceName, destName, destNumber)
		local sourceUnit
		local destUnit
		local destSide
		for side_name,side in pairs(oob_air) do									--iterate through sides in oob_air
			for unit_n,unit in pairs(side) do									--iterate through units in side
				if unit.name == sourceName then									--source unit found
					sourceUnit = unit											--point source oob unit table to variable
				elseif unit.name == destName then								--desitination unit found
					destUnit = unit												--point destination oob unit table to variable	
					destSide = side_name										--store side
				end
			end
		end
		if destUnit.roster.ready < destNumber then								--destination ready number is below nominal number
			if sourceUnit.roster.ready > 0 then									--source unit has ready aircraft
				local maxtrans = destNumber - destUnit.roster.ready				--maximal number of transferable aircraft
				if maxtrans > 4 then											--limit maxtrans to 4 aircraft
					maxtrans = 4
				end
				if maxtrans > sourceUnit.roster.ready then
					maxtrans = sourceUnit.roster.ready
				end
				local trans = math.random(1, maxtrans)							--set random number of actual transferable aircraft
				destUnit.roster.ready = destUnit.roster.ready + trans			--transfer aircraft
				sourceUnit.roster.ready = sourceUnit.roster.ready - trans		--transfer aircraft
				local text
				if trans == 1 then
					text = "" .. trans .. " replacement " .. ReplaceTypeName(destUnit.type) .. " has been transferred from " .. sourceName .. " to " .. destName .. ".\\n\\n"	--text to be added to briefing/oob
				else
					text = "" .. trans .. " replacement " .. ReplaceTypeName(destUnit.type) .. " have been transferred from " .. sourceName .. " to " .. destName .. ".\\n\\n"	--text to be added to briefing/oob
				end
				if destSide == "blue" then										--side is blue
					briefing_oob_text_blue = briefing_oob_text_blue .. text		--add to blue briefing oob text
				elseif destSide == "red" then									--side is red
					briefing_oob_text_red = briefing_oob_text_red .. text		--add to red briefing oob text
				end
			end
		end
	end
	
	--repair damaged aircraft in all air units
	function Action.AirUnitRepair(arg)
		local s = {}
		if arg == "blue" then														--repair only blue side
			s["blue"] = true
		elseif arg == "red" then													--repair only red side
			s["red"] = true
		else																		--repair both sides
			s["blue"] = true
			s["red"] = true
		end
		for side_name,side in pairs(oob_air) do										--iterate through sides in oob_air
			if s[side_name] then													--this side can repair aircraft
				for unit_n,unit in pairs(side) do									--iterate through units in side
					local repair = 0												--number of repaired aircraft un this round
					for n = 1, unit.roster.damaged do								--iterate through all damaged aircraft
						if math.random(1,20) == 1 then								--5% chance of repair
							repair = repair + 1
						end
					end
					if repair > 0 then												--if aircraft are repaird in this round
						unit.roster.damaged = unit.roster.damaged - repair
						unit.roster.ready = unit.roster.ready + repair
						local text
						if repair == 1 then
							text = "" .. repair .. " damaged " .. ReplaceTypeName(unit.type) .. " from ".. unit.name .. " has been repaired and returned back to service.\\n\\n"	--text to be added to briefing/oob
						else
							text = "" .. repair .. " damaged " .. ReplaceTypeName(unit.type) .. " from ".. unit.name .. " have been repaired and returned back to service.\\n\\n"	--text to be added to briefing/oob
						end
						if side_name == "blue" then									--side is blue
							briefing_oob_text_blue = briefing_oob_text_blue .. text	--add to blue briefing oob text
						elseif side_name == "red" then								--side is red
							briefing_oob_text_red = briefing_oob_text_red .. text	--add to red briefing oob text
						end
					end
				end
			end
		end
	end
	
	
	-- Miguel21 modification M19.f : Repair Ground
	function Action.GroundUnitRepair()

		for side_name,targetlistSide in pairs(targetlist) do
			local groundside = "red"					--get the opposing side if the group side
			if side_name == "red" then
				groundside = "blue"
			end
			
			for target_name, target in pairs(targetlistSide) do		--Iterat through all targets
				if target.alive then
					if target.elements   then 
						for e = 1, #target.elements do												--Iterate through elements of target
							local temp_dead = nil
							local temp_dead_last = nil
							local temp_CheckDay = nil
							local prob = 0
							local forcedReAlive = false												-- M19.f
							
							if target.elements[e].dead then 
								temp_dead = target.elements[e].dead
								temp_dead_last = target.elements[e].dead_last
								temp_CheckDay = target.elements[e].CheckDay	

							end
							
							if  (target.alive < 100 and target.alive >= campMod.RepairMinimumDestroyed ) then
								if  target.elements[e].dead  then
									if target.elements[e].CheckDay then
										if  camp.day > target.elements[e].CheckDay then
											 
											name = string.upper(target_name)
											if target.probRepair then prob = target.probRepair
											elseif (string.find(name,"SA") or string.find(name,"HAWK") or string.find(name,"RAPIER") or string.find(name,"EWR"))
												then prob = campMod.RepairSAM 
											elseif string.find(name,"AIRBASE") then prob = campMod.RepairAirbase
											elseif string.find(name,"STATION") then prob = campMod.RepairStation
											elseif string.find(name,"BRIDGE") then prob = campMod.RepairBridge
											else prob = campMod.Repair
											end
											
											local test_prob = math.random(1,100)

											-- si on ressucite l'�l�ment
											if prob >= test_prob then
												forcedReAlive = true
												temp_dead = nil
												temp_dead_last = false
												temp_CheckDay = nil
												
												text = "" .. target.elements[e].name .. " from ".. target_name .. " have been repaired and returned back to service.\\n\\n"
												
												if Debug.AfficheSol then
													print("DC CT Resurrection: "..target_name .. " "..target.elements[e].name)
													print("DC CT "..text)
												end
												
												
											
												
												if side_name == "blue" then									--side is blue
													briefing_oob_text_blue = briefing_oob_text_blue .. text	--add to blue briefing oob text
												elseif side_name == "red" then								--side is red
													briefing_oob_text_red = briefing_oob_text_red .. text	--add to red briefing oob text
												end
												

												target.elements[e].dead = nil
												target.elements[e].CheckDay = nil
												target.alive = math.floor(target.alive + (1/#target.elements *100))
												 if target.alive > 100 then  target.alive = 100 end
															
												target.dead_last = math.floor(target.dead_last -  (1/#target.elements *100))
												 if target.dead_last < 0 then  target.dead_last = 0 end
		
											else -- sinon on met � jour la date de check pour y revenir seulement un jour apres
												temp_CheckDay = camp.day
												target.elements[e].CheckDay = temp_CheckDay					-- pour mettre � jour les cible scenary qui ne sont pas dans oob_ground
											end
										end
									end
								end
							end

							if forcedReAlive then						 
								local endfunction = false
								for c = 1, #oob_ground[groundside] do													--iterate through countries in side
									for typename,typetable in pairs(oob_ground[groundside][c]) do						--iterate through country table content
										if typename == "vehicle" or typename == "ship" then			--for vehciles or ships
											for group_n,group in pairs(typetable.group) do			--iterate through groups	
												for unit_n,unit in pairs(group.units) do			--iterate through groups	
													if  target.elements[e].name == unit.name then
													
														if Debug.AfficheSol then
															if temp_dead then print(" temp_dead "..tostring(temp_dead))  end
															if temp_dead_last then print(" temp_dead_last "..tostring(temp_dead_last))  end
															if temp_CheckDay then print(" temp_CheckDay "..tostring(temp_CheckDay))  end
														end
														
														 group.units[unit_n]['dead'] = temp_dead
														 group.units[unit_n]['dead_last'] = temp_dead_last
														 group.units[unit_n].CheckDay = temp_CheckDay

														endfunction = true
														break
													end
													if endfunction then  break end
												end
												if endfunction then  break end	
											end
											if endfunction then  break end	
										end
										if endfunction then break end	
									end
									if endfunction then  break end
								end
							end
						end

					end
				end
			end	
		end
	end
	
	--add ground target intel updates to briefing
	function Action.AddGroundTargetIntel(side)
		if MissionInstance == 1 then											--ground target intel updates are only added in first mission instance (to avoid duplication)
			for target_name,target in pairs(targetlist[side]) do				--iterate through targets in side
			
				if target.expand then											--target should be displayed with expanded elements
					if target.elements then										--target has elements
						for e = 1, #target.elements do							--iterate through elements
							local element_name = target.elements[e].name
							if camp.ShipDamagedLast and camp.ShipDamagedLast[element_name] then				--ship has taken damage during last mission
								if camp.ShipHealth[element_name] == 0 then									--ship is sunk
									briefing_text = briefing_text .. "Intel Update: " .. element_name .. " has been sunk.\\n\\n"
								elseif camp.ShipHealth[element_name] < 33 then								--ship has less than 33% health
									briefing_text = briefing_text .. "Intel Update: " .. element_name .. " has been heavily damaged.\\n\\n"
								elseif camp.ShipHealth[element_name] < 66 then								--ship has less than 66% health
									briefing_text = briefing_text .. "Intel Update: " .. element_name .. " has been moderately damaged.\\n\\n"
								elseif camp.ShipHealth[element_name] < 100 then								--ship has less than 100% health
									briefing_text = briefing_text .. "Intel Update: " .. element_name .. " has been lightly damaged.\\n\\n"
								end
							end
						end
					end
				end
				
				if target.alive and target.dead_last > 0 and target.hidden ~= true then			--ground target was hit in last mission and should not be hidden
					if target.alive == 0 then									--target is dead
						briefing_text = briefing_text .. "Intel Update: " .. target_name .. " has been destroyed.\\n\\n"
					else														--target is still alive
						briefing_text = briefing_text .. "Intel Update: " .. target_name .. " has been reduced to " .. target.alive .. "%.\\n\\n"
					end
				end
			end
		end
	end
	
	--change vehicle/ship group hidden status
	function Action.GroupHidden(groupname, hidden_bool)
		for sidename,side in pairs(oob_ground) do								--iterate through sides in ground OOB
			for c = 1, #side do													--iterate through countries in side
				for typename,typetable in pairs(side[c]) do						--iterate through country table content
					if typename == "vehicle" or typename == "ship" then			--for vehciles or ships
						for group_n,group in pairs(typetable.group) do			--iterate through groups
							if group.name == groupname then						--group is found
								group.hidden = hidden_bool						--change group hidden status in ground OOB
								break
							end
						end
					end
				end
			end
		end
	end
	
	--change vehicle/ship group probability status
	--due to the way stats are reset for a new playrun upon completing a FirstMission, groups probability changed by trigger in first mission will not be carried over to second mission! Repeat trigger on second mission or use the trigger from mission 2 on only for flawless function.
	function Action.GroupProbability(groupname, prob_val)
		for sidename,side in pairs(oob_ground) do								--iterate through sides in ground OOB
			for c = 1, #side do													--iterate through countries in side
				for typename,typetable in pairs(side[c]) do						--iterate through country table content
					if typename == "vehicle" or typename == "ship" then			--for vehciles or ships
						for group_n,group in pairs(typetable.group) do			--iterate through groups
							if group.name == groupname then						--group is found
								group.probability = prob_val					--change group probability status in ground OOB
								break
							end
						end
					end
				end
			end
		end
	end
	
	--move vehicle group to refpoint
	--due to the way stats are reset for a new playrun upon completing a FirstMission, groups moved by trigger in first mission will not be carried over to second mission! Repeat trigger on second mission or use the trigger from mission 2 on only for flawless function.
	function Action.GroupMove(GroupName, ZoneName)
		for coal_name,coal in pairs(oob_ground) do								--go through sides(red/blue)	
			for country_n,country in ipairs(coal) do							--go through countries
				if country.vehicle then											--country has vehicles
					for group_n,group in ipairs(country.vehicle.group) do		--go through groups
						if GroupName == group.name then							--ship group found
							local newPoint = Refpoint[ZoneName]					--x-y coordinates of new group position
							local dx = group.x - newPoint.x						--delta x
							local dy = group.y - newPoint.y						--delta y
							group.x = newPoint.x								--new group position
							group.y = newPoint.y
							group.route.points[1].x = newPoint.x
							group.route.points[1].y = newPoint.y
							for u = 1, #group.units do
								group.units[u].x = group.units[u].x - dx		--new individual unit position
								group.units[u].y = group.units[u].y - dy
							end
						end
					end
				end
			end
		end
	end
	
	--move vehicle group relative to another group
	--due to the way stats are reset for a new playrun upon completing a FirstMission, groups moved by trigger in first mission will not be carried over to second mission! Repeat trigger on second mission or use the trigger from mission 2 on only for flawless function.
	function Action.GroupSlave(GroupName, master, bearing, distance)
		for coal_name,coal in pairs(oob_ground) do								--go through sides(red/blue)	
			for country_n,country in ipairs(coal) do							--go through countries
				if country.vehicle then											--country has vehicles
					for group_n,group in ipairs(country.vehicle.group) do		--go through groups
						if GroupName == group.name then							--ship group found
							
							--find master group and get master  x-y coordinates
							for m_coal_name,m_coal in pairs(oob_ground) do									--go through sides(red/blue)	
								for m_country_n,m_country in ipairs(m_coal) do								--go through countries
									if m_country.vehicle then												--country has vehicles
										for m_group_n,m_group in ipairs(m_country.vehicle.group) do			--go through groups
											if m_group.name == master then
												local newPoint = {}
												newPoint.x = m_group.x + math.cos(math.rad(bearing)) * distance		--update slave position relative to master position
												newPoint.y = m_group.y + math.sin(math.rad(bearing)) * distance		--update slave position relative to master position
												local dx = group.x - newPoint.x								--delta x
												local dy = group.y - newPoint.y								--delta y
												group.x = newPoint.x										--new group position
												group.y = newPoint.y
												group.route.points[1].x = newPoint.x
												group.route.points[1].y = newPoint.y
												for u = 1, #group.units do
													group.units[u].x = group.units[u].x - dx				--new individual unit position
													group.units[u].y = group.units[u].y - dy
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
	end
	
	--assign and run a movement mission to a ship group: move group along waypoints/polygons at cruise speed and optionally patrol at last polygon at patrol speed
	--GroupName is a string with the name of the ship group to get a mission
	--WPtable is a set of trigger zone names acting as waypoints for the ship to follow. WPtable is an array of multiple waypoints (example: {"ZoneName1", ZoneName2"} ).
	--Each individual waypoint can in turn consist of an array of two or more trigger zones, creating polygons where the waypont is placed within randomly (example: {{"Zone1-1", "Zone 1-2", "Zone1-3"}, {"Zone2-1", "Zone2-2", "Zone2-3"}} ).
	--The first waypoint in a WPtable can be nil to use the ship group's current position as first waypoint.
	--CruiseSpeed is the speed in m/s at which the ship group will follow the route.
	--PatrolSpeed is the speed in m/s at which the ship group will randomly patrol a polygon at the end of the route. Ships won't patrol at the end of the route if the PatrolSpeed is nil or zero or if the last waypoint is a single point only (no polygon).
	--StartTime is the campaign time in seconds (time since campaign start) at which the mission was assigned. It is used to control progress along the route across multiple missions of the campaign. If nil, then current campaign time us used automatically.
	function Action.ShipMission(GroupName, WPtable, CruiseSpeed, PatrolSpeed, StartTime)
		for coal_name,coal in pairs(oob_ground) do								--go through sides(red/blue)	
			for country_n,country in ipairs(coal) do							--go through countries
				if country.ship then											--country has ships
					for group_n,group in ipairs(country.ship.group) do			--go through groups
						if GroupName == group.name then							--ship group found
							
							if StartTime == nil then							--if StartTime is nil
								StartTime = (camp.day - 1) * 86400 + camp.time	--use current time in seconds since campaign start
							end
						
							camp.ShipMissions[GroupName] = {					--store ship mission in camp for subsequent executions during later missions
								WPtable = WPtable,
								CruiseSpeed = CruiseSpeed,
								PatrolSpeed = PatrolSpeed,
								StartTime = StartTime
							}
							ShipGroupMovement(GroupName, WPtable, CruiseSpeed, PatrolSpeed, StartTime)	--exectue ship mission
						end
					end
				end
			end
		end
	end
	
	--TemplateActive
	function Action.TemplateActive(TabFile)				
		local file
		function FindUnit(Group_name, category)
			for Oside_name, Oside in pairs(oob_ground) do																--iterate through sides
				for Ocountry_n, Ocountry in pairs(Oside) do															--iterate through countries
					if Ocountry[category] then																			--country has vehicles
						for g = 1, #Ocountry[category].group do							
							if Ocountry[category].group[g].name  == Group_name then
								return true
							end
						end
					end
				end
			end			
		end
		
		function mouvedXY(Unit, category)
			for Oside_name, Oside in pairs(oob_ground) do																--iterate through sides
				for Ocountry_n, Ocountry in pairs(Oside) do															--iterate through countries
					if Ocountry[category] then																			--country has vehicles
						for g = 1, #Ocountry[category].group do							
							for u = 1, #Ocountry[category].group[g].units do											--iterate through units								
								if Ocountry[category].group[g].units[u].name == Unit.name then
									Ocountry[category].group[g].units[u].x = Unit.x
									Ocountry[category].group[g].units[u].x = Unit.x																			
									print("DcCT mouvedXY passe 05 name "..tostring(Ocountry[category].group[g].units[u].name))								
								end														
							end
						end
					end
				end
			end			
		end
		
		-- cree une table identifiant des noms de pays
		local CountryId = {}
		for side_name, side in pairs(oob_ground) do																--iterate through sides
			for country_n, country in pairs(side) do															--iterate through countries
				if country.name then
					if not CountryId[country.name] then CountryId[country.name] = country_n end

				end
			end
		end

		if type(TabFile) == "table" then		
			file =  TabFile[math.random(1, #TabFile)]
		else 
			file = TabFile
		end
		
		-- print("DcCT TemplateActive(file) "..tostring(file))
		print("DcCT TemplateActive(file) "..tostring(file))
		_affiche(file)
		
		dofile("Templates/"..file)
		tmp_ground = {}
		tmp_ground["blue"] = deepcopy(staticTemplate.coalition.blue.country)											--copy mission data
		tmp_ground["red"] = deepcopy(staticTemplate.coalition.red.country)												--copy mission data
		
		tmp_dictionary = deepcopy(staticTemplate.localization.DEFAULT)
		
		--store group and unit names in oob_ground instead of pointers to dict table
		for side_name, side in pairs(tmp_ground) do																--iterate through sides
			for country_n, country in pairs(side) do															--iterate through countries
				if country.vehicle then																			--country has vehicles
					for g = 1, #country.vehicle.group do															--iterate through vehicle groups	
						local groupname = tmp_dictionary[country.vehicle.group[g].name]								--find groupname in dictionary table			
						local found = FindUnit(groupname, "vehicle")
						country.vehicle.group[g].name = groupname												--give group the actual groupname instead of the pointer to the dictionary table						
						
						for u = 1, #country.vehicle.group[g].units do											--iterate through units
							local unitname = tmp_dictionary[country.vehicle.group[g].units[u].name]					--find unitname in dictionary table
							country.vehicle.group[g].units[u].name = unitname									--give unit the actual unitname instead of the pointer to the dictionary table							
							if found then
								mouvedXY(country.vehicle.group[g].units[u], "vehicle" )
							end
						end							
							
						if not found then
							-- print("DcCT passe bb not resultat")
							if not oob_ground[side_name][CountryId[country.name]]["vehicle"] then oob_ground[side_name][CountryId[country.name]]["vehicle"] = {} end						
							table.insert(oob_ground[side_name][CountryId[country.name]]["vehicle"]["group"], country.vehicle.group[g])			
						end
					end
				end
				if country.ship then																			--country has ships
					for g = 1, #country.ship.group do															--iterate through ship groups	
						local groupname = tmp_dictionary[country.ship.group[g].name]								--find groupname in dictionary table			
						local found = FindUnit(groupname, "ship")
						country.ship.group[g].name = groupname												--give group the actual groupname instead of the pointer to the dictionary table						
						
						for u = 1, #country.ship.group[g].units do											--iterate through units
							local unitname = tmp_dictionary[country.ship.group[g].units[u].name]					--find unitname in dictionary table
							country.ship.group[g].units[u].name = unitname									--give unit the actual unitname instead of the pointer to the dictionary table							
							if found then
								mouvedXY(country.ship.group[g].units[u], "ship" )
							end
						end							
							
						if not found then
							-- print("DcCT passe bb not resultat")
							if not oob_ground[side_name][CountryId[country.name]]["ship"] then oob_ground[side_name][CountryId[country.name]]["ship"] = {} end						
							table.insert(oob_ground[side_name][CountryId[country.name]]["ship"]["group"], country.ship.group[g])			
						end
					end
				end
				if country.static then																			--country has static objects
					for g = 1, #country.static.group do															--iterate through static groups	
						local groupname = tmp_dictionary[country.static.group[g].name]								--find groupname in dictionary table			
						local found = FindUnit(groupname, "static")
						country.static.group[g].name = groupname												--give group the actual groupname instead of the pointer to the dictionary table						
						
						for u = 1, #country.static.group[g].units do											--iterate through units
							local unitname = tmp_dictionary[country.static.group[g].units[u].name]					--find unitname in dictionary table
							country.static.group[g].units[u].name = unitname									--give unit the actual unitname instead of the pointer to the dictionary table							
							if found then
								mouvedXY(country.static.group[g].units[u], "static" )
							end
						end							
							
						if not found then
							print("DcCT passe bb not resultat, TABLE.INSERT ")
							if not oob_ground[side_name][CountryId[country.name]]["static"] then oob_ground[side_name][CountryId[country.name]]["static"] = {} end						
							table.insert(oob_ground[side_name][CountryId[country.name]]["static"]["group"], country.static.group[g])

							print("DcCT "..file.." "
							..tostring(country.static.group[g].name).." UnitName: "
							..tostring(country.static.group[g].units[1].name).." Type: "
							..tostring(country.static.group[g].units[1].type))
						
							
						end
					end
				end
			end
		end
	end
	
----- run campaign triggers -----

--define variables to persist across multiple mission generation attempts
if briefing_status == nil then													--if briefing status string does not exist yet it must be created
	briefing_status = ""														--text string to be added to briefing
	briefing_oob_text_red = ""													--text string to be added to next briefing (red repair and reinforcements)
	briefing_oob_text_blue = ""													--text string to be added to next briefing (blue repair and reinforcements)
end
if BriefingImagesB == nil then
	BriefingImagesB = { }															--global table to hold information about briefing images to be added to miz mission file
end
if BriefingImagesR == nil then
  BriefingImagesR = { }                             --global table to hold information about briefing images to be added to miz mission file
end

briefing_text = ""																--briefing text to be added this mission instance
briefing_text_playable = ""														--briefing text to be added only if this mission instance results in a playable mission

--go through campaign triggers
for trigger_name,trigger in pairs(camp_triggers) do								--iterate through triggers
	if trigger.active then														--trigger is active
		local condition = loadstring("if " .. trigger.condition .." then return true end")	--make a function from the string condition
		if condition() then														--if the trigger condition is true
			if type(trigger.action) == "table" then								--multiple actions
				for i,action in ipairs(trigger.action) do
					local f = loadstring(action)()								--run the trigger action
				end
			else																--single action
				local f = loadstring(trigger.action)()							--run the trigger action
			end
			if trigger.once then												--trigger should only fire once
				trigger.active = false											--set trigger inactive
			end
		end
	end
end

--add date and time header for this mission instance briefing text
if briefing_text ~= "" then														--brefing text from this mission instance exists and should be added to briefing_status text
	briefing_status = briefing_status .. FormatDate(camp.date.day, camp.date.month, camp.date.year) .. ", " .. FormatTime(camp.time, "hh:mm") .. ":\\n\\n" .. briefing_text		--add date and time, then add briefing text of this mission instance
end

--add pictures cumulated in all mission generations attempts
-- for n = 1, #BriefingImagesB do
	-- mapResource["ResKey_BriefingImage_" .. BriefingImagesB[n]] = BriefingImagesB[n]			--define key in mapResource file
	-- table.insert(mission.pictureFileNameB, "ResKey_BriefingImage_" .. BriefingImagesB[n])	--add picture to blue briefing
-- end
-- for n = 1, #BriefingImagesR do
  -- mapResource["ResKey_BriefingImage_" .. BriefingImagesR[n]] = BriefingImagesR[n]     --define key in mapResource file
  -- table.insert(mission.pictureFileNameR, "ResKey_BriefingImage_" .. BriefingImagesR[n])  --add picture to red briefing
-- end