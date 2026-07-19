"""Species construction: saturated molecules and the radicals derived from them.

Everything the M0 hydrogen-abstraction chemistry needs reduces to two moves:

  * take a named closed-shell molecule (from ASE's G2 collection), and
  * remove one hydrogen to produce an open-shell radical.

The reaction  ``Tool· + H-W  ->  Tool-H + ·W``  is then expressed with four
species: the saturated tool ``Tool-H``, the tool radical ``Tool·``, the
saturated workpiece ``H-W``, and the product radical ``·W`` — each just a
molecule and, for the radicals, the index of the hydrogen that was removed.
"""

from __future__ import annotations

import numpy as np
from ase import Atoms
from ase.build import molecule as g2_molecule

from ..geometry import bond_graph, carbon_substitution, hydrogen_indices

DIAMOND_A = 3.5668  # diamond lattice constant, Angstrom
CH_BOND = 1.09      # placed C-H length, Angstrom (refined by the optimizer)


def _build_adamantane() -> Atoms:
    """Adamantane (C10H16) carved from the diamond lattice — exact Td geometry.

    Not in ASE's G2 set, and hand-typed coordinates are untrustworthy, so we
    construct it: the cage is 10 diamond lattice sites (in units of a/4 —
    4 CH carbons on one sublattice, 6 CH2 on the other), and every dangling
    tetrahedral direction gets a hydrogen. Diamond bonding directions alternate
    by sublattice: sites with all-even coordinates bond along D, all-odd sites
    along -D.
    """
    D = np.array([(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)])
    ch_sites = [(1, 1, 1), (3, 3, 1), (3, 1, 3), (1, 3, 3)]        # tertiary
    ch2_sites = [(0, 2, 2), (2, 0, 2), (2, 2, 0),
                 (2, 2, 4), (2, 4, 2), (4, 2, 2)]                   # secondary
    carbons = {tuple(c) for c in ch_sites + ch2_sites}

    scale = DIAMOND_A / 4.0
    symbols, positions = [], []
    for site in ch_sites + ch2_sites:
        site = np.array(site)
        symbols.append("C")
        positions.append(site * scale)
        offsets = -D if site[0] % 2 else D  # sublattice by parity
        for off in offsets:
            if tuple(site + off) not in carbons:  # dangling bond -> hydrogen
                symbols.append("H")
                positions.append(site * scale + off / np.linalg.norm(off) * CH_BOND)
    return Atoms(symbols=symbols, positions=positions)


CC_SP3_SP = 1.47   # C(sp3)-C(sp) single bond, Angstrom
CC_TRIPLE = 1.20   # C#C triple bond
CH_SP = 1.066      # acetylenic C-H


def _build_ethynyl_adamantane() -> Atoms:
    """1-ethynyladamantane (C12H16): an ethynyl tip on a diamondoid handle.

    The first *handle-mounted* tool — real mechanosynthesis tooltips are
    moieties on rigid frames a positioning machine can hold, not free
    radicals. Built by replacing one bridgehead hydrogen of the lattice-carved
    adamantane with a collinear C#C-H group. The acetylenic tip hydrogen is
    the only 'primary'-classified H in the molecule (its carbon has exactly
    one carbon neighbour), so donor_site='primary' selects the tip.
    """
    atoms = _build_adamantane()
    graph = bond_graph(atoms)
    tip_h = next(
        i for i in hydrogen_indices(atoms) if carbon_substitution(atoms, i, graph) == 3
    )
    parent = graph[tip_h][0]
    positions = atoms.get_positions()
    direction = positions[tip_h] - positions[parent]
    direction /= np.linalg.norm(direction)
    base = positions[parent].copy()

    del atoms[tip_h]
    for symbol, dist in (
        ("C", CC_SP3_SP),
        ("C", CC_SP3_SP + CC_TRIPLE),
        ("H", CC_SP3_SP + CC_TRIPLE + CH_SP),
    ):
        atoms += Atoms(symbol, positions=[base + direction * dist])
    return atoms


# Molecules the arbiter needs that ASE's G2 collection does not provide.
CUSTOM_MOLECULES = {
    "adamantane": _build_adamantane,
    "ethynyl-adamantane": _build_ethynyl_adamantane,
}


def saturated(name: str) -> Atoms:
    """A closed-shell molecule by G2 name (e.g. 'CH4', 'C2H2', 'isobutane'),
    or one of the custom-built molecules (e.g. 'adamantane')."""
    if name in CUSTOM_MOLECULES:
        return CUSTOM_MOLECULES[name]()
    return g2_molecule(name)


def electron_count(atoms: Atoms) -> int:
    return int(sum(atoms.get_atomic_numbers()))


def unpaired_electrons(atoms: Atoms, charge: int = 0) -> int:
    """Minimal number of unpaired electrons implied by electron parity.

    Even electron count -> 0 (singlet), odd -> 1 (doublet). This is the correct
    ground-state assumption for the small closed-shell molecules and the simple
    C/H radicals in M0; higher-spin states would be set explicitly elsewhere.
    """
    return (electron_count(atoms) - charge) % 2


def remove_hydrogen(atoms: Atoms, hydrogen_index: int) -> Atoms:
    """Return a copy with the given hydrogen deleted (an abstraction product)."""
    if atoms.get_chemical_symbols()[hydrogen_index] != "H":
        raise ValueError(f"atom {hydrogen_index} is not hydrogen")
    radical = atoms.copy()
    del radical[hydrogen_index]
    return radical


def pick_abstractable_hydrogen(atoms: Atoms, site: str) -> int:
    """Index of a hydrogen matching a requested site type.

    ``site`` is one of 'primary', 'secondary', 'tertiary', 'carbon', or 'any'.
    'primary'/'secondary'/'tertiary' select a hydrogen whose parent carbon has
    the matching number of carbon neighbours. 'carbon' selects any C-H
    regardless of substitution — needed for heteroatom molecules whose reactive
    C-H sits on a carbon with no carbon neighbours (e.g. methanol's α C-H,
    which must be told apart from the O-H). 'any' takes the first hydrogen and
    is correct only for molecules where every H is equivalent (e.g. the
    symmetric radical tools). Raises if no match.
    """
    graph = bond_graph(atoms)
    symbols = atoms.get_chemical_symbols()
    candidates = hydrogen_indices(atoms)
    if site == "any":
        if not candidates:
            raise ValueError("molecule has no hydrogen to abstract")
        return candidates[0]
    if site == "carbon":
        for h in candidates:
            parent = graph[h][0] if graph[h] else None
            if parent is not None and symbols[parent] == "C":
                return h
        raise ValueError("no C-H hydrogen found in molecule")
    wanted = {"primary": 1, "secondary": 2, "tertiary": 3}.get(site)
    if wanted is None:
        raise ValueError(f"unknown site type {site!r}")
    for h in candidates:
        if carbon_substitution(atoms, h, graph) == wanted:
            return h
    raise ValueError(f"no {site} C-H hydrogen found in molecule")
