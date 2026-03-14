"""Orchestration boundary for budget, state, and triage coordination."""

from kki.module_boundaries import ModuleBoundary, module_boundary

BOUNDARY: ModuleBoundary = module_boundary("orchestration")

__all__ = ["BOUNDARY"]
