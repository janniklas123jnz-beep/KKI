"""Operational action plans derived from readiness reviews."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .module_boundaries import ModuleBoundaryName
from .readiness_review import ReadinessFinding, ReadinessFindingSeverity, ReadinessReview, build_readiness_review
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


class ReviewActionPriority(str, Enum):
    """Canonical priorities for review-derived action items."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ReviewActionType(str, Enum):
    """Canonical action categories for readiness follow-up."""

    REMEDIATE = "remediate"
    GOVERN = "govern"
    RECOVER = "recover"
    MONITOR = "monitor"


@dataclass(frozen=True)
class ReviewActionItem:
    """Concrete operational action item derived from a readiness review."""

    action_id: str
    case_id: str
    priority: ReviewActionPriority
    action_type: ReviewActionType
    owner: ModuleBoundaryName
    summary: str
    target_status: str
    recommendation: str
    blocked_release: bool
    source_finding: ReadinessFinding | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "action_id", _non_empty(self.action_id, field_name="action_id"))
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        object.__setattr__(self, "target_status", _non_empty(self.target_status, field_name="target_status"))
        object.__setattr__(self, "recommendation", _non_empty(self.recommendation, field_name="recommendation"))

    def to_dict(self) -> dict[str, object]:
        return {
            "action_id": self.action_id,
            "case_id": self.case_id,
            "priority": self.priority.value,
            "action_type": self.action_type.value,
            "owner": self.owner.value,
            "summary": self.summary,
            "target_status": self.target_status,
            "recommendation": self.recommendation,
            "blocked_release": self.blocked_release,
            "source_finding": None if self.source_finding is None else self.source_finding.to_dict(),
        }


@dataclass(frozen=True)
class ReviewActionPlan:
    """Executable action plan compiled from a readiness review."""

    plan_id: str
    review: ReadinessReview
    actions: tuple[ReviewActionItem, ...]
    plan_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "plan_id", _non_empty(self.plan_id, field_name="plan_id"))

    @property
    def critical_case_ids(self) -> tuple[str, ...]:
        return tuple(action.case_id for action in self.actions if action.priority is ReviewActionPriority.CRITICAL)

    @property
    def blocked_case_ids(self) -> tuple[str, ...]:
        ordered: list[str] = []
        for action in self.actions:
            if not action.blocked_release:
                continue
            if action.case_id not in ordered:
                ordered.append(action.case_id)
        return tuple(ordered)

    @property
    def owner_boundaries(self) -> tuple[ModuleBoundaryName, ...]:
        ordered: list[ModuleBoundaryName] = []
        for action in self.actions:
            if action.owner not in ordered:
                ordered.append(action.owner)
        return tuple(ordered)

    def to_dict(self) -> dict[str, object]:
        return {
            "plan_id": self.plan_id,
            "review": self.review.to_dict(),
            "actions": [action.to_dict() for action in self.actions],
            "plan_signal": self.plan_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "critical_case_ids": list(self.critical_case_ids),
            "blocked_case_ids": list(self.blocked_case_ids),
            "owner_boundaries": [owner.value for owner in self.owner_boundaries],
        }


def _action_for_finding(plan_id: str, finding: ReadinessFinding) -> ReviewActionItem:
    priority = ReviewActionPriority.MEDIUM
    action_type = ReviewActionType.MONITOR
    owner = ModuleBoundaryName.TELEMETRY
    target_status = "score-reserve-improved"
    blocked_release = False

    if finding.severity is ReadinessFindingSeverity.CRITICAL:
        priority = ReviewActionPriority.CRITICAL
        action_type = ReviewActionType.REMEDIATE
        owner = ModuleBoundaryName.RECOVERY
        target_status = "containment-cleared"
        blocked_release = True
    elif finding.severity is ReadinessFindingSeverity.WARNING and "governance" in finding.summary:
        priority = ReviewActionPriority.HIGH
        action_type = ReviewActionType.GOVERN
        owner = ModuleBoundaryName.GOVERNANCE
        target_status = "governance-reviewed"
    elif finding.severity is ReadinessFindingSeverity.WARNING:
        priority = ReviewActionPriority.HIGH
        action_type = ReviewActionType.RECOVER
        owner = ModuleBoundaryName.RECOVERY
        target_status = "promotion-restored"
    elif finding.severity is ReadinessFindingSeverity.INFO:
        priority = ReviewActionPriority.LOW
        action_type = ReviewActionType.MONITOR
        owner = ModuleBoundaryName.TELEMETRY
        target_status = "headroom-improved"

    return ReviewActionItem(
        action_id=f"{plan_id}-{finding.case_id}-{action_type.value}",
        case_id=finding.case_id,
        priority=priority,
        action_type=action_type,
        owner=owner,
        summary=finding.summary,
        target_status=target_status,
        recommendation=finding.recommendation,
        blocked_release=blocked_release,
        source_finding=finding,
    )


def _sustain_action(plan_id: str, case_id: str) -> ReviewActionItem:
    return ReviewActionItem(
        action_id=f"{plan_id}-{case_id}-monitor",
        case_id=case_id,
        priority=ReviewActionPriority.LOW,
        action_type=ReviewActionType.MONITOR,
        owner=ModuleBoundaryName.TELEMETRY,
        summary=f"{case_id} remains healthy and should stay under observation",
        target_status="healthy-baseline-preserved",
        recommendation="Keep the healthy benchmark baseline under continuous observation.",
        blocked_release=False,
    )


def build_review_action_plan(
    review: ReadinessReview | None = None,
    *,
    plan_id: str = "review-action-plan",
) -> ReviewActionPlan:
    """Build an executable follow-up plan from a readiness review."""

    resolved_review = build_readiness_review(review_id=f"{plan_id}-review") if review is None else review
    actions = tuple(_action_for_finding(plan_id, finding) for finding in resolved_review.findings) + tuple(
        _sustain_action(plan_id, case_id) for case_id in resolved_review.healthy_case_ids
    )
    if not actions:
        raise ValueError("review action plan requires at least one action")

    severity = "info"
    status = "planned"
    if any(action.priority is ReviewActionPriority.CRITICAL for action in actions):
        severity = "critical"
        status = "critical-actions"
    elif any(action.priority is ReviewActionPriority.HIGH for action in actions):
        severity = "warning"
        status = "priority-actions"

    plan_signal = TelemetrySignal(
        signal_name="review-action-plan",
        boundary=ModuleBoundaryName.GOVERNANCE,
        correlation_id=plan_id,
        severity=severity,
        status=status,
        metrics={
            "action_count": float(len(actions)),
            "critical_count": float(len([action for action in actions if action.priority is ReviewActionPriority.CRITICAL])),
            "high_count": float(len([action for action in actions if action.priority is ReviewActionPriority.HIGH])),
            "blocked_case_count": float(len(resolved_review.blocked_case_ids)),
            "healthy_case_count": float(len(resolved_review.healthy_case_ids)),
        },
        labels={"plan_id": plan_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_review.final_snapshot.runtime_stage,
        signals=(plan_signal, resolved_review.review_signal, *resolved_review.final_snapshot.signals),
        alerts=resolved_review.final_snapshot.alerts,
        audit_entries=resolved_review.final_snapshot.audit_entries,
        active_controls=resolved_review.final_snapshot.active_controls,
    )
    return ReviewActionPlan(
        plan_id=plan_id,
        review=resolved_review,
        actions=actions,
        plan_signal=plan_signal,
        final_snapshot=final_snapshot,
    )
