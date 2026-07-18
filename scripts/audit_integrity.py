"""Audit every stored scan geometry against the tool-integrity gate.

Reads ``scans.jsonl``, rebuilds each point's initial supersystem, and checks
that the optimized geometry differs from it only by the intended H transfer.
Exit code 1 if any point fails — usable as a CI-style hard gate.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cheiron.approach import build_supersystem  # noqa: E402
from cheiron.chemistry.library import TOOLS, WORKPIECES  # noqa: E402
from cheiron.integrity import atoms_from_xyz_body, check_step_integrity  # noqa: E402
from cheiron.spec import CandidateSpec  # noqa: E402


def main() -> int:
    scans = ROOT / "experiments/m0_hydrogen_abstraction/results/scans.jsonl"
    failures = 0
    for line in scans.open():
        record = json.loads(line)
        if record["kind"] != "relaxed_approach_scan":
            continue
        _, tool_id, workpiece_id = record["spec_id"].split("-", 2)
        spec = CandidateSpec(
            id=record["spec_id"], tool=TOOLS[tool_id], workpiece=WORKPIECES[workpiece_id]
        )
        mode = "clamped" if "clamped" in record["method"] else "leash"
        for point in record["points"]:
            if not point.get("final_xyz"):
                continue
            system = build_supersystem(spec, point["distance"])
            result = check_step_integrity(
                system.atoms,
                atoms_from_xyz_body(point["final_xyz"]),
                system.target_h,
                system.workpiece_carbon,
                system.tool_center,
            )
            flag = "OK  " if result.ok else "FAIL"
            print(
                f"{flag} {record['spec_id']:32s} d={point['distance']:.1f} "
                f"[{mode}] transferred={result.transferred} "
                f"gained={result.unexpected_gained} lost={result.unexpected_lost}"
            )
            failures += 0 if result.ok else 1
    if failures:
        print(f"\n{failures} point(s) FAILED the integrity gate")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
