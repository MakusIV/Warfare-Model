--To evaluate the DCS debrief.log and update the campaign status files
--Initiated by DEBRIEF_Master.lua
-------------------------------------------------------------------------------------------------------

if not versionDCE then 
	versionDCE = {} 
end

               -- VERSION --

versionDCE["DEBRIEF_StatsEvalutation.lua"] = "OB.1.0.0"

---------------------------------------------------------------------------------------------------------
-- Old_Boy rev. OB.1.0.0: implements logging code and (very) little optimization
-- Old_Boy rev. OB.0.0.1: implements supply line sistems (logistics)
-- Miguel21 modification M19.f : Repair SAM
---------------------------------------------------------------------------------------------------------

local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua")
local log_level = LOGGING_LEVEL -- "traceVeryLow" --
local function_log_level = log_level
log.activate = false
log.level = log_level 
log.outfile = LOG_DIR .. "LOG_DEBRIEF_StatEvalutation." .. camp.mission .. ".log" 
local local_debug = false -- local debug   
local active_log = false
log.debug("Start")

-- ================== Local Function ================================================


--function to add new clients to clientstats
local function AddClient(name)
	local nameFunction = "function AddClient(" .. name .. "): "    
	log.debug("Start " .. nameFunction)		

	if clientstats[name] == nil then	
		log.trace(nameFunction .. "client has no previous stats entry, create a new clientstats table")															--if client has no previous stats entry, create a new one
		clientstats[name] = {
			kills_air = 0,
			kills_ground = 0,
			kills_ship = 0,
			friendly_kills_air = 0,
			friendly_kills_ground = 0,
			friendly_kills_ship = 0,
			mission = 0,
			crash = 0,
			eject = 0,
			dead = 0,
			score_last = { --stats current mission
				kills_air = 0,
				kills_ground = 0,
				kills_ship = 0,
				friendly_kills_air = 0,
				friendly_kills_ground = 0,
				friendly_kills_ship = 0,
				mission = 0,
				crash = 0,
				eject = 0,
				dead = 0
			}
		}
	end
	log.debug("End " .. nameFunction)																		
end


--function to check if a kill loss is attributed to the player package
local function AddPackstats(unitname, event)
	local nameFunction = "function AddPackstats(" .. unitname .. ", " .. event .. "): "    
	log.debug("Start " .. nameFunction .. "check if a loss is attributed to the player package")														
	
	if packstats[unitname] then
		log.trace(nameFunction .. "unitname is in packstats, increments packstats[" .. unitname .. "].".. event)																																	--aircraft was part of the package
		
		if event == "kill_air" then
			packstats[unitname].kills_air = packstats[unitname].kills_air + 1
			log.trace(nameFunction .. "packstats[" .. unitname .. "] exist. Event == kills_air, update packstats[" .. unitname .. "].kills_air; " .. packstats[unitname].kills_air)
		
		elseif event == "kill_ground" then
			packstats[unitname].kills_ground = packstats[unitname].kills_ground + 1
			log.trace(nameFunction .. "packstats[" .. unitname .. "] exist. Event == kills_ground, update packstats[" .. unitname .. "].kills_ground; " .. packstats[unitname].kills_ground)
		
		elseif event == "kill_ship" then
			packstats[unitname].kills_ship = packstats[unitname].kills_ship + 1
			log.trace(nameFunction .. "packstats[" .. unitname .. "] exist. Event == kills_ship, update packstats[" .. unitname .. "].kills_ship; " .. packstats[unitname].kills_ship)
		
		elseif event == "friendly_kill_air" then
			packstats[unitname].friendly_kills_air = packstats[unitname].friendly_kills_air + 1
			log.trace(nameFunction .. "packstats[" .. unitname .. "] exist. Event == friendly_kills_air, update packstats[" .. unitname .. "].friendly_kills_air; " .. packstats[unitname].friendly_kills_air)
		
		elseif event == "friendly_kill_ground" then
			packstats[unitname].friendly_kills_ground = packstats[unitname].friendly_kills_ground + 1
			log.trace(nameFunction .. "packstats[" .. unitname .. "] exist. Event == friendly_kills_ground, update packstats[" .. unitname .. "].friendly_kills_ground; " .. packstats[unitname].friendly_kills_ground)
		
		elseif event == "friendly_kill_ship" then
			packstats[unitname].friendly_kills_ship = packstats[unitname].friendly_kills_ship + 1
			log.trace(nameFunction .. "packstats[" .. unitname .. "] exist. Event == friendly_kills_ship, update packstats[" .. unitname .. "].friendly_kills_ship; " .. packstats[unitname].friendly_kills_ship)
		
		elseif event == "lost" then
			packstats[unitname].lost = packstats[unitname].lost + 1
			log.trace(nameFunction .. "packstats[" .. unitname .. "] exist. Event == lost, update packstats[" .. unitname .. "].lost; " .. packstats[unitname].lost)
		end	
	end
	log.debug("End " .. nameFunction)														
end

local function setUnitDeadLast(group_obj, group_type, side_name, country_name)

	for group_n,group in pairs(group_obj) do --groups table (number array)
		log.debug("Start reset" .. group_type .. " unit.dead_last: ".. side_name .. ", country: " .. country_name .. ", group: ".. group.name .. " - id: " .. group.groupId .. " - name: " .. group.name .. "   =======================================================")														

		for unit_n,unit in pairs(group.units) do --units table (number array)	
			log.trace("Reset" .. group_type .." unit.dead_last: unit_n: " ..unit_n ..  "-id: " .. unit.unitId .. "-name: " .. unit.name .. "-type: " .. unit.type)														
			unit.dead_last = false --reset unit died in last mission
		end
		log.debug("End reset" .. group_type .. " unit.dead_last   =======================================================")														
	end
end
-- ==================================================================================




--reset oob_air table last mission stats -----------------------------------------
log.info("Reset oob_air table units last mission stats: kills, lost, damaged and ready")

for side_name,side in pairs(oob_air) do														--iterate through all sides
	log.debug("Start reset unit.score_last: ".. side_name .. "   =======================================================")														
	
	for unit_n,unit in pairs(side) do--iterate through all air units
		log.trace("Reset unit.score_last: ".. side_name .. ", unit_n: " .. unit_n .. " - name: " .. unit.name .. " - type: " .. unit.type .. " - number(qty), lost, damaged, ready: " .. unit.number .. ", " .. unit.roster.lost .. ", " .. unit.roster.damaged .. ", " .. unit.roster.ready)	--iterate through all air units
		unit.score_last = {
			kills_air = 0,
			kills_ground = 0,
			kills_ship = 0,
			lost = 0,
			damaged = 0,
			ready = 0
		}
	end
	log.debug("End reset unit.score_last: ".. side_name .. "   =======================================================")														
end

--reset oob_ground table last mission stats ----------------------------------------
log.info("Reset oob_ground table last mission stat: dead state = false")

for side_name,side in pairs(oob_ground) do --side table(red/blue)											

	for country_n,country in pairs(side) do	--country table (number array)

		if country.vehicle then	--if country has vehicles
			setUnitDeadLast(country.vehicle.group, "vehicle", side_name, country.name)						
		end

		if country.static then --if country has static objects
			setUnitDeadLast(country.static.group, "static", side_name, country.name)			
		end
		
		if country.ship then --if country has ships
			setUnitDeadLast(country.static.group, "ship", side_name, country.name)					
		end
	end
end

--reset elements in targetlist table
log.info("Reset targetlist element state: dead state = false")

for side_name,side in pairs(targetlist) do	--iterate through targetlist
	
	for target_name,target in pairs(side) do --iterate through targets		
		
		if target.elements and target.elements[1].x then --if the target has subelements and is a scenery object target (element has x coordinate)
			log.debug("Start reset targetlist element.dead_last: ".. side_name .. ", target: " .. target_name .. "   =======================================================")														
			
			for element_n,element in pairs(target.elements) do								--iterate through target elements
				log.trace("Reset element.dead_last: element_n: " .. element_n .. " - element: " .. element.name)														
				element.dead_last = false													--reset element died in last mission
			end
			log.debug("End reset targetlist element.dead_last   =======================================================")																	
		end
	end
end


--reset client last mission stats
log.info("Reset score_last in clientstats table (kills, mission, crash, eject and dead)   =======================================================")														

for client_name, client in pairs(clientstats) do
	log.debug("Actual score for " .. client_name .. ", mission: " .. client.mission .. ", kills air-ground-ship, mission, eject, crash, dead: " .. client.kills_air .. ", " .. client.kills_ground .. ", " .. client.kills_ship .. ", " .. client.eject .. ", " .. client.crash .. ", " .. client.dead)														
	log.debug("Reset score_last for " .. client_name .. ", mission: " .. client.mission .. ", score_last(kills air-ground-ship, mission, eject, crash, dead: " .. client.score_last.kills_air .. ", " .. client.score_last.kills_ground .. ", " .. client.score_last.kills_ship .. ", " .. client.score_last.mission .. ", " .. client.score_last.eject .. ", " .. client.score_last.crash .. ", " .. client.score_last.dead)														
	client.score_last = {
		kills_air = 0,
		kills_ground = 0,
		kills_ship = 0,
		friendly_kills_air = 0,
		friendly_kills_ground = 0,
		friendly_kills_ship = 0,
		mission = 0,
		crash = 0,
		eject = 0,
		dead = 0
	}
end
log.info("End reset clientstats")	

local client_control = {} --local table to store which client controls which unit
local hit_table = {} --local table to store who was the last hitter to hit a unit
local health_table = {}	--local table to store health of a hit unit
local client_hit_table = {} --local table to store if a client has hit a unit
log.debug("Created local client_control table: to store which client controls which unit")	
log.debug("Created hit_table: to store who was the last hitter to hit a unit")	
log.debug("Created local client_hit_table: table to store if a client has hit a unit")	


--track stats for player package
log.info("Start track stats for player package =======================================================")														
packstats = {}

for role_name, role in pairs(camp.player.pack) do	--iterate through roles in player package

	for flight_n, flight in pairs(role) do 			--iterate through flights

		for n = 1, flight.number do
			local unitname = "Pack " .. camp.player.pack_n .. " - " .. flight.name .. " - " .. flight.task .. " " .. flight_n .. "-" .. n
			log.debug(" create packstats for unitname: " .. unitname)																				
			packstats[unitname] = {
				kills_air = 0,
				kills_ground = 0,
				kills_ship = 0,
				lost = 0,
				friendly_kills_air = 0,
				friendly_kills_ground = 0,
				friendly_kills_ship = 0,
			}
		end
	end
end
log.info("End track stats for player package =======================================================")														

--prepare client stats
log.info("Start prepare client stats =======================================================")														

for e = 1, #events do																					--iterate through all events
	if events[e].initiatorPilotName then		--event is by a client
		AddClient(events[e].initiatorPilotName) --check if exist clientstats table if not create one new
		client_control[events[e].initiator] = events[e].initiatorPilotName --store which unit name (initiator) is controlled by client (initiatorPilotName)
		log.debug("Event: " .. events[e].type .. " is by a client player: " .. events[e].initiatorPilotName .. ", store which unit name (initiator) is controlled by cliend (initiatorPilotName):" )
		log.debug("client_control[" .. events[e].initiator .. "] = " .. events[e].initiatorPilotName)
	end
end
log.traceVeryLow("\n\nevents table:\n" .. inspect(events) .. "\n\n")
log.info("End prepare client stats =======================================================")														

--evaluate log events
log.info("Start evaluate log events =====================================================")														

for e = 1, #events do	
	--review all events for stats updates
	if events[e].type == "hit" then																		--hit events		
		hit_table[events[e].target] = events[e].initiator												--store who hits a target (subsequent hits overwrite previous hits)
		health_table[events[e].target] = events[e].health												--store health of the target
		client_hit_table[events[e].target] = client_control[events[e].initiator]						--store client name that has hit a unit (stores nil  if hitter is not a client)				
		log.debug("event["..e.."] == hit, store hit in tables - events[e].target: " .. events[e].target)																
		
		if hit_table[events[e].target] then
			log.trace("hit_table[" .. events[e].target .."] = " .. hit_table[events[e].target])																
		end	

		if health_table[events[e].target] then
			log.trace("health_table[" .. events[e].target .."] = " .. health_table[events[e].target])																
		end	

		if client_hit_table[events[e].target] then
			log.info("client (player) had an event hit: hit this target: " .. events[e].target)
			log.trace("client_hit_table[" .. events[e].target .."] = " .. client_hit_table[events[e].target])																
		end	
		
		
	elseif events[e].type == "crash" then		
		log.debug("event["..e.."] == crash. Iterated oob_air for search initiator air unit in oob_air for storing stats")																
		--oob loss update for crashed aircraft
		local crash_side																				--local variable to store the side of the crashed aircraft
		
		for killer_side_name,killer_side in pairs(oob_air) do											--iterate through all sides
			
			for killer_unit_n,killer_unit in pairs(killer_side) do										--iterate through all air units
				
				if string.find(events[e].initiator, " " .. killer_unit.name .. " ", 1, true) then		--if the crashed aircraft name is part of air unit name
					log.debug("found initiator: " .. events[e].initiator .. " in oob_air: " .. killer_unit.name)
					crash_side = killer_side_name														--store side of the crashed aircraft
					killer_unit.roster.lost = killer_unit.roster.lost + 1								--increase loss counter of air unit
					killer_unit.score_last.lost = killer_unit.score_last.lost + 1						--increase loss counter for this mission of air unit
					
					if killer_unit.roster.ready > 0 then 
						killer_unit.roster.ready = killer_unit.roster.ready - 1								--decrease number of ready aircraft of air unit
					end

					if killer_unit.score_last.ready > 0 then 
						killer_unit.score_last.ready = killer_unit.score_last.ready - 1 --era +1 errore?    --decrease number of ready aircraft for this mission of air unit
					end
					log.debug("event["..e.."].initiator = oob_air killer_unit.name = " .. killer_unit.name .. ", increments killer_unit.roster.lost and killer_unit.score_last.lost (" .. killer_unit.roster.lost .. ", " .. killer_unit.score_last.lost .. ") - decrease killer_unit.roster.ready and killer_unit.score_last.ready (" .. killer_unit.roster.ready .. ", " ..  killer_unit.score_last.ready .. ")")
					AddPackstats(events[e].initiator, "lost")											--check if loss was in player package					
			
					--client stats for crashes
					if client_control[events[e].initiator] then --if crashed aircraft is a client
						log.info("client (player) had an event crash")											
						clientstats[client_control[events[e].initiator]].crash = clientstats[client_control[events[e].initiator]].crash + 1	--store crash for client
						clientstats[client_control[events[e].initiator]].score_last.crash =  1			--store crash for client
						log.debug("update crash in clientstats: clientstats[" .. client_control[events[e].initiator] .. "].crash = " .. clientstats[client_control[events[e].initiator]].crash .. ", clientstats[" .. client_control[events[e].initiator] .. "].score_last.crash = " .. clientstats[client_control[events[e].initiator]].score_last.crash)
					end
					log.debug("crashed aircraft name is part of air unit name -> break looping unit")		
					break -- exit from the loop because the crashed aircraft name is part of air unit name. No more store stats for other unit??
				end
			end
		end
		
		log.debug("iterate oob_air for kill update for crashed aircraft (if crashed aircraft have kill")																
		--oob kill update for crashed aircraft
		-- nota Old_Boy: questa iterazione è già presente sopra (255). Valutare se possibil inserire
		-- il codice interno nelle iterazioni suddette.
		for killer_side_name,killer_side in pairs(oob_air) do											--iterate through all sides
			
			for killer_unit_n,killer_unit in pairs(killer_side) do										--iterate through all air units
				
				if hit_table[events[e].initiator] ~= nil then											--check if the crashed aircraft has a hit entry
					log.debug("crashed air unit have hit in hit_table - hit_table[" .. events[e].initiator .. "] = " .. hit_table[events[e].initiator])
					
					if string.find(hit_table[events[e].initiator], " " .. killer_unit.name .. " ", 1, true) then			--if the hitting unit is part of air unit name
						log.debug("found initiator: " .. events[e].initiator .. " in oob_air: " .. killer_unit.name)
						
						if crash_side ~= killer_side_name then --make sure that hitting unit and crashed aircraft are not on same side (friendly fire is not awarded as kill)
							log.debug("iniziator (hitting killer) unit have different side of the crashed air unit - crash_side: " .. (crash_side or "nil") .. " ~= killer_side_name: " .. (killer_side_name or "nil"))							
							killer_unit.score.kills_air = killer_unit.score.kills_air + 1				--award air kill to air unit
							killer_unit.score_last.kills_air = killer_unit.score_last.kills_air + 1		--increase kill counter for this mission of air unit						
							log.debug("store stats for killer unit - killer_unit.name = " .. killer_unit.name .. ": update killer_unit.score.kills_air and killer_unit.score_last.kills_air (" .. killer_unit.score.kills_air .. ", " .. killer_unit.score_last.kills_air .. ") - decrease killer_unit.roster.ready and killer_unit.score_last.ready (" .. killer_unit.roster.ready .. ", " ..  killer_unit.score_last.ready .. ")")
							AddPackstats(hit_table[events[e].initiator], "kill_air")					--check if kill was in player package														
							
							--client stats for kills
							if client_hit_table[events[e].initiator] then								--if crashed aircraft was hit by a client
								log.info("crashed aircraft was hit by a client (player)")											
								clientstats[client_hit_table[events[e].initiator]].kills_air = clientstats[client_hit_table[events[e].initiator]].kills_air + 1	--award air kill to client.
								clientstats[client_hit_table[events[e].initiator]].score_last.kills_air = clientstats[client_hit_table[events[e].initiator]].score_last.kills_air + 1
								log.debug("store hit in clientstats: clientstats[" .. client_hit_table[events[e].initiator] .. "].kills_air = " .. clientstats[client_hit_table[events[e].initiator]].kills_air .. ", clientstats[" .. client_hit_table[events[e].initiator] .. "].score_last.kills_air = " .. clientstats[client_hit_table[events[e].initiator]].score_last.kills_air)
							end							
						
						else --friendly kill air
							log.debug("friendly kill air, store stats for killer unit - killer_unit.name = " .. killer_unit.name .. ": update killer_unit.score.friendly_kills_air and killer_unit.score_last.friendly_kills_air () - to be implement")
							AddPackstats(hit_table[events[e].initiator], "friendly_kill_air")

							if client_hit_table[events[e].initiator] then --client's friendly air kill								--if crashed aircraft was hit by a client
								-- implements new stats
								log.debug("crashed aircraft was hit by a client (player) and have both same side - crash_side: " .. crash_side .. " ~= killer_side_name: " .. killer_side_name)
								--log.debug(" - clientstats:\n" .. inspect(clientstats) )
								clientstats[client_hit_table[events[e].initiator]].friendly_kills_air = clientstats[client_hit_table[events[e].initiator]].friendly_kills_air + 1	--award air kill to client
								clientstats[client_hit_table[events[e].initiator]].score_last.friendly_kills_air = clientstats[client_hit_table[events[e].initiator]].score_last.friendly_kills_air + 1						 
								log.debug("store hit in clientstats: clientstats[" .. client_hit_table[events[e].initiator] .. "].friendly_kills_air = " .. clientstats[client_hit_table[events[e].initiator]].friendly_kills_air .. ", clientstats[" .. client_hit_table[events[e].initiator] .. "].score_last.friendly_kills_air = " .. clientstats[client_hit_table[events[e].initiator]].score_last.friendly_kills_air)
							end
						end
					end
				end
			end
		end		
		hit_table[events[e].initiator] = nil															--once kills for the dead aircraft are awarded, remove it from the hit_table. The aircraft remaining in the hit_table after completed log evaluation are only damaged.
		log.debug("once kills for the dead aircraft are awarded, remove it from the hit_table. The aircraft remaining in the hit_table after completed log evaluation are only damaged - hit_table[" .. events[e].initiator .. "] = nil")

	elseif events[e].type == "eject" then
		--client stats for ejections
		if client_control[events[e].initiator] then														--if ejected pilot is a client
			log.info("client (player) had an event eject")	
			clientstats[client_control[events[e].initiator]].eject = clientstats[client_control[events[e].initiator]].eject + 1	--store ejection for client
			clientstats[client_control[events[e].initiator]].score_last.eject =  1						--store eject for client
			log.debug("update eject in clientstats: clientstats[" .. client_control[events[e].initiator] .. "].eject = " .. clientstats[client_control[events[e].initiator]].eject .. ", clientstats[" .. client_control[events[e].initiator] .. "].score_last.eject = " .. clientstats[client_control[events[e].initiator]].score_last.eject)
		end
		
	elseif events[e].type == "pilot dead" then
		--client stats for dead pilots
		if client_control[events[e].initiator] then																	--if dead pilot is a client
			log.info("client (player) had an event pilot dead")	
			clientstats[client_control[events[e].initiator]].dead = clientstats[client_control[events[e].initiator]].dead + 1	--store death for client
			clientstats[client_control[events[e].initiator]].score_last.dead =  1						--store dead pilot for client
			log.debug("update eject in clientstats: clientstats[" .. client_control[events[e].initiator] .. "].dead = " .. clientstats[client_control[events[e].initiator]].dead .. ", clientstats[" .. client_control[events[e].initiator] .. "].score_last.score_last.dead = " .. clientstats[client_control[events[e].initiator]].score_last.dead)
		end
		
	elseif events[e].type == "takeoff" then
		--client stats for flown missions
		if client_control[events[e].initiator] then														--if take off is by a client
			log.info("client (player) had an event takeoff")	
			
			if clientstats[client_control[events[e].initiator]].score_last.mission == 0 then			--client has no take off logged yet for this mission
				clientstats[client_control[events[e].initiator]].mission = clientstats[client_control[events[e].initiator]].mission + 1	--increase flown mission number
				clientstats[client_control[events[e].initiator]].score_last.mission = 1					--store mission for client
				log.debug("if first takeoff, update mission in clientstats: clientstats[" .. client_control[events[e].initiator] .. "].mission = " .. clientstats[client_control[events[e].initiator]].mission .. ", clientstats[" .. client_control[events[e].initiator] .. "].score_last.score_last.mission = " .. clientstats[client_control[events[e].initiator]].score_last.mission)
			end
		end
		
	elseif events[e].type == "dead" then
		log.debug("event["..e.."] == dead. Iterated oob_ground for search dead unit")																
		--ground/naval/static loss events															--iterate through all the sub-tables of the oob_ground files and try to find the matching unitId of the dead unit (vehicle/ship/static)
		for side_name,side in pairs(oob_ground) do													--side table(red/blue)											
			
			for country_n,country in pairs(side) do													--country table (number array)
				
				-- event analisys for vehicle unit
				if country.vehicle then																--if country has vehicles
					
					for group_n,group in pairs(country.vehicle.group) do								--groups table (number array)
						
						for unit_n,unit in pairs(group.units) do										--units table (number array)					
							
							if unit.unitId == tonumber(events[e].initiatorMissionID) then				--check if unitId matches initiatorMissionID (string, needs to be converted to number)
								log.info("vehicle unit.id: " .. unit.unitId .. "is dead")
								unit.dead = true														--mark unit as dead in oob_ground
								unit.dead_last = true													--mark unit as died in last mission
								unit.CheckDay = camp.day                            					--campaign date of event		 Miguel21 modification M19 : Repair SAM	
								
								--award ground kill to air unit
								if hit_table[events[e].initiator] ~= nil then														--check if dead vehicle has a hit entry
									log.debug("dead unit: " .. unit.unitId .. " have this initiator in hit_table: " .. hit_table[events[e].initiator] .. ". Iterated oob_air for search initiator air unit for storing stats")																
									
									for killer_side_name,killer_side in pairs(oob_air) do											--iterate through all sides
										
										for killer_unit_n,killer_unit in pairs(killer_side) do										--iterate through all air units
											
											if string.find(hit_table[events[e].initiator], " " .. killer_unit.name .. " ", 1, true) then	--if the hitting unit is part of air unit name
												log.debug("found initiator: " .. events[e].initiator .. " in oob_air: " .. killer_unit.name)

												if side_name ~= killer_side_name then												--make sure that hitting unit is not on same side as dead unit (friendly fire gives no kills)
													log.debug("iniziator (killer) unit have different side of the dead ground unit - side ground unit: " .. side_name .. " ~= killer_side_name: " .. killer_side_name)
													killer_unit.score.kills_ground = killer_unit.score.kills_ground + 1				--award ground kill to air unit
													killer_unit.score_last.kills_ground = killer_unit.score_last.kills_ground + 1
													log.debug("store stats for killer unit - killer_unit.name = " .. killer_unit.name .. ": update killer_unit.score.kills_ground and killer_unit.score_last.kills_ground (" .. killer_unit.score.kills_ground .. ", " .. killer_unit.score_last.kills_ground .. ")")
													AddPackstats(hit_table[events[e].initiator], "kill_ground")						--check if kill was in player package
													
													--award ground kill to client
													if client_hit_table[events[e].initiator] then									--if dead vehicle was hit by a client
														log.info("dead ground unit was hit by a client (player)")											
														clientstats[client_hit_table[events[e].initiator]].kills_ground = clientstats[client_hit_table[events[e].initiator]].kills_ground + 1							--award gound kill to client
														clientstats[client_hit_table[events[e].initiator]].score_last.kills_ground = clientstats[client_hit_table[events[e].initiator]].score_last.kills_ground + 1		--award ground kill to client
														--log.debug("store hit in clientstats: clientstats[" .. client_hit_table[events[e].initiator] .. "].kills_ground = " .. clientstats[client_hit_table[events[e].initiator]].kills_ground .. ", clientstats[" .. client_hit_table[events[e].initiator]"].score_last.kills_ground = " .. clientstats[client_control[events[e].initiator]].score_last.kills_ground)
													end
												
												else --friendly kill ground  
													log.debug("friendly kill ground, store stats for killer unit - killer_unit.name = " .. killer_unit.name .. ": update killer_unit.score.friendly_kills_ground and killer_unit.score_last.friendly_kills_ground () - to be implement")
													AddPackstats(hit_table[events[e].initiator], "friendly_kill_ground")

													if client_hit_table[events[e].initiator] then									--client's friendly fire
														log.debug("dead ground unit was hit by a client (player) and have both same side (friendly kill)  - unit side: " .. side_name .. " ~= killer_side_name: " .. killer_side_name)
														clientstats[client_hit_table[events[e].initiator]].friendly_kills_ground = clientstats[client_hit_table[events[e].initiator]].friendly_kills_ground + 1							--award gound kill to client
														clientstats[client_hit_table[events[e].initiator]].score_last.friendly_kills_ground = clientstats[client_hit_table[events[e].initiator]].score_last.friendly_kills_ground + 1		--award ground kill to client
														log.debug("store hit in clientstats: clientstats[" .. client_hit_table[events[e].initiator] .. "].friendly_kills_ground = " .. clientstats[client_hit_table[events[e].initiator]].friendly_kills_ground .. ", clientstats[" .. client_hit_table[events[e].initiator]"].score_last.friendly_kills_ground = " .. clientstats[client_control[events[e].initiator]].score_last.friendly_kills_ground)
													end
												end								
											end
										end
									end
									hit_table[events[e].initiator] = nil							--after kills are assigned, remove hit unit from hit_table
									log.debug("kills assigned for iniziator:: " .. events[e].initiator .. " deleted initiator from hit_table")															
								end
								break
							end
						end
					end
				end
				-- event evalutation for ship unit
				if country.ship then																--if country has ships

					for group_n,group in pairs(country.ship.group) do								--groups table (number array)

						for unit_n,unit in pairs(group.units) do									--units table (number array)

							if unit.unitId == tonumber(events[e].initiatorMissionID) then			--check if unitId matches initiatorMissionID (string, needs to be converted to number)								
								log.info("ship unit.id: " .. unit.unitId .. "is dead")
								unit.dead = true													--mark unit as dead in oob_ground
								unit.dead_last = true												--mark unit as died in last mission
								unit.CheckDay = camp.day                            -- ajoute la date de destruction		 Miguel21 modification M19 : Repair SAM	
								camp.ShipHealth[unit.name] = 0										--mark unit has 0 health for briefing/debriefing
								camp.ShipDamagedLast[unit.name] = true								--mark ship took damage in last mission for briefing/debriefing
								
								--award ship kill to air unit
								if hit_table[events[e].initiator] ~= nil then														--check if dead ship has a hit entry
									log.debug("dead unit: " .. unit.unitId .. " have this initiator in hit_table: " .. hit_table[events[e].initiator] .. ". Iterated oob_air for search initiator air unit for storing stats")																

									for killer_side_name,killer_side in pairs(oob_air) do											--iterate through all sides

										for killer_unit_n,killer_unit in pairs(killer_side) do										--iterate through all air units

											if string.find(hit_table[events[e].initiator], " " .. killer_unit.name .. " ", 1, true) then	--if the hitting unit is part of air unit name
												log.debug("found initiator: " .. events[e].initiator .. " in oob_air: " .. killer_unit.name)

												if side_name ~= killer_side_name then												--make sure that hitting unit is not on same side as dead unit (friendly fire gives no kills)
													log.debug("iniziator (killer) unit have different side of the dead ground unit - side ground unit: " .. side_name .. " ~= killer_side_name: " .. killer_side_name)
													killer_unit.score.kills_ship = killer_unit.score.kills_ship + 1					--award ship kill to air unit
													killer_unit.score_last.kills_ship = killer_unit.score_last.kills_ship + 1
													log.debug("store stats for killer unit - killer_unit.name = " .. killer_unit.name .. ": update killer_unit.score.kills_ship and killer_unit.score_last.kills_ship (" .. killer_unit.score.kills_ship .. ", " .. killer_unit.score_last.kills_ship .. ")")
													AddPackstats(hit_table[events[e].initiator], "kill_ship")						--check if kill was in player package
													
													--award ship kill to client
													if client_hit_table[events[e].initiator] then									--if dead ship was hit by a client
														log.info("dead ship unit was hit by a client (player)")											
														clientstats[client_hit_table[events[e].initiator]].kills_ship = clientstats[client_hit_table[events[e].initiator]].kills_ship + 1							--award ship kill to client
														clientstats[client_hit_table[events[e].initiator]].score_last.kills_ship = clientstats[client_hit_table[events[e].initiator]].score_last.kills_ship + 1		--award ship kill to client
														log.debug("store hit in clientstats: clientstats[" .. client_hit_table[events[e].initiator] .. "].kills_ship = " .. clientstats[client_hit_table[events[e].initiator]].kills_ship .. ", clientstats[" .. client_hit_table[events[e].initiator]"].score_last.kills_ship = " .. clientstats[client_control[events[e].initiator]].score_last.kills_ship)
													end
												
												else --friendly kill ship  
													log.debug("friendly kill ship, store stats for killer unit - killer_unit.name = " .. killer_unit.name .. ": update killer_unit.score.friendly_kills_ship and killer_unit.score_last.friendly_kills_ship () - to be implement")
													AddPackstats(hit_table[events[e].initiator], "friendly_kill_ship")

													if client_hit_table[events[e].initiator] then									--client's friendly fire
														log.info("dead ship unit was hit by a client (player) and have both same side (friendly kill)  - unit side: " .. side_name .. " ~= killer_side_name: " .. killer_side_name)
														clientstats[client_hit_table[events[e].initiator]].friendly_kills_ship = clientstats[client_hit_table[events[e].initiator]].friendly_kills_ship + 1							--award gound kill to client
														clientstats[client_hit_table[events[e].initiator]].score_last.friendly_kills_ship = clientstats[client_hit_table[events[e].initiator]].score_last.friendly_kills_ship + 1		--award ground kill to client
														log.debug("store hit in clientstats: clientstats[" .. client_hit_table[events[e].initiator] .. "].friendly_kills_ship = " .. clientstats[client_hit_table[events[e].initiator]].friendly_kills_ship .. ", clientstats[" .. client_hit_table[events[e].initiator]"].score_last.friendly_kills_ship = " .. clientstats[client_control[events[e].initiator]].score_last.friendly_kills_ship)
													end
												end		
											end
										end
									end
									hit_table[events[e].initiator] = nil							--after kills are assigned, remove hit unit from hit_table
									log.debug("kills assigned for iniziator:: " .. events[e].initiator .. " deleted initiator from hit_table")															
								end
								break
							end
						end
					end
				end
				-- event evalutation for static unit
				if country.static then																--if country has static objects

					for group_n,group in pairs(country.static.group) do								--groups table (number array)

						for unit_n,unit in pairs(group.units) do									--units table (number array)

							if unit.unitId == tonumber(events[e].initiatorMissionID) then			--check if unitId matches initiatorMissionID (string, needs to be converted to number)
								
								if unit.dead ~= true then											--unit is not yet dead (some static objects that are spawned in a destroyed state are logged dead at mission start, these must be excluded here)
									group.dead = true												--mark group as dead in oob_ground (static objects can be set as group.dead and spawned in a destroyed state)
									log.debug("group of static unit.id: " .. unit.unitId .. ", assign dead")

									if group.linkOffset then										--static unit was linked to a carrier										
										group.linkOffset = false									--unlink  dead static from carrier
										group.x = 2000000
										group.y = 2000000
										group.units[1].x = 2000000
										group.units[1].y = 2000000
										group.route.points[1].x = 2000000
										group.route.points[1].y = 2000000
										log.debug("dead static unit.id: " .. unit.unitId .. " was linked to a carrier, unlink  dead static from carrier")
									end
									group.hidden = true												--hide dead static object
									unit.dead = true												--mark unit as dead in oob_ground (this is for the targetlist)
									unit.dead_last = true											--mark unit as died in last mission
									unit.CheckDay = camp.day                            			--assign destruction campaign date		 Miguel21 modification M19 : Repair SAM	
									log.debug("hidden dead static unit.id: " .. unit.unitId)

									--award ground kill to air unit
									if hit_table[events[e].initiator] ~= nil then														--check if dead static has a hit entry
										log.debug("dead unit: " .. unit.unitId .. " have this initiator in hit_table: " .. hit_table[events[e].initiator] .. ". Iterated oob_air for search initiator air unit for storing stats")																

										for killer_side_name,killer_side in pairs(oob_air) do											--iterate through all sides

											for killer_unit_n,killer_unit in pairs(killer_side) do										--iterate through all air units

												if string.find(hit_table[events[e].initiator], " " .. killer_unit.name .. " ", 1, true) then	--if the hitting unit is part of air unit name										
													log.debug("found initiator: " .. events[e].initiator .. " in oob_air: " .. killer_unit.name)

													if side_name ~= killer_side_name then												--make sure that hitting unit is not on same side as dead unit (friendly fire gives no kills)
														log.debug("iniziator (killer) unit have different side of the dead static unit - side static unit: " .. side_name .. " ~= killer_side_name: " .. killer_side_name)
														killer_unit.score.kills_ground = killer_unit.score.kills_ground + 1				--award ground kill to air unit
														killer_unit.score_last.kills_ground = killer_unit.score_last.kills_ground + 1
														log.debug("store stats for killer unit - killer_unit.name = " .. killer_unit.name .. ": update killer_unit.score.kills_ground and killer_unit.score_last.kills_ground (" .. killer_unit.score.kills_ground .. ", " .. killer_unit.score_last.kills_ground .. ")")
														AddPackstats(hit_table[events[e].initiator], "kill_ground")						--check if kill was in player package
														
														--award ground kill to client
														if client_hit_table[events[e].initiator] then									--if dead static was hit by a client
															log.info("dead static unit was hit by a client (player)")											
															clientstats[client_hit_table[events[e].initiator]].kills_ground = clientstats[client_hit_table[events[e].initiator]].kills_ground + 1							--award ground kill to client
															clientstats[client_hit_table[events[e].initiator]].score_last.kills_ground = clientstats[client_hit_table[events[e].initiator]].score_last.kills_ground + 1		--award ground kill to client
															--log.debug("store hit in clientstats: clientstats[" .. client_hit_table[events[e].initiator] .. "].kills_ground = " .. clientstats[client_hit_table[events[e].initiator]].kills_ground .. ", clientstats[" .. client_hit_table[events[e].initiator]"].score_last.kills_ship = " .. clientstats[client_control[events[e].initiator]].score_last.kills_ground)															
														end
													else --friendly kill  
														log.debug("friendly kill ground, store stats for killer unit - killer_unit.name = " .. killer_unit.name .. ": update killer_unit.score.friendly_kills_ship and killer_unit.score_last.friendly_kills_ground () - to be implement")
														AddPackstats(hit_table[events[e].initiator], "friendly_kill_ground")

														if client_hit_table[events[e].initiator] then									--client's friendly fire
															log.info("dead static unit was hit by a client (player) and have both same side (friendly kill) - unit side: " .. side_name .. " ~= killer_side_name: " .. killer_side_name)
															clientstats[client_hit_table[events[e].initiator]].friendly_kills_ground = clientstats[client_hit_table[events[e].initiator]].friendly_kills_ground + 1							--award ground kill to client
															clientstats[client_hit_table[events[e].initiator]].score_last.friendly_kills_ground = clientstats[client_hit_table[events[e].initiator]].score_last.friendly_kills_ground + 1		--award ground kill to client
															--log.debug("store hit in clientstats: clientstats[" .. client_hit_table[events[e].initiator] .. "].friendly_kills_ground = " .. clientstats[client_hit_table[events[e].initiator]].friendly_kills_ground .. ", clientstats[" .. client_hit_table[events[e].initiator]"].score_last.friendly_kills_ground = " .. clientstats[client_control[events[e].initiator]].score_last.friendly_kills_ground)															
														end
													end	
												end	
											end
										end
										hit_table[events[e].initiator] = nil						--after kills are assigned, remove hit unit from hit_table
										log.debug("kills assigned for iniziator:: " .. events[e].initiator .. " deleted initiator from hit_table")															
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
log.info("End evaluate log events =======================================================")														
	
log.info("Start evaluate log damaged aircraft in oob_air table ==========================")														
--log damaged aircraft in oob_air
for hit_unit,hitter in pairs(hit_table) do	--iterate through all remaining entries in the hit_table (all destroyed aircraft are removed meanwhile, damaged remain)
	
	for side_name,side in pairs(oob_air) do --iterate through all sides
		
		for unit_n,unit in pairs(side) do	--iterate through all air units
			
			if string.find(hit_unit, " " .. unit.name .. " ", 1, true) then					--if hit unit is part of air unit name
				log.info("found hit unit in oob_air - hit_unit included in unit.name of oob_air table(".. hit_unit .. ", " .. unit.name .. ")")	

				if health_table[hit_unit] and health_table[hit_unit] > 50 then				--if health of hit unit is bigger than 50%
					unit.roster.damaged = unit.roster.damaged + 1							--increase counter for damaged aircraft total
					unit.score_last.damaged = unit.score_last.damaged + 1					--increase counter for damaged aircraft in last mission
					log.debug("healt_table[" .. hit_unit .. "] = " .. health_table[hit_unit] .. " > 50 hit unit was damaged, store stats for hit unit - update unit.roster.damaged, unit.score_last.damaged (" .. unit.roster.damaged .. ", " .. unit.score_last.damaged)
				
				elseif health_table[hit_unit] then-- modified by Old_Boy																		--if health of hit unit is lower than 50%, the aircraft is written off
					unit.roster.lost = unit.roster.lost + 1									--increase counter for lost aircraft total
					unit.score_last.lost = unit.score_last.lost + 1							--increase counter for lost aircraft in last mission
					log.debug("healt_table[" .. hit_unit .. "] = " .. health_table[hit_unit] .. " <= 50, hit unit was destroyed store stats for hit unit - update unit.roster.lost, unit.score_last.lost (" .. unit.roster.lost .. ", " .. unit.score_last.lost .. ")")
										
					log.info("update oob ground kill for written off aircraft")	
					--oob air kill update for written off aircraft
					for killer_side_name,killer_side in pairs(oob_air) do --iterate through all sides
						
						for killer_unit_n,killer_unit in pairs(killer_side) do --iterate through all air units
							
							if string.find(hitter, " " .. killer_unit.name .. " ", 1, true) then --if the hitter unit is part of air unit name
								log.info("found hitter (killer) in oob_air. Hit unit: " .. hit_unit .. ", hitter (killer): " .. killer_unit.name .. ")")	
								
								if side_name ~= killer_side_name then --make sure that killer unit and hit aircraft are not on same side (friendly fire is not awarded as kill)
									log.debug("hitter (killer) unit have different side of hit unit, hit unit side: " .. side_name .. ", hitter side: " .. killer_side_name)									
									-- killer_unit.score.kills_ground = killer_unit.score.kills_ground + 1				--award ground kill to air unit
									-- killer_unit.score_last.kills_ground = killer_unit.score_last.kills_ground + 1	--increase kill counter for this mission of air unit
									killer_unit.score.kills_air = killer_unit.score.kills_air + 1				--award air kill to air unit
									killer_unit.score_last.kills_air = killer_unit.score_last.kills_air + 1	--increase air kill counter for this mission of air unit
									log.debug("store stats for oob_air unit (killer)- update killer_unit.score.kills_air, killer_unit.score_last.kills_air (" .. killer_unit.score.kills_air .. ", " .. killer_unit.score_last.kills_air .. ")")									
									AddPackstats(hitter, "kill_air")												--check if kill was in player package
									
									--client stats for kills
									if client_hit_table[hit_unit] then												--if hitter was a client
										log.info("hitter (killer) was a client (player): " .. client_hit_table[hit_unit] .. ", hit_unit: " .. hit_unit)
										clientstats[client_hit_table[hit_unit]].kills_air = clientstats[client_hit_table[hit_unit]].kills_air + 1								--award ground kill to client
										clientstats[client_hit_table[hit_unit]].score_last.kills_air = clientstats[client_hit_table[hit_unit]].score_last.kills_ground + 1
										log.debug("store client air stats - update clientstats[" .. client_hit_table[hit_unit] .. "].kills_air: " .. clientstats[client_hit_table[hit_unit]].kills_air .. ", clientstats[" .. client_hit_table[hit_unit] .. "].score_last.kills_air: " .. clientstats[client_hit_table[hit_unit]].score_last.kills_air)
									end

								else --friendly kill air  
									log.debug("hitter (killer) unit have same side of hit unit, hit unit side: " .. side_name .. ", hitter side: " .. killer_side_name)									
									log.debug("friendly kill air, store stats for killer unit - killer_unit.name = " .. killer_unit.name .. ": update killer_unit.score.friendly_kills_air and killer_unit.score_last.friendly_kills_air () - to be implement")
									AddPackstats(hitter, "friendly_kill_air")

									if client_hit_table[hit_unit] then									--client's friendly fire
										log.info("hit_unit was hit by a client (player) and have both same side (friendly kill) - unit side: " .. side_name .. " ~= killer_side_name: " .. killer_side_name)
										clientstats[client_hit_table[hit_unit]].friendly_kills_air = clientstats[client_hit_table[hit_unit]].friendly_kills_air + 1							--award air kill to client
										clientstats[client_hit_table[hit_unit]].score_last.friendly_kills_air = clientstats[client_hit_table[hit_unit]].score_last.friendly_kills_air + 1		--award air kill to client
										log.debug("store hit in clientstats: clientstats[" .. client_hit_table[hit_unit] .. "].friendly_kills_air = " .. clientstats[client_hit_table[hit_unit]].friendly_kills_air .. ", clientstats[" .. client_hit_table[hit_unit] .. "].score_last.friendly_kills_air = " .. clientstats[client_hit_table[hit_unit]].score_last.friendly_kills_air)															
									end	
								end
	 						end
						end
					end					
				end
				
				if unit.roster.ready > 0 then
					unit.roster.ready = unit.roster.ready - 1--decrease number of ready aircraft of air unit
				end

				if unit.score_last.ready > 0 then
					unit.score_last.ready = unit.score_last.ready - 1 -- MODIFIED BY Old_Boy --decrease number of ready aircraft for this mission of air unit
				end				
				log.debug("store stat for hit unit.name: " .. unit.name .. ", unit.roster.ready: " .. unit.roster.ready .. ", unit.score_last.ready(this mission): " .. unit.score_last.ready)
			end
		end
	end
end
--evaluate destroyed scenery objects
log.info("evaluate destroyed scenery objects")
for scen_name,scen in pairs(scen_log) do													--iterate through destroyed scenery objects
	log.trace("dead scen_name: " .. scen_name)

	if scen.x and scen.z then																--scenery object has x and z coordinates
		log.trace("dead scen_name: " .. scen_name .. " have coord x, z: " .. scen.x .. ", " .. scen.z)

		for side_name,side in pairs(targetlist) do											--iterate through targetlist

			for target_name,target in pairs(side) do										--iterate through targets

				if target.elements and target.elements[1].x then							--if the target has subelements and is a scenery object target (element has x coordinate)
					log.trace("target: " .. target_name .. " has subelements and is a scenery object target (element has x coordinate)")	

					for element_n,element in pairs(target.elements) do						--iterate through target elements

						if math.floor(scen.x) == math.floor(element.x) and math.floor(scen.z) == math.floor(element.y) then		--dead scenery is this element
							log.debug("dead scen: " .. scen_name .. " is this element: " .. element_n .. " of the target: " .. target_name)

							if element.dead then											--element was already total destroyed (dead) previously
								element.dead_last = false									--mark element as not died in last mission (because was total destroyed previously)
								log.debug("element was already total destroyed (dead) previously - update element dead status - element.dead: " .. tostring(element.dead) .. ", element.dead_last" .. tostring(element.dead_last) )
								
							else 															--element wasn't total destroyed (dead)
								element.dead = true											--mark element as dead 
								element.dead_last = true									--mark element as died in last mission
								element.CheckDay = camp.day									-- ajoute la date de destruction		 Miguel21 modification M19.f : Repair SAM	
								log.debug("element wasn't total destroyed (dead) - update element dead status - element.dead: " .. tostring(element.dead) .. ", element.dead_last" .. tostring(element.dead_last) )
								
								--award ground kill to air unit
								if scen.lasthit ~= nil then																			--check if dead scenery has a hit entry
									log.debug("dead scen has hit entry: " .. scen.lasthit .. ". Iterate oob_air for hitter (killer) search")

									for killer_side_name,killer_side in pairs(oob_air) do											--iterate through all sides

										for killer_unit_n,killer_unit in pairs(killer_side) do										--iterate through all air units

											if string.find(scen.lasthit, " " .. killer_unit.name .. " ", 1, true) then				--if the hitting unit is part of air unit name
												log.debug("found hitter (killer) in oob_air. Hit scen: " .. scen_name .. ", hitter (killer): " .. killer_unit.name .. ")")													

												if side_name == killer_side_name then												--make sure that hitting unit is hitting a target of his own side (friendly fire gives no kills)
													log.debug("hitter (killer) unit have same side of targetlist (enemy target): " .. side_name .. ", hitter side: " .. killer_side_name)													
													killer_unit.score.kills_ground = killer_unit.score.kills_ground + 1				--award ground kill to air unit
													killer_unit.score_last.kills_ground = killer_unit.score_last.kills_ground + 1
													log.debug("store stats for oob_air unit (killer)- update killer_unit.score.kills_ground, killer_unit.score_last.kills_ground (" .. killer_unit.score.kills_ground .. ", " .. killer_unit.score_last.kills_ground .. ")")									
													AddPackstats(scen.lasthit, "kill_ground")										--check if kill was in player package
													
													--award ground kill to client
													if client_control[scen.lasthit] then											--if dead scenery was hit by a client
														log.info("hit scen has different targetlist side from client side (player side) --> Friendly kill - targetlist side: " .. side_name .. " == killer_side_name: " .. killer_side_name)
														clientstats[client_control[scen.lasthit]].friendly_kills_ground = clientstats[client_control[scen.lasthit]].friendly_kills_ground + 1							--award ground kill to client
														clientstats[client_control[scen.lasthit]].score_last.friendly_kills_ground = clientstats[client_control[scen.lasthit]].score_last.friendly_kills_ground + 1	--award ground kill to client
														log.debug("store hit in clientstats: clientstats[" .. client_control[scen.lasthit] .. "].friendly_kills_ground = " .. clientstats[client_control[scen.lasthit]].friendly_kills_ground .. ", clientstats[" .. client_control[scen.lasthit] .. "].score_last.friendly_kills_gorund = " .. clientstats[client_control[scen.lasthit]].score_last.friendly_kills_ground)															
													end
												end
											end
										end
									end
								end
								break -- stop iterate for element of the dead scen
							end
						end
					end
				end
			end
		end
	end
end


-- ============================================================					
-- Last point for coding logger functionality by Old_Boy ------		
-- ============================================================		
