"""
MODULE Attack_Types

Tipi dato del profilo d'attacco (Proposta B, `Analysis/Document/Proposta_Munizioni_Compatibili_e_Rotte_Attacco.md`
§2.4, con la B3 riformulata dalla D-8 di `Proposta_Volumi_Rilevamento_Intercettazione.md` §4).

`AttackProfile` e' cio' che `Logic/Weapon_Delivery.plan_attack_profile` produce e che due esecutori
consumano allo stesso modo (vincolo simulator-agnostic):
  * il motore DES: rotta canonica, quota e velocita' di sgancio, gittata obliqua e tempo di caduta;
  * il futuro adapter DCS: quota (`altitude`), azimut d'ingresso (`direction`), arma (`weaponType`),
    quantita' (`expend`/`attackQty`) dei task AttackGroup/Bombing. Il punto di sgancio esatto in
    DCS lo calcola l'IA: il core fornisce il profilo, validato contro la finestra di rilascio
    dell'arma (DCS altrimenti cambia la quota in silenzio, `Controller.md:157`).

Il profilo e' un attributo della futura `Mission` (P1 di `Analisi_Modello_Missione_Sessione.md`, non
ancora costruita), non della rotta: `DataType.Waypoint` non ha ruolo ne' azione.

Stile di `Command/Command_Types.py`: dataclass immutabili, nessuna logica di calcolo.
Dipendenze: solo sympy e `DataType.Route`; nessun modulo di `Logic` importato, quindi
`Logic/Weapon_Delivery` puo' importare questo file senza cicli.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from sympy import Point3D

from Code.Dynamic_War_Manager.Source.DataType.Route import Route


@dataclass(frozen=True)
class ThreatExposure:
    """Esposizione del tratto d'attacco a UNA minaccia d'intercettazione (ThreatAA).

    Attributes:
        threat_id: `source_id` della minaccia (id dell'asset), None se la minaccia non lo porta.
        seconds: tempo totale dentro il volume d'intercettazione [s].
        effective_seconds: tempo dentro il volume DOPO il primo lancio possibile [s] (B3/D-8):
            t_lancio = max(t_ingresso V_I, t_contatto V_R + acquisition_time) + min_fire_time,
            effective = max(0, t_uscita V_I - t_lancio), sommato sulle finestre.
        danger_level: `danger_level` della minaccia, in [0, 1].
        detected_at_s: istante del primo ingresso nel volume di RILEVAMENTO dello stesso sito, dal
            punto iniziale d'attacco (IP) [s]; None se non valutabile (nessun volume di rilevamento
            associato: il sito e' assunto gia' in traccia, caso conservativo) o se mai rilevato
            (allora `effective_seconds` = 0).
        warning_time_s: preavviso al difensore, dal rilevamento all'ingresso nel volume d'arma [s]
            (0 se rilevato gia' dentro); None quando `detected_at_s` e' None.
        detected: False solo se il volume di rilevamento associato esiste e non viene mai toccato.
    """
    threat_id: Optional[str]
    seconds: float
    effective_seconds: float
    danger_level: float
    detected_at_s: Optional[float] = None
    warning_time_s: Optional[float] = None
    detected: bool = True

    @property
    def weighted_exposure(self) -> float:
        """effective_seconds x danger_level: il termine della metrica di scelta del profilo."""
        return self.effective_seconds * self.danger_level


@dataclass(frozen=True)
class AttackProfile:
    """Profilo d'attacco di un aereo contro un bersaglio con un'arma a caduta.

    Geometria (quote assolute, come le posizioni degli asset; AGL = quota - target_point.z):
        ip_point -> release_point (tratto d'ingresso rettilineo a quota costante) ->
        egress_point (disimpegno). `run_in_azimuth_deg` e' la direzione DAL bersaglio VERSO
        l'attaccante, gradi da nord (+y) in senso orario: l'aereo vola con prua opposta.

    Rotte canoniche (`DataType.Route`, ciò che il DES consuma):
        attack_route: IP -> sgancio -> uscita, sempre presente se `feasible`;
        full_route: base -> IP + attack_route + uscita -> base, solo se il pianificatore ha
        ricevuto il punto base e ha trovato le rotte di transito; altrimenti None.

    Con `feasible=False` il profilo porta solo arma, bersaglio e motivo (`reason`): nessuna finestra
    comune fra inviluppo d'attacco del loadout e finestra di rilascio dell'arma. Le minacce non
    rendono MAI un profilo non fattibile (decisione utente: la minaccia non evitabile vicino al
    bersaglio si accetta); decidono solo quale profilo scegliere.
    """
    target_id: Optional[str]
    target_point: Point3D
    weapon: str
    feasible: bool
    reason: Optional[str] = None
    quantity: int = 0
    passes: int = 1
    run_in_azimuth_deg: Optional[float] = None
    ip_point: Optional[Point3D] = None
    release_point: Optional[Point3D] = None
    egress_point: Optional[Point3D] = None
    release_altitude_m: Optional[float] = None       # AGL, sopra il bersaglio
    release_speed_kmh: Optional[float] = None
    release_mode: Optional[str] = None               # 'level' | 'dive' | 'loft'
    release_pitch_deg: Optional[float] = None        # < 0 picchiata, > 0 cabrata, 0 livellato
    drag: Optional[str] = None                       # 'low' | 'high': finestra di rilascio usata
    release_ground_range_m: Optional[float] = None
    release_slant_range_m: Optional[float] = None    # -> DES: max_range della ShotSpec
    fall_time_s: Optional[float] = None              # -> DES: time_of_flight della ShotSpec
    exposure: Tuple[ThreatExposure, ...] = ()
    weighted_exposure: float = 0.0                   # somma di ThreatExposure.weighted_exposure
    detection_exposure_s: float = 0.0                # tempo nei volumi di rilevamento (somma sui siti)
    first_detection_s: Optional[float] = None        # primo rilevamento dall'IP, None se mai/non valutato
    attack_route: Optional[Route] = None
    full_route: Optional[Route] = None
    candidates_evaluated: int = 0
