"""The ledger: one immutable JSONL record per candidate that enters the loop.

Append-only. Nothing is mutated or deleted — corrections are new records that
supersede old ones by id. This is what makes "failures published alongside
results" auditable rather than aspirational: a candidate that failed favorability
is as permanent in the ledger as one that succeeded.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LedgerRecord:
    spec: dict
    build: dict           # {"ok": bool, "error": str|None}
    measurement: dict | None
    fitness: dict | None
    select: dict | None = None   # filled by SELECT/EVOLVE
    veto: dict | None = None     # filled by the human gate
    status: str = "evaluated"    # evaluated | survived | retired | accepted | vetoed

    def to_json(self) -> str:
        return json.dumps(
            {
                "spec": self.spec,
                "build": self.build,
                "measurement": self.measurement,
                "fitness": self.fitness,
                "select": self.select,
                "veto": self.veto,
                "status": self.status,
            },
            sort_keys=True,
        )


class Ledger:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, record: LedgerRecord) -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(record.to_json() + "\n")

    def read_all(self) -> list[dict]:
        if not self.path.exists():
            return []
        with self.path.open(encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]

    def latest_by_spec(self) -> dict[str, dict]:
        """Most recent record per spec id (later records supersede earlier ones)."""
        latest: dict[str, dict] = {}
        for rec in self.read_all():
            spec_id = rec.get("spec", {}).get("id")
            if spec_id is not None:
                latest[spec_id] = rec
        return latest

    def fragment_reference(self, spec_id: str, method: str) -> float | None:
        """E(tool_radical) + E(workpiece) from this spec's latest usable record.

        Approach scans reference against separated fragments; reusing the
        ledger's converged energies keeps every scan consistent with the M0
        numbers by construction (independently re-optimized fragments can land
        in different local minima ~1 kcal/mol apart). ``method`` must match the
        record's method string — an energy is only reusable at the method that
        produced it. Returns None if there is no matching converged record.
        """
        record = self.latest_by_spec().get(spec_id)
        if not record or not record.get("measurement"):
            return None
        measurement = record["measurement"]
        if measurement.get("method") != method:
            return None
        energies = {}
        for s in measurement.get("species", []):
            if s.get("converged") and s.get("energy_hartree") is not None:
                energies[s["role"]] = s["energy_hartree"]
        if "tool_radical" not in energies or "workpiece" not in energies:
            return None
        return energies["tool_radical"] + energies["workpiece"]
