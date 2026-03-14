"""Shadow boundary for preview, replay, and parallel validation."""

from kki.module_boundaries import ModuleBoundary, module_boundary

BOUNDARY: ModuleBoundary = module_boundary("shadow")

__all__ = ["BOUNDARY"]
