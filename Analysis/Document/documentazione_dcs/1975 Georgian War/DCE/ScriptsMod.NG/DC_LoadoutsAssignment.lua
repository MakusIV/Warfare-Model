
--To create the Air Tasking Order
--Initiated by Main_NextMission.lua
-------------------------------------------------------------------------------------------------------

if not versionDCE then 
	versionDCE = {} 
end

               -- VERSION --

versionDCE["DC_LoadoutsAssignment.lua"] = "OB.1.0.3"

-------------------------------------------------------------------------------------------------------
-- Old_Boy rev. OB.1.0.3: grouping configuration parameters into a single table in camp_init/camp_status
-- Old_Boy rev. OB.1.0.2: implements compute loadouts cruise parameters code
-- Old_Boy rev. OB.1.0.1: implements compute firepower code
------------------------------------------------------------------------------------------------------- 

--NOTE: nella prima missione deve aggiornare Active/targelist (considerando il numero di elementi) e Init/db_loadouts
-- verificare l'effettiva esigenza nelle missioni successive di aggiornarli

local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua")
local log_level = "warn" --LOGGING_LEVEL -- 
local function_log_level = log_level --"warn" 
log.activate = false
log.level = log_level 
log.outfile = LOG_DIR .. "LOG_DC_LoadoutsAssignment.lua." .. camp.mission .. ".log" 
local local_debug = false -- local debug   
local active_log = false
log.debug("Start")
require("Init/db_firepower")
require("Init/db_loadouts")


-- global table in conf_mod
--[[
    module_config = {

        ["DC_LoadoutsAssignment"] = {

            ["ANGLE_OF_DESCENT_IN_GROUND_ATTACK"] = {             -- degree
                ["ASM"] = { 
                    ["min"] = 10,                                       
                    ["med"] = 25, 
                    ["max"] = 35,                                       
                },
                ["Rockets"] = { 
                    ["min"] = 20,                                       
                    ["med"] = 30,                                       
                    ["max"] = 40,                                       
                },                                   
            },
        
            ["PERCENTAGE_RANGE_FOR_STANDOFF_SETUP"] = {           -- standoff = percentage * range weapon
                ["ASM"] = 0.7,                                      
                ["Rockets"] = 0.6,                                  
            },
            
            ["ALTITUDE_ATTACK"] = {                               -- (m) min,max altitude attack for rockets/ASM loadout (hAltitude)
                ["ASM"] = { 
                    ["min"] = 200,                                             
                    ["max"] = 6000,                                       
                },
                ["Rockets"] = {
                    ["min"] = 50,                                             
                    ["max"] = 1000,                                       
                },
            },
        
            ["ACTIVATE_STANDOFF_SETUP"] = true,                    -- assign loadouts.standoff with weapon.range only for ASM (default = true)
            ["MIN_EFFICIENCY_WEAPON_ATTRIBUTE"] = 0.01,            -- don't touch! - minimum value for weapon efficiency,  efficiency = accuracy * destroy_capacity (1 max, 0.01 min),  accuracy: hit success percentage, 1 max, 0.1 min, destroy_capacity: destroy single element capacity,  1 max ( element destroyed with single hit),  0.1 min (default = 0.01)
            ["MAX_EFFICIENCY_WEAPON_ATTRIBUTE"] = 999999999,       -- don't touch! - maximum value for weapon efficiency,  efficiency = accuracy * destroy_capacity (1 max, 0.01 min),  accuracy: hit success percentage, 1 max, 0.1 min, destroy_capacity: destroy single element capacity,  1 max ( element destroyed with single hit),  0.1 min (default = 0.01)
            ["FIREPOWER_ROUNDED_COMPUTATION"] = 0.01,              -- don't touch!
            ["FIREPOWER_ROUNDED_ASSIGNEMENT"] = 0.1,               -- don't touch!
            ["FACTOR_FOR_CALCULATED_TARGET_FIREPOWER_MAX"] = 1.1,   -- factor for computed firepower max target: firepower_max = firepower_min * weapon_variability * FACTOR
            ["WEIGHT_MISSILE_A2A_RELIABILITY"] = 0.3,              -- look weight_missile_a2a_attribute calculus (down)
            ["WEIGHT_MISSILE_A2A_MANOUVRABILITY"] = 0.2,           -- look weight_missile_a2a_attribute calculus (down)
            
            ["FIREPOWER_FOR_AA_TARGETS"] = {        
                    
                ["blue"] = {
        
                    ["CAP"] = {
        
                        ["min"] = 2,        -- minimum number of enemy aircraft expected
                        ["max"] = 5,        -- maximum number of enemy aircraft expected
                    },
        
                    ["Intercept"] = {
        
                        ["min"] = 3,
                        ["max"] = 6,
                    },
        
                    ["Fighter Sweep"] = {
        
                        ["min"] = 4,
                        ["max"] = 7,
                    },
        
                    ["Escort"] = {
        
                        ["min"] = 3,
                        ["max"] = 5,
                    },
                },
        
                ["red"] = {
        
                    ["CAP"] = {
        
                        ["min"] = 2,
                        ["max"] = 5,
                    },
        
                    ["Intercept"] = {
        
                        ["min"] = 3,
                        ["max"] = 6,
                    },
        
                    ["Fighter Sweep"] = {
        
                        ["min"] = 4,
                        ["max"] = 7,
                    },
        
                    ["Escort"] = {
        
                        ["min"] = 3,
                        ["max"] = 5,
                    },
                },
            },
        
            -- SETTING FOR CALCULATE CRUISE PARAMETER: vCruise and hCruise
        
            ["CRUISE_PARAM"] = {  -- SETTING ALTITUDE (hCruise) AND SPEED (vCruise - tas) FOR AIRCRAFT ROLES
                
                ["blue"] = {
        
                    ["bomber"] = {
        
                        ["high"] = {
        
                            ["min_vCruise_TAS"] = 350 / 3.6, -- Km/h @ slm
                            ["max_vCruise_TAS"] = 450 / 3.6, -- Km/h @ slm
                            ["min_hCruise"] = 9000, -- m slm
                            ["max_hCruise"] = 12000, -- m slm
                        },
        
                        ["normal"] = {
        
                            ["min_vCruise_TAS"] = 400 / 3.6, -- Km/h @ slm
                            ["max_vCruise_TAS"] = 600 / 3.6, -- Km/h @ slm
                            ["min_hCruise"] = 2000, -- m slm
                            ["max_hCruise"] = 8999, -- m slm
                        },
        
                        ["low"] = {
        
                            ["min_vCruise_TAS"] = 450 / 3.6, -- Km/h @ slm
                            ["max_vCruise_TAS"] = 550 / 3.6, -- Km/h @ slm
                            ["min_hCruise"] = 100, -- m slm
                            ["max_hCruise"] = 1999, -- m slm
                        },
        
                        ["supersonic"] = {
        
                            ["min_vCruise_TAS"] = 1500 / 3.6, -- Km/h @ slm
                            ["max_vCruise_TAS"] = 2000 / 3.6, -- Km/h @ slm
                            ["min_hCruise"] = 200, -- m slm
                            ["max_hCruise"] = 12000, -- m slm
                        },
                    },
        
                    ["attacker"] = {
        
                        ["normal"] = {
        
                            ["min_vCruise_TAS"] = 450 / 3.6, -- Km/h @ slm
                            ["max_vCruise_TAS"] = 900 / 3.6, -- Km/h @ slm
                            ["min_hCruise"] = 1000, -- m slm
                            ["max_hCruise"] = 7000, -- m slm
                        },			
        
                        ["low"] = {
        
                            ["min_vCruise_TAS"] = 400 / 3.6, -- Km/h @ slm
                            ["max_vCruise_TAS"] = 500 / 3.6, -- Km/h @ slm
                            ["min_hCruise"] = 100, -- m slm
                            ["max_hCruise"] = 999, -- m slm
                        },			
                    },
        
                    ["transporter"] = {
        
                        ["normal"] = {
        
                            ["min_vCruise_TAS"] = 370 / 3.6, -- Km/h @ slm
                            ["max_vCruise_TAS"] = 500 / 3.6, -- Km/h @ slm
                            ["min_hCruise"] = 4500, -- m slm
                            ["max_hCruise"] = 10000, -- m slm
                        },						
                    },
        
                    ["refueler"] = {
        
                        ["normal"] = {
        
                            ["min_vCruise_TAS"] = 290 / 3.6, -- Km/h @ slm
                            ["max_vCruise_TAS"] = 330 / 3.6, -- Km/h @ slm
                            ["min_hCruise"] = 7000, -- m slm
                            ["max_hCruise"] = 10000, -- m slm
                        },		
                        
                        ["low"] = {
        
                            ["min_vCruise_TAS"] = 290 / 3.6, -- Km/h @ slm
                            ["max_vCruise_TAS"] = 320 / 3.6, -- Km/h @ slm
                            ["min_hCruise"] = 2000, -- m slm
                            ["max_hCruise"] = 6999, -- m slm
                        },	
                    },
        
                    ["AWACS"] = {
        
                        ["normal"] = {
        
                            ["min_vCruise_TAS"] = 370 / 3.6, -- Km/h @ slm
                            ["max_vCruise_TAS"] = 500 / 3.6, -- Km/h @ slm
                            ["min_hCruise"] = 9000, -- m slm
                            ["max_hCruise"] = 10000, -- m slm
                        },						
                    },
        
                    ["recon"] = {
        
                        ["normal"] = {
        
                            ["min_vCruise_TAS"] = 400 / 3.6, -- Km/h @ slm
                            ["max_vCruise_TAS"] = 700 / 3.6, -- Km/h @ slm
                            ["min_hCruise"] = 4500, -- m slm
                            ["max_hCruise"] = 10000, -- m slm
                        },						
                    },		
                },
        
                ["red"] = {
        
                    ["bomber"] = {
        
                        ["high"] = {
        
                            ["min_vCruise_TAS"] = 380 / 3.6, -- Km/h @ slm
                            ["max_vCruise_TAS"] = 470 / 3.6, -- Km/h @ slm
                            ["min_hCruise"] = 9000, -- m slm
                            ["max_hCruise"] = 12000, -- m slm
                        },
        
                        ["normal"] = {
        
                            ["min_vCruise_TAS"] = 400 / 3.6, -- Km/h @ slm
                            ["max_vCruise_TAS"] = 600 / 3.6, -- Km/h @ slm
                            ["min_hCruise"] = 2000, -- m slm
                            ["max_hCruise"] = 8999, -- m slm
                        },
        
                        ["low"] = {
        
                            ["min_vCruise_TAS"] = 370 / 3.6, -- Km/h @ slm
                            ["max_vCruise_TAS"] = 450 / 3.6, -- Km/h @ slm
                            ["min_hCruise"] = 100, -- m slm
                            ["max_hCruise"] = 1999, -- m slm
                        },
        
                        ["supersonic"] = {
        
                            ["min_vCruise_TAS"] = 1500 / 3.6, -- Km/h @ slm
                            ["max_vCruise_TAS"] = 2000 / 3.6, -- Km/h @ slm
                            ["min_hCruise"] = 200, -- m slm
                            ["max_hCruise"] = 12000, -- m slm
                        },
                    },
        
                    ["attacker"] = {
        
                        ["normal"] = {
        
                            ["min_vCruise_TAS"] = 450 / 3.6, -- Km/h @ slm
                            ["max_vCruise_TAS"] = 900 / 3.6, -- Km/h @ slm
                            ["min_hCruise"] = 1000, -- m slm
                            ["max_hCruise"] = 7000, -- m slm
                        },			
        
                        ["low"] = {
        
                            ["min_vCruise_TAS"] = 400 / 3.6, -- Km/h @ slm
                            ["max_vCruise_TAS"] = 550 / 3.6, -- Km/h @ slm
                            ["min_hCruise"] = 100, -- m slm
                            ["max_hCruise"] = 999, -- m slm
                        },			
                    },
        
                    ["transporter"] = {
        
                        ["normal"] = {
        
                            ["min_vCruise_TAS"] = 370 / 3.6, -- Km/h @ slm
                            ["max_vCruise_TAS"] = 500 / 3.6, -- Km/h @ slm
                            ["min_hCruise"] = 4500, -- m slm
                            ["max_hCruise"] = 10000, -- m slm
                        },						
                    },
        
                    ["refueler"] = {
        
                        ["normal"] = {
        
                            ["min_vCruise_TAS"] = 290 / 3.6, -- Km/h @ slm
                            ["max_vCruise_TAS"] = 330 / 3.6, -- Km/h @ slm
                            ["min_hCruise"] = 7000, -- m slm
                            ["max_hCruise"] = 10000, -- m slm
                        },		
                        
                        ["low"] = {
        
                            ["min_vCruise_TAS"] = 290 / 3.6, -- Km/h @ slm
                            ["max_vCruise_TAS"] = 330 / 3.6, -- Km/h @ slm
                            ["min_hCruise"] = 2000, -- m slm
                            ["max_hCruise"] = 6999, -- m slm
                        },	
                    },
        
                    ["AWACS"] = {
        
                        ["normal"] = {
        
                            ["min_vCruise_TAS"] = 370 / 3.6, -- Km/h @ slm
                            ["max_vCruise_TAS"] = 500 / 3.6, -- Km/h @ slm
                            ["min_hCruise"] = 9000, -- m slm
                            ["max_hCruise"] = 10000, -- m slm
                        },						
                    },
        
                    ["recon"] = {
        
                        ["normal"] = {
        
                            ["min_vCruise_TAS"] = 450 / 3.6, -- Km/h @ slm
                            ["max_vCruise_TAS"] = 600 / 3.6, -- Km/h @ slm
                            ["min_hCruise"] = 4500, -- m slm
                            ["max_hCruise"] = 10000, -- m slm
                        },						
                    },		
                },
            },
            ["ESCORT_ALTITUDE_OVERRIDE"] = { -- SETTING OVERRIDE ALTITUDE FOR ESCORT JOBS
                
                ["escort_bomber"]  = {
                    ["min"] = 300, -- ( m ) min override altitude from bomber
                    ["max"] = 1000, -- ( m ) max override altitude from bomber
                },
        
                ["escort_attacker"]  = {
                    ["min"] = 200, -- ( m ) min override altitude from attacker
                    ["max"] = 800, -- ( m ) max override altitude from attacker
                },
        
                ["escort_sead_bomber"]  = {
                    ["min"] = 500, -- ( m ) min override altitude from bomber with SEAD task
                    ["max"] = 1200, -- ( m ) max override altitude from bomber with SEAD task
                },
        
                ["escort_sead_attacker"]  = {
                    ["min"] = 300, -- ( m ) min override altitude from attacker with SEAD task
                    ["max"] = 800, -- ( m ) max override altitude from attacker with SEAD task
                },
            },
            ["ESCORT_TIME_FOR_DISTANCE_OVERRIDE"] = { -- SETTING OVERRIDE DISTANCE_TIME FOR ESCORT JOBS
                
                ["escort_bomber"]  = 1500, -- (s) time needed for escort override after join (default: 1500s == 25')
                ["escort_attacker"]  = 600, -- (s) time needed for escort override after join (default: 600s == 10')
                ["escort_sead_bomber"]  = 1200, -- (s) time needed for escort override after join (default: 1200s == 20')
                ["escort_sead_attacker"]  = 900, -- (s) time needed for escort override after join (default: 1200s == 15')
            },
            ["ESCORT_DISTANCE_OVERRIDE"] = {  -- SETTING OVERRIDE DISTANCE TIME FOR ESCORT JOBS
                
                ["escort_bomber"]  = {
                    ["min"] = 10000, -- ( m ) min override distance from join after the past ESCORT_TIME_FOR_DISTANCE_OVERRIDE
                    ["max"] = 20000, -- ( m ) max override distance from join after the past ESCORT_TIME_FOR_DISTANCE_OVERRIDE
                },
        
                ["escort_attacker"]  = {
                    ["min"] = 7000, -- ( m ) min override distance from join after the past ESCORT_TIME_FOR_DISTANCE_OVERRIDE
                    ["max"] = 12000, -- ( m ) max override distance from join after the past ESCORT_TIME_FOR_DISTANCE_OVERRIDE
                },
        
                ["escort_sead_bomber"]  = {
                    ["min"] = 20000, -- ( m ) min override distance from join after the past ESCORT_TIME_FOR_DISTANCE_OVERRIDE
                    ["max"] = 30000, -- ( m ) max override distance from join after the past ESCORT_TIME_FOR_DISTANCE_OVERRIDE
                },
        
                ["escort_sead_attacker"]  = {
                    ["min"] = 15000, -- ( m ) min override distance from join after the past ESCORT_TIME_FOR_DISTANCE_OVERRIDE
                    ["max"] = 25000, -- ( m ) max override distance from join after the past ESCORT_TIME_FOR_DISTANCE_OVERRIDE
                },
            },		
        },
    },
]]


-- PREPROCESSING

local weight_missile_a2a_attribute = 1 - camp.module_config.DC_LoadoutsAssignment.WEIGHT_MISSILE_A2A_RELIABILITY - camp.module_config.DC_LoadoutsAssignment.WEIGHT_MISSILE_A2A_MANOUVRABILITY -- weight for missile attibute for calculate missile firepower

local altitude_increments_for_escort = { 
	["escort_bomber"] = math.random(camp.module_config.DC_LoadoutsAssignment.ESCORT_ALTITUDE_OVERRIDE.escort_bomber.min, camp.module_config.DC_LoadoutsAssignment.ESCORT_ALTITUDE_OVERRIDE.escort_bomber.max), -- (m/s) increment speed for escort
	["escort_attacker"] = math.random(camp.module_config.DC_LoadoutsAssignment.ESCORT_ALTITUDE_OVERRIDE.escort_attacker.min, camp.module_config.DC_LoadoutsAssignment.ESCORT_ALTITUDE_OVERRIDE.escort_attacker.max), -- (m/s) increment speed for escort
	["escort_sead_bomber"] = math.random(camp.module_config.DC_LoadoutsAssignment.ESCORT_ALTITUDE_OVERRIDE.escort_sead_bomber.min, camp.module_config.DC_LoadoutsAssignment.ESCORT_ALTITUDE_OVERRIDE.escort_sead_bomber.max), -- (m/s) increment speed for escort
	["escort_sead_attacker"] = math.random(camp.module_config.DC_LoadoutsAssignment.ESCORT_ALTITUDE_OVERRIDE.escort_attacker.min, camp.module_config.DC_LoadoutsAssignment.ESCORT_ALTITUDE_OVERRIDE.escort_sead_attacker.max), -- (m/s) increment speed for escort
}
local cruise_param_calculated = {
	
	["blue"] = {

		["bomber"] = {

			["high"] = {

				["hCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.bomber.high.min_hCruise, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.bomber.high.max_hCruise)),
				["vCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.bomber.high.min_vCruise_TAS, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.bomber.high.max_vCruise_TAS)),								
			},

			["normal"] = {

				["hCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.bomber.normal.min_hCruise, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.bomber.normal.max_hCruise)),
				["vCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.bomber.normal.min_vCruise_TAS, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.bomber.normal.max_vCruise_TAS)),
			},

			["low"] = {

				["hCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.bomber.low.min_hCruise, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.bomber.low.max_hCruise)),
				["vCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.bomber.low.min_vCruise_TAS, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.bomber.low.max_vCruise_TAS)),			
			},

			["supersonic"] = {

				["hCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.bomber.supersonic.min_hCruise, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.bomber.supersonic.max_hCruise)),
				["vCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.bomber.supersonic.min_vCruise_TAS, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.bomber.supersonic.max_vCruise_TAS)),				
			},
		},

		["attacker"] = {

			["normal"] = {

				["hCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.attacker.normal.min_hCruise, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.attacker.normal.max_hCruise)),
				["vCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.attacker.normal.min_vCruise_TAS, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.attacker.normal.max_vCruise_TAS)),
			},			

			["low"] = {

				["hCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.attacker.low.min_hCruise, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.attacker.low.max_hCruise)),
				["vCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.attacker.low.min_vCruise_TAS, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.attacker.low.max_vCruise_TAS)),
			},			
		},

		["transporter"] = {

			["normal"] = {

				["hCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.transporter.normal.min_hCruise, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.transporter.normal.max_hCruise)),
				["vCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.transporter.normal.min_vCruise_TAS, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.transporter.normal.max_vCruise_TAS)),
			},						
		},

		["refueler"] = {

			["normal"] = {

				["hCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.refueler.normal.min_hCruise, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.refueler.normal.max_hCruise)),
				["vCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.refueler.normal.min_vCruise_TAS, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.refueler.normal.max_vCruise_TAS)),
			},	
            
            ["low"] = {

				["hCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.refueler.low.min_hCruise, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.refueler.low.max_hCruise)),
				["vCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.refueler.low.min_vCruise_TAS, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.refueler.low.max_vCruise_TAS)),
			},	
		},

		["AWACS"] = {

			["normal"] = {

				["hCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.AWACS.normal.min_hCruise, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.AWACS.normal.max_hCruise)),
				["vCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.AWACS.normal.min_vCruise_TAS, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.AWACS.normal.max_vCruise_TAS)),
			},						
		},

		["recon"] = {

			["normal"] = {

				["hCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.recon.normal.min_hCruise, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.recon.normal.max_hCruise)),
				["vCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.recon.normal.min_vCruise_TAS, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.blue.recon.normal.max_vCruise_TAS)),	
			},						
		},		
	},

    ["red"] = {

		["bomber"] = {

			["high"] = {

				["hCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.bomber.high.min_hCruise, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.bomber.high.max_hCruise)),
				["vCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.bomber.high.min_vCruise_TAS, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.bomber.high.max_vCruise_TAS)),								
			},

			["normal"] = {

				["hCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.bomber.normal.min_hCruise, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.bomber.normal.max_hCruise)),
				["vCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.bomber.normal.min_vCruise_TAS, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.bomber.normal.max_vCruise_TAS)),
			},

			["low"] = {

				["hCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.bomber.low.min_hCruise, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.bomber.low.max_hCruise)),
				["vCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.bomber.low.min_vCruise_TAS, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.bomber.low.max_vCruise_TAS)),			
			},

			["supersonic"] = {

				["hCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.bomber.supersonic.min_hCruise, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.bomber.supersonic.max_hCruise)),
				["vCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.bomber.supersonic.min_vCruise_TAS, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.bomber.supersonic.max_vCruise_TAS)),				
			},
		},

		["attacker"] = {

			["normal"] = {

				["hCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.attacker.normal.min_hCruise, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.attacker.normal.max_hCruise)),
				["vCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.attacker.normal.min_vCruise_TAS, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.attacker.normal.max_vCruise_TAS)),
			},			

			["low"] = {

				["hCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.attacker.low.min_hCruise, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.attacker.low.max_hCruise)),
				["vCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.attacker.low.min_vCruise_TAS, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.attacker.low.max_vCruise_TAS)),
			},			
		},

		["transporter"] = {

			["normal"] = {

				["hCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.transporter.normal.min_hCruise, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.transporter.normal.max_hCruise)),
				["vCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.transporter.normal.min_vCruise_TAS, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.transporter.normal.max_vCruise_TAS)),
			},						
		},

		["refueler"] = {

			["normal"] = {

				["hCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.refueler.normal.min_hCruise, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.refueler.normal.max_hCruise)),
				["vCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.refueler.normal.min_vCruise_TAS, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.refueler.normal.max_vCruise_TAS)),
			},						

            ["low"] = {

				["hCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.refueler.low.min_hCruise, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.refueler.low.max_hCruise)),
				["vCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.refueler.low.min_vCruise_TAS, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.refueler.low.max_vCruise_TAS)),
			},						
		},

		["AWACS"] = {

			["normal"] = {

				["hCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.AWACS.normal.min_hCruise, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.AWACS.normal.max_hCruise)),
				["vCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.AWACS.normal.min_vCruise_TAS, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.AWACS.normal.max_vCruise_TAS)),
			},						
		},

		["recon"] = {

			["normal"] = {

				["hCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.recon.normal.min_hCruise, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.recon.normal.max_hCruise)),
				["vCruise"] = math.ceil(math.random(camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.recon.normal.min_vCruise_TAS, camp.module_config.DC_LoadoutsAssignment.CRUISE_PARAM.red.recon.normal.max_vCruise_TAS)),	
			},						
		},		
	},    
}
local escort_cruise_altitude = {

	["blue"] = {

		["escort_bomber"] = {

			["high"] = math.ceil(cruise_param_calculated.blue.bomber.high.hCruise - altitude_increments_for_escort.escort_bomber),			
			["normal"] = math.ceil(cruise_param_calculated.blue.bomber.normal.hCruise + altitude_increments_for_escort.escort_bomber),
			["low"] = math.ceil(cruise_param_calculated.blue.bomber.low.hCruise + altitude_increments_for_escort.escort_bomber),		
			["supersonic"] = math.ceil(cruise_param_calculated.blue.bomber.supersonic.hCruise + altitude_increments_for_escort.escort_bomber),			
		},

		["escort_attacker"] = {
			
			["normal"] = math.ceil(cruise_param_calculated.blue.attacker.normal.hCruise + altitude_increments_for_escort.escort_attacker),			
			["low"] = math.ceil(cruise_param_calculated.blue.attacker.low.hCruise + altitude_increments_for_escort.escort_attacker),			
		},

		["escort_sead_attacker"] = {
			
			["normal"] = math.ceil(cruise_param_calculated.blue.attacker.normal.hCruise + altitude_increments_for_escort.escort_sead_attacker),
			["low"] = math.ceil(cruise_param_calculated.blue.attacker.low.hCruise + altitude_increments_for_escort.escort_sead_attacker),
		},

		["escort_sead_bomber"] = {
			
			["high"] = math.ceil(cruise_param_calculated.blue.bomber.high.hCruise - altitude_increments_for_escort.escort_sead_bomber),
			["normal"] = math.ceil(cruise_param_calculated.blue.bomber.normal.hCruise + altitude_increments_for_escort.escort_sead_bomber),
			["low"] = math.ceil(cruise_param_calculated.blue.bomber.low.hCruise + altitude_increments_for_escort.escort_sead_bomber),
			["supersonic"] = math.ceil(cruise_param_calculated.blue.bomber.supersonic.hCruise + altitude_increments_for_escort.escort_sead_bomber),
		},

        ["escort_jammer_attacker"] = { -- same sead
			
			["normal"] = math.ceil(cruise_param_calculated.blue.attacker.normal.hCruise + altitude_increments_for_escort.escort_sead_attacker),
			["low"] = math.ceil(cruise_param_calculated.blue.attacker.low.hCruise + altitude_increments_for_escort.escort_sead_attacker),
		},

		["escort_jammer_bomber"] = { -- same sead
			
			["high"] = math.ceil(cruise_param_calculated.blue.bomber.high.hCruise - altitude_increments_for_escort.escort_sead_bomber),
			["normal"] = math.ceil(cruise_param_calculated.blue.bomber.normal.hCruise + altitude_increments_for_escort.escort_sead_bomber),
			["low"] = math.ceil(cruise_param_calculated.blue.bomber.low.hCruise + altitude_increments_for_escort.escort_sead_bomber),
			["supersonic"] = math.ceil(cruise_param_calculated.blue.bomber.supersonic.hCruise + altitude_increments_for_escort.escort_sead_bomber),
		},

        ["escort_laser_illumination_attacker"] = { -- same sead
			
			["normal"] = math.ceil(cruise_param_calculated.blue.attacker.normal.hCruise + altitude_increments_for_escort.escort_sead_attacker),
			["low"] = math.ceil(cruise_param_calculated.blue.attacker.low.hCruise + altitude_increments_for_escort.escort_sead_attacker),
		},

		["escort_laser_illumination_bomber"] = { -- same sead
			
			["high"] = math.ceil(cruise_param_calculated.blue.bomber.high.hCruise - altitude_increments_for_escort.escort_sead_bomber),
			["normal"] = math.ceil(cruise_param_calculated.blue.bomber.normal.hCruise + altitude_increments_for_escort.escort_sead_bomber),
			["low"] = math.ceil(cruise_param_calculated.blue.bomber.low.hCruise + altitude_increments_for_escort.escort_sead_bomber),
			["supersonic"] = math.ceil(cruise_param_calculated.blue.bomber.supersonic.hCruise + altitude_increments_for_escort.escort_sead_bomber),
		},

        ["escort_flare_illumination_attacker"] = { -- same sead
			
			["normal"] = math.ceil(cruise_param_calculated.blue.attacker.normal.hCruise + altitude_increments_for_escort.escort_sead_attacker),
			["low"] = math.ceil(cruise_param_calculated.blue.attacker.low.hCruise + altitude_increments_for_escort.escort_sead_attacker),
		},
	},

    ["red"] = {

		["escort_bomber"] = {

			["high"] = math.ceil(cruise_param_calculated.red.bomber.high.hCruise - altitude_increments_for_escort.escort_bomber),			
			["normal"] = math.ceil(cruise_param_calculated.red.bomber.normal.hCruise + altitude_increments_for_escort.escort_bomber),
			["low"] = math.ceil(cruise_param_calculated.red.bomber.low.hCruise + altitude_increments_for_escort.escort_bomber),		
			["supersonic"] = math.ceil(cruise_param_calculated.red.bomber.supersonic.hCruise + altitude_increments_for_escort.escort_bomber),			
		},

		["escort_attacker"] = {
			
			["normal"] = math.ceil(cruise_param_calculated.red.attacker.normal.hCruise + altitude_increments_for_escort.escort_attacker),			
			["low"] = math.ceil(cruise_param_calculated.red.attacker.low.hCruise + altitude_increments_for_escort.escort_attacker),			
		},

		["escort_sead_attacker"] = {
			
			["normal"] = math.ceil(cruise_param_calculated.red.attacker.normal.hCruise + altitude_increments_for_escort.escort_sead_attacker),
			["low"] = math.ceil(cruise_param_calculated.red.attacker.low.hCruise + altitude_increments_for_escort.escort_sead_attacker),
		},

		["escort_sead_bomber"] = {
			
			["high"] = math.ceil(cruise_param_calculated.red.bomber.high.hCruise - altitude_increments_for_escort.escort_sead_bomber),
			["normal"] = math.ceil(cruise_param_calculated.red.bomber.normal.hCruise + altitude_increments_for_escort.escort_sead_bomber),
			["low"] = math.ceil(cruise_param_calculated.red.bomber.low.hCruise + altitude_increments_for_escort.escort_sead_bomber),
			["supersonic"] = math.ceil(cruise_param_calculated.red.bomber.supersonic.hCruise + altitude_increments_for_escort.escort_sead_bomber),
		},

        ["escort_jammer_attacker"] = { -- same sead
			
			["normal"] = math.ceil(cruise_param_calculated.red.attacker.normal.hCruise + altitude_increments_for_escort.escort_sead_attacker),
			["low"] = math.ceil(cruise_param_calculated.red.attacker.low.hCruise + altitude_increments_for_escort.escort_sead_attacker),
		},

		["escort_jammer_bomber"] = { -- same sead
			
			["high"] = math.ceil(cruise_param_calculated.red.bomber.high.hCruise - altitude_increments_for_escort.escort_sead_bomber),
			["normal"] = math.ceil(cruise_param_calculated.red.bomber.normal.hCruise + altitude_increments_for_escort.escort_sead_bomber),
			["low"] = math.ceil(cruise_param_calculated.red.bomber.low.hCruise + altitude_increments_for_escort.escort_sead_bomber),
			["supersonic"] = math.ceil(cruise_param_calculated.red.bomber.supersonic.hCruise + altitude_increments_for_escort.escort_sead_bomber),
		},

        ["escort_laser_illumination_attacker"] = { -- same sead
			
			["normal"] = math.ceil(cruise_param_calculated.red.attacker.normal.hCruise + altitude_increments_for_escort.escort_sead_attacker),
			["low"] = math.ceil(cruise_param_calculated.red.attacker.low.hCruise + altitude_increments_for_escort.escort_sead_attacker),
		},

		["escort_laser_illumination_bomber"] = { -- same sead
			
			["high"] = math.ceil(cruise_param_calculated.red.bomber.high.hCruise - altitude_increments_for_escort.escort_sead_bomber),
			["normal"] = math.ceil(cruise_param_calculated.red.bomber.normal.hCruise + altitude_increments_for_escort.escort_sead_bomber),
			["low"] = math.ceil(cruise_param_calculated.red.bomber.low.hCruise + altitude_increments_for_escort.escort_sead_bomber),
			["supersonic"] = math.ceil(cruise_param_calculated.red.bomber.supersonic.hCruise + altitude_increments_for_escort.escort_sead_bomber),
		},

        ["escort_flare_illumination_attacker"] = { -- same sead
			
			["normal"] = math.ceil(cruise_param_calculated.red.attacker.normal.hCruise + altitude_increments_for_escort.escort_sead_attacker),
			["low"] = math.ceil(cruise_param_calculated.red.attacker.low.hCruise + altitude_increments_for_escort.escort_sead_attacker),
		},
	},

}
local cruise_speed_at_altitude = {

	["blue"] = {

		["bomber"] = {

			["high"] = math.ceil(cruise_param_calculated.blue.bomber.high.vCruise * 1.02 ^ ( cruise_param_calculated.blue.bomber.high.hCruise / 300 )),
			["normal"] = math.ceil(cruise_param_calculated.blue.bomber.normal.vCruise * 1.02 ^ ( cruise_param_calculated.blue.bomber.normal.hCruise / 300 )),
			["low"] = math.ceil(cruise_param_calculated.blue.bomber.low.vCruise * 1.02 ^ ( cruise_param_calculated.blue.bomber.low.hCruise / 300 )),
			["supersonic"] = math.ceil(cruise_param_calculated.blue.bomber.supersonic.vCruise * 1.02 ^ ( cruise_param_calculated.blue.bomber.supersonic.hCruise / 300 )),
		},

		["attacker"] = {
			
			["normal"] = math.ceil(cruise_param_calculated.blue.attacker.normal.vCruise * 1.02 ^ ( cruise_param_calculated.blue.attacker.normal.hCruise / 300 )),			
			["low"] = math.ceil(cruise_param_calculated.blue.attacker.low.vCruise * 1.02 ^ ( cruise_param_calculated.blue.attacker.low.hCruise / 300 )),
		},

		["transporter"] = {
			
			["normal"] = math.ceil(cruise_param_calculated.blue.attacker.normal.vCruise * 1.02 ^ ( cruise_param_calculated.blue.attacker.normal.hCruise / 300 )),									
		},

		["refueler"] = {
			
			["normal"] = math.ceil(cruise_param_calculated.blue.attacker.normal.vCruise * 1.02 ^ ( cruise_param_calculated.blue.attacker.normal.hCruise / 300 )),									
            ["low"] = math.ceil(cruise_param_calculated.blue.attacker.low.vCruise * 1.02 ^ ( cruise_param_calculated.blue.attacker.low.hCruise / 300 )),									
		},

		["AWACS"] = {
			
			["normal"] = math.ceil(cruise_param_calculated.blue.attacker.normal.vCruise * 1.02 ^ ( cruise_param_calculated.blue.attacker.normal.hCruise / 300 )),									
		},

		["recon"] = {
			
			["normal"] = math.ceil(cruise_param_calculated.blue.attacker.normal.vCruise * 1.02 ^ ( cruise_param_calculated.blue.attacker.normal.hCruise / 300 )),									
		},
	},

    ["red"] = {

		["bomber"] = {

			["high"] = math.ceil(cruise_param_calculated.red.bomber.high.vCruise * 1.02 ^ ( cruise_param_calculated.red.bomber.high.hCruise / 300 )),
			["normal"] = math.ceil(cruise_param_calculated.red.bomber.normal.vCruise * 1.02 ^ ( cruise_param_calculated.red.bomber.normal.hCruise / 300 )),
			["low"] = math.ceil(cruise_param_calculated.red.bomber.low.vCruise * 1.02 ^ ( cruise_param_calculated.red.bomber.low.hCruise / 300 )),
			["supersonic"] = math.ceil(cruise_param_calculated.red.bomber.supersonic.vCruise * 1.02 ^ ( cruise_param_calculated.red.bomber.supersonic.hCruise / 300 )),
		},

		["attacker"] = {
			
			["normal"] = math.ceil(cruise_param_calculated.red.attacker.normal.vCruise * 1.02 ^ ( cruise_param_calculated.red.attacker.normal.hCruise / 300 )),			
			["low"] = math.ceil(cruise_param_calculated.red.attacker.low.vCruise * 1.02 ^ ( cruise_param_calculated.red.attacker.low.hCruise / 300 )),
		},

		["transporter"] = {
			
			["normal"] = math.ceil(cruise_param_calculated.red.attacker.normal.vCruise * 1.02 ^ ( cruise_param_calculated.red.attacker.normal.hCruise / 300 )),									
		},

		["refueler"] = {
			
			["normal"] = math.ceil(cruise_param_calculated.red.attacker.normal.vCruise * 1.02 ^ ( cruise_param_calculated.red.attacker.normal.hCruise / 300 )),									
            ["low"] = math.ceil(cruise_param_calculated.red.attacker.low.vCruise * 1.02 ^ ( cruise_param_calculated.red.attacker.low.hCruise / 300 )),									
		},

		["AWACS"] = {
			
			["normal"] = math.ceil(cruise_param_calculated.red.attacker.normal.vCruise * 1.02 ^ ( cruise_param_calculated.red.attacker.normal.hCruise / 300 )),									
		},

		["recon"] = {
			
			["normal"] = math.ceil(cruise_param_calculated.red.attacker.normal.vCruise * 1.02 ^ ( cruise_param_calculated.red.attacker.normal.hCruise / 300 )),									
		},
	},

}
local speed_increments_for_escort = { 
	["escort_bomber"] = math.random(camp.module_config.DC_LoadoutsAssignment.ESCORT_DISTANCE_OVERRIDE.escort_bomber.min / camp.module_config.DC_LoadoutsAssignment.ESCORT_TIME_FOR_DISTANCE_OVERRIDE.escort_bomber, camp.module_config.DC_LoadoutsAssignment.ESCORT_DISTANCE_OVERRIDE.escort_bomber.max / camp.module_config.DC_LoadoutsAssignment.ESCORT_TIME_FOR_DISTANCE_OVERRIDE.escort_bomber) , -- (m/s) increment speed for escort
	["escort_attacker"] = math.random(camp.module_config.DC_LoadoutsAssignment.ESCORT_DISTANCE_OVERRIDE.escort_attacker.min / camp.module_config.DC_LoadoutsAssignment.ESCORT_TIME_FOR_DISTANCE_OVERRIDE.escort_attacker, camp.module_config.DC_LoadoutsAssignment.ESCORT_DISTANCE_OVERRIDE.escort_attacker.max / camp.module_config.DC_LoadoutsAssignment.ESCORT_TIME_FOR_DISTANCE_OVERRIDE.escort_attacker) , -- (m/s) increment speed for escort
	["escort_sead_bomber"] = math.random(camp.module_config.DC_LoadoutsAssignment.ESCORT_DISTANCE_OVERRIDE.escort_sead_bomber.min / camp.module_config.DC_LoadoutsAssignment.ESCORT_TIME_FOR_DISTANCE_OVERRIDE.escort_sead_bomber, camp.module_config.DC_LoadoutsAssignment.ESCORT_DISTANCE_OVERRIDE.escort_sead_bomber.max / camp.module_config.DC_LoadoutsAssignment.ESCORT_TIME_FOR_DISTANCE_OVERRIDE.escort_sead_bomber) , -- (m/s) increment speed for escort
	["escort_sead_attacker"] = math.random(camp.module_config.DC_LoadoutsAssignment.ESCORT_DISTANCE_OVERRIDE.escort_attacker.min / camp.module_config.DC_LoadoutsAssignment.ESCORT_TIME_FOR_DISTANCE_OVERRIDE.escort_sead_attacker, camp.module_config.DC_LoadoutsAssignment.ESCORT_DISTANCE_OVERRIDE.escort_sead_attacker.max / camp.module_config.DC_LoadoutsAssignment.ESCORT_TIME_FOR_DISTANCE_OVERRIDE.escort_sead_attacker) , -- (m/s) increment speed for escort
}
local escort_cruise_speed_at_altitude = {

	["blue"] = {

		["escort_bomber"] = {

			["high"] = math.ceil(cruise_speed_at_altitude.blue.bomber.high + speed_increments_for_escort.escort_bomber),
			["normal"] = math.ceil(cruise_speed_at_altitude.blue.bomber.normal + speed_increments_for_escort.escort_bomber),
			["low"] = math.ceil(cruise_speed_at_altitude.blue.bomber.low + speed_increments_for_escort.escort_bomber),
			["supersonic"] = math.ceil(cruise_speed_at_altitude.blue.bomber.supersonic + speed_increments_for_escort.escort_bomber),
		},

		["escort_attacker"] = {
			
			["normal"] = math.ceil(cruise_speed_at_altitude.blue.attacker.normal + speed_increments_for_escort.escort_attacker),
			["low"] = math.ceil(cruise_speed_at_altitude.blue.attacker.low + speed_increments_for_escort.escort_attacker),
		},

		["escort_sead_bomber"] = {
			
			["high"] = math.ceil(cruise_speed_at_altitude.blue.bomber.high + speed_increments_for_escort.escort_sead_bomber),
			["normal"] = math.ceil(cruise_speed_at_altitude.blue.bomber.normal + speed_increments_for_escort.escort_sead_bomber),
			["low"] = math.ceil(cruise_speed_at_altitude.blue.bomber.low + speed_increments_for_escort.escort_sead_bomber),
			["supersonic"] = math.ceil(cruise_speed_at_altitude.blue.bomber.supersonic + speed_increments_for_escort.escort_sead_bomber),
		},

		["escort_sead_attacker"] = {
			
			["normal"] = math.ceil(cruise_speed_at_altitude.blue.attacker.normal + speed_increments_for_escort.escort_sead_attacker),
			["low"] = math.ceil(cruise_speed_at_altitude.blue.attacker.low + speed_increments_for_escort.escort_sead_attacker),
		},

        ["escort_jammer_bomber"] = { -- same sead
			
			["high"] = math.ceil(cruise_speed_at_altitude.blue.bomber.high + speed_increments_for_escort.escort_sead_bomber),
			["normal"] = math.ceil(cruise_speed_at_altitude.blue.bomber.normal + speed_increments_for_escort.escort_sead_bomber),
			["low"] = math.ceil(cruise_speed_at_altitude.blue.bomber.low + speed_increments_for_escort.escort_sead_bomber),
			["supersonic"] = math.ceil(cruise_speed_at_altitude.blue.bomber.supersonic + speed_increments_for_escort.escort_sead_bomber),
		},

		["escort_jammer_attacker"] = { -- same sead
			
			["normal"] = math.ceil(cruise_speed_at_altitude.blue.attacker.normal + speed_increments_for_escort.escort_sead_attacker),
			["low"] = math.ceil(cruise_speed_at_altitude.blue.attacker.low + speed_increments_for_escort.escort_sead_attacker),
		},

        ["escort_laser_illumination_bomber"] = { -- same sead
			
			["high"] = math.ceil(cruise_speed_at_altitude.blue.bomber.high + speed_increments_for_escort.escort_sead_bomber),
			["normal"] = math.ceil(cruise_speed_at_altitude.blue.bomber.normal + speed_increments_for_escort.escort_sead_bomber),
			["low"] = math.ceil(cruise_speed_at_altitude.blue.bomber.low + speed_increments_for_escort.escort_sead_bomber),
			["supersonic"] = math.ceil(cruise_speed_at_altitude.blue.bomber.supersonic + speed_increments_for_escort.escort_sead_bomber),
		},

		["escort_laser_illumination_attacker"] = { -- same sead
			
			["normal"] = math.ceil(cruise_speed_at_altitude.blue.attacker.normal + speed_increments_for_escort.escort_sead_attacker),
			["low"] = math.ceil(cruise_speed_at_altitude.blue.attacker.low + speed_increments_for_escort.escort_sead_attacker),
		},

        ["escort_flare_illumination_attacker"] = { -- same sead
			
			["normal"] = math.ceil(cruise_speed_at_altitude.blue.attacker.normal + speed_increments_for_escort.escort_sead_attacker),
			["low"] = math.ceil(cruise_speed_at_altitude.blue.attacker.low + speed_increments_for_escort.escort_sead_attacker),
		},

	},

    ["red"] = {

		["escort_bomber"] = {

			["high"] = math.ceil(cruise_speed_at_altitude.red.bomber.high + speed_increments_for_escort.escort_bomber),
			["normal"] = math.ceil(cruise_speed_at_altitude.red.bomber.normal + speed_increments_for_escort.escort_bomber),
			["low"] = math.ceil(cruise_speed_at_altitude.red.bomber.low + speed_increments_for_escort.escort_bomber),
			["supersonic"] = math.ceil(cruise_speed_at_altitude.red.bomber.supersonic + speed_increments_for_escort.escort_bomber),
		},

		["escort_attacker"] = {
			
			["normal"] = math.ceil(cruise_speed_at_altitude.red.attacker.normal + speed_increments_for_escort.escort_attacker),
			["low"] = math.ceil(cruise_speed_at_altitude.red.attacker.low + speed_increments_for_escort.escort_attacker),
		},

		["escort_sead_bomber"] = {
			
			["high"] = math.ceil(cruise_speed_at_altitude.red.bomber.high + speed_increments_for_escort.escort_sead_bomber),
			["normal"] = math.ceil(cruise_speed_at_altitude.red.bomber.normal + speed_increments_for_escort.escort_sead_bomber),
			["low"] = math.ceil(cruise_speed_at_altitude.red.bomber.low + speed_increments_for_escort.escort_sead_bomber),
			["supersonic"] = math.ceil(cruise_speed_at_altitude.red.bomber.supersonic + speed_increments_for_escort.escort_sead_bomber),
		},

		["escort_sead_attacker"] = {
			
			["normal"] = math.ceil(cruise_speed_at_altitude.red.attacker.normal + speed_increments_for_escort.escort_sead_attacker),
			["low"] = math.ceil(cruise_speed_at_altitude.red.attacker.low + speed_increments_for_escort.escort_sead_attacker),
		},

        ["escort_jammer_bomber"] = { -- same sead
			
			["high"] = math.ceil(cruise_speed_at_altitude.red.bomber.high + speed_increments_for_escort.escort_sead_bomber),
			["normal"] = math.ceil(cruise_speed_at_altitude.red.bomber.normal + speed_increments_for_escort.escort_sead_bomber),
			["low"] = math.ceil(cruise_speed_at_altitude.red.bomber.low + speed_increments_for_escort.escort_sead_bomber),
			["supersonic"] = math.ceil(cruise_speed_at_altitude.red.bomber.supersonic + speed_increments_for_escort.escort_sead_bomber),
		},

		["escort_jammer_attacker"] = { -- same sead
			
			["normal"] = math.ceil(cruise_speed_at_altitude.red.attacker.normal + speed_increments_for_escort.escort_sead_attacker),
			["low"] = math.ceil(cruise_speed_at_altitude.red.attacker.low + speed_increments_for_escort.escort_sead_attacker),
		},

        ["escort_laser_illumination_bomber"] = { -- same sead
			
			["high"] = math.ceil(cruise_speed_at_altitude.red.bomber.high + speed_increments_for_escort.escort_sead_bomber),
			["normal"] = math.ceil(cruise_speed_at_altitude.red.bomber.normal + speed_increments_for_escort.escort_sead_bomber),
			["low"] = math.ceil(cruise_speed_at_altitude.red.bomber.low + speed_increments_for_escort.escort_sead_bomber),
			["supersonic"] = math.ceil(cruise_speed_at_altitude.red.bomber.supersonic + speed_increments_for_escort.escort_sead_bomber),
		},

		["escort_laser_illumination_attacker"] = { -- same sead
			
			["normal"] = math.ceil(cruise_speed_at_altitude.red.attacker.normal + speed_increments_for_escort.escort_sead_attacker),
			["low"] = math.ceil(cruise_speed_at_altitude.red.attacker.low + speed_increments_for_escort.escort_sead_attacker),
		},

        ["escort_flare_illumination_attacker"] = { -- same sead
			
			["normal"] = math.ceil(cruise_speed_at_altitude.red.attacker.normal + speed_increments_for_escort.escort_sead_attacker),
			["low"] = math.ceil(cruise_speed_at_altitude.red.attacker.low + speed_increments_for_escort.escort_sead_attacker),
		},

	},

}
local weight_missile_a2a = {

    ["radar"] = {                               -- factor weight for compute missile firepower (weight sum must be 1)       

        ["range"] = 0.3,

        ["semiactive_range"] = 0,

        ["active_range"] = 0.15,

        ["height"] = 0.05,                      

        ["speed"] = 0.25,                       

        ["tnt"] = 0.25,
    },

    ["infrared"] = {                

        ["range"] = 0.3,

        ["height"] = 0.05,

        ["speed"] = 0.35,

        ["tnt"] = 0.3,
    },
}
local factor_angle_of_descent = {                       -- factor for compute hAttack 
    ["ASM"] = { 
        ["min"] = math.sin(camp.module_config.DC_LoadoutsAssignment.ANGLE_OF_DESCENT_IN_GROUND_ATTACK["ASM"].min * math.pi / 180),    
        ["med"] = math.sin(camp.module_config.DC_LoadoutsAssignment.ANGLE_OF_DESCENT_IN_GROUND_ATTACK["ASM"].med * math.pi / 180),    
        ["max"] = math.sin(camp.module_config.DC_LoadoutsAssignment.ANGLE_OF_DESCENT_IN_GROUND_ATTACK["ASM"].max * math.pi / 180),    
    },
    ["Rockets"] = { 
        ["min"] = math.sin(camp.module_config.DC_LoadoutsAssignment.ANGLE_OF_DESCENT_IN_GROUND_ATTACK["Rockets"].min * math.pi / 180),    
        ["med"] = math.sin(camp.module_config.DC_LoadoutsAssignment.ANGLE_OF_DESCENT_IN_GROUND_ATTACK["Rockets"].med * math.pi / 180),    
        ["max"] = math.sin(camp.module_config.DC_LoadoutsAssignment.ANGLE_OF_DESCENT_IN_GROUND_ATTACK["Rockets"].max * math.pi / 180),    
    },
}

-- updating table
local reference_missile_a2a = {

    ["radar"] = {
        
        ["max"] = {
            ["range"] = 0,                                -- km, range (aircraft must track target)                              
            ["semiactive_range"] = 0,                           -- km, semiactive range (aircraft can or not track target)                  
            ["active_range"] = 0,                               -- km, active range  (missile has active autonomous tracking target)                
            ["height"] = 0,                         -- km, max height    
            ["speed"] = 0,                          -- mach, max speed            
            ["tnt"] = 0,                                        -- kg                
        },

        ["min"] = {
            ["range"] = math.huge,                                -- km, range (aircraft must track target)                              
            ["semiactive_range"] = math.huge,                           -- km, semiactive range (aircraft can or not track target)                  
            ["active_range"] = math.huge,                               -- km, active range  (missile has active autonomous tracking target)                
            ["height"] = math.huge,                         -- km, max height    
            ["speed"] = math.huge,                          -- mach, max speed            
            ["tnt"] = math.huge,                                        -- kg                
        },
    },

    ["infrared"] = {
        
        ["max"] = {            
            ["range"] = 0,                                     -- km, range (aircraft must track target)                              
            ["height"] = 0,                        -- km, max height                        
            ["speed"] = 0,                          -- mach, max speed
            ["tnt"] = 0,                                       -- kg                
        },
        
        ["min"] = {
            ["range"] = math.huge,                                     -- km, range (aircraft must track target)                              
            ["height"] = math.huge,                        -- km, max height                        
            ["speed"] = math.huge,                          -- mach, max speed
            ["tnt"] = math.huge,                                       -- kg                
        },
    }
}

-- update reference_missile_a2a 
for side_name, side in pairs(weapon_db) do

    for missile_name, missile in pairs(side) do
    
        if missile.type == "AAM" then

            if missile.range > reference_missile_a2a[missile.seeker]["max"].range then
                reference_missile_a2a[missile.seeker]["max"].range = missile.range
            end     
            
            if missile.range < reference_missile_a2a[missile.seeker]["min"].range then
                reference_missile_a2a[missile.seeker]["min"].range = missile.range
            end 
            
            if missile.max_height > reference_missile_a2a[missile.seeker]["max"].height then
                reference_missile_a2a[missile.seeker]["max"].height = missile.max_height
            end

            if missile.max_height < reference_missile_a2a[missile.seeker]["min"].height then
                reference_missile_a2a[missile.seeker]["min"].height = missile.max_height
            end

            if missile.max_speed > reference_missile_a2a[missile.seeker]["max"].speed then
                reference_missile_a2a[missile.seeker]["max"].speed = missile.max_speed
            end

            if missile.max_speed < reference_missile_a2a[missile.seeker]["min"].speed then
                reference_missile_a2a[missile.seeker]["min"].speed = missile.max_speed
            end

            if missile.tnt > reference_missile_a2a[missile.seeker]["max"].tnt then
                reference_missile_a2a[missile.seeker]["max"].tnt = missile.tnt
            end

            if missile.tnt < reference_missile_a2a[missile.seeker]["min"].tnt then
                reference_missile_a2a[missile.seeker]["min"].tnt = missile.tnt
            end

            if missile.seeker == "radar" then
                            
                if missile.semiactive_range and missile.semiactive_range > reference_missile_a2a[missile.seeker]["max"].semiactive_range then
                    reference_missile_a2a[missile.seeker]["max"].semiactive_range = missile.semiactive_range
                end

                if missile.semiactive_range and missile.semiactive_range < reference_missile_a2a[missile.seeker]["min"].semiactive_range then
                    reference_missile_a2a[missile.seeker]["min"].semiactive_range = missile.semiactive_range
                end

                if missile.active_range and missile.active_range > reference_missile_a2a[missile.seeker]["max"].active_range then
                    reference_missile_a2a[missile.seeker]["max"].active_range = missile.active_range
                end

                if missile.active_range and missile.active_range < reference_missile_a2a[missile.seeker]["min"].active_range then
                    reference_missile_a2a[missile.seeker]["min"].active_range = missile.active_range
                end                            
            end                                    
        end
    end
end
log.info("\nreference_missile_a2a:\n" .. inspect(reference_missile_a2a).."\n")

local loadouts_cost  = {

	["Strike"] = {
		["min"] = math.huge,
		["max"] = 0,
	},
	["Anti-ship Strike"] = {
		["min"] = math.huge,
		["max"] = 0,
	},
	["SEAD"] = {
		["min"] = math.huge,
		["max"] = 0,
	},
	["Intercept"] = {
		["min"] = math.huge,
		["max"] = 0,
	},
	["CAP"] = {
		["min"] = math.huge,
		["max"] = 0,
	},
	["Escort"] = {
		["min"] = math.huge,
		["max"] = 0,
	},
	["Fighter Sweep"] = {
		["min"] = math.huge,
		["max"] = 0,
	},
	["Reconnaissance"] = {
		["min"] = math.huge,
		["max"] = 0,
	},   
}


-- LOCAL FUNCTION

-- return true if task_name is a A2A task (CAP, ..)
local function isA2ATask(task_name)    

    return task_name == "Intercept" or task_name == "CAP" or task_name == "Fighter Sweep" or task_name == "Escort"
end

-- return true if task_name is a A2G task (Strike, ..)
local function isA2GTask(task_name)    

    return task_name == "Strike" or task_name == "Anti-ship Strike" or task_name == "SEAD"
end

-- return true if task_name isn't air fight task (refuelling, Transport and AWACS)
local function isNotFightTask(task_name)

    return task_name == "Transport" or task_name == "Refueling" or task_name == "AWACS" or task_name == "Laser Illumination" or task_name == "Flare Illumination" or task_name == "Escort Jammer" or task_name == "Reconnaissance"
end
    
-- return weapon data for weapon (side optional to speed up searching). Return nil if weapon not found
local function searchWeapon(weapon, side)
    local previous_log_level = log.level
	log.level = function_log_level
	local nameFunction = "searchWeapon(weapon: ( " .. weapon .. "), side(" .. (side or "nil") .. ") ): "
    log.traceLow(nameFunction .. "Start")

    if side then -- side is defined

        for weapon_name, weapon_data in pairs(weapon_db[side]) do -- iterate in weapon_db for side
            
            if weapon == weapon_name then   --found weapon, return weapon data
                log.traceVeryLow(nameFunction .. "found weapon: " .. weapon .. ", return weapon data")
                log.level = previous_log_level
                return weapon_data
            end
        end

    else -- side isn't defined

        for side, side_data in pairs(weapon_db) do -- iterate from side

            for weapon_name, weapon_data in pairs(weapon_db[side]) do -- iterate in weapon_db for side
            
                if weapon == weapon_name then   --found weapon, return weapon data
                    log.traceVeryLow(nameFunction .. "found weapon: " .. weapon .. ", return weapon data")
                    log.level = previous_log_level
                    return weapon_data
                end
            end
        end
    end
    log.traceLow(nameFunction .. "End")
    log.level = previous_log_level
    return nil -- not weapon was found, return nil
end

-- compute loadouts.standoff and loadouts.hattack with weapon.range for ASM
local function assignStandoffAndCost(loadout)
    local cost = 0
    local weapons = loadout.weapons
    
    for weapon_name, weapon_qty in pairs(weapons) do                       --iterate wapons airccraft
        local weapon_data = searchWeapon(weapon_name, nil)   
        
        if weapon_data then-- search weapon in db_weapons        
            local cost_weapon = weapon_data.cost or 0
            local compatible_task = false
            cost = cost + cost_weapon * weapon_qty
            
            for task_num, task_name in pairs(weapon_data.task) do
                
                if isA2GTask(task_name) then
                    compatible_task = true
                end
            end
            
            -- loadout altitude attack (hAttack) and standoff evalutation
            if camp.module_config.DC_LoadoutsAssignment.ACTIVATE_STANDOFF_SETUP and compatible_task and weapon_data and weapon_data.range and weapon_data.type and ( weapon_data.type == "ASM" or  weapon_data.type == "Rockets") then 
                local range = math.floor( 1000 * weapon_data.range * camp.module_config.DC_LoadoutsAssignment.PERCENTAGE_RANGE_FOR_STANDOFF_SETUP[weapon_data.type] )                
                local alfa, alfa_limit
                
                if weapon_data.hAttack then -- weapons defined hAttack has priority
                    loadout.hAttack = weapon_data.hAttack                    
                
                elseif not loadout.hAttack then -- hAttack loadout not define                                        
                    loadout.hAttack = math.floor( range *  factor_angle_of_descent[weapon_data.type].med ) -- calculation of hAttack in order to have an angle of descent of desired degrees      
                end                                                    

                if loadout.hAttack > camp.module_config.DC_LoadoutsAssignment.ALTITUDE_ATTACK[weapon_data.type].max then -- altitude is bigger of maximum limits
                    loadout.hAttack = camp.module_config.DC_LoadoutsAssignment.ALTITUDE_ATTACK[weapon_data.type].max -- assigned maximum altitude allowed
                    alfa = camp.module_config.DC_LoadoutsAssignment.ALTITUDE_ATTACK[weapon_data.type].max / range -- descent angle with maximum altitude allowed  
                    alfa_limit = camp.module_config.DC_LoadoutsAssignment.ANGLE_OF_DESCENT_IN_GROUND_ATTACK[weapon_data.type].min * math.pi / 180 -- minimum angle allowed in rads                   

                    if alfa < alfa_limit then  -- new descent angle is lower of minimum descent angle allowed
                        loadout.hAttack = math.floor( range * math.sin(alfa_limit) )-- update hAttack with minimum descent angle allowed
                    end

                elseif loadout.hAttack < camp.module_config.DC_LoadoutsAssignment.ALTITUDE_ATTACK[weapon_data.type].min then -- altitude is lower of minimum limits
                    loadout.hAttack = camp.module_config.DC_LoadoutsAssignment.ALTITUDE_ATTACK[weapon_data.type].min -- assigned minimum altitude allowed
                    alfa = camp.module_config.DC_LoadoutsAssignment.ALTITUDE_ATTACK[weapon_data.type].min / range -- descent angle with manimum altitude allowed      
                    alfa_limit = camp.module_config.DC_LoadoutsAssignment.ANGLE_OF_DESCENT_IN_GROUND_ATTACK[weapon_data.type].max * math.pi / 180 -- maximum angle allowed in rads              

                    if alfa > alfa_limit then  -- new descent angle is lower of minimum descent angle allowed
                        loadout.hAttack = math.floor( range * math.sin(alfa_limit) )-- update hAttack with maximum descent angle allowed
                    end
                end
                                
                local calculated_standoff = math.floor( math.sqrt( range * range - loadout.hAttack * loadout.hAttack ) )-- standoff is the cathetus of the triangle having hypotenuse = range and cathetus = hAttack

                if weapon_data.type == "Rockets" then log.info("-- weapon: " .. weapon_name .. ", range: " .. range) end                                    
                
                if weapon_data.type == "Rockets" then log.info("-- weapon: " .. weapon_name .. ", hAttack: " .. loadout.hAttack .. ", computed standoff: " .. calculated_standoff) end
                
                if not loadout.standoff or loadout.standoff > calculated_standoff then -- loadout standoff not defined or bigger of calculated or weapon defined standoff
                    loadout.standoff = calculated_standoff -- update loadout.standoff to choice lesser standoff from any weapons loadout                    
                
                elseif loadout.standoff < calculated_standoff then
                    log.warn("Note: loadout.standoff ( " ..  loadout.standoff .. " ) is lesser of calculated_standoff( " ..  calculated_standoff .. " )")
                end
                
                if weapon_data.type == "Rockets" then log.info("-- weapon: " .. weapon_name .. ", hAttack: " .. loadout.hAttack .. ", assigned standoff: " .. loadout.standoff) end
            end
        end
    end    
    loadout.cost = cost
end

-- return firepower value for weapon parameter (weapon_table) of a weapon
local function getWeaponFirepower(side, task, attribute, weapon_table)
    local previous_log_level = log.level
	log.level = function_log_level
	local nameFunction = "getWeaponFirepower(side: (" .. (side or "nil") .. "), task(" .. task .. "), attribute(" .. attribute .. "), weapon_table ): "    
    log.traceLow(nameFunction .. "Start")
    local weapon_name
    local weapon_qty
    local weapon_data
    local weapon_data_db
    local firepower = 0
    local check

    for weapon_name, weapon_qty in pairs(weapon_table) do                
        log.traceVeryLow(nameFunction .. "weapon_name: " .. weapon_name .. ", weapon_qty: " .. weapon_qty)
        weapon_data_db = searchWeapon(weapon_name, side)

        if weapon_data_db then
           log.traceVeryLow(nameFunction .. "found weapon_data_db for weapon: " .. weapon_name) 
            --check task
            check = false
            
            --verify if exist weapon with the required task
            for task_num, task_name in pairs(weapon_data_db.task) do
                
                if task_name == task then
                    check = true --exist weapon with the required task
                    break
                end
            end

            if check then
               
                check = false
                 
                --verify if exist weapon with required attribute
                for attribute_name, attribute_item in pairs(weapon_data_db.efficiency) do

                    if attribute_name == attribute then 
                        check = true --exist weapon with the required attribute
                        break
                    end
                end
            
                if check then   -- calculates the average fire based on the data of each weapon that has the same task and the same attribute
                    firepower = firepower + roundAtNumber(weapon_qty * weapon_data_db.efficiency[attribute].mix.accuracy * weapon_data_db.efficiency[attribute].mix.destroy_capacity * ( 1 - weapon_data_db.perc_efficiency_variability), camp.module_config.DC_LoadoutsAssignment.FIREPOWER_ROUNDED_COMPUTATION) -- untis firepower is calculated considering dimension target = mix and decreased of perc_efficiency_variability (aircraft needed bigger loadoutas to compensate efficiency variability)            
                    log.traceVeryLow(nameFunction .. "update unit firepower for weapon " .. weapon_name .. ": firepower: " .. firepower .. ", accuracy: " .. weapon_data_db.efficiency[attribute].mix.accuracy .. ", destroy_capacity: " .. weapon_data_db.efficiency[attribute].mix.destroy_capacity .. ", weapon_qty: " .. weapon_qty) 
                end
            end
        end
    end
    log.traceLow(nameFunction .. "End")
    log.level = previous_log_level
    return firepower
end

-- return true if year is within validity period of wapon usage (start_service <= year <= end_service)
local function isWeaponUsable(weapon_name, year)
    return ( weapon_db[weapon_name].start_service and weapon_db[weapon_name].start_service <= year or false ) and ( weapon_db[weapon_name].end_service and weapon_db[weapon_name].start_service >= year or false )
end

-- return firepower of A2A missile
local function evalutateFirepowerA2AMissile(missile_data)
    local previous_log_level = log.level
	log.level = function_log_level
	local nameFunction = "evalutateFirepowerA2AMissile(missile_data): "
    log.traceLow(nameFunction .. "Start")


    local function computeMissileAttributeFactor(attribute_value, max_value, min_value, weight)
        return weight * (attribute_value - min_value ) / (max_value - min_value)
    end

    local range_factor = computeMissileAttributeFactor(missile_data.range, reference_missile_a2a[missile_data.seeker].max.range, reference_missile_a2a[missile_data.seeker].min.range, weight_missile_a2a[missile_data.seeker].range)    
    local height_factor = computeMissileAttributeFactor(missile_data.max_height, reference_missile_a2a[missile_data.seeker].max.height, reference_missile_a2a[missile_data.seeker].min.height, weight_missile_a2a[missile_data.seeker].height)
    local speed_factor = computeMissileAttributeFactor(missile_data.max_speed, reference_missile_a2a[missile_data.seeker].max.speed, reference_missile_a2a[missile_data.seeker].min.speed, weight_missile_a2a[missile_data.seeker].speed)
    local tnt_factor = computeMissileAttributeFactor(missile_data.tnt, reference_missile_a2a[missile_data.seeker].max.tnt, reference_missile_a2a[missile_data.seeker].min.tnt, weight_missile_a2a[missile_data.seeker].tnt)
    local active_range_factor = 0

    if missile_data.seeker == "radar" then
            
        if missile_data.active_range then
            active_range_factor = computeMissileAttributeFactor(missile_data.active_range, reference_missile_a2a[missile_data.seeker].max.active_range, reference_missile_a2a[missile_data.seeker].min.active_range, weight_missile_a2a[missile_data.seeker].active_range)    
        end
    end

    local firepower = missile_data.reliability * camp.module_config.DC_LoadoutsAssignment.WEIGHT_MISSILE_A2A_RELIABILITY +  missile_data.manouvrability * camp.module_config.DC_LoadoutsAssignment.WEIGHT_MISSILE_A2A_MANOUVRABILITY  + weight_missile_a2a_attribute * (range_factor + speed_factor + height_factor + tnt_factor)
    firepower = roundAtNumber(firepower, camp.module_config.DC_LoadoutsAssignment.FIREPOWER_ROUNDED_COMPUTATION)

    if firepower > 1 then
        firepower = 1
    end
    
    -- normalize firepower from 0.1 to 1.1
    --firepower = 2^(firepower) - 0.1 

    log.traceVeryLow(nameFunction .. "(range_factor + speed_factor + height_factor + tnt_factor): " .. (range_factor + speed_factor + height_factor + tnt_factor))
    log.traceVeryLow(nameFunction .. "missile_data.reliability: " .. missile_data.reliability .. ", missile_data.manouvrability: " .. missile_data.manouvrability .. ", firepower: " .. firepower)
    log.level = previous_log_level
    return firepower
end

-- return a key (string) for table computed_target_efficiency
local function getKeyComputedEfficiency(num_targets_element, side, dimension_element, attribute, task, firepower_min, choice_value)
    return tostring(num_targets_element) .. side .. tostring(dimension_element) .. attribute .. task .. tostring(firepower_min) .. choice_value
end

-- insert an element (key, value) in table computed_target_efficiency
local function insertEfficiency(key, efficiency)
    computed_target_efficiency[key] = efficiency
end
 
-- return name. median efficiency and median efficiency_variability of weapons defined in weapon_db for attribute and task parameters, return nil if no weapon found
-- efficiency = accuracy * destroy_capacity (1 max, 0.01 min)
-- accuracy: hit success percentage, 1 max, 0.1 min, 
-- destroy_capacity: destroy single element capacity,  1 max ( element destroyed with single hit),  0.1 min
local function medEfficiencyWeapon(side, target_attribute, target_dimension, task)
    local previous_log_level = log.level
	log.level = function_log_level
	local nameFunction = "medEfficiencyWeapon(target_attribute: " .. target_attribute .. ", target_dimension: " .. target_dimension .. ", task: " .. task .."): "
    log.traceLow(nameFunction .. "Start")
    
    local draft_weapon_efficiency = 0
    local draft_weapon_variability = 0    
    local i = 0
    local break_loop = false


    -- calculates the average fire based on the data of each weapon that has the same task and the same attribute
    for weapon_name, weapon_data in pairs(weapon_db[side]) do -- iterate weapons
        
        if weapon_data.start_service and ( weapon_data.start_service > camp.date.year ) then
            log.traceLow(nameFunction .. "campaign year(" .. camp.date.year .. ") is over of weapon start service(" .. weapon_data.start_service .. "), End")            
            
        else        

            for n_weapon_task, weapon_task in pairs(weapon_data.task) do -- itarate to search weapon for task

                if task == weapon_task then  -- found weapon for this task                

                    for attribute_name, attribute_data in pairs(weapon_data.efficiency) do -- iterate for search attribute data for target attirbute

                        if target_attribute == attribute_name then  -- found attribure data for target attribute
                            log.traceVeryLow(nameFunction .. "found weapon with attribute: " .. attribute_name .. ", and task: " .. task)
                            break_loop = true

                            for dimension_name, dimension_data in pairs(attribute_data) do -- iterate for search dimension data for target dimension

                                if dimension_name == target_dimension then -- found efficiency data for target dimension
                                    draft_weapon_efficiency = draft_weapon_efficiency + dimension_data.accuracy * dimension_data.destroy_capacity       
                                    draft_weapon_variability = draft_weapon_variability +  weapon_data.perc_efficiency_variability                         
                                    i = i + 1
                                    log.traceVeryLow(nameFunction .. "found weapon: " .. weapon_name .. " with efficienty: " .. tostring(dimension_data.accuracy * dimension_data.destroy_capacity) .. "(accuracy value: " .. dimension_data.accuracy .. ", destroy_capacity value: " .. dimension_data.destroy_capacity .. "), perc_efficiency_variability: " .. weapon_data.perc_efficiency_variability .. ", values added for comput media: " .. i)                                                                         
                                end
                            end  
                            break_loop = true
                            break -- break attribute iteration, weapon efficiency data are defined for single attribute and single task
                        end
                    end
                end             

                if break_loop then
                    break -- break task iteration, weapon efficiency data are defined for single attribute and single task
                end
            end
        end
    end

    if break_loop then
        draft_weapon_efficiency = roundAtNumber( draft_weapon_efficiency / i, camp.module_config.DC_LoadoutsAssignment.FIREPOWER_ROUNDED_COMPUTATION)
        draft_weapon_variability = roundAtNumber( draft_weapon_variability / i, camp.module_config.DC_LoadoutsAssignment.FIREPOWER_ROUNDED_COMPUTATION)
    else
        draft_weapon_efficiency = nil
        draft_weapon_variability = nil
    end

    log.traceLow(nameFunction .. "End")
    log.level = previous_log_level
    return draft_weapon_efficiency, draft_weapon_variability
end

-- return name. efficiency and efficiency_variability of weapon with max efficiency defined in weapon_db for attribute and task parameters, return efficiency -1 if no weapon found
-- efficiency = accuracy * destroy_capacity (1 max, 0.01 min)
-- accuracy: hit success percentage, 1 max, 0.1 min, 
-- destroy_capacity: destroy single element capacity,  1 max ( element destroyed with single hit),  0.1 min
local function maxEfficiencyWeapon(side, target_attribute, target_dimension, task)
    local previous_log_level = log.level
	log.level = function_log_level
	local nameFunction = "maxEfficiencyWeapon(target_attribute: " .. target_attribute .. ", target_dimension: " .. target_dimension .. ", task: " .. task .."): "
    log.traceLow(nameFunction .. "Start")

    local choice_weapon_efficiency = -1
    local draft_weapon_efficiency = -2
    local choice_weapon_variability = -3
    local choice_weapon_name = ""
    local break_loop = false

    for weapon_name, weapon_data in pairs(weapon_db[side]) do -- iterate weapons     
        
        if weapon_data.start_service and ( weapon_data.start_service > camp.date.year ) then
            log.traceLow(nameFunction .. "campaign year(" .. camp.date.year .. ") is over of weapon start service(" .. weapon_data.start_service .. "), End")            
            
        else  

            for n_weapon_task, weapon_task in pairs(weapon_data.task) do -- itarate to search weapon for task

                if task == weapon_task then  -- found weapon for this task               

                    for attribute_name, attribute_data in pairs(weapon_data.efficiency) do -- iterate for search attribute data for target attirbute

                        if target_attribute == attribute_name then  -- found attribure data for target attribute
                            log.traceVeryLow(nameFunction .. "found weapon with attribute: " .. attribute_name .. ", and task: " .. task)
                            break_loop = true

                            for dimension_name, dimension_data in pairs(attribute_data) do -- iterate for search dimension data for target dimension

                                if dimension_name == target_dimension then -- found efficiency data for target dimension
                                    draft_weapon_efficiency = roundAtNumber(dimension_data.accuracy * dimension_data.destroy_capacity, camp.module_config.DC_LoadoutsAssignment.FIREPOWER_ROUNDED_COMPUTATION)
                                    
                                    if choice_weapon_efficiency < draft_weapon_efficiency then                           
                                        log.traceVeryLow(nameFunction .. "found weapon: " .. weapon_name .. " with bigger efficienty: " .. draft_weapon_efficiency .. "(accuracy value: " .. dimension_data.accuracy .. ", destroy_capacity value: " .. dimension_data.destroy_capacity .. "), perc_efficiency_variability: " .. weapon_data.perc_efficiency_variability .. ", previous best efficiency value: " .. choice_weapon_efficiency)         
                                        choice_weapon_efficiency = draft_weapon_efficiency
                                        choice_weapon_variability = weapon_data.perc_efficiency_variability
                                        choice_weapon_name = weapon_name
                                    end
                                end
                            end  
                            break_loop = true
                            break -- break attribute iteration, weapon efficiency data are defined for single attribute and single task
                        end
                    end
                end
                
                if break_loop then
                    break -- break task iteration, weapon efficiency data are defined for single attribute and single task
                end            
            end
        end
    end
    log.traceLow(nameFunction .. "End")
    log.level = previous_log_level
    return choice_weapon_name, choice_weapon_efficiency, choice_weapon_variability
end

-- return name efficiency and efficiency_variability of weapon with min efficiency defined in weapon_db for attribute and task parameters, return efficiency math.uge if no weapon found
-- efficiency = accuracy * destroy_capacity (1 max, 0.01 min)
-- accuracy: hit success percentage, 1 max, 0.1 min, 
-- destroy_capacity: destroy single element capacity,  1 max ( element destroyed with single hit),  0.1 min
local function minEfficiencyWeapon(side, target_attribute, target_dimension, task)
    local previous_log_level = log.level
	log.level = function_log_level
	local nameFunction = "maxEfficiencyWeapon(target_attribute: " .. target_attribute .. ", target_dimension: " .. target_dimension .. ", task: " .. task .."): "
    log.traceLow(nameFunction .. "Start")

    local choice_weapon_efficiency = camp.module_config.DC_LoadoutsAssignment.MAX_EFFICIENCY_WEAPON_ATTRIBUTE
    local draft_weapon_efficiency
    local choice_weapon_variability = 0
    local choice_weapon_name = ""
    local break_loop = false


    for weapon_name, weapon_data in pairs(weapon_db[side]) do -- iterate weapons

        if weapon_data.start_service and ( weapon_data.start_service > camp.date.year ) then
            log.traceLow(nameFunction .. "campaign year(" .. camp.date.year .. ") is over of weapon start service(" .. weapon_data.start_service .. "), End")            
            
        else  
        
            for n_weapon_task, weapon_task in pairs(weapon_data.task) do -- itarate to search weapon for task

                if task == weapon_task then  -- found weapon for this task

                    for attribute_name, attribute_data in pairs(weapon_data.efficiency) do -- iterate for search attribute data for target attirbute

                        if target_attribute == attribute_name then  -- found attribure data for target attribute
                            log.traceVeryLow(nameFunction .. "found weapon with attribute: " .. attribute_name .. ", and task: " .. task)

                            for dimension_name, dimension_data in pairs(attribute_data) do -- iterate for search dimension data for target dimension

                                if dimension_name == target_dimension then -- found efficiency data for target dimension
                                    draft_weapon_efficiency = roundAtNumber(dimension_data.accuracy * dimension_data.destroy_capacity, camp.module_config.DC_LoadoutsAssignment.FIREPOWER_ROUNDED_COMPUTATION)
                                    
                                    if choice_weapon_efficiency > draft_weapon_efficiency then                           
                                        log.traceVeryLow(nameFunction .. "found weapon: " .. weapon_name .. " with bigger efficienty: " .. draft_weapon_efficiency .. "(accuracy value: " .. dimension_data.accuracy .. ", destroy_capacity value: " .. dimension_data.destroy_capacity .. "), perc_efficiency_variability: " .. weapon_data.perc_efficiency_variability .. ", previous best efficiency value: " .. choice_weapon_efficiency)         
                                        choice_weapon_efficiency = draft_weapon_efficiency
                                        choice_weapon_variability = weapon_data.perc_efficiency_variability
                                        choice_weapon_name = weapon_name
                                    end
                                end
                            end  
                            break_loop = true
                            break -- weapon efficiency data are defined for single task                        
                        end
                    end
                end
                if break_loop then
                    break -- break task iteration, weapon efficiency data are defined for single attribute and single task
                end               
            end
        end
    end
    log.traceLow(nameFunction .. "End")
    log.level = previous_log_level
    return choice_weapon_name, choice_weapon_efficiency, choice_weapon_variability
end

-- da inserire in UTIL_Function o in un nuovo file DC_Firepower.lua (con data tab e funzioni)
-- compute firepower min, max for a target utiling best efficiency dedicated weapon. number of element = num_targets_element, using a dedicated weapon (defined in targetlist for that task and attribute) 
local function evaluate_target_firepower( num_targets_element, side, dimension_element, attribute, task, choice_value )    
    local previous_log_level = log.level
	log.level = function_log_level
	local nameFunction = "evaluate_target_firepower( num_targets_element(" .. num_targets_element .. "), side: " .. side .. ", dimension_element(" .. dimension_element .. "), attribute(" .. attribute .. "), task(" .. task .. ") ): "
    log.traceLow(nameFunction .. "Start")
    local best_name_weapon, best_weapon_efficiency, best_weapon_variability
    local calculated_firepower_min, calculated_firepower_max

    if choice_value == "max" then
        best_name_weapon, best_weapon_efficiency, best_weapon_variability = maxEfficiencyWeapon(side, attribute, dimension_element, task)

    elseif choice_value == "min" then
        best_name_weapon, best_weapon_efficiency, best_weapon_variability = minEfficiencyWeapon(side, attribute, dimension_element, task)
    
    else
        best_weapon_efficiency, best_weapon_variability = medEfficiencyWeapon(side, attribute, dimension_element, task)
    end

    log.traceVeryLow(nameFunction .. "best_name_weapon(choice_value: " .. choice_value .. "): " .. (best_name_weapon or "nil") .. ", best_weapon_efficiency: " .. (best_weapon_efficiency or "nil") .. ", best_weapon_variability: " .. (best_weapon_variability or "nil"))

    if best_weapon_efficiency then

        if best_weapon_efficiency < camp.module_config.DC_LoadoutsAssignment.MIN_EFFICIENCY_WEAPON_ATTRIBUTE then

            if best_weapon_efficiency < 0 then -- not found a weapon for this target
                log.warn(nameFunction .. "not found weapon for task: " .. task .. ", attribute: " .. attribute .. ", compute firepower with best_efficiency = 0.5")
                best_weapon_efficiency = 0.5
            
            else
                log.warn(nameFunction .. "found weapon for task: " .. task .. ", attribute: " .. attribute .. ", with best_efficiency < camp.module_config.DC_LoadoutsAssignment.MIN_EFFICIENCY_WEAPON_ATTRIBUTE(" .. camp.module_config.DC_LoadoutsAssignment.MIN_EFFICIENCY_WEAPON_ATTRIBUTE .. "), compute firepower with best_efficiency = " .. camp.module_config.DC_LoadoutsAssignment.MIN_EFFICIENCY_WEAPON_ATTRIBUTE)
                best_weapon_efficiency = camp.module_config.DC_LoadoutsAssignment.MIN_EFFICIENCY_WEAPON_ATTRIBUTE
            end
        
        elseif best_weapon_efficiency >= camp.module_config.DC_LoadoutsAssignment.MAX_EFFICIENCY_WEAPON_ATTRIBUTE then -- not found a weapon for this target
            log.warn(nameFunction .. "not found weapon for task: " .. task .. ", attribute: " .. attribute)
            best_weapon_efficiency = nil
        end

    else
        log.warn(nameFunction .. "not found weapon for task: " .. task .. ", attribute: " .. attribute)
        best_weapon_efficiency = nil
    end
    
    if best_weapon_efficiency then
        calculated_firepower_min = math.ceil( num_targets_element / best_weapon_efficiency )
        calculated_firepower_max = math.floor( calculated_firepower_min * ( 1 + best_weapon_variability ) * camp.module_config.DC_LoadoutsAssignment.FACTOR_FOR_CALCULATED_TARGET_FIREPOWER_MAX )     
    end

    log.traceVeryLow(nameFunction .. "computed firepower min, max: " .. (calculated_firepower_min or "nil") .. ", " .. (calculated_firepower_max or "nil"))
    log.traceLow(nameFunction .. "End")
    log.level = previous_log_level
    return calculated_firepower_min, calculated_firepower_max
end

-- return firepower (min or max) value 
local function getTargetFirepower( num_targets_element, side, dimension_element, attribute, task, choice_firepower_min, choice_value )  
    local previous_log_level = log.level
	log.level = function_log_level
	local nameFunction = "getTargetFirepower( num_targets_element(" .. num_targets_element .. "), side: " .. side .. ", dimension_element(" .. dimension_element .. "), attribute(" .. attribute .. "), task(" .. task .. "), choice_firepower_min: " .. tostring(choice_firepower_min) .. ", choice_value: " .. choice_value .. "): "
    log.traceLow(nameFunction .. "Start")
    local key = getKeyComputedEfficiency(num_targets_element, side, dimension_element, attribute, task, choice_firepower_min, choice_value)
    log.traceVeryLow(nameFunction .. "key: " ..  key)
    local firepower = computed_target_efficiency[key]

    if firepower then -- firepower exist in computed_target_efficiency table
        log.traceVeryLow(nameFunction .. "firepower exist in computed_target_efficiency table, firepower: " ..  firepower)
        log.level = previous_log_level
        return firepower -- return firepower
    
    else  -- firepower not exist in computed_target_efficiency table  
        local firepower, firepower_max        
        firepower, firepower_max = evaluate_target_firepower( num_targets_element, side, dimension_element, attribute, task, choice_value ) --compute firepower min and max        

        if firepower and firepower_max then -- store firepower(min) and firepower_max in  computed_target_efficiency table  
            log.traceVeryLow(nameFunction .. "firepower not exist in computed_target_efficiency table, compute firepower min and max: " ..  firepower .. ", " .. firepower_max)
            key = getKeyComputedEfficiency(num_targets_element, side, dimension_element, attribute, task, true, choice_value)
            computed_target_efficiency[key] = firepower
            -- table.insert(computed_target_efficiency, 1, {[key] = firepower} )
            log.traceVeryLow(nameFunction .. "store firepower min  computed_target_efficiency table, key: " ..  key)
            key = getKeyComputedEfficiency(num_targets_element, side, dimension_element, attribute, task, false, choice_value)
            computed_target_efficiency[key] = firepower_max
            --table.insert(computed_target_efficiency, 1, {[key] = firepower_max} )
            log.traceVeryLow(nameFunction .. "store firepower max in  computed_target_efficiency table, key: " ..  key)
        else
            log.warn(nameFunction .. "firepower wasn't computed, returned nil value. End")
            log.level = previous_log_level
            return nil
        end
    
        if choice_firepower_min then --if requested firepower min
            log.level = previous_log_level
            log.warn(nameFunction .. "firepower min computed: " .. firepower .. ", returned value. End")
            return firepower
    
        else --if requested firepower max
            log.level = previous_log_level
            log.warn(nameFunction .. "firepower max computed: " .. firepower_max .. ", returned value. End")
            return firepower_max
        end        
    end
end

-- load computed_target_efficiency table, if not exist create one new
local function loadComputedTargetEfficiency()

    if camp.mission > 1 and io.open("Active/computed_target_efficiency.lua", "r") then
        require("Active/computed_target_efficiency") -- load stored computed_target_efficiency.lua if not first mission campaign and exist table

    else -- initialize new computed_target_efficiency if not exist 
        computed_target_efficiency = {} -- table contains target efficiency values: hash table with hash = target and value = firepower med for that target
        SaveTabOnPath( "Active/", "computed_target_efficiency", computed_target_efficiency )         
    end
end

-- upgrade loadouts_cost table
local function updateLoadoutsCostTable()
    for aircraft_type, loadouts in pairs(db_loadouts) do

        for task_name, task in pairs(loadouts) do

            if not isNotFightTask(task_name) then
            
                for loadout_name, loadout in pairs(task) do

                    if not loadout.cost then
                        log.warn("aircraft_type: " .. aircraft_type .. ", task_name: " .. task_name .. ", loadout_name: " .. loadout_name)
                    end
                                
                    if loadouts_cost[task_name].max < loadout.cost then
                        loadouts_cost[task_name].max = loadout.cost

                    elseif loadouts_cost[task_name].min > loadout.cost then
                        loadouts_cost[task_name].min = loadout.cost
                    end               
                end
            end
        end
    end
end

local function insertFactorCostIndb_loadouts()-- insert factor_cost in db_loadouts
    for aircraft_type, loadouts in pairs(db_loadouts) do

        for task_name, task in pairs(loadouts) do

            if not isNotFightTask(task_name) then
            
                for loadout_name, loadout in pairs(task) do
                
                    loadout.cost_factor = roundAtNumber( 1 - (loadout.cost - loadouts_cost[task_name].min ) / (loadouts_cost[task_name].max - loadouts_cost[task_name].min), camp.module_config.DC_LoadoutsAssignment.FIREPOWER_ROUNDED_COMPUTATION)			
                end
            end
        end
    end
end


-- GLOBAL FUNCTION

-- call from DC_UpdateTargetList, initialize firepower value for target in targetlist
function defineTargetListFirepower(targetlist)
    local previous_log_level = log.level
	log.level = function_log_level
	local nameFunction = "defineTargetListFirepower(targetlist): "
    log.traceLow(nameFunction .. "Start")
    local alive
 
    loadComputedTargetEfficiency()

    if not computed_target_efficiency then
        log.error(nameFunction .. "computed_target_efficiency wasn't initializated!")
    end

    local task, num_elements, attribute, class, dimension, firepower_min, firepower_max   

    for side_name, side in pairs(targetlist) do
    
        for target_name, target in pairs(side) do
            
            task = target.task -- antiship_strike, strike, ...            

            if isNotFightTask(task) then
                firepower_min = 1
                firepower_max = 1
            
            elseif task == "CAP" or  task == "Intercept" or task == "Fighter Sweep" or task == "Escort" then
                firepower_min = camp.module_config.DC_LoadoutsAssignment.FIREPOWER_FOR_AA_TARGETS[side_name][task].min -- minimum number of enemy aircraft expected
                firepower_max = camp.module_config.DC_LoadoutsAssignment.FIREPOWER_FOR_AA_TARGETS[side_name][task].max -- maximum number of enemy aircraft expected            

            else            
                attribute = target.attributes[1] or "nil" -- soft, armor ecc (deve? essere sempre un solo attributo)            
                class = target.class or "scenery"-- ship, vehicle, ecc.

                if target.elements then
                    
                    if target.alive then
                        alive = target.alive / 100
                    else
                        alive = 1
                    end

                    num_elements = #target.elements * alive -- num of element of target
                
                elseif target.unit and target.unit.number then
                    num_elements = target.unit.number
                
                elseif class == "ship" then
                    num_elements = 9

                elseif class == "vehicle" then
                    num_elements = 13

                elseif class == "airbase" then
                    num_elements = 9

                elseif class == "static" then
                    num_elements = 8

                else
                    num_elements = 8
                    log.warn(nameFunction .. "elements and class not defined -> nume_element = 8")
                end
                dimension = target.dimension or "mix" -- mix, med, big, small


                log.traceVeryLow(nameFunction .. "target_name: " .. target_name .. ", task: " .. task .. ", num_elements" .. num_elements .. ", attribute: " .. attribute .. ", class: " .. class .. ", dimension: " ..dimension)

                firepower_min = getTargetFirepower(num_elements, side_name, dimension, attribute, task, true, "med")
                firepower_max = getTargetFirepower(num_elements, side_name, dimension, attribute, task, false, "med")                
            end
            log.traceVeryLow(nameFunction .. "target_name: " .. target_name .. ", firepower_min: " .. (firepower_min or "nil") .. ", firepower_max: " .. (firepower_max or "nil"))

            target.firepower.min = firepower_min or 99999
            target.firepower.max = firepower_max or 99999            
        end
    end    
    SaveTabOnPath( "Active/", "computed_target_efficiency", computed_target_efficiency )         
    log.traceVeryLow(nameFunction .. "computed_target_efficiency:\n" .. inspect(computed_target_efficiency))
    log.traceLow(nameFunction .. "End")
    log.level = previous_log_level
    return
end

-- call from MAIN_NextMission, initialize firepower value for loadouts
function defineLoadoutsFirepowerAndCost()
    local previous_log_level = log.level
	log.level = function_log_level
	local nameFunction = "defineLoadoutsFirepower(): "
    log.traceLow(nameFunction .. "Start")
    local task, weapons, weapon_data, firepower, i    

    for aircraft_name, aircraft in pairs(db_loadouts) do -- interate aircraft
    
        for task_name, task in pairs(aircraft) do -- iterate task: Intercept, CAP, antiship_strike, strike, ...            

            for loadout_name, loadout in pairs(task) do -- iterate loadout       
                         
                weapons = loadout.weapons

                if weapons then --aircraft has weapons

                    assignStandoffAndCost(loadout) 
                    
                    if isA2ATask(task_name) or task_name == "Reconnaissance" then --air to air task or armed reconnaisance task
                        firepower = 0

                        for weapon_name, weapon_qty in pairs(weapons) do                       --iterate wapons airccraft
                            weapon_data = searchWeapon(weapon_name, nil)                        -- search weapon in db_weapons

                            if weapon_data and weapon_data.type and weapon_data.type == "AAM" and weapon_data.start_service and ( weapon_data.start_service <= camp.date.year ) then -- weapons is compliants update firepower
                                firepower = firepower + weapon_qty * evalutateFirepowerA2AMissile(weapon_data) --update firepower with firpowers weapon
                                log.traceVeryLow(nameFunction .. "computed firepower for aircraft: " .. aircraft_name .. ", task: " .. task_name .. ", weapon: " .. weapon_name .. ", quantity: " .. weapon_qty .. ", firepower: " .. firepower)
                                
                            elseif weapon_data and weapon_data.start_service and ( weapon_data.start_service > camp.date.year ) then -- weapon not in service during the campaign period
                                log.traceLow(nameFunction .. "campaign year(" .. camp.date.year .. ") is over of weapon start service(" .. weapon_data.start_service .. "), End")            
                                log.warn(nameFunction .. "weapon(" .. weapon_name .. ") start service: " .. weapon_data.start_service .. " not compliant with campaign year: " .. camp.date.year)
                                                            
                            else
                                log.warn(nameFunction .. "weapon:" .. weapon_name .. ", not found in db_weapon. Return")                                
                            end
                        end                        
                    
                    elseif isA2GTask(task_name) then --air to ground task
                        i = 0
                        firepower = 0
                        
                        for attribute_num, attribute_name in pairs(loadout.attributes) do -- iterate attributes loadout
                            firepower = firepower + getWeaponFirepower(nil, task_name, attribute_name, weapons) -- update firepower with weapon firepower
                            i = i + 1
                            log.traceVeryLow(nameFunction .. "computed firepower for aircraft: " .. aircraft_name .. ", task: " .. task_name .. ", attribute_name: " .. attribute_name .. ", firepower: " .. firepower .. ", i: " .. i)            
                        end 
                        firepower = roundAtNumber(firepower / i, camp.module_config.DC_LoadoutsAssignment.FIREPOWER_ROUNDED_ASSIGNEMENT ) -- firpower is median value of firepowers weapon                       

                    elseif isNotFightTask(task_name) then
                        log.warn(nameFunction .. "check db_loadouts.lua, found a Not Fight Task: " .. task_name .. " with weapons:\n" .. inspect(weapons))

                    else
                        log.warn(nameFunction .. "unknow task: " .. task_name .. ", check db_loadouts.lua")
                    end

                    if firepower then                        
                        loadout.firepower = firepower -- update firepower in db_loadouts.lua                        
                        log.traceVeryLow(nameFunction .. "computed firepower for aircraft: " .. aircraft_name .. ", task: " .. task_name .. ", firepower: " .. firepower .. " assigned in db_loadouts")
                    
                    else
                        log.traceVeryLow(nameFunction .. "firepower wasn't computed for aircraft: " .. aircraft_name .. ", task: " .. task_name .. ", fi6repower  assigned in db_loadouts")
                    end
                end                
            end            
        end
    end  
    log.info("\ndb_loadouts:\n" .. inspect(db_loadouts).."\n")
    updateLoadoutsCostTable() -- update loadouts_cost table
    log.info("\nloadouts_cost:\n" .. inspect(loadouts_cost).."\n")
    insertFactorCostIndb_loadouts()-- insert factor_cost in db_loadouts
    log.traceLow(nameFunction .. "End")
    log.level = previous_log_level
    return
end

-- call from MAIN_NextMission, update cruise parameters value (vCruise, hCruise) for loadouts
function defineLoadoutsCruiseParameters()       
    --activateLog(true, true, log, "traceVeryLow")
    -- assign cruise parameter: vCruise and hCruise
    for type_name, type in pairs(db_loadouts) do
        
        for task_name, task in pairs(type) do

            for loadout_name, loadout in pairs(task) do
                log.traceLow("aircraft type: " .. type_name .. ", loadout_name: " .. loadout_name ..  ", task: " .. task_name)

                if loadout.coalition and loadout.role and loadout.role_altitude then
                    log.traceLow("loadout cruise parameter: loadout.coalition: " .. (loadout.coalition or "nil") .. ", loadout.role: " .. (loadout.role or "nil") ..  ", loadout.role_altitude: " .. (loadout.role_altitude or "nil"))                
                    log.traceLow("loadout.vCruise: " .. (loadout.vCruise or "nil").. ", loadout.hCruise: " .. (loadout.hCruise or "nil") ..  ", loadout.hAttack: " .. (loadout.hAttack or "nil"))

                    if task_name == "Escort" or task_name == "SEAD" or task_name == "Laser Illumination" or task_name == "Flare Illumination" or task_name == "Escort Jammer" then
                        loadout.vCruise = escort_cruise_speed_at_altitude[loadout.coalition][loadout.role][loadout.role_altitude]
                        loadout.hCruise = escort_cruise_altitude[loadout.coalition][loadout.role][loadout.role_altitude]                    
                    
                    elseif task_name == "AWACS" or task_name == "Strike" or task_name == "Anti-ship Strike" or task_name == "Reconnaissance" or task_name == "Transport" or task_name == "Refueling" then
                        loadout.vCruise = cruise_speed_at_altitude[loadout.coalition][loadout.role][loadout.role_altitude]                
                        loadout.hCruise = cruise_param_calculated[loadout.coalition][loadout.role][loadout.role_altitude].hCruise

                        if loadout.role == "bomber" and loadout.weaponType == "Bombs" then
                            loadout.hAttack = loadout.hCruise
                        end
                    end
                    log.traceLow("loadout.vCruise: " .. (loadout.vCruise or "nil") .. ", loadout.hCruise: " .. (loadout.hCruise or "nil") ..  ", loadout.hAttack: " .. (loadout.hAttack or "nil"))
                else
                    log.warn("loadout cruise parameter not defined loadout.coalition: " .. (loadout.coalition or "nil") .. ", loadout.role: " .. (loadout.role or "nil") ..  ", loadout.role_altitude: " .. (loadout.role_altitude or "nil"))
                end
            end
        end
    end
--activateLog(false, true, log, log_level)
end
