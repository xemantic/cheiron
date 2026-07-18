"""M2 — tool integrity: did the step do exactly what it claimed, and nothing else?

A hydrogen-abstraction step is allowed to change the bonding graph in exactly
two ways: the target H may detach from its workpiece carbon, and it may attach
to the tool's radical center. Any other connectivity change — the tool
rearranging, the workpiece fragmenting, a bond to the wrong site — means the
"result" is not the reaction we scored, however good its energy looks. This is
a hard gate, not a score component (docs/design/03-milestones.md).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from ase import Atoms

from .geometry import connectivity_signature


def atoms_from_xyz_body(text: str) -> Atoms:
    """Parse the bare ``symbol x y z`` lines cheiron stores in ``final_xyz``."""
    symbols, positions = [], []
    for line in text.strip().splitlines():
        parts = line.split()
        symbols.append(parts[0])
        positions.append([float(x) for x in parts[1:4]])
    return Atoms(symbols=symbols, positions=np.array(positions))


@dataclass
class IntegrityResult:
    ok: bool
    transferred: bool  # did the target H move from workpiece to tool?
    unexpected_gained: list[tuple[int, int]] = field(default_factory=list)
    unexpected_lost: list[tuple[int, int]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "transferred": self.transferred,
            "unexpected_gained": [list(e) for e in self.unexpected_gained],
            "unexpected_lost": [list(e) for e in self.unexpected_lost],
        }


def _edge(i: int, j: int) -> tuple[int, int]:
    return (min(i, j), max(i, j))


def check_step_integrity(
    initial: Atoms,
    final: Atoms,
    target_h: int,
    workpiece_carbon: int,
    tool_center: int,
) -> IntegrityResult:
    """Compare bonding graphs; only the intended H-transfer edges may differ.

    ``initial`` and ``final`` must index atoms identically (cheiron's scans
    never reorder). The allowed changes are losing (target_h, workpiece_carbon)
    and gaining (target_h, tool_center); partial transfer (neither or both
    edges present) is fine at intermediate scan points — what matters is that
    nothing *else* changed.
    """
    if len(initial) != len(final):
        raise ValueError("initial and final structures differ in atom count")

    sig0 = connectivity_signature(initial)
    sig1 = connectivity_signature(final)
    allowed = {_edge(target_h, workpiece_carbon), _edge(target_h, tool_center)}

    unexpected_gained = sorted(e for e in sig1 - sig0 if e not in allowed)
    unexpected_lost = sorted(e for e in sig0 - sig1 if e not in allowed)
    transferred = (
        _edge(target_h, tool_center) in sig1
        and _edge(target_h, workpiece_carbon) not in sig1
    )
    return IntegrityResult(
        ok=not unexpected_gained and not unexpected_lost,
        transferred=transferred,
        unexpected_gained=unexpected_gained,
        unexpected_lost=unexpected_lost,
    )
