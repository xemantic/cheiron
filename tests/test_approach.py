"""Fast tests for the M1 approach-coordinate supersystem builder (no PySCF)."""

from __future__ import annotations

import numpy as np
import pytest

from cheiron.approach import ApproachBuildError, ApproachScan, ScanPoint, build_supersystem
from cheiron.chemistry.library import TOOLS, WORKPIECES
from cheiron.geometry import has_clash
from cheiron.spec import CandidateSpec


def _spec(tool_id: str, workpiece_id: str) -> CandidateSpec:
    return CandidateSpec(
        id=f"habs-{tool_id}-{workpiece_id}",
        tool=TOOLS[tool_id],
        workpiece=WORKPIECES[workpiece_id],
    )


def test_supersystem_atom_count_and_spin():
    system = build_supersystem(_spec("ethynyl", "methane"), 3.0)
    # CH4 (5) + C2H (3) = 8 atoms; closed shell + radical = doublet.
    assert len(system.atoms) == 8
    assert system.spin == 1


def test_requested_distance_is_realized():
    for d in (2.0, 3.0, 4.5):
        system = build_supersystem(_spec("methyl", "ethane"), d)
        realized = system.atoms.get_distance(system.target_h, system.tool_center)
        assert realized == pytest.approx(d, abs=1e-6)


def test_approach_is_collinear():
    """The canonical abstraction approach: C_w - H ... tool_center on one line."""
    system = build_supersystem(_spec("ethynyl", "isobutane"), 2.5)
    pos = system.atoms.get_positions()
    u = pos[system.target_h] - pos[system.workpiece_carbon]
    v = pos[system.tool_center] - pos[system.target_h]
    cos = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
    assert cos == pytest.approx(1.0, abs=1e-6)


def test_tool_points_open_valence_at_target():
    """The ethynyl radical is linear H-C≡C· — placed at the workpiece, its own
    hydrogen must be the atom *farthest* from the target H, not closest."""
    system = build_supersystem(_spec("ethynyl", "methane"), 3.0)
    pos = system.atoms.get_positions()
    symbols = system.atoms.get_chemical_symbols()
    tool_indices = [i for i in range(5, 8)]
    tool_h = [i for i in tool_indices if symbols[i] == "H"]
    assert len(tool_h) == 1
    dists = {i: np.linalg.norm(pos[i] - pos[system.target_h]) for i in tool_indices}
    assert max(dists, key=dists.get) == tool_h[0]
    assert min(dists, key=dists.get) == system.tool_center


def test_no_clash_at_moderate_distance_but_clash_when_rammed():
    spec = _spec("ethynyl", "methane")
    assert not has_clash(build_supersystem(spec, 3.0).atoms)
    assert has_clash(build_supersystem(spec, 0.3).atoms)


def test_invalid_distance_rejected():
    with pytest.raises(ApproachBuildError):
        build_supersystem(_spec("ethynyl", "methane"), 0.0)
    with pytest.raises(ApproachBuildError):
        build_supersystem(_spec("ethynyl", "methane"), -1.0)


def test_barrier_extraction_from_profile():
    scan = ApproachScan(spec_id="x", method="m", reference_hartree=0.0)
    kcal = 1.0 / 627.509474
    for d, e in ((4.0, 0.5), (3.0, 2.0), (2.0, -3.0)):
        scan.points.append(ScanPoint(d, e * kcal, True, False, 0.0))
    assert scan.barrier_kcal() == pytest.approx(2.0, rel=1e-6)


def test_barrier_is_zero_for_all_downhill_profile():
    scan = ApproachScan(spec_id="x", method="m", reference_hartree=0.0)
    kcal = 1.0 / 627.509474
    for d, e in ((4.0, -0.5), (3.0, -2.0)):
        scan.points.append(ScanPoint(d, e * kcal, True, False, 0.0))
    assert scan.barrier_kcal() == 0.0


def test_barrier_none_without_usable_points():
    scan = ApproachScan(spec_id="x", method="m")
    assert scan.barrier_kcal() is None
