"""Incident detection over run ledgers and aggregated telemetry."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from .module_boundaries import ModuleBoundaryName
from .run_ledger import OperationsRunLedger, RunLedgerEntry
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _frozen_mapping(data: Mapping[str, object] | None) -> Mapping[str, object]:
    return MappingProxyType(dict(data or {}))


class IncidentSeverity(str, Enum):
    """Canonical incident severity levels."""

    WARNING = "warning"
    CRITICAL = "critical"


class IncidentCause(str, Enum):
    """Canonical incident cause domains derived from ledger signals."""

    DISPATCH = "dispatch"
    GOVERNANCE = "governance"
    ROLLOUT = "rollout"
    RECOVERY = "recovery"
    TELEMETRY = "telemetry"


@dataclass(frozen=True)
class OperationsIncident:
    """Normalized incident record derived from one or more ledger entries."""

    incident_id: str
    wave_id: str
    severity: IncidentSeverity
    cause: IncidentCause
    summary: str
    mission_refs: tuple[str, ...]
    trigger_statuses: tuple[str, ...]
    escalation_required: bool
    labels: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "incident_id", _non_empty(self.incident_id, field_name="incident_id"))
        object.__setattr__(self, "wave_id", _non_empty(self.wave_id, field_name="wave_id"))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        cleaned_refs = tuple(ref.strip() for ref in self.mission_refs if ref.strip())
        cleaned_triggers = tuple(status.strip() for status in self.trigger_statuses if status.strip())
        if not cleaned_refs:
            raise ValueError("mission_refs must not be empty")
        if not cleaned_triggers:
            raise ValueError("trigger_statuses must not be empty")
        object.__setattr__(self, "mission_refs", cleaned_refs)
        object.__setattr__(self, "trigger_statuses", cleaned_triggers)
        object.__setattr__(self, "labels", _frozen_mapping(self.labels))

    def to_dict(self) -> dict[str, object]:
        return {
            "incident_id": self.incident_id,
            "wave_id": self.wave_id,
            "severity": self.severity.value,
            "cause": self.cause.value,
            "summary": self.summary,
            "mission_refs": list(self.mission_refs),
            "trigger_statuses": list(self.trigger_statuses),
            "escalation_required": self.escalation_required,
            "labels": dict(self.labels),
        }


@dataclass(frozen=True)
class IncidentReport:
    """Incident report compiled from a ledger and its telemetry."""

    wave_id: str
    ledger: OperationsRunLedger
    incidents: tuple[OperationsIncident, ...]
    incident_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "wave_id", _non_empty(self.wave_id, field_name="wave_id"))

    @property
    def critical_incidents(self) -> tuple[OperationsIncident, ...]:
        return tuple(incident for incident in self.incidents if incident.severity is IncidentSeverity.CRITICAL)

    @property
    def escalation_mission_refs(self) -> tuple[str, ...]:
        ordered: list[str] = []
        for incident in self.incidents:
            if not incident.escalation_required:
                continue
            for mission_ref in incident.mission_refs:
                if mission_ref not in ordered:
                    ordered.append(mission_ref)
        return tuple(ordered)

    def to_dict(self) -> dict[str, object]:
        return {
            "wave_id": self.wave_id,
            "ledger": self.ledger.to_dict(),
            "incidents": [incident.to_dict() for incident in self.incidents],
            "incident_signal": self.incident_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "critical_incidents": [incident.to_dict() for incident in self.critical_incidents],
            "escalation_mission_refs": list(self.escalation_mission_refs),
        }


def _incident_for_entry(entry: RunLedgerEntry) -> OperationsIncident | None:
    if entry.dispatch_lane == "block":
        return OperationsIncident(
            incident_id=f"incident-{entry.wave_id}-{entry.mission_ref}-dispatch",
            wave_id=entry.wave_id,
            severity=IncidentSeverity.CRITICAL,
            cause=IncidentCause.DISPATCH,
            summary=f"dispatch blocked mission {entry.mission_ref}",
            mission_refs=(entry.mission_ref,),
            trigger_statuses=(entry.dispatch_lane,),
            escalation_required=True,
            labels=dict(entry.labels),
        )
    if entry.highest_severity == "critical":
        cause = IncidentCause.TELEMETRY
        if entry.recovery_status == "rollback-active":
            cause = IncidentCause.RECOVERY
        elif entry.rollout_status == "rollback-ready":
            cause = IncidentCause.ROLLOUT
        elif entry.governance_status == "blocked":
            cause = IncidentCause.GOVERNANCE
        return OperationsIncident(
            incident_id=f"incident-{entry.wave_id}-{entry.mission_ref}-critical",
            wave_id=entry.wave_id,
            severity=IncidentSeverity.CRITICAL,
            cause=cause,
            summary=f"critical incident detected for mission {entry.mission_ref}",
            mission_refs=(entry.mission_ref,),
            trigger_statuses=(entry.governance_status, entry.rollout_status, entry.recovery_status),
            escalation_required=True,
            labels=dict(entry.labels),
        )
    if entry.dispatch_lane in {"hold", "defer"}:
        return OperationsIncident(
            incident_id=f"incident-{entry.wave_id}-{entry.mission_ref}-dispatch-hold",
            wave_id=entry.wave_id,
            severity=IncidentSeverity.WARNING,
            cause=IncidentCause.DISPATCH,
            summary=f"dispatch delayed mission {entry.mission_ref}",
            mission_refs=(entry.mission_ref,),
            trigger_statuses=(entry.dispatch_lane,),
            escalation_required=True,
            labels=dict(entry.labels),
        )
    if entry.governance_status in {"escalated", "held", "blocked"}:
        return OperationsIncident(
            incident_id=f"incident-{entry.wave_id}-{entry.mission_ref}-governance",
            wave_id=entry.wave_id,
            severity=IncidentSeverity.CRITICAL if entry.governance_status == "blocked" else IncidentSeverity.WARNING,
            cause=IncidentCause.GOVERNANCE,
            summary=f"governance intervention required for mission {entry.mission_ref}",
            mission_refs=(entry.mission_ref,),
            trigger_statuses=(entry.governance_status,),
            escalation_required=True,
            labels=dict(entry.labels),
        )
    if entry.recovery_status == "restart-active":
        return OperationsIncident(
            incident_id=f"incident-{entry.wave_id}-{entry.mission_ref}-recovery",
            wave_id=entry.wave_id,
            severity=IncidentSeverity.WARNING,
            cause=IncidentCause.RECOVERY,
            summary=f"recovery restart path active for mission {entry.mission_ref}",
            mission_refs=(entry.mission_ref,),
            trigger_statuses=(entry.recovery_status,),
            escalation_required=True,
            labels=dict(entry.labels),
        )
    return None


def detect_incidents(ledger: OperationsRunLedger) -> IncidentReport:
    """Compile explicit operational incidents from a run ledger."""

    incidents = tuple(
        incident
        for entry in ledger.entries
        for incident in (_incident_for_entry(entry),)
        if incident is not None
    )
    severity = "info"
    status = "clear"
    if any(incident.severity is IncidentSeverity.CRITICAL for incident in incidents):
        severity = "critical"
        status = "critical-incidents"
    elif incidents:
        severity = "warning"
        status = "attention-required"
    incident_signal = TelemetrySignal(
        signal_name="incident-report",
        boundary=ModuleBoundaryName.TELEMETRY,
        correlation_id=ledger.wave_id,
        severity=severity,
        status=status,
        metrics={
            "incident_count": float(len(incidents)),
            "critical_count": float(len([incident for incident in incidents if incident.severity is IncidentSeverity.CRITICAL])),
            "warning_count": float(len([incident for incident in incidents if incident.severity is IncidentSeverity.WARNING])),
        },
        labels={
            "wave_id": ledger.wave_id,
            "ledger_status": ledger.wave_signal.status,
        },
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=ledger.final_snapshot.runtime_stage,
        signals=(incident_signal, ledger.wave_signal, *ledger.final_snapshot.signals),
        alerts=ledger.final_snapshot.alerts,
        audit_entries=ledger.final_snapshot.audit_entries,
        active_controls=ledger.final_snapshot.active_controls,
    )
    return IncidentReport(
        wave_id=ledger.wave_id,
        ledger=ledger,
        incidents=incidents,
        incident_signal=incident_signal,
        final_snapshot=final_snapshot,
    )
