"""ARBITER stage: the physics engine that referees candidates.

Current engine is PySCF — unrestricted Kohn-Sham (UKS) so open-shell radicals
are treated correctly — with ``geometric`` driving geometry optimization. The
arbiter is deliberately the only slow stage; it returns measurements tagged with
the exact method that produced them, because a number without its method is not
a claim we can defend (see docs/design/02-arbiter.md).

For a hydrogen-abstraction step it optimizes the four species and reports the
reaction energy  ΔE = [E(Tool-H) + E(·W)] - [E(Tool·) + E(H-W)].
Negative ΔE means the abstraction is thermodynamically favorable.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .builder import BuiltReaction, Species

HARTREE_TO_KCAL = 627.509474  # kcal/mol per Hartree


@dataclass(frozen=True)
class ArbiterConfig:
    """How the arbiter should evaluate — captured in the ledger for reproducibility."""

    tier: int = 2
    functional: str = "PBE"
    basis: str = "def2-SVP"
    use_density_fitting: bool = True
    optimize_geometry: bool = True
    max_opt_steps: int = 50
    scf_conv_tol: float = 1e-8

    def method_string(self) -> str:
        tag = "df" if self.use_density_fitting else "no-df"
        opt = "opt" if self.optimize_geometry else "single-point"
        return f"UKS/{self.functional}/{self.basis} ({tag}, {opt})"


@dataclass
class SpeciesResult:
    role: str
    energy_hartree: float | None
    converged: bool
    spin: int
    charge: int
    wall_seconds: float
    error: str | None = None


@dataclass
class ReactionMeasurement:
    spec_id: str
    method: str
    tier: int
    species: list[SpeciesResult] = field(default_factory=list)
    reaction_energy_hartree: float | None = None
    reaction_energy_kcal: float | None = None
    ok: bool = False
    error: str | None = None
    wall_seconds: float = 0.0

    def to_dict(self) -> dict:
        return {
            "spec_id": self.spec_id,
            "method": self.method,
            "tier": self.tier,
            "reaction_energy_hartree": self.reaction_energy_hartree,
            "reaction_energy_kcal": self.reaction_energy_kcal,
            "ok": self.ok,
            "error": self.error,
            "wall_seconds": round(self.wall_seconds, 2),
            "species": [
                {
                    "role": s.role,
                    "energy_hartree": s.energy_hartree,
                    "converged": s.converged,
                    "spin": s.spin,
                    "charge": s.charge,
                    "wall_seconds": round(s.wall_seconds, 2),
                    "error": s.error,
                }
                for s in self.species
            ],
        }


def _to_pyscf_atom(species: Species):
    symbols = species.atoms.get_chemical_symbols()
    positions = species.atoms.get_positions()
    return [[sym, tuple(float(x) for x in pos)] for sym, pos in zip(symbols, positions)]


def evaluate_species(species: Species, config: ArbiterConfig) -> SpeciesResult:
    """Optimize (optionally) and compute the electronic energy of one species."""
    from pyscf import dft, gto

    start = time.time()
    try:
        mol = gto.M(
            atom=_to_pyscf_atom(species),
            basis=config.basis,
            spin=species.spin,       # n_alpha - n_beta = unpaired electrons
            charge=species.charge,
            verbose=0,
        )

        def make_mf(m):
            mf = dft.UKS(m)
            mf.xc = config.functional
            mf.conv_tol = config.scf_conv_tol
            if config.use_density_fitting:
                mf = mf.density_fit()
            return mf

        mf = make_mf(mol)

        if config.optimize_geometry and len(species.atoms) > 1:
            from pyscf.geomopt.geometric_solver import optimize

            # assert_convergence: a stalled geometry optimization must be an
            # error, not a silently wrong energy — a +7 kcal/mol reference
            # drift from exactly this slipped into the first relaxed scans.
            mol_eq = optimize(
                mf, maxsteps=config.max_opt_steps, assert_convergence=True
            )
            mf = make_mf(mol_eq)

        energy = float(mf.kernel())
        return SpeciesResult(
            role=species.role,
            energy_hartree=energy,
            converged=bool(mf.converged),
            spin=species.spin,
            charge=species.charge,
            wall_seconds=time.time() - start,
        )
    except Exception as exc:  # arbiter failures are data, not crashes
        return SpeciesResult(
            role=species.role,
            energy_hartree=None,
            converged=False,
            spin=species.spin,
            charge=species.charge,
            wall_seconds=time.time() - start,
            error=f"{type(exc).__name__}: {exc}",
        )


def evaluate_reaction(built: BuiltReaction, config: ArbiterConfig) -> ReactionMeasurement:
    """Evaluate all four species and combine them into a reaction energy."""
    start = time.time()
    measurement = ReactionMeasurement(
        spec_id=built.spec_id, method=config.method_string(), tier=config.tier
    )
    energies: dict[str, float | None] = {}
    for species in built.species():
        result = evaluate_species(species, config)
        measurement.species.append(result)
        energies[result.role] = result.energy_hartree

    measurement.wall_seconds = time.time() - start

    missing = [role for role, e in energies.items() if e is None]
    if missing:
        measurement.ok = False
        measurement.error = "missing energies for: " + ", ".join(missing)
        return measurement

    # ΔE = [E(Tool-H) + E(·W)] - [E(Tool·) + E(H-W)]
    delta = (
        energies["tool_saturated"]
        + energies["product_radical"]
        - energies["tool_radical"]
        - energies["workpiece"]
    )
    measurement.reaction_energy_hartree = delta
    measurement.reaction_energy_kcal = delta * HARTREE_TO_KCAL
    measurement.ok = all(s.converged for s in measurement.species)
    if not measurement.ok:
        measurement.error = "one or more SCF/optimizations did not converge"
    return measurement
