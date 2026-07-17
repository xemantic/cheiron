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

**M0 — reproduce a known step (hydrogen abstraction).** The loop runs end-to-end
with PySCF (unrestricted DFT) as the arbiter and confirms that an ethynyl radical
tool abstracting a hydrogen is thermodynamically favorable, with the right sign
and magnitude. Latest numbers and caveats live in
[`JOURNAL.md`](JOURNAL.md); raw records in
`experiments/m0_hydrogen_abstraction/results/ledger.jsonl`.

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

# tests (no quantum chemistry needed)
.venv/bin/pytest
```

## Journal & history

This is built in public: the narrative is in [`JOURNAL.md`](JOURNAL.md) and the
prompts steering the project are archived under `history/prompts/`.

## License

GNU AGPL-3.0-or-later — see [`LICENSE`](LICENSE).
