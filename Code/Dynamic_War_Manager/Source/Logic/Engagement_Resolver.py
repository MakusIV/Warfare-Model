"""Risolutore d'ingaggio — **chi rileva, chi spara per primo, con che esito**.

FASE 4 del motore di sessioni virtuali (strato 2 dell'architettura DES, v.
`Analysis/Document/Architettura_esecuzione_sessioni_virtuali_ANALISI.md` §6 e
[[project_virtual_session_engine_design]]).

Lo strato 1 (`Logic/Contact_Scheduler.py`) risponde a **quando** due forze si incontrano,
con sola geometria. Questo modulo consuma le sue `ContactWindow` e risponde a **come
finisce**: e' il primo punto del motore in cui entra la casualita', sempre e solo
attraverso l'RNG di sessione passato dal chiamante.

## La catena, per ogni ingaggio (due o piu' forze, v. "Ingaggi a N forze")

1. **Pd — chi rileva davvero.** La finestra di contatto dice che l'osservatore *potrebbe*
   vedere il bersaglio; se lo vede lo decide un'estrazione contro
   `detection_probability(d_cpa, portata)`. Una sola estrazione per coppia e direzione
   decide sia *se* sia *a che distanza* avviene il rilevamento (v. `detection_radius`), e
   quindi *quando*: l'istante e' ricavato analiticamente con
   `Contact_Scheduler.range_intervals` quando il chiamante fornisce i tratti delle rotte.
2. **Latenza di reazione — chi spara per primo.** Dal rilevamento al primo lancio passa
   `ReactionProfile.total` (RIV+VAL+COM+ATT, `Context/Reaction_Profile.py`); le salve
   successive sono separate da `refire_interval`. E' la parte salvata della "Strategia 1":
   l'iniziativa, che i modelli a rapporto di forze non sanno rappresentare.
3. **Dottrina di fuoco / ROE — se e con cosa si spara.** Iniettata: `fire_control(shooter,
   target)` restituisce una `ShotSpec` (accuracy, destroy_capacity, colpi per salva, tempo
   di volo, intercettabilita'), una SEQUENZA di `ShotSpec` in ordine di preferenza, oppure
   None (non ingaggia: ROE, arma inadatta). Con una sequenza il tiratore spara con la prima
   opzione la cui arma ha ancora scorta nello stato ombra (v. "Scorta per arma").
4. **Salva e saturazione (Hughes, R1).** I colpi che arrivano su una forza nello stesso
   evento-salva sono prima confrontati con la capacita' di intercettazione del bersaglio
   (`Military.salvo_interceptors`): i primi N intercettabili sono fermati e non
   raggiungono mai il modello di danno, il surplus lo raggiunge integralmente. Ogni
   intercettazione consuma la scorta di INTERCETTORI dell'asset che intercetta
   (`Mobile.interceptor_stock`) ed e' registrata come `InterceptionEvent`, un tipo
   distinto dall'`AmmunitionEvent` delle salve offensive (`Mobile.ammunition`): due
   contatori distinti, v. Mobile.ROUNDS_PER_GUN_INTERCEPT (ricalibrazione 2026-09-23 —
   prima si leggeva `ammunition`, e un cannone AA con 2000 colpi poteva intercettare 2000
   colpi in arrivo). Dal 2026-09-26 entrambe le scorte sono viste sulla scorta PER ARMA
   (v. "Scorta per arma"): un missile AD che intercetta e' lo stesso della salva offensiva.
   Dal 2026-09-28 (Proposta_Regole_Allocazione_SAM.md §7) intercetta solo un asset con armi
   dichiarate 'Anti_Missile' (regola D, v. Military.salvo_interceptors), prima quelli a soli
   cannoni (regola F), e l'allocazione e' PER SALVA (regola L1): un colpo e' intercettabile
   da un intercettore solo se il punto di lancio della salva e' fuori dal suo volume
   d'intercettazione V_I (`Mobile.air_defense_volume`, posizioni all'istante del lancio). Il
   lanciatore che spara da dentro la zona e' un bersaglio: i suoi colpi non si intercettano.
   Dal 2026-09-30 (regola R-INT, Proposta_Intercettazione_Reazione.md) l'intercettore deve
   anche avere una traccia del colpo e il tempo di reagire prima dell'impatto: se aveva gia'
   rilevato il lanciatore vede il lancio e reagisce in VAL+COM+ATT, altrimenti scopre il colpo
   quando entra nel suo raggio di rilevamento aereo (traiettoria rettilinea, deterministico:
   nessuna estrazione) e reagisce in RIV+VAL+COM+ATT. Rilevamento per asset; tempo di volo
   dell'intercettore e RCS del colpo non modellati. Un colpo con tempo di volo nullo non si
   intercetta mai.
5. **Danno per singolo colpo.** Ogni colpo superstite passa da
   `Damage_Model.build_damage_event` (che chiama `resolve_hit`), con un `draw` estratto
   qui dall'RNG iniettato. Nessuna reimplementazione del contratto del danno.
6. **Disingaggio (P1 + R2).** Dopo ogni evento-salva la forza colpita confronta le proprie
   perdite con la dottrina di lato (`Context/Doctrine.get_disengagement_thresholds`):
   erosione cumulata *oppure* shock della singola salva, qualunque scatti per primo, con la
   soglia di rottura propria della forza (v. "Soglia di rottura", dal 2026-09-29). Se
   scatta, **tutta la forza** rompe il contatto: esito `DISENGAGED`, distinto da
   `DESTROYED` (nessun asset impegnato ancora operativo).

   **Solo le forze militari possono disingaggiarsi** (decisione di progetto 2026-09-23).
   Un `Block` che non e' una `Military` (Transport, Storage, Urban, Production, o un
   `Block` generico con `category` 'Logistic'/'Civilian') e' un deposito, una linea di
   trasporto, un'area abitata: non puo' fisicamente rompere il contatto e ripiegare. Riceve
   quindi `thresholds=None` incondizionatamente — la stessa rappresentazione di "combatte
   fino alla fine" gia' usata per un lato senza dottrina — qualunque cosa dica la tabella
   dottrinale per il suo lato, e senza il warning di dottrina mancante (non manca nulla).
   Esiti possibili: `HELD` finche' ha asset operativi, `DESTROYED` se li perde tutti.
   Il controllo e' sulla gerarchia di classe (`validate_class`), non su un campo testuale
   come `category`. Un oggetto che non e' affatto un `Block` (stub duck-typed nei test,
   adapter futuri) resta trattato come una forza combattente: legge la dottrina di lato.

## Soglia di rottura (2026-09-29, decisioni D1-D9 e D4a-D4e)

`Analysis/Document/Proposta_Soglia_Rottura_Stocastica.md`. Con soglie fisse la perdita
minima 1/n faceva scattare il disingaggio alla prima perdita per le forze piccole (S1: 5
carri si ritiravano per un carro in 7 repliche su 8). Ora la soglia di erosione e' la soglia
di rottura B(t) della forza, con mediana `erosion` e parametri di `Context/Doctrine`:

* **tempra**: un quantile `u` estratto UNA volta per forza e per ingaggio, dal flusso
  separato `breakpoint_rng` (in sessione `SessionOrder.rng(event_id=temper_event_id(...))`):
  le estrazioni di rilevamento e danno di `rng` restano quelle di prima. Senza flusso
  dedicato la tempra non si estrae e B(t) sta alla mediana modulata;
* **morale** (`morale_for`, None = neutro), **rapporto di forze percepito** rho(t) dai
  nemici rilevati entro t (`seen_by`) e dalla stima a priori (`enemy_estimate_for`),
  **fuoco senza risposta** (perdite causate da tiratori non ancora rilevati: `loss_shooters`),
  **postura** (forza con tutti i tratti di rotta fermi);
* percezione dei nemici: rilevamento dei propri sensori, oppure (forza aerea) RWR — un asset
  AD che emette e illumina un aereo il cui RWR ne riconosce la categoria SAM
  (`Air_Defense_Efficacy.rwr_perception`, dati in `Asset/Aircraft_Rwr_Data`) e' percepito dalla
  forza dell'aereo: dal rilevamento se l'RWR rileva la ricerca, dal lancio se rileva solo
  tracciamento/guida (SPO-10); conta nel rapporto e rende "con risposta" le perdite che causa;
* rho(t) per una forza AEREA (tutti gli asset impegnati sono aerei): aerei propri operativi /
  (air_force_ratio_scale x minaccia), con minaccia = somma di `Air_Defense_Efficacy.air_threat_weight`
  dei nemici percepiti (E(N) degli asset AD con la scorta di DOTAZIONE stimata, perche' chi
  osserva non conosce quella residua; 1 per i caccia);
  per una forza di SUPERFICIE: somma dei `surface_threat_weight` propri / nemici (SAM puri 0).
  Nemici distrutti esclusi, danneggiati inclusi. Rapporto non definito -> neutro;
* **shock**: soglia (shock / erosion) x B(t), e solo se la salva ha tolto almeno
  `shock_min_losses` asset.

B(t) e' ricalcolata a ogni risoluzione di salva contro la forza. Una tabella con le sole
`erosion`/`shock` (chiavi facoltative ai valori neutri) riproduce esattamente le soglie
fisse precedenti; `erosion` = 1 resta "combatte fino all'annientamento".

## Controllo di portata (2026-09-24, decisione utente)

Prima di questa data il tiro partiva al primo istante utile dopo rilevamento + latenza,
qualunque fosse la distanza: una fire control che restituiva un'arma da 20 km faceva
sparare un aereo rilevato a 60 km. Ora `ShotSpec.max_range` [m] (opzionale) vincola il
LANCIO: la salva parte solo quando la distanza 3D tiratore-bersaglio e' <= max_range.

* **Ingresso in portata piu' tardi nella finestra**: il candidato e' rimandato
  (`_Candidate.not_before`) all'istante di ingresso, calcolato analiticamente in
  `engagement_intervals` (sfera di raggio max_range, `Contact_Scheduler.range_intervals`;
  funzione isolata e sostituibile, primo caso dei futuri volumi d'ingaggio) sui tratti delle rotte (gli stessi
  che gia' danno l'istante di rilevamento; `Session_Simulator` li passa sempre, statici per
  gli asset fermi). La scelta del bersaglio si ripete: un tiratore pronto spara intanto a
  un altro bersaglio gia' in portata, se ce n'e' uno.
* **Mai in portata nella finestra**: il candidato e' esaurito, come per un None della fire
  control ma solo per quella coppia/finestra.
* **Senza tratti di rotta** (chiamata diretta a `resolve_engagement` senza `legs`): la
  distanza nel tempo non e' ricostruibile dalla sola `ContactWindow`, che porta solo il
  massimo avvicinamento. Ripiego dichiarato: `distance_cpa > max_range` -> mai in portata;
  altrimenti il tiro non parte prima di `t_cpa`. Il contratto di `ContactWindow` non e'
  stato allargato: il percorso di sessione ha sempre i tratti ed e' esatto.
* **R4**: la portata e' valutata allo scheduling; il payload resta congelato al lancio, che
  avviene all'istante di ingresso gia' calcolato. Il controllo non estrae numeri casuali:
  l'ordine delle estrazioni RNG e' invariato, e con `max_range=None` il percorso di codice
  e' identico a quello precedente.

## Scorta per arma (decisione A1/A3, 2026-09-26)

Fino al 2026-09-26 lo stato ombra copiava lo scalare aggregato `Mobile.ammunition` e ogni
salva lo scalava, qualunque arma la fire control avesse scelto: l'arma non consumava mai
la propria scorta (un A-10 con 4 AGM-65D ne lanciava 642, pagati dai colpi del cannone).
Ora `_Shadow` porta una COPIA di `Mobile.stores` e la contabilita' e' quella di
`Asset/Weapon_Stores.py`, la stessa dell'asset reale:

* allo scheduling si prende la PRIMA opzione della fire control la cui arma ha scorta per
  almeno un colpo (`stock // stock_per_round >= 1`); se nessuna ne ha, il candidato e'
  esaurito come per un None. I colpi sono `min(spec.rounds, stock // stock_per_round)`;
* al lancio si scalano `rounds x stock_per_round` unita' dalla voce di quell'arma
  (`ShotSpec.stock_per_round`: 1, o i colpi di una raffica per le armi a tiro rapido);
  l'`AmmunitionEvent` porta l'arma e le UNITA' DI SCORTA consumate;
* le intercettazioni scalano le voci AD (cannoni prima, poi missili: regola F), un
  `InterceptionEvent` per arma;
* il tiratore smette di sparare quando nessuna arma ha piu' scorta (le armi non modellate,
  contate a unita' nei registri, non hanno vincolo);
* uno stub senza `stores` (pool anonimo `ammunition`) resta al comportamento precedente.

La scelta resta deterministica: dipende solo dallo stato della coda, come la ripartizione
del fuoco. Limite dichiarato: la scelta per scorta precede il controllo di portata; se
l'opzione con scorta e' fuori portata il candidato e' rimandato o esaurito anche se
un'opzione successiva sarebbe gia' in portata.

## Ingaggi a N forze (2+)

`resolve_engagement(force_a, force_b, ..., extra_forces=(...))` risolve in UNA run, con UNA
coda eventi condivisa, tutte le forze `(force_a, force_b, *extra_forces)`, trattate in modo
uniforme. Chi puo' combattere contro chi lo dicono solo le finestre di contatto passate
(ogni finestra fra asset di due forze diverse genera le due direzioni di rilevamento); il
lato (`side`) serve solo a leggere la dottrina, e piu' forze possono condividerlo.

Perche' serve (caso che ha originato la generalizzazione, 2026-09-23): la forza X e' in
contatto con A e con B in finestre sovrapposte. Risolvendo (X,A) e (X,B) con due chiamate
separate, la prima veniva svolta fino in fondo e applicata, e la seconda leggeva uno stato
di X gia' consumato anche per la parte di tempo in cui X combatteva su entrambi i fronti:
l'ordine delle chiamate decideva chi "arrivava prima" a salute e scorte di X. In una sola
run la salute e le scorte ombra di X evolvono in un'unica timeline, consumata da entrambi i
fronti nell'ordine esatto degli eventi. Con `extra_forces=()` il comportamento e' identico
a quello dell'ingaggio a due.

Nulla nel resto della catena assume due forze: rilevamento (stesso `force_id` -> ignorata),
saturazione e danno (chiavati sulla forza bersaglio), soglie (per lato), esito (per forza,
nell'ordine di ingresso) erano gia' generali. L'unico punto che non lo era e' il contatto
rotto, qui sotto.

## Forze rotte: per-forza, non un flag globale

Una forza che raggiunge DESTROYED o DISENGAGED entra in `broken_forces`. Da quel momento:
- nessun suo tiratore riceve un NUOVO lancio, e i suoi lanci schedulati e non ancora
  eseguiti sono annullati;
- nessun tiratore di altre forze puo' piu' sceglierla come bersaglio (un bersaglio
  disingaggiato e' vivo ma "andato via"); un lancio gia' schedulato contro di essa e'
  annullato e il tiratore decide di nuovo, eventualmente contro un'altra forza;
- le salve GIA' partite, da o verso di essa, arrivano comunque (payload congelato, R4).

Fino all'introduzione delle N forze il contatto rotto era un flag unico della run: appena
una delle due forze rompeva, ogni lancio si fermava. Con due forze le due formulazioni
coincidono — se una forza e' rotta, l'altra non ha piu' bersagli ingaggiabili e smette di
sparare per conseguenza naturale. Con N forze il flag globale sarebbe sbagliato: nello
scenario X/A/B, il disingaggio di X non deve fermare il fronte A-B, se esiste. Il ciclo
eventi finisce sempre e solo quando la coda si svuota.

## Vincoli di progetto rispettati

- **Congelamento del payload (R4, prima parte).** Il bersaglio, la `ShotSpec` e il numero
  di colpi sono fissati quando il lancio viene schedulato e, una volta che la salva e'
  partita, nessun evento successivo li modifica — nemmeno la distruzione del lanciatore:
  una salva in volo arriva comunque. Prima del lancio un evento programmato puo' solo
  essere *annullato* (lanciatore fuori combattimento, bersaglio gia' fuori combattimento
  o uscito dalla finestra, scorte insufficienti, contatto rotto), mai *riscritto*: la
  decisione successiva e' un nuovo evento con un nuovo payload.
- **Re-scheduling delle finestre NON implementato (R4, seconda parte, rimandato).** Una
  forza che si disingaggia e' solo *segnalata* nell'esito; il nuovo instradamento e il
  ricalcolo delle finestre di contatto spettano a un livello superiore (C2/campagna).
- **Il risolutore non muta gli asset.** Lavora su uno stato ombra (salute, scorte) che
  evolve durante l'ingaggio e restituisce gli eventi (`DamageEvent`, `AmmunitionEvent`,
  `InterceptionEvent`) in un `EngagementResult` immutabile. Applicarli e' un passo separato ed esplicito
  (`apply_engagement_result`): e' la separazione calcolo/applicazione gia' scelta da
  `Damage_Model` (build vs apply) e l'"applicazione in un'unica passata" dello strato 3.
- **RNG sempre iniettato**: un oggetto con `.random()` in [0, 1) — tipicamente
  `random.Random(seed)` creato dal chiamante. Mai `random` di modulo.
- **L'ordine delle estrazioni fa parte del contratto**: prima tutte le estrazioni di
  rilevamento, nell'ordine canonico delle finestre `(t_start, id_a, id_b, t_end)` e per
  ognuna la direzione a->b poi b->a; poi un'estrazione per colpo non intercettato, nell'
  ordine degli eventi. Coda eventi con tie-break deterministico `(t, tipo, id, sequenza)`,
  tipi nell'ordine LANCIO < IMPATTO < RISOLUZIONE: a parita' di istante tutti i lanci
  leggono lo stato *prima* dei danni (risoluzione simultanea, §4.4 del documento).
- **Mai eccezioni per dati mancanti** (forza senza asset utilizzabili, asset senza salute
  leggibile, lato senza soglie dottrinali): None/lista vuota/politica dichiarata + log.
  Le eccezioni restano per gli argomenti fuori dominio.
- **Nessun componente LLM**, in nessuna forma.

## Cosa NON fa (ancora)

- Non seleziona l'arma dai registri: `fire_control` e' iniettata. Una fire control che
  la seleziona dai registri esiste (`Logic/Fire_Control.make_registry_fire_control`, B2
  2026-09-24); la modulazione della Pk con la posizione nell'inviluppo resta da fare.
- Dal 2026-09-29 non spreca piu' salve su bersagli gia' condannati (v. "Dottrina di tiro"
  in `_schedule_next`): prima un tiratore poteva spendere tutta la scorta di un'arma prima
  del primo impatto, e tiratori diversi della stessa forza si sommavano sullo stesso bersaglio.
- La portata dell'arma e' un vincolo solo se la `ShotSpec` la dichiara (`max_range`, v.
  "Controllo di portata"); il resto dell'inviluppo (quota) e' materia della fire control.
  Una salva gia' lanciata arriva comunque (R4), anche se il bersaglio esce di portata
  durante il volo.
- Non applica il meteo da se': la degradazione di Pd resta un fattore iniettato
  (`detection_factor`, 1.0 di default). Il collegamento con `Meteo_Analysis` e' una
  fabbrica di quel fattore (`meteo_detection_factor`/`weather_detection_factor_fn`), che
  il chiamante passa esplicitamente; il fattore non distingue ancora radar da ottico.
- Non applica la nebbia di guerra da se': anch'essa e' una fabbrica dello stesso fattore
  (`recon_detection_factor_fn`, `region_recon_detection_factor`, attivita' C 2026-09-25),
  costruita su un'istantanea di ricognizione presa PRIMA della sessione e combinabile col
  meteo (`combine_detection_factors`). Nessuna nebbia dinamica: la ricognizione non
  evolve durante l'ingaggio e il fattore non consuma l'RNG.
- Ripartisce il fuoco fra i tiratori di una forza solo con una regola greedy locale
  (round-robin, v. `_EngagementRun._schedule_next`), non con un'assegnazione ottima.
- Non tocca `Logic/Tactical_Evaluation.calcFightResult` (fallback aggregato, invariato).
"""

import heapq
import math
from collections import abc
from statistics import NormalDist
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from Code.Dynamic_War_Manager.Source.Asset import Weapon_Stores as WS
from Code.Dynamic_War_Manager.Source.Context import Air_Defense_Efficacy as ADE
from Code.Dynamic_War_Manager.Source.Context import Doctrine
from Code.Dynamic_War_Manager.Source.Context import Reaction_Profile as RP
from Code.Dynamic_War_Manager.Source.DataType.State import HEALTH_LEVEL, StateCategory
from Code.Dynamic_War_Manager.Source.Logic import Damage_Model as DM
from Code.Dynamic_War_Manager.Source.Logic.Contact_Scheduler import TIME_EPS, position_on_legs, range_intervals
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.Utility.Utility import validate_class

# LOGGING --
logger = Logger(module_name=__name__, class_name='Engagement_Resolver').logger


# ── COSTANTI ──────────────────────────────────────────────────────────────────

# Pd sul bordo della portata di acquisizione. STIMA DICHIARATA: delle due convenzioni con
# cui si dichiara la portata di un radar (Pd 0.5 o 0.9 a quella distanza) si adotta la piu'
# prudente. Da ricalibrare.
PD_AT_ACQUISITION_RANGE = 0.5

# Esponente della distanza nella legge di Pd: e' la dipendenza R^4 dell'equazione radar
# (SNR proporzionale a 1/R^4, §4.6 del documento). La FORMA viene dalla fisica, la curva
# Pd(SNR) reale (Swerling) e' sigmoide: questa legge ne e' una semplificazione monotona.
PD_RANGE_EXPONENT = 4

# Degradazione ambientale della Pd (v. weather_detection_factor), moltiplicativa.
# STIMA DICHIARATA, nessuna fonte del progetto la fornisce; da ricalibrare via ATCAL interno.
# - Notte: un sensore ottico a occhio nudo perde quasi tutto, un visore/FLIR parte, un radar
#   nulla. Il fattore e' UNICO per tutti i sensori (il risolutore non sa quale sensore ha
#   prodotto la portata della finestra): 0.7 e' un compromesso dichiarato fra "radar, 1.0"
#   e "ottico, molto meno", pesato verso il radar perche' le portate maggiori — quelle che
#   la finestra riporta — sono in genere radar.
# - Meteo avverso: degrada tutti i sensori (l'ottico per visibilita', il radar per
#   attenuazione e clutter da precipitazione), in misura minore della notte sull'ottico
#   ma senza risparmiare il radar: 0.8.
# Notte + meteo avverso = 0.56.
NIGHT_DETECTION_FACTOR = 0.7
ADVERSE_WEATHER_DETECTION_FACTOR = 0.8

# Nebbia di guerra (v. recon_detection_factor_fn / region_recon_detection_factor),
# moltiplicativa come il meteo. STIME DICHIARATE, nessuna fonte del progetto le fornisce;
# da ricalibrare via ATCAL interno.
# - UNSEEN_DETECTION_FACTOR: Pd di un bersaglio il cui blocco NON e' nell'istantanea di
#   ricognizione dell'osservatore, con ricognizione nulla. 0.5 = "il sensore deve scoprirlo
#   da se', senza cueing": dimezza la Pd senza accecare (un sensore attivo resta un
#   sensore; la cecita' totale e' gia' esprimibile con un fattore 0.0 esplicito).
# - RECON_EFFICIENCY_FOG_RELIEF: quota massima della penalita' (seen - unseen) che una
#   ricognizione di efficienza 1.0 recupera. 0.5 = anche la ricognizione migliore non
#   rende un blocco NON confermato equivalente a uno confermato (l'istantanea dice che la
#   ricognizione non l'ha visto), ma ne dimezza lo svantaggio. Formula in
#   `recon_unseen_factor`.
UNSEEN_DETECTION_FACTOR = 0.5
RECON_EFFICIENCY_FOG_RELIEF = 0.5

# Una forza e' "operativa" per l'asset con salute sopra questa soglia: e' la stessa
# frontiera di State.isOperative (sotto il 50% l'asset e' Critical, fuori combattimento).
OPERATIVE_HEALTH_FLOOR = int(round(DM.HEALTH_MAX * HEALTH_LEVEL[StateCategory.CRITICAL.value]))

# Tolleranza nei confronti fra frazioni di perdita e soglie dottrinali: 3/10 deve valere
# 0.30 anche con l'aritmetica in virgola mobile.
FRACTION_EPS = 1e-9

# Soglia di rottura (2026-09-29): limiti del quantile della tempra (Phi^-1 finito) e
# tolleranza [m] per dire "fermo" un tratto di rotta.
BREAKPOINT_U_EPS = 1e-9
STATIONARY_EPS = 1e-6

# Esiti di forza.
HELD = 'held'                  # ancora in contatto a fine ingaggio (o nessuno ha rotto)
DISENGAGED = 'disengaged'      # ha rotto il contatto per soglia dottrinale (P1/R2)
DESTROYED = 'destroyed'        # nessun asset impegnato e' piu' operativo
FORCE_OUTCOMES = (HELD, DISENGAGED, DESTROYED)

# Motivi del cambio di esito.
TRIGGER_EROSION = Doctrine.DISENGAGEMENT_EROSION
TRIGGER_SHOCK = Doctrine.DISENGAGEMENT_SHOCK
TRIGGER_ANNIHILATION = 'annihilation'

# Tipi di evento, nell'ordine di risoluzione a parita' di istante (v. docstring).
_LAUNCH = 0
_IMPACT = 1
_RESOLVE = 2
# Ridecisione dopo la prelazione (regola L3, 2026-09-28): ultima a parita' d'istante, cosi' che
# la decisione veda tutti i lanci avvenuti in quell'istante.
_DECIDE = 3


# ── TIPI DI SCAMBIO ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ShotSpec:
    """Cosa spara un tiratore contro un bersaglio: prodotta dalla `fire_control` iniettata.

    Attributes:
        accuracy/destroy_capacity: Ph e Pk|h dal registro d'arma, [0, 1] (contratto di
            `Damage_Model`).
        rounds: colpi lanciati per salva (>= 1).
        weapon: modello d'arma di dominio, per la tracciabilita' dei DamageEvent.
        time_of_flight: secondi fra lancio e impatto (>= 0). Con 0 l'impatto e' nello
            stesso istante del lancio, ma risolto DOPO tutti i lanci di quell'istante.
        interceptable: True se i colpi possono essere intercettati dalla difesa del
            bersaglio (missili, bombe guidate); False per i proiettili d'artiglieria o di
            carro. La decide chi conosce l'arma (il chiamante), non il risolutore.
        cycle_time: intervallo fra due salve del tiratore; None = `refire_interval` del
            suo profilo di reazione.
        max_range: portata massima dell'arma [m], distanza tiratore-bersaglio (3D) oltre la
            quale la salva non parte (v. "Controllo di portata"); None = nessun vincolo di
            portata, comportamento precedente al 2026-09-24.
        stock_per_round: unita' di scorta dell'arma consumate da UN colpo della salva
            (>= 1, decisione A3 2026-09-26): 1 per missili, bombe e proietti singoli; i
            colpi di una raffica per le armi a tiro rapido, il cui "colpo" e' una raffica.
    """
    accuracy: float
    destroy_capacity: float
    rounds: int = 1
    weapon: Optional[str] = None
    time_of_flight: float = 0.0
    interceptable: bool = False
    cycle_time: Optional[float] = None
    max_range: Optional[float] = None
    stock_per_round: int = 1

    def __post_init__(self):
        for name in ('accuracy', 'destroy_capacity'):
            value = getattr(self, name)

            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be a number, got {value!r}")

            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0, 1], got {value!r}")

        if isinstance(self.rounds, bool) or not isinstance(self.rounds, int) or self.rounds < 1:
            raise ValueError(f"rounds must be an int >= 1, got {self.rounds!r}")

        if isinstance(self.time_of_flight, bool) or not isinstance(self.time_of_flight, (int, float)) \
                or self.time_of_flight < 0:
            raise ValueError(f"time_of_flight must be a non-negative number, got {self.time_of_flight!r}")

        if self.cycle_time is not None and (isinstance(self.cycle_time, bool)
                                            or not isinstance(self.cycle_time, (int, float))
                                            or self.cycle_time <= 0):
            raise ValueError(f"cycle_time must be None or a positive number, got {self.cycle_time!r}")

        if self.max_range is not None and (isinstance(self.max_range, bool)
                                           or not isinstance(self.max_range, (int, float))
                                           or self.max_range <= 0):
            raise ValueError(f"max_range must be None or a positive number, got {self.max_range!r}")

        if isinstance(self.stock_per_round, bool) or not isinstance(self.stock_per_round, int) \
                or self.stock_per_round < 1:
            raise ValueError(f"stock_per_round must be an int >= 1, got {self.stock_per_round!r}")


@dataclass(frozen=True)
class Detection:
    """Esito di un'estrazione di rilevamento (una per finestra e direzione).

    `time` e' l'istante del rilevamento (None se non rilevato); `probability` e' la Pd
    al massimo avvicinamento, `draw` il numero estratto.
    """
    observer_id: str
    target_id: str
    sensor_range: float
    distance_cpa: float
    probability: float
    draw: float
    detected: bool
    time: Optional[float] = None


@dataclass(frozen=True)
class Salvo:
    """Una salva lanciata: il suo payload e' CONGELATO (R4).

    Attributes:
        salvo_id: progressivo di lancio nell'ingaggio (ordine deterministico).
        t_launch/t_impact: secondi assoluti.
        shooter_id/target_id/target_force_id: id di dominio.
        rounds: colpi effettivamente lanciati (gia' limitati dalla scorta al momento della
            schedulazione).
        spec: la ShotSpec usata.
    """
    salvo_id: int
    t_launch: float
    t_impact: float
    shooter_id: str
    target_id: str
    target_force_id: str
    rounds: int
    spec: ShotSpec


@dataclass(frozen=True)
class SalvoResolution:
    """Un evento-salva risolto contro una forza: l'unita' di saturazione (R1) e di shock (R2).

    Attributes:
        time: istante di risoluzione.
        force_id: forza colpita.
        salvo_ids: salve che compongono l'evento.
        rounds: colpi in arrivo; interceptable_rounds: di cui intercettabili.
        capacity: capacita' di intercettazione disponibile all'istante: un TETTO (dal
            2026-09-28, regola L1, non tutti gli intercettori possono fermare ogni salva).
        intercepted: colpi fermati, <= min(interceptable_rounds, capacity); coincide col
            minimo quando la regola L1 non esclude nessun intercettore.
        wasted: colpi arrivati su bersagli gia' distrutti (nessuna estrazione).
        losses: asset impegnati passati da operativi a non operativi in questo evento.
        shock/erosion: frazioni dell'organico impegnato, v. Context/Doctrine.
    """
    time: float
    force_id: str
    salvo_ids: Tuple[int, ...]
    rounds: int
    interceptable_rounds: int
    capacity: int
    intercepted: int
    wasted: int
    losses: Tuple[str, ...]
    shock: float
    erosion: float


@dataclass(frozen=True)
class AmmunitionEvent:
    """Consumo esplicito di munizioni OFFENSIVE (R3): `rounds` unita' di scorta consumate da
    `asset_id` in una salva lanciata all'istante `time`. Si applica con
    `Mobile.consume_ammunition(rounds, weapon=weapon)`.

    Dal 2026-09-26 (A1/A3): `weapon` e' il modello d'arma della salva (None se la fire
    control non lo dichiara: paga l'aggregato, v. Asset/Weapon_Stores.py), e `rounds` sono
    UNITA' DI SCORTA, cioe' colpi della salva x `ShotSpec.stock_per_round` (per le armi a
    raffica i colpi sparati, non le raffiche; per tutte le altre coincidono con i colpi
    della salva, `Salvo.rounds`).

    Solo fuoco offensivo: le intercettazioni hanno il proprio tipo, `InterceptionEvent`
    (2026-09-23). Fino ad allora entrambe passavano di qui, distinte da un campo `purpose`
    ('salvo'/'interception'); con due tipi il campo avrebbe avuto un solo valore lecito,
    ed e' stato rimosso insieme alle costanti PURPOSE_*: il tipo dell'evento E' il suo
    scopo, e un consumatore non puo' piu' sommare per errore colpi e intercettazioni.
    """
    time: float
    asset_id: str
    rounds: int
    weapon: Optional[str] = None


@dataclass(frozen=True)
class InterceptionEvent:
    """Intercettazioni effettuate (R1/R3): `asset_id` ha fermato `interceptions` colpi in
    arrivo sulla forza `force_id` all'istante `time`. Si applica con
    `Mobile.consume_interceptor_stock`.

    `asset_id` e' l'INTERCETTORE (chi consuma la scorta), non chi ha sparato la salva
    intercettata. L'unita' e' l'intercettazione, non il colpo: per un cannone AA una
    intercettazione costa ~ROUNDS_PER_GUN_INTERCEPT colpi, gia' conteggiati nella scorta
    (v. Mobile.ROUNDS_PER_GUN_INTERCEPT) — per questo il campo non si chiama `rounds`.
    `weapon` (2026-09-26) e' l'arma AD che ha intercettato, dalla scorta per arma
    dell'asset (Mobile.stores): un missile AD e' lo stesso della salva offensiva, quindi
    intercettare riduce anche la scorta offensiva di quell'arma. Un asset che intercetta con
    piu' armi nello stesso evento (cannoni esauriti, poi missili: regola F) produce un
    evento per arma. None = pool anonimo di intercettori (stub, scorta impostata a mano).

    Tracciabilita': `force_id` e `salvo_ids` identificano l'evento-salva intercettato — la
    `SalvoResolution` con lo stesso `time` e `force_id`. Si referenziano tutte le salve
    del gruppo e non "quale" di esse perche' il modello non assegna intercettori a salve:
    la saturazione (R1) confronta la capacita' TOTALE con i colpi intercettabili
    dell'evento, e i colpi fermati sono i primi intercettabili nell'ordine (impatto, salva),
    indipendentemente da chi li ferma. `salvo_ids` sono progressivi del SINGOLO ingaggio
    (`Salvo.salvo_id`): hanno senso solo accanto all'`EngagementResult` che li ha prodotti,
    non in un `SessionOutcome` che aggrega piu' ingaggi (li' vale `force_id`, id di dominio).
    """
    time: float
    asset_id: str
    interceptions: int
    force_id: Optional[str] = None
    salvo_ids: Tuple[int, ...] = ()
    weapon: Optional[str] = None


@dataclass(frozen=True)
class ForceOutcome:
    """Esito di una forza. Pensato per essere promosso a voce del futuro `SessionOutcome`.

    Attributes:
        force_id/side: identita' di dominio della forza.
        outcome: uno di FORCE_OUTCOMES.
        time: istante del cambio di esito (None se HELD).
        triggers: motivi (TRIGGER_*) — possono scattare insieme erosione e shock.
        committed: asset impegnati all'inizio; lost: di questi, non piu' operativi alla fine.
        erosion: lost / committed alla fine; max_shock: la salva peggiore subita.
        temper: quantile `u` della tempra estratto per la forza (None: non estratto, mediana).
        breakpoint: soglia di rottura B(t) all'ultima valutazione (None: mai valutata o
            forza senza dottrina).
        morale: morale usato (None: sconosciuto, neutro).
        force_ratio: rapporto di forze percepito rho all'ultima valutazione (None: non
            definito, neutro).
        unanswered_fraction: quota delle perdite causate da tiratori non rilevati.
    """
    force_id: str
    side: Optional[str]
    outcome: str
    time: Optional[float]
    triggers: Tuple[str, ...]
    committed: int
    lost: int
    erosion: float
    max_shock: float
    temper: Optional[float] = None
    breakpoint: Optional[float] = None
    morale: Optional[float] = None
    force_ratio: Optional[float] = None
    unanswered_fraction: float = 0.0


@dataclass(frozen=True)
class EngagementResult:
    """Esito completo di un ingaggio. Immutabile: si sostituisce, non si riscrive.

    Contiene tutto cio' che serve ad applicare l'esito (`damage_events`,
    `ammunition_events` per le salve, `interception_events` per le intercettazioni) e a
    spiegarlo (`detections`, `salvos`, `resolutions`).
    """
    t_start: Optional[float]
    t_end: Optional[float]
    forces: Tuple[ForceOutcome, ...]
    detections: Tuple[Detection, ...] = ()
    salvos: Tuple[Salvo, ...] = ()
    resolutions: Tuple[SalvoResolution, ...] = ()
    damage_events: Tuple[DM.DamageEvent, ...] = ()
    ammunition_events: Tuple[AmmunitionEvent, ...] = ()
    interception_events: Tuple[InterceptionEvent, ...] = ()

    def outcome_of(self, force_id: str) -> Optional[ForceOutcome]:
        """L'esito della forza `force_id`, None se non partecipa."""
        for outcome in self.forces:
            if outcome.force_id == force_id:
                return outcome

        return None

    def ammunition_consumed(self) -> Dict[str, int]:
        """Unita' di scorta spese OFFENSIVAMENTE per asset (solo salve, `ammunition_events`).

        Cambio di comportamento del 2026-09-23: prima sommava anche le intercettazioni.
        Ora non piu' — per quelle v. `interceptions_consumed()`. Un missile AD usato per
        intercettare cala la stessa voce di scorta della salva offensiva (2026-09-26), ma i
        due conteggi restano separati per scopo.
        """
        consumed: Dict[str, int] = {}

        for event in self.ammunition_events:
            consumed[event.asset_id] = consumed.get(event.asset_id, 0) + event.rounds

        return consumed

    def ammunition_consumed_by_weapon(self) -> Dict[str, Dict[Optional[str], int]]:
        """Come `ammunition_consumed`, ripartito per arma: {asset: {arma: unita'}}."""
        consumed: Dict[str, Dict[Optional[str], int]] = {}

        for event in self.ammunition_events:
            by_weapon = consumed.setdefault(event.asset_id, {})
            by_weapon[event.weapon] = by_weapon.get(event.weapon, 0) + event.rounds

        return consumed

    def interceptions_consumed(self) -> Dict[str, int]:
        """Intercettazioni effettuate per asset (`interception_events`)."""
        consumed: Dict[str, int] = {}

        for event in self.interception_events:
            consumed[event.asset_id] = consumed.get(event.asset_id, 0) + event.interceptions

        return consumed


# ── PERCEZIONE: Pd ────────────────────────────────────────────────────────────

def _check_factor(factor) -> float:
    if isinstance(factor, bool) or not isinstance(factor, (int, float)):
        raise TypeError(f"detection factor must be a number, got {factor!r}")

    if not 0.0 <= factor <= 1.0:
        raise ValueError(f"detection factor must be in [0, 1], got {factor!r}")

    return float(factor)


def detection_probability(distance: float, sensor_range: float, factor: float = 1.0) -> float:
    """Pd di un sensore contro un bersaglio a `distance` [m].

        Pd(d) = factor * (1 - (1 - PD_AT_ACQUISITION_RANGE) * (d / R)^4)    per d <= R
        Pd(d) = 0                                                            per d >  R

    STIMA DICHIARATA di forma: 1 a distanza nulla, PD_AT_ACQUISITION_RANGE sul bordo della
    portata dichiarata dal registro, decrescente con la quarta potenza della distanza come
    il rapporto segnale/rumore dell'equazione radar. `factor` in [0, 1] e' la degradazione
    (meteo, notte, disturbo) applicata dal chiamante; 1.0 = nessuna.

    Raises:
        ValueError: distanza o portata negative, factor fuori [0, 1].
    """
    if distance < 0:
        raise ValueError(f"distance must be non-negative, got {distance!r}")

    if sensor_range <= 0:
        raise ValueError(f"sensor_range must be positive, got {sensor_range!r}")

    factor = _check_factor(factor)

    if distance > sensor_range:
        return 0.0

    ratio = (distance / sensor_range) ** PD_RANGE_EXPONENT

    return factor * (1.0 - (1.0 - PD_AT_ACQUISITION_RANGE) * ratio)


def detection_radius(draw: float, sensor_range: float, factor: float = 1.0) -> Optional[float]:
    """Distanza alla quale un'estrazione `draw` produce il rilevamento, None se mai.

    E' l'inversa di `detection_probability`: il rilevamento avviene quando
    `draw < Pd(d)`, cioe' quando il bersaglio entra nel raggio restituito. Cosi' UNA sola
    estrazione decide sia se il sensore rileva (raggio >= distanza minima raggiunta) sia
    quando (primo istante in cui la distanza scende sotto il raggio), senza campionare
    la finestra nel tempo.

    Returns:
        raggio [m] in (0, sensor_range], oppure None se `draw >= factor` (nemmeno a
        distanza nulla la Pd supera l'estrazione).
    """
    if not 0.0 <= draw < 1.0:
        raise ValueError(f"draw must be in [0, 1), got {draw!r}")

    if sensor_range <= 0:
        raise ValueError(f"sensor_range must be positive, got {sensor_range!r}")

    factor = _check_factor(factor)

    if draw >= factor:
        return None

    if draw < factor * PD_AT_ACQUISITION_RANGE:
        return float(sensor_range)

    ratio = (1.0 - draw / factor) / (1.0 - PD_AT_ACQUISITION_RANGE)

    return float(sensor_range) * ratio ** (1.0 / PD_RANGE_EXPONENT)


# ── DEGRADAZIONE AMBIENTALE DELLA Pd (meteo/notte, da Logic/Meteo_Analysis) ────

def weather_detection_factor(conditions: Optional[Mapping]) -> float:
    """Fattore di degradazione della Pd, in (0, 1], dalle condizioni meteo di una regione.

    `conditions` ha la forma di `Meteo_Analysis.get_meteo_conditions`:
    `{'day': bool, 'night': bool, 'adverse_weather': bool}`. I fattori si moltiplicano:

        factor = (NIGHT_DETECTION_FACTOR se notte) * (ADVERSE_WEATHER_DETECTION_FACTOR se avverso)

    Sede: qui e non in `Meteo_Analysis` perche' il numero e' un parametro della legge di
    Pd (entra in `detection_probability` accanto a PD_AT_ACQUISITION_RANGE), non una
    proprieta' del meteo; `Meteo_Analysis` resta il produttore delle condizioni.

    **Limite noto, dichiarato:** il fattore e' UNICO per ogni sensore. La finestra di
    contatto porta solo la portata migliore fra radar e TVD (`Mobile.detection_range`,
    default = massimo dei due), e il risolutore non sa quale dei due l'ha prodotta: non
    puo' quindi risparmiare al radar la degradazione notturna che fisicamente non subisce.
    Il valore notturno e' percio' un compromesso fra i due sensori; la discriminazione per
    tipo di sensore richiede che la finestra porti il sensore (passo futuro).

    Dati mancanti: `conditions` None -> 1.0 (nessuna degradazione) con un log; una chiave
    assente vale False; se manca 'night' la si ricava da 'day'.

    Raises:
        TypeError: `conditions` non e' un Mapping (errore di programmazione).
    """
    if conditions is None:
        logger.debug("weather_detection_factor: no meteo conditions, no degradation applied")
        return 1.0

    if not isinstance(conditions, abc.Mapping):
        raise TypeError(f"conditions must be a mapping like Meteo_Analysis.get_meteo_conditions, "
                        f"got {type(conditions).__name__}")

    night = conditions.get('night')

    if night is None:
        day = conditions.get('day')
        night = (not day) if day is not None else False

    factor = 1.0

    if night:
        factor *= NIGHT_DETECTION_FACTOR

    if conditions.get('adverse_weather'):
        factor *= ADVERSE_WEATHER_DETECTION_FACTOR

    return factor


def weather_detection_factor_fn(conditions: Optional[Mapping]) -> Callable:
    """La callable `(observer, target) -> float` per `resolve_engagement(detection_factor=...)`.

    La firma di `detection_factor` riceve solo la coppia di asset, non regione/data/ora:
    le condizioni sono quindi catturate qui (closure), quando il chiamante prepara la
    chiamata, e il fattore e' lo stesso per ogni coppia (v. il limite noto in
    `weather_detection_factor`). Il fattore e' calcolato una volta sola, subito: un errore
    sulle condizioni emerge qui e non a meta' ingaggio.
    """
    factor = weather_detection_factor(conditions)

    def detection_factor(observer, target) -> float:
        return factor

    return detection_factor


def meteo_detection_factor(region_name: str, date, time) -> Callable:
    """Come `weather_detection_factor_fn`, leggendo le condizioni da `Meteo_Analysis`.

    E' il collegamento con `Meteo_Analysis.get_meteo_conditions(region_name, date, time)`
    (oggi un placeholder deterministico): nessuna casualita' entra da qui. Import locale,
    come altrove nel progetto fra moduli di Logic.
    """
    from Code.Dynamic_War_Manager.Source.Logic.Meteo_Analysis import get_meteo_conditions

    return weather_detection_factor_fn(get_meteo_conditions(region_name, date, time))


# ── NEBBIA DI GUERRA: Pd DALL'ISTANTANEA DI RICOGNIZIONE (attivita' C) ─────────
#
# Solo costruttori del fattore iniettato `detection_factor`: il motore non cambia, e chi
# non passa questi fattori ottiene esattamente il comportamento precedente. La nebbia e'
# PER LATO (ognuno vede secondo la propria ricognizione) e STATICA: l'istantanea e' presa
# prima della sessione (decisione utente, niente nebbia dinamica/RNG nel motore). I fattori
# non consumano l'RNG di sessione: l'estrazione di rilevamento avviene comunque, una per
# direzione, nell'ordine del contratto — il fattore sposta solo la soglia.

_SIDES = ('Blue', 'Red', 'Neutral')


def _block_attribute(asset, name: str):
    """`asset.block.<name>`, None se l'asset non ha blocco (o il blocco non ha l'attributo)."""
    block = getattr(asset, 'block', None)
    return getattr(block, name, None) if block is not None else None


def _check_side(side) -> str:
    if side not in _SIDES:
        raise ValueError(f"side must be one of {_SIDES}, got {side!r}")

    return side


def recon_detection_factor_fn(seen_block_ids: Iterable[str], *, observer_side: str,
                              unseen_factor: float, seen_factor: float = 1.0) -> Callable:
    """La callable `(observer, target) -> float` della nebbia di guerra di un lato.

    Per un osservatore del lato `observer_side` (lato del suo blocco, `Asset.block.side`):

        seen_factor     se il blocco del bersaglio (`target.block.id`) e' in `seen_block_ids`
                        oppure e' dello stesso lato dell'osservatore (le proprie forze sono note)
        unseen_factor   altrimenti (blocco non confermato dalla ricognizione, o bersaglio
                        senza blocco: nessuna ricognizione puo' averlo confermato)

    Per ogni altro osservatore (lato opposto, o asset senza blocco/lato: non si puo'
    attribuirgli la ricognizione di `observer_side`) il fattore e' 1.0: la nebbia di un
    lato non tocca l'altro. Per applicarla a entrambi i lati si combinano due fattori
    (`combine_detection_factors`).

    `seen_block_ids` e' copiato subito in un frozenset: e' un'istantanea, una modifica
    successiva della collezione del chiamante non la altera.

    Raises:
        ValueError: `observer_side` non valido, fattori fuori [0, 1].
        TypeError: fattori non numerici.
    """
    observer_side = _check_side(observer_side)
    unseen_factor = _check_factor(unseen_factor)
    seen_factor = _check_factor(seen_factor)
    seen = frozenset(seen_block_ids)

    def detection_factor(observer, target) -> float:
        if _block_attribute(observer, 'side') != observer_side:
            return 1.0

        if _block_attribute(target, 'side') == observer_side:
            return seen_factor

        return seen_factor if _block_attribute(target, 'id') in seen else unseen_factor

    return detection_factor


def combine_detection_factors(*fns: Optional[Callable]) -> Callable:
    """Una sola callable `(observer, target) -> float` dal PRODOTTO di piu' fattori.

    Serve a usare insieme meteo e ricognizione (e le nebbie dei due lati) nell'unico
    `detection_factor` che `resolve_engagement` accetta. Le degradazioni sono indipendenti
    e moltiplicative, come gia' notte * meteo avverso in `weather_detection_factor`.

    Ogni componente e' riportato in [0, 1] prima del prodotto (un componente fuori
    dominio non puo' compensarne un altro), e il prodotto resta quindi in [0, 1]. Le voci
    None sono ignorate (e' il default di `detection_factor`); nessuna voce -> 1.0.

    Raises:
        TypeError: una voce non e' callable (subito), o un componente restituisce un
            valore non numerico (alla chiamata).
    """
    components = tuple(fn for fn in fns if fn is not None)

    for fn in components:
        if not callable(fn):
            raise TypeError(f"detection factors must be callables, got {fn!r}")

    def detection_factor(observer, target) -> float:
        product = 1.0

        for fn in components:
            value = fn(observer, target)

            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"detection factor must be a number, got {value!r}")

            product *= min(max(float(value), 0.0), 1.0)

        return product

    return detection_factor


def recon_unseen_factor(recon_efficiency: Optional[float], *,
                        unseen_factor: float = UNSEEN_DETECTION_FACTOR, seen_factor: float = 1.0,
                        relief: float = RECON_EFFICIENCY_FOG_RELIEF) -> float:
    """Fattore dei bersagli NON visti, modulato dall'efficienza di ricognizione dell'osservatore.

        e      = recon_efficiency riportata in [0, 1] (None -> 0.0)
        unseen = unseen_factor + (seen_factor - unseen_factor) * relief * e

    STIMA DICHIARATA di forma (lineare) e di peso (`relief`, v. RECON_EFFICIENCY_FOG_RELIEF):
    con ricognizione nulla il fattore e' `unseen_factor`; al crescere dell'efficienza si
    avvicina a `seen_factor`, recuperandone al massimo la quota `relief` della distanza.
    Razionale: un apparato di ricognizione efficiente fornisce cueing anche sui blocchi che
    l'istantanea non ha confermato (settori coperti, tracce parziali), ma non li rende
    confermati.

    Raises:
        ValueError/TypeError: fattori o `relief` fuori [0, 1] / non numerici.
    """
    unseen_factor = _check_factor(unseen_factor)
    seen_factor = _check_factor(seen_factor)
    relief = _check_factor(relief)

    if recon_efficiency is None:
        efficiency = 0.0
    elif isinstance(recon_efficiency, bool) or not isinstance(recon_efficiency, (int, float)):
        raise TypeError(f"recon_efficiency must be a number, got {recon_efficiency!r}")
    else:
        efficiency = min(max(float(recon_efficiency), 0.0), 1.0)

    return unseen_factor + (seen_factor - unseen_factor) * relief * efficiency


def side_recon_efficiency(region, side: str) -> float:
    """Efficienza di ricognizione di un LATO in una regione: il MASSIMO fra le sue `Military`.

    `Military.get_recon_efficiency()` e' per singolo blocco (mediana di `asset.efficiency`
    degli asset con ruolo RECONNAISSANCE, 0.0 senza). Aggregazione scelta: il massimo sui
    blocchi `Military` del lato nella regione, non la media di
    `Region.get_region_recon_efficiency`. Motivo: quella media include i blocchi SENZA asset
    di ricognizione (che valgono 0.0) e misura quanto la ricognizione e' diffusa nel lato;
    qui serve invece se l'area e' "illuminata", e per questo basta un solo buon sensore —
    una regione con cinque battaglioni corazzati e un solo ottimo squadrone da
    ricognizione non deve risultare poco ricognita. La mediana resta DENTRO il blocco
    (robusta agli asset anomali di una stessa unita'), il massimo FRA i blocchi. Limite
    dichiarato: il massimo ignora la copertura geografica (un buon sensore illumina tutta
    la regione, ovunque sia).

    Blocchi selezionati come in `Region.get_recon_reports`
    (`get_blocks_by_criteria(side, category='Military')`), cosi' osservatori e osservati
    seguono la stessa regola. Valori non numerici ignorati; nessun blocco -> 0.0.
    """
    from Code.Dynamic_War_Manager.Source.Context.Region import BlockCategory

    best = 0.0

    for block_item in region.get_blocks_by_criteria(side=side, category=BlockCategory.MILITARY.value):
        method = getattr(block_item.block, 'get_recon_efficiency', None)

        if not callable(method):
            continue

        value = method()

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            logger.debug(f"side_recon_efficiency: non-numeric recon efficiency {value!r} "
                         f"for block {getattr(block_item.block, 'id', None)!r}, ignored")
            continue

        best = max(best, float(value))

    return best


def region_recon_detection_factor(region, observer_side: str, *,
                                  unseen_factor: float = UNSEEN_DETECTION_FACTOR,
                                  seen_factor: float = 1.0,
                                  relief: float = RECON_EFFICIENCY_FOG_RELIEF) -> Callable:
    """`recon_detection_factor_fn` per `observer_side`, dall'istantanea di ricognizione di `region`.

    L'istantanea e' scattata QUI, una sola volta, prima della sessione, con la stessa
    ricetta di `Region.update_military_priorities(use_recon=True)`:

        seen = build_recon_cp_snapshot(region.get_recon_reports(enemySide(observer_side))).keys()

    e `unseen_factor` e' modulato dall'efficienza di ricognizione del lato osservatore
    (`side_recon_efficiency`, massimo fra le sue `Military`) con `recon_unseen_factor`.

    Casualita': `Block.get_recognition_report` estrae con il `random` di modulo
    (`Utility.calcProbability`) quali CAMPI del report compilare; avviene qui, fuori dal
    percorso del motore e prima della sessione, e non tocca l'RNG di sessione. L'insieme
    dei blocchi visti (le chiavi dell'istantanea) non dipende da quelle estrazioni.

    `observer_side == 'Neutral'` non e' un lato belligerante (stesso guard di
    `update_military_priorities`): warning e fattore neutro (1.0 ovunque).

    Raises:
        ValueError: `observer_side` non valido, fattori fuori [0, 1].
    """
    from Code.Dynamic_War_Manager.Source.Logic import Tactical_Analysis
    from Code.Dynamic_War_Manager.Source.Utility.Utility import enemySide

    observer_side = _check_side(observer_side)

    if observer_side == 'Neutral':
        logger.warning(f"region_recon_detection_factor: side 'Neutral' is not a belligerent, "
                       f"no fog of war applied (region {getattr(region, 'name', None)!r})")
        return lambda observer, target: 1.0

    snapshot = Tactical_Analysis.build_recon_cp_snapshot(region.get_recon_reports(enemySide(observer_side)))
    efficiency = side_recon_efficiency(region, observer_side)
    effective_unseen = recon_unseen_factor(efficiency, unseen_factor=unseen_factor,
                                           seen_factor=seen_factor, relief=relief)

    logger.debug(f"region_recon_detection_factor: side {observer_side!r} in region "
                 f"{getattr(region, 'name', None)!r} sees {sorted(snapshot)} "
                 f"(recon efficiency {efficiency:.3f} -> unseen factor {effective_unseen:.3f})")

    return recon_detection_factor_fn(snapshot.keys(), observer_side=observer_side,
                                     unseen_factor=effective_unseen, seen_factor=seen_factor)


# ── STATO OMBRA ───────────────────────────────────────────────────────────────

class _Shadow:
    """Copia di lavoro di un asset impegnato: salute e scorte evolvono qui, non sull'asset.

    Espone `id` e `health` perche' `Damage_Model.build_damage_event` la tratti come un
    asset (duck typing): cosi' il contratto del danno resta uno solo.

    Scorte (dal 2026-09-26): la stessa forma di `Mobile` — `stores` (COPIA della scorta per
    arma, o None), il pool anonimo `anonymous` (usato solo senza `stores`), le armi non
    modellate `unmodelled`, le armi AD `interceptor_weapons` su cui `interceptor_stock` e'
    una vista, e il pool anonimo di intercettori. La contabilita' e' quella di
    `Asset/Weapon_Stores.py`, condivisa con l'asset reale: cosi' `apply_engagement_result`
    ritrova sull'asset esattamente i consumi che l'ombra ha concesso. (Fino al 2026-09-26
    la condivisione munizioni/intercettori esisteva solo per i "SAM puri", `shared_pool`:
    ora e' per arma, per costruzione.)
    """
    __slots__ = ('id', 'asset', 'force_id', 'health', 'stores', 'anonymous', 'unmodelled',
                 'interceptor_weapons', 'anonymous_interceptors')

    def __init__(self, asset_id: str, asset, force_id: str, health: int, ammunition: Optional[int] = None,
                 interceptor_stock: Optional[int] = None, stores: Optional[Dict[str, int]] = None,
                 unmodelled: Iterable[str] = (), interceptor_weapons: Optional[Dict[str, bool]] = None):
        self.id = asset_id
        self.asset = asset
        self.force_id = force_id
        self.health = health
        self.stores = dict(stores) if stores is not None else None
        self.anonymous = None if stores is not None else ammunition
        self.unmodelled = WS.frozen_names(unmodelled)
        self.interceptor_weapons = dict(interceptor_weapons) if interceptor_weapons else None
        view = WS.interceptor_view_active(self.stores, self.interceptor_weapons)
        self.anonymous_interceptors = None if view else interceptor_stock

    @property
    def ammunition(self) -> Optional[int]:
        """Scorta totale (vista, come `Mobile.ammunition`)."""
        return WS.total_stock(self.stores, self.anonymous)

    def available(self, weapon: Optional[str]) -> Optional[int]:
        """Unita' spendibili da `weapon`; None = nessun vincolo."""
        return WS.available_stock(self.stores, self.anonymous, self.unmodelled, weapon)

    def has_stock(self) -> bool:
        return WS.has_stock(self.stores, self.anonymous, self.unmodelled)

    def consume(self, weapon: Optional[str], units: int) -> int:
        consumed, self.anonymous = WS.consume_stock(self.stores, self.anonymous, self.unmodelled, weapon,
                                                    units, self.interceptor_weapons)
        return consumed

    @property
    def interceptor_stock(self) -> Optional[int]:
        return WS.interceptor_stock(self.stores, self.interceptor_weapons, self.anonymous_interceptors)

    def consume_interceptions(self, amount: int) -> List[Tuple[Optional[str], int]]:
        """Consuma `amount` intercettazioni; ritorna la ripartizione [(arma | None, n), ...]."""
        if WS.interceptor_view_active(self.stores, self.interceptor_weapons):
            plan = WS.plan_interceptions(self.stores, self.interceptor_weapons, amount)
            WS.apply_interception_plan(self.stores, self.interceptor_weapons, plan)
            return plan

        if self.anonymous_interceptors is None:
            return [(None, amount)] if amount > 0 else []

        used = min(amount, self.anonymous_interceptors)
        self.anonymous_interceptors -= used
        return [(None, used)] if used > 0 else []

    @property
    def operative(self) -> bool:
        return self.health > OPERATIVE_HEALTH_FLOOR

    @property
    def destroyed(self) -> bool:
        return self.health <= DM.DESTROYED_HEALTH


@dataclass
class _Candidate:
    """Un bersaglio rilevato da un tiratore, ingaggiabile in [t_ready, t_end].

    `t_cpa`/`distance_cpa` vengono dalla finestra di contatto (ripiego del controllo di
    portata senza tratti di rotta); `not_before` e' l'istante di ingresso nella portata
    dell'arma quando il tiro e' stato rimandato (v. "Controllo di portata").
    """
    t_ready: float
    target_id: str
    t_end: float
    exhausted: bool = False
    t_cpa: Optional[float] = None
    distance_cpa: Optional[float] = None
    not_before: Optional[float] = None


@dataclass
class _ForceState:
    force_id: str
    side: Optional[str]
    committed: Tuple[str, ...]
    thresholds: Optional[Dict[str, float]]
    interceptors: List[Tuple[_Shadow, int]] = field(default_factory=list)
    outcome: Optional[str] = None
    time: Optional[float] = None
    triggers: Tuple[str, ...] = ()
    max_shock: float = 0.0
    # Soglia di rottura stocastica (2026-09-29, v. "Soglia di rottura" nel docstring).
    force: object = None
    air: bool = False
    temper: Optional[float] = None
    temper_z: float = 0.0
    morale: Optional[float] = None
    enemy_estimate: Optional[float] = None
    stationary: Optional[bool] = None
    loss_shooters: Dict[str, Tuple[str, float]] = field(default_factory=dict)
    breakpoint: Optional[float] = None
    force_ratio: Optional[float] = None
    unanswered_fraction: float = 0.0
    # Dottrina di tiro (2026-09-29): soglia di saturazione e tetto "due missili, poi guarda".
    fire: Dict[str, Optional[float]] = field(default_factory=dict)


@dataclass
class _PendingGroup:
    resolve_time: float
    salvos: List[Salvo] = field(default_factory=list)


def _domain_id(obj) -> Optional[str]:
    """Identificativo di dominio di un asset o di una forza. Mai un id del simulatore."""
    for attribute in ('id', 'name'):
        value = getattr(obj, attribute, None)

        if isinstance(value, str) and value:
            return value

    return None


def _can_disengage(force) -> bool:
    """True se la forza ha diritto a una politica di disingaggio (v. docstring del modulo, §6).

    Una `Military` si'; un `Block` non militare (deposito, trasporto, area urbana) no: non
    puo' rompere il contatto, combatte/subisce fino alla fine. Un oggetto che non e' un
    `Block` (stub duck-typed, adapter) e' trattato come forza combattente, come prima di
    questa regola: il risolutore non impone la gerarchia di classe ai suoi input.
    """
    if validate_class(force, 'Military'):
        return True

    return not validate_class(force, 'Block')


# ── PORTATA D'ARMA: INTERVALLI DI PERMANENZA (controllo di portata, 2026-09-24) ──
#
# Il calcolo "da quando a quando il bersaglio e' entro la portata" e' isolato qui, fuori
# dalla schedulazione, perche' e' il primo caso particolare dei futuri VOLUMI di
# rilevamento/ingaggio (decisione utente 2026-09-24: interfaccia "volume" che restituisce
# gli intervalli di permanenza su un tratto a moto relativo rettilineo uniforme, con
# primitive sfera/cilindro/fascia di quota/cono/orizzonte radar e combinatori di
# intervalli). Oggi c'e' solo la SFERA di raggio max_range centrata sul tiratore. Il
# risolutore la usa tramite l'attributo `_EngagementRun.engagement_intervals`, che un
# volume diverso potra' sostituire senza toccare `_range_entry` ne' `_schedule_next`.

IntervalList = List[Tuple[float, float]]


def engagement_intervals(legs_shooter: Sequence, legs_target: Sequence, max_range: float) -> IntervalList:
    """Intervalli [t_in, t_out] in cui il bersaglio e' nella SFERA di raggio `max_range` [m]
    centrata sul tiratore (distanza 3D), dai tratti di rotta di entrambi.

    E' `Contact_Scheduler.range_intervals` (soluzione esatta di |dr + dv s| <= R su ogni
    sottointervallo a velocita' relativa costante), la stessa geometria del rilevamento.
    """
    return range_intervals(legs_shooter, legs_target, max_range)


def engagement_intervals_without_legs(t_cpa: Optional[float], distance_cpa: Optional[float],
                                      t_end: float, max_range: float) -> IntervalList:
    """Ripiego senza tratti di rotta: la sola `ContactWindow` non ricostruisce la distanza
    nel tempo, l'unico dato certo e' il massimo avvicinamento (dichiarato).

    * `distance_cpa` ignota -> nessun vincolo: [(-inf, +inf)];
    * `distance_cpa > max_range` -> mai in portata: [];
    * altrimenti [(t_cpa, t_end)]: prima del CPA il tiro aspetta il CPA; dopo il CPA la
      distanza non e' verificabile e il tiro e' ammesso fino alla fine della finestra.
    """
    if distance_cpa is None:
        return [(float('-inf'), float('inf'))]

    if distance_cpa > max_range:
        return []

    return [(float('-inf') if t_cpa is None else float(t_cpa), float(t_end))]


# ── RISOLUTORE ────────────────────────────────────────────────────────────────

class _EngagementRun:
    """Stato e coda eventi di UN ingaggio (2+ forze). Uso interno: v. `resolve_engagement`."""

    def __init__(self, forces, contacts, fire_control, rng, legs, committed, thresholds,
                 reaction_profile_for, detection_factor, salvo_window, provenance,
                 breakpoint_rng=None, morale_for=None, enemy_estimate_for=None, fire_doctrine=None):
        self.fire_control = fire_control
        self.fire_doctrine = fire_doctrine
        self.rng = rng
        self.breakpoint_rng = breakpoint_rng
        self.morale_for = morale_for
        self.enemy_estimate_for = enemy_estimate_for
        # Primo istante in cui ciascuna forza ha rilevato ciascun asset nemico (qualunque
        # suo osservatore): la base della percezione del nemico (soglia di rottura, D4/D5).
        self.seen_by: Dict[str, Dict[str, float]] = {}
        self.surface_weights: Dict[str, float] = {}
        self.legs = legs or {}
        self.zone_cache: Dict[str, Optional[Tuple[float, float, float]]] = {}
        # Regole L2/L3 (2026-09-28): aerei che hanno lanciato armi aria-superficie contro
        # ciascuna forza, e generazione del lancio programmato di ogni tiratore (prelazione).
        self.launchers_against: Dict[str, set] = {}
        self.launch_generation: Dict[str, int] = {}
        self.pending_decide: set = set()
        self.may_intercept_cache: Dict[Tuple[str, int], bool] = {}
        # Regola R-INT (2026-09-30): istante di rilevamento per (osservatore, bersaglio), raggio
        # di rilevamento aereo degli intercettori, esito del vincolo di tempo per (intercettore, salva).
        self.detected_at: Optional[Dict[Tuple[str, str], float]] = None
        self.air_range_cache: Dict[str, Optional[float]] = {}
        self.in_time_cache: Dict[Tuple[str, int], bool] = {}
        self.reaction_profile_for = reaction_profile_for or RP.profile_for_asset
        self.detection_factor = detection_factor
        self.salvo_window = float(salvo_window)
        self.provenance = provenance
        self.contacts = list(contacts or [])

        self.shadows: Dict[str, _Shadow] = {}
        self.force_states: Dict[str, _ForceState] = {}
        self.force_order: List[str] = []
        self.profiles: Dict[str, RP.ReactionProfile] = {}
        self.candidates: Dict[str, List[_Candidate]] = {}
        # Ripartizione del fuoco (v. _schedule_next): bersaglio del lancio schedulato e non
        # ancora eseguito di ogni tiratore, e salve lanciate non ancora risolte.
        self.assigned: Dict[str, str] = {}
        # (ShotSpec, colpi, istante di lancio) del lancio schedulato di ogni tiratore: serve alla
        # stima della copertura (saturazione, v. _blocked); vale solo finche' `assigned` lo cita.
        self.assigned_shot: Dict[str, Tuple["ShotSpec", int, float]] = {}
        # Istante dell'evento in corso (per scartare lanci schedulati gia' passati).
        self.now = float('-inf')
        self.in_flight: Dict[int, Salvo] = {}
        # Geometria "bersaglio entro la portata" (sostituibile, v. engagement_intervals) e
        # intervalli gia' calcolati per (tiratore, bersaglio, max_range): v. _range_entry.
        self.engagement_intervals = engagement_intervals
        self.range_cache: Dict[Tuple[str, str, float], List[Tuple[float, float]]] = {}

        self.queue: List = []
        self.sequence = 0
        self.pending: Dict[str, _PendingGroup] = {}
        # Forze che hanno rotto il contatto (DESTROYED o DISENGAGED): per-forza, non un
        # flag globale della run (v. "Forze rotte" nel docstring del modulo).
        self.broken_forces: set = set()
        self.t_start: Optional[float] = None
        self.t_end: Optional[float] = None

        self.detections: List[Detection] = []
        self.salvos: List[Salvo] = []
        self.resolutions: List[SalvoResolution] = []
        self.damage_events: List[DM.DamageEvent] = []
        self.ammunition_events: List[AmmunitionEvent] = []
        self.interception_events: List[InterceptionEvent] = []

        self.usable = self._build_forces(forces, committed, thresholds)

        if self.usable:
            self._init_breakpoints()

    # ── costruzione ───────────────────────────────────────────────────────────

    def _build_forces(self, forces, committed, thresholds) -> bool:
        for index, force in enumerate(forces):
            force_id = _domain_id(force) or f'force_{index}'

            if force_id in self.force_states:
                raise ValueError(f"the forces must be distinct, {force_id!r} appears more than once")

            assets = getattr(force, 'assets', None) or {}
            selected = None

            if committed is not None and force_id in committed:
                selected = {str(asset_id) for asset_id in committed[force_id]}

            committed_ids = []

            for asset in sorted(assets.values(), key=lambda a: str(_domain_id(a))):
                asset_id = _domain_id(asset)

                if asset_id is None:
                    logger.debug(f"resolve_engagement: asset without domain id in force {force_id!r}, skipped")
                    continue

                if selected is not None and asset_id not in selected:
                    continue

                if asset_id in self.shadows:
                    raise ValueError(f"asset {asset_id!r} appears in more than one force")

                health = getattr(asset, 'health', None)

                if isinstance(health, bool) or not isinstance(health, int):
                    logger.warning(f"resolve_engagement: asset {asset_id!r} has no readable health, not committed")
                    continue

                is_operative = getattr(asset, 'is_operative', None)

                if callable(is_operative) and not is_operative():
                    continue

                if health <= OPERATIVE_HEALTH_FLOOR:
                    continue

                self.shadows[asset_id] = self._shadow_of(asset_id, asset, force_id, health)
                committed_ids.append(asset_id)

            side = getattr(force, 'side', None)

            if not _can_disengage(force):
                # Blocco non militare (deposito, linea di trasporto, area urbana): non puo'
                # rompere il contatto per definizione, nessuna dottrina da consultare e
                # nessun warning (non e' una dottrina mancante).
                side_thresholds = None
            else:
                side_thresholds = Doctrine.get_disengagement_thresholds(side, thresholds)

                if side_thresholds is None:
                    logger.warning(f"resolve_engagement: no disengagement doctrine for side {side!r} "
                                   f"(force {force_id!r}): it will fight until annihilation")

            state = _ForceState(force_id=force_id, side=side, committed=tuple(committed_ids),
                                thresholds=side_thresholds, force=force,
                                fire=Doctrine.get_fire_doctrine(side, self.fire_doctrine))
            state.interceptors = self._interceptors_of(force, force_id)
            self.force_states[force_id] = state
            self.force_order.append(force_id)

        empty = [force_id for force_id, state in self.force_states.items() if not state.committed]

        if not empty:
            return True

        if len(self.force_states) - len(empty) < 2:
            logger.warning(f"resolve_engagement: forces {empty} have no committed operative asset, "
                           f"engagement not resolvable")
            return False

        # Solo con 3+ forze: una forza vuota non blocca le altre, che hanno ancora almeno
        # un avversario possibile. Resta nell'esito (committed=0, HELD): nessuno la vede e
        # nessuno la colpisce, perche' non ha asset nello stato ombra.
        logger.warning(f"resolve_engagement: forces {empty} have no committed operative asset, "
                       f"they take no part in the engagement")
        return True

    @staticmethod
    def _shadow_of(asset_id: str, asset, force_id: str, health: int) -> _Shadow:
        """Stato ombra dalle scorte dell'asset (per arma se le ha, altrimenti pool anonimi).

        Letture difensive: uno stub duck-typed senza `stores` (o con valori non validi)
        ricade sul pool anonimo `ammunition`, comportamento precedente al 2026-09-26.
        """
        def _int_or_none(value):
            return value if isinstance(value, int) and not isinstance(value, bool) else None

        stores = getattr(asset, 'stores', None)

        try:
            stores = WS.normalize_stores(stores) if isinstance(stores, abc.Mapping) else None
        except (TypeError, ValueError):
            logger.warning(f"resolve_engagement: asset {asset_id!r} has malformed stores, ignored")
            stores = None

        unmodelled = getattr(asset, 'unmodelled_weapons', None)
        unmodelled = unmodelled if isinstance(unmodelled, (set, frozenset, tuple, list)) else ()
        weapons = getattr(asset, 'interceptor_weapons', None)
        weapons = dict(weapons) if isinstance(weapons, abc.Mapping) else None

        return _Shadow(asset_id, asset, force_id, health,
                       ammunition=None if stores is not None else _int_or_none(getattr(asset, 'ammunition', None)),
                       interceptor_stock=_int_or_none(getattr(asset, 'interceptor_stock', None)),
                       stores=stores, unmodelled=unmodelled, interceptor_weapons=weapons)

    def _interceptors_of(self, force, force_id: str) -> List[Tuple[_Shadow, int]]:
        provider = getattr(force, 'salvo_interceptors', None)

        if not callable(provider):
            return []

        interceptors = []

        for asset, channels in provider() or []:
            shadow = self.shadows.get(_domain_id(asset))

            if shadow is None or shadow.force_id != force_id:
                continue

            interceptors.append((shadow, int(channels)))

        # Regola F fra asset (2026-09-28): prima gli intercettori a soli cannoni, poi per id.
        interceptors.sort(key=lambda item: (WS.interceptor_rank(item[0].interceptor_weapons), item[0].id))

        return interceptors

    def _profile(self, shooter_id: str) -> RP.ReactionProfile:
        if shooter_id not in self.profiles:
            self.profiles[shooter_id] = self.reaction_profile_for(self.shadows[shooter_id].asset)

        return self.profiles[shooter_id]

    # ── fase 1: rilevamento ───────────────────────────────────────────────────

    def _detect(self) -> None:
        windows = sorted(self.contacts, key=lambda w: (w.t_start, str(w.asset_a_id),
                                                        str(w.asset_b_id), w.t_end))

        for window in windows:
            shadow_a = self.shadows.get(window.asset_a_id)
            shadow_b = self.shadows.get(window.asset_b_id)

            if shadow_a is None or shadow_b is None:
                logger.debug(f"_detect: window {window.asset_a_id!r}-{window.asset_b_id!r} "
                             f"involves an asset not committed to this engagement, skipped")
                continue

            if shadow_a.force_id == shadow_b.force_id:
                continue

            self.t_start = window.t_start if self.t_start is None else min(self.t_start, window.t_start)

            self._detect_direction(window, shadow_a, shadow_b, window.range_a, window.range_b)
            self._detect_direction(window, shadow_b, shadow_a, window.range_b, window.range_a)

    def _detect_direction(self, window, observer: _Shadow, target: _Shadow,
                          own_range: Optional[float], other_range: Optional[float]) -> None:
        if own_range is None or own_range <= 0:
            return

        factor = 1.0

        if self.detection_factor is not None:
            factor = _check_factor(self.detection_factor(observer.asset, target.asset))

        draw = self._draw()
        distance = max(float(window.distance_cpa), 0.0)
        probability = detection_probability(distance, own_range, factor) if distance <= own_range else 0.0
        detected = draw < probability
        time = None

        if detected:
            radius = detection_radius(draw, own_range, factor)
            time = self._detection_time(window, observer.id, target.id, own_range, other_range, radius)
            self._perceive(observer.force_id, target.id, time)

            # RWR (2026-09-29): il radar dell'osservatore illumina il bersaglio; se il bersaglio e'
            # un aereo il cui RWR identifica la categoria SAM dell'osservatore, la sua forza sa da
            # quell'istante chi la sta ingaggiando (percezione e fuoco senza risposta).
            if ADE.rwr_perception(target.asset, observer.asset) == ADE.PERCEIVED_AT_DETECTION:
                self._perceive(target.force_id, observer.id, time)

            t_ready = time + self._profile(observer.id).total

            if t_ready <= window.t_end + TIME_EPS:
                self.candidates.setdefault(observer.id, []).append(
                    _Candidate(t_ready=t_ready, target_id=target.id, t_end=window.t_end,
                               t_cpa=float(window.t_cpa), distance_cpa=distance))

        self.detections.append(Detection(observer_id=observer.id, target_id=target.id,
                                         sensor_range=float(own_range), distance_cpa=distance,
                                         probability=probability, draw=draw, detected=detected,
                                         time=time))

    def _perceive(self, force_id: str, asset_id: str, time: float) -> None:
        """La forza `force_id` percepisce l'asset nemico `asset_id` dall'istante `time`."""
        seen = self.seen_by.setdefault(force_id, {})
        seen[asset_id] = min(seen.get(asset_id, time), time)

    def _detection_time(self, window, observer_id: str, target_id: str, own_range: float,
                        other_range: Optional[float], radius: Optional[float]) -> float:
        """Istante del rilevamento dentro la finestra.

        Con i tratti di entrambe le rotte: primo istante in cui la distanza scende sotto il
        raggio di rilevamento estratto (esatto, `range_intervals`). Senza: l'istante
        geometrico in cui il bersaglio entra nella portata dell'osservatore — `t_start` se
        la sua e' la portata maggiore, `t_mutual_start` altrimenti — cosi' l'iniziativa di
        chi vede piu' lontano resta preservata; ultimo ripiego `t_cpa`.
        """
        legs_observer = self.legs.get(observer_id)
        legs_target = self.legs.get(target_id)

        if legs_observer and legs_target and radius is not None:
            for start, end in range_intervals(legs_observer, legs_target, radius):
                if end >= window.t_start - TIME_EPS and start <= window.t_end + TIME_EPS:
                    return max(start, window.t_start)

            return window.t_cpa

        if other_range is None or own_range >= other_range:
            return window.t_start

        if window.t_mutual_start is not None:
            return window.t_mutual_start

        return window.t_cpa

    # ── coda eventi ───────────────────────────────────────────────────────────

    def _push(self, time: float, kind: int, key: str, payload) -> None:
        self.sequence += 1
        heapq.heappush(self.queue, (time, kind, key, self.sequence, payload))

    def _draw(self) -> float:
        value = self.rng.random()

        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0.0 <= value < 1.0:
            raise ValueError(f"rng.random() must return a float in [0, 1), got {value!r}")

        return float(value)

    def _touch(self, time: float) -> None:
        self.t_end = time if self.t_end is None else max(self.t_end, time)

    # ── fase 2: scelta del bersaglio e lancio ─────────────────────────────────

    def _engaged_shooters(self, target_id: str, force_id: str, exclude: str) -> int:
        """Quanti ALTRI tiratori della forza `force_id` sono impegnati ora su `target_id`.

        Un tiratore e' "impegnato" su un bersaglio se ha un lancio gia' schedulato contro
        di esso e non ancora eseguito (`self.assigned`) oppure una salva gia' lanciata
        contro di esso e non ancora risolta (`self.in_flight`). Si contano tiratori
        distinti, non colpi ne' salve. Il tiratore che sta decidendo e' escluso: la
        ripartizione riguarda come si dividono i tiratori, non se un tiratore debba
        abbandonare il proprio bersaglio (con un solo tiratore il comportamento resta
        identico a quello senza ripartizione). Calcolato dinamicamente dallo stato della
        coda: nessun contatore da tenere allineato.
        """
        shooters = {shooter_id for shooter_id, assigned in self.assigned.items()
                    if assigned == target_id}
        shooters.update(salvo.shooter_id for salvo in self.in_flight.values()
                        if salvo.target_id == target_id)
        shooters.discard(exclude)

        return sum(1 for shooter_id in shooters if self.shadows[shooter_id].force_id == force_id)

    def _schedule_next(self, shooter_id: str, t_earliest: float) -> None:
        """Decide il prossimo lancio del tiratore e lo mette in coda con payload congelato.

        Un tiratore ingaggia un bersaglio alla volta, fra quelli rilevati, ancora operativi
        e ancora in finestra. `fire_control` e' interrogata QUI, allo scheduling: la
        ShotSpec e il numero di colpi (limitato dalla scorta attuale) viaggiano con
        l'evento e non vengono piu' ricalcolati.

        ## Ripartizione del fuoco: round-robin semplice (decisione utente 2026-09-23)

        Senza ripartizione ogni tiratore sceglieva da solo il bersaglio ingaggiabile per
        primo, e i tiratori di una stessa forza convergevano tutti sullo stesso bersaglio
        (id minore) lasciando gli altri indisturbati. La regola, nell'ordine:

        1. **Istante di tiro:** si considerano solo i bersagli ingaggiabili al PRIMO istante
           utile del tiratore (`t_fire` minimo, entro TIME_EPS). La ripartizione non fa mai
           aspettare un tiratore pronto per andare su un bersaglio meno coperto che sara'
           ingaggiabile solo piu' tardi: cosi' la latenza di reazione — chi spara per primo
           e QUANDO, la parte salvata della Strategia 1 — resta esattamente quella di prima;
           la ripartizione cambia solo CONTRO CHI si spara. (Scelta conservativa su un punto
           che il briefing non chiudeva: "meno coperto prima, poi il piu' vicino nel tempo"
           letto alla lettera potrebbe tenere fermo un tiratore anche a lungo.)
        2. **Copertura:** fra questi, quello con meno ALTRI tiratori della stessa forza gia'
           impegnati (v. `_engaged_shooters`: lancio schedulato o salva in volo).
        3. **Criterio precedente:** a parita', `t_ready` minore (il primo rilevato), poi l'id
           del bersaglio, poi l'ordine di rilevamento.

        Deterministica: dipende solo dallo stato della coda, e i tiratori decidono in un
        ordine fissato (id ordinati all'avvio, poi l'ordine canonico della coda eventi). La
        prima decisione di ogni tiratore vede i lanci gia' schedulati dai tiratori con id
        minore.

        ## Priorita' ai lanciatori (regole L2/L3, 2026-09-28, Proposta_Regole_Allocazione_SAM.md §7)

        Prima della regola sopra: se fra i bersagli possibili ci sono aerei che hanno gia'
        lanciato armi aria-superficie contro la forza del tiratore (`launchers_against`) e che
        sono ingaggiabili a portata al loro istante di tiro, la scelta si fa SOLO fra loro,
        anche se non sono al primo istante utile, con la stessa copertura (piu' lanciatori:
        il lavoro si ripartisce; uno solo: tutti su di lui). Alla prima salva aria-superficie
        di un aereo i tiratori della forza colpita che lo hanno a portata rinunciano al lancio
        programmato su un bersaglio non prioritario (annullamento per generazione, R4) e
        ridecidono dopo il proprio `refire_interval` (evento _DECIDE, v. _register_launcher).

        ## Dottrina di tiro (2026-09-29, Proposta_Overkill_Tiro.md)

        Prima della scelta si escludono i bersagli bloccati (`_blocked`): SATURI per la forza —
        la probabilita' che le salve gia' dirette contro di essi dalla forza (in volo o
        schedulate) li distruggano raggiunge `kill_probability_threshold` (0.9) — oppure su cui
        il tiratore ha gia' in volo `max_rounds_in_flight` colpi (2: "due missili, poi
        guarda"). I lanciatori prioritari (L2) sono esenti dalla saturazione, non dal tetto. Se
        tutti i bersagli sono bloccati il tiratore aspetta il primo impatto previsto su uno di
        essi (mai prima del proprio prossimo istante di tiro) e ridecide (`_wait`, evento
        _DECIDE). Dottrina di lato in `Context/Doctrine.DEFAULT_FIRE_DOCTRINE`.

        E' "semplice" perche' e' una regola greedy locale, presa dal singolo tiratore
        quando schedula il PROPRIO prossimo lancio. Cosa NON fa: non ottimizza globalmente
        l'assegnazione arma-bersaglio (nessun WTA, nessun peso per valore del bersaglio; la Pk
        della coppia entra solo nella saturazione); non redistribuisce assegnazioni gia' fatte — un lancio gia'
        in coda non viene mai spostato su un altro bersaglio (R4: al piu' annullato), e una
        salva in volo arriva dove era diretta; non tiene memoria del passato remoto: una
        salva gia' risolta non conta piu' come copertura.
        """
        shooter = self.shadows[shooter_id]

        if shooter.force_id in self.broken_forces:
            return

        if not shooter.operative or not shooter.has_stock():
            # Nessuna arma con scorta (le armi non modellate non hanno vincolo).
            return

        candidates = self.candidates.get(shooter_id, [])

        while True:
            viable = []

            for index, candidate in enumerate(candidates):
                if candidate.exhausted:
                    continue

                target = self.shadows[candidate.target_id]

                if not target.operative or target.force_id in self.broken_forces:
                    # Fuori combattimento, oppure la sua forza ha rotto il contatto: un
                    # bersaglio DISINGAGGIATO e' vivo ma non piu' raggiungibile.
                    candidate.exhausted = True
                    continue

                t_fire = max(candidate.t_ready, t_earliest)

                if candidate.not_before is not None:
                    t_fire = max(t_fire, candidate.not_before)

                if t_fire > candidate.t_end + TIME_EPS:
                    candidate.exhausted = True
                    continue

                viable.append((t_fire, index, candidate))

            if not viable:
                return

            # Regola L2 (2026-09-28): i lanciatori aria-superficie contro la mia forza, gia' a
            # portata, passano davanti a ogni altro bersaglio; fra loro resta la copertura (piu'
            # lanciatori -> il lavoro si ripartisce, uno solo -> tutti su di lui).
            priority = [item for item in viable
                        if self._is_launcher_against(item[2].target_id, shooter.force_id)
                        and self._in_range_at(shooter, item[1], item[2], item[0])]

            # Dottrina di tiro (2026-09-29): fuori i bersagli saturi per la forza (i lanciatori
            # prioritari ne sono esenti) e quelli su cui il tiratore ha gia' in volo il tetto di
            # colpi; se non resta nulla il tiratore aspetta il primo impatto e ridecide.
            pool = priority or viable
            open_pool = [item for item in pool if not self._blocked(shooter, item[2].target_id, bool(priority))]

            if not open_pool:
                if self._wait(shooter, pool, t_earliest):
                    return
            else:
                pool = open_pool

            # Round-robin (v. docstring): primo istante utile, poi copertura, poi il resto.
            t_first = min(t_fire for t_fire, _, _ in pool)
            best = None

            for t_fire, index, candidate in pool:
                if not priority and t_fire > t_first + TIME_EPS:
                    continue

                engaged = self._engaged_shooters(candidate.target_id, shooter.force_id, shooter_id)
                key = (engaged, t_fire, candidate.t_ready, candidate.target_id, index)

                if best is None or key < best:
                    best = key

            _, t_fire, _, target_id, index = best
            choice = self._first_with_stock(shooter, self.fire_control(shooter.asset, self.shadows[target_id].asset))

            if choice is None:
                # ROE o arma inadatta (None), oppure nessuna delle armi adatte ha piu'
                # scorta: questo bersaglio non verra' piu' ingaggiato da lui.
                candidates[index].exhausted = True
                continue

            spec, rounds = choice

            if spec.max_range is not None:
                # Controllo di portata (v. docstring del modulo): il tiro parte solo col
                # bersaglio entro max_range. Mai in portata nella finestra -> come un None,
                # ma solo per questa coppia/finestra. Ingresso piu' tardi -> il candidato
                # viene rimandato a quell'istante e la scelta si ripete: nel frattempo il
                # tiratore puo' ingaggiare un altro bersaglio gia' in portata.
                t_in_range = self._range_entry(shooter_id, candidates[index], spec.max_range, t_fire)

                if t_in_range is None:
                    candidates[index].exhausted = True
                    continue

                if t_in_range > t_fire + TIME_EPS:
                    candidates[index].not_before = t_in_range
                    continue

            self.assigned[shooter_id] = target_id
            self.assigned_shot[shooter_id] = (spec, rounds, t_fire)
            self._push(t_fire, _LAUNCH, shooter_id, (index, spec, rounds, self.launch_generation.get(shooter_id, 0)))
            return

    # ── dottrina di tiro: saturazione e "due missili, poi guarda" (2026-09-29) ──

    def _force_shots_on(self, target_id: str, force_id: str):
        """(ShotSpec, colpi, istante di arrivo) delle salve della forza dirette a `target_id`:
        in volo (non ancora risolte) o schedulate e non ancora lanciate."""
        for salvo in self.in_flight.values():
            if salvo.target_id == target_id and self.shadows[salvo.shooter_id].force_id == force_id:
                yield salvo.spec, salvo.rounds, salvo.t_impact, salvo.shooter_id

        for other_id, assigned in self.assigned.items():
            shot = self.assigned_shot.get(other_id)

            if assigned == target_id and shot is not None and self.shadows[other_id].force_id == force_id:
                spec, rounds, t_fire = shot

                if t_fire < self.now - TIME_EPS:
                    continue   # lancio gia' passato e non eseguito: non copre nulla

                yield spec, rounds, t_fire + float(spec.time_of_flight), other_id

    def _coverage(self, target_id: str, force_id: str) -> float:
        """P_cov: probabilita' che le salve gia' dirette dalla forza distruggano il bersaglio.

        Esito KILL del modello di danno (accuracy x destroy_capacity per colpo), colpi
        indipendenti; intercettazioni ignorate (decisione O5).
        """
        survival = 1.0

        for spec, rounds, _, _ in self._force_shots_on(target_id, force_id):
            survival *= (1.0 - spec.accuracy * spec.destroy_capacity) ** rounds

        return 1.0 - survival

    def _rounds_in_flight(self, shooter_id: str, target_id: str) -> int:
        return sum(salvo.rounds for salvo in self.in_flight.values()
                   if salvo.shooter_id == shooter_id and salvo.target_id == target_id)

    def _blocked(self, shooter: _Shadow, target_id: str, exempt_from_saturation: bool) -> bool:
        """Il tiratore non deve aggiungere salve su `target_id` (tetto o saturazione)."""
        fire = self.force_states[shooter.force_id].fire
        cap = fire.get(Doctrine.FIRE_MAX_ROUNDS_IN_FLIGHT)

        if cap is not None and self._rounds_in_flight(shooter.id, target_id) >= cap:
            return True

        threshold = fire.get(Doctrine.FIRE_KILL_THRESHOLD)

        if threshold is None or exempt_from_saturation:
            return False

        return self._coverage(target_id, shooter.force_id) >= threshold - FRACTION_EPS

    def _wait(self, shooter: _Shadow, pool, t_earliest: float) -> bool:
        """Tutti i bersagli bloccati: ridecisione al primo impatto previsto su uno di essi (O6).

        La ridecisione avviene al piu' tardi fra quell'impatto e `t_earliest`, il primo istante in
        cui il tiratore potrebbe comunque sparare: l'attesa non accorcia mai il ciclo di tiro.

        Returns:
            True se l'attesa e' stata programmata; False se non c'e' nessun impatto da aspettare
            (non dovrebbe accadere: un blocco nasce solo da salve in volo o schedulate), nel qual
            caso il chiamante procede senza il filtro, per non fermare il tiratore per sempre.
        """
        arrivals = [t_arrival + self.salvo_window
                    for _, _, candidate in pool
                    for _, _, t_arrival, _ in self._force_shots_on(candidate.target_id, shooter.force_id)]

        if not arrivals:
            return False

        self._push(max(min(arrivals), t_earliest, self.now), _DECIDE, shooter.id,
                   self.launch_generation.get(shooter.id, 0))
        return True

    def _is_launcher_against(self, asset_id: str, force_id: str) -> bool:
        return asset_id in self.launchers_against.get(force_id, ())

    def _in_range_at(self, shooter: "_Shadow", index: int, candidate: "_Candidate", t_fire: float) -> bool:
        """Il bersaglio del candidato e' ingaggiabile (arma con scorta, entro portata) a t_fire?

        Stessa scelta d'arma e stesso controllo di portata della schedulazione, senza effetti
        collaterali sul candidato. Senza portata dichiarata: ingaggiabile.
        """
        choice = self._first_with_stock(shooter, self.fire_control(shooter.asset,
                                                                   self.shadows[candidate.target_id].asset))

        if choice is None:
            return False

        spec, _ = choice

        if spec.max_range is None:
            return True

        t_in_range = self._range_entry(shooter.id, candidate, spec.max_range, t_fire)
        return t_in_range is not None and t_in_range <= t_fire + TIME_EPS

    def _register_launcher(self, time: float, launcher: "_Shadow", target_force_id: str) -> None:
        """Regola L3 (2026-09-28): primo lancio aria-superficie di un aereo contro una forza.

        I tiratori di quella forza che lo hanno fra i candidati e a portata, e che non sono gia'
        impegnati su un lanciatore (o gia' in ridecisione), rinunciano al lancio programmato su
        un bersaglio non prioritario (generazione) e RIDECIDONO dopo il loro `refire_interval`
        (VAL + COM + ATT del profilo di reazione): il tempo per valutare la minaccia e
        riassegnare il lavoro (decisione Q3/Q4), senza costanti nuove. La decisione e' presa
        ALLA FINE di quel tempo (evento _DECIDE) con cio' che si sa allora: piu' lanciatori
        comparsi nel frattempo vengono ripartiti fra le difese (copertura, L2).
        """
        launchers = self.launchers_against.setdefault(target_force_id, set())

        if launcher.id in launchers:
            return

        launchers.add(launcher.id)

        for shooter_id in sorted(self.candidates):
            shooter = self.shadows[shooter_id]

            if shooter.force_id != target_force_id or not shooter.operative \
                    or shooter.force_id in self.broken_forces:
                continue

            if shooter_id in self.pending_decide \
                    or self._is_launcher_against(self.assigned.get(shooter_id), target_force_id):
                continue

            t_decide = time + self._profile(shooter_id).refire_interval

            for index, candidate in enumerate(self.candidates[shooter_id]):
                if candidate.target_id != launcher.id or candidate.exhausted:
                    continue

                t_fire = max(candidate.t_ready, t_decide)

                if t_fire > candidate.t_end + TIME_EPS or not self._in_range_at(shooter, index, candidate, t_fire):
                    continue

                generation = self.launch_generation.get(shooter_id, 0) + 1
                self.launch_generation[shooter_id] = generation
                self.assigned.pop(shooter_id, None)
                self.pending_decide.add(shooter_id)
                self._push(t_decide, _DECIDE, shooter_id, generation)
                break

    def _on_decide(self, time: float, shooter_id: str, generation: int) -> None:
        """Fine della valutazione dopo una prelazione (L3): nuova decisione con lo stato attuale."""
        if generation != self.launch_generation.get(shooter_id, 0):
            return

        self.pending_decide.discard(shooter_id)
        self._schedule_next(shooter_id, time)

    @staticmethod
    def _options(result) -> Tuple[ShotSpec, ...]:
        """Le opzioni di una risposta della fire control: None, una ShotSpec o una sequenza."""
        if result is None:
            return ()

        if isinstance(result, ShotSpec):
            return (result,)

        if isinstance(result, (str, bytes)) or not isinstance(result, abc.Sequence):
            raise TypeError(f"fire_control must return a ShotSpec, a sequence of ShotSpec or None, "
                            f"got {type(result).__name__}")

        for option in result:
            if not isinstance(option, ShotSpec):
                raise TypeError(f"fire_control sequences must contain only ShotSpec, got {type(option).__name__}")

        return tuple(result)

    def _first_with_stock(self, shooter: _Shadow, result) -> Optional[Tuple[ShotSpec, int]]:
        """(ShotSpec, colpi) della prima opzione la cui arma ha scorta per almeno un colpo.

        colpi = min(spec.rounds, scorta // stock_per_round); con scorta non vincolante
        (None) colpi = spec.rounds. None se nessuna opzione ha scorta (o nessuna opzione).
        """
        for spec in self._options(result):
            stock = shooter.available(spec.weapon)

            if stock is None:
                return spec, spec.rounds

            rounds = min(spec.rounds, stock // spec.stock_per_round)

            if rounds >= 1:
                return spec, rounds

        return None

    def _range_entry(self, shooter_id: str, candidate: _Candidate, max_range: float,
                     t_from: float) -> Optional[float]:
        """Primo istante in [t_from, candidate.t_end] con il bersaglio entro la portata, o None.

        Solo SCELTA dell'istante: il "da quando a quando il bersaglio e' a portata" e'
        delegato a `self.engagement_intervals` (con i tratti di rotta) o a
        `engagement_intervals_without_legs` (senza), memoizzato per (tiratore, bersaglio,
        portata). Sostituire la geometria (volumi d'ingaggio non sferici) non tocca questa
        logica ne' la schedulazione.
        """
        key = (shooter_id, candidate.target_id, float(max_range))

        if key not in self.range_cache:
            legs_shooter = self.legs.get(shooter_id)
            legs_target = self.legs.get(candidate.target_id)

            if legs_shooter and legs_target:
                intervals = self.engagement_intervals(legs_shooter, legs_target, float(max_range))
            else:
                intervals = engagement_intervals_without_legs(candidate.t_cpa, candidate.distance_cpa,
                                                              candidate.t_end, float(max_range))

            self.range_cache[key] = list(intervals)

        t_until = candidate.t_end + TIME_EPS

        for start, end in self.range_cache[key]:
            if end < t_from - TIME_EPS:
                continue

            entry = max(start, t_from)
            return entry if entry <= t_until else None

        return None

    def _refire_interval(self, shooter_id: str, spec: ShotSpec) -> float:
        return spec.cycle_time if spec.cycle_time is not None else self._profile(shooter_id).refire_interval

    def _on_launch(self, time: float, shooter_id: str, payload) -> None:
        index, spec, rounds, generation = payload

        if generation != self.launch_generation.get(shooter_id, 0):
            # Lancio annullato dalla prelazione (regola L3): il tiratore ha gia' un nuovo
            # lancio programmato, questo evento non fa nulla.
            return

        # Il lancio schedulato si esaurisce qui, qualunque sia l'esito: se la salva parte,
        # la copertura passa a `in_flight`; se e' annullata, non copre piu' nulla.
        self.assigned.pop(shooter_id, None)

        shooter = self.shadows[shooter_id]

        if shooter.force_id in self.broken_forces:
            # La forza del lanciatore ha rotto il contatto: il lancio non ancora eseguito e'
            # annullato, e il tiratore non ne schedula altri.
            return

        if not shooter.operative:
            # Lanciatore fuori combattimento prima del lancio: la salva non parte.
            return

        candidate = self.candidates[shooter_id][index]
        target = self.shadows[candidate.target_id]
        next_time = time + self._refire_interval(shooter_id, spec)

        if not target.operative or target.force_id in self.broken_forces \
                or time > candidate.t_end + TIME_EPS:
            # Bersaglio fuori combattimento, la sua forza ha rotto il contatto, o finestra
            # chiusa. Annullamento, non riscrittura (R4): la prossima decisione e' un nuovo
            # evento (con N forze il tiratore puo' passare a un bersaglio di un'altra forza).
            candidate.exhausted = True
            self._schedule_next(shooter_id, next_time)
            return

        units = rounds * spec.stock_per_round
        stock = shooter.available(spec.weapon)

        if stock is not None and stock < units:
            # Scorta dell'arma erosa dopo lo scheduling: stesso trattamento. Succede quando
            # le intercettazioni fra scheduling e lancio consumano la stessa voce (un
            # missile AD e' uno solo, v. "Scorta per arma"); il controllo difende anche
            # l'invariante "la scorta non va mai sotto zero".
            self._schedule_next(shooter_id, next_time)
            return

        shooter.consume(spec.weapon, units)
        self.ammunition_events.append(AmmunitionEvent(time=time, asset_id=shooter_id, rounds=units,
                                                      weapon=spec.weapon))

        salvo = Salvo(salvo_id=len(self.salvos), t_launch=time,
                      t_impact=time + float(spec.time_of_flight), shooter_id=shooter_id,
                      target_id=target.id, target_force_id=target.force_id,
                      rounds=rounds, spec=spec)
        self.salvos.append(salvo)
        self.in_flight[salvo.salvo_id] = salvo
        self._touch(time)
        self._push(salvo.t_impact, _IMPACT, target.force_id, salvo)
        self._schedule_next(shooter_id, next_time)

        # RWR che rileva solo tracciamento/guida (SPO-10): la minaccia e' percepita al lancio.
        if ADE.rwr_perception(target.asset, shooter.asset) == ADE.PERCEIVED_AT_LAUNCH:
            self._perceive(target.force_id, shooter_id, time)

        if validate_class(shooter.asset, 'Aircraft') and not validate_class(target.asset, 'Aircraft'):
            self._register_launcher(time, shooter, target.force_id)

    # ── fase 3: impatto, saturazione, danno ───────────────────────────────────

    def _on_impact(self, time: float, force_id: str, salvo: Salvo) -> None:
        group = self.pending.get(force_id)

        if group is None or time > group.resolve_time + TIME_EPS:
            group = _PendingGroup(resolve_time=time + self.salvo_window)
            self.pending[force_id] = group
            self._push(group.resolve_time, _RESOLVE, force_id, None)

        group.salvos.append(salvo)

    def _capacity(self, state: _ForceState) -> int:
        """Capacita' di intercettazione attuale: stessa formula di Military.salvo_interception_capacity."""
        capacity = 0

        for shadow, channels in state.interceptors:
            if not shadow.operative:
                continue

            stock = shadow.interceptor_stock
            capacity += channels if stock is None else min(channels, stock)

        return capacity

    def _position_at(self, shadow: "_Shadow", t: float) -> Optional[Tuple[float, float, float]]:
        """Posizione (x, y, z) all'istante t: dai tratti di rotta se ci sono, altrimenti la
        posizione dell'asset (ferma). None se non nota."""
        position = position_on_legs(self.legs.get(shadow.id) or (), t)

        if position is not None:
            return position

        point = getattr(shadow.asset, 'position', None)

        try:
            return float(point.x), float(point.y), float(point.z)
        except (AttributeError, TypeError, ValueError):
            return None

    def _interception_zone(self, shadow: "_Shadow") -> Optional[Tuple[float, float, float]]:
        """V_I dell'intercettore come (raggio, quota base, quota tetto) RELATIVI alla sua
        posizione, da Mobile.air_defense_volume(); memoizzato. None = zona non modellata."""
        if shadow.id not in self.zone_cache:
            zone = None
            volume_of = getattr(shadow.asset, 'air_defense_volume', None)
            volume = volume_of() if callable(volume_of) else None
            point = getattr(shadow.asset, 'position', None)

            if volume is not None and type(volume).__name__ == 'Cylinder' and point is not None:
                try:
                    base = float(volume.center.z) - float(point.z)
                    zone = (float(volume.radius), base, base + float(volume.height))
                except (AttributeError, TypeError, ValueError):
                    zone = None

            self.zone_cache[shadow.id] = zone

        return self.zone_cache[shadow.id]

    def _may_intercept(self, shadow: "_Shadow", salvo: Salvo) -> bool:
        """Regola L1: True se il punto di lancio della salva e' FUORI dal V_I dell'intercettore.

        Posizioni all'istante del lancio (l'intercettore puo' essere in moto, es. una nave).
        Senza zona, o senza posizione del lanciatore o dell'intercettore, nessun vincolo
        (dato mancante = non modellato, come per scorte e carburante).
        """
        key = (shadow.id, salvo.salvo_id)

        if key not in self.may_intercept_cache:
            allowed = True
            zone = self._interception_zone(shadow)
            launch = self._position_at(self.shadows[salvo.shooter_id], salvo.t_launch)
            here = self._position_at(shadow, salvo.t_launch)

            if zone is not None and launch is not None and here is not None:
                radius, bottom, top = zone
                horizontal = ((launch[0] - here[0]) ** 2 + (launch[1] - here[1]) ** 2) ** 0.5
                height = launch[2] - here[2]
                allowed = not (horizontal <= radius and bottom <= height <= top)

            self.may_intercept_cache[key] = allowed

        return self.may_intercept_cache[key]

    def _detection_time_of(self, observer_id: str, target_id: str) -> Optional[float]:
        """Istante in cui `observer_id` ha rilevato `target_id` (None = mai rilevato)."""
        if self.detected_at is None:
            self.detected_at = {(d.observer_id, d.target_id): d.time
                                for d in self.detections if d.detected and d.time is not None}

        return self.detected_at.get((observer_id, target_id))

    def _air_detection_range(self, shadow: "_Shadow") -> Optional[float]:
        """Raggio di rilevamento aereo dell'intercettore [m], memoizzato. None = non modellato."""
        if shadow.id not in self.air_range_cache:
            value = None
            range_of = getattr(shadow.asset, 'detection_range', None)

            if callable(range_of):
                try:
                    value = range_of('air')
                except (TypeError, ValueError, AttributeError):
                    value = None

            ok = isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0
            self.air_range_cache[shadow.id] = float(value) if ok else None

        return self.air_range_cache[shadow.id]

    def _round_track_time(self, shadow: "_Shadow", salvo: Salvo) -> Optional[float]:
        """Istante in cui l'intercettore scopre dalla geometria un colpo di cui non ha visto il lancio.

        Il colpo vola in linea retta a velocita' costante dal punto di lancio alla posizione del
        bersaglio all'impatto; l'intercettore e' fermo nella posizione dell'istante di lancio.
        Restituisce il primo istante in cui il colpo e' entro il suo raggio di rilevamento aereo,
        None se non ci entra mai. Senza raggio o senza posizioni: t_launch (dato mancante = nessun
        vincolo geometrico).
        """
        radius = self._air_detection_range(shadow)
        start = self._position_at(self.shadows[salvo.shooter_id], salvo.t_launch)
        end = self._position_at(self.shadows[salvo.target_id], salvo.t_impact)
        here = self._position_at(shadow, salvo.t_launch)

        if radius is None or start is None or end is None or here is None:
            return salvo.t_launch

        d = [e - a for a, e in zip(start, end)]
        f = [a - q for a, q in zip(start, here)]
        a = sum(x * x for x in d)
        b = 2.0 * sum(x * y for x, y in zip(f, d))
        c = sum(x * x for x in f) - radius * radius

        if c <= 0.0:
            return salvo.t_launch

        disc = b * b - 4.0 * a * c

        if a <= 0.0 or disc < 0.0:
            return None

        s = (-b - disc ** 0.5) / (2.0 * a)

        if not 0.0 <= s <= 1.0:
            return None

        return salvo.t_launch + s * (salvo.t_impact - salvo.t_launch)

    def _in_time(self, shadow: "_Shadow", salvo: Salvo) -> bool:
        """Regola R-INT (2026-09-30, Proposta_Intercettazione_Reazione.md): l'intercettore ferma
        i colpi della salva solo se ne ha una traccia e il tempo di reagire prima dell'impatto,
        t_traccia + tau <= t_impact.

        Lancio osservato (l'intercettore aveva gia' rilevato il lanciatore all'istante del lancio):
        t_traccia = t_launch, tau = refire_interval (VAL+COM+ATT). Altrimenti il colpo e' una
        traccia nuova, scoperta dalla geometria (`_round_track_time`): tau = total
        (RIV+VAL+COM+ATT). Rilevamento per asset (nessun quadro condiviso fino alla Fase 0 C2) e
        deterministico (nessuna estrazione: il flusso RNG non cambia).
        """
        key = (shadow.id, salvo.salvo_id)

        if key not in self.in_time_cache:
            profile = self._profile(shadow.id)
            seen = self._detection_time_of(shadow.id, salvo.shooter_id)

            if seen is not None and seen <= salvo.t_launch + TIME_EPS:
                t_track, tau = salvo.t_launch, profile.refire_interval
            else:
                t_track, tau = self._round_track_time(shadow, salvo), profile.total

            self.in_time_cache[key] = t_track is not None and t_track + tau <= salvo.t_impact + TIME_EPS

        return self.in_time_cache[key]

    def _on_resolve(self, time: float, force_id: str) -> None:
        group = self.pending.pop(force_id, None)

        if group is None or not group.salvos:
            return

        state = self.force_states[force_id]
        committed = state.committed
        before = {asset_id for asset_id in committed if self.shadows[asset_id].operative}
        ordered = sorted(group.salvos, key=lambda s: (s.t_impact, s.salvo_id))

        for salvo in ordered:
            self.in_flight.pop(salvo.salvo_id, None)

        rounds = sum(s.rounds for s in ordered)
        interceptable = sum(s.rounds for s in ordered if s.spec.interceptable)
        capacity = self._capacity(state)

        # Allocazione PER SALVA (regola L1, 2026-09-28, Proposta_Regole_Allocazione_SAM.md §7):
        # un colpo intercettabile e' fermato solo da un intercettore per cui il punto di lancio
        # della salva e' FUORI dal proprio volume d'intercettazione V_I (Mobile.air_defense_volume):
        # un lanciatore che ha sparato da dentro la zona e' un bersaglio, non si inseguono i suoi
        # colpi. Salve nell'ordine (impatto, salva), intercettori nell'ordine della regola F, ogni
        # intercettore fino a min(canali, scorta) per evento. Senza vincoli geometrici (nessun
        # dato di volume o di posizione) il risultato coincide con l'allocazione sul totale usata
        # fino al 2026-09-28: stessi consumi per intercettore, stesse salve fermate.
        available = {}

        for shadow, channels in state.interceptors:
            if shadow.operative:
                stock = shadow.interceptor_stock
                available[shadow.id] = channels if stock is None else min(channels, stock)

        used: Dict[str, int] = {}
        stopped: Dict[int, int] = {}

        for salvo in ordered:
            if not salvo.spec.interceptable:
                continue

            left = salvo.rounds

            for shadow, _ in state.interceptors:
                if left <= 0:
                    break

                free = available.get(shadow.id, 0) - used.get(shadow.id, 0)

                if free <= 0 or not self._may_intercept(shadow, salvo) or not self._in_time(shadow, salvo):
                    continue

                take = min(free, left)
                used[shadow.id] = used.get(shadow.id, 0) + take
                left -= take

            if left < salvo.rounds:
                stopped[salvo.salvo_id] = salvo.rounds - left

        intercepted = sum(stopped.values())

        # Ogni intercettazione consuma la scorta di INTERCETTORI del difensore (R3,
        # ricalibrazione 2026-09-23) — dal 2026-09-26 le voci AD della sua scorta per arma,
        # cannoni prima e poi missili (v. _Shadow) — ed e' un InterceptionEvent (uno per
        # arma), mai un AmmunitionEvent: consumo esplicito, asset nell'ordine F.
        salvo_ids = tuple(s.salvo_id for s in ordered)

        for shadow, _ in state.interceptors:
            count_used = used.get(shadow.id, 0)

            if count_used <= 0:
                continue

            for weapon, count in shadow.consume_interceptions(count_used):
                self.interception_events.append(InterceptionEvent(time=time, asset_id=shadow.id,
                                                                  interceptions=count, force_id=force_id,
                                                                  salvo_ids=salvo_ids, weapon=weapon))

        wasted = 0

        for salvo in ordered:
            target = self.shadows[salvo.target_id]

            for _ in range(salvo.rounds - stopped.get(salvo.salvo_id, 0)):
                if target.destroyed:
                    # Payload congelato (R4): il colpo arriva comunque, ma su un relitto.
                    wasted += 1
                    continue

                was_operative = target.operative
                event = DM.build_damage_event(target, salvo.spec.accuracy, salvo.spec.destroy_capacity,
                                              self._draw(), time=time, source_id=salvo.shooter_id,
                                              weapon=salvo.spec.weapon, provenance=self.provenance)
                target.health = event.health_after
                self.damage_events.append(event)

                if was_operative and not target.operative:
                    # Chi ha messo fuori combattimento l'asset (fuoco senza risposta, D5).
                    state.loss_shooters[target.id] = (salvo.shooter_id, time)

        after = {asset_id for asset_id in committed if self.shadows[asset_id].operative}
        losses = tuple(sorted(before - after))
        shock = len(losses) / len(committed)
        erosion = (len(committed) - len(after)) / len(committed)

        self.resolutions.append(SalvoResolution(time=time, force_id=force_id,
                                                salvo_ids=salvo_ids,
                                                rounds=rounds, interceptable_rounds=interceptable,
                                                capacity=capacity, intercepted=intercepted,
                                                wasted=wasted, losses=losses, shock=shock,
                                                erosion=erosion))
        self._touch(time)
        self._check_doctrine(time, state, shock, erosion, len(after), len(losses))

    # ── fase 4: disingaggio ───────────────────────────────────────────────────

    def _check_doctrine(self, time: float, state: _ForceState, shock: float, erosion: float,
                        operative_left: int, salvo_losses: int = 0) -> None:
        """Confronta le perdite con la dottrina del lato, per la FORZA INTERA (P1 + R2).

        Le due soglie sono verificate con la stessa regola per entrambi i lati: nessun
        trattamento speciale per chi ha colpito o per chi ha iniziato (R2 lo richiede
        esplicitamente, per non ereditare l'applicazione incoerente della fonte). Dal
        2026-09-29 la soglia di erosione e' la soglia di rottura B(t) della forza e quella di
        shock (shock / erosion) x B(t), con un minimo di perdite nella salva (v. "Soglia di
        rottura" nel docstring del modulo).
        """
        state.max_shock = max(state.max_shock, shock)

        if operative_left == 0:
            # Annientamento: prevale su un disingaggio gia' deciso (la forza e' stata
            # distrutta mentre rompeva il contatto, da salve gia' in volo).
            if state.outcome != DESTROYED:
                state.outcome = DESTROYED
                state.time = time
                state.triggers = (TRIGGER_ANNIHILATION,)
            self.broken_forces.add(state.force_id)
            return

        if state.outcome is not None or state.thresholds is None:
            return

        breakpoint = self._breakpoint(time, state)
        median = state.thresholds[Doctrine.DISENGAGEMENT_EROSION]
        shock_threshold = state.thresholds[Doctrine.DISENGAGEMENT_SHOCK] * (breakpoint / median)
        min_losses = Doctrine.disengagement_parameter(state.thresholds, Doctrine.SHOCK_MIN_LOSSES)
        triggers = []

        if erosion >= breakpoint - FRACTION_EPS:
            triggers.append(TRIGGER_EROSION)

        if salvo_losses >= min_losses and shock >= shock_threshold - FRACTION_EPS:
            triggers.append(TRIGGER_SHOCK)

        if triggers:
            state.outcome = DISENGAGED
            state.time = time
            state.triggers = tuple(triggers)
            self.broken_forces.add(state.force_id)
            logger.debug(f"force {state.force_id!r} disengages at t={time} ({triggers}): "
                         f"erosion={erosion:.3f}, shock={shock:.3f}, breakpoint={breakpoint:.3f}")

    # ── soglia di rottura stocastica (2026-09-29) ─────────────────────────────

    def _init_breakpoints(self) -> None:
        """Tempra, morale, stima a priori e postura di ogni forza con dottrina.

        Un'estrazione della tempra per forza, nell'ordine di ingresso delle forze, dal flusso
        SEPARATO `breakpoint_rng` e solo se la dottrina ha dispersione > 0: l'ordine delle
        estrazioni di rilevamento e danno (`rng`) non cambia. Senza `breakpoint_rng` la tempra
        non e' estratta (z = 0, soglia alla mediana): politica dichiarata per le chiamate
        dirette senza flusso dedicato.
        """
        for force_id in self.force_order:
            state = self.force_states[force_id]

            if state.thresholds is None:
                continue

            state.air = bool(state.committed) and all(
                validate_class(self.shadows[asset_id].asset, 'Aircraft') for asset_id in state.committed)
            state.morale = self._morale_of(state)
            state.enemy_estimate = self._enemy_estimate_of(state)
            state.stationary = self._stationary(state)

            dispersion = Doctrine.disengagement_parameter(state.thresholds, Doctrine.BREAKPOINT_DISPERSION)

            if dispersion > 0.0 and self.breakpoint_rng is not None:
                u = float(self.breakpoint_rng.random())

                if not 0.0 <= u < 1.0:
                    raise ValueError(f"breakpoint_rng.random() must return a float in [0, 1), got {u!r}")

                u = min(max(u, BREAKPOINT_U_EPS), 1.0 - BREAKPOINT_U_EPS)
                state.temper = u
                state.temper_z = NormalDist().inv_cdf(u)

    def _morale_of(self, state: _ForceState) -> Optional[float]:
        if self.morale_for is None:
            return None

        value = self.morale_for(state.force)

        if value is None:
            return None

        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0.0 <= value <= 1.0:
            logger.warning(f"resolve_engagement: morale {value!r} of force {state.force_id!r} not in [0, 1], "
                           f"treated as unknown (neutral)")
            return None

        return float(value)

    def _enemy_estimate_of(self, state: _ForceState) -> Optional[float]:
        if self.enemy_estimate_for is None:
            return None

        value = self.enemy_estimate_for(state.force)

        if value is None:
            return None

        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
            logger.warning(f"resolve_engagement: enemy estimate {value!r} of force {state.force_id!r} "
                           f"not a number >= 0, ignored")
            return None

        return float(value)

    def _stationary(self, state: _ForceState) -> Optional[bool]:
        """True se tutti gli asset con tratti di rotta sono fermi; None se nessuno ne ha."""
        known = False

        for asset_id in state.committed:
            legs = self.legs.get(asset_id)

            if not legs:
                continue

            known = True

            for leg in legs:
                if any(abs(a - b) > STATIONARY_EPS for a, b in zip(leg.p_start, leg.p_end)):
                    return False

        return True if known else None

    def _is_enemy(self, state: _ForceState, shadow: _Shadow) -> bool:
        if shadow.force_id == state.force_id:
            return False

        other = self.force_states[shadow.force_id].side

        return state.side is None or other is None or other != state.side

    def _perceived_ratio(self, time: float, state: _ForceState) -> Optional[float]:
        """rho(t): forza propria / forza nemica percepita (D4a-D4e), None se non definito."""
        seen = self.seen_by.get(state.force_id, {})
        enemies = [self.shadows[asset_id] for asset_id, t_seen in seen.items()
                   if t_seen <= time + TIME_EPS and self._is_enemy(state, self.shadows[asset_id])
                   and not self.shadows[asset_id].destroyed]
        own = [self.shadows[asset_id] for asset_id in state.committed if self.shadows[asset_id].operative]

        if state.air:
            n_aircraft = len(own)
            # Scorta di DOTAZIONE (registro), non quella residua: chi osserva un sistema AD non sa
            # quanti missili gli restano, puo' solo presumere la dotazione (stima, non dato certo).
            threat = sum(ADE.air_threat_weight(shadow.asset, n_aircraft) for shadow in enemies)

            if state.enemy_estimate is not None:
                threat = max(threat, state.enemy_estimate)

            if threat <= 0.0:
                return None

            scale = Doctrine.disengagement_parameter(state.thresholds, Doctrine.AIR_FORCE_RATIO_SCALE)

            return n_aircraft / (scale * threat)

        enemy = sum(self._surface_weight(shadow) for shadow in enemies)

        if state.enemy_estimate is not None:
            enemy = max(enemy, state.enemy_estimate)

        own_strength = sum(self._surface_weight(shadow) for shadow in own)

        if enemy <= 0.0 or own_strength <= 0.0:
            return None

        return own_strength / enemy

    def _surface_weight(self, shadow: _Shadow) -> float:
        weight = self.surface_weights.get(shadow.id)

        if weight is None:
            weight = ADE.surface_threat_weight(shadow.asset)
            self.surface_weights[shadow.id] = weight

        return weight

    def _unanswered_fraction(self, state: _ForceState) -> float:
        """Quota delle perdite causate da tiratori che la forza non aveva rilevato (D5)."""
        if not state.loss_shooters:
            return 0.0

        seen = self.seen_by.get(state.force_id, {})
        unanswered = sum(1 for shooter_id, t_loss in state.loss_shooters.values()
                         if seen.get(shooter_id, float('inf')) > t_loss + TIME_EPS)

        return unanswered / len(state.loss_shooters)

    def _breakpoint(self, time: float, state: _ForceState) -> float:
        """B(t) = logistic(logit(mu_eff) + dispersion x z), v. Context/Doctrine."""
        thresholds = state.thresholds
        median = thresholds[Doctrine.DISENGAGEMENT_EROSION]

        if median >= 1.0 - FRACTION_EPS:
            # "Combatte fino all'annientamento": nessuna modulazione.
            state.breakpoint = 1.0
            return 1.0

        param = lambda key: Doctrine.disengagement_parameter(thresholds, key)
        factor = 1.0

        if state.morale is not None:
            factor *= 1.0 + param(Doctrine.MORALE_WEIGHT) * (2.0 * state.morale - 1.0)

        rho = self._perceived_ratio(time, state)
        state.force_ratio = rho
        exponent = param(Doctrine.FORCE_RATIO_EXPONENT)

        if rho is not None and exponent > 0.0:
            low, high = param(Doctrine.FORCE_RATIO_BOUNDS)
            factor *= min(max(rho ** exponent if rho > 0.0 else 0.0, low), high)

        state.unanswered_fraction = self._unanswered_fraction(state)
        factor *= 1.0 - param(Doctrine.UNANSWERED_FIRE_WEIGHT) * state.unanswered_fraction

        if state.stationary:
            factor *= param(Doctrine.DEFENSIVE_POSTURE_FACTOR)

        mu = median * factor

        if factor != 1.0:
            low, high = param(Doctrine.MEDIAN_BOUNDS)
            mu = min(max(mu, min(low, median)), max(high, median))

        dispersion = param(Doctrine.BREAKPOINT_DISPERSION)

        if dispersion > 0.0 and state.temper_z != 0.0:
            logit = math.log(mu / (1.0 - mu)) + dispersion * state.temper_z
            mu = 1.0 / (1.0 + math.exp(-logit))

        state.breakpoint = mu
        return mu

    # ── ciclo principale ──────────────────────────────────────────────────────

    def run(self) -> EngagementResult:
        self._detect()

        for shooter_id in sorted(self.candidates):
            self._schedule_next(shooter_id, float('-inf'))

        while self.queue:
            time, kind, key, _, payload = heapq.heappop(self.queue)
            self.now = time

            if kind == _LAUNCH:
                self._on_launch(time, key, payload)
            elif kind == _IMPACT:
                self._on_impact(time, key, payload)
            elif kind == _RESOLVE:
                self._on_resolve(time, key)
            else:
                self._on_decide(time, key, payload)

        return self._result()

    def _result(self) -> EngagementResult:
        outcomes = []

        for force_id in self.force_order:
            state = self.force_states[force_id]
            committed = len(state.committed)
            operative = sum(1 for asset_id in state.committed if self.shadows[asset_id].operative)
            lost = committed - operative

            outcomes.append(ForceOutcome(force_id=force_id, side=state.side,
                                         outcome=state.outcome or HELD, time=state.time,
                                         triggers=state.triggers, committed=committed, lost=lost,
                                         erosion=lost / committed if committed else 0.0,
                                         max_shock=state.max_shock, temper=state.temper,
                                         breakpoint=state.breakpoint, morale=state.morale,
                                         force_ratio=state.force_ratio,
                                         unanswered_fraction=state.unanswered_fraction))

        return EngagementResult(t_start=self.t_start,
                                t_end=self.t_end if self.t_end is not None else self.t_start,
                                forces=tuple(outcomes),
                                detections=tuple(self.detections),
                                salvos=tuple(self.salvos),
                                resolutions=tuple(self.resolutions),
                                damage_events=tuple(self.damage_events),
                                ammunition_events=tuple(self.ammunition_events),
                                interception_events=tuple(self.interception_events))


def resolve_engagement(force_a, force_b, contacts: Iterable, fire_control: Callable, rng, *,
                       extra_forces: Sequence = (),
                       legs: Optional[Mapping[str, Sequence]] = None,
                       committed: Optional[Mapping[str, Iterable[str]]] = None,
                       thresholds: Optional[Dict] = None,
                       reaction_profile_for: Optional[Callable] = None,
                       detection_factor: Optional[Callable] = None,
                       salvo_window: float = 0.0,
                       provenance: str = DM.DERIVED,
                       breakpoint_rng=None,
                       morale_for: Optional[Callable] = None,
                       enemy_estimate_for: Optional[Callable] = None,
                       fire_doctrine: Optional[Dict] = None) -> Optional[EngagementResult]:
    """Risolve un ingaggio fra due o piu' forze, in un'unica timeline. Non muta alcun asset.

    Args:
        force_a/force_b: due delle forze — `Military` o qualunque oggetto con `assets`
            (dict di asset), `side`, `name`; se espongono `salvo_interceptors()` la loro
            difesa satura le salve in arrivo (R1).
        extra_forces: altre forze della stessa run, oltre alle prime due (default nessuna:
            ingaggio a due, comportamento invariato). Le forze della run sono
            `(force_a, force_b, *extra_forces)`, tutte trattate allo stesso modo: nessuna
            delle prime due ha un ruolo speciale, l'ordine decide solo l'ordine di
            `EngagementResult.forces`. Chi combatte contro chi lo decidono le finestre in
            `contacts`, non i lati (v. "Ingaggi a N forze" nel docstring del modulo).
        contacts: le `ContactWindow` di `Contact_Scheduler` fra asset di forze diverse. Le
            finestre con asset non impegnati, o fra asset della stessa forza, sono ignorate.
            Con `range_type='engagement_range'` lo scheduler produce finestre "a tiro"
            invece che "a vista": la scelta e' del chiamante.
        fire_control: `(shooter, target) -> ShotSpec | Sequence[ShotSpec] | None`, riceve
            gli asset REALI (per la selezione dell'arma, non per leggerne lo stato: lo
            stato che evolve e' quello ombra del risolutore). Una sequenza e' l'ordine di
            preferenza: si spara con la prima opzione che ha scorta (v. "Scorta per arma").
        rng: oggetto con `.random()` in [0, 1), es. `random.Random(seed)`. Unica sorgente
            di casualita'.
        legs: `{asset_id: [Leg, ...]}` (`Contact_Scheduler.route_legs/static_legs`) per
            ricavare l'istante esatto di rilevamento; senza, v. `_detection_time`.
        committed: `{force_id: [asset_id, ...]}` per impegnare solo una parte della forza;
            di default tutti gli asset operativi.
        thresholds: tabella dottrinale al posto di `Doctrine.DEFAULT_DISENGAGEMENT_THRESHOLDS`.
        reaction_profile_for: `asset -> ReactionProfile`, default
            `Reaction_Profile.profile_for_asset`.
        detection_factor: `(observer, target) -> float in [0, 1]`, degradazione della Pd
            (meteo, notte, disturbo); default nessuna degradazione.
        salvo_window: secondi entro cui impatti successivi sulla stessa forza fanno parte
            dello STESSO evento-salva (saturazione e shock). Default 0: solo impatti
            simultanei — la scelta piu' conservativa; quale finestra usare e' un punto
            aperto di modello, da decidere con la taratura.
        provenance: provenienza dei DamageEvent prodotti (default DERIVED).
        breakpoint_rng: flusso casuale SEPARATO (oggetto con `.random()`) da cui estrarre la
            tempra di ogni forza (v. "Soglia di rottura"); None = tempra non estratta, soglia
            alla mediana modulata. Separato da `rng` perche' le sue estrazioni non spostino
            quelle di rilevamento e danno.
        morale_for: `force -> float in [0, 1] | None`, morale della forza; default None per
            tutte (neutro, mai "morale nullo").
        enemy_estimate_for: `force -> float >= 0 | None`, stima a priori della forza nemica
            (C2/ricognizione) nella stessa misura del rapporto percepito: minaccia
            antiaerea in aerei abbattuti attesi per una forza aerea, conteggio pesato per una
            di superficie. La forza nemica percepita e' il massimo fra stima e rilevato.
        fire_doctrine: tabella al posto di `Doctrine.DEFAULT_FIRE_DOCTRINE` (saturazione del
            bersaglio e tetto "due missili, poi guarda", v. `_blocked`); `{}` = nessuna regola.

    Returns:
        `EngagementResult`, oppure None (con un log) se meno di due forze hanno asset
        impegnabili — con due forze: se una delle due non ne ha. Con 3+ forze una forza
        senza asset impegnabili compare nell'esito con committed=0 e HELD.

    Raises:
        TypeError: `rng` senza `.random()`, `fire_control` non chiamabile o che non
            restituisce una ShotSpec, una sequenza di ShotSpec o None.
        ValueError: `salvo_window` negativo, provenance sconosciuta, forze ripetute o
            con asset in comune.
    """
    if not callable(getattr(rng, 'random', None)):
        raise TypeError("rng must expose a random() method returning a float in [0, 1)")

    if not callable(fire_control):
        raise TypeError("fire_control must be callable")

    if isinstance(salvo_window, bool) or not isinstance(salvo_window, (int, float)) or salvo_window < 0:
        raise ValueError(f"salvo_window must be a non-negative number, got {salvo_window!r}")

    if provenance not in DM.PROVENANCES:
        raise ValueError(f"provenance must be one of {DM.PROVENANCES}, got {provenance!r}")

    extra_forces = tuple(extra_forces) if extra_forces is not None else ()

    if breakpoint_rng is not None and not callable(getattr(breakpoint_rng, 'random', None)):
        raise TypeError("breakpoint_rng must expose a random() method returning a float in [0, 1)")

    for name, fn in (('morale_for', morale_for), ('enemy_estimate_for', enemy_estimate_for)):
        if fn is not None and not callable(fn):
            raise TypeError(f"{name} must be callable")

    run = _EngagementRun((force_a, force_b) + extra_forces, contacts, fire_control, rng, legs,
                         committed, thresholds, reaction_profile_for, detection_factor,
                         salvo_window, provenance, breakpoint_rng=breakpoint_rng,
                         morale_for=morale_for, enemy_estimate_for=enemy_estimate_for,
                         fire_doctrine=fire_doctrine)

    if not run.usable:
        return None

    return run.run()


def _call_with_weapon(consume: Callable, amount: int, weapon: Optional[str]) -> None:
    """`consume(amount, weapon=weapon)`; senza arma, la chiamata storica `consume(amount)`.

    Cosi' un asset duck-typed con la firma precedente al 2026-09-26 resta applicabile per
    gli eventi senza arma (pool anonimo).
    """
    if weapon is None:
        consume(amount)
    else:
        consume(amount, weapon=weapon)


def apply_engagement_result(result: EngagementResult, *forces) -> Dict[str, int]:
    """Applica un esito agli asset reali: danni (Damage_Model) e consumi di scorte.

    E' il passo separato che il risolutore non fa da se': cosi' un esito puo' essere
    ispezionato, confrontato fra repliche o scartato senza aver toccato la campagna.
    I DamageEvent si applicano nell'ordine in cui sono stati prodotti (i loro delta sono
    coerenti con quell'ordine); i consumi per tipo d'evento: gli `AmmunitionEvent` (salve)
    con `consume_ammunition(rounds, weapon=...)`, gli `InterceptionEvent` con
    `consume_interceptor_stock(interceptions, weapon=...)`: con la scorta per arma
    (2026-09-26) ciascun evento scala la voce della propria arma, la stessa scalata dallo
    stato ombra. Un asset stub senza il parametro `weapon` riceve la chiamata storica.

    Returns:
        {'damage_events': applicati, 'ammunition_events': applicati,
        'interception_events': applicati, 'missing_assets': non trovati} — un asset non
        trovato e' registrato e saltato, non e' un errore.
    """
    if not isinstance(result, EngagementResult):
        raise TypeError(f"result must be an EngagementResult, got {type(result).__name__}")

    assets: Dict[str, object] = {}

    for force in forces:
        for asset in (getattr(force, 'assets', None) or {}).values():
            asset_id = _domain_id(asset)

            if asset_id is not None:
                assets[asset_id] = asset

    summary = {'damage_events': 0, 'ammunition_events': 0, 'interception_events': 0, 'missing_assets': 0}

    for event in result.damage_events:
        asset = assets.get(event.target_id)

        if asset is None:
            logger.warning(f"apply_engagement_result: target {event.target_id!r} not found")
            summary['missing_assets'] += 1
            continue

        DM.apply_damage_event(asset, event)
        summary['damage_events'] += 1

    # Consumi nell'ORDINE in cui lo stato ombra li ha scalati (2026-09-26): per tempo, e a
    # parita' di istante i lanci prima delle intercettazioni (LANCIO < RISOLUZIONE nella
    # coda eventi); nell'ordine di produzione dentro ciascun tipo. Con la scorta per arma
    # l'ordine conta: un consumo che paga l'aggregato (arma non dichiarata) e
    # un'intercettazione sulla stessa voce non commutano quando la voce si esaurisce, e
    # applicarli in un ordine diverso da quello dell'ombra potrebbe lasciare sull'asset
    # uno stato diverso da quello che l'esito descrive.
    consumptions = sorted([(event.time, 0, index, event) for index, event in enumerate(result.ammunition_events)]
                          + [(event.time, 1, index, event) for index, event in enumerate(result.interception_events)],
                          key=lambda item: item[:3])

    for _, kind, _, event in consumptions:
        asset = assets.get(event.asset_id)

        if asset is None:
            role = 'shooter' if kind == 0 else 'interceptor'
            logger.warning(f"apply_engagement_result: {role} {event.asset_id!r} not found")
            summary['missing_assets'] += 1
            continue

        if kind == 0:
            consume = getattr(asset, 'consume_ammunition', None)

            if callable(consume):
                _call_with_weapon(consume, event.rounds, event.weapon)

            summary['ammunition_events'] += 1
            continue

        consume = getattr(asset, 'consume_interceptor_stock', None)

        if callable(consume):
            _call_with_weapon(consume, event.interceptions, event.weapon)

        summary['interception_events'] += 1

    return summary
