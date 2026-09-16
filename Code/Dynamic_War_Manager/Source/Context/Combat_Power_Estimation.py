"""Stima della combat power in condizioni di fog-of-war (Fase 3 del redesign priorità/combat-power).

Quando un blocco osserva un bersaglio via ricognizione, conosce solo `asset_summary['operative']`
(`{asset_type: {dimensione: conteggio}}`, v. `Block.get_recognition_report`) -- non i modelli
specifici. Questo modulo stima la combat power di quel bersaglio applicando ai conteggi osservati
la mediana del punteggio di combattimento reale dei modelli del registro che ricadono in ciascun
bucket `(asset_type, dimensione)`, con una catena di fallback per i bucket con pochi o nessun
campione.

Usa deliberatamente la STESSA formula del ground-truth (`Context.combat_power_from_score`): la
stima e il calcolo vero per un asset noto non devono poter divergere nel tempo.

Import dei registri Vehicle_Data/Ship_Data/Aircraft_Data sono LAZY (dentro le funzioni, mai a
livello di modulo): Context.py non importa nulla da Asset/*, mentre quei tre moduli importano da
Context.py -- un import a livello di modulo qui creerebbe un ciclo. È anche una scelta di
performance: Vehicle_Data.py costa ~0.25s a import (costruisce l'intero registry via 15 metodi di
normalizzazione per modello), un costo che non deve gravare sull'import di Region.py per i
chiamanti che non usano mai la stima fog-of-war.

Il modulo non fa mai riferimento a `Context.TARGET_CLASSIFICATION`/`get_target_classification`:
quel vocabolario risponde a una domanda diversa ("con quale arma attaccare un bersaglio di
questo tipo/dimensione") e non è nemmeno importato da Vehicle_Data.py/Ship_Data.py per il calcolo
di combat power intrinseca (`_combat_eval`/`_weapon_eval`, v. memoria di progetto).
"""
from functools import lru_cache
from statistics import median
from typing import Dict, Optional, Tuple

from Code.Dynamic_War_Manager.Source.Context import Context

DEFAULT_MIN_SAMPLES = 3


def _efficacy_table_for(force: str, action: Optional[str]) -> Dict[str, float]:
    """Tabella asset_type -> efficacia per (force, action).

    Per 'air' l'azione è ignorata: AIR_COMBAT_EFFICACY non è indicizzata per azione (i task aria
    sono ruoli di missione, non posture tattiche mutuamente esclusive, v. Aircraft.air_combat_power).
    """
    if force == 'ground':
        return Context.GROUND_COMBAT_EFFICACY[action]
    if force == 'sea':
        return Context.SEA_COMBAT_EFFICACY[action]
    if force == 'air':
        return Context.AIR_COMBAT_EFFICACY
    raise ValueError(f"force must be one of {Context.MILITARY_FORCES!r}, got {force!r}")


def _has_any_efficacy(asset_type: str, force: str) -> bool:
    """True se asset_type ha efficacia non-assente in ALMENO un'azione della force (per 'air',
    nella tabella piatta). Usata per escludere dalla mediana globale di fallback i modelli la cui
    combat power è identicamente zero per costruzione in ogni azione (SAM/AAA/EWR sul ground) --
    popolazione strutturalmente diversa da quella che si sta stimando, non un'esclusione arbitraria.
    """
    if force == 'air':
        return asset_type in Context.AIR_COMBAT_EFFICACY
    table = Context.GROUND_COMBAT_EFFICACY if force == 'ground' else Context.SEA_COMBAT_EFFICACY
    return any(asset_type in per_action for per_action in table.values())


@lru_cache(maxsize=None)
def _bucket_scores(force: str, side: Optional[str] = None) -> Dict[Tuple[str, str], Tuple[float, ...]]:
    """{(asset_type, dimensione): (score_modello_1, score_modello_2, ...)} su tutti i modelli del
    registro della force, con lo stesso score/bucket-key che userebbe il ground-truth.

    Bucket key: `asset_type` = campo `category` del modello nel registro *_Data (vocabolario
    generale, es. 'Tank' -- verificato, non la sotto-classe granulare della classe Asset
    Vehicle/Ship/Aircraft); per l'air `category` è una lista di Air_Asset_Type, un modello
    contribuisce a ogni bucket elencato. `dimensione` = Context.get_dimension sulle
    physical_characteristics del modello (Fase 3-bis per l'air).
    Score: VEHICLE[model]['combat score']['global_score'] / SHIP[model][...] / get_aircraft_combat_score.

    Filtro `side`: se un modello ha `users` non vuoto, viene incluso solo se un suo user è nella
    coalizione di `side`; un modello con `users` vuoto/assente è SEMPRE incluso (fallback
    inclusivo deliberato, v. Fase 4 -- oggi Vehicle_Data/Ship_Data non hanno affatto `users`,
    quindi per 'ground'/'sea' questo filtro non esclude ancora nulla).
    """
    if force == 'ground':
        from Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data import Vehicle_Data, VEHICLE
        registry, scores_table, class_name = Vehicle_Data._registry, VEHICLE, 'Vehicle'
    elif force == 'sea':
        from Code.Dynamic_War_Manager.Source.Asset.Ship_Data import Ship_Data, SHIP
        registry, scores_table, class_name = Ship_Data._registry, SHIP, 'Ship'
    elif force == 'air':
        from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import (
            Aircraft_Data, AIRCRAFT_PHYSICAL_CHARACTERISTICS, get_aircraft_combat_score,
        )
        registry, class_name = Aircraft_Data._registry, 'Aircraft'
    else:
        raise ValueError(f"force must be one of {Context.MILITARY_FORCES!r}, got {force!r}")

    buckets: Dict[Tuple[str, str], list] = {}

    for model, data in registry.items():
        users = getattr(data, 'users', None)
        if side is not None and users and not any(u in Context.COALITIONS.get(side, []) for u in users):
            continue

        if class_name == 'Aircraft':
            physical = AIRCRAFT_PHYSICAL_CHARACTERISTICS.get(model)
            score = get_aircraft_combat_score(model)
            asset_types = [c.value if hasattr(c, 'value') else c for c in (data.category or [])]
        else:
            physical = data.physical_characteristics
            score = scores_table[model]['combat score']['global_score']
            asset_types = [data.category]

        if not physical:
            continue
        dimension = Context.get_dimension(class_name, physical['length'], physical['width'], physical['height'], physical['weight'])
        if dimension == 'Unknown':
            continue

        for asset_type in asset_types:
            buckets.setdefault((asset_type, dimension), []).append(score)

    return {key: tuple(values) for key, values in buckets.items()}


def estimated_model_score(
    asset_type: str,
    dimension: Optional[str],
    force: str,
    side: Optional[str] = None,
    min_samples: int = DEFAULT_MIN_SAMPLES,
) -> float:
    """Mediana dello score di combattimento normalizzato per un asset ignoto, catena di fallback:

    1. bucket (asset_type, dimensione), se ha almeno `min_samples` campioni;
    2. altrimenti bucket asset_type-solo (tutte le dimensioni), se non vuoto;
    3. altrimenti mediana globale della force, escludendo gli asset_type senza alcuna efficacia
       in nessuna azione (popolazione strutturalmente disgiunta, v. _has_any_efficacy);
    4. altrimenti 0.0.
    """
    buckets = _bucket_scores(force, side)

    if dimension is not None:
        scores = buckets.get((asset_type, dimension), ())
        if len(scores) >= min_samples:
            return median(scores)

    asset_type_scores = tuple(s for (at, _dim), vals in buckets.items() if at == asset_type for s in vals)
    if asset_type_scores:
        return median(asset_type_scores)

    combatant_scores = tuple(
        s for (at, _dim), vals in buckets.items() if _has_any_efficacy(at, force) for s in vals
    )
    if combatant_scores:
        return median(combatant_scores)

    return 0.0


def build_estimated_combat_power_table(
    force: str,
    action: Optional[str],
    *,
    side: Optional[str] = None,
    efficiency: float = 1.0,
    min_samples: int = DEFAULT_MIN_SAMPLES,
) -> Dict[Tuple[str, Optional[str]], float]:
    """Tabella di calibrazione materializzata {(asset_type, dimensione): combat_power_stimata} per
    ogni asset_type con efficacia in (force, action) e ogni dimensione reale, più `dimension=None`
    per il valore asset_type-only (nessuna distinzione di dimensione). Diagnostica/test -- non è
    consumata da estimate_combat_power_from_asset_summary, che chiama estimated_model_score
    direttamente per ogni voce dell'asset_summary osservato.
    """
    efficacy_table = _efficacy_table_for(force, action)
    table: Dict[Tuple[str, Optional[str]], float] = {}
    for asset_type in efficacy_table:
        for dimension in (*Context.DIMENSION_CLASSES, None):
            score = estimated_model_score(asset_type, dimension, force, side=side, min_samples=min_samples)
            table[(asset_type, dimension)] = Context.combat_power_from_score(asset_type, score, efficacy_table, efficiency)
    return table


def estimate_combat_power_from_asset_summary(
    operative: Dict[str, Dict[str, int]],
    force: str,
    action: Optional[str],
    *,
    side: Optional[str] = None,
    efficiency: float = 1.0,
    min_samples: int = DEFAULT_MIN_SAMPLES,
) -> float:
    """Combat power totale stimata di un bersaglio a partire dal suo asset_summary osservato
    (formato grezzo `{asset_type: {dimensione: conteggio}}`, MAI l'output di get_target_report/
    TargetProfile -- quel collasso per classificazione distrugge il bucket asset_type necessario
    qui, v. memoria di progetto). Ritorna 0.0 per dict vuoto/tutto-zero: nessuna nuova logica
    no-visibility necessaria, si aggancia al gate esistente di Region._calculate_priority.
    """
    if not operative:
        return 0.0

    efficacy_table = _efficacy_table_for(force, action)
    total = 0.0
    for asset_type, dim_counts in operative.items():
        if asset_type not in efficacy_table:
            # Nessuna efficacia per questa azione (es. SAM/AAA/EWR sul ground): combat power
            # identicamente zero per costruzione, v. Context.combat_power_from_score -- salta
            # anche la ricerca di uno score, non solo il suo utilizzo.
            continue
        for dimension, count in dim_counts.items():
            if not count:
                continue
            score = estimated_model_score(asset_type, dimension, force, side=side, min_samples=min_samples)
            total += count * Context.combat_power_from_score(asset_type, score, efficacy_table, efficiency)

    return total
