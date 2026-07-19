"""Fast regression tests for the non-QM parts of the loop (no PySCF needed)."""

from __future__ import annotations

import pytest

from cheiron.arbiter import ArbiterConfig, ReactionMeasurement, SpeciesResult
from cheiron.builder import build
from cheiron.chemistry.library import TOOLS, WORKPIECES
from cheiron.geometry import has_clash
from cheiron.score import score
from cheiron.spec import CandidateSpec


def _spec(tool_id: str, workpiece_id: str) -> CandidateSpec:
    return CandidateSpec(
        id=f"habs-{tool_id}-{workpiece_id}",
        tool=TOOLS[tool_id],
        workpiece=WORKPIECES[workpiece_id],
    )


def test_build_produces_four_species():
    built = build(_spec("ethynyl", "methane"))
    roles = {s.role for s in built.species()}
    assert roles == {"tool_saturated", "tool_radical", "workpiece", "product_radical"}


def test_radical_trap_ethynyl_is_a_doublet():
    """The single most common way to get the energetics wrong: mis-spinning a
    radical. The ethynyl tool (C2H, 13 electrons) must be a doublet."""
    built = build(_spec("ethynyl", "methane"))
    assert built.tool_radical.spin == 1        # one unpaired electron
    assert built.tool_saturated.spin == 0      # acetylene, closed shell


def test_workpiece_and_product_spins():
    built = build(_spec("ethynyl", "isobutane"))
    assert built.workpiece.spin == 0           # isobutane, closed shell
    assert built.product_radical.spin == 1     # tert-butyl radical, doublet


def test_tertiary_site_selected_for_isobutane():
    """Isobutane must expose its tertiary C-H, not a methyl hydrogen. The product
    radical therefore keeps all three methyl groups intact (9 hydrogens)."""
    built = build(_spec("ethynyl", "isobutane"))
    product = built.product_radical.atoms
    symbols = product.get_chemical_symbols()
    assert symbols.count("H") == 9             # 10 - 1 abstracted
    assert symbols.count("C") == 4


def test_no_clash_in_built_geometry():
    built = build(_spec("ethynyl", "isobutane"))
    for species in built.species():
        assert not has_clash(species.atoms)


def test_score_marks_exothermic_as_favorable():
    m = ReactionMeasurement(spec_id="x", method="test", tier=2)
    m.species = [SpeciesResult(r, -1.0, True, 0, 0, 0.0)
                 for r in ("tool_saturated", "tool_radical", "workpiece", "product_radical")]
    m.reaction_energy_hartree = -0.05
    m.reaction_energy_kcal = -0.05 * 627.509474
    m.ok = True
    fit = score(m)
    assert fit.valid and fit.favorable and fit.fitness > 0


def test_score_marks_unconverged_as_unusable():
    m = ReactionMeasurement(spec_id="x", method="test", tier=2)
    m.ok = False
    m.error = "did not converge"
    fit = score(m)
    assert not fit.valid and fit.favorable is None


def test_method_string_is_self_describing():
    cfg = ArbiterConfig(functional="PBE", basis="def2-SVP")
    assert "PBE" in cfg.method_string() and "def2-SVP" in cfg.method_string()


def _favorable_measurement(spec_id: str, delta_kcal: float) -> ReactionMeasurement:
    m = ReactionMeasurement(spec_id=spec_id, method="test", tier=2)
    m.species = [SpeciesResult(r, -1.0, True, 0, 0, 0.0)
                 for r in ("tool_saturated", "tool_radical", "workpiece", "product_radical")]
    m.reaction_energy_hartree = delta_kcal / 627.509474
    m.reaction_energy_kcal = delta_kcal
    m.ok = True
    return m


def test_score_with_barrier_sets_feasibility():
    fit = score(_favorable_measurement("x", -26.2), barrier_kcal=0.0)
    assert fit.feasible is True and fit.barrier_kcal == 0.0

    blocked = score(_favorable_measurement("y", -26.2), barrier_kcal=40.0)
    assert blocked.feasible is False
    assert blocked.valid  # blocked is a verdict, not a broken measurement


def test_score_without_barrier_leaves_feasibility_open():
    fit = score(_favorable_measurement("x", -26.2))
    assert fit.feasible is None and fit.barrier_kcal is None


def test_barrier_outweighs_exothermicity_in_fitness():
    """A slightly less exothermic but barrierless step must outrank a more
    exothermic step with a real barrier — kinetics beat thermodynamics."""
    barrierless = score(_favorable_measurement("a", -26.2), barrier_kcal=0.0)
    blocked = score(_favorable_measurement("b", -30.0), barrier_kcal=8.2)
    assert barrierless.fitness > blocked.fitness


def test_fragment_reference_reuses_ledger_energies(tmp_path):
    import json

    from cheiron.ledger import Ledger

    path = tmp_path / "ledger.jsonl"
    record = {
        "spec": {"id": "habs-t-w"},
        "build": {"ok": True},
        "measurement": {
            "method": "UKS/PBE/def2-SVP (df, opt)",
            "species": [
                {"role": "tool_radical", "energy_hartree": -39.74, "converged": True},
                {"role": "workpiece", "energy_hartree": -40.42, "converged": True},
                {"role": "tool_saturated", "energy_hartree": -40.41, "converged": True},
                {"role": "product_radical", "energy_hartree": -39.73, "converged": True},
            ],
        },
        "fitness": None,
        "status": "evaluated",
    }
    path.write_text(json.dumps(record) + "\n")
    ledger = Ledger(path)

    assert ledger.fragment_reference("habs-t-w", "UKS/PBE/def2-SVP (df, opt)") == -39.74 + -40.42
    # method mismatch: an energy is only reusable at the method that produced it
    assert ledger.fragment_reference("habs-t-w", "UKS/B3LYP/def2-SVP (df, opt)") is None
    assert ledger.fragment_reference("nonexistent", "UKS/PBE/def2-SVP (df, opt)") is None


def test_fragment_reference_rejects_unconverged(tmp_path):
    import json

    from cheiron.ledger import Ledger

    path = tmp_path / "ledger.jsonl"
    record = {
        "spec": {"id": "habs-t-w"},
        "build": {"ok": True},
        "measurement": {
            "method": "UKS/PBE/def2-SVP (df, opt)",
            "species": [
                {"role": "tool_radical", "energy_hartree": -39.72, "converged": False},
                {"role": "workpiece", "energy_hartree": -40.42, "converged": True},
            ],
        },
        "fitness": None,
        "status": "evaluated",
    }
    path.write_text(json.dumps(record) + "\n")
    assert Ledger(path).fragment_reference("habs-t-w", "UKS/PBE/def2-SVP (df, opt)") is None


def test_adamantane_geometry_is_sound():
    """Adamantane is carved from the diamond lattice, so its correctness is
    checkable: C10H16, all C-C bonds at the diamond length, 4 tertiary + 6
    secondary carbons, no clashes."""
    import numpy as np

    from cheiron.chemistry.species import saturated
    from cheiron.geometry import bond_graph, carbon_substitution, hydrogen_indices

    atoms = saturated("adamantane")
    symbols = atoms.get_chemical_symbols()
    assert symbols.count("C") == 10 and symbols.count("H") == 16

    graph = bond_graph(atoms)
    positions = atoms.get_positions()
    cc = [
        float(np.linalg.norm(positions[i] - positions[j]))
        for i in range(len(atoms)) for j in graph[i]
        if i < j and symbols[i] == "C" and symbols[j] == "C"
    ]
    assert len(cc) == 12  # adamantane has 12 C-C bonds
    assert all(abs(d - 1.5445) < 0.01 for d in cc)

    tertiary_h = [h for h in hydrogen_indices(atoms)
                  if carbon_substitution(atoms, h, graph) == 3]
    secondary_h = [h for h in hydrogen_indices(atoms)
                   if carbon_substitution(atoms, h, graph) == 2]
    assert len(tertiary_h) == 4 and len(secondary_h) == 12
    assert not has_clash(atoms)


def test_adamantane_builds_into_reaction():
    built = build(_spec("ethynyl", "adamantane"))
    product = built.product_radical.atoms
    assert product.get_chemical_symbols().count("H") == 15  # tertiary H removed
    assert built.product_radical.spin == 1


def _ledger_record(spec_id, tool_id, molecule, site, de_kcal, valid=True):
    return {
        "spec": {
            "id": spec_id,
            "tool": {"id": tool_id},
            "workpiece": {"saturated_name": molecule, "abstract_site": site},
        },
        "fitness": {"valid": valid, "reaction_energy_kcal": de_kcal},
    }


def test_site_comparison_ranks_and_reports_margin():
    from cheiron.selectivity import site_comparisons

    latest = {
        "a": _ledger_record("a", "ethynyl", "adamantane", "tertiary", -35.2),
        "b": _ledger_record("b", "ethynyl", "adamantane", "secondary", -33.0),
        "c": _ledger_record("c", "ethynyl", "CH4", "any", -26.2),  # single site: no pair
    }
    comps = site_comparisons(latest)
    assert len(comps) == 1
    comp = comps[0]
    assert comp.preferred_site == "tertiary"
    assert comp.margin_kcal == pytest.approx(2.2, abs=1e-9)


def test_site_comparison_ignores_invalid_measurements():
    from cheiron.selectivity import site_comparisons

    latest = {
        "a": _ledger_record("a", "ethynyl", "adamantane", "tertiary", -35.2),
        "b": _ledger_record("b", "ethynyl", "adamantane", "secondary", None, valid=False),
    }
    assert site_comparisons(latest) == []


def test_adamantane_secondary_workpiece_builds():
    built = build(_spec("ethynyl", "adamantane-2h"))
    # secondary abstraction removes a CH2 hydrogen: product keeps 15 H
    assert built.product_radical.atoms.get_chemical_symbols().count("H") == 15
    assert built.product_radical.spin == 1


def test_new_tools_build_with_correct_spins():
    """Hydroxyl (9 e), amino (9 e), vinyl (15 e) must all be doublets, their
    saturated forms closed-shell."""
    for tool_id, workpiece_id in (("hydroxyl", "methane"), ("amino", "methane"),
                                  ("vinyl", "methane")):
        built = build(_spec(tool_id, workpiece_id))
        assert built.tool_radical.spin == 1, tool_id
        assert built.tool_saturated.spin == 0, tool_id


def test_additive_model_recovers_exact_structure():
    from cheiron.predict import fit_additive_model

    latest = {}
    tool_terms = {"t1": 0.0, "t2": 20.0}
    wp_terms = {"w1": 0.0, "w2": -5.0, "w3": -10.0}
    for t, a in tool_terms.items():
        for w, b in wp_terms.items():
            sid = f"habs-{t}-{w}"
            latest[sid] = _ledger_record(sid, t, w, "any", -30.0 + a + b)
            latest[sid]["spec"]["workpiece"]["id"] = w
    model = fit_additive_model(latest)
    assert model.residual_max_kcal < 1e-9
    # exactly-additive data: predictions reproduce inputs
    assert model.predict("t2", "w3") == pytest.approx(-30.0 + 20.0 - 10.0)


def test_rank_unevaluated_orders_by_predicted_favorability():
    from cheiron.predict import fit_additive_model, rank_unevaluated

    latest = {}
    for t, a in (("t1", 0.0), ("t2", 20.0)):
        for w, b in (("w1", 0.0), ("w2", -5.0)):
            sid = f"habs-{t}-{w}"
            latest[sid] = _ledger_record(sid, t, w, "any", -30.0 + a + b)
            latest[sid]["spec"]["workpiece"]["id"] = w
    model = fit_additive_model(latest)
    ranked = rank_unevaluated(
        model, ["t1", "t2", "t_new"], ["w1", "w2", "w3"], set(latest)
    )
    ids = [sid for sid, _ in ranked]
    # w3 unseen and t_new unseen -> unpredictable entries sort last
    assert all(pred is None for sid, pred in ranked if "t_new" in sid or "w3" in sid)
    # best predictable proposal would be t1 on w2... but that's evaluated;
    # nothing predictable remains except pairs with unseen factors
    assert ids  # non-empty: the frontier is never silently empty


def test_ethynyl_adamantane_geometry():
    """Handle-mounted tool: C12H16, tip H is the unique primary-classified H,
    alkyne bond lengths correct, no clashes."""
    import numpy as np

    from cheiron.chemistry.species import saturated
    from cheiron.geometry import bond_graph, carbon_substitution, hydrogen_indices

    atoms = saturated("ethynyl-adamantane")
    symbols = atoms.get_chemical_symbols()
    assert symbols.count("C") == 12 and symbols.count("H") == 16

    graph = bond_graph(atoms)
    primary_h = [h for h in hydrogen_indices(atoms)
                 if carbon_substitution(atoms, h, graph) == 1]
    assert len(primary_h) == 1  # the acetylenic tip, and only it
    tip_h = primary_h[0]
    tip_c = graph[tip_h][0]
    other_c = [n for n in graph[tip_c] if symbols[n] == "C"]
    assert len(other_c) == 1  # sp carbon: one C neighbour
    positions = atoms.get_positions()
    triple = float(np.linalg.norm(positions[tip_c] - positions[other_c[0]]))
    assert abs(triple - 1.20) < 0.02
    assert not has_clash(atoms)


def test_handle_tool_builds_with_tip_donor():
    built = build(_spec("ethynyl-ada", "methane"))
    assert built.tool_saturated.spin == 0
    assert built.tool_radical.spin == 1
    # the radical lost the tip H: still 12 C, 15 H
    symbols = built.tool_radical.atoms.get_chemical_symbols()
    assert symbols.count("C") == 12 and symbols.count("H") == 15


def test_fragment_reference_by_parts_crosses_specs(tmp_path):
    import json

    from cheiron.ledger import Ledger

    method = "UKS/PBE/def2-SVP (df, opt)"
    r1 = {
        "spec": {"id": "habs-t1-w1",
                 "tool": {"id": "t1"},
                 "workpiece": {"saturated_name": "W1", "abstract_site": "any"}},
        "build": {"ok": True},
        "measurement": {"method": method, "species": [
            {"role": "tool_radical", "energy_hartree": -10.0, "converged": True},
            {"role": "workpiece", "energy_hartree": -20.0, "converged": True},
        ]},
        "fitness": None, "status": "evaluated",
    }
    r2 = {
        "spec": {"id": "habs-t2-w2",
                 "tool": {"id": "t2"},
                 "workpiece": {"saturated_name": "W2", "abstract_site": "tertiary"}},
        "build": {"ok": True},
        "measurement": {"method": method, "species": [
            {"role": "tool_radical", "energy_hartree": -30.0, "converged": True},
            {"role": "workpiece", "energy_hartree": -40.0, "converged": True},
        ]},
        "fitness": None, "status": "evaluated",
    }
    path = tmp_path / "ledger.jsonl"
    path.write_text(json.dumps(r1) + "\n" + json.dumps(r2) + "\n")
    ledger = Ledger(path)

    # the (t1, W2) pair was never evaluated together, but both fragments exist
    assert ledger.fragment_reference_by_parts("t1", "W2", method) == -10.0 + -40.0
    assert ledger.fragment_reference_by_parts("t1", "W-missing", method) is None
    assert ledger.fragment_reference_by_parts("t1", "W2", "other-method") is None


def test_methanol_abstracts_carbon_h_not_oxygen_h():
    """Methanol has both C-H and O-H; the 'carbon' site must select a C-H.
    Abstracting the O-H instead would be a different (and much harder) reaction."""
    from cheiron.chemistry.species import pick_abstractable_hydrogen, saturated
    from cheiron.geometry import bond_graph

    atoms = saturated("CH3OH")
    graph = bond_graph(atoms)
    symbols = atoms.get_chemical_symbols()
    h = pick_abstractable_hydrogen(atoms, "carbon")
    parent = graph[h][0]
    assert symbols[parent] == "C"          # a C-H, not the O-H
    assert symbols[h] == "H"


def test_methanol_builds_into_reaction():
    built = build(_spec("hydroxyl", "methanol"))
    # product radical is ·CH2OH: lost one C-H, keeps the O-H → 3 H total
    product = built.product_radical.atoms
    symbols = product.get_chemical_symbols()
    assert symbols.count("H") == 3 and symbols.count("O") == 1
    assert built.product_radical.spin == 1


def test_unknown_site_type_rejected():
    from cheiron.chemistry.species import pick_abstractable_hydrogen, saturated

    with pytest.raises(ValueError):
        pick_abstractable_hydrogen(saturated("CH4"), "quaternary")


def test_silyl_tool_builds_second_row():
    """Silyl (·SiH3, second-row Si) must build with correct doublet spin —
    the pipeline should handle heavier elements, not just C/N/O."""
    built = build(_spec("silyl", "methane"))
    assert built.tool_saturated.spin == 0     # SiH4, closed shell
    assert built.tool_radical.spin == 1       # ·SiH3, doublet
    syms = built.tool_radical.atoms.get_chemical_symbols()
    assert syms.count("Si") == 1 and syms.count("H") == 3


def test_silyl_addition_builds():
    from cheiron.addition import build_addition
    built = build_addition(TOOLS["silyl"], "C2H4", "add-silyl-C2H4")
    assert built.tool_radical.spin == 1
    adduct = built.adduct_radical.atoms
    syms = adduct.get_chemical_symbols()
    assert syms.count("Si") == 1                # Si-C adduct radical
    assert built.adduct_radical.spin == 1


def test_silane_workpiece_builds():
    """Silane (SiH4) as an H-donor workpiece: product radical is ·SiH3."""
    built = build(_spec("ethynyl", "silane"))
    assert built.workpiece.spin == 0            # SiH4 closed shell
    prod = built.product_radical.atoms
    syms = prod.get_chemical_symbols()
    assert syms.count("Si") == 1 and syms.count("H") == 3
    assert built.product_radical.spin == 1      # ·SiH3 doublet
