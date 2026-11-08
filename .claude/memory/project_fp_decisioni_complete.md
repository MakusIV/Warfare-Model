---
name: project-fp-decisioni-complete
description: "FP (finestre per passaggio): FP-1..FP-10 TUTTE decise il 2026-11-08; elenco delle modifiche da riportare nella Proposta FP (da riscrivere con des-planner) e stato dei blocchi"
metadata:
  type: project
---

Proposta: `Analysis/Document/Proposta_Finestre_Per_Passaggio_Portata_Propria.md` (ancora NON aggiornata con le decisioni 2026-11-08; non toccata dal 2026-11-07).

## Decisioni
- FP-1 = B-R (passaggi dai tratti nel risolutore); FP-2 = O3 (stream separato `pass_rng`); FP-3 = (a) candidato valido fino alla FINE DEL PASSAGGIO; FP-4 = (a) CPA del passaggio (2026-11-07).
- **FP-5 = (d)** (2026-11-08): per R-INT il lancio e' "visto" solo se l'intercettore ha rilevato il lanciatore (rilevamento <= t_launch) NEL PASSAGGIO che contiene t_launch (i passaggi sono quelli dopo l'unione FP-10); nessun passaggio che contiene t_launch = non visto (geometria, tau = total). Il piano §4 punto 10 implementava (a): da riscrivere. (b) e (c) scartate col criterio [[feedback-interruttori-criterio]]. Difetto verificato: `_detection_time_of` costruisce un dict (osservatore, bersaglio) -> tempo, l'ultimo rilevamento sovrascrive il primo.
- **FP-6 = (a)**: permanenza D-5 = passaggio che contiene il CPA della finestra (in subordine il piu' lungo), mai la somma, senza interruttore nuovo; punto 8 del blocco 1 confermato incondizionato; test 14 ok, aggiungere test diretto del ripiego `next(..., longest)`.
- **FP-7 = (a)**: `Engagement_Resolver.FP_PER_PASS_DETECTION = False`, `pass_rng` passato solo se acceso; TEMPORANEO: dichiarare nella Proposta il criterio di rimozione (dopo sonda P-1, lettura delle cambiate da parte dell'utente, nuova fotografia, blocco di pulizia). Nessun test sulle combinazioni scartate.
- **FP-8 modificata = 4 varianti** `off`, `on`, `cas_off`, `cas_on` x 5 semi = 20 NEW (tolte le varianti dwell); dwell della ZSU in S33 = 2 s [S] (umano+ottica), con g=1 la D-5 non cambierebbe nulla. Confronto finale atteso derivato `compared 1113: 104` (1029 + 32 S35 + 32 S34 + 20 S33; da ricontrollare).
- **FP-9 = (a)**: pianificatore non toccato; limite dichiarato in §5.2; nota dell'utente sui 3 criteri di `Air_Route_Manager` (vedi [[project-session-2026-11-07-summary]]); metrica cumulativa quando ci sara' un consumatore.
- **FP-10 = (c)**: passaggi separati da un'uscita <= dwell del sensore si UNISCONO (permanenza dall'inizio del primo alla fine dell'ultimo, CPA del passaggio unito); usa il lettore di dwell della D-5 => solo con D-5 accesa e solo per sensori con dwell (oggi 10 EWR, DW-9 estendera'); senza dwell nessuna unione. Motivazione utente: tracciamento predittivo. Test unitari: unione se uscita <= dwell, no se > dwell, no senza dwell, no con D-5 spenta. Finestre e pianificatore restano con la tolleranza numerica (limite dichiarato).
- **Sonda P-1: aggiungere il conteggio dei passaggi di durata zero** (rotte tangenti: `range_intervals` tiene gli intervalli con s1==s2); correggere anche `Rapporti/Sonde_Finestre_Passaggio/LEGGIMI.md` e `probe_switch_on.py` (con FP-3 (a) cambiano al piu' le 44 AFTER_PASS).

## Da correggere nella Proposta (revisione di coerenza `Revisione_Incrociata_Coerenza_oc-reviewer.md`)
Bloccante 1 (FP-6) e importante 2 (FP-5) ora risolti dalle decisioni; precondizione 3 ("tutte le FP decise") ora soddisfatta; aggiungere la precondizione del branch dedicato; ricalcolare base e conteggi sull'ordine BI -> VA -> FP (BI blocco 2 gia' fatto: suite 4829); aggiornare glossario, stato in testa, §2.6-2.11, §3, §4 (blocchi, test, S33), §5.2.

## Stato
Riscrittura della Proposta: da fare con des-planner (Opus high), poi rilettura incrociata; i blocchi FP si eseguono dopo BI (blocchi 3-4) e VA. Dopo FP: analisi mirata degli interruttori e proposta di aggiornamento della regola in AGENTS.md (spetta all'utente).
