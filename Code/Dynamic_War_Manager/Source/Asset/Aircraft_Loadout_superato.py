from functools import lru_cache
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Union, Tuple
from Code.Dynamic_War_Manager.Source.Context import Context 
from Code.Dynamic_War_Manager.Source.Asset.Aircraft import Aircraft
from Code.Dynamic_War_Manager.Source.Utility import Utility
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.Utility.Utility import true_air_speed, indicated_air_speed, true_air_speed_at_new_altitude
from sympy import Point3D
from dataclasses import dataclass

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Aircraft_Data')

AIRCRAFT_ROLE = Context.AIR_MILITARY_CRAFT_ASSET.keys()
AIRCRAFT_TASK = Context.AIR_TASK

@dataclass
class Aircraft_Loadout:
    
	_registry = []

	def __init__(self, model_aircraft: str, id_loadout: str, task: str, role: str, targets: Dict, fuel: int, weapons: Dict, weapon_control_device: Optional[Dict] = None, jamming_device: Optional[Dict] = None, chaff_flare: Optional[Dict] = None, fuel_tank: Optional[Dict] = None ):
		self.model_aircraft = model_aircraft
		self.task = task # "Anti-ship Strike"
		self.role = role # [attacker, bomber,sead ....]         
		self.id_loadout = id_loadout # "Antiship Strike - Kormoran*2, AIM-9M*2, 2*Fuel role: ATTACKER @ LOW ALT" 
		self.targets = targets # ['aircraft', 'fighter', 'bomber', 'hard structure', 'armor', 'motorized']
		self.fuel = fuel
		self.weapons = weapons # {'model': model, 'type': type, 'quantity': qty}		
		self.weapon_control_device = weapon_control_device #(bool, {}) in ordinance_data -> model: {power, year, level, control_type}
		self.jamming_device = jamming_device # (bool, {'model': qty})	in ordinance_data -> model: {power, year, level}	
		self.chaff_flare = chaff_flare
		self.fuel_tank = fuel_tank
		self.fuel = fuel
		
		Aircraft_Loadout._registry.append(self)

	def firepower(self): Dict# {'a2a': (bool, val), 'a2g': {'target_category': val (totnn kg tnt) }, 'rocket':.... }}
		# by weapons and devices
	pass

	def attack_altitudes(self): Dict # min, max
		# by weapons
	pass

	def attack_speed(self): Dict # min, max
		# by weapons
	pass 

	def stand_off(self): Dict # min, max
		# by weapons
	pass

	def t_station(self): Dict # min, max
		# by weapons
	pass

	def night_attack(self): bool
		# by weapons
	pass

	def adverse_weather_attack(self): bool
		# by weapons and devices	
	pass

	def range(self): int
		#by fuel and fuel_tank and complessive weight
	pass
	


db_loadouts = {
	# Nato
	"Tornado IDS": {# 1971  SI  
		
		"Anti-ship Strike": {

			"Antiship Strike - Kormoran*2, AIM-9M*2, 2*Fuel role: ATTACKER @ LOW ALT": {
				'role': 'attacker',			
				'targets': {"ship"},
				'weapons': { # task dedicated weapons
					"Kormoran": ("ASM", 2), 								
				},
				"fuel": "4663",
				"flare": 45,
				"chaff": 90,
				"gun": 100,			
			},
		},
		"Strike": {

			"Pinpoint Strike - GBU-16*2, AIM-9M*2, 2*Fuel - FT role: ATTACKER @ NORMAL ALT": {
				'role': "attacker",			
				'targets': {"Bridge", "Structure"},
				'weapons': { # task dedicated weapons
					'GBU-16': ("Guided bombs", 2)
				},			
				"fuel": 4663,
				"flare": 45,
				"chaff": 90,
				"gun": 100,
			},	

			"Strike - Mk-82*4, AIM-9M*2, 2*Fuel - FT role: ATTACKER @ NORMAL ALT": { #
				'role': "attacker",			
				'targets': {"soft", "Parked Aircraft", "SAM", "armor"},
				'weapons': { # task dedicated weapons
					"Mk-82": ("Bombs", 4),																		
				},
				"fuel": 4663,
				"flare": 45,
				"chaff": 90,
				"gun": 100,
			},
		},	
		'SEAD': {		
			"SEAD Long Range - AGM-88*2, AIM-9M*2, ECM, 2*Fuel role: SEAD ESCORT FOR BOMBER @ NORMAL ALT": {
				'role': "escort_sead_bomber",						
				'targets': {"SAM"},
				'weapons': { # task dedicated weapons
					"AGM-88": ("ASM", 2),										
				},
			
				"fuel": 4663,
				"flare": 45,
				"chaff": 90,
				"gun": 100,
			},
			
			"SEAD - AGM-88*4, AIM-9M*2, ECM role: SEAD ESCORT FOR ATTACKER @ NORMAL ALT": {
				'role': "escort_sead_attacker",			
				'targets': {"SAM"},
				'weapons': { # task dedicated weapons
					"AGM-88" : ("ASM", 4),										
				},
				"fuel": 4663,
				"flare": 45,
				"chaff": 90,
				"gun": 100,
			},		
		},
	},

	"A10A": {  # 1977
		"Strike": {
			"CAS ASM AGM-65D *4, AIM-9*2, ECM": {
				'role': 'attacker',
				'targets': {"armor", "SAM"},
				'weapons': {
					"AGM-65D": ("ASM", 4),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": 5029,
				"flare": 120,
				"chaff": 240,
				"gun": 100,
			},
			"CAS Cluster Bombs Mk20*6, AIM-9*2, ECM": {
				'role': 'attacker',
				'targets': {"soft", "Parked Aircraft", "SAM"},
				'weapons': {
					"Mk-20": ("Cluster bombs", 6),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": 5029,
				"flare": 120,
				"chaff": 240,
				"gun": 100,
			},
			"CAS Cluster Bombs Mk20*8, AIM-9*2": {
				'role': 'attacker',
				'targets': {"soft", "Parked Aircraft", "SAM"},
				'weapons': {
					"Mk-20": ("Cluster bombs", 8),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": 5029,
				"flare": 120,
				"chaff": 240,
				"gun": 100,
			},
			"CAS Rockets LAU-68-MK5 *6": {
				'role': 'attacker',
				'targets': {"armor", "SAM"},
				'weapons': {
					"Hydra-70MK5": ("Rockets", 6),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": 5029,
				"flare": 120,
				"chaff": 240,
				"gun": 100,
			}
		}
	},

	"F15C": {  # 1976
		"Intercept": {
			"Intercept AIM-7M*2, AIM-7MH*2, AIM-9M*4, Fuel*1": {
				'role': None,
				'targets': set(),
				'weapons': {
					"AIM-7M": ("Missiles", 2),
					"AIM-7MH": ("Missiles", 2),
					"AIM-9M": ("Missiles", 4)
				},
				"fuel": "6103",
				"flare": 60,
				"chaff": 120,
				"gun": 100,
			}
		},
		"CAP": {
			"CAP-Escort AIM-7MH*4, AIM-9M*2, Fuel*3": {
				'role': None,
				'targets': {"Air Forces"},
				'weapons': {
					"AIM-7MH": ("Missiles", 4),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": "6103",
				"flare": 60,
				"chaff": 120,
				"gun": 100,
			}
		},
		"Escort": {
			"CAP-Escort AIM-7MH*4, AIM-9M*2, Fuel*3": {
				'role': "escort_bomber",
				'targets': {"Air Forces"},
				'weapons': {
					"AIM-7MH": ("Missiles", 4),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": "6103",
				"flare": 60,
				"chaff": 120,
				"gun": 100,
			}
		},
		"Fighter Sweep": {
			"CAP-Escort AIM-7MH*4, AIM-9M, Fuel*3": {
				'role': None,
				'targets': {"Air Forces"},
				'weapons': {
					"AIM-7MH": ("Missiles", 4),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": "6103",
				"flare": 60,
				"chaff": 120,
				"gun": 100,
			}
		}
	},

	"F16A": {  # 1978
		"Intercept": {
			"Intercept AIM-9P5*4, AIM-9M*2, ECM": {
				'role': None,
				'targets': set(),
				'weapons': {
					"AIM-9P5": ("Missiles", 4),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": "3104",
				"flare": 30,
				"chaff": 60,
				"gun": 100,
			}
		},
		"CAP": {
			"CAP-Escort AIM-9P5*4, AIM-9M*2, ECM, Fuel*2": {
				'role': None,
				'targets': {"Air Forces"},
				'weapons': {
					"AIM-9P5": ("Missiles", 4),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": "3104",
				"flare": 30,
				"chaff": 60,
				"gun": 100,
			}
		},
		"Escort": {
			"CAP-Escort AIM-9P5*4, AIM-9M*2, ECM, Fuel*2": {
				'role': "escort_attacker",
				'targets': set(),
				'weapons': {
					"AIM-9P5": ("Missiles", 4),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": "3104",
				"flare": 30,
				"chaff": 60,
				"gun": 100,
			}
		},
		"Fighter Sweep": {
			"CAP-Escort AIM-9P5*4, AIM-9M*2, ECM, Fuel*2": {
				'role': None,
				'targets': set(),
				'weapons': {
					"AIM-9P5": ("Missiles", 4),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": "3104",
				"flare": 30,
				"chaff": 60,
				"gun": 100,
			}
		},
		"Strike": {
			"Strike AIM-9P*2, Mk-82*6, ECM, Fuel*2": {
				'role': "attacker",
				'targets': {"Structure", "Bridge"},
				'weapons': {
					"AIM-9P": ("Missiles", 2),
					"Mk-82": ("Bombs", 6)
				},
				"fuel": "3104",
				"flare": 30,
				"chaff": 60,
				"gun": 100,
			},
			"Strike Bombs AIM-9M*2, Mk-84*2, ECM, Fuel*2": {
				'role': "attacker",
				'targets': {"Structure", "Bridge"},
				'weapons': {
					"AIM-9M": ("Missiles", 2),
					"Mk-84": ("Bombs", 2)
				},
				"fuel": "3104",
				"flare": 30,
				"chaff": 60,
				"gun": 100,
			},
			"Pinpoint Strike, bombs, AIM-9P*2, GBU-10*2, ECM, Lantirn, Fuel*2": {
				'role': "attacker",
				'targets': {"Structure", "Bridge"},
				'weapons': {
					"AIM-9P": ("Missiles", 2),
					"GBU-10": ("Guided bombs", 2)
				},
				"fuel": "3104",
				"flare": 30,
				"chaff": 60,
				"gun": 100,
			}
		}
	},

	"F117A": {  # 1983
		"Strike": {
			"Pinpoint Strike GBU-10*2": {
				'role': "bomber",
				'targets': {"Structure", "Bridge"},
				'weapons': {
					"GBU-10": ("Guided bombs", 2)
				},
				"fuel": "8255",
				"flare": 0,
				"chaff": 0,
				"gun": 100,
			},
			"Pinpoint Hard Strike GBU-27*2": {
				'role': "bomber",
				'targets': {"Structure", "Bridge"},
				'weapons': {
					"GBU-27": ("Guided bombs", 2)
				},
				"fuel": 8007,
				"flare": 0,
				"chaff": 0,
				"gun": 100,
			}
		}
	},

	"E3A": {  # 1977
		"AWACS": {
			"Default": {
				'role': "AWACS",
				'targets': {"Sentry"},
				'weapons': {},
				"fuel": "65000",
				"flare": 60,
				"chaff": 120,
				"gun": 100,
			}
		}
	},

	"E2C": {  # 1973
		"AWACS": {
			"Default": {
				'role': "AWACS",
				'targets': set(),
				'weapons': {},
				"fuel": "65000",
				"flare": 60,
				"chaff": 120,
				"gun": 100,
			}
		}
	},

	"F14A": {  # 1974
		"Intercept": {
			"TF-Old-AIM-54A-MK60*4, AIM-7M*2, AIM-9M*2, XT*2": {
				'role': None,
				'targets': set(),
				'weapons': {
					"AIM-54A-MK60": ("Missiles", 4),
					"AIM-7M": ("Missiles", 2),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": "7348",
				"flare": 60,
				"chaff": 140,
				"gun": 100,
			},
			"Intercept AIM-54C-Mk47*4, AIM-7MH*2, AIM-9M*1, Fuel *2": {
				'role': None,
				'targets': set(),
				'weapons': {
					"AIM-54C-MK47": ("Missiles", 4),
					"AIM-7MH": ("Missiles", 2),
					"AIM-9M": ("Missiles", 1)
				},
				"fuel": 7348,
				"flare": 60,
				"chaff": 140,
				"gun": 100,
			},
			"IRAN TF-Old-AIM-54A-MK60*4, AIM-7M*2, AIM-9M*2, XT*2": {
				'role': None,
				'targets': set(),
				'weapons': {
					"AIM-54A-MK60": ("Missiles", 4),
					"AIM-7M": ("Missiles", 2),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": "7348",
				"flare": 60,
				"chaff": 140,
				"gun": 100,
			}
		},
		"CAP": {
			"TF-Old-AIM-54A-MK60*4, AIM-7M*2, AIM-9M*2, XT*2": {
				'role': None,
				'targets': {"Air Forces"},
				'weapons': {
					"AIM-54A-MK60": ("Missiles", 4),
					"AIM-7M": ("Missiles", 2),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": "7348",
				"flare": 60,
				"chaff": 140,
				"gun": 100,
			},
			"CAP-Escort AIM-54C-Mk47*4, AIM-7P*2, AIM-9M*1, ACMI Pod, Fuel *2": {
				'role': None,
				'targets': {"Air Forces"},
				'weapons': {
					"AIM-54C-MK47": ("Missiles", 4),
					"AIM-7P": ("Missiles", 2),
					"AIM-9M": ("Missiles", 1)
				},
				"fuel": 7348,
				"flare": 60,
				"chaff": 140,
				"gun": 100,
			},
			"IRAN-TF-Old-AIM-54A-MK60*4, AIM-7M*2, AIM-9M*2, XT*2": {
				'role': None,
				'targets': {"Air Forces"},
				'weapons': {
					"AIM-54A-MK60": ("Missiles", 4),
					"AIM-7M": ("Missiles", 2),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": "7348",
				"flare": 60,
				"chaff": 140,
				"gun": 100,
			}
		},
		"Escort": {
			"TF-Old-AIM-54A-MK60*4, AIM-7M*2, AIM-9M*2, XT*2 role: ESCORT BOMBER @ NORMAL ALT": {
				'role': "escort_bomber",
				'targets': set(),
				'weapons': {
					"AIM-54A-MK60": ("Missiles", 4),
					"AIM-7M": ("Missiles", 2),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": "7348",
				"flare": 60,
				"chaff": 140,
				"gun": 100,
			},
			"TF-Old-AIM-54A-MK60*4, AIM-7M*2, AIM-9M*2, XT*2 role: ESCORT ATTACKER @ NORMAL ALT": {
				'role': "escort_attacker",
				'targets': set(),
				'weapons': {
					"AIM-54A-MK60": ("Missiles", 4),
					"AIM-7M": ("Missiles", 2),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": "7348",
				"flare": 60,
				"chaff": 140,
				"gun": 100,
			},
			"CAP-Escort AIM-54C-Mk47*4, AIM-7P*2, AIM-9M*1, ACMI Pod, Fuel *2 ESCORT BOMBER @ NORMAL ALT": {
				'role': "escort_bomber",
				'targets': set(),
				'weapons': {
					"AIM-54C-MK47": ("Missiles", 4),
					"AIM-7P": ("Missiles", 2),
					"AIM-9M": ("Missiles", 1)
				},
				"fuel": 7348,
				"flare": 60,
				"chaff": 140,
				"gun": 100,
			},
			"IRAN-TF-Old-AIM-54A-MK60*4, AIM-7M*2, AIM-9M*2, XT*2 role: ESCORT BOMBER @ NORMAL ALT": {
				'role': "escort_bomber",
				'targets': set(),
				'weapons': {
					"AIM-54A-MK60": ("Missiles", 4),
					"AIM-7M": ("Missiles", 2),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": "7348",
				"flare": 60,
				"chaff": 140,
				"gun": 100,
			}
		},
		"Fighter Sweep": {
			"TF-Old-AIM-54A-MK60*4, AIM-7M*2, AIM-9M*2, XT*2": {
				'role': None,
				'targets': set(),
				'weapons': {
					"AIM-54A-MK60": ("Missiles", 4),
					"AIM-7M": ("Missiles", 2),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": "7348",
				"flare": 60,
				"chaff": 140,
				"gun": 100,
			},
			"IRAN-TF-Old-AIM-54A-MK60*4, AIM-7M*2, AIM-9M*2, XT*2": {
				'role': None,
				'targets': set(),
				'weapons': {
					"AIM-54A-MK60": ("Missiles", 4),
					"AIM-7M": ("Missiles", 2),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": "7348",
				"flare": 60,
				"chaff": 140,
				"gun": 100,
			},
			"CAP-Escort AIM-54C-Mk47*4, AIM-7P*2, AIM-9M*1, ACMI Pod, Fuel *2": {
				'role': None,
				'targets': set(),
				'weapons': {
					"AIM-54C-MK47": ("Missiles", 4),
					"AIM-7P": ("Missiles", 2),
					"AIM-9M": ("Missiles", 1)
				},
				"fuel": 7348,
				"flare": 60,
				"chaff": 140,
				"gun": 100,
			}
		},
		"Strike": {
			"CAS Guided boms, GBU-12, AIM-7M, AIM-9M*2, Lantirn, Fuel *2": {
				'role': "attacker",
				'targets': {"Structure", "Bridge"},
				'weapons': {
					"GBU-12": ("Guided bombs", 1),
					"AIM-7M": ("Missiles", 1),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": 7348,
				"flare": 60,
				"chaff": 140,
				"gun": 100,
			},
			"CAS Guided boms, GBU-24, AIM-7M, AIM-9M*2, Lantirn, Fuel *2": {
				'role': "attacker",
				'targets': {"Structure", "Bridge"},
				'weapons': {
					"GBU-24": ("Guided bombs", 1),
					"AIM-7M": ("Missiles", 1),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": 7348,
				"flare": 60,
				"chaff": 140,
				"gun": 100,
			},
			"Strike TF GBU-10*2, AIM-54C*2, AIM-9M*2, AIM-7M*1,Lantirn, FT*2": {
				'role': "attacker",
				'targets': {"Structure", "Bridge"},
				'weapons': {
					"GBU-10": ("Guided bombs", 2),
					"AIM-54C": ("Missiles", 2),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": "7348",
				"flare": 60,
				"chaff": 140,
				"gun": 100,
			},
			"Strike AIM-9*2 AIM-7*2 FUEL*2 Mk 82*10 role: ATTACKER @ LOW ALT": {
				'role': "attacker",
				'targets': {"soft", "Parked Aircraft", "SAM", "armor"},
				'weapons': {
					"Mk-82": ("Bombs", 10),
					"AIM-7M": ("Missiles", 2),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": "7348",
				"flare": 60,
				"chaff": 140,
				"gun": 100,
			},
			"Strike AIM-9*2 AIM-7*2 AIM-54A*2 FUEL*2 Mk 84*2 role: ATTACKER @ NORMAL ALT": {
				'role': "attacker",
				'targets': {"Structure", "Bridge"},
				'weapons': {
					"Mk-84": ("Bombs", 2),
					"AIM-7M": ("Missiles", 2),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": "7348",
				"flare": 60,
				"chaff": 140,
				"gun": 100,
			},
			"Strike AIM-9*2 AIM-7*2 Fuel*2 Mk 20 *4 role: ATTACKER @ NORMAL ALT": {
				'role': "attacker",
				'targets': {"soft", "Parked Aircraft", "SAM", "armor"},
				'weapons': {
					"Mk-20": ("Bombs", 2),
					"AIM-7M": ("Missiles", 2),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": "7348",
				"flare": 60,
				"chaff": 140,
				"gun": 100,
			},
			"CAS Cluster Bombs, Mk-20*2, AIM-54C, AIM-7M, AIM-9M*2, Lantirn, Fuel *2 role: ATTACKER @ NORMAL ALT": {
				'role': "attacker",
				'targets': {"soft", "Parked Aircraft", "SAM", "armor"},
				'weapons': {
					"Mk-20": ("Bombs", 2),
					"AIM-7M": ("Missiles", 1),
					"AIM-54C-MK47": ("Missiles", 1),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": 7348,
				"flare": 60,
				"chaff": 140,
				"gun": 100,
			},
			"CAS Rockets short range, Zuni*28 role: ATTACKER @ LOW ALT": {
				'role': "attacker",
				'targets': {"soft", "Parked Aircraft", "SAM", "armor"},
				'weapons': {
					"Zuni-Mk71": ("Rockets", 28)
				},
				"fuel": 7348,
				"flare": 60,
				"chaff": 140,
				"gun": 100,
			}
		}
	},

	"KC135": {  # 1957
		"Refueling": {
			"Default": {
				'role': "refueler",
				'targets': {"KC135"},
				'weapons': {},
				"fuel": 90700,
				"flare": 60,
				"chaff": 120,
				"gun": 100,
			}
		}
	},

	"KC135MPRS": {  # 1957
		"Refueling": {
			"Default": {
				'role': "refueler",
				'targets': {"KC135"},
				'weapons': {},
				"fuel": 90700,
				"flare": 60,
				"chaff": 120,
				"gun": 100,
			}
		}
	},

	"AJS37": {  # 1971 SI
		"Intercept": {
			"Intercept RB-05A*2 RB-74*2 FUEL": {
				'targets': {},
				'weapons': {
					"RB-05A": ("ASM", 2),
					"RB-74": ("AAM", 2),
				},
				"fuel": 4476,
				"flare": 72,
				"chaff": 210,
				"gun": 100,
			},
		},
		"Anti-ship Strike": {
			"Antiship - RB 15F*2(antiship) - RB-74J*2(aim9) - RB-24J*2(aim9) - FT": {
				'role': 'attacker',
				'targets': {"ship"},
				'weapons': {
					"RB-15F": ("ASM", 2),
					"RB-74": ("AAM", 2),
					"RB-24J": ("AAM", 2),
				},
				"fuel": 4476,
				"flare": 36,
				"chaff": 105,
				"gun": 100,
			},
			"Antiship RB-04R*2 RB-74*2, FUEL role: ATTACKER @ LOW ALT": {
				'role': 'attacker',
				'targets': {"ship"},
				'weapons': {
					"RB-04E": ("ASM", 2),
					"RB-74": ("AAM", 2),
				},
				"fuel": 4476,
				"flare": 72,
				"chaff": 210,
				"gun": 100,
			},
			"Antiship RB-75T*4 FUEL role: ATTACKER @ LOW ALT": {
				'role': 'attacker',
				'targets': {"ship"},
				'weapons': {
					"RB-75T": ("ASM", 4),
				},
				"fuel": 4476,
				"flare": 72,
				"chaff": 210,
				"gun": 100,
			},
		},
		"Strike": {
			"CAS - Bomb M/71*8 - ECM*2 - RB-24J*2 - FT role: ATTACKER @ NORMAL ALT": {
				'role': 'attacker',
				'targets': {"soft", "Parked Aircraft", "SAM", "armor"},
				'weapons': {
					"M/71": ("Bombs", 8),
					"RB-24J": ("AAM", 2),
				},
				"fuel": 4476,
				"flare": 36,
				"chaff": 105,
				"gun": 100,
			},
			"CAS - Bomb M/71 chute*8 - ECM*2 - RB-24J*2 - FT role: ATTACKER @ NORMAL ALT": {
				'role': 'attacker',
				'targets': {"soft", "Parked Aircraft", "SAM", "armor"},
				'weapons': {
					"M/71": ("Bombs", 8),
					"RB-24J": ("AAM", 2),
				},
				"fuel": 4476,
				"flare": 36,
				"chaff": 105,
				"gun": 100,
			},
			"CAS Hard - RB-75T*2 - ECM*2 - RB-24J*2 - FT role: ATTACKER @ NORMAL ALT": {
				'role': 'attacker',
				'targets': {"Structure", "SAM", "armor"},
				'weapons': {
					"RB-75T": ("ASM", 2),
					"RB-24J": ("AAM", 2),
				},
				"fuel": 4476,
				"flare": 36,
				"chaff": 105,
				"gun": 100,
			},
			"ASM hard RB-75T*4 TV Guided Rb-24 Fuel role: ATTACKER @ NORMAL ALT": {
				'role': 'attacker',
				'targets': {"Structure", "SAM", "armor"},
				'weapons': {
					"RB-75T": ("ASM", 4),
					"RB-24J": ("AAM", 2),
				},
				"fuel": 4476,
				"flare": 72,
				"chaff": 210,
				"gun": 100,
			},
			"ASM ECM U25pod KBpod RB-75T*2 FUEL role: ATTACKER @ NORMAL ALT": {
				'role': 'attacker',
				'targets': {"SAM"},
				'weapons': {
					"RB-75T": ("ASM", 2),
				},
				"fuel": 4476,
				"flare": 72,
				"chaff": 210,
				"gun": 100,
			},
		},
		"SEAD": {
			"ASM SEAD ECM U25pod KBpod RB-75T*2 FUEL role: SEAD ESCORT FOR BOMBER @ NORMAL ALT": {
				'role': 'escort_sead_bomber',
				'targets': {"SAM"},
				'weapons': {
					"RB-75T": ("ASM", 2),
				},
				"fuel": 4476,
				"flare": 72,
				"chaff": 210,
				"gun": 100,
			},
			"ASM SEAD ECM U25pod KBpod RB-75T*2 FUEL role: SEAD ESCORT FOR ATTACKER @ NORMAL ALT": {
				'role': 'escort_sead_attacker',
				'targets': {"SAM"},
				'weapons': {
					"RB-75T": ("ASM", 2),
				},
				"fuel": 4476,
				"flare": 72,
				"chaff": 210,
				"gun": 100,
			},
		},
		"Escort Jammer": {
			"Antiship ECM Escort KB pod RB-04R*1RB-74*2, FUEL role: ATTACKER @ LOW ALT": {
				'role': 'escort_jammer_bomber',
				'targets': {"ship"},
				'weapons': {
					"RB-04E": ("ASM", 1),
					"RB-74": ("AAM", 2),
				},
				"fuel": 4476,
				"flare": 72,
				"chaff": 210,
				"gun": 100,
			},
			"ECM Escort KB pod RB-04R*1RB-74*2, FUEL role: ATTACKER @ NORMAL ALT": {
				'role': 'escort_jammer_attacker',
				'targets': {"ship"},
				'weapons': {
					"RB-04E": ("ASM", 1),
					"RB-74": ("AAM", 2),
				},
				"fuel": 4476,
				"flare": 72,
				"chaff": 210,
				"gun": 100,
			},
		},
	},

	"B52H": {  # 1955 SI
		
		"Strike": {
			"Strike Mk-84*18 role: BOMBER @ HIGH ALT": {
				'role': 'bomber',
				'targets': {"Structure", "Bridge"},
				'weapons': {
					"Mk-84": ("Bombs", 18)
				},
				"fuel": "141135",
				"flare": 192,
				"chaff": 1125,
				"gun": 100,
			},
		},
	},

	"S3B_Tanker": {  # 1974 SI
		
		"Refueling": {
			"Low Track": {
				'role': 'refueler',
				'targets': {"low"},
				'weapons': {},
				"fuel": 7813,
				"flare": 30,
				"chaff": 30,
				"gun": 100,
			},
			"Medium Track": {
				'role': 'refueler',
				'targets': {"medium"},
				'weapons': {},
				"fuel": 7813,
				"flare": 30,
				"chaff": 30,
				"gun": 100,
			},
		},
	},

	"S3B": {  # 1974 SI
		
		"Anti-ship Strike": {
			"ANTISHIP AGM-84A*2 role: BOMBER @ NORMAL ALT": {
				'role': 'bomber',
				'targets': {"ship"},
				'weapons': {
					"AGM-84A": ("ASM", 2)
				},
				"fuel": 7000,
				"flare": 30,
				"chaff": 30,
				"gun": 100,
			},
		},
		
		"Strike": {
			"GA MK-84*2, MK-82*4 role: BOMBER @ NORMAL ALT": {
				'role': 'bomber',
				'targets': {"Structure", "Bridge"},
				'weapons': {
					"Mk-84": ("Bombs", 2),
					"Mk-82": ("Bombs", 4)
				},
				"fuel": 7000,
				"flare": 30,
				"chaff": 30,
				"gun": 100,
			},
			"GA MK-82*10 role: BOMBER @ NORMAL ALT": {
				'role': 'bomber',
				'targets': {"soft", "Parked Aircraft", "SAM", "armor"},
				'weapons': {
					"Mk-82": ("Bombs", 10)
				},
				"fuel": 7000,
				"flare": 30,
				"chaff": 30,
				"gun": 100,
			},
			"CAS Cluster MK-20*4 role: BOMBER @ NORMAL ALT": {
				'role': 'bomber',
				'targets': {"soft", "Parked Aircraft", "SAM", "armor"},
				'weapons': {
					"Mk-20": ("Bombs", 4)
				},
				"fuel": 7000,
				"flare": 30,
				"chaff": 30,
				"gun": 100,
			},
		},
		
		"SEAD": {
			"SEAD AGM-65D-K*2 role: SEAD ESCORT FOR BOMBER @ NORMAL ALT": {
				'role': 'escort_sead_bomber',
				'targets': {"SAM"},
				'weapons': {
					"AGM-65D": ("ASM", 2),
					"AGM-65K": ("ASM", 2)
				},
				"fuel": 7000,
				"flare": 30,
				"chaff": 30,
				"gun": 100,
			},
		},
	},

	"F5E3": {  # 1972 SI
		
		"Strike": {
			"GTA CAS1/STRIKE Mk-82SE*4,AIM-9P*2,Fuel 2750 role: ATTACKER @ LOW ALT": {
				'role': 'attacker',
				'targets': {"soft"},
				'weapons': {
					"Mk-82": ("Bombs", 4),
					"AIM-9P": ("Missiles", 2)
				},
				"fuel": 2046,
				"flare": 15,
				"chaff": 30,
				"gun": 100,
			},
			"GTA CAS2/STRIKE CBU-52B*4,AIM-9P*2,Fuel 2750 role: ATTACKER @ LOW ALT": {
				'role': 'attacker',
				'targets': {"soft", "Parked Aircraft", "SAM"},
				'weapons': {
					"CBU-52B": ("Bombs", 4),
					"AIM-9P": ("Missiles", 2)
				},
				"fuel": 2046,
				"flare": 15,
				"chaff": 30,
				"gun": 100,
			},
		},
		
		"Intercept": {
			"Day, AIM-9P*2, Fuel": {
				'targets': {},
				'weapons': {
					"AIM-9P": ("Missiles", 2)
				},
				"fuel": 2046,
				"flare": 15,
				"chaff": 30,
				"gun": 100,
			},
		},
		
		"CAP": {
			"Day, AIM-9P*2, Fuel_275*1": {
				'targets': {"Air Forces"},
				'weapons': {
					"AIM-9P": ("Missiles", 2)
				},
				"fuel": 2046,
				"flare": 15,
				"chaff": 30,
				"gun": 100,
			},
		},
		
		"Escort": {
			"AIM-9P*2, Fuel_275*1 role: ESCORT ATTACKER @ NORMAL ALTITUDE": {
				'role': 'escort_attacker',
				'targets': {},
				'weapons': {
					"AIM-9P": ("Missiles", 2)
				},
				"fuel": 2046,
				"flare": 15,
				"chaff": 30,
				"gun": 100,
			},
		},
	},

	"M2000C": {  # 1983 SI
		
		"Intercept": {
			"Day, MagicII*2, S-530D*2, FT*1": {
				'targets': {},
				'weapons': {
					"R-550": ("Missiles", 2),
					"R-530EM": ("Missiles", 2)
				},
				"fuel": 3165,
				"flare": 48,
				"chaff": 112,
				"gun": 100,
			},
		},
		
		"CAP": {
			"Day, MagicII*2, S-530D*2, FT*1": {
				'targets': {"Air Forces"},
				'weapons': {
					"R-550": ("Missiles", 2),
					"R-530EM": ("Missiles", 2)
				},
				"fuel": 3165,
				"flare": 48,
				"chaff": 112,
				"gun": 100,
			},
		},
		
		"Strike": {
			"GBU-16*1, MagicII*2, FT*2": {
				'role': 'attacker',
				'targets': {"Bridge", "Structure"},
				'weapons': {
					"GBU-16": ("Guided bombs", 1),
					"R-550": ("Missiles", 2)
				},
				"fuel": 3165,
				"flare": 48,
				"chaff": 112,
				"gun": 100,
			},
		},
	},

	"MirageF1C": {  # 1974 SI
		
		"Strike": {
			"MirageF1C_GA_8xSAMP400kg_2xR550 role: ATTACKER @ LOW ALT": {
				'role': 'attacker',
				'targets': {"Structure", "Bridge"},
				'weapons': {
					"SAMP-400LD": ("Bombs", 2),
					"R-550": ("Missiles", 2)
				},
				"fuel": 3356,
				"flare": 0,
				"chaff": 0,
				"gun": 100,
			},
		},
		
		"Intercept": {
			"MirageF1C_GI_2xR550_1xR530IR": {
				'targets': {},
				'weapons': {
					"R-550": ("Missiles", 2),
					"R-530IR": ("Missiles", 1)
				},
				"fuel": 3356,
				"flare": 0,
				"chaff": 0,
				"gun": 100,
			},
		},
	},

	"F4E": {  # 1960 SI
		
		"Intercept": {
			"GTA AIR/AIR AIM-9*4,AIM-7*4": {
				'targets': {},
				'weapons': {
					"AIM-9B": ("Missiles", 4),
					"AIM-7E": ("Missiles", 4)
				},
				"fuel": "4864",
				"flare": 30,
				"chaff": 60,
				"gun": 100,
			},
		},
		
		"Strike": {
			"GTA CAS1 AGM-65K*4,AIM-7*2,Fuel*2,ECM role: ATTACKER @ NORMAL ALT": {
				'role': 'attacker',
				'targets': {"armor", "SAM"},
				'weapons': {
					"AGM-65K": ("ASM", 4),
					"AIM-7E": ("Missiles", 2)
				},
				"fuel": "4864",
				"flare": 30,
				"chaff": 60,
				"gun": 100,
			},
		},
		
		"SEAD": {
			"AGM-45*2, AIM-7M*3, ECM*1, Fuel*2 role: SEAD ESCORT FOR BOMBER @ NORMAL ALT": {
				'role': 'escort_sead_bomber',
				'targets': {"SAM"},
				'weapons': {
					"AGM-45": ("ASM", 2),
					"AIM-7M": ("Missiles", 3)
				},
				"fuel": "4864",
				"flare": 30,
				"chaff": 60,
				"gun": 100,
			},
		},
	},

	"C130": {  # 1957 SI
		
		"Transport": {
			"Default": {
				'role': 'transporter',
				'targets': {},
				'weapons': {},
				"fuel": "20830",
				"flare": 60,
				"chaff": 120,
				"gun": 100,
			},
		},
	},

	"C101CC": {  # 1983 SI
		
		"Strike": {
			"CAS Cluster Bombs, Belouga*2, AIM-9M, Fuel*2 attacker @ low altitude": {
				'role': 'attacker',
				'targets': {"soft", "Parked Aircraft", "SAM"},
				'weapons': {
					"BLG66": ("Bombs", 2),
					"AIM-9M": ("Missiles", 2)
				},
				"fuel": 1508.64,
				"flare": 0,
				"chaff": 0,
				"gun": 100,
			},
		},
		
		"Anti-ship Strike": {
			"Anti-ship Strike, Sea Eagle*2, AIM-9P*2, DEFA-553 Cannon, 84% fuel attacker @ normal altitude": {
				'role': 'attacker',
				'targets': {"ship"},
				'weapons': {
					"Sea Eagle": ("ASM", 2),
					"AIM-9P": ("Missiles", 2)
				},
				"fuel": 1706,
				"flare": 0,
				"chaff": 0,
				"gun": 100,
			},
		},
	},

	"UH_1H": {  # 1956 SI
		"Transport": {
			"Default": {
				'targets': {},
				'weapons': {},
				"fuel": "631",
				"flare": 60,
				"chaff": 0,
				"gun": 100,
			},
		},
		"Strike": {
			"Rockets Hydra-70MK5*14 Minigun": {
				'targets': {"soft", "SAM", "armor", "Parked Aircraft"},
				'weapons': {
					"Hydra-70MK5": ("Rockets", 14),
				},
				"fuel": "631",
				"flare": 60,
				"chaff": 0,
				"gun": 100,
			},
		},
	},

	"AH_1W": {  # 1973 SI
		"Strike": {
			"Rockets Hard Hydra-70MK5*28": {
				'targets': {"soft", "armor", "SAM", "Parked Aircraft"},
				'weapons': {
					"Hydra-70MK5": ("Rockets", 28),
				},
				"fuel": 1163,
				"flare": 30,
				"chaff": 30,
				"gun": 100,
			},
			"BGM-71*8 HYDRA-70*38 40perc Fuel": {
				'targets': {"armor", "SAM"},
				'weapons': {
					"Hydra-70MK1": ("Rockets", 38),
					"BGM-71": ("Rockets", 8),
				},
				"fuel": 1163,
				"flare": 30,
				"chaff": 30,
				"gun": 100,
			},
			"ASM BGM-71D * 8": {
				'targets': {"SAM", "armor"},
				'weapons': {
					"BGM-71D": ("ASM", 8),
				},
				"fuel": 1125,
				"flare": 30,
				"chaff": 30,
				"gun": 100,
			},
			"ASM AGM-114*8": {
				'targets': {"SAM", "armor"},
				'weapons': {
					"AGM-114": ("ASM", 8),
				},
				"fuel": 1250,
				"flare": 30,
				"chaff": 30,
				"gun": 100,
			},
		},
	},

	"SH_60B": {  # 1984 SI
		"Transport": {
			"Default": {
				'targets': {},
				'weapons': {},
				"fuel": "1100",
				"flare": 30,
				"chaff": 30,
				"gun": 100,
			},
			"ASW Patrol": {
				'targets': {"Seahawk"},
				'weapons': {},
				"fuel": "1100",
				"flare": 30,
				"chaff": 30,
				"gun": 100,
			},
		},
	},

	"OH_58D": {  # 1973 SI
		"Strike": {
			"CAS ASM AGM-114*4": {
				'targets': {"soft", "SAM"},
				'weapons': {
					"AGM-114": ("ASM", 4),
				},
				"fuel": 445,
				"flare": 30,
				"chaff": 30,
				"gun": 100,
			},
			"CAS Rockets, Hydra-70*14": {
				'targets': {"soft", "SAM", "Parked Aircraft"},
				'weapons': {
					"Hydra-70MK1": ("Rockets", 14),
				},
				"fuel": "454",
				"flare": 30,
				"chaff": 30,
				"gun": 100,
			},
		},
	},

	"CH_47D": {  # 1979 SI
		"Transport": {
			"Default": {
				'targets': {},
				'weapons': {},
				"fuel": "3600",
				"flare": 120,
				"chaff": 120,
				"gun": 100,
			},
		},
	},

	"F_14A": {  # 1970
		"Intercept": {
			"Interceptor - AIM-54C*4 , AIM-7M*2, AIM-9M*2": {
				'targets': {},
				'weapons': {
					"AIM-54C-MK47": ("Missiles", 4),
					"AIM-7M": ("Missiles", 2),
					"AIM-9M": ("Missiles", 2),
				},
				"fuel": "7348",
				"flare": 15,
				"chaff": 30,
				"gun": 100,
			},
		},
		"CAP": {
			"CAP - AIM-7M*4, AIM-9M*2, Fuel*2": {
				'targets': {"Air Forces"},
				'weapons': {
					"AIM-7M": ("Missiles", 4),
					"AIM-9M": ("Missiles", 2),
				},
				"fuel": 7348,
				"flare": 15,
				"chaff": 30,
				"gun": 100,
			},
		},
	},

	"SA342M": {  # 1973 Syria
		"Strike": {
			"Strike Hot3x4, IR Deflector": {
				'targets': {"armor", "Parked Aircraft", "SAM"},
				'weapons': {
					"Hot-3": ("ASM", 4),
				},
				"fuel": 275,
				"flare": 32,
				"chaff": 0,
				"gun": 100,
			},
		},
	},

	"SA342Minigun": {  # 1973 Syria
		"Strike": {
			"SA342Minigun": {
				'targets': {"soft", "Parked Aircraft"},
				'weapons': {
					"UPK-23": ("Rockets", 2),
				},
				"fuel": 416.33,
				"flare": 32,
				"chaff": 0,
				"gun": 100,
			},
		},
	},

	"SA342Mistral": {  # 1973 Syria
		"Strike": {
			"CAS Rockets Mistral *4": {
				'targets': {"soft", "Parked Aircraft", "SAM"},
				'weapons': {
					"Mistral": ("ASM", 2),
				},
				"fuel": 416.33,
				"flare": 32,
				"chaff": 0,
				"gun": 100,
			},
		},
	},

	"MiG_31": {  # 1982
		"Intercept": {
			"Intercept High R-40R *2, R-33*4": {
				'targets': {},
				'weapons': {
					"R-40R": ("Missiles", 2),
					"R-33": ("Missiles", 4),
				},
				"fuel": "15500",
				"flare": 0,
				"chaff": 0,
				"gun": 100,
			},
		},
	},

	"MiG_29A": {  # 1983
		"Intercept": {
			"R-27R*2, R-60M*4, Fuel*1": {
				'targets': {},
				'weapons': {
					"R-27R": ("Missiles", 2),
					"R-60M": ("Missiles", 4),
				},
				"fuel": "3380",
				"flare": 30,
				"chaff": 30,
				"gun": 100,
			},
		},
	},

	"Su_27": {  # 1984
		"Intercept": {
			"Intercept Normal R-73*2 R-27ER*4 R-27ET*2": {
				'targets': {},
				'weapons': {
					"R-27ER": ("Missiles", 4),
					"R-27ET": ("Missiles", 2),
					"R-73": ("Missiles", 2),
				},
				"fuel": 5590.18,
				"flare": 96,
				"chaff": 96,
				"gun": 100,
			},
		},
	},

	"Su_25": {  # 1981
		"SEAD": {
			"ARM, Fuel*2, ECM": {
				'targets': {"SAM"},
				'weapons': {
					"Kh-58": ("ASM", 2),
					"R-60": ("Missiles", 4),
				},
				"fuel": "3790",
				"flare": 128,
				"chaff": 128,
				"gun": 100,
			},
		},
		"Strike": {
			"GA Rockets R-60*2 B-8M1*2": {
				'targets': {"SAM", "armor"},
				'weapons': {
					"S-8 KOM": ("Rockets", 40),
					"R-60": ("Missiles", 2),
				},
				"fuel": "2835",
				"flare": 128,
				"chaff": 128,
				"gun": 100,
			},
		},
	},

	"Mi_26": {  # 1977/1983
		"Transport": {
			"Default": {
				'targets': {},
				'weapons': {},
				"fuel": "9600",
				"flare": 192,
				"chaff": 0,
				"gun": 100,
			},
		},
	},

	"Mi_24P": {  # 1980
		"Transport": {
			"Default": {
				'targets': {},
				'weapons': {},
				"fuel": "1704",
				"flare": 192,
				"chaff": 0,
				"gun": 100,
			},
		},
		"Strike": {
			"CAS Rockets Hard S-13*10 9M114*4": {
				'targets': {"soft", "SAM"},
				'weapons': {
					"S-13": ("Rockets", 10),
					"9M114": ("ASM", 4),
				},
				"fuel": "1414",
				"flare": 192,
				"chaff": 0,
				"gun": 100,
			},
		},
	},

	"Mi_24V": {  # 1969/1972
		"Transport": {
			"Default": {
				'targets': {},
				'weapons': {},
				"fuel": "1704",
				"flare": 192,
				"chaff": 0,
				"gun": 100,
			},
		},
		"Strike": {
			"CAS Cannon Soft UPK-23*4 9M114*4": {
				'targets': {"armor", "SAM"},
				'weapons': {
					"9M114": ("ASM", 4),
					"UPK-23": ("Cannon", 4),
				},
				"fuel": "1704",
				"flare": 192,
				"chaff": 0,
				"gun": 100,
			},
		},
	},

	"Mi8MT": {  # 1961
		"Transport": {
			"Default": {
				'targets': {},
				'weapons': {},
				"fuel": 1929,
				"flare": 128,
				"chaff": 0,
				"gun": 100,
			},
		},
		"Strike": {
			"Rockets S-8KOM*80": {
				'targets': {"armor", "SAM"},
				'weapons': {
					"S-8 KOM": ("Rockets", 80),
				},
				"fuel": 1929,
				"flare": 128,
				"chaff": 0,
				"gun": 100,
			},
			"S-8KOM*20-Gsh-23L Autocannon*2": {
				'targets': {"armor", "SAM"},
				'weapons': {
					"S-8 KOM": ("Rockets", 20),
					"Gsh-23L": ("Cannon", 2),
				},
				"fuel": 1929,
				"flare": 128,
				"chaff": 0,
				"gun": 100,
			},
			"Gsh-23L Autocannon*2": {
				'targets': {"soft", "Parked Aircraft"},
				'weapons': {
					"Gsh-23L": ("Cannon", 2),
				},
				"fuel": 1929,
				"flare": 128,
				"chaff": 0,
				"gun": 100,
			},
			"Bombs Fab-100*6": {
				'targets': {"soft", "SAM", "Parked Aircraft"},
				'weapons': {
					"FAB-100": ("Bombs", 6),
				},
				"fuel": 1929,
				"flare": 128,
				"chaff": 0,
				"gun": 100,
			},
		},
	},

	"Tu_22M3": {
		"Strike": {
			"BAI FAB-500*33 FAB -250*36": {
				'role': 'bomber',
				'targets': {"Structure", "Bridge", "hard"},
				'weapons': {
					"FAB-500M62": ("Bombs", 33),
					"FAB-250M54": ("Bombs", 36)
				},
				"fuel": "50000",
				"flare": 48,
				"chaff": 48,
				"gun": 100
			}
		},
		"Anti-ship Strike": {
			"Antiship  Kh-22N*1": {
				'role': 'bomber',
				'targets': {"ship"},
				'weapons': {
					"Kh-22N": ("ASM", 1)
				},
				"fuel": "50000",
				"flare": 48,
				"chaff": 48,
				"gun": 100
			}
		}
	},

	"Su_24MR": {
		"Reconnaissance": {
			"Reco TANGAZH,ETHER,R-60M*2,Fuel*2": {
				'role': 'recon',
				'targets': {},
				'weapons': {
					"R-60M": ("Missiles", 2)
				},
				"fuel": "11700",
				"flare": 96,
				"chaff": 96,
				"gun": 100
			}
		}
	},

	"Su_24M": {
		"Anti-ship Strike": {
			"Antiship S24/240mm.235kg.he.frag*6": {
				'role': 'bomber',
				'targets': {"ship"},
				'weapons': {
					"S-24": ("Rockets", 6)
				},
				"fuel": "11700",
				"flare": 96,
				"chaff": 96,
				"gun": 100
			},
			"Antiship  S25/340mm.480kg.pntr*2 Fuel*3": {
				'role': 'bomber',
				'targets': {"ship"},
				'weapons': {
					"S-25L": ("Rockets", 2)
				},
				"fuel": "11700",
				"flare": 96,
				"chaff": 96,
				"gun": 100
			}
		},
		"SEAD": {
			"SEAD  Kh58*2 R60*4 L-081 escort sead bomber normal altitude": {
				'role': 'escort_sead_bomber',
				'targets': {"SAM"},
				'weapons': {
					"Kh-58": ("ASM", 2),
					"R-60": ("Missiles", 4)
				},
				"fuel": "11700",
				"flare": 96,
				"chaff": 96,
				"gun": 100
			},
			"SEAD  Kh58*2 R60*4 L-081 escort sead bomber high altitude": {
				'role': 'escort_sead_bomber',
				'targets': {"SAM"},
				'weapons': {
					"Kh-58": ("ASM", 2),
					"R-60": ("Missiles", 4)
				},
				"fuel": "11700",
				"flare": 96,
				"chaff": 96,
				"gun": 100
			}
		},
		"Strike": {
			"BAI Fab1500*2 R-60*4": {
				'role': 'bomber',
				'targets': {"Structure", "Bridge"},
				'weapons': {
					"FAB-1500M54": ("Bombs", 2)
				},
				"fuel": "11700",
				"flare": 96,
				"chaff": 96,
				"gun": 100
			},
			"BAI Fab250*8": {
				'role': 'bomber',
				'targets': {"Structure", "armor"},
				'weapons': {
					"FAB-250M54": ("Bombs", 8)
				},
				"fuel": "11700",
				"flare": 96,
				"chaff": 96,
				"gun": 100
			},
			"Pinpoint Strike R-60M*2 Kh-29T*2": {
				'role': 'bomber',
				'targets': {"Structure", "armor"},
				'weapons': {
					"FAB-250M54": ("Bombs", 8)
				},
				"fuel": "11700",
				"flare": 96,
				"chaff": 96,
				"gun": 100
			},
			"Pinpoint Strike R-60M*2 Kh-29L*2": {
				'role': 'bomber',
				'targets': {"Structure", "armor"},
				'weapons': {
					"FAB-250M54": ("Bombs", 8)
				},
				"fuel": "11700",
				"flare": 96,
				"chaff": 96,
				"gun": 100
			}
		}
	},

	"A_50": {
		"AWACS": {
			"Default": {
				'role': 'AWACS',
				'targets': {},
				'weapons': {},
				"fuel": "70000",
				"flare": 192,
				"chaff": 192,
				"gun": 100
			}
		}
	},

	"An_26B": {
		"Transport": {
			"Default": {
				'role': 'transporter',
				'targets': {},
				'weapons': {},
				"fuel": "5500",
				"flare": 384,
				"chaff": 384,
				"gun": 100
			}
		}
	},

	"MiG_21Bis": {
		"Anti-ship Strike": {
			"Antiship IPW R-3R*1, R-3S*1, FT800L, S-24B*2": {
				'role': 'attacker',
				'targets': {"ship"},
				'weapons': {
					"S-24": ("Rockets", 2),
					"R-3R": ("Missiles", 1),
					"R-3S": ("Missiles", 1)
				},
				"fuel": 2280,
				"flare": 0,
				"chaff": 0,
				"gun": 100
			},
			"IPW - Antiship Strike - R-3R*1, R-3S*1, FT800L, FAB-500*2": {
				'role': 'attacker',
				'targets': {"ship"},
				'weapons': {
					"FAB-500M62": ("Bombs", 2),
					"R-3R": ("Missiles", 1),
					"R-3S": ("Missiles", 1)
				},
				"fuel": 2280,
				"flare": 0,
				"chaff": 0,
				"gun": 100
			},
			"ASM -Kh66*2 Fuel - R-13M1": {
				'role': 'attacker',
				'targets': {"ship"},
				'weapons': {
					"Kh-66": ("ASM", 2),
					"R-13M1": ("Missiles", 2)
				},
				"fuel": 2280,
				"flare": 40,
				"chaff": 18,
				"gun": 100
			}
		},
		"Strike": {
			"IPW - Strike - R-3R*1, R-3S*1, FT800L, FAB-250*2": {
				'role': 'attacker',
				'targets': {"soft", "Parked Aircraft", "SAM"},
				'weapons': {
					"FAB-250M54": ("Bombs", 2),
					"R-3R": ("Missiles", 1),
					"R-3S": ("Missiles", 1)
				},
				"fuel": 2280,
				"flare": 0,
				"chaff": 0,
				"gun": 100
			},
			"IPW - Strike - R-3R*1, R-3S*1, FT800L, FAB-100*8": {
				'role': 'attacker',
				'targets': {"soft", "Parked Aircraft", "SAM"},
				'weapons': {
					"FAB-100": ("Bombs", 8),
					"R-3R": ("Missiles", 1),
					"R-3S": ("Missiles", 1)
				},
				"fuel": 2280,
				"flare": 0,
				"chaff": 0,
				"gun": 100
			},
			"IPW - Strike - R-3R*1, R-3S*1, FT800L, FAB-500*2": {
				'role': 'attacker',
				'targets': {"Bridge", "hard", "Structure"},
				'weapons': {
					"FAB-500M62": ("Bombs", 2),
					"R-3R": ("Missiles", 1),
					"R-3S": ("Missiles", 1)
				},
				"fuel": 2280,
				"flare": 0,
				"chaff": 0,
				"gun": 100
			},
			"IPW - Strike - R-3R*1, R-3S*1, FT800L, UB16UM*2 (S-5M)": {
				'role': 'attacker',
				'targets': {"soft"},
				'weapons': {
					"S-5 M": ("Rockets", 32),
					"R-3R": ("Missiles", 1),
					"R-3S": ("Missiles", 1)
				},
				"fuel": 2280,
				"flare": 0,
				"chaff": 0,
				"gun": 100
			},
			"IPW - Strike - R-3R*1, R-3S*1, FT800L, S-24B*2": {
				'role': 'attacker',
				'targets': {"soft", "Structure"},
				'weapons': {
					"S-24": ("Rockets", 2),
					"R-3R": ("Missiles", 1),
					"R-3S": ("Missiles", 1)
				},
				"fuel": 2280,
				"flare": 0,
				"chaff": 0,
				"gun": 100
			}
		}
	},

	"Su_17M4": {
		"Anti-ship Strike": {
			"IPW - AntishipStrike - FAB 500 M62*4": {
				'role': 'bomber',
				'targets': {"ship"},
				'weapons': {
					"FAB-500M62": ("Bombs", 4)
				},
				"fuel": "3770",
				"flare": 96,
				"chaff": 96,
				"gun": 100
			}
		},
		"Strike": {
			"IPW - Strike - FAB 500 M62*4": {
				'role': 'bomber',
				'targets': {"Structure", "Bridge"},
				'weapons': {
					"FAB-500M62": ("Bombs", 4)
				},
				"fuel": "3770",
				"flare": 96,
				"chaff": 96,
				"gun": 100
			},
			"CAS Bombs FAB-500*6 R-60M*2": {
				'role': 'bomber',
				'targets': {"Structure", "Bridge", "hard"},
				'weapons': {
					"FAB-500M62": ("Bombs", 6),
					"R-60M": ("Missiles", 2)
				},
				"fuel": "3770",
				"flare": 64,
				"chaff": 64,
				"gun": 100
			},
			"IPW - Strike - S-24B*4": {
				'role': 'attacker',
				'targets': {"Structure"},
				'weapons': {
					"S-24": ("Rockets", 4)
				},
				"fuel": "3770",
				"flare": 60,
				"chaff": 60,
				"gun": 100
			},
			"CAS Rockets S-25*4 R-60M*2 Fuel*2": {
				'role': 'attacker',
				'targets': {"hard", "Structure"},
				'weapons': {
					"S-25L": ("Rockets", 4),
					"R-60M": ("Missiles", 2)
				},
				"fuel": "3770",
				"flare": 60,
				"chaff": 60,
				"gun": 100
			}
		},
		"SEAD": {
			"ASM SEAD Kh-25MPU*4 R-60M*2 Fuel*2 escort bomber normal altitude": {
				'role': 'escort_sead_bomber',
				'targets': {"SAM"},
				'weapons': {
					"Kh-25MPU": ("ASM", 4),
					"R-60M": ("Missiles", 2)
				},
				"fuel": "3770",
				"flare": 96,
				"chaff": 96,
				"gun": 100
			}
		}
	},

	"MiG_27K": {
		"Anti-ship Strike": {
			"GA Kh-25MPL*2 R-60M*2 Fuel": {
				'role': 'attacker',
				'targets': {"ship"},
				'weapons': {
					"Kh-25ML": ("ASM", 2),
					"R-60M": ("Missiles", 2)
				},
				"fuel": "4500",
				"flare": 60,
				"chaff": 60,
				"gun": 100
			}
		},
		"Strike": {
			"GA Kh-25MR*2 R-60M*2 Fuel": {
				'role': 'attacker',
				'targets': {"SAM"},
				'weapons': {
					"Kh-25MR": ("ASM", 2),
					"R-60M": ("Missiles", 2)
				},
				"fuel": "4500",
				"flare": 60,
				"chaff": 60,
				"gun": 100
			},
			"GA Kh-25ML*2 R-60M*2 Fuel": {
				'role': 'attacker',
				'targets': {"SAM"},
				'weapons': {
					"Kh-25ML": ("ASM", 2),
					"R-60M": ("Missiles", 2)
				},
				"fuel": "4500",
				"flare": 60,
				"chaff": 60,
				"gun": 100
			},
			"CAS Heavy Cluster RBK-500-255*2 R-60M*2 Fuel": {
				'role': 'attacker',
				'targets': {"armor", "SAM"},
				'weapons': {
					"RBK-500PTAB": ("Bombs", 2),
					"R-60M": ("Missiles", 2)
				},
				"fuel": "4500",
				"flare": 60,
				"chaff": 60,
				"gun": 100
			},
			"BAI Fab-250*6 R-60M*2 Fuel": {
				'role': 'attacker',
				'targets': {"soft", "armor", "SAM", "Parked Aircraft"},
				'weapons': {
					"FAB-250M54": ("Bombs", 6),
					"R-60M": ("Missiles", 2)
				},
				"fuel": "4500",
				"flare": 60,
				"chaff": 60,
				"gun": 100
			}
		},
		"SEAD": {
			"Mig-27K SEAD Kh-25MPU*2 R-60M*2 Fuel escort bomber normal altitude": {
				'role': 'escort_sead_bomber',
				'targets': {"SAM"},
				'weapons': {
					"Kh-25MPU": ("ASM", 2),
					"R-60M": ("Missiles", 2)
				},
				"fuel": "4500",
				"flare": 60,
				"chaff": 60,
				"gun": 100
			}
		}
	},

	"MiG23MLD": {  # 1967
		"Intercept": {
			"R-24R*2, R-60M*4, Fuel": {
				'targets': {},
				'weapons': {
					"R-24R": ("AAM", 2),
					"R-60M": ("AAM", 4),
				},
				"fuel": 3800,
				"flare": 60,
				"chaff": 60,
				"gun": 100,
			},
			"R-24R*1, R-24T*1, R-60M*4, Fuel": {
				'targets': {},
				'weapons': {
					"R-24R": ("AAM", 1),
					"R-24T": ("AAM", 1),
					"R-60M": ("AAM", 4),
				},
				"fuel": 3800,
				"flare": 60,
				"chaff": 60,
				"gun": 100,
			},
		},
		"CAP": {
			"R-24R*2, R-60M*4, Fuel": {
				'targets': {"Air Forces"},
				'weapons': {
					"R-24R": ("AAM", 2),
					"R-60M": ("AAM", 4),
				},
				"fuel": 3800,
				"flare": 60,
				"chaff": 60,
				"gun": 100,
			},
			"R-24R*1, R-24T*1, R-60M*4, Fuel": {
				'targets': {"Air Forces"},
				'weapons': {
					"R-24R": ("AAM", 1),
					"R-24T": ("AAM", 1),
					"R-60M": ("AAM", 4),
				},
				"fuel": 3800,
				"flare": 60,
				"chaff": 60,
				"gun": 100,
			},
		},
		"Escort": {
			"R-24R*2, R-60M*4, Fuel escort bomber at normal altitude": {
				'role': 'escort_bomber',
				'targets': {},
				'weapons': {
					"R-24R": ("AAM", 2),
					"R-60M": ("AAM", 4),
				},
				"fuel": 3800,
				"flare": 60,
				"chaff": 60,
				"gun": 100,
			},
			"R-24R*1, R-24T*1, R-60M*4, Fuel escort attacker at normal altitude": {
				'role': 'escort_attacker',
				'targets': {},
				'weapons': {
					"R-24R": ("AAM", 1),
					"R-24T": ("AAM", 1),
					"R-60M": ("AAM", 4),
				},
				"fuel": 3800,
				"flare": 60,
				"chaff": 60,
				"gun": 100,
			},
			"R-24R*1, R-24T*1, R-60M*4, Fuel escort attacker at low altitude": {
				'role': 'escort_attacker',
				'targets': {},
				'weapons': {
					"R-24R": ("AAM", 1),
					"R-24T": ("AAM", 1),
					"R-60M": ("AAM", 4),
				},
				"fuel": 3800,
				"flare": 60,
				"chaff": 60,
				"gun": 100,
			},
		},
		"Fighter Sweep": {
			"R-24R*2, R-60M*4, Fuel": {
				'targets': {},
				'weapons': {
					"R-24R": ("AAM", 2),
					"R-60M": ("AAM", 4),
				},
				"fuel": 3800,
				"flare": 60,
				"chaff": 60,
				"gun": 100,
			},
			"R-24R*1, R-24T*1, R-60M*4, Fuel": {
				'targets': {},
				'weapons': {
					"R-24R": ("AAM", 1),
					"R-24T": ("AAM", 1),
					"R-60M": ("AAM", 4),
				},
				"fuel": 3800,
				"flare": 60,
				"chaff": 60,
				"gun": 100,
			},
		},
		"Strike": {
			"GA FAB-500*2 R-60M*2 FUEL 800*1": {
				'role': 'attacker',
				'targets': {"Structure", "Bridge"},
				'weapons': {
					"FAB-500M62": ("Bombs", 2),
					"R-60M": ("AAM", 2),
				},
				"fuel": 3800,
				"flare": 60,
				"chaff": 60,
				"gun": 100,
			},
			"GA FAB-250*2 R-60M*2 FUEL 800*1": {
				'role': 'attacker',
				'targets': {"Structure", "SAM", "armor", "Parked Aircraft", "soft"},
				'weapons': {
					"FAB-250M54": ("Bombs", 2),
					"R-60M": ("AAM", 2),
				},
				"fuel": 3800,
				"flare": 60,
				"chaff": 60,
				"gun": 100,
			},
			"GA S-8KOM*40 R-60M*2 FUEL 800*1b": {
				'role': 'attacker',
				'targets': {"Structure", "Bridge"},
				'weapons': {
					"S-8 KOM": ("Rockets", 40),
					"R-60M": ("AAM", 2),
				},
				"fuel": 3800,
				"flare": 60,
				"chaff": 60,
				"gun": 100,
			},
			"GA S-5KO*64 R-60M*2 FUEL 800*1b": {
				'role': 'attacker',
				'targets': {"Structure", "Bridge"},
				'weapons': {
					"S-5 KO": ("Rockets", 64),
					"R-60M": ("AAM", 2),
				},
				"fuel": 3800,
				"flare": 60,
				"chaff": 60,
				"gun": 100,
			},
		},
	},

	"MiG_25PD": {
		"Intercept": {
			"R-40R*4": {
				'role': None,
				'targets': {},
				'weapons': {
					"R-40R": ("Missiles", 4)
				},
				"fuel": "15245",
				"flare": 64,
				"chaff": 64,
				"gun": 100
			},
			"R-40R*2, R-40T*2": {
				'role': None,
				'targets': {},
				'weapons': {
					"R-40R": ("Missiles", 2),
					"R-40T": ("Missiles", 2)
				},
				"fuel": "15245",
				"flare": 64,
				"chaff": 64,
				"gun": 100
			}
		},
		"Fighter Sweep": {
			"R-40R*4": {
				'role': None,
				'targets': {},
				'weapons': {
					"R-40R": ("Missiles", 4)
				},
				"fuel": "15245",
				"flare": 64,
				"chaff": 64,
				"gun": 100
			},
			"R-40R*2, R-40T*2": {
				'role': None,
				'targets': {},
				'weapons': {
					"R-40R": ("Missiles", 2),
					"R-40T": ("Missiles", 2)
				},
				"fuel": "15245",
				"flare": 64,
				"chaff": 64,
				"gun": 100
			}
		},
		"CAP": {
			"R-40R*4": {
				'role': None,
				'targets': {"Air Forces"},
				'weapons': {
					"R-40R": ("Missiles", 4)
				},
				"fuel": "15245",
				"flare": 64,
				"chaff": 64,
				"gun": 100
			},
			"R-40R*2, R-40T*2": {
				'role': None,
				'targets': {"Air Forces"},
				'weapons': {
					"R-40R": ("Missiles", 2),
					"R-40T": ("Missiles", 2)
				},
				"fuel": "15245",
				"flare": 64,
				"chaff": 64,
				"gun": 100
			}
		},
		"Escort": {
			"R-40R*4": {
				'role': "escort_bomber",
				'targets': {},
				'weapons': {
					"R-40R": ("Missiles", 4)
				},
				"fuel": "15245",
				"flare": 64,
				"chaff": 64,
				"gun": 100
			},
			"R-40R*2, R-40T*2": {
				'role': "escort_bomber",
				'targets': {},
				'weapons': {
					"R-40R": ("Missiles", 2),
					"R-40T": ("Missiles", 2)
				},
				"fuel": "15245",
				"flare": 64,
				"chaff": 64,
				"gun": 100
			}
		}
	},

	"MiG_25RBT": {
		"Reconnaissance": {
			"R-40R*4": {
				'role': "recon",
				'targets': {},
				'weapons': {
					"R-40R": ("Missiles", 4)
				},
				"fuel": "15245",
				"flare": 64,
				"chaff": 64,
				"gun": 100
			}
		},
		"AWACS": {
			"Default": {
				'role': "AWACS",
				'targets': {},
				'weapons': {},
				"fuel": "15245",
				"flare": 0,
				"chaff": 0,
				"gun": 100
			}
		}
	},

	"Il_76MD": {
		"Transport": {
			"Default": {
				'role': "transporter",
				'targets': {},
				'weapons': {},
				"fuel": 40000,
				"flare": 96,
				"chaff": 96,
				"gun": 100
			}
		}
	},

	"L_39C": {
		"Anti-ship Strike": {
			"Antiship IPW R-3R*1, R-3S*1, FT800L, S-24B*2": {
				'role': "attacker",
				'targets': {"ship"},
				'weapons': {
					"S-24": ("Rockets", 2),
					"R-3S": ("Missiles", 1),
					"R-3R": ("Missiles", 1)
				},
				"fuel": 2280,
				"flare": 0,
				"chaff": 0,
				"gun": 100
			},
			"IPW - Antiship Strike - R-3R*1, R-3S*1, FT800L, FAB-500*2": {
				'role': "attacker",
				'targets': {"ship"},
				'weapons': {
					"FAB-500M62": ("Bombs", 2),
					"R-3S": ("Missiles", 1),
					"R-3R": ("Missiles", 1)
				},
				"fuel": 2280,
				"flare": 0,
				"chaff": 0,
				"gun": 100
			}
		},
		"Intercept": {
			"IPW R-3R*2, R-3S*2, FT800L": {
				'role': None,
				'targets': {},
				'weapons': {
					"R-3R": ("Missiles", 2),
					"R-3S": ("Missiles", 2)
				},
				"fuel": 2280,
				"flare": 0,
				"chaff": 0,
				"gun": 100
			}
		},
		"CAP": {
			"IPW R-3R*2, R-3S*2, FT800L": {
				'role': None,
				'targets': {"Air Forces"},
				'weapons': {
					"R-3R": ("Missiles", 2),
					"R-3S": ("Missiles", 2)
				},
				"fuel": 2280,
				"flare": 0,
				"chaff": 0,
				"gun": 100
			}
		},
		"Escort": {
			"IPW R-3R*2, R-3S*2, FT800L escort attacker at normal altitude": {
				'role': "escort_attacker",
				'targets': {},
				'weapons': {
					"R-3R": ("Missiles", 2),
					"R-3S": ("Missiles", 2)
				},
				"fuel": 2280,
				"flare": 0,
				"chaff": 0,
				"gun": 100
			},
			"IPW R-3R*2, R-3S*2, FT800L escort attacker at low altitude": {
				'role': "escort_attacker",
				'targets': {},
				'weapons': {
					"R-3R": ("Missiles", 2),
					"R-3S": ("Missiles", 2)
				},
				"fuel": 2280,
				"flare": 0,
				"chaff": 0,
				"gun": 100
			}
		},
		"Fighter Sweep": {
			"IPW R-3R*2, R-3S*2, FT800L": {
				'role': None,
				'targets': {},
				'weapons': {
					"R-3R": ("Missiles", 2),
					"R-3S": ("Missiles", 2)
				},
				"fuel": 2280,
				"flare": 0,
				"chaff": 0,
				"gun": 100
			}
		},
		"Strike": {
			"IPW - Strike - R-3R*1, R-3S*1, FT800L, FAB-250*2": {
				'role': "attacker",
				'targets': {"soft", "Parked Aircraft", "SAM", "armor"},
				'weapons': {
					"FAB-250M54": ("Bombs", 2),
					"R-3R": ("Missiles", 1),
					"R-3S": ("Missiles", 1)
				},
				"fuel": 2280,
				"flare": 0,
				"chaff": 0,
				"gun": 100
			},
			"IPW - Strike - R-3R*1, R-3S*1, FT800L, FAB-100*8": {
				'role': "attacker",
				'targets': {"soft", "Parked Aircraft", "SAM", "armor"},
				'weapons': {
					"FAB-100": ("Bombs", 8),
					"R-3R": ("Missiles", 1),
					"R-3S": ("Missiles", 1)
				},
				"fuel": 2280,
				"flare": 0,
				"chaff": 0,
				"gun": 100
			},
			"IPW - Strike - R-3R*1, R-3S*1, FT800L, UB16UM*2": {
				'role': "attacker",
				'targets': {"soft", "armor"},
				'weapons': {
					"S-5 M": ("Rockets", 32),
					"R-3R": ("Missiles", 1),
					"R-3S": ("Missiles", 1)
				},
				"fuel": 2280,
				"flare": 0,
				"chaff": 0,
				"gun": 100
			},
			"IPW - Strike - R-3R*1, R-3S*1, FT800L, S-24B*2": {
				'role': "attacker",
				'targets': {"soft", "armor"},
				'weapons': {
					"S-24": ("Rockets", 2),
					"R-3R": ("Missiles", 1),
					"R-3S": ("Missiles", 1)
				},
				"fuel": 2280,
				"flare": 0,
				"chaff": 0,
				"gun": 100
			}
		}
	}

}
