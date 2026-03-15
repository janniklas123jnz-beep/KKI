"""Portfolio optimization over cockpit and remediation campaign data."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .module_boundaries import ModuleBoundaryName
from .operations_cockpit import CockpitEntry, CockpitStatus, OperationsCockpit, build_operations_cockpit
from .remediation_campaigns import RemediationCampaign, RemediationCampaignStatus, build_remediation_campaign
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class PortfolioPriority(str, Enum):
    """Priority bands for next-step portfolio recommendations."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PortfolioAction(str, Enum):
    """Canonical recommendation types derived from the cockpit."""

    CONTAIN = "contain"
    RECOVER = "recover"
    APPROVE = "approve"
    ADVANCE = "advance"
    MONITOR = "monitor"


@dataclass(frozen=True)
class PortfolioRecommendation:
    """Concrete next-step recommendation for one cockpit case."""

    recommendation_id: str
    case_id: str
    priority: PortfolioPriority
    action: PortfolioAction
    owner: ModuleBoundaryName
    expected_benefit: float
    risk_cost: float
    capacity_cost: float
    target_status: str
    rationale: str
    release_candidate: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "recommendation_id", _non_empty(self.recommendation_id, field_name="recommendation_id"))
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))
        object.__setattr__(self, "target_status", _non_empty(self.target_status, field_name="target_status"))
        object.__setattr__(self, "rationale", _non_empty(self.rationale, field_name="rationale"))
        object.__setattr__(self, "expected_benefit", _clamp01(self.expected_benefit))
        object.__setattr__(self, "risk_cost", _clamp01(self.risk_cost))
        object.__setattr__(self, "capacity_cost", _clamp01(self.capacity_cost))

    @property
    def net_value(self) -> float:
        return _clamp01(self.expected_benefit - (self.risk_cost * 0.55) - (self.capacity_cost * 0.35))

    def to_dict(self) -> dict[str, object]:
        return {
            "recommendation_id": self.recommendation_id,
            "case_id": self.case_id,
            "priority": self.priority.value,
            "action": self.action.value,
            "owner": self.owner.value,
            "expected_benefit": self.expected_benefit,
            "risk_cost": self.risk_cost,
            "capacity_cost": self.capacity_cost,
            "target_status": self.target_status,
            "rationale": self.rationale,
            "release_candidate": self.release_candidate,
            "net_value": self.net_value,
        }


@dataclass(frozen=True)
class PortfolioOptimizer:
    """Ordered portfolio recommendations derived from the operational cockpit."""

    optimizer_id: str
    cockpit: OperationsCockpit
    remediation_campaign: RemediationCampaign
    recommendations: tuple[PortfolioRecommendation, ...]
    optimizer_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "optimizer_id", _non_empty(self.optimizer_id, field_name="optimizer_id"))

    @property
    def release_candidate_ids(self) -> tuple[str, ...]:
        return tuple(rec.case_id for rec in self.recommendations if rec.release_candidate)

    @property
    def critical_case_ids(self) -> tuple[str, ...]:
        return tuple(rec.case_id for rec in self.recommendations if rec.priority is PortfolioPriority.CRITICAL)

    def to_dict(self) -> dict[str, object]:
        return {
            "optimizer_id": self.optimizer_id,
            "cockpit": self.cockpit.to_dict(),
            "remediation_campaign": self.remediation_campaign.to_dict(),
            "recommendations": [rec.to_dict() for rec in self.recommendations],
            "optimizer_signal": self.optimizer_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "release_candidate_ids": list(self.release_candidate_ids),
            "critical_case_ids": list(self.critical_case_ids),
        }


def _campaign_status_for_case(campaign: RemediationCampaign, case_id: str) -> RemediationCampaignStatus:
    statuses = tuple(stage.status for stage in campaign.stages if stage.case_id == case_id)
    if any(status is RemediationCampaignStatus.BLOCKED for status in statuses):
        return RemediationCampaignStatus.BLOCKED
    if any(status is RemediationCampaignStatus.RECOVERY_ONLY for status in statuses):
        return RemediationCampaignStatus.RECOVERY_ONLY
    if any(status is RemediationCampaignStatus.GUARDED for status in statuses):
        return RemediationCampaignStatus.GUARDED
    return RemediationCampaignStatus.READY


def _recommendation_for_entry(
    optimizer_id: str,
    entry: CockpitEntry,
    campaign: RemediationCampaign,
) -> PortfolioRecommendation:
    campaign_status = _campaign_status_for_case(campaign, entry.case_id)
    priority = PortfolioPriority.LOW
    action = PortfolioAction.MONITOR
    owner = ModuleBoundaryName.TELEMETRY
    expected_benefit = 0.48
    risk_cost = 0.12
    capacity_cost = 0.18
    target_status = "healthy-baseline-preserved"
    rationale = f"{entry.case_id} remains healthy and should stay under observation."
    release_candidate = (
        entry.status is CockpitStatus.HEALTHY
        and not entry.blocked_release
        and campaign_status is RemediationCampaignStatus.READY
    )

    if entry.status is CockpitStatus.CRITICAL:
        priority = PortfolioPriority.CRITICAL
        action = PortfolioAction.CONTAIN
        owner = ModuleBoundaryName.RECOVERY
        expected_benefit = 0.96
        risk_cost = 0.82
        capacity_cost = 0.74
        target_status = "containment-cleared"
        rationale = f"{entry.case_id} is blocking readiness and should be stabilized before any broader advance."
        release_candidate = False
    elif entry.remediation_status == RemediationCampaignStatus.RECOVERY_ONLY.value:
        priority = PortfolioPriority.HIGH
        action = PortfolioAction.RECOVER
        owner = ModuleBoundaryName.RECOVERY
        expected_benefit = 0.84
        risk_cost = 0.56
        capacity_cost = 0.58
        target_status = "promotion-restored"
        rationale = f"{entry.case_id} needs recovery safeguards cleared before it can re-enter the promotion path."
        release_candidate = False
    elif entry.remediation_status == RemediationCampaignStatus.GUARDED.value:
        priority = PortfolioPriority.HIGH
        action = PortfolioAction.APPROVE
        owner = ModuleBoundaryName.GOVERNANCE
        expected_benefit = 0.78
        risk_cost = 0.42
        capacity_cost = 0.36
        target_status = "governance-reviewed"
        rationale = f"{entry.case_id} is an attention case whose next best move is governance closure and approval."
        release_candidate = False
    elif release_candidate:
        priority = PortfolioPriority.MEDIUM
        action = PortfolioAction.ADVANCE
        owner = ModuleBoundaryName.ROLLOUT
        expected_benefit = 0.72
        risk_cost = 0.18
        capacity_cost = 0.22
        target_status = "promotion-advanced"
        rationale = f"{entry.case_id} is healthy and ready for the next release or optimization step."
    elif entry.status is CockpitStatus.ATTENTION:
        priority = PortfolioPriority.MEDIUM
        action = PortfolioAction.MONITOR
        owner = ModuleBoundaryName.TELEMETRY
        expected_benefit = 0.58
        risk_cost = 0.28
        capacity_cost = 0.2
        target_status = "attention-reduced"
        rationale = f"{entry.case_id} should stay under active observation until the attention indicators have settled."

    return PortfolioRecommendation(
        recommendation_id=f"{optimizer_id}-{entry.case_id}-{action.value}",
        case_id=entry.case_id,
        priority=priority,
        action=action,
        owner=owner,
        expected_benefit=expected_benefit,
        risk_cost=risk_cost,
        capacity_cost=capacity_cost,
        target_status=target_status,
        rationale=rationale,
        release_candidate=release_candidate,
    )


def build_portfolio_optimizer(
    cockpit: OperationsCockpit | None = None,
    remediation_campaign: RemediationCampaign | None = None,
    *,
    optimizer_id: str = "portfolio-optimizer",
) -> PortfolioOptimizer:
    """Build next-step portfolio recommendations from cockpit and campaign state."""

    resolved_cockpit = build_operations_cockpit(cockpit_id=f"{optimizer_id}-cockpit") if cockpit is None else cockpit
    resolved_campaign = resolved_cockpit.remediation_campaign if remediation_campaign is None else remediation_campaign
    recommendations = tuple(_recommendation_for_entry(optimizer_id, entry, resolved_campaign) for entry in resolved_cockpit.entries)
    if not recommendations:
        raise ValueError("portfolio optimizer requires at least one recommendation")

    ordered = tuple(
        sorted(
            recommendations,
            key=lambda rec: (
                {
                    PortfolioPriority.CRITICAL: 0,
                    PortfolioPriority.HIGH: 1,
                    PortfolioPriority.MEDIUM: 2,
                    PortfolioPriority.LOW: 3,
                }[rec.priority],
                -rec.net_value,
                rec.case_id,
            ),
        )
    )

    severity = "info"
    status = "optimized"
    if any(rec.priority is PortfolioPriority.CRITICAL for rec in ordered):
        severity = "critical"
        status = "critical-priorities"
    elif any(rec.priority is PortfolioPriority.HIGH for rec in ordered):
        severity = "warning"
        status = "priority-queue"
    elif any(rec.release_candidate for rec in ordered):
        status = "release-candidates"

    optimizer_signal = TelemetrySignal(
        signal_name="portfolio-optimizer",
        boundary=resolved_cockpit.cockpit_signal.boundary,
        correlation_id=optimizer_id,
        severity=severity,
        status=status,
        metrics={
            "recommendation_count": float(len(ordered)),
            "critical_count": float(len([rec for rec in ordered if rec.priority is PortfolioPriority.CRITICAL])),
            "high_count": float(len([rec for rec in ordered if rec.priority is PortfolioPriority.HIGH])),
            "release_candidate_count": float(len([rec for rec in ordered if rec.release_candidate])),
            "average_net_value": sum(rec.net_value for rec in ordered) / len(ordered),
        },
        labels={"optimizer_id": optimizer_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_cockpit.final_snapshot.runtime_stage,
        signals=(
            optimizer_signal,
            resolved_cockpit.cockpit_signal,
            resolved_campaign.campaign_signal,
            *resolved_cockpit.final_snapshot.signals,
        ),
        alerts=resolved_cockpit.final_snapshot.alerts,
        audit_entries=resolved_cockpit.final_snapshot.audit_entries,
        active_controls=resolved_cockpit.final_snapshot.active_controls,
    )
    return PortfolioOptimizer(
        optimizer_id=optimizer_id,
        cockpit=resolved_cockpit,
        remediation_campaign=resolved_campaign,
        recommendations=ordered,
        optimizer_signal=optimizer_signal,
        final_snapshot=final_snapshot,
    )
