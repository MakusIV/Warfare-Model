---
name: project-opencode-costi-misurati
description: "Costi REALI di oc-developer (DeepSeek V4 Pro via OpenRouter) misurati il 2026-10-22: F8a = 4,07 $ in 2 sessioni, ~3 $ in piu' per il fornitore (Azure, Relace) estratto a caso da OpenRouter; oc export sottostima ~1,95x; regole per contenere i costi; F8a fatta (c1182d8a)"
metadata:
  node_type: memory
  type: project
  originSessionId: 1d3b4d7d-48a4-4011-92a5-5c4578c21791
  modified: 2026-10-23T10:21:14.417Z
---

- **Misura (OpenRouter, Logs > Sessions; screenshot in `~/Downloads/screenshoot.*DeepSeek.Pro.V4.pdf`)**: sessione 1 di `oc-developer`
  su F8a = 3,0868 $ (103 richieste, fornitore **Azure**, interrotta dal limite della chiave da 3 $); sessione 2 = 0,979 $ (82 richieste,
  fornitore **Relace**, fp4, completata, commit `e593bc9a`). Totale 4,07 $. Con i prezzi di listino di Baidu/StreamLake sarebbero
  stati ~0,99 $: ~3 $ in piu' per il fornitore. Il prezzo medio dello screenshot (0,25 $/M a 94,8% di cache) coincide con quello di Azure.
- **OpenRouter sceglie UN fornitore per sessione (sticky) e non favorisce abbastanza i piu' economici**: il 2026-10-21 la stessa
  configurazione ha dato StreamLake, Cloudflare, Novita (chiave osboxes), Baidu, Relace (chiave ProArt). La configurazione di OpenCode non
  contiene nessuna preferenza di fornitore (verificato: global, progetto, agenti, `oc debug config`). Fornitori di V4 Pro 0423: 16, da
  0,44 a 1,91 $/M in ingresso; cache letta 0,037 (Baidu, StreamLake) fino a 0,33; V4 Pro 0813 esiste (Baidu 0,224/0,673, cache 0,007).
- **`oc export`/`oc stats` sottostimano di ~1,95x** (1,60 contro 3,09; 0,50 contro 0,98): per i soldi fa fede solo OpenRouter. I prezzi
  della guida `ai-multimodel` sono quelli del fornitore piu' economico alla data, non quelli che si pagano col routing di default.
- **La mia stima iniziale (0,15 $ per F8a) era sbagliata di un ordine di grandezza**: il costo cresce col contesto accumulato (fino a
  ~160k token riletti a ogni passo, 11,6 M di cache letta in una sessione), non col numero di righe del piano.
- **Regole adottate (2026-10-22)**: `steps` di `oc-developer` = 120; nel prompt dell'agente letture mirate, py_compile, regola dei due
  fallimenti (`adcf5043`); sessioni nuove per blocchi; suite e confronto lanciati dalla sessione principale in background
  (`/tmp/.../verifica_seq.sh`: `verifica.sh suite` poi `confronto` in un solo comando background, una notifica a fine) invece che
  dall'agente. Chiave osboxes portata a 5 $ dall'utente (rimasti ~0,9 $).
- **Fornitori fissati e PROVATI (2026-10-22, commit `6c0b021e`)**: nel `opencode.json` di progetto `provider.openrouter.models.<id>.options.provider`
  con `order` e `allow_fallbacks:false` per V4 Pro 0813 (baidu, deepseek, streamlake), V4 Pro 0423, V4.1 Flash (coreweave, streamlake),
  GLM 5.3 (morph, sail-research); planner/developer/debugger passati alla **0813**. Test `oc run --agent oc-planner ...`: Baidu + 0813,
  costo 0,001254 $ = prezzo di listino (8520 token); la richiesta 'doppia' e' il titolo della sessione (`small_model`, Flash su CoreWeave).
  Con `order` OpenRouter salta il routing sticky. Costo atteso di una richiesta a 160k di contesto con 0813/Baidu ~0,0014 $ (stima, non
  misurata): ~20 volte meno di Azure. Prezzi dei fornitori cambiano di giorno in giorno: ricontrollare. Impostazione workspace consigliata:
  Routing > Default Provider Sort = Price (rete di sicurezza, non sostituisce `order`). Chiave osboxes a 10 $ (residui ~5 $).
  Registro dei costi: `Analysis/Document/Rapporti/Costi_Deleghe.md` (F8b reale 0,155 $ con Baidu, 120 richieste, 23 minuti).
- **Prezzi 'ballano' (2026-10-23, CSV OpenRouter Activity)**: F8c1 su Baidu = 1,40 $ (85 chiamate) contro 0,155 $ di F8b (120 chiamate): stesso
  fornitore, prezzo x9,1 (Baidu 0813: 0,145/0,436/0,0046 il 22/10 -> 1,32/3,96/0,042 il 23/10, sconto finito). `order` mette Baidu per primo e
  disattiva `sort` e il Default Provider Sort dell'account (non e' indisponibilita'). StreamLake = meta' di Baidu (0,66/1,98/0,022); 2 chiamate
  isolate lo hanno servito con cache fredda (0,06-0,08 $ l'una). `sort: price` e' pericoloso: ordina sul prompt, ma il 95% dei token e' cache:
  Relace/Wafer costano +378% sul mix reale. Nessuna tolleranza % nativa in OpenRouter (solo `max_price` assoluto, `only`, `ignore`, `order`).
  **Soluzione (2026-10-23, nel repo ai-multimodel, commit 80a1358)**: `scripts/prezzi_fornitori.py` calcola il costo effettivo sul mix misurato (tolleranza 50%,
  candidati = TUTTI i fornitori utilizzabili, fp4 solo in coda, uscita max >= 32768) e scrive `order`+`allow_fallbacks:false`+`max_price`+`cost` in
  `~/.local/share/opencode/routing.local.json` (per macchina, fuori da git); `bin/oc` lo rigenera ogni 30 min e lo passa con `OPENCODE_CONFIG`.
  Il `opencode.json` di Warfare-Model NON ha piu' il blocco `provider` (un options.provider di progetto prevarrebbe). Prima prova reale: F8c2 = 0,4785 $ tutta
  su StreamLake (stesso consumo su Baidu ~0,94 $). `deepseek` ha fasce orarie a prezzo ridotto e poi torna a 1,32.
- **Baidu ha un prezzo che varia nella giornata (osservato 2026-10-23, dai CSV, non dichiarato da OpenRouter)**: fatturato 1,32/3,96/0,042 $/M alle 08-09 UTC; ~0,2/0,6/0,006 alle 13:20-13:40 UTC; 0,148/0,44/0,0047 listino alle 14:38 UTC; 0,145 il 22/10 alle 15 UTC. Probabile fascia oraria (sera/notte in Cina). Lo script sceglie il piu' economico AL LANCIO (F8c3: Baidu da solo, 0,2789 $ contro ~0,9 $ su StreamLake); `max_price` e' fissato al lancio.
- **Stato F8**: F8a FATTA (`c1182d8a`), F8b FATTA (`33698fb4`, suite 4640, 982 IDENTICHE); restano F8c (3 blocchi, v. [[project-f8c-comandi-blocchi]]), F8-R
  (rinviata: nessun agente OpenCode ha il web), F6-B3 (una riga di docstring). `steps` oc-developer = 180 dal 2026-10-22 (F8b ha esaurito 120).
- **Why:** la sessione principale ha il Pro al 93% (7d) e i soldi OpenRouter sono un tetto reale; un ciclo a vuoto o un fornitore caro
  brucia budget senza produrre lavoro verificabile.
- **How to apply:** stimare il costo con ~0,01-0,03 $ per passo (x2 se il fornitore non e' fissato) dichiarando che non e' misurato;
  dividere i piani grandi in blocchi con sessioni nuove; leggere il consumo da OpenRouter. Collegata a [[feedback-model-effort-delegation]].
