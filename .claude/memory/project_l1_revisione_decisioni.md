---
name: project-l1-revisione-decisioni
description: "Revisione della regola L1 (lanciatore dentro il V_I non si intercetta): sonda e decisioni a-e (2026-11-24), Proposta SCRITTA e committata; RIPRESA per la prossima sessione sul ProArt con il prospetto di scelte da riproporre all'utente"
metadata:
  node_type: memory
  type: project
  originSessionId: db4537e6-f512-41af-b45f-1c8dabc15406
  modified: 2026-11-24T17:42:49.508Z
---

## RIPRESA (fine sessione osboxes 2026-11-24, PROSSIMA SESSIONE SUL PROART) — Proposta L1 scritta, in attesa delle scelte dell'utente

**Stato di fatto.** Decisioni di design a-e PRESE (sotto); sonda fatta; **Proposta SCRITTA** da des-planner (Opus high, 54 min, 457 mila token, 185 chiamate): `Analysis/Document/Proposta_Revisione_L1_Lanciatore_Bersaglio.md` (1198 righe; committata e pushata a fine sessione). **Letta da me solo la struttura e le sezioni 2-3**: codice, numeri di riga, catture e test dichiarati (provati dall'agente su un prototipo FUORI dal repo) NON sono ancora verificati da me. Nessun codice del progetto cambiato. Pendente dal 2026-11-08 ([[project-bi-blocco3-punti-aperti]]). Documento di stato `Analysis/Document/Stato_Progetto_DES.md` committato (`0c7263cd`, riga 3 = L1 in corso).

**Esito chiave della Proposta.** Sulle 1219 esecuzioni la regola rivista NON esclude MAI nessuna coppia (414 valutate, 0 escluse); accesa, la fotografia coincide con quella con L1 spenta del tutto: **6 cambiate, 1213 identiche, 0 nuove** (S16/S16-3: intercettazioni 34 -> 44, il porto da distrutto a tenuto; S19AD/S19-4/tor_forward_ifv_only: il Tor intercetta 2 colpi; S35-ADTGT-0..3/naval_maverick_off: la Rezky sopravvive). Quindi il ramo "bersaglio immediato = non si intercetta" e' provato solo da test unitari. Suite con la regola in memoria (prototipo): Ran 4973, 6 falliti (5 stub che descrivono la regola di oggi, fissati a interruttore spento nel blocco 2; 1 `test_forward_tor_engages_launchers_inside_its_zone` da riscrivere all'accensione). Interruttore `L1_IMMEDIATE_TARGET_RULE`, default `False`, temporaneo (da eliminare al blocco 6). Zona = unione dei cilindri delle singole armi `Anti_Missile`, nuovo `Mobile.interceptor_envelopes()`; condizione "bersaglio immediato" = rilevato al lancio (come R-INT) + `_in_range_at` sul candidato del passaggio del lancio (C-pieno, non il ripiego). Nessuna estrazione RNG, nessuna costante nuova. Attenzione: con le armi `Anti_Missile` la fascia di quota di tutte le navi scende a 0 m per i CIWS (per questo zona per arma e non un cilindro unico).

**Dimensione (dalla Proposta):** blocchi 1-3 piccoli/medi (~50 righe in `Asset/Mobile.py`, ~90 in `Logic/Engagement_Resolver.py`, 8 test in `Test_Mobile`, 14 in `Test_Engagement_Resolver`, 9 di scenario fuori dalla fotografia, 3 classi ritoccate); suite attesa base + 31; confronto atteso 1219 identiche. Blocco 4 = sonda in sola lettura della sessione principale (script in Appendici A e B della Proposta). Blocco 5 = accensione (una riga di default e due test), SOLO dopo decisione esplicita dell'utente. Blocco 6 = pulizia (da ripianificare). Manuale: blocco separato per des-manual-writer.

### PROSPETTO DA RIPROPORRE ALL'UTENTE all'apertura della sessione (egli deve ancora rispondere)

**A. Scelta dell'esecutore dei blocchi 1-3** (proposta in una riga + conferma, regola di CLAUDE.md): `oc-developer` (DeepSeek V4 Pro high) su branch `ai/oc-l1-revisione` — prima commit della Proposta (gia' fatto), `git switch -c ai/oc-l1-revisione`, poi l'utente lancia `/esegui Proposta_Revisione_L1_Lanciatore_Bersaglio` nella TUI di `oc`. Il blocco 4 (sonda) lo fa la sessione principale. Prima di eseguire, tre strade da far scegliere:
1. **Rilettura incrociata con `oc-reviewer` (GLM 5.3)** (`/rivedi <branch> <Proposta>`; o des-planner/Opus se si vuole), poi esecuzione — raccomandata per prudenza (la Proposta e' il contratto e il planner ha lavorato da solo con un prototipo fuori dal repo);
2. **Esecuzione diretta**, con la mia verifica a campione dei codici citati (righe di `Engagement_Resolver.py`, `Mobile.py`, `_in_range_at`, `interceptor_weapons_from_registry`);
3. **Altra delega**: l'utente indica l'agente (alternativa: `des-developer`, Claude).
Prima di nuove deleghe controllare mix e limite OpenRouter ([[feedback-verifica-mix-a-ogni-delega]]).

**B. Conferme richieste all'utente (nessuna blocca i blocchi 1-4):**
| Voce | Domanda | Raccomandazione della Proposta |
|---|---|---|
| Q-L1-1 | interruttore temporaneo o permanente | temporaneo (A), si decide al blocco 6 |
| Q-L1-2 | accendere dopo il rapporto del blocco 4 | si', se conferma le 6 esecuzioni attese |
| Q-L1-3 | ordine rispetto a BI | prima L1 con la sua fotografia, poi BI con una sonda propria |
| Q-L1-4 | scenario S37 che eserciti davvero l'esclusione (facoltativo, Proposta separata) | non farlo ora |
| SD-1..SD-6 | scelte di realizzazione dell'analista: istante di tiro `max(t_ready, t_launch)`, zona per arma (unione), metodo in `Mobile`, nessun ripiego sul V_I, un solo interruttore, stato del lanciatore dopo il lancio ignorato | gia' adottate dal piano, confermabili |
Punti di dottrina APERTI, non da decidere ora: PD-1 (missile fire-and-forget gia' in volo non e' fermato dall'uccisione del lanciatore) e PD-2 (lanciatore abbattuto prima della risoluzione).

**C. Dopo l'esecuzione:** verifica del rapporto OpenCode con la procedura di CLAUDE.md (log con trailer, diff, status, stash vuota, modello effettivo, costo/provider da OpenRouter in `Rapporti/Costi_Deleghe.md`, rilettura del codice, suite e confronto con `tools/ai/verifica.sh`), poi blocco 4 (sonda), decisione di accensione, fotografia nuova (SOLO l'utente), manuale (des-manual-writer), blocco 6; solo dopo riaprire BI (S35 dipende da L1 e da BI).

**D. Altre attivita' pendenti (non L1):** prova dei 32 diagrammi Mermaid in Obsidian (utente; D15 modificato e non renderizzato); togliere o archiviare `Guida_Concettuale_DES_ParteA/B/C/D.md` (dopo l'ok dell'utente al documento di stato); `[S/D]` e `[B 9.1]`/`[B 9.2]` della guida restano; pendenti di `Stato_Progetto_DES.md` sezioni 3-4 (accensione BI e VA, fonte per la Pd 0,2, passaggio del rilevamento fra sessioni, D-5 nella rotta, interruttori, F8d, ecc.). Su ProArt usare `.direnv/python-3.12` (lo sceglie `verifica.sh`); suite ~10 min.

### Dettaglio per riferimento

**Che cos'e' L1** (`Engagement_Resolver._may_intercept`, `Logic/Engagement_Resolver.py:3719`): un intercettore NON ferma i colpi di una salva se il punto di lancio e' dentro il suo V_I (cilindro = raggio massimo di TUTTE le armi antiaeree dell'asset, `Mobile.air_defense_volume`; bordo = dentro). Viene dalla regola dell'utente 2026-09-28 (Proposta_Regole_Allocazione_SAM §7.7 Q1/Q2, "soglia a margine zero"). NON e' R-INT (traccia e tempo di reazione) ne' BI (classe della munizione): l'utente le aveva confuse.

**Sonda (2026-11-24; script temporaneo nello scratchpad di osboxes, NON nel repo e non portabile; sostituito da `sonda_L1_nuova.py` dell'agente e dall'Appendice A della Proposta):** confronto con la fotografia IDENTICAL (la sonda non altera nulla). L1 esclude 13 coppie (intercettore, salva) su 410 valutate, solo in S16 (7: Molniya vs F/A-18C, tof 60 s), S19AD (2: Tor vs A-10C, tof 23 s), S35-ADTGT (4: Rezky). In tutti e 13 R-INT avrebbe lasciato intercettare. In 9 su 13 (S16, S19AD) il lanciatore NON era rilevato dall'intercettore: ne' si intercetta ne' si spara al lanciatore. Distanze dal 19% al 92% del raggio. L1 spenta su S16/S19AD/S35: cambiano 6 esecuzioni su 1219. Il caso Burke (V_I 240 km) non e' esercitato da nessuna esecuzione. I canali di tiro NON sono condivisi fra sparare al lanciatore e intercettare (il codice sottrae solo i canali spesi per altre forze dello stesso dominio, nello stesso istante).

**Decisioni dell'utente (2026-11-24):**
- **a = 2**: esclusione CONDIZIONATA: vale solo se il lanciatore e' davvero un bersaglio immediato; altrimenti il colpo resta intercettabile (R-INT controlla il tempo).
- **c = 2**: "bersaglio immediato" = lanciatore GIA' RILEVATO dall'intercettore (per asset) E intercettore con arma con scorta e portata per colpirlo (stessa condizione del pool prioritario di L2, `_in_range_at`). Ripiego approvato ma non raccomandato: solo "rilevato al lancio".
- **d = 2**: zona di L1 = raggio dell'arma che intercetta (solo task `Anti_Missile`), non il V_I di tutte le armi antiaeree. Rezky, Grisha, Molniya 12 -> 4 km (AK-630), FFG-46 74 -> 1,5 km (Phalanx); Burke/CG-65 240, Type 052C 200, Kuznetsov/Piotr/Moskva 150, S-300PS 75, Buk 35, Tor 12 restano (riverificati dal planner dai registri). Burke: non intercetta i missili di un lanciatore che ha gia' rilevato entro 240 km, conseguenza accettata.
- **e = 1** (confermata dopo un'iniziale scelta 2): confronto NETTO, soglia a margine zero, bordo = dentro, nessuna fascia di transizione, nessuna costante nuova (come Proposta SAM §7.3).

**Regola finale:** un intercettore NON intercetta i colpi di un lanciatore solo se (1) il punto di lancio e' dentro la zona dell'arma che intercetta E (2) il lanciatore e' un suo bersaglio immediato. In ogni altro caso il colpo e' intercettabile, subordinato a R-INT, canali, scorta, BI.

**Why:** L1 ferma sia la difesa dal colpo sia la risposta al lanciatore quando questo non e' rilevato, e usa un volume (il V_I contro aerei) che non e' la portata d'intercettazione dei missili. **How to apply:** non toccare il codice finche' la Proposta non e' approvata e l'esecutore scelto; ogni costante nuova va dichiarata [S]; presentare le decisioni una per volta con sigle spiegate ([[feedback-presentazione-decisioni]]); deleghe come in [[feedback-model-effort-delegation]].
