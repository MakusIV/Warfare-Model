-- ====================================== DC_Logistic =================================================================
-- 
-- UpdateOobAir():                        Update oob_air number property considering airbase efficiency property
-- SaveTabOnDisk( table_name, table ):    Save table supply_tab.lua on disk
-- 
-- ====================================================================================================================

-------------------------------------------------------------------------------------------------------

if not versionDCE then 
	versionDCE = {} 
end

               -- VERSION --

versionDCE["DC_Logistic.lua"] = "OB.1.0.0"

---------------------------------------------------------------------------------------------------------
-- Old_Boy rev. OB.1.0.0: implements logging code
-- Old_Boy rev. OB.0.0.1: implements supply line sistems (logistics)
-------------------------------------------------------------------------------------------------------



--[[DESCRIPTION 

    Aircraft resupply (ready aircraft) depends from damage level of airbase and damage level of supply_line and supply_plant

    The supply infrastructure logic:

    supply plant --- supplies ---->|----> supply line A -- supplies---> |--> airbase 1
                                |                                    |--> airbase 3
                                |                                    |--> airbase 5
                                |
                                |----> supply line B -- supplies---> |--> airbase 2
                                |                                    |--> airbase 5
                                |
                                |----> supply line C -- supplies---> |--> airbase 2

    calculus:
    aircraft.ready = expected.aircraft.ready * ( 2^( airbase.efficiency * k ) -1 ). k: defined by user for balance. k:(0,1]
    airbase.efficiency = airbase.integrity * airbase.supply.       airbase.efficiency:[0,1]
    airbase.supply = max( supply_plant.integrity * supply_line.integrity ). airbase.supply:[0,1]
    <asset type>.integrity = <asset type>.alive/100.

    This module use two table: airbase_tab and supply_tab.
    airbase_tab include airbases with aircraft_type and efficiency values: used for number of aircraft avalaibility calculation.
    airbase_tab is created, update and saved (/Active) during mission generation.
    supply_tab is loaded initially from supply_tab_init.lua file (/Init), update and saved (/Active) during mission generation.
    supply_tab define association from airbase and supply asset (supply_line, supply_plant).
    The campaign maker must initialize supply_tab_init using targets presents in targetlist table and airbases presents in oob_air.
    Important: 
    I) the names of the airbases written in supply_tab_init must be the same as those used in the oob_air. 
    II) the names of the airbases defined in targetlist must be the same as those used in oob_air, eventually with the addition of postfix " Airbase" or prefix " FARP".
    For example: oob_air[<n>].base = "Mozdok", supply_tab[][][][airbases_supply]["Mozdok"], targetlist[]["Mozdok"] or targetlist[]["Mozdok Airbase"]]

    --[[

    airbase_tab structure example

    airbase_tab = {

        [blue] = {
            [base_1] = {
                ["aircraft_types"]
                    [aircraft_1] = name
                    [aircraft_2] = name
                ["efficiency"] 0.72
                ["integrity"] 0.8
                ["supply"] 0.9
            }
            ......
        }
        [red] = {
            [base_n] = {
                ......
            }
            .......
        }
    }

]]

-- supply_tab structure example
--[[
-- this definition of supply_tab is dedicated only for development enviroment
supply_tab = {
	['red'] = {
		['Prohladniy Depot MP 24'] = {--      supply plant
			['integrity'] = 0.8, --           supply plant integrity
			['supply_line_names'] = {          table of supply lines supplyed by supply plant
				['Bridge Alagir MN 36'] = {   supply line
					['integrity'] = 0.5,      integrity of supply line
					['airbase_supply'] = {    table of airbases supplyd by supply line
						['Beslan'] = true,    test info: Beslan dovrebbe prendere 0.8*0.5=0.4 efficiency
						['Mozdok'] = true,
					},
				},
				['Bridge South Beslan MN 68'] = {
					['integrity'] = 0.25,
					['airbase_supply'] = {
						['Beslan'] = true,
						['Nalchik'] = true,
						['Sochi-Adler'] = true,
					},
				},
			},
		},
		['Mineralnye-Vody Airbase'] = {
			['integrity'] = 0.6,
			['supply_line_names'] = {
				['Rail Bridge SE Mayskiy MP 23'] = {
					['integrity'] = 0.5,
					['airbase_supply'] = {
						['Mozdok'] = true,
						['Sochi-Adler'] = true,
						['Beslan'] = true,
					},
				},
				['Bridge South Elhotovo MN 39'] = {
					['integrity'] = 0.25,
					['airbase_supply'] = {
						['Reserves'] = true,
						['Sochi-Adler'] = true,
						['Maykop-Khanskaya'] = true,
						['Nalchik'] = true,
						['Mozdok'] = true,
						['Beslan'] = true,
						['Mineralnye-Vody'] = true,
					},
				},
			},
		},
		['101 EWR Site'] = {
			['integrity'] = 1,
			['supply_line_names'] = {
				['Russian Convoy 1'] = {
					['integrity'] = 0.5,
					['airbase_supply'] = {
						['Mozdok'] = true,
						['Mineralnye-Vody'] = true,
					},
				},
				['Bridge SW Kardzhin MN 49'] = {
					['integrity'] = 0.25,
					['airbase_supply'] = {
						['Reserves'] = true,
						['Sochi-Adler'] = true,
						['Mineralnye-Vody'] = true,
						['Beslan'] = true,
						['Mozdok'] = true,
					},
				},
			},
		},
	},
	['blue'] = {
		['Sukhumi Airbase Strategics'] = {
			['integrity'] = 0.4,
			['supply_line_names'] = {
				['Rail Bridge Grebeshok-EH99'] = {
					['integrity'] = 0.25,
					['airbase_supply'] = {
						['Kutaisi'] = true,
						['Vaziani'] = true,
					},
				},
				['Bridge Anaklia-GG19'] = {
					['integrity'] = 0.5,
					['airbase_supply'] = {
						['Senaki-Kolkhi'] = true,
						['Batumi'] = true,
						['Reserves'] = true,
					},
				},
			},
		},
		['Novyy Afon Train Station - FH57'] = {
			['integrity'] = 0.8,
			['supply_line_names'] = {
				['Bridge Tagrskiy-FH08'] = {
					['integrity'] = 0.25,
					['airbase_supply'] = {
						['Kutaisi'] = true,
						['Batumi'] = true,
					},
				},
				['Bridge Nizh Armyanskoe Uschele-FH47'] = {
					['integrity'] = 0.5,
					['airbase_supply'] = {
						['Vaziani'] = true,
						['Senaki-Kolkhi'] = true,
						['Reserves'] = true,
					},
				},
			},
		},
	},
}]]

--[[ this definition of supply_tab is for testing in an active campaign running in DCS dedicated server enviroment
-- don't use in developement enviroment
supply_tab = {
	['blue'] = {
		['EWR-1'] = {
			['integrity'] = 0.8,
			['supply_line_names'] = {
				['EAU East Front Convoy 1'] = {
					['integrity'] = 0.25,
					['airbase_supply'] = {
						['Al Maktoum Intl'] = true,
						['Sharjah Intl'] = true
					}
				},
				['US Army ELINT Station'] = {
					['integrity'] = 0.5,
					['airbase_supply'] = {
						['Dubai Intl'] = true,
						['Reserves'] = true,
						['Jazirat al Hamra FARP'] = true
					}
				}
			}
		},
		['EWR-2'] = {
			['integrity'] = 0.4,
			['supply_line_names'] = {
				['EAU West Front Convoy 2'] = {
					['integrity'] = 0.5,
					['airbase_supply'] = {
						['Reserves'] = true,
						['LHA_Nassau'] = true,
						['Al Dhafra AB'] = true
					}
				},
				['US Army ELINT Station 2'] = {
					['integrity'] = 0.25,
					['airbase_supply'] = {
						['LHA_Tarawa'] = true,
						['Dubai Intl'] = true
					}
				}
			}
		},
    ['EWR-3'] = {
      ['integrity'] = 0.4,
      ['supply_line_names'] = {
        ['EAU West Front Convoy 3'] = {
          ['integrity'] = 0.5,
          ['airbase_supply'] = {
            ['Reserves'] = true,
            ['LHA_Nassau'] = true,
            ['LHA_Tarawa'] = true
          }
        },
        ['EAU West Front Convoy 1'] = {
          ['integrity'] = 0.25,
          ['airbase_supply'] = {
            ['Jazirat al Hamra FARP'] = true,
            ['Reserves'] = true
          }
        }
      }
    }
	},
	['red'] = {
		['EWR 1'] = {
			['integrity'] = 0.8,
			['supply_line_names'] = {
				['Mountain Iranian convoy 4'] = {
					['integrity'] = 0.25,
					['airbase_supply'] = {
						['Shiraz Intl'] = true,
						['Khasab'] = true
					}
				},
				['4th Iranian Transport fleet'] = {
					['integrity'] = 0.5,
					['airbase_supply'] = {
						['Bandar e Jask airfield'] = true,
						['Qeshm Island'] = true
					}
				},
			}
		},
		['EWR 2'] = {
			['integrity'] = 0.4,
			['supply_line_names'] = {
				['2nd Iranian Transport fleet'] = {
					['integrity'] = 0.25,
					['airbase_supply'] = {
						['Bandar Abbas Intl'] = true,
						['Al Ima FARP'] = true,
						['Sirri Island'] = true
					}
				},
				['5th Iranian Transport fleet'] = {
					['integrity'] = 0.5,
					['airbase_supply'] = {
						['Lar Airbase'] = true,
						['Reserves'] = true
					}
				}
			}
		},
    ['EWR 3'] = {
      ['integrity'] = 0.4,
      ['supply_line_names'] = {
        ['Iranian West frontline convoy 1'] = {
          ['integrity'] = 0.25,
          ['airbase_supply'] = {
            ['Reserves'] = true
          }
        },
        ['Iranian West frontline convoy 2'] = {
          ['integrity'] = 0.5,
          ['airbase_supply'] = {
            ['Lar Airbase'] = true,
            ['Reserves'] = true
          },
        }
      }
    }
	}
}]]


--[[DCE IMPLEMENTATION INFO

    new file:

    ScriptsMod.NG/: DC_Logistic.lua
    Init/: supply_tab_init.lua --defined by campaign's maker

    file modified:


    DEBRIEF_Master.lua:

    94 --=====================  start marco implementation ==================================
    95
    96 --run logistic evalutation and save supply_tab
    97 dofile("../../../ScriptsMod."..versionPackageICM.."/DC_Logistic.lua")--mark
    98 UpdateOobAir()
    99
    100 --=====================  end marco implementation ==================================


    BAT_FirstMission.lua:

    84 --====================  start marco implementation ==================================
    85
    86 dofile("Init/supply_tab_init.lua")
    87 local tgt_str = "supply_tab = " .. TableSerialization(supply_tab, 0)
    88 local tgtFile = nil
    89 tgtFile = io.open("Active/supply_tab.lua", "w")
    90 tgtFile:write(tgt_str)
    91 tgtFile:close()
    92
    93 --=====================  end marco implementation ==================================
]]

-- load UTIL_Log for define a local istance of logger (allow a dedicated file for this module)
local log = dofile("../../../ScriptsMod."..versionPackageICM.."/UTIL_Log.lua") --log = require("UTIL_Log.lua")
log.level = LOGGING_LEVEL  --(variabile globale)
log.outfile = LOG_DIR .. "LOG_DC_Logistic." .. camp.mission .. ".log"
local local_debug = true -- local debug
local executeTest = false

if executeTest then
  print("TEST EXECUTING\n")
  dofile("E://DCE/DCE_GW_1975/DCS_SavedGames_Path/Mods/tech/DCE/Missions/Campaigns/1975 Georgian War/Init/db_airbases.lua")
  dofile("E://DCE/DCE_GW_1975/DCS_SavedGames_Path/Mods/tech/DCE/Missions/Campaigns/1975 Georgian War/Active/targetlist.lua")
  dofile("E://DCE/DCE_GW_1975/DCS_SavedGames_Path/Mods/tech/DCE/Missions/Campaigns/1975 Georgian War/Active/oob_air.lua")
  dofile("E://DCE/DCE_GW_1975/DCS_SavedGames_Path/Mods/tech/DCE/Missions/Campaigns/1975 Georgian War/Active/supply_tab.lua")
  dofile("E://DCE/DCE_GW_1975/DCS_SavedGames_Path/Mods/tech/DCE/ScriptsMod.NG/UTIL_Functions.lua")

else
  -- load supply_tab
  dofile("Active/supply_tab.lua")

end



local DC_L_CONFIG = {

    PERCENTAGE_EFFICIENCY_INFLUENCE_FOR_AIRBASES = 100, -- (0 - 100) parameter to balance the influence property in the calculation of aircraft number for airbases
    PERCENTAGE_EFFICIENCY_INFLUENCE_FOR_RESERVES = 100, -- (0 - 100) parameter to balance the influence property in the calculation of aircraft number for reserves
}

--============ LOCAL FUNCTION =================================

-- dump a table
--from: https://stackoverflow.com/questions/9168058/how-to-dump-a-table-to-console
local function dump(o)
   if type(o) == 'table' then
      local s = '{ '
      for k,v in pairs(o) do
         if type(k) ~= 'number' then k = '"'..k..'"' end
         s = s .. '['..k..'] = ' .. dump(v) .. ','
      end
      return s .. '} '
   else
      return tostring(o)
   end
end

-- copy the supply_tab from Init folder
--from: https://stackoverflow.com/questions/2705793/how-to-get-number-of-entries-in-a-lua-table
local function copySupplyTab()

    dofile("E://DCE/DCE_GW_1975/DCS_SavedGames_Path/Mods/tech/DCE/Missions/Campaigns/1975 Georgian War/Init/supply_tab_init.lua")
    local tgt_str = "supply_tab = " .. TableSerialization(supply_tab, 0)
    local tgtFile = nil
    tgtFile = io.open("E://DCE/DCE_GW_1975/DCS_SavedGames_Path/Mods/tech/DCE/Missions/Campaigns/1975 Georgian War/Active/supply_tab.lua", "w")
    tgtFile:write(tgt_str)
    tgtFile:close()

    return true

end

-- table lenght
local function tablelength(T)
    local count = 0
    for _ in pairs(T) do count = count + 1 end
    return count
  end




-- Logistic function

-- Initialize the airbase_tab by defining the planes operating in the airbase
-- OK
local function InitializeAirbaseTab()

    local nameFunction = " function InitializeAirbaseTab(): "    
    log.debug("Start " .. nameFunction)
    local aircraft_type
    local group_name
    local airbase_name

    for side, index in pairs(oob_air) do-- iterate oob_air for take aircraft type in an airbase        
            
        for index_value, oob_value in pairs(index) do
            aircraft_type = oob_value.type
            group_name = oob_value.name
            airbase_name = oob_value.base

            if airbase_name == "Reserves" then
                airbase_name = airbase_name .. "-" .. group_name
            end

            log.trace(nameFunction .. airbase_name .. "." .. side .. ": " .. aircraft_type)

            if airbase_tab == nil then
                log.trace(nameFunction .. "airbase_tab is nil. Initialize new airbase_tab") 
                airbase_tab = {
                    [side] = {
                        [airbase_name] = {
                            ["aircraft_types"] = {
                                [aircraft_type] = group_name,
                            },
                            ["efficiency"] = 1, -- efficiency_<airbase>  1 = max (full efficiency), 0 = min
                            ["integrity"] = 1, -- same of targetlist.alive 1 = max, 0 = min (full damage)
                            ["supply"] = 1 -- supply_<airbase> 1 (full supply) = max, 0 = min
                        }
                    }
                }
                log.trace(nameFunction .. " - airbase_tab:\n" .. inspect(airbase_tab)) --print("\n--->: " .. dump(airbase_tab).. " <----\n")

            elseif airbase_tab[side] == nil then
                log.trace(nameFunction .. "airbase_tab." .. side .. " is nil. Initialize new airbase_tab." .. side) 
                airbase_tab[side] = {
                    [airbase_name] = {
                        ["aircraft_types"] = {
                            [aircraft_type] = group_name,
                        },
                        ["efficiency"] = 1, -- efficiency_<airbase>  1 = max (full efficiency), 0 = min
                        ["integrity"] = 1, -- same of targetlist.alive 1 = max, 0 = min (full damage)
                        ["supply"] = 1 -- supply_<airbase> 1 (full supply) = max, 0 = min
                    }
                }
                log.trace(nameFunction .. "Created new airbase_tab." .. side .. ": " .. airbase_name .. ", aircraft_type: " .. aircraft_type .. ", group_name: " .. group_name)

            else
                log.trace(nameFunction .. "airbase_tab." .. side .. " not nil")
                log.trace(nameFunction .. "oob_air airbase_name: " .. side .. " " .. airbase_name)                

                if airbase_tab[side][airbase_name] then
                    log.trace(nameFunction .. "airbase: " .. side .. " " .. airbase_name .." exists in airbase_tab")

                        if airbase_tab[side][airbase_name].aircraft_types[aircraft_type] == nil then
                            log.trace(nameFunction .. "oob_air aircraft type: " .. aircraft_type .. " --> not exixst aircraft, insert in airbase_tab")
                            airbase_tab[side][airbase_name].aircraft_types[aircraft_type] = group_name
                        end
                        
                else
                    log.trace(nameFunction .. "airbase not exists in airbase_tab")
                    airbase_tab[side][airbase_name] =  { -- insert new airbase, initialize property and assign aircraft
                        ["aircraft_types"] = { [aircraft_type] = group_name },-- insert new airbase and assign aircraft
                        ["efficiency"] = 1, -- efficiency_<airbase>  1 = max (full efficiency), 0 = min
                        ["integrity"] = 1, -- same of targetlist.alive 1 = max, 0 = min (full damage)
                        ["supply"]= 1 -- supply_<airbase> 1 (full supply) = max, 0 = min
                    }
                end                
            end
        end
    end
    log.debug(nameFunction .. " - airbase_tab:\n" .. inspect(airbase_tab) )
    log.debug("End " .. nameFunction)
	return airbase_tab
end

-- Update the integrity property for supply plant in supply_tab, by using property alive in targetlist
-- OK
local function UpdateSupplyPlantIntegrity( sup_tab )
    local nameFunction = "function UpdateSupplyPlantIntegrity( sup_tab ): "    
    log.debug("Start " .. nameFunction)

    -- note: supply Plant are defined in supply_tab and also in targetlist like targets
    for sidepw, side_val in pairs( sup_tab ) do

        for supply_plant_name, supply_plant_values in pairs( side_val ) do -- iteration of supply plants in supply_tab

            for side, targets in pairs( targetlist ) do -- iteration of side in targetlist tab

                for target_name, target_value in pairs( targets ) do -- iteration of targets from a single side
                    log.trace(nameFunction .. "sup tab side: " .. sidepw .. " - " .. "sup_pl_name: " .. supply_plant_name .. " - " .. "targlist side: " .. side .. " - " .. "target name: " .. target_name)
                    log.trace(nameFunction .. "sup tab integrity: " .. supply_plant_values['integrity'] .. " - " .. "target_value[\"alive\"]: " .. tostring( target_value['alive']))

                    if supply_plant_name ==  target_name then  -- update integrity value of an supply plant using alive target property
                        log.trace(nameFunction .. " target_value:\n" .. inspect( target_value ))
                        supply_plant_values.integrity = target_value.alive / 100 -- normalize integrity from 0 to 1
                        -- eventuale codice per terminare l'iterazione
                    end

                end
            end
        end
    end
    log.debug("End " .. nameFunction)
	return sup_tab
end

-- Update the integrity property for supply line in supply_tab, by using property alive in targetlist
-- OK
local function UpdateSupplyLineIntegrity( sup_tab )
    -- note: supply Line are defined in supply_tab and also in targetlist like targets
    local nameFunction = "function UpdateSupplyLineIntegrity( sup_tab ): "    
    log.debug("Start " .. nameFunction)

    for sidepw, side_val in pairs( sup_tab ) do

        for supply_plant_name, supply_plant_values in pairs( side_val ) do -- iteration of supply plants in supply_tab

            for supply_line_name, supply_line_values in pairs( supply_plant_values.supply_line_names ) do-- iteration of supply lines from a single supply_tab

                for side, targets in pairs( targetlist ) do-- iteration of blue and red side in targetlist tab

                    for target_name, target_value in pairs( targets ) do -- iteration of targets from a single side

                        if supply_line_name == target_name then -- update integrity value of an supply line using alive target property
                            log.trace(nameFunction .. "supply_line_name == target_name (" .. target_name .. ", actual value of supply_line_values.integrity: " .. supply_line_values.integrity .. ", updated with new value: " .. target_value.alive / 100)
                            supply_line_values.integrity = target_value.alive / 100 -- normalize integrity from 0 to 1
                        end
                    end
                end
            end
        end
    end
    log.debug("End " .. nameFunction)
	return sup_tab
end


-- Update the supply property in airbase_tab using integrity property from supply_tab
-- OK
local function UpdateAirbaseSupply( airb_tab, sup_tab )

    local nameFunction = "function UpdateAirbaseSupply( airb_tab, sup_tab ): "    
    log.debug("Start " .. nameFunction)

    local max_supply_value = {}

    for side_base, side_values in pairs( airb_tab ) do

        for base_name, base_values in pairs( side_values ) do

            for supply_plant_name, supply_plant_values in pairs( sup_tab[side_base] ) do

                for supply_line_name, supply_line_values in pairs( supply_plant_values.supply_line_names ) do

                    for airbase_name, airbase_values in pairs( supply_line_values.airbase_supply ) do
                        log.trace(nameFunction .. "air_tab.airbase: " .. base_name .. ", supply_line.airbase: " .. airbase_name)
                        log.trace(nameFunction .. "supply_plant: " .. supply_plant_name .. ", supply_line_name: " .. supply_line_name)

                        if base_name == airbase_name then
                            log.trace(nameFunction .. "side: " .. side_base .. " air_tab.airbase: " .. base_name .. ", supply_line.airbase: " .. airbase_name)
                            local supply = supply_plant_values.integrity --  -- update supply value of an airbase for power plantwithout power line (power_line_name == power_plant_name)                            
                            
                            if supply_plant_name ~= supply_line_name then
                                supply = supply * supply_line_values.integrity  -- update supply value of an airbase for power line different from power plant                            
                            end

                            if max_supply_value[base_name] then -- check previous supply values for this airbase                                

                                if supply > max_supply_value[base_name] then
                                    max_supply_value[base_name] = supply                                                
                                end

                            else                                                                                        
                                max_supply_value[base_name] = supply    
                            end
                            log.trace(nameFunction .. "air_tab.airbase.supply: " .. base_values.supply .. ", calculated supply: " .. supply)
                            log.trace(nameFunction .. "supply_plant_values.integrity: " .. supply_plant_values.integrity .. ", supply_line_values.integrity: " .. supply_line_values.integrity .. ", calculated supply: " .. supply)
                        end
                    end
                end
            end
            --select supply value from highest supply supply integrity calculated
            if max_supply_value[base_name] then   
                base_values.supply  = max_supply_value[base_name]
            end
        end
    end
    log.debug("End " .. nameFunction)
	return airb_tab
end

-- Update the integrity property in airbase_tab using alive property from targetlist
-- OK
local function UpdateAirbaseIntegrity( airb_tab )

    local nameFunction = "function UpdateAirbaseIntegrity( airb_tab ): "    
    log.debug("Start " .. nameFunction)

    for side, side_values in pairs( airb_tab ) do

        local target_side = "red"

        if side == "red" then
            target_side = "blue"
        end

        for base, airbase_values in pairs( side_values ) do

            -- base = base .." Airbase" or " FARP"
            for target_name, target_value in pairs( targetlist[target_side] ) do
                log.trace(nameFunction .. "airbase_tab airbase: " .. base .. ", targetlist airbase: " .. target_name)

                if target_name == base or target_name  == base .. " Airbase" or  target_name == base .. " FARP" or  target_name == "FARP " .. base then
                    log.trace(nameFunction .. "==============================\nairbase_tab airbase == targetlist airbase\n==============================")
                    log.trace(nameFunction .. "airbase_tab airbase: " .. base .. ", targetlist airbase: " .. target_name)
                    log.trace(nameFunction .. "actual airbase_tab integrity: " .. airbase_values.integrity .. ", new value: " .. target_value.alive / 100)
                    airbase_values.integrity = roundAtNumber(target_value.alive / 100 , 0.01)
                    break
                end
            end
       end
    end
    log.debug("End " .. nameFunction)
	return airb_tab
end

-- Update the airbase efficiency property in airbase_tab
-- OK
local function UpdateAirbaseEfficiency( airb_tab )

    local nameFunction = "function UpdateAirbaseEfficiency( airb_tab ): "    
    log.debug("End " .. nameFunction)

	for side, side_val in pairs( airb_tab ) do

		for base, airbase_values in pairs( side_val ) do
			airbase_values.efficiency = roundAtNumber(airbase_values.integrity * airbase_values.supply, 0.01)
			log.trace(nameFunction .. "airbase: " .. base)
			log.trace(nameFunction .. "airbase_values.integrity: " .. airbase_values.integrity .. ", " .. "airbase_values.supply: " ..  airbase_values.supply .. ", " .. "airbase_values.efficiency: " ..  ", " .. airbase_values.efficiency)
		end
    end
    log.debug("End " .. nameFunction)
    return airb_tab
end

-- Update oob_air number property considering airbase efficiency property
function UpdateOobAir()

    local nameFunction = "function UpdateOobAir(): "    
    log.debug("Start " .. nameFunction)    
	airbase_tab = nil
    airbase_tab = InitializeAirbaseTab()

    if not executeTest then -- delete this condition in operative version and insert UpdatesupplyTestIntegrity in a new line
        UpdateSupplyPlantIntegrity( supply_tab )
        UpdateSupplyLineIntegrity( supply_tab )
    end

	airbase_tab = UpdateAirbaseSupply( airbase_tab, supply_tab )
	airbase_tab = UpdateAirbaseIntegrity( airbase_tab )
	airbase_tab = UpdateAirbaseEfficiency( airbase_tab )

	for side, index in pairs(oob_air) do -- iterate oob_air for take aircraft type in an airbase

        for index_value, oob_value in pairs(index) do
			log.trace(nameFunction .. "airbase_tab is not nil")
			log.trace(nameFunction .. "oob_air value.base, type, rooster.ready: ", side, oob_value.base, oob_value.type, oob_value.roster.ready)
            local existed_airbase_name = oob_value.base .. "-" .. oob_value.name

            if airbase_tab[side][oob_value.base] then
                existed_airbase_name = oob_value.base
            end


			if existed_airbase_name then -- airbase name in oob_air exists in airbase_tab
				log.trace(nameFunction .. "airbase: " .. side .. " " .. existed_airbase_name .." exists in airbase_tab")

				if airbase_tab[side][existed_airbase_name].aircraft_types[oob_value.type] then --aircraft_type in oob_air exist in airbase_tab
					result = true
                    local percentage_efficiency_influence = nil

					if string.sub(oob_value.base, 1, 8) ~= "Reserves" then
                        percentage_efficiency_influence = DC_L_CONFIG.PERCENTAGE_EFFICIENCY_INFLUENCE_FOR_AIRBASES/100

                    else
                        percentage_efficiency_influence = DC_L_CONFIG.PERCENTAGE_EFFICIENCY_INFLUENCE_FOR_RESERVES/100
                    end

                    log.trace(nameFunction .. "old airbase oob_value.number: " .. oob_value.number)
                    log.trace(nameFunction .. "airbase_tab[side][airbase_name].efficiency: " .. airbase_tab[side][existed_airbase_name].efficiency)

                    local old_ready = oob_value.roster.ready
                    oob_value.roster.ready = math.floor( 0.5 + oob_value.roster.ready * ( 2^( airbase_tab[side][existed_airbase_name].efficiency * percentage_efficiency_influence ) - 1 ) ) -- min: 0 max = actual roster.ready
                    local increment_lost = old_ready - oob_value.roster.ready
                    oob_value.roster.lost = oob_value.roster.lost + increment_lost --min: 0, Max 
				
                else
					log.trace(nameFunction .. "oob_air aircraft type: " .. oob_value.type .. " --> not exist in airbase_tab")
					result = false
				end

			else
				log.trace(nameFunction .. "airbase: " .. side .. " " .. airbase_name .. " not exists in airbase_tab" )
				result = false
			end
        end
	end
    log.trace(nameFunction .. "-airbase_tab:\n--->: " .. inspect(airbase_tab).. " <----")
	log.trace(nameFunction .. "oob_air:\n--->: " .. inspect(oob_air).. " <----")
    SaveTabOnDisk( "airbase_tab", airbase_tab )
    SaveTabOnDisk( "supply_tab", supply_tab )
  
    log.debug("End " .. nameFunction)
    return result, airbase_tab, supply_tab
end

-- ============================================================					
-- Last point for coding logger functionality by Old_Boy ------		
-- ============================================================		

-- Save table on disk supply_tab.lua
function SaveTabOnDisk( table_name, table )

    local nameFunction = "function SaveTabOnDisk( table_name, table ): "    
    log.debug("Start " .. nameFunction)

    local tgt_str = table_name .. " = " .. TableSerialization(table, 0)						    --make a string
    local tgtFile = nil

    if executeTest then
      tgtFile = io.open("E://DCE/DCE_GW_1975/DCS_SavedGames_Path/Mods/tech/DCE/Missions/Campaigns/1975 Georgian War/Test/" .. table_name .. ".lua", "w")	--open supply_tab file
    else
      tgtFile = io.open("Active/" .. table_name .. ".lua", "w")
    end

    tgtFile:write(tgt_str)																		--save new data
    tgtFile:close()
    log.debug("End " .. nameFunction)    
end

-- return a string report of logistic status
function reportLogisticStatus(sup_tab, airb_tab)
    -- note: supply Line are defined in supply_tab and also in targetlist like targets
    local nameFunction = "function reportLogisticStatus(supply_tab): "    
    log.debug("Start " .. nameFunction)
    local s = "======================================== LOGISTIC ASSET REPORT ============================================\n"

    for sidepw, side_val in pairs( sup_tab ) do
        s = s .. "\n\n\n***************************************** side: " .. sidepw .. " **************************************************\n"

        for supply_plant_name, supply_plant_values in pairs( side_val ) do -- iteration of supply plants in supply_tab
            s = s .. "\n- supply plant: " .. supply_plant_name .. " - integrity: " .. supply_plant_values.integrity .. "\n"

            for supply_line_name, supply_line_values in pairs( supply_plant_values.supply_line_names ) do-- iteration of supply lines from a single supply_tab
                s = s .. "  -- supply line: " .. supply_line_name .. " - integrity: " .. supply_line_values.integrity .. "\n"
                local efficiency

                for stocked_name, _ in pairs(supply_line_values.airbase_supply) do

                    efficiency, _ = getAssetEfficiency(stocked_name, airb_tab)

                    if efficiency then
                        s = s .. "     --- stocked: " .. stocked_name .. " - efficiency: " .. efficiency .. "\n"
                    end
                end
            end
        end
    end
    s = s .. "\n\n====================================== END LOGISTIC ASSET REPORT ==========================================\n"
    log.debug("End " .. nameFunction)
	return s
end

-- return a string report of logistic status
function reportLogisticStatus2(sup_tab, airb_tab)
    -- note: supply Line are defined in supply_tab and also in targetlist like targets
    local nameFunction = "function reportLogisticStatus(supply_tab): "    
    log.debug("Start " .. nameFunction)
    local s = "======= LOGISTIC ASSET REPORT ======\n"

    for sidepw, side_val in pairs( sup_tab ) do
        s = s .. "\n\n\nside: " .. sidepw .. " ------------------------------------------------------------------------------------------\n"

        for supply_plant_name, supply_plant_values in pairs( side_val ) do -- iteration of supply plants in supply_tab
            s = s .. "\n\n supply plant: " .. supply_plant_name .. " - integrity: " .. supply_plant_values.integrity .. "\n"

            for supply_line_name, supply_line_values in pairs( supply_plant_values.supply_line_names ) do-- iteration of supply lines from a single supply_tab
                s = s .. "\n - supply line: " .. supply_line_name .. " - integrity: " .. supply_line_values.integrity .. "\n"
                local efficiency

                for resupplier_name, _ in pairs(supply_line_values.airbase_supply) do

                    efficiency, info = getAssetEfficiency(resupplier_name, airb_tab)

                    if efficiency then
                        s = s .. "          resuppliers: " .. resupplier_name .. " - efficiency: " .. efficiency .. ", units:  " .. info .. "\n"
                    end
                end
            end
        end
    end
    s = s .. "\n\n======= END LOGISTIC ASSET REPORT ======\n"
    log.debug("End " .. nameFunction)
	return s
end

-- return the efficiency of the asset_name
function getAssetEfficiency(asset_name, airb_tab)
    
    local nameFunction = "function getAssetEfficiency(asset_name, airb_tab): "    
    log.debug("End " .. nameFunction)
    local efficiency, info

	for side, side_val in pairs( airb_tab ) do

		for base, airbase_values in pairs( side_val ) do
            log.trace(nameFunction .. "airbase: " .. base)

            if base == asset_name then
                efficiency = airbase_values.efficiency

                for aircraft_type, group_name in pairs(airbase_values.aircraft_types) do
                    info = group_name .. " (" .. aircraft_type .. ")" 
                end
                log.trace(nameFunction .. "asset_name (" .. base .. ") found in airbase_tab, airbase_values.efficiency: " ..  airbase_values.efficiency)
                break
            end			
		end
    end
    log.debug("End " .. nameFunction)
    return efficiency, info
end


-- Test function

local function Test_InitializeAirbaseTab()

    --[[
    airbase_tab = {

        [base_1] = {
            ["aircraft_types"]
                [aircraft_1] true
                [aircraft_2] true
            ["efficiency"] 0.72 -- efficiency_<airbase> = ( damage_<airbase>  / 100 ) * energy_<airbase>; ( 0: min - 1: max )
            ["damage"] 0.8 -- same of targetlist.alive
            ["supply"] 0.9 -- energy_<airbase> = energy_line_efficiency_<airbase> *  energy_request_<airbase> * total_energy_production ;   (  0: min - 1: max  )

        --......
        [base_n]
            --......
        }
    }
    ]]

    local airbase_tab = InitializeAirbaseTab()
	--print( dump( airbase_tab ) .. "\n")
	local result = true

	for side_base, side_values in pairs( airbase_tab ) do --

        for base_name, base_values in pairs( side_values ) do --
			--print( base_values["efficiency"] .. ", " .. base_values["integrity"] .. ", " .. base_values["supply"] .. "\n" )

			if base_values["efficiency"] ~= 1 or base_values["integrity"] ~= 1 or base_values["supply"] ~= 1 then

				result = false
				break;
			end

			if not result then
				break
			end
		end
	end

	if result then
		print("-------------------------> Test_InitalizeAirbaseAndAircraft(): true\n")
        SaveTabOnDisk("airbase_tab",  airbase_tab)
	else
		print("-------------------------> Test_InitalizeAirbaseAndAircraft(): false\n")
	end


    --for side, sideval in pairs(airbase_tab) do
        --print("\nside: " .. side .." ========================== \n")
        --for base_name, base_values in pairs(sideval) do
            --print("\nbase: " .. base_name .." ----------------------------- \n")
            --print("efficiency: " .. base_values.efficiency ..",  " .. "integrity: " .. base_values.integrity ..",  " .. "supply: " .. base_values.supply)

            --for aircraft_type, value in pairs(base_values.aircraft_types) do
                --print("\naircraft type: " .. aircraft_type ..",  value: " .. tostring(value) .."\n--------------------------------------\n")
            --end
        --end
    --end
	return result
end

local function Test_UpdateSupplyPlantIntegrity()

    local result = false
	local _supply_tab = UpdateSupplyPlantIntegrity( deepcopy( supply_tab ) )
	--print( dump( supply_tab) .. "\n"  )

    if _supply_tab.blue['Sukhumi Airbase Strategics'].integrity == 1 and _supply_tab.red["Mineralnye-Vody Airbase"].integrity == 1 then
        result = true
    end

    print("-------------------------> Test function UpdateSupplyPlantIntegrity(): " .. tostring(result) .."\n")


    return result
end

local function Test_UpdateSupplyLineIntegrity()

    local result = false
    local supply_tab = {
        ['red'] = {
            ['Mineralnye-Vody Airbase'] = {
                ['supply_line_names'] = {
                    ['Bridge South Elhotovo MN 39'] = {
                        ['airbase_supply'] = {
                            ['Reserves'] = true,
                            ['Nalchik'] = true,
                            ['Beslan'] = true,
                            ['Mozdok'] = true,
                            ['Maykop-Khanskaya'] = true,
                            ['Mineralnye-Vody'] = true,
                            ['Sochi-Adler'] = true,
                        },
                        ['integrity'] = 0.25,
                    },
                    ['Rail Bridge SE Mayskiy MP 23'] = {
                        ['airbase_supply'] = {
                            ['Mozdok'] = true,
                            ['Sochi-Adler'] = true,
                            ['Beslan'] = true,
                        },
                        ['integrity'] = 0.5,
                    },                   
                },
                ['integrity'] = 0.6,
            },
            ['Prohladniy Depot MP 24'] = {
                ['supply_line_names'] = {
                    ['Bridge South Beslan MN 68'] = {
                        ['airbase_supply'] = {
                            ['Beslan'] = true,
                            ['Sochi-Adler'] = true,
                            ['Nalchik'] = true,
                        },
                        ['integrity'] = 0.25,
                    },
                    ['Bridge Alagir MN 36'] = {
                        ['airbase_supply'] = {
                            ['Mozdok'] = true,
                            ['Beslan'] = true,
                        },
                        ['integrity'] = 0.5,
                    },
                },
                ['integrity'] = 0.8,
            },
            ['101 EWR Site'] = {
                ['supply_line_names'] = {
                    ['Bridge SW Kardzhin MN 49'] = {
                        ['airbase_supply'] = {
                            ['Reserves'] = true,
                            ['Mozdok'] = true,
                            ['Beslan'] = true,
                            ['Mineralnye-Vody'] = true,
                            ['Sochi-Adler'] = true,
                        },
                        ['integrity'] = 0.25,
                    },
                    ['Russian Convoy 1'] = {
                        ['airbase_supply'] = {
                            ['Mozdok'] = true,
                            ['Mineralnye-Vody'] = true,
                        },
                        ['integrity'] = 0.5,
                    },
                },
                ['integrity'] = 1,
            },
        },
        ['blue'] = {
            ['Novyy Afon Train Station - FH57'] = {
                ['supply_line_names'] = {
                    ['Bridge Tagrskiy-FH08'] = {
                        ['airbase_supply'] = {
                            ['Kutaisi'] = true,
                            ['Batumi'] = true,
                        },
                        ['integrity'] = 0.25,
                    },
                    ['Bridge Nizh Armyanskoe Uschele-FH47'] = {
                        ['airbase_supply'] = {
                            ['Senaki-Kolkhi'] = true,
                            ['Reserves'] = true,
                            ['Vaziani'] = true,
                        },
                        ['integrity'] = 0.5,
                    },
                },
                ['integrity'] = 0.8,
            },
            ['Sukhumi Airbase Strategics'] = {
                ['supply_line_names'] = {
                    ['Rail Bridge Grebeshok-EH99'] = {
                        ['airbase_supply'] = {
                            ['Kutaisi'] = true,
                            ['Vaziani'] = true,
                        },
                        ['integrity'] = 0.25,
                    },
                    ['Bridge Anaklia-GG19'] = {
                        ['airbase_supply'] = {
                            ['Senaki-Kolkhi'] = true,
                            ['Batumi'] = true,
                            ['Reserves'] = true,
                        },
                        ['integrity'] = 0.5,
                    },
                },
                ['integrity'] = 0.4,
            },
            ['Tbilissi'] = {
                ['supply_line_names'] = {
                    ['Tbilissi'] = {
                        ['airbase_supply'] = {
                            ['TF-71'] = true,                            
                        },
                        ['integrity'] = 0.5,
                    },
                    ['LHA-Group'] = {
                        ['airbase_supply'] = {
                            ['TF-74'] = true,                            
                        },
                        ['integrity'] = 0.5,
                    },               
                },
                ['integrity'] = 0.9,
            },
        },
    }

    local _supply_tab = UpdateSupplyLineIntegrity( deepcopy( supply_tab ) )

	--print( dump( supply_tab) .. "\n"  )

    if _supply_tab.blue["Sukhumi Airbase Strategics"]["supply_line_names"]['Rail Bridge Grebeshok-EH99'].integrity == 1 and _supply_tab.blue["Sukhumi Airbase Strategics"]["supply_line_names"]['Bridge Anaklia-GG19'].integrity == 1 and
    _supply_tab.blue["Novyy Afon Train Station - FH57"]["supply_line_names"]['Bridge Tagrskiy-FH08'].integrity == 1 and
    _supply_tab.red["Mineralnye-Vody Airbase"]["supply_line_names"]['Bridge South Elhotovo MN 39'].integrity == 1 and _supply_tab.red["Mineralnye-Vody Airbase"]["supply_line_names"]['Rail Bridge SE Mayskiy MP 23'].integrity == 1 and
    _supply_tab.red["Prohladniy Depot MP 24"]["supply_line_names"]['Bridge South Beslan MN 68'].integrity == 1 then
        result = true
    end

    print("-------------------------> Test function UpdateSupplyLineIntegrity(): " .. tostring(result) .."\n")

    --print( dump( supply_tab ) )

    return result
end

local function Test_UpdateAirbaseSupply()

	--print( dump( supply_tab) .. "\n"  )
    -- watch: use Active/oob_air, so any modify should be cause test failure

    supply_tab = {
        ['red'] = {
            ['Mineralnye-Vody Airbase'] = {
                ['supply_line_names'] = {
                    ['Bridge South Elhotovo MN 39'] = {
                        ['airbase_supply'] = {
                            ['Reserves'] = true,
                            ['Nalchik'] = true,
                            ['Beslan'] = true,
                            ['Mozdok'] = true,
                            ['Maykop-Khanskaya'] = true,
                            ['Mineralnye-Vody'] = true,
                            ['Sochi-Adler'] = true,
                        },
                        ['integrity'] = 0.25,
                    },
                    ['Rail Bridge SE Mayskiy MP 23'] = {
                        ['airbase_supply'] = {
                            ['Mozdok'] = true,
                            ['Sochi-Adler'] = true,
                            ['Beslan'] = true,
                        },
                        ['integrity'] = 0.5,
                    },                   
                },
                ['integrity'] = 0.6,
            },
            ['Prohladniy Depot MP 24'] = {
                ['supply_line_names'] = {
                    ['Bridge South Beslan MN 68'] = {
                        ['airbase_supply'] = {
                            ['Beslan'] = true,
                            ['Sochi-Adler'] = true,
                            ['Nalchik'] = true,
                        },
                        ['integrity'] = 0.25,
                    },
                    ['Bridge Alagir MN 36'] = {
                        ['airbase_supply'] = {
                            ['Mozdok'] = true,
                            ['Beslan'] = true,
                        },
                        ['integrity'] = 0.5,
                    },
                },
                ['integrity'] = 0.8,
            },
            ['101 EWR Site'] = {
                ['supply_line_names'] = {
                    ['Bridge SW Kardzhin MN 49'] = {
                        ['airbase_supply'] = {
                            ['Reserves'] = true,
                            ['Mozdok'] = true,
                            ['Beslan'] = true,
                            ['Mineralnye-Vody'] = true,
                            ['Sochi-Adler'] = true,
                        },
                        ['integrity'] = 0.25,
                    },
                    ['Russian Convoy 1'] = {
                        ['airbase_supply'] = {
                            ['Mozdok'] = true,
                            ['Mineralnye-Vody'] = true,
                        },
                        ['integrity'] = 0.5,
                    },
                },
                ['integrity'] = 1,
            },
        },
        ['blue'] = {
            ['Novyy Afon Train Station - FH57'] = {
                ['supply_line_names'] = {
                    ['Bridge Tagrskiy-FH08'] = {
                        ['airbase_supply'] = {
                            ['Kutaisi'] = true,
                            ['Batumi'] = true,
                        },
                        ['integrity'] = 0.25,
                    },
                    ['Bridge Nizh Armyanskoe Uschele-FH47'] = {
                        ['airbase_supply'] = {
                            ['Senaki-Kolkhi'] = true,
                            ['Reserves'] = true,
                            ['Vaziani'] = true,
                        },
                        ['integrity'] = 0.5,
                    },
                },
                ['integrity'] = 0.8,
            },
            ['Sukhumi Airbase Strategics'] = {
                ['supply_line_names'] = {
                    ['Rail Bridge Grebeshok-EH99'] = {
                        ['airbase_supply'] = {
                            ['Kutaisi'] = true,
                            ['Vaziani'] = true,
                        },
                        ['integrity'] = 0.25,
                    },
                    ['Bridge Anaklia-GG19'] = {
                        ['airbase_supply'] = {
                            ['Senaki-Kolkhi'] = true,
                            ['Batumi'] = true,
                            ['Reserves'] = true,
                        },
                        ['integrity'] = 0.5,
                    },
                },
                ['integrity'] = 0.4,
            },
            ['Tbilissi'] = {
                ['supply_line_names'] = {
                    ['Tbilissi'] = {
                        ['airbase_supply'] = {
                            ['CVN-71 Theodore Roosevelt'] = true,                            
                        },
                        ['integrity'] = 0.5,
                    },
                    ['LHA-Group'] = {
                        ['airbase_supply'] = {
                            ['CVN-74 John C. Stennis'] = true,                            
                        },
                        ['integrity'] = 0.5,
                    },               
                },
                ['integrity'] = 0.9,
            },
        },
    }

    airbase_tab = nil
    airbase_tab = UpdateAirbaseSupply( InitializeAirbaseTab(), supply_tab )
    local result = false

    --[[
    print("airbase_tab.red.Beslan.supply: " .. airbase_tab.red.Beslan.supply .. ", airbase_tab.red.Mozdok.supply: " .. airbase_tab.red.Mozdok.supply
    .. ", airbase_tab.red.Nalchik.supply: " .. airbase_tab.red.Nalchik.supply .. ", airbase_tab.red['Mineralnye-Vody'].supply :"
    .. airbase_tab.red['Mineralnye-Vody'].supply .. ", airbase_tab.red['Maykop-Khanskaya'].supply :" .. airbase_tab.red['Maykop-Khanskaya'].supply
    .. ", airbase_tab.red['Sochi-Adler'].supply :" .. airbase_tab.red['Sochi-Adler'].supply .. ", airbase_tab.blue.Batumi.supply :"
    .. airbase_tab.blue.Batumi.supply .. ", airbase_tab.blue.Vaziani.supply :" .. airbase_tab.blue.Vaziani.supply .. ", airbase_tab.blue.Kutaisi: " .. airbase_tab.blue.Kutaisi.supply
    .. ", airbase_tab.blue.Reserves.supply: " .. airbase_tab.blue.Reserves.supply .. ", airbase_tab.red.Reserves.supply: "
    .. airbase_tab.red.Reserves.supply .. "\n")
    ]]

    if airbase_tab.red.Beslan.supply == 0.4 and airbase_tab.red.Mozdok.supply == 0.5 and airbase_tab.red.Nalchik.supply == 0.2 and
    airbase_tab.red['Mineralnye-Vody'].supply == 0.5 and airbase_tab.red['Maykop-Khanskaya'].supply == 0.15 and
    airbase_tab.red['Sochi-Adler'].supply == 0.3 and airbase_tab.blue.Batumi.supply == 0.2 and airbase_tab.blue.Vaziani.supply == 0.4
    and airbase_tab.blue.Kutaisi.supply == 0.2 and airbase_tab.blue["CVN-71 Theodore Roosevelt"].supply == 0.9  and airbase_tab.blue["CVN-74 John C. Stennis"].supply == 0.45 then -- and airbase_tab.red.Reserves.supply == 0.25 and airbase_tab.blue.Reserves.supply == 0.4
        result = true
    end
    print("airbase_tab.blue[\"TF-71\"] == 0.9  and airbase_tab.blue[\"TF-74\"] == 0.45", airbase_tab.blue["CVN-71 Theodore Roosevelt"].supply, airbase_tab.blue["CVN-74 John C. Stennis"].supply)
    print("-------------------------> Test_UpdateAirbaseSupply(): " .. tostring(result) .. "\n")

    --print( dump( airbase_tab) )

    return result


end

local function Test_UpdateAirbaseIntegrity()

	local result = true

    airbase_tab = {
        ['blue'] = {
            ['Reserves'] = {
                ['aircraft_types'] = {
                    ['KC-135'] = true,
                    ['F/A-18C'] = true,
                    ['KC135MPRS'] = true,
                    ['AJS37'] = true,
                    ['AV8BNA'] = true,
                    ['E-2C'] = true,
                    ['F-16C_50'] = true,
                    ['F-15C'] = true,
                    ['S-3B Tanker'] = true,
                    ['F-15E'] = true,
                    ['F-14B'] = true,
                    ['M-2000C'] = true,
                },
                ['supply'] = 0.5,
                ['efficiency'] = 0.5,
                ['integrity'] = 0.5,
            },
            ['LHA_Tarawa'] = {
                ['aircraft_types'] = {
                    ['AV8BNA'] = true,
                },
                ['supply'] = 0.5,
                ['efficiency'] = 0.5,
                ['integrity'] = 0.5,
            },
            ['CVN-71 Theodore Roosevelt'] = {
                ['aircraft_types'] = {
                    ['F-14B'] = true,
                    ['FA-18C_hornet'] = true,
                    ['S-3B Tanker'] = true,
                    ['E-2C'] = true,
                },
                ['supply'] = 0.5,
                ['efficiency'] = 0.5,
                ['integrity'] = 0.5,
            },
            ['Soganlug'] = {
                ['aircraft_types'] = {
                    ['F-117A'] = true,
                },
                ['supply'] = 0.5,
                ['efficiency'] = 0.5,
                ['integrity'] = 0.5,
            },
            ['Senaki-Kolkhi'] = {
                ['aircraft_types'] = {
                    ['F-16C_50'] = true,
                    ['KC-135'] = true,
                },
                ['supply'] = 0.5,
                ['efficiency'] = 0.5,
                ['integrity'] = 0.5,
            },
            ['Tbilissi-Lochini'] = {
                ['aircraft_types'] = {
                    ['KC135MPRS'] = true,
                },
                ['supply'] = 0.5,
                ['efficiency'] = 0.5,
                ['integrity'] = 0.5,
            },
            ['Kutaisi'] = {
                ['aircraft_types'] = {
                    ['E-3A'] = true,
                    ['M-2000C'] = true,
                },
                ['supply'] = 0.5,
                ['efficiency'] = 0.5,
                ['integrity'] = 0.5,
            },
            ['Vaziani'] = {
                ['aircraft_types'] = {
                    ['F-15C'] = true,
                    ['F-15E'] = true,
                },
                ['supply'] = 0.5,
                ['efficiency'] = 0.5,
                ['integrity'] = 0.5,
            },
            ['Sukhumi'] = {
                ['aircraft_types'] = {
                    ['AJS37'] = true,
                },
                ['supply'] = 0.5,
                ['efficiency'] = 0.5,
                ['integrity'] = 0.5,
            },
            ['Batumi'] = {
                ['aircraft_types'] = {
                    ['KC135MPRS'] = true,
                },
                ['supply'] = 0.5,
                ['efficiency'] = 0.5,
                ['integrity'] = 0.5,
            },
        },
        ['red'] = {
            ['Beslan'] = {
                ['aircraft_types'] = {
                    ['MiG-29A'] = true,
                    ['An-26B'] = true,
                },
                ['supply'] = 0.5,
                ['efficiency'] = 0.5,
                ['integrity'] = 0.5,
            },
            ['Reserves'] = {
                ['aircraft_types'] = {
                    ['Su-27'] = true,
                    ['Tu-22M3'] = true,
                    ['Su-24M'] = true,
                    ['MiG-29A'] = true,
                    ['Su-25T'] = true,
                },
                ['supply'] = 0.5,
                ['efficiency'] = 0.5,
                ['integrity'] = 0.5,
            },
            ['Mineralnye-Vody'] = {
                ['aircraft_types'] = {
                    ['Su-24M'] = true,
                    ['Su-27'] = true,
                },
                ['supply'] = 0.5,
                ['efficiency'] = 0.5,
                ['integrity'] = 0.5,
            },
            ['Maykop-Khanskaya'] = {
                ['aircraft_types'] = {
                    ['Tu-22M3'] = true,
                    ['Su-24M'] = true,
                },
                ['supply'] = 0.5,
                ['efficiency'] = 0.5,
                ['integrity'] = 0.5,
            },
            ['Nalchik'] = {
                ['aircraft_types'] = {
                    ['A-50'] = true,
                    ['MiG-29A'] = true,
                },
                ['supply'] = 0.5,
                ['efficiency'] = 0.5,
                ['integrity'] = 0.5,
            },
            ['Sochi-Adler'] = {
                ['aircraft_types'] = {
                    ['An-26B'] = true,
                },
                ['supply'] = 0.5,
                ['efficiency'] = 0.5,
                ['integrity'] = 0.5,
            },
            ['Mozdok'] = {
                ['aircraft_types'] = {
                    ['MiG-31'] = true,
                    ['MiG-29A'] = true,
                    ['Su-25T'] = true,
                },
                ['supply'] = 0.5,
                ['efficiency'] = 0.5,
                ['integrity'] = 0.5,
            },
        },
    }

	airbase_tab = UpdateAirbaseIntegrity( airbase_tab )

    for side, side_values in pairs(targetlist) do
        local side_base = "red"

        if side == "red" then
            side_base = "blue"
        end

        for target_name, target_values in pairs(side_values) do

            if airbase_tab[side_base][target_name] and target_values.integrity ~= 1 then
                print("wrong integrity value in airbase_tab airbase: " .. target_name .. ", integrity: " .. target_values.integrity .. "\n")
				result = false
				break
			end
        end
    end


	if result then
		print("-------------------------> Test_UpdateAirbaseIntegrity(): true" .. "\n")

	else
		print("-------------------------> Test_UpdateAirbaseIntegrity(): false" .. "\n")

	end

    return result

end

local function Test_UpdateAirbaseEfficiency()

	--local airbase_tab = InitializeAirbaseTab()
	--print( dump( airbase_tab).."\n" )
    supply_tab = {
        ['red'] = {
            ['Mineralnye-Vody Airbase'] = {
                ['supply_line_names'] = {
                    ['Bridge South Elhotovo MN 39'] = {
                        ['airbase_supply'] = {
                            ['Reserves'] = true,
                            ['Nalchik'] = true,
                            ['Beslan'] = true,
                            ['Mozdok'] = true,
                            ['Maykop-Khanskaya'] = true,
                            ['Mineralnye-Vody'] = true,
                            ['Sochi-Adler'] = true,
                        },
                        ['integrity'] = 0.25,
                    },
                    ['Rail Bridge SE Mayskiy MP 23'] = {
                        ['airbase_supply'] = {
                            ['Mozdok'] = true,
                            ['Sochi-Adler'] = true,
                            ['Beslan'] = true,
                        },
                        ['integrity'] = 0.5,
                    },
                },
                ['integrity'] = 0.6,
            },
            ['Prohladniy Depot MP 24'] = {
                ['supply_line_names'] = {
                    ['Bridge South Beslan MN 68'] = {
                        ['airbase_supply'] = {
                            ['Beslan'] = true,
                            ['Sochi-Adler'] = true,
                            ['Nalchik'] = true,
                        },
                        ['integrity'] = 0.25,
                    },
                    ['Bridge Alagir MN 36'] = {
                        ['airbase_supply'] = {
                            ['Mozdok'] = true,
                            ['Beslan'] = true,
                        },
                        ['integrity'] = 0.5,
                    },
                },
                ['integrity'] = 0.8,
            },
            ['101 EWR Site'] = {
                ['supply_line_names'] = {
                    ['Bridge SW Kardzhin MN 49'] = {
                        ['airbase_supply'] = {
                            ['Reserves'] = true,
                            ['Mozdok'] = true,
                            ['Beslan'] = true,
                            ['Mineralnye-Vody'] = true,
                            ['Sochi-Adler'] = true,
                        },
                        ['integrity'] = 0.25,
                    },
                    ['Russian Convoy 1'] = {
                        ['airbase_supply'] = {
                            ['Mozdok'] = true,
                            ['Mineralnye-Vody'] = true,
                        },
                        ['integrity'] = 0.5,
                    },
                },
                ['integrity'] = 1,
            },
        },
        ['blue'] = {
            ['Novyy Afon Train Station - FH57'] = {
                ['supply_line_names'] = {
                    ['Bridge Tagrskiy-FH08'] = {
                        ['airbase_supply'] = {
                            ['Kutaisi'] = true,
                            ['Batumi'] = true,
                        },
                        ['integrity'] = 0.25,
                    },
                    ['Bridge Nizh Armyanskoe Uschele-FH47'] = {
                        ['airbase_supply'] = {
                            ['Senaki-Kolkhi'] = true,
                            ['Reserves'] = true,
                            ['Vaziani'] = true,
                        },
                        ['integrity'] = 0.5,
                    },
                },
                ['integrity'] = 0.8,
            },
            ['Sukhumi Airbase Strategics'] = {
                ['supply_line_names'] = {
                    ['Rail Bridge Grebeshok-EH99'] = {
                        ['airbase_supply'] = {
                            ['Kutaisi'] = true,
                            ['Vaziani'] = true,
                        },
                        ['integrity'] = 0.25,
                    },
                    ['Bridge Anaklia-GG19'] = {
                        ['airbase_supply'] = {
                            ['Senaki-Kolkhi'] = true,
                            ['Batumi'] = true,
                            ['Reserves'] = true,
                        },
                        ['integrity'] = 0.5,
                    },
                },
                ['integrity'] = 0.4,
            },
        },
    }

    airbase_tab = nil

    airbase_tab = InitializeAirbaseTab()
    --dofile("E://DCE/DCE_GW_1975/DCS_SavedGames_Path/Mods/tech/DCE/Missions/Campaigns/1975 Georgian War/Init/supply_tab_init.lua")
	airbase_tab = UpdateAirbaseSupply( airbase_tab, supply_tab )
	--print( dump( airbase_tab).."\n" )

	airbase_tab = UpdateAirbaseEfficiency( airbase_tab )
    local result = false

      --[[
    print("airbase_tab.red.Beslan.supply: " .. airbase_tab.red.Beslan.supply .. ", airbase_tab.red.Mozdok.supply: " .. airbase_tab.red.Mozdok.supply
    .. ", airbase_tab.red.Nalchik.supply: " .. airbase_tab.red.Nalchik.supply .. ", airbase_tab.red['Mineralnye-Vody'].supply :"
    .. airbase_tab.red['Mineralnye-Vody'].supply .. ", airbase_tab.red['Maykop-Khanskaya'].supply :" .. airbase_tab.red['Maykop-Khanskaya'].supply
    .. ", airbase_tab.red['Sochi-Adler'].supply :" .. airbase_tab.red['Sochi-Adler'].supply .. ", airbase_tab.blue.Batumi.supply :"
    .. airbase_tab.blue.Batumi.supply .. ", airbase_tab.blue.Vaziani.supply :" .. airbase_tab.blue.Vaziani.supply .. ", airbase_tab.blue.Kutaisi: " .. airbase_tab.blue.Kutaisi.supply
    .. ", airbase_tab.blue.Reserves.supply: " .. airbase_tab.blue.Reserves.supply .. ", airbase_tab.red.Reserves.supply: "
    .. airbase_tab.red.Reserves.supply .. "\n")
    ]]

    if airbase_tab.red.Beslan.supply == 0.4 and airbase_tab.red.Mozdok.supply == 0.5 and airbase_tab.red.Nalchik.supply == 0.2 and
    airbase_tab.red['Mineralnye-Vody'].supply == 0.5 and airbase_tab.red['Maykop-Khanskaya'].supply == 0.15 and
    airbase_tab.red['Sochi-Adler'].supply == 0.3 and airbase_tab.blue.Batumi.supply == 0.2 and airbase_tab.blue.Vaziani.supply == 0.4 then
        result = true
    end

    print("-------------------------> Test_UpdateAirbaseEfficiency(): " .. tostring(result) .. "\n")

    --print( dump( airbase_tab) )
    return result



end

local function Test_UpdateOobAir()

    --[[

    NOTE:
    In UpdateOobAir() needed: local percentage_efficiency_effect_for_airbases = 100, local percentage_efficiency_effect_for_resupplies = 100

    ]]

    local result = true
    dofile("E://DCE/DCE_GW_1975/DCS_SavedGames_Path/Mods/tech/DCE/Missions/Campaigns/1975 Georgian War/Test/oob_air.lua")
    oob_air_old = deepcopy ( oob_air )

    supply_tab = {
        ['red'] = {
            ['Mineralnye-Vody Airbase'] = {
                ['supply_line_names'] = {
                    ['Bridge South Elhotovo MN 39'] = {
                        ['airbase_supply'] = {
                            ['Reserves'] = true,
                            ['Nalchik'] = true,
                            ['Beslan'] = true,
                            ['Mozdok'] = true,
                            ['Maykop-Khanskaya'] = true,
                            ['Mineralnye-Vody'] = true,
                            ['Sochi-Adler'] = true,
                        },
                        ['integrity'] = 0.25,
                    },
                    ['Rail Bridge SE Mayskiy MP 23'] = {
                        ['airbase_supply'] = {
                            ['Mozdok'] = true,
                            ['Sochi-Adler'] = true,
                            ['Beslan'] = true,
                        },
                        ['integrity'] = 0.5,
                    },
                },
                ['integrity'] = 0.6,
            },
            ['Prohladniy Depot MP 24'] = {
                ['supply_line_names'] = {
                    ['Bridge South Beslan MN 68'] = {
                        ['airbase_supply'] = {
                            ['Beslan'] = true,
                            ['Sochi-Adler'] = true,
                            ['Nalchik'] = true,
                        },
                        ['integrity'] = 0.25,
                    },
                    ['Bridge Alagir MN 36'] = {
                        ['airbase_supply'] = {
                            ['Mozdok'] = true,
                            ['Beslan'] = true,
                        },
                        ['integrity'] = 0.5,
                    },
                },
                ['integrity'] = 0.8,
            },
            ['101 EWR Site'] = {
                ['supply_line_names'] = {
                    ['Bridge SW Kardzhin MN 49'] = {
                        ['airbase_supply'] = {
                            ['Reserves'] = true,
                            ['Mozdok'] = true,
                            ['Beslan'] = true,
                            ['Mineralnye-Vody'] = true,
                            ['Sochi-Adler'] = true,
                        },
                        ['integrity'] = 0.25,
                    },
                    ['Russian Convoy 1'] = {
                        ['airbase_supply'] = {
                            ['Mozdok'] = true,
                            ['Mineralnye-Vody'] = true,
                        },
                        ['integrity'] = 0.5,
                    },
                },
                ['integrity'] = 1,
            },
        },
        ['blue'] = {
            ['Novyy Afon Train Station - FH57'] = {
                ['supply_line_names'] = {
                    ['Bridge Tagrskiy-FH08'] = {
                        ['airbase_supply'] = {
                            ['Kutaisi'] = true,
                            ['Batumi'] = true,
                        },
                        ['integrity'] = 0.25,
                    },
                    ['Bridge Nizh Armyanskoe Uschele-FH47'] = {
                        ['airbase_supply'] = {
                            ['Senaki-Kolkhi'] = true,
                            ['Reserves'] = true,
                            ['Vaziani'] = true,
                        },
                        ['integrity'] = 0.5,
                    },
                },
                ['integrity'] = 0.8,
            },
            ['Sukhumi Airbase Strategics'] = {
                ['supply_line_names'] = {
                    ['Rail Bridge Grebeshok-EH99'] = {
                        ['airbase_supply'] = {
                            ['Kutaisi'] = true,
                            ['Vaziani'] = true,
                        },
                        ['integrity'] = 0.25,
                    },
                    ['Bridge Anaklia-GG19'] = {
                        ['airbase_supply'] = {
                            ['Senaki-Kolkhi'] = true,
                            ['Batumi'] = true,
                            ['Reserves'] = true,
                        },
                        ['integrity'] = 0.5,
                    },
                },
                ['integrity'] = 0.4,
            },
        },
    }

    UpdateOobAir()


	for side, index in pairs(oob_air) do

        for index_value, oob_value in pairs(index) do
            --print("oob_air value: ", side, oob_value.base, oob_value.type, oob_value.roster.ready )
            --print("old oob_air value: ", side, oob_air_old[side][index_value].base, oob_air_old[side][index_value].type, oob_air_old[side][index_value].roster.ready )

            if oob_value.base == "Mozdok" or oob_value.base == "Mineralnye-Vody"  then
                result = result and ( oob_value.roster.ready == math.floor( 0.5 + oob_air_old[side][index_value].roster.ready * ( 2^( 0.5 ) - 1  ) ) )

            elseif oob_value.base == "Beslan"  or oob_value.base == "Vaziani" or oob_value.base == "Senaki-Kolkhi" then
                result = result and ( oob_value.roster.ready == math.floor( 0.5 + oob_air_old[side][index_value].roster.ready * ( 2^( 0.4 ) - 1  ) ) )

            elseif oob_value.base == "Sochi-Adler"  then
                result = result and ( oob_value.roster.ready == math.floor( 0.5 + oob_air_old[side][index_value].roster.ready * ( 2^( 0.3 ) - 1  ) ) )

            elseif oob_value.base == "Nalchik" or oob_value.base == "Kutaisi" or oob_value.base == "Batumi" then
                result = result and ( oob_value.roster.ready == math.floor( 0.5 + oob_air_old[side][index_value].roster.ready * ( 2^( 0.2 ) - 1  ) ) )

            elseif oob_value.base == "Maykop-Khanskaya"  then
                result = result and ( oob_value.roster.ready == math.floor( 0.5 + oob_air_old[side][index_value].roster.ready * ( 2^( 0.15 ) - 1  ) ) )

            end
        end
	end

    --print("-------------------------> FIRST Test_UpdateOobAir(): " .. tostring(result) .. "\n")
    supply_tab = {
        ['red'] = {
            ['Mineralnye-Vody Airbase'] = {
                ['supply_line_names'] = {
                    ['Bridge South Elhotovo MN 39'] = {
                        ['airbase_supply'] = {
                            ['Reserves'] = true,
                            ['Nalchik'] = true,
                            ['Beslan'] = true,
                            ['Mozdok'] = true,
                            ['Maykop-Khanskaya'] = true,
                            ['Mineralnye-Vody'] = true,
                            ['Sochi-Adler'] = true,
                        },
                        ['integrity'] = 0.25,
                    },
                    ['Rail Bridge SE Mayskiy MP 23'] = {
                        ['airbase_supply'] = {
                            ['Mozdok'] = true,
                            ['Sochi-Adler'] = true,
                            ['Beslan'] = true,
                        },
                        ['integrity'] = 0.5,
                    },
                },
                ['integrity'] = 0.6,
            },
            ['Prohladniy Depot MP 24'] = {
                ['supply_line_names'] = {
                    ['Bridge South Beslan MN 68'] = {
                        ['airbase_supply'] = {
                            ['Beslan'] = true,
                            ['Sochi-Adler'] = true,
                            ['Nalchik'] = true,
                        },
                        ['integrity'] = 0.25,
                    },
                    ['Bridge Alagir MN 36'] = {
                        ['airbase_supply'] = {
                            ['Mozdok'] = true,
                            ['Beslan'] = true,
                        },
                        ['integrity'] = 0.5,
                    },
                },
                ['integrity'] = 0.8,
            },
            ['101 EWR Site'] = {
                ['supply_line_names'] = {
                    ['Bridge SW Kardzhin MN 49'] = {
                        ['airbase_supply'] = {
                            ['Reserves'] = true,
                            ['Mozdok'] = true,
                            ['Beslan'] = true,
                            ['Mineralnye-Vody'] = true,
                            ['Sochi-Adler'] = true,
                        },
                        ['integrity'] = 0.25,
                    },
                    ['Russian Convoy 1'] = {
                        ['airbase_supply'] = {
                            ['Mozdok'] = true,
                            ['Mineralnye-Vody'] = true,
                        },
                        ['integrity'] = 0.5,
                    },
                },
                ['integrity'] = 1,
            },
        },
        ['blue'] = {
            ['Novyy Afon Train Station - FH57'] = {
                ['supply_line_names'] = {
                    ['Bridge Tagrskiy-FH08'] = {
                        ['airbase_supply'] = {
                            ['Kutaisi'] = true,
                            ['Batumi'] = true,
                        },
                        ['integrity'] = 0.25,
                    },
                    ['Bridge Nizh Armyanskoe Uschele-FH47'] = {
                        ['airbase_supply'] = {
                            ['Senaki-Kolkhi'] = true,
                            ['Reserves'] = true,
                            ['Vaziani'] = true,
                        },
                        ['integrity'] = 0.5,
                    },
                },
                ['integrity'] = 0.8,
            },
            ['Sukhumi Airbase Strategics'] = {
                ['supply_line_names'] = {
                    ['Rail Bridge Grebeshok-EH99'] = {
                        ['airbase_supply'] = {
                            ['Kutaisi'] = true,
                            ['Vaziani'] = true,
                        },
                        ['integrity'] = 0.25,
                    },
                    ['Bridge Anaklia-GG19'] = {
                        ['airbase_supply'] = {
                            ['Senaki-Kolkhi'] = true,
                            ['Batumi'] = true,
                            ['Reserves'] = true,
                        },
                        ['integrity'] = 0.5,
                    },
                },
                ['integrity'] = 0.4,
            },
        },
    }
    targetlist.blue["Mozdok Airbase"].alive = 50
    targetlist.blue["Beslan Airbase"].alive = 50
    targetlist.blue["Nalchik Airbase"].alive = 50
    targetlist.red["Kutaisi Airbase"].alive = 50
    targetlist.red["Batumi Airbase"].alive = 50
    oob_air = deepcopy(oob_air_old)
    UpdateOobAir()

	for side, index in pairs(oob_air) do

        for index_value, oob_value in pairs(index) do
            --print("oob_air value: ", side, oob_value.base, oob_value.type, oob_value.roster.ready, "\n" )
            --print("old oob_air value: ", side, oob_air_old[side][index_value].base, oob_air_old[side][index_value].type, oob_air_old[side][index_value].roster.ready, "\n" )
            --rispetto il test precedente ho eliminato le airbase non presenti in targetlist che, pertanto, vengono escluse dall'aggiornamento dell'integrity in airbase_tab
            --effettuato in base alle info presenti in targetlist. Nel precedente funzionava perche il calcolo considera i valori di integrity=1(alive=100)

            if oob_value.base == "Mozdok"  then
                result = result and ( oob_value.roster.ready == math.floor( 0.5 + oob_air_old[side][index_value].roster.ready * ( 2^( 0.25 ) - 1  ) ) )
                --print( "Test_UpdateOobAir() - II Step oob_value.roster.ready", oob_value.roster.ready, math.floor( 0.5 + oob_air_old[side][index_value].roster.ready * ( 2^( 0.25 ) - 1  ) ) )

            elseif oob_value.base == "Beslan" then
                result = result and ( oob_value.roster.ready == math.floor( 0.5 + oob_air_old[side][index_value].roster.ready * ( 2^( 0.2 ) - 1  ) ) )
                --print( "Test_UpdateOobAir() - II Step oob_value.roster.ready", oob_value.roster.ready, math.floor( 0.5 + oob_air_old[side][index_value].roster.ready * ( 2^( 0.2 ) - 1  ) ) )

            elseif oob_value.base == "Nalchik" or oob_value.base == "Kutaisi" or oob_value.base == "Batumi" then
                result = result and ( oob_value.roster.ready == math.floor( 0.5 + oob_air_old[side][index_value].roster.ready * ( 2^( 0.1 ) - 1  ) ) )
                --print( "Test_UpdateOobAir() - II Step oob_value.roster.ready", oob_value.roster.ready, math.floor( 0.5 + oob_air_old[side][index_value].roster.ready * ( 2^( 0.1 ) - 1  ) ) )
            end
        end
	end

    print("-------------------------> Test_UpdateOobAir(): " .. tostring(result) .. "\n")
    return result
end

local function Test_SaveTabOnDisk()

    supply_tab_test = {
        ['red'] = {
            ['Prohladniy Depot MP 24'] = {
                ['integrity'] = 1,
                ['supply_line_names'] = {
                    ['Bridge Alagir MN 36'] = {
                        ['integrity'] = 1,
                        ['airbase_supply'] = {
                            ['Beslan'] = true,  -- Beslan dovrebbe prendere 0.8*0.5=0.4 efficiency
                            ['Mozdok'] = true,
                        },
                    },
                    ['Bridge South Beslan MN 68'] = {
                        ['integrity'] = 1,
                        ['airbase_supply'] = {
                            ['Beslan'] = true,
                            ['Nalchik'] = true, -- Nalchik dovrebbe prendere 0.8*0.25=0.2 efficiency
                            ['Sochi-Adler'] = true,
                        },
                    },
                },
            },
            ['Mineralnye-Vody Airbase'] = {
                ['integrity'] = 1,
                ['supply_line_names'] = {
                    ['Rail Bridge SE Mayskiy MP 23'] = {
                        ['integrity'] = 1,
                        ['airbase_supply'] = {
                            ['Mozdok'] = true,
                            ['Sochi-Adler'] = true,  -- Sochi-Adler dovrebbe prendere 0.6*0.5=0.3 efficiency
                            ['Beslan'] = true,
                        },
                    },
                    ['Bridge South Elhotovo MN 39'] = {
                        ['integrity'] = 1,
                        ['airbase_supply'] = {
                            ['Reserves'] = true,
                            ['Sochi-Adler'] = true,
                            ['Maykop-Khanskaya'] = true, -- Maykop-Khanskaya dovrebbe prendere 0.6*0.25=0.15 efficiency
                            ['Nalchik'] = true,
                            ['Mozdok'] = true,
                            ['Beslan'] = true,
                            ['Mineralnye-Vody'] = true,
                        },
                    },
                },
            },
            ['101 EWR Site'] = {
                ['integrity'] = 1,
                ['supply_line_names'] = {
                    ['Russian Convoy 1'] = {
                        ['integrity'] = 1,
                        ['airbase_supply'] = {
                            ['Mozdok'] = true, -- Mozdok dovrebbe prendere 1*0.5=0.5 efficiency
                            ['Mineralnye-Vody'] = true,-- Mineralnye-Vody dovrebbe prendere 1*0.5=0.5 efficiency
                        },
                    },
                    ['Bridge SW Kardzhin MN 49'] = {
                        ['integrity'] = 1,
                        ['airbase_supply'] = {
                            ['Reserves'] = true, -- Reserves dovrebbe prendere 1*0.25=0.25 efficiency
                            ['Sochi-Adler'] = true,
                            ['Mineralnye-Vody'] = true,
                            ['Beslan'] = true,
                            ['Mozdok'] = true,
                        },
                    },
                },
            },
        },
        ['blue'] = {
            ['Sukhumi Airbase Strategics'] = {
                ['integrity'] = 1,
                ['supply_line_names'] = {
                    ['Rail Bridge Grebeshok-EH99'] = {
                        ['integrity'] = 1,
                        ['airbase_supply'] = {
                            ['Kutaisi'] = true,
                            ['Vaziani'] = true,
                        },
                    },
                    ['Bridge Anaklia-GG19'] = {
                        ['integrity'] = 1,
                        ['airbase_supply'] = {
                            ['Senaki-Kolkhi'] = true,
                            ['Batumi'] = true,
                            ['Reserves'] = true,
                        },
                    },
                },
            },
            ['Novyy Afon Train Station - FH57'] = {
                ['integrity'] = 1,
                ['supply_line_names'] = {
                    ['Bridge Tagrskiy-FH08'] = {
                        ['integrity'] = 1,
                        ['airbase_supply'] = {
                            ['Kutaisi'] = true,
                            ['Batumi'] = true,
                        },
                    },
                    ['Bridge Nizh Armyanskoe Uschele-FH47'] = {
                        ['integrity'] = 1,
                        ['airbase_supply'] = {
                            ['Vaziani'] = true,
                            ['Senaki-Kolkhi'] = true,
                            ['Reserves'] = true,
                        },
                    },
                },
            },
        },
    }

    SaveTabOnDisk( "supply_tab_test", supply_tab_test )
    supply_tab_test = nil
    dofile("E://DCE/DCE_GW_1975/DCS_SavedGames_Path/Mods/tech/DCE/Missions/Campaigns/1975 Georgian War/Test/supply_tab_test.lua")
    local result = supply_tab_test.blue["Novyy Afon Train Station - FH57"].integrity == 1
    supply_tab_test = {

        ["red"] = {

            ["Prohladniy Depot MP 24"] = { -- supply plant
                integrity = 0.8, -- integrity (property alive in targetlist) of supply plant
                ["supply_line_names"] = { -- table of supply line supplyed of supply plant
                    ["Bridge Alagir MN 36"] = { -- supply line n.1
                        integrity = 0.5, -- integrity (property alive in targetlist) of supply line
                        ["airbase_supply"] = {  -- airbases supplyed from this supply line n.1
                            ["Beslan"] = true,
                            ["Reserves"] = true,
                            ["Mozdok"] = true
                        }
                    },
                    ["Bridge South Beslan MN 68"] = { -- supply line n.2
                        integrity = 0.25,
                        ["airbase_supply"] = { -- airbases supplyed from this supply line n.2
                            ["Nalchik"] = true,
                            ["Mineralnye-Vody"] = true
                        }
                    }
                }
            },
            ["Mineralnye-Vody Airbase"] = { -- another supply plant and
                integrity = 0.4,
                ["supply_line_names"] = {
                    ["Rail Bridge SE Mayskiy MP 23"] = {
                        integrity = 0.5,
                        ["airbase_supply"] = {
                            ["Sochi-Adler"] = true,
                            ["Reserves"] = true
                        }
                    },
                    ["Bridge South Elhotovo MN 39"] = {
                        integrity = 0.25,
                        ["airbase_supply"] = {
                            ["Mineralnye-Vody"] = true,
                            ["Sochi-Adler"] = true,
                            ["Maykop-Khanskaya"] = true,
                            ["Reserves"] = true
                        }
                    }
                }

            }
        },
        ["blue"] = {

            ["Novyy Afon Train Station - FH57"] = {
                integrity = 0.8,
                ["supply_line_names"] = {
                    ["Bridge Nizh Armyanskoe Uschele-FH47"] = {
                        integrity = 0.5,
                        ["airbase_supply"] = {
                            ["Senaki-Kolkhi"] = true,
                            ["Vaziani"] = true,
                            ["Reserves"] = true
                        }
                    },
                    ["Bridge Tagrskiy-FH08"] = {
                        integrity = 0.25,
                        ["airbase_supply"] = {
                            ["Kutaisi"] = true,
                            ["Batumi"] = true
                        }
                    }
                }
            },
            ["Sukhumi Airbase Strategics"] = {
                integrity = 0.4,
                ["supply_line_names"] = {
                    ["Bridge Anaklia-GG19"] = {
                        integrity = 0.5,
                        ["airbase_supply"] = {
                            ["Batumi"] = true,
                            ["Senaki-Kolkhi"] = true,
                            ["Reserves"] = true
                        }
                    },
                    ["Rail Bridge Grebeshok-EH99"] = {
                        integrity = 0.25,
                        ["airbase_supply"] = {
                            ["Kutaisi"] = true,
                            ["Vaziani"] = true
                        }
                    }
                }

            }
        }
    }
    SaveTabOnDisk( "supply_tab_test", supply_tab_test )
    supply_tab_test = nil
    dofile("E://DCE/DCE_GW_1975/DCS_SavedGames_Path/Mods/tech/DCE/Missions/Campaigns/1975 Georgian War/Test/supply_tab_test.lua")
    result = result and ( supply_tab_test.blue["Novyy Afon Train Station - FH57"].integrity == 0.8 )
    print("-------------------------> Test_SaveTabOnDisk(): " .. tostring(result) .. "\n")
    return result

end

local function Test_CopySupplyTab()

    supply_tab = {
        ['red'] = {
            ['Prohladniy Depot MP 24'] = {
                ['integrity'] = 1,
                ['supply_line_names'] = {
                    ['Bridge Alagir MN 36'] = {
                        ['integrity'] = 1,
                        ['airbase_supply'] = {
                            ['Beslan'] = true,  -- Beslan dovrebbe prendere 0.8*0.5=0.4 efficiency
                            ['Mozdok'] = true,
                        },
                    },
                    ['Bridge South Beslan MN 68'] = {
                        ['integrity'] = 1,
                        ['airbase_supply'] = {
                            ['Beslan'] = true,
                            ['Nalchik'] = true, -- Nalchik dovrebbe prendere 0.8*0.25=0.2 efficiency
                            ['Sochi-Adler'] = true,
                        },
                    },
                },
            },
            ['Mineralnye-Vody Airbase'] = {
                ['integrity'] = 1,
                ['supply_line_names'] = {
                    ['Rail Bridge SE Mayskiy MP 23'] = {
                        ['integrity'] = 1,
                        ['airbase_supply'] = {
                            ['Mozdok'] = true,
                            ['Sochi-Adler'] = true,  -- Sochi-Adler dovrebbe prendere 0.6*0.5=0.3 efficiency
                            ['Beslan'] = true,
                        },
                    },
                    ['Bridge South Elhotovo MN 39'] = {
                        ['integrity'] = 1,
                        ['airbase_supply'] = {
                            ['Reserves'] = true,
                            ['Sochi-Adler'] = true,
                            ['Maykop-Khanskaya'] = true, -- Maykop-Khanskaya dovrebbe prendere 0.6*0.25=0.15 efficiency
                            ['Nalchik'] = true,
                            ['Mozdok'] = true,
                            ['Beslan'] = true,
                            ['Mineralnye-Vody'] = true,
                        },
                    },
                },
            },
            ['101 EWR Site'] = {
                ['integrity'] = 1,
                ['supply_line_names'] = {
                    ['Russian Convoy 1'] = {
                        ['integrity'] = 1,
                        ['airbase_supply'] = {
                            ['Mozdok'] = true, -- Mozdok dovrebbe prendere 1*0.5=0.5 efficiency
                            ['Mineralnye-Vody'] = true,-- Mineralnye-Vody dovrebbe prendere 1*0.5=0.5 efficiency
                        },
                    },
                    ['Bridge SW Kardzhin MN 49'] = {
                        ['integrity'] = 1,
                        ['airbase_supply'] = {
                            ['Reserves'] = true, -- Reserves dovrebbe prendere 1*0.25=0.25 efficiency
                            ['Sochi-Adler'] = true,
                            ['Mineralnye-Vody'] = true,
                            ['Beslan'] = true,
                            ['Mozdok'] = true,
                        },
                    },
                },
            },
        },
        ['blue'] = {
            ['Sukhumi Airbase Strategics'] = {
                ['integrity'] = 1,
                ['supply_line_names'] = {
                    ['Rail Bridge Grebeshok-EH99'] = {
                        ['integrity'] = 1,
                        ['airbase_supply'] = {
                            ['Kutaisi'] = true,
                            ['Vaziani'] = true,
                        },
                    },
                    ['Bridge Anaklia-GG19'] = {
                        ['integrity'] = 1,
                        ['airbase_supply'] = {
                            ['Senaki-Kolkhi'] = true,
                            ['Batumi'] = true,
                            ['Reserves'] = true,
                        },
                    },
                },
            },
            ['Novyy Afon Train Station - FH57'] = {
                ['integrity'] = 0.8,
                ['supply_line_names'] = {
                    ['Bridge Tagrskiy-FH08'] = {
                        ['integrity'] = 1,
                        ['airbase_supply'] = {
                            ['Kutaisi'] = true,
                            ['Batumi'] = true,
                        },
                    },
                    ['Bridge Nizh Armyanskoe Uschele-FH47'] = {
                        ['integrity'] = 1,
                        ['airbase_supply'] = {
                            ['Vaziani'] = true,
                            ['Senaki-Kolkhi'] = true,
                            ['Reserves'] = true,
                        },
                    },
                },
            },
        },
    }

    SaveTabOnDisk( "supply_tab_test", supply_tab )
    supply_tab = supply_tab_test
    dofile("E://DCE/DCE_GW_1975/DCS_SavedGames_Path/Mods/tech/DCE/Missions/Campaigns/1975 Georgian War/Test/supply_tab_test.lua")
    local result = supply_tab.blue["Novyy Afon Train Station - FH57"].integrity == 0.8
    supply_tab = nil
    copySupplyTab()
    local result = supply_tab.blue["Novyy Afon Train Station - FH57"].integrity == 1
    print("-------------------------> Test_CopySupplyTab(): " .. tostring(result) .. "\n")
    return result

end


local function executeAllTest()

	print("\nExecuting tests" .. "\n")

    local result = Test_InitializeAirbaseTab() and Test_UpdateSupplyPlantIntegrity()
    and Test_UpdateSupplyLineIntegrity() and Test_UpdateAirbaseSupply() and Test_UpdateAirbaseIntegrity()
    and Test_UpdateAirbaseEfficiency()and Test_UpdateOobAir() and Test_SaveTabOnDisk() and Test_CopySupplyTab() 
    
    print("-------------------------> executeAllTest(): " .. tostring(result) .. "\n")

    return result
end

if executeTest then
	executeAllTest()
end

--[[

oob_air che contiene le informazioni sui resupply per airbases e reserves viene salvato su disco in MAIN_NextMission.lua
molto probabilmente il valore number non viene mai aggiornato in quanto costituisce il riferimento per calcolare se non ci
sono più aerei disponibili utilizzando i dati in [rooster]: lost, damaged e ready.
L'aggiornamento dei dati in [rooster]: lost, damaged e ready, viene fatto in DEBRIEF_StatsEvaluation.lua alla riga 149 "--oob loss update for crashed aircraft".
Quindi puoi fare l'updating di oob_air appena conclusa la missione in DEBRIEF_Master.lua prima della riga 87 "--run log evaluation and status updates"
considerando che la valutazione sulla vittoria della campagna deve essere fatta sicuramente dopo l'aggiornamento delle stat:

]]
