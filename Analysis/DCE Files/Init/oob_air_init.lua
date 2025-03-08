--Order of Battle - Aircraft/Helicopter
--organized in units (squadrons/regiments) containing a number of aircraft
--Campaign Version-V20.00

-- Miguel Fichier Revision M42
------------------------------------------------------------------------------------------------------- 

-- miguel21 modification M42 : liveryModex ajoute des Skin lié au numero de l avion
-- Miguel21 modification M33.e 	Custom Briefing (e: divers)
-- ATO_G_adjustment02 TASK Coef


--[[ Unit Entry Example ----------------------------------------------------------------------------

[1] = {
	inactive = true,								--true if unit is not active
	player = true,									--true for player unit
	name = "527 TFS",								--unit name
	type = "F-5E-3",								--aircraft type
	helicopter = true,								--true for helicopter units
	country = "USA",								--unit country
	livery = {"USAF Euro Camo"},					--unit livery
	liveryModex = {									--unit livery Modex  (optional)
		[100] = "VF-101 Dark",
		[110] = "VF-101 Grim Reapers Low Vis",
		},
	base = "Groom Lake AFB",						--unit base
	skill = "Random",								--unit skill
	tasks = {										--list of eligible unit tasks. Note: task names do not necessary match DCS tasks)
		["AWACS"] = true,							
		["Anti-ship Strike"] = true,
		["CAP"] = true,
		["Fighter Sweep"] = true,	
		["Intercept"] = true,
		["Reconnaissance"] = true,
		["Refueling"] = true,
		["Strike"] = true,							--Generic air-ground task (replaces "Ground Attack", "CAS" and "Pinpoint Strike")
		["Transport"] = true,
		["Escort"] = true,							--Support task: Fighter escort for package
		["SEAD"] = true,							--Support task: SEAD escort for package
		["Escort Jammer"] = true,					--Support task: Single airraft in center of package for defensive jamming
		["Flare Illumination"] = true,				--Support task: Illuminate target with flares for package
		["Laser Illumination"] = true,				--Support task: Lase target for package
		["Stand-Off Jammer"] = true,				--Not implemeted yet: On-station jamming
		["Chaff Escort"] = true,					--Not implemented yet: Lay chaff corrdior ahead of package
		["A-FAC"] = true,							--Not implemented yet: Airborne forward air controller
	},
	tasksCoef = {									--unit tasks coef (optional)
		["Strike"] = 1,								-- coef normal : = 1
		["SEAD"] = 1,
		["Laser Illumination"] = 1,
		["Intercept"] = 1,
		["CAP"] = 0.2,
		["Escort"] = 3,
		["Fighter Sweep"] = 1,	
	},
	number = 12,									--number of airframes
	refuelable = false,								--aucun affichage de TACAN ou autre Frequence des TANKER dans le briefing
},

]]-----------------------------------------------------------------------------------------------------

oob_air = {
	["blue"] = {											--side 1
		[1] = {
			name = "VFA-106",								--unit name
			player = false,									--player unit
			type = "FA-18C_hornet",							--aircraft type
			country = "USA",								--unit country
			livery = "vfa-106",								--unit livery	livery = "VFA-131",
			liveryModex = {									--unit livery Modex  (optional)
				[200] = "vfa-106 high visibility",
				},
			sidenumber = {200, 215},														 
			base = "CVN-71 Theodore Roosevelt",				--unit base
			skill = "High",									--unit skill
			tasks = {										--unit tasks
				["SEAD"] = true,
				["Intercept"] = false,
				["CAP"] = true,
				["Fighter Sweep"] = false,
				["Escort"] = true,
				["Strike"] = true,
				["Anti-ship Strike"] = true,
			},
			tasksCoef = {									--unit tasks coef (optional)
				["Strike"] = 1.5,								-- coef normal : = 1
				["SEAD"] = 2,
				["Laser Illumination"] = 1,
				["Intercept"] = 1,
				["CAP"] = 0.2,
				["Escort"] = 0.5,
				["Fighter Sweep"] = 0.2,
				["Anti-ship Strike"] = 2,
			},
			number = 16,
		},
		[2] = {
			name = "R/VFA-106",								--unit name
			inactive = true,
			type = "F/A-18C",								--aircraft type
			country = "USA",								--unit country
			base = "Reserves",								--unit base
			tasks = {},										--unit tasks
			number = 28,
		},
		[3] = {
			name = "VF-101",							--unit name
			player = true,									--player unit
			type = "F-14A-135-GR",								--aircraft type
			country = "USA",								--unit country
			livery = {"vf-101 grim reapers low vis", "vf-101 dark"},				--unit livery
			liveryModex = {									--unit livery Modex  (optional)
				[100] = "vf-101 red",
				[105] = "vf-101 grim reapers low vis",
				[111] = "vf-101 dark",
				},
			sidenumber = {100, 115},														 
			base = "CVN-71 Theodore Roosevelt",							--unit base
			skill = "High",								--unit skill
			tasks = {										--unit tasks
				["Intercept"] = true,
				["CAP"] = true,
				["Escort"] = true,
				["Fighter Sweep"] = false,
				["Strike"] = false,
			},
			tasksCoef = {									--unit tasks coef (optional)
				["Strike"] = 1,								-- coef normal : = 1
				["SEAD"] = 1,
				["Laser Illumination"] = 1,
				["Intercept"] = 1,
				["CAP"] = 1,
				["Escort"] = 1,
				["Fighter Sweep"] = 1,	
			},
			number = 16,
		},
		[4] = {
			name = "R/VF-101",								--unit name
			inactive = true,
			type = "F-14B",								--aircraft type
			base = "Reserves",
			skill = "High",								--unit skill
			tasks = {},										--unit tasks
			number = 24,
		},
		[5] = {
			name = "VAW-125",								--unit name
			type = "E-2C",									--aircraft type
			country = "USA",								--unit country
			livery = "",									--unit livery
			sidenumber = {600, 609},						--unit range of sidenumbers (optional)
			base = "CVN-71 Theodore Roosevelt",							--unit base
			skill = "High",								--unit skill
			tasks = {										--unit tasks
				["AWACS"] = true,
			},
			number = 8,
		},
		[6] = {
			name = "R/VAW-125",								--unit name
			inactive = true,
			type = "E-2C",									--aircraft type
			country = "USA",								--unit country
			base = "Reserves",							--unit base
			skill = "High",								--unit skill
			tasks = {},									--unit tasks
			number = 1,
		},
		[7] = {
			name = "174 ARW",								--unit name
			type = "S-3B Tanker",								--aircraft type
			country = "USA",								--unit country
			livery = "",									--unit livery
			sidenumber = {400, 429},						--unit range of sidenumbers (optional)
			base = "CVN-71 Theodore Roosevelt",							--unit base
			skill = "High",								--unit skill
			tasks = {										--unit tasks
				["Refueling"] = true,
			},
			number = 12,
		},
		[8] = {
			name = "R/174 ARW",								--unit name
			inactive = true,
			type = "S-3B Tanker",									--aircraft type
			country = "USA",								--unit country
			base = "Reserves",							--unit base
			skill = "High",								--unit skill
			tasks = {},									--unit tasks
			number = 10,
		},
		[9] = {
			name = "VMFA-312",								--unit name name = "VFA-192",
			player = false,									--player unit
			type = "FA-18C_hornet",							--aircraft type
			country = "USA",								--unit country
			livery = "vmfa-312",							--unit livery
			liveryModex = {									--unit livery Modex  (optional)
				[200] = "vmfa-312 high visibility",
				},
			sidenumber = {200, 215},														 
			base = "CVN-74 John C. Stennis",				--unit base
			skill = "High",									--unit skill
			tasks = {										--unit tasks
				["SEAD"] = true,
				["Intercept"] = true,
				["CAP"] = false,
				["Fighter Sweep"] = false,
				["Escort"] = false,
				["Strike"] = true,
				["Anti-ship Strike"] = false,
			},
			tasksCoef = {									--unit tasks coef (optional)
				["Strike"] = 1.5,								-- coef normal : = 1
				["SEAD"] = 2,
				["Laser Illumination"] = 1,
				["Intercept"] = 1,
				["CAP"] = 0.2,
				["Escort"] = 0.5,
				["Fighter Sweep"] = 0.2,
				["Anti-ship Strike"] = 2,
			},
			number = 16,
		},
		[10] = {
			name = "R/VMFA-312",								--unit name
			inactive = true,
			type = "FA-18C_hornet",							--aircraft type
			country = "USA",								--unit country
			base = "Reserves",								--unit base
			tasks = {},										--unit tasks
			number = 28,
		},
		-- [11] = {
			-- inactive = false,								--true if unit is not active		
			-- name = "96 BW",								--unit name
			-- type = "B-1B",								--aircraft type
			-- country = "USA",								--unit country
			-- livery = "Standard USAF",						--unit livery
			-- base = "Dyess AFB",							--unit base
			-- skill = "High",								--unit skill
			-- tasks = {										--unit tasks
				-- ["Strike"] = true,
			-- },
			-- number = 6,
		-- },
		-- [11] = {
			-- inactive = false,								--true if unit is not active
			-- name = "69 BS",									--unit name
			-- type = "B-52H",									--aircraft type
			-- country = "USA",								--unit country
			-- livery = "usaf standard",						--unit livery
			-- sidenumber = {020, 050},						--unit range of sidenumbers (optional)
			-- base = "Dyess AFB",								--unit base
			-- skill = "High",									--unit skill
			-- tasks = {										--unit tasks
				-- ["Strike"] = true,
			-- },
			-- number = 12,
		-- },
		[11] = {
			name = "175 ARW",								--unit name
			type = "S-3B Tanker",								--aircraft type
			country = "USA",								--unit country
			livery = "",									--unit livery
			sidenumber = {430, 450},						--unit range of sidenumbers (optional)
			base = "CVN-71 Theodore Roosevelt",							--unit base base = "CVN-71 Theodore Roosevelt",	
			skill = "High",								--unit skill
			tasks = {										--unit tasks
				["Refueling"] = true,
			},
			number = 12,
		},
		[12] = {
			name = "VF-143",								--unit name	name = "VF-32",
			player = false,									--player unit
			type = "F-14A-135-GR",									--aircraft type
			country = "USA",								--unit country
			livery = {"vf-143 pukin dogs low vis", "vf-143 pukin dogs low vis (1995)"},				--unit livery
			liveryModex = {									--unit livery Modex  (optional)
				[100] = "vf-143 pukin dogs cag",
				[110] = "vf-143 pukin dogs low vis (1995)",
				[114] = "vf-143 pukin dogs low vis",
				},
			sidenumber = {100, 115},						--unit range of sidenumbers (optional)
			base = "CVN-74 John C. Stennis",				--unit base
			skill = "High",									--unit skill
			tasks = {										--unit tasks
				["Intercept"] = true,
				["CAP"] = true,
				["Escort"] = true,
				["Fighter Sweep"] = false,
				["Strike"] = false,				
			},
			tasksCoef = {									--unit tasks coef (optional)
				["Strike"] = 1,								-- coef normal : = 1
				["SEAD"] = 1,
				["Laser Illumination"] = 1,
				["Intercept"] = 1,
				["CAP"] = 1,
				["Escort"] = 1,
				["Fighter Sweep"] = 1,	
			},
			number = 16,
		},
		[13] = {
			name = "R/VF-143",								--unit name
			inactive = true,
			type = "F-14B",								--aircraft type
			base = "Reserves",
			skill = "High",								--unit skill
			tasks = {},									--unit tasks
			number = 30,
		},
		[14] = {
			name = "VMA 311",								--unit name
			inactive = true,
			player = false,									--player unit
			type = "AV8BNA",								--aircraft type
			country = "USA",								--unit country
			livery = "vma-311",								--unit livery
			liveryModex = {									--unit livery Modex  (optional)
				[100] = "vma-311d",
				},
			sidenumber = {100, 103},
			base = "LHA_Tarawa",							--unit base
			skill = "High",									--unit skill
			tasks = {										--unit tasks
				["Strike"] = true,
				["SEAD"] = false,
				["Anti-ship Strike"] = true,
			},
			tasksCoef = {									--unit tasks coef (optional)
				["Strike"] = 3,								-- coef normal : = 1
				["SEAD"] = 1,
				["Laser Illumination"] = 1,
				["Intercept"] = 1,
				["CAP"] = 0.2,
				["Escort"] = 0.5,
				["Fighter Sweep"] = 0.2,
				["Anti-ship Strike"] = 2,
			},
			number = 4,
		},
		[15] = {
			name = "VMA 331",								--unit name
			inactive = true,
			type = "AV8BNA",								--aircraft type
			base = "Reserves",								--unit base
			tasks = {										--unit tasks
			},
			number = 30,
		},
	},
	["red"] = {												--side 2
		[1] = {
			name = "19.IAP",							--unit name
			type = "MiG-21Bis",								--aircraft type
			country = "Russia",								--unit country
			sidenumber = {010, 045},						--unit range of sidenumbers (optional)
			livery = {"VVS - AMT-11 Grey"},									--unit livery
			base = "Batumi",							--unit base
			skill = "Random",								--unit skill
			tasks = {										--unit tasks
				["Intercept"] = true,
				["CAP"] = true,
				["Escort"] = true,
				["Fighter Sweep"] = true,				
			},
			number = 10,
		},
		[2] = {
			name = "R/19.IAP",								--unit name
			inactive = true,
			type = "MiG-21Bis",								--aircraft type
			base = "Reserves",
			skill = "Random",								--unit skill
			tasks = {},									--unit tasks
			number = 24,
		},
		[3] = {
			name = "11.RAP",								--unit name
			type = "Su-24MR",								--aircraft type
			country = "Russia",								--unit country
			sidenumber = {400, 410},						--unit range of sidenumbers (optional)
			livery = "af standard",							--unit livery
			base = "Maykop-Khanskaya",							--unit base
			skill = "High",								--unit skill
			tasks = {										--unit tasks
				["Reconnaissance"] = true,
			},
			number = 6,
		},
		[4] = {
			name = "31.IAP",							--unit name
			type = "MiG-23MLD",								--aircraft type
			country = "Russia",							--unit country
			sidenumber = {050, 095},						--unit range of sidenumbers (optional)
			livery = "af standard",						--unit livery
			base = "Sukhumi",							--unit base
			skill = "Random",								--unit skill
			tasks = {										--unit tasks
				["Intercept"] = true,
				["CAP"] = true,
				["Escort"] = true,
				["Fighter Sweep"] = true,				
			},
			number = 12,
		},
		[5] = {
			name = "R/31.IAP",								--unit name
			inactive = true,
			type = "MiG-23MLD",								--aircraft type
			base = "Reserves",
			skill = "Random",								--unit skill
			tasks = {},									--unit tasks
			number = 24,
		},
		[6] = {
			name = "28.IAP",							--unit name
			type = "MiG-21Bis",								--aircraft type
			country = "Russia",							--unit country
			sidenumber = {100, 145},						--unit range of sidenumbers (optional)
			livery = "VVS - AMT-11 Grey",						--unit livery
			base = "Gudauta",							--unit base
			skill = "Random",								--unit skill
			tasks = {										--unit tasks
				["Intercept"] = true,
				["CAP"] = true,
				["Escort"] = true,
				["Fighter Sweep"] = true,				
			},
			number = 12,
		},
		[7] = {
			name = "R/28.IAP",								--unit name
			inactive = true,
			type = "MiG-21Bis",								--aircraft type
			base = "Reserves",
			skill = "Random",								--unit skill
			tasks = {},									--unit tasks
			number = 24,
		},
		[8] = {
			name = "368.ShAP",								--unit name
			type = "Su-17M4",								--aircraft type
			country = "Russia",								--unit country
			sidenumber = {300, 345},						--unit range of sidenumbers (optional)
			livery = "af standard (worn-out)",						--unit livery
			base = "Kobuleti",						--unit base
			skill = "Random",
			tasks = {
				["Strike"] = false,
				["SEAD"] = false,
				["Anti-ship Strike"] = true,
			},
			number = 24,
		},
		[9] = {
			name = "R/368.ShAP",								--unit name
			inactive = true,
			type = "Su-17M4",								--aircraft type
			base = "Reserves",
			skill = "Random",								--unit skill
			tasks = {},									--unit tasks
			number = 24,
		},
		[10] = {
			name = "3.IAP",								--unit name
			type = "MiG-23MLD",								--aircraft type
			country = "Russia",						--unit country
			sidenumber = {150, 195},						--unit range of sidenumbers (optional)
			livery = "af standard",			--unit livery
			base = "Kutaisi",							--unit base
			skill = "Random",								--unit skill
			tasks = {										--unit tasks
				["Intercept"] = true,
				["CAP"] = true,
				["Escort"] = true,
				["Fighter Sweep"] = true,				
			},
			number = 12,
		},
		[11] = {
			name = "R/3.IAP",								--unit name
			inactive = true,
			type = "MiG-23MLD",								--aircraft type
			base = "Reserves",
			skill = "Random",								--unit skill
			tasks = {},									--unit tasks
			number = 24,
		},
		[12] = {
			name = "559.BAP",								--unit name
			type = "Su-24M",								--aircraft type
			country = "Russia",								--unit country
			sidenumber = {350, 385},						--unit range of sidenumbers (optional)
			livery = "af standard",								--unit livery
			base = "Senaki-Kolkhi",						--unit base
			skill = "high",								--unit skill
			tasks = {
				["Strike"] = false,
				["SEAD"] = false,
				["Laser Illumination"] = false,
				["Anti-ship Strike"] = true,				
			},
			number = 12,
		},
		[13] = {
			name = "R/559.BAP",								--unit name
			inactive = true,
			type = "Su-24M",								--aircraft type
			base = "Reserves",
			skill = "high",								--unit skill
			tasks = {},									--unit tasks
			number = 18,
		},
		-- [14] = {
			-- name = "535-1.OSAP",								--unit name
			-- type = "An-26B",								--aircraft type
			-- country = "Russia",								--unit country
			-- livery = {"Aeroflot", "RF Air Force"},			--unit livery
			-- base = "Sochi-Adler",							--unit base
			-- skill = "Random",								--unit skill
			-- tasks = {										--unit tasks
				-- ["Transport"] = true,
			-- },
			-- number = 1,
		-- },
		-- [15] = {
			-- name = "535-5.OSAP",								--unit name
			-- type = "Mi-24V",								--aircraft type
			-- helicopter = true,								--true for helicopter units
			-- country = "Russia",								--unit country
			-- livery = {""},			--unit livery
			-- base = "Gudauta",								--unit base
			-- skill = "Random",								--unit skill
			-- tasks = {										--unit tasks
				-- ["Transport"] = true,
			-- },
			-- number = 3,
		-- },
		[14] = {
			name = "174.IAP-PVO",								--unit name
			type = "MiG-25PD",								--aircraft type
			country = "Russia",								--unit country
			sidenumber = {200, 245},						--unit range of sidenumbers (optional)
			livery = {"af standard"},			--unit livery
			base = "Mozdok",								--unit base
			skill = "high",								--unit skill
			tasks = {										--unit tasks
				["Intercept"] = true,
				["CAP"] = true,
				["Escort"] = false,
				["Fighter Sweep"] = true,			
			},
			number = 6,
		},
		[15] = {
			name = "R/174.IAP-PVO",								--unit name
			inactive = true,
			type = "MiG-25PD",								--aircraft type
			base = "Reserves",
			skill = "high",								--unit skill
			tasks = {},									--unit tasks
			number = 24,
		},		
		[16] = {
			name = "52.TBAP",								--unit name
			type = "Tu-22M3",								--aircraft type
			country = "Russia",								--unit country
			sidenumber = {600, 645},						--unit range of sidenumbers (optional)
			livery = {""},			--unit livery
			base = "Mineralnye-Vody",								--unit base
			skill = "high",								--unit skill
			tasks = {										--unit tasks
				["Strike"] = false,
				["Anti-ship Strike"] = true,				
			},
			number = 6,
		},
		[17] = {
			name = "R/52.TBAP",								--unit name
			inactive = true,
			type = "Tu-22M3",								--aircraft type
			base = "Reserves",
			skill = "high",								--unit skill
			tasks = {},									--unit tasks
			number = 24,
		},
		[18] = {
			name = "959.BAP",								--unit name
			type = "Su-24M",								--aircraft type
			country = "Russia",								--unit country
			sidenumber = {420, 445},						--unit range of sidenumbers (optional)
			livery = "af standard",								--unit livery
			base = "Kutaisi",						--unit base
			skill = "high",								--unit skill
			tasks = {
				["Strike"] = false,
				["SEAD"] = false,
				["Anti-ship Strike"] = true,				
				
			},
			number = 12,
		},
		[19] = {
			name = "R/959.BAP",								--unit name
			inactive = true,
			type = "Su-24M",								--aircraft type
			base = "Reserves",
			skill = "high",								--unit skill
			tasks = {},									--unit tasks
			number = 24,
		},
		[20] = {
			name = "79.TBAP",								--unit name
			type = "Tu-142",								--aircraft type
			country = "Russia",								--unit country
			sidenumber = {600, 645},						--unit range of sidenumbers (optional)
			livery = {""},			--unit livery
			base = "Tbilissi-Lochini",								--unit base
			skill = "high",								--unit skill
			tasks = {										--unit tasks
				["Strike"] = false,
				["Anti-ship Strike"] = true,				
			},
			number = 6,
		},
		[21] = {
			name = "R/79.TBAP",								--unit name
			inactive = true,
			type = "Tu-142",								--aircraft type
			base = "Reserves",
			skill = "high",								--unit skill
			tasks = {},									--unit tasks
			number = 24,
		},
		-- [24] = {
			-- name = "535-3.OSAP",								--unit name
			-- type = "Mi-8MT",								--aircraft type
			-- helicopter = true,								--true for helicopter units
			-- country = "Russia",								--unit country
			-- livery = {""},			--unit livery
			-- base = "Senaki-Kolkhi",								--unit base
			-- skill = "Random",								--unit skill
			-- tasks = {										--unit tasks
				-- ["Transport"] = true,
			-- },
			-- number = 2,
		-- },
		-- [25] = {
			-- name = "535-4.OSAP",								--unit name
			-- type = "Mi-26",								--aircraft type
			-- helicopter = true,								--true for helicopter units
			-- country = "Russia",								--unit country
			-- livery = {""},			--unit livery
			-- base = "Sukhumi",								--unit base
			-- skill = "Random",								--unit skill
			-- tasks = {										--unit tasks
				-- ["Transport"] = true,
			-- },
			-- number = 1,
		-- },	
		-- [26] = {
			-- name = "535-2.OSAP",								--unit name
			-- type = "An-26B",								--aircraft type
			-- country = "Russia",								--unit country
			-- livery = {"Aeroflot", "RF Air Force"},			--unit livery
			-- base = "Batumi",								--unit base
			-- skill = "Random",								--unit skill
			-- tasks = {										--unit tasks
				-- ["Transport"] = true,
			-- },
			-- number = 1,
		-- },
	},
}

--List of aliases to replace type names in briefing/debriefing
TypeAlias = {

}