#!/usr/bin/env bash
# Suite completa e confronto con la fotografia, eseguiti in background con esito leggibile a tratti.
# Pensato per gli agenti (Claude Code, OpenCode con modelli cloud o locali): nessun comando dura piu'
# di ~2 minuti, quindi nessun limite di tempo dello strumento bash interrompe una suite da ~10 minuti.
#
#   bash tools/ai/verifica.sh suite start       avvia la suite completa
#   bash tools/ai/verifica.sh suite wait        attende fino a 100 s; stampa IN CORSO oppure l'esito
#   bash tools/ai/verifica.sh confronto start   avvia il confronto con la fotografia (non la installa mai)
#   bash tools/ai/verifica.sh confronto wait
#   bash tools/ai/verifica.sh <job> status      come wait, senza attendere
#
# Log e catture in .ai-run/ (ignorata da git). Ripetere `wait` finche' non compare ESITO.
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT" || exit 1
RUN="$ROOT/.ai-run"; mkdir -p "$RUN"
JOB="${1:-}"; ACT="${2:-status}"; WAIT_MAX="${3:-100}"

# Interprete della macchina: direnv (ProArt) > venv funzionante > python3 di sistema (osboxes)
if   [ -x .direnv/python-3.12/bin/python3 ]; then PY=.direnv/python-3.12/bin/python3
elif [ -x venv/bin/python3 ] && venv/bin/python3 -c "import numpy" 2>/dev/null; then PY=venv/bin/python3
else PY=python3; fi

case "$JOB" in
  suite)     CMD=("$PY" -m unittest discover -s Code/Dynamic_War_Manager/Source/Test -p "Test_*.py") ;;
  confronto) CMD=("$PY" -m Code.Dynamic_War_Manager.Source.Test.Scenario_Baseline --compare
                  Code/Dynamic_War_Manager/Source/Test/baseline/scenario_baseline.json
                  --save "$RUN/confronto_capture.json" --quiet --summary) ;;
  *) echo "uso: bash tools/ai/verifica.sh suite|confronto start|wait|status"; exit 2 ;;
esac
LOG="$RUN/$JOB.log"; PID="$RUN/$JOB.pid"; RC="$RUN/$JOB.rc"; T0="$RUN/$JOB.start"

running() { [ -f "$PID" ] && kill -0 "$(cat "$PID")" 2>/dev/null; }

report() {
  local rc; rc="$(cat "$RC" 2>/dev/null || echo '?')"
  echo "ESITO $JOB: exit code $rc · interprete $PY · log $LOG"
  if [ "$JOB" = suite ]; then
    grep -E '^Ran [0-9]+ tests' "$LOG" | tail -1
    grep -E '^(OK|FAILED)' "$LOG" | tail -1
    # solo i fallimenti di unittest ("FAIL: test_x (modulo.Classe...)"), non le righe di log "ERROR:<logger>:"
    grep -E '^(FAIL|ERROR): [A-Za-z_][A-Za-z0-9_]* \(' "$LOG" | head -30
  else
    # solo le righe di riepilogo (UNCHANGED/CHANGED/NEW (n): ..., compared N runs: ...), accorciate:
    # l'elenco completo delle esecuzioni e' nel log e consumerebbe troppo contesto
    local summ; summ="$(grep -E '^([A-Z]{3,}[A-Z_ ]* \([0-9]+\)|compared [0-9]+ runs)' "$LOG" | cut -c1-300)"
    if [ -n "$summ" ]; then echo "$summ"; else tail -n 5 "$LOG" | cut -c1-300; fi
  fi
}

case "$ACT" in
  start)
    if running; then echo "$JOB gia' in corso (pid $(cat "$PID")): usare wait"; exit 0; fi
    rm -f "$RC"; date "+%Y-%m-%d %H:%M:%S" > "$T0"
    echo "avvio $JOB: ${CMD[*]}" > "$LOG"
    # setsid + nohup: processo in una sessione propria, cosi' sopravvive alla chiusura dello strumento
    # bash dell'agente (OpenCode termina i processi figli quando il comando finisce)
    nohup setsid bash -c '"${@:3}" >> "$1" 2>&1; echo $? > "$2"' _ "$LOG" "$RC" "${CMD[@]}" >/dev/null 2>&1 &
    echo $! > "$PID"
    echo "$JOB avviato (pid $(cat "$PID")). Ora: bash tools/ai/verifica.sh $JOB wait"
    ;;
  wait|status)
    [ "$ACT" = status ] && WAIT_MAX=0
    t=0
    while running && [ "$t" -lt "$WAIT_MAX" ]; do sleep 5; t=$((t+5)); done
    if running; then
      echo "IN CORSO $JOB (avviato $(cat "$T0" 2>/dev/null)); ripetere: bash tools/ai/verifica.sh $JOB wait"
    elif [ -f "$RC" ]; then report
    elif [ -f "$PID" ]; then echo "INTERROTTO $JOB: il processo e' terminato senza esito; rilanciare: bash tools/ai/verifica.sh $JOB start"
    else echo "$JOB mai avviato: bash tools/ai/verifica.sh $JOB start"; fi
    ;;
  *) echo "azione sconosciuta: $ACT"; exit 2 ;;
esac
