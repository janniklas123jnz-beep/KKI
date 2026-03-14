"""Recovery boundary for rollback, restart, and re-entry paths."""

from kki.module_boundaries import ModuleBoundary, module_boundary
from kki.recovery.primitives import (
    RecoveryCheckpoint,
    RecoveryMode,
    RecoveryOutcome,
    RollbackDirective,
    recovery_checkpoint_for_state,
    recovery_outcome,
    rollback_directive_for_checkpoint,
)

BOUNDARY: ModuleBoundary = module_boundary("recovery")

__all__ = [
    "BOUNDARY",
    "RecoveryCheckpoint",
    "RecoveryMode",
    "RecoveryOutcome",
    "RollbackDirective",
    "recovery_checkpoint_for_state",
    "recovery_outcome",
    "rollback_directive_for_checkpoint",
]
