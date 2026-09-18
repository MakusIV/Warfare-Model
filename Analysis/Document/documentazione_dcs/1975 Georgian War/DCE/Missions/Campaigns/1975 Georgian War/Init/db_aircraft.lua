-- aircraft database 
-- contains cost of aircraft
-------------------------------------------------------------------------------------------------------

if not versionDCE then 
	versionDCE = {} 
end

               -- VERSION --

versionDCE["db_aircraft.lua"] = "OB.1.0.1"


---------------------------------------------------------------------------------------------------------
-- Old_Boy rev. OB.1.0.1: implements compute firepower code (property)
---------------------------------------------------------------------------------------------------------

local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua")
local log_level = LOGGING_LEVEL -- "traceVeryLow"
local function_log_level = log_level --"warn" 
log.activate = true
log.level = log_level 
log.outfile = LOG_DIR .. "LOG_db_aircraft.lua." .. camp.mission .. ".log" 
log.debug("Start")


local ROLE = { 												-- (max 1 -- min 0) weight factor for score calculus with increment percentage aircraft cost

	["Fighter"] = true, -- 
	["Attacker"] = true, -- 
	["Bomber"] = true, -- 
	["Transporter"] = true, -- 
	["Reco"] = true, -- 
	["Refueler"] = true, -- 
	["AWACS"] = true, -- 
	["Helicopter"] = true, -- 
}

local MAX_COST_AIRCRAFT = { ---max cost

	["blue"] = {

		["Fighter"] = 0, -- K$
		["Attacker"] = 0, -- K$
		["Bomber"] = 0, -- K$
		["Transporter"] = 0, -- K$
		["Reco"] = 0, -- K$
		["Refueler"] = 0, -- K$
		["AWACS"] = 0, -- K$
		["Helicopter"] = 0, -- 
	},

	["red"] = {

		["Fighter"] = 0, -- K$
		["Attacker"] = 0, -- K$
		["Bomber"] = 0, -- K$
		["Transporter"] = 0, -- K$
		["Reco"] = 0, -- K$
		["Refueler"] = 0, -- K$
		["AWACS"] = 0, -- K$
		["Helicopter"] = 0, -- 
	},
}



local MIN_COST_AIRCRAFT = { ---max cost

	["blue"] = {

		["Fighter"] = math.huge, -- K$
		["Attacker"] = math.huge, -- K$
		["Bomber"] = math.huge, -- K$
		["Transporter"] = math.huge, -- K$
		["Reco"] = math.huge, -- K$
		["Refueler"] = math.huge, -- K$
		["AWACS"] = math.huge, -- K$
		["Helicopter"] = math.huge, -- 
	},

	["red"] = {

		["Fighter"] = math.huge, -- K$
		["Attacker"] = math.huge, -- K$
		["Bomber"] = math.huge, -- K$
		["Transporter"] = math.huge, -- K$
		["Reco"] = math.huge, -- K$
		["Refueler"] = math.huge, -- K$
		["AWACS"] = math.huge, -- K$
		["Helicopter"] = math.huge, -- 
	},
}


db_aircraft = {

    -- Nato

	["blue"] = {

		["E-3A"] = { -- 1975 (primo volo), 1977 (entrata in servizio)
			["role"] = {"AWACS"},
			["cost"] = 270000, --cos taircraft in K$
			["factor"] = {}, -- percentage factor for reduction score: {["AWACS"] = 0,}
		},

		["E-2C"] = {  --- 1973 (in servizio)
			["role"] = {"AWACS"},
			["cost"] = 80000, --cost aircraft in K$
			["factor"] = {},
		},

		["F-14A-135-GR"] = { --1970 (primo volo) 1974 (entrata in servizio),
			["role"] = {"Fighter", "Attacker", "Reco"},
			["cost"] = 38000, --cost aircraft in K$
			["factor"] = {},
		},

		["KC-135"] = { --1957 (entrata in servizio)
			["role"] = {"Transporter"},
			["cost"] = 40000, --cost aircraft in K$
			["factor"] = {},
		},

		["KC135MPRS"] = { --1957 (entrata in servizio)
			["role"] = {"Refueler"},
			["cost"] = 40000, --cost aircraft in K$
			["factor"] = {},
		},

		["AJS37"] = {-- 1971 (entrata in servizio)
			["role"] = {"Attacker", "Fighter", "Reco"},
			["cost"] = 30000, --cost aircraft in K$
			["factor"] = {},
		},

		["B-52H"] = { --1952 (primo volo) 1955 (entrata in servizio)
			["role"] = {"Bomber"},
			["cost"] = 54000, --cost aircraft in K$
			["factor"] = {},
		},

		["S-3B Tanker"] = { --1972 (primo volo) 1974 (entrata in servizio)
			["role"] = {"Refueler"},
			["cost"] = 27000, --cost aircraft in K$
			["factor"] = {},
		},

		["S-3B"] = { --1972 (primo volo) 1974 (entrata in servizio)
			["role"] = {"Bomber"},
			["cost"] = 27000, --cost aircraft in K$
			["factor"] = {},
		},

		["F-5E-3"] = {--1959 (primo volo) 1972 (entrata in servizio)
			["role"] = {"Fighter", "Attacker", "Reco"},
			["cost"] = 10000, --balanced for gameplay, doc cost: 2100 cost aircraft in K$
			["factor"] = {},
		},	
		-- < --- REVISIONE hattack, hcruise, vattack, vcruise, standoff, sortie_rate 
		["Mirage-F1C"] = {--
			["role"] = {"Fighter", "Attacker", "Reco"},
			["cost"] = 25000, --balanced for gameplay, doc cost: 15000, --cost aircraft in K$ (mirage 2000 23 M$)
			["factor"] = {},
		},	

		["F-4E"] = {--1958 (primo volo) 1960 (entrata in servizio)
			["role"] = {"Attacker", "Fighter", "Reco"},
			["cost"] = 15000, -- balanced for gameplay, doc cost: 2400, --cost aircraft in K$
			["factor"] = {},
		},

		["C-130"] = {--1954 (primo volo) 1957 (entrata in servizio)
			["role"] = {"Transporter"},
			["cost"] = 67000, --cost aircraft in K$
			["factor"] = {},
		},

		["UH-1H"] = {--? (primo volo) 1956 (entrata in servizio)
			["role"] = {"Helicopter"},
			["cost"] = 2000, --balanced for gameplay, doc cost: 895, --cost aircraft in K$
			["factor"] = {},
		},

		["AH-1W"] = {--1967 (primo volo) 1973 (entrata in servizio)
			["role"] = {"Helicopter"},
			["cost"] = 10700, --cost aircraft in K$
			["factor"] = {},
		},

		["MiG-27K"] = {--1970 (primo volo) 1975 (entrata in servizio) -- Bombe?
			["role"] = {"Attacker", "Fighter", "Reco"},		
			["cost"] = 13000, --balanced for gameplay, doc cost: 6600, --cost aircraft in K$  (1980)
			["factor"] = {},
		},

		["MiG-21Bis"] = {--1955 (primo volo) 1959 (entrata in servizio) inserire Kh-66, S-24 e/o S-21
			["role"] = {"Fighter", "Attacker", "Reco"},		
			["cost"] = 10000, -- balanced for gameplay, doc cost: 3000, --cost aircraft in K$  (1974)
			["factor"] = {},
		},

		["MiG-19P"] = {--1953 (primo volo) 1955 (entrata in servizio)
			["role"] = {"Fighter", "Attacker", "Reco"},		
			["cost"] = 2000, -- balanced for gameplay, doc cost: 1000, --cost aircraft in K$  (1980)
			["factor"] = {},
		},

		["An-26B"] = {--1969 (primo volo) 1973 (entrata in servizio)
			["role"] = {"Transporter"},
			["cost"] = 14000, -- balanced for gameplay, doc cost: 4000, --cost aircraft in K$
			["factor"] = {},
		},
		
		["Mi-24V"] = {--1969 (primo volo) 1972 (entrata in servizio)
			["role"] = {"Helicopter"},
			["cost"] = 12500, --cost aircraft in K$
			["factor"] = {},
		},
	},


	["red"] = {
		-- URSS

		["Tu-22M3"] = { --1969 (primo volo) 1972 (entrata in servizio) ok
			["role"] = {"Bomber"},
			["cost"] = 160000, --cost aircraft in K$
			["factor"] = {},
		},

		["Su-24MR"] = {--1967 (primo volo) 1974 (entrata in servizio)
			["role"] = {"Reco"},
			["cost"] = 25000, --cost aircraft in K$
			["factor"] = {},
		},

		["Su-24M"] = {--1967 (primo volo) 1974 (entrata in servizio)
			["role"] = {"Bomber"},
			["cost"] = 25000, --cost aircraft in K$
			["factor"] = {},
		},

		["Mi-8MT"] = {--1961 (primo volo) 1967 (entrata in servizio)
			["role"] = {"Helicopter"},
			["cost"] = 14000, --cost aircraft in K$
			["factor"] = {},
		},

		["Mi-24V"] = {--1969 (primo volo) 1972 (entrata in servizio)
			["role"] = {"Helicopter"},
			["cost"] = 12500, --cost aircraft in K$
			["factor"] = {},
		},

		["A-50"] = { -- 1978 (primo volo) 1984 (entrata in servizio) SI in quanto in DCS non esiste un'altro AWACS per l'USSR
			["role"] = {"AWACS"},
			["cost"] = 330000, --cost aircraft in K$
			["factor"] = {},
		},

		["An-26B"] = {--1969 (primo volo) 1973 (entrata in servizio)
			["role"] = {"Transporter"},
			["cost"] = 14000, -- balanced for gameplay, doc cost: 4000 --cost aircraft in K$
			["factor"] = {},
		},

		["MiG-21Bis"] = {--1955 (primo volo) 1959 (entrata in servizio) inserire Kh-66, S-24 e/o S-21
			["role"] = {"Fighter", "Attacker", "Reco"},		
			["cost"] = 10000, -- balanced for gameplay, doc cost: 3000, --cost aircraft in K$  (1974)
			["factor"] = {},
		},

		["Su-17M4"] = {--1967 (primo volo) 1972 (entrata in servizio)
			["role"] = {"Attacker", "Reco"},		
			["cost"] = 10000, --balanced for gameplay, doc cost: 5000, --cost aircraft in K$  ??
			["factor"] = {},
		},

		["MiG-27K"] = {--1970 (primo volo) 1975 (entrata in servizio) -- Bombe?
			["role"] = {"Attacker", "Fighter", "Reco"},		
			["cost"] = 13000, --balanced for gameplay, doc cost: 6600, --cost aircraft in K$  (1980)
			["factor"] = {},
		},

		["MiG-23MLD"] = {--1967 (primo volo) 1970 (entrata in servizio)
			["role"] = {"Fighter", "Attacker", "Reco"},		
			["cost"] = 13000, --balanced for gameplay, doc cost: 5000, --cost aircraft in K$  (1980)
			["factor"] = {},
		},

		["MiG-25PD"] = {--1964 (primo volo) 1970 (entrata in servizio)
			["role"] = {"Fighter"},		
			["cost"] = 40000, --cost aircraft in K$  (1980)
			["factor"] = {},
		},

		["MiG-25RBT"] = {--1964 (primo volo) 1970 (entrata in servizio)
			["role"] = {"Reco"},		
			["cost"] = 40000, --cost aircraft in K$  (1980)
			["factor"] = {},
		},

		["MiG-19P"] = {--1953 (primo volo) 1955 (entrata in servizio)
			["role"] = {"Fighter", "Attacker", "Reco"},		
			["cost"] = 2000, -- balanced for gameplay, doc cost: 1000, --cost aircraft in K$  (1980)
			["factor"] = {},
		},

		["Il-76MD"] = {--1971 (primo volo) 1974 (entrata in servizio)
			["role"] = {"Transporter"},
			["cost"] = 54000, --cost aircraft in K$
			["factor"] = {},
		},

		["L-39C"] = {--1968 (primo volo) 1971 (entrata in servizio)
			["role"] = {"Attacker", "Fighter", "Reco"},		
			["cost"] = 15000, --cost aircraft in K$  (1980)
			["factor"] = {},
		},
	},

    -- Not valid

    -- Nato
	--[[
    ["SH-60B"] = {--? (primo volo) 1984 (entrata in servizio) NO
		
	},

    ["B-1B"] = { --1974 (primo volo) 1986 (entrata in servizio) NO
		
	},

	]]
	-- UH-60 --1974 (primo volo) 1978 (entrata in servizio) NO
	-- SA-342 Gazelle (1978-2000 (sistemi d'arma)?)

    --URSS
	--[[
    ["Mi-26"] = {--1977 (primo volo) 1983 (entrata in servizio) NO
	
	},

    ["Tu-142"] = {--1975 (primo volo) 1980 (entrata in servizio) NO
		
	},

	["Mi-24P"] = {--1980 (primo volo) (entrata in servizio)
		
	},
	]]

}


-- LOCAL FUNCTION 

local function getMaxCost(aircraft_role, side)
	local max = 0

	for aircraft_type, aircraft_data in pairs(db_aircraft[side]) do
		
		for index, role in pairs(aircraft_data.role) do
		
			if role == aircraft_role and aircraft_data.cost > max then
				max = aircraft_data.cost
				break
			end
		end		
	end

	return max
end

local function getMinCost(aircraft_role, side)
	local min = math.huge

	for aircraft_type, aircraft_data in pairs(db_aircraft[side]) do
		
		for index, role in pairs(aircraft_data.role) do
		
			if role == aircraft_role and aircraft_data.cost < min then
				min = aircraft_data.cost
				break
			end
		end		
	end

	return min
end



-- PREPROCESSING

-- define MAX_COST_AIRCRAFT table
for side_name, side_data in pairs(MIN_COST_AIRCRAFT) do

	for aircraft_role, aircraft_cost in pairs(side_data) do
		MIN_COST_AIRCRAFT[side_name][aircraft_role] = getMinCost(aircraft_role, side_name)
	end	
end

-- define MIN_COST_AIRCRAFT table
for side_name, side_data in pairs(MAX_COST_AIRCRAFT) do

	for aircraft_role, aircraft_cost in pairs(side_data) do
		MAX_COST_AIRCRAFT[side_name][aircraft_role] = getMaxCost(aircraft_role, side_name)
	end	
end

log.info("MIN_COST_AIRCRAFT:\n" .. inspect(MIN_COST_AIRCRAFT) .. "\n\n")
log.info("MAX_COST_AIRCRAFT:\n" .. inspect(MAX_COST_AIRCRAFT) .. "\n\n")

-- define FACTOR_FOR_REDUCE_SCORE_COST_AIRCRAFT table
local base_log = 1.7 -- base for log  (1.6), 
for side_name, side_data in pairs(db_aircraft) do

	for aircraft_type, aircraft_data in pairs(side_data) do

		for index, role in pairs(aircraft_data.role) do		
			local min = MIN_COST_AIRCRAFT[side_name][role]
			local max = MAX_COST_AIRCRAFT[side_name][role]

			if (not min) or (not max) or (not  ROLE[role]) then
				log.warn("aircraft: " .. aircraft_type .. ", role: " .. role .. ". ATTENTION: no cost info for this role, check ROLE, MIN_COST_AIRCRAFT and MAX_COST_AIRCRAFT tables")	

			else	
				local y_, log_, factor
				if min == max then -- for this role there is only one plane or several planes with the same cost
					factor = 1	
				
				else				
					y_ = roundAtNumber( 1 + (aircraft_data.cost - min) * ( base_log - 1 ) / (max - min), 0.0001 )
					log_ = math.log(y_) / math.log(base_log)					
					factor = roundAtNumber( 1 - log_, 0.001 )

					if factor < 0.001 then
						factor = 0
					end					
				end
				log.traceVeryLow("aircraft: " .. aircraft_type .. ", role: " .. role .. ", min: " .. (min or "nil") .. ", max: " ..(max or "nil") ..", ROLE[" .. role .. "]: " .. tostring(ROLE[role]) .. ", aircraft_data.cost: " .. aircraft_data.cost .. ", y_: " .. (y_ or "nil") .. ", log_: " .. (log_ or "nil") ..", factor: " .. factor)				
				aircraft_data.factor[role] = factor 
			end
		end			
	end	
end

log.info("aircraft_data:\n" .. inspect(db_aircraft) .. "\n\n")




-- GLOBAL FUNCTION 

-- return the role for specifi task: CAP, SWEEP, Intercept = Fighter, Strike, Anti-ship Strike = Attack or Bomber, AWACS, Refueling or Transport same
function getRole(aircraft_type, aircraft_task, side)
	local role
	

	if aircraft_task == "CAP" or aircraft_task == "Intercept" or aircraft_task == "Fighter Sweep" or aircraft_task == "Escort" then 
		role = "Fighter"

	elseif aircraft_task == "Strike" or aircraft_task == "Anti-ship Strike" then
		local roles = db_aircraft[side][aircraft_type].role
		
		for num_role, name_role in pairs(roles) do
			
			if "Fighter" == name_role or "Attacker" == name_role then
				role = "Attacker"
			
			elseif "Bomber" == name_role or "Helicopter" == name_role then
				role = name_role	
			end
		end
	
	elseif aircraft_task == "Reconnaissance" then 
		role = "Reco"

	elseif aircraft_task == "Transport" then 
		role = "Transporter"

	elseif aircraft_task == "Refueling" then 
		role = "Refueler"

	elseif aircraft_task == "AWACS" then 
		role = "AWACS"

	end
	return role
end

-- return the primary (first) role: CAP, SWEEP, Intercept = Fighter, Strike, Anti-ship Strike = Attack or Bomber, AWACS, Refueling or Transport same
function getFirstRole(aircraft_type, side)

	local unit_type  = db_aircraft[side][aircraft_type]

	if unit_type then
		return unit_type.role[1]
	
	else
		return nil
	end
end