"""The tool and workpiece libraries the proposers draw from.

Small and hand-curated for M0. The evolutionary/agent proposers (M3) will grow
this space rather than replace it.
"""

from __future__ import annotations

from ..spec import ToolSpec, WorkpieceSpec

# Hydrogen-abstraction tools, keyed by id. Named by their saturated (Tool-H)
# form; the radical is that molecule minus the donor hydrogen.
TOOLS: dict[str, ToolSpec] = {
    # The canonical ethynyl radical tool, H-C#C· , saturated form = acetylene.
    # A strong abstractor (acetylene C-H ~133 kcal/mol).
    "ethynyl": ToolSpec(id="ethynyl", saturated_name="C2H2", donor_site="any"),
    # Methyl radical, ·CH3 (saturated form = methane, C-H ~105 kcal/mol). A
    # deliberately WEAK abstractor: it should be roughly thermoneutral on primary
    # C-H and only mildly favorable on tertiary. Included so the loop has to
    # discriminate a good tool from a poor one, and so the ledger records honest
    # marginal/unfavorable steps, not just wins.
    "methyl": ToolSpec(id="methyl", saturated_name="CH4", donor_site="any"),
}

# Hydrogenated workpieces, cheap -> realistic (the M0 "workpiece ladder").
# Site types span primary / secondary / tertiary C-H, plus a strained ring.
WORKPIECES: dict[str, WorkpieceSpec] = {
    "methane": WorkpieceSpec(id="methane", saturated_name="CH4", abstract_site="any"),
    "ethane": WorkpieceSpec(id="ethane", saturated_name="C2H6", abstract_site="primary"),
    "propane": WorkpieceSpec(id="propane", saturated_name="C3H8", abstract_site="secondary"),
    "butane": WorkpieceSpec(id="butane", saturated_name="trans-butane", abstract_site="secondary"),
    # Cyclobutane's strained secondary C-H — a step toward rigid, cage-like sites
    # that better model a real surface than floppy chains do.
    "cyclobutane": WorkpieceSpec(id="cyclobutane", saturated_name="cyclobutane", abstract_site="secondary"),
    "isobutane": WorkpieceSpec(id="isobutane", saturated_name="isobutane", abstract_site="tertiary"),
    # Adamantane: rigid diamondoid cage, the closest small-molecule model of a
    # diamond C(111) surface site. Tertiary C-H is the abstraction target.
    # Custom-built geometry (not in G2) — see chemistry.species.
    "adamantane": WorkpieceSpec(id="adamantane", saturated_name="adamantane", abstract_site="tertiary"),
    # The SAME cage offered through its secondary (CH2) site — the M2
    # selectivity probe: a selective tool should prefer the tertiary site above;
    # the margin between the two candidates is the site-preference measurement.
    "adamantane-2h": WorkpieceSpec(id="adamantane-2h", saturated_name="adamantane", abstract_site="secondary"),
}
