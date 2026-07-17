"""M0 experiment driver — hydrogen abstraction by the ethynyl tool.

Runs the cheiron loop over the tool x workpiece grid and writes an append-only
ledger next to this file. See docs/design/03-milestones.md for what M0 is
trying to establish (reproduce a known-favorable mechanosynthesis step).

Examples
--------
Fast pipeline smoke test on methane only::

    python experiments/m0_hydrogen_abstraction/run.py --workpieces methane --fast

The M0 result run (ethynyl on the isobutane tertiary C-H)::

    python experiments/m0_hydrogen_abstraction/run.py --workpieces isobutane
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Make the src/ package importable when run as a plain script.
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from cheiron.arbiter import ArbiterConfig  # noqa: E402
from cheiron.ledger import Ledger  # noqa: E402
from cheiron.loop import run_batch, select  # noqa: E402
from cheiron.proposer import enumerate_candidates  # noqa: E402

RESULTS = Path(__file__).resolve().parent / "results"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="cheiron M0 — hydrogen abstraction")
    parser.add_argument("--workpieces", nargs="*", default=None,
                        help="library ids to run (default: all)")
    parser.add_argument("--tools", nargs="*", default=None,
                        help="tool ids to run (default: all)")
    parser.add_argument("--functional", default="PBE")
    parser.add_argument("--basis", default="def2-SVP")
    parser.add_argument("--no-opt", action="store_true",
                        help="skip geometry optimization (single-point energies)")
    parser.add_argument("--no-df", action="store_true",
                        help="disable density fitting")
    parser.add_argument("--fast", action="store_true",
                        help="small-basis screening preset (STO-3G-ish, fast, rough)")
    parser.add_argument("--force", action="store_true",
                        help="re-evaluate candidates already in the ledger")
    parser.add_argument("--ledger", default=str(RESULTS / "ledger.jsonl"))
    args = parser.parse_args(argv)

    if args.fast:
        args.basis = "6-31G"

    config = ArbiterConfig(
        tier=1 if args.fast else 2,
        functional=args.functional,
        basis=args.basis,
        use_density_fitting=not args.no_df,
        optimize_geometry=not args.no_opt,
    )

    ledger = Ledger(args.ledger)
    candidates = list(enumerate_candidates(tools=args.tools, workpieces=args.workpieces))

    print(f"cheiron M0 — {len(candidates)} candidate(s)")
    print(f"arbiter: {config.method_string()} (tier {config.tier})")
    print(f"ledger:  {args.ledger}\n")

    result = run_batch(candidates, ledger, config, force=args.force)

    print("\n--- batch summary ---")
    print(f"evaluated={result.evaluated}  skipped={result.skipped}  "
          f"build_failures={result.build_failures}  "
          f"arbiter_failures={result.arbiter_failures}  favorable={result.favorable}")

    survivors = select(ledger, keep=8)
    if survivors:
        print("\n--- leaderboard (most favorable first) ---")
        for rec in survivors:
            fit = rec["fitness"]
            print(f"  {rec['spec']['id']:28s}  "
                  f"dE = {fit['reaction_energy_kcal']:+7.1f} kcal/mol  "
                  f"favorable={fit['favorable']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
