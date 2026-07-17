# 00 — Goal and scope

## The project in one sentence

`cheiron` is an autonomous design loop that proposes candidate **positional
molecular-assembly reactions**, submits them to physics engines that act as an
impartial arbiter, and evolves toward reactions that are *favorable, feasible,
and selective* — publishing its failures alongside its successes.

## What we are and are not aiming at

The [Feynman Grand Prize](https://foresight.org/grand-prize/) (Foresight
Institute, USD 250,000) has two requirements:

1. A **nanometer-scale robotic arm** with demonstrated positional control.
2. An **8-bit binary adder** that fits inside a 50 nm cube.

Both are *physical* devices. We are **not** trying to win the prize, and we are
not building hardware. We are attacking the design-side bottleneck that sits
under both requirements: **positional molecular assembly** — the ability to make
and break specific bonds at specific places under mechanical (positional)
control, rather than by bulk solution chemistry.

> Aimed at one sub-capability of the unclaimed Feynman Grand Prize — not at
> winning it. — `README.md`

### The one sub-capability we own

> **Design and computationally validate individual positional-assembly reaction
> steps.**

Concretely, a candidate is a `(tooltip, workpiece, approach geometry)` triple.
The loop asks of each candidate:

- **Favorable?** Is the intended bond rearrangement thermodynamically downhill
  (products lower in energy than reactants)?
- **Feasible?** Is there a kinetically accessible path — a barrier low enough (or
  removable under mechanical load) to proceed at the intended temperature?
- **Selective?** Does the tool geometry make the *intended* site react and not
  its neighbours, and does the tool survive the operation (no rearrangement,
  no loss of the wrong atom)?

These three questions are answerable *today* with open-source physics engines on
modest hardware, which is why this is the sub-capability we can actually make
progress on autonomously.

## Why this matters for the prize

Every atomically precise device — arm or adder — is a sequence of positional
assembly steps. A vetted **library of reaction steps** (a "toolset"), each with
quantified favorability/feasibility/selectivity, is the reusable substrate a
later synthesis-planning effort would compose into a structure. Freitas and
Merkle established by hand that a *minimal toolset* for diamond mechanosynthesis
is a small, finite set of reactions. Our bet is that searching and validating
such steps can be **automated and run continuously**, and that an agent-driven
loop can both reproduce the known steps and push into new ones.

## Success criteria (project-level)

- **S1** — The loop reproduces at least one literature-known mechanosynthesis
  step (favorability sign and rough magnitude), end-to-end, unattended.
- **S2** — The loop produces at least one *reaction-step datasheet* for a step
  not obviously in the literature, with the arbiter's evidence and a human
  veto/approval recorded.
- **S3** — Every negative result (proposed step that failed favorability,
  feasibility, or selectivity) is retained and published, not silently dropped.

S1 is the target of milestone **M0**. S2/S3 follow.

## Non-goals

- Winning or directly claiming the Feynman Grand Prize.
- Wet-lab or hardware work.
- Claiming that a computationally favorable step is experimentally realized —
  the loop produces *design hypotheses with physics evidence*, clearly labeled
  as such.

## Intellectual honesty commitments

- Semiempirical and low-basis DFT results are screening signals, not truth.
  Anything promoted toward a datasheet is re-checked at higher accuracy, and the
  method/limitations travel with the number.
- The VETO gate exists so a human domain expert can kill a direction the
  automated score would otherwise reward. Automated fitness is a proxy, and
  proxies get gamed.
