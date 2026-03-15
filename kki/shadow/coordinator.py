"""Shadow coordination for preview, parallel validation, and replay paths."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from kki.governance import GateDecision, GateOutcome, evaluate_gate
from kki.message_protocols import MessageEnvelope, command_message
from kki.module_boundaries import ModuleBoundaryName
from kki.orchestration import (
    DispatchAssignment,
    DispatchLane,
    GateState,
    OrchestrationState,
    PressureLevel,
    WorkStatus,
    WorkUnit,
    build_dispatch_plan,
)
from kki.security import AuthorizationIdentity, LoadedControlPlane, RoleName
from kki.shadow.interfaces import (
    DryRunEvaluation,
    PreviewMode,
    ShadowPreview,
    evaluate_dry_run,
    shadow_preview_for_command,
)
from kki.telemetry import CorrelatedOperation, TelemetrySignal, correlate_operation


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float, *, field_name: str) -> float:
    normalized = float(value)
    if not 0.0 <= normalized <= 1.0:
        raise ValueError(f"{field_name} must be between 0.0 and 1.0")
    return normalized


class ShadowCoordinationMode(str, Enum):
    """Operational shadow paths for preview, parallel validation, and replay."""

    PREVIEW = "preview"
    PARALLEL = "parallel"
    REPLAY = "replay"


@dataclass(frozen=True)
class ShadowCoordination:
    """Coordinated shadow execution view for a single operational work unit."""

    coordination_id: str
    mode: ShadowCoordinationMode
    work_unit: WorkUnit
    command: MessageEnvelope
    dispatch_assignment: DispatchAssignment
    gate_decision: GateDecision
    preview: ShadowPreview
    evaluation: DryRunEvaluation
    correlation: CorrelatedOperation
    divergence_threshold: float
    release_signal: TelemetrySignal
    release_ready: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "coordination_id", _non_empty(self.coordination_id, field_name="coordination_id"))
        object.__setattr__(
            self,
            "divergence_threshold",
            _clamp01(self.divergence_threshold, field_name="divergence_threshold"),
        )
        if self.command.context.correlation_id != self.work_unit.correlation_id:
            raise ValueError("command correlation_id must match work_unit correlation_id")
        if self.preview.correlation_id != self.work_unit.correlation_id:
            raise ValueError("preview correlation_id must match work_unit correlation_id")
        if self.evaluation.preview_id != self.preview.preview_id:
            raise ValueError("evaluation must belong to preview")
        if self.correlation.correlation_id != self.work_unit.correlation_id:
            raise ValueError("correlation view must match work_unit correlation_id")

    def to_dict(self) -> dict[str, object]:
        return {
            "coordination_id": self.coordination_id,
            "mode": self.mode.value,
            "work_unit": self.work_unit.to_dict(),
            "command": self.command.to_dict(),
            "dispatch_assignment": self.dispatch_assignment.to_dict(),
            "gate_decision": self.gate_decision.to_dict(),
            "preview": self.preview.to_dict(),
            "evaluation": self.evaluation.to_dict(),
            "correlation": self.correlation.to_dict(),
            "divergence_threshold": self.divergence_threshold,
            "release_signal": self.release_signal.to_dict(),
            "release_ready": self.release_ready,
        }


def _coordination_mode_for_work(
    state: OrchestrationState,
    work_unit: WorkUnit,
    dispatch_assignment: DispatchAssignment,
) -> ShadowCoordinationMode:
    if work_unit.attempt > 0 or work_unit.status is WorkStatus.HANDED_OFF or work_unit.handoff_ref is not None:
        return ShadowCoordinationMode.REPLAY
    if state.gates.shadow is GateState.GUARDED or dispatch_assignment.lane in {DispatchLane.HOLD, DispatchLane.DEFER}:
        return ShadowCoordinationMode.PARALLEL
    if state.pressure.level in {PressureLevel.HIGH, PressureLevel.CRITICAL}:
        return ShadowCoordinationMode.PARALLEL
    return ShadowCoordinationMode.PREVIEW


def _preview_mode_for_coordination(mode: ShadowCoordinationMode) -> PreviewMode:
    if mode is ShadowCoordinationMode.REPLAY:
        return PreviewMode.DRY_RUN
    return PreviewMode.SHADOW


def _shadow_command_for_work(work_unit: WorkUnit, mode: ShadowCoordinationMode) -> MessageEnvelope:
    return command_message(
        name=f"shadow-{mode.value}-{work_unit.boundary.value}",
        source_boundary=ModuleBoundaryName.ORCHESTRATION,
        target_boundary=work_unit.boundary,
        correlation_id=work_unit.correlation_id,
        payload={
            "work_unit_id": work_unit.unit_id,
            "work_title": work_unit.title,
            "mode": mode.value,
            "attempt": work_unit.attempt,
            "handoff_ref": work_unit.handoff_ref,
        },
    )


def _release_signal_for_coordination(
    *,
    coordination_id: str,
    mode: ShadowCoordinationMode,
    work_unit: WorkUnit,
    dispatch_assignment: DispatchAssignment,
    gate_decision: GateDecision,
    evaluation: DryRunEvaluation,
    divergence_threshold: float,
) -> tuple[TelemetrySignal, bool]:
    release_ready = False
    severity = "info"
    status = "release-ready"
    if dispatch_assignment.lane is DispatchLane.BLOCK or gate_decision.outcome is GateOutcome.BLOCK:
        severity = "critical"
        status = "blocked"
    elif dispatch_assignment.lane in {DispatchLane.HOLD, DispatchLane.DEFER} or gate_decision.outcome in {
        GateOutcome.HOLD,
        GateOutcome.ESCALATE,
    }:
        severity = "warning"
        status = "hold"
    elif not evaluation.replay_ready:
        severity = "warning"
        status = "replay-required"
    elif mode is ShadowCoordinationMode.PARALLEL:
        severity = "info"
        status = "parallel-required"
    elif mode is ShadowCoordinationMode.REPLAY:
        severity = "info"
        status = "replay-cleared"
        release_ready = True
    else:
        release_ready = True

    return (
        TelemetrySignal(
            signal_name="shadow-release",
            boundary=ModuleBoundaryName.SHADOW,
            correlation_id=work_unit.correlation_id,
            severity=severity,
            status=status,
            metrics={
                "divergence_score": evaluation.divergence_score,
                "divergence_threshold": divergence_threshold,
                "reserved_budget": dispatch_assignment.reserved_budget,
                "expected_budget": evaluation.expected_budget,
                "observed_budget": evaluation.observed_budget,
            },
            labels={
                "coordination_id": coordination_id,
                "mode": mode.value,
                "work_unit_id": work_unit.unit_id,
                "dispatch_lane": dispatch_assignment.lane.value,
                "gate_outcome": gate_decision.outcome.value,
                "target_boundary": work_unit.boundary.value,
            },
        ),
        release_ready,
    )


def coordinate_shadow_work(
    state: OrchestrationState,
    work_unit: WorkUnit,
    *,
    control_plane: LoadedControlPlane,
    identity: AuthorizationIdentity,
    mode: ShadowCoordinationMode | str | None = None,
    available_roles: tuple[RoleName | str, ...] = (),
    max_parallel: int | None = None,
    allow_guarded_dispatch: bool = False,
    observed_budget: float | None = None,
    expected_budget: float | None = None,
    drift_threshold: float | None = None,
    evidence_ref: str | None = None,
) -> ShadowCoordination:
    """Coordinate a work unit through shadow preview, parallel validation, or replay."""

    dispatch_plan = build_dispatch_plan(
        state,
        (work_unit,),
        available_roles=available_roles,
        max_parallel=max_parallel,
        allow_guarded_dispatch=allow_guarded_dispatch,
    )
    dispatch_assignment = dispatch_plan.assignments[0]
    coordination_mode = (
        mode if isinstance(mode, ShadowCoordinationMode) else ShadowCoordinationMode(mode)
        if mode is not None
        else _coordination_mode_for_work(state, work_unit, dispatch_assignment)
    )
    command = _shadow_command_for_work(work_unit, coordination_mode)
    gate_decision = evaluate_gate(
        identity,
        boundary=ModuleBoundaryName.SHADOW,
        control_plane=control_plane,
        message=command,
        dispatch_assignment=dispatch_assignment,
        evidence_ref=evidence_ref,
    )
    effective_threshold = (
        float(control_plane.effective_payload.get("drift_threshold", 0.08))
        if drift_threshold is None
        else float(drift_threshold)
    )
    preview = shadow_preview_for_command(
        state.to_core_state(),
        command,
        control_plane,
        mode=_preview_mode_for_coordination(coordination_mode),
        invariants=("dispatch-before-release", "gate-before-rollout"),
        labels={
            "coordination_mode": coordination_mode.value,
            "work_unit_id": work_unit.unit_id,
            "dispatch_lane": dispatch_assignment.lane.value,
        },
    )
    target_budget = work_unit.cost_profile.budget_share if expected_budget is None else float(expected_budget)
    measured_budget = dispatch_assignment.reserved_budget if observed_budget is None else float(observed_budget)
    evaluation = evaluate_dry_run(
        preview,
        observed_budget=measured_budget,
        expected_budget=target_budget,
        drift_threshold=effective_threshold,
        summary=f"Shadow {coordination_mode.value} evaluation for {work_unit.unit_id}",
    )
    correlation = correlate_operation(
        control_plane=control_plane,
        message=command,
        dispatch_assignment=dispatch_assignment,
        gate_decision=gate_decision,
    )
    coordination_id = f"shadow-{coordination_mode.value}-{work_unit.unit_id}"
    release_signal, release_ready = _release_signal_for_coordination(
        coordination_id=coordination_id,
        mode=coordination_mode,
        work_unit=work_unit,
        dispatch_assignment=dispatch_assignment,
        gate_decision=gate_decision,
        evaluation=evaluation,
        divergence_threshold=effective_threshold,
    )
    return ShadowCoordination(
        coordination_id=coordination_id,
        mode=coordination_mode,
        work_unit=work_unit,
        command=command,
        dispatch_assignment=dispatch_assignment,
        gate_decision=gate_decision,
        preview=preview,
        evaluation=evaluation,
        correlation=correlation,
        divergence_threshold=effective_threshold,
        release_signal=release_signal,
        release_ready=release_ready,
    )
