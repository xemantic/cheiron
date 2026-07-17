"""PROPOSE stage: emit candidate specs. Proposers never touch physics.

Only the enumerative proposer exists for M0 — a deterministic sweep of the
tool x workpiece grid, which is exactly what a reproduction milestone wants.
Evolutionary and agent proposers (M3) will subclass this interface and take the
ledger's history as input.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator

from .chemistry.library import TOOLS, WORKPIECES
from .spec import CandidateSpec, ToolSpec, WorkpieceSpec


def _candidate_id(tool: ToolSpec, workpiece: WorkpieceSpec) -> str:
    return f"habs-{tool.id}-{workpiece.id}"


def enumerate_candidates(
    tools: Iterable[str] | None = None,
    workpieces: Iterable[str] | None = None,
) -> Iterator[CandidateSpec]:
    """Yield one candidate per (tool, workpiece) pair from the library.

    ``tools``/``workpieces`` restrict the sweep to the given library ids; None
    means "all". Order is stable, so runs reproduce.
    """
    tool_ids = list(tools) if tools is not None else list(TOOLS)
    workpiece_ids = list(workpieces) if workpieces is not None else list(WORKPIECES)
    for tool_id in tool_ids:
        for workpiece_id in workpiece_ids:
            tool = TOOLS[tool_id]
            workpiece = WORKPIECES[workpiece_id]
            yield CandidateSpec(
                id=_candidate_id(tool, workpiece),
                tool=tool,
                workpiece=workpiece,
                generation=0,
                proposer="enumerative",
            )
