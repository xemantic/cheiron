# Step datasheet — radical addition across a C=C (bond-forming operation)

**Status: candidate datasheet, VETO-pending.** Every number was produced by the
cheiron loop's arbiter and lives in the append-only records
(`experiments/m1_radical_addition/results/`). No claim here has been reviewed by
a domain expert; the VETO gate is real and currently unstaffed. This document
consolidates; it does not add.

**The step.** `Tool· + alkene → Tool–CH2–CH2·` — a radical adds across a carbon–
carbon double bond, forming a new C–C σ bond at the cost of the alkene π bond
and leaving the unpaired electron on the far carbon. This is the loop's second
operation type and its first *bond-forming* one (abstraction transfers an atom;
addition builds structure). Reaction energy: `ΔE = E(adduct·) − E(Tool·) −
E(alkene)` — three species, not four.

**Methods.** UKS/PBE/def2-SVP (df, opt) for ΔE and screening barriers; PBE0 for
confirmation where stated. Barriers: relaxed approach scans freezing
d(alkene-C···tool-C), extracted by the shared guardrailed `ApproachScan`
(approach-only max, resolution + spike checks). No counterpoise; single π-face
approach. PBE underestimates barriers by a few kcal/mol (measured, consistent
with abstraction).

## Characterized tools (addition to ethylene)

| tool | ΔE (kcal/mol) | character |
|------|--------------:|-----------|
| ethynyl (·C≡CH) | **−66.1** | very hot sp radical |
| vinyl (·C₂H₃) | −42.5 | strong sp² |
| hydroxyl (·OH) | −39.8 | strong (O–C bond) |
| methyl (·CH₃) | −32.1 | moderate |
| amino (·NH₂) | −31.1 | moderate |

Validation anchor: methyl + ethylene → n-propyl radical, ΔE = −32.1 vs
literature electronic ΔE ≈ −28…−30 (PBE overbinds a few kcal, as in
abstraction).

## Structure, feasibility, selectivity

- **Approximately additive** (not exactly). Tool-difference (ethynyl−methyl) is
  substrate-independent to ~0.7 kcal/mol across ethylene/propene, so a
  tool-term + substrate-term model predicts ΔE to ~1 kcal/mol. Unlike
  abstraction's *exact* Hess-law additivity (0.0001 kcal/mol), this is
  empirical and must be **validated, not trusted** — no identity underwrites it.
- **Feasibility (methyl + ethylene barrier):** PBE 2.0 → **PBE0 3.84
  (certified, well-resolved)** → literature ≈6–8. PBE0 lifts it toward
  experiment but stays ~2–4 kcal low — the *same residual underestimate* PBE0
  shows for abstraction, a consistent method signature across two operations.
- **Regioselectivity (methyl + propene): anti-Markovnikov preferred.**
  - Thermodynamic: −32.5 (anti-Mark, radical on secondary C) vs −28.7 (Mark,
    primary C) → margin **3.8 kcal/mol** = the secondary/primary radical
    stabilization gap.
  - Kinetic: anti-Mark barrier **1.50** (certified) vs Markovnikov **~3.5**
    (interior points; the outermost point is a strained local minimum with a
    1.66 Å tool-methyl/alkene-methyl clash — flagged unresolved).
  - The disfavoured pathway is penalized through **two** channels: electronic
    (less-stable radical, in ΔE) and steric (hindered approach, seen only in
    the scan geometry).

## Two cross-operation findings (only two operations could give these)

1. **Tool ranking is operation-dependent.** Abstraction strength does not
   predict addition strength (Spearman ρ ≈ 0.8, but methyl is the worst
   abstractor and a solid adder; hydroxyl/vinyl swap). SELECT must rank tools
   *per operation* — the abstraction leaderboard is not the addition one.
2. **Where positional control is load-bearing differs by operation.**
   Abstraction site-selectivity on a diamondoid is ~0 (chemistry doesn't
   discriminate; the machine must choose the site). Addition regioselectivity
   is real (~2–4 kcal/mol, electronic + steric) — the chemistry helps.

## Provenance and caveats

- Single π-face, perpendicular approach; no face/angle scan.
- def2-SVP without counterpoise inflates well depths.
- PBE screens / PBE0 confirms; both a few kcal below experiment on barriers.
- Records: `experiments/m1_radical_addition/results/ledger.jsonl` (ΔE) and
  `scans.jsonl` (barriers, per-point geometries); narrative in `JOURNAL.md`
  (2026-07-19 entries).
