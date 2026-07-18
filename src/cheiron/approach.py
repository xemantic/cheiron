"""M1 — mechanical approach coordinate: supersystem geometry and rigid scan.

Favorability (M0) says a step is downhill; feasibility (M1) asks whether it
proceeds when the tool is *pushed* at the workpiece along a positional-control
trajectory. The first observable is the energy profile of the combined
``Tool· ... H-W`` supersystem as a function of the approach distance
d(tool-center ... target-H), with the tool's open valence aimed straight down
the workpiece C-H axis — the idealized geometry a positional assembler would
try to realize.

This module builds those supersystem geometries (pure geometry, cheap, heavily
testable) and computes a rigid scan over them (single-point energies at frozen
fragment geometries — an upper bound on the true barrier, since no relaxation
is allowed). Constrained *relaxed* scans come later; rigid first, so every
later refinement has a number to beat.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np
from ase import Atoms

from .arbiter import HARTREE_TO_KCAL, ArbiterConfig
from .chemistry.species import (
    pick_abstractable_hydrogen,
    remove_hydrogen,
    saturated,
    unpaired_electrons,
)
from .geometry import bond_graph, has_clash
from .spec import CandidateSpec


class ApproachBuildError(Exception):
    """Raised when a supersystem cannot be built for a spec/distance."""


@dataclass
class Supersystem:
    """The combined Tool· + H-W system at one approach distance.

    Atom order is workpiece first, then tool radical; the recorded indices
    refer to the combined system.
    """

    atoms: Atoms
    spin: int
    distance: float          # requested d(tool_center ... target_h), Angstrom
    target_h: int            # workpiece hydrogen under abstraction
    workpiece_carbon: int    # its parent carbon
    tool_center: int         # tool radical-center atom


def _radical_center_after_removal(tool_h: Atoms, donor_index: int) -> tuple[int, np.ndarray]:
    """Index (post-deletion) of the atom that carries the open valence, and the
    unit vector of the former bond from that atom toward the removed hydrogen —
    the direction the open valence points."""
    graph = bond_graph(tool_h)
    neighbours = graph[donor_index]
    if not neighbours:
        raise ApproachBuildError("tool donor hydrogen has no bonded parent atom")
    parent = neighbours[0]
    positions = tool_h.get_positions()
    valence_dir = positions[donor_index] - positions[parent]
    valence_dir /= np.linalg.norm(valence_dir)
    center = parent if parent < donor_index else parent - 1
    return center, valence_dir


def build_supersystem(spec: CandidateSpec, distance: float) -> Supersystem:
    """Place Tool· on the workpiece C-H axis, open valence toward the target H.

    The tool radical is rotated so its open-valence direction is anti-parallel
    to the workpiece C->H direction, then translated so its radical-center atom
    sits ``distance`` Angstrom beyond the target hydrogen. The resulting
    arrangement is collinear C_w - H ... tool_center, the canonical abstraction
    approach.
    """
    if spec.operation != "hydrogen_abstraction":
        raise ApproachBuildError(f"unsupported operation: {spec.operation!r}")
    if distance <= 0:
        raise ApproachBuildError(f"approach distance must be positive, got {distance}")

    workpiece = saturated(spec.workpiece.saturated_name)
    target_h = pick_abstractable_hydrogen(workpiece, spec.workpiece.abstract_site)
    wp_graph = bond_graph(workpiece)
    if not wp_graph[target_h]:
        raise ApproachBuildError("target hydrogen has no bonded parent atom")
    carbon = wp_graph[target_h][0]

    wp_pos = workpiece.get_positions()
    axis = wp_pos[target_h] - wp_pos[carbon]  # C -> H, points out of the workpiece
    axis /= np.linalg.norm(axis)

    tool_h = saturated(spec.tool.saturated_name)
    donor = pick_abstractable_hydrogen(tool_h, spec.tool.donor_site)
    center, valence_dir = _radical_center_after_removal(tool_h, donor)
    tool = remove_hydrogen(tool_h, donor)

    # Aim the open valence at the workpiece (against the outgoing C->H axis),
    # then put the radical center at H + axis * distance.
    tool = tool.copy()
    tool.rotate(valence_dir, -axis, center=tool.get_positions()[center])
    shift = (wp_pos[target_h] + axis * distance) - tool.get_positions()[center]
    tool.translate(shift)

    combined = workpiece + tool
    n_wp = len(workpiece)
    system = Supersystem(
        atoms=combined,
        spin=unpaired_electrons(combined),
        distance=distance,
        target_h=target_h,
        workpiece_carbon=carbon,
        tool_center=n_wp + center,
    )
    realized = combined.get_distance(system.target_h, system.tool_center)
    if abs(realized - distance) > 1e-6:
        raise ApproachBuildError(
            f"placement failed: requested d={distance:.4f}, realized {realized:.4f}"
        )
    return system


@dataclass
class ScanPoint:
    distance: float
    energy_hartree: float | None
    converged: bool
    clash: bool
    wall_seconds: float
    error: str | None = None
    final_xyz: str | None = None  # optimized geometry (relaxed scans), xyz-format body


@dataclass
class ApproachScan:
    """A rigid approach scan plus the separated-fragment reference energy."""

    spec_id: str
    method: str
    kind: str = "rigid_approach_scan"
    points: list[ScanPoint] = field(default_factory=list)
    reference_hartree: float | None = None  # E(Tool·) + E(H-W), same frozen geometries
    reference_source: str | None = None  # 'recomputed' | 'ledger'
    ok: bool = False
    error: str | None = None
    wall_seconds: float = 0.0

    def relative_kcal(self) -> list[tuple[float, float]]:
        """(distance, E - E_separated) in kcal/mol for usable points."""
        if self.reference_hartree is None:
            return []
        return [
            (p.distance, (p.energy_hartree - self.reference_hartree) * HARTREE_TO_KCAL)
            for p in self.points
            if p.energy_hartree is not None
        ]

    def barrier_kcal(self) -> float | None:
        """Highest point of the profile above the separated fragments — the
        rigid-scan estimate of the barrier under approach. None if no usable
        points; 0.0 if the whole profile is downhill."""
        rel = self.relative_kcal()
        if not rel:
            return None
        return max(0.0, max(e for _, e in rel))

    def to_dict(self) -> dict:
        return {
            "spec_id": self.spec_id,
            "method": self.method,
            "kind": self.kind,
            "reference_hartree": self.reference_hartree,
            "reference_source": self.reference_source,
            "barrier_kcal": self.barrier_kcal(),
            "ok": self.ok,
            "error": self.error,
            "wall_seconds": round(self.wall_seconds, 2),
            "points": [
                {
                    "distance": p.distance,
                    "energy_hartree": p.energy_hartree,
                    "converged": p.converged,
                    "clash": p.clash,
                    "wall_seconds": round(p.wall_seconds, 2),
                    "error": p.error,
                    "final_xyz": p.final_xyz,
                }
                for p in self.points
            ],
        }


def _single_point(atoms: Atoms, spin: int, config: ArbiterConfig) -> tuple[float | None, bool, str | None]:
    from pyscf import dft, gto

    try:
        mol = gto.M(
            atom=[
                [sym, tuple(float(x) for x in pos)]
                for sym, pos in zip(atoms.get_chemical_symbols(), atoms.get_positions())
            ],
            basis=config.basis,
            spin=spin,
            charge=0,
            verbose=0,
            max_memory=config.max_memory_mb,
        )
        mf = dft.UKS(mol)
        mf.xc = config.functional
        mf.conv_tol = config.scf_conv_tol
        if config.use_density_fitting:
            mf = mf.density_fit()
        energy = float(mf.kernel())
        return energy, bool(mf.converged), None
    except Exception as exc:
        return None, False, f"{type(exc).__name__}: {exc}"


def constraint_file_text(
    atom_i: int | None = None,
    atom_j: int | None = None,
    frozen_atoms: list[int] | None = None,
) -> str:
    """geomeTRIC ``$freeze`` block pinning the approach coordinate.

    Two modes, combinable: freeze the (i, j) distance (the one-leash scan),
    and/or freeze whole atoms in Cartesian space (``frozen_atoms`` — the
    clamped-bodies scan). One frozen distance alone is a leash, not positional
    control: on a crowded workpiece the tool swings around the target toward
    whatever site the chemistry prefers (measured 2026-07-18); and a frozen
    exactly-linear angle breaks geomeTRIC's internal coordinates, so the
    orientation clamp is Cartesian.

    geomeTRIC constraint files use **1-based** atom indices; the caller passes
    the 0-based indices used everywhere else in cheiron.
    """
    lines = ["$freeze"]
    if atom_i is not None and atom_j is not None:
        lines.append(f"distance {atom_i + 1} {atom_j + 1}")
    for a in frozen_atoms or []:
        lines.append(f"xyz {a + 1}")
    if len(lines) == 1:
        raise ValueError("no constraints requested")
    return "\n".join(lines) + "\n"


def _constrained_optimize(
    atoms: Atoms,
    spin: int,
    frozen_pair: tuple[int, int] | None,
    config: ArbiterConfig,
    frozen_atoms: list[int] | None = None,
) -> tuple[float | None, bool, str | None, str | None]:
    """Optimize with one distance frozen.

    Returns (energy, converged, error, final_xyz) — the optimized geometry is
    kept because a constrained optimizer is free to do chemistry we did not ask
    for (transfer a different hydrogen, reorient into a bridged complex), and
    an energy without its geometry cannot be audited.
    """
    import os
    import tempfile

    from pyscf import dft, gto
    from pyscf.geomopt.geometric_solver import optimize

    try:
        mol = gto.M(
            atom=[
                [sym, tuple(float(x) for x in pos)]
                for sym, pos in zip(atoms.get_chemical_symbols(), atoms.get_positions())
            ],
            basis=config.basis,
            spin=spin,
            charge=0,
            verbose=0,
            max_memory=config.max_memory_mb,
        )

        def make_mf(m):
            mf = dft.UKS(m)
            mf.xc = config.functional
            mf.conv_tol = config.scf_conv_tol
            if config.use_density_fitting:
                mf = mf.density_fit()
            return mf

        fd, cpath = tempfile.mkstemp(suffix=".txt", text=True)
        try:
            with os.fdopen(fd, "w") as f:
                pair = frozen_pair or (None, None)
                f.write(constraint_file_text(pair[0], pair[1], frozen_atoms))
            mol_eq = optimize(
                make_mf(mol),
                constraints=cpath,
                maxsteps=config.max_opt_steps,
                assert_convergence=True,
            )
        finally:
            os.unlink(cpath)

        mf = make_mf(mol_eq)
        energy = float(mf.kernel())
        from pyscf.data.nist import BOHR

        coords = mol_eq.atom_coords() * BOHR  # Bohr -> Angstrom
        xyz = "\n".join(
            f"{mol_eq.atom_symbol(i)} {c[0]:.6f} {c[1]:.6f} {c[2]:.6f}"
            for i, c in enumerate(coords)
        )
        return energy, bool(mf.converged), None, xyz
    except Exception as exc:
        return None, False, f"{type(exc).__name__}: {exc}", None


def relaxed_scan(
    spec: CandidateSpec,
    distances: list[float],
    config: ArbiterConfig,
    reference_hartree: float | None = None,
    clamp_bodies: bool = False,
) -> ApproachScan:
    """Constrained relaxed scan: freeze d(tool_center···target_H), relax the rest.

    Unlike the rigid scan, the target hydrogen is free to transfer, so the
    profile's maximum is a genuine estimate of the barrier under approach
    (within the method and the chosen coordinate). The reference is the sum of
    separately optimized fragment energies at the same method — pass
    ``reference_hartree`` (e.g. from ``Ledger.fragment_reference``) to reuse
    the ledger's converged fragments; independently re-optimized fragments can
    land in different local minima ~1 kcal/mol apart, and recomputing them is
    the most expensive part of a scan.
    """
    start = time.time()
    mode = " [relaxed scan, clamped]" if clamp_bodies else " [relaxed scan]"
    scan = ApproachScan(
        spec_id=spec.id,
        method=config.method_string() + mode,
        kind="relaxed_approach_scan",
    )

    if reference_hartree is not None:
        scan.reference_hartree = reference_hartree
        scan.reference_source = "ledger"
    else:
        # Reference: independently OPTIMIZED fragments (the M0 arbiter's
        # species). The scan config deliberately has optimize_geometry=False
        # (scan points are constrained-optimized separately), so it must be
        # overridden here — evaluating fragments as single points at library
        # geometries silently shifted every recomputed reference several
        # kcal/mol high (the true cause of the +6.96 drift of 2026-07-17).
        from dataclasses import replace as dc_replace

        from .builder import build

        ref_config = dc_replace(config, optimize_geometry=True)

        try:
            built = build(spec)
        except Exception as exc:
            scan.error = f"fragment build failed: {exc}"
            scan.wall_seconds = time.time() - start
            return scan

        from .arbiter import evaluate_species

        refs = {}
        for species in (built.tool_radical, built.workpiece):
            result = evaluate_species(species, ref_config)
            if result.energy_hartree is None or not result.converged:
                scan.error = f"fragment reference failed for {species.role}: {result.error or 'not converged'}"
                scan.wall_seconds = time.time() - start
                return scan
            refs[species.role] = result.energy_hartree
        scan.reference_hartree = refs["tool_radical"] + refs["workpiece"]
        scan.reference_source = "recomputed"

    for d in sorted(distances, reverse=True):  # far -> near
        point_start = time.time()
        try:
            system = build_supersystem(spec, d)
        except ApproachBuildError as exc:
            scan.points.append(
                ScanPoint(d, None, False, False, time.time() - point_start, str(exc))
            )
            continue
        clash = has_clash(system.atoms)
        if clamp_bodies:
            # Positional-control model: anchor each body's position AND
            # orientation by freezing two atoms per body in Cartesian space —
            # the workpiece carbon plus its farthest atom, the tool center
            # plus its farthest atom. The transferring H stays free, so no
            # frozen distance (the approach coordinate is the body separation
            # built into the geometry).
            pos = system.atoms.get_positions()
            n_wp = len(saturated(spec.workpiece.saturated_name))
            wp_indices = [i for i in range(n_wp) if i != system.target_h]
            tool_indices = list(range(n_wp, len(pos)))
            far_wp = max(
                wp_indices, key=lambda i: np.linalg.norm(pos[i] - pos[system.target_h])
            )
            far_tool = max(
                tool_indices, key=lambda i: np.linalg.norm(pos[i] - pos[system.tool_center])
            )
            anchors = sorted(
                {system.workpiece_carbon, far_wp, system.tool_center, far_tool}
            )
            energy, converged, error, xyz = _constrained_optimize(
                system.atoms, system.spin, None, config, frozen_atoms=anchors
            )
        else:
            energy, converged, error, xyz = _constrained_optimize(
                system.atoms,
                system.spin,
                (system.target_h, system.tool_center),
                config,
            )
        scan.points.append(
            ScanPoint(d, energy, converged, clash, time.time() - point_start, error, xyz)
        )

    usable = [p for p in scan.points if p.energy_hartree is not None and p.converged]
    scan.ok = bool(usable)
    if not scan.ok and scan.error is None:
        scan.error = "no scan point produced a converged energy"
    scan.wall_seconds = time.time() - start
    return scan


def rigid_scan(
    spec: CandidateSpec, distances: list[float], config: ArbiterConfig
) -> ApproachScan:
    """Single-point energies of the frozen supersystem at each distance.

    The reference is the sum of single-point fragment energies at the *same*
    frozen geometries and method, so the profile goes to zero at infinite
    separation by construction.
    """
    start = time.time()
    scan = ApproachScan(spec_id=spec.id, method=config.method_string())

    try:
        probe = build_supersystem(spec, max(distances))
    except ApproachBuildError as exc:
        scan.error = str(exc)
        scan.wall_seconds = time.time() - start
        return scan

    # Fragments at their frozen geometries (workpiece atoms first in the build).
    workpiece = saturated(spec.workpiece.saturated_name)
    n_wp = len(workpiece)
    tool_atoms = probe.atoms[n_wp:]
    e_wp, conv_wp, err_wp = _single_point(workpiece, unpaired_electrons(workpiece), config)
    e_tool, conv_tool, err_tool = _single_point(
        tool_atoms, unpaired_electrons(tool_atoms), config
    )
    if e_wp is None or e_tool is None or not (conv_wp and conv_tool):
        scan.error = f"fragment reference failed: {err_wp or err_tool or 'not converged'}"
        scan.wall_seconds = time.time() - start
        return scan
    scan.reference_hartree = e_wp + e_tool

    for d in sorted(distances, reverse=True):  # far -> near, failures cluster near
        point_start = time.time()
        try:
            system = build_supersystem(spec, d)
        except ApproachBuildError as exc:
            scan.points.append(
                ScanPoint(d, None, False, False, time.time() - point_start, str(exc))
            )
            continue
        clash = has_clash(system.atoms)
        energy, converged, error = _single_point(system.atoms, system.spin, config)
        scan.points.append(
            ScanPoint(d, energy, converged, clash, time.time() - point_start, error)
        )

    usable = [p for p in scan.points if p.energy_hartree is not None and p.converged]
    scan.ok = bool(usable)
    if not scan.ok and scan.error is None:
        scan.error = "no scan point produced a converged energy"
    scan.wall_seconds = time.time() - start
    return scan
