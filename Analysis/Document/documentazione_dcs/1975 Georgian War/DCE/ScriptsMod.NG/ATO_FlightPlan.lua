--To create the flight plans in the mission file for all flights in the ATO
--Initiated by Main_NextMission.lua
------------------------------------------------------------------------------------------------------- 
-- Miguel Fichier Revision M46.f
------------------------------------------------------------------------------------------------------- 

if not versionDCE then versionDCE = {} end
versionDCE["ATO_FlightPlan.lua"] = "1.40.133"

-- =====================  Marco implementation ==================================
local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua")
-- NOTE MARCO: prova a caricarlo usando require(".. . .. . .. .ScriptsMod."versionPackageICM..".UTIL_Log.lua")
-- NOTE MARCO: https://forum.defold.com/t/including-a-lua-module-solved/2747/2
log.level = LOGGING_LEVEL
log.outfile = LOG_DIR .. "LOG_ATO_FlightPlan." .. camp.mission .. ".log" 
local local_debug = true -- local debug   
log.info("Start")
-- =====================  End Marco implementation ==================================


-- CHCM_FP_01 Check and Help CampaignMaker

-- Eagle_01 Modification E02.a I16 and A-4e
-- Eagle_01 Modification E01.c

-- mouvedOption_CM_01.b : deplace les options de west callSign dans conf_mod /b: previent le CampaignMaker d'une nation manquante
-- ATO_FP_Reglage02 : ATO_lock sur les xpt Join
-- ATO_FP_Reglage01.b : emport, ne pas larguer les emports en cas d'urgence

-- ATO_FP_Debug09.b gestion des apparitions décalé au sol et en vol, 
-- ATO_FP_Debug08 vi trop faible pour les escorteurs des strike trop lent 
-- ATO_FP_Debug07 MP, alti vi unite 
-- ATO_FP_Debug06 strike ASM B52 
-- ATO_FP_Debug05 Escorte
-- ATO_FP_Debug04 Gun = 0 uniquement sur un Flight
-- ATO_FP_Debug03 Antiship strike
-- ATO_FP_Debug02 Interceptor error nb trigger
-- ATO_FP_Debug01.2 alti flight ai en multijoueur

-- miguel21 modification M47.c keeps the history of the campaign files (c: save debugging information during mission generation)
-- miguel21 modification M46.f  singlePlayer with dedicated server (f: set up the server correctly for sixpack)(d: MP spawnTime =0) ((c: D choice with AI AirSpawn) )
-- miguel21 modification M45.s : compatible with 2.7.0 (pqrs: debug deck)(o: bug spawnAir MP)(m: trigger)(l: debug Deck)(k: delayed landing before first catapults)(j: E2 S3 on catapult)(i: debug Deck)(h: player On Sixpack)(g: taxiing timetable)(f: activate true) (e: order of spawn on Deck)(c: IA catapult First)(b: F14 catapult)
-- miguel21 modification M43.c assignment of parking numbers of type C08 (b: ("1.38.106") assignment of parking with a simple numbering )
-- miguel21 modification M42.b : liveryModex
-- miguel21 modification M40 : Pedro Helicopter
											-- miguel21 modification M37.l SuperCarrier (l: ajout alt et speed aux unites)(k: limite à 10 le nb d'avion au début de mission)
-- miguel21 modification M34.i  custom FrequenceRadio (i  3 frequency bands)(g: VHF helicopter)(h: bug Gazelle)
-- Miguel21 modification M33.f2 	Custom Briefing (f: Divert/CVN possible)(d: Divert)(c: Alignement du txt)(onBoardNum)
-- Miguel21 modification M31 	Remove all static aircraft from the deck
-- Miguel21 modification M30.b 	Desactive TriggerStart
-- Miguel21 modification M27.c 	MovedBullseye (c: does not include carriers)
-- Miguel21 modification M24	Set Multiplayer 
-- Miguel21 modification M23	Désactive USN Mod 
-- Miguel21 modification M20	Pannes al�atoires en SingleMission et ForcedOption (external view etc..)
-- Miguel21 modification M18.d despawn/destroy Plane on BaseAirStart
-- Miguel21 modification M17.e	Option F-14B
-- Miguel21 Modification M15.d info catapulte/pont dans briefing
-- Miguel21 modification M14.b : Versionning (b:"1.38.107")
-- Miguel21 modification M12.b 	: Skill
-- Miguel21 modification M11B. 	: Multiplayer--briefing	
-- Miguel21 modification M11.s : Multiplayer (s: F14 no limited to 2) (r: notRecovery for Intercept)(q: take recovery plane)
-- Miguel21 modification M08	: hotstart  --||initialement ((départ de la piste + debug hotstart + intercepteur CVN))
-- Miguel21 modification M06.g : helicoptere playable (g: Start From FARP & LHA & delete E01)
-- Miguel21 modification M03.m4 : parking assignment CVN LHA FARP & shift the spawn (m: debug helico/FARP)(l: best check)(k: check place parking dispo en fonction des minutes)(i: Parking limite little base)
-- Miguel21 modification M01 : ajout datalink
------------------------------------------------------------------------------------------------------- 	
-- Miguel21 modification M24	Set Multiplayer

--todo ajouter une condition: joueur spawn sur sixpack si personne n'y est

local debugStart = true
local debugTxt = ""
local debugFLIGHT = ""

if Multi.NbGroup >= 1 then 

	
	mission_ini.PruneScript = true							-- reduce a mission by removing units (mod Tomsk M09) [MP: recommend: true]					PruneAggressiveness = 1.5,					-- How aggressive should the pruning be [0 to 2], larger numbers will remove more units, 0 = no pruning at all
	mission_ini.PruneStatic = true							-- Should ALL parked (static) aircraft be pruned [MP: recommend: true]
	-- mission_ini.ForcedPruneSam = true						-- PBO-CEF avait pr�vu de garder des SAM actif, cette option les d�sactives tout de m�me [MP: recommend: true]
	mission_ini.failure = false								-- (true or false) Miguel21 modification M20 [MP: recommend: false]
	-- mission_ini.ravitoByConvoy = false					-- [non encore fonctionnel] ravitaillement par convoy routier 
	mission_ini.Keep_USNdeckCrew = false					-- false = supprime US Navy deck crew dans la g�n�ration de mission. Miguel Modification M23
	mission_ini.CVN_CleanDeck = true 							-- true: Remove all static aircraft from the deck. ( M31 )
	
	-- Force vos propres options plutot que ceux de base_ini.miz, qui correspondent � ceux de PBO-CEF ^^
	if not mission.forcedOptions then mission.forcedOptions = {} end
	mission.forcedOptions.accidental_failures =  false
	mission_forcedOptions.wakeTurbulence = false			-- False / true : turbulence  [MP: recommend: false]
	mission_forcedOptions.civTraffic = ""					-- Traffic civil routier : ( "" : OFF ) || ( "low" : BAS ) || ( "medium" : MOYEN )|| ( "high" : ELEVE )  [MP: recommend: ""]
	mission_forcedOptions.birds = 0							-- Collision volatile (probabilit�) ( 0 � 1000 )  [MP: recommend: 0]

	end
	
	----- D�sactive USN Mod -----Miguel21 modification M23
	if not mission_ini.Keep_USNdeckCrew then
		mission.requiredModules = {
			['USN-Deckcrew'] = nil,
		}
	end
	
	--desactive la reservation pour ne pas perturber une boucle de refus de mission
	for k=1, Multi.NbGroup do
		 Multi.Group[k].assigned  = false
	end	 
	
----- Ajoute les pannes al�atoires en SingleMission -----Miguel21 modification M20
	for option, value  in pairs(mission_forcedOptions) do								-- ajoute les options du jeux
		if not mission.forcedOptions then mission.forcedOptions = {} end
		mission.forcedOptions[option] =  value
	end
		
	if mission_ini.failure then										-- not multiplayer --	if mission_ini.failure and not Multi.NbGroup then	
		-- ajoute accidental_failures = true � forcedOptions
		if not mission.forcedOptions then mission.forcedOptions = {} end
		mission.forcedOptions.accidental_failures =  true
		

		local n= 1	
		for _id, failure in pairs(mission.failures) do
			n = n+1
		end
		
		for f = 1, mission_ini.failureNbMax do
				
			local hh = math.random(0, 1)
			local mm = math.random(1, 59)
			local prob = math.random(1, mission_ini.failureProbMax)
			local mmint = math.random(1, 59)
			local id_failed = math.random(1, n-1)
						
			local m = 1
			for _id, failure in pairs(mission.failures) do
			
				if id_failed == m then 
					if not mission.failures[_id] then print("NotFailureId") end
					if not mission.failures[_id]['hh'] then print("NotFailureHh") end
					mission.failures[_id]['hh'] = hh
					mission.failures[_id]['mm'] = mm
					mission.failures[_id]['prob'] = prob
					mission.failures[_id]['enable'] = true
					mission.failures[_id]['mmint'] = mmint
					if Debug.AfficheFailure then print("PossibleFailure ".._id.." "..hh.."H"..mm.." ".." Duration "..mmint.." Probability: "..prob) end				
				end
				m = m+1
			end
		end
	end
	
----- function to create callsigns for aircraft in ATO -----
local callsign_west = {
	generic = {
		[1] = "Enfield",
		[2] = "Springfield",
		[3] = "Uzi",
		[4] = "Colt",
		[5] = "Dodge",
		[6] = "Ford",
		[7] = "Chevy",
		[8] = "Pontiac",
	},
	AWACS = {
		[1] = "Overlord",
		[2] = "Magic",
		[3] = "Wizard",
		[4] = "Focus",
		[5] = "Darkstar",
	},
	tanker = {
		[1] = "Texaco",
		[2] = "Arco",
		[3] = "Shell",
	}
}

local callsign_west_counter = {
	generic = math.random(0, #callsign_west.generic - 1),
	AWACS = math.random(0, #callsign_west.AWACS - 1),
	tanker = math.random(0, #callsign_west.tanker - 1),
}
local callsign_east_counter = 0

local function GetCallsign(country, flight_n, aircraft_n, task)
	local style
	
	-- mouvedOption_CM_01.b : deplace les options de west callSign dans conf_mod /b: previent le CampaignMaker d'une nation manquante
	style = "east"
	
	if not campMod.WestCallsign then 
		if country == "Belgium" or country == "UK" or country == "Georgia" or country == "Denmark" or country == "Israel" or country == "Spain" or country == "Canada" or country == "Norway" or country == "USA" or country == "Turkey" or country == "France" or country == "The Netherlands" or country == "Italy" or country == "Australia" or country == "South Korea" or country == "Croatia" or country == "USAF Aggressors" or country == "Sweden" or country == "Iran" then
			style = "west"
		end
	elseif  campMod.WestCallsign[country] == "west" then
		style = "west"
	end

	local callsign
	if style == "west" then
		local category
		if task == "AWACS" then
			category = "AWACS"
		elseif task == "Refueling" then
			category = "tanker"
		else
			category = "generic"
		end
	
		if flight_n == 1 and aircraft_n == 1 then
			callsign_west_counter[category] = callsign_west_counter[category] + 1
			if callsign_west_counter[category] > #callsign_west[category] then
				callsign_west_counter[category] = 1
			end
			callsign_flight = math.random(0, 8)
		end
		
		if aircraft_n == 1 then
			if not callsign_flight then 
				print()
				print("********************ATTENTION******************")
				print("***************Note for the Campaign Maker*****The nation of a previous aircraft misfiled in the table  conf_mod/campMod.WestCallsign or ATO_FlightPlan/country****************")
				print("********************ATTENTION******************")
				print()
				os.execute 'pause'
			end
			callsign_flight = callsign_flight + 1
			if callsign_flight > 9 then
				callsign_flight = 1
			end
		end
		
		callsign = {
			name = callsign_west[category][callsign_west_counter[category]] .. callsign_flight .. aircraft_n
		}

		_name = callsign_west[category][callsign_west_counter[category]] .. callsign_flight .. aircraft_n
		 
			callsign = {
				[1] = callsign_west_counter[category],
				[2] =  callsign_flight,
				[3] =  aircraft_n,
				name = _name
			}


	elseif style == "east" then
		if aircraft_n == 1 then
			callsign_east_counter = callsign_east_counter + 1
		end
		callsign = 90 + callsign_east_counter * 10 + aircraft_n
	end
	
	return callsign
end


---- function to get sidenumbers -----
local sidenumbers = {}

function GetSidenumber(squadron, lower, upper, nUnit, player, type)				--not local, also used in DC_StaticAircraft
	if sidenumbers[squadron] == nil then										--sidenumber squadron entry does not exist
		sidenumbers[squadron] = {}												--create sidenumber squadron entry
	end
		
	local s																		--new sidenumber
	local counter = 0
	
	--cherche si le joueur fait partie de cet escadron
	local reservedDigit = 0
	for side_name,side in pairs(oob_air) do	
		for n,unit in pairs(side) do
			if unit.name == squadron and unit.player  then
				reservedDigit = 1												--ajoute un chiffre pour les IA, exemple 200+1 pour l'ia, 200 etant reservé au joueur
			end
		end
	end
	-- miguel21 modification M42.b : liveryModex
	local leaderCheck															--on s assure que le num 200 (par exemple) est donné au leader et pas un ailier
	if player and nUnit == 1 then
		s = tonumber(lower)
	else
		repeat
			leaderCheck = true
			counter = counter + 1
			s = math.random(tonumber(lower)+reservedDigit, tonumber(upper))		--find random sidenumber

			if nUnit == 1 and tonumber(string.sub (s, -1)) ~= 0 and not sidenumbers[squadron][lower]  then	--on s assure que le num 200 (par exemple) est donné au leader et pas un ailier
				leaderCheck = false
			end
			
		until (sidenumbers[squadron][s] == nil and leaderCheck)	or counter == 100	--repeat until a sidenumber is found that is not yet in squadron use or stop after 100 tries
		
		--le script n'a pas trouvé de serial non libre
		if counter >= 100 then
			
			local totSerial = {}
			for n=tonumber(lower), tonumber(upper) do								--creation de la table de tous les serial
				totSerial[n] = false
			end

			for n, squad in pairs(sidenumbers[squadron]) do						--suppresion de la table totale des seriales déjà utilisé
				for totN, value in pairs(totSerial) do								--liste la table totale
					if n == totN then												--marque les serial dejà utilisé
						totSerial[totN] = true
					end
				end
			end

			for totN, value in pairs(totSerial) do									--prend le premier serial libre
				if totSerial[totN] == false then
					s = totN
					break
				end
			end
		end
	
	end
	sidenumbers[squadron][s] = true													--mark sidenumber in use for squadron
	
	-- particularité du Harrier : donner 810 pour afficher 18
	if type == "AV8BNA" then	
		local Digit_1 = string.sub(s, -1, -1)		
		local Digit_2 = string.sub(s, -2, -2)		
		s = tonumber(Digit_1..Digit_2.."0")			
		s = string.format("%03d", s)
	else
		local lNew = string.len(s)													--lenght of new sidenumber
		local lOld = string.len(lower)												--lenght of given lower end of sidenumbers
		for n = lNew, lOld - 1 do													--for each character that new sidenumber is smaller than given lower ranger
			s = "0" .. s															--add a zero in front
		end
	end
	
	return tostring(s)															--return sidenumber as string
end


-- --M43 assignation des numeros de parking du type C08 
-- local parkOccupied = {}
-- function GetParkingId(parkingId, base)
	-- local s	
	-- local counter
	-- if not parkOccupied[base]  then										
		-- parkOccupied[base] = {}												
	-- end

	-- for prefix, value in pairs(parkingId) do
		-- counter = 0
		-- if #value == 2 then
			-- lower = value[1]
			-- upper = value[2]
			
			-- repeat
				-- counter = counter + 1
				-- s = math.random(tonumber(lower), tonumber(upper))		
				-- s = prefix..string.format("%02d", s)
			-- until parkOccupied[base][s] == nil 	or counter == 100				
			
		-- elseif #value > 2 then
			-- repeat
				-- counter = counter + 1
				-- local r = math.random(1,#value)
				-- s = value[r]
				-- s = prefix..string.format("%02d", s)
			-- until parkOccupied[base][s] == nil 	or counter == 100					
		-- end
		-- if parkOccupied[base][s] == nil then
			-- break
		-- end
	-- end
	
	-- --ne trouve pas de place libre:
	-- if counter >= 100 then
		-- return false
	-- end
	-- parkOccupied[base][s] = true

	-- return tostring(s)

-- end


---- function to assign A-A TACAN channels ----
tanker_tacan = {}																--table to store tanker TACAN channels
-- https://forums.eagle.ru/showpost.php?p=3821502&postcount=139
-- https://forums.eagle.ru/topic/199994-tacan-and-dl-last-update/
-- 37-67  ??.?
local function GetTankerTACAN()
	local channel
	repeat
		channel = math.random(37, 67)											--find random TACAN channel
	until tanker_tacan[channel] == nil											--repeat until channel is found that is not in use yet
	
	tanker_tacan[channel] = true												--mark channel in use
	return channel																--return channel
end

--Mod M27.b Randomly moves the 2 BullsEye
function fct_MovedBullseye(side, NameTheatre)
	
	local tempArrayBulls = {}
	for name, base in pairs(db_airbases) do 
		if base.x and not base.unitname then
		-- if base.x  then
			if GetDistance(campMod.MovedBullseye[NameTheatre].pos, base) <= (campMod.MovedBullseye[NameTheatre].rayon * 1000) then 
				db_airbases[name]["name"] = name
				table.insert(tempArrayBulls, db_airbases[name])
			end
		end
	end
	
	local i = table.getn(tempArrayBulls)
	
	if i >= 1 then
		j = math.random(1, i)
		mission.coalition[side].bullseye.x = tempArrayBulls[j].x
		mission.coalition[side].bullseye.y = tempArrayBulls[j].y
		
		if not brief then brief = {} end
		if not brief[side] then brief[side] = {} end
		if not brief[side].bullseye then brief[side].bullseye = {} end
		brief[side].bullseye.name = tempArrayBulls[j].name
		brief[side].bullseye.x = tempArrayBulls[j].x
		brief[side].bullseye.y = tempArrayBulls[j].y
		
		if tempArrayBulls[j].gps then 
			brief[side].bullseye.gps = tempArrayBulls[j].gps	
		end
	end
end

-- miguel21 modification M37.l SuperCarrier (l: ajout alt et speed aux unites)(i: option deck air catapult)
--Spawn OnDeck, OnCatapult or OnAir
function SpawnOn(spawn, waypoints, group, Pn, spawnTime, from, flight, f)
	spawn = string.lower(spawn)
	

	
	if  spawn == "air" then								
		if debugStart then debugTxt = debugTxt.."\n"..("AtoFP spawnOair AIR from: "..tostring(from)) end	
		if debugStart then debugTxt = debugTxt.."\n"..("AtoFP spawnOair AIR from: "..tostring(from)) end		
	
		waypoints[1]["action"] = "Turning Point"
		waypoints[1]["type"] = "Turning Point"
		waypoints[1]["alt"] = waypoints[1]["alt"] + (Pn * 500)
		waypoints[1]["speed"] = 140
		-- waypoints[1].ETA = spawnTime
		
		group.start_time = spawnTime
		
		if waypoints[1]["helipadId"] then
			waypoints[1]["helipadId"] = nil
		end
		if waypoints[1]["linkUnit"] then
			waypoints[1]["linkUnit"] = nil
		end		
		
		local alt = 150

		if flight[f].helicopter  then 											-- M6.1 sauf helicopter			
			if db_airbases[flight[f].base].elevation then							--airbase has defined elevation
				alt = alt + db_airbases[flight[f].base].elevation					--make alt above base
			end
			waypoints[1]["alt"] = alt  + (Pn * 10)
		end
		
		-- ATO_FP_Debug01
		for	n = 1 , #group.units do
			group.units[n].x = ((Pn-1) * 1000) + group.units[n].x + (150 * n)
			group.units[n].y = ((Pn-1) * 1000) + group.units[n].y + (150 * n)
			group.units[n].speed = 140
			
			if flight[f].helicopter  then 
				group.units[n]["alt"] = alt  + (Pn * 10)
			else
				group.units[n]["alt"] = waypoints[1]["alt"] + (Pn * 500)
			end
		end
		
		if not group["TrigActivate"] and spawnTime and spawnTime > 1 and Missionfunc then
			
			group["TrigActivate"] = true
			group['lateActivation'] = true											--make group late activation "en vol"
			group['uncontrolled'] = false
			group['tasks'] = {}														--supprime le tasks start
			
			trig_n = Missionfunc + #mission.trig.funcStartup + 1										--next available trigger number
			Missionfunc = Missionfunc + 1 																	--M11.o
			mission.trig.func[trig_n] = "if mission.trig.conditions[" .. trig_n .. "]() then mission.trig.actions[" .. trig_n .. "]() end"
			mission.trig.flag[trig_n] = true
			mission.trig.conditions[trig_n] = "return(c_time_after(" .. spawnTime .. ") )"
			mission.trig.actions[trig_n] = "a_activate_group(" .. group.groupId .. "); mission.trig.func[" .. trig_n .. "]=nil;"	-- ATO_FP_Debug02 Interceptor error nb trigger
			mission.trigrules[trig_n] = {
				['rules'] = {
					[1] = {
						["seconds"] = spawnTime,
						["predicate"] = "c_time_after",
					},
				},
				['eventlist'] = '',
				['comment'] = 'Trigger ' .. trig_n,
				['predicate'] = 'triggerOnce',
				['actions'] = {
					[1] = {
						["group"] = group.groupId,
						["predicate"] = "a_activate_group",
					},
				}
			}
			if debugStart then debugTxt = debugTxt.."\n"..("AtoFP SpawnOn passe activate 01") end
		
		end
		
		-- remet l'horaire d'origine sur activate
		modify_activate_group_time(group, spawnTime, debug.getinfo(1).currentline)
		
		
	elseif spawn == "catapult" then
		
		if debugStart then debugTxt = debugTxt.."\n"..("AtoFP spawnOair CATAPULT from: "..tostring(from)) end	
		
		waypoints[1]["action"] = "From Runway"
		waypoints[1]["type"] = "TakeOff"
		
		waypoints[1]["alt"] = 0
		
		group.uncontrolled = false											-- sur cata, les F14 IA bloquent
	end
	
end


--activate_group_time_after
function activate_group_time_after(group, AirSpawnTime, from)
	
	if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe 1B activate_group_time_after "..tostring(from)) end	
	
	-- group['uncontrolled'] = true
	
	-- group['lateActivation'] = true --incompatible avec l'activation sur sixpack

	if not group["TrigActivate"]  then
		group["TrigActivate"] = true
		local trig_n = Missionfunc + #mission.trig.funcStartup + 1										--next available trigger number
		Missionfunc = Missionfunc + 1 																	--M11.o
		mission.trig.func[trig_n] = "if mission.trig.conditions[" .. trig_n .. "]() then mission.trig.actions[" .. trig_n .. "]() end"
		mission.trig.flag[trig_n] = true
		mission.trig.conditions[trig_n] = "return(c_time_after(" .. AirSpawnTime .. ") )"
		mission.trig.actions[trig_n] = "a_activate_group(" .. group.groupId .. "); mission.trig.func[" .. trig_n .. "]=nil;"	-- ATO_FP_Debug02 Interceptor error nb trigger
		mission.trigrules[trig_n] = {
			['rules'] = {
				[1] = {
					["seconds"] = AirSpawnTime,
					["predicate"] = "c_time_after",
				},
			},
			['eventlist'] = '',
			['comment'] = 'Trigger ' .. trig_n,
			['predicate'] = 'triggerOnce',
			['actions'] = {
				[1] = {
					["group"] = group.groupId,
					["predicate"] = "a_activate_group",
				},
			}
		}

	end
end							

--modify_activate_group_time
function modify_activate_group_time(group, AirSpawnTime, from)
	
	if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe 1B modify_activate_group_time "..tostring(from)) end	
	
	-- group['uncontrolled'] = true
	-- group['lateActivation'] = true --incompatible avec l'activation sur sixpack

	for trig_n = 1, #mission.trigrules  do
	
		if  mission.trigrules[trig_n] and mission.trigrules[trig_n].actions and mission.trigrules[trig_n].actions[1] then
			if  mission.trigrules[trig_n].actions[1].group and mission.trigrules[trig_n].actions[1].group == group.groupId then
				
				if AirSpawnTime == -1 then
					AirSpawnTime = 0
				end
					-- table.remove(mission.trigrules, trig_n)
					-- table.remove(mission.trig.conditions, trig_n)
					-- table.remove(mission.trig.actions, trig_n)
					-- if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe 1C delete_activate_group_time find groupId "..group.groupId.." trig_n: "..tostring(trig_n)) end	
				
				-- else
					mission.trigrules[trig_n].rules[1].seconds = AirSpawnTime			
					
					-- conditions[44] = 'return(c_time_after(2233.512158504) )',
					mission.trig.conditions[trig_n] = "return(c_time_after(" .. AirSpawnTime .. ") )"
					if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe 1Cc modify_activate_group_time find groupId "..group.groupId.." trig_n: "..tostring(trig_n)) end
				-- end
				
				
			end
		end
	end
end							


--Start_set_ai_task
function Start_set_ai_task(group, aiStart_spawn_time, from)
	
	group['uncontrolled'] = true
	
	if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe 1C Start_set_ai_task "..tostring(from)) end	
	
	local trig_n = Missionfunc + #mission.trig.funcStartup + 1										--next available trigger number
	Missionfunc = Missionfunc + 1 
	mission.trig.func[trig_n] = "if mission.trig.conditions[" .. trig_n .. "]() then mission.trig.actions[" .. trig_n .. "]() end"
	mission.trig.flag[trig_n] = true
	mission.trig.conditions[trig_n] = "return(c_time_after(" .. aiStart_spawn_time .. ") )"
	mission.trig.actions[trig_n] = "a_set_ai_task(" .. group.groupId .. ", 1); mission.trig.func[" .. trig_n .. "]=nil;"				-- ATO_FP_Debug02 Interceptor error nb trigger
	mission.trigrules[trig_n] = {
		['rules'] = {
			[1] = {
				["seconds"] = aiStart_spawn_time,
				["predicate"] = "c_time_after",
				["zone"] = "",
			},
		},
		['eventlist'] = '',
		['comment'] = 'Trigger ' .. trig_n,
		['predicate'] = 'triggerOnce',
		['actions'] = {
			[1] = {
				["predicate"] = "a_set_ai_task",
				["set_ai_task"] = {
					[1] = group.groupId,
					[2] = 1,
				}
			},
		},
	}
	--triggered action to start uncontrolled group
	group['tasks'] = {
		[1] = {
			["number"] = 1,
			["name"] = group.name,
			["id"] = "WrappedAction",
			["auto"] = false,
			["enabled"] = true,
			["params"] = {
				["action"] = {
					["id"] = "Start",
					["params"] = {},
				},
			},
		},
	}	
end


--modify_set_ai_task
function modify_set_ai_task(group, AirSpawnTime, from)
	
	if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe 1B modify_set_ai_task "..tostring(from)) end	
	
	-- group['uncontrolled'] = true
	-- group['lateActivation'] = true --incompatible avec l'activation sur sixpack

	for trig_n = 1, #mission.trigrules  do
	
		if mission.trigrules[trig_n] and mission.trigrules[trig_n].actions and mission.trigrules[trig_n].actions[1] then
					-- [25] = {
						-- ['rules'] = {
							-- [1] = {
								-- ['seconds'] = 2436.739371505,
								-- ['predicate'] = 'c_time_after',
								-- ['zone'] = '',
							-- },
						-- },
						-- ['eventlist'] = '',
						-- ['actions'] = {
							-- [1] = {
								-- ['predicate'] = 'a_set_ai_task',
								-- ['set_ai_task'] = {
									-- [1] = 100054,
									-- [2] = 1,
								-- },
							-- },
						-- },
						-- ['predicate'] = 'triggerOnce',
						-- ['comment'] = 'Trigger 25',
					-- },
					
			if  mission.trigrules[trig_n].actions[1].predicate and  mission.trigrules[trig_n].actions[1].predicate ==  "a_set_ai_task" 	
				and mission.trigrules[trig_n].actions[1].set_ai_task[1] == group.groupId then
				
				if AirSpawnTime == -1 then
					AirSpawnTime = 0
				end
				
					-- table.remove(mission.trigrules, trig_n)
					-- table.remove(mission.trig.conditions, trig_n)
					-- table.remove(mission.trig.actions, trig_n)
					-- if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe 1D delete_modify_set_ai_task find groupId "..group.groupId.." trig_n: "..tostring(trig_n)) end
				
				-- else
					mission.trigrules[trig_n].rules[1].seconds = AirSpawnTime			
					
					-- conditions[44] = 'return(c_time_after(2233.512158504) )',
					mission.trig.conditions[trig_n] = "return(c_time_after(" .. AirSpawnTime .. ") )"
					if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe 1Dd modify_set_ai_task find groupId "..group.groupId.." trig_n: "..tostring(trig_n)) end
				-- end
				
				
			end
		end
	end
end		


placePA = {}
TimingDeckCata = {}
testSixPack = {}
freqFM = {
	["red"] = 0,
	["blue"] = 0,
}		
			
---- table to store departure altitudes and times and all airbases to deconflict spawns and orbits ----
local DepartureOrbitAlt = {}	
Missionfunc = 0														--remplace #mission.trig.func qui ne commence plus à 0, donc impossible avec #

local NbFlightPackage = 0													-- calcul le nombre de flight dans un Package, en comptant ceux des Roles
local NbFlightPlayer = 2 													-- nb d'avion dans le flight du joueur	
local NbPlanetDeck = 0														-- nb d'avion total sur la plateform
local basePlayer = ""
-- Cherche le nb d'avion dans le package joueur
for side, pack in pairs(ATO) do	
	for p = 1, #pack do															--iterate through packages in sides
		if camp.player and camp.player.side == side and camp.player.pack_n == p then			
			for role,flight in pairs(pack[p]) do									--iterate through roles in package (main, SEAD, escort)		
				for f = 1, #flight do												--iterate through flights in roles				
					if flight[f].player then
						basePlayer = flight[f].base
					end	

					for role2,flight2 in pairs(pack[p]) do							-- calcul le nombre de flight dans un Package, en comptant ceux des Roles																									
						for x = 1, #flight2 do
							if flight2[x].player then
								NbFlightPlayer = #flight2								
								NbPlanetDeck = flight2[x].number
							elseif flight2[x].client then
								NbFlightPlayer = #flight2								
								NbPlanetDeck = flight2[x].number
							end					
						end
					end
				end
			end
		
			for role,flight in pairs(pack[p]) do									--iterate through roles in package (main, SEAD, escort)		
				for f = 1, #flight do												--iterate through flights in roles									
					if flight[f].base == basePlayer then
						NbFlightPackage = NbFlightPackage + 1
					end
				end
			end		
		end
	end
end


local mn_StartParking = 10 																		-- 10mn de temps de presence sur parking

-- Assigne le temp d occupation parking du joueur, pour manager le parking avion
for side, pack in pairs(ATO) do	
	for p = 1, #pack do	
		if camp.player and camp.player.side == side and camp.player.pack_n == p then			
			for role,flight in pairs(pack[p]) do	
				for f = 1, #flight do			
					if flight[f].player then
						
						if flight[f].player or flight[f].client then
							mn_StartParking = math.floor(mission_ini.startup_time_player / 60)	-- si joueur, le tps d occupation est égal à celui du confMod
							
							if db_airbases[flight[f].base].LimitedParkNb then
								-- db_airbases[flight[f].base].LimitedParkNb = db_airbases[flight[f].base].LimitedParkNb - flight[f].number
							end
						end	
					
					end	
				end
			end	
		end
	end
end

-- print("")
-- print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
-- print("")

local tabDivert = {}														-- Miguel21 modification M33.c 	Custom Briefing (onBoardNum)	
TabLPark	= {}
local PlayerTask = ""		
local tempBaseAirStart = {}
local tempDeckPlace = {}
local testDeckPlace = {}
----- create flight plans in mission file for all flights in ATO -----
for side, pack in pairs(ATO) do													--iterate through sides in ATO
	

	--M27 Randomly moves the 2 BullsEye
	local NameTheatre =  string.lower(mission.theatre)
	if campMod.MovedBullseye[NameTheatre] then	fct_MovedBullseye(side, NameTheatre) end
	
	for p = 1, #pack do															--iterate through packages in sides
		
		local Pn = 0															--variable to count flights in package
		
		for role,flight in pairs(pack[p]) do									--iterate through roles in package (main, SEAD, escort)		
			for f = 1, #flight do												--iterate through flights in roles
				
				if flight[f].player or flight[f].player	then
					PlayerTask = flight[f].task
				end
				
				-- Miguel21 modification M18.c despawn/destroy Plane on BaseAirStart
				if db_airbases[flight[f].base].BaseAirStart then
					if not tempBaseAirStart[flight[f].base] then
						tempBaseAirStart[flight[f].base] = db_airbases[flight[f].base]					
					end
				end
				
				
				
				local LimitedParkTiming = false
				-- modification Miguel21 M03 Apparition décalé sur PA, LHA et FARP
				
				local PlayerFirstParking = false

				if not TabLPark[flight[f].base] then TabLPark[flight[f].base] = {} end
				if not TabLPark[flight[f].base]["NbPlaneTot"] then TabLPark[flight[f].base]["NbPlaneTot"] = 0 end

				--M03.k : (k: best check) (j: check place parking dispo en fonction des minutes)(i: Parking limite little base)
				local timmingParking = math.floor(flight[f].route[1].eta / 60 )
				
				if  not db_airbases[flight[f].base].LimitedParkNb then
					TabLPark[flight[f].base][timmingParking] = 0
				end
				-- if  db_airbases[flight[f].base].LimitedParkNb then
					-- TabLPark[flight[f].base][NbPlaneTot] = 0
				-- end
				-- --si c'est un intercepteur sur piste dur, on bloque sa place en enlevant une place de LimitedParkNb
				-- if flight[f].route[w].id == "Intercept" and flight[f].route[1].eta and not db_airbases[flight[f].base].unitname then
					-- if  db_airbases[flight[f].base].LimitedParkNb then
						-- db_airbases[flight[f].base].LimitedParkNb = db_airbases[flight[f].base].LimitedParkNb - flight[f].number
					-- end
				-- end


				-- LimitedParkTiming  limite par timming l'apparition des avions
				--TabLPark[flight[f].base][NbPlaneTot] limite l'apparition des avions si cela depasse le total, cela permet d'afficher plus d'avion avec lateActivation = false
				if (flight[f].route[1].id ~= "Spawn" and flight[f].route[1].eta and flight[f].route[2]) or (flight[f].route[1].id ~= "Spawn" and flight[f].route[1].eta and not db_airbases[flight[f].base].unitname) then										
					
					for i = timmingParking - mn_StartParking, timmingParking  do						
						if not TabLPark[flight[f].base][i] then TabLPark[flight[f].base][i] = 0 end
						TabLPark[flight[f].base][i] = TabLPark[flight[f].base][i] + flight[f].number
					end

					if (db_airbases[flight[f].base].LimitedParkNb and TabLPark[flight[f].base][timmingParking]  )    then						 --or TabLPark[flight[f].base].flag										
						
						TabLPark[flight[f].base]["NbPlaneTot"] = TabLPark[flight[f].base]["NbPlaneTot"] + flight[f].number
						
						for i = timmingParking - mn_StartParking, timmingParking  do							
							-- print("AtoFP LimitedParkTiming 00 i: "..i)
							-- print("AtoFP LimitedParkTiming 01 "..tostring(TabLPark[flight[f].base][i] ).." >? "..db_airbases[flight[f].base].LimitedParkNb)
							if   TabLPark[flight[f].base][i] > db_airbases[flight[f].base].LimitedParkNb  then  								
								LimitedParkTiming = true
								-- print("AtoFP LimitedParkTiming 01a "..tostring(LimitedParkTiming))														
							elseif    string.find(flight[f].base,"FARP") and camp.player and TabLPark[flight[f].base][i] > (db_airbases[flight[f].base].LimitedParkNb - 4) and (flight[f].base == camp.player.airbase) and (not flight[f].player and not flight[f].client)  then  								
								-- le helico sur le FARP du joueur spawn en l'air
								LimitedParkTiming = true
								PlayerFirstParking = true			-- Helico FARP
								-- print("AtoFP LimitedParkTiming 01b "..tostring(LimitedParkTiming))
							end	
						end
						
												
						--si c'est un intercepteur sur piste dur, on bloque sa place en enlevant une place de LimitedParkNb
						if flight[f].task == "Intercept"  and not db_airbases[flight[f].base].unitname then
							if  db_airbases[flight[f].base].LimitedParkNb then
								db_airbases[flight[f].base].LimitedParkNb = db_airbases[flight[f].base].LimitedParkNb - flight[f].number
								-- print("AtoFP LimitedParkTiming passe LimitedParkNb - flight[f].number "..tostring(db_airbases[flight[f].base].LimitedParkNb))	
							end
						end
					end				
				end

-- if db_airbases[flight[f].base].LimitedParkNb then 
	-- print("AtoFP LimitedParkNb 01b "..flight[f].base.." "..db_airbases[flight[f].base].LimitedParkNb)
	
-- end
-- print("AtoFP LimitedParkTiming 02 "..flight[f].base.." : "..tostring(LimitedParkTiming))

				NavTargetPoints = {}
				flagPoints = {}
				index = 0
				removeWptF14 = {}
				
				local activG_spawn_time = 0
				local aiStart_spawn_time = 0
								
				Pn = Pn + 1														--count flights in package
				
				local weaponType = 1073741822																			--Weapon types to use (default auto)
				if flight[f].loadout.weaponType == "Cannon" then
					weaponType = 805306368																				--Use cannon only
				elseif flight[f].loadout.weaponType == "Rockets" then
					weaponType = 30720																					--Use rockets only
				elseif flight[f].loadout.weaponType == "Bombs" then
					weaponType = 2032																					--Use unguided bombs only
				elseif flight[f].loadout.weaponType == "Guided bombs" then
					weaponType = 14																						--Use guided bombs only
				elseif flight[f].loadout.weaponType == "ASM" then
					weaponType = 4161536																				--Use ASM only
				end
				
				----- define waypoints -----
				local egress_wp													--local variable to store the Egress WP
				local target_wp_remove											--local variable for the target waypoint to be potentially removed for standoff ground attacks
				local spawn_time												--local variable to store spawn time
				local departure_time											--local variable to store departure time
				local waypoints = {}											--define waypoints of flight
				
				for w = 1, #flight[f].route do

					waypoints[w] = {
						["name"] = flight[f].route[w].id,
						["briefing_name"] = flight[f].route[w].id,				--not needed for actual mission creation, but added for navigation overview in briefing
						["alt"] = flight[f].route[w].alt,
						["type"] = "Turning Point",
						["action"] = "Turning Point",
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
						["ETA"] = flight[f].route[w].eta,
						["y"] = flight[f].route[w].y,
						["x"] = flight[f].route[w].x,
						["speed"] = pack[p].main[1].loadout.vCruise,
						["ETA_locked"] = true,
						["task"] = 
						{
							["id"] = "ComboTask",
							["params"] = 
							{
								["tasks"] = {}
							},
						},
						["speed_locked"] = false,
					}
					
					if 	flight[f].loadout.vCruise and waypoints[w]["speed"] < flight[f].loadout.vCruise / 4 * 3 then
						waypoints[w]["speed"] = flight[f].loadout.vCruise / 4 * 3 +1
					end
					
					--Eagle_01 Modification E01.d
					-- if flight[f].helicopter and flight[f].airdromeId >= 100 then					
						-- if  w == 1  then	 	
								-- waypoints[w]["helipadId"] = flight[f].airdromeId
								-- -- E01.c attention, cette ligne enleve les helico du Tarawa
								-- -- flight[f].airdromeId = nil
								-- waypoints[w]["airdromeId"] = flight[f].airdromeId
						-- elseif  flight[f].route[w].id == "Land"  then	 	
								-- waypoints[w]["helipadId"] = flight[f].airdromeId
								-- waypoints[w]["airdromeId"] = flight[f].airdromeId
						-- end						
					-- end
					
					-- Miguel21 modification M17.e
					if flight[f].type == "F-14B" and ( flight[f].player ) and TargetPointF14 then		--or Multi.NbGroup >= 1 
						if  flight[f].route[w].id == "Target" or flight[f].route[w].id == "Attack" and not flagPoints["ST"] then
							index = index +1
							if not NavTargetPoints[index] then NavTargetPoints[index] = {} end
							NavTargetPoints[index]["text_comment"]  = "ST"
							NavTargetPoints[index]["x"] = flight[f].route[w].x
							NavTargetPoints[index]["y"] = flight[f].route[w].y
							NavTargetPoints[index]["index"] = index
							flagPoints["ST"] = true
							table.insert(removeWptF14, w)
						
						elseif flight[f].route[w].id == "IP" and not flagPoints["IP"] then
							index = index +1
							if not NavTargetPoints[index] then NavTargetPoints[index] = {} end
							NavTargetPoints[index]["text_comment"]  = "IP"
							NavTargetPoints[index]["x"] = flight[f].route[w].x
							NavTargetPoints[index]["y"] = flight[f].route[w].y
							NavTargetPoints[index]["index"] = index
							flagPoints["IP"] = true
							table.insert(removeWptF14, w)
							
						 elseif flight[f].route[w].id == "Station"  then --and not flagPoints["DP"]
							index = index +1
							if not NavTargetPoints[index] then NavTargetPoints[index] = {} end
							NavTargetPoints[index]["text_comment"]  = "DP"
							NavTargetPoints[index]["x"] = flight[f].route[w].x
							NavTargetPoints[index]["y"] = flight[f].route[w].y
							NavTargetPoints[index]["index"] = index
							-- flagPoints["DP"] = true
							table.insert(removeWptF14, w)
						end
						
						if TargetPointF14_BullsToFP and not flagPoints["FP"] then 
							index = index +1
							if not NavTargetPoints[index] then NavTargetPoints[index] = {} end
							NavTargetPoints[index]["text_comment"]  = "FP"
							NavTargetPoints[index]["x"] = mission.coalition[side].bullseye.x
							NavTargetPoints[index]["y"] = mission.coalition[side].bullseye.y
							NavTargetPoints[index]["index"] = index
							flagPoints["FP"] = true
						end

					end
					
					--store spawn and departure time for flight
					if flight[f].route[w].id == "Taxi" or flight[f].route[w].id == "Spawn" then
						spawn_time = flight[f].route[w].eta
					elseif flight[f].route[w].id == "Departure" then
						departure_time = flight[f].route[w].eta
					end
					
					--alter departure alt (spawn and orbit) to prevent collisions of multiple packages
					if flight[f].route[w].id == "Departure" and flight[f].route[w - 1] and flight[f].route[w].id == "Spawn" then							--for departure waypoints that come after spwn waypoints
						waypoints[w]["alt"] = waypoints[w - 1]["alt"]																						--use same altitude as departure as for spawn
					elseif flight[f].route[w].id == "Departure" or (flight[f].route[w].id == "Spawn" and flight[f].route[w + 1].id == "Departure") then		--for departure waypoint or spawn before departure waypoint
						local alt = 609.6														--initial departure alt to try: 2'000 ft
						if flight[f].helicopter  then 											-- M6.1 sauf helicopter
							alt = 150
						end
						if db_airbases[flight[f].base].elevation then							--airbase has defined elevation
							alt = alt + db_airbases[flight[f].base].elevation					--make alt above base
						end
						if DepartureOrbitAlt[flight[f].base] == nil then						--airbase has no departure altitute entries yet
							DepartureOrbitAlt[flight[f].base] = {								--make base table
								[alt] = {														--make altitude table
									[1] = waypoints[w]["ETA"],									--store time of departure
								}
							}
							waypoints[w]["alt"] = alt											--set departure altitude
						else																	--airbase has departure altitute entries
							local DepartureAlt
							repeat
								if DepartureOrbitAlt[flight[f].base][alt] == nil then			--no altitude entries yet			
									DepartureOrbitAlt[flight[f].base][alt] = {					--make altitude table
										[1] = waypoints[w]["ETA"],								--store time of departure
									}
									DepartureAlt = alt											--set departure altitude
								else															--there are already altitude entries for this airbase
									for a = 1, #DepartureOrbitAlt[flight[f].base][alt] do		--iterate through all entries of that alt
										if waypoints[w]["ETA"] > DepartureOrbitAlt[flight[f].base][alt][a] - 600 and waypoints[w]["ETA"] < DepartureOrbitAlt[flight[f].base][alt][a] + 600 then		--waypoint ETA is within 10 minutes of stored ETA 
											alt = alt + 304.8									--increase alt by 1'000 ft any try again for this next alt
											break												--break and continue with higher altitude
										end
										if a == #DepartureOrbitAlt[flight[f].base][alt] then	--if all stored ETAs have been checked
											table.insert(DepartureOrbitAlt[flight[f].base][alt], waypoints[w]["ETA"])	--insert new ETA for that altitude
											DepartureAlt = alt									--set this departure altitude
										end
									end
								end
							until DepartureAlt													--repeat until a departure altitude has been found
							waypoints[w]["alt"] = DepartureAlt									--set departure altitude
						end
					end
					
					--set attack speed for attack, target and egress waypoints
					if waypoints[w]["name"] == "Attack" or waypoints[w]["name"] == "Target" or waypoints[w]["name"] == "Egress" then
						waypoints[w]["ETA_locked"] = false
						waypoints[w]["speed_locked"] = true
						waypoints[w]["speed"] = pack[p].main[1].loadout.vAttack
					elseif waypoints[w]["name"] == "Join"  then		
						-- waypoints[w]["ETA_locked"] = false
						-- waypoints[w]["speed_locked"] = true
						-- ATO_FP_Reglage02 : ATO_lock sur les xpt Join
						waypoints[w]["ETA_locked"] = true
						waypoints[w]["speed_locked"] = false
						
						-- if not flight[f].helicopter then												-- M06.e not flight[f].helicopter
							waypoints[w]["speed"] = pack[p].main[1].loadout.vCruise / 4 * 3
						-- else
							-- waypoints[w]["speed"] = pack[p].main[1].loadout.vCruise 
						-- end
						
					elseif waypoints[w]["name"] == "Departure"  then
						-- if not flight[f].helicopter then												-- M06.e not flight[f].helicopter
							waypoints[w]["speed"] = pack[p].main[1].loadout.vCruise / 4 * 3
						-- else
							-- waypoints[w]["speed"] = pack[p].main[1].loadout.vCruise 
						-- end
					end
						
					-- ATO_FP_Debug08 vi trop faible pour les escorteurs des strike trop lent 					
					if 	flight[f].loadout.vCruise and waypoints[w]["speed"] < flight[f].loadout.vCruise / 4 * 3 then					
						waypoints[w]["speed"] = flight[f].loadout.vCruise / 4 * 3								
							
						-- if w < #flight[f].route then								
							-- print("AtoFP passe 02 w "..w)							
							-- local grpname = "Pack " .. p .. " - " .. flight[f].name .. " - " .. flight[f].task .. " " .. f
							-- local task_entry = {	
								-- ["enabled"] = true,
								-- ["auto"] = false,
								-- ["id"] = "WrappedAction",
								-- ["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								-- ["params"] = 
								-- {
									-- ["action"] = 
									-- {
										-- ["id"] = "Script",
										-- ["params"] = 
										-- {
											-- ["command"] = 'OrbitPosition("' .. grpname .. '", ' .. waypoints[w]["alt"] .. ', ' .. flight[f].loadout.vCruise / 3 * 2 .. ', ' .. waypoints[w].ETA .. ')',
										-- },
									-- },
								-- },
							-- }
							-- table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
						-- end																	
					end	
						
					--attack waypoint is a fly over point
					if waypoints[w]["name"] == "Attack" then
						waypoints[w]["action"] = "Fly Over Point"
					end
					
					if waypoints[w]["name"] == "IP" and flight[f].task == "Escort" then
						
						local grpname = "Pack " .. p .. " - " .. flight[f].name .. " - " .. flight[f].task .. " " .. f
						local task_entry = {	
							["enabled"] = true,
							["auto"] = false,
							["id"] = "WrappedAction",
							["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
							["params"] = 
							{
								["action"] = 
								{
									["id"] = "Script",
									["params"] = 
									{
										["command"] = 'OrbitPosition("' .. grpname .. '", ' .. waypoints[w]["alt"] .. ', ' .. flight[f].loadout.vCruise  / 4 * 3 .. ', ' .. (waypoints[w].ETA + 120) .. ')',
									},
								},
							},
						}
						table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
						-- local target = "Battle airplanes"
						-- -- local target = "Air"
						-- local task_entry = {	
							-- ["enabled"] = true,
							-- ["auto"] = false,
							-- ["id"] = "WrappedAction",
							-- ["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
							-- ["params"] = 
							-- {
								-- ["action"] = 
								-- {
									-- ["id"] = "Script",
									-- ["params"] = 
									-- {
										-- ["command"] = 'CustomSearchThenEngage("' .. grpname .. '", ' .. (flight[f].loadout.standoff/2) .. ', "'..target..'")',
									-- },
								-- },
							-- },
						-- }
						-- table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
							
					end
					
					--fighter escorts fly with cruise speed to egress
					if waypoints[w]["name"] == "Egress" and flight[f].task == "Escort" then
						waypoints[w]["speed"] = pack[p].main[1].loadout.vCruise
						if 	flight[f].loadout.vCruise and waypoints[w]["speed"] < flight[f].loadout.vCruise / 4 * 3 then					
							waypoints[w]["speed"] = flight[f].loadout.vCruise / 4 * 3		
						end						
					end
					
					---- ATO_FP_Debug05 Escorte
					-- --set speed locked for all WP after Egress or Station
					-- if flight[f].route[w].id == "Egress" or flight[f].route[w].id == "Station" and egress_wp == nil then	--find Egress or first Station WP
						-- egress_wp = w																						--store tgt wp number
					-- end
					-- if egress_wp and w > egress_wp then																		--for all WP after target or first station WP
						-- waypoints[w]["ETA_locked"] = false
						-- waypoints[w]["speed_locked"] = true
					-- end
					
					-- --set speed locked for all WPs after Join. TOT would be better for waypoints to coordinate flights in package, but when AI is unable to meet TOT due to delays it continues at stall speed. Due to this bug, folllowing workaround is required
					-- if flight[f].route[w].id ~= "Taxi" and flight[f].route[w].id ~= "Departure" and flight[f].route[w].id ~= "Join" and flight[f].route[w].id ~= "Spawn" then
						-- waypoints[w]["ETA_locked"] = false
						-- waypoints[w]["speed_locked"] = true
					-- end
					-- --end workaround
					
					--player flight WP ETA
					if flight[f].player then
						if waypoints[w]["name"] == "Target" or waypoints[w]["name"] == "Station" then
							waypoints[w]["ETA_locked"] = true
							waypoints[w]["speed_locked"] = false
						elseif waypoints[w]["name"] == "Join" then															--ETA of join should be unlocked (so it is no target point for Viggen), but speed needs to be reduced to allow time for start up and take off
							waypoints[w]["ETA_locked"] = false
							waypoints[w]["speed_locked"] = true
							waypoints[w]["speed"] = GetDistance(waypoints[w - 1], waypoints[w]) / (waypoints[w]["ETA"] - waypoints[w-1]["ETA"])		--exact speed to rach join at required ETA
						else
							waypoints[w]["ETA_locked"] = false
							waypoints[w]["speed_locked"] = true
						end
					end
					
					-- modification M06.b bug helico reste statique s'il demarre en horaire décalé
					-- M06.e
					if flight[f].helicopter == true   and flight[f].route[w].id ~= "Departure" then	 --and flight[f].task == "Transport"	
							waypoints[w]["ETA_locked"] = false
							waypoints[w]["speed_locked"] = true
					end
					
					--altitudes below 1000m are AGL instead of MSL
					if waypoints[w]["alt"] <= 1000 then
						waypoints[w]["alt_type"] = "RADIO"
					end
					
					--take off and landing
					if (flight[f].route[w].id == "Taxi" and flight[f].route[w].eta >= 0) or flight[f].route[w].id == "Intercept"  then							
						if  ( not flight[f].player and not flight[f].client) and db_airbases[flight[f].base].AI_Spawn and string.upper(db_airbases[flight[f].base].AI_Spawn) ~= "PARKING" then
							if string.upper(db_airbases[flight[f].base].AI_Spawn) == "AIR" then																
								waypoints[w]["type"] = "Turning Point"
								waypoints[w]["action"] = "Turning Point"
								flight[f].route[w].id = "Spawn"
								flight[f].route[w].eta = flight[f].route[w].eta - 300
								spawn_time = flight[f].route[w].eta							
							elseif string.upper(db_airbases[flight[f].base].AI_Spawn) == "RUNWAY" then								
								waypoints[w]["type"] = "Turning TakeOff"
								waypoints[w]["action"] = "From Runway"
								flight[f].route[w].eta = flight[f].route[w].eta - 200
								spawn_time = flight[f].route[w].eta										
							end											
						else
							waypoints[w]["type"] = "TakeOffParking"
							waypoints[w]["action"] = "From Parking Area"
							if db_airbases[flight[f].base].unitname or (flight[f].airdromeId and flight[f].airdromeId >= 100) then									--airbase is a carrier
								waypoints[w]["linkUnit"] = flight[f].airdromeId
								waypoints[w]["helipadId"] = flight[f].airdromeId
							else
								waypoints[w]["airdromeId"] = flight[f].airdromeId
							end
							
							--if defined in conf_mod, player flight starts with engines running
							if flight[f].player == true and mission_ini.parking_hotstart then											--if flight[f].player == true and camp.hotstart then
								waypoints[w]["action"] = "From Parking Area Hot"
								waypoints[w]["type"] = "TakeOffParkingHot"
							--if defined in conf_mod, task intercept player flight starts with engines running							-- Miguel21 modification M08	: hotstart
							elseif flight[f].player == true and mission_ini.intercept_hotstart and flight[f].task == "Intercept" then	--if flight[f].player == true and camp.hotstart then
								waypoints[w]["action"] = "From Parking Area Hot"
								waypoints[w]["type"] = "TakeOffParkingHot"
							end
						end
					elseif flight[f].route[w].id == "Land" then
						-- Miguel21 modification M18.c despawn/destroy Plane on BaseAirStart
						if db_airbases[flight[f].base].BaseAirStart then								
							waypoints[w]["type"] = "Turning Point"
							waypoints[w]["action"] = "Turning Point"
							waypoints[w]["speed"] = flight[f].loadout.vCruise / 3 * 2
							waypoints[w]["alt"] = 500 + db_airbases[flight[f].base].elevation	
							waypoints[w].ETA_locked = false
							waypoints[w].speed_locked = true
							
							local stopTime = waypoints[w].ETA + 7200
							
							
								
							local grpname = "Pack " .. p .. " - " .. flight[f].name .. " - " .. flight[f].task .. " " .. f
							local task_entry = {	
								["enabled"] = true,
								["auto"] = false,
								["id"] = "WrappedAction",
								["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								["params"] = 
								{
									["action"] = 
									{
										["id"] = "Script",
										["params"] = 
										{
											["command"] = 'OrbitPosition("' .. grpname .. '", ' .. waypoints[w]["alt"] .. ', ' .. waypoints[w]["speed"] .. ', ' .. stopTime .. ')',
										},
									},
								},
							}
							table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
							
						else	
							waypoints[w]["type"] = "Land"
							waypoints[w]["action"] = "Landing"
							if db_airbases[flight[f].base].unitname then
								waypoints[w]["linkUnit"] = flight[f].airdromeId
								waypoints[w]["helipadId"] = flight[f].airdromeId
							else
								waypoints[w]["airdromeId"] = flight[f].airdromeId
								if flight[f].task == "Nothing" then
									waypoints[w]["airdromeId"] = db_airbases[flight[f].target.destination].airdromeId
								end
							end
							
							--TODO ajouter un wpt intermediaire avec customOrbit
							if db_airbases[flight[f].base].unitname and waypoints[w]["ETA"] <= mission_ini.startup_time_player + 600 then
								if debugStart then debugTxt = debugTxt.."\n"..("AtoFP delayed LANDING ") end
								
								local grpname = "Pack " .. p .. " - " .. flight[f].name .. " - " .. flight[f].task .. " " .. f
						
								local distOrbit  = GetDistance({x = waypoints[w-1].x, y = waypoints[w-1].y}, {x = waypoints[w].x, y = waypoints[w].y})
								
								local HeadingOrbit  = GetHeading({x = waypoints[w-1].x, y = waypoints[w-1].y}, {x = waypoints[w].x, y = waypoints[w].y})
								
								local pointOrbit = GetOffsetPoint({x = waypoints[w-1].x, y = waypoints[w-1].y}, HeadingOrbit, distOrbit)
								
								local ETA_orbit = (waypoints[w-1]["ETA"] + waypoints[w]["ETA"]) / 2
								
								local departure_time = mission_ini.startup_time_player + 600
								
								waypoints[w]["ETA"] = mission_ini.startup_time_player + 1200
								
								--ajoute un waypoint intermediaire avec une orbit
								local wptOrbit = {
									['alt'] = waypoints[w-1]["alt"],
									['briefing_name'] = 'Stacking',
									['action'] = 'Turning Point',
									['alt_type'] = 'BARO',
									['speed_locked'] = false,
									['ETA'] = ETA_orbit,
									['y'] = pointOrbit.y,
									['formation_template'] = '',
									['name'] = 'Stacking',
									['ETA_locked'] = true,
									['speed'] = waypoints[w-1]["speed"],
									['x'] = pointOrbit.x,
									['task'] = {
										['id'] = 'ComboTask',
										['params'] = {
											['tasks'] = {
												[1] = {
													["enabled"] = true,
													["auto"] = false,
													["id"] = "WrappedAction",
													["number"] =  1,
													["params"] = 
													{
														["action"] = 
														{
															["id"] = "Script",
															["params"] = 
															{
																["command"] = 'OrbitPosition("' .. grpname .. '", ' .. waypoints[w-1]["alt"] .. ', ' .. waypoints[w-1]["speed"] .. ', ' .. departure_time .. ')',
															},
														},
													},
												},
											},
										},
									},
									['type'] = 'Turning Point',
								
								}
								
								table.insert(waypoints, w, wptOrbit )
								
							end
						end
						
					end				
					
					--target WP to be removed for non-player A-G attacks
					if flight[f].route[w].id == "Target" then											--WP is target WP
						if flight[f].task ~= "Reconnaissance" and flight[f].task ~= "Laser Illumination" then		--target WP is removed for all A-G tasks except recon or laser illumination
							if flight[f].player ~= true and flight[f].client ~= true then											--not the player flight (player always gets a target WP)
								target_wp_remove = w
							end
						end
					end
					
					--formations
					if flight[f].route[w].id == "Departure" or flight[f].route[w].id == "Spawn" then
						local task_entry = {															--Spread Four Close
							["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
							["auto"] = false,
							["id"] = "WrappedAction",
							["enabled"] = true,
							["params"] = 
							{
								["action"] = 
								{
									["id"] = "Option",
									["params"] = 
									{
										["variantIndex"] = 1,
										["name"] = 5,
										["formationIndex"] = 7,
										["value"] = 458753,
									},
								},
							},
						}
						table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
					end
					
					--ATO_FP_Reglage01 : emport, ne pas larguer les emports en cas d'urgence
					-- if flight[f].route[w].id == "Departure" or flight[f].route[w].id == "Spawn" then
						-- local task_entry = {
							-- ["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
							-- ["enabled"] = true,
							-- ["auto"] = false,
							-- ["id"] = "WrappedAction",
							-- ["params"] = 
							-- {
								-- ["action"] = 
								-- {
									-- ["id"] = "Option",
									-- ["params"] = 
									-- {
										-- ["value"] = true,
										-- ["name"] = 15,
									-- }, -- end of ["params"]
								-- }, -- end of ["action"]
							-- }, -- end of ["params"],
						-- }
						-- table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
					-- end


					-- modif Miguel M01 : ajout datalink EPLRS Capacity
					if (flight[f].route[w].id == "Departure"  or flight[f].route[w].id == "Spawn") and camp.date.year >= 1996 then
						if flight[f].type == "E-2C" or flight[f].type == "E-3A" or flight[f].type == "F-15C" or flight[f].type == "F-15E" or flight[f].type == "F-16C bl.52d"or flight[f].type == "FA-18C_hornet" or flight[f].type == "F/A-18C" then
							local task_entry = {
								["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								["auto"] = true,
								["id"] = "WrappedAction",
								["enabled"] = true,
								["params"] =
								{
									["action"] =
									{
										["id"] = "EPLRS",
										["params"] =
										{
											["value"] = true,
											["groupId"] = 1,
										}, -- end of ["params"]
									}, -- end of ["action"]
								},
							}
							table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
							end
						end
					
					--attack tasks
					if (flight[f].player == true and flight[f].route[w].id == "IP") or flight[f].route[w].id == "Attack" then	--Attack waypoint for AI or IP for player
						if flight[f].task == "Strike" and flight[f].target.class == nil then									--Tasks against scenery objects with multiple target sub-elements
							
							local target_element = {}																			--table to hold the target element number to be struck
							for e = 1, #flight[f].target.elements do															--iterate trough all target elements
								if flight[f].target.elements[e].dead ~= true then												--pick only elements that are not dead
									table.insert(target_element, e)																--add to target element table
								end
							end
							for n = 1, (f - 1) * 4 do																			--shift the order of target elements for subsequent flights in package, so that each flights starts attacking different elements (flight 1: element 1-4, flight 2: element 5-8, etc)
								table.insert(target_element, target_element[1])													--shift element order, copy first element to back
								table.remove(target_element, 1)																	--delete first element
							end
							
							--this is only to display attack markers in mission editor, task will be replaced in game by CustomMapObjectAttack
							-----------------------------------------------------------------------
							for n,e in ipairs(target_element) do
								local task_entry = {
									["enabled"] = false,
									["auto"] = false,
									["id"] = "AttackMapObject",
									["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
									["params"] = {
										["x"] = flight[f].target.elements[e].x,
										["y"] = flight[f].target.elements[e].y,
										["weaponType"] = weaponType,
										["expend"] = flight[f].loadout.expend,
										["direction"] = 0,
										["attackQtyLimit"] = false,
										["attackQty"] = 1,
										["directionEnabled"] = false,
										["groupAttack"] = true,
										["altitude"] = 2000,
										["altitudeEnabled"] = false,
									},
								}
								table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
							end
							-----------------------------------------------------------------------
							
							local grpname = "Pack " .. p .. " - " .. flight[f].name .. " - " .. flight[f].task .. " " .. f
							local expend = flight[f].loadout.expend
							local attackType = flight[f].loadout.attackType or "nil"
							local attackAlt = flight[f].loadout.attackAlt or flight[f].loadout.hAttack
							local tgtlist = ""																					--list of of names of all target elements
							for n,e in ipairs(target_element) do
								tgtlist = tgtlist .. '{ x = ' .. flight[f].target.elements[e].x .. ', y = ' .. flight[f].target.elements[e].y .. '}, '
							end
							
							local task_entry = {																				--task is a command to run LUA code
								["enabled"] = true,
								["auto"] = false,
								["id"] = "WrappedAction",
								["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								["params"] = 
								{
									["action"] = 
									{
										["id"] = "Script",
										["params"] = 
										{
											["command"] = 'CustomMapObjectAttack("' .. grpname .. '", {' .. tgtlist .. '}, "' .. expend .. '", "' .. weaponType .. '", "' .. attackType .. '", ' .. attackAlt .. ')',	--this is a custom written task to allow all aircraft in flight to attack multiple static objects simultenously
										},
									},
								},
							}
							table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
							
						elseif flight[f].task == "Strike" and flight[f].target.class == "vehicle" then
							
							--this is only to display attack markers in mission editor, task will be replaced in game by CustomGroupAttack
							-----------------------------------------------------------------------
							local task_entry = {
								["enabled"] = false,
								["auto"] = false,
								["id"] = "AttackGroup",
								["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								["params"] = 
								{
									["groupId"] = flight[f].target.groupId,
									["weaponType"] = weaponType,
									["expend"] = flight[f].loadout.expend,
									["attackType"] = flight[f].loadout.attackType,
								}
							}
							table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
							-----------------------------------------------------------------------
							
							local grpname = "Pack " .. p .. " - " .. flight[f].name .. " - " .. flight[f].task .. " " .. f
							local expend = flight[f].loadout.expend
							local attackType = flight[f].loadout.attackType or "nil"
							local attackAlt = flight[f].loadout.attackAlt or flight[f].loadout.hAttack
							
							local task_entry = {																				--task is a command to run LUA code
								["enabled"] = true,
								["auto"] = false,
								["id"] = "WrappedAction",
								["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								["params"] = 
								{
									["action"] = 
									{
										["id"] = "Script",
										["params"] = 
										{
											["command"] = 'CustomGroupAttack("' .. grpname .. '", "' .. flight[f].target.name .. '", "' .. expend .. '", "' .. weaponType .. '", "' .. attackType .. '", ' .. attackAlt .. ')',
										},
									},
								},
							}
							table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
							
						elseif flight[f].task == "Strike" and flight[f].target.class == "static" then
							
							local target_element = {}																			--table to hold the target element number to be struck
							for e = 1, #flight[f].target.elements do															--iterate trough all target elements
								if flight[f].target.elements[e].dead ~= true then												--pick only elements that are not dead
									table.insert(target_element, e)																--add to target element table
								end
							end
							for n = 1, (f - 1) * 4 do																			--shift the order of target elements for subsequent flights in package, so that each flights starts attacking different elements (flight 1: element 1-4, flight 2: element 5-8, etc)
								table.insert(target_element, target_element[1])													--shift element order, copy first element to back
								table.remove(target_element, 1)																	--delete first element
							end
							
							--this is only to display attack markers in mission editor, task will be replaced in game by CustomStaticAttack
							-----------------------------------------------------------------------
							for n,e in ipairs(target_element) do
								local task_entry = {
									["enabled"] = false,
									["auto"] = false,
									["id"] = "AttackGroup",
									["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
									["params"] = {
										["groupId"] = flight[f].target.elements[e].groupId,
										["weaponType"] = weaponType,
										["expend"] = flight[f].loadout.expend,
									},
								}
								table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
							end
							-----------------------------------------------------------------------
						
							local grpname = "Pack " .. p .. " - " .. flight[f].name .. " - " .. flight[f].task .. " " .. f
							local expend = flight[f].loadout.expend
							local attackType = flight[f].loadout.attackType or "nil"
							local attackAlt = flight[f].loadout.attackAlt or flight[f].loadout.hAttack
							local tgtlist = ""																					--list of of names of all target elements
							for n,e in ipairs(target_element) do
								tgtlist = tgtlist .. '"' .. flight[f].target.elements[e].name .. '", '
							end
							
							local task_entry = {																				--task is a command to run LUA code
								["enabled"] = true,
								["auto"] = false,
								["id"] = "WrappedAction",
								["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								["params"] = 
								{
									["action"] = 
									{
										["id"] = "Script",
										["params"] = 
										{
											["command"] = 'CustomStaticAttack("' .. grpname .. '", {' .. tgtlist .. '}, "' .. expend .. '", "' .. weaponType .. '", "' .. attackType .. '", ' .. attackAlt .. ')',	--this is a custom written task to allow all aircraft in flight to attack multiple static objects simultenously
										},
									},
								},
							}
							table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
							
						elseif flight[f].task == "Strike" and flight[f].target.class == "airbase" then							
							local grpname = "Pack " .. p .. " - " .. flight[f].name .. " - " .. flight[f].task .. " " .. f
							local expend = flight[f].loadout.expend
							local attackType = flight[f].loadout.attackType or "nil"
							local attackAlt = flight[f].loadout.attackAlt or flight[f].loadout.hAttack
							
							local task_entry = {																				--task is a command to run LUA code
								["enabled"] = true,
								["auto"] = false,
								["id"] = "WrappedAction",
								["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								["params"] = 
								{
									["action"] = 
									{
										["id"] = "Script",
										["params"] = 
										{
											["command"] = 'CustomAirbaseAttack("' .. grpname .. '", {x = ' .. flight[f].target.x .. ', y = ' .. flight[f].target.y .. '}, "' .. expend .. '", "' .. weaponType .. '", "' .. attackType .. '", ' .. attackAlt .. ')',
										},
									},
								},
							}
							table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
							
						elseif flight[f].task == "Anti-ship Strike" then
							
							-- + ATO_FP_Debug03 Antiship strik
							-- --this is only to display attack markers in mission editor, task will be replaced in game by CustomGroupAttack
							-- -----------------------------------------------------------------------
							-- local task_entry = {
								-- ["enabled"] = false,
								-- ["auto"] = false,
								-- ["id"] = "AttackGroup",
								-- ["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								-- ["params"] = 
								-- {
									-- ["groupId"] = flight[f].target.groupId,
									-- ["weaponType"] = weaponType,
									-- ["expend"] = flight[f].loadout.expend,
									-- ["attackType"] = flight[f].loadout.attackType,
								-- }
							-- }
							-- table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
							-- -----------------------------------------------------------------------
							
							-- local grpname = "Pack " .. p .. " - " .. flight[f].name .. " - " .. flight[f].task .. " " .. f
							-- local expend = flight[f].loadout.expend
							-- local attackType = flight[f].loadout.attackType or "nil"
							-- local attackAlt = flight[f].loadout.attackAlt or flight[f].loadout.hAttack
							
							-- local task_entry = {																				--task is a command to run LUA code
								-- ["enabled"] = true,
								-- ["auto"] = false,
								-- ["id"] = "WrappedAction",
								-- ["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								-- ["params"] = 
								-- {
									-- ["action"] = 
									-- {
										-- ["id"] = "Script",
										-- ["params"] = 
										-- {
											-- ["command"] = 'CustomGroupAttack("' .. grpname .. '", "' .. flight[f].target.name .. '", "' .. expend .. '", "' .. weaponType .. '", "' .. attackType .. '", ' .. attackAlt .. ')',
										-- },
									-- },
								-- },
							-- }
					
					
						-- + ATO_FP_Debug03 Antiship strike

							local task_entry = {															--Spread Four Close
								["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								["enabled"] = true,
								["key"] = "AntiShip",
								["id"] = "EngageTargets",
								["auto"] = true,
								["params"] = 
								{
									["targetTypes"] = 
									{
										[1] = "Ships",
									}, -- end of ["targetTypes"]
									["priority"] = 0,
								}, -- end of ["params"]

							}
							table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)

							-- + ATO_FP_Debug03 Antiship strike
							local task_entry = {
								["enabled"] = true,
								["auto"] = false,
								["id"] = "AttackGroup",
								["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								["params"] = 
								{
									["groupId"] = flight[f].target.groupId,
									["weaponType"] = weaponType,
									["expend"] = flight[f].loadout.expend,
									["attackType"] = flight[f].loadout.attackType,
								}
							}
							
							
							table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
							
						elseif flight[f].task == "Flare Illumination" then
							
							--this is only to display attack markers in mission editor, task will be replaced in game by CustomFlareAttack
							-----------------------------------------------------------------------
							local task_entry = {
								["enabled"] = false,
								["auto"] = false,
								["id"] = "Bombing",
								["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								["params"] = {
									["x"] = flight[f].target.x,
									["y"] = flight[f].target.y,
									["direction"] = 0,
									["attackQtyLimit"] = false,
									["attackQty"] = 1,
									["expend"] = flight[f].loadout.expend,
									["altitude"] = 1524,
									["directionEnabled"] = false,
									["groupAttack"] = true,
									["altitudeEdited"] = true,
									["altitudeEnabled"] = true,
									["weaponType"] = weaponType,
								},
							}
							table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
							-----------------------------------------------------------------------
						
							local grpname = "Pack " .. p .. " - " .. flight[f].name .. " - " .. flight[f].task .. " " .. f
							local expend = flight[f].loadout.expend
							local attackType = flight[f].loadout.attackType or "nil"
							local attackAlt = flight[f].loadout.attackAlt or flight[f].loadout.hAttack
							local tgtx = "n/a"																					--target coordinate n/a, custom attach script will determine latest target position at time of attack during the misssion
							local tgty = "n/a"																					--target coordinate n/a, custom attach script will determine latest target position at time of attack during the misssion
							if flight[f].target.class ~= "vehicle" then															--if target is not a vehicle or ship, then known target coordinates are used
								tgtx = flight[f].target.x																		--use known target coordinates
								tgty = flight[f].target.y																		--use known target coordinates
							end
							
							local task_entry = {																				--task is a command to run LUA code
								["enabled"] = true,
								["auto"] = false,
								["id"] = "WrappedAction",
								["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								["params"] = 
								{
									["action"] = 
									{
										["id"] = "Script",
										["params"] = 
										{
											["command"] = 'CustomFlareAttack("' .. grpname .. '", "' .. tgtx .. '", "' .. tgty .. '", "' .. flight[f].target.name .. '", "' .. expend .. '", "' .. weaponType .. '", "' .. attackType .. '", ' .. attackAlt .. ')',	--this is a custom written task to allow coordinates bombing of target poistion at time of attack
										},
									},
								},
							}
							table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
						
						elseif flight[f].task == "Laser Illumination" then
							local grpname = "Pack " .. p .. " - " .. flight[f].name .. " - " .. flight[f].task .. " " .. f
							local LaserCode1 = math.random(1,8)
							local LaserCode2 = math.random(1,8)
							local LaserCode3 = math.random(1,8)
							flight[f].target.LaserCode = tonumber("1" .. LaserCode1 .. LaserCode2 .. LaserCode3)				--store laser code for flight target
							for ff = 1, #pack[p].main do																		--iterate through all main body flights
								pack[p].main[ff].target.LaserCode = tonumber("1" .. LaserCode1 .. LaserCode2 .. LaserCode3)		--store laser code in all main body flights
							end
							
							local tgt = ""
							local class
							if flight[f].target.class == "static" then
								class = "static"
								for e = 1, #flight[f].target.elements do
									tgt = tgt .. '"' .. flight[f].target.elements[e].name .. '", '
								end
							elseif flight[f].target.class == "vehicle" then
								class = "vehicle"
								tgt = flight[f].target.name
							elseif flight[f].target.class == "airbase" then
							
							else
								class = "scenery"
								for e = 1, #flight[f].target.elements do
									tgt = tgt .. '{ x = ' .. flight[f].target.elements[e].x .. ', y = ' .. flight[f].target.elements[e].y .. '}, '
								end
							end
							
							local task_entry = {																				--task is a command to run LUA code
								["enabled"] = true,
								["auto"] = false,
								["id"] = "WrappedAction",
								["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								["params"] = 
								{
									["action"] = 
									{
										["id"] = "Script",
										["params"] = 
										{
											["command"] = 'CustomLaserDesignation("' .. grpname .. '", "' .. tgt .. '", "' .. class .. '", "' .. flight[f].target.LaserCode .. '")',	--this is a custom written task to allow coordinates bombing of target poistion at time of attack
										},
									},
								},
							}
							table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
						
						end
					end
					
					--SEAD engage tasks for each route segment
					if flight[f].task == "SEAD" then
						if flight[f].route[w].SEAD_radius then
							local task_entry = {
								["enabled"] = true,
								["auto"] = false,
								["id"] = "ControlledTask",
								["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								["params"] = 
								{
									["task"] = 
									{
										["id"] = "EngageTargets",
										["params"] = 
										{
											["targetTypes"] = 
											{
												[1] = "SAM TR",
											},
											["maxDistEnabled"] = true,
											["priority"] = 0,
											["maxDist"] = flight[f].route[w].SEAD_radius,
											["weaponType"] = weaponType,
											["expend"] = flight[f].loadout.expend,
											["attackType"] = flight[f].loadout.attackType,
											["altitudeEdited"] = true,
											["altitudeEnabled"] = true,
											["altitude"] = flight[f].loadout.attackAlt or flight[f].loadout.hAttack,
										},
									},
									["stopCondition"] = 
									{
										["lastWaypoint"] = w + 1,
									},
								}
							}
							if flight[f].loadout.weaponType == nil then							--if no specific weapon type defined in loadout
								task_entry.params.task.params.weaponType = 268402702			--use Anti-Radar Missile
							end
							table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
						end
					end
					
					--Escort and Fighter Sweep Custom Search and Engage Task
					if flight[f].task == "Fighter Sweep" then
						if flight[f].route[w].id == "Join" or (flight[f].route[w].id == "Spawn" and (flight[f].route[w + 1].id ~= "Join" and flight[f].route[w + 1].id ~= "Departure")) then
							local grpname = "Pack " .. p .. " - " .. flight[f].name .. " - " .. flight[f].task .. " " .. f
							local task_entry = {	
								["enabled"] = true,
								["auto"] = false,
								["id"] = "WrappedAction",
								["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								["params"] = 
								{
									["action"] = 
									{
										["id"] = "Script",
										["params"] = 
										{
											["command"] = 'CustomSearchThenEngage("' .. grpname .. '", ' .. flight[f].loadout.standoff .. ', "Air")',
										},
									},
								},
							}
							table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)	
						end
					elseif flight[f].task == "Escort" then
						if flight[f].route[w].id == "Join" or (flight[f].route[w].id == "Spawn" and (flight[f].route[w + 1].id ~= "Join" and flight[f].route[w + 1].id ~= "Departure")) then
							local target = "Battle airplanes"
							if  flight[f].helicopter == true then															-- modif Miguel21 M06 : helicoptere playable
								target = "Helicopters"
							end
							
							local grpname = "Pack " .. p .. " - " .. flight[f].name .. " - " .. flight[f].task .. " " .. f
							local task_entry = {	
								["enabled"] = true,
								["auto"] = false,
								["id"] = "WrappedAction",
								["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								["params"] = 
								{
									["action"] = 
									{
										["id"] = "Script",
										["params"] = 
										{
											["command"] = 'CustomSearchThenEngage("' .. grpname .. '", ' .. flight[f].loadout.standoff .. ', "'..target..'")',
										},
									},
								},
							}
							table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
						end
					end
					
					if flight[f].task == "CAP" then					
						if flight[f].route[w].id ~= "Station" and flight[f].route[w].id ~= "Departure" and flight[f].route[w].id ~= "Land" then
							local task_entry = {
								["enabled"] = true,
								["auto"] = false,
								["id"] = "ControlledTask",
								["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								["params"] = 
								{
									["task"] = 
									{
										["enabled"] = true,
										["auto"] = false,
										["id"] = "EngageTargets",
										["params"] = 
										{
											["targetTypes"] = 
											{
												[1] = "Air",
											}, -- end of ["targetTypes"]
											["priority"] = 0,
											["value"] = "Air;",
											["noTargetTypes"] = 
											{
												[1] = "Cruise missiles",
												[2] = "Antiship Missiles",
												[3] = "AA Missiles",
												[4] = "AG Missiles",
												[5] = "SA Missiles",
											}, -- end of ["noTargetTypes"]
											["maxDistEnabled"] = true,
											["maxDist"] = 30000,
										}, -- end of ["params"]
									},
								}
							}
							table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)	
						end
					end
					
					
					--station tasks
					if flight[f].route[w].id == "Station" and flight[f].route[w + 1].id == "Station" then
						if flight[f].task == "CAP" then
							local task_entry = {
								["enabled"] = true,
								["auto"] = false,
								["id"] = "ControlledTask",
								["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								["params"] = 
								{
									["task"] = 
									{
										["id"] = "EngageTargetsInZone",
										["params"] = 
										{
											["targetTypes"] = 
											{
												[1] = "Air",
												[2] = "Cruise missiles",
											},
											["x"] = flight[f].target.x,
											["y"] = flight[f].target.y,
											["value"] = "Air;Cruise missiles;",
											["priority"] = 0,
											["zoneRadius"] = flight[f].target.radius,
										},
									},
									["stopCondition"] = 
									{
										["lastWaypoint"] = w + 1,
									},
								}
							}
							table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)							
						elseif flight[f].task == "AWACS" then
							local task_entry = {
								["enabled"] = true,
								["auto"] = false,
								["id"] = "ControlledTask",
								["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								["params"] = 
								{
									["task"] = 
									{
										["id"] = "AWACS",
										["params"] = {},
									},
									["stopCondition"] = 
									{
										["lastWaypoint"] = w + 1,
									},
								}
							}
							table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
						elseif flight[f].task == "Refueling" then
							local task_entry = {
								["enabled"] = true,
								["auto"] = false,
								["id"] = "ControlledTask",
								["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								["params"] = 
								{
									["task"] = 
									{
										["id"] = "Tanker",
										["params"] = {},
									},
									["stopCondition"] = 
									{
										["lastWaypoint"] = w + 1,
									},
								}
							}
							table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
						end
					end
					
					--orbit on departure
					if flight[f].route[w].id == "Departure" then
						if flight[f].number > 1 or (#flight > 1 and flight[f].loadout.tStation == nil) or flight[f].target.firepower.packmax then		--orbit on departure only for flights larger than 1-ship, flights that are part of a package (but no on-station tasks) or multi-packages
							local speed = pack[p].main[1].loadout.vCruise / 3 * 2	
							if flight[f].loadout.vCruise then
								speed = flight[f].loadout.vCruise / 3 * 2
							end
								
							local grpname = "Pack " .. p .. " - " .. flight[f].name .. " - " .. flight[f].task .. " " .. f
							local task_entry = {	
								["enabled"] = true,
								["auto"] = false,
								["id"] = "WrappedAction",
								["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								["params"] = 
								{
									["action"] = 
									{
										["id"] = "Script",
										["params"] = 
										{
											["command"] = 'OrbitPosition("' .. grpname .. '", ' .. waypoints[w]["alt"] .. ', ' .. speed .. ', ' .. departure_time .. ')',
										},
									},
								},
							}
							table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
						end
					end
					
					--A-A TACAN for tankers, activate TACAN on first orbit WP
					if flight[f].route[w].id == "Station" and flight[f].route[w + 1].id == "Station" then
						if flight[f].task == "Refueling" then
							if flight[f].type == "KC-135" or flight[f].type == "KC130" or flight[f].type == "KC135BDA" or flight[f].type == "S-3B Tanker" or flight[f].type == "KC135MPRS" then	--only specific tanker types have air-air TACAN
								if flight[1].tacan == nil then
									flight[1].tacan = GetTankerTACAN()															--get new channel for first flight in pack only, all other flights will use same channel
								end
								local task_entry = {
									["enabled"] = true,
									["auto"] = true,
									["id"] = "WrappedAction",
									["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
									["params"] = 
									{
										["action"] = 
										{
											["id"] = "ActivateBeacon",
											["params"] = 
											{
												["type"] = 4,
												["AA"] = true,
												["unitId"] = id_counter,
												["modeChannel"] = "Y",
												["name"] = "",
												["channel"] = flight[1].tacan,
												["callsign"] = "TKR",
												["system"] = 4,
												["bearing"] = true,
												["frequency"] = 1087000000 + flight[1].tacan * 1000000,
											},
										},
									},
								}
								if task_entry.params.action.params.frequency > 1150000000 then
									task_entry.params.action.params.frequency = task_entry.params.action.params.frequency - 126000000
								end
								table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
							end
						end
					end
					
					--A-A TACAN for tankers, deactivate beacon on second orbit WP
					if flight[f].route[w].id == "Station" and flight[f].route[w - 1].id == "Station" then
						if flight[f].task == "Refueling" then
							if flight[f].type == "KC-135" or flight[f].type == "KC130" or flight[f].type == "KC135BDA" or flight[f].type == "S-3B Tanker" then	--only specific tanker types have air-air TACAN			
								local task_entry = {
									["enabled"] = true,
									["auto"] = false,
									["id"] = "WrappedAction",
									["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
									["params"] = 
									{
										["action"] = 
										{
											["id"] = "DeactivateBeacon",
											["params"] = 
											{
											},
										},
									},
								}
								table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
							end
						end
					end
					
					--orbit on station
					if flight[f].route[w].id == "Station" and flight[f].route[w + 1].id == "Station" then
						local task_entry = {
							["enabled"] = true,
							["auto"] = false,
							["id"] = "ControlledTask",
							["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
							["params"] = 
							{
								["task"] = 
								{
									["id"] = "Orbit",
									["params"] = 
									{
										["altitude"] = flight[f].loadout.hAttack,
										["pattern"] = "Race-Track",
										["speed"] = flight[f].loadout.vAttack,
									},
								},
								["stopCondition"] = 
								{
									["time"] = flight[f].route[w + 1].eta
								}
							}
						}
						table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
					end
					
					--SEAD switch from IP to egress
					if flight[f].route[w].id == "IP" and flight[f].task == "SEAD" then
						local speed = pack[p].main[1].loadout.vCruise	
						if flight[f].loadout.vCruise and flight[f].loadout.vCruise < speed then
							speed = flight[f].loadout.vCruise / 3 * 2
						end
						local task_entry = {
							["enabled"] = true,
							["auto"] = false,
							["id"] = "WrappedAction",
							["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
							["params"] = {
								["action"] = {
									["id"] = "SwitchWaypoint",
									["params"] = {				
										["fromWaypointIndex"] = w,						--from IP
										["goToWaypointIndex"] = w + 2,					--directly to egress
									},
								},
							},
						}
						table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
						
						local task_entry2 = {
							["enabled"] = true,
							["auto"] = false,
							["id"] = "ControlledTask",
							["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
							["params"] = {
								["task"] = {
									["id"] = "Orbit",
									["params"] = {
										["altitude"] = waypoints[w]["alt"],
										["pattern"] = "Race-Track",
										["speed"] = speed,
										["speedEdited"] = true,
									},
								}, 
								["stopCondition"] = {
									["time"] = flight[f].route[w + 2].eta,
								},
							},
						}
						table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry2)
					end
					
					--orbit on egress
					if flight[f].route[w].id == "Egress" and flight[f].task == "Escort" then
						local speed = pack[p].main[1].loadout.vCruise	
						if flight[f].loadout.vCruise and flight[f].loadout.vCruise < speed then
							speed = flight[f].loadout.vCruise / 3 * 2
						end
						local task_entry = {
							["enabled"] = true,
							["auto"] = false,
							["id"] = "ControlledTask",
							["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
							["params"] = 
							{
								["task"] = 
								{
									["id"] = "Orbit",
									["params"] = 
									{
										["altitude"] = waypoints[w]["alt"],
										["pattern"] = "Circle",
										["speed"] = speed,
									},
								},
								["stopCondition"] = 
								{
									["time"] = flight[f].route[w].eta
								}
							}
						}
						table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
					end
					
					--rejoin flight on egress
					if (flight[f].task == "Strike" or flight[f].task == "Anti-ship Strike" ) and flight[f].route[w].id == "Egress" then					
						local grpname = "Pack " .. p .. " - " .. flight[f].name .. " - " .. flight[f].task .. " " .. f
						local task_entry = {																				--task is a command to run LUA code
							["enabled"] = true,
							["auto"] = false,
							["id"] = "WrappedAction",
							["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
							["params"] = 
							{
								["action"] = 
								{
									["id"] = "Script",
									["params"] = 
									{
										["command"] = 'CustomRejoin("' .. grpname .. '")',
									},
								},
							},
						}
						table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
					end
					
					--restrict RTB on winchester from IP on
					--[[if flight[f].route[w].id == "IP" and (flight[f].task == "SEAD" or flight[f].task == "Strike" or flight[f].task == "Anti-ship Strike" or flight[f].task == "Flare Illumination" or flight[f].task == "Laser Illumination") then
						if flight[f].player ~= true then
							local task_entry = {
								["enabled"] = true,
								["auto"] = false,
								["id"] = "WrappedAction",
								["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								["params"] = 
								{
									["action"] = 
									{
										["id"] = "Option",
										["params"] = 
										{
											["value"] = 0,
											["name"] = 10,
										},
									},
								},
							}
							table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
						end
					end]]--
					
					--restrict weapon jettison from IP on
					--[[if flight[f].route[w].id == "IP" and (flight[f].task == "Strike" or flight[f].task == "Anti-ship Strike" or flight[f].task == "Flare Illumination" or flight[f].task == "Laser Illumination") then
						if flight[f].player ~= true then	
							local task_entry = {
								["enabled"] = true,
								["auto"] = false,
								["id"] = "WrappedAction",
								["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								["params"] = 
								{
									["action"] = 
									{
										["id"] = "Option",
										["params"] = 
										{
											["value"] = true,
											["name"] = 15,
										},
									},
								},
							}
							table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
						end
					end]]--
					
					--allow weapon jettison from egress on
					if flight[f].route[w].id == "Egress" and (flight[f].task == "SEAD" or flight[f].task == "Strike" or flight[f].task == "Anti-ship Strike" or flight[f].task == "Flare Illumination" or flight[f].task == "Laser Illumination") then
						if flight[f].player ~= true and flight[f].client ~= true then	
							local task_entry = {
								["enabled"] = true,
								["auto"] = false,
								["id"] = "WrappedAction",
								["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								["params"] = 
								{
									["action"] = 
									{
										["id"] = "Option",
										["params"] = 
										{
											["value"] = false,
											["name"] = 15,
										},
									},
								},
							}
							table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
						end
					end
					
					--IP/egress reaction on threat for recon
					if flight[f].task == "Reconnaissance" and flight[f].route[w].id == "IP" then
						if flight[f].player ~= true and flight[f].client ~= true then	
							local task_entry = {
								["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								["auto"] = false,
								["id"] = "WrappedAction",
								["enabled"] = true,
								["params"] = 
								{
									["action"] = 
									{
										["id"] = "Option",
										["params"] = 
										{
											["value"] = 1,
											["name"] = 1,
										},
									},
								},
							}
							table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
						end
					elseif flight[f].task == "Reconnaissance" and flight[f].route[w].id == "Egress" then
						if flight[f].player ~= true and flight[f].client ~= true then	
							local task_entry = {
								["number"] = #waypoints[w]["task"]["params"]["tasks"] + 1,
								["auto"] = false,
								["id"] = "WrappedAction",
								["enabled"] = true,
								["params"] = 
								{
									["action"] = 
									{
										["id"] = "Option",
										["params"] = 
										{
											["value"] = 2,
											["name"] = 1,
										},
									},
								},
							}
							table.insert(waypoints[w]["task"]["params"]["tasks"], task_entry)
						end
					end

			-- if flight[f].type == "A-10C" or flight[f].type == "A-10C_2" then
				-- -- for w, route_ in pairs(route) do
					-- if waypoints[w - 1] then																			--previous waypoint exists
						-- local distance = GetDistance(waypoints[w - 1], waypoints[w])										--distance between waypoints
						-- -- print("AtoFP waypoints distance "..waypoints[w].name.." "..math.ceil(distance))
					-- end
				-- -- end
			-- end	
			
			
					--navigation information on waypoint name for player flight
					if flight[f].player or flight[f].client then																				--flight is player flight
						if waypoints[w - 1] then																			--previous waypoint exists
							local distance = GetDistance(waypoints[w - 1], waypoints[w])									--distance between waypoints
							if waypoints[w].name == "Target" then
								distance = GetDistance(waypoints[w - 2], waypoints[w])										--for target waypoint measure distance from IP, since attack point is removed for player flight
							end
							if distance > 0 then																			--distance is not zero
								local heading = math.floor(GetHeading(waypoints[w - 1], waypoints[w]))						--heading between waypoints
								heading = heading - camp.variation															--adjust heading (true heading) with variation of map to get magnetix heading
								if heading < 0 then
									heading = heading + 360
								elseif heading > 359 then
									heading = heading - 360
								end
								if heading < 10 then
									heading = "00" .. heading
								elseif heading < 100 then
									heading = "0" .. heading
								end
								if camp.units == "metric" then
									distance = math.ceil(distance / 1000) .. "KM"
								else
									distance = math.ceil(distance / 1000 * 0.539957) .. "NM"
								end
								-- Miguel21 modification M17
								if flight[f].type == "F-14B" and NavTargetPoints[1] then
									if waypoints[w].name == "Target" or waypoints[w].name == "Attack" then  waypoints[w].name = "ST" end
									if waypoints[w].name == "Station"  then  waypoints[w].name = "DP" end
								end
								waypoints[w]["name"] = waypoints[w]["name"] .. ": " .. heading .. "/" .. distance			--add heading and distance to waypoint name
							end
						end
					end
				end	-- Fin de Route
			
				-- si multijoueur, les Flight AI commencent en vol + M11.n
				if ((flight[f].type == 'F-14B' or flight[f].type == 'FA-18C_hornet') and Multi.NbGroup >= 1 and flight[f].player ~= true and flight[f].client ~= true 
				and string.find(flight[f].base,"CVN") and flight[f].task ~= "Intercept") then
					if camp.startup then										--if player value defined in camp
						spawn_time = spawn_time + camp.startup						--if in-flight departure, the time initially added is deleted.
					else
						spawn_time = spawn_time + 300								--if in-flight departure, the time initially added is deleted.
					end
				end
			
				--lock ETA and speed of first waypoint
				waypoints[1]["ETA_locked"] = true
				waypoints[1]["speed_locked"] = true
				if waypoints[1]["speed"] == nil then
					waypoints[1]["speed"] = 1
				end
				
				--remove attack WP for player flight
				if flight[f].player == true or flight[f].client == true then
					for w = 1, #waypoints do
						if waypoints[w].briefing_name == "Attack" then
							table.remove(waypoints, w)
							camp.player.tgt_wp = camp.player.tgt_wp - 1
							break
						end
					end
				end
				
				--store player waypoints for briefing creation
				if flight[f].player == true then
					camp.player.waypoints = deepcopy(waypoints)
					if camp.player.waypoints[2] then
						camp.player.waypoints[2].speed = 0
						camp.player.waypoints[2].alt = 0
					end
					-- if camp.player.waypoints[3] then
						-- camp.player.waypoints[3].speed = pack[p].main[1].loadout.vCruise / 4 * 3
					-- end
				end
				
				if flight[f].client and flight[f].IdClient then
					camp.client[flight[f].IdClient].waypoints = deepcopy(waypoints)
				end
					
				
				--remove target WP for certain flights
				if target_wp_remove then
					table.remove(waypoints, target_wp_remove)
					
					for w = target_wp_remove, #waypoints do												--adjust stop condition WPs
						if waypoints[w]["task"]["params"]["tasks"] then									--WP has tasks
							for task_n,task in ipairs(waypoints[w]["task"]["params"]["tasks"]) do		--go through tasks
								if task["params"]["stopCondition"] and task["params"]["stopCondition"]["lastWaypoint"] then					--task has a last waypoint stop condition
									task["params"]["stopCondition"]["lastWaypoint"] = task["params"]["stopCondition"]["lastWaypoint"] - 1	--decreas last WP number by one to account for the removed WP
								end
								if task["params"]["action"] and task["params"]["action"]["id"] == "SwitchWaypoint" then						--task is a switch WP
									task["params"]["action"]["params"]["fromWaypointIndex"] = task["params"]["action"]["params"]["fromWaypointIndex"] - 1
									task["params"]["action"]["params"]["goToWaypointIndex"] = task["params"]["action"]["params"]["goToWaypointIndex"] - 1
								end
							end
						end
					end
				end
				
				--remove taxi waypoint
				if waypoints[1].name == "Taxi" then
					waypoints[2]["airdromeId"] = waypoints[1]["airdromeId"]
					waypoints[2]["linkUnit"] = waypoints[1]["linkUnit"]
					waypoints[2]["helipadId"] = waypoints[1]["helipadId"]
					waypoints[2]["action"] = waypoints[1]["action"]
					waypoints[2]["type"] = waypoints[1]["type"]
					table.remove(waypoints, 1)
					waypoints[1]["ETA"] = spawn_time
					waypoints[1]["ETA_locked"] = true
					waypoints[1]["speed_locked"] = true
					if waypoints[1]["speed"] == nil then
						waypoints[1]["speed"] = 1
					end
					
					for w = 1, #waypoints do															--adjust stop condition WPs
						if waypoints[w]["task"]["params"]["tasks"] then									--WP has tasks
							for task_n,task in ipairs(waypoints[w]["task"]["params"]["tasks"]) do		--go through tasks
								if task["params"]["stopCondition"] and task["params"]["stopCondition"]["lastWaypoint"] then					--task has a last waypoint stop condition
									task["params"]["stopCondition"]["lastWaypoint"] = task["params"]["stopCondition"]["lastWaypoint"] - 1	--decreas last WP number by one to account for the removed WP
								end
								if task["params"]["action"] and task["params"]["action"]["id"] == "SwitchWaypoint" then						--task is a switch WP
									task["params"]["action"]["params"]["fromWaypointIndex"] = task["params"]["action"]["params"]["fromWaypointIndex"] - 1
									task["params"]["action"]["params"]["goToWaypointIndex"] = task["params"]["action"]["params"]["goToWaypointIndex"] - 1
								end
							end
						end
					end
				end
				
				--add descend waypoint
				if flight[f].player ~= true and flight[f].client ~= true then																--for AI flights only
					for w = 3, #waypoints do
						if waypoints[w].alt < waypoints[w - 1].alt and waypoints[w]["type"] ~= "Land" then		--for any descend waypoint that is not the landing waypoint
							local extraWP = deepcopy(waypoints[w])												--make a copy of the descend waypoint
							extraWP.x = (waypoints[w].x + waypoints[w + -1].x) / 2								--position half-way between descend waypoint and previous waypoint
							extraWP.y = (waypoints[w].y + waypoints[w + -1].y) / 2								--position half-way between descend waypoint and previous waypoint
							extraWP.ETA = (waypoints[w].ETA + waypoints[w + -1].ETA) / 2						--ETA half-way between descend waypoint and previous waypoint
							extraWP.task.params.tasks = {}
							extraWP.name = "AI Descend Helper"
							table.insert(waypoints, w, extraWP)
							
							--adjust stop condition and switch WPs
							for w2 = w, #waypoints do															--go through waypoints from inserted WP to end
								if waypoints[w2]["task"]["params"]["tasks"] then								--WP has tasks
									for task_n,task in ipairs(waypoints[w2]["task"]["params"]["tasks"]) do		--go through tasks
										if task["params"]["stopCondition"] and task["params"]["stopCondition"]["lastWaypoint"] then					--task has a last waypoint stop condition
											task["params"]["stopCondition"]["lastWaypoint"] = task["params"]["stopCondition"]["lastWaypoint"] + 1	--increase last WP number by one to account for the inserted WP
										end
										if task["params"]["action"] and task["params"]["action"]["id"] == "SwitchWaypoint" then						--task is a switch WP
											task["params"]["action"]["params"]["fromWaypointIndex"] = task["params"]["action"]["params"]["fromWaypointIndex"] + 1
											task["params"]["action"]["params"]["goToWaypointIndex"] = task["params"]["action"]["params"]["goToWaypointIndex"] + 1
										end
									end
								end
							end
						end
					end
				end
				
				--first waypoint RTB on winchester
				--disabled due to AI problems (AI will ignore all threats once in RTB mode)
				--[[if flight[f].task == "SEAD" or flight[f].task == "CAS" or flight[f].task == "Ground Attack" or flight[f].task == "Pinpoint Strike" or flight[f].task == "Runway Attack" or flight[f].task == "Anti-ship Strike" then
					if flight[f].player ~= true then
						local task_entry = {
							["enabled"] = true,
							["auto"] = false,
							["id"] = "WrappedAction",
							["number"] = #waypoints[1]["task"]["params"]["tasks"] + 1,
							["params"] = 
							{
								["action"] = 
								{
									["id"] = "Option",
									["params"] = 
									{
										["value"] = weaponType,
										["name"] = 10,
									},
								},
							},
						}
						table.insert(waypoints[1]["task"]["params"]["tasks"], task_entry)
					end
				]]--end
				
				--first waypoint reaction to threat
				local task_entry = {
					["number"] = #waypoints[1]["task"]["params"]["tasks"] + 1,
					["auto"] = false,
					["id"] = "WrappedAction",
					["enabled"] = true,
					["params"] = 
					{
						["action"] = 
						{
							["id"] = "Option",
							["params"] = 
							{
								["value"] = 2,
								["name"] = 1,
							},
						},
					},
				}
				table.insert(waypoints[1]["task"]["params"]["tasks"], task_entry)
				
				--ATO_FP_Reglage01 : emport, ne pas larguer les emports en cas d'urgence pour les Strike
				--first waypoint restrict jettison for SEAD
				if flight[f].task == "SEAD" or flight[f].task == "Strike" or flight[f].task == "Anti-ship Strike" or flight[f].task == "Flare Illumination" or flight[f].task == "Laser Illumination" then
					local task_entry = {
						["enabled"] = true,
						["auto"] = false,
						["id"] = "WrappedAction",
						["number"] = #waypoints[1]["task"]["params"]["tasks"] + 1,
						["params"] = 
						{
							["action"] = 
							{
								["id"] = "Option",
								["params"] = 
								{
									["value"] = true,
									["name"] = 15,
								},
							},
						},
					}
					table.insert(waypoints[1]["task"]["params"]["tasks"], task_entry)
				end
				
				--first waypoint restrict air-air
				if flight[f].loadout.restrict_aa then
					local task_entry = {
						["enabled"] = true,
						["auto"] = false,
						["id"] = "WrappedAction",
						["number"] = #waypoints[1]["task"]["params"]["tasks"] + 1,
						["params"] = 
						{
							["action"] = 
							{
								["id"] = "Option",
								["params"] = 
								{
									["value"] = true,
									["name"] = 14,
								},
							},
						},
					}
					table.insert(waypoints[1]["task"]["params"]["tasks"], task_entry)
				end
				
				--first waypoint no RTB on bingo
				if flight[f].airdromeId == nil then
					local task_entry = {
						["enabled"] = true,
						["auto"] = false,
						["id"] = "WrappedAction",
						["number"] = #waypoints[1]["task"]["params"]["tasks"] + 1,
						["params"] = 
						{
							["action"] = 
							{
								["id"] = "Option",
								["params"] = 
								{
									["value"] = false,
									["name"] = 6,
								},
							},
						},
					}
					table.insert(waypoints[1]["task"]["params"]["tasks"], task_entry)
				end
												

				----- define units -----

				-- Miguel21 modification M11.l : Multiplayer (M11.l:groupe superieur à 2 possible)
				if Multi.NbGroup >= 1 then
					if  flight[f].client  or  flight[f].player  then
						if flight[f].number >= 2 and flight[f].NbPlaneClient <=2 then																			-- on ne veut pas d'avionIA au dela de 2
							flight[f].number = 2
						else
							flight[f].number = flight[f].NbPlaneClient
						end
					end
				end
				local units = {}
				
				for n = 1, flight[f].number do
					-- Miguel21 modification M12.b : Skill
					-- le niveau est s�par� en 4 (25% de 100)
					--Average (0 � 25)
					--Good (25� 50)
					--High (50 � 75)
					--Excellent (75 � 100)
					
					if flight[f].skill == "high" then
						calcWish = 62
					else 
						calcWish = skillWish[side]
					end
					
					if n == 1 or ( flight[f].player and n == 2 )then 
						mSkill =  math.random(calcWish-20, calcWish+18) / 25 		-- 75-62 = 13 (13 + 5 = 18 )5 % de chance d'avoir excellent
					else
						mSkill =  math.random(calcWish-50, calcWish+10) / 25
					end

		
					mSkill = math.floor(mSkill) + 1
					
					if mSkill < 1 then mSkill = 1
					elseif mSkill > 4 then mSkill = 4
					else mSkill = mSkill
					end	
					
					
					units[n] = {
						["alt"] = waypoints[1].alt,
						["heading"] = 0,
						["callsign"] = GetCallsign(flight[f].country, f, n, flight[f].task),
						["psi"] = 0,
						["livery_id"] = flight[f].livery,
						["type"] = flight[f].type,
						["y"] = waypoints[1]["y"] + ((n - 1) * 100) +  ((Pn - 1) * 1000), --ATO_FP_Debug01
						["x"] = waypoints[1]["x"] + ((n - 1) * 100) +  ((Pn - 1) * 1000), -- ATO_FP_Debug01
						["name"] = "Pack " .. p .. " - " .. flight[f].name .. " - " .. flight[f].task .. " " .. f .. "-" .. n,
						-- ["payload"] = flight[f].loadout.stores,
						["payload"] = {
							["pylons"] = flight[f].loadout.stores.pylons,
							["fuel"] = flight[f].loadout.stores.fuel,
							["flare"] = flight[f].loadout.stores.flare,
							["chaff"] = flight[f].loadout.stores.chaff,
							["gun"] =  flight[f].loadout.stores.gun,										-- ATO_FP_Debug04 Gun = 0 uniquement sur un Flight
						},
						["AddPropAircraft"] = flight[f].loadout.AddPropAircraft,
						["speed"] = waypoints[1].speed,
						["unitId"] = GenerateID(),
						["alt_type"] = waypoints[1].alt_type,
						["skill"] = skillTab[mSkill],
						["hardpoint_racks"] = true,

					}
					
					--FARP parking id
					-- if  flight[f].airdromeId >= 100 then
					if  string.find(flight[f].base,"FARP")  then
						units[n]["parking"] = tostring(n)
						units[n]["parking_id"] = tostring(n)
					end
					
					-- n assigne pas de parking aux IA qui spawn in air
					if waypoints[1]["action"] == "From Parking Area" and flight[f].parking_id and LimitedParkTiming ~= true and not db_airbases[flight[f].base].BaseAirStart then
						local findParkId = GetParkingId( flight[f].parking_id, flight[f].base)						
						if findParkId then
							units[n]["parking_id"] = findParkId
						end						
					end
										
					
					if flight[f].sidenumber and flight[f].sidenumber[1] and flight[f].sidenumber[2] then		--squadron has sidenumbers defined
						units[n]["onboard_num"] = GetSidenumber(flight[f].name, flight[f].sidenumber[1], flight[f].sidenumber[2],n , flight[f].player, flight[f].type)	--get new sidenumber
					else																						--squadron has no sidenumbers defined
						-- units[n]["onboard_num"] = "0" .. math.random(1, 99)										--us a random number
						units[n]["onboard_num"] = math.random(1, 99)										--us a random number
						units[n]["onboard_num"] = string.format("%03d", units[n]["onboard_num"])
					end
					
					--multiple skins for aircraft
					if flight[f].liveryModex then
						if flight[f].liveryModex[tonumber(units[n]["onboard_num"])] then
							units[n]["livery_id"] = flight[f].liveryModex[tonumber(units[n]["onboard_num"])]
						end					
					end
					
					if units[n]["livery_id"] and type(units[n]["livery_id"]) == "table" then												--if skin is a table
						units[n]["livery_id"] = units[n]["livery_id"][math.random(1, #units[n]["livery_id"])]	--chose a random skin from table
					end
					
					-- modification Miguel M17
					if flight[f].type == "F-14B" and ( flight[f].player or flight[f].client ) and AddPropAircraft then
						 units[n]["AddPropAircraft"] = AddPropAircraft 
					end
					
					--remove gun ammunition from AI escorts to prevent them from strafing aircraft on the ground at hostile air bases
					-- if (flight[f].task == "Escort" and not flight[f].player ) and (flight[f].task == "Escort" and not flight[f].client ) then	--if fligh is taskes as escort and is not player flight
					if flight[f].task == "Anti-ship Strike" and not (flight[f].player  ) then	--or Multi.NbGroup >= 1
						if units[n].payload.gun and units[n].payload.gun == 100 then								--if loadout has full gun ammo
							units[n].payload.gun = 0																--remove all gun ammo
						end
					end
				end
				
				----- define group -----
				local group = {				
					['frequency'] = GetFrequency(side, flight[f].target_name, flight[f].task, flight[f].type, "UHF"),				-- M06
					['taskSelected'] = true,
					['modulation'] = 0,
					['groupId'] = GenerateID(),
					['tasks'] = {
					},
					['route'] = {
						['points'] = waypoints,
					},
					['hidden'] = true,
					['units'] = units,
					['radioSet'] = true,
					["name"] = "Pack " .. p .. " - " .. flight[f].name .. " - " .. flight[f].task .. " " .. f,
					['communication'] = true,
					['x'] = waypoints[1]["x"],
					['y'] = waypoints[1]["y"],
					['start_time'] = 1,
					['task'] = flight[f].task,
					['uncontrolled'] = false,
				}

				-- ATO_FP_Debug01
				-- decale les apparitions en vol pour eviter les collisions en vol
				if waypoints[1]["type"] == "Spawn" then
					for	n = 1 , #group.units do
						group.units[n].x = ((Pn-1) * 1000) + group.units[n].x
						group.units[n].y = ((Pn-1) * 1000) + group.units[n].y
					end
				end
				
				-- modif M17
				if flight[f].type == "F-14B" and NavTargetPoints[1] then
					 group["NavTargetPoints"]= NavTargetPoints 
				end
				
				if flight[f].task == "Strike" then												--Strike is a generic A-G task that needs to be replaced by the respective DCS task
					if flight[f].loadout.weaponType == "ASM"  then						-- + ATO_FP_Debug06 strike ASM B52
						group['task'] = "Pinpoint Strike"
					elseif flight[f].target.class == nil then
						group['task'] = "Ground Attack"
					elseif flight[f].target.class == "vehicle" then
						group['task'] = "CAS"
					elseif flight[f].target.class == "static" then
						group['task'] = "CAS"
					elseif flight[f].target.class == "airbase" then
						group['task'] = "CAS"
					end
				elseif flight[f].task == "Escort Jammer" then									--Escort Jammer task does not exitsts in DCS and needs to be replaced
					group['task'] = "Ground Attack"
				elseif flight[f].task == "Flare Illumination" then								--Flare illumination task does not exist in DCS and needs to be replaced
					group['task'] = "Ground Attack"
				elseif flight[f].task == "Laser Illumination" then								--Laser illumination task does not exist in DCS and needs to be replaced
					group['task'] = "AFAC"
				elseif flight[f].task == "Anti-ship Strike" then 
					group['task'] = "Antiship Strike"											-- Miguel debugB 
				end

				---- unhide player package -----
				if camp.debug then																--debug is on
					group.hidden = false														--unhide all groups
				elseif camp.player and camp.player.side == side then							--player side										
					group.hidden = false														--unhide group
					--if camp.player.pack_n == p then											--package is player package
						--group.hidden = false													--unhide group
					--elseif flight[f].task == "AWACS" then										--flight is an AWACS on player side
						--group.hidden = false													--unhide group
					--elseif flight[f].task == "Refueling" then									--flight is a tanker on player side
						--group.hidden = false													--unhide group
					--end
				elseif camp.client and 	flight[f].IdClient and camp.client[flight[f].IdClient].side == side then							--player side										
					group.hidden = false														--unhide group
				end
				
				-- Miguel21 modification M31 	Remove all static aircraft from the deck
				if  mission_ini.CVN_CleanDeck == true and string.find(flight[f].base,"CVN") then
					deleteStaticOnCVN(flight[f].base)
				end
		
				if not mission_ini.SC_SpawnOn[flight[f].type] then  mission_ini.SC_SpawnOn[flight[f].type] = "deck" end

				local SpawnDeck = true
				local SpawnAir = false
				local SpawnCata = false
				-- if SuperCarrier and db_airbases[flight[f].base].unitname and not ( flight[f].player or flight[f].client ) then
				if db_airbases[flight[f].base].unitname and not ( flight[f].player or flight[f].client ) then
					if  mission_ini.SC_SpawnOn[flight[f].type] == "catapult" then 
						SpawnDeck = false
						SpawnCata = true
					elseif  mission_ini.SC_SpawnOn[flight[f].type] == "air" then 
						SpawnDeck = false
						SpawnAir = true
					end
				end
				
				-- START seulement utile au sol
				-- uncontrolled : SOL :permet d'utiliser (START + a_set_ai_task) au SOL
				
				-- lateActivation : SOL + VOL + a_activate_group (invisible avant cela)

				-- lateActivation : utile avec apparition joueur décalé sur PA (lié à activeGroup ou ai start?)
				
				--conclusion:
				-- SOL decale et visible : uncontrolled + (START + a_set_ai_task)
				-- SOL decale 			 : lateActivation + a_activate_group
				
				-- VOL decale			: ["start_time"] = 60, + ETA = 60 etc
				-- VOL decale			: lateActivation + a_activate_group
				
				-- VOL sur TRIGGER: lateActivation + triggerActiveGroup
				
				--CVN
				--uncontrolled
				--lateActivation
				--a_activate_group (fait apparaitre l'avion sans pilote)
				--(START + a_set_ai_task) (pilote + demarrage)
				
				if debugStart then debugTxt = debugTxt.."\n"..("") end	
				if debugStart then debugTxt = debugTxt.."\n"..("AtoFP FirstMsg " .. "Pack " .. p .. " - " .. flight[f].name .. " - " .. flight[f].task .. " " .. f) end
				
				if (not spawn_time or spawn_time == nil or spawn_time == "") and departure_time ~= "" then
					spawn_time = departure_time
				end
				
				local activate_time = spawn_time
				local FlagInsertSixpack = false
				
				-- local taxi_time = spawn_time
				-- = - = - = - = -- = - = - = - = - = - = - = - = - = - = -- = - = - = - = - = - = - = - = - = - = -- = - = - = - = - = - = - = - = - = - = -- = - = - = - = - = - = -
				--Player & Client on SuperCarrier
				-- = - = - = - = -- = - = - = - = - = - = - = - = - = - = -- = - = - = - = - = - = - = - = - = - = -- = - = - = - = - = - = - = - = - = - = -- = - = - = - = - = - = -
				if (db_airbases[flight[f].base].unitname or LimitedParkTiming ) and  ( flight[f].player or flight[f].client )  then --??? LimitedParkTiming? vraiment pour le joueur?
					if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe 0A-a SinglePlayer ..NbPlanetDeck: "..NbPlanetDeck) end
					
					spawn_time = mission_ini.startup_time_player
					
					if flight[f].task == "Intercept" then 
						spawn_time = -1
					end				
					
					group.start_time = 1
					group['route']['points'][1]["ETA"] = 1
					
					local PlayerSixPack = {}
					if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe PlayerClient AddTimingDeckCata "..spawn_time) end
					--construit une table que l'on triera plus tard pour decider qui a le droit d etre sur le sixpack et ne pas gener les autres
					PlayerSixPack = {
						time = spawn_time ,
						groupName = group.name,
						number = flight[f].number,
						LimitedParkNb = db_airbases[flight[f].base].LimitedParkNb,
						client = true,
						}	

					FlagInsertSixpack = true
					if not testSixPack[flight[f].base] then testSixPack[flight[f].base] = {} end
					table.insert(testSixPack[flight[f].base],  PlayerSixPack)	
				end
				
				--LimitedParkTiming RAPPEL concerne: CVN LHA FARP et Petite BASE, si le nombre de place est superieur à db_airbases.LimitedParkNb				
				----- late groups spawn uncontrolled at mission start -----
				if ((group['route']['points'][1]["ETA"] > 0 and flight[f].task ~= "Intercept")  or LimitedParkTiming ) and  not flight[f].player and not flight[f].client
					 then	--group launches after mission start																	-- calcul le nombre de flight dans un Package, en comptant ceux des Roles				
					if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe AA [ETA] > 0 "..tostring(LimitedParkTiming)) end
					
					if (db_airbases[flight[f].base].unitname and flight[f].task ~= "Intercept")  or string.find(flight[f].base,"FARP") then												--for groups on aircraft carriers -- miguel21 modification M37.e SuperCarrier   and ((not SuperCarrier ) or (SuperCarrier and spawn_time>600))
						if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe BB unitname+FARP "..group['route']['points'][1]["ETA"]) end
						
						--permet de spawner les avions avant qu'ils ne démarrent
						if spawn_time - 120	>  (mission_ini.startup_time_player + 200) then
							activate_time = spawn_time - 120
						end								
				
						--si multi ou ddserverAirAir: les IA en vol
						-- single ou ddserver : on gere les taxiing cata
						if  (SinglePlayer  or  SingleWithDServer) and not SingleWithDServerAiAir then
							if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe CC SinglePlayer") end
							
							
							-- = = = SixPack = = = = - = - = - = -- = - = - = - = - = - = - = - = - = - = -- = - =
							
							--construit une table que l'on triera plus tard pour decider qui a le droit d etre sur le sixpack et ne pas gener les autres
							if group['route']['points'][1]["ETA"]	<  (mission_ini.startup_time_player + 200) and waypoints[1]["action"] ~= "Turning Point" and not SpawnAir and not SpawnCata then
								-- and flight[f].type ~= "E-2C" and flight[f].type ~= "S-3B Tanker"
								
								if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe -- == SixPack == -- ") end
								
								if not TimingDeckCata[side] then TimingDeckCata[side] = {} end
								if not TimingDeckCata[side][flight[f].base] then TimingDeckCata[side][flight[f].base] = {} end
								
								--TODO il faudrait prendre en compte le nombre d'avion à lancer, mais bordel à faire
								-- local timeToLauch = flight[f].number * mission_ini.CVN_TimeBtwPlane
								-- placeTiming = math.ceil(spawn_time / 300) *300
							
								local timeToLauch = math.ceil(4 * mission_ini.CVN_TimeBtwPlane)
								local placeTiming = math.ceil(spawn_time / timeToLauch) * timeToLauch
								
								counter = 0
								repeat
									counter = counter + 1
									placeTiming = placeTiming - timeToLauch 
								until not TimingDeckCata[side][flight[f].base][placeTiming]  or counter == 20	or placeTiming < 0							

								if counter == 20 or placeTiming < 0 then 
									local BugFrom =  " TimingDeckCata "..debug.getinfo(1).currentline
									SpawnOn( "air", waypoints, group, Pn, spawn_time + 300, BugFrom, flight, f)
								else
									TimingDeckCata[side][flight[f].base][placeTiming] = group.name
									spawn_time = placeTiming
									activate_time = 5
									group.start_time = 5
									NbPlanetDeck = NbPlanetDeck + flight[f].number
									
									local tempSixPack = {}
									if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe BBB2 AddTimingDeckCata "..placeTiming.." NbPlanetDeck: "..NbPlanetDeck) end
									--construit une table que l'on triera plus tard pour decider qui a le droit d etre sur le sixpack et ne pas gener les autres
									tempSixPack = {
										time = placeTiming ,
										groupName = group.name,
										number = flight[f].number,
										LimitedParkNb = db_airbases[flight[f].base].LimitedParkNb,
										type = flight[f].type,
										}	

									FlagInsertSixpack = true
									if not testSixPack[flight[f].base] then testSixPack[flight[f].base] = {} end
									table.insert(testSixPack[flight[f].base],  tempSixPack)										
									
								end
							end
							
							
							if camp.player  and camp.player.side == side and camp.player.pack_n == p and camp.player.airbase == flight[f].base and flight[f].task ~= "AWACS" and flight[f].task ~= "Refueling" then					--for flights in player's package and package does not cover a station and flight[f].task ~= "CAP"
								if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe DD camp.player.pack_n") end

								
								--les Planes qui genent le taxiing spawn selon conf_mod
								if not SpawnDeck then 
									local BugFrom =  ""..debug.getinfo(1).currentline
									SpawnOn( mission_ini.SC_SpawnOn[flight[f].type], waypoints, group, Pn, spawn_time, BugFrom, flight, f)
								end
								
								-- les helico sur le FARP du joueur spawn en l'air
								--TODO mettre ça ailleur
								if PlayerFirstParking then 
									if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe EE PlayerFirstParking") end
									local BugFrom =  ""..debug.getinfo(1).currentline
									SpawnOn( "air", waypoints, group, Pn, spawn_time, BugFrom, flight, f)
								end

							elseif group['route']['points'][1]["ETA"] <= mission_ini.startup_time_player + 200  and db_airbases[flight[f].base].LimitedParkNb then		--+ 600					-- Gère le spawn des groupes au début de mission																	
								if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe FFa ETA mission_ini.startup_time_player + 200 & LimitedParkNb NbPlanetDeck: "..NbPlanetDeck) end
								
								if not FlagInsertSixpack and flight[f].number + NbPlanetDeck >= db_airbases[flight[f].base].LimitedParkNb  then										-- on ne dépasse pas le nb max de spawn sur le CVN 
									if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe FFb  NbPlanetDeck >= LimitedParkNb") end
									
									group['lateActivation'] = true																		--make group late activation  -- SOL decale 			 : lateActivation + a_activate_group
									group['uncontrolled'] = true																		--Seulement sur CVN, lateActivation and uncontrolled requis

									local BugFrom =  " NbPlanetDeck >= db_airbases[flight[f].base].LimitedParkNb "..debug.getinfo(1).currentline
									SpawnOn( "air", waypoints, group, Pn, spawn_time + 300, BugFrom, flight, f)	
									
								elseif FlagInsertSixpack and NbPlanetDeck >= db_airbases[flight[f].base].LimitedParkNb  then										-- on ne dépasse pas le nb max de spawn sur le CVN 
									if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe FFb  NbPlanetDeck >= LimitedParkNb") end
									
									group['lateActivation'] = true																		--make group late activation  -- SOL decale 			 : lateActivation + a_activate_group
									group['uncontrolled'] = true																		--Seulement sur CVN, lateActivation and uncontrolled requis

									local BugFrom =  " NbPlanetDeck >= db_airbases[flight[f].base].LimitedParkNb "..debug.getinfo(1).currentline
									SpawnOn( "air", waypoints, group, Pn, spawn_time + 300, BugFrom, flight, f)									
									
									--si le vol postulait pour le sixpack, on le supprime de la table
									table.remove(testSixPack[flight[f].base])
									FlagInsertSixpack = false
									for forTiming, value in pairs(TimingDeckCata[side][flight[f].base]) do
										if value == group.name then
											TimingDeckCata[side][flight[f].base][value] = nil
										end
									end								
								end								
							else
								if not FlagInsertSixpack then																			--les planes qui ne sont pas ajouté dans les catégories précédente, spawn décalé
									if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe FFd  not FlagInsertSixpack ") end
									group['lateActivation'] = true																		--make group late activation  -- SOL decale 			 : lateActivation + a_activate_group
									group['uncontrolled'] = true																		--Seulement sur CVN, lateActivation and uncontrolled requis
								end
							end

							--les Planes qui genent le taxiing spawn selon conf_mod
							if not SpawnDeck then 
								local BugFrom =  " if not SpawnDeck "..debug.getinfo(1).currentline
								SpawnOn( mission_ini.SC_SpawnOn[flight[f].type], waypoints, group, Pn, spawn_time, BugFrom, flight, f)
							end
							
							if LimitedParkTiming or db_airbases[flight[f].base].BaseAirStart then								
								if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe LLLa LimitedParkTiming OR BaseAirStart ") end
								local BugFrom =  " LimitedParkTiming or BaseAirStart "..debug.getinfo(1).currentline
								
								SpawnOn( "air", waypoints, group, Pn, spawn_time + 300, BugFrom, flight, f)
								if FlagInsertSixpack then																			--si le vol postulait pour le sixpack, on le supprime de la table
									table.remove(testSixPack[flight[f].base])
									FlagInsertSixpack = false
									for forTiming, value in pairs(TimingDeckCata[side][flight[f].base]) do
										if value == group.name then
											TimingDeckCata[side][flight[f].base][value] = nil
										end
									end
								end
							end
							
							--au final, Start+Activate si le flight ne spawn pas en vol
							if waypoints[1]["action"] ~= "Turning Point" then
								activate_group_time_after(group, activate_time, debug.getinfo(1).currentline )	-- = - = - = - = -- = - = - = - = - = - = - = - = - = - = --															
								Start_set_ai_task(group, spawn_time, debug.getinfo(1).currentline)			-- = - = - = - = -- = - = - = - = - = - = - = - = - = - = --
							end
							
						elseif   (Multi.NbGroup >= 1 and not camp.MultiPlayer.pack_n[p]) or SingleWithDServerAiAir  then	--en multiplayer: aucun décalage sur le pont, puisque tous les IA commencent en vol								
							if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe GG Multi.NbGroup >= 1") end
							
							group['lateActivation'] = true										--make group late activation 
							group['uncontrolled'] = true										--Seulement sur CVN, lateActivation and uncontrolled requis

							--les Planes qui genent le taxiing spawn selon conf_mod
							if not SpawnDeck then 
								local BugFrom =  " not SpawnDeck "..debug.getinfo(1).currentline
								SpawnOn( mission_ini.SC_SpawnOn[flight[f].type], waypoints, group, Pn, spawn_time + 300, BugFrom, flight, f)
								if FlagInsertSixpack then																			--si le vol postulait pour le sixpack, on le supprime de la table
									table.remove(testSixPack[flight[f].base])
									FlagInsertSixpack = false
									for forTiming, value in pairs(TimingDeckCata[side][flight[f].base]) do
										if value == group.name then
											TimingDeckCata[side][flight[f].base][value] = nil
										end
									end
								end
							end
 							
							--au final, Start+Activate si le flight ne spawn pas en vol
							if waypoints[1]["action"] ~= "Turning Point" then
								activate_group_time_after(group, activate_time, debug.getinfo(1).currentline )	-- = - = - = - = -- = - = - = - = - = - = - = - = - = - = --															
								Start_set_ai_task(group, spawn_time, debug.getinfo(1).currentline)			-- = - = - = - = -- = - = - = - = - = - = - = - = - = - = --
							end
					
						end	

					
						--permet de faire apparaitre sur CVN des planes qui decolleront plus tard, mais qui ont de la place pour apparaitre sur le pont des le début de mission
						--cela habille et occupe le  pont
						-- la decision sera prise en bas, en parsant le tableau testDeckPlace
						if group['route']['points'][1]["type"] ~= "Turning Point" and not FlagInsertSixpack and not SingleWithDServerAiAir then
							if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe GGa  ~= Turning Point and not FlagInsertSixpack") end
								
							tempDeckPlace = {
								time = group['route']['points'][1]["ETA"] ,
								groupName = group.name,
								number = flight[f].number,
								LimitedParkNb = db_airbases[flight[f].base].LimitedParkNb,
								}	

							-- FlagInsertSixpack = true
							if not testDeckPlace[flight[f].base] then testDeckPlace[flight[f].base] = {} end
							table.insert(testDeckPlace[flight[f].base],  tempDeckPlace)	
						end						
						
					------------------	
					--SUR PISTE DUR---
					------------------	
					elseif flight[f].task ~= "Intercept" then 															
						if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe II SUR PISTE DUR") end
						
						if LimitedParkTiming or db_airbases[flight[f].base].BaseAirStart then								
							group['lateActivation'] = true
							group['uncontrolled'] = false
							if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe LLLb LimitedParkTiming OR BaseAirStart ") end
							local BugFrom =  " LimitedParkTiming or BaseAirStart "..debug.getinfo(1).currentline
							SpawnOn( "air", waypoints, group, Pn, spawn_time + 300, BugFrom, flight, f)
						else

							group['uncontrolled'] = true																							--make group uncontrolled						
							group['lateActivation'] = false
							
							Start_set_ai_task(group, spawn_time, debug.getinfo(1).currentline)			-- = - = - = - = -- = - = - = - = - = - = - = - = - = - = --
						end												
					end

				end

				----- provisions for interceptors/GCI/AWACS -----
				if (flight[f].task == "Intercept" and flight[f].player ~= true) then				--and flight[f].client ~= true					
					GCI.Flag = GCI.Flag + 1															--go to next trigger flag number					
					if flight[f].client ~= true or LimitedParkTiming then								-- M11 PVP ne copie pas de trigger retardé START pour les clients/joueurs	

						group['uncontrolled'] = true											--make interceptor groups uncontrolled at mission start
						group['lateActivation'] = false

						--triggered action to start uncontrolled group
						group['tasks'] = {
							[1] = {
								["number"] = 1,
								["name"] = group.name,
								["id"] = "WrappedAction",
								["auto"] = false,
								["enabled"] = true,
								["params"] = {
									["action"] = {
										["id"] = "Start",
										["params"] = {},
									},
								},
							},
						}
						
						--mission trigger to initiate triggered action
						local trig_n = Missionfunc + #mission.trig.funcStartup + 1										--next available trigger number
						Missionfunc = Missionfunc + 1 																	--M11.o
						mission.trig.func[trig_n] = "if mission.trig.conditions[" .. trig_n .. "]() then mission.trig.actions[" .. trig_n .. "]() end"
						mission.trig.flag[trig_n] = true
						mission.trig.conditions[trig_n] = "return(c_flag_is_true(" .. GCI.Flag .. ") )"
						mission.trig.actions[trig_n] = "a_set_ai_task(" .. group.groupId .. ", 1); mission.trig.func[" .. trig_n .. "]=nil;"
						mission.trigrules[trig_n] = {
							['rules'] = {
								[1] = {
									["flag"] = GCI.Flag,
									["predicate"] = "c_flag_is_true",
									["zone"] = "",
								},
							},
							['eventlist'] = '',
							['comment'] = 'Trigger ' .. trig_n,
							['predicate'] = 'triggerOnce',
							['actions'] = {
								[1] = {
									["predicate"] = "a_set_ai_task",
									["set_ai_task"] = {
										[1] = group.groupId,
										[2] = 1,
									}
								},
							},
						}
						
						--if the group is on a carrier, it gets late activation instead of uncontrolled. An activate trigger is needed instead of AI task trigger.
						-- Les inter sur CVN et parking limité spawn en vol
						if db_airbases[flight[f].base].unitname or LimitedParkTiming or db_airbases[flight[f].base].BaseAirStart then
							
							local BugFrom =  " IA intercept "..debug.getinfo(1).currentline
							SpawnOn( "air", waypoints, group, Pn, 0, BugFrom, flight, f)
							
							group['lateActivation'] = true											--make group late activation "en vol"
							group['uncontrolled'] = false
							group['tasks'] = {}
							
							mission.trig.actions[trig_n] = "a_activate_group(" .. group.groupId .. "); mission.trig.func[" .. trig_n .. "]=nil;"
							mission.trigrules[trig_n]['actions'][1] = {
								["group"] = group.groupId,
								["predicate"] = "a_activate_group",	
							}
															
							if debugStart then debugTxt = debugTxt.."\n"..("AtoFP passe activate 03") end
						end
					end
					
					
					
					--build Interceptor table
					local t = {
						name = group.name,
						number = #group.units,
						range = flight[f].target.radius,
						x = group.x,
						y = group.y,
						flag = GCI.Flag,
						tot_from = flight[f].tot_from,
						tot_to = flight[f].tot_to,
						airdromeId = flight[f].airdromeId,
						time = -900
					}
					
					if GCI.Interceptor[side].base[flight[f].base] == nil then
						GCI.Interceptor[side].base[flight[f].base] = {
							ready30 = {},
							ready15 = {},
							ready15_n = 0,
							ready = {},
							ready_n = 0,
						}
					end
					
					if flight[f].player == true or flight[f].client == true then										-- M11 multiplayer, les joueurs sont ajouté dans la base ready pour ne pas attendre 
						table.insert(GCI.Interceptor[side].base[flight[f].base].ready, t)
						GCI.Interceptor[side].base[flight[f].base].ready_n = GCI.Interceptor[side].base[flight[f].base].ready_n + 1
					elseif #GCI.Interceptor[side].base[flight[f].base].ready == #GCI.Interceptor[side].base[flight[f].base].ready15 and #GCI.Interceptor[side].base[flight[f].base].ready == #GCI.Interceptor[side].base[flight[f].base].ready30 then
						table.insert(GCI.Interceptor[side].base[flight[f].base].ready, t)
						GCI.Interceptor[side].base[flight[f].base].ready_n = GCI.Interceptor[side].base[flight[f].base].ready_n + 1
					elseif #GCI.Interceptor[side].base[flight[f].base].ready15 == #GCI.Interceptor[side].base[flight[f].base].ready30 then
						table.insert(GCI.Interceptor[side].base[flight[f].base].ready15, t)
						GCI.Interceptor[side].base[flight[f].base].ready15_n = GCI.Interceptor[side].base[flight[f].base].ready15_n + 1
					else
						table.insert(GCI.Interceptor[side].base[flight[f].base].ready30, t)
					end
					
					
				elseif flight[f].task == "AWACS" then
					GCI.EWR[side][units[1].name] = true											--add AWACS to EWR table
				end
				

				-- si multijoueur, les Flight AI commencent en vol + M11.j
				if ( (Multi.NbGroup >= 1 or SingleWithDServerAiAir) and flight[f].player ~= true and flight[f].client ~= true and string.find(flight[f].base,"CVN") and flight[f].task ~= "Intercept") then
					if  waypoints[1]["type"] ~= "Turning Point" then 					-- si le vol a deja ete deplace pour un commencement en vol, on ne recommence pas le d�calage lat�ral
						local BugFrom =  " si multijoueur, les Flight AI commencent en vol "..debug.getinfo(1).currentline
						-- SpawnOn( "air", waypoints, group, Pn, spawn_time + 300, BugFrom, flight, f)	
						SpawnOn( "air", waypoints, group, Pn, spawn_time, BugFrom, flight, f)	
					end

					
				elseif (flight[f].type == 'F-14B' or flight[f].type == 'FA-18C_hornet') and flight[f].client 
					and string.find(flight[f].base,"CVN") and flight[f].task ~= "Intercept" then
					
					if not waypoints[1]['linkUnit'] then waypoints[1]['linkUnit'] = waypoints[#waypoints]['linkUnit'] end
					if not waypoints[1]['helipadId'] then waypoints[1]['helipadId'] = waypoints[#waypoints]['helipadId'] end
					
				end

				-- modification Miguel M17
				-- Player Flight : Multi.NbGroup >= 1, si 4 F-14, on le force � moins de 4 pour �viter les collisions
				if flight[f].type == 'F-14B'  and flight[f].player == true and flight[f].number > limiteNbF14CVN  and string.find(flight[f].base,"CVN") then
					for nb = flight[f].number ,limiteNbF14CVN +1, -1 do
						table.remove(units, nb)
					end
					flight[f].number = limiteNbF14CVN
					flight[f].NbPlaneClient = limiteNbF14CVN
				end

				
				if (db_airbases[flight[f].base].unitname or db_airbases[flight[f].base].helipadId) and group['route']['points'][1]["type"] ~= "Turning Point" then	-- and waypoints[1]["type"] ~= "Turning Point"
					-- initie et place dans la table placePA les horaires "esperés" de catapultage
					if not placePA[side] then placePA[side] = {} end
					if not placePA[side][flight[f].base] then placePA[side][flight[f].base] = {} end
					
					local EPlayer = "."
					if	flight[f].player == true then EPlayer = " - Player" end
					if	flight[f].client == true then EPlayer = " - Client" end
					
					-- local etiquette = "Pack " .. p .. " - "..flight[f].number.." "..flight[f].type.. " - " .. flight[f].name .." - " .. flight[f].task .." ".. f.. EPlayer.." spawn_time: "..spawn_time
					local etiquette = "Pack " .. p .. " - "..flight[f].number.." "..flight[f].type.. " - " .. flight[f].name .." - " .. flight[f].task .." ".. f.. EPlayer
					
					local testST =  spawn_time	- 120						--	+ 200					-- ajoute 200s, cela correspond au roulage apres activatin (donc demarrage)													
					if not testST then testST = 0 end
					
					--todo fini l'ordre de décollage sur cata
					repeat
						testST = testST + 1 
					until not placePA[side][flight[f].base][testST] 
					
					-- etiquette = etiquette .." HcvN: "..testST
					
					placePA[side][flight[f].base][testST] = etiquette
					
				end
				
				
				if SinglePlayer and flight[f].player and not SingleWithDServer then									--if this is the player flight
				-- Eagle_01 Modification E02.a												--Make Flight Lead an AI
					if flight[f].type == 'I-16' or flight[f].type == 'A-4E-C' then			--Compensate for Unit without a radio so AI in flight will automatically attack targets
						units[1]["skill"] = "Excellent"
						units[2]["skill"] = "Client"
					else
						units[1]["skill"] = "Player"										--make first aircraft in flight the player aircraft
					end																		--make first aircraft in flight the player aircraft
				
				-- Miguel21 modification M11.l : Multiplayer	
				elseif flight[f].client or flight[f].player and not SingleWithDServer then
					for i=1, flight[f].NbPlaneClient do
						units[i]["skill"] = "Client"
					end
					waypoints[1].ETA = 0													-- Place l'heure d'apparition au lancement de mission, pour avoir plus de temps...^^	
					waypoints[1]["type"] = "TakeOffParking"
					waypoints[1]["action"] = "From Parking Area"
				
				elseif SingleWithDServer and flight[f].player then
					units[1]["skill"] = "Client"
				
				end
				
				if type(units[1].callsign) == "number" then										--Russian style
					ATO[side][p][role][f].callsign = units[1].callsign							--store flight callsign in ATO
				else																			--NATO style
					ATO[side][p][role][f].callsign = units[1].callsign.name						--store flight callsign in ATO									
				end
				
				ATO[side][p][role][f].frequency = group.frequency								--store package frequency in ATO
				
				--M11.r ajoute une copie des avions multijoueur commançant en l'air
				local groupRTB = {}
				if mission_ini.MP_PlaneRecovery and Multi.NbGroup >= 1 and (flight[f].client or flight[f].player) then	
					groupRTB = deepcopy(group)
					groupRTB.groupId = GenerateID()
					if 	groupRTB.route.points[3] and groupRTB.route.points[3] then 
						groupRTB.route.points[1] = groupRTB.route.points[3]
						groupRTB.route.points[2] = groupRTB.route.points[3]
						groupRTB.name = "Recovery "..groupRTB.name
						
						for i=1 , #groupRTB.units do
							local unitId_ = GenerateID()
							groupRTB.units[i].payload.fuel = groupRTB.units[i].payload.fuel * 0.70
							groupRTB.units[i].name = "Recovery "..groupRTB.units[i].name
							groupRTB.units[i].unitId = unitId_
							
							groupRTB.units[i].x = groupRTB.route.points[1].x
							groupRTB.units[i].y = groupRTB.route.points[1].y
							
						end
					end
				end
				
				-- Miguel21 modification M33.e 	Custom Briefing (e: Divert/CVN possible)
				-- place dans une table les bases proches des WPT
				local TabBaseByWPT = {}
				if flight[f].player or flight[f].client then
					for n = 1, #waypoints   do
						for airbase, value in pairs(db_airbases) do							
							if  (not value.inactive or value.inactive == false) and value["side"] == side and flight[f].base ~= airbase then		--value.divert and					
								local distance = GetDistance(waypoints[n], value )
								if flight[f].type ~= AV8BNA and not flight[f].helicopter then								
									if  not flight[f].helipadId and not string.find(airbase, "LHA") then							
										if not TabBaseByWPT[n] then TabBaseByWPT[n] = {} end
										if not TabBaseByWPT[n]["dist"] then TabBaseByWPT[n]["dist"] = 9999999 end
										if not TabBaseByWPT[n]["baseName"] then TabBaseByWPT[n]["baseName"] = "" end
										
										if distance < TabBaseByWPT[n]["dist"] then
											TabBaseByWPT[n]["dist"] = distance
											TabBaseByWPT[n]["baseName"] = airbase
										end	
									end
								else
									if not TabBaseByWPT[n] then TabBaseByWPT[n] = {} end
									if not TabBaseByWPT[n]["dist"] then TabBaseByWPT[n]["dist"] = 9999999 end
									if not TabBaseByWPT[n]["baseName"] then TabBaseByWPT[n]["baseName"] = "" end
									
									if distance < TabBaseByWPT[n]["dist"] then
										TabBaseByWPT[n]["dist"] = distance
										TabBaseByWPT[n]["baseName"] = airbase
									end	
								end
							end
						end
					end															
					
					-- creer une table en evitant les doublons
					for wp, TabBase in pairs(TabBaseByWPT) do																	
						
						if not tabDivert then tabDivert = {} end
						if not tabDivert["player"] then tabDivert["player"] = {} end
						if not tabDivert["player"]["pack"] then tabDivert["player"]["pack"] = {} end							
						if not tabDivert["player"]["pack"][role] then tabDivert["player"]["pack"][role] = {} end							
						if not tabDivert["player"]["pack"][role][f] then tabDivert["player"]["pack"][role][f] = {} end								
						if not tabDivert["player"]["pack"][role][f].base then tabDivert["player"]["pack"][role][f].base = {} end
						
						if not tabDivert["player"]["pack"][role][f].base[TabBase.baseName] then
							tabDivert["player"]["pack"][role][f].base[TabBase.baseName] = TabBase.baseName 
						end					
					end
					
				end
				
				------ add group to mission -----
				local foundCountry = false
				for c = 1, #mission.coalition[side].country do
					if mission.coalition[side].country[c].name == flight[f].country then
						if flight[f].helicopter ~= true then
							if mission.coalition[side].country[c].plane == nil then
								mission.coalition[side].country[c].plane = {
									group = {}
								}
							end
							table.insert(mission.coalition[side].country[c].plane.group, group)
							foundCountry = true
							if flight[f].player == true then										
								camp.player.group = mission.coalition[side].country[c].plane.group[#mission.coalition[side].country[c].plane.group]		--store a link to the player group in mission
							-- Miguel21 modification M11B. : Multiplayer--briefing	
							elseif flight[f].client == true then										
								camp.client[flight[f].IdClient].group = mission.coalition[side].country[c].plane.group[#mission.coalition[side].country[c].plane.group]		--store a link to the player group in mission
								-- camp.client[flight[f].IdClient].group["divert"] = tabDivert
							end
							
							if groupRTB.groupId then
								table.insert(mission.coalition[side].country[c].plane.group, groupRTB)
							end
						else
							if mission.coalition[side].country[c].helicopter == nil then
								mission.coalition[side].country[c].helicopter = {
									group = {}
								}
							end
							table.insert(mission.coalition[side].country[c].helicopter.group, group)
							foundCountry = true
							if flight[f].player == true then										
								camp.player.group = mission.coalition[side].country[c].helicopter.group[#mission.coalition[side].country[c].helicopter.group]		--store a link to the player group in mission
							-- Miguel21 modification M11B. : Multiplayer--briefing	
							elseif flight[f].client == true then										
								camp.client[flight[f].IdClient].group = mission.coalition[side].country[c].helicopter.group[#mission.coalition[side].country[c].helicopter.group]		--store a link to the player group in mission
							end
							if groupRTB.groupId then
								table.insert(mission.coalition[side].country[c].helicopter.group, groupRTB)
							end
						end
					end
				end
								
				-- CHCM_FP_01 Check and Help CampaignMaker 
				if not foundCountry then
					print()
					print("********************ATTENTION******************")
					print("**** Note for the Campaign Maker: Impossible to add "..flight[f].type.."  in the mission, since this country: "..flight[f].country.." side: "..side.."  is not in the base_mission file. **********")
					print("********************ATTENTION******************")
					print()
					os.execute 'pause'
				end
				
				
				-- if Debug.AfficheFlight then 
				
				local debugTempFLIGHT = ""
				idSol = "SolRIEN"
				local ETA = -1
				local NbEta = "ETA "
				-- local WT = ""

				if spawn_time ~= nil then
					ETA = spawn_time
				end
				
				local info01 = ""
				local info02 = ""
				local info03 = ""
				local info04 = ""
				local info05 = ""
				local info06 = ""
				
				
				-- if waypoints[1].action then
					-- info01 = "info01 "..waypoints[1].alt
				-- end
				
				local a_activate = false
				local a_activate2 = false
				local a_set_ai_task = false
				local c_time = false
				local c_flag = false
				local testtrigrule = {}
				local activateSecondes = 999999
				local nbactivate = 0
				for n , trigrule in pairs(mission.trigrules) do
					if type(trigrule) == "table" then	
						if trigrule.actions and trigrule.actions[1] and trigrule.actions[1].group == group.groupId then
							
							if trigrule.actions[1]["predicate"] == "a_activate_group" then
								nbactivate = nbactivate + 1
								
								a_activate = true
								testtrigrule = trigrule
								if trigrule.rules[1].predicate == "c_time_after" then
									-- print("AtoFp passe rulesSeconds "..activateSecondes)
									activateSecondes = math.floor(trigrule.rules[1].seconds)
									c_time = true
								elseif trigrule.rules[1].predicate == "c_flag_is_true" then
									c_flag = true
								end
							end

						end
						if trigrule.actions and trigrule.actions[1] and trigrule.actions[1].set_ai_task and trigrule.actions[1].set_ai_task[1] == group.groupId then
							if trigrule.actions[1]["predicate"] == "a_set_ai_task" then
								a_set_ai_task = true
								testtrigrule = trigrule
								if trigrule.rules[1].predicate == "c_time_after" then
									-- print("AtoFp passe rulesSeconds "..activateSecondes)
									activateSecondes = math.floor(trigrule.rules[1].seconds)
									c_time = true
								elseif trigrule.rules[1].predicate == "c_flag_is_true" then
									c_flag = true
								end
							end
						end
					end
				end
				
				if nbactivate > 1 then
					info06 = info06.." |+|ATTENTION plusieurs ACTIVATE "
				end
				-- print("AtoFp passeb rulesSeconds "..activateSecondes)
				
				if group.tasks and group.tasks[1] and group.tasks[1].params.action.id == "Start" then					
					if not group.uncontrolled then
						info01 = "ATTENTION MANQUE uncontrolled "..group.groupId
					end						
					if waypoints[1].action == "Turning Point" then
						info01 = info01.." |+|ATTENTION Start en VOL "
					end						
				end

				if spawn_time and waypoints[1].action == "Turning Point" and spawn_time > 10 then										
					for n , trigrule in pairs(mission.trigrules) do
						if type(trigrule) == "table" then	
							if trigrule.actions and trigrule.actions[1] and trigrule.actions[1].group == group.groupId then									
								if trigrule.actions[1]["predicate"] == "a_activate_group" then		
									a_activate2 = true
								end
							end
						end
					end
					if not a_activate2 then
						info01 = info01.." |+|ATTENTION VOL sans  a_activate_group "
					end
				end

				
				if group.uncontrolled then
					if group.tasks and group.tasks[1] and group.tasks[1].params.action.id == "Start" then	
						if a_set_ai_task then
							if c_time then
								info02 = "SOL/VOL decale_A "..activateSecondes
								-- if activateSecondes == math.floor(ETA)   then 
									-- info02 = "SOL/VOL decale_A "..activateSecondes
								-- else
									-- info02 = info02.." |ATTENTION SECONDES Diff a_activate_group "..activateSecondes
								-- end
							elseif c_flag then								
								info02 = info02.." |VOL decale_B"
							else
								_affiche(testtrigrule, "testtrigrule")
							end
						else 
							info02 = info02.." |ATTENTION MANQUE a_set_ai_task: aucun demarrage possible "..group.groupId							
						end
					else 
						info02 = info02.." |ATTENTION MANQUE Start "..group.groupId						
					end
				end

				
				if group.lateActivation then
					if a_activate then
						if c_time then
							if activateSecondes == math.floor(ETA)   then 
								info03 = "SOL/VOL decale_A"
							else
								info03 = "ATTENTION SECONDES a_activate_group "..group.groupId
							end
						elseif c_flag then								
							info03 = "VOL FLAG decale _B"
						else
							_affiche(testtrigrule, "testtrigrule")
						end
					else 
						info03 = "ATTENTION MANQUE a_activate_group "..group.groupId						
					end
				end
				
				-- if a_set_ai_task then
					-- if a_activate then
					
					-- else
						-- info02 = info02.." __ATTENTION_PRESENT__"
					-- end
				-- end
				
				-- if a_activate then
					-- if a_set_ai_task then
						-- info02 = info02.." __INvisible_Avec_Start"
					-- else
						-- info02 = info02.." __INvisible_Sans_Start"
					-- end
				-- end
				
				if waypoints[1]["linkUnit"] then
				
					-- info04 = "linkUnit "..waypoints[1]["linkUnit"]
				
				end
				if waypoints[1]["helipadId"] then
				
					-- info04 = info04.." helipadId "..waypoints[1]["helipadId"]
				
				end	
				
				for i = 1, #units do
					if units[i]["parking_id"] then 
					
						-- info05 = info05.." "..units[i]["parking_id"]
						
					end												
				end
				
				
				
				
				if units[1].skill == "Player" or units[1].skill == "Client" then					
					debugTempFLIGHT = debugTempFLIGHT.."\n"..("= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ")
					debugTempFLIGHT = debugTempFLIGHT.."\n"..("= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ")						
				end
				
				local groupInfo = ""
				if debugStart then
					groupInfo = info01
					.." "..info02
					.." "..info03
					.." "..info04
					.." "..info05
					.." "..info06
				end
				
				debugTempFLIGHT = debugTempFLIGHT.."\n"..("Pack: "..p.." Nb "
					.."  "..flight[f].number
					.."  "..flight[f].type
					.."  "..group.name
					.."  "..flight[f].base
					.."  "..flight[f].target_name					
					.."  "..NbEta.. math.floor(ETA)
					.."  ".."StartT: "..tostring(math.floor(group.start_time))
					.."  ".."EtaWPT: "..tostring(math.floor(group['route']['points'][1]["ETA"]))
					.."  ".." // "..units[1].skill
					-- .."  ".."Acti: "..tostring(group['route']['points'][1]["action"])
					.."  ".."Type: "..tostring(group['route']['points'][1]["type"])
					-- .."  unCont: "..tostring(group.uncontrolled)
					-- .."  lateA: "..tostring(group.lateActivation)
					
					-- .."  ".." // "..group.frequency
					
					-- .." UAlt ".." // "..units[1].alt
					-- .." WAlt ".." // "..info01
					.." "..groupInfo
					)
					
				-- for nn = 1 , #units do
					-- debugTxt = debugTxt.."\n"..("\n")						
					-- debugTxt = debugTxt.."\n"..(" / ".. units[nn].onboard_num )
					-- debugTxt = debugTxt.."\n"..(" / ".. units[nn].livery_id )
				-- end
				
				if units[1].skill == "Player" or units[1].skill == "Client" then
					debugTempFLIGHT = debugTempFLIGHT.."\n"..("= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ")
					debugTempFLIGHT = debugTempFLIGHT.."\n"..("= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ")						
				end
				
				
				
				debugTempFLIGHT = debugTempFLIGHT.."\n"..("\n")
				
				debugFLIGHT = debugFLIGHT .. debugTempFLIGHT
				debugTxt = debugTxt .. debugTempFLIGHT
				
				-- end
			end
		end
	end
end

function AF_spawnOn(where, groupName)
	if debugStart then debugTxt = debugTxt.."\n"..("AtoFp AF_spawnOn  "..groupName) end
	
	if where == "catapult" then
		Action = 'From Runway'
		Type = 'TakeOff'
	end
			
	for _side,side in pairs(mission.coalition) do	
		for _country,country in pairs(side.country) do
			if country.plane then
				for Ngroup,group in pairs(country.plane.group) do
					if group.name ==  groupName then
						group.route.points[1]['action'] = Action
						group.route.points[1]['type'] = Type
						group['route']['points'][1]["ETA"] = 0
						group['uncontrolled'] = false
						if debugStart then debugTxt = debugTxt.."\n"..("AtoFp AF_spawnOn Find "..group.units[1].type.." "..group.name.." "..group.route.points[1]['type']) end	
					end
				end
			elseif country.helicopter  then
				for Ngroup,group in pairs(country.helicopter.group) do
					if group.name ==  groupName then
						group.route.points[1]['action'] = Action
						group.route.points[1]['type'] = Type
						group['route']['points'][1]["ETA"] = 0
						group['uncontrolled'] = false
						if debugStart then debugTxt = debugTxt.."\n"..("AtoFp AF_spawnOn Find "..group.units[1].type.." "..group.name.." "..group.route.points[1]['type']) end	
					end
				end
			end
		end
	end
end

--nombre d'avion UNIQUEMENT sur le SIXPACK
local sommePlane = {} 
for CVN, SixPack in pairs(testSixPack) do	
	
	if table.getn(SixPack) > 0 then

		table.sort(SixPack, function(a,b) return a.time < b.time  end)
		if debugStart then debugTxt = debugTxt.. _afficheTXT(SixPack, "SixPack") end	
		
		local breakloop = false	
		sommePlane[CVN] = 0
		local n = 1
		repeat
			
			if debugStart then debugTxt = debugTxt.."\n"..("n: "..n) end	
			
			local sixpackWiner = SixPack[n]["groupName"]
			
			--affiche la note concernant le joueur:
				-- s'il est sur le Sixpack ET serveur dédié : commencer serveur sur pause
				-- s'il n'est pas sur sixpack ET serveur dédié: commencer serveur en resume
			
			
			sommePlane[CVN] = 4													-- par defaut, le sixpack ne pourra etre utiliser à posteriorie, donc on estime que les 4 places sont occupé, cela evite les spawn derriere et le manque de place ensuite, sur tout le pont

			for _side,side in pairs(mission.coalition) do	
				for _country,country in pairs(side.country) do
					if country.plane then
						for Ngroup,group in pairs(country.plane.group) do
							if group.name ==  sixpackWiner then
								if group.units[1].type == "S-3B Tanker" or group.units[1].type == "E-2C"  then						-- cet endroit est bloqué par DCS pour ces 2 avions
									AF_spawnOn("catapult", group.name)
									modify_activate_group_time(group, -1, debug.getinfo(1).currentline)								--supprime le triger activate
									modify_set_ai_task(group, -1, debug.getinfo(1).currentline)										--supprime le triger start
									group['tasks'] = {}
									break
								end
								group['route']['points'][1]["ETA"] = 0
								group['start_time'] = 0
								modify_activate_group_time(group, -1, debug.getinfo(1).currentline)								--supprime le triger activate
								if debugStart then debugTxt = debugTxt.."\n"..("AtoFp SixPack Find "..group.name) end	
								breakloop = true
								
							end
						end
					elseif country.helicopter  then
						for Ngroup,group in pairs(country.helicopter.group) do
							if group.name ==  sixpackWiner then
								group['route']['points'][1]["ETA"] = 0
								group['start_time'] = 0
								modify_activate_group_time(group, -1, debug.getinfo(1).currentline)								--supprime le triger activate
								if debugStart then debugTxt = debugTxt.."\n"..("AtoFp SixPack Find "..group.name) end	
								breakloop = true
								
							end
						end
					end
				end
			end
			
			if breakloop or n > table.getn(SixPack) then									
				if SixPack[n]["client"] and SingleWithDServer  then	-- and not SingleWithDServerAiAir
					print()
					print("********************ATTENTION******************")
					print()
					print("        You MUST set the server to PAUSE")
					print("          (to appear on the SIXPACK) ")
					print()
					print("********************ATTENTION******************")
					print()
					os.execute 'pause'

					
				elseif  SingleWithDServer then	-- and not SingleWithDServerAiAirthen	
					
					print()
					print("*****************************************ATTENTION***************************************************")
					print()
					print("				  You MUST set the server to RESUME ")
					print()
					print("(so that you don't appear on the Sixpack, you'd be annoying the AIs that will be driving before you) ")
					print()
					print("*****************************************ATTENTION***************************************************")
					print()
					os.execute 'pause'
				end
			end
			
			n = n +1 
		until breakloop or n > table.getn(SixPack)
	end
end

if debugStart then debugTxt = debugTxt.. _afficheTXT(testDeckPlace, "testDeckPlace") end

-- nombre d'avion sur le pont total
-- limite le nombre d'avion sur le pont (permet de faire apparaitre les avions tardif, s'il y a de la place)
for CVN, deck in pairs(testDeckPlace) do	
	
	if table.getn(deck) > 0 then

		table.sort(deck, function(a,b) return a.time < b.time  end)
		if debugStart then debugTxt = debugTxt.. _afficheTXT(deck, "testDeckPlace deck") end	
		
		if testSixPack[CVN] and table.getn(testSixPack[CVN]) > 0 then
			
			--cherche une place dispo sur le deck pour les avions tardif
			local counter = 0
			local testSomme = 0
			for n = 1 , #deck do 
				repeat
					counter = counter +1

					local DeckWiner = deck[n]["groupName"]		
	
					if not deck[n]["LimitedParkNb"] then
						break
					else
						--enleve les 4 places du Sixpack
						--et aussi le nombre de place du pack client/joueur
						LimitedDeckNb  = deck[n]["LimitedParkNb"] - 4 - NbPlanetDeck
					end
					
					if debugStart then debugTxt = debugTxt.."\n"..("AtoFp DeckWiner "..DeckWiner) end						
					if debugStart then debugTxt = debugTxt.."\n"..("AtoFp DeckWiner "..tostring(deck[n]["number"]) .." |LimitedDeckNb: "..tostring(LimitedDeckNb)) end
					
					testSomme = testSomme + deck[n]["number"]
					if debugStart then debugTxt = debugTxt.."\n"..("AtoFp testSomme "..testSomme) end	
					if testSomme <= LimitedDeckNb and not deck[n]["OnDeck"] then
						for _side,side in pairs(mission.coalition) do	
							for _country,country in pairs(side.country) do
								if country.plane then
									for Ngroup,group in pairs(country.plane.group) do
										if group.name ==  DeckWiner then
											group['uncontrolled'] = true				
											group['lateActivation'] = true
											modify_activate_group_time(group, 2, debug.getinfo(1).currentline)
											sommePlane[CVN] = sommePlane[CVN] + tonumber(deck[n]["number"])
											deck[n]["OnDeck"] = true
											if debugStart then debugTxt = debugTxt.."\n"..("AtoFp DeckWiner Find "..group.name.." +number: "..deck[n]["number"]) end												
										end
									end
								elseif country.helicopter  then
									for Ngroup,group in pairs(country.helicopter.group) do
										if group.name ==  DeckWiner then
											group['uncontrolled'] = true				
											group['lateActivation'] = true
											modify_activate_group_time(group, 2, debug.getinfo(1).currentline)
											sommePlane[CVN] = sommePlane[CVN] + tonumber(deck[n]["number"])
											deck[n]["OnDeck"] = true
											if debugStart then debugTxt = debugTxt.."\n"..("AtoFp DeckWiner Find "..group.name.." +number: "..deck[n]["number"]) end
										end
									end
								end
							end
						end
					end
					 
				until sommePlane[CVN] >= LimitedDeckNb or counter >= 2
			end
		end
	end
end

if debugStart then 
	-- affiche  le timing des avions sur le pont/catapulte pour prévenir le/les joueurs que des IA seront dessus
	local tabNam = {}
	debugTxt = debugTxt.."\n"..("AtoFP startup_time_player: " ..FormatTime(mission_ini.startup_time_player, "hh:mm"))
	debugTxt = debugTxt.."\n"..("AtoFP NowTime: " ..FormatTime(camp.time, "hh:mm"))

	print("\n")
	if placePA and camp.player then
		for side , pPA in pairs(placePA) do	
			if camp.player.side == side then
				for base , Tmn in pairs(pPA) do	
					debugTxt = debugTxt.."\n"..(tostring(base).." Takeoff time on the platform at ...")
					for s, name in pairsByKeys(Tmn) do
						
						if tabNam[name] ~= true then
							catTime = camp.time + s
							debugTxt = debugTxt.."\n"..(" "..FormatTime(catTime, "hh:mm").. " - "..tostring(name).."\n")
							tabNam[name] = true
						end
					end
				end
			end
		end
	end
end		
----- make a copy of player package for easy reference in briefing -----
local breakloop = false
if camp.player then
	camp.player.pack = deepcopy(ATO[camp.player.side][camp.player.pack_n])
	
	--for multi-package strikes, add flights from other packages with the same target to player package to enrich the briefiing
	for p = 1, #ATO[camp.player.side] do										--iterate through packages in player side	
		for role,flight in pairs(ATO[camp.player.side][p]) do					--iterate through roles in package (main, SEAD, escort)		
			for f = 1, #flight do												--iterate through flights in roles
				if flight[f].target_name == camp.player.target.TitleName and camp.player.pack_n ~= p then	--flights that have the same target as player but are not in the player package
					table.insert(camp.player.pack[role], deepcopy(flight[f]))							--insert flight into player package to list it in player briefing
				end	
				if flight[f].player or flight[f].client then
					-- Miguel21 modification M33.b 	Custom Briefing (onBoardNum)
					if flight[f].target_name == camp.player.target.TitleName and camp.player.pack_n == p and not breakloop then
						for _side,side in pairs(mission.coalition) do	
							for _country,country in pairs(side.country) do
								if country.plane and _side == camp.player.side then
									for Ngroup,group in pairs(country.plane.group) do
										if group.units and ( group.units[1].skill == "Player" or group.units[1].skill == "Client" ) then
											camp.player.pack[role][f].units = group.units
											if tabDivert and tabDivert["player"] then
												camp.player.pack[role][f]["divert"] = tabDivert["player"]["pack"][role][f].base
											end
											breakloop = true
										end
									end
								elseif country.helicopter and _side == camp.player.side then
									for Ngroup,group in pairs(country.helicopter.group) do
										if group.units and ( group.units[1].skill == "Player" or group.units[1].skill == "Client" ) then
											camp.player.pack[role][f].units = group.units
											if tabDivert and tabDivert["player"] then
												camp.player.pack[role][f]["divert"] = tabDivert["player"]["pack"][role][f].base
											end
											breakloop = true
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


-- Miguel21 modification M11B. : Multiplayer--briefing	
if camp.client then
	for i = 2, Multi.NbGroup do
		camp.client[i].pack = deepcopy(ATO[camp.client[i].side][camp.client[i].pack_n])
	end
end

local function ShipFindByName(name)		
	for coal_name,coal in pairs(oob_ground) do												--go through sides(red/blue)	
		for country_n,country in ipairs(coal) do											--go through countries
			if country.ship then															--country has ships
				for group_n,group in ipairs(country.ship.group) do							--go through groups
					for n = 1, #group.units do												--ship group found
						if name == group.units[n].name then
							return group.units[n]
						end
					end
				end
			end
		end
	end
end


-- miguel21 modification M40 : Pedro Helicopter
-- Place les Pedro au demarrage de la mission sur le pont, alors qu'en Base_mission il est place sur le cote du CVN en vol
if ( mission_ini.SC_SpawnOn["Pedro"] == "deck" or mission_ini.SC_SpawnOn["Pedro"] == "catapult") and PlayerTask ~= "Intercept"  then
	local TabPedro			
	for coalition_name,coal in pairs(mission.coalition) do
		for country_n,country in pairs(coal.country) do
			if country.helicopter then
				for group_n,group in pairs(country.helicopter.group) do
					for w = 1, #group.units do																		--iterate through all group waypoints														
						-- if group.units[w].name and dictionary[group.units[w].name] and string.gsub(dictionary[group.units[w].name], "Pedro_", "") then
						if group.units[w].name and group.units[w].name and string.gsub(group.units[w].name, "Pedro_", "") then		--M45
							-- local PedroName = dictionary[group.units[w].name]
							local PedroName = group.units[w].name																	--M45
							if string.find(PedroName, "Pedro_") then
								
								local StringShipName = string.gsub(PedroName, "Pedro_", "")
								local Ship_unit = ShipFindByName(StringShipName)

								group.units[w]['linkUnit'] = Ship_unit.unitId
								group.route.points[1]['linkUnit'] = Ship_unit.unitId
								group.route.points[1]['helipadId'] = Ship_unit.unitId
								
								if  mission_ini.SC_SpawnOn["Pedro"] == "catapult" then
									group.route.points[1]['action'] = 'From Runway'
									group.route.points[1]['type'] = 'TakeOff'
									group.route.points[1]["alt"] = 0
								elseif  mission_ini.SC_SpawnOn["Pedro"] == "deck" then
									group.route.points[1]['action'] = 'From Parking Area'
									group.route.points[1]['type'] = 'TakeOffParking'
									-- group.route.points[1]["action"] = "From Parking Area Hot"
									-- group.route.points[1]["type"] = "TakeOffParkingHot"
									-- group.units[w]["parking"] = 1
									-- group.units[w]["parking_id"] = 1
									-- group.uncontrolled = false											-- sur cata, les F14 IA bloquent
								end
							end							
						end
					end
				end
			end
		end
	end
end

-- Miguel21 modification M18.c despawn/destroy Plane on BaseAirStart
camp.BaseAirStart = tempBaseAirStart

-- local debugTxt = debugTxt
local debugGenMFile = io.open("Debug/debugGenMission.txt", "w")										--open targetlist file
debugGenMFile:write(debugTxt)																		--save new data
debugGenMFile:close()

local debugFLIGHTFile = io.open("Debug/debugFlight.txt", "w")										--open targetlist file
debugFLIGHTFile:write(debugFLIGHT)																		--save new data
debugFLIGHTFile:close()


-- _affiche(tabDivert, "tabDivert")
-- _affiche(TabLPark)

-- local camp_str = "trigrules = " .. TableSerialization(mission.trigrules, 0)						--make a string
-- local campFile = io.open("Debug/AtoFP__mission.trigrules.lua", "w")								--open targetlist file
-- campFile:write(camp_str)															--save new data
-- campFile:close()



-- local camp_str = "db_airbases = " .. TableSerialization(db_airbases, 0)						--make a string
-- local campFile = io.open("Debug/db_airbases___AtoFP.lua", "w")								--open targetlist file
-- campFile:write(camp_str)															--save new data
-- campFile:close()



-- _affiche(package_freq, "ATO_FP package_freq")

-- local camp_str = "Trig_AtoFP = " .. TableSerialization(mission.trig, 0)						--make a string
-- local campFile = io.open("Debug/AtoFP__Trig_ATO.lua", "w")								--open targetlist file
-- campFile:write(camp_str)															--save new data
-- campFile:close()

-- local camp_str = "camp_AtoFP = " .. TableSerialization(camp, 0)						--make a string
-- local campFile = io.open("Debug/camp_AtoFP_FINAL.lua", "w")								--open targetlist file
-- campFile:write(camp_str)															--save new data
-- campFile:close()

-- local camp_str = "mission_AtoFP = " .. TableSerialization(mission, 0)						--make a string
-- local campFile = io.open("Debug/mission_AtoFP.lua", "w")								--open targetlist file
-- campFile:write(camp_str)															--save new data
-- campFile:close()
