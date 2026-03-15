"""Compact operational cockpit over review, risk, drift, and remediation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .drift_monitor import DriftMonitor, build_drift_monitor
from .readiness_review import ReadinessReview, ReadinessFindingSeverity, build_readiness_review
from .remediation_campaigns import RemediationCampaign, RemediationCampaignStatus, build_remediation_campaign
from .risk_register import RiskRegister, RiskMitigationStatus, build_risk_register
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


class CockpitStatus(str, Enum):
    """Canonical high-level operational states for the cockpit."""

    HEALTHY = "healthy"
    ATTENTION = "attention"
    CRITICAL = "critical"


@dataclass(frozen=True)
class CockpitEntry:
    """Compact operational summary for one case across all control layers."""

    case_id: str
    status: CockpitStatus
    release_ready: bool
    risk_status: str
    drift_status: str
    remediation_status: str
    overall_score: float
    blocked_release: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))

    def to_dict(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "status": self.status.value,
            "release_ready": self.release_ready,
            "risk_status": self.risk_status,
            "drift_status": self.drift_status,
            "remediation_status": self.remediation_status,
            "overall_score": self.overall_score,
            "blocked_release": self.blocked_release,
        }


@dataclass(frozen=True)
class OperationsCockpit:
    """Compact operational overview over review, risk, drift, and remediation."""

    cockpit_id: str
    review: ReadinessReview
    risk_register: RiskRegister
    drift_monitor: DriftMonitor
    remediation_campaign: RemediationCampaign
    entries: tuple[CockpitEntry, ...]
    cockpit_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "cockpit_id", _non_empty(self.cockpit_id, field_name="cockpit_id"))

    @property
    def healthy_case_ids(self) -> tuple[str, ...]:
        return tuple(entry.case_id for entry in self.entries if entry.status is CockpitStatus.HEALTHY)

    @property
    def attention_case_ids(self) -> tuple[str, ...]:
        return tuple(entry.case_id for entry in self.entries if entry.status is CockpitStatus.ATTENTION)

    @property
    def critical_case_ids(self) -> tuple[str, ...]:
        return tuple(entry.case_id for entry in self.entries if entry.status is CockpitStatus.CRITICAL)

    def to_dict(self) -> dict[str, object]:
        return {
            "cockpit_id": self.cockpit_id,
            "review": self.review.to_dict(),
            "risk_register": self.risk_register.to_dict(),
            "drift_monitor": self.drift_monitor.to_dict(),
            "remediation_campaign": self.remediation_campaign.to_dict(),
            "entries": [entry.to_dict() for entry in self.entries],
            "cockpit_signal": self.cockpit_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "healthy_case_ids": list(self.healthy_case_ids),
            "attention_case_ids": list(self.attention_case_ids),
            "critical_case_ids": list(self.critical_case_ids),
        }


def _entry_for_case(
    case_id: str,
    review: ReadinessReview,
    risk_register: RiskRegister,
    drift_monitor: DriftMonitor,
    remediation_campaign: RemediationCampaign,
) -> CockpitEntry:
    score_entry = next(entry for entry in review.scorecard.entries if entry.case_id == case_id)
    findings = tuple(finding for finding in review.findings if finding.case_id == case_id)
    risks = tuple(risk for risk in risk_register.risks if risk.case_id == case_id)
    observation = next((item for item in drift_monitor.observations if item.case_id == case_id), None)
    stages = tuple(stage for stage in remediation_campaign.stages if stage.case_id == case_id)

    status = CockpitStatus.HEALTHY
    if any(finding.severity is ReadinessFindingSeverity.CRITICAL for finding in findings):
        status = CockpitStatus.CRITICAL
    elif any(finding.severity is ReadinessFindingSeverity.WARNING for finding in findings):
        status = CockpitStatus.ATTENTION

    if any(risk.mitigation_status is RiskMitigationStatus.BLOCKING for risk in risks):
        status = CockpitStatus.CRITICAL
    elif status is CockpitStatus.HEALTHY and any(
        risk.mitigation_status is RiskMitigationStatus.ACTIVE for risk in risks
    ):
        status = CockpitStatus.ATTENTION

    if observation is not None:
        critical_drift = any(
            "overall_score" in violation or "recovery_score" in violation
            for violation in observation.guardrail_violations
        )
        governance_only_drift = (
            observation.severity.value == "critical"
            and not critical_drift
            and any("governance_score" in violation for violation in observation.guardrail_violations)
        )
        if observation.severity.value == "critical" and not governance_only_drift:
            status = CockpitStatus.CRITICAL
        elif status is CockpitStatus.HEALTHY and (
            observation.severity.value == "warning" or governance_only_drift
        ):
            status = CockpitStatus.ATTENTION

    if any(stage.status is RemediationCampaignStatus.BLOCKED for stage in stages):
        remediation_status = RemediationCampaignStatus.BLOCKED.value
        status = CockpitStatus.CRITICAL
    elif any(stage.status is RemediationCampaignStatus.RECOVERY_ONLY for stage in stages):
        remediation_status = RemediationCampaignStatus.RECOVERY_ONLY.value
        if status is CockpitStatus.HEALTHY:
            status = CockpitStatus.ATTENTION
    elif any(stage.status is RemediationCampaignStatus.GUARDED for stage in stages):
        remediation_status = RemediationCampaignStatus.GUARDED.value
        if status is CockpitStatus.HEALTHY:
            status = CockpitStatus.ATTENTION
    else:
        remediation_status = RemediationCampaignStatus.READY.value

    risk_status = "observed"
    if any(risk.mitigation_status is RiskMitigationStatus.BLOCKING for risk in risks):
        risk_status = "blocking"
    elif any(risk.mitigation_status is RiskMitigationStatus.ACTIVE for risk in risks):
        risk_status = "active"

    drift_status = "stable" if observation is None else observation.severity.value
    blocked_release = case_id in review.blocked_case_ids or any(risk.blocked_release for risk in risks)
    return CockpitEntry(
        case_id=case_id,
        status=status,
        release_ready=review.release_ready and not blocked_release and status is not CockpitStatus.CRITICAL,
        risk_status=risk_status,
        drift_status=drift_status,
        remediation_status=remediation_status,
        overall_score=score_entry.overall_score,
        blocked_release=blocked_release,
    )


def build_operations_cockpit(
    review: ReadinessReview | None = None,
    risk_register: RiskRegister | None = None,
    drift_monitor: DriftMonitor | None = None,
    remediation_campaign: RemediationCampaign | None = None,
    *,
    cockpit_id: str = "operations-cockpit",
) -> OperationsCockpit:
    """Build a compact operational cockpit over the current control loop."""

    resolved_review = build_readiness_review(review_id=f"{cockpit_id}-review") if review is None else review
    resolved_risk_register = (
        build_risk_register(register_id=f"{cockpit_id}-register")
        if risk_register is None
        else risk_register
    )
    resolved_drift_monitor = build_drift_monitor(monitor_id=f"{cockpit_id}-drift") if drift_monitor is None else drift_monitor
    resolved_remediation_campaign = (
        build_remediation_campaign(campaign_id=f"{cockpit_id}-campaign")
        if remediation_campaign is None
        else remediation_campaign
    )

    case_ids = tuple(
        dict.fromkeys(
            [
                *(entry.case_id for entry in resolved_review.scorecard.entries),
                *(risk.case_id for risk in resolved_risk_register.risks),
                *(observation.case_id for observation in resolved_drift_monitor.observations),
                *(stage.case_id for stage in resolved_remediation_campaign.stages),
            ]
        )
    )
    entries = tuple(
        _entry_for_case(case_id, resolved_review, resolved_risk_register, resolved_drift_monitor, resolved_remediation_campaign)
        for case_id in case_ids
    )
    if not entries:
        raise ValueError("operations cockpit requires at least one entry")

    severity = "info"
    status = CockpitStatus.HEALTHY.value
    if any(entry.status is CockpitStatus.CRITICAL for entry in entries):
        severity = "critical"
        status = CockpitStatus.CRITICAL.value
    elif any(entry.status is CockpitStatus.ATTENTION for entry in entries):
        severity = "warning"
        status = CockpitStatus.ATTENTION.value

    cockpit_signal = TelemetrySignal(
        signal_name="operations-cockpit",
        boundary=resolved_review.review_signal.boundary,
        correlation_id=cockpit_id,
        severity=severity,
        status=status,
        metrics={
            "entry_count": float(len(entries)),
            "healthy_count": float(len([entry for entry in entries if entry.status is CockpitStatus.HEALTHY])),
            "attention_count": float(len([entry for entry in entries if entry.status is CockpitStatus.ATTENTION])),
            "critical_count": float(len([entry for entry in entries if entry.status is CockpitStatus.CRITICAL])),
            "release_ready_count": float(len([entry for entry in entries if entry.release_ready])),
        },
        labels={"cockpit_id": cockpit_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_remediation_campaign.final_snapshot.runtime_stage,
        signals=(
            cockpit_signal,
            resolved_review.review_signal,
            resolved_risk_register.register_signal,
            resolved_drift_monitor.drift_signal,
            resolved_remediation_campaign.campaign_signal,
            *resolved_remediation_campaign.final_snapshot.signals,
        ),
        alerts=resolved_remediation_campaign.final_snapshot.alerts,
        audit_entries=resolved_remediation_campaign.final_snapshot.audit_entries,
        active_controls=tuple(
            dict.fromkeys(
                (
                    *resolved_review.final_snapshot.active_controls,
                    *resolved_risk_register.final_snapshot.active_controls,
                    *resolved_drift_monitor.final_snapshot.active_controls,
                    *resolved_remediation_campaign.final_snapshot.active_controls,
                )
            )
        ),
    )
    return OperationsCockpit(
        cockpit_id=cockpit_id,
        review=resolved_review,
        risk_register=resolved_risk_register,
        drift_monitor=resolved_drift_monitor,
        remediation_campaign=resolved_remediation_campaign,
        entries=entries,
        cockpit_signal=cockpit_signal,
        final_snapshot=final_snapshot,
    )
