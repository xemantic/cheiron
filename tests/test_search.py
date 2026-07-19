"""Tests for the M3 autonomous candidate proposer (no PySCF)."""

from __future__ import annotations

from cheiron.search import propose_next


def _rec(tool, wp, de):
    return {
        "spec": {"id": f"habs-{tool}-{wp}",
                 "tool": {"id": tool, "saturated_name": tool},
                 "workpiece": {"id": wp, "saturated_name": wp, "abstract_site": "any"}},
        "fitness": {"valid": True, "reaction_energy_kcal": de},
    }


def test_proposes_anchor_for_unmeasured_tool():
    latest = {"a": _rec("methyl", "methane", 0.0)}
    p = propose_next(latest, ["methyl", "ethynyl"], ["methane", "ethane"])
    # ethynyl is unmeasured -> anchor it against the measured workpiece
    assert p.tool_id == "ethynyl" and p.predicted_kcal is None
    assert "anchor" in p.rationale


def test_proposes_anchor_for_unmeasured_workpiece():
    latest = {"a": _rec("methyl", "methane", 0.0), "b": _rec("ethynyl", "methane", -26.0)}
    p = propose_next(latest, ["methyl", "ethynyl"], ["methane", "ethane"])
    # both tools measured, but ethane workpiece is not -> anchor it
    assert p.workpiece_id == "ethane" and p.predicted_kcal is None


def test_exploits_most_favourable_when_all_anchored():
    # 2x2 fully cross-measured except one cell; model predicts it
    latest = {
        "a": _rec("methyl", "methane", 0.0),
        "b": _rec("methyl", "ethane", -5.0),
        "c": _rec("ethynyl", "methane", -26.0),
    }
    p = propose_next(latest, ["methyl", "ethynyl"], ["methane", "ethane"])
    # only unmeasured cell is ethynyl-ethane; model predicts it (all factors anchored)
    assert p.spec_id == "habs-ethynyl-ethane"
    assert p.predicted_kcal is not None
    assert "verify" in p.rationale


def test_returns_none_when_grid_complete():
    latest = {
        "a": _rec("methyl", "methane", 0.0),
        "b": _rec("methyl", "ethane", -5.0),
        "c": _rec("ethynyl", "methane", -26.0),
        "d": _rec("ethynyl", "ethane", -31.0),
    }
    assert propose_next(latest, ["methyl", "ethynyl"], ["methane", "ethane"]) is None
