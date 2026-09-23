"""Profili di reazione RIV/VAL/COM/ATT — **chi spara per primo**.

FASE 4 del motore di sessioni virtuali (strato 2 dell'architettura DES, v.
`Analysis/Document/Architettura_esecuzione_sessioni_virtuali_ANALISI.md` §4.2 e §6).

## Da dove viene

La "Strategia 1" proposta dall'utente decomponeva il comportamento di un asset in quattro
classi di latenza — **RIV** (rilevazione), **VAL** (valutazione e decisione), **COM**
(traduzione in comandi), **ATT** (attuazione) — e le contava in cicli da 1 ms. L'analisi ha
bocciato il tick (§3.3: 74 giorni di calcolo per 2 ore di sessione) ma ha **salvato la
decomposizione**, che e' la parte migliore di quella strategia: e' l'unica cosa che
risponde a "chi spara per primo", cioe' all'iniziativa, la cui assenza fa fallire
empiricamente i modelli a rapporto di forze (§4.5). Qui le latenze diventano **parametri
per tipo di sistema**, e il risolutore (`Logic/Engagement_Resolver.py`) le usa per
schedulare eventi futuri ("questo asset lancera' fra 26 s"), non per contare iterazioni.

## Statuto dei numeri — leggere prima di usarli

**Sono documentati SOLO i totali** rilevazione -> lancio (tabella §4.2 del documento di
architettura, con le fonti in bibliografia): 9K33 Osa ~26 s, S-300P ~28 s, Tor da fermo
5-8 s, Tor-M2 "short stop" 2-3 s, pilota umano 1-2 s, equipaggio carro ~31 s per bersaglio,
IADS: valutazione della minaccia ~1 s, assegnazione arma-bersaglio poche centinaia di ms.
Dove la fonte da' un intervallo si usa il punto medio.

**La scomposizione nelle quattro fasi e' una STIMA DICHIARATA**, costruita cosi':
VAL, COM e ATT prendono gli ordini di grandezza citati nel testo della Strategia 1 (v. le
costanti *_S sotto: 100 ms di valutazione per una macchina e 10 s per un umano, 1 ms di
comando per un sistema automatico e 1 s per un equipaggio manuale, 0,1 s di brandeggio e
0,5 s di sgancio di un missile) e RIV e' il **residuo** fino al totale documentato. Il
totale resta quindi esattamente quello della fonte; la ripartizione no. Serve lo stesso,
perche' le degradazioni future colpiscono una fase sola (meteo/notte/disturbo sulla RIV,
addestramento sulla VAL) e senza fasi separate andrebbero riscritte a posteriori.

Il risolutore oggi consuma solo due grandezze derivate: `total` (latenza del primo
ingaggio, dal rilevamento al lancio) e `refire_interval` (VAL+COM+ATT: fra una salva e la
successiva contro un bersaglio gia' in traccia non si rileva di nuovo).

## SKILL

`Context.SKILL` (Average/Good/High/Excellent, i livelli DCS) e' previsto dalla roadmap
come modulatore. **Nessuna fonte del progetto da' un fattore per livello**: i fattori
sono quindi tutti 1.0 (neutri) finche' l'utente non li decide o non vengono calibrati.
L'aggancio c'e' — `profile_for_asset(asset, skill=...)` — ma non cambia nulla.

## Convenzioni

- Tempi in **secondi**.
- Nessuna casualita': una latenza e' un dato, la varianza del combattimento sta altrove.
- Mai eccezioni per dati mancanti: un asset senza corrispondenza riceve il profilo di
  ripiego `DEFAULT_PROFILE_KEY`, con un log. Le eccezioni restano per argomenti fuori
  dominio (chiave di profilo inesistente, skill sconosciuto).
"""

from dataclasses import dataclass, replace
from typing import Dict, Optional

from Code.Dynamic_War_Manager.Source.Context.Context import SKILL, Ground_Vehicle_Asset_Type as gat
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger

# LOGGING --
logger = Logger(module_name=__name__, class_name='Reaction_Profile').logger


# ── ORDINI DI GRANDEZZA PER FASE (testo della Strategia 1, §2 del documento) ──

MACHINE_EVALUATION_S = 0.1      # VAL: "~100 ms per una macchina"
HUMAN_EVALUATION_S = 10.0       # VAL: "~10 s per un umano"
AUTOMATED_COMMAND_S = 0.001     # COM: "1 ms per un autopilota"
MANUAL_COMMAND_S = 1.0          # COM: "1 s per un pilota di carro WW2"
TURRET_ACTUATION_S = 0.1        # ATT: "0,1 s per la rotazione minima di una torretta"
MISSILE_ACTUATION_S = 0.5       # ATT: "0,5 s per lo sgancio di un missile"

# IADS (tabella §4.2): la valutazione della minaccia avviene "entro un aggiornamento radar
# (~1 s)" e l'assegnazione arma-bersaglio in "poche centinaia di ms" (qui 0,3 s). Per un
# sistema con posto comando di batteria/battaglione (S-300P) la VAL e' la loro somma.
IADS_THREAT_EVALUATION_S = 1.0
IADS_WEAPON_ASSIGNMENT_S = 0.3


@dataclass(frozen=True)
class ReactionProfile:
    """Latenze di reazione di un tipo di sistema, in secondi.

    Attributes:
        detection:  RIV — dal primo contatto geometrico alla traccia utilizzabile.
        evaluation: VAL — valutazione della minaccia e decisione di ingaggio.
        command:    COM — traduzione della decisione in comandi agli attuatori.
        actuation:  ATT — esecuzione (brandeggio, sgancio, uscita dalla rampa).
        source:     provenienza del profilo (testo libero, per la tracciabilita').
    """
    detection: float
    evaluation: float
    command: float
    actuation: float
    source: str = ''

    def __post_init__(self):
        for name in ('detection', 'evaluation', 'command', 'actuation'):
            value = getattr(self, name)

            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be a number, got {value!r}")

            if value < 0:
                raise ValueError(f"{name} must be non-negative, got {value!r}")

        # Un intervallo di tiro nullo farebbe sparare un asset infinite volte nello stesso
        # istante: il risolutore a eventi non terminerebbe.
        if self.evaluation + self.command + self.actuation <= 0:
            raise ValueError("evaluation + command + actuation must be positive "
                             "(it is the re-fire interval)")

    @property
    def total(self) -> float:
        """Latenza del primo ingaggio: dal contatto al lancio (RIV+VAL+COM+ATT)."""
        return self.detection + self.evaluation + self.command + self.actuation

    @property
    def refire_interval(self) -> float:
        """Intervallo fra due salve contro un bersaglio gia' in traccia (VAL+COM+ATT).

        La RIV non si ripete: la traccia e' gia' stabilita. Stima dichiarata, coerente con
        la decomposizione: e' il ciclo "valuta l'esito, decide, spara".
        """
        return self.evaluation + self.command + self.actuation

    def scaled(self, factor: float) -> 'ReactionProfile':
        """Copia con tutte le fasi moltiplicate per `factor` (> 0)."""
        if isinstance(factor, bool) or not isinstance(factor, (int, float)) or factor <= 0:
            raise ValueError(f"factor must be a positive number, got {factor!r}")

        if factor == 1:
            return self

        return replace(self,
                       detection=self.detection * factor,
                       evaluation=self.evaluation * factor,
                       command=self.command * factor,
                       actuation=self.actuation * factor)


def _from_total(total: float, evaluation: float, command: float, actuation: float,
                source: str) -> ReactionProfile:
    """Profilo con totale documentato: RIV = residuo (v. docstring del modulo)."""
    detection = total - (evaluation + command + actuation)

    if detection < 0:
        raise ValueError(f"documented total {total} smaller than VAL+COM+ATT")

    return ReactionProfile(detection=detection, evaluation=evaluation, command=command,
                           actuation=actuation, source=source)


# ── PROFILI ───────────────────────────────────────────────────────────────────
#
# Chiavi: il modello come compare nei registry (Vehicle_Data._registry) quando la fonte
# documenta proprio quel sistema; altrimenti un archetipo ('pilot', 'tank_crew').

PILOT = 'pilot'
TANK_CREW = 'tank_crew'
TOR_SHORT_STOP = '9K331-Tor/short_stop'
DEFAULT_PROFILE_KEY = 'default'

REACTION_PROFILES: Dict[str, ReactionProfile] = {
    # Sistemi autonomi (radar e direzione del tiro sullo stesso veicolo): VAL da macchina,
    # COM automatico, ATT di sgancio missile.
    '9A33-Osa': _from_total(26.0, MACHINE_EVALUATION_S, AUTOMATED_COMMAND_S, MISSILE_ACTUATION_S,
                            source='documented total 26 s (9K33 Osa); phase split estimated'),
    '9K331-Tor': _from_total(6.5, MACHINE_EVALUATION_S, AUTOMATED_COMMAND_S, MISSILE_ACTUATION_S,
                             source='documented total 5-8 s from standstill, midpoint; phase split estimated'),
    # Variante "short stop" del Tor-M2: stesso sistema, procedura diversa. Non e' associata
    # automaticamente a nessun modello (il registry non distingue la procedura): e'
    # disponibile a chi la richiede esplicitamente.
    TOR_SHORT_STOP: _from_total(2.5, MACHINE_EVALUATION_S, AUTOMATED_COMMAND_S, MISSILE_ACTUATION_S,
                                source='documented total 2-3 s (Tor-M2 short stop), midpoint; phase split estimated'),
    # Sistema con posto comando (IADS): la VAL e' valutazione minaccia + assegnazione.
    'S-300PS': _from_total(28.0, IADS_THREAT_EVALUATION_S + IADS_WEAPON_ASSIGNMENT_S,
                           AUTOMATED_COMMAND_S, MISSILE_ACTUATION_S,
                           source='documented total 28 s (S-300P); VAL from documented IADS figures; split estimated'),
    # Pilota: il dato documentato (1-2 s) e' un tempo di REAZIONE umana, non un tempo
    # rilevamento->lancio: non include l'aggancio del sensore. RIV = 0 perche' per un
    # aereo l'istante di rilevamento e' gia' quello stimato dal risolutore (Pd); VAL e' il
    # residuo del totale dopo COM automatico (catena di comando elettrica) e ATT di sgancio.
    PILOT: ReactionProfile(detection=0.0,
                           evaluation=1.5 - AUTOMATED_COMMAND_S - MISSILE_ACTUATION_S,
                           command=AUTOMATED_COMMAND_S,
                           actuation=MISSILE_ACTUATION_S,
                           source='documented human reaction 1-2 s, midpoint; RIV excluded; split estimated'),
    # Equipaggio carro: VAL umana, COM manuale, ATT di brandeggio.
    TANK_CREW: _from_total(31.0, HUMAN_EVALUATION_S, MANUAL_COMMAND_S, TURRET_ACTUATION_S,
                           source='documented total ~31 s per target (M1 gunnery, DTIC ADA217416); split estimated'),
    # Ripiego per i sistemi senza profilo: il PIU' LENTO dei totali documentati, con la
    # ripartizione dell'equipaggio carro. Scelta deliberata: la mancanza di un dato non
    # deve regalare l'iniziativa (stessa logica di [[feedback_no_visibility_low_priority]]:
    # l'ignoto non alza la priorita', qui non accorcia la reazione).
    DEFAULT_PROFILE_KEY: _from_total(31.0, HUMAN_EVALUATION_S, MANUAL_COMMAND_S, TURRET_ACTUATION_S,
                                     source='fallback: slowest documented total (31 s); split estimated'),
}

# Fattore moltiplicativo delle latenze per livello di addestramento. TUTTI NEUTRI: nessuna
# fonte del progetto li fornisce (v. docstring del modulo, sezione SKILL).
SKILL_LATENCY_FACTOR: Dict[str, float] = {skill.value: 1.0 for skill in SKILL}

# Categorie di veicolo servite dal profilo dell'equipaggio carro: e' l'unico sistema
# terrestre con equipaggio documentato; motorizzati e artiglieria lo riusano come il
# sistema documentato piu' vicino (stima dichiarata).
_CREWED_GROUND_TYPES = {gat.TANK.value, gat.ARMORED.value, gat.MOTORIZED.value,
                        gat.ARTILLERY_FIXED.value, gat.ARTILLERY_SEMOVENT.value}
_SAM_TYPES = {gat.SAM_BIG.value, gat.SAM_MEDIUM.value, gat.SAM_SMALL.value}
_AAA_TYPES = {gat.AAA.value}


def reaction_profile(key: str) -> ReactionProfile:
    """Profilo per chiave esplicita (modello di registry o archetipo).

    Raises:
        KeyError: chiave sconosciuta — qui la chiave la sceglie il programmatore, non i dati.
    """
    if key not in REACTION_PROFILES:
        raise KeyError(f"unknown reaction profile {key!r}; known: {sorted(REACTION_PROFILES)}")

    return REACTION_PROFILES[key]


def _skill_factor(skill) -> float:
    if skill is None:
        return 1.0

    value = getattr(skill, 'value', skill)

    if value not in SKILL_LATENCY_FACTOR:
        raise ValueError(f"skill must be one of {sorted(SKILL_LATENCY_FACTOR)}, got {skill!r}")

    return SKILL_LATENCY_FACTOR[value]


def _air_defense_profile(asset, has_missiles: bool) -> ReactionProfile:
    """Profilo di un sistema AD non documentato qui, dalla fabbrica ThreatAA esistente.

    `Logic/Air_Route_Manager.threat_reaction_times` fornisce gia' (min_detection_time,
    min_fire_time) per ogni asset AD — il primo dalla tabella minacce SAM ricercata o da
    una stima per classe, il secondo da una stima per tipo di lanciatore — ed e' cio' che
    la pianificazione di rotta usa per la STESSA minaccia. Riusarlo qui evita due verita'
    diverse sulla reattivita' dello stesso sito: RIV = min_detection_time, ATT =
    min_fire_time, VAL e COM da sistema automatico. Import locale: Context non deve
    dipendere da Logic a tempo di import.
    """
    from Code.Dynamic_War_Manager.Source.Logic.Air_Route_Manager import threat_reaction_times

    detection_time, fire_time = threat_reaction_times(asset, has_missiles=has_missiles)

    return ReactionProfile(detection=float(detection_time),
                           evaluation=MACHINE_EVALUATION_S,
                           command=AUTOMATED_COMMAND_S,
                           actuation=float(fire_time),
                           source='Air_Route_Manager.threat_reaction_times (declared estimates there)')


def profile_for_asset(asset, skill=None) -> ReactionProfile:
    """Profilo di reazione di un asset reale.

    Precedenza:
      1. modello con profilo documentato (REACTION_PROFILES[asset._model]);
      2. Aircraft -> PILOT;
      3. Vehicle SAM/AAA -> dalla fabbrica ThreatAA (v. _air_defense_profile);
      4. Vehicle con equipaggio (carri, corazzati, motorizzati, artiglieria) -> TANK_CREW;
      5. tutto il resto (navi, EWR, classi non riconosciute) -> DEFAULT_PROFILE_KEY, con
         un log: nessuna fonte del progetto documenta latenze navali.

    La classe e' riconosciuta dal NOME (come Context.classify_asset_dimension): Vehicle,
    Ship e Aircraft non sono importabili qui per il ciclo d'import noto del progetto. Il
    tipo e' cercato sia in `asset_type` sia in `category`, perche' i registry di veicoli
    usano la categoria granulare (es. 'SAM_Small') e le istanze la classe generale.

    Args:
        skill: membro o valore di `Context.SKILL`, oppure None. Oggi neutro (fattori 1.0).
    """
    factor = _skill_factor(skill)

    model = getattr(asset, '_model', None)

    if model in REACTION_PROFILES:
        return REACTION_PROFILES[model].scaled(factor)

    class_name = asset.__class__.__name__

    if class_name == 'Aircraft':
        return REACTION_PROFILES[PILOT].scaled(factor)

    if class_name == 'Vehicle':
        kinds = {getattr(asset, 'asset_type', None), getattr(asset, 'category', None)}

        if kinds & _SAM_TYPES:
            return _air_defense_profile(asset, has_missiles=True).scaled(factor)

        if kinds & _AAA_TYPES:
            return _air_defense_profile(asset, has_missiles=False).scaled(factor)

        if kinds & _CREWED_GROUND_TYPES:
            return REACTION_PROFILES[TANK_CREW].scaled(factor)

    logger.debug(f"profile_for_asset: no reaction profile for {class_name} model {model!r}, "
                 f"using {DEFAULT_PROFILE_KEY!r}")

    return REACTION_PROFILES[DEFAULT_PROFILE_KEY].scaled(factor)


def reaction_delay(asset, skill=None) -> float:
    """Latenza [s] fra il rilevamento e il primo lancio di `asset` (profile.total)."""
    return profile_for_asset(asset, skill=skill).total
