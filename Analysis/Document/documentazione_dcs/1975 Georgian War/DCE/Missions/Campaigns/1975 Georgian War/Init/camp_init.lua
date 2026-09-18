--Initial status of the campaign (static file, not updated)
--Copied to camp_status.lua and for use in running campaign


---------------------------------------------------------------------------------------------------------
-- Old_Boy rev. OB.1.0.2: grouping module configuration parameters into a single table: module_config 
-- Old_Boy rev. OB.1.0.1: implements compute firepower code (property)
-------------------------------------------------------------------------------------------------------

camp = {
	title = "1975 Georgian War",	--Title of campaign (name of missions)
	version = "V 1.1",
	mission = 1,					--campaig mission number
	date = {						--campaign date
        day = 13,
        year = 1975,
        month = 9,
    },
	time = 3600,					--daytime in seconds
	dawn = 21600,					--time of dawn in seconds
	dusk = 65700,					--time of dusk in seconds
	mission_duration = 5400,		--duration of a mission in seconds
	idle_time_min = 10800,			--minimum time between missions in seconds
	idle_time_max = 14400,			--maximum time between missions in seconds
	startup = 900,					--time in seconds allocated for player start-up
	units = "metric",				--unit output in briefing (imperial or metric)
	weather = {						--campaign weather
		pHigh = 50,				    --probability of high pressure weather system
		pLow = 50,					--probability of low pressure weather system
		refTemp = 20,				--average day max temperature
	},
	variation = 4,					--variation in degrees from true north to magneitic north
	debug = false,					--debug mode
	-- hotstart = false,       		--player flights starts with engines running     ---- change it  in init/conf_mod.lua
    -- intercept_hotstart = true,    --player flights with intercept task starts with engines running  ---- change it  in init/conf_mod.lua

	module_config = {

        SCORE_TASK_FACTOR = {

            ["blue"] = {
                ["CAP"] = 1,
                ["AWACS"] = 1,
                ["Intercept"] = 1,
                ["Escort"] = 1,
                ["Fighter Sweep"] = 1,
                ["Anti-ship Strike"] = 1,
                ["Strike"] = {
                    ["armor"] = 1,
                    ["soft"] = 1,
                    ["SAM"] = 1,
                    ["Structure"] = 1,
                    ["Bridge"] = 1,
                    ["Parked Aircraft"] = 1,
                    ["hard"] = 1,
                },
                ["Reconnaissance"] = 1,
                ["Refueling"] = 1,
                ["Transport"] = 1,
                ["SEAD"] = 1,
                ["Laser Illumination"] = 1,
            },
    
            ["red"] = {
                ["CAP"] = 1,
                ["AWACS"] = 1,
                ["Intercept"] = 1,
                ["Escort"] = 1,
                ["Fighter Sweep"] = 1,
                ["Anti-ship Strike"] = 1,
                ["Strike"] = {
                    ["armor"] = 1,
                    ["soft"] = 1,
                    ["SAM"] = 1,
                    ["Structure"] = 1,
                    ["Bridge"] = 1,
                    ["Parked Aircraft"] = 1,
                    ["hard"] = 1,
                },
                ["Reconnaissance"] = 1,
                ["Refueling"] = 1,
                ["Transport"] = 1,
                ["SEAD"] = 1,
                ["Laser Illumination"] = 1,
            },
        },

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
        
                        ["min"] = 3,
                        ["max"] = 6,
                    },
        
                    ["Escort"] = {
        
                        ["min"] = 2,
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
        
                        ["min"] = 3,
                        ["max"] = 6,
                    },
        
                    ["Escort"] = {
        
                        ["min"] = 2,
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
        
                            ["min_vCruise_TAS"] = 450 / 3.6, -- Km/h @ slm
                            ["max_vCruise_TAS"] = 600 / 3.6, -- Km/h @ slm
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

		["ATO_ThreatEvaluation"] = {
	
			MIN_ASSET_FOR_COMPUTE_LEVEL_INTERCEPT = 3,								-- minimum asset unless specified otherwise
			MIN_ASSET_FOR_COMPUTE_LEVEL_CAP = 3,									-- minimum asset unless specified otherwise
			GROUND_THREAT_RILEVABILITY_BLUE_AIR_CAPACITY = 1,						-- capacity for ground threath rilevability (1: max capacity, 0 minimum capacity)
			GROUND_THREAT_RILEVABILITY_BLUE_GROUND_CAPACITY = 1,					-- capacity for ground threath rilevability (1: max capacity, 0 minimum capacity)
			GROUND_THREAT_RILEVABILITY_RED_AIR_CAPACITY = 1,						-- capacity for ground threath rilevability (1: max capacity, 0 minimum capacity)
			GROUND_THREAT_RILEVABILITY_RED_GROUND_CAPACITY = 1,						-- capacity for ground threath rilevability (1: max capacity, 0 minimum capacity)
			MAN_SAM_RILEVABILITY = 0.2,												-- specific ground asset rilevability (1: detectability ensured, 0 asset undetectable)
			SMALL_AAA_SAM_IR_VEHICLE_RILEVABILITY = 0.5,							-- specific ground asset rilevability (1: detectability ensured, 0 asset undetectable)
			SMALL_AAA_SAM_RADAR_VEHICLE_RILEVABILITY = 0.6,							-- specific ground asset rilevability (1: detectability ensured, 0 asset undetectable)
			MEDIUM_AAA_SAM_IR_VEHICLE_RILEVABILITY = 0.7,							-- specific ground asset rilevability (1: detectability ensured, 0 asset undetectable)
			MEDIUM_AAA_SAM_RADAR_VEHICLE_RILEVABILITY = 0.8,
			LARGE_SAM_VEHICLE_RILEVABILITY = 0.9,
			SMALL_AAA_SAM_FIXEDPOS_RILEVABILITY = 0.8,
			MEDIUM_AAA_SAM_FIXEDPOS_RILEVABILITY = 0.9,
			LARGE_AAA_SAM_FIXEDPOS_RILEVABILITY = 1,
			SMALL_SHIP_RILEVABILITY = 0.75,
			MEDIUM_SHIP_RILEVABILITY = 1,
			LARGE_SHIP_RILEVABILITY = 1,
		},

		["ATO_Generator"] = {
                            
                MIN_CLOUD_DENSITY = 0.8,											-- min clouds density for evalutation weather mission condition (defalut = 0.8)
                MIN_FOG_VISIBILITY = 5000,											-- min fog visibility for any task (default: 5000m)
                MIN_CLOUD_EIGHT_ABOVE_AIRBASE = 333,								-- min eight above airbase for execute any task (default: 333m, 1000 ft)
                BOMBERS_RECO = {"S-3B",  "F-117A", "B-1B", "B-52H", "Tu-22M3", "Tu-95MS", "Tu-142", "Tu-160", "MiG-25RBT"},

            ["blue"] = {

                WEIGHT_SCORE_FOR_LOADOUT_COST = {									-- weight for weapon cost in mission score calculus (0 .. 1)
            
                    ["Strike"] = 0.3,
                    ["Anti-ship Strike"] = 0.1,
                    ["SEAD"] = 0.1,
                    ["Intercept"] = 0.2,
                    ["CAP"] = 0.4,
                    ["Escort"] = 0.3,
                    ["Fighter Sweep"] = 0.2,
                    ["Reconnaissance"] = 0.1,
                },
            
                WEIGHT_SCORE_FOR_AIRCRAFT_COST = { 								-- weight for aircraft cost in mission score calculus (0 .. 1) 
            
                    ["Fighter"] = 0.3, 
                    ["Attacker"] = 0.5,  
                    ["Bomber"] = 0.2,  
                    ["Transporter"] = 0.1, 
                    ["Reco"] = 0.2, 
                    ["Refueler"] = 0.1,  
                    ["AWACS"] = 0.1, 
                    ["Helicopter"] = 0.2, 
                },
            
                MINIMUM_REQUESTED_AIRCRAFT_FOR_STRIKE = 2,							-- minimum aircraft for strike and anti-ship strike task (default 2 or 3 -needed to survive the anti-aircraft defenses)
                ESCORT_NUMBER_MULTIPLIER = 3,										-- max multiplier for escort number: when more escorts ESCORT_NUMBER_MULTIPLIER times escorts than escorted aircraft, limit escort number to ESCORT_NUMBER_MULTIPLIER times escorted aircraft (default 3)
                MINIMUM_VALUE_OF_AIR_THREAT = 0.5,									-- minimum value of air threat for air unit with self escort capacity (default = 0.5) 	
                FACTOR_FOR_REDUCTION_AIR_THREAT = 0.5,								-- factor for reduction of air threat for air unit with self escort capacity (default = 0.5)
                SCORE_INFLUENCE_ROUTE_THREAT = 1,									-- (min 1) factor for draft_sorties_entry.score = unit_loadouts[l].capability * target.priority / ( route_threat * SCORE_INFLUENCE_ROUTE_THREAT )
                FACTOR_FOR_REDUCE_SCORE = 0.01, 									-- factor for reduce_score in CAP (score = score - reduce_score * factor)
                MULTIPLIER_TARGET_DISTANCE_FOR_EVALUTATION_UNIT_RANGE_LOADOUT = 2,	-- factor for check if target distance is lesser of support.unit.range route.lenght > unit_loadouts[l].minrange * MULTIPLIER_TARGET_DISTANCE_FOR_EVALUTATION_UNIT_RANGE_LOADOUT) (default = 2)
                MULTIPLIER_TARGET_DISTANCE_FOR_EVALUTATION_COMPUTING_ROUTE = 1.5,   -- factor for check if target distance is bigger of unit.loadout.minrange,  computed before intensive route calculations (getRoute) (ToTarget * MULTIPLIER_TARGET_DISTANCE_FOR_EVALUTATION_COMPUTING_ROUTE > unit_loadouts[l].minrange) (default = 1.5)
                MIN_TOTAL_AIR_THREAT_FOR_ESCORT_SUPPORT = 0.5,						-- min total air threat level to authorize support escort flight (default = 0.5)                
                UNIT_SERVICEABILITY = 0.8,											-- serviceability percentage of unit.roster.ready 
                MIN_PERCENTAGE_FOR_ESCORT = 0.75,	    							-- min percentage reduction of avalaible asset request for an escort group (for ammissible strike with escort), default 0.75
                MAX_AIRCRAFT_FOR_INTERCEPT = 2,			    						-- max number of aircraft for an intercept mission 
                MAX_AIRCRAFT_FOR_RECONNAISSANCE = 1, 								-- max number of aircraft for an reconnaisance mission 
                MAX_AIRCRAFT_FOR_STRIKE = 4, 										-- max number of aircraft for an strike mission 
                MAX_AIRCRAFT_FOR_CAP = 4, 											-- max number of aircraft for an cap mission 
                MAX_AIRCRAFT_FOR_ESCORT = 4,		 								-- max number of aircraft for an escort mission 
                MAX_AIRCRAFT_FOR_SWEEP = 4,		 			    					-- max number of aircraft for an sweep mission 
                MAX_AIRCRAFT_FOR_OTHER = 1,		 				    				-- max number of aircraft for other mission 
                --MIN_AIRCRAFT_FOR_OTHER = 1, 										-- min number of aircraft for other mission 
                MAX_AIRCRAFT_FOR_BOMBER = 2,										-- max number of aircraft for bomber                 
            },
             
            ["red"] = {

                WEIGHT_SCORE_FOR_LOADOUT_COST = {									-- weight for weapon cost in mission score calculus (0 .. 1)
            
                    ["Strike"] = 0.3,
                    ["Anti-ship Strike"] = 0.1,
                    ["SEAD"] = 0.1,
                    ["Intercept"] = 0.2,
                    ["CAP"] = 0.4,
                    ["Escort"] = 0.3,
                    ["Fighter Sweep"] = 0.2,
                    ["Reconnaissance"] = 0.1,
                },
            
                WEIGHT_SCORE_FOR_AIRCRAFT_COST = { 								-- weight for aircraft cost in mission score calculus (0 .. 1) 
            
                    ["Fighter"] = 0.3, 
                    ["Attacker"] = 0.5,  
                    ["Bomber"] = 0.2,  
                    ["Transporter"] = 0.1, 
                    ["Reco"] = 0.2, 
                    ["Refueler"] = 0.1,  
                    ["AWACS"] = 0.1, 
                    ["Helicopter"] = 0.2, 
                },
            
                MINIMUM_REQUESTED_AIRCRAFT_FOR_STRIKE = 2,							-- minimum aircraft for strike and anti-ship strike task (default 2 or 3 -needed to survive the anti-aircraft defenses)
                ESCORT_NUMBER_MULTIPLIER = 3,										-- max multiplier for escort number: when more escorts ESCORT_NUMBER_MULTIPLIER times escorts than escorted aircraft, limit escort number to ESCORT_NUMBER_MULTIPLIER times escorted aircraft (default 3)
                MINIMUM_VALUE_OF_AIR_THREAT = 0.5,									-- minimum value of air threat for air unit with self escort capacity (default = 0.5) 	
                FACTOR_FOR_REDUCTION_AIR_THREAT = 0.5,								-- factor for reduction of air threat for air unit with self escort capacity (default = 0.5)
                SCORE_INFLUENCE_ROUTE_THREAT = 1,									-- (min 1) factor for draft_sorties_entry.score = unit_loadouts[l].capability * target.priority / ( route_threat * SCORE_INFLUENCE_ROUTE_THREAT )
                FACTOR_FOR_REDUCE_SCORE = 0.01, 									-- factor for reduce_score in CAP (score = score - reduce_score * factor)
                MIN_TOTAL_AIR_THREAT_FOR_ESCORT_SUPPORT = 0.5,						-- min total air threat level to authorize support escort flight (default = 0.5)
                MULTIPLIER_TARGET_DISTANCE_FOR_EVALUTATION_UNIT_RANGE_LOADOUT = 2,	-- factor for check if target distance is lesser of support.unit.range route.lenght > unit_loadouts[l].minrange * MULTIPLIER_TARGET_DISTANCE_FOR_EVALUTATION_UNIT_RANGE_LOADOUT) (default = 2)
                MULTIPLIER_TARGET_DISTANCE_FOR_EVALUTATION_COMPUTING_ROUTE = 1.5,   -- factor for check if target distance is bigger of unit.loadout.minrange,  computed before intensive route calculations (getRoute) (ToTarget * MULTIPLIER_TARGET_DISTANCE_FOR_EVALUTATION_COMPUTING_ROUTE > unit_loadouts[l].minrange) (default = 1.5)                                
                UNIT_SERVICEABILITY = 0.8,											-- serviceability percentage of unit.roster.ready 
                MIN_PERCENTAGE_FOR_ESCORT = 0.75,									-- min percentage reduction of avalaible asset request for an escort group (for ammissible strike with escort), default 0.75
                MAX_AIRCRAFT_FOR_INTERCEPT = 2,			    						-- max number of aircraft for an intercept mission 
                MAX_AIRCRAFT_FOR_RECONNAISSANCE = 1, 								-- max number of aircraft for an reconnaisance mission 
                MAX_AIRCRAFT_FOR_STRIKE = 4, 										-- max number of aircraft for an strike mission 
                MAX_AIRCRAFT_FOR_CAP = 4, 											-- max number of aircraft for an cap mission 
                MAX_AIRCRAFT_FOR_ESCORT = 4,		 								-- max number of aircraft for an escort mission 
                MAX_AIRCRAFT_FOR_SWEEP = 4,		 								    -- max number of aircraft for an sweep mission 
                MAX_AIRCRAFT_FOR_OTHER = 1,		 								    -- max number of aircraft for other mission 
                --MIN_AIRCRAFT_FOR_OTHER = 1, 										-- min number of aircraft for other mission 
                MAX_AIRCRAFT_FOR_BOMBER = 2,										-- max number of aircraft for bomber                 
            },
		},
    },

	
	
	-- ANY MODIFICATIONS IN THIS FILE NEED TO RESTART ALL THE CAMPAIGN USING FIRSTMISSION.BAT FILE
}
