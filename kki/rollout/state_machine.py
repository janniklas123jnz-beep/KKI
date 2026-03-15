"""Validated rollout state machine built from shadow release decisions."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from kki.data_models import CoreState
from kki.governance import GateDecision, GateOutcome, evaluate_gate
from kki.message_protocols import MessageEnvelope, command_message
from kki.module_boundaries import ModuleBoundaryName, module_boundary
from kki.security import AuthorizationIdentity, LoadedControlPlane, OperatingMode
from kki.shadow import ShadowCoordination, ShadowCoordinationMode
from kki.telemetry import CorrelatedOperation, TelemetrySignal, correlate_operation


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _frozen_mapping(data: Mapping[str, object] | None) -> Mapping[str, object]:
    return MappingProxyType(dict(data or {}))


class RolloutPhase(str, Enum):
    """Canonical rollout phases after shadow validation."""

    STAGED = "staged"
    PROMOTING = "promoting"
    CANARY = "canary"
    ACTIVE = "active"
    HELD = "held"
    ROLLBACK_READY = "rollback-ready"


@dataclass(frozen=True)
class RolloutState:
    """Validated rollout state derived from a shadow coordination result."""

    rollout_id: str
    correlation_id: str
    runtime_stage: str
    phase: RolloutPhase
    work_unit_id: str
    target_boundary: ModuleBoundaryName
    command: MessageEnvelope
    shadow_coordination: ShadowCoordination
    gate_decision: GateDecision
    correlation: CorrelatedOperation
    promotion_signal: TelemetrySignal
    blockers: tuple[str, ...] = ()
    labels: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "rollout_id", _non_empty(self.rollout_id, field_name="rollout_id"))
        object.__setattr__(self, "correlation_id", _non_empty(self.correlation_id, field_name="correlation_id"))
        object.__setattr__(self, "runtime_stage", _non_empty(self.runtime_stage, field_name="runtime_stage"))
        object.__setattr__(self, "work_unit_id", _non_empty(self.work_unit_id, field_name="work_unit_id"))
        module_boundary(self.target_boundary)
        cleaned_blockers = tuple(blocker.strip() for blocker in self.blockers if blocker.strip())
        object.__setattr__(self, "blockers", cleaned_blockers)
        object.__setattr__(self, "labels", _frozen_mapping(self.labels))
        if self.command.context.correlation_id != self.correlation_id:
            raise ValueError("command correlation_id must match rollout correlation_id")
        if self.shadow_coordination.work_unit.unit_id != self.work_unit_id:
            raise ValueError("shadow coordination must reference the same work unit")
        if self.correlation.correlation_id != self.correlation_id:
            raise ValueError("correlated rollout view must match rollout correlation_id")
        if self.phase is RolloutPhase.ROLLBACK_READY and not cleaned_blockers:
            raise ValueError("rollback-ready rollout state requires blockers")

    @property
    def promotion_ready(self) -> bool:
        return self.phase in {RolloutPhase.PROMOTING, RolloutPhase.CANARY, RolloutPhase.ACTIVE}

    @property
    def rollback_required(self) -> bool:
        return self.phase is RolloutPhase.ROLLBACK_READY

    def to_core_state(self) -> CoreState:
        return CoreState(
            identity_slug=self.shadow_coordination.work_unit.mission_ref,
            module_boundary=ModuleBoundaryName.ROLLOUT,
            runtime_stage=self.shadow_coordination.preview.runtime_stage,
            status=self.phase.value,
            budget=self.shadow_coordination.dispatch_assignment.reserved_budget,
            labels={
                "work_unit_id": self.work_unit_id,
                "shadow_mode": self.shadow_coordination.mode.value,
                "shadow_release_status": self.shadow_coordination.release_signal.status,
                "gate_outcome": self.gate_decision.outcome.value,
                "promotion_ready": self.promotion_ready,
                "rollback_required": self.rollback_required,
                "blockers": self.blockers,
                **dict(self.labels),
            },
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "rollout_id": self.rollout_id,
            "correlation_id": self.correlation_id,
            "runtime_stage": self.runtime_stage,
            "phase": self.phase.value,
            "work_unit_id": self.work_unit_id,
            "target_boundary": self.target_boundary.value,
            "command": self.command.to_dict(),
            "shadow_coordination": self.shadow_coordination.to_dict(),
            "gate_decision": self.gate_decision.to_dict(),
            "correlation": self.correlation.to_dict(),
            "promotion_signal": self.promotion_signal.to_dict(),
            "blockers": list(self.blockers),
            "labels": dict(self.labels),
            "promotion_ready": self.promotion_ready,
            "rollback_required": self.rollback_required,
        }


_ALLOWED_TRANSITIONS = {
    RolloutPhase.STAGED: {RolloutPhase.PROMOTING, RolloutPhase.HELD, RolloutPhase.ROLLBACK_READY},
    RolloutPhase.PROMOTING: {RolloutPhase.CANARY, RolloutPhase.HELD, RolloutPhase.ROLLBACK_READY},
    RolloutPhase.CANARY: {RolloutPhase.ACTIVE, RolloutPhase.HELD, RolloutPhase.ROLLBACK_READY},
    RolloutPhase.ACTIVE: {RolloutPhase.HELD, RolloutPhase.ROLLBACK_READY},
    RolloutPhase.HELD: {RolloutPhase.STAGED, RolloutPhase.PROMOTING, RolloutPhase.CANARY, RolloutPhase.ROLLBACK_READY},
    RolloutPhase.ROLLBACK_READY: set(),
}


def _rollout_command_for_shadow(coordination: ShadowCoordination) -> MessageEnvelope:
    return command_message(
        name=f"promote-{coordination.work_unit.boundary.value}",
        source_boundary=ModuleBoundaryName.SHADOW,
        target_boundary=ModuleBoundaryName.ROLLOUT,
        correlation_id=coordination.work_unit.correlation_id,
        payload={
            "work_unit_id": coordination.work_unit.unit_id,
            "shadow_mode": coordination.mode.value,
            "shadow_release_status": coordination.release_signal.status,
            "release_ready": coordination.release_ready,
            "target_boundary": coordination.work_unit.boundary.value,
        },
    )


def _phase_for_rollout(coordination: ShadowCoordination, gate_decision: GateDecision) -> RolloutPhase:
    if coordination.release_signal.status in {"parallel-required", "replay-required"}:
        return RolloutPhase.STAGED
    if coordination.release_signal.status == "hold" or gate_decision.outcome in {GateOutcome.HOLD, GateOutcome.ESCALATE}:
        return RolloutPhase.HELD
    if coordination.release_signal.status == "blocked" or gate_decision.outcome is GateOutcome.BLOCK:
        return RolloutPhase.ROLLBACK_READY
    if coordination.mode is ShadowCoordinationMode.REPLAY:
        return RolloutPhase.CANARY
    return RolloutPhase.PROMOTING


def _promotion_signal_for_state(
    *,
    coordination: ShadowCoordination,
    phase: RolloutPhase,
    gate_decision: GateDecision,
    blockers: tuple[str, ...],
) -> TelemetrySignal:
    severity = "info"
    if phase is RolloutPhase.HELD:
        severity = "warning"
    elif phase is RolloutPhase.ROLLBACK_READY:
        severity = "critical"
    return TelemetrySignal(
        signal_name="rollout-phase",
        boundary=ModuleBoundaryName.ROLLOUT,
        correlation_id=coordination.work_unit.correlation_id,
        severity=severity,
        status=phase.value,
        metrics={
            "reserved_budget": coordination.dispatch_assignment.reserved_budget,
            "divergence_score": coordination.evaluation.divergence_score,
            "blocker_count": len(blockers),
        },
        labels={
            "work_unit_id": coordination.work_unit.unit_id,
            "shadow_mode": coordination.mode.value,
            "shadow_release_status": coordination.release_signal.status,
            "gate_outcome": gate_decision.outcome.value,
            "target_boundary": coordination.work_unit.boundary.value,
        },
    )


def rollout_state_for_shadow(
    coordination: ShadowCoordination,
    *,
    control_plane: LoadedControlPlane,
    identity: AuthorizationIdentity,
    operating_mode: OperatingMode | str = OperatingMode.NORMAL,
    evidence_ref: str | None = None,
    commitment_ref: str | None = None,
) -> RolloutState:
    """Build the validated rollout state from a coordinated shadow release decision."""

    command = _rollout_command_for_shadow(coordination)
    gate_decision = evaluate_gate(
        identity,
        boundary=ModuleBoundaryName.ROLLOUT,
        control_plane=control_plane,
        message=command,
        dispatch_assignment=coordination.dispatch_assignment,
        operating_mode=operating_mode,
        evidence_ref=evidence_ref,
        commitment_ref=commitment_ref,
    )
    phase = _phase_for_rollout(coordination, gate_decision)
    blockers = tuple(dict.fromkeys(coordination.gate_decision.blockers + gate_decision.blockers))
    if coordination.release_signal.status == "blocked" and not blockers:
        blockers = ("shadow release blocked rollout promotion",)
    correlation = correlate_operation(
        control_plane=control_plane,
        message=command,
        dispatch_assignment=coordination.dispatch_assignment,
        gate_decision=gate_decision,
    )
    return RolloutState(
        rollout_id=f"rollout-{coordination.work_unit.unit_id}",
        correlation_id=coordination.work_unit.correlation_id,
        runtime_stage=coordination.preview.runtime_stage.value,
        phase=phase,
        work_unit_id=coordination.work_unit.unit_id,
        target_boundary=coordination.work_unit.boundary,
        command=command,
        shadow_coordination=coordination,
        gate_decision=gate_decision,
        correlation=correlation,
        promotion_signal=_promotion_signal_for_state(
            coordination=coordination,
            phase=phase,
            gate_decision=gate_decision,
            blockers=blockers,
        ),
        blockers=blockers,
        labels={
            "shadow_release_ready": coordination.release_ready,
            "shadow_release_status": coordination.release_signal.status,
        },
    )


def advance_rollout_state(
    rollout_state: RolloutState,
    *,
    phase: RolloutPhase,
    blockers: tuple[str, ...] = (),
    labels: Mapping[str, object] | None = None,
) -> RolloutState:
    """Advance the rollout state through validated promotion transitions."""

    if phase is not rollout_state.phase and phase not in _ALLOWED_TRANSITIONS[rollout_state.phase]:
        raise ValueError(f"invalid rollout transition: {rollout_state.phase.value} -> {phase.value}")
    next_blockers = rollout_state.blockers if not blockers else tuple(blockers)
    next_labels = dict(rollout_state.labels)
    if labels:
        next_labels.update(labels)
    return RolloutState(
        rollout_id=rollout_state.rollout_id,
        correlation_id=rollout_state.correlation_id,
        runtime_stage=rollout_state.runtime_stage,
        phase=phase,
        work_unit_id=rollout_state.work_unit_id,
        target_boundary=rollout_state.target_boundary,
        command=rollout_state.command,
        shadow_coordination=rollout_state.shadow_coordination,
        gate_decision=rollout_state.gate_decision,
        correlation=rollout_state.correlation,
        promotion_signal=_promotion_signal_for_state(
            coordination=rollout_state.shadow_coordination,
            phase=phase,
            gate_decision=rollout_state.gate_decision,
            blockers=next_blockers,
        ),
        blockers=next_blockers,
        labels=next_labels,
    )
