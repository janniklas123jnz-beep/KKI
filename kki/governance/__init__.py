"""Governance boundary for approvals, commitments, and intervention control."""

from kki.module_boundaries import ModuleBoundary, module_boundary

from .gates import GateDecision, GateOutcome, evaluate_gate

BOUNDARY: ModuleBoundary = module_boundary("governance")

__all__ = ["BOUNDARY", "GateDecision", "GateOutcome", "evaluate_gate"]
