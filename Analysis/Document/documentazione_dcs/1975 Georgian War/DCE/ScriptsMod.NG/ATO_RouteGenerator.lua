-- To generate a flight route from base to target, evading as much threats as possible
-- Returns route points, route lenght and route threat level (unavoided threats)
-- Initiated by Main_NextMission.lua
-- Usecase with two public functions: getRoute() and getEscortRoute()
-------------------------------------------------------------------------------------------------------

if not versionDCE then 
	versionDCE = {} 
end

               -- VERSION --

versionDCE["ATO_RouteGenerator.lua"] = "OB.1.0.1"

-------------------------------------------------------------------------------------------------------
-- Old_Boy rev. OB.1.0.1: implements new algorithm for FindPath()
-- Old_Boy rev. OB.1.0.0: implements logging code
-- ATO_RG_Debug03 supprime trop de waypoint lors de l'escorte
-- ATO_RG_Debug02 quand les EWR sont d�truit: on active les CAP, si les CAP on besoin d'EWR c'est nul
-- ATO_RG_Debug01 targetPoint ligne 473 Reconnaissance


-- Miguel21 modification M16.d : SpawnAir B1b & B-52 need BaseAirStart = true in db_aibase
-- Miguel21 modification M06 : helicoptere playable


local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua")
-- NOTE MARCO: prova a caricarlo usando require(".. . .. . .. .ScriptsMod."versionPackageICM..".UTIL_Log.lua")
-- NOTE MARCO: https://forum.defold.com/t/including-a-lua-module-solved/2747/2
local log_level = LOGGING_LEVEL -- "traceVeryLow" --
local function_log_level = "info" --log_level
log.level = log_level 
log.outfile = LOG_DIR .. "LOG_ATO_RouteGenerator." .. camp.mission .. ".log" 
local local_debug = true -- local debug   
log.info("Start")

-- module parameters8
local ATO_RG_CONFIG = {
	TIME_FOR_INGRESS_CALCULATION = 60, -- (s) default 60s, time for compute ingress distance distance = speed(vattack) * time + standoff
	MINIMUM_STANDOFF_DISTANCE = 7000, -- (m) default 7000m, minimum standoff value for calculation (not not applicable when the value is defined in db_loadouts: always with new firepower code)
	TIME_FOR_STANDOFF_CALCULATION = 30, -- (s) default 30s, time for compute standoff distance distance = speed(vattack) * time + hattack
	PROFILE_MIN_ALT_FOR_CAP_DETECTION = 3000, -- min altitude for generic CAP detection (no need EWR support)(default = 3000 m ). Questo parametro condiziona la classificazione come minaccia di una CAP
	ALT_MIN_FOR_CLUTTER_EFFECT = 100, -- (defalut = 100 m)
	PERC_REDUCTION_THREAT_LEVER_FOR_CLUTTER = 0.5, -- (1 max, 0 total. default = 0.5)
	MAX_FACTOR_FOR_LENGHT_ROUTE = 1.5, -- default = 1.5, factor for calculate max distance of a route: max distance = factor * direct distance (from start to end point)
	MIN_DIFF_ALTITUDES_FOR_ALT_ROUTE = 300, -- min difference from leg_alt and profile.hattack to compute alternative route with altitude = hattack
	SEPARATION_FROM_THREAT_RANGE = 1000, -- min distance from threat.range border
	MAX_NUM_ISTANCE_PATH_FINDING = 7, -- max number of istances of function findPathLeg(), default = 7
	MAX_TANGENT_ANGLE = 30 -- max tangent angle for p1 and threat circle. if tangent angle > max new point is calculated with original metodi.
	-- note: diminish FACTOR_FOR_DISTANCE_FROM_THREAT_RANGE and increments MAX_NUM_ISTANCE_PATH_FINDING could be generate a more optimized route (maybe)
	-- note: increments MAX_NUM_ISTANCE_PATH_FINDING could be generate  a more optimized route (maybe)
}

--function to return radar horizon
local function RadarHorizon(h1, h2)
	local previous_log_level = log.level
	log.level = function_log_level
	local nameFunction = "function RadarHorizon(h1, h2): "    
	log.traceVeryLow("Start " .. nameFunction)						
	local r = 8500000																									--radius of earth (actual value 6371000 currected for refraction of radio waves)
	local d1 = math.sqrt(math.pow(r + h1, 2) - math.pow(r, 2))															--distance from radar height to earth tangent point
	local d2 = math.sqrt(math.pow(r + h2, 2) - math.pow(r, 2))															--distance from target altitude to earth tangent point
	local alpha1 = math.deg(math.atan(d1 / r))																			--angle between radar and earth tangent point
	local alpha2 = math.deg(math.atan(d2 / r))																			--angle beteen target and earth tangent point
	local u1 = 2 * r * math.pi / 360 * alpha1																			--ground distance from radar to earth tangent point
	local u2 = 2 * r * math.pi / 360 * alpha2						
	log.traceVeryLow("u1+u2 = " .. tostring(u1+u2))
	log.traceVeryLow("End " .. nameFunction)																			--ground distance from target to earth tangent point
	log.level = previous_log_level
	return u1 + u2																										--return total ground distance from radar to target
end

-- evalutate radar threat detection for an altitude profile, 
-- if profile alt is in range of threat altitude detection threat will be add in threat_table[profile alt]
local function evalRadarDetection(profile_alt, threat, type_profile, threat_table, threatentry, not_ewr)
	local previous_log_level = log.level
	log.level = function_log_level
	local nameFunction = "function evalRadarDetection(profile_alt, threat, type_profile, threat_table, threatentry, not_ewr: "    
	log.traceLow("Start " .. nameFunction)						
	log.traceLow(type_profile .. " profile is within threat altitude detection range (threat.min_alt: " .. tostring(threat.min_alt) .. ", threat.max_alt: " .. tostring(threat.max_alt) ..", profile.hCruise: " .. tostring(profile_alt) .. ")")
	local maxrange = RadarHorizon(threat.elevation, profile_alt + 100)									    --get the maximal range due to radar horizon (profile alt +100 m for safety)
	log.traceLow("maximal range due to radar horizon (" .. type_profile .. " profile alt +100 m for safety): " .. tostring(maxrange))
	
	if threat.max_low_alt and threat.range_at_low and profile_alt <= threat.max_low_alt then			
		log.traceLow("threat.max_low_alt and threat.range_at_low and profile_alt <= threat.max_low_alt, threatentry.range: " .. threatentry.range)

		if maxrange < threat.range_at_low then
			threatentry.range = maxrange																		--use maximal range due to radar horizon		
			log.traceLow("maxrange < threat.range_at_low, maximal range due to radar horizon is smaller than threat range, use maximal range due to radar horizon - > threatentry.range: " .. threatentry.range)
		
		else
			threatentry.range = threat.range_at_low																		--use maximal range due to radar horizon		
			log.traceLow("maxrange >= threat.range_at_low, maximal range due to radar horizon is bigger than threat.range_at_low, use threat.range_at_low - > threatentry.range: " .. threatentry.range)
		end

	elseif maxrange < threat.range then																			--maximal range due to radar horizon is smaller than threat range							
		threatentry.range = maxrange																		--use maximal range due to radar horizon
		log.traceLow("maximal range due to radar horizon is smaller than threat range, use maximal range due to radar horizon - > threatentry.range: " .. threatentry.range)
	end		

	if not_ewr then
		
		if profile_alt <= ATO_RG_CONFIG.ALT_MIN_FOR_CLUTTER_EFFECT then																				--if alt is lower than 100m
			threatentry.level = threat.level * (1 - ATO_RG_CONFIG.PERC_REDUCTION_THREAT_LEVER_FOR_CLUTTER)																--only 50% of threat level is applied as low level clutter bonus
			log.traceLow("type_profile: " .. type_profile .. " alt(" .. profile_alt .. "), threat isn't ewr and lower than 100m, only 50% of threat level is applied as low level clutter bonus, threatentry.level = " .. threatentry.level)		
		
		else
			threatentry.level = threat.level																	--full threat level is applied
			log.traceLow("type_profile: " .. type_profile .. ", threat isn't ewr assigned full threatentry.level = " .. threatentry.level .. ", insert ewr in threat_table.ground[" .. profile_alt .. "]")
		end
		table.insert(threat_table.ground[profile_alt], threatentry)
	
	else
		log.traceLow("type_profile: " .. type_profile .. ", threat is an ewr, insert ewr in threat_table.ewr[" .. profile_alt .. "]")
		table.insert(threat_table.ewr[profile_alt], threatentry)												-- insert ewr in threat_table.ewr
	end

	log.traceVeryLow("for this " .. type_profile .. " profile altitude (" .. profile_alt .. ") added this new threat entry:\n" .. inspect(threatentry))
	log.traceLow("End " .. nameFunction)	
	log.level = previous_log_level					
end


--[[
la valutazione della radar detection delle threats viene effettuata in base ai profili di cruise e di attack 
presi dai profili degli aerei e dalle dotazioni: per ogni tipo di armamento viene definito la quota di attacco 
e questo dato viene utilizzato per valutare il livello di minaccia che poi, verrà utilizzato per 
la route generation (in effetti sarà poi con queste info che il programma definirà le quote di volo dei diversi asset)


threat_table[cruise altitude o attack altitude]: tabella creata per contenere le minacce terrestri: vengono memorizzate 
le minacce terrestri con altitudini operative (min e max) che includono le altitudini cruise e attack del profilo 
di riferimento

]]



-- call from ATO_Generator profile is unit.loadout.task.tipi
function GetRoute(basePoint, targetPoint, profile, side_, task, time, multipackn, multipackmax, helicopter)	--side_: "blue" or "red"; time: "day" or "night" -- Miguel21 modification M06 : helicoptere playable (ajout variable helico)
	local previous_log_level = log.level
	log.level = function_log_level -- "traceVeryLow"
	-- activateLog(true, not profile.hAttack or not profile.hCruise, log, "traceVeryLow")	-- per torvare quale loadout ha problemi con hattack o hcruise
	local nameFunction = "function GetRoute(basePoint, targetPoint, profile, side_, task, time, multipackn, multipackmax, helicopter): "    
	log.trace("Start " .. nameFunction)						
	log.trace("GetRoute parameters:" .. inspect(basePoint) .. "\n" .. inspect(targetPoint) .. "\n " .. profile.name .. ", " .. side_ .. ", " .. task .. ",\n " .. time .. ",\n " .. tostring(multipackn) .. ",\n " .. multipackmax .. ",\n " .. tostring(helicopter) .. ")")
	local route = {}																									--table to store the route to be built
	local route_axis = GetHeading(targetPoint, basePoint)
	log.trace("targetPoint: " .. tostring(targetPoint) .. ", basePoint: " .. tostring(basePoint) .. ", route_axis(heading): " .. route_axis)																--axis base-target
	local standoff																										--standoff distance of attack WP from target
	--local threat table adjusted for cruise and attack altitudes
	local threat_table = {
		ground = {},
		ewr = {},
	}
	local HiddenCheck = false																						-- 	
	
	if helicopter then -- M28 gli elicotteri possono vedere tutte le difese, anche quelle nascoste  mentre l'aereo vola alto e veloce e non vede minacce 
		HiddenCheck = true 
		log.traceLow("helicopter == true -> HiddenCheck = true")
	end																		
	
	-- DEFINE THREAT TABLE FOR GROUND THREAT (NOT EWR) FOR SPECIFIC PROFILE

	threat_table.ground[profile.hCruise] = {}
	threat_table.ground[profile.hAttack] = {}	
	log.trace("iterate groundthreats[" .. side_ .. "] for threat radar detection")

	for threat_n,threat in pairs(groundthreats[side_]) do	
		log.traceLow("evalutation (threat) with threat_n: " .. threat_n .. " - type: ".. threat.type .. " - class: " .. threat.class)						--iterate through ground threats
		
		if (time == "day" or threat.night == true) and threat.hidden == HiddenCheck then																	--during day or threat is night capable to be counted as threat			
			local threatentry = {
				class = threat.class,
				SEAD_offset = threat.SEAD_offset, -- > 0 only radar sam
				x = threat.x,
				y = threat.y,
				range = threat.range,
				minrange = threat.minrange,
				range_at_low = threat.range_at_low,
				max_low_alt = threat.max_low_alt,
				min_alt = threat.min_alt,-- eliminare se non è possibile inserire le quote per i singoli points
				max_alt = threat.max_alt,-- eliminare se non è possibile inserire le quote per i singoli points				
			}
			log.traceLow("time(" .. time .. ") == day or threat_n: " .. threat_n .." has night capability ( threat.night == " .. tostring(threat.night) .. "), define a new threatentry:\n" .. inspect(threatentry))			
			
			if threat.min_alt <= profile.hCruise and threat.max_alt >= profile.hCruise then								--threat covers cruise alt														
				evalRadarDetection(profile.hCruise, threat, "cruise", threat_table, threatentry, true)				
			end
			
			if ( profile.hCruise ~= profile.hAttack ) and ( threat.min_alt <= profile.hAttack ) and ( threat.max_alt >= profile.hAttack ) then -- threat covers attack alt																--attack alt is different than cruise alt
				log.traceVeryLow("attack alt (profile.hAttack: " .. profile.hAttack .. ") is different than cruise alt (profile.hCruise: " .. profile.hCruise .. ") and threat covers attack alt")								
				threatentry.range = threat.range
				evalRadarDetection(profile.hAttack, threat, "attack", threat_table, threatentry, true)					
			end
		end
	end
	
	-- DEFINE THREAT TABLE FOR EWR THREAT FOR SPECIFIC PROFILE

	threat_table.ewr[profile.hCruise] = {}
	threat_table.ewr[profile.hAttack] = {}
	log.trace("iterate groundthreats[" .. side_ .. "] for ewr radar detection")

	for threat_n, threat in pairs(ewr[side_]) do																			--iterate through ewr threats
		log.traceLow("evalutation (ewr) with threat_n: " .. threat_n .. " - type: ewr - class: " .. threat.class)		--iterate through ground threats
		local cruisethreatentry = {
			class = threat.class,
			x = threat.x,
			y = threat.y,
			range = threat.range,
			min_alt = threat.min_alt,-- eliminare se non è possibile inserire le quote per i singoli points
			max_alt = threat.max_alt,-- eliminare se non è possibile inserire le quote per i singoli points				
		}

		if threat.min_alt <= profile.hCruise and threat.max_alt >= profile.hCruise then									--threat covers cruise alt			
			evalRadarDetection(profile.hCruise, threat, "ewr", threat_table, cruisethreatentry, false)								
		end
		local attackthreatentry = {
			class = threat.class,
			x = threat.x,
			y = threat.y,
			range = threat.range,
		}
		
		if threat.min_alt <= profile.hAttack and threat.max_alt >= profile.hAttack then									--threat covers attack alt					
			evalRadarDetection(profile.hAttack, threat, "ewr", threat_table, attackthreatentry, false)							
		end
	end
		
	-- function to check if a line .between two points runs through a threat. 
	-- Returns a table of AAA or SAM threats with assigned threat level and approachfactor ( 1 -> profile directly up the threat, 0 -> profile very far from threat )
	local function ThreatOnLeg(point1, point2, leg_alt)
		local previous_log_level = log.level
		log.level = function_log_level
		local nameFunction = "function ThreatOnLeg(point1, point2, leg_alt): "    		
		log.traceLow("Start " .. nameFunction)						
		log.traceLow("point1: (" .. point1.x .. "," .. point1.y .. "), point2: (" .. point2.x .. "," .. point2.y .. "), leg_alt: " .. leg_alt .. "")    
		local tbl = {}																									--local table to collect threats on route leg		
		log.traceLow("check ground threat -> iterate threat_table.ground[" .. leg_alt .. "]")
		--check ground threats:
		for t = 1, #threat_table.ground[leg_alt] do																		--iterate through all ground threats
			local threat_route_distance = GetTangentDistance(point1, point2, threat_table.ground[leg_alt][t])			--get closest distance from threat to route between point 1 and point 2
			log.traceVeryLow("compute closest distance from threat (pos x,y: " .. threat_table.ground[leg_alt][t].x .. ", " .. threat_table.ground[leg_alt][t].y .. ") to route between point 1 and point 2, threat_route_distance = " .. threat_route_distance)

			if threat_route_distance < threat_table.ground[leg_alt][t].range then										--route line (p1-p2) it's inside threat range
				log.traceLow("route line (p1-p2) it's inside threat range, threat_route_distance (" .. threat_route_distance .. ") < threat_table.ground[leg_alt][t].range (" .. threat_table.ground[leg_alt][t].range .. "). Insert threat in aux table threats (tbl), threat:\n" .. inspect(threat_table.ground[leg_alt][t]))
				table.insert(tbl, threat_table.ground[leg_alt][t])
				local approachfactor = 1 - threat_route_distance / threat_table.ground[leg_alt][t].range				--factor how close route passes to threat (1 = on top)
				tbl[#tbl].approachfactor = approachfactor
				log.traceLow("calculated approachfactor(1 = on top) = " .. approachfactor)
			end
		end
		
		if profile.avoid_EWR then																							--only count EWR as threats if loadout should avoid them
			log.traceLow("profile.avoid_EWR = true, check ewr threat -> iterate threat_table.ewr[" .. leg_alt .. "]")

			for e = 1, #threat_table.ewr[leg_alt] do																		--iterate through all ewr/awacs

				if threat_table.ewr[leg_alt][e].class == "EWR" then															--only do for EWR, ignore AWACS (too large area to avoid))										
					local entry = {
						approachfactor = 0
					}
					
					log.traceVeryLow("iterate through all fighter threats")

					for t = 1, #fighterthreats[side_] do																	--iterate through all fighter threats
						local ewr_required																					--boolean whether ewr is required for the fighter to be a threat
						
						if fighterthreats[side_][t].class == "CAP" then														--if the fighter is CAP
							log.traceVeryLow("fighterthreats[" .. side_ .. "][" .. t .. "] is a CAP")
							
							if leg_alt >= ATO_RG_CONFIG.PROFILE_MIN_ALT_FOR_CAP_DETECTION then											--if route leg is at high altitude 
								ewr_required = false																		--CAP does not need ewr to be a threat
								log.traceVeryLow("route leg (" .. leg_alt .. ") is at high altitude (> PROFILE_MIN_ALT_FOR_CAP_DETECTION(default 3000m)) -> CAP does not need ewr to be a threat")

							else																							--if route leg is at low altitude
								
								if fighterthreats[side_][t].LDSD then														--if fighter is look down/shoot down capable
									ewr_required = false																	--CAP does not need ewr to be a threat
									log.traceVeryLow("fighter is look down/shoot down (LDSD) capable -> CAP does not need ewr to be a threat")
								
								else																						--if fighter is not look down/shoot down capable
									ewr_required = true																		--CAP needs ewr to be a threat
									log.traceVeryLow("fighter is not look down/shoot down (LDSD) capable -> CAP does need ewr to be a threat")
								end
							end
						
						elseif fighterthreats[side_][t].class == "Intercept" then											--if the fighter is an interceptor
							ewr_required = true																				--ewr is required for fighter to be a threat (needs early warning to take off)
							log.traceVeryLow("fighterthreats[" .. side_ .. "][" .. t .. "] is a Interceptor -> ewr is required for fighter to be a threat (needs early warning to take off)")
						end
						
						if ewr_required == true then																		--EWR stations that can command fighters that require ewr guidance are counted as threats (AWACS and fighter areas are ignored, since these are too large areas to avoid anyway)
							log.traceVeryLow("ewr is required")
							local fighter_ewr_distance = GetDistance(threat_table.ewr[leg_alt][e], fighterthreats[side_][t])
							local sum_range_ewr_fighter = threat_table.ewr[leg_alt][e].range + fighterthreats[side_][t].range
							log.traceVeryLow("calculated fighter_ewr_distance = " .. fighter_ewr_distance .. ", sum_range_ewr_fighter = " .. sum_range_ewr_fighter)

							if fighter_ewr_distance <  sum_range_ewr_fighter then	--if fighterthreats and ewr are overlapping
								log.traceVeryLow("fighter_ewr_distance <  sum_range_ewr_fighter -> fighterthreats and ewr are overlapping")
								local route_fighter_distance = GetTangentDistance(point1, point2, fighterthreats[side_][t])
								log.traceVeryLow("calculated route_fighter_distance = " .. route_fighter_distance)

								if route_fighter_distance < fighterthreats[side_][t].range then								--if route leg is in range of fighterthreat
									log.traceVeryLow("route_fighter_distance < fighterthreats[side_][t].range (" .. fighterthreats[side_][t].range .. ") -> route leg is in range of fighterthreat")
									local route_ewr_distance = GetTangentDistance(point1, point2, threat_table.ewr[leg_alt][e])
									log.traceVeryLow("calculated route_fighter_distance = " .. route_fighter_distance)

									if route_ewr_distance < threat_table.ewr[leg_alt][e].range then					--if route leg is in range of ewr										
										local approachfactor = 1 - route_ewr_distance / threat_table.ewr[leg_alt][e].range		--factor how close route passes to threat (1 = on top)
										log.traceLow("route_ewr_distance < threat_table.ewr[leg_alt][e].range (" .. threat_table.ewr[leg_alt][e].range .. ") -> route leg is in range of ewr. Calculated approachfactor(1 = on top) = " .. approachfactor)	
										
										if approachfactor > entry.approachfactor then										--approach factor is higher than current entry for this ewr											
											entry = threat_table.ewr[leg_alt][e]											--make this ewr the entry
											entry.level = fighterthreats[side_][t].level									--capability level of fighter becomes new threat level of EWR station
											entry.approachfactor = approachfactor											--factor how close route passes to threat (1 = on top)
											log.traceLow("calculated approach factor is higher than current entry for this ewr -> make this ewr the entry, capability level(" .. entry.level .. ") of fighter becomes new threat level of EWR station and calculated approachfactor(" .. approachfactor ..  ") become entry's approachfactor")
										end						
									end
								end
							end
						end
					end
					
					if entry.approachfactor > 0 then																		--if an approach factor for this ewr was found
						table.insert(tbl, entry)																			--save ewr station as threat on this leg
						log.traceLow("an approach factor for this ewr was defined (>0) -> insert ewr station in aux table threats (tbl)")
						log.traceVeryLow("entry: \n" .. inspect(entry))
					end
				end
			end
		end
		
		log.traceVeryLow("return aux table threats (tbl):\n" .. inspect(tbl))
		log.traceLow("End " .. nameFunction)						
		log.level = previous_log_level
		return tbl
	end	
	
	--function to define a set of nav points to make a route between two points that evades threats
	local function FindPath(from, to)
		local previous_log_level = log.level
		log.level = function_log_level --"traceVeryLow" 
		local nameFunction = "function FindPath(from, to): "    		
		log.traceVeryLow("Start " .. nameFunction)						
		local FindPathLegTable = {}																									--table to store the the FindPathLeg functions for execution
		local NavRoutes = {}																										--table to temporary store all possible nav routes
		local direct_distance = GetDistance(from, to)																				--distance of direct path between start and end of route
		local no_threat_route = {}																									--to collect route branches that found a no threat route in order to cancel other arms of that branch
		
		--find a route between point1 and point2
		local function FindPathLeg(point1, point2, pointEnd, distance, route, instance, leg_alt)	
			local previous_log_level = log.level	
			log.level = function_log_level	--"traceVeryLow" --
			local nameFunction = "function FindPathLeg(point1, point2, pointEnd, distance, route, instance, leg_alt): "    		
			log.traceVeryLow("Start " .. nameFunction .. ", instance: " .. instance .. ", point1: " .. point1.x .. ", " .. point1.y .. ", point2: " .. point2.x .. ", " .. point2.y .. ", pointend: " .. pointEnd.x .. ", " .. pointEnd.y .. ", distance: " .. distance .. ", leg_alt: " .. leg_alt)									
			
			--local function to remove threats that point1(start) or pointend(end) is already in (unavoidable)
			local function removeThreatsAtStartEnd(threat_leg, point1, pointEnd)
				log.level = function_log_level	--"traceVeryLow" --
				local nameFunction = "function removeThreatsAtStartEnd(threat_leg, point1, pointEnd): "    		
				log.traceVeryLow("Start " .. nameFunction .. ", instance: " .. instance)	
				log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", #threat_leg: " .. #threat_leg .. ", point1: " .. point1.x .. ", " .. point1.y .. ", pointEnd: " .. pointEnd.x .. ", " .. pointEnd.y)    		
				
				for t = #threat_leg, 1, -1 do																				--iterate through threats from back to front
					local threat_in_range_from_point1 = GetDistance(point1, threat_leg[t]) <= threat_leg[t].range
					local threat_in_range_from_pointend = GetDistance(pointEnd, threat_leg[t]) <= threat_leg[t].range
					log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", threat_in_range_from_point1 = " .. tostring(threat_in_range_from_point1) .. ", threat_in_range_from_pointend = " .. tostring(threat_in_range_from_pointend))
					
					if threat_in_range_from_point1 or threat_in_range_from_pointend then	--if threat is in range of point1 or pointEnd it cannot be avoided and must be ignored
						table.remove(threat_leg, t)																			--remove threat
						log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", threat is in range of point1 or pointEnd, it cannot be avoided and must be ignored -> remove from threat_leg table threat " .. t)
					end
				end
				log.traceVeryLow("End " .. nameFunction .. ", instance: " .. instance)	
			end

			instance = instance + 1																									--increase instance of the function
			log.traceVeryLow(nameFunction .. "instance: " .. instance)	


			--also try a low variant
			if instance == 1 and ATO_RG_CONFIG.MIN_DIFF_ALTITUDES_FOR_ALT_ROUTE < ( leg_alt - profile.hAttack ) then																		--in first instance also make a low level route if attack alt is lower than cruise alt
				log.traceVeryLow(nameFunction .. "instance: " .. instance .. ", try a low variant, cruise alt (" .. leg_alt .. ") - attack alt(" .. profile.hAttack .. ") > MIN_DIFF_ALTITUDES_FOR_ALT_ROUTE (" .. ATO_RG_CONFIG.MIN_DIFF_ALTITUDES_FOR_ALT_ROUTE .. "), in first instance added in FindPathLegTable a low level route")
				table.insert(FindPathLegTable, {point1, point2, pointEnd, distance + 1, route, instance - 1, profile.hAttack})		--try leg again low (do not increase instance), increase distance slighly to introduce a bias against going low compared to the identical route high
			end
						
			--abort unneeded pathfinding after a valid route has been found
			if no_threat_route[leg_alt] and instance > no_threat_route[leg_alt] then												--if a no threat route has been found for this altitue, stop subsequent route branches(parallel instances of the no threat route are still checked as they might be shorter)
				log.traceVeryLow("no_threat route has been found for this altitude(" .. leg_alt .."), current instance is: " .. instance .. ", end function: stop subsequent route branches(parallel instances of the no threat route are still checked as they might be shorter)\nEnd " .. nameFunction)					
				return																												--stop this route branch
			end			

			local distance_remain = GetDistance(point1, pointEnd)																	--remaining distance to end
			local threat = ThreatOnLeg(point1, point2, leg_alt)				
																				--get the threat between point1 and point2
			log.traceVeryLow(nameFunction .. "remaining distance to end: " .. distance_remain .. ", threats on leg(point1, point2, leg_alt): " .. #threat)
			
			--save the current route variant directly to end before trying to refine it further
			local threatsum = 0				--sum of approach factor of threats from current point1 to end
			local threat_choice

			if point2 == pointEnd then																								--if point2 is the pointEnd
				threat_choice = threat				
				log.traceVeryLow(nameFunction .. "point2 == pointEnd -> evalutated threat from point1 to point2 at leg_alt, computed threat: " .. #threat_choice)

			else
				threat_choice = ThreatOnLeg(point1, pointEnd, leg_alt)																--get the threat between point1 and pointEnd				
				log.traceVeryLow(nameFunction .. "point2 ~= pointEnd - > evalutate threat from point1 to pointEnd at leg_alt, computed threat table of #" .. #threat_choice)
			end

			for t = 1, #threat_choice do	
				threatsum = threatsum + threat_choice[t].approachfactor																--sum the factors of each threat (1 = on top, 0 = tangential)
			end
			log.traceVeryLow(nameFunction .. "threatsum (summatory of all approachfactor threats) = " .. threatsum)


			table.insert(NavRoutes, {navpoints = route, dist = distance + distance_remain, threats = threatsum})					--save route variant directly to end from current route branch
			log.traceVeryLow(nameFunction .. "added  #route: (" .. #NavRoutes .. ") in NavRoutes table")			

			if threatsum == 0 then																									--there are no threats to end (also no unavoidable threats)
				log.traceVeryLow(nameFunction .. "there are no threats to end (also no unavoidable threats), stop function\nEnd " .. nameFunction)
				return																												--abort this route branch
			end						

			--ignore threats that directly cover point1 or pointEnd
			removeThreatsAtStartEnd(threat, point1, pointEnd)
			local tot_distance = distance + distance_remain

			if instance > ATO_RG_CONFIG.MAX_NUM_ISTANCE_PATH_FINDING then																									--if function instance is bigger than 7
				log.traceVeryLow(nameFunction .. "instance(" .. instance .. ") is bigger than " .. ATO_RG_CONFIG.MAX_NUM_ISTANCE_PATH_FINDING .. " -> stop function\nEnd " .. nameFunction)
				return																												--abort this route branch
			
			elseif tot_distance > (direct_distance * ATO_RG_CONFIG.MAX_FACTOR_FOR_LENGHT_ROUTE) then														--if total route distance is bigger than 1.5 times the direct distance
				log.traceVeryLow(nameFunction .. "instance(" .. instance .. "), total route distance(" .. distance + distance_remain .. ") is bigger than " .. ATO_RG_CONFIG.MAX_FACTOR_FOR_LENGHT_ROUTE .. " times the direct distance(" .. direct_distance .. " -> stop function\nEnd " .. nameFunction)
				return																												--abort this route branch
			
			elseif #threat == 0 then																							--if no more threats on remaining route
				log.traceVeryLow(nameFunction .. "instance(" .. instance .. "), no more threats(#threat == 0) on remaining route")
				
				if point2 == pointEnd then																						--if point2 is the pointEnd
					no_threat_route[leg_alt] = instance																			--variable that will cancel subsequent route finding at this altitude (parallel branches of the same instance are still being checked)
					log.traceVeryLow(nameFunction .. "instance(" .. instance .. "), point2 == pointEnd, variable that will cancel subsequent route finding at this altitude (parallel branches of the same instance are still being checked). no_threat_route[leg_alt: " .. leg_alt .. "] = ".. instance .. "(instance) -> stop function\nEnd " .. nameFunction)
					return																										--abort further route finding
				
				else																											--if point2 is not the end
					distance = distance + GetDistance(point1, point2)															--complete route distance of this variant up to point2
					table.insert(route, point2)																					--add point2 to route
					table.insert(FindPathLegTable, {point2, pointEnd, pointEnd, distance, route, instance, leg_alt})			--continue find route from point2 to end
					log.traceVeryLow(nameFunction .. "instance(" .. instance .. "), point2 is not the end(pointEnd), add point2 to route, continue find route from point2 to end (added {point2, pointEnd, pointEnd, distance(" .. distance .."), route, instance(".. instance .."), leg_alt(" .. leg_alt ..")}")
				end
			
			else --if there is a threat on leg, find left/right side alternates around threat	
				--log.level = "traceVeryLow" -- ELIMINARE SOLO PER DEBUGGING LOCALE																									
				-- return true if exist tangents follow of these info:
				-- tpL, tpR, headingL, headingR, lenghtL, lenghtR, alfaL and alfaR (degree), and position:
				-- tp are tangent points from p1 at circle with centre pc and radius r,
				-- heading are relative at tangents and heading_p1-p2 is heading line p1-p2,
				-- lenght are distance from p1 and tp,
				-- alfaL is angle in degree from left tangent and line p1-p2,
				-- alfaR is angle in degree from left tangent and line p1-p2,
				-- position is position respect centre of cirlce: left(right)-up(down)
				-- if p1 is on circonference return tp = inf, heading with offset of 90 degree (left and right), r/2 < lenght < r, alfaR=alfaL=90
				-- if p1 is within circle return false, other value nil
				local function GetTangentInfo(p1, p2, pc, r, max_tan_angle, separation_from_threat_range)	
					local previous_log_level = log.level
					log.level = function_log_level --   --"traceVeryLow" --
					local nameFunction = "function GetTangentInfo(p1, p2, pc, r, max_tan_angle): "    
					log.traceLow("Start " .. nameFunction .. ", instance: " .. instance)		
					
					if max_tan_angle and math.abs(max_tan_angle) < 90 then										-- check max angle limit for compute tangent info
						max_tangent_angle = math.abs(max_tan_angle)
						log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", max_tan_angle (" .. max_tan_angle .. ") < 90 -> max_tangent_angle = " .. max_tangent_angle)		

					else
						max_tangent_angle = ATO_RG_CONFIG.MAX_TANGENT_ANGLE
						log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", max_tan_angle (" .. max_tan_angle .. ") >= 90 -> max_tangent_angle = 45")		
					end

					-- return data for new route point computer with old metodi (shifting at 90,-90 degree)
					local function GetTangentInfoBase(p1, p1_p2_heading, min_distance_from_p1_p2, r, position, separation_from_threat_range) 
						local previous_log_level = log.level
						log.level = function_log_level --"traceVeryLow" -- 
						local nameFunction = "function GetTangentInfoBase(p1_p2_heading, min_distance_from_p1_p2, r, position): "    
						log.traceLow("Start " .. nameFunction .. ", instance: " .. instance)		
						local headingL = p1_p2_heading + 90 
						local headingR = p1_p2_heading - 90 
						local lenghtL, lenghtR 
						log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", headingL: " .. headingL .. ", headingR: " .. headingR)
						
						--p1 on right of cente.r circle		
					        lenghtR = min_distance_from_p1_p2 + (r - min_distance_from_p1_p2)/2 + separation_from_threat_range --r/2 per non esagerare nello spostamento?
						lenghtL = min_distance_from_p1_p2 + r/2 + separation_from_threat_range
							
						if string.sub(position, 1, 2) == "le" then	-- p1 on left of center circle			
							local ll = lenghtL 
							lenghtL = lenghtR 
							lenghtR = ll
							log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", p1 on left of center circle (position: " .. position .. "), lenghtL: " .. lenghtL .. ", lenghtR: " .. lenghtR)
						else
                                                        log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", p1 on right of center circle (position: " .. position .. "), lenghtL: " .. lenghtL .. ", lenghtR: " .. lenghtR)

						end

						local alfaL = 90
						local alfaR = -90
						local tpL = GetOffsetPoint(p1, headingL, lenghtL)
						local tpR = GetOffsetPoint(p1, headingR, lenghtR)
						log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", alfaL: " .. alfaL .. ", alfaR: " .. alfaR .. ", tpL: " .. tpL.x .. ", " .. tpL.y .. ", tpR: " .. tpR.x .. ", " .. tpR.y)
						log.traceLow("End " .. nameFunction .. ", instance: " .. instance)								
						log.level = previous_log_level
						return tpL, tpR, headingL, headingR, lenghtL, lenghtR, alfaL, alfaR
					end

					local tolerance = r * 0.01 																	-- distance tolerance, default = 1% of radius
					local exist_tangents = false
					local tpR, tpL, headingR, headingL, alfaR, alfaL, lenghtL, lenghtR
					local p1_pc_distance = GetDistance(p1, pc)														
					local p1_p2_heading = GetHeading(p1, p2)
					local min_distance_from_p1_p2 = GetTangentDistance(p1, p2, pc)								-- min distance from line p1-p2 to center of circle
					local diff = p1_pc_distance - r
					local position = ""
					local r_with_separation = r + separation_from_threat_range									-- radius of threat range with add separation		
					log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", p1_pc_distance = " .. p1_pc_distance .. ", p1_p2_heading = " .. p1_p2_heading .. ", min_distance_from_p1_p2 = " .. min_distance_from_p1_p2 .. ", p1_pc_distance - radius = " .. p1_pc_distance - r)		

					if p1.x < pc.x then  -- p1 is on left side of center
						position = "left"
					
					else  -- -- p1 is on right side of center
						position = "right"
					end

					if p1.y > pc.y then  -- p1 is upper of center
						position = position .. "-up"

					else  -- p1 is bottom of center
						position = position .. "-down"
					end
					log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", position: " .. position)		

					if  diff < 0 and math.abs(diff) > tolerance then -- p1 within circonference
						log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", p1(" .. p1.x .. ", " .. p1.y .. ") within circonference, instance: " .. instance .. ", return false")
						return false

					elseif  math.abs(diff) <= tolerance then -- p1 on circonference
						log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", p1(" .. p1.x .. ", " .. p1.y .. ") on circonference, instance: " .. instance .. ", compute info base and return them")
						tpL, tpR, headingL, headingR, lenghtL, lenghtR, alfaL, alfaR = GetTangentInfoBase(p1, p1_p2_heading, min_distance_from_p1_p2, r, position, separation_from_threat_range)
						
					else -- p1 out circonferenze
						-- compute alt point on up side of threat circle
						local alfa = math.deg( math.asin(r_with_separation / p1_pc_distance) )									-- alfa        angle from line p1-pc and tangent from p1 and circle
						local gamma = math.deg( math.asin( min_distance_from_p1_p2 / p1_pc_distance ) )						-- gamma       angle from line p1-pc and line p1-p2		
						local alfaL = alfa - gamma																-- omega       angle from left tangent from p1 and  circle and line p1-p2
						local alfaR = alfa + gamma																-- phi         angle from right tangent from p1 and circle and line p1-p2
						local lenght = r_with_separation / math.tan( math.rad(alfa) )												-- distance from p1 to tp 
						log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", p1(" .. p1.x .. ", " .. p1.y .. ") out circonference, instance: " .. instance .. ", alfa: " .. alfa .. ", gamma: " .. gamma .. ", alfaL: " .. alfaL .. ", alfaR: " .. alfaR .. ", lenght: " .. lenght)

						if alfaL <= max_tangent_angle then
							headingL = p1_p2_heading + alfaL
							lenghtL = lenght																	-- distance from p1 to tpL
							tpL = GetOffsetPoint(p1, headingL, lenghtL)		 									-- tangent point on left side
							log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", alfaL <= max_tangent_angle(" .. max_tangent_angle .. "), headingL: " .. headingL .. ", lenghtL: " .. lenghtL .. ", tpL: " .. tpL.x .. ", " .. tpL.y)
							
						else
							log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", alfaL > max_tangent_angle(" .. max_tangent_angle .. ")")
							tpL, _, headingL, _, lenghtL, _, alfaL, _ = GetTangentInfoBase(p1, p1_p2_heading, min_distance_from_p1_p2, threat[1].range, position, separation_from_threat_range)
							log.traceVeryLow(nameFunction .. ", instance: " .. instance .. "headingL: " .. headingL .. ", lenghtL: " .. lenghtL .. ", tpL: " .. tpL.x .. ", " .. tpL.y)
						end

						if alfaR <= max_tangent_angle then
							headingR = p1_p2_heading - alfaR
							lenghtR =  lenght																	-- distance from p1 to tpR
							tpR = GetOffsetPoint(p1, headingR, lenghtR) 										-- tangent point on right side
							log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", alfaR <= max_tangent_angle(" .. max_tangent_angle .. "), headingR: " .. headingR .. ", lenghtR: " .. lenghtR .. ", tpR: " .. tpR.x .. ", " .. tpR.y)
							
						else
							log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", alfaR > max_tangent_angle(" .. max_tangent_angle .. ")")
							_, tpR, _, headingR, _, lenghtR, _, alfaR = GetTangentInfoBase(p1, p1_p2_heading, min_distance_from_p1_p2, threat[1].range, position, separation_from_threat_range)
							log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", headingR: " .. headingR .. ", lenghtR: " .. lenghtR .. ", tpR: " .. tpR.x .. ", " .. tpR.y)
						end
					end
					log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", return info, headingL: " .. headingL .. ", headingR: " .. headingR .. ", lenghtL: " .. lenghtL .. ", lenghtR: " .. lenghtR .. ", tpR: " .. tpR.x .. ", " .. tpR.y .. ", tpL: " .. tpL.x .. ", " .. tpL.y)
					log.traceLow("End " .. nameFunction .. ", instance: " .. instance)			
					log.level = previous_log_level				
					return "true", tpL, tpR, headingL, headingR, lenghtL, lenghtR, position
				end

				local function InsertAlternativePoint(point1, point2alt, leg_alt, pointEnd, distance, route_alt, FindPathLegTable, instance)
					local previous_log_level = log.level
					log.level = function_log_level --"traceVeryLow" --
					local nameFunction = "function InsertAlternativePoint(point1, point2alt, leg_alt, pointEnd, route_alt, FindPathLegTable, instance): "    		
					log.traceVeryLow("Start " .. nameFunction .. ", instance: " .. instance)						

					local threat_leg = ThreatOnLeg(point1, point2alt, leg_alt)													--get threat between point1 and alternate point2					
					log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", calculated alternate point2 (" .. point2alt.x .. ", " .. point2alt.y .. ") on left/right side of current threat, #threats between point1 and point2alt: " .. #threat_leg)										
					--ignore threats that point1 or pointend is already in										
					removeThreatsAtStartEnd(threat_leg, point1, pointEnd, route_alt, FindPathLegTable, instance, leg_alt)
										
					if #threat_leg == 0 then																					--if there is no threat between point 1 and alternate point2
						log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", there isn't threat between point 1 and alternate point2(point2alt)")
						local distance_alt = distance + GetDistance(point1, point2alt)											--complete route distance of this variant up to point2alt
						local route_alt = {}																					--make a local copy of the route up to now

						for k, v in pairs(route) do
							route_alt[k] = {
								x = v.x,
								y = v.y,
							}
						end
						table.insert(route_alt, point2alt)																		--add point2alt to this route variant
						table.insert(FindPathLegTable, {point2alt, pointEnd, pointEnd, distance_alt, route_alt, instance, leg_alt})	--continue route from point2alt
						log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", update route distance of this variant up to point2alt, add alternate point(point2alt) to this route variant(route_alt) and continue route from point2alt(insert {point2alt, pointEnd, pointEnd, distance_alt(" .. distance_alt .. "), route_alt, instance(".. instance .."), leg_alt(" .. leg_alt ..")} in FindPathLegTable)")

					else																										--if there is a threat between point1 and point2alt
						log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", there is a threat between point 1 and alternate point2(point2alt), find new route to point2alt (insert {point1, point2alt, pointEnd, distance(" .. distance .. "), route, instance(".. instance .."), leg_alt(" .. leg_alt ..")} in FindPathLegTable)")
						table.insert(FindPathLegTable, {point1, point2alt, pointEnd, distance, route, instance, leg_alt})		--find new route to point2alt
					end		
					log.level = previous_log_level			
				end
				
				local radius_with_separation = threat[1].range + ATO_RG_CONFIG.SEPARATION_FROM_THREAT_RANGE 	-- R           calculated offset for new alternative point2																
				local response, tpL, tpR, headingL, headingR, lenghtL, lenghtR, alfaL, alfaR, position, hl, wl, dl, sl, ll							
				local tpL1, tpR1, headingL1, headingR1, lenghtL1, lenghtR1, alfaL1, alfaR1, hr, wr, dr, sr, lr
				log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", there is a threat on leg, find left/right side routes alternates around threat")	
				log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", point1: " .. point1.x .. ", " .. point1.y .. ", point2: " .. point2.x .. ", " .. point2.y .. ", threat_center: " .. threat[1].x  .. ", " .. threat[1].y .. ", threat[1].range: " .. threat[1].range .. ", SEPARATION_FOR_...: " .. ATO_RG_CONFIG.SEPARATION_FROM_THREAT_RANGE)								
				log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", radius_with_separation: " .. radius_with_separation .. ", p1_threat_distance: " .. GetDistance(point1, threat[1]) .. ", p2_threat_distance: " .. GetDistance(point2, threat[1]) .. ", min_distance_from_threat_p1_p2: " .. GetTangentDistance(point1, point2, threat[1]))					
				
				log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", compute tangent info with p1-p2: ")
				response, tpL, tpR, headingL, headingR, lenghtL, lenghtR, position = GetTangentInfo(point1, point2, threat[1], threat[1].range, ATO_RG_CONFIG.MAX_TANGENT_ANGLE, ATO_RG_CONFIG.SEPARATION_FROM_THREAT_RANGE)								
		
				log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", compute tangent info with p2-p1: ")
				response1, tpL1, tpR1, headingL1, headingR1, lenghtL1, lenghtR1, position1 = GetTangentInfo(point2, point1, threat[1], threat[1].range, ATO_RG_CONFIG.MAX_TANGENT_ANGLE, ATO_RG_CONFIG.SEPARATION_FROM_THREAT_RANGE)				
				
				if response and response1 then
					log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", point1 and point2 are within threat circonference ")
					--QUI IL PROBLEMA UNO O TUTTE E DUE I RISULTATI DI GetTangentInfo POSSONO ESSERE FALSI, SE TUTTI E DUE è CRTITICO IN QUANTO IL CALCOLO DOVREBBE ESLUDERE IL PUNTO INTERNO ELIMINANDOLO SE SOLO IL SECONDO P2 (P2-P1) QUINDI
					-- P1 E FUORI CERCHIO E' RISOLVIBILE CONSIDERANDO SOLO IL PUNTO ALTERNATIVO CALCOLATO IN RESPONSE (NON RESPONSE1)
					--RIVEDERE INSERENDO QUI TUTTO IL CODICE DI RESPONSE1 DISTINGUENDO I CASI IN CUI SI HANNO RISULTATI SOLO A LEFT OèPPURE RIGHT
				
					-- LEFT
					log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", response: " .. tostring(response) .. ", tpL: " .. tpL.x .. ", " .. tpL.y .. ", tpR: " .. tpR.x .. ", " .. tpR.y .. ", headingL: " .. headingL .. ", headingR: " .. headingR .. ", lenghtL: " .. lenghtL .. ", lenghtR: " .. lenghtR .. ", position: " .. position)												
					hl = GetDistance( tpL, tpL1 ) / 2
					wl = math.asin( hl / radius_with_separation ) 
					lenghtL_extension = hl * math.cos(wl)
					log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", hl: " .. hl .. ", wl: " .. wl .. ", lenghtL_extension: " .. lenghtL_extension .. ", lenghtL_extension / lenghtL: " .. lenghtL_extension / lenghtL)								

					if lenghtL_extension / lenghtL < 0.2 then
						point2Lalt = GetOffsetPoint(point1, headingL, lenghtL + lenghtL_extension)
						log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", enghtR_extension / lenghtR < 0.2: compute pointLalt2 with extension, headingL: " .. headingL .. ", lenghtL + lenghtL_extension: " .. lenghtL + lenghtL_extension .. ", point2Lalt: " .. point2Lalt.x .. ", " .. point2Lalt.y)								
						--dl = GetTangentDistance(tpL, tpL1)
						--sl = hl * tan(wl)
						--ll = dl + sl

					else
						point2Lalt = GetOffsetPoint(point1, headingL, lenghtL)
						log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", lenghtL_extension / lenghtL >= 0.2: compute pointLAlt2 without extension, headingL: " .. headingL .. ", lenghtL: " .. lenghtL .. ", point2Lalt: " .. point2Lalt.x .. ", " .. point2Lalt.y)								
					end					
					InsertAlternativePoint(point1, point2Lalt, leg_alt, pointEnd, distance, route_alt, FindPathLegTable, instance)

					-- RIGHT
					log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", response1: " .. tostring(response1) .. ", tpL1: " .. tpL1.x .. ", " .. tpL1.y .. ", tpR1: " .. tpR1.x .. ", " .. tpR1.y .. ", headingL1: " .. headingL1 .. ", headingR1: " .. headingR1 .. ", lenghtL1: " .. lenghtL1 .. ", lenghtR1: " .. lenghtR1 .. ", position: " .. position1)								
					hr = GetDistance( tpR, tpR1) / 2
					wr = math.asin( hr/ radius_with_separation ) 
					lenghtR_extension = hr * math.cos(wr)					
					log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", hr: " .. hr .. ", wr: " .. wr .. ", lenghtR_extension: " .. lenghtR_extension .. ", lenghtR_extension / lenghtR: " .. lenghtR_extension / lenghtR)								

					if lenghtR_extension / lenghtR < 0.2 then						
						point2Ralt = GetOffsetPoint(point1, headingR, lenghtR + lenghtR_extension)
						log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", lenghtR_extension / lenghtR < 0.2: compute pointRlt2 with extension, headingR: " .. headingR .. ", lenghtR + lenghtR_extension: " .. lenghtR + lenghtR_extension .. ", point2Ralt: " .. point2Ralt.x .. ", " .. point2Ralt.y)								
						--dl = GetTangentDistance(tpL, tpL1)
						--sl = hl * tan(wl)
						--ll = dl + sl

					else						
						point2Ralt = GetOffsetPoint(point1, headingR, lenghtR)
						log.traceVeryLow(nameFunction .. ", instance: " .. instance .. ", lenghtR_extension / lenghtR >= 0.2: compute pointRAlt2 without extension, headingR: " .. headingR .. ", lenghtR: " .. lenghtR .. ", point2Ralt: " .. point2Ralt.x .. ", " .. point2Ralt.y)								
					end					
					InsertAlternativePoint(point1, point2Ralt, leg_alt, pointEnd, distance, route_alt, FindPathLegTable, instance)
										
				elseif response then -- point2 within threat circonferenze, point1 out
					log.traceVeryLow(nameFunction .. ", instance: " .. instance .. "point1 within threat circonferenze, point2 out")
					point2Lalt = GetOffsetPoint(point1, headingL, lenghtL)
					point2Ralt = GetOffsetPoint(point1, headingR, lenghtR)
					InsertAlternativePoint(point1, point2Ralt, leg_alt, pointEnd, distance, route_alt, FindPathLegTable, instance)

				elseif response1 then -- point1 within threat circonferenze, point2 out
					log.error(nameFunction .. ", instance: " .. instance .. ", ANOMALY!! point1 within threat circonferenze, point2 out: procees without add points")					
					return --  abort pathfinding (or stop?)
				else
					log.error(nameFunction .. ", instance: " .. instance .. ", point1 and point2 are within circonference, return false")
					return --  abort pathfinding (or stop?)
				end				
				--log.level = log_level -- ELIMINARE SOLO PER DEBUGGING LOCALE																	
			end
			log.traceVeryLow("End " .. nameFunction .. ", instance: " .. instance)						
			log.level = previous_log_level
		end

		table.insert(FindPathLegTable, {from, to, to, 0, {}, 0, profile.hCruise})									--insert first instance of FindPathLeg to find a route between start and end point. arguments: start, end, final end (same), initial route distance 0, initial route empty {}, initial instance of the function 0, cruise alt
		log.traceVeryLow(nameFunction .. "insert first instance of FindPathLeg to find a route between point1: " ..from.x .. ", " .. from.y .. ", point2: " ..to.x .. ", " .. to.y .. " and endpoint == point2. Initial route distance 0, initial route empty {}, initial instance of the function 0, cruise alt: " .. profile.hCruise) 
		
		for num,arg in ipairs(FindPathLegTable) do																	--go through table of FindPathLegt functions and execute them. Each FindPathLegt functions can add more instances of same function for execution at end of table
			log.traceVeryLow(nameFunction .. "FindPathLegTable instance: " .. arg[6] .. ", call FindPathLeg(point1: " .. arg[1].x .. ", " .. arg[1].y .. " , point2: " .. arg[2].x .. ", " .. arg[2].y .. ", pointEnd: " .. arg[3].x .. ", " .. arg[3].y .. ", distance(" .. arg[4] .."), route, instance(" .. arg[6] .."), leg_alt(" .. arg[7] .."))")
			FindPathLeg(arg[1], arg[2], arg[3], arg[4], arg[5], arg[6], arg[7])										--Execute function with the stored arguments: define and added item in NavRoutes and FindPathLeg tables
		end
				
		--Determine best nav route from NavRoutes table
		local temp_route = {																						--local table to store the currently selected optimal route
			navpoints = {},
			dist = GetDistance(from, to)
		}
		
		if #NavRoutes == 0 then
			log.traceVeryLow(nameFunction .. "there aren't routes in NavRoutes table, stop function and return default temp_route\nEnd " .. nameFunction)
			return temp_route

		else
			log.traceVeryLow(nameFunction .. "there are #routes in NavRoutes table: " .. #NavRoutes)
			temp_route = NavRoutes[1]																		--make first route the temp route			

			for n = 2, #NavRoutes do																				--Go through all stored routes

				if NavRoutes[n].threats < temp_route.threats or (NavRoutes[n].threats == temp_route.threats and NavRoutes[n].dist < temp_route.dist) then	--if next route has either less threats or the same threats and shorter distance, make this the current temp route
					log.traceVeryLow(nameFunction .. "NavRoutes[" .. n .. "] next route has either less threats or the same threats and shorter distance, make this the current temp_route. NavRoutes[n].threats:  " .. NavRoutes[n].threats .. ", temp_route.threats: " .. temp_route.threats .. ", NavRoutes[n].dist: " .. NavRoutes[n].dist .. ", temp_route.dist: " ..temp_route.dist)					
					temp_route = NavRoutes[n]
				end

			end
			log.traceVeryLow("End " .. nameFunction)
			return temp_route																						--return the selected route
		end
		log.traceVeryLow("End " .. nameFunction)
		log.level = previous_log_level						
	end
	
	local function threatEvalutationInRoute(threat, EWRpenality, total_threat_level, point1, point2, type_service, storage_table, computedPoint)
		local previous_log_level = log.level
		log.level = function_log_level
		local break_loop = false
		
		for t = 1, #threat do																--iterate through all threats on this option				
			
			if threat[t].class == "EWR" then												--threat is an EWR
				
				if EWRpenality == false then												--threat is the first EWR encountered
					total_threat_level = total_threat_level + 0.1							--add a small threat level once if there are any EWR encountered betwen draft IP and draft attack point (this means there will be a small bias for IPs that are not under any EWR, but multiple EWR will not affect IP direction).
					EWRpenality = true														--mark that the threat penality for one EWR has been marked 
					log.traceVeryLow("threat is the first EWR encountered, set true for EWRPenality and update total_threat_level: " .. total_threat_level)
				end
			
			else

				if type_service == "ingress" or type_service == "egress" then
					local closest_approach = GetTangentDistance(point1, point2, threat[t])	--closest approach distance to threat
					local closest_approach_factor = 1 - closest_approach / threat[t].range		--factor how close threat is approached (1 = on top, 0 not at all)
					local lenght_in_threat = GetTangentLenght(point1, point2, threat[t], threat[t].range)	--distance that is traveled within threat range
					local threat_level = threat[t].level * (lenght_in_threat / (threat[t].range * 2)) * closest_approach_factor --threat level for this indiviudal threat (path lenght in threat circle compared to threat diameter * approach factor)
					total_threat_level = total_threat_level + threat_level						--sum all threat levels to total threat level
					log.traceVeryLow("computed closest_approach: " .. closest_approach .. ", factor how close threat is approached (1 = on top, 0 not at all): " .. closest_approach_factor)
					log.traceVeryLow("distance that is traveled within threat range: " ..  lenght_in_threat .. ", threat_level: " .. threat_level .. ", update total_threat_level: " .. total_threat_level)
					
				elseif type_service == "reco egress" then
					local threat_level = GetTangentLenght(point1, point2, threat[t], threat[t].range) / (threat[t].range * 2) * threat[t].level		--threat level for this indiviudal threat (path lenght in threat circle compared to threat diameter)
					total_threat_level = total_threat_level + threat_level							--sum all threat levels to total threat level
					log.traceVeryLow("threat_level: " .. threat_level .. ", update total_threat_level: " .. total_threat_level)
				
				elseif type_service == "altro" then
					--inserire se presente
				end
			end
		end
		log.traceVeryLow("calculated total_threat_level = " .. total_threat_level .. "")
							
		if total_threat_level == 0 then														--if there is no threat, make this the IP and stop evaluation
			computedPoint = point1
			log.traceVeryLow("there isn't threat, make this the IP and stop evaluation -> make initialPoint the IP and stop evaluation, initialPoint = (" .. computedPoint.x .. ", " .. computedPoint.y .. ")")
			break_loop = true

		else																				--if there are threats
			table.insert(storage_table, {point = point1, threat = total_threat_level})			--store current draft IP in IP table
			log.traceVeryLow("there isn't threat -> store current draft point in " .. type_service .. "table, draft_point = (" .. point1.x .. ", " .. point1.y .. "), stored threat level for this point: " .. total_threat_level)
		end
		log.level = previous_log_level
		return break_loop, total_threat_level, point1, point2 , computedPoint			
	end

	--< ===============================================================					
	--<                Last point for code analisys 		
	--< ===============================================================	

	local break_loop = false
	----- find a route depending on task -----
	if task == "Strike" or task == "Anti-ship Strike" or task == "Reconnaissance" then
		log.traceVeryLow("task = " .. task)			
		--set Initial Point IP
		local initialPoint = {}																				--initial point		
		local base_target_route = FindPath(basePoint, targetPoint)											--find the safest route between basePoint and targetPoint
		log.traceVeryLow("calculated the safest route between basePoint and targetPoint: " .. inspect(base_target_route))
		local ideal_axis																					--ideal axis of the IP
		
		if #base_target_route.navpoints == 0 then															--if there are no navpoints
			ideal_axis = route_axis																			--ideal IP is on base-target axis
			log.traceVeryLow("there aren't navpoints (#base_target_route.navpoints == 0) -> ideal axis (heading) of IP is base2target axis: " .. ideal_axis)
		
		else																								--if there are navpoints
			ideal_axis = GetHeading(targetPoint, base_target_route.navpoints[#base_target_route.navpoints])	--ideal IP is on target-last navpoint axis
			log.traceVeryLow("there are navpoints (#base_target_route.navpoints ~= 0) -> ideal axis (heading) of IP is target - last navpoint axis: " .. ideal_axis)
		end
		
		if profile.standoff then																			--if standoff defined in loadout profile
			standoff = profile.standoff																		--use value from loadout profile
			log.traceVeryLow("standoff defined in loadout profile")
		
		else																								--if no standoff defined in loadout profile
			standoff = profile.hAttack + profile.vAttack * ATO_RG_CONFIG.TIME_FOR_STANDOFF_CALCULATION 												--standoff distance is attack alt plus 30 seconds at attack speed
			
			if standoff < ATO_RG_CONFIG.MINIMUM_STANDOFF_DISTANCE then																			--standoff should be at least 7000m
				standoff = ATO_RG_CONFIG.MINIMUM_STANDOFF_DISTANCE
			end
			log.traceVeryLow("standoff isn't define in loadout profile")
		end
		log.traceVeryLow("standoff = " .. standoff .. "\nStart computing Initial point (IP)")
				
		do
			local IP_distance
			
			if profile.ingress then																			--ingress distance is defined in loadout
				IP_distance = standoff + profile.ingress
				log.traceVeryLow("ingress distance is defined in loadout")
			else
				IP_distance = standoff + profile.vAttack * ATO_RG_CONFIG.TIME_FOR_INGRESS_CALCULATION												--distance target-IP is standoff range from profile + 60 seconds run in at attack speed
				log.traceVeryLow("ingress distance isn't defined in loadout")
			end
			log.traceVeryLow("ingress distance (IP_distance) = " .. IP_distance) 
			local IP_table = {}																				--table to store all possible IPs
			
			local MaxAttackOffset = 90
			
			if profile.MaxAttackOffset then
				MaxAttackOffset = profile.MaxAttackOffset
				log.traceVeryLow("MaxAttackOffset is defined in loadout")
			
			else
				log.traceVeryLow("MaxAttackOffset isn't defined in loadout")
			end
			log.traceVeryLow("MaxAttackOffset: " .. MaxAttackOffset)
			local heading_min = ideal_axis - MaxAttackOffset												--lowest heading from target to IP
			local heading_max = ideal_axis + MaxAttackOffset												--highest heading from target to IP
			log.traceVeryLow("lowest heading from target to IP(heading_min): " .. heading_min .. ", highest heading from target to IP (heading_max): " .. heading_max)

			if multipackmax > 1 then																		--if this is part of a multi package attack
				ideal_axis = heading_min + (multipackn - 1) / (multipackmax - 1) * (MaxAttackOffset * 2)	--distribute ideal axis evenly across maximal left/right offset depending on package number
				log.traceVeryLow("this is part of a multi package attack -> distribute ideal axis evenly across maximal left/right offset depending on package number, ideal_axis = " .. ideal_axis)
			end			

			log.traceVeryLow("find IP by evaluating threat level for IPs between heading min and heading max in 5 steps")

			for n = 0, 180, 5 do																			--find IP by evaluating threat level for IPs between heading min and heading max in 5� steps
				
				if initialPoint.x then																		--break loop if an IP is set																
					log.traceVeryLow("break loop if an IP is set, initialPoint.x: " .. initialPoint.x)
					break
				
				else

					for m = 1, -1, -2 do																		--try left and right option for each offset from ideal axis (*1, *-1)
						local IP_heading = ideal_axis + (n * m)													--current IP heading to consider
						
						if IP_heading >= heading_min and IP_heading <= heading_max then							--IP heading must be within min and max offsets
							local draft_IP = GetOffsetPoint(targetPoint, IP_heading, IP_distance)				--draft IP for current offset
							local draft_attackPoint = targetPoint
							log.traceVeryLow("IP heading is within min and max offsets, draft_IP = (" .. draft_IP.x .. ", " .. draft_IP.y .. "), draft_attackPoint = targetPoint (" .. draft_attackPoint.x .. ", " .. draft_attackPoint.y .. ")")
							
							if standoff > 15000 then															--if standoff range is more than 15'000m, assume target will not be overflown. (forse teme che l'aereo è molto veloce (vattack) oppire vola molto in alto (standoff =  hattack +  vattack * 30) e quindi la distanza di inizio attacco è presa con un certo anticipo rispetto al target. L'angolo di discesa dovrebbe essere calcolato da questo codice nell'ordine di 30 gradi, se voli troppo alto o troppo veloce c'è il rischio di sorvolare il target )
								draft_attackPoint = GetOffsetPoint(targetPoint, IP_heading, standoff)			--draft attack point
								log.traceVeryLow("standoff range(" .. standoff .. ") is more than 15'000m, draft_attackPoint = targetPoint (" .. draft_attackPoint.x .. ", " .. draft_attackPoint.y .. ")")
							end
							local threat = ThreatOnLeg(draft_IP, draft_attackPoint, profile.hAttack)			--all threats between draft IP and draft attack point
							log.traceVeryLow("threats between draft IP and draft attack point:\n" .. inspect(threat) .. "\nEvalutate threat to compute total_threat_level")
							local total_threat_level = 0														--cumulated threat level for this leg
							local EWRpenality = false
							break_loop, total_threat_level, draft_IP, draft_attackPoint, initialPoint = threatEvalutationInRoute(threat, EWRpenality, total_threat_level, draft_IP, draft_attackPoint, "ingress", IP_table, initialPoint) -- break_loop, total_threat_level, draft_IP, draft_attackPoint, initialPoint							
							
							if break_loop then
								break
							end							
						end
					end
				end
			end
						
			if initialPoint.x == nil then																	--if IP is not yet set, find the best from IP table
				log.traceVeryLow("best IP is not yet set, find the best from IP table")
				local current_threat = math.huge

				for n = 1, #IP_table do																		--iterate through all draft IPs to find to one with the lowest threat level
					local roundedThreat = math.floor(IP_table[n].threat * 10000000000) / 10000000000		--round threat value to remove rounding errors
					log.traceVeryLow("roundedThreat: " .. roundedThreat .. ". current_threat: " .. current_threat)

					if roundedThreat < current_threat then													--if this draft IP has a lower threat level than the IP currently set						
						initialPoint = IP_table[n].point													--make it the new IP
						current_threat = roundedThreat														--this is the threat level of the currently set IP					
						log.traceVeryLow("draft IP has a lower threat level than the IP currently set, updated initialPoint:\n" .. inspect(initialPoint) ..  "\n updated current_threat: " .. current_threat)
					end
				end
			end
			
			if initialPoint.x then
				log.traceVeryLow("best IP found is(" .. initialPoint.x ..  ")")	
			else
				log.traceVeryLow("IP is not yet set. #IP_table: " .. #IP_table)	
			end
			
		end
		
		--set attack point		
		local target_ip_heading = GetHeading(targetPoint, initialPoint)
		local attackPoint = GetOffsetPoint(targetPoint, target_ip_heading, standoff)						--attack point is standoff range from target on straight IP-target line
		log.traceVeryLow("calculated attack point like standoff range from target on straight IP-target line")				
		--set egress point
		local egressPoint = {}																				--egress point
		do
			local egress_point_start																		--point from where egress is initiated (target or attack point depending on standoff profile)
			local egress_table = {}
			local egress_distance																			--egress point is standoff range from target plus 90 seconds run out at attack speed

			if profile.egress then																			--egress distance is defined in loadout
				egress_distance = standoff + profile.egress
				log.traceVeryLow("egress_distance is defined in loadout")	
			else
				egress_distance = standoff + profile.vAttack * 90											--egress point is standoff range from target plus 90 seconds run out at attack speed
			end
			log.traceVeryLow("calculated egress_distance: " .. egress_distance)
			local egress_heading
			
			if task == "Strike" or task == "Anti-ship Strike" then

				if standoff <= 15000 then																		--if standoff range is 15'000m or less, assume target will be overflown. Optimal egress should be 90� offset from ingress in direction of RTB					
					egress_point_start = targetPoint															--egress starts from target
					log.traceVeryLow("standoff range <= 15000m, assume target will be overflown. Optimal egress should be 90g offset from ingress in direction of RTB -> egress starts from target, egress_point_start: " .. targetPoint.x .. ", " .. targetPoint.y)

					if GetDeltaHeading(route_axis, target_ip_heading) < 0 then									--homebase is on left side of ingress heading
						egress_heading = target_ip_heading + 90													--optimal egress heading is 90� to left
						log.traceVeryLow("homebase is on left side of ingress heading -> optimal egress heading is 90g to left")
					
					else																						--homebase is on right side of ingress heading
						egress_heading = target_ip_heading - 90													--optimal egress heading is 90� to right
						log.traceVeryLow("homebase is on right side of ingress heading -> optimal egress heading is 90g to right")
					end
					log.traceVeryLow("egress_heading: " .. egress_heading)

				else																							--if standoff range is bigger than 15'000m, optimal egrees should be in direction of home base
					egress_point_start = attackPoint															--egress starts from attack point

					if profile.egress then																		--egress distance is defined in loadout
						egress_distance = profile.egress
					
					else
						egress_distance = profile.vAttack * 90													--egress distance for stand off attacks is 90 seconds run out at attack speed
					end					
					egress_heading = GetHeading(attackPoint, basePoint)											--direct egress from attack point
					log.traceVeryLow("standoff range > 15000m, optimal egrees should be in direction of home base, egress starts from attack point, egress_distance: " .. egress_distance .. ", egress_heading: " .. egress_heading)										
				end
				
				log.traceVeryLow("find egress point by evaluating threat level for egress between egress heading and +/- 135 offset in 5 steps")

				for n = 0, 180, 5 do																			--find egress point by evaluating threat level for egress between egress heading and +/- 135� offset in 5� steps
					
					if egressPoint.x then																		--break loop if an egress point is set
						log.traceVeryLow("egress point is set, egressPoint = (" .. egressPoint.x .. ", " .. egressPoint.y .. ")")																
						break
					
					else
						
						for m = 1, -1, -2 do																	--try left and right option for each offset from egress heading (*1, *-1)
							local dH = GetDeltaHeading(egress_heading + n * m, target_ip_heading)
							
							if dH >= 15 or dH <= -15 then	--valid egresses must be at least 15� offset from ingress
								local draft_egress = GetOffsetPoint(egress_point_start, egress_heading + n * m, egress_distance)	--draft egress for current offset
								local threat = ThreatOnLeg(egress_point_start, draft_egress, profile.hAttack)		--all threats between attack point and draft egress point
								local total_threat_level = 0														--cumulated threat level for this leg
								local EWRpenality = false
								log.traceVeryLow("egress offset from ingress > 15 degree (left or right): " .. dH .. ", calculate draft point egresss = " .. draft_egress.x)
								log.traceVeryLow("threats between attack point and draft egress point:\n" .. inspect(threat))
								
								break_loop, total_threat_level, egress_point_start, draft_egress, egressPoint = threatEvalutationInRoute(threat, EWRpenality, total_threat_level, egress_point_start, draft_egress, "egress", egress_table, egressPoint)
									
								if break_loop then
									break
								end		
							end
						end
					end
				end
				
			elseif task == "Reconnaissance" then																	--for recon missions
				egress_heading = GetHeading(initialPoint, targetPoint)
				
				for n = 0, 30, 5 do																					--find egress point by evaluating threat level for egress between egress heading and +/- 30� offset in 5� steps
					
					if egressPoint.x then																			--break loop if an egress point is set																
						log.traceVeryLow("an egress point is set, egress point.x: " .. egressPoint.x)
						break
					
					else
						
						for m = 1, -1, -2 do																		--try left and right option for each offset from egress heading (*1, *-1)
							local draft_egress = GetOffsetPoint(targetPoint, egress_heading + n * m, egress_distance)	--draft egress for current offset
							local threat = ThreatOnLeg(targetPoint, draft_egress, profile.hAttack)					--all threats between target point and draft egress point
							local total_threat_level = 0															--cumulated threat level for this leg
							local EWRpenality = false
							log.traceVeryLow("calculate draft point egresss = " .. draft_egress.x)
							log.traceVeryLow("threats between attack point and draft egress point:\n" .. inspect(threat))							
							break_loop, total_threat_level, targetPoint, draft_egress , egressPoint = threatEvalutationInRoute(threat, EWRpenality, total_threat_level, targetPoint, draft_egress, "reco egress", egress_table, egressPoint)
							
							if break_loop then
								break
							end							
						end
					end
				end
			end
			
			if egressPoint.x == nil then																			--if egress is not yet set, find the best from egress table
				log.traceVeryLow("egress is not yet set, find the best from egress table")
				local current_threat = 1000000
				
				for n = 1, #egress_table do																			--iterate through all draft egress points to find to one with the lowest threat level
					
					if egress_table[n].threat < current_threat then													--if this draft egress has a lower threat level than the egress currently set
						egressPoint = egress_table[n].point															--make it the new egress point
						current_threat = egress_table[n].threat														--this is the threat level of the currently set egress			
					end
				end
			end
			log.traceVeryLow("egress found is " .. egressPoint.x)
		end

		-- ============================================================					
		-- Last point for coding logger functionality by Old_Boy ------		
		-- ============================================================	

		
		--set outbound and inbound routes
		local outbound_navRoute = FindPath(basePoint, initialPoint)														--find the safest route between basePoint and initialPoint
		local inbound_navRoute = FindPath(basePoint, egressPoint)														--find the safest route between egressPoint and basePoint
	

		--set form-up point
		local joinPoint = {}																							--point where package joins on common flight route
		do
			local point																									--join point is between basePoint and this local point
			if #outbound_navRoute.navpoints == 0 then																	--if there is no outbound nav route
				point = initialPoint																					--point is IP
			else																										--if there is an outbound nav route
				point = outbound_navRoute.navpoints[1]																	--point is first nav point
			end
			local heading = GetHeading(basePoint, point)
			
			local distance = math.abs((profile.hCruise - basePoint.h) * 10)												--distance to climb from base elevation to cruise altitude with 6� pitch (make sure distance is positive)
			if distance >= GetDistance(basePoint, point) then															--climb distance bigger than distance to first WP
				distance = GetDistance(basePoint, point) / 3 * 2														--join point is 2/3 to first WP
			elseif distance < 15000 then																				--climb distance less than 15 km
				distance = 15000																						--join point should be at least 15 km from base
			end
			
			joinPoint = GetOffsetPoint(basePoint, heading, distance)													--define join point
		end
		
		
		--set split point
		local splitPoint = {}																							--point where package splits to land on individual airbases		
		do
			local point																									--split point is between basePoint and this local point
			if #inbound_navRoute.navpoints == 0 then																	--if there is no inbound nav route
				point = egressPoint																						--point is egress point
			else																										--if there is an inbound nav route
				point = inbound_navRoute.navpoints[1]																	--point is first nav point
			end
			local heading = GetHeading(basePoint, point)
			
			local distance = math.abs((profile.hCruise - basePoint.h) * 4)												--distance to descend from cruise alt to base elevation with 15� pitch (make sure distance is positive)
			if distance >= GetDistance(basePoint, point) then															--descend distance bigger than distance to last WP
				distance = GetDistance(basePoint, point) / 3 * 2														--join point is 2/3 to last WP
			elseif distance < 15000 then																				--descend distance less than 15 km
				distance = 15000																						--split point should be at least 15 km from base
			end
			
			splitPoint = GetOffsetPoint(basePoint, heading, distance)													--define split point
		end
		
		--altitude plus basse pour helicopter -- Miguel21 modification M06 : helicoptere playable 
		if helicopter then  delta_h = 50 else delta_h = 1524 end
		
		--build complete route if virtual air base, in the AIR ;), Spawn
		-- Miguel21 modification M16.d : SpawnAir B1b & B-52 need BaseAirStart = true in db_aibase
		if basePoint.BaseAirStart == true then
			table.insert(route, {x = basePoint.x, y = basePoint.y, id = "Spawn", alt = profile.hCruise })
			table.insert(route, {x = joinPoint.x, y = joinPoint.y, id = "Join", alt = profile.hCruise})
		else
			--build complete route
			table.insert(route, {x = basePoint.x, y = basePoint.y, id = "Taxi", alt = 0})
			table.insert(route, {x = basePoint.x, y = basePoint.y, id = "Departure", alt = basePoint.h + delta_h})
			table.insert(route, {x = joinPoint.x, y = joinPoint.y, id = "Join", alt = profile.hCruise})
		end
		for n = 1, #outbound_navRoute.navpoints do
			table.insert(route, {x = outbound_navRoute.navpoints[n].x, y = outbound_navRoute.navpoints[n].y, id = "Nav", alt = profile.hCruise})
		end
		table.insert(route, {x = initialPoint.x, y = initialPoint.y, id = "IP", alt = profile.hAttack})
		table.insert(route, {x = attackPoint.x, y = attackPoint.y, id = "Attack", alt = profile.hAttack})
		if standoff <= 15000 then																						--if standoff is less than 15 km, then assume target is overflown. For higher standoff, targetPoint is only inserted after route lenght and threats are calculated-
			table.insert(route, {x = targetPoint.x, y = targetPoint.y, id = "Target", alt = profile.hAttack})
		end
		table.insert(route, {x = egressPoint.x, y = egressPoint.y, id = "Egress", alt = profile.hAttack})
		for n = #inbound_navRoute.navpoints, 1, -1 do
			table.insert(route, {x = inbound_navRoute.navpoints[n].x, y = inbound_navRoute.navpoints[n].y, id = "Nav", alt = profile.hCruise})
		end
		table.insert(route, {x = splitPoint.x, y = splitPoint.y, id = "Split", alt = profile.hCruise})
		table.insert(route, {x = basePoint.x, y = basePoint.y, id = "Land", alt = profile.hCruise})
		
		
		--set descend and climb points in route
		if profile.hCruise > profile.hAttack then																		--if cruise is higher than attack altitude, a descend and a climb point must be inserted
			
			--descend point
			for n = 3, #route - 2 do																					--iterate through route between join and split point
				if route[n].alt == profile.hCruise then	
					
					--get high and low threats on route segement
					local threat = {}																					--threats on leg at high alt default to 0 as an earlier change in altitude is of no advantage
					if profile.hAttack < 1000 then																		--if attack alt is at low altitude, collect actual threats to determine descend point on route
						threat = ThreatOnLeg(route[n], route[n + 1], profile.hCruise)									--collect threats on leg at high alt
					end
					
					--reduce threat range of EWR to areas of fighter threat
					for t = 1, #threat do																				--iterate through threats
						if threat[t].class == "EWR" then																--threat is an EWR
							local newEWRrange = 0																		--reduce EWR range to point where route enters the first fighter threat
							for f = 1, #fighterthreats[side_] do														--iterate through fighter threats to find the first fighter threat that route enters into
								if GetTangentDistance(route[n], route[n + 1], fighterthreats[side_][f]) < fighterthreats[side_][f].range then	--route passes though fighter threat circle
									--find point where route enters fighter circle					
									local heading1 = GetHeading(route[n], route[n + 1])									--route heading
									local heading2 = GetHeading(route[n], fighterthreats[side_][f])						--heading to center of threat circle
									local alpha = math.abs(heading1 - heading2)											--angle beteen both headings
									if alpha > 180 then
										alpha = math.abs(alpha - 360)
									end
									alpha = math.rad(alpha)
									local a = fighterthreats[side_][f].range											--radius of threat circle
									local b = GetDistance(route[n], fighterthreats[side_][f])							--distance to center of threat circle
									local beta = math.asin(b / (a / math.sin(alpha)))									--sinus sentence
									beta = math.pi - beta																--since sinus sentence results in two possible angles for beta and only the second is valid, use the second
									local gamma = math.pi - alpha - beta
									local c = a / math.sin(alpha) * math.sin(gamma)										--distance from WP1 to point intersecting threat circle
									local p = GetOffsetPoint(route[n], heading1, c)										--point where route is intersecting threat circle
									local EWR_p = GetDistance(threat[t], p)												--distance from EWR to this point
									if EWR_p < threat[t].range and EWR_p > newEWRrange then								--find longest new EWR range that is shorter than the original EWR range
										newEWRrange = EWR_p
									end
									
									local heading_p_t = GetHeading(p, fighterthreats[side_][f])							--heading from intersection point to fighter threat
									local heading_p_EWR = GetHeading(p, threat[t])										--heading from intersection point to EWR
									local angle = math.abs(heading_p_t - heading_p_EWR)									--angle beteen both headings
									if angle > 180 then
										angle = math.abs(angle - 360)
									end
									if angle > 90 then																	--when angle is bigger then 90																											
										threat[t].invert = true															--the treat circle of EWR is outside of the interception area!
									end

								end
							end
							if newEWRrange > 0 then																		--an adjusted EWR range was determined
								threat[t].range = newEWRrange															--make this the new EWR range
							end
						end
					end
					
					if #threat == 0 then																				--no threat on route
						if route[n].alt > route[n + 1].alt then															--but route segment is the descend leg
							local descendPoint = {}																		--point to start descend
							local heading = GetHeading(route[n + 1], route[n])											--descend point is on route leg
							local distance = math.abs((profile.hCruise - profile.hAttack)) * 6							--distance to descend is 6 times the altitude difference (~-10� pitch) (make sure is positive)
							if distance < GetDistance(route[n + 1], route[n]) then										--if descend distance is longer than route leg distance, ignore descend point
								descendPoint = GetOffsetPoint(route[n + 1], heading, distance)							--define descend point position
								descendPoint.id = "Nav"
								descendPoint.alt = profile.hCruise
								table.insert(route, n + 1, descendPoint)												--insert into route
							end
							break																						--stop going through waypoints for the descend
						end
					else																								--if there are threats on route leg, make the descend on this route leg
						for m = n, #route do																			--move forward in route and put all subsequent waypoints until IP to low alt
							if route[m + 1].alt == profile.hCruise then													--if next waypoint is still at cruise
								route[m + 1].alt = profile.hAttack														--adjust waypoint alt to attack
							else
								break																					--stop when attack part of route is reached
							end
						end
						
						local descendPointEnd = {}																		--point where descend must be completed (here the high alt threat is entered)
						local distance = 100000000
						local heading = GetHeading(route[n], route[n + 1])
						for t = 1, #threat do
							local p1_t_heading = GetHeading(route[n], threat[t])
							local alpha = math.abs(heading - p1_t_heading)												--angle beteen route and p1-threat
							if alpha > 180 then
								alpha = math.abs(alpha - 360)
							end						
							local p1_t = GetDistance(route[n], threat[t])												--distance between p1 and threat
							local p1_p90t = math.cos(math.rad(alpha)) * p1_t											--distance between p1 and point on route perpendicular to threat
							local p90t_t = p1_t * math.sin(math.rad(alpha))												--distance between threat and point on route perpendicular to threat
							local p90t_pC = math.sqrt(math.pow(threat[t].range, 2) - math.pow(p90t_t, 2))				--distance between point on route perpendiculat to threat and point on route intersecting threat circle
							local p1_pC = p1_p90t - p90t_pC																--distance from p1 to point on route intersecting threat circle
							if p1_pC <= 0 then																			--if point on route intersecting threat circle is ahead of p1
								if threat[t].invert then																--area outside of EWR range is the threat area
									distance = -p1_pC
								else
									distance = 0
									break																				--p1 is already within a threat circle. No descend point is needed, alter p1 to low level instead
								end
							elseif p1_pC < distance then
								distance = p1_pC																		--find the shortest distance to all threat circles (this is the point on route where the decend to low alt must be completed)
							end
						end
						
						if distance == 0 then																			--descend point is ahead of route[n]
							route[n].alt = profile.hAttack																--set route[n] to low alttude
						else																							--descend point is beyond of route[n]
							descendPointEnd = GetOffsetPoint(route[n], heading, distance)								--define descend point position
							descendPointEnd.id = "Nav"
							descendPointEnd.alt = profile.hAttack
							table.insert(route, n + 1, descendPointEnd)													--insert into route
							local descend_distance = (profile.hCruise - profile.hAttack) * 6							--distance to descend is 6 times the altitude difference (~-10� pitch)
							if descend_distance < distance then
								local descendPointStart = {}															--point where descend starts
								descendPointStart = GetOffsetPoint(route[n], heading, (distance - descend_distance))	--define descend point position
								descendPointStart.id = "Nav"
								descendPointStart.alt = profile.hCruise
								table.insert(route, n + 1, descendPointStart)											--insert into route
							end
						end
						break																							--stop going through waypoints for the descend
					end
				end
			end
			
			--climb point
			for n = #route - 1, 4, -1 do																				--iterate through route backkwards between split and join point
				if route[n].alt == profile.hCruise then	
					
					--get high and low threats on route segement
					local threat = {}																					--threats on leg at high alt default to 0 as an earlier change in altitude is of no advantage
					if profile.hAttack < 1000 then																		--if attack alt is at low altitude, collect actual threats to determine climb point on route
						threat = ThreatOnLeg(route[n], route[n - 1], profile.hCruise)									--collect threats on leg at high alt
					end
					
					--reduce threat range of EWR to areas of fighter threat
					for t = 1, #threat do																				--iterate through threats
						if threat[t].class == "EWR" then																--threat is an EWR
							local newEWRrange = 0																		--reduce EWR range to point where route enters the first fighter threat
							for f = 1, #fighterthreats[side_] do														--iterate through fighter threats to find the first fighter threat that route enters into
								if GetTangentDistance(route[n], route[n - 1], fighterthreats[side_][f]) < fighterthreats[side_][f].range then	--route passes though fighter threat circle
									--find point where route enters fighter circle					
									local heading1 = GetHeading(route[n], route[n - 1])									--route heading
									local heading2 = GetHeading(route[n], fighterthreats[side_][f])						--heading to center of threat circle
									local alpha = math.abs(heading1 - heading2)											--angle beteen both headings
									if alpha > 180 then
										alpha = math.abs(alpha - 360)
									end
									alpha = math.rad(alpha)
									local a = fighterthreats[side_][f].range											--radius of threat circle
									local b = GetDistance(route[n], fighterthreats[side_][f])							--distance to center of threat circle
									local beta = math.asin(b / (a / math.sin(alpha)))									--sinus sentence
									beta = math.pi - beta																--since sinus sentence results in two possible angles for beta and only the second is valid, use the second
									local gamma = math.pi - alpha - beta
									local c = a / math.sin(alpha) * math.sin(gamma)										--distance from WP1 to point intersecting threat circle
									local p = GetOffsetPoint(route[n], heading1, c)										--point where route is intersecting threat circle
									local EWR_p = GetDistance(threat[t], p)												--distance from EWR to this point
									if EWR_p < threat[t].range and EWR_p > newEWRrange then								--find longest new EWR range that is shorter than the original EWR range
										newEWRrange = EWR_p
									end
									
									local heading_p_t = GetHeading(p, fighterthreats[side_][f])							--heading from intersection point to fighter threat
									local heading_p_EWR = GetHeading(p, threat[t])										--heading from intersection point to EWR
									local angle = math.abs(heading_p_t - heading_p_EWR)									--angle beteen both headings
									if angle > 180 then
										angle = math.abs(angle - 360)
									end
									if angle > 90 then																	--when angle is bigger then 90																											
										threat[t].invert = true															--the treat circle of EWR is outside of the interception area!
									end
								end
							end
							if newEWRrange > 0 then																		--an adjusted EWR range was determined
								threat[t].range = newEWRrange															--make this the new EWR range
							end
						end
					end
					
					if #threat == 0 then																				--no threat on route
						if route[n].alt > route[n - 1].alt then															--but route segment is the climb leg
							local climbPoint = {}																		--point to start climb
							local heading = GetHeading(route[n - 1], route[n])											--climb point is on route leg
							local distance = math.abs((profile.hCruise - profile.hAttack)) * 10							--distance to climb is 10 times the altitude difference (~-6� pitch) (make sure is positive)
							if distance < GetDistance(route[n - 1], route[n]) then										--if climb distance is longer than route leg distance, ignore clinb point
								climbPoint = GetOffsetPoint(route[n - 1], heading, distance)							--define climb point position
								climbPoint.id = "Nav"
								climbPoint.alt = profile.hCruise
								table.insert(route, n, climbPoint)														--insert into route
							end
							break																						--stop going through waypoints for the climb
						end
					else																								--if there are threats on route leg, make the climb on this route leg
						for m = n, 1, -1 do																				--move backward in route and put all previous wayoints until Egress to low alt
							if route[m - 1].alt == profile.hCruise then													--if previous waypoint is still at cruise
								route[m - 1].alt = profile.hAttack														--adjust waypoint alt to attack
							else
								break																					--stop when attack part of route is reached
							end
						end
						
						local climbPointStart = {}																		--point where climb starts (here the high alt threat is left)
						local distance = 100000000
						local heading = GetHeading(route[n], route[n - 1])
						for t = 1, #threat do
							local p1_t_heading = GetHeading(route[n], threat[t])
							local alpha = math.abs(heading - p1_t_heading)												--angle beteen route and p1-threat
							if alpha > 180 then
								alpha = math.abs(alpha - 360)
							end						
							local p1_t = GetDistance(route[n], threat[t])												--distance between p1 and threat
							local p1_p90t = math.cos(math.rad(alpha)) * p1_t											--distance between p1 and point on route perpendicular to threat
							local p90t_t = p1_t * math.sin(math.rad(alpha))												--distance between threat and point on route perpendicular to threat
							local p90t_pC = math.sqrt(math.pow(threat[t].range, 2) - math.pow(p90t_t, 2))				--distance between point on route perpendiculat to threat and point on route intersecting threat circle
							local p1_pC = p1_p90t - p90t_pC																--distance from p1 to point on route intersecting threat circle
							if p1_pC <= 0 then																			--if point on route intersecting threat circle is ahead of p1
								if threat[t].invert then																--area outside of EWR range is the threat area
									distance = -p1_pC
								else
									distance = 0
									break																				--p1 is already within a threat circle. No climb point is needed, alter p1 to low level instead
								end
							elseif p1_pC < distance then
								distance = p1_pC																		--find the shortest distance to all threat circles (this is the point on route where the decend to low alt must be completed)
							end
						end
						
						if distance == 0 then																			--climb point is after of route[n]
							route[n].alt = profile.hAttack																--set route[n] to low alttude
						else																							--climb point is beyond of route[n]
							climbPointStart = GetOffsetPoint(route[n], heading, distance)								--define climb point position
							climbPointStart.id = "Nav"
							climbPointStart.alt = profile.hAttack
							table.insert(route, n, climbPointStart)														--insert into route
							local climb_distance = (profile.hCruise - profile.hAttack) * 10								--distance to climb is 10 times the altitude difference (~-6� pitch)
							if climb_distance < distance then
								local climbPointEnd = {}																--point where climb ends
								climbPointEnd = GetOffsetPoint(route[n + 1], heading, (distance - climb_distance))		--define climb point position
								climbPointEnd.id = "Nav"
								climbPointEnd.alt = profile.hCruise
								table.insert(route, n + 1, climbPointEnd)												--insert into route
							end
						end
						break																							--stop going through waypoints for the climb
					end
				end
			end
			
		elseif profile.hCruise < profile.hAttack then																	--if cruise is lower than attack altitude, a descend and a climb point must be inserted
			for n = 3, #route - 2 do																					--iterate through route between join and split point
				if route[n].alt < route[n + 1].alt then																	--climb route leg
					local climbPoint = {}																				--point to start climb
					local heading = GetHeading(route[n + 1], route[n])													--climb point is on route leg
					local distance = math.abs((profile.hCruise - profile.hAttack) * 10)									--distance to climb is 10 times the altitude difference (~6� pitch) (make sure is positive)
					if distance < GetDistance(route[n], route[n + 1]) then												--if climb distance is longer than route leg distance, ignore climb point
						climbPoint = GetOffsetPoint(route[n + 1], heading, distance)									--define climb point position
						climbPoint.id = "Nav"
						climbPoint.alt = profile.hCruise
						table.insert(route, n + 1, climbPoint)															--insert into route
					end
					break
				end
			end
			for n = 3, #route - 2 do																					--iterate through route between join and split point
				if route[n].alt > route[n + 1].alt then																	--descend route leg
					local descendPoint = {}																				--point to start descend
					local heading = GetHeading(route[n], route[n + 1])													--descend point is on route leg
					local distance = math.abs((profile.hCruise - profile.hAttack) * 10)									--distance to descend is 10 times the altitude difference (~-6� pitch) (make sure is positive)
					if distance < GetDistance(route[n + 1], route[n]) then												--if descend distance is longer than route leg distance, ignore descend point
						descendPoint = GetOffsetPoint(route[n], heading, distance)										--define descend point position
						descendPoint.id = "Nav"
						descendPoint.alt = profile.hCruise
						table.insert(route, n + 1, descendPoint)														--insert into route
					end
					break
				end
			end
		end
		
		
	elseif task == "Fighter Sweep" then
		
		--set outbound and inbound routes
		local sweepStart = targetPoint																					--start point of sweep
		local sweepEnd																									--end point of sweep
		if targetPoint.MultiPoints then																					--the sweep target has multiple points
			sweepEnd = targetPoint.MultiPoints[#targetPoint.MultiPoints]												--sweep ends at last point
		else																											--the sweep target has a single point only
			sweepEnd = targetPoint																						--sweep ends at target point
		end
		
		local outbound_navRoute = FindPath(basePoint, sweepStart)														--find the safest outbound route
		local inbound_navRoute = FindPath(basePoint, sweepEnd)															--find the safest inbound route
		
		
		--set form-up point
		local joinPoint = {}																							--point where package joins on common flight route
		do
			local point																									--join point is between basePoint and this local point
			if #outbound_navRoute.navpoints == 0 then																	--if there is no outbound nav route
				point = sweepStart																						--point is sweepStart
			else																										--if there is an outbound nav route
				point = outbound_navRoute.navpoints[1]																	--point is first nav point
			end
			local heading = GetHeading(basePoint, point)
			
			local distance = math.abs((profile.hCruise - basePoint.h) * 7)												--distance to climb from base elevation to cruise altitude with 8� pitch (make sure distance is positive)
			if distance >= GetDistance(basePoint, point) then															--climb distance bigger than distance to first WP
				distance = GetDistance(basePoint, point) / 3 * 2														--join point is 2/3 to first WP
			elseif distance < 15000 then																				--climb distance less than 15 km
				distance = 15000																						--join point should be at least 15 km from base
			end
			
			joinPoint = GetOffsetPoint(basePoint, heading, distance)													--define join point
		end
		
		
		--set split point
		local splitPoint = {}																							--point where package splits to land on individual airbases		
		do
			local point																									--split point is between basePoint and this local point
			if #inbound_navRoute.navpoints == 0 then																	--if there is no inbound nav route
				point = sweepEnd																						--point is sweepEnd
			else																										--if there is an inbound nav route
				point = inbound_navRoute.navpoints[1]																	--point is first nav point
			end
			local heading = GetHeading(basePoint, point)
			
			local distance = math.abs((profile.hCruise - basePoint.h) * 7)												--distance to descend from cruise alt to base elevation with 8� pitch (make sure distance is positive)
			if distance >= GetDistance(basePoint, point) then															--descend distance bigger than distance to last WP
				distance = GetDistance(basePoint, point) / 3 * 2														--join point is 2/3 to last WP
			elseif distance < 15000 then																				--descend distance less than 15 km
				distance = 15000																						--split point should be at least 15 km from base
			end
			
			splitPoint = GetOffsetPoint(basePoint, heading, distance)													--define split point
		end
		
		
		--build complete route
		table.insert(route, {x = basePoint.x, y = basePoint.y, id = "Taxi", alt = 0})
		table.insert(route, {x = basePoint.x, y = basePoint.y, id = "Departure", alt = basePoint.h + 1000})
		table.insert(route, {x = joinPoint.x, y = joinPoint.y, id = "Join", alt = profile.hCruise})
		for n = 1, #outbound_navRoute.navpoints do
			table.insert(route, {x = outbound_navRoute.navpoints[n].x, y = outbound_navRoute.navpoints[n].y, id = "Nav", alt = profile.hCruise})
		end
		if targetPoint.MultiPoints then																					--the sweep target has multiple points
			for n = 1, #targetPoint.MultiPoints do
				table.insert(route, {x = targetPoint.MultiPoints[n].x, y = targetPoint.MultiPoints[n].y, id = "Sweep", alt = profile.hAttack})
			end
		else																											--the sweep target has a single point only
			table.insert(route, {x = targetPoint.x, y = targetPoint.y, id = "Sweep", alt = profile.hAttack})
		end
		for n = #inbound_navRoute.navpoints, 1, -1 do
			table.insert(route, {x = inbound_navRoute.navpoints[n].x, y = inbound_navRoute.navpoints[n].y, id = "Nav", alt = profile.hCruise})
		end
		table.insert(route, {x = splitPoint.x, y = splitPoint.y, id = "Split", alt = profile.hCruise})
		table.insert(route, {x = basePoint.x, y = basePoint.y, id = "Land", alt = profile.hCruise})
	
		
	elseif task == "CAP" or task == "AWACS" or task == "Refueling" then
		
		--set orbit points
		local orbit_lenght
		if task == "CAP" then
			orbit_lenght = profile.vAttack * 180																		--orbit leg 3 minutes
		elseif task == "AWACS" then
			orbit_lenght = profile.vAttack * 180																		--orbit leg 3 minutes
		elseif task == "Refueling" then
			orbit_lenght = profile.vAttack * 180																		--orbit leg 3 minutes
		end
		
		local orbitStart = {}
		local orbitEnd = {}
		
		orbitStart = GetOffsetPoint(targetPoint, route_axis + 90, orbit_lenght / 2)
		orbitEnd = GetOffsetPoint(targetPoint, route_axis - 90, orbit_lenght / 2)
		
		
		--set outbound and inbound routes
		local outbound_navRoute = FindPath(basePoint, orbitStart)														--find the safest outbound route
		local inbound_navRoute = FindPath(basePoint, orbitEnd)															--find the safest inbound route
	

		--set form-up point
		local joinPoint = {}																							--point where package joins on common flight route
		do
			local point																									--join point is between basePoint and this local point
			if #outbound_navRoute.navpoints == 0 then																	--if there is no outbound nav route
				point = orbitStart																						--point is orbitStart
			else																										--if there is an outbound nav route
				point = outbound_navRoute.navpoints[1]																	--point is first nav point
			end
			local heading = GetHeading(basePoint, point)
			
			local distance = math.abs((profile.hCruise - basePoint.h) * 7)												--distance to climb from base elevation to cruise altitude with 8� pitch (make sure distance is positive)
			if distance >= GetDistance(basePoint, point) then															--climb distance bigger than distance to first WP
				distance = GetDistance(basePoint, point) / 3 * 2														--join point is 2/3 to first WP
			elseif distance < 15000 then																				--climb distance less than 15 km
				distance = 15000																						--join point should be at least 15 km from base
			end
			
			joinPoint = GetOffsetPoint(basePoint, heading, distance)													--define join point
		end
		
		
		--set split point
		local splitPoint = {}																							--point where package splits to land on individual airbases		
		do
			local point																									--split point is between basePoint and this local point
			if #inbound_navRoute.navpoints == 0 then																	--if there is no inbound nav route
				point = orbitEnd																						--point is orbitEnd
			else																										--if there is an inbound nav route
				point = inbound_navRoute.navpoints[1]																	--point is first nav point
			end
			local heading = GetHeading(basePoint, point)
			
			local distance = math.abs((profile.hCruise - basePoint.h) * 7)												--distance to descend from cruise alt to base elevation with 8� pitch (make sure distance is positive)
			if distance >= GetDistance(basePoint, point) then															--descend distance bigger than distance to last WP
				distance = GetDistance(basePoint, point) / 3 * 2														--join point is 2/3 to last WP
			elseif distance < 15000 then																				--descend distance less than 15 km
				distance = 15000																						--split point should be at least 15 km from base
			end
			
			splitPoint = GetOffsetPoint(basePoint, heading, distance)													--define split point
		end	
		
		
		--build complete route
		table.insert(route, {x = basePoint.x, y = basePoint.y, id = "Taxi", alt = 0})
		table.insert(route, {x = basePoint.x, y = basePoint.y, id = "Departure", alt = basePoint.h + 1000})
		table.insert(route, {x = joinPoint.x, y = joinPoint.y, id = "Join", alt = profile.hCruise})
		for n = 1, #outbound_navRoute.navpoints do
			table.insert(route, {x = outbound_navRoute.navpoints[n].x, y = outbound_navRoute.navpoints[n].y, id = "Nav", alt = profile.hCruise})
		end
		table.insert(route, {x = orbitStart.x, y = orbitStart.y, id = "Station", alt = profile.hAttack})
		table.insert(route, {x = orbitEnd.x, y = orbitEnd.y, id = "Station", alt = profile.hAttack})
		for n = #inbound_navRoute.navpoints, 1, -1 do
			table.insert(route, {x = inbound_navRoute.navpoints[n].x, y = inbound_navRoute.navpoints[n].y, id = "Nav", alt = profile.hCruise})
		end
		table.insert(route, {x = splitPoint.x, y = splitPoint.y, id = "Split", alt = profile.hCruise})
		table.insert(route, {x = basePoint.x, y = basePoint.y, id = "Land", alt = profile.hCruise})
		
		
		--climb and descend points
		if profile.hCruise < profile.hAttack then																		--if cruise and attack altitude are not the same, a descend and a climb point must be inserted
			for n = 3, #route - 2 do																					--iterate through route between join and split point
				if route[n].alt < route[n + 1].alt then																	--climb route leg
					local climbPoint = {}																				--point to start climb
					local heading = GetHeading(route[n + 1], route[n])													--climb point is on route leg
					local distance = math.abs((profile.hCruise - profile.hAttack) * 10)									--distance to climb is 10 times the altitude difference (~6� pitch) (make sure is positive)
					if distance < GetDistance(route[n], route[n + 1]) then												--if climb distance is longer than route leg distance, ignore climb point
						climbPoint = GetOffsetPoint(route[n + 1], heading, distance)									--define climb point position
						climbPoint.id = "Nav"
						climbPoint.alt = profile.hCruise
						table.insert(route, n + 1, climbPoint)															--insert into route
					end
					break
				end
			end
			for n = 3, #route - 2 do																					--iterate through route between join and split point
				if route[n].alt > route[n + 1].alt then																	--descend route leg
					local descendPoint = {}																				--point to start descend
					local heading = GetHeading(route[n], route[n + 1])													--descend point is on route leg
					local distance = math.abs((profile.hCruise - profile.hAttack) * 10)									--distance to descend is 10 times the altitude difference (~-6� pitch) (make sure is positive)
					if distance < GetDistance(route[n + 1], route[n]) then												--if descend distance is longer than route leg distance, ignore descend point
						descendPoint = GetOffsetPoint(route[n], heading, distance)										--define descend point position
						descendPoint.id = "Nav"
						descendPoint.alt = profile.hCruise
						table.insert(route, n + 1, descendPoint)														--insert into route
					end
					break
				end
			end
		elseif profile.hCruise > profile.hAttack then																		--if cruise and attack altitude are not the same, a descend and a climb point must be inserted
			for n = 3, #route - 2 do																					--iterate through route between join and split point
				if route[n].alt < route[n + 1].alt then																	--climb route leg
					local climbPoint = {}																				--point to start climb
					local heading = GetHeading(route[n], route[n + 1])													--climb point is on route leg
					local distance = math.abs((profile.hCruise - profile.hAttack) * 10)									--distance to climb is 10 times the altitude difference (~6� pitch) (make sure is positive)
					if distance < GetDistance(route[n], route[n + 1]) then												--if climb distance is longer than route leg distance, ignore climb point
						climbPoint = GetOffsetPoint(route[n], heading, distance)										--define climb point position
						climbPoint.id = "Nav"
						climbPoint.alt = profile.hCruise
						table.insert(route, n + 1, climbPoint)															--insert into route
					end
					break
				end
			end
			for n = 3, #route - 2 do																					--iterate through route between join and split point
				if route[n].alt > route[n + 1].alt then																	--descend route leg
					local descendPoint = {}																				--point to start descend
					local heading = GetHeading(route[n + 1], route[n])													--descend point is on route leg
					local distance = math.abs((profile.hCruise - profile.hAttack) * 10)									--distance to descend is 10 times the altitude difference (~-6� pitch) (make sure is positive)
					if distance < GetDistance(route[n + 1], route[n]) then												--if descend distance is longer than route leg distance, ignore descend point
						descendPoint = GetOffsetPoint(route[n + 1], heading, distance)									--define descend point position
						descendPoint.id = "Nav"
						descendPoint.alt = profile.hCruise
						table.insert(route, n + 1, descendPoint)														--insert into route
					end
					break
				end
			end
		end
		
		
	elseif task == "Transport" or task == "Nothing" then
		
		--set outbound and inbound routes
		local outbound_navRoute = FindPath(basePoint, targetPoint)														--find the safest outbound route
	
		--set form-up point
		local joinPoint = {}																							--point where package joins on common flight route
		do
			local point																									--join point is between basePoint and this local point
			if #outbound_navRoute.navpoints == 0 then																	--if there is no outbound nav route
				point = targetPoint																						--point is targetPoint
			else																										--if there is an outbound nav route
				point = outbound_navRoute.navpoints[1]																	--point is first nav point
			end
			local heading = GetHeading(basePoint, point)
			
			local distance = math.abs((profile.hCruise - basePoint.h) * 7)												--distance to climb from base elevation to cruise altitude with 8� pitch (make sure distance is positive)
			if distance >= GetDistance(basePoint, point) then															--climb distance bigger than distance to first WP
				distance = GetDistance(basePoint, point) / 3 * 2														--join point is 2/3 to first WP
			elseif distance < 15000 then																				--climb distance less than 15 km
				distance = 15000																						--join point should be at least 15 km from base
			end
			
			joinPoint = GetOffsetPoint(basePoint, heading, distance)													--define join point
		end
		
		--set split point
		local splitPoint = {}																							--point where package splits to land on individual airbases		
		do
			local point																									--split point is between basePoint and this local point
			if #outbound_navRoute.navpoints == 0 then																	--if there is no outbound nav route
				point = joinPoint																						--point is joinPoint
			else																										--if there is an outbound nav route
				point = outbound_navRoute.navpoints[#outbound_navRoute.navpoints]										--point is last nav point
			end
			local heading = GetHeading(targetPoint, point)
			
			local distance = math.abs((profile.hCruise - basePoint.h) * 7)												--distance to descend from cruise alt to base elevation with 8� pitch (make sure distance is positive)
			if distance >= GetDistance(basePoint, point) then															--descend distance bigger than distance to last WP
				distance = GetDistance(basePoint, point) / 3 * 2														--join point is 2/3 to last WP
			elseif distance < 15000 then																				--descend distance less than 15 km
				distance = 15000																						--split point should be at least 15 km from base
			end
			
			splitPoint = GetOffsetPoint(targetPoint, heading, distance)													--define split point
		end
		
		table.insert(route, {x = basePoint.x, y = basePoint.y, id = "Taxi", alt = 0})
		table.insert(route, {x = basePoint.x, y = basePoint.y, id = "Departure", alt = basePoint.h + 1000})
		table.insert(route, {x = joinPoint.x, y = joinPoint.y, id = "Join", alt = profile.hCruise})
		table.insert(route, {x = splitPoint.x, y = splitPoint.y, id = "Split", alt = profile.hCruise})
		table.insert(route, {x = targetPoint.x, y = targetPoint.y, id = "Land", alt = profile.hCruise})
	end
	
	
	--measure lenght of complete route
	local route_lenght = 0
	for n = 1, #route - 1 do
		route_lenght = route_lenght + GetDistance(route[n], route[n + 1])
	end
	route.lenght = route_lenght
	
	
	--evauluate threat level of complete route
	do
		route.threats = {}																								--table to store threats for route
		
		--ground threats
		route.threats.ground = {}																						--table to store ground threats for route
		for alt,threat in pairs(threat_table.ground) do																	--iterate through all ground threat altitudes
			for t = 1, #threat do																						--iterate through all ground threats within altitude band
				for n = 1, #route - 1 do																				--iterate through all route segements
					if route[n + 1].alt == alt then																		--if route segement is in threat altitude
						local distance = GetTangentDistance(route[n], route[n + 1], threat[t])							--distance of route segment to threat
						if distance < threat[t].range then																--if route segment is in range of threat						
							local adjusted_threat = threat[t].level - (threat[t].level / threat[t].range * distance)	--threat adjusted to distance to route leg
							if route.threats.ground[threat[t].x .. "/" .. threat[t].y] then									--if this ground threat already has a threat entry for this route
								if route.threats.ground[threat[t].x .. "/" .. threat[t].y].level < adjusted_threat then		--if the existing threat entry is lower than the new one
									route.threats.ground[threat[t].x .. "/" .. threat[t].y].level = adjusted_threat			--overwrite threat entry with new one
								end
							else																						--if this fighter unit has no threat entry for this route yet
								route.threats.ground[threat[t].x .. "/" .. threat[t].y] = {								--make new threat entry for this ground threat
									level = adjusted_threat,
									offset = threat[t].SEAD_offset
								}
							end
							if threat[t].class == "SAM" then															--threat is a SAM
								if route[n].SEAD_radius then															--waypoint has a SEAD radius entry
									if threat[t].range > route[n].SEAD_radius then										--find longest ranging threat that route segment penetrates
										route[n].SEAD_radius = threat[t].range											--store the range of the threat that route segment penetrates
									end
								else																					--waypoint has no SEAD radius entry
									route[n].SEAD_radius = threat[t].range												--store the range of the threat that route segment penetrates
								end
							end
						end
					end
				end
			end
		end
		
		--air threats
		route.threats.air = {}																										--table to store air threats for route
		for t = 1, #fighterthreats[side_] do																						--iterate through all fighter threats
			if fighterthreats[side_][t].class == "CAP" or fighterthreats[side_][t].class == "Intercept" then
				for n = 1, #route - 1 do																							--iterate through all route segements
					local route_leg_alt
					local route_leg_band
					if route[n].alt >= 3000 and route[n + 1].alt >= 3000 then
						route_leg_alt = profile.hCruise
						route_leg_band = "high"
					else
						route_leg_alt = profile.hAttack
						route_leg_band = "low"
					end
					if GetTangentDistance(route[n], route[n + 1], fighterthreats[side_][t]) < fighterthreats[side_][t].range then	--if route segment is in range of fighter threat
						local ewr_required																							--boolean whether ewr is required for the fighter to be a threat
						if fighterthreats[side_][t].class == "CAP" then																--if the fighter is CAP
							if route_leg_band == "high" then																		--if route leg is at high altitude
								ewr_required = false																				--CAP does not need ewr to be a threat
							else																									--if route leg is at low altitude
								if fighterthreats[side_][t].LDSD then																--if fighter is look down/shoot down capable
									ewr_required = false																			--CAP does not need ewr to be a threat
								else																								--if fighter is not look down/shoot down capable
									-- ATO_RG_Debug02		quand les EWR sont d�truit: on active les CAP, si les CAP on besoin d'EWR c'est nul
									-- ewr_required = true																				--CAP needs ewr to be a threat
								end
							end
						elseif fighterthreats[side_][t].class == "Intercept" then													--if the fighter is an interceptor
							ewr_required = true																						--ewr is required for fighter to be a threat (needs early warning to take off)
						end
						
						if ewr_required == true then																				--fighter needs ewr/awacs station to be a threat
							local break_loop = false
							for e = 1, #threat_table.ewr[route_leg_alt] do															--iterate through all ewr/awacs
								if GetDistance(threat_table.ewr[route_leg_alt][e], fighterthreats[side_][t]) < threat_table.ewr[route_leg_alt][e].range + fighterthreats[side_][t].range then	--fighter operation area and ewr coverage are overlapping
									if GetTangentDistance(route[n], route[n + 1], fighterthreats[side_][t]) < fighterthreats[side_][t].range then				--if route leg is in range of fighter
										if GetTangentDistance(route[n], route[n + 1], threat_table.ewr[route_leg_alt][e]) < threat_table.ewr[route_leg_alt][e].range then	--if route leg is in range of ewr/awacs
											if route.threats.air[fighterthreats[side_][t].name] then															--if this fighter unit already has a threat entry for this route
												if route.threats.air[fighterthreats[side_][t].name].level < fighterthreats[side_][t].level then					--if the existing threat entry is lower than the new one
													route.threats.air[fighterthreats[side_][t].name].level = fighterthreats[side_][t].level						--overwrite threat entry with new one
												end
											else																					--if this fighter unit has no threat entry for this route yet
												route.threats.air[fighterthreats[side_][t].name] = {								--make new threat entry for this fighter unit
													level = fighterthreats[side_][t].level,
												}
											end
											break_loop = true																		--two breaks would be required to break ewr loop and route loop
											break																					--ewr loop
										end
									end
								end
							end
							if break_loop == true then
								break																								--break route segemnt loop and go to next threat
							end
						else																										--no ewr is needed for fighter to be a threat
							if route.threats.air[fighterthreats[side_][t].name] then												--if this fighter unit already has a threat entry for this route
								if route.threats.air[fighterthreats[side_][t].name].level < fighterthreats[side_][t].level then		--if the existing threat entry is lower than the new one
									route.threats.air[fighterthreats[side_][t].name].level = fighterthreats[side_][t].level			--overwrite threat entry with new one
								end
							else																									--if this fighter unit has no threat entry for this route yet
								route.threats.air[fighterthreats[side_][t].name] = {												--make new threat entry for this fighter unit
									level = fighterthreats[side_][t].level,
								}
							end
							break																									--break route segemnt loop and go to next threat
						end
					end
				end
			end
		end
		
		--combine route threats
		route.threats.SEAD_offset = 0																								--counter for SEAD sorties required to offset ground threats
		route.threats.ground_total = 0.5																							--cummulative route ground threat level (0.5 = no threat)
		route.threats.air_total = 0.5																								--cuumulative route air threat level (0.5 = no threat)

		for k,v in pairs(route.threats.ground) do																					--iterate through route ground threats
			route.threats.SEAD_offset = route.threats.SEAD_offset + v.offset														--collect combined SEAD offset
			route.threats.ground_total = route.threats.ground_total + v.level														--sum route ground threat levels
		end
		for k,v in pairs(route.threats.air) do																						--iterate through route air threats
			route.threats.air_total = route.threats.air_total + v.level																--sum route air threat levels
		end
	end
	
	if standoff and standoff > 15000 then																							--if standoff from attack point to target is bigger than 15 km, then target point has not yet been inserted to route in order to calculate threats and route lenght from attack point to egress point
		for r = 1, #route do																										--go through route
			if route[r].id == "Attack" then																							--find attack point
				table.insert(route, r + 1, {x = targetPoint.x, y = targetPoint.y, id = "Target", alt = profile.hAttack})			--insert target point after attack point
				break
			end
		end
	end
	log.level = previous_log_level
	return route
end


function GetEscortRoute(basePoint, orig_route)		
	local previous_log_level = log.level																			--get the escort route given the escort start point and an existing package route
	log.level = function_log_level
	--make a local copy of the route table forwarded as function argument (otherwise the original route gets adjusted
	local route = deepcopy(orig_route)

	-- Miguel21 modification M16.c // ne recopie pas le Spawn des B1b et B-52 en apparation sur une base virtuel en alti
	if route[1].id == "Spawn" then
		route[1].id = "Taxi"
		route[2].id = "Departure"
	end

	--adjust route for escort joining the package
	local join_distance = 99999999																								--shortest distance from escort start point to package route leg
	local WP
	for n = 3, #route - 1 do																									--iterate through route points from Join Point on
		if GetTangentDistance(route[n], route[n + 1], basePoint) < join_distance then											--distance to this route leg is shorter than to previous leg
			join_distance = GetTangentDistance(route[n], route[n + 1], basePoint)												--set new shortest join distance
			WP = n
		else																													--distance to this route leg is longer than to previous leg
			break																												--stop searching
		end
		if route[n + 1].id == "IP" then																							--only search to IP
			break
		end
	end
	
	route[1].x = basePoint.x																									--modify route to start at escort start point
	route[1].y = basePoint.y
	route[2].x = basePoint.x
	route[2].y = basePoint.y
	
	if GetDistance(basePoint, route[WP]) == join_distance then																	--shortest distance to route leg is to first leg waypoint
		route[3].x = route[WP].x
		route[3].y = route[WP].y
		for n = WP, 4, -1 do
			-- table.remove(route, n)	-- ATO_RG_Debug03 supprime trop de waypoint lors de l'escorte
		end
	elseif GetDistance(basePoint, route[WP + 1]) == join_distance then															--shortest distance to route leg is to second leg waypoint
		route[3].x = route[WP + 1].x
		route[3].y = route[WP + 1].y
		for n = WP + 1, 4, -1 do
			-- table.remove(route, n)	-- ATO_RG_Debug03 supprime trop de waypoint lors de l'escorte
		end
	else																														--shortest distance to route leg is between first and second leg waypoint
		local join_heading
		local heading1 = GetHeading(route[WP], route[WP + 1])
		local heading2 = GetHeading(route[WP], basePoint)
		if heading1 - heading2 > 180 then
			heading1 = heading1 - 360
		elseif heading2 - heading1 > 180 then
			heading2 = heading2 - 360
		end
		if heading1 <= heading2 then
			join_heading = heading1 - 90
		else
			join_heading = heading1 + 90
		end
		local mod_joinPoint = GetOffsetPoint(basePoint, join_heading, join_distance)											--modify the Joint Point to be between route leg WP 1 and 2
		route[3].x = mod_joinPoint.x
		route[3].y = mod_joinPoint.y
		for n = WP, 4, -1 do
			-- table.remove(route, n)	-- ATO_RG_Debug03 supprime trop de waypoint lors de l'escorte
		end
	end
	
	--adjust route for escort to leave the package
	local split_distance = 99999999																								--shortest distance from escort end point to package route leg
	for n = #route - 1, 2, -1 do																								--iterate backwards through route points from Split Point on
		if GetTangentDistance(route[n], route[n - 1], basePoint) < split_distance then											--distance to this route leg is shorter than to previous leg
			split_distance = GetTangentDistance(route[n], route[n - 1], basePoint)												--set new shortest split distance
			WP = n
		else																													--distance to this route leg is longer than to previous leg
			break																												--stop searching
		end
		if route[n - 1].id == "Egress" then																						--only search to Egress
			break
		end
	end
	
	route[#route].x = basePoint.x																								--modify route to end at escort land point
	route[#route].y = basePoint.y
	
	if GetDistance(basePoint, route[WP]) == split_distance then																	
		route[#route - 1].x = route[WP].x
		route[#route - 1].y = route[WP].y
		for n = #route - 2, WP, -1 do
			table.remove(route, n)
		end
	elseif GetDistance(basePoint, route[WP - 1]) == split_distance then															
		route[#route - 1].x = route[WP - 1].x
		route[#route - 1].y = route[WP - 1].y
		for n = #route - 2, WP - 1, -1 do
			table.remove(route, n)
		end
	else																														--if a point between last Nav and Split Point is closest to escort land point
		local split_heading
		local heading1 = GetHeading(route[WP], route[WP - 1])
		local heading2 = GetHeading(route[WP], basePoint)
		if heading1 - heading2 > 180 then
			heading1 = heading1 - 360
		elseif heading2 - heading1 > 180 then
			heading2 = heading2 - 360
		end
		if heading1 <= heading2 then
			split_heading = heading1 - 90
		else
			split_heading = heading1 + 90
		end
		local mod_splitPoint = GetOffsetPoint(basePoint, split_heading, split_distance)											--modify the Split Point to be between last Nav and old Split Point
		route[#route - 1].x = mod_splitPoint.x
		route[#route - 1].y = mod_splitPoint.y
		for n = #route - 2, WP, -1 do
			table.remove(route, n)
		end
	end
	
	--measure lenght of complete route
	local route_lenght = 0
	for n = 1, #route - 1 do
		route_lenght = route_lenght + GetDistance(route[n], route[n + 1])
	end
	route.lenght = route_lenght
	log.level = previous_log_level
	return route
end
