"""
MODULE Doctrine

Configurazione/dottrina condivisa per il calcolo delle priorità militari (v.
Logic/Tactical_Evaluation.py, Context/Region.py). Separato da Context.py (già molto esteso) e da
Region.py: questi valori sono parametri di bilanciamento, non stato di una specifica istanza
Region né logica di calcolo -- una Region li custodisce e li passa alle funzioni tattiche, non li
usa direttamente.
"""
from typing import Dict, Optional, Tuple


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
# ── SOGLIA DI ROTTURA STOCASTICA (2026-09-29) ─────────────────────────────────
#
# DECISIONE (Analysis/Document/Proposta_Soglia_Rottura_Stocastica.md, D1-D9 e D4a-D4e).
# Con soglie fisse, per le forze piccole la perdita minima 1/n faceva scattare la soglia
# alla prima perdita (S1: 5 carri si ritiravano per un carro perso in 7 repliche su 8).
# Ora 'erosion' e' la MEDIANA di una soglia di rottura B(t) propria di ogni forza:
#
#   B(t) = logistic( logit(mu_eff(t)) + dispersion * z )        z = Phi^-1(u)
#   mu_eff(t) = clamp( erosion * M(morale) * R(t) * U(t) * P,  median_bounds )
#
#   u         "tempra" della forza, estratta UNA volta per ingaggio da un flusso casuale
#             separato (D1, D8): non dipende dal numero di eventi-perdita;
#   M         morale in ingresso, 1 + morale_weight * (2m - 1), None = neutro (D3);
#   R         rapporto di forze percepito, clamp(rho^force_ratio_exponent, force_ratio_bounds),
#             rho dai nemici rilevati (v. Context/Air_Defense_Efficacy per la misura, D4);
#   U         fuoco senza risposta, 1 - unanswered_fire_weight * (perdite da tiratori non
#             rilevati / perdite) (D5);
#   P         defensive_posture_factor se la forza e' ferma per tutto l'ingaggio (D6).
#
# 'shock' resta la soglia di shock alla mediana: durante l'ingaggio vale
# (shock / erosion) * B(t), e scatta solo se la salva ha tolto almeno shock_min_losses
# asset (D7). Con 'erosion' = 1.0 la forza combatte fino all'annientamento, senza modulazione.
#
# Le chiavi oltre 'erosion'/'shock' sono FACOLTATIVE: se mancano valgono i valori NEUTRI di
# DISENGAGEMENT_NEUTRAL, e una tabella con le sole 'erosion'/'shock' si comporta esattamente
# come le soglie fisse precedenti al 2026-09-29 (modalita' deterministica: test, scenari
# "combatte fino alla fine"). La tabella di default dichiara invece tutti i parametri.
#
# VALORI: STIME DI PARTENZA DICHIARATE, NON DATI VALIDATI. Da ricalibrare con il processo
# ATCAL interno (risolutore fine fatto girare offline), mai con numeri da fonti non
# validate (in particolare nessun coefficiente dei documenti Lanchester ingeriti).
#   erosion 0.30 — regola empirica diffusa nella letteratura militare per cui un'unita'
#                  scesa sotto ~70% dell'organico non e' piu' pienamente efficace in
#                  combattimento. E' un ordine di grandezza, non una misura.
#   shock   0.20 — nessuna fonte: scelta solo per essere strettamente minore di
#                  'erosion' (altrimenti non scatterebbe mai per prima).
#   dispersion 0.5 — deviazione standard ~0.10 attorno a 0.30, 90% delle soglie fra 0.16 e
#                  0.49: le soglie di rottura storiche sono una distribuzione, non un valore.
#   morale_weight 0.3, force_ratio_exponent 0.5 con limiti (0.6, 1.5),
#   air_force_ratio_scale 2.0, unanswered_fire_weight 0.3, defensive_posture_factor 1.2,
#   shock_min_losses 2 — stime dichiarate della proposta, senza fonte.
# I due lati hanno di default GLI STESSI valori: l'asimmetria dottrinale, se voluta, va
# dichiarata esplicitamente dal chiamante (v. [[c2-hierarchy-design]], dottrina per lato),
# mai introdotta di nascosto da un default — R2 chiede proprio che la soglia si applichi
# allo stesso modo a entrambi i lati.
DISENGAGEMENT_EROSION = 'erosion'
DISENGAGEMENT_SHOCK = 'shock'
DISENGAGEMENT_KEYS = (DISENGAGEMENT_EROSION, DISENGAGEMENT_SHOCK)

BREAKPOINT_DISPERSION = 'dispersion'
MORALE_WEIGHT = 'morale_weight'
FORCE_RATIO_EXPONENT = 'force_ratio_exponent'
FORCE_RATIO_BOUNDS = 'force_ratio_bounds'
AIR_FORCE_RATIO_SCALE = 'air_force_ratio_scale'
UNANSWERED_FIRE_WEIGHT = 'unanswered_fire_weight'
DEFENSIVE_POSTURE_FACTOR = 'defensive_posture_factor'
SHOCK_MIN_LOSSES = 'shock_min_losses'
MEDIAN_BOUNDS = 'median_bounds'

# Valori NEUTRI delle chiavi facoltative: con questi la soglia e' quella fissa di prima.
DISENGAGEMENT_NEUTRAL = {
    BREAKPOINT_DISPERSION: 0.0,
    MORALE_WEIGHT: 0.0,
    FORCE_RATIO_EXPONENT: 0.0,
    FORCE_RATIO_BOUNDS: (0.6, 1.5),
    AIR_FORCE_RATIO_SCALE: 2.0,
    UNANSWERED_FIRE_WEIGHT: 0.0,
    DEFENSIVE_POSTURE_FACTOR: 1.0,
    SHOCK_MIN_LOSSES: 1,
    MEDIAN_BOUNDS: (0.05, 0.95),
}
DISENGAGEMENT_OPTIONAL_KEYS = tuple(DISENGAGEMENT_NEUTRAL)

_DEFAULT_SIDE_DOCTRINE = {
    DISENGAGEMENT_EROSION: 0.30,
    DISENGAGEMENT_SHOCK: 0.20,
    BREAKPOINT_DISPERSION: 0.5,
    MORALE_WEIGHT: 0.3,
    FORCE_RATIO_EXPONENT: 0.5,
    FORCE_RATIO_BOUNDS: (0.6, 1.5),
    AIR_FORCE_RATIO_SCALE: 2.0,
    UNANSWERED_FIRE_WEIGHT: 0.3,
    DEFENSIVE_POSTURE_FACTOR: 1.2,
    SHOCK_MIN_LOSSES: 2,
    MEDIAN_BOUNDS: (0.05, 0.95),
}

DEFAULT_DISENGAGEMENT_THRESHOLDS = {
    "Blue":    dict(_DEFAULT_SIDE_DOCTRINE),
    "Red":     dict(_DEFAULT_SIDE_DOCTRINE),
    "Neutral": dict(_DEFAULT_SIDE_DOCTRINE),
}


def _check_number(side: str, key: str, value) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"Threshold {key!r} for side {side!r} must be a number, got {value!r}")

    return float(value)


def _check_bounds(side: str, key: str, value) -> Tuple[float, float]:
    if not isinstance(value, (tuple, list)) or len(value) != 2:
        raise TypeError(f"Threshold {key!r} for side {side!r} must be a pair (low, high), got {value!r}")

    low, high = (_check_number(side, key, item) for item in value)

    return low, high


def _validate_optional(side: str, key: str, value) -> None:
    """Vincoli delle chiavi facoltative (v. commento sopra)."""
    if key == SHOCK_MIN_LOSSES:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"Threshold {key!r} for side {side!r} must be an int, got {value!r}")
        if value < 1:
            raise ValueError(f"Threshold {key!r} for side {side!r} must be >= 1, got {value!r}")
        return

    if key == FORCE_RATIO_BOUNDS:
        low, high = _check_bounds(side, key, value)
        if not 0.0 < low <= 1.0 <= high:
            raise ValueError(f"Threshold {key!r} for side {side!r} must satisfy 0 < low <= 1 <= high, got {value!r}")
        return

    if key == MEDIAN_BOUNDS:
        low, high = _check_bounds(side, key, value)
        if not 0.0 < low <= high < 1.0:
            raise ValueError(f"Threshold {key!r} for side {side!r} must satisfy 0 < low <= high < 1, got {value!r}")
        return

    number = _check_number(side, key, value)

    if key in (MORALE_WEIGHT, UNANSWERED_FIRE_WEIGHT):
        valid = 0.0 <= number < 1.0
    elif key in (BREAKPOINT_DISPERSION, FORCE_RATIO_EXPONENT):
        valid = number >= 0.0
    else:  # AIR_FORCE_RATIO_SCALE, DEFENSIVE_POSTURE_FACTOR
        valid = number > 0.0

    if not valid:
        raise ValueError(f"Threshold {key!r} for side {side!r} out of range, got {value!r}")


def validate_disengagement_thresholds(value: Dict) -> None:
    """Valida la struttura {side: {'erosion': float, 'shock': float, [chiavi facoltative]}}.

    Vincoli: 'erosion' e 'shock' obbligatorie, numeri in (0, 1] — 0 significherebbe
    disingaggiarsi senza perdite, 1 equivale a "combattere fino all'annientamento" ed e'
    ammesso come scelta dottrinale esplicita; `shock <= erosion`, perche' con lo stesso
    denominatore la perdita di una singola salva non supera mai la perdita cumulata (v.
    commento sopra). Le chiavi facoltative (DISENGAGEMENT_OPTIONAL_KEYS) hanno i vincoli di
    `_validate_optional`.

    Raises:
        TypeError: struttura non a dizionario, lato non stringa, valore del tipo sbagliato.
        ValueError: chiave mancante o sconosciuta, valore fuori dominio, shock > erosion.
    """
    if not isinstance(value, dict):
        raise TypeError("Disengagement thresholds must be a dictionary")

    for side, thresholds in value.items():
        if not isinstance(side, str):
            raise TypeError(f"Side key {side!r} must be a string")

        if not isinstance(thresholds, dict):
            raise TypeError(f"Thresholds for side {side!r} must be a dictionary")

        missing = [key for key in DISENGAGEMENT_KEYS if key not in thresholds]
        unknown = [key for key in thresholds
                   if key not in DISENGAGEMENT_KEYS and key not in DISENGAGEMENT_OPTIONAL_KEYS]

        if missing:
            raise ValueError(f"Thresholds for side {side!r} miss keys {missing}")

        if unknown:
            raise ValueError(f"Thresholds for side {side!r} have unknown keys {unknown}")

        for key in DISENGAGEMENT_KEYS:
            threshold = _check_number(side, key, thresholds[key])

            if not 0.0 < threshold <= 1.0:
                raise ValueError(f"Threshold {key!r} for side {side!r} must be in (0, 1], got {thresholds[key]!r}")

        if thresholds[DISENGAGEMENT_SHOCK] > thresholds[DISENGAGEMENT_EROSION]:
            raise ValueError(f"Side {side!r}: shock threshold ({thresholds[DISENGAGEMENT_SHOCK]}) must not "
                             f"exceed erosion threshold ({thresholds[DISENGAGEMENT_EROSION]}), "
                             f"otherwise it could never trigger first")

        for key in DISENGAGEMENT_OPTIONAL_KEYS:
            if key in thresholds:
                _validate_optional(side, key, thresholds[key])


def get_disengagement_thresholds(side: Optional[str],
                                 thresholds: Optional[Dict] = None) -> Optional[Dict]:
    """Soglie di disingaggio del lato `side`, o None se il lato non ne dichiara.

    Args:
        side: 'Blue', 'Red', 'Neutral' (o qualunque lato presente in `thresholds`).
        thresholds: tabella dottrinale da usare al posto di DEFAULT_DISENGAGEMENT_THRESHOLDS
                    (es. quella custodita da un C2 di lato); viene validata.

    Returns:
        Una COPIA della voce del lato — il chiamante puo' modificarla senza alterare la
        dottrina; le chiavi facoltative assenti restano assenti (v. `disengagement_parameter`)
        — oppure None se il lato e' sconosciuto. None e' un dato mancante, non un errore: e'
        il consumatore (Engagement_Resolver) a decidere la propria politica e a registrarla.
    """
    table = DEFAULT_DISENGAGEMENT_THRESHOLDS if thresholds is None else thresholds
    validate_disengagement_thresholds(table)

    entry = table.get(side) if isinstance(side, str) else None

    return dict(entry) if entry is not None else None


def disengagement_parameter(entry: Dict, key: str):
    """Valore di `key` nella voce di un lato, o il suo valore neutro se la voce non lo dichiara."""
    if key in DISENGAGEMENT_KEYS:
        return entry[key]

    if key not in DISENGAGEMENT_NEUTRAL:
        raise KeyError(f"unknown disengagement parameter {key!r}")

    return entry.get(key, DISENGAGEMENT_NEUTRAL[key])


# ── DOTTRINA DI TIRO: SATURAZIONE E "DUE MISSILI, POI GUARDA" (2026-09-29) ─────
#
# DECISIONE (Analysis/Document/Proposta_Overkill_Tiro.md, O1-O6). Un tiratore non deve continuare
# a lanciare su un bersaglio gia' condannato dalle salve in volo (overkill). Due regole, di lato:
#
#   'kill_probability_threshold'  soglia P_des: un bersaglio e' SATURO per una forza quando la
#       probabilita' che le salve gia' dirette contro di esso dalla forza (in volo o schedulate)
#       lo distruggano, 1 - prod (1 - accuracy x destroy_capacity)^colpi, raggiunge la soglia.
#       Nessun tiratore della forza gli aggiunge salve (i lanciatori prioritari della regola L2
#       sono esenti). Le intercettazioni possibili sono ignorate nella stima (O5).
#   'max_rounds_in_flight'  tetto per TIRATORE e bersaglio: "due missili, poi guarda". Un tiratore
#       non lancia su un bersaglio finche' ha gia' in volo verso di esso almeno questo numero di
#       colpi (una salva non si spezza: con 0 in volo parte la salva intera).
#
# Se tutti i bersagli di un tiratore sono bloccati, il tiratore aspetta il primo impatto previsto
# su uno di essi e ridecide (O6). Un lato assente dalla tabella (o una chiave None) non ha la
# regola: comportamento precedente al 2026-09-29.
#
# VALORI: STIME DICHIARATE. 0.9 (decisione O3 dell'utente); 2 colpi = la dottrina reale di tiro
# dei SAM "shoot-shoot-look" (decisione dell'utente).
FIRE_KILL_THRESHOLD = 'kill_probability_threshold'
FIRE_MAX_ROUNDS_IN_FLIGHT = 'max_rounds_in_flight'
FIRE_DOCTRINE_KEYS = (FIRE_KILL_THRESHOLD, FIRE_MAX_ROUNDS_IN_FLIGHT)

_DEFAULT_FIRE_DOCTRINE = {FIRE_KILL_THRESHOLD: 0.9, FIRE_MAX_ROUNDS_IN_FLIGHT: 2}

DEFAULT_FIRE_DOCTRINE = {
    "Blue":    dict(_DEFAULT_FIRE_DOCTRINE),
    "Red":     dict(_DEFAULT_FIRE_DOCTRINE),
    "Neutral": dict(_DEFAULT_FIRE_DOCTRINE),
}


def validate_fire_doctrine(value: Dict) -> None:
    """Valida {side: {'kill_probability_threshold': float | None, 'max_rounds_in_flight': int | None}}.

    Raises:
        TypeError: struttura non a dizionario, lato non stringa, valore del tipo sbagliato.
        ValueError: chiave sconosciuta, soglia fuori (0, 1], tetto < 1.
    """
    if not isinstance(value, dict):
        raise TypeError("Fire doctrine must be a dictionary")

    for side, entry in value.items():
        if not isinstance(side, str):
            raise TypeError(f"Side key {side!r} must be a string")

        if not isinstance(entry, dict):
            raise TypeError(f"Fire doctrine for side {side!r} must be a dictionary")

        unknown = [key for key in entry if key not in FIRE_DOCTRINE_KEYS]

        if unknown:
            raise ValueError(f"Fire doctrine for side {side!r} has unknown keys {unknown}")

        threshold = entry.get(FIRE_KILL_THRESHOLD)

        if threshold is not None:
            number = _check_number(side, FIRE_KILL_THRESHOLD, threshold)
            if not 0.0 < number <= 1.0:
                raise ValueError(f"{FIRE_KILL_THRESHOLD!r} for side {side!r} must be in (0, 1], got {threshold!r}")

        cap = entry.get(FIRE_MAX_ROUNDS_IN_FLIGHT)

        if cap is not None:
            if isinstance(cap, bool) or not isinstance(cap, int):
                raise TypeError(f"{FIRE_MAX_ROUNDS_IN_FLIGHT!r} for side {side!r} must be an int, got {cap!r}")
            if cap < 1:
                raise ValueError(f"{FIRE_MAX_ROUNDS_IN_FLIGHT!r} for side {side!r} must be >= 1, got {cap!r}")


def get_fire_doctrine(side: Optional[str], doctrine: Optional[Dict] = None) -> Dict:
    """Dottrina di tiro del lato: COPIA con entrambe le chiavi (None = regola assente).

    Un lato sconosciuto non ha regole ({chiave: None}): e' un dato mancante, non un errore.
    """
    table = DEFAULT_FIRE_DOCTRINE if doctrine is None else doctrine
    validate_fire_doctrine(table)

    entry = table.get(side) if isinstance(side, str) else None
    entry = entry or {}

    return {key: entry.get(key) for key in FIRE_DOCTRINE_KEYS}
