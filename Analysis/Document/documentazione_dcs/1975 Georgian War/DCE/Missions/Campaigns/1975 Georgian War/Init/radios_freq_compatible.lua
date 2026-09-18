--cree pour controler les plages des frequences
--Initiated by MAIN_NextMission.lua
-------------------------------------------------------------------------------------------------------

if not versionDCE then 
	versionDCE = {} 
end

               -- VERSION --

versionDCE["radio_freq_compatible.lua"] = "OB.1.0.0"

-------------------------------------------------------------------------------------------------------
-- Old_Boy rev. OB.1.0.0: update freq with mod M34B_a
-- last modification:  M34B_a
-- if not versionDCE then versionDCE = {} end
-- versionDCE["radios_freq_compatible.lua"] = "1.2.27"
------------------------------------------------------------------------------------------------------- 
-- miguel21 modification M34B_a  custom FrequenceRadio (Ba A-4E-C bug)(w correction F16)(v delete Radio3 AV8)(u: L39+Su25)(t: radioname)(p LVHF)(m: add AH-64D_BLK_II)(kl: fix Mi24 VHF/UHF)(i: 3 frequency bands)(j: add Mi24)
-- miguel21 modification M34_b  custom FrequenceRadio
-- -------------------------------------------------------------------------------------------------------



-- miguel21 modification M34.j  custom FrequenceRadio (i  3 frequency bands)(j: add Mi24)
-- miguel21 modification M34.b  custom FrequenceRadio


frequency = {
	["F-86F Sabre"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1
				UHF = {
					min = 225,				--minimum radio frequency in mHz
					max = 269,				--maxium  radio frequency in mHz
				},
				nbCanal = 18,
			},
		},
	},
	["A-4C"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1
				UHF = {
					min = 225,				--minimum radio frequency in mHz   UHF ARC-27 20 preset channels
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
			},
		},
	},
	["A-4E-C"] = {							--A-4C
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1
				UHF = {
					min = 225,				--minimum radio frequency in mHz   UHF ARC-27 20 preset channels
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
			},
		},
	},
	["A-10A"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {
				LVHF = {
					min = 36,				--minimum radio frequency in mHz
					max = 76,				--maxium  radio frequency in mHz
				},
				VHF = {
					min = 116,
					max = 151.975,
				},
				UHF = {
					min = 225,
					max = 399.98,
				},
				nbCanal = 0,
				FC3 = true,
				FC3Frequency = 124,
			},
		},	
	},
	["A-10C"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1 AN/ARC 164 UHF
				UHF = {
					min = 225,				--minimum radio frequency in mHz  
					max = 399.975,			--maxium  radio frequency in mHz
				},
				nbCanal = 0,				--TODO check	
			},
			[2] = {						--radio 2 AN/ARC 186(V) VHF AM # 1  VHF FM #2
				LVHF = {
					min = 36,				--minimum radio frequency in mHz
					max = 76,				--maxium  radio frequency in mHz
				},
				VHF = {
					min = 116,				--minimum radio frequency in mHz 
					max = 151.975,			--maxium  radio frequency in mHz
				},	
				nbCanal = 0,			-- ???? TODO check		
			},
		},
	},
	["A-10C_2"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1 AN/ARC 164 UHF
				UHF = {
					min = 225,				--minimum radio frequency in mHz  
					max = 399.975,			--maxium  radio frequency in mHz
				},
				nbCanal = 0,				--TODO check	
			},
			[2] = {						--radio 2 AN/ARC 186(V) VHF AM # 1  VHF FM #2
				LVHF = {
					min = 36,				--minimum radio frequency in mHz
					max = 76,				--maxium  radio frequency in mHz
				},
				VHF = {
					min = 116,				--minimum radio frequency in mHz 
					max = 151.975,			--maxium  radio frequency in mHz
				},	
				nbCanal = 0,			-- ???? TODO check		
			},
		},
	},

	["F-5E-3"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {				
				UHF = {
					min = 225,				--minimum radio frequency in mHz   UHF ARC-164 20 preset channels
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
			},			
		},
	},
	["F-14B"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1
				UHF = {
					min = 225,				--minimum radio frequency in mHz    UHF ARC-159    20  preset channels
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
			},
			[2] = {						--radio 2
				VHF = {
					min = 108,				--minimum radio frequency in mHz   V/UHF FM ARC-210 20 preset channels
					max = 173,				--maxium  radio frequency in mHz
				},
				UHF = {
					min = 225,				--minimum radio frequency in mHz   MIN 108 MAX 399
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 30,
			},
		},
	},
	["F-14A-135-GR"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1
				UHF = {
					min = 225,				--minimum radio frequency in mHz    UHF ARC-159    20  preset channels
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
			},
			[2] = {						--radio 2
				VHF = {
					min = 108,				--minimum radio frequency in mHz   V/UHF FM ARC-210 20 preset channels
					max = 173,				--maxium  radio frequency in mHz
				},
				UHF = {
					min = 225,				--minimum radio frequency in mHz   MIN 108 MAX 399
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 30,
			},
		},
	},
	["F-16C_50"] = {
		radio = {			
			[1] = {						--radio 1 AN/ARC-164
				UHF = {
					min = 225,				--minimum radio frequency in mHz 
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
			},
			[2] = {						--radio 2 AN/ARC-222
				LVHF = {
					min = 30,				--minimum radio frequency in mHz 
					max = 87,				--maxium  radio frequency in mHz
				},
				VHF = {
					min = 116,				--minimum radio frequency in mHz   
					max = 151,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
			},
		},
	},
	["FA-18C_hornet"] = {
		radio = {						--range of radio frequencies of player aircraft			
			[1] = {						--radio 1
				LVHF = {
					min = 30,				--minimum radio frequency in mHz   V/UHF FM ARC-210 20 preset channels
					max = 87,				--maxium  radio frequency in mHz
				},
				VHF = {
					min = 118,				--minimum radio frequency in mHz   V/UHF FM ARC-210 20 preset channels
					max = 173,				--maxium  radio frequency in mHz
				},
				UHF = {
					min = 225,				--minimum radio frequency in mHz   V/UHF FM ARC-210 20 preset channels
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
			},
			[2] = {						--radio 2
				LVHF = {
					min = 30,				--minimum radio frequency in mHz   V/UHF FM ARC-210 20 preset channels
					max = 87,				--maxium  radio frequency in mHz
				},
				VHF = {
					min = 118,				--minimum radio frequency in mHz   V/UHF FM ARC-210 20 preset channels
					max = 173,				--maxium  radio frequency in mHz
				},
				UHF = {
					min = 225,				--minimum radio frequency in mHz   V/UHF FM ARC-210 20 preset channels
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
			},
		},
	},
	["AJS37"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						-- V/UHF FR 22 radio
				VHF = {
					min = 103,				--minimum radio frequency in mHz 	TODO a fonfirmer avec notice
					max = 155.975,			--maxium  radio frequency in mHz
				},
				UHF = {
					min = 225,				--minimum radio frequency in mHz  
					max = 399.95,			--maxium  radio frequency in mHz
				},
				nbCanal = 7,
			},
			-- [2] = {						--radio 1 mode 2
				-- min = 103,				--minimum radio frequency in mHz   VHF FR-22 25 Khz interval    10  preset channels
				-- max = 155,				--maxium  radio frequency in mHz
			-- },
			-- [3] = {						--radio 2
				-- min = 228,				--minimum radio frequency in mHz   VHF FR-24 3 preset channels only
				-- max = 399,				--maxium  radio frequency in mHz
			-- },
		},
	},
	["AV8BNA"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						-- V/UHF FM ARC-210 26 preset channels
				LVHF = {
					min = 30,				--minimum radio frequency in mHz  30 à 400, mais on limite artificielement pour harmoniser avec les autres types d avion
					max = 87,				--maxium  radio frequency in mHz
				},
				VHF = {
					min = 118,				--minimum radio frequency in mHz 
					max = 173,				--maxium  radio frequency in mHz
				},
				UHF = {
					min = 225,				--minimum radio frequency in mHz  
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 26,
			},
			[2] = {						-- V/UHF FM ARC-210 26 preset channels
				LVHF = {
					min = 30,				--minimum radio frequency in mHz  
					max = 87,				--maxium  radio frequency in mHz
				},
				VHF = {
					min = 118,				--minimum radio frequency in mHz  
					max = 173,				--maxium  radio frequency in mHz
				},
				UHF = {
					min = 225,				--minimum radio frequency in mHz   
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 26,
			},			
			-- [3] = {						--V/UHF FM ARC-210 30 preset channels  RCS
				-- LVHF = {
					-- min = 30,				--minimum radio frequency in mHz  
					-- max = 87,				--maxium  radio frequency in mHz
				-- },
				-- VHF = {
					-- min = 118,				--minimum radio frequency in mHz   
					-- max = 173,				--maxium  radio frequency in mHz
				-- },
				-- UHF = {
					-- min = 225,				--minimum radio frequency in mHz   
					-- max = 399,				--maxium  radio frequency in mHz
				-- },
				-- nbCanal = 30,
			-- },
		},
	},
	["M-2000C"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1
				UHF = {
					min = 225,				--minimum radio frequency in mHz  
					max = 400,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
				name = "Poste Vert",
			},
			[2] = {						--radio 2
				VHF = {
					min = 118,				--minimum radio frequency in mHz   V/UHF FM ARC-210 20 preset channels
					max = 140,				--maxium  radio frequency in mHz
				},
				UHF = {
					min = 225,				--minimum radio frequency in mHz 
					max = 400,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
				name = "Poste Rouge",
			},
		},
	},
	-- ["Mirage-F1CE"] = {
		-- radio = {						--range of radio frequencies of player aircraft
			-- [1] = {						--radio 1
				-- UHF = {
					-- min = 225,				--minimum radio frequency in mHz  
					-- max = 400,				--maxium  radio frequency in mHz
				-- },
				-- nbCanal = 20,
				-- name = "Poste Vert",
			-- },
			-- [2] = {						--radio 2
				-- VHF = {
					-- min = 118,				--minimum radio frequency in mHz   V/UHF FM ARC-210 20 preset channels
					-- max = 143,				--maxium  radio frequency in mHz
				-- },
				-- UHF = {
					-- min = 225,				--minimum radio frequency in mHz 
					-- max = 400,				--maxium  radio frequency in mHz
				-- },
				-- nbCanal = 20,
				-- name = "Poste Rouge",
			-- },
		-- },
	-- },	
	
	["Mirage-F1CE"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1
				VHF = {
					min = 118,				--minimum radio frequency in mHz   V/UHF FM ARC-210 20 preset channels
					max = 143,				--maxium  radio frequency in mHz
				},
				UHF = {
					min = 225,				--minimum radio frequency in mHz 
					max = 400,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
				name = "Poste Vert",
			},			
			[2] = {						--radio 2
				UHF = {
					min = 225,				--minimum radio frequency in mHz  
					max = 400,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
				name = "Poste Rouge",
			},

		},
	},	
	
	["SA342M"] = {
		helicopter = true,
		prefFreqPackage = {
			nRadio = 2,
			range = "VHF",
			},
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1
				LVHF = {
					min = 30,				--minimum radio frequency in mHz
					max = 50,				--maxium  radio frequency in mHz
				},
				nbCanal = 8,
				name = "FM",
			},
			[2] = {						--radio 2
				VHF = {
					min = 118,				--minimum radio frequency in mHz
					max = 143,				--maxium  radio frequency in mHz
				},
				nbCanal = 0,
				name = "VHF Radio",
			},
			[3] = {						--radio 3
				UHF = {
					min = 225,				--minimum radio frequency in mHz
					max = 399.9,				--maxium  radio frequency in mHz
				},
				nbCanal = 0,
				name = "UHF Radio",
			},
		},
	},
	["AH-64D_BLK_II"] = {
		helicopter = true,
		-- prefFreqPackage = {
			-- nRadio = 2,
			-- range = "VHF",
			-- },
		radio = {								--range of radio frequencies of player aircraft
			[1] = {								--radio 1 name = _("ARC-186"),
				VHF = {
					min = 108.0,				--minimum radio frequency in mHz
					max = 151.975,				--maxium  radio frequency in mHz
				},
				nbCanal = 10,
				name = "VHF",
			},
			[2] = {								--radio 2 name = _("ARC-164"),
				UHF = {
					min = 225,					--minimum radio frequency in mHz
					max = 399.975,				--maxium  radio frequency in mHz
				},
				nbCanal = 10,
				name = "UHF",
			},
			[3] = {								--radio 3 name = _("FM 1: ARC-201D"),
				LVHF = {
					min = 30.0,					--minimum radio frequency in mHz
					max = 87.995,				--maxium  radio frequency in mHz
				},
				nbCanal = 10,
				name = "FM 1",
			},
			[4] = {								--radio 4 name = _("FM 2: ARC-201D"),
				LVHF = {
					min = 30.0,					--minimum radio frequency in mHz
					max = 87.995,				--maxium  radio frequency in mHz
				},
				nbCanal = 10,
				name = "FM 2",
			},
			[5] = {						--radio 3 Yadro1 HF
				HF = {
					min = 2,				--minimum radio frequency in mHz
					max = 17.999,			--maxium  radio frequency in mHz
				},
				nbCanal = 0,
				name = "HF  ",
			},
		},
	},
	["UH-1H"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1
				UHF = {
					min = 225,				--minimum radio frequency in mHz
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
			},
		},
		helicopter = true,
	},	
	["L-39C"] = {
		radio = {
			[1] = {
				VHF = {
					min = 118,
					max = 224.995,
				},
				UHF = {
					min = 225,
					max = 399.95,
				},
				nbCanal = 20,
				startCanal = 0,
				name = "R-832M"
			},
		},	
	},
	["Su-25"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {
				VHF = {
					min = 100,
					max = 224.995,
				},
				UHF = {
					min = 225,
					max = 399.98,
				},
				nbCanal = 0,
				FC3 = true,
				FC3Frequency = 124,
			},
		},	
	},
	["Su-25T"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {
				VHF = {
					min = 100,
					max = 224.995,
				},
				UHF = {
					min = 225,
					max = 399.98,
				},
				nbCanal = 0,
				FC3 = true,
				FC3Frequency = 124,
			},
		},	
	},
	["MiG-19P"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1 RSIU 4 V VHF
				VHF = {
					min = 100,				--minimum radio frequency in mHz   
					max = 150,				--maxium  radio frequency in mHz
				},
				nbCanal = 6,
			},
		},	
	},
	["MiG-21Bis"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1  RSIU 5V 
				VHF = {
					min = 118,				--minimum radio frequency in mHz   RS-832 0 to 19 preset channels only
					max = 224.995,				--maxium  radio frequency in mHz
				},
				UHF = {
					min = 225,				--minimum radio frequency in mHz  
					max = 390,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
				startCanal = 0,
				name = "RS-832",
			},
		},
	},
	["JF-17"] = {
		radio = {			
			[1] = {						--radio 1
				LVHF = {
					min = 30,				--minimum radio frequency in mHz 
					max = 100,				--maxium  radio frequency in mHz
				},
				VHF = {
					min = 101,				--minimum radio frequency in mHz 
					max = 224,				--maxium  radio frequency in mHz
				},
				UHF = {
					min = 225,				--minimum radio frequency in mHz  
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
			},
		},
	},

	["Mi-8MT"] = {
		helicopter = true,
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1
				UHF = {
					min = 220,				--minimum radio frequency in mHz
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
				name = "R-863",
				startCanal = 0,
			},
			[2] = {						--radio 2
				LVHF = {
					min = 20,				--minimum radio frequency in mHz
					max = 59.97,				--maxium  radio frequency in mHz
				},
				nbCanal = 10,
				name = "R-868",
				startCanal = 0,
			},
			[3] = {						--radio 3 Yadro1 HF
				HF = {
					min = 2,				--minimum radio frequency in mHz
					max = 17.999,			--maxium  radio frequency in mHz
				},
				nbCanal = 0,
				name = "Yadro",
			},
		},
	},
	["Mi-24P"] = {
		helicopter = true,
		radio = {
			[1] = {						--radio 1 R863 VHF/UHF
				VHF = {
					min = 100,				--minimum radio frequency in mHz
					max = 225,				--maxium  radio frequency in mHz
				},
				UHF = {
					min = 226,				--minimum radio frequency in mHz
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
				name = "R-863",
				startCanal = 0,
			},
			[2] = {						--radio 2 R828 LVHF
				LVHF = {
					min = 20,				--minimum radio frequency in mHz
					max = 59.97,			--maxium  radio frequency in mHz
				},
				nbCanal = 10,
				name = "R-868",
				startCanal = 0,
			},
			[3] = {						--radio 3 Yadro1 HF
				HF = {
					min = 2,				--minimum radio frequency in mHz
					max = 17.999,			--maxium  radio frequency in mHz
				},
				nbCanal = 0,
				name = "Yadro",
			},
		},
	},
	["Ka-50"] = {
		helicopter = true,
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1
				LVHF = {
					min = 20,				--minimum radio frequency in mHz
					max = 59,				--maxium  radio frequency in mHz
				},
				nbCanal = 10,
			},
			[2] = {						--radio 2 simule la frequence FC3 de DCS
				VHF = {
					min = 100,				--minimum radio frequency in mHz
					max = 224,				--maxium  radio frequency in mHz
				},
				UHF = {
					min = 225,				--minimum radio frequency in mHz
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 0,
			},
			-- [2] = {						--radio 2
				-- min = 0.215,				--minimum radio frequency in mHz
				-- max = 1.065,				--maxium  radio frequency in mHz
				-- nbCanal = 16,
			-- },
		},
	},
	["P-51D-30-NA"] = {
		radio = {							
			[1] = {						--radio  SCR 522 A VHF RADIO
				VHF = {
					min = 100,				--minimum radio frequency in mHz
					max = 156,				--maxium  radio frequency in mHz
				},
				nbCanal = 4,
			},
		},
	},
	["P-47D-30"] = {
		radio = {									
			[1] = {						--radio SCR 522 A VHF RADIO
				VHF = {
					min = 100,				--minimum radio frequency in mHz
					max = 156,				--maxium  radio frequency in mHz
				},
				nbCanal = 4,
			},
		},
	},
	["SpitfireLFMkIX"] = {
		radio = {									
			[1] = {						--radio A R I 1063 type HF
				VHF = {
					min = 38,				--minimum radio frequency in mHz
					max = 156,				--maxium  radio frequency in mHz
				},
				nbCanal = 4,
			},
		},
	},
	["Bf-109K-4"] = {
		radio = {									
			[1] = {						--radio 4 is equipped with a FUG 16ZY radio transmitter and receiver.
				FM = {
					min = 38.4,				--minimum radio frequency in mHz
					max = 42.4,				--maxium  radio frequency in mHz
				},
				nbCanal = 4,
			},
		},
	},
}	


-- previous freq
--[[frequency = {
	["F-86F Sabre"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1
				UHF = {
					min = 225,				--minimum radio frequency in mHz
					max = 269,				--maxium  radio frequency in mHz
				},
				nbCanal = 18,
			},
		},
	},
	["A-4C"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1
				UHF = {
					min = 225,				--minimum radio frequency in mHz   UHF ARC-27 20 preset channels
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
			},
		},
	},
	["A-4E-C"] = {							--A-4C
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1
				UHF = {
					min = 225,				--minimum radio frequency in mHz   UHF ARC-27 20 preset channels
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
			},
		},
	},
	["A-10C"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1 AN/ARC 164 UHF
				UHF = {
					min = 225,				--minimum radio frequency in mHz  
					max = 399.975,			--maxium  radio frequency in mHz
				},
				nbCanal = 0,				--TODO check	
			},
			[2] = {						--radio 2 AN/ARC 186(V) VHF AM # 1  VHF FM #2
				FM = {
					min = 36,				--minimum radio frequency in mHz
					max = 76,				--maxium  radio frequency in mHz
				},
				VHF = {
					min = 116,				--minimum radio frequency in mHz 
					max = 151.975,			--maxium  radio frequency in mHz
				},	
				nbCanal = 0,			-- ???? TODO check		
			},
		},
	},
	["A-10C_2"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1 AN/ARC 164 UHF
				UHF = {
					min = 225,				--minimum radio frequency in mHz  
					max = 399.975,			--maxium  radio frequency in mHz
				},
				nbCanal = 0,				--TODO check	
			},
			[2] = {						--radio 2 AN/ARC 186(V) VHF AM # 1  VHF FM #2
				FM = {
					min = 36,				--minimum radio frequency in mHz
					max = 76,				--maxium  radio frequency in mHz
				},
				VHF = {
					min = 116,				--minimum radio frequency in mHz 
					max = 151.975,			--maxium  radio frequency in mHz
				},	
				nbCanal = 0,			-- ???? TODO check		
			},
		},
	},
	["F-5E-3"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {				
				UHF = {
					min = 225,				--minimum radio frequency in mHz   UHF ARC-164 20 preset channels
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
			},			
		},
	},
	["F-14B"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1
				UHF = {
					min = 225,				--minimum radio frequency in mHz    UHF ARC-159    20  preset channels
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
			},
			[2] = {						--radio 2
				VHF = {
					min = 108,				--minimum radio frequency in mHz   V/UHF FM ARC-210 20 preset channels
					max = 173,				--maxium  radio frequency in mHz
				},
				UHF = {
					min = 225,				--minimum radio frequency in mHz   MIN 108 MAX 399
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 30,
			},
		},
	},
	["F-14A-135-GR"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1
				UHF = {
					min = 225,				--minimum radio frequency in mHz    UHF ARC-159    20  preset channels
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
			},
			[2] = {						--radio 2
				VHF = {
					min = 108,				--minimum radio frequency in mHz   V/UHF FM ARC-210 20 preset channels
					max = 173,				--maxium  radio frequency in mHz
				},
				UHF = {
					min = 225,				--minimum radio frequency in mHz   MIN 108 MAX 399
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 30,
			},
		},
	},
	["F-16C_50"] = {
		radio = {			
			[1] = {						--radio 1 AN/ARC-164
				UHF = {
					min = 225,				--minimum radio frequency in mHz 
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
			},
			[2] = {						--radio 2 AN/ARC-222
				FM = {
					min = 30,				--minimum radio frequency in mHz 
					max = 87,				--maxium  radio frequency in mHz
				},
				VHF = {
					min = 116,				--minimum radio frequency in mHz   
					max = 155,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
			},
		},
	},
	["FA-18C_hornet"] = {
		radio = {						--range of radio frequencies of player aircraft			
			[1] = {						--radio 1
				LVHF = {
					min = 30,				--minimum radio frequency in mHz   V/UHF FM ARC-210 20 preset channels
					max = 87,				--maxium  radio frequency in mHz
				},
				VHF = {
					min = 118,				--minimum radio frequency in mHz   V/UHF FM ARC-210 20 preset channels
					max = 173,				--maxium  radio frequency in mHz
				},
				UHF = {
					min = 225,				--minimum radio frequency in mHz   V/UHF FM ARC-210 20 preset channels
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
			},
			[2] = {						--radio 2
				LVHF = {
					min = 30,				--minimum radio frequency in mHz   V/UHF FM ARC-210 20 preset channels
					max = 87,				--maxium  radio frequency in mHz
				},
				VHF = {
					min = 118,				--minimum radio frequency in mHz   V/UHF FM ARC-210 20 preset channels
					max = 173,				--maxium  radio frequency in mHz
				},
				UHF = {
					min = 225,				--minimum radio frequency in mHz   V/UHF FM ARC-210 20 preset channels
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
			},
		},
	},
	["AJS37"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						-- V/UHF FR 22 radio
				VHF = {
					min = 103,				--minimum radio frequency in mHz 	TODO a fonfirmer avec notice
					max = 155.975,			--maxium  radio frequency in mHz
				},
				UHF = {
					min = 225,				--minimum radio frequency in mHz  
					max = 399.95,			--maxium  radio frequency in mHz
				},
				nbCanal = 7,
			},
			-- [2] = {						--radio 1 mode 2
				-- min = 103,				--minimum radio frequency in mHz   VHF FR-22 25 Khz interval    10  preset channels
				-- max = 155,				--maxium  radio frequency in mHz
			-- },
			-- [3] = {						--radio 2
				-- min = 228,				--minimum radio frequency in mHz   VHF FR-24 3 preset channels only
				-- max = 399,				--maxium  radio frequency in mHz
			-- },
		},
	},
	["AV8BNA"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						-- V/UHF FM ARC-210 26 preset channels
				FM = {
					min = 30,				--minimum radio frequency in mHz  30 à 400, mais on limite artificielement pour harmoniser avec les autres types d avion
					max = 87,				--maxium  radio frequency in mHz
				},
				VHF = {
					min = 118,				--minimum radio frequency in mHz 
					max = 173,				--maxium  radio frequency in mHz
				},
				UHF = {
					min = 225,				--minimum radio frequency in mHz  
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 26,
			},
			[2] = {						-- V/UHF FM ARC-210 26 preset channels
				FM = {
					min = 30,				--minimum radio frequency in mHz  
					max = 87,				--maxium  radio frequency in mHz
				},
				VHF = {
					min = 118,				--minimum radio frequency in mHz  
					max = 173,				--maxium  radio frequency in mHz
				},
				UHF = {
					min = 225,				--minimum radio frequency in mHz   
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 26,
			},			
			[3] = {						--V/UHF FM ARC-210 30 preset channels  RCS
				FM = {
					min = 30,				--minimum radio frequency in mHz  
					max = 87,				--maxium  radio frequency in mHz
				},
				VHF = {
					min = 118,				--minimum radio frequency in mHz   
					max = 173,				--maxium  radio frequency in mHz
				},
				UHF = {
					min = 225,				--minimum radio frequency in mHz   
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 30,
			},
		},
	},
	["M-2000C"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1
				UHF = {
					min = 225,				--minimum radio frequency in mHz  
					max = 400,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
			},
			[2] = {						--radio 2
				VHF = {
					min = 118,				--minimum radio frequency in mHz   V/UHF FM ARC-210 20 preset channels
					max = 140,				--maxium  radio frequency in mHz
				},
				UHF = {
					min = 225,				--minimum radio frequency in mHz 
					max = 400,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
			},
		},
	},
	["Mirage-F1CE"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1
				VHF = {
					min = 118,				--minimum radio frequency in mHz   V/UHF FM ARC-210 20 preset channels
					max = 143,				--maxium  radio frequency in mHz
				},
				UHF = {
					min = 225,				--minimum radio frequency in mHz 
					max = 400,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
				name = "Poste Vert",
			},			
			[2] = {						--radio 2
				UHF = {
					min = 225,				--minimum radio frequency in mHz  
					max = 400,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
				name = "Poste Rouge",
			},

		},
	},	
	["MiG-19P"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1 RSIU 4 V VHF
				VHF = {
					min = 100,				--minimum radio frequency in mHz   
					max = 150,				--maxium  radio frequency in mHz
				},
				nbCanal = 6,
			},
		},	
	},
	["MiG-21Bis"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1  RSIU 5V 
				VHF = {
					min = 118,				--minimum radio frequency in mHz   RS-832 0 to 19 preset channels only
					max = 224.995,				--maxium  radio frequency in mHz
				},
				UHF = {
					min = 225,				--minimum radio frequency in mHz  
					max = 390,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
				startCanal = 0,
				name = "RS-832",
			},
		},
	},
	["JF-17"] = {
		radio = {			
			[1] = {						--radio 1
				LVHF = {
					min = 30,				--minimum radio frequency in mHz 
					max = 100,				--maxium  radio frequency in mHz
				},
				VHF = {
					min = 101,				--minimum radio frequency in mHz 
					max = 224,				--maxium  radio frequency in mHz
				},
				UHF = {
					min = 225,				--minimum radio frequency in mHz  
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
			},
		},
	},
	["SA342M"] = {
		helicopter = true,
		prefFreqPackage = {
			nRadio = 2,
			range = "VHF",
			},
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1
				FM = {
					min = 30,				--minimum radio frequency in mHz
					max = 50,				--maxium  radio frequency in mHz
				},
				nbCanal = 8,
			},
			[2] = {						--radio 2
				VHF = {
					min = 118,				--minimum radio frequency in mHz
					max = 143,				--maxium  radio frequency in mHz
				},
				nbCanal = 0,
			},
			[3] = {						--radio 3
				UHF = {
					min = 225,				--minimum radio frequency in mHz
					max = 399.9,				--maxium  radio frequency in mHz
				},
				nbCanal = 0,
			},
		},

	},
	["AH-64D_BLK_II"] = {
		helicopter = true,
		-- prefFreqPackage = {
			-- nRadio = 2,
			-- range = "VHF",
			-- },
		radio = {								--range of radio frequencies of player aircraft
			[1] = {								--radio 1 name = _("ARC-186"),
				VHF = {
					min = 108.0,				--minimum radio frequency in mHz
					max = 151.975,				--maxium  radio frequency in mHz
				},
				nbCanal = 10,
				name = "VHF",
			},
			[2] = {								--radio 2 name = _("ARC-164"),
				UHF = {
					min = 225,					--minimum radio frequency in mHz
					max = 399.975,				--maxium  radio frequency in mHz
				},
				nbCanal = 10,
				name = "UHF",
			},
			[3] = {								--radio 3 name = _("FM 1: ARC-201D"),
				LVHF = {
					min = 30.0,					--minimum radio frequency in mHz
					max = 87.995,				--maxium  radio frequency in mHz
				},
				nbCanal = 10,
				name = "FM 1",
			},
			[4] = {								--radio 4 name = _("FM 2: ARC-201D"),
				LVHF = {
					min = 30.0,					--minimum radio frequency in mHz
					max = 87.995,				--maxium  radio frequency in mHz
				},
				nbCanal = 10,
				name = "FM 2",
			},
			[5] = {						--radio 3 Yadro1 HF
				HF = {
					min = 2,				--minimum radio frequency in mHz
					max = 17.999,			--maxium  radio frequency in mHz
				},
				nbCanal = 0,
				name = "HF  ",
			},
		},
	},
	["UH-1H"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1
				UHF = {
					min = 225,				--minimum radio frequency in mHz
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
			},
		},
		helicopter = true,
	},
	["L-39C"] = {
		radio = {
			[1] = {
				VHF = {
					min = 118,
					max = 224.995,
				},
				UHF = {
					min = 225,
					max = 399.95,
				},
				nbCanal = 20,
				startCanal = 0,
				name = "R-832M"
			},
		},	
	},
	["Su-25"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {
				VHF = {
					min = 100,
					max = 224.995,
				},
				UHF = {
					min = 225,
					max = 399.98,
				},
				nbCanal = 0,
				FC3 = true,
				FC3Frequency = 124,
			},
		},	
	},
	["Su-25T"] = {
		radio = {						--range of radio frequencies of player aircraft
			[1] = {
				VHF = {
					min = 100,
					max = 224.995,
				},
				UHF = {
					min = 225,
					max = 399.98,
				},
				nbCanal = 0,
				FC3 = true,
				FC3Frequency = 124,
			},
		},	
	},
	["Mi-8MT"] = {
		helicopter = true,
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1
				UHF = {
					min = 220,				--minimum radio frequency in mHz
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
			},
			[2] = {						--radio 2
				FM = {
					min = 20,				--minimum radio frequency in mHz
					max = 59.97,				--maxium  radio frequency in mHz
				},
				nbCanal = 10,
			},
		},
	},
	["Mi-24P"] = {
		helicopter = true,
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1
				UHF = {
					min = 100,				--minimum radio frequency in mHz
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 20,
			},
			[2] = {						--radio 2
				FM = {
					min = 20,				--minimum radio frequency in mHz
					max = 59.97,				--maxium  radio frequency in mHz
				},
				nbCanal = 10,
			},
		},
	},
	["Ka-50"] = {
		helicopter = true,
		radio = {						--range of radio frequencies of player aircraft
			[1] = {						--radio 1
				FM = {
					min = 20,				--minimum radio frequency in mHz
					max = 59,				--maxium  radio frequency in mHz
				},
				nbCanal = 10,
			},
			[2] = {						--radio 2 simule la frequence FC3 de DCS
				VHF = {
					min = 100,				--minimum radio frequency in mHz
					max = 224,				--maxium  radio frequency in mHz
				},
				UHF = {
					min = 225,				--minimum radio frequency in mHz
					max = 399,				--maxium  radio frequency in mHz
				},
				nbCanal = 0,
			},
			-- [2] = {						--radio 2
				-- min = 0.215,				--minimum radio frequency in mHz
				-- max = 1.065,				--maxium  radio frequency in mHz
				-- nbCanal = 16,
			-- },
		},
	},
	["P-51D-30-NA"] = {
		radio = {							
			[1] = {						--radio  SCR 522 A VHF RADIO
				VHF = {
					min = 100,				--minimum radio frequency in mHz
					max = 156,				--maxium  radio frequency in mHz
				},
				nbCanal = 4,
			},
		},
	},
	["P-47D-30"] = {
		radio = {									
			[1] = {						--radio SCR 522 A VHF RADIO
				VHF = {
					min = 100,				--minimum radio frequency in mHz
					max = 156,				--maxium  radio frequency in mHz
				},
				nbCanal = 4,
			},
		},
	},
	["SpitfireLFMkIX"] = {
		radio = {									
			[1] = {						--radio A R I 1063 type HF
				VHF = {
					min = 38,				--minimum radio frequency in mHz
					max = 156,				--maxium  radio frequency in mHz
				},
				nbCanal = 4,
			},
		},
	},
	["Bf-109K-4"] = {
		radio = {									
			[1] = {						--radio 4 is equipped with a FUG 16ZY radio transmitter and receiver.
				FM = {
					min = 38.4,				--minimum radio frequency in mHz
					max = 42.4,				--maxium  radio frequency in mHz
				},
				nbCanal = 4,
			},
		},
	},
}	]]
	
