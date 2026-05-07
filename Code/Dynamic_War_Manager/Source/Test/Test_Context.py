import unittest

from Code.Dynamic_War_Manager.Source.Context.Context import (
    # Enums
    Asset_Role,
    Logistic_Asset_Type,
    Ground_Vehicle_Asset_Type,
    Air_Asset_Type,
    Sea_Asset_Type,
    Ground_Action,
    Air_To_Air_Task,
    Air_To_Ground_Task,
    Sea_Task,
    Target_Class_Name,
    Weapon_Power_Effect,
    Weapon_Area_Effect,
    VALUE,
    SHAPE3D,
    SHAPE2D,
    FOOD_CATEGORY,
    COUNTRY,
    SKILL,
    GROUP_CATEGORY,
    Parked_Asset_Type,
    # Constants
    COALITIONS,
    PATH_TYPE,
    ROUTE_TYPE,
    VEHICLE_SIZE_CATEGORY,
    SHIP_SIZE_CATEGORY,
    STRUCTURE_SIZE_CATEGORY,
    PRODUCTION_WEIGHT,
    GROUND_ACTION,
    AIR_TO_AIR_TASK,
    AIR_TO_GROUND_TASK,
    AIR_TASK,
    SEA_TASK,
    ACTION_TASKS,
    BLOCK_CATEGORY,
    MILITARY_CATEGORY,
    MILITARY_FORCES,
    SIDE,
    GROUND_COMBAT_EFFICACY,
    WEIGHT_FORCE_GROUND_ASSET,
    GROUND_WEAPON_TASK,
    GROUND_MILITARY_VEHICLE_ASSET,
    AIR_MILITARY_CRAFT_ASSET,
    SEA_MILITARY_CRAFT_ASSET,
    AIR_DEFENSE_ASSET,
    AREA_FOR_VOLUME,
    TASK_FOR_WEAPON_PARAM,
    WEAPON_PARAM_ASSIGNATION_FOR_ASSET_TYPE,
    MAX_AIRCRAFT_TYPE_FOR_MISSION,
    # Functions
    get_dimension,
    _get_task_from_weapon_param,
    _get_weapon_param_from_target,
    get_task_from_target,
)


# ---------------------------------------------------------------------------
# TestEnumValues
# ---------------------------------------------------------------------------

class TestEnumValues(unittest.TestCase):
    """Verify that each enum exposes the expected member names and .value strings."""

    def test_asset_role_values(self):
        """Asset_Role has the 5 expected members."""
        expected = {'C2', 'LOGISTIC', 'SUPPORT', 'RECONNAISSANCE', 'STRUCTURE'}
        self.assertEqual({m.name for m in Asset_Role}, expected)

    def test_asset_role_string_values(self):
        """Asset_Role .value strings are correct."""
        self.assertEqual(Asset_Role.C2.value, 'C2')
        self.assertEqual(Asset_Role.LOGISTIC.value, 'Logistic')
        self.assertEqual(Asset_Role.RECONNAISSANCE.value, 'Reconnaissance')

    def test_ground_vehicle_asset_type_values(self):
        """Ground_Vehicle_Asset_Type has the 10 expected members."""
        expected = {
            'TANK', 'ARMORED', 'MOTORIZED',
            'ARTILLERY_FIXED', 'ARTILLERY_SEMOVENT',
            'SAM_BIG', 'SAM_MEDIUM', 'SAM_SMALL', 'EWR', 'AAA',
        }
        self.assertEqual({m.name for m in Ground_Vehicle_Asset_Type}, expected)

    def test_ground_vehicle_asset_type_string_values(self):
        """Ground_Vehicle_Asset_Type .value strings are correct."""
        self.assertEqual(Ground_Vehicle_Asset_Type.TANK.value, 'Tank')
        self.assertEqual(Ground_Vehicle_Asset_Type.ARMORED.value, 'Armored')
        self.assertEqual(Ground_Vehicle_Asset_Type.SAM_BIG.value, 'SAM_Big')
        self.assertEqual(Ground_Vehicle_Asset_Type.EWR.value, 'EWR')
        self.assertEqual(Ground_Vehicle_Asset_Type.AAA.value, 'AAA')

    def test_air_asset_type_values(self):
        """Air_Asset_Type has the 9 expected members."""
        expected = {
            'FIGHTER', 'FIGHTER_BOMBER', 'ATTACKER', 'BOMBER',
            'HEAVY_BOMBER', 'AWACS', 'RECON', 'TRANSPORT', 'HELICOPTER',
        }
        self.assertEqual({m.name for m in Air_Asset_Type}, expected)

    def test_air_asset_type_string_values(self):
        """Air_Asset_Type .value strings are correct."""
        self.assertEqual(Air_Asset_Type.FIGHTER.value, 'Fighter')
        self.assertEqual(Air_Asset_Type.FIGHTER_BOMBER.value, 'Fighter_Bomber')
        self.assertEqual(Air_Asset_Type.HEAVY_BOMBER.value, 'Heavy_Bomber')
        self.assertEqual(Air_Asset_Type.AWACS.value, 'Awacs')

    def test_sea_asset_type_values(self):
        """Sea_Asset_Type has the 9 expected members."""
        expected = {
            'CARRIER', 'CRUISER', 'DESTROYER', 'FRIGATE', 'CORVETTE',
            'SUBMARINE', 'AMPHIBIOUS_ASSAULT_SHIP', 'TRANSPORT', 'CIVILIAN',
        }
        self.assertEqual({m.name for m in Sea_Asset_Type}, expected)

    def test_ground_action_values(self):
        """Ground_Action has the 4 expected members."""
        expected = {'ATTACK', 'DEFENSE', 'MAINTAIN', 'RETRAIT'}
        self.assertEqual({m.name for m in Ground_Action}, expected)
        self.assertEqual(Ground_Action.ATTACK.value, 'Attack')
        self.assertEqual(Ground_Action.MAINTAIN.value, 'Maintain')

    def test_air_to_air_task_values(self):
        """Air_To_Air_Task has the 5 expected members."""
        expected = {'CAP', 'FIGHTER_SWEEP', 'INTERCEPT', 'ESCORT', 'RECON'}
        self.assertEqual({m.name for m in Air_To_Air_Task}, expected)
        self.assertEqual(Air_To_Air_Task.FIGHTER_SWEEP.value, 'Fighter_Sweep')

    def test_air_to_ground_task_values(self):
        """Air_To_Ground_Task has the 5 expected members."""
        expected = {'CAS', 'STRIKE', 'PINPOINT_STRIKE', 'SEAD', 'ANTI_SHIP'}
        self.assertEqual({m.name for m in Air_To_Ground_Task}, expected)
        self.assertEqual(Air_To_Ground_Task.PINPOINT_STRIKE.value, 'Pinpoint_Strike')
        self.assertEqual(Air_To_Ground_Task.ANTI_SHIP.value, 'Anti_Ship')

    def test_sea_task_values(self):
        """Sea_Task has the 3 expected members."""
        expected = {'ATTACK', 'DEFENSE', 'RETRAIT'}
        self.assertEqual({m.name for m in Sea_Task}, expected)

    def test_target_class_name_military_values(self):
        """Target_Class_Name contains the expected military asset class values."""
        military_values = {
            'Soft', 'Armored', 'Hard', 'Structure', 'Air_Defense',
            'Airbase', 'Helibase', 'Port', 'Shipyard', 'Farp',
            'Stronghold', 'ship', 'Aircraft', 'Generic',
        }
        tc_values = {m.value for m in Target_Class_Name}
        self.assertTrue(military_values.issubset(tc_values))

    def test_weapon_power_effect_values(self):
        """Weapon_Power_Effect has the 8 expected members."""
        expected = {
            'PENETRATION', 'FRAGMENTATION', 'HIGH_EXPLOSIVE', 'CLUSTER',
            'THERMOBARIC', 'THERMAL', 'BLAST', 'KINETIC',
        }
        self.assertEqual({m.name for m in Weapon_Power_Effect}, expected)
        self.assertEqual(Weapon_Power_Effect.HIGH_EXPLOSIVE.value, 'High_Explosive')
        self.assertEqual(Weapon_Power_Effect.THERMOBARIC.value, 'Thermobaric')

    def test_weapon_area_effect_values(self):
        """Weapon_Area_Effect has the 3 expected members."""
        expected = {'PRECISION', 'WIDE', 'LOCALIZED'}
        self.assertEqual({m.name for m in Weapon_Area_Effect}, expected)

    def test_value_enum_values(self):
        """VALUE enum has the 6 expected level members."""
        expected = {'CRITICAL', 'VERY_HIGH', 'HIGH', 'MEDIUM', 'LOW', 'VERY_LOW'}
        self.assertEqual({m.name for m in VALUE}, expected)
        self.assertEqual(VALUE.CRITICAL.value, 'Critical')
        self.assertEqual(VALUE.VERY_HIGH.value, 'Very_High')

    def test_shape3d_values(self):
        """SHAPE3D has the 8 expected members."""
        expected = {
            'CYLINDER', 'CUBE', 'SPHERE', 'SEMISPHERE',
            'CONE', 'TRUNC_CONE', 'PRISM', 'SOLID',
        }
        self.assertEqual({m.name for m in SHAPE3D}, expected)

    def test_shape2d_values(self):
        """SHAPE2D has the 3 expected members."""
        expected = {'CIRCLE', 'SQUARE', 'HEXAGON'}
        self.assertEqual({m.name for m in SHAPE2D}, expected)

    def test_logistic_asset_type_has_expected_members(self):
        """Logistic_Asset_Type contains Bridge, Hangar, Depot, Farm, Runway, etc."""
        expected_subset = {
            'BRIDGE', 'HANGAR', 'DEPOT', 'OIL_TANK', 'FARM',
            'POWER_PLANT', 'STATION', 'BUILDING', 'FACTORY', 'BARRACK',
            'RUNWAY', 'BUNKER', 'COMMAND_AND_CONTROL',
        }
        actual = {m.name for m in Logistic_Asset_Type}
        self.assertTrue(expected_subset.issubset(actual))


# ---------------------------------------------------------------------------
# TestConstants
# ---------------------------------------------------------------------------

class TestConstants(unittest.TestCase):
    """Verify structure and content of module-level constants."""

    # ---- COALITIONS / SIDE -------------------------------------------------

    def test_coalitions_keys(self):
        """COALITIONS has exactly Blue, Red and Neutral keys."""
        self.assertEqual(set(COALITIONS.keys()), {'Blue', 'Red', 'Neutral'})

    def test_coalitions_blue_contains_expected_countries(self):
        """COALITIONS['Blue'] contains USA and Germany."""
        self.assertIn('USA', COALITIONS['Blue'])
        self.assertIn('Germany', COALITIONS['Blue'])

    def test_coalitions_red_contains_russia(self):
        """COALITIONS['Red'] contains Russia."""
        self.assertIn('Russia', COALITIONS['Red'])

    def test_coalitions_neutral_is_not_empty(self):
        """COALITIONS['Neutral'] is non-empty."""
        self.assertTrue(len(COALITIONS['Neutral']) > 0)

    def test_side_list(self):
        """SIDE contains exactly Blue, Red and Neutral in that order."""
        self.assertEqual(SIDE, ['Blue', 'Red', 'Neutral'])

    # ---- BLOCK_CATEGORY / PATH / ROUTE ------------------------------------

    def test_block_category_keys(self):
        """BLOCK_CATEGORY has Civilian, Logistic, Military and All."""
        self.assertEqual(set(BLOCK_CATEGORY.keys()), {'Civilian', 'Logistic', 'Military', 'All'})

    def test_block_category_values_match_keys(self):
        """BLOCK_CATEGORY values equal their keys."""
        for k, v in BLOCK_CATEGORY.items():
            self.assertEqual(k, v)

    def test_path_type_and_route_type(self):
        """PATH_TYPE and ROUTE_TYPE are non-empty lists of strings."""
        self.assertIsInstance(PATH_TYPE, list)
        self.assertIsInstance(ROUTE_TYPE, list)
        self.assertTrue(all(isinstance(p, str) for p in PATH_TYPE))
        self.assertIn('air', PATH_TYPE)
        self.assertIn('ground', ROUTE_TYPE)

    # ---- SIZE CATEGORIES ---------------------------------------------------

    def test_vehicle_size_category_levels(self):
        """VEHICLE_SIZE_CATEGORY has the three levels big/medium/small."""
        self.assertEqual(set(VEHICLE_SIZE_CATEGORY.keys()), {'big', 'medium', 'small'})

    def test_vehicle_size_category_fields(self):
        """Each level of VEHICLE_SIZE_CATEGORY has the 4 required fields."""
        required = {'length', 'width', 'height', 'weight'}
        for level in VEHICLE_SIZE_CATEGORY.values():
            self.assertEqual(set(level.keys()), required)

    def test_vehicle_size_big_heavier_than_medium(self):
        """big vehicle weight threshold is strictly greater than medium."""
        self.assertGreater(
            VEHICLE_SIZE_CATEGORY['big']['weight'],
            VEHICLE_SIZE_CATEGORY['medium']['weight'],
        )

    def test_ship_size_category_levels(self):
        """SHIP_SIZE_CATEGORY has the three levels big/medium/small."""
        self.assertEqual(set(SHIP_SIZE_CATEGORY.keys()), {'big', 'medium', 'small'})

    def test_ship_size_big_heavier_than_medium(self):
        """big ship weight threshold is strictly greater than medium."""
        self.assertGreater(
            SHIP_SIZE_CATEGORY['big']['weight'],
            SHIP_SIZE_CATEGORY['medium']['weight'],
        )

    def test_structure_size_category_contains_expected_types(self):
        """STRUCTURE_SIZE_CATEGORY contains Bridge, Hangar, Depot, Farm, etc."""
        expected_subset = {'Bridge', 'Hangar', 'Depot', 'Oil_Tank', 'Farm',
                           'Power_Plant', 'Station', 'Building', 'Factory', 'Barrack'}
        self.assertTrue(expected_subset.issubset(set(STRUCTURE_SIZE_CATEGORY.keys())))

    def test_structure_size_category_sub_keys(self):
        """Each structure type has exactly the Big/Medium/Small sub-keys."""
        for stype, levels in STRUCTURE_SIZE_CATEGORY.items():
            with self.subTest(structure_type=stype):
                self.assertEqual(set(levels.keys()), {'Big', 'Medium', 'Small'})

    def test_structure_size_thresholds_ordered(self):
        """For Bridge, Big.length > Medium.length > Small.length."""
        bridge = STRUCTURE_SIZE_CATEGORY['Bridge']
        self.assertGreater(bridge['Big']['length'], bridge['Medium']['length'])
        self.assertGreater(bridge['Medium']['length'], bridge['Small']['length'])

    # ---- PRODUCTION_WEIGHT ------------------------------------------------

    def test_production_weight_keys(self):
        """PRODUCTION_WEIGHT covers all 6 resource types."""
        self.assertEqual(set(PRODUCTION_WEIGHT.keys()), {'goods', 'energy', 'hr', 'hc', 'hs', 'hb'})

    def test_production_weight_values_positive(self):
        """All PRODUCTION_WEIGHT values are positive integers."""
        for resource, w in PRODUCTION_WEIGHT.items():
            with self.subTest(resource=resource):
                self.assertIsInstance(w, int)
                self.assertGreater(w, 0)

    # ---- TASK DICTS --------------------------------------------------------

    def test_ground_action_dict_built_from_enum(self):
        """GROUND_ACTION keys match Ground_Action enum values."""
        expected = {m.value for m in Ground_Action}
        self.assertEqual(set(GROUND_ACTION.keys()), expected)

    def test_air_task_is_union(self):
        """AIR_TASK is the union of AIR_TO_AIR_TASK and AIR_TO_GROUND_TASK."""
        self.assertEqual(set(AIR_TASK.keys()),
                         set(AIR_TO_AIR_TASK.keys()) | set(AIR_TO_GROUND_TASK.keys()))

    def test_sea_task_dict_built_from_enum(self):
        """SEA_TASK keys match Sea_Task enum values."""
        expected = {m.value for m in Sea_Task}
        self.assertEqual(set(SEA_TASK.keys()), expected)

    def test_action_tasks_keys(self):
        """ACTION_TASKS has the ground/air/sea keys."""
        self.assertEqual(set(ACTION_TASKS.keys()), {'ground', 'air', 'sea'})
        self.assertEqual(ACTION_TASKS['ground'], GROUND_ACTION)
        self.assertEqual(ACTION_TASKS['air'], AIR_TASK)
        self.assertEqual(ACTION_TASKS['sea'], SEA_TASK)

    # ---- MILITARY DICTS ----------------------------------------------------

    def test_military_category_keys(self):
        """MILITARY_CATEGORY has Ground_Base, Air_Base and Naval_Base."""
        self.assertEqual(set(MILITARY_CATEGORY.keys()), {'Ground_Base', 'Air_Base', 'Naval_Base'})

    def test_military_forces_list(self):
        """MILITARY_FORCES contains ground, air, sea."""
        self.assertEqual(set(MILITARY_FORCES), {'ground', 'air', 'sea'})

    def test_ground_combat_efficacy_actions(self):
        """GROUND_COMBAT_EFFICACY covers all 4 Ground_Action values."""
        expected_actions = {m.value for m in Ground_Action}
        self.assertEqual(set(GROUND_COMBAT_EFFICACY.keys()), expected_actions)

    def test_ground_combat_efficacy_vehicle_types(self):
        """Each action in GROUND_COMBAT_EFFICACY covers 5 vehicle types."""
        expected_types = {'Tank', 'Armored', 'Motorized', 'Artillery_Semovent', 'Artillery_Fixed'}
        for action, types in GROUND_COMBAT_EFFICACY.items():
            with self.subTest(action=action):
                self.assertEqual(set(types.keys()), expected_types)

    def test_weight_force_ground_asset_keys(self):
        """WEIGHT_FORCE_GROUND_ASSET covers the 5 combat vehicle types."""
        expected_types = {
            Ground_Vehicle_Asset_Type.TANK,
            Ground_Vehicle_Asset_Type.ARMORED,
            Ground_Vehicle_Asset_Type.MOTORIZED,
            Ground_Vehicle_Asset_Type.ARTILLERY_FIXED,
            Ground_Vehicle_Asset_Type.ARTILLERY_SEMOVENT,
        }
        self.assertEqual(set(WEIGHT_FORCE_GROUND_ASSET.keys()), expected_types)

    def test_ground_weapon_task_keys(self):
        """GROUND_WEAPON_TASK contains Anti_Tank, Anti_Air, Artillery, Infantry_Support."""
        expected = {'Anti_Tank', 'Anti_Air', 'Artillery', 'Infantry_Support'}
        self.assertEqual(set(GROUND_WEAPON_TASK.keys()), expected)

    # ---- ASSET DICTS -------------------------------------------------------

    def test_air_military_craft_asset_covers_all_types(self):
        """AIR_MILITARY_CRAFT_ASSET covers all Air_Asset_Type values."""
        expected = {m.value for m in Air_Asset_Type}
        self.assertEqual(set(AIR_MILITARY_CRAFT_ASSET.keys()), expected)

    def test_sea_military_craft_asset_covers_all_types(self):
        """SEA_MILITARY_CRAFT_ASSET covers all Sea_Asset_Type values."""
        expected = {m.value for m in Sea_Asset_Type}
        self.assertEqual(set(SEA_MILITARY_CRAFT_ASSET.keys()), expected)

    def test_ground_military_vehicle_asset_covers_combat_types(self):
        """GROUND_MILITARY_VEHICLE_ASSET covers Tank, Armored, Motorized, and Artillery types."""
        expected_subset = {
            Ground_Vehicle_Asset_Type.TANK.value,
            Ground_Vehicle_Asset_Type.ARMORED.value,
            Ground_Vehicle_Asset_Type.MOTORIZED.value,
            Ground_Vehicle_Asset_Type.ARTILLERY_FIXED.value,
            Ground_Vehicle_Asset_Type.ARTILLERY_SEMOVENT.value,
        }
        self.assertTrue(expected_subset.issubset(set(GROUND_MILITARY_VEHICLE_ASSET.keys())))

    def test_air_defense_asset_keys(self):
        """AIR_DEFENSE_ASSET has SAM, EWR and AAA top-level keys."""
        self.assertEqual(set(AIR_DEFENSE_ASSET.keys()), {'SAM', 'EWR', 'AAA'})

    def test_sam_big_sub_components(self):
        """AIR_DEFENSE_ASSET['SAM']['Big'] has Command_&_Control and Launcher."""
        sam_big = AIR_DEFENSE_ASSET['SAM']['Big']
        self.assertIn('Command_&_Control', sam_big)
        self.assertIn('Launcher', sam_big)

    # ---- AREA_FOR_VOLUME ---------------------------------------------------

    def test_area_for_volume_keys_are_shape2d(self):
        """AREA_FOR_VOLUME keys are SHAPE2D enum members."""
        for key in AREA_FOR_VOLUME:
            self.assertIsInstance(key, SHAPE2D)

    def test_area_for_volume_circle_includes_cylinder(self):
        """AREA_FOR_VOLUME[CIRCLE] contains CYLINDER."""
        self.assertIn(SHAPE3D.CYLINDER, AREA_FOR_VOLUME[SHAPE2D.CIRCLE])

    def test_area_for_volume_square_includes_cube(self):
        """AREA_FOR_VOLUME[SQUARE] contains CUBE."""
        self.assertIn(SHAPE3D.CUBE, AREA_FOR_VOLUME[SHAPE2D.SQUARE])

    # ---- TASK_FOR_WEAPON_PARAM / WEAPON_PARAM_ASSIGNATION ------------------

    def test_task_for_weapon_param_keys(self):
        """TASK_FOR_WEAPON_PARAM has Pinpoint_Strike and Strike entries."""
        self.assertIn(Air_To_Ground_Task.PINPOINT_STRIKE.value, TASK_FOR_WEAPON_PARAM)
        self.assertIn(Air_To_Ground_Task.STRIKE.value, TASK_FOR_WEAPON_PARAM)

    def test_weapon_param_assignation_sections(self):
        """WEAPON_PARAM_ASSIGNATION_FOR_ASSET_TYPE has area_effect and power_effect sections."""
        self.assertIn('area_effect', WEAPON_PARAM_ASSIGNATION_FOR_ASSET_TYPE)
        self.assertIn('power_effect', WEAPON_PARAM_ASSIGNATION_FOR_ASSET_TYPE)

    def test_max_aircraft_type_for_mission_is_positive(self):
        """MAX_AIRCRAFT_TYPE_FOR_MISSION is a positive integer."""
        self.assertIsInstance(MAX_AIRCRAFT_TYPE_FOR_MISSION, int)
        self.assertGreater(MAX_AIRCRAFT_TYPE_FOR_MISSION, 0)


# ---------------------------------------------------------------------------
# TestGetDimensionVehicle
# ---------------------------------------------------------------------------

class TestGetDimensionVehicle(unittest.TestCase):
    """Unit tests for get_dimension() with asset_type='Vehicle'."""

    def test_big_vehicle_typical_tank(self):
        """Tank-class vehicle (62t, 9.8m) is classified as 'big'."""
        result = get_dimension('Vehicle', length=9.8, width=3.7, height=2.4, weight=62)
        self.assertEqual(result, 'big')

    def test_big_vehicle_exactly_at_threshold(self):
        """Vehicle exactly at the big threshold (8m, 40t) is 'big'."""
        result = get_dimension('Vehicle', length=8.0, width=3.0, height=2.0, weight=40)
        self.assertEqual(result, 'big')

    def test_big_vehicle_via_width_height(self):
        """Vehicle qualifies as 'big' via width+height match even with shorter length."""
        # length < 8 but width >= 3 AND height >= 2 AND weight >= 40
        result = get_dimension('Vehicle', length=7, width=3.5, height=2.5, weight=45)
        self.assertEqual(result, 'big')

    def test_medium_vehicle_typical_ifv(self):
        """IFV-class vehicle (28t, 7m) is classified as 'medium'."""
        result = get_dimension('Vehicle', length=7.0, width=2.5, height=2.5, weight=30)
        self.assertEqual(result, 'medium')

    def test_medium_vehicle_exactly_at_threshold(self):
        """Vehicle exactly at the medium threshold (6m, 20t) is 'medium'."""
        result = get_dimension('Vehicle', length=6.0, width=2.0, height=2.0, weight=20)
        self.assertEqual(result, 'medium')

    def test_small_vehicle_typical_apc(self):
        """APC-class vehicle (14t, 4m) is classified as 'small'."""
        result = get_dimension('Vehicle', length=4.0, width=1.8, height=1.8, weight=14)
        self.assertEqual(result, 'small')

    def test_small_vehicle_exactly_at_threshold(self):
        """Vehicle exactly at the small threshold (2m, 1t) is 'small'."""
        result = get_dimension('Vehicle', length=2.0, width=1.0, height=1.0, weight=1)
        self.assertEqual(result, 'small')

    def test_unknown_vehicle_tiny_dimensions(self):
        """Vehicle below all thresholds returns 'Unknown'."""
        result = get_dimension('Vehicle', length=0.5, width=0.5, height=0.5, weight=0.5)
        self.assertEqual(result, 'Unknown')

    def test_below_big_weight_falls_to_medium(self):
        """Vehicle with big-length but insufficient weight falls to 'medium'."""
        # length=9 satisfies big size, but weight=30 < 40 → big fails; medium matches
        result = get_dimension('Vehicle', length=9, width=2.5, height=2.5, weight=30)
        self.assertEqual(result, 'medium')

    def test_below_medium_weight_falls_to_small(self):
        """Vehicle with medium-length but insufficient weight falls to 'small'."""
        result = get_dimension('Vehicle', length=7, width=2.5, height=2.5, weight=5)
        self.assertEqual(result, 'small')


# ---------------------------------------------------------------------------
# TestGetDimensionShip
# ---------------------------------------------------------------------------

class TestGetDimensionShip(unittest.TestCase):
    """Unit tests for get_dimension() with asset_type='Ship'."""

    def test_big_ship_carrier_class(self):
        """Carrier-class ship (103kt, 333m) is classified as 'big'."""
        result = get_dimension('Ship', length=333, width=76, height=65, weight=103000)
        self.assertEqual(result, 'big')

    def test_big_ship_exactly_at_threshold(self):
        """Ship exactly at the big threshold (200m, 24000t) is 'big'."""
        result = get_dimension('Ship', length=200, width=28, height=40, weight=24000)
        self.assertEqual(result, 'big')

    def test_medium_ship_destroyer_class(self):
        """Destroyer-class ship (9100t, 155m) is classified as 'medium'."""
        result = get_dimension('Ship', length=155, width=20, height=20, weight=9100)
        self.assertEqual(result, 'medium')

    def test_medium_ship_exactly_at_threshold(self):
        """Ship exactly at the medium threshold (90m, 3000t) is 'medium'."""
        result = get_dimension('Ship', length=90, width=10, height=10, weight=3000)
        self.assertEqual(result, 'medium')

    def test_small_ship_corvette_class(self):
        """Corvette-class ship (950t, 71m) is classified as 'small'."""
        result = get_dimension('Ship', length=71, width=10, height=12, weight=950)
        self.assertEqual(result, 'small')

    def test_unknown_ship_tiny_dimensions(self):
        """Boat below all ship thresholds returns 'Unknown'."""
        result = get_dimension('Ship', length=10, width=3, height=3, weight=50)
        self.assertEqual(result, 'Unknown')

    def test_big_ship_via_width_height(self):
        """Ship with width>=28 and height>=40 qualifies as 'big' regardless of length."""
        result = get_dimension('Ship', length=150, width=30, height=45, weight=25000)
        self.assertEqual(result, 'big')


# ---------------------------------------------------------------------------
# TestGetDimensionStructure
# ---------------------------------------------------------------------------

class TestGetDimensionStructure(unittest.TestCase):
    """Unit tests for get_dimension() with asset_type='Structure'."""

    def test_bridge_big(self):
        """Bridge with length>=100 is 'Big'."""
        result = get_dimension('Structure', length=120, width=25, height=25, weight=0,
                               structure_type='Bridge')
        self.assertEqual(result, 'Big')

    def test_bridge_big_exactly_at_threshold(self):
        """Bridge exactly at Big threshold (100m, 20m, 20m) is 'Big'."""
        result = get_dimension('Structure', length=100, width=20, height=20, weight=0,
                               structure_type='Bridge')
        self.assertEqual(result, 'Big')

    def test_bridge_medium(self):
        """Bridge with 50<=length<100 is 'Medium'."""
        result = get_dimension('Structure', length=70, width=12, height=12, weight=0,
                               structure_type='Bridge')
        self.assertEqual(result, 'Medium')

    def test_bridge_medium_exactly_at_threshold(self):
        """Bridge exactly at Medium threshold (50m) is 'Medium'."""
        result = get_dimension('Structure', length=50, width=10, height=10, weight=0,
                               structure_type='Bridge')
        self.assertEqual(result, 'Medium')

    def test_bridge_small(self):
        """Bridge with 20<=length<50 is 'Small'."""
        result = get_dimension('Structure', length=30, width=6, height=6, weight=0,
                               structure_type='Bridge')
        self.assertEqual(result, 'Small')

    def test_bridge_unknown(self):
        """Bridge below all thresholds returns 'Unknown'."""
        result = get_dimension('Structure', length=5, width=2, height=2, weight=0,
                               structure_type='Bridge')
        self.assertEqual(result, 'Unknown')

    def test_structure_weight_is_irrelevant(self):
        """Very high weight does not affect structure classification."""
        r1 = get_dimension('Structure', length=120, width=25, height=25, weight=0,
                           structure_type='Bridge')
        r2 = get_dimension('Structure', length=120, width=25, height=25, weight=999999,
                           structure_type='Bridge')
        self.assertEqual(r1, r2)

    def test_hangar_big(self):
        """Hangar with length>=100 is 'Big'."""
        result = get_dimension('Structure', length=110, width=60, height=35, weight=0,
                               structure_type='Hangar')
        self.assertEqual(result, 'Big')

    def test_hangar_small(self):
        """Hangar with length>=20 (but <50) is 'Small'."""
        result = get_dimension('Structure', length=25, width=12, height=12, weight=0,
                               structure_type='Hangar')
        self.assertEqual(result, 'Small')

    def test_farm_big(self):
        """Farm with length>=200 is 'Big'."""
        result = get_dimension('Structure', length=200, width=200, height=10, weight=0,
                               structure_type='Farm')
        self.assertEqual(result, 'Big')

    def test_oil_tank_small(self):
        """Oil_Tank with length>=10 is 'Small'."""
        result = get_dimension('Structure', length=12, width=12, height=12, weight=0,
                               structure_type='Oil_Tank')
        self.assertEqual(result, 'Small')

    def test_oil_tank_big(self):
        """Oil_Tank with length>=30 is 'Big'."""
        result = get_dimension('Structure', length=35, width=35, height=35, weight=0,
                               structure_type='Oil_Tank')
        self.assertEqual(result, 'Big')


# ---------------------------------------------------------------------------
# TestGetDimensionErrors
# ---------------------------------------------------------------------------

class TestGetDimensionErrors(unittest.TestCase):
    """Error handling in get_dimension()."""

    def test_invalid_asset_type_raises_value_error(self):
        """Passing an unknown asset_type raises ValueError."""
        with self.assertRaises(ValueError):
            get_dimension('Missile', length=5, width=1, height=1, weight=1)

    def test_negative_length_raises_value_error(self):
        """Negative length raises ValueError."""
        with self.assertRaises(ValueError):
            get_dimension('Vehicle', length=-1, width=2, height=2, weight=10)

    def test_negative_width_raises_value_error(self):
        """Negative width raises ValueError."""
        with self.assertRaises(ValueError):
            get_dimension('Vehicle', length=5, width=-1, height=2, weight=10)

    def test_negative_height_raises_value_error(self):
        """Negative height raises ValueError."""
        with self.assertRaises(ValueError):
            get_dimension('Vehicle', length=5, width=2, height=-1, weight=10)

    def test_negative_weight_raises_value_error(self):
        """Negative weight raises ValueError."""
        with self.assertRaises(ValueError):
            get_dimension('Vehicle', length=5, width=2, height=2, weight=-1)

    def test_structure_without_structure_type_raises_value_error(self):
        """Structure asset_type without structure_type raises ValueError."""
        with self.assertRaises(ValueError):
            get_dimension('Structure', length=50, width=10, height=10, weight=0)

    def test_structure_invalid_structure_type_raises_value_error(self):
        """Unknown structure_type raises ValueError."""
        with self.assertRaises(ValueError):
            get_dimension('Structure', length=50, width=10, height=10, weight=0,
                          structure_type='NonExistentStructure')

    def test_zero_dimensions_vehicle_returns_unknown(self):
        """All-zero dimensions return 'Unknown' (no negative values, no error)."""
        result = get_dimension('Vehicle', length=0, width=0, height=0, weight=0)
        self.assertEqual(result, 'Unknown')


# ---------------------------------------------------------------------------
# TestGetTaskFromWeaponParam
# ---------------------------------------------------------------------------

class TestGetTaskFromWeaponParam(unittest.TestCase):
    """Unit tests for _get_task_from_weapon_param()."""

    # ---- Pinpoint_Strike cases -------------------------------------------

    def test_precision_high_explosive_gives_pinpoint_strike(self):
        """Precision + High_Explosive → Pinpoint_Strike (cond1)."""
        result = _get_task_from_weapon_param(
            ['Precision'], ['High_Explosive'])
        self.assertEqual(result, 'Pinpoint_Strike')

    def test_precision_penetration_gives_pinpoint_strike(self):
        """Precision + Penetration → Pinpoint_Strike (cond1)."""
        result = _get_task_from_weapon_param(
            ['Precision'], ['Penetration'])
        self.assertEqual(result, 'Pinpoint_Strike')

    def test_precision_kinetic_gives_pinpoint_strike(self):
        """Precision + Kinetic → Pinpoint_Strike (cond1)."""
        result = _get_task_from_weapon_param(
            ['Precision'], ['Kinetic'])
        self.assertEqual(result, 'Pinpoint_Strike')

    def test_localized_high_explosive_gives_pinpoint_strike(self):
        """Localized + High_Explosive → Pinpoint_Strike (cond2: area=[Precision,Localized], power=[HE,Penetration])."""
        result = _get_task_from_weapon_param(
            ['Localized'], ['High_Explosive'])
        self.assertEqual(result, 'Pinpoint_Strike')

    def test_localized_penetration_gives_pinpoint_strike(self):
        """Localized + Penetration → Pinpoint_Strike (cond2)."""
        result = _get_task_from_weapon_param(
            ['Localized'], ['Penetration'])
        self.assertEqual(result, 'Pinpoint_Strike')

    # ---- Strike cases ----------------------------------------------------

    def test_precision_blast_gives_strike(self):
        """Precision + Blast → Strike (Strike cond1)."""
        result = _get_task_from_weapon_param(
            ['Precision'], ['Blast'])
        self.assertEqual(result, 'Strike')

    def test_precision_fragmentation_gives_strike(self):
        """Precision + Fragmentation → Strike (Strike cond1)."""
        result = _get_task_from_weapon_param(
            ['Precision'], ['Fragmentation'])
        self.assertEqual(result, 'Strike')

    def test_localized_blast_gives_strike(self):
        """Localized + Blast → Strike (Strike cond2)."""
        result = _get_task_from_weapon_param(
            ['Localized'], ['Blast'])
        self.assertEqual(result, 'Strike')

    def test_wide_high_explosive_gives_strike(self):
        """Wide + High_Explosive → Strike (Strike cond2)."""
        result = _get_task_from_weapon_param(
            ['Wide'], ['High_Explosive'])
        self.assertEqual(result, 'Strike')

    def test_wide_kinetic_gives_strike(self):
        """Wide + Kinetic → Strike (Strike cond2)."""
        result = _get_task_from_weapon_param(
            ['Wide'], ['Kinetic'])
        self.assertEqual(result, 'Strike')

    # ---- No-match case ---------------------------------------------------

    def test_no_match_returns_none(self):
        """No matching condition returns None (Cluster not in Strike or Pinpoint power lists)."""
        result = _get_task_from_weapon_param(
            ['Wide'], ['Cluster'])
        self.assertIsNone(result)

    # ---- Error cases -----------------------------------------------------

    def test_empty_area_effect_raises_value_error(self):
        """Empty area_effect list raises ValueError."""
        with self.assertRaises(ValueError):
            _get_task_from_weapon_param([], ['Blast'])

    def test_empty_power_effect_raises_value_error(self):
        """Empty power_effect list raises ValueError."""
        with self.assertRaises(ValueError):
            _get_task_from_weapon_param(['Precision'], [])

    def test_non_list_area_effect_raises_value_error(self):
        """Non-list area_effect raises ValueError."""
        with self.assertRaises(ValueError):
            _get_task_from_weapon_param('Precision', ['Blast'])

    def test_non_list_power_effect_raises_value_error(self):
        """Non-list power_effect raises ValueError."""
        with self.assertRaises(ValueError):
            _get_task_from_weapon_param(['Precision'], 'Blast')

    def test_invalid_area_effect_value_raises_value_error(self):
        """Unknown area_effect string raises ValueError."""
        with self.assertRaises(ValueError):
            _get_task_from_weapon_param(['SuperPrecision'], ['Blast'])

    def test_invalid_power_effect_value_raises_value_error(self):
        """Unknown power_effect string raises ValueError."""
        with self.assertRaises(ValueError):
            _get_task_from_weapon_param(['Precision'], ['MegaBlast'])

    def test_multiple_power_effects_first_match_wins(self):
        """When multiple power effects are provided, the first matching one determines the task."""
        # Blast matches Strike; Penetration would match Pinpoint — Pinpoint is checked first
        # Precision + [Penetration, Blast] → Pinpoint_Strike (Penetration matches Pinpoint cond1)
        result = _get_task_from_weapon_param(
            ['Precision'], ['Penetration', 'Blast'])
        self.assertEqual(result, 'Pinpoint_Strike')


# ---------------------------------------------------------------------------
# TestGetWeaponParamFromTarget
# ---------------------------------------------------------------------------

class TestGetWeaponParamFromTarget(unittest.TestCase):
    """Unit tests for _get_weapon_param_from_target()."""

    # ---- Soft target (Big) -----------------------------------------------

    def test_soft_big_count_1_area_precision(self):
        """Soft / Big / 1 unit → area_effect=Precision."""
        wp = _get_weapon_param_from_target('Soft', 'Big', 1)
        self.assertEqual(wp['area_effect'], 'Precision')

    def test_soft_big_count_2_area_precision(self):
        """Soft / Big / 2 units → still Precision (range 1-2)."""
        wp = _get_weapon_param_from_target('Soft', 'Big', 2)
        self.assertEqual(wp['area_effect'], 'Precision')

    def test_soft_big_count_3_area_localized(self):
        """Soft / Big / 3 units → area_effect=Localized."""
        wp = _get_weapon_param_from_target('Soft', 'Big', 3)
        self.assertEqual(wp['area_effect'], 'Localized')

    def test_soft_big_count_7_area_wide(self):
        """Soft / Big / 7 units → area_effect=Wide."""
        wp = _get_weapon_param_from_target('Soft', 'Big', 7)
        self.assertEqual(wp['area_effect'], 'Wide')

    def test_soft_big_power_effect(self):
        """Soft / Big → power_effect includes Blast, Cluster, Fragmentation, Thermobaric."""
        wp = _get_weapon_param_from_target('Soft', 'Big', 1)
        expected = {'Blast', 'Cluster', 'Fragmentation', 'Thermobaric'}
        self.assertEqual(set(wp['power_effect']), expected)

    # ---- Soft target (Med) -----------------------------------------------

    def test_soft_med_count_1_area_precision(self):
        """Soft / Med / 1 unit → Precision (range 1-4 for Med)."""
        wp = _get_weapon_param_from_target('Soft', 'Med', 1)
        self.assertEqual(wp['area_effect'], 'Precision')

    def test_soft_med_count_5_area_localized(self):
        """Soft / Med / 5 units → Localized (range 5-8 for Med)."""
        wp = _get_weapon_param_from_target('Soft', 'Med', 5)
        self.assertEqual(wp['area_effect'], 'Localized')

    def test_soft_med_count_9_area_wide(self):
        """Soft / Med / 9 units → Wide (range 9+ for Med)."""
        wp = _get_weapon_param_from_target('Soft', 'Med', 9)
        self.assertEqual(wp['area_effect'], 'Wide')

    # ---- Soft target (Small) ---------------------------------------------

    def test_soft_small_count_1_area_precision(self):
        """Soft / Small / 1 unit → Precision (range 1-1)."""
        wp = _get_weapon_param_from_target('Soft', 'Small', 1)
        self.assertEqual(wp['area_effect'], 'Precision')

    def test_soft_small_count_2_area_localized(self):
        """Soft / Small / 2 units → Localized (range 2-7)."""
        wp = _get_weapon_param_from_target('Soft', 'Small', 2)
        self.assertEqual(wp['area_effect'], 'Localized')

    # ---- Hard target -----------------------------------------------------

    def test_hard_big_count_1_area_precision(self):
        """Hard / Big / 1 unit → Precision (range 1-4)."""
        wp = _get_weapon_param_from_target('Hard', 'Big', 1)
        self.assertEqual(wp['area_effect'], 'Precision')

    def test_hard_big_count_5_area_localized(self):
        """Hard / Big / 5 units → Localized (range 5-9)."""
        wp = _get_weapon_param_from_target('Hard', 'Big', 5)
        self.assertEqual(wp['area_effect'], 'Localized')

    def test_hard_big_count_10_area_wide(self):
        """Hard / Big / 10 units → Wide (range 10+)."""
        wp = _get_weapon_param_from_target('Hard', 'Big', 10)
        self.assertEqual(wp['area_effect'], 'Wide')

    def test_hard_big_power_effect(self):
        """Hard / Big → power_effect includes High_Explosive, Penetration, Kinetic."""
        wp = _get_weapon_param_from_target('Hard', 'Big', 1)
        expected = {'High_Explosive', 'Penetration', 'Kinetic'}
        self.assertEqual(set(wp['power_effect']), expected)

    # ---- Ship target -----------------------------------------------------

    def test_ship_big_always_precision(self):
        """Ship / Big → always Precision regardless of count."""
        for count in (1, 5, 100):
            with self.subTest(count=count):
                wp = _get_weapon_param_from_target('ship', 'Big', count)
                self.assertEqual(wp['area_effect'], 'Precision')

    def test_ship_big_power_effect(self):
        """Ship / Big → power_effect includes High_Explosive and Kinetic."""
        wp = _get_weapon_param_from_target('ship', 'Big', 1)
        self.assertIn('High_Explosive', wp['power_effect'])
        self.assertIn('Kinetic', wp['power_effect'])

    # ---- Error cases -----------------------------------------------------

    def test_invalid_target_type_raises_value_error(self):
        """Unknown target_type raises ValueError."""
        with self.assertRaises(ValueError):
            _get_weapon_param_from_target('InvalidType', 'Big', 1)

    def test_invalid_target_dim_raises_value_error(self):
        """Unknown target_dim raises ValueError."""
        with self.assertRaises(ValueError):
            _get_weapon_param_from_target('Soft', 'Huge', 1)

    def test_target_count_zero_raises_value_error(self):
        """target_count=0 raises ValueError (must be >= 1)."""
        with self.assertRaises(ValueError):
            _get_weapon_param_from_target('Soft', 'Big', 0)

    def test_target_count_negative_raises_value_error(self):
        """Negative target_count raises ValueError."""
        with self.assertRaises(ValueError):
            _get_weapon_param_from_target('Soft', 'Big', -3)

    def test_target_count_non_int_raises_value_error(self):
        """Float target_count raises ValueError."""
        with self.assertRaises(ValueError):
            _get_weapon_param_from_target('Soft', 'Big', 1.5)


# ---------------------------------------------------------------------------
# TestGetTaskFromTarget
# ---------------------------------------------------------------------------

class TestGetTaskFromTarget(unittest.TestCase):
    """Integration tests for the public get_task_from_target() API."""

    def test_hard_big_single_gives_pinpoint_strike(self):
        """Hard / Big / 1 unit → Pinpoint_Strike (Precision + HE/Penetration/Kinetic)."""
        result = get_task_from_target('Hard', 'Big', 1)
        self.assertEqual(result, 'Pinpoint_Strike')

    def test_soft_big_single_gives_strike(self):
        """Soft / Big / 1 unit → Strike (Precision + Blast/Cluster/Frag/Thermobaric)."""
        result = get_task_from_target('Soft', 'Big', 1)
        self.assertEqual(result, 'Strike')

    def test_soft_big_many_units_gives_strike(self):
        """Soft / Big / 7 units → Strike (Wide + Blast/...)."""
        result = get_task_from_target('Soft', 'Big', 7)
        self.assertEqual(result, 'Strike')

    def test_armored_big_single_gives_strike(self):
        """Armored / Big / 1 unit → Strike (same power group as Soft)."""
        result = get_task_from_target('Armored', 'Big', 1)
        self.assertEqual(result, 'Strike')

    def test_ship_big_single_gives_pinpoint_strike(self):
        """Ship / Big / 1 unit → Pinpoint_Strike (Precision + HE/Kinetic)."""
        result = get_task_from_target('ship', 'Big', 1)
        self.assertEqual(result, 'Pinpoint_Strike')

    def test_structure_big_single_gives_pinpoint_strike(self):
        """Structure / Big / 1 unit → Pinpoint_Strike (Precision + HE/Blast/Frag/Kinetic)."""
        result = get_task_from_target('Structure', 'Big', 1)
        self.assertEqual(result, 'Pinpoint_Strike')

    def test_airbase_big_single_gives_pinpoint_strike(self):
        """Airbase / Big / 1 unit → Pinpoint_Strike (Precision + HE/Thermal/Frag/Blast)."""
        result = get_task_from_target('Airbase', 'Big', 1)
        self.assertEqual(result, 'Pinpoint_Strike')

    def test_stronghold_big_single_gives_pinpoint_strike(self):
        """Stronghold / Big / 1 unit → Pinpoint_Strike (Precision + HE/Penetration/Kinetic)."""
        result = get_task_from_target('Stronghold', 'Big', 1)
        self.assertEqual(result, 'Pinpoint_Strike')

    def test_invalid_target_type_propagates_value_error(self):
        """Invalid target_type propagates ValueError from the inner helper."""
        with self.assertRaises(ValueError):
            get_task_from_target('InvalidType', 'Big', 1)

    def test_invalid_target_dim_propagates_value_error(self):
        """Invalid target_dim propagates ValueError."""
        with self.assertRaises(ValueError):
            get_task_from_target('Soft', 'Huge', 1)

    def test_zero_count_propagates_value_error(self):
        """target_count=0 propagates ValueError."""
        with self.assertRaises(ValueError):
            get_task_from_target('Soft', 'Big', 0)

    def test_result_is_valid_air_to_ground_task(self):
        """get_task_from_target always returns an Air_To_Ground_Task value (or None)."""
        valid_tasks = {m.value for m in Air_To_Ground_Task} | {None}
        test_cases = [
            ('Soft', 'Big', 1),
            ('Hard', 'Big', 1),
            ('ship', 'Big', 1),
            ('Structure', 'Med', 3),
            ('Armored', 'Small', 8),
        ]
        for tt, td, tc in test_cases:
            with self.subTest(target_type=tt, target_dim=td, target_count=tc):
                result = get_task_from_target(tt, td, tc)
                self.assertIn(result, valid_tasks)


if __name__ == '__main__':
    unittest.main()
