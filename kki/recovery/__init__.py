"""Recovery boundary for rollback, restart, and re-entry paths."""

from kki.module_boundaries import ModuleBoundary, module_boundary

BOUNDARY: ModuleBoundary = module_boundary("recovery")

__all__ = ["BOUNDARY"]
