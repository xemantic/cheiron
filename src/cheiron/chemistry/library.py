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
    "ethynyl": ToolSpec(id="ethynyl", saturated_name="C2H2", donor_site="any"),
}

# Hydrogenated workpieces, cheap -> realistic (the M0 "workpiece ladder").
WORKPIECES: dict[str, WorkpieceSpec] = {
    "methane": WorkpieceSpec(id="methane", saturated_name="CH4", abstract_site="any"),
    "isobutane": WorkpieceSpec(
        id="isobutane", saturated_name="isobutane", abstract_site="tertiary"
    ),
    # Ethane's primary C-H, a useful mid-point on the ladder.
    "ethane": WorkpieceSpec(id="ethane", saturated_name="C2H6", abstract_site="primary"),
}
