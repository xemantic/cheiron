# cheiron

An autonomous design loop for positional molecular assembly, built in public. Looping coding agents as harness, physics engines as arbiter, domain experts with veto. Aimed at one sub-capability of the unclaimed Feynman Grand Prize — not at winning it. Failures published alongside results.

## What this is

`cheiron` proposes candidate **positional-assembly reaction steps** — a tooltip
that, under positional control, makes or breaks a specific bond at a specific
site — and submits each to physics engines that judge whether it is:

- **favorable** — thermodynamically downhill,
- **feasible** — reachable over a low-enough barrier under mechanical approach,
- **selective** — hitting the intended site only, with the tool surviving.

The one sub-capability we own is *designing and computationally validating those
steps*. We are not building hardware and not trying to win the prize. See
[`docs/design/00-goal-and-scope.md`](docs/design/00-goal-and-scope.md).

## The loop

```
PROPOSE ─▶ BUILD ─▶ ARBITER ─▶ SCORE ─▶ SELECT/EVOLVE ─┐
   ▲            (physics engine)                        │
   └──────────────── VETO (human) ◀─────────────────────┘
        every candidate ─▶ append-only ledger (successes and failures alike)
```

Architecture: [`docs/design/01-loop-architecture.md`](docs/design/01-loop-architecture.md) ·
Arbiter: [`docs/design/02-arbiter.md`](docs/design/02-arbiter.md) ·
Milestones: [`docs/design/03-milestones.md`](docs/design/03-milestones.md)

## Status

**M0–M2 complete; M3 (search, not enumeration) in progress.** Highlights, all
produced unattended by the loop and pushed as they happened:

- **Favorability solved for the family**: 40/40 tool×workpiece candidates
  measured (5 tools × 8 workpieces, UKS/PBE/def2-SVP), zero unresolved
  failures; reaction energies decompose exactly (Hess's law), so the additive
  model now predicts and the arbiter only verifies.
- **Feasibility is per-tool-family**: relaxed approach scans give a
  hybrid-grade barrier map that tracks literature activation energies
  (hydroxyl 1.8 vs exp ≈1.7; methyl 10.6; amino 8.4; vinyl 6.7; ethynyl 0) —
  and ΔE alone cannot rank tools kinetically.
- **Selectivity is positional, not chemical** (the project premise, measured):
  on adamantane — the diamondoid surface model — the thermodynamic site margin
  is 1.14 kcal/mol and the kinetic margin under clamped positional control is
  zero. Whichever C–H the tool is held over reacts.
- **First step datasheet** (criterion S2, VETO-pending):
  [`docs/datasheets/habs-adamantane.md`](docs/datasheets/habs-adamantane.md).
- **Handle-mounted tools work**: an ethynyl tip on an adamantyl frame costs
  only 0.8 kcal/mol of driving force vs the free radical — cheap surrogate
  screening is predictive of realistic tooltips.
- **A second operation (M4): radical addition.** The loop is not hardwired to
  hydrogen abstraction — it now also does a *bond-forming* step (a radical
  adding across a C=C), characterized to the same depth: favorability
  (validated vs known ΔE), approximate additivity, a **certified** PBE0 barrier
  (methyl+ethylene 3.84 kcal/mol), and anti-Markovnikov regioselectivity
  (3.8 kcal/mol). Two findings only two operations could give: **tool ranking is
  operation-dependent** (abstraction strength doesn't predict addition
  strength), and **abstraction needs the machine to pick the site while
  addition has real intrinsic regiochemistry** to lean on.

The narrative, including every failure and correction, lives in
[`JOURNAL.md`](JOURNAL.md); raw append-only records in
`experiments/m0_hydrogen_abstraction/results/` (abstraction) and
`experiments/m1_radical_addition/results/` (addition).

## Running it

```bash
# one-time environment (no system packages required)
python3 -m venv .venv --without-pip
curl -sS https://bootstrap.pypa.io/get-pip.py | .venv/bin/python
.venv/bin/pip install -e .

# fast pipeline smoke test (rough, small basis)
.venv/bin/python experiments/m0_hydrogen_abstraction/run.py --workpieces methane --fast

# the M0 result run
.venv/bin/python experiments/m0_hydrogen_abstraction/run.py --workpieces isobutane

# a second-operation run: radical addition (M4)
.venv/bin/python experiments/m1_radical_addition/run_addition.py --tool ethynyl --substrate C2H4

# tests (no quantum chemistry needed)
.venv/bin/pytest
```

## Journal & history

This is built in public: the narrative is in [`JOURNAL.md`](JOURNAL.md) and the
prompts steering the project are archived under `history/prompts/`.

## License

GNU AGPL-3.0-or-later — see [`LICENSE`](LICENSE).
