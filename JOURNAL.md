# cheiron — project journal

A running, human-readable log of what the project decided, tried, learned, and
where it got stuck. Newest entries at the top. Failures are recorded here on
equal footing with successes — that is a design commitment of the project
(see `README.md`).

Machine-readable run records live in `experiments/*/results/` as JSONL; this
file is the narrative that ties them together.

---

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
