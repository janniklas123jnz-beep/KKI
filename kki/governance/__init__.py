"""Governance boundary for approvals, commitments, and intervention control."""

from kki.module_boundaries import ModuleBoundary, module_boundary

BOUNDARY: ModuleBoundary = module_boundary("governance")

__all__ = ["BOUNDARY"]
