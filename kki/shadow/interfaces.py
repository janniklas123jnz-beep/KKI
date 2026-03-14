"""Shadow and dry-run interfaces for previewing control-plane effects."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from kki.data_models import CoreState
from kki.message_protocols import EventEnvelope, MessageEnvelope, event_message
from kki.module_boundaries import ModuleBoundaryName, module_boundary
from kki.runtime_dna import RuntimeStage
from kki.security.config_loader import LoadedControlPlane
from kki.telemetry.foundation import (
    AuditTrailEntry,
    TelemetryAlert,
    TelemetrySignal,
    TelemetrySnapshot,
    audit_entry_for_artifact,
    audit_entry_for_message,
    build_telemetry_snapshot,
)


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _frozen_mapping(data: Mapping[str, object] | None) -> Mapping[str, object]:
    return MappingProxyType(dict(data or {}))


class PreviewMode(str, Enum):
    """Canonical preview modes for the shadow boundary."""

    SHADOW = "shadow"
    DRY_RUN = "dry-run"


@dataclass(frozen=True)
class ShadowPreview:
    """Canonical preview contract for a command executed in a shadow path."""

    preview_id: str
    mode: PreviewMode
    runtime_stage: RuntimeStage
    source_boundary: ModuleBoundaryName
    target_boundary: ModuleBoundaryName
    correlation_id: str
    input_state: CoreState
    command: MessageEnvelope
    control_versions: tuple[str, ...]
    invariants: tuple[str, ...] = ()
    labels: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "preview_id", _non_empty(self.preview_id, field_name="preview_id"))
        object.__setattr__(self, "correlation_id", _non_empty(self.correlation_id, field_name="correlation_id"))
        module_boundary(self.source_boundary)
        module_boundary(self.target_boundary)
        if self.command.target_boundary != self.target_boundary:
            raise ValueError("command target boundary must match preview target boundary")
        if self.command.context.correlation_id != self.correlation_id:
            raise ValueError("preview correlation_id must match command correlation_id")
        object.__setattr__(self, "invariants", tuple(invariant.strip() for invariant in self.invariants if invariant.strip()))
        object.__setattr__(self, "labels", _frozen_mapping(self.labels))

    def to_dict(self) -> dict[str, object]:
        return {
            "preview_id": self.preview_id,
            "mode": self.mode.value,
            "runtime_stage": self.runtime_stage.value,
            "source_boundary": self.source_boundary.value,
            "target_boundary": self.target_boundary.value,
            "correlation_id": self.correlation_id,
            "input_state": self.input_state.to_dict(),
            "command": self.command.to_dict(),
            "control_versions": list(self.control_versions),
            "invariants": list(self.invariants),
            "labels": dict(self.labels),
        }


@dataclass(frozen=True)
class DryRunEvaluation:
    """Result of evaluating a shadow or dry-run preview against expectations."""

    preview_id: str
    status: str
    divergence_score: float
    replay_ready: bool
    summary: str
    observed_budget: float
    expected_budget: float
    signal: TelemetrySignal
    alert: TelemetryAlert | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "preview_id", _non_empty(self.preview_id, field_name="preview_id"))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.status not in {"matched", "drift", "blocked"}:
            raise ValueError("status must be one of: matched, drift, blocked")
        if not 0.0 <= self.divergence_score <= 1.0:
            raise ValueError("divergence_score must be between 0.0 and 1.0")

    def to_dict(self) -> dict[str, object]:
        return {
            "preview_id": self.preview_id,
            "status": self.status,
            "divergence_score": self.divergence_score,
            "replay_ready": self.replay_ready,
            "summary": self.summary,
            "observed_budget": self.observed_budget,
            "expected_budget": self.expected_budget,
            "signal": self.signal.to_dict(),
            "alert": self.alert.to_dict() if self.alert else None,
        }


def shadow_preview_for_command(
    state: CoreState,
    command: MessageEnvelope,
    control_plane: LoadedControlPlane,
    *,
    mode: PreviewMode = PreviewMode.SHADOW,
    invariants: tuple[str, ...] = (),
    labels: Mapping[str, object] | None = None,
) -> ShadowPreview:
    """Build the canonical shadow preview contract for a command."""

    return ShadowPreview(
        preview_id=f"{mode.value}-{command.context.correlation_id}",
        mode=mode,
        runtime_stage=control_plane.runtime_stage,
        source_boundary=state.module_boundary,
        target_boundary=command.target_boundary,
        correlation_id=command.context.correlation_id,
        input_state=state,
        command=command,
        control_versions=tuple(artifact.version for artifact in control_plane.applied_artifacts),
        invariants=invariants,
        labels=labels,
    )


def evaluate_dry_run(
    preview: ShadowPreview,
    *,
    observed_budget: float,
    expected_budget: float | None = None,
    drift_threshold: float = 0.1,
    summary: str | None = None,
) -> DryRunEvaluation:
    """Evaluate the shadow preview against an expected budget outcome."""

    expected = preview.input_state.budget if expected_budget is None else float(expected_budget)
    observed = float(observed_budget)
    divergence = abs(observed - expected)
    severity = "warning" if divergence > drift_threshold else "info"
    status = "drift" if divergence > drift_threshold else "matched"
    signal = TelemetrySignal(
        signal_name=f"{preview.mode.value}-comparison",
        boundary=ModuleBoundaryName.SHADOW,
        correlation_id=preview.correlation_id,
        severity=severity,
        status=status,
        metrics={
            "observed_budget": observed,
            "expected_budget": expected,
            "divergence_score": divergence,
        },
        labels={
            "preview_id": preview.preview_id,
            "target_boundary": preview.target_boundary.value,
        },
    )
    alert = None
    if divergence > drift_threshold:
        alert = TelemetryAlert(
            alert_key=f"{preview.preview_id}-drift",
            boundary=ModuleBoundaryName.SHADOW,
            severity="warning",
            summary="Shadow drift exceeds permitted preview threshold",
            observed_value=divergence,
            threshold=drift_threshold,
            correlation_id=preview.correlation_id,
        )
    return DryRunEvaluation(
        preview_id=preview.preview_id,
        status=status,
        divergence_score=divergence,
        replay_ready=divergence <= drift_threshold,
        summary=summary or ("Shadow preview matched expected envelope" if status == "matched" else "Shadow preview drift exceeded threshold"),
        observed_budget=observed,
        expected_budget=expected,
        signal=signal,
        alert=alert,
    )


def shadow_snapshot(
    preview: ShadowPreview,
    evaluation: DryRunEvaluation,
    control_plane: LoadedControlPlane,
) -> TelemetrySnapshot:
    """Build the telemetry drill-down snapshot for a shadow preview run."""

    audit_entries: list[AuditTrailEntry] = [audit_entry_for_message(preview.command)]
    audit_entries.extend(audit_entry_for_artifact(artifact) for artifact in control_plane.applied_artifacts)
    return build_telemetry_snapshot(
        runtime_stage=preview.runtime_stage,
        signals=(evaluation.signal,),
        alerts=(evaluation.alert,) if evaluation.alert else (),
        audit_entries=tuple(audit_entries),
        active_controls=tuple(artifact.artifact_id for artifact in control_plane.applied_artifacts),
    )


def shadow_event(preview: ShadowPreview, evaluation: DryRunEvaluation) -> EventEnvelope:
    """Emit the canonical shadow event for telemetry and governance observers."""

    return event_message(
        name=f"{preview.mode.value}-evaluation",
        event_class="shadow",
        severity=evaluation.signal.severity,
        source_boundary=ModuleBoundaryName.SHADOW,
        target_boundary=ModuleBoundaryName.TELEMETRY,
        correlation_id=preview.correlation_id,
        payload={
            "preview_id": preview.preview_id,
            "status": evaluation.status,
            "divergence_score": evaluation.divergence_score,
            "replay_ready": evaluation.replay_ready,
            "target_boundary": preview.target_boundary.value,
        },
    )
