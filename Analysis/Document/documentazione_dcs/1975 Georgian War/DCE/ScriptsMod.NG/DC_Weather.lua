--Weather
--Initiated by MAIN_NextMission.lua
------------------------------------------------------------------------------------------------------- 
------------------------------------------------------------------------------------------------------- 
-- Miguel Fichier Revision M45.e + DC_W_Debug01c
------------------------------------------------------------------------------------------------------- 

-- DC_W_Debug01c %chance pHigh pLow 
-- miguel21 modification M45.e : compatible with 2.7.0s  (e: debug cleaning)(d: less clounds in the PG)(c: debugWeather)

if not versionDCE then versionDCE = {} end
versionDCE["DC_Weather.lua"] = "1.2.5"

-- =====================  Marco implementation ==================================
local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua")
-- NOTE MARCO: prova a caricarlo usando require(".. . .. . .. .ScriptsMod."versionPackageICM..".UTIL_Log.lua")
-- NOTE MARCO: https://forum.defold.com/t/including-a-lua-module-solved/2747/2
log.level = LOGGING_LEVEL
log.outfile = LOG_DIR .. "LOG_DC_Weather." .. camp.mission .. ".log" 
local local_debug = true -- local debug   
log.info("Start")
-- =====================  End Marco implementation ==================================


local debugWeather = false


local FieldElevation = 0												--elevation of players airfield used for minimum cloud base
for side,unit in pairs(oob_air) do										--iterate through all sides
	for n = 1, #unit do													--iterate through all units
		if unit[n].player then											--find player unit
			FieldElevation = db_airbases[unit[n].base].elevation		--get field elevation of player base
			if FieldElevation == nil then
				FieldElevation = 0
			end
			break
		end
	end
end


if debugWeather then print("time              "..tostring((camp.day - 1) * 86400 + camp.time)) end	
if debugWeather then print("camp.weather.zoneEnd "..tostring(camp.weather.zoneEnd)) end	

-- print("time              "..tostring((camp.day - 1) * 86400 + camp.time))
-- print("camp.weather.zoneEnd "..tostring(camp.weather.zoneEnd))


mission.weather["atmosphere_type"] = 0									--set simple weather model
local InitalW = false

--Initial weather
if camp.weather.zone == nil then										--no weather exists yet
	camp.weather.zoneTemp = math.random(camp.weather.refTemp - 5, camp.weather.refTemp + 5)				--Set temperature of weather zone (+/- 5°C of reference tempereature)
	camp.weather.zoneNextTemp = math.random(camp.weather.refTemp - 5, camp.weather.refTemp + 5)			--Set temperature of next weather zone (+/- 5°C of reference tempereature)
	
	-- local chance = 100 / (camp.weather.pHigh + camp.weather.pLow) * camp.weather.pHigh					--chance of next weather zone being a high pressure system
	--DC_W_Debug01
	local ProbaPhight = (camp.weather.pHigh / (camp.weather.pHigh + camp.weather.pLow)) * 100					--chance of next weather zone being a high pressure system
	local randChance = math.random(1, 100)
	if debugWeather then print("Initial weather: "..tostring(randChance).. "<=? "..tostring(ProbaPhight)) end	
	
	if randChance <= ProbaPhight   then								--High pressure system
		if debugWeather then print("YES camp.weather.zoneNext = high" ) end
		camp.weather.zoneNext = "high"									--set next weather zone
	else																--Low pressure system
		local rando = math.random(1,4)
		if debugWeather then print("NO rando: " ..rando) end
		
		if rando == 1 then
			camp.weather.zoneNext = "low sector cold"					--next zone is a cold sector
		elseif rando == 2 then
			camp.weather.zoneNext = "low sector warm"					--next zone is a warm sector
		elseif rando == 3 then
			camp.weather.zoneNext = "low front cold"					--Next zone is a cold front
		elseif rando == 4 then
			camp.weather.zoneNext = "low front warm"					--Next zone is a warm front
		end
	end
	
	camp.weather.zoneEnd = -1											--Current (non-existing) zone end negative to trigger weather change
	InitalW = true
end 



if debugWeather then print("camp.weather.zoneTemp: " ..tostring(camp.weather.zoneTemp)) end
if debugWeather then print("camp.weather.zone: " ..tostring(camp.weather.zone)) end


if debugWeather then print("camp.weather.zoneNext: " ..camp.weather.zoneNext) end
local elapsed_time = (camp.day - 1) * 86400 + camp.time					--elapsed time since campaign start in seconds


--Weather change
if elapsed_time > camp.weather.zoneEnd then								--active weather zone has ended

	--Active zone
	camp.weather.zone = camp.weather.zoneNext							--make next weather zone the active weather zone
	camp.weather.zoneStart = camp.weather.zoneEnd						--time active weather zone has started
	if camp.weather.zone == "high" then
		camp.weather.zoneEnd = elapsed_time + math.random(86400, 432000)	--set duration of current weather zone (between 1 and 5 days for High system)
		camp.weather.zoneTemp = camp.weather.zoneNextTemp				--make next weather zone temperature the current temperature
	elseif camp.weather.zone == "low front cold" then
		camp.weather.zoneEnd = elapsed_time + math.random(14400, 28800)	--set duration of current weather zone (between 4 and 8 hours for cold front)
	elseif camp.weather.zone == "low front warm" then
		camp.weather.zoneEnd = elapsed_time + math.random(43200, 86400)	--set duration of current weather zone (between 12 and 24 hours for warm front)
	elseif camp.weather.zone == "low sector cold" then
		camp.weather.zoneEnd = elapsed_time + math.random(21600, 172800)	--set duration of current weather zone (between 6 and 48 hours for cold sector)
		camp.weather.zoneTemp = camp.weather.zoneNextTemp				--make next weather zone temperature the current temperature
	elseif camp.weather.zone == "low sector warm" then
		camp.weather.zoneEnd = elapsed_time + math.random(21600, 172800)	--set duration of current weather zone (between 6 and 48 hours for warm sector)
		camp.weather.zoneTemp = camp.weather.zoneNextTemp				--make next weather zone temperature the current temperature
	end
	
	--Next zone
	camp.weather.zoneNextTemp = math.random(camp.weather.refTemp - 5, camp.weather.refTemp + 5)			--Set temperature of next weather zone (+/- 5°C of reference tempereature)
	
	if  not InitalW then 																		-- evite de passer 2 fois le random lors de la premiere mission
		
		-- local chance = 100 / (camp.weather.pHigh + camp.weather.pLow) * camp.weather.pHigh					--chance of next weather zone being a high pressure system
		local ProbaPhight = (camp.weather.pHigh / (camp.weather.pHigh + camp.weather.pLow)) * 100					--chance of next weather zone being a high pressure system
		local randChance = math.random(1, 100)
			if debugWeather then print("Next zone: "..tostring(randChance).. "<=? "..tostring(ProbaPhight)) end	
			
		if randChance <= ProbaPhight   then								--High pressure system
			camp.weather.zoneNext = "high"									--set next weather zone		
		else																--Low pressure system
			if camp.weather.zone == "low front cold" then					--active zone is a cold front
				camp.weather.zoneNext = "low sector cold"					--next zone is a cold sector
			elseif camp.weather.zone == "low front warm" then				--active zone is a warm front
				camp.weather.zoneNext = "low sector warm"					--next zone is a warm sector
			else															--active zone is a sector (warm or cold), next zone is a front (warm or cold)
				if camp.weather.zoneTemp > camp.weather.zoneNextTemp then	--Next zone is colder
					camp.weather.zoneNext = "low front cold"				--Next zone is a cold front
				elseif camp.weather.zoneTemp < camp.weather.zoneNextTemp then	--Next zone is warmer
					camp.weather.zoneNext = "low front warm"				--Next zone is a warm front
				else														--Next zone has same tempreature
					camp.weather.zoneNext = camp.weather.zone				--Next zone remains the same (warm or cold sectior)
				end
			end
		end
	end
end


-- print("camp.weather.zone "..tostring(camp.weather.zone))
if debugWeather then print("camp.weather.zone "..tostring(camp.weather.zone)) end	

preset = {
	[1] = {
		altiMin = 840,
		altiMax = 4100,
		name = "Preset1",
		nameVignette = "Light Scattered 1",				--ok	ok
		["thickness"] = 200,
	},
	[2] = {
		altiMin = 1260,
		altiMax = 2520,
		name = "Preset2",
		nameVignette = "Light Scattered 2",				--ok	ok
		["thickness"] = 200,
	},
	[3] = {
		altiMin = 840,
		altiMax = 2520,
		name = "Preset3",
		nameVignette = "Hight Scattered 1",				--ok	ok
	},
	[4] = {
		altiMin = 1260,
		altiMax = 2520,
		name = "Preset4",
		nameVignette = "Hight Scattered 2",				--ok	ok
	},
	[5] = {
		altiMin = 1260,
		altiMax = 4620,
		name = "Preset5",
		nameVignette = "Scattered 1",					--okok				
	},
	[6] = {
		altiMin = 1260,
		altiMax = 4200,
		name = "Preset6",
		nameVignette = "Scattered 2",					--okok
	},
	[7] = {
		altiMin = 1680,
		altiMax = 5040,
		name = "Preset7",
		nameVignette = "Scattered 3",					--okok
	},
	[8] = {
		altiMin = 3780,
		altiMax = 5460,
		name = "Preset8",
		nameVignette = "Hight Scattered 3",				--ok	ok
	},
	[9] = {
		altiMin = 1680,
		altiMax = 3780,
		name = "Preset9",
		nameVignette = "Scattered 4",				--ok	ok
	},
	[10] = {
		altiMin = 1260,
		altiMax = 4200,
		name = "Preset10",
		nameVignette = "Scattered 5",				-- OK	ok
	},
	[11] = {
		altiMin = 2520,
		altiMax = 5460,
		name = "Preset11",
		nameVignette = "Scattered 6",				--okok
	},
	[12] = {
		altiMin = 1680,
		altiMax = 3360,
		name = "Preset12",
		nameVignette = "Scattered 7",					--okok
	},
	[13] = {
		altiMin = 1680,
		altiMax = 3360,
		name = "Preset13",
		nameVignette = "Broken 1",					--okok
	},
	[14] = {
		altiMin = 1680,
		altiMax = 3360,
		name = "Preset14",
		nameVignette = "Broken 2",					--okok
	},
	[15] = {
		altiMin = 840,
		altiMax = 5040,
		name = "Preset15",
		nameVignette = "Broken 3",
	},
	[16] = {
		altiMin = 1260,
		altiMax = 4200,
		name = "Preset16",
		nameVignette = "Broken 4",
	},
	[17] = {
		altiMin = 0,
		altiMax = 2520,
		name = "Preset17",
		nameVignette = "Broken 5",
	},
	[18] = {
		altiMin = 0,
		altiMax = 3780,
		name = "Preset18",
		nameVignette = "Broken 6",
	},
	[19] = {
		altiMin = 0,
		altiMax = 2940,
		name = "Preset19",
		nameVignette = "Broken 7",
	},
	[20] = {
		altiMin = 0,
		altiMax = 3780,
		name = "Preset20",
		nameVignette = "Broken 8",					--okok
	},
	[21] = {
		altiMin = 1260,
		altiMax = 4200,
		name = "Preset21",
		nameVignette = "Overcast 1",				--okok
	},
	[22] = {
		altiMin = 420,
		altiMax = 4200,
		name = "Preset22",
		nameVignette = "Overcast 2",
	},
	[23] = {
		altiMin = 840,
		altiMax = 3360,
		name = "Preset23",
		nameVignette = "Overcast 3",
	},
	[24] = {
		altiMin = 420,
		altiMax = 2520,
		name = "Preset24",
		nameVignette = "Overcast 4",
	},
	[25] = {
		altiMin = 420,
		altiMax = 3360,
		name = "Preset25",
		nameVignette = "Overcast 5",
	},
	[26] = {
		altiMin = 420,
		altiMax = 2940,
		name = "Preset26",
		nameVignette = "Overcast 6",
	},
	[27] = {
		altiMin = 420,
		altiMax = 2520,
		name = "Preset27",
		nameVignette = "Overcast 7",				--OK ok
	},
	[28] = {
		altiMin = 420,
		altiMax = 2500,
		name = "RainyPreset1",
		nameVignette = "Overcast And Rain 1",		--okok
	},
	[29] = {
		altiMin = 840,
		altiMax = 2520,
		name = "RainyPreset2",
		nameVignette = "Overcast And Rain 2",
	},
	[30] = {
		altiMin = 840,
		altiMax = 2520,
		name = "RainyPreset3",
		nameVignette = "Overcast And Rain 2",	--okok
	},
}


--Set current weather
----- HIGH -----
if camp.weather.zone == "high" then
	
	if camp.weather.zoneTemp >= 30 then				--si T° sup= à 30: aucun nuage, on se passe du nouveau systeme de nuage de DCS
		Rmini = 0
		Rmaxi = 0
	elseif camp.weather.zoneTemp >= 25 then				--si T° sup= à 25: proba entre ancien systeme (pas de nuage) et les 2 premiers nuages du nouveau systeme DCS
		Rmini = 0
		Rmaxi = 2
	else											--sinon, proba entre les 4 premiers nuages du nouveau systeme DCS
		Rmini = 1
		Rmaxi = 5
	end
	
	presetMiss = ""
	baseChoice = 0
	PresetChoice = math.random(Rmini, Rmaxi)
	
	if PresetChoice ~= 0 then
		baseChoice =  math.random(preset[PresetChoice].altiMin, preset[PresetChoice].altiMax)		
		presetMiss = preset[PresetChoice].name
	end
	
	--clouds
	mission.weather["clouds"] = {
		["thickness"] = 0,
		["density"] = 0,
		["base"] = baseChoice,
		["iprecptns"] = 0,
		["preset"] = presetMiss,
	}

	--wind
	local windDir = math.random(0, 359)
	local windSpeed = math.random(0, 5)
	mission.weather["wind"] = {
		["at8000"] = 
		{
			["speed"] = windSpeed * 2.5,
			["dir"] = windDir,
		},
		["at2000"] = 
		{
			["speed"] = windSpeed * 0.8,
			["dir"] = windDir,
		},
		["atGround"] = 
		{
			["speed"] = windSpeed,
			["dir"] = windDir,
		},
	}
	
	--turbulence
	mission.weather["turbulence"] = {
		["at8000"] = math.random(0, 10),
		["at2000"] = math.random(0, 10),
		["atGround"] = math.random(0, 10),
	}
	
	--temperature
	mission.weather["season"]["temperature"] = camp.weather.zoneTemp
	
	--pressure
	mission.weather["qnh"] = math.random(760, 780)

	
----- COLD FRONT -----
elseif camp.weather.zone == "low front cold" then
	
	local front_remaining = (camp.weather.zoneEnd - elapsed_time) / 3600					--hours until end of cold front
	local front_duration = (camp.weather.zoneEnd - camp.weather.zoneStart) / 3600			--duration of the front in hours
	local strength = 10 - front_remaining * 10 / front_duration								--strength of the front on a scale of 0-10
	
	--clouds
	PresetChoice = math.random(25, 30)
	baseChoice =  math.random(preset[PresetChoice].altiMin, preset[PresetChoice].altiMax)
	
	mission.weather["clouds"] = {
		["thickness"] = math.random(4000, 8000),
		["density"] = math.random(9, 10),
		-- ["base"] = FieldElevation + math.random(100, 500),
		["base"] = FieldElevation + baseChoice,
		["iprecptns"] = math.random(1, 2),
		["preset"] = preset[PresetChoice].name,
	}

	--wind
	local windDir = math.random(0, 359)
	local windSpeed = math.random(3, 5)
	mission.weather["wind"] = {
		["at8000"] = 
		{
			["speed"] = windSpeed * 2.5,
			["dir"] = windDir,
		},
		["at2000"] = 
		{
			["speed"] = windSpeed * 0.8,
			["dir"] = windDir,
		},
		["atGround"] = 
		{
			["speed"] = windSpeed,
			["dir"] = windDir,
		},
	}
	
	--turbulence
	mission.weather["turbulence"] = {
		["at8000"] = math.random(10, 60),
		["at2000"] = math.random(10, 60),
		["atGround"] = math.random(10, 60),
	}
	
	--temperature
	mission.weather["season"]["temperature"] = math.ceil(camp.weather.zoneTemp + strength * (camp.weather.zoneNextTemp - camp.weather.zoneTemp) / 10)
	
	--pressure
	mission.weather["qnh"] = math.random(740, 760)


------ WARM FRONT -----
elseif camp.weather.zone == "low front warm" then
	
	local front_remaining = (camp.weather.zoneEnd - elapsed_time) / 3600					--hours until end of warm front
	local front_duration = (camp.weather.zoneEnd - camp.weather.zoneStart) / 3600			--duration of the front in hours
	local strength = 10 - front_remaining * 10 / front_duration								--strength of the front on a scale of 0-10
	
	--clouds
	PresetChoice = math.random(10, 20)
	baseChoice =  math.random(preset[PresetChoice].altiMin, preset[PresetChoice].altiMax)
		
	local dens = math.ceil(strength * 1.5)
	if dens > 10 then
		dens = 10
	end
	mission.weather["clouds"] = {
		["thickness"] = math.ceil(strength * 200),
		["density"] = dens,
		-- ["base"] = FieldElevation + 100 + math.ceil(8000 - strength * 800),
		["base"] = FieldElevation + 100 + baseChoice,
		
		["iprecptns"] = math.floor(strength * 0.2),
		["preset"] = preset[PresetChoice].name,
	}

	--wind
	local windDir = math.random(0, 359)
	local windSpeed = math.random(2, 5)
	mission.weather["wind"] = {
		["at8000"] = 
		{
			["speed"] = windSpeed * 2.5,
			["dir"] = windDir,
		},
		["at2000"] = 
		{
			["speed"] = windSpeed * 0.8,
			["dir"] = windDir,
		},
		["atGround"] = 
		{
			["speed"] = windSpeed,
			["dir"] = windDir,
		},
	}
	
	--turbulence
	mission.weather["turbulence"] = {
		["at8000"] = math.random(5, 30),
		["at2000"] = math.random(5, 30),
		["atGround"] = math.random(5, 30),
	}
	
	--temperature
	mission.weather["season"]["temperature"] = math.ceil(camp.weather.zoneTemp + strength * (camp.weather.zoneNextTemp - camp.weather.zoneTemp) / 10)
	
	--pressure
	mission.weather["qnh"] = math.random(740, 760)

	
----- COLD SECTOR ------
elseif camp.weather.zone == "low sector cold" then
	
	--clouds
	PresetChoice = math.random(20, 25)
	baseChoice =  math.random(preset[PresetChoice].altiMin, preset[PresetChoice].altiMax)
	
	mission.weather["clouds"] = {
		["thickness"] = math.random(100, 1000),
		["density"] = math.random(0, 1),
		-- ["base"] = math.random(4000, 6000),
		["base"] = baseChoice,
		
		["iprecptns"] = 0,
		["preset"] = preset[PresetChoice].name,
	}

	--wind
	local windDir = math.random(0, 359)
	local windSpeed = math.random(1, 5)
	mission.weather["wind"] = {
		["at8000"] = 
		{
			["speed"] = windSpeed * 2.5,
			["dir"] = windDir,
		},
		["at2000"] = 
		{
			["speed"] = windSpeed * 0.8,
			["dir"] = windDir,
		},
		["atGround"] = 
		{
			["speed"] = windSpeed,
			["dir"] = windDir,
		},
	}
	
	--turbulence
	mission.weather["turbulence"] = {
		["at8000"] = math.random(5, 30),
		["at2000"] = math.random(5, 30),
		["atGround"] = math.random(5, 30),
	}
	
	--temperature
	mission.weather["season"]["temperature"] = camp.weather.zoneTemp
	
	--pressure
	mission.weather["qnh"] = math.random(740, 760)


----- WARM SECTOR -----
elseif camp.weather.zone == "low sector warm" then

	--clouds
	PresetChoice = math.random(5, 20)
	baseChoice =  math.random(preset[PresetChoice].altiMin, preset[PresetChoice].altiMax)
	
	mission.weather["clouds"] = {
		["thickness"] = math.random(100, 1000),
		["density"] = math.random(1, 4),
		-- ["base"] = math.random(4000, 6000),
		["base"] = baseChoice,
		["iprecptns"] = 0,
		["preset"] = preset[PresetChoice].name,
	}

	--wind
	local windDir = math.random(0, 359)
	local windSpeed = math.random(1, 5)
	mission.weather["wind"] = {
		["at8000"] = 
		{
			["speed"] = windSpeed * 2.5,
			["dir"] = windDir,
		},
		["at2000"] = 
		{
			["speed"] = windSpeed * 0.8,
			["dir"] = windDir,
		},
		["atGround"] = 
		{
			["speed"] = windSpeed,
			["dir"] = windDir,
		},
	}
	
	--turbulence
	mission.weather["turbulence"] = {
		["at8000"] = math.random(5, 30),
		["at2000"] = math.random(5, 30),
		["atGround"] = math.random(5, 30),
	}
	
	--temperature
	mission.weather["season"]["temperature"] = camp.weather.zoneTemp
	
	--pressure
	mission.weather["qnh"] = math.random(740, 760)
	
	
end


--Time of day temperature modification, min at 5 o'clock, max at 17 o'clock, deltaT 1 °C per hour
local hour = math.floor(camp.time / 3600)								--convert time to hours rounded down
if hour <= 5 then														--before 5 o'clock in the morning
	mission.weather["season"]["temperature"] = mission.weather["season"]["temperature"] - 7 - hour
elseif hour <= 17 then													--between 5 and 17 o'clock
	mission.weather["season"]["temperature"] = mission.weather["season"]["temperature"] - 17 + hour
else																	--after 17 o'clock
	mission.weather["season"]["temperature"] = mission.weather["season"]["temperature"] + 17 - hour
end


--Fog
if mission.weather["wind"]["atGround"]["speed"] < 2 then															--Fog is possible at speeds below 2 m/s
	if mission.weather["season"]["temperature"] < 12 and mission.weather["season"]["temperature"] > -2 then			--Fog is possoble at temperatures between -2 and 12 °C
		if math.random(1, 2) == 1 then																				--20% chance of fog
			mission.weather["enable_fog"] = true
			mission.weather["fog"] = {
				["thickness"] = math.random(0, 1000),
				["visibility"] = math.random(0,10000),
			}
		end
	end
end


----- Build METAR -----
METAR = "METAR "

--time and date
if camp.date.day < 10 then
	METAR = METAR .. "0" .. camp.date.day
else
	METAR = METAR .. camp.date.day
end
local t = math.floor(camp.time / 3600)
if t < 10 then
	METAR = METAR .. "0" .. t
else
	METAR = METAR .. t
end
local minute = math.floor((camp.time / 3600 - t) * 60)
if minute < 10 then
	minute = "0" .. minute
end
METAR = METAR .. minute .. " "

--wind
local direction = mission.weather["wind"]["atGround"]["dir"] - 180
if direction < 0 then
	direction = direction + 360
end
direction = math.floor(direction / 10) * 10
if direction < 10 then
	direction = "00" .. direction
elseif direction < 100 then
	direction = "0" .. direction
end
local speed = mission.weather["wind"]["atGround"]["speed"]
if camp.units == "imperial" then
	speed = math.ceil(speed * 1.94384)
end
if speed < 10 then
	speed = "0" .. speed
end
if camp.units == "imperial" then
	if mission.weather["wind"]["atGround"]["speed"] == 0 then
		METAR = METAR .. "00000KT "
	else
		METAR = METAR .. direction .. speed .. "KT "
	end
else
	if mission.weather["wind"]["atGround"]["speed"] == 0 then
		METAR = METAR .. "00000MPS "
	else
		METAR = METAR .. direction .. speed .. "MPS "
	end
end

--visilility
if mission.weather["enable_fog"] == true then
	local vis = math.floor(mission.weather["fog"]["visibility"] / 100) * 100
	if vis < 10 then
		vis = "000" .. vis
	elseif vis < 100 then
		vis = "00" .. vis
	elseif vis < 1000 then
		vis = "0" .. vis
	end
	METAR = METAR .. vis .. " " 
else
	if mission.weather["clouds"]["iprecptns"] == 1 then
		METAR = METAR .. "9999 "
	elseif mission.weather["clouds"]["iprecptns"] == 2 then
		METAR = METAR .. "9999 "
	else
		METAR = METAR .. "CAVOK "
	end
end

--fog
if mission.weather["enable_fog"] == true then
	METAR = METAR .. "FG "
end

--precipitation
if mission.weather["clouds"]["iprecptns"] == 1 then
	if mission.weather["season"]["temperature"] <= 0 then
		METAR = METAR .. "SN "
	else
		METAR = METAR .. "RA "
	end
elseif mission.weather["clouds"]["iprecptns"] == 2 then
	METAR = METAR .. "TS "
else
	METAR = METAR .. "NSW "
end

--clouds
local ceiling = mission.weather["clouds"]["base"]
if camp.units == "imperial" then
	ceiling = mission.weather["clouds"]["base"] * 3.28084
end
if ceiling < 100 then
	ceiling = "000"
elseif ceiling < 1000 then
	ceiling = "00" .. math.floor(ceiling / 100)
elseif ceiling < 10000 then
	ceiling = "0" .. math.floor(ceiling / 100)
else
	ceiling = "" .. math.floor(ceiling / 100)
end
if mission.weather["clouds"]["density"] == 0 then
	METAR = METAR .. "SKC "
elseif mission.weather["clouds"]["density"] < 4 then
	METAR = METAR .. "FEW" .. ceiling .. " "
elseif mission.weather["clouds"]["density"] < 7 then
	METAR = METAR .. "SCT" .. ceiling .. " "
elseif mission.weather["clouds"]["density"] < 9 then
	METAR = METAR .. "BKN" .. ceiling .. " "
else
	METAR = METAR .. "OVC" .. ceiling .. " "
end

--QNH
local qnh = math.floor(mission.weather["qnh"] / 760 * 1013.25)
METAR = METAR .. "Q" .. qnh .. "="

-- mission.weather["clouds"] = {
		-- ["thickness"] = 0,
		-- ["density"] = 0,
		-- ["base"] = baseChoice,
		-- ["iprecptns"] = 0,
		-- ["preset"] = preset[PresetChoice].name,
		


print(METAR)

print("\nPlease Wait...\n")