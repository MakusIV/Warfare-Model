# =============================================================================
# Aircraft_Loadouts.py
# =============================================================================
# Defines AIRCRAFT_LOADOUTS: all possible weapon loadouts for each aircraft.
# Keys match the "model" field in Aircraft_Data.py.
# Weapon names match AIR_WEAPONS keys in Aircraft_Weapon_Data.py.
#
# IMPROVEMENTS over original template:
#   - attributes: Python list instead of numbered dict
#   - range: in km (altitude fields remain in metres)
#   - mandatory_support: uses proper Python dict syntax (:)
#   - self_escort_capability: bool, A/A defensive ability on A/G loadouts
#   - stores.devices: sub-section for non-weapon pylon items (pods, tanks)
#   - stores.pylon_count: total number of hardpoints
#   - stores.pylons keys: integers (1-N) or "bay_N" for internal weapon bays
#
# LOADOUT FIELDS:
#   loadout_code          : unique string identifier
#   tasks                 : list of AIR_TASK values this loadout supports
#   attributes            : list of custom target-matching strings (A/G only)
#   Lock_Down_Shoot_Down  : bool, BVR/WVR lock-down capability (A/A tasks)
#   self_escort_capability: bool, loadout retains A/A self-defence weapons
#   cruise                : best-endurance performance with this loadout
#   attack                : max-performance envelope during weapon employment
#   usability             : environmental operating conditions
#   mandatory_support     : required external support for this loadout
#   stores                : full list of carried stores and internal resources
# =============================================================================

from Code.Dynamic_War_Manager.Source.Context.Context import AIR_TASK

# ---------------------------------------------------------------------------
# Shared helper comment: range values are combat radius in km
# fuel_25/50/75/100 = fraction of full internal fuel (+ aux tanks if carried)
# ---------------------------------------------------------------------------

AIRCRAFT_LOADOUTS = {

    # =========================================================================
    # US FIGHTERS
    # =========================================================================

    # -------------------------------------------------------------------------
    "F-14A Tomcat": {

        "Phoenix Fleet Defense": {
            "loadout_code": "F14A-CAP-1",
            "tasks": ["CAP", "Intercept"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True,
            "self_escort_capability": True,
            "cruise": {
                "speed": 850, "reference_altitude": 9000,
                "altitude_max": 15000, "altitude_min": 5000,
                "range": {"fuel_25%": 200, "fuel_50%": 420, "fuel_75%": 640, "fuel_100%": 850},
            },
            "attack": {
                "speed": 1800, "reference_altitude": 10000,
                "altitude_max": 16000, "altitude_min": 3000,
                "range": {"fuel_25%": 150, "fuel_50%": 320, "fuel_75%": 490, "fuel_100%": 650},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AIM-54A-MK47", 1], 2: ["AIM-54A-MK47", 1],
                    3: ["AIM-54A-MK47", 1], 4: ["AIM-54A-MK47", 1],
                    5: ["AIM-9L", 1], 6: ["AIM-9L", 1],
                    7: ["AIM-7M", 1], 8: ["AIM-7M", 1],
                },
                "devices": {},
                "pylon_count": 10,
                "fuel_internal_max": 7348, "flare": 60, "chaff": 60, "gun_rounds": 675,
            },
        },

        "Sparrow CAP/Escort": {
            "loadout_code": "F14A-CAP-2",
            "tasks": ["CAP", "Escort"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True,
            "self_escort_capability": True,
            "cruise": {
                "speed": 800, "reference_altitude": 9000,
                "altitude_max": 15000, "altitude_min": 1000,
                "range": {"fuel_25%": 220, "fuel_50%": 450, "fuel_75%": 680, "fuel_100%": 950},
            },
            "attack": {
                "speed": 1600, "reference_altitude": 8000,
                "altitude_max": 15000, "altitude_min": 1000,
                "range": {"fuel_25%": 160, "fuel_50%": 340, "fuel_75%": 520, "fuel_100%": 720},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AIM-7M", 1], 2: ["AIM-7M", 1],
                    3: ["AIM-7M", 1], 4: ["AIM-7M", 1],
                    5: ["AIM-9L", 1], 6: ["AIM-9L", 1],
                    7: ["267gal_tank", 1, 900], 8: ["267gal_tank", 1, 900],
                },
                "devices": {},
                "pylon_count": 10,
                "fuel_internal_max": 7348, "flare": 60, "chaff": 60, "gun_rounds": 675,
            },
        },

        "Sidewinder Dogfight": {
            "loadout_code": "F14A-CAP-3",
            "tasks": ["CAP", "Intercept"],
            "attributes": [],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 900, "reference_altitude": 8000,
                "altitude_max": 15000, "altitude_min": 100,
                "range": {"fuel_25%": 250, "fuel_50%": 500, "fuel_75%": 760, "fuel_100%": 1000},
            },
            "attack": {
                "speed": 1800, "reference_altitude": 5000,
                "altitude_max": 15000, "altitude_min": 100,
                "range": {"fuel_25%": 180, "fuel_50%": 380, "fuel_75%": 570, "fuel_100%": 780},
            },
            "usability": {"day": True, "night": True, "adverse_weather": False},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AIM-9M", 1], 2: ["AIM-9M", 1],
                    3: ["AIM-7M", 1], 4: ["AIM-7M", 1],
                    5: ["267gal_tank", 1, 900], 6: ["267gal_tank", 1, 900],
                },
                "devices": {},
                "pylon_count": 10,
                "fuel_internal_max": 7348, "flare": 60, "chaff": 60, "gun_rounds": 675,
            },
        },
    },

    # -------------------------------------------------------------------------
    "F-14B Tomcat": {

        "Phoenix Fleet Defense": {
            "loadout_code": "F14B-CAP-1",
            "tasks": ["CAP", "Intercept"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True,
            "self_escort_capability": True,
            "cruise": {
                "speed": 880, "reference_altitude": 9000,
                "altitude_max": 16000, "altitude_min": 5000,
                "range": {"fuel_25%": 210, "fuel_50%": 430, "fuel_75%": 660, "fuel_100%": 880},
            },
            "attack": {
                "speed": 1900, "reference_altitude": 10000,
                "altitude_max": 16000, "altitude_min": 3000,
                "range": {"fuel_25%": 155, "fuel_50%": 330, "fuel_75%": 510, "fuel_100%": 680},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AIM-54C-MK47", 1], 2: ["AIM-54C-MK47", 1],
                    3: ["AIM-54C-MK47", 1], 4: ["AIM-54C-MK47", 1],
                    5: ["AIM-9M", 1], 6: ["AIM-9M", 1],
                    7: ["AIM-7M", 1], 8: ["AIM-7M", 1],
                },
                "devices": {},
                "pylon_count": 10,
                "fuel_internal_max": 7348, "flare": 60, "chaff": 60, "gun_rounds": 675,
            },
        },

        "Escort CAP": {
            "loadout_code": "F14B-ESCORT-1",
            "tasks": ["Escort", "CAP"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True,
            "self_escort_capability": True,
            "cruise": {
                "speed": 820, "reference_altitude": 9000,
                "altitude_max": 15000, "altitude_min": 1000,
                "range": {"fuel_25%": 230, "fuel_50%": 470, "fuel_75%": 710, "fuel_100%": 980},
            },
            "attack": {
                "speed": 1600, "reference_altitude": 8000,
                "altitude_max": 15000, "altitude_min": 1000,
                "range": {"fuel_25%": 170, "fuel_50%": 360, "fuel_75%": 540, "fuel_100%": 740},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AIM-54C-MK47", 1], 2: ["AIM-54C-MK47", 1],
                    3: ["AIM-7M", 1], 4: ["AIM-7M", 1],
                    5: ["AIM-9M", 1], 6: ["AIM-9M", 1],
                    7: ["267gal_tank", 1, 900], 8: ["267gal_tank", 1, 900],
                },
                "devices": {},
                "pylon_count": 10,
                "fuel_internal_max": 7348, "flare": 60, "chaff": 60, "gun_rounds": 675,
            },
        },

        "Strike/LANTIRN": {
            "loadout_code": "F14B-STRIKE-1",
            "tasks": ["Strike"],
            "attributes": ["Precision", "Day/Night"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 800, "reference_altitude": 7000,
                "altitude_max": 12000, "altitude_min": 500,
                "range": {"fuel_25%": 190, "fuel_50%": 390, "fuel_75%": 600, "fuel_100%": 820},
            },
            "attack": {
                "speed": 900, "reference_altitude": 3000,
                "altitude_max": 8000, "altitude_min": 300,
                "range": {"fuel_25%": 140, "fuel_50%": 300, "fuel_75%": 460, "fuel_100%": 640},
            },
            "usability": {"day": True, "night": True, "adverse_weather": False},
            "mandatory_support": {
                "Escort": True, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["GBU-24", 1], 2: ["GBU-24", 1],
                    3: ["AIM-9M", 1], 4: ["AIM-9M", 1],
                    5: ["267gal_tank", 1, 900],
                },
                "devices": {1: ["LANTIRN_pod", 1]},
                "pylon_count": 10,
                "fuel_internal_max": 7348, "flare": 60, "chaff": 60, "gun_rounds": 675,
            },
        },
    },

    # -------------------------------------------------------------------------
    "F-15C Eagle": {

        "Eagle Sweep": {
            "loadout_code": "F15C-CAP-1",
            "tasks": ["CAP", "Fighter_Sweep", "Intercept"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True,
            "self_escort_capability": True,
            "cruise": {
                "speed": 900, "reference_altitude": 9000,
                "altitude_max": 18000, "altitude_min": 3000,
                "range": {"fuel_25%": 250, "fuel_50%": 520, "fuel_75%": 790, "fuel_100%": 1050},
            },
            "attack": {
                "speed": 2200, "reference_altitude": 12000,
                "altitude_max": 18000, "altitude_min": 1000,
                "range": {"fuel_25%": 180, "fuel_50%": 380, "fuel_75%": 580, "fuel_100%": 780},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AIM-7M", 1], 2: ["AIM-7M", 1],
                    3: ["AIM-7M", 1], 4: ["AIM-7M", 1],
                    5: ["AIM-9M", 1], 6: ["AIM-9M", 1],
                    7: ["AIM-9M", 1], 8: ["AIM-9M", 1],
                },
                "devices": {},
                "pylon_count": 8,
                "fuel_internal_max": 6103, "flare": 120, "chaff": 120, "gun_rounds": 940,
            },
        },

        "Eagle Escort": {
            "loadout_code": "F15C-ESCORT-1",
            "tasks": ["Escort", "CAP"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True,
            "self_escort_capability": True,
            "cruise": {
                "speed": 870, "reference_altitude": 9000,
                "altitude_max": 18000, "altitude_min": 1000,
                "range": {"fuel_25%": 280, "fuel_50%": 570, "fuel_75%": 870, "fuel_100%": 1200},
            },
            "attack": {
                "speed": 1800, "reference_altitude": 9000,
                "altitude_max": 18000, "altitude_min": 1000,
                "range": {"fuel_25%": 200, "fuel_50%": 420, "fuel_75%": 640, "fuel_100%": 880},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AIM-7M", 1], 2: ["AIM-7M", 1],
                    3: ["AIM-9M", 1], 4: ["AIM-9M", 1],
                    5: ["AIM-9M", 1], 6: ["AIM-9M", 1],
                    7: ["600gal_tank", 1, 2000], 8: ["600gal_tank", 1, 2000],
                },
                "devices": {},
                "pylon_count": 8,
                "fuel_internal_max": 6103, "flare": 120, "chaff": 120, "gun_rounds": 940,
            },
        },
    },

    # -------------------------------------------------------------------------
    "F-15E Strike Eagle": {

        "Eagle SEAD": {
            "loadout_code": "F15E-SEAD-1",
            "tasks": ["SEAD"],
            "attributes": ["Anti-radar", "Stand-off"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 900, "reference_altitude": 9000,
                "altitude_max": 15000, "altitude_min": 3000,
                "range": {"fuel_25%": 260, "fuel_50%": 530, "fuel_75%": 800, "fuel_100%": 1100},
            },
            "attack": {
                "speed": 1000, "reference_altitude": 5000,
                "altitude_max": 12000, "altitude_min": 1000,
                "range": {"fuel_25%": 200, "fuel_50%": 410, "fuel_75%": 620, "fuel_100%": 860},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AGM-88", 1], 2: ["AGM-88", 1],
                    3: ["AGM-88", 1], 4: ["AGM-88", 1],
                    5: ["AIM-9M", 1], 6: ["AIM-9M", 1],
                    7: ["AIM-7M", 1], 8: ["AIM-7M", 1],
                },
                "devices": {},
                "pylon_count": 11,
                "fuel_internal_max": 6103, "flare": 120, "chaff": 120, "gun_rounds": 940,
            },
        },

        "Laser Strike": {
            "loadout_code": "F15E-STRIKE-1",
            "tasks": ["Pinpoint_Strike"],
            "attributes": ["Precision", "Laser-guided"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 880, "reference_altitude": 8000,
                "altitude_max": 14000, "altitude_min": 500,
                "range": {"fuel_25%": 240, "fuel_50%": 490, "fuel_75%": 740, "fuel_100%": 1000},
            },
            "attack": {
                "speed": 950, "reference_altitude": 4000,
                "altitude_max": 10000, "altitude_min": 300,
                "range": {"fuel_25%": 180, "fuel_50%": 370, "fuel_75%": 560, "fuel_100%": 780},
            },
            "usability": {"day": True, "night": True, "adverse_weather": False},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["GBU-12", 1], 2: ["GBU-12", 1],
                    3: ["GBU-12", 1], 4: ["GBU-12", 1],
                    5: ["AIM-9M", 1], 6: ["AIM-9M", 1],
                    7: ["AIM-7M", 1], 8: ["AIM-7M", 1],
                },
                "devices": {1: ["LANTIRN_pod", 1]},
                "pylon_count": 11,
                "fuel_internal_max": 6103, "flare": 120, "chaff": 120, "gun_rounds": 940,
            },
        },

        "Iron Bomb Strike": {
            "loadout_code": "F15E-STRIKE-2",
            "tasks": ["Strike"],
            "attributes": ["Dumb bomb", "Area"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 880, "reference_altitude": 7000,
                "altitude_max": 12000, "altitude_min": 500,
                "range": {"fuel_25%": 220, "fuel_50%": 450, "fuel_75%": 690, "fuel_100%": 940},
            },
            "attack": {
                "speed": 950, "reference_altitude": 3000,
                "altitude_max": 8000, "altitude_min": 300,
                "range": {"fuel_25%": 160, "fuel_50%": 340, "fuel_75%": 520, "fuel_100%": 720},
            },
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {
                "Escort": True, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["Mk-82", 2], 2: ["Mk-82", 2],
                    3: ["Mk-82", 2], 4: ["Mk-82", 2],
                    5: ["AIM-9M", 1], 6: ["AIM-9M", 1],
                },
                "devices": {},
                "pylon_count": 11,
                "fuel_internal_max": 6103, "flare": 120, "chaff": 120, "gun_rounds": 940,
            },
        },

        "Eagle CAP": {
            "loadout_code": "F15E-CAP-1",
            "tasks": ["CAP"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True,
            "self_escort_capability": True,
            "cruise": {
                "speed": 900, "reference_altitude": 9000,
                "altitude_max": 18000, "altitude_min": 3000,
                "range": {"fuel_25%": 270, "fuel_50%": 540, "fuel_75%": 820, "fuel_100%": 1100},
            },
            "attack": {
                "speed": 2200, "reference_altitude": 12000,
                "altitude_max": 18000, "altitude_min": 1000,
                "range": {"fuel_25%": 195, "fuel_50%": 400, "fuel_75%": 600, "fuel_100%": 810},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AIM-7M", 1], 2: ["AIM-7M", 1],
                    3: ["AIM-7M", 1], 4: ["AIM-7M", 1],
                    5: ["AIM-9M", 1], 6: ["AIM-9M", 1],
                    7: ["AIM-9M", 1], 8: ["AIM-9M", 1],
                },
                "devices": {},
                "pylon_count": 11,
                "fuel_internal_max": 6103, "flare": 120, "chaff": 120, "gun_rounds": 940,
            },
        },
    },

    # -------------------------------------------------------------------------
    "F/A-18A Hornet": {

        "Fleet CAP": {
            "loadout_code": "FA18A-CAP-1",
            "tasks": ["CAP", "Intercept"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True,
            "self_escort_capability": True,
            "cruise": {
                "speed": 850, "reference_altitude": 9000,
                "altitude_max": 15000, "altitude_min": 1000,
                "range": {"fuel_25%": 180, "fuel_50%": 380, "fuel_75%": 580, "fuel_100%": 780},
            },
            "attack": {
                "speed": 1800, "reference_altitude": 10000,
                "altitude_max": 15000, "altitude_min": 500,
                "range": {"fuel_25%": 135, "fuel_50%": 285, "fuel_75%": 440, "fuel_100%": 600},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AIM-9M", 1], 2: ["AIM-7M", 1],
                    3: ["AIM-7M", 1], 4: ["AIM-9M", 1],
                    5: ["330gal_tank", 1, 1100],
                },
                "devices": {},
                "pylon_count": 9,
                "fuel_internal_max": 4925, "flare": 60, "chaff": 60, "gun_rounds": 578,
            },
        },

        "Strike": {
            "loadout_code": "FA18A-STRIKE-1",
            "tasks": ["Strike"],
            "attributes": ["Dumb bomb", "Area"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 820, "reference_altitude": 6000,
                "altitude_max": 12000, "altitude_min": 300,
                "range": {"fuel_25%": 160, "fuel_50%": 340, "fuel_75%": 520, "fuel_100%": 700},
            },
            "attack": {
                "speed": 900, "reference_altitude": 3000,
                "altitude_max": 8000, "altitude_min": 300,
                "range": {"fuel_25%": 120, "fuel_50%": 260, "fuel_75%": 400, "fuel_100%": 550},
            },
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {
                "Escort": True, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["Mk-83", 1], 2: ["Mk-82", 2],
                    3: ["Mk-82", 2], 4: ["Mk-83", 1],
                    5: ["AIM-9M", 1], 6: ["AIM-9M", 1],
                },
                "devices": {},
                "pylon_count": 9,
                "fuel_internal_max": 4925, "flare": 60, "chaff": 60, "gun_rounds": 578,
            },
        },

        "CAS": {
            "loadout_code": "FA18A-CAS-1",
            "tasks": ["CAS"],
            "attributes": ["Close Air Support"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 800, "reference_altitude": 3000,
                "altitude_max": 8000, "altitude_min": 100,
                "range": {"fuel_25%": 140, "fuel_50%": 300, "fuel_75%": 460, "fuel_100%": 620},
            },
            "attack": {
                "speed": 850, "reference_altitude": 1500,
                "altitude_max": 5000, "altitude_min": 100,
                "range": {"fuel_25%": 110, "fuel_50%": 230, "fuel_75%": 360, "fuel_100%": 490},
            },
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["Mk-82AIR", 2], 2: ["Mk-82AIR", 2],
                    3: ["AIM-9M", 1], 4: ["AIM-9M", 1],
                    5: ["330gal_tank", 1, 1100],
                },
                "devices": {},
                "pylon_count": 9,
                "fuel_internal_max": 4925, "flare": 60, "chaff": 60, "gun_rounds": 578,
            },
        },

        "Anti-Ship": {
            "loadout_code": "FA18A-ANTISHIP-1",
            "tasks": ["Anti_Ship"],
            "attributes": ["Anti-ship", "Stand-off"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 830, "reference_altitude": 6000,
                "altitude_max": 12000, "altitude_min": 100,
                "range": {"fuel_25%": 155, "fuel_50%": 330, "fuel_75%": 510, "fuel_100%": 690},
            },
            "attack": {
                "speed": 900, "reference_altitude": 100,
                "altitude_max": 5000, "altitude_min": 30,
                "range": {"fuel_25%": 110, "fuel_50%": 240, "fuel_75%": 370, "fuel_100%": 510},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": True, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AGM-84A", 1], 2: ["AGM-84A", 1],
                    3: ["AIM-9M", 1], 4: ["AIM-9M", 1],
                    5: ["330gal_tank", 1, 1100],
                },
                "devices": {},
                "pylon_count": 9,
                "fuel_internal_max": 4925, "flare": 60, "chaff": 60, "gun_rounds": 578,
            },
        },
    },

    # -------------------------------------------------------------------------
    "F/A-18C Hornet": {

        "Fleet CAP": {
            "loadout_code": "FA18C-CAP-1",
            "tasks": ["CAP", "Intercept"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True,
            "self_escort_capability": True,
            "cruise": {
                "speed": 850, "reference_altitude": 9000,
                "altitude_max": 15000, "altitude_min": 1000,
                "range": {"fuel_25%": 185, "fuel_50%": 385, "fuel_75%": 590, "fuel_100%": 790},
            },
            "attack": {
                "speed": 1800, "reference_altitude": 10000,
                "altitude_max": 15000, "altitude_min": 500,
                "range": {"fuel_25%": 140, "fuel_50%": 290, "fuel_75%": 450, "fuel_100%": 610},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AIM-9M", 1], 2: ["AIM-7M", 1],
                    3: ["AIM-7M", 1], 4: ["AIM-7M", 1],
                    5: ["AIM-9M", 1], 6: ["330gal_tank", 1, 1100],
                },
                "devices": {},
                "pylon_count": 9,
                "fuel_internal_max": 4925, "flare": 60, "chaff": 60, "gun_rounds": 578,
            },
        },

        "SEAD": {
            "loadout_code": "FA18C-SEAD-1",
            "tasks": ["SEAD"],
            "attributes": ["Anti-radar", "Stand-off"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 840, "reference_altitude": 7000,
                "altitude_max": 14000, "altitude_min": 1000,
                "range": {"fuel_25%": 170, "fuel_50%": 360, "fuel_75%": 550, "fuel_100%": 740},
            },
            "attack": {
                "speed": 950, "reference_altitude": 4000,
                "altitude_max": 12000, "altitude_min": 500,
                "range": {"fuel_25%": 130, "fuel_50%": 275, "fuel_75%": 420, "fuel_100%": 580},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AGM-88", 1], 2: ["AGM-88", 1],
                    3: ["AIM-9M", 1], 4: ["AIM-9M", 1],
                    5: ["AIM-7M", 1], 6: ["330gal_tank", 1, 1100],
                },
                "devices": {},
                "pylon_count": 9,
                "fuel_internal_max": 4925, "flare": 60, "chaff": 60, "gun_rounds": 578,
            },
        },

        "Anti-Ship": {
            "loadout_code": "FA18C-ANTISHIP-1",
            "tasks": ["Anti_Ship"],
            "attributes": ["Anti-ship", "Stand-off"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 830, "reference_altitude": 6000,
                "altitude_max": 12000, "altitude_min": 100,
                "range": {"fuel_25%": 160, "fuel_50%": 340, "fuel_75%": 520, "fuel_100%": 700},
            },
            "attack": {
                "speed": 900, "reference_altitude": 100,
                "altitude_max": 5000, "altitude_min": 30,
                "range": {"fuel_25%": 115, "fuel_50%": 245, "fuel_75%": 380, "fuel_100%": 520},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": True, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AGM-84A", 1], 2: ["AGM-84A", 1],
                    3: ["AIM-9M", 1], 4: ["AIM-9M", 1],
                    5: ["330gal_tank", 1, 1100],
                },
                "devices": {},
                "pylon_count": 9,
                "fuel_internal_max": 4925, "flare": 60, "chaff": 60, "gun_rounds": 578,
            },
        },

        "Strike": {
            "loadout_code": "FA18C-STRIKE-1",
            "tasks": ["Strike"],
            "attributes": ["Dumb bomb", "Area"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 820, "reference_altitude": 6000,
                "altitude_max": 12000, "altitude_min": 300,
                "range": {"fuel_25%": 155, "fuel_50%": 330, "fuel_75%": 510, "fuel_100%": 690},
            },
            "attack": {
                "speed": 900, "reference_altitude": 3000,
                "altitude_max": 8000, "altitude_min": 300,
                "range": {"fuel_25%": 115, "fuel_50%": 250, "fuel_75%": 385, "fuel_100%": 530},
            },
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {
                "Escort": True, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["Mk-83", 1], 2: ["Mk-83", 1],
                    3: ["Mk-82", 2], 4: ["Mk-82", 2],
                    5: ["AIM-9M", 1], 6: ["AIM-9M", 1],
                },
                "devices": {},
                "pylon_count": 9,
                "fuel_internal_max": 4925, "flare": 60, "chaff": 60, "gun_rounds": 578,
            },
        },
    },

    # -------------------------------------------------------------------------
    "F/A-18C Lot 20": {

        "Fleet CAP": {
            "loadout_code": "FA18CLOT20-CAP-1",
            "tasks": ["CAP", "Intercept"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True,
            "self_escort_capability": True,
            "cruise": {
                "speed": 860, "reference_altitude": 9000,
                "altitude_max": 15000, "altitude_min": 1000,
                "range": {"fuel_25%": 190, "fuel_50%": 395, "fuel_75%": 600, "fuel_100%": 810},
            },
            "attack": {
                "speed": 1800, "reference_altitude": 10000,
                "altitude_max": 15000, "altitude_min": 500,
                "range": {"fuel_25%": 145, "fuel_50%": 300, "fuel_75%": 460, "fuel_100%": 625},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AIM-9X", 1], 2: ["AIM-7MH", 1],
                    3: ["AIM-7MH", 1], 4: ["AIM-7MH", 1],
                    5: ["AIM-9X", 1], 6: ["330gal_tank", 1, 1100],
                },
                "devices": {},
                "pylon_count": 9,
                "fuel_internal_max": 4925, "flare": 60, "chaff": 60, "gun_rounds": 578,
            },
        },

        "Pinpoint Strike": {
            "loadout_code": "FA18CLOT20-PSTRIKE-1",
            "tasks": ["Pinpoint_Strike"],
            "attributes": ["Precision", "Laser-guided"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 840, "reference_altitude": 7000,
                "altitude_max": 12000, "altitude_min": 300,
                "range": {"fuel_25%": 160, "fuel_50%": 340, "fuel_75%": 520, "fuel_100%": 700},
            },
            "attack": {
                "speed": 900, "reference_altitude": 4000,
                "altitude_max": 9000, "altitude_min": 300,
                "range": {"fuel_25%": 120, "fuel_50%": 260, "fuel_75%": 400, "fuel_100%": 550},
            },
            "usability": {"day": True, "night": True, "adverse_weather": False},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["GBU-16", 1], 2: ["GBU-16", 1],
                    3: ["GBU-12", 1], 4: ["GBU-12", 1],
                    5: ["AIM-9X", 1], 6: ["AIM-9X", 1],
                    7: ["330gal_tank", 1, 1100],
                },
                "devices": {1: ["Litening_pod", 1]},
                "pylon_count": 9,
                "fuel_internal_max": 4925, "flare": 60, "chaff": 60, "gun_rounds": 578,
            },
        },

        "SEAD": {
            "loadout_code": "FA18CLOT20-SEAD-1",
            "tasks": ["SEAD"],
            "attributes": ["Anti-radar", "Stand-off"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 840, "reference_altitude": 7000,
                "altitude_max": 14000, "altitude_min": 1000,
                "range": {"fuel_25%": 175, "fuel_50%": 365, "fuel_75%": 560, "fuel_100%": 755},
            },
            "attack": {
                "speed": 950, "reference_altitude": 4000,
                "altitude_max": 12000, "altitude_min": 500,
                "range": {"fuel_25%": 130, "fuel_50%": 280, "fuel_75%": 430, "fuel_100%": 590},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AGM-88", 1], 2: ["AGM-88", 1],
                    3: ["AIM-9X", 1], 4: ["AIM-9X", 1],
                    5: ["AIM-7MH", 1], 6: ["330gal_tank", 1, 1100],
                },
                "devices": {},
                "pylon_count": 9,
                "fuel_internal_max": 4925, "flare": 60, "chaff": 60, "gun_rounds": 578,
            },
        },

        "Anti-Ship": {
            "loadout_code": "FA18CLOT20-ANTISHIP-1",
            "tasks": ["Anti_Ship"],
            "attributes": ["Anti-ship", "Stand-off"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 830, "reference_altitude": 6000,
                "altitude_max": 12000, "altitude_min": 100,
                "range": {"fuel_25%": 160, "fuel_50%": 345, "fuel_75%": 530, "fuel_100%": 715},
            },
            "attack": {
                "speed": 900, "reference_altitude": 100,
                "altitude_max": 5000, "altitude_min": 30,
                "range": {"fuel_25%": 115, "fuel_50%": 250, "fuel_75%": 385, "fuel_100%": 530},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": True, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AGM-84A", 1], 2: ["AGM-84A", 1],
                    3: ["AIM-9X", 1], 4: ["AIM-9X", 1],
                    5: ["330gal_tank", 1, 1100],
                },
                "devices": {},
                "pylon_count": 9,
                "fuel_internal_max": 4925, "flare": 60, "chaff": 60, "gun_rounds": 578,
            },
        },

        "Strike": {
            "loadout_code": "FA18CLOT20-STRIKE-1",
            "tasks": ["Strike"],
            "attributes": ["Area attack", "Unguided"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 830, "reference_altitude": 6000,
                "altitude_max": 12000, "altitude_min": 200,
                "range": {"fuel_25%": 155, "fuel_50%": 330, "fuel_75%": 505, "fuel_100%": 680},
            },
            "attack": {
                "speed": 850, "reference_altitude": 3000,
                "altitude_max": 8000, "altitude_min": 200,
                "range": {"fuel_25%": 115, "fuel_50%": 245, "fuel_75%": 375, "fuel_100%": 510},
            },
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["Mk-83", 2], 2: ["Mk-83", 2],
                    3: ["Mk-82", 3], 4: ["Mk-82", 3],
                    5: ["AIM-9X", 1], 6: ["AIM-9X", 1],
                    7: ["330gal_tank", 1, 1100],
                },
                "devices": {},
                "pylon_count": 9,
                "fuel_internal_max": 4925, "flare": 60, "chaff": 60, "gun_rounds": 578,
            },
        },
    },

    # -------------------------------------------------------------------------
    "F-4E Phantom II": {

        "Air Superiority": {
            "loadout_code": "F4E-CAP-1",
            "tasks": ["CAP"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True,
            "self_escort_capability": True,
            "cruise": {
                "speed": 870, "reference_altitude": 9000,
                "altitude_max": 18000, "altitude_min": 1000,
                "range": {"fuel_25%": 200, "fuel_50%": 430, "fuel_75%": 660, "fuel_100%": 900},
            },
            "attack": {
                "speed": 2300, "reference_altitude": 12000,
                "altitude_max": 18000, "altitude_min": 1000,
                "range": {"fuel_25%": 145, "fuel_50%": 310, "fuel_75%": 475, "fuel_100%": 650},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AIM-7E", 1], 2: ["AIM-7E", 1],
                    3: ["AIM-7E", 1], 4: ["AIM-7E", 1],
                    5: ["AIM-9P", 1], 6: ["AIM-9P", 1],
                    7: ["AIM-9P", 1], 8: ["AIM-9P", 1],
                    9: ["600gal_tank", 1, 2000],
                },
                "devices": {},
                "pylon_count": 9,
                "fuel_internal_max": 5980, "flare": 0, "chaff": 0, "gun_rounds": 639,
            },
        },

        "Strike": {
            "loadout_code": "F4E-STRIKE-1",
            "tasks": ["Strike"],
            "attributes": ["Dumb bomb", "Area"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 850, "reference_altitude": 7000,
                "altitude_max": 12000, "altitude_min": 300,
                "range": {"fuel_25%": 175, "fuel_50%": 375, "fuel_75%": 575, "fuel_100%": 780},
            },
            "attack": {
                "speed": 950, "reference_altitude": 3000,
                "altitude_max": 8000, "altitude_min": 300,
                "range": {"fuel_25%": 130, "fuel_50%": 280, "fuel_75%": 430, "fuel_100%": 590},
            },
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {
                "Escort": True, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["Mk-83", 1], 2: ["Mk-83", 1],
                    3: ["Mk-83", 1], 4: ["Mk-83", 1],
                    5: ["AIM-9P", 1], 6: ["AIM-9P", 1],
                    7: ["600gal_tank", 1, 2000],
                },
                "devices": {},
                "pylon_count": 9,
                "fuel_internal_max": 5980, "flare": 0, "chaff": 0, "gun_rounds": 639,
            },
        },

        "CAS": {
            "loadout_code": "F4E-CAS-1",
            "tasks": ["CAS"],
            "attributes": ["Close Air Support"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 830, "reference_altitude": 3000,
                "altitude_max": 8000, "altitude_min": 100,
                "range": {"fuel_25%": 160, "fuel_50%": 345, "fuel_75%": 530, "fuel_100%": 720},
            },
            "attack": {
                "speed": 900, "reference_altitude": 1500,
                "altitude_max": 5000, "altitude_min": 100,
                "range": {"fuel_25%": 120, "fuel_50%": 260, "fuel_75%": 400, "fuel_100%": 550},
            },
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": True, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["Mk-82", 2], 2: ["Mk-82", 2],
                    3: ["Mk-82AIR", 2], 4: ["Mk-82AIR", 2],
                    5: ["AIM-9P", 1], 6: ["AIM-9P", 1],
                },
                "devices": {},
                "pylon_count": 9,
                "fuel_internal_max": 5980, "flare": 0, "chaff": 0, "gun_rounds": 639,
            },
        },
    },

    # -------------------------------------------------------------------------
    "F-5E Tiger II": {

        "Air Combat": {
            "loadout_code": "F5E-CAP-1",
            "tasks": ["CAP", "Intercept"],
            "attributes": [],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 900, "reference_altitude": 8000,
                "altitude_max": 15000, "altitude_min": 500,
                "range": {"fuel_25%": 130, "fuel_50%": 280, "fuel_75%": 430, "fuel_100%": 580},
            },
            "attack": {
                "speed": 1700, "reference_altitude": 10000,
                "altitude_max": 15000, "altitude_min": 500,
                "range": {"fuel_25%": 95, "fuel_50%": 205, "fuel_75%": 315, "fuel_100%": 430},
            },
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AIM-9L", 1], 2: ["AIM-9L", 1],
                    3: ["275gal_tank", 1, 900],
                },
                "devices": {},
                "pylon_count": 7,
                "fuel_internal_max": 2600, "flare": 30, "chaff": 30, "gun_rounds": 280,
            },
        },

        "Light CAP": {
            "loadout_code": "F5E-CAP-2",
            "tasks": ["CAP", "Intercept"],
            "attributes": [],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 950, "reference_altitude": 9000,
                "altitude_max": 15000, "altitude_min": 500,
                "range": {"fuel_25%": 145, "fuel_50%": 305, "fuel_75%": 465, "fuel_100%": 630},
            },
            "attack": {
                "speed": 1700, "reference_altitude": 10000,
                "altitude_max": 15000, "altitude_min": 500,
                "range": {"fuel_25%": 105, "fuel_50%": 225, "fuel_75%": 345, "fuel_100%": 465},
            },
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AIM-9P5", 1], 2: ["AIM-9P5", 1],
                },
                "devices": {},
                "pylon_count": 7,
                "fuel_internal_max": 2600, "flare": 30, "chaff": 30, "gun_rounds": 280,
            },
        },
    },

    # -------------------------------------------------------------------------
    "F-86E Sabre": {

        "Gun Fighter": {
            "loadout_code": "F86E-CAP-1",
            "tasks": ["CAP", "Intercept"],
            "attributes": [],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 830, "reference_altitude": 9000,
                "altitude_max": 15000, "altitude_min": 1000,
                "range": {"fuel_25%": 90, "fuel_50%": 190, "fuel_75%": 295, "fuel_100%": 400},
            },
            "attack": {
                "speed": 1100, "reference_altitude": 9000,
                "altitude_max": 15000, "altitude_min": 1000,
                "range": {"fuel_25%": 65, "fuel_50%": 140, "fuel_75%": 215, "fuel_100%": 295},
            },
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {},
                "devices": {},
                "pylon_count": 2,
                "fuel_internal_max": 1370, "flare": 0, "chaff": 0, "gun_rounds": 1600,
            },
        },
    },

    # -------------------------------------------------------------------------
    "F-16A Fighting Falcon": {

        "CAP": {
            "loadout_code": "F16A-CAP-1",
            "tasks": ["CAP", "Intercept"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True,
            "self_escort_capability": True,
            "cruise": {
                "speed": 870, "reference_altitude": 9000,
                "altitude_max": 16000, "altitude_min": 1000,
                "range": {"fuel_25%": 140, "fuel_50%": 295, "fuel_75%": 455, "fuel_100%": 610},
            },
            "attack": {
                "speed": 2100, "reference_altitude": 12000,
                "altitude_max": 16000, "altitude_min": 500,
                "range": {"fuel_25%": 100, "fuel_50%": 215, "fuel_75%": 330, "fuel_100%": 450},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AIM-9M", 1], 2: ["AIM-7P", 1],
                    3: ["AIM-7P", 1], 4: ["AIM-9M", 1],
                    5: ["370gal_tank", 1, 1200],
                },
                "devices": {},
                "pylon_count": 9,
                "fuel_internal_max": 3200, "flare": 60, "chaff": 60, "gun_rounds": 511,
            },
        },

        "Strike": {
            "loadout_code": "F16A-STRIKE-1",
            "tasks": ["Strike"],
            "attributes": ["Dumb bomb", "Area"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 840, "reference_altitude": 6000,
                "altitude_max": 12000, "altitude_min": 300,
                "range": {"fuel_25%": 125, "fuel_50%": 265, "fuel_75%": 405, "fuel_100%": 550},
            },
            "attack": {
                "speed": 950, "reference_altitude": 3000,
                "altitude_max": 8000, "altitude_min": 300,
                "range": {"fuel_25%": 90, "fuel_50%": 195, "fuel_75%": 300, "fuel_100%": 410},
            },
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {
                "Escort": True, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["Mk-83", 1], 2: ["Mk-83", 1],
                    3: ["AIM-9M", 1], 4: ["AIM-9M", 1],
                    5: ["370gal_tank", 1, 1200],
                },
                "devices": {},
                "pylon_count": 9,
                "fuel_internal_max": 3200, "flare": 60, "chaff": 60, "gun_rounds": 511,
            },
        },

        "SEAD": {
            "loadout_code": "F16A-SEAD-1",
            "tasks": ["SEAD"],
            "attributes": ["Anti-radar"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 850, "reference_altitude": 7000,
                "altitude_max": 14000, "altitude_min": 500,
                "range": {"fuel_25%": 135, "fuel_50%": 280, "fuel_75%": 430, "fuel_100%": 585},
            },
            "attack": {
                "speed": 950, "reference_altitude": 4000,
                "altitude_max": 12000, "altitude_min": 500,
                "range": {"fuel_25%": 97, "fuel_50%": 208, "fuel_75%": 318, "fuel_100%": 435},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AGM-45", 1], 2: ["AGM-45", 1],
                    3: ["AIM-9M", 1], 4: ["AIM-9M", 1],
                    5: ["370gal_tank", 1, 1200],
                },
                "devices": {},
                "pylon_count": 9,
                "fuel_internal_max": 3200, "flare": 60, "chaff": 60, "gun_rounds": 511,
            },
        },
    },

    # -------------------------------------------------------------------------
    "F-16A MLU": {

        "CAP": {
            "loadout_code": "F16AMLU-CAP-1",
            "tasks": ["CAP", "Intercept"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True,
            "self_escort_capability": True,
            "cruise": {
                "speed": 880, "reference_altitude": 9000,
                "altitude_max": 16000, "altitude_min": 1000,
                "range": {"fuel_25%": 145, "fuel_50%": 305, "fuel_75%": 465, "fuel_100%": 630},
            },
            "attack": {
                "speed": 2100, "reference_altitude": 12000,
                "altitude_max": 16000, "altitude_min": 500,
                "range": {"fuel_25%": 105, "fuel_50%": 225, "fuel_75%": 345, "fuel_100%": 465},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AIM-9M", 1], 2: ["AIM-7MH", 1],
                    3: ["AIM-7MH", 1], 4: ["AIM-9M", 1],
                    5: ["370gal_tank", 1, 1200],
                },
                "devices": {},
                "pylon_count": 9,
                "fuel_internal_max": 3200, "flare": 60, "chaff": 60, "gun_rounds": 511,
            },
        },

        "Strike": {
            "loadout_code": "F16AMLU-STRIKE-1",
            "tasks": ["Strike"],
            "attributes": ["Dumb bomb"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 840, "reference_altitude": 6000,
                "altitude_max": 12000, "altitude_min": 300,
                "range": {"fuel_25%": 130, "fuel_50%": 275, "fuel_75%": 420, "fuel_100%": 570},
            },
            "attack": {
                "speed": 950, "reference_altitude": 3000,
                "altitude_max": 8000, "altitude_min": 300,
                "range": {"fuel_25%": 94, "fuel_50%": 200, "fuel_75%": 310, "fuel_100%": 420},
            },
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {
                "Escort": True, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["Mk-83", 1], 2: ["Mk-82", 2],
                    3: ["AIM-9M", 1], 4: ["AIM-9M", 1],
                    5: ["370gal_tank", 1, 1200],
                },
                "devices": {},
                "pylon_count": 9,
                "fuel_internal_max": 3200, "flare": 60, "chaff": 60, "gun_rounds": 511,
            },
        },

        "SEAD": {
            "loadout_code": "F16AMLU-SEAD-1",
            "tasks": ["SEAD"],
            "attributes": ["Anti-radar"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 850, "reference_altitude": 7000,
                "altitude_max": 14000, "altitude_min": 500,
                "range": {"fuel_25%": 138, "fuel_50%": 290, "fuel_75%": 445, "fuel_100%": 600},
            },
            "attack": {
                "speed": 950, "reference_altitude": 4000,
                "altitude_max": 12000, "altitude_min": 500,
                "range": {"fuel_25%": 100, "fuel_50%": 215, "fuel_75%": 330, "fuel_100%": 450},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AGM-88", 1], 2: ["AGM-88", 1],
                    3: ["AIM-9M", 1], 4: ["AIM-9M", 1],
                    5: ["370gal_tank", 1, 1200],
                },
                "devices": {},
                "pylon_count": 9,
                "fuel_internal_max": 3200, "flare": 60, "chaff": 60, "gun_rounds": 511,
            },
        },
    },

    # -------------------------------------------------------------------------
    "F-16C Block 52d": {

        "CAP": {
            "loadout_code": "F16C52D-CAP-1",
            "tasks": ["CAP"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True,
            "self_escort_capability": True,
            "cruise": {
                "speed": 890, "reference_altitude": 9000,
                "altitude_max": 16000, "altitude_min": 1000,
                "range": {"fuel_25%": 148, "fuel_50%": 312, "fuel_75%": 476, "fuel_100%": 640},
            },
            "attack": {
                "speed": 2100, "reference_altitude": 12000,
                "altitude_max": 16000, "altitude_min": 500,
                "range": {"fuel_25%": 108, "fuel_50%": 230, "fuel_75%": 352, "fuel_100%": 475},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AIM-9M", 1], 2: ["AIM-7M", 1],
                    3: ["AIM-7M", 1], 4: ["AIM-9M", 1],
                    5: ["370gal_tank", 1, 1200],
                },
                "devices": {},
                "pylon_count": 9,
                "fuel_internal_max": 3200, "flare": 60, "chaff": 60, "gun_rounds": 511,
            },
        },

        "Pinpoint Strike": {
            "loadout_code": "F16C52D-PSTRIKE-1",
            "tasks": ["Pinpoint_Strike"],
            "attributes": ["Precision", "Laser-guided"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 840, "reference_altitude": 7000,
                "altitude_max": 12000, "altitude_min": 300,
                "range": {"fuel_25%": 128, "fuel_50%": 270, "fuel_75%": 415, "fuel_100%": 560},
            },
            "attack": {
                "speed": 900, "reference_altitude": 4000,
                "altitude_max": 9000, "altitude_min": 300,
                "range": {"fuel_25%": 93, "fuel_50%": 197, "fuel_75%": 303, "fuel_100%": 410},
            },
            "usability": {"day": True, "night": True, "adverse_weather": False},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["GBU-12", 1], 2: ["GBU-12", 1],
                    3: ["AIM-9M", 1], 4: ["AIM-9M", 1],
                    5: ["370gal_tank", 1, 1200],
                },
                "devices": {1: ["LANTIRN_pod", 1]},
                "pylon_count": 9,
                "fuel_internal_max": 3200, "flare": 60, "chaff": 60, "gun_rounds": 511,
            },
        },

        "SEAD": {
            "loadout_code": "F16C52D-SEAD-1",
            "tasks": ["SEAD"],
            "attributes": ["Anti-radar"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 860, "reference_altitude": 7000,
                "altitude_max": 14000, "altitude_min": 500,
                "range": {"fuel_25%": 140, "fuel_50%": 295, "fuel_75%": 452, "fuel_100%": 610},
            },
            "attack": {
                "speed": 1000, "reference_altitude": 5000,
                "altitude_max": 12000, "altitude_min": 500,
                "range": {"fuel_25%": 102, "fuel_50%": 218, "fuel_75%": 334, "fuel_100%": 450},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AGM-88", 1], 2: ["AGM-88", 1],
                    3: ["AIM-9M", 1], 4: ["AIM-9M", 1],
                    5: ["370gal_tank", 1, 1200],
                },
                "devices": {},
                "pylon_count": 9,
                "fuel_internal_max": 3200, "flare": 60, "chaff": 60, "gun_rounds": 511,
            },
        },

        "Strike": {
            "loadout_code": "F16C52D-STRIKE-1",
            "tasks": ["Strike"],
            "attributes": ["Area attack", "Unguided"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 840, "reference_altitude": 6000,
                "altitude_max": 12000, "altitude_min": 200,
                "range": {"fuel_25%": 135, "fuel_50%": 285, "fuel_75%": 437, "fuel_100%": 590},
            },
            "attack": {
                "speed": 850, "reference_altitude": 3000,
                "altitude_max": 8000, "altitude_min": 200,
                "range": {"fuel_25%": 98, "fuel_50%": 208, "fuel_75%": 319, "fuel_100%": 430},
            },
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["Mk-83", 2], 2: ["Mk-83", 2],
                    3: ["Mk-82", 3], 4: ["Mk-82", 3],
                    5: ["AIM-9M", 1], 6: ["AIM-9M", 1],
                    7: ["370gal_tank", 1, 1200],
                },
                "devices": {},
                "pylon_count": 9,
                "fuel_internal_max": 3200, "flare": 60, "chaff": 60, "gun_rounds": 511,
            },
        },
    },

    # -------------------------------------------------------------------------
    "F-16CM Block 50": {

        "CAP": {
            "loadout_code": "F16CM50-CAP-1",
            "tasks": ["CAP"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True,
            "self_escort_capability": True,
            "cruise": {
                "speed": 900, "reference_altitude": 9000,
                "altitude_max": 16000, "altitude_min": 1000,
                "range": {"fuel_25%": 150, "fuel_50%": 318, "fuel_75%": 485, "fuel_100%": 652},
            },
            "attack": {
                "speed": 2100, "reference_altitude": 12000,
                "altitude_max": 16000, "altitude_min": 500,
                "range": {"fuel_25%": 110, "fuel_50%": 234, "fuel_75%": 358, "fuel_100%": 483},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AIM-9X", 1], 2: ["AIM-7MH", 1],
                    3: ["AIM-7MH", 1], 4: ["AIM-9X", 1],
                    5: ["370gal_tank", 1, 1200],
                },
                "devices": {},
                "pylon_count": 9,
                "fuel_internal_max": 3200, "flare": 60, "chaff": 60, "gun_rounds": 511,
            },
        },

        "Pinpoint Strike": {
            "loadout_code": "F16CM50-PSTRIKE-1",
            "tasks": ["Pinpoint_Strike"],
            "attributes": ["Precision", "Laser-guided"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 850, "reference_altitude": 7000,
                "altitude_max": 12000, "altitude_min": 300,
                "range": {"fuel_25%": 132, "fuel_50%": 278, "fuel_75%": 425, "fuel_100%": 573},
            },
            "attack": {
                "speed": 900, "reference_altitude": 4000,
                "altitude_max": 9000, "altitude_min": 300,
                "range": {"fuel_25%": 96, "fuel_50%": 203, "fuel_75%": 311, "fuel_100%": 420},
            },
            "usability": {"day": True, "night": True, "adverse_weather": False},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["GBU-12", 1], 2: ["GBU-12", 1],
                    3: ["AIM-9X", 1], 4: ["AIM-9X", 1],
                    5: ["370gal_tank", 1, 1200],
                },
                "devices": {1: ["HTS_pod", 1]},
                "pylon_count": 9,
                "fuel_internal_max": 3200, "flare": 60, "chaff": 60, "gun_rounds": 511,
            },
        },

        "SEAD/DEAD": {
            "loadout_code": "F16CM50-SEAD-1",
            "tasks": ["SEAD"],
            "attributes": ["Anti-radar", "Stand-off"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 870, "reference_altitude": 7000,
                "altitude_max": 14000, "altitude_min": 500,
                "range": {"fuel_25%": 143, "fuel_50%": 302, "fuel_75%": 461, "fuel_100%": 622},
            },
            "attack": {
                "speed": 1000, "reference_altitude": 5000,
                "altitude_max": 12000, "altitude_min": 500,
                "range": {"fuel_25%": 104, "fuel_50%": 222, "fuel_75%": 340, "fuel_100%": 458},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AGM-88", 1], 2: ["AGM-88", 1],
                    3: ["AIM-9X", 1], 4: ["AIM-9X", 1],
                    5: ["370gal_tank", 1, 1200],
                },
                "devices": {1: ["HTS_pod", 1]},
                "pylon_count": 9,
                "fuel_internal_max": 3200, "flare": 60, "chaff": 60, "gun_rounds": 511,
            },
        },

        "Strike": {
            "loadout_code": "F16CM50-STRIKE-1",
            "tasks": ["Strike"],
            "attributes": ["Area", "Dumb bomb"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 840, "reference_altitude": 6000,
                "altitude_max": 12000, "altitude_min": 300,
                "range": {"fuel_25%": 130, "fuel_50%": 274, "fuel_75%": 420, "fuel_100%": 567},
            },
            "attack": {
                "speed": 950, "reference_altitude": 3000,
                "altitude_max": 8000, "altitude_min": 300,
                "range": {"fuel_25%": 94, "fuel_50%": 200, "fuel_75%": 307, "fuel_100%": 415},
            },
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {
                "Escort": True, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["Mk-83", 1], 2: ["Mk-83", 1],
                    3: ["Mk-82", 2], 4: ["AIM-9X", 1],
                    5: ["370gal_tank", 1, 1200],
                },
                "devices": {},
                "pylon_count": 9,
                "fuel_internal_max": 3200, "flare": 60, "chaff": 60, "gun_rounds": 511,
            },
        },
    },


    # =========================================================================
    # US ATTACKERS
    # =========================================================================

    # -------------------------------------------------------------------------
    "A-10A Thunderbolt II": {

        "Ground Pounding": {
            "loadout_code": "A10A-CAS-1",
            "tasks": ["CAS"],
            "attributes": ["Close Air Support", "Anti-armor"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": False,
            "cruise": {
                "speed": 520, "reference_altitude": 3000,
                "altitude_max": 8000, "altitude_min": 100,
                "range": {"fuel_25%": 200, "fuel_50%": 420, "fuel_75%": 640, "fuel_100%": 860},
            },
            "attack": {
                "speed": 600, "reference_altitude": 1000,
                "altitude_max": 4000, "altitude_min": 30,
                "range": {"fuel_25%": 145, "fuel_50%": 310, "fuel_75%": 475, "fuel_100%": 640},
            },
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {
                "Escort": True, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["Mk-82", 2], 2: ["Mk-82", 2],
                    3: ["Mk-82AIR", 2], 4: ["Mk-82AIR", 2],
                    5: ["Hydra-70MK5", 1], 6: ["Hydra-70MK5", 1],
                },
                "devices": {},
                "pylon_count": 11,
                "fuel_internal_max": 4853, "flare": 120, "chaff": 120, "gun_rounds": 1174,
            },
        },

        "Anti-Armor Rockets": {
            "loadout_code": "A10A-CAS-2",
            "tasks": ["CAS"],
            "attributes": ["Close Air Support", "Anti-armor"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": False,
            "cruise": {
                "speed": 500, "reference_altitude": 2000,
                "altitude_max": 6000, "altitude_min": 50,
                "range": {"fuel_25%": 210, "fuel_50%": 440, "fuel_75%": 670, "fuel_100%": 900},
            },
            "attack": {
                "speed": 580, "reference_altitude": 500,
                "altitude_max": 3000, "altitude_min": 30,
                "range": {"fuel_25%": 155, "fuel_50%": 325, "fuel_75%": 500, "fuel_100%": 675},
            },
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {
                "Escort": True, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["Hydra-70MK5", 1], 2: ["Hydra-70MK5", 1],
                    3: ["Hydra-70MK5", 1], 4: ["Hydra-70MK5", 1],
                    5: ["Mk-20", 1], 6: ["Mk-20", 1],
                },
                "devices": {},
                "pylon_count": 11,
                "fuel_internal_max": 4853, "flare": 120, "chaff": 120, "gun_rounds": 1174,
            },
        },
    },

    # -------------------------------------------------------------------------
    "A-10C Thunderbolt II": {

        "Maverick/Gun CAS": {
            "loadout_code": "A10C-CAS-1",
            "tasks": ["CAS", "Pinpoint_Strike"],
            "attributes": ["Close Air Support", "Anti-armor", "Precision"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": False,
            "cruise": {
                "speed": 520, "reference_altitude": 3000,
                "altitude_max": 8000, "altitude_min": 100,
                "range": {"fuel_25%": 200, "fuel_50%": 420, "fuel_75%": 640, "fuel_100%": 860},
            },
            "attack": {
                "speed": 580, "reference_altitude": 1000,
                "altitude_max": 4000, "altitude_min": 30,
                "range": {"fuel_25%": 145, "fuel_50%": 310, "fuel_75%": 475, "fuel_100%": 640},
            },
            "usability": {"day": True, "night": True, "adverse_weather": False},
            "mandatory_support": {
                "Escort": True, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AGM-65D", 1], 2: ["AGM-65D", 1],
                    3: ["AGM-65D", 1], 4: ["AGM-65D", 1],
                    5: ["Mk-82AIR", 2], 6: ["Mk-82AIR", 2],
                    7: ["AIM-9M", 1],
                },
                "devices": {1: ["LITENING_AT", 1]},
                "pylon_count": 11,
                "fuel_internal_max": 4853, "flare": 120, "chaff": 120, "gun_rounds": 1174,
            },
        },

        "GBU Precision Strike": {
            "loadout_code": "A10C-PSTRIKE-1",
            "tasks": ["Strike", "Pinpoint_Strike"],
            "attributes": ["Precision", "Laser-guided"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": False,
            "cruise": {
                "speed": 510, "reference_altitude": 5000,
                "altitude_max": 10000, "altitude_min": 300,
                "range": {"fuel_25%": 195, "fuel_50%": 415, "fuel_75%": 630, "fuel_100%": 850},
            },
            "attack": {
                "speed": 560, "reference_altitude": 4000,
                "altitude_max": 8000, "altitude_min": 300,
                "range": {"fuel_25%": 142, "fuel_50%": 300, "fuel_75%": 460, "fuel_100%": 620},
            },
            "usability": {"day": True, "night": True, "adverse_weather": False},
            "mandatory_support": {
                "Escort": True, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["GBU-12", 1], 2: ["GBU-12", 1],
                    3: ["GBU-10", 1], 4: ["GBU-10", 1],
                    5: ["AIM-9M", 1],
                },
                "devices": {1: ["LITENING_AT", 1]},
                "pylon_count": 11,
                "fuel_internal_max": 4853, "flare": 120, "chaff": 120, "gun_rounds": 1174,
            },
        },

        "Heavy CAS": {
            "loadout_code": "A10C-CAS-2",
            "tasks": ["CAS"],
            "attributes": ["Close Air Support", "Area"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": False,
            "cruise": {
                "speed": 490, "reference_altitude": 2000,
                "altitude_max": 6000, "altitude_min": 50,
                "range": {"fuel_25%": 185, "fuel_50%": 395, "fuel_75%": 600, "fuel_100%": 810},
            },
            "attack": {
                "speed": 560, "reference_altitude": 500,
                "altitude_max": 3000, "altitude_min": 30,
                "range": {"fuel_25%": 135, "fuel_50%": 290, "fuel_75%": 445, "fuel_100%": 600},
            },
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {
                "Escort": True, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["Mk-82", 2], 2: ["Mk-82", 2],
                    3: ["Mk-82", 2], 4: ["Mk-82", 2],
                    5: ["CBU-52B", 1], 6: ["CBU-52B", 1],
                    7: ["AIM-9M", 1],
                },
                "devices": {},
                "pylon_count": 11,
                "fuel_internal_max": 4853, "flare": 120, "chaff": 120, "gun_rounds": 1174,
            },
        },
    },

    # -------------------------------------------------------------------------
    "A-10C II Thunderbolt II": {

        "Maverick/Gun CAS": {
            "loadout_code": "A10C2-CAS-1",
            "tasks": ["CAS", "Pinpoint_Strike"],
            "attributes": ["Close Air Support", "Anti-armor", "Precision"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": False,
            "cruise": {
                "speed": 520, "reference_altitude": 3000,
                "altitude_max": 8000, "altitude_min": 100,
                "range": {"fuel_25%": 205, "fuel_50%": 430, "fuel_75%": 655, "fuel_100%": 880},
            },
            "attack": {
                "speed": 580, "reference_altitude": 1000,
                "altitude_max": 4000, "altitude_min": 30,
                "range": {"fuel_25%": 150, "fuel_50%": 315, "fuel_75%": 485, "fuel_100%": 655},
            },
            "usability": {"day": True, "night": True, "adverse_weather": False},
            "mandatory_support": {
                "Escort": True, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AGM-65K", 1], 2: ["AGM-65K", 1],
                    3: ["AGM-65K", 1], 4: ["AGM-65K", 1],
                    5: ["GBU-12", 1], 6: ["GBU-12", 1],
                    7: ["AIM-9M", 1],
                },
                "devices": {1: ["Sniper_ATP", 1]},
                "pylon_count": 11,
                "fuel_internal_max": 4853, "flare": 120, "chaff": 120, "gun_rounds": 1174,
            },
        },

        "Precision Strike": {
            "loadout_code": "A10C2-PSTRIKE-1",
            "tasks": ["Strike", "Pinpoint_Strike"],
            "attributes": ["Precision", "Laser-guided"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": False,
            "cruise": {
                "speed": 510, "reference_altitude": 5000,
                "altitude_max": 10000, "altitude_min": 300,
                "range": {"fuel_25%": 200, "fuel_50%": 422, "fuel_75%": 644, "fuel_100%": 866},
            },
            "attack": {
                "speed": 560, "reference_altitude": 4000,
                "altitude_max": 9000, "altitude_min": 300,
                "range": {"fuel_25%": 146, "fuel_50%": 308, "fuel_75%": 472, "fuel_100%": 636},
            },
            "usability": {"day": True, "night": True, "adverse_weather": False},
            "mandatory_support": {
                "Escort": True, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["GBU-12", 1], 2: ["GBU-12", 1],
                    3: ["GBU-16", 1], 4: ["GBU-16", 1],
                    5: ["AIM-9M", 1],
                },
                "devices": {1: ["Sniper_ATP", 1]},
                "pylon_count": 11,
                "fuel_internal_max": 4853, "flare": 120, "chaff": 120, "gun_rounds": 1174,
            },
        },
    },

    # -------------------------------------------------------------------------
    "A-20G Havoc": {

        "Low Level Bomb Run": {
            "loadout_code": "A20G-STRIKE-1",
            "tasks": ["CAS", "Strike"],
            "attributes": ["Dumb bomb", "Area"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": False,
            "cruise": {
                "speed": 380, "reference_altitude": 3000,
                "altitude_max": 7000, "altitude_min": 100,
                "range": {"fuel_25%": 220, "fuel_50%": 465, "fuel_75%": 715, "fuel_100%": 960},
            },
            "attack": {
                "speed": 450, "reference_altitude": 1500,
                "altitude_max": 5000, "altitude_min": 50,
                "range": {"fuel_25%": 160, "fuel_50%": 340, "fuel_75%": 520, "fuel_100%": 700},
            },
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {
                "Escort": True, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": True, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["Mk-82", 2], 2: ["Mk-82", 2],
                    3: ["Mk-82", 2], 4: ["Mk-82", 2],
                },
                "devices": {},
                "pylon_count": 4,
                "fuel_internal_max": 2800, "flare": 0, "chaff": 0, "gun_rounds": 800,
            },
        },
    },

    # -------------------------------------------------------------------------
    "A-4E Skyhawk": {

        "Light Strike": {
            "loadout_code": "A4EC-STRIKE-1",
            "tasks": ["CAS", "Strike"],
            "attributes": ["Dumb bomb", "Area"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 820, "reference_altitude": 6000,
                "altitude_max": 12000, "altitude_min": 300,
                "range": {"fuel_25%": 160, "fuel_50%": 340, "fuel_75%": 520, "fuel_100%": 700},
            },
            "attack": {
                "speed": 900, "reference_altitude": 2000,
                "altitude_max": 6000, "altitude_min": 100,
                "range": {"fuel_25%": 115, "fuel_50%": 245, "fuel_75%": 380, "fuel_100%": 515},
            },
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {
                "Escort": True, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["Mk-82", 2], 2: ["Mk-83", 1],
                    3: ["Mk-83", 1], 4: ["AIM-9B", 1],
                    5: ["AIM-9B", 1],
                },
                "devices": {},
                "pylon_count": 5,
                "fuel_internal_max": 3720, "flare": 0, "chaff": 0, "gun_rounds": 200,
            },
        },

        "Anti-Ship": {
            "loadout_code": "A4EC-ANTISHIP-1",
            "tasks": ["Anti_Ship"],
            "attributes": ["Anti-ship"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {
                "speed": 820, "reference_altitude": 100,
                "altitude_max": 3000, "altitude_min": 30,
                "range": {"fuel_25%": 140, "fuel_50%": 300, "fuel_75%": 460, "fuel_100%": 620},
            },
            "attack": {
                "speed": 950, "reference_altitude": 30,
                "altitude_max": 1000, "altitude_min": 15,
                "range": {"fuel_25%": 100, "fuel_50%": 215, "fuel_75%": 330, "fuel_100%": 450},
            },
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {
                "Escort": True, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["Mk-83", 1], 2: ["Mk-83", 1],
                    3: ["AIM-9B", 1], 4: ["AIM-9B", 1],
                    5: ["150gal_tank", 1, 500],
                },
                "devices": {},
                "pylon_count": 5,
                "fuel_internal_max": 3720, "flare": 0, "chaff": 0, "gun_rounds": 200,
            },
        },
    },

    # =========================================================================
    # US BOMBERS & MARITIME
    # =========================================================================

    # -------------------------------------------------------------------------
    "F-117 Nighthawk": {

        "Stealth Strike GBU-27": {
            "loadout_code": "F117-PSTRIKE-1",
            "tasks": ["Pinpoint_Strike"],
            "attributes": ["Precision", "Stealth", "Laser-guided", "Bunker buster"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": False,
            "cruise": {
                "speed": 920, "reference_altitude": 10000,
                "altitude_max": 14000, "altitude_min": 5000,
                "range": {"fuel_25%": 260, "fuel_50%": 550, "fuel_75%": 840, "fuel_100%": 1130},
            },
            "attack": {
                "speed": 950, "reference_altitude": 8000,
                "altitude_max": 14000, "altitude_min": 3000,
                "range": {"fuel_25%": 190, "fuel_50%": 400, "fuel_75%": 615, "fuel_100%": 830},
            },
            "usability": {"day": True, "night": True, "adverse_weather": False},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    "bay_1": ["GBU-27", 1],
                    "bay_2": ["GBU-27", 1],
                },
                "devices": {},
                "pylon_count": 2,
                "fuel_internal_max": 8200, "flare": 0, "chaff": 0, "gun_rounds": 0,
            },
        },

        "Stealth Strike GBU-10": {
            "loadout_code": "F117-PSTRIKE-2",
            "tasks": ["Pinpoint_Strike"],
            "attributes": ["Precision", "Stealth", "Laser-guided"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": False,
            "cruise": {
                "speed": 920, "reference_altitude": 10000,
                "altitude_max": 14000, "altitude_min": 5000,
                "range": {"fuel_25%": 265, "fuel_50%": 558, "fuel_75%": 852, "fuel_100%": 1145},
            },
            "attack": {
                "speed": 950, "reference_altitude": 8000,
                "altitude_max": 14000, "altitude_min": 3000,
                "range": {"fuel_25%": 193, "fuel_50%": 408, "fuel_75%": 623, "fuel_100%": 838},
            },
            "usability": {"day": True, "night": True, "adverse_weather": False},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    "bay_1": ["GBU-10", 1],
                    "bay_2": ["GBU-10", 1],
                },
                "devices": {},
                "pylon_count": 2,
                "fuel_internal_max": 8200, "flare": 0, "chaff": 0, "gun_rounds": 0,
            },
        },
    },

    # -------------------------------------------------------------------------
    "B-1B Lancer": {

        "Carpet Bomb": {
            "loadout_code": "B1B-STRIKE-1",
            "tasks": ["Strike"],
            "attributes": ["Area", "Dumb bomb", "Heavy payload"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": False,
            "cruise": {
                "speed": 850, "reference_altitude": 12000,
                "altitude_max": 16000, "altitude_min": 100,
                "range": {"fuel_25%": 900, "fuel_50%": 1900, "fuel_75%": 2900, "fuel_100%": 3800},
            },
            "attack": {
                "speed": 1200, "reference_altitude": 3000,
                "altitude_max": 12000, "altitude_min": 100,
                "range": {"fuel_25%": 650, "fuel_50%": 1380, "fuel_75%": 2100, "fuel_100%": 2800},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": True, "SEAD": True, "Escort_Jammer": True,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    "bay_1": ["Mk-82", 28],
                    "bay_2": ["Mk-82", 28],
                    "bay_3": ["Mk-82", 28],
                },
                "devices": {},
                "pylon_count": 3,
                "fuel_internal_max": 88000, "flare": 0, "chaff": 0, "gun_rounds": 0,
            },
        },

        "Precision Strike": {
            "loadout_code": "B1B-PSTRIKE-1",
            "tasks": ["Pinpoint_Strike"],
            "attributes": ["Precision", "Laser-guided"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": False,
            "cruise": {
                "speed": 870, "reference_altitude": 12000,
                "altitude_max": 16000, "altitude_min": 3000,
                "range": {"fuel_25%": 940, "fuel_50%": 1980, "fuel_75%": 3020, "fuel_100%": 4050},
            },
            "attack": {
                "speed": 1100, "reference_altitude": 8000,
                "altitude_max": 14000, "altitude_min": 3000,
                "range": {"fuel_25%": 680, "fuel_50%": 1440, "fuel_75%": 2195, "fuel_100%": 2950},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": True, "SEAD": True, "Escort_Jammer": True,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    "bay_1": ["GBU-10", 8],
                    "bay_2": ["GBU-10", 8],
                    "bay_3": ["GBU-10", 8],
                },
                "devices": {},
                "pylon_count": 3,
                "fuel_internal_max": 88000, "flare": 0, "chaff": 0, "gun_rounds": 0,
            },
        },
    },

    # -------------------------------------------------------------------------
    "B-52H Stratofortress": {

        "Iron Bomb Strike": {
            "loadout_code": "B52H-STRIKE-1",
            "tasks": ["Strike"],
            "attributes": ["Area", "Dumb bomb", "Heavy payload"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": False,
            "cruise": {
                "speed": 800, "reference_altitude": 12000,
                "altitude_max": 15000, "altitude_min": 5000,
                "range": {"fuel_25%": 1800, "fuel_50%": 3700, "fuel_75%": 5500, "fuel_100%": 7200},
            },
            "attack": {
                "speed": 900, "reference_altitude": 8000,
                "altitude_max": 15000, "altitude_min": 5000,
                "range": {"fuel_25%": 1300, "fuel_50%": 2700, "fuel_75%": 4100, "fuel_100%": 5500},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": True, "SEAD": True, "Escort_Jammer": True,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    "bay_1": ["Mk-82", 27],
                    "bay_2": ["Mk-82", 24],
                },
                "devices": {},
                "pylon_count": 2,
                "fuel_internal_max": 144700, "flare": 0, "chaff": 0, "gun_rounds": 0,
            },
        },

        "Heavy Strike Mk-84": {
            "loadout_code": "B52H-STRIKE-2",
            "tasks": ["Strike"],
            "attributes": ["Area", "Heavy payload", "Anti-fortification"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": False,
            "cruise": {
                "speed": 810, "reference_altitude": 12000,
                "altitude_max": 15000, "altitude_min": 5000,
                "range": {"fuel_25%": 1850, "fuel_50%": 3800, "fuel_75%": 5650, "fuel_100%": 7500},
            },
            "attack": {
                "speed": 900, "reference_altitude": 10000,
                "altitude_max": 15000, "altitude_min": 5000,
                "range": {"fuel_25%": 1350, "fuel_50%": 2780, "fuel_75%": 4210, "fuel_100%": 5650},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": True, "SEAD": True, "Escort_Jammer": True,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    "bay_1": ["Mk-84", 8],
                    "bay_2": ["Mk-84", 8],
                },
                "devices": {},
                "pylon_count": 2,
                "fuel_internal_max": 144700, "flare": 0, "chaff": 0, "gun_rounds": 0,
            },
        },
    },

    # -------------------------------------------------------------------------
    "S-3B Viking": {

        "Anti-Ship Maritime Strike": {
            "loadout_code": "S3B-ANTISHIP-1",
            "tasks": ["Anti_Ship"],
            "attributes": ["Anti-ship", "Stand-off", "Maritime"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": False,
            "cruise": {
                "speed": 680, "reference_altitude": 6000,
                "altitude_max": 10000, "altitude_min": 100,
                "range": {"fuel_25%": 310, "fuel_50%": 650, "fuel_75%": 990, "fuel_100%": 1340},
            },
            "attack": {
                "speed": 780, "reference_altitude": 100,
                "altitude_max": 3000, "altitude_min": 30,
                "range": {"fuel_25%": 225, "fuel_50%": 475, "fuel_75%": 725, "fuel_100%": 975},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": True, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AGM-84A", 1], 2: ["AGM-84A", 1],
                },
                "devices": {},
                "pylon_count": 4,
                "fuel_internal_max": 7000, "flare": 30, "chaff": 30, "gun_rounds": 0,
            },
        },

        "Maritime Recon": {
            "loadout_code": "S3B-RECON-1",
            "tasks": ["Recon"],
            "attributes": ["Maritime", "Surveillance"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": False,
            "cruise": {
                "speed": 650, "reference_altitude": 5000,
                "altitude_max": 10000, "altitude_min": 100,
                "range": {"fuel_25%": 340, "fuel_50%": 715, "fuel_75%": 1090, "fuel_100%": 1470},
            },
            "attack": {
                "speed": 700, "reference_altitude": 300,
                "altitude_max": 5000, "altitude_min": 50,
                "range": {"fuel_25%": 248, "fuel_50%": 522, "fuel_75%": 797, "fuel_100%": 1072},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": True, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {},
                "devices": {1: ["FLIR_sensor", 1], 2: ["MAD_sensor", 1]},
                "pylon_count": 4,
                "fuel_internal_max": 7000, "flare": 30, "chaff": 30, "gun_rounds": 0,
            },
        },
    },

    # -------------------------------------------------------------------------
    "S-3B Viking Tanker": {

        "Tanker Standard": {
            "loadout_code": "S3BTKR-STD-1",
            "tasks": [],
            "attributes": ["Tanker", "Buddy refueling"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": False,
            "cruise": {
                "speed": 660, "reference_altitude": 6000,
                "altitude_max": 10000, "altitude_min": 1000,
                "range": {"fuel_25%": 320, "fuel_50%": 670, "fuel_75%": 1020, "fuel_100%": 1380},
            },
            "attack": {
                "speed": 660, "reference_altitude": 3000,
                "altitude_max": 6000, "altitude_min": 1000,
                "range": {"fuel_25%": 230, "fuel_50%": 490, "fuel_75%": 745, "fuel_100%": 1005},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": True, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["buddy_refueling_pod", 1, 5000],
                },
                "devices": {},
                "pylon_count": 4,
                "fuel_internal_max": 7000, "flare": 0, "chaff": 0, "gun_rounds": 0,
            },
        },
    },

    # =========================================================================
    # US AWACS & RECON
    # =========================================================================

    # -------------------------------------------------------------------------
    "E-2D Advanced Hawkeye": {

        "AWACS Standard": {
            "loadout_code": "E2D-AWACS-1",
            "tasks": [],
            "attributes": ["AWACS", "C2", "Early Warning"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": False,
            "cruise": {
                "speed": 550, "reference_altitude": 9400,
                "altitude_max": 11000, "altitude_min": 5000,
                "range": {"fuel_25%": 300, "fuel_50%": 640, "fuel_75%": 975, "fuel_100%": 1310},
            },
            "attack": {
                "speed": 600, "reference_altitude": 9400,
                "altitude_max": 11000, "altitude_min": 5000,
                "range": {"fuel_25%": 218, "fuel_50%": 462, "fuel_75%": 705, "fuel_100%": 950},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": True, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {},
                "devices": {},
                "pylon_count": 0,
                "fuel_internal_max": 5600, "flare": 0, "chaff": 0, "gun_rounds": 0,
            },
        },
    },

    # -------------------------------------------------------------------------
    "E-3A Sentry": {

        "AWACS Standard": {
            "loadout_code": "E3A-AWACS-1",
            "tasks": [],
            "attributes": ["AWACS", "C2", "Early Warning"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": False,
            "cruise": {
                "speed": 740, "reference_altitude": 9000,
                "altitude_max": 12000, "altitude_min": 5000,
                "range": {"fuel_25%": 800, "fuel_50%": 1650, "fuel_75%": 2500, "fuel_100%": 3350},
            },
            "attack": {
                "speed": 800, "reference_altitude": 9000,
                "altitude_max": 12000, "altitude_min": 5000,
                "range": {"fuel_25%": 580, "fuel_50%": 1200, "fuel_75%": 1830, "fuel_100%": 2450},
            },
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {
                "Escort": True, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {},
                "devices": {},
                "pylon_count": 0,
                "fuel_internal_max": 90750, "flare": 0, "chaff": 0, "gun_rounds": 0,
            },
        },
    },

    # -------------------------------------------------------------------------
    "MQ-1 Predator": {

        "Armed Recon": {
            "loadout_code": "MQ1A-RECON-1",
            "tasks": ["Recon", "CAS"],
            "attributes": ["ISR", "Loitering", "Precision"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": False,
            "cruise": {
                "speed": 150, "reference_altitude": 5000,
                "altitude_max": 7500, "altitude_min": 1000,
                "range": {"fuel_25%": 500, "fuel_50%": 1100, "fuel_75%": 1700, "fuel_100%": 2300},
            },
            "attack": {
                "speed": 200, "reference_altitude": 3000,
                "altitude_max": 5000, "altitude_min": 500,
                "range": {"fuel_25%": 360, "fuel_50%": 800, "fuel_75%": 1230, "fuel_100%": 1660},
            },
            "usability": {"day": True, "night": True, "adverse_weather": False},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AGM-114", 1], 2: ["AGM-114", 1],
                },
                "devices": {1: ["MTS-A", 1]},
                "pylon_count": 2,
                "fuel_internal_max": 665, "flare": 0, "chaff": 0, "gun_rounds": 0,
            },
        },

        "Pure ISR": {
            "loadout_code": "MQ1A-RECON-2",
            "tasks": ["Recon"],
            "attributes": ["ISR", "Loitering", "Surveillance"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": False,
            "cruise": {
                "speed": 130, "reference_altitude": 5000,
                "altitude_max": 7500, "altitude_min": 1000,
                "range": {"fuel_25%": 560, "fuel_50%": 1200, "fuel_75%": 1840, "fuel_100%": 2480},
            },
            "attack": {
                "speed": 160, "reference_altitude": 3000,
                "altitude_max": 5000, "altitude_min": 500,
                "range": {"fuel_25%": 410, "fuel_50%": 875, "fuel_75%": 1340, "fuel_100%": 1810},
            },
            "usability": {"day": True, "night": True, "adverse_weather": False},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {},
                "devices": {1: ["MTS-A", 1]},
                "pylon_count": 2,
                "fuel_internal_max": 665, "flare": 0, "chaff": 0, "gun_rounds": 0,
            },
        },
    },

    # -------------------------------------------------------------------------
    "MQ-9 Reaper": {

        "COIN Strike": {
            "loadout_code": "MQ9-CAS-1",
            "tasks": ["Recon", "CAS", "Strike"],
            "attributes": ["ISR", "Loitering", "Precision", "Anti-armor"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": False,
            "cruise": {
                "speed": 280, "reference_altitude": 7500,
                "altitude_max": 13500, "altitude_min": 1000,
                "range": {"fuel_25%": 800, "fuel_50%": 1700, "fuel_75%": 2600, "fuel_100%": 3500},
            },
            "attack": {
                "speed": 380, "reference_altitude": 5000,
                "altitude_max": 8000, "altitude_min": 500,
                "range": {"fuel_25%": 580, "fuel_50%": 1235, "fuel_75%": 1890, "fuel_100%": 2545},
            },
            "usability": {"day": True, "night": True, "adverse_weather": False},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {
                    1: ["AGM-114", 2], 2: ["AGM-114", 2],
                    3: ["GBU-12", 1], 4: ["GBU-12", 1],
                },
                "devices": {1: ["MTS-B", 1]},
                "pylon_count": 6,
                "fuel_internal_max": 1814, "flare": 0, "chaff": 0, "gun_rounds": 0,
            },
        },

        "Pure ISR": {
            "loadout_code": "MQ9-RECON-1",
            "tasks": ["Recon"],
            "attributes": ["ISR", "Loitering", "Surveillance"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": False,
            "cruise": {
                "speed": 250, "reference_altitude": 8000,
                "altitude_max": 13500, "altitude_min": 1000,
                "range": {"fuel_25%": 900, "fuel_50%": 1900, "fuel_75%": 2900, "fuel_100%": 3900},
            },
            "attack": {
                "speed": 300, "reference_altitude": 5000,
                "altitude_max": 8000, "altitude_min": 500,
                "range": {"fuel_25%": 655, "fuel_50%": 1390, "fuel_75%": 2120, "fuel_100%": 2850},
            },
            "usability": {"day": True, "night": True, "adverse_weather": False},
            "mandatory_support": {
                "Escort": False, "SEAD": False, "Escort_Jammer": False,
                "Flare_Illumination": False, "Laser_Illumination": False,
            },
            "stores": {
                "pylons": {},
                "devices": {1: ["MTS-B", 1], 2: ["Lynx_SAR", 1]},
                "pylon_count": 6,
                "fuel_internal_max": 1814, "flare": 0, "chaff": 0, "gun_rounds": 0,
            },
        },
    },

    # =========================================================================
    # US TRANSPORT & TANKERS  (no combat loadouts, standard config only)
    # =========================================================================

    "C-130 Hercules": {
        "Standard Transport": {
            "loadout_code": "C130-STD-1", "tasks": [], "attributes": ["Transport"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": False,
            "cruise": {"speed": 540, "reference_altitude": 6700, "altitude_max": 9000, "altitude_min": 100,
                       "range": {"fuel_25%": 450, "fuel_50%": 950, "fuel_75%": 1450, "fuel_100%": 1950}},
            "attack": {"speed": 580, "reference_altitude": 3000, "altitude_max": 6000, "altitude_min": 50,
                       "range": {"fuel_25%": 325, "fuel_50%": 690, "fuel_75%": 1055, "fuel_100%": 1420}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": True, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {}, "devices": {}, "pylon_count": 0,
                       "fuel_internal_max": 26340, "flare": 60, "chaff": 0, "gun_rounds": 0},
        },
    },

    "C-17A Globemaster III": {
        "Standard Transport": {
            "loadout_code": "C17A-STD-1", "tasks": [], "attributes": ["Transport", "Strategic"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": False,
            "cruise": {"speed": 740, "reference_altitude": 10000, "altitude_max": 13100, "altitude_min": 100,
                       "range": {"fuel_25%": 700, "fuel_50%": 1500, "fuel_75%": 2200, "fuel_100%": 2950}},
            "attack": {"speed": 800, "reference_altitude": 5000, "altitude_max": 10000, "altitude_min": 50,
                       "range": {"fuel_25%": 508, "fuel_50%": 1087, "fuel_75%": 1596, "fuel_100%": 2140}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": True, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {}, "devices": {}, "pylon_count": 0,
                       "fuel_internal_max": 134000, "flare": 60, "chaff": 0, "gun_rounds": 0},
        },
    },

    "KC-130": {
        "Tanker/Transport": {
            "loadout_code": "KC130-STD-1", "tasks": [], "attributes": ["Tanker", "Transport"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": False,
            "cruise": {"speed": 540, "reference_altitude": 6700, "altitude_max": 9000, "altitude_min": 1000,
                       "range": {"fuel_25%": 430, "fuel_50%": 915, "fuel_75%": 1395, "fuel_100%": 1880}},
            "attack": {"speed": 580, "reference_altitude": 4000, "altitude_max": 7000, "altitude_min": 500,
                       "range": {"fuel_25%": 312, "fuel_50%": 665, "fuel_75%": 1015, "fuel_100%": 1365}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": True, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["hose_drogue_pod", 1, 20000]}, "devices": {}, "pylon_count": 2,
                       "fuel_internal_max": 26340, "flare": 0, "chaff": 0, "gun_rounds": 0},
        },
    },

    "KC-135 Stratotanker": {
        "Tanker Standard": {
            "loadout_code": "KC135-STD-1", "tasks": [], "attributes": ["Tanker", "Strategic"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": False,
            "cruise": {"speed": 850, "reference_altitude": 10700, "altitude_max": 13000, "altitude_min": 5000,
                       "range": {"fuel_25%": 800, "fuel_50%": 1700, "fuel_75%": 2600, "fuel_100%": 3500}},
            "attack": {"speed": 900, "reference_altitude": 8000, "altitude_max": 12000, "altitude_min": 3000,
                       "range": {"fuel_25%": 580, "fuel_50%": 1235, "fuel_75%": 1885, "fuel_100%": 2530}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": True, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["boom_refueling", 1, 90000]}, "devices": {}, "pylon_count": 1,
                       "fuel_internal_max": 118000, "flare": 0, "chaff": 0, "gun_rounds": 0},
        },
    },

    "KC-135 MPRS": {
        "Tanker MPRS": {
            "loadout_code": "KC135MPRS-STD-1", "tasks": [], "attributes": ["Tanker", "Multi-point"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": False,
            "cruise": {"speed": 850, "reference_altitude": 10700, "altitude_max": 13000, "altitude_min": 5000,
                       "range": {"fuel_25%": 800, "fuel_50%": 1700, "fuel_75%": 2600, "fuel_100%": 3500}},
            "attack": {"speed": 900, "reference_altitude": 8000, "altitude_max": 12000, "altitude_min": 3000,
                       "range": {"fuel_25%": 580, "fuel_50%": 1235, "fuel_75%": 1885, "fuel_100%": 2530}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": True, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["hose_drogue_pod", 2, 90000]}, "devices": {}, "pylon_count": 2,
                       "fuel_internal_max": 118000, "flare": 0, "chaff": 0, "gun_rounds": 0},
        },
    },


    # =========================================================================
    # NATO / ALLIED
    # =========================================================================

    "AJ/ASJ 37 Viggen": {

        "Air-to-Air": {
            "loadout_code": "ASJ37-CAP-1",
            "tasks": ["CAP", "Fighter_Sweep"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True,
            "self_escort_capability": True,
            "cruise": {"speed": 900, "reference_altitude": 9000, "altitude_max": 15000, "altitude_min": 500,
                       "range": {"fuel_25%": 165, "fuel_50%": 350, "fuel_75%": 535, "fuel_100%": 720}},
            "attack": {"speed": 2100, "reference_altitude": 11000, "altitude_max": 15000, "altitude_min": 500,
                       "range": {"fuel_25%": 120, "fuel_50%": 255, "fuel_75%": 390, "fuel_100%": 525}},
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["RB-74", 1], 2: ["RB-74", 1],
                                  3: ["RB-24J", 1], 4: ["RB-24J", 1]},
                       "devices": {}, "pylon_count": 7,
                       "fuel_internal_max": 5050, "flare": 0, "chaff": 0, "gun_rounds": 150},
        },

        "Anti-Ship Strike": {
            "loadout_code": "ASJ37-ANTISHIP-1",
            "tasks": ["Strike"],
            "attributes": ["Anti-ship", "Stand-off"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {"speed": 870, "reference_altitude": 100, "altitude_max": 5000, "altitude_min": 30,
                       "range": {"fuel_25%": 140, "fuel_50%": 295, "fuel_75%": 455, "fuel_100%": 615}},
            "attack": {"speed": 1100, "reference_altitude": 50, "altitude_max": 2000, "altitude_min": 15,
                       "range": {"fuel_25%": 102, "fuel_50%": 215, "fuel_75%": 330, "fuel_100%": 445}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": True, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["RB-15F", 1], 2: ["RB-15F", 1],
                                  3: ["RB-24", 1], 4: ["RB-24", 1]},
                       "devices": {}, "pylon_count": 7,
                       "fuel_internal_max": 5050, "flare": 0, "chaff": 0, "gun_rounds": 150},
        },

        "Ground Strike": {
            "loadout_code": "ASJ37-STRIKE-1",
            "tasks": ["Strike", "CAS"],
            "attributes": ["Ground attack"],
            "Lock_Down_Shoot_Down": False,
            "self_escort_capability": True,
            "cruise": {"speed": 860, "reference_altitude": 5000, "altitude_max": 12000, "altitude_min": 100,
                       "range": {"fuel_25%": 150, "fuel_50%": 318, "fuel_75%": 487, "fuel_100%": 655}},
            "attack": {"speed": 1000, "reference_altitude": 1000, "altitude_max": 5000, "altitude_min": 50,
                       "range": {"fuel_25%": 110, "fuel_50%": 232, "fuel_75%": 355, "fuel_100%": 478}},
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["RB-05A", 1], 2: ["RB-05A", 1],
                                  3: ["SNEB-253", 1], 4: ["SNEB-253", 1],
                                  5: ["RB-24", 1]},
                       "devices": {}, "pylon_count": 7,
                       "fuel_internal_max": 5050, "flare": 0, "chaff": 0, "gun_rounds": 150},
        },
    },

    # -------------------------------------------------------------------------
    "Mirage 2000C": {

        "Matra CAP": {
            "loadout_code": "M2000C-CAP-1",
            "tasks": ["CAP", "Intercept"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True,
            "self_escort_capability": True,
            "cruise": {"speed": 900, "reference_altitude": 9000, "altitude_max": 18000, "altitude_min": 1000,
                       "range": {"fuel_25%": 175, "fuel_50%": 370, "fuel_75%": 565, "fuel_100%": 760}},
            "attack": {"speed": 2200, "reference_altitude": 11000, "altitude_max": 18000, "altitude_min": 500,
                       "range": {"fuel_25%": 128, "fuel_50%": 270, "fuel_75%": 413, "fuel_100%": 556}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["R-530EM", 1], 2: ["R-530EM", 1],
                                  3: ["R-550", 1], 4: ["R-550", 1],
                                  5: ["1300L_tank", 1, 1050]},
                       "devices": {}, "pylon_count": 9,
                       "fuel_internal_max": 3900, "flare": 112, "chaff": 112, "gun_rounds": 250},
        },

        "Fighter Sweep": {
            "loadout_code": "M2000C-CAP-2",
            "tasks": ["Fighter_Sweep", "CAP"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True,
            "self_escort_capability": True,
            "cruise": {"speed": 950, "reference_altitude": 9000, "altitude_max": 18000, "altitude_min": 500,
                       "range": {"fuel_25%": 190, "fuel_50%": 400, "fuel_75%": 610, "fuel_100%": 820}},
            "attack": {"speed": 2338, "reference_altitude": 11000, "altitude_max": 18000, "altitude_min": 500,
                       "range": {"fuel_25%": 138, "fuel_50%": 292, "fuel_75%": 447, "fuel_100%": 601}},
            "usability": {"day": True, "night": True, "adverse_weather": False},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["R-530IR", 1], 2: ["R-530IR", 1],
                                  3: ["R-550", 1], 4: ["R-550", 1]},
                       "devices": {}, "pylon_count": 9,
                       "fuel_internal_max": 3900, "flare": 112, "chaff": 112, "gun_rounds": 250},
        },
    },

    # =========================================================================
    # SOVIET / RUSSIAN FIGHTERS
    # =========================================================================

    "MiG-15bis": {
        "Gun Fighter": {
            "loadout_code": "MIG15-CAP-1",
            "tasks": ["CAP", "Intercept"],
            "attributes": [],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 800, "reference_altitude": 9000, "altitude_max": 15000, "altitude_min": 1000,
                       "range": {"fuel_25%": 60, "fuel_50%": 130, "fuel_75%": 200, "fuel_100%": 270}},
            "attack": {"speed": 1075, "reference_altitude": 9000, "altitude_max": 15000, "altitude_min": 1000,
                       "range": {"fuel_25%": 44, "fuel_50%": 95, "fuel_75%": 145, "fuel_100%": 196}},
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {}, "devices": {}, "pylon_count": 2,
                       "fuel_internal_max": 1200, "flare": 0, "chaff": 0, "gun_rounds": 200},
        },
        "Rocket CAS": {
            "loadout_code": "MIG15-CAS-1",
            "tasks": ["CAP"],
            "attributes": ["Close Air Support"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 750, "reference_altitude": 5000, "altitude_max": 12000, "altitude_min": 100,
                       "range": {"fuel_25%": 55, "fuel_50%": 118, "fuel_75%": 182, "fuel_100%": 245}},
            "attack": {"speed": 900, "reference_altitude": 1000, "altitude_max": 5000, "altitude_min": 50,
                       "range": {"fuel_25%": 40, "fuel_50%": 86, "fuel_75%": 132, "fuel_100%": 178}},
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["S-5 M", 1], 2: ["S-5 M", 1]},
                       "devices": {}, "pylon_count": 2,
                       "fuel_internal_max": 1200, "flare": 0, "chaff": 0, "gun_rounds": 200},
        },
    },

    "MiG-19P": {
        "Air Defense": {
            "loadout_code": "MIG19-CAP-1",
            "tasks": ["CAP", "Intercept"],
            "attributes": [],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 900, "reference_altitude": 10000, "altitude_max": 17500, "altitude_min": 1000,
                       "range": {"fuel_25%": 95, "fuel_50%": 200, "fuel_75%": 308, "fuel_100%": 415}},
            "attack": {"speed": 1500, "reference_altitude": 10000, "altitude_max": 17500, "altitude_min": 500,
                       "range": {"fuel_25%": 69, "fuel_50%": 146, "fuel_75%": 224, "fuel_100%": 302}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["R-3R", 1], 2: ["R-3R", 1]},
                       "devices": {}, "pylon_count": 4,
                       "fuel_internal_max": 2170, "flare": 0, "chaff": 0, "gun_rounds": 200},
        },
    },

    "MiG-21bis": {
        "Fishbed CAP": {
            "loadout_code": "MIG21-CAP-1",
            "tasks": ["CAP", "Intercept"],
            "attributes": [],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 900, "reference_altitude": 10000, "altitude_max": 19000, "altitude_min": 1000,
                       "range": {"fuel_25%": 100, "fuel_50%": 212, "fuel_75%": 325, "fuel_100%": 438}},
            "attack": {"speed": 2175, "reference_altitude": 12000, "altitude_max": 19000, "altitude_min": 500,
                       "range": {"fuel_25%": 73, "fuel_50%": 155, "fuel_75%": 237, "fuel_100%": 320}},
            "usability": {"day": True, "night": True, "adverse_weather": False},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["R-13M1", 1], 2: ["R-13M1", 1],
                                  3: ["R-60M", 1], 4: ["R-60M", 1],
                                  5: ["800L_tank", 1, 600]},
                       "devices": {}, "pylon_count": 4,
                       "fuel_internal_max": 2650, "flare": 0, "chaff": 0, "gun_rounds": 200},
        },
        "Ground Strike": {
            "loadout_code": "MIG21-STRIKE-1",
            "tasks": ["Strike"],
            "attributes": ["Ground attack"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 850, "reference_altitude": 5000, "altitude_max": 12000, "altitude_min": 100,
                       "range": {"fuel_25%": 90, "fuel_50%": 192, "fuel_75%": 295, "fuel_100%": 397}},
            "attack": {"speed": 1000, "reference_altitude": 1000, "altitude_max": 5000, "altitude_min": 50,
                       "range": {"fuel_25%": 65, "fuel_50%": 140, "fuel_75%": 215, "fuel_100%": 290}},
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["S-24", 1], 2: ["S-24", 1],
                                  3: ["FAB-250M54", 1], 4: ["R-13M1", 1]},
                       "devices": {}, "pylon_count": 4,
                       "fuel_internal_max": 2650, "flare": 0, "chaff": 0, "gun_rounds": 200},
        },
    },

    "MiG-23MLD": {
        "Flogger CAP": {
            "loadout_code": "MIG23-CAP-1",
            "tasks": ["CAP"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True, "self_escort_capability": True,
            "cruise": {"speed": 900, "reference_altitude": 9000, "altitude_max": 18500, "altitude_min": 1000,
                       "range": {"fuel_25%": 150, "fuel_50%": 318, "fuel_75%": 487, "fuel_100%": 655}},
            "attack": {"speed": 2500, "reference_altitude": 12000, "altitude_max": 18500, "altitude_min": 500,
                       "range": {"fuel_25%": 109, "fuel_50%": 232, "fuel_75%": 355, "fuel_100%": 478}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["R-24R", 1], 2: ["R-24R", 1],
                                  3: ["R-60M", 1], 4: ["R-60M", 1],
                                  5: ["800L_tank", 1, 600]},
                       "devices": {}, "pylon_count": 6,
                       "fuel_internal_max": 5750, "flare": 30, "chaff": 30, "gun_rounds": 200},
        },
        "Ground Attack": {
            "loadout_code": "MIG23-STRIKE-1",
            "tasks": ["Strike", "CAS"],
            "attributes": ["Ground attack"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 850, "reference_altitude": 5000, "altitude_max": 12000, "altitude_min": 100,
                       "range": {"fuel_25%": 135, "fuel_50%": 287, "fuel_75%": 440, "fuel_100%": 592}},
            "attack": {"speed": 1000, "reference_altitude": 1000, "altitude_max": 5000, "altitude_min": 50,
                       "range": {"fuel_25%": 98, "fuel_50%": 208, "fuel_75%": 318, "fuel_100%": 428}},
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["FAB-500M62", 1], 2: ["FAB-250M54", 2],
                                  3: ["S-24", 1], 4: ["R-60M", 1]},
                       "devices": {}, "pylon_count": 6,
                       "fuel_internal_max": 5750, "flare": 30, "chaff": 30, "gun_rounds": 200},
        },
    },

    "MiG-25PD": {
        "Long Range Intercept": {
            "loadout_code": "MIG25PD-INT-1",
            "tasks": ["Intercept", "CAP"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True, "self_escort_capability": True,
            "cruise": {"speed": 1000, "reference_altitude": 17000, "altitude_max": 23000, "altitude_min": 5000,
                       "range": {"fuel_25%": 260, "fuel_50%": 550, "fuel_75%": 840, "fuel_100%": 1130}},
            "attack": {"speed": 3395, "reference_altitude": 20000, "altitude_max": 23000, "altitude_min": 5000,
                       "range": {"fuel_25%": 189, "fuel_50%": 400, "fuel_75%": 611, "fuel_100%": 822}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["R-40R", 1], 2: ["R-40R", 1],
                                  3: ["R-40T", 1], 4: ["R-40T", 1]},
                       "devices": {}, "pylon_count": 4,
                       "fuel_internal_max": 14570, "flare": 0, "chaff": 0, "gun_rounds": 0},
        },
    },

    "MiG-25RB": {
        "Recon": {
            "loadout_code": "MIG25RB-RECON-1",
            "tasks": ["Recon"],
            "attributes": ["High-altitude recon"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": False,
            "cruise": {"speed": 1200, "reference_altitude": 20000, "altitude_max": 23000, "altitude_min": 5000,
                       "range": {"fuel_25%": 350, "fuel_50%": 740, "fuel_75%": 1130, "fuel_100%": 1520}},
            "attack": {"speed": 3000, "reference_altitude": 20000, "altitude_max": 23000, "altitude_min": 5000,
                       "range": {"fuel_25%": 255, "fuel_50%": 538, "fuel_75%": 822, "fuel_100%": 1106}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {}, "devices": {1: ["SIGINT_pod", 1], 2: ["photo_recon_pod", 1]},
                       "pylon_count": 4,
                       "fuel_internal_max": 14570, "flare": 0, "chaff": 0, "gun_rounds": 0},
        },
    },

    "MiG-27K": {
        "Precision Ground Attack": {
            "loadout_code": "MIG27K-PSTRIKE-1",
            "tasks": ["Strike", "CAS", "Pinpoint_Strike"],
            "attributes": ["Precision", "Laser-guided", "Anti-armor"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 850, "reference_altitude": 6000, "altitude_max": 14000, "altitude_min": 100,
                       "range": {"fuel_25%": 155, "fuel_50%": 328, "fuel_75%": 502, "fuel_100%": 675}},
            "attack": {"speed": 1000, "reference_altitude": 2000, "altitude_max": 6000, "altitude_min": 50,
                       "range": {"fuel_25%": 113, "fuel_50%": 239, "fuel_75%": 365, "fuel_100%": 491}},
            "usability": {"day": True, "night": True, "adverse_weather": False},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["Kh-25ML", 1], 2: ["Kh-25ML", 1],
                                  3: ["Kh-29L", 1], 4: ["R-60M", 1], 5: ["R-60M", 1]},
                       "devices": {1: ["Kaira_laser", 1]},
                       "pylon_count": 9,
                       "fuel_internal_max": 5000, "flare": 30, "chaff": 30, "gun_rounds": 300},
        },
        "CAS Rocket Attack": {
            "loadout_code": "MIG27K-CAS-1",
            "tasks": ["CAS"],
            "attributes": ["Close Air Support"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 820, "reference_altitude": 3000, "altitude_max": 8000, "altitude_min": 50,
                       "range": {"fuel_25%": 140, "fuel_50%": 298, "fuel_75%": 456, "fuel_100%": 614}},
            "attack": {"speed": 950, "reference_altitude": 500, "altitude_max": 3000, "altitude_min": 30,
                       "range": {"fuel_25%": 102, "fuel_50%": 217, "fuel_75%": 332, "fuel_100%": 447}},
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["S-24", 1], 2: ["S-24", 1],
                                  3: ["S-8 OFP2", 1], 4: ["S-8 OFP2", 1],
                                  5: ["R-60M", 1]},
                       "devices": {}, "pylon_count": 9,
                       "fuel_internal_max": 5000, "flare": 30, "chaff": 30, "gun_rounds": 300},
        },
    },

    "MiG-29A": {
        "Fulcrum CAP": {
            "loadout_code": "MIG29A-CAP-1",
            "tasks": ["CAP", "Intercept", "Fighter_Sweep"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True, "self_escort_capability": True,
            "cruise": {"speed": 900, "reference_altitude": 9000, "altitude_max": 18000, "altitude_min": 1000,
                       "range": {"fuel_25%": 145, "fuel_50%": 308, "fuel_75%": 470, "fuel_100%": 633}},
            "attack": {"speed": 2450, "reference_altitude": 12000, "altitude_max": 18000, "altitude_min": 500,
                       "range": {"fuel_25%": 106, "fuel_50%": 224, "fuel_75%": 342, "fuel_100%": 460}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["R-27R", 1], 2: ["R-27R", 1],
                                  3: ["R-73", 1], 4: ["R-73", 1],
                                  5: ["R-73", 1], 6: ["R-73", 1]},
                       "devices": {}, "pylon_count": 7,
                       "fuel_internal_max": 4365, "flare": 30, "chaff": 30, "gun_rounds": 150},
        },
        "IRST Dogfight": {
            "loadout_code": "MIG29A-CAP-2",
            "tasks": ["CAP", "Fighter_Sweep"],
            "attributes": [],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 950, "reference_altitude": 9000, "altitude_max": 18000, "altitude_min": 500,
                       "range": {"fuel_25%": 155, "fuel_50%": 330, "fuel_75%": 505, "fuel_100%": 680}},
            "attack": {"speed": 2450, "reference_altitude": 10000, "altitude_max": 18000, "altitude_min": 100,
                       "range": {"fuel_25%": 113, "fuel_50%": 240, "fuel_75%": 368, "fuel_100%": 495}},
            "usability": {"day": True, "night": True, "adverse_weather": False},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["R-27T", 1], 2: ["R-27T", 1],
                                  3: ["R-73", 1], 4: ["R-73", 1],
                                  5: ["R-60M", 1], 6: ["R-60M", 1]},
                       "devices": {}, "pylon_count": 7,
                       "fuel_internal_max": 4365, "flare": 30, "chaff": 30, "gun_rounds": 150},
        },
    },

    "MiG-29S": {
        "CAP": {
            "loadout_code": "MIG29S-CAP-1",
            "tasks": ["CAP", "Intercept", "Fighter_Sweep"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True, "self_escort_capability": True,
            "cruise": {"speed": 920, "reference_altitude": 9000, "altitude_max": 18000, "altitude_min": 1000,
                       "range": {"fuel_25%": 150, "fuel_50%": 317, "fuel_75%": 485, "fuel_100%": 652}},
            "attack": {"speed": 2450, "reference_altitude": 12000, "altitude_max": 18000, "altitude_min": 500,
                       "range": {"fuel_25%": 109, "fuel_50%": 231, "fuel_75%": 353, "fuel_100%": 474}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["R-27ER", 1], 2: ["R-27ER", 1],
                                  3: ["R-73", 1], 4: ["R-73", 1],
                                  5: ["R-73", 1], 6: ["R-73", 1]},
                       "devices": {}, "pylon_count": 7,
                       "fuel_internal_max": 4825, "flare": 30, "chaff": 30, "gun_rounds": 150},
        },
        "Strike": {
            "loadout_code": "MIG29S-STRIKE-1",
            "tasks": ["Strike"],
            "attributes": ["Ground attack"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 870, "reference_altitude": 5000, "altitude_max": 12000, "altitude_min": 100,
                       "range": {"fuel_25%": 135, "fuel_50%": 287, "fuel_75%": 438, "fuel_100%": 590}},
            "attack": {"speed": 1000, "reference_altitude": 1500, "altitude_max": 5000, "altitude_min": 50,
                       "range": {"fuel_25%": 98, "fuel_50%": 209, "fuel_75%": 320, "fuel_100%": 430}},
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["FAB-500M62", 1], 2: ["FAB-500M62", 1],
                                  3: ["FAB-250M54", 2], 4: ["R-73", 1], 5: ["R-73", 1]},
                       "devices": {}, "pylon_count": 7,
                       "fuel_internal_max": 4825, "flare": 30, "chaff": 30, "gun_rounds": 150},
        },
    },

    "MiG-31": {
        "Foxhound Intercept": {
            "loadout_code": "MIG31-INT-1",
            "tasks": ["Intercept", "CAP"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True, "self_escort_capability": True,
            "cruise": {"speed": 1000, "reference_altitude": 17000, "altitude_max": 20600, "altitude_min": 5000,
                       "range": {"fuel_25%": 300, "fuel_50%": 640, "fuel_75%": 975, "fuel_100%": 1310}},
            "attack": {"speed": 3000, "reference_altitude": 18000, "altitude_max": 20600, "altitude_min": 5000,
                       "range": {"fuel_25%": 218, "fuel_50%": 465, "fuel_75%": 709, "fuel_100%": 952}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["R-40R", 1], 2: ["R-40R", 1],
                                  3: ["R-40T", 1], 4: ["R-40T", 1],
                                  5: ["R-60M", 1], 6: ["R-60M", 1]},
                       "devices": {}, "pylon_count": 6,
                       "fuel_internal_max": 16350, "flare": 0, "chaff": 0, "gun_rounds": 260},
        },
    },


    # =========================================================================
    # SOVIET ATTACKERS
    # =========================================================================

    "Su-17M4": {
        "Ground Attack": {
            "loadout_code": "SU17M4-STRIKE-1",
            "tasks": ["Strike", "CAS"],
            "attributes": ["Ground attack", "Area"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 850, "reference_altitude": 5000, "altitude_max": 14000, "altitude_min": 100,
                       "range": {"fuel_25%": 170, "fuel_50%": 360, "fuel_75%": 550, "fuel_100%": 740}},
            "attack": {"speed": 1000, "reference_altitude": 1000, "altitude_max": 5000, "altitude_min": 50,
                       "range": {"fuel_25%": 124, "fuel_50%": 262, "fuel_75%": 400, "fuel_100%": 538}},
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["Kh-25ML", 1], 2: ["Kh-25ML", 1],
                                  3: ["FAB-500M62", 1], 4: ["FAB-250M54", 2],
                                  5: ["R-60M", 1], 6: ["R-60M", 1]},
                       "devices": {}, "pylon_count": 8,
                       "fuel_internal_max": 3630, "flare": 30, "chaff": 30, "gun_rounds": 200},
        },
        "CAS Rocket": {
            "loadout_code": "SU17M4-CAS-1",
            "tasks": ["CAS"],
            "attributes": ["Close Air Support"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 820, "reference_altitude": 2000, "altitude_max": 8000, "altitude_min": 50,
                       "range": {"fuel_25%": 155, "fuel_50%": 328, "fuel_75%": 502, "fuel_100%": 675}},
            "attack": {"speed": 950, "reference_altitude": 500, "altitude_max": 3000, "altitude_min": 30,
                       "range": {"fuel_25%": 113, "fuel_50%": 239, "fuel_75%": 365, "fuel_100%": 491}},
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["S-24", 1], 2: ["S-24", 1],
                                  3: ["S-8 OFP2", 1], 4: ["S-8 OFP2", 1],
                                  5: ["R-60M", 1]},
                       "devices": {}, "pylon_count": 8,
                       "fuel_internal_max": 3630, "flare": 30, "chaff": 30, "gun_rounds": 200},
        },
    },

    "Su-24M": {
        "Night Precision Strike": {
            "loadout_code": "SU24M-PSTRIKE-1",
            "tasks": ["Strike", "Pinpoint_Strike"],
            "attributes": ["Precision", "Laser-guided", "Day/Night"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 850, "reference_altitude": 8000, "altitude_max": 11000, "altitude_min": 300,
                       "range": {"fuel_25%": 265, "fuel_50%": 560, "fuel_75%": 855, "fuel_100%": 1150}},
            "attack": {"speed": 1000, "reference_altitude": 3000, "altitude_max": 8000, "altitude_min": 100,
                       "range": {"fuel_25%": 193, "fuel_50%": 407, "fuel_75%": 622, "fuel_100%": 836}},
            "usability": {"day": True, "night": True, "adverse_weather": False},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["Kh-29L", 1], 2: ["Kh-29L", 1],
                                  3: ["Kh-25ML", 1], 4: ["Kh-25ML", 1],
                                  5: ["R-60M", 1], 6: ["R-60M", 1]},
                       "devices": {1: ["Kaira_laser", 1]},
                       "pylon_count": 8,
                       "fuel_internal_max": 7260, "flare": 30, "chaff": 30, "gun_rounds": 500},
        },
        "SEAD": {
            "loadout_code": "SU24M-SEAD-1",
            "tasks": ["SEAD"],
            "attributes": ["Anti-radar", "Stand-off"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 850, "reference_altitude": 8000, "altitude_max": 11000, "altitude_min": 1000,
                       "range": {"fuel_25%": 268, "fuel_50%": 567, "fuel_75%": 866, "fuel_100%": 1165}},
            "attack": {"speed": 1000, "reference_altitude": 5000, "altitude_max": 11000, "altitude_min": 500,
                       "range": {"fuel_25%": 195, "fuel_50%": 412, "fuel_75%": 629, "fuel_100%": 847}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["Kh-58", 1], 2: ["Kh-58", 1],
                                  3: ["Kh-25MPU", 1], 4: ["Kh-25MPU", 1],
                                  5: ["R-60M", 1], 6: ["R-60M", 1]},
                       "devices": {}, "pylon_count": 8,
                       "fuel_internal_max": 7260, "flare": 30, "chaff": 30, "gun_rounds": 500},
        },
        "Heavy Strike": {
            "loadout_code": "SU24M-STRIKE-1",
            "tasks": ["Strike"],
            "attributes": ["Area", "Dumb bomb"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 840, "reference_altitude": 7000, "altitude_max": 11000, "altitude_min": 100,
                       "range": {"fuel_25%": 250, "fuel_50%": 530, "fuel_75%": 810, "fuel_100%": 1090}},
            "attack": {"speed": 1100, "reference_altitude": 2000, "altitude_max": 6000, "altitude_min": 100,
                       "range": {"fuel_25%": 182, "fuel_50%": 385, "fuel_75%": 588, "fuel_100%": 792}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["FAB-500M62", 2], 2: ["FAB-500M62", 2],
                                  3: ["FAB-250M54", 2], 4: ["R-60M", 1], 5: ["R-60M", 1]},
                       "devices": {}, "pylon_count": 8,
                       "fuel_internal_max": 7260, "flare": 30, "chaff": 30, "gun_rounds": 500},
        },
    },

    "Su-24MR": {
        "Tactical Recon": {
            "loadout_code": "SU24MR-RECON-1",
            "tasks": ["Recon"],
            "attributes": ["Tactical recon", "Day/Night"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 900, "reference_altitude": 8000, "altitude_max": 11000, "altitude_min": 100,
                       "range": {"fuel_25%": 280, "fuel_50%": 592, "fuel_75%": 904, "fuel_100%": 1216}},
            "attack": {"speed": 1300, "reference_altitude": 300, "altitude_max": 5000, "altitude_min": 50,
                       "range": {"fuel_25%": 204, "fuel_50%": 431, "fuel_75%": 658, "fuel_100%": 884}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": True, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {}, "devices": {1: ["BKR-3", 1], 2: ["Shpil-2M", 1]},
                       "pylon_count": 8,
                       "fuel_internal_max": 7260, "flare": 30, "chaff": 30, "gun_rounds": 0},
        },
    },

    "Su-25": {
        "CAS Ground Pounding": {
            "loadout_code": "SU25-CAS-1",
            "tasks": ["CAS"],
            "attributes": ["Close Air Support", "Area"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 680, "reference_altitude": 3000, "altitude_max": 7000, "altitude_min": 100,
                       "range": {"fuel_25%": 175, "fuel_50%": 370, "fuel_75%": 565, "fuel_100%": 760}},
            "attack": {"speed": 800, "reference_altitude": 1000, "altitude_max": 4000, "altitude_min": 30,
                       "range": {"fuel_25%": 127, "fuel_50%": 269, "fuel_75%": 411, "fuel_100%": 553}},
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {"Escort": True, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["FAB-250M54", 2], 2: ["FAB-250M54", 2],
                                  3: ["S-8 OFP2", 1], 4: ["S-8 OFP2", 1],
                                  5: ["R-60M", 1], 6: ["R-60M", 1]},
                       "devices": {}, "pylon_count": 10,
                       "fuel_internal_max": 2840, "flare": 192, "chaff": 0, "gun_rounds": 250},
        },
        "Strike": {
            "loadout_code": "SU25-STRIKE-1",
            "tasks": ["Strike"],
            "attributes": ["Dumb bomb", "Area"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 660, "reference_altitude": 5000, "altitude_max": 9000, "altitude_min": 100,
                       "range": {"fuel_25%": 185, "fuel_50%": 393, "fuel_75%": 600, "fuel_100%": 807}},
            "attack": {"speed": 800, "reference_altitude": 2000, "altitude_max": 6000, "altitude_min": 100,
                       "range": {"fuel_25%": 135, "fuel_50%": 286, "fuel_75%": 437, "fuel_100%": 588}},
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {"Escort": True, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["FAB-500M62", 1], 2: ["FAB-500M62", 1],
                                  3: ["FAB-250M54", 2], 4: ["FAB-250M54", 2],
                                  5: ["R-60M", 1], 6: ["R-60M", 1]},
                       "devices": {}, "pylon_count": 10,
                       "fuel_internal_max": 2840, "flare": 192, "chaff": 0, "gun_rounds": 250},
        },
    },

    "Su-25T": {
        "Anti-Tank Precision": {
            "loadout_code": "SU25T-PSTRIKE-1",
            "tasks": ["CAS", "Pinpoint_Strike"],
            "attributes": ["Anti-tank", "Precision", "Laser-guided"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 680, "reference_altitude": 4000, "altitude_max": 9000, "altitude_min": 100,
                       "range": {"fuel_25%": 180, "fuel_50%": 382, "fuel_75%": 583, "fuel_100%": 784}},
            "attack": {"speed": 780, "reference_altitude": 1500, "altitude_max": 5000, "altitude_min": 30,
                       "range": {"fuel_25%": 131, "fuel_50%": 277, "fuel_75%": 424, "fuel_100%": 570}},
            "usability": {"day": True, "night": True, "adverse_weather": False},
            "mandatory_support": {"Escort": True, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["Kh-29T", 1], 2: ["Kh-29T", 1],
                                  3: ["Kh-25ML", 1], 4: ["Kh-25ML", 1],
                                  5: ["R-60M", 1], 6: ["R-60M", 1]},
                       "devices": {1: ["Shkval_TV", 1]},
                       "pylon_count": 10,
                       "fuel_internal_max": 3780, "flare": 192, "chaff": 0, "gun_rounds": 250},
        },
        "Strike": {
            "loadout_code": "SU25T-STRIKE-1",
            "tasks": ["Strike"],
            "attributes": ["Dumb bomb", "Area"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 660, "reference_altitude": 5000, "altitude_max": 9000, "altitude_min": 100,
                       "range": {"fuel_25%": 188, "fuel_50%": 398, "fuel_75%": 608, "fuel_100%": 817}},
            "attack": {"speed": 800, "reference_altitude": 2000, "altitude_max": 6000, "altitude_min": 100,
                       "range": {"fuel_25%": 137, "fuel_50%": 290, "fuel_75%": 442, "fuel_100%": 595}},
            "usability": {"day": True, "night": True, "adverse_weather": False},
            "mandatory_support": {"Escort": True, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["FAB-500M62", 1], 2: ["FAB-500M62", 1],
                                  3: ["FAB-250M54", 2], 4: ["R-60M", 1], 5: ["R-60M", 1]},
                       "devices": {}, "pylon_count": 10,
                       "fuel_internal_max": 3780, "flare": 192, "chaff": 0, "gun_rounds": 250},
        },
    },

    "Su-25TM": {
        "SEAD/Anti-Radar": {
            "loadout_code": "SU25TM-SEAD-1",
            "tasks": ["SEAD"],
            "attributes": ["Anti-radar", "Stand-off"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 680, "reference_altitude": 5000, "altitude_max": 10000, "altitude_min": 1000,
                       "range": {"fuel_25%": 182, "fuel_50%": 386, "fuel_75%": 589, "fuel_100%": 793}},
            "attack": {"speed": 780, "reference_altitude": 3000, "altitude_max": 8000, "altitude_min": 500,
                       "range": {"fuel_25%": 133, "fuel_50%": 281, "fuel_75%": 429, "fuel_100%": 577}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["Kh-25MP", 1], 2: ["Kh-25MP", 1],
                                  3: ["Kh-58", 1],
                                  4: ["R-60M", 1], 5: ["R-60M", 1]},
                       "devices": {1: ["Kopyo-25_radar", 1]},
                       "pylon_count": 10,
                       "fuel_internal_max": 3780, "flare": 192, "chaff": 0, "gun_rounds": 250},
        },
        "Precision CAS": {
            "loadout_code": "SU25TM-PSTRIKE-1",
            "tasks": ["CAS", "Pinpoint_Strike"],
            "attributes": ["Anti-tank", "Precision"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 680, "reference_altitude": 4000, "altitude_max": 9000, "altitude_min": 100,
                       "range": {"fuel_25%": 183, "fuel_50%": 387, "fuel_75%": 592, "fuel_100%": 796}},
            "attack": {"speed": 780, "reference_altitude": 1500, "altitude_max": 5000, "altitude_min": 30,
                       "range": {"fuel_25%": 133, "fuel_50%": 282, "fuel_75%": 430, "fuel_100%": 579}},
            "usability": {"day": True, "night": True, "adverse_weather": False},
            "mandatory_support": {"Escort": True, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["Kh-29T", 1], 2: ["Kh-29T", 1],
                                  3: ["Kh-25ML", 1], 4: ["Kh-25ML", 1],
                                  5: ["R-60M", 1], 6: ["R-60M", 1]},
                       "devices": {1: ["Shkval_TV", 1]},
                       "pylon_count": 10,
                       "fuel_internal_max": 3780, "flare": 192, "chaff": 0, "gun_rounds": 250},
        },
        "Strike": {
            "loadout_code": "SU25TM-STRIKE-1",
            "tasks": ["Strike"],
            "attributes": ["Area attack", "Unguided"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 670, "reference_altitude": 4000, "altitude_max": 9000, "altitude_min": 200,
                       "range": {"fuel_25%": 178, "fuel_50%": 377, "fuel_75%": 576, "fuel_100%": 775}},
            "attack": {"speed": 760, "reference_altitude": 2000, "altitude_max": 6000, "altitude_min": 200,
                       "range": {"fuel_25%": 130, "fuel_50%": 275, "fuel_75%": 420, "fuel_100%": 565}},
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {"Escort": True, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["FAB-500M62", 1], 2: ["FAB-500M62", 1],
                                  3: ["FAB-250M54", 2], 4: ["FAB-250M54", 2],
                                  5: ["R-60M", 1], 6: ["R-60M", 1]},
                       "devices": {},
                       "pylon_count": 10,
                       "fuel_internal_max": 3780, "flare": 192, "chaff": 0, "gun_rounds": 250},
        },
    },

    # =========================================================================
    # SOVIET MULTIROLE
    # =========================================================================

    "Su-27": {
        "Flanker CAP": {
            "loadout_code": "SU27-CAP-1",
            "tasks": ["CAP", "Intercept", "Fighter_Sweep"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True, "self_escort_capability": True,
            "cruise": {"speed": 900, "reference_altitude": 11000, "altitude_max": 18500, "altitude_min": 1000,
                       "range": {"fuel_25%": 245, "fuel_50%": 518, "fuel_75%": 792, "fuel_100%": 1065}},
            "attack": {"speed": 2500, "reference_altitude": 14000, "altitude_max": 18500, "altitude_min": 500,
                       "range": {"fuel_25%": 178, "fuel_50%": 377, "fuel_75%": 576, "fuel_100%": 774}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["R-27ER", 1], 2: ["R-27ER", 1],
                                  3: ["R-27ET", 1], 4: ["R-27ET", 1],
                                  5: ["R-73", 1], 6: ["R-73", 1],
                                  7: ["R-73", 1], 8: ["R-73", 1]},
                       "devices": {}, "pylon_count": 10,
                       "fuel_internal_max": 9400, "flare": 96, "chaff": 96, "gun_rounds": 150},
        },
        "Escort": {
            "loadout_code": "SU27-ESCORT-1",
            "tasks": ["Escort", "CAP"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True, "self_escort_capability": True,
            "cruise": {"speed": 880, "reference_altitude": 11000, "altitude_max": 18500, "altitude_min": 1000,
                       "range": {"fuel_25%": 262, "fuel_50%": 554, "fuel_75%": 847, "fuel_100%": 1140}},
            "attack": {"speed": 2200, "reference_altitude": 11000, "altitude_max": 18500, "altitude_min": 500,
                       "range": {"fuel_25%": 190, "fuel_50%": 403, "fuel_75%": 615, "fuel_100%": 828}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["R-27R", 1], 2: ["R-27R", 1],
                                  3: ["R-73", 1], 4: ["R-73", 1],
                                  5: ["R-73", 1], 6: ["R-73", 1],
                                  7: ["PTB-1500", 1, 1500]},
                       "devices": {}, "pylon_count": 10,
                       "fuel_internal_max": 9400, "flare": 96, "chaff": 96, "gun_rounds": 150},
        },
    },

    "Su-30": {
        "CAP/Escort": {
            "loadout_code": "SU30-CAP-1",
            "tasks": ["CAP", "Escort"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True, "self_escort_capability": True,
            "cruise": {"speed": 920, "reference_altitude": 11000, "altitude_max": 17500, "altitude_min": 1000,
                       "range": {"fuel_25%": 280, "fuel_50%": 592, "fuel_75%": 904, "fuel_100%": 1216}},
            "attack": {"speed": 2120, "reference_altitude": 14000, "altitude_max": 17500, "altitude_min": 500,
                       "range": {"fuel_25%": 204, "fuel_50%": 431, "fuel_75%": 658, "fuel_100%": 884}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["R-27ER", 1], 2: ["R-27ER", 1],
                                  3: ["R-27ET", 1], 4: ["R-27ET", 1],
                                  5: ["R-73", 1], 6: ["R-73", 1],
                                  7: ["PTB-1500", 1, 1500]},
                       "devices": {}, "pylon_count": 12,
                       "fuel_internal_max": 9400, "flare": 96, "chaff": 96, "gun_rounds": 150},
        },
        "Multirole Strike": {
            "loadout_code": "SU30-STRIKE-1",
            "tasks": ["Strike"],
            "attributes": ["Precision", "TV-guided"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 880, "reference_altitude": 8000, "altitude_max": 14000, "altitude_min": 100,
                       "range": {"fuel_25%": 260, "fuel_50%": 550, "fuel_75%": 840, "fuel_100%": 1130}},
            "attack": {"speed": 1000, "reference_altitude": 3000, "altitude_max": 8000, "altitude_min": 100,
                       "range": {"fuel_25%": 189, "fuel_50%": 400, "fuel_75%": 611, "fuel_100%": 822}},
            "usability": {"day": True, "night": True, "adverse_weather": False},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["Kh-29T", 1], 2: ["Kh-29T", 1],
                                  3: ["Kh-25ML", 1], 4: ["Kh-25ML", 1],
                                  5: ["R-73", 1], 6: ["R-73", 1]},
                       "devices": {}, "pylon_count": 12,
                       "fuel_internal_max": 9400, "flare": 96, "chaff": 96, "gun_rounds": 150},
        },
        "SEAD": {
            "loadout_code": "SU30-SEAD-1",
            "tasks": ["SEAD"],
            "attributes": ["Anti-radar", "Stand-off"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 890, "reference_altitude": 9000, "altitude_max": 14000, "altitude_min": 1000,
                       "range": {"fuel_25%": 265, "fuel_50%": 561, "fuel_75%": 857, "fuel_100%": 1152}},
            "attack": {"speed": 1000, "reference_altitude": 5000, "altitude_max": 12000, "altitude_min": 500,
                       "range": {"fuel_25%": 193, "fuel_50%": 408, "fuel_75%": 623, "fuel_100%": 838}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["Kh-58", 1], 2: ["Kh-58", 1],
                                  3: ["Kh-25MPU", 1], 4: ["Kh-25MPU", 1],
                                  5: ["R-73", 1], 6: ["R-73", 1]},
                       "devices": {}, "pylon_count": 12,
                       "fuel_internal_max": 9400, "flare": 96, "chaff": 96, "gun_rounds": 150},
        },
        "Anti-Ship": {
            "loadout_code": "SU30-ANTISHIP-1",
            "tasks": ["Anti_Ship"],
            "attributes": ["Anti-ship", "Stand-off"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 880, "reference_altitude": 100, "altitude_max": 5000, "altitude_min": 30,
                       "range": {"fuel_25%": 255, "fuel_50%": 540, "fuel_75%": 825, "fuel_100%": 1110}},
            "attack": {"speed": 1000, "reference_altitude": 50, "altitude_max": 2000, "altitude_min": 15,
                       "range": {"fuel_25%": 185, "fuel_50%": 393, "fuel_75%": 600, "fuel_100%": 807}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": True, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["Kh-59", 1], 2: ["Kh-59", 1],
                                  3: ["R-73", 1], 4: ["R-73", 1],
                                  5: ["PTB-1500", 1, 1500]},
                       "devices": {}, "pylon_count": 12,
                       "fuel_internal_max": 9400, "flare": 96, "chaff": 96, "gun_rounds": 150},
        },
    },

    "Su-33": {
        "Carrier CAP": {
            "loadout_code": "SU33-CAP-1",
            "tasks": ["CAP", "Intercept"],
            "attributes": [],
            "Lock_Down_Shoot_Down": True, "self_escort_capability": True,
            "cruise": {"speed": 900, "reference_altitude": 11000, "altitude_max": 17000, "altitude_min": 1000,
                       "range": {"fuel_25%": 235, "fuel_50%": 497, "fuel_75%": 759, "fuel_100%": 1020}},
            "attack": {"speed": 2300, "reference_altitude": 14000, "altitude_max": 17000, "altitude_min": 500,
                       "range": {"fuel_25%": 171, "fuel_50%": 361, "fuel_75%": 552, "fuel_100%": 742}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["R-27ER", 1], 2: ["R-27ER", 1],
                                  3: ["R-73", 1], 4: ["R-73", 1],
                                  5: ["R-73", 1], 6: ["R-73", 1]},
                       "devices": {}, "pylon_count": 12,
                       "fuel_internal_max": 9400, "flare": 96, "chaff": 96, "gun_rounds": 150},
        },
        "Strike": {
            "loadout_code": "SU33-STRIKE-1",
            "tasks": ["Strike"],
            "attributes": ["Dumb bomb"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 870, "reference_altitude": 7000, "altitude_max": 12000, "altitude_min": 100,
                       "range": {"fuel_25%": 218, "fuel_50%": 462, "fuel_75%": 705, "fuel_100%": 948}},
            "attack": {"speed": 1000, "reference_altitude": 2000, "altitude_max": 6000, "altitude_min": 100,
                       "range": {"fuel_25%": 158, "fuel_50%": 335, "fuel_75%": 512, "fuel_100%": 689}},
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["FAB-500M62", 2], 2: ["FAB-500M62", 2],
                                  3: ["FAB-250M54", 2], 4: ["R-73", 1], 5: ["R-73", 1]},
                       "devices": {}, "pylon_count": 12,
                       "fuel_internal_max": 9400, "flare": 96, "chaff": 96, "gun_rounds": 150},
        },
    },

    "Su-34": {
        "Precision Strike": {
            "loadout_code": "SU34-PSTRIKE-1",
            "tasks": ["Pinpoint_Strike"],
            "attributes": ["Precision", "TV-guided"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 900, "reference_altitude": 10000, "altitude_max": 14000, "altitude_min": 300,
                       "range": {"fuel_25%": 290, "fuel_50%": 614, "fuel_75%": 938, "fuel_100%": 1262}},
            "attack": {"speed": 1000, "reference_altitude": 4000, "altitude_max": 10000, "altitude_min": 100,
                       "range": {"fuel_25%": 211, "fuel_50%": 447, "fuel_75%": 682, "fuel_100%": 918}},
            "usability": {"day": True, "night": True, "adverse_weather": False},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["Kh-29T", 1], 2: ["Kh-29T", 1],
                                  3: ["Kh-29T", 1], 4: ["Kh-29T", 1],
                                  5: ["R-73", 1], 6: ["R-73", 1]},
                       "devices": {}, "pylon_count": 12,
                       "fuel_internal_max": 12100, "flare": 96, "chaff": 96, "gun_rounds": 150},
        },
        "SEAD": {
            "loadout_code": "SU34-SEAD-1",
            "tasks": ["SEAD"],
            "attributes": ["Anti-radar", "Stand-off"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 900, "reference_altitude": 10000, "altitude_max": 14000, "altitude_min": 1000,
                       "range": {"fuel_25%": 293, "fuel_50%": 620, "fuel_75%": 947, "fuel_100%": 1274}},
            "attack": {"speed": 1000, "reference_altitude": 6000, "altitude_max": 14000, "altitude_min": 500,
                       "range": {"fuel_25%": 213, "fuel_50%": 451, "fuel_75%": 689, "fuel_100%": 927}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["Kh-58", 1], 2: ["Kh-58", 1],
                                  3: ["Kh-58", 1], 4: ["Kh-58", 1],
                                  5: ["R-73", 1], 6: ["R-73", 1]},
                       "devices": {}, "pylon_count": 12,
                       "fuel_internal_max": 12100, "flare": 96, "chaff": 96, "gun_rounds": 150},
        },
        "Anti-Ship": {
            "loadout_code": "SU34-ANTISHIP-1",
            "tasks": ["Anti_Ship"],
            "attributes": ["Anti-ship", "Stand-off"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 890, "reference_altitude": 100, "altitude_max": 5000, "altitude_min": 30,
                       "range": {"fuel_25%": 285, "fuel_50%": 603, "fuel_75%": 921, "fuel_100%": 1239}},
            "attack": {"speed": 1000, "reference_altitude": 50, "altitude_max": 2000, "altitude_min": 15,
                       "range": {"fuel_25%": 207, "fuel_50%": 438, "fuel_75%": 670, "fuel_100%": 901}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": True, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["Kh-59", 1], 2: ["Kh-59", 1],
                                  3: ["R-73", 1], 4: ["R-73", 1]},
                       "devices": {}, "pylon_count": 12,
                       "fuel_internal_max": 12100, "flare": 96, "chaff": 96, "gun_rounds": 150},
        },
        "Heavy Strike": {
            "loadout_code": "SU34-STRIKE-1",
            "tasks": ["Strike"],
            "attributes": ["Area", "Dumb bomb", "Heavy payload"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": True,
            "cruise": {"speed": 880, "reference_altitude": 8000, "altitude_max": 14000, "altitude_min": 100,
                       "range": {"fuel_25%": 275, "fuel_50%": 582, "fuel_75%": 889, "fuel_100%": 1196}},
            "attack": {"speed": 1100, "reference_altitude": 2000, "altitude_max": 6000, "altitude_min": 100,
                       "range": {"fuel_25%": 200, "fuel_50%": 423, "fuel_75%": 646, "fuel_100%": 869}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": False, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["FAB-500M62", 2], 2: ["FAB-500M62", 2],
                                  3: ["FAB-500M62", 2], 4: ["FAB-500M62", 2],
                                  5: ["R-73", 1], 6: ["R-73", 1]},
                       "devices": {}, "pylon_count": 12,
                       "fuel_internal_max": 12100, "flare": 96, "chaff": 96, "gun_rounds": 150},
        },
    },

    # =========================================================================
    # SOVIET HEAVY BOMBERS
    # =========================================================================

    "Tu-22M": {
        "Anti-Ship Strike": {
            "loadout_code": "TU22M-ANTISHIP-1",
            "tasks": ["Anti_Ship"],
            "attributes": ["Anti-ship", "Stand-off", "Heavy payload"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": False,
            "cruise": {"speed": 850, "reference_altitude": 10000, "altitude_max": 13000, "altitude_min": 100,
                       "range": {"fuel_25%": 900, "fuel_50%": 1900, "fuel_75%": 2900, "fuel_100%": 3900}},
            "attack": {"speed": 1500, "reference_altitude": 100, "altitude_max": 5000, "altitude_min": 30,
                       "range": {"fuel_25%": 655, "fuel_50%": 1382, "fuel_75%": 2110, "fuel_100%": 2836}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": True, "SEAD": True, "Escort_Jammer": True,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {"bay_1": ["Kh-22N", 1], 2: ["Kh-22N", 1]},
                       "devices": {}, "pylon_count": 3,
                       "fuel_internal_max": 50000, "flare": 0, "chaff": 0, "gun_rounds": 0},
        },
        "Carpet Bomb": {
            "loadout_code": "TU22M-STRIKE-1",
            "tasks": ["Strike"],
            "attributes": ["Area", "Dumb bomb", "Heavy payload"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": False,
            "cruise": {"speed": 840, "reference_altitude": 10000, "altitude_max": 13000, "altitude_min": 3000,
                       "range": {"fuel_25%": 870, "fuel_50%": 1840, "fuel_75%": 2810, "fuel_100%": 3780}},
            "attack": {"speed": 1000, "reference_altitude": 5000, "altitude_max": 12000, "altitude_min": 3000,
                       "range": {"fuel_25%": 633, "fuel_50%": 1338, "fuel_75%": 2043, "fuel_100%": 2748}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": True, "SEAD": True, "Escort_Jammer": True,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {"bay_1": ["FAB-500M62", 12], 1: ["FAB-500M62", 4]},
                       "devices": {}, "pylon_count": 3,
                       "fuel_internal_max": 50000, "flare": 0, "chaff": 0, "gun_rounds": 0},
        },
    },

    "Tu-95MS": {
        "Strategic Strike": {
            "loadout_code": "TU95MS-STRIKE-1",
            "tasks": ["Strike"],
            "attributes": ["Strategic", "Stand-off", "Long-range"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": False,
            "cruise": {"speed": 830, "reference_altitude": 10000, "altitude_max": 12000, "altitude_min": 5000,
                       "range": {"fuel_25%": 2500, "fuel_50%": 5200, "fuel_75%": 7900, "fuel_100%": 10500}},
            "attack": {"speed": 900, "reference_altitude": 10000, "altitude_max": 12000, "altitude_min": 5000,
                       "range": {"fuel_25%": 1818, "fuel_50%": 3782, "fuel_75%": 5746, "fuel_100%": 7637}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": True, "SEAD": True, "Escort_Jammer": True,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {"bay_1": ["Kh-22N", 6]},
                       "devices": {}, "pylon_count": 1,
                       "fuel_internal_max": 87000, "flare": 0, "chaff": 0, "gun_rounds": 0},
        },
    },

    "Tu-142": {
        "Maritime Strike": {
            "loadout_code": "TU142-ANTISHIP-1",
            "tasks": ["Anti_Ship"],
            "attributes": ["Maritime", "Anti-ship"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": False,
            "cruise": {"speed": 720, "reference_altitude": 8000, "altitude_max": 12000, "altitude_min": 100,
                       "range": {"fuel_25%": 2100, "fuel_50%": 4400, "fuel_75%": 6700, "fuel_100%": 9000}},
            "attack": {"speed": 800, "reference_altitude": 200, "altitude_max": 5000, "altitude_min": 50,
                       "range": {"fuel_25%": 1527, "fuel_50%": 3200, "fuel_75%": 4873, "fuel_100%": 6545}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": True, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {"bay_1": ["FAB-500M62", 4]},
                       "devices": {1: ["Berkut_MAD", 1], 2: ["Korshun_radar", 1]},
                       "pylon_count": 1,
                       "fuel_internal_max": 87600, "flare": 0, "chaff": 0, "gun_rounds": 0},
        },
        "Maritime Recon": {
            "loadout_code": "TU142-RECON-1",
            "tasks": ["Recon"],
            "attributes": ["Maritime", "Surveillance"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": False,
            "cruise": {"speed": 700, "reference_altitude": 8000, "altitude_max": 12000, "altitude_min": 100,
                       "range": {"fuel_25%": 2200, "fuel_50%": 4600, "fuel_75%": 7000, "fuel_100%": 9400}},
            "attack": {"speed": 750, "reference_altitude": 300, "altitude_max": 5000, "altitude_min": 50,
                       "range": {"fuel_25%": 1600, "fuel_50%": 3345, "fuel_75%": 5091, "fuel_100%": 6836}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": True, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {},
                       "devices": {1: ["Berkut_MAD", 1], 2: ["Korshun_radar", 1], 3: ["sonobuoy_dispenser", 1]},
                       "pylon_count": 1,
                       "fuel_internal_max": 87600, "flare": 0, "chaff": 0, "gun_rounds": 0},
        },
    },

    "Tu-160": {
        "Strategic Strike": {
            "loadout_code": "TU160-STRIKE-1",
            "tasks": ["Strike"],
            "attributes": ["Strategic", "Stand-off", "Heavy payload"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": False,
            "cruise": {"speed": 900, "reference_altitude": 12000, "altitude_max": 16000, "altitude_min": 5000,
                       "range": {"fuel_25%": 3000, "fuel_50%": 6300, "fuel_75%": 9600, "fuel_100%": 12300}},
            "attack": {"speed": 2000, "reference_altitude": 14000, "altitude_max": 16000, "altitude_min": 5000,
                       "range": {"fuel_25%": 2182, "fuel_50%": 4582, "fuel_75%": 6982, "fuel_100%": 8945}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": True, "SEAD": True, "Escort_Jammer": True,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {"bay_1": ["Kh-22N", 6], "bay_2": ["Kh-22N", 6]},
                       "devices": {}, "pylon_count": 2,
                       "fuel_internal_max": 171000, "flare": 0, "chaff": 0, "gun_rounds": 0},
        },
        "Precision Strike": {
            "loadout_code": "TU160-PSTRIKE-1",
            "tasks": ["Pinpoint_Strike"],
            "attributes": ["Precision", "Stand-off"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": False,
            "cruise": {"speed": 920, "reference_altitude": 12000, "altitude_max": 16000, "altitude_min": 5000,
                       "range": {"fuel_25%": 3100, "fuel_50%": 6500, "fuel_75%": 9900, "fuel_100%": 12700}},
            "attack": {"speed": 2000, "reference_altitude": 12000, "altitude_max": 16000, "altitude_min": 5000,
                       "range": {"fuel_25%": 2255, "fuel_50%": 4727, "fuel_75%": 7200, "fuel_100%": 9236}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": True, "SEAD": True, "Escort_Jammer": True,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {"bay_1": ["Kh-59", 6], "bay_2": ["Kh-59", 6]},
                       "devices": {}, "pylon_count": 2,
                       "fuel_internal_max": 171000, "flare": 0, "chaff": 0, "gun_rounds": 0},
        },
    },

    # =========================================================================
    # SOVIET AWACS / TRANSPORT / SUPPORT  (standard config, no weapons)
    # =========================================================================

    "A-50": {
        "AWACS Standard": {
            "loadout_code": "A50-AWACS-1", "tasks": [], "attributes": ["AWACS", "C2", "Early Warning"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": False,
            "cruise": {"speed": 750, "reference_altitude": 9000, "altitude_max": 12000, "altitude_min": 5000,
                       "range": {"fuel_25%": 950, "fuel_50%": 2000, "fuel_75%": 3050, "fuel_100%": 4100}},
            "attack": {"speed": 800, "reference_altitude": 9000, "altitude_max": 12000, "altitude_min": 5000,
                       "range": {"fuel_25%": 691, "fuel_50%": 1455, "fuel_75%": 2218, "fuel_100%": 2982}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": True, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {}, "devices": {}, "pylon_count": 0,
                       "fuel_internal_max": 102000, "flare": 0, "chaff": 0, "gun_rounds": 0},
        },
    },

    "An-26B": {
        "Transport Standard": {
            "loadout_code": "AN26B-STD-1", "tasks": [], "attributes": ["Transport"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": False,
            "cruise": {"speed": 440, "reference_altitude": 6000, "altitude_max": 7500, "altitude_min": 100,
                       "range": {"fuel_25%": 400, "fuel_50%": 840, "fuel_75%": 1280, "fuel_100%": 1720}},
            "attack": {"speed": 500, "reference_altitude": 3000, "altitude_max": 6000, "altitude_min": 50,
                       "range": {"fuel_25%": 291, "fuel_50%": 611, "fuel_75%": 931, "fuel_100%": 1251}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": True, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {}, "devices": {}, "pylon_count": 0,
                       "fuel_internal_max": 5500, "flare": 0, "chaff": 0, "gun_rounds": 0},
        },
    },

    "An-30M": {
        "Recon Standard": {
            "loadout_code": "AN30M-RECON-1", "tasks": [], "attributes": ["Recon", "Photo"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": False,
            "cruise": {"speed": 430, "reference_altitude": 6000, "altitude_max": 8000, "altitude_min": 100,
                       "range": {"fuel_25%": 380, "fuel_50%": 800, "fuel_75%": 1220, "fuel_100%": 1640}},
            "attack": {"speed": 490, "reference_altitude": 3000, "altitude_max": 6000, "altitude_min": 100,
                       "range": {"fuel_25%": 276, "fuel_50%": 582, "fuel_75%": 887, "fuel_100%": 1193}},
            "usability": {"day": True, "night": False, "adverse_weather": False},
            "mandatory_support": {"Escort": True, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {}, "devices": {1: ["AFA_photo_camera", 1]}, "pylon_count": 0,
                       "fuel_internal_max": 5700, "flare": 0, "chaff": 0, "gun_rounds": 0},
        },
    },

    "Il-76MD": {
        "Transport Standard": {
            "loadout_code": "IL76MD-STD-1", "tasks": [], "attributes": ["Transport", "Strategic"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": False,
            "cruise": {"speed": 780, "reference_altitude": 10000, "altitude_max": 12000, "altitude_min": 100,
                       "range": {"fuel_25%": 900, "fuel_50%": 1900, "fuel_75%": 2900, "fuel_100%": 3900}},
            "attack": {"speed": 850, "reference_altitude": 5000, "altitude_max": 10000, "altitude_min": 50,
                       "range": {"fuel_25%": 655, "fuel_50%": 1382, "fuel_75%": 2109, "fuel_100%": 2836}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": True, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {}, "devices": {}, "pylon_count": 0,
                       "fuel_internal_max": 109000, "flare": 0, "chaff": 0, "gun_rounds": 0},
        },
    },

    "Il-78M": {
        "Tanker Standard": {
            "loadout_code": "IL78M-STD-1", "tasks": [], "attributes": ["Tanker", "Strategic"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": False,
            "cruise": {"speed": 800, "reference_altitude": 10000, "altitude_max": 12000, "altitude_min": 3000,
                       "range": {"fuel_25%": 950, "fuel_50%": 2000, "fuel_75%": 3050, "fuel_100%": 4100}},
            "attack": {"speed": 850, "reference_altitude": 7000, "altitude_max": 11000, "altitude_min": 2000,
                       "range": {"fuel_25%": 691, "fuel_50%": 1455, "fuel_75%": 2218, "fuel_100%": 2982}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": True, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {1: ["hose_drogue_pod", 3, 100000]}, "devices": {}, "pylon_count": 3,
                       "fuel_internal_max": 105700, "flare": 0, "chaff": 0, "gun_rounds": 0},
        },
    },

    "Yak-40": {
        "Transport Standard": {
            "loadout_code": "YAK40-STD-1", "tasks": [], "attributes": ["Transport", "Light"],
            "Lock_Down_Shoot_Down": False, "self_escort_capability": False,
            "cruise": {"speed": 500, "reference_altitude": 6000, "altitude_max": 8000, "altitude_min": 100,
                       "range": {"fuel_25%": 320, "fuel_50%": 670, "fuel_75%": 1020, "fuel_100%": 1370}},
            "attack": {"speed": 550, "reference_altitude": 3000, "altitude_max": 6000, "altitude_min": 50,
                       "range": {"fuel_25%": 233, "fuel_50%": 487, "fuel_75%": 742, "fuel_100%": 996}},
            "usability": {"day": True, "night": True, "adverse_weather": True},
            "mandatory_support": {"Escort": True, "SEAD": False, "Escort_Jammer": False,
                                   "Flare_Illumination": False, "Laser_Illumination": False},
            "stores": {"pylons": {}, "devices": {}, "pylon_count": 0,
                       "fuel_internal_max": 4500, "flare": 0, "chaff": 0, "gun_rounds": 0},
        },
    },

}  # end AIRCRAFT_LOADOUTS



