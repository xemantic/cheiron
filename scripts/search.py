"""Autonomous proposer: print the next candidate the loop would evaluate.

Fits the additive model to the abstraction ledger and applies the
explore-then-exploit strategy (`cheiron.search.propose_next`) to choose the
single most informative unmeasured candidate. Prints the proposal and the exact
`run.py` command to evaluate it — the SELECT→PROPOSE closure of M3, one step.
With --evaluate, runs that command itself.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cheiron.chemistry.library import TOOLS, WORKPIECES  # noqa: E402
from cheiron.ledger import Ledger  # noqa: E402
from cheiron.search import propose_next  # noqa: E402

LEDGER = ROOT / "experiments/m0_hydrogen_abstraction/results/ledger.jsonl"
RUN = ROOT / "experiments/m0_hydrogen_abstraction/run.py"


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    evaluate = "--evaluate" in argv

    proposal = propose_next(
        Ledger(LEDGER).latest_by_spec(), list(TOOLS), list(WORKPIECES)
    )
    if proposal is None:
        print("grid fully measured — no informative candidate to propose")
        return 0

    pred = "unpredictable (anchor)" if proposal.predicted_kcal is None \
        else f"{proposal.predicted_kcal:+.1f} kcal/mol"
    print(f"next candidate: {proposal.spec_id}")
    print(f"  prediction:  {pred}")
    print(f"  rationale:   {proposal.rationale}")
    cmd = [sys.executable, str(RUN),
           "--tools", proposal.tool_id, "--workpieces", proposal.workpiece_id]
    print(f"  evaluate:    {' '.join(cmd[1:])}")

    if evaluate:
        print("\n--evaluate: running the arbiter ...")
        return subprocess.call(cmd)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
