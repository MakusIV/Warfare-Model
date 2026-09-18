-- CAP: p:20, fp: 2-2
-- Ship convoy p:1, fp:6-12
-- OCA Strike: p:1, fp: 2-4
-- EWR/ELINT Site: p:5, fp: 2-4
-- SAM Site: p:6, fp: 3-6
-- FASP AA: p:2, fp: 2-4 
-- FARP: p:6, fp 5-8
-- Airbase: p:4, fp:4-8
-- SUPPLY Plant: p:4, fp:4-10
-- Long SUPPLY Line: p:1-2, fp:6-12
-- SUPPLY Line: p:6, fp:4-8
-- Ground Troops: p:1, fp:2-4
-- Bidge: p:3, fp:2-4
-- Airbase Defenses: p:2, fp:4-8

-- ATT: nella proprietà slaved = nome gruppo (NO nome unità o nome targetlist)

-- la firepower per le missioni A2A (Intercept, sweep, CAP) deve essere calcolata con riferimento al 1 a 1: un aereo per ogni nemico.
-- intercept 
-- 
--[[

new firepower definition:


["Russian Convoy 1"] = {
			task = "Anti-ship Strike",
			priority = 1,
			attributes = {"ship"},
			dimesnion = "mix",
			num_targets_element = 8, -- 8 ship se lo inserisci nella funzione non è necessario definirlo qui
			num_dedicated_weapon_for_destroy_element = 3, -- 3 ASM ship se lo inserisci nella funzione non è necessario definirlo qui
			
			firepower = {				
				min = evaluate_target_firepower( num_targets_element = 8, num_dedicated_weapon_for_destroy_single_element = 3, "min", attribute = {"ship"}, task = "Anti-ship Strike"), -- 
				max = evaluate_target_firepower( num_targets_element = 8, num_dedicated_weapon_for_destroy_single_element = 3, "max", attribute = {"ship"}, task = "Anti-ship Strike" ), --
			},
			class = "ship",
.			name = "Russian Convoy 1",
		},


5 ship convoy -> min firepower: 7, max firepower: 10
standard SAM-2 site: 7 elements -> min firepower: 9, max firepower: 14 
airport oca strike: 15 elements(structure and aircraft) -> min firepower: 9, max firepower: 14 
]]


targetlist = {   
	["blue"] = {
		["Vaziani Alert"] = {
			task = "Intercept",
			priority = 5,
			attributes = {},
			firepower = {
				min = 2,  -- min num enemy aircraft
				max = 4, -- max num enemy aircraft
			},
			base = "Vaziani",
			radius = 200000,
			inactive = false,
		},
		["Kutaisi Alert"] = {
			task = "Intercept",
			priority = 5,
			attributes = {},
			firepower = {
				min = 2,
				max = 4,
			},
			base = "Kutaisi",
			radius = 200000,
			inactive = false,
		},
		["Kutaisi Alert 100"] = {
			task = "Intercept",
			priority = 7,
			attributes = {},
			firepower = {
				min = 2,
				max = 4,
			},
			base = "Kutaisi",
			radius = 100000,
			inactive = false,
		},
		["CVN-71 Theodore Roosevelt Alert"] = {
			task = "Intercept",
			priority = 7,
			attributes = {},
			firepower = {
				min = 2,
				max = 4,
			},
			base = "CVN-71 Theodore Roosevelt",
			radius = 250000,
		},
		["Battle Group CAP"] = {
			task = "CAP",
			priority = 10,
			attributes = {"CV CAP"},
			firepower = {
				min = 2,
				max = 4,
			},
			slaved = {"TF-71", 335, 50000},
			radius = 111000,
			text = "",
		},
		["Battle Group AEW"] = {
			task = "AWACS",
			priority = 10,
			attributes = {"AEW"},
			firepower = {
				min = 1, -- min num AWACS aircraft
				max = 1, -- max num AWACS aircraft
			},
			slaved = {"TF-71",320, 40000},
			text = "",
		},
		["Mission Support Tanker"] = {
			task = "Refueling",
			priority = 10,
			attributes = {"medium"},
			firepower = {
				min = 1, -- min num Tanker aircraft
				max = 1, -- max num Tanker aircraft
			},
			slaved = {"TF-71", 330, 35000},
			text = "",
		},
		["Recovery Tanker"] = {
			task = "Refueling",
			priority = 5,
			attributes = {"low"},
			firepower = {
				min = 1,
				max = 1,
			},
			slaved = {"TF-71", 310, 30000},
			text = "",
		},
		["Russian Convoy 1"] = {
			task = "Anti-ship Strike",
			priority = 1,
			attributes = {"ship"},
			dimension ="mix",
			firepower = {
				min = 5, 
				max = 8, 
			},
			class = "ship",
			name = "Russian Convoy 1",
		},
		["Russian Convoy 2"] = {
			task = "Anti-ship Strike",
			priority = 1,
			attributes = {"ship"},
			firepower = {
				min = 5, 
				max = 8, 
			},
			class = "ship",
			name = "Russian Convoy 2",
		},		
		["AWACS"] = {
			task = "AWACS",
			priority = 10,
			attributes = {"Sentry"},
			firepower = {
				min = 1,
				max = 1,
			},
			refpoint = "AWACS",
			radius = 15000,
			text = "",
		},
		["Tanker Track West"] = {
			task = "Refueling",
			priority = 10,
			attributes = {"KC135MPRS"},
			firepower = {
				min = 1,
				max = 1,
			},
			refpoint = "Tanker Track West",
			radius = 15000,
			text = "West of Kutaisi",
		},
		["Tanker Track East"] = {
			task = "Refueling",
			priority = 10,
			attributes = {"KC135"},
			firepower = {
				min = 1,
				max = 1,
			},
			refpoint = "Tanker Track East KC135",
			radius = 15000,
			text = "north west of Tbilissi",
		},
		["Sweep Center"] = {
			task = "Fighter Sweep",
			priority = 1,
			attributes = {},
			firepower = {
				min = 3, --estimated aircraft : 5, efficiency: 0.5 ( 2 missile for one shot ): 5 / 0.5 = 10
				max = 5,
			},
			x = -165988,
			y = 852489,
			text = "in the center front area",
		},
		["Sweep West"] = {
			task = "Fighter Sweep",
			priority = 1,
			attributes = {},
			firepower = {
				min = 3,
				max = 5,
			},
			x = -138197,
			y = 776021,
			text = "in the west front area",
		},
		["Sweep East"] = {
			task = "Fighter Sweep",
			priority = 1,
			attributes = {},
			firepower = {
				min = 3,
				max = 5,
			},
			x = -129150,
			y = 888342,
			text = "in the east front area",
		},
		["Beslan Airbase OCA Strike"] = {
			task = "Strike",
			priority = 1,
			attributes = {"Parked Aircraft"},
			firepower = {
				min = 2, 
				max = 4, 
			},
			class = "airbase",
			name = "Beslan",
		},
		["Mozdok airbase OCA Strike"] = {
			task = "Strike",
			priority = 1,
			attributes = {"Parked Aircraft"},
			firepower = {
				min = 2, 
				max = 4, 
			},
			class = "airbase",
			name = "Mozdok",
		},
		["Nalchik airbase OCA Strike"] = {
			task = "Strike",
			priority = 1,
			attributes = {"Parked Aircraft"},
			firepower = {
				min = 2, 
				max = 4, 
			},
			class = "airbase",
			name = "Nalchik",
		},
		["Mineralnye-Vody airbase OCA Strike"] = {
			task = "Strike",
			priority = 1,
			attributes = {"Parked Aircraft"},
			firepower = {
				min = 2,
				max = 4, 
			},
			class = "airbase",
			name = "Mineralnye-Vody",
		},
		["101 EWR Site"] = {
			task = "Strike",
			priority = 5,
			-- picture = {""},
			attributes = {"soft"},
			firepower = {
				min = 2, 
				max = 4, 
			},
			class = "vehicle",
			name = "101 EWR Site",
		},
		["102 EWR Site"] = {
			task = "Strike",
			priority = 5,
			attributes = {"soft"},
			firepower = {
				min = 2, 
				max = 4, 
			},
			class = "vehicle",
			name = "102 EWR Site",
		},
		["103 EWR Site"] = {
			task = "Strike",
			priority = 5,
			attributes = {"soft"},
			firepower = {
				min = 2, 
				max = 4, 
			},
			class = "vehicle",
			name = "103 EWR Site",
		},
		["CAP Tbilissi"] = {
			task = "CAP",
			priority = 20,
			attributes = {"Air Forces"},
			firepower = {
				min = 2,
				max = 4,
			},
			refpoint = "CAP Tbilissi",
			radius = 50000,
			text = "North west of Tbilissi",
		},		
		["CAP Kutaisi"] = {
			task = "CAP",
			priority = 20,
			attributes = {"Air Forces"},
			firepower = {
				min = 2,
				max = 4,
			},
			refpoint = "CAP Kutaisi",
			radius = 50000,
			text = "North of Kutaisi",
		},
		["203 SA-2 Site A-3"] = {
			task = "Strike",
			priority = 6,
			attributes = {"SAM"},
			firepower = {
				min = 2, 
				max = 4, 
			},
			class = "vehicle",
			name = "203 SA-2 Site A-3",
		},
		["204 SA-6 Site B-1"] = {
			task = "Strike",
			priority = 6,
			attributes = {"SAM"},
			firepower = {
				min = 3, 
				max = 6, 
			},
			class = "vehicle",
			name = "204 SA-6 Site B-1",
		},
		["206 SA-2 Site B-3"] = {
			task = "Strike",
			priority = 6,
			attributes = {"SAM"},
			firepower = {
				min = 3,  --3,
				max = 6,  --4,
			},
			class = "vehicle",
			name = "206 SA-2 Site B-3",
		},		
		["209 SA-2 Site R-3"] = {
			task = "Strike",
			priority = 6,
			attributes = {"SAM"},
			firepower = {
				min = 3,   --3,
				max = 6, --  --4,
			},
			class = "vehicle",
			name = "209 SA-2 Site R-3",
		},
		["101 SA-3 Site E-1"] = {
			task = "Strike",
			priority = 6,
			attributes = {"SAM"},
			firepower = {
				min = 3, -- --3,
				max = 6, -- --4,
			},
			class = "vehicle",
			name = "101 SA-3 Site E-1",
		},
		["104 SA-6 Site E-4"] = {
			task = "Strike",
			priority = 6,
			attributes = {"SAM"},
			firepower = {
				min = 3, -- --3,
				max = 3, -- --4,
			},
			class = "vehicle",
			name = "104 SA-6 Site E-4",
		},		
		["106 SA-2 Site C-6"] = {
			task = "Strike",
			priority = 6,
			-- picture = {""},
			attributes = {"SAM"},
			firepower = {
				min = 3,  --3,
				max = 3, -- --4,
			},
			class = "vehicle",
			name = "106 SA-2 Site C-6",
		},
		["Teberda SA-2 Site"] = {
			task = "Strike",
			priority = 6,
			-- picture = {""},
			attributes = {"SAM"},
			firepower = {
				min = 3,  --3,
				max = 3, -- --4,
			},
			class = "vehicle",
			name = "Teberda SA-2 Site",
		},
		["DM-34 SA-5 Site-1"] = {
			task = "Strike",
			priority = 6,
			-- picture = {""},
			attributes = {"SAM"},
			firepower = {
				min = 3,  --3,
				max = 3, -- --4,
			},
			class = "vehicle",
			name = "DM-34 SA-5 Site-1",
		},
		["Maykop SA-2"] = {
			task = "Strike",
			priority = 4,
			-- picture = {""},
			attributes = {"SAM"},
			firepower = {
				min = 3,  --3,
				max = 3, -- --4,
			},
			class = "vehicle",
			name = "Maykop SA-2",
		},
		["NOVOROSSIYSK SA-2 Site DK-04"] = {
			task = "Strike",
			priority = 4,
			-- picture = {""},
			attributes = {"SAM"},
			firepower = {
				min = 3,  --3,
				max = 6, -- --4,
			},
			class = "vehicle",
			name = "Maykop SA-2",
		},
		["NKRYMSK SA-5 Site DK-17"] = {
			task = "Strike",
			priority = 4,
			-- picture = {""},
			attributes = {"SAM"},
			firepower = {
				min = 3,  --3,
				max = 6, -- --4,
			},
			class = "vehicle",
			name = "Maykop SA-2",
		},
		["LENIGORI FARP AA"] = {
			task = "Strike",
			priority = 2,
			attributes = {"SAM"},
			firepower = {
				min = 3, -- --2,
				max = 3, -- --3,
			},
			class = "vehicle",
			name = "LENIGORI FARP AA",
		},
		["TSKHINVALI FARP AA"] = {
			task = "Strike",
			priority = 2,
			attributes = {"SAM"},
			firepower = {
				min = 3, -- --2,
				max = 3, -- --3,
			},
			class = "vehicle",
			name = "TSKHINVALI FARP AA",
		},		
		["Beslan Airbase"] = {
			task = "Strike",
			priority = 4,
			picture = {"Beslan_Airbase.png"},
			attributes = {"Structure"},
			firepower = {
				min = 3, -- --3,
				max = 3, -- --6,
			},
			elements = {
				[1] = {
					name = "Beslan Control Tower",
					x = -148962.921875,
					y = 843620.0625,
				},
				[2] = {
					name = "Beslan Hangar 1",
					x = -148993.71875,
					y = 843839.625,
				},
				[3] = {
					name = "Beslan Hangar 2",
					x = -149028.84375,
					y = 843837.375,
				},
				[4] = {
					name = "Beslan Barrack",
					x = -149005.96875,
					y = 843724.125,
				},
				[5] = {
					name = "Rescue Station",
					x = -149021.625,
					y = 844018.875,
				},
				[6] = {
					name = "Repair Hangar",
					x = -149043.3125,
					y = 844111.125,
				},
				[7] = {
					name = "Refuel Station",
					x = -149049.53125,
					y = 844187,
				},
				[8] = {
					name = "Beslan Terminal",
					x = -148948.96875,
					y = 843511.75,
				},
				[9] = {
					name = "Beslan Hangar 3",
					x = -149149.171875,
					y = 843921.125,
				},
				[10] = {
					name = "Beslan Power Supply",
					x = -149095.828125,
					y = 843622.9375,
				},
			},
		},
		["Nalchik Airbase"] = {
			task = "Strike",
			priority = 3,
			picture = {"Nalchik_Airbase.png"},
			attributes = {"Structure"},
			firepower = {
				min = 3, --getTargetFirepower(7, "blue", "mix", "Structure", "Strike", true, "med"), --3,
				max = 3, --getTargetFirepower(7, "blue", "mix", "Structure", "Strike", false, "med"), --6,
			},
			elements = {
				[1] = {
					name = "Fuel Support House",
					x = -124614.8046875,
					y = 760428.9375,
				},
				[2] = {
					name = "Ammunition Command Center",
					x = -123918.15625,
					y = 760783.8125,
				},
				[3] = {
					name = "Nalchik Control Tower",
					x = -125484.5,
					y = 760367.0625,
				},
				[4] = {
					name = "Nalchik Main Hangar",
					x = -125478.59375,
					y = 760683.75,
				},
				[5] = {
					name = "Nalchik Admin House",
					x = -125382.1953125,
					y = 760720.875,
				},
				[6] = {
					name = "Nalchik Crew House",
					x = -125487.359375,
					y = 760813.5625,
				},
				[7] = {
					name = "Nalchik Rescue Station",
					x = -124947.9921875,
					y = 761007.4375,
				},
			},
		},
		["Mozdok Airbase"] = {
			task = "Strike",
			priority = 3,
			picture = {"Mozdok_Airbase.png"},
			attributes = {"Structure"},
			firepower = {
				min = 3, -- --3,
				max = 3, -- --6,
			},
			elements = {
				[1] = {
					name = "Fuel Support House",
					x = -84118.1328125,
					y = 835186.75,
				},
				[2] = {
					name = "Mozdok Control Tower",
					x = -84169.25,
					y = 834521,
				},
				[3] = {
					name = "Mozdok Command House",
					x = -84198.1640625,
					y = 834535.3125,
				},
				[4] = {
					name = "Mozdok Power Supply",
					x = -84205.1796875,
					y = 834497.9375,
				},
				[5] = {
					name = "Hangar 1",
					x = -84026.2890625,
					y = 835012.6875,
				},
				[6] = {
					name = "Hangar 2",
					x = -84049.09375,
					y = 835015.5,
				},
				[7] = {
					name = "Hangar 3",
					x = -83996.3828125,
					y = 832570.8125,
				},
				[8] = {
					name = "Deported Hangar 1",
					x = -85358.21875,
					y = 832253.125,
				},
				[9] = {
					name = "Deported Hangar 2",
					x = -85306.453125,
					y = 832343.125,
				},
				[10] = {
					name = "Deported Hangar 3",
					x = -85320.0078125,
					y = 832356.5625,
				},
			},
		},	
		["Maykop-Khanskaya Airbase"] = {
			task = "Strike",
			priority = 3,
			picture = {"Maykop-Khanskaya_Airbase.png"},
			attributes = {"Structure"},
			firepower = {
				min = 3, -- --3,
				max = 3, -- --6,
			},
			elements = {
				[1] = {
					name = "Fuel Support House",
					y = 459714.12029112,
                    x = -25626.210368722,
				},
				[2] = {
					name = "Maykop-Khanskaya Control Tower",
					y = 458080.20081024,
					x = -26609.600935969,
				},
				[3] = {
					name = "Maykop-Khanskaya Command House",
					y = 457898.61932232,
					x = -27909.578430298,
				},
				[4] = {
					name = "Maykop-Khanskaya Power Supply",
					y = 459533.14364873,
					x = -26750.182378145,
				},
				[5] = {
					name = "Hangar 1",
					y = 458753.34034553,
					x = -27095.421929516,
				},
				[6] = {
					name = "Hangar 2",
					y = 458777.92501568,
					x = -27044.613611215,
				},
				[7] = {
					name = "Hangar 3",
					y = 458800.87070781,
					x = -26990.527336894,
				},
				[8] = {
					name = "Deported Hangar 1",
					y = 458262.61709523,
					x = -26869.132821437,
				},
				[9] = {
					name = "Deported Hangar 2",
					y = 458936.15460273,
					x = -26327.536576484,
				},
				[10] = {
					name = "Deported Hangar 3",
					y = 458692.63445234,
					x = -27122.013356338,
				},
			},
		},	
		["Mineralnye-Vody Airbase"] = {
			task = "Strike",
			priority = 3,
			picture = {"Mineralnye-Vody_Airbase.png"},
			attributes = {"Structure"},
			firepower = {
				min = 3, -- --3,
				max = 3, -- --6,
			},
			elements = {
				[1] = {
					name = "Fuel Support House",
					x = -52146.515625,
					y = 705679.875,
				},
				[2] = {
					name = "Crew Home 1",
					x = -52287.57421875,
					y = 705966.375,
				},
				[3] = {
					name = "Crew Home 2",
					x = -52165.984375,
					y = 706024.8125,
				},
				[4] = {
					name = "Crew Home 3",
					x = -52380.97265625,
					y = 706210.75,
				},
				[5] = {
					name = "Mineralnye Rescue station",
					x = -52477.5859375,
					y = 707329.75,
				},
				[6] = {
					name = "Officers Club",
					x = -52277.8671875,
					y = 706074.125,
				},
				[7] = {
					name = "Crew club",
					x = -52337.421875,
					y = 706088.5,
				},
				[8] = {
					name = "Mineralnye Control Tower",
					x = -52318.4140625,
					y = 706580.8125,
				},
				[9] = {
					name = "Mineralnye Command House",
					x = -51810.00390625,
					y = 705714.1875,
				},
				[10] = {
					name = "Mineralnye Power Supply 1",
					x = -52009.95703125,
					y = 705334.3125,
				},
				[11] = {
					name = "Mineralnye Power Supply 2",
					x = -51528.6640625,
					y = 708070.625,
				},
				[12] = {
					name = "Main Hangar 1",
					x = -51905.54296875,
					y = 705799.25,
				},
				[13] = {
					name = "Main Hangar 2",
					x = -51691.8046875,
					y = 705462,
				},
				[14] = {
					name = "Main Hangar 3",
					x = -51936.640625,
					y = 706042.6875,
				},
				[15] = {
					name = "Deported Repair Hangar 1",
					x = -51419.0859375,
					y = 707823.8125,
				},
				[16] = {
					name = "Deported Repair Hangar 2",
					x = -51376.71484375,
					y = 707733.75,
				},
				[17] = {
					name = "Deported Repair Hangar 3",
					x = -51190.4765625,
					y = 708177.25,
				},
			},
		},		
		["Prohladniy Depot MP 24"] = {
			task = "Strike",
			priority = 4,
			picture = {"Prohladniy_Depot.png"},
			attributes = {"Structure"},
			firepower = {
				min = 3,  --3,
				max = 3,  --6,
			},
			class = "static",
			elements = {
				[1] = {
					name = "Prohladniy Depot 1",
				},
				[2] = {
					name = "Prohladniy Depot 2",
				},
				[3] = {
					name = "Prohladniy Depot 3",
				},
				[4] = {
					name = "Prohladniy Depot 4",
				},
				[5] = {
					name = "Prohladniy Depot 5",
				},
				[6] = {
					name = "Prohladniy Depot 6",
				},
				[7] = {
					name = "Prohladniy Depot Railway station",
				},
				[8] = {
					name = "Prohladniy Depot container 1",
				},
				[9] = {
					name = "Prohladniy Depot container 2",
				},
				[10] = {
					name = "Prohladniy Depot container 3",
				},
				[11] = {
					name = "Prohladniy Depot container 4",
				},
				[12] = {
					name = "Prohladniy Depot container 5",
				},
				[13] = {
					name = "Prohladniy Depot container 6",
				},
				[14] = {
					name = "Prohladniy Depot container 7",
				},
				[15] = {
					name = "Prohladniy Depot container 8",
				},
				[16] = {
					name = "Prohladniy Depot container 9",
				},
				[17] = {
					name = "Prohladniy Depot container 10",
				},
				[18] = {
					name = "Prohladniy Depot container 11",
				},
				[19] = {
					name = "Prohladniy Depot container 12",
				},
				[20] = {
					name = "Prohladniy Depot container 13",
				},
				[21] = {
					name = "Prohladniy Depot container 14",
				},
				[22] = {
					name = "Prohladniy Depot container 15",
				},
				[23] = {
					name = "Prohladniy Depot container 16",
				},
				[24] = {
					name = "Prohladniy Depot container 17",
				},
				[25] = {
					name = "Prohladniy Depot container 18",
				},
				[26] = {
					name = "Prohladniy Depot container 19",
				},
				[27] = {
					name = "Prohladniy Depot container 20",
				},
				[28] = {
					name = "Prohladniy Depot Fuel tank 1",
				},
				[29] = {
					name = "Prohladniy Depot Fuel tank 2",
				},
				[30] = {
					name = "Prohladniy Depot Fuel tank 3",
				},
				[31] = {
					name = "Prohladniy Depot Fuel tank 4",
				},
				[32] = {
					name = "Prohladniy Depot Fuel tank 5",
				},
				[33] = {
					name = "Prohladniy Depot Fuel tank 6",
				},
				[34] = {
					name = "Prohladniy Depot Fuel tank 7",
				},
				[35] = {
					name = "Prohladniy Depot Fuel tank 8",
				},
				[36] = {
					name = "Prohladniy Depot Fuel tank 9",
				},
				[37] = {
					name = "Prohladniy Depot Fuel tank 10",
				},

			},
		},		
		["Peredovaya SUPPLY PLANT"] = {
			task = "Strike",
			priority = 4,
			--picture = {"Prohladniy_Depot.png"},
			attributes = {"Structure"},
			firepower = {
				min = 3,  --3,
				max = 3,  --6,
			},
			class = "static",
			elements = {
				[1] = {
					name = "Peredovaya SUPPLY PLANT",
				},
				[2] = {
					name = "Peredovaya SUPPLY PLANT-1",
				},
				[3] = {
					name = "Peredovaya SUPPLY PLANT-2",
				},
				[4] = {
					name = "Peredovaya SUPPLY PLANT-3",
				},
				[5] = {
					name = "Peredovaya SUPPLY PLANT-4",
				},			
			},
		},	
		["SUPPLY PLANT BAKSAN LP83"] = {
			task = "Strike",
			priority = 4,
			--picture = {"Prohladniy_Depot.png"},
			attributes = {"Structure"},
			firepower = {
				min = 3,  --3,
				max = 3,  --6,
			},
			class = "static",
			elements = {
				[1] = {
					name = "SUPPLY PLANT BAKSAN LP83",
				},
				[2] = {
					name = "SUPPLY PLANT BAKSAN LP83-1",
				},
				[3] = {
					name = "SUPPLY PLANT BAKSAN LP83-2",
				},
				[4] = {
					name = "SUPPLY PLANT BAKSAN LP83-3",
				},
				[5] = {
					name = "SUPPLY PLANT BAKSAN LP83-4",
				},
				[6] = {
					name = "SUPPLY PLANT BAKSAN LP83-5",
				},
				[7] = {
					name = "SUPPLY PLANT BAKSAN LP83-6",
				},
				[8] = {
					name = "SUPPLY PLANT BAKSAN LP83-7",
				},
				[9] = {
					name = "SUPPLY PLANT BAKSAN LP83-8",
				},
				[10] = {
					name = "SUPPLY PLANT BAKSAN LP83-9",
				},
				[11] = {
					name = "SUPPLY PLANT BAKSAN LP83-10",
				},
				[12] = {
					name = "SUPPLY PLANT BAKSAN LP83-11",
				},
				[13] = {
					name = "SUPPLY PLANT BAKSAN LP83-13",
				},
				[14] = {
					name = "SUPPLY PLANT BAKSAN LP83-14",
				},
				[15] = {
					name = "SUPPLY PLANT BAKSAN LP83-15",
				},
				[16] = {
					name = "SUPPLY PLANT BAKSAN LP83-16",
				},
				[17] = {
					name = "SUPPLY PLANT BAKSAN LP83-17",
				},
				[18] = {
					name = "SUPPLY PLANT BAKSAN LP83-18",
				},
				[19] = {
					name = "SUPPLY PLANT BAKSAN LP83-19",
				},
				[20] = {
					name = "SUPPLY PLANT BAKSAN LP83-20",
				},
				[21] = {
					name = "SUPPLY PLANT BAKSAN LP83-21",
				},
				[22] = {
					name = "SUPPLY PLANT BAKSAN LP83-22",
				},
				[23] = {
					name = "SUPPLY PLANT BAKSAN LP83-23",
				},
				[24] = {
					name = "SUPPLY PLANT BAKSAN LP83-24",
				},
				[25] = {
					name = "SUPPLY PLANT BAKSAN LP83-25",
				},
				[26] = {
					name = "SUPPLY PLANT BAKSAN LP83-26",
				},
				[27] = {
					name = "SUPPLY PLANT BAKSAN LP83-27",
				},
				[28] = {
					name = "SUPPLY PLANT BAKSAN LP83-28",
				},
				[29] = {
					name = "SUPPLY PLANT BAKSAN LP83-29",
				},					
			},
		},		
		["CHERKESSK SUPPLY PLANT KP69"] = {
			task = "Strike",
			priority = 4,
			--picture = {""},
			attributes = {"Structure"},
			firepower = {
				min = 3,  --3,
				max = 3,  --6,
			},
			class = "static",
			elements = {
				[1] = {
					name = "CHERKESSK SUPPLY PLANT KP69",
				},
				[2] = {
					name = "CHERKESSK SUPPLY PLANT KP69-1",
				},
				[3] = {
					name = "CHERKESSK SUPPLY PLANT KP69-2",
				},
				[4] = {
					name = "CHERKESSK SUPPLY PLANT KP69-3",
				},
				[5] = {
					name = "CHERKESSK SUPPLY PLANT KP69-4",
				},
				[6] = {
					name = "CHERKESSK SUPPLY PLANT KP69-5",
				},
				[7] = {
					name = "CHERKESSK SUPPLY PLANT KP69-6",
				},
				[8] = {
					name = "CHERKESSK SUPPLY PLANT KP69-7",
				},
				[9] = {
					name = "CHERKESSK SUPPLY PLANT KP69-8",
				},
				[10] = {
					name = "CHERKESSK SUPPLY PLANT KP69-9",
				},
				[11] = {
					name = "CHERKESSK SUPPLY PLANT KP69-11",
				},
				[12] = {
					name = "CHERKESSK SUPPLY PLANT KP69-12",
				},
				[13] = {
					name = "CHERKESSK SUPPLY PLANT KP69-13",
				},
				[14] = {
					name = "CHERKESSK SUPPLY PLANT KP69-14",
				},
				[15] = {
					name = "CHERKESSK SUPPLY PLANT KP69-15",
				},
				[16] = {
					name = "CHERKESSK SUPPLY PLANT KP69-16",
				},
				[17] = {
					name = "CHERKESSK SUPPLY PLANT KP69-17",
				},
				[18] = {
					name = "CHERKESSK SUPPLY PLANT KP69-18",
				},
				[19] = {
					name = "CHERKESSK SUPPLY PLANT KP69-19",
				},
				[20] = {
					name = "CHERKESSK SUPPLY PLANT KP69-20",
				},
				[21] = {
					name = "CHERKESSK SUPPLY PLANT KP69-21",
				},
				[22] = {
					name = "CHERKESSK SUPPLY PLANT KP69-22",
				},
				[23] = {
					name = "CHERKESSK SUPPLY PLANT KP69-23",
				},
				[24] = {
					name = "CHERKESSK SUPPLY PLANT KP69-24",
				},
				[25] = {
					name = "CHERKESSK SUPPLY PLANT KP69-25",
				},
				[26] = {
					name = "CHERKESSK SUPPLY PLANT KP69-26",
				},
				[27] = {
					name = "CHERKESSK SUPPLY PLANT KP69-27",
				},
				[28] = {
					name = "CHERKESSK SUPPLY PLANT KP69-28",
				},
				[29] = {
					name = "CHERKESSK SUPPLY PLANT KP69-29",
				},			
			},
		},		
		["BAKSAN-MINERALNYE SUPPLY LINE"] = {
			task = "Strike",
			priority = 4,
			picture = {"Target - BAKSAN-MINERALNYE SUPPLY LINE.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3, --  --3,
				max = 3, -- --6,
			},
			elements = {
				[1] = {
					name = "bridge Progress",
					x = -94312.612672011,
					y = 732728.82550397,
				},
				[2] = {
					name = "bridge Kamennomostskoe",
					x =-106420.67313121,
					y = 709761.90427801,
				},
			},
		},		
		["BAKSAN-MOZDOK SUPPLY LINE"] = {--change with new bridge elements
			task = "Strike",
			priority = 2,
			picture = {"Target - Vladikavkaz Bridge.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3, -- --3,
				max = 3, -- --6,
			},
			elements = {
				[1] = {
					name = "Bridge Vladikavkaz MN 76",
					x = -165689.171875,
					y = 850781.9375,
				},
				[2] = {
					name = "Bridge Vladikavkaz North MN 76",
					x = -164245.28125,
					y = 850403,
				},
				[3] = {
					name = "Bridge Vladikavkaz South MN 76",
					x = -168229.1875,
					y = 852723.0625,
				},
			},
		},
		["BESLAN-NOGIR FARP SUPPLY LINE"] = {--ok
			task = "Strike",
			priority = 1,
			--picture = {"Target - Beslan Bridge.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3, -- --3,
				max = 3, -- --6,
			},
			elements = {
				[1] = {
					name = "Bridge Vladikavkaz MN 76",
					x = -165689.171875,
					y = 850781.9375,
				},
				[2] = {
					name = "Bridge Vladikavkaz North MN 76",
					x = -164245.28125,
					y = 850403,
				},
				[3] = {
					name = "Bridge Vladikavkaz South MN 76",
					x = -168229.1875,
					y = 852723.0625,
				},
				[4] = {
					name = "Bridge north bank South Beslan",
					x = -151580.80078125,
					y = 835949.02734375,
				},
				[5] = {
					name = "Bridge south bank South Beslan",
					x = -151456.44921875,
					y = 836013.34375,
				},
				[6] = {
					name = "Bridge Alagir",
					x = -173099.3125,
					y = 815939.25,
				},				
			},
		},	
		["High priority Target BESLAN FARP SUPPLY LINE A"] = {--ok
			task = "Strike",
			priority = 6,
			picture = {"Target - Vladikavkaz Bridge.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3, -- --3,
				max = 3, -- --6,
			},
			elements = {
				[1] = {
					name = "Bridge Vladikavkaz MN 76",
					x = -165689.171875,
					y = 850781.9375,
				},
				[2] = {
					name = "Bridge Vladikavkaz North MN 76",
					x = -164245.28125,
					y = 850403,
				},
				[3] = {
					name = "Bridge Vladikavkaz South MN 76",
					x = -168229.1875,
					y = 852723.0625,
				},
			},
		},	
		["High priority Target BESLAN FARP SUPPLY LINE B"] = {--ok
			task = "Strike",
			priority = 6,
			picture = {"Target - Beslan Bridge.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3, --getTargetFirepower(2, "blue", "med", "Bridge", "Strike", true, "med"), --3,
				max = 3, -- --6,
			},
			elements = {				
				[1] = {
					name = "Bridge north bank South Beslan",
					x = -151580.80078125,
					y = 835949.02734375,
				},
				[2] = {
					name = "Bridge south bank South Beslan",
					x = -151456.44921875,
					y = 836013.34375,
				},								
			},
		},
		["High priority Target BESLAN FARP SUPPLY LINE C"] = {--ok
			task = "Strike",
			priority = 6,
			picture = {"Target - Alagir Bridge.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3, --getTargetFirepower(1, "blue", "med", "Bridge", "Strike", true, "med"), --3,
				max = 3, --getTargetFirepower(1, "blue", "med", "Bridge", "Strike", false, "med"), --6,
			},
			elements = {				
				[1] = {
					name = "Bridge Alagir",
					x = -173099.3125,
					y = 815939.25,
				},				
			},
		},				
		["BESLAN-LENIGORI FARP SUPPLY LINE"] = {-- same BESLAN-NOGIR FARP SUPPLY LINE
			task = "Strike",
			priority = 1,
			--picture = {"Vladikavkaz_Bridge.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3, -- --3,
				max = 3, -- --6,
			},
			elements = {
				[1] = {
					name = "Bridge Vladikavkaz MN 76",
					x = -165689.171875,
					y = 850781.9375,
				},				
				[2] = {
					name = "Bridge Vladikavkaz South MN 76",
					x = -168229.1875,
					y = 852723.0625,
				},
				[3] = {
					name = "Bridge Vladikavkaz North MN 76",
					x = -164245.28125,
					y = 850403,
				},
				[4] = {
					name = "Bridge north bank South Beslan",
					x = -151580.80078125,
					y = 835949.02734375,
				},
				[5] = {
					name = "Bridge south bank South Beslan",
					x = -151456.44921875,
					y = 836013.34375,
				},
				[6] = {
					name = "Bridge Alagir",
					x = -173099.3125,
					y = 815939.25,
				},
			},
		},	
		["BESLAN-TSKHINVALI FARP SUPPLY LINE"] = {-- same BESLAN-NOGIR FARP SUPPLY LINE + Rail Bridge Digora MN 38
			task = "Strike",
			priority = 1,
			--picture = {"Vladikavkaz_Bridge.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3, --getTargetFirepower(7, "blue", "mix", "Bridge", "Strike", true, "med"), --3,
				max = 3, --getTargetFirepower(7, "blue", "mix", "Bridge", "Strike", false, "med"), --6,
			},
			elements = {
				[1] = {
					name = "Bridge Vladikavkaz MN 76",
					x = -165689.171875,
					y = 850781.9375,
				},				
				[2] = {
					name = "Bridge Vladikavkaz South MN 76",
					x = -168229.1875,
					y = 852723.0625,
				},
				[3] = {
					name = "Bridge Vladikavkaz North MN 76",
					x = -164245.28125,
					y = 850403,
				},
				[4] = {
					name = "Bridge north bank South Beslan",
					x = -151580.80078125,
					y = 835949.02734375,
				},
				[5] = {
					name = "Bridge south bank South Beslan",
					x = -151456.44921875,
					y = 836013.34375,
				},
				[6] = {
					name = "Bridge Alagir",
					x = -173099.3125,
					y = 815939.25,
				},
				[7] = {
					name = "Rail Bridge Digora MN 38",
					x = -157146.546875,
					y = 809730.375,
				},		
			},
		},		
		["High priority Target Rail Bridge Digora MN 38"] = {
			task = "Strike",
			priority = 6,
			--picture = {"Vladikavkaz_Bridge.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3, --getTargetFirepower(1, "blue", "big", "Bridge", "Strike", true, "med"), --3,
				max = 3, --getTargetFirepower(1, "blue", "big", "Bridge", "Strike", false, "med"), --6,,
			},
			elements = {
				[1] = {
					name = "Rail Bridge Digora MN 38",
					x = -157146.546875,
					y = 809730.375,
				},							
			},
		},			
		["Prohladniy Depot MP 24-BESLAN SUPPLY LINE"] = {
			task = "Strike",
			priority = 1,
			--picture = {"Vladikavkaz_Bridge.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3, --getTargetFirepower(8, "blue", "mix", "Bridge", "Strike", true, "med"), --3,
				max = 3, --getTargetFirepower(8, "blue", "mix", "Bridge", "Strike", false, "med"), --6,
			},
			elements = {
				[1] = {
					name = "Rail Bridge right bank SE Mayskiy",
					x = -111785.2421875,
					y = 795963.7109375,
				},
				[2] = {
					name = "Rail Bridge Center SE Mayskiy",
					x = -111727.7109375,
					y = 795881.91699219,
				},
				[3] = {
					name = "Rail Bridge left bank SE Mayskiy",
					x = -111670.1796875,
					y = 795800.12207031,
				},
				[4] = {
					name = "Bridge north bank South Elhotovo",
					x = -140288.05761719,
					y = 809993.75585938,
				},
				[5] = {
					name = "Bridge south bank South Elhotovo",
					x = -140195.16113281,
					y = 810098.49414063,
				},
				[6] = {
					name = "Rail Bridge right bank SW Kardzhin",
					x = -145428.47167969,
					y = 814533.16210938,
				},
				[7] = {
					name = "Rail Bridge left bank SW Kardzhin",
					x = -145376.90332031,
					y = 814618.83789063,
				},
				[8] = {
					name = "Rail Bridge Kardzhin MN 49",
					x = -144986.53125,
					y = 816502.625,
				},				
			},
		},
		["High priority Target Prohladniy Depot MP 24 SUPPLY LINE A"] = {
			task = "Strike",
			priority = 6,
			--picture = {"Vladikavkaz_Bridge.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3, -- --3,
				max = 3, -- --6,
			},
			elements = {
				[1] = {
					name = "Rail Bridge right bank SE Mayskiy",
					x = -111785.2421875,
					y = 795963.7109375,
				},
				[2] = {
					name = "Rail Bridge Center SE Mayskiy",
					x = -111727.7109375,
					y = 795881.91699219,
				},
				[3] = {
					name = "Rail Bridge left bank SE Mayskiy",
					x = -111670.1796875,
					y = 795800.12207031,
				},				
			},
		},
		["High priority Target Prohladniy Depot MP 24 SUPPLY LINE B"] = {
			task = "Strike",
			priority = 6,
			--picture = {"Vladikavkaz_Bridge.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3, -- --3,
				max = 3, -- --6,
			},
			elements = {				
				[1] = {
					name = "Bridge north bank South Elhotovo",
					x = -140288.05761719,
					y = 809993.75585938,
				},
				[2] = {
					name = "Bridge south bank South Elhotovo",
					x = -140195.16113281,
					y = 810098.49414063,
				},			
			},
		},
		["High priority Target Prohladniy Depot MP 24 SUPPLY LINE C"] = {
			task = "Strike",
			priority = 6,
			--picture = {"Vladikavkaz_Bridge.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3, -- --3,
				max = 3, -- --6,
			},
			elements = {			
				[1] = {
					name = "Rail Bridge right bank SW Kardzhin",
					x = -145428.47167969,
					y = 814533.16210938,
				},
				[2] = {
					name = "Rail Bridge left bank SW Kardzhin",
					x = -145376.90332031,
					y = 814618.83789063,
				},
				[3] = {
					name = "Rail Bridge Kardzhin MN 49",
					x = -144986.53125,
					y = 816502.625,
				},				
			},
		},
		["NOGIR FARP MN76"] = {
			task = "Strike",
			priority = 6,
			picture = {"FARP_Vladikavkaz.png"},
			attributes = {"SAM"},
			firepower = {
				min = 3, --3,
				max = 3, -- --6,
			},
			class = "static",
			elements = {
				[1] = {
					name = "NOGIR FARP - Hind 1",
				},
				[2] = {
					name = "NOGIR FARP - Hind 2",
				},
				[3] = {
					name = "NOGIR FARP - Hind 3",
				},
				[4] = {
					name = "NOGIR FARP - Hip 1",
				},
				[5] = {
					name = "NOGIR FARP - Hip 2",
				},
				[6] = {
					name = "NOGIR FARP - Hip 3",
				},
				[7] = {
					name = "NOGIR FARP - Hip 4",
				},
				[8] = {
					name = "NOGIR FARP - Hip 5",
				},
				[9] = {
					name = "NOGIR FARP - Ammo depot 1",
				},
				[10] = {
					name = "NOGIR FARP - Ammo depot 2",
				},
				[11] = {
					name = "NOGIR FARP - Ammo depot 3",
				},
				[12] = {
					name = "NOGIR FARP - Fuel depot 1",
				},
				[13] = {
					name = "NOGIR FARP - Fuel depot 2",
				},
				[14] = {
					name = "NOGIR FARP - Fuel depot 3",
				},
				[15] = {
					name = "NOGIR FARP - Crew house",
				},
				[16] = {
					name = "NOGIR FARP - Crew Tent 1",
				},
				[17] = {
					name = "NOGIR FARP - Crew Tent 2",
				},
				[18] = {
					name = "NOGIR FARP - Crew Tent 3",
				},
			},
		},
		["LENIGORI FARP MM56"] = {
			task = "Strike",
			priority = 6,
			--picture = {"FARP_Vladikavkaz.png"},
			attributes = {"soft"},
			firepower = {
				min = 3,  --3,
				max = 3,  --6,
			},
			class = "static",
			elements = {
				[1] = {
					name = "LENIGORI FARP MM56",
				},
				[2] = {
					name = "LENIGORI FARP MM56 - 1",
				},
				[3] = {
					name = "LENIGORI FARP MM56 - 2",
				},
				[4] = {
					name = "LENIGORI FARP MM56 - 3",
				},			
			},
		},
		["TSKHINVALI FARP MM27"] = {
			task = "Strike",
			priority = 6,
			--picture = {"FARP_Vladikavkaz.png"},
			attributes = {"soft"},
			firepower = {
				min = 3,
				max = 6,
			},
			class = "static",
			elements = {
				[1] = {
					name = "TSKHINVALI FARP MM27",
				},
				[2] = {
					name = "TSKHINVALI FARP MM27-1",
				},
				[3] = {
					name = "TSKHINVALI FARP MM27-2",
				},			
				[4] = {
					name = "TSKHINVALI FARP MM27-3",
				},
				[5] = {
					name = "TSKHINVALI FARP MM27-5",
				},			
			},
		},
		["407 8th Army ELINT Station"] = {
			task = "Strike",
			priority = 6,
			picture = {"ElintStationIntel.png"},
			attributes = {"soft"},
			firepower = {
				min = 2,
				max = 4,
			},
			class = "static",
			elements = {
				[1] = {
					name = "ELINT Antenna Truck 1",
				},
				[2] = {
					name = "ELINT Antenna Truck 2",
				},
				[3] = {
					name = "ELINT Crew Van",
				},
				[4] = {
					name = "ELINT Equipment Van",
				},
				[5] = {
					name = "ELINT Generator Truck",
				},
			},
		},
		["501 5th Artillery Division/1.Btry"] = {
			task = "Strike",
			priority = 1,
			attributes = {"soft"},
			firepower = {
				min = 3, -- 2,
				max = 3,  -- 4,
			},
			class = "vehicle",
			name = "501 5th Artillery Division/1.Btry",
		},
		["502 5th Artillery Division/2.Btry"] = {
			task = "Strike",
			priority = 1,
			attributes = {"soft"},
			firepower = {
				min = 3, -- 2,
				max = 3,  -- 4,
			},
			class = "vehicle",
			name = "502 5th Artillery Division/2.Btry",
		},
		["503 5th Artillery Division/3.Btry"] = {
			task = "Strike",
			priority = 1,
			attributes = {"soft"},
			firepower = {
				min = 3,  -- 2,
				max = 3,  -- 4,
			},
			class = "vehicle",
			name = "503 5th Artillery Division/3.Btry",
		},
		["504 5th Artillery Division/4.Btry"] = {
			task = "Strike",
			priority = 1,
			attributes = {"soft"},
			firepower = {
				min = 3,  -- 2,
				max = 3,  -- 4,
			},
			class = "vehicle",
			name = "504 5th Artillery Division/4.Btry",
		},		
		["Bridge Alagir MN 36"] = {
			task = "Strike",
			priority = 3,
			picture = {"Alagir_Bridge.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3,  --2,
				max = 3,  --4,
			},
			elements = {
				[1] = {
					name = "Bridge Alagir",
					x = -173099.3125,
					y = 815939.25,
				},
			},
		},
		["Bridge Vladikavkaz MN 76"] = {
			task = "Strike",
			priority = 3,
			picture = {"Vladikavkaz_Bridge.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3,  --2,
				max = 3, --4,
			},
			elements = {
				[1] = {
					name = "Bridge Vladikavkaz MN 76",
					x = -165689.171875,
					y = 850781.9375,
				},
			},
		},
		["Bridge Vladikavkaz North MN 76"] = {
			task = "Strike",
			priority = 3,
			picture = {"Vladikavkaz_Bridge.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3,  --2,
				max = 3, --4,
			},
			elements = {
				[1] = {
					name = "Bridge Vladikavkaz North MN 76",
					x = -164245.28125,
					y = 850403,
				},
			},
		},
		["Bridge Vladikavkaz South MN 76"] = {
			task = "Strike",
			priority = 3,
			picture = {"Vladikavkaz_Bridge.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3,  --2,
				max = 3, --4,
			},
			elements = {
				[1] = {
					name = "Bridge Vladikavkaz South MN 76",
					x = -168229.1875,
					y = 852723.0625,
				},
			},
		},
		["Bridge SW Kardzhin MN 49"] = {
			task = "Strike",
			priority = 3,
			picture = {"Kardzhin_Bridges.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3,  --2,
				max = 3, -- --4,
			},
			elements = {
				[1] = {
					name = "Bridge north bank SW Kardzhin",
					x = -145416.77636719,
					y = 815400.75,
				},
				[2] = {
					name = "Bridge south bank SW Kardzhin",
					x = -145554.66015625,
					y = 815425,
				},
			},
		},
		["Bridge South Elhotovo MN 39"] = {
			task = "Strike",
			priority = 3,
			picture = {"Elhotovo_Bridge.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3,  --2,
				max = 3, -- --4,
			},
			elements = {
				[1] = {
					name = "Bridge north bank South Elhotovo",
					x = -140288.05761719,
					y = 809993.75585938,
				},
				[2] = {
					name = "Bridge south bank South Elhotovo",
					x = -140195.16113281,
					y = 810098.49414063,
				},
			},
		},
		["Bridge South Beslan MN 68"] = {
			task = "Strike",
			priority = 3,
			picture = {"Beslan_Bridge.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3,  --2,
				max = 3, -- --4,
			},
			elements = {
				[1] = {
					name = "Bridge north bank South Beslan",
					x = -151580.80078125,
					y = 835949.02734375,
				},
				[2] = {
					name = "Bridge south bank South Beslan",
					x = -151456.44921875,
					y = 836013.34375,
				},
			},
		},
		["Rail Bridge Digora MN 38"] = {
			task = "Strike",
			priority = 3,
			picture = {"Digora_Rail_Bridge.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3,  --2,
				max = 3,  --4,
			},
			elements = {
				[1] = {
					name = "Rail Bridge Digora MN 38",
					x = -157146.546875,
					y = 809730.375,
				},
			},
		},
		["Rail Bridge SW Kardzhin MN 49"] = {
			task = "Strike",
			priority = 3,
			picture = {"Kardzhin_Bridges.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3,  --2,
				max = 3,  --4,
			},
			elements = {
				[1] = {
					name = "Rail Bridge right bank SW Kardzhin",
					x = -145428.47167969,
					y = 814533.16210938,
				},
				[2] = {
					name = "Rail Bridge left bank SW Kardzhin",
					x = -145376.90332031,
					y = 814618.83789063,
				},
			},
		},
		["Rail Bridge SE Mayskiy MP 23"] = {
			task = "Strike",
			priority = 3,
			picture = {"Mayskiy_Rail_Bridge.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3,  --2,
				max = 3, --4,
			},
			elements = {
				[1] = {
					name = "Rail Bridge right bank SE Mayskiy",
					x = -111785.2421875,
					y = 795963.7109375,
				},
				[2] = {
					name = "Rail Bridge Center SE Mayskiy",
					x = -111727.7109375,
					y = 795881.91699219,
				},
				[3] = {
					name = "Rail Bridge left bank SE Mayskiy",
					x = -111670.1796875,
					y = 795800.12207031,
				},
			},
		},
		["Rail Bridge Kardzhin MN 49"] = {
			task = "Strike",
			priority = 3,
			picture = {"Kardzhin_Bridges.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3,  --2,
				max = 3,  --4,
			},
			elements = {
				[1] = {
					name = "Rail Bridge Kardzhin MN 49",
					x = -144986.53125,
					y = 816502.625,
				},
			},
		},
		-- ["CVN-74 John C. Stennis Alert"] = {
			-- task = "Intercept",
			-- priority = 10,
			-- attributes = {},
			-- firepower = {
				-- min = 2,
				-- max = 2,
			-- },
			-- base = "CVN-74 John C. Stennis",
			-- radius = 250000,
		-- },
		-- ["Sukhumi 100"] = {
			-- task = "Intercept",
			-- priority = 10,
			-- attributes = {},
			-- firepower = {
				-- min = 2,
				-- max = 4,
			-- },
			-- base = "Sukhumi",
			-- radius = 100000,
		-- },
			-- ["107 SA-3 Goa Site C-7 N433338 E0434288"] = {
			-- task = "Strike",
			-- priority = 6,
			-- attributes = {"SAM"},
			-- firepower = {
				-- min = 2,
				-- max = 6,
			-- },
			-- class = "vehicle",
			-- name = "107 SA-3 Goa Site C-7",
		-- },
		-- ["110 SA-3 Goa Site W-10 N440952 E0430940"] = {
			-- task = "Strike",
			-- priority = 6,
			-- attributes = {"SAM"},
			-- firepower = {
				-- min = 2,
				-- max = 6,
			-- },
			-- class = "vehicle",
			-- name = "110 SA-3 Goa Site W-10",
		-- },
		-- ["207 SA-6 Gainful Site R-1 N441526 E0431537"] = {
			-- task = "Strike",
			-- priority = 6,
			-- attributes = {"SAM"},
			-- firepower = {
				-- min = 2,
				-- max = 8,
			-- },
			-- class = "vehicle",
			-- name = "207 SA-6 Gainful Site R-1",
		-- },		
	},
	["red"] = {		
		["SUPPLY PLANT DAPNARI KM76"] = {
			task = "Strike",
			priority = 4,
			--picture = {"Prohladniy_Depot.png"},
			attributes = {"Structure"},
			firepower = {
				min = 4,
				max = 6,
			},
			class = "static",
			elements = {
				[1] = {
					name = "SUPPLY PLANT DAPNARI KM76",
				},
				[2] = {
					name = "SUPPLY PLANT DAPNARI KM76-1",
				},
				[3] = {
					name = "SUPPLY PLANT DAPNARI KM76-2",
				},
				[4] = {
					name = "SUPPLY PLANT DAPNARI KM76-3",
				},
				[5] = {
					name = "SUPPLY PLANT DAPNARI KM76-4",
				},
				[6] = {
					name = "SUPPLY PLANT DAPNARI KM76-5",
				},
				[7] = {
					name = "SUPPLY PLANT DAPNARI KM76-6",
				},
				[8] = {
					name = "SUPPLY PLANT DAPNARI KM76-7",
				},
				[9] = {
					name = "SUPPLY PLANT DAPNARI KM76-8",
				},
				[10] = {
					name = "SUPPLY PLANT DAPNARI KM76-9",
				},
				[11] = {
					name = "SUPPLY PLANT DAPNARI KM76-10",
				},
				[12] = {
					name = "SUPPLY PLANT DAPNARI KM76-11",
				},
				[13] = {
					name = "SUPPLY PLANT DAPNARI KM76-12",
				},
				[14] = {
					name = "SUPPLY PLANT DAPNARI KM76-13",
				},
				[15] = {
					name = "SUPPLY PLANT DAPNARI KM76-14",
				},
				[16] = {
					name = "SUPPLY PLANT DAPNARI KM76-15",
				},
				[17] = {
					name = "SUPPLY PLANT DAPNARI KM76-16",
				},
				[18] = {
					name = "SUPPLY PLANT DAPNARI KM76-17",
				},
				[19] = {
					name = "SUPPLY PLANT DAPNARI KM76-18",
				},
				[20] = {
					name = "SUPPLY PLANT DAPNARI KM76-19",
				},
				[21] = {
					name = "SUPPLY PLANT DAPNARI KM76-20",
				},
				[22] = {
					name = "SUPPLY PLANT DAPNARI KM76-21",
				},
				[23] = {
					name = "SUPPLY PLANT DAPNARI KM76-22",
				},
				[24] = {
					name = "SUPPLY PLANT DAPNARI KM76-23",
				},
				[25] = {
					name = "SUPPLY PLANT DAPNARI KM76-24",
				},
				[26] = {
					name = "SUPPLY PLANT DAPNARI KM76-25",
				},
				[27] = {
					name = "SUPPLY PLANT DAPNARI KM76-26",
				},							
			},
		},
		["SUPPLY PLANT MARNEULI ML89"] = {
			task = "Strike",
			priority = 4,
			--picture = {"Prohladniy_Depot.png"},
			attributes = {"Structure"},
			firepower = {
				min = 4,
				max = 6,
			},
			class = "static",
			elements = {
				[1] = {
					name = "SUPPLY PLANT MARNEULI ML89",
				},	
				[2] = {
					name = "SUPPLY PLANT MARNEULI ML89-1",
				},
				[3] = {
					name = "SUPPLY PLANT MARNEULI ML89-2",
				},
				[4] = {
					name = "SUPPLY PLANT MARNEULI ML89-3",
				},
				[5] = {
					name = "SUPPLY PLANT MARNEULI ML89-4",
				},
				[6] = {
					name = "SUPPLY PLANT MARNEULI ML89-5",
				},
				[7] = {
					name = "SUPPLY PLANT MARNEULI ML89-6",
				},
				[8] = {
					name = "SUPPLY PLANT MARNEULI ML89-7",
				},
				[9] = {
					name = "SUPPLY PLANT MARNEULI ML89-8",
				},
				[10] = {
					name = "SUPPLY PLANT MARNEULI ML89-9",
				},
				[11] = {
					name = "SUPPLY PLANT MARNEULI ML89-29",
				},
				[12] = {
					name = "SUPPLY PLANT MARNEULI ML89-11",
				},
				[13] = {
					name = "SUPPLY PLANT MARNEULI ML89-12",
				},
				[14] = {
					name = "SUPPLY PLANT MARNEULI ML89-13",
				},
				[15] = {
					name = "SUPPLY PLANT MARNEULI ML89-14",
				},
				[16] = {
					name = "SUPPLY PLANT MARNEULI ML89-15",
				},
				[17] = {
					name = "SUPPLY PLANT MARNEULI ML89-16",
				},
				[18] = {
					name = "SUPPLY PLANT MARNEULI ML89-17",
				},
				[19] = {
					name = "SUPPLY PLANT MARNEULI ML89-18",
				},
				[20] = {
					name = "SUPPLY PLANT MARNEULI ML89-19",
				},
				[21] = {
					name = "SUPPLY PLANT MARNEULI ML89-20",
				},
				[22] = {
					name = "SUPPLY PLANT MARNEULI ML89-21",
				},
				[23] = {
					name = "SUPPLY PLANT MARNEULI ML89-22",
				},
				[24] = {
					name = "SUPPLY PLANT MARNEULI ML89-23",
				},
				[25] = {
					name = "SUPPLY PLANT MARNEULI ML89-24",
				},
				[26] = {
					name = "SUPPLY PLANT MARNEULI ML89-25",
				},
				[27] = {
					name = "SUPPLY PLANT MARNEULI ML89-26",
				},
				[28] = {
					name = "SUPPLY PLANT MARNEULI ML89-27",
				},	
				[29] = {
					name = "SUPPLY PLANT MARNEULI ML89-28",
				},															
			},
		},
		["KHASHURI FARP LM84"] = {
			task = "Strike",
			priority = 6,
			--picture = {"FARP_Vladikavkaz.png"},
			attributes = {"soft"},
			firepower = {
				min = 3,
				max = 6,
			},
			class = "static",
			elements = {
				[1] = {
					name = "KHASHURI FARP LM84",
				},				
				[2] = {
					name = "KHASHURI FARP LM84-1",
				},				
				[3] = {
					name = "KHASHURI FARP LM84-2",
				},				
				[4] = {
					name = "KHASHURI FARP LM84-3",
				},				
				[5] = {
					name = "KHASHURI FARP LM84-4",
				},				
				[6] = {
					name = "KHASHURI FARP LM84-5",
				},				
				[7] = {
					name = "KHASHURI FARP LM84-6",
				},				
				[8] = {
					name = "KHASHURI FARP LM84-7",
				},				
				[9] = {
					name = "KHASHURI FARP LM84-8",
				},				
				[10] = {
					name = "KHASHURI FARP LM84-9",
				},				
				[11] = {
					name = "KHASHURI FARP LM84-10",
				},				
				[12] = {
					name = "KHASHURI FARP LM84-11",
				},				
			},
		},
		["GORI FARP MM25"] = {
			task = "Strike",
			priority = 6,
			--picture = {"FARP_Vladikavkaz.png"},
			attributes = {"SAM"},
			firepower = {
				min = 3,
				max = 6,
			},
			class = "static",
			elements = {
				[1] = {
					name = "GORI FARP MM25",
				},			
				[2] = {
					name = "GORI FARP MM25-1",
				},			
				[3] = {
					name = "GORI FARP MM25-2",
				},			
				[4] = {
					name = "GORI FARP MM25-3",
				},			
				[5] = {
					name = "GORI FARP MM25-4",
				},			
				[6] = {
					name = "GORI FARP MM25-5",
				},			
				[7] = {
					name = "GORI FARP MM25-6",
				},			
				[8] = {
					name = "GORI FARP MM25-7",
				},			
				[9] = {
					name = "GORI FARP MM25-8",
				},			
				[10] = {
					name = "GORI FARP MM25-9",
				},			
				[11] = {
					name = "GORI FARP MM25-11",
				},	
			},		
		},
		["AMBROLAURI FARP LN41"] = {
			task = "Strike",
			priority = 6,
			--picture = {"FARP_Vladikavkaz.png"},
			attributes = {"soft"},
			firepower = {
				min = 3,
				max = 6,
			},
			class = "static",
			elements = {
				[1] = {
					name = "AMBROLAURI FARP LN41",
				},
				[2] = {
					name = "AMBROLAURI FARP LN41-1",
				},
				[3] = {
					name = "AMBROLAURI FARP LN41-2",
				},
				[4] = {
					name = "AMBROLAURI FARP LN41-3",
				},
				[5] = {
					name = "AMBROLAURI FARP LN41-4",
				},
				[6] = {
					name = "AMBROLAURI FARP LN41-5",
				},
				[7] = {
					name = "AMBROLAURI FARP LN41-6",
				},
				[8] = {
					name = "AMBROLAURI FARP LN41-7",
				},
				[9] = {
					name = "AMBROLAURI FARP LN41-8",
				},
				[10] = {
					name = "AMBROLAURI FARP LN41-9",
				},
				[11] = {
					name = "AMBROLAURI FARP LN41-11",
				},
				[12] = {
					name = "AMBROLAURI FARP LN41-12",
				},				
			},
		},
		["EWR-1 Site"] = {
			task = "Strike",
			priority = 5,
			attributes = {"soft"},
			firepower = {
				min = 2,
				max = 4,
			},
			class = "vehicle",
			name = "EWR-1",
		},
		["EWR-2 Site"] = {
			task = "Strike",
			priority = 5,
			attributes = {"soft"},
			firepower = {
				min = 2,
				max = 4,
			},
			class = "vehicle",
			name = "EWR-2",
		},
		["EWR-3 Site"] = {
			task = "Strike",
			priority = 5,
			attributes = {"soft"},
			firepower = {
				min = 2,
				max = 4,
			},
			class = "vehicle",
			name = "EWR-3",
		},
		["AWACS"] = {
			task = "AWACS",
			priority = 10,
			attributes = {},
			firepower = {
				min = 1,
				max = 1,
			},
			refpoint = "AWACS-RED",
			radius = 15000,
			text = "",
		},
		["CAP AWACS"] = {
			task = "CAP",
			priority = 10,
			attributes = {},
			firepower = {
				min = 2,
				max = 4,
			},
			refpoint = "CAP-AWACS",
			radius = 50000,
			text = "south AWACS",
			inactive = false,
		},
		["Mozdok Alert 200 Km"] = {
			task = "Intercept",
			priority = 5,
			attributes = {},
			firepower = {
				min = 3,
				max = 5,
			},
			base = "Mozdok",
			radius = 200000,
		},
		["Mozdok Alert 120 Km"] = {
			task = "Intercept",
			priority = 7,
			attributes = {},
			firepower = {
				min = 3,
				max = 5,
			},
			base = "Mozdok",
			radius = 120000,
		},
		["CAP Mozdok"] = {
			task = "CAP",
			priority = 20,
			attributes = {},
			firepower = {
				min = 2,
				max = 4,
			},
			refpoint = "CAP Mozdok",
			radius = 50000,
			text = "south Mozdok",
			inactive = true,
		},
		["Sweep South"] = {
			task = "Fighter Sweep",
			priority = 1,
			attributes = {},
			firepower = {
				min = 3,
				max = 5,
			},
			x = -246773,
			y = 864192,
			text = "in the south area",
		},
		["Nalchik Alert 200 Km"] = {
			task = "Intercept",
			priority = 7,
			attributes = {},
			firepower = {
				min = 3,
				max = 5,
			},
			base = "Nalchik",
			radius = 200000,
		},
		["Mineralnye-Vody Alert 280 Km"] = {
			task = "Intercept",
			priority = 4,
			attributes = {},
			firepower = {
				min = 3,
				max = 5,
			},
			base = "Mineralnye-Vody",
			radius = 280000,
		},
		["Beslan Alert 120 Km"] = {
			task = "Intercept",
			priority = 7,
			attributes = {},
			firepower = {
				min = 3,
				max = 5,
			},
			base = "Beslan",
			radius = 120000,
		},
		["CAP Beslan"] = {
			task = "CAP",
			priority = 10,
			attributes = {},
			firepower = {
				min = 3,
				max = 5,
			},
			refpoint = "CAP Beslan",
			radius = 50000,
			text = "South West Beslan",
			--inactive = true,
		},
		["Mineralnye-Vody Alert 200 Km"] = {
			task = "Intercept",
			priority = 5,
			attributes = {},
			firepower = {
				min = 3,
				max = 5,
			},
			base = "Mineralnye-Vody",
			radius = 200000,
		},
		["CAP Mineralnye-Vody"] = {
			task = "CAP",
			priority = 7,
			attributes = {},
			firepower = {
				min = 2,
				max = 4,
			},
			refpoint = "CAP Mineralnye-Vody",
			radius = 50000,
			text = "south east Mineralnye-Vody",
			inactive = true,
		},
		["Nalchik Alert 100 Km"] = {
			task = "Intercept",
			priority = 6,
			attributes = {},
			firepower = {
				min = 3,
				max = 5,
			},
			base = "Nalchik",
			radius = 100000,
		},
		["CAP Nalchik"] = {
			task = "CAP",
			priority = 6,
			attributes = {},
			firepower = {
				min = 2,
				max = 4,
			},
			refpoint = "CAP Nalchik",
			radius = 50000,
			text = "south east Nalchik",
			inactive = true,
		},
		["CAP Center"] = {
			task = "CAP",
			priority = 7,
			attributes = {},
			firepower = {
				min = 2,
				max = 4,
			},
			refpoint = "CAP Center",
			radius = 50000,
			text = "over Center front",
			--inactive = true,
		},		
		["Airlift Beslan"] = {
			task = "Transport",
			priority = 1,
			attributes = {},
			firepower = {
				min = 1,
				max = 1,
			},
			base = "Maykop-Khanskaya",
			destination = "Beslan",
		},
		["Airlift Mineralnye-Vody"] = {
			task = "Transport",
			priority = 1,
			attributes = {},
			firepower = {
				min = 1,
				max = 1,
			},
			base = "Beslan",
			destination = "Mineralnye-Vody",
		},
		["Tbilissi-Lochini OCA Strike"] = {
			task = "Strike",
			priority = 1,
			attributes = {"Parked Aircraft"},
			firepower = {
				min = 3,
				max = 6,
			},
			class = "airbase",
			name = "Tbilissi-Lochini",
		},
		["Sukhumi OCA Strike"] = {
			task = "Strike",
			priority = 1,
			attributes = {"Parked Aircraft"},
			firepower = {
				min = 3,
				max = 6,
			},
			class = "airbase",
			name = "Sukhumi",
		},
		["Vaziani OCA Strike"] = {
			task = "Strike",
			priority = 1,
			attributes = {"Parked Aircraft"},
			firepower = {
				min = 3,
				max = 6,
			},
			class = "airbase",
			name = "Vaziani",
		},
		["Kutaisi OCA Strike"] = {
			task = "Strike",
			priority = 1,
			attributes = {"Parked Aircraft"},
			firepower = {
				min = 3,
				max = 6,
			},
			class = "airbase",
			name = "Kutaisi",
		},
		["Senaki-Kolkhi OCA Strike"] = {
			task = "Strike",
			priority = 1,
			attributes = {"Parked Aircraft"},
			firepower = {
				min = 3,
				max = 6,
			},
			class = "airbase",
			name = "Senaki-Kolkhi",
		},
		["CVN-71 Theodore Roosevelt"] = { -- was TF-71
			task = "Anti-ship Strike",
			priority = 1,
			attributes = {"ship"},
			firepower = {
				min = 3,
				max = 6,
			},
			class = "ship",
			name = "TF-71",
		},
		["CVN-74 John C. Stennis"] = { -- was TF-74
			task = "Anti-ship Strike",
			priority = 1,
			attributes = {"ship"},
			firepower = {
				min = 3,
				max = 6,
			},
			class = "ship",
			name = "TF-74",
		},
		["LHA-Group"] = {
			task = "Anti-ship Strike",
			priority = 1,
			attributes = {"ship"},
			firepower = {
				min = 3,
				max = 6,
			},
			class = "ship",
			name = "LHA-Group",
		},
		["NATO Convoy 1"] = {
			task = "Anti-ship Strike",
			priority = 1,
			attributes = {"ship"},
			firepower = {
				min = 3,
				max = 6,
			},
			class = "ship",
			name = "NATO Convoy 1",
		},
		["Hawk Site Kutaisi"] = {
			task = "Strike",
			priority = 6,
			attributes = {"SAM"},
			firepower = {
				min = 3,
				max = 6,
			},
			class = "vehicle",
			name = "Hawk Site Kutaisi",
		},
		["Rapier Site Tabakhmela"] = {
			task = "Strike",
			priority = 6,
			attributes = {"SAM"},
			firepower = {
				min = 3,
				max = 6,
			},
			class = "vehicle",
			name = "Rapier Site Tabakhmela",
		},
		["Vaziani Defenses"] = {
			task = "Strike",
			priority = 2,
			attributes = {"SAM"},
			firepower = {
				min = 3,
				max = 6,
			},
			class = "vehicle",
			name = "Vaziani Defenses",
		},
		["Tbilisi Defenses"] = {
			task = "Strike",
			priority = 2,
			attributes = {"SAM"},
			firepower = {
				min = 3,
				max = 6,
			},
			class = "vehicle",
			name = "Tbilisi Defenses",
		},
		["Sukhumi Defenses"] = {
			task = "Strike",
			priority = 2,
			attributes = {"SAM"},
			firepower = {
				min = 3,
				max = 6,
			},
			class = "vehicle",
			name = "Sukhumi Defenses",
		},
		["Kobuleti Defenses"] = {
			task = "Strike",
			priority = 2,
			attributes = {"SAM"},
			firepower = {
				min = 3,
				max = 6,
			},
			class = "vehicle",
			name = "Kobuleti Defenses",
		},
		["Batumi Air Defenses"] = {
			task = "Strike",
			priority = 2,
			attributes = {"SAM"},
			firepower = {
				min = 3,
				max = 6,
			},
			class = "vehicle",
			name = "Batumi Air Defenses",
		},
		["Kutaisi Defenses"] = {
			task = "Strike",
			priority = 2,
			attributes = {"SAM"},
			firepower = {
				min = 3,
				max = 6,
			},
			class = "vehicle",
			name = "Kutaisi Defenses",
		},
		["Senaki Defenses"] = {
			task = "Strike",
			priority = 2,
			attributes = {"SAM"},
			firepower = {
				min = 3,
				max = 6,
			},
			class = "vehicle",
			name = "Senaki Defenses",
		},
		["Rapier Site bridge Vartsihe Geguti"] = {
			task = "Strike",
			priority = 6,
			attributes = {"SAM"},
			firepower = {
				min = 3,
				max = 6,
			},
			class = "vehicle",
			name = "Rapier Site bridge Vartsihe Geguti",
		},
		["GORI AA"] = {
			task = "Strike",
			priority = 2,
			attributes = {"SAM"},
			firepower = {
				min = 3,
				max = 4,
			},
			class = "vehicle",
			name = "GORI AA",
		},
		["KHASHURI FARP AA"] = {
			task = "Strike",
			priority = 2,
			attributes = {"SAM"},
			firepower = {
				min = 3,
				max = 4,
			},
			class = "vehicle",
			name = "KHASHURI FARP AA",
		},
		["AMBROLAURI FARP AA"] = {
			task = "Strike",
			priority = 2,
			attributes = {"SAM"},
			firepower = {
				min = 3,
				max = 4,
			},
			class = "vehicle",
			name = "AMBROLAURI FARP AA",
		},
		["10 US Army ELINT Station"] = {
			task = "Strike",
			priority = 5,
			attributes = {"soft"},
			firepower = {
				min = 3,
				max = 4,
			},
			class = "static",
			elements = {
				[1] = {
					name = "US ELINT Antenna Truck 1",
				},
				[2] = {
					name = "US ELINT Antenna Truck 2",
				},
				[3] = {
					name = "US ELINT Crew Van",
				},
				[4] = {
					name = "US ELINT Equipment Van",
				},
				[5] = {
					name = "US ELINT Generator Truck",
				},
			},
		},
		["11 1st Artillery Division/1.Btry"] = {
			task = "Strike",
			priority = 1,
			attributes = {"soft"},
			firepower = {
				min = 3,
				max = 4,
			},
			class = "vehicle",
			name = "11 1st Artillery Division/1.Btry",
		},
		["12 1st Artillery Division/2.Btry"] = {
			task = "Strike",
			priority = 1,
			attributes = {"soft"},
			firepower = {
				min = 2,
				max = 4,
			},
			class = "vehicle",
			name = "12 1st Artillery Division/2.Btry",
		},
		["13 1st Artillery Division/3.Btry"] = {
			task = "Strike",
			priority = 1,
			attributes = {"soft"},
			firepower = {
				min = 2,
				max = 4,
			},
			class = "vehicle",
			name = "13 1st Artillery Division/3.Btry",
		},
		["14 1st Artillery Division/4.Btry"] = {
			task = "Strike",
			priority = 1,
			attributes = {"soft"},
			firepower = {
				min = 2,
				max = 4,
			},
			class = "vehicle",
			name = "14 1st Artillery Division/4.Btry",
		},
		["15 1st Artillery Division/5.Btry"] = {
			task = "Strike",
			priority = 1,
			attributes = {"soft"},
			firepower = {
				min = 2,
				max = 4,
			},
			class = "vehicle",
			name = "15 1st Artillery Division/5.Btry",
		},
		["16 1st Artillery Division/6.Btry"] = {
			task = "Strike",
			priority = 1,
			attributes = {"soft"},
			firepower = {
				min = 2,
				max = 4,
			},
			class = "vehicle",
			name = "16 1st Artillery Division/6.Btry",
		},
		["17 1st Artillery Division/7.Btry"] = {
			task = "Strike",
			priority = 1,
			attributes = {"soft"},
			firepower = {
				min = 2,
				max = 4,
			},
			class = "vehicle",
			name = "17 1st Artillery Division/7.Btry",
		},
		["18 1st Artillery Division/8.Btry"] = {
			task = "Strike",
			priority = 1,
			attributes = {"soft"},
			firepower = {
				min = 2,
				max = 4,
			},
			class = "vehicle",
			name = "18 1st Artillery Division/8.Btry",
		},
		["19 4th Army HQ"] = {
			task = "Strike",
			priority = 6,
			attributes = {"soft"},
			firepower = {
				min = 2,
				max = 4,
			},
			class = "vehicle",
			name = "19 4th Army HQ",
		},		
		["Leselidze Train Station - EJ80"] = {
			task = "Strike",
			priority = 1,
			picture = {"Leselidze Train Station.png"},
			attributes = {"Structure"},
			firepower = {
				min = 3,
				max = 4,
			},
			elements = {
				[1] = {
					name = "Leselidze Train Station Hangar 1",
					x = -169643.34375,
					y = 470197.90625,
				},
				[2] = {
					name = "Leselidze Train Station Hangar 2",
					x = -169649.5,
					y = 470258.59375,
				},
				[3] = {
					name = "Leselidze Train Station Hangar 3",
					x = -169836.35205078,
					y = 470377.88964844,
				},
				[4] = {
					name = "Leselidze Train Station Hangar 4",
					x = -169724.6875,
					y = 470219.125,
				},
			},
		},
		["Bzyb Train Station - FH18"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bzyb Train Station.png"},
			attributes = {"Structure"},
			firepower = {
				min = 3,
				max = 4,
			},
			elements = {
				[1] = {
					name = "Bzyb Train Station Hangar 1",
					x = -185802.78125,
					y = 497412.5,
				},
				[2] = {
					name = "Bzyb Train Station Hangar 2",
					x = -185798.53125,
					y = 497473.34375,
				},
				[3] = {
					name = "Bzyb Train Station Hangar 3",
					x = -185871.625,
					y = 497466.28125,
				},
				[4] = {
					name = "Bzyb Train Station Hangar 4",
					x = -185871.046875,
					y = 497421.78125,
				},
			},
		},
		["Adzhkhahara Train Station - FH28"] = {
			task = "Strike",
			priority = 1,
			picture = {"Adzhkhahara Train Station.png"},
			attributes = {"Structure"},
			firepower = {
				min = 3,
				max = 6,
			},
			elements = {
				[1] = {
					name = "Adzhkhahara Train Station Hangar 1",
					x = -186107.1875,
					y = 508142.1875,
				},
				[2] = {
					name = "Adzhkhahara Train Station Hangar 2",
					x = -186052.78125,
					y = 508035.40625,
				},
				[3] = {
					name = "Adzhkhahara Train Station Hangar 3",
					x = -186081.21875,
					y = 508089.34375,
				},
				[4] = {
					name = "Adzhkhahara Train Station Hangar 4",
					x = -186135.640625,
					y = 508196.125,
				},
				[5] = {
					name = "Adzhkhahara Train Station Hangar 5",
					x = -186151.65625,
					y = 508070.03125,
				},
				[6] = {
					name = "Adzhkhahara Train Station Hangar 6",
					x = -186114.59375,
					y = 507998.1875,
				},
			},
		},	
		["Gudauta Train Station - FH37"] = {
			task = "Strike",
			priority = 1,
			picture = {"Gudauta Train Station.png"},
			attributes = {"Structure"},
			firepower = {
				min = 3,
				max = 6,
			},
			elements = {
				[1] = {
					name = "Gudauta Train Station Hangar 1",
					x = -196995.96875,
					y = 519848.40625,
				},
				[2] = {
					name = "Gudauta Train Station Hangar 2",
					x = -196992.15625,
					y = 519787.53125,
				},
				[3] = {
					name = "Gudauta Train Station Hangar 3",
					x = -196930.96875,
					y = 519884.96875,
				},
				[4] = {
					name = "Gudauta Train Station Hangar 4",
					x = -196930.875,
					y = 519927.5625,
				},
				[5] = {
					name = "Gudauta Train Station Hangar 5",
					x = -197092.15625,
					y = 519718.28125,
				},
				[6] = {
					name = "Gudauta Train Station Hangar 6",
					x = -197092.15625,
					y = 519749.53125,
				},
				[7] = {
					name = "Gudauta Train Station Hangar 7",
					x = -197040.53125,
					y = 519628.59375,
				},
				[8] = {
					name = "Gudauta Train Station Hangar 8",
					x = -197092.82836914,
					y = 519652.375,
				},
				[9] = {
					name = "Gudauta Train Station Hangar 9",
					x = -197092.82836914,
					y = 519671.90625,
				},
				[10] = {
					name = "Gudauta Train Station Hangar 10",
					x = -197092.82836914,
					y = 519690.9375,
				},
				[11] = {
					name = "Gudauta Train Station Hangar 11",
					x = -197055.8125,
					y = 519824.65625,
				},
			},
		},
		["Novyy Afon Train Station - FH57"] = {
			task = "Strike",
			priority = 1,
			picture = {"Novyy Afon Train Station.png"},
			attributes = {"Structure"},
			firepower = {
				min = 3,
				max = 6,
			},
			elements = {
				[1] = {
					name = "Novyy Afon Train Station Hangar 1",
					x = -198444.3125,
					y = 538777.375,
				},
				[2] = {
					name = "Novyy Afon Train Station Hangar 2",
					x = -198418.21875,
					y = 538722.25,
				},
				[3] = {
					name = "Novyy Afon Train Station Hangar 3",
					x = -198356.1875,
					y = 538764.75,
				},
				[4] = {
					name = "Novyy Afon Train Station Hangar 4",
					x = -198378.46875,
					y = 538803.25,
				},
			},
		},
		["Gumista Train Station - FH56"] = {
			task = "Strike",
			priority = 1,
			picture = {"Gumista Train Station.png"},
			attributes = {"Structure"},
			firepower = {
				min = 3,
				max = 6,
			},
			elements = {
				[1] = {
					name = "Gumista Train Station Hangar 1",
					x = -203787.28125,
					y = 547048.4375,
				},
				[2] = {
					name = "Gumista Train Station Hangar 2",
					x = -203761.8125,
					y = 546993,
				},
				[3] = {
					name = "Gumista Train Station Hangar 3",
					x = -203899.54248047,
					y = 546970.57617188,
				},
				[4] = {
					name = "Gumista Train Station Hangar 4",
					x = -203867.72363281,
					y = 546904.91210938,
				},
				[5] = {
					name = "Gumista Train Station Hangar 5",
					x = -203849.30273438,
					y = 546948.3125,
				},
			},
		},
		["Sukhumi Train Station - FH66"] = {
			task = "Strike",
			priority = 1,
			picture = {"Sukhumi Train Station.png"},
			attributes = {"Structure"},
			firepower = {
				min = 3,
				max = 6,
			},
			elements = {
				[1] = {
					name = "Sukhumi Train Station Hangar 1",
					x = -204884.0625,
					y = 554344.375,
				},
				[2] = {
					name = "Sukhumi Train Station Hangar 2",
					x = -204955.125,
					y = 554377.1875,
				},
				[3] = {
					name = "Sukhumi Train Station Hangar 3",
					x = -204968.50488281,
					y = 554325.88476563,
				},
				[4] = {
					name = "Sukhumi Train Station Hangar 4",
					x = -204995.84375,
					y = 554283,
				},
				[5] = {
					name = "Sukhumi Train Station Hangar 5",
					x = -204949.65007019,
					y = 554210.63818359,
				},
			},
		},
		["Kvemo-Merheuli Train Station - FH66"] = {
			task = "Strike",
			priority = 1,
			picture = {"Kvemo-Merheuli Train Station.png"},
			attributes = {"Structure"},
			firepower = {
				min = 3,
				max = 4,
			},
			elements = {
				[1] = {
					name = "Kvemo-Merheuli Train Station Hangar 1",
					x = -207974.40625,
					y = 557894.3125,
				},
				[2] = {
					name = "Kvemo-Merheuli Train Station Hangar 2",
					x = -208008.9375,
					y = 557919.25,
				},
				[3] = {
					name = "Kvemo-Merheuli Train Station Hangar 3",
					x = -207881.71875,
					y = 557755.5,
				},
				[4] = {
					name = "Kvemo-Merheuli Train Station Hangar 4",
					x = -207933.375,
					y = 557787.875,
				},
			},
		},			
		["Sukhumi-Babushara Train Station - FH74"] = {
			task = "Strike",
			priority = 1,
			picture = {"Sukhumi-Babushara Train Station.png"},
			attributes = {"Structure"},
			firepower = {
				min = 3,
				max = 6,
			},
			elements = {
				[1] = {
					name = "Sukhumi-Babushara Train Station Hangar 1",
					x = -219071.4375,
					y = 565464.4375,
				},
				[2] = {
					name = "Sukhumi-Babushara Train Station Hangar 2",
					x = -219023.4375,
					y = 565426.8125,
				},
				[3] = {
					name = "Sukhumi-Babushara Train Station Hangar 3",
					x = -219005.28125,
					y = 565502.9375,
				},
				[4] = {
					name = "Sukhumi-Babushara Train Station Hangar 4",
					x = -219001.41796875,
					y = 565629.19628906,
				},
				[5] = {
					name = "Sukhumi-Babushara Train Station Hangar 5",
					x = -219245.6875,
					y = 565555.05175781,
				},
				[6] = {
					name = "Sukhumi-Babushara Train Station Hangar 6",
					x = -219235.99511719,
					y = 565595.43847656,
				},
				[7] = {
					name = "Sukhumi-Babushara Train Station Fuel Tank 1",
					x = -219203.48779297,
					y = 565530.51834106,
				},
				[8] = {
					name = "Sukhumi-Babushara Train Station Fuel Tank 2",
					x = -219196.45996094,
					y = 565561.22433472,
				},
				[9] = {
					name = "Sukhumi-Babushara Train Station Fuel Tank 3",
					x = -219146.88867188,
					y = 565517.56420898,
				},
			},
		},
		["Senaki-Kolkhi Train Station - KM58"] = {
			task = "Strike",
			priority = 2,
			picture = {"Senaki-Kolkhi Train Station.png"},
			attributes = {"Structure"},
			firepower = {
				min = 3,
				max = 6,
			},
			elements = {
				[1] = {
					name = "Senaki-Kolkhi Train Station Hangar 1",
					x = -278439.875,
					y = 648014.0625,
				},
				[2] = {
					name = "Senaki-Kolkhi Train Station Hangar 2",
					x = -278455.3125,
					y = 647955,
				},
				[3] = {
					name = "Senaki-Kolkhi Train Station Hangar 3",
					x = -278521.20019531,
					y = 648174.72851563,
				},
				[4] = {
					name = "Senaki-Kolkhi Train Station Hangar 4",
					x = -278343.05957031,
					y = 648212.17578125,
				},
				[5] = {
					name = "Senaki-Kolkhi Train Station Hangar 5",
					x = -278502.85058594,
					y = 648053.55078125,
				},
				[6] = {
					name = "Senaki-Kolkhi Train Station Hangar 6",
					x = -278530.84375,
					y = 647975.75,
				},
				[7] = {
					name = "Senaki-Kolkhi Train Station Fuel Tank 1",
					x = -278419.37255859,
					y = 647905.97418213,
				},
				[8] = {
					name = "Senaki-Kolkhi Train Station Fuel Tank 2",
					x = -278418.84960938,
					y = 647877.89447021,
				},
				[9] = {
					name = "Senaki-Kolkhi Train Station Fuel Tank 3",
					x = -278398.14453125,
					y = 647870.21691895,
				},
				[10] = {
					name = "Senaki-Kolkhi Train Station Fuel Tank 4",
					x = -278397.734375,
					y = 647898.79650879,
				},
				[11] = {
					name = "Senaki-Kolkhi Train Station Hangar 7",
					x = -278609.26757813,
					y = 648182.73242188,
				},
			},
		},
		["Kobuleti Train Station - GG44"] = {
			task = "Strike",
			priority = 2,
			picture = {" Kobuleti Train Station.png"},
			attributes = {"Structure"},
			firepower = {
				min = 3,
				max = 6,
			},
			elements = {
				[1] = {
					name = "Kobuleti Train Station Hangar 1",
					x = -316275.96289063,
					y = 638171.36035156,
				},
				[2] = {
					name = "Kobuleti Train Station Hangar 2",
					x = -316280.92919922,
					y = 638212.02636719,
				},
				[3] = {
					name = "Kobuleti Train Station Hangar 3",
					x = -316282.33740234,
					y = 638238.39453125,
				},
				[4] = {
					name = "Kobuleti Train Station Hangar 4",
					x = -316283.07177734,
					y = 638260.47753906,
				},
				[5] = {
					name = "Kobuleti Train Station Hangar 5",
					x = -316336.25,
					y = 638392.6875,
				},
				[6] = {
					name = "Kobuleti Train Station Hangar 6",
					x = -316335.1875,
					y = 638495.125,
				},
				[7] = {
					name = "Kobuleti Train Station Hangar 7",
					x = -316337,
					y = 638439.0625,
				},
			},
		},		
		["bridge GORI"] = {--{supply line  gori
			task = "Strike",
			priority = 6,
			--picture = {"Bridges positions EJ80-EH99.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3,
				max = 6,
			},
			elements = {
				[1] = {
					name = "bridge little river",
					x = -289338.90250721,
					y = 821231.45182713,
				},
				[2] = {
					name = "bridge big river",
					x = -290558.91171324,
					y = 820769.67147346,
				},
			},
		},		
		["Bridge Supply Line Gori - Tbilisi"] =  {--{supply line  gori
			task = "Strike",
			priority = 6,
			--picture = {"Bridges positions EJ80-EH99.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 4,
				max = 8,
			},			
			elements = {
				[1] = {
					name = "Bridge Supply Line Gori - Tbilisi-1",
					x = -291901.15661608,
					y = 836269.95717029,
				},
				[2] = {
					name = "Bridge Supply Line Gori - Tbilisi-2",
					x = -293785.15756579,
					y = 848374.93828642,
				},
				[3] = {
					name = "Bridge Supply Line Gori - Tbilisi-3",
					x = -299055.94360335,
					y = 864280.68645882,
				},
				[4] = {
					name = "Bridge Supply Line Gori - Tbilisi-4",
					x = -299277.05648133,
					y = 872977.58810726,
				},
				[5] = {
					name = "Bridge Supply Line Gori - Tbilisi-5",
					x = -300308.92274769,
					y = 878191.35657638,
				},
			},
		},		
		["bridge TKIBULI"] = { -- supply line kutaisi - farp ambrolauri
			task = "Strike",
			priority = 6,
			--picture = {"Bridges positions EJ80-EH99.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3,
				max = 6,
			},
			elements = {
				[1] = {
					name = "bridge TKIBULI river", -- cambia il nome
					x = -263345.09071519,
					y = 722875.74340048,				
				},
				[2] = {
					name = "bridge TKIBULI lake", -- cambia il nome
					x = -263318.92491384,
					y = 722806.48098515,				
				},
			},							
		},		
		["Bridge Supply Line Marneuli - Tbilisi"] = { -- kutaisi - farp ambrolauri
			task = "Strike",
			priority = 6,
			--picture = {"Bridges positions EJ80-EH99.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 4,
				max = 8,
			},
			elements = {
				[1] = {
					name = "Bridge Supply Line Marneuli - Tbilisi-1", -- cambia il nome
					x = -324597.40552542,
					y = 882950.48548748,				
				},					
				[2] = {
					name = "Bridge Supply Line Marneuli - Tbilisi-2", -- cambia il nome
					x = -317070.77633033,
					y = 891234.90923188,				
				},					
				[3] = {
					name = "Bridge Supply Line Marneuli - Tbilisi-3", -- cambia il nome
					x = -313485.95939054,
					y = 883397.98896592,				
				},	
			},								
		},		
		["Rail Bridge Dapnari-KM76"] = { --supply line kobuleti - kutaisi
			task = "Strike",
			priority = 6,
			picture = {"Bridges positions Dapnari-KM76.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3,
				max = 6,
			},
			elements = {
				[1] = {
					name = "Rail Bridge Dapnari North part-KM76",
					x = -292722.10351563,
					y = 671988.8125,
				},
				[2] = {
					name = "Rail Bridge Dapnari Center part-KM76",
					x = -292822.03710938,
					y = 671985.1875,
				},
				[3] = {
					name = "Rail Bridge Dapnari South part-KM76",
					x = -292921.97070313,
					y = 671981.56445313,
				},
			},
		},		
		["Bridge Dapnari-KM76"] = { --supply line kobuleti - kutaisi
			task = "Strike",
			priority = 6,
			picture = {"Bridges positions Dapnari-KM76.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3,
				max = 6,
			},
			elements = {
				[1] = {
					name = "Bridge Dapnari North part-KM76",
					x = -292658.8359375,
					y = 672266.87695313,
				},
				[2] = {
					name = "Bridge Dapnari South part-KM76",
					x = -292795.8515625,
					y = 672238.12304688,
				},
			},
		},
		["Bridge Vartsihe-LM16"] = { --supply line kutaisi - farp khashuri, gor
			task = "Strike",
			priority = 6,
			picture = {"Bridges positions LM16-LM17-LM18.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3,
				max = 6,
			},
			elements = {
				[1] = {
					name = "Bridge Vartsihe West part-LM16",
					x = -285269.1875,
					y = 702893.90625,
				},
				[2] = {
					name = "Bridge Vartsihe Center West part-LM16",
					x = -285340.36523438,
					y = 703014.46484375,
				},
				[3] = {
					name = "Bridge Vartsihe Center East part-LM16",
					x = -285411.54101563,
					y = 703135.01953125,
				},
				[4] = {
					name = "Bridge Vartsihe East part-LM16",
					x = -285482.71875,
					y = 703255.578125,
				},
			},
		},				
		["Bridge Geguti-LM17"] = {--supply line kutaisi - farp khashuri, gori
			task = "Strike",
			priority = 6,
			--picture = {"Bridges positions LM16-LM17-LM18.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3,
				max = 6,
			},
			elements = {
				[1] = {
					name = "Bridge Geguti North part-LM17",
					x = -282606.98828125,
					y = 704785.0078125,
				},
				[2] = {
					name = "Bridge Geguti Center part-LM17",
					x = -282733.71875,
					y = 704844.5,
				},
				[3] = {
					name = "Bridge Geguti South part-LM17",
					x = -282860.44921875,
					y = 704903.9921875,
				},
			},
		},
		["Bridge Kutaisi-LM18"] = {--supply line -kutaisi -ambrolauri
			task = "Strike",
			priority = 6,
			--picture = {"Bridges positions LM16-LM17-LM18.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3,
				max = 6,
			},
			elements = {
				[1] = {
					name = "Bridge Kutaisi West part-LM18",
					x = -274859.59277344,
					y = 701001.1796875,
				},
				[2] = {
					name = "Bridge Kutaisi East part-LM18",
					x = -274873.90722656,
					y = 701140.4453125,
				},
			},
		},
		["Rail Bridge North Geguti-LM17"] = {--supply line kutaisi - farp khashuri, gori
			task = "Strike",
			priority = 6,
			picture = {"Bridges positions LM16-LM17-LM18.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3,
				max = 6,
			},
			elements = {
				[1] = {
					name = "Rail Bridge North Geguti West part-LM17",
					x = -280436.1328125,
					y = 701658.0546875,
				},
				[2] = {
					name = "Rail Bridge North Geguti Center part-LM17",
					x = -280394.33398438,
					y = 701748.8984375,
				},
				[3] = {
					name = "Rail Bridge North Geguti East part-LM17",
					x = -280352.53515625,
					y = 701839.7421875,
				},
			},
		},
		["Bridge Koki-GH20"] = { --supply line sukhumi -senaki
			task = "Strike",
			priority = 6,
			picture = {"Bridge positions GG19-GH10-GH20-GH21-GH31-GH42.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3,
				max = 6,
			},
			elements = {
				[1] = {
					name = "Bridge Koki North part-GH20",
					x = -255475.2109375,
					y = 616593.7421875,
				},
				[2] = {
					name = "Bridge Koki Center part-GH20",
					x = -255590.4296875,
					y = 616673.2734375,
				},
				[3] = {
					name = "Bridge Koki South part-GH20",
					x = -255705.6484375,
					y = 616752.796875,
				},
			},
		},
		["Rail Bridge Tagiloni-GH21"] = { --supply line sukhumi -senaki
			task = "Strike",
			priority = 6,
			picture = {"Bridge positions GG19-GH10-GH20-GH21-GH31-GH42.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 3,
				max = 6,
			},
			elements = {
				[1] = {
					name = "Rail Bridge Tagiloni North up part-GH21",
					x = -250657.7734375,
					y = 622172,
				},
				[2] = {
					name = "Rail Bridge Tagiloni North middle part-GH21",
					x = -250744.234375,
					y = 622222.2421875,
				},
				[3] = {
					name = "Rail Bridge Tagiloni North down part-GH21",
					x = -250830.6953125,
					y = 622272.4921875,
				},
				[4] = {
					name = "Rail Bridge Tagiloni South up part-GH21",
					x = -250917.15625,
					y = 622322.734375,
				},
				[5] = {
					name = "Rail Bridge Tagiloni South middle part-GH21",
					x = -251003.6171875,
					y = 622372.984375,
				},
				[6] = {
					name = "Rail Bridge Tagiloni South down part-GH21",
					x = -251090.078125,
					y = 622423.2265625,
				},
			},
		},
		["Sukhumi Airbase"] = {
			task = "Strike",
			priority = 4,
			picture = {"Sukhumi Airbase.png"},
			attributes = {"Structure"},
			firepower = {
				min = 3,
				max = 6,
			},
			elements = {
				[1] = {
					name = "Sukhumi Control Tower",
					x = -219668.28125,
					y = 563758.0625,
				},
				[2] = {
					name = "Sukhumi Main Ammo Depot",
					x = -219592.921875,
					y = 564007.3125,
				},
				[3] = {
					name = "Sukhumi Main Fuel Depot",
					x = -219594.640625,
					y = 564086.9375,
				},
				[4] = {
					name = "Sukhumi Hangar 1",
					x = -219719.84375,
					y = 564339.1875,
				},
				[5] = {
					name = "Sukhumi Hangar 2",
					x = -219773.015625,
					y = 564363.875,
				},
				[6] = {
					name = "Sukhumi Hangar 3",
					x = -219843.78125,
					y = 564393.9375,
				},
				[7] = {
					name = "Sukhumi Hangar 4",
					x = -219594.296875,
					y = 564065.0625,
				},
			},
		},
		["Sukhumi Airbase Strategics"] = {--supply plant
			task = "Strike",
			priority = 4,
			picture = {"Sukhumi Airbase.png"},
			attributes = {"Structure"},
			firepower = {
				min = 4,
				max = 8,
			},
			class = "static",
			elements = {
				[1] = {
					name = "Sukhumi Fuel Tank 1",
				},
				[2] = {
					name = "Sukhumi Fuel Tank 2",
				},
				[3] = {
					name = "Sukhumi Fuel Tank 3",
				},
				[4] = {
					name = "Sukhumi Fuel Tank 4",
				},
				[5] = {
					name = "Sukhumi Fuel Tank 5",
				},
				[6] = {
					name = "Sukhumi Fuel Tank 6",
				},
				[7] = {
					name = "Sukhumi Ammo Dump 1",
				},
				[8] = {
					name = "Sukhumi Ammo Dump 2",
				},
				[9] = {
					name = "Sukhumi Ammo Dump 3",
				},
				[10] = {
					name = "Sukhumi Ammo Dump 4",
				},
				[11] = {
					name = "Sukhumi Command Center",
				},
				[12] = {
					name = "Sukhumi Power Supply",
				},
			},
		},
		["Gudauta Airbase"] = {
			task = "Strike",
			priority = 1,
			picture = {"Gudauta Airbase South.png", "Gudauta Airbase North"},
			attributes = {"Structure"},
			firepower = {
				min = 4,
				max = 8,
			},
			elements = {
				[1] = {
					name = "Gudauta Control Tower",
					x = -196854.59375,
					y = 515805.6875,
				},
				[2] = {
					name = "Gudauta Main Ammo Depot",
					x = -196462.671875,
					y = 514975.65625,
				},
				[3] = {
					name = "Gudauta Ammo Depot 1",
					x = -196499.59375,
					y = 514970.40625,
				},
				[4] = {
					name = "Gudauta Ammo Depot 2",
					x = -196492.46875,
					y = 514964,
				},
				[5] = {
					name = "Gudauta Ammo Depot 3",
					x = -196478.40625,
					y = 514951.40625,
				},
				[6] = {
					name = "Gudauta Ammo Depot 4",
					x = -196485.53125,
					y = 514957.8125,
				},
				[7] = {
					name = "Gudauta Ammo Depot 5",
					x = -196457.453125,
					y = 515021.125,
				},
				[8] = {
					name = "Gudauta Ammo Depot 6",
					x = -196443.375,
					y = 515008.53125,
				},
				[9] = {
					name = "Gudauta Ammo Depot 7",
					x = -196450.328125,
					y = 515014.75,
				},
				[10] = {
					name = "Gudauta Ammo Depot 8",
					x = -196436.296875,
					y = 515002.125,
				},
				[11] = {
					name = "Gudauta Ammo Depot 9",
					x = -196550.5,
					y = 515104.625,
				},
				[12] = {
					name = "Gudauta Ammo Depot 10",
					x = -196543.375,
					y = 515098.21875,
				},
				[13] = {
					name = "Gudauta Ammo Depot 11",
					x = -196536.4375,
					y = 515092,
				},
				[14] = {
					name = "Gudauta Ammo Depot 12",
					x = -196529.3125,
					y = 515085.625,
				},
				[15] = {
					name = "Gudauta Ammo Depot 13",
					x = -196500.171875,
					y = 515059.5,
				},
				[16] = {
					name = "Gudauta Ammo Depot 14",
					x = -196507.125,
					y = 515065.71875,
				},
				[17] = {
					name = "Gudauta Ammo Depot 15",
					x = -196493.0625,
					y = 515053.09375,
				},
				[18] = {
					name = "Gudauta Ammo Depot 16",
					x = -196538.984375,
					y = 515005.59375,
				},
				[19] = {
					name = "Gudauta Ammo Depot 17",
					x = -196546.125,
					y = 515011.96875,
				},
				[20] = {
					name = "Gudauta Ammo Depot 18",
					x = -196566.625,
					y = 515077.96875,
				},
				[21] = {
					name = "Gudauta Fuel Depot 1",
					x = -198426.40625,
					y = 516965.21875,
				},
				[22] = {
					name = "Gudauta Fuel Depot 2",
					x = -198479.4375,
					y = 517047.53125,
				},
				[23] = {
					name = "Gudauta Fuel Depot 3",
					x = -198571.0625,
					y = 517098.375,
				},
				[24] = {
					name = "Gudauta Fuel Depot 4",
					x = -198611.3125,
					y = 517034,
				},
				[25] = {
					name = "Gudauta Power Supply",
					x = -198410.5,
					y = 516806.5,
				},
				[26] = {
					name = "Gudauta Hangar 1",
					x = -197271.71875,
					y = 515917.8125,
				},
				[27] = {
					name = "Gudauta Hangar 2",
					x = -197326.15625,
					y = 515835.875,
				},
				[28] = {
					name = "Gudauta Hangar 3",
					x = -197374.578125,
					y = 515832.21875,
				},
				[29] = {
					name = "Gudauta Hangar 4",
					x = -197416.390625,
					y = 515856.53125,
				},
				[30] = {
					name = "Gudauta Hangar 5",
					x = -197445.5,
					y = 515862.6875,
				},
				[31] = {
					name = "Gudauta Hangar 6",
					x = -197469.203125,
					y = 515867.90625,
				},
				[32] = {
					name = "Gudauta Hangar 7",
					x = -197491.546875,
					y = 515920.46875,
				},
				[33] = {
					name = "Gudauta Hangar 8",
					x = -197486.703125,
					y = 515958.34375,
				},
				[34] = {
					name = "Gudauta Command Center 1",
					x = -195456.59667969,
					y = 515649.80810547,
				},
				[35] = {
					name = "Gudauta Command Center 2",
					x = -195480.84228516,
					y = 515642.35498047,
				},
			},
		},
		["Senaki Airbase"] = {
			task = "Strike",
			priority = 1,
			picture = {"Senaki Airbase.png", "Senaki Airbase-Ammo"},
			attributes = {"Structure"},
			firepower = {
				min = 4,
				max = 8,
			},
			elements = {
				[1] = {
					name = "Senaki Control Tower",
					x = -280806.5625,
					y = 646965.25,
				},
				[2] = {
					name = "Senaki Main Ammo Depot",
					x = -282847.90625,
					y = 646751.875,
				},
				[3] = {
					name = "Senaki Ammo Depot 1",
					x = -282812.40625,
					y = 646740.4375,
				},
				[4] = {
					name = "Senaki Ammo Depot 2",
					x = -282816,
					y = 646749.3125,
				},
				[5] = {
					name = "Senaki Ammo Depot 3",
					x = -282823.125,
					y = 646766.8125,
				},
				[6] = {
					name = "Senaki Ammo Depot 4",
					x = -282819.53125,
					y = 646757.9375,
				},
				[7] = {
					name = "Senaki Ammo Depot 5",
					x = -282872.53125,
					y = 646713.3125,
				},
				[8] = {
					name = "Senaki Ammo Depot 6",
					x = -282879.65625,
					y = 646730.75,
				},
				[9] = {
					name = "Senaki Ammo Depot 7",
					x = -282876.125,
					y = 646722.125,
				},
				[10] = {
					name = "Senaki Ammo Depot 8",
					x = -282883.21875,
					y = 646739.625,
				},
				[11] = {
					name = "Senaki Ammo Depot 9",
					x = -282792.4375,
					y = 646691.5,
				},
				[12] = {
					name = "Senaki Ammo Depot 10",
					x = -282788.8125,
					y = 646682.625,
				},
				[13] = {
					name = "Senaki Ammo Depot 11",
					x = -282850.9375,
					y = 646660.0625,
				},
				[14] = {
					name = "Senaki Ammo Depot 12",
					x = -282854.53125,
					y = 646668.9375,
				},
				[15] = {
					name = "Senaki Ammo Depot 13",
					x = -282847.4375,
					y = 646651.4375,
				},
				[16] = {
					name = "Senaki Ammo Depot 14",
					x = -282825.5,
					y = 646597.4375,
				},
				[17] = {
					name = "Senaki Ammo Depot 15",
					x = -282829.09375,
					y = 646606.3125,
				},
				[18] = {
					name = "Senaki Ammo Depot 16",
					x = -282832.59375,
					y = 646614.9375,
				},
				[19] = {
					name = "Senaki Ammo Depot 17",
					x = -282836.21875,
					y = 646623.8125,
				},
				[20] = {
					name = "Senaki Ammo Depot 18",
					x = -282799.3125,
					y = 646614.375,
				},
				[21] = {
					name = "Senaki Fuel Depot 1",
					x = -280223.46875,
					y = 646882.5625,
				},
				[22] = {
					name = "Senaki Fuel Depot 2",
					x = -280257.1875,
					y = 646685.1875,
				},
				[23] = {
					name = "Senaki Fuel Depot 3",
					x = -280330.03125,
					y = 646706.8125,
				},
				[24] = {
					name = "Senaki Fuel Depot 4",
					x = -280305.5,
					y = 646808.625,
				},
				[25] = {
					name = "Senaki Power Supply",
					x = -281924.46875,
					y = 645939.3125,
				},
				[26] = {
					name = "Senaki Hangar 1",
					x = -280708.84375,
					y = 647660.1875,
				},
				[27] = {
					name = "Senaki Hangar 2",
					x = -280663,
					y = 647573.875,
				},
				[28] = {
					name = "Senaki Hangar 3",
					x = -280709.46875,
					y = 647200.5,
				},
				[29] = {
					name = "Senaki Hangar 4",
					x = -280812.5625,
					y = 647103.625,
				},
				[30] = {
					name = "Senaki Hangar 5",
					x = -280773.84375,
					y = 647140.5625,
				},
				[31] = {
					name = "Senaki Hangar 6",
					x = -281007.71875,
					y = 647236,
				},
				[32] = {
					name = "Senaki Hangar 7",
					x = -281047.84375,
					y = 647268.0625,
				},
				[33] = {
					name = "Senaki Hangar 8",
					x = -281449.625,
					y = 646244.5,
				},
				[34] = {
					name = "Senaki Command Center 1",
					x = -280573.5625,
					y = 647218.25,
				},
				[35] = {
					name = "Senaki Command Center 2",
					x = -280655.46875,
					y = 647088.125,
				},
				[36] = {
					name = "Senaki Communication Center",
					x = -281379.90625,
					y = 646323.0625,
				},
			},
		},
		["Kutaisi Airbase"] = {
			task = "Strike",
			priority = 4,
			picture = {"Kutaisi Airbase.png", "Kutaisi Airbase-AmmoFuel.png"},
			attributes = {"Structure"},
			firepower = {
				min = 4,
				max = 8,
			},
			elements = {
				[1] = {
					name = "Kutaisi Control Tower",
					x = -284566.3125,
					y = 683780.0625,
				},
				[2] = {
					name = "Kutaisi Main Ammo Depot",
					x = -285856.6875,
					y = 683802.875,
				},
				[3] = {
					name = "Kutaisi Ammo Depot 1",
					x = -285843.96875,
					y = 683828.9375,
				},
				[4] = {
					name = "Kutaisi Ammo Depot 2",
					x = -285853.15625,
					y = 683831.5625,
				},
				[5] = {
					name = "Kutaisi Ammo Depot 3",
					x = -285835,
					y = 683826.4375,
				},
				[6] = {
					name = "Kutaisi Ammo Depot 4",
					x = -285825.78125,
					y = 683823.75,
				},
				[7] = {
					name = "Kutaisi Ammo Depot 5",
					x = -285868.875,
					y = 683767.5625,
				},
				[8] = {
					name = "Kutaisi Ammo Depot 6",
					x = -285850.71875,
					y = 683762.375,
				},
				[9] = {
					name = "Kutaisi Ammo Depot 7",
					x = -285859.6875,
					y = 683764.875,
				},
				[10] = {
					name = "Kutaisi Ammo Depot 8",
					x = -285841.53125,
					y = 683759.6875,
				},
				[11] = {
					name = "Kutaisi Ammo Depot 9",
					x = -285765.75,
					y = 683806.6875,
				},
				[12] = {
					name = "Kutaisi Ammo Depot 10",
					x = -285774.96875,
					y = 683809.3125,
				},
				[13] = {
					name = "Kutaisi Ammo Depot 11",
					x = -285777.375,
					y = 683741.3125,
				},
				[14] = {
					name = "Kutaisi Ammo Depot 12",
					x = -285795.53125,
					y = 683746.5,
				},
				[15] = {
					name = "Kutaisi Ammo Depot 13",
					x = -285786.34375,
					y = 683743.875,
				},
				[16] = {
					name = "Kutaisi Ammo Depot 14",
					x = -285748.71875,
					y = 683733.0625,
				},
				[17] = {
					name = "Kutaisi Ammo Depot 15",
					x = -285739.5,
					y = 683730.5,
				},
				[18] = {
					name = "Kutaisi Ammo Depot 16",
					x = -285730.5625,
					y = 683727.875,
				},
				[19] = {
					name = "Kutaisi Ammo Depot 17",
					x = -285721.34375,
					y = 683725.25,
				},
				[20] = {
					name = "Kutaisi Ammo Depot 18",
					x = -285718.5,
					y = 683756.3125,
				},
				[21] = {
					name = "Kutaisi Fuel Depot 1",
					x = -285673.59375,
					y = 685097.1875,
				},
				[22] = {
					name = "Kutaisi Fuel Depot 2",
					x = -285763.34375,
					y = 685069.125,
				},
				[23] = {
					name = "Kutaisi Fuel Depot 3",
					x = -285847.0625,
					y = 685006.125,
				},
				[24] = {
					name = "Kutaisi Communication Center",
					x = -284333.28125,
					y = 683327.3125,
				},
				[25] = {
					name = "Kutaisi Power Supply",
					x = -284195.59375,
					y = 682949.75,
				},
				[26] = {
					name = "Kutaisi Hangar 1",
					x = -284214,
					y = 682983.375,
				},
				[27] = {
					name = "Kutaisi Hangar 2",
					x = -284263.5,
					y = 683027.0625,
				},
				[28] = {
					name = "Kutaisi Hangar 3",
					x = -284305.5,
					y = 682967.5,
				},
				[29] = {
					name = "Kutaisi Hangar 4",
					x = -284238.75,
					y = 683005.25,
				},
				[30] = {
					name = "Kutaisi Hangar 5",
					x = -284331.5,
					y = 683082.5,
				},
				[31] = {
					name = "Kutaisi Hangar 6",
					x = -284269.59375,
					y = 683079.8125,
				},
				[32] = {
					name = "Kutaisi Hangar 7",
					x = -284501.1875,
					y = 682949.125,
				},
				[33] = {
					name = "Kutaisi Command Center 1",
					x = -284312.34375,
					y = 682837.625,
				},
				[34] = {
					name = "Kutaisi Command Center 2",
					x = -284396.40625,
					y = 682946.3125,
				},
			},
		},
		["Kobuleti Airbase"] = {
			task = "Strike",
			priority = 2,
			picture = {"Kobuleti Airbase.png", "Kobuleti Airbase-Ammo-Hangar-Command.png"},
			attributes = {"Structure"},
			firepower = {
				min = 4,
				max = 8,
			},
			elements = {
				[1] = {
					name = "Kobuleti Control Tower",
					x = -317800.125,
					y = 635457.5625,
				},
				[2] = {
					name = "Kobuleti Main Ammo Depot",
					x = -316652.8125,
					y = 637940.9375,
				},
				[3] = {
					name = "Kobuleti Ammo Depot 1",
					x = -316586.8125,
					y = 637878.25,
				},
				[4] = {
					name = "Kobuleti Ammo Depot 2",
					x = -316591.34375,
					y = 637886.6875,
				},
				[5] = {
					name = "Kobuleti Ammo Depot 3",
					x = -316590.125,
					y = 637809.25,
				},
				[6] = {
					name = "Kobuleti Ammo Depot 4",
					x = -316614.375,
					y = 637789.75,
				},
				[7] = {
					name = "Kobuleti Ammo Depot 5",
					x = -316618.875,
					y = 637798.1875,
				},
				[8] = {
					name = "Kobuleti Ammo Depot 6",
					x = -316623.25,
					y = 637806.375,
				},
				[9] = {
					name = "Kobuleti Ammo Depot 7",
					x = -316627.78125,
					y = 637814.8125,
				},
				[10] = {
					name = "Kobuleti Ammo Depot 8",
					x = -316646.25,
					y = 637849.375,
				},
				[11] = {
					name = "Kobuleti Ammo Depot 9",
					x = -316650.75,
					y = 637857.8125,
				},
				[12] = {
					name = "Kobuleti Ammo Depot 10",
					x = -316641.84375,
					y = 637841.125,
				},
				[13] = {
					name = "Kobuleti Ammo Depot 11",
					x = -316673.28125,
					y = 637900,
				},
				[14] = {
					name = "Kobuleti Ammo Depot 12",
					x = -316682.1875,
					y = 637916.625,
				},
				[15] = {
					name = "Kobuleti Ammo Depot 13",
					x = -316677.78125,
					y = 637908.4375,
				},
				[16] = {
					name = "Kobuleti Ammo Depot 14",
					x = -316686.65625,
					y = 637925.125,
				},
				[17] = {
					name = "Kobuleti Ammo Depot 15",
					x = -316616.3125,
					y = 637933.25,
				},
				[18] = {
					name = "Kobuleti Ammo Depot 16",
					x = -316620.8125,
					y = 637941.75,
				},
				[19] = {
					name = "Kobuleti Ammo Depot 17",
					x = -316629.71875,
					y = 637958.375,
				},
				[20] = {
					name = "Kobuleti Ammo Depot 18",
					x = -316625.21875,
					y = 637949.9375,
				},
				[21] = {
					name = "Kobuleti Fuel Depot 1",
					x = -318647.5625,
					y = 635707.4375,
				},
				[22] = {
					name = "Kobuleti Fuel Depot 2",
					x = -318735.71875,
					y = 635640.9375,
				},
				[23] = {
					name = "Kobuleti Fuel Depot 3",
					x = -318769.03125,
					y = 635541.625,
				},
				[24] = {
					name = "Kobuleti Fuel Depot 4",
					x = -318698.34375,
					y = 635513.75,
				},
				[25] = {
					name = "Kobuleti Fuel Depot 5",
					x = -318607.25,
					y = 635575.75,
				},
				[26] = {
					name = "Kobuleti Fuel Depot 6",
					x = -318590.40625,
					y = 635620.1875,
				},
				[27] = {
					name = "Kobuleti Fuel Depot 7",
					x = -318404.875,
					y = 635401.125,
				},
				[28] = {
					name = "Kobuleti Communication Center",
					x = -318352.6875,
					y = 635388.125,
				},
				[29] = {
					name = "Kobuleti Hangar 1",
					x = -317209.8125,
					y = 636555.25,
				},
				[30] = {
					name = "Kobuleti Hangar 2",
					x = -317137.9375,
					y = 636613.625,
				},
				[31] = {
					name = "Kobuleti Hangar 3",
					x = -317170.21875,
					y = 636620.5625,
				},
				[32] = {
					name = "Kobuleti Hangar 4",
					x = -317297.65625,
					y = 636662.375,
				},
				[33] = {
					name = "Kobuleti Hangar 5",
					x = -317344.46875,
					y = 636576.6875,
				},
				[34] = {
					name = "Kobuleti Command Center 1",
					x = -317240.1875,
					y = 636446.875,
				},
				[35] = {
					name = "Kobuleti Command Center 2",
					x = -317284.6875,
					y = 636484.125,
				},
			},
		},
		["Batumi Airbase"] = {
			task = "Strike",
			priority = 2,
			picture = {"Batumi Airbase.png", "Batumi Airbase-Ammo.png"},
			attributes = {"Structure"},
			firepower = {
				min = 4,
				max = 8,
			},
			elements = {
				[1] = {
					name = "Batumi Control Tower",
					x = -355688.28125,
					y = 617693,
				},
				[2] = {
					name = "Batumi Main Ammo Depot",
					x = -355414.625,
					y = 617513.1875,
				},
				[3] = {
					name = "Batumi Ammo Depot 1",
					x = -355494.59375,
					y = 617445.625,
				},
				[4] = {
					name = "Batumi Ammo Depot 2",
					x = -355438.48291016,
					y = 617354.99682617,
				},
				[5] = {
					name = "Batumi Ammo Depot 3",
					x = -355382.0625,
					y = 617296.9375,
				},
				[6] = {
					name = "Batumi Fuel Depot 1",
					x = -355929.40625,
					y = 618273.875,
				},
				[7] = {
					name = "Batumi Fuel Depot 2",
					x = -355926.875,
					y = 618297.6875,
				},
				[8] = {
					name = "Batumi Power Supply",
					x = -355586.30224609,
					y = 617921.95751953,
				},
				[9] = {
					name = "Batumi Hangar 1",
					x = -356082.15625,
					y = 618377,
				},
				[10] = {
					name = "Batumi Hangar 2",
					x = -356147.5,
					y = 618389.25,
				},
				[11] = {
					name = "Batumi Hangar 3",
					x = -356193.8125,
					y = 618383.6875,
				},
				[12] = {
					name = "Batumi Hangar 4",
					x = -356258.34375,
					y = 618359.375,
				},
				[13] = {
					name = "Batumi Hangar 5",
					x = -355467.21875,
					y = 617597.6875,
				},
				[14] = {
					name = "Batumi Hangar 6",
					x = -355432.3125,
					y = 617586.625,
				},
				[15] = {
					name = "Batumi Hangar 7",
					x = -355603.28125,
					y = 617639.3125,
				},
				[16] = {
					name = "Batumi Command Center 1",
					x = -355499.375,
					y = 617559.6875,
				},
				[17] = {
					name = "Batumi Command Center 2",
					x = -355546.5,
					y = 617541.6875,
				},
			},
		},
		["Tbilissi Airbase"] = {
			task = "Strike",
			priority = 2,
			picture = {"Tbilisi Airbase.png"},
			attributes = {"Structure"},
			firepower = {
				min = 4,
				max = 8,
			},
			elements = {
				[1] = {
					name = "Tbilisi Control Tower",
					x = -314980.84375,
					y = 897071.3125,
				},
				[2] = {
					name = "Tbilisi Main Ammo Depot",
					x = -315172.15625,
					y = 896782.375,
				},
				[3] = {
					name = "Tbilisi Ammo Depot 1",
					x = -315008.84375,
					y = 897111.5625,
				},
				[4] = {
					name = "Tbilisi Ammo Depot 2",
					x = -314980.84375,
					y = 897071.3125,
				},
				[5] = {
					name = "Tbilisi Communication Center",
					x = -314733.0625,
					y = 896689.1875,
				},
				[6] = {
					name = "Tbilisi Fuel Depot",
					x = -315618.28125,
					y = 897633.25,
				},
				[7] = {
					name = "Tbilisi Fuel Tank 1",
					x = -315674.03125,
					y = 897667.5625,
				},
				[8] = {
					name = "Tbilisi Fuel Tank 2",
					x = -315667.09375,
					y = 897686.1875,
				},
				[9] = {
					name = "Tbilisi Fuel Tank 3",
					x = -315679.375,
					y = 897698,
				},
				[10] = {
					name = "Tbilisi Fuel Tank 4",
					x = -316143.1875,
					y = 898172.8125,
				},
				[11] = {
					name = "Tbilisi Fuel Tank 5",
					x = -316138.09375,
					y = 898194.25,
				},
				[12] = {
					name = "Tbilisi Fuel Tank 6",
					x = -316121.625,
					y = 898166.125,
				},
				[13] = {
					name = "Tbilisi Fuel Tank 7",
					x = -316174.375,
					y = 898189.3125,
				},
				[14] = {
					name = "Tbilisi Fuel Tank 8",
					x = -316166.21875,
					y = 898218.8125,
				},
				[15] = {
					name = "Tbilisi Power Supply",
					x = -314906.03125,
					y = 896979,
				},
				[16] = {
					name = "Tbilisi Hangar 1",
					x = -314246.3125,
					y = 895591,
				},
				[17] = {
					name = "Tbilisi Hangar 2",
					x = -314477.8125,
					y = 896415,
				},
				[18] = {
					name = "Tbilisi Hangar 3",
					x = -314608.84375,
					y = 896341.1875,
				},
				[19] = {
					name = "Tbilisi Hangar 4",
					x = -314785.6875,
					y = 896438.5,
				},
				[20] = {
					name = "Tbilisi Command Center",
					x = -314791.78125,
					y = 896795.625,
				},
			},
		},	
		--[[
		["Rail Bridge Kul tubani-EJ80"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions EJ80-EH99.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Rail Bridge Kul tubani-EJ80",
					x = -169535.234375,
					y = 468038.5625,
				},
			},
		},
		["Bridge Kul tubani-EJ80"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions EJ80-EH99.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Bridge Kul tubani-EJ80",
					x = -169308.046875,
					y = 468062.34375,
				},
			},
		},
		["Rail Bridge Tsalkoti-EJ80"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions EJ80-EH99.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Rail Bridge Tsalkoti-EJ80",
					x = -170051.65625,
					y = 472717.5625,
				},
			},
		},
		["Bridge Tsalkoti-EJ80"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions EJ80-EH99.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Bridge Tsalkoti-EJ80",
					x = -170576,
					y = 472735.90625,
				},
			},
		},		
		["Rail Bridge West Gantiadi-EJ80"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions EJ80-EH99.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Rail Bridge West Gantiadi-EJ80",
					x = -170473.796875,
					y = 473638.875,
				},
			},
		},
		["Bridge West Gantiadi-EJ80"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions EJ80-EH99.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Bridge West Gantiadi-EJ80",
					x = -170589.21875,
					y = 473621.0625,
				},
			},
		},
		["Rail Bridge East Gantiadi-EJ80"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions EJ80-EH99.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Rail Bridge East Gantiadi-EJ80",
					x = -170816.078125,
					y = 474374.84375,
				},
			},
		},
		["Bridge East Gantiadi-EJ80"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions EJ80-EH99.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Bridge East Gantiadi-EJ80",
					x = -170287.515625,
					y = 474441.984375,
				},
			},
		},
		["Rail Bridge Grebeshok-EH99"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions EJ80-EH99.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Rail Bridge Grebeshok-EH99",
					x = -175437.140625,
					y = 486008.4375,
				},
			},
		},
		["Bridge Grebeshok-EH99"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions EJ80-EH99.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Bridge Grebeshok-EH99",
					x = -175487.625,
					y = 485999.78125,
				},
			},
		},
		["Bridge Tagrskiy-FH08"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions FH08-FH18-FH28-FH27.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Bridge Tagrskiy-FH08",
					x = -189757.84765625,
					y = 493199.7578125,
				},
			},
		},
		["Rail Bridge Akvara-FH18"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions FH08-FH18-FH28-FH27.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Rail Bridge Akvara-FH18",
					x = -185827.1875,
					y = 500617.84375,
				},
			},
		},
		["Bridge Akvara-FH18"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions FH08-FH18-FH28-FH27.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Bridge Akvara-FH18",
					x = -185377.203125,
					y = 501025.8671875,
				},
			},
		},
		["Bridge Adzhkhahara-FH28"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions FH08-FH18-FH28-FH27.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Bridge Adzhkhahara-FH28",
					x = -186212.46875,
					y = 510276.9375,
				},
			},
		},
		["Rail Bridge Mugudzyrhva-FH28"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions FH08-FH18-FH28-FH27.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Rail Bridge Mugudzyrhva-FH28",
					x = -190870.578125,
					y = 513094.03125,
				},
			},
		},
		["Bridge Mugudzyrhva-FH28"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions FH08-FH18-FH28-FH27.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Bridge Mugudzyrhva-FH28",
					x = -190062.953125,
					y = 513422.03125,
				},
			},
		},
		["Rail Bridge Gudauta-FH27"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions FH08-FH18-FH28-FH27.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Rail Bridge Gudauta-FH27",
					x = -194627.296875,
					y = 515373.625,
				},
			},
		},
		["Bridge Gudauta-FH27"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions FH08-FH18-FH28-FH27.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Bridge Gudauta-FH27",
					x = -194555.703125,
					y = 515508.125,
				},
			},
		},
		["Bridge Primorskoe North-FH37"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridge Positions FH37-FH47-FH56-FH66.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Bridge Primorskoe North-FH37",
					x = -196679.6875,
					y = 526428.625,
				},
			},
		},
		["Bridge Primorskoe-FH37"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridge Positions FH37-FH47-FH56-FH66.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Bridge Primorskoe-FH37",
					x = -198076.4375,
					y = 526178.4375,
				},
			},
		},
		["Rail Bridge Primorskoe-FH37"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridge Positions FH37-FH47-FH56-FH66.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Rail Bridge Primorskoe-FH37",
					x = -198137.234375,
					y = 526192.0625,
				},
			},
		},	
		["Rail Bridge Nizh Armyanskoe Uschele-FH47"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridge Positions FH37-FH47-FH56-FH66.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Rail Bridge Nizh Armyanskoe Uschele-FH47",
					x = -198041.84375,
					y = 535039.0625,
				},
			},
		},
		["Bridge Nizh Armyanskoe Uschele-FH47"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridge Positions FH37-FH47-FH56-FH66.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Bridge Nizh Armyanskoe Uschele-FH47",
					x = -198238.734375,
					y = 535057.125,
				},
			},
		},
		["Rail Bridge Gumista West-FH56"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridge Positions FH37-FH47-FH56-FH66.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Rail Bridge Gumista West-FH56",
					x = -204594.21875,
					y = 548287,
				},
			},
		},
		["Rail Bridge Gumista East-FH56"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridge Positions FH37-FH47-FH56-FH66.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Rail Bridge Gumista East-FH56",
					x = -204775.890625,
					y = 548488.25,
				},
			},
		},
		["Bridge Gumista-FH56"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridge Positions FH37-FH47-FH56-FH66.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Bridge Gumista-FH56",
					x = -204543.046875,
					y = 548369.125,
				},
			},
		},
		["Bridge Uazabaa-FH66"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridge Positions FH37-FH47-FH56-FH66.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Bridge Uazabaa-FH66",
					x = -199885.375,
					y = 551708.625,
				},
			},
		},
		["Rail Bridge Kvemo-Merheuli North-FH65"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions FH65-FH75-FH74.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Rail Bridge Kvemo-Merheuli North-FH65",
					x = -208651.4375,
					y = 558293.5625,
				},
			},
		},
		["Bridge Kvemo-Merheuli North-FH65"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions FH65-FH75-FH74.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Bridge Kvemo-Merheuli North-FH65",
					x = -208624.78125,
					y = 558366.9375,
				},
			},
		},		
		["Rail Bridge Kvemo-Merheuli-FH65"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions FH65-FH75-FH74.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Rail Bridge Kvemo-Merheuli-FH65",
					x = -210831.09375,
					y = 559669.4375,
				},
			},
		},
		["Bridge Kvemo-Merheuli-FH75"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions FH65-FH75-FH74.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Bridge Kvemo-Merheuli-FH75",
					x = -210863.9375,
					y = 560317.8125,
				},
			},
		},
		["Rail Bridge Pshap-FH75"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions FH65-FH75-FH74.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Rail Bridge Pshap-FH75",
					x = -216667.140625,
					y = 563639.6875,
				},
			},
		},
		["Bridge Pshap West-FH75"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions FH65-FH75-FH74.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Bridge Pshap West-FH75",
					x = -216871.515625,
					y = 563349,
				},
			},
		},
		["Bridge Pshap East-FH75"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions FH65-FH75-FH74.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Bridge Pshap East-FH75",
					x = -216795.40625,
					y = 565105.875,
				},
			},
		},
		["Rail Bridge Sukhumi-Babushara North-FH74"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions FH65-FH75-FH74.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Rail Bridge Sukhumi-Babushara North-FH74",
					x = -218542.625,
					y = 565109.875,
				},
			},
		},
		["Bridge Sukhumi-Babushara North East-FH74"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions FH65-FH75-FH74.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Bridge Sukhumi-Babushara North East-FH74",
					x = -218727.34375,
					y = 566000.125,
				},
			},
		},
		["Bridge Sukhumi-Babushara North-FH74"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions FH65-FH75-FH74.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Bridge Sukhumi-Babushara North-FH74",
					x = -218590.5625,
					y = 563885.9375,
				},
			},
		},
		["Bridge Sukhumi-Babushara North West-FH74"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions FH65-FH75-FH74.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
			},
			elements = {
				[1] = {
					name = "Bridge Sukhumi-Babushara North West-FH74",
					x = -219430.109375,
					y = 562378,
				},
			},
		},	
		]]		
		["Bridge Anaklia-GG19"] = {
			task = "Strike",
			priority = 2,
			picture = {"Bridge positions GG19-GH10-GH20-GH21-GH31-GH42.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 4,
			},
			elements = {
				[1] = {
					name = "Bridge Anaklia North part-GG19",
					x = -267377.86865234,
					y = 606642.265625,
				},
				[2] = {
					name = "Bridge Anaklia South part-GG19",
					x = -267516.02490234,
					y = 606664.90625,
				},
			},
		},
		["Bridge Orsantia-GH10"] = {
			task = "Strike",
			priority = 2,
			picture = {"Bridge positions GG19-GH10-GH20-GH21-GH31-GH42.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 4,
			},
			elements = {
				[1] = {
					name = "Bridge Orsantia East part-GH10",
					x = -260460.296875,
					y = 612201.3203125,
				},
				[2] = {
					name = "Bridge Orsantia West part-GH10",
					x = -260463.796875,
					y = 612061.3671875,
				},
			},
		},		
		["Bridge Rike-GH31"] = {
			task = "Strike",
			priority = 4,
			picture = {"Bridge positions GG19-GH10-GH20-GH21-GH31-GH42.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 4,
			},
			elements = {
				[1] = {
					name = "Bridge Rike West part-GH31",
					x = -245409.5234375,
					y = 626855.359375,
				},
				[2] = {
					name = "Bridge Rike Center West part-GH31",
					x = -245465.4453125,
					y = 626983.703125,
				},
				[3] = {
					name = "Bridge Rike Center East part-GH31",
					x = -245521.3671875,
					y = 627112.046875,
				},
				[4] = {
					name = "Bridge Rike East part-GH31",
					x = -245577.2890625,
					y = 627240.390625,
				},
			},
		},	
		["Bridge Pahulani-GH42"] = {
			task = "Strike",
			priority = 2,
			picture = {"Bridge positions GG19-GH10-GH20-GH21-GH31-GH42.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 4,
			},
			elements = {
				[1] = {
					name = "Bridge Pahulani North part-GH42",
					x = -235275.5546875,
					y = 637292.2578125,
				},
				[2] = {
					name = "Bridge Pahulani Center part-GH42",
					x = -235374.34375,
					y = 637391.453125,
				},
				[3] = {
					name = "Bridge Pahulani South part-GH42",
					x = -235473.1328125,
					y = 637490.65625,
				},
			},
		},
		["Bridge Patara-Poti East-GG27"] = {
			task = "Strike",
			priority = 2,
			picture = {"Bridges Positions Patara-Poti-GG27.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 4,
			},
			elements = {
				[1] = {
					name = "Bridge Patara-Poti East North part-GG27",
					x = -290571.91992188,
					y = 619661.9921875,
				},
				[2] = {
					name = "Bridge Patara-Poti East South part-GH27",
					x = -290689.265625,
					y = 619585.6328125,
				},
			},
		},
		["Bridge Patara-Poti West-GG27"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges Positions Patara-Poti-GG27.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 4,
			},
			elements = {
				[1] = {
					name = "Bridge Patara-Poti West North part-GG27",
					x = -290212.75,
					y = 619188.875,
				},
				[2] = {
					name = "Bridge Patara-Poti West Center part-GG27",
					x = -290330,
					y = 619112.375,
				},
				[3] = {
					name = "Bridge Patara-Poti West South part-GH27",
					x = -290447.25,
					y = 619035.875,
				},
			},
		},			
		["Rail Bridge Patara-Poti-GG27"] = {
			task = "Strike",
			priority = 2,
			picture = {"Bridges Positions Patara-Poti-GG27.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 4,
			},
			elements = {
				[1] = {
					name = "Rail Bridge Patara-Poti North part-GG27",
					x = -290165.734375,
					y = 619140.03125,
				},
				[2] = {
					name = "Rail Bridge Patara-Poti Center part-GG27",
					x = -290248.08398438,
					y = 619083.296875,
				},
				[3] = {
					name = "Rail Bridge Patara-Poti South part-GH27",
					x = -290330.43359375,
					y = 619026.5625,
				},
			},
		},					
	},
}