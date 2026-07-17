"""Tier-0 geometry utilities: bonding graph, clash detection, site typing.

These are the cheapest arbiter checks — pure geometry, no energy. They exist to
kill impossible structures before any quantum-chemistry cost is paid, and to
identify reactive sites (e.g. which hydrogen is the tertiary one).
"""

from __future__ import annotations

import numpy as np
from ase import Atoms
from ase.data import covalent_radii


def bond_graph(atoms: Atoms, tolerance: float = 1.2) -> dict[int, list[int]]:
    """Return adjacency (atom index -> neighbour indices) from covalent radii.

    Two atoms are bonded if their distance is within ``tolerance`` times the sum
    of their covalent radii. ``tolerance`` of 1.2 is the usual generous default
    that captures real bonds without linking through-space neighbours.
    """
    positions = atoms.get_positions()
    radii = np.array([covalent_radii[z] for z in atoms.get_atomic_numbers()])
    n = len(atoms)
    graph: dict[int, list[int]] = {i: [] for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            d = np.linalg.norm(positions[i] - positions[j])
            if d < tolerance * (radii[i] + radii[j]):
                graph[i].append(j)
                graph[j].append(i)
    return graph


def has_clash(atoms: Atoms, min_ratio: float = 0.65) -> bool:
    """True if any non-bonded pair is closer than ``min_ratio`` * (r_i + r_j).

    Catches builds where fragments were placed on top of each other. The ratio
    sits below the bonding tolerance so genuine bonds are not flagged as clashes.
    """
    positions = atoms.get_positions()
    radii = np.array([covalent_radii[z] for z in atoms.get_atomic_numbers()])
    n = len(atoms)
    for i in range(n):
        for j in range(i + 1, n):
            d = np.linalg.norm(positions[i] - positions[j])
            if d < min_ratio * (radii[i] + radii[j]):
                return True
    return False


def carbon_substitution(atoms: Atoms, hydrogen_index: int, graph: dict[int, list[int]]) -> int:
    """For a C-H hydrogen, how many carbons the parent carbon is bonded to.

    1 => primary, 2 => secondary, 3 => tertiary, 0 => (e.g.) not on a carbon.
    Used to pick which hydrogen a workpiece exposes for abstraction.
    """
    symbols = atoms.get_chemical_symbols()
    neighbours = graph[hydrogen_index]
    if not neighbours:
        return 0
    parent = neighbours[0]
    if symbols[parent] != "C":
        return 0
    return sum(1 for k in graph[parent] if symbols[k] == "C")


def hydrogen_indices(atoms: Atoms) -> list[int]:
    return [i for i, s in enumerate(atoms.get_chemical_symbols()) if s == "H"]


def connectivity_signature(atoms: Atoms) -> frozenset[tuple[int, int]]:
    """A comparable summary of who-is-bonded-to-whom, for tool-integrity checks.

    Returns the set of bonded index pairs. Comparing signatures before and after
    a reaction step tells us whether a fragment rearranged.
    """
    graph = bond_graph(atoms)
    edges = set()
    for i, neighbours in graph.items():
        for j in neighbours:
            edges.add((min(i, j), max(i, j)))
    return frozenset(edges)
