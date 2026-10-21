@AGENTS.md

# Solo per Claude Code

- **Memoria** (`.claude/memory/`, collegata alla memoria automatica): la scrive solo una sessione Claude
  Code con modello Claude. Le informazioni prodotte da agenti non-Claude entrano in memoria solo dopo la
  verifica descritta sotto. Una sessione Claude Code avviata con un backend non-Claude (lanciatori
  `claude-local`/`claude-or`) non deve scrivere memoria.
- **Deleghe**: regole di modello e sforzo in memoria `feedback_model_effort_delegation` (tabella dei ruoli
  con primario e alternative). Gli agenti OpenCode sono elencati in `AGENTS.md`; si propongono sempre in
  una riga "compito -> agente, modello, motivo" e con conferma. I modelli Claude si usano solo qui, nel
  piano Pro: mai Opus/Sonnet via OpenRouter.
- **Preparare una delega OpenCode**: commit del piano, `git switch -c ai/oc-<tema>`, poi l'utente lancia
  il comando del ruolo nel repo (`/esegui <Proposta>` nella TUI di `oc`, oppure
  `oc run --command esegui <Proposta>`). I comandi usano SEMPRE il modello dell'agente (`-m` e' ignorato,
  verificato): per un modello alternativo `oc run --agent oc-developer -m <provider/modello> "<compito>"`. Per revisione e
  diagnosi (`/rivedi`, `/diagnosi`) il working tree non cambia. La sessione Claude non modifica il
  working tree finche' l'esecutore lavora.
- **Verificare un rapporto OpenCode** prima di integrare (mai fidarsi del solo rapporto):
  `git log --format='%h %s%n%(trailers:key=AI-Agent)' <base>..ai/oc-<tema>`, `git diff --stat`,
  `git status`, `git stash list` vuota; modello effettivo della sessione OpenCode (`oc session list`,
  `oc export <id>` -> `modelID`), da riportare nel messaggio di merge; leggere il codice nuovo principale; rieseguire suite e confronto
  con `tools/ai/verifica.sh` e confrontarli con l'esito atteso dal piano; nessun file riservato toccato.
  Solo dopo: merge nel branch di lavoro, aggiornamento della memoria, push su richiesta dell'utente.
