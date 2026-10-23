#!/usr/bin/env bash
# Delega a OpenCode con i fornitori OpenRouter aggiornati ai prezzi del momento.
#
#   bash tools/ai/oc-delega.sh --command esegui "<compito>"      equivale a `oc run ...`, preceduto dall'aggiornamento
#   bash tools/ai/oc-delega.sh --agent oc-developer "<compito>"
#
# Prima riscrive `provider.openrouter.models.<0813>` di opencode.json (order, max_price, cost) con
# tools/ai/prezzi_fornitori.py --apply; se l'aggiornamento fallisce (rete) si prosegue con la configurazione
# esistente, protetta da max_price. Dalla TUI di `oc` (`/esegui`) lo script non gira: lanciarlo a mano prima di `oc`:
#   python3 tools/ai/prezzi_fornitori.py --apply
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT" || exit 1

if ! python3 tools/ai/prezzi_fornitori.py --apply | sed -n '/^Tolleranza/,$p'; then
  echo "ATTENZIONE: aggiornamento dei fornitori non riuscito, uso opencode.json com'e'." >&2
fi
git status --short opencode.json
exec oc run "$@"
