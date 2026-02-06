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

#@dataclass
#Class Weapon_Data:

AIR_WEAPONS = {}


AIR_WEAPONS = {
   
    "blue": {
        'MISSILES_AAM': {
            "Riferimento AAM": {
                "type": "AAM",
                "seeker": "radar",
                "task": ["A2A"],
                "start_service": 1974,
                "end_service": 2004,
                "cost": 400,
                "tnt": 61,
                "reliability": 0.8,
                "range": 160,
                "semiactive_range": 130,
                "active_range": 18,
                "max_height": 24.8,
                "max_speed": 3.8,
                "manouvrability": 0.6
            },
            "AIM-54A-MK47": {
                "type": "AAM",
                "model": "AIM-54A-MK47",
                "users": ["USA", "Iran"],
                "seeker": "radar",
                "task": ["A2A"],
                "start_service": 1974,
                "end_service": 2004,
                "cost": 400,
                "tnt": 61,
                "reliability": 0.8,
                "range": 160,
                "semiactive_range": 130,
                "active_range": 18,
                "max_height": 24.8,
                "max_speed": 3.8,
                "manouvrability": 0.6,
                "accuracy": 0.75
            },
            "AIM-54A-MK60": {
                "type": "AAM",
                "model": "AIM-54A-MK60",
                "users": ["USA", "Iran"],
                "seeker": "radar",
                "task": ["A2A"],
                "start_service": 1975,
                "end_service": 2004,
                "cost": 400,
                "tnt": 61,
                "reliability": 0.8,
                "range": 160,
                "semiactive_range": 130,
                "active_range": 18,
                "max_height": 24.8,
                "max_speed": 3.8,
                "manouvrability": 0.6,
                "accuracy": 0.75
            },
            "AIM-54C-MK47": {
                "type": "AAM",
                "model": "AIM-54C-MK47",
                "users": ["USA", "Iran"],
                "seeker": "radar",
                "task": ["A2A"],
                "start_service": 1982,
                "end_service": 2004,
                "cost": 477,
                "tnt": 61,
                "reliability": 0.8,
                "range": 160,
                "semiactive_range": 148,
                "active_range": 18,
                "max_height": 24.8,
                "max_speed": 4.5,
                "manouvrability": 0.73,
                "accuracy": 0.8
            },
            "AIM-54C-MK60": {
                "type": "AAM",
                "model": "AIM-54C-MK60",
                "users": ["USA", "Iran"],
                "seeker": "radar",
                "task": ["A2A"],
                "start_service": 1982,
                "end_service": 2004,
                "cost": 477,
                "tnt": 61,
                "reliability": 0.8,
                "range": 160,
                "semiactive_range": 148,
                "active_range": 18,
                "max_height": 24.8,
                "max_speed": 4.5,
                "manouvrability": 0.73,
                "accuracy": 0.8
            },
            "AIM-7E": {
                "type": "AAM",
                "model": "AIM-7E",
                "users": ["USA", "UK", "Germany", "Italy", "Japan", "Turkey", "Greece", "Israel", "South Korea", "Taiwan"],
                "seeker": "radar",
                "task": ["A2A"],
                "start_service": 1970,
                "end_service": None,
                "cost": 125,
                "tnt": 40,
                "reliability": 0.8,
                "range": 45,
                "semiactive_range": 45,
                "active_range": None,
                "max_height": 18,
                "max_speed": 3,
                "manouvrability": 0.6,
                "accuracy": 0.6
            },
            "AIM-7F": {
                "type": "AAM",
                "model": "AIM-7F",
                "users": ["USA", "UK", "Germany", "Italy", "Japan", "Turkey", "Greece", "Israel", "South Korea", "Taiwan"],
                "seeker": "radar",
                "task": ["A2A"],
                "start_service": 1975,
                "end_service": None,
                "cost": 130,
                "tnt": 40,
                "reliability": 0.8,
                "range": 70,
                "semiactive_range": 70,
                "active_range": None,
                "max_height": 18,
                "max_speed": 3,
                "manouvrability": 0.6,
                "accuracy": 0.65
            },
            "AIM-7M": {
                "type": "AAM",
                "model": "AIM-7M",
                "users": ["USA", "UK", "Germany", "Italy", "Japan", "Turkey", "Greece", "Israel", "South Korea", "Taiwan", "Saudi Arabia"],
                "seeker": "radar",
                "task": ["A2A"],
                "start_service": 1982,
                "end_service": None,
                "cost": 150,
                "tnt": 40,
                "reliability": 0.8,
                "range": 70,
                "semiactive_range": 70,
                "active_range": None,
                "max_height": 18,
                "max_speed": 3,
                "manouvrability": 0.65,
                "accuracy": 0.7
            },
            "AIM-7MH": {
                "type": "AAM",
                "model": "AIM-7MH",
                "users": ["USA", "UK", "Germany", "Italy", "Japan", "Turkey", "Greece", "Israel", "South Korea", "Taiwan", "Saudi Arabia"],
                "seeker": "radar",
                "task": ["A2A"],
                "start_service": 1985,
                "end_service": None,
                "cost": 160,
                "tnt": 40,
                "reliability": 0.8,
                "range": 70,
                "semiactive_range": 70,
                "active_range": None,
                "max_height": 18,
                "max_speed": 3,
                "manouvrability": 0.66,
                "accuracy": 0.72
            },
            "AIM-7P": {
                "type": "AAM",
                "model": "AIM-7P",
                "users": ["USA", "UK", "Germany", "Italy", "Japan", "Turkey", "Greece", "Israel", "South Korea", "Taiwan", "Saudi Arabia"],
                "seeker": "radar",
                "task": ["A2A"],
                "start_service": 1987,
                "end_service": None,
                "cost": 170,
                "tnt": 40,
                "reliability": 0.8,
                "range": 70,
                "semiactive_range": 70,
                "active_range": None,
                "max_height": 18,
                "max_speed": 3,
                "manouvrability": 0.7,
                "accuracy": 0.75
            },
            "AIM-9B": {
                "type": "AAM",
                "model": "AIM-9B",
                "users": ["USA", "UK", "Germany", "France", "Italy", "Japan", "Turkey", "Greece", "Israel", "Taiwan", "South Korea"],
                "seeker": "infrared",
                "task": ["A2A"],
                "start_service": 1956,
                "end_service": None,
                "cost": 60,
                "tnt": 4.5,
                "reliability": 0.5,
                "range": 4.6,
                "max_height": 18,
                "max_speed": 1.7,
                "manouvrability": 0.5,
                "accuracy": 0.45
            },
            "AIM-9P": {
                "type": "AAM",
                "model": "AIM-9P",
                "users": ["USA", "UK", "Germany", "Italy", "Japan", "Turkey", "Greece", "Israel", "Taiwan", "South Korea", "Indonesia", "Pakistan"],
                "seeker": "infrared",
                "task": ["A2A"],
                "start_service": 1975,
                "end_service": None,
                "cost": 70,
                "tnt": 4.5,
                "reliability": 0.6,
                "range": 18.5,
                "max_height": 18,
                "max_speed": 2,
                "manouvrability": 0.5,
                "accuracy": 0.55
            },
            "AIM-9P5": {
                "type": "AAM",
                "model": "AIM-9P5",
                "users": ["USA", "Germany", "Italy", "Turkey", "Greece", "Israel", "Taiwan", "South Korea", "Indonesia"],
                "seeker": "infrared",
                "task": ["A2A"],
                "start_service": 1975,
                "end_service": None,
                "cost": 73,
                "tnt": 4.5,
                "reliability": 0.6,
                "range": 18.5,
                "max_height": 18,
                "max_speed": 2,
                "manouvrability": 0.6,
                "accuracy": 0.58
            },
            "AIM-9L": {
                "type": "AAM",
                "model": "AIM-9L",
                "users": ["USA", "UK", "Germany", "Italy", "Japan", "Turkey", "Greece", "Israel", "Taiwan", "South Korea", "Saudi Arabia", "Australia"],
                "seeker": "infrared",
                "task": ["A2A"],
                "start_service": 1975,
                "end_service": None,
                "cost": 75,
                "tnt": 9.4,
                "reliability": 0.6,
                "range": 18.5,
                "max_height": 18,
                "max_speed": 2.5,
                "manouvrability": 0.7,
                "accuracy": 0.7
            },
            "AIM-9M": {
                "type": "AAM",
                "model": "AIM-9M",
                "users": ["USA", "UK", "Germany", "Italy", "Japan", "Turkey", "Greece", "Israel", "Taiwan", "South Korea", "Saudi Arabia", "Australia"],
                "seeker": "infrared",
                "task": ["A2A"],
                "start_service": 1982,
                "end_service": None,
                "cost": 80,
                "tnt": 9.4,
                "reliability": 0.6,
                "range": 18.5,
                "max_height": 18,
                "max_speed": 2.5,
                "manouvrability": 0.7,
                "accuracy": 0.75
            },
            "AIM-9X": {
                "type": "AAM",
                "model": "AIM-9X",
                "users": ["USA", "UK", "Germany", "Italy", "Japan", "Turkey", "Greece", "Israel", "Taiwan", "South Korea", "Saudi Arabia", "Australia", "Poland"],
                "seeker": "infrared",
                "task": ["A2A"],
                "start_service": 2003,
                "end_service": None,
                "cost": 100,
                "tnt": 9.4,
                "reliability": 0.6,
                "range": 37,
                "max_height": 25,
                "max_speed": 2.9,
                "manouvrability": 0.9,
                "accuracy": 0.9
            },
            "R-550": {
                "type": "AAM",
                "model": "R-550",
                "users": ["France", "Argentina", "Brazil", "Chile", "Ecuador", "Egypt", "India", "Iraq", "Kuwait", "Pakistan", "Peru", "Qatar", "UAE"],
                "seeker": "infrared",
                "task": ["A2A"],
                "start_service": 1975,
                "end_service": None,
                "cost": 27.5,
                "tnt": 12.5,
                "reliability": 0.6,
                "range": 10,
                "max_height": 18,
                "max_speed": 2.8,
                "manouvrability": 0.6,
                "accuracy": 0.65
            },
            "R-530IR": {
                "type": "AAM",
                "model": "R-530IR",
                "users": ["France", "Argentina", "Australia", "Brazil", "Israel", "Pakistan", "South Africa", "Spain"],
                "seeker": "infrared",
                "task": ["A2A"],
                "start_service": 1975,
                "end_service": None,
                "cost": 157,
                "tnt": 27,
                "reliability": 0.6,
                "range": 18,
                "max_height": 18,
                "max_speed": 3,
                "manouvrability": 0.6,
                "accuracy": 0.55
            },
            "R-530EM": {
                "type": "AAM",
                "model": "R-530EM",
                "users": ["France", "Argentina", "Australia", "Brazil", "Israel", "Pakistan", "South Africa", "Spain"],
                "seeker": "radar",
                "task": ["A2A"],
                "start_service": 1975,
                "end_service": None,
                "cost": 157,
                "tnt": 30,
                "reliability": 0.7,
                "range": 40,
                "semiactive_range": 40,
                "max_height": 20,
                "max_speed": 4,
                "manouvrability": 0.7,
                "accuracy": 0.6
            },
            "RB-24": {
                "type": "AAM",
                "model": "RB-24",
                "users": ["Sweden"],
                "seeker": "infrared",
                "task": ["A2A"],
                "start_service": 1956,
                "end_service": None,
                "cost": 60,
                "tnt": 4.5,
                "reliability": 0.5,
                "range": 4.6,
                "max_height": 18,
                "max_speed": 1.7,
                "manouvrability": 0.5,
                "accuracy": 0.45
            },
            "RB-24J": {
                "type": "AAM",
                "model": "RB-24J",
                "users": ["Sweden"],
                "seeker": "infrared",
                "task": ["A2A"],
                "start_service": 1975,
                "end_service": None,
                "cost": 75,
                "tnt": 4.5,
                "reliability": 0.6,
                "range": 18.5,
                "max_height": 18,
                "max_speed": 2,
                "manouvrability": 0.6,
                "accuracy": 0.6
            },
            "RB-74": {
                "type": "AAM",
                "model": "RB-74",
                "users": ["Sweden"],
                "seeker": "infrared",
                "task": ["A2A"],
                "start_service": 1975,
                "end_service": None,
                "cost": 73,
                "tnt": 9.4,
                "reliability": 0.6,
                "range": 18.5,
                "max_height": 18,
                "max_speed": 2.5,
                "manouvrability": 0.7,
                "accuracy": 0.7
            },            
        },  
        'MISSILES_ASM': {
            "RB-05A": {
                "type": "ASM",
                "model": "RB-05A",
                "users": ["Sweden"],
                "seeker": "electro-optical",
                "task": ["Anti-ship Strike", "Strike", "SEAD"],
                "start_service": 1972,
                "end_service": 2005,
                "cost": 180,
                "tnt": 160,
                "reliability": 0.5,
                "range": 9,
                "max_height": 18,
                "max_speed": 1,
                "manouvrability": 0.4,
                 "efficiency": {
                    "ship": {
                        "big": {"accuracy": 0.8, "destroy_capacity": 0.6},
                        "med": {"accuracy": 0.7, "destroy_capacity": 0.8},
                        "small": {"accuracy": 0.5, "destroy_capacity": 1}
                    },
                    "soft": {
                        "big": {"accuracy": 0.8, "destroy_capacity": 0.9},
                        "med": {"accuracy": 0.75, "destroy_capacity": 1},
                        "small": {"accuracy": 0.65, "destroy_capacity": 1}
                    },
                    "armor": {
                        "big": {"accuracy": 0.8, "destroy_capacity": 0.8},
                        "med": {"accuracy": 0.7, "destroy_capacity": 0.9},
                        "small": {"accuracy": 0.6, "destroy_capacity": 1}
                    },
                    "SAM": {
                        "big": {"accuracy": 0.8, "destroy_capacity": 0.8},
                        "med": {"accuracy": 0.75, "destroy_capacity": 0.9},
                        "small": {"accuracy": 0.6, "destroy_capacity": 1}
                    }
                }
            },
            "RB-15F": {
                "type": "ASM",
                "model": "RB-15F",
                "users": ["Sweden"],
                "task": ["Anti-ship Strike"],
                "start_service": 1985,
                "end_service": None,
                "cost": 720,
                "tnt": 220,
                "range": 75,
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "ship": {
                        "big": {
                            "accuracy": 1,
                            "destroy_capacity": 0.6
                        },
                        "med": {
                            "accuracy": 1,
                            "destroy_capacity": 0.8
                        },
                        "small": {
                            "accuracy": 1,
                            "destroy_capacity": 1
                        }
                    }
                }
            },
            "AGM-45": {
                "type": "ASM",
                "model": "AGM-45",
                "users": ["USA", "Israel", "UK"],
                "task": ["SEAD"],
                "start_service": 1966,
                "end_service": 1992,
                "cost": 32,
                "tnt": 66,
                "range": 10,
                "perc_efficiency_variability": 0.2,
                "efficiency": {
                    "SAM": {
                        "big": {"accuracy": 0.7, "destroy_capacity": 0.7},
                        "med": {"accuracy": 0.7, "destroy_capacity": 0.8},
                        "small": {"accuracy": 0.6, "destroy_capacity": 1}
                    }
                }
            },
            "AGM-84A": {
                "type": "ASM",
                "model": "AGM-84A",
                "users": ["USA", "UK", "Germany", "Denmark", "Australia", "Japan", "South Korea", "Taiwan", "Egypt", "Saudi Arabia"],
                "task": ["Anti-ship Strike"],
                "start_service": 1970,
                "end_service": None,
                "cost": 720,
                "tnt": 221,
                "range": 50,
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "ship": {
                        "big": {"accuracy": 1, "destroy_capacity": 0.6},
                        "med": {"accuracy": 1, "destroy_capacity": 0.8},
                        "small": {"accuracy": 1, "destroy_capacity": 1}
                    }
                }
            },
            "AGM-88": {
                "type": "ASM",
                "model": "AGM-88",
                "users": ["USA", "Germany", "Italy", "Spain", "Greece", "Turkey", "Israel", "Australia", "South Korea", "Taiwan"],
                "task": ["SEAD"],
                "start_service": 1966,
                "end_service": 1992,
                "cost": 200,
                "tnt": 88,
                "range": 80,
                "perc_efficiency_variability": 0.2,
                "efficiency": {
                    "SAM": {
                        "big": {"accuracy": 0.8, "destroy_capacity": 0.77},
                        "med": {"accuracy": 0.7, "destroy_capacity": 0.88},
                        "small": {"accuracy": 0.6, "destroy_capacity": 1}
                    }
                }
            },
            "Kormoran": {
                "type": "ASM",
                "model": "Kormoran",
                "users": ["Germany", "Italy"],
                "task": ["Anti-ship Strike"],
                "start_service": 1973,
                "end_service": None,
                "cost": 200,
                "tnt": 165,
                "range": 30,
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "ship": {
                        "big": {"accuracy": 1, "destroy_capacity": 0.45},
                        "med": {"accuracy": 1, "destroy_capacity": 0.7},
                        "small": {"accuracy": 1, "destroy_capacity": 1}
                    }
                }
            },
            "RB-05E": {
                "type": "ASM",
                "model": "RB-05E",
                "users": ["Sweden"],
                "task": ["Anti-ship Strike", "Strike", "SEAD"],
                "start_service": 1972,
                "end_service": 2005,
                "cost": 300,
                "tnt": 160,
                "range": 9,
                "perc_efficiency_variability": 0.2,
                "efficiency": {
                    "ship": {
                        "big": {"accuracy": 0.8, "destroy_capacity": 0.6},
                        "med": {"accuracy": 0.7, "destroy_capacity": 0.8},
                        "small": {"accuracy": 0.5, "destroy_capacity": 1}
                    },
                    "soft": {
                        "big": {"accuracy": 0.8, "destroy_capacity": 0.9},
                        "med": {"accuracy": 0.75, "destroy_capacity": 1},
                        "small": {"accuracy": 0.65, "destroy_capacity": 1}
                    },
                    "armor": {
                        "big": {"accuracy": 0.8, "destroy_capacity": 0.8},
                        "med": {"accuracy": 0.7, "destroy_capacity": 0.9},
                        "small": {"accuracy": 0.6, "destroy_capacity": 1}
                    },
                    "SAM": {
                        "big": {"accuracy": 0.8, "destroy_capacity": 0.8},
                        "med": {"accuracy": 0.75, "destroy_capacity": 0.9},
                        "small": {"accuracy": 0.6, "destroy_capacity": 1}
                    }
                }
            },
            "RB-04E": {
                "type": "ASM",
                "model": "RB-04E",
                "users": ["Sweden"],
                "task": ["Anti-ship Strike"],
                "start_service": 1975,
                "end_service": 2000,
                "cost": 700,
                "tnt": 300,
                "range": 32,
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "ship": {
                        "big": {"accuracy": 0.9, "destroy_capacity": 0.8},
                        "med": {"accuracy": 0.8, "destroy_capacity": 0.9},
                        "small": {"accuracy": 0.7, "destroy_capacity": 1}
                    }
                }
            },
            "Sea Eagle": {
                "type": "ASM",
                "model": "Sea Eagle",
                "users": ["UK", "India", "Saudi Arabia"],
                "task": ["Anti-ship Strike"],
                "start_service": 1985,
                "end_service": None,
                "cost": 700,
                "tnt": 230,
                "range": 100,
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "ship": {
                        "big": {"accuracy": 0.9, "destroy_capacity": 0.6},
                        "med": {"accuracy": 0.8, "destroy_capacity": 0.7},
                        "small": {"accuracy": 0.7, "destroy_capacity": 0.8}
                    }
                }
            },
            "RB-75T": {
                "type": "ASM",
                "model": "RB-75T",
                "users": ["Sweden"],
                "task": ["Anti-ship Strike", "Strike", "SEAD"],
                "start_service": 1972,
                "end_service": None,
                "cost": 160,
                "tnt": 52,
                "range": 15,
                "perc_efficiency_variability": 0.05,
                "efficiency": {
                    "ship": {
                        "big": {"accuracy": 1, "destroy_capacity": 0.6},
                        "med": {"accuracy": 1, "destroy_capacity": 0.8},
                        "small": {"accuracy": 1, "destroy_capacity": 1}
                    },
                    "soft": {
                        "big": {"accuracy": 0.8, "destroy_capacity": 1},
                        "med": {"accuracy": 0.8, "destroy_capacity": 1},
                        "small": {"accuracy": 0.7, "destroy_capacity": 1}
                    },
                    "armor": {
                        "big": {"accuracy": 0.8, "destroy_capacity": 0.8},
                        "med": {"accuracy": 0.8, "destroy_capacity": 0.9},
                        "small": {"accuracy": 0.7, "destroy_capacity": 1}
                    },
                    "SAM": {
                        "big": {"accuracy": 1, "destroy_capacity": 1},
                        "med": {"accuracy": 1, "destroy_capacity": 1},
                        "small": {"accuracy": 0.9, "destroy_capacity": 1}
                    }
                }
            },
            "RB-15": {
                "type": "ASM",
                "model": "RB-15",
                "users": ["Sweden", "Finland", "Croatia"],
                "task": ["Anti-ship Strike"],
                "start_service": 1989,
                "end_service": None,
                "cost": 350,
                "tnt": 200,
                "range": 70,
                "perc_efficiency_variability": 0.05,
                "efficiency": {
                    "ship": {
                        "big": {"accuracy": 1, "destroy_capacity": 0.6},
                        "med": {"accuracy": 1, "destroy_capacity": 0.8},
                        "small": {"accuracy": 1, "destroy_capacity": 1}
                    }
                }
            },
            "AGM-65D": {
                "type": "ASM",
                "model": "AGM-65D",
                "users": ["USA", "UK", "Germany", "Italy", "Spain", "Greece", "Turkey", "Israel", "Egypt", "South Korea", "Taiwan"],
                "task": ["Anti-ship Strike", "Strike", "SEAD"],
                "start_service": 1967,
                "end_service": None,
                "cost": 160,
                "tnt": 52,
                "range": 15,
                "perc_efficiency_variability": 0.05,
                "efficiency": {
                    "ship": {
                        "big": {"accuracy": 1, "destroy_capacity": 0.6},
                        "med": {"accuracy": 1, "destroy_capacity": 0.8},
                        "small": {"accuracy": 1, "destroy_capacity": 1}
                    },
                    "soft": {
                        "big": {"accuracy": 0.8, "destroy_capacity": 1},
                        "med": {"accuracy": 0.8, "destroy_capacity": 1},
                        "small": {"accuracy": 0.7, "destroy_capacity": 1}
                    },
                    "armor": {
                        "big": {"accuracy": 0.8, "destroy_capacity": 0.8},
                        "med": {"accuracy": 0.8, "destroy_capacity": 0.9},
                        "small": {"accuracy": 0.7, "destroy_capacity": 1}
                    },
                    "SAM": {
                        "big": {"accuracy": 1, "destroy_capacity": 1},
                        "med": {"accuracy": 1, "destroy_capacity": 1},
                        "small": {"accuracy": 0.9, "destroy_capacity": 1}
                    }
                }
            },
            "AGM-65K": {
                "type": "ASM",
                "model": "AGM-65K",
                "users": ["USA", "South Korea", "Taiwan"],
                "task": ["Anti-ship Strike", "Strike", "SEAD"],
                "start_service": 1970,
                "end_service": None,
                "cost": 160,
                "tnt": 52,
                "range": 15,
                "perc_efficiency_variability": 0.05,
                "efficiency": {
                    "ship": {
                        "big": {"accuracy": 1, "destroy_capacity": 0.6},
                        "med": {"accuracy": 1, "destroy_capacity": 0.8},
                        "small": {"accuracy": 1, "destroy_capacity": 1}
                    },
                    "soft": {
                        "big": {"accuracy": 0.8, "destroy_capacity": 1},
                        "med": {"accuracy": 0.8, "destroy_capacity": 1},
                        "small": {"accuracy": 0.7, "destroy_capacity": 1}
                    },
                    "armor": {
                        "big": {"accuracy": 0.8, "destroy_capacity": 0.8},
                        "med": {"accuracy": 0.8, "destroy_capacity": 0.9},
                        "small": {"accuracy": 0.7, "destroy_capacity": 1}
                    },
                    "SAM": {
                        "big": {"accuracy": 1, "destroy_capacity": 1},
                        "med": {"accuracy": 1, "destroy_capacity": 1},
                        "small": {"accuracy": 0.9, "destroy_capacity": 1}
                    }
                }
            },
            "AGM-114": {
                "type": "ASM",
                "model": "AGM-114",
                "users": ["USA", "UK", "Germany", "France", "Italy", "Israel", "Saudi Arabia", "UAE", "Japan", "South Korea", "Australia"],
                "task": ["Strike", "SEAD", "Anti-ship Strike"],
                "start_service": 1984,
                "end_service": None,
                "cost": 80,
                "tnt": 9,
                "range": 8,
                "perc_efficiency_variability": 0.05,
                "efficiency": {
                    "soft": {
                        "big": {"accuracy": 1, "destroy_capacity": 0.5},
                        "med": {"accuracy": 1, "destroy_capacity": 0.6},
                        "small": {"accuracy": 0.9, "destroy_capacity": 0.7}
                    },
                    "armor": {
                        "big": {"accuracy": 1, "destroy_capacity": 0.4},
                        "med": {"accuracy": 1, "destroy_capacity": 0.5},
                        "small": {"accuracy": 0.9, "destroy_capacity": 0.6}
                    },
                    "SAM": {
                        "big": {"accuracy": 1, "destroy_capacity": 0.6},
                        "med": {"accuracy": 1, "destroy_capacity": 0.7},
                        "small": {"accuracy": 0.9, "destroy_capacity": 0.8}
                    }
                }
            },
            "BGM-71D": {
                "type": "ASM",
                "model": "BGM-71D",
                "users": ["USA", "UK", "Germany", "Italy", "Turkey", "Greece", "Israel", "Egypt", "Saudi Arabia", "Iran", "Pakistan"],
                "task": ["Strike", "SEAD"],
                "start_service": 1970,
                "end_service": None,
                "cost": 12,
                "tnt": 6.14,
                "range": 3,
                "perc_efficiency_variability": 0.05,
                "efficiency": {
                    "soft": {
                        "big": {"accuracy": 1, "destroy_capacity": 1},
                        "med": {"accuracy": 1, "destroy_capacity": 1},
                        "small": {"accuracy": 0.9, "destroy_capacity": 1}
                    },
                    "armor": {
                        "big": {"accuracy": 1, "destroy_capacity": 0.8},
                        "med": {"accuracy": 1, "destroy_capacity": 0.9},
                        "small": {"accuracy": 0.9, "destroy_capacity": 1}
                    },
                    "SAM": {
                        "big": {"accuracy": 1, "destroy_capacity": 0.8},
                        "med": {"accuracy": 1, "destroy_capacity": 0.9},
                        "small": {"accuracy": 0.9, "destroy_capacity": 1}
                    }
                }
            }, 
        },       
        'BOMBS': {
            "Riferimento Bomb": {
                "type": "Bombs",
                "model": "Riferimento Bomb",
                "users": ["USA", "UK", "Germany", "Italy", "Turkey", "Greece", "Israel", "Egypt", "Saudi Arabia", "Iran", "Pakistan"],
                "task": ["Strike", "Anti-ship Strike"],
                "start_service": 1950,
                "end_service": None,
                "cost": 4.4,
                "tnt": 429,
                "perc_efficiency_variability": 0.1,
                'efficiency': {
                    "Soft": {
                        "big": {"accuracy": 0.95, "destroy_capacity": 0.4},
                        "med": {"accuracy": 0.9, "destroy_capacity": 0.45},
                        "small": {"accuracy": 0.8, "destroy_capacity": 0.5},
                    },
                    "Armored": {
                        "big": {"accuracy": 0.85, "destroy_capacity": 0.95},
                        "med": {"accuracy": 0.75, "destroy_capacity": 1},
                        "small": {"accuracy": 0.7, "destroy_capacity": 1},
                    },
                    "Hard": {
                        "big": {"accuracy": 0.95, "destroy_capacity": 0.35},
                        "med": {"accuracy": 0.9, "destroy_capacity": 0.4},
                        "small": {"accuracy": 0.8, "destroy_capacity": 0.45},
                    },
                    "Structure": {
                        "big": {"accuracy": 0.95, "destroy_capacity": 0.005},
                        "med": {"accuracy": 0.9, "destroy_capacity": 0.02},
                        "small": {"accuracy": 0.8, "destroy_capacity": 0.1},
                    },
                    "Air_Defense": {
                        "big": {"accuracy": 0.85, "destroy_capacity": 0.95},
                        "med": {"accuracy": 0.75, "destroy_capacity": 1},
                        "small": {"accuracy": 0.7, "destroy_capacity": 1},
                    },
                    "Airbase": {
                        "big": {"accuracy": 0.9, "destroy_capacity": sys.float_info.min},
                        "med": {"accuracy": 0.9, "destroy_capacity": sys.float_info.min},
                        "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                    },
                    "Port": {
                        "big": {"accuracy": 0.9, "destroy_capacity": sys.float_info.min},
                        "med": {"accuracy": 0.9, "destroy_capacity": sys.float_info.min},
                        "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                    },
                    "Shipyard": {
                        "big": {"accuracy": 0.9, "destroy_capacity": sys.float_info.min},
                        "med": {"accuracy": 0.9, "destroy_capacity": sys.float_info.min},
                        "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                    },
                    "Farp": {
                        "big": {"accuracy": 0.9, "destroy_capacity": sys.float_info.min},
                        "med": {"accuracy": 0.9, "destroy_capacity": sys.float_info.min},
                        "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                    },
                    "Stronghold": {
                        "big": {"accuracy": 0.9, "destroy_capacity": sys.float_info.min},
                        "med": {"accuracy": 0.9, "destroy_capacity": sys.float_info.min},
                        "small": {"accuracy": 0.9, "destroy_capacity": 1e-8},
                    },
                    "ship": {
                        "big": {"accuracy": 0.7, "destroy_capacity": 0.42},
                        "med": {"accuracy": 0.5, "destroy_capacity": 0.5},
                        "small": {"accuracy": 0.3, "destroy_capacity": 0.5},
                    },
                    "SAM": {
                        "big": {"accuracy": 1, "destroy_capacity": 0.8},
                        "med": {"accuracy": 1, "destroy_capacity": 0.9},
                        "small": {"accuracy": 0.9, "destroy_capacity": 1}
                    }
                }
            },            
            "Mk-84": {
                "type": "Bombs",
                "task": ["Strike", "Anti-ship Strike"],
                "start_service": 1950,
                "end_service": None,
                "cost": 4.4,
                "tnt": 429,
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "Structure": {
                        "big": {"accuracy": 1, "destroy_capacity": 0.8},
                        "med": {"accuracy": 0.9, "destroy_capacity": 0.9},
                        "small": {"accuracy": 0.8, "destroy_capacity": 1}
                    },
                    "Bridge": {
                        "big": {"accuracy": 1, "destroy_capacity": 0.7},
                        "med": {"accuracy": 0.9, "destroy_capacity": 0.8},
                        "small": {"accuracy": 0.8, "destroy_capacity": 0.9}
                    },
                    "ship": {
                        "big": {"accuracy": 0.5, "destroy_capacity": 0.85},
                        "med": {"accuracy": 0.4, "destroy_capacity": 1},
                        "small": {"accuracy": 0.2, "destroy_capacity": 1}
                    },
                    "soft": {
                        "med": {"accuracy": 0.8, "destroy_capacity": 0.85},
                        "small": {"accuracy": 0.7, "destroy_capacity": 0.95}
                    },
                    "SAM": {
                        "med": {"accuracy": 0.85, "destroy_capacity": 1},
                        "small": {"accuracy": 0.8, "destroy_capacity": 1}
                    },
                    "armor": {
                        "med": {"accuracy": 0.85, "destroy_capacity": 1},
                        "small": {"accuracy": 0.8, "destroy_capacity": 1}
                    }
                }
            },
            "Mk-83": {
                "type": "Bombs",
                "task": ["Strike", "Anti-ship Strike"],
                "start_service": 1950,
                "end_service": None,
                "cost": 3.3,
                "tnt": 202,
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "Structure": {
                        "big": {"accuracy": 1, "destroy_capacity": 0.4},
                        "med": {"accuracy": 0.9, "destroy_capacity": 0.45},
                        "small": {"accuracy": 0.8, "destroy_capacity": 0.5}
                    },
                    "Bridge": {
                        "big": {"accuracy": 1, "destroy_capacity": 0.35},
                        "med": {"accuracy": 0.9, "destroy_capacity": 0.4},
                        "small": {"accuracy": 0.8, "destroy_capacity": 0.45}
                    },
                    "ship": {
                        "big": {"accuracy": 0.7, "destroy_capacity": 0.42},
                        "med": {"accuracy": 0.5, "destroy_capacity": 0.5},
                        "small": {"accuracy": 0.3, "destroy_capacity": 0.5}
                    },
                    "soft": {
                        "med": {"accuracy": 0.9, "destroy_capacity": 0.95},
                        "small": {"accuracy": 0.9, "destroy_capacity": 1}
                    },
                    "armor": {
                        "big": {"accuracy": 0.85, "destroy_capacity": 0.95},
                        "med": {"accuracy": 0.75, "destroy_capacity": 1},
                        "small": {"accuracy": 0.7, "destroy_capacity": 1}
                    },
                    "SAM": {
                        "big": {"accuracy": 0.85, "destroy_capacity": 0.95},
                        "med": {"accuracy": 0.75, "destroy_capacity": 1},
                        "small": {"accuracy": 0.7, "destroy_capacity": 1}
                    }
                }
            },
            "Mk-82": {
                "type": "Bombs",
                "task": ["Strike", "Anti-ship Strike"],
                "start_service": 1950,
                "end_service": None,
                "cost": 2.7,
                "tnt": 92,
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "Structure": {
                        "big": {"accuracy": 1, "destroy_capacity": 0.13},
                        "med": {"accuracy": 0.9, "destroy_capacity": 0.21},
                        "small": {"accuracy": 0.8, "destroy_capacity": 0.52}
                    },
                    "Bridge": {
                        "med": {"accuracy": 0.9, "destroy_capacity": 0.21},
                        "small": {"accuracy": 0.8, "destroy_capacity": 0.31}
                    },
                    "ship": {
                        "big": {"accuracy": 0.7, "destroy_capacity": 0.21},
                        "med": {"accuracy": 0.5, "destroy_capacity": 0.25},
                        "small": {"accuracy": 0.3, "destroy_capacity": 0.33}
                    },
                    "soft": {
                        "med": {"accuracy": 0.8, "destroy_capacity": 0.85},
                        "small": {"accuracy": 0.7, "destroy_capacity": 0.95}
                    },
                    "SAM": {
                        "big": {"accuracy": 0.9, "destroy_capacity": 0.69},
                        "med": {"accuracy": 0.85, "destroy_capacity": 0.74},
                        "small": {"accuracy": 0.75, "destroy_capacity": 0.79}
                    },
                    "armor": {
                        "big": {"accuracy": 0.9, "destroy_capacity": 0.39},
                        "med": {"accuracy": 0.85, "destroy_capacity": 0.44},
                        "small": {"accuracy": 0.75, "destroy_capacity": 0.49}
                    }
                }
            },
            "Mk-82AIR": {
                "type": "Bombs",
                "task": ["Strike", "Anti-ship Strike"],
                "start_service": 1950,
                "end_service": None,
                "cost": 4,
                "tnt": 92,
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "Structure": {
                        "big": {"accuracy": 1, "destroy_capacity": 0.13},
                        "med": {"accuracy": 0.9, "destroy_capacity": 0.21},
                        "small": {"accuracy": 0.8, "destroy_capacity": 0.52}
                    },
                    "Bridge": {
                        "med": {"accuracy": 0.9, "destroy_capacity": 0.21},
                        "small": {"accuracy": 0.8, "destroy_capacity": 0.31}
                    },
                    "ship": {
                        "big": {"accuracy": 0.7, "destroy_capacity": 0.21},
                        "med": {"accuracy": 0.5, "destroy_capacity": 0.25},
                        "small": {"accuracy": 0.3, "destroy_capacity": 0.33}
                    },
                    "soft": {
                        "med": {"accuracy": 0.8, "destroy_capacity": 0.85},
                        "small": {"accuracy": 0.7, "destroy_capacity": 0.95}
                    },
                    "SAM": {
                        "big": {"accuracy": 0.9, "destroy_capacity": 0.69},
                        "med": {"accuracy": 0.85, "destroy_capacity": 0.74},
                        "small": {"accuracy": 0.75, "destroy_capacity": 0.79}
                    },
                    "armor": {
                        "big": {"accuracy": 0.9, "destroy_capacity": 0.39},
                        "med": {"accuracy": 0.85, "destroy_capacity": 0.44},
                        "small": {"accuracy": 0.75, "destroy_capacity": 0.49}
                    }
                }
            },
            "GBU-10": {
                "type": "Guided bombs",
                "task": ["Strike", "Anti-ship Strike"],
                "start_service": 1980,
                "end_service": None,
                "cost": 27,
                "tnt": 428,
                "perc_efficiency_variability": 0.05,
                "efficiency": {
                    "Structure": {
                        "big": {"accuracy": 1, "destroy_capacity": 0.8},
                        "med": {"accuracy": 1, "destroy_capacity": 0.9},
                        "small": {"accuracy": 0.95, "destroy_capacity": 1}
                    },
                    "Bridge": {
                        "big": {"accuracy": 1, "destroy_capacity": 0.7},
                        "med": {"accuracy": 1, "destroy_capacity": 0.8},
                        "small": {"accuracy": 0.9, "destroy_capacity": 0.9}
                    },
                    "ship": {
                        "big": {"accuracy": 0.7, "destroy_capacity": 0.85},
                        "med": {"accuracy": 0.6, "destroy_capacity": 1},
                        "small": {"accuracy": 0.4, "destroy_capacity": 1}
                    }
                }
            },
            "GBU-16": {
                "type": "Guided bombs",
                "task": ["Strike", "Anti-ship Strike"],
                "start_service": 1970,
                "end_service": None,
                "cost": 25,
                "tnt": 202,
                "perc_efficiency_variability": 0.05,
                "efficiency": {
                    "Structure": {
                        "big": {"accuracy": 1, "destroy_capacity": 0.4},
                        "med": {"accuracy": 1, "destroy_capacity": 0.45},
                        "small": {"accuracy": 0.95, "destroy_capacity": 0.5}
                    },
                    "Bridge": {
                        "big": {"accuracy": 1, "destroy_capacity": 0.35},
                        "med": {"accuracy": 1, "destroy_capacity": 0.4},
                        "small": {"accuracy": 0.9, "destroy_capacity": 0.45}
                    },
                    "ship": {
                        "big": {"accuracy": 0.8, "destroy_capacity": 0.42},
                        "med": {"accuracy": 0.7, "destroy_capacity": 0.5},
                        "small": {"accuracy": 0.5, "destroy_capacity": 0.5}
                    }
                }
            },
            "GBU-12": {
                "type": "Guided bombs",
                "task": ["Strike"],
                "start_service": 1970,
                "end_service": None,
                "cost": 22,
                "tnt": 90,
                "perc_efficiency_variability": 0.05,
                "efficiency": {
                    "Structure": {
                        "med": {"accuracy": 1, "destroy_capacity": 0.21},
                        "small": {"accuracy": 0.95, "destroy_capacity": 0.25}
                    },
                    "ship": {
                        "big": {"accuracy": 0.8, "destroy_capacity": 0.21},
                        "med": {"accuracy": 0.7, "destroy_capacity": 0.25},
                        "small": {"accuracy": 0.5, "destroy_capacity": 0.25}
                    }
                }
            },        
            "GBU-24": {  # like Mk-84
                "type": "Guided bombs",
                "task": ["Strike"],
                "start_service": 1983,
                "end_service": None,
                "cost": 55,  # k$
                "tnt": 429,  # kg
                "perc_efficiency_variability": 0.05,  # percentage of efficiency variability 0-1 (100%)
                "efficiency": {
                    "Structure": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "big": {
                            "accuracy": 1,  # 1 max, 0.1 min ( hit success percentage )
                            "destroy_capacity": 0.8,  # 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )
                        },
                        "med": {
                            "accuracy": 0.9,
                            "destroy_capacity": 0.9,
                        },
                        "small": {
                            "accuracy": 0.8,
                            "destroy_capacity": 1,
                        }
                    },
                    "Bridge": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "big": {
                            "accuracy": 1,
                            "destroy_capacity": 0.7,
                        },
                        "med": {
                            "accuracy": 0.9,
                            "destroy_capacity": 0.8,
                        },
                        "small": {
                            "accuracy": 0.8,
                            "destroy_capacity": 0.9,
                        }
                    },
                    "ship": {  # mobile target
                        "big": {
                            "accuracy": 0.5,
                            "destroy_capacity": 0.85,
                        },
                        "med": {
                            "accuracy": 0.4,
                            "destroy_capacity": 1,
                        },
                        "small": {
                            "accuracy": 0.2,
                            "destroy_capacity": 1,
                        }
                    },
                },
            },
            "GBU-27": {  # bunker
                "type": "Guided bombs",
                "task": ["Strike"],
                "start_service": 1985,
                "end_service": None,
                "cost": 55,  # k$
                "tnt": 429,  # kg
                "perc_efficiency_variability": 0.05,  # percentage of efficiency variability 0-1 (100%)
                "efficiency": {
                    "Structure": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "big": {
                            "accuracy": 1,  # 1 max, 0.1 min ( hit success percentage )
                            "destroy_capacity": 0.8,  # 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )
                        },
                        "med": {
                            "accuracy": 0.9,
                            "destroy_capacity": 0.9,
                        },
                        "small": {
                            "accuracy": 0.8,
                            "destroy_capacity": 1,
                        }
                    },
                    "Bridge": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "big": {
                            "accuracy": 1,
                            "destroy_capacity": 0.7,
                        },
                        "med": {
                            "accuracy": 0.9,
                            "destroy_capacity": 0.8,
                        },
                        "small": {
                            "accuracy": 0.8,
                            "destroy_capacity": 0.9,
                        }
                    },
                    "ship": {  # mobile target
                        "big": {
                            "accuracy": 0.5,
                            "destroy_capacity": 0.85,
                        },
                        "med": {
                            "accuracy": 0.4,
                            "destroy_capacity": 1,
                        },
                        "small": {
                            "accuracy": 0.2,
                            "destroy_capacity": 1,
                        }
                    },
                },
            },
            "Mk-20": {  # aka CBU-100 anti-armor cluster
                "type": "Cluster bombs",
                "task": ["Strike"],
                "start_service": 1970,
                "end_service": None,
                "cost": 15,  # k$
                "weight": 222,  # kg
                "perc_efficiency_variability": 0.1,  # percentage of efficiency variability 0-1 (100%)
                "efficiency": {
                    "SAM": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "big": {
                            "accuracy": 0.75,  # 1 max, 0.1 min ( hit success percentage )
                            "destroy_capacity": 2,  # element destroyed (single hit), 0.1 min ( element destroy capacity )
                        },
                        "med": {
                            "accuracy": 0.7,
                            "destroy_capacity": 5,
                        },
                        "small": {
                            "accuracy": 0.65,
                            "destroy_capacity": 7,
                        }
                    },
                    "soft": {  # mobile target(artillery group)
                        "big": {
                            "accuracy": 0.75,
                            "destroy_capacity": 3,
                        },
                        "med": {
                            "accuracy": 0.7,
                            "destroy_capacity": 5,
                        },
                        "small": {
                            "accuracy": 0.65,
                            "destroy_capacity": 7,
                        }
                    },
                    "armor": {  # mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                        "big": {
                            "accuracy": 0.75,
                            "destroy_capacity": 3,
                        },
                        "med": {
                            "accuracy": 0.7,
                            "destroy_capacity": 5,
                        },
                        "small": {
                            "accuracy": 0.65,
                            "destroy_capacity": 7,
                        }
                    },
                },
            },
            "BLG66": {  # aka Belouga cluster soft target
                "type": "Cluster bombs",
                "task": ["Strike"],
                "start_service": 1980,
                "end_service": None,
                "cost": 15,  # k$
                "weight": 305,  # kg
                "perc_efficiency_variability": 0.1,  # percentage of efficiency variability 0-1 (100%)
                "efficiency": {
                    "SAM": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "big": {
                            "accuracy": 0.75,  # 1 max, 0.1 min ( hit success percentage )
                            "destroy_capacity": 2.1,  # element destroyed (single hit), 0.1 min ( element destroy capacity )
                        },
                        "med": {
                            "accuracy": 0.7,
                            "destroy_capacity": 3.2,
                        },
                        "small": {
                            "accuracy": 0.65,
                            "destroy_capacity": 4.5,
                        }
                    },
                    "soft": {  # mobile target(artillery group)
                        "big": {
                            "accuracy": 0.7,
                            "destroy_capacity": 2.7,
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 4.5,
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 6.5,
                        }
                    },
                    "armor": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "big": {
                            "accuracy": 0.75,  # 1 max, 0.1 min ( hit success percentage )
                            "destroy_capacity": 1,  # element destroyed (single hit), 0.1 min ( element destroy capacity )
                        },
                        "med": {
                            "accuracy": 0.7,
                            "destroy_capacity": 1.5,
                        },
                        "small": {
                            "accuracy": 0.65,
                            "destroy_capacity": 2,
                        }
                    },
                },
            },
            "CBU-52B": {  # aka cluster soft target
                "type": "Cluster bombs",
                "task": ["Strike"],
                "start_service": 1970,
                "end_service": None,
                "cost": 17,  # k$
                "weight": 347,  # kg
                "perc_efficiency_variability": 0.1,  # percentage of efficiency variability 0-1 (100%)
                "efficiency": {
                    "SAM": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "big": {
                            "accuracy": 0.75,  # 1 max, 0.1 min ( hit success percentage )
                            "destroy_capacity": 2.5,  # element destroyed (single hit), 0.1 min ( element destroy capacity )
                        },
                        "med": {
                            "accuracy": 0.7,
                            "destroy_capacity": 3.7,
                        },
                        "small": {
                            "accuracy": 0.65,
                            "destroy_capacity": 5,
                        }
                    },
                    "soft": {  # mobile target(artillery group)
                        "big": {
                            "accuracy": 0.7,
                            "destroy_capacity": 3,
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 5,
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 7,
                        }
                    },
                },
            },
            "BK-90MJ1": {  # aka DWS 39 Mjölner MJ1 soft target, mj2 anti-armor, mj1+2 both, cluster bomb
                "type": "Cluster bombs",
                "task": ["Strike"],
                "start_service": 1990,
                "end_service": None,
                "cost": 15,  # k$
                "weight": None,  # kg
                "perc_efficiency_variability": 0.1,  # percentage of efficiency variability 0-1 (100%)
                "efficiency": {
                    "SAM": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "big": {
                            "accuracy": 0.7,  # 1 max, 0.1 min ( hit success percentage )
                            "destroy_capacity": 2,  # element destroyed (single hit), 0.1 min ( element destroy capacity )
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 3,
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 4,
                        }
                    },
                    "armor": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "big": {
                            "accuracy": 0.7,  # 1 max, 0.1 min ( hit success percentage )
                            "destroy_capacity": 2,  # element destroyed (single hit), 0.1 min ( element destroy capacity )
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 3,
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 4,
                        }
                    },
                    "soft": {  # mobile target(artillery group)
                        "big": {
                            "accuracy": 0.7,
                            "destroy_capacity": 3,
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 5,
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 7,
                        }
                    },
                },
            },
            "BK-90MJ1-2": {  # aka DWS 39 Mjölner MJ1 soft target, mj2 anti-armor, mj1+2 both, cluster bomb
                "type": "Cluster bombs",
                "task": ["Strike"],
                "start_service": 1990,
                "end_service": None,
                "cost": 15,  # k$
                "weight": None,  # kg
                "perc_efficiency_variability": 0.1,  # percentage of efficiency variability 0-1 (100%)
                "efficiency": {
                    "SAM": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "big": {
                            "accuracy": 0.7,  # 1 max, 0.1 min ( hit success percentage )
                            "destroy_capacity": 2,  # element destroyed (single hit), 0.1 min ( element destroy capacity )
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 3,
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 4,
                        }
                    },
                    "armor": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "big": {
                            "accuracy": 0.7,  # 1 max, 0.1 min ( hit success percentage )
                            "destroy_capacity": 3,  # element destroyed (single hit), 0.1 min ( element destroy capacity )
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 4,
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 5,
                        }
                    },
                    "soft": {  # mobile target(artillery group)
                        "big": {
                            "accuracy": 0.7,
                            "destroy_capacity": 3,
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 5,
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 7,
                        }
                    },
                },
            },
            "BK-90MJ2": {  # aka DWS 39 Mjölner MJ1 soft target, mj2 anti-armor, mj1+2 both, cluster bomb
                "type": "Cluster bombs",
                "task": ["Strike"],
                "start_service": 1990,
                "end_service": None,
                "cost": 15,  # k$
                "weight": None,  # kg
                "perc_efficiency_variability": 0.1,  # percentage of efficiency variability 0-1 (100%)
                "efficiency": {
                    "SAM": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "big": {
                            "accuracy": 0.7,  # 1 max, 0.1 min ( hit success percentage )
                            "destroy_capacity": 2,  # element destroyed (single hit), 0.1 min ( element destroy capacity )
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 3,
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 4,
                        }
                    },
                    "armor": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "big": {
                            "accuracy": 0.7,  # 1 max, 0.1 min ( hit success percentage )
                            "destroy_capacity": 3,  # element destroyed (single hit), 0.1 min ( element destroy capacity )
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 4,
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 5,
                        }
                    },
                    "soft": {  # mobile target(artillery group)
                        "big": {
                            "accuracy": 0.7,
                            "destroy_capacity": 3,
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 5,
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 7,
                        }
                    },
                },
            },
            "M/71": {  # HE Fragmentation bombs for AJS37 Viggen
                "type": "Bombs",
                "task": ["Strike", "Anti-ship Strike"],
                "start_service": 1970,
                "end_service": None,
                "cost": 2,  # k$
                "tnt": 40,  # kg
                "perc_efficiency_variability": 0.1,  # percentage of efficiency variability 0-1 (100%)
                "efficiency": {
                    "Structure": {  # fixed target (guided bombs and agm missile are more efficiency)
                    },
                    "ship": {  # mobile target
                        "big": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.07,
                        },
                        "med": {
                            "accuracy": 0.5,
                            "destroy_capacity": 0.12,
                        },
                        "small": {
                            "accuracy": 0.3,
                            "destroy_capacity": 0.25,
                        }
                    },
                    "soft": {  # mobile target(artillery group)
                        "big": {
                            "accuracy": 0.8,
                            "destroy_capacity": 0.9,
                        },
                        "med": {
                            "accuracy": 0.8,
                            "destroy_capacity": 1,
                        },
                        "small": {
                            "accuracy": 0.7,
                            "destroy_capacity": 1,
                        }
                    },
                    "armor": {  # mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                        "big": {
                            "accuracy": 0.8,
                            "destroy_capacity": 0.2,
                        },
                        "med": {
                            "accuracy": 0.8,
                            "destroy_capacity": 0.4,
                        },
                        "small": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.5,
                        }
                    }
                },
            },
            "SAMP-400LD": {  # SAMP-21 400 kg (Mk-83)
                "type": "Bombs",
                "task": ["Strike", "Anti-ship Strike"],
                "start_service": 1950,
                "end_service": None,
                "cost": 3.3,  # k$
                "tnt": 202,  # kg
                "perc_efficiency_variability": 0.1,  # percentage of efficiency variability 0-1 (100%)
                "efficiency": {
                    "Structure": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "big": {
                            "accuracy": 1,  # 1 max, 0.1 min ( hit success percentage )
                            "destroy_capacity": 0.4,  # 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )
                        },
                        "med": {
                            "accuracy": 0.9,
                            "destroy_capacity": 0.45,
                        },
                        "small": {
                            "accuracy": 0.8,
                            "destroy_capacity": 0.5,
                        }
                    },
                    "Bridge": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "big": {
                            "accuracy": 1,
                            "destroy_capacity": 0.35,
                        },
                        "med": {
                            "accuracy": 0.9,
                            "destroy_capacity": 0.4,
                        },
                        "small": {
                            "accuracy": 0.8,
                            "destroy_capacity": 0.45,
                        }
                    },
                    "ship": {  # mobile target
                        "big": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.42,
                        },
                        "med": {
                            "accuracy": 0.5,
                            "destroy_capacity": 0.5,
                        },
                        "small": {
                            "accuracy": 0.3,
                            "destroy_capacity": 0.5,
                        }
                    },
                    "soft": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "med": {
                            "accuracy": 0.9,
                            "destroy_capacity": 0.95,
                        },
                        "small": {
                            "accuracy": 0.9,
                            "destroy_capacity": 1,
                        }
                    },
                    "SAM": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "med": {
                            "accuracy": 0.85,
                            "destroy_capacity": 0.75,
                        },
                        "small": {
                            "accuracy": 0.75,
                            "destroy_capacity": 0.9,
                        }
                    },
                },
            },
            "SAMP-250HD": {  # SAMP-19 250 kg (Mk-82)
                "type": "Bombs",
                "task": ["Strike", "Anti-ship Strike"],
                "start_service": 1950,
                "end_service": None,
                "cost": 2.7,  # k$
                "tnt": 92,  # kg
                "perc_efficiency_variability": 0.1,  # percentage of efficiency variability 0-1 (100%)
                "efficiency": {
                    "Structure": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "med": {
                            "accuracy": 0.9,
                            "destroy_capacity": 0.21,
                        },
                        "small": {
                            "accuracy": 0.8,
                            "destroy_capacity": 0.52,
                        }
                    },
                    "ship": {  # mobile target
                        "big": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.21,
                        },
                        "med": {
                            "accuracy": 0.5,
                            "destroy_capacity": 0.25,
                        },
                        "small": {
                            "accuracy": 0.3,
                            "destroy_capacity": 0.25,
                        }
                    },
                    "soft": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "med": {
                            "accuracy": 0.8,
                            "destroy_capacity": 0.7,
                        },
                        "small": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.8,
                        }
                    },
                    "SAM": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "med": {
                            "accuracy": 0.8,
                            "destroy_capacity": 0.65,
                        },
                        "small": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.8,
                        }
                    },
                },
            },
        },
        'ROCKETS': {   
                "Zuni-Mk71": {  # Rockets 127 mm soft target
                    "type": "Rockets",
                    "task": ["Strike", "Anti-ship Strike"],
                    "start_service": 1956,
                    "end_service": None,
                    "cost": 0.4,  # k$
                    "tnt": 6.8,  # kg
                    "range": 8,  # Km
                    "perc_efficiency_variability": 0.1,  # percentage of efficiency variability 0-1 (100%)
                    "efficiency": {  # for single rocket
                        "Structure": {  # fixed target (guided bombs and agm missile are more efficiency)
                            "small": {
                                "accuracy": 0.6,
                                "destroy_capacity": 0.15,
                            },
                        },
                        "ship": {  # mobile target
                            "med": {
                                "accuracy": 0.7,
                                "destroy_capacity": 0.12,
                            },
                            "small": {
                                "accuracy": 0.5,
                                "destroy_capacity": 0.12,
                            }
                        },
                        "soft": {  # mobile target(artillery group)
                            "big": {
                                "accuracy": 0.7,
                                "destroy_capacity": 0.4,
                            },
                            "med": {
                                "accuracy": 0.6,
                                "destroy_capacity": 0.5,
                            },
                            "small": {
                                "accuracy": 0.5,
                                "destroy_capacity": 0.6,
                            }
                        },
                        "armor": {  # mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                            "big": {
                                "accuracy": 0.7,
                                "destroy_capacity": 0.3,
                            },
                            "med": {
                                "accuracy": 0.6,
                                "destroy_capacity": 0.4,
                            },
                            "small": {
                                "accuracy": 0.5,
                                "destroy_capacity": 0.6,
                            }
                        }
                    },
                },
                "Hydra-70MK5": {  # Rockets 70 mm Mk-5 hard target
                    "type": "Rockets",
                    "task": ["Strike", "Anti-ship Strike"],
                    "start_service": 1956,
                    "end_service": None,
                    "cost": 2.8,  # k$
                    "tnt": 6.2,  # kg ?? (not applicable?)
                    "range": 8,  # Km
                    "perc_efficiency_variability": 0.1,  # percentage of efficiecy variability 0-1 (100%)
                    "efficiency": {
                        "Structure": {  # fixed target (guided bombs and agm missile are more efficiency)
                            "small": {
                                "accuracy": 0.7,
                                "destroy_capacity": 0.15,
                            },
                        },
                        "ship": {  # mobile target
                            "med": {
                                "accuracy": 0.7,
                                "destroy_capacity": 0.1,
                            },
                            "small": {
                                "accuracy": 0.6,
                                "destroy_capacity": 0.15,
                            }
                        },
                        "soft": {  # mobile target(artillery group)
                            "big": {
                                "accuracy": 0.7,
                                "destroy_capacity": 0.3,
                            },
                            "med": {
                                "accuracy": 0.6,
                                "destroy_capacity": 0.4,
                            },
                            "small": {
                                "accuracy": 0.5,
                                "destroy_capacity": 0.6,
                            }
                        },
                        "armor": {  # mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                            "big": {
                                "accuracy": 0.7,
                                "destroy_capacity": 0.2,
                            },
                            "med": {
                                "accuracy": 0.6,
                                "destroy_capacity": 0.3,
                            },
                            "small": {
                                "accuracy": 0.5,
                                "destroy_capacity": 0.4,
                            }
                        }
                    },
                },
                "Hydra-70MK1": {  # Rockets 70 mm Mk-1 soft target
                    "type": "Rockets",
                    "task": ["Strike", "Anti-ship Strike"],
                    "start_service": 1956,
                    "end_service": None,
                    "cost": 2.8,  # k$
                    "tnt": 6.2,  # kg ?? (not applicable?)
                    "range": 8,  # Km
                    "perc_efficiency_variability": 0.1,  # percentage of efficiecy variability 0-1 (100%)
                    "efficiency": {
                        "Structure": {  # fixed target (guided bombs and agm missile are more efficiency)
                            "small": {
                                "accuracy": 0.7,
                                "destroy_capacity": 0.08,
                            },
                        },
                        "ship": {  # mobile target
                            "med": {
                                "accuracy": 0.7,
                                "destroy_capacity": 0.08,
                            },
                            "small": {
                                "accuracy": 0.6,
                                "destroy_capacity": 0.1,
                            }
                        },
                        "soft": {  # mobile target(artillery group)
                            "big": {
                                "accuracy": 0.7,
                                "destroy_capacity": 0.3,
                            },
                            "med": {
                                "accuracy": 0.6,
                                "destroy_capacity": 0.4,
                            },
                            "small": {
                                "accuracy": 0.5,
                                "destroy_capacity": 0.6,
                            }
                        }
                    },
                },
                "SNEB-256": {  # Rockets 68 mm HE_DEFR
                    "type": "Rockets",
                    "task": ["Strike", "Anti-ship Strike"],
                    "start_service": 1955,
                    "end_service": None,
                    "cost": 2.5,  # k$
                    "tnt": 6.8,  # kg ???
                    "range": 8,  # Km ??
                    "perc_efficiency_variability": 0.1,  # percentage of efficiecy variability 0-1 (100%)
                    "efficiency": {
                        "Structure": {  # fixed target (guided bombs and agm missile are more efficiency)
                            "small": {
                                "accuracy": 0.6,
                                "destroy_capacity": 0.15,
                            }
                        },
                        "ship": {  # mobile target
                            "med": {
                                "accuracy": 0.7,
                                "destroy_capacity": 0.12,
                            },
                            "small": {
                                "accuracy": 0.6,
                                "destroy_capacity": 0.2,
                            }
                        },
                        "soft": {  # mobile target(artillery group)
                            "big": {
                                "accuracy": 0.7,
                                "destroy_capacity": 0.3,
                            },
                            "med": {
                                "accuracy": 0.6,
                                "destroy_capacity": 0.4,
                            },
                            "small": {
                                "accuracy": 0.5,
                                "destroy_capacity": 0.5,
                            }
                        },
                        "armor": {  # mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                            "big": {
                                "accuracy": 0.7,
                                "destroy_capacity": 0.2,
                            },
                            "med": {
                                "accuracy": 0.6,
                                "destroy_capacity": 0.3,
                            },
                            "small": {
                                "accuracy": 0.5,
                                "destroy_capacity": 0.4,
                            }
                        }
                    },
                },
                "SNEB-253": {  # Rockets ? mm HE , aka Matra f1
                    "type": "Rockets",
                    "task": ["Strike", "Anti-ship Strike"],
                    "start_service": 1955,
                    "end_service": None,
                    "cost": 1.7,  # k$
                    "tnt": 3,  # kg ???
                    "range": 8,  # Km ??
                    "perc_efficiency_variability": 0.1,  # percentage of efficiecy variability 0-1 (100%)
                    "efficiency": {
                        "Structure": {  # fixed target (guided bombs and agm missile are more efficiency)
                            "small": {
                                "accuracy": 0.7,
                                "destroy_capacity": 0.07,
                            }
                        },
                        "ship": {  # mobile target
                            "small": {
                                "accuracy": 0.6,
                                "destroy_capacity": 0.08,
                            }
                        },
                        "soft": {  # mobile target(artillery group)
                            "big": {
                                "accuracy": 0.7,
                                "destroy_capacity": 0.3,
                            },
                            "med": {
                                "accuracy": 0.6,
                                "destroy_capacity": 0.4,
                            },
                            "small": {
                                "accuracy": 0.5,
                                "destroy_capacity": 0.5,
                            }
                        },
                        "armor": {  # mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                            "big": {
                                "accuracy": 0.7,
                                "destroy_capacity": 0.1,
                            },
                            "med": {
                                "accuracy": 0.6,
                                "destroy_capacity": 0.2,
                            },
                            "small": {
                                "accuracy": 0.5,
                                "destroy_capacity": 0.3,
                            }
                        }
                    },
                },
        },
    },
    'red': {
        'MISSILES_AAM': {

            "R-13M": {
                "type": "AAM",
                "model": "R-13M",
                "users": ["USSR", "Russia", "Poland", "East Germany", "Czechoslovakia", "Cuba", "North Korea", "Vietnam", "Syria", "Egypt", "Iraq", "India"],
                "seeker": "infrared",
                "task": ["A2A"],
                "start_service": 1974,
                "end_service": None,
                "cost": 70,  # k$
                "tnt": 5.5,  # kg
                "reliability": 0.6,
                "range": 15,  # km
                "max_height": 20,  # km
                "max_speed": 2.7,  # mach
                "manouvrability": 0.8,
                "accuracy": 0.55
            },
            
            "R-13M1": {
                "type": "AAM",
                "model": "R-13M1",
                "users": ["USSR", "Russia", "Poland", "East Germany", "Czechoslovakia", "Cuba", "North Korea", "Vietnam", "Syria", "Egypt", "Iraq", "India"],
                "seeker": "infrared",
                "task": ["A2A"],
                "start_service": 1975,  # 1976
                "end_service": None,
                "cost": 77,  # k$
                "tnt": 5.5,  # kg
                "reliability": 0.6,
                "range": 17,  # km
                "max_height": 20,  # km
                "max_speed": 2.4,  # mach
                "manouvrability": 0.8,
                "accuracy": 0.58
            },

            "R-60": {
                "type": "AAM",
                "model": "R-60",
                "users": ["USSR", "Russia", "Poland", "East Germany", "Czechoslovakia", "Cuba", "North Korea", "Vietnam", "Syria", "Egypt", "Iraq", "India", "Libya", "Algeria"],
                "seeker": "infrared",
                "task": ["A2A"],
                "start_service": 1974,
                "end_service": None,
                "cost": 50,  # k$
                "tnt": 3,  # kg
                "reliability": 0.6,
                "range": 8,  # km
                "max_height": 20,  # km
                "max_speed": 2.7,  # mach
                "manouvrability": 0.7,
                "accuracy": 0.6
            },

            "R-60M": {
                "type": "AAM",
                "model": "R-60M",
                "users": ["USSR", "Russia", "Poland", "East Germany", "Czechoslovakia", "Cuba", "North Korea", "Vietnam", "Syria", "Egypt", "Iraq", "India", "Libya", "Algeria"],
                "seeker": "infrared",
                "task": ["A2A"],
                "start_service": 1974,  # 1982?
                "end_service": None,
                "cost": 60,  # k$
                "tnt": 3,  # kg
                "reliability": 0.6,
                "range": 8,  # km
                "max_height": 20,  # km
                "max_speed": 2.7,  # mach
                "manouvrability": 0.7,
                "accuracy": 0.65
            },

            "R-73": {
                "type": "AAM",
                "model": "R-73",
                "users": ["USSR", "Russia", "India", "China", "Malaysia", "Algeria", "Syria", "Iran", "North Korea", "Vietnam", "Cuba"],
                "seeker": "infrared",
                "task": ["A2A"],
                "start_service": 1984,
                "end_service": None,
                "cost": 90,  # k$
                "tnt": 7,  # kg
                "reliability": 0.8,
                "range": 30,  # km
                "max_height": 20,  # km
                "max_speed": 2.7,  # mach
                "manouvrability": 0.85,
                "accuracy": 0.85
            },

            "R-3S": {  # aka K-13A
                "type": "AAM",
                "model": "R-3S",
                "users": ["USSR", "Russia", "China", "Poland", "East Germany", "Czechoslovakia", "Cuba", "North Korea", "Vietnam", "Syria", "Egypt", "Iraq", "India", "Libya", "Algeria"],
                "seeker": "infrared",
                "task": ["A2A"],
                "start_service": 1960,
                "end_service": None,
                "cost": 30,  # k$
                "tnt": 8.8,  # kg
                "reliability": 0.6,
                "range": 8,  # km
                "max_height": 20,  # km
                "max_speed": 2.85,  # mach
                "manouvrability": 0.7,
                "accuracy": 0.45
            },

            "R-3R": {
                "type": "AAM",
                "model": "R-3R",
                "users": ["USSR", "Russia", "Poland", "East Germany", "Czechoslovakia", "Cuba", "North Korea", "Vietnam", "Syria", "Egypt", "Iraq", "India"],
                "seeker": "radar",
                "task": ["A2A"],
                "start_service": 1966,
                "end_service": None,
                "cost": 30,  # k$
                "tnt": 8.8,  # kg
                "reliability": 0.6,
                "range": 8,  # km
                "semiactive_range": 8,  # km
                "max_height": 20,  # km
                "max_speed": 2.85,  # mach
                "manouvrability": 0.7,
                "accuracy": 0.5
            },
            
            "R-24R": {
                "type": "AAM",
                "model": "R-24R",
                "users": ["USSR", "Russia", "India", "Syria", "Libya", "Iraq", "Algeria"],
                "seeker": "radar",
                "task": ["A2A"],
                "start_service": 1975,
                "end_service": 1992,
                "cost": 125,  # k$
                "tnt": 35,  # kg
                "reliability": 0.6,
                "range": 50,  # km
                "semiactive_range": 50,  # km
                "max_height": 25,  # km
                "max_speed": 3.42,  # mach
                "manouvrability": 0.7,
                "accuracy": 0.65
            },
            
            "R-24T": {
                "type": "AAM",
                "model": "R-24T",
                "users": ["USSR", "Russia", "India", "Syria", "Libya", "Iraq", "Algeria"],
                "seeker": "infrared",
                "task": ["A2A"],
                "start_service": 1975,
                "end_service": 1992,
                "cost": 125,  # k$
                "tnt": 35,  # kg
                "reliability": 0.6,
                "range": 15,  # km
                "max_height": 25,  # km
                "max_speed": 3.42,  # mach
                "manouvrability": 0.7,
                "accuracy": 0.6
            },
            
            "R-40R": {
                "type": "AAM",
                "model": "R-40R",
                "users": ["USSR", "Russia", "Syria", "Libya", "Iraq", "Algeria", "North Korea"],
                "seeker": "radar",
                "task": ["A2A"],
                "start_service": 1972,
                "end_service": None,
                "cost": 200,  # k$
                "tnt": 70,  # kg
                "reliability": 0.6,
                "range": 50,  # km
                "semiactive_range": 50,  # km
                "max_height": 25,  # km
                "max_speed": 4.5,  # mach
                "manouvrability": 0.7,
                "accuracy": 0.6
            },
            
            "R-40T": {
                "type": "AAM",
                "model": "R-40T",
                "users": ["USSR", "Russia", "Syria", "Libya", "Iraq", "Algeria", "North Korea"],
                "seeker": "infrared",
                "task": ["A2A"],
                "start_service": 1972,
                "end_service": None,
                "cost": 180,  # k$
                "tnt": 70,  # kg
                "reliability": 0.6,
                "range": 30,  # km
                "max_height": 25,  # km
                "max_speed": 4.5,  # mach
                "manouvrability": 0.7,
                "accuracy": 0.55
            },
            
            "R-27R": {
                "type": "AAM",
                "model": "R-27R",
                "users": ["USSR", "Russia", "Ukraine", "India", "China", "Malaysia", "Algeria", "Syria", "Iran", "Vietnam"],
                "seeker": "radar",
                "task": ["A2A"],
                "start_service": 1983,
                "end_service": None,
                "cost": 230,  # k$
                "tnt": 39,  # kg
                "reliability": 0.6,
                "range": 50,  # km
                "semiactive_range": 50,  # km
                "max_height": 25,  # km
                "max_speed": 4.5,  # mach
                "manouvrability": 0.7,
                "accuracy": 0.7
            },

            "R-27T": {
                "type": "AAM",
                "model": "R-27T",
                "users": ["USSR", "Russia", "Ukraine", "India", "China", "Malaysia", "Algeria", "Syria", "Iran", "Vietnam"],
                "seeker": "infrared",
                "task": ["A2A"],
                "start_service": 1984,
                "end_service": None,
                "cost": 230,  # k$
                "tnt": 39,  # kg
                "reliability": 0.6,
                "range": 40,  # km
                "max_height": 25,  # km
                "max_speed": 4.5,  # mach
                "manouvrability": 0.7,
                "accuracy": 0.65
            },
            
            "R-27ER": {
                "type": "AAM",
                "model": "R-27ER",
                "users": ["USSR", "Russia", "Ukraine", "India", "China", "Malaysia", "Algeria", "Syria", "Iran", "Vietnam"],
                "seeker": "radar",
                "task": ["A2A"],
                "start_service": 1983,
                "end_service": None,
                "cost": 230,  # k$
                "tnt": 39,  # kg
                "reliability": 0.6,
                "range": 120,  # km
                "semiactive_range": 50,  # km
                "max_height": 25,  # km
                "max_speed": 4.5,  # mach
                "manouvrability": 0.7,
                "accuracy": 0.72
            },
            
            "R-27ET": {
                "type": "AAM",
                "model": "R-27ET",
                "users": ["USSR", "Russia", "Ukraine", "India", "China", "Malaysia", "Algeria", "Syria", "Iran", "Vietnam"],
                "seeker": "infrared",
                "task": ["A2A"],
                "start_service": 1984,
                "end_service": None,
                "cost": 230,  # k$
                "tnt": 39,  # kg
                "reliability": 0.6,
                "range": 130,  # km
                "max_height": 25,  # km
                "max_speed": 4.5,  # mach
                "manouvrability": 0.7,
                "accuracy": 0.68
            },
        },        
        'MISSILES_ASM':{
            "9M120-F": {
                "type": "ASM",
                "model": "9M120-F",
                "users": ["Russia", "Belarus", "Kazakhstan", "Algeria"],
                "task": ["Strike", "Anti-ship Strike"],
                "start_service": 1980,
                "end_service": None,
                "cost": 50,  # k$
                "tnt": 7.4,  # kg
                "range": 6,  # Km
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "Structure": {
                    },
                    "ship": {
                        "med": {
                            "accuracy": 0.8,
                            "destroy_capacity": 0.1,
                        },
                        "small": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.15,
                        }
                    },
                    "soft": {
                        "big": {
                            "accuracy": 0.8,
                            "destroy_capacity": 0.4,
                        },
                        "med": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.5,
                        },
                        "small": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.6,
                        }
                    },
                    "armor": {
                        "big": {
                            "accuracy": 0.8,
                            "destroy_capacity": 0.1,
                        },
                        "med": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.2,
                        },
                        "small": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.3,
                        }
                    }
                },
            },
            "9M120": {
                "type": "ASM",
                "model": "9M120",
                "users": ["Russia", "Belarus", "Kazakhstan", "Algeria", "Syria"],
                "task": ["Strike", "Anti-ship Strike"],
                "start_service": 1980,
                "end_service": None,
                "cost": 50,  # k$
                "tnt": 7.4,  # kg
                "range": 6,  # Km
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "Structure": {
                    },
                    "ship": {
                        "med": {
                            "accuracy": 0.8,
                            "destroy_capacity": 0.1,
                        },
                        "small": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.15,
                        }
                    },
                    "soft": {
                        "big": {
                            "accuracy": 0.8,
                            "destroy_capacity": 0.4,
                        },
                        "med": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.5,
                        },
                        "small": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.6,
                        }
                    },
                    "armor": {
                        "big": {
                            "accuracy": 0.8,
                            "destroy_capacity": 0.35,
                        },
                        "med": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.45,
                        },
                        "small": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.55,
                        }
                    }
                },
            },

            "9M114": {
                "type": "ASM",
                "model": "9M114",
                "users": ["USSR", "Russia", "India", "Syria", "Iraq", "Libya", "Algeria"],
                "task": ["Strike", "Anti-ship Strike"],
                "start_service": 1975,
                "end_service": None,
                "cost": 35,  # k$
                "tnt": 5,  # kg
                "range": 7,  # Km
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "Structure": {
                    },
                    "ship": {
                        "med": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.1,
                        },
                        "small": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.15,
                        }
                    },
                    "soft": {
                        "big": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.4,
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.5,
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 0.6,
                        }
                    },
                    "armor": {
                        "big": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.3,
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.4,
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 0.6,
                        }
                    }
                },
            },

            "Hot-3": {
            "type": "ASM",
            "model": "Hot-3",
            "users": ["France", "Germany", "Egypt", "Iraq", "Saudi Arabia", "UAE", "Syria"],
                "task": ["Strike", "Anti-ship Strike"],
                "start_service": 1978,
                "end_service": None,
                "cost": 35,  # k$
                "tnt": 6,  # kg
                "range": 4,  # Km
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "Structure": {
                    },
                    "ship": {
                        "med": {
                            "accuracy": 0.85,
                            "destroy_capacity": 0.15,
                        },
                        "small": {
                            "accuracy": 0.8,
                            "destroy_capacity": 0.2,
                        }
                    },
                    "soft": {
                        "big": {
                            "accuracy": 0.9,
                            "destroy_capacity": 0.6,
                        },
                        "med": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.7,
                        },
                        "small": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.9,
                        }
                    },
                    "armor": {
                        "big": {
                            "accuracy": 0.9,
                            "destroy_capacity": 0.45,
                        },
                        "med": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.6,
                        },
                        "small": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.8,
                        }
                    }
                },
            },

            "Mistral": {
            "type": "ASM",
            "model": "Mistral",
            "users": ["France", "Belgium", "Brazil", "Chile", "Cyprus", "Egypt", "Finland", "Indonesia", "South Korea", "Norway", "Singapore"],
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1985,
            "end_service": None,
            "cost": 40,  # k$
            "tnt": 3,  # kg
            "range": 6,  # Km
            "perc_efficiency_variability": 0.1,
            "efficiency": {
                "Structure": {
                },
                "ship": {
                    "small": {
                        "accuracy": 0.8,
                        "destroy_capacity": 0.1,
                    }
                },
                "soft": {
                    "big": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.3,
                    },
                    "med": {
                        "accuracy": 0.7,
                        "destroy_capacity": 0.37,
                    },
                    "small": {
                        "accuracy": 0.6,
                        "destroy_capacity": 0.4,
                    }
                },
                "armor": {
                    "big": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.25,
                    },
                    "med": {
                        "accuracy": 0.7,
                        "destroy_capacity": 0.3,
                    },
                    "small": {
                        "accuracy": 0.6,
                        "destroy_capacity": 0.4,
                    }
                }
            },
            },
                    
        "Kh-22N": {  # radar antiship
            "type": "ASM",
            "model": "Kh-22N",
            "users": ["USSR", "Russia", "Ukraine"],
            "task": ["Anti-ship Strike"],
            "start_service": 1967,
            "end_service": None,
            "cost": 1000,  # k$
            "tnt": 1000,  # kg
            "range": 330,
            "perc_efficiency_variability": 0.05,  # efficiecy variability 0-1 (100%)
            "efficiency": {
                "ship": {  # mobile target
                    "big": {
                        "accuracy": 1,
                        "destroy_capacity": 1,
                    },
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 1,
                    },
                    "small": {
                        "accuracy": 0.95,
                        "destroy_capacity": 1,
                    }
                },
            },
        },
        
        "Kh-58": {  # antiradiation
            "type": "ASM",
            "model": "Kh-58",
            "users": ["USSR", "Russia", "India", "Syria", "Libya", "Iraq", "Algeria"],
            "task": ["SEAD"],
            "start_service": 1975,  # 1978 --1982 vers. U
            "end_service": None,
            "cost": 700,  # k$
            "tnt": 149,  # kg
            "range": 250,
            "perc_efficiency_variability": 0.2,  # efficiecy variability(0-1): firepower_max = firepower_max * ( 1 + perc_efficiency_variability )
            "efficiency": {
                "SAM": {
                    "big": {
                        "accuracy": 0.7,
                        "destroy_capacity": 0.9,
                    },
                    "med": {
                        "accuracy": 0.7,
                        "destroy_capacity": 1,
                    },
                    "small": {
                        "accuracy": 0.6,
                        "destroy_capacity": 1,
                    }
                },
            },
        },
        
        "Kh-66": {  # radar
            "type": "ASM",
            "model": "Kh-66",
            "users": ["USSR", "Russia", "Syria", "Libya", "Iraq", "Egypt"],
            "task": ["Anti-ship Strike", "Strike", "SEAD"],
            "start_service": 1967,
            "end_service": None,
            "cost": 200,  # k$
            "tnt": 111,  # kg
            "range": 10,  # Km
            "perc_efficiency_variability": 0.05,  # efficiecy variability 0-1 (100%)
            "efficiency": {
                "Structure": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 1,  # 1 max, 0.1 min ( hit success percentage )
                        "destroy_capacity": 0.15,  # 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )
                    },
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.22,
                    },
                    "small": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.53,
                    }
                },
                "Bridge": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.22,
                    },
                    "small": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.33,
                    }
                },
                "ship": {  # mobile target
                    "big": {
                        "accuracy": 1,
                        "destroy_capacity": 0.7,
                    },
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.8,
                    },
                    "small": {
                        "accuracy": 0.8,
                        "destroy_capacity": 1,
                    }
                },
                "soft": {  # mobile target(artillery group)
                    "big": {
                        "accuracy": 0.8,
                        "destroy_capacity": 1,
                    },
                    "med": {
                        "accuracy": 0.7,
                        "destroy_capacity": 1,
                    },
                    "small": {
                        "accuracy": 0.7,
                        "destroy_capacity": 1,
                    }
                },
                "armor": {  # mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    "big": {
                        "accuracy": 0.8,
                        "destroy_capacity": 0.8,
                    },
                    "med": {
                        "accuracy": 0.7,
                        "destroy_capacity": 0.9,
                    },
                    "small": {
                        "accuracy": 0.7,
                        "destroy_capacity": 1,
                    }
                },
                "SAM": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 0.8,
                        "destroy_capacity": 0.8,
                    },
                    "med": {
                        "accuracy": 0.8,
                        "destroy_capacity": 0.9,
                    },
                    "small": {
                        "accuracy": 0.7,
                        "destroy_capacity": 1,
                    }
                },
            },
        },
        
        "Kh-59": {  # TV guided, vers. M -> 1990
            "type": "ASM",
            "model": "Kh-59",
            "users": ["USSR", "Russia", "India", "China", "Algeria"],
            "task": ["Anti-ship Strike", "Strike", "SEAD"],
            "start_service": 1980,
            "end_service": None,
            "cost": 600,  # k$
            "tnt": 142,  # kg
            "range": 90,  # Km
            "perc_efficiency_variability": 0.05,  # efficiecy variability 0-1 (100%)
            "efficiency": {
                "Structure": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 1,  # 1 max, 0.1 min ( hit success percentage )
                        "destroy_capacity": 0.3,  # 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )
                    },
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.4,
                    },
                    "small": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.7,
                    }
                },
                "Bridge": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.3,
                    },
                    "small": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.5,
                    }
                },
                "ship": {  # mobile target
                    "big": {
                        "accuracy": 1,
                        "destroy_capacity": 0.4,
                    },
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.6,
                    },
                    "small": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.8,
                    }
                },
                "soft": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.95,
                    },
                    "small": {
                        "accuracy": 0.9,
                        "destroy_capacity": 1,
                    }
                },
                "armor": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 1,
                        "destroy_capacity": 0.65,
                    },
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.7,
                    },
                    "small": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.75,
                    }
                },
                "SAM": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 1,
                        "destroy_capacity": 0.7,
                    },
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.75,
                    },
                    "small": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.8,
                    }
                },
            },
        },
    
        "Kh-25ML": {  # laser guided
            "type": "ASM",
            "model": "Kh-25ML",
            "users": ["USSR", "Russia", "India", "Syria", "Iraq", "Libya", "Algeria", "Vietnam"],
            "task": ["Anti-ship Strike", "Strike", "SEAD"],
            "start_service": 1975,
            "end_service": None,
            "cost": 160,  # k$
            "tnt": 90,  # kg
            "range": 11,  # Km
            "perc_efficiency_variability": 0.05,  # efficiency variability 0-1 (100%)
            "efficiency": {
                "Structure": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 1,  # 1 max, 0.1 min (hit success percentage)
                        "destroy_capacity": 0.15,  # 1 max: element destroyed (single hit), 0.1 min (element destroy capacity)
                    },
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.22,
                    },
                    "small": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.53,
                    }
                },
                "Bridge": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.22,
                    },
                    "small": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.33,
                    }
                },
                "ship": {  # mobile target
                    "big": {
                        "accuracy": 1,
                        "destroy_capacity": 0.22,
                    },
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.27,
                    },
                    "small": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.35,
                    }
                },
                "soft": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.85,
                    },
                    "small": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.95,
                    }
                },
                "armor": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 1,
                        "destroy_capacity": 0.65,
                    },
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.7,
                    },
                    "small": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.75,
                    }
                },
                "SAM": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 1,
                        "destroy_capacity": 0.7,
                    },
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.75,
                    },
                    "small": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.8,
                    }
                },
            },
        },

        "Kh-25MR": {  # radar guided
            "type": "ASM",
            "model": "Kh-25MR",
            "users": ["USSR", "Russia", "India", "Syria", "Iraq", "Libya", "Algeria"],
            "task": ["Anti-ship Strike", "Strike", "SEAD"],
            "start_service": 1975,
            "end_service": None,
            "cost": 160,  # k$
            "tnt": 140,  # kg
            "range": 11,  # Km
            "perc_efficiency_variability": 0.05,  # efficiency variability 0-1 (100%)
            "efficiency": {
                "Structure": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 1,
                        "destroy_capacity": 0.22,
                    },
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.35,
                    },
                    "small": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.78,
                    }
                },
                "Bridge": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.35,
                    },
                    "small": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.45,
                    }
                },
                "ship": {  # mobile target
                    "big": {
                        "accuracy": 1,
                        "destroy_capacity": 0.33,
                    },
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.44,
                    },
                    "small": {
                        "accuracy": 0.9,
                        "destroy_capacity": 0.52,
                    }
                },
                "soft": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 1,
                    },
                    "small": {
                        "accuracy": 0.9,
                        "destroy_capacity": 1,
                    }
                },
                "armor": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 1,
                        "destroy_capacity": 0.9,
                    },
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 1,
                    },
                    "small": {
                        "accuracy": 0.9,
                        "destroy_capacity": 1,
                    }
                },
                "SAM": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 1,
                        "destroy_capacity": 0.9,
                    },
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 1,
                    },
                    "small": {
                        "accuracy": 0.9,
                        "destroy_capacity": 1,
                    }
                },
            },
        },

        "Kh-25MPU": {  # antiradiation
            "type": "ASM",
            "model": "Kh-25MPU",
            "users": ["USSR", "Russia", "India", "Syria"],
            "task": ["SEAD"],
            "start_service": 1975,  # 1978 --1982 vers. U
            "end_service": None,
            "cost": 300,  # k$
            "tnt": 90,  # kg
            "range": 30,  # Km
            "perc_efficiency_variability": 0.1,  # efficiency variability(0-1): firepower_max = firepower_max * (1 + perc_efficiency_variability)
            "efficiency": {
                "SAM": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 0.83,
                        "destroy_capacity": 0.7,
                    },
                    "med": {
                        "accuracy": 0.83,
                        "destroy_capacity": 0.75,
                    },
                    "small": {
                        "accuracy": 0.75,
                        "destroy_capacity": 0.8,
                    }
                },
            },
        },

        "Kh-25MP": {  # antiradiation
            "type": "ASM",
            "model": "Kh-25MP",
            "users": ["USSR", "Russia", "India", "Syria", "Iraq", "Libya"],
            "task": ["SEAD"],
            "start_service": 1975,  # 1978 --1982 vers. U
            "end_service": None,
            "cost": 200,  # k$
            "tnt": 90,  # kg
            "range": 18,  # Km
            "perc_efficiency_variability": 0.2,  # efficiency variability(0-1): firepower_max = firepower_max * (1 + perc_efficiency_variability)
            "efficiency": {
                "SAM": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 0.7,
                        "destroy_capacity": 0.7,
                    },
                    "med": {
                        "accuracy": 0.7,
                        "destroy_capacity": 0.75,
                    },
                    "small": {
                        "accuracy": 0.6,
                        "destroy_capacity": 0.8,
                    }
                },
            },
        },

        "Kh-29L": {  # laser guided
            "type": "ASM",
            "model": "Kh-29L",
            "users": ["USSR", "Russia", "India", "China", "Syria", "Algeria"],
            "task": ["Anti-ship Strike", "Strike", "SEAD"],
            "start_service": 1980,
            "end_service": None,
            "cost": 160,  # k$
            "tnt": 320,  # kg
            "range": 10,  # Km
            "perc_efficiency_variability": 0.05,  # efficiency variability 0-1 (100%)
            "efficiency": {
                "Structure": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 1,
                        "destroy_capacity": 0.55,
                    },
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.7,
                    },
                    "small": {
                        "accuracy": 0.95,
                        "destroy_capacity": 1,
                    }
                },
                "Bridge": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.5,
                    },
                    "small": {
                        "accuracy": 0.95,
                        "destroy_capacity": 0.95,
                    }
                },
                "ship": {  # mobile target
                    "big": {
                        "accuracy": 1,
                        "destroy_capacity": 0.9,
                    },
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 1,
                    }
                },
            },
        },

        "Kh-29T": {  # TV guided
            "type": "ASM",
            "model": "Kh-29T",
            "users": ["USSR", "Russia", "India", "China", "Syria", "Algeria"],
            "task": ["Anti-ship Strike", "Strike", "SEAD"],
            "start_service": 1980,
            "end_service": None,
            "cost": 160,  # k$
            "tnt": 320,  # kg
            "range": 12,  # Km
            "perc_efficiency_variability": 0.05,  # efficiency variability 0-1 (100%)
            "efficiency": {
                "Structure": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "big": {
                        "accuracy": 1,
                        "destroy_capacity": 0.55,
                    },
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.7,
                    },
                    "small": {
                        "accuracy": 0.95,
                        "destroy_capacity": 1,
                    }
                },
                "Bridge": {  # fixed target (guided bombs and agm missile are more efficiency)
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 0.5,
                    },
                    "small": {
                        "accuracy": 0.95,
                        "destroy_capacity": 0.95,
                    }
                },
                "ship": {  # mobile target
                    "big": {
                        "accuracy": 1,
                        "destroy_capacity": 0.9,
                    },
                    "med": {
                        "accuracy": 1,
                        "destroy_capacity": 1,
                    }
                },
            },
        },

        },
        'BOMBS': {
            "FAB-1500M54": {
                "type": "Bombs",
                "task": ["Strike"],
                "start_service": 1962,
                "end_service": None,
                "cost": 6,  # k$
                "tnt": 667,  # kg
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "Structure": {
                        "big": {
                            "accuracy": 1,
                            "destroy_capacity": 0.88
                        },
                        "med": {
                            "accuracy": 0.9,
                            "destroy_capacity": 1
                        },
                        "small": {
                            "accuracy": 0.8,
                            "destroy_capacity": 1
                        }
                    },
                    "Bridge": {
                        "big": {
                            "accuracy": 1,
                            "destroy_capacity": 0.9
                        },
                        "med": {
                            "accuracy": 0.9,
                            "destroy_capacity": 1
                        },
                        "small": {
                            "accuracy": 0.8,
                            "destroy_capacity": 1
                        }
                    }
                }
            },
            
            "FAB-500M62": {
                "type": "Bombs",
                "task": ["Strike", "Anti-ship Strike"],
                "start_service": 1962,
                "end_service": None,
                "cost": 3.3,  # k$
                "tnt": 201,  # kg
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "Structure": {
                        "big": {
                            "accuracy": 1,
                            "destroy_capacity": 0.4
                        },
                        "med": {
                            "accuracy": 0.9,
                            "destroy_capacity": 0.45
                        },
                        "small": {
                            "accuracy": 0.8,
                            "destroy_capacity": 0.5
                        }
                    },
                    "Bridge": {
                        "big": {
                            "accuracy": 1,
                            "destroy_capacity": 0.35
                        },
                        "med": {
                            "accuracy": 0.9,
                            "destroy_capacity": 0.4
                        },
                        "small": {
                            "accuracy": 0.8,
                            "destroy_capacity": 0.45
                        }
                    },
                    "ship": {
                        "big": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.42
                        },
                        "med": {
                            "accuracy": 0.5,
                            "destroy_capacity": 0.5
                        },
                        "small": {
                            "accuracy": 0.3,
                            "destroy_capacity": 0.5
                        }
                    },
                    "soft": {
                        "big": {
                            "accuracy": 0.85,
                            "destroy_capacity": 1
                        },
                        "med": {
                            "accuracy": 0.75,
                            "destroy_capacity": 1
                        },
                        "small": {
                            "accuracy": 0.65,
                            "destroy_capacity": 1
                        }
                    },
                    "armor": {
                        "big": {
                            "accuracy": 0.85,
                            "destroy_capacity": 0.8
                        },
                        "med": {
                            "accuracy": 0.75,
                            "destroy_capacity": 0.9
                        },
                        "small": {
                            "accuracy": 0.7,
                            "destroy_capacity": 1
                        }
                    },
                    "SAM": {
                        "big": {
                            "accuracy": 0.85,
                            "destroy_capacity": 0.95
                        },
                        "med": {
                            "accuracy": 0.75,
                            "destroy_capacity": 1
                        },
                        "small": {
                            "accuracy": 0.7,
                            "destroy_capacity": 1
                        }
                    }
                }
            },
            
            "FAB-250M54": {
                "type": "Bombs",
                "task": ["Strike", "Anti-ship Strike"],
                "start_service": 1962,
                "end_service": None,
                "cost": 2.7,  # k$
                "tnt": 94,  # kg
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "Structure": {
                        "big": {
                            "accuracy": 1,
                            "destroy_capacity": 0.15
                        },
                        "med": {
                            "accuracy": 0.9,
                            "destroy_capacity": 0.22
                        },
                        "small": {
                            "accuracy": 0.8,
                            "destroy_capacity": 0.53
                        }
                    },
                    "Bridge": {
                        "med": {
                            "accuracy": 0.9,
                            "destroy_capacity": 0.22
                        },
                        "small": {
                            "accuracy": 0.8,
                            "destroy_capacity": 0.33
                        }
                    },
                    "ship": {
                        "big": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.22
                        },
                        "med": {
                            "accuracy": 0.5,
                            "destroy_capacity": 0.27
                        },
                        "small": {
                            "accuracy": 0.3,
                            "destroy_capacity": 0.35
                        }
                    },
                    "soft": {
                        "med": {
                            "accuracy": 0.8,
                            "destroy_capacity": 0.85
                        },
                        "small": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.95
                        }
                    },
                    "armor": {
                        "big": {
                            "accuracy": 0.85,
                            "destroy_capacity": 0.65
                        },
                        "med": {
                            "accuracy": 0.8,
                            "destroy_capacity": 0.7
                        },
                        "small": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.75
                        }
                    },
                    "SAM": {
                        "big": {
                            "accuracy": 0.9,
                            "destroy_capacity": 0.7
                        },
                        "med": {
                            "accuracy": 0.85,
                            "destroy_capacity": 0.75
                        },
                        "small": {
                            "accuracy": 0.75,
                            "destroy_capacity": 0.8
                        }
                    }
                }
            },
        
            "FAB-100": {
                "type": "Bombs",
                "task": ["Strike", "Anti-ship Strike"],
                "start_service": 1962,
                "end_service": None,
                "cost": 1.5,  # k$
                "tnt": 39,  # kg
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "Structure": {
                        "med": {"accuracy": 0.9, "destroy_capacity": 0.1},
                        "small": {"accuracy": 0.8, "destroy_capacity": 0.20}
                    },
                    "ship": {
                        "med": {"accuracy": 0.5, "destroy_capacity": 0.1},
                        "small": {"accuracy": 0.3, "destroy_capacity": 0.2}
                    },
                    "soft": {
                        "med": {"accuracy": 0.8, "destroy_capacity": 0.4},
                        "small": {"accuracy": 0.7, "destroy_capacity": 0.5}
                    },
                    "armor": {
                        "big": {"accuracy": 0.85, "destroy_capacity": 0.2},
                        "med": {"accuracy": 0.8, "destroy_capacity": 0.25},
                        "small": {"accuracy": 0.7, "destroy_capacity": 0.35}
                    },
                    "SAM": {
                        "big": {"accuracy": 0.9, "destroy_capacity": 0.25},
                        "med": {"accuracy": 0.85, "destroy_capacity": 0.3},
                        "small": {"accuracy": 0.75, "destroy_capacity": 0.4}
                    },
                },
            },

            "FAB-50": {
                "type": "Bombs",
                "task": ["Strike"],
                "start_service": 1950,
                "end_service": None,
                "cost": 1,  # k$
                "tnt": 20,  # kg
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "soft": {
                        "med": {"accuracy": 0.8, "destroy_capacity": 0.2},
                        "small": {"accuracy": 0.7, "destroy_capacity": 0.25}
                    },
                    "armor": {
                        "big": {"accuracy": 0.85, "destroy_capacity": 0.08},
                        "med": {"accuracy": 0.8, "destroy_capacity": 0.12},
                        "small": {"accuracy": 0.7, "destroy_capacity": 0.17}
                    },
                    "SAM": {
                        "big": {"accuracy": 0.9, "destroy_capacity": 0.12},
                        "med": {"accuracy": 0.85, "destroy_capacity": 0.15},
                        "small": {"accuracy": 0.75, "destroy_capacity": 0.2}
                    },
                },
            },

            "RBK-250AO": {
                "type": "Cluster bombs",
                "task": ["Strike"],
                "start_service": 1970,
                "end_service": None,
                "cost": 16,  # k$
                "weight": 250,  # kg
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "SAM": {
                        "big": {"accuracy": 0.75, "destroy_capacity": 2},
                        "med": {"accuracy": 0.7, "destroy_capacity": 3},
                        "small": {"accuracy": 0.65, "destroy_capacity": 4}
                    },
                    "soft": {
                        "big": {"accuracy": 0.75, "destroy_capacity": 3.2},
                        "med": {"accuracy": 0.7, "destroy_capacity": 4.3},
                        "small": {"accuracy": 0.65, "destroy_capacity": 7.5}
                    },
                },
            },

            "RBK-500AO": {
                "type": "Cluster bombs",
                "task": ["Strike"],
                "start_service": 1970,
                "end_service": None,
                "cost": 17,  # k$
                "weight": 500,  # kg
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "SAM": {
                        "big": {"accuracy": 0.75, "destroy_capacity": 3},
                        "med": {"accuracy": 0.7, "destroy_capacity": 4},
                        "small": {"accuracy": 0.65, "destroy_capacity": 5}
                    },
                    "soft": {
                        "big": {"accuracy": 0.75, "destroy_capacity": 4},
                        "med": {"accuracy": 0.7, "destroy_capacity": 6},
                        "small": {"accuracy": 0.65, "destroy_capacity": 8}
                    },
                },
            },

            "RBK-500PTAB": {
                "type": "Cluster bombs",
                "task": ["Strike"],
                "start_service": 1970,
                "end_service": None,
                "cost": 20,  # k$
                "weight": 500,  # kg
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "SAM": {
                        "big": {"accuracy": 0.75, "destroy_capacity": 3},
                        "med": {"accuracy": 0.7, "destroy_capacity": 4},
                        "small": {"accuracy": 0.65, "destroy_capacity": 5}
                    },
                    "soft": {
                        "big": {"accuracy": 0.75, "destroy_capacity": 4},
                        "med": {"accuracy": 0.7, "destroy_capacity": 6},
                        "small": {"accuracy": 0.65, "destroy_capacity": 8}
                    },
                    "armor": {
                        "big": {"accuracy": 0.75, "destroy_capacity": 3.2},
                        "med": {"accuracy": 0.8, "destroy_capacity": 4.3},
                        "small": {"accuracy": 0.7, "destroy_capacity": 6}
                    },
                },
            },

            "BetAB-500": {
                "type": "Bombs",
                "task": ["Strike", "Anti-ship Strike"],
                "start_service": 1962,
                "end_service": None,
                "cost": 2.7,  # k$
                "tnt": 92,  # kg
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "Structure": {
                        "big": {"accuracy": 1, "destroy_capacity": 0.15},
                        "med": {"accuracy": 0.9, "destroy_capacity": 0.22},
                        "small": {"accuracy": 0.8, "destroy_capacity": 0.53}
                    },
                    "Bridge": {
                        "med": {"accuracy": 0.9, "destroy_capacity": 0.22},
                        "small": {"accuracy": 0.8, "destroy_capacity": 0.33}
                    },
                    "ship": {
                        "big": {"accuracy": 0.7, "destroy_capacity": 0.22},
                        "med": {"accuracy": 0.5, "destroy_capacity": 0.27},
                        "small": {"accuracy": 0.3, "destroy_capacity": 0.35}
                    },
                    "soft": {
                        "med": {"accuracy": 0.8, "destroy_capacity": 0.85},
                        "small": {"accuracy": 0.7, "destroy_capacity": 0.95}
                    },
                    "armor": {
                        "big": {"accuracy": 0.85, "destroy_capacity": 0.65},
                        "med": {"accuracy": 0.8, "destroy_capacity": 0.7},
                        "small": {"accuracy": 0.7, "destroy_capacity": 0.75}
                    },
                    "SAM": {
                        "big": {"accuracy": 0.9, "destroy_capacity": 0.7},
                        "med": {"accuracy": 0.85, "destroy_capacity": 0.75},
                        "small": {"accuracy": 0.75, "destroy_capacity": 0.8}
                    },
                },
            },
        
            "KAB-500L": {  # laser bomb (FAB-500 with laser guide)
                "type": "Guided bombs",
                "task": ["Strike"],
                "start_service": 1975,
                "end_service": None,
                "cost": 25,  # k$
                "tnt": 201,  # kg
                "perc_efficiency_variability": 0.05,  # percentage of efficiecy variability 0-1 (100%)
                "efficiency": {
                    "Structure": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "big": {
                            "accuracy": 1,  # 1 max, 0.1 min ( hit success percentage )
                            "destroy_capacity": 0.4,  # 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )
                        },
                        "med": {
                            "accuracy": 1,
                            "destroy_capacity": 0.45,
                        },
                        "small": {
                            "accuracy": 0.9,
                            "destroy_capacity": 0.5,
                        }
                    },
                    "Bridge": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "big": {
                            "accuracy": 1,
                            "destroy_capacity": 0.35,
                        },
                        "med": {
                            "accuracy": 1,
                            "destroy_capacity": 0.4,
                        },
                        "small": {
                            "accuracy": 0.9,
                            "destroy_capacity": 0.45,
                        }
                    },
                    "soft": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "big": {
                            "accuracy": 0.85,
                            "destroy_capacity": 1,
                        },
                        "med": {
                            "accuracy": 0.75,
                            "destroy_capacity": 1,
                        },
                        "small": {
                            "accuracy": 0.65,
                            "destroy_capacity": 1,
                        }
                    },
                    "armor": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "big": {
                            "accuracy": 0.85,
                            "destroy_capacity": 0.8,
                        },
                        "med": {
                            "accuracy": 0.75,
                            "destroy_capacity": 0.9,
                        },
                        "small": {
                            "accuracy": 0.7,
                            "destroy_capacity": 1,
                        }
                    },
                    "SAM": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "big": {
                            "accuracy": 0.85,
                            "destroy_capacity": 0.95,
                        },
                        "med": {
                            "accuracy": 0.75,
                            "destroy_capacity": 1,
                        },
                        "small": {
                            "accuracy": 0.7,
                            "destroy_capacity": 1,
                        }
                    },
                },
            },
            
            "KAB-500Kr": {  # tv-guided bomb fire&forget (FAB-500)
                "type": "Guided bombs",
                "task": ["Strike"],
                "start_service": 1980,
                "end_service": None,
                "cost": 23,  # k$
                "tnt": 201,  # kg
                "perc_efficiency_variability": 0.05,  # percentage of efficiecy variability 0-1 (100%)
                "efficiency": {
                    "Structure": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "big": {
                            "accuracy": 1,  # 1 max, 0.1 min ( hit success percentage )
                            "destroy_capacity": 0.4,  # 1 max: element destroyed (single hit), 0.1 min ( element destroy capacity )
                        },
                        "med": {
                            "accuracy": 1,
                            "destroy_capacity": 0.45,
                        },
                        "small": {
                            "accuracy": 0.9,
                            "destroy_capacity": 0.5,
                        }
                    },
                    "Bridge": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "big": {
                            "accuracy": 1,
                            "destroy_capacity": 0.35,
                        },
                        "med": {
                            "accuracy": 1,
                            "destroy_capacity": 0.4,
                        },
                        "small": {
                            "accuracy": 0.9,
                            "destroy_capacity": 0.45,
                        }
                    },
                    "soft": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "big": {
                            "accuracy": 0.85,
                            "destroy_capacity": 1,
                        },
                        "med": {
                            "accuracy": 0.75,
                            "destroy_capacity": 1,
                        },
                        "small": {
                            "accuracy": 0.65,
                            "destroy_capacity": 1,
                        }
                    },
                    "armor": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "big": {
                            "accuracy": 0.85,
                            "destroy_capacity": 0.8,
                        },
                        "med": {
                            "accuracy": 0.75,
                            "destroy_capacity": 0.9,
                        },
                        "small": {
                            "accuracy": 0.7,
                            "destroy_capacity": 1,
                        }
                    },
                    "SAM": {  # fixed target (guided bombs and agm missile are more efficiency)
                        "big": {
                            "accuracy": 0.85,
                            "destroy_capacity": 0.95,
                        },
                        "med": {
                            "accuracy": 0.75,
                            "destroy_capacity": 1,
                        },
                        "small": {
                            "accuracy": 0.7,
                            "destroy_capacity": 1,
                        }
                    },
                },
            },
            
            "KGBU-2AO": {  # cluster bomb soft target
                "type": "Cluster bombs",
                "task": ["Strike"],
                "start_service": 1970,
                "end_service": None,
                "cost": 12,  # k$
                "weight": 250,  # ??--kg
                "perc_efficiency_variability": 0.1,  # percentage of efficiecy variability 0-1 (100%)
                "efficiency": {
                    "SAM": {  # non Anti-tank but antenna, launcher gear and PSU system are like soft units
                        "big": {
                            "accuracy": 0.75,  # 1 max, 0.1 min ( hit success percentage )
                            "destroy_capacity": 2,  # element destroyed (single hit), 0.1 min ( element destroy capacity )
                        },
                        "med": {
                            "accuracy": 0.7,
                            "destroy_capacity": 3,
                        },
                        "small": {
                            "accuracy": 0.65,
                            "destroy_capacity": 4,
                        }
                    },
                    "soft": {  # mobile target(artillery group)
                        "big": {
                            "accuracy": 0.75,
                            "destroy_capacity": 3.2,
                        },
                        "med": {
                            "accuracy": 0.7,
                            "destroy_capacity": 4.3,
                        },
                        "small": {
                            "accuracy": 0.65,
                            "destroy_capacity": 7.5,
                        }
                    },
                },
            },
            
            "KGBU-2PTAB": {  # cluster bomb armor target
                "type": "Cluster bombs",
                "task": ["Strike"],
                "start_service": 1970,
                "end_service": None,
                "cost": 16,  # k$
                "weight": 250,  # ??--kg
                "perc_efficiency_variability": 0.1,  # percentage of efficiecy variability 0-1 (100%)
                "efficiency": {
                    "SAM": {  # non Anti-tank but antenna, launcher gear and PSU system are like soft units
                        "big": {
                            "accuracy": 0.75,  # 1 max, 0.1 min ( hit success percentage )
                            "destroy_capacity": 2,  # element destroyed (single hit), 0.1 min ( element destroy capacity )
                        },
                        "med": {
                            "accuracy": 0.7,
                            "destroy_capacity": 3,
                        },
                        "small": {
                            "accuracy": 0.65,
                            "destroy_capacity": 4,
                        }
                    },
                    "soft": {  # mobile target(artillery group)
                        "big": {
                            "accuracy": 0.75,
                            "destroy_capacity": 3.2,
                        },
                        "med": {
                            "accuracy": 0.7,
                            "destroy_capacity": 4.3,
                        },
                        "small": {
                            "accuracy": 0.65,
                            "destroy_capacity": 7.5,
                        }
                    },
                    "armor": {
                        "big": {
                            "accuracy": 0.75,
                            "destroy_capacity": 3.2,
                        },
                        "med": {
                            "accuracy": 0.8,
                            "destroy_capacity": 4.3,
                        },
                        "small": {
                            "accuracy": 0.7,
                            "destroy_capacity": 7,
                        }
                    },
                },
            },
            
            "KGBU-96r": {  # ?? cluster bomb soft target VERIFY
                "type": "Cluster bombs",
                "task": ["Strike"],
                "start_service": 1970,
                "end_service": None,
                "cost": 12,  # k$
                "weight": 250,  # ??--kg
                "perc_efficiency_variability": 0.1,  # percentage of efficiecy variability 0-1 (100%)
                "efficiency": {
                    "SAM": {  # non Anti-tank but antenna, launcher gear and PSU system are like soft units
                        "big": {
                            "accuracy": 0.75,  # 1 max, 0.1 min ( hit success percentage )
                            "destroy_capacity": 2,  # element destroyed (single hit), 0.1 min ( element destroy capacity )
                        },
                        "med": {
                            "accuracy": 0.7,
                            "destroy_capacity": 3,
                        },
                        "small": {
                            "accuracy": 0.65,
                            "destroy_capacity": 4,
                        }
                    },
                    "soft": {  # mobile target(artillery group)
                        "big": {
                            "accuracy": 0.75,
                            "destroy_capacity": 3.2,
                        },
                        "med": {
                            "accuracy": 0.7,
                            "destroy_capacity": 4.3,
                        },
                        "small": {
                            "accuracy": 0.65,
                            "destroy_capacity": 7.5,
                        }
                    },
                },
            },
        },
        'ROCKETS':{
            "UPK-23": {
                "type": "Rockets",
                "task": ["Strike", "Anti-ship Strike"],
                "start_service": 1972,
                "end_service": None,
                "cost": None,  # k$
                "tnt": None,  # kg
                "range": 2,  # Km
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "ship": {
                        "small": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.15,
                        }
                    },
                    "soft": {
                        "big": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.1,
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.2,
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 0.4,
                        }
                    },
                    "armor": {
                        "big": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.05,
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.1,
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 0.2,
                        }
                    }
                },
            },
        
            "Gsh-23L": {
                "type": "Rockets",
                "task": ["Strike"],
                "start_service": 1972,
                "end_service": None,
                "cost": None,
                "tnt": None,
                "range": 2,
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "ship": {
                        "small": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.15
                        }
                    },
                    "soft": {
                        "big": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.1
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.2
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 0.4
                        }
                    },
                    "armor": {
                        "big": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.05
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.1
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 0.2
                        }
                    }
                }
            },
            
            "S-5 M": {
                "type": "Rockets",
                "task": ["Strike", "Anti-ship Strike"],
                "start_service": 1960,
                "end_service": None,
                "cost": 0.4,
                "tnt": 6,
                "range": 4,
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "Structure": {
                    },
                    "ship": {
                        "med": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.1
                        },
                        "small": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.15
                        }
                    },
                    "soft": {
                        "big": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.3
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.4
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 0.6
                        }
                    },
                    "armor": {
                        "big": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.2
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.3
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 0.4
                        }
                    }
                }
            },
            
            "S-5 KO": {
                "type": "Rockets",
                "task": ["Strike", "Anti-ship Strike"],
                "start_service": 1973,
                "end_service": None,
                "cost": 0.8,
                "tnt": 6,
                "range": 4,
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "Structure": {
                    },
                    "ship": {
                        "med": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.1
                        },
                        "small": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.15
                        }
                    },
                    "soft": {
                        "big": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.3
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.4
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 0.6
                        }
                    },
                    "armor": {
                        "big": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.2
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.3
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 0.4
                        }
                    }
                }
            },
            
            "S-8 OFP2": {
                "type": "Rockets",
                "task": ["Strike", "Anti-ship Strike"],
                "start_service": 1973,
                "end_service": None,
                "cost": 0.6,
                "tnt": 6,
                "range": 4,
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "Structure": {
                    },
                    "ship": {
                        "med": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.08
                        },
                        "small": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.1
                        }
                    },
                    "soft": {
                        "big": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.3
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.4
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 0.6
                        }
                    }
                }
            },
            
            "S-8 KOM": {
                "type": "Rockets",
                "task": ["Strike", "Anti-ship Strike"],
                "start_service": 1973,
                "end_service": None,
                "cost": 1,
                "tnt": 6,
                "range": 4,
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "Structure": {
                    },
                    "ship": {
                        "med": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.1
                        },
                        "small": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.15
                        }
                    },
                    "soft": {
                        "big": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.3
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.4
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 0.6
                        }
                    },
                    "armor": {
                        "big": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.2
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.3
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 0.4
                        }
                    }
                }
            },
            
            "S-13": {
                "type": "Rockets",
                "task": ["Strike", "Anti-ship Strike"],
                "start_service": 1973,
                "end_service": None,
                "cost": 0.8,
                "tnt": 1.9,
                "range": 3,
                "perc_efficiency_variability": 0.1,
                "efficiency": {
                    "soft": {
                        "big": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.1
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.13
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 0.15
                        }
                    }
                }
            },

            "S-25L": {  # Rockets 340 mm hard target (antitank), 250OFM, Launcher O-25 (qty: 1)
                "type": "Rockets",
                "task": ["Strike", "Anti-ship Strike"],
                "start_service": 1975,
                "end_service": None,
                "cost": 2.8,  # k$
                "tnt": 20,
                "range": 7,  # Km
                "perc_efficiency_variability": 0.1,  # percentage of efficiecy variability 0-1 (100%)
                "efficiency": {
                    "Structure": {  # fixed target (guided bombs and agm missile are more efficiency)
                    },
                    "ship": {  # mobile target
                        "med": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.4,
                        },
                        "small": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.5,
                        }
                    },
                    "soft": {  # mobile target(artillery group)
                        "big": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.8,
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.9,
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 1,
                        }
                    },
                    "armor": {  # mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                        "big": {
                            "accuracy": 0.7,
                            "destroy_capacity": 0.4,
                        },
                        "med": {
                            "accuracy": 0.6,
                            "destroy_capacity": 0.6,
                        },
                        "small": {
                            "accuracy": 0.5,
                            "destroy_capacity": 0.8,
                        }
                    }
                },
            },

            "S-24": {  # (Vers. A/B) Rockets 240 mm soft target, launcher: PU-12-40U (qty: 1), APU-7D, APU-68U
            "type": "Rockets",
            "task": ["Strike", "Anti-ship Strike"],
            "start_service": 1960,
            "end_service": None,
            "cost": 1.5,  # k$
            "tnt": 25.5,  # kg ?? (not applicable?)
            "range": 3,  # Km
            "perc_efficiency_variability": 0.1,  # percentage of efficiecy variability 0-1 (100%)
            "efficiency": {
                "Structure": {  # fixed target (guided bombs and agm missile are more efficiency)
                },
                "ship": {  # mobile target
                    "med": {
                        "accuracy": 0.7,
                        "destroy_capacity": 0.3,
                    },
                    "small": {
                        "accuracy": 0.6,
                        "destroy_capacity": 0.4,
                    }
                },
                "soft": {  # mobile target(artillery group)
                    "big": {
                        "accuracy": 0.7,
                        "destroy_capacity": 0.8,
                    },
                    "med": {
                        "accuracy": 0.6,
                        "destroy_capacity": 0.9,
                    },
                    "small": {
                        "accuracy": 0.5,
                        "destroy_capacity": 1,
                    }
                },
                "armor": {  # mobile target armor non è presente in targetlist, cmq valuta se inserirlo x distinguerlo da soft
                    "big": {
                        "accuracy": 0.7,
                        "destroy_capacity": 0.2,
                    },
                    "med": {
                        "accuracy": 0.6,
                        "destroy_capacity": 0.3,
                    },
                    "small": {
                        "accuracy": 0.5,
                        "destroy_capacity": 0.4,
                    }
                }
            },
        },
        },        
    }
}



#for side in weapon_db:
#    for weapon_name, weapon_data in side:        
#        AIR_WEAPONS[side][weapon_data['type']][weapon_name] = weapon_data

                




# Nota: Ho notato che in alcuni dizionari c'è "manouvrability" e in altri "manouvrability" (con una 'a' in più)
# Sarebbe meglio uniformare l'ortografia per mantenere la coerenza nel codice

