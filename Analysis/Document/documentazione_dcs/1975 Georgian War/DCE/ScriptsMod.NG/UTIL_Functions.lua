--Various functions

---------------------------------------------------------------------------------------------------------
-- Old_Boy rev. OB.1.0.1 (CopyFile(), getSkill(), roundAtNumber(), SaveTabOnPath(), SaveTabWithNameOnPath())
-- Miguel Fichier Revision M47.c
------------------------------------------------------------------------------------------------------- 


if not versionDCE then 
	versionDCE = {} 
end

               -- VERSION --

versionDCE["UTIL_Functions.lua"] = "OB.1.0.1"


-- debugC Angle et Bearing des statics sur PA

-- miguel21 modification M47.c keeps the history of the campaign files (c: save debugging information during mission generation)
-- miguel21 modification M43 assignation des numeros de parking du type C08 
-- Miguel21 modification M41 	Scratchpad written in the Sratchpad file, if this modul is installed
-- miguel21 modification M38.e (e:  helps to balance the game (type "Z" in firstmission.bat))(d: checks only the right  theatre) (c: Check conf_mod) Check and Help CampaignMaker
-- miguel21 modification M34.i  custom FrequenceRadio (i  3 frequency bands)(g: VHF helicopter)(h: bug Gazelle)

--function to return txt whith carriage return
function StringToTxt(text)
	text = string.gsub(text, "\\n", "\n")	
	return text
end

--function to return txt whith carriage return for Sratchpad
-- Miguel21 modification M41
function StringToTxtBrief(text)
	if type(text) == "string" then
		text = string.gsub(text, "\\n", " \\\n")		
		return text
	else
		return  text
	end
end

--function to turn a table into a string
function TableSerialization(t, i)
	
	
	
	local text = "{\n"
	local tab = ""
	for n = 1, i + 1 do																	--controls the indent for the current text line
		tab = tab .. "\t"
	end
	for k,v in pairs(t) do
		if type(k) == "string" then
			text = text .. tab .. "['" .. k .. "'] = "
		else
			text = text .. tab .. "[" .. k .. "] = "
		end
		if type(v) == "string" then
			text = text .. "'" .. v .. "',\n"
		elseif type(v) == "number" then
			text = text .. v .. ",\n"
		elseif type(v) == "table" then
			text = text .. TableSerialization(v, i + 1)
		elseif type(v) == "boolean" then
			if v == true then
				text = text .. "true,\n"
			else
				text = text .. "false,\n"
			end
		elseif type(v) == "function" then
			text = text .. v .. ",\n"
		elseif v == nil then
			text = text .. "nil,\n"
		end
	end
	tab = ""
	for n = 1, i do																		--indent for closing bracket is one less then previous text line
		tab = tab .. "\t"
	end
	if i == 0 then
		text = text .. tab .. "}\n"														--the last bracket should not be followed by an comma
	else
		text = text .. tab .. "},\n"													--all brackets with indent higher than 0 are followed by a comma
	end
	return text
end


--function to make a deep copy of a table
function deepcopy(orig)
    local orig_type = type(orig)
    local copy
    if orig_type == 'table' then
        copy = {}
        for orig_key, orig_value in next, orig, nil do
            copy[deepcopy(orig_key)] = deepcopy(orig_value)
        end
        setmetatable(copy, deepcopy(getmetatable(orig)))
    else -- number, string, boolean, etc
        copy = orig
    end
    return copy
end


--function to return heading between two vector2 points
function GetHeading(p1, p2)
	local deltax = p2.x - p1.x
	local deltay = p2.y - p1.y
	if (deltax > 0) and (deltay == 0) then
		return 0
	elseif (deltax > 0) and (deltay > 0) then
		return math.deg(math.atan(deltay / deltax))
	elseif (deltax == 0) and (deltay > 0) then
		return 90
	elseif (deltax < 0) and (deltay > 0) then
		return 90 - math.deg(math.atan(deltax / deltay))
	elseif (deltax < 0) and (deltay == 0) then
		return 180
	elseif (deltax < 0) and (deltay < 0) then
		return 180 + math.deg(math.atan(deltay / deltax))
	elseif (deltax == 0) and (deltay < 0) then
		return 270
	elseif (deltax > 0) and (deltay < 0) then
		return 270 - math.deg(math.atan(deltax / deltay))
	else
		return 0
	end
end

--https://github.com/mrSkortch/MissionScriptingTools/releases
--- Returns heading of given unit.
-- @tparam Unit unit unit whose heading is returned.
-- @param rawHeading
-- @treturn number heading of the unit, in range
-- of 0 to 2*pi.
function getHeadingByPos(unit)
	local unitpos = unit:getPosition()
	if unitpos then
		local Heading = math.atan2(unitpos.x.z, unitpos.x.x)
		if Heading < 0 then
			Heading = Heading + 2*math.pi	-- put heading in range of 0 to 2*pi
		end
		return Heading
	end
end
	
function HeadingDegToRad(angle)
	angle = angle % 360 							-- garde le reste de 360
	return angle * 0.0174532925				-- 0,0174532925
end
	
	
--function to return the angle between two headings
function GetDeltaHeading(h1, h2)
	local delta = h2 - h1
	if delta > 180 then
		delta = delta - 360
	elseif delta <= -180 then
		delta = delta + 360
	end
	return delta
end


--function to return distance between two vector2 points
function GetDistance(p1, p2)
	local deltax = p2.x - p1.x
	local deltay = p2.y - p1.y
	return math.sqrt(math.pow(deltax, 2) + math.pow(deltay, 2))
end


--function to return a new point offset from an initial point
function GetOffsetPoint(point, heading, distance)
	return {
		x = point.x + math.cos(math.rad(heading)) * distance,
		y = point.y + math.sin(math.rad(heading)) * distance
	}
end


--function to return closest distance of point p3 to the line p1 to p2
function GetTangentDistance(p1, p2, p3)
	local p1_p2_heading = GetHeading(p1, p2)
	local p1_p3_heading = GetHeading(p1, p3)
	local alpha = math.abs(p1_p2_heading - p1_p3_heading)
	if alpha > 180 then
		alpha = math.abs(alpha - 360)
	end
	local p1_p3_distance = GetDistance(p1, p3)
	
	local p2_p1_heading = GetHeading(p2, p1)
	local p2_p3_heading = GetHeading(p2, p3)
	
	local beta = math.abs(p2_p1_heading - p2_p3_heading)
	if beta > 180 then
		beta = math.abs(beta - 360)
	end
	local p2_p3_distance = GetDistance(p2, p3)
	
	if alpha > 90 or alpha < -90 then
		return p1_p3_distance
	elseif beta > 90 or beta < -90 then
		return p2_p3_distance
	elseif GetDistance(p1, p2) == 0 then
		return p1_p3_distance
	else
		return math.abs(math.sin(math.rad(alpha)) * p1_p3_distance)
	end
end


--function to return lenght of a line from p1 to p2 that is within a circle c with radius r
function GetTangentLenght(p1, p2, pc, r)
	local p1_pc = GetDistance(p1, pc)
	local p2_pc = GetDistance(p2, pc)
	local p1_p2 = GetDistance(p1, p2)
	
	if (p1.x == pc.x and p1.y == pc.y) or (p2.x == pc.x and p2.y == pc.y) then			--p1 or p2 are the center of the circle
		if p1_p2 > r then																--the other point is outside of the circle
			return r																	--return the circle radius
		else																			--the other point is inside the cicle
			return p1_p2																--return distance from p1 to p2
		end
	elseif p1_pc < r and p2_pc < r then													--p1 and p2 are in circle
		return p1_p2																	--return distance from p1 to p2
	elseif p1_pc < r then																--only p1 is in circle
		local p1_p2_heading = GetHeading(p1, p2)										--heading from p1 to p2
		local p1_pc_heading = GetHeading(p1, pc)										--heading from p1 to pc
		local alpha = math.abs(p1_p2_heading - p1_pc_heading)							--angle in deg		
		local a = r
		local b = p1_pc
		local beta = math.deg(math.asin(b * math.sin(math.rad(alpha)) / a))
		local gamma = 180 - alpha - beta
		local c = a * math.sin(math.rad(gamma)) / math.sin(math.rad(alpha))
		return math.abs(c)
	elseif p2_pc < r then																--only p2 is in circle
		local p2_p1_heading = GetHeading(p2, p1)										--heading from p2 to p1
		local p2_pc_heading = GetHeading(p2, pc)										--heading from p2 to pc
		local alpha = math.abs(p2_p1_heading - p2_pc_heading)							--angle in deg		
		local a = r
		local b = p2_pc
		local beta = math.deg(math.asin(b * math.sin(math.rad(alpha)) / a))
		local gamma = 180 - alpha - beta
		local c = a * math.sin(math.rad(gamma)) / math.sin(math.rad(alpha))
		return math.abs(c)
	else																				--neither p1 or p2 is in circle
		local t = GetTangentDistance(p1, p2, pc)
		return 2 * math.sqrt(math.pow(r, 2) - math.pow(t, 2))
	end
end



--function to return subsequent IDs
id_counter = 100000
function GenerateID()
	local id = id_counter
	id_counter = id_counter + 1
	return id
end


--function to return various date and time formats of a number in seconds
function FormatTime(t, form)
	local hour
	local minute
	local second
		
	hour = math.floor(t / 3600)
	t = t - hour * 3600
	if hour < 10 then
		hour = "0" .. hour
	end
	
	minute = math.floor(t / 60)
	t = t - minute * 60
	if minute < 10 then
		minute = "0" .. minute
	end
	
	second = math.floor(t)
	if second < 10 then
		second = "0" .. second
	end
	
	if form == "hh:mm" then
		return hour .. ":" .. minute
	elseif form == "hh:mm:ss" then
		return hour .. ":" .. minute .. ":" .. second
	end
end


--function to format date
function FormatDate(day, month, year)
	if month == 1 then
		month = "January"
	elseif month == 2 then
		month = "February"
	elseif month == 3 then
		month = "March"
	elseif month == 4 then
		month = "April"
	elseif month == 5 then
		month = "May"
	elseif month == 6 then
		month = "June"
	elseif month == 7 then
		month = "July"
	elseif month == 8 then
		month = "August"
	elseif month == 9 then
		month = "September"
	elseif month == 10 then
		month = "October"
	elseif month == 11 then
		month = "November"
	elseif month == 12 then
		month = "December"
	end
	
	return month .. " " .. day .. ", " .. year
end


--function to format altitude in metric or imperial measurement
function FormatDistance(a)
	a = a / 1000																			--round to km
	if camp.units == "metric" then															--metric units
		a = math.floor(a) .. " km"															--kilometers
	elseif camp.units == "imperial" then													--imperial units
		a = a * 0.539957																	--covert to nm
		a = math.floor(a) .. " nm"															--nautical miles
	end
	return a
end


--function to format altitude in metric or imperial measurement
function FormatAlt(a)
	if camp.units == "metric" then															--metric units
		a = math.ceil(a / 10) * 10															--round to tens
		if a <= 1000 then																	--for altitudes until 1000m
			a = a .. " m AGL"																--meters AGL
		else
			a = a .. " m MSL"																--meters MSL
		end
	elseif camp.units == "imperial" then													--imperial units
		a = a * 3.28																		--covert to feet
		a = math.ceil(a / 100) * 100														--round to hunderts
		if a <= 3300 then																	--for altitudes until 3300ft
			a = a .. " ft AGL"																--feet AGL
		else
			a = a .. " ft MSL"																--feet MSL
		end
	end
	return a
end


--function to format speed in metric or imperial measurement
function FormatSpeed(a)
	if camp.units == "metric" then															--metric units
		a = a * 3.6
		a = math.floor(a / 10) * 10															--round to tens
		a = a .. " kph"																		--km per hour
	elseif camp.units == "imperial" then													--imperial units
		a = a * 1.94																		--covert to knots
		a = math.floor(a / 5) * 5															--round to fives
		a = a .. " kts"																		--knots
	end
	return a
end


--function to replace certain type names
function ReplaceTypeName(s)
	if TypeAlias and TypeAlias[s] then
		return TypeAlias[s]
	else
		return s
	end
end




 function _affiche(_table, titre, prof)
 
 if not prof or prof == nil then prof = 999 end 						-- prof = profondeur de niveau dans la hierarchie
  print()
   print()
    print()
    if titre == nil then print( string.format(" _affiche() titre = nil ")) 
    elseif type( titre) == "string" then
		print( string.format(" _affiche(titre) "..tostring(titre)))
	end
  
	if type( _table) == "table"  then
	
		for a, b in pairs(_table) do 
		
			if  type(b) ~= "table" then
				print(" _affiche(a b)     "..tostring(a).." "..tostring(b))
			elseif type(b) == "table"   and prof >= 2 then
				for c, d in pairs(b) do
					print( " _affiche(a c)     "..tostring(a).."   "..tostring(c))
					
					
					if type(d)~= "table"  then
						print( " _affiche(d)                "..tostring(d))
					elseif type(d) == "table"  and prof >= 3 then
						for e, f in pairs(d) do							
							
							if type( f ) ~= "table"  then
								print( " _affiche(e f)                          "..tostring(e).." "..tostring(f))
							elseif type( f ) == "table"  and prof >= 4 then
								for g, h in pairs(f) do
									print( " _affiche(  e)                     "..tostring(e))									
									
									if type( h ) ~= "table"  then
										print( " _affiche(g h)                                    "..tostring(g).." "..tostring(h))	
									elseif type( h ) == "table"  and prof >= 5 then
										for i, j in pairs(h) do										
										
											if type( j ) ~= "table"  then
												print( " _affiche(i j)                                              "..tostring(i).." "..tostring(j))
											elseif type( j ) == "table" and prof >= 6 then									
												for k, l in pairs(j) do
													print( " _affiche(k)                                                   "..tostring(k))
													
													if type( l ) ~= "table"  then
														print( " _affiche(l)                                                   "..tostring(l))
													elseif type( l ) == "table" and prof >= 7 then
														for m, n in pairs(l) do
															print( " _affiche(m)                                                        "..tostring(m))
														
															if type( n ) ~= "table"  then
																print( " _affiche(n)                                                             "..tostring(n))
															elseif type( n ) == "table"  and prof >= 8 then
																print( " n est une table                                                              "..tostring(n).."---------------------------")
												  
															end --if
														end --for l
													end --if
												end -- for j
											end --if
										end -- for h
									end --if
								end --for f
							end --elseif
						end -- for d
					end -- if d
				end -- for v
			end -- if v
		end  -- for _table
	
	else print( "_affiche NoTable==> " ..tostring(_table))
	
	end -- if if type( _table) == "table"
	
end -- function affiche

function _afficheTXT(_table, titre, prof)


	--export custom mission log
	local logExp = "logExp  " 
		
 if not prof or prof == nil then prof = 999 end 						-- prof = profondeur de niveau dans la hierarchie
  logExp = logExp.."\n"
  
    if titre == nil then logExp = logExp.. string.format(" _affiche() titre = nil ")
    elseif type( titre) == "string" then
		logExp = logExp.. string.format(" _affiche(titre) "..tostring(titre)).."\n"
	end
  
	if type( _table) == "table"  then --and  (table.getn(_table) ~= 0 or table.getn(_table) ~= nil
	
		for a, b in pairs(_table) do --for a, b in pairs(event.initiator) do --for a, b in pairs(_ammo) do
		
			if  type(b) ~= "table" then
				logExp = logExp.." _affiche (a b)     "..tostring(a).." "..tostring(b).."\n"
			elseif type(b) == "table"   and prof >= 2 then
				for c, d in pairs(b) do
					logExp = logExp.. " _affiche(a c)           "..tostring(a).." "..tostring(c).."\n"
					
					
					if type(d)~= "table"  then
						logExp = logExp.. " _affiche(d)                "..tostring(d).."\n"
					elseif type(d) == "table"  and prof >= 3 then
						for e, f in pairs(d) do
							
							if type( f ) ~= "table"  then
								logExp = logExp.. " _affiche(e f)                          "..tostring(e).." "..tostring(f).."\n"
							elseif type( f ) == "table"  and prof >= 4 then
								logExp = logExp.. " _affiche( e)                                "..tostring(e).."\n"
								for g, h in pairs(f) do
									logExp = logExp.. " _affiche(Ig)                                 "..tostring(g).."\n"
									
									
									if type( h ) ~= "table"  then
										logExp = logExp.. " _affiche(g h)                                    "..tostring(g).." "..tostring(h).."\n"	
									elseif type( h ) == "table"  and prof >= 5 then
										logExp = logExp.. " _affiche( g)                                         "..tostring(g).."\n"
										for i, j in pairs(h) do
										
											if type( j ) ~= "table"  then
												logExp = logExp.. " _affiche(i j)                                              "..tostring(i).." "..tostring(j).."\n"
											elseif type( j ) == "table" and prof >= 6 then									
												logExp = logExp.. " _affiche(i)                                                  "..tostring(i).."\n"
												for k, l in pairs(j) do													
													
													if type( l ) ~= "table"  then
														logExp = logExp.. " _affiche(k l)                                                   "..tostring(k).." "..tostring(l).."\n"
													elseif type( l ) == "table" and prof >= 7 then
														logExp = logExp.. " _affiche(k)                                                       "..tostring(k).."\n"
														for m, n in pairs(l) do
															logExp = logExp.. " _affiche(m)                                                        "..tostring(m).."\n"
														
														
															if type( n ) ~= "table"  then
																logExp = logExp.. " _affiche(m n)                                                   "..tostring(m).." "..tostring(n).."\n"
															elseif type( n ) == "table" and prof >= 7 then
																logExp = logExp.. " _affiche(m)                                                       "..tostring(m).."\n"
																for o, p in pairs(n) do
																	logExp = logExp.. " _affiche(o)                                                        "..tostring(o).."\n"
														
														
																	if type( p ) ~= "table"  then
																		logExp = logExp.. " _affiche(p)                                                             "..tostring(p).."\n"
																	elseif type( p ) == "table"  and prof >= 8 then
																		logExp = logExp.. " p est une table                                                              "..tostring(p).."---------------------------".."\n"
																			
																	end
																end
															end --if
														end --for l
													end --if
												end -- for j
											end --if
										end -- for h
									end --if
								end --for f
							end --elseif
						end -- for d
					end -- if d
				end -- for v
			end -- if v
		end  -- for _table
	
	else logExp = logExp.. "_affiche NoTable==> " ..tostring(_table).."\n"
	
	end -- if if type( _table) == "table"
	
	return logExp
	
end -- function affiche

--function pour assigner les fr�quences pour tout le monde, Plane and vehicle (EWR)
-- miguel21 modification M34.i  custom FrequenceRadio (i  3 frequency bands)(g: VHF helicopter)(h: bug Gazelle)

function CreatePlageFrequency()																				--trouve une plage de frequence commune si c'est possible
	local activeVHF = false
	camp.radio = {}
	
	local TempRadio = {
		["blue"] = {
			-- [1] = {
			-- },
		},
		["red"] = {
			-- [1] = {
			-- },
		},
	}

	-- miguel21 modification M38.g (g: prise en compte des 3 bandes de fr�quence)(e: priority to the player's frequencies)
	for side, oob_side in pairs(oob_air) do
		for n, sqd in pairs(oob_side) do
			if not sqd.inactive and sqd.player then
				if frequency[sqd.type] then					
					for n = 1,  #frequency[sqd.type].radio do	
						for bandFreq, value in pairs(frequency[sqd.type].radio[n]) do
							if bandFreq == "FM" or bandFreq == "VHF"  or bandFreq == "LVHF" or bandFreq == "UHF" then								
								
								if not TempRadio[side][n] then TempRadio[side][n] = {} end	
								if not TempRadio[side][n][bandFreq] then TempRadio[side][n][bandFreq] = {} end
								
								TempRadio[side][n][bandFreq].min = value.min
								TempRadio[side][n][bandFreq].max = value.max
							end
						end					
					end				
				end
			end
		end
	end	
	-- _affiche(TempRadio, "UTIL_F 1er TempRadio")
	
	for side, oob_side in pairs(oob_air) do
		for n, sqd in pairs(oob_side) do
			if not sqd.inactive then
				if frequency[sqd.type] then
					for typeRadio , PlaneFreqRadio in pairs(frequency[sqd.type]) do	
						if typeRadio == "radio" and type(PlaneFreqRadio) == "table" then
							for nr , _bandFreq in pairs(PlaneFreqRadio) do	--for nr , value in pairs(frequency[sqd.type].radio) do
								for bandFreq , value in pairs(_bandFreq) do		
									if bandFreq == "FM" or bandFreq == "VHF" or bandFreq == "UHF" then		
			
										if not TempRadio[side][nr] then TempRadio[side][nr] = {} end	
										if not TempRadio[side][nr][bandFreq] then TempRadio[side][nr][bandFreq] = {} end
										if not TempRadio[side][nr][bandFreq].min then TempRadio[side][nr][bandFreq].min = value.min  end
										if not TempRadio[side][nr][bandFreq].max then TempRadio[side][nr][bandFreq].max = value.max  end
								
										if (value.min < TempRadio[side][nr][bandFreq].max)  then								--si une plage radio est en dehors des autres, on privil�gie le joueur
											if value.min > TempRadio[side][nr][bandFreq].min then 
												TempRadio[side][nr][bandFreq].min =  value.min	
											end
											
											if (value.max < TempRadio[side][nr][bandFreq].max) and (value.max > TempRadio[side][nr][bandFreq].min )  then 
												TempRadio[side][nr][bandFreq].max =  value.max
											end
										end
									end
								end
							end
						elseif typeRadio == "frequency"  then											-- frequence de base utilis� par FC3 ou gazelle
								print("UTIL_F Type No Frequency FC3? "..sqd.type)
						end
					end
				else
					-- print("UTIL_F Type No Frequency "..sqd.type)
				end
			end
		end
	end

	camp.radio = TempRadio
	-- _affiche(camp.radio, "UTIL_F camp.radio")

end


----- function to assign frquencies to packages -----
assigned_freq = {}														--table to store frequencies in use
package_freq = {															--table to store frequencies assigned to packages
	["blue"] = {
		["UHF"] = {},
		["VHF"] = {},
		["FM"] = {},		
	},
	["red"] = {
		["UHF"] = {},
		["VHF"] = {},
		["FM"] = {},
	},
}
function GetFrequency(side, targetname,  task , type, waves)
	local freq
	local radio_n = 1															--chose frequency range from radio 1
	if camp.radio[side][2] and (task == "EWR" or task == "AWACS" or task == "Refueling") then			--if player has two radions, chose frequency range from AWACS and tanker from radio 2
		radio_n = 2
	end

	if package_freq[side]["UHF"][targetname] then
		return package_freq[side]["UHF"][targetname]									--return frequency
	elseif package_freq[side]["VHF"][targetname] then
		return package_freq[side]["VHF"][targetname]									--return frequency
	elseif package_freq[side]["FM"][targetname] then
		return package_freq[side]["FM"][targetname]									--return frequency
	end

	local function GetLocFrequency(side, targetname, nRadio, range)
		if range == "UHF" then
			if camp.radio[side][nRadio] and camp.radio[side][nRadio][range] then		--Cherche d'abord une frequence UHF commune
				repeat
					freq = math.random(camp.radio[side][nRadio][range].min, camp.radio[side][nRadio][range].max - 1)		--find random frequency in mHz
					local deci = math.random(0, 9) / 10									--random first decimal place
					local mil = math.random(0, 3) * 25 / 1000							--random second and third decimal place (00/25/50/75)
					freq = freq + deci + mil											--combine to complete frequency
				until assigned_freq[freq] == nil										--repeat until a frequency is found that is not yet in use

				assigned_freq[freq] = true												--mark frequency in use
				package_freq[side][range][targetname] = freq									--store frequency for package
				return freq																--return frequency
			end
		elseif range == "VHF" then
			if camp.radio[side][nRadio] and camp.radio[side][nRadio][range] then	--Cherche ensuite une frequence VHF
				repeat
					freq = math.random(camp.radio[side][nRadio][range].min, camp.radio[side][nRadio][range].max - 1)		--find random frequency in mHz
					local deci = math.random(0, 9) / 10									--random first decimal place
					local mil = math.random(0, 3) * 25 / 1000							--random second and third decimal place (00/25/50/75)
					freq = freq + deci + mil											--combine to complete frequency
				until assigned_freq[freq] == nil										--repeat until a frequency is found that is not yet in use

				assigned_freq[freq] = true												--mark frequency in use
				package_freq[side][range][targetname] = freq									--store frequency for package
				return freq																--return frequency
			end
		elseif range == "FM" then				
			if camp.radio[side][nRadio] and camp.radio[side][nRadio][range] then	--Cherche enfin une frequence FM
				repeat
					freq = math.random(camp.radio[side][nRadio][range].min, camp.radio[side][nRadio][range].max - 1)		--find random frequency in mHz
				until assigned_freq[freq] == nil										--repeat until a frequency is found that is not yet in use

				assigned_freq[freq] = true												--mark frequency in use
				package_freq[side][range][targetname] = freq									--store frequency for package
				return freq																--return frequency
			end	
		end
	end



	
--TODO faire des functions pour nettoyer ce code
	if type and type ~= false and type ~= nil then
		if frequency[type]  and frequency[type].prefFreqPackage  then
			result = GetLocFrequency(side, targetname, frequency[type].prefFreqPackage.nRadio,  frequency[type].prefFreqPackage.range)
			return result
		end
	end
	local result = GetLocFrequency(side, targetname, radio_n,  "UHF")
	
	if result then	
		return result	
	else 
		result = GetLocFrequency(side, targetname, radio_n,  "VHF")
		if result then	
			return result
		else 
			result = GetLocFrequency(side, targetname, radio_n,  "FM")
			if result then	
				return result
			else 
				if not camp.radio[side] then camp.radio[side] = {} end
				if not camp.radio[side][radio_n] then camp.radio[side][radio_n] = {} end
				if not camp.radio[side][radio_n]["VHF"] then camp.radio[side][radio_n]["VHF"]  = {} end
				camp.radio[side][radio_n]["VHF"] = {
					min = 118,
					max = 136,
				}
				result = GetLocFrequency(side, targetname, radio_n,  "VHF")
				return result				
			end
		end
	end
end


-- http://www.lua.org/pil/19.3.html
-- Trier un tableau A[b] en le classant par A, et non b... pas simple .. ^^
function pairsByKeys (t, f)
	local a = {}
	for n in pairs(t) do table.insert(a, n) end
		table.sort(a, f)
		local i = 0      -- iterator variable
		local iter = function ()   -- iterator function
		i = i + 1
		if a[i] == nil then return nil
		else return a[i], t[a[i]]
		end
	end
	return iter
end
	
	

-- miguel21 modification M38.d Check and Help CampaignMaker
	
function CheckConfModMaster()
	function CheckConfMod( check, _table, chapter)		
		for key1, value1 in pairs(check) do
			if  _table[key1] == nil then
				print(" (0a) ATTENTION: the variable: "..key1.." was not found in the conf_mod file, chapter: "..chapter)
				os.execute 'pause'
			end
			
			local stopCTRL = false
			if type(value1) == "table" then
				for key2, value2 in pairs(value1) do
					if  _table[key1][key2] == nil and key1 ~= "MovedBullseye" then
						print(" (0b) ATTENTION: the variable: "..key1.." "..key2.." was not found in the conf_mod file, chapter: "..chapter)
						os.execute 'pause'
					elseif  key1 == "MovedBullseye" then 
						local test_theatre = string.lower(mission.theatre)
						stopCTRL = true
						key2 = test_theatre
						if  _table[key1][test_theatre] == nil  then
							print(" (0bb) ATTENTION: the variable: "..key1.." "..test_theatre.." was not found in the conf_mod file, chapter: "..chapter)
							os.execute 'pause'
						end
					end
							
					if type(value2) == "table"  then
						for key3, value3 in pairs(value2) do
							-- print("1: "..tostring(key1).." ".." 2: "..tostring(key2).." ".." 3: "..tostring(key3))
							if  _table[key1][key2][key3] == nil then
								print(" (0c) ATTENTION: the variable: "..key1.." "..key2.." "..key3.." was not found in the conf_mod file, chapter: "..chapter)
								os.execute 'pause'
							end
							
							if type(value3) == "table"  then
								for key4, value4 in pairs(value3) do
									if  _table[key1][key2][key3][key4] == nil then
										print(" (0d) ATTENTION: the variable: "..key1.." "..key2.." "..key3.." "..key4.." was not found in the conf_mod file, chapter: "..chapter)
										os.execute 'pause'
									end
									
									if type(value4) == "table" then
										for key5, value5 in pairs(value4) do
											if  _table[key1][key2][key3][key4][key5] == nil then
												print(" (0e) ATTENTION: the variable: "..key1.." "..key2.." "..key3.." "..key4.." "..key5.." was not found in the conf_mod file, chapter: "..chapter)
												os.execute 'pause'
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
	
	--["theatre"] = "PersianGulf",
	
	dofile("../../../ScriptsMod."..versionPackageICM.."/conf_mod_check.lua")

	CheckConfMod(mission_ini_check, mission_ini, "mission_ini")
	CheckConfMod(mission_forcedOptions_check, mission_forcedOptions, "mission_forcedOptions")
	CheckConfMod(AddPropAircraft_check, AddPropAircraft, "AddPropAircraft")
	CheckConfMod(Debug_check, Debug, "Debug")
	CheckConfMod(campMod_check, campMod, "campMod")
	CheckConfMod(playable_m_check, playable_m, "playable_m")

end


--M43 assignation des numeros de parking du type C08 
parkOccupied = {}
function GetParkingId(parkingId, base)
	local s	
	local counter
	if not parkOccupied[base]  then										
		parkOccupied[base] = {}												
	end

	for prefix, value in pairs(parkingId) do
		counter = 0
		if #value == 2 then
			lower = value[1]
			upper = value[2]
			
			repeat
				counter = counter + 1
				s = math.random(tonumber(lower), tonumber(upper))		
				s = prefix..string.format("%02d", s)
			until parkOccupied[base][s] == nil 	or counter == 100				
			
		elseif #value > 2 then
			repeat
				counter = counter + 1
				local r = math.random(1,#value)
				s = value[r]
				s = prefix..string.format("%02d", s)
			until parkOccupied[base][s] == nil 	or counter == 100					
		end
		if parkOccupied[base][s] == nil then
			break
		end
	end
	
	--ne trouve pas de place libre:
	if counter >= 100 then
		return false
	end
	parkOccupied[base][s] = true

	return tostring(s)

end

-- MARCO copy file
function CopyFile(old_path, new_path)
	local old_file = io.open(old_path, "rb")
	local new_file = io.open(new_path, "wb")
	local old_file_sz, new_file_sz = 0, 0
	if not old_file or not new_file then
	  return false
	end
	while true do
	  local block = old_file:read(2^13)
	  if not block then 
		old_file_sz = old_file:seek( "end" )
		break
	  end
	  new_file:write(block)
	end
	old_file:close()
	new_file_sz = new_file:seek( "end" )
	new_file:close()
	return new_file_sz == old_file_sz
end

function SaveTabOnPath( path, table_name, table )
    -- path = "Active/"
    local tgt_str = table_name .. " = " .. TableSerialization(table, 0)						    --make a string
    local tgtFile = io.open(path .. table_name .. ".lua", "w")
    tgtFile:write(tgt_str)																		--save new data
    tgtFile:close()
end

function SaveTabWithNameOnPath( path, table_file, table_name, table )
    -- path = "Active/"
    local tgt_str = table_name .. " = " .. TableSerialization(table, 0)						    --make a string
    local tgtFile = io.open(path .. table_file .. ".lua", "w")
    tgtFile:write(tgt_str)																		--save new data
    tgtFile:close()
end

-- return random skill within min_skill and max_kill. If min_skill = nil -> min_skill = Random or max_skill = nil -> max_skill = Random
function getSkill(min_skill, max_skill)
	local skill = {"Average" , "Good", "High", "Excellent"}
	local skill_found
	local compute_skill

	if min_skill and type(min_skill) == "string" then
		skill_found = false

		for n = 1, 4 do
			
			if skill[n] == min_skill then 
				skill_found = true
				min_skill = n
				break
			end
		end

		if not skill_found then
			min_skill = math.random(1,4)
		end
	
	elseif type(min_skill) ~= "number" or min_skill < 1 or min_skill > 4 then
		min_skill = math.random(1,4)
	end

	if max_skill and type(max_skill) == "string" then
		skill_found = false

		for n = 1, 4 do
			
			if skill[n] == max_skill then 
				skill_found = true
				max_skill = n
				break
			end
		end

		if not skill_found then
			max_skill = math.random(1,4)
		end
	
	elseif type(max_skill) ~= "number" or max_skill < 1 or max_skill > 4 then
		max_skill = math.random(1,4)
	end

	if min_skill >= max_skill then
		compute_skill = skill[min_skill]
	
	else
		compute_skill = skill[ math.random(min_skill, max_skill)]
	end
	return compute_skill
end

-- return x round at number ()
function roundAtNumber(x, number)
	number = number or 1
	
	if number > x then
		return x -- original false
	end
	x = x / number
	return (x > 0 and math.floor(x + .5) or math.ceil(x - .5)) * number
end

-- activate log
function activateLog(activate, condition, log_var, log_level)
	
	if activate and condition then		
		log_var.level = log_level
		log_var.activate = true
		log_var.info("activateLog")
		return true
	
	elseif not activate then		
		log_var.level = log_level
		log_var.activate = false
		log_var.info("de-activateLog")
		return false
	end
end
  