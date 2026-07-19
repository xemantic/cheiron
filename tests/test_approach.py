"""Fast tests for the M1 approach-coordinate supersystem builder (no PySCF)."""

from __future__ import annotations

import numpy as np
import pytest

from cheiron.approach import (
    ApproachBuildError,
    ApproachScan,
    ScanPoint,
    build_supersystem,
    constraint_file_text,
)
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


def test_constraint_file_uses_one_based_indices():
    """geomeTRIC constraint files are 1-based; cheiron indices are 0-based.
    Off-by-one here would silently freeze the wrong atom pair."""
    text = constraint_file_text(3, 6)
    assert text.splitlines() == ["$freeze", "distance 4 7"]


def test_constraint_file_with_frozen_atoms():
    text = constraint_file_text(frozen_atoms=[0, 4, 5, 7])
    assert text.splitlines() == ["$freeze", "xyz 1", "xyz 5", "xyz 6", "xyz 8"]


def test_constraint_file_requires_some_constraint():
    with pytest.raises(ValueError):
        constraint_file_text()


def _shift_h_to_tool(system):
    """Fake a completed transfer: move the target H next to the tool center."""
    atoms = system.atoms.copy()
    pos = atoms.get_positions()
    ct, th = system.tool_center, system.target_h
    direction = pos[th] - pos[ct]
    direction /= np.linalg.norm(direction)
    pos[th] = pos[ct] + direction * 1.09
    atoms.set_positions(pos)
    return atoms


def test_integrity_accepts_clean_transfer():
    from cheiron.integrity import check_step_integrity

    system = build_supersystem(_spec("methyl", "methane"), 2.8)
    final = _shift_h_to_tool(system)
    result = check_step_integrity(
        system.atoms, final, system.target_h, system.workpiece_carbon, system.tool_center
    )
    assert result.ok and result.transferred


def test_integrity_accepts_no_reaction():
    from cheiron.integrity import check_step_integrity

    system = build_supersystem(_spec("methyl", "methane"), 2.8)
    result = check_step_integrity(
        system.atoms, system.atoms.copy(),
        system.target_h, system.workpiece_carbon, system.tool_center,
    )
    assert result.ok and not result.transferred


def test_integrity_rejects_tool_fragmentation():
    from cheiron.integrity import check_step_integrity

    system = build_supersystem(_spec("methyl", "methane"), 2.8)
    broken = system.atoms.copy()
    pos = broken.get_positions()
    # rip a hydrogen off the tool (an atom that is neither target H nor anchor)
    tool_h = system.tool_center + 1
    pos[tool_h] += np.array([0.0, 0.0, 5.0])
    broken.set_positions(pos)
    result = check_step_integrity(
        system.atoms, broken, system.target_h, system.workpiece_carbon, system.tool_center
    )
    assert not result.ok and result.unexpected_lost


def test_integrity_roundtrip_through_xyz_body():
    from cheiron.integrity import atoms_from_xyz_body, check_step_integrity

    system = build_supersystem(_spec("ethynyl", "methane"), 3.0)
    body = "\n".join(
        f"{s} {p[0]:.6f} {p[1]:.6f} {p[2]:.6f}"
        for s, p in zip(system.atoms.get_chemical_symbols(), system.atoms.get_positions())
    )
    rebuilt = atoms_from_xyz_body(body)
    result = check_step_integrity(
        system.atoms, rebuilt, system.target_h, system.workpiece_carbon, system.tool_center
    )
    assert result.ok


def test_barrier_excludes_post_transfer_compression():
    """After the H transfers (deep product-like well), forcing the approach
    distance shorter compresses the formed bond into a wall that is NOT a
    reaction barrier. The barrier must be the peak on the approach side only."""
    scan = ApproachScan(spec_id="x", method="m", reference_hartree=0.0)
    kcal = 1.0 / 627.509474
    # far -> near: mild pre-barrier, then product well, then compression wall
    for d, e in ((2.4, -0.5), (2.0, 1.3), (1.6, -5.8), (1.3, 11.0), (1.1, 28.0)):
        scan.points.append(ScanPoint(d, e * kcal, True, False, 0.0))
    # min-energy point is 1.6; only d>=1.6 count -> peak is +1.3, not +28
    assert scan.barrier_kcal() == pytest.approx(1.3, rel=1e-6)


def test_barrier_well_resolved_flags_coarse_grid():
    """The methyl+methanol miss: a coarse grid steps over the saddle. A peak
    with a >0.3 A gap to a neighbour is not trustworthy."""
    kcal = 1.0 / 627.509474
    # coarse: peak +1.26 at 2.0, but 2.0->1.6 is a 0.4 A gap hiding the real saddle
    coarse = ApproachScan(spec_id="x", method="m", reference_hartree=0.0)
    for d, e in ((2.4, -0.5), (2.0, 1.26), (1.6, -5.76)):
        coarse.points.append(ScanPoint(d, e * kcal, True, False, 0.0))
    assert coarse.barrier_well_resolved() is False

    # fine: peak +3.16 at 1.8 with 0.2 A neighbours on both sides
    fine = ApproachScan(spec_id="x", method="m", reference_hartree=0.0)
    for d, e in ((2.4, -0.5), (2.2, 0.12), (2.0, 1.26), (1.8, 3.16), (1.6, -5.76)):
        fine.points.append(ScanPoint(d, e * kcal, True, False, 0.0))
    assert fine.barrier_well_resolved() is True


def test_barrier_well_resolved_none_when_downhill():
    scan = ApproachScan(spec_id="x", method="m", reference_hartree=0.0)
    kcal = 1.0 / 627.509474
    for d, e in ((2.4, -0.5), (2.0, -2.0), (1.6, -8.0)):
        scan.points.append(ScanPoint(d, e * kcal, True, False, 0.0))
    assert scan.barrier_kcal() == 0.0
    assert scan.barrier_well_resolved() is None


def test_barrier_well_resolved_false_when_peak_at_endpoint():
    """Monotonically rising (no product well sampled): peak is the nearest
    point, so the saddle is not bracketed."""
    scan = ApproachScan(spec_id="x", method="m", reference_hartree=0.0)
    kcal = 1.0 / 627.509474
    for d, e in ((2.4, 0.5), (2.2, 2.0), (2.0, 4.0)):
        scan.points.append(ScanPoint(d, e * kcal, True, False, 0.0))
    assert scan.barrier_well_resolved() is False
