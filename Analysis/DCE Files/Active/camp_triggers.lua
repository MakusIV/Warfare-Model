camp_triggers = {
	['Reinforce VAW-125'] = {
		['action'] = 'Action.AirUnitReinforce("R/VAW-125", "VAW-125", 8)',
		['condition'] = 'true',
		['active'] = true,
	},
	['Tbilissi Airbase Disabled Text'] = {
		['action'] = {
			[1] = 'Action.Text("The infrastructure at Tbilissi-Lochini Airbase has been destroyed by air strikes. Flying operations at this base have ceased completely and are unlikely to resume. This will ease our efforts to hit other targets in the Kutaisi Country area.")',
		},
		['once'] = false,
		['condition'] = 'Return.TargetAlive("Tbilisi Airbase") < 7',
		['active'] = true,
	},
	['VF-101 Alive 25%'] = {
		['action'] = 'Action.Text("Aircraft strength of the VF-101 equiped with Tomcat has fallen below 25%. The number of available airframes is critically low. The squadron is short of destruction.")',
		['once'] = true,
		['condition'] = 'Return.AirUnitAlive("VF-101") + Return.AirUnitReady("R/VF-101") < 5',
		['active'] = true,
	},
	['Reinforce 28.IAP'] = {
		['action'] = 'Action.AirUnitReinforce("R/28.IAP", "28.IAP", 12)',
		['condition'] = 'true',
		['active'] = true,
	},
	['Cargo convoy 2 Patrol ATest Sea'] = {
		['action'] = 'Action.ShipMission("Cargo convoy 2", {{"Ships 1-5", "Ships 1-4", "Ships 1-3", "Ships 1-2"}}, 8, 5, nil)',
		['once'] = true,
		['condition'] = 'Return.Mission() == 1',
		['active'] = false,
	},
	['Reinforce 559.BAP'] = {
		['action'] = 'Action.AirUnitReinforce("R/559.BAP", "559.BAP", 12)',
		['condition'] = 'true',
		['active'] = true,
	},
	['CVN-74 John C. Stennis sunk'] = {
		['action'] = {
			[1] = 'db_airbases["CVN-74 John C. Stennis"].inactive = true',
			[2] = 'Action.Text("After the CVN-74 John C. Stennis has been hit by air strikes and sunk, Squadrons are no longer able to fly. Most of its planes are deep into the Gulf waters and it will need a long time to restore this unit s capabilities")',
		},
		['condition'] = 'Return.TargetAlive("CVN-74 John C. Stennis") == 0',
		['active'] = true,
	},
	['Reinforce VMFA-312'] = {
		['action'] = 'Action.AirUnitReinforce("R/VMFA-312", "VMFA-312", 16)',
		['condition'] = 'true',
		['active'] = true,
	},
	['Kobuleti Airbase Disabled'] = {
		['action'] = {
			[1] = 'db_airbases["Kobuleti"].inactive = true',
		},
		['condition'] = 'Return.TargetAlive("Kobuleti Airbase") < 11',
		['active'] = true,
	},
	['Gudauta Airbase Disabled Text'] = {
		['action'] = {
			[1] = 'Action.Text("After the facilities at Gudauta Airbase have been hit by air strikes, air operations at this base came to a complete stop. Intelligence believes that due to the heavy damage inflicted, the base is no longer ably to produce any aviation sorties.")',
		},
		['once'] = false,
		['condition'] = 'Return.TargetAlive("Gudauta Airbase") < 10',
		['active'] = true,
	},
	['Campaign End Draw'] = {
		['action'] = {
			[1] = 'Action.CampaignEnd("draw")',
			[2] = 'Action.Text("The air campaign has seen a sustained period of inactivity. Seemingly unable to complete the destruction of the Russian Air Force and infrastructure, US Central Command has called off all squadrons from offensive operations. We hope negociations with Russians will convince them to withdraw from Georgia")',
			[3] = 'NoMoreNewspaper = true',
		},
		['once'] = true,
		['condition'] = 'MissionInstance == 40',
		['active'] = true,
	},
	['TF-71 Patrol ATest Sea'] = {
		['action'] = 'Action.ShipMission("TF-71", {{"Indy 1-1", "Indy 1-2", "Indy 1-3", "Indy 1-4"}}, 10, 8, nil)',
		['once'] = true,
		['condition'] = 'Return.Mission() == 1',
		['active'] = false,
	},
	['VF-101 Alive 50%'] = {
		['action'] = 'Action.Text("Aircraft strength of the VF-101 equiped with Tomcat has fallen below 50%. If losses continue at the present rate, the combat capability of the squadron is in jeopardy.")',
		['once'] = true,
		['condition'] = 'Return.AirUnitAlive("VF-101") + Return.AirUnitReady("R/VF-101") < 9',
		['active'] = true,
	},
	['Reinforce 31.IAP'] = {
		['action'] = 'Action.AirUnitReinforce("R/31.IAP", "31.IAP", 12)',
		['condition'] = 'true',
		['active'] = true,
	},
	['Reinforce 52.TBAP'] = {
		['action'] = 'Action.AirUnitReinforce("R/52.TBAP", "52.TBAP", 6)',
		['condition'] = 'true',
		['active'] = true,
	},
	['Kutaisi Airbase Disabled'] = {
		['action'] = {
			[1] = 'db_airbases["Kutaisi"].inactive = true',
		},
		['condition'] = 'Return.TargetAlive("Kutaisi Airbase") < 11',
		['active'] = true,
	},
	['Campaign End Loss 2'] = {
		['action'] = {
			[2] = 'Action.Text("After the CVN-71 Theodore Roosevelt has been hit by air strikes and sunk, VF-101 is no longer able to fly. Most of its planes are deep into the Caucasian waters and it will need a long time to restore this unit s capabilities. Other US Navy units will have to continue the fight without the VF-101 support. This is a bitter failure for the Navy")',
			[3] = 'Action.AddImage("Newspaper_Victory_red.jpg", "red")',
			[1] = 'Action.CampaignEnd("loss")',
			[4] = 'Action.AddImage("Newspaper_Defeat_blue.jpg", "blue")',
			[5] = 'NoMoreNewspaper = true',
		},
		['once'] = false,
		['condition'] = 'Return.TargetAlive("CVN-71 Theodore Roosevelt") == 0',
		['active'] = true,
	},
	['Reinforce VF-143'] = {
		['action'] = 'Action.AirUnitReinforce("R/VF-143", "VF-143", 16)',
		['condition'] = 'true',
		['active'] = true,
	},
	['CAP After EWR Destroyed'] = {
		['action'] = {
			[1] = 'Action.Text("With the recent destruction of all Early Warning Radar sites in the operations area, the ability of the enemy to launch interceptors against our strike packages was severely degraded. Intelligence expects that the enemy will increasingly depend on Combat Air Patrols to compensate, though without the support of ground controllers these are estimated to be of limited effectiveness.")',
		},
		['once'] = false,
		['condition'] = 'Return.TargetAlive("EWR 1 501") == 0 and Return.TargetAlive("EWR 2 502") == 0 and Return.TargetAlive("EWR 3 503") == 0',
		['active'] = true,
	},
	['Campaign End Victory 2'] = {
		['action'] = {
			[2] = 'Action.Text("Russian forces are completly defeated. After repeated air strikes and disastrous losses in air-air combat, the russians are no longer able to produce any sorties or offer any resistance. The US Navy now owns complete air superiority. With the disappearance of the air threat, we hope that russians will decide to leave Georgia quickly. Well done.")',
			[3] = 'Action.AddImage("Newspaper_Victory_blue.jpg", "blue")',
			[1] = 'Action.CampaignEnd("win")',
			[4] = 'Action.AddImage("Newspaper_Defeat_red.jpg", "red")',
			[5] = 'NoMoreNewspaper = true',
		},
		['once'] = false,
		['condition'] = 'Return.AirUnitReady("19.IAP") + Return.AirUnitReady("31.IAP") + Return.AirUnitReady("28.IAP") + Return.AirUnitReady("368.ShAP") + Return.AirUnitReady("3.IAP") + Return.AirUnitReady("559.BAP") + Return.AirUnitReady("174.IAP-PVO") + Return.AirUnitReady("52.TBAP") + Return.AirUnitReady("959.BAP") + Return.AirUnitReady("79.TBAP") < 4',
		['active'] = true,
	},
	['Reinforce 174 ARW'] = {
		['action'] = 'Action.AirUnitReinforce("R/174 ARW", "174 ARW", 12)',
		['condition'] = 'true',
		['active'] = true,
	},
	['Reinforce 79.TBAP'] = {
		['action'] = 'Action.AirUnitReinforce("R/79.TBAP", "79.TBAP", 6)',
		['condition'] = 'true',
		['active'] = true,
	},
	['Repair'] = {
		['action'] = 'Action.AirUnitRepair()',
		['condition'] = 'true',
		['active'] = true,
	},
	['CVN-71 Theodore Roosevelt Damaged Heavy'] = {
		['action'] = {
			[2] = 'Action.Text("CVN-71 Theodore Roosevelt has sustained heavy damage under circumstances still somewhat unclear at the moment. After a valiant damage control effort by its crew and support from other ships of Task Force 70, the complete loss of the carrier could be averted. Being taken under tow by its escorts, CVN-71 Theodore Roosevelt is on the way to friendly harbor for emergency repairs before returning to the United States. All combat operations against Russian forces have been put on hold until further notice.")',
			[3] = 'Action.AddImage("Newspaper_Victory_red.jpg", "red")',
			[1] = 'Action.CampaignEnd("loss")',
			[4] = 'Action.AddImage("Newspaper_Defeat_blue.jpg", "blue")',
			[5] = 'NoMoreNewspaper = true',
		},
		['once'] = true,
		['condition'] = 'camp.ShipHealth and camp.ShipHealth["CVN-71 Theodore Roosevelt"] and camp.ShipHealth["CVN-71 Theodore Roosevelt"] < 33 and camp.ShipHealth["CVN-71 Theodore Roosevelt"] > 0',
		['active'] = true,
	},
	['Reinforce 174.IAP-PVO'] = {
		['action'] = 'Action.AirUnitReinforce("R/174.IAP-PVO", "174.IAP-PVO", 6)',
		['condition'] = 'true',
		['active'] = true,
	},
	['CVN-71 Theodore Roosevelt Sunk'] = {
		['action'] = {
			[2] = 'Action.Text("CVN-71 Theodore Roosevelt has been lost, the exact cause of her sinking is still somewhat unclear at the moment. Despite her evacuation being orderly and escorts of the Battle Group picking up many survivors, losses are expected to be very high. Search and rescue operations are still ongoing. All combat operations against Russian forces have been put on hold until further notice.")',
			[3] = 'Action.AddImage("Newspaper_Victory_red.jpg", "red")',
			[1] = 'Action.CampaignEnd("loss")',
			[4] = 'Action.AddImage("Newspaper_Defeat_blue.jpg", "blue")',
			[5] = 'NoMoreNewspaper = true',
		},
		['once'] = true,
		['condition'] = 'Return.UnitDead("CVN-71 Theodore Roosevelt")',
		['active'] = true,
	},
	['LHA Group Close to Georgian Coasts'] = {
		['action'] = {
			[1] = 'Action.ShipMission("LHA-Group", {{"Indy 3-5", "Indy 3-6", "Indy 3-7", "Indy 3-8""}}, 10, 8, nil)',
			[2] = 'Action.AirUnitActive("VMA 311", true)',
			[3] = 'Action.Text("After the estimated near destruction of all the enemy anti-ship air squadrons, LHA Group is allowed to move closer of Georgian coast and VMA-311 will begin its air to ground campaign.")',
		},
		['once'] = true,
		['condition'] = 'Return.AirUnitReady("368.ShAP") + Return.AirUnitReady("559.BAP") + Return.AirUnitReady("52.TBAP") + Return.AirUnitReady("959.BAP") + Return.AirUnitReady("79.TBAP") < 10',
		['active'] = true,
	},
	['CVN-71 Theodore Roosevelt Damaged Light'] = {
		['action'] = {
			[1] = 'Action.Text("CVN-71 Theodore Roosevelt has sustained light damage under circumstances still somewhat unclear at the moment. Flight operations continue as scheduled.")',
		},
		['once'] = true,
		['condition'] = 'camp.ShipHealth and camp.ShipHealth["CVN-71 Theodore Roosevelt"] and camp.ShipHealth["CVN-71 Theodore Roosevelt"] < 100 and camp.ShipHealth["CVN-71 Theodore Roosevelt"] >= 66',
		['active'] = true,
	},
	['VF-101 Alive 75%'] = {
		['action'] = 'Action.Text("Aircraft strength of the VF-101 equiped with Tomcat has fallen below 75%.")',
		['once'] = true,
		['condition'] = 'Return.AirUnitAlive("VF-101") + Return.AirUnitReady("R/VF-101") < 13',
		['active'] = true,
	},
	['Tbilissi Airbase Disabled'] = {
		['action'] = {
			[1] = 'db_airbases["Tbilissi-Lochini"].inactive = true',
		},
		['condition'] = 'Return.TargetAlive("Tbilisi Airbase") < 7',
		['active'] = true,
	},
	['Reinforce 19.IAP'] = {
		['action'] = 'Action.AirUnitReinforce("R/19.IAP", "19.IAP", 10)',
		['condition'] = 'true',
		['active'] = true,
	},
	['Reinforce 368.ShAP'] = {
		['action'] = 'Action.AirUnitReinforce("R/368.ShAP", "368.ShAP", 16)',
		['condition'] = 'true',
		['active'] = true,
	},
	['TF-74 Patrol ATest Sea'] = {
		['action'] = 'Action.ShipMission("TF-74", {{"Indy 2-1", "Indy 2-2", "Indy 2-3", "Indy 2-4"}}, 10, 8, nil)',
		['once'] = true,
		['condition'] = 'Return.Mission() == 1',
		['active'] = false,
	},
	['Batumi Airbase Disabled Text'] = {
		['action'] = {
			[1] = 'Action.Text("After the facilities at Batumi Airbase have been hit by air strikes, air operations at this base came to a complete stop. Intelligence believes that due to the heavy damage inflicted, the base is no longer ably to produce any aviation sorties.")',
		},
		['once'] = false,
		['condition'] = 'Return.TargetAlive("Batumi Airbase") < 6',
		['active'] = true,
	},
	['Red Ground Target Briefing Intel'] = {
		['action'] = 'Action.AddGroundTargetIntel("red")',
		['condition'] = 'true',
		['active'] = true,
	},
	['Sukhumi Airbase Disabled Text'] = {
		['action'] = {
			[1] = 'Action.Text("Recent air strikes have destroyed enemy ground elements running operations at Sukhumi Airbase. Without their ground support, any remaining aircraft at the airstrip will no longer be able to launch on sorties.")',
		},
		['once'] = false,
		['condition'] = 'Return.TargetAlive("Sukhumi Airbase") < 4 and Return.TargetAlive("Sukhumi Airbase Strategics") < 5',
		['active'] = true,
	},
	['Reinforce VFA-106'] = {
		['action'] = 'Action.AirUnitReinforce("R/VFA-106", "VFA-106", 16)',
		['condition'] = 'true',
		['active'] = true,
	},
	['Cargo convoy 1 Patrol ATest Sea'] = {
		['action'] = 'Action.ShipMission("Cargo convoy 1", {{"Ships 1-1", "Ships 1-2", "Ships 1-3", "Ships 1-4"}}, 8, 5, nil)',
		['once'] = true,
		['condition'] = 'Return.Mission() == 1',
		['active'] = false,
	},
	['Reinforce 3.IAP'] = {
		['action'] = 'Action.AirUnitReinforce("R/3.IAP", "3.IAP", 12)',
		['condition'] = 'true',
		['active'] = true,
	},
	['Senaki Airbase Disabled Text'] = {
		['action'] = {
			[1] = 'Action.Text("After the facilities at Senaki-Kolkhi Airbase have been hit by air strikes, air operations at this base came to a complete stop. Intelligence believes that due to the heavy damage inflicted, the base is no longer ably to produce any aviation sorties.")',
		},
		['once'] = false,
		['condition'] = 'Return.TargetAlive("Senaki Airbase") < 12',
		['active'] = true,
	},
	['Campaign End Victory 1'] = {
		['action'] = {
			[2] = 'Action.Text("The US Navy units deployed off the coasts of Georgia have successfully destroyed all the targets that they were assigned by US Central Command. With the complete destruction of the Russian airforce over Georgia, the air campaign of this war comes to an end. Russian will soon begin to withdraw from Georgia. Well done.")',
			[3] = 'Action.AddImage("Newspaper_Victory_blue.jpg", "blue")',
			[1] = 'Action.CampaignEnd("win")',
			[4] = 'Action.AddImage("Newspaper_Defeat_red.jpg", "red")',
			[5] = 'NoMoreNewspaper = true',
		},
		['once'] = false,
		['condition'] = 'GroundTarget["blue"].percent < 45',
		['active'] = true,
	},
	['Campaign first destructions'] = {
		['action'] = {
			[1] = 'Action.Text("First targets have been destroyed. Keep up the good work")',
		},
		['once'] = true,
		['condition'] = 'GroundTarget["blue"].percent < 100',
		['active'] = false,
	},
	['Batumi Airbase Disabled'] = {
		['action'] = {
			[1] = 'db_airbases["Batumi"].inactive = true',
		},
		['condition'] = 'Return.TargetAlive("Batumi Airbase") < 6',
		['active'] = true,
	},
	['Sukhumi Airbase Disabled'] = {
		['action'] = {
			[1] = 'db_airbases["Sukhumi"].inactive = true',
		},
		['condition'] = 'Return.TargetAlive("Sukhumi Airbase") < 4 and Return.TargetAlive("Sukhumi Airbase Strategics") < 5',
		['active'] = true,
	},
	['CVN-71 Theodore Roosevelt Damaged Moderate'] = {
		['action'] = {
			[2] = 'Action.Text("CVN-71 Theodore Roosevelt has sustained substantial damage under circumstances still somewhat unclear at the moment. Unable to continue flight operations, the carrier is retreating under own power for repairs. All combat operations against Russian forces have been put on hold until further notice.")',
			[3] = 'Action.AddImage("Newspaper_Victory_red.jpg", "red")',
			[1] = 'Action.CampaignEnd("loss")',
			[4] = 'Action.AddImage("Newspaper_Defeat_blue.jpg", "blue")',
			[5] = 'NoMoreNewspaper = true',
		},
		['once'] = true,
		['condition'] = 'camp.ShipHealth and camp.ShipHealth["CVN-71 Theodore Roosevelt"] and camp.ShipHealth["CVN-71 Theodore Roosevelt"] < 66 and camp.ShipHealth["CVN-71 Theodore Roosevelt"] >= 33',
		['active'] = true,
	},
	['Gudauta Airbase Disabled'] = {
		['action'] = {
			[1] = 'db_airbases["Gudauta"].inactive = true',
		},
		['condition'] = 'Return.TargetAlive("Gudauta Airbase") < 10',
		['active'] = true,
	},
	['Reinforce 959.BAP'] = {
		['action'] = 'Action.AirUnitReinforce("R/959.BAP", "959.BAP", 12)',
		['condition'] = 'true',
		['active'] = true,
	},
	['Reinforce VMA 311'] = {
		['action'] = 'Action.AirUnitReinforce("VMA 331", "VMA 311", 4)',
		['condition'] = 'true',
		['active'] = true,
	},
	['Kutaisi Airbase Disabled Text'] = {
		['action'] = {
			[1] = 'Action.Text("The infrastructure at Kutaisi Airbase has been destroyed by air strikes. Flying operations at this base have ceased completely and are unlikely to resume. This will ease our efforts to hit other targets in the Kutaisi Country area.")',
		},
		['once'] = false,
		['condition'] = 'Return.TargetAlive("Kutaisi Airbase") < 11',
		['active'] = true,
	},
	['Campaign Briefing'] = {
		['action'] = {
			[2] = 'Action.Text("The US Navy has sent considerable forces near Georgia. The Task Force 71 is leaded by the CVN-71 Theodore Roosevelt. At the forefront are the F/A-18C of the VFA-106 and VMFA-312 who are tasked to attack Russian air defenses, Airbases and many strategical targets in Georgia like bridges train stations and Harbors. Air superiority and strikers escort will be the mission of the VF-101 and VF-143 with their legendary F-14A Tomcats. E-2D will provide AWACS constant cover. Together these squadrons form a powerful and mighty force.")',
			[3] = 'Action.Text("The Russian Air Force is flying a mix of MiG-21, MiG-25 and MiG-23 fighters directed by ground based early warning radar. Air bases and target complexes of high value are protected by a variety of surface-air missile systems, such as the Sa-2 Guindeline, SA-6 Gainful, the SA-8 Gecko and the SA-3 Goa, as well as short-range IR-SAMs and AAA. Our goal will be to gain air superiority over Georgia by neutralizing main bases in the country and destroying SAM systems. Russia Homeland is strictly forbidden. You are not allowed to attack ground target in Russia but air to air combat can be initiated near and over Russia. Our Task Force can be targeted by Russians anti-ship fleet : Su-24, Tu-22 and TU-142 with dangerous missiles")',
			[1] = 'Action.Text("In a desperate try to free from russian tyrany, Georgia patriots tried to bring down the governement. This action was reprimed with violence by russian troops and loyal Georgian forces. Many civilians were killed and tortured to prevent any other freedom movements. United Nations were not able to stop russians violences and the United States of America decided to do something to convince Russia to stop this. Turkish government was not ready to open his bases to US attack planes and only one Navy Task Force can be sent near Georgian coasts to show Russia they have to stop violence in Georgia.")',
			[4] = 'Action.AddImage("Newspaper_FirstNight_blue.jpg", "blue")',
			[5] = 'Action.AddImage("Newspaper_FirstNight_red.jpg", "red")',
		},
		['once'] = true,
		['condition'] = 'true',
		['active'] = false,
	},
	['Campaign End Loss'] = {
		['action'] = {
			[2] = 'Action.Text("Ongoing combat operations have exhausted VF-101. Loss rate has reached a level where reinforcements are no longer able to sustain combat operations. With the failure of US Navy Air Force to attain air superiority, US Central Command has decided to call of the air campaign against the Russians. They will be abble to stay in Georgia and our diplomatic power in the world is really weaked by this defeat.")',
			[3] = 'Action.AddImage("Newspaper_Victory_red.jpg", "red")',
			[1] = 'Action.CampaignEnd("loss")',
			[4] = 'Action.AddImage("Newspaper_Defeat_blue.jpg", "blue")',
			[5] = 'NoMoreNewspaper = true',
		},
		['once'] = false,
		['condition'] = 'Return.AirUnitAlive("VF-101") + Return.AirUnitReady("R/VF-101") < 5',
		['active'] = true,
	},
	['Reinforce VF-101'] = {
		['action'] = 'Action.AirUnitReinforce("R/VF-101", "VF-101", 16)',
		['condition'] = 'true',
		['active'] = true,
	},
	['Kobuleti Airbase Disabled Text'] = {
		['action'] = {
			[1] = 'Action.Text("After the facilities at Kobuleti Airbase have been hit by air strikes, air operations at this base came to a complete stop. Intelligence believes that due to the heavy damage inflicted, the base is no longer ably to produce any aviation sorties.")',
		},
		['once'] = false,
		['condition'] = 'Return.TargetAlive("Kobuleti Airbase") < 11',
		['active'] = true,
	},
	['Campaign 40 percents destructions'] = {
		['action'] = {
			[1] = 'Action.Text("Enemy targets have sustained great damages. Strike missions are really efficient and we will win this war soon")',
		},
		['once'] = true,
		['condition'] = 'GroundTarget["blue"].percent < 60',
		['active'] = true,
	},
	['LHA-Group Far from Georgian Coasts'] = {
		['action'] = {
			[1] = 'Action.ShipMission("LHA-Group", {{"Indy 3-1", "Indy 3-2", "Indy 3-3", "Indy 3-4"}}, 10, 8, nil)',
		},
		['once'] = true,
		['condition'] = 'Return.Mission() == 1',
		['active'] = false,
	},
	['LHA_Tarawa'] = {
		['action'] = {
			[1] = 'db_airbases["LHA_Tarawa"].inactive = true',
			[2] = 'Action.Text("After the LHA_Tarawa has been hit by air strikes and sunk, VMA 311 is no longer able to fly. Most of its planes are deep into the Gulf waters and it will need a long time to restore this unit s capabilities")',
		},
		['condition'] = 'Return.TargetAlive("LHA_Tarawa") == 0',
		['active'] = true,
	},
	['Blue Ground Target Briefing Intel'] = {
		['action'] = 'Action.AddGroundTargetIntel("blue")',
		['condition'] = 'true',
		['active'] = true,
	},
	['Senaki Airbase Disabled'] = {
		['action'] = {
			[1] = 'db_airbases["Senaki-Kolkhi"].inactive = true',
		},
		['condition'] = 'Return.TargetAlive("Senaki Airbase") < 12',
		['active'] = true,
	},
	['Campaign 20 percents destructions'] = {
		['action'] = {
			[1] = 'Action.Text("Enemy targets have sustained fair damages. Keep up the good work")',
		},
		['once'] = true,
		['condition'] = 'GroundTarget["blue"].percent < 80',
		['active'] = true,
	},
	['GroundUnitRepair'] = {
		['action'] = 'Action.GroundUnitRepair()',
		['condition'] = 'true',
		['active'] = true,
	},
	['Campaign 50 percents destructions'] = {
		['action'] = {
			[1] = 'Action.Text("More than half of our targets are neutralized. Intelligence think that the enemy will ask for a cease fire soon")',
		},
		['once'] = true,
		['condition'] = 'GroundTarget["blue"].percent < 50',
		['active'] = true,
	},
}
