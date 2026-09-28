"""Weapon delivery — **da che quota, a che velocita' e da che direzione si sgancia una bomba**.

Proposta B di `Analysis/Document/Proposta_Munizioni_Compatibili_e_Rotte_Attacco.md` (§2.3-§2.5),
implementata il 2026-09-27 con le decisioni dell'utente:
  * B1: finestre di rilascio nel registro (`AIR_WEAPONS['BOMBS'][...]['release']`, fatte il 2026-09-26);
  * B2: vale per TUTTE le missioni, DCS e virtuali (una fisica, un pianificatore, due esecutori);
  * B3/D-8: due liste di minacce (intercettazione e rilevamento) e tempo di esposizione "dopo il
    primo lancio possibile" (v. `ThreatExposure` in `Command/Attack_Types.py`);
  * B4: tre profili ammessi, livellato / picchiata / cabrata (loft), con UN SOLO modello balistico
    vettoriale;
  * B5: direzione d'attacco libera, scelta dall'algoritmo;
  * B6: il DES ricava gittata e tempo di caduta delle bombe da qui (`bomb_engagement_estimate`,
    chiamata da `Logic/Fire_Control.shot_spec_for`);
  * drag selezionabile (Mk-82AIR, M/71, SAMP-250HD): si usa la finestra `low_drag` se la quota
    candidata vi rientra, altrimenti `high_drag`.

Due livelli, stateless come il resto di `Logic/`:

1. **Fisica pura** (`release_windows`, `fall_time`, `release_solution`, `bomb_engagement_estimate`):
   nessuna dipendenza da rotte o minacce. E' la parte condivisa con il DES.
2. **Pianificazione** (`plan_attack_profile`): sceglie quota, velocita', profilo e azimut d'ingresso
   minimizzando l'esposizione alle minacce del tratto d'attacco, e restituisce un `AttackProfile`.

## Balistica (STIMA DICHIARATA, fisica elementare da tarare)

Moto parabolico nel vuoto con velocita' iniziale v inclinata di `pitch` (negativo in picchiata,
positivo in cabrata, 0 livellato), da quota h sopra il bersaglio:

    v_z = v * sin(pitch);   t = (v_z + sqrt(v_z^2 + 2*g*h)) / g;   R = v * cos(pitch) * t

poi i fattori di resistenza della classe `drag` (DRAG_FACTORS: gittata ridotta, caduta allungata).
Due casi del registro sostituiscono la balistica:
  * `glide_ratio` (bombe guidate plananti, GBU-24): R = max(balistica, glide_ratio * h) e, se vince
    la planata, t = R / v (planata a velocita' costante: stima);
  * `standoff_range_km` (dispenser planante BK-90): R interpolata linearmente nella finestra di quota
    fra (min, max) del registro, t = R / v.
Gittata obliqua (quella che il DES confronta con la sua sfera di portata): sqrt(R^2 + h^2).

Ordini di grandezza (vuoto, livellato): F-16 a 850 km/h da 3000 m -> t ~ 24,7 s, R ~ 5,8 km;
A-10 a 580 km/h da 1000 m -> t ~ 14,3 s, R ~ 2,3 km.

## Pianificazione (euristica deterministica, nessun RNG)

1. Fascia ammessa = inviluppo `attack` del loadout ∩ finestra `release` dell'arma, per quota (AGL
   sopra il bersaglio) e velocita'. Vuota -> `feasible=False` con il motivo: e' il controllo che
   evita la correzione silenziosa della quota da parte di DCS.
2. Velocita': quella `attack` del loadout, ridotta al massimo della finestra se lo supera (un aereo
   puo' rallentare, non accelerare oltre il suo inviluppo); sotto il minimo -> finestra scartata.
3. Quote candidate: griglia di ALTITUDE_GRID_STEPS quote sulla fascia, piu' i bordi di ogni volume
   d'intercettazione (tetto x 1,05, base x 0,95: i margini di Air_Route_Manager) che cadono nella
   fascia. Profili: quelli della finestra; angoli di picchiata DIVE_ANGLES_DEG dentro `dive_angle`;
   cabrata a LOFT_PITCH_DEG.
4. Azimut: AZIMUTH_COUNT direzioni equispaziate, o quelle imposte dal chiamante.
5. Per ogni candidato: tratto IP -> sgancio -> uscita a quota costante e velocita' costante;
   finestre di permanenza nei volumi (analitiche, `_segment_cylinder_interval`) ed esposizione
   effettiva per minaccia (B3/D-8):
       t_lancio  = max(t_ingresso V_I, t_contatto V_R + acquisition_time) + min_fire_time
       effettivo = max(0, t_uscita V_I - t_lancio)
   dove V_R e' il volume di rilevamento con lo stesso `source_id` del volume d'intercettazione. Senza
   V_R associato: t_contatto = -inf (sito gia' in traccia, caso conservativo). Con V_R associato e mai
   toccato: il sito non vede l'aereo e non lancia (effettivo = 0). IP gia' dentro V_R: rilevato
   prima dell'IP, t_contatto = -inf.
6. Scelta: minimo di  sum(effettivo x danger_level)  (esposizione pesata; 0 = tratto d'attacco
   senza possibilita' di lancio nemico), poi quota piu' bassa (precisione di sgancio [I]), poi
   azimut piu' vicino alla direzione della base se data (transito piu' corto), poi azimut,
   profilo, angolo e drag (determinismo). Le minacce non rendono MAI il profilo non
   fattibile: la minaccia non evitabile vicino al bersaglio si accetta (decisione utente).
7. Transito (opzionale, con `home_point`): base -> IP e uscita -> base con
   `RoutePlanner.calcCanonicalRoute`, concatenati nella `full_route`.

Le finestre del tratto d'attacco si calcolano con l'intervallo analitico segmento/cilindro
(`Air_Route_Manager._segment_cylinder_interval`, lo stesso delle metriche di rilevamento dei
percorsi) e non con `Contact_Scheduler.route_threat_windows`: quest'ultimo usa la geometria sympy,
troppo lenta per le centinaia di candidati valutati, e sui segmenti rettilinei da' lo stesso
intervallo.

## Limiti dichiarati

- La geometria della picchiata/cabrata non e' nel tratto: IP -> sgancio e' a quota costante, il
  profilo entra solo nella balistica (gittata e caduta).
- Il cilindro d'intercettazione e' l'unione degli inviluppi dell'asset: nessuna zona morta interna.
  Il vantaggio del volo basso lo da' l'orizzonte radar del volume di RILEVAMENTO (se fornito).
- Terreno non modellato: AGL = quota - quota del bersaglio.
- Solo armi a caduta (`AIR_WEAPONS['BOMBS']`); missili aria-superficie: fuori scope.
- Nessun componente LLM, nessun uso del modulo `random`.
"""

import math
from collections import namedtuple
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple, Union

from sympy import Point3D

from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Loadouts import AIRCRAFT_LOADOUTS
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Weapon_Data import AIR_WEAPONS
from Code.Dynamic_War_Manager.Source.Command.Attack_Types import AttackProfile, ThreatExposure
from Code.Dynamic_War_Manager.Source.Logic.Air_Route_Manager import (
    MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MAX_VALUE,
    MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MIN_VALUE,
    RoutePlanner,
    ThreatMode,
    _segment_cylinder_interval,
)
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger


logger = Logger(module_name=__name__, class_name='Weapon_Delivery').logger


# ── COSTANTI ──────────────────────────────────────────────────────────────────

# Accelerazione di gravita' standard [m/s^2] (definizione).
G_MS2 = 9.80665

# km/h -> m/s (definizione).
KMH_MS = 1000.0 / 3600.0

# Fattori di resistenza per classe `drag` del registro. STIME non tarate: una bomba a bassa
# resistenza perde ~10 % di gittata rispetto al vuoto alle quote/velocita' d'impiego tattico; una
# frenata (Snakeye, ballute AIR, paracadute) circa la meta', e cade ~30 % piu' a lungo.
DRAG_FACTORS = {
    'low':  {'range': 0.9, 'time': 1.05},
    'high': {'range': 0.5, 'time': 1.3},
}

# Angolo di cabrata al rilascio in loft [gradi]. STIMA: il registro dichiara se il loft e' ammesso,
# non l'angolo; 30 gradi e' il centro della fascia tipica 20-45.
LOFT_PITCH_DEG = 30.0

# Angoli di picchiata candidati [gradi], filtrati dentro `dive_angle` del registro. STIMA: i profili
# tipici di picchiata leggera, media e ripida.
DIVE_ANGLES_DEG = (15.0, 30.0, 45.0, 60.0)

# Quote candidate sulla fascia ammessa (estremi inclusi).
ALTITUDE_GRID_STEPS = 6

# Azimut d'ingresso candidati (equispaziati da nord). 12 = passo di 30 gradi.
AZIMUTH_COUNT = 12

# Distanza IP -> punto di sgancio [m]. STIMA: tratto d'ingresso rettilineo di 5-6 NM, dentro la
# fascia tipica 5-15 km dei punti iniziali d'attacco.
IP_RUN_IN_DISTANCE_M = 10_000.0

# Disimpegno: dopo lo sgancio l'aereo vira di EGRESS_TURN_DEG rispetto alla direzione bersaglio ->
# attaccante (cioe' non ripercorre l'ingresso) e percorre EGRESS_DISTANCE_M. STIME.
EGRESS_TURN_DEG = 45.0
EGRESS_DISTANCE_M = 10_000.0

# Tempo di inversione di default per le rotte di transito [s] (parametro di calcRoute non presente
# nei dati d'aereo). STIMA, stesso valore d'esempio di Utility/visualizer.py.
DEFAULT_TIME_TO_INVERSION_S = 20.0

# Ordine deterministico dei profili a parita' di tutto il resto.
_MODE_ORDER = {'level': 0, 'dive': 1, 'loft': 2}
_DRAG_ORDER = {'low': 0, 'high': 1}

# Tolleranza per i confronti di tempo [s] e di quota [m].
_EPS = 1e-9


# ── LIVELLO 1: FISICA ─────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ReleaseWindow:
    """Una finestra di rilascio del registro, normalizzata (quote in m AGL, velocita' in km/h)."""
    drag: str
    modes: Tuple[str, ...]
    min_altitude: float
    max_altitude: float
    min_speed_kmh: float
    max_speed_kmh: float
    dive_angle: Optional[Tuple[float, float]] = None
    glide_ratio: Optional[float] = None
    standoff_range_km: Optional[Tuple[float, float]] = None

    def admits_altitude(self, altitude_agl: float) -> bool:
        return self.min_altitude - _EPS <= altitude_agl <= self.max_altitude + _EPS

    def admits_speed(self, speed_kmh: float) -> bool:
        return self.min_speed_kmh - _EPS <= speed_kmh <= self.max_speed_kmh + _EPS


@dataclass(frozen=True)
class ReleaseSolution:
    """Soluzione balistica di un rilascio."""
    mode: str
    drag: str
    altitude_agl: float
    speed_kmh: float
    pitch_deg: float
    ground_range_m: float
    slant_range_m: float
    fall_time_s: float


def _weapon_data(weapon: Union[str, Mapping]) -> Optional[Mapping]:
    if isinstance(weapon, Mapping):
        return weapon

    if isinstance(weapon, str):
        return AIR_WEAPONS.get('BOMBS', {}).get(weapon)

    return None


def _window_from(data: Mapping, drag: str, glide_ratio, standoff) -> Optional[ReleaseWindow]:
    try:
        modes = tuple(m for m in data.get('modes', ()) if m in _MODE_ORDER)
        dive = data.get('dive_angle')
        window = ReleaseWindow(drag=drag, modes=modes,
                               min_altitude=float(data['min_altitude']),
                               max_altitude=float(data['max_altitude']),
                               min_speed_kmh=float(data['min_speed']),
                               max_speed_kmh=float(data['max_speed']),
                               dive_angle=(float(dive[0]), float(dive[1])) if dive else None,
                               glide_ratio=float(glide_ratio) if glide_ratio else None,
                               standoff_range_km=(float(standoff[0]), float(standoff[1])) if standoff else None)
    except (KeyError, TypeError, ValueError, IndexError) as exc:
        logger.warning(f"release window not usable ({exc}): {data!r}")
        return None

    return window if window.modes else None


def release_windows(weapon: Union[str, Mapping]) -> Tuple[ReleaseWindow, ...]:
    """Finestre di rilascio di una bomba, in ordine di preferenza (low_drag prima di high_drag).

    Args:
        weapon: nome in `AIR_WEAPONS['BOMBS']` o il dizionario del registro.
    Returns:
        Tupla vuota se l'arma non e' una bomba o non ha il campo `release` (oggi nessuna bomba del registro):
        dato non modellato, nessun vincolo a valle.
    """
    data = _weapon_data(weapon)
    release = data.get('release') if isinstance(data, Mapping) else None

    if not isinstance(release, Mapping):
        return ()

    glide_ratio = release.get('glide_ratio')
    standoff = release.get('standoff_range_km')

    if release.get('drag') == 'selectable':
        windows = [_window_from(release.get(key) or {}, drag, glide_ratio, standoff)
                   for key, drag in (('low_drag', 'low'), ('high_drag', 'high'))]
    else:
        windows = [_window_from(release, release.get('drag', 'low'), glide_ratio, standoff)]

    return tuple(w for w in windows if w is not None)


def fall_time(altitude_agl: float, speed_ms: float = 0.0, pitch_deg: float = 0.0) -> float:
    """Tempo di caduta nel vuoto [s] da `altitude_agl` [m] con velocita' iniziale `speed_ms`
    inclinata di `pitch_deg` (negativo = picchiata, positivo = cabrata)."""
    h = max(0.0, float(altitude_agl))
    v_z = float(speed_ms) * math.sin(math.radians(pitch_deg))
    return (v_z + math.sqrt(v_z * v_z + 2.0 * G_MS2 * h)) / G_MS2


def _solve(window: ReleaseWindow, altitude_agl: float, speed_kmh: float, mode: str,
           pitch_deg: float) -> ReleaseSolution:
    """Balistica (v. docstring del modulo) senza controlli di finestra."""
    h = max(0.0, float(altitude_agl))
    v = float(speed_kmh) * KMH_MS
    factors = DRAG_FACTORS.get(window.drag, DRAG_FACTORS['low'])
    t_vacuum = fall_time(h, v, pitch_deg)
    t = t_vacuum * factors['time']
    ground_range = v * math.cos(math.radians(pitch_deg)) * t_vacuum * factors['range']

    if window.standoff_range_km is not None:
        lo, hi = window.standoff_range_km
        span = window.max_altitude - window.min_altitude
        f = 0.0 if span <= 0 else min(1.0, max(0.0, (h - window.min_altitude) / span))
        ground_range = (lo + (hi - lo) * f) * 1000.0
        t = ground_range / v if v > 0 else t

    elif window.glide_ratio is not None and window.glide_ratio * h > ground_range:
        ground_range = window.glide_ratio * h
        t = ground_range / v if v > 0 else t

    return ReleaseSolution(mode=mode, drag=window.drag, altitude_agl=h, speed_kmh=float(speed_kmh),
                           pitch_deg=float(pitch_deg), ground_range_m=ground_range,
                           slant_range_m=math.hypot(ground_range, h), fall_time_s=t)


def _pitch_of(mode: str, angle_deg: Optional[float]) -> float:
    if mode == 'dive':
        return -abs(float(angle_deg))

    if mode == 'loft':
        return abs(float(angle_deg)) if angle_deg is not None else LOFT_PITCH_DEG

    return 0.0


def release_solution(window: ReleaseWindow, altitude_agl: float, speed_kmh: float, mode: str = 'level',
                     angle_deg: Optional[float] = None) -> Optional[ReleaseSolution]:
    """Soluzione balistica di un rilascio DENTRO la finestra, o None se il rilascio non e' ammesso.

    Args:
        window: finestra di rilascio (v. `release_windows`).
        altitude_agl: quota di rilascio sopra il bersaglio [m].
        speed_kmh: velocita' di rilascio [km/h].
        mode: 'level' | 'dive' | 'loft'.
        angle_deg: angolo di picchiata (obbligatorio per 'dive', dentro `dive_angle`) o di cabrata
            ('loft', default LOFT_PITCH_DEG); ignorato per 'level'.
    Raises:
        ValueError: mode sconosciuto o 'dive' senza angolo (errori di programmazione).
    """
    if mode not in _MODE_ORDER:
        raise ValueError(f"mode must be one of {tuple(_MODE_ORDER)}, got {mode!r}")

    if mode == 'dive' and angle_deg is None:
        raise ValueError("dive release requires angle_deg")

    if mode not in window.modes or not window.admits_altitude(altitude_agl) or not window.admits_speed(speed_kmh):
        return None

    if mode == 'dive':
        if window.dive_angle is None:
            return None

        lo, hi = window.dive_angle

        if not (lo - _EPS <= abs(angle_deg) <= hi + _EPS) or abs(angle_deg) <= 0.0:
            return None

    return _solve(window, altitude_agl, speed_kmh, mode, _pitch_of(mode, angle_deg))


def select_window(windows: Sequence[ReleaseWindow], altitude_agl: float) -> Optional[ReleaseWindow]:
    """La finestra da usare a una quota: la prima (low_drag) che la ammette, altrimenti None
    (decisione utente sul drag selezionabile: low se la quota ci sta, altrimenti high)."""
    for window in windows:
        if window.admits_altitude(altitude_agl):
            return window

    return None


def bomb_engagement_estimate(weapon: Union[str, Mapping], altitude_agl: float,
                             speed_kmh: Optional[float]) -> Optional[ReleaseSolution]:
    """Gittata e caduta di una bomba per il risolutore DES (decisione B6), senza profilo pianificato.

    Rilascio LIVELLATO (picchiata a meta' fascia se la finestra non ammette il livellato). Se quota o
    velocita' sono fuori finestra vengono portate al valore ammesso piu' vicino — lo stesso
    comportamento dell'IA di DCS ("will choose closest altitude", `Controller.md:157`): l'aereo sale
    o scende alla quota di sgancio. Finestra: quella che ammette la quota (low_drag prima), altrimenti
    quella col bordo di quota piu' vicino.

    Args:
        weapon: nome o dizionario del registro.
        altitude_agl: quota del tiratore sopra il bersaglio [m].
        speed_kmh: velocita' d'attacco [km/h]; None -> centro della finestra di velocita'.
    Returns:
        ReleaseSolution, o None se l'arma non ha dati di rilascio (resta il comportamento precedente).
    """
    windows = release_windows(weapon)

    if not windows:
        return None

    h = max(0.0, float(altitude_agl))
    window = select_window(windows, h)

    if window is None:
        window = min(windows, key=lambda w: min(abs(h - w.min_altitude), abs(h - w.max_altitude)))

    h = min(max(h, window.min_altitude), window.max_altitude)
    v = (window.min_speed_kmh + window.max_speed_kmh) / 2.0 if speed_kmh is None else float(speed_kmh)
    v = min(max(v, window.min_speed_kmh), window.max_speed_kmh)

    if 'level' in window.modes:
        return _solve(window, h, v, 'level', 0.0)

    if 'dive' in window.modes and window.dive_angle is not None:
        angle = max(sum(window.dive_angle) / 2.0, 1.0)
        return _solve(window, h, v, 'dive', -angle)

    return _solve(window, h, v, 'loft', LOFT_PITCH_DEG)


# ── LIVELLO 2: PIANIFICAZIONE ─────────────────────────────────────────────────

DetectionSource = Union[Sequence, Callable[[float], Sequence], None]


# Punto leggero per l'intervallo analitico (che legge solo .x/.y/.z come float): evita il costo
# della costruzione di Point3D sympy per ogni tratto di ogni candidato.
_Point = namedtuple('_Point', 'x y z')


def _xyz(point) -> Tuple[float, float, float]:
    return float(point.x), float(point.y), float(point.z)


def _unit(azimuth_deg: float) -> Tuple[float, float]:
    """Versore orizzontale dell'azimut (gradi da nord = +y, senso orario)."""
    rad = math.radians(azimuth_deg)
    return math.sin(rad), math.cos(rad)


def _volume_windows(points: Sequence[Tuple[float, float, float]], speed_ms: float,
                    cylinder) -> List[Tuple[float, float]]:
    """Intervalli di tempo [s dal primo punto] in cui la spezzata e' dentro il cilindro, fusi se contigui."""
    raw: List[Tuple[float, float]] = []
    elapsed = 0.0

    for a, b in zip(points, points[1:]):
        length = math.dist(a, b)
        duration = length / speed_ms if speed_ms > 0 else 0.0
        interval = _segment_cylinder_interval(_Point(*a), _Point(*b), cylinder)

        if interval is not None:
            s_in, s_out = interval
            raw.append((elapsed + s_in * duration, elapsed + s_out * duration))

        elapsed += duration

    merged: List[Tuple[float, float]] = []

    for t_in, t_out in sorted(raw):
        if merged and t_in <= merged[-1][1] + 1e-6:
            merged[-1] = (merged[-1][0], max(merged[-1][1], t_out))
        else:
            merged.append((t_in, t_out))

    return merged


def _evaluate_exposure(points, speed_ms: float, threats: Sequence, detection_threats: Sequence
                       ) -> Tuple[Tuple[ThreatExposure, ...], float, float, Optional[float]]:
    """(esposizioni per minaccia, esposizione pesata, esposizione di rilevamento, primo rilevamento)."""
    contact: Dict[str, Tuple[float, Optional[float]]] = {}   # source_id -> (t_contatto, detected_at)
    detection_exposure = 0.0
    first_detection = None

    for detection in detection_threats:
        windows = _volume_windows(points, speed_ms, detection.cylinder)
        detection_exposure += sum(t_out - t_in for t_in, t_out in windows)

        if windows:
            first_detection = windows[0][0] if first_detection is None else min(first_detection, windows[0][0])
            detected_at = windows[0][0]
            # IP gia' dentro il volume: rilevato prima dell'inizio del tratto d'attacco
            t_contact = -math.inf if detected_at <= _EPS else detected_at
        else:
            detected_at, t_contact = None, math.inf     # volume presente ma mai toccato

        source = getattr(detection, 'source_id', None)

        if source is None:
            continue

        previous = contact.get(source)

        if previous is None or t_contact < previous[0]:
            contact[source] = (t_contact, detected_at)

    exposures = []
    weighted = 0.0

    for threat in threats:
        windows = _volume_windows(points, speed_ms, threat.cylinder)

        if not windows:
            continue

        source = getattr(threat, 'source_id', None)
        t_contact, detected_at = contact.get(source, (-math.inf, None)) if source is not None else (-math.inf, None)
        acquisition = float(getattr(threat, 'acquisition_time', 0.0) or 0.0)
        fire = float(getattr(threat, 'min_fire_time', 0.0) or 0.0)
        seconds = 0.0
        effective = 0.0

        for t_in, t_out in windows:
            seconds += t_out - t_in
            t_launch = max(t_in, t_contact + acquisition) + fire
            effective += max(0.0, t_out - t_launch)

        detected = t_contact != math.inf
        warning = None if detected_at is None else max(0.0, windows[0][0] - detected_at)
        danger = float(getattr(threat, 'danger_level', 0.0) or 0.0)
        exposure = ThreatExposure(threat_id=source, seconds=seconds, effective_seconds=effective,
                                  danger_level=danger, detected_at_s=detected_at,
                                  warning_time_s=warning, detected=detected)
        exposures.append(exposure)
        weighted += exposure.weighted_exposure

    exposures.sort(key=lambda e: (-e.weighted_exposure, str(e.threat_id)))
    return tuple(exposures), weighted, detection_exposure, first_detection


def _bearing_gap(azimuth: float, bearing: Optional[float]) -> float:
    """Scarto angolare [0, 180] fra l'azimut d'ingresso e la direzione della base (0 senza base)."""
    if bearing is None:
        return 0.0

    gap = abs(azimuth - bearing) % 360.0
    return round(min(gap, 360.0 - gap), 6)


def _loadout_record(aircraft_model: str, loadout: str) -> Optional[Mapping]:
    record = (AIRCRAFT_LOADOUTS.get(aircraft_model) or {}).get(loadout)
    return record if isinstance(record, Mapping) else None


def weapon_quantity(aircraft_model: str, loadout: str, weapon: str) -> int:
    """Esemplari di `weapon` sui piloni del loadout (0 se assente)."""
    record = _loadout_record(aircraft_model, loadout) or {}
    pylons = (record.get('stores') or {}).get('pylons') or {}
    total = 0

    for item in pylons.values():
        if isinstance(item, (list, tuple)) and len(item) >= 2 and item[0] == weapon:
            try:
                total += int(item[1])
            except (TypeError, ValueError):
                continue

    return total


def _candidate_altitudes(windows: Sequence[ReleaseWindow], att_min: float, att_max: float,
                         threats: Sequence, target_z: float) -> List[float]:
    """Quote AGL candidate: griglia sulla fascia di ogni finestra + bordi dei volumi d'intercettazione."""
    altitudes = set()

    for window in windows:
        lo, hi = max(att_min, window.min_altitude), min(att_max, window.max_altitude)

        if lo > hi + _EPS:
            continue

        steps = max(2, ALTITUDE_GRID_STEPS)
        altitudes.update(round(lo + (hi - lo) * i / (steps - 1), 3) for i in range(steps))

        for threat in threats:
            for edge in (float(threat.max_altitude) * MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MAX_VALUE,
                         float(threat.min_altitude) * MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MIN_VALUE):
                agl = edge - target_z

                if lo - _EPS <= agl <= hi + _EPS:
                    altitudes.add(round(agl, 3))

    return sorted(altitudes)


def _release_options(window: ReleaseWindow, modes: Optional[Iterable[str]]) -> List[Tuple[str, Optional[float]]]:
    """(profilo, angolo) ammessi da una finestra, filtrati dai profili richiesti."""
    allowed = set(modes) if modes is not None else set(_MODE_ORDER)
    options: List[Tuple[str, Optional[float]]] = []

    for mode in sorted(window.modes, key=_MODE_ORDER.get):
        if mode not in allowed:
            continue

        if mode == 'dive':
            if window.dive_angle is None:
                continue

            lo, hi = window.dive_angle
            options.extend(('dive', angle) for angle in DIVE_ANGLES_DEG if max(lo, _EPS) <= angle <= hi + _EPS)
        elif mode == 'loft':
            options.append(('loft', LOFT_PITCH_DEG))
        else:
            options.append(('level', None))

    return options


def _detections_at(detection_threats: DetectionSource, altitude_abs: float, cache: Dict) -> Sequence:
    if detection_threats is None:
        return ()

    if not callable(detection_threats):
        return detection_threats

    key = round(altitude_abs, 3)

    if key not in cache:
        cache[key] = tuple(t for t in (detection_threats(altitude_abs) or ()) if t is not None)

    return cache[key]


def _terminal_route(points: Sequence[Tuple[float, float, float]], speed_ms: float):
    """DataType.Route canonica IP -> sgancio -> uscita."""
    from Code.Dynamic_War_Manager.Source.Logic import Route_Adapter

    names = ('IP', 'RELEASE', 'EGRESS')
    wps = [SimpleNamespace(point=Point3D(*p), name=n) for p, n in zip(points, names)]
    edges = [SimpleNamespace(wpA=a, wpB=b, speed=speed_ms, danger=0.0, name=f"{a.name}-{b.name}")
             for a, b in zip(wps, wps[1:])]
    return Route_Adapter.to_canonical_route(SimpleNamespace(edges=edges, name='attack'),
                                            name='attack', path_type='air', route_type='air')


def _join_routes(routes: Sequence, name: str):
    """Concatena rotte canoniche (nell'ordine) in un'unica DataType.Route."""
    from Code.Dynamic_War_Manager.Source.Logic import Route_Adapter

    edges = []

    for route in routes:
        for edge in route.edges.values():
            edges.append(SimpleNamespace(wpA=edge.wpA, wpB=edge.wpB, speed=edge.speed,
                                         danger=edge.danger_level, name=edge.name))

    return Route_Adapter.to_canonical_route(SimpleNamespace(edges=edges, name=name),
                                            name=name, path_type='air', route_type='air')


def _transit_routes(record: Mapping, home_point, ip_point, egress_point, threats: Sequence,
                    detection_threats: DetectionSource, options: Optional[Mapping]):
    """(base -> IP, uscita -> base) con RoutePlanner.calcCanonicalRoute; None dove non trovate.

    Parametri di default dal blocco `cruise` del loadout (quota di riferimento e fascia, velocita'
    km/h -> m/s, raggio d'azione a pieno carico km -> m) e da `attack` (velocita' massima); il
    chiamante li sovrascrive con `options` (stessi nomi degli argomenti di `calcRoute`).
    """
    cruise = record.get('cruise') or {}
    attack = record.get('attack') or {}
    radius_km = ((cruise.get('range') or {}).get('fuel_100%')) or 1000.0
    kwargs = {
        'aircraft_altitude_route': float(cruise.get('reference_altitude', ip_point.z)),
        'aircraft_altitude_min': float(cruise.get('altitude_min', 0.0)),
        'aircraft_altitude_max': float(cruise.get('altitude_max', 15_000.0)),
        'aircraft_speed_max': float(attack.get('speed', cruise.get('speed', 800.0))) * KMH_MS,
        'aircraft_speed': float(cruise.get('speed', 800.0)) * KMH_MS,
        'aircraft_range_max': float(radius_km) * 1000.0,
        'aircraft_time_to_inversion': DEFAULT_TIME_TO_INVERSION_S,
        'mode': ThreatMode.AVOID,
    }
    kwargs.update(options or {})

    if 'detection_threats' not in kwargs and detection_threats is not None:
        kwargs['detection_threats'] = list(_detections_at(detection_threats, kwargs['aircraft_altitude_route'], {}))

    kwargs.setdefault('canonical_speed', kwargs['aircraft_speed'])
    routes = []

    for start, end in ((home_point, ip_point), (egress_point, home_point)):
        planner = RoutePlanner(start, end, list(threats))

        try:
            routes.append(planner.calcCanonicalRoute(start, end, list(threats), **dict(kwargs)))
        except Exception as exc:     # il pianificatore di transito non deve far cadere il profilo
            logger.warning(f"_transit_routes: transit {start} -> {end} failed ({exc})")
            routes.append(None)

    return routes[0], routes[1]


def plan_attack_profile(aircraft_model: str, loadout: str, weapon: str, target_point: Point3D,
                        threats: Sequence = (), detection_threats: DetectionSource = None, *,
                        target_id: Optional[str] = None, azimuths_deg: Optional[Iterable[float]] = None,
                        modes: Optional[Iterable[str]] = None, quantity: Optional[int] = None,
                        passes: int = 1, home_point: Optional[Point3D] = None,
                        transit_options: Optional[Mapping] = None) -> AttackProfile:
    """Profilo d'attacco di un aereo con una bomba contro `target_point` (v. docstring del modulo).

    Args:
        aircraft_model, loadout: chiavi di AIRCRAFT_LOADOUTS; l'inviluppo `attack` del loadout vincola
            quota e velocita'.
        weapon: bomba di AIR_WEAPONS['BOMBS'] presente sui piloni del loadout.
        target_point: posizione del bersaglio (la sua z e' la quota del suolo per l'AGL).
        threats: volumi d'INTERCETTAZIONE (ThreatAA), comprese le difese del bersaglio.
        detection_threats: volumi di RILEVAMENTO (DetectionThreat): una sequenza (costruita a una
            quota), oppure una funzione quota_assoluta -> sequenza, per rispettare l'orizzonte radar
            a ogni quota candidata (v. `detection_threats_factory`). None = nessun dato di
            rilevamento: ogni sito e' assunto gia' in traccia.
        target_id: id di dominio del bersaglio, riportato nel profilo.
        azimuths_deg: azimut d'ingresso ammessi (default: AZIMUTH_COUNT equispaziati).
        modes: profili ammessi, sottoinsieme di ('level', 'dive', 'loft') (default: tutti).
        quantity: bombe da sganciare (default: tutte quelle del loadout).
        passes: passaggi sul bersaglio (-> attackQty DCS).
        home_point: base di partenza/rientro; se dato, si pianificano anche i transiti.
        transit_options: argomenti di `RoutePlanner.calcRoute` che sovrascrivono i default.
    Returns:
        AttackProfile; `feasible=False` con `reason` se loadout, arma o inviluppi non lo consentono.
    Raises:
        TypeError: target_point non Point3D (errore di programmazione).
    """
    if not isinstance(target_point, Point3D):
        raise TypeError(f"target_point must be a Point3D, got {type(target_point).__name__}")

    def infeasible(reason: str) -> AttackProfile:
        logger.debug(f"plan_attack_profile: {aircraft_model!r}/{loadout!r} with {weapon!r}: {reason}")
        return AttackProfile(target_id=target_id, target_point=target_point, weapon=weapon,
                             feasible=False, reason=reason)

    record = _loadout_record(aircraft_model, loadout)

    if record is None:
        return infeasible(f"loadout {loadout!r} not found for {aircraft_model!r}")

    carried = weapon_quantity(aircraft_model, loadout, weapon)

    if carried <= 0:
        return infeasible(f"weapon {weapon!r} not carried by loadout {loadout!r}")

    if weapon not in AIR_WEAPONS.get('BOMBS', {}):
        return infeasible(f"weapon {weapon!r} is not a bomb: attack profile planning covers bombs only")

    windows = release_windows(weapon)

    if not windows:
        return infeasible(f"weapon {weapon!r} has no release data")

    attack = record.get('attack') or {}

    try:
        att_speed = float(attack['speed'])
        att_min = float(attack.get('altitude_min', 0.0))
        att_max = float(attack['altitude_max'])
    except (KeyError, TypeError, ValueError):
        return infeasible(f"loadout {loadout!r} has no usable 'attack' envelope")

    tx, ty, tz = _xyz(target_point)
    threats = [t for t in (threats or ()) if t is not None]
    azimuths = sorted({float(a) % 360.0 for a in azimuths_deg}) if azimuths_deg is not None \
        else [360.0 * i / AZIMUTH_COUNT for i in range(AZIMUTH_COUNT)]

    if not azimuths:
        return infeasible("no attack azimuth allowed")

    home_bearing = None

    if home_point is not None and (float(home_point.x) != tx or float(home_point.y) != ty):
        home_bearing = math.degrees(math.atan2(float(home_point.x) - tx, float(home_point.y) - ty)) % 360.0

    altitudes = _candidate_altitudes(windows, att_min, att_max, threats, tz)
    detection_cache: Dict = {}
    best = None
    best_key = None
    evaluated = 0
    reasons = []

    for altitude in altitudes:
        window = select_window(windows, altitude)

        if window is None:
            continue

        speed_kmh = min(att_speed, window.max_speed_kmh)

        if speed_kmh < window.min_speed_kmh - _EPS:
            reasons.append(f"{window.drag}-drag window needs >= {window.min_speed_kmh:.0f} km/h, "
                           f"loadout attack speed {att_speed:.0f} km/h")
            continue

        speed_ms = speed_kmh * KMH_MS
        altitude_abs = tz + altitude
        detections = _detections_at(detection_threats, altitude_abs, detection_cache)

        for mode, angle in _release_options(window, modes):
            solution = release_solution(window, altitude, speed_kmh, mode, angle)

            if solution is None:
                continue

            for azimuth in azimuths:
                ux, uy = _unit(azimuth)
                ex, ey = _unit(azimuth + EGRESS_TURN_DEG)
                rng = solution.ground_range_m
                release = (tx + ux * rng, ty + uy * rng, altitude_abs)
                ip = (release[0] + ux * IP_RUN_IN_DISTANCE_M, release[1] + uy * IP_RUN_IN_DISTANCE_M, altitude_abs)
                egress = (release[0] + ex * EGRESS_DISTANCE_M, release[1] + ey * EGRESS_DISTANCE_M, altitude_abs)
                points = (ip, release, egress)
                exposures, weighted, det_exposure, first_det = _evaluate_exposure(points, speed_ms, threats,
                                                                                  detections)
                evaluated += 1
                key = (round(weighted, 6), round(altitude, 3), _bearing_gap(azimuth, home_bearing), azimuth,
                       _MODE_ORDER[mode], abs(solution.pitch_deg), _DRAG_ORDER.get(window.drag, 9))

                if best_key is None or key < best_key:
                    best_key = key
                    best = (azimuth, points, solution, exposures, weighted, det_exposure, first_det, speed_ms)

    if best is None:
        detail = f": {reasons[0]}" if reasons else ""
        return infeasible(f"no common window between loadout 'attack' envelope "
                          f"({att_min:.0f}-{att_max:.0f} m, {att_speed:.0f} km/h) and {weapon!r} release data{detail}")

    azimuth, points, solution, exposures, weighted, det_exposure, first_det, speed_ms = best
    ip, release, egress = (Point3D(*p) for p in points)
    attack_route = _terminal_route(points, speed_ms)
    full_route = None
    note = None

    if home_point is not None and attack_route is not None:
        ingress_route, egress_route = _transit_routes(record, home_point, ip, egress, threats,
                                                      detection_threats, transit_options)

        if ingress_route is not None and egress_route is not None:
            full_route = _join_routes((ingress_route, attack_route, egress_route), 'attack_mission')
        else:
            note = "transit route not found: full_route not built"

    return AttackProfile(target_id=target_id, target_point=target_point, weapon=weapon, feasible=True,
                         reason=note, quantity=min(carried, quantity) if quantity is not None else carried,
                         passes=int(passes), run_in_azimuth_deg=azimuth, ip_point=ip,
                         release_point=release, egress_point=egress,
                         release_altitude_m=solution.altitude_agl, release_speed_kmh=solution.speed_kmh,
                         release_mode=solution.mode, release_pitch_deg=solution.pitch_deg, drag=solution.drag,
                         release_ground_range_m=solution.ground_range_m,
                         release_slant_range_m=solution.slant_range_m, fall_time_s=solution.fall_time_s,
                         exposure=exposures, weighted_exposure=weighted, detection_exposure_s=det_exposure,
                         first_detection_s=first_det, attack_route=attack_route, full_route=full_route,
                         candidates_evaluated=evaluated)


def detection_threats_factory(assets: Iterable) -> Callable[[float], Tuple]:
    """Funzione quota_assoluta -> DetectionThreat degli `assets`, per `plan_attack_profile`.

    Costruisce i volumi di rilevamento alla quota di ogni candidato (il raggio dipende
    dall'orizzonte radar, v. `Air_Route_Manager.build_detection_threat`).
    """
    from Code.Dynamic_War_Manager.Source.Logic.Air_Route_Manager import build_detection_threat

    assets = tuple(assets)

    def factory(altitude_abs: float) -> Tuple:
        return tuple(t for t in (build_detection_threat(a, altitude_abs) for a in assets) if t is not None)

    return factory
