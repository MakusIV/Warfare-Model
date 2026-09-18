--To evaluate the DCS debrief.log, update the campaign status files/OOBs, generate a debriefing and initiate generation of next campaign mission
--Initiated by MissionEnd.lua running from within DCS
-------------------------------------------------------------------------------------------------------

if not versionDCE then 
	versionDCE = {} 
end

               -- VERSION --

versionDCE["DEBRIEF_Master.lua"] = "OB.1.0.0"

---------------------------------------------------------------------------------------------------------
-- Old_Boy rev. OB.1.0.1: implements compute firepower code
-- Old_Boy rev. OB.1.0.0: implements logging code
-- Old_Boy rev. OB.0.0.0: implements supply line sistems (logistics)
-- adjustment A01.b : robust form
-- debug01.b EndMission
-- miguel21 modification M47.c keeps the history of the campaign files (c: save debugging information during mission generation)
-- miguel21 modification M46.d  singlePlayer with dedicated server (c: DF choice)(c: D choice with AI AirSpawn)
-- Miguel21 modification M35.d version ScriptsMod + camp
-- Miguel21 modification M14 : Versionning
-- Miguel21 modification M11.q : Multiplayer (q: displays all tasks of several squadrons)
--
-- NOTE MARCO:
-- le righe di codice da analizzare, verificare o correggere le identifico con la parola chiave -- VERIFICARE: 
-- le note al codice sono identificate con la parola chiave NOTE MARCO

--if not versionDCE then versionDCE = {} end
--versionDCE["DEBRIEF_Master.lua"] = "1.7.33"


--================== LOCAL FUNCTION ===============================================

local function AcceptMission()

	local nameFunction = "AcceptMission() --> "    


	repeat
		print("\n\n Night or Day ? : "..daytime)													-- info day or not
		print("\n\nAccept Mission ?:")

		print("a".." - Accept mission")
		print("s".." - Skip mission")

		m = tostring(io.read())
		m = string.lower(m)

		if not ( m ~= nil and ( m == "a" or m == "s" or m == "d")) then
			print("\nInvalid entry.\n")
		end
	until m ~= nil and ( m == "a" or m == "s" or m == "d")



	if  m == "s" then
		TaskRefused = true
		return false

	elseif  m == "d" then
		os.execute('start "Debug" "notepad++.exe" "Debug/debugFlight' .. '.txt"')		
		return true
	else		
		return true
	end
end

--================== END LOCAL FUNCTION ===============================================

----- random seed -----
math.randomseed(tonumber(tostring(os.time()):reverse():sub(1,6)))
math.random(); math.random(); math.random()


--load functions
dofile("Init/conf_mod.lua")

local activate_testing_enviroment = ACTIVATE_TESTING_ENVIROMENTS -- false: for running in DCE enviroment (DEBRIEF_Master.lua launched from DEBUG_DebriefMission.bat), true: for running in testing enviroment (DEBRIEF_Master.lua launched from DEBUG_DebriefMissionTesting.bat) --By Old_Boy

local logExport 											-- mission events log -- 
local scenExport											-- destroyed scenery objects
local campExport											-- camp_status

if not activate_testing_enviroment then
	-- questi file sono temporanei generati allo stop del server (vedi script caricati nel Missione Generator)
	logExport = loadfile("MissionEventsLog.lua")() 											-- mission events log -- 
	scenExport = loadfile("scen_destroyed.lua")()											-- destroyed scenery objects
	campExport = loadfile("camp_status.lua")()												-- camp_status

else		
	-- test temporary file
	logExport = loadfile("MissionEventsLog.2t.lua")() 										-- mission events log -- 
	scenExport = loadfile("scen_destroyed.2t.lua")()										-- destroyed scenery objects
	campExport = loadfile("camp_status.2t.lua")()											-- camp_status
end


versionPackageICM = camp.versionPackageICM -- camp is defined in camp_status

if not versionPackageICM or versionPackageICM == nil then									-- Miguel21 modification M35.d version ScriptsMod
	versionPackageICM = os.getenv('versionPackageICM')										-- Miguel21 modification M35.c version ScriptsMod
end

inspect = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_inspect.lua")
-- load UTIL_Log for define a local istance of logger (allow a dedicated file for this module)
local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua")
log.activate = false-- select true to activate log
log.level = LOGGING_LEVEL
log.outfile = LOG_DIR .. "LOG_DEBRIEF_Master."  .. camp.mission .. ".log"
log.activate = false-- select true to activate log
local local_debug = false -- local debug
local active_log = false -- select true to activate log
log.info("Start")
log.debug(versionPackageICM) 
dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Functions.lua")

if not activate_testing_enviroment then
	log.warn("activate testing enviroment")	
end

--load status file to be updated
log.debug("load: Active/oob_ground, Init/db_airbases, Active/oob_air, Active/targetlist, Active/clientstats")
require("Active/oob_ground")																		--load ground oob
require("Init/db_airbases")																			--load db_airbases
require("Active/oob_air")																			--load air oob
require("Active/targetlist")																		--load targetlist
require("Active/clientstats")																		--load clientstats
require("Init/db_aircraft")																			--load clientstats

if local_debug then
	log.warn("activate local debug")
	log.debug("copy before updating (ante) Active/oob_ground, Active/oob_air, Active/targetlist and Active/clientstats in Debug for mission: "..camp.mission)
	CopyFile("Active/oob_ground.lua", "Debug/oob_ground." .. camp.mission .. ".ante.lua" )
	CopyFile("Active/oob_air.lua", "Debug/oob_air." .. camp.mission .. ".ante.lua" )
	CopyFile("Active/targetlist.lua", "Debug/targetlist." .. camp.mission .. ".ante.lua" )
	CopyFile("Active/clientstats.lua", "Debug/clientstats." .. camp.mission .. ".ante.lua" )
end

--run log evaluation and status updates
log.debug("run run log evaluation and status updates (loading UTIL_Functions.lua, DEBRIEF_StatsEvaluation.lua, DC_DestroyTarget.lua, DC_UpdateTargetlist.lua)")--By Old_Boy
dofile("../../../ScriptsMod."..versionPackageICM.."/DEBRIEF_StatsEvaluation.lua")
dofile("../../../ScriptsMod."..versionPackageICM.."/DC_DestroyTarget.lua")												--Mod11.j
dofile("../../../ScriptsMod."..versionPackageICM.."/DC_UpdateTargetlist.lua")

--run logistic evalutation, save power_tab and airbase_tab
log.debug("run logistic evalutation (load DC_Logistic.lua and execute UpdateOobAir() function)")
dofile("../../../ScriptsMod."..versionPackageICM.."/DC_Logistic.lua")
local result_update_logistic
result_update_logistic, airbase_tab, supply_tab = UpdateOobAir()--update <logistics

if not result_update_logistic then
	log.warn("DC_logistic function UpdateOobAir() failed!!")
end

--update campaign time.
local elapsed_time = math.floor(events[#events].t - events[1].t)								--mission runtime in seconds
camp.time = camp.time + elapsed_time															--add mission time to campaign time
log.debug("update campaign time - elapsed_time: " .. elapsed_time .. ". camp.time: " .. camp.time)

--create and view debriefing file for mission
log.debug("run debriefing visualization (load DEBRIEF_Text.lua)")
dofile("../../../ScriptsMod."..versionPackageICM.."/DEBRIEF_Text.lua")							--In this script the actual text is created. Script loaded after oob modifications above have been made.
local debriefFile = io.open("Debriefing/Debriefing " .. camp.mission .. ".txt", "w")			--create new debriefing file
debriefFile:write(debriefing)																	--write debriefing text into file (variable debriefing comes from DEBRIEF_Text.lua)
debriefFile:close()
os.execute('start "Debriefing" "notepad.exe" "Debriefing/Debriefing ' .. camp.mission .. '.txt"')	--open the debriefing file with notepad

local TabTask = {
	["a"] = "Anti-ship Strike",
		["Anti-ship Strike"] = "a",
	["c"] = "CAP",
		["CAP"] = "c",
	["d"] = "SEAD",
		["SEAD"] = "d",
	["e"] = "Escort",
		["Escort"] = "e",
	["f"] = "Fighter Sweep",
		["Fighter Sweep"] = "f",
	["i"] = "Intercept",
		["Intercept"] = "i",
	["l"] = "Laser Illumination",
		["Laser Illumination"] = "l",
	["r"] = "Reconnaissance",
		["Reconnaissance"] = "r",
	["s"] = "Strike",
		["Strike"] = "s",
	["t"] = "Transport",
		["Transport"] = "t",
	["u"] = "Refueling",
		["Refueling"] = "u",
	}

local showVersion = versionPackageICM
local verScriptsModPath = "../../../ScriptsMod."..versionPackageICM.."/UTIL_Version.lua"
local TestPath = io.open(verScriptsModPath, "r")

if  TestPath ~= nil then	
	io.close(TestPath)
	dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Version.lua")
	showVersion = showVersion.." ("..version_ScriptsMod.ScriptsMod..")"
	log.trace("file: " .. verScriptsModPath .. "open. Script Version: " .. showVersion)
end

if versionPackageICM then
	print("= = = = = = = = = = = = = = = = = = = = = = = "..camp.title.." = = = = = = = = = = = = = = = = = =")
	print("= = = = = = = = = = = = = = Version: "..camp.version)
	print("= = = = = = = = = = = = = Script: "..showVersion)
	print()
else
	print("= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =")
end
--===================================================================================
-- Ecran N�0 Choix next campaign mission
--ask for input to save results and continue with campaign or disregard the last mission
log.debug("Ask for input about confirm client results")
print("\nAccept mission results and continue with campaign? y(es)/n(o):\n")					--ask for user confirmation
local input
local playable_type = {}

SinglePlayer = false
Multi =
	{
		NbGroup = 0,
	}																						--user input

repeat
	input = io.read()
	input = string.lower(input)
	if input == "y" or input == "yes" or input == "n" or input == "no" then
		break
	else
		print("\n\nInvalid entry. Respond with y(es) or n(o):\n")
	end
until input == "y" or input == "yes" or input == "n" or input == "no"

print("\n\n")

if input == "y" or input == "yes" then

	--save new data (remaining files are updated in MAIN_NextMission.lua)
	log.debug("Save updated clientstats in Active/clientstats.lua file")
	local client_str = "clientstats = " .. TableSerialization(clientstats, 0)					--make a string
	local clientFile = io.open("Active/clientstats.lua", "w")									--open clientstats file
	clientFile:write(client_str)																--save new data
	clientFile:close()		

	-- UPDATE OOB_SCEN 
	log.debug("update oob_scen file with new destroyed scenery objects")
	
	if local_debug then
		log.debug("copy before updating (ante) Active/oob_scen in Debug for mission: "..camp.mission)
		CopyFile("Active/oob_scen.lua", "Debug/oob_scen." .. camp.mission .. ".ante.lua" )
	end	
	local oob_scen_old = loadfile("Active/oob_scen.lua")()	
		
	--load oob_scen file. Note: scen_log is defined in scenery_destroyed.lua temp file
	for scen_name,scen in pairs(scen_log) do													--iterate through destroyed scenery objects
		if scen.x and scen.z then																--destroyed scenery object has x and z coordinates
			oob_scen[scen_name] = scen															--add/update to oob_scen
			log.trace("update oob_scen with new destroyed scenery objects id.: " .. scen_name .. "position(x,z): " ..scen.x .. "," .. scen.z)--By Old_Boy
		end
	end
	log.debug("Save oob_scen.lua file")
	local scen_str = "oob_scen = " .. TableSerialization(oob_scen, 0)							--make a string
	local scenFile = io.open("Active/oob_scen.lua", "w")										--open oob_scen file
	log.debug("Save oob_scen.lua file")
	scenFile:write(scen_str)																	--save new data
	scenFile:close()	
	
	if local_debug then
		log.debug("copy after updating (post) Active/oob_scen in Debug for mission: "..camp.mission)
		CopyFile("Active/oob_scen.lua", "Debug/oob_scen." .. camp.mission .. ".post.lua" )
	end	

	log.debug("Ask for input about client's choice")
	repeat
		--===================================================================================
		-- Ecran N�1 Choix entre Single ou Multiplayer
		print("Select :\n"..
			"S (S)ingleplayer  \n"..
			"D Singleplayer with (D)edicated Server (In Test) \n"..
			"DF Singleplayer with (D)edicated Server, (F)ull plane on Deck (Testing: Bug Catapult possible) \n"..
			"\n"..

			-- "C (C)hange type of plane (coming soon) \n"..
			-- "\n"..
			"T Multiplayer by choice of (T)arget \n"..
			"N multiplayer by choice of (N)ATO")

		local tabIndex01 = {
			["s"] = true,
			["d"] = true,

			["df"] = true,

			["n"] = true,
			["t"] = true,


			["y"] = true,
			["z"] = true,
		}


		repeat																							-- adjustment A01 : robust form

			choix1 = io.read()
			choix1 = string.lower(choix1)
			log.trace("client's choice: " .. choix1)--By Old_Boy
			
			if choix1 == "n" or  choix1 == "t"  then
				log.debug("Multiplayer choice")--By Old_Boy
				
				if choix1 == "t"  then
				--===================================================================================
				-- Ecran N�2 Selection du Target
					print("choose a Single target")					
					local tableTargetlist = {}
					local i = 1
					local tableTargetlist = {
							["blue"] = {},
							["red"] = {},
							}

					for side, target_side in pairs(targetlist) do														--iterate through sides in targetlist
						
						for target_name, target in pairs(target_side) do												--iterate through all hostile targets
							
							if target.inactive ~= true and ( target.task == "Strike" or target.task == "Anti-ship Strike") then															--if target is active and should be added to ATO
								local draftTarget = {
										["name"] = tostring(target_name),
										["priority"] = tonumber(target.priority),
										}

								table.insert(tableTargetlist[side], draftTarget)

								i = i + 1
							end
						end
					end

					table.sort(tableTargetlist["red"], function(a,b) return a.priority > b.priority  end) -- table order by priority
					table.sort(tableTargetlist["blue"], function(a,b) return a.priority > b.priority  end)

					local tabIndex = {}

					for side, Targetlist in pairs(tableTargetlist) do
						local j = 1
						local Ckey = 0
						print() print(side..":")
						
						for key, value in pairs(Targetlist) do
							
							if  j <= 20  then
								
								if side == "red" then
									Ckey = key + #tableTargetlist["blue"]															--permet de n'afficher qu'un nombre continue pour les 2 camps
								
								else
									Ckey = key
								end
								io.write(  Ckey.." "..side.." "..tostring(value.name) .."  "..tostring(value.priority).."\n")
								
								if not tabIndex[Ckey] then tabIndex[Ckey] = {} end
								tabIndex[Ckey]["side"] = side
								j = j+1
							end
						end
					end

					repeat
						input = tonumber(io.read())

						if (input == nil or input == "") then input = 999 end
						
						if input >  #tableTargetlist["blue"] then
							Ckey = input - #tableTargetlist["blue"]
						
						else
							Ckey = input
						end
						
						if  tabIndex[input] then
							local side = tabIndex[input]["side"]
							if not Multi.Target then Multi.Target = {} end
							if not Multi.Target[side] then Multi.Target[side]= {} end
							Multi.Target[side] = tableTargetlist[side][Ckey].name
							print("\n"..tableTargetlist[side][Ckey].name.."\n")
						
						else
							print("\nInvalid entry.\n")
						end
					until  tabIndex[input]

					io.write( "\n")
				end	--if choix1 == "t"  then

			--===================================================================================
			-- Ecran N�3 Selection nb of Flight
				repeat
					print("Select number of Flight :\n")
					input = tonumber(io.read())

					if (input == nil or input == "") then input = 999 end
					
					if  (input >= 1 and  input <= 10) then
						Multi.NbGroup = input
					
					else
						print("\nInvalid entry.\n")
					end
				until   (input >= 1 and  input <= 10)

			--===================================================================================
			-- Ecran N�4 Selection du type d'avion Multiplayer
				local tabIndex = {}
				
				for i = 1 , Multi.NbGroup do
					local ExPlaneA = ""
					local stopLoop = false
					
					for nSide , oob_airSide in pairs(oob_air) do														--pour afficher l'exemple de selection du premier avion pr�sent�
						
						for m , unit in pairs(oob_airSide) do
							
							if playable_m[unit.type] and unit.inactive ~= true and not stopLoop then
								ExPlaneA = unit.type
								stopLoop = true
							end
						end
					end
					print("Choose your aircraft type for Flight n�"..i)
					print("(number of aircraft) (type of aircraft) (type of mission)")
					print("example for (4 "..ExPlaneA..": Escort): 4ae or 4AE")

					if not Multi.Group then Multi.Group= {} end

					if not Multi.Group[i] then Multi.Group[i]= {} end
					local playable_type = {}
					local seen = {}
					local tasks = {}
				local ti = 65 																						--char(65) == a
				tabTaskAvailable = {}

				-- parse toutes les unit�s et rempli le tab tabTaskAvailable pour etre sur de proposer toutes les task propos� active
				for nSide , oob_airSide in pairs(oob_air) do
					print() print(nSide..":")
					
					for m , unit in pairs(oob_airSide) do
						
						if playable_m[unit.type]  and unit.inactive ~= true then
							
							for taskStr , nbool in pairs(oob_air[nSide][m].tasks) do
								taskStr = tostring(taskStr)

								if not tabTaskAvailable[nSide] then tabTaskAvailable[nSide] = {} end
								
								if not tabTaskAvailable[nSide][unit.type] then tabTaskAvailable[nSide][unit.type] = {} end
								
								if not tabTaskAvailable[nSide][unit.type][taskStr] then tabTaskAvailable[nSide][unit.type][taskStr] = nbool end
								
								if nbool == true then	tabTaskAvailable[nSide][unit.type][taskStr] = true	end
							end
						end
					end
				end

				-- display le tableau des choix d'avion et de task
				--tabTaskAvailable[nSide][unit.type][taskStr]
				for nSide , unit_type in pairs(tabTaskAvailable) do
					print() print(nSide..":")
					
					for unitType , TabType in pairs(unit_type) do

						local IndexStringType = string.lower(string.char(ti))
					
						if not playable_type[IndexStringType] then playable_type[IndexStringType] = {} end
						playable_type[IndexStringType]["type"] = unitType
						playable_type[IndexStringType]["side"] = nSide

						io.write(" (1 to 8): ("..IndexStringType.."): "..unitType..":")

						for taskStr , nbool in pairs(TabType) do
					
							if   nbool == true then
								io.write( " ("..TabTask[taskStr]..")"..taskStr.."")
								local FstLetTask = string.lower(string.sub (taskStr, 1, 1))
								tabIndex[tostring(1)..IndexStringType..TabTask[taskStr]] = true
								tabIndex[tostring(2)..IndexStringType..TabTask[taskStr]] = true
								tabIndex[tostring(3)..IndexStringType..TabTask[taskStr]] = true
								tabIndex[tostring(4)..IndexStringType..TabTask[taskStr]] = true
								tabIndex[tostring(5)..IndexStringType..TabTask[taskStr]] = true
								tabIndex[tostring(6)..IndexStringType..TabTask[taskStr]] = true
								tabIndex[tostring(7)..IndexStringType..TabTask[taskStr]] = true
								tabIndex[tostring(8)..IndexStringType..TabTask[taskStr]] = true

							end
						end
						io.write("\n")
						ti = ti+1
					end
				end

				io.write( "\n")
			--===================================================================================
				-- Ecran N�5 Selection Nombre d'avion Multiplayer
					repeat
						input = string.lower(io.read())
						
						if  tabIndex[input] then
							
							if not Multi.Group[i] then Multi.Group[i]= {} end

							local inputNb = tonumber(string.sub (input, 1, 1))
							Multi.Group[i].NbPlane = inputNb

							local inputTyp = tostring(string.sub (input, 2, 2))
							Multi.Group[i].PlaneType = playable_type[inputTyp].type
							Multi.Group[i].side = playable_type[inputTyp].side

							local inputTsk = tostring(string.sub (input, 3, 3))
							Multi.Group[i].task = TabTask[inputTsk]

						else
							print("\nInvalid entry.\n")
						end
					until   tabIndex[input]

					io.write( "\n")

					--========================= affiche le choix du joueurs
					print(" -------------------------------------------------------> Building your different Flight: ")
					for k=1, i do
						print(" -------------------------------------------------------> "..Multi.Group[k].NbPlane.." "..Multi.Group[k].PlaneType.." ("..Multi.Group[k].side..")".." "..Multi.Group[k].task)
					end
					io.write( "\n")

				end
			--===================================================================================
				-- Ecran N�6 SinglePlayer

		elseif choix1 == "s" then
			log.debug("SinglePlayer choice")--By Old_Boy
		  	SinglePlayer = true

		elseif choix1 == "d" then
			log.debug("SinglePlayer with Dedicated Server choice")--By Old_Boy
		  	SinglePlayer = true
		  	SingleWithDServer = true
		  	SingleWithDServerAiAir = true

		elseif choix1 == "df" then
			log.debug("SinglePlayer with Dedicated Server choice full deck")--By Old_Boy
		  	SinglePlayer = true
		  	SingleWithDServer = true
		end

	until tabIndex01[choix1]

	--==========================================================

	--increase campaign mission number
	camp.mission = camp.mission + 1

	--generate next campaign mission
	briefing_status = ""																		--text string to be added to next briefing (status reports are amended for each mission generation attempt until mission is succesfully generated)
	briefing_oob_text_red = ""																	--text string to be added to next briefing (red repair and reinforcements)
	briefing_oob_text_blue = ""																	--text string to be added to next briefing (blue repair and reinforcements)
	PlayerFlight = false																		--variable to control mission generation loop

	MissionInstance = 0

	repeat
		print("Generating Next Mission.\n")

		MissionInstance = MissionInstance + 1													--count the number of times the mission is generated
		log.debug("load: MAIN_NextMission.lua")
		dofile("../../../ScriptsMod."..versionPackageICM.."/MAIN_NextMission.lua")				--generate next mission

		if v_EndCampaign then 	
																								-- debug01.b EndMission
			if AcceptMission() then
				log.debug("End Campaign")
				print("\nEND OF THE CAMPAIGN, SEE THE BRIEFING IN THE MISSION..\n")				-- end of camapaign
				break
			end
		
		elseif Multi.NbGroup >= 1 and PlayerFlight then
			
			if AcceptMission() then
				log.debug("Multi.NbGroup >= 1 and PlayerFlight is true -> MultiplayerCampaign Next mission generated")--By Old_Boy
				print("\nMultiplayerCampaign Next mission generated.\n")						--confirmation text
				break
			end
		
		elseif SinglePlayer and PlayerFlight  then												--mission has a player flight
			
			if AcceptMission() then
				log.debug("SinglePlayer and PlayerFlight is true -> MultiplayerCampaign Next mission generated")--By Old_Boy
				print("\nNext mission generated.\n")											--confirmation text
				break
			end
		
		elseif stopBug then
			log.debug("Multi.NbGroup >= 1 or PlayerFlight or SinglePlayer is false and stopBug is true -> stopBug")			--By Old_Boy															--mission has a player flight
			print("\n\n stopBug .\n")															--confirmation text
			break
		
		elseif MissionInstance == 50 then
			log.debug("Mission Generation Error. No eligible player flight in 50 attempts")												--By Old_Boy		--no player flight could be assigned in 50 tries, stop it
			print("Mission Generation Error. No eligible player flight in 50 attempts. Start a new campaign.\n\n")
			break
		else																					--no player flight could be assigned, advance time and try again
			
			if playability_criterium.active_unit == nil then
				print("Player unit is not active.\n\n")
			
			elseif playability_criterium.base == nil then
				print("Player airbase is not operational.\n\n")
			
			elseif playability_criterium.ready_aircraft == nil then
				print("Player unit has no ready aircraft.\n\n")
			
			elseif playability_criterium.tot == nil then
				print("Player aircraft type cannot operate at this time of day.\n\n")
			
			elseif playability_criterium.target == nil then
				print("No eligible mission available for player.\n\n")
			
			elseif playability_criterium.target_firepower == nil then
				print("Not enough ready aircraft for this mission.\n\n")
			
			elseif playability_criterium.weather == nil then
				print("Player aircraft type cannot operate in this weather.\n\n")
			
			elseif playability_criterium.target_range == nil then
				print("No eligible mission available for player.\n\n")
			
			elseif playability_criterium.coop == nil then
				print("Not enough ready aircraft for all clients.\n\n")
			
			elseif Multi.NbGroup and not PlayerFlight then
				print("Not enough ready aircraft for all clients.\n\n")
			
			elseif playability_criterium.intercept == nil then
				print("Ground alert intercept duty without launch.\n\n")
			end
		end
		
		if showVersion then
			print("= = = = = = = = = = = = = = = = = = = = = = = "..camp.title.." = = = = = = = = = = = = = = = = = =")
			print("= = = = = = = = = = = = = = Version: "..camp.version)
			print("= = = = = = = = = = = = = Script: "..showVersion)
			print()
		else
			print("= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =")
		end
	until 1 == 2																					--repeat until the next mission is ready (has a player flight)
	break
  until 1 == 2
	os.execute 'pause'
end



if local_debug then -- Copy file for Debug
	log.debug("copy MissionEventsLog.lua, scen_destroyed.lua, camp_status.lua in Debug for mission: "..camp.mission)
	CopyFile("MissionEventsLog.lua", "Debug/MissionEventsLog." .. camp.mission .. ".lua" )
	CopyFile("scen_destroyed.lua", "Debug/scen_destroyed." .. camp.mission .. ".lua" )
	CopyFile("camp_status.lua", "Debug/camp_status." .. camp.mission .. ".lua" )
end

--delete mission export files
os.remove("MissionEventsLog.lua")	--DISABLE FOR DEBUG
os.remove("scen_destroyed.lua")		--DISABLE FOR DEBUG
os.remove("camp_status.lua")		--DISABLE FOR DEBUG

log.debug("End")

os.exit()
