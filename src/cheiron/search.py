"""M3 — search, not enumeration: propose the next candidate to measure.

The additive ΔE model (``cheiron.predict``) lets the loop *choose* what to
evaluate next instead of grinding a hand-written grid. The strategy is
explore-then-exploit, expressed as a strict priority:

1. **Anchor an unmeasured factor.** If some tool or workpiece has no usable
   measurement yet, the model cannot predict any cell involving it — one
   measurement (paired with the most-measured partner) pins its whole
   row/column. Highest information per calculation.
2. **Verify the model where it's most confident, on the most promising cell.**
   Once every factor is anchored, every unmeasured cell is predictable; propose
   the one predicted *most favourable* (best candidate for the project goal) and
   publish predicted-vs-measured — the residual is the S3 negative-or-positive
   result the model must earn, not assume.

Selection is pure (no physics); the arbiter disposes. Returns None only when
the grid is fully measured.
"""

from __future__ import annotations

from dataclasses import dataclass

from .predict import fit_additive_model


@dataclass
class Proposal:
    spec_id: str
    tool_id: str
    workpiece_id: str
    predicted_kcal: float | None   # None when proposing an anchor (unpredictable yet)
    rationale: str


def _measured_factors(latest_records: dict[str, dict]) -> tuple[set[str], set[str]]:
    tools: set[str] = set()
    workpieces: set[str] = set()
    for record in latest_records.values():
        fitness = record.get("fitness") or {}
        if not fitness.get("valid") or fitness.get("reaction_energy_kcal") is None:
            continue
        spec = record["spec"]
        tools.add(spec["tool"]["id"])
        workpieces.add(spec["workpiece"]["id"])
    return tools, workpieces


def propose_next(
    latest_records: dict[str, dict],
    tool_ids: list[str],
    workpiece_ids: list[str],
    anchor_workpiece: str = "methane",
    anchor_tool: str = "methane",
) -> Proposal | None:
    """Choose the next abstraction candidate to evaluate (or None if grid done)."""
    measured_tools, measured_workpieces = _measured_factors(latest_records)
    evaluated = {
        r["spec"]["id"] for r in latest_records.values()
        if (r.get("fitness") or {}).get("valid")
    }

    # 1. explore: anchor an unmeasured tool (× a measured workpiece) ...
    for t in tool_ids:
        if t not in measured_tools:
            w = anchor_workpiece if anchor_workpiece in measured_workpieces \
                else (next(iter(measured_workpieces)) if measured_workpieces else workpiece_ids[0])
            return Proposal(f"habs-{t}-{w}", t, w, None,
                            f"anchor: tool '{t}' unmeasured — pins its whole ladder")
    # ... or an unmeasured workpiece (× a measured tool).
    for w in workpiece_ids:
        if w not in measured_workpieces:
            t = anchor_tool if anchor_tool in measured_tools \
                else (next(iter(measured_tools)) if measured_tools else tool_ids[0])
            return Proposal(f"habs-{t}-{w}", t, w, None,
                            f"anchor: workpiece '{w}' unmeasured — pins its whole column")

    # 2. exploit: every factor anchored; verify the most-favourable unmeasured cell.
    model = fit_additive_model(latest_records)
    if model is None:
        return None
    best: Proposal | None = None
    for t in tool_ids:
        for w in workpiece_ids:
            sid = f"habs-{t}-{w}"
            if sid in evaluated:
                continue
            pred = model.predict(t, w)
            if pred is None:
                continue
            if best is None or pred < best.predicted_kcal:
                best = Proposal(sid, t, w, pred,
                                f"verify: model predicts {pred:+.1f} kcal/mol "
                                f"(most favourable unmeasured); publish residual")
    return best
