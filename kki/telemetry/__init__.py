"""Telemetry boundary for audit, diagnostics, and evidence flows."""

from kki.module_boundaries import ModuleBoundary, module_boundary

BOUNDARY: ModuleBoundary = module_boundary("telemetry")

__all__ = ["BOUNDARY"]
