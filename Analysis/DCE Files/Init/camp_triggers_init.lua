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
			[1] = 'Action.Text("In a desperate try to free from russian tyrany, Georgia patriots tried to bring down the governement. This action was reprimed with violence by russian troops and loyal Georgian forces. Many civilians were killed and tortured to prevent any other freedom movements. United Nations were not able to stop russians violences and the United States of America decided to do something to convince Russia to stop this. Turkish government was not ready to open his bases to US attack planes and only one Navy Task Force can be sent near Georgian coasts to show Russia they have to stop violence in Georgia.")',
			[2] = 'Action.Text("The US Navy has sent considerable forces near Georgia. The Task Force 71 is leaded by the CVN-71 Theodore Roosevelt. At the forefront are the F/A-18C of the VFA-106 and VMFA-312 who are tasked to attack Russian air defenses, Airbases and many strategical targets in Georgia like bridges train stations and Harbors. Air superiority and strikers escort will be the mission of the VF-101 and VF-143 with their legendary F-14A Tomcats. E-2D will provide AWACS constant cover. Together these squadrons form a powerful and mighty force.")',
			[3] = 'Action.Text("The Russian Air Force is flying a mix of MiG-21, MiG-25 and MiG-23 fighters directed by ground based early warning radar. Air bases and target complexes of high value are protected by a variety of surface-air missile systems, such as the Sa-2 Guindeline, SA-6 Gainful, the SA-8 Gecko and the SA-3 Goa, as well as short-range IR-SAMs and AAA. Our goal will be to gain air superiority over Georgia by neutralizing main bases in the country and destroying SAM systems. Russia Homeland is strictly forbidden. You are not allowed to attack ground target in Russia but air to air combat can be initiated near and over Russia. Our Task Force can be targeted by Russians anti-ship fleet : Su-24, Tu-22 and TU-142 with dangerous missiles")',
			[4] = 'Action.AddImage("Newspaper_FirstNight_blue.jpg", "blue")',
			[5] = 'Action.AddImage("Newspaper_FirstNight_red.jpg", "red")',
		},
	},
	
----- CAMPAIGN SITUATION -----
	["Campaign first destructions"] = {
		active = true,
		once = true,
		condition = 'GroundTarget["blue"].percent < 100',
		action = {
			[1] = 'Action.Text("First targets have been destroyed. Keep up the good work")',
		},
	},
	["Campaign 20 percents destructions"] = {
		active = true,
		once = true,
		condition = 'GroundTarget["blue"].percent < 80',
		action = {
			[1] = 'Action.Text("Enemy targets have sustained fair damages. Keep up the good work")',
		},
	},
	["Campaign 40 percents destructions"] = {
		active = true,
		once = true,
		condition = 'GroundTarget["blue"].percent < 60',
		action = {
			[1] = 'Action.Text("Enemy targets have sustained great damages. Strike missions are really efficient and we will win this war soon")',
		},
	},
	["Campaign 50 percents destructions"] = {
		active = true,
		once = true,
		condition = 'GroundTarget["blue"].percent < 50',
		action = {
			[1] = 'Action.Text("More than half of our targets are neutralized. Intelligence think that the enemy will ask for a cease fire soon")',
		},
	},

	
	----- CAMPAIGN END -----
	["Campaign End Victory 1"] = {
		active = true,
		once = false,
		condition = 'GroundTarget["blue"].percent < 45',
		action = {
			[1] = 'Action.CampaignEnd("win")',
			[2] = 'Action.Text("The US Navy units deployed off the coasts of Georgia have successfully destroyed all the targets that they were assigned by US Central Command. With the complete destruction of the Russian airforce over Georgia, the air campaign of this war comes to an end. Russian will soon begin to withdraw from Georgia. Well done.")',
			[3] = 'Action.AddImage("Newspaper_Victory_blue.jpg", "blue")',
			[4] = 'Action.AddImage("Newspaper_Defeat_red.jpg", "red")',
			[5] = 'NoMoreNewspaper = true',
		},
	},
	["Campaign End Victory 2"] = {
		active = true,
		once = false,
		condition = 'Return.AirUnitReady("19.IAP") + Return.AirUnitReady("31.IAP") + Return.AirUnitReady("28.IAP") + Return.AirUnitReady("368.ShAP") + Return.AirUnitReady("3.IAP") + Return.AirUnitReady("559.BAP") + Return.AirUnitReady("174.IAP-PVO") + Return.AirUnitReady("52.TBAP") + Return.AirUnitReady("959.BAP") + Return.AirUnitReady("79.TBAP") < 4',
		action = {
			[1] = 'Action.CampaignEnd("win")',
			[2] = 'Action.Text("Russian forces are completly defeated. After repeated air strikes and disastrous losses in air-air combat, the russians are no longer able to produce any sorties or offer any resistance. The US Navy now owns complete air superiority. With the disappearance of the air threat, we hope that russians will decide to leave Georgia quickly. Well done.")',
			[3] = 'Action.AddImage("Newspaper_Victory_blue.jpg", "blue")',
			[4] = 'Action.AddImage("Newspaper_Defeat_red.jpg", "red")',
			[5] = 'NoMoreNewspaper = true',
		},
	},
	["Campaign End Loss"] = {
		active = true,
		once = false,
		condition = 'Return.AirUnitAlive("VF-101") + Return.AirUnitReady("R/VF-101") < 5',
		action = {
			[1] = 'Action.CampaignEnd("loss")',
			[2] = 'Action.Text("Ongoing combat operations have exhausted VF-101. Loss rate has reached a level where reinforcements are no longer able to sustain combat operations. With the failure of US Navy Air Force to attain air superiority, US Central Command has decided to call of the air campaign against the Russians. They will be abble to stay in Georgia and our diplomatic power in the world is really weaked by this defeat.")',
			[3] = 'Action.AddImage("Newspaper_Victory_red.jpg", "red")',
			[4] = 'Action.AddImage("Newspaper_Defeat_blue.jpg", "blue")',
			[5] = 'NoMoreNewspaper = true',
		},
	},
	["Campaign End Loss 2"] = {
		active = true,
		once = false,
		condition = 'Return.TargetAlive("CVN-71 Theodore Roosevelt") == 0',
		action = {
			[1] = 'Action.CampaignEnd("loss")',
			[2] = 'Action.Text("After the CVN-71 Theodore Roosevelt has been hit by air strikes and sunk, VF-101 is no longer able to fly. Most of its planes are deep into the Caucasian waters and it will need a long time to restore this unit s capabilities. Other US Navy units will have to continue the fight without the VF-101 support. This is a bitter failure for the Navy")',
			[3] = 'Action.AddImage("Newspaper_Victory_red.jpg", "red")',
			[4] = 'Action.AddImage("Newspaper_Defeat_blue.jpg", "blue")',
			[5] = 'NoMoreNewspaper = true',
		},
	},	
	["Campaign End Draw"] = {
		active = true,
		once = true,
		condition = 'MissionInstance == 40',
		action = {
			[1] = 'Action.CampaignEnd("draw")',
			[2] = 'Action.Text("The air campaign has seen a sustained period of inactivity. Seemingly unable to complete the destruction of the Russian Air Force and infrastructure, US Central Command has called off all squadrons from offensive operations. We hope negociations with Russians will convince them to withdraw from Georgia")',
			[3] = 'NoMoreNewspaper = true',
		},
	},
	["CVN-71 Theodore Roosevelt Sunk"] = {
		active = true,
		once = true,
		condition = 'Return.UnitDead("CVN-71 Theodore Roosevelt")',
		action = {
			[1] = 'Action.CampaignEnd("loss")',
			[2] = 'Action.Text("CVN-71 Theodore Roosevelt has been lost, the exact cause of her sinking is still somewhat unclear at the moment. Despite her evacuation being orderly and escorts of the Battle Group picking up many survivors, losses are expected to be very high. Search and rescue operations are still ongoing. All combat operations against Russian forces have been put on hold until further notice.")',
			[3] = 'Action.AddImage("Newspaper_Victory_red.jpg", "red")',
			[4] = 'Action.AddImage("Newspaper_Defeat_blue.jpg", "blue")',
			[5] = 'NoMoreNewspaper = true',
		}	
	},
	["CVN-71 Theodore Roosevelt Damaged Light"] = {
		active = true,
		once = true,
		condition = 'camp.ShipHealth and camp.ShipHealth["CVN-71 Theodore Roosevelt"] and camp.ShipHealth["CVN-71 Theodore Roosevelt"] < 100 and camp.ShipHealth["CVN-71 Theodore Roosevelt"] >= 66',
		action = {
			[1] = 'Action.Text("CVN-71 Theodore Roosevelt has sustained light damage under circumstances still somewhat unclear at the moment. Flight operations continue as scheduled.")',
		}	
	},
	["CVN-71 Theodore Roosevelt Damaged Moderate"] = {
		active = true,
		once = true,
		condition = 'camp.ShipHealth and camp.ShipHealth["CVN-71 Theodore Roosevelt"] and camp.ShipHealth["CVN-71 Theodore Roosevelt"] < 66 and camp.ShipHealth["CVN-71 Theodore Roosevelt"] >= 33',
		action = {
			[1] = 'Action.CampaignEnd("loss")',
			[2] = 'Action.Text("CVN-71 Theodore Roosevelt has sustained substantial damage under circumstances still somewhat unclear at the moment. Unable to continue flight operations, the carrier is retreating under own power for repairs. All combat operations against Russian forces have been put on hold until further notice.")',
			[3] = 'Action.AddImage("Newspaper_Victory_red.jpg", "red")',
			[4] = 'Action.AddImage("Newspaper_Defeat_blue.jpg", "blue")',
			[5] = 'NoMoreNewspaper = true',
		}	
	},
	["CVN-71 Theodore Roosevelt Damaged Heavy"] = {
		active = true,
		once = true,
		condition = 'camp.ShipHealth and camp.ShipHealth["CVN-71 Theodore Roosevelt"] and camp.ShipHealth["CVN-71 Theodore Roosevelt"] < 33 and camp.ShipHealth["CVN-71 Theodore Roosevelt"] > 0',
		action = {
			[1] = 'Action.CampaignEnd("loss")',
			[2] = 'Action.Text("CVN-71 Theodore Roosevelt has sustained heavy damage under circumstances still somewhat unclear at the moment. After a valiant damage control effort by its crew and support from other ships of Task Force 70, the complete loss of the carrier could be averted. Being taken under tow by its escorts, CVN-71 Theodore Roosevelt is on the way to friendly harbor for emergency repairs before returning to the United States. All combat operations against Russian forces have been put on hold until further notice.")',
			[3] = 'Action.AddImage("Newspaper_Victory_red.jpg", "red")',
			[4] = 'Action.AddImage("Newspaper_Defeat_blue.jpg", "blue")',
			[5] = 'NoMoreNewspaper = true',
		}	
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
	["LHA-Group Far from Georgian Coasts"] = {
		active = true,
		once = true,
		condition = 'Return.Mission() == 1',
		action = {
			[1] = 'Action.ShipMission("LHA-Group", {{"Indy 3-1", "Indy 3-2", "Indy 3-3", "Indy 3-4"}}, 10, 8, nil)',
		}	
	},
	["LHA Group Close to Georgian Coasts"] = {
		active = true,
		once = true,
		condition = 'Return.AirUnitReady("368.ShAP") + Return.AirUnitReady("559.BAP") + Return.AirUnitReady("52.TBAP") + Return.AirUnitReady("959.BAP") + Return.AirUnitReady("79.TBAP") < 10',
		action = {
			[1] = 'Action.ShipMission("LHA-Group", {{"Indy 3-5", "Indy 3-6", "Indy 3-7", "Indy 3-8""}}, 10, 8, nil)',
			[2] = 'Action.AirUnitActive("VMA 311", true)',
			[3] = 'Action.Text("After the estimated near destruction of all the enemy anti-ship air squadrons, LHA Group is allowed to move closer of Georgian coast and VMA-311 will begin its air to ground campaign.")',
		}	
	},

	----- CONVOY MOVEMENT -----
	["Cargo convoy 1 Patrol ATest Sea"] = {
		active = true,
		once = true,
		condition = 'Return.Mission() == 1',
		action = 'Action.ShipMission("Cargo convoy 1", {{"Ships 1-1", "Ships 1-2", "Ships 1-3", "Ships 1-4"}}, 8, 5, nil)',
	},
	["Cargo convoy 2 Patrol ATest Sea"] = {
		active = true,
		once = true,
		condition = 'Return.Mission() == 1',
		action = 'Action.ShipMission("Cargo convoy 2", {{"Ships 1-5", "Ships 1-4", "Ships 1-3", "Ships 1-2"}}, 8, 5, nil)',
	},


	----- UNIT DESACTIVATION -----
	-- ["Unit Desactivate B-52H and B-1B"] = {
		-- active = true,
		-- once = true,
		-- condition = 'Return.Mission() >= 10',
		-- action = {
			-- [1] = 'Action.AirUnitActive("96 BW", false)',
			-- [2] = 'Action.AirUnitActive("69 BS", false)',
			-- [3] = 'Action.Text("After intensive flights against Russians SAM sites, B-52H from 96 BS and B-1B from 69 BS have reduced significantly SAM sites effectiveness. They have to stop their missions but it should be easier for TF-74 to attack strategics targets in Georgia")',
			-- [4] = 'Action.AddImage("Newspaper_Phantom.jpg")',
		-- },
	-- },	

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
		condition = 'Return.TargetAlive("Tbilisi Airbase") < 7',
		action = {
			[1] = 'db_airbases["Tbilissi-Lochini"].inactive = true',
		}
	},
	["Tbilissi Airbase Disabled Text"] = {
		active = true,
		once = false,
		condition = 'Return.TargetAlive("Tbilisi Airbase") < 7',
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
		once = false,
		condition = 'Return.TargetAlive("Sukhumi Airbase") < 4 and Return.TargetAlive("Sukhumi Airbase Strategics") < 5',
		action = {
			[1] = 'Action.Text("Recent air strikes have destroyed enemy ground elements running operations at Sukhumi Airbase. Without their ground support, any remaining aircraft at the airstrip will no longer be able to launch on sorties.")',
		}
	},
	["LHA_Tarawa"] = {
		active = true,
		condition = 'Return.TargetAlive("LHA_Tarawa") == 0',
		action = {
			[1] = 'db_airbases["LHA_Tarawa"].inactive = true',
			[2] = 'Action.Text("After the LHA_Tarawa has been hit by air strikes and sunk, VMA 311 is no longer able to fly. Most of its planes are deep into the Gulf waters and it will need a long time to restore this unit s capabilities")',
		}
	},
	["CVN-74 John C. Stennis sunk"] = {
		active = true,
		condition = 'Return.TargetAlive("CVN-74 John C. Stennis") == 0',
		action = {
			[1] = 'db_airbases["CVN-74 John C. Stennis"].inactive = true',
			[2] = 'Action.Text("After the CVN-74 John C. Stennis has been hit by air strikes and sunk, Squadrons are no longer able to fly. Most of its planes are deep into the Gulf waters and it will need a long time to restore this unit s capabilities")',
		}
	},
	
	
	----- RED CAP -----
	["CAP After EWR Destroyed"] = {
		active = true,
		condition = 'Return.TargetAlive("EWR 1 501") == 0 and Return.TargetAlive("EWR 2 502") == 0 and Return.TargetAlive("EWR 3 503") == 0',
		action = {
			[1] = 'Action.TargetActive("CAP Red North", true)',
			[2] = 'Action.TargetActive("CAP Red Center", true)',
			[3] = 'Action.TargetActive("CAP Red South", true)',
			[4] = 'Action.TargetActive("Mozdok Interception 2", false)',
			[5] = 'Action.TargetActive("Batumi Interception 1", false)',
			[6] = 'Action.TargetActive("Batumi Interception 2", false)',
			[7] = 'Action.TargetActive("Batumi Interception Standby 1", false)',
			[8] = 'Action.TargetActive("Sukhumi Interception 1", false)',
			[9] = 'Action.TargetActive("Sukhumi Interception 2", false)',
			[10] = 'Action.TargetActive("Sukhumi Interception Standby 1", false)',
			[11] = 'Action.TargetActive("Gudauta Interception 1", false)',
			[12] = 'Action.TargetActive("Gudauta Interception 2", false)',
			[13] = 'Action.TargetActive("Kutaisi Interception 1", false)',
			[14] = 'Action.TargetActive("Kutaisi Interception 2", false)',
			[15] = 'Action.TargetActive("Mozdok Interception 1", false)',
		},
	},
	["CAP After EWR Destroyed"] = {
		active = true,
		once = false,
		condition = 'Return.TargetAlive("EWR 1 501") == 0 and Return.TargetAlive("EWR 2 502") == 0 and Return.TargetAlive("EWR 3 503") == 0',
		action = {
			[1] = 'Action.Text("With the recent destruction of all Early Warning Radar sites in the operations area, the ability of the enemy to launch interceptors against our strike packages was severely degraded. Intelligence expects that the enemy will increasingly depend on Combat Air Patrols to compensate, though without the support of ground controllers these are estimated to be of limited effectiveness.")',
		},
	},
	
	----- REPAIR AND REINFORCEMENTS -----
	["Repair"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitRepair()',
	},
	-- Miguel21 modification M19 : Repair SAM
	["GroundUnitRepair"] = {
		active = true,
		condition = 'true',
		action = 'Action.GroundUnitRepair()',
	},
	["Reinforce VAW-125"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/VAW-125", "VAW-125", 8)',
	},
	["Reinforce 174 ARW"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/174 ARW", "174 ARW", 12)',
	},	
	["Reinforce VFA-106"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/VFA-106", "VFA-106", 16)',
	},
	["Reinforce VMFA-312"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/VMFA-312", "VMFA-312", 16)',
	},
	["Reinforce VMA 311"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("VMA 331", "VMA 311", 4)',
	},
	["Reinforce VF-101"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/VF-101", "VF-101", 16)',
	},
	["Reinforce VF-143"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/VF-143", "VF-143", 16)',
	},
	["Reinforce 19.IAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/19.IAP", "19.IAP", 10)',
	},	
	["Reinforce 31.IAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/31.IAP", "31.IAP", 12)',
	},
	["Reinforce 28.IAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/28.IAP", "28.IAP", 12)',
	},
	["Reinforce 368.ShAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/368.ShAP", "368.ShAP", 16)',
	},
	["Reinforce 3.IAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/3.IAP", "3.IAP", 12)',
	},
	["Reinforce 559.BAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/559.BAP", "559.BAP", 12)',
	},
	["Reinforce 52.TBAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/52.TBAP", "52.TBAP", 6)',
	},	
	["Reinforce 959.BAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/959.BAP", "959.BAP", 12)',
	},
	["Reinforce 79.TBAP"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/79.TBAP", "79.TBAP", 6)',
	},
	["Reinforce 174.IAP-PVO"] = {
		active = true,
		condition = 'true',
		action = 'Action.AirUnitReinforce("R/174.IAP-PVO", "174.IAP-PVO", 6)',
	},	

	----- AVIATION UNIT STATUS -----
	["VF-101 Alive 75%"] = {
		active = true,
		once = true,
		condition = 'Return.AirUnitAlive("VF-101") + Return.AirUnitReady("R/VF-101") < 13',
		action = 'Action.Text("Aircraft strength of the VF-101 equiped with Tomcat has fallen below 75%.")',
	},
	["VF-101 Alive 50%"] = {
		active = true,
		once = true,
		condition = 'Return.AirUnitAlive("VF-101") + Return.AirUnitReady("R/VF-101") < 9',
		action = 'Action.Text("Aircraft strength of the VF-101 equiped with Tomcat has fallen below 50%. If losses continue at the present rate, the combat capability of the squadron is in jeopardy.")',
	},
	["VF-101 Alive 25%"] = {
		active = true,
		once = true,
		condition = 'Return.AirUnitAlive("VF-101") + Return.AirUnitReady("R/VF-101") < 5',
		action = 'Action.Text("Aircraft strength of the VF-101 equiped with Tomcat has fallen below 25%. The number of available airframes is critically low. The squadron is short of destruction.")',
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
}
