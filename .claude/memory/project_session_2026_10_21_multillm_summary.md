---
name: project-session-2026-10-21-multillm-summary
description: "Sessione 2026-10-21 (ProArt, progetto ai-multimodel) CHIUSA e pushata: ruoli multi-agente ridefiniti (nuovi oc-planner/oc-debugger/oc-writer, comandi /piano /esegui /rivedi /diagnosi /bozza), prove U4 4/4 riuscite, Piano Missione allineato (voce 11 e riga F7b), osboxes pronta con OpenCode; si puo' assegnare l'esecuzione F8"
metadata:
  type: project
---
- **Ruoli ridefiniti**: tabella in [[feedback-model-effort-delegation]] (dettagli `ai-multimodel/docs/Valutazione_Ruoli_DeepSeek.md` §5 e
  `docs/Guida_Uso_Agenti.md`). Modelli Claude solo nel Pro; DeepSeek/GLM con effort high; modelli OpenRouter limitati a 6
  (lista ammessa). Agenti in `AGENTS.md`. `oc-ui-developer` e' globale e DISATTIVATO in questo progetto.
- **Prove U4** (registro `ai-multimodel/registro_pilota.md`, ~0,35 $): U4a oc-developer + V4.1 Flash su
  `Proposta_Allineamento_Piano_Missione.md` -> Piano della Missione identico al piano (merge `ac716125`, suite 4555 OK, confronto
  982 IDENTICAL rieseguiti dal principale): **chiude la voce 11 del manuale §9.6 e anche la voce 23** (riga F7b del Piano non piu'
  "da verificare"); il manuale va aggiornato da des-manual-writer. U4b oc-debugger: diagnosi esatta (0,26 $, istruzioni corrette
  per evitare la suite superflua, `bc27a801`). U4c oc-writer: 16/16 interruttori esatti; trovata anche una riga obsoleta in
  `Proposta_F7_Bersagli_Filtro_Armi.md:356` (cita `:799`, oggi gli interruttori F7 sono a `Session_Simulator.py:873-881`).
- **Regole tecniche nuove**: in `oc run` un permesso `ask` rifiutato INTERROMPE la sessione, `deny` no -> negli agenti
  `bash "*": deny` (`4b1db769`); `rg` consentito; i comandi `/esegui` ecc. usano sempre il modello dell'agente (`-m` ignorato),
  per un modello alternativo `oc run --agent <agente> -m <modello> "..."`; trailer `AI-Agent` solo dall'hook, il modello
  effettivo lo riporta il principale nel messaggio di merge (da `oc export <sessione>`).
- **osboxes**: OpenCode 1.19.3 installato e verificato (Fasi 0-6 di `ai-multimodel/docs/Piano_osboxes.md`), chiave
  `opencode-osboxes` 3 $, `claude-or` OK. La VM gira sul Notebook HP ProBook (Windows 10) che ha una **VPN aziendale**: con la
  VPN attiva Game_PC (corsia locale) NON e' raggiungibile; OpenRouter si'.
- **`claude-local` NON funziona** con i modelli di Game_PC (template di qwen3.8 rifiuta messaggi di sistema successivi): la
  corsia locale si usa solo con OpenCode (`oc-helper`).
- **Prossimo**: assegnare gli esecutori di F8a-F8c con la tabella dei ruoli (proposta in una riga per passo, conferma
  dell'utente); manuale DES: voci 11 e 23 chiuse + riga obsoleta della Proposta F7; voci §9.6 aperte 19, 21.
