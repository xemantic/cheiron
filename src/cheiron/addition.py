"""M4 (scaffold) — radical addition: a bond-*forming* operation.

Every step so far transfers a hydrogen (abstraction). Positional assembly also
needs steps that *build* structure — the canonical one being a radical adding
across an unsaturated bond:

    Tool·  +  H2C=CH2  ->  Tool-CH2-CH2·        (the β-carbon carries the radical)

This is genuinely different chemistry from abstraction: a new C-C σ bond forms
at the cost of the alkene π bond, and the reaction energy is
``ΔE = E(adduct·) - E(Tool·) - E(alkene)`` — three species, not four.

This module is the geometry-only first slice: it builds a sane *starting*
adduct (the arbiter will relax it) and returns the three species with correct
spins. It deliberately does **not** touch the shared abstraction builder or
arbiter, so the existing pipeline stays green while the operation grows in
test-backed pieces (next: an addition runner that scores ΔE).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from ase import Atoms

from .builder import Species
from .chemistry.species import (
    pick_abstractable_hydrogen,
    remove_hydrogen,
    saturated,
    unpaired_electrons,
)
from .geometry import bond_graph, has_clash
from .spec import ToolSpec

CC_ADD_BOND = 1.54  # forming C(tool-center)-C(alkene) single bond, Angstrom


class AdditionBuildError(Exception):
    """Raised when a radical-addition system cannot be built."""


@dataclass
class BuiltAddition:
    """The three species of a radical addition, ready for the arbiter."""

    spec_id: str
    tool_radical: Species     # Tool·
    substrate: Species        # the alkene (closed shell)
    adduct_radical: Species   # Tool-CH2-CH2·

    def species(self) -> list[Species]:
        return [self.tool_radical, self.substrate, self.adduct_radical]


def _alkene_double_bond(atoms: Atoms) -> tuple[int, int]:
    """Return the two carbons of the (assumed single) C=C double bond.

    Picked as the closest C-C pair — a double bond is shorter than any single
    C-C — which is unambiguous for the small mono-alkene substrates here.
    """
    symbols = atoms.get_chemical_symbols()
    positions = atoms.get_positions()
    carbons = [i for i, s in enumerate(symbols) if s == "C"]
    best = None
    for a_i in range(len(carbons)):
        for b_i in range(a_i + 1, len(carbons)):
            ca, cb = carbons[a_i], carbons[b_i]
            d = float(np.linalg.norm(positions[ca] - positions[cb]))
            if best is None or d < best[0]:
                best = (d, ca, cb)
    if best is None:
        raise AdditionBuildError("substrate has fewer than two carbons")
    return best[1], best[2]


def _alkene_face_normal(atoms: Atoms, carbon: int, graph: dict[int, list[int]]) -> np.ndarray:
    """Unit normal to the local plane at ``carbon`` — the π face a radical
    attacks. Computed from two of the carbon's substituent directions."""
    positions = atoms.get_positions()
    neighbours = graph[carbon]
    if len(neighbours) < 2:
        raise AdditionBuildError("alkene carbon has too few neighbours for a face normal")
    v1 = positions[neighbours[0]] - positions[carbon]
    v2 = positions[neighbours[1]] - positions[carbon]
    normal = np.cross(v1, v2)
    n = np.linalg.norm(normal)
    if n < 1e-6:
        raise AdditionBuildError("degenerate alkene geometry (collinear substituents)")
    return normal / n


def _place_tool_over_alkene(tool: ToolSpec, substrate_name: str, distance: float):
    """Shared placement: put the tool radical's center ``distance`` Å above the
    anti-Markovnikov (terminal) alkene carbon along its π-face normal.

    Returns (tool_radical, substrate, combined, c_attack, tool_center_combined)
    where indices refer to the combined system (substrate atoms first).
    """
    try:
        tool_h = saturated(tool.saturated_name)
    except Exception as exc:
        raise AdditionBuildError(f"unknown tool molecule {tool.saturated_name!r}: {exc}")
    donor = pick_abstractable_hydrogen(tool_h, tool.donor_site)
    tool_graph = bond_graph(tool_h)
    parent = tool_graph[donor][0]
    tool_radical = remove_hydrogen(tool_h, donor)
    tool_center = parent if parent < donor else parent - 1

    try:
        substrate = saturated(substrate_name)
    except Exception as exc:
        raise AdditionBuildError(f"unknown substrate molecule {substrate_name!r}: {exc}")
    sub_graph = bond_graph(substrate)
    c_a, c_b = _alkene_double_bond(substrate)
    symbols = substrate.get_chemical_symbols()
    def n_h(c: int) -> int:
        return sum(1 for k in sub_graph[c] if symbols[k] == "H")
    c_attack = c_a if n_h(c_a) >= n_h(c_b) else c_b
    normal = _alkene_face_normal(substrate, c_attack, sub_graph)

    tool_moved = tool_radical.copy()
    target = substrate.get_positions()[c_attack] + normal * distance
    tool_moved.translate(target - tool_moved.get_positions()[tool_center])
    combined = substrate + tool_moved
    return tool_radical, substrate, combined, c_attack, len(substrate) + tool_center


@dataclass
class AdditionApproach:
    """The Tool· ... alkene supersystem at one approach distance (for barrier
    scans of the bond-forming coordinate d(tool_center ... alkene_carbon))."""

    atoms: Atoms
    spin: int
    distance: float
    alkene_carbon: int    # the attacked carbon, in the combined system
    tool_center: int      # the tool radical center, in the combined system


def build_addition_approach(
    tool: ToolSpec, substrate_name: str, distance: float
) -> AdditionApproach:
    """Supersystem for an addition approach scan: tool radical ``distance`` Å
    from the alkene attack-carbon along the π-face normal, no bond yet formed.

    Unlike abstraction's approach coordinate (a hydrogen in flight between two
    heavy atoms), the addition coordinate is the tool center closing on the
    alkene carbon; freezing that distance and relaxing the rest traces the
    barrier to C–C bond formation.
    """
    if distance <= 0:
        raise AdditionBuildError(f"approach distance must be positive, got {distance}")
    _tr, _sub, combined, c_attack, tool_center = _place_tool_over_alkene(
        tool, substrate_name, distance
    )
    realized = combined.get_distance(c_attack, tool_center)
    if abs(realized - distance) > 1e-6:
        raise AdditionBuildError(
            f"placement failed: requested d={distance:.4f}, realized {realized:.4f}"
        )
    return AdditionApproach(
        atoms=combined,
        spin=unpaired_electrons(combined),
        distance=distance,
        alkene_carbon=c_attack,
        tool_center=tool_center,
    )


def build_addition(tool: ToolSpec, substrate_name: str, spec_id: str) -> BuiltAddition:
    """Build ``Tool· + alkene -> Tool-CH2-CH2·`` as three species.

    The tool radical is placed with its radical-center carbon ``CC_ADD_BOND``
    above one alkene carbon's π face (perpendicular attack), giving the
    optimizer a sane starting adduct — it will pyramidalize the attacked carbon
    and localize the radical on the other one.
    """
    tool_radical, substrate, adduct, _c_attack, _tc = _place_tool_over_alkene(
        tool, substrate_name, CC_ADD_BOND
    )

    for label, atoms in (
        ("tool_radical", tool_radical),
        ("substrate", substrate),
        ("adduct_radical", adduct),
    ):
        if has_clash(atoms):
            raise AdditionBuildError(f"steric clash in {label} starting geometry")

    return BuiltAddition(
        spec_id=spec_id,
        tool_radical=Species("tool_radical", tool_radical, unpaired_electrons(tool_radical)),
        substrate=Species("substrate", substrate, unpaired_electrons(substrate)),
        adduct_radical=Species("adduct_radical", adduct, unpaired_electrons(adduct)),
    )
