"""M3 — ledger-informed prediction: additivity as a search prior.

The M0/M2 measurements showed ΔE decomposes cleanly into a tool term plus a
workpiece term (cross-tool agreement ≤0.1 kcal/mol over the whole grid). That
regularity is a *search prior*: fit the additive model to everything the
ledger has measured, predict every unevaluated (tool, workpiece) pair, and
spend QM time where it is most informative — one methane measurement per new
tool pins that tool's entire ladder.

Predictions are proposals, never results: nothing predicted here may enter
the ledger as a measurement. The arbiter disposes.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class AdditiveModel:
    mean: float
    tool_terms: dict[str, float]
    workpiece_terms: dict[str, float]
    residual_max_kcal: float  # worst training-set residual — honesty metric

    def predict(self, tool_id: str, workpiece_id: str) -> float | None:
        """Predicted ΔE (kcal/mol), or None if either factor is unseen."""
        if tool_id not in self.tool_terms or workpiece_id not in self.workpiece_terms:
            return None
        return self.mean + self.tool_terms[tool_id] + self.workpiece_terms[workpiece_id]


def fit_additive_model(latest_records: dict[str, dict]) -> AdditiveModel | None:
    """Least-squares fit of ΔE(t, w) = μ + a_t + b_w over usable ledger records.

    ``latest_records`` is ``Ledger.latest_by_spec()``. Returns None with fewer
    than two usable measurements. Terms are centered (sum to zero) so μ is the
    grand mean and the terms are comparable across fits.
    """
    rows = []
    for record in latest_records.values():
        fitness = record.get("fitness") or {}
        if not fitness.get("valid") or fitness.get("reaction_energy_kcal") is None:
            continue
        spec = record["spec"]
        rows.append(
            (spec["tool"]["id"], spec["workpiece"]["id"], fitness["reaction_energy_kcal"])
        )
    if len(rows) < 2:
        return None

    tools = sorted({t for t, _, _ in rows})
    workpieces = sorted({w for _, w, _ in rows})
    t_index = {t: i for i, t in enumerate(tools)}
    w_index = {w: i for i, w in enumerate(workpieces)}

    # Design: [1 | tool one-hots | workpiece one-hots]; lstsq handles the
    # gauge freedom, centering fixes it afterwards.
    a = np.zeros((len(rows), 1 + len(tools) + len(workpieces)))
    y = np.zeros(len(rows))
    for i, (t, w, de) in enumerate(rows):
        a[i, 0] = 1.0
        a[i, 1 + t_index[t]] = 1.0
        a[i, 1 + len(tools) + w_index[w]] = 1.0
        y[i] = de
    coef, *_ = np.linalg.lstsq(a, y, rcond=None)

    tool_terms = {t: float(coef[1 + t_index[t]]) for t in tools}
    workpiece_terms = {w: float(coef[1 + len(tools) + w_index[w]]) for w in workpieces}
    t_shift = float(np.mean(list(tool_terms.values())))
    w_shift = float(np.mean(list(workpiece_terms.values())))
    tool_terms = {t: v - t_shift for t, v in tool_terms.items()}
    workpiece_terms = {w: v - w_shift for w, v in workpiece_terms.items()}
    mean = float(coef[0]) + t_shift + w_shift

    residuals = [
        abs(mean + tool_terms[t] + workpiece_terms[w] - de) for t, w, de in rows
    ]
    return AdditiveModel(
        mean=mean,
        tool_terms=tool_terms,
        workpiece_terms=workpiece_terms,
        residual_max_kcal=float(max(residuals)),
    )


def rank_unevaluated(
    model: AdditiveModel,
    tool_ids: list[str],
    workpiece_ids: list[str],
    evaluated_spec_ids: set[str],
) -> list[tuple[str, float | None]]:
    """Unevaluated candidate spec ids, most promising (most negative ΔE) first.

    Pairs the model cannot predict (unseen tool or workpiece) sort last with
    prediction None — those are exactly the ones worth one anchoring
    measurement (tool × methane) before trusting the model.
    """
    proposals = []
    for tool_id in tool_ids:
        for workpiece_id in workpiece_ids:
            spec_id = f"habs-{tool_id}-{workpiece_id}"
            if spec_id in evaluated_spec_ids:
                continue
            proposals.append((spec_id, model.predict(tool_id, workpiece_id)))
    return sorted(
        proposals, key=lambda p: (p[1] is None, p[1] if p[1] is not None else 0.0)
    )
