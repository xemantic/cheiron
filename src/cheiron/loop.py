"""The outer controller: run candidates through the full loop, log everything.

  PROPOSE -> BUILD -> ARBITER -> SCORE -> (ledger) -> SELECT

This module wires the stages together and keeps the run resumable: a candidate
already present in the ledger is skipped unless ``force`` is set, so a killed
run restarts without repeating expensive arbiter work. The human VETO gate is
applied out-of-band (see docs/design/01-loop-architecture.md); nothing here can
stamp a candidate ``accepted`` on its own.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass

from .arbiter import ArbiterConfig, evaluate_reaction
from .builder import BuildError, build
from .ledger import Ledger, LedgerRecord
from .score import score
from .spec import CandidateSpec


@dataclass
class LoopResult:
    evaluated: int
    skipped: int
    build_failures: int
    arbiter_failures: int
    favorable: int


def run_batch(
    candidates: Iterable[CandidateSpec],
    ledger: Ledger,
    config: ArbiterConfig,
    force: bool = False,
    log=print,
) -> LoopResult:
    """Evaluate a batch of candidates end-to-end, appending one record each."""
    already = set() if force else set(ledger.latest_by_spec())
    result = LoopResult(0, 0, 0, 0, 0)

    for spec in candidates:
        if spec.id in already:
            result.skipped += 1
            log(f"[skip] {spec.id} (already in ledger)")
            continue

        log(f"[eval] {spec.id}  tool={spec.tool.id}  workpiece={spec.workpiece.id}")

        # BUILD
        try:
            built = build(spec)
        except BuildError as exc:
            result.build_failures += 1
            log(f"       build failed: {exc}")
            ledger.append(
                LedgerRecord(
                    spec=spec.to_dict(),
                    build={"ok": False, "error": str(exc)},
                    measurement=None,
                    fitness=None,
                    status="retired",
                )
            )
            continue

        # ARBITER
        measurement = evaluate_reaction(built, config)
        # SCORE
        fitness = score(measurement)
        result.evaluated += 1
        if not measurement.ok:
            result.arbiter_failures += 1
        if fitness.favorable:
            result.favorable += 1

        delta = measurement.reaction_energy_kcal
        delta_str = f"{delta:+.1f} kcal/mol" if delta is not None else "n/a"
        verdict = "FAVORABLE" if fitness.favorable else (
            "unfavorable" if fitness.favorable is False else "unusable"
        )
        log(
            f"       dE = {delta_str}  -> {verdict}  "
            f"({measurement.wall_seconds:.0f}s, {measurement.method})"
        )

        ledger.append(
            LedgerRecord(
                spec=spec.to_dict(),
                build={"ok": True, "error": None},
                measurement=measurement.to_dict(),
                fitness=fitness.to_dict(),
                status="evaluated",
            )
        )

    return result


def select(ledger: Ledger, keep: int = 8) -> list[dict]:
    """Rank usable candidates by fitness and return the survivors (highest first).

    Pure read over the ledger; the returned survivors are what an evolutionary
    proposer would use as parents. Retirement is recorded in the ledger by the
    caller when it chooses to persist a selection round.
    """
    latest = ledger.latest_by_spec().values()
    usable = [
        rec
        for rec in latest
        if rec.get("fitness") and rec["fitness"].get("valid") and rec["fitness"].get("fitness") is not None
    ]
    usable.sort(key=lambda r: r["fitness"]["fitness"], reverse=True)
    return usable[:keep]
