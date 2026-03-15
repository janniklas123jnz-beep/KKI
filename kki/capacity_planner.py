"""Capacity planning over portfolio recommendations and evidence tracks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .evidence_ledger import EvidenceLedger, build_evidence_ledger
from .escalation_router import EscalationRoutePath
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


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class CapacityWindow(str, Enum):
    """Implementation windows for capacity admission."""

    IMMEDIATE = "immediate"
    CURRENT = "current"
    NEXT = "next"
    BACKLOG = "backlog"


class CapacityLane(str, Enum):
    """Admission result for one capacity candidate."""

    ADMIT = "admit"
    HOLD = "hold"
    DEFER = "defer"


@dataclass(frozen=True)
class CapacityPlanEntry:
    """Concrete capacity reservation for one portfolio recommendation."""

    plan_entry_id: str
    case_id: str
    window: CapacityWindow
    lane: CapacityLane
    route_path: EscalationRoutePath
    budget_share: float
    reserved_budget: float
    wip_slot: int | None
    lease_window: int
    rationale: str
    release_candidate: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "plan_entry_id", _non_empty(self.plan_entry_id, field_name="plan_entry_id"))
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))
        object.__setattr__(self, "budget_share", _clamp01(self.budget_share))
        object.__setattr__(self, "reserved_budget", _clamp01(self.reserved_budget))
        object.__setattr__(self, "rationale", _non_empty(self.rationale, field_name="rationale"))
        if self.lease_window < 1:
            raise ValueError("lease_window must be positive")
        if self.wip_slot is not None and self.wip_slot < 1:
            raise ValueError("wip_slot must be positive when provided")

    def to_dict(self) -> dict[str, object]:
        return {
            "plan_entry_id": self.plan_entry_id,
            "case_id": self.case_id,
            "window": self.window.value,
            "lane": self.lane.value,
            "route_path": self.route_path.value,
            "budget_share": self.budget_share,
            "reserved_budget": self.reserved_budget,
            "wip_slot": self.wip_slot,
            "lease_window": self.lease_window,
            "rationale": self.rationale,
            "release_candidate": self.release_candidate,
        }


@dataclass(frozen=True)
class CapacityPlanner:
    """Deterministic capacity plan over prioritized portfolio work."""

    planner_id: str
    optimizer: PortfolioOptimizer
    evidence_ledger: EvidenceLedger
    total_budget: float
    max_parallel: int
    entries: tuple[CapacityPlanEntry, ...]
    planner_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "planner_id", _non_empty(self.planner_id, field_name="planner_id"))
        object.__setattr__(self, "total_budget", _clamp01(self.total_budget))
        if self.max_parallel < 1:
            raise ValueError("max_parallel must be positive")

    @property
    def consumed_budget(self) -> float:
        return round(sum(entry.reserved_budget for entry in self.entries), 3)

    @property
    def admitted_case_ids(self) -> tuple[str, ...]:
        return tuple(entry.case_id for entry in self.entries if entry.lane is CapacityLane.ADMIT)

    @property
    def held_case_ids(self) -> tuple[str, ...]:
        return tuple(entry.case_id for entry in self.entries if entry.lane is CapacityLane.HOLD)

    @property
    def deferred_case_ids(self) -> tuple[str, ...]:
        return tuple(entry.case_id for entry in self.entries if entry.lane is CapacityLane.DEFER)

    @property
    def immediate_case_ids(self) -> tuple[str, ...]:
        return tuple(entry.case_id for entry in self.entries if entry.window is CapacityWindow.IMMEDIATE)

    @property
    def current_window_case_ids(self) -> tuple[str, ...]:
        return tuple(entry.case_id for entry in self.entries if entry.window is CapacityWindow.CURRENT)

    def to_dict(self) -> dict[str, object]:
        return {
            "planner_id": self.planner_id,
            "optimizer": self.optimizer.to_dict(),
            "evidence_ledger": self.evidence_ledger.to_dict(),
            "total_budget": self.total_budget,
            "max_parallel": self.max_parallel,
            "entries": [entry.to_dict() for entry in self.entries],
            "planner_signal": self.planner_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "consumed_budget": self.consumed_budget,
            "admitted_case_ids": list(self.admitted_case_ids),
            "held_case_ids": list(self.held_case_ids),
            "deferred_case_ids": list(self.deferred_case_ids),
            "immediate_case_ids": list(self.immediate_case_ids),
            "current_window_case_ids": list(self.current_window_case_ids),
        }


def _route_by_case(ledger: EvidenceLedger) -> dict[str, EscalationRoutePath]:
    return {
        case_id: next(entry.route_path for entry in ledger.entries if entry.case_id == case_id)
        for case_id in ledger.case_ids
    }


def _window_for_route(route_path: EscalationRoutePath, recommendation: PortfolioRecommendation) -> CapacityWindow:
    if route_path is EscalationRoutePath.RECOVERY_CONTAINMENT:
        return CapacityWindow.IMMEDIATE
    if route_path in {EscalationRoutePath.GOVERNANCE_REVIEW, EscalationRoutePath.RECOVERY_RESTART}:
        return CapacityWindow.CURRENT
    if recommendation.release_candidate or recommendation.action is PortfolioAction.ADVANCE:
        return CapacityWindow.NEXT
    return CapacityWindow.BACKLOG


def _budget_share_for_recommendation(recommendation: PortfolioRecommendation) -> float:
    base = {
        PortfolioAction.CONTAIN: 0.34,
        PortfolioAction.RECOVER: 0.28,
        PortfolioAction.APPROVE: 0.18,
        PortfolioAction.ADVANCE: 0.16,
        PortfolioAction.MONITOR: 0.12,
    }[recommendation.action]
    return _clamp01(base + (recommendation.capacity_cost * 0.1))


def _lease_window_for_entry(window: CapacityWindow) -> int:
    return {
        CapacityWindow.IMMEDIATE: 1,
        CapacityWindow.CURRENT: 2,
        CapacityWindow.NEXT: 3,
        CapacityWindow.BACKLOG: 4,
    }[window]


def build_capacity_planner(
    optimizer: PortfolioOptimizer | None = None,
    evidence_ledger: EvidenceLedger | None = None,
    *,
    planner_id: str = "capacity-planner",
    total_budget: float = 0.72,
    max_parallel: int = 2,
) -> CapacityPlanner:
    """Build deterministic capacity reservations over prioritized portfolio work."""

    resolved_optimizer = build_portfolio_optimizer(optimizer_id=f"{planner_id}-optimizer") if optimizer is None else optimizer
    resolved_ledger = build_evidence_ledger(ledger_id=f"{planner_id}-ledger") if evidence_ledger is None else evidence_ledger
    route_by_case = _route_by_case(resolved_ledger)
    ordered_recommendations = tuple(resolved_optimizer.recommendations)
    entries: list[CapacityPlanEntry] = []
    admitted = 0
    consumed_budget = 0.0

    for recommendation in ordered_recommendations:
        route_path = route_by_case[recommendation.case_id]
        window = _window_for_route(route_path, recommendation)
        budget_share = _budget_share_for_recommendation(recommendation)
        lane = CapacityLane.ADMIT
        rationale = f"{recommendation.case_id} is admitted into the {window.value} capacity window."
        if window is CapacityWindow.BACKLOG:
            lane = CapacityLane.DEFER
            rationale = f"{recommendation.case_id} stays in backlog until higher-priority windows clear."
        elif window is CapacityWindow.NEXT:
            lane = CapacityLane.DEFER
            rationale = f"{recommendation.case_id} is queued for the next implementation window rather than the active cycle."
        elif admitted >= max_parallel:
            lane = CapacityLane.HOLD
            rationale = f"{recommendation.case_id} is held because the WIP limit for this cycle is exhausted."
        elif budget_share > total_budget - consumed_budget:
            lane = CapacityLane.HOLD
            rationale = f"{recommendation.case_id} is held to preserve budget headroom for already admitted work."

        reserved_budget = budget_share if lane is CapacityLane.ADMIT else 0.0
        wip_slot = admitted + 1 if lane is CapacityLane.ADMIT else None
        entries.append(
            CapacityPlanEntry(
                plan_entry_id=f"{planner_id}-{recommendation.case_id}",
                case_id=recommendation.case_id,
                window=window,
                lane=lane,
                route_path=route_path,
                budget_share=budget_share,
                reserved_budget=reserved_budget,
                wip_slot=wip_slot,
                lease_window=_lease_window_for_entry(window),
                rationale=rationale,
                release_candidate=recommendation.release_candidate,
            )
        )
        if lane is CapacityLane.ADMIT:
            admitted += 1
            consumed_budget += reserved_budget

    resolved_entries = tuple(entries)
    if not resolved_entries:
        raise ValueError("capacity planner requires at least one entry")

    severity = "info"
    status = "scheduled"
    if any(entry.window is CapacityWindow.IMMEDIATE and entry.lane is CapacityLane.ADMIT for entry in resolved_entries):
        severity = "critical"
        status = "immediate-capacity"
    elif any(entry.lane is CapacityLane.HOLD for entry in resolved_entries):
        severity = "warning"
        status = "constrained-capacity"
    elif any(entry.window is CapacityWindow.NEXT for entry in resolved_entries):
        status = "next-window"

    planner_signal = TelemetrySignal(
        signal_name="capacity-planner",
        boundary=resolved_optimizer.optimizer_signal.boundary,
        correlation_id=planner_id,
        severity=severity,
        status=status,
        metrics={
            "entry_count": float(len(resolved_entries)),
            "admit_count": float(len([entry for entry in resolved_entries if entry.lane is CapacityLane.ADMIT])),
            "hold_count": float(len([entry for entry in resolved_entries if entry.lane is CapacityLane.HOLD])),
            "defer_count": float(len([entry for entry in resolved_entries if entry.lane is CapacityLane.DEFER])),
            "consumed_budget": round(consumed_budget, 3),
            "remaining_budget": round(max(total_budget - consumed_budget, 0.0), 3),
            "max_parallel": float(max_parallel),
        },
        labels={"planner_id": planner_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_ledger.final_snapshot.runtime_stage,
        signals=(
            planner_signal,
            resolved_optimizer.optimizer_signal,
            resolved_ledger.ledger_signal,
            *resolved_ledger.final_snapshot.signals,
        ),
        alerts=resolved_ledger.final_snapshot.alerts,
        audit_entries=resolved_ledger.final_snapshot.audit_entries,
        active_controls=resolved_ledger.final_snapshot.active_controls,
    )
    return CapacityPlanner(
        planner_id=planner_id,
        optimizer=resolved_optimizer,
        evidence_ledger=resolved_ledger,
        total_budget=total_budget,
        max_parallel=max_parallel,
        entries=resolved_entries,
        planner_signal=planner_signal,
        final_snapshot=final_snapshot,
    )
