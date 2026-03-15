"""Risk register derived from readiness reviews and action plans."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .module_boundaries import ModuleBoundaryName
from .review_action_plan import ReviewActionPlan, ReviewActionPriority, ReviewActionType, build_review_action_plan
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


class RiskLikelihood(str, Enum):
    """Canonical likelihood levels for operational risks."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskImpact(str, Enum):
    """Canonical impact levels for operational risks."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskMitigationStatus(str, Enum):
    """Canonical mitigation states for registered risks."""

    OBSERVE = "observe"
    PLANNED = "planned"
    ACTIVE = "active"
    BLOCKING = "blocking"


@dataclass(frozen=True)
class RiskRecord:
    """Persistent operational risk entry linked to review actions."""

    risk_id: str
    case_id: str
    owner: ModuleBoundaryName
    likelihood: RiskLikelihood
    impact: RiskImpact
    mitigation_status: RiskMitigationStatus
    summary: str
    mitigation_ref: str
    action_ref: str
    blocked_release: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "risk_id", _non_empty(self.risk_id, field_name="risk_id"))
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        object.__setattr__(self, "mitigation_ref", _non_empty(self.mitigation_ref, field_name="mitigation_ref"))
        object.__setattr__(self, "action_ref", _non_empty(self.action_ref, field_name="action_ref"))

    def to_dict(self) -> dict[str, object]:
        return {
            "risk_id": self.risk_id,
            "case_id": self.case_id,
            "owner": self.owner.value,
            "likelihood": self.likelihood.value,
            "impact": self.impact.value,
            "mitigation_status": self.mitigation_status.value,
            "summary": self.summary,
            "mitigation_ref": self.mitigation_ref,
            "action_ref": self.action_ref,
            "blocked_release": self.blocked_release,
        }


@dataclass(frozen=True)
class RiskRegister:
    """Aggregated risk register over a review action plan."""

    register_id: str
    action_plan: ReviewActionPlan
    risks: tuple[RiskRecord, ...]
    register_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "register_id", _non_empty(self.register_id, field_name="register_id"))

    @property
    def blocking_case_ids(self) -> tuple[str, ...]:
        ordered: list[str] = []
        for risk in self.risks:
            if not risk.blocked_release:
                continue
            if risk.case_id not in ordered:
                ordered.append(risk.case_id)
        return tuple(ordered)

    @property
    def active_case_ids(self) -> tuple[str, ...]:
        ordered: list[str] = []
        for risk in self.risks:
            if risk.mitigation_status not in {RiskMitigationStatus.ACTIVE, RiskMitigationStatus.BLOCKING}:
                continue
            if risk.case_id not in ordered:
                ordered.append(risk.case_id)
        return tuple(ordered)

    @property
    def owner_boundaries(self) -> tuple[ModuleBoundaryName, ...]:
        ordered: list[ModuleBoundaryName] = []
        for risk in self.risks:
            if risk.owner not in ordered:
                ordered.append(risk.owner)
        return tuple(ordered)

    def to_dict(self) -> dict[str, object]:
        return {
            "register_id": self.register_id,
            "action_plan": self.action_plan.to_dict(),
            "risks": [risk.to_dict() for risk in self.risks],
            "register_signal": self.register_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "blocking_case_ids": list(self.blocking_case_ids),
            "active_case_ids": list(self.active_case_ids),
            "owner_boundaries": [owner.value for owner in self.owner_boundaries],
        }


def _risk_for_action(register_id: str, plan_id: str, action) -> RiskRecord:
    likelihood = RiskLikelihood.MEDIUM
    impact = RiskImpact.MEDIUM
    mitigation_status = RiskMitigationStatus.PLANNED

    if action.priority is ReviewActionPriority.CRITICAL:
        likelihood = RiskLikelihood.HIGH
        impact = RiskImpact.CRITICAL
        mitigation_status = RiskMitigationStatus.BLOCKING
    elif action.priority is ReviewActionPriority.HIGH:
        likelihood = RiskLikelihood.HIGH
        impact = RiskImpact.HIGH
        mitigation_status = RiskMitigationStatus.ACTIVE
    elif action.priority is ReviewActionPriority.LOW:
        likelihood = RiskLikelihood.LOW
        impact = RiskImpact.LOW
        mitigation_status = RiskMitigationStatus.OBSERVE

    if action.action_type is ReviewActionType.GOVERN:
        impact = RiskImpact.HIGH if action.priority is not ReviewActionPriority.CRITICAL else RiskImpact.CRITICAL
    elif action.action_type is ReviewActionType.RECOVER:
        likelihood = RiskLikelihood.HIGH
        impact = RiskImpact.HIGH if action.priority is not ReviewActionPriority.CRITICAL else RiskImpact.CRITICAL
    elif action.action_type is ReviewActionType.MONITOR and action.priority is ReviewActionPriority.LOW:
        mitigation_status = RiskMitigationStatus.OBSERVE

    return RiskRecord(
        risk_id=f"{register_id}-{action.case_id}-{action.action_type.value}",
        case_id=action.case_id,
        owner=action.owner,
        likelihood=likelihood,
        impact=impact,
        mitigation_status=mitigation_status,
        summary=action.summary,
        mitigation_ref=f"mitigation-{plan_id}-{action.case_id}",
        action_ref=action.action_id,
        blocked_release=action.blocked_release,
    )


def build_risk_register(
    action_plan: ReviewActionPlan | None = None,
    *,
    register_id: str = "risk-register",
) -> RiskRegister:
    """Build the persistent risk register from a review action plan."""

    resolved_plan = build_review_action_plan(plan_id=f"{register_id}-plan") if action_plan is None else action_plan
    risks = tuple(_risk_for_action(register_id, resolved_plan.plan_id, action) for action in resolved_plan.actions)
    if not risks:
        raise ValueError("risk register requires at least one risk")

    severity = "info"
    status = "observed"
    if any(risk.mitigation_status is RiskMitigationStatus.BLOCKING for risk in risks):
        severity = "critical"
        status = "blocking-risks"
    elif any(risk.mitigation_status is RiskMitigationStatus.ACTIVE for risk in risks):
        severity = "warning"
        status = "active-risks"

    register_signal = TelemetrySignal(
        signal_name="risk-register",
        boundary=ModuleBoundaryName.GOVERNANCE,
        correlation_id=register_id,
        severity=severity,
        status=status,
        metrics={
            "risk_count": float(len(risks)),
            "blocking_count": float(len([risk for risk in risks if risk.mitigation_status is RiskMitigationStatus.BLOCKING])),
            "active_count": float(len([risk for risk in risks if risk.mitigation_status is RiskMitigationStatus.ACTIVE])),
            "observe_count": float(len([risk for risk in risks if risk.mitigation_status is RiskMitigationStatus.OBSERVE])),
            "high_likelihood_count": float(len([risk for risk in risks if risk.likelihood is RiskLikelihood.HIGH])),
        },
        labels={"register_id": register_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_plan.final_snapshot.runtime_stage,
        signals=(register_signal, resolved_plan.plan_signal, *resolved_plan.final_snapshot.signals),
        alerts=resolved_plan.final_snapshot.alerts,
        audit_entries=resolved_plan.final_snapshot.audit_entries,
        active_controls=resolved_plan.final_snapshot.active_controls,
    )
    return RiskRegister(
        register_id=register_id,
        action_plan=resolved_plan,
        risks=risks,
        register_signal=register_signal,
        final_snapshot=final_snapshot,
    )
