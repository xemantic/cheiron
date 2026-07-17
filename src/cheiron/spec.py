"""Candidate specifications — the serializable currency the loop passes around.

A spec says *what to evaluate*, never *how*. Proposers emit specs; the builder
turns a spec into geometry; nothing in a spec touches physics. Specs are plain
dataclasses so they serialize cleanly into the ledger and reproduce exactly.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class ToolSpec:
    """A hydrogen-abstraction tool, named by its *saturated* form.

    ``saturated_name`` is the closed-shell Tool-H (e.g. acetylene 'C2H2' for the
    ethynyl tool); the radical tool Tool· is that molecule minus the hydrogen at
    the site ``donor_site`` ('any' picks the first hydrogen, correct for the
    symmetric ethynyl case).
    """

    id: str
    saturated_name: str
    donor_site: str = "any"


@dataclass(frozen=True)
class WorkpieceSpec:
    """A hydrogenated workpiece, named by its saturated molecule and target site.

    ``abstract_site`` selects which C-H is offered to the tool: 'primary',
    'secondary', 'tertiary', or 'any'.
    """

    id: str
    saturated_name: str
    abstract_site: str = "any"


@dataclass(frozen=True)
class CandidateSpec:
    """A full candidate: a tool acting on a workpiece, plus provenance."""

    id: str
    tool: ToolSpec
    workpiece: WorkpieceSpec
    operation: str = "hydrogen_abstraction"
    generation: int = 0
    parents: tuple[str, ...] = field(default_factory=tuple)
    proposer: str = "enumerative"

    def to_dict(self) -> dict:
        return asdict(self)
