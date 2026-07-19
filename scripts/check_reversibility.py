"""Run the ledger's built-in physics-consistency checks; nonzero exit on failure.

Verifies that reverse-reaction candidate pairs have ΔE summing to ~0 (and that
self-reverse pairs are ~0) — a free, rigorous check that the arbiter's
independent per-candidate calculations respect microscopic reversibility. CI-
usable: exits 1 if any pair breaks tolerance.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cheiron.ledger import Ledger  # noqa: E402
from cheiron.validate import check_reversibility  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    ledger_path = Path(argv[0]) if argv else \
        ROOT / "experiments/m0_hydrogen_abstraction/results/ledger.jsonl"
    findings = check_reversibility(Ledger(ledger_path).latest_by_spec())
    if not findings:
        print("no reverse-reaction pairs in the ledger yet")
        return 0
    bad = 0
    for f in findings:
        flag = "OK  " if f.ok() else "FAIL"
        rel = "self-reverse (must be ~0)" if f.forward_id == f.reverse_id else "sum must be ~0"
        print(f"{flag} {f.forward_id} ({f.forward_kcal:+.1f}) + "
              f"{f.reverse_id} ({f.reverse_kcal:+.1f}) = "
              f"{f.residual_kcal:+.2f} kcal/mol   [{rel}]")
        bad += 0 if f.ok() else 1
    if bad:
        print(f"\n{bad} reversibility check(s) FAILED")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
