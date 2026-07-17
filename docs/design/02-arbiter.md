# 02 — The arbiter (physics engines)

The arbiter is the project's referee. It must be **impartial** (it does not know
what score we want), **tiered** (cheap methods gate expensive ones), and
**honest about its own accuracy** (every measurement carries the method that
produced it and a note on what that method can and cannot be trusted for).

## Why bond-breaking forces the method choice

Positional assembly *is* bond breaking and forming. That rules out ordinary
classical force fields (fixed bond topology) for the reactive step. The methods
that can watch a bond break, in rough cost order:

| Tier | Method | Cost | Good for | Not to be trusted for |
|-----:|--------|------|----------|-----------------------|
| 0 | geometry/clash heuristics (bond-length graph, steric overlap) | µs–ms | killing impossible builds | anything energetic |
| 1 | semiempirical QM (GFN2-xTB and similar) | ~s | screening reaction energies, relaxations, big systems | absolute barriers, unusual bonding |
| 2 | DFT (GGA/hybrid, moderate basis), unrestricted for radicals | ~min | reaction energies, barriers on shortlisted candidates | near-degeneracy, dispersion without a correction, basis-set error |
| 3 | high-level (hybrid/large basis, dispersion, or correlated WFT) | ~min–h | datasheet-grade confirmation | — (this is our ceiling here) |

**Current implementation.** Tier 0 is a pure-Python geometry check. Tiers 2–3
are **PySCF** (unrestricted Kohn–Sham for open-shell radicals) with
**geometric** driving geometry optimization. Tier 1 (semiempirical) is stubbed:
the intended engine is GFN2-xTB, but the pip `tblite` wheel on this host ships
without its compiled extension and there is no sudo/conda to fix it. Until a
working xTB is available, iteration 0 runs a **small, fast DFT setting as a
stand-in Tier 1** (see below). This is logged honestly as a known limitation.

> **External help wanted:** a working GFN2-xTB (conda `xtb`/`tblite`, or a built
> binary on PATH) would give the loop a ~100× cheaper screening tier and let it
> handle workpieces far larger than DFT allows. Tracked in `03-milestones.md`.

## What the arbiter measures for a reaction step

For a hydrogen-abstraction-type step `Tool· + H–W → Tool–H + ·W`:

1. **Optimize** each species (tool, tool–H, workpiece H–W, product radical ·W)
   at the chosen tier, with correct spin multiplicity.
2. **Reaction energy** `ΔE = [E(Tool–H) + E(·W)] − [E(Tool·) + E(H–W)]`.
   Negative ⇒ favorable (the loop's thermodynamic signal).
   Optionally add zero-point / thermal corrections at Tier ≥ 2.
3. **Approach scan (survivors only):** step the tool toward the workpiece along
   the reaction coordinate, relaxing the rest, to expose the barrier and whether
   mechanical load removes it. This is what makes the step *positional* rather
   than merely thermodynamic.
4. **Tool integrity:** confirm the tool's connectivity is unchanged after the
   step (no rearrangement, no wrong-atom loss).

Each of these becomes a field in the ledger record, tagged with `method` and
`tier`.

## Spin, charge, and the radical trap

The single most common way to get mechanosynthesis energetics silently wrong is
mishandling open-shell species. Radicals (the ethynyl tool, the product
workpiece radical) are doublets and **must** be treated unrestricted with the
right multiplicity. The builder sets `spin` (number of unpaired electrons) per
species and the arbiter refuses to run a closed-shell method on an odd-electron
system. A regression test pins the ethynyl radical as a doublet.

## Accuracy discipline

- A number never travels without its method. `E = -40.51 Ha` is meaningless;
  `E = -40.51 Ha [UKS/PBE/def2-SVP]` is a claim we can defend or refute.
- Screening-tier signs can be trusted more than magnitudes; magnitudes that
  matter get re-run at a higher tier before a datasheet is written.
- Systematic errors partly cancel in a *difference* of similar species — which
  is exactly why we score reaction energies (differences), not absolute
  energies.

## Configuration

Arbiter settings (functional, basis, tier thresholds, optimizer tolerances) live
in the experiment's config, not hard-coded, so a run's exact method is captured
in its ledger and reproducible.
