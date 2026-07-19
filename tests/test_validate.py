"""Tests for automated physics-consistency checks (no PySCF)."""

from __future__ import annotations

from cheiron.validate import check_reversibility


def _rec(spec_id, tool_sat, wp_sat, de):
    return {
        "spec": {"id": spec_id,
                 "tool": {"saturated_name": tool_sat},
                 "workpiece": {"saturated_name": wp_sat}},
        "fitness": {"valid": True, "reaction_energy_kcal": de},
    }


def test_reversibility_detects_swapped_pair():
    latest = {
        "f": _rec("habs-silyl-methane", "SiH4", "CH4", +19.7),
        "r": _rec("habs-methyl-silane", "CH4", "SiH4", -19.7),
        "x": _rec("habs-ethynyl-ethane", "C2H2", "C2H6", -31.7),  # no reverse present
    }
    findings = check_reversibility(latest)
    assert len(findings) == 1              # the one swapped pair, once
    f = findings[0]
    assert abs(f.residual_kcal) < 1e-9     # +19.7 + -19.7 == 0
    assert f.ok()


def test_reversibility_flags_a_broken_pair():
    latest = {
        "f": _rec("habs-a-b", "A", "B", +10.0),
        "r": _rec("habs-b-a", "B", "A", -6.0),   # should be -10; pipeline bug
    }
    findings = check_reversibility(latest)
    assert len(findings) == 1
    assert not findings[0].ok()            # residual +4.0 > tol
    assert abs(findings[0].residual_kcal - 4.0) < 1e-9


def test_self_reverse_identity_must_be_zero():
    latest = {"m": _rec("habs-methyl-methane", "CH4", "CH4", 0.0)}
    findings = check_reversibility(latest)
    assert len(findings) == 1              # A-from-A pairs with itself
    assert findings[0].ok()               # residual is its own ΔE == 0
