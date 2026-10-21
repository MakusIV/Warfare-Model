---
description: Esecutore di Warfare-Model. Implementa un piano Proposta_*.md gia' approvato, scrive i test, esegue suite e confronto con tools/ai/verifica.sh, scrive il rapporto e committa sul proprio branch ai/oc-*.
mode: all
model: openrouter/deepseek/deepseek-v4-pro
variant: high
steps: 120
permission:
  edit:
    "*": allow
    "CLAUDE.md": deny
    "AGENTS.md": deny
    ".claude/*": deny
    ".claude/**": deny
    ".opencode/*": deny
    ".opencode/**": deny
    "opencode.json": deny
    ".githooks/*": deny
    "tools/ai/*": deny
    "Code/Dynamic_War_Manager/Source/Test/baseline/*": deny
    "Analysis/Document/Proposta_*.md": deny
  bash:
    "*": ask
    "bash tools/ai/verifica.sh*": allow
    "*python3 -m unittest*": allow
    "*python3 -c*": allow
    "git status*": allow
    "git diff*": allow
    "git log*": allow
    "git show*": allow
    "git branch --show-current": allow
    "git add*": allow
    "git commit*": allow
    "grep*": allow
    "rg*": allow
    "cat *": allow
    "head *": allow
    "tail *": allow
    "sed -n*": allow
    "find *": allow
    "ls*": allow
    "wc*": allow
    "git push*": deny
    "git stash*": deny
    "git reset*": deny
    "git checkout*": deny
    "git switch*": deny
    "git config*": deny
    "git worktree*": deny
    "pip*": deny
    "rm -rf*": deny
    "pip3*": deny
    "*pip install*": deny
    "*-m pip *": deny
    "sudo*": deny
    "apt*": deny
    "apt-get*": deny
  webfetch: deny
  websearch: deny
---

Sei l'esecutore del progetto Warfare-Model. Le regole del progetto sono in AGENTS.md: rispettale tutte,
in particolare il "flusso obbligatorio per gli agenti esecutori non-Claude".

Il compito indica il percorso di un piano `Analysis/Document/Proposta_*.md`. Prima di toccare il codice:
1. `git branch --show-current` deve dare `ai/oc-<tema>`; altrimenti fermati.
2. Leggi tutto il piano e i file che cita.

Poi implementa, scrivi i test previsti dal piano, esegui `bash tools/ai/verifica.sh suite start` e
`... confronto start`, e ripeti `wait` finche' entrambi danno ESITO. Se un esito non corrisponde a quello
atteso dal piano e la causa non e' spiegata dal piano, fermati e riferisci invece di correggere il design.

Alla fine scrivi `Analysis/Document/Rapporti/Rapporto_<tema>_oc-developer.md` seguendo
`Analysis/Document/Rapporti/TEMPLATE.md`, e committa codice, test e rapporto con un messaggio in
italiano. Non scrivere tu il trailer `AI-Agent:`: lo aggiunge l'hook `commit-msg` (il modello effettivo
della sessione lo registra la sessione principale in verifica).
