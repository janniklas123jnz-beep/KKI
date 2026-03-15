"""Escalation coordination over incident reports."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .governance import HumanDecision
from .incident_detector import IncidentCause, IncidentReport, IncidentSeverity, OperationsIncident
from .module_boundaries import ModuleBoundaryName
from .recovery import RecoveryDisposition
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


class EscalationPath(str, Enum):
    """Canonical escalation paths for operational incidents."""

    DISPATCH_REPLAN = "dispatch-replan"
    GOVERNANCE_REVIEW = "governance-review"
    RECOVERY_RESTART = "recovery-restart"
    ROLLBACK_CONTAINMENT = "rollback-containment"
    TELEMETRY_TRIAGE = "telemetry-triage"


@dataclass(frozen=True)
class EscalationDirective:
    """Concrete escalation directive derived from an incident."""

    directive_id: str
    wave_id: str
    incident_id: str
    mission_ref: str
    path: EscalationPath
    severity: IncidentSeverity
    summary: str
    release_blocked: bool
    governance_decision: HumanDecision | None = None
    recovery_disposition: RecoveryDisposition | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "directive_id", _non_empty(self.directive_id, field_name="directive_id"))
        object.__setattr__(self, "wave_id", _non_empty(self.wave_id, field_name="wave_id"))
        object.__setattr__(self, "incident_id", _non_empty(self.incident_id, field_name="incident_id"))
        object.__setattr__(self, "mission_ref", _non_empty(self.mission_ref, field_name="mission_ref"))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))

    def to_dict(self) -> dict[str, object]:
        return {
            "directive_id": self.directive_id,
            "wave_id": self.wave_id,
            "incident_id": self.incident_id,
            "mission_ref": self.mission_ref,
            "path": self.path.value,
            "severity": self.severity.value,
            "summary": self.summary,
            "release_blocked": self.release_blocked,
            "governance_decision": None if self.governance_decision is None else self.governance_decision.value,
            "recovery_disposition": None if self.recovery_disposition is None else self.recovery_disposition.value,
        }


@dataclass(frozen=True)
class EscalationPlan:
    """Escalation plan compiled from an incident report."""

    wave_id: str
    incident_report: IncidentReport
    directives: tuple[EscalationDirective, ...]
    escalation_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "wave_id", _non_empty(self.wave_id, field_name="wave_id"))

    @property
    def blocked_release_refs(self) -> tuple[str, ...]:
        ordered: list[str] = []
        for directive in self.directives:
            if not directive.release_blocked:
                continue
            if directive.mission_ref not in ordered:
                ordered.append(directive.mission_ref)
        return tuple(ordered)

    @property
    def governance_review_refs(self) -> tuple[str, ...]:
        return tuple(
            directive.mission_ref
            for directive in self.directives
            if directive.path is EscalationPath.GOVERNANCE_REVIEW
        )

    @property
    def recovery_refs(self) -> tuple[str, ...]:
        return tuple(
            directive.mission_ref
            for directive in self.directives
            if directive.recovery_disposition is not None
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "wave_id": self.wave_id,
            "incident_report": self.incident_report.to_dict(),
            "directives": [directive.to_dict() for directive in self.directives],
            "escalation_signal": self.escalation_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "blocked_release_refs": list(self.blocked_release_refs),
            "governance_review_refs": list(self.governance_review_refs),
            "recovery_refs": list(self.recovery_refs),
        }


def _directive_for_incident(incident: OperationsIncident) -> EscalationDirective:
    mission_ref = incident.mission_refs[0]
    path = EscalationPath.TELEMETRY_TRIAGE
    governance_decision = None
    recovery_disposition = None
    release_blocked = incident.escalation_required
    summary = incident.summary

    if incident.cause is IncidentCause.DISPATCH:
        path = EscalationPath.DISPATCH_REPLAN
        governance_decision = HumanDecision.HOLD
        summary = f"replan dispatch capacity for mission {mission_ref}"
    elif incident.cause is IncidentCause.GOVERNANCE:
        path = EscalationPath.GOVERNANCE_REVIEW
        governance_decision = HumanDecision.ESCALATE
        summary = f"route mission {mission_ref} into governance review"
    elif incident.cause is IncidentCause.RECOVERY:
        if incident.severity is IncidentSeverity.CRITICAL:
            path = EscalationPath.ROLLBACK_CONTAINMENT
            recovery_disposition = RecoveryDisposition.CONTAIN
            governance_decision = HumanDecision.HOLD
            summary = f"contain and rollback mission {mission_ref}"
        else:
            path = EscalationPath.RECOVERY_RESTART
            recovery_disposition = RecoveryDisposition.RESTART
            governance_decision = HumanDecision.ESCALATE
            summary = f"restart recovery path for mission {mission_ref}"
    elif incident.cause is IncidentCause.ROLLOUT:
        path = EscalationPath.ROLLBACK_CONTAINMENT
        recovery_disposition = RecoveryDisposition.CONTAIN
        governance_decision = HumanDecision.HOLD
        summary = f"rollback rollout state for mission {mission_ref}"
    elif incident.cause is IncidentCause.TELEMETRY:
        path = EscalationPath.TELEMETRY_TRIAGE
        governance_decision = HumanDecision.ESCALATE
        summary = f"triage telemetry anomaly for mission {mission_ref}"

    return EscalationDirective(
        directive_id=f"directive-{incident.incident_id}",
        wave_id=incident.wave_id,
        incident_id=incident.incident_id,
        mission_ref=mission_ref,
        path=path,
        severity=incident.severity,
        summary=summary,
        release_blocked=release_blocked,
        governance_decision=governance_decision,
        recovery_disposition=recovery_disposition,
    )


def coordinate_escalations(incident_report: IncidentReport) -> EscalationPlan:
    """Coordinate concrete escalation directives from an incident report."""

    directives = tuple(_directive_for_incident(incident) for incident in incident_report.incidents)
    severity = "info"
    status = "clear"
    if any(directive.severity is IncidentSeverity.CRITICAL for directive in directives):
        severity = "critical"
        status = "critical-response"
    elif directives:
        severity = "warning"
        status = "response-required"
    escalation_signal = TelemetrySignal(
        signal_name="escalation-plan",
        boundary=ModuleBoundaryName.GOVERNANCE,
        correlation_id=incident_report.wave_id,
        severity=severity,
        status=status,
        metrics={
            "directive_count": float(len(directives)),
            "blocked_release_count": float(len([directive for directive in directives if directive.release_blocked])),
            "recovery_count": float(len([directive for directive in directives if directive.recovery_disposition is not None])),
            "governance_count": float(len([directive for directive in directives if directive.governance_decision is not None])),
        },
        labels={
            "wave_id": incident_report.wave_id,
            "incident_status": incident_report.incident_signal.status,
        },
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=incident_report.final_snapshot.runtime_stage,
        signals=(escalation_signal, incident_report.incident_signal, *incident_report.final_snapshot.signals),
        alerts=incident_report.final_snapshot.alerts,
        audit_entries=incident_report.final_snapshot.audit_entries,
        active_controls=incident_report.final_snapshot.active_controls,
    )
    return EscalationPlan(
        wave_id=incident_report.wave_id,
        incident_report=incident_report,
        directives=directives,
        escalation_signal=escalation_signal,
        final_snapshot=final_snapshot,
    )
