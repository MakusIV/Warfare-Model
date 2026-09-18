supply_tab = {
	['red'] = {
		['Prohladniy Depot MP 24'] = {--        supply plant
			['integrity'] = 1, --             supply plant integrity    
			['supply_line_names'] = {--         table of supply lines supplyed by supply plant
				['Mozdok Airbase'] = {
					['integrity'] = 1,
					['airbase_supply'] = {
						['Mozdok'] = true,											
					},
				},			
				['Prohladniy Depot MP 24-BESLAN SUPPLY LINE'] = {
					['integrity'] = 1,
					['airbase_supply'] = {						 	
						['Beslan'] =  true,							
					},
				},
			},
		},
		['Peredovaya SUPPLY PLANT'] = {--        supply plant
			['integrity'] = 1, --             supply plant integrity    
			['supply_line_names'] = {--         table of supply lines supplyed by supply plant
				['Sochi-Adler Airbase'] = {
					['integrity'] = 1,
					['airbase_supply'] = {
						['Sochi-Adler'] = true,											
					},
				},			
				['Maykop-Khanskaya Airbase'] = {
					['integrity'] = 1,
					['airbase_supply'] = {						 	
						['Maykop-Khanskaya'] =  true,							
					},
				},
			},
		},
		['SUPPLY PLANT BAKSAN LP83'] = {--      supply plant
			['integrity'] = 1,
			['supply_line_names'] = {
				['BAKSAN-MINERALNYE SUPPLY LINE'] = {
					['integrity'] = 1,
					['airbase_supply'] = {	
						['Mineralnye-Vody'] = true,										
					},
				},
				['Nalchik Airbase'] = {
					['integrity'] = 1,
					['airbase_supply'] = {
						['Nalchik'] = true,											
					},
				},
				['BAKSAN-MOZDOK SUPPLY LINE'] = {
					['integrity'] = 1,
					['airbase_supply'] = {
						['Mozdok'] = true,													
					},
				},
			},
		},
		['CHERKESSK SUPPLY PLANT KP69'] = {--   supply plant
			['integrity'] = 1,
			['supply_line_names'] = {
				['Mineralnye-Vody Airbase'] = {
					['integrity'] = 1,
					['airbase_supply'] = {
						['Mineralnye-Vody'] = true,											
					},
				},
				['Russian Convoy 2'] = {
					['integrity'] = 1,
					['airbase_supply'] = {												
						['Sochi-Adler'] = true,
						['Maykop-Khanskaya'] = true,				
					},
				},				
			},
		},
		['Mineralnye-Vody Airbase'] = {
			['integrity'] = 1,
			['supply_line_names'] = {
				['Mineralnye-Vody Airbase'] = {
					['integrity'] = 1,
					['airbase_supply'] = {					
						['Reserves-R/41.IAP'] = true,			
						['Reserves-R/133.IAP'] = true,			
						['Reserves-R/135.IAP'] = true,	
						['Reserves-R/29.OSAP'] = true,		
															
					},
				},			
			},
		},
		['Beslan Airbase'] = {
			['integrity'] = 1,
			['supply_line_names'] = {
				['Beslan Airbase'] = {
					['integrity'] = 1,
					['airbase_supply'] = {
						['Reserves-R/37.IAP'] = true,
						['Reserves-R/127.IAP'] = true,
						['Reserves-R/123.IAP'] = true,
						['Reserves-R/115AS.IAP'] = true,
					},
				},
				['BESLAN-NOGIR FARP SUPPLY LINE'] = {
					['integrity'] = 1,
					['airbase_supply'] = {						
						["NOGIR FARP MN76"] = true,
						['Reserves-R/1st GHR'] = true,
					},
				},
				['BESLAN-LENIGORI FARP SUPPLY LINE'] = {
					['integrity'] = 1,
					['airbase_supply'] = {						
						["LENIGORI FARP MM56"] = true,
						['Reserves-R/13th GHR'] = true,
					},
				},		
				['BESLAN-TSKHINVALI FARP SUPPLY LINE'] = {
					['integrity'] = 1,
					['airbase_supply'] = {						
						["TSKHINVALI FARP MM27"] = true,
					},
				},						
			},
		},
		['Nalchik Airbase'] = {
			['integrity'] = 1,
			['supply_line_names'] = {
				['Nalchik Airbase'] = {
					['integrity'] = 1,
					['airbase_supply'] = {	
						['Reserves-R/19.IAP'] = true,				
						['Reserves-R/107.IAP'] = true,				
						['Reserves-R/111AS.IAP'] = true,	
						['Reserves-R/13.OSAP'] = true,	
					},
				},	
				['NALCHIK-TSKHINVALI FARP SUPPLY LINE'] = {
					['integrity'] = 1,
					['airbase_supply'] = {						
						["TSKHINVALI FARP MM27"] = true,
						['Reserves-R/2nd GHR'] = true,	
					},
				},				
			},
		},
		['Mozdok Airbase'] = {
			['integrity'] = 1,
			['supply_line_names'] = {
				['Mozdok Airbase'] = {
					['integrity'] = 1,
					['airbase_supply'] = {						
						['Reserves-R/117.IAP'] = true,
						['Reserves-R/113.IAP'] = true,						
					},
				},				
			},
		},		
		['Krasnodar-Center Airbase'] = {
			['integrity'] = 1,
			['supply_line_names'] = {
				['Krasnodar-Center Airbase'] = {
					['integrity'] = 1,
					['airbase_supply'] = {													
						['Reserves-R/159.IAP'] = true,	
						['Reserves-R/25.OSAP'] = true,		
															
					},
				},	
				['Maykop-Khanskaya Airbase'] = {
					['integrity'] = 1,
					['airbase_supply'] = {						
						['Reserves-R/81.IAP'] = true,
						['Reserves-R/61.IAP'] = true,
						['Reserves-R/27.OSAP'] = true,								
						['Reserves-R/115.IAP'] = true,
					},
				},
				['Anapa-Vityazevo Airbase'] = {
					['integrity'] = 1,
					['airbase_supply'] = {												
						['Reserves-R/23.OSAP'] = true,														
					},
				},	
				['Sochi-Adler Airbase'] = {
					['integrity'] = 1,
					['airbase_supply'] = {												
						['Reserves-R/23.OSAP'] = true,														
					},
				},				
			},
		},
	},
	['blue'] = {
		['SUPPLY PLANT DAPNARI KM76'] = {--      supply plant: Gori Farp, Ambrolauri Farp, Kobuleti, Khashuri Farp
			['integrity'] = 1,
			['supply_line_names'] = {
				['Bridge Supply Line Marneuli - Tbilisi'] = {
					['integrity'] = 1,
					['airbase_supply'] = {	
						['GORI FARP MM25'] = true,																	
					},
				},
				['Rail Bridge Dapnari-KM76'] = {
					['integrity'] = 1,
					['airbase_supply'] = {
						['Kobuleti'] = true,											
					},
				},
				['Bridge Dapnari-KM76'] = {
					['integrity'] = 1,
					['airbase_supply'] = {
						['Kobuleti'] = true,											
					},
				},
				['Bridge Vartsihe-LM16'] = {
					['integrity'] = 1,
					['airbase_supply'] = {
						['KHASHURI FARP LM84'] = true,											
					},
				},
				['Bridge Geguti-LM17'] = {
					['integrity'] = 1,
					['airbase_supply'] = {
						['KHASHURI FARP LM84'] = true,											
					},
				},
				['Bridge Kutaisi-LM18'] = {
					['integrity'] = 1,
					['airbase_supply'] = {
						['AMBROLAURI FARP LN41'] = true,											
					},
				},
				['Kutaisi Airbase'] = {
					['integrity'] = 1,
					['airbase_supply'] = {
						['Kutaisi'] = true,													
					},
				},
				['bridge GORI'] = {
					['integrity'] = 1,
					['airbase_supply'] = {
						['GORI FARP MM25'] = true,													
					},
				},
			},
		},
		['SUPPLY PLANT  MARNEULI ML89'] = {--      supply plant: Gori Farp, Tbilissi
			['integrity'] = 1,
			['supply_line_names'] = {
				['Bridge Supply Line Gori - Tbilisi'] = {
					['integrity'] = 1,
					['airbase_supply'] = {	
						['GORI FARP MM25'] = true,										
					},
				},
				['Tbilissi Airbase'] = {
					['integrity'] = 1,
					['airbase_supply'] = {
						['Tbilissi-Lochini'] = true,											
					},
				},			
			},
		},
		['Sukhumi Airbase Strategics'] = {  -- supply plant: Sukhumi, Senaki, Kobuleti
			['integrity'] = 1,
			['supply_line_names'] = {
				['Sukhumi Airbase Strategics'] = {
					['integrity'] = 1,
					['airbase_supply'] = {
						['Sukhumi'] = true,
					},
				},
				['Rail Bridge Tagiloni-GH21'] = {
					['integrity'] = 1,
					['airbase_supply'] = {
						['Senaki-Kolkhi'] = true,													
					},
				},
				['Bridge Koki-GH20'] = {
					['integrity'] = 1,
					['airbase_supply'] = {
						['Kobuleti'] = true,													
					},
				},
			},
		},
		['CVN-71 Theodore Roosevelt'] = {--supply: kutaisi
			['integrity'] = 1,
			['supply_line_names'] = {
				['CVN-71 Theodore Roosevelt'] = {
					['integrity'] = 1,
					['airbase_supply'] = {
						['CVN-71 Theodore Roosevelt'] = true,
						['Kutaisi'] = true,																					
						['Reserves-R/VF-101'] = true,			
						['Reserves-R/VAW-125'] = true,			
						['Reserves-R/VS-27'] = true,								
						['Reserves-R/VS-21'] = true,															
					},
				},
			},
		},
		['CVN-74 John C. Stennis'] = {-- supply: batumi
			['integrity'] = 1,
			['supply_line_names'] = {
				['CVN-74 John C. Stennis'] = {
					['integrity'] = 1,
					['airbase_supply'] = {	
						['CVN-74 John C. Stennis'] = true,					
						['Batumi'] = true,									
						['Reserves-R/VF-118/GA'] = true,																					
						['Reserves-R/VS-22'] = true,																						
						['Reserves-R/VMFA-159'] = true,						
						['Reserves-R/58 TFS'] = true,						
					},
				},
			},
		},
		['Kutaisi Airbase'] = {
			['integrity'] = 1,
			['supply_line_names'] = {
				['Kutaisi Airbase'] = {
					['integrity'] = 1,
					['airbase_supply'] = {
						['Kutaisi'] = true,												
						['Reserves-R/F7'] = true,												
					},
				},			
			},
		},
		['Kobuleti Airbase'] = { 
			['integrity'] = 1,
			['supply_line_names'] = {
				['Kobuleti Airbase'] = {
					['integrity'] = 1,
					['airbase_supply'] = {
						['Kobuleti'] = true,	
						--['69 BS'] = true,
						['Reserves-R/69 BS'] = true,										
					},
				},
			},
		},		
		['Batumi Airbase'] = {
			['integrity'] = 1,
			['supply_line_names'] = {
				['Batumi Airbase'] = {
					['integrity'] = 1,
					['airbase_supply'] = {	
						['Batumi'] = true,																		
						['Reserves-R/VMFA-151'] = true,						
						['Reserves-R/VMFA-157'] = true,		
						['Reserves-R/315th Air Division'] = true,																	
					},
				},
			},
		},
		['Senaki-Kolkhi Airbase'] = {
			['integrity'] = 1,
			['supply_line_names'] = {
				['Senaki-Kolkhi Airbase'] = {
					['integrity'] = 1,
					['airbase_supply'] = {		
						['Senaki-Kolkhi'] = true,										
						['Reserves-R/GA 7rd AS'] = true,							
						['Reserves-R/GA 5rd TS'] = true,
						['Reserves-R/801 ARS'] = true,											
					},
				},				
			},
		},
		['Tbilissi Airbase'] = {
			['integrity'] = 1,
			['supply_line_names'] = {
				['Tbilissi-Lochini'] = {
					['integrity'] = 1,
					['airbase_supply'] = {		
						['Tbilissi'] = true,						
						['Reserves-R/F9'] = true,
						['Reserves-R/174 ARW'] = true,		
						['Reserves-R/GAH 2rd'] = true, --for Ambrolauri FARP														
					},
				},
				['Vaziani'] = {
					['integrity'] = 1,
					['airbase_supply'] = {		
						['Vaziani'] = true,					
						['Reserves-R/GA 3rd AS'] = true,
						['Reserves-R/GA 4rd AS'] = true,
						['Reserves-R/6th Cavalry'] = true,	 --for Gori FARP
						['Reserves-R/17th Cavalry'] = true,	 --for KHASHURI FARP
					},
				},
			},			
		},
		['Sukhumi Airbase'] = {
			['integrity'] = 1,
			['supply_line_names'] = {
				['Sukhumi Airbase'] = {
					['integrity'] = 1,
					['airbase_supply'] = {	
						['Sukhumi'] = true,																			
						['Reserves-R/171 ARW'] = true,					
					},
				},				
			},
		},
		['Sukhumi Train Station - FH66'] = {
			['integrity'] = 1,
			['supply_line_names'] = {
				['Sukhumi Train Station - FH66'] = {
					['integrity'] = 1,
					['airbase_supply'] = {
						['Sukhumi'] = true,										
					},
				},				
			},
		},
		['Sukhumi-Babushara Train Station - FH74'] = {
			['integrity'] = 1,
			['supply_line_names'] = {
				['Sukhumi-Babushara Train Station - FH74'] = {
					['integrity'] = 1,
					['airbase_supply'] = {
						['Sukhumi'] = true,									
					},
				},		
			},
		},
		['Senaki-Kolkhi Train Station - KM58'] = {
			['integrity'] = 1,
			['supply_line_names'] = {
				['Senaki-Kolkhi Train Station - KM58'] = {
					['integrity'] = 1,
					['airbase_supply'] = {
						['Senaki-Kolkhi'] = true,					
					},
				},				
			},
		},
		['Kobuleti Train Station - GG44'] = {
			['integrity'] = 1,
			['supply_line_names'] = {
				['Kobuleti Train Station - GG44'] = {
					['integrity'] = 1,
					['airbase_supply'] = {
						['Kutaisi'] = true,					
					},
				},
			},
		},
		--[[

		['Gudauta Airbase'] = { -- watch! Gudauta not exists in oob_air_init. Delete it or insert an air groub with base = Kobuleti
			['integrity'] = 1,
			['supply_line_names'] = {
				['Gudauta Airbase'] = { -- attention: not present in oob_air_init
					['integrity'] = 1,
					['airbase_supply'] = {
						['Gudauta'] = true,										
					},
				},
			},
		},
		['Gudauta Train Station - FH37'] = {
			['integrity'] = 1,
			['supply_line_names'] = {
				['Gudauta Train Station - FH37'] = {
					['integrity'] = 1,
					['airbase_supply'] = {
						['Gudauta'] = true, -- watch! Kobuleti not exists in oob_air_init. Delete it or insert an air groub with base = Kobuleti
						['Kutaisi'] = true,
					},
				},			
			},
		},
		]]	
	},
}

-- SUPPLY PLANT:
-- RED: SUPPLY PLANT BAKSAN LP83, "CHERKESSK SUPPLY PLANT KP69, Prohladniy Depot MP 24
-- BLUE:  SUPPLY PLANT DAPNARI KM76, 
---