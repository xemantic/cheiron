# Operating the loop continuously

The loop is built to run in bounded, resumable **ticks**. One tick =
`scripts/autopilot.sh [BATCH_SIZE]`, which:

1. ensures the Python environment exists (bootstraps a venv from scratch if not —
   no sudo required),
2. pulls the latest `main` so it appends to the current ledger,
3. evaluates the next `BATCH_SIZE` not-yet-done candidates through the loop,
4. regenerates `experiments/*/results/summary.md` from the ledger,
5. **commits and pushes** the result.

If everything is already evaluated, a tick does nothing and exits cleanly. This
makes it safe to call on any schedule.

```bash
# a single tick by hand (evaluate 3 candidates, publish)
bash scripts/autopilot.sh 3

# commit but don't push (local testing)
CHEIRON_NOPUSH=1 bash scripts/autopilot.sh 1
```

## Option A — Claude Code `/loop` (recommended; runs where the env already works)

From a **fresh Claude Code session in this repo**, start a self-repeating loop:

```
/loop 20m Run one cheiron autopilot tick: execute `bash scripts/autopilot.sh 3`
from the repo root. If the batch produced anything notable (a new most-favorable
step, an unfavorable or failed step, or an arbiter error), append a short dated
bullet to JOURNAL.md and commit + push that too. If nothing was pending, stop
quietly.
```

- `20m` is the interval — tune it (`10m`, `1h`, …). Omit the interval entirely
  (`/loop Run one cheiron autopilot tick …`) to let the model self-pace.
- This form uses the agent to add journal narrative on top of the mechanical
  script. For a pure mechanical loop, use: `/loop 20m bash scripts/autopilot.sh 3`.
- The session must stay open for the loop to keep firing. Best run from an
  environment where the scientific stack and `git push` credentials already work
  (e.g. the machine this project was bootstrapped on).

## Option B — scheduled cloud agent (unattended, no open session)

A cron-scheduled routine runs ticks without anyone present. Set one up with the
`/schedule` command, e.g. "run `bash scripts/autopilot.sh 2` in the cheiron repo
every 2 hours." Caveats to verify once, because a cloud sandbox starts clean:

- **git push credentials.** The sandbox needs a deploy key / token with push
  access to `github.com:xemantic/cheiron`, or the tick will evaluate but fail to
  publish (the script logs this and continues). This is the one thing that may
  need setting up — see `docs/design/03-milestones.md` → External help wanted.
- **environment build time.** The first tick in a fresh sandbox installs the
  scientific stack (PySCF etc.), a few minutes; later ticks in the same sandbox
  reuse it.

## What a tick actually advances

Right now the enumerative proposer sweeps a fixed tool × workpiece grid, so ticks
chew through that grid until it is exhausted, publishing each result (favorable
or not). Once the grid is done, continuous progress requires new work — the next
milestones add it: barriers (M1), selectivity (M2), and search-based proposers
that generate candidates instead of enumerating them (M3). See
`docs/design/03-milestones.md`.
