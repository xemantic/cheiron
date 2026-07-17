# 01 — Loop architecture

The continuous-operation loop is the core deliverable. It is a pipeline of six
stages with a human veto gate, wrapped in an outer controller that runs it
forever (or until a stop condition), logging every candidate to an append-only
ledger.

```
        ┌──────────────────────── cheiron loop ───────────────────────────┐
        │                                                                  │
   ┌────────┐   ┌────────┐   ┌─────────┐   ┌────────┐   ┌──────────────┐
   │PROPOSE │──▶│ BUILD  │──▶│ ARBITER │──▶│ SCORE  │──▶│ SELECT/EVOLVE │──┐
   │        │   │geometry│   │(physics)│   │fitness │   │  population    │  │
   └────────┘   └────────┘   └─────────┘   └────────┘   └──────────────┘  │
        ▲                                       │                          │
        │                                       ▼                          │
        │                                  ┌─────────┐                     │
        └──────────────────────────────────│  VETO   │◀────────────────────┘
             feedback / new proposals       │ (human) │
                                            └─────────┘
                              every candidate ─▶ LEDGER (append-only JSONL)
```

## Stages

### 1. PROPOSE
Emits candidate designs. A candidate is a small, serializable spec:
`(tooltip id + params, workpiece id + params, approach geometry, intended
operation)`. Proposers are pluggable:

- **enumerative** — sweep a defined grid of tools × workpieces × geometries
  (used for M0; deterministic and reproducible).
- **evolutionary** — mutate/recombine the current population's survivors.
- **agent** — an LLM/agent proposes chemically-motivated candidates from the
  ledger's history (added once the cheaper proposers plateau).

A proposer never touches physics; it only produces specs. This keeps proposal
strategy orthogonal to evaluation.

### 2. BUILD
Turns a spec into a concrete 3-D structure (an `ase.Atoms`): places the tooltip
and workpiece in the requested approach geometry, sets total charge and spin
multiplicity (radicals matter here), and flags which atoms are the reacting
pair. Pure geometry; no energy is computed. A build can fail (steric
impossibility) — that is a legitimate, logged outcome.

### 3. ARBITER
The physics engine(s). Takes a built structure and returns measurements:
relaxed geometry, energies of reactant/product states, reaction energy, and
(for survivors) an approach-coordinate scan and/or barrier. Tiered so cheap
methods filter before expensive ones ever run. Fully described in
`02-arbiter.md`. The arbiter is deliberately the only stage allowed to be slow.

### 4. SCORE
Maps arbiter measurements to a fitness record: the three axes from
`00-goal-and-scope.md` — **favorability**, **feasibility**, **selectivity** —
plus a **tool-integrity** penalty. Kept as separate components (not prematurely
collapsed to one number) so SELECT can apply different pressures and so humans
can see *why* a candidate scored as it did. `score.py` documents the exact
formulas; they are intended to be revised as we learn.

### 5. SELECT / EVOLVE
Ranks the population, keeps survivors, retires the rest (retired ≠ deleted — see
LEDGER), and hands survivors back to PROPOSE as parents. Also decides which
survivors are *promoted* — escalated to a higher arbiter tier for confirmation.

### 6. VETO (human gate)
Before any candidate is marked `accepted` (eligible to become a published
reaction-step datasheet), a human domain expert may reject it or the whole
direction. The gate is asynchronous: the loop keeps running and simply cannot
stamp `accepted` without a recorded human decision. Vetoes are logged with a
reason and become negative training signal for the proposers.

## The ledger

Every candidate that enters the loop gets one immutable JSONL record appended to
`experiments/<milestone>/results/ledger.jsonl`, capturing: id, provenance
(parent ids, proposer, generation), the full spec, build outcome, arbiter
measurements (with method + tier), the score components, select decision, and
any veto. Nothing is ever mutated or deleted — corrections are new records that
supersede old ones by id. This is what makes "failures published alongside
results" concrete and auditable.

## The outer controller

`loop.py` runs:

```
initialize population from PROPOSE(seed)
while not stop_condition:
    for spec in current_batch:
        atoms  = BUILD(spec)          # may fail → log, continue
        meas   = ARBITER(atoms, tier) # tiered
        score  = SCORE(meas)
        LEDGER.append(record)
    survivors = SELECT(population)
    apply any pending human VETOs
    current_batch = PROPOSE(survivors)   # next generation
    checkpoint()                         # resumable
```

Design properties we hold ourselves to:

- **Resumable** — state is the ledger plus a small checkpoint; a killed process
  restarts without losing work.
- **Deterministic where it can be** — seeds are recorded; the enumerative
  proposer + a fixed arbiter tier reproduce bit-for-bit.
- **Interruptible** — a batch is the unit of progress; stopping between batches
  is always safe.
- **Cheap-first** — no candidate reaches an expensive tier without surviving the
  cheap ones.

## Autonomy and cadence

"Continuous operation" is realized two ways, both supported:

- **In-process:** the outer `while` loop above, for a bounded run.
- **Scheduled:** an external scheduler (cron / Claude Code `/loop`) re-invokes
  the harness to run the next batch, review the ledger, update the journal, and
  raise any `Requests to the human`. This is how the project makes progress
  across sessions without a human babysitting it. See `03-milestones.md`.
