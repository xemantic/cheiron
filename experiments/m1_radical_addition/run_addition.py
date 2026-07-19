"""M4 — radical-addition evaluator (first slice of a second operation type).

Computes ΔE = E(adduct·) − E(Tool·) − E(alkene) for ``Tool· + alkene ->
Tool-CH2-CH2·`` by optimizing each of the three species with the *existing*
arbiter (``evaluate_species``) and combining them here — so the shared
abstraction arbiter is untouched. Appends to an append-only JSONL ledger,
mirroring the M0 discipline (every energy travels with its method; failures
recorded, not hidden).

Example:
    python run_addition.py --tool ethynyl --substrate C2H4
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from cheiron.addition import AdditionBuildError, build_addition  # noqa: E402
from cheiron.arbiter import HARTREE_TO_KCAL, ArbiterConfig, evaluate_species  # noqa: E402
from cheiron.chemistry.library import TOOLS  # noqa: E402

RESULTS = Path(__file__).parent / "results"


def main() -> int:
    parser = argparse.ArgumentParser(description="cheiron M4 — radical addition")
    parser.add_argument("--tool", required=True, choices=sorted(TOOLS))
    parser.add_argument("--substrate", default="C2H4", help="alkene (ASE G2 name)")
    parser.add_argument("--attack", default="anti-markovnikov",
                        choices=["anti-markovnikov", "markovnikov"],
                        help="regiochemistry: which alkene carbon the tool attacks")
    parser.add_argument("--functional", default="PBE")
    parser.add_argument("--basis", default="def2-SVP")
    parser.add_argument("--max-memory", type=int, default=2000)
    parser.add_argument("--ledger", type=Path, default=RESULTS / "ledger.jsonl")
    parser.add_argument("--barrier", action="store_true",
                        help="run an approach-barrier scan instead of the reaction energy")
    parser.add_argument("--distances", type=float, nargs="+",
                        default=[2.7, 2.5, 2.3, 2.1, 1.9])
    args = parser.parse_args()

    regio = "" if args.attack == "anti-markovnikov" else "-mark"
    spec_id = f"add-{args.tool}-{args.substrate}{regio}"
    config = ArbiterConfig(
        functional=args.functional, basis=args.basis, max_memory_mb=args.max_memory
    )
    print(f"cheiron M4 — radical addition  {spec_id}")
    print(f"method: {config.method_string()}")

    if args.barrier:
        return _run_barrier(args, config, spec_id)

    record: dict = {
        "spec_id": spec_id,
        "operation": "radical_addition",
        "tool": args.tool,
        "substrate": args.substrate,
        "attack": args.attack,
        "method": config.method_string(),
        "created_unix": int(time.time()),
    }
    try:
        built = build_addition(TOOLS[args.tool], args.substrate, spec_id, args.attack)
    except AdditionBuildError as exc:
        record.update(ok=False, error=f"build failed: {exc}")
        _append(args.ledger, record)
        print(f"BUILD FAILED: {exc}")
        return 1

    start = time.time()
    energies: dict[str, float | None] = {}
    species_records = []
    for species in built.species():
        result = evaluate_species(species, config)
        energies[species.role] = result.energy_hartree
        species_records.append({
            "role": result.role, "energy_hartree": result.energy_hartree,
            "converged": result.converged, "spin": result.spin,
            "wall_seconds": round(result.wall_seconds, 2), "error": result.error,
        })
    record["species"] = species_records
    record["wall_seconds"] = round(time.time() - start, 2)

    missing = [r for r, e in energies.items() if e is None]
    unconverged = [s["role"] for s in species_records if not s["converged"]]
    if missing or unconverged:
        record.update(ok=False,
                      error=f"missing={missing} unconverged={unconverged}")
        _append(args.ledger, record)
        print(f"EVAL FAILED: missing={missing} unconverged={unconverged}")
        return 1

    delta = (
        energies["adduct_radical"] - energies["tool_radical"] - energies["substrate"]
    )
    de_kcal = delta * HARTREE_TO_KCAL
    record.update(
        reaction_energy_hartree=delta,
        reaction_energy_kcal=de_kcal,
        favorable=de_kcal < 0.0,
        ok=True,
    )
    _append(args.ledger, record)
    print(f"       dE = {de_kcal:+.1f} kcal/mol  -> "
          f"{'FAVORABLE' if de_kcal < 0 else 'unfavorable'}  "
          f"({record['wall_seconds']:.0f}s, {config.method_string()})")
    return 0


def _run_barrier(args, config, spec_id: str) -> int:
    from cheiron.addition import addition_barrier_scan

    scans = RESULTS / "scans.jsonl"
    print(f"distances (A): {sorted(args.distances, reverse=True)}")
    scan = addition_barrier_scan(TOOLS[args.tool], args.substrate, args.distances, config)
    record = scan.to_dict()
    record["created_unix"] = int(time.time())
    _append(scans, record)
    print(f"appended scan record -> {scans}")
    if not scan.ok:
        print(f"SCAN FAILED: {scan.error}")
        return 1
    for d, e in sorted(scan.relative_kcal(), reverse=True):
        print(f"  d={d:4.2f} A   E-Einf = {e:+8.2f} kcal/mol")
    print(f"barrier estimate: {scan.barrier_kcal():.2f} kcal/mol  "
          f"(well-resolved: {scan.barrier_well_resolved()}; {scan.wall_seconds:.0f}s)")
    if scan.barrier_well_resolved() is False:
        print("  WARNING: barrier not well-resolved — refine the grid across the saddle.")
    return 0


def _append(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
