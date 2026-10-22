---
name: project-opencode-costi-misurati
description: "Costi REALI di oc-developer (DeepSeek V4 Pro via OpenRouter) misurati il 2026-10-22: F8a = 4,07 $ in 2 sessioni, ~3 $ in piu' per il fornitore (Azure, Relace) estratto a caso da OpenRouter; oc export sottostima ~1,95x; regole per contenere i costi; F8a fatta (c1182d8a)"
metadata:
  type: project
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
- **DA FARE**: fissare il fornitore nel `opencode.json` di progetto (`provider.openrouter.models["deepseek/deepseek-v4-pro"].options.provider`
  con `order` baidu, streamlake e `allow_fallbacks:false`) e provarlo con un `oc run` da 0,005 $ guardando i Logs; poi provare la 0813;
  registro `Rapporti/Costi_Deleghe.md`; alzare il limite della chiave prima di F8b. Criteri fornitore: costo atteso su carico ~95% cache
  (cache letta + ingresso), uptime 100%, fp8, niente fp4, un fornitore per sessione.
- **Stato F8**: F8a FATTA e verificata (suite 4619 OK skipped 7, confronto 982 IDENTICHE, merge `c1182d8a`, Piano aggiornato `73cd5e22`);
  restano F8b, F8c, F8-R (rinviata: nessun agente OpenCode ha accesso al web), F6-B3 (una riga di docstring), push da chiedere all'utente.
- **Why:** la sessione principale ha il Pro al 93% (7d) e i soldi OpenRouter sono un tetto reale; un ciclo a vuoto o un fornitore caro
  brucia budget senza produrre lavoro verificabile.
- **How to apply:** stimare il costo con ~0,01-0,03 $ per passo (x2 se il fornitore non e' fissato) dichiarando che non e' misurato;
  dividere i piani grandi in blocchi con sessioni nuove; leggere il consumo da OpenRouter. Collegata a [[feedback-model-effort-delegation]].
