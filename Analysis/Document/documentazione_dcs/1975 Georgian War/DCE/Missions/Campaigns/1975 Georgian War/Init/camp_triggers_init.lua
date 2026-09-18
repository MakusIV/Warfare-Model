--Initial campaign triggers (static file, not updated)
--Copied to Status/camp_triggers.lua in first mission and subsequently read and updated there
--Campaign triggers are defined with conditions and actions
-------------------------------------------------------------------------------------------------------

--List of Return functions to build conditions:
--Return.Time()												returns time of day in seconds
--Return.Day()												returns day of month
--Return.Month()											returns month as number
--Return.Year()												returns year as number
--Return.Mission()											returns campaign mission number
--Return.CampFlag(flag-n)									returns value of campaign flag
--Return.AirUnitActive("UnitName")							returned boolean whether the air unit is active			
--Return.AirUnitReady("UnitName")							returns amount of ready aircraft in unit
--Return.AirUnitAlive("UnitName")							returns amount of ready and damaged aircraft in unit
--Return.AirUnitBase("UnitName")							returns the name of the airbase the unit operats from
--Return.AirUnitPlayer("UnitName")							returns boolean whether the air units is playable
--Return.TargetAlive("TargetName")							returns percentage of alive sub elements in target
--Return.UnitDead(unitname)									(ADD) return vehicle/ship units dead (ADD)
--Return.GroupHidden("GroupName")							returns group hidden status
--Return.GroupProbability("GroupName")						returns group spawn probability value between 0 and 1
--Return.ShipGroupInPoly(GroupName, PolyZonesTable)			(ADD) return boolean whether ship group is in polygon (ADD)

--List of Action functions for trigger actions:
--Action.None()
--Action.Text("your briefing text")
--Action.TextPlayMission(arg)																--add trigger text to briefing text of this mission only if it is playable
--Action.SetCampFlag(flag-n, boolean/number)												--
--Action.AddCampFlag(flag-n, number)														--
--Action.AddImage("filname.jpg")															--
--Action.CampaignEnd("win"/"draw"/"loss")													--
--Action.TargetActive("TargetName", boolean)												--
--Action.AirUnitActive("UnitName", boolean)													--
--Action.AirUnitBase("UnitName", "BaseName")												--
--Action.AirUnitPlayer("UnitName", boolean)													--
--Action.AirUnitReinforce("SourceUnitName", "DestinationUnitName", destNumber)				--
--Action.AirUnitRepair()																	--
--Action.GroundUnitRepair()																	-- (ADD) M19.f : Repair Ground
--Action.AddGroundTargetIntel("sideName")													--
--Action.GroupHidden("GroupName", boolean)													--
--Action.GroupProbability("GroupName", number 0-1)											--
--Action.GroupMove(GroupName, ZoneName)														-- (ADD) move vehicle group to refpoint (See the DC_CheckTriggers.lua file for more explanation)
--Action.GroupSlave(GroupName, master, bearing, distance)									-- (ADD)
--Action.ShipMission(GroupName, WPtable, CruiseSpeed, PatrolSpeed, StartTime)				-- (ADD) assign and run a movement mission to a ship group (See the DC_CheckTriggers.lua file for more explanation)
--Action.TemplateActive(TabFile)															-- (ADD) M40 : Template Active GroundGroup moving front (single file : active template) (if tab file: random activation)



--Important notes:
--for condition and action strings: outside with single quotes '', inside with double quotes ""!

camp_triggers = {
	
	----- CAMPAIGN INTRO ----
	["Campaign Briefing"] = {										--Trigger name
		active = true,												--Trigger is active
		once = true,												--Trigger is fired once
		condition = 'true',											--Condition of the trigger to return true or false embedded as string
		action = {													--Trigger action function embedded as string
			[1] = 'Action.Text("After the effective political action of the Minister of the Interior, a group of Georgian nationalists led by the Army Corps General Baaka Kobakhidze, carried out a coup by supporting Georgian military forces and with the political and military support of some western countries coordinated by the USA. On 9 September 1975, Tbilissi government buildings were occupied by Georgian military forces, at the same time the airports of Tbilissi, Soganlug, Vaziani, Kutaisi, Batumi, Kobuleti, Senaki, Sukhumi and Gudauta were occupied by Western coalition and/or Georgian military forces (Georgian War Coalition).")',
			[2] = 'Action.Text("The Georgian War Coalition occupy the whole area of North Ossetia up to Kurta. During this expansion phase, Georgian forces manage to appropriate an important quantity of Russian military equipment, including: Mig-19, Mig-21, Mig-27, SU-17, AN-26 as well as SAM systems of the SA-2, SA-3, SA-6, SA-8, SA-9 with AAA ZSU-23, ZSU-57. ")',
			[3] = 'Action.Text("The goal of the Georgian War Coalition is to exploit the weakness of the Soviet Union to establish control in this important area through important and explicit military action. The decision made by Western countries to participate directly in the military action is based on the security that the conflict will remain localized in the Caucasian area due to the extreme weakness and instability facing the entire Soviet Union.")',
			[4] = 'Action.Text("Against all odds, Russia reacts swiftly and forcefully to the attack by engaging an impressive amount of military air forces in support of the ground operations necessary to restore military control over Georgia. After being relegated to Sakire, the Russian forces present in North Ossetia launch an immediate counterattack that allows them to consolidate their position in the areas of Didmukha, Tskhinvali and Sathiari by rejecting Georgian forces in the areas of Tsveri, Tkviavi and Kaspi.")',
			[5] = 'Action.Text("At this stage of the conflict, the main Russian military air bases are Mineralnye, Nalchik, Beslan and Mozdok where are operative squadrons of Mig-21, Mig-23, Mig-25, Mig-27, Su-17, Su-24, L-39. Maykop and Mineralnye are used by heavy bomber Tu-22, Kransnodar and Nalchik are operative Tu-126 (A-50 :| ) Awacs. In many Russian airbases are operative An-26 for transport. Russian FARP are presents in Nogir, Tskhinvali and Lenigori area, where are operative Mi-8MTV2 and Mi-24 squads.")',
			[6] = 'Action.Text("The main Georgian and Western Coalition military base are Batumi, Kutaisi, Tbilissi, Vaziani where are operative squadron of Mig-19, Mig-21, Mig-27, F-4E, F-5, AJS-37 (Sweden). Batumi airbase are operative heavy bomber B-52 and at Kutaisi airbase are operative some new E-3 Awacs. In many Georgian airbases are operative C-130 and An-26 for transport and KC135 for refuelling. Georgian FARP are presents in Gori, khashuri, Ambrolauri where are operative the 6th and 17th Cavalry with UH-1H and AH-1.")',
			[7] = 'Action.Text("US NAvy has sent the CVN-68 USS Nimitz (T.Roosvelt) and CV-67 USS John F. Kennedy (J.C. Stennis) which operates off the coast of Batumi, and VF 101 (your group) and VF 118/GA are ready for aggressive operation.")',
			[8] = 'Action.Text("The effectiveness of operations depends on obtaining air superiority, of destruction airbases, ground forces and on the integrity of supply asset (supply plant and supply line). Obviously, these assets are sensitive targets for the enemy, so it is very important to defend them and destroy those of the enemy. ")',
			[9] = 'Action.AddImage("Newspaper_FirstNight_blue.jpg", "blue")',
			[10] = 'Action.AddImage("Newspaper_FirstNight_red.jpg", "red")',
		},
	},
	
	
	----- CAMPAIGN END -----
	["Campaign End Victory 1"] = {
		active = true,
		once = true,
		condition = 'GroundTarget["blue"].percent < 40',
		action = {
			[1] = 'Action.CampaignEnd("win")',
			[2] = 'Action.Text("The Allied units deployed to Georgia have successfully destroyed all the targets that they were assigned by US Central Command with the precious help of the French and Swedish fighters. With the complete destruction of the Russian airbases, the air campaign of this war comes to an end. Allied air power has once again proven its effectiveness and decisiveness. Well done.")',
			[3] = 'Action.AddImage("Newspaper_Victory_blue.jpg", "blue")',
			[4] = 'Action.AddImage("Newspaper_Defeat_red.jpg", "red")',
			[5] = 'NoMoreNewspaper = true',
		},
	},
	["Campaign End Victory 2"] = {
		active = true,
		once = true,
		condition = 'Return.AirUnitReady("113.IAP") + Return.AirUnitReady("790.IAP") + Return.AirUnitReady("123.IAP") + Return.AirUnitReady("37.IAP") + Return.AirUnitReady("19.IAP") + Return.AirUnitReady("133.IAP") + Return.AirUnitReady("153.IAP") < 8',
		action = {
			[1] = 'Action.CampaignEnd("win")',
			[2] = 'Action.Text("The Russian Air Force is in ruins. After repeated air strikes and disastrous losses in air-air combat, the Russians are no longer able to produce any sorties or offer any resistance. The NATO now owns complete air superiority. With the disappearance of the air threat, the role of the F-15C Eagle and Mirage 2000C in this war comes to an end. Once again the victorious Eagle has proved to be to leading fighter in the world. Well done.")',
			[3] = 'Action.AddImage("Newspaper_Victory_blue.jpg", "blue")',
			[4] = 'Action.AddImage("Newspaper_Defeat_red.jpg", "red")',
			[5] = 'NoMoreNewspaper = true',
		},
	},

	--[[

	["Campaign End Victory 2 (enemy Fighter + Fighter-Bomber < 10 unit)"] = {
		active = true,
		once = true,
		condition = 'Return.AirUnitReady("790.IAP") + Return.AirUnitReady("113.IAP") + Return.AirUnitReady("123.IAP") + Return.AirUnitReady("948 Squadron") + Return.AirUnitReady("67 Squadron") + Return.AirUnitReady("764.IAP") + Return.AirUnitReady("797.IAP") + Return.AirUnitReady("159.IAP") < 10',
		action = {
			[1] = 'Action.CampaignEnd("win")',
			[2] = 'Action.Text("Syrian coalition fighter planes have been annihilated. After repeated air strikes and disastrous losses in air-air combat (aircraft losses are bigger of 80%), the Syrian coalition is not longer able to produce any sorties or offer any resistance. The The USA and Nato countries now owns complete air superiority. With the disappearance of the air threat, the role of the F-14A Tomcat in this war comes to an end. Once again the victorious Tomcat has proved to be to leading fighter in the world. Well done.")',
			[3] = 'Action.AddImage("Newspaper_Victory_blue.jpg", "blue")',
			[4] = 'Action.AddImage("Newspaper_Defeat_red.jpg", "red")',
			[5] = 'NoMoreNewspaper = true',
		},
	},
	["Campaign End Victory 3 (enemy Attacker + Bomber < 12 unit)"] = {
		active = true,
		once = true,
		condition = 'Return.AirUnitReady("117.IAP") + Return.AirUnitReady("127.IAP") + Return.AirUnitReady("127.IAP") + Return.AirUnitReady("3 Squadron") + Return.AirUnitReady("677 Squadron") + Return.AirUnitReady("368 ShAP")  + Return.AirUnitReady("3 BAP 149th BAA")  + Return.AirUnitReady("402nd Heavy Bomber Aviation Regiment") + Return.AirUnitReady("373 ShAP") + Return.AirUnitReady("4 Guards BAP 132nd BAA") + Return.AirUnitReady("132nd Heavy Bomber Aviation Regiment") + Return.AirUnitReady("637 Squadron") < 12',
		action = {
			[1] = 'Action.CampaignEnd("win")',
			[2] = 'Action.Text("Syrian coalition Attacker and Bomber planes have been annihilated. After repeated air strikes and disastrous losses (aircraft losses are bigger of 80%), the Syrian coalition is not longer able to produce any sorties or offer any resistance. The USA and Nato countries now owns complete ground invasion. With the disappearance of the air threat, the role of the F-14A Tomcat in this war comes to an end. Once again the victorious Tomcat has proved to be to leading fighter in the world. Well done.")',
			[3] = 'Action.AddImage("Newspaper_Victory_blue.jpg", "blue")',
			[4] = 'Action.AddImage("Newspaper_Defeat_red.jpg", "red")',
			[5] = 'NoMoreNewspaper = true',
		},
	},
	["Campaign End Victory 4 (enemy Fighter + Fighter-Bomber < 12 unit and Attacker + Bomber < 15 unit)"] = {
		active = true,
		once = true,
		condition = '( Return.AirUnitReady("790.IAP") + Return.AirUnitReady("113.IAP") + Return.AirUnitReady("123.IAP") + Return.AirUnitReady("948 Squadron") + Return.AirUnitReady("67 Squadron") + Return.AirUnitReady("764.IAP") + Return.AirUnitReady("797.IAP") + Return.AirUnitReady("159.IAP") < 12 ) and ( Return.AirUnitReady("117.IAP") + Return.AirUnitReady("127.IAP") + Return.AirUnitReady("127.IAP") + Return.AirUnitReady("3 Squadron") + Return.AirUnitReady("677 Squadron") + Return.AirUnitReady("368 ShAP")  + Return.AirUnitReady("3 BAP 149th BAA")  + Return.AirUnitReady("402nd Heavy Bomber Aviation Regiment") + Return.AirUnitReady("373 ShAP") + Return.AirUnitReady("4 Guards BAP 132nd BAA") + Return.AirUnitReady("132nd Heavy Bomber Aviation Regiment") + Return.AirUnitReady("637 Squadron") < 15 )',
		action = {
			[1] = 'Action.CampaignEnd("win")',
			[2] = 'Action.Text("Syrian coalition Air Force is in ruins. After repeated air strikes and disastrous losses in air-air combat (aircraft losses are bigger 70% for Fighter and 60% for Bomber), the Syrian coalition is not longer able to offer any resistance. The Usa and Nato countries now owns complete ground invasion. With the disappearance of the air threat, the role of the F-14A Tomcat in this war comes to an end. Once again the victorious Tomcat has proved to be to leading fighter in the world. Well done.")',
			[3] = 'Action.AddImage("Newspaper_Victory_blue.jpg", "blue")',
			[4] = 'Action.AddImage("Newspaper_Defeat_red.jpg", "red")',
			[5] = 'NoMoreNewspaper = true',
		},
	},

	]]
	["Campaign End Victory 3"] = {
		active = true,
		once = true,
		condition = 'Return.TargetAlive("Beslan Airbase") < 2 and Return.TargetAlive("Nalchik Airbase") < 2 and Return.TargetAlive("Mozdok Airbase") < 2 and Return.TargetAlive("Mineralnye-Vody Airbase") < 3',
		action = {
			[1] = 'Action.CampaignEnd("win")',
			[2] = 'Action.Text("The Russian Air Force is in ruins. All their main bases are destroyed, Russians are no longer able to produce any sorties or offer any resistance. The Allied forces now owns complete air superiority. Well done.")',
			[3] = 'Action.AddImage("Newspaper_Victory_blue.jpg", "blue")',
			[4] = 'Action.AddImage("Newspaper_Defeat_red.jpg", "red")',
			[5] = 'NoMoreNewspaper = true',
		},
	},
	["Campaign End Loss"] = {
		active = true,
		once = true,
		condition = 'Return.AirUnitAlive("VF-101") + Return.AirUnitReady("R/VF-101") < 5',
		action = {
			[1] = 'Action.CampaignEnd("loss")',
			[2] = 'Action.Text("Ongoing combat operations have exhausted VF-101 Squadron. Loss rate has reached a level where reinforcements are no longer able to sustain combat operations. With the failure of Allied Air Force to attain air superiority, US Central Command has decided to call of the air campaign against the Russians. Without destroying Russians airbases it seems unlikely that the coalition will be able to win this war.")',
			[3] = 'Action.AddImage("Newspaper_Victory_red.jpg", "red")',
			[4] = 'Action.AddImage("Newspaper_Defeat_blue.jpg", "blue")',
			[5] = 'NoMoreNewspaper = true',
		},
	},
	["Campaign End Loss 2"] = {
		active = true,
		once = true,
		condition = 'Return.TargetAlive("CVN-71 Theodore Roosevelt") == 0',
		action = {
			[1] = 'Action.CampaignEnd("loss")',
			[2] = 'Action.Text("After the CVN-71 Theodore Roosevelt has been hit by air strikes and neutralised, VF-101 Squadron is no longer able to fly. Other US units will have to continue the fight without the VF-101 Squadron support. This is a bitter failure.")',
			[3] = 'Action.AddImage("Newspaper_Victory_red.jpg", "red")',
			[4] = 'Action.AddImage("Newspaper_Defeat_blue.jpg", "blue")',
			[5] = 'NoMoreNewspaper = true',
		},
	},
	["Campaign End Loss 3"] = {
		active = true,
		once = true,
		condition = 'GroundTarget["red"].percent < 50',
		action = {
			[1] = 'Action.CampaignEnd("loss")',
			[2] = 'Action.Text("Russian airforce was able to destroy enough allied forces to decide US Command to ask for a cease fire  and stop any Air missions. This is a bitter failure for the Allies")',
			[3] = 'Action.AddImage("Newspaper_Victory_red.jpg", "red")',
			[4] = 'Action.AddImage("Newspaper_Defeat_blue.jpg", "blue")',
			[5] = 'NoMoreNewspaper = true',
		},
	},
	["Campaign End Loss 4"] = {
		active = true,
		once = true,
		condition = 'Return.AirUnitReady("F7") + Return.AirUnitReady("F9") + Return.AirUnitReady("VMFA-151") + Return.AirUnitReady("GA 7rd AS") + Return.AirUnitReady("VMFA-157") + Return.AirUnitReady("GA 3rd AS") + Return.AirUnitReady("58 TFS") + Return.AirUnitReady("GA 4rd AS") < 8',
		action = {
			[1] = 'Action.CampaignEnd("win")',
			[2] = 'Action.Text("The Russian Air Force is in ruins. After repeated air strikes and disastrous losses in air-air combat, the Russians are no longer able to produce any sorties or offer any resistance. The NATO now owns complete air superiority. With the disappearance of the air threat, the role of the F-15C Eagle and Mirage 2000C in this war comes to an end. Once again the victorious Eagle has proved to be to leading fighter in the world. Well done.")',
			[3] = 'Action.AddImage("Newspaper_Victory_blue.jpg", "blue")',
			[4] = 'Action.AddImage("Newspaper_Defeat_red.jpg", "red")',
			[5] = 'NoMoreNewspaper = true',
		},
	},

	--[[

	["Campaign End Loss 4 (avalaible Fighter + Fighter-Bomber < 10 unit)"] = {
		active = true,
		once = true,
		condition = 'Return.AirUnitReady("111th Squadron Panther") + Return.AirUnitReady("151th Squadron Bronze") + Return.AirUnitReady("56th Operations Group") + Return.AirUnitReady("173rd Fighter Group") + Return.AirUnitReady("F6 Karlsborg") + Return.AirUnitReady("Escadron de Chasse 2/5 Ile-de-France") + Return.AirUnitReady("Escadron de Chasse 1/2 Cigognes") + Return.AirUnitReady("Jagdbombergeschwader 33") + Return.AirUnitReady("154 Gruppo, 6 Stormo") + Return.AirUnitReady("152th Squadron Iron") + Return.AirUnitReady("VF-101") + Return.AirUnitReady("VF-118/GA") < 10',
		action = {
			[1] = 'Action.CampaignEnd("win")',
			[2] = 'Action.Text("The USA Air Force is in ruins. After repeated air strikes and disastrous losses (Fighter losses > 80% ) in air-air combat, USA and Nato Countries are no longer able to produce any sorties or offer any resistance.")',
			[3] = 'Action.AddImage("Newspaper_Victory_blue.jpg", "blue")',
			[4] = 'Action.AddImage("Newspaper_Defeat_red.jpg", "red")',
			[5] = 'NoMoreNewspaper = true',
		},
	},
	["Campaign End Loss 5 (avalaible Attacker + Bomber < 12 unit)"] = {
		active = true,
		once = true,
		condition = 'Return.AirUnitReady("69 BS") + Return.AirUnitReady("4450th Tactical Group") + Return.AirUnitReady("23rd FG") + Return.AirUnitReady("122nd Squadron") + Return.AirUnitReady("4453th Tactical Group") + Return.AirUnitReady("VS-21") < 12',
		action = {
			[1] = 'Action.CampaignEnd("win")',
			[2] = 'Action.Text("The USA Air Force is in ruins. After repeated air strikes and disastrous losses (Attacker and Bomber losses > 80% )in air-air combat, USA and Nato Countries are no longer able to produce any sorties or offer any resistance.")',
			[3] = 'Action.AddImage("Newspaper_Victory_blue.jpg", "blue")',
			[4] = 'Action.AddImage("Newspaper_Defeat_red.jpg", "red")',
			[5] = 'NoMoreNewspaper = true',
		},
	},
	["Campaign End Loss 6 (avalaible Fighter + Fighter-Bomber < 12 unit and Attacker + Bomber < 15 unit)"] = {
		active = true,
		once = true,
		condition = '( Return.AirUnitReady("111th Squadron Panther") + Return.AirUnitReady("151th Squadron Bronze") + Return.AirUnitReady("56th Operations Group") + Return.AirUnitReady("173rd Fighter Group") + Return.AirUnitReady("F6 Karlsborg") + Return.AirUnitReady("Escadron de Chasse 2/5 Ile-de-France") + Return.AirUnitReady("Escadron de Chasse 1/2 Cigognes") + Return.AirUnitReady("Jagdbombergeschwader 33") + Return.AirUnitReady("154 Gruppo, 6 Stormo") + Return.AirUnitReady("152th Squadron Iron") + Return.AirUnitReady("VF-101") + Return.AirUnitReady("VF-118/GA") < 12 ) and ( Return.AirUnitReady("69 BS") + Return.AirUnitReady("4450th Tactical Group") + Return.AirUnitReady("23rd FG") + Return.AirUnitReady("122nd Squadron") + Return.AirUnitReady("4453th Tactical Group") + Return.AirUnitReady("VS-21") + Return.AirUnitReady("VS-22") < 15 )',
		action = {
			[1] = 'Action.CampaignEnd("win")',
			[2] = 'Action.Text("The USA Air Force is in ruins. After repeated air strikes and disastrous losses (Fighter loss > 70% and Attacker-Bomber loss > 60% ) in air-air combat, USA and Nato Countries are no longer able to produce any sorties or offer any resistance.")',
			[3] = 'Action.AddImage("Newspaper_Victory_blue.jpg", "blue")',
			[4] = 'Action.AddImage("Newspaper_Defeat_red.jpg", "red")',
			[5] = 'NoMoreNewspaper = true',
		},
	},
	["Campaign End Loss 7"] = {
		active = true,
		once = true,
		condition = 'Return.TargetAlive("Vaziani Airbase") < 4 and Return.TargetAlive("Tbilisi Airbase") < 8 and Return.TargetAlive("Soganlug Airbase") < 5 and Return.TargetAlive("Kutaisi Airbase") < 10 and Return.TargetAlive("Senaki Airbase") < 12 and Return.TargetAlive("Batumi Airbase") < 7 and Return.TargetAlive("Sukhumi Airbase") < 3',
		action = {
			[1] = 'Action.CampaignEnd("win")',
			[2] = 'Action.Text("The USA and NATO Air Force are in ruins. All ours main bases are destroyed, USA and NATO Countries are not longer able to produce any sorties or offer any resistance. The Russian forces now owns complete air superiority and reconquer their territories.")',
			[3] = 'Action.AddImage("Newspaper_Victory_red.jpg", "red")',
			[4] = 'Action.AddImage("Newspaper_Defeat_blue.jpg", "blue")',
			[5] = 'NoMoreNewspaper = true',
		},
	},

	]]
	["Campaign End Draw"] = {
		active = true,
		once = true,
		condition = 'MissionInstance == 40',
		action = {
			[1] = 'Action.CampaignEnd("draw")',
			[2] = 'Action.Text("The air campaign has seen a sustained period of inactivity. Seemingly unable to complete the destruction of the Russian Air Force and infrastructure, US Central Command has called off all squadrons from offensive operations. We hope negociations with Russians will convince them to stop attacks in Georgia")',
			[3] = 'NoMoreNewspaper = true',
		},
	},

	----- CAMPAIGN SITUATION -----
	["Campaign first destructions"] = {
		active = true,
		once = true,
		condition = 'GroundTarget["red"].percent < 100',
		action = {
			[1] = 'Action.Text("First targets have been destroyed. Keep up the good work")',
		},
	},
	["Campaign 20 percents destructions"] = {
		active = true,
		once = true,
		condition = 'GroundTarget["red"].percent < 80',
		action = {
			[1] = 'Action.Text("Enemy targets have sustained fair damages. Keep up the good work")',
		},
	},
	["Campaign 40 percents destructions"] = {
		active = true,
		once = true,
		condition = 'GroundTarget["red"].percent < 60',
		action = {
			[1] = 'Action.Text("Enemy targets have sustained great damages. Strike missions are really efficient and we will win this war soon")',
		},
	},
	["Campaign 50 percents destructions"] = {
		active = true,
		once = true,
		condition = 'GroundTarget["red"].percent < 50',
		action = {
			[1] = 'Action.Text("More than half of our targets are neutralized. Intelligence think that the enemy will ask for a cease fire soon")',
		},
	},

	----- CARRIER MOVEMENT -----
	["TF-71 Patrol ATest Sea"] = {
		active = true,
		once = true,
		condition = 'Return.Mission() == 1',
		action = 'Action.ShipMission("TF-71", {{"Indy 1-1", "Indy 1-2", "Indy 1-3", "Indy 1-4"}}, 10, 8, nil)',
	},
	["TF-74 Patrol ATest Sea"] = {
		active = true,
		once = true,
		condition = 'Return.Mission() == 1',
		action = 'Action.ShipMission("TF-74", {{"Indy 2-1", "Indy 2-2", "Indy 2-3", "Indy 2-4"}}, 10, 8, nil)',
	},
	["LHA-Group Patrol ATest Sea"] = {
		active = true,
		once = true,
		condition = 'Return.Mission() == 1',
		action = 'Action.ShipMission("LHA-Group", {{"Indy 3-1", "Indy 3-2", "Indy 3-3", "Indy 3-4"}}, 10, 8, nil)',
	},
	
	
	----- CONVOY MOVEMENT -----
	["Russian convoy 1 Patrol ATest Sea"] = {
		active = true,
		once = true,
		condition = 'Return.Mission() == 1',
		action = 'Action.ShipMission("Russian Convoy 1", {{"Convoy 1-1", "Convoy 1-2", "Convoy 1-3", "Convoy 1-4"}}, 8, 5, nil)',
	},
	["Russian convoy 2 Patrol ATest Sea"] = {
		active = true,
		once = true,
		condition = 'Return.Mission() == 1',
		action = 'Action.ShipMission("Russian Convoy 2", {{"Convoy 2-1", "Convoy 2-2", "Convoy 2-3", "Convoy 2-4"}}, 8, 5, nil)',
	},
	["NATO convoy 1 Patrol ATest Sea"] = {
		active = true,
		once = true,
		condition = 'Return.Mission() == 1',
		action = 'Action.ShipMission("NATO Convoy 1", {{"NATO convoy 1-1", "NATO convoy 1-2", "NATO convoy 1-3", "NATO convoy 1-4"}}, 8, 5, nil)',
	},
	
	
	----- AIRBASE STRIKES -----
	["Gudauta Airbase Disabled"] = {
		active = true,
		condition = 'Return.TargetAlive("Gudauta Airbase") < 10',
		action = {
			[1] = 'db_airbases["Gudauta"].inactive = true',
		}
	},
	["Gudauta Airbase Disabled Text"] = {
		active = true,
		once = false,
		condition = 'Return.TargetAlive("Gudauta Airbase") < 10',
		action = {
			[1] = 'Action.Text("After the facilities at Gudauta Airbase have been hit by air strikes, air operations at this base came to a complete stop. Intelligence believes that due to the heavy damage inflicted, the base is no longer ably to produce any aviation sorties.")',
		}
	},
	["Batumi Airbase Disabled"] = {
		active = true,
		condition = 'Return.TargetAlive("Batumi Airbase") < 6',
		action = {
			[1] = 'db_airbases["Batumi"].inactive = true',
		}
	},
	["Batumi Airbase Disabled Text"] = {
		active = true,
		once = false,
		condition = 'Return.TargetAlive("Batumi Airbase") < 6',
		action = {
			[1] = 'Action.Text("After the facilities at Batumi Airbase have been hit by air strikes, air operations at this base came to a complete stop. Intelligence believes that due to the heavy damage inflicted, the base is no longer ably to produce any aviation sorties.")',
		}
	},
	["Kobuleti Airbase Disabled"] = {
		active = true,
		condition = 'Return.TargetAlive("Kobuleti Airbase") < 11',
		action = {
			[1] = 'db_airbases["Kobuleti"].inactive = true',
		}
	},
	["Kobuleti Airbase Disabled Text"] = {
		active = true,
		once = false,
		condition = 'Return.TargetAlive("Kobuleti Airbase") < 11',
		action = {
			[1] = 'Action.Text("After the facilities at Kobuleti Airbase have been hit by air strikes, air operations at this base came to a complete stop. Intelligence believes that due to the heavy damage inflicted, the base is no longer ably to produce any aviation sorties.")',
		}
	},
	["Senaki Airbase Disabled"] = {
		active = true,
		condition = 'Return.TargetAlive("Senaki Airbase") < 12',
		action = {
			[1] = 'db_airbases["Senaki-Kolkhi"].inactive = true',
		}
	},
	["Senaki Airbase Disabled Text"] = {
		active = true,
		once = false,
		condition = 'Return.TargetAlive("Senaki Airbase") < 12',
		action = {
			[1] = 'Action.Text("After the facilities at Senaki-Kolkhi Airbase have been hit by air strikes, air operations at this base came to a complete stop. Intelligence believes that due to the heavy damage inflicted, the base is no longer ably to produce any aviation sorties.")',
		}
	},	
	["Kutaisi Airbase Disabled"] = {
		active = true,
		condition = 'Return.TargetAlive("Kutaisi Airbase") < 11',
		action = {
			[1] = 'db_airbases["Kutaisi"].inactive = true',
		}
	},
	["Kutaisi Airbase Disabled Text"] = {
		active = true,
		once = false,
		condition = 'Return.TargetAlive("Kutaisi Airbase") < 11',
		action = {
			[1] = 'Action.Text("The infrastructure at Kutaisi Airbase has been destroyed by air strikes. Flying operations at this base have ceased completely and are unlikely to resume. This will ease our efforts to hit other targets in the Kutaisi Country area.")',
		}
	},
	["Tbilissi Airbase Disabled"] = {
		active = true,
		condition = 'Return.TargetAlive("Tbilissi Airbase") < 7',
		action = {
			[1] = 'db_airbases["Tbilissi-Lochini"].inactive = true',
		}
	},
	["Tbilissi Airbase Disabled Text"] = {
		active = true,
		once = false,
		condition = 'Return.TargetAlive("Tbilissi Airbase") < 7',
		action = {
			[1] = 'Action.Text("The infrastructure at Tbilissi-Lochini Airbase has been destroyed by air strikes. Flying operations at this base have ceased completely and are unlikely to resume. This will ease our efforts to hit other targets in the Kutaisi Country area.")',
		}
	},	
	["Sukhumi Airbase Disabled"] = {
		active = true,
		condition = 'Return.TargetAlive("Sukhumi Airbase") < 4 and Return.TargetAlive("Sukhumi Airbase Strategics") < 5',
		action = {
			[1] = 'db_airbases["Sukhumi"].inactive = true',
		}
	},
	["Sukhumi Airbase Disabled Text"] = {
		active = true,
		once = true,
		condition = 'Return.TargetAlive("Sukhumi Airbase") < 4 and Return.TargetAlive("Sukhumi Airbase Strategics") < 5',
		action = {
			[1] = 'Action.Text("Recent air strikes have destroyed enemy ground elements running operations at Sukhumi Airbase. Without their ground support, any remaining aircraft at the airstrip will no longer be able to launch on sorties.")',
		}
	},
	["Beslan Airbase Disabled"] = {
		active = true,
		condition = 'Return.TargetAlive("Beslan Airbase") < 2',
		action = {
			[1] = 'db_airbases["Beslan"].inactive = true',
		}
	},
	["Beslan Airbase Disabled Text"] = {
		active = true,
		once = true,
		condition = 'Return.TargetAlive("Beslan Airbase") < 2',
		action = {
			[1] = 'Action.Text("After the facilities at Beslan Airbase have been hit by air strikes, air operations at this base came to a complete stop. Intelligence believes that due to the heavy damage inflicted, the base is no longer ably to produce any aviation sorties.")',
		--[[		[2] = 'Action.AddImage("BDA_Beatty.jpg")', ]]--  ---A changer
		}
	},
	["Nalchik Airbase Disabled"] = {
		active = true,
		condition = 'Return.TargetAlive("Nalchik Airbase") < 2',
		action = {
			[1] = 'db_airbases["Nalchik"].inactive = true',
		}
	},
	["Nalchik Airbase Disabled Text"] = {
		active = true,
		once = true,
		condition = 'Return.TargetAlive("Nalchik Airbase") < 2',
		action = {
			[1] = 'Action.Text("The infrastructure at Nalchik Airbase has been destroyed by air strikes. Flying operations at this base have ceased completely and are unlikely to resume. This will ease our efforts to hit other targets in the Nalchik Country area.")',
		--[[		[2] = 'Action.AddImage("BDA_Lincoln.jpg")', ]]--  ---A changer
		}
	},
	["Mozdok Airbase Disabled"] = {
		active = true,
		condition = 'Return.TargetAlive("Mozdok Airbase") < 2',
		action = {
			[1] = 'db_airbases["Mozdok"].inactive = true',
		}
	},
	["Mozdok Airbase Disabled Text"] = {
		active = true,
		once = true,
		condition = 'Return.TargetAlive("Mozdok Airbase") < 2',
		action = {
			[1] = 'Action.Text("Recent air strikes have destroyed enemy ground elements running operations at Mozdok Airbase. Without their ground support, any remaining aircraft at the airstrip will no longer be able to launch on sorties.")',
		}
	},
	["Mineralnye Vody Airbase Disabled"] = {
		active = true,
		condition = 'Return.TargetAlive("Mineralnye-Vody Airbase") < 3',
		action = {
			[1] = 'db_airbases["Mineralnye-Vody"].inactive = true',
		}
	},
	["Mineralnye Vody Airbase Disable Text"] = {
		active = true,
		once = true,
		condition = 'Return.TargetAlive("Mineralnye-Vody Airbase") < 3',
		action = {
			[1] = 'Action.Text("Thanks to the destruction of the fuel and ammunition stocks at Mineralnye Vody Airbase, air operations at that base have come to a complete halt. Intelligence estimates that interceptors at Mineralnye Vody Airbase no longer pose a threat to allied strike aircraft. This will considerably ease our access to targets in the enemy rear area.")',
		--[[		[2] = 'Action.AddImage("BDA_Creech.jpg")', ]]-- ---A changer
		}
	},
	["Maykop-Khanskaya Airbase Disabled"] = {
		active = true,
		condition = 'Return.TargetAlive("Maykop-Khanskaya Airbase") < 2',
		action = {
			[1] = 'db_airbases["Maykop-Khanskaya"].inactive = true',
		}
	},
	["Maykop-Khanskaya Airbase Disabled Text"] = {
		active = true,
		once = true,
		condition = 'Return.TargetAlive("Maykop-Khanskaya Airbase") < 2',
		action = {
			[1] = 'Action.Text("Recent air strikes have destroyed enemy ground elements running operations at Maykop-Khanskaya Airbase. Without their ground support, any remaining aircraft at the airstrip will no longer be able to launch on sorties.")',
		}
	},
	["CVN-74 John C. Stennis sunk"] = {
		active = true,
		condition = 'Return.TargetAlive("CVN-74 John C. Stennis") == 0',
		action = {
			[1] = 'db_airbases["CVN-74 John C. Stennis"].inactive = true',
			[2] = 'Action.Text("After the CVN-74 John C. Stennis has been hit by air strikes and sunk, its Navy Squadrons are no longer able to fly. Most of its planes are deep into the sea and it will need a long time to restore this unit s capabilities")',			
		}
	},
	["CVN-71 Theodore Roosevelt Sunk"] = {
		active = true,
		once = true,
		condition = 'Return.UnitDead("CVN-71 Theodore Roosevelt")',
		action = {
			[1] = 'db_airbases["CVN-71 Theodore Roosevelt"].inactive = true',
			[2] = 'Action.Text("CVN-71 Theodore Roosevelt has been lost, the exact cause of her sinking is still somewhat unclear at the moment. Despite her evacuation being orderly and escorts of the Battle Group picking up many survivors, losses are expected to be very high. Search and rescue operations are still ongoing. It s a difficult time for the US Navy.")',
			-- [3] = 'Action.AddImage("Newspaper_Victory_red.jpg", "red")',
			-- [4] = 'Action.AddImage("Newspaper_Defeat_blue.jpg", "blue")',
			-- [5] = 'NoMoreNewspaper = true',
		}	
	},
	["LHA_Tarawa Sunk"] = {
		active = true,
		once = true,
		condition = 'Return.UnitDead("LHA_Tarawa")',
		action = {
			[1] = 'db_airbases["LHA_Tarawa"].inactive = true',
			[2] = 'Action.Text("LHA_Tarawa has been lost, the exact cause of her sinking is still somewhat unclear at the moment. Despite her evacuation being orderly and escorts of the Battle Group picking up many survivors, losses are expected to be very high. Search and rescue operations are still ongoing. It s a difficult time for the US Navy.")',
			-- [3] = 'Action.AddImage("Newspaper_Victory_red.jpg", "red")',
			-- [4] = 'Action.AddImage("Newspaper_Defeat_blue.jpg", "blue")',
			-- [5] = 'NoMoreNewspaper = true',
		}	
	},
	
	----- RED CAP -----
	["CAP After EWR Destroyed"] = {
		active = true,
		once = true,
		condition = 'Return.TargetAlive("102 EWR Site") == 0 and Return.TargetAlive("103 EWR Site") == 0 and Return.TargetAlive("101 EWR Site") == 0 and Return.AirUnitAlive("2457 SDRLO") == 0',
		action = {
			[1] = 'Action.TargetActive("CAP Beslan", true)',
			[2] = 'Action.TargetActive("CAP Mozdok", true)',
			[3] = 'Action.TargetActive("CAP Nalchik", true)',
			[4] = 'Action.TargetActive("CAP Mineralnye-Vody", true)',
			[5] = 'Action.TargetActive("CAP Center", true)',
			[6] = 'Action.TargetActive("Mozdok Alert 200 Km", false)',
			[7] = 'Action.TargetActive("Mozdok Alert 120 Km", false)',
			[8] = 'Action.TargetActive("Nalchik Alert 200 Km", false)',
			[9] = 'Action.TargetActive("Mineralnye-Vody Alert 280 Km", false)',
			[10] = 'Action.TargetActive("Beslan Alert 120 Km", false)',
			[11] = 'Action.TargetActive("Mineralnye-Vody Alert 200 Km", false)',
			[12] = 'Action.TargetActive("Nalchik Alert 100 Km", false)',
			[13] = 'Action.Text("With the recent destruction of all Early Warning Radar sites in the operations area, and Russians AWACS squadron being anihilated, the ability of the enemy to launch interceptors against our strike packages was severely degraded. Intelligence expects that the enemy will increasingly depend on Combat Air Patrols to compensate, though without the support of ground controllers these are estimated to be of limited effectiveness.")',
		},
	},		
	
	----- REPAIR AND REINFORCEMENTS -----
	["GroundUnitRepair"] = {
		active = true,
		condition = 'true',
		action = 'Action.GroundUnitRepair()',
	},
	["Repair"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitRepair()',
	},
	-- blue reinforcement
	["Reinforce VMFA-151"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/VMFA-151", "VMFA-151", 4)',
	},	
	["Reinforce VMFA-157"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/VMFA-157", "VMFA-157", 6)',
	},
	["Reinforce 315th Air Division"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/315th Air Division", "315th Air Division", 4)',
	},	
	["Reinforce 171 ARW"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/171 ARW", "171 ARW", 4)',
	},
	["Reinforce GA 3rd AS"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/GA 3rd AS", "GA 3rd AS", 8)',
	},	
	["Reinforce GA 4rd AS"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/GA 4rd AS", "GA 4rd AS", 8)',
	},	
	["Reinforce 58 TFS"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/58 TFS", "58 TFS", 8)',
	},
	["Reinforce BA 113"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/BA 113", "BA 113", 8)',
	},	
	["Reinforce GA 7rd AS"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/GA 7rd AS", "GA 7rd AS", 8)',
	},	
	["Reinforce 801 ARS"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/801 ARS", "801 ARS", 2)',
	},
	["Reinforce GA 5rd TS"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/GA 5rd TS", "GA 5rd TS", 1)',
	},
	["Reinforce F9"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/F9", "F9", 8)',
	},
	["Reinforce 174 ARW"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/174 ARW", "174 ARW", 4)',
	},
	["Reinforce VMFA-159"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/VMFA-159", "VMFA-159", 4)',
	},
	["Reinforce F7"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/F7", "F7", 8)',
	},
	["Reinforce VF-101"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/VF-101", "VF-101", 8)',
	},
	["Reinforce VAW-125"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/VAW-125", "VAW-125", 2)',
	},
	["Reinforce VS-27"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/VS-27", "VS-27", 2)',
	},
	["Reinforce VS-21"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/VS-21", "VS-21", 8)',
	},
	["Reinforce VF-118/GA"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/VF-118/GA", "VF-118/GA", 8)',
	},
	["Reinforce VS-22"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/VS-22", "VS-22", 8)',
	},
	["Reinforce 17th Cavalry"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/17th Cavalry", "17th Cavalry", 6)',
	},
	["Reinforce 6th Cvy"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/6th Cavalry", "6th Cavalry", 6)',
	},
	["Reinforce GAH 2rd"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/GAH 2rd", "GAH 2rd", 6)',
	},
	["Reinforce 69 BS"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/69 BS", "69 BS", 2)',
	},
	["Reinforce 54 TFS"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/54 TFS", "54 TFS", 8)',
	},		
	
	--red reinforcement
	["Reinforce 117.IAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/117.IAP", "117.IAP", 8)',
	},
	["Reinforce 113.IAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/113.IAP", "113.IAP", 8)',
	},
	["Reinforce 37.IAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/37.IAP", "37.IAP", 8)',
	},
	["Reinforce 127.IAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/127.IAP", "127.IAP", 8)',
	},	
	["Reinforce 123.IAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/123.IAP", "123.IAP", 8)',
	},	
	["Reinforce 115AS.IAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/115AS.IAP", "115AS.IAP", 8)',
	},	
	["Reinforce 19.IAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/19.IAP", "19.IAP", 8)',
	},
	["Reinforce 107.IAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/107.IAP", "107.IAP", 8)',
	},	
	["Reinforce 111AS.IAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/111AS.IAP", "111AS.IAP", 8)',
	},
	["Reinforce 13.OSAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/13.OSAP", "13.OSAP", 2)',
	},	
	["Reinforce 41.IAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/41.IAP", "41.IAP", 8)',
	},
	["Reinforce 133.IAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/133.IAP", "133.IAP", 8)',
	},		
	["Reinforce 135.IAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/135.IAP", "135.IAP", 8)',
	},
	["Reinforce 29.OSAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/29.OSAP", "29.OSAP", 2)',
	},	
	["Reinforce 153.IAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/153.IAP", "153.IAP", 8)',
	},
	["Reinforce 61.IAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/61.IAP", "61.IAP", 8)',
	},
	["Reinforce 81.IAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/81.IAP", "81.IAP", 8)',
	},	
	["Reinforce 27.OSAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/27.OSAP", "27.OSAP", 2)',
	},
	["Reinforce 115.IAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/115.IAP", "115.IAP", 8)',
	},	
	["Reinforce 23.OSAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/23.OSAP", "23.OSAP", 2)',
	},	
	["Reinforce 25.OSAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/25.OSAP", "25.OSAP", 2)',
	},
	["Reinforce 159.IAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/159.IAP", "159.IAP", 8)',
	},
	["Reinforce 1st GHR"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/1st GHR", "1st GHR", 6)',
	},	
	["Reinforce 2nd GHR"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/2nd GHR", "2nd GHR", 6)',
	},	
	["Reinforce 13th GHR"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/13th GHR", "13th GHR", 6)',
	},
	

	
	----- AVIATION UNIT STATUS -----
	["VF-101 Alive 75%"] = {-- aircraft=16+30 = 46 --> 75% = 40, 40% = 23,  25% = 15
		active = true,
		once = true,
		condition = 'Return.AirUnitAlive("VF-101") + Return.AirUnitReady("R/VF-101") < 34',
		action = 'Action.Text("Aircraft strength of the VF-101 Squadron equiped with F-14A-135-GR has fallen below 75%.")',
	},
	["VF-101 Alive 50%"] = {
		active = true,
		once = true,
		condition = 'Return.AirUnitAlive("VF-101") + Return.AirUnitReady("R/VF-101") < 23',
		action = 'Action.Text("Aircraft strength of the VF-101 Squadron equiped with F-14A-135-GR has fallen below 50%. If losses continue at the present rate, the combat capability of the squadron is in jeopardy.")',
	},
	["VF-101 Alive 25%"] = {
		active = true,
		once = true,
		condition = 'Return.AirUnitAlive("VF-101") + Return.AirUnitReady("R/VF-101") < 12',
		action = 'Action.Text("Aircraft strength of the VF-101 Squadron equiped with F-14A-135-GR has fallen below 25%. The number of available airframes is critically low. The squadron is short of destruction.")',
	},
	
	
	---- GROUND TARGET STATUS ---
	["Blue Ground Target Briefing Intel"] = {
		active = true,
		condition = 'true',
		action = 'Action.AddGroundTargetIntel("blue")',
	},
	["Red Ground Target Briefing Intel"] = {
		active = true,
		condition = 'true',
		action = 'Action.AddGroundTargetIntel("red")',
	},

	--[[
	--
	--

	--------------TARGETS LATE ACTIVATIONS	----------------------------
	
	["Scud launcher 1 Activation"] = {
		active = true,
		once = true,
		condition = 'Return.Mission() > 4',
		action = {
			[1] = 'Action.TargetActive("Scud 1",true)',
			[2] = 'Action.Text("A Scud launcher has been detected on the coastline far north of Bandar e Jask.")',
			[3] = 'Action.Text("Un lanceur Scud a été détecté le long de la côte loin au nord de Bandar e Jask.")',	
		}
	},
	["Scud launcher 2 Activation"] = {
		active = true,
		once = true,
		condition = 'Return.Mission() > 5',
		action = {
			[1] = 'Action.TargetActive("Scud 2",true)',
			[2] = 'Action.Text("A Scud launcher has been detected on Abu Musa Island.")',
			[3] = 'Action.Text("Un lanceur Scud a été détecté sur l île de Abu Musa.")',	
		}
	},
	["Scud launcher 3 Activation"] = {
		active = true,
		once = true,
		condition = 'Return.Mission() > 7',
		action = {
			[1] = 'Action.TargetActive("Scud 3",true)',
			[2] = 'Action.Text("A new Scud launcher has been detected on Abu Musa Island.")',
			[3] = 'Action.Text("Un autre lanceur Scud a été détecté sur l île de Abu Musa.")',	
		}
	},



	]]
}