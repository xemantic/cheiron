"""Fast regression tests for the non-QM parts of the loop (no PySCF needed)."""

from __future__ import annotations

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
