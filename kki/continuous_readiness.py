"""Continuous readiness cycle over cockpit and portfolio recommendations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .module_boundaries import ModuleBoundaryName
from .operations_cockpit import CockpitStatus, OperationsCockpit, build_operations_cockpit
from .portfolio_optimizer import (
    PortfolioAction,
    PortfolioOptimizer,
    PortfolioPriority,
    PortfolioRecommendation,
    build_portfolio_optimizer,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


class ContinuousReadinessStatus(str, Enum):
    """High-level states for the continuous readiness loop."""

    READY = "ready"
    ATTENTION = "attention"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ContinuousReadinessIteration:
    """One loop iteration derived from cockpit and optimization state."""

    iteration_id: str
    case_id: str
    sequence: int
    cockpit_status: CockpitStatus
    portfolio_priority: PortfolioPriority
    recommended_action: PortfolioAction
    owner: ModuleBoundaryName
    next_review_status: str
    target_status: str
    release_candidate: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "iteration_id", _non_empty(self.iteration_id, field_name="iteration_id"))
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))
        object.__setattr__(self, "next_review_status", _non_empty(self.next_review_status, field_name="next_review_status"))
        object.__setattr__(self, "target_status", _non_empty(self.target_status, field_name="target_status"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")

    @property
    def status(self) -> ContinuousReadinessStatus:
        if self.next_review_status == "not-ready":
            return ContinuousReadinessStatus.BLOCKED
        if self.next_review_status == "review-required":
            return ContinuousReadinessStatus.ATTENTION
        return ContinuousReadinessStatus.READY

    def to_dict(self) -> dict[str, object]:
        return {
            "iteration_id": self.iteration_id,
            "case_id": self.case_id,
            "sequence": self.sequence,
            "cockpit_status": self.cockpit_status.value,
            "portfolio_priority": self.portfolio_priority.value,
            "recommended_action": self.recommended_action.value,
            "owner": self.owner.value,
            "next_review_status": self.next_review_status,
            "target_status": self.target_status,
            "release_candidate": self.release_candidate,
            "status": self.status.value,
        }


@dataclass(frozen=True)
class ContinuousReadinessCycle:
    """Closed operational loop over cockpit and optimized next steps."""

    cycle_id: str
    cockpit: OperationsCockpit
    optimizer: PortfolioOptimizer
    iterations: tuple[ContinuousReadinessIteration, ...]
    cycle_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "cycle_id", _non_empty(self.cycle_id, field_name="cycle_id"))

    @property
    def ready_case_ids(self) -> tuple[str, ...]:
        return tuple(iteration.case_id for iteration in self.iterations if iteration.status is ContinuousReadinessStatus.READY)

    @property
    def attention_case_ids(self) -> tuple[str, ...]:
        return tuple(iteration.case_id for iteration in self.iterations if iteration.status is ContinuousReadinessStatus.ATTENTION)

    @property
    def blocked_case_ids(self) -> tuple[str, ...]:
        return tuple(iteration.case_id for iteration in self.iterations if iteration.status is ContinuousReadinessStatus.BLOCKED)

    @property
    def next_focus_case_ids(self) -> tuple[str, ...]:
        return tuple(
            iteration.case_id
            for iteration in self.iterations
            if iteration.portfolio_priority in {PortfolioPriority.CRITICAL, PortfolioPriority.HIGH}
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "cycle_id": self.cycle_id,
            "cockpit": self.cockpit.to_dict(),
            "optimizer": self.optimizer.to_dict(),
            "iterations": [iteration.to_dict() for iteration in self.iterations],
            "cycle_signal": self.cycle_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "ready_case_ids": list(self.ready_case_ids),
            "attention_case_ids": list(self.attention_case_ids),
            "blocked_case_ids": list(self.blocked_case_ids),
            "next_focus_case_ids": list(self.next_focus_case_ids),
        }


def _next_review_status_for_recommendation(recommendation: PortfolioRecommendation) -> str:
    if recommendation.action is PortfolioAction.CONTAIN:
        return "not-ready"
    if recommendation.action in {PortfolioAction.RECOVER, PortfolioAction.APPROVE, PortfolioAction.MONITOR}:
        return "review-required"
    return "ready"


def _iteration_for_recommendation(
    cycle_id: str,
    sequence: int,
    recommendation: PortfolioRecommendation,
    cockpit: OperationsCockpit,
) -> ContinuousReadinessIteration:
    cockpit_entry = next(entry for entry in cockpit.entries if entry.case_id == recommendation.case_id)
    return ContinuousReadinessIteration(
        iteration_id=f"{cycle_id}-{recommendation.case_id}",
        case_id=recommendation.case_id,
        sequence=sequence,
        cockpit_status=cockpit_entry.status,
        portfolio_priority=recommendation.priority,
        recommended_action=recommendation.action,
        owner=recommendation.owner,
        next_review_status=_next_review_status_for_recommendation(recommendation),
        target_status=recommendation.target_status,
        release_candidate=recommendation.release_candidate,
    )


def build_continuous_readiness_cycle(
    cockpit: OperationsCockpit | None = None,
    optimizer: PortfolioOptimizer | None = None,
    *,
    cycle_id: str = "continuous-readiness",
) -> ContinuousReadinessCycle:
    """Build a closed readiness loop from cockpit state and next-step recommendations."""

    resolved_cockpit = build_operations_cockpit(cockpit_id=f"{cycle_id}-cockpit") if cockpit is None else cockpit
    resolved_optimizer = (
        build_portfolio_optimizer(cockpit=resolved_cockpit, remediation_campaign=resolved_cockpit.remediation_campaign, optimizer_id=f"{cycle_id}-optimizer")
        if optimizer is None
        else optimizer
    )
    iterations = tuple(
        _iteration_for_recommendation(cycle_id, index, recommendation, resolved_cockpit)
        for index, recommendation in enumerate(resolved_optimizer.recommendations, start=1)
    )
    if not iterations:
        raise ValueError("continuous readiness cycle requires at least one iteration")

    severity = "info"
    status = ContinuousReadinessStatus.READY.value
    if any(iteration.status is ContinuousReadinessStatus.BLOCKED for iteration in iterations):
        severity = "critical"
        status = ContinuousReadinessStatus.BLOCKED.value
    elif any(iteration.status is ContinuousReadinessStatus.ATTENTION for iteration in iterations):
        severity = "warning"
        status = ContinuousReadinessStatus.ATTENTION.value

    cycle_signal = TelemetrySignal(
        signal_name="continuous-readiness",
        boundary=resolved_cockpit.cockpit_signal.boundary,
        correlation_id=cycle_id,
        severity=severity,
        status=status,
        metrics={
            "iteration_count": float(len(iterations)),
            "ready_count": float(len([iteration for iteration in iterations if iteration.status is ContinuousReadinessStatus.READY])),
            "attention_count": float(len([iteration for iteration in iterations if iteration.status is ContinuousReadinessStatus.ATTENTION])),
            "blocked_count": float(len([iteration for iteration in iterations if iteration.status is ContinuousReadinessStatus.BLOCKED])),
            "release_candidate_count": float(len([iteration for iteration in iterations if iteration.release_candidate])),
        },
        labels={"cycle_id": cycle_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_optimizer.final_snapshot.runtime_stage,
        signals=(
            cycle_signal,
            resolved_cockpit.cockpit_signal,
            resolved_optimizer.optimizer_signal,
            *resolved_optimizer.final_snapshot.signals,
        ),
        alerts=resolved_optimizer.final_snapshot.alerts,
        audit_entries=resolved_optimizer.final_snapshot.audit_entries,
        active_controls=resolved_optimizer.final_snapshot.active_controls,
    )
    return ContinuousReadinessCycle(
        cycle_id=cycle_id,
        cockpit=resolved_cockpit,
        optimizer=resolved_optimizer,
        iterations=iterations,
        cycle_signal=cycle_signal,
        final_snapshot=final_snapshot,
    )
