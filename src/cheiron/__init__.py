"""cheiron — an autonomous design loop for positional molecular assembly.

The loop: PROPOSE -> BUILD -> ARBITER -> SCORE -> SELECT/EVOLVE, with a human
VETO gate, logging every candidate to an append-only ledger. See docs/design/.
"""

__version__ = "0.0.1"

from .arbiter import ArbiterConfig, evaluate_reaction
from .builder import build
from .ledger import Ledger, LedgerRecord
from .loop import run_batch, select
from .proposer import enumerate_candidates
from .score import score
from .spec import CandidateSpec, ToolSpec, WorkpieceSpec

__all__ = [
    "ArbiterConfig",
    "CandidateSpec",
    "Ledger",
    "LedgerRecord",
    "ToolSpec",
    "WorkpieceSpec",
    "build",
    "enumerate_candidates",
    "evaluate_reaction",
    "run_batch",
    "score",
    "select",
]
