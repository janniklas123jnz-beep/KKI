"""Recovery orchestration across rollout state, directives, and re-entry paths."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from kki.governance import GateDecision, GateOutcome, evaluate_gate
from kki.message_protocols import MessageEnvelope, command_message
from kki.module_boundaries import ModuleBoundaryName
from kki.recovery.primitives import (
    RecoveryCheckpoint,
    RecoveryMode,
    RecoveryOutcome,
    RollbackDirective,
    recovery_checkpoint_for_state,
    recovery_outcome,
    rollback_directive_for_checkpoint,
)
from kki.rollout import RolloutPhase, RolloutState
from kki.security import AuthorizationIdentity, LoadedControlPlane, OperatingMode
from kki.telemetry import CorrelatedOperation, TelemetrySignal, correlate_operation


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


class RecoveryDisposition(str, Enum):
    """Resolved recovery disposition over rollback, restart, and re-entry."""

    CONTAIN = "contain"
    RESTART = "restart"
    RESUME = "resume"


@dataclass(frozen=True)
class RecoveryOrchestration:
    """Coordinated recovery plan derived from a rollout state."""

    orchestration_id: str
    mode: RecoveryMode
    disposition: RecoveryDisposition
    rollout_state: RolloutState
    recovery_command: MessageEnvelope
    checkpoint: RecoveryCheckpoint
    directive: RollbackDirective
    gate_decision: GateDecision
    outcome: RecoveryOutcome
    correlation: CorrelatedOperation
    recovery_signal: TelemetrySignal
    resume_ready: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "orchestration_id", _non_empty(self.orchestration_id, field_name="orchestration_id"))
        if self.rollout_state.correlation_id != self.checkpoint.correlation_id:
            raise ValueError("checkpoint correlation_id must match rollout state")
        if self.directive.correlation_id != self.rollout_state.correlation_id:
            raise ValueError("directive correlation_id must match rollout state")
        if self.outcome.directive.directive_id != self.directive.directive_id:
            raise ValueError("outcome must belong to directive")
        if self.correlation.correlation_id != self.rollout_state.correlation_id:
            raise ValueError("correlation view must match rollout state")

    def to_dict(self) -> dict[str, object]:
        return {
            "orchestration_id": self.orchestration_id,
            "mode": self.mode.value,
            "disposition": self.disposition.value,
            "rollout_state": self.rollout_state.to_dict(),
            "recovery_command": self.recovery_command.to_dict(),
            "checkpoint": self.checkpoint.to_dict(),
            "directive": self.directive.to_dict(),
            "gate_decision": self.gate_decision.to_dict(),
            "outcome": self.outcome.to_dict(),
            "correlation": self.correlation.to_dict(),
            "recovery_signal": self.recovery_signal.to_dict(),
            "resume_ready": self.resume_ready,
        }


def _recovery_command_for_rollout(rollout_state: RolloutState, mode: RecoveryMode) -> MessageEnvelope:
    return command_message(
        name=f"{mode.value}-{rollout_state.work_unit_id}",
        source_boundary=ModuleBoundaryName.ROLLOUT,
        target_boundary=ModuleBoundaryName.RECOVERY,
        correlation_id=rollout_state.correlation_id,
        payload={
            "rollout_id": rollout_state.rollout_id,
            "phase": rollout_state.phase.value,
            "promotion_ready": rollout_state.promotion_ready,
            "rollback_required": rollout_state.rollback_required,
            "mode": mode.value,
        },
    )


def _mode_for_rollout_state(rollout_state: RolloutState) -> RecoveryMode:
    if rollout_state.phase is RolloutPhase.ROLLBACK_READY:
        return RecoveryMode.ROLLBACK
    if rollout_state.phase is RolloutPhase.HELD:
        return RecoveryMode.RESTART
    return RecoveryMode.REENTRY


def _disposition_for_mode(mode: RecoveryMode) -> RecoveryDisposition:
    return {
        RecoveryMode.ROLLBACK: RecoveryDisposition.CONTAIN,
        RecoveryMode.RESTART: RecoveryDisposition.RESTART,
        RecoveryMode.REENTRY: RecoveryDisposition.RESUME,
    }[mode]


def _replay_ready_for_rollout(rollout_state: RolloutState, mode: RecoveryMode) -> bool:
    if mode is RecoveryMode.REENTRY:
        return rollout_state.shadow_coordination.release_ready and rollout_state.phase in {
            RolloutPhase.CANARY,
            RolloutPhase.ACTIVE,
        }
    return False


def _reason_for_mode(rollout_state: RolloutState, mode: RecoveryMode) -> str:
    if mode is RecoveryMode.ROLLBACK:
        return f"rollback required after rollout phase {rollout_state.phase.value}"
    if mode is RecoveryMode.RESTART:
        return f"restart required while rollout phase {rollout_state.phase.value} is held"
    return f"reentry path prepared after rollout phase {rollout_state.phase.value}"


def _recovery_signal_for_orchestration(
    *,
    mode: RecoveryMode,
    disposition: RecoveryDisposition,
    rollout_state: RolloutState,
    gate_decision: GateDecision,
    outcome: RecoveryOutcome,
) -> tuple[TelemetrySignal, bool]:
    status = outcome.status
    severity = "info" if outcome.replay_ready else ("critical" if mode is RecoveryMode.ROLLBACK else "warning")
    return (
        TelemetrySignal(
            signal_name="recovery-orchestration",
            boundary=ModuleBoundaryName.RECOVERY,
            correlation_id=rollout_state.correlation_id,
            severity=severity,
            status=status,
            metrics={
                "rollback_required": float(rollout_state.rollback_required),
                "promotion_ready": float(rollout_state.promotion_ready),
                "rollback_steps": len(outcome.directive.rollback_chain),
            },
            labels={
                "mode": mode.value,
                "disposition": disposition.value,
                "rollout_phase": rollout_state.phase.value,
                "gate_outcome": gate_decision.outcome.value,
            },
        ),
        outcome.replay_ready and gate_decision.outcome is GateOutcome.GO,
    )


def orchestrate_recovery_for_rollout(
    rollout_state: RolloutState,
    *,
    control_plane: LoadedControlPlane,
    identity: AuthorizationIdentity,
    mode: RecoveryMode | str | None = None,
    operating_mode: OperatingMode | str = OperatingMode.RECOVERY,
    evidence_ref: str,
    commitment_ref: str | None = None,
    audit_ref: str | None = None,
) -> RecoveryOrchestration:
    """Orchestrate rollback, restart, or re-entry for a rollout state."""

    resolved_mode = mode if isinstance(mode, RecoveryMode) else RecoveryMode(mode) if mode is not None else _mode_for_rollout_state(rollout_state)
    recovery_command = _recovery_command_for_rollout(rollout_state, resolved_mode)
    gate_decision = evaluate_gate(
        identity,
        boundary=ModuleBoundaryName.RECOVERY,
        control_plane=control_plane,
        message=recovery_command,
        operating_mode=operating_mode,
        evidence_ref=evidence_ref,
        commitment_ref=commitment_ref,
    )
    checkpoint = recovery_checkpoint_for_state(rollout_state.to_core_state(), correlation_id=rollout_state.correlation_id)
    directive = rollback_directive_for_checkpoint(
        checkpoint,
        control_plane,
        reason=_reason_for_mode(rollout_state, resolved_mode),
        mode=resolved_mode,
    )
    replay_ready = _replay_ready_for_rollout(rollout_state, resolved_mode)
    outcome = recovery_outcome(
        directive,
        checkpoint,
        control_plane,
        replay_ready=replay_ready,
        audit_ref=audit_ref or f"audit-{rollout_state.correlation_id}",
        commitment_ref=commitment_ref,
    )
    correlation = correlate_operation(
        control_plane=control_plane,
        message=recovery_command,
        dispatch_assignment=rollout_state.shadow_coordination.dispatch_assignment,
        gate_decision=gate_decision,
    )
    disposition = _disposition_for_mode(resolved_mode)
    recovery_signal, resume_ready = _recovery_signal_for_orchestration(
        mode=resolved_mode,
        disposition=disposition,
        rollout_state=rollout_state,
        gate_decision=gate_decision,
        outcome=outcome,
    )
    return RecoveryOrchestration(
        orchestration_id=f"recovery-{rollout_state.work_unit_id}",
        mode=resolved_mode,
        disposition=disposition,
        rollout_state=rollout_state,
        recovery_command=recovery_command,
        checkpoint=checkpoint,
        directive=directive,
        gate_decision=gate_decision,
        outcome=outcome,
        correlation=correlation,
        recovery_signal=recovery_signal,
        resume_ready=resume_ready,
    )
