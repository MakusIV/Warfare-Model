#!/usr/bin/env bash
# SessionStart hook: warns Claude (via additionalContext) if the local branch
# is behind its upstream remote. Never pulls automatically.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../.." || exit 0

git fetch --quiet 2>/dev/null || exit 0

upstream=$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null) || exit 0
[ -z "$upstream" ] && exit 0

counts=$(git rev-list --left-right --count "HEAD...$upstream" 2>/dev/null) || exit 0
ahead=$(echo "$counts" | awk '{print $1}')
behind=$(echo "$counts" | awk '{print $2}')

if [ -n "$behind" ] && [ "$behind" -gt 0 ] 2>/dev/null; then
  branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
  msg="ATTENZIONE: il branch locale '$branch' e' indietro di $behind commit rispetto a '$upstream' (avanti di $ahead). Segnala questo all'utente e chiedi se vuole fare git pull prima di procedere con modifiche al codice; NON eseguire il pull automaticamente."
  jq -n --arg msg "$msg" '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $msg}}'
fi
exit 0
