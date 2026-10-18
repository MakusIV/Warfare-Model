"""Dalla Missione al movimento per asset: rotta, partenza e velocita' che il motore consuma.

FASE 3 di `Analysis/Document/Piano_Implementazione_Missione.md` ("la Missione attraversa la
porta di sessione"). `Command/Mission_Types` e' solo struttura; la LOGICA che ricava, per ogni
asset di una `Mission`, la forma che `Session_Simulator.run_session` consuma (le tre mappe
`routes`/`starts`/`speeds` di `Contact_Scheduler.schedule_contacts`) vive qui.

## Rotta per asset: rotta di riferimento + offset di formazione (D3.b)

La missione ha UNA rotta di riferimento (`Mission.route`, o in mancanza la spezzata dei
`MissionWaypoint`, v. `reference_route`); ogni `MissionAsset` dichiara un offset
(`forward_m`, `right_m`, `up_m`) nella terna della direzione di marcia:
  * avanti = versore ORIZZONTALE della direzione di marcia (la quota non inclina la formazione);
  * destra = avanti ruotato di 90 gradi in senso orario visto dall'alto (convenzione del
    progetto: nord = +y, est = +x, azimut orario, v. `Weapon_Delivery._unit`): avanti (hx, hy)
    -> destra (hy, -hx);
  * alto = +z, sempre.

**Offset nullo = la STESSA rotta** (lo stesso oggetto `Route`): i tratti sono identici a quelli
che si avrebbero passando la rotta di riferimento, senza alcuna aritmetica in mezzo.

**Regola ai cambi di direzione (decisa in F3): la formazione ruota con la rotta, sulla
bisettrice.** L'offset si applica PUNTO PER PUNTO, non tratto per tratto (applicarlo per tratto
staccherebbe i tratti consecutivi):
  * primo punto: terna del primo tratto; ultimo punto: terna dell'ultimo tratto;
  * punto intermedio: terna della BISETTRICE b = normalizzato(h_entrata + h_uscita), cioe' la
    direzione media fra il tratto in arrivo e quello in partenza;
  * la componente laterale e' scalata di 1/cos(theta/2) (theta = angolo di virata; giunzione "a
    spigolo", la stessa delle spezzate parallele): cosi' i tratti dell'asset restano PARALLELI a
    quelli di riferimento, a distanza `right_m`, prima e dopo la virata. Il fattore e' limitato
    a `MITER_LIMIT` per le virate strette (oltre 120 gradi il punto non schizza lontano);
  * la componente avanti e' presa lungo la bisettrice, senza scala;
  * inversione esatta (h_uscita = -h_entrata, bisettrice indefinita): si usa la terna del
    tratto in ENTRATA; il tratto successivo porta l'asset nella terna d'uscita al punto dopo
    (in una virata di 180 gradi il gregario di destra finisce dall'altra parte del riferimento,
    come in una formazione vera);
  * tratti senza componente orizzontale (salita/discesa sulla verticale, punti ripetuti)
    ereditano la direzione dal tratto orizzontale piu' vicino (prima il precedente); una rotta
    senza alcun tratto orizzontale ammette solo `up_m` (altrimenti ValueError).

Conseguenza da sapere: una formazione che TRASLA rigidamente (stesso spostamento per ogni
punto) coincide con una rotta di riferimento + offset solo se la rotta non cambia direzione;
con virate la traslata e' un'altra geometria (v. la migrazione degli scenari, F3).

Le coordinate della rotta per asset sono arrotondate al micrometro (`OFFSET_DECIMALS`): il
rumore della rotazione (ordine 1e-12 m) non ha significato fisico e non deve comparire come
differenza di posizione (sympy `Point3D` conserva i float come razionali).

## Velocita'

`MissionWaypoint.speed_kmh` e' la velocita' del tratto IN ARRIVO al punto (None = quella
dell'arco della rotta, in m/s). Quella del primo punto non ha tratto in arrivo ed e' ignorata.
  * nessuna velocita' dichiarata: valgono quelle degli archi, nessuna voce in `speeds`;
  * tutti i tratti dichiarano la STESSA velocita': una voce in `speeds` [m/s] (sostituisce
    quella degli archi, semantica di `route_legs`), rotta invariata;
  * dichiarazioni diverse o parziali: la rotta per asset e' ricostruita con la velocita'
    dichiarata sui tratti che la dichiarano e quella dell'arco sugli altri.
Conversione km/h -> m/s: `kmh / 3.6`.

## Partenza (istante assoluto)

Gli istanti della missione sono in secondi dall'inizio della sessione; la partenza assoluta e'
`t0 + ...` con `t0 = SessionOrder.t_start`. In ordine di precedenza:
  1. `start_time` (dalla F5-C ritardata da un'ETA bloccata piu' tarda sul punto di partenza);
  2. il primo waypoint con `eta_locked`: partenza = ETA - tempo di percorrenza fino a quel punto
     sulla rotta di riferimento (con le velocita' di missione e, dalla F5-C, le attese di durata
     nota prima del punto);
  3. `tot`, ancorato al primo waypoint ATTACK (o, in mancanza, OBJECTIVE): stessa derivazione;
     senza un punto d'ancoraggio ValueError. Il TOT e' della missione, non dell'Operazione (v.
     sotto, "Attese, ETA bloccate e TOT").
Tutti gli asset di una missione partono insieme (la formazione e' una). Una partenza derivata
anteriore all'inizio della sessione e' un errore (le missioni fuori finestra saranno rifiutate dal
validatore di sessione della F8; qui non si tagliano in silenzio). `Activation.ON_EVENT` e' solo
dichiarabile: ValueError.

## Regola A: la missione si muove insieme, alla velocita' del mezzo piu' lento (F4a)

Decisione dell'utente (2026-10-05): una missione e' un gruppo (come un gruppo DCS) e si muove
INSIEME; chi vuole velocita' diverse fa missioni separate, eventualmente coordinate da
un'Operazione. `check_mission_speed` lo verifica dove gli asset sono noti (lo chiama
`Session_Simulator` nella validazione delle missioni; `Command/Mission_Types` e' solo struttura e
non conosce gli asset): la velocita' pianificata di ogni tratto (quella di missione, o in mancanza
quella dell'arco) non puo' superare la velocita' MASSIMA (`asset.speed['max']`, m/s, dal
registro, v. `Mobile.speed_profile_from_registry`) del mezzo piu' lento della missione.
  * un asset senza velocita' massima nota (modello senza `speed_data`, asset non `Mobile`) e'
    escluso dal confronto con un warning: non blocca la missione; se nessun asset ha il dato il
    controllo non si fa;
  * il limite e' il regime 'max' generico, NON quello per terreno (`speed['off_road']['max']`):
    gli scenari pianificano oggi i mezzi terrestri al regime nominale su archi 'offroad', e il
    vincolo per tipo d'arco va deciso con il modulo mappe (limite noto);
  * tolleranza `SPEED_TOLERANCE` (rumore di conversione delle unita', non un margine fisico).

## La missione come forza d'ingaggio: `MissionForce` (F4b, D3.e)

Dalla F4b l'unita' d'ingaggio del motore e' la MISSIONE, non il blocco: `Session_Simulator`
passa allo scheduler i blocchi (le finestre sono per coppia di asset, la potatura per blocco resta
quella di prima) ma raggruppa le finestre e chiama `Engagement_Resolver.resolve_engagement` sulle
viste `MissionForce`. Disingaggio, soglia di rottura (tempra) e `committed` valgono quindi per
missione (ripartizione del fuoco e percezione del nemico, dal 2026-10-11, per dominio di
coordinamento: v. sotto); il blocco resta l'unita' di appartenenza, rifornimento e comando (gli
asset sono gli stessi oggetti, `asset.block` non cambia).

Verifica fatta all'inizio della F4b: cosa legge il risolutore della forza, oltre agli asset.
  * `id`/`name` (id di forza: chiave di `committed`, dei `ForceOutcome`, della percezione);
  * `side` (dottrina di disingaggio e di tiro, amico/nemico nella percezione);
  * `salvo_interceptors()` (difesa di salva, R1): la vista lo RESTRINGE ai propri asset (il
    risolutore filtra comunque per forza, la restrizione rende la vista corretta anche da sola;
    dalla F4b++ il risolutore riunisce poi gli intercettori delle forze di uno stesso dominio di
    coordinamento, v. `coordination_domains`);
  * la CLASSE della forza (`_can_disengage`: `Military` si', `Block` non militare no): una vista
    non e' ne' l'una ne' l'altra, quindi dichiara `can_disengage` calcolato sul blocco con la
    stessa regola (ADATTATORE: il risolutore onora un `can_disengage` booleano dichiarato);
  * l'oggetto forza intero, passato tale e quale a `morale_for`/`enemy_estimate_for`: ricevono la
    vista, che espone il blocco in `owner_block` (nessun chiamante di produzione li fornisce).
  Rilevamento, nebbia di guerra (`recon_detection_factor_fn`), RWR, carburante, danno e munizioni
  leggono gli ASSET (e `asset.block`), non la forza: invariati.

Nessuna delega generica degli attributi al blocco (niente `__getattr__`): le grandezze aggregate
del blocco (potenza di combattimento, volumi, ...) riguardano TUTTI i suoi asset e, lette sulla
vista, sarebbero sbagliate in silenzio.

Il riferimento al blocco si chiama `owner_block`, NON `block`: `Contact_Scheduler._as_block` e
`Session_Simulator._as_block` scartano un `.block` (forma del `BlockItem`) e scambierebbero la
vista per il suo blocco.

**Asset del blocco senza missione**: fermi nella loro posizione per tutta la sessione. Un blocco
senza missioni entra nel risolutore come prima della F4b (l'oggetto blocco, id del blocco); un
blocco con missioni e anche asset non assegnati li raggruppa nella vista residua
`MissionForce.unassigned`, con l'id DEL BLOCCO e `mission_id` None. La loro postura e' quella
continua della F4c (sotto).

## Postura continua degli asset senza missione (F4c, D1.c)

Decisioni dell'utente (2026-10-11), `continuous_posture`:
  * **aereo senza missione = a terra** (`PARKED_POSTURE`): bersaglio di SUPERFICIE passivo.
    Colpibile da bombe, razzi, cannoni e missili aria-suolo come un'unita' di superficie, mai
    ingaggiato da SAM/AAA/caccia come minaccia aerea, non spara mai e non osserva (sensori
    spenti). Si riconosce dall'appartenere alla vista residua (o a un blocco senza missioni):
    nessuno stato nuovo nell'`Aircraft`, nessuna mutazione degli asset. L'insieme degli id a terra
    (`grounded_assets`) e' calcolato dalla sessione e passato a scheduler (portate) e risolutore
    (rilevamento, tiro, peso di minaccia, disingaggio);
  * **unita' terrestri e navali senza missione**: postura `Defense` DICHIARATA
    (`Context.Ground_Action.DEFENSE` / `Sea_Task.DEFENSE`, stessa stringa), tiro INVARIATO:
    sparano a cio' che rilevano a portata, come prima. Nessun ROE "hold fire". La postura e'
    solo un dato della vista (`MissionForce.postures`): non cambia estrazioni ne' esiti.
La postura vale per asset, non per forza: una vista residua mista (aerei parcheggiati e difese
della base) ha aerei a terra e unita' in difesa.

Dalla F5 (passo (a) la forma, passo (b) il cablaggio) anche un aereo con missione non ancora
decollato e' a terra: il criterio e' un PROGRAMMA nel tempo (`grounded_schedule`, sotto), non una
proprieta' della forza; la vista e il protocollo di fire control non cambiano.

## Presenza prima della partenza e dopo la fine (F5 passo (b), D1.a/b, decisioni dell'utente)

Con `F5_PRESENCE` (attivo dalla F5-B) `mission_movements` dichiara per ogni asset di missione
(`_presence`) se e' presente FERMO nella posizione di partenza prima di partire e in quella finale
dopo la fine, e se in quei tratti e' un aereo a terra:
  * terra e mare: presenti prima e dopo, in postura `Defense` (`final_posture`), quindi rilevabili
    e ingaggiabili come un'unita' ferma; il tiro e' quello di sempre;
  * aereo che NON parte in volo (`start_mode` parcheggio o pista): presente e A TERRA dalla
    sessione al decollo (bersaglio di superficie passivo, come gli aerei senza missione);
  * aereo dopo la fine della rotta: a terra SOLO se l'ultimo punto e' LAND su una base vera
    (`lands_on_air_base`: riferimento del waypoint a un asset di una base, oppure punto nell'area
    di una base del suo lato, `air_base_points` entro `AIR_BASE_AREA_RADIUS_M`, stima); altrimenti
    esce di scena all'arrivo, come prima (postura
    `OFF_SCENE_POSTURE`), finche' la F6 non portera' il rientro nella rotta.
`movement_legs` costruisce i tratti (movimento + presenza) che `Session_Simulator` passa a scheduler
e risolutore, `grounded_schedule` gli intervalli a terra, `session_postures` la postura di ogni
asset a fine sessione nel `SessionOutcome`. Senza `F5_PRESENCE` i tratti sono quelli della sola
rotta e il programma contiene solo gli aerei senza missione: la sessione e' quella della F5-A.

## Dominio di coordinamento (2026-10-11, decisioni dell'utente 6 e 7)

`coordination_domains` assegna a ogni forza d'ingaggio la chiave del suo DOMINIO di
coordinamento, che `Engagement_Resolver.resolve_engagement` riceve come `coordination_of`: dentro
un dominio ripartizione del fuoco, saturazione e percezione del nemico sono condivise (v. il
docstring del risolutore). Regola dell'utente: due forze dello stesso lato sono nello stesso
dominio se hanno lo stesso blocco OPPURE appartengono alla stessa Operazione, con unione
TRANSITIVA (union-find: A e B dello stesso blocco, B e C della stessa Operazione -> A, B, C in un
solo dominio). La vista residua e un blocco senza missioni hanno l'id del blocco, quindi entrano
nel dominio delle missioni del blocco.
  * **Lati**: un dominio non sta mai a cavallo di due lati. Un'Operazione che elenca missioni di
    lati diversi (`SessionOrder` non conosce i blocchi e non puo' vietarlo) lega solo le missioni
    dello stesso lato: un dominio per lato, con un warning. Scelta la via che non rifiuta l'ordine
    perche' l'Operazione e' un raggruppamento di scopo, non di comando; il risolutore verifica
    comunque l'invariante (ValueError se due lati condividono una chiave).
  * **Chiave**: l'id di forza minore (ordine delle stringhe) fra i membri del dominio. E' l'id di
    una delle sue forze, quindi non puo' coincidere con la chiave di un altro dominio, e senza
    legami la chiave di una forza e' il suo id (comportamento precedente).
  * L'appartenenza all'Operazione e' letta da `Operation.mission_ids` e da `Mission.operation_id`
    della missione della vista (`SessionOrder` ne garantisce la coerenza): le missioni arrivano
    con le viste, non serve passarle a parte.

## Attese, ETA bloccate e TOT (F5 passi (c)-(d), N2.b/N2.c, cablati dalla F5-C)

Con `F5_WAITS` (attivo dalla F5-C) `mission_movements` dichiara le ATTESE della missione
(`mission_holds`, `AssetMovement.holds`): tratti FERMI nel punto della rotta, inseriti nel
movimento da `_timeline` (i tratti successivi sono spostati della durata). Le stesse attese per
tutti gli asset della missione (la formazione attende insieme, regola A). Fonti di un'attesa:
  * azione WAIT del punto (`_wait_end`): durata data o fino all'istante t, con la sua condizione
    d'avvio; 'hold' (sosta) e 'orbit' (circuito) sono la STESSA cosa per il motore: presenza
    ferma nel punto per la durata. Per l'orbita e' un'APPROSSIMAZIONE DICHIARATA: nessun circuito
    geometrico (MissionAction non dichiara raggio ne' velocita' d'orbita, e non se ne inventano);
    le finestre di contatto coprono quindi tutta l'attesa intorno al punto. Errore di posizione
    pari al raggio del circuito reale (qualche km per un caccia);
  * ETA bloccata di un punto (`eta_locked`) e TOT della missione (`Mission.tot`): se il punto
    sarebbe raggiunto in anticipo l'asset attende nel punto PRECEDENTE quanto basta per arrivarci all'istante; in
    ritardo un warning e l'ETA effettiva lo riporta (la velocita' non cambia);
  * partenza (`mission_start`): senza `start_time` e' derivata all'indietro dall'ETA bloccata o
    dal TOT, comprese le attese di durata nota prima del punto (ANTICIPO); un'ETA bloccata sul
    punto di partenza piu' tarda di `start_time` la RITARDA.
Il TOT e' SPECIFICO DI OGNI MISSIONE, anche fra le missioni della stessa Operazione (decisione
dell'utente del 2026-10-12, che ha rimosso il TOT comune `Operation.tot`, usato dalla F5-C come
TOT delle missioni dell'Operazione che non ne dichiaravano uno):
es. una Fighter Sweep su una zona che anticipa di qualche minuto l'arrivo dei bombardieri di
un'altra missione sulla stessa zona ha un TOT diverso da quello dei bombardieri. Missioni
coordinate dichiarano quindi ciascuna il proprio TOT (uguali o sfalsati); senza `start_time` la
partenza e' anticipata in proporzione alla distanza, con `start_time` la missione attende prima
del punto d'ancoraggio.
Gli istanti EFFETTIVI di arrivo ai punti (`waypoint_times`, dalle attese comprese) vanno nel
`MissionOutcome.actual_etas` (`Session_Simulator`); le ETA pianificate restano nella missione.
**Carburante**: dalla F6-A le attese consumano NEL TEMPO alla crociera dell'asset, con un `FuelEvent`
per tratto, e l'esaurimento tronca i tratti (`Session_Simulator`, "Carburante"; `Fuel_Model`); qui i
tratti non cambiano.

## Bingo a priori (F6-B2 del piano della Missione, decisione 14; rientro rifatto dalla F6-B2bis e dal G2, sotto)

`check_mission_bingo` e' il VALIDATORE di pianificazione del carburante: una missione aerea che non
rientra con la riserva (`Fuel_Model.BINGO_RESERVE`, stima) e' RIFIUTATA con un `ValueError` che dice
quanto carburante manca. Fabbisogno = la missione intera pianificata alla crociera (`airborne_legs`:
andata, attese, ritorno; le soste a terra non consumano) + rientro in linea retta dall'ultimo punto alla
base idonea piu' vicina (con una rotta che atterra su una base il rientro e' quasi nullo). Base idonea =
qualunque base aerea del lato (`air_base_points`, lo stesso criterio della planata della F6-A); nessuna
base = rifiuto. Non si applica alle missioni di terra e mare ne' a quelle con `EndCriteria.bingo` False
(dichiarano di non rientrare al bingo).
Il controllo NON e' chiamato da `Session_Simulator.run_session`: e' del pianificatore (il futuro C2),
che decide con lo stato della campagna; l'esecutore (sintetico o DCS, "RTB on bingo") non rifiuta un
ordine ma fa tornare l'aereo al bingo in volo (`Session_Simulator`, "Bingo"). I due usano lo stesso
criterio (`Fuel_Model.bingo_point`): con lo stesso carburante e le stesse basi la missione rifiutata qui
e' esattamente quella che in sessione arriva al bingo.

**F6-B2bis (decisioni dell'utente del 2026-10-15).** Con `reverse_route` True (default, come
`Session_Simulator.F6_BINGO_REVERSE_ROUTE` acceso) il rientro non e' piu' la retta dall'ultimo punto: e'
la rotta percorsa A RITROSO (tratti di movimento senza le soste) fino al DEPARTURE, o, partendo in volo,
fino al punto di comparsa e poi diretto alla base del lato piu' vicina; il fabbisogno e'
`Fuel_Model.BINGO_RETURN_FACTOR` (1,2, stima) x il carburante del ritorno, al posto della riserva fissa.
La regola della missione e' `bingo_return_rule`; la missione ad ANELLO (`is_loop_mission`: LAND sulla
stessa base del DEPARTURE, per blocco del riferimento o, in mancanza, entro `AIR_BASE_AREA_RADIUS_M`)
rientra per la via piu' breve fra ritroso e resto della rotta, quindi e' sicura con circa 1,1 volte il
carburante della rotta. Il LAND su un'altra base (divert) non conta. Base idonea richiesta solo con la
partenza in volo: chi parte da una base rientra sul suo DEPARTURE. Con False la regola della F6-B2 qui
sopra, invariata.

**G1, minimo di pianificazione (decisioni dell'utente del 2026-10-15).** `check_mission_fuel` e' un secondo
validatore, distinto da `check_mission_bingo`: ogni aereo deve caricare PIU' del carburante della rotta
INTERA (`airborne_legs` alla crociera, attese comprese, `route_fuel_demand`) + la riserva di disimpegno
(`Fuel_Model.disengagement_reserve`: 5 minuti alla massima spinta militare, stima; ripiego sul regime 'max'
del loadout); altrimenti `ValueError` con asset, carburante, fabbisogno, riserva e mancanza. Funzione
separata e non parametro di `check_mission_bingo` perche' e' un'altra regola: il bingo verifica il criterio
del rientro in volo dell'esecutore (lo stesso di `Fuel_Model.bingo_point`), il minimo verifica il carico; i
passi G2-G4 rifaranno il bingo sopra la stessa riserva. Stessa applicabilita' (solo aerea, `EndCriteria.bingo`
False = nessun controllo); un asset senza carburante o riserva modellati non e' controllato. Come l'altro,
NON e' chiamato da `run_session` (nessun interruttore: il comportamento in sessione non cambia).

**G2, soglia di bingo e albero di decisione (decisioni dell'utente del 2026-10-15).** Con `disengage_reserve`
True (default, come `Session_Simulator.F6_BINGO_DISENGAGE_RESERVE` acceso) `check_mission_bingo` applica la
soglia del G2 all'inizio dei tratti (`mission_bingo_decision` -> `Fuel_Model.bingo_decision`): rifiuta la
missione se un aereo parte con carburante < rotta intera + riserva di disimpegno, cioe' esattamente quella che
in sessione va in bingo (anche un trasferimento che poi CONTINUA consumando la riserva: e' sotto il minimo);
`reserve` e `reverse_route` sono ignorati, le basi non sono richieste. Rapporto con `check_mission_fuel` (G1):
stessa grandezza, rotta intera + riserva; il G1 rifiuta con carburante <= minimo (decisione "caricato >
minimo"), il G2 con carburante < soglia (decisione "bingo se residuo < soglia"): differiscono solo
all'uguaglianza esatta (e al rumore `Fuel_Model._FUEL_EPS`). Il G1 resta il controllo del CARICO, il G2 quello
che annuncia cosa fara' l'esecutore (istante e decisione dell'albero). Il tipo di missione per l'albero e'
`is_transfer_mission` (categoria TRANSPORT della mappa di Context; ogni altro tipo = combattimento).

**F7a, regole d'ingaggio di missione (decisioni dell'utente del 2026-10-18).** `designated_targets`,
`weapon_policies` e `target_rules` traducono bersaglio, ROE e armi designate della missione nelle forme che il
motore consuma (`Fire_Control.WeaponPolicy` per lo strato W, `Engagement_Resolver.TargetRules` per lo strato T):
il risolutore e la fire control non leggono mai la `Mission`. Bersaglio designato = i NEMICI della missione
(ASSET: l'asset; GROUP: gli asset del blocco, della missione o l'asset stesso, ristretti da `Target.asset_ids`;
POINT/AREA/ZONE: area orizzontale con raggio efficace = raggio dichiarato, `TARGET_POINT_RADIUS_M` per un POINT
senza raggio, piu' l'incertezza di una stima); un gruppo amico (scorta, trasporto) non designa nessuno.
`attack_point` da' alle regole `priority_designated` il punto ATTACK della missione sulla rotta dell'asset (con
l'offset di formazione): il risolutore ne ricava il passaggio dai tratti reali (fine dell'attacco).

## Cosa NON fa
- Nessun circuito d'orbita (v. sopra); il carburante non e' calcolato qui (`Fuel_Model`, F6-A).
- Non usa ruoli ne' criteri di fine; regole e bersaglio solo per le regole d'ingaggio della F7a (v. sopra).
- Nessun rientro (RTB) nella rotta: un aereo che non atterra su una base vera esce di scena; il rientro
  al bingo lo costruisce la sessione (F6-B2, `Session_Simulator`, "Bingo"; dal G2 dalla decisione di
  `mission_bingo_decision`).
- Nessun RNG, nessuna mutazione: funzioni pure (la vista non copia ne' muta gli asset).
"""

import math
from dataclasses import dataclass
from typing import Dict, FrozenSet, Iterable, List, Mapping, Optional, Sequence, Tuple

from sympy import Point3D

from Code.Dynamic_War_Manager.Source.Command.Mission_Types import (
    ActionKind,
    Activation,
    Mission,
    MissionAction,
    MissionAsset,
    Operation,
    StartConditionKind,
    StartMode,
    TargetKind,
    TargetProvenance,
    WaypointRole,
    route_waypoints,
)
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Loadouts import AIRCRAFT_LOADOUTS
from Code.Dynamic_War_Manager.Source.Context.Context import (
    Ground_Action,
    Mission_Category,
    Sea_Task,
    TARGET_CLASS_AIR,
    WEAPON_RULE_SELF_DEFENCE,
    mission_weapon_policy,
    postures_for,
)
from Code.Dynamic_War_Manager.Source.DataType.Edge import Edge
from Code.Dynamic_War_Manager.Source.DataType.Route import Route
from Code.Dynamic_War_Manager.Source.DataType.Waypoint import Waypoint
from Code.Dynamic_War_Manager.Source.Logic import Contact_Scheduler as CS
from Code.Dynamic_War_Manager.Source.Logic import Engagement_Resolver as ER
from Code.Dynamic_War_Manager.Source.Logic import Fire_Control as FC
from Code.Dynamic_War_Manager.Source.Logic import Fuel_Model as FM
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.Utility.Utility import validate_class

# LOGGING --
logger = Logger(module_name=__name__, class_name='Mission_Adapter').logger


# ── COSTANTI ──────────────────────────────────────────────────────────────────

# Limite del fattore 1/cos(theta/2) della componente laterale alle virate (v. docstring). STIMA DI
# PROGETTO, non un dato: 2.0 = esatto fino a virate di 120 gradi, tagliato oltre.
MITER_LIMIT = 2.0

# Decimali [m] delle coordinate di una rotta con offset: micrometro (v. docstring).
OFFSET_DECIMALS = 6

# Sotto questa norma [m] un tratto non ha direzione orizzontale; sotto questa norma (adimensionale)
# la somma di due versori e' un'inversione.
_HORIZONTAL_EPS = 1e-9
_REVERSAL_EPS = 1e-9

# Tipo d'arco e tipo di rotta per una rotta costruita dai soli MissionWaypoint.
_PATH_TYPE_BY_DOMAIN = {'air': 'air', 'ground': 'offroad', 'sea': 'water'}
_ROUTE_TYPE_BY_DOMAIN = {'air': 'air', 'ground': 'ground', 'sea': 'water'}

# Tolleranza [m/s] del controllo di velocita' della regola A: solo rumore di conversione delle
# unita' (km/h, nodi, mph -> m/s), non un margine fisico.
SPEED_TOLERANCE = 1e-6

# Ruoli d'ancoraggio del TOT, in ordine di preferenza.
_TOT_ANCHOR_ROLES = (WaypointRole.ATTACK, WaypointRole.OBJECTIVE)

# Postura continua (F4c, v. docstring). Etichette, non grandezze: l'aereo a terra e' l'aereo sul
# parcheggio a motori spenti (lo stato `uncontrolled` di DCS, stessa etichetta di
# `StartMode.PARKING_COLD`); le unita' di superficie sono in difesa.
PARKED_POSTURE = StartMode.PARKING_COLD.value
GROUND_DEFENSE_POSTURE = Ground_Action.DEFENSE.value
SEA_DEFENSE_POSTURE = Sea_Task.DEFENSE.value
# Postura finale (F5, nell'esito di sessione) di un aereo uscito di scena alla fine di una rotta che
# non termina su una base vera: ETICHETTA PROVVISORIA, finche' la F6 non portera' il rientro (RTB)
# nella rotta. Non e' un valore di Context ne' una grandezza.
OFF_SCENE_POSTURE = 'off_scene'
# Postura finale (F6-B1, nell'esito di sessione) di un asset DISTRUTTO a fine sessione, in combattimento o
# per carburante: ETICHETTA, non un valore di Context ne' una grandezza. La assegna
# `Session_Simulator.run_session` (interruttore `F6_DESTROYED_POSTURE`): `session_postures` resta la
# postura di piano (non legge lo stato dell'asset).
DESTROYED_POSTURE = 'destroyed'
# Raggio [m] dell'AREA di una base aerea per il criterio d'atterraggio (F5-B, `lands_on_air_base`):
# un punto LAND entro questa distanza orizzontale da un asset non aereo di una base vera e' un
# atterraggio sulla base. STIMA DI PROGETTO, non un dato: ordine di grandezza di una pista (2-3,5 km
# negli aeroporti delle carte DCS, es. 2900 m) con le installazioni a lato. Da sostituire con il
# perimetro reale della base quando arrivera' il modulo mappe.
AIR_BASE_AREA_RADIUS_M = 3_000.0

# Raggio efficace [m] di un bersaglio POINT dichiarato senza raggio (F7a, designazione geometrica, decisione 11
# del 2026-10-18). STIMA DI PROGETTO, non un dato: ordine di grandezza dell'errore di un punto d'impatto/di
# posizione per un obiettivo puntiforme (un compound, una batteria); da ricalibrare con i dati di precisione.
TARGET_POINT_RADIUS_M = 500.0

# F5, due interruttori separati (F5-B, 2026-10-12), cosi' che la fotografia di ogni passo attribuisca
# le differenze a una sola causa:
#   * `F5_PRESENCE` (passo (b), ATTIVO): presenza ferma prima della partenza e dopo la fine (D1.a/b,
#     `_presence`): terra/mare presenti in `Defense`, aerei a terra prima del decollo se non partono
#     in volo e dopo l'atterraggio SOLO su una base vera. Con False `mission_movements` non dichiara
#     presenza (l'asset esiste solo sulla rotta, come prima della F5) e la sessione cablata da F5-B
#     e' identica alla F5-A (verificato con la fotografia). La postura nell'esito
#     (`session_postures`) e' riportata in ogni caso: e' un'uscita, non cambia la storia.
#   * `F5_WAITS` (passi (c)-(d), ATTIVO dalla F5-C): attese WAIT, ETA bloccate e TOT della missione
#     (`mission_holds`, anticipo della partenza in `mission_start`). Con False nessuna attesa:
#     partenza e ETA come prima della F5 (il TOT della missione deriva comunque la partenza, come
#     dalla F3).
F5_PRESENCE = True
F5_WAITS = True


def kmh_to_ms(speed_kmh: float) -> float:
    """km/h -> m/s."""
    return float(speed_kmh) / 3.6


# ── TIPI ──────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AssetMovement:
    """Movimento di un asset di missione nella sessione, nella forma del motore.

    Attributes:
        mission_id/asset_id: id di dominio.
        route: `DataType.Route` dell'asset (None = missione senza rotta: l'asset resta fermo).
        start: istante assoluto di partenza [s] (t0 + istante di missione).
        speed: velocita' [m/s] che sostituisce quella degli archi, None = quella degli archi.
        holds: attese (F5, N2.c) come `((indice del waypoint, durata [s]), ...)` in ordine di
            indice: l'asset resta fermo nel punto `indice` della sua rotta per la durata, dopo
            l'arrivo (azioni WAIT e sincronizzazione delle ETA bloccate, v. `mission_holds`).
            Vuota = nessuna attesa (comportamento precedente).
        present_before/present_after: presente FERMO nella posizione di partenza prima di partire
            e nella posizione finale dopo la fine (F5, D1.a/b). Default False = assente (prima
            della F5).
        grounded_before/grounded_after: in quei tratti l'asset e' un aereo A TERRA (parcheggio
            prima del decollo, base vera dopo l'atterraggio).
    """
    mission_id: str
    asset_id: str
    route: Optional[Route]
    start: float
    speed: Optional[float] = None
    holds: Tuple[Tuple[int, float], ...] = ()
    present_before: bool = False
    present_after: bool = False
    grounded_before: bool = False
    grounded_after: bool = False


# ── ROTTA DI RIFERIMENTO E VELOCITA' ──────────────────────────────────────────

def _route_from_waypoints(mission: Mission) -> Route:
    """Rotta costruita dai `MissionWaypoint` quando la missione non porta una `Route`.

    Ogni tratto prende la velocita' dichiarata dal punto d'arrivo: senza, la rotta non e'
    percorribile (nessun arco da cui leggerla) e si solleva ValueError.
    """
    path_type = _PATH_TYPE_BY_DOMAIN[mission.domain]
    edges = {}

    for index in range(len(mission.waypoints) - 1):
        a, b = mission.waypoints[index], mission.waypoints[index + 1]

        if b.speed_kmh is None:
            raise ValueError(f"mission {mission.mission_id!r} has no route and waypoint {index + 1} "
                             f"declares no speed_kmh: the leg cannot be travelled")

        edges[(a.waypoint.name, b.waypoint.name)] = Edge(wpA=a.waypoint, wpB=b.waypoint, path_type=path_type,
                                                         danger_level=None, speed=kmh_to_ms(b.speed_kmh),
                                                         name=f'{mission.mission_id}-E{index}')

    return Route(route_type=_ROUTE_TYPE_BY_DOMAIN[mission.domain], edges=edges, name=f'{mission.mission_id}-route')


def reference_route(mission: Mission) -> Optional[Route]:
    """La rotta di riferimento della missione, None se la missione non si muove.

    `Mission.route` se presente; altrimenti, con almeno due `MissionWaypoint`, la spezzata dei
    loro `Waypoint` (v. `_route_from_waypoints`); altrimenti None (missione sul posto).
    """
    if not isinstance(mission, Mission):
        raise TypeError(f"mission must be a Mission, got {type(mission).__name__}")

    if mission.route is not None:
        return mission.route if mission.route.edges else None

    if len(mission.waypoints) >= 2:
        return _route_from_waypoints(mission)

    return None


def _leg_speeds(mission: Mission, route: Route) -> Tuple[Optional[float], Optional[List[Optional[float]]]]:
    """(velocita' uniforme [m/s] | None, velocita' per tratto [m/s | None] | None), v. docstring.

    Solo per una missione con `Mission.route`: una rotta costruita dai waypoint ha gia' le
    velocita' dichiarate sugli archi.
    """
    if mission.route is None or not mission.waypoints:
        return None, None

    declared = [mw.speed_kmh for mw in mission.waypoints[1:]]

    if all(speed is None for speed in declared):
        return None, None

    if len(declared) == len(route.edges) and len(set(declared)) == 1:
        return kmh_to_ms(declared[0]), None

    return None, [kmh_to_ms(speed) if speed is not None else None for speed in declared]


# ── GEOMETRIA DELL'OFFSET ─────────────────────────────────────────────────────

def _xyz(point) -> Tuple[float, float, float]:
    return float(point.x), float(point.y), float(point.z)


def _horizontal_heading(a, b) -> Optional[Tuple[float, float]]:
    dx, dy = b[0] - a[0], b[1] - a[1]
    norm = math.hypot(dx, dy)
    return (dx / norm, dy / norm) if norm > _HORIZONTAL_EPS else None


def _leg_headings(points: Sequence[Tuple[float, float, float]]) -> List[Tuple[float, float]]:
    """Direzione orizzontale di ogni tratto; i tratti senza componente orizzontale la ereditano."""
    raw = [_horizontal_heading(points[i], points[i + 1]) for i in range(len(points) - 1)]

    if all(h is None for h in raw):
        raise ValueError("the route has no horizontal leg: forward/right offsets are undefined")

    headings: List[Optional[Tuple[float, float]]] = list(raw)

    for index, heading in enumerate(raw):
        if heading is not None:
            continue

        previous = next((raw[j] for j in range(index - 1, -1, -1) if raw[j] is not None), None)
        following = next((raw[j] for j in range(index + 1, len(raw)) if raw[j] is not None), None)
        headings[index] = previous if previous is not None else following

    return headings  # type: ignore[return-value]


def _point_frame(h_in: Optional[Tuple[float, float]], h_out: Optional[Tuple[float, float]]
                 ) -> Tuple[Tuple[float, float], float]:
    """(direzione avanti al punto, fattore della componente laterale), v. docstring."""
    if h_in is None:
        return h_out, 1.0

    if h_out is None:
        return h_in, 1.0

    sx, sy = h_in[0] + h_out[0], h_in[1] + h_out[1]
    norm = math.hypot(sx, sy)

    if norm < _REVERSAL_EPS:
        return h_in, 1.0   # inversione esatta: terna del tratto in entrata

    bisector = (sx / norm, sy / norm)
    cos_half = bisector[0] * h_in[0] + bisector[1] * h_in[1]
    return bisector, min(1.0 / cos_half, MITER_LIMIT)


def offset_points(points: Sequence[Tuple[float, float, float]], forward_m: float, right_m: float,
                  up_m: float) -> List[Tuple[float, float, float]]:
    """Punti della spezzata spostati dell'offset di formazione (regola nel docstring del modulo).

    Args:
        points: punti della rotta di riferimento (x, y, z) [m], almeno due.
        forward_m/right_m/up_m: offset nella terna della direzione di marcia [m].

    Returns:
        Lista di punti (x, y, z) arrotondati a `OFFSET_DECIMALS`.

    Raises:
        ValueError: meno di due punti; offset orizzontale su una rotta senza tratti orizzontali.
    """
    if len(points) < 2:
        raise ValueError(f"an offset needs at least two route points, got {len(points)}")

    if forward_m == 0.0 and right_m == 0.0:
        headings = [None] * (len(points) - 1)
    else:
        headings = _leg_headings(points)

    shifted = []

    for index, (x, y, z) in enumerate(points):
        if headings[0] is None:   # solo offset verticale
            dx = dy = 0.0
        else:
            h_in = headings[index - 1] if index > 0 else None
            h_out = headings[index] if index < len(headings) else None
            (fx, fy), lateral = _point_frame(h_in, h_out)
            rx, ry = fy, -fx   # destra = avanti ruotato di 90 gradi in senso orario
            dx = forward_m * fx + right_m * lateral * rx
            dy = forward_m * fy + right_m * lateral * ry

        shifted.append((round(x + dx, OFFSET_DECIMALS), round(y + dy, OFFSET_DECIMALS),
                        round(z + up_m, OFFSET_DECIMALS)))

    return shifted


def _rebuild_route(route: Route, points: Sequence[Tuple[float, float, float]],
                   speeds: Optional[Sequence[Optional[float]]], suffix: str) -> Route:
    """Copia di `route` con i punti dati e (se date) le velocita' per tratto; archi in ordine."""
    edges_in = list(route.edges.values())
    originals = route_waypoints(route)

    if len(originals) != len(edges_in) + 1 or len(points) != len(originals):
        raise ValueError(f"route {route.name!r} is not a chain of edges: cannot derive an asset route")

    waypoints = [Waypoint(point=Point3D(*point), name=f'{original.name}@{suffix}', obj_reference=original.reference)
                 for point, original in zip(points, originals)]
    edges = {}

    for index, edge in enumerate(edges_in):
        a, b = waypoints[index], waypoints[index + 1]
        speed = speeds[index] if speeds is not None and speeds[index] is not None else edge.speed
        edges[(a.name, b.name)] = Edge(wpA=a, wpB=b, path_type=edge.path_type, danger_level=edge.danger_level,
                                       speed=speed, name=f'{edge.name}@{suffix}')

    return Route(route_type=route.route_type, edges=edges, name=f'{route.name}@{suffix}')


# ── API ───────────────────────────────────────────────────────────────────────

def asset_route(mission: Mission, mission_asset: MissionAsset) -> Tuple[Optional[Route], Optional[float]]:
    """Rotta dell'asset di missione e velocita' uniforme [m/s] (None = quella degli archi).

    Offset nullo e nessuna velocita' per tratto: la rotta di riferimento STESSA (stesso oggetto).

    Raises:
        ValueError: asset non della missione, geometria non derivabile (v. `offset_points`).
    """
    if not isinstance(mission_asset, MissionAsset) or mission_asset not in mission.assets:
        raise ValueError(f"asset {getattr(mission_asset, 'asset_id', mission_asset)!r} is not in mission "
                         f"{mission.mission_id!r}")

    route = reference_route(mission)

    if route is None:
        return None, None

    uniform, per_leg = _leg_speeds(mission, route)
    zero_offset = (mission_asset.forward_m, mission_asset.right_m, mission_asset.up_m) == (0.0, 0.0, 0.0)

    if zero_offset and per_leg is None:
        return route, uniform

    points = [_xyz(waypoint.point) for waypoint in route_waypoints(route)]

    if not zero_offset:
        points = offset_points(points, mission_asset.forward_m, mission_asset.right_m, mission_asset.up_m)

    return _rebuild_route(route, points, per_leg, f'{mission.mission_id}:{mission_asset.asset_id}'), uniform


def _travel_time_to(route: Route, speed: Optional[float], index: int) -> float:
    """Tempo [s] dalla partenza al waypoint `index` (0 = partenza) della rotta."""
    if index == 0:
        return 0.0

    legs = CS.route_legs(route, t0=0.0, speed=speed)

    if len(legs) < index:
        raise ValueError(f"route {route.name!r} is not schedulable up to waypoint {index}")

    return legs[index - 1].t_end


def mission_start(mission: Mission, t0: float = 0.0) -> float:
    """Istante assoluto [s] di partenza della missione (precedenze nel docstring del modulo).

    Raises:
        ValueError: attivazione ON_EVENT, TOT senza punto d'ancoraggio, partenza derivata
            anteriore a `t0`.
    """
    if mission.activation is Activation.ON_EVENT:
        raise ValueError(f"mission {mission.mission_id!r}: ON_EVENT activation is declarable only, "
                         f"no executor runs it yet")

    if mission.start_time is not None:
        start = float(t0) + mission.start_time

        # F5: un'ETA bloccata sul punto di partenza piu' tarda di `start_time` ritarda la partenza
        # (l'asset resta presente fermo nel punto, D1.b), invece di un'attesa "in movimento".
        if F5_WAITS and mission.waypoints and mission.waypoints[0].eta_locked:
            start = max(start, float(t0) + mission.waypoints[0].planned_eta)

        return start

    route = reference_route(mission)
    locked = next((index for index, mw in enumerate(mission.waypoints) if mw.eta_locked), None)

    if locked is not None:
        anchor, instant, label = locked, mission.waypoints[locked].planned_eta, 'locked ETA'
    else:
        anchor = next((index for role in _TOT_ANCHOR_ROLES
                       for index, mw in enumerate(mission.waypoints) if mw.role is role), None)

        if anchor is None:
            raise ValueError(f"mission {mission.mission_id!r}: tot needs an ATTACK or OBJECTIVE waypoint "
                             f"to anchor the departure")

        instant, label = mission.tot, 'tot'

    travel = 0.0

    if route is not None and anchor > 0:
        uniform, per_leg = _leg_speeds(mission, route)
        timed = route if per_leg is None else _rebuild_route(
            route, [_xyz(w.point) for w in route_waypoints(route)], per_leg, f'{mission.mission_id}:timing')
        travel = _travel_time_to(timed, uniform, anchor)

    # F5: le attese DI DURATA sui punti prima dell'ancoraggio anticipano la partenza; quelle fino a
    # un istante assoluto no (dipendono dalla partenza stessa): se ritardano l'arrivo, l'ETA
    # effettiva lo riporta (v. `mission_holds`).
    if F5_WAITS:
        travel += sum(_relative_wait(mw.actions) for mw in mission.waypoints[:anchor])
    start = float(t0) + instant - travel

    if start < float(t0) - CS.TIME_EPS:
        raise ValueError(f"mission {mission.mission_id!r}: departure derived from the {label} ({instant} s) "
                         f"falls {float(t0) - start:.1f} s before the session start")

    return start


# ── ATTESE E ETA BLOCCATE (F5, N2.b/N2.c) ─────────────────────────────────────

def _wait_actions(actions) -> List[MissionAction]:
    return [action for action in actions if action.kind is ActionKind.WAIT]


def _relative_wait(actions) -> float:
    """Somma delle attese di DURATA (avvio all'arrivo o dopo una durata) di un punto [s]; le attese
    fino a un istante assoluto (`wait_until`, avvio AT_TIME) non hanno una durata nota a priori."""
    total = 0.0

    for action in _wait_actions(actions):
        if action.wait_duration_s is None or action.start.kind is StartConditionKind.AT_TIME:
            continue

        total += action.wait_duration_s

        if action.start.kind is StartConditionKind.AFTER_DURATION:
            total += action.start.duration_s

    return total


def _wait_end(actions, arrival: float, t0: float) -> float:
    """Istante [s] in cui l'asset lascia il punto dopo le azioni WAIT, in ordine di dichiarazione.

    Ogni attesa comincia secondo la sua condizione d'avvio (N2.d) e l'asset resta fermo nel punto
    dall'arrivo alla fine dell'ultima: ON_ARRIVAL alla fine della precedente (la prima all'arrivo),
    AT_TIME non prima di `t0 + time`, AFTER_DURATION dopo `duration_s`. Fine = inizio + durata,
    oppure `t0 + wait_until` (se gia' passato, nessuna attesa).
    """
    t = arrival

    for action in _wait_actions(actions):
        begin = t

        if action.start.kind is StartConditionKind.AT_TIME:
            begin = max(t, float(t0) + action.start.time)
        elif action.start.kind is StartConditionKind.AFTER_DURATION:
            begin = t + action.start.duration_s

        if action.wait_duration_s is not None:
            t = begin + action.wait_duration_s
        else:
            t = max(begin, float(t0) + action.wait_until)

    return t


def _locked_targets(mission: Mission, t0: float) -> Dict[int, float]:
    """`{indice: istante assoluto}` dei punti con ETA bloccata e del punto d'ancoraggio del TOT della
    missione; un'ETA bloccata sull'ancoraggio prevale."""
    targets = {index: float(t0) + mw.planned_eta for index, mw in enumerate(mission.waypoints) if mw.eta_locked}
    tot = mission.tot

    if tot is not None:
        anchor = next((index for role in _TOT_ANCHOR_ROLES
                       for index, mw in enumerate(mission.waypoints) if mw.role is role), None)

        if anchor is not None:
            targets.setdefault(anchor, float(t0) + tot)
        else:
            logger.warning(f"_locked_targets: mission {mission.mission_id!r} has a tot but no ATTACK or "
                           f"OBJECTIVE waypoint to anchor it: tot ignored")

    return targets


def mission_holds(mission: Mission, start: float, t0: float = 0.0) -> Tuple[Tuple[int, float], ...]:
    """Attese della missione per punto: `((indice, durata [s]), ...)`, v. docstring del modulo.

    Calcolate UNA volta sulla rotta di riferimento con le velocita' di missione (la stessa
    temporizzazione di `mission_start`) e applicate a tutti gli asset: la formazione attende
    insieme (regola A). Per ogni punto, nell'ordine:
      * azioni WAIT del punto (`_wait_end`);
      * sincronizzazione: se il punto SUCCESSIVO ha un'ETA bloccata (o e' l'ancoraggio del TOT) e
        sarebbe raggiunto in anticipo, l'attesa si allunga fino a raggiungerlo esattamente
        all'istante bloccato (attesa PRIMA del punto); in ritardo: un warning, l'ETA effettiva
        dell'esito lo riporta (la velocita' non cambia).

    Returns:
        Tupla vuota se la missione non ha rotta o non ha attese.
    """
    route = reference_route(mission)

    if route is None or not mission.waypoints:
        return ()

    uniform, per_leg = _leg_speeds(mission, route)
    timed = route if per_leg is None else _rebuild_route(
        route, [_xyz(w.point) for w in route_waypoints(route)], per_leg, f'{mission.mission_id}:timing')
    legs = CS.route_legs(timed, t0=0.0, speed=uniform)

    if len(legs) != len(mission.waypoints) - 1:
        return ()

    targets = _locked_targets(mission, t0)
    holds = []
    arrival = float(start)

    for index, mw in enumerate(mission.waypoints):
        leave = _wait_end(mw.actions, arrival, t0)

        if index < len(legs):
            travel = legs[index].duration
            target = targets.get(index + 1)

            if target is not None and leave + travel < target - CS.TIME_EPS:
                leave = target - travel
            elif target is not None and leave + travel > target + CS.TIME_EPS:
                logger.warning(f"mission_holds: mission {mission.mission_id!r} reaches waypoint {index + 1} at "
                               f"{leave + travel:.1f} s, after its locked time {target:.1f} s")

            next_arrival = leave + travel
        else:
            next_arrival = None

        if leave - arrival > CS.TIME_EPS:
            holds.append((index, leave - arrival))

        if next_arrival is not None:
            arrival = next_arrival

    return tuple(holds)


# ── PRESENZA PRIMA DELLA PARTENZA E DOPO LA FINE (F5, D1.a/b) ─────────────────

def is_air_base_reference(reference) -> bool:
    """Il riferimento di un waypoint e' su una BASE AEREA VERA (criterio della F5, v. docstring).

    `Waypoint.reference` e' un `Asset`; e' una base vera se il suo blocco (`asset.block`) dichiara
    `is_Air_Base()` vero (`Military` di categoria `MILITARY_CATEGORY['Air_Base']`: 'Airbase',
    'Heliport'). Un riferimento assente o di un altro blocco non lo e'.
    """
    block = getattr(reference, 'block', None)
    check = getattr(block, 'is_Air_Base', None)

    try:
        return callable(check) and bool(check())
    except Exception:   # noqa: BLE001 — un blocco senza categoria leggibile non e' una base
        return False


def air_base_points(blocks: Iterable, side: Optional[str] = None) -> Tuple[Tuple[float, float], ...]:
    """Posizioni orizzontali (x, y) che definiscono l'AREA delle basi aeree vere (F5-B).

    Gli asset NON aerei (strutture, difese, veicoli) dei blocchi che dichiarano `is_Air_Base()`
    vero, del solo lato `side` se dato (None = tutti). Gli aerei sono esclusi: la loro posizione
    registrata non e' la base (possono essere in volo o in missione altrove). Ordine: blocchi e
    asset nell'ordine dato (le posizioni servono solo a un test di distanza).
    """
    points = []

    for block in blocks:
        check = getattr(block, 'is_Air_Base', None)

        try:
            is_base = callable(check) and bool(check())
        except Exception:   # noqa: BLE001 — un blocco senza categoria leggibile non e' una base
            is_base = False

        if not is_base or (side is not None and getattr(block, 'side', None) != side):
            continue

        for asset in (getattr(block, 'assets', None) or {}).values():
            position = getattr(asset, 'position', None)

            if position is None or validate_class(asset, 'Aircraft'):
                continue

            points.append((float(position.x), float(position.y)))

    return tuple(points)


def lands_on_air_base(mission: Mission, air_bases: Iterable[Tuple[float, float]] = ()) -> bool:
    """La missione aerea finisce con un punto LAND su una base vera.

    Due criteri, basta uno (decisione dell'utente, F5-B):
      * il riferimento del waypoint e' un asset di una base vera (`is_air_base_reference`);
      * il punto sta nell'AREA di una base: entro `AIR_BASE_AREA_RADIUS_M` (in orizzontale) da una
        delle posizioni `air_bases` (`air_base_points`, in sessione quelle del lato della missione).
    """
    if mission.domain != 'air' or not mission.waypoints:
        return False

    last = mission.waypoints[-1]

    if last.role is not WaypointRole.LAND:
        return False

    if is_air_base_reference(last.waypoint.reference):
        return True

    x, y, _ = _xyz(last.waypoint.point)
    return any(math.hypot(x - bx, y - by) <= AIR_BASE_AREA_RADIUS_M for bx, by in air_bases)


def _presence(mission: Mission, air_bases: Iterable[Tuple[float, float]] = ()) -> Dict[str, bool]:
    """Presenza e stato a terra prima della partenza e dopo la fine (decisioni D1.a/b, F5)."""
    if mission.domain != 'air':
        return dict(present_before=True, present_after=True, grounded_before=False, grounded_after=False)

    parked = mission.start_mode is not StartMode.AIR
    landed = lands_on_air_base(mission, air_bases)
    return dict(present_before=parked, present_after=landed, grounded_before=parked, grounded_after=landed)


def mission_movements(mission: Mission, t0: float = 0.0,
                      air_bases: Iterable[Tuple[float, float]] = ()) -> Tuple[AssetMovement, ...]:
    """Un `AssetMovement` per asset della missione, nell'ordine degli asset (con attese e presenza
    della F5: `mission_holds` con `F5_WAITS`, `_presence` con `F5_PRESENCE`). `air_bases`: le
    posizioni dell'area delle basi aeree (`air_base_points`) per il criterio d'atterraggio; vuoto =
    solo il riferimento del waypoint."""
    start = mission_start(mission, t0)
    holds = mission_holds(mission, start, t0) if F5_WAITS else ()
    presence = _presence(mission, tuple(air_bases)) if F5_PRESENCE else {}

    movements = []

    for mission_asset in mission.assets:
        route, speed = asset_route(mission, mission_asset)
        movements.append(AssetMovement(mission.mission_id, mission_asset.asset_id, route, start, speed,
                                       holds=holds, **presence))

    return tuple(movements)


def _timeline(movement: AssetMovement) -> Tuple[List[CS.Leg], Tuple[float, ...]]:
    """(tratti del movimento con le attese, istanti d'ARRIVO ai punti), senza taglio alla sessione.

    Senza attese i tratti sono esattamente `route_legs` (stessi valori). Un'attesa al punto i e' un
    tratto fermo nel punto i della rotta dell'asset; i tratti successivi sono spostati della sua
    durata. Liste vuote se l'asset non ha rotta o la rotta non e' percorribile.
    """
    if movement.route is None:
        return [], ()

    legs = CS.route_legs(movement.route, t0=movement.start, speed=movement.speed)

    if not legs:
        return [], ()

    arrivals = [legs[0].t_start] + [leg.t_end for leg in legs]

    if not movement.holds:
        return legs, tuple(arrivals)

    holds = dict(movement.holds)
    timeline: List[CS.Leg] = []
    shift = 0.0
    arrivals = []

    for index in range(len(legs) + 1):
        point = legs[index].p_start if index < len(legs) else legs[-1].p_end
        here = legs[index].t_start + shift if index < len(legs) else legs[-1].t_end + shift
        arrivals.append(here)
        hold = holds.get(index, 0.0)

        if hold > CS.TIME_EPS:
            timeline.append(CS.Leg(t_start=here, t_end=here + hold, p_start=point, p_end=point, edge_name=None))
            shift += hold

        if index < len(legs):
            leg = legs[index]
            timeline.append(CS.Leg(t_start=leg.t_start + shift, t_end=leg.t_end + shift, p_start=leg.p_start,
                                   p_end=leg.p_end, edge_name=leg.edge_name))

    return timeline, tuple(arrivals)


def movement_legs(movement: AssetMovement, t0: float, t_end: float, presence: bool = True) -> List[CS.Leg]:
    """Tratti dell'asset nella sessione `[t0, t_end]` (F5), nella forma di `Contact_Scheduler`.

    Movimento con le attese (`_timeline`); con `presence` anche il tratto fermo nella posizione di
    partenza da `t0` alla partenza (`present_before`) e quello nella posizione finale dalla fine
    del movimento a `t_end` (`present_after`). Ritagliati a `[t0, t_end]` con `clamp_legs`, come
    faceva lo scheduler: senza attese ne' presenza i valori sono quelli di prima. `presence=False`
    = solo il movimento (consumo di carburante, `Session_Simulator`). Lista vuota se l'asset non ha
    una rotta percorribile (il chiamante lo tiene fermo nella sua posizione).
    """
    timeline, _ = _timeline(movement)

    if not timeline:
        return []

    legs = list(timeline)

    if presence and movement.present_before and timeline[0].t_start > t0 + CS.TIME_EPS:
        point = timeline[0].p_start
        legs.insert(0, CS.Leg(t_start=float(t0), t_end=timeline[0].t_start, p_start=point, p_end=point))

    if presence and movement.present_after and timeline[-1].t_end < t_end - CS.TIME_EPS:
        point = timeline[-1].p_end
        legs.append(CS.Leg(t_start=timeline[-1].t_end, t_end=float(t_end), p_start=point, p_end=point))

    return CS.clamp_legs(legs, t0, t_end)


def grounded_intervals(movement: AssetMovement) -> Tuple[Tuple[float, float], ...]:
    """Intervalli `[lo, hi)` in cui l'aereo di missione e' A TERRA (F5).

    Prima del decollo (`grounded_before`): (-inf, fine delle attese al punto di partenza), cioe' il
    parcheggio e un'eventuale sosta a terra prima del decollo. Dopo l'atterraggio su una base vera
    (`grounded_after`): [arrivo all'ultimo punto, +inf), compresa un'eventuale sosta a terra.
    """
    _, arrivals = _timeline(movement)

    if not arrivals:
        return ()

    holds = dict(movement.holds)
    spans = []

    if movement.grounded_before:
        spans.append((float('-inf'), arrivals[0] + holds.get(0, 0.0)))

    if movement.grounded_after:
        spans.append((arrivals[-1], float('inf')))

    return tuple(spans)


def grounded_schedule(forces: Mapping[str, object], movements: Iterable[AssetMovement] = ()) -> CS.GroundedSchedule:
    """Gli aerei A TERRA della sessione nel tempo (F5): `Contact_Scheduler.GroundedSchedule`.

    Sempre a terra gli aerei senza missione (`grounded_assets`, F4c); a intervalli gli aerei di
    missione prima del decollo e dopo l'atterraggio su una base vera (`grounded_intervals`).
    """
    intervals: Dict[str, List[Tuple[float, float]]] = {asset_id: [CS.ALWAYS] for asset_id in grounded_assets(forces)}

    for movement in movements:
        spans = grounded_intervals(movement)

        if spans:
            intervals.setdefault(movement.asset_id, []).extend(spans)

    return CS.GroundedSchedule(intervals)


def session_movements(missions: Iterable[Mission], t0: float = 0.0
                      ) -> Tuple[Dict[str, Route], Dict[str, float], Dict[str, float]]:
    """`(routes, starts, speeds)` per `schedule_contacts`/`run_session` da tutte le missioni.

    Solo gli asset con rotta compaiono nelle mappe (gli altri restano fermi, come prima); `speeds`
    solo per gli asset con velocita' uniforme dichiarata. Le mappe NON portano le attese ne' la
    presenza (F5): in sessione i tratti completi vanno allo scheduler come `legs`
    (`movement_legs`), che hanno la precedenza.

    Raises:
        ValueError: un asset in due missioni (lo vieta gia' `SessionOrder`; qui per chi chiama
            direttamente), e gli errori di `mission_movements`.
    """
    routes: Dict[str, Route] = {}
    starts: Dict[str, float] = {}
    speeds: Dict[str, float] = {}
    seen: Dict[str, str] = {}

    for mission in missions:
        for movement in mission_movements(mission, t0):
            if movement.asset_id in seen:
                raise ValueError(f"asset {movement.asset_id!r} is in missions {seen[movement.asset_id]!r} "
                                 f"and {movement.mission_id!r}")

            seen[movement.asset_id] = movement.mission_id

            if movement.route is None:
                continue

            routes[movement.asset_id] = movement.route
            starts[movement.asset_id] = movement.start

            if movement.speed is not None:
                speeds[movement.asset_id] = movement.speed

    return routes, starts, speeds


def waypoint_times(movement: AssetMovement) -> Tuple[float, ...]:
    """Istanti assoluti [s] di ARRIVO ai punti della rotta dell'asset (0 = partenza), con le attese
    (F5: ETA effettive, `_timeline`), senza taglio alla sessione; tupla vuota se l'asset non ha
    rotta o la rotta non e' percorribile."""
    return _timeline(movement)[1]


def _max_speed(asset) -> Optional[float]:
    """Velocita' massima [m/s] dell'asset dal profilo cinematico, None se non disponibile."""
    profile = getattr(asset, 'speed', None)

    if not isinstance(profile, Mapping):
        return None

    value = profile.get('max')
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0 else None


def planned_speeds(movement: AssetMovement) -> Tuple[float, ...]:
    """Velocita' pianificate [m/s] dei tratti dell'asset: quella di missione, o quella dell'arco."""
    if movement.route is None:
        return ()

    if movement.speed is not None:
        return tuple(float(movement.speed) for _ in movement.route.edges)

    return tuple(float(edge.speed) for edge in movement.route.edges.values() if edge.speed is not None)


def check_mission_speed(mission: Mission, assets: Mapping[str, object], t0: float = 0.0) -> Optional[float]:
    """Regola A (v. docstring del modulo): nessun tratto piu' veloce del mezzo piu' lento.

    Args:
        mission: la missione.
        assets: `{asset_id: asset}` che contiene almeno gli asset della missione (gli id di
            dominio, come in `Mission.asset_ids`).
        t0: inizio della sessione (serve solo a derivare i movimenti).

    Returns:
        Il limite applicato [m/s] (la velocita' massima del mezzo piu' lento con il dato), None
        se nessun asset della missione ha la velocita' massima nota (controllo non fatto) o la
        missione non si muove.

    Raises:
        ValueError: un tratto pianificato supera il limite.
    """
    movements = mission_movements(mission, t0)
    planned = max((speed for movement in movements for speed in planned_speeds(movement)), default=None)

    if planned is None:
        return None

    limits = {}

    for asset_id in mission.asset_ids:
        limit = _max_speed(assets.get(asset_id))

        if limit is None:
            logger.warning(f"check_mission_speed: mission {mission.mission_id!r}, asset {asset_id!r} has no "
                           f"known max speed: excluded from the rule-A check")
            continue

        limits[asset_id] = limit

    if not limits:
        return None

    slowest = min(limits, key=lambda asset_id: (limits[asset_id], asset_id))
    limit = limits[slowest]

    if planned > limit + SPEED_TOLERANCE:
        raise ValueError(f"mission {mission.mission_id!r}: planned speed {planned:.3f} m/s exceeds the max speed "
                         f"{limit:.3f} m/s of its slowest asset {slowest!r} (a mission moves together, at the "
                         f"speed of its slowest asset)")

    logger.debug(f"check_mission_speed: mission {mission.mission_id!r}, planned {planned:.3f} m/s <= "
                 f"{limit:.3f} m/s ({slowest!r})")
    return limit


# ── BINGO A PRIORI (F6-B2, validatore di pianificazione) ──────────────────────

def airborne_legs(movement: AssetMovement) -> List[CS.Leg]:
    """Tratti del movimento che CONSUMANO carburante, senza taglio alla sessione (F6-B2).

    I tratti di `_timeline` (movimento e attese, la missione intera: andata, attese, ritorno) esclusi
    quelli di durata nulla e quelli FERMI di un aereo A TERRA (`grounded_intervals`: parcheggio prima
    del decollo, sosta dopo l'atterraggio su una base vera), come `Session_Simulator._consuming_legs`
    in sessione."""
    timeline, _ = _timeline(movement)
    spans = grounded_intervals(movement)
    legs = []

    for leg in timeline:
        if leg.duration <= CS.TIME_EPS:
            continue

        middle = 0.5 * (leg.t_start + leg.t_end)

        if FM.is_stationary(leg) and any(lo <= middle < hi for lo, hi in spans):
            continue

        legs.append(leg)

    return legs


def is_loop_mission(mission: Mission) -> bool:
    """La missione aerea e' ad ANELLO: parte da una base (`start_mode` diverso da AIR, primo punto DEPARTURE) e
    finisce con un LAND sulla STESSA base (F6-B2bis, v. "Bingo a priori" nel docstring del modulo).

    "Stessa base", deterministico, con lo stesso modello di `lands_on_air_base` (F5-B):
      * se i riferimenti di DEPARTURE e LAND sono ENTRAMBI asset di una base vera (`is_air_base_reference`),
        decide il blocco: stessa base se e solo se e' lo stesso oggetto blocco;
      * altrimenti decide la distanza orizzontale fra i due punti: entro `AIR_BASE_AREA_RADIUS_M` (l'area di
        una base, stima gia' dichiarata della F5-B) sono la stessa base.
    """
    if mission.domain != 'air' or mission.start_mode is StartMode.AIR or len(mission.waypoints) < 2:
        return False

    first, last = mission.waypoints[0], mission.waypoints[-1]

    if first.role is not WaypointRole.DEPARTURE or last.role is not WaypointRole.LAND:
        return False

    origin, landing = first.waypoint.reference, last.waypoint.reference

    if is_air_base_reference(origin) and is_air_base_reference(landing):
        return origin.block is landing.block

    (x0, y0, _), (x1, y1, _) = _xyz(first.waypoint.point), _xyz(last.waypoint.point)
    return math.hypot(x1 - x0, y1 - y0) <= AIR_BASE_AREA_RADIUS_M


def bingo_return_rule(mission: Mission) -> FM.ReturnRule:
    """La regola di rientro al bingo lungo la rotta a ritroso (F6-B2bis) della missione aerea: partenza da una
    base se `start_mode` non e' AIR (il primo punto e' allora il DEPARTURE, `Mission` lo impone), anello se
    `is_loop_mission`; fattore `Fuel_Model.BINGO_RETURN_FACTOR`. La usano il validatore (`check_mission_bingo`)
    e l'esecutore (`Session_Simulator`): stesso criterio."""
    departure = mission.start_mode is not StartMode.AIR
    return FM.ReturnRule(departure=departure, loop=departure and is_loop_mission(mission))


def is_transfer_mission(mission: Mission) -> bool:
    """La missione aerea e' un TRASFERIMENTO per l'albero di bingo del G2: categoria TRANSPORT nella mappa tipo
    -> categoria di Context (`Mission.category`, oggi il solo task 'Transport'). Ogni altra missione aerea
    (combattimento aria-aria e aria-suolo, AWACS, Tanker, Recon, ...) segue la regola di COMBATTIMENTO."""
    return mission.domain == 'air' and mission.category is Mission_Category.TRANSPORT


def mission_bingo_decision(mission: Mission, movement: AssetMovement, asset, air_bases: Iterable[Tuple[float, float]],
                           time: Optional[float] = None, fuel: Optional[float] = None,
                           legs: Optional[Sequence] = None, forced: bool = False,
                           exit_scene: bool = False) -> Optional[FM.BingoDecision]:
    """Soglia di bingo e albero di decisione del G2 (`Fuel_Model.bingo_decision`) per un asset della missione:
    tratti della missione INTERA (`airborne_legs`, o `legs` se dati: in sessione quelli che consumano),
    partenza e anello dalla regola della missione (`bingo_return_rule`), trasferimento o combattimento dal tipo
    (`is_transfer_mission`). `time` None = l'inizio dei tratti, `fuel` None = il carburante dell'asset. La
    usano il validatore (`check_mission_bingo`) e l'esecutore (`Session_Simulator`): stesso criterio.

    `forced` (G4b): RIENTRO FORZATO dopo il disingaggio della forza d'ingaggio, sempre con la regola di
    COMBATTIMENTO (`transfer` False qualunque sia il tipo di missione, decisione dell'utente del 2026-10-17) e
    senza controllo di soglia (v. `Fuel_Model.bingo_decision`).

    `exit_scene` (G4b, decisione dell'utente del 2026-10-17): partenza in volo senza alcuna base del lato, uscita
    di scena al punto di comparsa (`Fuel_Model.BINGO_EXIT`) al posto di `BINGO_NO_BASE`; la usa solo la
    ri-pianificazione dopo un episodio, non il validatore ne' la decisione alla partenza."""
    legs = airborne_legs(movement) if legs is None else legs
    return FM.bingo_decision(asset, legs, air_bases, bingo_return_rule(mission),
                             transfer=False if forced else is_transfer_mission(mission), time=time, fuel=fuel,
                             forced=forced, exit_scene=exit_scene)


def check_mission_bingo(mission: Mission, assets: Mapping[str, object], air_bases: Iterable[Tuple[float, float]],
                        t0: float = 0.0, reserve: Optional[float] = None,
                        reverse_route: bool = True, disengage_reserve: bool = True) -> Optional[Dict[str, float]]:
    """Bingo A PRIORI (v. "Bingo a priori" nel docstring del modulo): una missione aerea che in volo
    arriverebbe al bingo e' RIFIUTATA.

    `disengage_reserve` True (G2, come `Session_Simulator.F6_BINGO_DISENGAGE_RESERVE` acceso, il default):
    rifiutata se un asset parte in bingo (`mission_bingo_decision` all'inizio dei tratti: carburante < rotta
    intera + riserva di disimpegno), cioe' ESATTAMENTE la missione che in sessione va in bingo (anche un
    trasferimento che poi continua consumando la riserva); `reserve` e `reverse_route` non sono usati e le
    basi non sono richieste (servono al rientro, non alla soglia). Il margine e' carburante - soglia.

    Con `disengage_reserve` False, per ogni asset della missione, sulla missione intera alla crociera
    (`airborne_legs`: andata, attese, ritorno pianificati, senza taglio alla sessione):
      * `reverse_route` True (F6-B2bis, come `Session_Simulator.F6_BINGO_REVERSE_ROUTE` acceso): il
        carburante non scende mai sotto `Fuel_Model.BINGO_RETURN_FACTOR` x il ritorno lungo la rotta a
        ritroso (regola `bingo_return_rule`); `reserve` non e' usata;
      * `reverse_route` False (F6-B2, interruttore spento): carburante - fabbisogno - rientro in linea retta
        dall'ultimo punto alla base idonea piu' vicina - riserva >= 0.
    Il chiamante passa `reverse_route` uguale all'interruttore dell'esecutore: e' lo stesso criterio
    (`Fuel_Model.bingo_point`).

    Args:
        mission: la missione.
        assets: `{asset_id: asset}` che contiene almeno gli asset della missione.
        air_bases: posizioni (x, y) delle basi IDONEE (`air_base_points` del lato della missione: qualunque
            base aerea amica, come la planata della F6-A; idoneita' per tipo d'aereo non modellata).
        t0: inizio della sessione (serve solo a derivare i movimenti).
        reserve: riserva della regola F6-B2 [frazione del carico pieno], None = `Fuel_Model.BINGO_RESERVE`.
        reverse_route: regola del rientro (sopra), con `disengage_reserve` False.
        disengage_reserve: regola del G2 (sopra).

    Returns:
        `{asset_id: margine}` [frazione del carico pieno, >= 0, v. `Fuel_Model.return_margin`] degli asset
        controllati; None se il controllo non si applica (missione non aerea, o `EndCriteria.bingo` False: la
        missione dichiara di non rientrare al bingo). Un asset con carburante non modellato o senza rotta
        non e' controllato (debug).

    Raises:
        ValueError: nessuna base idonea a cui rientrare quando serve (F6-B2 sempre; F6-B2bis solo con
            partenza in volo: partendo da una base il rientro finisce sul DEPARTURE; G2 mai), oppure un asset
            arriverebbe al bingo (il messaggio dice quanto carburante manca e dove cadrebbe il bingo in volo;
            G2: soglia, riserva e decisione dell'albero).
    """
    if mission.domain != 'air' or not mission.end_criteria.bingo:
        return None

    if disengage_reserve:
        return _check_reserve_bingo(mission, assets, tuple(air_bases), t0)

    reserve = FM.BINGO_RESERVE if reserve is None else float(reserve)
    rule = bingo_return_rule(mission) if reverse_route else None
    bases = tuple(air_bases)

    if not bases and (rule is None or not rule.departure):
        reason = "it cannot return with the fuel reserve (bingo)" if rule is None else \
            "an aircraft starting in the air cannot return at bingo"
        raise ValueError(f"mission {mission.mission_id!r}: no suitable air base of its side to return to: {reason}")

    margins: Dict[str, float] = {}

    for movement in mission_movements(mission, t0, bases):
        asset = assets.get(movement.asset_id)
        legs = airborne_legs(movement)
        margin = None if asset is None else FM.return_margin(asset, legs, bases, reserve, rule=rule)

        if margin is None:
            logger.debug(f"check_mission_bingo: mission {mission.mission_id!r}, asset {movement.asset_id!r}: fuel "
                         f"not modelled or no route, not checked")
            continue

        # Lo stesso criterio del bingo in volo (`Fuel_Model.bingo_point`, che esiste se e solo se il margine
        # e' negativo): la missione rifiutata qui e' esattamente quella che in sessione tornerebbe al bingo.
        bingo = FM.bingo_point(asset, legs, bases, reserve, rule=rule)

        if bingo is not None and rule is None:
            raise ValueError(f"mission {mission.mission_id!r}: asset {movement.asset_id!r} does not return with the "
                             f"fuel reserve ({reserve:.3f} of a full load): {-margin:.4f} of a full load is missing "
                             f"for the route and the return to the nearest air base (fuel {float(asset.fuel):.4f}); "
                             f"in flight it would reach bingo at t={bingo.time:.1f} s")

        if bingo is not None:
            raise ValueError(f"mission {mission.mission_id!r}: asset {movement.asset_id!r} does not keep the bingo "
                             f"fuel ({rule.factor:.2f} x the return along its route): {-margin:.4f} of a full load "
                             f"is missing (fuel {float(asset.fuel):.4f}); in flight it would reach bingo at "
                             f"t={bingo.time:.1f} s and return {bingo.via} ({bingo.return_length:.0f} m)")

        margins[movement.asset_id] = margin

    return margins


def _check_reserve_bingo(mission: Mission, assets: Mapping[str, object], bases: Tuple[Tuple[float, float], ...],
                         t0: float) -> Dict[str, float]:
    """`check_mission_bingo` con la regola del G2 (v. il suo docstring)."""
    margins: Dict[str, float] = {}

    for movement in mission_movements(mission, t0, bases):
        asset = assets.get(movement.asset_id)
        legs = airborne_legs(movement)
        threshold = None if asset is None or getattr(asset, 'fuel', None) is None else FM.bingo_threshold(asset, legs)

        if threshold is None:
            logger.debug(f"check_mission_bingo: mission {mission.mission_id!r}, asset {movement.asset_id!r}: fuel "
                         f"or reserve not modelled, or no route, not checked")
            continue

        # Lo stesso criterio del bingo in sessione (`mission_bingo_decision` all'inizio dei tratti): la missione
        # rifiutata qui e' esattamente quella che in sessione va in bingo.
        decision = mission_bingo_decision(mission, movement, asset, bases, legs=legs)

        if decision is not None:
            where = 'continues on its route consuming the reserve' if decision.action == FM.BINGO_CONTINUE else \
                f"decides {decision.action!r}" + ('' if decision.via is None else
                                                  f" ({decision.via}, {decision.return_length:.0f} m)")
            raise ValueError(f"mission {mission.mission_id!r}: asset {movement.asset_id!r} starts under the bingo "
                             f"threshold: fuel {decision.fuel:.4f} < rest of the route {decision.rest:.4f} + "
                             f"disengagement reserve {decision.reserve:.4f}: {decision.threshold - decision.fuel:.4f} "
                             f"of a full load is missing; in flight it reaches bingo at t={decision.time:.1f} s and "
                             f"{where}")

        margins[movement.asset_id] = float(asset.fuel) - threshold

    return margins


def route_fuel_demand(asset, legs: Sequence) -> Optional[float]:
    """Carburante [frazione del carico pieno] dei tratti `legs` (la rotta intera, `airborne_legs`) alla
    crociera, attese comprese nel tempo (`Fuel_Model.leg_fuel_demand`); None se non modellato."""
    total = 0.0

    for leg in legs:
        demand = FM.leg_fuel_demand(asset, leg)

        if demand is None:
            return None

        total += demand

    return total


def check_mission_fuel(mission: Mission, assets: Mapping[str, object], t0: float = 0.0,
                       air_bases: Iterable[Tuple[float, float]] = ()) -> Optional[Dict[str, float]]:
    """Minimo di PIANIFICAZIONE del carburante (G1, v. "Bingo a priori" nel docstring del modulo): ogni aereo
    della missione deve caricare PIU' del carburante della rotta intera + la riserva di disimpegno.

    Per ogni asset con carburante modellato: `asset.fuel > fabbisogno + riserva`, dove il fabbisogno e' la
    rotta INTERA pianificata alla crociera (`airborne_legs`: andata, attese, ritorno; le soste a terra non
    consumano) e la riserva e' `Fuel_Model.disengagement_reserve` (5 minuti alla massima spinta militare,
    stima). E' un controllo distinto da `check_mission_bingo` (che verifica il criterio del bingo in volo
    dell'esecutore): i due si possono chiamare entrambi. Dal G2 `check_mission_bingo` usa la stessa grandezza
    come soglia di bingo (rifiuto con carburante < minimo, qui con carburante <= minimo: differiscono solo
    all'uguaglianza, v. "Bingo a priori" nel docstring del modulo). NON e' chiamato da
    `Session_Simulator.run_session`.

    Args:
        mission: la missione.
        assets: `{asset_id: asset}` che contiene almeno gli asset della missione.
        t0: inizio della sessione (serve solo a derivare i movimenti).
        air_bases: posizioni (x, y) delle basi aeree del lato (`air_base_points`), solo per riconoscere
            l'atterraggio su una base vera (la sosta dopo non consuma), come `mission_movements`.

    Returns:
        `{asset_id: margine}` [frazione del carico pieno, > 0: carburante - fabbisogno - riserva] degli asset
        controllati; None se il controllo non si applica (missione non aerea, o `EndCriteria.bingo` False).
        Un asset senza carburante modellato, senza rotta o senza riserva modellata non e' controllato (debug).

    Raises:
        ValueError: un asset non carica piu' di rotta intera + riserva (il messaggio dice asset, carburante,
            fabbisogno, riserva con la sua provenienza e mancanza).
    """
    if mission.domain != 'air' or not mission.end_criteria.bingo:
        return None

    margins: Dict[str, float] = {}

    for movement in mission_movements(mission, t0, tuple(air_bases)):
        asset = assets.get(movement.asset_id)
        fuel = None if asset is None else getattr(asset, 'fuel', None)
        legs = airborne_legs(movement)
        demand = None if fuel is None or not legs else route_fuel_demand(asset, legs)
        reserve = None if demand is None else FM.disengagement_reserve_with_source(asset)

        if reserve is None:
            logger.debug(f"check_mission_fuel: mission {mission.mission_id!r}, asset {movement.asset_id!r}: fuel or "
                         f"reserve not modelled, or no route: not checked")
            continue

        reserve, source = reserve
        margin = float(fuel) - demand - reserve

        if margin <= 0.0:
            raise ValueError(f"mission {mission.mission_id!r}: asset {movement.asset_id!r} loads fuel "
                             f"{float(fuel):.4f} of a full load, not more than the whole route {demand:.4f} + the "
                             f"disengagement reserve {reserve:.4f} ({source}, {FM.DISENGAGE_TIME:.0f} s at max "
                             f"military thrust): {-margin:.4f} of a full load is missing")

        logger.debug(f"check_mission_fuel: mission {mission.mission_id!r}, asset {movement.asset_id!r}: fuel "
                     f"{float(fuel):.4f} > route {demand:.4f} + reserve {reserve:.4f} ({source})")
        margins[movement.asset_id] = margin

    return margins


def mission_routes(missions: Iterable[Mission], t0: float = 0.0) -> Dict[str, Route]:
    """Solo le rotte per asset di `session_movements` (comodita' per chi interroga lo scheduler)."""
    return session_movements(missions, t0)[0]


# ── VISTA D'INGAGGIO (F4b) ────────────────────────────────────────────────────

def _domain_id(obj) -> Optional[str]:
    """Id di dominio (id, poi name): stesso criterio di `Engagement_Resolver`/`Session_Simulator`."""
    for attribute in ('id', 'name'):
        value = getattr(obj, attribute, None)

        if isinstance(value, str) and value:
            return value

    return None


# ── POSTURA CONTINUA (F4c, D1.c) ──────────────────────────────────────────────

def continuous_posture(asset) -> str:
    """Postura continua di un asset SENZA missione (v. "Postura continua" nel docstring).

    Aereo (`Aircraft` nella gerarchia di classe) -> `PARKED_POSTURE` (a terra, bersaglio di
    superficie passivo); nave -> `SEA_DEFENSE_POSTURE`; ogni altro asset (veicolo, struttura,
    stub) -> `GROUND_DEFENSE_POSTURE`. Funzione pura: non legge ne' muta lo stato dell'asset.
    """
    if validate_class(asset, 'Aircraft'):
        return PARKED_POSTURE

    if validate_class(asset, 'Ship'):
        return SEA_DEFENSE_POSTURE

    return GROUND_DEFENSE_POSTURE


def unassigned_postures(assets: Iterable) -> Dict[str, str]:
    """`{asset_id: postura continua}` di asset senza missione (gli asset senza id sono saltati)."""
    postures: Dict[str, str] = {}

    for asset in assets:
        asset_id = _domain_id(asset)

        if asset_id is not None:
            postures[asset_id] = continuous_posture(asset)

    return postures


def grounded_assets(forces: Mapping[str, object]) -> FrozenSet[str]:
    """Id degli aerei A TERRA fra le forze d'ingaggio della sessione (F4c).

    Args:
        forces: `{force_id: forza}` come le costruisce `Session_Simulator._engagement_forces`. A
            terra sono gli aerei della vista residua (`MissionForce.grounded`) e di un blocco
            senza missioni (passato tale e quale: stessa regola, `continuous_posture`); gli aerei
            di una vista di missione no (a terra solo a intervalli, prima del decollo e dopo
            l'atterraggio: `grounded_schedule`, F5).

    Returns:
        Insieme (vuoto se non ce ne sono: comportamento identico a prima della F4c).
    """
    grounded = set()

    for force in forces.values():
        if isinstance(force, MissionForce):
            grounded |= force.grounded
            continue

        postures = unassigned_postures((getattr(force, 'assets', None) or {}).values())
        grounded |= {asset_id for asset_id, posture in postures.items() if posture == PARKED_POSTURE}

    return frozenset(grounded)


# ── POSTURA NELL'ESITO (F5, deviazione 12 del piano) ──────────────────────────

def final_posture(mission: Mission, movement: AssetMovement, grounded: CS.GroundedSchedule,
                  session_end: float) -> str:
    """Postura di un asset DI MISSIONE alla fine della sessione (F5, deviazione 12 del piano; v.
    "Presenza prima della partenza e dopo la fine" nel docstring del modulo).

    * a terra a `session_end` (parcheggiato prima del decollo, atterrato su una base vera):
      `PARKED_POSTURE`;
    * aereo in volo: il tipo di missione (per l'aria il task E' l'asse della postura, N3.f);
      uscito di scena alla fine della rotta: `OFF_SCENE_POSTURE`;
    * terra e mare: `Defense` di fine missione (D1.a) se ha finito il movimento o non e' ancora
      partito (D1.b); in movimento, o in missione sul posto (senza rotta), la postura di
      riferimento del tipo di missione (`Context.postures_for`).
    """
    if grounded.at(movement.asset_id, session_end):
        return PARKED_POSTURE

    timeline, _ = _timeline(movement)

    if mission.domain == 'air':
        if timeline and timeline[-1].t_end <= session_end + CS.TIME_EPS and not movement.present_after:
            return OFF_SCENE_POSTURE

        return mission.mission_type

    if timeline and (timeline[-1].t_end <= session_end + CS.TIME_EPS or timeline[0].t_start >= session_end):
        return SEA_DEFENSE_POSTURE if mission.domain == 'sea' else GROUND_DEFENSE_POSTURE

    return postures_for(mission.domain, mission.mission_type)[1]


def session_postures(forces: Mapping[str, object], movements: Mapping[str, AssetMovement],
                     grounded: CS.GroundedSchedule, session_end: float) -> Dict[str, str]:
    """`{asset_id: postura finale}` di TUTTI gli asset delle forze d'ingaggio, in ordine di id (F5).

    Asset di missione: `final_posture`; asset senza missione (vista residua o blocco senza
    missioni, passato tale e quale): la postura continua della F4c (`continuous_posture`).

    Args:
        forces: `{force_id: forza}` come le costruisce `Session_Simulator._engagement_forces`.
        movements: `{asset_id: AssetMovement}` degli asset di missione.
    """
    postures: Dict[str, str] = {}

    for force in forces.values():
        mission = force.mission if isinstance(force, MissionForce) else None

        for asset in (getattr(force, 'assets', None) or {}).values():
            asset_id = _domain_id(asset)

            if asset_id is None:
                continue

            if mission is not None and asset_id in movements:
                postures[asset_id] = final_posture(mission, movements[asset_id], grounded, session_end)
            else:
                postures[asset_id] = continuous_posture(asset)

    return dict(sorted(postures.items()))


class MissionForce:
    """Una missione vista come FORZA d'ingaggio (v. "La missione come forza d'ingaggio").

    Espone al risolutore solo cio' che legge della forza: `id`/`name`, `side`, `assets`,
    `salvo_interceptors()` e `can_disengage`. Gli asset sono gli oggetti REALI del blocco (la vista
    non li copia): danno, munizioni e carburante applicati dal motore arrivano al blocco.

    Attributes:
        id/name: `mission_id` (vista residua: id e nome del blocco).
        mission_id: id della missione, None per la vista residua degli asset senza missione.
        mission: la `Mission`, None per la vista residua.
        owner_block: il blocco d'appartenenza (`Block`/`Military`), non `block` (v. docstring).
        block_id: id di dominio del blocco.
        side: lato del blocco.
        assets: `{chiave: asset}` del blocco ristretto agli asset della vista, con le chiavi e
            nell'ordine del blocco.
        can_disengage: diritto a una politica di disingaggio, con la regola di
            `Engagement_Resolver._can_disengage` applicata al BLOCCO (adattatore: la vista non e'
            ne' `Military` ne' `Block`).
        postures: `{asset_id: postura continua}` degli asset della vista residua (F4c,
            `continuous_posture`); vuota per una vista di missione.
        grounded: id degli aerei a terra della vista (postura `PARKED_POSTURE`); vuoto per una
            vista di missione.
    """

    def __init__(self, block, asset_ids: Iterable[str], force_id: str, name: str,
                 mission: Optional[Mission] = None):
        block_id = _domain_id(block)

        if block_id is None:
            raise ValueError("the block of a MissionForce must have a domain id (id or name)")

        wanted = set(asset_ids)
        self.id = force_id
        self.name = name
        self.mission = mission
        self.mission_id = mission.mission_id if mission is not None else None
        self.owner_block = block
        self.block_id = block_id
        self.side = getattr(block, 'side', None)
        self.assets = {key: asset for key, asset in (getattr(block, 'assets', None) or {}).items()
                       if _domain_id(asset) in wanted}
        self.can_disengage = validate_class(block, 'Military') or not validate_class(block, 'Block')
        missing = sorted(wanted - {_domain_id(asset) for asset in self.assets.values()})

        if missing:
            raise ValueError(f"force {force_id!r}: assets {missing} do not belong to block {block_id!r}")

        # Postura continua (F4c): solo per la vista residua; una missione non ne ha (F5).
        self.postures: Dict[str, str] = unassigned_postures(self.assets.values()) if mission is None else {}
        self.grounded: FrozenSet[str] = frozenset(asset_id for asset_id, posture in self.postures.items()
                                                  if posture == PARKED_POSTURE)

    @classmethod
    def of_mission(cls, mission: Mission, block) -> 'MissionForce':
        """La vista della missione: i suoi asset, id e nome = `mission_id`.

        Raises:
            TypeError: `mission` non e' una `Mission`.
            ValueError: blocco diverso da `mission.block_id` o asset che non gli appartengono.
        """
        if not isinstance(mission, Mission):
            raise TypeError(f"mission must be a Mission, got {type(mission).__name__}")

        if _domain_id(block) != mission.block_id:
            raise ValueError(f"mission {mission.mission_id!r} belongs to block {mission.block_id!r}, "
                             f"not to {_domain_id(block)!r}")

        return cls(block, mission.asset_ids, mission.mission_id, mission.mission_id, mission)

    @classmethod
    def unassigned(cls, block, missions: Iterable[Mission]) -> Optional['MissionForce']:
        """La vista residua degli asset del blocco in NESSUNA delle `missions`, con id e nome del
        blocco e la postura continua dei suoi asset (F4c); None se non ne restano."""
        assigned = {asset_id for mission in missions for asset_id in mission.asset_ids}
        residual = [asset_id for asset_id in (_domain_id(asset) for asset in (getattr(block, 'assets', None) or {}).values())
                    if asset_id is not None and asset_id not in assigned]

        if not residual:
            return None

        name = getattr(block, 'name', None)
        return cls(block, residual, _domain_id(block), name if isinstance(name, str) and name else _domain_id(block))

    def salvo_interceptors(self) -> List[Tuple[object, int]]:
        """`salvo_interceptors()` del blocco ristretto agli asset della vista (stesso ordine);
        vuota se il blocco non lo espone."""
        provider = getattr(self.owner_block, 'salvo_interceptors', None)

        if not callable(provider):
            return []

        own = {_domain_id(asset) for asset in self.assets.values()}
        return [(asset, channels) for asset, channels in (provider() or []) if _domain_id(asset) in own]

    def __repr__(self) -> str:
        return (f"MissionForce(id={self.id!r}, block={self.block_id!r}, side={self.side!r}, "
                f"assets={len(self.assets)})")


# ── DOMINIO DI COORDINAMENTO (2026-10-11) ─────────────────────────────────────

def coordination_domains(forces: Mapping[str, object], operations: Iterable[Operation] = ()) -> Dict[str, str]:
    """`{force_id: chiave di dominio}` per le forze d'ingaggio (v. "Dominio di coordinamento").

    Args:
        forces: `{force_id: forza}` come le costruisce `Session_Simulator._engagement_forces`:
            `MissionForce` (di missione o residua) o blocchi senza missioni (id = id del blocco).
        operations: le `Operation` della sessione (`SessionOrder.operations`).

    Returns:
        Una voce per forza, chiave = id di forza minore del dominio. Funzione pura e
        deterministica (nessuna dipendenza dall'ordine dei dizionari).

    Raises:
        TypeError: `forces` non e' una mappa, `operations` contiene altro che `Operation`.
    """
    if not isinstance(forces, Mapping):
        raise TypeError(f"forces must be a mapping force_id -> force, got {type(forces).__name__}")

    operation_of: Dict[str, str] = {}

    for operation in operations or ():
        if not isinstance(operation, Operation):
            raise TypeError(f"operations must contain Operation, got {type(operation).__name__}")

        for mission_id in operation.mission_ids:
            operation_of.setdefault(mission_id, operation.operation_id)

    parent: Dict[tuple, tuple] = {}

    def find(node: tuple) -> tuple:
        parent.setdefault(node, node)

        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]

        return node

    def union(a: tuple, b: tuple) -> None:
        root_a, root_b = find(a), find(b)

        if root_a != root_b:
            parent[max(root_a, root_b)] = min(root_a, root_b)

    operation_sides: Dict[str, set] = {}

    for force_id in sorted(forces):
        force = forces[force_id]
        side = getattr(force, 'side', None)
        side_key = side if isinstance(side, str) else repr(side)
        node = ('force', force_id)
        find(node)

        if isinstance(force, MissionForce):
            block_id = force.block_id
            mission = force.mission
        else:
            block_id = _domain_id(force) or force_id
            mission = None

        union(node, ('block', side_key, block_id))

        if mission is not None:
            operation_id = operation_of.get(mission.mission_id, mission.operation_id)

            if operation_id is not None:
                union(node, ('operation', side_key, operation_id))
                operation_sides.setdefault(operation_id, set()).add(side_key)

    for operation_id in sorted(operation_sides):
        if len(operation_sides[operation_id]) > 1:
            logger.warning(f"coordination_domains: operation {operation_id!r} has missions of sides "
                           f"{sorted(operation_sides[operation_id])}: it links only the missions of the "
                           f"same side, one coordination domain per side")

    members: Dict[tuple, List[str]] = {}

    for force_id in sorted(forces):
        members.setdefault(find(('force', force_id)), []).append(force_id)

    return {force_id: min(group) for group in members.values() for force_id in group}


# ── REGOLE D'INGAGGIO DI MISSIONE (F7a) ───────────────────────────────────────

def _asset_sides(blocks: Mapping[str, object]) -> Dict[str, Optional[str]]:
    """`{asset_id: lato del blocco proprietario}` di tutti gli asset dei blocchi passati."""
    sides: Dict[str, Optional[str]] = {}

    for block in blocks.values():
        side = getattr(block, 'side', None)

        for asset in (getattr(block, 'assets', None) or {}).values():
            asset_id = _domain_id(asset)

            if asset_id is not None:
                sides[asset_id] = side

    return sides


def designated_targets(mission: Mission, blocks: Mapping[str, object], mission_of: Mapping[str, Mission],
                       assets: Mapping[str, object], side: Optional[str]
                       ) -> Tuple[FrozenSet[str], Optional[Tuple[float, float, float]]]:
    """Il bersaglio designato dalla missione (F7a, v. "F7a" nel docstring): `(id degli asset nemici, area)`.

    Args:
        mission: la missione; `side` e' il lato dei suoi asset (i nemici sono gli asset di lato diverso).
        blocks: `{block_id: blocco}` delle forze della sessione; `mission_of`: `{mission_id: Mission}`;
            `assets`: `{asset_id: asset}` di tutte le forze.

    Returns:
        ASSET: l'asset `target_id` se nemico. GROUP: gli asset del blocco `target_id`, oppure della missione
        `target_id`, oppure l'asset stesso, ristretti a `Target.asset_ids` se dichiarato, SEMPRE filtrati ai
        nemici (un gruppo amico, come la missione protetta di una scorta, non designa nessuno). Id sconosciuto:
        insieme vuoto con un warning. POINT/AREA/ZONE: `(x, y, raggio efficace)` orizzontali, raggio =
        `radius_m` (POINT senza raggio: `TARGET_POINT_RADIUS_M`) + `uncertainty_m` se la provenienza e'
        ESTIMATED; nessun id. NONE: niente.
    """
    target = mission.target

    if target.kind is TargetKind.NONE:
        return frozenset(), None

    if target.kind in (TargetKind.POINT, TargetKind.AREA, TargetKind.ZONE):
        radius = target.radius_m if target.radius_m else \
            (TARGET_POINT_RADIUS_M if target.kind is TargetKind.POINT else 0.0)

        if target.provenance is TargetProvenance.ESTIMATED:
            radius += target.uncertainty_m

        return frozenset(), (float(target.position.x), float(target.position.y), float(radius))

    target_id = target.target_id

    if target.kind is TargetKind.GROUP and target_id in blocks:
        members = frozenset(asset_id for asset_id in (_domain_id(a) for a in
                                                      (getattr(blocks[target_id], 'assets', None) or {}).values())
                            if asset_id is not None)
    elif target.kind is TargetKind.GROUP and target_id in mission_of:
        members = frozenset(mission_of[target_id].asset_ids)
    elif target_id in assets:
        members = frozenset((target_id,))
    else:
        logger.warning(f"designated_targets: mission {mission.mission_id!r}: target {target_id!r} matches no "
                       f"asset, block or mission passed: it designates nothing")
        return frozenset(), None

    if target.asset_ids:
        unknown = sorted(set(target.asset_ids) - members)

        if unknown:
            logger.warning(f"designated_targets: mission {mission.mission_id!r}: asset_ids {unknown} are not "
                           f"in the target group {target_id!r}, ignored")

        members = members & frozenset(target.asset_ids)

    sides = _asset_sides(blocks)
    enemies = frozenset(asset_id for asset_id in members if sides.get(asset_id) != side)

    if members and not enemies:
        logger.info(f"designated_targets: mission {mission.mission_id!r}: the target {target_id!r} is not "
                    f"hostile (side {side!r}): it designates nothing")

    return enemies, None


def weapon_policies(missions: Iterable[Mission], assets: Mapping[str, object]) -> Dict[str, FC.WeaponPolicy]:
    """`{asset_id: WeaponPolicy}` degli asset delle missioni la cui politica d'armi ha vincoli (F7a, strato W).

    Solo le missioni aeree hanno una politica (`Context.mission_weapon_policy`; terra e mare None nella F7a).
    `self_escort` dell'asset viene dal suo loadout ASSEGNATO (`AIRCRAFT_LOADOUTS[modello][loadout]
    ['self_escort_capability']`), False se manca. Gli asset non passati in `assets` sono saltati.
    """
    policies: Dict[str, FC.WeaponPolicy] = {}

    for mission in missions:
        rules = mission_weapon_policy(mission.domain, mission.mission_type)

        if rules is None:
            continue

        for mission_asset in mission.assets:
            asset = assets.get(mission_asset.asset_id)

            if asset is None:
                continue

            loadout = (AIRCRAFT_LOADOUTS.get(getattr(asset, '_model', None), {})
                       .get(getattr(asset, 'assigned_loadout', None)) or {})
            policies[mission_asset.asset_id] = FC.WeaponPolicy(
                mission_id=mission.mission_id, domain=mission.domain, rules=rules,
                self_escort=bool(loadout.get('self_escort_capability', False)))

    return policies


def attack_point(mission: Mission, mission_asset: MissionAsset) -> Optional[Tuple[float, float, float]]:
    """Posizione `(x, y, z)` del punto ATTACK della missione sulla rotta DELL'ASSET (con l'offset di formazione),
    per la fine dell'attacco di `priority_designated` (F7a). Se la missione ha piu' punti ATTACK vale l'ultimo
    (l'attacco finisce dopo l'ultimo). None se la missione e' senza punto ATTACK o la rotta dell'asset non e'
    ricavabile: l'aereo resta allora in fase di avvicinamento (comportamento conservativo)."""
    indices = [index for index, waypoint in enumerate(mission.waypoints) if waypoint.role is WaypointRole.ATTACK]

    if not indices:
        return None

    try:
        route, _ = asset_route(mission, mission_asset)
        points = route_waypoints(route) if route is not None else ()
    except ValueError:
        return None

    if len(points) != len(mission.waypoints):
        return None

    return _xyz(points[indices[-1]].point)


def target_rules(missions: Iterable[Mission], blocks: Mapping[str, object], mission_of: Mapping[str, Mission],
                 assets: Mapping[str, object], side_of: Mapping[str, Optional[str]]
                 ) -> Dict[str, ER.TargetRules]:
    """`{asset_id: TargetRules}` per il risolutore (F7a, strato T).

    Crea una regola SOLO per gli asset la cui missione ha una ROE diversa da `weapon_free` OPPURE armi
    designate (`MissionAsset.designated_weapons`) non vuote: senza, nessuna voce e il risolutore e' identico a
    quello di prima. `side_of` e' `{block_id: lato}`; `air_self_defence` vale True se la politica d'armi della
    missione ha l'autodifesa (`self_defence`) per la classe aria.
    """
    rules: Dict[str, ER.TargetRules] = {}

    for mission in missions:
        roe = mission.rules.roe
        wanted = [mission_asset for mission_asset in mission.assets
                  if roe != ER.ROE_WEAPON_FREE or mission_asset.designated_weapons]

        if not wanted:
            continue

        ids, area = designated_targets(mission, blocks, mission_of, assets, side_of.get(mission.block_id))
        policy = mission_weapon_policy(mission.domain, mission.mission_type)
        self_defence = policy is not None and policy.get(TARGET_CLASS_AIR) == WEAPON_RULE_SELF_DEFENCE

        for mission_asset in wanted:
            rules[mission_asset.asset_id] = ER.TargetRules(
                roe=roe, designated_ids=ids, designated_area=area,
                designated_weapons=frozenset(mission_asset.designated_weapons), air_self_defence=self_defence,
                attack_point=attack_point(mission, mission_asset) if roe == ER.ROE_PRIORITY_DESIGNATED else None)

    return rules
