"""
 MODULE Military Resources Assigner

methods for allocating military resources: aircraft, vehicle, ecc.

"""

from __future__ import annotations  # must be the very first statement

import copy
from typing import Dict, List, Optional, Tuple

from Code.Dynamic_War_Manager.Source.Context.Context import AIR_TASK, AIR_TO_AIR_TASK, AIR_TO_GROUND_TASK
from Code.Dynamic_War_Manager.Source.Context.Campaign_State import Campaign_State
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Loadouts import (
    AIRCRAFT_LOADOUTS,
    get_aircrafts_quantity,
    loadout_cost,
    get_loadout,
    get_aircraft_loadouts_by_task,
    get_weapons_by_loadout
)
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import Aircraft_Data
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger


logger = Logger(module_name=__name__, class_name='Military_Resources_Assigner').logger


"""
DATA STRUCTURE

_ASSET_AVAILABILITY: Dict[str, Tuple[float, float]] = {   

        'air': {at.FIGHTER.value: {
                    'F-14A Tomcat': 100,
                    'F-14B Tomcat': 100,        
                },
                at.FIGHTER_BOMBER.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,                                
        }, 

        'ground': {
                ag.TANK.value: {
                    'F-14A Tomcat': 100,
                    'F-14B Tomcat': 100,
                    },
                ag.ARMORED.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                },
                
        },

        'sea': {asea.CARRIER.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,                    
                },
                asea.DESTROYER.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,                    
                },                           
            },
}"""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DIRECTIVE_WEIGHTS: Dict[str, Tuple[float, float]] = {
    'performance_high': (1.00, 0.00),
    'performance':      (0.75, 0.25),
    'balanced':         (0.50, 0.50),
    'economy':          (0.25, 0.75),
    'economy_high':     (0.10, 0.90),
}

# Reference total cost [k$] used to normalise the cost factor (≈ average fighter+loadout)
_REFERENCE_COST_K: float = 303_000.0




# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _extract_quantities(target_data: Dict) -> Dict:
    """Convert ``{type: {dim: {'quantity': int, 'priority': int}}}`` to
    ``{type: {dim: int}}`` as expected by ``get_aircrafts_quantity``."""
    result = {}
    for target_type, dims in target_data.items():
        result[target_type] = {}
        for dim, data in dims.items():
            result[target_type][dim] = data['quantity'] if isinstance(data, dict) else int(data)
    return result

def _extract_target_lists(target_data: Dict) -> Tuple[List[str], List[str]]:
    """Return ``(target_types, target_dimensions)`` lists from *target_data*."""
    types: List[str] = []
    dims: List[str] = []
    for t_type, t_dims in target_data.items():
        for dim in t_dims:
            if t_type not in types:
                types.append(t_type)
            if dim not in dims:
                dims.append(dim)
    return types, dims

def _check_mission_requirements(loadout: Dict, mission_requirements: Dict) -> bool:
    """Return *True* if *loadout* satisfies cruise and attack *mission_requirements*.

    ``loadout[phase]['range']`` is a dict ``{'fuel_25%': km, …, 'fuel_100%': km}``;
    the comparison uses ``fuel_100%`` (maximum range).
    """
    for phase in ('cruise', 'attack'):
        req = mission_requirements.get(phase, {})
        lo  = loadout.get(phase, {})
        if not req or not lo:
            return False

        lo_range  = lo.get('range', {})
        lo_range_max = lo_range.get('fuel_100%', 0) if isinstance(lo_range, dict) else lo_range

        if not (
            lo.get('speed', 0)              >= req.get('speed', 0)              and
            lo.get('altitude_max', 0)>= req.get('reference_altitude', 0) and
            lo.get('altitude_max', 0) >= req.get('altitude_max', 0) <= lo.get('altitude_min', float('inf')) and
            lo.get('altitude_min', float('inf')) <= req.get('altitude_min', float('inf')) and
            lo_range_max >= req.get('range', 0)
        ):
            return False
    return True

def _usability_met(loadout_usability: Dict, required_usability: Dict) -> bool:
    """Return *True* if *loadout_usability* satisfies every condition required by *required_usability*.

    Both arguments have the form ``{'day': bool, 'night': bool, 'adverse_weather': bool}``.
    A condition in *required_usability* set to ``True`` means the mission demands that capability;
    the loadout must also expose it as ``True``.  Conditions set to ``False`` in the requirement
    are ignored (the mission does not need them).

    Examples::

        _usability_met({'day': True, 'night': True,  'adverse_weather': False},
                       {'day': True, 'night': False, 'adverse_weather': False})
        # → True  (mission needs day only; loadout supports day)

        _usability_met({'day': True, 'night': False, 'adverse_weather': False},
                       {'day': True, 'night': True,  'adverse_weather': False})
        # → False (mission needs night; loadout does not support it)
    """
    return all(
        loadout_usability.get(cond, False)
        for cond, required in required_usability.items()
        if required
    )

def _compute_score(
    combat_score: float,
    aircraft_cost_M: float,
    loadout_cost_k: float,
    directive: str,
) -> float:
    """Return a weighted score combining combat effectiveness and cost.

    Aircraft cost is stored in M$; loadout cost in k$.  Both are converted to
    k$ before combining so the units are consistent.

    Formula::

        score = combat * ws  +  combat * wc * (_REFERENCE_COST_K / total_cost_k)

    which simplifies to::

        score = combat * (ws  +  wc * _REFERENCE_COST_K / max(1, total_cost_k))
    """
    ws, wc = _DIRECTIVE_WEIGHTS[directive]
    total_cost_k = aircraft_cost_M * 1_000.0 + loadout_cost_k
    cost_factor = _REFERENCE_COST_K / max(1.0, total_cost_k)
    return combat_score * (ws + wc * cost_factor)

def _reduce_target_data(target_data: Dict, reduction_ratio: float) -> Dict:
    """Return a deep copy of *target_data* with quantities scaled by *reduction_ratio*,
    preserving priority weights (higher-priority targets retain more quantity).

    Uses linear interpolation between *reduction_ratio* (low-priority targets,
    maximum cut) and 1.0 (high-priority targets, no cut):

        multiplier = reduction_ratio + weight * (1.0 - reduction_ratio)
        weight     = priority / total_priority_weight  ∈ [0, 1]

    Edge cases:
      - reduction_ratio ≤ 0  → all quantities zeroed (no missions possible).
      - reduction_ratio ≥ 1  → deep copy returned unchanged.
    """
    updated = copy.deepcopy(target_data)

    if reduction_ratio <= 0.0:
        for _, category_data in updated.items():
            for _, dim_data in category_data.items():
                dim_data['quantity'] = 0
        return updated

    if reduction_ratio >= 1.0:
        return updated

    total_priority_weight = sum(
        dim_data['priority']
        for _, category_data in updated.items()
        for _, dim_data in category_data.items()
    )
    for _, category_data in updated.items():
        for _, dim_data in category_data.items():
            weight = dim_data['priority'] / max(1, total_priority_weight)
            multiplier = reduction_ratio + weight * (1.0 - reduction_ratio)
            dim_data['quantity'] = max(0, round(dim_data['quantity'] * multiplier))
    return updated

def _loadout_availability(weapons_availability: Dict, aircraft_model: str, loadout_name: str):
    """"""
    pylons = get_weapons_by_loadout(aircraft_model, loadout_name)
    loadout_quantity = 0
    weapons_quantity_loadout = {}

    # conta il numero di armi di una stessa tipologia montate sui piloni dell'aereo
    for pylon, weapon in pylons:
        weapon_name_load = weapon[0]
        weapons_quantity_loadout[weapon_name_load] += weapon[1]

    # verifica se la quantità di armi disponibili per uno specifica tipo è superiore alla quantità prevista nel loadout
    for wl_name, wl_qty in weapons_quantity_loadout:
        w_qty_available = weapons_availability.get(wl_name, None) 

        if not w_qty_available:
            logger.warning(f"weapon: {wl_name} is not present in the available quantity dictionary. Continute with the next weapon")
            continue

        if w_qty_available < wl_qty:
            logger.warning(f"The required amount of {wl_name} is not avalaible ({wl_qty}: requested, {w_qty_available}: available). The loadout: {loadout_name} is not available")
            return loadout_quantity
        
        else:
            loadout_quantity = min(loadout_quantity, w_qty_available // wl_qty)
                
    return loadout_quantity


def _reduction_weapons_availability(weapons_availability: Dict, weapons_list: Dict):
        """
        weapon_list = { <weapon_name>: quantity }
        """

        for weapon_name, quantity in weapons_list:

            if weapons_availability.get(weapon_name, None):

                if weapons_availability[weapon_name] >= quantity:
                    weapons_availability[weapon_name] -= quantity

                else:
                    logger.warning(f"The weapon: {weapon_name} quantity in weapons_availabilitY dictionary is less than the requested reduction. The requested update is not performed. Returns None")    
                    return False
            
            else:
                logger.warning(f"The weapon: {weapon_name} is not present in weapons_availabilitY dictionary. Continue with the next weapon")
        return True

def _increase_weapons_availability(weapons_availability: Dict, weapons_list: Dict):
        """
        weapon_list = { <weapon_name>: quantity }
        """

        for weapon_name, quantity in weapons_list:

            if weapons_availability.get(weapon_name, None):                
                weapons_availability[weapon_name] += quantity
            
            else:
                logger.warning(f"The weapon: {weapon_name} is not present in weapons_availabilitY dictionary. Continue with the next weapon")
        return True


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_loadouts_availability(weapons_availability: Dict, loadouts_list: Dict):
    """

    weapons_availability = {

        <weapon_type>: {<weapon_name>:  quantity}

    }    
    <weapon_type> : MISSILES_AAM, MISSILES_ASM, ....

    
    loadout_list = {
        
        <aircraft_model>: {<loadout_name>: quantity(float)}
    
    }
    
    Aggiorna i due dizionari passati come argomenti (riferimenti) aggiornando le quantità richieste in loadout_list con quelle effettivamente disponibili e aggiornando weapons_availability riducendo le wapons delle quantità richieste nei loadouts
    """
    
    for aircraft_model, loadout in loadouts_list:
        
        for loadout_name, loadout_quantity in loadout:            
            quantity = _loadout_availability(weapons_availability, aircraft_model, loadout_name)

            if quantity >= loadout_quantity:                    
                weapons_list = get_weapons_by_loadout(aircraft_model, loadout_name)
                
                for i in range(0, loadout_quantity):
                    reduction_results = _reduction_weapons_availability(weapons_availability, weapons_list)
            
                    if not reduction_results:
                        logger.error(f"loadout_availability was verified but not update weapons_availability was performed!! Raise Exception")
                        raise Exception(f"loadout_availability was verified but not update weapons_availability was performed!!")
                logger.info(f"The loadout: {loadout_name} quantity requested {loadout_quantity} has been assigned. weapons_list was udated")

            else:
                logger.warning(f"The loadout: {loadout_name} quantity requested is lesser of loadout available {quantity}")
                loadout_quantity_reduction = False

                for i in range(loadout_quantity-1, 0, -1):
                    
                    if quantity >= i:
                        loadout_quantity_reduction = True
                        logger.warning(f"The loadout: {loadout_name} quantity assigned has been reduced (requested: {loadout_quantity}, assigned: {i}")
                        loadout[loadout_name] = i

                        for i in range(0, i):
                            reduction_results = _reduction_weapons_availability(weapons_availability, weapons_list)
                    
                            if not reduction_results:
                                logger.error(f"loadout_availability was verified but not update weapons_availability was performed!! Raise Exception")
                                raise Exception(f"loadout_availability was verified but not update weapons_availability was performed!!")
                        break
                    
                if not loadout_quantity_reduction:
                    loadout[loadout_name] = 0
                    logger.warning(f"The loadout: {loadout_name} quantity assigned is 0") 

                                   


def get_aircraft_mission(
    task: str,
    aircraft_availability: List[Dict],
    mission_requirements: Dict,
    target_data: Dict,
    max_aircraft_for_mission: int,
    max_missions: int,
    directive: str,
) -> Dict:
    """Select and rank available aircraft/loadout combinations for a mission.

    Parameters
    ----------
    task:
        Air task string, one of ``AIR_TASK``.
    aircraft_availability:
        List of ``{'model': str, 'loadout': str, 'quantity': int}``.
    mission_requirements:
        Dict with ``'cruise'``, ``'attack'`` performance sub-dicts and a
        ``'usability'`` dict ``{'day': bool, 'night': bool, 'adverse_weather': bool}``
        where ``True`` marks a condition the mission demands.
    target_data:
        ``{type: {dim: {'quantity': int, 'priority': int}}}``
    max_aircraft_for_mission:
        Maximum number of aircraft per single mission sortie.
    max_missions:
        Maximum number of missions (sorties) allowed.
    directive:
        Optimisation directive – one of ``_DIRECTIVE_WEIGHTS`` keys.

    Returns
    -------
    Dict with keys ``'fully_compliant'`` and ``'derated'``, each a list of
    ``{'aircraft_model': str, 'loadout': str, 'score': float}`` dicts sorted
    descending by score.

    Format example
    --------------
    task = 'Strike'

    aircraft_availability = [
        {'model': 'F-4E Phantom II',       'loadout': 'Strike',             'quantity': 10},
        {'model': 'F-15E Strike Eagle',    'loadout': 'Iron Bomb Strike',   'quantity': 15},
        {'model': 'A-10A Thunderbolt II',  'loadout': 'Precision Strike',   'quantity': 5},
        {'model': 'B-52H Stratofortress',  'loadout': 'Heavy Strike Mk-84', 'quantity': 3},
        {'model': 'F-16C Block 52d',       'loadout': 'Strike',             'quantity': 20},
    ]

    mission_requirements = {
        'cruise': {
            'speed': 850, 'reference_altitude': 7000,
            'altitude_max': 12000, 'altitude_min': 300,
            'range': 1000,
        },
        'attack': {
            'speed': 950, 'reference_altitude': 3000,
            'altitude_max': 8000, 'altitude_min': 300,
            'range': 500,
        },
        'usability': {'day': True, 'night': False, 'adverse_weather': False},
    }

    target_data = {
        'Soft':     {'big': {'quantity': 3, 'priority': 5},
                     'med': {'quantity': 5, 'priority': 6},
                     'small': {'quantity': 10, 'priority': 6}},
        'Armored':  {'big': {'quantity': 2, 'priority': 3},
                     'med': {'quantity': 4, 'priority': 3},
                     'small': {'quantity': 5, 'priority': 5}},
        'Structure':{'big': {'quantity': 3, 'priority': 10},
                     'med': {'quantity': 6, 'priority': 7},
                     'small': {'quantity': 12, 'priority': 7}},
    }

    max_aircraft_for_mission = 9
    max_missions = 2  # if >1 missions are queued; availability must be re-checked
    directive = 'balanced'
    """

    # ------------------------------------------------------------------
    # Input validation
    # ------------------------------------------------------------------
    if directive not in _DIRECTIVE_WEIGHTS:
        logger.error(f"directive ({directive!r}) unknown. Permitted values: {list(_DIRECTIVE_WEIGHTS)}")
        raise ValueError(f"directive ({directive!r}) unknown. Permitted values: {list(_DIRECTIVE_WEIGHTS)}")

    if not task or not isinstance(task, str):
        raise TypeError("task must be a non-empty string")

    if task not in AIR_TASK:
        raise ValueError(f"task must be one of {AIR_TASK!r}, got {task!r}")

    # ------------------------------------------------------------------
    # Pre-compute target info that does not change across aircraft
    # ------------------------------------------------------------------
    target_types, target_dims = _extract_target_lists(target_data)
    base_quantities = _extract_quantities(target_data)          # {type: {dim: int}}
    required_usability: Dict = mission_requirements.get('usability', {'day': True, 'night': False, 'adverse_weather': False})

    # Result lists
    available_aircraft_list: Dict[str, List] = {'fully_compliant': [], 'derated': []}

    # ------------------------------------------------------------------
    # Evaluate each candidate aircraft/loadout
    # ------------------------------------------------------------------
    for aircraft in aircraft_availability:
        model   = aircraft['model']
        lo_name = aircraft['loadout']
        qty     = aircraft['quantity']

        # --- Loadout existence check -----------------------------------
        loadout = AIRCRAFT_LOADOUTS.get(model, {}).get(lo_name, {})
        if not loadout:
            logger.warning(f"Loadout {lo_name!r} for model {model!r} not found in AIRCRAFT_LOADOUTS.")
            continue

        # --- Performance check -----------------------------------------
        if not _check_mission_requirements(loadout, mission_requirements):
            logger.info(f"Aircraft {model!r} / loadout {lo_name!r}: does not meet mission performance requirements.")
            continue

        # --- Usability check -------------------------------------------
        if not _usability_met(loadout.get('usability', {}), required_usability):
            logger.info(f"Aircraft {model!r} / loadout {lo_name!r}: does not meet usability requirements {required_usability!r}.")
            continue

        # --- Effective max aircraft for this entry (never mutates outer var) ---
        # Caps formation size to what is actually available; get_aircrafts_quantity
        # will naturally compute a higher missions_needed if effective_max < max_aircraft_for_mission,
        # so no separate reduction ratio is needed for aircraft availability.
        effective_max = min(qty, max_aircraft_for_mission)

        # --- Quantity needed for the full target set -------------------
        aq = get_aircrafts_quantity(
            model=model,
            loadout=lo_name,
            target_data=base_quantities,
            year=None,
            max_aircraft_for_mission=effective_max,
        )
        calculated_missions = aq.get('missions_needed', 0)
        reduction_ratio_missions = 1.0
        effective_quantities = base_quantities

        if calculated_missions > max_missions:
            # Target set must be reduced to fit within max_missions
            reduction_ratio_missions = max_missions / max(1, calculated_missions)
            reduced_target = _reduce_target_data(target_data, reduction_ratio_missions)
            effective_quantities = _extract_quantities(reduced_target)

            # Recompute with reduced target
            aq = get_aircrafts_quantity(
                model=model,
                loadout=lo_name,
                target_data=effective_quantities,
                year=None,
                max_aircraft_for_mission=effective_max,
            )
            calculated_missions = aq.get('missions_needed', 0)

            if calculated_missions > max_missions:
                logger.error(
                    f"Aircraft {model!r} / loadout {lo_name!r}: still exceeds max_missions "
                    f"({calculated_missions} > {max_missions}) after target reduction."
                )
                # Still keep as derated candidate but flag the shortfall
                reduction_ratio_missions = max_missions / max(1, calculated_missions)

        # --- Combat score (with target context for better ranking) -----
        aircraft_data: Optional[Aircraft_Data] = Aircraft_Data._registry.get(model)
        if aircraft_data is None:
            logger.warning(f"Aircraft {model!r} not found in Aircraft_Data registry. Skipping.")
            continue

        combat_score_value = aircraft_data.combat_score_target_effectiveness(
            task, lo_name, target_types, target_dims
        )
        aircraft_cost_M  = aircraft_data.cost               # int, M$
        lo_cost_k        = loadout_cost(model, lo_name)     # float, k$

        score_value = _compute_score(combat_score_value, aircraft_cost_M, lo_cost_k, directive)

        # --- Assign to correct list ------------------------------------
        # fully_compliant: target integrally covered within max_missions
        # derated:         target partially covered (mission count constraint triggered reduction)
        entry = {
            'aircraft_model':      model,
            'loadout':             lo_name,
            'score':               score_value,
            'aircraft_per_mission': aq.get('max_aircraft_for_mission', 0),
            'missions_needed':     calculated_missions,
            'derating_factor':     1.0 - reduction_ratio_missions
        }

        if reduction_ratio_missions == 1.0:
            available_aircraft_list['fully_compliant'].append(entry)
        else:
            derated_entry = dict(entry)
            derated_entry['score'] = score_value * reduction_ratio_missions
            available_aircraft_list['derated'].append(derated_entry)

    # ------------------------------------------------------------------
    # Sort both lists descending by score
    # ------------------------------------------------------------------
    available_aircraft_list['fully_compliant'].sort(key=lambda x: x['score'], reverse=True)
    available_aircraft_list['derated'].sort(key=lambda x: x['score'], reverse=True)

    return available_aircraft_list



    