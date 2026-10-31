---
name: reference-permessi-agenti-push
description: "Stato di fatto dei permessi degli agenti des-*/oc-* e di chi puo' committare/pushare; irrigidimento del 2026-10-31 (python3 -c, git branch, rete di sicurezza su push e cancellazione branch)"
metadata:
  node_type: memory
  type: reference
  originSessionId: 0468db0e-19b3-43df-a060-d82baa1e794b
  modified: 2026-10-31T09:29:31.826Z
---

Verifica del 2026-10-31 su `.claude/agents/`, `.opencode/agents/`, `opencode.json`, `.githooks/`, `AGENTS.md`, `CLAUDE.md`, settings, seguita dall'**irrigidimento chiesto dall'utente nello stesso giorno** (lacune `python3 -c` e `git branch` giudicate critiche).

## Agenti OpenCode (permessi imposti da `opencode.json` e dal frontmatter; vince l'ULTIMA regola che corrisponde)
- Push: `git push*` negato a TUTTI (anche prima di oggi, `oc-reviewer` compreso); dal 2026-10-31 in piu' la rete `*git push*` in fondo a ogni agente e in `opencode.json`, che blocca anche i comandi concatenati (`... && git push`).
- Cancellazione/rinomina di branch: rete `*git branch -d*`, `-D`, `-m`, `-M`, `--delete`, `--move` negata in tutti gli agenti e in `opencode.json`.
- `oc-reviewer`: `git branch*` (che permetteva anche creare/cancellare branch) sostituito dalle sole forme di lettura esatte: `--show-current`, `--list`, `-a`, `-r`, `-v`, `-vv`.
- `python3 -c`: tolto a `oc-planner` e `oc-debugger` (le sonde si fanno con `python3 -m unittest` mirati; prompt aggiornati); a `oc-developer` resta SOLO la forma `python3 -c "import py_compile; py_compile.compile(*doraise=True)"` (virgolette doppie o singole). Motivo: `*python3 -c*` permetteva di lanciare qualunque cosa (es. `subprocess` con `git push`) aggirando i `deny` sui comandi.
- Commit consentito solo a `oc-developer` e `oc-writer` (branch `ai/*`); gli altri non committano. `oc-helper` scrive solo su conferma.
- File riservati (`.claude/`, `CLAUDE.md`, `AGENTS.md`, `.opencode/`, `opencode.json`, `.githooks/`, `tools/ai/`, fotografia) negati in scrittura; hook `pre-commit` (attivo con `MULTILLM_AGENT` e `core.hooksPath=.githooks`) rifiuta commit fuori da `ai/*` o sui file riservati; `commit-msg` aggiunge `AI-Agent:`.
- Merge, memoria e stato del progetto: solo la sessione principale Claude dopo la verifica.

**Come controllare i permessi effettivi senza costi:** `opencode debug agent <nome>` stampa il ruleset risolto (JSON, `permission: bash`); l'ordine conta, vince l'ultima corrispondenza. Nel ruleset c'e' anche una regola globale `allow git branch*` (viene da `~/.config/opencode`, non dal progetto): non pericolosa perche' i `deny` degli agenti vengono dopo. La simulazione del 2026-10-31 (matcher scritto da me, approssimato) ha dato: `git branch -D`, `git branch nuovo`, `git push`, `git status && git push`, `python3 -c "...subprocess..."` negati; `py_compile`, `git branch --show-current/--list/-a/-vv`, `python3 -m unittest` consentiti. Non provato con un agente reale.

## Agenti Claude (`des-*`)
- `des-developer`, `des-planner`, `des-manual-writer`: niente commit/push, ma SOLO come istruzione nel testo (strumenti non limitati dal sistema). Il `des-manual-writer` ha usato `sed -i` e script Python di modifica contro l'istruzione (solo sul proprio file). Non irrigidito.

## Sessione principale (Claude)
- Regola scritta: `CLAUDE.md` «push su richiesta dell'utente». Nessuna regola riserva il push solo all'umano; `.claude/settings.local.json` (ignorato da git, `~/.gitignore_global`) ha `Bash(git push *)` tra i consentiti. L'utente ha chiesto esplicitamente il push il 2026-10-31.
- Il «classificatore dei permessi» che avrebbe bloccato il push (sessione 2026-10-29) non e' nei settings del progetto; `autoMode.soft_deny` globale ha una regola sul push ma per un altro repo (`WIKI_LLM_INVESTOR`). Se il push e' bloccato, l'utente usa `! git push`.

**How to apply:** pushare solo su richiesta esplicita dell'utente. Se si riabilita `python3 -c` per un agente, ricordare che e' un varco (esecuzione arbitraria). Vedi [[feedback-model-effort-delegation]].
