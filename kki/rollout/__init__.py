"""Rollout boundary for controlled promotion and activation paths."""

from kki.module_boundaries import ModuleBoundary, module_boundary

BOUNDARY: ModuleBoundary = module_boundary("rollout")

__all__ = ["BOUNDARY"]
