"""
MODULE Doctrine

Configurazione/dottrina condivisa per il calcolo delle priorità militari (v.
Logic/Tactical_Evaluation.py, Context/Region.py). Separato da Context.py (già molto esteso) e da
Region.py: questi valori sono parametri di bilanciamento, non stato di una specifica istanza
Region né logica di calcolo -- una Region li custodisce e li passa alle funzioni tattiche, non li
usa direttamente.
"""
from typing import Dict, Optional


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


# ── SOGLIE DI DISINGAGGIO (motore di sessioni virtuali, Fase 4) ───────────────
#
# DECISIONE (2026-09-23, wiki decisions/soglie-disingaggio-e-attrito-aggregato P1 e
# decisions/risolutore-ingaggio-salva-fase4 R2). Un ingaggio non deve risolversi sempre
# fino all'annientamento di una delle due parti: una forza rompe il contatto quando le
# perdite superano una soglia. La soglia e' DOTTRINA DI LATO — non una costante del
# risolutore (Logic/Engagement_Resolver.py), non un parametro di sessione, non una
# proprieta' del singolo asset — ed e' valutata PER FORZA INTERA: quando scatta, tutto il
# blocco impegnato si disingaggia insieme.
#
# Due soglie coesistenti, stessa grandezza, stesso denominatore:
#
#   'erosion'  frazione CUMULATA dell'organico impegnato non piu' operativo (P1): la forza
#              si logora lentamente e a un certo punto smette di combattere;
#   'shock'    frazione dell'organico impegnato persa in UN SINGOLO impulso, cioe' in una
#              sola salva risolta (R2): la forza si rompe per un colpo improvviso anche se
#              le perdite cumulate sono ancora sotto 'erosion'.
#
# Entrambe sono frazioni dell'ORGANICO IMPEGNATO all'inizio dell'ingaggio (non della forza
# superstite): con lo stesso denominatore la perdita di una salva non puo' mai superare
# la perdita cumulata, quindi le due soglie sono confrontabili e la coerenza fra loro e'
# verificabile — `shock <= erosion`, altrimenti la soglia di shock non potrebbe mai
# scattare per prima e sarebbe un parametro morto (v. validate_disengagement_thresholds).
# "Perso" significa "non piu' operativo" (State.isOperative falso, salute <= 50): e' la
# stessa nozione di "fuori combattimento" usata da Military.combat_power, che somma solo
# gli asset operativi.
#
# VALORI: STIMA DI PARTENZA DICHIARATA, NON DATI VALIDATI. Da ricalibrare con il processo
# ATCAL interno (risolutore fine fatto girare offline), mai con numeri da fonti non
# validate (in particolare nessun coefficiente dei documenti Lanchester ingeriti).
#   erosion 0.30 — regola empirica diffusa nella letteratura militare per cui un'unita'
#                  scesa sotto ~70% dell'organico non e' piu' pienamente efficace in
#                  combattimento. E' un ordine di grandezza, non una misura.
#   shock   0.20 — nessuna fonte: scelta solo per essere strettamente minore di
#                  'erosion' (altrimenti non scatterebbe mai per prima) e abbastanza alta
#                  da non rompere una forza per la perdita di un singolo mezzo in un
#                  gruppo piccolo (1 su 6 = 0.17 non basta).
# I due lati hanno di default GLI STESSI valori: l'asimmetria dottrinale, se voluta, va
# dichiarata esplicitamente dal chiamante (v. [[c2-hierarchy-design]], dottrina per lato),
# mai introdotta di nascosto da un default — R2 chiede proprio che la soglia si applichi
# allo stesso modo a entrambi i lati.
DISENGAGEMENT_EROSION = 'erosion'
DISENGAGEMENT_SHOCK = 'shock'
DISENGAGEMENT_KEYS = (DISENGAGEMENT_EROSION, DISENGAGEMENT_SHOCK)

DEFAULT_DISENGAGEMENT_THRESHOLDS = {
    "Blue":    {DISENGAGEMENT_EROSION: 0.30, DISENGAGEMENT_SHOCK: 0.20},
    "Red":     {DISENGAGEMENT_EROSION: 0.30, DISENGAGEMENT_SHOCK: 0.20},
    "Neutral": {DISENGAGEMENT_EROSION: 0.30, DISENGAGEMENT_SHOCK: 0.20},
}


def validate_disengagement_thresholds(value: Dict) -> None:
    """Valida la struttura {side: {'erosion': float, 'shock': float}}.

    Vincoli: ogni soglia e' un numero in (0, 1] — 0 significherebbe disingaggiarsi senza
    perdite, 1 equivale a "combattere fino all'annientamento" ed e' ammesso come scelta
    dottrinale esplicita; `shock <= erosion`, perche' con lo stesso denominatore la
    perdita di una singola salva non supera mai la perdita cumulata (v. commento sopra).

    Raises:
        TypeError: struttura non a dizionario, lato non stringa, valore non numerico.
        ValueError: chiave mancante o sconosciuta, valore fuori (0, 1], shock > erosion.
    """
    if not isinstance(value, dict):
        raise TypeError("Disengagement thresholds must be a dictionary")

    for side, thresholds in value.items():
        if not isinstance(side, str):
            raise TypeError(f"Side key {side!r} must be a string")

        if not isinstance(thresholds, dict):
            raise TypeError(f"Thresholds for side {side!r} must be a dictionary")

        missing = [key for key in DISENGAGEMENT_KEYS if key not in thresholds]
        unknown = [key for key in thresholds if key not in DISENGAGEMENT_KEYS]

        if missing:
            raise ValueError(f"Thresholds for side {side!r} miss keys {missing}")

        if unknown:
            raise ValueError(f"Thresholds for side {side!r} have unknown keys {unknown}")

        for key in DISENGAGEMENT_KEYS:
            threshold = thresholds[key]

            if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
                raise TypeError(f"Threshold {key!r} for side {side!r} must be a number, got {threshold!r}")

            if not 0.0 < threshold <= 1.0:
                raise ValueError(f"Threshold {key!r} for side {side!r} must be in (0, 1], got {threshold!r}")

        if thresholds[DISENGAGEMENT_SHOCK] > thresholds[DISENGAGEMENT_EROSION]:
            raise ValueError(f"Side {side!r}: shock threshold ({thresholds[DISENGAGEMENT_SHOCK]}) must not "
                             f"exceed erosion threshold ({thresholds[DISENGAGEMENT_EROSION]}), "
                             f"otherwise it could never trigger first")


def get_disengagement_thresholds(side: Optional[str],
                                 thresholds: Optional[Dict] = None) -> Optional[Dict[str, float]]:
    """Soglie di disingaggio del lato `side`, o None se il lato non ne dichiara.

    Args:
        side: 'Blue', 'Red', 'Neutral' (o qualunque lato presente in `thresholds`).
        thresholds: tabella dottrinale da usare al posto di DEFAULT_DISENGAGEMENT_THRESHOLDS
                    (es. quella custodita da un C2 di lato); viene validata.

    Returns:
        Una COPIA di {'erosion': float, 'shock': float} — il chiamante puo' modificarla
        senza alterare la dottrina — oppure None se il lato e' sconosciuto. None e' un dato
        mancante, non un errore: e' il consumatore (Engagement_Resolver) a decidere la
        propria politica e a registrarla.
    """
    table = DEFAULT_DISENGAGEMENT_THRESHOLDS if thresholds is None else thresholds
    validate_disengagement_thresholds(table)

    entry = table.get(side) if isinstance(side, str) else None

    return dict(entry) if entry is not None else None
