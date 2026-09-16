"""
MODULE Doctrine

Configurazione/dottrina condivisa per il calcolo delle priorità militari (v.
Logic/Tactical_Evaluation.py, Context/Region.py). Separato da Context.py (già molto esteso) e da
Region.py: questi valori sono parametri di bilanciamento, non stato di una specifica istanza
Region né logica di calcolo -- una Region li custodisce e li passa alle funzioni tattiche, non li
usa direttamente.
"""
from typing import Dict


# Pesi di default per la selezione del bersaglio nel calcolo delle priorità militari:
# weight_priority_target[block_category][task][target_category] -> peso [0,1].
# Usato da Logic.Tactical_Evaluation.select_weight.
DEFAULT_WEIGHT_PRIORITY_TARGET = {
    "Ground_Base": {
        "attack": {"Ground_Base": 0.7, "Naval_Base": 0.0, "Air_Base": 0.1, "Logistic": 0.2, "Civilian": 0.0},
        "defense": {"Ground_Base": 0.1, "Naval_Base": 0.1, "Air_Base": 0.1, "Logistic": 0.4, "Civilian": 0.3}
    },
    "Air_Base": {
        "attack": {"Ground_Base": 0.3, "Naval_Base": 0.2, "Air_Base": 0.2, "Logistic": 0.3, "Civilian": 0.0},
        "defense": {"Ground_Base": 0.3, "Naval_Base": 0.1, "Air_Base": 0.2, "Logistic": 0.3, "Civilian": 0.0}
    },
    "Naval_Base": {
        "attack": {"Ground_Base": 0.0, "Naval_Base": 0.5, "Air_Base": 0.2, "Logistic": 0.3, "Civilian": 0.0},
        "defense": {"Ground_Base": 0.1, "Naval_Base": 0.6, "Air_Base": 0.1, "Logistic": 0.2, "Civilian": 0.0}
    }
}


def validate_weight_priority_target(value: Dict) -> None:
    """Validate weight priority target structure."""
    if not isinstance(value, dict):
        raise TypeError("Weight priority target must be a dictionary")

    # Add more specific validation based on expected structure
    for category, weights in value.items():
        if not isinstance(weights, dict):
            raise TypeError(f"Weights for {category} must be a dictionary")

        if 'attack' not in weights or 'defense' not in weights:
            raise ValueError(f"Category {category} must have 'attack' and 'defense' keys")

        # Ulteriore validazione dei sottodizionari attack/defense
        for action_type in ['attack', 'defense']:
            if not isinstance(weights[action_type], dict):
                raise TypeError(f"'{action_type}' weights for {category} must be a dictionary with values")

            if not weights[action_type]:
                raise ValueError(f"'{action_type}' weights for {category} cannot be empty")

            for target_cat, weight_val in weights[action_type].items():
                if not isinstance(target_cat, str):
                    raise TypeError(f"Target category '{target_cat}' in {action_type} for {category} must be a string.")
                if not isinstance(weight_val, (int, float)) or not (0 <= weight_val <= 1):
                    raise ValueError(f"Weight value '{weight_val}' for target")
