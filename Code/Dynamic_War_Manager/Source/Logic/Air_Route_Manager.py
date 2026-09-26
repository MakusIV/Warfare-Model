import sys
import os
from heapq import heappop, heappush
import math
import copy
from numpy import arange
from sympy import Point3D, Point2D, Segment3D, Line3D, Line2D, Circle
from sympy.geometry import intersection
from collections import defaultdict
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from functools import singledispatch
from enum import Enum
from Code.Dynamic_War_Manager.Source.Utility.Utility import rotate_vector, get_direction_vector, getFormattedPoint
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.DataType.Cylinder import Cylinder
from Code.Dynamic_War_Manager.Source.Context.Context import GROUND_WEAPON_TASK, Ground_Vehicle_Asset_Type

logger = Logger(module_name = __name__, class_name = 'Air_Route_Manager').logger


#NOTA: QUESTI PARAMETRI INFLUENZANO I RISULTATI DI RICERCA - CONSIGLIO: MANTENERE BASSO IL NUMERO DI RICORRENZE (MAX_RECURSION) E ALZARE IL NUMERO DI PATH (MAX_PATHS) PER OTTENERE UNA RICERCA VELOCE E CHE CONSIDERI I PERCORSI PIU' CORTI
# SE SI VUOLE UNA RICERCA PIÙ RAPIDA MA MENO CAPACE DI TROVARE IL PERCORSO OTTIMO -> DIMINUIRE SU MAX_PATH
# SI SCONSIGLIA DI AUMENTARE MAX_RECURSION OLTRE 10: LA RICERCA DIVENTA MOLTO ONEROSA E NON NECESSARIAMENTE CAPACE DI TROVARE PERCORSI MIGLIORI: LE RICORSIONI SONO EFFETTUATE PER OGNI SINGLO PATH DI RICERCA
MAX_PATHS = 50      # 50 path per una singola ricerca
MAX_COMPLETED = 10  # 10 path completati per ogni singolo percorso per interrompere la ricerca
MAX_RECURSION = 10  # 10 ricorsione per ogni path dedicato ad una ricerca
MAX_EDGES = 30      # 30
MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MAX_VALUE = 1.05 # factor to increment upper limits for altitude route path
MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MIN_VALUE = 0.95 # factor to decrement lower limits for altitude route path
RADIUS_EXTENSION_THREAT_CIRCONFERENCE = 1.03 # factor to increments radius threat circonference for route path calculus
MIN_SECURE_LENGTH_EDGE = 0.1 # max length of edge in threat zone (per velocizzare il calcolo: tutti i segmenti )
MIN_DISTANCE_TO_CHANGE_ALTITUDE = 1 # min distance from threat to change altitude
TOLERANCE_FOR_INTERSECTION_CALCULUS = 0.1 # minimum length of segment to consider it as valid intersection ATT questa è necessaria per distinguere un segmento da un punto 


class ThreatMode(Enum):
    """Modalita' di trattamento delle minacce del pianificatore di rotta (decisione D-2, 2026-09-26).

    AVOID                aggira i volumi d'INTERCETTAZIONE (ThreatAA): il comportamento storico di
                         calcRoute con intersecate_threat=False;
    CROSS_UNINTERCEPTED  attraversa i volumi d'intercettazione con la corda di sicurezza
                         (calcMaxLenghtCrossSegmentInterception): intersecate_threat=True;
    AVOID_DETECTION      aggira i volumi di RILEVAMENTO (DetectionThreat) e attraversa con la stessa
                         corda limitata di CROSS_UNINTERCEPTED ogni tratto che ricada comunque in un
                         volume d'intercettazione. Non si assume che evitare il rilevamento eviti
                         l'intercettazione: per i SAM tipici (sensore e lanciatore co-locati,
                         scoperta > arma) i volumi sono annidati, ma a bassa quota l'orizzonte radar
                         puo' rendere il volume di rilevamento PIU' PICCOLO di quello d'intercettazione
                         (v. radar_horizon_range), e il controllo si fa sempre sui volumi dichiarati.

    Le combinazioni ("evita il rilevamento dove puoi, altrimenti attraversa senza essere intercettato")
    restano una strategia del chiamante: piu' chiamate a calcRoute e confronto dei risultati.
    """
    AVOID = 'avoid'
    CROSS_UNINTERCEPTED = 'cross_unintercepted'
    AVOID_DETECTION = 'avoid_detection'


def resolve_threat_mode(mode=None, intersecate_threat: bool = False) -> 'ThreatMode':
    """Modalita' effettiva: `mode` prevale; se None si usa l'alias storico `intersecate_threat`.

    Accetta un membro di ThreatMode o il suo valore stringa ('avoid', ...).

    Raises:
        ValueError: mode non riconosciuta (errore di programmazione).
    """
    if mode is None:
        return ThreatMode.CROSS_UNINTERCEPTED if intersecate_threat else ThreatMode.AVOID

    if isinstance(mode, ThreatMode):
        return mode

    return ThreatMode(mode)


class AirThreat:
    """Base comune dei volumi di minaccia aerea usati dal pianificatore di rotta.

    E' cio' che la ricerca del percorso usa di una minaccia: un volume con innerPoint/edgeIntersect,
    una fascia di quota e un danger_level. Due specializzazioni con parametri disgiunti:
    ThreatAA (INTERCETTAZIONE: velocita' dell'intercettore, sequenza di lancio) e DetectionThreat
    (RILEVAMENTO: sensore, portata nominale, quota di riferimento). V. la proposta
    `Analysis/Document/Proposta_Volumi_Rilevamento_Intercettazione.md` §2.3.

    `volume` e' oggi sempre un Cylinder; `cylinder` ne resta l'alias finche' esiste solo quella forma
    (Contact_Scheduler._cylinder_of e l'algoritmo di aggiramento lo leggono). Con l'Attivita' D
    `volume` diventera' l'interfaccia volume generica.

    `source_id` e' l'id dell'asset che genera la minaccia: lega il volume di rilevamento e quello
    d'intercettazione dello stesso sito (None per le minacce scritte a mano).
    """

    def __init__(self, danger_level, cylinder: Cylinder, source_id: Optional[str] = None):
        self.danger_level = danger_level
        self.volume = cylinder                                                  # geometric volume object of threat
        self.min_altitude = cylinder.bottom_center.z                            # minimum altitude of the threat
        self.max_altitude = cylinder.bottom_center.z + cylinder.height          # maximum altitude of the threat
        self.source_id = source_id                                              # id of the asset generating the threat

    @property
    def cylinder(self) -> Cylinder:
        """Alias di `volume` finche' l'unica forma e' il Cylinder."""
        return self.volume

    @cylinder.setter
    def cylinder(self, value: Cylinder):
        self.volume = value

    def edgeIntersect(self, edge) -> Tuple[bool, Optional[Segment3D]]:
        
        """_Check if the edge intersects with the threat cylinder. Returns the intersection segment if it does. 

        Returns:
            tuple: _bool, Segment3D/None:
              - True, Segment3D se il segmento interseca il cilindro in due punti posti sulla superfice laterale del cilindro, Segment3D definito dai punti di intersezione;
              - False, Segment3D se il segmento interseca il cilindro in due punti ed uno dei punti è su una delle superfici orizzontali del cilindro (top/down);
              - False, Segment3D se il segmento interseca il cilindro in un solo punto e uno degli estremi dell'edge è interno;
              - False, None se il segmento non interseca il cilindro;


        """

        segment = Segment3D(edge.wpA.point, edge.wpB.point)        
        return self.cylinder.getIntersection(segment, tolerance = TOLERANCE_FOR_INTERSECTION_CALCULUS)
    
    def innerPoint(self, point:Point3D):
        """ Check if the point is inside the threat cylinder. Returns True if it is."""            
        if self.cylinder.innerPoint(point):
            return True
        return False


class ThreatAA(AirThreat):
    """Minaccia d'INTERCETTAZIONE: il volume in cui l'arma di difesa aerea puo' ingaggiare.

    La classe storica del pianificatore, stesso costruttore posizionale
    (danger_level, interception_speed, min_fire_time, acquisition_time, cylinder).

    `acquisition_time` (rinominato da `min_detection_time`, decisione D-6) e' la LATENZA di
    acquisizione — dall'istante del contatto alla traccia utile al tiro — non un tempo di
    rilevamento ne' un volume: viene da `acquire_time` della tabella minacce SAM ed e' il RIV del
    profilo di reazione del DES (Context/Reaction_Profile). `min_detection_time` resta accettato
    come parola chiave del costruttore e come attributo alias, per compatibilita'.
    """

    def __init__(self, danger_level, interception_speed: float, min_fire_time: float,
                 acquisition_time: Optional[float] = None, cylinder: Optional[Cylinder] = None,
                 source_id: Optional[str] = None, min_detection_time: Optional[float] = None):

        if cylinder is None:
            raise TypeError("ThreatAA requires a cylinder")

        if acquisition_time is None:
            acquisition_time = min_detection_time               # alias storico (D-6)

        elif min_detection_time is not None and min_detection_time != acquisition_time:
            raise TypeError("ThreatAA: acquisition_time and its alias min_detection_time disagree")

        if acquisition_time is None:
            raise TypeError("ThreatAA requires acquisition_time (alias: min_detection_time)")

        super().__init__(danger_level, cylinder, source_id=source_id)
        self.interception_speed = interception_speed                            # speed of the interception object in m/s
        self.min_fire_time = min_fire_time                                      # minimum time to fire an interception object in seconds
        self.acquisition_time = acquisition_time                                # latency from contact to a fire-control track, in seconds

    @property
    def min_detection_time(self) -> float:
        """Alias storico di `acquisition_time` (decisione D-6)."""
        return self.acquisition_time

    @min_detection_time.setter
    def min_detection_time(self, value: float):
        self.acquisition_time = value

    def calcMaxLenghtCrossSegmentInterception(self, aircraft_speed: float, aircraft_altitude: float,
                                              time_to_inversion: float, ready_delay_s: float = 0.0) -> float:
        """ Calculate the maximum length of the segment that can be crossed in the interception zone before interception. Returns the length in meters.

        Modella specificamente il volume di INTERCETTAZIONE di ThreatAA (portata/velocita' dell'arma):
        e' il caso "attraversamento senza essere intercettati" (ThreatMode.CROSS_UNINTERCEPTED, e i
        tratti d'intercettazione di ThreatMode.AVOID_DETECTION). Il volume di rilevamento distinto
        (DetectionThreat) entra solo nell'istante in cui il sito e' pronto a lanciare, tramite
        `ready_delay_s` (v. sotto). Nome precedente: calcMaxLenghtCrossSegment (alias mantenuto, D-6).

        Modello fisico (tutte le grandezze in m, s, m/s):
          - l'aereo entra nel volume sulla superficie laterale (distanza orizzontale R dal sito) e vola
            RADIALMENTE verso il sito a velocita' v_a, quota relativa h = aircraft_altitude - quota base del
            cilindro: e' il caso peggiore per chi attraversa (velocita' di avvicinamento massima, quindi
            intercettazione piu' precoce), per cui la lunghezza ottenuta e' conservativa per qualsiasi corda;
          - il sito e' pronto a lanciare `ready_delay_s` (t_r) dopo l'ingresso, e l'intercettore parte
            dopo la sequenza di lancio min_fire_time (t_f), poi vola in linea retta a v_i;
          - lm = distanza percorsa dall'intercettore fino all'intercettazione. In quell'istante l'aereo e'
            a distanza orizzontale x0 - k*lm, con x0 = R - v_a*(t_r + t_f) (posizione al lancio) e
            k = v_a/v_i, e la distanza obliqua deve eguagliare lm:  lm^2 = (x0 - k*lm)^2 + h^2, cioe'
                (1 - k^2)*lm^2 + 2*k*x0*lm - (x0^2 + h^2) = 0      [tutti i termini in m^2]
          - tempo di intercettazione dall'ingresso: t* = t_r + t_f + lm/v_i. L'aereo deve essere fuori
            prima di t* e gli serve time_to_inversion per la manovra d'uscita, che consuma il tempo
            disponibile:  L_max = v_a * (t* - time_to_inversion), saturato a 0.
        Se l'intercettore non puo' raggiungere l'aereo (nessuna radice positiva) restituisce float('inf'):
        qualsiasi attraversamento e' sicuro.

        Ipotesi con ready_delay_s = 0 (default, e l'unico valore che il pianificatore usa oggi): il sito
        e' GIA' PRONTO all'ingresso nel volume d'intercettazione, cioe' ha acquisito l'aereo prima (con il
        proprio sensore o via rete) da almeno acquisition_time. E' conservativo per chi attacca. Non e'
        sempre vero: a bassa quota l'orizzonte radar puo' nascondere l'aereo fino a dentro il volume
        d'arma, e allora il ritardo reale e' max(0, t_contatto + acquisition_time - t_ingresso) (v.
        proposta §3.4, secondo passo non ancora implementato).
        """
        if aircraft_speed <= 0:
            return 0

        v_a = aircraft_speed
        v_i = self.interception_speed
        k = v_a / v_i
        ready_delay_s = max(0.0, float(ready_delay_s))
        # quota relativa al sito. APPROSSIMAZIONE: la base del cilindro e' quota del sito + quota minima d'ingaggio
        # (v. Mobile.air_defense_volume), la sola informazione disponibile qui; h risulta sottostimato di quella
        # quota minima, quindi l'intercettazione anticipata: errore conservativo
        h = max(0.0, aircraft_altitude - self.cylinder.bottom_center.z)
        x0 = self.cylinder.radius - v_a * (self.min_fire_time + ready_delay_s)  # distanza orizzontale al lancio

        a = 1 - k**2
        b = 2 * k * x0
        c = -(x0**2 + h**2)

        if abs(a) < 1e-12:  # v_a == v_i: equazione di primo grado
            if b != 0:
                roots = [-c / b]
            else:
                roots = [0.0] if c == 0 else [] # aereo sul sito al lancio: intercettazione immediata
        else:
            delta = b**2 - 4*a*c

            if delta < 0:
                roots = []
            else:
                sqrt_delta = math.sqrt(delta)
                roots = [(-b + sqrt_delta) / (2*a), (-b - sqrt_delta) / (2*a)]

        positive_roots = [r for r in roots if r >= 0]

        if not positive_roots:
            return float('inf')

        lm = min(positive_roots) # prima intercettazione possibile

        time_to_interception = ready_delay_s + self.min_fire_time + lm / v_i
        max_segment_lenght_in_threat_zone = max(0.0, (time_to_interception - time_to_inversion) * v_a)

        return max_segment_lenght_in_threat_zone

    def calcMaxLenghtCrossSegment(self, aircraft_speed: float, aircraft_altitude: float, time_to_inversion: float) -> float:
        """Alias retrocompatibile di calcMaxLenghtCrossSegmentInterception con sito gia' pronto (D-6)."""
        return self.calcMaxLenghtCrossSegmentInterception(aircraft_speed, aircraft_altitude, time_to_inversion)

    def __repr__(self):
            """
            Rappresentazione ufficiale dell'oggetto Block.
            Utile per il debugging.
            """
            return (f"cylinder {self.cylinder!r}, alt:( {self.min_altitude:.2f} - {self.max_altitude:.2f} ), danger: {self.danger_level:.2f}")

    def __str__(self):
        """
        Rappresentazione leggibile dell'oggetto Block.
        Utile per l'utente finale.
        """
        return (f"Threat Information:\n"
                f"  cylinder: {self.cylinder!r}\n"
                f"  min alt: {self.min_altitude:.2f}\n"
                f"  max alt: {self.max_altitude:.2f}\n"
                f"  danger: {self.danger_level:.2f}\n"
                f"  interception_speed: {self.interception_speed:.2f}\n"
                f"  min_fire_time: {self.min_fire_time:.2f}\n"
                f"  acquisition_time: {self.acquisition_time:.2f}")


class DetectionThreat(AirThreat):
    """Minaccia di RILEVAMENTO: il volume in cui un sensore nemico vede un bersaglio aereo.

    Non abbatte nessuno: `danger_level` e' sempre 0.0 (decisione D-3), cosi' total_danger dei
    percorsi e Military.air_defense_power restano, per costruzione, misure della sola potenza di
    fuoco. Il rilevamento si misura con metriche proprie del Path (detection_exposure_s,
    first_detection_time_s, warning_time_s, max_detection_probability).

    Il volume e' un Cylinder costruito ALLA QUOTA DI ROTTA `reference_altitude`: raggio =
    min(acquisition_range, orizzonte radar alla quota del bersaglio) (v. build_air_defense_threats).
    Un volume di rilevamento vero e' un solido di rotazione il cui raggio cresce con la quota; il
    cilindro ne e' la sezione alla sola quota di rotta, per cui il pianificatore non consente cambi
    di quota per aggirarlo (v. _handle_threat_avoidance).

    Params:
        sensor:             sensore che definisce il raggio: 'radar' | 'TVD' ('visual' previsto per
                            i sensori visivi di ripiego, non ancora nei dati: decisione D-4(c)).
        acquisition_range:  portata nominale di scoperta [m], prima dell'orizzonte: e' la R della
                            legge di Pd del DES (Engagement_Resolver.detection_probability).
        reference_altitude: quota [m] alla quale e' stato calcolato il raggio del cilindro.
    """

    def __init__(self, cylinder: Cylinder, sensor: str, acquisition_range: float,
                 reference_altitude: float, source_id: Optional[str] = None):
        super().__init__(0.0, cylinder, source_id=source_id)
        self.sensor = sensor
        self.acquisition_range = float(acquisition_range)
        self.reference_altitude = float(reference_altitude)

    def __repr__(self):
            """
            Rappresentazione ufficiale dell'oggetto DetectionThreat.
            Utile per il debugging.
            """
            return (f"detection {self.sensor}: cylinder {self.cylinder!r}, alt:( {self.min_altitude:.2f} - {self.max_altitude:.2f} ), "
                    f"acquisition_range: {self.acquisition_range:.2f}, reference_altitude: {self.reference_altitude:.2f}")

    def __str__(self):
        """
        Rappresentazione leggibile dell'oggetto DetectionThreat.
        Utile per l'utente finale.
        """
        return (f"Detection Threat Information:\n"
                f"  cylinder: {self.cylinder!r}\n"
                f"  min alt: {self.min_altitude:.2f}\n"
                f"  max alt: {self.max_altitude:.2f}\n"
                f"  sensor: {self.sensor}\n"
                f"  acquisition_range: {self.acquisition_range:.2f}\n"
                f"  reference_altitude: {self.reference_altitude:.2f}\n"
                f"  source_id: {self.source_id!r}")


# ── FABBRICA ThreatAA ─────────────────────────────────────────────────────────
#
# ThreatAA esisteva da sempre ma nessun codice di produzione lo costruiva: le rotte
# aeree si pianificavano solo su minacce scritte a mano nei test. La fabbrica sta qui,
# accanto alla classe che produce e ai suoi consumatori (RoutePlanner), e non come
# metodo di Asset/Mobile, per una ragione di direzione delle dipendenze: ThreatAA e' un
# tipo dello strato Logic (pianificazione di rotta), e Asset non deve dipendere da Logic.
# La geometria — l'unica parte che dipende davvero dai dati dell'asset — resta dov'era:
# Mobile.air_defense_volume() produce il Cylinder e questa fabbrica lo avvolge.
#
# Le tre grandezze non geometriche di ThreatAA si ricavano cosi':
#
#   interception_speed  dai dati d'arma reali (`speed` dei missili SAM, `muzzle_speed`
#                       dei cannoni AA), stessa fonte che air_defense_volume() legge
#                       per range/quote;
#   acquisition_time    da `acquire_time_s` della tabella minacce SAM ricercata
#                       (v. SAM_REACTION_TABLE) quando il modello vi compare;
#   min_fire_time       PLACEHOLDER DETERMINISTICO: non esiste in nessuna fonte dati del
#                       progetto (v. LAUNCH_SEQUENCE_TIME_S).
#
# Convenzione del progetto per i dati che mancano: stima di default dichiarata
# esplicitamente tale, deterministica, mai `random` (v. Logic/Meteo_Analysis.py).

# Velocita' d'intercettazione di ripiego [m/s] quando il modello ha armi AD senza dato di
# velocita'. ThreatAA divide per interception_speed, quindi non puo' mai valere 0.
# ~Mach 1.8: ordine di grandezza di un SAM a corto raggio, il caso piu' frequente.
DEFAULT_INTERCEPTION_SPEED_MS = 600.0

# Tabella minacce SAM ricercata, ingerita il 2026-09-18 in
# Analysis/Document/documentazione_dcs/estratti/sam_threat_table.csv (23 sistemi reali).
# Qui e' trascritta — non letta a runtime — per due motivi: il core non deve leggere file
# di documentazione per funzionare, e la tabella e' una fonte di riferimento stabile, non
# un dato di campagna. Chiave: il modello come compare nei registry del progetto
# (Vehicle_Data._registry); `acquire_time` e `launcher` sono le colonne omonime del CSV.
# I 14 sistemi della tabella senza corrispondenza nei registry sono deliberatamente
# omessi: si aggiungono quando i rispettivi modelli entrano in Vehicle_Data.
SAM_REACTION_TABLE = {
    'S-300PS':          {'nato_name': 'SA-10B Grumble',      'acquire_time': 3.0,  'launcher': 'Quad TEL'},
    '9K37-Buk':         {'nato_name': 'SA-11 Gadfly',        'acquire_time': 21.0, 'launcher': 'Quad Rail Launcher'},
    '2K12-Kub':         {'nato_name': 'SA-6 Gainful',        'acquire_time': 21.0, 'launcher': 'Triple Rack TEL'},
    '9A33-Osa':         {'nato_name': 'SA-8 Gecko',          'acquire_time': 19.0, 'launcher': 'Wheeled Launcher'},
    '9K331-Tor':        {'nato_name': 'SA-15 Gauntlet',      'acquire_time': 9.0,  'launcher': 'Tracked Launcher'},
    '9K35-Strela-10':   {'nato_name': 'SA-13 Gopher',        'acquire_time': 2.5,  'launcher': 'Quad Launcher'},
    'Strela-1-9P31':    {'nato_name': 'SA-9 Gaskin',         'acquire_time': 2.5,  'launcher': 'Wheeled Launcher'},
    '2K22-Tunguska':    {'nato_name': 'SA-19 Grison',        'acquire_time': 4.0,  'launcher': 'Tracked Launcher'},
    'MIM-115-Roland':   {'nato_name': 'MIM-115 Roland ADS',  'acquire_time': 11.0, 'launcher': 'Tracked'},
}

# PLACEHOLDER DETERMINISTICO — sequenza di lancio [s]: dal comando di fuoco all'uscita del
# missile dalla rampa. Il CSV non ha questa colonna e nessun registro d'arma del progetto
# la contiene; la stima e' ordinata sul tipo di lanciatore, che il CSV invece dichiara
# (colonna launcher_type): una rampa singola da brandeggiare e' piu' lenta di un TEL
# verticale, che e' piu' lento di un lanciatore cingolato di difesa di punto, pensato
# proprio per la reattivita'. Da sostituire con dati reali, senza cambiare la forma.
LAUNCH_SEQUENCE_TIME_S = {
    'Single Rail Launcher':  8.0,
    'Quad Rail Launcher':    6.0,
    'Triple Rack TEL':       5.0,
    'Quad TEL':              4.0,
    'Quad Launcher':         3.0,
    'Wheeled Launcher':      3.0,
    'Six Pack':              3.0,
    'Tracked':               3.0,
    'Tracked Launcher':      2.0,
    'Quad Fixed':            2.0,
}
DEFAULT_LAUNCH_SEQUENCE_TIME_S = 5.0

# Un cannone AA non ha sequenza di lancio: una volta puntato spara. Resta il solo
# brandeggio, molto piu' rapido dell'erezione/lancio di un missile.
GUN_LAUNCH_SEQUENCE_TIME_S = 1.0

# PLACEHOLDER DETERMINISTICO — tempo di acquisizione [s] per i modelli che NON compaiono
# nella tabella (MIM-72G-Chaparral, M6-Linebacker, tutte le AAA, tutti i SAM navali: il
# CSV copre solo sistemi SAM terrestri). I valori sono presi dalla distribuzione della
# tabella stessa, per classe: i SAM grandi con radar a scansione elettronica acquisiscono
# in ~3 s (S-300), i medi in 12-21 s (Kub/Buk/Hawk), i piccoli in 2,5-19 s, e l'AAA con
# puntamento ottico/radar semplice e' rapida ma a cortissimo raggio.
# Le navi non hanno voce propria: la loro `category` e' un Sea_Asset_Type (Carrier,
# Destroyer, ...), che non e' una classe di difesa aerea, quindi ricadono sul valore di
# ripiego. Si aggiungeranno quando esistera' una fonte navale equivalente al CSV.
DEFAULT_ACQUIRE_TIME_S = {
    Ground_Vehicle_Asset_Type.SAM_BIG.value:    3.0,
    Ground_Vehicle_Asset_Type.SAM_MEDIUM.value: 16.0,
    Ground_Vehicle_Asset_Type.SAM_SMALL.value:  8.0,
    Ground_Vehicle_Asset_Type.AAA.value:        4.0,
}
DEFAULT_ACQUIRE_TIME_FALLBACK_S = 10.0

# ── danger_level ──────────────────────────────────────────────────────────────
# `danger_level` non aveva scala canonica in nessun punto del codice: i consumatori
# (Route.max/min/avg_danger_level, Ground_Route_Manager, Air_Route_Manager riga ~1090) lo
# usano solo per confronti monotoni "piu' alto = piu' pericoloso". Qui si fissa la scala a
# [0, 1] — la stessa di tutti gli altri punteggi normalizzati del progetto (efficiency,
# combat power, score dei registry) — come combinazione lineare di tre fattori, ciascuno
# saturato a 1:
#   portata     quanto lontano la minaccia impegna, ed e' il fattore che pesa piu' di tutti
#               perche' l'evitamento di rotta e' un problema geometrico: un raggio grande
#               costringe a una deviazione grande;
#   quota       fin dove arriva: una minaccia scavalcabile in quota e' meno pericolosa di
#               una che copre tutto l'inviluppo di volo, a parita' di raggio;
#   reattivita' (1 - latenza/riferimento): a parita' di geometria, il sistema che acquisisce
#               e spara prima e' piu' pericoloso. Pesa meno perche' conta solo se si e' gia'
#               dentro il volume, mentre gli altri due decidono se ci si entra.
DANGER_LEVEL_REFERENCE_RADIUS_M = 100_000.0   # ~ S-300 (5V55R, 75 km) e oltre: cima della scala
DANGER_LEVEL_REFERENCE_CEILING_M = 25_000.0   # quota massima d'impiego dell'aviazione tattica
DANGER_LEVEL_REFERENCE_REACTION_S = 30.0      # latenza oltre la quale la reattivita' e' nulla
DANGER_LEVEL_WEIGHTS = {'reach': 0.5, 'ceiling': 0.3, 'reaction': 0.2}


def threat_danger_level(radius: float, max_altitude: float, reaction_time: float) -> float:
    """Livello di pericolo di una minaccia AA in [0, 1]; monotono crescente.

    Params:
        radius:        raggio d'ingaggio [m]
        max_altitude:  quota massima raggiunta dall'inviluppo [m]
        reaction_time: latenza totale = acquisition_time + min_fire_time [s]

    V. il commento DANGER_LEVEL_* sopra per la scelta dei pesi e dei riferimenti.
    """
    def _saturate(value: float) -> float:
        return min(1.0, max(0.0, float(value)))

    reach = _saturate(radius / DANGER_LEVEL_REFERENCE_RADIUS_M)
    ceiling = _saturate(max_altitude / DANGER_LEVEL_REFERENCE_CEILING_M)
    reaction = 1.0 - _saturate(reaction_time / DANGER_LEVEL_REFERENCE_REACTION_S)

    return (DANGER_LEVEL_WEIGHTS['reach'] * reach
            + DANGER_LEVEL_WEIGHTS['ceiling'] * ceiling
            + DANGER_LEVEL_WEIGHTS['reaction'] * reaction)


def _air_defense_weapons(asset) -> Optional[Dict]:
    """Sintesi delle armi di difesa aerea del modello dell'asset, dai registri d'arma reali.

    Selezione identica a Mobile.air_defense_volume() — stesso discriminante su quote e
    task Anti_Air, stessi tipi d'arma per veicoli (AA_CANNONS/MISSILES) e navi
    (MISSILES_SAM) — perche' le due funzioni devono descrivere lo stesso inviluppo.

    Returns:
        {'interception_speed': float|None, 'has_missiles': bool, 'has_guns': bool}
        oppure None se il modello non e' noto o non ha armi AD.
    """
    from Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data import Vehicle_Data as _VehicleData
    from Code.Dynamic_War_Manager.Source.Asset.Ship_Data import Ship_Data as _ShipData
    from Code.Dynamic_War_Manager.Source.Asset.Ground_Weapon_Data import GROUND_WEAPONS
    from Code.Dynamic_War_Manager.Source.Asset.Ship_Weapon_Data import SHIP_WEAPONS

    model = getattr(asset, '_model', None)

    if model is None:
        logger.warning("_air_defense_weapons: _model not set")
        return None

    data_record = _VehicleData._registry.get(model) or _ShipData._registry.get(model)

    if data_record is None:
        logger.warning(f"_air_defense_weapons: no registry entry for model {model!r}")
        return None

    is_ship = isinstance(data_record, _ShipData)

    speeds = []
    has_missiles = False
    has_guns = False

    for weapon_type, weapon_list in (data_record.weapons or {}).items():
        if is_ship:
            if weapon_type != 'MISSILES_SAM':
                continue
            weapon_db = SHIP_WEAPONS.get('MISSILES_SAM', {})
        else:
            if weapon_type not in ('AA_CANNONS', 'MISSILES'):
                continue
            weapon_db = GROUND_WEAPONS.get(weapon_type, {})

        for weapon_model, _qty in weapon_list:
            wdata = weapon_db.get(weapon_model)

            if ( wdata is None or 'min_altitude' not in wdata or 'max_altitude' not in wdata ) or ( 'task' in wdata and GROUND_WEAPON_TASK['Anti_Air'] not in wdata['task'] ):
                continue

            if float(wdata.get('max_altitude', 0)) <= 0.0:
                continue

            if weapon_type == 'AA_CANNONS':
                has_guns = True
                speed = wdata.get('muzzle_speed')
            else:
                has_missiles = True
                speed = wdata.get('speed')

            if speed is not None and float(speed) > 0.0:
                speeds.append(float(speed))

    if not (has_missiles or has_guns):
        logger.warning(f"_air_defense_weapons: no AD weapons for model {model!r}")
        return None

    # Massimo, non media: l'intercettore piu' veloce e' quello che l'intruso incontra per
    # primo, quindi il caso peggiore per chi pianifica la rotta.
    return {
        'interception_speed': max(speeds) if speeds else None,
        'has_missiles': has_missiles,
        'has_guns': has_guns,
    }


def threat_reaction_times(asset, has_missiles: bool = True) -> Tuple[float, float]:
    """Latenze di reazione (acquisition_time, min_fire_time) in secondi per un asset AD.

    acquisition_time (gia' min_detection_time, rinominato con D-6) viene da `acquire_time_s`
    della tabella minacce SAM ricercata quando il modello vi compare (v. SAM_REACTION_TABLE), altrimenti dalla stima di default per
    classe (DEFAULT_ACQUIRE_TIME_S, placeholder dichiarato). min_fire_time e' sempre una
    stima (LAUNCH_SEQUENCE_TIME_S): il dato non esiste in nessuna fonte del progetto.

    `has_missiles=False` (asset con soli cannoni AA) porta min_fire_time al tempo di
    brandeggio, non a una sequenza di lancio che non avviene.
    """
    model = getattr(asset, '_model', None)
    entry = SAM_REACTION_TABLE.get(model)

    if entry is not None:
        detection_time = float(entry['acquire_time'])
        fire_time = LAUNCH_SEQUENCE_TIME_S.get(entry['launcher'], DEFAULT_LAUNCH_SEQUENCE_TIME_S)
    else:
        category = getattr(asset, 'category', None)
        detection_time = DEFAULT_ACQUIRE_TIME_S.get(category, DEFAULT_ACQUIRE_TIME_FALLBACK_S)
        fire_time = DEFAULT_LAUNCH_SEQUENCE_TIME_S
        logger.debug(f"threat_reaction_times: model {model!r} not in SAM_REACTION_TABLE, "
                     f"using placeholder estimate for category {category!r}")

    if not has_missiles:
        fire_time = GUN_LAUNCH_SEQUENCE_TIME_S

    return detection_time, fire_time


def build_threat_aa(asset) -> Optional[ThreatAA]:
    """Costruisce la ThreatAA di un singolo asset di difesa aerea reale (Vehicle o Ship).

    E' il ponte fra i dati d'asset e la pianificazione di rotta: la geometria arriva da
    Mobile.air_defense_volume(), le armi dai registri d'arma, le latenze dalla tabella
    minacce SAM ricercata (v. il commento della fabbrica sopra per le motivazioni e per
    cio' che e' stima dichiarata).

    Returns:
        ThreatAA, oppure None se l'asset non e' una minaccia AA costruibile — nessuna
        posizione, modello sconosciuto, nessun'arma di difesa aerea. Non solleva mai per
        dati mancanti, come le funzioni d'asset su cui si appoggia.
    """
    if not hasattr(asset, 'air_defense_volume'):
        logger.debug(f"build_threat_aa: {asset!r} has no air_defense_volume()")
        return None

    cylinder = asset.air_defense_volume()

    if cylinder is None:
        # air_defense_volume() ha gia' loggato il perche' (posizione, modello o armi).
        return None

    weapons = _air_defense_weapons(asset)

    if weapons is None:
        return None

    interception_speed = weapons['interception_speed']

    if interception_speed is None:
        logger.warning(f"build_threat_aa: no weapon speed for model "
                       f"{getattr(asset, '_model', None)!r}, using "
                       f"{DEFAULT_INTERCEPTION_SPEED_MS} m/s")
        interception_speed = DEFAULT_INTERCEPTION_SPEED_MS

    acquisition_time, min_fire_time = threat_reaction_times(
        asset, has_missiles=weapons['has_missiles'])

    danger_level = threat_danger_level(
        radius=float(cylinder.radius),
        max_altitude=float(cylinder.bottom_center.z) + float(cylinder.height),
        reaction_time=acquisition_time + min_fire_time)

    return ThreatAA(danger_level=danger_level,
                    interception_speed=interception_speed,
                    min_fire_time=min_fire_time,
                    acquisition_time=acquisition_time,
                    cylinder=cylinder)


# ── FABBRICA DetectionThreat (volumi di rilevamento, 2026-09-26) ──────────────
#
# Il volume di RILEVAMENTO di un asset nasce dai dati sensore gia' presenti nei registri
# (`radar`/`TVD` -> capabilities['air'] -> acquisition_range), esposti da
# Mobile.detection_range('air'): gli stessi che il DES usa per rilevare
# (Contact_Scheduler.mutual_detection_ranges). Il pianificatore di rotta finora leggeva solo
# il volume delle ARMI (Mobile.air_defense_volume), cioe' quello d'intercettazione.
#
# Il raggio e' limitato dall'ORIZZONTE, che produce l'effetto fisico cercato: un aereo in
# quota e' visto a tutta portata, uno a bassissima quota solo da vicino.
#
#   d = sqrt(2*k*R_T*h_antenna) + sqrt(2*k*R_T*h_bersaglio)        [m]
#
# con R_T = raggio terrestre medio (6 371 km) e k = fattore di raggio terrestre equivalente.
# Per il radar k = 4/3 (atmosfera standard, refrazione della troposfera): sqrt(2*k*R_T) =
# 4121,8 m/sqrt(m), cioe' la forma nota d_km ~= 4,12*(sqrt(h_a) + sqrt(h_t)) con h in metri
# [formula standard dell'orizzonte radio/radar, conoscenza generale, non una fonte del
# progetto]. Per i sensori ottici/IR (TVD) si usa k = 1, la sola linea di vista geometrica
# (3,57 km/sqrt(m)): STIMA DICHIARATA, la refrazione ottica reale e' minore di quella radio;
# con le portate TVD dei registri (8-12 km) l'orizzonte conta solo per bersagli radenti.
#
# Il terreno (mascheramento) NON e' modellato: il core non ha un modello del terreno. La
# quota del bersaglio e' misurata rispetto alla quota del sito.
EARTH_RADIUS_M = 6_371_000.0
EFFECTIVE_EARTH_RADIUS_FACTOR = {'radar': 4.0 / 3.0, 'TVD': 1.0}

# ALTEZZA D'ANTENNA/SENSORE [m] sopra il sito. STIME DI PROGETTO DICHIARATE (decisione D-4(a),
# 2026-09-26), per classe di piattaforma, in attesa di un dato di registro: un record puo'
# gia' sovrascriverle con la chiave opzionale `antenna_height` [m] nel dizionario
# `radar`/`TVD` (nessun record la contiene oggi).
#   veicolo  ~5 m: radar su scafo/torretta di un mezzo semovente (SA-6, SA-8, Tunguska, ...);
#   EWR      ~20 m: radar di scoperta su palo o sito predisposto (nessun record EWR oggi);
#   nave     ~30 m: centro dell'intervallo 20-40 m delle antenne d'albero delle unita' navali.
SENSOR_HEIGHT_VEHICLE_M = 5.0
SENSOR_HEIGHT_EWR_M = 20.0
SENSOR_HEIGHT_SHIP_M = 30.0

# Fascia di quota del volume di rilevamento: dal sito fino al tetto di riferimento. STIMA
# DICHIARATA: i registri non hanno la copertura in quota dei sensori (§2.2 della proposta);
# il limite basso lo fa gia' l'orizzonte, quello alto e' il tetto d'impiego dell'aviazione
# tattica usato anche per il danger_level.
DETECTION_VOLUME_CEILING_M = DANGER_LEVEL_REFERENCE_CEILING_M


def radar_horizon_range(antenna_height: float, target_height: float,
                        k_factor: float = EFFECTIVE_EARTH_RADIUS_FACTOR['radar']) -> float:
    """Distanza dell'orizzonte [m] fra un sensore ad altezza `antenna_height` e un bersaglio a
    `target_height` (entrambe in m sopra il sito):

        d = sqrt(2*k*R_T*h_a) + sqrt(2*k*R_T*h_t)

    Con k = 4/3 e' l'orizzonte radar standard (~4,12 km * (sqrt(h_a) + sqrt(h_t)), h in m).
    Altezze negative sono saturate a 0.
    """
    two_k_r = 2.0 * float(k_factor) * EARTH_RADIUS_M
    return (math.sqrt(two_k_r * max(0.0, float(antenna_height)))
            + math.sqrt(two_k_r * max(0.0, float(target_height))))


def _sensor_record(asset):
    """(record di registry, is_ship) del modello dell'asset, oppure (None, False)."""
    from Code.Dynamic_War_Manager.Source.Asset.Vehicle_Data import Vehicle_Data as _VehicleData
    from Code.Dynamic_War_Manager.Source.Asset.Ship_Data import Ship_Data as _ShipData

    model = getattr(asset, '_model', None)

    if model is None:
        return None, False

    record = _VehicleData._registry.get(model)

    if record is not None:
        return record, False

    record = _ShipData._registry.get(model)
    return record, record is not None


def sensor_antenna_height(asset, sensor: str) -> float:
    """Altezza [m] del sensore `sensor` ('radar'/'TVD') dell'asset sopra il sito.

    Precedenza: chiave opzionale `antenna_height` del dizionario sensore nel registro; poi la
    stima per classe (SENSOR_HEIGHT_*: nave, EWR, veicolo). V. il commento SENSOR_HEIGHT_*.
    """
    record, is_ship = _sensor_record(asset)
    sensor_data = getattr(record, sensor, None) if record is not None else None

    if isinstance(sensor_data, dict):
        value = sensor_data.get('antenna_height')

        if isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0:
            return float(value)

    if is_ship:
        return SENSOR_HEIGHT_SHIP_M

    ewr = Ground_Vehicle_Asset_Type.EWR.value

    if ewr in (getattr(asset, 'category', None), getattr(asset, 'asset_type', None),
               getattr(record, 'category', None)):
        return SENSOR_HEIGHT_EWR_M

    return SENSOR_HEIGHT_VEHICLE_M


def build_detection_threat(asset, route_altitude: float) -> Optional[DetectionThreat]:
    """Costruisce la DetectionThreat di un asset (Vehicle o Ship) alla quota di rotta `route_altitude`.

    Per ogni sensore con portata di scoperta aria (`Mobile.detection_range('air', sensor=...)`):
        raggio = min(acquisition_range, orizzonte(altezza sensore, route_altitude - quota sito))
    e si tiene il sensore col raggio EFFETTIVO maggiore (stessa composizione "il sensore che
    arriva piu' lontano" di Mobile.detection_range). Il cilindro va dal sito a
    DETECTION_VOLUME_CEILING_M.

    Non richiede armi: un sensore puro (EWR, livello 1 della proposta §2.6) produce la sua
    DetectionThreat senza codice dedicato.

    Returns:
        DetectionThreat, oppure None se l'asset non ha posizione o nessun `acquisition_range`
        aria utilizzabile — es. ZSU-57-2 e M163-VADS, senza sensori nei registri: rilevamento
        non modellato, nessun vincolo (decisione D-4: i dati mancanti restano da ricercare).
        Non solleva mai per dati mancanti.
    """
    position = getattr(asset, '_position', None)

    if position is None or not hasattr(asset, 'detection_range'):
        logger.debug(f"build_detection_threat: {asset!r} has no position or no detection_range()")
        return None

    site_z = float(position.z)
    target_height = max(0.0, float(route_altitude) - site_z)
    best = None  # (raggio effettivo, sensore, portata nominale)

    for sensor in ('radar', 'TVD'):
        nominal = asset.detection_range('air', sensor=sensor)

        if nominal is None:
            continue

        horizon = radar_horizon_range(sensor_antenna_height(asset, sensor), target_height,
                                      EFFECTIVE_EARTH_RADIUS_FACTOR[sensor])
        radius = min(float(nominal), horizon)

        if best is None or radius > best[0]:
            best = (radius, sensor, float(nominal))

    if best is None or best[0] <= 0.0:
        logger.debug(f"build_detection_threat: no usable air acquisition_range for model "
                     f"{getattr(asset, '_model', None)!r}")
        return None

    radius, sensor, nominal = best
    cylinder = Cylinder(center=Point3D(float(position.x), float(position.y), site_z),
                        radius=radius, height=DETECTION_VOLUME_CEILING_M)
    asset_id = getattr(asset, 'id', None)

    return DetectionThreat(cylinder=cylinder, sensor=sensor, acquisition_range=nominal,
                           reference_altitude=float(route_altitude),
                           source_id=str(asset_id) if asset_id is not None else None)


def build_air_defense_threats(asset, route_altitude: float) -> Tuple[Optional[DetectionThreat], Optional[ThreatAA]]:
    """I due volumi di un asset: (rilevamento, intercettazione), ciascuno eventualmente None.

    Il volume d'intercettazione e' quello di build_threat_aa (che resta invariata per i suoi
    chiamanti), con in piu' `source_id`, lo stesso della DetectionThreat: lega i due volumi
    dello stesso sito. Il volume di rilevamento e' costruito alla quota `route_altitude`
    (v. build_detection_threat).

    LIMITE NOTO: il raggio d'intercettazione resta la portata dell'arma, senza il
    min(arma, engagement_range della guida) della proposta §2.1: con i dati attuali la guida
    e' >= arma ovunque sia dichiarata (verifica E-1 della proposta), quindi il risultato non
    cambierebbe.
    """
    interception = build_threat_aa(asset)
    detection = build_detection_threat(asset, route_altitude)

    if interception is not None:
        asset_id = getattr(asset, 'id', None)
        interception.source_id = str(asset_id) if asset_id is not None else None

    return detection, interception


def _segment_cylinder_interval(p_a: Point3D, p_b: Point3D, cylinder: Cylinder) -> Optional[Tuple[float, float]]:
    """Intervallo [s_in, s_out] di [0, 1] in cui il segmento p_a + s*(p_b - p_a) e' dentro il cilindro.

    Calcolo analitico in float (nessuna geometria sympy): disco orizzontale (equazione di secondo grado
    in s) intersecato con la fascia di quota (vincolo lineare in s). Bordo incluso. None se il segmento
    non entra o vi resta per una lunghezza nulla. Serve alle metriche di rilevamento del Path; la
    ricerca del percorso continua a usare Cylinder.getIntersection.
    """
    ax, ay, az = float(p_a.x), float(p_a.y), float(p_a.z)
    dx, dy, dz = float(p_b.x) - ax, float(p_b.y) - ay, float(p_b.z) - az
    cx, cy = float(cylinder.bottom_center.x), float(cylinder.bottom_center.y)
    z_min = float(cylinder.bottom_center.z)
    z_max = z_min + float(cylinder.height)
    radius = float(cylinder.radius)
    s_lo, s_hi = 0.0, 1.0

    # fascia di quota
    if abs(dz) < 1e-12:
        if az < z_min or az > z_max:
            return None
    else:
        s1, s2 = (z_min - az) / dz, (z_max - az) / dz
        s_lo, s_hi = max(s_lo, min(s1, s2)), min(s_hi, max(s1, s2))

    # disco orizzontale: |(a - c) + s*d|^2 <= r^2
    ex, ey = ax - cx, ay - cy
    qa = dx * dx + dy * dy
    qb = 2.0 * (ex * dx + ey * dy)
    qc = ex * ex + ey * ey - radius * radius

    if qa < 1e-12:
        if qc > 0.0:
            return None
    else:
        delta = qb * qb - 4.0 * qa * qc

        if delta < 0.0:
            return None

        sqrt_delta = math.sqrt(delta)
        s_lo = max(s_lo, (-qb - sqrt_delta) / (2.0 * qa))
        s_hi = min(s_hi, (-qb + sqrt_delta) / (2.0 * qa))

    if s_hi - s_lo <= 1e-12:
        return None

    return s_lo, s_hi


def _min_distance_to_site(p_a: Point3D, p_b: Point3D, s_in: float, s_out: float, site: Point3D) -> float:
    """Distanza 3D minima fra `site` e il tratto del segmento p_a -> p_b con parametro in [s_in, s_out]."""
    ax, ay, az = float(p_a.x), float(p_a.y), float(p_a.z)
    dx, dy, dz = float(p_b.x) - ax, float(p_b.y) - ay, float(p_b.z) - az
    sx, sy, sz = float(site.x), float(site.y), float(site.z)
    length2 = dx * dx + dy * dy + dz * dz
    s = 0.0 if length2 < 1e-12 else ((sx - ax) * dx + (sy - ay) * dy + (sz - az) * dz) / length2
    s = min(max(s, s_in), s_out)
    return math.sqrt((ax + s * dx - sx) ** 2 + (ay + s * dy - sy) ** 2 + (az + s * dz - sz) ** 2)


class Waypoint:
    """Rappresents a waypoint in 3D space."""
    
    def __init__(self, name: str, point: Point3D, id: str|None):
        self.id = id                                # waypoint id    
        self.name = name                            # waypoint name
        self.point = point                          # 3d point
        self.point2d = Point2D(point.x, point.y)    # 2d point

        if not id:
            self.id = name
    
    def to_dict(self) -> Dict:
        """Converte il waypoint in un dizionario per serializzazione."""
        return {
            'name': self.name,
            'point': (self.point.x, self.point.y, self.point.z),
            'id': self.id
        }

    def __lt__(self, other):
        # Implementazione di confronto basata sulle coordinate
        return (self.point.x, self.point.y, self.point.z) < (other.point.x, other.point.y, other.point.z)

    def __eq__(self, other):
        if not isinstance(other, Waypoint):
            return False
        return self.point == other.point

    def __hash__(self):
        return hash((self.point.x, self.point.y, self.point.z))

    def __repr__(self):
        """
        Rappresentazione ufficiale dell'oggetto Block.
        Utile per il debugging.
        """
        return (f"name: {self.name!r}, point: {getFormattedPoint(self.point)}")

    def __str__(self):
        """
        Rappresentazione leggibile dell'oggetto Block.
        Utile per l'utente finale.
        """
        return (f"Air Route Manager - Waypoint info:\n"
                f"  id: {self.id!r}\n"
                f"  name: {self.name!r}\n")                



class Edge:
    """Rappresents a route segment from two waypoints."""
    
    def __init__(self, name: str, order_position: int, wpA: Waypoint, wpB: Waypoint, speed: float):
        self.name = name                                        # name = "P: num path - E: num edge "
        self.order_position = order_position                    # order position of the edge in the path (deprecatd ?)
        self.wpA = wpA                                          # waypoint A of edge
        self.wpB = wpB                                          # waypoint B of edge
        self.speed = speed                                      # speed of the edge (deprecated ?)
        self.length = wpA.point.distance(wpB.point)             # length of the edge
        self.danger = 0                                         # danger of the edge

    def getSegment3D(self):
        """Returns the Segment3D of edge"""
        return Segment3D(self.wpA.point, self.wpB.point)

    def to_dict(self) -> Dict:
        """Converts the edge to a dictionary for serialization."""
        
        return {
            'name': self.name,
            'wpA': self.wpA.to_dict(),
            'wpB': self.wpB.to_dict(),
            'length': self.length,
            'danger': self.danger
        }
    
    def __repr__(self):
            """
            Rappresentazione ufficiale dell'oggetto Block.
            Utile per il debugging.
            """
            return (f"name: {self.name!r}, order position: {self.order_position}, wpA: {self.wpA!r}, wpB: {self.wpB!r}, length: {self.length:.2f}")

    def __str__(self):
        """
        Rappresentazione leggibile dell'oggetto Block.
        Utile per l'utente finale.
        """
        return (f"Air Route Manager - Edge Information:\n"
                f"  name: {self.name!r},\n"
                f"  order position: {self.order_position},\n"
                f"  wpA: {self.wpA!r}\n"
                f"  wpB: {self.wpB!r}\n"
                f"  length: {self.length:.2f}\n"
                f"  speed: {self.speed:.2f}\n"
                f"  danger: {self.danger:.2f}"
                )
    
class Route:
    """Rappresents a route composed of multiple edges."""

    def __init__(self, name, length: float|None, danger: float|None):
        self.name = name                    # name of the route
        self.edges = {}                     # dictionary of edges (key: tuple of waypoints)
        self.length = length                # length of the route
        self.danger = danger                # danger of the route
    
    def add_edge(self, edge: Edge):
        self.edges[(edge.wpA, edge.wpB)] = edge
    
    def getWaypoints(self):
        """Returns the waypoints list of the route (order)."""
        # Calcola self.start come il primo waypoint che non è un punto di arrivo
        all_start_points = {a for a, b in self.edges.keys()}
        all_end_points = {b for a, b in self.edges.keys()}
        self.start = next(iter(all_start_points - all_end_points), None)

        if not self.start:
            raise ValueError("Impossibile determinare il punto di partenza (self.start).")

        path = []
        current = self.start

        while True:
            path.append(current)
            next_edges = [e for (a, b), e in self.edges.items() if a == current]

            if not next_edges:
                break
            current = next_edges[0].wpB

        return path

    
    def getPoints(self):
        """Returns the points list of the route (order)."""
        waypoints = self.getWaypoints()
        points = [wp.point for wp in waypoints]
        return points  

    def getLength(self) -> float:
        """Returns the total length of the route."""
        length = 0
        
        for edge in self.edges:
            length += edge.length

        return length

    def __repr__(self):
            """
            Rappresentazione ufficiale dell'oggetto Block.
            Utile per il debugging.
            """
            return (f"name: {self.name!r}, edges: {len(self.edges)}, length: {self.length:.2f}, danger: {self.danger:.2f}")

    def __str__(self):
        """
        Rappresentazione leggibile dell'oggetto Block.
        Utile per l'utente finale.
        """
        return (f"Air Route Manager - Route Information:\n"
                f"  name: {self.name!r},\n"
                f"  edges ({len(self.edges)}):\n"                  
                f"  length: {self.length:.2f}\n"                
                f"  danger: {self.danger:.2f}"
                )


# ottimizzazione deepseek
@dataclass
class Path:
    """Rappresents a path composed of multiple edges."""
    edges: List['Edge']         # list of edges in the path
    completed: bool = False     # flag to indicate if the path is completed

    def __post_init__(self):
        # metriche di rilevamento (decisione D-3): separate da total_danger, calcolate a ricerca
        # conclusa da compute_detection_metrics. Valori di default = nessun rilevamento.
        self.detection_exposure_s = 0.0         # tempo totale dentro volumi di rilevamento [s]
        self.first_detection_time_s = None      # istante del primo ingresso in un volume di rilevamento [s], None se mai
        self.warning_time_s = 0.0               # preavviso al difensore: da primo rilevamento ad arrivo [s]
        self.max_detection_probability = 0.0    # Pd massima sui tratti rilevati, legge del DES (D-5)
        self.detection_tracts = []              # un dict per tratto dentro un volume di rilevamento
        self._calculate_metrics()
    
    def _calculate_metrics(self):
        """Calcola le metriche aggregate del percorso."""
        self.total_length = sum(edge.length for edge in self.edges)
        self.total_danger = sum(edge.danger for edge in self.edges)
        self.waypoints = self._get_waypoints()
    
    def _get_waypoints(self) -> List[Waypoint]:
        """Restituisce la sequenza ordinata di waypoint del percorso."""
        if not self.edges:
            return []
            
        waypoints = [self.edges[0].wpA]
        for edge in self.edges:
            waypoints.append(edge.wpB)
        return waypoints
    
    def add_edge(self, edge: 'Edge'):
        """Aggiunge un edge al percorso e aggiorna le metriche."""
        self.edges.append(edge)
        self._calculate_metrics()

    def compute_detection_metrics(self, detection_threats: List['DetectionThreat'], speed: float) -> None:
        """Calcola le metriche di rilevamento del percorso contro `detection_threats` (decisione D-3).

        Per ogni edge e ogni volume di rilevamento si calcola il tratto dell'edge dentro il volume
        (intervallo analitico segmento/cilindro, fascia di quota inclusa); i tempi vengono dalle
        lunghezze percorse a velocita' costante `speed`, come per l'intero pianificatore:
          - detection_exposure_s: somma delle durate dei tratti (volumi sovrapposti contano
            ciascuno: e' esposizione a sensore, non tempo di calendario);
          - first_detection_time_s: istante del primo ingresso, dalla partenza; None se mai;
          - warning_time_s: arrivo - first_detection_time_s (0.0 se mai rilevato);
          - max_detection_probability e detection_tracts: per ogni tratto, la Pd con la STESSA
            legge del DES (Engagement_Resolver.detection_probability, nessuna modifica al
            risolutore: e' una metrica di pianificazione che ne replica il calcolo, decisione D-5)
            con d = distanza minima (3D) dal sito lungo il tratto e R = acquisition_range NOMINALE del
            sensore (la R del DES). Fuori dal volume (oltre l'orizzonte) Pd = 0. Nessun ritocco alla
            legge: dove il cilindro di pianificazione e la sfera del DES divergono (tratto dentro il
            cilindro ma a distanza 3D > R, cioe' in quota vicino al bordo) il tempo conta
            nell'esposizione ma la Pd vale 0, come nel DES (divergenza nota, proposta §1.4).

        Sono metriche, non vincoli: servono al chiamante per scegliere fra alternative quando
        l'aggiramento totale del rilevamento non esiste. Non toccano total_danger.
        """
        from Code.Dynamic_War_Manager.Source.Logic.Engagement_Resolver import detection_probability

        self.detection_exposure_s = 0.0
        self.first_detection_time_s = None
        self.warning_time_s = 0.0
        self.max_detection_probability = 0.0
        self.detection_tracts = []

        if not detection_threats or not self.edges or speed is None or speed <= 0:
            return

        speed = float(speed)
        travelled = 0.0

        for edge in self.edges:
            length = float(edge.length)

            for threat in detection_threats:
                interval = _segment_cylinder_interval(edge.wpA.point, edge.wpB.point, threat.cylinder)

                if interval is None:
                    continue

                s_in, s_out = interval
                entry_s = (travelled + s_in * length) / speed
                exit_s = (travelled + s_out * length) / speed
                min_distance = _min_distance_to_site(edge.wpA.point, edge.wpB.point, s_in, s_out,
                                                     threat.cylinder.bottom_center)
                sensor_range = float(getattr(threat, 'acquisition_range', 0.0) or threat.cylinder.radius)
                pd = detection_probability(min_distance, sensor_range)

                self.detection_exposure_s += exit_s - entry_s
                self.max_detection_probability = max(self.max_detection_probability, pd)

                if self.first_detection_time_s is None or entry_s < self.first_detection_time_s:
                    self.first_detection_time_s = entry_s

                self.detection_tracts.append({'source_id': getattr(threat, 'source_id', None),
                                              'edge': edge.name,
                                              'entry_time_s': entry_s,
                                              'exit_time_s': exit_s,
                                              'min_distance': min_distance,
                                              'detection_probability': pd})

            travelled += length

        if self.first_detection_time_s is not None:
            self.warning_time_s = travelled / speed - self.first_detection_time_s

    def detection_metrics(self) -> Dict:
        """Le metriche di rilevamento come dizionario (v. compute_detection_metrics)."""
        return {
            'detection_exposure_s': self.detection_exposure_s,
            'first_detection_time_s': self.first_detection_time_s,
            'warning_time_s': self.warning_time_s,
            'max_detection_probability': self.max_detection_probability,
            'detection_tracts': list(self.detection_tracts),
        }

    def to_dict(self) -> Dict:
        """Converte il percorso in un dizionario per serializzazione."""
        return {
            'edges': [edge.to_dict() for edge in self.edges],
            'total_length': self.total_length,
            'total_danger': self.total_danger,
            'completed': self.completed,
            **self.detection_metrics()
        }
    def to_route(self) -> Route:
        """Converte il percorso in un oggetto Route (con le metriche di rilevamento in `detection_metrics`)."""
        route = Route("Route", self.total_length, self.total_danger)

        for edge in self.edges:
            route.add_edge(edge)

        route.detection_metrics = self.detection_metrics()
        return route

    def __repr__(self):
            """
            Rappresentazione ufficiale dell'oggetto Block.
            Utile per il debugging.
            """
            return (f"( edges: {len(self.edges)}, length: {self.total_length:.2f}, danger: {self.total_danger:.2f},completed: {self.completed} )")

    def __str__(self):
        """
        Rappresentazione leggibile dell'oggetto Block.
        Utile per l'utente finale.
        """
        return (f"Air Route Manager - Path Information:\n"                     
                f"  edges: {len(self.edges)},\n,"
                f"  length: {self.total_length:.2f},\n"                
                f"  danger: {self.total_danger:.2f},\n"
                f"  completed: {self.completed}"
                )



class PathCollection:
    """Collection of paths with utility methods."""
    
    def __init__(self):
        self.paths: List[Path] = []
        self._active_path_indices = set()
        self.completed = 0

    
    def add_path(self, initial_edges: Optional[List['Edge']] = None) -> int:
        """
        Aggiunge un nuovo percorso alla collezione.
        Restituisce l'ID del percorso creato.
        """
        path_id = len(self.paths)
        new_path = Path(initial_edges or [])
        self.paths.append(new_path)
        self._active_path_indices.add(path_id)
        return path_id
    
    def get_path(self, path_id: int) -> Path:
        """Restituisce il percorso con l'ID specificato."""
        if path_id < 0 or path_id >= len(self.paths):
            raise IndexError(f"Invalid path ID: {path_id}")
        return self.paths[path_id]
    
    def mark_path_completed(self, path_id: int):
        """Segna un percorso come completato con successo."""
        if path_id in self._active_path_indices:
            self._active_path_indices.remove(path_id)
            self.paths[path_id].completed = True
            self.completed += 1
    
    def get_active_paths(self) -> List[Path]:
        """Restituisce una lista dei percorsi ancora attivi."""
        return [self.paths[i] for i in sorted(self._active_path_indices)]
    
    @staticmethod
    def best_path_key(mode: Optional['ThreatMode'] = None):
        """Chiave di scelta del percorso migliore per modalita' (decisione D-3).

        AVOID_DETECTION: (detection_exposure_s, total_danger, total_length) — prima il minimo tempo
        sotto sensore, poi il pericolo residuo d'intercettazione, poi la lunghezza.
        Altre modalita' (e None): (total_danger, total_length), la chiave storica.
        """
        if mode is not None and resolve_threat_mode(mode) == ThreatMode.AVOID_DETECTION:
            return lambda p: (p.detection_exposure_s, p.total_danger, p.total_length)

        return lambda p: (p.total_danger, p.total_length)

    def get_best_path(self, max_range: float, mode: Optional['ThreatMode'] = None) -> Optional[Path]:
        """Restituisce il percorso migliore basato su pericolo e lunghezza escludendo i percorsi che superano come lunghezza il max_range.

        La chiave di confronto dipende da `mode` (v. best_path_key): None = chiave storica."""
        if not self.paths:
            return None
            
        # Filtra solo i percorsi completati
        completed_paths = [p for p in self.paths if p.completed]

        # Filtro per lunghezza massima. NON un ciclo for+remove sulla stessa lista: rimuovere un
        # elemento durante l'iterazione fa saltare l'elemento successivo (l'indice dell'iteratore
        # avanza ma la lista si e' accorciata), lasciando in lista percorsi che superano max_range
        # quando due o piu' di essi sono consecutivi (verificato).
        completed_paths = [path for path in completed_paths if path.total_length <= max_range]

        if not completed_paths:
            return None
            
        # Trova il percorso con il miglior compromesso pericolo-lunghezza (o rilevamento, per AVOID_DETECTION)
        return min(completed_paths, key=self.best_path_key(mode))
    
    def to_dict(self) -> Dict:
        """Converte l'intera collezione in un dizionario."""
        return {
            'paths': [path.to_dict() for path in self.paths],
            'active_paths': list(sorted(self._active_path_indices))
        }

    def __repr__(self):
            """
            Rappresentazione ufficiale dell'oggetto Block.
            Utile per il debugging.
            """
            return (f"paths: {len(self.paths)}, active_path_indicies: {self._active_path_indices}")

    def __str__(self):
        """
        Rappresentazione leggibile dell'oggetto Block.
        Utile per l'utente finale.
        """
        return (f"Air Route Manager - Path Information:\n"
                f"  paths: {len(self.paths)},\n"
                f"  active_path_indicies: {self._active_path_indices}\n"                                
                )


class RoutePlanner:
    
    """ Class to calculate the best route avoiding threats with lesser length or best route with lesser danger and path length."""

    def __init__(self, start: Point3D, end: Point3D, threats: List[ThreatAA]):
        self.start = start                      # starting point of the route
        self.end = end                          # ending point of the route
        self.threats = threats                  # list of threats to avoid
        
        
    def calcRoute(self, start: Point3D, end: Point3D, threats_: list[ThreatAA], aircraft_altitude_route: float, aircraft_altitude_min: float, aircraft_altitude_max: float, aircraft_speed_max: float, aircraft_speed: float, aircraft_range_max: float, aircraft_time_to_inversion: float, change_alt_option: str = "no_change", intersecate_threat: bool = False, consider_aircraft_altitude_route: bool = True, mode: Optional[ThreatMode] = None, detection_threats: Optional[List[DetectionThreat]] = None) -> Route:      
        """_summary_

        Args:
            start (Point3D): starting point of the route_
            end (Point3D): _ending point of the route_
            threats_ (list[ThreatAA]): _list of INTERCEPTION threats (weapon volumes)_
            aircraft_altitude_route (float): _aircraft reference altitude for the route_
            aircraft_altitude_min (float): _minimum altitude of the aircraft_
            aircraft_altitude_max (float): _maximum altitude of the aircraft_
            aircraft_speed_max (float): _maximum speed of the aircraft_
            aircraft_speed (float): _aircraft referemce speed_
            aircraft_range_max (float): _aircraft maximum range_
            aircraft_time_to_inversion (float): _aircraft time to inversion manouver to exit from threat volume_
            change_alt_option (str, optional): _flag to authorize change in aircraft altitude to avoid threat. Defaults to "no_change".
            intersecate_threat (bool, optional): _legacy alias of mode: False -> ThreatMode.AVOID, True -> ThreatMode.CROSS_UNINTERCEPTED. Ignored when mode is given. Defaults to False.
            consider_aircraft_altitude_route (bool, optional): _flag to authorize deleting threat with maximum height lesser of aircraft_altitude_route. Defaults to True.
            mode (ThreatMode, optional): _threat handling mode (v. ThreatMode); prevails on intersecate_threat. Defaults to None.
            detection_threats (list[DetectionThreat], optional): _DETECTION volumes, built at aircraft_altitude_route (v. build_detection_threat). Searched only in ThreatMode.AVOID_DETECTION; in every mode they feed the detection metrics of the paths (detection_exposure_s, first_detection_time_s, warning_time_s, max_detection_probability). Defaults to None.

        Returns:
            Route: best route avoiding threats or lesser danger level and path length. Detection metrics
            of the chosen path in route.detection_metrics.
        """
        

        # change_alt_option: str = "no_change", "change_down", "change_up"
        # NOTA: 
        # CONSIDERANDO L'ARCHITETTURA DI QUESTO ALGORITMO CONVIENE CALCOLARE LE ROTTE 
        # ESEGUENDO QUESTA FUNZIONE CONSIDERANDO LA DOPPIA ESECUZIONE CON 
        # change_alt_option = "no_change" E CON change_alt_optiNo = "change_up o down"
        # p.e.: la scelta di cosa eseguire prima eè in base alle caratteristiche della missione:
        # mission low profile (evitare intercettazione): prima esegui calcRoute con l'opzione change_down" e se non trovi un percorso soddisfacente esegui calcRoute con l'altezza cosnisderata e l'opzione "no_change" seconda della convenienza prima esegui 
        
        DEBUG = True

        mode = resolve_threat_mode(mode, intersecate_threat)
                      
        found_path = False
        threats = copy.deepcopy(threats_) # Copia profonda della lista delle minacce per evitare modifiche indesiderate
        detections = copy.deepcopy(detection_threats) if detection_threats else []

        if mode == ThreatMode.AVOID_DETECTION and not detections:
            logger.warning("calcRoute: mode AVOID_DETECTION without detection_threats: only interception volumes are crossed")

        # Inizializzazione
        path_collection = PathCollection()
        initial_path_id = path_collection.add_path()

        # esclusione dal calcolo delle threats che includono l'inizio del percorso (tipicamente la base propria)
        self.excludeThreat(threats, start)
        self.excludeThreat(detections, start)

        # le threats che includono la fine del percorso NON vengono piu' ignorate: se end e' un bersaglio difeso
        # la minaccia sopra di esso e' reale. Per costruzione pero' non e' evitabile (end e' al suo interno):
        # viene tolta dalla ricerca (evitamento/attraversamento), che altrimenti fallirebbe o produrrebbe
        # deviazioni assurde, e il suo danger viene registrato sui tratti che entrano nel suo volume
        # (v. applyTerminalThreatsDanger), cosi' pesa su total_danger e quindi sulla scelta del percorso migliore.
        # Stesso trattamento, per lista, per i volumi di rilevamento: il bersaglio sta quasi sempre dentro un
        # volume di rilevamento, e il suo peso non e' un danger ma il tempo di preavviso (metriche di rilevamento).
        terminal_threats = self.extractTerminalThreats(threats, end)
        terminal_detections = self.extractTerminalThreats(detections, end)

        # volumi di rilevamento per le metriche: tutti tranne quelli che contengono start (stessa esclusione della ricerca)
        metric_detections = detections + terminal_detections

        if consider_aircraft_altitude_route:

            if change_alt_option == "change_down":
                raise Exception("Warning: consider_aricraft altitude == True and change:_alt_option == /'change_down'/ could be dangerous for path calculus")             
            self.excludeThreat(threats, aircraft_altitude_route) # exclude threats with max altitude lesser than aircraft altitude route
            self.excludeThreat(detections, aircraft_altitude_route)

        if mode == ThreatMode.CROSS_UNINTERCEPTED: # the aircraft can cross the threat volume. Path calculus is done with the crossing of the threat volume            
            found_path = self.calcPathWithThreat(
                start, 
                end, 
                end,
                threats,
                n_edge = 0,                
                path_id = initial_path_id,
                path_collection = path_collection,
                aircraft_altitude = aircraft_altitude_route,
                aircraft_altitude_min = aircraft_altitude_min,
                aircraft_altitude_max = aircraft_altitude_max,
                aircraft_speed_max = aircraft_speed_max,
                aircraft_speed = aircraft_speed,
                aircraft_range_max = aircraft_range_max,
                time_to_inversion = aircraft_time_to_inversion,
                change_alt_option = change_alt_option,
                max_recursion = MAX_RECURSION,
                debug = True
            )    

        elif mode == ThreatMode.AVOID_DETECTION:
            # aggiramento dei volumi di RILEVAMENTO (motore di ricerca dell'evitamento, invariato) e
            # attraversamento a corda limitata dei volumi d'INTERCETTAZIONE che la rotta tocca comunque
            # (cross_threats: v. _cross_interception_while_avoiding). Nessun cambio di quota sui volumi di
            # rilevamento: sono costruiti alla sola quota di rotta (v. _handle_threat_avoidance).
            found_path = self.calcPathWithoutThreat(
                start, 
                end, 
                end,
                detections,
                n_edge = 0,            
                path_id = initial_path_id,
                path_collection = path_collection,
                aircraft_altitude_min = aircraft_altitude_min,
                aircraft_altitude_max = aircraft_altitude_max,
                aircraft_speed_max = aircraft_speed_max,
                aircraft_speed = aircraft_speed,
                aircraft_range_max = aircraft_range_max,
                time_to_inversion = aircraft_time_to_inversion,
                change_alt_option = change_alt_option,
                max_recursion = MAX_RECURSION,
                debug = True,
                cross_threats = threats,
                aircraft_altitude = aircraft_altitude_route
            )

        else: 
            found_path = self.calcPathWithoutThreat( # in this case the aircraft can't cross the threat volume. Path calculus is done avoiding threat volume
                start, 
                end, 
                end,
                threats,
                n_edge = 0,            
                path_id = initial_path_id,
                path_collection = path_collection,
                aircraft_altitude_min = aircraft_altitude_min,
                aircraft_altitude_max = aircraft_altitude_max,
                aircraft_speed_max = aircraft_speed_max,
                aircraft_speed = aircraft_speed,
                aircraft_range_max = aircraft_range_max,
                time_to_inversion = aircraft_time_to_inversion,
                change_alt_option = change_alt_option,
                max_recursion = MAX_RECURSION,
                debug = True
            )           

        
        
        if found_path: # if a path is found

            processed_edges = set()

            for _path in path_collection.paths:

                if _path.completed:
                    self.applyTerminalThreatsDanger(_path, terminal_threats, processed_edges)
                    _path.compute_detection_metrics(metric_detections, aircraft_speed)

            for id_path in range(len(path_collection.paths)):
                _path = path_collection.get_path(id_path)                
                print(f"\nFound path --> Path ID: {id_path}, path: {_path!r}")

                for edge in _path.edges:                    
                    print(f"Edge {edge!r}")

            best_path = path_collection.get_best_path(aircraft_range_max, mode)       

            if best_path is None: # tutti i percorsi completati superano aircraft_range_max
                return None

            print(f"\nBest path length: {best_path.total_length:.2f}, danger: {best_path.total_danger:.2f}, detection exposure: {best_path.detection_exposure_s:.2f}")

            for edge in best_path.edges:                
                print(f"Edge {edge!r}")
                
            return best_path.to_route()
        
        return None

   

    def calcCanonicalRoute(self, *args, **kwargs):
        """Come `calcRoute`, ma restituisce una `DataType.Route` invece della Route interna.

        E' la sola uscita pubblica supportata verso il resto del sistema: `Waypoint`, `Edge`,
        `Route`, `Path` e `PathCollection` di questo modulo sono stato di lavoro privato
        dell'algoritmo di ricerca (v. la decisione registrata in `Logic/Route_Adapter.py`) e
        non vanno consumati altrove. Il tipo canonico e' l'unico che porta `positionAtTime` e
        `travelTimeToEdge`, cioe' cio' che serve al Contact_Scheduler (Fase 3).

        Il parametro opzionale `canonical_speed` [m/s] sovrascrive la velocita' degli archi
        (quella interna e' marcata "deprecated" nel modello del pianificatore); gli altri
        argomenti sono quelli di `calcRoute`.

        Import locale al metodo per non creare una dipendenza a tempo di import verso
        Route_Adapter, che resta libero di non conoscere questo modulo.

        Returns:
            DataType.Route, oppure None se nessun percorso e' stato trovato.
        """
        from Code.Dynamic_War_Manager.Source.Logic import Route_Adapter

        canonical_speed = kwargs.pop('canonical_speed', None)
        route = self.calcRoute(*args, **kwargs)

        if route is None:
            return None

        canonical = Route_Adapter.to_canonical_route(route,
                                                     name=getattr(route, 'name', None),
                                                     path_type='air',
                                                     route_type='air',
                                                     speed=canonical_speed)

        # le metriche di rilevamento del percorso scelto non hanno un campo nel tipo canonico:
        # viaggiano come attributo, come sulla Route interna (v. Path.to_route)
        if canonical is not None and hasattr(route, 'detection_metrics'):
            canonical.detection_metrics = route.detection_metrics

        return canonical

    def excludeThreat(self, threats: list[AirThreat], arg) -> bool:
        """Delete threats from the list of threats if match with the arg.

        Vale per entrambi i tipi di volume (ThreatAA d'intercettazione, DetectionThreat di rilevamento).

        Args:
            threats (list[AirThreat]): _List of threats to check_
            arg (_Point3D or float or int_): _Point3D or float or int_ - Point3D to check if inside the threat volume or altitude to check if inside the threat volume
        

        Returns:
            bool: _True if threats was deleted, False otherwise_
        """        
        # Controlla che gli elementi della lista siano minacce aeree (ThreatAA o DetectionThreat)
        if not all(isinstance(threat, AirThreat) for threat in threats):
            raise TypeError("All elements in the list must be of type AirThreat (ThreatAA or DetectionThreat)")
        
        check_for_altitude = False
        check_for_point = False

        if isinstance(arg, Point3D):
            point = arg
            check_for_point = True

        if isinstance(arg, float) or isinstance(arg, int):
            aircraft_altitude_route = arg
            check_for_altitude = True
                    
        threats_to_remove = []

        for threat in threats:
            
            if check_for_point and threat.innerPoint(point):
                threats_to_remove.append(threat)                

            if check_for_altitude and (  aircraft_altitude_route > threat.max_altitude or aircraft_altitude_route < threat.min_altitude):
                threats_to_remove.append(threat)                
                

        for threat in threats_to_remove:
            threats.remove(threat)

        return check_for_altitude or check_for_point
    
    def extractTerminalThreats(self, threats: list[ThreatAA], end: Point3D) -> list[ThreatAA]:
        """Remove from threats (in place) the threats whose volume contains the end point and returns them.

        Una minaccia che contiene end non e' evitabile se si vuole raggiungere end: la ricerca del percorso non
        deve tentare di evitarla (ne' di attraversarla con una corda di sicurezza, poiche' non si esce dal suo
        volume prima di arrivare). Viene quindi separata dalle minacce della ricerca e il suo danger viene
        applicato a posteriori con applyTerminalThreatsDanger.

        Args:
            threats (list[ThreatAA]): _list of threats considered in path search (modified in place)_
            end (Point3D): _end point of the route_

        Returns:
            list[ThreatAA]: _threats containing end point_
        """
        terminal_threats = [threat for threat in threats if threat.innerPoint(end)]

        for threat in terminal_threats:
            threats.remove(threat)

        return terminal_threats

    def applyTerminalThreatsDanger(self, path: Path, terminal_threats: list[ThreatAA], processed_edges: Optional[set] = None) -> None:
        """Add the danger level of terminal threats to the edges of the path entering their volume.

        Un edge "entra" nel volume se lo interseca partendo da un punto esterno: ogni ingresso nel volume conta
        una volta (un edge che parte gia' dentro il volume non e' un nuovo ingresso). E' la stessa convenzione di
        _handle_threat_crossing, dove il danger della minaccia attraversata e' assegnato al solo edge di
        attraversamento. Le metriche del path vengono ricalcolate.

        Args:
            path (Path): _completed path_
            terminal_threats (list[ThreatAA]): _threats containing the end point of the route_
            processed_edges (set, optional): _id of edges already processed: protects against a double
                application if the same Edge object were shared by more paths_
        """
        if not terminal_threats:
            return

        if processed_edges is None:
            processed_edges = set()

        for edge in path.edges:

            if id(edge) in processed_edges:
                continue

            processed_edges.add(id(edge))

            for threat in terminal_threats:

                if threat.innerPoint(edge.wpA.point):
                    continue

                _, intersection = threat.edgeIntersect(edge)

                if intersection is not None or threat.innerPoint(edge.wpB.point):
                    edge.danger += threat.danger_level

        path._calculate_metrics()

    def firstThreatIntersected(self, edge: Edge, threats: list[ThreatAA]) -> ThreatAA:
        """_Returns first threat intersected by the edge and the intersection with the threat volume._

        Args:
            edge (Edge): _description_
            threats (list[ThreatAA]): _description_

        Returns:
            bool, ThreatAA: Returns bool and first threat encountered.
            _If intersection has two points on surface (lateral or horizzontal) cylinder - bool == True, first threat encountered. 
            _If intersection has only one point on lateral or horizzontal surface of cylinder and other point inside of cylinder - bool == False, , first threat encountered.
            _otherwise - bool == False, None 
        """        
        DEBUG = True
        threat_distance = float('inf') # distanza da edge.wpa a threat.center
        first_threat = None
        complete_intersection = None
        complete_intersection_first_threat = None

        for threat in threats:
            complete_intersection, intersection = threat.edgeIntersect(edge)
            
            if complete_intersection or intersection:                
                wpA_Intersection_distance = edge.wpA.point.distance(intersection.p1) # distanza dalla circonferenza della threat
                
                if wpA_Intersection_distance < threat_distance:
                    threat_distance = wpA_Intersection_distance
                    complete_intersection_first_threat = complete_intersection
                    first_threat = threat                    
                    if DEBUG: print(f"Found threat intersection at lesser distance: threat: {threat!r}, threat_distance: {threat_distance:.2f}")        

        return complete_intersection_first_threat, first_threat

    def checkPathOverlimits(self, path_id, path: Path, range_max: float, danger_max: float) -> bool:
        
        """_Check if the path exceed the limits of range and danger.

        Args:
            path_id (_type_): _id of the path_
            path (Path): _path object_
            range_max (float): _range max value_
            danger_max (float): _danger max value

        Returns:
            bool: True if the path exceed the limits, False otherwise
        """        
        DEBUG = True

        if path.total_length > range_max:
            if DEBUG:
                print(f"Current path {path_id} with length {path.total_length:.2f} exceed range_max {range_max:.2f}")
            return True
        
        if path.total_danger > danger_max:
            if DEBUG:
                print(f"Current path {path_id} with danger {path.total_danger:.2f} exceed danger_max {danger_max:.2f}")
            return True
        
        return False

    # ottimizzazione deepseek
    def calcPathWithoutThreat(
        self,
        p1: Point3D,
        p2: Point3D,
        end: Point3D,
        threats: List[ThreatAA],
        n_edge: int,        
        path_id: int,
        path_collection: PathCollection,
        aircraft_altitude_min: float,
        aircraft_altitude_max: float,
        aircraft_speed_max: float,
        aircraft_speed: float,
        aircraft_range_max: float,
        time_to_inversion: float,
        change_alt_option: str,
        max_recursion: int = MAX_RECURSION,
        debug: bool = False,
        cross_threats: Optional[List[ThreatAA]] = None,
        aircraft_altitude: Optional[float] = None
    ) -> bool:
        """
        Calcola un percorso evitando minacce usando una strategia ricorsiva.
        
        Args:
            p1: Punto di partenza corrente
            p2: Punto di arrivo corrente
            end: Punto finale del percorso
            threats: Lista di minacce da evitare
            n_edge: Contatore di edge nel percorso corrente
            path_collection: Collezione di tutti i percorsi
            path_id: ID del percorso corrente
            aircraft_*: Parametri delle prestazioni dell'aereo
            change_alt_option: Strategia per il cambio di quota
            max_recursion: Limite di sicurezza per la ricorsione
            debug: Flag per abilitare i log di debug
            cross_threats: (ThreatMode.AVOID_DETECTION) minacce d'INTERCETTAZIONE da attraversare con la corda
                limitata sui tratti che, pur evitando le minacce di `threats`, le toccano. None = nessuna
                (comportamento storico di ThreatMode.AVOID). Lista mai modificata sul posto.
            aircraft_altitude: quota di rotta per la corda d'intercettazione; None = quota del punto p1
            
        Returns:
            True se è stato trovato almeno un percorso valido (inserito nella path collection), False altrimenti
        """
        if max_recursion <= 0 or path_collection.completed >= MAX_COMPLETED:
            if debug:
                print(f"Max recursion depth  or Max path completed {path_collection.completed} reached for path {path_id}")
            return False

        current_path = path_collection.get_path(path_id)
        wp_A = Waypoint(f"wp_A{path_id}_{n_edge}", p1, None)
        wp_B = Waypoint(f"wp_B{path_id}_{n_edge}", p2, None)
        edge = Edge(f"P:{path_id}-E:{n_edge}", n_edge, wp_A, wp_B, aircraft_speed)

        if debug:
            print(f"\nRecursion: {max_recursion} - Processing path {path_id}, edge {n_edge}: {wp_A.name}({getFormattedPoint(wp_A.point)}) -> {wp_B.name}({getFormattedPoint(wp_B.point)})")

        # Verifica intersezioni con minacce
        _, threat_intersect = self.firstThreatIntersected(edge, threats)

        if not threat_intersect:

            # ThreatMode.AVOID_DETECTION: il tratto evita i volumi da aggirare ma puo' ricadere comunque in
            # un volume d'intercettazione (non annidato, o piu' largo del volume di rilevamento ridotto
            # dall'orizzonte): lo si attraversa con la corda limitata, mai per ipotesi di annidamento.
            if cross_threats:
                complete_intersection, cross_threat = self.firstThreatIntersected(edge, cross_threats)

                if cross_threat is not None:
                    return self._cross_interception_while_avoiding(
                        edge, cross_threat, complete_intersection, p2, end, threats, cross_threats, n_edge,
                        path_id, path_collection,
                        aircraft_altitude_min, aircraft_altitude_max,
                        aircraft_speed_max, aircraft_speed, aircraft_range_max, time_to_inversion,
                        change_alt_option, max_recursion, debug, aircraft_altitude
                    )

            current_path.add_edge(edge)
            
            # terminate path if length or danger exceed limits
            if self.checkPathOverlimits(path_id, current_path, aircraft_range_max, float('inf')):
                return False
            
            if debug:
                print(f"No threats found. Added edge to path {path_id}")

            if p2 == end:
                path_collection.mark_path_completed(path_id)
                if debug:
                    print(f"Path {path_id} completed successfully!")
                return True

            return self.calcPathWithoutThreat(
                p2, end, end, threats, n_edge + 1, path_id, path_collection, 
                aircraft_altitude_min, aircraft_altitude_max,
                aircraft_speed_max, aircraft_speed, aircraft_range_max, time_to_inversion,
                change_alt_option, max_recursion - 1, debug,
                cross_threats = cross_threats, aircraft_altitude = aircraft_altitude
            )

        # Gestione alternativa (cambio quota o percorso alternativo)
        return self._handle_threat_avoidance(
            edge, threat_intersect, p1, p2, end, threats, n_edge,
            path_id, path_collection, 
            aircraft_altitude_min, aircraft_altitude_max,
            aircraft_speed_max, aircraft_speed, aircraft_range_max, time_to_inversion,
            change_alt_option, max_recursion, debug,
            cross_threats = cross_threats, aircraft_altitude = aircraft_altitude
        )        

    def _cross_interception_while_avoiding(
        self,
        edge: Edge,
        threat: ThreatAA,
        complete_intersection: bool,
        p2: Point3D,
        end: Point3D,
        threats: List[AirThreat],
        cross_threats: List[ThreatAA],
        n_edge: int,
        path_id: int,
        path_collection: PathCollection,
        aircraft_altitude_min: float,
        aircraft_altitude_max: float,
        aircraft_speed_max: float,
        aircraft_speed: float,
        aircraft_range_max: float,
        time_to_inversion: float,
        change_alt_option: str,
        max_recursion: int,
        debug: bool,
        aircraft_altitude: Optional[float] = None
    ) -> bool:
        """_Crossing of an INTERCEPTION volume met by an edge that already avoids the volumes to avoid (ThreatMode.AVOID_DETECTION)._

        Stessa logica a corda limitata di ThreatMode.CROSS_UNINTERCEPTED (calcPathWithThreat/_handle_threat_crossing):
          - solo intersezione COMPLETA (due punti sulla superficie laterale); ogni altra intersezione (estremo
            interno, ingresso dall'alto/basso) fa fallire il ramo, come in calcPathWithThreat;
          - corda massima da calcMaxLenghtCrossSegmentInterception (sito gia' pronto, ready_delay_s = 0); se
            l'intersezione e' piu' lunga, corda alternativa da Cylinder.find_chord_coordinates;
          - danger della minaccia sull'arco di attraversamento, minaccia tolta dalle successive.
        Differenze, per non violare l'aggiramento dei volumi di rilevamento:
          - i nuovi archi (p1 -> ingresso, attraversamento) sono verificati contro `threats` (i volumi da
            aggirare) e contro le altre minacce d'intercettazione: se ne toccano una il ramo fallisce, invece
            degli spostamenti laterali di _handle_threat_crossing (che non conoscono i volumi da aggirare);
          - dall'uscita la ricerca riprende verso p2 (il waypoint d'aggiramento previsto), non verso end;
          - `cross_threats` non e' mai modificata sul posto: al ramo successivo passa una lista nuova senza
            la minaccia attraversata (i rami d'aggiramento condividono la lista).

        Returns:
            bool: _True if a valid path is found, False otherwise_
        """
        if not complete_intersection:
            if debug:
                print(f"Interception threat {threat!r} intersected but not laterally crossed: branch dropped")
            return False

        _, intersection = threat.edgeIntersect(edge)

        if intersection is None:
            return False

        altitude = aircraft_altitude if aircraft_altitude is not None else edge.wpA.point.z
        max_length = threat.calcMaxLenghtCrossSegmentInterception(aircraft_speed, altitude, time_to_inversion)

        p_A = Point2D(intersection.p1.x, intersection.p1.y)
        p_B = Point2D(intersection.p2.x, intersection.p2.y)

        if intersection.length < max_length:
            c, d = p_A, p_B

        else:
            if max_length <= 0:
                if debug:
                    print(f"Interception threat {threat!r} not crossable (max length {max_length:.2f}): branch dropped")
                return False

            c, d = threat.cylinder.find_chord_coordinates(threat.cylinder.radius, threat.cylinder.center, p_A, p_B, max_length)

        # c primo punto (ingresso), d secondo (uscita)
        if c.distance(edge.wpA.point2d) > d.distance(edge.wpA.point2d):
            c, d = d, c

        v_norm = get_direction_vector(Point2D(c.x, c.y), Point2D(d.x, d.y))
        d = Point2D(d.x + v_norm[0] * TOLERANCE_FOR_INTERSECTION_CALCULUS, d.y + v_norm[1] * TOLERANCE_FOR_INTERSECTION_CALCULUS)

        wp_c = Waypoint(f"wp_{path_id}_{n_edge}_icross1", Point3D(c.x, c.y, edge.wpA.point.z), None)
        wp_d = Waypoint(f"wp_{path_id}_{n_edge}_icross2", Point3D(d.x, d.y, edge.wpA.point.z), None)
        edge_to_c = Edge(f"P:{path_id}-E:{n_edge}_pre", n_edge, edge.wpA, wp_c, edge.speed)
        edge_through = Edge(f"P:{path_id}-E:{n_edge + 1}_through", n_edge + 1, wp_c, wp_d, edge.speed)
        other_cross_threats = [t for t in cross_threats if t is not threat]

        for new_edge in (edge_to_c, edge_through):
            _, avoided = self.firstThreatIntersected(new_edge, threats)
            _, other_interception = self.firstThreatIntersected(new_edge, other_cross_threats)

            if avoided is not None or other_interception is not None:
                if debug:
                    print(f"Interception crossing edge {new_edge!r} meets another threat: branch dropped")
                return False

        current_path = path_collection.get_path(path_id)
        current_path.add_edge(edge_to_c)
        edge_through.danger = threat.danger_level
        current_path.add_edge(edge_through)

        if debug:
            print(f"Crossed interception threat {threat!r} while avoiding detection. Current path: {current_path!r}")

        if self.checkPathOverlimits(path_id, current_path, aircraft_range_max, float('inf')):
            return False

        return self.calcPathWithoutThreat(
            wp_d.point, p2, end, threats, n_edge + 2, path_id, path_collection,
            aircraft_altitude_min, aircraft_altitude_max,
            aircraft_speed_max, aircraft_speed, aircraft_range_max, time_to_inversion,
            change_alt_option, max_recursion - 1, debug,
            cross_threats = other_cross_threats, aircraft_altitude = aircraft_altitude
        )


    def calcPathWithThreat(
        self,
        p1: Point3D,
        p2: Point3D,
        end: Point3D,
        threats: List[ThreatAA],
        n_edge: int,
        path_id: int,
        path_collection: PathCollection,   
        aircraft_altitude: float,             
        aircraft_altitude_min: float,
        aircraft_altitude_max: float,
        aircraft_speed_max: float,
        aircraft_speed: float,
        aircraft_range_max: float,
        time_to_inversion: float,
        change_alt_option: str,
        max_recursion: int = MAX_RECURSION,
        debug: bool = False
    ) -> bool:
        """
        Calcola un percorso considerando l'attraversamento controllato delle minacce.
        
        Args:
            p1: Punto di partenza corrente
            p2: Punto di arrivo corrente
            end: Punto finale del percorso
            threats: Lista di minacce da valutare
            n_edge: Contatore di edge nel percorso corrente
            path_collection: Collezione di tutti i percorsi
            path_id: ID del percorso corrente
            aircraft_*: Parametri delle prestazioni dell'aereo
            change_alt_option: Strategia per il cambio di quota
            max_recursion: Limite di sicurezza per la ricorsione
            debug: Flag per abilitare i log di debug
            
        Returns:
            True se è stato trovato almeno un percorso valido (inserito nella path collection), False altrimenti
        """
        if max_recursion <= 0 or path_collection.completed >= MAX_COMPLETED:
            if debug:
                print(f"Max recursion depth or Max path completed {path_collection.completed}  completed reached for path {path_id}")
            return False

        current_path = path_collection.get_path(path_id)
        wp_A = Waypoint(f"wp_A{path_id}_{n_edge}", p1, None)
        wp_B = Waypoint(f"wp_B{path_id}_{n_edge}", p2, None)
        edge = Edge(f"P:{path_id}-E:{n_edge}", n_edge, wp_A, wp_B, aircraft_speed)

        if debug:
            print(f"\nProcessing path {path_id}, edge n:{n_edge}: {edge!r}")

        # Verifica intersezioni con minacce
        complete_intersection, threat_intersect = self.firstThreatIntersected(edge, threats)

        if not threat_intersect:
            current_path.add_edge(edge)

            # terminate path if length or danger exceed limits
            if self.checkPathOverlimits(path_id, current_path, aircraft_range_max, float('inf')):
                return False
            
            if debug:
                print(f"No threats found. Added edge to path {path_id}")

            if p2 == end:
                path_collection.mark_path_completed(path_id)
                if debug:
                    print(f"Path {path_id} completed successfully!")
                return True

            return self.calcPathWithThreat(
                p2,
                end, 
                end, 
                threats, 
                n_edge + 1, 
                path_id, 
                path_collection, 
                aircraft_altitude,
                aircraft_altitude_min, 
                aircraft_altitude_max,
                aircraft_speed_max, 
                aircraft_speed, 
                aircraft_range_max, 
                time_to_inversion,
                change_alt_option, 
                max_recursion - 1, 
                debug
            )

        elif complete_intersection: # l'intersezione con la prima threat trovata è completa (il segmento interseca la threat in due punti)
            threatInrange, intersection = threat_intersect.edgeIntersect(edge) # crea l'intersezione

            if not threatInrange and intersection:
                raise Exception(f"not valid intersection: {getFormattedPoint(intersection.p1)} - {getFormattedPoint(intersection.p2)}")
                
            max_length = threat_intersect.calcMaxLenghtCrossSegmentInterception(aircraft_speed, 
                                                                                aircraft_altitude, 
                                                                                time_to_inversion)
                                                     
            # Verifica se possiamo attraversare la minaccia in sicurezza        
            return self._handle_threat_crossing(
                edge, 
                threat_intersect, 
                p2, 
                end, 
                threats, 
                n_edge,
                path_id, 
                path_collection, 
                max_length, 
                aircraft_altitude,
                aircraft_altitude_min, 
                aircraft_altitude_max,
                aircraft_speed_max, 
                aircraft_speed, 
                aircraft_range_max, 
                time_to_inversion,
                change_alt_option, 
                intersection, 
                max_recursion, 
                debug
            )
                    
        else:
            return False

    def _handle_threat_crossing(
        self,
        edge: Edge,
        threat: ThreatAA,
        p2: Point3D,# da eliminare
        end: Point3D,
        threats: List[ThreatAA],
        n_edge: int,
        path_id: int,
        path_collection: PathCollection,        
        max_length: float,
        aircraft_altitude: float,
        aircraft_altitude_min: float,
        aircraft_altitude_max: float,
        aircraft_speed_max: float,
        aircraft_speed: float,
        aircraft_range_max: float,
        time_to_inversion: float,
        change_alt_option: str,
        intersection: Segment3D,
        max_recursion: int,
        debug: bool
    ) -> bool:        
        """_Handles the threat crossing logic, including creating new edges and checking for valid paths._

        Args:
            edge (Edge): _edge object for evaluation_
            threat (ThreatAA): _threat object for evaluation_
            p2 (Point3D): _description_
            end (Point3D): _end point of the path_
            threats (List[ThreatAA]): _list of threats 
            n_edge (int): _edges counter
            path_id (int): _path id
            path_collection (PathCollection): _collection of paths found_
            max_length (float): _max length reference for calulated a valid intersection alternative 
            aircraft_altitude (float): _aircraft reference altitude_
            aircraft_altitude_min (float): _aircraft minimum altitude
            aircraft_altitude_max (float): _aircraft maximum altitude
            aircraft_speed_max (float): _aircraft maximum speed
            aircraft_speed (float): _aircraft reference speed
            aircraft_range_max (float): __aircraft maximum range
            time_to_inversion (float): _minimum time needed to invert aircraft direction
            change_alt_option (str): _flag to authorize change in aircraft altitude to avoid threat. Defaults to "no_change".
            intersection (Segment3D): _actual intersection segment of the edge with threat
            max_recursion (int): _recursion counter
            debug (bool): _flag to print debug info

        Returns:
            bool: _True if a valid path is found, False otherwise_
        """

        if debug:
            print(f"Attempting to cross threat: {threat!r} with max length {max_length: .2f}")

        # punti dell'intersezione relativa all'edge
        p_A = Point2D(intersection.p1.x, intersection.p1.y)
        p_B = Point2D(intersection.p2.x, intersection.p2.y)

        if intersection.length < max_length: # l'intersezione relativa all'edge è più corta della lunghezza massima consentita per l'attraversamento sicuro
            if debug:
                print(f"Intersection length {intersection.length:.2f} is less than max length {max_length:.2f}.")

            c = p_A
            d = p_B    


        else: # necesssario determinare un segmento d'intersezione alternativo da utilizzare come nuovo edge per un attarversamento sicuro
            if debug:
                print(f"Intersection length {intersection.length:.2f} is bigger than max length {max_length:.2f}.")

            
            # Trova i punti di attraversamento ottimali
            c, d = threat.cylinder.find_chord_coordinates(
                threat.cylinder.radius,
                threat.cylinder.center,
                p_A,
                p_B,
                max_length
            )
        # riordina i punti in modo da considerare c come primo punto e d come secondo punto
        if c.distance(edge.wpA.point2d) > d.distance(edge.wpA.point2d):
            s = c
            c = d
            d = s


        # calcola il vettore direzione e lo utilizza per lo spostamento  del punto esternamente alla threat in direzione del segmento intersecante                
        v_norm = get_direction_vector(Point2D(c.x, c.y), Point2D(d.x, d.y))
        #v_dx = d.x - c.x
        #v_dy = d.y - c.y
        #v_norm = math.sqrt(v_dx**2 + v_dy**2)        
        #d = Point2D( d.x + v_dx  * TOLERANCE_FOR_INTERSECTION_CALCULUS / v_norm, d.y + v_dy * TOLERANCE_FOR_INTERSECTION_CALCULUS / v_norm)
        d = Point2D( d.x + v_norm[0]  * TOLERANCE_FOR_INTERSECTION_CALCULUS, d.y + v_norm[1] * TOLERANCE_FOR_INTERSECTION_CALCULUS)

        # Crea i waypoint di attraversamento
        wp_c = Waypoint(f"wp_{path_id}_{n_edge}_cross1", Point3D(c.x, c.y, edge.wpA.point.z), None)
        wp_d = Waypoint(f"wp_{path_id}_{n_edge}_cross2", Point3D(d.x, d.y, edge.wpA.point.z), None)

        # Edge fino al punto di ingresso
        edge_to_c = Edge(
            f"P:{path_id}-E:{n_edge}_pre", 
            n_edge,
            edge.wpA,
            wp_c,
            edge.speed
        )

        # Edge attraverso la minaccia
        edge_through = Edge(
            f"P:{path_id}-E:{n_edge + 1}_through", 
            n_edge + 1,
            wp_c,
            wp_d,
            edge.speed
        )        

        if debug:
            print(f"calculated candidate edges to path {path_id}:\n - from p1 to threat: {edge_to_c!r},\n - through threat: {edge_through!r}")
        
        # Verify other threat on exit point        
        for other_threat in threats:

            if other_threat != threat and other_threat.innerPoint(wp_d.point): # exit point inside another threat
                # se sono rilevate altre threat non inserisco nessun edge dei due precedentemente calcolati e procedo
                # per calcolare due punti spostati lateralmente di +90 gradi e -90 gradi rispetto la direzione dell'edge iniziale di attraversamento della threat
                result1 = False
                result2 = False

                if debug:
                    print(f"cross threat edge intersecate another threat: ( {other_threat!r} )")
         
                # continue to avoid threat with lateral moving from wpA to new lateral point wp_b1
                dir = get_direction_vector(Point2D(d.x, d.y), Point2D(c.x, c.y))
                dir = rotate_vector(dir, math.pi / 2) # ruota il vettore direzione di 90 gradi rispetto al segmento intersecante
                new_p1 = Point3D(threat.cylinder.center.x + dir[0] * 1.5 * threat.cylinder.radius, threat.cylinder.center.y + dir[1] * 1.5 * threat.cylinder.radius, edge.wpA.point.z)# nuovo punto calcolato in direzione di 90 gradi rispetto la direzione dell'edge  precedentemente calcolato
                wp_b1 = Waypoint(f"wp_{path_id}_{n_edge}_lateral_1", new_p1, None)
                new_edge_1 = Edge(
                    f"P:{path_id}-E:{n_edge}_new_lateral_1", 
                    n_edge,
                    edge.wpA,
                    wp_b1,
                    edge.speed
                )


                # continue to avoid threat with lateral moving from wpA to new lateral point wp_b2 - new path
                path_edges_copy = copy.deepcopy(path_collection.get_path(path_id).edges) #copy list of edges of current path
                new_path_id = path_collection.add_path(path_edges_copy) 
                dir = rotate_vector(dir, math.pi) # ruota il vettore di 180 (-90) gradi rispetto al segmento intersecante
                new_p2 = Point3D(threat.cylinder.center.x + dir[0] * 1.5 * threat.cylinder.radius, threat.cylinder.center.y + dir[1] * 1.5 * threat.cylinder.radius, edge.wpA.point.z)# nuovo punto calcolato in direzione di -90 gradi rispetto la direzione dell'edge  precedentemente calcolato                    
                wp_b2 = Waypoint(f"wp_{path_id}_{n_edge}_lateral_2", new_p2, None)
                new_edge_2 = Edge(
                    f"P:{new_path_id}-E:{n_edge}_new_lateral_2", 
                    n_edge,
                    edge.wpA,
                    wp_b2,
                    edge.speed
                )

                if debug:
                    print(f"\n   calculare two lateral point: new_p1: {getFormattedPoint(new_p1)}, new_p2: {getFormattedPoint(new_p2)}")
                    print(f"\n   will try with lateral moving of radius of the first threat. New point p1: {getFormattedPoint(new_p1)}")
                
                result1 = self.calcPathWithThreat( # prova a calcolare il percorso con il nuovo edge relativo al nuovo punto calcolato con uno spostamento di 90 gradi rispetto l'edge precedentemente calcolato
                    new_edge_1.wpA.point,  # punto wpA  dell'edge precedentemente calcolato
                    new_edge_1.wpB.point,  # nuovo punto calcolato con uno spostamento di +90 gradi rispetto l'edge precedentemente calcolato
                    end,
                    threats, 
                    n_edge, 
                    path_id, 
                    path_collection, 
                    aircraft_altitude,
                    aircraft_altitude_min, 
                    aircraft_altitude_max,
                    aircraft_speed_max, 
                    aircraft_speed, 
                    aircraft_range_max, 
                    time_to_inversion, 
                    change_alt_option, 
                    max_recursion - 1, 
                    debug
                )
                
                if debug:
                    print(f"\n   will try with lateral moving of radius of the first threat. New point p2: {getFormattedPoint(new_p1)}")

                result2 = self.calcPathWithThreat(# prova a calcolare il percorso con il nuovo edge relativo al nuovo punto calcolato con uno spostamento di -90 gradi rispetto l'edge precedentemente calcolato
                    new_edge_2.wpA.point,  # punto wpA  dell'edge precedentemente calcolato
                    new_edge_2.wpB.point,  # nuovo punto calcolato con uno spostamento di -90 gradi rispetto l'edge precedentemente calcolato
                    end,
                    threats, 
                    n_edge, 
                    new_path_id, 
                    path_collection, 
                    aircraft_altitude,
                    aircraft_altitude_min, 
                    aircraft_altitude_max,
                    aircraft_speed_max, 
                    aircraft_speed, 
                    aircraft_range_max, 
                    time_to_inversion, 
                    change_alt_option, 
                    max_recursion - 1, 
                    debug
                )

                return result1 or result2

        # exit_point isn't inside other threats
        current_path = path_collection.get_path(path_id)
        current_path.add_edge(edge_to_c) # inserisco l'edge da p1 a c
        edge_through.danger = threat.danger_level
        current_path.add_edge(edge_through) # inserisco l'edge da c a d
        threats.remove(threat) #remove crossing threat. È improbabile che il calcolo dei successivi edge possa determinare una inversione della direzione del percorso tale da reintersecare la threat da cancellare

        if debug:
            print(f"cross threat edge don't intersecate other threat. Current path: {current_path!r},\n    added two edges candidate edges (from p1 to threat, through threat) and delete crossing threat {threat!r}")
            
        # terminate path if length or danger exceed limits
        if self.checkPathOverlimits(path_id, current_path, aircraft_range_max, float('inf')):
            return False

        # Prosegui dal punto di uscita
        return self.calcPathWithThreat(
            edge_through.wpB.point,  # Punto d
            end, 
            end, 
            threats, 
            n_edge + 2, # gli edge inseriti nel path sono due: edge_to_c e edge_through
            path_id, 
            path_collection, 
            aircraft_altitude,
            aircraft_altitude_min, 
            aircraft_altitude_max,
            aircraft_speed_max, 
            aircraft_speed, 
            aircraft_range_max, 
            time_to_inversion, 
            change_alt_option, 
            max_recursion - 1, 
            debug
        )

    def _handle_threat_avoidance(
        self,
        edge: Edge,
        threat: ThreatAA,
        p1: Point3D,
        p2: Point3D,
        end: Point3D,
        threats: List[ThreatAA],
        n_edge: int,        
        path_id: int,
        path_collection: PathCollection,
        aircraft_altitude_min: float,
        aircraft_altitude_max: float,
        aircraft_speed_max: float,
        aircraft_speed: float,
        aircraft_range_max: float,
        time_to_inversion: float, 
        change_alt_option: str,
        max_recursion: int,
        debug: bool,
        cross_threats: Optional[List[ThreatAA]] = None,
        aircraft_altitude: Optional[float] = None
    ) -> bool:
        """_Handles the threat avoidance logic, including altitude change or alternative paths._

        Args:            
            edge (Edge): _edge object for evaluation_
            threat (ThreatAA): _threat object for evaluation_
            p1 (Point3D): _first point of the edge_
            p2 (Point3D): _second point of the edge_
            end (Point3D): _end point of the path_
            threats (List[ThreatAA]): _list of threats 
            n_edge (int): _edges counter
            path_id (int): _path id
            path_collection (PathCollection): _collection of paths found_                        
            aircraft_altitude_min (float): _aircraft minimum altitude
            aircraft_altitude_max (float): _aircraft maximum altitude
            aircraft_speed_max (float): _aircraft maximum speed
            aircraft_speed (float): _aircraft reference speed
            aircraft_range_max (float): __aircraft maximum range
            time_to_inversion (float): _minimum time needed to invert aircraft direction
            change_alt_option (str): _flag to authorize change in aircraft altitude to avoid threat. Defaults to "no_change".            
            max_recursion (int): _recursion counter
            debug (bool): _flag to print debug info
            cross_threats (List[ThreatAA], optional): _interception threats crossed with limited chord (ThreatMode.AVOID_DETECTION), passed through to calcPathWithoutThreat
            aircraft_altitude (float, optional): _route altitude for the interception chord, passed through


        Returns:
            bool: _True if a valid path is found, False otherwise_
        """        
        
        # Verifica se possiamo cambiare quota
        # Un volume di RILEVAMENTO non si scavalca ne' si sottopassa: e' costruito alla sola quota di rotta (raggio
        # dall'orizzonte a quella quota) e non ha la fascia piatta dei volumi d'intercettazione. Il suo limite basso
        # e' ~0 (non si passa sotto un radar vicino) e scendere RESTRINGE il raggio invece di uscire dal volume:
        # il cambio di quota resta disabilitato finche' il volume non sara' ricostruito alla nuova quota
        # (proposta §3.6, Attivita' D).
        can_change_altitude =   not isinstance(threat, DetectionThreat) and ( ( change_alt_option!= "no_change") and (change_alt_option == "change_up" and (aircraft_altitude_max > threat.max_altitude * MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MAX_VALUE)) or (change_alt_option == "change_down" and (aircraft_altitude_min < threat.min_altitude * MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MIN_VALUE)) )

        if can_change_altitude:
            
            if debug:
                print(f"Attempting altitude change for threat at {threat!r}")

            intersected, segm = threat.cylinder.getIntersection(
                edge.getSegment3D(), tolerance = TOLERANCE_FOR_INTERSECTION_CALCULUS
            )
            
            
            if not intersected and segm: # se l'intersezione è un segmento (parte dell'edge) che attraversa la threat viene dall'alto e và verso il basso, può essere gestito con cambio quota di pb. altrimenti no

                pa, pb = segm.points

                if  not ( threat.cylinder.innerPoint(pa) and  pa.z >= threat.max_altitude ): # l'intersezione non è un segmentro (parte dell'edge) che attraversa la threat viene dall'alto e và verso il basso. Quind non gestito con cambio quota

                    if debug:
                        print(f"Unexpected: no intersection found where threat was detected  (segm: {segm!r})")                    
                    
                    return False
            

            new_p1 = segm.p1
            new_p2 = segm.p2

            if edge.wpA.point.distance(Point3D(new_p1.x, new_p1.y, edge.wpA.point.z)) < MIN_DISTANCE_TO_CHANGE_ALTITUDE:# la distanza tra p1 e il cilindro è insufficiente a consentire all'aereo di cambiare quota

                if debug:
                    print(f"Distance to change altitude is too small: {edge.wpA.point.distance(Point3D(new_p1.x, new_p1.y, edge.wpA.point.z)):.2f} < {MIN_DISTANCE_TO_CHANGE_ALTITUDE}")

                # calcola il vettore direzione e lo utilizza per lo spostamento  del punto esternamente alla threat in direzione traslata di +90 gradi e -90 gradi rispetto al segmento intersecante
                direction_movement = get_direction_vector(edge.wpA.point2d, edge.wpB.point2d)
                direction_movement = rotate_vector(direction_movement, math.pi / 2) # direzione +90 gradi
                direction_movement_1 = rotate_vector(direction_movement, math.pi) # direzione -90 gradi
                new_p = None

                # prova a calcolare nuovo punti di attraversamento spostati lateralmente di +90 gradi e -90 gradi, a diverse distannze, rispetto la direzione dell'edge iniziale di attraversamento della threat verificando per ogni punto calcolato se questo è interno  ad una threat.
                #for ds in (0.1, 0.3, 0.6, 0.9, 1.2, 1.5, 2):
                for ds in (5, 10, 30, 70, 100):
                    #new_pA = Point3D(new_p1.x + direction_movement[0] * threat.cylinder.radius * ds, new_p1.y + direction_movement[1] * threat.cylinder.radius * ds, edge.wpA.point.z)                
                    #new_pB = Point3D(new_p1.x + direction_movement_1[0] * threat.cylinder.radius * ds, new_p1.y + direction_movement_1[1] * threat.cylinder.radius * ds, edge.wpA.point.z)                    
                    new_pA = Point3D(new_p1.x + direction_movement[0] * MIN_DISTANCE_TO_CHANGE_ALTITUDE * ds, new_p1.y + direction_movement[1] * MIN_DISTANCE_TO_CHANGE_ALTITUDE * ds, edge.wpA.point.z)                
                    new_pB = Point3D(new_p1.x + direction_movement_1[0] * MIN_DISTANCE_TO_CHANGE_ALTITUDE * ds, new_p1.y + direction_movement_1[1] * MIN_DISTANCE_TO_CHANGE_ALTITUDE * ds, edge.wpA.point.z)                    
                    
                    if not threat.innerPoint(new_pA):
                        new_p = new_pA
                        break
                        
                    elif not threat.innerPoint(new_pB):
                        new_p = new_pB
                        break

                if new_p: # trovato un nuovo punto laterale non interno ad una threat

                    if debug:
                        print(f" I'll try search path with new point: {getFormattedPoint(new_p)}.")

                    return self.calcPathWithoutThreat( # prosegue la ricerca del path utilizzando questo nuovo punto come p2
                        edge.wpA.point, new_p, end, threats, n_edge, path_id, path_collection, 
                        aircraft_altitude_min, aircraft_altitude_max,
                        aircraft_speed_max, aircraft_speed, aircraft_range_max, time_to_inversion,
                        change_alt_option, max_recursion - 1, debug,
                        cross_threats = cross_threats, aircraft_altitude = aircraft_altitude
                    )
                                                        

            else:# la distanza tra p1 e il cilindro è idonea a consentire all'aereo di cambiare quota

                # calcolo nuovo punto sopra la threat
                if change_alt_option == "change_up":
                    new_altitude = ( 2 * aircraft_altitude_max + threat.max_altitude * MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MAX_VALUE ) / 3
                    new_p1 = Point3D(new_p1.x, new_p1.y, new_altitude )
                    new_p2 = Point3D(new_p2.x, new_p2.y, new_altitude ) 
                    if debug:
                        print(f"Changing altitude UP to {new_p1.z:.2f}")
                
                # calcolo nuovo punto sotto la threat        
                else:
                    new_altitude = ( threat.min_altitude * MARGIN_AIRCRAFT_ALTITUDE_AVOIDANCE_MIN_VALUE + 2 * aircraft_altitude_min ) / 3
                    new_p1 = Point3D(new_p1.x, new_p1.y, new_altitude )
                    new_p2 = Point3D(new_p2.x, new_p2.y, new_altitude )
                    if debug:
                        print(f"Changing altitude DOWN to {new_p1.z:.2f}")

                # Crea nuovo edge con punto modificato
                new_wp_B = Waypoint(f"wp_B{path_id}_{n_edge}_alt", new_p1, None)
                new_wp_C = Waypoint(f"wp_C{path_id}_{n_edge}_alt", new_p2, None)

                new_edge = Edge( # edge da wpA al primo punto spra la threat
                    f"P:{path_id}-E:{n_edge}_alt",
                    n_edge, 
                    edge.wpA, 
                    new_wp_B, 
                    aircraft_speed
                )

                new_edge_C = Edge(# edge dal primo punto spra la threat alla fine della threat
                    f"P:{path_id}-E:{n_edge + 1}_alt", 
                    n_edge + 1, 
                    new_wp_B, 
                    new_wp_C, 
                    aircraft_speed
                )

                current_path = path_collection.get_path(path_id)
                current_path.add_edge(new_edge) # inserisco il primo edge nel path
                edge_incr = 1

                if debug:
                    if debug:
                        print(f"current path: {current_path!r} added edge from wpA to threat: {new_edge!r}")

                # verifico se il secondo edge, quello che passa sopra la threat, non intersechi una threat differente rispetto quella considerata per il cambio della quota
                threatInRange, threat_intersect = self.firstThreatIntersected(new_edge_C, threats)

                # se il secondo edge non interseca una minaccia diversa da quella utilizzata per il calcolo della quota procede con il suo inserimento nel path
                if not threat_intersect or threat_intersect.max_altitude < new_edge_C.wpB.point.z: #not self.firstThreatIntersected(new_edge_C, threats):                      
                    current_path.add_edge(new_edge_C) # se il segmento che passa sopra la minaccia incontra altre minacce lo aggiunge al pth
                    edge_incr = 2
                    new_p1 = new_p2
                    if debug:
                        print(f"current path: {current_path!r} added edge from previous edge.wpB up or down threat: {new_edge_C!r}")
            
                # terminate path if length or danger exceed limits
                if self.checkPathOverlimits(path_id, current_path, aircraft_range_max, float('inf')):
                    return False

                return self.calcPathWithoutThreat(# prosegue nella creazione del path
                    new_p1, end, end, threats, n_edge + edge_incr, path_id, path_collection, 
                    aircraft_altitude_min, aircraft_altitude_max,
                    aircraft_speed_max, aircraft_speed, aircraft_range_max, time_to_inversion,
                    change_alt_option, max_recursion - 1, debug,
                    cross_threats = cross_threats, aircraft_altitude = aircraft_altitude
                )
                        
        # Se non possiamo cambiare quota, troviamo percorsi alternativi calcolando gli extended points per una circonferenza leggermente più grande della threat
        extended_cylinder = Cylinder(threat.cylinder.center, threat.cylinder.radius * RADIUS_EXTENSION_THREAT_CIRCONFERENCE, threat.cylinder.height)
        ext_p1, ext_p2 = extended_cylinder.getExtendedPoints(
            edge.getSegment3D(), tolerance = TOLERANCE_FOR_INTERSECTION_CALCULUS
        )
        

        if not ext_p1 and not ext_p2: # punti esterni non trovati: si può verificare solo nel caso che uno dei punti p1 o p2 sia sulla circonferenza
            if debug:
                print(f"Could not find extended points around threat: p1 or p2 on threat circonferenze? -> wpA: {threat.cylinder.pointOfCirconference(edge.wpA.point2d)}, wpB: {threat.cylinder.pointOfCirconference(edge.wpB.point2d)}")
            return False

        if debug:
            print(f"found two external point from extended_cylinder threat({extended_cylinder!r}), ext1: {getFormattedPoint(ext_p1)}, ext2: {getFormattedPoint(ext_p2)}")

        # verifica della lunghezza dai punti calcolati rispetto il primo punto per eliminare quello la cui distanza eccessiva è dovuta ad una condizione critica di posizione rispetto al punto di destinazione e vicinanza rispetto la superfica laterale della threat: le  due tangenti utilizzate per determinare il punto d'intersezione ext_p sono quasi parallele)
        ext_p1_distance = ext_p1.distance(edge.wpA.point) + ext_p1.distance(edge.wpB.point) # new
        ext_p2_distance = ext_p2.distance(edge.wpA.point) + ext_p2.distance(edge.wpB.point)  # new      
        
        if ext_p2_distance > 2 * ext_p1_distance: # new ext_p2 richiede un punto del percorso troppo distante rispetto ext_p1. Il punto non viemne considerato per procedere nella ricorsione per la valutazione di un percorso
            ext_p2 = None # procede solo ext_p2 con il path corrente
            if debug:
                print(f"Deleted ext_p2 from path ricorsion: ext_p2_distance{ext_p2_distance:.2f} > double ext_p1_distance{ext_p1_distance:.2f}")


        elif ext_p1_distance > 2 * ext_p2_distance: # new ext_p1 richiede un punto del percorso troppo distante rispetto ext_p12. Il punto non viemne considerato per procedere nella ricorsione per la valutazione di un percorso
            ext_p1 = None            
            new_path_id = path_id # procede solo ext_p2 con il path corrente
            if debug:
                print(f"Deleted ext_p1 from path ricorsion: ext_p1_distance{ext_p1_distance:.2f} > double ext_p2_distance{ext_p2_distance:.2f}")


        # Verifica se i punti estesi sono all'interno di altre minacce
        for other_threat in threats:
            
            if ext_p1 and other_threat != threat and other_threat.innerPoint(ext_p1):
                
                if debug:
                    print(f"Extended point ext_p1 is inside another threat: {other_threat!r}. Trying to find a new point with lateral movement.")
                
                
                # calcola un nuovo punto applicando uno spostamento laterale in linea con la (direzione centro del cilindro - punto esterno)
                direction_movement = get_direction_vector(Point2D(threat.cylinder.center.x, threat.cylinder.center.y), Point2D(ext_p1.x, ext_p1.y))
                valid_lateral_movement_ext_p1 = False
                
                # calcola nuove posizioni applicando uno spostamento laterale in linea con la (direzione centro del cilindro - punto esterno) considerando come nuovo punto da considerare il primo che risulta non interno ad una threat
                for ds in (0.1, 0.3, 0.5, 0.7, 0.9, 1.1, 1.3, 1.5, 1.7, 2.0):
                    ext_p1 = Point3D(ext_p1.x + direction_movement[0] * ds * other_threat.cylinder.radius, ext_p1.y + direction_movement[1] * ds * other_threat.cylinder.radius, ext_p1.z)                                        
                    
                    if not other_threat.innerPoint(ext_p1):
                        print(f"Valid lateral movement of Extended point ext_p1 {getFormattedPoint(ext_p1)}")
                        valid_lateral_movement_ext_p1 = True
                        break
            
                if not valid_lateral_movement_ext_p1:
                    if debug:
                        print(f"Not valid lateral movement of Extended point ext_p1. ext_p1 is inside another threat: {other_threat!r}")
                    ext_p1 = None


            if ext_p2 and other_threat != threat and other_threat.innerPoint(ext_p2):
                
                if debug:
                    print(f"Extended point ext_p2 is inside another threat: {other_threat!r}. Trying to find a new point with lateral movement.")
                
                # calcola un nuovo punto applicando uno spostamento laterale in linea con la (direzione centro del cilindro - punto esterno)
                direction_movement = get_direction_vector(Point2D(threat.cylinder.center.x, threat.cylinder.center.y), Point2D(ext_p2.x, ext_p2.y))
                valid_lateral_movement_ext_p2 = False

                # calcola nuove posizioni applicando uno spostamento laterale in linea con la (direzione centro del cilindro - punto esterno) considerando come nuovo punto da considerare il primo che risulta non interno ad una threat
                for ds in (0.1, 0.3, 0.5, 0.7, 0.9, 1.1, 1.3, 1.5, 1.7, 2.0):
                    ext_p2 = Point3D(ext_p2.x + direction_movement[0] * ds * other_threat.cylinder.radius, ext_p2.y + direction_movement[1] * ds * other_threat.cylinder.radius, ext_p2.z)                                        
                    
                    if not other_threat.innerPoint(ext_p2):
                        print(f"Valid lateral movement of Extended point ext_p2 {getFormattedPoint(ext_p2)}")
                        valid_lateral_movement_ext_p2 = True
                        break
                
                
                if not valid_lateral_movement_ext_p2:
                    if debug:
                        print(f"Not valid lateral movement of Extended point ext_p2. ext_p2 is inside another threat: {other_threat!r}")
                    ext_p2 = None

        if len(path_collection.paths) < MAX_PATHS: # procedono sia ext_p1 che  ext_p2 il primo con il path corrente, il secondo con un nuovo path
            path_edges_copy = copy.deepcopy(path_collection.get_path(path_id).edges) #copy list of edges of current path
            new_path_id = path_collection.add_path(path_edges_copy) 

        else:
            if debug:
                print(f"Stop paths creation due max limit achieve{MAX_PATHS}")
            return False

        found_path1 = False
        found_path2 = False


        if ext_p1 or ext_p2: # uno o due nuovi punti esterni alla minaccia sono stati trovati

            if ext_p1: # new
                #path_edges_copy = copy.deepcopy(path_collection.get_path(path_id).edges) #copy list of edges of current path
                #new_path_id = path_collection.add_path(path_edges_copy) 

                if debug:
                    print(f"Creating alternative path through new point (ext_p1): {getFormattedPoint(ext_p1)}")#, \nProcessing path {path_id}, new edge {new_edge1}: {new_edge1.wpA.name}({getFormattedPoint(new_edge1.wpA.point)}) -> {new_edge1.wpB.name}({getFormattedPoint(new_edge1.wpB.point)})")
                    
                #path_edges_copy_1_1 = copy.deepcopy(path_collection.get_path(path_id).edges) #copy list of edges of current path
                #new_path_id_1_1 = path_collection.add_path(path_edges_copy_1_1) 
                #new_path_id_1_2 = path_collection.add_path(path_edges_copy_1_1) 

                found_path1 = self.calcPathWithoutThreat(# prosegue la ricerca del path considerando il nuovo punto
                    p1, 
                    ext_p1, 
                    end, 
                    threats, 
                    n_edge, 
                    path_id, 
                    path_collection, 
                    aircraft_altitude_min, 
                    aircraft_altitude_max,
                    aircraft_speed_max, 
                    aircraft_speed, 
                    aircraft_range_max, 
                    time_to_inversion,
                    change_alt_option, 
                    max_recursion - 1, 
                    debug,
                    cross_threats = cross_threats,
                    aircraft_altitude = aircraft_altitude
                )                    
               
            if ext_p2:# new
                # Percorso alternativo 2 (ext_p2)    
                
                
                if debug:
                        print(f"alterative path for path_id {path_id} with ext_p1: {getFormattedPoint(ext_p2)} not found")
                
                #path_edges_copy_1 = copy.deepcopy(path_collection.get_path(path_id).edges) #copy list of edges of current path
                #new_path_id_1_1 = path_collection.add_path(path_edges_copy_1) 
                #new_path_id_1_2 = path_collection.add_path(path_edges_copy_1) 

                found_path2 = self.calcPathWithoutThreat(# prosegue la ricerca del path considerando il nuovo punto
                    p1,
                    ext_p2, 
                    end, 
                    threats, 
                    n_edge, 
                    new_path_id, 
                    path_collection, # o path_edges_copy?
                    aircraft_altitude_min, 
                    aircraft_altitude_max,
                    aircraft_speed_max, 
                    aircraft_speed, 
                    aircraft_range_max, 
                    time_to_inversion,
                    change_alt_option, 
                    max_recursion - 1, 
                    debug,
                    cross_threats = cross_threats,
                    aircraft_altitude = aircraft_altitude
                )
                
            return found_path1 or found_path2



            
                    

                

        


