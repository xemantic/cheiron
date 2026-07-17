"""SCORE stage: map arbiter measurements onto the project's three fitness axes.

The axes come straight from docs/design/00-goal-and-scope.md:

  * favorability  — is the step thermodynamically downhill? (have it at M0)
  * feasibility   — is there a low-enough barrier under approach? (arrives at M1)
  * selectivity   — does the tool hit the intended site only? (arrives at M2)

plus a tool-integrity flag. The components are kept separate on purpose: SELECT
applies pressure to them differently, and a human reading the ledger needs to
see *why* something scored as it did, not just a collapsed number.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .arbiter import ReactionMeasurement

# Feasibility gate: a step whose barrier under approach exceeds this is treated
# as blocked. ~15 kcal/mol still gives ~10^2/s at room temperature by TST, and
# positional load can only lower a real barrier below the scan's estimate.
# PBE biases barriers low, so this gate is generous in the other direction —
# both caveats travel with the number in the note.
FEASIBLE_BARRIER_KCAL = 15.0

# Explicit heuristic weight: one kcal/mol of barrier costs two of exothermicity
# in the scalar fitness. Kinetics beat thermodynamics exponentially, so the
# barrier must dominate a linear score; 2:1 is a declared choice, not physics.
BARRIER_WEIGHT = 2.0


@dataclass
class FitnessRecord:
    spec_id: str
    # favorability
    reaction_energy_kcal: float | None
    favorable: bool | None
    # feasibility (M1) and selectivity (M2): not yet measured
    barrier_kcal: float | None = None
    feasible: bool | None = None
    selectivity: float | None = None
    tool_integrity_ok: bool | None = True
    # overall scalar used by SELECT; None when the measurement is unusable
    fitness: float | None = None
    valid: bool = False
    note: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def score(
    measurement: ReactionMeasurement, barrier_kcal: float | None = None
) -> FitnessRecord:
    """Turn a reaction measurement (plus optional approach barrier) into fitness.

    ``barrier_kcal`` is the M1 relaxed-scan barrier under approach
    (``ApproachScan.barrier_kcal()``); pass None when no scan has been run —
    the record then scores on favorability alone, exactly as in M0.
    """
    if not measurement.ok or measurement.reaction_energy_kcal is None:
        return FitnessRecord(
            spec_id=measurement.spec_id,
            reaction_energy_kcal=measurement.reaction_energy_kcal,
            favorable=None,
            fitness=None,
            valid=False,
            note=measurement.error or "unusable measurement",
        )

    delta = measurement.reaction_energy_kcal
    favorable = delta < 0.0

    if barrier_kcal is None:
        return FitnessRecord(
            spec_id=measurement.spec_id,
            reaction_energy_kcal=delta,
            favorable=favorable,
            fitness=-delta,
            valid=True,
            note="M0: favorability only (feasibility/selectivity not yet measured)",
        )

    feasible = barrier_kcal <= FEASIBLE_BARRIER_KCAL
    fitness = -delta - BARRIER_WEIGHT * barrier_kcal
    return FitnessRecord(
        spec_id=measurement.spec_id,
        reaction_energy_kcal=delta,
        favorable=favorable,
        barrier_kcal=barrier_kcal,
        feasible=feasible,
        fitness=fitness,
        valid=True,
        note=(
            f"M1: fitness = -dE - {BARRIER_WEIGHT}*barrier; feasible gate at "
            f"{FEASIBLE_BARRIER_KCAL} kcal/mol (PBE biases barriers low; "
            "mechanical load lowers real barriers)"
        ),
    )
