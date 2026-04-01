"""
 MODULE DA VEDERE SE MANTENERE O INSERIRE LE INFO IN INITAL_CONTEXT

methods for allocating military resources: aircraft, vehicle, ecc.

"""

from __future__ import annotations  # must be the very first statement

import copy
from typing import Dict, List, Optional, Tuple

from Code.Dynamic_War_Manager.Source.Context.Context import (
    AIR_TASK, 
    AIR_TO_AIR_TASK, 
    AIR_TO_GROUND_TASK, 
    Air_Asset_Type as at, 
    Ground_Vehicle_Asset_Type as ag,
    Sea_Asset_Type as asea
)
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Loadouts import (
    AIRCRAFT_LOADOUTS,
    get_aircrafts_quantity,
    loadout_cost,
)
from Code.Dynamic_War_Manager.Source.Asset.Aircraft_Data import Aircraft_Data
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger


logger = Logger(module_name=__name__, class_name='Initial_Context').logger


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

"""
DATA STRUCTURE

_ASSET_AVAILABILITY: Dict[str, Tuple[float, float]] = {   

        'air': {at.FIGHTER.value: {
                    'F-14A Tomcat': 100,
                    'F-14B Tomcat': 100,        
                },
                at.FIGHTER_BOMBER.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,                                
        }, 

        'ground': {
                ag.TANK.value: {
                    'F-14A Tomcat': 100,
                    'F-14B Tomcat': 100,
                    },
                ag.ARMORED.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,
                },
                
        },

        'sea': {asea.CARRIER.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,                    
                },
                asea.DESTROYER.value: {
                    'F-14A Tomcat': 100,
                    'F-14A Tomcat': 100,                    
                },                           
            },
}"""


PRODUCTION_ASSET:Dict[str, Tuple[float, float]] = {   
        'air':      {at.FIGHTER.value: 1,
                    at.FIGHTER_BOMBER.value: 1,
                    at.ATTACKER.value: 1,
                    at.BOMBER.value: 1,
                    at.HEAVY_BOMBER.value: 1,
                    at.RECON.value: 1,
                    at.AWACS.value: 1,
                    at.TRANSPORT.value: 1,
                    at.HELICOPTER.value: 1,},
        'ground':   {ag.TANK.value: 1,
                     ag.ARMORED.value: 1,
                     ag.MOTORIZED.value: 1,
                     ag.ARTILLERY_FIXED.value: 1,
                     ag.ARTILLERY_SEMOVENT.value: 1,
                     ag.SAM_BIG.value: 1,
                     ag.SAM_MEDIUM.value: 1,
                     ag.SAM_SMALL.value: 1,
                     ag.AAA.value: 1,
                     ag.EWR.value: 1,},
        'sea':      {asea.CARRIER.value: 1,
                     asea.DESTROYER.value: 1,
                     asea.CRUISER.value: 1,
                     asea.FRIGATE.value: 1,
                     asea.FAST_ATTACK.value: 1,
                     asea.SUBMARINE.value: 1,
                     asea.AMPHIBIOUS_ASSAULT_SHIP.value: 1,
                     asea.TRANSPORT.value: 1,
                     asea.CIVILIAN.value: 1,}
}





_ASSET_AVAILABILITY: Dict[str, Tuple[float, float]] = {

    """
    _ASSET_AVAILABILITY è un dizionario che mappa ogni categoria di asset (aria, terra, mare) a un sotto-dizionario che specifica i tipi di asset e i loro valori associati.

    Ecco un riepilogo dei valori assegnati e della logica utilizzata:

    Struttura per ogni asset:
    {'quantity': int, 'production': X/30, 'repair': {'heavy_damage': A/30,
    'medium_damage': B/30, 'light_damage': C/30}, 'local_industrial_capacity':
    0.75}

    Logica dei valori:

    ┌───────────────────────────┬─────────┬─────────────┬────────────────────┐
    │                           │ quantit │ production  │                    │
    │         Categoria         │    y    │ (unità/mese │ repair heavy→light │
    │                           │         │      )      │                    │
    ├───────────────────────────┼─────────┼─────────────┼────────────────────┤
    │ Caccia moderni (F-15,     │ 20–48   │ 2–4/30      │ 4→8→15/30          │
    │ MiG-29, Su-27)            │         │             │                    │
    ├───────────────────────────┼─────────┼─────────────┼────────────────────┤
    │ Caccia legacy (F-86,      │ 8–15    │ 0 (cessata) │ 6→12→22/30         │
    │ MiG-15)                   │         │             │                    │
    ├───────────────────────────┼─────────┼─────────────┼────────────────────┤
    │ Cacciabombardieri (F-16,  │ 20–48   │ 2–4/30      │ 5→10→20/30         │
    │ Su-30, Su-34)             │         │             │                    │
    ├───────────────────────────┼─────────┼─────────────┼────────────────────┤
    │ Attaccanti (A-10, Su-25)  │ 16–36   │ 1–4/30      │ 7→14→24/30         │
    │                           │         │             │ (robusti)          │
    ├───────────────────────────┼─────────┼─────────────┼────────────────────┤
    │ Bombardieri strategici    │ 4–10    │ 0–1/30      │ 0–1→2→3/30         │
    │ (B-52, Tu-160)            │         │             │ (lentissima)       │
    ├───────────────────────────┼─────────┼─────────────┼────────────────────┤
    │ UAV (MQ-1, MQ-9)          │ 15–20   │ 4–6/30      │ 6→12→22/30         │
    │                           │         │             │ (semplici)         │
    ├───────────────────────────┼─────────┼─────────────┼────────────────────┤
    │ Carri armati moderni      │ 60–100  │ 8–12/30     │ 4–6→10–14→22–28/30 │
    │ (T-90M, M1A2)             │         │             │                    │
    ├───────────────────────────┼─────────┼─────────────┼────────────────────┤
    │ MBT legacy (T-55,         │ 120–150 │ 10–12/30    │ 12→22→40/30        │
    │ Type-59)                  │         │             │ (semplici)         │
    ├───────────────────────────┼─────────┼─────────────┼────────────────────┤
    │ IFV/APC (BMP, BTR, M2     │ 80–150  │ 15–22/30    │ 9–16→20–28→38–50/3 │
    │ Bradley)                  │         │             │ 0                  │
    ├───────────────────────────┼─────────┼─────────────┼────────────────────┤
    │ Artiglieria (M109, 2S19,  │ 20–60   │ 3–10/30     │ 6–12→14–22→28–42/3 │
    │ BM-21)                    │         │             │ 0                  │
    ├───────────────────────────┼─────────┼─────────────┼────────────────────┤
    │ SAM grande/medio          │ 8–20    │ 1–3/30      │ 1–3→2–7→4–14/30    │
    │ (S-300PS, Buk)            │         │             │                    │
    ├───────────────────────────┼─────────┼─────────────┼────────────────────┤
    │ Portaerei                 │ 1       │ 0           │ 0→1→2/30 (arsenale │
    │                           │         │             │  remoto)           │
    ├───────────────────────────┼─────────┼─────────────┼────────────────────┤
    │ Cacciatorpediniere/Fregat │ 2–4     │ 0–1/30      │ 0→1→3–4/30         │
    │ e                         │         │             │                    │
    └───────────────────────────┴─────────┴─────────────┴────────────────────┘

    """


    # quantity  : unità disponibili all'inizio del conflitto per la coalizione
    # production: capacità produttiva massima [unità/mese] (0 = produzione cessata o irrilevante)
    # repair    : capacità di riparazione [unità/mese] per livello di danno (heavy→medium→light)
    #             es. heavy_damage=3/30 → in media 3 unità pesantemente danneggiate riparate al mese
    # local_industrial_capacity: frazione (0.0-1.0) di production e repair dipendente
    #             dalle infrastrutture industriali presenti nella zona di conflitto
    'air': {at.FIGHTER.value: {
                # ── Aerei da combattimento ─────────────────────────────────────────────
                # F-14A: produzione cessata (1991); parco ridotto, riparazione lenta per complessità
                'F-14A Tomcat':      {'quantity':  24, 'production': 1/60,  'repair': {'heavy_damage':  2/30, 'medium_damage':  4/30, 'light_damage':  8/30}, 'local_industrial_capacity': 0.75},
                # F-14B: versione motori F110, stesso parco Iran/US; produzione cessata
                'F-14B Tomcat':      {'quantity':  18, 'production': 0,     'repair': {'heavy_damage':  2/30, 'medium_damage':  4/30, 'light_damage':  8/30}, 'local_industrial_capacity': 0.75},
                # F-15C: caccia aria-aria principale USAF; ancora in servizio, produzione nuovi lotti ridotta
                'F-15C Eagle':       {'quantity':  48, 'production': 2/30,  'repair': {'heavy_damage':  4/30, 'medium_damage':  8/30, 'light_damage': 15/30}, 'local_industrial_capacity': 0.75},
                # F-5E: addestratore/caccia leggero; semplice, riparazione veloce
                'F-5E Tiger II':     {'quantity':  30, 'production': 1/30,  'repair': {'heavy_damage':  5/30, 'medium_damage': 10/30, 'light_damage': 20/30}, 'local_industrial_capacity': 0.75},
                # F-86E: obsoleto (Corea/Guerra Fredda); scorte limitate, produzione nulla
                'F-86E Sabre':       {'quantity':  10, 'production': 0,     'repair': {'heavy_damage':  6/30, 'medium_damage': 12/30, 'light_damage': 22/30}, 'local_industrial_capacity': 0.75},
                # Mirage 2000C: caccia francese; parco Francia/Grecia/India; produzione lenta
                'Mirage 2000C':      {'quantity':  30, 'production': 2/30,  'repair': {'heavy_damage':  4/30, 'medium_damage':  8/30, 'light_damage': 15/30}, 'local_industrial_capacity': 0.75},
                # MiG-15bis: velivolo storico; scarso valore operativo, parco molto ridotto
                'MiG-15bis':         {'quantity':   8, 'production': 0,     'repair': {'heavy_damage':  7/30, 'medium_damage': 14/30, 'light_damage': 25/30}, 'local_industrial_capacity': 0.75},
                # MiG-19P: caccia supersonico anni '50-'60; quasi fuori servizio
                'MiG-19P':           {'quantity':  12, 'production': 0,     'repair': {'heavy_damage':  6/30, 'medium_damage': 12/30, 'light_damage': 22/30}, 'local_industrial_capacity': 0.75},
                # MiG-21bis: diffusissimo; India/Siria/altri ancora in servizio; parti di ricambio disponibili
                'MiG-21bis':         {'quantity':  48, 'production': 1/30,  'repair': {'heavy_damage':  6/30, 'medium_damage': 12/30, 'light_damage': 22/30}, 'local_industrial_capacity': 0.75},
                # MiG-25PD: intercettore ad alta quota; parco russo limitato, produzione cessata
                'MiG-25PD':          {'quantity':  16, 'production': 0,     'repair': {'heavy_damage':  2/30, 'medium_damage':  5/30, 'light_damage': 10/30}, 'local_industrial_capacity': 0.75},
                # MiG-29A: caccia russo diffuso; export ampio; produzione attiva
                'MiG-29A':           {'quantity':  48, 'production': 4/30,  'repair': {'heavy_damage':  5/30, 'medium_damage': 10/30, 'light_damage': 18/30}, 'local_industrial_capacity': 0.75},
                # MiG-29S: versione aggiornata BVR; produzione limitata
                'MiG-29S':           {'quantity':  36, 'production': 3/30,  'repair': {'heavy_damage':  5/30, 'medium_damage': 10/30, 'light_damage': 18/30}, 'local_industrial_capacity': 0.75},
                # MiG-31: intercettore supersonico pesante; parco ridotto, costoso
                'MiG-31':            {'quantity':  20, 'production': 1/30,  'repair': {'heavy_damage':  2/30, 'medium_damage':  4/30, 'light_damage':  8/30}, 'local_industrial_capacity': 0.75},
                # Su-27: caccia pesante superiore; produzione attiva (Russia/Cina)
                'Su-27':             {'quantity':  36, 'production': 3/30,  'repair': {'heavy_damage':  4/30, 'medium_damage':  8/30, 'light_damage': 15/30}, 'local_industrial_capacity': 0.75},
            },
            at.FIGHTER_BOMBER.value: {
                # ── Cacciabombardieri ──────────────────────────────────────────────────
                # F-15E: polivalente pesante USAF; parco ampio, produzione ridotta
                'F-15E Strike Eagle':   {'quantity':  36, 'production': 2/30,  'repair': {'heavy_damage':  3/30, 'medium_damage':  6/30, 'light_damage': 12/30}, 'local_industrial_capacity': 0.75},
                # F/A-18A: versione navale iniziale; alcune in riserva
                'F/A-18A Hornet':        {'quantity':  30, 'production': 1/30,  'repair': {'heavy_damage':  4/30, 'medium_damage':  8/30, 'light_damage': 15/30}, 'local_industrial_capacity': 0.75},
                # F/A-18C: versione avanzata; ampio impiego US Navy/Marines
                'F/A-18C Hornet':        {'quantity':  36, 'production': 2/30,  'repair': {'heavy_damage':  4/30, 'medium_damage':  8/30, 'light_damage': 15/30}, 'local_industrial_capacity': 0.75},
                # F/A-18C Lot 20: lotto avanzato con JHMCS/AIM-9X
                'F/A-18C Lot 20':        {'quantity':  24, 'production': 2/30,  'repair': {'heavy_damage':  4/30, 'medium_damage':  8/30, 'light_damage': 15/30}, 'local_industrial_capacity': 0.75},
                # F-4E: produzione cessata (1981); export ampio, scorte residue
                'F-4E Phantom II':       {'quantity':  24, 'production': 0,     'repair': {'heavy_damage':  5/30, 'medium_damage': 10/30, 'light_damage': 18/30}, 'local_industrial_capacity': 0.75},
                # F-16A: monomotore economico; export massiccio, produzione attiva
                'F-16A Fighting Falcon': {'quantity':  48, 'production': 4/30,  'repair': {'heavy_damage':  6/30, 'medium_damage': 12/30, 'light_damage': 22/30}, 'local_industrial_capacity': 0.75},
                # F-16A MLU: Mid-Life Update; avionico potenziato
                'F-16A MLU':             {'quantity':  36, 'production': 3/30,  'repair': {'heavy_damage':  6/30, 'medium_damage': 12/30, 'light_damage': 22/30}, 'local_industrial_capacity': 0.75},
                # F-16C Blk52d: versione moderna con motore potenziato
                'F-16C Block 52d':       {'quantity':  36, 'production': 3/30,  'repair': {'heavy_damage':  5/30, 'medium_damage': 10/30, 'light_damage': 20/30}, 'local_industrial_capacity': 0.75},
                # F-16CM Blk50: versione HARM Targeting System
                'F-16CM Block 50':       {'quantity':  36, 'production': 3/30,  'repair': {'heavy_damage':  5/30, 'medium_damage': 10/30, 'light_damage': 20/30}, 'local_industrial_capacity': 0.75},
                # AJ/ASJ 37 Viggen: svedese, produzione cessata (1990); parco ridotto
                'AJ/ASJ 37 Viggen':      {'quantity':  20, 'production': 0,     'repair': {'heavy_damage':  3/30, 'medium_damage':  7/30, 'light_damage': 14/30}, 'local_industrial_capacity': 0.75},
                # MiG-23MLD: cacciabombardiere variabile; Russia/Siria/altri
                'MiG-23MLD':             {'quantity':  30, 'production': 1/30,  'repair': {'heavy_damage':  5/30, 'medium_damage': 10/30, 'light_damage': 18/30}, 'local_industrial_capacity': 0.75},
                # MiG-27K: attaccante terra russo; produzione cessata
                'MiG-27K':               {'quantity':  20, 'production': 0,     'repair': {'heavy_damage':  5/30, 'medium_damage': 10/30, 'light_damage': 18/30}, 'local_industrial_capacity': 0.75},
                # Su-17M4: attaccante supersonico russo; produzione cessata
                'Su-17M4':               {'quantity':  24, 'production': 0,     'repair': {'heavy_damage':  5/30, 'medium_damage': 10/30, 'light_damage': 18/30}, 'local_industrial_capacity': 0.75},
                # Su-30: bimotore polivalente; export ampio (India/Algeria/Malesia), produzione attiva
                'Su-30':                 {'quantity':  24, 'production': 3/30,  'repair': {'heavy_damage':  3/30, 'medium_damage':  7/30, 'light_damage': 14/30}, 'local_industrial_capacity': 0.75},
                # Su-33: versione navale Su-27 per Kuznetsov; parco ristretto
                'Su-33':                 {'quantity':  20, 'production': 1/30,  'repair': {'heavy_damage':  2/30, 'medium_damage':  5/30, 'light_damage': 10/30}, 'local_industrial_capacity': 0.75},
                # Su-34: bombardiere tattico moderno; produzione attiva (Russia)
                'Su-34':                 {'quantity':  20, 'production': 3/30,  'repair': {'heavy_damage':  2/30, 'medium_damage':  5/30, 'light_damage': 10/30}, 'local_industrial_capacity': 0.75},
            },
            at.ATTACKER.value: {
                # ── Aerei d'attacco al suolo ───────────────────────────────────────────
                # A-10A: corazzato, robusto; alta sopravvivenza → riparazione più rapida
                'A-10A Thunderbolt II':    {'quantity':  36, 'production': 1/30,  'repair': {'heavy_damage':  7/30, 'medium_damage': 14/30, 'light_damage': 24/30}, 'local_industrial_capacity': 0.75},
                # A-10C: versione avionics upgrade; stessa robustezza strutturale
                'A-10C Thunderbolt II':    {'quantity':  36, 'production': 1/30,  'repair': {'heavy_damage':  7/30, 'medium_damage': 14/30, 'light_damage': 24/30}, 'local_industrial_capacity': 0.75},
                # A-10C II: LITENING/Sniper pod; parco più limitato
                'A-10C II Thunderbolt II': {'quantity':  24, 'production': 1/30,  'repair': {'heavy_damage':  7/30, 'medium_damage': 14/30, 'light_damage': 24/30}, 'local_industrial_capacity': 0.75},
                # A-20G: WWII; valore puramente simbolico/storico
                'A-20G Havoc':             {'quantity':   6, 'production': 0,     'repair': {'heavy_damage':  7/30, 'medium_damage': 14/30, 'light_damage': 24/30}, 'local_industrial_capacity': 0.75},
                # A-4E: attaccante navale Vietnam-era; produzione cessata
                'A-4E Skyhawk':            {'quantity':  18, 'production': 0,     'repair': {'heavy_damage':  6/30, 'medium_damage': 12/30, 'light_damage': 22/30}, 'local_industrial_capacity': 0.75},
                # Su-25: attaccante blindato russo; molto diffuso, parti disponibili
                'Su-25':                   {'quantity':  36, 'production': 4/30,  'repair': {'heavy_damage':  8/30, 'medium_damage': 16/30, 'light_damage': 26/30}, 'local_industrial_capacity': 0.75},
                # Su-25T: versione antitank avanzata; sensori migliorati
                'Su-25T':                  {'quantity':  24, 'production': 3/30,  'repair': {'heavy_damage':  7/30, 'medium_damage': 14/30, 'light_damage': 24/30}, 'local_industrial_capacity': 0.75},
                # Su-25TM (Su-39): versione multimissione avanzata; parco molto ridotto
                'Su-25TM':                 {'quantity':  16, 'production': 2/30,  'repair': {'heavy_damage':  6/30, 'medium_damage': 12/30, 'light_damage': 22/30}, 'local_industrial_capacity': 0.75},
            },
            at.BOMBER.value: {
                # ── Bombardieri tattici ────────────────────────────────────────────────
                # F-117: stealth; produzione cessata (1990), ritirato 2008 → scorte storiche
                'F-117 Nighthawk': {'quantity':  10, 'production': 0,     'repair': {'heavy_damage':  1/30, 'medium_damage':  2/30, 'light_damage':  4/30}, 'local_industrial_capacity': 0.75},
                # S-3B Viking: pattugliatore navale/tanker; fuori produzione
                'S-3B Viking':     {'quantity':  16, 'production': 0,     'repair': {'heavy_damage':  3/30, 'medium_damage':  6/30, 'light_damage': 12/30}, 'local_industrial_capacity': 0.75},
                # Su-24M: bombardiere tattico russo; ancora in servizio, produzione lenta
                'Su-24M':          {'quantity':  24, 'production': 2/30,  'repair': {'heavy_damage':  3/30, 'medium_damage':  7/30, 'light_damage': 14/30}, 'local_industrial_capacity': 0.75},
                # Tu-142: pattugliatore marittimo/ASW; parco ridotto russo
                'Tu-142':          {'quantity':   8, 'production': 1/30,  'repair': {'heavy_damage':  1/30, 'medium_damage':  2/30, 'light_damage':  4/30}, 'local_industrial_capacity': 0.75},
            },
            at.HEAVY_BOMBER.value: {
                # ── Bombardieri strategici ────────────────────────────────────────────
                # B-1B: supersonico strategico; produzione cessata (1988); manutenzione costosa
                'B-1B Lancer':          {'quantity':   8, 'production': 0,     'repair': {'heavy_damage':  1/30, 'medium_damage':  2/30, 'light_damage':  3/30}, 'local_industrial_capacity': 0.75},
                # B-52H: bombardiere storico; ancora in servizio USAF; produzione cessata
                'B-52H Stratofortress': {'quantity':   6, 'production': 0,     'repair': {'heavy_damage':  1/30, 'medium_damage':  2/30, 'light_damage':  3/30}, 'local_industrial_capacity': 0.75},
                # Tu-22M: bombardiere supersonico russo a geometria variabile; produzione ripresa lentamente
                'Tu-22M':               {'quantity':  10, 'production': 1/30,  'repair': {'heavy_damage':  1/30, 'medium_damage':  2/30, 'light_damage':  4/30}, 'local_industrial_capacity': 0.75},
                # Tu-95MS: bombardiere a elica turbo; ancora operativo con missili cruise
                'Tu-95MS':              {'quantity':   6, 'production': 1/30,  'repair': {'heavy_damage':  1/30, 'medium_damage':  2/30, 'light_damage':  3/30}, 'local_industrial_capacity': 0.75},
                # Tu-160: supersonico strategico; parco molto ridotto, produzione lentissima
                'Tu-160':               {'quantity':   4, 'production': 1/30,  'repair': {'heavy_damage':  0,    'medium_damage':  1/30, 'light_damage':  2/30}, 'local_industrial_capacity': 0.75},
            },
            at.RECON.value: {
                # ── Ricognizione / UAV ────────────────────────────────────────────────
                # MQ-1 Predator: MALE UAV; produzione attiva, costo contenuto
                'MQ-1 Predator': {'quantity':  20, 'production': 6/30,  'repair': {'heavy_damage':  8/30, 'medium_damage': 16/30, 'light_damage': 26/30}, 'local_industrial_capacity': 0.75},
                # MQ-9 Reaper: MALE UAV avanzato; più costoso del Predator
                'MQ-9 Reaper':   {'quantity':  15, 'production': 4/30,  'repair': {'heavy_damage':  6/30, 'medium_damage': 12/30, 'light_damage': 22/30}, 'local_industrial_capacity': 0.75},
                # MiG-25RB: ricognitore supersonico; versione specializzata
                'MiG-25RB':      {'quantity':  12, 'production': 0,     'repair': {'heavy_damage':  2/30, 'medium_damage':  4/30, 'light_damage':  8/30}, 'local_industrial_capacity': 0.75},
                # Su-24MR: versione ricognizione Su-24; pod ELINT/SLAR
                'Su-24MR':       {'quantity':  15, 'production': 2/30,  'repair': {'heavy_damage':  3/30, 'medium_damage':  6/30, 'light_damage': 12/30}, 'local_industrial_capacity': 0.75},
            },
            at.AWACS.value: {
                # ── AWACS / C2 aereo ──────────────────────────────────────────────────
                # E-2D: AWACS imbarcato US Navy; parco ridotto, costoso
                'E-2D Advanced Hawkeye': {'quantity':   8, 'production': 1/30,  'repair': {'heavy_damage':  2/30, 'medium_damage':  3/30, 'light_damage':  6/30}, 'local_industrial_capacity': 0.75},
                # E-3A: AWACS basato Boeing 707; produzione cessata
                'E-3A Sentry':           {'quantity':   6, 'production': 0,     'repair': {'heavy_damage':  1/30, 'medium_damage':  2/30, 'light_damage':  4/30}, 'local_industrial_capacity': 0.75},
                # A-50: AWACS russo basato Il-76; parco molto ridotto
                'A-50':                  {'quantity':   6, 'production': 1/30,  'repair': {'heavy_damage':  1/30, 'medium_damage':  2/30, 'light_damage':  4/30}, 'local_industrial_capacity': 0.75},
            },
            at.TRANSPORT.value: {
                # ── Trasporti / Tanker ────────────────────────────────────────────────
                # S-3B Viking Tanker: tanker imbarcato; fuori produzione
                'S-3B Viking Tanker':    {'quantity':  12, 'production': 0,     'repair': {'heavy_damage':  3/30, 'medium_damage':  6/30, 'light_damage': 12/30}, 'local_industrial_capacity': 0.75},
                # C-130 Hercules: trasporto tattico; ampiamente diffuso, ancora in produzione
                'C-130 Hercules':        {'quantity':  20, 'production': 4/30,  'repair': {'heavy_damage':  6/30, 'medium_damage': 12/30, 'light_damage': 22/30}, 'local_industrial_capacity': 0.75},
                # C-17A: trasporto strategico; costoso, parco limitato
                'C-17A Globemaster III': {'quantity':   8, 'production': 1/30,  'repair': {'heavy_damage':  2/30, 'medium_damage':  4/30, 'light_damage':  8/30}, 'local_industrial_capacity': 0.75},
                # KC-130: tanker/trasporto Marines
                'KC-130':                {'quantity':  10, 'production': 2/30,  'repair': {'heavy_damage':  5/30, 'medium_damage': 10/30, 'light_damage': 20/30}, 'local_industrial_capacity': 0.75},
                # KC-135: tanker storico USAF; produzione cessata
                'KC-135 Stratotanker':   {'quantity':  10, 'production': 0,     'repair': {'heavy_damage':  2/30, 'medium_damage':  5/30, 'light_damage': 10/30}, 'local_industrial_capacity': 0.75},
                # KC-135 MPRS: versione con Multi-Point Refueling System
                'KC-135 MPRS':           {'quantity':   8, 'production': 0,     'repair': {'heavy_damage':  2/30, 'medium_damage':  5/30, 'light_damage': 10/30}, 'local_industrial_capacity': 0.75},
                # An-26B: trasporto tattico leggero russo; diffuso
                'An-26B':                {'quantity':  20, 'production': 3/30,  'repair': {'heavy_damage':  7/30, 'medium_damage': 14/30, 'light_damage': 24/30}, 'local_industrial_capacity': 0.75},
                # An-30M: ricognizione/rilievo fotografico; parco ridotto
                'An-30M':                {'quantity':   8, 'production': 1/30,  'repair': {'heavy_damage':  5/30, 'medium_damage': 10/30, 'light_damage': 18/30}, 'local_industrial_capacity': 0.75},
                # Il-76MD: trasporto pesante russo; ancora in produzione
                'Il-76MD':               {'quantity':  12, 'production': 2/30,  'repair': {'heavy_damage':  3/30, 'medium_damage':  6/30, 'light_damage': 12/30}, 'local_industrial_capacity': 0.75},
                # Il-78M: tanker pesante russo basato Il-76
                'Il-78M':                {'quantity':   8, 'production': 1/30,  'repair': {'heavy_damage':  2/30, 'medium_damage':  5/30, 'light_damage': 10/30}, 'local_industrial_capacity': 0.75},
                # Yak-40: trasporto regionale/liaison; semplice, riparazione rapida
                'Yak-40':                {'quantity':  10, 'production': 2/30,  'repair': {'heavy_damage':  7/30, 'medium_damage': 14/30, 'light_damage': 24/30}, 'local_industrial_capacity': 0.75},
            },
            at.HELICOPTER.value: {
            },
    },
    'ground': {
            ag.TANK.value: {
                # ── Carri armati ──────────────────────────────────────────────────────
                # Valori di produzione in unità/mese; riparazione più rapida rispetto agli aerei
                # T-90M: MBT russo moderno; produzione attiva
                'T-90M':         {'quantity':  80, 'production': 10/30, 'repair': {'heavy_damage':  5/30, 'medium_damage': 12/30, 'light_damage': 25/30}, 'local_industrial_capacity': 0.75},
                # T-90: MBT russo base; diffuso, parco ampio
                'T-90':          {'quantity': 100, 'production': 12/30, 'repair': {'heavy_damage':  6/30, 'medium_damage': 14/30, 'light_damage': 28/30}, 'local_industrial_capacity': 0.75},
                # T-80U: turbina a gas; costoso ma veloce; parco ridotto rispetto T-72
                'T-80U':         {'quantity':  80, 'production':  8/30, 'repair': {'heavy_damage':  4/30, 'medium_damage': 10/30, 'light_damage': 22/30}, 'local_industrial_capacity': 0.75},
                # T-72B: MBT più diffuso al mondo; produzione massiccia storica
                'T-72B':         {'quantity': 120, 'production': 15/30, 'repair': {'heavy_damage':  8/30, 'medium_damage': 18/30, 'light_damage': 35/30}, 'local_industrial_capacity': 0.75},
                # T-72B3: versione modernizzata con FCS avanzato
                'T-72B3':        {'quantity': 100, 'production': 12/30, 'repair': {'heavy_damage':  7/30, 'medium_damage': 16/30, 'light_damage': 32/30}, 'local_industrial_capacity': 0.75},
                # T-55: MBT Cold War; molto diffuso, semplice → alta riparabilità
                'T-55':          {'quantity': 150, 'production': 10/30, 'repair': {'heavy_damage': 12/30, 'medium_damage': 22/30, 'light_damage': 40/30}, 'local_industrial_capacity': 0.75},
                # M1A2 Abrams: MBT US di ultima generazione; costoso, parco limitato al teatro
                'M1A2-Abrams':   {'quantity':  80, 'production':  8/30, 'repair': {'heavy_damage':  4/30, 'medium_damage': 10/30, 'light_damage': 22/30}, 'local_industrial_capacity': 0.75},
                # M60A3 Patton: MBT Cold War US; ancora in uso presso alleati
                'M60A3-Patton':  {'quantity':  60, 'production':  5/30, 'repair': {'heavy_damage':  8/30, 'medium_damage': 18/30, 'light_damage': 35/30}, 'local_industrial_capacity': 0.75},
                # Leopard 2A6M: versione con protezione mina migliorata; produzione attiva
                'Leopard-2A6M':  {'quantity':  60, 'production':  6/30, 'repair': {'heavy_damage':  4/30, 'medium_damage': 10/30, 'light_damage': 22/30}, 'local_industrial_capacity': 0.75},
                # Leopard 2A5: armatura a cuneo; molto diffuso in NATO
                'Leopard-2A5':   {'quantity':  80, 'production':  8/30, 'repair': {'heavy_damage':  5/30, 'medium_damage': 12/30, 'light_damage': 25/30}, 'local_industrial_capacity': 0.75},
                # Leopard 2A4: versione base più diffusa
                'Leopard-2A4':   {'quantity':  90, 'production':  8/30, 'repair': {'heavy_damage':  6/30, 'medium_damage': 14/30, 'light_damage': 28/30}, 'local_industrial_capacity': 0.75},
                # Leopard 1A3: vecchia generazione; più semplice, riparazione rapida
                'Leopard-1A3':   {'quantity':  60, 'production':  4/30, 'repair': {'heavy_damage':  8/30, 'medium_damage': 18/30, 'light_damage': 35/30}, 'local_industrial_capacity': 0.75},
                # Chieftain MK3: britannico; produzione cessata, parco residuo
                'Chieftain-MK3': {'quantity':  40, 'production':  2/30, 'repair': {'heavy_damage':  6/30, 'medium_damage': 14/30, 'light_damage': 28/30}, 'local_industrial_capacity': 0.75},
                # Challenger II: MBT britannico moderno; armatura Chobham avanzata
                'Challenger-II': {'quantity':  60, 'production':  5/30, 'repair': {'heavy_damage':  4/30, 'medium_damage': 10/30, 'light_damage': 22/30}, 'local_industrial_capacity': 0.75},
                # Leclerc: MBT francese; caricatore automatico; produzione limitata
                'Leclerc':       {'quantity':  60, 'production':  4/30, 'repair': {'heavy_damage':  4/30, 'medium_damage': 10/30, 'light_damage': 22/30}, 'local_industrial_capacity': 0.75},
                # Merkava IV: israeliano; protezione attiva Trophy; produzione attiva
                'Merkava-IV':    {'quantity':  80, 'production':  8/30, 'repair': {'heavy_damage':  5/30, 'medium_damage': 12/30, 'light_damage': 25/30}, 'local_industrial_capacity': 0.75},
                # Type-59: MBT cinese derivato T-54; molto diffuso; semplice
                'Type-59':       {'quantity': 150, 'production': 12/30, 'repair': {'heavy_damage': 12/30, 'medium_damage': 22/30, 'light_damage': 40/30}, 'local_industrial_capacity': 0.75},
                # ZTZ-96B: MBT cinese moderno; produzione attiva
                'ZTZ-96B':       {'quantity':  80, 'production':  8/30, 'repair': {'heavy_damage':  5/30, 'medium_damage': 12/30, 'light_damage': 25/30}, 'local_industrial_capacity': 0.75},
            },
            ag.ARMORED.value: {
                # ── IFV / APC / veicoli corazzati ────────────────────────────────────
                # Più semplici dei carri; produzione e riparazione più rapide
                'BMP-1':           {'quantity': 150, 'production': 20/30, 'repair': {'heavy_damage': 12/30, 'medium_damage': 24/30, 'light_damage': 45/30}, 'local_industrial_capacity': 0.75},
                'BMP-2':           {'quantity': 150, 'production': 22/30, 'repair': {'heavy_damage': 12/30, 'medium_damage': 24/30, 'light_damage': 45/30}, 'local_industrial_capacity': 0.75},
                'BMP-3':           {'quantity': 100, 'production': 15/30, 'repair': {'heavy_damage':  9/30, 'medium_damage': 20/30, 'light_damage': 38/30}, 'local_industrial_capacity': 0.75},
                'BMD-1':           {'quantity':  80, 'production': 15/30, 'repair': {'heavy_damage': 12/30, 'medium_damage': 24/30, 'light_damage': 45/30}, 'local_industrial_capacity': 0.75},
                'BTR-80':          {'quantity': 120, 'production': 20/30, 'repair': {'heavy_damage': 14/30, 'medium_damage': 26/30, 'light_damage': 48/30}, 'local_industrial_capacity': 0.75},
                'BTR-82A':         {'quantity': 100, 'production': 18/30, 'repair': {'heavy_damage': 14/30, 'medium_damage': 26/30, 'light_damage': 48/30}, 'local_industrial_capacity': 0.75},
                'BTR-RD':          {'quantity':  80, 'production': 15/30, 'repair': {'heavy_damage': 14/30, 'medium_damage': 26/30, 'light_damage': 48/30}, 'local_industrial_capacity': 0.75},
                'MT-LB':           {'quantity': 120, 'production': 20/30, 'repair': {'heavy_damage': 16/30, 'medium_damage': 28/30, 'light_damage': 50/30}, 'local_industrial_capacity': 0.75},
                'M2-Bradley':      {'quantity': 100, 'production': 15/30, 'repair': {'heavy_damage':  9/30, 'medium_damage': 20/30, 'light_damage': 38/30}, 'local_industrial_capacity': 0.75},
                # M2A1 Halftrack: WWII; semplice, riparazione velocissima
                'M2A1-Halftrack':  {'quantity':  30, 'production':  3/30, 'repair': {'heavy_damage': 18/30, 'medium_damage': 30/30, 'light_damage': 55/30}, 'local_industrial_capacity': 0.75},
                'M-113':           {'quantity': 120, 'production': 15/30, 'repair': {'heavy_damage': 14/30, 'medium_damage': 26/30, 'light_damage': 48/30}, 'local_industrial_capacity': 0.75},
                'M1126-Stryker-ICV':{'quantity': 80, 'production': 12/30, 'repair': {'heavy_damage': 11/30, 'medium_damage': 22/30, 'light_damage': 42/30}, 'local_industrial_capacity': 0.75},
                'Marder':          {'quantity':  80, 'production': 10/30, 'repair': {'heavy_damage':  9/30, 'medium_damage': 20/30, 'light_damage': 38/30}, 'local_industrial_capacity': 0.75},
                'Warrior':         {'quantity':  70, 'production':  8/30, 'repair': {'heavy_damage':  9/30, 'medium_damage': 20/30, 'light_damage': 38/30}, 'local_industrial_capacity': 0.75},
                'LAV-25':          {'quantity':  80, 'production': 12/30, 'repair': {'heavy_damage': 14/30, 'medium_damage': 26/30, 'light_damage': 48/30}, 'local_industrial_capacity': 0.75},
                'AAV7':            {'quantity':  60, 'production':  8/30, 'repair': {'heavy_damage':  9/30, 'medium_damage': 20/30, 'light_damage': 38/30}, 'local_industrial_capacity': 0.75},
                'TPz-Fuchs':       {'quantity':  60, 'production':  8/30, 'repair': {'heavy_damage': 14/30, 'medium_damage': 26/30, 'light_damage': 48/30}, 'local_industrial_capacity': 0.75},
                'ZBD-04A':         {'quantity':  80, 'production': 12/30, 'repair': {'heavy_damage':  9/30, 'medium_damage': 20/30, 'light_damage': 38/30}, 'local_industrial_capacity': 0.75},
                # Sd.Kfz-251: WWII; valore storico, riparazione semplice
                'Sd.Kfz-251':      {'quantity':  20, 'production':  2/30, 'repair': {'heavy_damage': 18/30, 'medium_damage': 30/30, 'light_damage': 55/30}, 'local_industrial_capacity': 0.75},
            },
            ag.MOTORIZED.value: {
            },
            ag.ARTILLERY_FIXED.value: {
            },
            ag.ARTILLERY_SEMOVENT.value: {
                # ── Artiglieria semovente / lanciarazzi ───────────────────────────────
                # 2S1 Gvozdika: obice 122mm su cingolato; semplice, ampiamente diffuso
                '2S1-Gvozdika':  {'quantity':  60, 'production':  8/30, 'repair': {'heavy_damage':  8/30, 'medium_damage': 18/30, 'light_damage': 35/30}, 'local_industrial_capacity': 0.75},
                # 2S3 Akatsia: obice 152mm; peso maggiore → riparazione leggermente più lenta
                '2S3-Akatsia':   {'quantity':  50, 'production':  6/30, 'repair': {'heavy_damage':  7/30, 'medium_damage': 16/30, 'light_damage': 30/30}, 'local_industrial_capacity': 0.75},
                # 2S9 Nona: mortaio/obice anfibio leggero
                '2S9-Nona':      {'quantity':  40, 'production':  6/30, 'repair': {'heavy_damage':  9/30, 'medium_damage': 20/30, 'light_damage': 38/30}, 'local_industrial_capacity': 0.75},
                # 2S19 Msta-S: obice 152mm moderno; automatizzato
                '2S19-Msta':     {'quantity':  40, 'production':  5/30, 'repair': {'heavy_damage':  6/30, 'medium_damage': 14/30, 'light_damage': 28/30}, 'local_industrial_capacity': 0.75},
                # BM-21 Grad: lanciarazzi 122mm; molto diffuso; riparazione semplice
                'BM-21-Grad':    {'quantity':  50, 'production': 10/30, 'repair': {'heavy_damage': 12/30, 'medium_damage': 22/30, 'light_damage': 42/30}, 'local_industrial_capacity': 0.75},
                # BM-27 Uragan: lanciarazzi 220mm; medio-pesante
                'BM-27-Uragan':  {'quantity':  30, 'production':  5/30, 'repair': {'heavy_damage':  8/30, 'medium_damage': 16/30, 'light_damage': 30/30}, 'local_industrial_capacity': 0.75},
                # 9A52 Smerch: lanciarazzi 300mm pesante; alta precisione
                '9A52-Smerch':   {'quantity':  20, 'production':  3/30, 'repair': {'heavy_damage':  5/30, 'medium_damage': 12/30, 'light_damage': 24/30}, 'local_industrial_capacity': 0.75},
                # Dana vz.77: obice cecoslovacco su ruote; diffuso in Europa orientale
                'Dana-vz77':     {'quantity':  30, 'production':  4/30, 'repair': {'heavy_damage':  7/30, 'medium_damage': 16/30, 'light_damage': 30/30}, 'local_industrial_capacity': 0.75},
                # M109 Paladin: obice 155mm US; standard NATO
                'M109-Paladin':  {'quantity':  40, 'production':  5/30, 'repair': {'heavy_damage':  6/30, 'medium_damage': 14/30, 'light_damage': 28/30}, 'local_industrial_capacity': 0.75},
                # M270 MLRS: lanciarazzi NATO 227mm; elevata precisione con GMLRS
                'M270-MLRS':     {'quantity':  30, 'production':  4/30, 'repair': {'heavy_damage':  6/30, 'medium_damage': 14/30, 'light_damage': 28/30}, 'local_industrial_capacity': 0.75},
                # PLZ-05: obice cinese 155mm; produzione attiva
                'PLZ-05':        {'quantity':  40, 'production':  6/30, 'repair': {'heavy_damage':  6/30, 'medium_damage': 14/30, 'light_damage': 28/30}, 'local_industrial_capacity': 0.75},
                # T155 Firtina: obice turco 155mm derivato K9
                'T155-Firtina':  {'quantity':  30, 'production':  4/30, 'repair': {'heavy_damage':  6/30, 'medium_damage': 14/30, 'light_damage': 28/30}, 'local_industrial_capacity': 0.75},
            },
            ag.SAM_BIG.value: {
                # ── SAM a lungo raggio ────────────────────────────────────────────────
                # S-300PS: sistema complesso, riparazione lenta; parco limitato per teatro
                'S-300PS': {'quantity':   8, 'production': 1/30, 'repair': {'heavy_damage':  1/30, 'medium_damage':  3/30, 'light_damage':  6/30}, 'local_industrial_capacity': 0.75},
            },
            ag.SAM_MEDIUM.value: {
                # ── SAM a medio raggio ────────────────────────────────────────────────
                # 2K12 Kub (SA-6): semovente cingolato; diffuso
                '2K12-Kub':  {'quantity':  20, 'production': 3/30, 'repair': {'heavy_damage':  3/30, 'medium_damage':  7/30, 'light_damage': 14/30}, 'local_industrial_capacity': 0.75},
                # 9K37 Buk (SA-11/17): più moderno e flessibile
                '9K37-Buk':  {'quantity':  20, 'production': 3/30, 'repair': {'heavy_damage':  3/30, 'medium_damage':  7/30, 'light_damage': 14/30}, 'local_industrial_capacity': 0.75},
            },
            ag.SAM_SMALL.value: {
                # ── SAM a corto raggio / MANPADS ─────────────────────────────────────
                # Sistemi più semplici → produzione e riparazione più rapide
                'Strela-1-9P31':    {'quantity':  30, 'production': 5/30, 'repair': {'heavy_damage':  6/30, 'medium_damage': 12/30, 'light_damage': 24/30}, 'local_industrial_capacity': 0.75},
                '9A33-Osa':         {'quantity':  25, 'production': 4/30, 'repair': {'heavy_damage':  5/30, 'medium_damage': 10/30, 'light_damage': 20/30}, 'local_industrial_capacity': 0.75},
                '9K35-Strela-10':   {'quantity':  30, 'production': 5/30, 'repair': {'heavy_damage':  6/30, 'medium_damage': 12/30, 'light_damage': 24/30}, 'local_industrial_capacity': 0.75},
                '9K331-Tor':        {'quantity':  20, 'production': 3/30, 'repair': {'heavy_damage':  3/30, 'medium_damage':  8/30, 'light_damage': 16/30}, 'local_industrial_capacity': 0.75},
                '2K22-Tunguska':    {'quantity':  20, 'production': 3/30, 'repair': {'heavy_damage':  3/30, 'medium_damage':  8/30, 'light_damage': 16/30}, 'local_industrial_capacity': 0.75},
                'MIM-72G-Chaparral':{'quantity':  20, 'production': 2/30, 'repair': {'heavy_damage':  5/30, 'medium_damage': 10/30, 'light_damage': 20/30}, 'local_industrial_capacity': 0.75},
                'MIM-115-Roland':   {'quantity':  15, 'production': 2/30, 'repair': {'heavy_damage':  3/30, 'medium_damage':  7/30, 'light_damage': 14/30}, 'local_industrial_capacity': 0.75},
                'M6-Linebacker':    {'quantity':  20, 'production': 3/30, 'repair': {'heavy_damage':  5/30, 'medium_damage': 10/30, 'light_damage': 20/30}, 'local_industrial_capacity': 0.75},
            },
            ag.AAA.value: {
                # ── Antiaerea (cannoni) ───────────────────────────────────────────────
                # Sistemi relativamente semplici; riparazione rapida
                'ZSU-57-2':          {'quantity':  30, 'production': 4/30, 'repair': {'heavy_damage':  7/30, 'medium_damage': 14/30, 'light_damage': 26/30}, 'local_industrial_capacity': 0.75},
                'ZSU-23-4-Shilka':   {'quantity':  40, 'production': 5/30, 'repair': {'heavy_damage':  8/30, 'medium_damage': 16/30, 'light_damage': 28/30}, 'local_industrial_capacity': 0.75},
                'M163-VADS':         {'quantity':  30, 'production': 4/30, 'repair': {'heavy_damage':  8/30, 'medium_damage': 16/30, 'light_damage': 28/30}, 'local_industrial_capacity': 0.75},
                'Flakpanzer-Gepard': {'quantity':  30, 'production': 3/30, 'repair': {'heavy_damage':  6/30, 'medium_damage': 12/30, 'light_damage': 24/30}, 'local_industrial_capacity': 0.75},
            },
            ag.EWR.value: {
            },
    },
    'sea': {asea.CARRIER.value: {
                # ── Portaerei ─────────────────────────────────────────────────────────
                # Costruzione: 5-10 anni → production ≈ 0 nel contesto di un conflitto regionale
                # Danno pesante: irrecuperabile nel breve periodo (dry-dock lontano dal teatro)
                'CVN-70 Carl Vinson':          {'quantity': 1, 'production': 0, 'repair': {'heavy_damage': 0,    'medium_damage': 1/30, 'light_damage': 2/30}, 'local_industrial_capacity': 0.75},
                'CVN-71 Theodore Roosevelt':   {'quantity': 1, 'production': 0, 'repair': {'heavy_damage': 0,    'medium_damage': 1/30, 'light_damage': 2/30}, 'local_industrial_capacity': 0.75},
                'CVN-72 Abraham Lincoln':      {'quantity': 1, 'production': 0, 'repair': {'heavy_damage': 0,    'medium_damage': 1/30, 'light_damage': 2/30}, 'local_industrial_capacity': 0.75},
                'CVN-73 George Washington':    {'quantity': 1, 'production': 0, 'repair': {'heavy_damage': 0,    'medium_damage': 1/30, 'light_damage': 2/30}, 'local_industrial_capacity': 0.75},
                'CVN-74 John C. Stennis':      {'quantity': 1, 'production': 0, 'repair': {'heavy_damage': 0,    'medium_damage': 1/30, 'light_damage': 2/30}, 'local_industrial_capacity': 0.75},
                'CVN-75 Harry S. Truman':      {'quantity': 1, 'production': 0, 'repair': {'heavy_damage': 0,    'medium_damage': 1/30, 'light_damage': 2/30}, 'local_industrial_capacity': 0.75},
                'CV-59 USS Forrestal':         {'quantity': 1, 'production': 0, 'repair': {'heavy_damage': 0,    'medium_damage': 1/30, 'light_damage': 2/30}, 'local_industrial_capacity': 0.75},
                'CV 1143.5 Admiral Kuznetsov': {'quantity': 1, 'production': 0, 'repair': {'heavy_damage': 0,    'medium_damage': 1/30, 'light_damage': 2/30}, 'local_industrial_capacity': 0.75},
            },
            asea.DESTROYER.value: {
                # ── Cacciatorpediniere ────────────────────────────────────────────────
                # Costruzione: 3-5 anni; riparazioni pesanti richiedono arsenale
                'USS Arleigh Burke IIa':    {'quantity': 4, 'production': 0,    'repair': {'heavy_damage': 0,    'medium_damage': 1/30, 'light_damage': 3/30}, 'local_industrial_capacity': 0.75},
                'Type 052B Guangzhou-class': {'quantity': 3, 'production': 1/30, 'repair': {'heavy_damage': 0,    'medium_damage': 1/30, 'light_damage': 3/30}, 'local_industrial_capacity': 0.75},
                'Type 052C':                {'quantity': 3, 'production': 1/30, 'repair': {'heavy_damage': 0,    'medium_damage': 1/30, 'light_damage': 3/30}, 'local_industrial_capacity': 0.75},
            },
            asea.CRUISER.value: {
                # ── Incrociatori ──────────────────────────────────────────────────────
                # Classi uniche; produzione nulla nel breve termine
                'CG-65':                  {'quantity': 2, 'production': 0, 'repair': {'heavy_damage': 0, 'medium_damage': 1/30, 'light_damage': 2/30}, 'local_industrial_capacity': 0.75},
                'CGN 1144.2 Piotr Velikiy':{'quantity': 1, 'production': 0, 'repair': {'heavy_damage': 0, 'medium_damage': 1/30, 'light_damage': 2/30}, 'local_industrial_capacity': 0.75},
                'CG 1164 Moskva':          {'quantity': 1, 'production': 0, 'repair': {'heavy_damage': 0, 'medium_damage': 1/30, 'light_damage': 2/30}, 'local_industrial_capacity': 0.75},
            },
            asea.FRIGATE.value: {
                # ── Fregate ───────────────────────────────────────────────────────────
                # Più numerose e più rapide da riparare degli incrociatori
                'FFG-46':              {'quantity': 4, 'production': 0,    'repair': {'heavy_damage': 0,    'medium_damage': 1/30, 'light_damage': 4/30}, 'local_industrial_capacity': 0.75},
                'FF 1135M Rezky':      {'quantity': 3, 'production': 0,    'repair': {'heavy_damage': 0,    'medium_damage': 1/30, 'light_damage': 4/30}, 'local_industrial_capacity': 0.75},
                'FFG 11540 Neustrashimy':{'quantity':2, 'production': 0,    'repair': {'heavy_damage': 0,    'medium_damage': 1/30, 'light_damage': 4/30}, 'local_industrial_capacity': 0.75},
                'Type 054A':           {'quantity': 4, 'production': 1/30, 'repair': {'heavy_damage': 0,    'medium_damage': 1/30, 'light_damage': 4/30}, 'local_industrial_capacity': 0.75},
            },
            asea.CORVETTE.value: {
                # ── Corvette / pattugliatori veloci ───────────────────────────────────
                # Più piccole e numerose; riparazione relativamente più rapida
                'FFL 1124.4 Grisha':    {'quantity': 4, 'production': 1/30, 'repair': {'heavy_damage': 0,    'medium_damage': 2/30, 'light_damage': 5/30}, 'local_industrial_capacity': 0.75},
                'FSG 1241.1MP Molniya': {'quantity': 4, 'production': 1/30, 'repair': {'heavy_damage': 0,    'medium_damage': 2/30, 'light_damage': 5/30}, 'local_industrial_capacity': 0.75},
            },
            asea.SUBMARINE.value: {
                # ── Sottomarini ───────────────────────────────────────────────────────
                # Danno pesante non riparabile in teatro; manutenzione in arsenale dedicato
                'Type 093': {'quantity': 2, 'production': 0, 'repair': {'heavy_damage': 0, 'medium_damage': 1/30, 'light_damage': 2/30}, 'local_industrial_capacity': 0.75},
            },
            asea.AMPHIBIOUS_ASSAULT_SHIP.value: {
                # ── Navi da sbarco ────────────────────────────────────────────────────
                'LHA-1 Tarawa': {'quantity': 1, 'production': 0,    'repair': {'heavy_damage': 0, 'medium_damage': 1/30, 'light_damage': 2/30}, 'local_industrial_capacity': 0.75},
                'Type 071':     {'quantity': 2, 'production': 1/30, 'repair': {'heavy_damage': 0, 'medium_damage': 1/30, 'light_damage': 2/30}, 'local_industrial_capacity': 0.75},
            },
            asea.TRANSPORT.value: {
            },
            asea.CIVILIAN.value: {
            },
        },
}


navi = {
    'Carrier': {
        'CVN-70 Carl Vinson': {'class': 'Nimitz-class', 'Nationality': 'USA'},
        'CVN-71 Theodore Roosevelt': {'class': 'Supercarrier', 'Nationality': 'USA'},
        'CVN-72 Abraham Lincoln': {'class': 'Supercarrier', 'Nationality': 'USA'},
        'CVN-73 George Washington': {'class': 'Supercarrier', 'Nationality': 'USA'},
        'CVN-74 John C. Stennis': {'class': 'Nimitz-class', 'Nationality': 'USA'},
        'CVN-75 Harry S. Truman': {'class': 'Supercarrier', 'Nationality': 'USA'},
        'CV-59 USS Forrestal': {'class': 'Forrestal-class', 'Nationality': 'USA'},
        'CV 1143.5 Admiral Kuznetsov': {'class': 'Admiral Kuznetsov', 'Nationality': 'Russia'}
    },
    'Destroyer': {
        'USS Arleigh Burke IIa': {'class': 'Arleigh Burke-class', 'Nationality': 'USA'},
        'Type 052B Guangzhou-class': {'class': 'Luyang I-class', 'Nationality': 'China'},
        'Type 052C': {'class': 'Luyang II-class', 'Nationality': 'China'}
    },
    'Cruiser': {
        'CG-65': {'class': 'Ticonderoga-class', 'Nationality': 'USA'},
        'CGN 1144.2 Piotr Velikiy': {'class': 'Kirov-class Battlecruiser', 'Nationality': 'Russia'},
        'CG 1164 Moskva': {'class': 'Slava-class', 'Nationality': 'Russia'}
    },
    'Frigate': {
        'FFG-46': {'class': 'Oliver Hazard Perry-class', 'Nationality': 'USA'},
        'FF 1135M Rezky': {'class': 'Krivak II-class', 'Nationality': 'Russia'},
        'FFG 11540 Neustrashimy': {'class': 'Neustrashimy-class', 'Nationality': 'Russia'},
        'Type 054A': {'class': 'Jiangkai II-class', 'Nationality': 'China'}
    },
    'Fast Attack': {
        'FFL 1124.4 Grisha': {'class': 'Grisha V-class Corvette', 'Nationality': 'Russia'},
        'FSG 1241.1MP Molniya': {'class': 'Tarantul III-class', 'Nationality': 'Russia'}
    },
    'Submarine': {
        'Type 093': {'class': 'Shang-class Attack Submarine', 'Nationality': 'China'}
    },
    'Amphibious': {
        'LHA-1 Tarawa': {'class': 'Tarawa-class', 'Nationality': 'USA'},
        'Type 071': {'class': 'Yuzhao-class Amphibious Transport Dock', 'Nationality': 'China'}
    }
}



_WEAPONS_AVAILABILITY: Dict[str, Tuple[float, float]] = {   
        'air_weapons': {

            'MISSILES_AAM': {
                    'AIM-54A-MK47': 100,
                    'AIM-54A-MK60': 100,
                    'AIM-54C-MK47': 100,
                    'AIM-54C-MK60': 100,
                    'AIM-7E': 100,
                    'AIM-7F': 100,
                    'AIM-7M': 100,
                    'AIM-7MH': 100,
                    'AIM-7P': 100,
                    'AIM-9B': 100,
                    'AIM-9P': 100,
                    'AIM-9P5': 100,
                    'AIM-9L': 100,
                    'AIM-9M': 100,
                    'AIM-9X': 100,
                    'R-550': 100,
                    'R-530IR': 100,
                    'R-530EM': 100,
                    'RB-24': 100,
                    'RB-24J': 100,
                    'RB-74': 100,
                    'R-13M': 100,
                    'R-13M1': 100,
                    'R-60': 100,
                    'R-60M': 100,
                    'R-73': 100,
                    'R-3S': 100,
                    'R-3R': 100,
                    'R-24R': 100,
                    'R-24T': 100,
                    'R-40R': 100,
                    'R-40T': 100,
                    'R-27R': 100,
                    'R-27T': 100,
                    'R-27ER': 100,
                    'R-27ET': 100,
                    'R-33': 100,
                    'R-37': 100,
            },
            'MISSILES_ASM': {
                    'RB-05A': 100,
                    'RB-15F': 100,
                    'AGM-45': 100,
                    'AGM-84A': 100,
                    'AGM-88': 100,
                    'Kormoran': 100,
                    'RB-05E': 100,
                    'RB-04E': 100,
                    'Sea Eagle': 100,
                    'RB-75T': 100,
                    'RB-15': 100,
                    'AGM-65D': 100,
                    'AGM-65K': 100,
                    'AGM-114': 100,
                    'BGM-71D': 100,
                    '9M120-F': 100,
                    '9M120': 100,
                    '9M114': 100,
                    'Hot-3': 100,
                    'Mistral': 100,
                    'Kh-55': 100,
                    'Kh-101': 100,
                    'Kh-22N': 100,
                    'Kh-58': 100,
                    'Kh-66': 100,
                    'Kh-59': 100,
                    'Kh-25ML': 100,
                    'Kh-25MR': 100,
                    'Kh-25MPU': 100,
                    'Kh-25MP': 100,
                    'Kh-29L': 100,
                    'Kh-29T': 100,
            },
            'BOMBS': {
                    'Mk-84': 100,
                    'Mk-83': 100,
                    'Mk-82': 100,
                    'Mk-82AIR': 100,
                    'GBU-10': 100,
                    'GBU-16': 100,
                    'GBU-12': 100,
                    'GBU-24': 100,
                    'GBU-27': 100,
                    'Mk-20': 100,
                    'BLG66': 100,
                    'CBU-52B': 100,
                    'BK-90MJ1': 100,
                    'BK-90MJ1-2': 100,
                    'BK-90MJ2': 100,
                    'M/71': 100,
                    'SAMP-400LD': 100,
                    'SAMP-250HD': 100,
                    'FAB-1500M54': 100,
                    'FAB-500M62': 100,
                    'FAB-250M54': 100,
                    'FAB-100': 100,
                    'FAB-50': 100,
                    'RBK-250AO': 100,
                    'RBK-500AO': 100,
                    'RBK-500PTAB': 100,
                    'BetAB-500': 100,
            },
            'ROCKETS': {
                    'Zuni-Mk71': 100,
                    'Hydra-70MK5': 100,
                    'Hydra-70MK1': 100,
                    'SNEB-256': 100,
                    'SNEB-253': 100,
                    'S-5 M': 100,
                    'S-5 KO': 100,
                    'S-8 OFP2': 100,
                    'S-8 KOM': 100,
                    'S-13': 100,
                    'S-25L': 100,
                    'S-24': 100,
            },
            'CANNONS': {
                    'UPK-23': 100,
                    'Gsh-23L': 100,
                    'GAU-8/A': 100,
                    'M61A1': 100,
                    'M39A3': 100,
                    'Mk-12': 100,
                    'DEFA-554': 100,
                    'N-37': 100,
                    'NR-23': 100,
                    'NR-30': 100,
                    'GSh-30-1': 100,
                    'GSh-30-2': 100,
                    'GSh-6-23M': 100,
                    'GSh-6-30': 100,
                    'Oerlikon-KCA': 100,
            },
            'MACHINE_GUNS': {
                    'AN-M2': 100,
                    'M3-Browning': 100,
            },
        },
        'ground_weapons': {

            'AUTO_CANNONS': {
                    '2A42': 100,
                    'APV-23': 100,
                    'M242 Bushmaster': 100,
                    'M230 Chain Gun': 100,
                    '2A42-30mm': 100,
                    'M242-Bushmaster-25mm': 100,
                    '2A72-30mm': 100,
                    'ZPT-99-30mm': 100,
                    'L21A1-RARDEN-30mm': 100,
                    'M242-25mm': 100,
                    'MK-20-Rh-202-20mm': 100,
            },
            'CANNONS': {
                    '2A28-Grom-73mm': 100,
                    '2A46M': 100,
                    '2A20': 100,
                    'U-5TS "Molot"': 100,
                    '2A46M-5': 100,
                    '2A46': 100,
                    '2A61': 100,
                    '2A64': 100,
                    '2A70': 100,
                    'M68A1': 100,
                    'M256': 100,
                    'M255': 100,
                    'D30': 100,
                    'D-10T': 100,
                    '2A28 Grom': 100,
                    'D-10T2S-100mm': 100,
                    'L11A5-120mm': 100,
                    'L7A3-105mm': 100,
                    'M68-105mm': 100,
                    'Rheinmetall-120mm-L44': 100,
                    'Rheinmetall-120mm-L55': 100,
                    'M256-120mm': 100,
                    'CN120-26-120mm': 100,
                    'L30A1-120mm': 100,
                    'MG251-120mm': 100,
                    'Type-59-100mm': 100,
                    '2A46M-125mm': 100,
                    '2A46M5-125mm': 100,
                    'ZPT-98-125mm': 100,
                    '2A70-100mm': 100,
            },
            'AA_CANNONS': {
                    'S-68-57mm': 100,
                    'AZP-23-23mm': 100,
                    'M61-Vulcan-20mm': 100,
                    'Oerlikon-KDA-35mm': 100,
                    '2A38M-30mm': 100,
            },
            'MISSILES': {
                    '9K119M': 100,
                    '99K120': 100,
                    '9M14 Malyutka': 100,
                    '9M113 Konkurs': 100,
                    '9M35 Kornet': 100,
                    '9M37M': 100,
                    '9M331': 100,
                    'TOW-2': 100,
                    '9M119-Refleks': 100,
                    '9M119M-Refleks-M': 100,
                    '9M113-Konkurs': 100,
                    '9M14-Malyutka': 100,
                    'BGM-71-TOW': 100,
                    'MILAN': 100,
                    'HJ-73C': 100,
                    '9M311-SAM': 100,
                    '9M31-SAM': 100,
                    'MIM-72-SAM': 100,
                    '9M33-SAM': 100,
                    '9M37-SAM': 100,
                    'Roland-SAM': 100,
                    '9M331-SAM': 100,
                    'FIM-92-Stinger': 100,
                    '3M9-SAM': 100,
                    '9M38-SAM': 100,
                    '5V55R-SAM': 100,
            },
            'ROCKETS': {
                    '122mm-Grad-Rocket': 100,
                    '220mm-Uragan-Rocket': 100,
                    '300mm-Smerch-Rocket': 100,
                    '227mm-MLRS-Rocket': 100,
            },
            'MORTARS': {
                    'M933-60mm': 100,
            },
            'ARTILLERY': {
                    '2A33-152mm': 100,
                    '2A31-122mm': 100,
                    '2A51-120mm': 100,
                    '2A64-152mm': 100,
                    'Dana-152mm': 100,
                    'M284-155mm': 100,
                    'PL-45-155mm': 100,
                    'Firtina-155mm': 100,
            },
            'FLAME_TRHOWERS': {
            },
            'GRENADE_LAUNCHERS': {
                    'AGS-17': 100,
            },
            'MACHINE_GUNS': {
                    'PKT-7.62': 100,
                    'Kord-12.7': 100,
                    'NSVT-12.7': 100,
                    'M2HB-12.7': 100,
                    'M240-7.62': 100,
                    'KPVT-14.5': 100,
                    'DShK-12.7': 100,
                    'L8A1-7.62': 100,
                    'L37A1-7.62': 100,
                    'L37A2-7.62': 100,
                    'L94A1-7.62': 100,
                    'MG3-7.62': 100,
                    'MG34-7.92': 100,
                    'M240C-7.62': 100,
                    'M1919-7.62': 100,
                    'FN MAG-7.62': 100,
                    'ANF1-7.62': 100,
                    'M693-12.7': 100,
                    'PKM-7.62': 100,
                    'PKTM-7.62': 100,
                    'Type-59T-7.62': 100,
                    'Type-86-7.62': 100,
                    'QJC88-12.7': 100,
                    'K6-12.7': 100,
            },

        },
        'sea_weapons': {},
}

_REFERENCE_COST_K: float = 303_000.0