"""M1 — rigid approach-coordinate scan runner.

Runs ``cheiron.approach.rigid_scan`` for one tool/workpiece pair and appends the
result to ``results/scans.jsonl`` (append-only, like the candidate ledger, but a
separate file so the M0 ledger schema stays untouched).

Example:
    python run_scan.py --tool ethynyl --workpiece methane \
        --distances 4.0 3.5 3.0 2.6 2.2 1.9 1.6 1.4 1.2
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from cheiron.approach import relaxed_scan, rigid_scan  # noqa: E402
from cheiron.arbiter import ArbiterConfig  # noqa: E402
from cheiron.chemistry.library import TOOLS, WORKPIECES  # noqa: E402
from cheiron.ledger import Ledger  # noqa: E402
from cheiron.spec import CandidateSpec  # noqa: E402

DEFAULT_DISTANCES = [4.0, 3.5, 3.0, 2.6, 2.2, 1.9, 1.6, 1.4, 1.2]


def main() -> int:
    parser = argparse.ArgumentParser(description="cheiron M1 — rigid approach scan")
    parser.add_argument("--tool", required=True, choices=sorted(TOOLS))
    parser.add_argument("--workpiece", required=True, choices=sorted(WORKPIECES))
    parser.add_argument("--distances", type=float, nargs="+", default=DEFAULT_DISTANCES)
    parser.add_argument("--functional", default="PBE")
    parser.add_argument("--basis", default="def2-SVP")
    parser.add_argument(
        "--relaxed",
        action="store_true",
        help="constrained relaxed scan (H can transfer) instead of rigid",
    )
    parser.add_argument(
        "--out", type=Path, default=Path(__file__).parent / "results" / "scans.jsonl"
    )
    args = parser.parse_args()

    spec = CandidateSpec(
        id=f"habs-{args.tool}-{args.workpiece}",
        tool=TOOLS[args.tool],
        workpiece=WORKPIECES[args.workpiece],
    )
    config = ArbiterConfig(
        functional=args.functional, basis=args.basis, optimize_geometry=False
    )

    mode = "relaxed" if args.relaxed else "rigid"
    print(f"cheiron M1 — {mode} scan  {spec.id}")
    print(f"method: {config.method_string()}")
    print(f"distances (A): {sorted(args.distances, reverse=True)}")

    if args.relaxed:
        # Reuse the M0 ledger's converged fragment energies (opt method) so the
        # scan reference is consistent with the ledger by construction.
        opt_method = ArbiterConfig(
            functional=args.functional, basis=args.basis
        ).method_string()
        ledger = Ledger(Path(__file__).parent / "results" / "ledger.jsonl")
        reference = ledger.fragment_reference(spec.id, opt_method)
        print(f"fragment reference: {'ledger (' + opt_method + ')' if reference is not None else 'recomputing'}")
        scan = relaxed_scan(spec, list(args.distances), config, reference_hartree=reference)
    else:
        scan = rigid_scan(spec, list(args.distances), config)

    record = scan.to_dict()
    record["created_unix"] = int(time.time())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("a") as f:
        f.write(json.dumps(record) + "\n")
    print(f"appended scan record -> {args.out}")

    if not scan.ok:
        print(f"SCAN FAILED: {scan.error}")
        return 1
    for d, e in sorted(scan.relative_kcal(), reverse=True):
        print(f"  d={d:4.2f} A   E-Einf = {e:+8.2f} kcal/mol")
    print(f"{mode} barrier estimate: {scan.barrier_kcal():.2f} kcal/mol  ({scan.wall_seconds:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
