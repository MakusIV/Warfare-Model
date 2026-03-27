"""
 MODULE Air Resources Assigner

methods for allocating air military resources: aircraft and loadouts.

"""

from __future__ import annotations  # must be the very first statement

import copy
from typing import Dict, List, Optional, Tuple

import random
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np
from Code.Dynamic_War_Manager.Source.Asset import Aircraft
from Code.Dynamic_War_Manager.Source.Block import Military

from Code.Dynamic_War_Manager.Source.Context.Context import (
    AIR_TASK, AIR_TO_AIR_TASK, AIR_TO_GROUND_TASK,
    Air_To_Air_Task, Air_To_Ground_Task,
    TARGET_CLASSIFICATION,
    Target_Class_Name,
    Weapon_Power_Effect,
    Weapon_Area_Effect,
    get_block_infrastructure_components,
    get_task_from_target
)
from Code.Dynamic_War_Manager.Source.Context.Campaign_State import Campaign_State
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Loadouts import (
    AIRCRAFT_LOADOUTS,
    get_aircrafts_quantity,
    loadout_cost,
    get_loadout,
    get_aircraft_loadouts_by_task,
    get_weapons_by_loadout,
    
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
            # multiplier = reduction_ratio * weight
            dim_data['quantity'] = max(0, round(dim_data['quantity'] * multiplier))
    return updated

def _find_weapon_in_availability(weapons_availability: Dict, weapon_name: str) -> Tuple[Optional[str], int]:
    """Cerca *weapon_name* nella struttura annidata *weapons_availability*.

    La struttura attesa è::

        weapons_availability = {
            <weapon_type>: {<weapon_name>: <quantity (int)>},
            ...
        }

    Returns
    -------
    (type_key, quantity)
        *type_key* è la chiave del tipo in cui è stata trovata l'arma;
        *quantity* è la disponibilità corrente.
        Se l'arma non è trovata restituisce ``(None, 0)``.
    """
    for wtype, weapons_dict in weapons_availability.items():
        if weapon_name in weapons_dict:
            return wtype, weapons_dict[weapon_name]
    return None, 0

def _pylons_to_weapons_dict(pylons: Dict) -> Dict[str, int]:
    """Converte la struttura pylons in un dizionario piatto armi→quantità totale.

    Formato pylons::

        {<pylon_id>: [<weapon_name>, <quantity>, ...], ...}

    Returns
    -------
    Dict[str, int]
        ``{weapon_name: total_quantity}`` — somma delle quantità per ogni arma
        presente su più piloni dello stesso tipo.

    Raises
    ------
    TypeError
        Se *pylons* non è un dict.
    """
    if not isinstance(pylons, dict):
        raise TypeError(f"pylons deve essere un dict, ricevuto {type(pylons).__name__!r}")

    weapons: Dict[str, int] = {}
    for pylon_id, weapon_data in pylons.items():
        if not isinstance(weapon_data, (list, tuple)) or len(weapon_data) < 2:
            logger.warning(f"Pylon {pylon_id!r}: formato non valido ({weapon_data!r}), ignorato.")
            continue
        name = weapon_data[0]
        qty  = weapon_data[1]
        if not isinstance(name, str) or not isinstance(qty, (int, float)):
            logger.warning(f"Pylon {pylon_id!r}: nome o quantità non validi ({name!r}, {qty!r}), ignorato.")
            continue
        weapons[name] = weapons.get(name, 0) + int(qty)
    return weapons

def _loadout_availability(weapons_availability: Dict, aircraft_model: str, loadout_name: str) -> int:
    """Restituisce quanti loadout completi possono essere allestiti con le armi disponibili.

    Per ogni arma richiesta dal loadout (sommando le quantità tra i piloni dello
    stesso tipo), calcola quante unità di loadout completo è possibile formare
    con la scorta attuale.  Restituisce il minimo tra tutte le armi (fattore
    limitante).

    Parameters
    ----------
    weapons_availability:
        ``{weapon_type: {weapon_name: quantity}}``
        (``weapon_type``: MISSILES_AAM, MISSILES_ASM, ecc.)
    aircraft_model:
        Nome del modello aereo (deve esistere in ``AIRCRAFT_LOADOUTS``).
    loadout_name:
        Nome del loadout (deve esistere per l'aereo indicato).

    Returns
    -------
    int
        Numero di loadout completi allestibili (≥ 0).

    Raises
    ------
    TypeError
        Se i parametri non rispettano il tipo atteso.
    """
    if not isinstance(weapons_availability, dict):
        raise TypeError(f"weapons_availability deve essere un dict, ricevuto {type(weapons_availability).__name__!r}")
    if not isinstance(aircraft_model, str) or not aircraft_model:
        raise TypeError("aircraft_model deve essere una stringa non vuota")
    if not isinstance(loadout_name, str) or not loadout_name:
        raise TypeError("loadout_name deve essere una stringa non vuota")

    pylons = get_weapons_by_loadout(aircraft_model, loadout_name)

    # Aggrega armi per nome: {weapon_name: qty_per_loadout}
    weapons_per_loadout = _pylons_to_weapons_dict(pylons)

    if not weapons_per_loadout:
        logger.warning(f"Nessuna arma trovata per il loadout {loadout_name!r} / {aircraft_model!r}.")
        return 0

    # Calcola il numero di loadout possibile per ciascuna arma (fattore limitante)
    loadout_quantity: Optional[int] = None

    for weapon_name, qty_needed in weapons_per_loadout.items():
        wtype, w_qty_available = _find_weapon_in_availability(weapons_availability, weapon_name)

        if wtype is None:
            logger.warning(
                f"Arma {weapon_name!r} non trovata in weapons_availability. "
                f"Il loadout {loadout_name!r} non è disponibile."
            )
            return 0

        if w_qty_available < qty_needed:
            logger.warning(
                f"Arma {weapon_name!r}: richieste {qty_needed}, disponibili {w_qty_available}. "
                f"Il loadout {loadout_name!r} non è disponibile."
            )
            return 0

        possible = w_qty_available // qty_needed
        loadout_quantity = possible if loadout_quantity is None else min(loadout_quantity, possible)

    return loadout_quantity if loadout_quantity is not None else 0

def _reduction_weapons_availability(weapons_availability: Dict, weapons_list: Dict) -> bool:
    """Riduce la disponibilità delle armi scalando le quantità indicate in *weapons_list*.

    Modifica *weapons_availability* in-place.

    Parameters
    ----------
    weapons_availability:
        ``{weapon_type: {weapon_name: quantity}}``
    weapons_list:
        ``{weapon_name: quantity}`` — quantità da sottrarre per ogni arma.

    Returns
    -------
    bool
        ``True`` se l'aggiornamento è avvenuto correttamente per tutte le armi,
        ``False`` se una o più armi non hanno scorte sufficienti
        (in tal caso nessuna modifica viene applicata).

    Raises
    ------
    TypeError
        Se i parametri non rispettano il tipo atteso.
    ValueError
        Se una quantità richiesta è negativa.
    """
    if not isinstance(weapons_availability, dict):
        raise TypeError(f"weapons_availability deve essere un dict, ricevuto {type(weapons_availability).__name__!r}")
    if not isinstance(weapons_list, dict):
        raise TypeError(f"weapons_list deve essere un dict {{weapon_name: quantity}}, ricevuto {type(weapons_list).__name__!r}")

    # Validazione preventiva: verifica disponibilità prima di applicare riduzioni
    for weapon_name, quantity in weapons_list.items():
        if not isinstance(quantity, (int, float)) or quantity < 0:
            raise ValueError(f"Quantità non valida per {weapon_name!r}: {quantity!r} (deve essere ≥ 0)")

        wtype, available = _find_weapon_in_availability(weapons_availability, weapon_name)

        if wtype is None:
            logger.warning(f"Arma {weapon_name!r} non trovata in weapons_availability. Riduzione ignorata.")
            continue

        if available < quantity:
            logger.warning(
                f"Arma {weapon_name!r}: riduzione richiesta {quantity} > disponibile {available}. "
                f"Operazione annullata."
            )
            return False

    # Applicazione delle riduzioni (solo se la validazione è passata)
    for weapon_name, quantity in weapons_list.items():
        wtype, _ = _find_weapon_in_availability(weapons_availability, weapon_name)
        if wtype is not None:
            weapons_availability[wtype][weapon_name] -= int(quantity)

    return True

def _increase_weapons_availability(weapons_availability: Dict, weapons_list: Dict) -> bool:
    """Incrementa la disponibilità delle armi aggiungendo le quantità indicate in *weapons_list*.

    Modifica *weapons_availability* in-place.

    Parameters
    ----------
    weapons_availability:
        ``{weapon_type: {weapon_name: quantity}}``
    weapons_list:
        ``{weapon_name: quantity}`` — quantità da aggiungere per ogni arma.

    Returns
    -------
    bool
        ``True`` sempre (l'aggiunta non può fallire per carenza di scorte);
        le armi non presenti nel dizionario vengono saltate con un warning.

    Raises
    ------
    TypeError
        Se i parametri non rispettano il tipo atteso.
    ValueError
        Se una quantità è negativa.
    """
    if not isinstance(weapons_availability, dict):
        raise TypeError(f"weapons_availability deve essere un dict, ricevuto {type(weapons_availability).__name__!r}")
    if not isinstance(weapons_list, dict):
        raise TypeError(f"weapons_list deve essere un dict {{weapon_name: quantity}}, ricevuto {type(weapons_list).__name__!r}")

    for weapon_name, quantity in weapons_list.items():
        if not isinstance(quantity, (int, float)) or quantity < 0:
            raise ValueError(f"Quantità non valida per {weapon_name!r}: {quantity!r} (deve essere ≥ 0)")

        wtype, _ = _find_weapon_in_availability(weapons_availability, weapon_name)

        if wtype is None:
            logger.warning(f"Arma {weapon_name!r} non trovata in weapons_availability. Incremento ignorato.")
            continue

        weapons_availability[wtype][weapon_name] += int(quantity)

    return True

def _count_target_dimension(target_dimension_list: Dict) -> Dict:    
    return  sum(dim_values["quantity"] for dim_name, dim_values in target_dimension_list.items())

def _create_ground_mission_task_table(target_data: Dict) -> Dict:
    """Create a ground mission task table from target_data.

    Parameters
    ----------
    target_data:
        ``{type: {dim: {'quantity': int, 'priority': int}}}``

    Returns
    -------
    Dict
        ``{target_type: {'task': str, 'priority': int}}``

        *task* è il valore stringa di ``Air_To_Ground_Task`` o ``Air_To_Air_Task``
        corrispondente alla dimensione con priorità più alta per quel tipo di target.

    Format example
    --------------

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
        'Aircraft' :{'big': {'quantity': 0, 'priority': 10},
                    'med': {'quantity': 6, 'priority': 7},
                    'small': {'quantity': 12, 'priority': 7}},
    }

    task_table = {
        'Soft':      {'task': 'Strike',          'priority': 6},
        'Armored':   {'task': 'Strike',          'priority': 5},
        'Structure': {'task': 'Strike',          'priority': 10},
        'Aircraft':  {'task': 'Escort',          'priority': 10},
    }

    Raises
    ------
    TypeError
        Se *target_data* non è un dict.
    """
    if not isinstance(target_data, dict):
        raise TypeError(f"target_data deve essere un dict, ricevuto {type(target_data).__name__!r}")

    admitted_target_types = {item.value for item in Target_Class_Name}
    _task_table = {}
    
    for tg_type, tg_dims in target_data.items():

        if not isinstance(tg_dims, dict):
            logger.warning(f"Dimensioni non valide per il tipo target {tg_type!r} (atteso dict). Ignorato.")
            continue

        if tg_type not in admitted_target_types:
            logger.warning(
                f"Tipo target sconosciuto: {tg_type!r}. "
                f"Verrà trattato come {Target_Class_Name.GENERIC.value!r}."
            )
            target_type = Target_Class_Name.GENERIC.value
        else:
            target_type = tg_type

        _task_table[target_type] = {}
        _task = None
        _max_priority = 0

        for target_dim, dim_item in tg_dims.items():

            if not isinstance(dim_item, dict):
                logger.warning(f"Dati dimensione {target_dim!r} non validi per {target_type!r}. Ignorato.")
                continue

            if dim_item.get('priority', 0) > _max_priority:

                if target_type == Target_Class_Name.AIRCRAFT.value:
                    # Escort: la valutazione di una Fighter_Sweep richiede anche la stima dei nemici
                    _task = Air_To_Air_Task.ESCORT.value

                elif target_type == Target_Class_Name.SHIP.value:
                    _task = Air_To_Ground_Task.ANTI_SHIP.value

                elif target_type == Target_Class_Name.AIR_DEFENSE.value:
                    _task = Air_To_Ground_Task.SEAD.value

                else:
                    _task = get_task_from_target(target_type, target_dim, dim_item.get('quantity', 0))

                _max_priority = dim_item['priority']

        _task_table[target_type]['task'] = _task
        _task_table[target_type]['priority'] = _max_priority

    return _task_table




# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

# NOTE
# get_ground_mission_task_list() determina i task in funzione del target. La task_list include anche l'eventuale scorta se nel target_type sono incluse le info relative al target_type = 'Aircraft'
# Non ho implementato la funzione corrispondente per target aerei in quanto non è possibile determinare un air_task (Intercept, Fighter:Sweep, ..) in funzione del target_type = 'Aircraft'-
# Per le task_list relative a missioni air_to_air è utilizzabile direttamente la funzione get_aircraft_mission() specificando il task: Intercept, Fighter_Sweep, ecc


# utilizzabile avendo già definito la lista delle armi disponibili, degli aerei e dei loadout da considerare
def get_loadouts_availability(weapons_availability: Dict, loadouts_list: Dict) -> Dict:
    """Verifica e assegna i loadout in base alla disponibilità corrente delle armi.

    Per ogni loadout richiesto calcola quante unità possono essere effettivamente
    allestite con la scorta disponibile, deduce le armi consumate da
    *weapons_availability* e restituisce la lista assegnata con le eventuali
    riduzioni percentuali rispetto alla richiesta.

    Parameters
    ----------
    weapons_availability:
        ``{weapon_type: {weapon_name: quantity}}``
        Struttura mutata in-place: le armi assegnate vengono scalate.
    loadouts_list:
        ``{aircraft_model: {loadout_name: requested_quantity}}``

    Returns
    -------
    Dict
        ``{aircraft_model: {loadout_name: {'quantity': int, 'reduction_percentage': int}}}``

        *reduction_percentage* = 100 se la richiesta è stata soddisfatta per
        intero, un valore minore altrimenti (0 se nessuna unità è disponibile).

    Raises
    ------
    TypeError
        Se i parametri non rispettano il tipo atteso.
    Exception
        Se si verifica un'inconsistenza tra la disponibilità calcolata da
        ``_loadout_availability`` e la successiva deduzione.
    """
    if not isinstance(weapons_availability, dict):
        raise TypeError(f"weapons_availability deve essere un dict, ricevuto {type(weapons_availability).__name__!r}")
    if not isinstance(loadouts_list, dict):
        raise TypeError(f"loadouts_list deve essere un dict {{aircraft_model: {{loadout_name: qty}}}}, ricevuto {type(loadouts_list).__name__!r}")

    loadout_list_assigned: Dict = {}

    for aircraft_model, loadouts in loadouts_list.items():

        if not isinstance(loadouts, dict):
            logger.warning(f"Formato non valido per i loadout di {aircraft_model!r} (atteso dict). Ignorato.")
            continue

        # Inizializza la voce per questo modello una sola volta, fuori dal loop interno
        loadout_list_assigned[aircraft_model] = {}

        for loadout_name, requested_qty in loadouts.items():

            if not isinstance(requested_qty, int) or requested_qty < 0:
                logger.warning(
                    f"Quantità non valida per {loadout_name!r} / {aircraft_model!r} "
                    f"({requested_qty!r}). Skipping."
                )
                continue

            # ---- Calcola il massimo numero di loadout allestibili --------
            available_qty = _loadout_availability(weapons_availability, aircraft_model, loadout_name)
            assigned_qty  = min(requested_qty, available_qty)

            if assigned_qty <= 0:
                loadout_list_assigned[aircraft_model][loadout_name] = {
                    'quantity': 0,
                    'reduction_percentage': 0,
                }
                logger.warning(
                    f"Loadout {loadout_name!r} ({aircraft_model!r}): "
                    f"0 unità assegnabili su {requested_qty} richieste."
                )
                continue

            # ---- Costruisce il dizionario armi totali da detrarre --------
            # (quantità per singolo loadout × unità assegnate)
            pylons = get_weapons_by_loadout(aircraft_model, loadout_name)
            per_loadout_weapons = _pylons_to_weapons_dict(pylons)
            total_weapons_needed = {
                wname: wqty * assigned_qty
                for wname, wqty in per_loadout_weapons.items()
            }

            # ---- Deduce le armi dalla disponibilità ---------------------
            result = _reduction_weapons_availability(weapons_availability, total_weapons_needed)
            if not result:
                logger.error(
                    f"Inconsistenza: la disponibilità di {loadout_name!r} ({aircraft_model!r}) "
                    f"era verificata ma la deduzione ha fallito. Eccezione sollevata."
                )
                raise Exception(
                    f"Inconsistency: weapons deduction failed for {loadout_name!r} / {aircraft_model!r}"
                )

            percentage = int(assigned_qty * 100 / requested_qty) if requested_qty > 0 else 100
            loadout_list_assigned[aircraft_model][loadout_name] = {
                'quantity': assigned_qty,
                'reduction_percentage': percentage,
            }

            if assigned_qty == requested_qty:
                logger.info(
                    f"Loadout {loadout_name!r} ({aircraft_model!r}): "
                    f"{assigned_qty}/{requested_qty} unità assegnate (100%)."
                )
            else:
                logger.warning(
                    f"Loadout {loadout_name!r} ({aircraft_model!r}): "
                    f"{assigned_qty}/{requested_qty} unità assegnate ({percentage}%)."
                )

    return loadout_list_assigned

# utilizzabile avendo già definito la lista degli aerei e dei loadout da utilizzare
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
            # Target set must be reduced to fit within max_missions.
            # A plain ratio T = max_missions/calculated_missions is insufficient because
            # _reduce_target_data applies a priority-weighted multiplier that preserves
            # high-priority targets, making the effective total reduction < T.
            # We pre-compensate analytically: given the normalised priority-quantity
            # correlation C = Σ(q_i*p_i)/(Q_tot*P_tot), the effective fraction after
            # reduction is r*(1-C)+C, so we solve for r such that r*(1-C)+C = T:
            #   r_corrected = (T - C) / (1 - C)
            T = max_missions / max(1, calculated_missions)
            flat = [
                (d['quantity'], d['priority'])
                for cat in target_data.values()
                for d in cat.values()
            ]
            Q_tot = sum(q for q, _ in flat)
            P_tot = sum(p for _, p in flat)
            if Q_tot > 0 and P_tot > 0:
                C = sum(q * p for q, p in flat) / (Q_tot * P_tot)
            else:
                C = 0.0
            reduction_ratio_missions = (T - C) / (1.0 - C) if C < 1.0 else 0.0
            reduction_ratio_missions = max(0.0, min(1.0, reduction_ratio_missions))

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
                # Residual excess from integer rounding or efficiency heterogeneity:
                # apply one additional proportional correction step on the already-
                # reduced target (r2 ≈ 1, so priority distribution is barely altered).
                r2 = max_missions / max(1, calculated_missions)
                reduced_target = _reduce_target_data(reduced_target, r2)
                effective_quantities = _extract_quantities(reduced_target)
                aq = get_aircrafts_quantity(
                    model=model,
                    loadout=lo_name,
                    target_data=effective_quantities,
                    year=None,
                    max_aircraft_for_mission=effective_max,
                )
                calculated_missions = aq.get('missions_needed', 0)
                reduction_ratio_missions *= r2
        
        # --- Combat score (with target context for better ranking) -----
        aircraft_data: Optional[Aircraft_Data] = Aircraft_Data._registry.get(model)
        if aircraft_data is None:
            logger.warning(f"Aircraft {model!r} not found in Aircraft_Data registry. Skipping.")
            continue

        combat_score_value = aircraft_data.combat_score_target_effectiveness(
            task, lo_name, target_types, target_dims
        )
        total_aircraft_needed = max(1, aq.get('total', 1))
        aircraft_cost_M  = aircraft_data.cost * total_aircraft_needed        # int, M$
        lo_cost_k        = loadout_cost(model, lo_name) * total_aircraft_needed  # float, k$
        total_cost       = aircraft_cost_M + lo_cost_k

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
            'derating_factor':     1.0 - reduction_ratio_missions,
            'total_cost'     :     total_cost 
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

# utilizzabile avendo già definito la lista degli aerei e dei loadout da utilizzare
def get_ground_mission_task_list(aircraft_availability: List[Dict],
                                    mission_requirements: Dict,
                                    target_data: Dict,
                                    max_aircraft_for_mission: int,
                                    max_missions: int,
                                    directive: str
                                ) -> Dict:
    """Create and return a task list of available aircraft/loadout combinations from target_data.

    Parameters
    ----------
    aircraft_availability:
        Lista di disponibilità degli aeromobili.
    mission_requirements:
        Requisiti della missione (velocità, quota, raggio d'azione, usabilità).
    target_data:
        ``{type: {dim: {'quantity': int, 'priority': int}}}``
    max_aircraft_for_mission:
        Numero massimo di aeromobili per singola missione.
    max_missions:
        Numero massimo di missioni pianificabili.
    directive:
        Direttiva di bilanciamento prestazioni/costo
        (``'performance_high'``, ``'performance'``, ``'balanced'``, ``'economy'``, ``'economy_high'``).

    Returns
    -------
    Dict
        ``{target_type: {'task': str, 'priority': int, 'fully_compliant': [...], 'derated': [...]}}``

    Format example
    --------------

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

    aircraft_mission_task_list = {
        'Soft': {
            'task': 'Strike',
            'priority': 6,
            'fully_compliant': [
                {'aircraft_model': 'B-52H', 'loadout': 'Bomber Strike', 'score': 12.4,
                 'aircraft_per_mission': 2, 'missions_needed': 1, 'derating_factor': 0.0},
            ],
            'derated': [
                {'aircraft_model': 'F-16A', 'loadout': 'Viper Strike', 'score': 4.2,
                 'aircraft_per_mission': 4, 'missions_needed': 3, 'derating_factor': 18.0},
            ]
        },
        'Structure': {
            'task': 'Pinpoint_Strike',
            'priority': 10,
            'fully_compliant': [...],
            'derated': [...]
        }
    }

    Raises
    ------
    TypeError
        Se i parametri non rispettano il tipo atteso.
    ValueError
        Se *directive* non è un valore valido.
    """
    if not isinstance(aircraft_availability, list):
        raise TypeError(f"aircraft_availability deve essere una list, ricevuto {type(aircraft_availability).__name__!r}")
    if not isinstance(mission_requirements, dict):
        raise TypeError(f"mission_requirements deve essere un dict, ricevuto {type(mission_requirements).__name__!r}")
    if not isinstance(target_data, dict):
        raise TypeError(f"target_data deve essere un dict, ricevuto {type(target_data).__name__!r}")
    if not isinstance(max_aircraft_for_mission, int) or max_aircraft_for_mission < 1:
        raise TypeError("max_aircraft_for_mission deve essere un intero >= 1")
    if not isinstance(max_missions, int) or max_missions < 1:
        raise TypeError("max_missions deve essere un intero >= 1")
    if directive not in _DIRECTIVE_WEIGHTS:
        raise ValueError(f"directive non valida: {directive!r}. Valori ammessi: {list(_DIRECTIVE_WEIGHTS)}")

    task_table = _create_ground_mission_task_table(target_data)
    aircraft_mission_task_list = {}

    for target_type, task_item in task_table.items():
        task = task_item['task']

        if task is None:
            logger.warning(f"Nessun task determinato per il tipo target {target_type!r}. Ignorato.")
            continue
        aircraft_mission_task_list[target_type] = get_aircraft_mission( # aircraft mission list for specific target_type
            task, aircraft_availability, mission_requirements, {target_type: target_data[target_type]},
            max_aircraft_for_mission, max_missions, directive
        )
        aircraft_mission_task_list[target_type]['task'] = task
        aircraft_mission_task_list[target_type]['priority'] = task_item['priority']

    return aircraft_mission_task_list

# utilizzabile avendo già definito la lista degli aerei e dei loadout da utilizzare
def get_air_mission_task_list(aircraft_availability: List[Dict],
                                    task: str,
                                    mission_requirements: Dict,                                    
                                    target_data: Dict,
                                    max_aircraft_for_mission: int,
                                    max_missions: int,
                                    directive: str
                                ) -> Dict:
    """Create and return a task list of available aircraft/loadout combinations from target_data.

    Parameters
    ----------
    aircraft_availability:
        Lista di disponibilità degli aeromobili.
    task:
        air task: Intercept, Fighter_Sweep, ...
    mission_requirements:
        Requisiti della missione (velocità, quota, raggio d'azione, usabilità).
    target_data:
        ``{'Aircraft': {dim: {'quantity': int, 'priority': int}}}``
        Big -> Bomber, Transport, AWACS, Tanker
        Med -> Attacker, Fighter_Bomber
        small -> Fighter, Recon, Helicopter
        
    max_aircraft_for_mission:
        Numero massimo di aeromobili per singola missione.
    max_missions:
        Numero massimo di missioni pianificabili.
    directive:
        Direttiva di bilanciamento prestazioni/costo
        (``'performance_high'``, ``'performance'``, ``'balanced'``, ``'economy'``, ``'economy_high'``).

    Returns
    -------
    Dict
        ``{target_type: {'task': str, 'priority': int, 'fully_compliant': [...], 'derated': [...]}}``

    Format example
    --------------

    target_data = {
        'Aircraft':     {'big': {'quantity': 3, 'priority': 5},
                        'med': {'quantity': 5, 'priority': 6},
                        'small': {'quantity': 10, 'priority': 6}},        
    }

    aircraft_mission_task_list = {
        'Intercept'
            'task': 'Strike',
            'priority': 6,
            'fully_compliant': [
                {'aircraft_model': 'B-52H', 'loadout': 'Bomber Strike', 'score': 12.4,
                 'aircraft_per_mission': 2, 'missions_needed': 1, 'derating_factor': 0.0},
            ],
            'derated': [
                {'aircraft_model': 'F-16A', 'loadout': 'Viper Strike', 'score': 4.2,
                 'aircraft_per_mission': 4, 'missions_needed': 3, 'derating_factor': 18.0},
            ]
        },
    }

    Raises
    ------
    TypeError
        Se i parametri non rispettano il tipo atteso.
    ValueError
        Se *directive* non è un valore valido.
    """
    if not isinstance(aircraft_availability, list):
        raise TypeError(f"aircraft_availability deve essere una list, ricevuto {type(aircraft_availability).__name__!r}")
    if not isinstance(task, str) or task not in AIR_TO_AIR_TASK:
        raise TypeError(f"task deve essere una stringa appartenente a AIR_TO_AIR_TASK, ricevuto {type(task).__name__!r}")
    if not isinstance(mission_requirements, dict):
        raise TypeError(f"mission_requirements deve essere un dict, ricevuto {type(mission_requirements).__name__!r}")
    if not isinstance(target_data, dict) or target_data.get('Aircraft', None) == None or len(target_data) > 1:
        raise TypeError(f"target_data deve essere un dict contenente l'unica chiave 'Aircraft', ricevuto {type(target_data).__name__!r}")
    if not isinstance(max_aircraft_for_mission, int) or max_aircraft_for_mission < 1:
        raise TypeError("max_aircraft_for_mission deve essere un intero >= 1")
    if not isinstance(max_missions, int) or max_missions < 1:
        raise TypeError("max_missions deve essere un intero >= 1")
    if directive not in _DIRECTIVE_WEIGHTS:
        raise ValueError(f"directive non valida: {directive!r}. Valori ammessi: {list(_DIRECTIVE_WEIGHTS)}")

    aircraft_mission_task_list = {}

    if task in [Air_To_Air_Task.FIGHTER_SWEEP.value, Air_To_Air_Task.INTERCEPT.value, Air_To_Air_Task.CAP, Air_To_Air_Task.ESCORT]:
        aircraft_mission_task_list['Aircraft'] = get_aircraft_mission( # aircraft mission list for specific target_type
            task, aircraft_availability, mission_requirements, target_data,
            max_aircraft_for_mission, max_missions, directive
        )
    elif task in [Air_To_Air_Task.RECON]:
        get_aircraft_mission( # aircraft mission list for specific target_type
            task, aircraft_availability, mission_requirements, {'Aircraft': {'small': 1}},
            max_aircraft_for_mission, max_missions, directive
        )
    aircraft_mission_task_list['Aircraft']['task'] = task
    aircraft_mission_task_list['Aircraft']['priority'] = target_data['priority']

    return aircraft_mission_task_list

def get_aircraft_availability_list(airbase_name: str, aircraft_category: Optional[str] = None, ):

    """ 
    asset_type: Aircraft
    asset_category: Fighter

    asset_type: Weapon
    asset_category: Bombs
    

    asset_type: Aircraft
    asset_category: Fighter
    task: 'Strike'



    asset_list = [ {'asset_type': str, 'asset_category': str, 'asset_name': str, asset_quantity: int} ]

    asset_list = [  {'asset_type': 'Aircraft, 'asset_category': 'Fighter_Bomber' ,'asset_name': 'F-4E': asset_quantity: 23}, 
                    {'asset_type': 'Aircraft, 'asset_category': 'Fighter_Bomber' ,'asset_name': 'F-16A': asset_quantity: 18} ]

    asset_list = [ {'asset_type': 'AIR_WEAPON', 'asset_category': 'MISSILES_ASM' ,'asset_name': 'AGM_64D Maverick': asset_quantity: 230} ]

    

    """


    pass
    
    # airbase = get_airbase(airbase_name) # funzione implementata in Campaign_Stae dovesono definite le Region con le rispettive Military Base assegnate.

    # asset_list = airbase.get_asset_type_list(asset_type, asset_category, status = 'operative')# 'operative', 'repair', 'destroyed'
    # asset_quantity = len(asset_list)







