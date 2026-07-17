"""BUILD stage: turn a CandidateSpec into concrete geometry for the arbiter.

For a hydrogen-abstraction step the "geometry" is the four species that appear
in ``Tool· + H-W -> Tool-H + ·W``. Each is an ASE ``Atoms`` plus the number of
unpaired electrons the arbiter must treat it with. Nothing energetic happens
here; a build can still fail (unknown molecule, no matching site, steric clash),
which is a legitimate, logged outcome.
"""

from __future__ import annotations

from dataclasses import dataclass

from ase import Atoms

from .chemistry.species import (
    pick_abstractable_hydrogen,
    remove_hydrogen,
    saturated,
    unpaired_electrons,
)
from .geometry import has_clash
from .spec import CandidateSpec


@dataclass
class Species:
    """One molecule the arbiter will evaluate."""

    role: str  # 'tool_saturated' | 'tool_radical' | 'workpiece' | 'product_radical'
    atoms: Atoms
    spin: int  # unpaired electrons (0 singlet, 1 doublet, ...)
    charge: int = 0


@dataclass
class BuiltReaction:
    """The four species of a hydrogen-abstraction step, ready for the arbiter."""

    spec_id: str
    tool_saturated: Species
    tool_radical: Species
    workpiece: Species
    product_radical: Species

    def species(self) -> list[Species]:
        return [
            self.tool_saturated,
            self.tool_radical,
            self.workpiece,
            self.product_radical,
        ]


class BuildError(Exception):
    """Raised when a spec cannot be turned into valid geometry."""


def build(spec: CandidateSpec) -> BuiltReaction:
    """Construct the four-species reaction system for a hydrogen abstraction."""
    if spec.operation != "hydrogen_abstraction":
        raise BuildError(f"unsupported operation: {spec.operation!r}")

    # Tool: saturated form (Tool-H) and its radical (Tool·, minus donor H).
    try:
        tool_h = saturated(spec.tool.saturated_name)
    except Exception as exc:  # ASE raises varied errors for unknown names
        raise BuildError(f"unknown tool molecule {spec.tool.saturated_name!r}: {exc}")
    tool_donor_h = pick_abstractable_hydrogen(tool_h, spec.tool.donor_site)
    tool_radical = remove_hydrogen(tool_h, tool_donor_h)

    # Workpiece: saturated form (H-W) and product radical (·W, minus target H).
    try:
        workpiece = saturated(spec.workpiece.saturated_name)
    except Exception as exc:
        raise BuildError(
            f"unknown workpiece molecule {spec.workpiece.saturated_name!r}: {exc}"
        )
    target_h = pick_abstractable_hydrogen(workpiece, spec.workpiece.abstract_site)
    product_radical = remove_hydrogen(workpiece, target_h)

    for label, atoms in (
        ("tool_saturated", tool_h),
        ("tool_radical", tool_radical),
        ("workpiece", workpiece),
        ("product_radical", product_radical),
    ):
        if has_clash(atoms):
            raise BuildError(f"steric clash in {label} geometry")

    return BuiltReaction(
        spec_id=spec.id,
        tool_saturated=Species("tool_saturated", tool_h, unpaired_electrons(tool_h)),
        tool_radical=Species("tool_radical", tool_radical, unpaired_electrons(tool_radical)),
        workpiece=Species("workpiece", workpiece, unpaired_electrons(workpiece)),
        product_radical=Species(
            "product_radical", product_radical, unpaired_electrons(product_radical)
        ),
    )
