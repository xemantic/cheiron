"""Fast tests for the M4 radical-addition geometry builder (no PySCF)."""

from __future__ import annotations

import numpy as np
import pytest

from cheiron.addition import AdditionBuildError, build_addition
from cheiron.chemistry.library import TOOLS
from cheiron.geometry import bond_graph, has_clash


def test_addition_produces_three_species_with_right_counts():
    built = build_addition(TOOLS["ethynyl"], "C2H4", "add-ethynyl-ethylene")
    roles = {s.role for s in built.species()}
    assert roles == {"tool_radical", "substrate", "adduct_radical"}
    # ethynyl radical C2H (3 atoms) + ethylene C2H4 (6) = adduct C4H5 (9 atoms)
    adduct = built.adduct_radical.atoms
    assert adduct.get_chemical_symbols().count("C") == 4
    assert adduct.get_chemical_symbols().count("H") == 5


def test_addition_spins_are_doublet_radicals():
    built = build_addition(TOOLS["methyl"], "C2H4", "add-methyl-ethylene")
    assert built.tool_radical.spin == 1     # ·CH3, doublet
    assert built.substrate.spin == 0        # ethylene, closed shell
    assert built.adduct_radical.spin == 1   # ·CH2-CH2-CH3, doublet


def test_addition_forms_a_new_carbon_carbon_bond():
    """The starting adduct must place the tool's radical carbon within bonding
    range of an alkene carbon — the σ bond the optimizer will complete."""
    built = build_addition(TOOLS["methyl"], "C2H4", "add-methyl-ethylene")
    adduct = built.adduct_radical.atoms
    graph = bond_graph(adduct)
    symbols = adduct.get_chemical_symbols()
    # ethylene carbons are indices 0..1 (substrate placed first); tool carbon(s) after
    n_sub = 6  # C2H4
    tool_carbons = [i for i in range(n_sub, len(adduct)) if symbols[i] == "C"]
    sub_carbons = [i for i in range(n_sub) if symbols[i] == "C"]
    # at least one tool carbon is bonded to at least one substrate carbon
    assert any(sc in graph[tc] for tc in tool_carbons for sc in sub_carbons)
    assert not has_clash(adduct)


def test_addition_rejects_non_alkene_substrate():
    with pytest.raises(AdditionBuildError):
        build_addition(TOOLS["methyl"], "CH4", "add-methyl-methane")  # no C=C, one carbon
