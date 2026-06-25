#!/usr/bin/env bash
# Measure REAL token cost: /sh:architecture-panel vs /sh:analyze --focus architecture.
# Replaces the estimates from the 2026-06-25 session with measured output_tokens.
#
# Usage:  ./scripts/measure-panel-vs-analyze.sh [TARGET_FILE]
#   TARGET_FILE defaults to a small fixed sample so runs are comparable.
#
# Reads usage from `claude -p --output-format json` (.usage.output_tokens /
# .input_tokens / .cache_read_input_tokens). Prices below are $/1M tokens from
# the claude-api skill (2026-06-04 cache): Opus 4.8 = 5/25, Sonnet 4.6 = 3/15.
#
# NOTE: run this in a FRESH session — it spawns its own `claude -p` subprocesses,
# so it does not need (and should not inherit) a heavy parent context.
set -euo pipefail

TARGET="${1:-$HOME/projects/20_agentflow/.claude/skills/sh-analyze/SKILL.md}"
OUT_DIR="$HOME/projects/20_agentflow/.tmp/measure-$(date +%s)"
mkdir -p "$OUT_DIR"

run() {  # name  model  prompt
  local name="$1" model="$2" prompt="$3" f="$OUT_DIR/$1.json"
  echo "→ $name ($model) ..." >&2
  # --model overrides session model; -p is non-interactive; capture JSON usage.
  claude -p "$prompt" --model "$model" --output-format json > "$f" 2>"$OUT_DIR/$name.err" || {
    echo "  FAILED — see $OUT_DIR/$name.err" >&2; return 1; }
  python3 - "$f" "$name" "$model" <<'PY'
import json,sys
f,name,model=sys.argv[1],sys.argv[2],sys.argv[3]
d=json.load(open(f))
u=d.get("usage",{})
out=u.get("output_tokens",0)
inp=u.get("input_tokens",0)
cr=u.get("cache_read_input_tokens",0)
price={"opus":(5,25),"claude-opus-4-8":(5,25),"sonnet":(3,15),"claude-sonnet-4-6":(3,15)}
pi,po=price.get(model,(5,25))
cost=(inp*pi + out*po)/1_000_000
print(f"{name:34s} in={inp:>7} cache_read={cr:>7} out={out:>7}  ${cost:.4f}/run  ${cost*50:.2f}/50")
PY
}

echo "Target: $TARGET" >&2
echo "Results -> $OUT_DIR" >&2
echo >&2

# Same task, three configurations. Silent is now the panel default (no flag needed);
# add --verbose to measure the old behavior for comparison.
run "panel_verbose_opus" "claude-opus-4-8" \
    "/sh:architecture-panel @$TARGET --verbose"
run "panel_silent_opus"  "claude-opus-4-8" \
    "/sh:architecture-panel @$TARGET"
run "analyze_opus"       "claude-opus-4-8" \
    "/sh:analyze --focus architecture $TARGET"
run "analyze_sonnet"     "claude-sonnet-4-6" \
    "/sh:analyze --focus architecture $TARGET"

echo >&2
echo "Done. Raw JSON in $OUT_DIR — the \$/50 column is the measured answer to" >&2
echo "'how much cheaper for 50 runs', replacing the session's estimates." >&2
