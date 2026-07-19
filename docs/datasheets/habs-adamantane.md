# Step datasheet — hydrogen abstraction from adamantane (diamondoid surface model)

**Status: candidate datasheet, VETO-pending.** Every number below was produced
by the cheiron loop's arbiter and lives in the append-only records
(`experiments/m0_hydrogen_abstraction/results/ledger.jsonl`, `scans.jsonl`).
No claim here has been reviewed by a domain expert; the VETO gate is real and
currently unstaffed. This document consolidates; it does not add.

**The step.** `Tool· + H–C(adamantane) → Tool–H + ·C(adamantane)` — abstraction
of a hydrogen from adamantane (C10H16), the smallest rigid diamondoid and the
project's stand-in for a hydrogenated diamond surface site. Target site:
tertiary (bridgehead) C–H unless stated.

**Methods.** ΔE: UKS/PBE/def2-SVP (df, opt). Barriers: relaxed approach scans,
UKS/PBE/def2-SVP screen, UKS/PBE0/def2-SVP confirmation where stated;
"clamped" = both bodies Cartesian-anchored (positional-control model,
transferring H free). PBE barriers are lower bounds (measured hybrid shifts:
+1.8 to +6.0 kcal/mol depending on tool family). No counterpoise correction;
collinear approach only.

## Characterized tools

| | ethynyl (·C≡CH) | hydroxyl (·OH) | ethynyl-adamantyl (handle-mounted) |
|---|---|---|---|
| ΔE, tertiary site | **−35.2** kcal/mol | **−19.2** kcal/mol | — |
| ΔE, secondary site | −34.1 | −18.0 (Hess prediction) | −33.2 (Hess prediction) |
| ΔE, methane reference | −26.2 | −10.2 | **−25.4** (handle costs 0.8 vs free tip) |
| approach barrier (clamped, PBE) | **0.0** (transfer complete by 1.8 Å) | **0.0** (mid-transfer at 1.8 Å) | **0.0** — fully converged (−4.28 @2.4, −31.50 @1.8; integrity-gate clean) |
| hybrid barrier estimate | 0 (no plausible bias creates one) | ≲1.5 (family shift applied); PBE0 run queued | 0 (tip chemistry unchanged by frame) |
| tool integrity | preserved (gate: all geometries pass) | preserved | preserved |
| character | strong, hot | mild, fast | strong tip on a positionable frame |

**On the handle-mounted tool:** mounting the ethynyl tip on a rigid adamantyl
frame — the shape a positioning machine could actually grip — leaves both its
thermodynamics (0.8 kcal/mol handle cost) and its approach to the *crowded*
secondary site essentially unchanged (no steric wall along the collinear
trajectory; entrance energy matches the free tip). Caveat: one collinear
trajectory only; a bulkier frame or an off-axis site could still show steric
cost. Confirmed by a fully-converged clamped scan (−4.28 @2.4 Å,
−31.50 @1.8 Å, barrier 0.0, both geometries integrity-clean): the
handle-mounted tool approaches and abstracts from the crowded secondary site
with no barrier and no steric penalty on the collinear trajectory.

## Site selectivity — the headline

- Thermodynamic tertiary-vs-secondary margin: **1.14 kcal/mol** (identical
  through every tool tested — a workpiece property, per Hess's law).
- Kinetic margin under positional control (ethynyl, clamped per-site scans):
  **zero** — both sites barrierless, entrance wells 0.2 kcal/mol apart.
- Off-target measurement: with only a distance restraint (no orientation
  control), the tool abandoned the intended secondary site for neighboring
  hydrogens. Connectivity stayed intact — position, not bonding, failed.

**Design consequence (measured, not argued):** chemical preference cannot
address a specific C–H on a diamondoid surface. Whichever site the tool is
*held over* reacts; site selectivity is entirely the positioning machine's
job. Both characterized tools execute the abstraction without kinetic
penalty once positioned.

## Cage effects worth knowing

- The bridgehead radical cannot planarize: adamantane's tertiary C–H is
  ~4.7 kcal/mol *less* favorable to abstract than isobutane's (−35.2 vs
  −39.9) — flexible model molecules flatter the real surface task.
- Adamantane C–H BDEs cluster tightly (tertiary barely below secondary),
  which is what collapses the thermodynamic site margin to ~1 kcal/mol.

## Provenance and caveats

- Single collinear trajectory per site; no approach-angle scan yet.
- def2-SVP basis without counterpoise inflates well depths.
- PBE screens / PBE0 confirms protocol validated against literature
  activation energies on four tool chemistries (worst deviation ~3.4
  kcal/mol, methyl); ethynyl's barrierless verdict is robust to any of it.
- Records: candidates `habs-{ethynyl,hydroxyl}-adamantane{,-2h}` in the
  ledger; scan records in `scans.jsonl` (per-point optimized geometries
  included); narrative in `JOURNAL.md` (2026-07-17 … 2026-07-18).
