"""Recovery boundary for rollback, restart, and re-entry paths."""

from kki.module_boundaries import ModuleBoundary, module_boundary
from kki.recovery.orchestrator import RecoveryDisposition, RecoveryOrchestration, orchestrate_recovery_for_rollout
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
    "RecoveryDisposition",
    "RecoveryMode",
    "RecoveryOrchestration",
    "RecoveryOutcome",
    "RollbackDirective",
    "orchestrate_recovery_for_rollout",
    "recovery_checkpoint_for_state",
    "recovery_outcome",
    "rollback_directive_for_checkpoint",
]
