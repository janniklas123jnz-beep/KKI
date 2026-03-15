"""Strategic council over executive orders, escalation mandates, and durable lanes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .executive_watchtower import (
    ExecutiveOrder,
    ExecutiveOrderMode,
    ExecutiveWatchStatus,
    ExecutiveWatchtower,
    build_executive_watchtower,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class StrategyLane(str, Enum):
    """Durable strategic lanes derived from executive orders."""

    STABILITY = "stability-lane"
    GOVERNANCE = "governance-lane"
    EXPANSION = "expansion-lane"


class StrategyPriority(str, Enum):
    """Priority posture assigned by the strategy council."""

    IMMEDIATE = "immediate"
    DIRECTED = "directed"
    COMPOUND = "compound"


class StrategyEscalationMandate(str, Enum):
    """Escalation mandate attached to a strategic lane."""

    CONTAINMENT = "containment-mandate"
    REVIEW = "review-mandate"
    EXPANSION = "expansion-mandate"


class StrategyCouncilStatus(str, Enum):
    """High-level operating posture of a strategic mandate."""

    ESCALATED = "escalated"
    ORCHESTRATED = "orchestrated"
    PRIMED = "primed"


@dataclass(frozen=True)
class StrategyMandate:
    """Strategic mandate resolved from one executive order."""

    mandate_id: str
    sequence: int
    order_id: str
    track_id: str
    lane: StrategyLane
    priority: StrategyPriority
    escalation_mandate: StrategyEscalationMandate
    council_status: StrategyCouncilStatus
    case_ids: tuple[str, ...]
    release_ready: bool
    strategic_budget: float
    review_window: int
    control_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "mandate_id", _non_empty(self.mandate_id, field_name="mandate_id"))
        object.__setattr__(self, "order_id", _non_empty(self.order_id, field_name="order_id"))
        object.__setattr__(self, "track_id", _non_empty(self.track_id, field_name="track_id"))
        object.__setattr__(self, "strategic_budget", _clamp01(self.strategic_budget))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.review_window < 1:
            raise ValueError("review_window must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "mandate_id": self.mandate_id,
            "sequence": self.sequence,
            "order_id": self.order_id,
            "track_id": self.track_id,
            "lane": self.lane.value,
            "priority": self.priority.value,
            "escalation_mandate": self.escalation_mandate.value,
            "council_status": self.council_status.value,
            "case_ids": list(self.case_ids),
            "release_ready": self.release_ready,
            "strategic_budget": self.strategic_budget,
            "review_window": self.review_window,
            "control_tags": list(self.control_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class StrategyCouncil:
    """Strategic council that consolidates executive orders into durable lanes."""

    council_id: str
    executive_watchtower: ExecutiveWatchtower
    mandates: tuple[StrategyMandate, ...]
    council_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "council_id", _non_empty(self.council_id, field_name="council_id"))

    @property
    def escalated_mandate_ids(self) -> tuple[str, ...]:
        return tuple(mandate.mandate_id for mandate in self.mandates if mandate.council_status is StrategyCouncilStatus.ESCALATED)

    @property
    def orchestrated_mandate_ids(self) -> tuple[str, ...]:
        return tuple(
            mandate.mandate_id for mandate in self.mandates if mandate.council_status is StrategyCouncilStatus.ORCHESTRATED
        )

    @property
    def primed_mandate_ids(self) -> tuple[str, ...]:
        return tuple(mandate.mandate_id for mandate in self.mandates if mandate.council_status is StrategyCouncilStatus.PRIMED)

    def to_dict(self) -> dict[str, object]:
        return {
            "council_id": self.council_id,
            "executive_watchtower": self.executive_watchtower.to_dict(),
            "mandates": [mandate.to_dict() for mandate in self.mandates],
            "council_signal": self.council_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "escalated_mandate_ids": list(self.escalated_mandate_ids),
            "orchestrated_mandate_ids": list(self.orchestrated_mandate_ids),
            "primed_mandate_ids": list(self.primed_mandate_ids),
        }


def _lane_for_order(order: ExecutiveOrder) -> StrategyLane:
    return {
        ExecutiveOrderMode.EXECUTIVE_OVERRIDE: StrategyLane.STABILITY,
        ExecutiveOrderMode.GOVERNED_EXECUTION: StrategyLane.GOVERNANCE,
        ExecutiveOrderMode.AUTONOMY_WINDOW: StrategyLane.EXPANSION,
    }[order.mode]


def _priority_for_order(order: ExecutiveOrder) -> StrategyPriority:
    if order.watch_status is ExecutiveWatchStatus.LOCKED:
        return StrategyPriority.IMMEDIATE
    if order.watch_status is ExecutiveWatchStatus.COMMANDING:
        return StrategyPriority.DIRECTED
    return StrategyPriority.COMPOUND


def _escalation_for_order(order: ExecutiveOrder) -> StrategyEscalationMandate:
    return {
        ExecutiveOrderMode.EXECUTIVE_OVERRIDE: StrategyEscalationMandate.CONTAINMENT,
        ExecutiveOrderMode.GOVERNED_EXECUTION: StrategyEscalationMandate.REVIEW,
        ExecutiveOrderMode.AUTONOMY_WINDOW: StrategyEscalationMandate.EXPANSION,
    }[order.mode]


def _status_for_order(order: ExecutiveOrder) -> StrategyCouncilStatus:
    if order.watch_status is ExecutiveWatchStatus.LOCKED:
        return StrategyCouncilStatus.ESCALATED
    if order.watch_status is ExecutiveWatchStatus.COMMANDING:
        return StrategyCouncilStatus.ORCHESTRATED
    return StrategyCouncilStatus.PRIMED


def _strategic_budget(order: ExecutiveOrder) -> float:
    floor = {
        ExecutiveOrderMode.EXECUTIVE_OVERRIDE: 1.0,
        ExecutiveOrderMode.GOVERNED_EXECUTION: 0.7,
        ExecutiveOrderMode.AUTONOMY_WINDOW: 0.4,
    }[order.mode]
    return round(max(floor, order.command_budget), 3)


def _review_window(order: ExecutiveOrder) -> int:
    if order.watch_status is ExecutiveWatchStatus.LOCKED:
        return max(1, order.escalation_window)
    if order.watch_status is ExecutiveWatchStatus.COMMANDING:
        return max(1, order.escalation_window + 1)
    return max(1, order.escalation_window + 2)


def build_strategy_council(
    executive_watchtower: ExecutiveWatchtower | None = None,
    *,
    council_id: str = "strategy-council",
) -> StrategyCouncil:
    """Build the strategic council from executive watchtower orders."""

    resolved_watchtower = (
        build_executive_watchtower(watchtower_id=f"{council_id}-watchtower")
        if executive_watchtower is None
        else executive_watchtower
    )
    mandates = tuple(
        StrategyMandate(
            mandate_id=f"{council_id}-{_lane_for_order(order).value}",
            sequence=index,
            order_id=order.order_id,
            track_id=order.track_id,
            lane=_lane_for_order(order),
            priority=_priority_for_order(order),
            escalation_mandate=_escalation_for_order(order),
            council_status=_status_for_order(order),
            case_ids=order.case_ids,
            release_ready=order.release_ready,
            strategic_budget=_strategic_budget(order),
            review_window=_review_window(order),
            control_tags=tuple(
                dict.fromkeys(
                    (
                        *order.control_tags,
                        _lane_for_order(order).value,
                        _escalation_for_order(order).value,
                        "release-window-open" if order.release_ready else "release-window-closed",
                    )
                )
            ),
            summary=(
                f"{_lane_for_order(order).value} carries {_priority_for_order(order).value} priority "
                f"under {_status_for_order(order).value} council posture."
            ),
        )
        for index, order in enumerate(resolved_watchtower.orders, start=1)
    )
    if not mandates:
        raise ValueError("strategy council requires at least one mandate")

    severity = "info"
    status = "strategy-primed"
    if any(mandate.council_status is StrategyCouncilStatus.ESCALATED for mandate in mandates):
        severity = "critical"
        status = "strategy-escalated"
    elif any(mandate.council_status is StrategyCouncilStatus.ORCHESTRATED for mandate in mandates):
        severity = "warning"
        status = "strategy-orchestrated"

    council_signal = TelemetrySignal(
        signal_name="strategy-council",
        boundary=resolved_watchtower.watchtower_signal.boundary,
        correlation_id=council_id,
        severity=severity,
        status=status,
        metrics={
            "mandate_count": float(len(mandates)),
            "escalated_count": float(
                len([mandate for mandate in mandates if mandate.council_status is StrategyCouncilStatus.ESCALATED])
            ),
            "orchestrated_count": float(
                len([mandate for mandate in mandates if mandate.council_status is StrategyCouncilStatus.ORCHESTRATED])
            ),
            "primed_count": float(
                len([mandate for mandate in mandates if mandate.council_status is StrategyCouncilStatus.PRIMED])
            ),
            "release_ready_count": float(len([mandate for mandate in mandates if mandate.release_ready])),
            "avg_strategic_budget": round(sum(mandate.strategic_budget for mandate in mandates) / len(mandates), 3),
        },
        labels={"council_id": council_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_watchtower.final_snapshot.runtime_stage,
        signals=(council_signal, *resolved_watchtower.final_snapshot.signals),
        alerts=resolved_watchtower.final_snapshot.alerts,
        audit_entries=resolved_watchtower.final_snapshot.audit_entries,
        active_controls=resolved_watchtower.final_snapshot.active_controls,
    )
    return StrategyCouncil(
        council_id=council_id,
        executive_watchtower=resolved_watchtower,
        mandates=mandates,
        council_signal=council_signal,
        final_snapshot=final_snapshot,
    )
