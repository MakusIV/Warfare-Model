-- helps the CampaignMaker to balance the campaign
--
------------------------------------------------------------------------------------------------------- 
-- Miguel Fichier Revision 
------------------------------------------------------------------------------------------------------- 

-- miguel21 modification M38.e  helps to balance the game

-- =====================  Marco implementation ==================================
local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua")
-- NOTE MARCO: prova a caricarlo usando require(".. . .. . .. .ScriptsMod."versionPackageICM..".UTIL_Log.lua")
-- NOTE MARCO: https://forum.defold.com/t/including-a-lua-module-solved/2747/2
log.level = LOGGING_LEVEL
log.outfile = LOG_DIR .. "LOG_UTIL_HelpBalancePower." .. camp.mission .. ".log" 
local local_debug = true -- local debug   
log.info("Start")
-- =====================  End Marco implementation ==================================


require("Init/oob_air_init")
 
 
-- if should_reload( 'oob_air_init' ) then
    package.loaded[ 'Init/oob_air_init' ] = nil
    require("Init/oob_air_init")
-- end

require("Init/db_loadouts")

-- if should_reload( 'db_loadouts' ) then
    package.loaded[ 'Init/db_loadouts' ] = nil
    require("Init/db_loadouts")
-- end




-- require("Init/db_loadouts")
require("Init/db_airbases")
-- require("Init/oob_air_init")
require("Active/oob_ground")
require("Init/conf_mod")															-- Miguel21 modification M00 : need option
require("Init/radios_freq_compatible")												-- miguel21 modification M34 custom FrequenceRadio
require("Active/camp_triggers")

dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Functions.lua")


balance = {}
balanceTS = {}

tabMaxSum = {}
	
	
for side,unit in pairs(oob_air) do																								--iterate through all sides

	for n = 1, #unit do																				--iterate through all units

		if unit[n].inactive ~= true and db_airbases[unit[n].base] and db_airbases[unit[n].base].inactive ~= true then
			
			local plane = unit[n].type
			
			for task,task_bool in pairs(unit[n].tasks) do											--iterate through all tasks of unit

				if task_bool then	
					local temp_draft_sorties = {}														--temporary table to hold additional draft sorties with escorts assigned
					--get possible loadouts
					local unit_loadouts = {}														--table to hold all loadouts for this aircraft type and task
					for loadout_name, ltable in pairs(db_loadouts[unit[n].type][task]) do			--iterate through all loadouts for the aircraft type and task
						ltable.name = loadout_name
						unit_loadouts[#unit_loadouts+1] = ltable
					end

					-- ajoute dans une table les informations aux plus hautes valeurs
					if unit[n].number > 0 and db_loadouts[unit[n].type][task]  then																				--has ready aircraft
								
						local somme = 0
						local sum_fireP = 0
						local sum_capY = 0
						for l = 1, #unit_loadouts do
							sum_fireP = sum_fireP +  unit_loadouts[l].firepower
							sum_capY = sum_capY +  unit_loadouts[l].capability
							
							local break_loop = false
							for n = 1, 6 do
								
								if not tabMaxSum[side] then tabMaxSum[side] = {} end
								if not tabMaxSum[side][n] then tabMaxSum[side][n] = {}  tabMaxSum[side][n]["sum"] = 0 end
								
								if ((sum_fireP * sum_capY)  /#unit_loadouts) > tabMaxSum[side][n]["sum"] then								

									tabMaxSum[side][n] = nil
									tabMaxSum[side][n] = {
										["sum"] = (sum_fireP * sum_capY)  /#unit_loadouts,
										["plane"] = plane,
										["task"] = task,
										["name"] = unit_loadouts[l].name,
										["firepower"] = unit_loadouts[l].firepower,
										["capability"] = unit_loadouts[l].capability,
										["nbLoadout"] = #unit_loadouts
									}
									break_loop = true
									break
									
								end
								if break_loop then break end
							end
						end  
						
						--(sum_fireP  /#unit_loadouts) pour calculer la moyenne des firepowers
						-- aditionne ici les plus hautes valeurs
						
						if not balanceTS[task] then balanceTS[task] = {} end
						if not balanceTS[task][side] then balanceTS[task][side] = {} end
						if not balanceTS[task][side]["somme"..side] then balanceTS[task][side]["somme"..side] = 0 end
						if not balanceTS[task][side]["number"..side] then balanceTS[task][side]["number"..side] = 0 end
						
--todo la sum de firepower = 1 fait 3 pour 3 loadout, a revoir, 	
						if task == "Escort" or task == "CAP" or task == "Intercept" then	
							somme = ((sum_fireP * sum_capY)  /#unit_loadouts)  * unit[n].number
							balanceTS[task][side]["somme"..side] = balanceTS[task][side]["somme"..side] + somme
							balanceTS[task][side]["number"..side] = balanceTS[task][side]["number"..side] + unit[n].number
							
						else
							somme = (sum_fireP  /#unit_loadouts)  * unit[n].number
							balanceTS[task][side]["somme"..side] = balanceTS[task][side]["somme"..side] + somme
							balanceTS[task][side]["number"..side] = balanceTS[task][side]["number"..side] + unit[n].number
							
						end
						--unit_loadouts[l].capability * unit_loadouts[l].firepower
					
					end
				end

			end
			
		end
		
	end

end

print()
print("The 3 highest values of each camp:")
_affiche(tabMaxSum)

function Space(txt, space_)
	space_ = space_ - string.len(tostring(txt))

	for n = 1, space_ * 1.0 do	 --for n = 1, space_ * 1.5 do														
		txt = txt .. " "																	--add 1.5 spaces for every missing letter
	end

	return txt

end

local s = "\\n"																	--make a list with details of the player waypoints

local entries = {																			--list entries that are making up the navigaion overview
		
	[1] = {
		lookup = "task",
		header = "Task",
		str_length = 20,
	},
	[2] = {
		lookup = "numberblue",
		header = "NbBlue",
		str_length = 8,
	},
	[3] = {
		lookup = "sommeblue",
		header = "TotBlue",		
		str_length = 8,	
	},
	[4] = {
		lookup = "numberred",
		header = "NbRed",
		str_length = 8,
	},
	[5] = {
		lookup = "sommered",
		header = "TotRed",		
		str_length = 8,	
	},
}

--build the list header
for e = 1, #entries do																		--iterate through all entries
	s = s .. entries[e].header																--add entry of this waypoint to list
																							--if this is not the last entry of the waypoints, add spaces to the next entry	
	local space = entries[e].str_length + 0 - string.len(tostring(entries[e].header))		--calculate number of spaces that need to be added for alignement (string length of largest entry of same type + 3 - length of current entry = number of spaces)
	entries[e]["space"] = space
	for n = 1, space * 1.0 do															
		s = s .. " "																		--add 1.5 spaces for every missing letter
	end

end
s = s .. "\\n"


-- _affiche(entries)
-- _affiche(balanceTS)

local test = ""
for task, _side in pairs(balanceTS) do
	-- io.write("A")

	for e = 1, #entries do
		local entry = ""
		if entries[e].lookup == "task" then
			entry = Space(task, entries[e].str_length)
		end
		s = s.. entry
	end

					
	for side, _value in pairs(_side) do
		-- io.write("B")
		
		-- for key, value in pairs(_value) do
			-- io.write("C")
			
			
				for e = 1, #entries do
					-- io.write("D")
					local entry = ""
					
					if entries[e].lookup == "number"..side then
						entry = ""..Space(balanceTS[task][side]["number"..side], entries[e].str_length)
						-- io.write("|E_/"..entry.."/")
					elseif entries[e].lookup == "somme"..side then
						entry = ""..Space(balanceTS[task][side]["somme"..side], entries[e].str_length)
						-- io.write("|F_/"..entry.."/")
					end
					s = s.. entry
					-- if e ~= #entries then															--if this is not the last entry of the waypoint, add spaces to the next entry	
						-- local space = entries[e].str_length + 3 - string.len(tostring(entry))		--calculate number of spaces that need to be added for alignement (string length of largest entry of same type + 3 - length of current entry = number of spaces)
						-- for n = 1, space * 1.5 do														
							-- s = s .. " "															--add 1.5 spaces for every missing letter
						-- end
					-- end
				end
		
		-- end

		
	end
		
	s = s .. "\\n"

end
print()
print("Nb: ".." Number of plane in oob_air_init ")
print("CAP or Escorte or Intercept Tot : ".." Tot = ((sum_firepower * sum_capability)  /#unit_loadouts)  * unit[n].number ")
print("Other Tot :                       ".." Tot = ((sum_firepower)  /#unit_loadouts)  * unit[n].number ")
local DebugTXT = StringToTxt(s)
print("UTIL_HBP HelpBalancePwer "..DebugTXT)
print()
print("You can change oob_air_init.lua or db_loadout.lua file ")
print("And touch any key for restart the script without closing/opening a dos windows ")
	