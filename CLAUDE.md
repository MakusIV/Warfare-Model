@AGENTS.md

# Solo per Claude Code

- **Memoria** (`.claude/memory/`, collegata alla memoria automatica): la scrive solo una sessione Claude
  Code con modello Claude. Le informazioni prodotte da agenti non-Claude entrano in memoria solo dopo la
  verifica descritta sotto. Una sessione Claude Code avviata con un backend non-Claude (lanciatori
  `claude-local`/`claude-or`) non deve scrivere memoria.
- **Deleghe**: regole di modello e sforzo in memoria `feedback_model_effort_delegation`. In piu' esiste la
  corsia OpenCode: per eseguire un piano `Proposta_*.md` gia' approvato si puo' proporre all'utente
  `oc-developer` (modello cloud economico, OpenRouter) o `oc-helper` (modello locale su Game_PC, solo
  compiti meccanici), sempre in una riga "compito -> agente, modello, motivo" e con conferma.
- **Preparare una delega OpenCode**: commit del piano, `git switch -c ai/oc-<tema>`, poi l'utente lancia
  `oc --agent oc-developer` nel repo (oppure `oc run --agent oc-developer "<compito>"`). La sessione
  Claude non modifica il working tree finche' l'esecutore lavora.
- **Verificare un rapporto OpenCode** prima di integrare (mai fidarsi del solo rapporto):
  `git log --format='%h %s%n%(trailers:key=AI-Agent)' <base>..ai/oc-<tema>`, `git diff --stat`,
  `git status`, `git stash list` vuota; leggere il codice nuovo principale; rieseguire suite e confronto
  con `tools/ai/verifica.sh` e confrontarli con l'esito atteso dal piano; nessun file riservato toccato.
  Solo dopo: merge nel branch di lavoro, aggiornamento della memoria, push su richiesta dell'utente.
