targetlist = {
	["blue"] = {
		["CVN-71 Theodore Roosevelt Interception"] = {
			task = "Intercept",
			priority = 10,
			attributes = {},
			firepower = {
				min = 2,
				max = 4,
			},
			base = "CVN-71 Theodore Roosevelt",
			radius = 150000,
		},
		["CVN-71 Theodore Roosevelt Interception 2"] = {
			task = "Intercept",
			priority = 10,
			attributes = {},
			firepower = {
				min = 2,
				max = 4,
			},
			base = "CVN-71 Theodore Roosevelt",
			radius = 130000,
		},
		["CVN-74 John C. Stennis Interception"] = {
			task = "Intercept",
			priority = 10,
			attributes = {},
			firepower = {
				min = 2,
				max = 4,
			},
			base = "CVN-74 John C. Stennis",
			radius = 160000,
		},
		["CVN-74 John C. Stennis Interception 2"] = {
			task = "Intercept",
			priority = 10,
			attributes = {},
			firepower = {
				min = 2,
				max = 4,
			},
			base = "CVN-74 John C. Stennis",
			radius = 140000,
		},
		["Battle Group CAP"] = {
			task = "CAP",
			priority = 20,
			attributes = {},
			firepower = {
				min = 2,
				max = 2,
			},
			slaved = {"CVN-71 Theodore Roosevelt", 85, 70600},
			radius = 111000,
			text = "",
		},
		["Battle Group CAP 2"] = {
			task = "CAP",
			priority = 10,
			attributes = {},
			firepower = {
				min = 2,
				max = 2,
			},
			slaved = {"CVN-71 Theodore Roosevelt", 45, 70600},
			radius = 111000,
			text = "",
		},		
		-- ["AWACS"] = {
			-- task = "AWACS",
			-- priority = 1,
			-- attributes = {},
			-- firepower = {
				-- min = 1,
				-- max = 1,
			-- },
			-- refpoint = "AWACS",
			-- radius = 15000,
			-- text = "",
		-- },		
		["Battle Group AEW"] = {
			task = "AWACS",
			priority = 10,
			attributes = {},
			firepower = {
				min = 1,
				max = 1,
			},
			slaved = {"CVN-71 Theodore Roosevelt",090, 60000},
			text = "",
		},
		["Mission Support Tanker"] = {
			task = "Refueling",
			priority = 2,
			attributes = {"medium"},
			firepower = {
				min = 1,
				max = 1,
			},
			slaved = {"CVN-71 Theodore Roosevelt", 085, 40000},
			text = "",
		},
		["Recovery Tanker"] = {
			task = "Refueling",
			priority = 1,
			attributes = {"low"},
			firepower = {
				min = 1,
				max = 1,
			},
			slaved = {"CVN-71 Theodore Roosevelt", 085, 20000},
			text = "",
		},
		["EWR 1 501"] = {
			task = "Strike",
			priority = 10,
			attributes = {"soft"},
			firepower = {
				min = 2,
				max = 2,
			},
			class = "vehicle",
			name = "EWR 1 501",
		},
		["EWR 2 502"] = {
			task = "Strike",
			priority = 10,
			attributes = {"soft"},
			firepower = {
				min = 2,
				max = 2,
			},
			class = "vehicle",
			name = "EWR 2 502",
		},
		["EWR 3 503"] = {
			task = "Strike",
			priority = 10,
			attributes = {"soft"},
			firepower = {
				min = 2,
				max = 2,
			},
			class = "vehicle",
			name = "EWR 3 503",
		},
		-- ["SA-6 Gainful Site Sochi"] = {
			-- task = "Strike",
			-- priority = 6,
			-- attributes = {"SAM"},
			-- firepower = {
				-- min = 20,
				-- max = 80,
			-- },
			-- class = "vehicle",
			-- name = "Sa-6 Sochi",
		-- },
		["SA-2 Guideline Site N1"] = {
			task = "Strike",
			priority = 7,
			attributes = {"SAM"},
			firepower = {
				min = 4,
				max = 4,
			},
			class = "vehicle",
			name = "Sa-2 N1",
		},
		["SA-3 Goa Site Gudauta"] = {
			task = "Strike",
			priority = 4,
			attributes = {"SAM"},
			firepower = {
				min = 4,
				max = 4,
			},
			class = "vehicle",
			name = "Sa-3 Gudauta",
		},
		["SA-2 Guideline Site N2"] = {
			task = "Strike",
			priority = 7,
			attributes = {"SAM"},
			firepower = {
				min = 4,
				max = 4,
			},
			class = "vehicle",
			name = "Sa-2 N2",
		},
		["SA-2 Guideline Site C1"] = {
			task = "Strike",
			priority = 7,
			attributes = {"SAM"},
			firepower = {
				min = 4,
				max = 4,
			},
			class = "vehicle",
			name = "Sa-2 C1",
		},		
		["SA-6 Gainful Site Senaki"] = {
			task = "Strike",
			priority = 3,
			attributes = {"SAM"},
			firepower = {
				min = 4,
				max = 4,
			},
			class = "vehicle",
			name = "Sa-6 Senaki",
		},
		["SA-3 Goa Site Kutaisi"] = {
			task = "Strike",
			priority = 4,
			attributes = {"SAM"},
			firepower = {
				min = 4,
				max = 4,
			},
			class = "vehicle",
			name = "Sa-3 Kutaisi",
		},
		["SA-6 Gainful Site Kobuleti"] = {
			task = "Strike",
			priority = 3,
			attributes = {"SAM"},
			firepower = {
				min = 4,
				max = 4,
			},
			class = "vehicle",
			name = "Sa-6 Kobuleti",
		},
		["SA-2 Guideline Site S1"] = {
			task = "Strike",
			priority = 7,
			attributes = {"SAM"},
			firepower = {
				min = 4,
				max = 4,
			},
			class = "vehicle",
			name = "Sa-2 S1",
		},
		["SA-3 Goa Site Batumi"] = {
			task = "Strike",
			priority = 4,
			attributes = {"SAM"},
			firepower = {
				min = 4,
				max = 4,
			},
			class = "vehicle",
			name = "Sa-3 Batumi",
		},
		["SA-2 Guideline Site Tbilisi"] = {
			task = "Strike",
			priority = 1,
			attributes = {"SAM"},
			firepower = {
				min = 4,
				max = 4,
			},
			class = "vehicle",
			name = "Sa-2 Tbilisi",
		},
		["Cargo convoy 1"] = {
			task = "Anti-ship Strike",
			priority = 15,
			attributes = {"ship"},
			firepower = {
				min = 4,
				max = 8,
			},
			class = "ship",
			name = "Cargo convoy 1",
		},
		["Cargo convoy 2"] = {
			task = "Anti-ship Strike",
			priority = 15,
			attributes = {"ship"},
			firepower = {
				min = 4,
				max = 8,
			},
			class = "ship",
			name = "Cargo convoy 2",
		},			
		["Leselidze Train Station - EJ80"] = {
			task = "Strike",
			priority = 1,
			picture = {"Leselidze Train Station.png"},			
			attributes = {"Structure"},
			firepower = {
				min = 4,
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
				min = 4,
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
				min = 4,
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
			priority = 3,
			picture = {"Gudauta Train Station.png"},			
			attributes = {"Structure"},
			firepower = {
				min = 4,
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
				min = 4,
				max = 4,
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
				min = 4,
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
			priority = 2,
			picture = {"Sukhumi Train Station.png"},			
			attributes = {"Structure"},
			firepower = {
				min = 4,
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
				min = 4,
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
			priority = 3,
			picture = {"Sukhumi-Babushara Train Station.png"},			
			attributes = {"Structure"},
			firepower = {
				min = 4,
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
			priority = 3,
			picture = {"Senaki-Kolkhi Train Station.png"},			
			attributes = {"Structure"},
			firepower = {
				min = 4,
				max = 8,
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
			priority = 3,
			picture = {" Kobuleti Train Station.png"},			
			attributes = {"Structure"},
			firepower = {
				min = 4,
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
		["Bridge Koki-GH20"] = {
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
		["Rail Bridge Tagiloni-GH21"] = {
			task = "Strike",
			priority = 5,
			picture = {"Bridge positions GG19-GH10-GH20-GH21-GH31-GH42.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
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
				max = 2,
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
		["Rail Bridge Dapnari-KM76"] = {
			task = "Strike",
			priority = 2,
			picture = {"Bridges positions Dapnari-KM76.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 4,
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
		["Bridge Dapnari-KM76"] = {
			task = "Strike",
			priority = 1,
			picture = {"Bridges positions Dapnari-KM76.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
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
		["Bridge Vartsihe-LM16"] = {
			task = "Strike",
			priority = 3,
			picture = {"Bridges positions LM16-LM17-LM18.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 4,
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
		["Bridge Geguti-LM17"] = {
			task = "Strike",
			priority = 2,
			picture = {"Bridges positions LM16-LM17-LM18.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 4,
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
		["Bridge Kutaisi-LM18"] = {
			task = "Strike",
			priority = 2,
			picture = {"Bridges positions LM16-LM17-LM18.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 2,
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
		["Rail Bridge North Geguti-LM17"] = {
			task = "Strike",
			priority = 2,
			picture = {"Bridges positions LM16-LM17-LM18.png"},
			attributes = {"Bridge"},
			firepower = {
				min = 2,
				max = 4,
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
		["Batumi Marshalling Yard"] = {
			task = "Strike",
			priority = 5,
			picture = {"Batumi Marshalling Yard.png", "Batumi Harbor.png"},			
			attributes = {"Structure"},
			firepower = {
				min = 4,
				max = 8,
			},
			elements = {
				[1] = {
					name = "Batumi Marshalling Yard Fuel Tank 1",
					x = -351450.03564453,
					y = 621410.86572266,
				},
				[2] = {
					name = "Batumi Marshalling Yard Fuel Tank 2",
					x = -351332.61621094,
					y = 621781.40722656,
				},
				[3] = {
					name = "Batumi Marshalling Yard Fuel Tank 3",
					x = -351709.57226563,
					y = 621801.42138672,
				},
				[4] = {
					name = "Batumi Marshalling Yard Fuel Tank 4",
					x = -351729.64648438,
					y = 621810.38720703,
				},
				[5] = {
					name = "Batumi Marshalling Yard Fuel Tank 5",
					x = -351829.71582031,
					y = 621773.09863281,
				},
				[6] = {
					name = "Batumi Marshalling Yard Fuel Tank 6",
					x = -351877.93359375,
					y = 621716.05712891,
				},
				[7] = {
					name = "Batumi Marshalling Yard Fuel Tank 7",
					x = -351666.63037109,
					y = 621367.16894531,
				},
				[8] = {
					name = "Batumi Marshalling Yard Hangar 1",
					x = -351524.5,
					y = 621702.8125,
				},
				[9] = {
					name = "Batumi Marshalling Yard Hangar 2",
					x = -351478.71679688,
					y = 621899.84375,
				},
				[10] = {
					name = "Batumi Marshalling Yard Hangar 3",
					x = -351259.67041016,
					y = 622073.90039063,
				},
				[11] = {
					name = "Batumi Marshalling Yard Hangar 4",
					x = -351562.22998047,
					y = 621498.87597656,
				},
				[12] = {
					name = "Batumi Marshalling Yard Hangar 5",
					x = -351260.18359375,
					y = 622331.16015625,
				},
				[13] = {
					name = "Batumi Marshalling Yard Hangar 6",
					x = -351246.75585938,
					y = 622496.31054688,
				},
				[14] = {
					name = "Batumi Marshalling Yard Hangar 7",
					x = -351330.26904297,
					y = 622095.34375,
				},
				[15] = {
					name = "Batumi Marshalling Yard Hangar 8",
					x = -351340.39306641,
					y = 622382.44628906,
				},
				[16] = {
					name = "Batumi Marshalling Yard Hangar 9",
					x = -351572.35400391,
					y = 621785.97851563,
				},
				[17] = {
					name = "Batumi Marshalling Yard Hangar 10",
					x = -351675.84179688,
					y = 621301.3828125,
				},
				[18] = {
					name = "Batumi Marshalling Yard Hangar 11",
					x = -351708.91308594,
					y = 621436.11914063,
				},
				[19] = {
					name = "Batumi Marshalling Yard Hangar 12",
					x = -351723.6015625,
					y = 621399.765625,
				},
				[20] = {
					name = "Batumi Marshalling Yard Hangar 13",
					x = -351788.48046875,
					y = 621439.44628906,
				},
				[21] = {
					name = "Batumi Marshalling Yard Hangar 14",
					x = -351773.80419922,
					y = 621475.77050781,
				},				
			},
		},
		["Batumi Harbor"] = {
			task = "Strike",
			priority = 5,
			picture = {"Batumi Marshalling Yard.png", "Batumi Harbor.png"},			
			attributes = {"Structure"},
			firepower = {
				min = 4,
				max = 8,
			},
			elements = {
				[1] = {
					name = "Batumi Harbor Fuel Tank 1",
					x = -351435.31738281,
					y = 621042.38769531,
				},
				[2] = {
					name = "Batumi Harbor Fuel Tank 2",
					x = -351471.55322266,
					y = 620717.09375,
				},
				[3] = {
					name = "Batumi Harbor Fuel Tank 3",
					x = -351458.22460938,
					y = 620707.38525391,
				},
				[4] = {
					name = "Batumi Harbor Fuel Tank 4",
					x = -351378.99511719,
					y = 620719.13720703,
				},
				[5] = {
					name = "Batumi Harbor Fuel Tank 5",
					x = -351334.72314453,
					y = 620753.46728516,
				},
				[6] = {
					name = "Batumi Harbor Fuel Tank 6",
					x = -351193.66943359,
					y = 620711.55419922,
				},
				[7] = {
					name = "Batumi Harbor Fuel Tank 7",
					x = -351176.08789063,
					y = 620699.69433594,
				},
				[8] = {
					name = "Batumi Harbor Fuel Tank 8",
					x = -351157.61328125,
					y = 620687.23193359,
				},
				[9] = {
					name = "Batumi Harbor Hangar 1",
					x = -351415.05371094,
					y = 620985.20703125,
				},
				[10] = {
					name = "Batumi Harbor Hangar 2",
					x = -351398.60742188,
					y = 621009.58789063,
				},
				[11] = {
					name = "Batumi Harbor Hangar 3",
					x = -351194.83349609,
					y = 620815.92480469,
				},
				[12] = {
					name = "Batumi Harbor Hangar 4",
					x = -351194.22851563,
					y = 620668.17773438,
				},
				[13] = {
					name = "Batumi Harbor Hangar 5",
					x = -351115.78320313,
					y = 620664.43554688,
				},
				[14] = {
					name = "Batumi Harbor Hangar 6",
					x = -351096.95898438,
					y = 620692.34179688,
				},
				[15] = {
					name = "Batumi Harbor Hangar 7",
					x = -351176.81738281,
					y = 620521.88476563,
				},
				[16] = {
					name = "Batumi Harbor Hangar 8",
					x = -351118.00585938,
					y = 620472.18945313,
				},
				[17] = {
					name = "Batumi Harbor Hangar 9",
					x = -351128.65185547,
					y = 620603.54101563,
				},
				[18] = {
					name = "Batumi Harbor Hangar 10",
					x = -351058.64404297,
					y = 620552.19335938,
				},
				[19] = {
					name = "Batumi Harbor Hangar 11",
					x = -351021.15136719,
					y = 620526.94433594,
				},
				[20] = {
					name = "Batumi Harbor Hangar 12",
					x = -350943.17382813,
					y = 620548.86035156,
				},
				[21] = {
					name = "Batumi Harbor Hangar 13",
					x = -350920.21435547,
					y = 620593.23486328,
				},
				[22] = {
					name = "Batumi Harbor Hangar 14",
					x = -350949.62451172,
					y = 620402.96386719,
				},
				[23] = {
					name = "Batumi Harbor Hangar 15",
					x = -351244.16015625,
					y = 621355.69824219,
				},
			},
		},
		["Batumi Harbor Supply"] = {
			task = "Strike",
			picture = {"Batumi Marshalling Yard.png", "Batumi Harbor.png"},
			priority = 4,
			attributes = {"soft"},
			firepower = {
				min = 4,
				max = 8,
			},
			class = "static",
			elements = {
				[1] = {
					name = "Batumi Harbor Tanker 1",
				},
				[2] = {
					name = "Batumi Harbor Tanker 2",
				},
				[3] = {
					name = "Batumi Harbor Cargo ship 1",
				},
				[4] = {
					name = "Batumi Harbor Cargo ship 2",
				},
				[5] = {
					name = "Batumi Harbor Cargo ship 3",
				},
				[6] = {
					name = "Batumi Harbor truck 1",
				},
				[7] = {
					name = "Batumi Harbor truck 2",
				},
				[8] = {
					name = "Batumi Harbor truck 3",
				},
				[9] = {
					name = "Batumi Harbor truck 4",
				},
				[10] = {
					name = "Batumi Harbor truck 5",
				},
				[11] = {
					name = "Batumi Harbor truck 6",
				},
				[12] = {
					name = "Batumi Harbor truck 7",
				},
				[13] = {
					name = "Batumi Harbor truck 8",
				},
				[14] = {
					name = "Batumi Harbor truck 9",
				},
				[15] = {
					name = "Batumi Harbor truck 10",
				},
				[16] = {
					name = "Batumi Harbor truck 11",
				},
				[17] = {
					name = "Batumi Harbor truck 12",
				},
				[18] = {
					name = "Batumi Harbor truck 13",
				},
				[19] = {
					name = "Batumi Harbor truck 14",
				},
				[20] = {
					name = "Batumi Harbor truck 15",
				},
				[21] = {
					name = "Batumi Harbor truck 16",
				},
				[22] = {
					name = "Batumi Harbor truck 17",
				},
				[23] = {
					name = "Batumi Harbor truck 18",
				},
				[24] = {
					name = "Batumi Harbor truck 19",
				},
				[25] = {
					name = "Batumi Harbor truck 20",
				},
				[26] = {
					name = "Batumi Harbor truck 21",
				},
				[27] = {
					name = "Batumi Harbor truck 22",
				},
				[28] = {
					name = "Batumi Harbor truck 23",
				},
				[29] = {
					name = "Batumi Harbor truck 24",
				},
				[30] = {
					name = "Batumi Harbor truck 25",
				},
				[31] = {
					name = "Batumi Harbor truck 26",
				},
			},
		},
		["Sukhumi Russian Army Depot"] = {
			task = "Strike",
			picture = {"Sukhumi Russian Army Depot.png", "Sukhumi Russian Army Depot 2.png"},
			priority = 5,
			attributes = {"soft"},
			firepower = {
				min = 4,
				max = 8,
			},
			class = "static",
			elements = {
				[1] = {
					name = "Sukhumi Russian Army Depot 1",
				},
				[2] = {
					name = "Sukhumi Russian Army Depot 2",
				},
				[3] = {
					name = "Sukhumi Russian Army Depot 3",
				},
				[4] = {
					name = "Sukhumi Russian Army Depot 4",
				},
				[5] = {
					name = "Sukhumi Russian Army Depot 5",
				},
				[6] = {
					name = "Sukhumi Russian Army Depot 6",
				},
				[7] = {
					name = "Sukhumi Russian Army Depot 7",
				},
				[8] = {
					name = "Sukhumi Russian Army Depot 8",
				},
				[9] = {
					name = "Sukhumi Russian Army Depot 9",
				},
				[10] = {
					name = "Sukhumi Russian Army Depot 10",
				},
				[11] = {
					name = "Sukhumi Russian Army Depot 11",
				},
				[12] = {
					name = "Sukhumi Russian Army Depot 12",
				},
				[13] = {
					name = "Sukhumi Russian Army Depot 13",
				},
				[14] = {
					name = "Sukhumi Russian Army Depot 14",
				},
				[15] = {
					name = "Sukhumi Russian Army Depot 15",
				},
				[16] = {
					name = "Sukhumi Russian Army Depot 16",
				},
				[17] = {
					name = "Sukhumi Russian Army Depot 17",
				},
				[18] = {
					name = "Sukhumi Russian Army Depot 18",
				},
				[19] = {
					name = "Sukhumi Russian Army Depot 19",
				},
				[20] = {
					name = "Sukhumi Russian Army Depot 20",
				},
				[21] = {
					name = "Sukhumi Russian Army Depot 21",
				},
				[22] = {
					name = "Sukhumi Russian Army Depot 22",
				},
				[23] = {
					name = "Sukhumi Russian Army Depot 23",
				},
				[24] = {
					name = "Sukhumi Russian Army Depot 24",
				},
				[25] = {
					name = "Sukhumi Russian Army Depot 25",
				},
				[26] = {
					name = "Sukhumi Russian Army Depot 26",
				},
				[27] = {
					name = "Sukhumi Russian Army Depot 27",
				},
				[28] = {
					name = "Sukhumi Russian Army Depot 28",
				},
				[29] = {
					name = "Sukhumi Russian Army Depot 29",
				},
				[30] = {
					name = "Sukhumi Russian Army Depot 30",
				},
			},
		},
		["Kutaisi Russian Army Depot"] = {
			task = "Strike",
			picture = {"Kutaisi Russian Army Depot.png", "Kutaisi Russian Army Depot 2.png"},
			priority = 5,
			attributes = {"soft"},
			firepower = {
				min = 4,
				max = 8,
			},
			class = "static",
			elements = {
				[1] = {
					name = "Kutaisi Russian Army Depot 1",
				},
				[2] = {
					name = "Kutaisi Russian Army Depot 2",
				},
				[3] = {
					name = "Kutaisi Russian Army Depot 3",
				},
				[4] = {
					name = "Kutaisi Russian Army Depot 4",
				},
				[5] = {
					name = "Kutaisi Russian Army Depot 5",
				},
				[6] = {
					name = "Kutaisi Russian Army Depot 6",
				},
				[7] = {
					name = "Kutaisi Russian Army Depot 7",
				},
				[8] = {
					name = "Kutaisi Russian Army Depot 8",
				},
				[9] = {
					name = "Kutaisi Russian Army Depot 9",
				},
				[10] = {
					name = "Kutaisi Russian Army Depot 10",
				},
				[11] = {
					name = "Kutaisi Russian Army Depot 11",
				},
				[12] = {
					name = "Kutaisi Russian Army Depot 12",
				},
				[13] = {
					name = "Kutaisi Russian Army Depot 13",
				},
				[14] = {
					name = "Kutaisi Russian Army Depot 14",
				},
				[15] = {
					name = "Kutaisi Russian Army Depot 15",
				},
				[16] = {
					name = "Kutaisi Russian Army Depot 16",
				},
				[17] = {
					name = "Kutaisi Russian Army Depot 17",
				},
				[18] = {
					name = "Kutaisi Russian Army Depot 18",
				},
				[19] = {
					name = "Kutaisi Russian Army Depot 19",
				},
				[20] = {
					name = "Kutaisi Russian Army Depot 20",
				},
				[21] = {
					name = "Kutaisi Russian Army Depot 21",
				},
				[22] = {
					name = "Kutaisi Russian Army Depot 22",
				},
				[23] = {
					name = "Kutaisi Russian Army Depot 23",
				},
				[24] = {
					name = "Kutaisi Russian Army Depot 24",
				},
				[25] = {
					name = "Kutaisi Russian Army Depot 25",
				},
				[26] = {
					name = "Kutaisi Russian Army Depot 26",
				},
				[27] = {
					name = "Kutaisi Russian Army Depot 27",
				},
				[28] = {
					name = "Kutaisi Russian Army Depot 28",
				},
				[29] = {
					name = "Kutaisi Russian Army Depot 29",
				},
				[30] = {
					name = "Kutaisi Russian Army Depot 30",
				},
			},
		},		
		["Batumi Power Supply Unit"] = {
			task = "Strike",
			priority = 3,
			picture = {"Batumi Power Supply Unit.png", "Batumi Power Supply Unit2.png"},			
			attributes = {"Structure"},
			firepower = {
				min = 2,
				max = 8,
			},
			elements = {
				[1] = {
					name = "Batumi Power Supply Main Structure",
					x = -353819.09277344,
					y = 621881.40527344,
				},
				[2] = {
					name = "Batumi Power Supply Fuel Tank 1",
					x = -353884.28198242,
					y = 621878.83105469,
				},
				[3] = {
					name = "Batumi Power Supply Fuel Tank 2",
					x = -353957.31616211,
					y = 621883.60742188,
				},
				[4] = {
					name = "Batumi Power Supply Fuel Tank 3",
					x = -353922.57373047,
					y = 621887.21484375,
				},
				[5] = {
					name = "Batumi Power Supply Fuel Tank 4",
					x = -353942.5546875,
					y = 621902.6796875,
				},
				[6] = {
					name = "Batumi Power Supply Fuel Tank 5",
					x = -353908.24560547,
					y = 621905.72802734,
				},
				[7] = {
					name = "Batumi Power Supply Fuel Tank 6",
					x = -353928.2265625,
					y = 621921.19287109,
				},
				[8] = {
					name = "Batumi Power Supply Fuel Tank 7",
					x = -353893.48413086,
					y = 621924.80029297,
				},
				[9] = {
					name = "Batumi Power Supply Fuel Tank 8",
					x = -353903.6619873,
					y = 621853.79101563,
				},
				[10] = {
					name = "Batumi Power Supply Fuel Tank 9",
					x = -353937.33520508,
					y = 621868.14257813,
				},
				[11] = {
					name = "Batumi Power Supply Fuel Tank 10",
					x = -353864.94824219,
					y = 621903.81152344,
				},
				[12] = {
					name = "Batumi Power Supply Fuel Tank 11",
					x = -353913.46508789,
					y = 621940.26513672,
				},
				[13] = {
					name = "Batumi Power Supply Hangar 1",
					x = -353863.45019531,
					y = 621953.19238281,
				},
				[14] = {
					name = "Batumi Power Supply Hangar 2",
					x = -353881.76660156,
					y = 621964.36621094,
				},
				[15] = {
					name = "Batumi Power Supply Hangar 3",
					x = -353846.39746094,
					y = 621941.53417969,
				},
				[16] = {
					name = "Batumi Power Supply Hangar 4",
					x = -353899.60546875,
					y = 621978.17285156,
				},
			},
		},
		["Kutaisi Air Supply Base"] = {
			task = "Strike",
			picture = {"Kutaisi Air Supply Base.png"},
			priority = 5,
			attributes = {"soft"},
			firepower = {
				min = 2,
				max = 8,
			},
			class = "static",
			elements = {
				[1] = {
					name = "Kutaisi Air Supply Base Mi-26-1",
				},
				[2] = {
					name = "Kutaisi Air Supply Base Mi-26-2",
				},
				[3] = {
					name = "Kutaisi Air Supply Base Mi-26-3",
				},
				[4] = {
					name = "Kutaisi Air Supply Base Mi-26-4",
				},
				[5] = {
					name = "Kutaisi Air Supply Base AN-30-1",
				},
				[6] = {
					name = "Kutaisi Air Supply Base AN-30-2",
				},
				[7] = {
					name = "Kutaisi Air Supply Base AN-30-3",
				},
				[8] = {
					name = "Kutaisi Air Supply Base Hangar 1",
				},
				[9] = {
					name = "Kutaisi Air Supply Base Hangar 2",
				},
				[10] = {
					name = "Kutaisi Air Supply Base Hangar 3",
				},
				[11] = {
					name = "Kutaisi Air Supply Base Hangar 4",
				},
				[12] = {
					name = "Kutaisi Air Supply Base Truck 1",
				},
				[13] = {
					name = "Kutaisi Air Supply Base Truck 2",
				},
				[14] = {
					name = "Kutaisi Air Supply Base Truck 3",
				},
				[15] = {
					name = "Kutaisi Air Supply Base Truck 4",
				},
				[16] = {
					name = "Kutaisi Air Supply Base Truck 5",
				},
				[17] = {
					name = "Kutaisi Air Supply Base Truck 6",
				},
				[18] = {
					name = "Kutaisi Air Supply Base Fuel Tank 1",
				},
				[19] = {
					name = "Kutaisi Air Supply Base Fuel Tank 2",
				},
				[20] = {
					name = "Kutaisi Air Supply Base Fuel Tank 3",
				},
				[21] = {
					name = "Kutaisi Air Supply Base Fuel Tank 4",
				},
				[22] = {
					name = "Kutaisi Air Supply Base Fuel Truck 1",
				},
				[23] = {
					name = "Kutaisi Air Supply Base Fuel Truck 2",
				},
				[24] = {
					name = "Kutaisi Air Supply Base Fuel Truck 3",
				},
				[25] = {
					name = "Kutaisi Air Supply Base Fuel Truck 4",
				},
				[26] = {
					name = "Kutaisi Air Supply Base Fuel Truck 5",
				},
				[27] = {
					name = "Kutaisi Air Supply Base Fuel Truck 6",
				},
				[28] = {
					name = "Kutaisi Air Supply Base Command truck 1",
				},
				[29] = {
					name = "Kutaisi Air Supply Base Command truck 2",
				},
				[30] = {
					name = "Kutaisi Air Supply Base Command truck 3",
				},
				[31] = {
					name = "Kutaisi Air Supply Base Command truck 4",
				},
				[32] = {
					name = "Kutaisi Air Supply Base Convoy Truck 1",
				},
				[33] = {
					name = "Kutaisi Air Supply Base Convoy Truck 2",
				},
				[34] = {
					name = "Kutaisi Air Supply Base Convoy Truck 3",
				},
				[35] = {
					name = "Kutaisi Air Supply Base Convoy Truck 4",
				},
				[36] = {
					name = "Kutaisi Air Supply Base Convoy Truck 5",
				},
				[37] = {
					name = "Kutaisi Air Supply Base Convoy Truck 6",
				},
				[38] = {
					name = "Kutaisi Air Supply Base Convoy Truck 7",
				},
				[39] = {
					name = "Kutaisi Air Supply Base Convoy Truck 8",
				},
			},
		},		
		["Zugdidi Power Supply Complex"] = {
			task = "Strike",
			priority = 3,
			picture = {"Zugdidi Power Supply Complex.png"},			
			attributes = {"Structure"},
			firepower = {
				min = 2,
				max = 8,
			},
			elements = {
				[1] = {
					name = "Zugdidi Power Supply Complex Main Structure",
					x = -254855.10546875,
					y = 626719.45019531,
				},
				[2] = {
					name = "Zugdidi Power Supply Complex Main Structure 2",
					x = -254361.63085938,
					y = 626969.03320313,
				},
				[3] = {
					name = "Zugdidi Power Supply Complex Main Structure 3",
					x = -254143.90820313,
				y = 626935.04492188,
				},
				[4] = {
					name = "Zugdidi Power Supply Complex Main Structure 4",
					x = -255072.82226563,
					y = 626753.45117188,
				},
				[5] = {
					name = "Zugdidi Power Supply Complex Main Structure 5",
					x = -254752.38671875,
					y = 627670.94238281,
				},
				[6] = {
					name = "Zugdidi Power Supply Complex Small Structure 1",
					x = -254656.0625,
					y = 626671.68164063,
				},
				[7] = {
					name = "Zugdidi Power Supply Complex Small Structure 2",
					x = -254918.03710938,
					y = 626857.00097656,
				},
				[8] = {
					name = "Zugdidi Power Supply Complex Small Structure 3",
					x = -254298.69921875,
					y = 626831.50341797,
				},
				[9] = {
					name = "Zugdidi Power Supply Complex Small Structure 4",
					x = -254340.59179688,
					y = 627229.23876953,
				},
				[10] = {
					name = "Zugdidi Power Supply Complex Small Structure 5",
					x = -253983.22851563,
					y = 627389.06054688,
				},
				[11] = {
					name = "Zugdidi Power Supply Complex Fuel Tank 1",
					x = -254858.40527344,
					y = 626523.30419922,
				},
				[12] = {
					name = "Zugdidi Power Supply Complex Fuel Tank 2",
					x = -254673.80175781,
					y = 626607.59619141,
				},
				[13] = {
					name = "Zugdidi Power Supply Complex Fuel Tank 3",
					x = -254358.33007813,
					y = 627165.15332031,
				},
				[14] = {
					name = "Zugdidi Power Supply Complex Main line",
					x = -254608.5,
					y = 627186.5,
				},
			},
		},
		["Tbilisi High Value Target"] = {
			task = "Strike",
			priority = 6,
			picture = {"Tbilisi High Value Target.png", "Tbilisi High Value Target Zone.png"},			
			attributes = {"Structure"},
			firepower = {
				min = 2,
				max = 4,
			},
			elements = {
				[1] = {
					name = "Tbilisi Russian HQ",
					x = -312621.16015625,
					y = 882128.07617188,
				},
				[2] = {
					name = "Tbilisi Russian Intelligence HQ",
					x = -312865.32434082,
					y = 882050.53417969,
				},
				[3] = {
					name = "Tbilisi Russian Air Force HQ",
					x = -312938.66748047,
					y = 882121.21386719,
				},
				[4] = {
					name = "Tbilisi Russian Army HQ",
					x = -312963.33581543,
					y = 882050.31542969,
				},
			},
		},		
		["Sukhumi Airbase"] = {
			task = "Strike",
			priority = 4,
			picture = {"Sukhumi Airbase.png"},			
			attributes = {"Structure"},
			firepower = {
				min = 2,
				max = 8,
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
		["Sukhumi Airbase Strategics"] = {
			task = "Strike",
			priority = 4,
			picture = {"Sukhumi Airbase.png"},
			attributes = {"Structure"},
			firepower = {
				min = 2,
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
			priority = 4,
			picture = {"Gudauta Airbase South.png", "Gudauta Airbase North.png"},			
			attributes = {"Structure"},
			firepower = {
				min = 2,
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
			priority = 4,
			picture = {"Senaki Airbase.png", "Senaki Airbase-Ammo.png"},			
			attributes = {"Structure"},
			firepower = {
				min = 2,
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
				min = 2,
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
			priority = 4,
			picture = {"Kobuleti Airbase.png", "Kobuleti Airbase-Ammo-Hangar-Command.png"},			
			attributes = {"Structure"},
			firepower = {
				min = 2,
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
			priority = 6,
			picture = {"Batumi Airbase.png", "Batumi Airbase-Ammo.png"},			
			attributes = {"Structure"},
			firepower = {
				min = 2,
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
		["Tbilisi Airbase"] = {
			task = "Strike",
			priority = 1,
			picture = {"Tbilisi Airbase.png"},			
			attributes = {"Structure"},
			firepower = {
				min = 2,
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
		----- CVN-74 John C. Stennis Support -----
		-- ["Battle Group CAP"] = {
			-- task = "CAP",
			-- priority = 1,
			-- attributes = {},
			-- firepower = {
				-- min = 2,
				-- max = 2,
			-- },
			-- slaved = {"CVN-74 John C. Stennis", 080, 92600},
			-- radius = 111000,
			-- text = "",
		-- },
		-- ["Battle Group AEW"] = {
			-- task = "AWACS",
			-- priority = 1,
			-- attributes = {},
			-- firepower = {
				-- min = 1,
				-- max = 1,
			-- },
			-- slaved = {"CVN-74 John C. Stennis", 045, 55500},
			-- text = "",
		-- },
		-- ["Mission Support Tanker 1"] = {
			-- task = "Refueling",
			-- priority = 1,
			-- attributes = {"medium"},
			-- firepower = {
				-- min = 1,
				-- max = 1,
			-- },
			-- slaved = {"CVN-74 John C. Stennis", 080, 83300},
			-- text = "",
		-- },
		-- ["Mission Support Tanker 2"] = {
			-- task = "Refueling",
			-- priority = 1,
			-- attributes = {"medium"},
			-- firepower = {
				-- min = 1,
				-- max = 1,
			-- },
			-- slaved = {"CVN-74 John C. Stennis", 090, 83300},
			-- text = "",
		-- },		
		-- ["Recovery Tanker 1"] = {
			-- task = "Refueling",
			-- priority = 1.1,
			-- attributes = {"low"},
			-- firepower = {
				-- min = 1,
				-- max = 1,
			-- },
			-- slaved = {"CVN-74 John C. Stennis", 080, 10000},
			-- text = "",
		-- },
		-- ["Recovery Tanker 2"] = {
			-- task = "Refueling",
			-- priority = 1.1,
			-- attributes = {"low"},
			-- firepower = {
				-- min = 1,
				-- max = 1,
			-- },
			-- slaved = {"CVN-74 John C. Stennis", 090, 10000},
			-- text = "",
		-- },		
		-- ["Outer ASW Patrol"] = {
			-- task = "CAP",
			-- priority = 1,
			-- attributes = {"Viking"},
			-- firepower = {
				-- min = 1,
				-- max = 1,
			-- },
			-- slaved = {"CVN-74 John C. Stennis", 075, 92600},
			-- radius = 0,
			-- text = "",
		-- },
		-- ["Inner ASW Patrol"] = {
			-- task = "CAP",
			-- priority = 1,
			-- attributes = {"Seahawk"},
			-- firepower = {
				-- min = 1,
				-- max = 1,
			-- },
			-- slaved = {"CVN-74 John C. Stennis", 045, 27700},
			-- radius = 0,
			-- text = "",
		-- },		
	},
	["red"] = {
		["CAP Red North"] = {
			task = "CAP",
			priority = 1,
			attributes = {},
			firepower = {
				min = 2,
				max = 2,
			},
			refpoint = "CAP Red North",
			radius = 100000,
			text = "CAP Red North",
			inactive = true,
		},
		["CAP Red Center"] = {
			task = "CAP",
			priority = 1,
			attributes = {},
			firepower = {
				min = 2,
				max = 2,
			},
			refpoint = "CAP Red Center",
			radius = 100000,
			text = "CAP Red Center",
			inactive = true,
		},
		["CAP Red South"] = {
			task = "CAP",
			priority = 1,
			attributes = {},
			firepower = {
				min = 2,
				max = 2,
			},
			refpoint = "CAP Red South",
			radius = 100000,
			text = "CAP Red South",
			inactive = true,
		},
		["CAP Red Georgia Center"] = {
			task = "CAP",
			priority = 1,
			attributes = {},
			firepower = {
				min = 2,
				max = 4,
			},
			refpoint = "CAP Red Georgia Center",
			radius = 100000,
			text = "CAP Red Georgia Center",
			inactive = false,
		},		
		-- ["Airlift Batumi 1"] = {
			-- task = "Transport",
			-- priority = 1,
			-- attributes = {},
			-- firepower = {
				-- min = 1,
				-- max = 1,
			-- },
			-- base = "Sochi-Adler",
			-- destination = "Batumi",
		-- },
		-- ["Airlift Senaki-Kolkhi"] = {
			-- task = "Transport",
			-- priority = 1,
			-- attributes = {},
			-- firepower = {
				-- min = 1,
				-- max = 1,
			-- },
			-- base = "Gudauta",
			-- destination = "Senaki-Kolkhi",
		-- },
		-- ["Airlift Senaki-Kolkhi 2"] = {
			-- task = "Transport",
			-- priority = 1,
			-- attributes = {},
			-- firepower = {
				-- min = 1,
				-- max = 1,
			-- },
			-- base = "Sukhumi",
			-- destination = "Senaki-Kolkhi",
		-- },
		-- ["Airlift Batumi 2"] = {
			-- task = "Transport",
			-- priority = 1,
			-- attributes = {},
			-- firepower = {
				-- min = 1,
				-- max = 1,
			-- },
			-- base = "Senaki-Kolkhi",
			-- destination = "Batumi",
		-- },
		-- ["Airlift Gudauta"] = {
			-- task = "Transport",
			-- priority = 1,
			-- attributes = {},
			-- firepower = {
				-- min = 1,
				-- max = 1,
			-- },
			-- base = "Senaki-Kolkhi",
			-- destination = "Gudauta",
		-- },		
		-- ["Airlift Sochi-Adler"] = {
			-- task = "Transport",
			-- priority = 1,
			-- attributes = {},
			-- firepower = {
				-- min = 1,
				-- max = 1,
			-- },
			-- base = "Batumi",
			-- destination = "Sochi-Adler",
		-- },
		-- ["Airlift Sochi-Adler 2"] = {
			-- task = "Transport",
			-- priority = 1,
			-- attributes = {},
			-- firepower = {
				-- min = 1,
				-- max = 1,
			-- },
			-- base = "Sukhumi",
			-- destination = "Sochi-Adler",
		-- },		
		["Batumi Interception 1"] = {
			task = "Intercept",
			priority = 10,
			attributes = {},
			firepower = {
				min = 2,
				max = 4,
			},
			base = "Batumi",
			radius = 100000,
			inactive = false,
		},
		["Batumi Interception 2"] = {
			task = "Intercept",
			priority = 5,
			attributes = {},
			firepower = {
				min = 2,
				max = 4,
			},
			base = "Batumi",
			radius = 100000,
			inactive = false,
		},
		["Batumi Interception Standby 1"] = {
			task = "Intercept",
			priority = 3,
			attributes = {},
			firepower = {
				min = 2,
				max = 4,
			},
			base = "Batumi",
			radius = 50000,
			inactive = false,
		},
		["Sukhumi Interception 1"] = {
			task = "Intercept",
			priority = 10,
			attributes = {},
			firepower = {
				min = 2,
				max = 4,
			},
			base = "Sukhumi",
			radius = 90000,
			inactive = false,
		},
		["Sukhumi Interception 2"] = {
			task = "Intercept",
			priority = 5,
			attributes = {},
			firepower = {
				min = 2,
				max = 4,
			},
			base = "Sukhumi",
			radius = 90000,
			inactive = false,
		},
		["Sukhumi Interception Standby 1"] = {
			task = "Intercept",
			priority = 2,
			attributes = {},
			firepower = {
				min = 2,
				max = 4,
			},
			base = "Sukhumi",
			radius = 50000,
			inactive = false,
		},
		["Gudauta Interception 1"] = {
			task = "Intercept",
			priority = 10,
			attributes = {},
			firepower = {
				min = 2,
				max = 4,
			},
			base = "Gudauta",
			radius = 90000,
			inactive = false,
		},
		["Gudauta Interception 2"] = {
			task = "Intercept",
			priority = 5,
			attributes = {},
			firepower = {
				min = 2,
				max = 4,
			},
			base = "Gudauta",
			radius = 90000,
			inactive = false,
		},		
		["Kutaisi Interception 1"] = {
			task = "Intercept",
			priority = 10,
			attributes = {},
			firepower = {
				min = 2,
				max = 4,
			},
			base = "Kutaisi",
			radius = 180000,
			inactive = false,
		},
		["Kutaisi Interception 2"] = {
			task = "Intercept",
			priority = 5,
			attributes = {},
			firepower = {
				min = 2,
				max = 4,
			},
			base = "Kutaisi",
			radius = 180000,
			inactive = false,
		},		
		["Mozdok Interception 1"] = {
			task = "Intercept",
			priority = 10,
			attributes = {},
			firepower = {
				min = 2,
				max = 4,
			},
			base = "Mozdok",
			radius = 300000,
			inactive = false,
		},	
		["Mozdok Interception 2"] = {
			task = "Intercept",
			priority = 5,
			attributes = {},
			firepower = {
				min = 2,
				max = 4,
			},
			base = "Mozdok",
			radius = 300000,
			inactive = false,
		},			
		["TF-71"] = {
			task = "Anti-ship Strike",
			picture = {"TF-71.png"},
			priority = 10,
			attributes = {"ship"},
			firepower = {
				min = 4,
				max = 30,
				packmax = 25,
			},
			class = "vehicle",
			name = "TF-71",
		},
		["TF-74"] = {
			task = "Anti-ship Strike",
			picture = {""},
			priority = 10,
			attributes = {"ship"},
			firepower = {
				min = 4,
				max = 30,
				packmax = 25,
			},
			class = "vehicle",
			name = "TF-74",
		},
		["LHA-Group"] = {
			task = "Anti-ship Strike",
			picture = {""},
			priority = 10,
			attributes = {"ship"},
			firepower = {
				min = 4,
				max = 30,
				packmax = 25,
			},
			class = "vehicle",
			name = "LHA-Group",
		},
		-- ["TF-68.2"] = {
			-- task = "Anti-ship Strike",
			-- picture = {"TF-68-2.png"},
			-- priority = 10,
			-- attributes = {"ship"},
			-- firepower = {
				-- min = 4,
				-- max = 30,
				-- packmax = 25,
			-- },
			-- class = "vehicle",
			-- name = "TF-68.2",
		-- },
		-- ["CVN-70 Carl Vinson"] = {
			-- task = "Anti-ship Strike",
			-- priority = 1,
			-- attributes = {"ship"},
			-- firepower = {
				-- min = 40,
				-- max = 240,
			-- },
			-- class = "ship",
			-- name = "CVN-70 Carl Vinson",
		-- },
		-- ["CVN-71 Theodore Roosevelt"] = {
			-- task = "Anti-ship Strike",
			-- priority = 1,
			-- attributes = {"ship"},
			-- firepower = {
				-- min = 40,
				-- max = 240,
			-- },
			-- class = "ship",
			-- name = "CVN-71 Theodore Roosevelt",
		-- },
		-- ["CVN-72 Abraham Lincoln"] = {
			-- task = "Anti-ship Strike",
			-- priority = 1,
			-- attributes = {"ship"},
			-- firepower = {
				-- min = 40,
				-- max = 240,
			-- },
			-- class = "ship",
			-- name = "CVN-72 Abraham Lincoln",
		-- },		
		-- ["LHA_Tarawa"] = {
			-- task = "Anti-ship Strike",
			-- priority = 1,
			-- attributes = {"ship"},
			-- firepower = {
				-- min = 40,
				-- max = 240,
			-- },
			-- class = "ship",
			-- name = "LHA_Tarawa",
		-- },		
		-- ["TF_Escort"] = {
			-- task = "Anti-ship Strike",
			-- priority = 2,
			-- attributes = {"ship"},
			-- firepower = {
				-- min = 40,
				-- max = 240,
			-- },
			-- class = "ship",
			-- name = "TF_Escort",
		-- },
		["Recon TF Nord"] = {
			task = "Reconnaissance",
			priority = 5,
			attributes = {},
			firepower = {
				min = 1,
				max = 1,
			},
			refpoint = "Recon TF Nord",
			radius = 15000,
			text = "Recon TF Nord",
		},
		["Recon TF South"] = {
			task = "Reconnaissance",
			priority = 5,
			attributes = {},
			firepower = {
				min = 1,
				max = 1,
			},
			refpoint = "Recon TF South",
			radius = 15000,
			text = "Recon TF South",
		},		
	},
}