--To check oob_ground for threats and rate and store them in a table for later mission plannning
--Initiated by Main_NextMission.lua
-------------------------------------------------------------------------------------------------------

if not versionDCE then 
	versionDCE = {} 
end

               -- VERSION --

versionDCE["ATO_ThreatEvaluation.lua"] = "OB.1.0.2"

-------------------------------------------------------------------------------------------------------
-- Old_Boy rev. OB.1.0.2: grouping configuration parameters into a single table in camp_init/camp_status
-- Old_Boy rev. OB.1.0.1: implements some customizing property (threat rilevability)
-- Old_Boy rev. OB.1.0.0: implements logging code + new groundthreats and ewr items (from Reglage_f "war over tchad" campaign)
-- miguel21 modification M34.k change freq EWR + custom FrequenceRadio (k: utilise les indicatifs WEST pour EWR)
-- Miguel21 modification M28.b : helicoptere see all SAM
-- Miguel21 modification  M07.g : EWR toujours affich� dans le briefing + 07g ajout des SAM et Boat dans la chaine de detection

-- miguel21 modification M34.f custom FrequenceRadio

--[[ NOTE: launcher, tracker e hq vengono definiti con il livello di minaccia: se la valutazione delle minaccia per il calcolo della rotta dovrebbe 
considerare solo traker e radar rilevati dall'"intelligence" e dalle reco quindi verificare se la tabella delle minaccie viene popolata includendo 
in modo casuale una percentuale degli asset totali differenziando dai grandi SAM che é molto probabile che vengano immediatamente rilevati: 

igla.rilevability = 0.3
Shilka.rilevability = 0.5 (ha il radar)
S2.rilevability = 0.9

ground_threat_rilevability_capacity[0-1] = (air_recon_efficency [0-1] + air_recon_efficency[0-1])/2

ground_threat_rilevability_capacity = 1 -> rilev_success = 0.5 + rand(0-1)
ground_threat_rilevability_capacity = 0.5 -> rilev_success = 0.25 + rand(0-1)
rilev_success = ground_threat_rilevability_capacity/2 + rand(0, 1)
if rilev_success > 1 then rilev_success = 1

se rand > (1-sam.rilevability)
  add.table(sam)

teoricamente igla e sam IR (senza radar)  non dovrebbero essere rilevati inoltre solo i radar 
sam (tracker ecc) dovrebbero essere rilevati

controlla se SA-3 e SA-2 sono inseriti boh non ci sono neanche nel modulo aggiornato, verifica le unit.tyope
è preso da miz e qual'è quello del sa-2

]]


local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua")
-- NOTE MARCO: prova a caricarlo usando require(".. . .. . .. .ScriptsMod."versionPackageICM..".UTIL_Log.lua")
-- NOTE MARCO: https://forum.defold.com/t/including-a-lua-module-solved/2747/2
local log_level = LOGGING_LEVEL -- "traceVeryLow" --
local function_log_level = log_level --log_level
log.activate = false-- select true to activate log
log.level = log_level 
log.outfile = LOG_DIR .. "LOG_ATO_ThreatEvalutation." .. camp.mission .. ".log" 
local local_debug = false -- local debug   
local active_log = false -- select true to activate log
log.info("Start")

--[[
camp.module_config.ATO_ThreatEvaluation = {
	
	MIN_ASSET_FOR_COMPUTE_LEVEL_INTERCEPT = 3,								-- minimum asset unless specified otherwise
	MIN_ASSET_FOR_COMPUTE_LEVEL_CAP = 3,									-- minimum asset unless specified otherwise
	GROUND_THREAT_RILEVABILITY_BLUE_AIR_CAPACITY = 1,						-- capacity for ground threath rilevability (1: max capacity, 0 minimum capacity)
	GROUND_THREAT_RILEVABILITY_BLUE_GROUND_CAPACITY = 1,					-- capacity for ground threath rilevability (1: max capacity, 0 minimum capacity)
	GROUND_THREAT_RILEVABILITY_RED_AIR_CAPACITY = 1,						-- capacity for ground threath rilevability (1: max capacity, 0 minimum capacity)
	GROUND_THREAT_RILEVABILITY_RED_GROUND_CAPACITY = 1,						-- capacity for ground threath rilevability (1: max capacity, 0 minimum capacity)
	MAN_SAM_RILEVABILITY = 0.2,												-- specific ground asset rilevability (1: detectability ensured, 0 asset undetectable)
	SMALL_AAA_SAM_IR_VEHICLE_RILEVABILITY = 0.4,							-- specific ground asset rilevability (1: detectability ensured, 0 asset undetectable)
	SMALL_AAA_SAM_RADAR_VEHICLE_RILEVABILITY = 0.5,							-- specific ground asset rilevability (1: detectability ensured, 0 asset undetectable)
	MEDIUM_AAA_SAM_IR_VEHICLE_RILEVABILITY = 0.6,							-- specific ground asset rilevability (1: detectability ensured, 0 asset undetectable)
	MEDIUM_AAA_SAM_RADAR_VEHICLE_RILEVABILITY = 0.7,
	LARGE_SAM_VEHICLE_RILEVABILITY = 0.8,
	SMALL_AAA_SAM_FIXEDPOS_RILEVABILITY = 0.6,
	MEDIUM_AAA_SAM_FIXEDPOS_RILEVABILITY = 0.8,
	LARGE_AAA_SAM_FIXEDPOS_RILEVABILITY = 0.9,
	SMALL_SHIP_RILEVABILITY = 0.7,
	MEDIUM_SHIP_RILEVABILITY = 0.8,
	LARGE_SHIP_RILEVABILITY = 0.95,
}
]]


CreatePlageFrequency()																--trouve une plage de frequence commune si c'est possible

--table to store ground/sea threats
groundthreats = {
	blue = {																		--blue threats (to red)
	},
	red = {																			--red threats (to blue)
	}
}

local callsign_west = {
		JTAC_EWR = {
			[1] = "Axeman",	
			[2] = "Darknight",
			[3] = "Warrior",
			[4] = "Pointer",	
			[5] = "Eyeball",	
			[6] = "Moonbeam",	
			[7] = "Whiplash",	
			[8] = "Finger",	
			[9] = "Pinpoint",	
			[10] = "Ferret",	
			[11] = "Shaba",	
			[12] = "Playboy",	
			[13] = "Hammer",	
			[14] = "Jaguar",	
			[15] = "Deathstar",	
			[16] = "Anvil",	
			[17] = "Firefly",	
			[18] = "Mantis",	
			[19] = "Badger",
			}
}

-- evalutate threat rilevability from recognition capability of a specific side
local function evalutateThreatRilevation(unit_rilevability, side_)
	local previous_log_level = log.level
	log.level =function_log_level
	local nameFunction = "function evalutateThreatRilevation(unit_rilevability: " .. unit_rilevability .. ", side_: " .. side_ .. "): "    
	log.debug("Start " .. nameFunction)
	local ret = false

	if side_ == "blue" then
		ground_threat_rilevability_air_capacity = camp.module_config.ATO_ThreatEvaluation.GROUND_THREAT_RILEVABILITY_BLUE_AIR_CAPACITY
		ground_threat_rilevability_ground_capacity = camp.module_config.ATO_ThreatEvaluation.GROUND_THREAT_RILEVABILITY_BLUE_GROUND_CAPACITY
	
	elseif side_ == "red" then
		ground_threat_rilevability_air_capacity = camp.module_config.ATO_ThreatEvaluation.GROUND_THREAT_RILEVABILITY_RED_AIR_CAPACITY
		ground_threat_rilevability_ground_capacity = camp.module_config.ATO_ThreatEvaluation.GROUND_THREAT_RILEVABILITY_RED_GROUND_CAPACITY

	else
		log.warn(nameFunction .. "Anomaly: undefined side")
		ground_threat_rilevability_air_capacity = 1
		ground_threat_rilevability_ground_capacity = 1
	end

	local a = 1 -- weight factor for air_threat_rilevability_air_capacity
	local b = 3 -- weight factor for ground_threat_rilevability_ground_capacity
	local ground_threat_rilevability_capacity = ( ground_threat_rilevability_air_capacity * a + ground_threat_rilevability_ground_capacity * b ) / ( a + b ) -- ground_threat_rilevability_capacity = 0 - 1 (max)
	local rilev_success = ground_threat_rilevability_capacity / 3.33 + math.random() -- with ground_... = 1 -> always success for unit with rilevability >= 0.7
	log.trace("ground_threat_rilevability_air_capacity: " .. ground_threat_rilevability_air_capacity .. ", ground_threat_rilevability_ground_capacity: " .. ground_threat_rilevability_ground_capacity .. ", ground_threat_rilevability_capacity: " .. ground_threat_rilevability_capacity .. ", rilev_success: " .. rilev_success)

	if rilev_success >= (1 - unit_rilevability)  then
		ret = true

	else
		ret = false
	end	 	

	log.trace("return: " .. tostring(ret))
	log.level = previous_log_level
	return ret
end
	
--function to check if a unit is a threat, assign threat values and add to threats table
local function AddThreat(unit, side, hide)											--unput is side and unit-table from oob_ground	-- Miguel21 modification M28.b : helicoptere see all SAM (on ajoute Hide)			
	local previous_log_level = log.level					
	log.level = function_log_level
	local nameFunction = "function AddThreat(" .. unit.type .. "-" .. unit.name .. ", " .. side .. ", " .. tostring(hide) .. "): "    
	log.debug("Start " .. nameFunction)
	local threatentry = {}	
		

	if unit.type == "Vulcan" then --OK
		threatentry = {
			type = unit.type,
			class = "AAA",
			level = 1,																--threat level: da 1 a 10(max) -- 1 = low, 2 = medium, 3 = high. NOTA MARCO: nel modulo sono assegnati valori fino a 10
			SEAD_offset = 0,														--number of SEAD sorties required to offset threat
			x = unit.x,																--position x-coordinate
			y = unit.y,																--position y-coordinate
			range = 2600,-- https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 2000, verifica ME  --range of threat --  
			night = false,															--night capable
			elevation = 3,															--sensor elevation above ground
			min_alt = 0,															--minimal threat altitute
			max_alt = 1400,--DCE 1400, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 1500, verifica ME --maximal threat altitude
			rilevability =  camp.module_config.ATO_ThreatEvaluation.MEDIUM_AAA_SAM_RADAR_VEHICLE_RILEVABILITY,				--rilevability level: from 0 to 1 (max)
		}
	
		
	elseif unit.type == "ZSU-23-4 Shilka" then --OK
		threatentry = {
			type = unit.type,
			class = "AAA",
			level = 2,
			SEAD_offset = 0,
			x = unit.x,
			y = unit.y,
			range = 2500, -- stesso di airgoon
			night = true,
			elevation = 3.5,
			min_alt = 10,
			max_alt = 2000, -- stesso di airgoon
			rilevability =  camp.module_config.ATO_ThreatEvaluation.MEDIUM_AAA_SAM_RADAR_VEHICLE_RILEVABILITY,
		}
	
	elseif unit.type == "ZU-23 Emplacement Closed" or unit.type == "Ural-375 ZU-23" then  --OK
		threatentry = {
			type = unit.type,
			class = "AAA",
			level = 1,
			SEAD_offset = 0, -- radar sam >0, ir sam = 0; num of sam asset used for evalutate num of sead unit (max 4 (patriot, s-300 min 1 (tunguska 1))  
			x = unit.x,
			y = unit.y,
			range = 2500,  --DCS ENCYCLOPEDIA: 2500, stesso di airgoon
			night = false,
			elevation = 3.5,
			min_alt = 10,
			max_alt = 2000,  --DCS ENCYCLOPEDIA: 2000, stesso di airgoon
			rilevability =  camp.module_config.ATO_ThreatEvaluation.SMALL_AAA_SAM_IR_VEHICLE_RILEVABILITY,
		}

	elseif unit.type == "ZSU_57_2" then --OK
		threatentry = {
			type = unit.type,
			class = "AAA",
			level = 1,
			SEAD_offset = 0,
			x = unit.x,
			y = unit.y,
			range = 7000,  -- detection from ME: 5000 (detection < range) DCS ENCYCLOPEDIA: no, airgoon: 7000-0 
			night = false,
			elevation = 3.5,
			min_alt = 0,
			max_alt = 4000,  --DCS ENCYCLOPEDIA: no, , airgoon: 4000 
			rilevability =  camp.module_config.ATO_ThreatEvaluation.SMALL_AAA_SAM_IR_VEHICLE_RILEVABILITY,
		}
			
	elseif unit.type == "Gepard" then --OK
		threatentry = {
			type = unit.type,
			class = "AAA",
			level = 2,
			SEAD_offset = 0,
			x = unit.x,
			y = unit.y,
			range = 4000, --DCE 3700, DCS ENCYCLOPEDIA: 3000, , airgoon: 4000-0 , verifica ME
			night = true,
			elevation = 4,
			min_alt = 0,
			max_alt = 3000,--DCE 2900, airgoon: 3000 
			rilevability = camp.module_config.ATO_ThreatEvaluation.MEDIUM_AAA_SAM_RADAR_VEHICLE_RILEVABILITY,
		}
	
		
	elseif unit.type == "M1097 Avenger" then
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 3,
			SEAD_offset = 0,
			x = unit.x,
			y = unit.y,
			range = 7000, --airgoon 6000-200, DCE: 7000 verifica ME
			--minrange = 200,
			night = true,
			elevation = 3,
			min_alt = 10,
			max_alt = 3400,--airgoon 3500
			rilevability = camp.module_config.ATO_ThreatEvaluation.MEDIUM_AAA_SAM_IR_VEHICLE_RILEVABILITY,
		}
		
	
		
	elseif unit.type == "M48 Chaparral" then
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 3,
			SEAD_offset = 0,
			x = unit.x,
			y = unit.y,
			range = 5600, -- DCS ENCYCLOPEDIA: 4800, --airgoon 8500-300 -- verifica ME
			--minrange = 300,
			night = false,
			elevation = 3,
			min_alt = 46,
			max_alt = 2900, -- airgoon 3000
			rilevability = camp.module_config.ATO_ThreatEvaluation.MEDIUM_AAA_SAM_IR_VEHICLE_RILEVABILITY,
		}
	
		
	elseif unit.type == "M6 Linebacker" then
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 3,
			SEAD_offset = 0,
			x = unit.x,
			y = unit.y,
			range = 4500, --DCE: 3750, DCS ENCYCLOPEDIA: no info, airgoon: 4500-200, verifica ME
			--minrange = 200,
			night = true,
			elevation = 3,
			min_alt = 0,
			max_alt = 3400, --airgoon 3500
			rilevability = camp.module_config.ATO_ThreatEvaluation.MEDIUM_AAA_SAM_IR_VEHICLE_RILEVABILITY,
		}
	
		
	elseif unit.type == "Stinger manpad" then
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 3,
			SEAD_offset = 0,
			x = unit.x,
			y = unit.y,
			range = 4500, --DCE 3750, DCS ENCYCLOPEDIA: 4000 (FIM-92A), 4500 FIM-92B/C), airgoon: 4500-200, verifica ME
			--minrange = 200,
			night = false,
			elevation = 3,
			min_alt = 10,
			max_alt = 3500,  --DCE: 2000, DCS ENCYCLOPEDIA: 3500 (FIM-92A), 3800 FIM-92B/C), airgoon: 3500,
			rilevability = camp.module_config.ATO_ThreatEvaluation.MAN_SAM_RILEVABILITY,
		}
	
		
	elseif unit.type == "SA-18 Igla-S manpad" then
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 3,
			SEAD_offset = 0,
			x = unit.x,
			y = unit.y,
			range = 4650,  --DCS ENCYCLOPEDIA: 6000, airgoon: 4500-500 -verifica ME
			--minrange = 500,
			night = false,
			elevation = 3,
			min_alt = 10, --DCS ENCYCLOPEDIA: 10
			max_alt = 3500, --DCE: 3800, DCS ENCYCLOPEDIA: 3500, airgoon: 3500
			rilevability = camp.module_config.ATO_ThreatEvaluation.MAN_SAM_RILEVABILITY,
		}
	
	elseif unit.type == "SA-18 Igla manpad" then -- new
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 3,
			SEAD_offset = 0,
			x = unit.x,
			y = unit.y,
			range = 5200,  --DCS ENCYCLOPEDIA: 5200, airgoon: 4500-500 -verifica ME
			--minrange = 500,
			night = false,
			elevation = 3,
			min_alt = 10, --DCS ENCYCLOPEDIA: 10
			max_alt = 3500, --DCS ENCYCLOPEDIA: 3500, airgoon: 3500
			rilevability = camp.module_config.ATO_ThreatEvaluation.MAN_SAM_RILEVABILITY,
		}
		
	elseif unit.type == "Strela-1 9P31" then
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 3,
			SEAD_offset = 0,
			x = unit.x,
			y = unit.y,
			range = 4650, --DCE: 4650, DCS ENCYCLOPEDIA: 4200, airgoon 4200-800 -verifica ME
			--minrange = 800,
			night = false,
			elevation = 3,
			min_alt = 30, --DCS ENCYCLOPEDIA: 30, airgoon: 30
			max_alt = 3700, --DCE: 3700, DCS ENCYCLOPEDIA: 3500, airgoon: 3500
			rilevability = camp.module_config.ATO_ThreatEvaluation.MEDIUM_AAA_SAM_IR_VEHICLE_RILEVABILITY,
		}
	
	
	elseif unit.type == "Strela-10M3" then
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 3,
			SEAD_offset = 0,
			x = unit.x,
			y = unit.y,
			range = 5200, --DCE:5200, --DCS ENCYCLOPEDIA: 5000, airgoon: 5000, verifica ME
			-- minrange = 200, --airgoon 800
			night = false,
			elevation = 3.5,
			min_alt = 22, --DCS ENCYCLOPEDIA: 10
			max_alt = 4600, --DCS ENCYCLOPEDIA: 3500
			rilevability = camp.module_config.ATO_ThreatEvaluation.MEDIUM_AAA_SAM_IR_VEHICLE_RILEVABILITY,
		}
	
		
	elseif unit.type == "2S6 Tunguska" then
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 5,
			SEAD_offset = 1,
			x = unit.x,
			y = unit.y,
			range = 8000,  --DCE: 7450, DCS ENCYCLOPEDIA: 12000, airgoon 8000-2000 -- verifica ME
			--minrange = 1500, --airgoon: 2000
			night = true,
			elevation = 3.5,
			min_alt = 0, --DCS ENCYCLOPEDIA: 10, airgoon 14.5, 0 (cannons)
			max_alt = 6000,  --DCE: 4900,  DCS ENCYCLOPEDIA: 6000, airgoon: 3500
			rilevability = camp.module_config.ATO_ThreatEvaluation.MEDIUM_AAA_SAM_RADAR_VEHICLE_RILEVABILITY,
		}
	
	
	elseif unit.type == "rapier_fsa_blindfire_radar" then
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 5,
			SEAD_offset = 1,
			x = unit.x,
			y = unit.y,
			range = 8500,  --DCE: 8500--DCS MISSION EDITOR: 30000 (?? tracker o launcher), airgoon: 6800-400 (launcher) --verifica ME (vedi con il launcher)
			--minrange = 500, airgoon: 500
			night = true,
			elevation = 2.5,
			min_alt = 50, --airgoon: 50
			max_alt = 3000,--airgoon: 3000
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_AAA_SAM_FIXEDPOS_RILEVABILITY,
		}
	
		
	elseif unit.type == "rapier_fsa_optical_tracker_unit" then --valuta se eliminare per evitare doppio con sopra
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 5,
			SEAD_offset = 0,
			x = unit.x,
			y = unit.y,
			range = 8550,--DCS MISSIONE EDITOR: launcher 6800
			night = false,
			elevation = 1.5,
			min_alt = 0,
			max_alt = 3000,
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_AAA_SAM_FIXEDPOS_RILEVABILITY,
		}
	
	
	elseif unit.type == "Roland ADS" then
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 5,
			SEAD_offset = 1,
			x = unit.x,
			y = unit.y,
			range = 8000, --DCS MISSION EDITOR: 6300, airgoon 8000-500 --verifica ME (launcher)
			--minrange = 500,
			night = true,
			elevation = 4,
			min_alt = 10,--DCS MISSION EDITOR: launcher 10
			max_alt = 6000,--DCS MISSION EDITOR: launcher 5500, airgoon: 15-6000
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_SAM_VEHICLE_RILEVABILITY,
		}
	
		
	elseif unit.type == "HQ-7_STR_SP" then --SAM china ?
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 3,
			SEAD_offset = 1,
			x = unit.x,
			y = unit.y,
			range = 12000,
			night = true,
			elevation = 4,
			min_alt = 0,
			max_alt = 5500,
			rilevability = camp.module_config.ATO_ThreatEvaluation.MEDIUM_AAA_SAM_RADAR_VEHICLE_RILEVABILITY,
		}

	
	elseif unit.type == "HQ-7_LN_SP" then --SAM china ?
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 2,
			SEAD_offset = 1,
			x = unit.x,
			y = unit.y,
			range = 12000,--DCS MISSIONE EDITOR, ENCYCLOPEDIA: non presente
			night = true,
			elevation = 4,
			min_alt = 0,
			max_alt = 5500,
			rilevability = camp.module_config.ATO_ThreatEvaluation.MEDIUM_AAA_SAM_RADAR_VEHICLE_RILEVABILITY,
		}

		
	elseif unit.type == "Hawk tr" then 
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 7,
			SEAD_offset = 2,
			x = unit.x,
			y = unit.y,
			range = 45000, --DCS ENCYCLOPEDIA:  40000, LAUNCHER DCS ENCYCLOPEDIA:  32000, MISSION EDITOR : 45000, airgoon: 45000-1500
			--minrange = 2000, --LAUNCHER, airgoon 1500
			range_at_low = 40000, -- NEW from airgoon: 22000
			max_low_alt = 200,-- boh NEW NEW from airgoon
			night = true,
			elevation = 3,
			min_alt = 100, -- DCE: 135, LAUNCHER DCS ENCYCLOPEDIA:  60, airgoon 25-18000
			max_alt = 18000, --LAUNCHER DCS ENCYCLOPEDIA = 13700, airgoon 18000
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_SAM_VEHICLE_RILEVABILITY,
		}	
		
	elseif unit.type == "Patriot str" then 
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 10,
			SEAD_offset = 4,
			x = unit.x,
			y = unit.y,
			range = 100000,--DCS ENCYCLOPEDIA:  170000, LAUNCHER DCS ENCYCLOPEDIA:  160000, MISSION EDITOR : 100000, airgoon: 120000
			--minrange = 3000,
			range_at_low = 90000, 
			max_low_alt = 200,-- boh
			night = true,
			elevation = 6,
			min_alt = 25, --airgoon 25
			max_alt = 24240, -- LAUNCHER --DCS ENCYCLOPEDIA:  24240, airgoon 24240
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_SAM_VEHICLE_RILEVABILITY,
		}
	
	
	elseif unit.type == "NASAMS_Radar_MPQ64F1" then 
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 8,
			SEAD_offset = 2,
			x = unit.x,
			y = unit.y,
			range = 15000,--DCS ENCYCLOPEDIA:  no, LAUNCHER DCS ENCYCLOPEDIA: nothing, MISSION EDITOR : 15000 AIM-120B e C airgoon  AIM-B: 57000, AIM-C: 61000 --verifica ME
			--minrange = 700
			range_at_low = 13000, -- NEW from airgoon  120B: 14000, 120C: 16000
			max_low_alt = 200,-- boh, NEW NEW from airgoon
			night = true,
			elevation = 4,
			min_alt = 1,
			max_alt = 15000, --airgoon: 120B, 20000, 120C: 26000
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_SAM_VEHICLE_RILEVABILITY,
		}

	
	elseif unit.type == "SNR_75V" then -- SAM SA-2  S-75 "Guideline" OK
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 5,
			SEAD_offset = 2,
			x = unit.x,
			y = unit.y,
			range = 43000,--DCS ENCYCLOPEDIA:  no, LAUNCHER DCS ENCYCLOPEDIA:  no, MISSION EDITOR : 43000, airgoon 7000-30000 (high alt), 7000-40000 --verifica ME
			--minrange = 7000,
			range_at_low = 38000, -- NEW from airgoon: 30000  
			max_low_alt = 200,--boh
			night = true,
			elevation = 3,
			min_alt = 100, --DCE: 50, airgoon 100, test: 100
			max_alt = 25000, --DCE: 25000, airgoon 20000
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_AAA_SAM_FIXEDPOS_RILEVABILITY,
		}
	
	
	elseif unit.type == "snr s-125 tr" then
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 6,
			SEAD_offset = 2,
			x = unit.x,
			y = unit.y,
			range = 25000, --DCS ENCYCLOPEDIA:  no, LAUNCHER DCS ENCYCLOPEDIA:  no, MISSION EDITOR : 18000, airgoon: 3500-18000 (high alt), 3500-11000 (low alt)
			range_at_low = 22000, -- NEW from airgoon: 11000  
			max_low_alt = 200,-- boh, NEW NEW from airgoon
			-- minrange = 3500,
			night = true,
			elevation = 3,
			min_alt = 20,-- airgoon 20
			max_alt = 20000, --airgoon 20000
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_AAA_SAM_FIXEDPOS_RILEVABILITY,
		}
	
		
	elseif unit.type == "Kub 1S91 str" then
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 7,
			SEAD_offset = 2,
			x = unit.x,
			y = unit.y,
			range = 25000, --DCS ENCYCLOPEDIA:  24000, LAUNCHER DCS ENCYCLOPEDIA:  24000, MISSION EDITOR : 25000, arigoon: 4000-25000
			--minrange = 4000,
			night = true,
			elevation = 6,
			min_alt = 30, -- 
			max_alt = 14000, --DCS ENCYCLOPEDIA:  14000, airgoon: 30-8000
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_SAM_VEHICLE_RILEVABILITY,
		}
	
		
	elseif unit.type == "Osa 9A33 ln" then
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 7,
			SEAD_offset = 1,
			x = unit.x,
			y = unit.y,
			range = 14000, --DCS ENCYCLOPEDIA:  no -- MISSION EDITOR: 11000 --airgoon: 1500-10300 (high alt), 1500-8500 (low alt)
			--minarange = 1500, 
			range_at_low = 11000, -- NEW from airgoon: 11000  
			max_low_alt = 500,-- boh, NEW NEW from airgoon
			night = true,
			elevation = 5.5,
			min_alt = 10, --DCS ENCYCLOPEDIA:  100, airgoon 10-5000
			max_alt = 6400,
			rilevability = camp.module_config.ATO_ThreatEvaluation.MEDIUM_AAA_SAM_RADAR_VEHICLE_RILEVABILITY,
		}
	
		
	elseif unit.type == "SA-11 Buk SR 9S18M1" then --OK
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 8,
			SEAD_offset = 2,
			x = unit.x,
			y = unit.y,
			range = 35000, --DCS ENCYCLOPEDIA:  no -- MISSION EDITOR: 35000, airgoon: 3300-35000 (high alt),  3300-25500 (high alt) --verifica ME launcher
			--minarange = 1500, 
			range_at_low = 32000, -- NEW from airgoon: 11000  
			max_low_alt = 200,-- boh, NEW NEW from airgoon
			night = true,
			elevation = 7,
			min_alt = 15,
			max_alt = 25000, --DCE: 25000, airgoon 15-22000
			rilevability =  camp.module_config.ATO_ThreatEvaluation.LARGE_SAM_VEHICLE_RILEVABILITY,
		}
	
		
	elseif unit.type == "SA-11 Buk LN 9S18M1" then --valuta se elimiare per evitare ridondanza con il Buk SR
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 8,
			SEAD_offset = 2,
			x = unit.x,
			y = unit.y,
			range = 35000, --DCS ENCYCLOPEDIA:  no -- MISSION EDITOR: 35000, airgoon: 3300-35000 (high alt),  3300-25500 (high alt) --verifica ME launcher
			--minarange = 1500, 
			range_at_low = 32000, -- NEW from airgoon: 11000  
			max_low_alt = 200,-- boh, NEW NEW from airgoon
			night = true,
			elevation = 7,
			min_alt = 15,
			max_alt = 25000,
			rilevability =  camp.module_config.ATO_ThreatEvaluation.LARGE_SAM_VEHICLE_RILEVABILITY,
		}

		
	elseif unit.type == "Tor 9A331" then --OK
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 8,
			SEAD_offset = 2,
			x = unit.x,
			y = unit.y,
			range = 12100, --DCS ENCYCLOPEDIA:  no -- MISSION EDITOR: 12000, airgoon: 1500-12000
			--minrange = 1500, 
			night = true,
			elevation = 5,
			min_alt = 10,
			max_alt = 8000, --airgoon: 10-6000
			rilevability = camp.module_config.ATO_ThreatEvaluation.MEDIUM_AAA_SAM_RADAR_VEHICLE_RILEVABILITY,
		}
	
			
	elseif unit.type == "S-300PS 40B6M tr" then -- SA-10 S-300 TEL C e D
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 10,
			SEAD_offset = 4,
			x = unit.x,
			y = unit.y,
			range = 120000, --DCE: 74100, DCS ENCYCLOPEDIA:  47000 (h >= 2000m), 25000 (h <= 25m) -- MISSION EDITOR: 120000, airgoon: 5000-120000 (high alt),  5000-40000 (high alt) --verifica ME launcher
			--minrange = 5000,
			range_at_low = 96000,  
			max_low_alt = 200,-- boh, NEW NEW from airgoon
			night = true,
			elevation = 27.5,
			min_alt = 25, --DCS ENCYCLOPEDIA:  25-27000
			max_alt = 45000, --DCS ENCYCLOPEDIA:  30000, airgoon: 27000
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_SAM_VEHICLE_RILEVABILITY,
		}
	
	-- qui
	elseif unit.type == "RLS_19J6" then --S-200: unit type: RLS_19J6, RPC_5N62V e S-200_Launcher
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 8,
			SEAD_offset = 4,
			x = unit.x,
			y = unit.y,
			range = 254000,  --DCS ENCYCLOPEDIA:  no -- MISSION EDITOR: 254000
			night = true,
			elevation = 27.5,
			min_alt = 50, --DCS ENCYCLOPEDIA:  no
			max_alt = 25000, --verificare --DCS ENCYCLOPEDIA:  no
			rilevability =  camp.module_config.ATO_ThreatEvaluation.LARGE_AAA_SAM_FIXEDPOS_RILEVABILITY,
		}

	elseif unit.type == "RPC_5N62V" then --S-200: unit type: RLS_19J6, RPC_5N62V e S-200_Launcher NOTA: forse da eliminare per non avere ridondanze
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 8,
			SEAD_offset = 4,
			x = unit.x,
			y = unit.y,
			range = 255000,--DCS ENCYCLOPEDIA:  no -- MISSION EDITOR: 7000
			night = true,
			elevation = 27.5,
			min_alt = 50, --DCS ENCYCLOPEDIA:  no
			max_alt = 25000, --verificare --DCS ENCYCLOPEDIA:  no
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_AAA_SAM_FIXEDPOS_RILEVABILITY,
		}

	
	elseif unit.type == "052B" then -- chinese ship, Multirole missile destroyer
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 8,
			SEAD_offset = 2,
			x = unit.x,
			y = unit.y,
			range = 50000,--DCS ENCYCLOPEDIA:  no -- MISSION EDITOR: 7000(??), --DCE: 50000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 150000 --verifica ME
			night = true,
			elevation = 20,
			min_alt = 0,
			max_alt = 25000,--DCE: 25000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 30000 
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_SHIP_RILEVABILITY,
		}
	
	
	elseif unit.type == "052C" then -- chinese ship, Guided missile destroyer
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 10,
			SEAD_offset = 4,
			x = unit.x,
			y = unit.y,
			range = 150000, --DCE: 150000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 100000 --verifica ME
			night = true,
			elevation = 25,
			min_alt = 0,
			max_alt = 30000,--DCE:30000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 30000 
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_SHIP_RILEVABILITY,
		}
	
		
	elseif unit.type == "054A" then -- chinese ship, Multi-role frigate
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 8,
			SEAD_offset = 2,
			x = unit.x,
			y = unit.y,
			range = 60000,--DCE: 60000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 45000 --verifica ME
			night = true,
			elevation = 20,
			min_alt = 0,
			max_alt = 25000,--DCE:25000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 30000 
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_SHIP_RILEVABILITY,
		}
	
		
	elseif unit.type == "MOLNIYA" then -- tarantul III corvette
		threatentry = {
			type = unit.type,
			class = "AAA",
			level = 3,
			SEAD_offset = 0,
			x = unit.x,
			y = unit.y,
			range = 2000,  -- MISSION EDITOR: 2000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 2000
			night = true,
			elevation = 10,
			min_alt = 0,
			max_alt = 1300, -- https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 1300
			rilevability = camp.module_config.ATO_ThreatEvaluation.MEDIUM_SHIP_RILEVABILITY,
		}
	
		
	elseif unit.type == "ALBATROS" then -- nome in ME: Grisha  Corvetta
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 7,
			SEAD_offset = 1,
			x = unit.x,
			y = unit.y,
			range = 15000, -- MISSION EDITOR: 16000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 16000
			night = true,
			elevation = 20,
			min_alt = 25,
			max_alt = 10300, -- https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 10500
			rilevability =  camp.module_config.ATO_ThreatEvaluation.MEDIUM_SHIP_RILEVABILITY,
		}
		
		
	elseif unit.type == "REZKY" then --fregata (Krivak-2)
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 7,
			SEAD_offset = 1,
			x = unit.x,
			y = unit.y,
			range = 16000, -- MISSION EDITOR: 16000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 16000
			night = true,
			elevation = 20,
			min_alt = 25,
			max_alt = 10300, -- https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 10300
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_SHIP_RILEVABILITY,
		}
	
		
	elseif unit.type == "KUZNECOW" then --kuznetsow -- verifica nome quando presente in miz
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 8,
			SEAD_offset = 2,
			x = unit.x,
			y = unit.y,
			range = 12000,-- MISSION EDITOR: 12000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 12000
			night = true,
			elevation = 20,
			min_alt = 25,
			max_alt = 9200,--https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 9200
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_SHIP_RILEVABILITY,
		}
	
			
	elseif unit.type == "NEUSTRASH" then -- frigate
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 8,
			SEAD_offset = 2,
			x = unit.x,
			y = unit.y,
			range = 12000, -- MISSION EDITOR: 12000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 27000 ma i sistemi a bordo (3K95 Kinzhal / SA-N-9 Gauntlet e 3M86 Kortik / CADS-N-1 Kashtan / SA-N-11 “Grison) sono limitati a 12000 range, 6000-10 alt --verifica ME
			--minrange = 0 -- https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 1000 (vedi sopra)
			night = true,
			elevation = 20,
			min_alt = 0,
			max_alt = 6000, --https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 17400, i sistemi SAM sono limitati a  6000 (vedi sopra)
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_SHIP_RILEVABILITY,
		}
	
		
	elseif unit.type == "MOSCOW" then -- Moskva Cruiser? verifica nome quando in miz 
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 10,
			SEAD_offset = 4,
			x = unit.x,
			y = unit.y,
			range = 75000, -- DCE: 90000,  MISSION EDITOR Moskva: 75000, ha un s-300F -https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 120000--verifica ME
			--minrange =2000, -https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 2000
			night = true,
			elevation = 25,
			min_alt = 25, -- -https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 25
			max_alt = 27000, ---DCE: 27000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 30000
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_SHIP_RILEVABILITY,
		}
	
		
	elseif unit.type == "PIOTR" then -- Battlecruiser
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 10,
			SEAD_offset = 4,
			x = unit.x,
			y = unit.y,
			range = 188000, -- DCE: 145000, MISSION EDITOR: 188000, ha un s-300F -https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 120000 --verifica ME
			--minrange =2000, -https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 2000
			night = true,
			elevation = 30,
			min_alt = 25,-- -https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 25
			max_alt = 30000, ---https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 30000
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_SHIP_RILEVABILITY,
		}
	
		
	elseif unit.type == "PERRY" then -- missile frigate
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 7,
			SEAD_offset = 2,
			x = unit.x,
			y = unit.y,
			range = 100000, --DCE: 90000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 100000
			night = true,
			elevation = 20,
			min_alt = 10,
			max_alt = 24400, --DCE: 30000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 24400
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_SHIP_RILEVABILITY,
		}
	
	elseif unit.type == "USS_Arleigh_Burke_IIa" then -- missile destroyer
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 9,
			SEAD_offset = 4,
			x = unit.x,
			y = unit.y,
			range = 100000,--DCE: 10000 (per me typo), https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 100000 --verifica ME
			night = true,
			elevation = 25,
			min_alt = 0,
			max_alt = 30000,--DCE: 30000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 30000
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_SHIP_RILEVABILITY,
		}
		
	elseif unit.type == "TICONDEROG" then -- missile cruiser
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 10,
			SEAD_offset = 4,
			x = unit.x,
			y = unit.y,
			range = 100000,--DCE: 10000 (typo?), https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 100000--verifica ME
			night = true,
			elevation = 25,
			min_alt = 0,
			max_alt = 30000,-- DCE: 30000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 30000
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_SHIP_RILEVABILITY,
		}
	
		
	elseif unit.type == "Stennis" then --CVN-74 John C. Stennis
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 6,
			SEAD_offset = 0,
			x = unit.x,
			y = unit.y,
			range = 27000,--DCE: 27000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 15000 --verifica ME
			night = true,
			elevation = 30,
			min_alt = 0,
			max_alt = 15000,--DCE: 15000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 15000
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_SHIP_RILEVABILITY,
		}
	elseif unit.type == "CVN_71" then --Theodore Roosevelt
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 6,
			SEAD_offset = 2,
			x = unit.x,
			y = unit.y,
			range = 27000,--DCE: 27000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 30000 --verifica ME
			--minrange = 400,
			night = true,
			elevation = 30,
			min_alt = 0,
			max_alt = 15000,--DCE: 15000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 15000
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_SHIP_RILEVABILITY,
		}		
	
	elseif unit.type == "CVN_75" then --Harry S. Truman
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 6,
			SEAD_offset = 2,
			x = unit.x,
			y = unit.y,
			range = 27000,--DCE: 27000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 30000 --verifica ME
			--minrange = 400,
			night = true,
			elevation = 30,
			min_alt = 0,
			max_alt = 15000,--DCE: 15000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 15000
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_SHIP_RILEVABILITY,
		}
	
	elseif unit.type == "CVN_72" then --Abraham Lincoln 
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 6,
			SEAD_offset = 2,
			x = unit.x,
			y = unit.y,
			range = 27000,--DCE: 27000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 30000 --verifica ME
			--minrange = 400,
			night = true,
			elevation = 30,
			min_alt = 0,
			max_alt = 15000,--DCE: 15000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 15000
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_SHIP_RILEVABILITY,
		}

	elseif unit.type == "CVN_73" then -- George Washington
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 6,
			SEAD_offset = 2,
			x = unit.x,
			y = unit.y,
			range = 27000,--DCE: 27000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 30000 --verifica ME
			--minrange = 400,
			night = true,
			elevation = 30,
			min_alt = 0,
			max_alt = 15000,--DCE: 15000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 15000
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_SHIP_RILEVABILITY,
		}

	
		
	elseif unit.type == "VINSON" then
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 6,
			SEAD_offset = 0,
			x = unit.x,
			y = unit.y,
			range = 27000,
			night = true,
			elevation = 30,
			min_alt = 0,
			max_alt = 15000,
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_SHIP_RILEVABILITY,
		}
	
		
	elseif unit.type == "LHA_Tarawa" then --anphibiuos assautl ship
		threatentry = {
			type = unit.type,
			class = "SAM",
			level = 6,
			SEAD_offset = 0,
			x = unit.x,
			y = unit.y,
			range = 27000,--DCE: 27000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 30000
			night = true,
			elevation = 30,
			min_alt = 0,
			max_alt = 15000,--DCE: 15000, https://www.airgoons.com/w/DCS_Reference/Ships/Eastern: 15000
			rilevability = camp.module_config.ATO_ThreatEvaluation.LARGE_SHIP_RILEVABILITY,
		}		
	
	end
	
	-- Miguel21 modification M28.b : helicoptere see all SAM
	if threatentry and threatentry.type then 
		threatentry.hidden = hide
		log.trace(nameFunction .. "defined threatentry for this unit: " .. unit.type .. " - " .. unit.name .. "\nthreathentry:\n" .. inspect(threatentry))			
			
		if evalutateThreatRilevation(threatentry.rilevability, side) then
			table.insert(groundthreats[side], threatentry)			
			log.trace(nameFunction .. "current threatentry tab, inserted in groundthreats[" .. side .. "]")			

		else					
			log.trace(nameFunction .. "current threatentry tab, NOT inserted in groundthreats[" .. side .. "] table")
		end
	end	
	log.level = previous_log_level
end

-- return asset_avalaiability, factor needed to compute level threat of CAP and Intercept task,
-- this factor the factor is calculated considering the number of assets available (roster.ready)
-- ( level threat = capability * firepower * asset_avalaiability )
local function computeAssetAvalaiability(task_type, unit_roster_ready)  --(unit[n].roster.ready / 3),		--total unit threat is capability * firepower * one third of ready aircraft --rivedere se roster.ready è opportuno: la quantità di aerei disponibili non dovrebbe influenzare la sua letalità se ci sono un numero minimo disponibile
	local min_asset
	local asset_avalaiability

	if task_type == "Intercept" then
		min_asset = camp.module_config.ATO_ThreatEvaluation.MIN_ASSET_FOR_COMPUTE_LEVEL_CAP
	
	elseif task_type == "CAP" then
		min_asset = camp.module_config.ATO_ThreatEvaluation.MIN_ASSET_FOR_COMPUTE_LEVEL_INTERCEPT
	
	else
		min_asset = 1
	end

	
	if unit_roster_ready < 	min_asset then
		asset_avalaiability = unit_roster_ready/min_asset
	
	else
		asset_avalaiability = 1
	end

	return asset_avalaiability

end


--table to store ewr
ewr = {
	blue = {																		--blue EWR
	},
	red = {																			--red EWR
	}
}

--GCI table to store EWR radars (and later AWACS and interceptors)
GCI = {
	EWR = {
		["blue"] = {},
		["red"] = {},
	},
	Interceptor = {
		["blue"] = {
			base = {},
			assigned = {},
		},
		["red"] = {
			base = {},
			assigned = {},
		},
	},
	Flag = 500,
}

--function to add EWR units to EWR table
--le navi non sono inserite nella EWR table forse a causa del loro inserimento come SAM (?). 
--le navi sono comunque inserite nella GCI chain detection
local function AddEWR(unit, side, freq, call)
	local call_str = "nil"
	local freq_str = "nil"

	if call then
		call_str = tostring(cal)
	end

	if freq then
		freq_str = tostring(freq)
	end

	local nameFunction = "function AddEWR(" .. unit.type .. "-" .. unit.name .. ", " .. side .. ", " ..  freq_str .. ", " .. call_str .. "): "    
	log.debug("Start " .. nameFunction)
	local entry

	if unit.type == "1L13 EWR" then
		entry = {
			type = unit.type,
			class = "EWR",
			x = unit.x,
			y = unit.y,
			range = 330000,
			frequency = freq,
			callsign = call,
			elevation = 39,
			min_alt = 0,
			max_alt = 30000,
		}
		table.insert(ewr[side], entry)
		GCI.EWR[side][unit.name] = true		
		
	elseif unit.type == "55G6 EWR" then
		local entry = {
			type = unit.type,
			class = "EWR",
			x = unit.x,
			y = unit.y,
			range = 340000,
			frequency = freq,
			callsign = call,
			elevation = 39,
			min_alt = 50,
			max_alt = 30000,
			[call] = true,
		}
		table.insert(ewr[side], entry)
		GCI.EWR[side][unit.name] = true
		
	elseif unit.type == "FPS-117" then
		local entry = {
			type = unit.type,
			class = "EWR",
			x = unit.x,
			y = unit.y,
			range = 461000,
			frequency = freq,
			callsign = call,
			elevation = 39,
			min_alt = 50,
			max_alt = 30000,
			[call] = true,
		}
		table.insert(ewr[side], entry)
		GCI.EWR[side][unit.name] = true	
		
	elseif unit.type == "55G6 EWR" then
		entry = {
			type = unit.type,
			class = "EWR",
			x = unit.x,
			y = unit.y,
			range = 340000,
			frequency = freq,
			callsign = call,
			elevation = 39,
			min_alt = 50,
			max_alt = 30000,
		}
		table.insert(ewr[side], entry)
		GCI.EWR[side][unit.name] = true
		
	elseif unit.type == "p-19 s-125 sr" then								--Participe � la chaine de detection
		entry = {
			type = unit.type,
			class = "EWR",
			x = unit.x,
			y = unit.y,
			range = 160000,
			frequency = freq,
			callsign = call,
			elevation = 6,
			min_alt = 0,
			max_alt = 30000,
		}
		table.insert(ewr[side], entry)
		GCI.EWR[side][unit.name] = true
	
	elseif unit.type == "Dog Ear radar" then								--Participe � la chaine de detection
		entry = {
			type = unit.type,
			class = "EWR",
			x = unit.x,
			y = unit.y,
			range = 35000,
			frequency = freq,
			callsign = call,
			elevation = 4,
			min_alt = 0,
			max_alt = 20000,
		}
		table.insert(ewr[side], entry)
		GCI.EWR[side][unit.name] = true
	
	--M07.g
	elseif unit.type == "SNR_75V" then										--Participe � la chaine de detection
		GCI.EWR[side][unit.name] = true
		
	elseif unit.type == "snr s-125 tr" then										--Participe � la chaine de detection
		GCI.EWR[side][unit.name] = true
		
	elseif unit.type == "RPC_5N62V" then	--SA-5		radar							--Participe � la chaine de detection
		GCI.EWR[side][unit.name] = true
		
	elseif unit.type == "S-300PS 40B6M tr" then										--Participe � la chaine de detection
		GCI.EWR[side][unit.name] = true
		
	elseif unit.type == "Patriot str" then										--Participe � la chaine de detection
		GCI.EWR[side][unit.name] = true
		
	elseif unit.type == "NASAMS_Radar_MPQ64F1" then										--Participe � la chaine de detection
		GCI.EWR[side][unit.name] = true
			
	elseif unit.type == "Hawk tr" then										--Participe � la chaine de detection
		GCI.EWR[side][unit.name] = true
		
	elseif unit.type == "TICONDEROG" then										--Participe � la chaine de detection
		--[[
			entry = {
			type = unit.type,
			class = "EWR",
			x = unit.x,
			y = unit.y,
			range = 35000,
			frequency = freq,
			callsign = call,
			elevation = 4,
			min_alt = 0,
			max_alt = 20000,
		}
		table.insert(ewr[side], entry)
		]]
		GCI.EWR[side][unit.name] = true

	elseif unit.type == "PERRY" then										--Participe � la chaine de detection
		--[[
			entry = {
			type = unit.type,
			class = "EWR",
			x = unit.x,
			y = unit.y,
			range = 100000,
			frequency = freq,
			callsign = call,
			elevation = 20,
			min_alt = 10,
			max_alt = 25000,
		}
		table.insert(ewr[side], entry)
		]]
		GCI.EWR[side][unit.name] = true

	elseif unit.type == "ALBATROS" then										--Participe � la chaine de detection
		--[[
			entry = {
			type = unit.type,
			class = "EWR",
			x = unit.x,
			y = unit.y,
			range = 35000,
			frequency = freq,
			callsign = call,
			elevation = 20,
			min_alt = 25,
			max_alt = 20000,
		}
		table.insert(ewr[side], entry)
		]]
		GCI.EWR[side][unit.name] = true
		
	elseif unit.type == "USS_Arleigh_Burke_IIa" then										--Participe � la chaine de detection
		--[[
			entry = {
			type = unit.type,
			class = "EWR",
			x = unit.x,
			y = unit.y,
			range = 35000,
			frequency = freq,
			callsign = call,
			elevation = 4,
			min_alt = 0,
			max_alt = 20000,
		}
		table.insert(ewr[side], entry)
		]]
		GCI.EWR[side][unit.name] = true
	
	elseif unit.type == "Stennis" then										--Participe � la chaine de detection
		--[[
			entry = {
			type = unit.type,
			class = "EWR",
			x = unit.x,
			y = unit.y,
			range = 35000,
			frequency = freq,
			callsign = call,
			elevation = 4,
			min_alt = 0,
			max_alt = 20000,
		}
		table.insert(ewr[side], entry)
		]]
		GCI.EWR[side][unit.name] = true
		
	elseif unit.type == "CVN_71" then										--Participe � la chaine de detection
		--[[
			entry = {
			type = unit.type,
			class = "EWR",
			x = unit.x,
			y = unit.y,
			range = 35000,
			frequency = freq,
			callsign = call,
			elevation = 4,
			min_alt = 0,
			max_alt = 20000,
		}
		table.insert(ewr[side], entry)
		]]
		GCI.EWR[side][unit.name] = true
		
	elseif unit.type == "CVN_72" then										--Participe � la chaine de detection
		--[[
			entry = {
			type = unit.type,
			class = "EWR",
			x = unit.x,
			y = unit.y,
			range = 35000,
			frequency = freq,
			callsign = call,
			elevation = 4,
			min_alt = 0,
			max_alt = 20000,
		}
		table.insert(ewr[side], entry)
		]]
		GCI.EWR[side][unit.name] = true

	elseif unit.type == "CVN_73" then	  --George Washington						--Participe � la chaine de detection
		--[[
			entry = {
			type = unit.type,
			class = "EWR",
			x = unit.x,
			y = unit.y,
			range = 35000,
			frequency = freq,
			callsign = call,
			elevation = 4,
			min_alt = 0,
			max_alt = 20000,
		}
		table.insert(ewr[side], entry)
		]]
		GCI.EWR[side][unit.name] = true	
		
	elseif unit.type == "CVN_75" then										--Participe � la chaine de detection
		--[[
			entry = {
			type = unit.type,
			class = "EWR",
			x = unit.x,
			y = unit.y,
			range = 35000,
			frequency = freq,
			callsign = call,
			elevation = 4,
			min_alt = 0,
			max_alt = 20000,
		}
		table.insert(ewr[side], entry)
		]]
		GCI.EWR[side][unit.name] = true
	
	elseif unit.type == "LHA_Tarawa" then										--Participe � la chaine de detection
		GCI.EWR[side][unit.name] = true
		
	elseif unit.type == "PIOTR" then										--Participe � la chaine de detection
		GCI.EWR[side][unit.name] = true
		
	elseif unit.type == "MOSCOW" then										--Participe � la chaine de detection
		GCI.EWR[side][unit.name] = true
		
	elseif unit.type == "KUZNECOW" then										--Participe � la chaine de detection
		GCI.EWR[side][unit.name] = true
		
	else 
		-- print("AtoTE ATTENTION, not found "..tostring(unit.type).." in data ATO_ThreatEvaluation. Side: "..tostring(side).." freq: "..tostring(freq).." call: "..tostring(call)) 
		log.warn("unit.type .not found ".. unit.type .." in data ATO_ThreatEvaluation. Side: " .. side .. " freq: " .. freq_str .. " call: ".. call_str)
			-- os.execute 'pause'
	end

	if GCI.EWR[side][unit.name] then
		log.debug(nameFunction .. "Insert in  GCI[" .. side .. "] this unit: " .. unit.type .. "-" .. unit.name)
	end
	
	if entry then
		log.debug(nameFunction .. "Insert in  ewr[" .. side .. "] this unit: " .. unit.type .. "-" .. unit.name)
		log.trace(nameFunction .. "Property inserted in  ewr[" .. side .. "] for this unit: " .. unit.type .. "-" .. unit.name .. ":\n" .. inspect(entry))
	end
	
end


--find ground threats and EWR in vehicles and ships
log.info("find ground threats and EWR in vehicles and ships in oob_ground")

for sidename, side in pairs(oob_ground) do									--Iterate through all sides
	
	for country_n, country in pairs(side) do								--Iterate through all countries
		
		if country.vehicle then												--If country has vehicles
			log.debug("country_n" .. country_n .. ", has vehicles. Iterate groups and units")
			
			for group_n, group in pairs(country.vehicle.group) do			--Iterate through all groups
				log.trace("group.hidden: " .. tostring(group.hidden) .. " should be false ( not hidden). If true evalutate to implements if condition for hidden")
				-- if group.hidden == false then								--group is not hidden	 --Miguel21 modification M28.b
					for unit_n, unit in pairs(group.units) do				--Iterate through all units
						
						if unit.dead ~= true then							--If unit is not dead					
							log.debug("Evaluate group's unit: " .. sidename .. "-" .. unit.type .. "-" .. unit.name .. " as threat")													
							AddThreat(unit, sidename, group.hidden)						--Evaluate unit as threat and add to groundthreats table	 --Miguel21 modification M28.b (ajout hidden)							
							local ewr_task = false							--group has EWR task
							local ewr_freq = nil							--group has a communications frequency
							local ewr_call = nil							--group has a communications callsign
							
							for t = 1, #group.route.points[1].task.params.tasks do												--Iterate through WP1 tasks of group
								
								if group.route.points[1].task.params.tasks[t].id == "EWR" then									--If there is a EWR task
									ewr_task = true																				--set ewr_task true
									log.debug("group has an EWR task -> set ewr_task true")
								end
								
								-- {
									-- ["number"] = 2,
									-- ["auto"] = false,
									-- ["id"] = "EWR",
									-- ["enabled"] = true,
									-- ["params"] = 
									-- {
										-- ["number"] = 1,
										-- ["callname"] = 3,
									-- }, -- end of ["params"]
								-- }, -- end of [2]
								-- camp west, si utilisation des EWR, pour que les indicatifs soient bien pris en compte, l'enregistrement par DCS est comme ci dessus, il n'y a pas de SetCallsign
								if group.route.points[1].task.params.tasks[t].params.callname then							--if group has a callsign set																		
									ewr_call = group.route.points[1].task.params.tasks[t].params.callname					--set callname miguel21 modification M07f
									ewr_call = callsign_west.JTAC_EWR[ewr_call]										
									log.debug("group has a callsign set -> set callname: " .. ewr_call)
								end
								
								if group.route.points[1].task.params.tasks[t].params.action then

									if group.route.points[1].task.params.tasks[t].params.action.id == "SetCallsign" then							--if group has a callsign set										
										-- ewr_call = group.route.points[1].task.params.tasks[t].params.action.params.callsign						--set callsign
									
										if group.route.points[1].task.params.tasks[t].params.action.params.callsign then
											ewr_call = group.route.points[1].task.params.tasks[t].params.action.params.callsign						--set callsign
											log.debug("group has a callsign set -> set callname: " .. ewr_call)

										elseif group.route.points[1].task.params.tasks[t].params.action.params.callname then						-- callname is callsign_west
											ewr_call = group.route.points[1].task.params.tasks[t].params.action.params.callname						--set callname miguel21 modification M07e
											ewr_call = callsign_west.JTAC_EWR[ewr_call]
											log.debug("group has a callsign set -> set callname: " .. ewr_call)
										end	
									end									
									
									if group.route.points[1].task.params.tasks[t].params.action.id == "SetFrequency" then							--if group has a frequency set
										-- ewr_freq = group.route.points[1].task.params.tasks[t].params.action.params.frequency						--set frequency
										-- ewr_freq = tostring(ewr_freq / 1000000)																	--make a string

										ewr_freq = GetFrequency(sidename, group.name, "EWR")
										group.route.points[1].task.params.tasks[t].params.action.params.frequency = ewr_freq * 1000000				-- miguel21 modification M34 change freq EWR
										log.debug("group has a frequency set -> set frequency: " .. tostring(ewr_freq))
										
										for Mgroup_n, Mgroup in pairs(mission.coalition[sidename].country[country_n].vehicle.group) do				-- M34.b, verifie si le Num du group OOB, correspond au Num du groupe mission
											-- mission.coalition[sidename].country[country_n].vehicle.group[group_n].route.points[1].task.params.tasks[t].params.action.params.frequency = ewr_freq * 1000000 -- met à jour la table mission qui est déjà en mémoire
											if group.groupId == Mgroup.groupId then
												Mgroup.route.points[1].task.params.tasks[t].params.action.params.frequency = ewr_freq * 1000000 	-- met à jour la table mission qui est déjà en mémoire
												log.debug("group is mission's group -> set frequency in mission group: " .. tostring(ewr_freq))
											end
										end
										
										ewr_freq = tostring(ewr_freq)
									end
								end
							end

							if ewr_task then
								log.debug("group's unit: " .. unit.type .. "-" .. unit.name .. " added in EWR table, ewr_freq: " .. tostring(ewr_freq) .. ", ewr_call: " .. ewr_call)
								AddEWR(unit, sidename, ewr_freq, ewr_call)	--Add to EWR table								
							end
						end
					end
				--end
			end
		end

		if country.ship then												--If country has ships
			log.debug("country has ships. Iterate groups and units")

			for group_n, group in pairs(country.ship.group) do				--Iterate through all groups
				log.trace("group_n" .. group_n .. " group.hidden: " .. tostring(group.hidden))

				if group.hidden == false then								--group is not hidden
					log.debug("group_n" .. group_n .. " is not hidden. Iterate through all units")

					for unit_n, unit in pairs(group.units) do				--Iterate through all units

						if unit.dead ~= true then							--If unit is not dead
							log.debug("unit: " .. sidename .. "-" .. unit.type .. "-" .. unit.name .. " is not dead, evaluate unit as threat and add to groundthreats table and evaluate unit as EWR and add to EWR table")
							AddThreat(unit, sidename)						--Evaluate unit as threat and add to groundthreats table
							AddEWR(unit, sidename)							--Evaluate unit as EWR and add to EWR table
						end
					end
				end
			end
		end
	end
end


--table to store fighter threats (CAP and intercept)
fighterthreats = {
	blue = {},																					--blue threats (to red)
	red = {}																					--red threats (to blue)
}


--find AWACS, CAP and interceptors in aircraft units and populate ewr/fighterthreats table
log.info("find AWACS, CAP and interceptors in aircraft units and populate ewr/fighterthreats table")

for side,unit in pairs(oob_air) do																--iterate through all sides

	for n = 1, #unit do																			--iterate through all units

		if unit[n].inactive ~= true and unit[n].roster.ready > 0 and db_airbases[unit[n].base] and db_airbases[unit[n].base].inactive ~= true and db_airbases[unit[n].base].x and db_airbases[unit[n].base].y then		--if unit is active and has ready aircraft and its airbase is active
			log.debug("unit[" .. n .. "]: " .. side .. "-" .. unit[n].type .. "-" .. unit[n].name .. " is active and has ready aircraft and its airbase is active. Iterate through all task unit")

			for task,task_bool in pairs(unit[n].tasks) do										--iterate through all tasks of unit

				if task_bool and db_loadouts[unit[n].type][task] then							--task is true and db_loadouts has such tasks
					log.debug("unit[" .. n .. "]: " .. side .. "-" .. unit[n].type .. "-" .. unit[n].name .. " has task:" .. task .. " true and db_loadouts has such tasks. Iterate through all loadout.descriptions for a given aircraft type")

					for loadout_name, loadout in pairs(db_loadouts[unit[n].type][task]) do		--iterate through all loadout.descriptions for a given aircraft type						

						if (daytime == "day" and loadout.day) or (daytime == "night" and loadout.night) or (daytime == "night-day" and (loadout.day or loadout.night)) or (daytime == "day-night" and (loadout.day or loadout.night)) then	--loadout works for current time of day
							log.debug("unit[" .. n .. "]: " .. side .. "-" .. unit[n].type .. "-" .. unit[n].name .. " has loadout:" .. loadout_name .. " operative for current time of day") 

							if loadout.country == nil or loadout.country == unit[n].country then	--loadout is country unspecific or applies to unit country
								log.debug("unit[" .. n .. "]: " .. side .. "-" .. unit[n].type .. "-" .. unit[n].name .. ", loadout is country unspecific or applies to unit country") 
								local entry

								if task == "AWACS" then												--if loadout is AWACS									
									entry = {													--define fighterthreats table entry
										name = unit[n].name,										--unit name
										class = "AWACS",											--class
										x = db_airbases[unit[n].base].x,							--unit homebase position
										y = db_airbases[unit[n].base].y,
										level = 0,
										range = loadout.range + 600000,								--AWACS surveilance radius = AWACS mission range + radar range,
										elevation = 30000,
										min_alt = 0,
										max_alt = 30000,
									}									
									table.insert(ewr[side], entry)

								elseif task == "CAP" then											--if loadout is CAP
									entry = {													--define fighterthreats table entry
										name = unit[n].name,										--unit name
										class = "CAP",												--class
										x = db_airbases[unit[n].base].x,							--unit homebase position
										y = db_airbases[unit[n].base].y,
										level = loadout.capability * loadout.firepower * computeAssetAvalaiability("CAP", unit[n].roster.ready),  --(unit[n].roster.ready / 3),		--total unit threat is capability * firepower * one third of ready aircraft --rivedere se roster.ready è opportuno: la quantità di aerei disponibili non dovrebbe influenzare la sua letalità se ci sono un numero minimo disponibile										
										range = loadout.range,										--Fighter action radius
										LDSD = loadout.LDSD,										--Look Down/Shoot Down
									}									
									table.insert(fighterthreats[side], entry)

								elseif task == "Intercept" then										--if loadout is Intercept
									entry = {													--define fighterthreats table entry
										name = unit[n].name,										--unit name
										class = "Intercept",										--class
										x = db_airbases[unit[n].base].x,							--unit homebase position
										y = db_airbases[unit[n].base].y,
										level = loadout.capability * loadout.firepower * computeAssetAvalaiability("Intercept", unit[n].roster.ready),  --(unit[n].roster.ready / 3),		--total unit threat is capability * firepower * one third of ready aircraft --rivedere se roster.ready è opportuno: la quantità di aerei disponibili non dovrebbe influenzare la sua letalità se ci sono un numero minimo disponibile												--total unit threat is capability * firepower * one third of ready aircraft
										range = loadout.range,										--Fighter action radius
									}									
									table.insert(fighterthreats[side], entry)
								end

								if entry then
									log.info("unit[" .. n .. "]: " .. side .. "-" .. unit[n].type .. "-" .. unit[n].name .. ", with task: " .. task .. ", added in fighterthreats table:\n" .. inspect(entry))
								end
							end
						end
					end
				end
			end
		end
	end
end

-- _affiche(fighterthreats, "ATO_TE fighterthreats")
--add avoidance zones to threattable
log.debug("add avoidance zones to threattable. Iterate through all trigger zones")

for zone_n,zone in pairs(mission.triggers.zones) do												--iterate through all trigger zones

	if string.find(zone.name, "AvoidanceZone") then												--zone is named as avoidance zone
		log.debug("zone is named as avoidance zone")
	
		local threatentry = {																	--define threattable entry
			type = "TriggerZone",
			class = "AvoidanceZone",
			level = 1000,
			SEAD_offset = 0,
			x = zone.x,
			y = zone.y,
			range = zone.radius,
			night = true,
			elevation = 20000,
		}
		local side, level

		if string.find(zone.name, "Blue") then													--Blue avoidance zone is a threat to blue

			if string.find(zone.name, "Low") then												--Low level

				threatentry.min_alt = 0
				threatentry.max_alt = 3000
				table.insert(groundthreats.red, threatentry)

			elseif string.find(zone.name, "High") then											--High level
				threatentry.min_alt = 3000
				threatentry.max_alt = 30000
				table.insert(groundthreats.red, threatentry)
			
			else																				--Low and high level
				threatentry.min_alt = 0
				threatentry.max_alt = 30000
				table.insert(groundthreats.red, threatentry)
			end
		
		elseif string.find(zone.name, "Red") then												--Red avoidance zone is a threat to red
			
			if string.find(zone.name, "Low") then												--Low level
				threatentry.min_alt = 0
				threatentry.max_alt = 3000
				table.insert(groundthreats.blue, threatentry)
	
			elseif string.find(zone.name, "High") then											--High level
				threatentry.min_alt = 3000
				threatentry.max_alt = 30000
				table.insert(groundthreats.blue, threatentry)
	
			else																				--Low and high level
				threatentry.min_alt = 0
				threatentry.max_alt = 30000
				table.insert(groundthreats.blue, threatentry)
			end

		else																					--Undefined avoidance zone is a threat to red and blue
			
			if string.find(zone.name, "Low") then												--Low level
				threatentry.min_alt = 0
				threatentry.max_alt = 3000
				table.insert(groundthreats.red, threatentry)
				table.insert(groundthreats.blue, threatentry)
			
			elseif string.find(zone.name, "High") then											--High level
				threatentry.min_alt = 3000
				threatentry.max_alt = 30000
				table.insert(groundthreats.red, threatentry)
				table.insert(groundthreats.blue, threatentry)
			
			else																				--Low and high level
				threatentry.min_alt = 0
				threatentry.max_alt = 30000
				table.insert(groundthreats.red, threatentry)
				table.insert(groundthreats.blue, threatentry)
			end
		end

		if side and level then
			log.debug("avoidance zone_n: " .. zone_n .. "-" .. side .. "-" .. zone.name .. " with level: " .. level .. " was added in groundthreats table")
			log.trace("threatentry for avoidance zone_n: " .. zone_n .. "-" .. side .. "-" .. zone.name .. ":\n" .. inspect(threatentry))
		end		
	end
end