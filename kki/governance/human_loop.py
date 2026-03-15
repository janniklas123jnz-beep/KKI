"""Human-in-the-loop governance for rollout and recovery intervention paths."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from kki.data_models import EvidenceRecord
from kki.security import ActionName
from kki.governance.gates import GateDecision, GateOutcome, evaluate_gate
from kki.message_protocols import MessageEnvelope, command_message
from kki.module_boundaries import ModuleBoundaryName
from kki.recovery import RecoveryOrchestration
from kki.rollout import RolloutState
from kki.security import AuthorizationIdentity, LoadedControlPlane, OperatingMode
from kki.telemetry import CorrelatedOperation, TelemetrySignal, correlate_operation


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


class HumanDecision(str, Enum):
    """Human governance decisions over promotion and recovery paths."""

    APPROVE = "approve"
    HOLD = "hold"
    ESCALATE = "escalate"
    OVERRIDE = "override"


@dataclass(frozen=True)
class HumanLoopGovernance:
    """Bound human governance decision over rollout and recovery state."""

    governance_id: str
    decision: HumanDecision
    subject_ref: str
    recovery_orchestration: RecoveryOrchestration
    command: MessageEnvelope
    gate_decision: GateDecision
    evidence: EvidenceRecord
    correlation: CorrelatedOperation
    governance_signal: TelemetrySignal
    release_authorized: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "governance_id", _non_empty(self.governance_id, field_name="governance_id"))
        object.__setattr__(self, "subject_ref", _non_empty(self.subject_ref, field_name="subject_ref"))
        if self.command.context.correlation_id != self.recovery_orchestration.rollout_state.correlation_id:
            raise ValueError("command correlation_id must match recovery orchestration")
        if self.correlation.correlation_id != self.recovery_orchestration.rollout_state.correlation_id:
            raise ValueError("correlation view must match recovery orchestration")
        if self.evidence.correlation_id != self.recovery_orchestration.rollout_state.correlation_id:
            raise ValueError("evidence correlation_id must match recovery orchestration")

    def to_dict(self) -> dict[str, object]:
        return {
            "governance_id": self.governance_id,
            "decision": self.decision.value,
            "subject_ref": self.subject_ref,
            "recovery_orchestration": self.recovery_orchestration.to_dict(),
            "command": self.command.to_dict(),
            "gate_decision": self.gate_decision.to_dict(),
            "evidence": self.evidence.to_dict(),
            "correlation": self.correlation.to_dict(),
            "governance_signal": self.governance_signal.to_dict(),
            "release_authorized": self.release_authorized,
        }


def _governance_command_for_decision(
    recovery_orchestration: RecoveryOrchestration,
    decision: HumanDecision,
) -> MessageEnvelope:
    return command_message(
        name=f"governance-{decision.value}",
        source_boundary=ModuleBoundaryName.GOVERNANCE,
        target_boundary=ModuleBoundaryName.GOVERNANCE,
        correlation_id=recovery_orchestration.rollout_state.correlation_id,
        payload={
            "decision": decision.value,
            "rollout_phase": recovery_orchestration.rollout_state.phase.value,
            "recovery_mode": recovery_orchestration.mode.value,
            "recovery_disposition": recovery_orchestration.disposition.value,
            "resume_ready": recovery_orchestration.resume_ready,
        },
    )


def _operating_mode_for_decision(decision: HumanDecision) -> OperatingMode:
    if decision is HumanDecision.OVERRIDE:
        return OperatingMode.EMERGENCY
    if decision is HumanDecision.ESCALATE:
        return OperatingMode.RECOVERY
    return OperatingMode.NORMAL


def _release_authorized(
    *,
    decision: HumanDecision,
    gate_decision: GateDecision,
    recovery_orchestration: RecoveryOrchestration,
) -> bool:
    if decision is HumanDecision.APPROVE:
        return gate_decision.outcome is GateOutcome.GO and recovery_orchestration.resume_ready
    if decision is HumanDecision.OVERRIDE:
        return gate_decision.authorization.allowed and gate_decision.outcome in {GateOutcome.GO, GateOutcome.ESCALATE}
    return False


def _signal_for_governance(
    *,
    decision: HumanDecision,
    gate_decision: GateDecision,
    recovery_orchestration: RecoveryOrchestration,
    release_authorized: bool,
) -> TelemetrySignal:
    severity = "info"
    status = "authorized" if release_authorized else "held"
    if release_authorized and decision is HumanDecision.OVERRIDE:
        severity = "warning"
        status = "authorized-override"
    if decision in {HumanDecision.HOLD, HumanDecision.ESCALATE} or gate_decision.outcome in {
        GateOutcome.HOLD,
        GateOutcome.ESCALATE,
    }:
        severity = "warning"
        status = "escalated" if decision is HumanDecision.ESCALATE else status
    if gate_decision.outcome is GateOutcome.BLOCK:
        severity = "critical"
        status = "blocked"
    return TelemetrySignal(
        signal_name="human-governance",
        boundary=ModuleBoundaryName.GOVERNANCE,
        correlation_id=recovery_orchestration.rollout_state.correlation_id,
        severity=severity,
        status=status,
        metrics={
            "resume_ready": float(recovery_orchestration.resume_ready),
            "rollback_required": float(recovery_orchestration.rollout_state.rollback_required),
            "promotion_ready": float(recovery_orchestration.rollout_state.promotion_ready),
        },
        labels={
            "decision": decision.value,
            "recovery_mode": recovery_orchestration.mode.value,
            "gate_outcome": gate_decision.outcome.value,
            "rollout_phase": recovery_orchestration.rollout_state.phase.value,
        },
    )


def govern_recovery_orchestration(
    recovery_orchestration: RecoveryOrchestration,
    *,
    control_plane: LoadedControlPlane,
    identity: AuthorizationIdentity,
    decision: HumanDecision | str,
    audit_ref: str,
    commitment_ref: str | None = None,
) -> HumanLoopGovernance:
    """Bind a human governance decision to a recovery orchestration path."""

    resolved_decision = decision if isinstance(decision, HumanDecision) else HumanDecision(decision)
    command = _governance_command_for_decision(recovery_orchestration, resolved_decision)
    operating_mode = _operating_mode_for_decision(resolved_decision)
    gate_decision = evaluate_gate(
        identity,
        boundary=ModuleBoundaryName.GOVERNANCE,
        control_plane=control_plane,
        message=command,
        action=ActionName.OVERRIDE if resolved_decision is HumanDecision.OVERRIDE else ActionName.APPROVE,
        operating_mode=operating_mode,
        evidence_ref=audit_ref,
        commitment_ref=commitment_ref,
    )
    evidence = EvidenceRecord(
        evidence_type="human-governance-decision",
        subject=recovery_orchestration.orchestration_id,
        correlation_id=recovery_orchestration.rollout_state.correlation_id,
        audit_ref=audit_ref,
        commitment_ref=commitment_ref,
        payload={
            "decision": resolved_decision.value,
            "recovery_mode": recovery_orchestration.mode.value,
            "disposition": recovery_orchestration.disposition.value,
            "resume_ready": recovery_orchestration.resume_ready,
            "gate_outcome": gate_decision.outcome.value,
        },
    )
    correlation = correlate_operation(
        control_plane=control_plane,
        message=command,
        dispatch_assignment=recovery_orchestration.rollout_state.shadow_coordination.dispatch_assignment,
        gate_decision=gate_decision,
    )
    release_authorized = _release_authorized(
        decision=resolved_decision,
        gate_decision=gate_decision,
        recovery_orchestration=recovery_orchestration,
    )
    return HumanLoopGovernance(
        governance_id=f"governance-{recovery_orchestration.rollout_state.work_unit_id}",
        decision=resolved_decision,
        subject_ref=recovery_orchestration.orchestration_id,
        recovery_orchestration=recovery_orchestration,
        command=command,
        gate_decision=gate_decision,
        evidence=evidence,
        correlation=correlation,
        governance_signal=_signal_for_governance(
            decision=resolved_decision,
            gate_decision=gate_decision,
            recovery_orchestration=recovery_orchestration,
            release_authorized=release_authorized,
        ),
        release_authorized=release_authorized,
    )
