"""
 MODULE Manager
 
Sequence of processes for evaluating DCS data (missions and status), recording statistics, planning missions and writing DCS data to LUA tables

"""






from Dynamic_War_Manager.Source import Mil_Base
import Context

regions = { #blocks in region

    "blue": {},
    "red": {},
    "neutral": {}

    }

missions = {

    "blue": {},
    "red": {},
    "neutral": {}

    }

state = {

    "morale": {"blue": {}, "red": {}, "neutral": {}},
    "global_efficiency": {"blue": {}, "red": {}, "neutral": {}},
    "production": { "goods": {"blue": {}, "red": {}, "neutral": {}},
                    "food": {"blue": {}, "red": {}, "neutral": {}}, 
                    "energy": {"blue": {}, "red": {}, "neutral": {}}, 
                    "human resource": {"HC": {"blue": {}, "red": {}, "neutral": {}}, "HS": {"blue": {}, "red": {}, "neutral": {}}, "HB": {"blue": {}, "red": {}, "neutral": {}}, "HR": {"blue": {}, "red": {}, "neutral": {}}}
                    },
    "transport": {"blue": {}, "red": {}, "neutral": {}},
    "military": {"blue": {}, "red": {}, "neutral": {}},
    "urban": {"blue": {}, "red": {}, "neutral": {}},

    }



# reading and loading DCS data: reading from lua table and loading to python object
pass

# evaluate mission result: from python object evaluate mission results
pass

# execute simulation for virtual mission result: execution of the simulation in relation to the mission results
pass

# save mission result: saving the mission results for statistical use and analysis 
pass

# execute tactical blocks evaluation and planning: loop of recon request to all blocks
# recoinassance report request   
recons = { "side": None, "mil_base": None, "id": None, "reports": None }

for side in Context.SIDE:
    recons["side"] = side
    
    for block in regions[side]:    

        if isinstance(block, Mil_Base):
            recons["mil_base"] = block.name
            recons["id"] = block.id
            recons["reports"] = block.getRecon()

"""
evaluate strategic directive: 
    parameters:
    zone 
        level of air operation: 
            interdiction (strategic strike): production, storage and transport of: goods, energy, hr, military, urban
            ground support: ground attack operation, ground defence operation
            naval support: naval attack operation, naval defence operation
            air superiority: awacs, fighter sweep, 
            air defence operation: intercept, patrol (goods, energy, hr, military, urban)
            air escort: air strike mission, air transport mission, air recon mission, ground operation, naval operation 
            air recon, 
            air transport, 
                
        level of ground operation:
            offensive: ground attack operation: production, storage and transport of: goods, energy, hr, military, urban,
            defensive: ground defence operation, 
            maintaing: ground patrol operation,
            recon: ground recon operation: production, storage and transport of: goods, energy, hr, military, urban,
            transport: ground transport operation: production, storage and transport of: goods, energy, hr, military, urban,
            
        level of naval operation:
            offensive: naval attack operation,
            defensive: naval defence operation,
            maintaing: naval patrol operation,
            transport: naval transport operation,
            recon: naval recon operation,

        level of goods: production, storage and transport

        minimum level of goods

        level of energy: production, storage and transport

        minimum level of energy

        level of human resource
            civilian: hr
            military: hc, hs, hb
            
        minimum level of human resource


    Il modello TLC introduce un "C2 Planner" (Pianificatore di Comando e Controllo) che simula l'esecuzione di piani operativi di manovra, 
    valutando la probabilità di successo di un piano operativo e allocando risorse di terra e aeree per massimizzare la probabilità di raggiungere 
    gli obiettivi prioritari.

    Il documento descrive l'uso di algoritmi adattativi per l'allocazione delle risorse, come l'algoritmo Sequential Analytic Game Evaluation (SAGE), 
    che consente di simulare decisioni basate su obiettivi e di adattare le strategie in risposta alle informazioni disponibili.

    Questo approccio adattativo è fondamentale per rappresentare il valore dei sistemi di comando, controllo, comunicazioni, computer e intelligence (C4I) e 
    per analizzare l'impatto delle decisioni sotto incertezza.

    assegnazione riserve in relazione agli obiettivi prioritari
    assegnazione risorse in relazione agli obiettivi prioritari




    Crea in DCS ed in WM percorsi spostamenti asset

    Questi percorsi sono rappresentati dalle route e/o dagli oggetti DCS (cross point, stop point, ecc) utilizzati per identificare e localizzare gli 
    elementi importanti del percorso di spostamento (incroci, ponti, ecc)   Nel WM devono essere utilizzati per definire un grafo con: 
    
    - Nodi: costituiti dagli waypoint DCS di una route: i waypoint dovrebbero essere definiti tra due punti dove la percorribilità è possibile e nel 
    caso di offroad è in linea retta. Quindi è opportuno uilizzare anche degli oggetti statici DCS per ulteriore localizzazione e gestione del waypoint 
    ed eventualmente anche dello stato (verifica se e come DCE gestisce lo stato delle infrastrutture predefinite nelle mappe DCS)

    - Archi: il percorso definito tra due waypoint: questo percorso è caratterizzato da un livello di minaccia (aerea, terrestre), da un tempo di 
    percorrenza, dal livello di pendenza e dalla tipologia di terreno che viene utilizzata in relazione per verificare difficoltà e possibilità di 
    percorrenza di un mezzo specifico


    

    
   """     

pass

# execute strategical and tactical evaluation and planning: analysis of block reports and global situation (general status and intelligence) and block mission planning
pass

# writing DCS data to lua table: writing from python object to lua table
pass