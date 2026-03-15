"""Shadow boundary for preview, replay, and parallel validation."""

from kki.module_boundaries import ModuleBoundary, module_boundary
from kki.shadow.coordinator import ShadowCoordination, ShadowCoordinationMode, coordinate_shadow_work
from kki.shadow.interfaces import (
    DryRunEvaluation,
    PreviewMode,
    ShadowPreview,
    evaluate_dry_run,
    shadow_event,
    shadow_preview_for_command,
    shadow_snapshot,
)

BOUNDARY: ModuleBoundary = module_boundary("shadow")

__all__ = [
    "BOUNDARY",
    "DryRunEvaluation",
    "PreviewMode",
    "ShadowCoordination",
    "ShadowCoordinationMode",
    "ShadowPreview",
    "coordinate_shadow_work",
    "evaluate_dry_run",
    "shadow_event",
    "shadow_preview_for_command",
    "shadow_snapshot",
]
