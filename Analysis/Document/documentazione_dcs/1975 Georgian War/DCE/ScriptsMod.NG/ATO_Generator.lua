--To create the Air Tasking Order
--Initiated by Main_NextMission.lua
-------------------------------------------------------------------------------------------------------

if not versionDCE then 
	versionDCE = {} 
end

               -- VERSION --

versionDCE["ATO_Generator.lua"] = "OB.1.0.3"

-------------------------------------------------------------------------------------------------------
-- Old_Boy rev. OB.1.0.3: grouping configuration parameters into a single table in camp_init/camp_status
-- Old_Boy rev. OB.1.0.2: implements compute cruise parameters code
-- Old_Boy rev. OB.1.0.1: implements compute firepower code
-- Old_Boy rev. OB.1.0.0: implements logging code 
-- Old_Boy rev. OB.0.0.1: implements code for Logistic 
------------------------------------------------------------------------------------------------------- 
-- Miguel Fichier Revision M38.e
------------------------------------------------------------------------------------------------------ 

-- ATO_G_adjustment03.b support équitable entre escadron
-- ATO_G_adjustment02 TASK Coef
-- ATO_G_adjustment01 escort mandatory or not
-- ATO_G_Debug05 interdit l'escorte avion/helico
-- ATO_G_Debug04.b correction targetName
-- ATO_G_Debug03 mauvaise insertion dans la base
-- ATO_G debug02b haut score
-- ATO_G_debug01 Fin de campagne

-- miguel21 modification M43 assignation des numeros de parking du type C08 
-- miguel21 modification M42 : liveryModex
-- miguel21 modification M38.e Check and Help CampaignMaker (e: loadout Task?)
-- Miguel21 modification M16.b : SpawnAir B1b & B-52 need BaseAirStart = true in db_aibase
-- Modif Miguel21 M13.e Performance Scripting
														-- Modif Miguel21 M12 Loadout option false
-- Miguel21 modification M11.z : Multiplayer			(z: debug MP avec 1 Plane)(y: interdit l'escorte avion/helico) (x: EscorteTot-max) (w: choix EscorteMax) (v: interdit Strike sans escorte)(u: reserve avion Escorte) (t: different Type possible/task)
														-- Miguel21 modification M10 : un maximum d'avion sur Porte Aeronef
-- Miguel21 modification M06 : helicoptere playable

--[[
draft[n] =
local draft_sorties_entry = {
								name = unit[n].name,
								playable = unit[n].player,
								type = unit[n].type,
								helicopter = unit[n].helicopter,
								number = aircraft_assign,
								flights = flights_requested,
								country = unit[n].country,
								livery = unit[n].livery,
								sidenumber = unit[n].sidenumber,
								liveryModex = unit[n].liveryModex,
								base = unit[n].base,
								airdromeId = db_airbases[unit[n].base].airdromeId,
								parking_id = unit[n].parking_id,
								skill = unit[n].skill,
								task = task,
								loadout = unit_loadouts[l],
								target = deepcopy(target),
								target_name = target_name,
								route = route,
								tot_from = tot_from,
								tot_to = tot_to,
								support = {
									["Escort"] = {},
									["SEAD"] = {},
									["Escort Jammer"] = {},
									["Flare Illumination"] = {},
									["Laser Illumination"] = {},
									},
								multipack = multipack,
								threatsGround = route.threats.ground_total,
								threatsAir = route.threats.air_total,
								id = "id"..#draft_sorties[side]+1,
								rejected = {},

playability_criterium = {} --to track what caused lack of playable sortie for the player
aircraft_availability = {} --table to hold availability of aircraft (from camp.aircraft_availability)
draft_sorties = {} --table to store draft sorties (all valid unit/task/loadout/target combinations)
multiPlaneSet = {}


check oob_air units without task and report warn log
create draft_sortie for all avalaible aircaft,
create avalaible tab for sorties, conditions: 
	- active unit,
	- exist an active airbase (unit.base),
	- exist ready unit (roster.read  > 0),
	- unit avalaiability (unit.unavalaible = false)
	- % unit serviceability (unit.serviceability or UNIT_SERVICEABILITY)
removes from aircraft_availability tab, the unavailable units that exceeds the number of roster.ready units or if the current time has exceeded the period of unavailability 
check loadout for specific task of avalaible aircraft
check loadout day time compatibility
search in targetlist an active target task compatible
verify loadout elegibility: if exist target attributes (soft, hard ecc.) check if target.attributes match loadout.attributes
assign aircraft conditions: 
	- airbase
	- target.firepower.min <= aircraft_available * unit_loadouts.firepower(Intercept or Transport task)  or MPOverride
	- loadout weather compatibility
	- target range < loadout.range (strike task or similar)
compute route (ATO_RouteGenerator.getRoute)
check route.lenght <= loadout.range.multiplier and multiplier * loadout.minrange <= route.lenght
requested aircraft = unit.firepower.max / target.firepower 
evalutate flight requested: (tot_to - tot_from)/loadout.tStation (only for CAP, AWACS, Refueling)
assigned aircraft = requested aircraft otherwise avalaible aircraft
evalutate score sortie: 
	- score = loadouts.capability * target.priority CAP and Intercept task
	- score = loadouts.capability * target.priority/route_threar other task
reduce score sorties (only CAP, AWACS and Refueling):
	- reduce_score = ( flights_requested - aircraft_assign ) * loadout.firepower / target.firepower.max for CAP task
	- reduce_score = flights_requested - aircraft_assign for AWACS, Refueling task
update score sorties: score = score - reduce_score * 0.01
update score sorties: score = score = score * unit.tasksCoef[task]	
if MultiplayerOverride -> score = score * 5000
if multiplaneset -> score = score * 10 and score >= 150
create additional draft sorties with support flight assigned, conditions:
	- draft.route.threat.airtotal > MIN_TOTAL_AIR_THREAT for escort
	- draft.route.threat.SEAD_offset > 0  for SEAD
	- draft.route.threat.SEAD_offset > 0 and draft.route.threat.airtotal > MIN_TOTAL_AIR_THREAT for jammer escort
	- always true for other task (laser Illumination, flare Illumination)
	- loadout day time compatibility
	- loadout.vcruise >= draft.loadout.vcruise (primary flight)
	- loadout weather compatibility
	







]]


local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua")
local log_level = LOGGING_LEVEL -- "traceVeryLow" --
local function_log_level = log_level
log.activate = false
log.level = log_level 
log.outfile = LOG_DIR .. "LOG_ATO_Generator." .. camp.mission .. ".log" 
local local_debug = false -- local debug   
local active_log = false
log.debug("Start")

require("Init/db_aircraft")

-- SETTING 
--[[
camp.module_config.ATO_Generator = {

	WEIGHT_SCORE_FOR_LOADOUT_COST = {									-- weight for weapon cost in mission score calculus (0 .. 1)

	["Strike"] = 0.3,
	["Anti-ship Strike"] = 0.1,
	["SEAD"] = 0.1,
	["Intercept"] = 0.2,
	["CAP"] = 0.4,
	["Escort"] = 0.3,
	["Fighter Sweep"] = 0.2,
	["Reconnaissance"] = 0.1,
	},

	WEIGHT_SCORE_FOR_AIRCRAFT_COST = { 								-- weight for aircraft cost in mission score calculus (0 .. 1) 

		["Fighter"] = 0.3, 
		["Attacker"] = 0.5,  
		["Bomber"] = 0.2,  
		["Transporter"] = 0.1, 
		["Reco"] = 0.2, 
		["Refueler"] = 0.1,  
		["AWACS"] = 0.1, 
		["Helicopter"] = 0.2, 
	},

	MINIMUM_REQUESTED_AIRCRAFT_FOR_STRIKE = 2,									-- minimum aircraft for strike and anti-ship strike task (default 2 or 3 -needed to survive the anti-aircraft defenses)
	ESCORT_NUMBER_MULTIPLIER = 3,										-- max multiplier for escort number: when more escorts ESCORT_NUMBER_MULTIPLIER times escorts than escorted aircraft, limit escort number to ESCORT_NUMBER_MULTIPLIER times escorted aircraft (default 3)
	MINIMUM_VALUE_OF_AIR_THREAT = 0.5,									-- minimum value of air threat for air unit with self escort capacity (default = 0.5) 	
	FACTOR_FOR_REDUCTION_AIR_THREAT = 0.5,								-- factor for reduction of air threat for air unit with self escort capacity (default = 0.5)
	SCORE_INFLUENCE_ROUTE_THREAT = 1,									-- (min 1) factor for draft_sorties_entry.score = unit_loadouts[l].capability * target.priority / ( route_threat * SCORE_INFLUENCE_ROUTE_THREAT )
	FACTOR_FOR_REDUCE_SCORE = 0.01, 									-- factor for reduce_score in CAP (score = score - reduce_score * factor)
	MULTIPLIER_TARGET_DISTANCE_FOR_EVALUTATION_UNIT_RANGE_LOADOUT = 2,	-- factor for check if target distance is lesser of support.unit.range route.lenght > unit_loadouts[l].minrange * MULTIPLIER_TARGET_DISTANCE_FOR_EVALUTATION_UNIT_RANGE_LOADOUT) (default = 2)
	MULTIPLIER_TARGET_DISTANCE_FOR_EVALUTATION_COMPUTING_ROUTE = 1.5,  -- factor for check if target distance is bigger of unit.loadout.minrange,  computed before intensive route calculations (getRoute) (ToTarget * MULTIPLIER_TARGET_DISTANCE_FOR_EVALUTATION_COMPUTING_ROUTE > unit_loadouts[l].minrange) (default = 1.5)
	MIN_TOTAL_AIR_THREAT_FOR_ESCORT_SUPPORT = 0.5,						-- min total air threat level to authorize support escort flight (default = 0.5)
	MIN_CLOUD_DENSITY = 0.8,											-- min clouds density for evalutation weather mission condition (defalut = 0.8)
	MIN_FOG_VISIBILITY = 5000,											-- min fog visibility for any task (default: 5000m)
	MIN_CLOUD_EIGHT_ABOVE_AIRBASE = 333,								-- min eight above airbase for execute any task (default: 333m, 1000 ft)
	UNIT_SERVICEABILITY = 0.8,											-- serviceability percentage of unit.roster.ready 
	MIN_PERCENTAGE_FOR_ESCORT = 0.75,									-- min percentage reduction of avalaible asset request for an escort group (for ammissible strike with escort), default 0.75
	MAX_AIRCRAFT_FOR_INTERCEPT = 2,									-- max number of aircraft for an intercept mission 
	MAX_AIRCRAFT_FOR_RECONNAISSANCE = 2, 								-- max number of aircraft for an reconnaisance mission 
	MAX_AIRCRAFT_FOR_STRIKE = 4, 										-- max number of aircraft for an strike mission 
	MAX_AIRCRAFT_FOR_CAP = 4, 											-- max number of aircraft for an cap mission 
	MAX_AIRCRAFT_FOR_ESCORT = 4,		 								-- max number of aircraft for an escort mission 
	MAX_AIRCRAFT_FOR_SWEEP = 4,		 								-- max number of aircraft for an sweep mission 
	MAX_AIRCRAFT_FOR_OTHER = 3,		 								-- max number of aircraft for other mission 
	--MIN_AIRCRAFT_FOR_OTHER = 1, 										-- min number of aircraft for other mission 
	MAX_AIRCRAFT_FOR_BOMBER = 1,										-- max number of aircraft for bomber 
	BOMBERS_RECO = {"S-3B",  "F-117A", "B-1B", "B-52H", "Tu-22M3", "Tu-95MS", "Tu-142", "Tu-160", "MiG-25RBT"},
}
]]

--return true if bomber_type is an element of BOMBERS_RECO table
local function isBomberOrRecoType(bomber_type)
	
	for n = 1, #camp.module_config.ATO_Generator.BOMBERS_RECO do
		
		if bomber_type == camp.module_config.ATO_Generator.BOMBERS_RECO[n] then 
			return true
		end		
	end
	return false
end

--return tot_to (latest Time on target for this loadout) and tot_from (earliest Time on Target for this loadout) for a specific unit loadouts
local function defineToTtiming(isSupportFlight, unit_loadouts)

	if isSupportFlight then
		
		if active_log then log.traceLow("compute tot_to (latest Time on target for this loadout) and tot_from (earliest Time on Target for this loadout) for support flight") end
	else
		
		if active_log then log.traceLow("compute tot_to (latest Time on target for this loadout) and tot_from (earliest Time on Target for this loadout) for primary flight") end
	end

	local tot_from = 0																						--earliest Time on Target for this loadout
	local tot_to = 0																						--latest Time on target for this loadout

	if unit_loadouts.day and unit_loadouts.night then													--loadout is day and night capable										
		tot_from = 0																						--from mission start
		tot_to = camp.mission_duration																		--to mission end
		
		if active_log then log.traceLow("loadout is day and night capable, total time to(camp.mission_duration): " .. tot_to) end

		if not isSupportFlight and task == "Intercept" then																			--for interceptors, tot_to is not limitted by mission duration
			tot_to = 999999
			if active_log then log.traceLow("for interceptors, tot_to is not limitted by mission duration, total time to: " .. tot_to) end
		end

	elseif unit_loadouts.day then																		--loadout is day capable
		
		if daytime == "night-day" then
			tot_from = camp.dawn - camp.time																--from dawn
			tot_to = camp.mission_duration																	--to mission end
			
			if active_log then log.traceLow("daytime == night-day, loadout is only day capable, total time to(camp.mission_duration): " .. tot_to) end

			if not isSupportFlight and task == "Intercept" then																		--for interceptors, tot_to is not limitted by mission duration
				tot_to = camp.dusk - camp.time
				
				if active_log then log.traceLow("daytime == night-day, loadout is only day capable, Intercept task, total time to(camp.mission_duration): " .. tot_to) end
			end

		elseif daytime == "day" then
			tot_from = 0																					--from missiom start
			tot_to = camp.mission_duration																	--to mission end
			
			if active_log then log.traceLow("daytime == day, loadout is day capable, total time to(camp.mission_duration): " .. tot_to) end

			if not isSupportFlight and task == "Intercept" then																		--for interceptors, tot_to is not limitted by mission duration
				tot_to = camp.dusk - camp.time
				
				if active_log then log.traceLow("daytime == day, loadout is day capable, Intercept task, total time to(camp.mission_duration): " .. tot_to) end
			end

		elseif daytime == "day-night" then
			tot_from = 0																					--from mission start
			tot_to = camp.dusk - camp.time																	--to dusk
			
			if active_log then log.traceLow("daytime == day-night, loadout is only day capable, total time to(camp.mission_duration): " .. tot_to) end
		end

	elseif unit_loadouts.night then																		--loadout is night capable

		if daytime == "day-night" then
			tot_from = camp.dusk - camp.time																--from dusk
			tot_to = camp.mission_duration																	--to mission end
			
			if active_log then log.traceLow("daytime == day-night, loadout is night capable, total time to(camp.mission_duration): " .. tot_to) end

			if not isSupportFlight and task == "Intercept" then																		--for interceptors, tot_to is not limitted by mission duration
				tot_to = camp.dawn - camp.time
				
				if active_log then log.traceLow("daytime == day-night, loadout is night capable, Intercept task, total time to(camp.mission_duration): " .. tot_to) end
			end

		elseif daytime == "night" then
			tot_from = 0																					--from mission start
			tot_to = camp.mission_duration																	--to mission end
			
			if active_log then log.traceLow("daytime == night, loadout is night capable, total time to(camp.mission_duration): " .. tot_to) end

			if not isSupportFlight and task == "Intercept" then																		--for interceptors, tot_to is not limitted by mission duration
				tot_to = camp.dawn - camp.time
				
				if active_log then log.traceLow("daytime == night, loadout is night capable, Intercept task, total time to(camp.mission_duration): " .. tot_to)		end
			end

		elseif daytime == "night-day" then
			tot_from = 0																					--from mission start
			tot_to = camp.dawn - camp.time																	--to dawn
			
			if active_log then log.traceLow("daytime == night-day, loadout is night capable, total time to(camp.mission_duration): " .. tot_to) end
		end
	end	
	return tot_from, tot_to
end

-- return weather_eligible (true or false) for a unit with task, loadout in specific mission weather condition
local function checkWeather(mission, unit, unit_loadout, flight_loadout, task, isSupportFlight)
	local weather_eligible = true

	if mission.weather["clouds"]["density"] > camp.module_config.ATO_Generator.MIN_CLOUD_DENSITY then																				--overcast clouds
		local cloud_base = mission.weather["clouds"]["base"]
		local cloud_top = mission.weather["clouds"]["base"] + mission.weather["clouds"]["thickness"]
		if active_log then log.traceVeryLow("overcast clouds, cloud_base: " .. cloud_base .. ", cloud_top: " .. cloud_top) end
		
		if db_airbases[unit.base].elevation + camp.module_config.ATO_Generator.MIN_CLOUD_EIGHT_ABOVE_AIRBASE > cloud_base then																--cloud base is less than 1000 ft above airbase elevation
			if active_log then log.traceVeryLow("cloud base is less than " ..  camp.module_config.ATO_Generator.MIN_CLOUD_EIGHT_ABOVE_AIRBASE .. "m above airbase elevation (" .. db_airbases[unit.base].elevation .. ")") end
		
			if unit_loadout.adverseWeather == false then																		--loadout is not adverse weather capable
				if active_log then log.traceVeryLow("loadout isn't adverse weather capable -> loaout isn't weather eligible for this task: " .. task) end
				weather_eligible = false																							--not eligible for this weather

			else
				if active_log then log.traceVeryLow("loadout is adverse weather capable -> loaout is weather eligible for this task: " .. task) end
			end
		
		else

			if flight_loadout.hCruise and flight_loadout.hCruise > cloud_base and flight_loadout.hCruise < cloud_top then			--cruise alt is in the clouds
				if active_log then log.traceVeryLow("cruise alt for this loadout is in the clouds (" .. flight_loadout.hCruise .. ") ") end
		
				if unit_loadout.adverseWeather == false then																	--loadout is not adverse weather capable
					if active_log then log.traceVeryLow("loadout isn't adverse weather capable -> loaout isn't weather eligible for this task: " .. task) end
					weather_eligible = false																						--not eligible for this weather

				else
					if active_log then log.traceVeryLow("loadout is adverse weather capable -> loaout is weather eligible for this task: " .. task) end
				end

		
			elseif flight_loadout.hAttack and flight_loadout.hAttack > cloud_base and flight_loadout.hAttack < cloud_top then		--attack alt is in the clouds
				
				if unit_loadout.adverseWeather == false then																	--loadout is not adverse weather capable
					if active_log then log.traceVeryLow("loadout isn't adverse weather capable -> loaout isn't weather eligible for this task: " .. task) end
					weather_eligible = false																						--not eligible for this weather

				else
					if active_log then log.traceVeryLow("loadout is adverse weather capable -> loaout is weather eligible for this task: " .. task) end
				end
			end
			
			if not isSupportFlight and ( task == "Strike" or task == "Anti-ship Strike" or task == "Reconnaissance" ) then		--extra requirement for A-G tasks
				if active_log then log.traceLow("extra requirement for A-G tasks in weather capable analisys")		 end

				--print("unit: " .. unit.name .. "-" .. unit.type .. ", task: " .. task .. ", unit_loadout: " .. inspect(unit_loadout))
				if unit_loadout.hAttack > cloud_base then																		--attack alt is above cloud base
					if active_log then log.traceLow("attack alt(" .. unit_loadout.hAttack .. ") is above cloud base(" .. cloud_base .. ")") end
					
					if unit_loadout.adverseWeather == false then																--loadout is not adverse weather capable
						if active_log then log.traceLow("loadout isn't adverse weather capable -> loaout isn't weather eligible for this task: " .. task) end
						weather_eligible = false																					--not eligible for this weather
					
					else
						if active_log then log.traceLow("loadout is adverse weather capable -> loaout is weather eligible for this task: " .. task) end
					end
				end
			end	
		end
	end

	if mission.weather["enable_fog"] == true then															--fog
		if active_log then log.traceLow("mission.weather[enable_fog] == true") end
		
		if db_airbases[unit.base].elevation < mission.weather["fog"]["thickness"] then					--base elevation in fog
			if active_log then log.traceLow("base elevation(" .. db_airbases[unit.base].elevation .. ") in fog(tickness: " .. mission.weather["fog"]["thickness"] .. ")") end
			
			if mission.weather["fog"]["visibility"] < camp.module_config.ATO_Generator.MIN_FOG_VISIBILITY then												--less than 5000m visibility
				if active_log then log.traceLow("visibiliy (" .. mission.weather["fog"]["visibility"] < camp.module_config.ATO_Generator.MIN_FOG_VISIBILITY .. ") less MIN_FOG_VISIBILIY(".. camp.module_config.ATO_Generator.MIN_FOG_VISIBILITY .. ")") end
				
				if unit_loadout.adverseWeather == false then											--loadout is not adverse weather capable
					if active_log then log.traceLow("loadout isn't adverse weather capable -> loaout isn't weather eligible for this task: " .. task) end
					weather_eligible = false																					--not eligible for this weather
				else
					if active_log then log.traceLow("loadout is adverse weather capable -> loaout is weather eligible for this task: " .. task) end
				end																
			end
		end
	end
	return weather_eligible
end

local function round(num)
	local dec = 2
  	local mult = 10^(dec or 0)
  	return math.floor(num * mult + 0.5) / mult
end

-- utilizzata anche da ATO_PlayerAssign
function TrackPlayability(player_unit, criterium)																				--function that tracks whether a playability criterium has been met
	
	if player_unit == true then																									--unit in question is playable by player
		playability_criterium[criterium] = true																					--set playability criterium to be met
	end
end

-- check oob_air units without task
for side,unit in pairs(oob_air) do																								--iterate through all sides	

	for n = 1, #unit do			
		
		for task,task_bool in pairs(unit[n].tasks) do			
			
			if task_bool then			
				
				if db_loadouts[unit[n].type] then					
					
					if not db_loadouts[unit[n].type][task] then						
						log.warn(unit[n].type.." "..task.." not found in db_loadouts")
					end

				else
					log.warn(unit[n].type.." not found in db_loadouts")
				end
			end
		end
	end
end


--status report counters
local status_counter_sorties = 0
local status_counter_escorts = 0
local status_counter_ATO = 0


--to track what caused lack of playable sortie for the player
playability_criterium = {}


--table to hold availability of aircraft
if camp.aircraft_availability == nil then
	camp.aircraft_availability = {}
end
aircraft_availability = camp.aircraft_availability																				--link to table for easier reference

--table to store draft sorties (all valid unit/task/loadout/target combinations)
draft_sorties = {
	blue = {},
	red = {}
}

multiPlaneSet = {}

for k=1, Multi.NbGroup do
	if not multiPlaneSet[Multi.Group[k].PlaneType] then multiPlaneSet[Multi.Group[k].PlaneType] = {} end	
	-- multiPlaneSet[Multi.Group[k].PlaneType][Multi.Group[k].task] = true
	
	if not multiPlaneSet[Multi.Group[k].PlaneType][Multi.Group[k].task] then multiPlaneSet[Multi.Group[k].PlaneType][Multi.Group[k].task] = {} end
	if not multiPlaneSet[Multi.Group[k].PlaneType][Multi.Group[k].task]["NbPlane"] then multiPlaneSet[Multi.Group[k].PlaneType][Multi.Group[k].task]["NbPlane"] = 0 end
	multiPlaneSet[Multi.Group[k].PlaneType][Multi.Group[k].task].NbPlane = Multi.Group[k].NbPlane + multiPlaneSet[Multi.Group[k].PlaneType][Multi.Group[k].task].NbPlane
end

-- _affiche(multiPlaneSet, "ATO_G multiPlaneSet")
-- _affiche(Multi, "ATO_G Multi")
--create draft sorties
for side,unit in pairs(oob_air) do																								--iterate through all sides
	
	--determine enemy_side side
	local enemy_side																													--determine enemy_side side (opposite of unit side)
	if side == "blue" then
		enemy_side = "red"
	else
		enemy_side = "blue"
	end

	for n = 1, #unit do																											--iterate through all units
		
		if unit[n].inactive ~= true then																						--if unit is active
			TrackPlayability(unit[n].player, "active_unit")																		--track playabilty criterium has been met
			if active_log then log.traceLow("unit[" .. n .. "]: " .. unit[n].name .. " is active") end

			if unit[n].player then
				if active_log then log.traceLow("unit[" .. n .. "]: " .. unit[n].name .. " is playable -> insert in trackPlayability tab") end
			end

			
			if db_airbases[unit[n].base] and db_airbases[unit[n].base].inactive ~= true and db_airbases[unit[n].base].x and db_airbases[unit[n].base].y then	--base exists and is active and has a position value (carrier that exists)
				TrackPlayability(unit[n].player, "base")																		--track playabilty criterium has been met
				if active_log then log.traceLow("unit[" .. n .. "]: " .. unit[n].name .. " active base exists: " .. unit[n].base) end
				
				if unit[n].roster.ready > 0 then																				--has ready aircraft
					TrackPlayability(unit[n].player, "ready_aircraft")															--track playabilty criterium has been met
					if active_log then log.traceLow("unit[" .. n .. "]: " .. unit[n].name .. " has ready aircraft: " .. unit[n].roster.ready) end
					
					if aircraft_availability[unit[n].name] == nil then															--unit has no aircraft availability entry yet
						aircraft_availability[unit[n].name] = {}																--make an aircraft availability entry for this unit
					end
					
					if aircraft_availability[unit[n].name].unavailable == nil then												--unit has no unavailable table yet

						if unit[n].unavailable then																				--there are preset unavailabilities in oob_air
							aircraft_availability[unit[n].name].unavailable = unit[n].unavailable								--use this as initial unavailability
						
						else
							aircraft_availability[unit[n].name].unavailable = {}												--create an empty unavailable table
						end
						if active_log then log.traceLow("unit[" .. n .. "]: " .. unit[n].name .. " unit has no unavailable table yet, create new empy table or take the initial defined unavailability tabel: \n" .. inspect(aircraft_availability[unit[n].name].unavailable)) end
					end
					
					--serviceable aircraft
					local aircraft_serviceable = 0																				--serviceable aircraft of unit
					local serviceability = camp.module_config.ATO_Generator[side].UNIT_SERVICEABILITY																	-- defaults unit serviceability rating (0.8)

					if unit[n].serviceability then																				--if serviceability for unit is defined
						serviceability = unit[n].serviceability																	--use it instead
					end
					if active_log then log.traceLow("unit[" .. n .. "]: " .. unit[n].name .. ", serviceability: " .. serviceability) end
					

					for s = 1, unit[n].roster.ready do																			--iterate through ready aircraft

						if math.random(1, 100) <= serviceability * 100 then														--default (serviceability)% chance that it is mission ready
							aircraft_serviceable = aircraft_serviceable + 1														--sum serviceable aircraft
						end
					end
					if active_log then log.traceLow("unit[" .. n .. "]: " .. unit[n].name .. ", computed aircraft_serviceable: " .. aircraft_serviceable) end

					aircraft_availability[unit[n].name].ready = unit[n].roster.ready											--store ready aircraft un availability table
					aircraft_availability[unit[n].name].serviceable = aircraft_serviceable										--store serviceable aircraft in availability table
					
					
					--unavailable aircraft
					local current_time = (camp.day - 1) * 86400 + camp.time														--current absolute campaign time
					local u_entry = 0
					

					if active_log then log.traceLow("Removes from aircraft_availability tab, the unavailable units that exceeds the number of roster.ready units or if the current time has exceeded the period of unavailability ") end
					
					for u = #aircraft_availability[unit[n].name].unavailable, 1, -1 do											--iterate backwards through unavailable aircraft from this unit
						u_entry = u_entry + 1
						
						if u_entry <= unit[n].roster.ready then	 																--for each unavailable entry that is within the amounty of ready aircraft of unit
														
							if current_time > aircraft_availability[unit[n].name].unavailable[u] then --(elimina le #unit unavalaible superiore alle ready)	--check absolute campaign time is past unvailable time for this entry
								if active_log then log.traceLow("u_entry(" .. u_entry .. ") <= unit[n].roster.ready(" .. unit[n].name .. ": " .. unit[n].roster.ready .. "),  and current time has exceeded the period of unavailability for this unit - > remove unit from aircraft_availability table") end
								table.remove(aircraft_availability[unit[n].name].unavailable, u)								--remove this entry
							end
						
						else																									--for each unavailable entry that is beyond the amount of ready aircraft of unit (due to losses in last mission)
							if active_log then log.traceLow("u_entry(" .. u_entry .. ") <= unit[n].roster.ready(" .. unit[n].name .. ": " .. unit[n].roster.ready .. "), and unavailable entry is beyond the amount of ready aircraft of unit (due to losses in last mission) - > remove unit from aircraft_availability table") end
							table.remove(aircraft_availability[unit[n].name].unavailable, u)									--remove this entry
						end
					end

					local aircraft_available = unit[n].roster.ready - #aircraft_availability[unit[n].name].unavailable			--number of available aircraft
					if active_log then log.traceLow("aircraft_available: " .. aircraft_available) end

					if aircraft_serviceable < aircraft_available then
						aircraft_available = aircraft_serviceable
					end

					aircraft_availability[unit[n].name].available = aircraft_available											--store available aircraft in availability table
					aircraft_availability[unit[n].name].assigned = 0
					aircraft_availability[unit[n].name].unassigned = aircraft_available											--store unassigned aircraft in availability table
					if active_log then log.traceLow("aircraft_available: " .. aircraft_available) end

					if aircraft_available > 0 then																				--unit has available aircraft
						TrackPlayability(unit[n].player, "available_aircraft")													--track playabilty criterium has been met						
						
						for task,task_bool in pairs(unit[n].tasks) do																		--iterate through all tasks of unit		

							if task_bool and task ~= "SEAD" and task ~= "Escort" and task ~= "Escort Jammer" and task ~= "Flare Illumination" and task ~= "Laser Illumination" then		--task is true and is no support task
								if active_log then log.traceLow("exist task but no support task(SEAD, Escort, Escort Jammer, Flare Illumination, Laser Illumination), task: " .. task) end
								
								--get possible loadouts
								local unit_loadouts = {}																					--table to hold all loadouts for this aircraft type and task
								
								if db_loadouts[unit[n].type][task] then																		--db_loadouts table has loadouts for this task
									if active_log then log.traceLow("db_loadouts table has loadouts for this task") end
									
									for loadout_name, ltable in pairs(db_loadouts[unit[n].type][task]) do									--iterate through all loadouts for the aircraft type and task
										
										if ltable.country == nil or ltable.country == unit[n].country then									--loadout is country unspecific or applies to unit country
											ltable.name = loadout_name																		--store loadout name
											-- table.insert(unit_loadouts, ltable)															--add loadout to local table
											unit_loadouts[#unit_loadouts+1] = ltable
											if active_log then log.traceLow("loadout is country unspecific or applies to unit country, loadout_name: " .. loadout_name .. ", add loadout to unit_loadouts table") end
										end
									end
								end
																
								for l = 1, #unit_loadouts do																				--iterate through all available loadouts													
									tot_from, tot_to = defineToTtiming(false, unit_loadouts[l])									
									
									if tot_to < 0 then
										tot_to = tot_to + 86400 -- + 24h (se tot_from < 0 -> nuovo giorno!?)
									end

									if tot_from < 0 then
										tot_from = tot_from + 86400 -- + 24h (se tot_from < 0 -> nuovo giorno!?)
									end
									
									if tot_from ~= 0 or tot_to ~= 0 then																	--loadout has an eligible time on target
										if active_log then log.traceLow("tot_from: " .. tot_from ..", tot_to: " .. tot_to) end

										if tot_from == 0 then																				--player is only allowed to start at mission start
											TrackPlayability(unit[n].player, "tot")															--track playabilty criterium has been met
										end																				
										i_timmer01 = 0
										if active_log then log.traceLow("iterate through in targetlist") end

										for target_side_name, target_side in pairs(targetlist) do											--iterate through sides in targetlist															
											i_timmer01 = i_timmer01 + 1
											
											if side == target_side_name then --if the target is hostile
												if active_log then log.traceLow("target is hostile (side == target_side_name = " .. side .. ")") end
												
												-- debug code
												if isLogNoUpper(log_level,"debug") then
												
													for target_name, target in pairs(target_side) do
														local attr = "attr: "
														local xcoord, ycoord

														if target.slaved then
															attr = attr .. "slaved"	
														end													

														if target.x then 
															xcoord = tostring(target.x )
														else
															xcoord = "not x"
														end

														if target.y then 
															ycoord = tostring(target.y )
														else
															ycoord = "not y"
														end		
														
														if ycoord == "not y" or xcoord == "not x" then											
															if active_log then log.debug("target: " .. target_name .. ", task: " .. target.task .. ", side: " .. side .. " - coord: ".. xcoord .. ", " .. ycoord) end
															if active_log then log.debug("attributes: " .. attr) end
														end
													end
												end
												-- end debug code

												for target_name, target in pairs(target_side) do
													if active_log then log.traceVeryLow("target: " .. target_name .. ", side: " .. side) end
													
													
													if active_log then log.traceVeryLow("target coord: ".. (target.x or "nil") .. ", " .. (target.y or "nil") ) end
													

													if target.inactive ~= true and target.ATO then											--if target is active and should be added to ATO
														if active_log then log.traceLow("target is active and signed for added to ATO") end

														if target.task == task then															--if target is valid for aircaft-loadout
															if active_log then log.traceLow("target is valid for aircaft-loadout, task: " .. task) end

															
															MultiPlayerOveRide = false

															if Multi.Target and Multi.Target[side] == target_name  then
																MultiPlayerOveRide = true
																if active_log then log.traceVeryLow("Multi.Target[side] == target_name (" .. target_name .. ")") end
															end
															
															--check target/loadout attributes
															if active_log then log.traceVeryLow("check target/loadout attributes") end
															local loadout_eligible = true																					--boolean if loadout matches any target attributes (default true, because target might have no attributes)
															
															if target.attributes[1] then																					--target has attributes
																loadout_eligible = false
																if active_log then log.traceVeryLow("one target attibutes exist: " .. target.attributes[1]) end
																
																for target_attribute_number, target_attribute in ipairs(target.attributes) do								--Iterate through target attributes
																	if active_log then log.traceVeryLow("target attibutes(" .. target_attribute_number .. "): " .. target_attribute) end
																	
																	for loadout_attribute_number, loadout_attribute in ipairs(unit_loadouts[l].attributes) do				--Iterate through loadout attributes
																																				
																		if target_attribute == loadout_attribute then														--if match is found
																			if active_log then log.traceVeryLow("target_attribute(" .. target_attribute .. ") == unit_loadouts[" .. l .. "].loadout_attribute, this loadout is eligible") end
																			loadout_eligible = true																			--set variable true
																			break																							--break the loadout attributes iteration
																		end
																	end
																end
															end
															
															if loadout_eligible then	
																--continue if loadout is eligible
																if (task == "Intercept" and target.base == unit[n].base) or (task == "Transport" and target.base == unit[n].base) or (task == "Nothing" and target.base == unit[n].base) or (task ~= "Intercept" and task ~= "Transport" and task ~= "Nothing") then	--intercept and transport missions are only assigned to units of a certain base as per targetlist	
																	TrackPlayability(unit[n].player, "target")																							--track playabilty criterium has been met																	
																	if active_log then log.traceVeryLow("task is intercept or transport and target.base == unit[" .. n .. "].base: " .. (target.base or "traget.base == nil and task ~= Intercept and task ~= Transport and task ~= Nothing (intercept and transport missions are only assigned to units of a certain base as per targetlist)")) end

																	if target.firepower.min <= aircraft_available * unit_loadouts[l].firepower or MultiPlayerOveRide then				--enough aircraft are available to satisfy minimum firepower requirement of target	
																		TrackPlayability(unit[n].player, "target_firepower")																			--track playabilty criterium has been met
																		if active_log then log.traceVeryLow("target.firepower.min(" .. target.firepower.min .. ") <= aircraft_available(" .. aircraft_available .. ") * unit_loadouts[" .. l .. "].firepower(" .. unit_loadouts[l].firepower .. ") or MultiPlayerOveRide(" .. tostring(MultiPlayerOveRide) .. ") is true") end

																	
																		--check weather															
																		local weather_eligible = checkWeather(mission, unit[n], unit_loadouts[l],  unit_loadouts[l], task, false)
																		if active_log then log.traceLow("check weather") end																		
																		
																		if weather_eligible then																				--continue of this loadout is eligible for weather
																			TrackPlayability(unit[n].player, "weather")															--track playabilty criterium has been met
																			if active_log then log.traceLow("this loadout is weather elegible for this task: " .. task) end
																			
																			--get airbase position
																			local airbasePoint = {																				--get the x-y coordinates of the airbase where the unit is located
																				x = db_airbases[unit[n].base].x,
																				y = db_airbases[unit[n].base].y,
																				h = db_airbases[unit[n].base].elevation,
																				BaseAirStart = db_airbases[unit[n].base].BaseAirStart
																			}
																			

																			if airbasePoint.x == nil then
																				log.warn("ANOMALY airbasePoint.x == nil, was a carrier!?")																			
																			end

																			if airbasePoint.y == nil then
																				log.warn("ANOMALY airbasePoint.y == nil, was a carrier!?")																																							
																			end

																			local multipack = 1
																			
																			if target.firepower.packmax and unit_loadouts[l].MaxAttackOffset then								--target has a requirement for multiple packages and loadout is multipack capable (defined maximum attack offset)
																				multipack = target.firepower.packmax															--create draft sorties for this target for the requested amount of packages
																				if active_log then log.traceLow("target has a requirement for multiple packages and loadout is multipack capable (defined maximum attack offset), start to create " .. multipack .. " sorties request for this package") end
																			end
																			
																			for r = 1, multipack do																				--repeat draft sortie generation for the requirement amount of packages (may create different routes each time)
																				if active_log then log.traceLow("start to generate #: " .. r .. " sorties for this package") end
																				--determine route variants depending on daytime
																				local variant
																			
																				if daytime == "day" then
																					variant = 1
																			
																				elseif daytime == "night" then
																					variant = 2
																			
																				elseif daytime == "night-day" then
																					variant = 3
																			
																				elseif daytime == "day-night" then
																					variant = 4
																				end
																			
																				while variant > 0 do --serve per ripetere il loop quando "night-day" -> day e day-night -> night
																					i_timmer01 = i_timmer01 +1
																					
																					if i_timmer01 >= 10  then 
																						io.write(".") 
																						i_timmer01 = 0 
																					end
																					--determine route
																					status_counter_sorties = status_counter_sorties + 1													--status report
																					local route = {}
																					
																					if task == "Intercept" then																			--intercept task only get a stub route
																						route = {
																							[1] = {
																								['y'] = airbasePoint.y,
																								['x'] = airbasePoint.x,
																								['alt'] = 0,
																								['id'] = 'Intercept',
																							},
																							threats = {
																								SEAD_offset = 0,
																								ground_total = 0.5,
																								air_total = 0.5
																							},
																							['lenght'] = target.radius * 2,																--interception task radius *2 because below it is compared with range *2
																						}
																						if active_log then log.traceLow("task is Intercept, define initial route property: first route point is airbase: (" .. (airbasePoint.x or "nil") .. ", " .. (airbasePoint.y or "nil") .. "), mission lenght(target.radius * 2): " .. target.radius * 2) end
																					
																					else --all other tasks than intercept																								
																						
																						if active_log then log.traceLow("task: " .. task) end
																						if active_log then log.traceLow("r: " .. r .. ", variant: " .. variant  .. ", base: " .. unit[n].base .. "airbasePoint: " .. (airbasePoint.x or "nil") .. ", " .. (airbasePoint.y or "nil") .. ", target: " .. target_name) end

																						if target.x ~= nil and target.y ~= nil then
																							if active_log then log.info("target coord: ".. target.x .. ", " .. target.y) end													
																						end
																						--print("unit: " .. unit[n].name .. "-" .. unit[n].type .. ", task: " .. task .. ", target: " .. target_name .. ", side: " .. side .. ", target coord: ".. (target.x or "nil") .. ", " .. (target.y or "nil"))
																						local ToTarget = GetDistance(airbasePoint, target)											--direct distance to target
																						if active_log then log.traceLow("direct distance to target: " .. ToTarget) end
																						
																						
																						if ToTarget <= unit_loadouts[l].range and (unit_loadouts[l].minrange == nil or ToTarget * camp.module_config.ATO_Generator[side].MULTIPLIER_TARGET_DISTANCE_FOR_EVALUTATION_COMPUTING_ROUTE > unit_loadouts[l].minrange) then	--basic feasibility check of range before performance intensive route calculations are done
																							if active_log then log.traceLow("target is in range") end
																							if active_log then log.traceLow("ToTarget(" .. ToTarget .. ") <= unit_loadouts[l].range(" .. unit_loadouts[l].range .. ") and (unit_loadouts[l].minrange(" .. (unit_loadouts[l].minrange or "nil") .. ") == nil or ToTarget * (" .. camp.module_config.ATO_Generator[side].MULTIPLIER_TARGET_DISTANCE_FOR_EVALUTATION_COMPUTING_ROUTE .. ") > unit_loadouts[l].minrange))") end

																							if variant == 1 or variant == 4 then
																								if active_log then log.traceLow("daytime is day or day-night, compute route: getRoute(airbasePoint(" .. (airbasePoint.x or "nil") .. ", " .. (airbasePoint.y or "nil") .. "), target(" .. target_name .. "), unit_loadouts[" .. l .. "], enemy_side(" .. enemy_side .. "), task(" .. task .. "), day, r(" .. r .. "), multipack(" .. multipack .. "), unit[n].helicopter(" .. tostring(unit[n].helicopter) .. "))") end
																								route = GetRoute(airbasePoint, target, unit_loadouts[l], enemy_side, task, "day", r, multipack, unit[n].helicopter)			--get the best route to this target at day-- Miguel21 modification M06 : helicoptere playable(ajout variable helico pour generer une route )

																							elseif variant == 2 or variant == 3 then																
																								if active_log then log.traceLow("daytime is day or day-night, compute route: getRoute(airbasePoint(" .. (airbasePoint.x or "nil") .. ", " .. (airbasePoint.y or "nil") .. "), target(" .. target_name .. "), unit_loadouts[" .. l .. "], enemy_side(" .. enemy_side .. "), task(" .. task .. "), night, r(" .. r .. "), multipack(" .. multipack .. "), unit[n].helicopter(" .. tostring(unit[n].helicopter) .. "))" .. ", loadout name: " .. unit_loadouts[l].name .. ", unit: " .. unit[n].type .. "-" .. unit[n].name) end
																								route = GetRoute(airbasePoint, target, unit_loadouts[l], enemy_side, task, "night", r, multipack, unit[n].helicopter)		--get the best route to this target at night-- Miguel21 modification M06 : helicoptere playable
																							end
																						end																						
																					end
																					
																					if (target.x == nil or target.y == nil) then
																						log.warn("target: " .. target_name .. " has nil coord")
																					end																					
																					if active_log then log.traceLow("target coord: ".. (target.x or "nil") .. ", " .. (target.y or "nil")) end

																					if route.lenght and route.lenght <= unit_loadouts[l].range * camp.module_config.ATO_Generator[side].MULTIPLIER_TARGET_DISTANCE_FOR_EVALUTATION_UNIT_RANGE_LOADOUT and (unit_loadouts[l].minrange == nil or route.lenght > unit_loadouts[l].minrange * camp.module_config.ATO_Generator[side].MULTIPLIER_TARGET_DISTANCE_FOR_EVALUTATION_UNIT_RANGE_LOADOUT) then		--if sortie route lenght is within range of aircraft-loadout
																						TrackPlayability(unit[n].player, "target_range")												--track playabilty criterium has been met
																						
																						--determine number of aircraft needed for sortie
																						local aircraft_requested = target.firepower.max / unit_loadouts[l].firepower					--how many aircraft are needed to satisfy the maximum firepower requirement of the target
																						if active_log then log.trace("aircraft neededs for this task(" .. task .. "): " .. aircraft_requested .. "target.firepower.max: " .. target.firepower.max .. ", unit_loadouts[" .. l .. "].firepower: " .. unit_loadouts[l].firepower) end

																						local flights_requested	
																						
																						if task == "CAP" or task == "AWACS" or task == "Refueling" then									--multiple flights are required to continously cover a station for the duration of the mission
																							flights_requested = math.ceil((tot_to - tot_from) / unit_loadouts[l].tStation) + 1			--how many flights are needed to keep continous coverage of station, plus 1 for on station before mission start
																							aircraft_requested = aircraft_requested * flights_requested									--total number of requested aircraft is number of aircraft needed to statisfy firepower requirement of station * number of flights needed for continous coverage
																							if active_log then log.traceLow("tot_to - tot_from for this task(" .. task .. "): " .. tostring(tot_to - tot_from) .. " and unit_loadouts[l].tStation: " .. unit_loadouts[l].tStation) end
																							if active_log then log.trace("flights_requested for this task(" .. task .. "): " .. flights_requested) end
																						end
																						
																						if task == "AWACS" or task == "Refueling" or task == "Transport" or task == "Nothing" or task == "Reconnaissance" then
																							aircraft_requested = math.ceil(aircraft_requested)											--round up
																						
																						elseif isBomberOrRecoType(unit[n].type) then
																							aircraft_requested = math.ceil(aircraft_requested)											--round up
																						
																						else
																							--aircraft_requested = math.ceil(aircraft_requested / 2) * 2								--round up to an even number
																							aircraft_requested = math.ceil(aircraft_requested)											--round up

																							if aircraft_requested == 1 then
																								aircraft_requested = camp.module_config.ATO_Generator[side].MINIMUM_REQUESTED_AIRCRAFT_FOR_STRIKE
																							end
																						end
																						if active_log then log.trace("total aircraft_requested for this task(" .. task .. "): " .. aircraft_requested) end
																						local aircraft_assign
																				
																						if aircraft_requested > aircraft_available then													--if more aircraft are requested than are available from this unit
																							aircraft_assign = aircraft_available														--assign all available aircraft
																							if active_log then log.trace("aircraft_available (" .. aircraft_available .. ") < aircraft_requested (" .. aircraft_requested .. ")for this task(" .. task .. ")") end
																				
																						else																							--enough available aircraft to satisfy requested aircraft
																							aircraft_assign = aircraft_requested														--assign all requested aicraft
																							if active_log then log.trace("aircraft_assigned for this task(" .. task .. "): " .. aircraft_assign) end
																						end
																						
																						-- miguel21 modification M11.o multiplayer
																						if multiPlaneSet then
																				
																							if multiPlaneSet[unit[n].type]  and multiPlaneSet[unit[n].type][task] then	--and task ~= "CAP" and task ~= "Intercept"																																															
																								--M11.z
																								if aircraft_assign < multiPlaneSet[unit[n].type][task].NbPlane then
																									aircraft_assign = multiPlaneSet[unit[n].type][task].NbPlane
																									if active_log then log.trace("multiPlaneset presents (multiplayer) for these unit[" .. n .. "].type(" .. unit[n].type .. ") and unit[n].type][task](" .. multiPlaneSet[ unit[n].type][task] .. "), aircraft_assign: " .. aircraft_assign) end
																								end																								
																							end
																						end
																				
																						--self escort
																						if unit_loadouts[l].self_escort then															--if the loadout is capable of self-escort																							
																							route.threats.air_total = route.threats.air_total * camp.module_config.ATO_Generator[side].FACTOR_FOR_REDUCTION_AIR_THREAT										--reduce the fighter threat by half
																							
																					
																							if route.threats.air_total < camp.module_config.ATO_Generator[side].MINIMUM_VALUE_OF_AIR_THREAT then
																								route.threats.air_total = camp.module_config.ATO_Generator[side].MINIMUM_VALUE_OF_AIR_THREAT
																							end
																							if active_log then log.traceLow("loadout is capable of self-escort, reduce the fighter threat by half (minimum 0.5): " .. route.threats.air_total) end
																						end
																						
																						--build sortie entry
																						repeat																							--for tasks with station repeat to make entries for lesser amount of aircraft, repeat once for everything else
																							
																							local draft_sorties_entry = {
																								name = unit[n].name,
																								playable = unit[n].player,
																								type = unit[n].type,
																								helicopter = unit[n].helicopter,
																								number = aircraft_assign,
																								flights = flights_requested,
																								country = unit[n].country,
																								livery = unit[n].livery,
																								sidenumber = unit[n].sidenumber,
																								liveryModex = unit[n].liveryModex,
																								base = unit[n].base,
																								airdromeId = db_airbases[unit[n].base].airdromeId,
																								parking_id = unit[n].parking_id,
																								skill = unit[n].skill,
																								task = task,
																								loadout = unit_loadouts[l],
																								target = deepcopy(target),
																								target_name = target_name,
																								route = route,
																								tot_from = tot_from,
																								tot_to = tot_to,
																								support = {
																									["Escort"] = {},
																									["SEAD"] = {},
																									["Escort Jammer"] = {},
																									["Flare Illumination"] = {},
																									["Laser Illumination"] = {},
																									},
																								multipack = multipack,
																								threatsGround = route.threats.ground_total,
																								threatsAir = route.threats.air_total,
																								id = "id"..#draft_sorties[side]+1,
																								rejected = {},
																							}
																							draft_sorties_entry.target.TitleName =  target_name													-- ATO_G_Debug04 correction targetName																																																																
																							if active_log then log.traceVeryLow("new draft_sorties_entry:\n" .. inspect(draft_sorties_entry)) end

																							--score the sortie
																							local route_threat = route.threats.ground_total + route.threats.air_total							--combine route ground and air threat
																							if active_log then log.traceLow("target: " .. target_name .. ", route_threat total: " .. route_threat .. ", (air: " .. route.threats.air_total .." + ground: " .. route.threats.ground_total .. ")") end
																				
																							 -- Compute score for CAP or Intercept
																							if task == "CAP" or task == "Intercept" then
																								draft_sorties_entry.score = unit_loadouts[l].capability * target.priority					--route threat does not matter for CAP and intercept
																								if active_log then log.traceLow(" task is CAP or Intercept, compute score without threat: draft_sorties_entry.score(" .. draft_sorties_entry.score .. ") = unit_loadouts[" .. l .. "].capability(" .. unit_loadouts[l].capability .. ") * target.priority(" .. target.priority .. ")") end
																							
																							-- Compute score for Fighter Sweep, Strike, Anti-ship Strike, Transport, Refueling, Reco
																							else 
																								draft_sorties_entry.score = unit_loadouts[l].capability * target.priority / ( route_threat * camp.module_config.ATO_Generator[side].SCORE_INFLUENCE_ROUTE_THREAT )		--calculate the score to measure the importance of the sortie
																								if active_log then log.traceLow(" task(" .. task .."), draft_sorties_entry.score(" .. draft_sorties_entry.score .. ") = unit_loadouts[" .. l .. "].capability(" .. unit_loadouts[l].capability .. ") * target.priority(" .. target.priority .. ") / route_threat(" .. route_threat .. ")") end
																							end
																							local reduce_score = 0																				--factor to reduce score for station missions with less aircraft than required to cover station
																							
																							 -- Compute reduction score for CAP
																							if task == "CAP" then																				--station tasks with flights of 2
																								reduce_score = flights_requested - aircraft_assign / math.ceil(target.firepower.max / unit_loadouts[l].firepower) --increase factor by one for each flight that is missing
																								if active_log then log.traceLow("task is CAP, compute reduce score(" .. reduce_score .. ") =  flights_requested(" .. flights_requested .. ") - aircraft_assign(" .. aircraft_assign .. ") / math.ceil(target.firepower.max)(" .. math.ceil(target.firepower.max) .. " / unit_loadouts[l].firepower(" .. unit_loadouts[l].firepower .. "))" ) end																								
																							
																							-- Compute reduction score for AWACS or Refueling
																							elseif task == "AWACS" or task == "Refueling"  then													--station tasks with flights of 1
																								reduce_score = flights_requested - aircraft_assign												--increase factor by one for each flight that is missing
																								if active_log then log.traceLow("task is AWACS or Refueling, compute reduce score(" .. reduce_score .. ") =  flights_requested(" .. flights_requested .. ") - aircraft_assign(" .. aircraft_assign .. ")") end
																							
																							end

																							-- update reduction for aircraft cost
																							local unit_role = getRole(draft_sorties_entry.type, task, side) -- return the primary role: CAP, SWEEP, Intercept = Fighter, Strike, Anti-ship Strike = Attack or Bomber, AWACS, Refueling or Transport same
																							if active_log then log.traceLow("draft_sorties_entry.type: " .. draft_sorties_entry.type .. ", task: " .. task .. ", side: " .. side .. ", unit_role: " .. ( unit_role or "nil") ) end
																							local cost_factor = db_aircraft[side][draft_sorties_entry.type].factor[unit_role] or 0 -- bigger cost -> lesser factor
																																														
																							if active_log then log.traceLow("EVALUTATE FACTOR COST: task: " .. task .. ", aircraft: " .. draft_sorties_entry.type .. ", unit_role: " .. unit_role .. ", score: " .. draft_sorties_entry.score) end
																							if active_log then log.traceLow("cost ( db_aircraft[" .. side .. "][" .. draft_sorties_entry.type .. "].factor[" .. unit_role .. "] ): " .. (db_aircraft[side][draft_sorties_entry.type].factor[unit_role] or "nil" ) .. ", cost: " .. cost_factor) end

																							-- Update score with factor_cost
																							local aircraft_cost_factor = ( 1 + camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_AIRCRAFT_COST[unit_role] * cost_factor ) -- bigger aircraft cost -> lesser factor cost --> lesser aircraft_cost_factor
																							local loadout_cost_factor = ( 1 + ( camp.module_config.ATO_Generator[side].WEIGHT_SCORE_FOR_LOADOUT_COST[task] or 0 ) * ( unit_loadouts[l].cost_factor or 0 ) )	-- bigger loadouts cost -> lesser loadout factor	--> lesser loadout_cost_factor 																					
																							draft_sorties_entry.score = ( draft_sorties_entry.score - reduce_score * camp.module_config.ATO_Generator[side].FACTOR_FOR_REDUCE_SCORE ) * aircraft_cost_factor * loadout_cost_factor
																							if active_log then log.traceLow("Update score with factor_cost: side: " .. side .. ", aircraft: " .. draft_sorties_entry.type .. ", unit_role: " .. unit_role .. ", aircraft_cost_factor: " .. aircraft_cost_factor .. ", loadout_cost_factor: " .. loadout_cost_factor .. ", score: " .. draft_sorties_entry.score) end																				
																							
																							-- Update score with SCORE_TASK_FACTOR
																							if task == "Strike" then
																								draft_sorties_entry.score = draft_sorties_entry.score * camp.module_config.SCORE_TASK_FACTOR[side][task][target.attributes[1]] 	--reduce score slighthly for station missions with less aircraft than required to cover station																									
																							
																							else
																								draft_sorties_entry.score = draft_sorties_entry.score * camp.module_config.SCORE_TASK_FACTOR[side][task] 							--reduce score slighthly for station missions with less aircraft than required to cover station
																							end																						
																							if active_log then log.traceLow("side: " .. side .. ", aircraft: " .. draft_sorties_entry.type .. ", unit_role: " .. unit_role .. ", score: " .. draft_sorties_entry.score) end
																							if active_log then log.traceLow("update draft_sorties_entry.score(" .. draft_sorties_entry.score .. ") = draft_sorties_entry.score - reduce_score(" .. reduce_score .. ") * " .. camp.module_config.ATO_Generator[side].FACTOR_FOR_REDUCE_SCORE .. ")") end
																							
																							--ATO_G_adjustment02 -- Update score with unit.taskCoeff 
																							if unit[n].tasksCoef and unit[n].tasksCoef[task] then
																								draft_sorties_entry.score = draft_sorties_entry.score * unit[n].tasksCoef[task]		--aumenta lo score di un fattore pari al taskcoeff (ha senso)																				 
																								if active_log then log.traceLow("for this task(" .. task .. ") unit(" .. unit[n].name .. " - " .. unit[n].type .. " have taskcoeff: " .. unit[n].tasksCoef[task] .. ", update draft_sorties_entry.score = " .. draft_sorties_entry.score) end
																							end
																							
																							-- miguel21 modification M11.q multiplayer
																							if multiPlaneSet then
																				
																								if multiPlaneSet[unit[n].type] and  multiPlaneSet[unit[n].type][task]  then  					--and task ~= "CAP" and task ~= "Intercept"
																				
																									if Multi.Target and Multi.Target[side] then
																				
																										if MultiPlayerOveRide then 	
																											draft_sorties_entry.score = draft_sorties_entry.score * 50000																											
																											-- print("ATO_G Type: "..unit[n].type.." AfterScore: "..draft_sorties_entry.score.." target_name: "..target_name)
																										end

																									else
																										draft_sorties_entry.score = draft_sorties_entry.score * 10								-- augmente le score pour avoir plus de chance d'avoir l'avion dispo	
																				
																										if draft_sorties_entry.score < 200 then 
																											draft_sorties_entry.score = draft_sorties_entry.score + 150
																										end
																										if active_log then log.traceLow("multiPlaneset presents (multiplayer) for these unit[" .. n .. "].type(" .. unit[n].type .. ") and unit[n].type][task](" .. multiPlaneSet[ unit[n].type][task] .. "), update draft_sorties_entry.score: " .. draft_sorties_entry.score) end
																									end
																								end	
																							end			
																							--insert sortie entry into draft_sorties table sorted by score (highest first)
																							if active_log then log.traceLow("insert sortie entry into draft_sorties table sorted by score (highest first)") end																																										
																							
																							if #draft_sorties[side] == 0 then															--if draft_sorties table is empty
																								-- table.insert(draft_sorties[side], draft_sorties_entry)
																								draft_sorties[side][#draft_sorties[side]+1] = draft_sorties_entry
																				
																							else

																								for d = 1, #draft_sorties[side] do																		--iterate through draft_sorties
																									
																									--if not draft_sorties_entry.score or not draft_sorties[side][d].score then					
																										--log.warn("d: " .. d .. ", side: " .. side ..", task: " .. tsk .. ", draft_sorties[side][d].score: " .. (draft_sorties[side][d].score or "nil") .. ", draft_sorties_entry.score: " .. (draft_sorties_entry.score or "nil"))
																									--end
																									local da1
																									if draft_sorties_entry.score > draft_sorties[side][d].score then					--score is bigger than current table entry
																										-- table.insert(draft_sorties[side], d, draft_sorties_entry)	--RIPRISTINA QUESTO				--insert at current position in table (e scala le altre nelle posizioni sccessiva, quindi il più alto è nella posizione 1)
																										draft_sorties[side][#draft_sorties[side]+1] = draft_sorties_entry				-- qui la aggiunge alla fine e quindi il più alto è alla fine
																										if active_log then log.traceLow("the draft_sorties_entry have bigger score of element in draft_sorties[" .. side .. "][" .. d .. "], insert in " .. d .. " position") end
																										break
																				
																									elseif draft_sorties_entry.score == draft_sorties[side][d].score then				--score is same as current table entry
																										local sum = 1
																				
																										for s = d + 1, #draft_sorties[side] do											--iterate through subsequent table entries
																				
																											if draft_sorties_entry.score == draft_sorties[side][s].score then			--if these entries also have the same score
																												sum = sum + 1															--sum them
																				
																											else
																												break
																											end
																										end
																										da1 = math.random(0, sum)
																										table.insert(draft_sorties[side], da1 + d, draft_sorties_entry)	--insert random position position in table
																										-- draft_sorties[side][d + math.random(0, sum)] = draft_sorties_entry
																										if active_log then log.traceLow("the draft_sorties_entry have same score of element in draft_sorties[" .. side .. "][" .. d .. "], insert in " .. da1 + d .. " position") end
																										break
																				
																									elseif d == #draft_sorties[side] then												--if end of table is reached
																										-- draft_sorties_entry["id"] = "id"..#draft_sorties[side]+1
																										draft_sorties[side][#draft_sorties[side]+1] = draft_sorties_entry 				-- aggiunge la nuova entry con score inferiore a tutti gli altri elementi presenti nella tabella, all fine della stessa
																										if active_log then log.traceLow("the draft_sorties_entry have lesser score of all elements in draft_sorties[" .. side .. "], insert in " .. #draft_sorties[side]+1 .. " (last) position. Is correct??") end
																									end
																								end
																							end
																							if active_log then log.traceVeryLow("complete draft_sorties[" .. side .. "]: " .. inspect( draft_sorties[side] )) end
																				
																							if task == "CAP" or task == "AWACS" or task == "Refueling"  then
																								aircraft_assign = aircraft_assign - 1													--make additional draft sortie for lesser amount of aircraft																								
																								if active_log then log.traceLow("task: " .. task .. ", make additional draft sortie for lesser amount of aircraft, aircraft_assign: " .. aircraft_assign) end
																							
																							else
																								aircraft_assign = 0																		--do not make additional draft sorties
																							end
																							if active_log then log.traceLow("continue generation sortie if aircraft assign > 0, aircraft_assign: " .. aircraft_assign) end

																						until aircraft_assign <= 0																		--stop making more draft sorties
																						if active_log then log.traceLow("generation sorties complete, stop making more draft sorties aircraft_assign = 0") end
																						
																						--print("ATO Generating Sortie (" .. status_counter_sorties .. ") - Complete")	--DEBUG
																					end
																					
																					variant = variant - 2																			--determines if while-loop does another route variant depending on daytime
																					if active_log then log.traceLow("update variant(" .. variant .. "), variante determines if while-loop does another route variant depending on daytime") end
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

print("-")
print("ATO Generating Sortie (" .. status_counter_sorties .. ") - Complete")
if active_log then log.traceVeryLow("unsorted draft_sorties[blue]:\n" .. inspect(draft_sorties["blue"])) end
if active_log then log.traceVeryLow("unsorted draft_sorties[red]:\n" .. inspect(draft_sorties["red"])) end

-- Modif Miguel21 M13 Performance Scripting	
-- ATO_G_debug02b haut score

-- local sorties_str = TableSerialization(draft_sorties["blue"], 0)
-- local sorties_File = io.open("Debug/BEFORE_sorties_str_R.lua", "w")										--open targetlist file
-- sorties_File:write(sorties_str)																		--save new data
-- sorties_File:close()

log.traceLow("shuffle oob_air and sort draft_sorties")
-- shuffle oob_air["blue"]
local shuffled = {}

for i, v in ipairs(oob_air["blue"]) do
	local pos = math.random(1, #shuffled+1)
	table.insert(shuffled, pos, v)
end
oob_air["blue"] = shuffled

-- shuffle oob_air["red"]
shuffled = {}

for i, v in ipairs(oob_air["red"]) do
	local pos = math.random(1, #shuffled+1)
	table.insert(shuffled, pos, v)
end
oob_air["red"] = shuffled

--sort blue and red draft_sorties
table.sort(draft_sorties["blue"], function(a,b) return a.score > b.score  end)
table.sort(draft_sorties["red"], function(a,b) return a.score > b.score  end)

if active_log then log.traceVeryLow("sorted draft_sorties[blue]:\n" .. inspect(draft_sorties["blue"])) end
if active_log then log.traceVeryLow("sorted draft_sorties[red]:\n" .. inspect(draft_sorties["red"])) end
	
	
-- local sorties_str = TableSerialization(draft_sorties["blue"], 0)
-- local sorties_File = io.open("Debug/AFTER_sorties_str_R.lua", "w")										--open targetlist file
-- sorties_File:write(sorties_str)																		--save new data
-- sorties_File:close()


-- if Debug.Generator.affiche then	
	-- local di = 1 
	-- for draft_n, draft in pairs(draft_sorties["blue"]) do	
		-- if  di < Debug.Generator.nb  then		--if  di < Debug.Generator.nb and string.find(draft.task, "Strike") then
			-- print(	"N� " .. draft_n..
					-- " /Id/ " ..tostring(draft.id)..
					-- " /Nb/ " ..draft.number..
					-- " /Type/ "..draft.type..
					-- " /threatsGround/ "..round(draft.threatsGround)..
					-- " /threatsAir/ "..round(draft.threatsAir)..
					-- " /Score/ " ..round(draft.score)..
					-- " /Task/ "..draft.task..
					-- " /Target/ "..draft.target_name
					-- )
			-- di = di +1
		-- end
	-- end
	-- print()	
-- end

-- if Debug.Generator.affiche then	
	-- local di = 1 
	-- for draft_n, draft in pairs(draft_sorties["red"]) do	
		-- if  di < Debug.Generator.nb or draft.name == "GA 2nd AS" then
			-- print(	"N� " .. draft_n..
					-- " /Id/ " ..tostring(draft.id)..
					-- " /Nb/ " ..draft.number..
					-- " /Type/ "..draft.type..
					-- " /threatsGround/ "..round(draft.threatsGround)..
					-- " /threatsAir/ "..round(draft.threatsAir)..
					-- " /Score/ " ..round(draft.score)..
					-- " /Task/ "..draft.task..
					-- " /Target/ "..draft.target_name
					-- )
			-- di = di +1
		-- end
	-- end
	-- print()	
	-- print()	
	-- print()	
-- end


	-- table.sort(oob_air["blue"], function(a,b) return a.number > b.number  end)
	-- table.sort(oob_air["red"], function(a,b) return a.number > b.number  end)
	
-- shuffled = {}
-- for i, v in ipairs(oob_air["blue"]) do
	-- local pos = math.random(1, #shuffled+1)
	-- table.insert(shuffled, pos, v)
-- end
-- oob_air["blue"] = shuffled

-- shuffled = {}
-- for i, v in ipairs(oob_air["red"]) do
	-- local pos = math.random(1, #shuffled+1)
	-- table.insert(shuffled, pos, v)
-- end
-- oob_air["red"] = shuffled

	-- local camp_str = "oob_air = " .. TableSerialization(oob_air, 0)						--make a string
	-- local campFile = io.open("Debug/shuffled_ATO_Generator.lua", "w")										--open targetlist file
	-- campFile:write(camp_str)																		--save new data
	-- campFile:close()
	



--create additional draft sorties with support flights assigned
if active_log then log.traceLow("create additional draft sorties with support flights assigned") end
local wk = 1							
i_timmer02 = 0

--inversion des 2 boucles draft_sortie en premier, oob_air ensuite, pour homogeniser les chances de sortie de tous les escadrons support
--inversione dei 2 loop draft_exit prima, poi oob_air, per uniformare le possibilità di uscita di tutti gli squadroni di supporto
for sideS, draftT in pairs(draft_sorties) do		

	for draft_n, draft in pairs(draft_sorties[sideS]) do													--iterate through all draft sorties beginning with the highest scored

		--determine enemy_side side
		local enemy_side																						--determine enemy_side side (opposite of unit side)
		if side == "blue" then
			enemy_side = "red"
		else
			enemy_side = "blue"
		end
		
		
		log.traceLow("shuffle oob_air")
		local shuffled = {}

		for i, v in ipairs(oob_air["blue"]) do
			local pos = math.random(1, #shuffled+1)
			table.insert(shuffled, pos, v)
		end
		oob_air["blue"] = shuffled

		shuffled = {}

		for i, v in ipairs(oob_air["red"]) do
			local pos = math.random(1, #shuffled+1)
			table.insert(shuffled, pos, v)
		end
		oob_air["red"] = shuffled		
		
		for side, unit in pairs(oob_air) do																	--iterate through all sides
						
			local NbTotalSupport = {}

			for n = 1, #unit do																				--iterate through all units

				if side == sideS and unit[n].inactive ~= true and db_airbases[unit[n].base] and db_airbases[unit[n].base].inactive ~= true and aircraft_availability[unit[n].name] and aircraft_availability[unit[n].name].available > 0  and db_airbases[unit[n].base].x and db_airbases[unit[n].base].y then	--if unit is active, its base is active and has available aircraft -- ATO_G_debug01 Fin de campagne					
					
					if active_log then log.traceLow("side: " .. side .. "draft_sortie_n: " .. draft_n .. ", sortie.score: " .. draft.score .. ", unit: " .. unit[n].name .. " - " .. unit[n].type .. ", airbase: " .. unit[n].base ..", is active, its base is active and has available aircraft") end					
					
					for task, task_bool in pairs(unit[n].tasks) do											--iterate through all tasks of unit
						local temp_draft_sorties = {}														--temporary table to hold additional draft sorties with escorts assigned
						
						if (task == "SEAD" or task == "Escort" or task == "Escort Jammer" or task == "Flare Illumination" or task == "Laser Illumination") and task_bool then	--task is a support task and is true
							-- active_log = activateLog(true, true, log, "traceVeryLow")
							
							if active_log then log.traceLow("side: " .. side .. "draft_sortie_n: " .. draft_n .. ", sortie.score: " .. draft.score .. ", unit: " .. unit[n].name .. " - " .. unit[n].type .. ", airbase: " .. unit[n].base ..", is active, its base is active and has available aircraft") end					
							
							--get possible loadouts
							local unit_loadouts = {}														--table to hold all loadouts for this aircraft type and task
							
							for loadout_name, ltable in pairs(db_loadouts[unit[n].type][task]) do			--iterate through all loadouts for the aircraft type and task
								ltable.name = loadout_name
								-- table.insert(unit_loadouts, ltable)											--add loadout to local table
								unit_loadouts[#unit_loadouts + 1] = ltable
							end
							
							for l = 1, #unit_loadouts do													--iterate through all available loadouts				
								tot_from, toto_to = defineToTtiming(true, unit_loadouts[l])
								
								if tot_from ~= 0 or tot_to ~= 0 then										--loadout has an eligible time on target
									
									if active_log then log.traceLow("loadout has an eligible time on target, tot_from: " .. tot_from .. ", tot_to: " .. tot_to) end
									
									local _NbTotalSupport = 0
										
									if not draft.support[task]["NbTotalSupport"] then 
										draft.support[task]["NbTotalSupport"] = 0 
									end
									-- if not draft.support[task]["escort_max"] then draft.support[task]["escort_max"] = campMod.Setting_Generation.limit_escort end
									if not draft.support[task]["escort_max"] then 
										draft.support[task]["escort_max"] = 999 
									end
									local MP_Game = false

									if multiPlaneSet then
										
										if multiPlaneSet[unit[n].type]  and multiPlaneSet[unit[n].type][task] then	--and task ~= "CAP" and task ~= "Intercept"

											if Multi.Target and Multi.Target[side] and Multi.Target[side] == draft.target_name then	
												MP_Game = true
											end
										end
									end
									
									-- print("ATO_G draft_sortiesName "..draft.name.." "..draft.type)
									i_timmer02 = i_timmer02 + 1
									
									--qui puoi togliere draft.loadout.support and draft.loadout.support[task] in quanto presenti negli if sopra
									if draft.loadout.support and draft.loadout.support[task] and ( (tonumber(draft.support[task]["NbTotalSupport"]) < tonumber(draft.support[task]["escort_max"])) or MP_Game ) then																												

										if active_log then log.traceLow("loadout requires support for this task (" .. task .. ") and  eligible time on target, tot_from: draft.support[task][escort_max](" .. draft.support[task]["escort_max"] .. ") > draft.support[task][NbTotalSupport]" .. draft.support[task]["NbTotalSupport"] .. ", or this is an multiplayer: " .. tostring(MP_Game)) end																				
										local support_requirement = false

										if task == "SEAD" then
											if draft.route.threats.SEAD_offset > 0 then												--draft sortie has a SEAD offset requirement
												support_requirement = true
												if active_log then log.traceLow("draft sortie (task: " .. task .. "), has a SEAD offset requirement of: " .. draft.route.threats.SEAD_offset) end
											end

										elseif task == "Escort" then
											
											if draft.route.threats.air_total > camp.module_config.ATO_Generator[side].MIN_TOTAL_AIR_THREAT_FOR_ESCORT_SUPPORT then												--draft sortie has an air threat
												support_requirement = true
												if active_log then log.traceLow("draft sortie (task: " .. task .. "), has has an air threat(> " .. camp.module_config.ATO_Generator[side].MIN_TOTAL_AIR_THREAT_FOR_ESCORT_SUPPORT .. " ) of: " .. draft.route.threats.air_total .. ", set support_requirement = true") end
											end
										
										elseif task == "Escort Jammer" then

											if draft.route.threats.SEAD_offset > 0 or draft.route.threats.air_total > MIN_TOTAL_AIR_THREAT_FOR_ESCORT_SUPPORT then		--draft sortie has either a SEAD offest requirement or an air threat
												support_requirement = true
												if active_log then log.traceLow("draft sortie (task: " .. task .. "), has a SEAD offset requirement of: " .. draft.route.threats.SEAD_offset .. ", and has has an air threat(> " .. camp.module_config.ATO_Generator[side].MIN_TOTAL_AIR_THREAT_FOR_ESCORT_SUPPORT .. " ) of: " .. draft.route.threats.SEAD_offset .. ", set support_requirement = true") end
											end

										elseif task == "Flare Illumination" or task == "Laser Illumination"then
											support_requirement = true
											if active_log then log.traceLow("draft sortie (task: " .. task .. "), set support_requirement = true") end
										end
											
										if support_requirement or MP_Game then																	--go ahead with this support task
											
											if active_log then log.traceLow("draft sortie (task: " .. task .. "), support requires or multiplayer game") end

											if (unit_loadouts[l].day and draft.loadout.day) or (unit_loadouts[l].night and draft.loadout.night) then	--support can join package at either day or night
												TrackPlayability(unit[n].player, "tot")															--track playabilty criterium has been met
												if active_log then log.traceLow("draft sortie (task: " .. task .. "), support can join package at either day or night") end
												if active_log then log.traceLow("unit_loadouts[l]:\n" .. inspect(unit_loadouts[l]) .. "\n\ndraft.loadout:\n" .. inspect(draft.loadout)) end
											
												if unit_loadouts[l].vCruise >= draft.loadout.vCruise then										--support has a cruise speed equal or higher than main body
													TrackPlayability(unit[n].player, "target")													--track playabilty criterium has been met
													if active_log then log.traceLow("draft sortie (task: " .. task .. "), support has a cruise speed equal or higher than main body") end
													-- io.write("ATO_G passeBB ")
													--check weather
											
													if active_log then log.traceLow("check weather") end
													local weather_eligible = checkWeather(mission, unit[n], unit_loadouts[l], draft.loadout, task, true)																								
								
													if weather_eligible then																	--continue of this loadout is eligible for weather
														TrackPlayability(unit[n].player, "weather")												--track playabilty criterium has been met								
														if active_log then log.traceLow("support flight loadout is weather elegible for this task: " .. task) end
														
														--get airbase position
														local airbasePoint = {																	--get the x-y coordinates of the airbase where the unit is located
															x = db_airbases[unit[n].base].x,
															y = db_airbases[unit[n].base].y
														}	
														
														if airbasePoint.x == nil then
															log.warn("support task: ANOMALY airbasePoint.x == nil, was a carrier!?")																			
														end

														if airbasePoint.y == nil then
															log.warn("support task: ANOMALY airbasePoint.y == nil, was a carrier!?")																																							
														end
														

														if active_log then log.traceLow("compute escort route for this support flight") end
														local route = GetEscortRoute(airbasePoint, draft.route)									--get the route to escort this sortie

														--<========================================= QUI PER ANALISI E LOGGING ========================================================================

														if route.lenght <= unit_loadouts[l].range * camp.module_config.ATO_Generator[side].MULTIPLIER_TARGET_DISTANCE_FOR_EVALUTATION_UNIT_RANGE_LOADOUT and (unit_loadouts[l].minrange == nil or route.lenght > unit_loadouts[l].minrange * camp.module_config.ATO_Generator[side].MULTIPLIER_TARGET_DISTANCE_FOR_EVALUTATION_UNIT_RANGE_LOADOUT) then		--escort route lenght is within range capability of loadout
															TrackPlayability(unit[n].player, "target_range")									--track playabilty criterium has been met
															
															--determine number of escorts
															local escort_num = 0
															local escort_max = 0
															
															if draft.support[task]["escort_max"] ~= 999 then
																escort_max = draft.support[task]["escort_max"]
															else
																escort_max = 0
															end																																																										
															
															if active_log then log.traceLow("support task: route.lenght( " .. route.lenght .. " ) < range ( " .. unit_loadouts[l].range .. " ) * multiplier ( " .. camp.module_config.ATO_Generator[side].MULTIPLIER_TARGET_DISTANCE_FOR_EVALUTATION_UNIT_RANGE_LOADOUT .. " ): " .. unit_loadouts[l].range * camp.module_config.ATO_Generator[side].MULTIPLIER_TARGET_DISTANCE_FOR_EVALUTATION_UNIT_RANGE_LOADOUT .. ", or unit_loadouts[l].minrange( " .. (unit_loadouts[l].minrange or "nil") .. " ) == nil or route.lenght > unit_loadouts[l].minrange * multiplier ( " .. camp.module_config.ATO_Generator[side].MULTIPLIER_TARGET_DISTANCE_FOR_EVALUTATION_UNIT_RANGE_LOADOUT .. " )") end

															if task == "SEAD" then
																--escort_num = math.ceil( draft.route.threats.SEAD_offset / unit_loadouts[l].capability )		--capability determines amount of offset per aircraft
																-- considere l'offset come il numero di unità SAM attive (radar) da distruggere per interdire il SAM. (la capability la utilizzo per la scelta del migliore aereo mediante lo score)
																-- draft.route.threats.SEAD_offset dovrebbe essere la somma di tutti gli offset dei SAM sulla route (VERIFICARE in RouteGenerator)
																escort_num = math.ceil( draft.route.threats.SEAD_offset / unit_loadouts[l].firepower )			--firepower determines amount of offset per aircraft
																--escort_num = math.ceil(escort_num / 2) * 2										    --round up requested escorts to even number																

																if escort_num > 0 and escort_num == 1 then
																	escort_num = 2
																end

																if active_log then log.traceLow("support task: SEAD, draft.route.threats.SEAD_offset: " .. draft.route.threats.SEAD_offset .. ", unit_loadouts[l].firepower: " .. unit_loadouts[l].firepower .. ", escort_num: " .. escort_num) end																

															elseif task == "Escort" then

																if draft.support[task]["escort_max"] ~= 999 then
																	escort_num = draft.support[task]["escort_max"] - draft.support[task]["NbTotalSupport"]	-- Miguel21 modification M11.x : Multiplayer	(x: EscorteTot-max)
																	if active_log then log.traceLow("support task: ESCORT, escort_num = draft.support[task][escort_max](" .. draft.support[task]['escort_max'] .. ") - draft.support[task][NbTotalSupport]( " .. draft.support[task]["NbTotalSupport"] .. " ): " .. escort_num ) end																
																else
															
																	local escort_offset_level = unit_loadouts[l].capability * unit_loadouts[l].firepower	--threat level that each fighter escort can offset																	
																	escort_num = (draft.route.threats.air_total - 0.5) / escort_offset_level		--number of escorts needed to offset total air threat (-0.5 because that is no air threat)																	
																	if active_log then log.traceLow("support task: ESCORT, escort_num = (draft.route.threats.air_total(" .. draft.route.threats.air_total .. ")  - 0.5) / escort_offset_level(firepower)( " .. escort_offset_level .. " ): " .. escort_num ) end																
																	
																	if escort_num > draft.number * camp.module_config.ATO_Generator[side].ESCORT_NUMBER_MULTIPLIER then											--when more escorts camp.module_config.ATO_Generator.ESCORT_NUMBER_MULTIPLIER(3) times escorts than escorted aircraft
																		escort_num = draft.number * camp.module_config.ATO_Generator[side].ESCORT_NUMBER_MULTIPLIER												--limit escort number to camp.module_config.ATO_Generator.ESCORT_NUMBER_MULTIPLIER(3) times escorted aircraft
																	end
																	
																	if escort_num > campMod.Setting_Generation.limit_escort then
																		escort_num = campMod.Setting_Generation.limit_escort
																	else
																		escort_num = math.ceil(escort_num)
																		-- escort_num = math.ceil(escort_num / 2) * 2										--round up requested escorts to even number
																	end
																	
																	if escort_num > escort_max then
																		escort_max = escort_num
																	end	
																	if active_log then log.traceLow("support task: ESCORT, escort_num limited (<=) to draft.number( " .. draft.number .. " ) * camp.module_config.ATO_Generator.ESCORT_NUMBER_MULTIPLIER( " .. camp.module_config.ATO_Generator[side].ESCORT_NUMBER_MULTIPLIER .. " ): " .. draft.number * camp.module_config.ATO_Generator[side].ESCORT_NUMBER_MULTIPLIER .. ", and escort_num limited to campMod.Setting_Generation.limit_escort( " .. campMod.Setting_Generation.limit_escort .. " ) - escort_num: " .. escort_num ) end																
																end
															
															elseif task == "Escort Jammer" then
																escort_num = 1																	--escort jamming by single aircraft
															
															elseif task == "Flare Illumination" then
																escort_num = 1																	--flare illumination by single aircraft
															
															elseif task == "Laser Illumination" then
																escort_num = 1																	--laser illumination by single aircraft
															end
															
															if escort_num > aircraft_availability[unit[n].name].available then					--if more escorts are requested than available
																escort_num = aircraft_availability[unit[n].name].available						--reduce requested escorts to number of available escorts																
																if active_log then log.traceLow("support task: ESCORT, escort_num > aircraft_availability[unit[n].name].available( " .. aircraft_availability[unit[n].name].available .. " --> escort_num = aircraft_availability[unit[n].name].available " .. escort_num ) end																
															
															else
																-- escort_num = math.floor(escort_num / 2) * 2										--round down to even number
																escort_num = math.ceil(escort_num)
															end
															
															if MP_Game	then
																escort_num = multiPlaneSet[unit[n].type][task].NbPlane
															end
															
															-- ATO_G_Debug05 interdit l'escorte avion/helico
															if draft.helicopter then
																if not  unit[n].helicopter	then
																	escort_num = 0
																end
															end
															
															local wi = 1
															if escort_num > 0  then																--repeat to make multiple new sorties with various even number of escorts (from all requested down to 2)
																
																TrackPlayability(unit[n].player, "target_firepower")							--track playabilty criterium has been met
																
																if not draft.support[task] then
																	draft.support[task] = {}
																end

																if not draft.support[task][unit[n].type] then
																	draft.support[task][unit[n].type] = {}
																end		
																
																--add escort table to sortie															
																draft.support[task]["NbTotalSupport"] = draft.support[task]["NbTotalSupport"] + escort_num
																draft.support[task]["escort_max"] = escort_max
																
																draft.support[task][unit[n].type] = {
																	id = draft.id.."-"..wi.."-"..wk,
																	name = unit[n].name,
																	playable = unit[n].player,
																	type = unit[n].type,
																	helicopter = unit[n].helicopter,											-- Miguel21 modification M06 : helicoptere playable
																	number = escort_num,
																	country = unit[n].country,
																	livery = unit[n].livery,
																	sidenumber = unit[n].sidenumber,
																	liveryModex = unit[n].liveryModex,
																	base = unit[n].base,
																	airdromeId = db_airbases[unit[n].base].airdromeId,
																	parking_id = unit[n].parking_id,
																	skill = unit[n].skill,
																	task = task,
																	loadout = unit_loadouts[l],
																	route = route,
																	target = deepcopy(draft.target),
																	target_name = draft.target_name,
																	tot_from = draft.tot_from,
																	tot_to = draft.tot_to,
																	rejected = {},
																}

																--recalculate threat level for sortie adjusted by number of escort
																local route_threat_recalc = 0.5														--recalculated route threat with escort in place (0.5 == no threat)

																if task == "SEAD" then -- serve per il calcolo dello score e non per la definizione delle unità di scorta
																	-- local escort_offset = escort_num * unit_loadouts[l].capability					--number of available SEAD to offset threats
																	local escort_offset = escort_num * unit_loadouts[l].firepower					-- number of available SEAD to offset threats
																	if active_log then log.traceLow("recalculate threat level for sortie adjusted by number of escort (task: SEAD) - number of available SEAD to offset threats: " .. escort_offset .. ", route_threat_recalc: " .. route_threat_recalc ) end																
																	

																	for k,v in pairs(draft.route.threats.ground) do									--iterate through route ground threats
																		
																		if v.offset > 0 then														--if threat can be offset by SEAD

																			if escort_offset >= v.offset then										--some SEAD aircraft remain to offset the threat
																				escort_offset = escort_offset - v.offset							--use these SEAD aircraft to offset and ignore the therat
																			
																			else																	--no SEAD aircraft remain unassignedd
																				route_threat_recalc = route_threat_recalc + v.level					--sum route ground threat levels
																			end
																		
																		else																		--threat cannot be offset by SEAD
																			route_threat_recalc = route_threat_recalc + v.level						--sum route ground threat levels
																		end
																	end
																	draft.route.threats.ground_total = route_threat_recalc			--recalculated total route grund threat
																	if active_log then log.traceLow("recalculate threat level for sortie adjusted by number of escort (task: SEAD)- update number of available SEAD to offset threats: " .. escort_offset .. ", update route_threat_recalc: " .. route_threat_recalc ) end																
																
																elseif task == "Escort" then
																	local escort_offset_level = unit_loadouts[l].capability * unit_loadouts[l].firepower		--threat level that each fighter escort can offset
																	route_threat_recalc = draft.route.threats.air_total - escort_offset_level * escort_num			--recalculated total route air threat																	
																	
																	if route_threat_recalc < 0.5 then
																		route_threat_recalc = 0.5
																	end
																	draft.route.threats.air_total = route_threat_recalc
																	if active_log then log.traceLow("recalculate threat level for sortie adjusted by number of escort (task: Escort)- threat level that each fighter escort can offset: " .. escort_offset_level .. ", route_threat_recalc: " .. route_threat_recalc ) end																
																
																elseif task == "Escort Jammer" then
																--ADD RECALCULATED THREAT LEVEL WITH ESCORT JAMMERS
																end
															
																local route_threat = draft.route.threats.ground_total + draft.route.threats.air_total		--combine adjusted ground and air threat levels (1 equald no threat)
																draft.score = draft.loadout.capability * draft.target.priority / route_threat		--calculate the score to measure the importance of the sortie	
																if active_log then log.traceLow("calculate total route threat level (air: " .. draft.route.threats.ground_total .. " + ground: " .. draft.route.threats.air_total .. ") for this sortie: " .. route_threat .. ", calculated sortie score = loadout.capability: " .. draft.loadout.capability .. " * targte.priority: " .. draft.target.priority .. " / route threat =  " .. draft.score ) end																	

																--ATO_G_adjustment02
																if unit[n].tasksCoef and unit[n].tasksCoef[task] then
																	draft.score = draft.score * unit[n].tasksCoef[task]															
																	if active_log then log.traceLow("update sortie score = score * unit[n].tasksCoef[task]: " .. unit[n].tasksCoef[task] .. "  =  " .. draft.score ) end																	
																end
																
																-- miguel21 modification M11.r multiplayer
																if multiPlaneSet and multiPlaneSet[draft.type] and multiPlaneSet[draft.type][draft.task] then	-- check le type de plane en MAIN Strike
																	if Multi.Target and Multi.Target[side] and Multi.Target[side] == draft.target_name then		--si cible selectionnee et plane et task																		--si cible choisi par joueur
																		if multiPlaneSet[unit[n].type] and multiPlaneSet[unit[n].type][task] then
																			for iTask, _Support in pairs(draft.support) do										--boucle les supports pour trouver tous les vols support et augmenter leur valeur si ils correspondent aux planes demandé
																				if type(_Support) == "table" then	
																					for iPlane, iiSupport in pairs(_Support) do
																						draft.score = draft.score * 2
																						if  type(iiSupport) == table and multiPlaneSet[iiSupport.type] and multiPlaneSet[iiSupport.type][iTask] then
																							draft.score = draft.score + 500
																						end
																					end
																				end	
																			end																																	
																		end
																	
																	else																		--si cible choisi par joueur																		
																		if multiPlaneSet[draft.type] and multiPlaneSet[draft.type][draft.task] then
																				
																			for iTask, _Support in pairs(draft.support) do
																				if type(_Support) == "table" then
																					for iPlane, iiSupport in pairs(_Support) do	
																						draft.score = draft.score * 1.1
																						if  type(iiSupport) == table and multiPlaneSet[iiSupport.type] and multiPlaneSet[iiSupport.type][iTask] then
																							draft.score = draft.score + 10
																						end
																						-- print("ATO_G 02 "..draft.score)
																					end
																				end
																			end																																	
																		end
																		-- draft.score = draft.score * 25								-- augmente le score pour avoir plus de chance d'avoir l'avion dispo					
																		if draft.score < 200 then draft.score = draft.score + 200 end
																	end
																
																end	
																
																--adjust sortie Time on Target
																if tot_from > draft.tot_from then									--if earliest escort Time on Target is later than main body TOT
																	draft.tot_from = tot_from							--make earliest escort TOT the draft sortie earliest TOT 
																end
																if tot_to < draft.tot_to then										--if latest escort Time on Target is sooner than main body TOT
																	draft.tot_to = tot_to								--make latest escort TOT the draft sortie latest TOT
																end

																--status report
																status_counter_escorts = status_counter_escorts + 1
																--print("ATO Assigning Escorts (" .. status_counter_escorts .. ")")	--DEBUG
																
																-- print()
																-- print("ATO_G draft_n "..draft_n
																-- .." Strike: "..draft.type
																-- .." "..task
																-- .." Escorte: "..unit[n].name
																-- .." "..unit[n].type
																-- .." "..draft.target_name
																-- .." NbTotS: "..draft.support[task]["NbTotalSupport"]
																-- .." esctMax: "..draft.support[task]["escort_max"]
																-- )
																-- print()
																
																wi = wi + 1																
															end
														end
													end
												else
													-- print("ATO_G  Refused02 ||:if unit_loadouts[l].vCruise >= draft.loadout.vCruise "..debug.getinfo(1).currentline)
												end
											else
												-- print("ATO_G  Refused02 ||:if (unit_loadouts[l].day and draft.loadout.day) or "..debug.getinfo(1).currentline)
											end
										end
									else
										-- print("ATO_G  Refused02 ||:if draft.loadout.support and draft.loadout.support[task] and "..debug.getinfo(1).currentline)
										-- print("    draft.type"..tostring(draft.type).."[task]?: "..tostring(task).." NbTotalSupport: "..tonumber(draft.support[task]["NbTotalSupport"]).." < "..tonumber(draft.support[task]["escort_max"]).." or "..tostring(MP_Game))
									end
									-- active_log = activateLog(false, true, log, log_level)	
									if i_timmer02 >= 1000  then io.write(".") i_timmer02 = 0 end
									wk = wk +1
								end	
							end
						end
					end
				end
			end
		end
	end
end

print()
print("ATO Assigning Escorts (" .. status_counter_escorts .. ")")	--DEBUG
-- ATO_G_debug02b haut score

	table.sort(draft_sorties["blue"], function(a,b) return a.score > b.score  end)
	table.sort(draft_sorties["red"], function(a,b) return a.score > b.score  end)

	
-- if Debug.Generator.affiche then	
	-- local di = 1 
	-- for draft_n, draft in pairs(draft_sorties["blue"]) do	
		-- if  di < Debug.Generator.nb  then
			
			-- print(	"N° " .. draft_n..
					-- -- " /support/ " ..tostring(draft.support)..
					-- " /Name/ " ..tostring(draft.name)..
					-- " /Nb/ " ..draft.number..
					-- " /Type/ "..draft.type..
					-- " /thrtGrnd/ "..round(draft.threatsGround)..
					-- " /thrtA/ "..round(draft.threatsAir)..
					-- " /Score/ " ..round(draft.score)..
					-- " /NbTotSupt/ " ..tostring(draft.NbTotalSupport)..
					
					-- " /Task/ "..draft.task..
					-- " /Target/ "..draft.target_name
					-- )
			-- di = di +1
			-- for _PlaneTask, PlaneTask in pairs(draft.support) do
				-- -- draft.support[task]["escort_max"] = escort_max
				-- -- if PlaneTask.escort_max then
					-- -- print(tostring(PlaneTask.escort_max))
				-- -- end
				-- for taskName, task in pairs(PlaneTask) do	
				
					-- if type(task) == "table" then	
						-- -- print(	"    ---> Nsupport " .._PlaneTask.." ".. task.escort_max)
						-- print(	"    ---> Nsupport " .._PlaneTask.." ".. taskName..
								-- " /Id/ " ..tostring(task.id)..
								-- " /Nb/ " ..task.number..
								-- " /escort_max/ " ..tostring(PlaneTask.escort_max)..
								-- " /Type/ "..task.type..
								-- " /Task/ "..task.task..
								-- " /NbTotSupt/ " ..tostring(task.NbTotalSupport)..
								-- " /Target/ "..task.target_name
								-- )
					-- end
				-- end
			-- end
		-- end
	-- end
	-- print()	
-- end

	
-- if Debug.Generator.affiche then	
	-- local di = 1 
	-- for draft_n, draft in pairs(draft_sorties["red"]) do	
		-- if  di < Debug.Generator.nb or draft.name == "GA 2nd AS" then
			-- print(	"N° " .. draft_n..
					-- -- " /support/ " ..tostring(draft.support)..
					-- " /Id/ " ..tostring(draft.id)..
					-- " /Nb/ " ..draft.number..
					-- " /Type/ "..draft.type..
					-- " /threatsGround/ "..round(draft.threatsGround)..
					-- " /threatsAir/ "..round(draft.threatsAir)..
					-- " /Score/ " ..round(draft.score)..
					-- " /Task/ "..draft.task..
					-- " /Target/ "..tostring(draft.target_name)
					-- )
			-- di = di +1
			-- for _PlaneTask, PlaneTask in pairs(draft.support) do
				-- for taskName, task in pairs(PlaneTask) do	
					-- if type(task) == "table" then	
						-- print(	"    ---> Nsupport " .._PlaneTask.." ".. taskName..
								-- " /Id/ " ..tostring(task.id)..
								-- " /Nb/ " ..task.number..
								-- " /escort_max/ " ..tostring(PlaneTask.escort_max)..
								-- " /Type/ "..task.type..
								-- " /Task/ "..task.task..
								-- " /NbTotSupt/ " ..tostring(task.NbTotalSupport)..
								-- " /Target/ "..task.target_name
								-- )
					-- end
				-- end
			-- end
		-- end
	-- end
	-- print()	
	-- print()	
	-- print()	
-- end



--table to store the final ATO
ATO = {
	blue = {},
	red = {}
}


--assign draft sorties to ATO and build packages/flights
log.trace("assign draft sorties to ATO and build packages/flights ----------------------")
for side, draft in pairs(draft_sorties) do																		--iterate through all sides

	for n = 1, #draft do		
		log.traceLow("draft[" .. n .. "].name: " .. draft[n].name)
																						--iterate through all draft sorties beginning with the highest scored	
		if draft[n].loadout.minscore == nil or draft[n].loadout.minscore <= draft[n].score then					--draft sortie has no minimum score requirement or minimum score requirement is satisified		

			if draft[n].loadout.minscore ~= nil then
				log.traceLow("draft[n].loadout.minscore(" .. draft[n].loadout.minscore .. ") <= draft[n].score(" .. draft[n].score .. ")")
			
			else
				log.traceLow("draft[n].loadout.minscore == nil")
			end

			if draft[n].multipack == nil or draft[n].multipack > 0 then												--target does not have a requirment for a specific number of packages, or still needs more packages		
				
				if draft[n].multipack ~= nil then
					log.traceLow("draft[n].multipack > 0>: target does not have a requirment for a specific number of packages, or still needs more packages")
				
				else
					log.traceLow("draft[n].multipack == nil")
				end

				if draft[n].target.firepower.max > 0 and draft[n].target.firepower.max >= draft[n].target.firepower.min then	--the target of this draft sortie must have a need for firepower above the minimum firepower threshold	
					local available = aircraft_availability[draft[n].name].unassigned											--shortcut for available aircraft for this draft sortie					
					log.traceLow("draft[n].target.firepower.max(" .. draft[n].target.firepower.max .. ") > draft[n].target.firepower.min(" .. draft[n].target.firepower.min .. ") > 0, avalaible_aircraft[" .. draft[n].name .. "] = " .. available)

					if available * draft[n].loadout.firepower >= draft[n].target.firepower.min and draft[n].number * draft[n].loadout.firepower >= draft[n].target.firepower.min then	--enough aircraft are available to satisfy minimum firepower requirement for target						
						log.traceLow("aircraft available(" .. available .. ") * draft[n].loadout.firepower(" .. draft[n].loadout.firepower .. ") >= draft[n].target.firepower.min(" .. draft[n].target.firepower.min .. ")")
						log.traceLow("draft[n].number(" .. draft[n].number .. ") * draft[n].loadout.firepower(" .. draft[n].loadout.firepower .. ") > >= draft[n].target.firepower.min(" .. draft[n].target.firepower.min .. ")")

						if draft[n].target.firepower.packmin == nil or available * draft[n].loadout.firepower >= (draft[n].target.firepower.packmin - 1) * draft[n].target.firepower.max + draft[n].target.firepower.min then	--if the target has a minimum package number requirement, sufficient aircraft are available from this unit to satisfy it					
							
							if draft[n].target.firepower.packmin ~= nil then
								log.traceLow("available * draft[n].loadout.firepower (= " .. available * draft[n].loadout.firepower .. ")  >= (draft[n].target.firepower.packmin - 1) * draft[n].target.firepower.max + draft[n].target.firepower.min (" .. (draft[n].target.firepower.packmin - 1) * draft[n].target.firepower.max + draft[n].target.firepower.min .. ")")
							
							else
								log.traceLow("draft[n].target.firepower.packmin == nil")
							end

							if draft[n].flights == nil or draft[n].number <= available then											--for targets with station time (multiple flights), continue only if sufficient aircraft are availabe. Additional lower scored sorties with less airctaft required will come later 

								if draft[n].flights ~= nil then
									log.traceLow("draft[n].number(" .. draft[n].number .. ") <= available(" .. available .. ")")
								
								else
									log.traceLow("draft[n].flights == nil")
								end

								--adjust the number of requested aircraft to the number of available aircraft
								if draft[n].number > available then
									draft[n].number = available
									log.traceLow("update draft[n].number: " .. draft[n].number)
								end																
								
								
								
								--check if there are enough supports available if supports are required		
								local support_available = true							
								
								local need = {}																														--collect the total number of aircraft needed from each unit to complete the package
								need[draft[n].name] = draft[n].number																								--number of main body aircraft 
								local avail = {}																													--collect the maximal number of available aircraft from this unit (biggest number of all tasks)
								avail[draft[n].name] = aircraft_availability[draft[n].name].unassigned																

								for unitname,_ in pairs(need) do 
									
									if need[unitname] > avail[unitname] then																						--more aircraft are needed from this unit across all package tasks than are available
										support_available = false																									--not enough support available
										local TabRejected = {}
										TabRejected["sujet"]  = "AVION SUPPORT INSUFFISANT()support_available if need[unitname] > avail[unitname]"
										TabRejected["cause"] = { [1] =  need[unitname], [2] = avail[unitname], }
										TabRejected["ligne"]  = debug.getinfo(1).currentline														
										table.insert(draft[n]["rejected"], TabRejected)
										log.traceLow("need[" .. unitname .. "](" .. need[unitname] .. ") > avail[" .. unitname .. "](" .. avail[unitname] .. ") -> draft[" .. n .. "][rejected];\n" .. inspect(TabRejected))
									end
								end
								
								-- ATO_G_adjustment01 escort mandatory or not
								-- regarde uniquement pour les bombardiers necessitant une escorte
								-- probabilmente richiede che support = {ESCORT = { valore }} e 3non con un boolean
								-- non serve se il support è richiesto tramite boolean e comunque hio dubbi sul funzionamento, eliminare??
								if campMod.StrikeOnlyWithEscorte and not draft[n].loadout.self_escort then
									log.traceLow("strike missions request escort (only for loadout with self_escort = false")

									if (db_loadouts[draft[n].type]["Anti-ship Strike"] or db_loadouts[draft[n].type]["Strike"])  then											
										local break_loop = false
										log.traceLow("loadouts is compatible for strike missions")
										
										for n_squad, squad in pairs(oob_air[side]) do
										
											if (squad.tasks["Anti-ship Strike"]  or squad.tasks["Strike"] ) and squad.type == draft[n].type then
												log.traceLow("the oob_air squad with same type defined in draft (" .. squad.type .. ") have strike task, search for an support request:\n" .. inspect(draft[n].support))
												local needS = {}																														--collect the total number of aircraft needed from each unit to complete the package
												needS[draft[n].name] = 0																								--number of main body aircraft 
												local availS = {}																													--collect the maximal number of available aircraft from this unit (biggest number of all tasks)
												availS[draft[n].name] = 0
												
												for _p,_support in pairs(draft[n].support) do																							--iterate through support in draft sortie	
													log.traceLow("support request: " .. _p)
													
													if 	type(_support) == "table" then	
														
														for _a,support in pairs(_support) do
															log.traceLow("support items request: " .. _a)											
															
															if 	type(support) == "table" then																
																needS[draft[n].name] =  needS[draft[n].name] + support.number																	--add number of support aircraft from same unit
																availS[draft[n].name] = availS[draft[n].name] + aircraft_availability[support.name].unassigned	
																log.traceLow("support.number: " .. support.number .. ", update needS[" .. draft[n].name .. "] = " .. needS[draft[n].name] .. ", update availS[" .. draft[n].name .. "] = " .. availS[draft[n].name])													
															end
														end
													end
												end

												for unitname,_ in pairs(needS) do

													if needS[unitname] * camp.module_config.ATO_Generator[side].MIN_PERCENTAGE_FOR_ESCORT > availS[unitname] then	-- questo dovrebbe sempre essere vero con escort = true (comporta un needS = 0 in quanto escort non è una tab contentente un valore numerico)
													--more aircraft are needed from this unit across all package tasks than are available
														support_available = false																									--not enough support available
														local TabRejected = {}
														TabRejected["sujet"]  = "BOMBARDIER NECESSITANT ESCORTE()support_available if needS[unitname] - (needS[unitname] * 0.15) > availS[unitname]"
														TabRejected["cause"] = { [1] = needS[unitname]* camp.module_config.ATO_Generator[side].MIN_PERCENTAGE_FOR_ESCORT, [2] = availS[unitname], }
														TabRejected["ligne"]  = debug.getinfo(1).currentline														
														table.insert(draft[n]["rejected"], TabRejected)
														log.traceLow("needS[" .. unitname .. "](" .. needS[unitname] .. ") *  > availS[" .. unitname .. "](" .. availS[unitname] .. ") -> draft[" .. n .. "][rejected];\n" .. inspect(TabRejected))
													end
												end
											
											end
										end
									end	
								end
								
								-- assegnazione scorte con support = {ESCORT = boolean} ?? NO c'è un errore logico che comunque non comporta conseguenze - prova ad eliminare l'intero ciclo
								for _p,_support in pairs(draft[n].support) do			
																													--iterate through support in draft sortie
									if  not support_available and	type(_support) == "table" then
										
										for _,support in pairs(_support) do		
																																--iterate through support in draft sortie
											if 	type(support) == "table" then	
												
												if support.number > aircraft_availability[support.name].unassigned then															--not enough aircraft available from this unit for this task
													support_available = false																									--not enough support available
													local TabRejected = {}
													TabRejected["sujet"]  = "ILLUMINATION ABSENT()support_available if support.number > aircraft_availability[support.name].unassigned" --???? come fà ad essere illumination (errore)
													TabRejected["cause"] = { [1] =  support.number, [2] = aircraft_availability[support.name].unassigned, }
													TabRejected["ligne"]  = debug.getinfo(1).currentline														
													table.insert(draft[n]["rejected"], TabRejected)
													log.traceLow("draft[" .. n .. "][rejected];\n" .. inspect(TabRejected))
												end
											end
										end
									end
								end
								
								-- assegnazione scorte con support = {ESCORT = boolean} controlla solo se il draft[n] presenta il support previsto nel loadout !??
								if not support_available and draft[n].loadout.support then																									--main body loadout support requirements
									
									for supporttype, bool in pairs(draft[n].loadout.support) do																		--iterate through support requirements of loadout
										
										if (supporttype == "Flare Illumination" or supporttype == "Laser Illumination") and bool then								--Flare Illumination and Laser Illumination is a necessary support type. If it is not present in the draft sortie, no package will be created				
											
											if draft[n].support[supporttype] == nil then																			--if draft sortie has no such support type assigned
												support_available = false																							--necessary support is not available											
												local TabRejected = {}
												TabRejected["sujet"]  = "ILLUMINATION ABSENT()support_available if draft[n].support[supporttype] == nil"
												TabRejected["cause"] = { [1] =  draft[n].support[supporttype], [2] = "", }
												TabRejected["ligne"]  = debug.getinfo(1).currentline														
												table.insert(draft[n]["rejected"], TabRejected)
												log.traceLow("draft[" .. n .. "][rejected];\n" .. inspect(TabRejected))
											end
										end
									end
								end
								
								
								for _p,_support in pairs(draft[n].support) do																							--iterate through support in draft sortie

									if not support_available and type(_support) == "table" then	

										for _,support in pairs(_support) do																							--iterate through support in draft sortie

											if 	type(support) == "table" then	

												if aircraft_availability[support.name].unassigned <=0 then
													support_available = false
													
														local TabRejected = {}
														TabRejected["sujet"]  = "AVION SUPPORT INSUFFISANT()support_available if aircraft_availability[support.name].unassigned <=0"
														TabRejected["cause"] = { [1] = aircraft_availability[support.name].unassigned, [2] = "", }
														TabRejected["ligne"]  = debug.getinfo(1).currentline														
														table.insert(draft[n]["rejected"], TabRejected)
														log.traceLow("draft[" .. n .. "][rejected];\n" .. inspect(TabRejected))
												end
											end
										end
									end
								end	
									
								-- Miguel21 modification M11.u : Multiplayer	(u: reserve avion Escorte)
								-- interdit aux possible avion d'escorte de tout donner dans CAP ou Intercept
								if (draft[n].task == "CAP" or draft[n].task == "Intercept") and ((db_loadouts[draft[n].type]["Escort"] or db_loadouts[draft[n].type]["SEAD"]) and aircraft_availability[draft[n].name].serviceable > 4) then
									local break_loop = false
									
									for n_squad, squad in pairs(oob_air[side]) do
										
										if squad.type == draft[n].type and (squad.tasks["Escort"] or squad.tasks["SEAD"]) then
											
											if aircraft_availability[draft[n].name].unassigned - draft[n].number <= aircraft_availability[draft[n].name].serviceable/2 then
												support_available = false												
												local TabRejected = {}
												TabRejected["sujet"]  = "NE DONNE PAS TOUT en CAP ou Intercept ()support_available if aircraft_availability[draft[n].name].unassigned - draft[n].number <= aircraft_availability[draft[n].name].serviceable/2"
												TabRejected["cause"] = { [1] = aircraft_availability[draft[n].name].unassigned - draft[n].number, [2]  = aircraft_availability[draft[n].name].serviceable/2, }
												TabRejected["ligne"]  = debug.getinfo(1).currentline														
												table.insert(draft[n]["rejected"], TabRejected)	
												log.traceLow("draft[" .. n .. "][rejected];\n" .. inspect(TabRejected))
												break_loop = true																		
												break
											end
										end
										if break_loop == true then
											break																							
										end
									end
								end
									
									
									
								
								
								if support_available then																		--continue if no support is required or enough support is available to create package
									--add new package to ATO
									local pack_n = #ATO[side]
									ATO[side][pack_n + 1] = {
										["main"] = {},																			--package main body
										["Escort"] = {},																		--Fighter escort
										["SEAD"] = {},																			--SEAD escort
										["Escort Jammer"] = {},																	--jammer escort
										["Flare Illumination"] = {},															--illumination flare
										["Laser Illumination"] = {},															--laser illumination
									}
									pack_n = pack_n + 1
									
									--add flights of 1, 2 or 4 aircraft to package
									local function AddFlight(assign, role, entry)
										local previous_log_level = log.level
										log.level =function_log_level
										local assigned
										
										while assign > 0 do																		--loop as long as there are aircraft to assign
											
											if entry.flights then																--for multiple flights with station time (CAP, AWACS, Tanker etc.)
												local flightsize = math.ceil(draft[n].target.firepower.max / draft[n].loadout.firepower)	--how many aircraft should be in each flight
												if assign >= flightsize then													--if there are more aircraft left to assign than the size of one flight
													assigned = flightsize														--assign one full flight
												else																			--if there are less aircraft left to assign than size of one flight
													assigned = assign															--assign whatever is left
												end
												entry.flights = entry.flights - 1												--one less flight to assign
												log.traceLow("update assigned = " .. assigned .. ", update entry.flights = " .. entry.flights)
											
											elseif entry.task == "Transport" or entry.task == "Escort Jammer" or entry.task == "Flare Illumination" or entry.task == "Laser Illumination" then		--for tasks with single aircraft
												assigned = 1																	--assign one aircraft per flight	
												log.traceLow("entry.task = Transport or Escort jammer or Flare illumination or Laser Illumination, assigned = " .. assigned)
											
											elseif entry.task == "Intercept" then
											
												if assign >= camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_INTERCEPT then 									--if more than 2 aircraft are to be assigned
													assigned = camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_INTERCEPT										--assign flight of 2 aircaft
											
												else
													assigned = assign 																-- else assign flight of 1 aicraft
												end
												log.traceLow("entry.task = Intercept, assigned = " .. assigned)
											
											elseif isBomberOrRecoType(entry.type) then												-- for bombers

												if assign >= camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_BOMBER then 	-- if more than 2 aircraft are to be assigned
													assigned = camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_BOMBER		-- assign flight of 2 aircaft
											
												else
													assigned = assign 																-- else assign flight of 1 aicraft
												end												
												log.traceLow("entry.type = Bomber, assigned = " .. assigned)
											
											elseif entry.task == "Reconnaissance" then												-- for recon
											
												if assign >= camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_RECONNAISSANCE then 	-- if more than 2 aircraft are to be assigned
													assigned = camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_RECONNAISSANCE		-- assign flight of 2 aircaft
											
												else
													assigned = assign																-- else assign flight of 1 aicraft
												end
												log.traceLow("entry.task = Reconnaisance, assigned = " .. assigned)
											
											elseif entry.task == "Strike" then												--for recon
											
												if assign >= camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_STRIKE then 									--if more than 2 aircraft are to be assigned
													assigned = camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_STRIKE										--assign flight of 2 aircaft
											
												else
													assigned = assign			 										--else assign flight of 1 aicraft
												end
												log.traceLow("entry.task = Strike, assigned = " .. assigned)

											elseif entry.task == "CAP" then											--for recon
											
												if assign >= camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_CAP then 									--if more than 2 aircraft are to be assigned
													assigned = camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_CAP										--assign flight of 2 aircaft
											
												else
													assigned = assign 										--else assign flight of 1 aicraft
												end
												log.traceLow("entry.task = CAP, assigned = " .. assigned)

											elseif entry.task == "Escort" then												--for recon
											
												if assign >= camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_ESCORT then 									--if more than 2 aircraft are to be assigned
													assigned = camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_ESCORT										--assign flight of 2 aircaft
											
												else
													assigned = assign													--else assign flight of 1 aicraft
												end
												log.traceLow("entry.task = Escort, assigned = " .. assigned)

											elseif entry.task == "Fighter Sweep" then										--for recon
											
												if assign >= camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_SWEEP then 									--if more than 2 aircraft are to be assigned
													assigned = camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_SWEEP										--assign flight of 2 aircaft
											
												else
													assigned = assign 													--else assign flight of 1 aicraft
												end
												log.traceLow("entry.task = Fighter Sweep, assigned = " .. assigned)

											else 																			--for everything else
											
												if assigned and assign == 1 then												--if there is one aircraft left to assign and there was already a previous flight assigned, stop assigning (do not add leftover single-ships)
													break
											
												elseif assign >= camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_OTHER then															--if more than 4 aircraft are to be assigned
													assigned = camp.module_config.ATO_Generator[side].MAX_AIRCRAFT_FOR_OTHER																--assign flight of 4 aircaft
											
												else
													assigned = assign															--else assign flight size of what is left
												end
											end
											----- QUI: definisci min e max x transport, cap, sweep, strike ecc
											local flight = {																	--build ATO flight entry
												name = entry.name,
												playable = entry.playable,
												type = entry.type,
												helicopter = entry.helicopter,
												number = assigned,																--number of aircraft in flight
												country = entry.country,
												livery = entry.livery,
												sidenumber = entry.sidenumber,
												liveryModex = entry.liveryModex,
												base = entry.base,
												airdromeId = entry.airdromeId,
												parking_id = entry.parking_id,
												skill = entry.skill,
												task = entry.task,
												loadout = entry.loadout,
												route = {},																		--route is a table and connot be copied as a whole
												target = deepcopy(entry.target),
												target_name = entry.target_name,
												firepower = assigned * entry.loadout.firepower,
												tot_from = entry.tot_from,
												tot_to = entry.tot_to,
											}
											for r = 1, #entry.route do															--make copy of route table
												flight.route[r] = {}
												for k,v in pairs(entry.route[r]) do
													flight.route[r][k] = v
												end
											end
											table.insert(ATO[side][pack_n][role], flight)										--add flight to package role (main, SEAD or escort)											
											
											--store time assigned aircraft are unavailable for future missions
											local operating_hours														--time the unit is operating each day
											if entry.loadout.day and entry.loadout.night then							--day/night loadout
												operating_hours = 86400													--full day in seconds
											elseif entry.loadout.day then												--day loadout
												operating_hours = camp.dusk - camp.dawn									--daytime in seconds
											elseif entry.loadout.night then												--night loadout
												operating_hours = camp.dawn + (86400 - camp.dusk)						--nighttime in seconds
											end
											local time_to_next_mission = operating_hours / entry.loadout.sortie_rate	--time duration until aircraft can do the next mission based on its sortie rate
											if entry.loadout.tStation and #ATO[side][pack_n][role] == 1 then			--for a flight that has a station time and for the first flight in package
												time_to_next_mission = time_to_next_mission - entry.loadout.tStation	--remove station time from time to next mission, because flight could airstart current mission at close to end of its station time
											end
											local current_time = (camp.day - 1) * 86400 + camp.time						--current absolute campaign time
											local unavailable = current_time + time_to_next_mission 					--campaign time until this aircraft unavailable for new mission
											for a = 1, assigned do														--iterate through all assigned aircraft
												if #aircraft_availability[entry.name].unavailable == 0 then
													table.insert(aircraft_availability[entry.name].unavailable, unavailable)						--insert unavailable time into unavailable table of this unit
												else
													for u = 1, #aircraft_availability[entry.name].unavailable do
														if unavailable > aircraft_availability[entry.name].unavailable[u] then
															table.insert(aircraft_availability[entry.name].unavailable, u, unavailable)				--insert unavailable time into unavailable table of this unit sorted from highest to lowest
															break
														elseif u == #aircraft_availability[entry.name].unavailable then
															table.insert(aircraft_availability[entry.name].unavailable, u + 1, unavailable)			--insert unavailable time into unavailable table of this unit sorted from highest to lowest
														end
													end
												end
											end
											
											aircraft_availability[entry.name].assigned = aircraft_availability[entry.name].assigned + assigned
											aircraft_availability[entry.name].unassigned = aircraft_availability[entry.name].unassigned - assigned		--remove assigned aircraft from total number of available aircraft for this unit
											
											assign = assign - assigned															--continue loop until are aircraft are assigned
										
										end
										log.level = previous_log_level
									end
									
									AddFlight(draft[n].number, "main", draft[n])												--add main body flights to package

									for support_name,_support in pairs(draft[n].support) do										--iterate through all package support

										if type(_support) == "table" then	

											for _plane,support in pairs(_support) do
												local number  = 0
											
												if type(support) == "table" and aircraft_availability[support.name].unassigned >= 2 then
													
													if support.number >= aircraft_availability[support.name].unassigned then number = aircraft_availability[support.name].unassigned end
													if support.number < aircraft_availability[support.name].unassigned then number = support.number end
													
													-- print("ATO_G Zb support_name: "..support_name.." _plane :".._plane.." "..support.name.." |unassigned: "..aircraft_availability[support.name].unassigned.." |number: "..number)
								
													AddFlight(number, support_name, support)										--add support flights to package
												
												end
											end
										end
									end
															
									--remove the firepower applied by package to target from maximum firepower of all other draft sorties to the same target
									local firepower_applied = 0																	--collect the amount of firepower combined by all main body flights of this package
									for f = 1, #ATO[side][pack_n].main do														--iterate through all main body flights
										firepower_applied = firepower_applied + ATO[side][pack_n].main[f].firepower				--sum firepower
									end
									for m = 1, #draft do																		--iterate through all draft sorties again
										if draft[n].target_name == draft[m].target_name then									--if draft sortie with same target as present package is found
											if draft[m].multipack then															--target has a fixed requirement for number of packages 
												draft[m].multipack = draft[m].multipack - 1										--reduce number of packages per one
												if draft[m].target.firepower.packmin then											--target has a fixed requirement for minimal number of packages 
													draft[m].target.firepower.packmin = draft[m].target.firepower.packmin - 1		--reduce number of minimal packages per one
												end
											else																				--target is stricly firepower controlled
												draft[m].target.firepower.max = draft[m].target.firepower.max - firepower_applied	--remove the firepower applied by current package from maximum firepower for this sortie
												draft[m].number = math.ceil(draft[m].number - (firepower_applied / draft[m].loadout.firepower))	--reduce the number of aircraf to be assigned to this sortie as a result of the firepower reduction
											end
										end
									end
									
									--status report
									status_counter_ATO = status_counter_ATO + 1
									--print("ATO Generation (" .. status_counter_ATO .. ")")	--DEBUG
								else
									local TabRejected = {}
									TabRejected["sujet"]  = "SUPPORT IMPOSSIBLE()if support_available"
									TabRejected["cause"] = { [1] = support_available, [2]  = "", }
									TabRejected["ligne"]  = debug.getinfo(1).currentline
									table.insert(draft[n]["rejected"], TabRejected)
								end
							else
								local TabRejected = {}
								TabRejected["sujet"]  = "AVIONS INSUFFISANT()if draft[n].flights == nil or draft[n].number <= available then"
								TabRejected["cause"] = { [1] = draft[n].flights, [2]  = draft[n].number, }
								TabRejected["ligne"]  = debug.getinfo(1).currentline
								table.insert(draft[n]["rejected"], TabRejected)
							end
						else
							--if draft[n].target.firepower.packmin == nil or available * draft[n].loadout.firepower >= (draft[n].target.firepower.packmin - 1) * draft[n].target.firepower.max + draft[n].target.firepower.min
							local TabRejected = {}
							TabRejected["sujet"]  = "FIREPOWER du PACKAGE INSUFFISANT()if  available * draft[n].loadout.firepower >= (draft[n].target.firepower.packmin - 1) * draft[n].target.firepower.max"
							TabRejected["cause"] = { [1] = available * draft[n].loadout.firepower, [2]  = (draft[n].target.firepower.packmin - 1) * draft[n].target.firepower.max, }
							TabRejected["ligne"]  = debug.getinfo(1).currentline
							table.insert(draft[n]["rejected"], TabRejected)
							log.traceVeryLow("draft[" .. n .. "][rejected]:\n" .. inspect(TabRejected))
						end
					else
						local TabRejected = {}
						TabRejected["sujet"]  = "AVION DISPONIBLE INSUFFISANT ()if available * draft[n].loadout.firepower >= draft[n].target.firepower.min and draft[n].number * draft[n].loadout.firepower >= draft[n].target.firepower.min"
						TabRejected["cause"] = { [1] = available * draft[n].loadout.firepower, [2]  = draft[n].target.firepower.min, }
						TabRejected["ligne"]  = debug.getinfo(1).currentline
						table.insert(draft[n]["rejected"], TabRejected)
						log.traceVeryLow("draft[" .. n .. "][rejected]:\n" .. inspect(TabRejected))
					end
				else
					local TabRejected = {}
					TabRejected["sujet"]  = "FIREPOWER INSUFFISANT (a augmenter dans loadout)if draft[n].target.firepower.max > 0 and draft[n].target.firepower.max >= draft[n].target.firepower.min"
					TabRejected["cause"] = { [1] = draft[n].target.firepower.max, [2]  = draft[n].target.firepower.max, }
					TabRejected["ligne"]  = debug.getinfo(1).currentline
					table.insert(draft[n]["rejected"], TabRejected)
					log.traceVeryLow("draft[" .. n .. "][rejected]:\n" .. inspect(TabRejected))
				end
			else
				local TabRejected = {}
				TabRejected["sujet"]  = "MultiPACKAGE A 0 (?)if draft[n].multipack == nil or draft[n].multipack > 0"
				TabRejected["cause"] = { [1] = draft[n].multipack, [2]  = draft[n].multipack, }
				TabRejected["ligne"]  = debug.getinfo(1).currentline
				table.insert(draft[n]["rejected"], TabRejected)
			end
		else 
			local TabRejected = {}
			TabRejected["sujet"]  = "MENACE TROP IMPORTANTE (descendre minscore ou diminuer Menace AA AS) draft[n].loadout.minscore <= draft[n].score"
			TabRejected["cause"] = { [1] = draft[n].loadout.minscore, [2]  = draft[n].score, }
			TabRejected["ligne"]  = debug.getinfo(1).currentline
			table.insert(draft[n]["rejected"], TabRejected)	
			log.traceVeryLow("draft[" .. n .. "][rejected]:\n" .. inspect(TabRejected))
		end
	end
end

if Debug.Generator.affiche then	
		
	for side, sorties in pairs(draft_sorties) do	
		local di = 1 
		for draft_n, draft in pairs(sorties) do	
			local NameOK = false
			for _PlaneTask, PlaneTask in pairs(draft.support) do
				for taskName, task in pairs(PlaneTask) do	
					if type(task) == "table" then
						if task.name == "testsquad" then
							NameOK = true
						end
					end
				end
			end	
						
			if  di < Debug.Generator.nb or draft.name == "testsquad" or NameOK  then
				print(	"N° " .. draft_n..
						-- " /support/ " ..tostring(draft.support)..
						" /Id/ " ..tostring(draft.id)..
						" /name/ " ..draft.name..
						" /Nb/ " ..draft.number..
						" /Type/ "..draft.type..
						" /threatsGround/ "..round(draft.threatsGround)..
						" /threatsAir/ "..round(draft.threatsAir)..
						" /Score/ " ..round(draft.score)..
						" /Task/ "..draft.task..
						" /Target/ "..tostring(draft.target_name)
						)
				di = di +1
				for _PlaneTask, PlaneTask in pairs(draft.support) do
					for taskName, task in pairs(PlaneTask) do	
						if type(task) == "table" then	
							print(	"    ---> Nsupport " .._PlaneTask.." ".. taskName..
									" /Id/ " ..tostring(task.id)..
									" /name/ " ..task.name..
									" /Nb/ " ..task.number..
									" /escort_max/ " ..tostring(PlaneTask.escort_max)..
									" /Type/ "..task.type..
									" /Task/ "..task.task..
									" /NbTotSupt/ " ..tostring(task.NbTotalSupport)..
									" /Target/ "..task.target_name
									)
						end
					end
				end
				if draft.rejected then
					for id, _rejected in pairs(draft.rejected) do
						print(	" rejected/ ".._rejected.sujet..
							" / cause " ..tostring(_rejected.cause[1])..
							" "..tostring(_rejected.cause[2])..
							" / ligne " ..tostring(_rejected.ligne)
							)
					end
				end
				print()
			end
		end
		-- print()	
		-- print()	
		-- print()	
	end
	-- print()	
	-- print()	
	-- print()	
end

--complete unit unavailable table with zero entries for unassigned aircraft
for side,unit in pairs(oob_air) do																					--iterate through all sides
	for n = 1, #unit do																								--iterate through all units
		if aircraft_availability[unit[n].name] and aircraft_availability[unit[n].name].unavailable then
			for u = 1, unit[n].roster.ready - #aircraft_availability[unit[n].name].unavailable do					--for all ready aircraft that are not assigned to the ATO			
				table.insert(aircraft_availability[unit[n].name].unavailable, 0)									--insert a zero unavilable entry
			end
		end
	end
end


if Debug.Generator.affiche then	
	
	local camp_str = "ATO = " .. TableSerialization(ATO, 0)						--make a string
	local campFile = io.open("Debug/ATO_ATO_Generator.lua", "w")										--open targetlist file
	campFile:write(camp_str)																		--save new data
	campFile:close()

	local camp_str = "camp = " .. TableSerialization(camp, 0)						--make a string
	local campFile = io.open("Debug/camp_ATO_Generator.lua", "w")										--open targetlist file
	campFile:write(camp_str)																		--save new data
	campFile:close()
end