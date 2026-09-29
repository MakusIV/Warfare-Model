"""Efficacia difensiva antiaerea di un asset e pesi di minaccia per il rapporto di forze percepito.

DECISIONE D4 (2026-09-29, `Analysis/Document/Proposta_Soglia_Rottura_Stocastica.md` §11,
D4a-D4e). La soglia di rottura di una forza (`Logic/Engagement_Resolver`, dottrina in
`Context/Doctrine.py`) dipende dal rapporto fra la forza propria e quella nemica percepita.
La combat power non basta a misurare quest'ultima: SAM, AAA e EWR valgono 0 per definizione
(`Military.air_defense_power()` e' un'altra grandezza, su un'altra scala), e contare un Kub
come un Buk non distingue difese di capacita' molto diversa. Questo modulo da' la misura.

## Efficacia difensiva: aerei abbattuti attesi (D4a)

Per un asset di difesa aerea e N aerei nemici nella sua zona d'intercettazione:

    E(N) = N * (1 - prod_w (1 - p_w) ** (K_w / N))

* `p_w` — potenza contro un SINGOLO aereo dell'arma antiaerea w: `accuracy x
  destroy_capacity` contro la classe di bersaglio di riferimento (righe "Aircraft*" dei
  registri d'arma, B1), per i cannoni per raffica (`Fire_Control.GUN_BURST_ROUNDS`);
  eventualmente corretta per modello (`EFFICACY_CORRECTIONS`, D4c).
* `K_w` — ingaggi possibili mentre un aereo attraversa la zona:
  `min(quota di tempo-canale x canali x cicli, scorta_w // colpi_per_ingaggio)`. I canali sono
  `Mobile.engagement_channels('air')` (default 1); i cicli sono gli ingaggi successivi
  possibili nel tempo di esposizione `T = 2 x portata / REFERENCE_AIRCRAFT_SPEED`
  (attraversamento lungo il diametro, D4b): il primo dopo acquisizione + sequenza di lancio
  + tempo di volo a meta' portata (`Air_Route_Manager.threat_reaction_times`), i successivi
  ogni sequenza di lancio + tempo di volo (durata della raffica per i cannoni). La scorta e'
  quella CORRENTE quando il chiamante la passa (un Buk senza missili vale 0).
* Gli ingaggi sono distribuiti uniformemente sugli N aerei e ogni aereo si abbatte una volta
  sola: per N = 1 e' la letalita' contro un aereo solo, per N grande tende a sum(K_w x p_w),
  quanti aerei il sistema puo' abbattere al massimo.

## Sistema di puntamento (2026-09-29, richiesta dell'utente)

Le armi guidate dallo STESSO sistema di puntamento non si sommano come indipendenti: si
ripartiscono i suoi canali nel tempo di esposizione. Dentro un sistema si impiega prima l'arma
piu' letale finche' ha scorta, poi la successiva nel tempo-canale che resta (Tunguska: prima i
9M311, poi i 2A38M). Sistemi di puntamento diversi dello stesso asset (i SAM di una nave e i
suoi CIWS, un'arma IR a guida autonoma) restano indipendenti fra loro. Regole in `_director`.

## Pesi di minaccia (D4d, D4e)

* Forza AEREA che valuta (`air_threat_weight`): gli asset AD nemici pesano E(N), i caccia
  (Fighter, Fighter_Bomber) 1, il resto 0 — un carro non minaccia un aereo.
* Forza di SUPERFICIE che valuta (`surface_threat_weight`): 1 per ogni asset che puo' colpire
  bersagli di superficie (mezzi da combattimento, aerei non da trasporto/ricognizione, AAA con
  impiego terrestre), 0 per i SAM puri. La stessa regola vale per la forza propria.

Tutte le stime (classe di riferimento, velocita', raffica) sono DICHIARATE, da ricalibrare
con il processo ATCAL interno. Mai eccezioni per dati mancanti: modello ignoto o senza armi AD
-> None / peso di ripiego, con log di debug.
"""

import math
from dataclasses import dataclass
from typing import Dict, Mapping, Optional, Tuple

from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.Utility.Utility import validate_class

# LOGGING --
logger = Logger(module_name=__name__, class_name='Air_Defense_Efficacy').logger


# ── STIME DICHIARATE (D4b) ────────────────────────────────────────────────────

# Bersaglio di riferimento: aereo d'attacco di dimensione media (A-10).
REFERENCE_TARGET_CLASS = 'Aircraft_Attacker'
REFERENCE_TARGET_SIZE = 'med'
# Velocita' dell'aereo che attraversa la zona [m/s].
REFERENCE_AIRCRAFT_SPEED = 200.0
# Velocita' del proiettile se il registro non la dichiara [m/s] (cannoni CIWS).
DEFAULT_PROJECTILE_SPEED = 1000.0

# Correzioni per modello d'asset (D4c): fattore moltiplicativo sulla p delle sue armi, per
# distinguere un sistema dalla sua classe d'efficienza. Vuota: i valori calcolati sono la base.
EFFICACY_CORRECTIONS: Dict[str, float] = {}

AD_TASKS = ('Anti_Air', 'Anti_Missile')
# Tipi d'arma candidati alla difesa aerea (stessi di Mobile.air_defense_volume + CIWS navali).
_AD_WEAPON_TYPES_VEHICLE = ('AA_CANNONS', 'MISSILES')
_AD_WEAPON_TYPES_SHIP = ('MISSILES_SAM', 'CIWS')
_GUN_WEAPON_TYPES = ('AA_CANNONS', 'CIWS')

# Aerei: chi minaccia un aereo (D4d) e chi non minaccia la superficie (D4e).
AIR_TO_AIR_TYPES = ('Fighter', 'Fighter_Bomber')
NON_COMBAT_AIRCRAFT_TYPES = ('Transport', 'Recon', 'Awacs')


# Guide autonome: l'arma non dipende dal radar di tiro dell'asset (cercatore IR del missile).
AUTONOMOUS_GUIDANCE = ('IR',)


@dataclass(frozen=True)
class ADWeaponProfile:
    """Parte statica (dipende solo dal modello) dell'efficacia di un'arma antiaerea.

    Attributes:
        weapon: modello dell'arma (chiave della scorta per arma).
        p: probabilita' di abbattimento per ingaggio contro il bersaglio di riferimento.
        director: sistema di puntamento che guida l'arma (v. "Sistema di puntamento"); le armi
            con lo stesso `director` si ripartiscono i suoi canali, non si sommano.
        channels: canali del sistema di puntamento.
        cycles: ingaggi successivi possibili per canale nel tempo di esposizione, se l'arma
            avesse il sistema di puntamento tutto per se'.
        rounds_per_engagement: unita' di scorta per ingaggio (1 missile, o una raffica).
        full_stock: scorta di dotazione (registro), usata se il chiamante non ne passa una.
    """
    weapon: str
    p: float
    director: str
    channels: int
    cycles: int
    rounds_per_engagement: int
    full_stock: Optional[int]

    @property
    def time_limited_engagements(self) -> int:
        """Canali x cicli: il tetto di ingaggi dell'arma da sola."""
        return self.channels * self.cycles


@dataclass(frozen=True)
class ADProfile:
    model: str
    weapons: Tuple[ADWeaponProfile, ...]


# Cache per (modello, categoria, canali, dotazione): le ultime tre sono lette dall'asset (la
# categoria decide i tempi di reazione di ripiego), quindi due asset dello stesso modello
# con dati diversi (uno stub di test e un Vehicle reale) non condividono il profilo.
_PROFILE_CACHE: Dict[tuple, Optional[ADProfile]] = {}


def clear_cache() -> None:
    """Svuota la cache dei profili (test, registri modificati a runtime)."""
    _PROFILE_CACHE.clear()


def _registry_entry(model: str):
    """(record, is_ship) dal registro veicoli o navi, o (None, False)."""
    from Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data import Vehicle_Data as _VehicleData
    from Code.Dynamic_War_Manager.Source.Asset.Ship_Data import Ship_Data as _ShipData

    record = _VehicleData._registry.get(model)

    if record is not None:
        return record, False

    record = _ShipData._registry.get(model)

    return record, record is not None


def _weapon_db(is_ship: bool):
    from Code.Dynamic_War_Manager.Source.Asset.Ground_Weapon_Data import GROUND_WEAPONS
    from Code.Dynamic_War_Manager.Source.Asset.Ship_Weapon_Data import SHIP_WEAPONS

    return SHIP_WEAPONS if is_ship else GROUND_WEAPONS


def _is_ad_weapon(wdata) -> bool:
    """Arma antiaerea: dati di quota e task Anti_Air (stesso filtro di air_defense_volume)."""
    if not isinstance(wdata, Mapping):
        return False

    if wdata.get('min_altitude') is None or wdata.get('max_altitude') is None:
        return False

    if float(wdata.get('max_altitude') or 0.0) <= 0.0:
        return False

    return 'task' not in wdata or 'Anti_Air' in (wdata.get('task') or ())


def _single_shot_p(wdata, model: str) -> Optional[float]:
    efficiency = wdata.get('efficiency')

    if not isinstance(efficiency, Mapping):
        return None

    entry = (efficiency.get(REFERENCE_TARGET_CLASS) or {}).get(REFERENCE_TARGET_SIZE)

    if not isinstance(entry, Mapping):
        return None

    p = float(entry.get('accuracy', 0.0)) * float(entry.get('destroy_capacity', 0.0))
    p *= float(EFFICACY_CORRECTIONS.get(model, 1.0))

    return min(max(p, 0.0), 1.0)


def _cycles(asset, wdata, weapon_range: float, is_gun: bool) -> int:
    """Ingaggi successivi possibili nel tempo di esposizione (per canale)."""
    from Code.Dynamic_War_Manager.Source.Logic.Air_Route_Manager import threat_reaction_times
    from Code.Dynamic_War_Manager.Source.Logic.Fire_Control import GUN_BURST_ROUNDS

    acquisition, fire = threat_reaction_times(asset, has_missiles=not is_gun)
    speed = float(wdata.get('speed') or wdata.get('muzzle_speed') or DEFAULT_PROJECTILE_SPEED)
    time_of_flight = (weapon_range / 2.0) / speed

    if is_gun and wdata.get('fire_rate'):
        cycle = GUN_BURST_ROUNDS * 60.0 / float(wdata['fire_rate'])
    else:
        cycle = fire + time_of_flight

    exposure = 2.0 * weapon_range / REFERENCE_AIRCRAFT_SPEED
    first = acquisition + fire + time_of_flight

    if exposure < first or cycle <= 0.0:
        return 0

    return 1 + int((exposure - first) // cycle)


def _channels(asset) -> int:
    engagement_channels = getattr(asset, 'engagement_channels', None)
    channels = engagement_channels('air') if callable(engagement_channels) else None

    if isinstance(channels, bool) or not isinstance(channels, int) or channels <= 0:
        return 1

    return channels


def _has_air_radar(record) -> bool:
    radar = getattr(record, 'radar', None)

    try:
        return bool(radar and radar['capabilities']['air'][0])
    except (KeyError, IndexError, TypeError):
        return False


def _director(is_ship: bool, weapon_type: str, weapon: str, wdata, has_radar: bool,
              quantity: int, asset_channels: int) -> Tuple[str, int]:
    """(sistema di puntamento, canali) dell'arma.

    * Veicolo: le armi guidate dal radar di tiro dell'asset (comando radio, SARH, SACLOS e i
      cannoni di un mezzo con radar) condividono il radar e i suoi canali — il caso del
      Tunguska, cannoni e missili sotto lo stesso 1RL144. Le armi a guida autonoma (IR) e i
      cannoni senza radar puntano da se', un canale per arma.
    * Nave: i SAM condividono il direttore di tiro della nave e i suoi canali; ogni tipo di
      CIWS ha il proprio radar, con un canale per impianto (quantita' del registro).
    """
    if is_ship:
        if weapon_type == 'CIWS':
            return f'ciws:{weapon}', max(int(quantity), 1)
        return 'director', asset_channels

    guidance = wdata.get('guide')

    if has_radar and guidance not in AUTONOMOUS_GUIDANCE:
        return 'radar', asset_channels

    return f'own:{weapon}', 1


def _full_stock(asset) -> Optional[Dict[str, int]]:
    stores_from_registry = getattr(asset, 'stores_from_registry', None)
    full = stores_from_registry() if callable(stores_from_registry) else None

    return dict(full) if isinstance(full, Mapping) else None


def _build_profile(asset, model: str, channels: int,
                   full: Optional[Dict[str, int]]) -> Optional[ADProfile]:
    from Code.Dynamic_War_Manager.Source.Logic.Fire_Control import GUN_BURST_ROUNDS

    record, is_ship = _registry_entry(model)
    weapons = getattr(record, 'weapons', None) if record is not None else None

    if not isinstance(weapons, Mapping) or not weapons:
        logger.debug(f"air_defense_profile: model {model!r} unknown or without weapons")
        return None

    allowed = _AD_WEAPON_TYPES_SHIP if is_ship else _AD_WEAPON_TYPES_VEHICLE
    database = _weapon_db(is_ship)
    has_radar = _has_air_radar(record)
    profiles = []

    for weapon_type, weapon_list in weapons.items():
        if weapon_type not in allowed:
            continue

        for item in weapon_list or ():
            if not isinstance(item, (tuple, list)) or not item or not isinstance(item[0], str):
                continue

            weapon = item[0]
            wdata = database.get(weapon_type, {}).get(weapon)

            if not _is_ad_weapon(wdata):
                continue

            p = _single_shot_p(wdata, model)

            if p is None or p <= 0.0:
                continue

            is_gun = weapon_type in _GUN_WEAPON_TYPES or 'fire_rate' in wdata
            raw_range = wdata.get('range')
            weapon_range = (float(raw_range) * 1000.0 if is_ship
                            else float((raw_range or {}).get('direct', 0.0)))

            if weapon_range <= 0.0:
                continue

            quantity = item[1] if len(item) > 1 and isinstance(item[1], int) else 1
            director, director_channels = _director(is_ship, weapon_type, weapon, wdata, has_radar,
                                                    quantity, channels)
            profiles.append(ADWeaponProfile(
                weapon=weapon, p=p, director=director, channels=director_channels,
                cycles=_cycles(asset, wdata, weapon_range, is_gun),
                rounds_per_engagement=GUN_BURST_ROUNDS if is_gun else 1,
                full_stock=(full or {}).get(weapon)))

    if not profiles:
        logger.debug(f"air_defense_profile: model {model!r} has no air-defence weapon with data")
        return None

    # Dentro un sistema di puntamento si impiega prima l'arma piu' letale (v. expected_kills).
    profiles.sort(key=lambda w: (w.director, -w.p, w.weapon))

    return ADProfile(model=model, weapons=tuple(profiles))


def air_defense_profile(asset) -> Optional[ADProfile]:
    """Profilo statico dell'asset (in cache), o None se non e' un asset di difesa aerea.

    Gli aerei non hanno profilo: la loro minaccia aria-aria e' un peso fisso (v.
    `air_threat_weight`).
    """
    if validate_class(asset, 'Aircraft'):
        return None

    model = getattr(asset, '_model', None)

    if not isinstance(model, str):
        return None

    channels = _channels(asset)
    full = _full_stock(asset)
    category = getattr(asset, 'category', None)
    key = (model, category if isinstance(category, str) else None, channels,
           tuple(sorted(full.items())) if full is not None else None)

    if key not in _PROFILE_CACHE:
        _PROFILE_CACHE[key] = _build_profile(asset, model, channels, full)

    return _PROFILE_CACHE[key]


def expected_kills(profile: ADProfile, n_aircraft: int,
                   stock: Optional[Mapping[str, int]] = None) -> float:
    """E(N) del profilo contro `n_aircraft` aerei, con la scorta data (default: dotazione).

    Una voce assente da `stock` usa la dotazione; una dotazione non modellata (None) non
    limita gli ingaggi, che restano limitati dal tempo.
    """
    if isinstance(n_aircraft, bool) or not isinstance(n_aircraft, int) or n_aircraft < 0:
        raise ValueError(f"n_aircraft must be an int >= 0, got {n_aircraft!r}")

    if n_aircraft == 0:
        return 0.0

    log_survival = 0.0
    time_left: Dict[str, float] = {}

    for weapon in profile.weapons:
        # Quota del tempo-canale del sistema di puntamento ancora libera: le armi dello stesso
        # sistema se la ripartiscono, nell'ordine di letalita' (la migliore finche' ha scorta).
        left = time_left.get(weapon.director, 1.0)
        capacity = weapon.time_limited_engagements

        if left <= 0.0 or capacity <= 0:
            continue

        units = stock.get(weapon.weapon) if stock is not None and weapon.weapon in stock else weapon.full_stock
        engagements = left * capacity

        if units is not None:
            engagements = min(engagements, max(int(units), 0) // weapon.rounds_per_engagement)

        if engagements <= 0:
            continue

        time_left[weapon.director] = left - engagements / capacity

        if weapon.p >= 1.0:
            return float(n_aircraft)

        log_survival += (engagements / n_aircraft) * math.log1p(-weapon.p)

    return n_aircraft * (1.0 - math.exp(log_survival))


def air_defense_efficacy(asset, n_aircraft: int, *,
                         stock: Optional[Mapping[str, int]] = None) -> Optional[float]:
    """E(N): aerei abbattuti attesi mentre `n_aircraft` aerei attraversano la zona dell'asset.

    Returns:
        float in [0, n_aircraft], oppure None se l'asset non e' un asset di difesa aerea
        noto (modello ignoto, nessun'arma antiaerea con dati di efficacia, aereo).
    """
    profile = air_defense_profile(asset)

    if profile is None:
        return None

    return expected_kills(profile, n_aircraft, stock)


def _registry_has_surface_weapon(model: str) -> Optional[bool]:
    """True se il modello ha almeno un'arma con impiego diverso dalla sola difesa aerea."""
    record, is_ship = _registry_entry(model)
    weapons = getattr(record, 'weapons', None) if record is not None else None

    if not isinstance(weapons, Mapping):
        return None

    database = _weapon_db(is_ship)

    for weapon_type, weapon_list in weapons.items():
        for item in weapon_list or ():
            if not isinstance(item, (tuple, list)) or not item or not isinstance(item[0], str):
                continue

            wdata = database.get(weapon_type, {}).get(item[0])

            if not isinstance(wdata, Mapping):
                # Arma senza dati: non si puo' escludere l'impiego terrestre.
                return True

            tasks = wdata.get('task')

            if not _is_ad_weapon(wdata) or not tasks or any(t not in AD_TASKS for t in tasks):
                return True

    return False


def surface_threat_weight(asset) -> float:
    """Peso di un asset come minaccia per una forza di SUPERFICIE (D4e): 1 oppure 0.

    0 per i SAM puri (tutte le armi solo antiaeree/antimissile) e per gli aerei da trasporto,
    ricognizione e AWACS; 1 per tutto il resto, compresi gli asset senza dati di registro
    (non si esclude cio' che non si conosce).
    """
    if validate_class(asset, 'Aircraft'):
        return 0.0 if getattr(asset, 'asset_type', None) in NON_COMBAT_AIRCRAFT_TYPES else 1.0

    model = getattr(asset, '_model', None)

    if not isinstance(model, str):
        return 1.0

    has_surface = _registry_has_surface_weapon(model)

    return 0.0 if has_surface is False else 1.0


def air_threat_weight(asset, n_aircraft: int, *,
                      stock: Optional[Mapping[str, int]] = None) -> float:
    """Peso di un asset come minaccia per una forza AEREA di `n_aircraft` aerei (D4d).

    Asset di difesa aerea: E(N) con la scorta data; caccia (AIR_TO_AIR_TYPES): 1; altro: 0.
    """
    if validate_class(asset, 'Aircraft'):
        return 1.0 if getattr(asset, 'asset_type', None) in AIR_TO_AIR_TYPES else 0.0

    efficacy = air_defense_efficacy(asset, n_aircraft, stock=stock)

    return efficacy if efficacy is not None else 0.0


# ── RWR E CATEGORIE SAM (2026-09-29, richiesta dell'utente) ───────────────────
#
# Un aereo "sa" di essere ingaggiato da un sistema di difesa aerea se il suo RWR identifica la
# categoria di quel sistema quando il radar del sistema lo illumina (Asset/Aircraft_Rwr_Data).
# Categorie: VSHORAD, SHORAD, MRSAM, LRSAM. Fonte primaria SAM_WEAPON_CATEGORY (classificazione
# per sistema missilistico fornita dall'utente); ripiego per i veicoli dai `roles` del registro
# (la categoria piu' alta dichiarata vince: Tunguska AAA + SHORAD -> SHORAD; AAA -> VSHORAD), per
# le navi dalla portata del SAM piu' lungo (soglie SHIP_SAM_*_KM, stima dichiarata), VSHORAD se
# ha solo CIWS.
# Solo chi EMETTE e' identificabile: un veicolo senza radar aria (Strela-1/10, Chaparral,
# Linebacker, ZSU-57-2, VADS: puntamento ottico o cercatore IR) non accende nessun RWR.

from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Rwr_Data import (  # noqa: E402
    GUIDANCE, LRSAM, MRSAM, SEARCH, SHORAD, TRACK, VSHORAD, rwr_categories, rwr_modes)

SAM_CATEGORIES = (VSHORAD, SHORAD, MRSAM, LRSAM)

# Categoria per SISTEMA MISSILISTICO, fonte primaria: `Analysis/Document/classificazione_sam_1950_2000.md`
# (tabella 1, fornita dall'utente il 2026-09-29). Solo i missili dei registri che vi compaiono;
# le varianti navali sono ricondotte al sistema terrestre da cui derivano (derivazione, annotata).
# Per le armi assenti vale il ripiego: `roles` del veicolo o portata del SAM navale.
SAM_WEAPON_CATEGORY = {
    'FIM-92-Stinger': VSHORAD,      # FIM-92 Stinger
    '9M31-SAM': SHORAD,             # 9K31 Strela-1 (SA-9)
    '9M37-SAM': SHORAD,             # 9K35 Strela-10 (SA-13)
    '9M33-SAM': SHORAD,             # 9K33 Osa (SA-8)
    '9M331-SAM': SHORAD,            # 9K330 Tor (SA-15)
    'MIM-72-SAM': SHORAD,           # MIM-72 Chaparral
    'Roland-SAM': SHORAD,           # Roland
    '3M9-SAM': MRSAM,               # 2K12 Kub (SA-6)
    '9M38-SAM': MRSAM,              # 9K37 Buk (SA-11)
    '5V55R-SAM': LRSAM,             # S-300P (SA-10)
    'HHQ-7': SHORAD,                # HQ-7, versione navale
    'HHQ-9': LRSAM,                 # HQ-9, versione navale
    'SA-N-4-Gecko': SHORAD,         # derivazione: versione navale dell'Osa
    'SA-N-9-Gauntlet': SHORAD,      # derivazione: versione navale del Tor
    'S-300F': LRSAM,                # derivazione: versione navale dell'S-300
}
_CATEGORY_RANK = {category: rank for rank, category in enumerate(SAM_CATEGORIES)}
_ROLE_CATEGORY = (('LORAD', LRSAM), ('MERAD', MRSAM), ('SHORAD', SHORAD), ('AAA', VSHORAD))
SHIP_SAM_LONG_RANGE_KM = 100.0
SHIP_SAM_MEDIUM_RANGE_KM = 30.0


def sam_category(asset) -> Optional[str]:
    """Categoria SAM dell'asset di difesa aerea (v. sopra), o None se non classificabile."""
    if validate_class(asset, 'Aircraft'):
        return None

    model = getattr(asset, '_model', None)

    if not isinstance(model, str):
        return None

    record, is_ship = _registry_entry(model)

    if record is None:
        return None

    # Fonte primaria: la categoria dei sistemi missilistici dell'asset (la piu' alta).
    listed = [SAM_WEAPON_CATEGORY[item[0]] for items in (getattr(record, 'weapons', None) or {}).values()
              for item in items or () if isinstance(item, (tuple, list)) and item and item[0] in SAM_WEAPON_CATEGORY]

    if listed:
        return max(listed, key=_CATEGORY_RANK.__getitem__)

    if not is_ship:
        roles = getattr(record, 'roles', None) or ()

        for role, category in _ROLE_CATEGORY:
            if role in roles:
                return category

        return None

    weapons = getattr(record, 'weapons', None) or {}
    ranges = [float((_weapon_db(True).get('MISSILES_SAM', {}).get(item[0]) or {}).get('range') or 0.0)
              for item in weapons.get('MISSILES_SAM') or () if isinstance(item, (tuple, list)) and item]

    if ranges and max(ranges) > 0.0:
        longest = max(ranges)
        return LRSAM if longest >= SHIP_SAM_LONG_RANGE_KM else MRSAM if longest >= SHIP_SAM_MEDIUM_RANGE_KM else SHORAD

    return VSHORAD if weapons.get('CIWS') else None


def emits_radar(asset) -> bool:
    """True se l'asset ha un radar aria (le navi sempre): solo allora un RWR lo puo' vedere."""
    model = getattr(asset, '_model', None)

    if not isinstance(model, str):
        return False

    record, is_ship = _registry_entry(model)

    if record is None:
        return False

    return True if is_ship else _has_air_radar(record)


def rwr_identifies(aircraft, emitter) -> bool:
    """True se l'RWR di `aircraft` riconosce come minaccia SAM la categoria di `emitter`, che emette.

    Basta che la categoria stia in una delle classi dell'RWR: un RWR che non separa le categorie
    (SPO-10: "SAM" generico; ALR-45: SAM non distinti fra loro) riconosce comunque la minaccia.
    """
    if not validate_class(aircraft, 'Aircraft') or not emits_radar(emitter):
        return False

    category = sam_category(emitter)

    return category is not None and category in rwr_categories(getattr(aircraft, '_model', None))


# Istante in cui la minaccia riconosciuta e' percepita (v. rwr_perception).
PERCEIVED_AT_DETECTION = 'detection'
PERCEIVED_AT_LAUNCH = 'launch'


def rwr_perception(aircraft, emitter) -> Optional[str]:
    """Quando l'RWR di `aircraft` percepisce `emitter` come minaccia SAM, o None se mai.

    * PERCEIVED_AT_DETECTION — l'RWR rileva la ricerca: la minaccia e' percepita quando il radar
      del sistema rileva l'aereo;
    * PERCEIVED_AT_LAUNCH — l'RWR rileva solo tracciamento o guida (SPO-10): la minaccia e'
      percepita al lancio contro l'aereo, preceduto dal tracciamento (approssimazione dichiarata:
      il tracciamento comincia qualche istante prima).
    """
    if not rwr_identifies(aircraft, emitter):
        return None

    modes = rwr_modes(getattr(aircraft, '_model', None))

    if SEARCH in modes:
        return PERCEIVED_AT_DETECTION

    if TRACK in modes or GUIDANCE in modes:
        return PERCEIVED_AT_LAUNCH

    return None
