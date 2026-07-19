"""Automated physics-consistency checks on the abstraction ledger.

The arbiter computes each candidate independently, so relationships that *must*
hold between candidates are free internal checks — if one breaks, a pipeline
bug (bad convergence, wrong spin, drifted reference) is the cause. This module
turns two such relationships into standing guards:

- **Reversibility.** Abstraction ΔE(tool A from workpiece B) =
  BDE(B–H) − BDE(A–H) = −ΔE(B from A). So two candidates whose tool and
  workpiece *saturated molecules are swapped* are the same reaction reversed,
  and their ΔE must sum to zero. (Recovered to the decimal for silyl+methane /
  methyl+silane: +19.7 / −19.7.)
- **Identity.** A tool abstracting from its own saturated form (A from A) is
  thermoneutral by symmetry: ΔE = 0. (methyl+methane = 0.0.)

Both are consequences of ΔE being a difference of bond strengths; neither is
told to the loop.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ReversibilityFinding:
    forward_id: str
    reverse_id: str
    forward_kcal: float
    reverse_kcal: float

    @property
    def residual_kcal(self) -> float:
        """ΔE_forward + ΔE_reverse — should be ~0 (self-reverse: just ΔE)."""
        return self.forward_kcal + self.reverse_kcal

    def ok(self, tol: float = 0.2) -> bool:
        return abs(self.residual_kcal) <= tol


def check_reversibility(latest_records: dict[str, dict]) -> list[ReversibilityFinding]:
    """Find reverse-reaction pairs in the ledger and report ΔE_f + ΔE_r.

    ``latest_records`` is ``Ledger.latest_by_spec()``. Returns one finding per
    unordered (forward, reverse) pair where the tool/workpiece saturated
    molecules are swapped — including self-reverse pairs (A from A), whose
    residual is the candidate's own ΔE (which must be ~0).
    """
    # index usable abstraction candidates by (tool_saturated, workpiece_saturated)
    by_pair: dict[tuple[str, str], tuple[str, float]] = {}
    for record in latest_records.values():
        fitness = record.get("fitness") or {}
        if not fitness.get("valid") or fitness.get("reaction_energy_kcal") is None:
            continue
        spec = record["spec"]
        key = (spec["tool"]["saturated_name"], spec["workpiece"]["saturated_name"])
        by_pair[key] = (spec["id"], fitness["reaction_energy_kcal"])

    findings: list[ReversibilityFinding] = []
    seen: set[frozenset] = set()
    for (a, b), (fid, fkcal) in by_pair.items():
        rev = by_pair.get((b, a))
        if rev is None:
            continue
        tag = frozenset({(a, b), (b, a)})
        if tag in seen:
            continue
        seen.add(tag)
        rid, rkcal = rev
        findings.append(ReversibilityFinding(fid, rid, fkcal, rkcal))
    return findings
