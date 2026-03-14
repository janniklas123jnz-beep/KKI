"""Telemetry foundation primitives for audit, diagnostics, and drill-down views."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Mapping

from kki.message_protocols import EventEnvelope, MessageEnvelope
from kki.module_boundaries import ModuleBoundaryName, module_boundary
from kki.runtime_dna import RuntimeStage
from kki.security.config_loader import ControlArtifact


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _frozen_mapping(data: Mapping[str, object] | None) -> Mapping[str, object]:
    return MappingProxyType(dict(data or {}))


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_boundary(value: ModuleBoundaryName | str) -> ModuleBoundaryName:
    boundary = value if isinstance(value, ModuleBoundaryName) else ModuleBoundaryName(value)
    module_boundary(boundary)
    return boundary


@dataclass(frozen=True)
class TelemetrySignal:
    """Canonical telemetry observation emitted for a boundary or protocol flow."""

    signal_name: str
    boundary: ModuleBoundaryName
    correlation_id: str
    severity: str
    status: str
    metrics: Mapping[str, object] = field(default_factory=dict)
    labels: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "signal_name", _non_empty(self.signal_name, field_name="signal_name"))
        object.__setattr__(self, "correlation_id", _non_empty(self.correlation_id, field_name="correlation_id"))
        object.__setattr__(self, "status", _non_empty(self.status, field_name="status"))
        if self.severity not in {"info", "warning", "critical"}:
            raise ValueError("severity must be one of: info, warning, critical")
        module_boundary(self.boundary)
        object.__setattr__(self, "metrics", _frozen_mapping(self.metrics))
        object.__setattr__(self, "labels", _frozen_mapping(self.labels))

    def to_dict(self) -> dict[str, object]:
        return {
            "signal_name": self.signal_name,
            "boundary": self.boundary.value,
            "correlation_id": self.correlation_id,
            "severity": self.severity,
            "status": self.status,
            "metrics": dict(self.metrics),
            "labels": dict(self.labels),
        }


@dataclass(frozen=True)
class TelemetryAlert:
    """Canonical alert record for critical diagnostics and operator drill-downs."""

    alert_key: str
    boundary: ModuleBoundaryName
    severity: str
    summary: str
    observed_value: float
    threshold: float
    correlation_id: str
    status: str = "open"

    def __post_init__(self) -> None:
        object.__setattr__(self, "alert_key", _non_empty(self.alert_key, field_name="alert_key"))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        object.__setattr__(self, "correlation_id", _non_empty(self.correlation_id, field_name="correlation_id"))
        if self.severity not in {"warning", "critical"}:
            raise ValueError("severity must be one of: warning, critical")
        if self.status not in {"open", "acknowledged", "resolved"}:
            raise ValueError("status must be one of: open, acknowledged, resolved")
        if self.threshold < 0.0:
            raise ValueError("threshold must be >= 0.0")
        module_boundary(self.boundary)

    def to_dict(self) -> dict[str, object]:
        return {
            "alert_key": self.alert_key,
            "boundary": self.boundary.value,
            "severity": self.severity,
            "summary": self.summary,
            "observed_value": self.observed_value,
            "threshold": self.threshold,
            "correlation_id": self.correlation_id,
            "status": self.status,
        }


@dataclass(frozen=True)
class AuditTrailEntry:
    """Canonical audit trace for messages, evidence, and control-plane changes."""

    entry_type: str
    subject: str
    boundary: ModuleBoundaryName
    correlation_id: str
    recorded_at: str = field(default_factory=_timestamp)
    evidence_ref: str | None = None
    commitment_ref: str | None = None
    integrity_status: str | None = None
    payload: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "entry_type", _non_empty(self.entry_type, field_name="entry_type"))
        object.__setattr__(self, "subject", _non_empty(self.subject, field_name="subject"))
        object.__setattr__(self, "correlation_id", _non_empty(self.correlation_id, field_name="correlation_id"))
        object.__setattr__(self, "recorded_at", _non_empty(self.recorded_at, field_name="recorded_at"))
        if self.evidence_ref is not None:
            object.__setattr__(self, "evidence_ref", _non_empty(self.evidence_ref, field_name="evidence_ref"))
        if self.commitment_ref is not None:
            object.__setattr__(self, "commitment_ref", _non_empty(self.commitment_ref, field_name="commitment_ref"))
        if self.integrity_status is not None:
            object.__setattr__(self, "integrity_status", _non_empty(self.integrity_status, field_name="integrity_status"))
        module_boundary(self.boundary)
        object.__setattr__(self, "payload", _frozen_mapping(self.payload))

    def to_dict(self) -> dict[str, object]:
        return {
            "entry_type": self.entry_type,
            "subject": self.subject,
            "boundary": self.boundary.value,
            "correlation_id": self.correlation_id,
            "recorded_at": self.recorded_at,
            "evidence_ref": self.evidence_ref,
            "commitment_ref": self.commitment_ref,
            "integrity_status": self.integrity_status,
            "payload": dict(self.payload),
        }


@dataclass(frozen=True)
class TelemetrySnapshot:
    """Resolved telemetry view for dashboards, handbooks, and operational drill-downs."""

    runtime_stage: RuntimeStage
    signals: tuple[TelemetrySignal, ...]
    alerts: tuple[TelemetryAlert, ...] = ()
    audit_entries: tuple[AuditTrailEntry, ...] = ()
    active_controls: tuple[str, ...] = ()

    def highest_severity(self) -> str:
        levels = {"info": 0, "warning": 1, "critical": 2}
        highest = "info"
        for signal in self.signals:
            if levels[signal.severity] > levels[highest]:
                highest = signal.severity
        for alert in self.alerts:
            if levels[alert.severity] > levels[highest]:
                highest = alert.severity
        return highest

    def status_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for signal in self.signals:
            counts[signal.status] = counts.get(signal.status, 0) + 1
        return counts

    def to_dict(self) -> dict[str, object]:
        return {
            "runtime_stage": self.runtime_stage.value,
            "highest_severity": self.highest_severity(),
            "status_counts": self.status_counts(),
            "signals": [signal.to_dict() for signal in self.signals],
            "alerts": [alert.to_dict() for alert in self.alerts],
            "audit_entries": [entry.to_dict() for entry in self.audit_entries],
            "active_controls": list(self.active_controls),
        }


def telemetry_signal_from_event(
    event: EventEnvelope,
    *,
    status: str = "observed",
    metrics: Mapping[str, object] | None = None,
    labels: Mapping[str, object] | None = None,
) -> TelemetrySignal:
    """Project an event envelope into a canonical telemetry signal."""

    return TelemetrySignal(
        signal_name=event.message.name,
        boundary=event.message.source_boundary,
        correlation_id=event.message.context.correlation_id,
        severity=event.severity,
        status=status,
        metrics=metrics,
        labels={"event_class": event.event_class, **dict(labels or {})},
    )


def telemetry_alert(
    *,
    alert_key: str,
    boundary: ModuleBoundaryName | str,
    severity: str,
    summary: str,
    observed_value: float,
    threshold: float,
    correlation_id: str,
) -> TelemetryAlert:
    """Create a canonical telemetry alert."""

    return TelemetryAlert(
        alert_key=alert_key,
        boundary=_normalize_boundary(boundary),
        severity=severity,
        summary=summary,
        observed_value=float(observed_value),
        threshold=float(threshold),
        correlation_id=correlation_id,
    )


def audit_entry_for_message(message: MessageEnvelope) -> AuditTrailEntry:
    """Create an audit trail entry from a canonical message envelope."""

    payload = {
        "message_name": message.name,
        "message_kind": message.kind,
        "target_boundary": message.target_boundary.value,
        "delivery_mode": message.delivery_mode,
        "delivery_guarantee": message.delivery_guarantee,
    }
    return AuditTrailEntry(
        entry_type="message",
        subject=message.name,
        boundary=message.source_boundary,
        correlation_id=message.context.correlation_id,
        integrity_status=message.integrity_status,
        payload=payload,
    )


def audit_entry_for_artifact(artifact: ControlArtifact) -> AuditTrailEntry:
    """Create an audit trail entry from a control-plane artifact change."""

    payload = {
        "artifact_id": artifact.artifact_id,
        "artifact_kind": artifact.kind.value,
        "version": artifact.version,
        "scope": artifact.scope.value,
        "rollback_version": artifact.rollback_version,
    }
    return AuditTrailEntry(
        entry_type="control-artifact",
        subject=artifact.artifact_id,
        boundary=artifact.boundary or ModuleBoundaryName.SECURITY,
        correlation_id=f"artifact-{artifact.artifact_id}-{artifact.version}",
        evidence_ref=artifact.evidence_ref,
        commitment_ref=artifact.commitment_ref,
        payload=payload,
    )


def build_telemetry_snapshot(
    *,
    runtime_stage: RuntimeStage,
    signals: tuple[TelemetrySignal, ...] | list[TelemetrySignal],
    alerts: tuple[TelemetryAlert, ...] | list[TelemetryAlert] = (),
    audit_entries: tuple[AuditTrailEntry, ...] | list[AuditTrailEntry] = (),
    active_controls: tuple[str, ...] | list[str] = (),
) -> TelemetrySnapshot:
    """Build the canonical telemetry snapshot view for a runtime context."""

    return TelemetrySnapshot(
        runtime_stage=runtime_stage,
        signals=tuple(signals),
        alerts=tuple(alerts),
        audit_entries=tuple(audit_entries),
        active_controls=tuple(str(control) for control in active_controls),
    )
