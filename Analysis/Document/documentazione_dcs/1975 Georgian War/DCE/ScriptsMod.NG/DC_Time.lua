--To advance the campaign time for next mission
--Initiated by MAIN_NextMission.lua
-------------------------------------------------------------------------------------------------------

if not versionDCE then 
	versionDCE = {} 
end

               -- VERSION --

versionDCE["DC_Time.lua"] = "OB.1.0.0"

---------------------------------------------------------------------------------------------------------
-- Old_Boy rev. OB.1.0.0: implements logging code
-- Miguel21 modification M25.b OnlyDayMission


local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua")
-- NOTE MARCO: prova a caricarlo usando require(".. . .. . .. .ScriptsMod."versionPackageICM..".UTIL_Log.lua")
-- NOTE MARCO: https://forum.defold.com/t/including-a-lua-module-solved/2747/2
log.level = LOGGING_LEVEL
log.outfile = LOG_DIR .. "LOG_DC_Time." .. camp.mission .. ".log" 
local local_debug = true -- local debug   
log.info("Start")


--campaign day counter
if camp.day == nil then																			--if counter does not exist yet
	camp.day = 1																				--start counting with first day in campaign
end

--advance campaign time
local idle_time = math.random(camp.idle_time_min, camp.idle_time_max)							--random idle time to next mission in seconds, depending on min-max defined for campaign
camp.time = camp.time + idle_time																--add idle time to campaign time
log.info("advance campaign time: new camp.time: " .. camp.time .. ", time increment was: " .. idle_time)

-- Miguel21 modification M25.b OnlyDayMission
if mission_ini.OnlyDayMission then
		-- dawn = 27900,					--time of dawn in seconds						--27900 == 7h45mn
		-- dusk = 65700					--time of dusk in seconds

	HTdawn = camp.dawn /(1 + mission_ini.HourlyTolerance/100)
	HTdusk = camp.dusk *(1 - mission_ini.HourlyTolerance/100) - camp.mission_duration
		
	addTime = 0
	while camp.time%86400 < HTdawn or  camp.time%86400 > HTdusk do
		addTime = addTime + 3600
		camp.time = camp.time + addTime
	end
	idle_time = idle_time + addTime
	log.trace("mission_ini.OnlyDayMission == true -> idle_time = " .. idle_time)
end

log.info("compute years, monthsand days from camp.time: " .. camp.time .. ", camp.date.day: " .. camp.date.day .. ", camp.date.month: " .. camp.date.month .. ", camp.date.year: " .. camp.date.year)

while camp.time >= 86400 do																		--repeat as long as time 24 hours or more
	camp.time = camp.time - 86400																--remove 24 hours from time
	camp.date.day = camp.date.day + 1															--add a day to date
	log.trace("remove 24 hours from camp.time: " .. camp.time .. " and add a day to date: " .. camp.date.day)
	
	if camp.date.day == 32 and (camp.date.month == 1 or camp.date.month == 3 or camp.date.month == 5 or camp.date.month == 7 or camp.date.month == 8 or camp.date.month == 10 or camp.date.month == 12) then	--month change for large months
		camp.date.day = 1																		--first day of next month
		camp.date.month = camp.date.month + 1													--advance month
		log.trace("first day of next month. advance month: " .. camp.date.month)
	
	elseif camp.date.day == 31 and (camp.date.month == 4 or camp.date.month == 6 or camp.date.month == 9 or camp.date.month == 11) then	--month change for small months
		camp.date.day = 1																		--first day of next month
		camp.date.month = camp.date.month + 1													--advance month
		log.trace("first day of next month. advance month: " .. camp.date.month)
	
	elseif camp.date.month == 30 and camp.date.month == 2 then									--month change for February
		camp.date.day = 1																		--first day of next month
		camp.date.month = camp.date.month + 1													--advance month
		log.trace("first day of next month, advance month: " .. camp.date.month)
	end
	
	if camp.date.month == 13 then																--year change
		camp.date.month = 1																		--first month of next year
		camp.date.year = camp.date.year + 1														--advance year
		log.trace("first month of next year, advance year: " .. camp.date.year)
	end
	camp.day = camp.day + 1																		--counter for campaign days
end

mission["start_time"] = camp.time																--set mission start time
mission["date"]["Day"] = camp.date.day															--set mission day
mission["date"]["Year"] = camp.date.year														--set mission year
mission["date"]["Month"] = camp.date.month														--set mission month
log.info("set mission time: camp.time: " .. camp.time .. ", camp.date.day: " .. camp.date.day .. ", camp.date.month: " .. camp.date.month .. ", camp.date.year: " .. camp.date.year)
print(FormatTime(idle_time, "hh:mm") .. "h passed. Next mission scheduled at: " .. FormatTime(camp.time, "hh:mm") .. ", " .. camp.date.day .. "." .. camp.date.month .. "." .. camp.date.year .. ".\n")

--determine mission time of day
log.info("determine mission time of day")
daytime	= ""																					--variable what daytime the is covered in the duration of the mission

if camp.time >= camp.dawn and camp.time <= camp.dusk then										--current time is between dawn and dusk

	if camp.time + camp.mission_duration <= camp.dusk then									 	--mission duration ends before dusk
		log.debug("current time is between dawn and dusk and mission duration ends before dusk - > daytime = 'day'")
		daytime = "day"
	
	else																						--mission duration ends after dusk
		log.debug("current time is between dawn and dusk and mission duration ends after dusk - > daytime = 'day-night'")
		daytime = "day-night"
	end

else																							--current time is between dusk and dawn
	
	if camp.time < camp.dawn then																--mission starts before dawn
		
		if camp.time + camp.mission_duration < camp.dawn then									--mission duration ends before dawn
			log.debug("current time is between dusk and dawn, mission starts before dawn and mission duration ends before dawn - > daytime = 'night'")
			daytime = "night"
		
		else
			log.debug("current time is between dusk and dawn, mission starts before dawn and mission duration ends after dawn - > daytime = 'night-day'")
			daytime = "night-day"
		end
	
	else																						--mission starts after dusk
		
		if camp.time + camp.mission_duration < camp.dawn + 86400 then							--mission duration ends before dawn of next day
			log.debug("current time is between dusk and dawn, mission starts after dusk and mission duration ends before dawn of next day - > daytime = 'night'")
			daytime = "night"
		
		else
			daytime = "night-day"
			log.debug("current time is between dusk and dawn, mission starts after dusk and mission duration ends after dawn of next day - > daytime = 'night-day'")
		end
	end
end