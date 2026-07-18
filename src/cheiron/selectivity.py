"""M2 — selectivity: does the tool prefer the intended site over competitors?

A selectivity measurement needs the same tool offered the same molecule
through different C-H sites — separate candidates in the ledger differing only
in ``abstract_site``. This module groups those records and reports the
site preference per (tool, molecule).

The M0-level metric is thermodynamic: rank sites by reaction energy and report
the margin between the best and runner-up. The real (kinetic) selectivity is
the *barrier* difference under approach; it plugs into the same structure once
per-site scans exist. Both are attack-agnostic upper bounds on selectivity —
they say which site the chemistry prefers, not yet whether tool geometry can
physically reach only one of them.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SiteComparison:
    """All evaluated sites of one molecule under one tool, most favorable first."""

    tool_id: str
    molecule: str  # saturated_name of the workpiece
    # (abstract_site, spec_id, reaction_energy_kcal), sorted most favorable first
    sites: list[tuple[str, str, float]] = field(default_factory=list)

    @property
    def preferred_site(self) -> str:
        return self.sites[0][0]

    @property
    def margin_kcal(self) -> float:
        """ΔΔE between the preferred site and the runner-up (positive)."""
        return self.sites[1][2] - self.sites[0][2]

    def to_dict(self) -> dict:
        return {
            "tool_id": self.tool_id,
            "molecule": self.molecule,
            "preferred_site": self.preferred_site,
            "margin_kcal": self.margin_kcal,
            "sites": [
                {"site": s, "spec_id": sid, "reaction_energy_kcal": e}
                for s, sid, e in self.sites
            ],
        }


def site_comparisons(latest_records: dict[str, dict]) -> list[SiteComparison]:
    """Group ledger records into per-(tool, molecule) site comparisons.

    ``latest_records`` is ``Ledger.latest_by_spec()``. Only groups where at
    least two distinct sites have usable measurements yield a comparison.
    """
    groups: dict[tuple[str, str], list[tuple[str, str, float]]] = {}
    for record in latest_records.values():
        fitness = record.get("fitness") or {}
        if not fitness.get("valid") or fitness.get("reaction_energy_kcal") is None:
            continue
        spec = record["spec"]
        key = (spec["tool"]["id"], spec["workpiece"]["saturated_name"])
        groups.setdefault(key, []).append(
            (
                spec["workpiece"]["abstract_site"],
                spec["id"],
                fitness["reaction_energy_kcal"],
            )
        )

    comparisons = []
    for (tool_id, molecule), sites in sorted(groups.items()):
        distinct_sites = {s for s, _, _ in sites}
        if len(distinct_sites) < 2:
            continue
        comparisons.append(
            SiteComparison(
                tool_id=tool_id,
                molecule=molecule,
                sites=sorted(sites, key=lambda t: t[2]),  # most negative dE first
            )
        )
    return comparisons
