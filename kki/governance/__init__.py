"""Governance boundary for approvals, commitments, and intervention control."""

from kki.module_boundaries import ModuleBoundary, module_boundary

from .gates import GateDecision, GateOutcome, evaluate_gate
from .human_loop import HumanDecision, HumanLoopGovernance, govern_recovery_orchestration

BOUNDARY: ModuleBoundary = module_boundary("governance")

__all__ = [
    "BOUNDARY",
    "GateDecision",
    "GateOutcome",
    "HumanDecision",
    "HumanLoopGovernance",
    "evaluate_gate",
    "govern_recovery_orchestration",
]
