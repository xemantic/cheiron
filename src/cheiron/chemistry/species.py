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

from ase import Atoms
from ase.build import molecule as g2_molecule

from ..geometry import bond_graph, carbon_substitution, hydrogen_indices


def saturated(name: str) -> Atoms:
    """A closed-shell molecule by G2 name (e.g. 'CH4', 'C2H2', 'isobutane')."""
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

    ``site`` is one of 'primary', 'secondary', 'tertiary', or 'any'. For a site
    type we return a hydrogen whose parent carbon has the matching substitution
    (tertiary = parent carbon bonded to three other carbons). Raises if none.
    """
    graph = bond_graph(atoms)
    wanted = {"primary": 1, "secondary": 2, "tertiary": 3}.get(site)
    candidates = hydrogen_indices(atoms)
    if wanted is None:  # 'any'
        if not candidates:
            raise ValueError("molecule has no hydrogen to abstract")
        return candidates[0]
    for h in candidates:
        if carbon_substitution(atoms, h, graph) == wanted:
            return h
    raise ValueError(f"no {site} C-H hydrogen found in molecule")
