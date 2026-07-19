# cheiron — project journal

A running, human-readable log of what the project decided, tried, learned, and
where it got stuck. Newest entries at the top. Failures are recorded here on
equal footing with successes — that is a design commitment of the project
(see `README.md`).

Machine-readable run records live in `experiments/*/results/` as JSONL; this
file is the narrative that ties them together.

---

## 2026-07-19 — Predict-then-verify, exact: methyl+water = +10.2, and the guard passes on three element families

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

Tested the reversibility guard on fresh, silicon-free data. Added water (H2O)
as an O-H donor workpiece; `methyl` abstracting its O-H is the exact reverse of
the measured `hydroxyl`-from-methane (−10.2), so reversibility *predicts* it at
**+10.2 before computing**. The arbiter returned **+10.2** — to the decimal.

The automated check now enforces three reverse relationships, one per element
family, all passing exactly:

    OK  methyl+methane  (+0.0) self-reverse                = +0.00   [carbon]
    OK  hydroxyl+methane(-10.2) + methyl+water   (+10.2)   = -0.00   [oxygen]
    OK  silyl+methane   (+19.7) + methyl+silane  (-19.7)   = -0.00   [silicon]

Two things at once: a **prediction made from a physics identity and confirmed
exactly** (the design-then-validate cycle at its cleanest — the number was
known before the calculation ran), and the **guard demonstrated on independent
data** (it found the new pair automatically and passed). A convergence or spin
bug that shifted `methyl+water` even 1 kcal/mol would now break this pair and
exit nonzero. The loop predicts its own results from invariants and then checks
that the arbiter obeyed them — across C, O, and Si.

## 2026-07-19 — Made the reversibility check permanent: an automated physics guard on the ledger

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

Turned yesterday's happy accident — the ±19.7 reversibility pair — into a
standing automated check, the same way each barrier near-miss became a
guardrail. `cheiron.validate.check_reversibility` scans the ledger for
candidate pairs whose tool/workpiece *saturated molecules are swapped* (the
same abstraction run backwards, so ΔE_forward + ΔE_reverse must be ~0) and for
self-reverse pairs (A-from-A, which must be ~0), and reports the residual.
`scripts/check_reversibility.py` runs it with a nonzero exit on failure — a
free, rigorous CI check that the arbiter's *independent* per-candidate
calculations respect microscopic reversibility.

On the current ledger it passes exactly:

    OK  habs-methyl-methane (+0.0) + habs-methyl-methane (+0.0) = +0.00  [self-reverse]
    OK  habs-silyl-methane (+19.7) + habs-methyl-silane (-19.7) = -0.00  [sum must be ~0]

Why this matters: the two bugs this session that reached real numbers — the
geometry-opt reference drift and the SCF-state spike — both violated a physics
invariant the eye had to catch. A convergence failure that shifted one
candidate's ΔE would now break its reversibility pair and be caught
mechanically, for free, every time the check runs. Three built-in physics
identities are now *enforced*, not just observed: reversibility, the
thermoneutral identity, and cross-tool additivity. The loop increasingly
audits its own physics.

## 2026-07-19 — The silicon symmetry closes — and the loop passes an exact reversibility check (+19.7 / −19.7)

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

Added silane (SiH4) as an H-*donor* workpiece, the mirror of silyl-as-tool.
Both predictions confirmed, and one landed as an exact internal-consistency
check the loop passed on its own numbers.

| step | ΔE (kcal/mol) | note |
|------|--------------:|------|
| ethynyl abstracts from silane | **−45.9** | most favorable abstraction in the whole ledger |
| methyl abstracts from silane | **−19.7** | favorable — even a weak tool empties a weak Si–H |

**The silicon picture is symmetric, from one bond.** The weak Si–H bond makes
silicon the *worst* H-remover as a tool (silyl+methane +19.7, unfavorable) and
the *best* H-donor as a workpiece (ethynyl+silane −45.9). Same bond property,
mirror-image roles — the loop showed both.

**An exact reversibility check, unplanned.** `silyl+methane` (+19.7) and
`methyl+silane` (−19.7) are the *same reaction run backwards*
(·CH3 + SiH4 → CH4 + ·SiH3 reverses ·SiH3 + CH4 → SiH4 + ·CH3), so their ΔE
must be exact negatives — and they are, to the decimal: **+19.7 / −19.7**.
The loop was never told these two candidates are related; the arbiter computed
them independently from four separately-optimized species each and they came
out ± the same number. That is microscopic reversibility (ΔE_forward =
−ΔE_reverse) recovered as a rigorous check of the whole pipeline — the third
built-in physics identity it has passed (after methyl+methane = 0.0 exactly,
and cross-tool ΔE additivity to 0.0001). These self-consistency checks are the
strongest evidence, short of an external referee, that the numbers are sound.

Silicon is now characterized on both sides of abstraction (tool and workpiece)
plus addition — the loop spans two operations, two periodic rows, and both
reaction roles, reproducing known bond physics and its own reversibility
throughout.

## 2026-07-19 — Silicon works, and silyl is the sharpest operation-split yet: worst abstractor, fine adder

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

Extended the loop to a **second-row element** — a silyl radical ·SiH3, the tool
family behind real proposed silicon mechanosynthesis tips. Two predictions,
both confirmed with the right sign, and the pipeline handled silicon
(def2-SVP) end to end with no changes:

| operation | ΔE (kcal/mol) | predicted | verdict |
|-----------|--------------:|-----------|---------|
| abstraction from CH4 | **+19.7** | poor (Si–H < C–H, endothermic) | **unfavorable** — the worst abstractor measured |
| addition to C2H4 | **−23.0** | competent (Si–C bond) | **favorable** |

**The most dramatic operation-dependent ranking so far.** Silyl is the *only*
strongly unfavorable abstractor in the whole ledger (+19.7 — it cannot pull an
H off a hydrocarbon, because the Si–H bond it would form is too weak) yet a
perfectly good adder (−23, mid-pack). Worst at one operation, fine at the
other — because abstraction cares about the tool's bond to *hydrogen* and
addition about its bond to *carbon*, and for silicon those diverge sharply.
Every earlier tool at least abstracted *somewhat*; silicon makes the split
categorical.

Two things banked. (1) **Generality:** the arbiter, builders (both operations),
and spin handling extend to second-row elements untouched — evidence the loop
isn't overfit to C/N/O first-row chemistry. (2) **A genuine negative result,
published:** silyl+methane at +19.7 is the ledger's first strongly-endothermic
abstraction — a tool the loop tried and correctly rejected for that operation.
Publishing the "this tool doesn't work here" is the failures-alongside-results
commitment made concrete, and it is *useful*: it tells a real toolkit designer
not to reach for a silyl tip when the step is an H-abstraction.

## 2026-07-19 — Kinetic regioselectivity too: anti-Markovnikov barrier 1.5 vs Markovnikov ~3.5, reinforced by sterics

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

Extended addition selectivity from thermodynamic to kinetic — the sharper axis,
since radical additions are often kinetically controlled. Threaded the
regiochemistry option through the barrier path and scanned both pathways for
methyl + propene (PBE/def2-SVP):

- **anti-Markovnikov barrier: 1.50 kcal/mol** — certified (`well_resolved =
  True`): smooth saddle at 2.5 Å, product bracketed. (Slightly below
  methyl+ethylene's 2.05, as the more-stabilized secondary radical lowers it.)
- **Markovnikov barrier: ≈3.5 kcal/mol** — *not* certified, and the reason is
  itself the finding. The raw extractor reported 8.78 with the peak at the
  outermost point (2.7 Å), and the guardrail flagged it unresolved. The
  geometry audit showed why: at 2.7 Å the constrained optimum has a **1.66 Å
  steric contact** — the tool's methyl jammed against propene's methyl at the
  hindered internal carbon — a strained local minimum, not the barrier. The
  clean interior points (2.5:+3.57, 2.3:+3.34) put the real Markovnikov saddle
  near ~3.5 kcal/mol.

**Kinetic regioselectivity favors anti-Markovnikov by ~2 kcal/mol**, agreeing
with the thermodynamic 3.8 margin and textbook radical control. And the
Markovnikov steric clash is a mechanistic bonus the loop surfaced by geometry
auditing: the disfavoured pathway is penalized through **two** channels —
electronic (less-stable primary radical, seen in ΔE) *and* steric (a hindered
approach, seen only in the scan geometry). Abstraction's selectivity was
positional-only; addition's is chemistry-plus-sterics — a richer intrinsic
selectivity for the machine to exploit.

Addition selectivity is now characterized on both sub-axes (thermodynamic +
kinetic), matching how abstraction's site selectivity was done. The guardrail
correctly refused to certify the strained Markovnikov number — the pipeline
declining a bad value is the system working, and the honest ~3.5 comes from
reading the clean points, flagged as such.

## 2026-07-19 — Addition selectivity: anti-Markovnikov by 3.8 kcal/mol — the fourth axis, and a cross-operation contrast

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

Radical addition's last uncharacterized axis is regioselectivity — *which*
alkene carbon the tool attacks — the bond-forming analog of abstraction's C–H
site selectivity. Measured both regiochemistries of methyl + propene
(UKS/PBE/def2-SVP):

| pathway | attacked C | radical lands on | ΔE (kcal/mol) |
|---------|-----------|------------------|--------------:|
| anti-Markovnikov | terminal CH2 | secondary C | **−32.5** |
| Markovnikov | internal CH | primary C | −28.7 |

**Anti-Markovnikov preferred by 3.8 kcal/mol** — the textbook radical
regiochemistry, recovered from first principles. The margin *is* the
secondary-vs-primary radical stabilization difference (~3–4 kcal/mol known);
attacking the terminal carbon leaves the unpaired electron on the
more-substituted, more-stabilized carbon. Same known-regularity validation
used throughout, now on selectivity.

**Cross-operation contrast worth noting.** Abstraction's *site* selectivity on
adamantane was tiny — 1.14 kcal/mol thermodynamic, ~0 kinetic — so it
concluded "selectivity is entirely positional; chemistry doesn't discriminate."
Addition's *regio* selectivity is 3× larger (3.8 kcal/mol) because
primary-vs-secondary radical is a bigger energy gap than adamantane's
tertiary-vs-secondary C–H. So the two operations sit differently on the
chemistry-vs-positioning axis: **abstraction needs the machine to choose the
site; addition has real intrinsic regiochemistry the machine can lean on.**
A toolkit-level design rule that only comparing two operations could produce.

Radical addition is now characterized on all four axes — favorability,
structure, feasibility, selectivity — matching abstraction. The design loop
handles two reaction classes to the same depth.

## 2026-07-19 — Certified: PBE0 addition barrier 3.84 kcal/mol (well-resolved), closing addition feasibility

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

Reran the PBE0 methyl+ethylene barrier on a grid that brackets the product
(down to −13.2 @1.9 Å) and samples the correct electronic state around the
saddle (2.4/2.6, skipping the documented d=2.5 pathology). Clean this time:

| d (Å) | 2.7 | 2.6 | 2.4 | 2.3 | 2.1 | 1.9 |
|---|---:|---:|---:|---:|---:|---:|
| E−E∞ | +2.02 | +3.83 | **+3.84** | +3.54 | −1.22 | −13.24 |

**Barrier 3.84 kcal/mol, `barrier_well_resolved = True`** — the pipeline now
*certifies* it: smooth interior plateau at ~2.4 Å, product bracketed, no spike,
all four guardrails satisfied. This refines yesterday's uncertified read-off
(~4.9, eyeballed off the spiky scan) down to a firm 3.84 — which is exactly the
point of certification: the eyeball was in the ballpark; the guardrailed grid
is the number.

Final picture for the methyl+ethylene addition barrier: PBE 2.0 → PBE0 3.84 →
literature ≈6–8. PBE0 lifts it toward experiment but stays ~2–4 kcal below —
the *same residual underestimate* PBE0 shows for abstraction (methyl+methane
PBE0 10.6 vs exp ~14). Two independent operations, one consistent method
signature. That consistency is the strongest evidence — short of an external
referee — that the addition pipeline computes the same physics as the
abstraction one, and it is now certified rather than eyeballed.

Second operation status: favorability (validated), structure (approximately
additive), feasibility (certified barrier, PBE0-confirmed) — radical addition
is a first-class citizen of the loop alongside abstraction.

## 2026-07-19 — PBE0 addition barrier ≈5 (corrects toward literature) — and a reproducible SCF spike, now guarded

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

PBE0 barrier for methyl+ethylene addition, meant as the hybrid confirmation of
yesterday's PBE ≈2. It delivered both a result and a bug.

**The result.** Away from one pathological point, the profile is smooth and
peaks at **≈4.9 kcal/mol near d = 2.4 Å** (2.7:+2.0 → 2.6:+3.8 → 2.4:+4.9 →
2.3:+3.5 → 2.2:+2.1). So PBE0 lifts the barrier from PBE's ≈2 toward the
literature ≈6–8 — the **same correction direction and rough size as
abstraction** (methyl+methane: PBE 8.2 → PBE0 10.6 → exp ≈14). The
PBE-screens/PBE0-confirms protocol transfers to the second operation: both
operations sit a few kcal below experiment at PBE0, consistently.

**The bug.** At *exactly* d = 2.5 Å the constrained optimization **reproducibly**
(twice, independent runs) converges to a solution ~28 kcal/mol above its
neighbours — a higher electronic state PySCF flags "converged," the same
"converged ≠ correct" trap as the abstraction reference-drift bug, but now a
spin/symmetry-broken SCF state rather than a stalled optimizer. It stands
alone: +28 between neighbours of +3.8 and +4.9.

**The guardrail gap it exposed, now closed.** `barrier_well_resolved` checked
grid *geometry* (interior max, small gaps, ≥3 points) but not energetic
plausibility — so a spike, being a valid interior maximum, would have passed if
the grid had bracketed the product. Fixed: a barrier point more than 8 kcal/mol
above its nearest sampled neighbour (≤0.3 Å away) is flagged as a likely
mis-converged state, not a saddle. Four guardrails now, each from a real miss:
compression walls, coarse grids stepping over the saddle, sparse "barrierless"
verdicts, and now energetic spikes. (This scan's grid also didn't reach the
product well, so the extractor's reported number was meaningless — and
well_resolved already returned False for that, correctly.)

Honest status of the number: PBE0 addition barrier ≈5 kcal/mol is a *read off
the smooth points*, not a clean extractor output — the d=2.5 pathology and the
un-bracketed grid mean the pipeline itself declined to certify it, which is the
correct behaviour. A clean automated value needs a grid that brackets the
product and either avoids or auto-reruns the 2.5 Å state. Filed, not faked.

## 2026-07-19 — Addition feasibility: first barrier, well-resolved, and PBE's bias transfers

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

The second operation now has all three axes measured, not just favorability.
First production addition barrier — methyl + ethylene, PBE/def2-SVP, the
bond-forming coordinate d(alkene-C···tool-C) frozen per point:

| d (Å) | 2.7 | 2.5 | 2.3 | 2.1 | 1.9 |
|---|---:|---:|---:|---:|---:|
| E−E∞ (kcal/mol) | +0.93 | **+2.05** | +0.70 | −4.10 | −15.22 |

**Barrier 2.05 kcal/mol, and the resolution guardrail passed it** (`well_resolved
= True`): an interior maximum at 2.5 Å with lower points on both sides and
0.2 Å spacing — a genuine early transition state, not a grid artifact. The same
`ApproachScan` extraction and the three guardrails built for abstraction
(approach-only max, compression-wall exclusion, sampling check) applied to the
new operation unchanged.

**PBE's barrier bias transfers.** Literature puts the methyl+ethylene addition
barrier at ≈6–8 kcal/mol; PBE gives ≈2 — the same several-kcal underestimate
PBE showed for abstraction (methyl+methane: PBE 8.2, PBE0 10.6, experiment
≈14). So the barrier is qualitatively right (small, early, correct position)
and quantitatively low by the expected amount; a PBE0 pass would lift it toward
the literature value, exactly as it did for abstraction. That the *bias itself*
is consistent across two independent operations is a small validation of the
method ladder.

Where the second operation stands: **favorability** (validated vs known ΔE),
**structure** (approximately additive, empirically), and now **feasibility**
(a real, guardrail-certified barrier that behaves like abstraction's under the
same method bias). The design loop does two reaction classes end to end. Next
refinements: a PBE0 addition barrier to confirm the ~6–8 target, and the same
scan for a hotter tool (ethynyl — likely near-barrierless, mirroring
abstraction).

## 2026-07-19 — Addition is *approximately* additive — empirically, not by identity

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

Added propene (C3H6_Cs) as a second substrate — with anti-Markovnikov
attack-site selection (the tool hits the terminal CH2, radical lands on the
more-substituted carbon) — to ask whether addition ΔE decomposes into
tool + substrate terms the way abstraction does. Results (UKS/PBE/def2-SVP):

| tool | + ethylene | + propene | Δ(substrate) |
|------|-----------:|----------:|-------------:|
| ethynyl | −66.1 | −67.2 | −1.1 |
| methyl | −32.1 | −32.5 | −0.4 |
| **ethynyl − methyl** | **−34.0** | **−34.7** | |

**It is additive — but only approximately, and that "approximately" is the
point.** The tool-difference is substrate-independent to ~0.7 kcal/mol, and
both tools gain a similar small amount going to propene (the secondary product
radical is slightly more stabilized than ethylene's primary one). So a
tool-term-plus-substrate-term model predicts addition ΔE to within ~1 kcal/mol.

But contrast the abstraction ladder, where additivity held to **0.0001**
kcal/mol: there it is an *exact identity* (ΔE = BDE_workpiece − BDE_tool,
Hess's law). Addition has **no such guarantee** — the adduct fuses tool and
substrate into one molecule whose energy need not split cleanly — yet it very
nearly does, because the tool's C–C bond strength and the substrate's
radical-stabilization contribute almost independently. The residual (~0.7–1
kcal/mol) is the real coupling between them, and it is *information*: it is
exactly what an additive screening model would get wrong, and it is small.

Practical read: the anchor-then-predict strategy that made abstraction
screening cheap transfers to addition — one measurement per tool (× ethylene)
plus a per-substrate offset predicts the grid to ~1 kcal/mol — but here the
model must be *validated*, not trusted, because no identity underwrites it.
That is the honest difference between a guaranteed regularity and an empirical
one, and the loop can now tell them apart by construction.

## 2026-07-19 — Operation-dependent tool ranking: abstraction strength does not predict addition strength

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

Completed the addition tool ladder on ethylene and set it beside the
abstraction ladder (both UKS/PBE/def2-SVP, ΔE in kcal/mol):

| tool | abstraction (vs CH4) | addition (vs C2H4) |
|------|---------------------:|-------------------:|
| ethynyl | −26.2 | −66.1 |
| vinyl | −3.1 | −42.5 |
| hydroxyl | −10.2 | −39.8 |
| methyl | 0.0 | −32.1 |
| amino | −1.2 | −31.1 |

**The two rankings are not the same.** Spearman ρ ≈ 0.8 — positively
correlated (ethynyl dominates both, amino is weak in both), but the middle and
bottom reshuffle materially:

- **methyl** is the loop's *worst* abstractor (thermoneutral on methane) yet a
  perfectly good adder (−32, ahead of amino). A methyl radical forms a weak
  new C–H on abstraction but a strong new C–C on addition — different bonds,
  different verdict.
- **hydroxyl and vinyl swap**: hydroxyl out-abstracts vinyl by 7 kcal/mol
  (strong O–H) but under-adds it (−39.8 vs −42.5), because the C–O bond it
  forms on addition is weaker than vinyl's new C–C.

This is exactly the kind of result the loop exists to surface, and — unlike
the abstraction additivity, which Hess's law guarantees — **nothing forced it**:
addition ΔE = π-bond-broken − new-σ-bond-formed depends on the tool's bond to
*carbon*, a different quantity from the tool's X–H strength that governs
abstraction. A tool has no single scalar "reactivity"; its suitability is
operation-specific.

Direct consequence for SELECT (and for any real toolkit): **rank tools per
operation, never by a generic reactivity.** The abstraction leaderboard is not
the addition leaderboard. That is a concrete design rule the loop produced by
doing two operations rather than one — the payoff of M4 beyond merely "it also
works."

## 2026-07-19 — A second operation: radical addition works and validates against known chemistry

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

The loop now does more than one reaction. Everything before this was hydrogen
abstraction (bond *transfer*); today it took a **bond-forming** step —
radical addition across a C=C — from scaffold to validated result in one
session, without disturbing the abstraction pipeline (52→ green throughout;
the shared arbiter is untouched, the new evaluator just calls `evaluate_species`
on the three species and combines them).

First two additions (`Tool· + H2C=CH2 → Tool-CH2-CH2·`, UKS/PBE/def2-SVP):

| tool | ΔE (kcal/mol) |
|------|--------------:|
| ethynyl | −66.1 |
| methyl | −32.1 |

The **methyl anchor validates the operation the same way methane validated
abstraction**: methyl + ethylene → n-propyl radical has a literature electronic
ΔE around −28 to −30 kcal/mol; PBE gives −32.1, overbinding by the same few
kcal/mol it overbinds abstraction. Right sign, right magnitude, right method
bias. And the tool ordering carries across operations — ethynyl is as
dramatically hotter here (−66 vs −32) as it was in abstraction (−26 vs 0 on
methane), because the same strong-radical character drives both.

Significance for the project: this is the M4 headline — **the design loop is
not hardwired to one reaction.** The PROPOSE→BUILD→ARBITER→SCORE machinery,
the append-only ledger discipline, and the method-with-every-number rule all
transferred to a new bond-forming operation with a small isolated module. A
positional-assembly toolkit needs both take-away and build-up steps; the loop
now demonstrably validates both.

Next slices: barriers under approach for addition (the M1 machinery is
abstraction-shaped, so this needs its own thin adapter), a SCORE path, and a
few more tool/substrate pairs to see whether an additivity-like structure
holds for addition too (no Hess-law guarantee here — the three-species
stoichiometry differs).

## 2026-07-19 — PBE0 on the surface model — and the guardrail catches its own blind spot

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

Ran hydroxyl+adamantane (tertiary) clamped at **PBE0** to give the datasheet's
surface-model barrier a hybrid-grade value instead of a family-shift estimate.
Two points: −1.38 @2.4 Å, −2.26 @1.8 Å; the extractor said barrier 0.0.

I did **not** record that as "barrierless," because the resolution guardrail I
added this morning had a blind spot I hit immediately: `barrier_well_resolved`
returned `None` (no flag) whenever the barrier was 0, but a *2-point* scan
cannot exclude a small saddle sitting between its points — and hydroxyl is the
exact tool that goes 0 → 1.8 kcal/mol from PBE to PBE0 on methane. So a sparse
grid reporting "0" is as untrustworthy as a sparse grid reporting a peak.

Fix: the guardrail now flags a barrierless verdict too unless the approach is
actually sampled — ≥3 points, gaps ≤0.3 Å, monotonically downhill. The
2-point PBE0 scan is now correctly marked *unresolved* (and I fixed a
floating-point gap comparison that a real 0.3 Å grid trips: 2.1 − 1.8 =
0.30000000000000004). The honest statement for the datasheet stands as the
prior estimate: hydroxyl on the adamantane tertiary site has a **small PBE0
barrier, ≲1.5 kcal/mol** (consistent with the two negative points and the
methane family shift), not a measured zero.

Third near-miss turned into a guardrail this session (compression walls →
approach-only max; coarse positive barriers → interior-max + gap check; sparse
"barrierless" → sampling check). The barrier extractor is now hard to fool in
the three ways I actually fooled it.

## 2026-07-19 — Closed: the fully-converged handle-steric barrier, after six tries and a 2-hour window

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

The one measurement the host had blocked for two days finally ran. In a rare
4.5 GB window that held for the full ~2 h (7429 s), the converged clamped scan
of the handle-mounted ethynyl-adamantyl tool on adamantane's crowded secondary
site completed: **−4.28 kcal/mol @2.4 Å → −31.50 @1.8 Å, barrier 0.0**, both
geometries clean through the integrity gate (transfer complete at 1.8 Å, no
unexpected bonds). The −4.28 entrance matches the free tip's −4.26 and the
earlier step-7 partial (−4.25) to two decimals.

So every route to this number — rigid scan, relaxed partial, and now the
fully-converged relaxed scan — agrees: **the bulky adamantyl handle imposes
no steric penalty and no barrier** on the collinear approach to a crowded
site. The datasheet's last open caveat is closed; the handle-tool row now
reads "fully converged" rather than "rigid + partial."

Process notes worth keeping: (1) six attempts, five killed by neighbor-daemon
memory spikes, one survivor — the fix was not cleverness but a genuinely
sustained window plus one-shot patience (no competing jobs while it ran); the
`--max-memory` cap and cross-spec reference (job reaches the optimizer in
seconds) made the survivor possible. (2) Deciding to make it a *final*
attempt, publish either way, and stop chasing — that discipline is what let
the loop spend the intervening days on productive small-system science
instead of spinning on one blocked calc.

## 2026-07-19 — Correction: I overstated it. The polar-substrate effect is modest (~1 kcal/mol), not dramatic

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

The previous entry's ≈1.3 kcal/mol methyl+methanol barrier was a coarse-grid
artifact — exactly the caveat I flagged there, now realized. The 5-point grid
jumped 2.0 → 1.6 Å and **stepped over the saddle**. A fine grid
(2.4/2.2/2.0/1.8/1.6) resolves it: −0.49 → +0.12 → +1.26 → **+3.16 @1.8 Å**
→ −5.76 (transfer). The barrier is **≈3.2 kcal/mol**, cleanly bracketed
(rising to the peak at 1.8, falling to the product well at 1.6).

Revised conclusion: against the methyl-family PBE BEP prediction of ~4.1
kcal/mol at ΔE −7.9, the polar substrate lowers the barrier by only about
**1 kcal/mol — modest, not the "roughly a third" I claimed**. The direction
still holds (polar C-H is somewhat easier than a nonpolar C-H at matched
driving force), but the magnitude I reported yesterday was wrong, and the
"heteroatom sites are kinetically *cheap*" framing was too strong. Corrected
to: heteroatom-adjacent C-H is *modestly* easier, mostly a small effect on top
of its favorable thermodynamics.

Two lessons banked: (1) grid density is not a detail — a barrier from a grid
that doesn't bracket the saddle is a lower bound, and I should run the fine
grid *before* drawing the conclusion, not after; (2) the barrier_kcal fix from
the same session did its job here (the fine grid's own +3.16 peak is a real
bracketed saddle, not a compression wall), so the extractor and the grid are
now both honest. Leaving yesterday's overstatement in the log, struck through
by this entry — that is the point of the log.

## 2026-07-19 — Separating experiment: a polar substrate lowers the barrier even for a nonpolar tool

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

The control that separates driving force from polarity: **methyl** (nonpolar
tool) on **methanol** (polar substrate), clamped PBE. If the barrier landed
near the C-family BEP prediction (~4.1 kcal/mol at ΔE −7.9), substrate
polarity would be kinetically inert; if well below, the polar C-H is
intrinsically easier regardless of the tool.

It landed **well below: barrier ≈ 1.3 kcal/mol** (peak +1.26 at 2.0 Å) —
roughly a third of the ~4.1 the nonpolar-substrate methyl ladder predicts.
So a polar substrate *does* carry a genuine kinetic advantage, independent of
the tool's own polarity. Combined with hydroxyl+methanol (barrierless), the
methanol α C-H is easy for both a polar and a nonpolar abstractor. Practical
read for SELECT: **heteroatom-adjacent C-H sites are kinetically cheap targets**
— useful, since real functionalized surfaces are full of them.

**A code bug this exposed and fixed.** The raw profile was
−0.5 → +1.3 → −5.8 → +11.3 → +28.3: the H transfers by ~1.6 Å (deep well),
then forcing the approach distance still shorter just *compresses the
newly-formed bond* into a +28 wall. `barrier_kcal()` was taking the max over
all points and so reported that compression wall as the "barrier." Fixed: the
barrier is now the peak on the **approach side only** — points nearer than the
product minimum are compression and excluded (test-backed; correction record
appended to `scans.jsonl`, superseding the bogus 28.3). Same lesson as the
rigid-scan wall from three days ago, now handled in the extractor rather than
by eye.

Caveat kept: 1.3 is provisional — the coarse 5-point grid may not bracket the
true product minimum, so it is a lower-bound estimate; a fine grid near the
saddle would sharpen it. The *direction* (well below the C-family line) is
robust.

## 2026-07-19 — Clamped fix works: hydroxyl abstracts methanol's α C-H barrierlessly (audited)

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

The clamped-bodies rerun of hydroxyl+methanol (PBE0, 8 atoms, fit even at
500 MB) replaced yesterday's jagged leash profile with a clean one:
−2.58 @2.4 Å → −0.84 @2.0 → −1.10 @1.6 → −13.97 @1.3, **barrier 0.0**.
Geometry audited at the transfer point: the target α C-H is broken (C–H
1.81 Å), the new tool O–H formed (0.97 Å), and methanol's *own* O–H stayed
clear (2.93 Å) — so it abstracted the intended C-H, not the easier O-H. That
is the third method-vs-chemistry check the clamped scan has passed where the
leash failed; pinning orientation *and* conformation is now the standard tool
for anything not a small rigid alkane.

**Interpretation, kept honest.** hydroxyl's barrier: methane 1.8 → methanol
0.0 (PBE0). Tempting to call this polar-tool-meets-polar-substrate synergy —
but methanol's α C-H is also 7.9 kcal/mol more exothermic, and on any normal
BEP slope that extra driving force alone lowers the barrier ~3 kcal/mol,
more than enough to erase 1.8. So the barrierless result is *fully explained
by the weaker C-H*; it does **not** by itself demonstrate a distinct
polarity effect. Separating the two would need a case where driving force and
polarity push in opposite directions (e.g. a nonpolar tool on this polar
substrate, or a polar tool on a substrate made more exothermic without a
heteroatom) — a clean experiment to queue, not a conclusion to claim now.

What the methanol pair *does* establish: (1) the loop handles heteroatom
substrates end to end — build, site-typing, favorability, audited kinetics;
(2) polar pairs form a real ~9 kcal/mol H-bonded pre-complex (prior entry);
(3) the abstraction itself is barrierless and site-correct.

## 2026-07-19 — Polar-polar barrier: the leash scan breaks, but a real H-bonded pre-complex appears

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

Attempted the hydroxyl-on-methanol barrier (PBE0, one-leash relaxed scan) to
ask whether a polar substrate compounds oxygen's kinetic advantage. The raw
profile came back non-physical — −9.0 @2.4 Å, **+12.4 @2.0**, −3.2 @1.6,
−7.2 @1.3 — so I did **not** trust the +12.4 as a barrier, and the geometry
audit (kept for exactly this) explained why:

- The target C-H is correctly addressed (tool O approaches H2; C-H stretches
  to 1.33 Å at 2.0, i.e. mid-transfer), so it is not the off-target failure.
- But each constrained point relaxes into a *different* hydrogen-bonding
  conformer: the tool-O···methanol-O distance wanders 2.71 → 2.88 → 2.74 →
  3.29 Å and the C-H length oscillates (1.10 → 1.33 → 1.13 → 1.27). Two
  rotatable OH groups give the leash coordinate several nearby minima, so
  consecutive points sit on different surfaces and the profile is jagged.

**Methodological result (the second time the one-leash scan has failed, now
for a new reason):** it breaks not only on crowded rigid sites (tool slides
off — adamantane) but on *flexible polar* substrates (each point finds a
different H-bond conformer). Both failure modes have the same fix — the
clamped-bodies scan, which pins orientation and conformation — and both were
caught by geometry auditing, not by the energy looking wrong. Clamped
hydroxyl+methanol is queued.

**Real signal salvaged:** the 2.4 Å point is a genuine **hydrogen-bonded
pre-reactive complex** — tool O-H···O(methanol) at 2.71 Å, **~9 kcal/mol
below the separated fragments**. Polar tool meeting polar substrate forms a
directional pre-complex before any C-H chemistry; on a real hydroxylated
surface that is a steering interaction a positioning machine could exploit or
must fight. That much is defensible from this run; the abstraction barrier
itself waits on the clamped scan.

## 2026-07-19 — First heteroatom workpiece: methanol, and a textbook radical stabilization recovered

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

The library steps outside hydrocarbons for the first time. Methanol (CH3OH)
joins as a workpiece, abstracting its **α C-H** — which required a new
`carbon` site type to tell the reactive C-H apart from the much stronger O-H
(getting that wrong would silently measure a different reaction). Three
anchors (UKS/PBE/def2-SVP): ethynyl −34.1, hydroxyl −18.1, methyl −7.9.

The additive model (now 45 records) absorbs it with **worst residual 0.0001
kcal/mol** and a methanol workpiece term of **−7.90 relative to methane** —
identical offset from all three tools, as Hess's law requires. But the number
itself is real chemistry the loop was not told: the α C-H of methanol is
7.9 kcal/mol easier to abstract than methane's, because the resulting
·CH2OH radical is stabilized by the adjacent oxygen lone pair. That is the
textbook α-heteroatom radical stabilization (~8 kcal/mol), recovered from
three independent measurements — the same kind of known-regularity check that
has validated the pipeline throughout, now on a polar substrate.

The genuinely open question methanol sets up is **kinetic, not thermodynamic**:
oxygen *tools* undercut the barrier–ΔE line (an electronegative-TS effect);
does a polar *substrate* do likewise, and do the two compound when a polar
tool meets a polar C-H? hydroxyl+methanol is a small system that fits memory —
its relaxed barrier scan is the next step, and unlike ΔE, no identity
guarantees the answer.

## 2026-07-19 — Handle-steric question answered: the adamantyl frame pays ~zero toll; my earlier hint was wrong

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

Two converging measurements settle it, and retire the "+4.8 kcal/mol steric
toll" I floated two entries ago — that number came from a badly-referenced
step-0 built geometry and does not survive contact with real data.

1. **Rigid approach scan (complete, in `scans.jsonl`)** — the memory-light
   route I should have taken first: single points, no optimizer, so it runs
   in ~2 GB. Handle tool (ethynyl-adamantyl) onto adamantane's crowded
   secondary site, collinear: −1.1 @3.0 Å → −2.2 @2.6 → −4.2 @2.2 →
   −6.5 @1.9. **Monotonically attractive, no steric wall, barrier 0.0.**
2. **Relaxed clamped scan (partial)** — reached step 7 at d = 2.4 Å before
   the host's memory race killed it (fourth kill; it converges cleanly when
   it runs, it just needs a sustained window the neighbors won't grant).
   Partial energy already at **−4.25 kcal/mol and still descending** —
   versus the *free* ethynyl tip's −4.26 at the identical site and distance.

The handle adds **≈0 kcal/mol** at the entrance. Conclusion: on this
trajectory the adamantyl frame does not clash with the crowded site — the
tip approaches as if unmounted. Caveat kept honest: this is one collinear
trajectory; a frame *is* bulky, and an off-axis or more-hindered site could
still show a real steric cost. The fully-converged clamped barrier remains
the one number the host won't let me finish; the rigid scan and the
matching partial are what can be defended today, and they agree.

Engineering lesson banked: for oversized systems on a contended host, run the
**rigid** scan first — it answers "is there a wall?" at a fraction of the
memory and never needs a sustained window. Relaxed refinement is a luxury,
not the screen.

## 2026-07-19 — The 44-atom scan fits after all — and lost a race; first steric hint salvaged

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

The overnight window opened (3.9 GB) and the parked handle-steric scan
launched — and this time it *ran*: first SCF converged (44 atoms,
E = −855.0920 Ha at the built geometry), first gradient done. Then a
neighbor JVM daemon spawned mid-run, reclaimed 2.4 GB, and the OOM killer
took the optimization at step 0. Revised diagnosis: **the calculation fits;
it needs a ~30–60 min *sustained* window, and the host's neighbors respawn
faster than that.** Still parked; still racing.

One observation salvaged from the wreck, stated with all its caveats (single
unrelaxed step-0 energy, never entered the records, not a measurement): at
d = 2.4 Å the built handle-tool supersystem sits **+4.8 kcal/mol above the
separated fragments** against the ledger reference — where the *free* tip's
relaxed entrance at the same site and distance was −4.26. Rigid-vs-relaxed
accounts for some of that gap, but free-tip rigid entrances ran ≈ −1, not +5.
Tentative reading: **the adamantyl handle pays a real steric toll at the
crowded secondary site** — exactly the effect this scan exists to measure.
The number that can be defended has to come from the completed constrained
optimization, when the host finally allows it.

## 2026-07-18 — Hardware boundary measured: 44 atoms needs ~4 GB this host can't give

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

The handle-steric scan (ethynyl-adamantyl tip vs the cage's secondary site,
44-atom clamped supersystem) was attempted three times, down to the most
conservative settings this stack allows (1 thread, 900 MB PySCF cap,
cross-spec ledger reference so the job is *only* the one constrained
optimization). All three: SIGKILL during the first SCF. Together with the
successes at 28 atoms under the same settings, that brackets the requirement:
**≥28 atoms fits in ~2 GB free; 44 atoms needs roughly 4 GB free**, which
this host — sharing 7.7 GB with ~4 GB of neighbor JVM daemons — does not
reliably have. The loop stops attempting until free memory ≥3.5 GB
(cheap check each wakeup) and the question stays on the books: it is the
first measurement where the *tool's handle*, not its tip, is the subject.

(For the record, the failed attempts validated the new cross-spec reference
path in production: the job now reaches the optimizer in seconds.)

## 2026-07-18 — C-family curvature confirmed at hybrid grade; small-system kinetics wrapped

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

Last small-system measurement while the memory squeeze holds:
**vinyl+ethane at PBE0 — barrier 5.31 kcal/mol** (peak resolved at 1.6 Å).
A straight-line C-family extrapolation predicted ≈3.5, so the local slope
between the vinyl points is only ≈0.25 — the C-family barrier–ΔE curve
flattens toward higher driving force at hybrid grade, just as it did at PBE.
Prediction missed by 1.8 kcal/mol; curvature, not noise.

The hybrid-grade kinetic dataset now spans seven barriers across three
families (C: 10.6/6.7/5.3, N: 8.4/6.1, O: 1.8/0.0). Family lines are curved,
family identity dominates, oxygen undercuts everything. Small-system kinetics
is at diminishing returns; what remains parked (44-atom handle sterics, cage
PBE0 confirmations) waits on host memory.

## 2026-07-18 — N-family slope at hybrid grade: ordinary BEP (0.43); oxygen stays the outlier

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

While waiting out the host's memory squeeze (the 44-atom steric scan remains
parked), a measurement that fits: **amino+ethane at PBE0 — barrier 6.06
kcal/mol** (3 points, 269 s), vs amino+methane's 8.37. That gives the
N-family its first hybrid-grade barrier–ΔE slope: ≈0.43 over the 5.4
kcal/mol of extra driving force — ordinary Brønsted–Evans–Polanyi behavior,
right in the classic range, and within the band predicted by assuming
C-family-like kinetics. The picture holds: **C and N families follow normal
BEP lines; oxygen alone undercuts them.** (Addendum, same day: the companion
measurement — hydroxyl+ethane at PBE0, 3 points, 234 s — is **barrierless**,
exactly as the outlier picture predicts; the oxygen claim is now two-point
solid at hybrid grade.)

## 2026-07-18 — Handle-tool term verified twice; remaining ladder ceded to the model

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

`habs-ethynyl-ada-ethane`: **−30.8** vs predicted −30.9 (survival-mode QM:
1 thread, 900 MB cap, 29 min — the shared host is under heavy neighbor load
and this recipe is now the proven fallback). With the handle tool's additive
term pinned by two independent workpieces, the six remaining ladder entries
are Hess-law bookkeeping. **Decision: the loop stops measuring them.**
Predicted values (kcal/mol): propane −35.3, butane −35.0, cyclobutane −34.2,
isobutane −39.1, adamantane −34.4, adamantane-2h −33.2 — published here as
predictions, clearly labeled, never entering the ledger as measurements.
QM time belongs to questions additivity cannot answer.

The open question for this tool is **steric**: does the bulky adamantyl
frame change the *approach* on a crowded site (clamped scan, 44-atom
supersystem)? That needs a memory window the host currently can't give
(~2 GB available, neighbors at ~4 GB). It runs when the window opens.

## 2026-07-18 — The handle doesn't spoil the tip: ethynyl-adamantyl at −25.4

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

First handle-mounted tool measured: `habs-ethynyl-ada-methane`
**ΔE = −25.4 kcal/mol** (UKS/PBE/def2-SVP, df, opt; 959 s at a 1.2 GB memory
cap after one OOM retry — `run.py` now has the same `--max-memory` survival
knob as the scanner). Free ethynyl: −26.2. **The adamantyl handle costs just
0.8 kcal/mol of driving force** — mounting the tip on a rigid frame a
positioning machine could hold leaves its abstraction thermodynamics
essentially intact.

Why this matters: it licenses the loop's whole screening strategy. Small
free-radical surrogates are thermodynamically predictive of realistic
tooltips, so tool-space search can stay cheap and only graduate winners to
handle-mounted form. The place the handle *should* matter is sterics — a
bulky frame approaching a crowded site — which is exactly the clamped-scan
question queued next for this tool (tip vs the cage's secondary site, where
free ethynyl needed positional control to stay on target).

## 2026-07-18 — Grid complete: 40/40, every prediction within 0.1 kcal/mol

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

The full 5-tool × 8-workpiece favorability grid is measured: **40 distinct
candidates, 39 favorable, 1 unfavorable** (the methyl+methane thermoneutral
control), **zero unresolved failures** across the whole campaign. The
anchor-then-predict protocol held perfectly: after each new tool's single
methane measurement, all 21 subsequently measured candidates matched their
additive predictions within 0.1 kcal/mol — Hess-law bookkeeping, as expected,
but 21-for-21 is also a clean bill of health for the pipeline's convergence
discipline (a single sloppy optimization anywhere would have broken the
pattern, as it did twice earlier before being caught and fixed).

The favorability axis of this reaction family is now, for practical
purposes, *solved and closed*: one number per tool, one per workpiece,
arbitrary combinations predictable. Open axes remain kinetics (per-family
barrier relations — measured for all five tools vs methane, only spot-
measured elsewhere), positional/steric effects (clamped scans exist for
ethynyl and hydroxyl on adamantane), and everything beyond this reaction
family (M3's real horizon: new operations, bigger cages, tools with
handles a positional machine could actually hold).

## 2026-07-18 — First step datasheet published (S2): H-abstraction from adamantane

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

[`docs/datasheets/habs-adamantane.md`](docs/datasheets/habs-adamantane.md)
consolidates everything the loop has measured about the step — two
characterized tools (ethynyl: strong/hot; hydroxyl: mild/fast), the
selectivity headline (position is the only selector), cage effects, methods,
and caveats. No new numbers; records only. Status is explicitly
**VETO-pending**: criterion S2 asks for a datasheet-grade characterization,
and this is the loop's candidate for it — but the claim isn't done until a
domain expert has held the pen over it. (Standing request to Kazik: that
reviewer is still the project's most-wanted external contribution.)

## 2026-07-18 — The mild tool works on the surface model: hydroxyl+adamantane barrierless at PBE

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

`habs-hydroxyl-adamantane` (tertiary site): **ΔE = −19.2 kcal/mol**, exactly
the Hess-law bookkeeping value. Clamped approach scan (PBE screen, ledger
reference): −2.3 @2.4 Å → −8.0 @1.8 (mid-transfer) — **barrier 0.0 at PBE**.
Applying the measured hydroxyl-family PBE0 shift (+1.8 at methane, shrinking
with driving force): hybrid estimate **≲1.5 kcal/mol**; a full PBE0
confirmation on the cage is queued but not decision-blocking.

Datasheet line: on a diamondoid tertiary site, the hydroxyl radical is a
*mild, fast* abstraction tool — moderate driving force (−19), near-zero
barrier, and (like ethynyl) site-selective only through positional control.
Next iteration consolidates the characterized steps into the project's first
**step datasheet** document (criterion S2).

## 2026-07-18 — Hybrid-grade kinetic map: the lone-pair advantage is oxygen's alone

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

The PBE0 anchors landed, and the flagged number moved exactly as feared —
**amino: 2.4 → 8.37 kcal/mol** (×3.5). The completed map (vs methane,
def2-SVP; literature activation energies for orientation):

| tool | ΔE | Ea PBE | Ea PBE0 | Ea literature |
|------|---:|---:|---:|---:|
| ethynyl | −26.2 | 0.0 | — | ≈0 (fast at 25 K) |
| hydroxyl | −10.2 | 0.0 | **1.8** | ≈1.7 |
| vinyl | −3.1 | 4.9 | **6.7** | ≈6–8 |
| amino | −1.2 | 2.4 | **8.4** | ≈10 |
| methyl | 0.0 | 8.2 | **10.6** | ≈14 |

Conclusions, hybrid-grade:

1. **The nitrogen "advantage" was PBE's self-interaction artifact.** At PBE0
   amino sits essentially on the C-radical barrier–ΔE line. The story
   simplifies: **only oxygen genuinely undercuts the line** (~3 kcal/mol
   below a C-tool at matched ΔE) — an electronegativity-driven polar-TS
   effect, not a generic lone-pair one.
2. **PBE0//def2-SVP tracks experiment across the whole map** (worst case
   methyl, still ~3.4 low). For a screening loop this is more than good
   enough to rank; the PBE-screens/PBE0-confirms protocol is validated on
   four independent chemistries.
3. Design input for SELECT, final form: among these tools, ethynyl is
   unmatched (barrierless AND most exothermic); hydroxyl is the best
   *mild* tool (small barrier at moderate driving force); methyl/amino/vinyl
   are kinetically expensive. Barrier rankings must be measured per family —
   and now they are.

## 2026-07-18 — Five-tool kinetic map complete at PBE; lone-pair tools sit below the C-radical line

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

Vinyl and amino barrier anchors landed (UKS/PBE/def2-SVP, relaxed leash, vs
methane). The tool map, ΔE and barrier under approach:

| tool | family | ΔE | barrier (PBE) | barrier (PBE0) |
|------|--------|---:|---:|---:|
| ethynyl | C·, sp | −26.2 | 0.0 | — |
| hydroxyl | O·, lone pair | −10.2 | 0.0 | 1.8 |
| vinyl | C·, sp² | −3.1 | 4.9 | — |
| amino | N·, lone pair | −1.2 | 2.4 | — |
| methyl | C·, sp³ | 0.0 | 8.2 | 10.6 |

Reading: the C-radical tools form one coherent barrier–ΔE trend (methyl 8.2 →
vinyl 4.9 → ethynyl 0, tracking exothermicity); the lone-pair tools sit
**below** that line at matched ΔE (amino 2.4 where the C-line says ≈7.5;
hydroxyl 0 where it says ≈3.6). Kinetically, heteroatom radicals are the
bargain tools of this space.

Caveats before enthusiasm: amino's 2.4 is the number most likely to move at
PBE0 — literature puts NH₂+CH₄ around Ea ≈ 10, far above its PBE value, and
SIE hits N lone-pair TSs hard. If PBE0 lifts amino back onto or above the
C-line, the "lone-pair advantage" reduces to an oxygen-specific effect —
worth knowing either way. PBE0 anchors for amino and vinyl are the queued
next step; only then does this map feed SELECT.

## 2026-07-18 — PBE0 lands on experiment: hydroxyl barrier 1.8 (exp ≈ 1.7); family effect confirmed

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

The queued PBE0 re-scan of hydroxyl+methane (5 points, 655 s, optimized-
fragment reference):

| d (Å) | 2.6 | 2.0 | 1.6 | 1.3 | 1.2 |
|---|---:|---:|---:|---:|---:|
| PBE | −3.23 | −3.16 | −4.26 | −5.65 | −6.90 |
| PBE0 | −0.79 | −1.25 | +0.18 | **+1.82** | +1.01 |

As pre-cautioned: PBE's barrierless verdict was the self-interaction
artifact. PBE0 restores a small barrier — **1.82 kcal/mol**, essentially the
experimental activation energy (≈1.7) — and shrinks the pre-reactive complex
to a physical depth. Two conclusions, now hybrid-grade:

1. **The tool-family kinetic effect is real**: at PBE0, hydroxyl+methane is
   1.8 kcal/mol vs methyl+methane's 10.6 — a ~9 kcal/mol kinetic advantage
   invisible to ΔE. Polar tools punch far above their thermodynamic weight.
2. **The method ladder works**: PBE screens (cheap, bias low), PBE0 confirms
   (lands on experiment for this system). This pairing is the loop's working
   protocol from here: PBE for search, PBE0 for anything that feeds a
   decision or a claim.

## 2026-07-18 — First non-additive discovery: the barrier relation is tool-family dependent

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

The hydroxyl+methane relaxed scan (5 points, 810 s, ledger reference)
delivered the first result no thermodynamic identity could have predicted:

| d (Å) | 2.6 | 2.0 | 1.6 | 1.3 | 1.2 |
|---|---:|---:|---:|---:|---:|
| E−E∞ | −3.23 | −3.16 | −4.26 | −5.65 | −6.90 |

**Barrier: 0.0.** The methyl-family barrier–ΔE relation, interpolated at
hydroxyl's ΔE = −10.2, predicts ≈ 3.6 kcal/mol; the measurement says the
O–H tool goes downhill the whole way, with a hydrogen-bonded pre-reactive
complex already at 2.6 Å (−3.2). Same exothermicity class as methyl+propane
(barrier 3.66) — completely different kinetics. **Barrier-vs-ΔE is a
per-tool-family relation, not a universal curve**; polar character in the
transition state is invisible to ΔE and decisive for feasibility.

Caveat, stated before anyone else can: PBE's self-interaction error
notoriously *over*-stabilizes polar TSs — OH + CH4 is a textbook case
(experimental Ea ≈ 1.7 kcal/mol, not 0). A PBE0 re-scan of this system is
queued; the qualitative claim (hydroxyl family ≪ methyl family at equal ΔE)
should survive, the exact zero may not.

For SELECT, today's practical rule: rank tools by measured *family kinetics*,
not by ΔE — a mid-strength polar tool (hydroxyl) may outperform a stronger
nonpolar one on feasibility. That is a real, non-obvious design input the
loop produced.

## 2026-07-18 — Clarification: the ΔE additivity is Hess's law, not a discovery. Barriers are the real search space.

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

A correction of emphasis the record deserves. For single hydrogen
abstraction, ΔE(t, w) = BDE(w–H) − BDE(t–H) *identically* — reactants and
products are the same four fragments, so the additive decomposition is
guaranteed by Hess's law, not discovered by the loop. The 0.000 training
residual and the −15.7/−15.7 verification are therefore **consistency checks
of the pipeline** (valuable: they certify that every optimization converges
to the same fragment energies across candidates) — but they carry no new
chemistry. The earlier entries' excitement about "rediscovered additivity"
stands corrected: rediscovering a thermodynamic identity is quality control,
not science.

What is *not* guaranteed by any identity, and where M3's search genuinely
lives:

- **Barriers.** The methyl series already shows curvature vs ΔE (local BEP
  slopes 0.64 → 0.26). Whether hydroxyl/vinyl/amino fall on the same
  barrier–ΔE relation or each tool family has its own is an open, measurable
  question — polar effects in the TS (electronegative O attacking C–H) are
  exactly the physics ΔE cannot see.
- **Steric/positional effects** (the M2 axis): clamp geometry, approach
  angle, crowding — none additive, all decisive for assembly.

Next: relaxed barrier scans for the three new tools vs methane, starting
with hydroxyl — the polar-TS case where deviation from the methyl-family
BEP is most likely.

## 2026-07-18 — M3 loop closes: predicted −15.7, measured −15.7

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

All five tools are anchored (UKS/PBE/def2-SVP, vs methane): ethynyl −26.2,
hydroxyl −10.2, vinyl −3.1, amino −1.2, methyl 0.0 — a genuine
abstractor-strength spectrum. (Amino landed on its bond-energy estimate;
vinyl came in softer than the BDE guess, consistent with PBE compressing
X–H differences.)

Then the model went on trial: it predicted `habs-hydroxyl-ethane` at
**−15.7**, and the arbiter measured **−15.7**. First full M3 cycle —
propose from the prior, predict, verify, publish — and the prediction hit
to the decimal. With 20 records the additive model's training residual is
still 0.000 kcal/mol; within this reaction family at this method, additivity
is not an approximation, it is the structure of the data.

Where this goes next: the enumerative frontier is no longer interesting to
*measure* exhaustively — the model owns it. Search value now lies in
(a) anchoring more diverse tools (halogens? silyl? charged/strained
abstractors — library work), (b) workpieces that should *break* additivity
(conjugation, strain coupling, heteroatoms nearby) — publishing the first
honest failure of the prior is worth more than ten confirmations, and
(c) the M1/M2 axes (barriers, clamps) over the newly-anchored tools.

## 2026-07-18 — M3 first anchor: hydroxyl measured once, its ladder predicted whole

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

M3's search machinery is live. The tool space grew to five abstractors
(ethynyl, methyl + new hydroxyl, amino, vinyl), and `cheiron.predict` fits
the additive ΔE model from the ledger (worst residual over 17 records:
0.000 kcal/mol) and ranks the unevaluated frontier, anchors first.

First anchor: `habs-hydroxyl-methane` **ΔE = −10.2 kcal/mol** (30 s). Honest
gap: experimental BDEs (CH4 105, H2O 119) suggest ≈ −14; PBE gives −10.2 —
GGA underbinds O–H relative to C–H, so hydroxyl's whole PBE ladder will read
~4 kcal/mol weak. Noted next to the numbers, as always.

That one measurement pinned seven predictions (kcal/mol): isobutane −23.8,
propane −20.1, butane −19.8, adamantane −19.2, cyclobutane −19.1,
adamantane-2h −18.0, ethane −15.7. Next: anchors for amino and vinyl, then
one *verification* measurement against a hydroxyl prediction — the model
earns trust by being tested where it claims to know, and every hit or miss
gets published (criterion S3).

## 2026-07-18 — PBE0 spot-check done — and a root-cause correction owed to the record

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

**Correction first.** The 2026-07-17 reference-drift entry blamed a stalled
geometry optimization passing as converged. Wrong. The real bug, found when
the PBE0 spot-check reproduced the drift (+6.68, matching the original
+6.96): `relaxed_scan`'s recomputed fragment reference inherited the scan
config, whose `optimize_geometry=False` meant fragments were evaluated as
**single points at unoptimized library geometries**. `assert_convergence`
was a fine hardening but fixed nothing; the ledger-reference reuse silently
masked the bug for PBE. Now actually fixed: the fallback reference always
optimizes (`ref_config = replace(config, optimize_geometry=True)`).
Lesson kept: a fix that "worked" because a later change routed around the
bug is not a diagnosis.

**The spot-check (methyl+methane, corrected PBE0/def2-SVP, relaxed leash):**

| d (Å) | 2.0 | 1.6 | 1.3 |
|---|---:|---:|---:|
| PBE | +1.24 | +5.82 | +8.19 |
| PBE0 | +2.25 | +8.43 | **+10.61** |

PBE0 raises the identity barrier ~2.4 kcal/mol toward the literature 14–18 —
direction and rough size of the GGA bias confirmed. Standing method note for
every PBE barrier in the ledger: treat as a **lower bound**, bias ≈ +2–3
kcal/mol at PBE0, more at higher levels. (The barrierless ethynyl verdicts
are safe: no plausible bias turns a steep −4 to −35 descent into a barrier.)

With that, **M2's checklist is complete**: site selectivity measured
(thermodynamic 1.14, kinetic 0.0 — position is the only selector), tool-
integrity hard gate live, method bias bounded. The frontier is **M3**:
proposers that search instead of enumerate.

## 2026-07-18 — Tool-integrity gate landed; all 24 stored geometries pass — and one lesson

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

`cheiron.integrity` implements M2's hard gate: a step may change the bonding
graph only by the intended transfer (target H off its carbon, onto the tool
center); anything else — tool fragmentation, workpiece rearrangement, bonding
to the wrong site — fails, regardless of how good the energy looks. 34 tests
green; `scripts/audit_integrity.py` runs the gate over every stored scan
geometry (exit 1 on failure, CI-usable).

Audit of all 24 stored relaxed-scan points: **all pass**. No tool ever broke,
no workpiece ever rearranged, and the transfer flags line up with the
energies (products exactly where the profiles said).

The instructive subtlety: the **off-target point passes the gate**. When the
one-leash tool slid toward neighboring hydrogens it *approached* them
(1.83 Å) but never bonded — connectivity intact, position wrong. Integrity
and positional fidelity are different failure classes: the gate catches
broken chemistry, only trajectory auditing (`final_xyz` + geometry checks)
catches misdirected chemistry. A positional-assembly pipeline needs both,
and now has both.

M2 remaining: hybrid-functional spot-check of the PBE numbers.

## 2026-07-18 — Kinetic selectivity measured: zero. Position is the only selector.

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

The clamped per-site comparison for ethynyl on adamantane is complete
(UKS/PBE/def2-SVP, clamped bodies, ledger references):

| E−E∞ (kcal/mol) | tertiary | secondary |
|---|---:|---:|
| entrance, d = 2.4 Å | −4.46 | −4.26 |
| d = 1.8 Å | −35.09 (→ products) | −33.13 (→ products) |
| **barrier under approach** | **0.0** | **0.0** |

Both sites: barrierless, entrance wells 0.2 kcal/mol apart, hydrogen transfer
complete by 1.8 Å. **The strong tool has no kinetic site preference at all on
a diamondoid workpiece.** Combined with the small thermodynamic margin
(1.14 kcal/mol), the chemistry alone selects nothing: whichever C–H the tool
is *held over* is the one that reacts — and the off-target incident two
entries ago showed exactly what happens when the hold is loose.

This is the M2 headline, and it is the project's premise converted from
argument to measurement: **for hydrogen abstraction on diamondoid surfaces,
site selectivity is entirely the machine's job, not the molecule's.** The
practical datasheet line for this step: works on any accessible C–H,
barrierless, ΔE −34…−35 kcal/mol at this method; place the tool within reach
of exactly one C–H and only that site reacts; place it between two and
chemistry will not save you.

(Method caveats: PBE/def2-SVP, no counterpoise, collinear clamp only, one
tool geometry. A hybrid-functional spot-check remains queued.)

## 2026-07-18 — Clamped-bodies scans work; entrance channels are site-blind (ΔΔ ≈ 0.2)

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

The one-leash flaw is fixed. Frozen exactly-linear angles break geomeTRIC's
internal coordinates, so the positional-control model is **Cartesian**: clamp
two anchor atoms per body (position + orientation fixed, like assembler
grippers), leave the transferring H and everything else free. Validated:
zero anchor drift, collinearity cos = 0.9999, and on the adamantane
secondary site the off-target artifact vanishes (−9.95 → **−4.26**).

First method-consistent kinetic-selectivity data (UKS/PBE/def2-SVP, clamped,
d = 2.4 Å, ledger references):

| site | E−E∞ (kcal/mol) |
|------|----------------:|
| tertiary | −4.46 |
| secondary | −4.26 |

**The entrance channels are site-blind** — 0.20 kcal/mol apart. At the
approach stage, the strong tool feels the two sites as nearly identical;
whatever kinetic discrimination exists must appear in the transfer region
(shorter d, next points) — or be imposed by *where the tool is held*, which
positional control does by construction. Remaining: extend both clamped
profiles to d = 1.8 and 1.4.

## 2026-07-18 — One distance is not positional control: the tool slid off-target

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

The memory window reopened (~5 GB free) and the adamantane kinetic scans ran
after all — the **tertiary** approach profile completed cleanly and
barrierless (−4.3 @2.4 Å → −12.4 @1.8 → −23.5 @1.4, ledger references,
one point per invocation for kill-resilience).

Then the **secondary-site** point produced −9.95 kcal/mol at d = 2.4 Å — more
than twice the tertiary well at the same distance, after an optimization that
wandered 5× longer. The `final_xyz` audit (kept for exactly this purpose)
shows why: the frozen d(target-H···tool-C) held at 2.400 exactly, the target
H stayed on its carbon — and the ethynyl radical *swung around on its leash*
to sit 1.83/1.85 Å from two neighboring hydrogens it was never aimed at.

**The number is not a secondary-site well depth. It is a measurement of the
constraint being insufficient.** A single frozen distance leaves the tool
free to reorient toward whatever site the chemistry prefers — which is
precisely the failure mode positional assembly exists to prevent. The
simulation has, inadvertently and quantitatively, demonstrated the project's
core claim: distance control alone does not target a site; **orientation
must be constrained too**. On crowded workpieces the one-leash relaxed scan
measures chemistry's preference, not the intended trajectory's feasibility.

Fix queued: add angular constraints to the scan (hold the
C_w–H···tool-center angle collinear alongside the frozen distance) so the
scan follows the trajectory a positional assembler would actually impose.
The bad point stays in `scans.jsonl`, correctly labeled by this entry — it
is data about the method, not about adamantane.

## 2026-07-18 — Blocked: kinetic selectivity scans don't fit host memory (3 OOM kills)

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

The per-site adamantane approach scans (29-atom supersystem, constrained
def2-SVP optimizations) were **SIGKILLed three times**: at PySCF's 4 GB
default, at a 2 GB cap, and at a 1.2 GB cap with 2 OMP threads — the last one
died before the first SCF finished allocating. The host's free memory is
~1.5 GB and shrinking (unrelated JVM/Gradle daemons hold ~4 GB and grow). The
M0/M1 work at ≤17 atoms fits; 29 atoms does not. Mitigations already in
place: per-`gto.M` memory caps, `--max-memory` on the scan runner, one-point-
per-invocation scanning. The append-only records took no damage at any kill.

**Request to the human (Kazik):** kinetic selectivity on adamantane needs one
of: (a) a quieter window / more RAM on this host (~4 GB free sustained),
(b) a second host with ≥8 GB free for QM, or (c) the long-requested GFN2-xTB
tier, which would make 29-atom scans trivial. Until then the loop proceeds
with chemistry that fits: completing the methyl barrier ladder
(propane/butane/cyclobutane, BEP-predicted 4.1–4.7 kcal/mol) — direct tests
of the curved BEP relation on systems ≤14 atoms.

## 2026-07-18 — Selectivity comparison complete: both tools prefer tertiary by 1.14; margins are tool-independent

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

The memory-capped retry ran clean (1215 s): `habs-methyl-adamantane-2h`
**ΔE = −7.8 kcal/mol** (predicted −7.9 by additivity). Grid complete, 16/16,
zero unresolved failures. The two-tool selectivity table:

> ethynyl on adamantane: prefers tertiary by **1.14** kcal/mol
> methyl on adamantane: prefers tertiary by **1.14** kcal/mol

Identical to the hundredth — the *site margin is a property of the workpiece
alone*, carried unchanged through either tool. This is thermodynamic
additivity's sharpest confirmation yet, and it has a practical M2/M3
consequence: thermodynamic site preference can be measured once per workpiece
(with any convenient tool) and reused across the whole tool space. Kinetic
selectivity (per-site barriers) remains the open question the scans must
answer — barriers do depend on the tool (methyl 8.2 vs ethynyl 0.0 on
methane), so kinetic margins need not be tool-independent.

## 2026-07-18 — Operational failure: OOM kill on a shared host; PySCF memory now capped

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

The methyl+adamantane-2h evaluation was **SIGKILLed (exit 137)** mid-
optimization: the bootstrap host has 7 GB RAM shared with unrelated JVM/Gradle
build daemons (~4 GB), and PySCF's default 4 GB working-memory assumption
didn't fit. The append-only ledger took no damage — the killed run simply
never appended, which is exactly how that design is supposed to fail.

Fix: `ArbiterConfig.max_memory_mb = 2000`, passed to every `gto.M` call
(arbiter + both scan paths). Capped, PySCF switches to disk/batched integral
algorithms instead of dying — slower beats dead. The candidate is being
re-evaluated with the cap in place. (Not touched: the other project's build
daemons — not this loop's to kill.)

## 2026-07-18 — First selectivity measurement: tertiary over secondary by 1.1 kcal/mol

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

`habs-ethynyl-adamantane-2h` (the cage's CH2 site): **ΔE = −34.1 kcal/mol**
(UKS/PBE/def2-SVP, df, opt; 1869 s — the 2-adamantyl radical optimizes slowly).
With the tertiary result (−35.2), `cheiron.selectivity` produces the project's
first site-preference measurement:

> ethynyl on adamantane: prefers **tertiary** by **1.1 kcal/mol** (ΔΔE).

The margin is small, as the literature says it should be — adamantane
abstraction is only weakly tertiary-selective, because cage rigidity claws
back most of the usual tertiary advantage (the −13.7 kcal/mol
isobutane-tertiary offset collapses to −9.0 here, and the secondary site sits
only 1.1 above that). Implication for M2: at ΔΔE ≈ 1 kcal/mol, thermodynamic
preference alone gives roughly a 6:1 ratio at room temperature — *chemical*
selectivity won't reliably pick one site on a diamond-like surface. Site
discrimination will have to come from **positional control and approach
geometry**, which is of course the project's whole premise; the loop has now
measured, rather than assumed, why that premise is necessary.

Pending: methyl+adamantane-2h completes the comparison for the weak tool;
then surface the selectivity table in the published summary.

## 2026-07-17 — Grid complete at 14/14; additivity prediction lands exact

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

`habs-methyl-adamantane`: predicted **−9.0** kcal/mol by cross-tool additivity
(ethynyl-adamantane offset applied to the methyl tool), measured **−9.0**
(UKS/PBE/def2-SVP, df, opt; 435 s). The additivity rule now covers the custom
diamond-lattice cage as cleanly as the G2 molecules. Grid fully evaluated:
14 candidates, 13 favorable, 1 unfavorable, 0 failures.

Frontier shifts to **M2 — selectivity**: adamantane is the natural first
subject (tertiary vs secondary sites in one rigid molecule); the plan is
per-site comparison — same tool, same workpiece, intended vs competing C–H —
first on ΔE, then on approach barriers.

## 2026-07-17 — M0 ladder complete: adamantane, and the cage-rigidity penalty

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

`habs-ethynyl-adamantane` evaluated: **ΔE = −35.2 kcal/mol** (UKS/PBE/def2-SVP,
df, opt; 434 s), completing all three rungs of the M0 workpiece ladder
(methane → isobutane → adamantane). The adamantane geometry is carved from the
diamond lattice programmatically, so its correctness is test-pinned rather
than trusted.

The interesting part: naive expectation put the tertiary bridgehead near
isobutane (−39.9), but it landed *below the acyclic secondaries* (−35.2 vs
−35.9/−36.1). This is the **cage-rigidity penalty**: the bridgehead radical
cannot planarize, so adamantane's tertiary C–H is unusually strong (known
experimentally, BDE ≈ 99–100 kcal/mol vs isobutane's ≈96.5) — and the loop
recovered the effect from geometry alone, third known regularity reproduced
without being told (after bond-additivity and BEP). Project relevance: rigid,
surface-like sites — the regime positional assembly actually operates in —
are *harder* to abstract from than floppy analogues; favorability numbers
taken on flexible model molecules will systematically flatter the real task.

Remaining pending: methyl+adamantane (the weak tool against the rigid cage —
expect only mildly favorable, ≈ −9 by additivity with the cage penalty).

## 2026-07-17 — BEP prediction tested: predicted 6.0, computed 4.8

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

The previous entry's BEP fit (slope 0.41 from two points) predicted the
methyl+ethane barrier at ≈6.0 kcal/mol. The relaxed scan (5 points, 1441 s,
ledger reference) measured **4.75 kcal/mol** at d = 1.6 Å — right ordering,
1.2 kcal/mol off in magnitude. With three barriers in hand (8.2, 4.75, 2.6 vs
ΔE 0, −5.4, −13.6) the relation is visibly curved, not linear: the local slope
runs 0.64 on the endothermic side and 0.26 toward the exothermic side. So BEP
works here as a *screen* (rank candidates, spot outliers) but not as a
substitute for the scan — which is the right division of labor anyway: cheap
regularities propose, the arbiter disposes.

Remaining unscanned: 2 ethynyl secondaries + cyclobutane (all safely
predicted barrierless — ethynyl is barrierless even for methane, its hardest
case) and methyl propane/butane/cyclobutane (BEP interpolation now predicts
≈4.3–4.7). Diminishing returns per scan; the frontier should shift toward M2
(selectivity) or the adamantane workpiece once the cheap wins are banked.

## 2026-07-17 — Barrier matrix complete; the loop rediscovers Brønsted–Evans–Polanyi

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

Methyl+isobutane relaxed scan (5 points, 834 s, ledger fragment reference —
first scan on the consistent-reference path): well −0.95 @2.6 Å, **barrier
+2.6 @1.6 Å**, then H transfer and descent to −12.0 @1.2 Å. The 2×2
tool×workpiece matrix (UKS/PBE/def2-SVP, relaxed scans, kcal/mol):

| barrier (ΔE) | methane | isobutane |
|---|---|---|
| **ethynyl** | 0.0 (−26.2) | 0.0 (−39.9) |
| **methyl** | 8.2 (0.0) | 2.6 (−13.6) |

Two observations worth keeping:

- **The feasibility axis is not redundant with favorability.** Methyl+isobutane
  is decently downhill yet carries a real barrier; ethynyl is barrierless even
  toward methane, its *least* favorable target. Ranking by ΔE alone would never
  show this.
- **Brønsted–Evans–Polanyi, rediscovered from scratch:** the methyl barriers
  drop with exothermicity at slope ≈ 0.41 (8.2→2.6 over 13.6 kcal/mol) —
  squarely in the classic α ≈ 0.4–0.5 range for H abstraction. Like the M0
  additivity result, the loop's numbers keep reproducing known chemical
  regularities it was never told about — the strongest available evidence
  (short of an external referee) that the pipeline computes chemistry, not
  noise.

Caveats attached to the matrix: coarse distance grids mean each "barrier" is
the profile max over ~0.3–0.4 Å spacing (true saddle may sit slightly higher);
PBE biases barriers low; single collinear trajectory only.

## 2026-07-17 — Flagship confirmed: ethynyl+isobutane is barrierless under approach

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

Relaxed def2-SVP scan of the M0 leaderboard leader, tertiary C–H of isobutane
(3 points, 754 s, all converged, in `scans.jsonl`): −4.7 @2.4 Å →
−12.7 @1.8 → −25.8 @1.4 — monotonically downhill, **barrier 0.0 kcal/mol**,
already 65% of the way down the −39.9 exotherm by 1.4 Å.
`habs-ethynyl-isobutane` is now the first candidate with top marks on both
axes: most favorable (M0) *and* mechanically unimpeded (M1). Under the new
scoring: fitness = 39.9 vs methane's 26.2 — recommendation unchanged by
feasibility, which is itself worth knowing.

**Reproducibility note:** the scan's freshly-optimized fragment reference sits
+1.3 kcal/mol above the M0 ledger's, *with both optimizations converged* —
independently optimized isobutane lands in slightly different local minima.
The barrier verdict is insensitive to this (profile is downhill under either
reference), but ~1 kcal/mol is the current noise floor on absolute well
depths. Fix queued: relaxed scans should *reuse* the ledger's fragment
energies instead of recomputing, making every scan consistent with M0 by
construction (and cheaper — the isobutane reference re-optimization was most
of this run's 754 s).

## 2026-07-17 — A bug caught by unphysical numbers: silent geometry-opt non-convergence; methyl barrier is ≈8.2, and M1's discrimination now works

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

The methyl+methane relaxed scan came back with a −7.7 kcal/mol "van der Waals
well" at 2.6 Å — vdW binding for CH3/CH4 should be well under 1 kcal/mol, so
the number was disbelieved on sight (project rule: never trust a number you
didn't check). Diagnosis, in order:

1. Instrumented the relaxed scan to save optimized geometries (`final_xyz` on
   every point) — an energy without its geometry cannot be audited.
2. Reran the 2.6 Å point: constraint held (2.601 Å), target H still on its
   carbon (1.109 Å), clean vdW geometry, E−E∞ = **−0.75 kcal/mol**. Sensible.
3. So the *points* were fine — the original run's fragment **reference** was
   6.96 kcal/mol too high vs the M0 ledger's converged fragments. Root cause:
   `evaluate_species` reported SCF convergence only; a geometry optimization
   that stalls returns its last geometry and passes as "converged".
   (The ethynyl scan's reference had the same disease, mildly: +0.62.)

**Fixes, all pushed:** `assert_convergence=True` on every geometry
optimization (a stalled opt is now an error, not a wrong number); correction
records appended to `scans.jsonl` (append-only: originals stay, corrections
supersede, with the drift documented in a `note`).

**Corrected physics (UKS/PBE/def2-SVP, relaxed, vs M0 references):**

| pair | profile verdict | barrier |
|------|-----------------|--------:|
| ethynyl + methane | monotonically downhill | **0.0** |
| methyl + methane | well −0.75 @2.6 → peak @1.3 → product complex | **≈8.2** |

The methyl profile is now textbook: shallow well, barrier at 1.3 Å, near-
thermoneutral product complex. PBE undershoots the literature identity barrier
(~14–18 kcal/mol) as GGAs do, so 8.2 is a lower bound; but the *discrimination*
M1 was built for is live — same favorable-sign chemistry, an order-of-magnitude
feasibility gap between the strong and weak tool.

## 2026-07-17 — First production feasibility number: ethynyl→methane is barrierless under approach

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

First def2-SVP **relaxed** approach scan (UKS/PBE, df; constrained
optimizations, 152 s for 4 points), `habs-ethynyl-methane`, in `scans.jsonl`:

| d(C···H) Å | 2.6 | 2.0 | 1.6 | 1.3 |
|---|---|---|---|---|
| E−E∞ kcal/mol | −1.6 | −3.8 | −8.2 | −16.7 |

Monotonically downhill; **barrier under approach = 0.0 kcal/mol**. By 1.3 Å
the constrained optimum already has the hydrogen migrating toward the tool —
the −16.7 point is partway down the reaction exotherm (M0 measured −26.2 for
completion). So the M0 "favorable" verdict for this pair upgrades to
"favorable *and* mechanically feasible along the idealized collinear
trajectory" — the first candidate to clear both axes. Caveat as always: PBE
biases barriers low; but C2H + alkane abstraction is independently known to
be near-barrierless, so the qualitative call stands.

Next: the same relaxed scan for **methyl**+methane — PBE should show its
identity barrier (literature ≈14 kcal/mol; PBE will undershoot) and give M1
its first *blocked-despite-downhill-adjacent* contrast at production method.

## 2026-07-17 — Relaxed scan implemented: the H can now transfer, and barriers appear

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

`cheiron.approach.relaxed_scan` landed (18 tests green): freeze
d(tool···target-H) with a geomeTRIC `$freeze` constraint, relax everything
else, reference against *separately optimized* fragments. A test pins the
1-based-index convention of geomeTRIC constraint files — the classic silent
off-by-one that would freeze the wrong atom pair.

STO-3G smoke (methyl + methane, the identity reaction): −0.37 kcal/mol at
3.0 Å, **+2.36 kcal/mol at 1.3 Å** — once relaxation lets the H move, the weak
tool shows a genuine positive barrier where the rigid scan of the strong tool
(previous entry) showed none. That is exactly the favorable-vs-feasible
discrimination M1 exists to measure. (STO-3G/PBE underestimates the known
~14 kcal/mol CH3·/CH4 identity barrier several-fold; production numbers will
be def2-SVP, and even those inherit PBE's low-barrier bias — worth a hybrid
functional cross-check later.)

Next: production def2-SVP relaxed scans for ethynyl+methane and
methyl+methane into `scans.jsonl` — the first tool-pair *feasibility*
comparison at consistent method.

## 2026-07-17 — First approach-coordinate profile: ethynyl→methane entrance channel is attractive

**Who:** Claude (Fable 5) as harness, inside the continuous `/loop`.

First production rigid scan (UKS/PBE/def2-SVP, df, frozen fragments, 9 single
points, 53 s), `habs-ethynyl-methane`, appended to `results/scans.jsonl`:

| d(C···H) Å | 4.0 | 3.5 | 3.0 | 2.6 | 2.2 | 1.9 | 1.6 | 1.4 | 1.2 |
|---|---|---|---|---|---|---|---|---|---|
| E−E∞ kcal/mol | −0.1 | −0.2 | −0.5 | −0.9 | −1.8 | −3.2 | −4.3 | −2.7 | +6.6 |

**Reading:** the entrance channel is attractive the whole way in to ~1.6 Å —
no barrier under approach along the idealized collinear trajectory, consistent
with C2H + alkane abstraction being known fast/near-barrierless. The upturn at
short range is the *rigid approximation showing its edge*: the target H is
frozen in the methane geometry and cannot transfer, so pushing to 1.2 Å just
compresses a non-reacting system. Consequently `barrier_kcal() = 6.55` here is
a wall-compression number, **not** a reaction barrier — the extractor is
honest but the rigid coordinate stops being meaningful past the well.

Method caveats, stated plainly: PBE (GGA) tends to underestimate abstraction
barriers, and def2-SVP without counterpoise inflates the attraction (BSSE), so
the −4.3 kcal/mol well depth is likely too deep. The *shape* — barrierless
approach, well, wall — is the robust content.

**Next:** a constrained *relaxed* scan (optimize with d(tool···H) frozen, all
else free) so the H can actually transfer; that turns the profile into a real
barrier estimate and replaces the wall artifact with chemistry.

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
