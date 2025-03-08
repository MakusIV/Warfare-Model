--
--
------------------------------------------------------------------------------------------------------- 
-- Miguel Fichier Revision M33.d
------------------------------------------------------------------------------------------------------- 
-- Miguel21 modification M33.d VOR + NDB Custom Briefing (d: Divert)

--[[ db_airbases Entry Example ----------------------------------------------------------------------------
	--example for an air base
	['Kerman Airbase'] = {
		x =	454116.78125,
		y = 71096.058594,
		elevation = 1751,
		airdromeId = 18,
		ATC_frequency = "250.300",
		--startup = 300,							-- (secondes) Timing for take-off, generally used for small runways to give time for all aircraft to gather together
		side = "red",								-- side : Required information for the divert
		divert = true,								-- divert : Required information for the divert)
		--VOR = "112.00",							-- optional information
		--NDB = "",									-- optional information
		--TACAN = "97X",							-- TACAN : optional information
		--ILS = "RWY 30R/111.95 RWY 12L/108.55",	-- ILS : optional information
		LimitedParkNb = 3,							-- number of parking spaces available
	},
	--example for an airplane carrier
	['CVN-71 Theodore Roosevelt'] = {                            
		unitname = "CVN-71 Theodore Roosevelt",
		startup = 300,								-- (secondes) Timing for take-off, generally used for small runways to give time for all aircraft to gather together
		ATC_frequency = "255.500",					-- Optional information, if absent, the base_mission frequency will be used.
	},	
	--example for a FARP
	['As Salamah FARP'] = {
		x =	-74348.375716192,
		y = -67705.331836707,
		elevation = 0,
		airdromeId = 837,							--be careful this Id depends on units placements and is helipadID in fact
		helipadId = 837,
		ATC_frequency = "128.600",
		side = "blue",								-- side : Required information for the divert
		divert = false,								-- divert : Required information for the divert)
	},	
	--example for a Virtual Base
	['Reserves'] = {								--dummy airbase to place virtual reserves
		inactive = true,
		x =	9999999999,								--position far away will make all range checks negative
		y = 9999999999,
		elevation = 0,
		airdromeId = nil,							--no id makes sure that no static aircraft are to be placed at this air base
		ATC_frequency = "0",
	},

]]-----------------------------------------------------------------------------------------------------



db_airbases = {
	['Vaziani'] = {
		x =	-319069.063,
		y = 903150.625,
		elevation = 455,
		airdromeId = 31,
		ATC_frequency = "269.000",
		startup = 800,
		side = "red",							-- side : info obligatoire
		divert = true,							-- divert : info obligatoire (pour l instant)
		VOR = "",
		-- NDB = "",
		TACAN = "22X",							-- TACAN : optionnel
		ILS = "RWY 135/108.75 RWY 315/108.75",							-- ILS : optionnel
		LimitedParkNb = 91,
	},
	['Tbilissi-Lochini'] = {
		x =	-315478.57142857,
		y = 896538.85714286,
		elevation = 471,
		airdromeId = 29,
		ATC_frequency = "267.000",
		startup = 800,
		side = "red",							-- side : info obligatoire
		divert = true,							-- divert : info obligatoire (pour l instant)
		VOR = "113.7",
		NDB = "342.00 923.00 211.00 435.00",
		TACAN = "25X",							-- TACAN : optionnel
		ILS = "RWY 122/110.30 RWY 302/108.90",							-- ILS : optionnel
		LimitedParkNb = 73,
	},
	['Soganlug'] = {
		x =	-317838.57142857,
		y = 895424.57142858,
		elevation = 449,
		airdromeId = 30,
		ATC_frequency = "268.000",
		startup = 800,
		side = "red",							-- side : info obligatoire
		divert = true,							-- divert : info obligatoire (pour l instant)
		-- VOR = "",
		-- NDB = "",
		TACAN = "25X",							-- TACAN : optionnel
		-- ILS = "",							-- ILS : optionnel
		LimitedParkNb = 05,
	},
	['Kutaisi'] = {
		x =	-284889.06283057,
		y = 683853.75717885,
		elevation = 45,
		airdromeId = 25,
		ATC_frequency = "263.000",
		startup = 600,
		side = "red",							-- side : info obligatoire
		divert = true,							-- divert : info obligatoire (pour l instant)
		VOR = "113.6",
		NDB = "477.00",
		TACAN = "44X",							-- TACAN : optionnel
		ILS = "RWY 068/109.75",							-- ILS : optionnel
		LimitedParkNb = 58,
	},
	['Senaki-Kolkhi'] = {
		x =	-281713.83114196,
		y = 647369.87369832,
		elevation = 13,
		airdromeId = 23,
		ATC_frequency = "261.000",
		startup = 800,
		side = "red",							-- side : info obligatoire
		divert = true,							-- divert : info obligatoire (pour l instant)
		-- VOR = "",
		NDB = "335.00 688.00",
		TACAN = "31X",							-- TACAN : optionnel
		ILS = "RWY 089/108.90",							-- ILS : optionnel
		LimitedParkNb = 67,
	},
	['Kobuleti'] = {
		x = -317948.32727306,
		y =	635639.37385346,
		elevation = 18,
		airdromeId = 24,
		ATC_frequency = "262.000",
		startup = 800,
		side = "red",							-- side : info obligatoire
		divert = true,							-- divert : info obligatoire (pour l instant)
		-- VOR = "",
		NDB = "870.00 490.00",
		TACAN = "67X",							-- TACAN : optionnel
		ILS = "RWY 064/111.50",							-- ILS : optionnel
		LimitedParkNb = 42,
	},
	['Batumi'] = {
		x =	-355692.3067714,
		y = 617269.96285781,
		elevation = 10,
		airdromeId = 22,
		ATC_frequency = "260.000",
		startup = 800,
		side = "red",							-- side : info obligatoire
		divert = true,							-- divert : info obligatoire (pour l instant)
		-- VOR = "",
		NDB = "430.00",
		TACAN = "16X",							-- TACAN : optionnel
		ILS = "RWY 120/110.30",							-- ILS : optionnel
		LimitedParkNb = 10,
	},
	['Sukhumi'] = {
		x =	-220531.73642658,
		y = 564387.05872916,
		elevation = 11,
		airdromeId = 20,
		ATC_frequency = "258.000",
		startup = 800,
		side = "red",							-- side : info obligatoire
		divert = true,							-- divert : info obligatoire (pour l instant)
		-- VOR = "",
		NDB = "489.00 995.00",
		-- TACAN = "",							-- TACAN : optionnel
		-- ILS = "",							-- ILS : optionnel
		LimitedParkNb = 20,
	},
	['Gudauta'] = {
		x =	-196974.19851241,
		y = 516290.23098695,
		elevation = 21,
		airdromeId = 21,
		ATC_frequency = "259.000",
		startup = 800,
		side = "red",							-- side : info obligatoire
		divert = true,							-- divert : info obligatoire (pour l instant)
		-- VOR = "",
		NDB = "395.00",
		-- TACAN = "",							-- TACAN : optionnel
		-- ILS = "",							-- ILS : optionnel
		LimitedParkNb = 31,
	},
	['Sochi-Adler'] = {
		x =	-164474.73482633,
		y = 462236.21834688,
		elevation = 30,
		airdromeId = 18,
		ATC_frequency = "256.000",
		startup = 800,
		side = "red",							-- side : info obligatoire
		divert = true,							-- divert : info obligatoire (pour l instant)
		-- VOR = "",
		NDB = "761.00",
		-- TACAN = "",							-- TACAN : optionnel
		ILS = "RWY 056/111.10",							-- ILS : optionnel
		LimitedParkNb = 68,
	},
	['Beslan'] = {
		x =	-148810.84954665,
		y = 843756.7533062,
		elevation = 540,
		airdromeId = 32,
		ATC_frequency = "270.000",
		startup = 800,
		side = "red",							-- side : info obligatoire
		divert = false,							-- divert : info obligatoire (pour l instant)
		-- VOR = "",
		NDB = "1050.00 250.00",
		-- TACAN = "",							-- TACAN : optionnel
		ILS = "RWY 086/110.50",							-- ILS : optionnel
		LimitedParkNb = 15,
	},
	['Nalchik'] = {
		x =	-124921.90954665,
		y = 760428.0733062,
		elevation = 430,
		airdromeId = 27,
		ATC_frequency = "265.000",
		startup = 800,
		side = "red",							-- side : info obligatoire
		divert = false,							-- divert : info obligatoire (pour l instant)
		-- VOR = "",
		NDB = "718.00 350.00",
		-- TACAN = "",							-- TACAN : optionnel
		ILS = "RWY 229/110.50",							-- ILS : optionnel
		LimitedParkNb = 14,
	},
	['Mozdok'] = {
		x =	-83454.571428571,
		y = 834453.14285714,
		elevation = 154,
		airdromeId = 28,
		ATC_frequency = "266.000",
		startup = 800,
		side = "red",							-- side : info obligatoire
		divert = false,							-- divert : info obligatoire (pour l instant)
		-- VOR = "",
		NDB = "525.00 1065.00",
		-- TACAN = "",							-- TACAN : optionnel
		-- ILS = "",							-- ILS : optionnel
		LimitedParkNb = 39,
	},
	['Mineralnye-Vody'] = {
		x =	-51251.551717591,
		y = 705718.47981263,
		elevation = 320,
		airdromeId = 26,
		ATC_frequency = "264.000",
		startup = 800,
		side = "red",							-- side : info obligatoire
		divert = false,							-- divert : info obligatoire (pour l instant)
		VOR = "117.1",
		NDB = "583.00 283.00",
		-- TACAN = "",							-- TACAN : optionnel
		ILS = "RWY 109/111.70 RWY 289/109.30",							-- ILS : optionnel
		LimitedParkNb = 28,
	},
	['Maykop-Khanskaya'] = {
		x =	-26441.347360305,
		y = 458040.61422532,
		elevation = 180,
		airdromeId = 16,
		ATC_frequency = "254.000",
		startup = 800,
		side = "red",							-- side : info obligatoire
		divert = false,							-- divert : info obligatoire (pour l instant)
		-- VOR = "",
		NDB = "289.00 591.00",
		-- TACAN = "",							-- TACAN : optionnel
		-- ILS = "",							-- ILS : optionnel
		LimitedParkNb = 57,
	},
	['Gelendzhik'] = {
		x =	-50392.648146355,
		y = 298387.43849386,
		elevation = 25,
		airdromeId = 17,
		ATC_frequency = "255.000",
		startup = 800,
		side = "red",							-- side : info obligatoire
		divert = false,							-- divert : info obligatoire (pour l instant)
		VOR = "114.3",
		-- NDB = "",
		-- TACAN = "",							-- TACAN : optionnel
		-- ILS = "",							-- ILS : optionnel
		LimitedParkNb = 13,
	},
	['Novorossiysk'] = {
		x =	-40915.496728899,
		y = 279256.64920952,
		elevation = 40,
		airdromeId = 14,
		ATC_frequency = "252.000",
		startup = 800,
		side = "red",							-- side : info obligatoire
		divert = false,							-- divert : info obligatoire (pour l instant)
		-- VOR = "",
		-- NDB = "",
		-- TACAN = "",							-- TACAN : optionnel
		-- ILS = "",							-- ILS : optionnel
		LimitedParkNb = 37,
	},
	['Krymsk'] = {
		x =	-6583.663574989,
		y = 294383.98405512,
		elevation = 20,
		airdromeId = 15,
		ATC_frequency = "253.000",
		startup = 800,
		side = "red",							-- side : info obligatoire
		divert = false,							-- divert : info obligatoire (pour l instant)
		-- VOR = "",
		NDB = "408.00 803.00",
		-- TACAN = "",							-- TACAN : optionnel
		-- ILS = "",							-- ILS : optionnel
		LimitedParkNb = 57,
	},
	['Anapa-Vityazevo'] = {
		x =	-5406.2803440839,
		y = 243127.2973737,
		elevation = 45,
		airdromeId = 12,
		ATC_frequency = "250.000",
		startup = 800,
		side = "red",							-- side : info obligatoire
		divert = false,							-- divert : info obligatoire (pour l instant)
		-- VOR = "",
		NDB = "443.00 215.00",
		-- TACAN = "",							-- TACAN : optionnel
		-- ILS = "",							-- ILS : optionnel
		LimitedParkNb = 92,
	},
	['Krasnodar-Center'] = {
		x =	11692.789495652,
		y = 367948.47230953,
		elevation = 30,
		airdromeId = 13,
		ATC_frequency = "251.000",
		startup = 800,
		side = "red",							-- side : info obligatoire
		divert = false,							-- divert : info obligatoire (pour l instant)
		-- VOR = "",
		NDB = "625.00 303.00",
		-- TACAN = "",							-- TACAN : optionnel
		-- ILS = "",							-- ILS : optionnel
		LimitedParkNb = 56,
	},
	['Krasnodar-Pashkovsky'] = {
		x =	7674.038444859,
		y = 385029.5736699,
		elevation = 34,
		airdromeId = 19,
		ATC_frequency = "257.000",
		startup = 800,
		side = "red",							-- side : info obligatoire
		divert = false,							-- divert : info obligatoire (pour l instant)
		VOR = "115.8",
		NDB = "493.00 240.00",
		-- TACAN = "",							-- TACAN : optionnel
		-- ILS = "",							-- ILS : optionnel
		LimitedParkNb = 19,
	},
	['CVN-74 John C. Stennis'] = {                            
		unitname = "CVN-74 John C. Stennis",
		startup = 300,
		side = "blue",							-- side : info obligatoire
		LimitedParkNb  = 10, 
		ATC_frequency = "255.255",				--si ATC_frequency non present, on utilise la freq de base_mission
	},
	['CVN-71 Theodore Roosevelt'] = {                            
		unitname = "CVN-71 Theodore Roosevelt",
		startup = 300,
		side = "blue",							-- side : info obligatoire
		-- ATC_frequency = "255.500",			--si ATC_frequency non present, on utilise la freq de base_mission
		LimitedParkNb  = 9, 
	},	
	['LHA_Tarawa'] = {
		unitname = "LHA_Tarawa",
		startup = 300,
		side = "blue",							-- side : info obligatoire
		ATC_frequency = "250.255",				--si ATC_frequency non present, on utilise la freq de base_mission
		LimitedParkNb  = 4,
	},
	['Dyess AFB'] = {
		x = -298118.0120668,
		y = -89509.223854664, 
		elevation = 0,
		airdromeId = nil,
		side = "blue",							-- side : info obligatoire
		ATC_frequency = "0",
		BaseAirStart = true,
	},	
	['Reserves'] = {						--dummy airbase to place virtual reserves
		inactive = true,
		x =	9999999999,						--position far away will make all range checks negative
		y = 9999999999,
		elevation = 0,
		airdromeId = nil,					--no id makes sure that no static aircraft are to be placed at this air base
		ATC_frequency = "0",
	},
}
	