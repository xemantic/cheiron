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


def score(measurement: ReactionMeasurement) -> FitnessRecord:
    """Turn a reaction measurement into a fitness record."""
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

    # M0 fitness: exothermicity. More negative ΔE -> higher fitness. Feasibility
    # and selectivity terms fold in here as those measurements come online.
    fitness = -delta

    return FitnessRecord(
        spec_id=measurement.spec_id,
        reaction_energy_kcal=delta,
        favorable=favorable,
        fitness=fitness,
        valid=True,
        note="M0: favorability only (feasibility/selectivity not yet measured)",
    )
