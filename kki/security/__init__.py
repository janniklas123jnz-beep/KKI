"""Security boundary for gates, policies, and quarantine decisions."""

from kki.module_boundaries import ModuleBoundary, module_boundary

BOUNDARY: ModuleBoundary = module_boundary("security")

__all__ = ["BOUNDARY"]
