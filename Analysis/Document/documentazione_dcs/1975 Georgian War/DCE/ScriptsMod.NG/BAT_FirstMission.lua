--To manually generate the first campaign mission and reset the campaign to initial status. For manual use by campaign designer only, not required for normal campaign play.
--Initiated by FirstMission.bat
-------------------------------------------------------------------------------------------------------

if not versionDCE then 
	versionDCE = {} 
end

               -- VERSION --

versionDCE["BAT_FirstMission.lua"] = "OB.1.0.0"

---------------------------------------------------------------------------------------------------------
-- Old_Boy rev. OB.1.0.0: implements logging code
-- adjustment A01.b : robust form.
-- miguel21 modification M47.c keeps the history of the campaign files (c: save debugging information during mission generation)
-- miguel21 modification M46.d  singlePlayer with dedicated server (c: DF choice)(c: D choice with AI AirSpawn)
-- miguel21 modification M38.e  helps to balance the game
-- Miguel21 modification M35.d version ScriptsMod + camp
-- Miguel21 modification M14 : Versionning
-- Miguel21 modification M11.q : Multiplayer (q: displays all tasks of several squadrons)(p: Task table)

--if not versionDCE then versionDCE = {} end
--versionDCE["BAT_FirstMission.lua"] = "1.7.33"

versionPackageICM = os.getenv('versionPackageICM')														-- Miguel21 modification M35.b version ScriptsMod
math.randomseed(tonumber(tostring(os.time()):reverse():sub(1,6)))										----- random seed -----
math.random(); math.random(); math.random()																----- random seed -----
dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Functions.lua")
dofile("Init/conf_mod.lua")
dofile("Init/camp_init.lua")
dofile("Init/db_firepower.lua")
dofile("Init/oob_air_init.lua")
dofile("Init/targetlist_init.lua")

local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua")
-- NOTE MARCO: prova a caricarlo usando require(".. . .. . .. .ScriptsMod."versionPackageICM..".UTIL_Log.lua")
-- NOTE MARCO: https://forum.defold.com/t/including-a-lua-module-solved/2747/2
log.level = LOGGING_LEVEL
log.outfile = LOG_DIR .. "LOG_BAT_FirstMission." .. camp.mission .. ".log" 
local local_debug = true -- local debug   
log.info("Start")

local function AcceptMission()
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

dofile("Init/supply_tab_init.lua") -- load initial supply tab
local tgt_str = "supply_tab = " .. TableSerialization(supply_tab, 0)				    --make a string
local tgtFile = nil
tgtFile = io.open("Active/supply_tab.lua", "w")
tgtFile:write(tgt_str)																		--save new data
tgtFile:close()


local showVersion = versionPackageICM

local verScriptsModPath = "../../../ScriptsMod."..versionPackageICM.."/UTIL_Version.lua"
local TestPath = io.open(verScriptsModPath, "r")
if  TestPath ~= nil then
	io.close(TestPath)
	dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Version.lua")
	showVersion = showVersion.." ("..version_ScriptsMod.ScriptsMod..")"
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
	-- Ecran N°0 Choix next mission
print("Reset the campaign and generate a new first mission.\n")

local input
local playable_type = {}

SinglePlayer = false
Multi =
	{
		NbGroup = 0,
	}

repeat
	--===================================================================================
	-- Ecran N°1 Choix entre Single ou Multiplayer

	local tabIndex01 = {
		["s"] = true,
		["d"] = true,

		["df"] = true,

		["n"] = true,
		["t"] = true,


		-- ["y"] = true,
		["z"] = true,
	}

	repeat

		print("Select :\n"..
			"S (S)ingleplayer  \n"..
			"D Singleplayer with (D)edicated Server \n"..
			"DF Singleplayer with (D)edicated Server, (F)ull plane on Deck (Testing: Bug Catapult possible) \n"..
			"\n"..
			-- "C (C)hange type of plane (coming soon) \n"..
			-- "\n"..
			"T Multiplayer by choice of (T)arget \n"..
			"N multiplayer by choice of (N)ATO")

		choix1 = io.read()
		-- if choix1 == ""  then choix1 = "A" end
		choix1 = string.lower(choix1)

		if choix1 == "n" or  choix1 == "t"  then
			if choix1 == "t"  then
				--===================================================================================
				-- Ecran N°2 Selection du Target
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

							i = i +1
						end
					end
				end

				table.sort(tableTargetlist["red"], function(a,b) return a.priority > b.priority  end)
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
							if not tabIndex[Ckey]  then tabIndex[Ckey] = {} end
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
			-- Ecran N°3 Selection nb of Flight
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
			-- Ecran N°4 Selection du type d'avion Multiplayer
			local tabIndex = {}
			for i = 1 , Multi.NbGroup do
				local ExPlaneA = ""
				local stopLoop = false
				for nSide , oob_airSide in pairs(oob_air) do														--pour afficher l'exemple de selection du premier avion présenté
					for m , unit in pairs(oob_airSide) do
						if playable_m[unit.type] and unit.inactive ~= true and not stopLoop then
							ExPlaneA = unit.type
							stopLoop = true
						end
					end
				end

				print("Choose your aircraft type for Flight n°"..i)
				print("(number of aircraft) (type of aircraft) (type of mission)")
				print("example for (4 "..ExPlaneA..": Escort): 4ae or 4AE")

				if not Multi.Group then Multi.Group= {} end
				if not Multi.Group[i] then Multi.Group[i]= {} end

				local playable_type = {}
				local ti = 65 																						--char(65) == a
				tabTaskAvailable = {}

				-- parse toutes les unités et rempli le tab tabTaskAvailable pour etre sur de proposer toutes les task proposé active
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
				-- Ecran N°5 Selection Nombre d'avion Multiplayer
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
			-- Ecran N°6 SinglePlayer

		elseif choix1 == "s" then
		  SinglePlayer = true

		elseif choix1 == "d" then
		  SinglePlayer = true
		  SingleWithDServer = true
		  SingleWithDServerAiAir = true

		elseif choix1 == "df" then
		  SinglePlayer = true
		  SingleWithDServer = true


		-- miguel21 modification M38.e Check and helps to balance the game for CampaignMaker
		elseif choix1 == "z" then
		  	repeat
				dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_HelpBalancePower.lua")
				os.execute 'pause'
			until 1 == 2
		end

	until tabIndex01[choix1]

	FirstMission = true																					--variable used during mission generation to make sure that mission is generated as first campaign mission
	MissionInstance = 0
	print("\n\n")
	repeat
		print("Generating First Mission.\n")

		MissionInstance = MissionInstance + 1															--count the number of times the mission is generated
		dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_ResetCampaign.lua")					--reset campaign status files. Required for first mission to generate according to initial status
		dofile("../../../ScriptsMod."..versionPackageICM.."/MAIN_NextMission.lua")						--generate mission

		if Multi.NbGroup >= 1 and PlayerFlight then
			if AcceptMission() then
				 print("\nMultiplayerCampaign Next mission generated.\n")								--confirmation text
				 break
			end
		elseif SinglePlayer and PlayerFlight  then														--mission has a player flight
			if AcceptMission() then
				 print("\nCampaign reset and first campaign mission re-generated.\n")					--confirmation text
				 break
			end
		elseif stopBug then																				--mission has a player flight
			print("\n\n stopBug .\n")																	--confirmation text
			break

		elseif MissionInstance == 20 then																--no player flight could be assigned in 20 tries, stop it
			print("Mission Generation Error. No eligible player flight in 20 attempts. Try again.\n\n")
			break
		else																							--no player flight could be assigned, advance time and try again
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
			-- elseif playability_criterium.coop == nil then
				-- print("Not enough ready aircraft for all clients.\n\n")
			elseif Multi.NbGroup and not PlayerFlight then
				print("Not enough ready aircraft for all clients..\n\n")
			elseif playability_criterium.intercept == nil then
				print("Ground alert intercept duty without launch.\n\n")
			end
		end

	if showVersion  then
		print("= = = = = = = = = = = = = = = = = = = = = = = "..camp.title.." = = = = = = = = = = = = = = = = = =")
		print("= = = = = = = = = = = = = = Version: "..camp.version)
		print("= = = = = = = = = = = = = Script: "..showVersion)
		print()
	else
		print("= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =")
	end
	until 1 == 2
	break

until 1 == 2

os.execute 'pause'																					--pause command window for user to read text
os.exit()
