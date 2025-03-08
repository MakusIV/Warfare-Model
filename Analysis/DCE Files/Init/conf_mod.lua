--Modification PBO-CEF / Miguel21
-- Miguel Fichier Revision M18.e
------------------------------------------------------------------------------------------------------- 

-- Miguel21 modification M18.e despawn (e: option confMod)
-- mouvedOption_CM_01 : deplace les options de west callSign dans conf_mod

if not versionDCE then versionDCE = {} end
versionDCE["conf_mod.lua"] = "1.27.30"

-- 1 ############################################################################################################################################################
-- 1 ############################################################################################################################################################
-- The options in this first part of the file can be modified by players. Changes do not require the campaign to be restarted. They will automatically be taken 
--		into account for the generation of the next mission.
-- 1 ############################################################################################################################################################	
-- 1 ############################################################################################################################################################

mission_ini = {
	PruneScript = true,							-- reduce a mission by removing units (mod Tomsk M09)
	PruneAggressiveness = 1.9,					-- How aggressive should the pruning be [0 to 2], larger numbers will remove more units, 0 = no pruning at all
	PruneStatic = true,							-- (default : false), true: Should ALL parked (static) aircraft be pruned [MP: recommend: true]
	ForcedPruneSam = false,						-- (default : false), true: PBO-CEF wanted to keep some actives SAMs, this option desactivates them too. 
	
	AIemergencyLaunch = true,					-- (default : false), Tanks and Bombs emergency In Task Strike: autorise ou non aux AI à larguer leur emport sous la menace pendant un strike
	
	parking_hotstart = false,					-- (default : false), true: player flights starts with engines running on parking
	intercept_hotstart = true,					-- (default : true), true: player flights with intercept task starts with engines running on parking
	startup_time_player = 1500,					-- (default : 600), time in seconds allocated for startup, taxi and take off for player flight
	
	failure = false,							-- (default : false), true = aircraft failures activated, works in SOLO, bug in MP, M20
	failureProbMax = 10,						-- (1 to 100) probabilité maximum sur une panne -- Miguel21 modification M20
	failureNbMax = 5 ,							-- ( 1 to ...57?) Max failures number in one mission --Miguel21 modification M20
	
	Keep_USNdeckCrew = false,					-- (default : false), false = supprime US Navy deck crew dans la génération de mission (Ceci n'installe/desinstalle pas le MOD USN) Miguel Modification M23
	
	OnlyDayMission = false,						-- (default : false), true: Force all missions to be played in daylight (Mod M25)
	HourlyTolerance = 2,						-- %, When activating OnlyDayMission, allows you to play a little before or a little after the day. In percentage terms
	
	MovedBullseye = true, 						-- (default : true), true : Moves the bullseye to each mission
	
	TriggerStart = true,						-- (default : true), true: All planes appear at mission start (No freeze), but problems with using Mission Planner (Attack planes often don't attack target). false: some Planes appear during the mission so some freezes could occur but Mission Planner can be used without bugs ( M30 )
	
	CVN_CleanDeck = false, 						-- (default : false), true: Remove all static aircraft from the deck. ( M31 )
	CVN_TimeBtwPlane = 45, 						-- (default : false), Time between each aircraft for catapulting
	CVN_Vmax = 10,								-- (default = 15.4333( m/s)==30kts), can have bp with F14, go down to 10 m/s
	CVN_windDeck = 9,							-- (default = 13.89( m/s)==27kts), can have bp with F14, go down to 9 m/s
	CVN_despawnAfterLanding = true,				-- (default = true) despawn aircraft landing on CVN and LHA ,this avoids collisions between taxxing and landing aircraft

	SC_SpawnOn = {
		["F-14B"] = "deck",						-- (default: "deck"), "catapult", "air"
		["E-2C"] = "deck",
		["S-3B Tanker"] = "deck",
		["Pedro"] = "deck",
	},
	
	MP_PlaneRecovery = false,					--  (defaut: false) In multiplayer, this allows you to control an aircraft already in flight in case of a crash. M11.q
	SC_CarrierIntoWind = "man",				-- (defaut: "auto")("man"), "auto": Original Mbot code: the CVN rotates according to the air operations. "man": the CVN runs only once via the commands in the radio menu F10
	
	WrittenOnScratchpadMod = true,				-- (defaut: true) pre-fills the scratchpad MOD sheet, for the moment, only works if DCS is not launched.
	
	backupAllMissionFiles = false,				-- (defaut: false) only the last mission is saved //true: save all missions in the Debriefing directory,
	
}

-- Force your own options rather than those of base_ini.miz, which correspond to those of PBO-CEF ^^
-- Force vos propres options plutot que ceux de base_ini.miz, qui correspondent à ceux de PBO-CEF ^^
mission_forcedOptions = { 
	--["accidental_failures"] = true,						-- False / true : Panne aléatoire (sera automatiquement desactivé en multijoueur dans DCE)
	["wakeTurbulence"] = true,							-- False / true : turbulence  [MP: recommend: false]
	["labels"] = 0,										-- etiquette : ( 0 : aucune étiquette ) || ( 1 : étiquette PLEINE ) || ( 2 : étiquette abrégée )|| ( 3 : étiquette Plate )
	["optionsView"] = "optview_all",				-- Vue de la Map F10: ( "optview_onlymap": ONLY the MAP) || ( "optview_myaircraft": only my plane on map) || ( "optview_allies": fog of war) || ( "optview_onlyallies" : Allied only  ) || ( "optview_all" : every visible targets and planes on map allowed by campaign maker : usefull to program JDAM or JSAW - non target units will stay invisible to player )
	["externalViews"] = true,							-- False / true : Vue externe
	["permitCrash"] = true,								-- False / true : Récupération de crash
	["miniHUD"] = false,								-- False / true : Mini HUD
	["cockpitVisualRM"] = true,						-- False / true : Mod reconnaissance Visuel dans le cockoit
	["userMarks"] = true,								-- False / true : autorise les marqueurs sur la vue MAP F10
	["civTraffic"] = "",								-- Traffic civil routier : ( "" : OFF ) || ( "low" : BAS ) || ( "medium" : MOYEN )|| ( "high" : ELEVE )  [MP: recommend: ""]
	["birds"] = 100,										-- Collision volatile (probabilité) ( 0 à 1000 )  [MP: recommend: 0]
	["cockpitStatusBarAllowed"] = false,				-- False / true : Barre d'état cockpit
	["RBDAI"] = true,									-- False / true : Evaluation des dommages au combat
}
				
-- modif Miguel M17 Options F-14B
-- Special option for F-14
AddPropAircraft = {
	["LGB100"] = 6,
	["M61BURST"] = 0,
	["IlsChannel"] = 11,				-- preset ILS channel
	["LGB1"] = 8,
	["KY28Key"] = 1,
	["TacanBand"] = 0,
	["ALE39Loadout"] = 3,
	["UseLAU138"] = true,
	["LGB10"] = 8,
	["INSAlignmentStored"] = true,		-- fast alignment, remember to modify also the value: "startup_time_player" in this file
	["TacanChannel"] = 37,				-- preset TACAN channel
	["LGB1000"] = 1,
}

TargetPointF14 = true 						-- transforms IP, Station and Target points into IP, DP and ST

TargetPointF14_BullsToFP = true				-- assigns the BullsEye position to the NavPoint FP of the F-14
			
-- limit the number of F-14s (in the same Flight as the player) on the CVN to avoid taxiing collisions
limiteNbF14CVN = 4							-- advice 3 max is a good value





















-- 2 ############################################################################################################################################################
-- 2 ############################################################################################################################################################
--The options in this second part are exclusively reserved for the campaign editor. Players must not modify them.
-- 2 ############################################################################################################################################################	
-- 2 ############################################################################################################################################################


Debug = {
	AfficheFailure = false,                        -- affiche les infos Pannes Aléatoires
	AfficheFlight = false,						-- affiche les infos des packages créés dans ATO_FlightPlan
	AfficheSol = false,							-- affiche les infos des cibles encore intactes
	KillGround  = {
		flag = false,				-- Active la destruction aléatoires des cibles, via les options plus bas
		sideGround = "red",			-- le camp où l'on veut détruire les unités
		sideTarget = "blue",		-- les targets de notre camp
		pourcent = 50,				-- pourcentage de chance que l'unité soit détruite (juste l'unité, pas le groupe)
	},
	Generator  = {
		affiche = false,			-- affiche les infos des premiers vols créés dans ATO_Generator
		nb = 200,					-- nb de vol à afficher
	},
	checkTargetName = true,						-- FirsMission Alerte si les noms des targets possede 1 espace en premier ou en dernier
	checkTargetName2Space = true,				-- FirsMission Alerte si les noms des targets possede 2 espaces consécutif			
}


-- modif Miguel M19 RepairGround
-- probabilité de réparation des unités détruites au sol, calculé à chaque tentative de création de mission
-- 2 possibilités de réparation:
--	soit par une valeur individuelle ['probRepair'] propre à chaque cible (cette valeur sera prioritaire sur le 2eme choix)
	-- targetlist = {
	-- ['SA-3 Goa Site Batumi'] = {
				-- ['dead_last'] = 25,
				-- ['alive'] = 70,
				-- ['probRepair'] = 30,		-- en %
				-- ['priority'] = 6,
				-- ['task'] = 'Strike',
-- soit avec une valeur par caterorie RepairSAM RepairAirbase etc
campMod = {
	-- RepairTotallyDestroyed = false,			-- répare (ou pas) les targets totalement détruites
	RepairMinimumDestroyed = 25,			-- ne répare pas si le target.alive est inférieur à
	RepairSAM = 15,							-- en %, Only CampaignMaker please
	RepairAirbase = 12,						-- en %, Only CampaignMaker please
	RepairStation = 8,						-- en %, Only CampaignMaker please
	RepairBridge = 8,						-- en %, Only CampaignMaker please
	Repair = 2,								-- en %, Only CampaignMaker please	
	
	KillTargetValue = 20,					-- en %, si la vie du Target est < 20%, on déclare les survivants mort, pour éviter d'y retourner.
								
	DeltaMn = {								-- minute, décale le temps necessaire lors d'apparition sur CVN, LHA ou FARP
		CVN = 3,
		LHA = 7,
		FARP = 7,
	},
		
	MovedBullseye = { 						-- Miguel21 modification M27 	MovedBullseye
		caucasus = {
			pos = {
				x = -281713,	-- centre du rayon autour de laquelle on s'autorise à placer le nouveau BullsEye ['Senaki-Kolkhi']
				y = 647369,		-- centre du rayon autour de laquelle on s'autorise à placer le nouveau BullsEye ['Senaki-Kolkhi']
			},
			rayon = 200,	-- distance en Km autour de laquelle on peut placer le bullsEye
		},
		persiangulf = {
			pos = {
				x =	64800.714844,	-- Qeshm Island
				y = -33383.481445,	-- Qeshm Island
			},
			rayon = 200,		-- distance en Km autour de laquelle on peut placer le bullsEye
		},
		syria = {
											pos = {
												x =	-22163,	-- Israel Line 974
												y = -11800,	-- Israel Line 974
											},
											rayon = 200,		-- distance en Km autour de laquelle on peut placer le bullsEye
									},		
	},

	WestCallsign = {	
		["Belgium"] = "west",
		["UK"] = "west",
		["Georgia"] = "west",
		["Denmark"] = "west",
		["Israel"] = "west", 
		["Spain"] = "west", 
		["Canada"] = "west", 
		["Norway"] = "west", 
		["USA"] = "west", 
		["Turkey"] = "west",
		["France"] = "west", 
		["The Netherlands"] = "west", 
		["Italy"] = "west", 
		["Australia"] = "west", 
		["South Korea"] = "west", 
		["Croatia"] = "west",
		["USAF Aggressors"] = "west", 
		["Sweden"] = "west", 
		["Iran"] = "west",
		["India"] = "west",
		["Pakistan"] = "west",
		["United Arab Emirates"] = "west",
	},
	
	-- reglage composition Package
	Setting_Generation= {
		["limit_escort"] = 8,												-- (default : 99)(recommended : 8), limit escort number to
	},
	StrikeOnlyWithEscorte = false, 											-- (default : true) strikes are possible with only one escort
}




-- modif Miguel M12 Skill aléatoire

skillWish = {
	["red"] = 50,				-- 1 à 100, valeur ULTRA conseillé :50
	["blue"] = 62,				-- 1 à 100 : valuer ULTRA conseillé : 62
}
			
skillTab = {
	[1] = "Average",				-- don't touch
	[2] = "Good", 					-- don't touch
	[3] = "High",					-- don't touch
	[4] = "Excellent",				-- don't touch
}

-- mod M11 multijoueur
playable_m = {
	["AJS37"] = true,
	["M-2000C"] = true,
	["F-15C"] = true,
	["FA-18C_hornet"] = true,
	["F-5E-3"] = true,
	["UH-1H"] = true,
	["MiG-21Bis"] = true,
	["F-14B"] = true,
	["F-14A-135-GR"] = true,
	["A-10C"] = true,
	["A-10C_2"] = true,
	["AV8BNA"] = true,
	["MiG-29A"] = true,
	["SA342M"] = true,
	["F-16C_50"] = true,
	["Su-27"] = true,
	["Su-25"] = true,				 
}
-- modif Miguel21 M05.b : ajout picture Briefing + pictures Target


pictureBrief = {
				["blue"] = {
							 "FrontlineCaucasus1-old.png",
							 "FrontlineCaucasus2-old.png",
							},
				["red"] = {
							 "FrontlineCaucasus1-old.png",
							 "FrontlineCaucasus2-old.png",
							},
				} 
