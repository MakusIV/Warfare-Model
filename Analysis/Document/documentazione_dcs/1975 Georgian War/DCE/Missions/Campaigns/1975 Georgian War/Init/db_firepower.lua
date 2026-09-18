
--To create the Air Tasking Order
--Initiated by Main_NextMission.lua
-------------------------------------------------------------------------------------------------------

if not versionDCE then 
	versionDCE = {} 
end

               -- VERSION --

versionDCE["db_firepower.lua"] = "OB.1.0.0"

-------------------------------------------------------------------------------------------------------
-- Old_Boy rev. OB.1.0.0: first coding 
------------------------------------------------------------------------------------------------------- 

-- Missili A2G nel caloclo della firpower non è utilizzato per non sbilanciare le valutazioni con le bombe e perchè è considerato nella generazione delle missioni. 

-- nato
-- a2a: missile /AIM-54A-MK60/, /AIM-7/, /AIM-7M/, /AIM-7E/, /AIM-9/, /AIM-9M/, /AIM-9P/, /RB-05A viggen/, /RB-74 (AIM-9L) viggen/, /RB-24(aka AIM-9B) - viggen/, /RB-24J(aka AIM-9P3) - viggen/, /R550 mirage/, /R530IR mirage/, /R530EM(super 530!?) mirage/, 
-- bomb: /GBU-12/, GBU-16, GBU-10, /Mk-82/, /Mk-82SE(air)/, /Mk-83/, /Mk-84/, /Mk-20 (cluster)/, /M/71/, /RB-75T/, /CBU-52B/ (cluster), CBU-52 (cluster), /SAMP-21 (400kg)  mirage, , /SAMP-19 (250kg)  mirage,  /SAMP250kgHD/, 
-- rockets: /Zuni-Mk71/, /Hydra-70/, /SNEB256_HE_DEFR mirage/, /SNEB253_HEAT mirage/,
-- a2g missile: AGM-86C(1986 no), /AGM-65D/, /AGM-65K/, /BGM-71D/, /AGM-114 (dal 1982)/
-- a2r missile: /AGM-45/ 
-- a2s missile: RB 15F (dal 1985), /AGM-84A/,

--russia
-- a2a missile: K-13A, R-60M, R-3R, R-3S, R-24T, R-24R, R-40R, R-40T, R-27T(dopo), R-27R(dopo)
-- bomb: FAB-1500, FAB-500, FAB-250, FAB-100, BL-755(cluster? att inglese??), RBK-250(cluster), RBK-500AO(cluster), FAB-500-M62(?), KAB-500L(laser), KMGU-96r(cluster), KMGU-2F/2B(cluster, )
-- rockets: S24-HE-FRAG, S-25, S-13, B-8, UB-13, UB-32, S-5KO, S-8KOM, UPK-23, 9M114, S-24B, UB16UM, S-5M, ORO-57K_S5M_HEFRAG
-- a2g missile: Kh-58, Kh-66, Kh-25ML, Kh-25MR, Kh-29L, Kh-29T, Kh-31A(dopo), Kh-31P(dopo), Kh-35(dopo), Kh-41(dopo), Kh-65(dopo)
-- a2r missile: Kh-25MPU,
-- a2s missile: Kh-22N, Kh-59M (1980), 

-- store weapon info
weapon_db = {	
    
    ["blue"] = {

        ["AIM-54A-MK47"] = {                                    -- weapon name
            ["type"] = "AAM",                                   -- weapon type
            ["seeker"] = "radar",                               -- seeker type (infrared, radar)
            ["task"] = {"A2A"},                                 -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1974,
            ["end_service"] = 2004,
            ["cost"] = 400,-- k$  
            ["tnt"] = 61, --kg
            ["reliability"] = 0.8,                              -- reliability (min 0 - max 1)
            ["range"] = 160,                                    -- km, range ()                  
            ["semiactive_range"] = 130,                         -- km, semiactive range (aircraft must track target)                  
            ["active_range"] = 18,                              -- km, active range  (missile has active autonomous tracking target)                
            ["max_height"] = 24.8,                              -- km max height
            ["max_speed"] = 3.8,                                  -- mach                            
            ["manouvrability"] = 0.6,                           -- manouvrability (min 0 - max 1)
        },

        ["AIM-54A-MK60"] = {                                    -- weapon name
            ["type"] = "AAM",                                   -- weapon type
            ["seeker"] = "radar",                               -- seeker type (infrared, radar)
            ["task"] = {"A2A"},                                 -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1975,
            ["end_service"] = 2004,
            ["cost"] = 400,-- k$  
            ["tnt"] = 61, --kg
            ["reliability"] = 0.8,                              -- reliability (0-1)
            ["range"] = 160,                                    -- km, range ()                  
            ["semiactive_range"] = 130,                         -- km, semiactive range (aircraft must track target)                  
            ["active_range"] = 18,                              -- km, active range  (missile has active autonomous tracking target)                
            ["max_height"] = 24.8 ,                             -- km max height
            ["max_speed"] = 3.8,                                  -- mach                            
            ["manouvrability"] = 0.6,
        },

        ["AIM-54C-MK47"] = {                                             -- weapon name
            ["type"] = "AAM",                                       -- weapon type
            ["seeker"] = "radar",                                -- seeker type (infrared, radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1982, 
            ["end_service"] = 2004,
            ["cost"] = 477,-- k$  
            ["tnt"] = 61, --kg
            ["reliability"] = 0.8,                              -- reliability (0-1)
            ["range"] = 160,                                    -- km, range ()                  
            ["semiactive_range"] = 148,                         -- km, semiactive range (aircraft must track target)                  
            ["active_range"] = 18,                              -- km, active range  (missile has active autonomous tracking target)                
            ["max_height"] = 24.8 ,                             -- km max height
            ["max_speed"] = 4.5,                                  -- mach                             
            ["manouvrability"] = 0.73,
        },

        ["AIM-54C-MK60"] = {                                             -- weapon name
            ["type"] = "AAM",                                       -- weapon type
            ["seeker"] = "radar",                                -- seeker type (infrared, radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1982, 
            ["end_service"] = 2004,
            ["cost"] = 477,-- k$  
            ["tnt"] = 61, --kg
            ["reliability"] = 0.8,                              -- reliability (0-1)
            ["range"] = 160,                                    -- km, range ()                  
            ["semiactive_range"] = 148,                         -- km, semiactive range (aircraft must track target)                  
            ["active_range"] = 18,                              -- km, active range  (missile has active autonomous tracking target)                
            ["max_height"] = 24.8 ,                             -- km max height
            ["max_speed"] = 4.5,                                  -- mach                             
            ["manouvrability"] = 0.73,
        },

        ["AIM-7E"] = {                                             -- weapon name
            ["type"] = "AAM",                                       -- weapon type
            ["seeker"] = "radar",                                -- seeker type (infrared, radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1970,
            ["end_service"] = nil,
            ["cost"] = 125,-- k$  
            ["tnt"] = 40, --kg
            ["reliability"] = 0.8,                              -- reliability (0-1)
            ["range"] = 45,                                     -- km, range (aircraft must track target)                  
            ["semiactive_range"] = 45,                         -- km, semiactive range (aircraft can or not track target)                  
            ["active_range"] = nil,                              -- km, active range  (missile has active autonomous tracking target)                
            ["max_height"] = 18,                                -- km max height
            ["max_speed"] = 3,                                  -- mach                            
            ["manouvrability"] = 0.6,
        },

        ["AIM-7F"] = {                                             -- weapon name
            ["type"] = "AAM",                                       -- weapon type
            ["seeker"] = "radar",                                -- seeker type (infrared, radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1975,
            ["end_service"] = nil,
            ["cost"] = 130,-- k$  
            ["tnt"] = 40, --kg
            ["reliability"] = 0.8,                              -- reliability (0-1)
            ["range"] = 70,                                     -- km, range (aircraft must track target)                  
            ["semiactive_range"] = 70,                         -- km, semiactive range (aircraft can or not track target)                  
            ["active_range"] = nil,                              -- km, active range  (missile has active autonomous tracking target)                
            ["max_height"] = 18,                                -- km max height
            ["max_speed"] = 3,                                  -- mach                            
            ["manouvrability"] = 0.6,
        },

        ["AIM-7M"] = {                                             -- weapon name
            ["type"] = "AAM",                                       -- weapon type
            ["seeker"] = "radar",                                -- seeker type (infrared, radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1982,
            ["end_service"] = nil,
            ["cost"] = 150,-- k$  
            ["tnt"] = 40, --kg
            ["reliability"] = 0.8,                              -- reliability (0-1)
            ["range"] = 70,                                     -- km, range ()                  
            ["semiactive_range"] = 70,                         -- km, semiactive range aircraft must track target)                  
            ["active_range"] = nil,                              -- km, active range  (missile has active autonomous tracking target)                
            ["max_height"] = 18,                                -- km max height
            ["max_speed"] = 3,                                  -- mach                            
            ["manouvrability"] = 0.65,
        },

        ["AIM-7MH"] = {                                             -- weapon name
            ["type"] = "AAM",                                       -- weapon type
            ["seeker"] = "radar",                                -- seeker type (infrared, radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1985,
            ["end_service"] = nil,
            ["cost"] = 160,-- k$  
            ["tnt"] = 40, --kg
            ["reliability"] = 0.8,                              -- reliability (0-1)
            ["range"] = 70,                                     -- km, range ()                  
            ["semiactive_range"] = 70,                         -- km, semiactive range (aircraft must track target))                  
            ["active_range"] = nil,                              -- km, active range  (missile has active autonomous tracking target)                
            ["max_height"] = 18,                                -- km max height
            ["max_speed"] = 3,                                  -- mach                            
            ["manouvrability"] = 0.66,
        },

        ["AIM-7P"] = {                                             -- weapon name
            ["type"] = "AAM",                                       -- weapon type
            ["seeker"] = "radar",                                -- seeker type (infrared, radar)
            ["task"] = {"A2A"},                                 -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1987,
            ["end_service"] = nil,
            ["cost"] = 170,-- k$  
            ["tnt"] = 40, --kg
            ["reliability"] = 0.8,                              -- reliability (0-1)
            ["range"] = 70,                                     -- km, range ()                  
            ["semiactive_range"] = 70,                         -- km, semiactive range (aircraft must track target)                  
            ["active_range"] = nil,                              -- km, active range  (missile has active autonomous tracking target)                
            ["max_height"] = 18,                                -- km max height
            ["max_speed"] = 3,                                  -- mach                            
            ["manouvrability"] = 0.7,
        },

        ["AIM-9B"] = {                                              -- weapon name
            ["type"] = "AAM",                                       -- weapon type            
            ["seeker"] = "infrared",                                -- seeker type (infrared, semiactive_radar, active_radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1956,
            ["end_service"] = nil,
            ["cost"] = 60,-- k$  
            ["tnt"] = 4.5, --kg
            ["reliability"] = 0.5,                              -- reliability (0-1)
            ["range"] = 4.6,                                    -- km, range (aircraft must track target)                              
            ["max_height"] = 18,                                -- km max height
            ["max_speed"] = 1.7,                                  -- mach                            
            ["manouvrability"] = 0.5,
        },

        ["AIM-9P"] = {                                              -- weapon name
            ["type"] = "AAM",                                       -- weapon type            
            ["seeker"] = "infrared",                                -- seeker type (infrared, semiactive_radar, active_radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1975,
            ["end_service"] = nil,
            ["cost"] = 70,-- k$  
            ["tnt"] = 4.5, --kg
            ["reliability"] = 0.6,                              -- reliability (0-1)
            ["range"] = 18.5,                                    -- km, range (aircraft must track target)                              
            ["max_height"] = 18,                                -- km max height
            ["max_speed"] = 2,                                  -- mach                            
            ["manouvrability"] = 0.5,
        },
        
        ["AIM-9P5"] = {                                              -- weapon name
            ["type"] = "AAM",                                       -- weapon type            
            ["seeker"] = "infrared",                                -- seeker type (infrared, semiactive_radar, active_radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1975,
            ["end_service"] = nil,
            ["cost"] = 73,-- k$  
            ["tnt"] = 4.5, --kg
            ["reliability"] = 0.6,                              -- reliability (0-1)
            ["range"] = 18.5,                                    -- km, range (aircraft must track target)                              
            ["max_height"] = 18,                                -- km max height
            ["max_speed"] = 2,                                  -- mach                            
            ["manouvrability"] = 0.6,
        },

        ["AIM-9L"] = {                                              -- weapon name
            ["type"] = "AAM",                                       -- weapon type            
            ["seeker"] = "infrared",                                -- seeker type (infrared, semiactive_radar, active_radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1975, --1977
            ["end_service"] = nil,
            ["cost"] = 75,-- k$  
            ["tnt"] = 9.4, --kg
            ["reliability"] = 0.6,                              -- reliability (0-1)
            ["range"] = 18.5,                                    -- km, range (aircraft must track target)                              
            ["max_height"] = 18,                                -- km max height
            ["max_speed"] = 2.5,                                  -- mach                            
            ["manouvrability"] = 0.7,
        },

        ["AIM-9M"] = {                                              -- weapon name
            ["type"] = "AAM",                                       -- weapon type            
            ["seeker"] = "infrared",                                -- seeker type (infrared, semiactive_radar, active_radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1982,
            ["end_service"] = nil,
            ["cost"] = 80,-- k$  
            ["tnt"] = 9.4, --kg
            ["reliability"] = 0.6,                              -- reliability (0-1)
            ["range"] = 18.5,                                    -- km, range (aircraft must track target)                              
            ["max_height"] = 18,                                -- km max height
            ["max_speed"] = 2.5,                                  -- mach                            
            ["manouvrability"] = 0.7,
        },

        ["AIM-9X"] = {                                              -- weapon name
            ["type"] = "AAM",                                       -- weapon type            
            ["seeker"] = "infrared",                                -- seeker type (infrared, semiactive_radar, active_radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 2003,
            ["end_service"] = nil,
            ["cost"] = 100,-- k$  
            ["tnt"] = 9.4, --kg
            ["reliability"] = 0.6,                              -- reliability (0-1)
            ["range"] = 37,                                    -- km, range (aircraft must track target)                              
            ["max_height"] = 25,                                -- km max height
            ["max_speed"] = 2.9,                                  -- mach                            
            ["manouvrability"] = 0.9,
        },

        ["R-550"] = {  -- R-550 Magic Mirage                                -- weapon name
            ["type"] = "AAM",                                       -- weapon type            
            ["seeker"] = "infrared",                                -- seeker type (infrared, semiactive_radar, active_radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1975,
            ["end_service"] = nil,
            ["cost"] = 27.5,-- k$  
            ["tnt"] = 12.5, --kg
            ["reliability"] = 0.6,                              -- reliability (0-1)
            ["range"] = 10,                                    -- km, range (aircraft must track target)                                          
            ["max_height"] = 18,                                -- km max height
            ["max_speed"] = 2.8,                                  -- mach                            
            ["manouvrability"] = 0.6,
        },

        ["R-530IR"] = { -- R-530 Magic Mirage                                  -- weapon name
            ["type"] = "AAM",                                       -- weapon type
            ["seeker"] = "infrared",                                -- seeker type (infrared, radar)
            ["task"] = {"A2A"},                                 -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1975,
            ["end_service"] = nil,
            ["cost"] = 157,-- k$  
            ["tnt"] = 27, --kg
            ["reliability"] = 0.6,                              -- reliability (0-1)
            ["range"] = 18,                                     -- km, range (aircraft must track target)                              
            ["max_height"] = 18,                                -- km max height
            ["max_speed"] = 3,                                  -- mach                            
            ["manouvrability"] = 0.6,
        },

        ["R-530EM"] = { -- R-530 Magic Mirage                                  -- weapon name
            ["type"] = "AAM",                                       -- weapon type
            ["seeker"] = "radar",                                -- seeker type (infrared, radar)
            ["task"] = {"A2A"},                                 -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1975, --1980,
            ["end_service"] = nil,
            ["cost"] = 157,-- k$  
            ["tnt"] = 30, --kg
            ["reliability"] = 0.7,                              -- reliability (0-1)
            ["range"] = 40,                                     -- km, range (aircraft must track target)                  
            ["semiactive_range"] = 40,                         -- km, semiactive range (aircraft must track target)                             
            ["max_height"] = 20,                                -- km max height
            ["max_speed"] = 4,                                  -- mach                            
            ["manouvrability"] = 0.7,
        },

        ["RB-24"] = {-- aka AIM-9B   Viggen                               -- weapon name
            ["type"] = "AAM",                                       -- weapon type            
            ["seeker"] = "infrared",                                -- seeker type (infrared, semiactive_radar, active_radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1956,
            ["end_service"] = nil,
            ["cost"] = 60,-- k$  
            ["tnt"] = 4.5, --kg
            ["reliability"] = 0.5,                              -- reliability (0-1)
            ["range"] = 4.6,                                    -- km, range (aircraft must track target)                              
            ["max_height"] = 18,                                -- km max height
            ["max_speed"] = 1.7,                                  -- mach                            
            ["manouvrability"] = 0.5,
        },

        ["RB-24J"] = {-- aka AIM-9P3   Viggen                               -- weapon name
            ["type"] = "AAM",                                       -- weapon type            
            ["seeker"] = "infrared",                                -- seeker type (infrared, semiactive_radar, active_radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1975,
            ["end_service"] = nil,
            ["cost"] = 75,-- k$  
            ["tnt"] = 4.5, --kg
            ["reliability"] = 0.6,                              -- reliability (0-1)
            ["range"] = 18.5,                                    -- km, range (aircraft must track target)                              
            ["max_height"] = 18,                                -- km max height
            ["max_speed"] = 2,                                  -- mach                            
            ["manouvrability"] = 0.6,
        },

        ["RB-74"] = {-- aka AIM-9L                                              -- weapon name
            ["type"] = "AAM",                                       -- weapon type            
            ["seeker"] = "infrared",                                -- seeker type (infrared, semiactive_radar, active_radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1975, --1977
            ["end_service"] = nil,
            ["cost"] = 73,-- k$  
            ["tnt"] = 9.4, --kg
            ["reliability"] = 0.6,                              -- reliability (0-1)
            ["range"] = 18.5,                                    -- km, range (aircraft must track target)                              
            ["max_height"] = 18,                                -- km max height
            ["max_speed"] = 2.5,                                  -- mach                            
            ["manouvrability"] = 0.7,
        },

        ["RB-05A"] = {        --a2g and limited a2a                               -- weapon name
            ["type"] = "ASM",                                       -- weapon type            
            ["seeker"] = "electro-optical",                    -- seeker type (infrared, semiactive_radar, active_radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1972, 
            ["end_service"] = 2005,
            ["cost"] = 180,-- k$  
            ["tnt"] = 160, --kg
            ["reliability"] = 0.5,                              -- reliability (0-1)
            ["range"] = 9,                                    -- km, range (aircraft must track target)                              
            ["max_height"] = 18,                                -- km max height
            ["max_speed"] = 1,                                  -- mach                            
            ["manouvrability"] = 0.4,
        },

        ["RB-15F"] = {                                             -- weapon name
            ["type"] = "ASM",                                       -- weapon type
            ["task"] = {"Anti-ship Strike"},                        -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1985,
            ["end_service"] = nil,
            ["cost"] = 720,-- k$  
            ["tnt"] = 220, --kg
            ["range"] = 75, -- Km
            ["perc_efficiency_variability"] = 0.1,                  -- efficiecy variability(0-1): firepower_max = firepower_max * ( 1 + perc_efficiency_variability )
            ["efficiency"] = {                                      -- efficiency attribute table
                
                ["ship"] = {                                        -- attribute
                    ["big"] = {                                     -- element dimension (big, medium, small, mix)
                        ["accuracy"] = 1,                           -- accuracy: hit success probability percentage, 1 max, 0.1 min
                        ["destroy_capacity"] = 0.6,                 -- destroy_capacity: number of destroyed single element ( element destroyed with single hit),  0.1 min
                    },
                    ["med"] = {
                        ["accuracy"] = 1,  
                        ["destroy_capacity"] = 0.8,
                    },
                    ["small"] = {
                        ["accuracy"] = 1,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.85,
                    },
                },        
            },                              
        },

        ["AGM-45"] = {                                             -- weapon name
            ["type"] = "ASM",                                       -- weapon type
            ["task"] = {"SEAD"},                        -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1966,
            ["end_service"] = 1992,
            ["cost"] = 32,-- k$  
            ["tnt"] = 66, --kg
            ["range"] = 10, -- Km
            ["perc_efficiency_variability"] = 0.2,                  -- efficiecy variability(0-1): firepower_max = firepower_max * ( 1 + perc_efficiency_variability )
            ["efficiency"] = {                                      -- efficiency attribute table
                
                ["SAM"] = {                                        -- attribute                    
                    ["big"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.7,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.8,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.8,
                    },
                },        
            },                              
        },

        ["AGM-84A"] = {                                             -- weapon name
            ["type"] = "ASM",                                       -- weapon type
            ["task"] = {"Anti-ship Strike"},                        -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1970,
            ["end_service"] = nil,
            ["cost"] = 720,-- k$  
            ["tnt"] = 221, --kg
            ["range"] = 50, -- Km
            ["perc_efficiency_variability"] = 0.1,                  -- efficiecy variability(0-1): firepower_max = firepower_max * ( 1 + perc_efficiency_variability )
            ["efficiency"] = {                                      -- efficiency attribute table
                
                ["ship"] = {                                        -- attribute
                    ["big"] = {                                     -- element dimension (big, medium, small, mix)
                        ["accuracy"] = 1,                           -- accuracy: hit success probability percentage, 1 max, 0.1 min
                        ["destroy_capacity"] = 0.6,                 -- destroy_capacity: number of destroyed single element ( element destroyed with single hit),  0.1 min
                    },
                    ["med"] = {
                        ["accuracy"] = 1,  
                        ["destroy_capacity"] = 0.8,
                    },
                    ["small"] = {
                        ["accuracy"] = 1,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.85,
                    },
                },        
            },                              
        },

        ["AGM-88"] = {                                             -- weapon name
            ["type"] = "ASM",                                       -- weapon type
            ["task"] = {"SEAD"},                        -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1966,
            ["end_service"] = 1992,
            ["cost"] = 200,-- k$  
            ["tnt"] = 88, --kg
            ["range"] = 80, -- Km
            ["perc_efficiency_variability"] = 0.2,                  -- efficiecy variability(0-1): firepower_max = firepower_max * ( 1 + perc_efficiency_variability )
            ["efficiency"] = {                                      -- efficiency attribute table
                
                ["SAM"] = {                                        -- attribute                    
                    ["big"] = {
                        ["accuracy"] = 0.8,  
                        ["destroy_capacity"] = 0.77,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.88,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.85,
                    },
                },        
            },                              
        },

        ["Kormoran"] = {                                             -- weapon name
            ["type"] = "ASM",                                       -- weapon type
            ["task"] = {"Anti-ship Strike"},                        -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1973,
            ["end_service"] = nil,
            ["cost"] = 200,-- k$  
            ["tnt"] = 165, --kg
            ["range"] = 30, -- Km
            ["perc_efficiency_variability"] = 0.1,                  -- efficiecy variability(0-1): firepower_max = firepower_max * ( 1 + perc_efficiency_variability )
            ["efficiency"] = {                                      -- efficiency attribute table
                
                ["ship"] = {                                        -- attribute
                    ["big"] = {                                     -- element dimension (big, medium, small, mix)
                        ["accuracy"] = 1,                           -- accuracy: hit success probability percentage, 1 max, 0.1 min
                        ["destroy_capacity"] = 0.45,                 -- destroy_capacity: number of destroyed single element ( element destroyed with single hit),  0.1 min
                    },
                    ["med"] = {
                        ["accuracy"] = 1,  
                        ["destroy_capacity"] = 0.7,
                    },
                    ["small"] = {
                        ["accuracy"] = 1,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.70,
                    },
                },        
            },                              
        },

        ["RB-05E"] = { -- ROBOT 05 RB-05E  Viggen electro optical
            ["type"] = "ASM",       
            ["task"] = {"Anti-ship Strike", "Strike", "SEAD"},
            ["start_service"] = 1972,
            ["end_service"] = 2005,
            ["cost"] = 300,-- k$  
            ["tnt"] = 160, --kg
            ["range"] = 9, --Km
            ["perc_efficiency_variability"] = 0.2, -- efficiency variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 0.6,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.8,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.68, 
                        ["destroy_capacity"] = 0.8,
                    },
                },   
                
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 0.9,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.75,  
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.95,
                    },
                },

                ["armor"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.9,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.9,
                    },
                },   

                ["Parked Aircraft"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 1,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 1,
                    },
                },

                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 0.8, -- element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.9,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 1,
                    },
                }, 
            },                              
        },

        ["RB-04E"] = { -- ROBOT 05 RB-05E  antiship Viggen radar 
            ["type"] = "ASM",       
            ["task"] = {"Anti-ship Strike"},
            ["start_service"] = 1975,
            ["end_service"] = 2000,
            ["cost"] = 700,-- k$  
            ["tnt"] = 300, --kg
            ["range"] = 32, --Km
            ["perc_efficiency_variability"] = 0.1, -- efficiency variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 0.9,   -- 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.8,  
                        ["destroy_capacity"] = 0.9,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.94,
                    },
                },                                   
            },                              
        },

        ["Sea Eagle"] = { -- ROBOT 05 RB-05E  antiship Viggen radar 
            ["type"] = "ASM",       
            ["task"] = {"Anti-ship Strike"},
            ["start_service"] = 1985,
            ["end_service"] = nil,
            ["cost"] = 700,-- k$  
            ["tnt"] = 230, --kg
            ["range"] = 100, --Km
            ["perc_efficiency_variability"] = 0.1, -- efficiency variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 0.9,   -- 
                        ["destroy_capacity"] = 0.6,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.8,  
                        ["destroy_capacity"] = 0.7,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 0.8,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.8,
                    },
                },                                   
            },                              
        },

        ["RB-75T"] = { -- ROBOT 05 RB-75T aka AGM-65D Viggen electro optical
            ["type"] = "ASM",       
            ["task"] = {"Anti-ship Strike", "Strike", "SEAD"},
            ["start_service"] = 1972,
            ["end_service"] = nil,
            ["cost"] = 160,-- k$  
            ["tnt"] = 52, --kg
            ["range"] = 15, -- Km
            ["perc_efficiency_variability"] = 0.05, -- efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 1,   -- 
                        ["destroy_capacity"] = 0.6,
                    },
                    ["med"] = {
                        ["accuracy"] = 1,  
                        ["destroy_capacity"] = 0.8,
                    },
                    ["small"] = {
                        ["accuracy"] = 1,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.85,
                    },
                },   
                
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 1,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.8,  
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 1,
                    },
                },

                ["armor"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.8,  
                        ["destroy_capacity"] = 0.9,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 1,
                    },
                },   

                ["Parked Aircraft"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 1,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.8,  
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 1,
                    },
                },

                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 1, -- element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 1,
                    },
                }, 
            },                          
        },

        ["RB-15"] = { -- ROBOT 15 antiship Viggen                   -- weapon name
            ["type"] = "ASM",                                       -- weapon type
            ["task"] = {"Anti-ship Strike"},                        -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1989,
            ["end_service"] = nil,
            ["cost"] = 350,-- k$  
            ["tnt"] = 200, --kg
            ["range"] = 70, -- Km
            ["perc_efficiency_variability"] = 0.05,                  -- efficiecy variability(0-1): firepower_max = firepower_max * ( 1 + perc_efficiency_variability )
            ["efficiency"] = {                                      -- efficiency attribute table
                
                ["ship"] = {                                        -- attribute
                    ["big"] = {                                     -- element dimension (big, medium, small, mix)
                        ["accuracy"] = 1,                           -- accuracy: hit success probability percentage, 1 max, 0.1 min
                        ["destroy_capacity"] = 0.6,                 -- destroy_capacity: number of destroyed single element ( element destroyed with single hit),  0.1 min
                    },
                    ["med"] = {
                        ["accuracy"] = 1,  
                        ["destroy_capacity"] = 0.8,
                    },
                    ["small"] = {
                        ["accuracy"] = 1,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.85,
                    },
                },        
            },                              
        },

        ["AGM-65D"] = { -- infrared
            ["type"] = "ASM",       
            ["task"] = {"Anti-ship Strike", "Strike", "SEAD"},
            ["start_service"] = 1967,
            ["end_service"] = nil,
            ["cost"] = 160,-- k$  
            ["tnt"] = 52, --kg
            ["range"] = 15, -- Km
            ["perc_efficiency_variability"] = 0.05, -- efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 1,   -- 
                        ["destroy_capacity"] = 0.6,
                    },
                    ["med"] = {
                        ["accuracy"] = 1,  
                        ["destroy_capacity"] = 0.8,
                    },
                    ["small"] = {
                        ["accuracy"] = 1,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.85,
                    },
                },   
                
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 1,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.8,  
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 1,
                    },
                },

                ["armor"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.8,  
                        ["destroy_capacity"] = 0.9,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 1,
                    },
                },   

                ["Parked Aircraft"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 1,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.8,  
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 1,
                    },
                },

                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 1, -- element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 1,
                    },
                }, 
            },                              
        },

        ["AGM-65K"] = { -- electro - optic
            ["type"] = "ASM",       
            ["task"] = {"Anti-ship Strike", "Strike", "SEAD"},
            ["start_service"] = 1970,
            ["end_service"] = nil,
            ["cost"] = 160,-- k$  
            ["tnt"] = 52, --kg
            ["range"] = 15, -- Km
            ["perc_efficiency_variability"] = 0.05, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 1,   -- 
                        ["destroy_capacity"] = 0.6,
                    },
                    ["med"] = {
                        ["accuracy"] = 1,  
                        ["destroy_capacity"] = 0.8,
                    },
                    ["small"] = {
                        ["accuracy"] = 1,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.85,
                    },
                },   
                
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 1,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.8,  
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 1,
                    },
                },

                ["armor"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.8,  
                        ["destroy_capacity"] = 0.9,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 1,
                    },
                },   

                ["Parked Aircraft"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 1,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.8,  
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 1,
                    },
                },

                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 1, -- element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 1,
                    },
                }, 
            },                              
        },

        ["AGM-114"] = { -- laser
            ["type"] = "ASM",       
            ["task"] = {"Strike", "SEAD", "Anti-ship Strike"},
            ["start_service"] = 1984,
            ["end_service"] = nil,
            ["cost"] = 80,-- k$  
            ["tnt"] = 9, --kg
            ["range"] = 8, -- Km
            ["perc_efficiency_variability"] = 0.05, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                               
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 1,   -- 
                        ["destroy_capacity"] = 0.5,
                    },
                    ["med"] = {
                        ["accuracy"] = 1,  
                        ["destroy_capacity"] = 0.6,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9,   
                        ["destroy_capacity"] = 0.7,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.6,
                    },
                },

                ["armor"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 1,   -- 
                        ["destroy_capacity"] = 0.4,
                    },
                    ["med"] = {
                        ["accuracy"] = 1,  
                        ["destroy_capacity"] = 0.5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9,   
                        ["destroy_capacity"] = 0.6,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.5,
                    },
                },                   

                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 0.6, -- element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.7,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["mix"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.7,
                    },
                }, 
            },                              
        },

        ["BGM-71D"] = { -- antitank missile
            ["type"] = "ASM",       
            ["task"] = {"Strike", "SEAD"},
            ["start_service"] = 1970,
            ["end_service"] = nil,
            ["cost"] = 12,-- k$  
            ["tnt"] = 6.14, --kg
            ["range"] = 3, -- Km
            ["perc_efficiency_variability"] = 0.05, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                               
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 1,   -- 
                        ["destroy_capacity"] = 1,
                    },
                    ["med"] = {
                        ["accuracy"] = 1,  
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 1,
                    },
                },

                ["armor"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 1,   -- 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["med"] = {
                        ["accuracy"] = 1,  
                        ["destroy_capacity"] = 0.9,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.95,
                    },
                },                   

                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   -- 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["med"] = {
                        ["accuracy"] = 1,  
                        ["destroy_capacity"] = 0.9,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.95,
                    },
                }, 
            },                              
        },
    
        ["Mk-84"] = {
            ["type"] = "Bombs",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1950,
            ["end_service"] = nil,
            ["cost"] = 4.4,-- k$  
            ["tnt"] = 429, --kg
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 0.8, -- 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.9,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.85,
                    },
                },                
            
                ["Bridge"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   
                        ["destroy_capacity"] = 0.7,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.9,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.8,
                    },
                },        

                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 0.5,   -- 
                        ["destroy_capacity"] = 0.85,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.4,  
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.2,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.3, 
                        ["destroy_capacity"] = 0.8,
                    },
                },
                
                ["soft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["med"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.85,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.95,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.85,
                    },
                },                

                ["Parked Aircraft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 1,
                    },
                },                

                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["med"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.85,
                    },
                }, 
                
                ["armor"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                

                    ["med"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.85,
                    },
                }, 
            },                              
        },

        ["Mk-83"] = {
            ["type"] = "Bombs",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1950,
            ["end_service"] = nil,
            ["cost"] = 3.3,--?? k$  
            ["tnt"] = 202, --kg
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 0.4, -- 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.45,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.42,
                    },
                },                
            
                ["Bridge"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   
                        ["destroy_capacity"] = 0.35,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.45,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.4,
                    },
                },        

                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.42,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.5,  
                        ["destroy_capacity"] = 0.5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.3,   
                        ["destroy_capacity"] = 0.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.5, 
                        ["destroy_capacity"] = 0.4,
                    },
                },        

                ["soft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.95,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.95,
                    },
                },    
                
                ["armor"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["big"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.95,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.98,
                    },
                },  

                ["Parked Aircraft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["med"] = {
                        ["accuracy"] = 0.93, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.83, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.93, 
                        ["destroy_capacity"] = 1,
                    },
                },                

                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["big"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.95,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.98,
                    },
                },    
            },                              
        },

        ["Mk-82"] = {
            ["type"] = "Bombs",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1950,
            ["end_service"] = nil,
            ["cost"] = 2.7,-- k$  
            ["tnt"] = 92, --kg
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 0.13, -- 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },

                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.21,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.52,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.21,
                    },
                },      
                
                ["Bridge"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    
                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.21,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.31,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.27,
                    },
                },   
                            
                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.21,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.5,  
                        ["destroy_capacity"] = 0.25,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.3,   
                        ["destroy_capacity"] = 0.33,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.4, 
                        ["destroy_capacity"] = 0.3,
                    },
                },        

                ["soft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["med"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.85,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.95,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.9,
                    },
                },                

                ["Parked Aircraft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.94,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.87, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.77, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 1,
                    },  
                },              

                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.69,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.74,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.79,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.74,
                    },
                }, 
                
                ["armor"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.39,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.44,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.49,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.44,
                    },
                },
            },
        },

        ["Mk-82AIR"] = { -- verificare se sigla Mk-82SE
            ["type"] = "Bombs",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1950,
            ["end_service"] = nil,
            ["cost"] = 4,-- k$  
            ["tnt"] = 92, --kg
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 0.13, -- 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },

                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.21,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.52,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.21,
                    },
                },      
                
                ["Bridge"] = {-- fixed target (guided bombs and agm missile are more efficiency)
                    
                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.21,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.31,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.27,
                    },
                },   
                            
                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.21,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.5,  
                        ["destroy_capacity"] = 0.25,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.3,   
                        ["destroy_capacity"] = 0.33,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.4, 
                        ["destroy_capacity"] = 0.3,
                    },
                },        

                ["soft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["med"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.85,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.95,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.9,
                    },
                },                

                ["Parked Aircraft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.94,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.87, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.77, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 1,
                    },                
                },                

                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.69,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.74,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.79,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.74,
                    },
                }, 
                
                ["armor"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.39,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.44,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.49,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.44,
                    },
                },
            },                              
        },

        ["GBU-10"] = {
            ["type"] = "Guided bombs",
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1980,
            ["end_service"] = nil,
            ["cost"] = 27,-- k$  
            ["tnt"] = 428, --kg
            ["perc_efficiency_variability"] = 0.05, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 0.8, -- 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.9,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.85,
                    },
                },                
            
                ["Bridge"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   
                        ["destroy_capacity"] = 0.7,
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.9,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.8,
                    },
                },        

                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity "] = 0.85,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.4,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.5, 
                        ["destroy_capacity"] = 0.8,
                    },
                },        
            },                  
        },
    
        ["GBU-16"] = {  -- like Mk-83
            ["type"] = "Guided bombs",
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1970,
            ["end_service"] = nil,
            ["cost"] = 25,-- k$  
            ["tnt"] = 202, --kg
            ["perc_efficiency_variability"] = 0.05, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 0.4, -- 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.45,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.42,
                    },
                },                
            
                ["Bridge"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   
                        ["destroy_capacity"] = 0.35,
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.45,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.4,
                    },
                },        

                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 0.42,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.4,
                    },
                },        
            },                  
        },

        ["GBU-12"] = {
            ["type"] = "Guided bombs",
            ["task"] = {"Strike"},
            ["start_service"] = 1970,
            ["end_service"] = nil,
            ["cost"] = 22,-- k$  
            ["tnt"] = 90, --kg
            ["perc_efficiency_variability"] = 0.05, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                   
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.21,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.25,
                    },
                    ["mix"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.21,
                    },
                },                 

                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 0.21,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.25,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.25,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.2,
                    },
                },        
            },                   
        },

        ["GBU-24"] = {  -- like Mk-84
            ["type"] = "Guided bombs",
            ["task"] = {"Strike"},
            ["start_service"] = 1983,
            ["end_service"] = nil,
            ["cost"] = 55,-- k$  
            ["tnt"] = 429, --kg
            ["perc_efficiency_variability"] = 0.05, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 0.8, -- 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.9,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.85,
                    },
                },                
            
                ["Bridge"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   
                        ["destroy_capacity"] = 0.7,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.9,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.8,
                    },
                },        

                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 0.5,   -- 
                        ["destroy_capacity"] = 0.85,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.4,  
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.2,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.3, 
                        ["destroy_capacity"] = 0.8,
                    },
                },
            },                    
        },

        ["GBU-27"] = { -- bunker
            ["type"] = "Guided bombs",
            ["task"] = {"Strike"},
            ["start_service"] = 1985,
            ["end_service"] = nil,
            ["cost"] = 55,-- k$  
            ["tnt"] = 429, --kg
            ["perc_efficiency_variability"] = 0.05, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 0.8, -- 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.9,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.85,
                    },
                },                
            
                ["Bridge"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   
                        ["destroy_capacity"] = 0.7,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.9,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.8,
                    },
                },        

                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 0.5,   -- 
                        ["destroy_capacity"] = 0.85,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.4,  
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.2,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.3, 
                        ["destroy_capacity"] = 0.8,
                    },
                },
            },                   
        },
            
        ["Mk-20"] = {  --aka CBU-100 anti-armor cluster
            ["type"] = "Cluster bombs",
            ["task"] = {"Strike"},	
            ["start_service"] = 1970,
            ["end_service"] = nil,
            ["cost"] = 15,-- k$  
            ["weight"] = 222, --kg
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.75,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 2, -- element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 7,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.67, 
                        ["destroy_capacity"] = 6,
                    },
                },                
            
                ["Parked Aircraft"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.75,   
                        ["destroy_capacity"] = 3,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 7,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.67, 
                        ["destroy_capacity"] = 6,
                    },
                },        

                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.75,   -- 
                        ["destroy_capacity"] = 3,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65,   
                        ["destroy_capacity"] = 7,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.67, 
                        ["destroy_capacity"] = 6,
                    },
                },

                ["armor"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.75,   -- 
                        ["destroy_capacity"] = 3,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65,   
                        ["destroy_capacity"] = 7,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.67, 
                        ["destroy_capacity"] = 6,
                    },
                },    
            },                  
        },

        ["BLG66"] = {  --aka Belouga cluster soft target
            ["type"] = "Cluster bombs",
            ["task"] = {"Strike"},	
            ["start_service"] = 1980,
            ["end_service"] = nil,
            ["cost"] = 15,-- k$  
            ["weight"] = 305, --kg
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.75,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 2.1, -- element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 3.2,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 4.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 4,
                    },
                },                              
            
                ["Parked Aircraft"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.75,   
                        ["destroy_capacity"] = 3.2,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 4.5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 6.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.67, 
                        ["destroy_capacity"] = 5,
                    },
                },        

                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 2.7,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 4.5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 6.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 5.5,
                    },
                },   
                
                ["armor"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.75,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 1, -- element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 1.5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 2,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 1.5,
                    },
                },              
            },                  
        },

        ["CBU-52B"] = {  --aka cluster soft target
            ["type"] = "Cluster bombs",
            ["task"] = {"Strike"},	
            ["start_service"] = 1970,
            ["end_service"] = nil,
            ["cost"] = 17,-- k$  
            ["weight"] = 347, --kg
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.75,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 2.5, -- element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 3.7,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 4.4,
                    },
                },                              
            
                ["Parked Aircraft"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.75,   
                        ["destroy_capacity"] = 3.7,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 7,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.67, 
                        ["destroy_capacity"] = 5.5,
                    },
                },        

                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 3,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 7,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 6,
                    },
                },                
            },                  
        },

        ["BK-90MJ1"] = {  --aka DWS 39 Mjölner MJ1 soft target, mj2 anti-armor, mj1+2 both,  cluster bomb
            ["type"] = "Cluster bombs",
            ["task"] = {"Strike"},	
            ["start_service"] = 1990,
            ["end_service"] = nil,
            ["cost"] = 15,-- k$  
            ["weight"] = nil, --kg
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = { 
                
                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 2, -- element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5, 
                        ["destroy_capacity"] = 4,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 3,
                    },
                },        
                
                ["armor"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 2, -- element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5, 
                        ["destroy_capacity"] = 4,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 3,
                    },
                },       
            
                ["Parked Aircraft"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 3,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5, 
                        ["destroy_capacity"] = 5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 4,
                    },
                },        

                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 3,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 7,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 6,
                    },
                },                
            },                  
        },

        ["BK-90MJ1-2"] = {  --aka DWS 39 Mjölner MJ1 soft target, mj2 anti-armor, mj1+2 both,  cluster bomb
            ["type"] = "Cluster bombs",
            ["task"] = {"Strike"},	
            ["start_service"] = 1990,
            ["end_service"] = nil,
            ["cost"] = 15,-- k$  
            ["weight"] = nil, --kg
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = { 
                
                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 2, -- element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5, 
                        ["destroy_capacity"] = 4,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 3,
                    },
                },        
                
                ["armor"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 3, -- element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5, 
                        ["destroy_capacity"] = 5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 4,
                    },
                },       
            
                ["Parked Aircraft"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 3,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5, 
                        ["destroy_capacity"] = 5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 4,
                    },
                },        

                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 3,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 7,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 6,
                    },
                },                
            },                  
        },

        ["BK-90MJ2"] = {  --aka DWS 39 Mjölner MJ1 soft target, mj2 anti-armor, mj1+2 both,  cluster bomb
            ["type"] = "Cluster bombs",
            ["task"] = {"Strike"},	
            ["start_service"] = 1990,
            ["end_service"] = nil,
            ["cost"] = 15,-- k$  
            ["weight"] = nil, --kg
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = { 
                
                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 2, -- element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5, 
                        ["destroy_capacity"] = 4,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 3,
                    },
                },        
                
                ["armor"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 3, -- element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5, 
                        ["destroy_capacity"] = 5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 4,
                    },
                },       
            
                ["Parked Aircraft"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 3,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5, 
                        ["destroy_capacity"] = 5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 4,
                    },
                },        

                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 3,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 7,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 6,
                    },
                },                
            },                  
        },

        ["M/71"] = { -- HE Framegtation bombs for AJS37 Viggen
            ["type"] = "Bombs",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1970,
            ["end_service"] = nil,
            ["cost"] = 2,-- k$  
            ["tnt"] = 40, --kg
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                                   
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.3,
                    },                   
                },                            
                
                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.07,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.5,  
                        ["destroy_capacity"] = 0.12,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.3,   
                        ["destroy_capacity"] = 0.25,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.5, 
                        ["destroy_capacity"] = 0.2,
                    },
                },    
                
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 0.9,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.8,  
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 1,
                    },
                },

                ["armor"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 0.2,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.8,  
                        ["destroy_capacity"] = 0.4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 0.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.45,
                    },
                },   

                ["Parked Aircraft"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 1,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.8,  
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 1,
                    },
                },
            },                              
        },

        ["SAMP-400LD"] = {-- SAMP-21 400 kg   (Mk-83)
            ["type"] = "Bombs",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1950,
            ["end_service"] = nil,
            ["cost"] = 3.3,-- k$  
            ["tnt"] = 202, --kg
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 0.4, -- 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.45,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.42,
                    },
                },                
            
                ["Bridge"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   
                        ["destroy_capacity"] = 0.35,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.45,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.4,
                    },
                },        

                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.42,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.5,  
                        ["destroy_capacity"] = 0.5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.3,   
                        ["destroy_capacity"] = 0.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.5, 
                        ["destroy_capacity"] = 0.4,
                    },
                },        

                ["soft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.95,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.95,
                    },
                },                

                ["Parked Aircraft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["med"] = {
                        ["accuracy"] = 0.93, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.83, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.93, 
                        ["destroy_capacity"] = 1,
                    },
                },                

                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["med"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.75,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.9,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.75,
                    },
                },    
            },                              
        },

        ["SAMP-250HD"] = { -- SAMP-19 250 kg  (Mk-82)
            ["type"] = "Bombs",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1950,
            ["end_service"] = nil,
            ["cost"] = 2.7,-- k$  
            ["tnt"] = 92, --kg
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.21,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.52,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.21,
                    },
                },                
                            
                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.21,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.5,  
                        ["destroy_capacity"] = 0.25,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.3,   
                        ["destroy_capacity"] = 0.25,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.5, 
                        ["destroy_capacity"] = 0.2,
                    },
                },        

                ["soft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["med"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.7,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.7,
                    },
                },                

                ["Parked Aircraft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.9,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.85,
                    },
                },                

                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["med"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.65,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.65,
                    },
                },                
            },                              
        },

        ["Zuni-Mk71"] = { -- Rockets 127 mm soft target
            ["type"] = "Rockets",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1956,
            ["end_service"] = nil,
            ["cost"] = 0.4,-- k$  
            ["tnt"] = 6.8, --kg
            ["range"] = 8, -- Km
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  -- for single rocket
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                                   
                    ["small"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 0.15,
                    },                   
                },                
                            
                ["ship"] = { -- mobile target
                    
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.12,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.12,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 0.1,
                    },
                },    
                
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.4,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.6,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.55, 
                        ["destroy_capacity"] = 0.5,
                    },
                },

                ["armor"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.3,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.6,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.55, 
                        ["destroy_capacity"] = 0.5,
                    },
                },   

                ["Parked Aircraft"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.3,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacit"] = 0.5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.6,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.55, 
                        ["destroy_capacity"] = 0.55,
                    },
                },
            },                              
        },        

        ["Hydra-70MK5"] = { -- Rockets 70 mm Mk-5 hard target
            ["type"] = "Rockets",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1956,
            ["end_service"] = nil,
            ["cost"] = 2.8,-- k$  
            ["tnt"] = 6.2, --kg ?? (not applicable?)
            ["range"] = 8, -- Km
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                                   
                    ["small"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.15,
                    },                   
                },                
                            
                ["ship"] = { -- mobile target
                    
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 0.15,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 0.1,
                    },
                },    
                
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.3,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.6,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 0.5,
                    },
                },

                ["armor"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.2,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.4,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 0.35,
                    },
                },   

                ["Parked Aircraft"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.4,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacit"] = 0.5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.6,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.55, 
                        ["destroy_capacity"] = 0.55,
                    },
                },
            },                              
        },     
        
        ["Hydra-70MK1"] = { -- Rockets 70 mm  Mk-1 soft target
            ["type"] = "Rockets",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1956,
            ["end_service"] = nil,
            ["cost"] = 2.8,-- k$  
            ["tnt"] = 6.2, --kg ?? (not applicable?)
            ["range"] = 8, -- Km
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                                
                    ["small"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.08,
                    },                   
                },                
                            
                ["ship"] = { -- mobile target
                    
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.08,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 0.1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 0.1,
                    },
                },    
                
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.3,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.6,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.55, 
                        ["destroy_capacity"] = 0.5,
                    },
                },

                ["Parked Aircraft"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.1,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacit"] = 0.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.4,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.55, 
                        ["destroy_capacity"] = 0.35,
                    },
                },
            },                              
        },  

        ["SNEB-256"] = { -- Rockets 68 mm HE_DEFR , 
            ["type"] = "Rockets",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1955,
            ["end_service"] = nil,
            ["cost"] = 2.5,-- k$  
            ["tnt"] = 6.8, --kg ???
            ["range"] = 8, -- Km ??
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                                   
                    ["small"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 0.15,
                    },  
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 0.15,
                    },                 
                },                
                            
                ["ship"] = { -- mobile target
                    
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.12,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 0.2,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 0.15,
                    },
                },    
                
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.3,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.55, 
                        ["destroy_capacity"] = 0.55,
                    },
                },

                ["armor"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.2,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.4,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.55, 
                        ["destroy_capacity"] = 0.35,
                    },
                },   

                ["Parked Aircraft"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.4,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.6,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.55, 
                        ["destroy_capacity"] = 0.55,
                    },
                },
            },                              
        }, 

        ["SNEB-253"] = { -- Rockets ? mm HE , aka Matra f1
            ["type"] = "Rockets",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1955,
            ["end_service"] = nil,
            ["cost"] = 1.7,-- k$  
            ["tnt"] = 3, --kg ???
            ["range"] = 8, -- Km ??
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                                
                    ["small"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.07,
                    },     
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.07,
                    },              
                },                
                            
                ["ship"] = { -- mobile target
                                    
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 0.08,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 0.07,
                    },
                },    
                
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.3,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.55, 
                        ["destroy_capacity"] = 0.45,
                    },
                },

                ["armor"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.1,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.2,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.3,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.55, 
                        ["destroy_capacity"] = 0.25,
                    },
                },   

                ["Parked Aircraft"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.3,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.55, 
                        ["destroy_capacity"] = 0.45,
                    },
                },
            },                              
        }, 
    },

    -- MATRA_F1_SNEBT253
    --russia
    -- a2a missile: /K-13A/, /R-60M/, /R-3R/, /R-3S/, /R-24T/, /R-24R/, /R-40R/, /R-40T/, /R-27T(dopo)/, /R-27R(dopo)/
    -- bomb: /FAB-1500/, /FAB-500/, /FAB-250/, /FAB-100/, /FAB-50/, BL-755(cluster? att inglese??), /RBK-250(cluster)/, /RBK-500AO(cluster)/, /KAB-500L(laser)/, /KMGU-96r(cluster)/, /KMGU-2F/2B(cluster )/
    -- rockets:  /UPK-23/, /9M114/, /ORO-57K_S5M_HEFRAG/, /S24-HE-FRAG/, /S-25/, /S-13/, /B-8/, /UB-13/, /UB-32/, S-5KO, /S-8KOM/, /S-24B/, /UB16UM/, /S-5M/,
    -- a2g missile: , /Kh-66/, /Kh-25ML/, /Kh-25MR/, /Kh-25MP/, ,Kh-29L, Kh-29T, Kh-31A(dopo), Kh-31P(dopo), Kh-35(dopo), Kh-41(dopo), Kh-65(dopo)
    -- a2r missile: /Kh-25MPU/, /Kh-58/
    -- a2s missile: /Kh-22N/, Kh-59M (1980), 
    
    ["red"] = {  

        ["9M120-F"] = { -- Missile radioguided 130 mm soft and structure target thermobaric warhead,
            ["type"] = "ASM",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1980, 
            ["end_service"] = nil,
            ["cost"] = 50,-- k$  
            ["tnt"] = 7.4, --kg 
            ["range"] = 6, -- Km
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  

                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                                
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.5,
                    },                   
                },                
                            
                ["ship"] = { -- mobile target
                    
                    ["med"] = {
                        ["accuracy"] = 0.8,  
                        ["destroy_capacity"] = 0.1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 0.15,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.1,
                    },
                },    
                                
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 0.4,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 0.6,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.5,
                    },
                },               

                ["armor"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 0.1,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.2,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 0.3,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.25,
                    },
                }, 

                ["Parked Aircraft"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 0.4,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacit"] = 0.5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 0.6,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 0.55,
                    },
                },
            },                              
        },

        ["9M120"] = { -- Missile radioguided 130 mm hard target HEAT (High Explosive Anti Tank warhead,
            ["type"] = "ASM",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1980, 
            ["end_service"] = nil,
            ["cost"] = 50,-- k$  
            ["tnt"] = 7.4, --kg 
            ["range"] = 6, -- Km
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  

                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                                
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.1,
                    },                   
                },                
                            
                ["ship"] = { -- mobile target
                    
                    ["med"] = {
                        ["accuracy"] = 0.8,  
                        ["destroy_capacity"] = 0.1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 0.15,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.1,
                    },
                },    
                                
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 0.4,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 0.6,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.5,
                    },
                },               

                ["armor"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 0.35,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.45,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 0.55,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.45,
                    },
                }, 

                ["Parked Aircraft"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 0.4,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacit"] = 0.5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 0.6,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 0.55,
                    },
                },
            },                              
        },

        ["9M114"] = { -- Missile radioguided 80 mm antitank hard target,
            ["type"] = "ASM",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1975, --1976: trial-- service: 1983
            ["end_service"] = nil,
            ["cost"] = 35,-- k$  
            ["tnt"] = 5, --kg ?? (not applicable?)
            ["range"] = 7, -- Km
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  

                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                                   
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.1,
                    },                   
                },                
                            
                ["ship"] = { -- mobile target
                    
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 0.15,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 0.1,
                    },
                },    
                                
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.4,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.6,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 0.5,
                    },
                },               

                ["armor"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.3,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.6,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 0.35,
                    },
                }, 

                ["Parked Aircraft"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.4,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacit"] = 0.5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.6,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.55, 
                        ["destroy_capacity"] = 0.55,
                    },
                },
            },                              
        },

        ["Hot-3"] = { -- Missile wire-guide 150 mm antitank hard target,
            ["type"] = "ASM",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1978,
            ["end_service"] = nil,
            ["cost"] = 35,-- k$  
            ["tnt"] = 6, --kg ?? (not applicable?)
            ["range"] = 4, -- Km
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  

                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                                   
                    ["mix"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.12,
                    },                   
                },                
                            
                ["ship"] = { -- mobile target
                    
                    ["med"] = {
                        ["accuracy"] = 0.85,  
                        ["destroy_capacity"] = 0.15,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8,   
                        ["destroy_capacity"] = 0.2,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.17,
                    },
                },    
                                
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.9,   -- 
                        ["destroy_capacity"] = 0.6,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.7,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 0.9,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.7,
                    },
                },               

                ["armor"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.9,   -- 
                        ["destroy_capacity"] = 0.45,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.6,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 0.8,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.6,
                    },
                }, 

                ["Parked Aircraft"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.9,   -- 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacit"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.95,
                    },
                },
            },                              
        },

        ["Mistral"] = { -- Missile wire-guide 150 mm antitank hard target,
            ["type"] = "ASM",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1985, -- 1988
            ["end_service"] = nil,
            ["cost"] = 40,-- k$  
            ["tnt"] = 3, --kg ?? (not applicable?)
            ["range"] = 6, -- Km
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  

                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                                   
                    ["mix"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.3,
                    },                   
                },                
                            
                ["ship"] = { -- mobile target
                                        
                    ["small"] = {
                        ["accuracy"] = 0.8,   
                        ["destroy_capacity"] = 0.1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.17,
                    },
                },    
                                
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.9,   -- 
                        ["destroy_capacity"] = 0.3,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.37,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 0.4,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.35,
                    },
                },               

                ["armor"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.9,   -- 
                        ["destroy_capacity"] = 0.25,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 0.4,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.3,
                    },
                }, 

                ["Parked Aircraft"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.9,   -- 
                        ["destroy_capacity"] = 0.4,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacit"] = 0.5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 0.7,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.6,
                    },
                },
            },                              
        },

        ["UPK-23"] = { -- autocannon 23 mm soft target, light armored, 
            ["type"] = "Rockets",    -- change, implements new type?   
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1972, 
            ["end_service"] = nil,
            ["cost"] = nil,-- k$  
            ["tnt"] = nil, --kg not applicable
            ["range"] = 2, -- Km
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {                          
                            
                ["ship"] = { -- mobile target
                                        
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 0.15,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 0.1,
                    },
                },    
                                
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.1,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.2,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.4,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 0.35     ,
                    },
                },               

                ["armor"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.05,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.2,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 0.15,
                    },
                }, 

                ["Parked Aircraft"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.2,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacit"] = 0.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.4,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.55, 
                        ["destroy_capacity"] = 0.35,
                    },
                },
            },                              
        },

        ["Gsh-23L"] = { -- autocannon 23 mm soft target, light armored, 
            ["type"] = "Rockets",    -- change, implements new type?   
            ["task"] = {"Strike"},
            ["start_service"] = 1972, 
            ["end_service"] = nil,
            ["cost"] = nil,-- k$  
            ["tnt"] = nil, --kg not applicable
            ["range"] = 2, -- Km
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {                          
                            
                ["ship"] = { -- mobile target
                                        
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 0.15,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 0.1,
                    },
                },    
                                
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.1,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.2,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.4,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 0.35     ,
                    },
                },               

                ["armor"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.05,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.2,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 0.15,
                    },
                }, 

                ["Parked Aircraft"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.2,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacit"] = 0.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.4,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.55, 
                        ["destroy_capacity"] = 0.35,
                    },
                },
            },                              
        },

        ["S-5 M"] = { -- Rockets 57 mm soft target, launcher UB-32UM/16UM (qty: 32/16), ORO-57K(8)
            ["type"] = "Rockets",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1960,
            ["end_service"] = nil,
            ["cost"] = 0.4,-- k$  
            ["tnt"] = 6, --kg ?? (not applicable?)
            ["range"] = 4, -- Km
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  

                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                                
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.15,
                    },                   
                },                
                            
                ["ship"] = { -- mobile target
                    
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 0.15,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 0.1,
                    },
                },    
                                
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.3,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.6,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 0.5,
                    },
                },               

                ["armor"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.2,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.4,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 0.35,
                    },
                }, 

                ["Parked Aircraft"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.4,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacit"] = 0.5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.6,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.55, 
                        ["destroy_capacity"] = 0.55,
                    },
                },
            },                              
        },

        ["S-5 KO"] = { -- Rockets 57 mm light armor target, launcher UB-32A (qty: 32),
            ["type"] = "Rockets",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1973, --1973: trial-- service: 1983
            ["end_service"] = nil,
            ["cost"] = 0.8,-- k$  
            ["tnt"] = 6, --kg ?? (not applicable?)
            ["range"] = 4, -- Km
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  

                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                                   
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.15,
                    },                   
                },                
                            
                ["ship"] = { -- mobile target
                    
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 0.15,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 0.1,
                    },
                },    
                                
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.3,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.6,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 0.5,
                    },
                },               

                ["armor"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.2,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.4,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 0.35,
                    },
                }, 

                ["Parked Aircraft"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.4,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacit"] = 0.5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.6,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.55, 
                        ["destroy_capacity"] = 0.55,
                    },
                },
            },                              
        }, 

        ["S-8 OFP2"] = { -- Rockets 80 mm soft target, launcher B-8MI (qty: 20), B-8V20A (qty: 10),
            ["type"] = "Rockets",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1973, --1973: trial-- service: 1983
            ["end_service"] = nil,
            ["cost"] = 0.6,-- k$  
            ["tnt"] = 6, --kg ?? (not applicable?)
            ["range"] = 4, -- Km
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  

                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                                   
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.08,
                    },                   
                },                
                            
                ["ship"] = { -- mobile target
                    
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.08,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 0.1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 0.1,
                    },
                },    
                                
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.3,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.6,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 0.5,
                    },
                },               

                ["Parked Aircraft"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.1,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacit"] = 0.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.4,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.55, 
                        ["destroy_capacity"] = 0.35,
                    },
                },
            },                              
        },

        ["S-8 KOM"] = { -- Rockets 80 mm antitank hard target, launcher B-8MI (qty: 20), B-8V20A (qty: 10),
            ["type"] = "Rockets",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1973, --1973: trial-- service: 1983
            ["end_service"] = nil,
            ["cost"] = 1,-- k$  
            ["tnt"] = 6, --kg ?? (not applicable?)
            ["range"] = 4, -- Km
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  

                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                                   
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.15,
                    },                   
                },                
                            
                ["ship"] = { -- mobile target
                    
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 0.15,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 0.1,
                    },
                },    
                                
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.3,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.6,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 0.5,
                    },
                },               

                ["armor"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.2,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.4,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 0.35,
                    },
                }, 

                ["Parked Aircraft"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.4,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacit"] = 0.5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.6,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.55, 
                        ["destroy_capacity"] = 0.55,
                    },
                },
            },                              
        }, 

        ["S-13"] = { -- Rockets 122 mm soft target, launcher UB-13 (qty: 5)
            ["type"] = "Rockets",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1973, --1973: trial-- service: 1983
            ["end_service"] = nil,
            ["cost"] = 0.8,-- k$  
            ["tnt"] = 1.9, --kg ?? (not applicable?)
            ["range"] = 3, -- Km
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                                
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.1,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.13,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.15,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 0.13,
                    },
                },               

                ["Parked Aircraft"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.05,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacit"] = 0.1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.2,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.55, 
                        ["destroy_capacity"] = 0.17,
                    },
                },
            },                              
        }, 

        ["S-25L"] = { -- Rockets 340 mm hard target (antitank), 250OFM,   Launcher O-25 (qty: 1)
            ["type"] = "Rockets",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1975,
            ["end_service"] = nil,
            ["cost"] = 2.8,-- k$  
            ["tnt"] = 20,
            ["range"] = 7, -- Km
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                                   
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.3,
                    },                   
                },                
                            
                ["ship"] = { -- mobile target
                    
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 0.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 0.45,
                    },
                },    
                
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.9,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 0.9,
                    },
                },

                ["armor"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.4,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.6,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.8,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 0.7,
                    },
                },   

                ["Parked Aircraft"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 1,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacit"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.55, 
                        ["destroy_capacity"] = 1,
                    },
                },
            },                              
        }, 

        ["S-24"] = { -- (Vers. A/B) Rockets 240 mm soft target, launcher: PU-12-40U (qty: 1), APU-7D, APU-68U
            ["type"] = "Rockets",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1960,
            ["end_service"] = nil,
            ["cost"] = 1.5,-- k$  
            ["tnt"] = 25.5, --kg ?? (not applicable?)
            ["range"] = 3, -- Km
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                                   
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.3,
                    },                   
                },                
                            
                ["ship"] = { -- mobile target
                    
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 0.4,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 0.4,
                    },
                },    
                
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.9,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 0.95,
                    },
                },

                ["armor"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.2,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacity"] = 0.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 0.4,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 0.35,
                    },
                },   

                ["Parked Aircraft"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.6,  
                        ["destroy_capacit"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.5,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.55, 
                        ["destroy_capacity"] = 0.9,
                    },
                },
            },                              
        }, 

        ["Kh-22N"] = { -- radar antiship
            ["type"] = "ASM",       
            ["task"] = {"Anti-ship Strike"},
            ["start_service"] = 1967,
            ["end_service"] = nil,
            ["cost"] = 1000,-- k$  
            ["tnt"] = 1000, --kg
            ["range"] = 330,
            ["perc_efficiency_variability"] = 0.05, -- efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 1,   -- 
                        ["destroy_capacity"] = 1,
                    },
                    ["med"] = {
                        ["accuracy"] = 1,  
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.95,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 1,
                    },
                },                                   
            },                              
        },

        ["Kh-58"] = {  --antiradiation                                           -- weapon name
            ["type"] = "ASM",                                       -- weapon type
            ["task"] = {"SEAD"},                        -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1975, --1978 --1982 vers. U
            ["end_service"] = nil,
            ["cost"] = 700,-- k$  
            ["tnt"] = 149, --kg
            ["range"] = 250,
            ["perc_efficiency_variability"] = 0.2,                  -- efficiecy variability(0-1): firepower_max = firepower_max * ( 1 + perc_efficiency_variability )
            ["efficiency"] = {                                      -- efficiency attribute table
                
                ["SAM"] = {                                        -- attribute                    
                    ["big"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.9,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 1,
                    },
                },        
            },                              
        },

        ["Kh-66"] = { -- radar
            ["type"] = "ASM",       
            ["task"] = {"Anti-ship Strike", "Strike", "SEAD"},
            ["start_service"] = 1967,
            ["end_service"] = nil,
            ["cost"] = 200,-- k$  
            ["tnt"] = 111, --kg
            ["range"] = 10, -- Km
            ["perc_efficiency_variability"] = 0.05, -- efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 0.15, -- 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.22,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.53,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.96, 
                        ["destroy_capacity"] = 0.24,
                    },
                },                
            
                ["Bridge"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.22,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.33,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.28,
                    },
                },      

                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 1,   -- 
                        ["destroy_capacity"] = 0.7,
                    },
                    ["med"] = {
                        ["accuracy"] = 1,  
                        ["destroy_capacity"] = 0.8,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.85,
                    },
                },   
                
                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 1,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 1,
                    },
                },

                ["armor"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 0.9,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 1,
                    },
                },   

                ["Parked Aircraft"] = { -- mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 
                        ["destroy_capacity"] = 1,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.8,  
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 1,
                    },
                },

                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.8,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 0.8, -- element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.9,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 1,
                    },
                }, 
            },                              
        },

        ["Kh-59"] = { -- TV guided, vers. M -> 1990
            ["type"] = "ASM",       
            ["task"] = {"Anti-ship Strike", "Strike", "SEAD"},
            ["start_service"] = 1980,
            ["end_service"] = nil,
            ["cost"] = 600,-- k$  
            ["tnt"] = 142, --kg
            ["range"] = 90, --Km
            ["perc_efficiency_variability"] = 0.05, -- efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 0.3, -- 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.7,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.5,
                    },
                },                
            
                ["Bridge"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.7,
                    },
                },        

                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 1,   -- 
                        ["destroy_capacity"] = 0.4,
                    },
                    ["med"] = {
                        ["accuracy"] = 1,  
                        ["destroy_capacity"] = 0.6,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9,   
                        ["destroy_capacity"] = 0.8,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.7,
                    },
                },        

                ["soft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.95,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 1,
                    },
                },                

                ["Parked Aircraft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 1,
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.96, 
                        ["destroy_capacity"] = 1,
                    },
                },   
                
                 ["armor"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.65,
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.7,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.75,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.7,
                    },
                },

                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.7,
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.75,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.75,
                    },
                },    
            },                               
        },

        ["Kh-25ML"] = { -- laser guided
            ["type"] = "ASM",       
            ["task"] = {"Anti-ship Strike", "Strike", "SEAD"},
            ["start_service"] = 1975,
            ["end_service"] = nil,
            ["cost"] = 160,-- k$  
            ["tnt"] = 90, --kg
            ["range"] = 11, --Km
            ["perc_efficiency_variability"] = 0.05, -- efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 0.15, -- 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.22,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.53,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.24,
                    },
                },                
            
                ["Bridge"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.22,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.33,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.28,
                    },
                },        

                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 1,   -- 
                        ["destroy_capacity"] = 0.22,
                    },
                    ["med"] = {
                        ["accuracy"] = 1,  
                        ["destroy_capacity"] = 0.27,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9,   
                        ["destroy_capacity"] = 0.35,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.3,
                    },
                },        

                ["soft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.85,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.95,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.9,
                    },
                },                

                ["Parked Aircraft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.95,
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.96, 
                        ["destroy_capacity"] = 1,
                    },
                },   
                
                 ["armor"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.65,
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.7,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.75,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.7,
                    },
                },

                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.7,
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.75,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.75,
                    },
                },    
            },                               
        },

        ["Kh-25MR"] = { -- radar guided 
            ["type"] = "ASM",       
            ["task"] = {"Anti-ship Strike", "Strike", "SEAD"},
            ["start_service"] = 1975,
            ["end_service"] = nil,
            ["cost"] = 160,-- k$  
            ["tnt"] = 140, --kg
            ["range"] = 11, --Km
            ["perc_efficiency_variability"] = 0.05, -- efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 0.22, -- 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.35,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.78,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.6,
                    },
                },                
            
                ["Bridge"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.35,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.45,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.4,
                    },
                },        

                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 1,   -- 
                        ["destroy_capacity"] = 0.33,
                    },
                    ["med"] = {
                        ["accuracy"] = 1,  
                        ["destroy_capacity"] = 0.44,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9,   
                        ["destroy_capacity"] = 0.52,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.45,
                    },
                },        

                ["soft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 1,
                    },
                },                

                ["Parked Aircraft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 1,
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.96, 
                        ["destroy_capacity"] = 1,
                    },
                },   
                
                ["armor"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.9,
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.98,
                    },
                },

                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.9,
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.98,
                    },
                },    
            },                               
        },

        ["Kh-25MPU"] = {  --antiradiation                                           -- weapon name
            ["type"] = "ASM",                                       -- weapon type
            ["task"] = {"SEAD"},                        -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1975, --1978 --1982 vers. U
            ["end_service"] = nil,
            ["cost"] = 300,-- k$  
            ["tnt"] = 90, --kg
            ["range"] = 30, --Km
            ["perc_efficiency_variability"] = 0.1,                  -- efficiecy variability(0-1): firepower_max = firepower_max * ( 1 + perc_efficiency_variability )
            ["efficiency"] = {                                      -- efficiency attribute table                
                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.83, 
                        ["destroy_capacity"] = 0.7,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.83, 
                        ["destroy_capacity"] = 0.75,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.82, 
                        ["destroy_capacity"] = 0.75,
                    },
                },           
            },                              
        },

        ["Kh-25MP"] = {  --antiradiation                                           -- weapon name
            ["type"] = "ASM",                                       -- weapon type
            ["task"] = {"SEAD"},                        -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1975, --1978 --1982 vers. U
            ["end_service"] = nil,
            ["cost"] = 200,-- k$  
            ["tnt"] = 90, --kg
            ["range"] = 18, --Km
            ["perc_efficiency_variability"] = 0.2,                  -- efficiecy variability(0-1): firepower_max = firepower_max * ( 1 + perc_efficiency_variability )
            ["efficiency"] = {                                      -- efficiency attribute table                
                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.7,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.75,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.6, 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.75,
                    },
                },           
            },                              
        },

        ["Kh-29L"] = { -- laser guided
            ["type"] = "ASM",       
            ["task"] = {"Anti-ship Strike", "Strike", "SEAD"},
            ["start_service"] = 1980,
            ["end_service"] = nil,
            ["cost"] = 160,-- k$  
            ["tnt"] = 320, --kg
            ["range"] = 10, --Km
            ["perc_efficiency_variability"] = 0.05, -- efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 0.55, -- 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.7,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.7,
                    },
                },                
            
                ["Bridge"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.95,
                    },
                    ["mix"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.85,
                    },
                },        

                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 1,   -- 
                        ["destroy_capacity"] = 0.9,
                    },
                    ["med"] = {
                        ["accuracy"] = 1,  
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 1,
                    },
                },        
            },                               
        },

        ["Kh-29T"] = { -- TV guided
            ["type"] = "ASM",       
            ["task"] = {"Anti-ship Strike", "Strike", "SEAD"},
            ["start_service"] = 1980,
            ["end_service"] = nil,
            ["cost"] = 160,-- k$  
            ["tnt"] = 320, --kg
            ["range"] = 12, --Km
            ["perc_efficiency_variability"] = 0.05, -- efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 0.55, -- 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.7,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.7,
                    },
                },                
            
                ["Bridge"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.95,
                    },
                    ["mix"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.85,
                    },
                },        

                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 1,   -- 
                        ["destroy_capacity"] = 0.9,
                    },
                    ["med"] = {
                        ["accuracy"] = 1,  
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 1,
                    },
                },        
            },                               
        },

        ["R-13M"] = {                                              -- weapon name
            ["type"] = "AAM",                                       -- weapon type            
            ["seeker"] = "infrared",                                -- seeker type (infrared, semiactive_radar, active_radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1974, 
            ["end_service"] = nil,
            ["cost"] = 70,-- k$  
            ["tnt"] = 5.5, --kg
            ["reliability"] = 0.6,                              -- reliability (0-1)
            ["range"] = 15,                                    -- km, range (aircraft must track target)                              
            ["max_height"] = 20,                                -- km max height
            ["max_speed"] = 2.7,                                  -- mach                            
            ["manouvrability"] = 0.8,
        },

        ["R-13M1"] = {                                              -- weapon name
            ["type"] = "AAM",                                       -- weapon type            
            ["seeker"] = "infrared",                                -- seeker type (infrared, semiactive_radar, active_radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1975, -- 1976 
            ["end_service"] = nil,
            ["cost"] = 77,-- k$  
            ["tnt"] = 5.5, --kg
            ["reliability"] = 0.6,                              -- reliability (0-1)
            ["range"] = 17,                                    -- km, range (aircraft must track target)                              
            ["max_height"] = 20,                                -- km max height
            ["max_speed"] = 2.4,                                  -- mach                            
            ["manouvrability"] = 0.8,
        },

        ["R-60"] = {                                              -- weapon name
            ["type"] = "AAM",                                       -- weapon type            
            ["seeker"] = "infrared",                                -- seeker type (infrared, semiactive_radar, active_radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1974, 
            ["end_service"] = nil,
            ["cost"] = 50,-- k$  
            ["tnt"] = 3, --kg
            ["reliability"] = 0.6,                              -- reliability (0-1)
            ["range"] = 8,                                    -- km, range (aircraft must track target)                              
            ["max_height"] = 20,                                -- km max height
            ["max_speed"] = 2.7,                                  -- mach                            
            ["manouvrability"] = 0.7,
        },

        ["R-60M"] = {                                              -- weapon name
            ["type"] = "AAM",                                       -- weapon type            
            ["seeker"] = "infrared",                                -- seeker type (infrared, semiactive_radar, active_radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1974, --1982? 
            ["end_service"] = nil,
            ["cost"] = 60,-- k$  
            ["tnt"] = 3, --kg
            ["reliability"] = 0.6,                              -- reliability (0-1)
            ["range"] = 8,                                    -- km, range (aircraft must track target)                              
            ["max_height"] = 20,                                -- km max height
            ["max_speed"] = 2.7,                                  -- mach                            
            ["manouvrability"] = 0.7,
        },

        ["R-73"] = {                                            -- weapon name
            ["type"] = "AAM",                                   -- weapon type            
            ["seeker"] = "infrared",                            -- seeker type (infrared, semiactive_radar, active_radar)
            ["task"] = {"A2A"},                                 -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1984, 
            ["end_service"] = nil,
            ["cost"] = 90,-- k$  
            ["tnt"] = 7, --kg
            ["reliability"] = 0.8,                              -- reliability (0-1)
            ["range"] = 30,                                     -- km, range (aircraft must track target)                              
            ["max_height"] = 20,                                -- km max height
            ["max_speed"] = 2.7,                                -- mach                            
            ["manouvrability"] = 0.85,
        },

        ["R-3S"] = {             -- aka K-13A                     -- weapon name
            ["type"] = "AAM",                                       -- weapon type            
            ["seeker"] = "infrared",                                -- seeker type (infrared, semiactive_radar, active_radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1960,  
            ["end_service"] = nil,
            ["cost"] = 30,-- k$  
            ["tnt"] = 8.8, --kg
            ["reliability"] = 0.6,                              -- reliability (0-1)
            ["range"] = 8,                                    -- km, range (aircraft must track target)                              
            ["max_height"] = 20,                                -- km max height
            ["max_speed"] = 2.85,                                  -- mach                            
            ["manouvrability"] = 0.7,
        },

        ["R-3R"] = {                                              -- weapon name
            ["type"] = "AAM",                                       -- weapon type            
            ["seeker"] = "radar",                                -- seeker type (infrared, semiactive_radar, active_radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1966,  
            ["end_service"] = nil,
            ["cost"] = 30,-- k$  
            ["tnt"] = 8.8, --kg
            ["reliability"] = 0.6,                              -- reliability (0-1)
            ["range"] = 8,                                    -- km, range (aircraft must track target)                              
            ["semiactive_range"] = 8,                                    -- km, range (aircraft must track target) 
            ["max_height"] = 20,                                -- km max height
            ["max_speed"] = 2.85,                                  -- mach                            
            ["manouvrability"] = 0.7,
        },

        ["R-24R"] = {                                              -- weapon name
            ["type"] = "AAM",                                       -- weapon type            
            ["seeker"] = "radar",                                -- seeker type (infrared, semiactive_radar, active_radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1975, --1981,  
            ["end_service"] = 1992,
            ["cost"] = 125,-- k$  
            ["tnt"] = 35, --kg 
            ["reliability"] = 0.6,                              -- reliability (0-1)
            ["range"] = 50,                                    -- km, range (aircraft must track target) 
            ["semiactive_range"] = 50,                                    -- km, range (aircraft must track target)                                                           
            ["max_height"] = 25,                                -- km max height
            ["max_speed"] = 3.42,                                  -- mach                            
            ["manouvrability"] = 0.7,
        },

        ["R-24T"] = {                                              -- weapon name
            ["type"] = "AAM",                                       -- weapon type            
            ["seeker"] = "infrared",                                -- seeker type (infrared, semiactive_radar, active_radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1975, --1981,  
            ["end_service"] = 1992,
            ["cost"] = 125,-- k$  
            ["tnt"] = 35, --kg 
            ["reliability"] = 0.6,                              -- reliability (0-1)
            ["range"] = 15,                                    -- km, range (aircraft must track target)                              
            ["max_height"] = 25,                                -- km max height
            ["max_speed"] = 3.42,                                  -- mach                            
            ["manouvrability"] = 0.7,
        },

        ["R-40R"] = {                                              -- weapon name
            ["type"] = "AAM",                                       -- weapon type            
            ["seeker"] = "radar",                                -- seeker type (infrared, semiactive_radar, active_radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1972, --1981,  
            ["end_service"] = nil,
            ["cost"] = 200,-- k$  
            ["tnt"] = 70, --kg 
            ["reliability"] = 0.6,                              -- reliability (0-1)
            ["range"] = 50,                                    -- km, range (aircraft must track target) 
            ["semiactive_range"] = 50,                                    -- km, range (aircraft must track target)                                                           
            ["max_height"] = 25,                                -- km max height
            ["max_speed"] = 4.5,                                  -- mach                            
            ["manouvrability"] = 0.7,
        },

        ["R-40T"] = {                                              -- weapon name
            ["type"] = "AAM",                                       -- weapon type            
            ["seeker"] = "infrared",                                -- seeker type (infrared, semiactive_radar, active_radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1972, --1981,  
            ["end_service"] = nil,
            ["cost"] = 180,-- k$  
            ["tnt"] = 70, --kg 
            ["reliability"] = 0.6,                              -- reliability (0-1)
            ["range"] = 30,                                    -- km, range (aircraft must track target)                              
            ["max_height"] = 25,                                -- km max height
            ["max_speed"] = 4.5,                                  -- mach                            
            ["manouvrability"] = 0.7,
        },

        ["R-27R"] = {                                              -- weapon name
            ["type"] = "AAM",                                       -- weapon type            
            ["seeker"] = "radar",                                -- seeker type (infrared, semiactive_radar, active_radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1983, 
            ["end_service"] = nil,
            ["cost"] = 230,-- k$  
            ["tnt"] = 39, --kg 
            ["reliability"] = 0.6,                              -- reliability (0-1)
            ["range"] = 50,                                    -- km, range (aircraft must track target)                              
            ["semiactive_range"] = 50,                                    -- km, range (aircraft must track target)                              
            ["max_height"] = 25,                                -- km max height
            ["max_speed"] = 4.5,                                  -- mach                            
            ["manouvrability"] = 0.7,
        },

        ["R-27T"] = {                                              -- weapon name
            ["type"] = "AAM",                                       -- weapon type            
            ["seeker"] = "infrared",                                -- seeker type (infrared, semiactive_radar, active_radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1984, 
            ["end_service"] = nil,
            ["cost"] = 230,-- k$  
            ["tnt"] = 39, --kg 
            ["reliability"] = 0.6,                              -- reliability (0-1)
            ["range"] = 40,                                    -- km, range (aircraft must track target)                              
            ["max_height"] = 25,                                -- km max height
            ["max_speed"] = 4.5,                                  -- mach                            
            ["manouvrability"] = 0.7,
        },

        ["R-27ER"] = {                                              -- weapon name
            ["type"] = "AAM",                                       -- weapon type            
            ["seeker"] = "radar",                                -- seeker type (infrared, semiactive_radar, active_radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1983, 
            ["end_service"] = nil,
            ["cost"] = 230,-- k$  
            ["tnt"] = 39, --kg 
            ["reliability"] = 0.6,                              -- reliability (0-1)
            ["range"] = 120,                                    -- km, range (aircraft must track target)                              
            ["semiactive_range"] = 50,                                    -- km, range (aircraft must track target)                              
            ["max_height"] = 25,                                -- km max height
            ["max_speed"] = 4.5,                                  -- mach                            
            ["manouvrability"] = 0.7,
        },

        ["R-27ET"] = {                                              -- weapon name
            ["type"] = "AAM",                                       -- weapon type            
            ["seeker"] = "infrared",                                -- seeker type (infrared, semiactive_radar, active_radar)
            ["task"] = {"A2A"},                               -- weapon task: loadout and targetlist task (Strike, Anti-ship Strike, CAP, Intercept, AWACS, Fighter Sweep, Escort, SEAD)
            ["start_service"] = 1984, 
            ["end_service"] = nil,
            ["cost"] = 230,-- k$  
            ["tnt"] = 39, --kg 
            ["reliability"] = 0.6,                              -- reliability (0-1)
            ["range"] = 130,                                    -- km, range (aircraft must track target)                              
            ["max_height"] = 25,                                -- km max height
            ["max_speed"] = 4.5,                                  -- mach                            
            ["manouvrability"] = 0.7,
        },

        ["FAB-1500M54"] = {
            ["type"] = "Bombs",       
            ["task"] = {"Strike"},
            ["start_service"] = 1962,
            ["end_service"] = nil,
            ["cost"] = 6,-- k$  
            ["tnt"] = 667, --kg
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 0.88, -- 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 1,
                    },
                },                
            
                ["Bridge"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   
                        ["destroy_capacity"] = 0.9,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 1,
                    },
                },                                              
            },                              
        },

        ["FAB-500M62"] = {
            ["type"] = "Bombs",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1962,
            ["end_service"] = nil,
            ["cost"] = 3.3,-- k$  
            ["tnt"] = 201, --kg
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 0.4, -- 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.45,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.42,
                    },
                },                
            
                ["Bridge"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   
                        ["destroy_capacity"] = 0.35,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.45,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.4,
                    },
                },        

                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.42,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.5,  
                        ["destroy_capacity"] = 0.5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.3,   
                        ["destroy_capacity"] = 0.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.5, 
                        ["destroy_capacity"] = 0.4,
                    },
                },        

                ["soft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["big"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 1,
                    },

                    ["med"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 1,
                    },
                },  
            
                ["armor"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["big"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.9,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.95,
                    },
                },   

                ["Parked Aircraft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["med"] = {
                        ["accuracy"] = 0.93, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.83, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.93, 
                        ["destroy_capacity"] = 1,
                    },
                },                

                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["big"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.95,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.98,
                    },
                },    
            },                              
        },

        ["FAB-250M54"] = {
            ["type"] = "Bombs",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1962,
            ["end_service"] = nil,
            ["cost"] = 2.7,-- k$  
            ["tnt"] = 94, --kg
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 0.15, -- 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.22,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.53,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.24,
                    },
                },                
            
                ["Bridge"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    
                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.22,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.33,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.28,
                    },
                },        

                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.22,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.5,  
                        ["destroy_capacity"] = 0.27,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.3,   
                        ["destroy_capacity"] = 0.35,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.4, 
                        ["destroy_capacity"] = 0.3,
                    },
                },        

                ["soft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["med"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.85,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.95,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.74, 
                        ["destroy_capacity"] = 0.9,
                    },
                },                

                ["Parked Aircraft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.95,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.87, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.77, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 1,
                    },
                },   
                
                 ["armor"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.65,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.7,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.75,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.7,
                    },
                },

                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.7,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.75,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.75,
                    },
                },    
            },                              
        },

        ["FAB-100"] = {
            ["type"] = "Bombs",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1962,
            ["end_service"] = nil,
            ["cost"] = 1.5,-- k$  
            ["tnt"] = 39, --kg
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.20,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.13,
                    },
                },                
                            
                ["ship"] = { -- mobile target
            
                    ["med"] = {
                        ["accuracy"] = 0.5,  
                        ["destroy_capacity"] = 0.1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.3,   
                        ["destroy_capacity"] = 0.2,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.4, 
                        ["destroy_capacity"] = 0.15,
                    },
                },        

                ["soft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["med"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.74, 
                        ["destroy_capacity"] = 0.4,
                    },
                },                

                ["Parked Aircraft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.33,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.87, 
                        ["destroy_capacity"] = 0.4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.77, 
                        ["destroy_capacity"] = 0.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.55,
                    },
                },   
                
                ["armor"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.2,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.25,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.35,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.30,
                    },
                },    

                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.25,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.4,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.35,
                    },
                },    
            },                              
        },

        ["FAB-50"] = {
            ["type"] = "Bombs",       
            ["task"] = {"Strike"},
            ["start_service"] = 1950,
            ["end_service"] = nil,
            ["cost"] = 1,-- k$  
            ["tnt"] = 20, --kg
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                    
                ["soft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["med"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.2,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.25,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.74, 
                        ["destroy_capacity"] = 0.2,
                    },
                },                

                ["Parked Aircraft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.16,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.87, 
                        ["destroy_capacity"] = 0.2,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.77, 
                        ["destroy_capacity"] = 0.2,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.25,
                    },
                },  
                
                ["armor"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.08,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.12,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.17,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.15,
                    },
                },    

                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.12,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.15,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.2,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.17,
                    },
                },    
            },                              
        },

        ["RBK-250AO"] = {  --cluster bomb soft target
            ["type"] = "Cluster bombs",
            ["task"] = {"Strike"},	
            ["start_service"] = 1970,
            ["end_service"] = nil,
            ["cost"] = 16,-- k$  
            ["weight"] = 250, --kg
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["SAM"] = { -- non Anti-tank but antenna, launcher gear and PSU system are like soft units
                    ["big"] = {
                        ["accuracy"] = 0.75,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 2, -- element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 4,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.67, 
                        ["destroy_capacity"] = 3.5,
                    },
                },                
            
                ["Parked Aircraft"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.75,   
                        ["destroy_capacity"] = 3.2,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 4.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 7,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.67, 
                        ["destroy_capacity"] = 5.5,
                    },
                },        

                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.75,   -- 
                        ["destroy_capacity"] = 3.2,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 4.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65,   
                        ["destroy_capacity"] = 7.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.67, 
                        ["destroy_capacity"] = 6.3,
                    },
                },

                --[[["armor"] = { -- questa cluster non è per tank
                    ["big"] = {
                        ["accuracy"] = 0.75,   -- 
                        ["destroy_capacity"] = 3.2,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.8,  
                        ["destroy_capacity"] = 4.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 7,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 6,
                    },
                },]]    
            },                  
        },

        ["RBK-500AO"] = {  --cluster bomb soft target
            ["type"] = "Cluster bombs",
            ["task"] = {"Strike"},	
            ["start_service"] = 1970,
            ["end_service"] = nil,
            ["cost"] = 17,-- k$  
            ["weight"] = 500, --kg
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["SAM"] = { -- non Anti-tank but antenna, launcher gear and PSU system are like soft units
                    ["big"] = {
                        ["accuracy"] = 0.75,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 3, -- element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.67, 
                        ["destroy_capacity"] = 4.5,
                    },
                },                
            
                ["Parked Aircraft"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.75,   
                        ["destroy_capacity"] = 4,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 7.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.67, 
                        ["destroy_capacity"] = 6,
                    },
                },        

                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.75,   -- 
                        ["destroy_capacity"] = 4,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 6,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65,   
                        ["destroy_capacity"] = 8,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.67, 
                        ["destroy_capacity"] = 7,
                    },
                },

                --[[["armor"] = { -- questa cluster non è per tank
                    ["big"] = {
                        ["accuracy"] = 0.75,   -- 
                        ["destroy_capacity"] = 3.2,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.8,  
                        ["destroy_capacity"] = 4.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 7,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 6,
                    },
                },]]    
            },                  
        },

        ["RBK-500PTAB"] = {  --cluster bomb armor target (Anti-tank)
            ["type"] = "Cluster bombs",
            ["task"] = {"Strike"},	
            ["start_service"] = 1970,
            ["end_service"] = nil,
            ["cost"] = 20,-- k$  
            ["weight"] = 500, --kg
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["SAM"] = { -- antenna, launcher gear and PSU system are like soft units
                    ["big"] = {
                        ["accuracy"] = 0.75,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 3, -- element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.67, 
                        ["destroy_capacity"] = 4.5,
                    },
                },                
            
                ["Parked Aircraft"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.75,   
                        ["destroy_capacity"] = 4,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 5,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 7.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.67, 
                        ["destroy_capacity"] = 6,
                    },
                },        

                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.75,   -- 
                        ["destroy_capacity"] = 4,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 6,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65,   
                        ["destroy_capacity"] = 8,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.67, 
                        ["destroy_capacity"] = 7,
                    },
                },

                ["armor"] = { -- questa cluster è antitank
                    ["big"] = {
                        ["accuracy"] = 0.75,   -- 
                        ["destroy_capacity"] = 3.2,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.8,  
                        ["destroy_capacity"] = 4.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 6,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 5,
                    },
                },
            },                  
        },

        ["BetAB-500"] = {
            ["type"] = "Bombs",       
            ["task"] = {"Strike", "Anti-ship Strike"},
            ["start_service"] = 1962,
            ["end_service"] = nil,
            ["cost"] = 2.7,-- k$  
            ["tnt"] = 92, --kg
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 0.15, -- 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.22,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.53,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.24,
                    },
                },                
            
                ["Bridge"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    
                    ["med"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.22,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.33,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.28,
                    },
                },        

                ["ship"] = { -- mobile target
                    ["big"] = {
                        ["accuracy"] = 0.7,   -- 
                        ["destroy_capacity"] = 0.22,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.5,  
                        ["destroy_capacity"] = 0.27,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.3,   
                        ["destroy_capacity"] = 0.35,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.4, 
                        ["destroy_capacity"] = 0.3,
                    },
                },        

                ["soft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["med"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.85,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.95,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.74, 
                        ["destroy_capacity"] = 0.9,
                    },
                },                

                ["Parked Aircraft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.95,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.87, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.77, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 1,
                    },
                },   
                
                 ["armor"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.65,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 0.7,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.75,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 0.7,
                    },
                },

                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.7,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.75,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.75,
                    },
                },    
            },                              
        },

        ["KAB-500L"] = { -- laser bomb (FAB-500 with laser guide)
            ["type"] = "Guided bombs",       
            ["task"] = {"Strike"},
            ["start_service"] = 1975,
            ["end_service"] = nil,
            ["cost"] = 25,-- k$  
            ["tnt"] = 201, --kg
            ["perc_efficiency_variability"] = 0.05, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 0.4, -- 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.45,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.42,
                    },
                },                
            
                ["Bridge"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   
                        ["destroy_capacity"] = 0.35,
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.45,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.4,
                    },
                },        
                
                ["soft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["big"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 1,
                    },

                    ["med"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 1,
                    },
                },  
                
                ["armor"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["big"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.9,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.95,
                    },
                },   

                ["Parked Aircraft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["big"] = {
                        ["accuracy"] = 0.97, 
                        ["destroy_capacity"] = 1,
                    },

                    ["med"] = {
                        ["accuracy"] = 0.93, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.83, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.93, 
                        ["destroy_capacity"] = 1,
                    },
                },                

                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["big"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.95,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.98,
                    },
                },    
            },                              
        },

        ["KAB-500Kr"] = { -- tv-guided bomb fire&forget (FAB-500)
            ["type"] = "Guided bombs",       
            ["task"] = {"Strike"},
            ["start_service"] = 1980,
            ["end_service"] = nil,
            ["cost"] = 23,-- k$  
            ["tnt"] = 201, --kg
            ["perc_efficiency_variability"] = 0.05, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["Structure"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 0.4, -- 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.45,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.42,
                    },
                },                
            
                ["Bridge"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 1,   
                        ["destroy_capacity"] = 0.35,
                    },
                    ["med"] = {
                        ["accuracy"] = 1, 
                        ["destroy_capacity"] = 0.4,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.9, 
                        ["destroy_capacity"] = 0.45,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.95, 
                        ["destroy_capacity"] = 0.4,
                    },
                },        
                
                ["soft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["big"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 1,
                    },

                    ["med"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 1,
                    },
                },  
                
                ["armor"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["big"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.8,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.9,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.95,
                    },
                },   

                ["Parked Aircraft"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["big"] = {
                        ["accuracy"] = 0.97, 
                        ["destroy_capacity"] = 1,
                    },

                    ["med"] = {
                        ["accuracy"] = 0.93, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.83, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.93, 
                        ["destroy_capacity"] = 1,
                    },
                },                

                ["SAM"] = { -- fixed target (guided bombs and agm missile are more efficiency)            
                
                    ["big"] = {
                        ["accuracy"] = 0.85, 
                        ["destroy_capacity"] = 0.95,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 1,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 1,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.75, 
                        ["destroy_capacity"] = 0.98,
                    },
                },    
            },                              
        },

        ["KGBU-2AO"] = {  --cluster bomb soft target
            ["type"] = "Cluster bombs",
            ["task"] = {"Strike"},	
            ["start_service"] = 1970,
            ["end_service"] = nil,
            ["cost"] = 12,-- k$  
            ["weight"] = 250, --??--kg
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["SAM"] = { -- non Anti-tank but antenna, launcher gear and PSU system are like soft units
                    ["big"] = {
                        ["accuracy"] = 0.75,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 2, -- element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 4,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.67, 
                        ["destroy_capacity"] = 3.5,
                    },
                },                
            
                ["Parked Aircraft"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.75,   
                        ["destroy_capacity"] = 3.2,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 4.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 7,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.67, 
                        ["destroy_capacity"] = 5.5,
                    },
                },        

                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.75,   -- 
                        ["destroy_capacity"] = 3.2,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 4.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65,   
                        ["destroy_capacity"] = 7.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.67, 
                        ["destroy_capacity"] = 6.3,
                    },
                },

                --[[["armor"] = { -- questa cluster non è per tank
                    ["big"] = {
                        ["accuracy"] = 0.75,   -- 
                        ["destroy_capacity"] = 3.2,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.8,  
                        ["destroy_capacity"] = 4.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 7,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 6,
                    },
                },]]    
            },                  
        },

        ["KGBU-2PTAB"] = {  --cluster bomb armor target
            ["type"] = "Cluster bombs",
            ["task"] = {"Strike"},	
            ["start_service"] = 1970,
            ["end_service"] = nil,
            ["cost"] = 16,-- k$  
            ["weight"] = 250, --??--kg
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["SAM"] = { -- non Anti-tank but antenna, launcher gear and PSU system are like soft units
                    ["big"] = {
                        ["accuracy"] = 0.75,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 2, -- element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 4,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.67, 
                        ["destroy_capacity"] = 3.5,
                    },
                },                
            
                ["Parked Aircraft"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.75,   
                        ["destroy_capacity"] = 3.2,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 4.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 7,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.67, 
                        ["destroy_capacity"] = 5.5,
                    },
                },        

                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.75,   -- 
                        ["destroy_capacity"] = 3.2,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 4.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65,   
                        ["destroy_capacity"] = 7.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.67, 
                        ["destroy_capacity"] = 6.3,
                    },
                },

                ["armor"] = { 
                    ["big"] = {
                        ["accuracy"] = 0.75,   -- 
                        ["destroy_capacity"] = 3.2,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.8,  
                        ["destroy_capacity"] = 4.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 7,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 6,
                    },
                },
            },                  
        },

        ["KGBU-96r"] = {  --?? cluster bomb soft target VERIFY
            ["type"] = "Cluster bombs",
            ["task"] = {"Strike"},	
            ["start_service"] = 1970,
            ["end_service"] = nil,
            ["cost"] = 12,-- k$  
            ["weight"] = 250, --??--kg
            ["perc_efficiency_variability"] = 0.1, -- percentage of efficiecy variability 0-1 (100%)
            ["efficiency"] = {  
                
                ["SAM"] = { -- non Anti-tank but antenna, launcher gear and PSU system are like soft units
                    ["big"] = {
                        ["accuracy"] = 0.75,   -- 1 max, 0.1 min ( hit success percentage )
                        ["destroy_capacity"] = 2, -- element destroyed (single hit), 0.1 min ( element destroy capacity )                                    
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 4,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.67, 
                        ["destroy_capacity"] = 3.5,
                    },
                },                
            
                ["Parked Aircraft"] = {-- fixed target (guided bombs and agm missile are more efficiency)            
                    ["big"] = {
                        ["accuracy"] = 0.75,   
                        ["destroy_capacity"] = 3.2,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7, 
                        ["destroy_capacity"] = 4.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65, 
                        ["destroy_capacity"] = 7,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.67, 
                        ["destroy_capacity"] = 5.5,
                    },
                },        

                ["soft"] = { -- mobile target(artillery group)
                    ["big"] = {
                        ["accuracy"] = 0.75,   -- 
                        ["destroy_capacity"] = 3.2,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.7,  
                        ["destroy_capacity"] = 4.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.65,   
                        ["destroy_capacity"] = 7.5,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.67, 
                        ["destroy_capacity"] = 6.3,
                    },
                },

                --[[["armor"] = { -- questa cluster non è per tank
                    ["big"] = {
                        ["accuracy"] = 0.75,   -- 
                        ["destroy_capacity"] = 3.2,
                    },
                    ["med"] = {
                        ["accuracy"] = 0.8,  
                        ["destroy_capacity"] = 4.3,
                    },
                    ["small"] = {
                        ["accuracy"] = 0.7,   
                        ["destroy_capacity"] = 7,
                    },
                    ["mix"] = {
                        ["accuracy"] = 0.8, 
                        ["destroy_capacity"] = 6,
                    },
                },]]    
            },                  
        },
    },
}

