---
name: feedback-verifica-mix-a-ogni-delega
description: A ogni verifica di una delega oc: dal CSV OpenRouter calcolare il mix reale e lanciare prezzi_fornitori.py --mostra --mix; riferire solo se la testa della graduatoria cambia (decisione utente 2026-11-11)
metadata:
  type: feedback
---

Quando verifico una delega oc (CSV Activity di OpenRouter), calcolo dal CSV il mix reale dei soli record del modello principale (token non in cache = `tokens_prompt - tokens_cached`, in cache = `tokens_cached`, output = `tokens_completion`) e lancio `python3 ~/Sviluppo/ai-multimodel/scripts/prezzi_fornitori.py --mostra --mix <nc>,<cache>,<out>`. Lo riporto all'utente **solo se la testa della graduatoria cambia** (primo classificato diverso, distacco #1-#2 > 20%, o un fornitore non fp4 con struttura di prezzo diversa fra i primi tre); altrimenti una riga ("graduatoria invariata"). Il calcolo del costo con i prezzi dello script quadra col costo reale del CSV (verificato sul FP 1B: 0,447 $).

**Why:** il `MIX` dello script (F8c1, 23/10) non si aggiorna su una o due sessioni (varianza alta: non in cache 4,7-8,8%, output 0,65-1,9%); il test su 5 mix, da 2% a 100% non in cache, ha mostrato che la testa (Baidu, StreamLake, DeepSeek diretto, distacco < 2%) non cambia: il mix conta solo con fornitori fp4 (Relace, Wafer), esclusi. Un selettore per tipo di lavoro non conviene finche' la testa e' robusta. L'utente ha scelto solo il controllo manuale a ogni delega, NON l'opzione `--verifica-mix` automatica con hook (puo' riconsiderarla).

**How to apply:** `MIX` e lo script in `ai-multimodel` restano invariati (progetto dell'utente: non toccarlo senza ok). Riaprire l'idea di un selettore solo se la testa diventa sensibile al mix. Collegata a [[feedback-oc-blocchi-piccoli-verifica-parziale]] e [[project-opencode-costi-misurati]].
