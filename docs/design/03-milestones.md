# 03 — Milestones and roadmap

Milestones are deliberately small and each ends in something checkable. The loop
is the constant; the milestones are what we point it at.

## M0 — Hydrogen abstraction (reproduce a known step) · **in progress**

**Claim to test:** the loop, unattended, confirms that an **ethynyl radical
tooltip** (`H–C≡C·`) abstracting a hydrogen from a hydrogenated carbon workpiece
is thermodynamically **favorable**, with the right sign and roughly the right
magnitude.

**Why this step:** it is the textbook first move of mechanosynthesis and its
answer is known independently of any simulation — the C–H bond formed in
acetylene (`H–C≡C–H`, ~132 kcal/mol) is much stronger than the C–H bond broken
in a typical hydrocarbon (~96–105 kcal/mol), so abstraction should release on
the order of 30–40 kcal/mol. A loop that can't recover this shouldn't be trusted
on anything novel. (Sign and order of magnitude are the bar; exact numbers
depend on method and workpiece.)

**Workpiece ladder (cheap → realistic):**
1. methane `CH4` (primary C–H) — smallest possible smoke test of the pipeline.
2. isobutane `(CH3)3C–H` (tertiary C–H) — the chemically relevant weak C–H.
3. adamantane C–H — a rigid cage that better models a diamond surface site.

**Done when:** the ledger contains, for at least the isobutane case, a
reaction-energy record with `ΔE < 0` of the expected order, produced by the loop
without hand-holding, and the journal's M0 entry reports the number with its
method and caveats. That satisfies project criterion **S1**.

## M1 — Feasibility, not just favorability · **in progress**

Add the approach-coordinate scan to the arbiter so survivors report a **barrier
under mechanical approach**, not only a reaction energy. Distinguish steps that
are downhill-but-blocked from steps that actually proceed under positional load.

Status: `cheiron.approach` builds the collinear `C–H···Tool·` supersystem at a
controlled approach distance and runs a **rigid scan** (frozen fragments,
single-point energies, referenced to the separated fragments) with a
`barrier_kcal()` extraction. Geometry logic is test-covered; the first real
def2-SVP scan on a known-favorable pair is next, then a constrained *relaxed*
scan, then wiring the barrier into SCORE as the feasibility axis.

## M2 — Selectivity and tool integrity

Introduce workpieces with multiple inequivalent C–H sites and score whether the
tool geometry selects the intended one. Add the tool-integrity check as a hard
gate. First candidates for a *novel* datasheet (criterion **S2**) come from
here.

## M3 — Search, not enumeration

Turn on the evolutionary and agent proposers; let the loop explore the
tool/workpiece space rather than a hand-written grid, seeded by everything the
ledger has learned. Publish the negative results this generates (criterion
**S3**).

## Cross-cutting: continuous operation

Wire the harness to a scheduler so a batch runs, the ledger and journal update,
and any human requests surface — on a cadence, across sessions, without a person
driving each step. The in-process loop already runs unattended for a bounded
run; this makes it perpetual.

---

## External help wanted

Collected asks for the human (and, through them, other people/systems). None
block M0.

- **A working GFN2-xTB** (conda `xtb`/`tblite`, or a compiled binary on PATH).
  Gives the loop a ~100× cheaper screening tier and access to much larger
  workpieces than DFT allows on this host. *Currently blocked by: no sudo/conda
  on the build host.*
- **A modest higher-accuracy compute budget** for Tier-3 confirmation runs
  (larger basis / hybrid functionals / dispersion) on shortlisted candidates.
- **A domain expert to hold the VETO pen** — someone from the molecular
  nanotechnology / computational chemistry community willing to review promoted
  candidates and reject bad directions. The gate is real but currently unstaffed.
- **Pointers to reference data** — published DFT energetics for specific
  mechanosynthesis steps we can calibrate the arbiter against.
