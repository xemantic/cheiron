#!/usr/bin/env bash
# cheiron autopilot — one bounded tick of continuous operation.
#
# Ensures the environment exists, evaluates the next few not-yet-done candidates,
# regenerates the ledger summary, and commits + pushes the result. Idempotent and
# resumable: if everything is already evaluated, it does nothing and exits 0.
#
# Designed to be driven repeatedly by a scheduler (Claude Code `/loop`, cron, or a
# scheduled cloud agent). Each invocation is a small, safe unit of progress.
#
# Usage:   scripts/autopilot.sh [BATCH_SIZE]
#   BATCH_SIZE  candidates to evaluate this tick (default: env CHEIRON_BATCH or 2)
#
# Env:
#   CHEIRON_BATCH   default batch size
#   CHEIRON_NOPUSH  if set to 1, commit but do not push (for local testing)

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"

BATCH="${1:-${CHEIRON_BATCH:-2}}"
VENV="$REPO/.venv"
PY="$VENV/bin/python"
LEDGER="$REPO/experiments/m0_hydrogen_abstraction/results/ledger.jsonl"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-4}"

log() { printf '[autopilot %s] %s\n' "$(date -u +%H:%M:%S)" "$*"; }

# 1. Ensure the Python environment (works from a fresh clone; no sudo needed).
if [[ ! -x "$PY" ]]; then
  log "bootstrapping virtualenv (no ensurepip on this host)"
  python3 -m venv "$VENV" --without-pip
  "$PY" - <<'PYEOF'
import urllib.request
urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", "/tmp/get-pip.py")
PYEOF
  "$PY" /tmp/get-pip.py >/dev/null
  "$PY" -m pip install --quiet -e "$REPO"
fi

# 2. Sync with the remote so we append to the latest ledger, not a stale one.
if git remote get-url origin >/dev/null 2>&1; then
  log "pulling latest"
  git pull --rebase --autostash origin main || log "pull failed (continuing offline)"
fi

# 3. One bounded tick of the loop.
log "evaluating up to $BATCH candidate(s)"
"$PY" experiments/m0_hydrogen_abstraction/run.py --limit "$BATCH"

# 4. Regenerate the committable summary from the ledger.
"$PY" scripts/summarize.py "$LEDGER"

# 5. Commit + push if anything changed.
git add -A
if git diff --cached --quiet; then
  log "no changes this tick — nothing to publish"
  exit 0
fi

n_usable="$("$PY" - "$LEDGER" <<'PYEOF'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1])]
latest = {}
for r in rows:
    latest[r["spec"]["id"]] = r
usable = [r for r in latest.values()
          if r.get("fitness") and r["fitness"].get("valid")]
print(len(usable))
PYEOF
)"

git commit -q -m "autopilot: evaluate next batch (${n_usable} usable candidates)

Automated tick of the cheiron loop. See experiments/*/results/summary.md.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
log "committed"

if [[ "${CHEIRON_NOPUSH:-0}" != "1" ]] && git remote get-url origin >/dev/null 2>&1; then
  git push origin main && log "pushed" || log "push failed (will retry next tick)"
fi
