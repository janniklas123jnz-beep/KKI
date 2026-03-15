"""Operational workboard over steward directives."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .operations_steward import OperationsSteward, StewardDirective, StewardDirectiveType, build_operations_steward
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


class WorkboardQueue(str, Enum):
    """Operational queues exposed by the steward workboard."""

    STABILIZATION = "stabilization"
    GOVERNANCE = "governance"
    ADAPTATION = "adaptation"
    MONITORING = "monitoring"


class WorkboardLane(str, Enum):
    """Priority lanes for workboard execution."""

    EXPEDITE = "expedite"
    COMMITTED = "committed"
    FOLLOW_UP = "follow-up"
    WATCH = "watch"


class WorkboardStatus(str, Enum):
    """Execution state for one workboard item."""

    DUE_NOW = "due-now"
    SCHEDULED = "scheduled"
    TRACKED = "tracked"


@dataclass(frozen=True)
class WorkboardItem:
    """Operational board item derived from a steward directive."""

    item_id: str
    case_id: str
    sequence: int
    directive_type: StewardDirectiveType
    queue: WorkboardQueue
    lane: WorkboardLane
    status: WorkboardStatus
    sla_hours: int
    evidence_refs: tuple[str, ...]
    commitment_refs: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "item_id", _non_empty(self.item_id, field_name="item_id"))
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.sla_hours < 1:
            raise ValueError("sla_hours must be positive")

    def to_dict(self) -> dict[str, object]:
        return {
            "item_id": self.item_id,
            "case_id": self.case_id,
            "sequence": self.sequence,
            "directive_type": self.directive_type.value,
            "queue": self.queue.value,
            "lane": self.lane.value,
            "status": self.status.value,
            "sla_hours": self.sla_hours,
            "evidence_refs": list(self.evidence_refs),
            "commitment_refs": list(self.commitment_refs),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class StewardWorkboard:
    """Operational work surface over steward directives."""

    workboard_id: str
    steward: OperationsSteward
    items: tuple[WorkboardItem, ...]
    board_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "workboard_id", _non_empty(self.workboard_id, field_name="workboard_id"))

    @property
    def expedite_case_ids(self) -> tuple[str, ...]:
        return tuple(item.case_id for item in self.items if item.lane is WorkboardLane.EXPEDITE)

    @property
    def committed_case_ids(self) -> tuple[str, ...]:
        return tuple(item.case_id for item in self.items if item.lane is WorkboardLane.COMMITTED)

    @property
    def follow_up_case_ids(self) -> tuple[str, ...]:
        return tuple(item.case_id for item in self.items if item.lane is WorkboardLane.FOLLOW_UP)

    @property
    def watch_case_ids(self) -> tuple[str, ...]:
        return tuple(item.case_id for item in self.items if item.lane is WorkboardLane.WATCH)

    @property
    def due_now_case_ids(self) -> tuple[str, ...]:
        return tuple(item.case_id for item in self.items if item.status is WorkboardStatus.DUE_NOW)

    def to_dict(self) -> dict[str, object]:
        return {
            "workboard_id": self.workboard_id,
            "steward": self.steward.to_dict(),
            "items": [item.to_dict() for item in self.items],
            "board_signal": self.board_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "expedite_case_ids": list(self.expedite_case_ids),
            "committed_case_ids": list(self.committed_case_ids),
            "follow_up_case_ids": list(self.follow_up_case_ids),
            "watch_case_ids": list(self.watch_case_ids),
            "due_now_case_ids": list(self.due_now_case_ids),
        }


def _queue_for_directive(directive: StewardDirective) -> WorkboardQueue:
    return {
        StewardDirectiveType.STABILIZE: WorkboardQueue.STABILIZATION,
        StewardDirectiveType.GOVERN: WorkboardQueue.GOVERNANCE,
        StewardDirectiveType.ADAPT: WorkboardQueue.ADAPTATION,
        StewardDirectiveType.MONITOR: WorkboardQueue.MONITORING,
    }[directive.directive_type]


def _lane_for_directive(directive: StewardDirective) -> WorkboardLane:
    if directive.directive_type is StewardDirectiveType.STABILIZE:
        return WorkboardLane.EXPEDITE
    if directive.directive_type is StewardDirectiveType.GOVERN:
        return WorkboardLane.COMMITTED
    if directive.directive_type is StewardDirectiveType.ADAPT:
        return WorkboardLane.FOLLOW_UP
    return WorkboardLane.WATCH


def _status_for_directive(directive: StewardDirective) -> WorkboardStatus:
    if directive.directive_type is StewardDirectiveType.STABILIZE:
        return WorkboardStatus.DUE_NOW
    if directive.directive_type in {StewardDirectiveType.GOVERN, StewardDirectiveType.ADAPT}:
        return WorkboardStatus.SCHEDULED
    return WorkboardStatus.TRACKED


def _sla_hours_for_directive(directive: StewardDirective) -> int:
    return {
        StewardDirectiveType.STABILIZE: 4,
        StewardDirectiveType.GOVERN: 12,
        StewardDirectiveType.ADAPT: 24,
        StewardDirectiveType.MONITOR: 72,
    }[directive.directive_type]


def build_steward_workboard(
    steward: OperationsSteward | None = None,
    *,
    workboard_id: str = "steward-workboard",
) -> StewardWorkboard:
    """Build an operational workboard over steward directives."""

    resolved_steward = build_operations_steward(steward_id=f"{workboard_id}-steward") if steward is None else steward
    items = tuple(
        WorkboardItem(
            item_id=f"{workboard_id}-{directive.case_id}",
            case_id=directive.case_id,
            sequence=index,
            directive_type=directive.directive_type,
            queue=_queue_for_directive(directive),
            lane=_lane_for_directive(directive),
            status=_status_for_directive(directive),
            sla_hours=_sla_hours_for_directive(directive),
            evidence_refs=directive.evidence_refs,
            commitment_refs=directive.commitment_refs,
            summary=f"{directive.case_id} is queued in the { _queue_for_directive(directive).value } workboard queue.",
        )
        for index, directive in enumerate(resolved_steward.directives, start=1)
    )
    if not items:
        raise ValueError("steward workboard requires at least one item")

    severity = "info"
    status = "tracked-board"
    if any(item.lane is WorkboardLane.EXPEDITE for item in items):
        severity = "critical"
        status = "expedite-board"
    elif any(item.lane is WorkboardLane.COMMITTED for item in items):
        severity = "warning"
        status = "committed-board"

    board_signal = TelemetrySignal(
        signal_name="steward-workboard",
        boundary=resolved_steward.steward_signal.boundary,
        correlation_id=workboard_id,
        severity=severity,
        status=status,
        metrics={
            "item_count": float(len(items)),
            "expedite_count": float(len([item for item in items if item.lane is WorkboardLane.EXPEDITE])),
            "committed_count": float(len([item for item in items if item.lane is WorkboardLane.COMMITTED])),
            "follow_up_count": float(len([item for item in items if item.lane is WorkboardLane.FOLLOW_UP])),
            "watch_count": float(len([item for item in items if item.lane is WorkboardLane.WATCH])),
            "due_now_count": float(len([item for item in items if item.status is WorkboardStatus.DUE_NOW])),
        },
        labels={"workboard_id": workboard_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_steward.final_snapshot.runtime_stage,
        signals=(board_signal, resolved_steward.steward_signal, *resolved_steward.final_snapshot.signals),
        alerts=resolved_steward.final_snapshot.alerts,
        audit_entries=resolved_steward.final_snapshot.audit_entries,
        active_controls=resolved_steward.final_snapshot.active_controls,
    )
    return StewardWorkboard(
        workboard_id=workboard_id,
        steward=resolved_steward,
        items=items,
        board_signal=board_signal,
        final_snapshot=final_snapshot,
    )
