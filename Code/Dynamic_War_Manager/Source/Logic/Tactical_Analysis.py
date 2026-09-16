"""
MODULE Tactical_Analysis

Analisi/raccolta di informazioni a livello tattico: producono FATTI (profili di composizione di
un bersaglio, potenza di combattimento stimata/rappresentativa, inventario di asset) a partire da
un blocco o da un report di ricognizione -- mai un punteggio/una scelta. Il livello di scoring
(che assegna una priorità/un punteggio a un'opzione) è in Logic/Tactical_Evaluation.py.

Nessuna funzione di questo modulo riceve o importa una `Region`: operano su singoli blocchi/report
già estratti dal chiamante. Questo è deliberato -- è il vincolo che permette a un futuro
pianificatore (centrale o regionale) di valutare bersagli/scenari ipotetici senza dover costruire
una Region reale, e che evita qualunque ciclo di import verso Context.Region.

Estratto da Region.py durante il refactoring architetturale 2026-09-16 (v. memoria di progetto
project_region_tactical_refactor_plan) -- le docstring originali sono state preservate.
"""
from typing import Any, Dict, List, Optional

from Code.Dynamic_War_Manager.Source.Context import Context
from Code.Dynamic_War_Manager.Source.Context import Combat_Power_Estimation
from Code.Dynamic_War_Manager.Source.Block.Block import Block, ASSET_TYPE
from Code.Dynamic_War_Manager.Source.Block.Military import Military
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger

logger = Logger(module_name=__name__, class_name='Tactical_Analysis').logger

# Shape shared by both "target classification" producers: get_target_report (fog-of-war, built
# from a recon report) and Tactical_Evaluation's ground-truth producer built directly from a
# block's real assets. {classification: {'big'|'med'|'small': count}}.
TargetProfile = Dict[str, Dict[str, int]]


def estimate_target_combat_power(report: Dict, force: Optional[str], action: Optional[str]) -> float:
    """Combat power stimata (fog-of-war) di UN bersaglio per una specifica azione, a partire
    dal suo report di ricognizione (v. Region.get_recon_reports). Building block dello snapshot
    di ricognizione (v. Tactical_Evaluation): legge `asset_summary['operative']` grezzo (MAI
    l'output di get_target_report/TargetProfile, che collassa per classificazione) e lo passa a
    Combat_Power_Estimation con `side=report['side']` (il lato del bersaglio osservato, per
    calibrare la stima sui modelli plausibili per quel lato -- v. Fase 4/campo `users`) e
    `efficiency=1.0` quando il report non riporta un'efficienza rilevata (scelta prudenziale
    deliberata, indipendente dalla policy "non visto -> priorità bassa": qui il bersaglio È
    stato visto, solo la sua efficienza operativa è incerta).
    """
    if not force:
        return 0.0
    operative = ((report or {}).get('asset_summary') or {}).get('operative') or {}
    side = (report or {}).get('side')
    efficiency = 1.0 if (report or {}).get('efficiency') is None else report['efficiency']
    return Combat_Power_Estimation.estimate_combat_power_from_asset_summary(
        operative, force, action, side=side, efficiency=efficiency
    )


def get_target_report(report: Dict) -> Optional[Dict]:

    """Classify a target based on reconnaissance report."""

    if not isinstance(report, dict):
        raise TypeError(f"Report must be a dictionary, got {type(report).__name__}")

    _assets = report.get('asset_summary', None)
    _operative = _assets.get('operative', None) if _assets else None

    if not _operative:
        logger.warning("No operative assets found in report for target classification.")
        return None

    # FIX 5: un dict non vuoto ma con conteggi tutti a zero non è "dati validi con zero asset" --
    # è il caso in cui asset_summary esiste (asset_type/dimension bucket popolati dal loop di
    # Block.get_recognition_report) ma il gate probabilistico di rilevamento non è scattato per
    # questo report, quindi nessun conteggio è stato incrementato. Va trattato come "nessuna
    # visibilità" alla pari del dict vuoto sopra, non come un profilo target reale a zero asset.
    # Controllato sui conteggi grezzi di _operative, PRIMA del raggruppamento per classificazione,
    # per non confondere questo caso con quello (preesistente, diverso) in cui gli asset_type
    # presenti sono reali/con conteggi ma nessuno è coperto da TARGET_CLASSIFICATION.
    raw_total = sum(count for asset_data in _operative.values() for count in asset_data.values())
    if raw_total == 0:
        logger.warning("Operative asset counts all zero (no detection this report) -- no visibility for target classification.")
        return None

    target_classification_report = {}  # FIX 1: inizializzare prima del loop

    for asset_type, asset_data in _operative.items():

        _classification = Context.get_target_classification(asset_type)

        if _classification is None:  # FIX 4: saltare asset_type senza classificazione
            logger.warning(f"No target classification found for asset type: {asset_type}. Skipping.")
            continue

        if target_classification_report.get(_classification) is None:
            target_classification_report[_classification] = asset_data.copy()  # FIX 2: aggiunge la chiave, non resetta il dict

        else:
            for dim_key, count in asset_data.items():  # FIX 3: usa le chiavi reali di asset_data
                target_classification_report[_classification][dim_key] = (
                    target_classification_report[_classification].get(dim_key, 0) + count
                )

    return target_classification_report


def profile_to_weapon_distribution(profile: TargetProfile) -> Dict[str, Dict[str, Any]]:
    """Convert a TargetProfile into the weighted-distribution shape used by
    Aircraft_Data.combat_score_target_effectiveness_by_distribution /
    Aircraft_Loadouts.loadout_target_effectiveness_by_distribuition:
    {classification: {'perc_type': float, 'perc_dimension': {dim: float}}}.

    Replaces the previous coverage-truncation heuristic (_profile_to_weapon_lists, which
    included/excluded (class, dimension) pairs via an 85% coverage cutoff): every
    classification/dimension actually present in the profile contributes to the score,
    weighted by its real share of the target's composition, instead of being dropped once a
    coverage threshold was already met. No pre-collapsing through Context.get_weapon_target_class
    is needed here -- get_weapon_score_target already normalizes each classification internally
    when scoring, and the weighted sum is mathematically equivalent whether or not distinct
    classifications that collapse onto the same weapon-table class are merged beforehand.

    perc_type values sum to 1.0 across the returned classifications (rounding aside); each
    classification's perc_dimension values sum to 1.0 among themselves. Zero-count dimensions
    and classifications with a zero total are dropped. Returns {} for an empty/falsy profile or
    one whose total count is zero.
    """
    if not profile:
        return {}

    total = sum(sum(dims.values()) for dims in profile.values())
    if total <= 0:
        return {}

    distribution: Dict[str, Dict[str, Any]] = {}
    for classification, dims in profile.items():
        class_total = sum(dims.values())
        if class_total <= 0:
            continue
        distribution[classification] = {
            'perc_type': class_total / total,
            'perc_dimension': {
                dimension: count / class_total
                for dimension, count in dims.items()
                if count > 0
            },
        }

    return distribution


def target_profile_from_report(report: Dict) -> Optional[TargetProfile]:
    """Recon-report-based producer of a TargetProfile (fog-of-war), delegates to get_target_report.

    Mirrors the ground-truth producer in Tactical_Evaluation (target_profile_from_block) so future
    callers needing "a TargetProfile, from whichever source" can depend on this name regardless of
    which producer backs it. get_target_report remains the canonical, public, separately-tested
    implementation.
    """
    return get_target_report(report)


def representative_combat_power(block: Military, force: Optional[str], action: Optional[str] = None) -> float:
    """Combat power di un blocco per una forza (ed eventualmente un'azione specifica), usata dal
    rapporto di confronto nel calcolo di priorità (v. Tactical_Evaluation.calculate_priority).

    Per 'air': Aircraft.set_combat_power replica LO STESSO valore aggregato su tutti i task di
    ACTION_TASKS['air'] (i task aria — CAP, Strike, Intercept, ... — non sono posture tattiche
    mutuamente esclusive come Attack/Defense/Maintain/Retrait, v. Context.AIR_COMBAT_EFFICACY, che è
    piatta), quindi `action` è ignorato per costruzione: si prende un solo task.
    Per 'ground'/'sea': se `action` è specificato, ritorna la combat power per quel solo task
    (v. memoria di progetto feedback_combat_power_action_selection). Se `action` è None, comportamento
    legacy: somma su tutti i task (mantenuto per compatibilità con i chiamanti che non selezionano
    un'azione specifica).
    """
    if not force:
        return 0.0
    if force == 'air':
        breakdown = block.combat_power(force=force)
        return next(iter(breakdown.values()), 0.0)
    if action is None:
        breakdown = block.combat_power(force=force)
        return sum(breakdown.values())
    return block.combat_power(force=force, action=action)


def target_profile_from_block(target_block: Block) -> TargetProfile:
    """Ground-truth (non-random) target classification profile built directly from target_block's
    assets.

    Deterministic counterpart of get_target_report: classifies target_block's real assets with
    the same rule as Block.get_recognition_report (Context.classify_asset_dimension), with all
    recon probability/randomness gating removed -- every operative asset is counted
    unconditionally. Damaged/destroyed assets are ignored: only live threats matter for the
    priority calculations this feeds.

    Nessuna cache: v. memoria di progetto project_region_tactical_refactor_plan sul perché le
    funzioni tattiche estratte non usano più @lru_cache (un futuro pianificatore what-if ha
    bisogno di valutazioni isolate, non di una cache condivisa fra scenari ipotetici).
    """
    target_profile: TargetProfile = {}

    for asset in target_block.assets.values():

        if not asset.is_operative():
            continue

        asset_type = getattr(asset, 'asset_type', None)

        asset_dimension = Context.classify_asset_dimension(asset, valid_asset_types=ASSET_TYPE)
        if asset_dimension is None:
            logger.warning(
                f"Asset not classifiable for target profile (asset id: {getattr(asset, 'id', None)}, "
                f"asset type: {asset_type}). Skipping."
            )
            continue

        classification = Context.get_target_classification(asset_type)
        if classification is None:
            logger.warning(f"No target classification found for asset type: {asset_type}. Skipping.")
            continue

        class_counts = target_profile.setdefault(classification, {})
        class_counts[asset_dimension] = class_counts.get(asset_dimension, 0) + 1

    return target_profile


def operative_aircraft_by_model(block: Military) -> Dict[str, List]:
    """{model: [Aircraft operativi]} per block, raggruppati per modello (non per ruolo/asset_type
    come fa get_asset_list). Usato da Tactical_Evaluation.target_affinity per pesare il contributo
    di ciascun modello per numero di velivoli."""
    asset_list = block.get_asset_list(asset_class='Aircraft')
    if not asset_list:
        return {}

    by_model: Dict[str, List] = {}
    for assets in asset_list.get('Aircraft', {}).values():
        for asset in assets:
            if not asset.is_operative():
                continue
            model = getattr(asset, 'model', None)
            if model is None:
                continue
            by_model.setdefault(model, []).append(asset)

    return by_model
