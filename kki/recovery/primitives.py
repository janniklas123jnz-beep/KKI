"""Recovery and rollback primitives for the build-phase package."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from kki.data_models import (
    CoreState,
    EvidenceRecord,
    PersistenceRecord,
    TransferEnvelope,
    transfer_envelope_for_state,
)
from kki.module_boundaries import ModuleBoundaryName, module_boundary
from kki.security.config_loader import LoadedControlPlane
from kki.telemetry.foundation import AuditTrailEntry, TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


class RecoveryMode(str, Enum):
    """Canonical recovery modes for rollback, restart, and re-entry."""

    ROLLBACK = "rollback"
    RESTART = "restart"
    REENTRY = "reentry"


@dataclass(frozen=True)
class RecoveryCheckpoint:
    """Captured recovery checkpoint built from state, persistence, and transfer contracts."""

    checkpoint_id: str
    correlation_id: str
    source_boundary: ModuleBoundaryName
    state: CoreState
    persistence_record: PersistenceRecord
    transfer_envelope: TransferEnvelope

    def __post_init__(self) -> None:
        object.__setattr__(self, "checkpoint_id", _non_empty(self.checkpoint_id, field_name="checkpoint_id"))
        object.__setattr__(self, "correlation_id", _non_empty(self.correlation_id, field_name="correlation_id"))
        module_boundary(self.source_boundary)
        if self.state.module_boundary != self.source_boundary:
            raise ValueError("checkpoint source boundary must match the state boundary")
        if self.transfer_envelope.target_boundary != ModuleBoundaryName.RECOVERY:
            raise ValueError("recovery checkpoint transfers must target the recovery boundary")

    def to_dict(self) -> dict[str, object]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "correlation_id": self.correlation_id,
            "source_boundary": self.source_boundary.value,
            "state": self.state.to_dict(),
            "persistence_record": self.persistence_record.to_dict(),
            "transfer_envelope": self.transfer_envelope.to_dict(),
        }


@dataclass(frozen=True)
class RollbackDirective:
    """Rollback or restart directive derived from a checkpoint and control-plane state."""

    directive_id: str
    mode: RecoveryMode
    correlation_id: str
    checkpoint_id: str
    target_boundary: ModuleBoundaryName
    target_state: CoreState
    rollback_chain: tuple[str, ...]
    reason: str
    replay_source: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "directive_id", _non_empty(self.directive_id, field_name="directive_id"))
        object.__setattr__(self, "correlation_id", _non_empty(self.correlation_id, field_name="correlation_id"))
        object.__setattr__(self, "checkpoint_id", _non_empty(self.checkpoint_id, field_name="checkpoint_id"))
        object.__setattr__(self, "reason", _non_empty(self.reason, field_name="reason"))
        object.__setattr__(self, "replay_source", _non_empty(self.replay_source, field_name="replay_source"))
        module_boundary(self.target_boundary)
        if self.target_state.module_boundary != self.target_boundary:
            raise ValueError("target_state boundary must match target_boundary")
        if not self.rollback_chain:
            raise ValueError("rollback_chain must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "directive_id": self.directive_id,
            "mode": self.mode.value,
            "correlation_id": self.correlation_id,
            "checkpoint_id": self.checkpoint_id,
            "target_boundary": self.target_boundary.value,
            "target_state": self.target_state.to_dict(),
            "rollback_chain": list(self.rollback_chain),
            "reason": self.reason,
            "replay_source": self.replay_source,
        }


@dataclass(frozen=True)
class RecoveryOutcome:
    """Resolved recovery outcome with evidence and telemetry bindings."""

    directive: RollbackDirective
    status: str
    replay_ready: bool
    evidence: EvidenceRecord
    signal: TelemetrySignal
    snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        if self.status not in {"rollback-active", "restart-active", "reentry-ready"}:
            raise ValueError("status must be one of: rollback-active, restart-active, reentry-ready")

    def to_dict(self) -> dict[str, object]:
        return {
            "directive": self.directive.to_dict(),
            "status": self.status,
            "replay_ready": self.replay_ready,
            "evidence": self.evidence.to_dict(),
            "signal": self.signal.to_dict(),
            "snapshot": self.snapshot.to_dict(),
        }


def recovery_checkpoint_for_state(
    state: CoreState,
    *,
    correlation_id: str,
    schema_version: str = "1.0",
    retention_class: str = "restart",
) -> RecoveryCheckpoint:
    """Create the canonical recovery checkpoint for a runtime state."""

    checkpoint_id = f"checkpoint-{correlation_id}-{state.module_boundary.value}"
    persistence_record = PersistenceRecord(
        record_type="recovery-checkpoint",
        boundary=ModuleBoundaryName.RECOVERY,
        schema_version=schema_version,
        retention_class=retention_class,
        payload=state.to_dict(),
    )
    transfer_envelope = transfer_envelope_for_state(
        state,
        target_boundary=ModuleBoundaryName.RECOVERY,
        correlation_id=correlation_id,
        schema_version=schema_version,
        integrity_status="verified",
    )
    return RecoveryCheckpoint(
        checkpoint_id=checkpoint_id,
        correlation_id=correlation_id,
        source_boundary=state.module_boundary,
        state=state,
        persistence_record=persistence_record,
        transfer_envelope=transfer_envelope,
    )


def rollback_directive_for_checkpoint(
    checkpoint: RecoveryCheckpoint,
    control_plane: LoadedControlPlane,
    *,
    reason: str,
    mode: RecoveryMode = RecoveryMode.ROLLBACK,
) -> RollbackDirective:
    """Create the canonical rollback or restart directive for a checkpoint."""

    rollback_chain = control_plane.rollback_chain or ("state-only-recovery",)
    return RollbackDirective(
        directive_id=f"{mode.value}-{checkpoint.checkpoint_id}",
        mode=mode,
        correlation_id=checkpoint.correlation_id,
        checkpoint_id=checkpoint.checkpoint_id,
        target_boundary=checkpoint.source_boundary,
        target_state=checkpoint.state,
        rollback_chain=tuple(rollback_chain),
        reason=reason,
        replay_source=checkpoint.transfer_envelope.correlation_id,
    )


def recovery_outcome(
    directive: RollbackDirective,
    checkpoint: RecoveryCheckpoint,
    control_plane: LoadedControlPlane,
    *,
    replay_ready: bool,
    audit_ref: str,
    commitment_ref: str | None = None,
) -> RecoveryOutcome:
    """Resolve recovery status into evidence and telemetry artifacts."""

    status = "reentry-ready" if replay_ready else f"{directive.mode.value}-active"
    severity = "info" if replay_ready else "warning"
    signal = TelemetrySignal(
        signal_name=f"{directive.mode.value}-status",
        boundary=ModuleBoundaryName.RECOVERY,
        correlation_id=directive.correlation_id,
        severity=severity,
        status=status,
        metrics={
            "rollback_steps": len(directive.rollback_chain),
            "checkpoint_budget": checkpoint.state.budget,
            "active_controls": len(control_plane.applied_artifacts),
        },
        labels={
            "checkpoint_id": checkpoint.checkpoint_id,
            "target_boundary": directive.target_boundary.value,
        },
    )
    evidence = EvidenceRecord(
        evidence_type="recovery-outcome",
        subject=directive.directive_id,
        correlation_id=directive.correlation_id,
        audit_ref=audit_ref,
        commitment_ref=commitment_ref,
        payload={
            "mode": directive.mode.value,
            "status": status,
            "rollback_chain": list(directive.rollback_chain),
            "replay_ready": replay_ready,
        },
    )
    audit_entries = [
        AuditTrailEntry(
            entry_type="recovery-checkpoint",
            subject=checkpoint.checkpoint_id,
            boundary=ModuleBoundaryName.RECOVERY,
            correlation_id=directive.correlation_id,
            integrity_status=checkpoint.transfer_envelope.integrity_status,
            payload={
                "source_boundary": checkpoint.source_boundary.value,
                "retention_class": checkpoint.persistence_record.retention_class,
            },
        ),
        AuditTrailEntry(
            entry_type="rollback-directive",
            subject=directive.directive_id,
            boundary=ModuleBoundaryName.RECOVERY,
            correlation_id=directive.correlation_id,
            evidence_ref=audit_ref,
            commitment_ref=commitment_ref,
            payload={
                "mode": directive.mode.value,
                "rollback_chain": list(directive.rollback_chain),
                "reason": directive.reason,
            },
        ),
    ]
    snapshot = build_telemetry_snapshot(
        runtime_stage=control_plane.runtime_stage,
        signals=(signal,),
        audit_entries=tuple(audit_entries),
        active_controls=tuple(artifact.artifact_id for artifact in control_plane.applied_artifacts),
    )
    return RecoveryOutcome(
        directive=directive,
        status=status,
        replay_ready=replay_ready,
        evidence=evidence,
        signal=signal,
        snapshot=snapshot,
    )
