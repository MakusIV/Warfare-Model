targetlist = {
	['blue'] = {
		['101 EWR Site'] = {
			['elements'] = {
				[1] = {
					['name'] = 'EWR Station West',
				},
				[2] = {
					['name'] = 'EWR CP West',
				},
			},
			['groupId'] = 21,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 700465.26372636,
			['x'] = -44781.216798702,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['name'] = '101 EWR Site',
			['priority'] = 5,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'soft',
			},
		},
		['Mozdok airbase OCA Strike'] = {
			['class'] = 'airbase',
			['ATO'] = true,
			['unit'] = {
				['number'] = 12,
				['type'] = 'Su-25T',
				['name'] = '1./17.IAP',
			},
			['y'] = 834453.14285714,
			['x'] = -83454.571428571,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['foundOobGround'] = true,
			['name'] = 'Mozdok',
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Parked Aircraft',
			},
		},
		['Recovery Tanker'] = {
			['slaved'] = {
				[1] = 'CVN-71 Theodore Roosevelt',
				[2] = 310,
				[3] = 30000,
			},
			['text'] = '',
			['ATO'] = true,
			['y'] = 517828.66670643,
			['x'] = -281040.3717094,
			['firepower'] = {
				['min'] = 1,
				['max'] = 1,
			},
			['priority'] = 5,
			['task'] = 'Refueling',
			['attributes'] = {
				[1] = 'low',
			},
		},
		['102 EWR Site'] = {
			['elements'] = {
				[1] = {
					['name'] = 'EWR Station Center',
				},
				[2] = {
					['name'] = 'EWR CP Center',
				},
			},
			['groupId'] = 19,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 838506.51200001,
			['x'] = -110842.00914282,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['name'] = '102 EWR Site',
			['priority'] = 5,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'soft',
			},
		},
		['Bridge Vladikavkaz South MN 76'] = {
			['elements'] = {
				[1] = {
					['y'] = 852723.0625,
					['x'] = -168229.1875,
					['name'] = 'Bridge Vladikavkaz South MN 76',
				},
			},
			['picture'] = {
				[1] = 'Vladikavkaz_Bridge.png',
			},
			['ATO'] = true,
			['y'] = 852723.0625,
			['x'] = -168229.1875,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 3,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Mozdok Airbase'] = {
			['elements'] = {
				[7] = {
					['y'] = 832570.8125,
					['x'] = -83996.3828125,
					['name'] = 'Hangar 3',
				},
				[1] = {
					['y'] = 835186.75,
					['x'] = -84118.1328125,
					['name'] = 'Fuel Support House',
				},
				[2] = {
					['y'] = 834521,
					['x'] = -84169.25,
					['name'] = 'Mozdok Control Tower',
				},
				[4] = {
					['y'] = 834497.9375,
					['x'] = -84205.1796875,
					['name'] = 'Mozdok Power Supply',
				},
				[8] = {
					['y'] = 832253.125,
					['x'] = -85358.21875,
					['name'] = 'Deported Hangar 1',
				},
				[9] = {
					['y'] = 832343.125,
					['x'] = -85306.453125,
					['name'] = 'Deported Hangar 2',
				},
				[5] = {
					['y'] = 835012.6875,
					['x'] = -84026.2890625,
					['name'] = 'Hangar 1',
				},
				[10] = {
					['y'] = 832356.5625,
					['x'] = -85320.0078125,
					['name'] = 'Deported Hangar 3',
				},
				[3] = {
					['y'] = 834535.3125,
					['x'] = -84198.1640625,
					['name'] = 'Mozdok Command House',
				},
				[6] = {
					['y'] = 835015.5,
					['x'] = -84049.09375,
					['name'] = 'Hangar 2',
				},
			},
			['picture'] = {
				[1] = 'Mozdok_Airbase.png',
			},
			['ATO'] = true,
			['y'] = 833829.28125,
			['x'] = -84474.7171875,
			['firepower'] = {
				['min'] = 4,
				['max'] = 8,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 3,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Structure',
			},
		},
		['Kutaisi Alert'] = {
			['radius'] = 200000,
			['ATO'] = true,
			['inactive'] = false,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['attributes'] = {
			},
			['priority'] = 10,
			['base'] = 'Kutaisi',
			['task'] = 'Intercept',
		},
		['Bridge Vladikavkaz North MN 76'] = {
			['elements'] = {
				[1] = {
					['y'] = 850403,
					['x'] = -164245.28125,
					['name'] = 'Bridge Vladikavkaz North MN 76',
				},
			},
			['picture'] = {
				[1] = 'Vladikavkaz_Bridge.png',
			},
			['ATO'] = true,
			['y'] = 850403,
			['x'] = -164245.28125,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 3,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['206 SA-11 Site B-3'] = {
			['elements'] = {
				[1] = {
					['name'] = '206 SA-11 Site B-3-1',
				},
				[2] = {
					['name'] = '206 SA-11 Site B-3-2',
				},
				[3] = {
					['name'] = '206 SA-11 Site B-3-3',
				},
				[4] = {
					['name'] = '206 SA-11 Site B-3-4',
				},
				[5] = {
					['name'] = '206 SA-11 Site B-3-5',
				},
				[6] = {
					['name'] = '206 SA-11 Site B-3-6',
				},
				[7] = {
					['name'] = '206 SA-11 Site B-3-7',
				},
				[8] = {
					['name'] = '206 SA-11 Site B-3-8',
				},
				[9] = {
					['name'] = '206 SA-11 Site B-3-9',
				},
				[10] = {
					['name'] = '206 SA-11 Site B-3-10',
				},
				[11] = {
					['name'] = '206 SA-11 Site B-3-11',
				},
				[12] = {
					['name'] = '206 SA-11 Site B-3-12',
				},
			},
			['groupId'] = 427,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 696007.89224936,
			['x'] = -63181.709052048,
			['firepower'] = {
				['min'] = 2,
				['max'] = 8,
			},
			['dead_last'] = 0,
			['name'] = '206 SA-11 Site B-3',
			['priority'] = 6,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'SAM',
			},
		},
		['Russian Convoy 1'] = {
			['elements'] = {
				[1] = {
					['name'] = 'Naval-1-1',
				},
				[2] = {
					['name'] = 'Russian Convoy 1-1',
				},
				[3] = {
					['name'] = 'Russian Convoy 1-2',
				},
				[4] = {
					['name'] = 'Russian Convoy 1-3',
				},
				[5] = {
					['name'] = 'Russian Convoy 1-4',
				},
				[6] = {
					['name'] = 'Russian Convoy 1-5',
				},
				[7] = {
					['name'] = 'Russian Convoy 1-6',
				},
				[8] = {
					['name'] = 'Russian Convoy 1-7',
				},
				[9] = {
					['name'] = 'Russian Convoy 1-8',
				},
				[10] = {
					['name'] = 'Russian Convoy 1-9',
				},
				[11] = {
					['name'] = 'Russian Convoy 1-10',
				},
				[12] = {
					['name'] = 'Russian Convoy 1-11',
				},
				[13] = {
					['name'] = 'Russian Convoy 1-12',
				},
				[14] = {
					['name'] = 'Russian Convoy 1-13',
				},
			},
			['groupId'] = 415,
			['foundOobGround'] = true,
			['class'] = 'ship',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 397421,
			['x'] = -143749,
			['firepower'] = {
				['min'] = 6,
				['max'] = 12,
			},
			['dead_last'] = 0,
			['name'] = 'Russian Convoy 1',
			['priority'] = 1,
			['task'] = 'Anti-ship Strike',
			['attributes'] = {
				[1] = 'ship',
			},
		},
		['106 SA-11 Site C-6'] = {
			['elements'] = {
				[1] = {
					['name'] = '106 SA-11 Site C-6-1',
				},
				[2] = {
					['name'] = '106 SA-11 Site C-6-2',
				},
				[3] = {
					['name'] = '106 SA-11 Site C-6-3',
				},
				[4] = {
					['name'] = '106 SA-11 Site C-6-4',
				},
				[5] = {
					['name'] = '106 SA-11 Site C-6-5',
				},
				[6] = {
					['name'] = '106 SA-11 Site C-6-6',
				},
				[7] = {
					['name'] = '106 SA-11 Site C-6-7',
				},
				[8] = {
					['name'] = '106 SA-11 Site C-6-8',
				},
				[9] = {
					['name'] = '106 SA-11 Site C-6-9',
				},
				[10] = {
					['name'] = '106 SA-11 Site C-6-10',
				},
				[11] = {
					['name'] = '106 SA-11 Site C-6-11',
				},
				[12] = {
					['name'] = '106 SA-11 Site C-6-12',
				},
			},
			['groupId'] = 425,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 773679.40615594,
			['x'] = -127419.38346039,
			['firepower'] = {
				['min'] = 2,
				['max'] = 6,
			},
			['dead_last'] = 0,
			['name'] = '106 SA-11 Site C-6',
			['priority'] = 6,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'SAM',
			},
		},
		['CAP Tbilissi'] = {
			['radius'] = 50000,
			['refpoint'] = 'CAP Tbilissi',
			['text'] = 'North west of Tbilissi',
			['ATO'] = true,
			['y'] = 841876.47838909,
			['x'] = -286139.46402038,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['priority'] = 20,
			['task'] = 'CAP',
			['attributes'] = {
				[1] = 'Air Forces',
			},
		},
		['Battle Group CAP'] = {
			['radius'] = 111000,
			['slaved'] = {
				[1] = 'CVN-71 Theodore Roosevelt',
				[2] = 335,
				[3] = 50000,
			},
			['text'] = '',
			['ATO'] = true,
			['y'] = 519679.08691297,
			['x'] = -255008.61064817,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['priority'] = 20,
			['task'] = 'CAP',
			['attributes'] = {
				[1] = 'CV CAP',
			},
		},
		['103 EWR Site'] = {
			['elements'] = {
				[1] = {
					['name'] = 'EWR Station East',
				},
				[2] = {
					['name'] = 'EWR CP East',
				},
			},
			['groupId'] = 20,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 902985.7142857,
			['x'] = -125550,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['name'] = '103 EWR Site',
			['priority'] = 5,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'soft',
			},
		},
		['AWACS'] = {
			['radius'] = 15000,
			['refpoint'] = 'AWACS',
			['text'] = '',
			['ATO'] = true,
			['y'] = 784780.20793295,
			['x'] = -331846.62818631,
			['firepower'] = {
				['min'] = 1,
				['max'] = 1,
			},
			['priority'] = 10,
			['task'] = 'AWACS',
			['attributes'] = {
				[1] = 'Sentry',
			},
		},
		['Tanker Track East'] = {
			['radius'] = 15000,
			['refpoint'] = 'Tanker Track East KC135',
			['text'] = 'north west of Tbilissi',
			['ATO'] = true,
			['y'] = 833669.56291753,
			['x'] = -283814.54933411,
			['firepower'] = {
				['min'] = 1,
				['max'] = 1,
			},
			['priority'] = 10,
			['task'] = 'Refueling',
			['attributes'] = {
				[1] = 'KC135',
			},
		},
		['Mineralnye-Vody airbase OCA Strike'] = {
			['class'] = 'airbase',
			['ATO'] = true,
			['unit'] = {
				['number'] = 8,
				['type'] = 'Su-24M',
				['name'] = '1./41.IAP',
			},
			['y'] = 705718.47981263,
			['x'] = -51251.551717591,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['foundOobGround'] = true,
			['name'] = 'Mineralnye-Vody',
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Parked Aircraft',
			},
		},
		['Beslan Airbase'] = {
			['elements'] = {
				[7] = {
					['y'] = 844187,
					['x'] = -149049.53125,
					['name'] = 'Refuel Station',
				},
				[1] = {
					['y'] = 843620.0625,
					['x'] = -148962.921875,
					['name'] = 'Beslan Control Tower',
				},
				[2] = {
					['y'] = 843839.625,
					['x'] = -148993.71875,
					['name'] = 'Beslan Hangar 1',
				},
				[4] = {
					['y'] = 843724.125,
					['x'] = -149005.96875,
					['name'] = 'Beslan Barrack',
				},
				[8] = {
					['y'] = 843511.75,
					['x'] = -148948.96875,
					['name'] = 'Beslan Terminal',
				},
				[9] = {
					['y'] = 843921.125,
					['x'] = -149149.171875,
					['name'] = 'Beslan Hangar 3',
				},
				[5] = {
					['y'] = 844018.875,
					['x'] = -149021.625,
					['name'] = 'Rescue Station',
				},
				[10] = {
					['y'] = 843622.9375,
					['x'] = -149095.828125,
					['name'] = 'Beslan Power Supply',
				},
				[3] = {
					['y'] = 843837.375,
					['x'] = -149028.84375,
					['name'] = 'Beslan Hangar 2',
				},
				[6] = {
					['y'] = 844111.125,
					['x'] = -149043.3125,
					['name'] = 'Repair Hangar',
				},
			},
			['picture'] = {
				[1] = 'Beslan_Airbase.png',
			},
			['ATO'] = true,
			['y'] = 843839.4,
			['x'] = -149029.9890625,
			['firepower'] = {
				['min'] = 4,
				['max'] = 8,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 4,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Structure',
			},
		},
		['Beslan Airbase OCA Strike'] = {
			['class'] = 'airbase',
			['ATO'] = true,
			['unit'] = {
				['number'] = 1,
				['type'] = 'An-26B',
				['name'] = '3.OSAP',
			},
			['y'] = 843756.7533062,
			['x'] = -148810.84954665,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['foundOobGround'] = true,
			['name'] = 'Beslan',
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Parked Aircraft',
			},
		},
		['Sweep West'] = {
			['text'] = 'in the west front area',
			['ATO'] = true,
			['y'] = 776021,
			['x'] = -138197,
			['firepower'] = {
				['min'] = 4,
				['max'] = 4,
			},
			['priority'] = 1,
			['task'] = 'Fighter Sweep',
			['attributes'] = {
			},
		},
		['Rail Bridge Kardzhin MN 49'] = {
			['elements'] = {
				[1] = {
					['y'] = 816502.625,
					['x'] = -144986.53125,
					['name'] = 'Rail Bridge Kardzhin MN 49',
				},
			},
			['picture'] = {
				[1] = 'Kardzhin_Bridges.png',
			},
			['ATO'] = true,
			['y'] = 816502.625,
			['x'] = -144986.53125,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 3,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Nalchik Airbase'] = {
			['elements'] = {
				[6] = {
					['y'] = 760813.5625,
					['x'] = -125487.359375,
					['name'] = 'Nalchik Crew House',
				},
				[2] = {
					['y'] = 760783.8125,
					['x'] = -123918.15625,
					['name'] = 'Ammunition Command Center',
				},
				[3] = {
					['y'] = 760367.0625,
					['x'] = -125484.5,
					['name'] = 'Nalchik Control Tower',
				},
				[1] = {
					['y'] = 760428.9375,
					['x'] = -124614.8046875,
					['name'] = 'Fuel Support House',
				},
				[4] = {
					['y'] = 760683.75,
					['x'] = -125478.59375,
					['name'] = 'Nalchik Main Hangar',
				},
				[5] = {
					['y'] = 760720.875,
					['x'] = -125382.1953125,
					['name'] = 'Nalchik Admin House',
				},
				[7] = {
					['y'] = 761007.4375,
					['x'] = -124947.9921875,
					['name'] = 'Nalchik Rescue Station',
				},
			},
			['picture'] = {
				[1] = 'Nalchik_Airbase.png',
			},
			['ATO'] = true,
			['y'] = 760686.49107143,
			['x'] = -125044.80022321,
			['firepower'] = {
				['min'] = 4,
				['max'] = 8,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 4,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Structure',
			},
		},
		['203 SA-10 Site A-3'] = {
			['elements'] = {
				[1] = {
					['name'] = '203 SA-10 Gainful Site A-3-1',
				},
				[2] = {
					['name'] = '203 SA-10 Site A-3-2',
				},
				[3] = {
					['name'] = '203 SA-10 Site A-3-3',
				},
				[4] = {
					['name'] = '203 SA-10 Site A-3-4',
				},
				[5] = {
					['name'] = '203 SA-10 Site A-3-5',
				},
				[6] = {
					['name'] = '203 SA-10 Site A-3-6',
				},
				[7] = {
					['name'] = '203 SA-10 Site A-3-7',
				},
				[8] = {
					['name'] = '203 SA-10 Site A-3-8',
				},
				[9] = {
					['name'] = '203 SA-10 Site A-3-9',
				},
				[10] = {
					['name'] = '203 SA-10 Site A-3-10',
				},
				[11] = {
					['name'] = '203 SA-10 Site A-3-11',
				},
			},
			['groupId'] = 422,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 883213.42857685,
			['x'] = -132438.21387713,
			['firepower'] = {
				['min'] = 2,
				['max'] = 8,
			},
			['dead_last'] = 0,
			['name'] = '203 SA-10 Site A-3',
			['priority'] = 6,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'SAM',
			},
		},
		['502 5th Artillery Division/2.Btry'] = {
			['elements'] = {
				[1] = {
					['name'] = 'BM-27 Uragan #7',
				},
				[2] = {
					['name'] = 'BM-27 Uragan #8',
				},
				[3] = {
					['name'] = 'BM-27 Uragan #9',
				},
				[4] = {
					['name'] = 'BM-27 Uragan #10',
				},
				[5] = {
					['name'] = 'BM-27 Uragan #11',
				},
				[6] = {
					['name'] = 'BM-27 Uragan #12',
				},
				[7] = {
					['name'] = 'MTLB-U 2./Btry CP',
				},
			},
			['groupId'] = 96,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 847405.6,
			['x'] = -167568.67428572,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['name'] = '502 5th Artillery Division/2.Btry',
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'soft',
			},
		},
		['504 5th Artillery Division/4.Btry'] = {
			['elements'] = {
				[1] = {
					['name'] = '2S3 Akatsia #1',
				},
				[2] = {
					['name'] = '2S3 Akatsia #2',
				},
				[3] = {
					['name'] = '2S3 Akatsia #3',
				},
				[4] = {
					['name'] = '2S3 Akatsia #4',
				},
				[5] = {
					['name'] = '2S3 Akatsia #5',
				},
				[6] = {
					['name'] = '2S3 Akatsia #6',
				},
				[7] = {
					['name'] = 'MTLB-U 4./Btry CP',
				},
			},
			['groupId'] = 98,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 855014.36571429,
			['x'] = -145299.40571429,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['name'] = '504 5th Artillery Division/4.Btry',
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'soft',
			},
		},
		['Tanker Track West'] = {
			['radius'] = 15000,
			['refpoint'] = 'Tanker Track West',
			['text'] = 'West of Kutaisi',
			['ATO'] = true,
			['y'] = 712191.85702698,
			['x'] = -270016.84129864,
			['firepower'] = {
				['min'] = 1,
				['max'] = 1,
			},
			['priority'] = 10,
			['task'] = 'Refueling',
			['attributes'] = {
				[1] = 'KC135MPRS',
			},
		},
		['204 SA-10 Site B-1'] = {
			['elements'] = {
				[1] = {
					['name'] = '204 SA-10 Site B-1-1',
				},
				[2] = {
					['name'] = '204 SA-10 Site B-1-2',
				},
				[3] = {
					['name'] = '204 SA-10 Site B-1-3',
				},
				[4] = {
					['name'] = '204 SA-10 Site B-1-4',
				},
				[5] = {
					['name'] = '204 SA-10 Site B-1-5',
				},
				[6] = {
					['name'] = '204 SA-10 Site B-1-6',
				},
				[7] = {
					['name'] = '204 SA-10 Site B-1-7',
				},
				[8] = {
					['name'] = '204 SA-10 Site B-1-8',
				},
				[9] = {
					['name'] = '204 SA-10 Site B-1-9',
				},
				[10] = {
					['name'] = '204 SA-10 Site B-1-10',
				},
				[11] = {
					['name'] = '204 SA-10 Site B-1-11',
				},
			},
			['groupId'] = 426,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 774914.01298398,
			['x'] = -115111.93913496,
			['firepower'] = {
				['min'] = 2,
				['max'] = 8,
			},
			['dead_last'] = 0,
			['name'] = '204 SA-10 Site B-1',
			['priority'] = 6,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'SAM',
			},
		},
		['Mineralnye-Vody Airbase'] = {
			['elements'] = {
				[1] = {
					['y'] = 705679.875,
					['x'] = -52146.515625,
					['name'] = 'Fuel Support House',
				},
				[2] = {
					['y'] = 705966.375,
					['x'] = -52287.57421875,
					['name'] = 'Crew Home 1',
				},
				[4] = {
					['y'] = 706210.75,
					['x'] = -52380.97265625,
					['name'] = 'Crew Home 3',
				},
				[8] = {
					['y'] = 706580.8125,
					['x'] = -52318.4140625,
					['name'] = 'Mineralnye Control Tower',
				},
				[16] = {
					['y'] = 707733.75,
					['x'] = -51376.71484375,
					['name'] = 'Deported Repair Hangar 2',
				},
				[17] = {
					['y'] = 708177.25,
					['x'] = -51190.4765625,
					['name'] = 'Deported Repair Hangar 3',
				},
				[9] = {
					['y'] = 705714.1875,
					['x'] = -51810.00390625,
					['name'] = 'Mineralnye Command House',
				},
				[5] = {
					['y'] = 707329.75,
					['x'] = -52477.5859375,
					['name'] = 'Mineralnye Rescue station',
				},
				[10] = {
					['y'] = 705334.3125,
					['x'] = -52009.95703125,
					['name'] = 'Mineralnye Power Supply 1',
				},
				[11] = {
					['y'] = 708070.625,
					['x'] = -51528.6640625,
					['name'] = 'Mineralnye Power Supply 2',
				},
				[3] = {
					['y'] = 706024.8125,
					['x'] = -52165.984375,
					['name'] = 'Crew Home 2',
				},
				[6] = {
					['y'] = 706074.125,
					['x'] = -52277.8671875,
					['name'] = 'Officers Club',
				},
				[12] = {
					['y'] = 705799.25,
					['x'] = -51905.54296875,
					['name'] = 'Main Hangar 1',
				},
				[13] = {
					['y'] = 705462,
					['x'] = -51691.8046875,
					['name'] = 'Main Hangar 2',
				},
				[7] = {
					['y'] = 706088.5,
					['x'] = -52337.421875,
					['name'] = 'Crew club',
				},
				[14] = {
					['y'] = 706042.6875,
					['x'] = -51936.640625,
					['name'] = 'Main Hangar 3',
				},
				[15] = {
					['y'] = 707823.8125,
					['x'] = -51419.0859375,
					['name'] = 'Deported Repair Hangar 1',
				},
			},
			['picture'] = {
				[1] = 'Mineralnye-Vody_Airbase.png',
			},
			['ATO'] = true,
			['y'] = 706477.22794118,
			['x'] = -51956.542738971,
			['firepower'] = {
				['min'] = 4,
				['max'] = 8,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 2,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Structure',
			}
		},
		['209 SA-11 Site R-3'] = {
			['elements'] = {
				[1] = {
					['name'] = '209 SA-11 Site R-3-1',
				},
				[2] = {
					['name'] = '209 SA-11 Site R-3-2',
				},
				[3] = {
					['name'] = '209 SA-11 Site R-3-3',
				},
				[4] = {
					['name'] = '209 SA-11 Site R-3-4',
				},
				[5] = {
					['name'] = '209 SA-11 Site R-3-5',
				},
				[6] = {
					['name'] = '209 SA-11 Site R-3-6',
				},
				[7] = {
					['name'] = '209 SA-11 Site R-3-7',
				},
				[8] = {
					['name'] = '209 SA-11 Site R-3-8',
				},
				[9] = {
					['name'] = '209 SA-11 Site R-3-9',
				},
				[10] = {
					['name'] = '209 SA-11 Site R-3-10',
				},
				[11] = {
					['name'] = '209 SA-11 Site R-3-11',
				},
				[12] = {
					['name'] = '209 SA-11 Site R-3-12',
				},
			},
			['groupId'] = 424,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 845506.11025898,
			['x'] = -83928.376679949,
			['firepower'] = {
				['min'] = 2,
				['max'] = 8,
			},
			['dead_last'] = 0,
			['name'] = '209 SA-11 Site R-3',
			['priority'] = 6,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'SAM',
			},
		},
		['104 SA-11 Site E-4'] = {
			['elements'] = {
				[1] = {
					['name'] = '104 SA-11 Site E-4-1',
				},
				[2] = {
					['name'] = '104 SA-11 Site E-4-2',
				},
				[3] = {
					['name'] = '104 SA-11 Site E-4-3',
				},
				[4] = {
					['name'] = '104 SA-11 Site E-4-4',
				},
				[5] = {
					['name'] = '104 SA-11 Site E-4-5',
				},
				[6] = {
					['name'] = '104 SA-11 Site E-4-6',
				},
				[7] = {
					['name'] = '104 SA-11 Site E-4-7',
				},
				[8] = {
					['name'] = '104 SA-11 Site E-4-8',
				},
				[9] = {
					['name'] = '104 SA-11 Site E-4-9',
				},
				[10] = {
					['name'] = '104 SA-11 Site E-4-10',
				},
				[11] = {
					['name'] = '104 SA-11 Site E-4-11',
				},
				[12] = {
					['name'] = '104 SA-11 Site E-4-12',
				},
			},
			['groupId'] = 423,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 842716.62772461,
			['x'] = -152303.98677198,
			['firepower'] = {
				['min'] = 2,
				['max'] = 6,
			},
			['dead_last'] = 0,
			['name'] = '104 SA-11 Site E-4',
			['priority'] = 6,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'SAM',
			},
		},
		['Vaziani Alert'] = {
			['radius'] = 200000,
			['ATO'] = true,
			['inactive'] = false,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['attributes'] = {
			},
			['priority'] = 10,
			['base'] = 'Vaziani',
			['task'] = 'Intercept',
		},
		['Sweep East'] = {
			['text'] = 'in the east front area',
			['ATO'] = true,
			['y'] = 888342,
			['x'] = -129150,
			['firepower'] = {
				['min'] = 4,
				['max'] = 4,
			},
			['priority'] = 1,
			['task'] = 'Fighter Sweep',
			['attributes'] = {
			},
		},
		['CAP Kutaisi'] = {
			['radius'] = 50000,
			['refpoint'] = 'CAP Kutaisi',
			['text'] = 'North of Kutaisi',
			['ATO'] = true,
			['y'] = 709042.54974514,
			['x'] = -254908.91653356,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['priority'] = 20,
			['task'] = 'CAP',
			['attributes'] = {
				[1] = 'Air Forces',
			},
		},
		['Sweep Center'] = {
			['text'] = 'in the center front area',
			['ATO'] = true,
			['y'] = 852489,
			['x'] = -165988,
			['firepower'] = {
				['min'] = 4,
				['max'] = 4,
			},
			['priority'] = 1,
			['task'] = 'Fighter Sweep',
			['attributes'] = {
			},
		},
		['101 SA-11 Site E-1'] = {
			['elements'] = {
				[1] = {
					['name'] = '101 SA-11 Site E-1',
				},
				[2] = {
					['name'] = '101 SA-11 Site E-1-2',
				},
				[3] = {
					['name'] = '101 SA-11 Site E-1-3',
				},
				[4] = {
					['name'] = '101 SA-11 Site E-1-4',
				},
				[5] = {
					['name'] = '101 SA-11 Site E-1-5',
				},
				[6] = {
					['name'] = '101 SA-11 Site E-1-6',
				},
				[7] = {
					['name'] = '101 SA-11 Site E-1-7',
				},
				[8] = {
					['name'] = '101 SA-11 Site E-1-8',
				},
				[9] = {
					['name'] = '101 SA-11 Site E-1-9',
				},
				[10] = {
					['name'] = '101 SA-11 Site E-1-10',
				},
				[11] = {
					['name'] = '101 SA-11 Site E-1-11',
				},
				[12] = {
					['name'] = '101 SA-11 Site E-1-12',
				},
			},
			['groupId'] = 421,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 903620.61498002,
			['x'] = -138641.86587154,
			['firepower'] = {
				['min'] = 2,
				['max'] = 6,
			},
			['dead_last'] = 0,
			['name'] = '101 SA-11 Site E-1',
			['priority'] = 6,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'SAM',
			},
		},
		['Prohladniy Depot MP 24'] = {
			['elements'] = {
				[27] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot container 20',
					['groupId'] = 256,
				},
				[2] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot 2',
					['groupId'] = 220,
				},
				[3] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot 3',
					['groupId'] = 219,
				},
				[4] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot 4',
					['groupId'] = 223,
				},
				[5] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot 5',
					['groupId'] = 224,
				},
				[6] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot 6',
					['groupId'] = 225,
				},
				[7] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot Railway station',
					['groupId'] = 222,
				},
				[8] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot container 1',
					['groupId'] = 226,
				},
				[10] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot container 3',
					['groupId'] = 239,
				},
				[12] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot container 5',
					['groupId'] = 241,
				},
				[14] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot container 7',
					['groupId'] = 243,
				},
				[16] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot container 9',
					['groupId'] = 245,
				},
				[20] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot container 13',
					['groupId'] = 249,
				},
				[24] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot container 17',
					['groupId'] = 253,
				},
				[28] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot Fuel tank 1',
					['groupId'] = 257,
				},
				[32] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot Fuel tank 5',
					['groupId'] = 261,
				},
				[33] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot Fuel tank 6',
					['groupId'] = 262,
				},
				[17] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot container 10',
					['groupId'] = 246,
				},
				[21] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot container 14',
					['groupId'] = 250,
				},
				[25] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot container 18',
					['groupId'] = 254,
				},
				[29] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot Fuel tank 2',
					['groupId'] = 258,
				},
				[34] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot Fuel tank 7',
					['groupId'] = 263,
				},
				[9] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot container 2',
					['groupId'] = 238,
				},
				[11] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot container 4',
					['groupId'] = 240,
				},
				[13] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot container 6',
					['groupId'] = 242,
				},
				[15] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot container 8',
					['groupId'] = 244,
				},
				[18] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot container 11',
					['groupId'] = 247,
				},
				[22] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot container 15',
					['groupId'] = 251,
				},
				[26] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot container 19',
					['groupId'] = 255,
				},
				[30] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot Fuel tank 3',
					['groupId'] = 259,
				},
				[36] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot Fuel tank 9',
					['groupId'] = 265,
				},
				[37] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot Fuel tank 10',
					['groupId'] = 266,
				},
				[31] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot Fuel tank 4',
					['groupId'] = 260,
				},
				[1] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot 1',
					['groupId'] = 221,
				},
				[19] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot container 12',
					['groupId'] = 248,
				},
				[23] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot container 16',
					['groupId'] = 252,
				},
				[35] = {
					['foundOobGround'] = true,
					['name'] = 'Prohladniy Depot Fuel tank 8',
					['groupId'] = 264,
				},
			},
			['picture'] = {
				[1] = 'Prohladniy_Depot.png',
			},
			['class'] = 'static',
			['ATO'] = true,
			['foundOobGround'] = true,
			['y'] = 790939.06271041,
			['x'] = -94335.530200779,
			['attributes'] = {
				[1] = 'soft',
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 2,
			['task'] = 'Strike',
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			}
		},
		['501 5th Artillery Division/1.Btry'] = {
			['elements'] = {
				[1] = {
					['name'] = 'BM-27 Uragan #1',
				},
				[2] = {
					['name'] = 'BM-27 Uragan #2',
				},
				[3] = {
					['name'] = 'BM-27 Uragan #3',
				},
				[4] = {
					['name'] = 'BM-27 Uragan #4',
				},
				[5] = {
					['name'] = 'BM-27 Uragan #5',
				},
				[6] = {
					['name'] = 'BM-27 Uragan #6',
				},
				[7] = {
					['name'] = 'MTLB-U 1./Btry CP',
				},
			},
			['groupId'] = 95,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 847995.06057145,
			['x'] = -152508.20428572,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['name'] = '501 5th Artillery Division/1.Btry',
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'soft',
			},
		},
		['Bridge Alagir MN 36'] = {
			['elements'] = {
				[1] = {
					['y'] = 815939.25,
					['x'] = -173099.3125,
					['name'] = 'Bridge Alagir',
				},
			},
			['picture'] = {
				[1] = 'Alagir_Bridge.png',
			},
			['ATO'] = true,
			['y'] = 815939.25,
			['x'] = -173099.3125,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 3,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Mission Support Tanker'] = {
			['slaved'] = {
				[1] = 'CVN-71 Theodore Roosevelt',
				[2] = 330,
				[3] = 35000,
			},
			['text'] = '',
			['ATO'] = true,
			['y'] = 523310,
			['x'] = -270013.11086754,
			['firepower'] = {
				['min'] = 1,
				['max'] = 1,
			},
			['priority'] = 10,
			['task'] = 'Refueling',
			['attributes'] = {
				[1] = 'medium',
			},
		},
		['Nalchik airbase OCA Strike'] = {
			['class'] = 'airbase',
			['ATO'] = true,
			['unit'] = {
				['number'] = 4,
				['type'] = 'A-50',
				['name'] = '2457 SDRLO',
			},
			['y'] = 760428.0733062,
			['x'] = -124921.90954665,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['foundOobGround'] = true,
			['name'] = 'Nalchik',
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Parked Aircraft',
			},
		},
		['Russian Convoy 2'] = {
			['elements'] = {
				[1] = {
					['name'] = 'Russian Convoy 1-1-1',
				},
				[2] = {
					['name'] = 'Russian Convoy 1-1-2',
				},
				[3] = {
					['name'] = 'Russian Convoy 1-1-3',
				},
				[4] = {
					['name'] = 'Russian Convoy 1-1-4',
				},
				[5] = {
					['name'] = 'Russian Convoy 1-1-5',
				},
				[6] = {
					['name'] = 'Russian Convoy 1-1-6',
				},
				[7] = {
					['name'] = 'Russian Convoy 1-1-7',
				},
				[8] = {
					['name'] = 'Russian Convoy 1-1-8',
				},
				[9] = {
					['name'] = 'Russian Convoy 1-1-9',
				},
				[10] = {
					['name'] = 'Russian Convoy 1-1-10',
				},
				[11] = {
					['name'] = 'Russian Convoy 1-1-11',
				},
				[12] = {
					['name'] = 'Russian Convoy 1-1-12',
				},
				[13] = {
					['name'] = 'Russian Convoy 1-1-13',
				},
				[14] = {
					['name'] = 'Russian Convoy 1-1-14',
				},
			},
			['groupId'] = 416,
			['foundOobGround'] = true,
			['class'] = 'ship',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 329183,
			['x'] = -167663,
			['firepower'] = {
				['min'] = 6,
				['max'] = 12,
			},
			['dead_last'] = 0,
			['name'] = 'Russian Convoy 2',
			['priority'] = 1,
			['task'] = 'Anti-ship Strike',
			['attributes'] = {
				[1] = 'ship',
			},
		},
		['Bridge South Beslan MN 68'] = {
			['elements'] = {
				[1] = {
					['y'] = 835949.02734375,
					['x'] = -151580.80078125,
					['name'] = 'Bridge north bank South Beslan',
				},
				[2] = {
					['y'] = 836013.34375,
					['x'] = -151456.44921875,
					['name'] = 'Bridge south bank South Beslan',
				},
			},
			['picture'] = {
				[1] = 'Beslan_Bridge.png',
			},
			['ATO'] = true,
			['y'] = 835981.18554688,
			['x'] = -151518.625,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 3,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Rail Bridge SE Mayskiy MP 23'] = {
			['elements'] = {
				[1] = {
					['y'] = 795963.7109375,
					['x'] = -111785.2421875,
					['name'] = 'Rail Bridge right bank SE Mayskiy',
				},
				[2] = {
					['y'] = 795881.91699219,
					['x'] = -111727.7109375,
					['name'] = 'Rail Bridge Center SE Mayskiy',
				},
				[3] = {
					['y'] = 795800.12207031,
					['x'] = -111670.1796875,
					['name'] = 'Rail Bridge left bank SE Mayskiy',
				},
			},
			['picture'] = {
				[1] = 'Mayskiy_Rail_Bridge.png',
			},
			['ATO'] = true,
			['y'] = 795881.91666667,
			['x'] = -111727.7109375,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 3,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Bridge South Elhotovo MN 39'] = {
			['elements'] = {
				[1] = {
					['y'] = 809993.75585938,
					['x'] = -140288.05761719,
					['name'] = 'Bridge north bank South Elhotovo',
				},
				[2] = {
					['y'] = 810098.49414063,
					['x'] = -140195.16113281,
					['name'] = 'Bridge south bank South Elhotovo',
				},
			},
			['picture'] = {
				[1] = 'Elhotovo_Bridge.png',
			},
			['ATO'] = true,
			['y'] = 810046.12500001,
			['x'] = -140241.609375,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 3,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['407 8th Army ELINT Station'] = {
			['elements'] = {
				[2] = {
					['foundOobGround'] = true,
					['name'] = 'ELINT Antenna Truck 2',
					['groupId'] = 105,
				},
				[3] = {
					['foundOobGround'] = true,
					['name'] = 'ELINT Crew Van',
					['groupId'] = 107,
				},
				[1] = {
					['foundOobGround'] = true,
					['name'] = 'ELINT Antenna Truck 1',
					['groupId'] = 104,
				},
				[4] = {
					['foundOobGround'] = true,
					['name'] = 'ELINT Equipment Van',
					['groupId'] = 108,
				},
				[5] = {
					['foundOobGround'] = true,
					['name'] = 'ELINT Generator Truck',
					['groupId'] = 106,
				},
			},
			['picture'] = {
				[1] = 'ElintStationIntel.png',
			},
			['class'] = 'static',
			['ATO'] = true,
			['foundOobGround'] = true,
			['y'] = 844145.20000006,
			['x'] = -203621.71428574,
			['attributes'] = {
				[1] = 'soft',
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 6,
			['task'] = 'Strike',
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
		},
		['Kutaisi Alert 100'] = {
			['radius'] = 100000,
			['ATO'] = true,
			['inactive'] = false,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['attributes'] = {
			},
			['priority'] = 10,
			['base'] = 'Kutaisi',
			['task'] = 'Intercept',
		},
		['503 5th Artillery Division/3.Btry'] = {
			['elements'] = {
				[1] = {
					['name'] = 'BM-27 Uragan #13',
				},
				[2] = {
					['name'] = 'BM-27 Uragan #14',
				},
				[3] = {
					['name'] = 'BM-27 Uragan #15',
				},
				[4] = {
					['name'] = 'BM-27 Uragan #16',
				},
				[5] = {
					['name'] = 'BM-27 Uragan #17',
				},
				[6] = {
					['name'] = 'BM-27 Uragan #18',
				},
				[7] = {
					['name'] = 'MTLB-U 3./Btry CP',
				},
			},
			['groupId'] = 97,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 833359.93142858,
			['x'] = -152114.38857143,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['name'] = '503 5th Artillery Division/3.Btry',
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'soft',
			},
		},
		['CVN-71 Theodore Roosevelt Alert'] = {
			['radius'] = 250000,
			['attributes'] = {
			},
			['ATO'] = true,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['priority'] = 10,
			['base'] = 'CVN-71 Theodore Roosevelt',
			['task'] = 'Intercept',
		},
		['Rail Bridge Digora MN 38'] = {
			['elements'] = {
				[1] = {
					['y'] = 809730.375,
					['x'] = -157146.546875,
					['name'] = 'Rail Bridge Digora MN 38',
				},
			},
			['picture'] = {
				[1] = 'Digora_Rail_Bridge.png',
			},
			['ATO'] = true,
			['y'] = 809730.375,
			['x'] = -157146.546875,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 3,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Bridge Vladikavkaz MN 76'] = {
			['elements'] = {
				[1] = {
					['y'] = 850781.9375,
					['x'] = -165689.171875,
					['name'] = 'Bridge Vladikavkaz MN 76',
				},
			},
			['picture'] = {
				[1] = 'Vladikavkaz_Bridge.png',
			},
			['ATO'] = true,
			['y'] = 850781.9375,
			['x'] = -165689.171875,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 3,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Rail Bridge SW Kardzhin MN 49'] = {
			['elements'] = {
				[1] = {
					['y'] = 814533.16210938,
					['x'] = -145428.47167969,
					['name'] = 'Rail Bridge right bank SW Kardzhin',
				},
				[2] = {
					['y'] = 814618.83789063,
					['x'] = -145376.90332031,
					['name'] = 'Rail Bridge left bank SW Kardzhin',
				},
			},
			['picture'] = {
				[1] = 'Kardzhin_Bridges.png',
			},
			['ATO'] = true,
			['y'] = 814576.00000001,
			['x'] = -145402.6875,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 3,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Bridge SW Kardzhin MN 49'] = {
			['elements'] = {
				[1] = {
					['y'] = 815400.75,
					['x'] = -145416.77636719,
					['name'] = 'Bridge north bank SW Kardzhin',
				},
				[2] = {
					['y'] = 815425,
					['x'] = -145554.66015625,
					['name'] = 'Bridge south bank SW Kardzhin',
				},
			},
			['picture'] = {
				[1] = 'Kardzhin_Bridges.png',
			},
			['ATO'] = true,
			['y'] = 815412.875,
			['x'] = -145485.71826172,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 3,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Battle Group AEW'] = {
			['slaved'] = {
				[1] = 'CVN-71 Theodore Roosevelt',
				[2] = 320,
				[3] = 40000,
			},
			['text'] = '',
			['ATO'] = true,
			['y'] = 515098.49561254,
			['x'] = -269682.22227524,
			['firepower'] = {
				['min'] = 1,
				['max'] = 1,
			},
			['priority'] = 10,
			['task'] = 'AWACS',
			['attributes'] = {
				[1] = 'AEW',
			},
		},
		['FARP Vladikavkaz - MN76'] = {
			['elements'] = {
				[1] = {
					['foundOobGround'] = true,
					['name'] = 'FARP 1 - Hind 1',
					['groupId'] = 176,
				},
				[2] = {
					['foundOobGround'] = true,
					['name'] = 'FARP 1 - Hind 2',
					['groupId'] = 175,
				},
				[4] = {
					['foundOobGround'] = true,
					['name'] = 'FARP 1 - Hip 1',
					['groupId'] = 178,
				},
				[8] = {
					['foundOobGround'] = true,
					['name'] = 'FARP 1 - Hip 5',
					['groupId'] = 183,
				},
				[16] = {
					['foundOobGround'] = true,
					['name'] = 'FARP 1 - Crew Tent 1',
					['groupId'] = 198,
				},
				[17] = {
					['foundOobGround'] = true,
					['name'] = 'FARP 1 - Crew Tent 2',
					['groupId'] = 199,
				},
				[9] = {
					['foundOobGround'] = true,
					['name'] = 'FARP 1 - Ammo depot 1',
					['groupId'] = 171,
				},
				[18] = {
					['foundOobGround'] = true,
					['name'] = 'FARP 1 - Crew Tent 3',
					['groupId'] = 200,
				},
				[5] = {
					['foundOobGround'] = true,
					['name'] = 'FARP 1 - Hip 2',
					['groupId'] = 177,
				},
				[10] = {
					['foundOobGround'] = true,
					['name'] = 'FARP 1 - Ammo depot 2',
					['groupId'] = 185,
				},
				[11] = {
					['foundOobGround'] = true,
					['name'] = 'FARP 1 - Ammo depot 3',
					['groupId'] = 172,
				},
				[3] = {
					['foundOobGround'] = true,
					['name'] = 'FARP 1 - Hind 3',
					['groupId'] = 180,
				},
				[6] = {
					['foundOobGround'] = true,
					['name'] = 'FARP 1 - Hip 3',
					['groupId'] = 181,
				},
				[12] = {
					['foundOobGround'] = true,
					['name'] = 'FARP 1 - Fuel depot 1',
					['groupId'] = 173,
				},
				[13] = {
					['foundOobGround'] = true,
					['name'] = 'FARP 1 - Fuel depot 2',
					['groupId'] = 184,
				},
				[7] = {
					['foundOobGround'] = true,
					['name'] = 'FARP 1 - Hip 4',
					['groupId'] = 182,
				},
				[14] = {
					['foundOobGround'] = true,
					['name'] = 'FARP 1 - Fuel depot 3',
					['groupId'] = 174,
				},
				[15] = {
					['foundOobGround'] = true,
					['name'] = 'FARP 1 - Crew house',
					['groupId'] = 197,
				},
			},
			['picture'] = {
				[1] = 'FARP_Vladikavkaz.png',
			},
			['class'] = 'static',
			['ATO'] = true,
			['foundOobGround'] = true,
			['y'] = 849272.35228571,
			['x'] = -163311.9991111,
			['attributes'] = {
				[1] = 'soft',
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 2,
			['task'] = 'Strike',
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
		},
	},
	['red'] = {
		['Novyy Afon Train Station - FH57'] = {
			['elements'] = {
				[1] = {
					['y'] = 538777.375,
					['x'] = -198444.3125,
					['name'] = 'Novyy Afon Train Station Hangar 1',
				},
				[2] = {
					['y'] = 538722.25,
					['x'] = -198418.21875,
					['name'] = 'Novyy Afon Train Station Hangar 2',
				},
				[4] = {
					['y'] = 538803.25,
					['x'] = -198378.46875,
					['name'] = 'Novyy Afon Train Station Hangar 4',
				},
				[3] = {
					['y'] = 538764.75,
					['x'] = -198356.1875,
					['name'] = 'Novyy Afon Train Station Hangar 3',
				},
			},
			['picture'] = {
				[1] = 'Novyy Afon Train Station.png',
			},
			['ATO'] = true,
			['y'] = 538766.90625,
			['x'] = -198399.296875,
			['firepower'] = {
				['min'] = 4,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Structure',
			},
		},
		['Bridge Nizh Armyanskoe Uschele-FH47'] = {
			['elements'] = {
				[1] = {
					['y'] = 535057.125,
					['x'] = -198238.734375,
					['name'] = 'Bridge Nizh Armyanskoe Uschele-FH47',
				},
			},
			['picture'] = {
				[1] = 'Bridge Positions FH37-FH47-FH56-FH66.png',
			},
			['ATO'] = true,
			['y'] = 535057.125,
			['x'] = -198238.734375,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['CAP Beslan'] = {
			['radius'] = 50000,
			['refpoint'] = 'CAP Beslan',
			['text'] = 'South West Beslan',
			['ATO'] = true,
			['y'] = 874135.99956653,
			['inactive'] = true,
			['attributes'] = {
				[1] = '',
			},
			['x'] = -150875.19661469,
			['priority'] = 5,
			['task'] = 'CAP',
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
		},
		['Bridge Tagrskiy-FH08'] = {
			['elements'] = {
				[1] = {
					['y'] = 493199.7578125,
					['x'] = -189757.84765625,
					['name'] = 'Bridge Tagrskiy-FH08',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions FH08-FH18-FH28-FH27.png',
			},
			['ATO'] = true,
			['y'] = 493199.7578125,
			['x'] = -189757.84765625,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Bridge Anaklia-GG19'] = {
			['elements'] = {
				[1] = {
					['y'] = 606642.265625,
					['x'] = -267377.86865234,
					['name'] = 'Bridge Anaklia North part-GG19',
				},
				[2] = {
					['y'] = 606664.90625,
					['x'] = -267516.02490234,
					['name'] = 'Bridge Anaklia South part-GG19',
				},
			},
			['picture'] = {
				[1] = 'Bridge positions GG19-GH10-GH20-GH21-GH31-GH42.png',
			},
			['ATO'] = true,
			['y'] = 606653.5859375,
			['x'] = -267446.94677734,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 2,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['EWR-1 Site'] = {
			['elements'] = {
				[1] = {
					['name'] = 'Unit #267',
				},
				[2] = {
					['name'] = 'Unit #268',
				},
			},
			['groupId'] = 380,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 607800.50910075,
			['x'] = -217638.71488428,
			['firepower'] = {
				['min'] = 4,
				['max'] = 8,
			},
			['dead_last'] = 0,
			['name'] = 'EWR-1',
			['priority'] = 6,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'soft',
			},
		},
		['CAP AWACS'] = {
			['radius'] = 50000,
			['refpoint'] = 'CAP-AWACS',
			['text'] = 'south AWACS',
			['ATO'] = true,
			['y'] = 799179.81432139,
			['inactive'] = false,
			['attributes'] = {
				[1] = '',
			},
			['x'] = -67528.423782838,
			['priority'] = 10,
			['task'] = 'CAP',
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
		},
		['Bridge Rike-GH31'] = {
			['elements'] = {
				[1] = {
					['y'] = 626855.359375,
					['x'] = -245409.5234375,
					['name'] = 'Bridge Rike West part-GH31',
				},
				[2] = {
					['y'] = 626983.703125,
					['x'] = -245465.4453125,
					['name'] = 'Bridge Rike Center West part-GH31',
				},
				[4] = {
					['y'] = 627240.390625,
					['x'] = -245577.2890625,
					['name'] = 'Bridge Rike East part-GH31',
				},
				[3] = {
					['y'] = 627112.046875,
					['x'] = -245521.3671875,
					['name'] = 'Bridge Rike Center East part-GH31',
				},
			},
			['picture'] = {
				[1] = 'Bridge positions GG19-GH10-GH20-GH21-GH31-GH42.png',
			},
			['ATO'] = true,
			['y'] = 627047.875,
			['x'] = -245493.40625,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 4,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Bridge Vartsihe-LM16'] = {
			['elements'] = {
				[1] = {
					['y'] = 702893.90625,
					['x'] = -285269.1875,
					['name'] = 'Bridge Vartsihe West part-LM16',
				},
				[2] = {
					['y'] = 703014.46484375,
					['x'] = -285340.36523438,
					['name'] = 'Bridge Vartsihe Center West part-LM16',
				},
				[4] = {
					['y'] = 703255.578125,
					['x'] = -285482.71875,
					['name'] = 'Bridge Vartsihe East part-LM16',
				},
				[3] = {
					['y'] = 703135.01953125,
					['x'] = -285411.54101563,
					['name'] = 'Bridge Vartsihe Center East part-LM16',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions LM16-LM17-LM18.png',
			},
			['ATO'] = true,
			['y'] = 703074.7421875,
			['x'] = -285375.953125,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 3,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['AWACS'] = {
			['radius'] = 15000,
			['refpoint'] = 'AWACS-RED',
			['text'] = '',
			['ATO'] = true,
			['y'] = 800169.7911155,
			['x'] = -51193.806680015,
			['firepower'] = {
				['min'] = 1,
				['max'] = 1,
			},
			['priority'] = 10,
			['task'] = 'AWACS',
			['attributes'] = {
				[1] = '',
			},
		},
		['Kobuleti Train Station - GG44'] = {
			['elements'] = {
				[6] = {
					['y'] = 638495.125,
					['x'] = -316335.1875,
					['name'] = 'Kobuleti Train Station Hangar 6',
				},
				[2] = {
					['y'] = 638212.02636719,
					['x'] = -316280.92919922,
					['name'] = 'Kobuleti Train Station Hangar 2',
				},
				[3] = {
					['y'] = 638238.39453125,
					['x'] = -316282.33740234,
					['name'] = 'Kobuleti Train Station Hangar 3',
				},
				[1] = {
					['y'] = 638171.36035156,
					['x'] = -316275.96289063,
					['name'] = 'Kobuleti Train Station Hangar 1',
				},
				[4] = {
					['y'] = 638260.47753906,
					['x'] = -316283.07177734,
					['name'] = 'Kobuleti Train Station Hangar 4',
				},
				[5] = {
					['y'] = 638392.6875,
					['x'] = -316336.25,
					['name'] = 'Kobuleti Train Station Hangar 5',
				},
				[7] = {
					['y'] = 638439.0625,
					['x'] = -316337,
					['name'] = 'Kobuleti Train Station Hangar 7',
				},
			},
			['picture'] = {
				[1] = ' Kobuleti Train Station.png',
			},
			['ATO'] = true,
			['y'] = 638315.59054129,
			['x'] = -316304.39125279,
			['firepower'] = {
				['min'] = 4,
				['max'] = 6,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 3,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Structure',
			},
		},
		['Nalchik Alert 200 Km'] = {
			['radius'] = 200000,
			['attributes'] = {
			},
			['ATO'] = true,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['priority'] = 4,
			['base'] = 'Nalchik',
			['task'] = 'Intercept',
		},
		['Bridge Orsantia-GH10'] = {
			['elements'] = {
				[1] = {
					['y'] = 612201.3203125,
					['x'] = -260460.296875,
					['name'] = 'Bridge Orsantia East part-GH10',
				},
				[2] = {
					['y'] = 612061.3671875,
					['x'] = -260463.796875,
					['name'] = 'Bridge Orsantia West part-GH10',
				},
			},
			['picture'] = {
				[1] = 'Bridge positions GG19-GH10-GH20-GH21-GH31-GH42.png',
			},
			['ATO'] = true,
			['y'] = 612131.34375,
			['x'] = -260462.046875,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 2,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['TF-71'] = {
			['elements'] = {
				[1] = {
					['name'] = 'CVN-71 Theodore Roosevelt',
				},
				[2] = {
					['name'] = 'CG-60 Ticonderoga',
				},
				[3] = {
					['name'] = 'DDG-101 Gridley',
				},
				[4] = {
					['name'] = 'FFG-52 Carr',
				},
				[5] = {
					['name'] = 'FFG-55 Elrod',
				},
				[6] = {
					['name'] = 'FFG-54 Ford',
				},
				[7] = {
					['name'] = 'TF-71-1',
				},
			},
			['groupId'] = 293,
			['foundOobGround'] = true,
			['class'] = 'ship',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 540810,
			['x'] = -300324,
			['firepower'] = {
				['min'] = 6,
				['max'] = 12,
			},
			['dead_last'] = 0,
			['name'] = 'TF-71',
			['priority'] = 1,
			['task'] = 'Anti-ship Strike',
			['attributes'] = {
				[1] = 'ship',
			},
		},
		['LHA-Group'] = {
			['elements'] = {
				[1] = {
					['name'] = 'LHA_Tarawa',
				},
				[2] = {
					['name'] = 'FFG-48 Vandergrift',
				},
				[3] = {
					['name'] = 'FFG-46 Rentz',
				},
				[4] = {
					['name'] = 'DDG-116 Thomas Hudner',
				},
				[5] = {
					['name'] = 'CG-69 Viksburg',
				},
				[6] = {
					['name'] = 'FFG-57 Reuben James',
				},
				[7] = {
					['name'] = 'LHA-Group-1',
				},
			},
			['groupId'] = 294,
			['foundOobGround'] = true,
			['class'] = 'ship',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 512085,
			['x'] = -217166,
			['firepower'] = {
				['min'] = 6,
				['max'] = 12,
			},
			['dead_last'] = 0,
			['name'] = 'LHA-Group',
			['priority'] = 1,
			['task'] = 'Anti-ship Strike',
			['attributes'] = {
				[1] = 'ship',
			},
		},
		['NATO Convoy 1'] = {
			['elements'] = {
				[1] = {
					['name'] = 'NATO Convoy 1-1-1',
				},
				[2] = {
					['name'] = 'NATO Convoy 1-1-2',
				},
				[3] = {
					['name'] = 'NATO Convoy 1-1',
				},
				[4] = {
					['name'] = 'NATO Convoy 1-2',
				},
				[5] = {
					['name'] = 'NATO Convoy 1-3',
				},
				[6] = {
					['name'] = 'NATO Convoy 1-4',
				},
				[7] = {
					['name'] = 'NATO Convoy 1-5',
				},
				[8] = {
					['name'] = 'NATO Convoy 1-6',
				},
				[9] = {
					['name'] = 'NATO Convoy 1-7',
				},
				[10] = {
					['name'] = 'NATO Convoy 1-8',
				},
			},
			['groupId'] = 418,
			['foundOobGround'] = true,
			['class'] = 'ship',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 535454,
			['x'] = -349349,
			['firepower'] = {
				['min'] = 6,
				['max'] = 12,
			},
			['dead_last'] = 0,
			['name'] = 'NATO Convoy 1',
			['priority'] = 1,
			['task'] = 'Anti-ship Strike',
			['attributes'] = {
				[1] = 'ship',
			},
		},
		['Patriot Site West'] = {
			['elements'] = {
				[1] = {
					['name'] = 'Patriot Site West-1-1',
				},
				[2] = {
					['name'] = 'Patriot Site West-2',
				},
				[3] = {
					['name'] = 'Patriot Site West-3',
				},
				[4] = {
					['name'] = 'Patriot Site West-4',
				},
				[5] = {
					['name'] = 'Patriot Site West-5',
				},
				[6] = {
					['name'] = 'Patriot Site West-6',
				},
				[7] = {
					['name'] = 'Patriot Site West-7',
				},
				[8] = {
					['name'] = 'Patriot Site West-8',
				},
				[9] = {
					['name'] = 'Patriot Site West-9',
				},
				[10] = {
					['name'] = 'Patriot Site West-10',
				},
				[11] = {
					['name'] = 'Patriot Site West-11',
				},
			},
			['groupId'] = 432,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 668812.63278446,
			['x'] = -282723.10534374,
			['firepower'] = {
				['min'] = 4,
				['max'] = 8,
			},
			['dead_last'] = 0,
			['name'] = 'Patriot Site West',
			['priority'] = 2,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'SAM',
			},
		},
		['Bridge Primorskoe-FH37'] = {
			['elements'] = {
				[1] = {
					['y'] = 526178.4375,
					['x'] = -198076.4375,
					['name'] = 'Bridge Primorskoe-FH37',
				},
			},
			['picture'] = {
				[1] = 'Bridge Positions FH37-FH47-FH56-FH66.png',
			},
			['ATO'] = true,
			['y'] = 526178.4375,
			['x'] = -198076.4375,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['17 1st Artillery Division/7.Btry'] = {
			['elements'] = {
				[1] = {
					['name'] = 'Unit #129',
				},
				[2] = {
					['name'] = 'Unit #130',
				},
				[3] = {
					['name'] = 'Unit #131',
				},
				[4] = {
					['name'] = 'Unit #132',
				},
				[5] = {
					['name'] = 'Unit #133',
				},
				[6] = {
					['name'] = 'Unit #134',
				},
				[7] = {
					['name'] = 'Unit #135',
				},
			},
			['groupId'] = 159,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 824611.88228577,
			['x'] = -292906.74285713,
			['firepower'] = {
				['min'] = 4,
				['max'] = 6,
			},
			['dead_last'] = 0,
			['name'] = '17 1st Artillery Division/7.Btry',
			['priority'] = 4,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'soft',
			},
		},
		['Mineralnye-Vody Alert 200 Km'] = {
			['radius'] = 200000,
			['attributes'] = {
			},
			['ATO'] = true,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['priority'] = 4,
			['base'] = 'Mineralnye-Vody',
			['task'] = 'Intercept',
		},
		['Bzyb Train Station - FH18'] = {
			['elements'] = {
				[1] = {
					['y'] = 497412.5,
					['x'] = -185802.78125,
					['name'] = 'Bzyb Train Station Hangar 1',
				},
				[2] = {
					['y'] = 497473.34375,
					['x'] = -185798.53125,
					['name'] = 'Bzyb Train Station Hangar 2',
				},
				[4] = {
					['y'] = 497421.78125,
					['x'] = -185871.046875,
					['name'] = 'Bzyb Train Station Hangar 4',
				},
				[3] = {
					['y'] = 497466.28125,
					['x'] = -185871.625,
					['name'] = 'Bzyb Train Station Hangar 3',
				},
			},
			['picture'] = {
				[1] = 'Bzyb Train Station.png',
			},
			['ATO'] = true,
			['y'] = 497443.4765625,
			['x'] = -185835.99609375,
			['firepower'] = {
				['min'] = 4,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 2,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Structure',
			},
		},
		['Adzhkhahara Train Station - FH28'] = {
			['elements'] = {
				[6] = {
					['y'] = 507998.1875,
					['x'] = -186114.59375,
					['name'] = 'Adzhkhahara Train Station Hangar 6',
				},
				[2] = {
					['y'] = 508035.40625,
					['x'] = -186052.78125,
					['name'] = 'Adzhkhahara Train Station Hangar 2',
				},
				[3] = {
					['y'] = 508089.34375,
					['x'] = -186081.21875,
					['name'] = 'Adzhkhahara Train Station Hangar 3',
				},
				[1] = {
					['y'] = 508142.1875,
					['x'] = -186107.1875,
					['name'] = 'Adzhkhahara Train Station Hangar 1',
				},
				[4] = {
					['y'] = 508196.125,
					['x'] = -186135.640625,
					['name'] = 'Adzhkhahara Train Station Hangar 4',
				},
				[5] = {
					['y'] = 508070.03125,
					['x'] = -186151.65625,
					['name'] = 'Adzhkhahara Train Station Hangar 5',
				},
			},
			['picture'] = {
				[1] = 'Adzhkhahara Train Station.png',
			},
			['ATO'] = true,
			['y'] = 508088.546875,
			['x'] = -186107.1796875,
			['firepower'] = {
				['min'] = 4,
				['max'] = 6,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 2,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Structure',
			},
		},
		['CAP Mozdok'] = {
			['radius'] = 50000,
			['refpoint'] = 'CAP Mozdok',
			['text'] = 'south Mozdok',
			['ATO'] = true,
			['y'] = 836695.7313728,
			['inactive'] = true,
			['attributes'] = {
				[1] = '',
			},
			['x'] = -138093.51866269,
			['priority'] = 5,
			['task'] = 'CAP',
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
		},
		['Gumista Train Station - FH56'] = {
			['elements'] = {
				[2] = {
					['y'] = 546993,
					['x'] = -203761.8125,
					['name'] = 'Gumista Train Station Hangar 2',
				},
				[3] = {
					['y'] = 546970.57617188,
					['x'] = -203899.54248047,
					['name'] = 'Gumista Train Station Hangar 3',
				},
				[1] = {
					['y'] = 547048.4375,
					['x'] = -203787.28125,
					['name'] = 'Gumista Train Station Hangar 1',
				},
				[4] = {
					['y'] = 546904.91210938,
					['x'] = -203867.72363281,
					['name'] = 'Gumista Train Station Hangar 4',
				},
				[5] = {
					['y'] = 546948.3125,
					['x'] = -203849.30273438,
					['name'] = 'Gumista Train Station Hangar 5',
				},
			},
			['picture'] = {
				[1] = 'Gumista Train Station.png',
			},
			['ATO'] = true,
			['y'] = 546973.04765625,
			['x'] = -203833.13251953,
			['firepower'] = {
				['min'] = 4,
				['max'] = 6,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Structure',
			},
		},
		['Senaki-Kolkhi Train Station - KM58'] = {
			['elements'] = {
				[7] = {
					['y'] = 647905.97418213,
					['x'] = -278419.37255859,
					['name'] = 'Senaki-Kolkhi Train Station Fuel Tank 1',
				},
				[1] = {
					['y'] = 648014.0625,
					['x'] = -278439.875,
					['name'] = 'Senaki-Kolkhi Train Station Hangar 1',
				},
				[2] = {
					['y'] = 647955,
					['x'] = -278455.3125,
					['name'] = 'Senaki-Kolkhi Train Station Hangar 2',
				},
				[4] = {
					['y'] = 648212.17578125,
					['x'] = -278343.05957031,
					['name'] = 'Senaki-Kolkhi Train Station Hangar 4',
				},
				[8] = {
					['y'] = 647877.89447021,
					['x'] = -278418.84960938,
					['name'] = 'Senaki-Kolkhi Train Station Fuel Tank 2',
				},
				[9] = {
					['y'] = 647870.21691895,
					['x'] = -278398.14453125,
					['name'] = 'Senaki-Kolkhi Train Station Fuel Tank 3',
				},
				[5] = {
					['y'] = 648053.55078125,
					['x'] = -278502.85058594,
					['name'] = 'Senaki-Kolkhi Train Station Hangar 5',
				},
				[10] = {
					['y'] = 647898.79650879,
					['x'] = -278397.734375,
					['name'] = 'Senaki-Kolkhi Train Station Fuel Tank 4',
				},
				[3] = {
					['y'] = 648174.72851563,
					['x'] = -278521.20019531,
					['name'] = 'Senaki-Kolkhi Train Station Hangar 3',
				},
				[6] = {
					['y'] = 647975.75,
					['x'] = -278530.84375,
					['name'] = 'Senaki-Kolkhi Train Station Hangar 6',
				},
				[11] = {
					['y'] = 648182.73242188,
					['x'] = -278609.26757813,
					['name'] = 'Senaki-Kolkhi Train Station Hangar 7',
				},
			},
			['picture'] = {
				[1] = 'Senaki-Kolkhi Train Station.png',
			},
			['ATO'] = true,
			['y'] = 648010.98928001,
			['x'] = -278457.86456854,
			['firepower'] = {
				['min'] = 4,
				['max'] = 8,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 3,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Structure',
			},
		},
		['Rail Bridge Grebeshok-EH99'] = {
			['elements'] = {
				[1] = {
					['y'] = 486008.4375,
					['x'] = -175437.140625,
					['name'] = 'Rail Bridge Grebeshok-EH99',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions EJ80-EH99.png',
			},
			['ATO'] = true,
			['y'] = 486008.4375,
			['x'] = -175437.140625,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Nalchik Alert 100 Km'] = {
			['radius'] = 100000,
			['attributes'] = {
			},
			['ATO'] = true,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['priority'] = 4,
			['base'] = 'Nalchik',
			['task'] = 'Intercept',
		},
		['Bridge Tsalkoti-EJ80'] = {
			['elements'] = {
				[1] = {
					['y'] = 472735.90625,
					['x'] = -170576,
					['name'] = 'Bridge Tsalkoti-EJ80',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions EJ80-EH99.png',
			},
			['ATO'] = true,
			['y'] = 472735.90625,
			['x'] = -170576,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Mozdok Alert 200 Km'] = {
			['radius'] = 200000,
			['attributes'] = {
			},
			['ATO'] = true,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['priority'] = 4,
			['base'] = 'Mozdok',
			['task'] = 'Intercept',
		},
		['Bridge Koki-GH20'] = {
			['elements'] = {
				[1] = {
					['y'] = 616593.7421875,
					['x'] = -255475.2109375,
					['name'] = 'Bridge Koki North part-GH20',
				},
				[2] = {
					['y'] = 616673.2734375,
					['x'] = -255590.4296875,
					['name'] = 'Bridge Koki Center part-GH20',
				},
				[3] = {
					['y'] = 616752.796875,
					['x'] = -255705.6484375,
					['name'] = 'Bridge Koki South part-GH20',
				},
			},
			['picture'] = {
				[1] = 'Bridge positions GG19-GH10-GH20-GH21-GH31-GH42.png',
			},
			['ATO'] = true,
			['y'] = 616673.27083333,
			['x'] = -255590.4296875,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 2,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Rail Bridge West Gantiadi-EJ80'] = {
			['elements'] = {
				[1] = {
					['y'] = 473638.875,
					['x'] = -170473.796875,
					['name'] = 'Rail Bridge West Gantiadi-EJ80',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions EJ80-EH99.png',
			},
			['ATO'] = true,
			['y'] = 473638.875,
			['x'] = -170473.796875,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Bridge Kutaisi-LM18'] = {
			['elements'] = {
				[1] = {
					['y'] = 701001.1796875,
					['x'] = -274859.59277344,
					['name'] = 'Bridge Kutaisi West part-LM18',
				},
				[2] = {
					['y'] = 701140.4453125,
					['x'] = -274873.90722656,
					['name'] = 'Bridge Kutaisi East part-LM18',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions LM16-LM17-LM18.png',
			},
			['ATO'] = true,
			['y'] = 701070.8125,
			['x'] = -274866.75,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 2,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Bridge Kvemo-Merheuli North-FH65'] = {
			['elements'] = {
				[1] = {
					['y'] = 558366.9375,
					['x'] = -208624.78125,
					['name'] = 'Bridge Kvemo-Merheuli North-FH65',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions FH65-FH75-FH74.png',
			},
			['ATO'] = true,
			['y'] = 558366.9375,
			['x'] = -208624.78125,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Kvemo-Merheuli Train Station - FH66'] = {
			['elements'] = {
				[1] = {
					['y'] = 557894.3125,
					['x'] = -207974.40625,
					['name'] = 'Kvemo-Merheuli Train Station Hangar 1',
				},
				[2] = {
					['y'] = 557919.25,
					['x'] = -208008.9375,
					['name'] = 'Kvemo-Merheuli Train Station Hangar 2',
				},
				[4] = {
					['y'] = 557787.875,
					['x'] = -207933.375,
					['name'] = 'Kvemo-Merheuli Train Station Hangar 4',
				},
				[3] = {
					['y'] = 557755.5,
					['x'] = -207881.71875,
					['name'] = 'Kvemo-Merheuli Train Station Hangar 3',
				},
			},
			['picture'] = {
				[1] = 'Kvemo-Merheuli Train Station.png',
			},
			['ATO'] = true,
			['y'] = 557839.234375,
			['x'] = -207949.609375,
			['firepower'] = {
				['min'] = 4,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Structure',
			},
		},
		['15 1st Artillery Division/5.Btry'] = {
			['elements'] = {
				[1] = {
					['name'] = 'Unit #107',
				},
				[2] = {
					['name'] = 'Unit #108',
				},
				[3] = {
					['name'] = 'Unit #109',
				},
				[4] = {
					['name'] = 'Unit #121',
				},
				[5] = {
					['name'] = 'Unit #122',
				},
				[6] = {
					['name'] = 'Unit #123',
				},
				[7] = {
					['name'] = 'Unit #124',
				},
			},
			['groupId'] = 157,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 781437.60657145,
			['x'] = -292056.23285715,
			['firepower'] = {
				['min'] = 4,
				['max'] = 6,
			},
			['dead_last'] = 0,
			['name'] = '15 1st Artillery Division/5.Btry',
			['priority'] = 4,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'soft',
			},
		},
		['18 1st Artillery Division/8.Btry'] = {
			['elements'] = {
				[1] = {
					['name'] = 'Unit #159',
				},
				[2] = {
					['name'] = 'Unit #160',
				},
				[3] = {
					['name'] = 'Unit #161',
				},
				[4] = {
					['name'] = 'Unit #162',
				},
				[5] = {
					['name'] = 'Unit #163',
				},
				[6] = {
					['name'] = 'Unit #164',
				},
				[7] = {
					['name'] = 'Unit #165',
				},
			},
			['groupId'] = 165,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 932179.25885715,
			['x'] = -304359.74628569,
			['firepower'] = {
				['min'] = 4,
				['max'] = 6,
			},
			['dead_last'] = 0,
			['name'] = '18 1st Artillery Division/8.Btry',
			['priority'] = 4,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'soft',
			},
		},
		['CAP Mineralnye-Vody'] = {
			['radius'] = 50000,
			['refpoint'] = 'CAP Mineralnye-Vody',
			['text'] = 'south east Mineralnye-Vody',
			['ATO'] = true,
			['y'] = 732428.27214772,
			['inactive'] = true,
			['attributes'] = {
				[1] = '',
			},
			['x'] = -103048.66652807,
			['priority'] = 5,
			['task'] = 'CAP',
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
		},
		['12 1st Artillery Division/2.Btry'] = {
			['elements'] = {
				[1] = {
					['name'] = 'Unit #088',
				},
				[2] = {
					['name'] = 'Unit #089',
				},
				[3] = {
					['name'] = 'Unit #090',
				},
				[4] = {
					['name'] = 'Unit #093',
				},
				[5] = {
					['name'] = 'Unit #094',
				},
				[6] = {
					['name'] = 'Unit #095',
				},
				[7] = {
					['name'] = 'Unit #096',
				},
			},
			['groupId'] = 149,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 629740.3931429,
			['x'] = -247760.61114286,
			['firepower'] = {
				['min'] = 4,
				['max'] = 6,
			},
			['dead_last'] = 0,
			['name'] = '12 1st Artillery Division/2.Btry',
			['priority'] = 4,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'soft',
			},
		},
		['Sukhumi Airbase'] = {
			['elements'] = {
				[6] = {
					['y'] = 564393.9375,
					['x'] = -219843.78125,
					['name'] = 'Sukhumi Hangar 3',
				},
				[2] = {
					['y'] = 564007.3125,
					['x'] = -219592.921875,
					['name'] = 'Sukhumi Main Ammo Depot',
				},
				[3] = {
					['y'] = 564086.9375,
					['x'] = -219594.640625,
					['name'] = 'Sukhumi Main Fuel Depot',
				},
				[1] = {
					['y'] = 563758.0625,
					['x'] = -219668.28125,
					['name'] = 'Sukhumi Control Tower',
				},
				[4] = {
					['y'] = 564339.1875,
					['x'] = -219719.84375,
					['name'] = 'Sukhumi Hangar 1',
				},
				[5] = {
					['y'] = 564363.875,
					['x'] = -219773.015625,
					['name'] = 'Sukhumi Hangar 2',
				},
				[7] = {
					['y'] = 564065.0625,
					['x'] = -219594.296875,
					['name'] = 'Sukhumi Hangar 4',
				},
			},
			['picture'] = {
				[1] = 'Sukhumi Airbase.png',
			},
			['ATO'] = true,
			['y'] = 564144.91071429,
			['x'] = -219683.82589286,
			['firepower'] = {
				['min'] = 6,
				['max'] = 10,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 4,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Structure',
			},
		},
		['Rail Bridge Patara-Poti-GG27'] = {
			['elements'] = {
				[1] = {
					['y'] = 619140.03125,
					['x'] = -290165.734375,
					['name'] = 'Rail Bridge Patara-Poti North part-GG27',
				},
				[2] = {
					['y'] = 619083.296875,
					['x'] = -290248.08398438,
					['name'] = 'Rail Bridge Patara-Poti Center part-GG27',
				},
				[3] = {
					['y'] = 619026.5625,
					['x'] = -290330.43359375,
					['name'] = 'Rail Bridge Patara-Poti South part-GH27',
				},
			},
			['picture'] = {
				[1] = 'Bridges Positions Patara-Poti-GG27.png',
			},
			['ATO'] = true,
			['y'] = 619083.296875,
			['x'] = -290248.08398438,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 2,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['13 1st Artillery Division/3.Btry'] = {
			['elements'] = {
				[1] = {
					['name'] = 'Unit #100',
				},
				[2] = {
					['name'] = 'Unit #101',
				},
				[3] = {
					['name'] = 'Unit #102',
				},
				[4] = {
					['name'] = 'Unit #103',
				},
				[5] = {
					['name'] = 'Unit #104',
				},
				[6] = {
					['name'] = 'Unit #105',
				},
				[7] = {
					['name'] = 'Unit #106',
				},
			},
			['groupId'] = 151,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 687491.57228577,
			['x'] = -255942.71514287,
			['firepower'] = {
				['min'] = 4,
				['max'] = 6,
			},
			['dead_last'] = 0,
			['name'] = '13 1st Artillery Division/3.Btry',
			['priority'] = 4,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'soft',
			},
		},
		['Rail Bridge Kvemo-Merheuli-FH65'] = {
			['elements'] = {
				[1] = {
					['y'] = 559669.4375,
					['x'] = -210831.09375,
					['name'] = 'Rail Bridge Kvemo-Merheuli-FH65',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions FH65-FH75-FH74.png',
			},
			['ATO'] = true,
			['y'] = 559669.4375,
			['x'] = -210831.09375,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['EWR-2 Site'] = {
			['elements'] = {
				[1] = {
					['name'] = 'Unit #281',
				},
				[2] = {
					['name'] = 'Unit #282',
				},
			},
			['groupId'] = 384,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 775502.73257949,
			['x'] = -242255.46591607,
			['firepower'] = {
				['min'] = 4,
				['max'] = 8,
			},
			['dead_last'] = 0,
			['name'] = 'EWR-2',
			['priority'] = 6,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'soft',
			},
		},
		['Rail Bridge Nizh Armyanskoe Uschele-FH47'] = {
			['elements'] = {
				[1] = {
					['y'] = 535039.0625,
					['x'] = -198041.84375,
					['name'] = 'Rail Bridge Nizh Armyanskoe Uschele-FH47',
				},
			},
			['picture'] = {
				[1] = 'Bridge Positions FH37-FH47-FH56-FH66.png',
			},
			['ATO'] = true,
			['y'] = 535039.0625,
			['x'] = -198041.84375,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Bridge Pshap West-FH75'] = {
			['elements'] = {
				[1] = {
					['y'] = 563349,
					['x'] = -216871.515625,
					['name'] = 'Bridge Pshap West-FH75',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions FH65-FH75-FH74.png',
			},
			['ATO'] = true,
			['y'] = 563349,
			['x'] = -216871.515625,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Bridge Geguti-LM17'] = {
			['elements'] = {
				[1] = {
					['y'] = 704785.0078125,
					['x'] = -282606.98828125,
					['name'] = 'Bridge Geguti North part-LM17',
				},
				[2] = {
					['y'] = 704844.5,
					['x'] = -282733.71875,
					['name'] = 'Bridge Geguti Center part-LM17',
				},
				[3] = {
					['y'] = 704903.9921875,
					['x'] = -282860.44921875,
					['name'] = 'Bridge Geguti South part-LM17',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions LM16-LM17-LM18.png',
			},
			['ATO'] = true,
			['y'] = 704844.5,
			['x'] = -282733.71875,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 2,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Mozdok Alert 120 Km'] = {
			['radius'] = 120000,
			['attributes'] = {
			},
			['ATO'] = true,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['priority'] = 4,
			['base'] = 'Mozdok',
			['task'] = 'Intercept',
		},
		['Gudauta Train Station - FH37'] = {
			['elements'] = {
				[7] = {
					['y'] = 519628.59375,
					['x'] = -197040.53125,
					['name'] = 'Gudauta Train Station Hangar 7',
				},
				[1] = {
					['y'] = 519848.40625,
					['x'] = -196995.96875,
					['name'] = 'Gudauta Train Station Hangar 1',
				},
				[2] = {
					['y'] = 519787.53125,
					['x'] = -196992.15625,
					['name'] = 'Gudauta Train Station Hangar 2',
				},
				[4] = {
					['y'] = 519927.5625,
					['x'] = -196930.875,
					['name'] = 'Gudauta Train Station Hangar 4',
				},
				[8] = {
					['y'] = 519652.375,
					['x'] = -197092.82836914,
					['name'] = 'Gudauta Train Station Hangar 8',
				},
				[9] = {
					['y'] = 519671.90625,
					['x'] = -197092.82836914,
					['name'] = 'Gudauta Train Station Hangar 9',
				},
				[5] = {
					['y'] = 519718.28125,
					['x'] = -197092.15625,
					['name'] = 'Gudauta Train Station Hangar 5',
				},
				[10] = {
					['y'] = 519690.9375,
					['x'] = -197092.82836914,
					['name'] = 'Gudauta Train Station Hangar 10',
				},
				[3] = {
					['y'] = 519884.96875,
					['x'] = -196930.96875,
					['name'] = 'Gudauta Train Station Hangar 3',
				},
				[6] = {
					['y'] = 519749.53125,
					['x'] = -197092.15625,
					['name'] = 'Gudauta Train Station Hangar 6',
				},
				[11] = {
					['y'] = 519824.65625,
					['x'] = -197055.8125,
					['name'] = 'Gudauta Train Station Hangar 11',
				},
			},
			['picture'] = {
				[1] = 'Gudauta Train Station.png',
			},
			['ATO'] = true,
			['y'] = 519762.25,
			['x'] = -197037.19182795,
			['firepower'] = {
				['min'] = 6,
				['max'] = 8,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 2,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Structure',
			},
		},
		['Bridge Patara-Poti West-GG27'] = {
			['elements'] = {
				[1] = {
					['y'] = 619188.875,
					['x'] = -290212.75,
					['name'] = 'Bridge Patara-Poti West North part-GG27',
				},
				[2] = {
					['y'] = 619112.375,
					['x'] = -290330,
					['name'] = 'Bridge Patara-Poti West Center part-GG27',
				},
				[3] = {
					['y'] = 619035.875,
					['x'] = -290447.25,
					['name'] = 'Bridge Patara-Poti West South part-GH27',
				},
			},
			['picture'] = {
				[1] = 'Bridges Positions Patara-Poti-GG27.png',
			},
			['ATO'] = true,
			['y'] = 619112.375,
			['x'] = -290330,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Vaziani OCA Strike'] = {
			['class'] = 'airbase',
			['ATO'] = true,
			['unit'] = {
				['number'] = 6,
				['type'] = 'F-15E',
				['name'] = '335 TFS',
			},
			['y'] = 903150.625,
			['x'] = -319069.063,
			['firepower'] = {
				['min'] = 4,
				['max'] = 6,
			},
			['foundOobGround'] = true,
			['name'] = 'Vaziani',
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Parked Aircraft',
			},
		},
		['Kutaisi Airbase'] = {
			['elements'] = {
				[27] = {
					['y'] = 683027.0625,
					['x'] = -284263.5,
					['name'] = 'Kutaisi Hangar 2',
				},
				[2] = {
					['y'] = 683802.875,
					['x'] = -285856.6875,
					['name'] = 'Kutaisi Main Ammo Depot',
				},
				[3] = {
					['y'] = 683828.9375,
					['x'] = -285843.96875,
					['name'] = 'Kutaisi Ammo Depot 1',
				},
				[4] = {
					['y'] = 683831.5625,
					['x'] = -285853.15625,
					['name'] = 'Kutaisi Ammo Depot 2',
				},
				[5] = {
					['y'] = 683826.4375,
					['x'] = -285835,
					['name'] = 'Kutaisi Ammo Depot 3',
				},
				[6] = {
					['y'] = 683823.75,
					['x'] = -285825.78125,
					['name'] = 'Kutaisi Ammo Depot 4',
				},
				[7] = {
					['y'] = 683767.5625,
					['x'] = -285868.875,
					['name'] = 'Kutaisi Ammo Depot 5',
				},
				[8] = {
					['y'] = 683762.375,
					['x'] = -285850.71875,
					['name'] = 'Kutaisi Ammo Depot 6',
				},
				[10] = {
					['y'] = 683759.6875,
					['x'] = -285841.53125,
					['name'] = 'Kutaisi Ammo Depot 8',
				},
				[12] = {
					['y'] = 683809.3125,
					['x'] = -285774.96875,
					['name'] = 'Kutaisi Ammo Depot 10',
				},
				[14] = {
					['y'] = 683746.5,
					['x'] = -285795.53125,
					['name'] = 'Kutaisi Ammo Depot 12',
				},
				[16] = {
					['y'] = 683733.0625,
					['x'] = -285748.71875,
					['name'] = 'Kutaisi Ammo Depot 14',
				},
				[20] = {
					['y'] = 683756.3125,
					['x'] = -285718.5,
					['name'] = 'Kutaisi Ammo Depot 18',
				},
				[24] = {
					['y'] = 683327.3125,
					['x'] = -284333.28125,
					['name'] = 'Kutaisi Communication Center',
				},
				[28] = {
					['y'] = 682967.5,
					['x'] = -284305.5,
					['name'] = 'Kutaisi Hangar 3',
				},
				[32] = {
					['y'] = 682949.125,
					['x'] = -284501.1875,
					['name'] = 'Kutaisi Hangar 7',
				},
				[33] = {
					['y'] = 682837.625,
					['x'] = -284312.34375,
					['name'] = 'Kutaisi Command Center 1',
				},
				[17] = {
					['y'] = 683730.5,
					['x'] = -285739.5,
					['name'] = 'Kutaisi Ammo Depot 15',
				},
				[21] = {
					['y'] = 685097.1875,
					['x'] = -285673.59375,
					['name'] = 'Kutaisi Fuel Depot 1',
				},
				[25] = {
					['y'] = 682949.75,
					['x'] = -284195.59375,
					['name'] = 'Kutaisi Power Supply',
				},
				[29] = {
					['y'] = 683005.25,
					['x'] = -284238.75,
					['name'] = 'Kutaisi Hangar 4',
				},
				[34] = {
					['y'] = 682946.3125,
					['x'] = -284396.40625,
					['name'] = 'Kutaisi Command Center 2',
				},
				[9] = {
					['y'] = 683764.875,
					['x'] = -285859.6875,
					['name'] = 'Kutaisi Ammo Depot 7',
				},
				[11] = {
					['y'] = 683806.6875,
					['x'] = -285765.75,
					['name'] = 'Kutaisi Ammo Depot 9',
				},
				[13] = {
					['y'] = 683741.3125,
					['x'] = -285777.375,
					['name'] = 'Kutaisi Ammo Depot 11',
				},
				[15] = {
					['y'] = 683743.875,
					['x'] = -285786.34375,
					['name'] = 'Kutaisi Ammo Depot 13',
				},
				[18] = {
					['y'] = 683727.875,
					['x'] = -285730.5625,
					['name'] = 'Kutaisi Ammo Depot 16',
				},
				[22] = {
					['y'] = 685069.125,
					['x'] = -285763.34375,
					['name'] = 'Kutaisi Fuel Depot 2',
				},
				[26] = {
					['y'] = 682983.375,
					['x'] = -284214,
					['name'] = 'Kutaisi Hangar 1',
				},
				[30] = {
					['y'] = 683082.5,
					['x'] = -284331.5,
					['name'] = 'Kutaisi Hangar 5',
				},
				[1] = {
					['y'] = 683780.0625,
					['x'] = -284566.3125,
					['name'] = 'Kutaisi Control Tower',
				},
				[19] = {
					['y'] = 683725.25,
					['x'] = -285721.34375,
					['name'] = 'Kutaisi Ammo Depot 17',
				},
				[23] = {
					['y'] = 685006.125,
					['x'] = -285847.0625,
					['name'] = 'Kutaisi Fuel Depot 3',
				},
				[31] = {
					['y'] = 683079.8125,
					['x'] = -284269.59375,
					['name'] = 'Kutaisi Hangar 6',
				},
			},
			['picture'] = {
				[1] = 'Kutaisi Airbase.png',
				[2] = 'Kutaisi Airbase-AmmoFuel.png',
			},
			['ATO'] = true,
			['y'] = 683641.08455882,
			['x'] = -285276.64613971,
			['firepower'] = {
				['min'] = 6,
				['max'] = 12,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 5,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Structure',
			},
		},
		['Rail Bridge Primorskoe-FH37'] = {
			['elements'] = {
				[1] = {
					['y'] = 526192.0625,
					['x'] = -198137.234375,
					['name'] = 'Rail Bridge Primorskoe-FH37',
				},
			},
			['picture'] = {
				[1] = 'Bridge Positions FH37-FH47-FH56-FH66.png',
			},
			['ATO'] = true,
			['y'] = 526192.0625,
			['x'] = -198137.234375,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Rail Bridge East Gantiadi-EJ80'] = {
			['elements'] = {
				[1] = {
					['y'] = 474374.84375,
					['x'] = -170816.078125,
					['name'] = 'Rail Bridge East Gantiadi-EJ80',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions EJ80-EH99.png',
			},
			['ATO'] = true,
			['y'] = 474374.84375,
			['x'] = -170816.078125,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Sukhumi Airbase Strategics'] = {
			['elements'] = {
				[7] = {
					['foundOobGround'] = true,
					['name'] = 'Sukhumi Ammo Dump 1',
					['groupId'] = 406,
				},
				[1] = {
					['foundOobGround'] = true,
					['name'] = 'Sukhumi Fuel Tank 1',
					['groupId'] = 400,
				},
				[2] = {
					['foundOobGround'] = true,
					['name'] = 'Sukhumi Fuel Tank 2',
					['groupId'] = 401,
				},
				[4] = {
					['foundOobGround'] = true,
					['name'] = 'Sukhumi Fuel Tank 4',
					['groupId'] = 403,
				},
				[8] = {
					['foundOobGround'] = true,
					['name'] = 'Sukhumi Ammo Dump 2',
					['groupId'] = 407,
				},
				[9] = {
					['foundOobGround'] = true,
					['name'] = 'Sukhumi Ammo Dump 3',
					['groupId'] = 408,
				},
				[5] = {
					['foundOobGround'] = true,
					['name'] = 'Sukhumi Fuel Tank 5',
					['groupId'] = 404,
				},
				[10] = {
					['foundOobGround'] = true,
					['name'] = 'Sukhumi Ammo Dump 4',
					['groupId'] = 409,
				},
				[3] = {
					['foundOobGround'] = true,
					['name'] = 'Sukhumi Fuel Tank 3',
					['groupId'] = 402,
				},
				[6] = {
					['foundOobGround'] = true,
					['name'] = 'Sukhumi Fuel Tank 6',
					['groupId'] = 405,
				},
				[12] = {
					['foundOobGround'] = true,
					['name'] = 'Sukhumi Power Supply',
					['groupId'] = 411,
				},
				[11] = {
					['foundOobGround'] = true,
					['name'] = 'Sukhumi Command Center',
					['groupId'] = 410,
				},
			},
			['picture'] = {
				[1] = 'Sukhumi Airbase.png',
			},
			['class'] = 'static',
			['ATO'] = true,
			['foundOobGround'] = true,
			['y'] = 564375.94459601,
			['x'] = -220076.4487766,
			['attributes'] = {
				[1] = 'Structure',
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['alive2'] = 100,
			['priority'] = 4,
			['task'] = 'Strike',
			['firepower'] = {
				['min'] = 6,
				['max'] = 10,
			}
		},
		['Rail Bridge Sukhumi-Babushara North-FH74'] = {
			['elements'] = {
				[1] = {
					['y'] = 565109.875,
					['x'] = -218542.625,
					['name'] = 'Rail Bridge Sukhumi-Babushara North-FH74',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions FH65-FH75-FH74.png',
			},
			['ATO'] = true,
			['y'] = 565109.875,
			['x'] = -218542.625,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Bridge Sukhumi-Babushara North West-FH74'] = {
			['elements'] = {
				[1] = {
					['y'] = 562378,
					['x'] = -219430.109375,
					['name'] = 'Bridge Sukhumi-Babushara North West-FH74',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions FH65-FH75-FH74.png',
			},
			['ATO'] = true,
			['y'] = 562378,
			['x'] = -219430.109375,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Bridge West Gantiadi-EJ80'] = {
			['elements'] = {
				[1] = {
					['y'] = 473621.0625,
					['x'] = -170589.21875,
					['name'] = 'Bridge West Gantiadi-EJ80',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions EJ80-EH99.png',
			},
			['ATO'] = true,
			['y'] = 473621.0625,
			['x'] = -170589.21875,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['EWR-3 Site'] = {
			['elements'] = {
				[1] = {
					['name'] = 'Unit #274',
				},
				[2] = {
					['name'] = 'Unit #275',
				},
			},
			['groupId'] = 382,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 865077.30898244,
			['x'] = -296717.35832523,
			['firepower'] = {
				['min'] = 4,
				['max'] = 8,
			},
			['dead_last'] = 0,
			['name'] = 'EWR-3',
			['priority'] = 6,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'soft',
			},
		},
		['Tbilisi Airbase'] = {
			['elements'] = {
				[1] = {
					['y'] = 897071.3125,
					['x'] = -314980.84375,
					['name'] = 'Tbilisi Control Tower',
				},
				[2] = {
					['y'] = 896782.375,
					['x'] = -315172.15625,
					['name'] = 'Tbilisi Main Ammo Depot',
				},
				[4] = {
					['y'] = 897071.3125,
					['x'] = -314980.84375,
					['name'] = 'Tbilisi Ammo Depot 2',
				},
				[8] = {
					['y'] = 897686.1875,
					['x'] = -315667.09375,
					['name'] = 'Tbilisi Fuel Tank 2',
				},
				[16] = {
					['y'] = 895591,
					['x'] = -314246.3125,
					['name'] = 'Tbilisi Hangar 1',
				},
				[17] = {
					['y'] = 896415,
					['x'] = -314477.8125,
					['name'] = 'Tbilisi Hangar 2',
				},
				[9] = {
					['y'] = 897698,
					['x'] = -315679.375,
					['name'] = 'Tbilisi Fuel Tank 3',
				},
				[18] = {
					['y'] = 896341.1875,
					['x'] = -314608.84375,
					['name'] = 'Tbilisi Hangar 3',
				},
				[5] = {
					['y'] = 896689.1875,
					['x'] = -314733.0625,
					['name'] = 'Tbilisi Communication Center',
				},
				[10] = {
					['y'] = 898172.8125,
					['x'] = -316143.1875,
					['name'] = 'Tbilisi Fuel Tank 4',
				},
				[20] = {
					['y'] = 896795.625,
					['x'] = -314791.78125,
					['name'] = 'Tbilisi Command Center',
				},
				[11] = {
					['y'] = 898194.25,
					['x'] = -316138.09375,
					['name'] = 'Tbilisi Fuel Tank 5',
				},
				[3] = {
					['y'] = 897111.5625,
					['x'] = -315008.84375,
					['name'] = 'Tbilisi Ammo Depot 1',
				},
				[6] = {
					['y'] = 897633.25,
					['x'] = -315618.28125,
					['name'] = 'Tbilisi Fuel Depot',
				},
				[12] = {
					['y'] = 898166.125,
					['x'] = -316121.625,
					['name'] = 'Tbilisi Fuel Tank 6',
				},
				[13] = {
					['y'] = 898189.3125,
					['x'] = -316174.375,
					['name'] = 'Tbilisi Fuel Tank 7',
				},
				[7] = {
					['y'] = 897667.5625,
					['x'] = -315674.03125,
					['name'] = 'Tbilisi Fuel Tank 1',
				},
				[14] = {
					['y'] = 898218.8125,
					['x'] = -316166.21875,
					['name'] = 'Tbilisi Fuel Tank 8',
				},
				[15] = {
					['y'] = 896979,
					['x'] = -314906.03125,
					['name'] = 'Tbilisi Power Supply',
				},
				[19] = {
					['y'] = 896438.5,
					['x'] = -314785.6875,
					['name'] = 'Tbilisi Hangar 4',
				},
			},
			['picture'] = {
				[1] = 'Tbilisi Airbase.png',
			},
			['ATO'] = true,
			['y'] = 897245.61875,
			['x'] = -315303.725,
			['firepower'] = {
				['min'] = 6,
				['max'] = 12,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 5,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Structure',
			},
		},
		['Bridge Dapnari-KM76'] = {
			['elements'] = {
				[1] = {
					['y'] = 672266.87695313,
					['x'] = -292658.8359375,
					['name'] = 'Bridge Dapnari North part-KM76',
				},
				[2] = {
					['y'] = 672238.12304688,
					['x'] = -292795.8515625,
					['name'] = 'Bridge Dapnari South part-KM76',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions Dapnari-KM76.png',
			},
			['ATO'] = true,
			['y'] = 672252.50000001,
			['x'] = -292727.34375,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Bridge Uazabaa-FH66'] = {
			['elements'] = {
				[1] = {
					['y'] = 551708.625,
					['x'] = -199885.375,
					['name'] = 'Bridge Uazabaa-FH66',
				},
			},
			['picture'] = {
				[1] = 'Bridge Positions FH37-FH47-FH56-FH66.png',
			},
			['ATO'] = true,
			['y'] = 551708.625,
			['x'] = -199885.375,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Rail Bridge Akvara-FH18'] = {
			['elements'] = {
				[1] = {
					['y'] = 500617.84375,
					['x'] = -185827.1875,
					['name'] = 'Rail Bridge Akvara-FH18',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions FH08-FH18-FH28-FH27.png',
			},
			['ATO'] = true,
			['y'] = 500617.84375,
			['x'] = -185827.1875,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Airlift Beslan'] = {
			['ATO'] = true,
			['y'] = 843756.7533062,
			['x'] = -148810.84954665,
			['attributes'] = {
			},
			['firepower'] = {
				['min'] = 1,
				['max'] = 1,
			},
			['task'] = 'Transport',
			['destination'] = 'Beslan',
			['base'] = 'Sochi-Adler',
			['priority'] = 1,
		},
		['TF-74'] = {
			['elements'] = {
				[1] = {
					['name'] = 'CVN-74 John C. Stennis',
				},
				[2] = {
					['name'] = 'CG-68 Anzio',
				},
				[3] = {
					['name'] = 'DDG-103 Truxtun',
				},
				[4] = {
					['name'] = 'FFG-51 Gary',
				},
				[5] = {
					['name'] = 'FFG-53 Hawes',
				},
				[6] = {
					['name'] = 'FFG-59 Kauffman',
				},
				[7] = {
					['name'] = 'TF-74-1',
				},
			},
			['groupId'] = 292,
			['foundOobGround'] = true,
			['class'] = 'ship',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 534544,
			['x'] = -333909,
			['firepower'] = {
				['min'] = 6,
				['max'] = 12,
			},
			['dead_last'] = 0,
			['name'] = 'TF-74',
			['priority'] = 1,
			['task'] = 'Anti-ship Strike',
			['attributes'] = {
				[1] = 'ship',
			},
		},
		['CAP Nalchik'] = {
			['radius'] = 50000,
			['refpoint'] = 'CAP Nalchik',
			['text'] = 'south east Nalchik',
			['ATO'] = true,
			['y'] = 781027.78373928,
			['inactive'] = true,
			['attributes'] = {
				[1] = '',
			},
			['x'] = -145930.58852062,
			['priority'] = 5,
			['task'] = 'CAP',
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
		},
		['10 US Army ELINT Station'] = {
			['elements'] = {
				[2] = {
					['foundOobGround'] = true,
					['name'] = 'US ELINT Antenna Truck 2',
					['groupId'] = 142,
				},
				[3] = {
					['foundOobGround'] = true,
					['name'] = 'US ELINT Crew Van',
					['groupId'] = 143,
				},
				[1] = {
					['foundOobGround'] = true,
					['name'] = 'US ELINT Antenna Truck 1',
					['groupId'] = 141,
				},
				[4] = {
					['foundOobGround'] = true,
					['name'] = 'US ELINT Equipment Van',
					['groupId'] = 145,
				},
				[5] = {
					['foundOobGround'] = true,
					['name'] = 'US ELINT Generator Truck',
					['groupId'] = 144,
				},
			},
			['class'] = 'static',
			['ATO'] = true,
			['foundOobGround'] = true,
			['y'] = 736691.54285715,
			['x'] = -189961.25925711,
			['firepower'] = {
				['min'] = 4,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 6,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'soft',
			},
		},
		['19 4th Army HQ'] = {
			['elements'] = {
				[1] = {
					['name'] = 'Unit #174',
				},
				[2] = {
					['name'] = 'Unit #175',
				},
				[3] = {
					['name'] = 'Unit #176',
				},
				[4] = {
					['name'] = 'Unit #177',
				},
				[5] = {
					['name'] = 'Unit #178',
				},
				[6] = {
					['name'] = 'Unit #179',
				},
				[7] = {
					['name'] = 'Unit #180',
				},
				[8] = {
					['name'] = 'Unit #181',
				},
				[9] = {
					['name'] = 'Unit #182',
				},
			},
			['groupId'] = 168,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 883576.93885714,
			['x'] = -311166.24828569,
			['firepower'] = {
				['min'] = 4,
				['max'] = 6,
			},
			['dead_last'] = 0,
			['name'] = '19 4th Army HQ',
			['priority'] = 6,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'soft',
			},
		},
		['Bridge Sukhumi-Babushara North-FH74'] = {
			['elements'] = {
				[1] = {
					['y'] = 563885.9375,
					['x'] = -218590.5625,
					['name'] = 'Bridge Sukhumi-Babushara North-FH74',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions FH65-FH75-FH74.png',
			},
			['ATO'] = true,
			['y'] = 563885.9375,
			['x'] = -218590.5625,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Rail Bridge Gumista West-FH56'] = {
			['elements'] = {
				[1] = {
					['y'] = 548287,
					['x'] = -204594.21875,
					['name'] = 'Rail Bridge Gumista West-FH56',
				},
			},
			['picture'] = {
				[1] = 'Bridge Positions FH37-FH47-FH56-FH66.png',
			},
			['ATO'] = true,
			['y'] = 548287,
			['x'] = -204594.21875,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Bridge Pahulani-GH42'] = {
			['elements'] = {
				[1] = {
					['y'] = 637292.2578125,
					['x'] = -235275.5546875,
					['name'] = 'Bridge Pahulani North part-GH42',
				},
				[2] = {
					['y'] = 637391.453125,
					['x'] = -235374.34375,
					['name'] = 'Bridge Pahulani Center part-GH42',
				},
				[3] = {
					['y'] = 637490.65625,
					['x'] = -235473.1328125,
					['name'] = 'Bridge Pahulani South part-GH42',
				},
			},
			['picture'] = {
				[1] = 'Bridge positions GG19-GH10-GH20-GH21-GH31-GH42.png',
			},
			['ATO'] = true,
			['y'] = 637391.45572917,
			['x'] = -235374.34375,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 2,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Bridge East Gantiadi-EJ80'] = {
			['elements'] = {
				[1] = {
					['y'] = 474441.984375,
					['x'] = -170287.515625,
					['name'] = 'Bridge East Gantiadi-EJ80',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions EJ80-EH99.png',
			},
			['ATO'] = true,
			['y'] = 474441.984375,
			['x'] = -170287.515625,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Bridge Grebeshok-EH99'] = {
			['elements'] = {
				[1] = {
					['y'] = 485999.78125,
					['x'] = -175487.625,
					['name'] = 'Bridge Grebeshok-EH99',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions EJ80-EH99.png',
			},
			['ATO'] = true,
			['y'] = 485999.78125,
			['x'] = -175487.625,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Kobuleti Airbase'] = {
			['elements'] = {
				[27] = {
					['y'] = 635401.125,
					['x'] = -318404.875,
					['name'] = 'Kobuleti Fuel Depot 7',
				},
				[2] = {
					['y'] = 637940.9375,
					['x'] = -316652.8125,
					['name'] = 'Kobuleti Main Ammo Depot',
				},
				[3] = {
					['y'] = 637878.25,
					['x'] = -316586.8125,
					['name'] = 'Kobuleti Ammo Depot 1',
				},
				[4] = {
					['y'] = 637886.6875,
					['x'] = -316591.34375,
					['name'] = 'Kobuleti Ammo Depot 2',
				},
				[5] = {
					['y'] = 637809.25,
					['x'] = -316590.125,
					['name'] = 'Kobuleti Ammo Depot 3',
				},
				[6] = {
					['y'] = 637789.75,
					['x'] = -316614.375,
					['name'] = 'Kobuleti Ammo Depot 4',
				},
				[7] = {
					['y'] = 637798.1875,
					['x'] = -316618.875,
					['name'] = 'Kobuleti Ammo Depot 5',
				},
				[8] = {
					['y'] = 637806.375,
					['x'] = -316623.25,
					['name'] = 'Kobuleti Ammo Depot 6',
				},
				[10] = {
					['y'] = 637849.375,
					['x'] = -316646.25,
					['name'] = 'Kobuleti Ammo Depot 8',
				},
				[12] = {
					['y'] = 637841.125,
					['x'] = -316641.84375,
					['name'] = 'Kobuleti Ammo Depot 10',
				},
				[14] = {
					['y'] = 637916.625,
					['x'] = -316682.1875,
					['name'] = 'Kobuleti Ammo Depot 12',
				},
				[16] = {
					['y'] = 637925.125,
					['x'] = -316686.65625,
					['name'] = 'Kobuleti Ammo Depot 14',
				},
				[20] = {
					['y'] = 637949.9375,
					['x'] = -316625.21875,
					['name'] = 'Kobuleti Ammo Depot 18',
				},
				[24] = {
					['y'] = 635513.75,
					['x'] = -318698.34375,
					['name'] = 'Kobuleti Fuel Depot 4',
				},
				[28] = {
					['y'] = 635388.125,
					['x'] = -318352.6875,
					['name'] = 'Kobuleti Communication Center',
				},
				[32] = {
					['y'] = 636662.375,
					['x'] = -317297.65625,
					['name'] = 'Kobuleti Hangar 4',
				},
				[33] = {
					['y'] = 636576.6875,
					['x'] = -317344.46875,
					['name'] = 'Kobuleti Hangar 5',
				},
				[17] = {
					['y'] = 637933.25,
					['x'] = -316616.3125,
					['name'] = 'Kobuleti Ammo Depot 15',
				},
				[21] = {
					['y'] = 635707.4375,
					['x'] = -318647.5625,
					['name'] = 'Kobuleti Fuel Depot 1',
				},
				[25] = {
					['y'] = 635575.75,
					['x'] = -318607.25,
					['name'] = 'Kobuleti Fuel Depot 5',
				},
				[29] = {
					['y'] = 636555.25,
					['x'] = -317209.8125,
					['name'] = 'Kobuleti Hangar 1',
				},
				[34] = {
					['y'] = 636446.875,
					['x'] = -317240.1875,
					['name'] = 'Kobuleti Command Center 1',
				},
				[9] = {
					['y'] = 637814.8125,
					['x'] = -316627.78125,
					['name'] = 'Kobuleti Ammo Depot 7',
				},
				[11] = {
					['y'] = 637857.8125,
					['x'] = -316650.75,
					['name'] = 'Kobuleti Ammo Depot 9',
				},
				[13] = {
					['y'] = 637900,
					['x'] = -316673.28125,
					['name'] = 'Kobuleti Ammo Depot 11',
				},
				[15] = {
					['y'] = 637908.4375,
					['x'] = -316677.78125,
					['name'] = 'Kobuleti Ammo Depot 13',
				},
				[18] = {
					['y'] = 637941.75,
					['x'] = -316620.8125,
					['name'] = 'Kobuleti Ammo Depot 16',
				},
				[22] = {
					['y'] = 635640.9375,
					['x'] = -318735.71875,
					['name'] = 'Kobuleti Fuel Depot 2',
				},
				[26] = {
					['y'] = 635620.1875,
					['x'] = -318590.40625,
					['name'] = 'Kobuleti Fuel Depot 6',
				},
				[30] = {
					['y'] = 636613.625,
					['x'] = -317137.9375,
					['name'] = 'Kobuleti Hangar 2',
				},
				[31] = {
					['y'] = 636620.5625,
					['x'] = -317170.21875,
					['name'] = 'Kobuleti Hangar 3',
				},
				[1] = {
					['y'] = 635457.5625,
					['x'] = -317800.125,
					['name'] = 'Kobuleti Control Tower',
				},
				[19] = {
					['y'] = 637958.375,
					['x'] = -316629.71875,
					['name'] = 'Kobuleti Ammo Depot 17',
				},
				[23] = {
					['y'] = 635541.625,
					['x'] = -318769.03125,
					['name'] = 'Kobuleti Fuel Depot 3',
				},
				[35] = {
					['y'] = 636484.125,
					['x'] = -317284.6875,
					['name'] = 'Kobuleti Command Center 2',
				},
			},
			['picture'] = {
				[1] = 'Kobuleti Airbase.png',
				[2] = 'Kobuleti Airbase-Ammo-Hangar-Command.png',
			},
			['ATO'] = true,
			['y'] = 637014.63035714,
			['x'] = -317238.49017857,
			['firepower'] = {
				['min'] = 6,
				['max'] = 12,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 5,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Structure',
			},
		},
		['Rail Bridge Mugudzyrhva-FH28'] = {
			['elements'] = {
				[1] = {
					['y'] = 513094.03125,
					['x'] = -190870.578125,
					['name'] = 'Rail Bridge Mugudzyrhva-FH28',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions FH08-FH18-FH28-FH27.png',
			},
			['ATO'] = true,
			['y'] = 513094.03125,
			['x'] = -190870.578125,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Rail Bridge North Geguti-LM17'] = {
			['elements'] = {
				[1] = {
					['y'] = 701658.0546875,
					['x'] = -280436.1328125,
					['name'] = 'Rail Bridge North Geguti West part-LM17',
				},
				[2] = {
					['y'] = 701748.8984375,
					['x'] = -280394.33398438,
					['name'] = 'Rail Bridge North Geguti Center part-LM17',
				},
				[3] = {
					['y'] = 701839.7421875,
					['x'] = -280352.53515625,
					['name'] = 'Rail Bridge North Geguti East part-LM17',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions LM16-LM17-LM18.png',
			},
			['ATO'] = true,
			['y'] = 701748.8984375,
			['x'] = -280394.33398438,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 2,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Bridge Kvemo-Merheuli-FH75'] = {
			['elements'] = {
				[1] = {
					['y'] = 560317.8125,
					['x'] = -210863.9375,
					['name'] = 'Bridge Kvemo-Merheuli-FH75',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions FH65-FH75-FH74.png',
			},
			['ATO'] = true,
			['y'] = 560317.8125,
			['x'] = -210863.9375,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Rail Bridge Pshap-FH75'] = {
			['elements'] = {
				[1] = {
					['y'] = 563639.6875,
					['x'] = -216667.140625,
					['name'] = 'Rail Bridge Pshap-FH75',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions FH65-FH75-FH74.png',
			},
			['ATO'] = true,
			['y'] = 563639.6875,
			['x'] = -216667.140625,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Rail Bridge Kul tubani-EJ80'] = {
			['elements'] = {
				[1] = {
					['y'] = 468038.5625,
					['x'] = -169535.234375,
					['name'] = 'Rail Bridge Kul tubani-EJ80',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions EJ80-EH99.png',
			},
			['ATO'] = true,
			['y'] = 468038.5625,
			['x'] = -169535.234375,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Airlift Mineralnye-Vody'] = {
			['ATO'] = true,
			['y'] = 705718.47981263,
			['x'] = -51251.551717591,
			['attributes'] = {
			},
			['firepower'] = {
				['min'] = 1,
				['max'] = 1,
			},
			['task'] = 'Transport',
			['destination'] = 'Mineralnye-Vody',
			['base'] = 'Beslan',
			['priority'] = 1,
		},
		['Tbilissi-Lochini OCA Strike'] = {
			['class'] = 'airbase',
			['ATO'] = true,
			['unit'] = {
				['number'] = 4,
				['type'] = 'KC135MPRS',
				['name'] = '174 ARW',
			},
			['y'] = 896538.85714286,
			['x'] = -315478.57142857,
			['firepower'] = {
				['min'] = 2,
				['max'] = 6,
			},
			['foundOobGround'] = true,
			['name'] = 'Tbilissi-Lochini',
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Parked Aircraft',
			},
		},
		['Kutaisi OCA Strike'] = {
			['class'] = 'airbase',
			['ATO'] = true,
			['unit'] = {
				['number'] = 3,
				['type'] = 'E-3A',
				['name'] = '7 ACCS',
			},
			['y'] = 683853.75717885,
			['x'] = -284889.06283057,
			['firepower'] = {
				['min'] = 4,
				['max'] = 6,
			},
			['foundOobGround'] = true,
			['name'] = 'Kutaisi',
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Parked Aircraft',
			},
		},
		['Senaki Airbase'] = {
			['elements'] = {
				[27] = {
					['y'] = 647573.875,
					['x'] = -280663,
					['name'] = 'Senaki Hangar 2',
				},
				[2] = {
					['y'] = 646751.875,
					['x'] = -282847.90625,
					['name'] = 'Senaki Main Ammo Depot',
				},
				[3] = {
					['y'] = 646740.4375,
					['x'] = -282812.40625,
					['name'] = 'Senaki Ammo Depot 1',
				},
				[4] = {
					['y'] = 646749.3125,
					['x'] = -282816,
					['name'] = 'Senaki Ammo Depot 2',
				},
				[5] = {
					['y'] = 646766.8125,
					['x'] = -282823.125,
					['name'] = 'Senaki Ammo Depot 3',
				},
				[6] = {
					['y'] = 646757.9375,
					['x'] = -282819.53125,
					['name'] = 'Senaki Ammo Depot 4',
				},
				[7] = {
					['y'] = 646713.3125,
					['x'] = -282872.53125,
					['name'] = 'Senaki Ammo Depot 5',
				},
				[8] = {
					['y'] = 646730.75,
					['x'] = -282879.65625,
					['name'] = 'Senaki Ammo Depot 6',
				},
				[10] = {
					['y'] = 646739.625,
					['x'] = -282883.21875,
					['name'] = 'Senaki Ammo Depot 8',
				},
				[12] = {
					['y'] = 646682.625,
					['x'] = -282788.8125,
					['name'] = 'Senaki Ammo Depot 10',
				},
				[14] = {
					['y'] = 646668.9375,
					['x'] = -282854.53125,
					['name'] = 'Senaki Ammo Depot 12',
				},
				[16] = {
					['y'] = 646597.4375,
					['x'] = -282825.5,
					['name'] = 'Senaki Ammo Depot 14',
				},
				[20] = {
					['y'] = 646614.375,
					['x'] = -282799.3125,
					['name'] = 'Senaki Ammo Depot 18',
				},
				[24] = {
					['y'] = 646808.625,
					['x'] = -280305.5,
					['name'] = 'Senaki Fuel Depot 4',
				},
				[28] = {
					['y'] = 647200.5,
					['x'] = -280709.46875,
					['name'] = 'Senaki Hangar 3',
				},
				[32] = {
					['y'] = 647268.0625,
					['x'] = -281047.84375,
					['name'] = 'Senaki Hangar 7',
				},
				[33] = {
					['y'] = 646244.5,
					['x'] = -281449.625,
					['name'] = 'Senaki Hangar 8',
				},
				[17] = {
					['y'] = 646606.3125,
					['x'] = -282829.09375,
					['name'] = 'Senaki Ammo Depot 15',
				},
				[21] = {
					['y'] = 646882.5625,
					['x'] = -280223.46875,
					['name'] = 'Senaki Fuel Depot 1',
				},
				[25] = {
					['y'] = 645939.3125,
					['x'] = -281924.46875,
					['name'] = 'Senaki Power Supply',
				},
				[29] = {
					['y'] = 647103.625,
					['x'] = -280812.5625,
					['name'] = 'Senaki Hangar 4',
				},
				[34] = {
					['y'] = 647218.25,
					['x'] = -280573.5625,
					['name'] = 'Senaki Command Center 1',
				},
				[9] = {
					['y'] = 646722.125,
					['x'] = -282876.125,
					['name'] = 'Senaki Ammo Depot 7',
				},
				[11] = {
					['y'] = 646691.5,
					['x'] = -282792.4375,
					['name'] = 'Senaki Ammo Depot 9',
				},
				[13] = {
					['y'] = 646660.0625,
					['x'] = -282850.9375,
					['name'] = 'Senaki Ammo Depot 11',
				},
				[15] = {
					['y'] = 646651.4375,
					['x'] = -282847.4375,
					['name'] = 'Senaki Ammo Depot 13',
				},
				[18] = {
					['y'] = 646614.9375,
					['x'] = -282832.59375,
					['name'] = 'Senaki Ammo Depot 16',
				},
				[22] = {
					['y'] = 646685.1875,
					['x'] = -280257.1875,
					['name'] = 'Senaki Fuel Depot 2',
				},
				[26] = {
					['y'] = 647660.1875,
					['x'] = -280708.84375,
					['name'] = 'Senaki Hangar 1',
				},
				[30] = {
					['y'] = 647140.5625,
					['x'] = -280773.84375,
					['name'] = 'Senaki Hangar 5',
				},
				[36] = {
					['y'] = 646323.0625,
					['x'] = -281379.90625,
					['name'] = 'Senaki Communication Center',
				},
				[31] = {
					['y'] = 647236,
					['x'] = -281007.71875,
					['name'] = 'Senaki Hangar 6',
				},
				[1] = {
					['y'] = 646965.25,
					['x'] = -280806.5625,
					['name'] = 'Senaki Control Tower',
				},
				[19] = {
					['y'] = 646623.8125,
					['x'] = -282836.21875,
					['name'] = 'Senaki Ammo Depot 17',
				},
				[23] = {
					['y'] = 646706.8125,
					['x'] = -280330.03125,
					['name'] = 'Senaki Fuel Depot 3',
				},
				[35] = {
					['y'] = 647088.125,
					['x'] = -280655.46875,
					['name'] = 'Senaki Command Center 2',
				},
			},
			['picture'] = {
				[1] = 'Senaki Airbase.png',
				[2] = 'Senaki Airbase-Ammo',
			},
			['ATO'] = true,
			['y'] = 646809.11458333,
			['x'] = -281875.45659722,
			['firepower'] = {
				['min'] = 6,
				['max'] = 12,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 5,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Structure',
			},
		},
		['Sukhumi-Babushara Train Station - FH74'] = {
			['elements'] = {
				[7] = {
					['y'] = 565530.51834106,
					['x'] = -219203.48779297,
					['name'] = 'Sukhumi-Babushara Train Station Fuel Tank 1',
				},
				[1] = {
					['y'] = 565464.4375,
					['x'] = -219071.4375,
					['name'] = 'Sukhumi-Babushara Train Station Hangar 1',
				},
				[2] = {
					['y'] = 565426.8125,
					['x'] = -219023.4375,
					['name'] = 'Sukhumi-Babushara Train Station Hangar 2',
				},
				[4] = {
					['y'] = 565629.19628906,
					['x'] = -219001.41796875,
					['name'] = 'Sukhumi-Babushara Train Station Hangar 4',
				},
				[8] = {
					['y'] = 565561.22433472,
					['x'] = -219196.45996094,
					['name'] = 'Sukhumi-Babushara Train Station Fuel Tank 2',
				},
				[9] = {
					['y'] = 565517.56420898,
					['x'] = -219146.88867188,
					['name'] = 'Sukhumi-Babushara Train Station Fuel Tank 3',
				},
				[5] = {
					['y'] = 565555.05175781,
					['x'] = -219245.6875,
					['name'] = 'Sukhumi-Babushara Train Station Hangar 5',
				},
				[3] = {
					['y'] = 565502.9375,
					['x'] = -219005.28125,
					['name'] = 'Sukhumi-Babushara Train Station Hangar 3',
				},
				[6] = {
					['y'] = 565595.43847656,
					['x'] = -219235.99511719,
					['name'] = 'Sukhumi-Babushara Train Station Hangar 6',
				},
			},
			['picture'] = {
				[1] = 'Sukhumi-Babushara Train Station.png',
			},
			['ATO'] = true,
			['y'] = 565531.46454535,
			['x'] = -219125.56591797,
			['firepower'] = {
				['min'] = 4,
				['max'] = 6,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 3,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Structure',
			},
		},
		['Patriot Site East'] = {
			['elements'] = {
				[1] = {
					['name'] = 'Patriot Site East-1',
				},
				[2] = {
					['name'] = 'Patriot Site East-2',
				},
				[3] = {
					['name'] = 'Patriot Site East-3',
				},
				[4] = {
					['name'] = 'Patriot Site East-4',
				},
				[5] = {
					['name'] = 'Patriot Site East-5',
				},
				[6] = {
					['name'] = 'Patriot Site East-6',
				},
				[7] = {
					['name'] = 'Patriot Site East-7',
				},
				[8] = {
					['name'] = 'Patriot Site East-8',
				},
				[9] = {
					['name'] = 'Patriot Site East-9',
				},
				[10] = {
					['name'] = 'Patriot Site East-10',
				},
				[11] = {
					['name'] = 'Patriot Site East-11',
				},
			},
			['groupId'] = 434,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 904999.51333318,
			['x'] = -319105.63432902,
			['firepower'] = {
				['min'] = 4,
				['max'] = 8,
			},
			['dead_last'] = 0,
			['name'] = 'Patriot Site East',
			['priority'] = 2,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'SAM',
			},
		},
		['Senaki-Kolkhi OCA Strike'] = {
			['class'] = 'airbase',
			['ATO'] = true,
			['unit'] = {
				['number'] = 4,
				['type'] = 'KC-135',
				['name'] = '801 ARS',
			},
			['y'] = 647369.87369832,
			['x'] = -281713.83114196,
			['firepower'] = {
				['min'] = 4,
				['max'] = 6,
			},
			['foundOobGround'] = true,
			['name'] = 'Senaki-Kolkhi',
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Parked Aircraft',
			},
		},
		['Bridge Pshap East-FH75'] = {
			['elements'] = {
				[1] = {
					['y'] = 565105.875,
					['x'] = -216795.40625,
					['name'] = 'Bridge Pshap East-FH75',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions FH65-FH75-FH74.png',
			},
			['ATO'] = true,
			['y'] = 565105.875,
			['x'] = -216795.40625,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Rail Bridge Gudauta-FH27'] = {
			['elements'] = {
				[1] = {
					['y'] = 515373.625,
					['x'] = -194627.296875,
					['name'] = 'Rail Bridge Gudauta-FH27',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions FH08-FH18-FH28-FH27.png',
			},
			['ATO'] = true,
			['y'] = 515373.625,
			['x'] = -194627.296875,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Rail Bridge Tsalkoti-EJ80'] = {
			['elements'] = {
				[1] = {
					['y'] = 472717.5625,
					['x'] = -170051.65625,
					['name'] = 'Rail Bridge Tsalkoti-EJ80',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions EJ80-EH99.png',
			},
			['ATO'] = true,
			['y'] = 472717.5625,
			['x'] = -170051.65625,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Bridge Primorskoe North-FH37'] = {
			['elements'] = {
				[1] = {
					['y'] = 526428.625,
					['x'] = -196679.6875,
					['name'] = 'Bridge Primorskoe North-FH37',
				},
			},
			['picture'] = {
				[1] = 'Bridge Positions FH37-FH47-FH56-FH66.png',
			},
			['ATO'] = true,
			['y'] = 526428.625,
			['x'] = -196679.6875,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Batumi Airbase'] = {
			['elements'] = {
				[1] = {
					['y'] = 617693,
					['x'] = -355688.28125,
					['name'] = 'Batumi Control Tower',
				},
				[2] = {
					['y'] = 617513.1875,
					['x'] = -355414.625,
					['name'] = 'Batumi Main Ammo Depot',
				},
				[4] = {
					['y'] = 617354.99682617,
					['x'] = -355438.48291016,
					['name'] = 'Batumi Ammo Depot 2',
				},
				[8] = {
					['y'] = 617921.95751953,
					['x'] = -355586.30224609,
					['name'] = 'Batumi Power Supply',
				},
				[16] = {
					['y'] = 617559.6875,
					['x'] = -355499.375,
					['name'] = 'Batumi Command Center 1',
				},
				[17] = {
					['y'] = 617541.6875,
					['x'] = -355546.5,
					['name'] = 'Batumi Command Center 2',
				},
				[9] = {
					['y'] = 618377,
					['x'] = -356082.15625,
					['name'] = 'Batumi Hangar 1',
				},
				[5] = {
					['y'] = 617296.9375,
					['x'] = -355382.0625,
					['name'] = 'Batumi Ammo Depot 3',
				},
				[10] = {
					['y'] = 618389.25,
					['x'] = -356147.5,
					['name'] = 'Batumi Hangar 2',
				},
				[11] = {
					['y'] = 618383.6875,
					['x'] = -356193.8125,
					['name'] = 'Batumi Hangar 3',
				},
				[3] = {
					['y'] = 617445.625,
					['x'] = -355494.59375,
					['name'] = 'Batumi Ammo Depot 1',
				},
				[6] = {
					['y'] = 618273.875,
					['x'] = -355929.40625,
					['name'] = 'Batumi Fuel Depot 1',
				},
				[12] = {
					['y'] = 618359.375,
					['x'] = -356258.34375,
					['name'] = 'Batumi Hangar 4',
				},
				[13] = {
					['y'] = 617597.6875,
					['x'] = -355467.21875,
					['name'] = 'Batumi Hangar 5',
				},
				[7] = {
					['y'] = 618297.6875,
					['x'] = -355926.875,
					['name'] = 'Batumi Fuel Depot 2',
				},
				[14] = {
					['y'] = 617586.625,
					['x'] = -355432.3125,
					['name'] = 'Batumi Hangar 6',
				},
				[15] = {
					['y'] = 617639.3125,
					['x'] = -355603.28125,
					['name'] = 'Batumi Hangar 7',
				},
			},
			['picture'] = {
				[1] = 'Batumi Airbase.png',
				[2] = 'Batumi Airbase-Ammo.png',
			},
			['ATO'] = true,
			['y'] = 617837.15172622,
			['x'] = -355711.24287684,
			['firepower'] = {
				['min'] = 6,
				['max'] = 12,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 5,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Structure',
			},
		},
		['Bridge Gumista-FH56'] = {
			['elements'] = {
				[1] = {
					['y'] = 548369.125,
					['x'] = -204543.046875,
					['name'] = 'Bridge Gumista-FH56',
				},
			},
			['picture'] = {
				[1] = 'Bridge Positions FH37-FH47-FH56-FH66.png',
			},
			['ATO'] = true,
			['y'] = 548369.125,
			['x'] = -204543.046875,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Rail Bridge Dapnari-KM76'] = {
			['elements'] = {
				[1] = {
					['y'] = 671988.8125,
					['x'] = -292722.10351563,
					['name'] = 'Rail Bridge Dapnari North part-KM76',
				},
				[2] = {
					['y'] = 671985.1875,
					['x'] = -292822.03710938,
					['name'] = 'Rail Bridge Dapnari Center part-KM76',
				},
				[3] = {
					['y'] = 671981.56445313,
					['x'] = -292921.97070313,
					['name'] = 'Rail Bridge Dapnari South part-KM76',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions Dapnari-KM76.png',
			},
			['ATO'] = true,
			['y'] = 671985.18815104,
			['x'] = -292822.03710938,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 2,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Sukhumi Train Station - FH66'] = {
			['elements'] = {
				[2] = {
					['y'] = 554377.1875,
					['x'] = -204955.125,
					['name'] = 'Sukhumi Train Station Hangar 2',
				},
				[3] = {
					['y'] = 554325.88476563,
					['x'] = -204968.50488281,
					['name'] = 'Sukhumi Train Station Hangar 3',
				},
				[1] = {
					['y'] = 554344.375,
					['x'] = -204884.0625,
					['name'] = 'Sukhumi Train Station Hangar 1',
				},
				[4] = {
					['y'] = 554283,
					['x'] = -204995.84375,
					['name'] = 'Sukhumi Train Station Hangar 4',
				},
				[5] = {
					['y'] = 554210.63818359,
					['x'] = -204949.65007019,
					['name'] = 'Sukhumi Train Station Hangar 5',
				},
			},
			['picture'] = {
				[1] = 'Sukhumi Train Station.png',
			},
			['ATO'] = true,
			['y'] = 554308.21708984,
			['x'] = -204950.6372406,
			['firepower'] = {
				['min'] = 4,
				['max'] = 6,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 2,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Structure',
			},
		},
		['Bridge Gudauta-FH27'] = {
			['elements'] = {
				[1] = {
					['y'] = 515508.125,
					['x'] = -194555.703125,
					['name'] = 'Bridge Gudauta-FH27',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions FH08-FH18-FH28-FH27.png',
			},
			['ATO'] = true,
			['y'] = 515508.125,
			['x'] = -194555.703125,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Leselidze Train Station - EJ80'] = {
			['elements'] = {
				[1] = {
					['y'] = 470197.90625,
					['x'] = -169643.34375,
					['name'] = 'Leselidze Train Station Hangar 1',
				},
				[2] = {
					['y'] = 470258.59375,
					['x'] = -169649.5,
					['name'] = 'Leselidze Train Station Hangar 2',
				},
				[4] = {
					['y'] = 470219.125,
					['x'] = -169724.6875,
					['name'] = 'Leselidze Train Station Hangar 4',
				},
				[3] = {
					['y'] = 470377.88964844,
					['x'] = -169836.35205078,
					['name'] = 'Leselidze Train Station Hangar 3',
				},
			},
			['picture'] = {
				[1] = 'Leselidze Train Station.png',
			},
			['ATO'] = true,
			['y'] = 470263.37866211,
			['x'] = -169713.47082519,
			['firepower'] = {
				['min'] = 4,
				['max'] = 4,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 2,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Structure',
			},
		},
		['Rail Bridge Kvemo-Merheuli North-FH65'] = {
			['elements'] = {
				[1] = {
					['y'] = 558293.5625,
					['x'] = -208651.4375,
					['name'] = 'Rail Bridge Kvemo-Merheuli North-FH65',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions FH65-FH75-FH74.png',
			},
			['ATO'] = true,
			['y'] = 558293.5625,
			['x'] = -208651.4375,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Bridge Sukhumi-Babushara North East-FH74'] = {
			['elements'] = {
				[1] = {
					['y'] = 566000.125,
					['x'] = -218727.34375,
					['name'] = 'Bridge Sukhumi-Babushara North East-FH74',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions FH65-FH75-FH74.png',
			},
			['ATO'] = true,
			['y'] = 566000.125,
			['x'] = -218727.34375,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Gudauta Airbase'] = {
			['elements'] = {
				[27] = {
					['y'] = 515835.875,
					['x'] = -197326.15625,
					['name'] = 'Gudauta Hangar 2',
				},
				[2] = {
					['y'] = 514975.65625,
					['x'] = -196462.671875,
					['name'] = 'Gudauta Main Ammo Depot',
				},
				[3] = {
					['y'] = 514970.40625,
					['x'] = -196499.59375,
					['name'] = 'Gudauta Ammo Depot 1',
				},
				[4] = {
					['y'] = 514964,
					['x'] = -196492.46875,
					['name'] = 'Gudauta Ammo Depot 2',
				},
				[5] = {
					['y'] = 514951.40625,
					['x'] = -196478.40625,
					['name'] = 'Gudauta Ammo Depot 3',
				},
				[6] = {
					['y'] = 514957.8125,
					['x'] = -196485.53125,
					['name'] = 'Gudauta Ammo Depot 4',
				},
				[7] = {
					['y'] = 515021.125,
					['x'] = -196457.453125,
					['name'] = 'Gudauta Ammo Depot 5',
				},
				[8] = {
					['y'] = 515008.53125,
					['x'] = -196443.375,
					['name'] = 'Gudauta Ammo Depot 6',
				},
				[10] = {
					['y'] = 515002.125,
					['x'] = -196436.296875,
					['name'] = 'Gudauta Ammo Depot 8',
				},
				[12] = {
					['y'] = 515098.21875,
					['x'] = -196543.375,
					['name'] = 'Gudauta Ammo Depot 10',
				},
				[14] = {
					['y'] = 515085.625,
					['x'] = -196529.3125,
					['name'] = 'Gudauta Ammo Depot 12',
				},
				[16] = {
					['y'] = 515065.71875,
					['x'] = -196507.125,
					['name'] = 'Gudauta Ammo Depot 14',
				},
				[20] = {
					['y'] = 515077.96875,
					['x'] = -196566.625,
					['name'] = 'Gudauta Ammo Depot 18',
				},
				[24] = {
					['y'] = 517034,
					['x'] = -198611.3125,
					['name'] = 'Gudauta Fuel Depot 4',
				},
				[28] = {
					['y'] = 515832.21875,
					['x'] = -197374.578125,
					['name'] = 'Gudauta Hangar 3',
				},
				[32] = {
					['y'] = 515920.46875,
					['x'] = -197491.546875,
					['name'] = 'Gudauta Hangar 7',
				},
				[33] = {
					['y'] = 515958.34375,
					['x'] = -197486.703125,
					['name'] = 'Gudauta Hangar 8',
				},
				[17] = {
					['y'] = 515053.09375,
					['x'] = -196493.0625,
					['name'] = 'Gudauta Ammo Depot 15',
				},
				[21] = {
					['y'] = 516965.21875,
					['x'] = -198426.40625,
					['name'] = 'Gudauta Fuel Depot 1',
				},
				[25] = {
					['y'] = 516806.5,
					['x'] = -198410.5,
					['name'] = 'Gudauta Power Supply',
				},
				[29] = {
					['y'] = 515856.53125,
					['x'] = -197416.390625,
					['name'] = 'Gudauta Hangar 4',
				},
				[34] = {
					['y'] = 515649.80810547,
					['x'] = -195456.59667969,
					['name'] = 'Gudauta Command Center 1',
				},
				[9] = {
					['y'] = 515014.75,
					['x'] = -196450.328125,
					['name'] = 'Gudauta Ammo Depot 7',
				},
				[11] = {
					['y'] = 515104.625,
					['x'] = -196550.5,
					['name'] = 'Gudauta Ammo Depot 9',
				},
				[13] = {
					['y'] = 515092,
					['x'] = -196536.4375,
					['name'] = 'Gudauta Ammo Depot 11',
				},
				[15] = {
					['y'] = 515059.5,
					['x'] = -196500.171875,
					['name'] = 'Gudauta Ammo Depot 13',
				},
				[18] = {
					['y'] = 515005.59375,
					['x'] = -196538.984375,
					['name'] = 'Gudauta Ammo Depot 16',
				},
				[22] = {
					['y'] = 517047.53125,
					['x'] = -198479.4375,
					['name'] = 'Gudauta Fuel Depot 2',
				},
				[26] = {
					['y'] = 515917.8125,
					['x'] = -197271.71875,
					['name'] = 'Gudauta Hangar 1',
				},
				[30] = {
					['y'] = 515862.6875,
					['x'] = -197445.5,
					['name'] = 'Gudauta Hangar 5',
				},
				[31] = {
					['y'] = 515867.90625,
					['x'] = -197469.203125,
					['name'] = 'Gudauta Hangar 6',
				},
				[1] = {
					['y'] = 515805.6875,
					['x'] = -196854.59375,
					['name'] = 'Gudauta Control Tower',
				},
				[19] = {
					['y'] = 515011.96875,
					['x'] = -196546.125,
					['name'] = 'Gudauta Ammo Depot 17',
				},
				[23] = {
					['y'] = 517098.375,
					['x'] = -198571.0625,
					['name'] = 'Gudauta Fuel Depot 3',
				},
				[35] = {
					['y'] = 515642.35498047,
					['x'] = -195480.84228516,
					['name'] = 'Gudauta Command Center 2',
				},
			},
			['picture'] = {
				[1] = 'Gudauta Airbase South.png',
				[2] = 'Gudauta Airbase North',
			},
			['ATO'] = true,
			['y'] = 515560.61269531,
			['x'] = -196945.439774,
			['firepower'] = {
				['min'] = 6,
				['max'] = 12,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 5,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Structure',
			},
		},
		['Beslan Alert 120 Km'] = {
			['radius'] = 120000,
			['attributes'] = {
			},
			['ATO'] = true,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['priority'] = 4,
			['base'] = 'Beslan',
			['task'] = 'Intercept',
		},
		['Bridge Adzhkhahara-FH28'] = {
			['elements'] = {
				[1] = {
					['y'] = 510276.9375,
					['x'] = -186212.46875,
					['name'] = 'Bridge Adzhkhahara-FH28',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions FH08-FH18-FH28-FH27.png',
			},
			['ATO'] = true,
			['y'] = 510276.9375,
			['x'] = -186212.46875,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Sukhumi OCA Strike'] = {
			['class'] = 'airbase',
			['ATO'] = true,
			['unit'] = {
				['number'] = 12,
				['type'] = 'AJS37',
				['name'] = 'F7',
			},
			['y'] = 564387.05872916,
			['x'] = -220531.73642658,
			['firepower'] = {
				['min'] = 4,
				['max'] = 6,
			},
			['foundOobGround'] = true,
			['name'] = 'Sukhumi',
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Parked Aircraft',
			},
		},
		['CAP Center'] = {
			['radius'] = 50000,
			['refpoint'] = 'CAP Center',
			['text'] = 'over Center front',
			['ATO'] = true,
			['y'] = 803884.27348393,
			['inactive'] = true,
			['attributes'] = {
				[1] = '',
			},
			['x'] = -180111.22121794,
			['priority'] = 5,
			['task'] = 'CAP',
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
		},
		['Rail Bridge Tagiloni-GH21'] = {
			['elements'] = {
				[6] = {
					['y'] = 622423.2265625,
					['x'] = -251090.078125,
					['name'] = 'Rail Bridge Tagiloni South down part-GH21',
				},
				[2] = {
					['y'] = 622222.2421875,
					['x'] = -250744.234375,
					['name'] = 'Rail Bridge Tagiloni North middle part-GH21',
				},
				[3] = {
					['y'] = 622272.4921875,
					['x'] = -250830.6953125,
					['name'] = 'Rail Bridge Tagiloni North down part-GH21',
				},
				[1] = {
					['y'] = 622172,
					['x'] = -250657.7734375,
					['name'] = 'Rail Bridge Tagiloni North up part-GH21',
				},
				[4] = {
					['y'] = 622322.734375,
					['x'] = -250917.15625,
					['name'] = 'Rail Bridge Tagiloni South up part-GH21',
				},
				[5] = {
					['y'] = 622372.984375,
					['x'] = -251003.6171875,
					['name'] = 'Rail Bridge Tagiloni South middle part-GH21',
				},
			},
			['picture'] = {
				[1] = 'Bridge positions GG19-GH10-GH20-GH21-GH31-GH42.png',
			},
			['ATO'] = true,
			['y'] = 622297.61328125,
			['x'] = -250873.92578125,
			['firepower'] = {
				['min'] = 2,
				['max'] = 6,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 5,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Bridge Akvara-FH18'] = {
			['elements'] = {
				[1] = {
					['y'] = 501025.8671875,
					['x'] = -185377.203125,
					['name'] = 'Bridge Akvara-FH18',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions FH08-FH18-FH28-FH27.png',
			},
			['ATO'] = true,
			['y'] = 501025.8671875,
			['x'] = -185377.203125,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Mineralnye-Vody Alert 280 Km'] = {
			['radius'] = 280000,
			['attributes'] = {
			},
			['ATO'] = true,
			['firepower'] = {
				['min'] = 2,
				['max'] = 4,
			},
			['priority'] = 4,
			['base'] = 'Mineralnye-Vody',
			['task'] = 'Intercept',
		},
		['Bridge Mugudzyrhva-FH28'] = {
			['elements'] = {
				[1] = {
					['y'] = 513422.03125,
					['x'] = -190062.953125,
					['name'] = 'Bridge Mugudzyrhva-FH28',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions FH08-FH18-FH28-FH27.png',
			},
			['ATO'] = true,
			['y'] = 513422.03125,
			['x'] = -190062.953125,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Bridge Patara-Poti East-GG27'] = {
			['elements'] = {
				[1] = {
					['y'] = 619661.9921875,
					['x'] = -290571.91992188,
					['name'] = 'Bridge Patara-Poti East North part-GG27',
				},
				[2] = {
					['y'] = 619585.6328125,
					['x'] = -290689.265625,
					['name'] = 'Bridge Patara-Poti East South part-GH27',
				},
			},
			['picture'] = {
				[1] = 'Bridges Positions Patara-Poti-GG27.png',
			},
			['ATO'] = true,
			['y'] = 619623.8125,
			['x'] = -290630.59277344,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 2,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['14 1st Artillery Division/4.Btry'] = {
			['elements'] = {
				[1] = {
					['name'] = 'Unit #110',
				},
				[2] = {
					['name'] = 'Unit #111',
				},
				[3] = {
					['name'] = 'Unit #112',
				},
				[4] = {
					['name'] = 'Unit #113',
				},
				[5] = {
					['name'] = 'Unit #114',
				},
				[6] = {
					['name'] = 'Unit #115',
				},
				[7] = {
					['name'] = 'Unit #116',
				},
			},
			['groupId'] = 153,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 734869.19485719,
			['x'] = -239619.54171429,
			['firepower'] = {
				['min'] = 4,
				['max'] = 6,
			},
			['dead_last'] = 0,
			['name'] = '14 1st Artillery Division/4.Btry',
			['priority'] = 4,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'soft',
			},
		},
		['11 1st Artillery Division/1.Btry'] = {
			['elements'] = {
				[1] = {
					['name'] = 'Unit #060',
				},
				[2] = {
					['name'] = 'Unit #061',
				},
				[3] = {
					['name'] = 'Unit #064',
				},
				[4] = {
					['name'] = 'Unit #065',
				},
				[5] = {
					['name'] = 'Unit #070',
				},
				[6] = {
					['name'] = 'Unit #071',
				},
				[7] = {
					['name'] = 'Unit #072',
				},
			},
			['groupId'] = 147,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 643080.57142862,
			['x'] = -230897.14285715,
			['firepower'] = {
				['min'] = 4,
				['max'] = 6,
			},
			['dead_last'] = 0,
			['name'] = '11 1st Artillery Division/1.Btry',
			['priority'] = 4,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'soft',
			},
		},
		['16 1st Artillery Division/6.Btry'] = {
			['elements'] = {
				[1] = {
					['name'] = 'Unit #152',
				},
				[2] = {
					['name'] = 'Unit #153',
				},
				[3] = {
					['name'] = 'Unit #154',
				},
				[4] = {
					['name'] = 'Unit #155',
				},
				[5] = {
					['name'] = 'Unit #156',
				},
				[6] = {
					['name'] = 'Unit #157',
				},
				[7] = {
					['name'] = 'Unit #158',
				},
			},
			['groupId'] = 164,
			['foundOobGround'] = true,
			['class'] = 'vehicle',
			['ATO'] = true,
			['alive'] = 100,
			['y'] = 893868.6188572,
			['x'] = -284523.6042857,
			['firepower'] = {
				['min'] = 4,
				['max'] = 6,
			},
			['dead_last'] = 0,
			['name'] = '16 1st Artillery Division/6.Btry',
			['priority'] = 4,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'soft',
			},
		},
		['Rail Bridge Gumista East-FH56'] = {
			['elements'] = {
				[1] = {
					['y'] = 548488.25,
					['x'] = -204775.890625,
					['name'] = 'Rail Bridge Gumista East-FH56',
				},
			},
			['picture'] = {
				[1] = 'Bridge Positions FH37-FH47-FH56-FH66.png',
			},
			['ATO'] = true,
			['y'] = 548488.25,
			['x'] = -204775.890625,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Bridge Kul tubani-EJ80'] = {
			['elements'] = {
				[1] = {
					['y'] = 468062.34375,
					['x'] = -169308.046875,
					['name'] = 'Bridge Kul tubani-EJ80',
				},
			},
			['picture'] = {
				[1] = 'Bridges positions EJ80-EH99.png',
			},
			['ATO'] = true,
			['y'] = 468062.34375,
			['x'] = -169308.046875,
			['firepower'] = {
				['min'] = 2,
				['max'] = 2,
			},
			['dead_last'] = 0,
			['alive'] = 100,
			['priority'] = 1,
			['task'] = 'Strike',
			['attributes'] = {
				[1] = 'Bridge',
			},
		},
		['Sweep South'] = {
			['text'] = 'in the south area',
			['ATO'] = true,
			['y'] = 864192,
			['x'] = -246773,
			['firepower'] = {
				['min'] = 4,
				['max'] = 6,
			},
			['priority'] = 1,
			['task'] = 'Fighter Sweep',
			['attributes'] = {
			},
		},
	},
}
