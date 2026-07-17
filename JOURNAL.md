# cheiron — project journal

A running, human-readable log of what the project decided, tried, learned, and
where it got stuck. Newest entries at the top. Failures are recorded here on
equal footing with successes — that is a design commitment of the project
(see `README.md`).

Machine-readable run records live in `experiments/*/results/` as JSONL; this
file is the narrative that ties them together.

---

## 2026-07-17 — M1 begins: approach-coordinate supersystem builder + rigid scan landed

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

First M1 increment: new module `cheiron.approach` (test-backed, 9 new tests,
17 total green).

- `build_supersystem(spec, d)` places the tool radical on the workpiece C–H
  axis — open valence aimed at the target H, collinear `C_w–H···Tool·` — at an
  exact approach distance `d`. Tests pin atom count, spin, realized distance,
  collinearity, orientation (tool's own H must face *away*), and clash
  behavior when rammed.
- `rigid_scan(spec, distances, config)` computes frozen-fragment single-point
  energies referenced to the separated fragments, and `barrier_kcal()` extracts
  the highest point above zero — the rigid estimate of the barrier under
  approach. Rigid first, deliberately: it upper-bounds the true barrier, so
  every later relaxed refinement has a number to beat.
- STO-3G smoke test (methyl + methane, d = 4.0/3.0/2.5 Å): profile is ~0 at
  4 Å and mildly attractive coming in (−0.9 kcal/mol at 2.5 Å) — sensible
  long-range behavior; the repulsive wall lives at shorter range.

Next: run the first real def2-SVP rigid scan on a known-favorable pair
(ethynyl + methane) into the ledger, then extract and publish its barrier.

## 2026-07-17 — M0 grid complete (12/12); ΔE is additive across tool and workpiece to 0.1 kcal/mol

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

The 2-tool × 6-workpiece grid is fully evaluated (UKS/PBE/def2-SVP, df, opt;
12 distinct candidates, 11 favorable, 1 unfavorable, 0 failures). The striking
result is how cleanly ΔE decomposes into a tool term plus a workpiece term.
Taking methane as the reference site, the workpiece offsets measured with each
tool independently:

| workpiece | offset via ethynyl | offset via methyl |
|-----------|-------------------:|------------------:|
| ethane | −5.5 | −5.4 |
| cyclobutane | −8.9 | −8.8 |
| butane | −9.7 | −9.6 |
| propane | −9.9 | −9.9 |
| isobutane | −13.7 | −13.6 |

Every offset agrees across tools to ≤0.1 kcal/mol — bond-energy additivity
reproduced from scratch by the loop's own numbers. Practical consequence for
M3-era screening: measuring a new *tool* against one reference workpiece (plus
this table) predicts its whole ladder, so tool-space search can spend ~1 QM
calc per tool instead of 6.

Honest miss: the previous entry predicted the methyl secondaries/tertiary at
ΔE ≈ −2…−7 kcal/mol; actuals ran −8.8…−13.6. Direction right, magnitude
underestimated — the CH4 C–H (BDE ~105) vs secondary/tertiary (~96–99) gap is
larger than the guess assumed.

**Grid exhausted → the frontier is now M1**: add a mechanical
approach-coordinate scan to the arbiter so survivors report a barrier under
approach, not just a reaction energy. Next iterations build it in small,
test-backed pieces (constrained-distance scan → barrier extraction → SCORE
feasibility axis).

## 2026-07-17 — First unfavorable result: the thermoneutral control comes back exactly 0

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

The loop reached the first methyl-tool candidate, and it behaved exactly as a
control should: `habs-methyl-methane` (CH3· + CH4 → CH4 + CH3·) is the identity
reaction, and the arbiter returned **ΔE = +0.0 kcal/mol → unfavorable**
(UKS/PBE/def2-SVP, df, opt; 40 s). This is the ledger's first non-favorable
record, which matters more than another favorable one would have: it shows the
pipeline discriminates rather than rubber-stamping, and the exact zero on a
by-symmetry-thermoneutral reaction is a clean internal consistency check of the
build→optimize→energy path (both sides optimized independently to the same
species).

Earlier the same loop evaluated `habs-ethynyl-cyclobutane`: **−35.1 kcal/mol,
favorable** — slotting just below butane-secondary (−35.9), consistent with
cyclobutane's C–H being marginally stronger than an acyclic secondary C–H
(ring strain largely retained in the radical).

Five methyl candidates remain pending; those against secondary/tertiary sites
should come out mildly favorable (ΔE ≈ −2…−7 kcal/mol) — a much finer
discrimination test than the ethynyl ladder.

## 2026-07-17 — Continuous operation is live; publishing to GitHub

**Who:** Claude (Fable 5) as harness, on Kazik's follow-up: *always push results to
GitHub, and set up a scheduled loop (or document how to start it via `/loop`).*

**What changed**

- The project is now **published to GitHub** (`github.com:xemantic/cheiron`) and
  every result is pushed. This is the "built in public" commitment made literal.
- Added **`scripts/autopilot.sh`** — one bounded, resumable *tick* of the loop:
  ensure the environment, evaluate the next N candidates, regenerate
  `results/summary.md`, then commit and push. It bootstraps its own venv from a
  fresh clone, so it runs anywhere. Proven end-to-end: an unattended tick
  evaluated two new candidates and pushed the result by itself.
- Expanded the candidate space so continuous running actually makes progress:
  a second, deliberately *weak* tool (methyl radical) to force the loop to
  discriminate good abstractors from poor ones, and secondary / ring-strained
  workpieces (propane, butane, cyclobutane).
- Documented both ways to run it continuously in
  [`docs/OPERATIONS.md`](docs/OPERATIONS.md): Claude Code `/loop` (reliable where
  the environment and push credentials already exist) and a scheduled cloud
  agent (unattended, but needs push credentials provisioned in the sandbox).

**New physics this session** (`UKS/PBE/def2-SVP`, ethynyl tool):

| workpiece | site | ΔE (kcal/mol) |
|-----------|------|--------------:|
| isobutane | tertiary | −39.9 |
| propane | secondary | −36.1 |
| butane | secondary | −35.9 |
| ethane | primary | −31.7 |
| methane | primary | −26.2 |

The secondary sites land neatly between primary and tertiary — the loop keeps
reproducing the C–H bond-strength ladder as it widens. Still favorability-only;
barriers (M1) are next.

**Operational note:** two def2-SVP candidates took ~12.5 min per tick, so ticks
should be small (batch 1–2) until a faster screening tier (xTB) is available.

**Requests to the human**

- To run the **scheduled cloud** loop unattended, the sandbox needs a git
  **deploy key / token with push access** to the repo — otherwise ticks compute
  but can't publish. The `/loop` path from an already-authenticated session
  needs nothing extra. (Also still open: a working GFN2-xTB, and a VETO-holding
  domain expert — see `docs/design/03-milestones.md`.)

---

## 2026-07-17 — Iteration 0: bootstrapping the loop

**Who:** Claude (Fable 5) as harness, on the mandate in
`history/prompts/0001-initial-prompt.md`.

**Goal for this iteration:** stand up a continuous-operation design loop and take
it around the track once with a real physics result, however small.

### What I decided

- **Scope.** The Feynman Grand Prize as a whole is out of reach and not the aim.
  We target *one sub-capability*: the ability to **design and computationally
  validate individual positional-assembly reaction steps** — a tooltip that,
  under positional control, performs a site-specific atomic operation that is
  thermodynamically favorable, kinetically accessible, and positionally
  selective. Rationale and boundaries in `docs/design/00-goal-and-scope.md`.

- **The loop.** Six stages — PROPOSE → BUILD → ARBITER → SCORE → SELECT/EVOLVE,
  with a human VETO gate — logging every candidate to an append-only ledger.
  Full description in `docs/design/01-loop-architecture.md`.

- **The arbiter.** Physics engines, tiered cheap→expensive so most candidates
  die cheaply and only survivors pay for accuracy. Details in
  `docs/design/02-arbiter.md`. For iteration 0 the arbiter is PySCF
  (DFT/HF, unrestricted for radicals) with `geometric` for geometry
  optimization.

- **First milestone, M0.** Reproduce the canonical first mechanosynthesis step:
  **hydrogen abstraction** by an ethynyl radical tooltip (`H–C≡C·`) pulling a
  hydrogen off a hydrogenated carbon workpiece. This is a known, checkable
  result (ethynyl's C–H bond is far stronger than a typical C–H, so abstraction
  should be strongly exothermic). If the loop can't confirm a textbook reaction,
  it isn't trustworthy on novel ones. Plan in `docs/design/03-milestones.md`.

### What I built

- Repository skeleton, Python package `cheiron`, docs, this journal, and the
  prompt archive.
- A working, isolated Python environment (no sudo on this host; bootstrapped
  `pip` by hand into a venv). Stack: NumPy, SciPy, ASE, PySCF, geometric.
- The loop stages as real, runnable code and an M0 experiment driver.

### What the physics said

The loop ran end-to-end, unattended, and **M0 succeeded** (project criterion
S1). The ethynyl radical tool abstracting a hydrogen is favorable for every
workpiece on the ladder, at `UKS/PBE/def2-SVP` (density-fitted, geometry
optimized):

| workpiece | C–H site | ΔE (kcal/mol) | expected¹ |
|-----------|----------|--------------:|----------:|
| methane   | primary   | **−26.2** | ~ −28 |
| ethane    | primary   | **−31.7** | ~ −32 |
| isobutane | tertiary  | **−39.9** | ~ −37 |

¹ Rough expectation from bond dissociation energies: ΔE ≈ BDE(workpiece C–H) −
BDE(acetylene C–H ≈ 133 kcal/mol), with workpiece BDEs ≈ 105 (methane), 101
(ethane), 96 (isobutane tertiary).

Two things make this convincing rather than lucky:

1. **Sign and magnitude are right** across all three, without any fitting.
2. **The ordering is physically correct** — the weaker the C–H bond being
   broken, the more exothermic the abstraction (isobutane's tertiary C–H is the
   weakest, so it's the most favorable). The loop recovered the C–H bond-strength
   ladder on its own. That is exactly the internal consistency we need before
   trusting the arbiter on novel steps.

Caveats kept with the number (see `docs/design/02-arbiter.md`): PBE/def2-SVP is a
screening-grade method; these are electronic energies without thermal/zero-point
corrections; and this is *favorability only* — the barrier under mechanical
approach (feasibility, M1) and site selectivity (M2) are not yet measured. A
downhill reaction can still be kinetically blocked; M1 addresses that next.

Raw records: `experiments/m0_hydrogen_abstraction/results/ledger.jsonl` (note it
also retains the earlier fast 6-31G methane screen, −25.4 kcal/mol, superseded
by the def2-SVP value — the append-only ledger keeps both).

### What I learned / would change

- The fragment-based reaction energy (four separately-optimized species) is a
  clean, fast favorability signal and the right thing for M0. It deliberately
  does **not** capture the positional/mechanical part of the step — that needs
  the tool-plus-workpiece supersystem and an approach scan, which is M1.
- `tblite`/GFN2-xTB would have made screening ~100× cheaper; its pip wheel is
  broken on this host (no compiled extension, no sudo/conda). Logged as an
  external help request. The small-basis DFT `--fast` preset is a serviceable
  stand-in for now.

### Requests to the human

Nothing blocking yet. Longer-term asks are collected in
`docs/design/03-milestones.md` under "External help wanted" (e.g. access to a
higher-accuracy compute budget, and a domain expert willing to hold the VETO
pen). None of these gate iteration 0.

---
