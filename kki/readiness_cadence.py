"""Recurring readiness cadence over continuous readiness cycles."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .continuous_readiness import (
    ContinuousReadinessCycle,
    ContinuousReadinessIteration,
    ContinuousReadinessStatus,
    build_continuous_readiness_cycle,
)
from .module_boundaries import ModuleBoundaryName
from .portfolio_optimizer import PortfolioAction
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


class ReadinessCadenceTrigger(str, Enum):
    """Deterministic triggers that open the next readiness window."""

    CONTAINMENT = "containment"
    RECOVERY = "recovery"
    GOVERNANCE = "governance"
    PROMOTION = "promotion"
    OBSERVATION = "observation"


class ReadinessCadenceWindow(str, Enum):
    """Fixed cadence windows for recurring readiness follow-up."""

    IMMEDIATE = "immediate"
    CURRENT = "current"
    NEXT = "next"
    ROUTINE = "routine"


class ReadinessCadenceStatus(str, Enum):
    """High-level cadence state for one case."""

    ESCALATED = "escalated"
    REVIEW_REQUIRED = "review-required"
    STEADY = "steady"


@dataclass(frozen=True)
class ReadinessCadenceEntry:
    """Scheduled cadence view for one readiness case."""

    cadence_entry_id: str
    case_id: str
    sequence: int
    trigger: ReadinessCadenceTrigger
    window: ReadinessCadenceWindow
    cadence_status: ReadinessCadenceStatus
    owner: ModuleBoundaryName
    due_cycle: int
    next_review_status: str
    target_status: str
    release_candidate: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "cadence_entry_id", _non_empty(self.cadence_entry_id, field_name="cadence_entry_id"))
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))
        object.__setattr__(self, "next_review_status", _non_empty(self.next_review_status, field_name="next_review_status"))
        object.__setattr__(self, "target_status", _non_empty(self.target_status, field_name="target_status"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.due_cycle < 1:
            raise ValueError("due_cycle must be positive")

    def to_dict(self) -> dict[str, object]:
        return {
            "cadence_entry_id": self.cadence_entry_id,
            "case_id": self.case_id,
            "sequence": self.sequence,
            "trigger": self.trigger.value,
            "window": self.window.value,
            "cadence_status": self.cadence_status.value,
            "owner": self.owner.value,
            "due_cycle": self.due_cycle,
            "next_review_status": self.next_review_status,
            "target_status": self.target_status,
            "release_candidate": self.release_candidate,
        }


@dataclass(frozen=True)
class ReadinessCadence:
    """Recurring cadence plan derived from continuous readiness state."""

    cadence_id: str
    cycle: ContinuousReadinessCycle
    entries: tuple[ReadinessCadenceEntry, ...]
    cadence_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "cadence_id", _non_empty(self.cadence_id, field_name="cadence_id"))

    @property
    def immediate_case_ids(self) -> tuple[str, ...]:
        return tuple(entry.case_id for entry in self.entries if entry.window is ReadinessCadenceWindow.IMMEDIATE)

    @property
    def current_window_case_ids(self) -> tuple[str, ...]:
        return tuple(entry.case_id for entry in self.entries if entry.window is ReadinessCadenceWindow.CURRENT)

    @property
    def next_window_case_ids(self) -> tuple[str, ...]:
        return tuple(entry.case_id for entry in self.entries if entry.window is ReadinessCadenceWindow.NEXT)

    @property
    def routine_case_ids(self) -> tuple[str, ...]:
        return tuple(entry.case_id for entry in self.entries if entry.window is ReadinessCadenceWindow.ROUTINE)

    @property
    def escalated_case_ids(self) -> tuple[str, ...]:
        return tuple(entry.case_id for entry in self.entries if entry.cadence_status is ReadinessCadenceStatus.ESCALATED)

    @property
    def review_required_case_ids(self) -> tuple[str, ...]:
        return tuple(
            entry.case_id for entry in self.entries if entry.cadence_status is ReadinessCadenceStatus.REVIEW_REQUIRED
        )

    @property
    def focus_case_ids(self) -> tuple[str, ...]:
        return tuple(entry.case_id for entry in self.entries if entry.due_cycle <= 2)

    def to_dict(self) -> dict[str, object]:
        return {
            "cadence_id": self.cadence_id,
            "cycle": self.cycle.to_dict(),
            "entries": [entry.to_dict() for entry in self.entries],
            "cadence_signal": self.cadence_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "immediate_case_ids": list(self.immediate_case_ids),
            "current_window_case_ids": list(self.current_window_case_ids),
            "next_window_case_ids": list(self.next_window_case_ids),
            "routine_case_ids": list(self.routine_case_ids),
            "escalated_case_ids": list(self.escalated_case_ids),
            "review_required_case_ids": list(self.review_required_case_ids),
            "focus_case_ids": list(self.focus_case_ids),
        }


def _trigger_for_iteration(iteration: ContinuousReadinessIteration) -> ReadinessCadenceTrigger:
    if iteration.recommended_action is PortfolioAction.CONTAIN:
        return ReadinessCadenceTrigger.CONTAINMENT
    if iteration.recommended_action is PortfolioAction.RECOVER:
        return ReadinessCadenceTrigger.RECOVERY
    if iteration.recommended_action is PortfolioAction.APPROVE:
        return ReadinessCadenceTrigger.GOVERNANCE
    if iteration.recommended_action is PortfolioAction.ADVANCE:
        return ReadinessCadenceTrigger.PROMOTION
    return ReadinessCadenceTrigger.OBSERVATION


def _window_for_iteration(iteration: ContinuousReadinessIteration) -> tuple[ReadinessCadenceWindow, int]:
    if iteration.status is ContinuousReadinessStatus.BLOCKED:
        return (ReadinessCadenceWindow.IMMEDIATE, 1)
    if iteration.recommended_action in {PortfolioAction.RECOVER, PortfolioAction.APPROVE}:
        return (ReadinessCadenceWindow.CURRENT, 2)
    if iteration.recommended_action is PortfolioAction.ADVANCE:
        return (ReadinessCadenceWindow.NEXT, 3)
    return (ReadinessCadenceWindow.ROUTINE, 4)


def _cadence_status_for_iteration(iteration: ContinuousReadinessIteration) -> ReadinessCadenceStatus:
    if iteration.status is ContinuousReadinessStatus.BLOCKED:
        return ReadinessCadenceStatus.ESCALATED
    if iteration.status is ContinuousReadinessStatus.ATTENTION:
        return ReadinessCadenceStatus.REVIEW_REQUIRED
    return ReadinessCadenceStatus.STEADY


def _entry_for_iteration(cadence_id: str, iteration: ContinuousReadinessIteration) -> ReadinessCadenceEntry:
    window, due_cycle = _window_for_iteration(iteration)
    return ReadinessCadenceEntry(
        cadence_entry_id=f"{cadence_id}-{iteration.case_id}",
        case_id=iteration.case_id,
        sequence=iteration.sequence,
        trigger=_trigger_for_iteration(iteration),
        window=window,
        cadence_status=_cadence_status_for_iteration(iteration),
        owner=iteration.owner,
        due_cycle=due_cycle,
        next_review_status=iteration.next_review_status,
        target_status=iteration.target_status,
        release_candidate=iteration.release_candidate,
    )


def build_readiness_cadence(
    cycle: ContinuousReadinessCycle | None = None,
    *,
    cadence_id: str = "readiness-cadence",
) -> ReadinessCadence:
    """Build recurring cadence windows and triggers from the continuous readiness loop."""

    resolved_cycle = build_continuous_readiness_cycle(cycle_id=f"{cadence_id}-cycle") if cycle is None else cycle
    entries = tuple(_entry_for_iteration(cadence_id, iteration) for iteration in resolved_cycle.iterations)
    if not entries:
        raise ValueError("readiness cadence requires at least one entry")

    severity = "info"
    status = ReadinessCadenceStatus.STEADY.value
    if any(entry.cadence_status is ReadinessCadenceStatus.ESCALATED for entry in entries):
        severity = "critical"
        status = ReadinessCadenceStatus.ESCALATED.value
    elif any(entry.cadence_status is ReadinessCadenceStatus.REVIEW_REQUIRED for entry in entries):
        severity = "warning"
        status = ReadinessCadenceStatus.REVIEW_REQUIRED.value

    cadence_signal = TelemetrySignal(
        signal_name="readiness-cadence",
        boundary=resolved_cycle.cycle_signal.boundary,
        correlation_id=cadence_id,
        severity=severity,
        status=status,
        metrics={
            "entry_count": float(len(entries)),
            "immediate_count": float(len([entry for entry in entries if entry.window is ReadinessCadenceWindow.IMMEDIATE])),
            "current_count": float(len([entry for entry in entries if entry.window is ReadinessCadenceWindow.CURRENT])),
            "next_count": float(len([entry for entry in entries if entry.window is ReadinessCadenceWindow.NEXT])),
            "routine_count": float(len([entry for entry in entries if entry.window is ReadinessCadenceWindow.ROUTINE])),
            "escalated_count": float(len([entry for entry in entries if entry.cadence_status is ReadinessCadenceStatus.ESCALATED])),
            "review_required_count": float(
                len([entry for entry in entries if entry.cadence_status is ReadinessCadenceStatus.REVIEW_REQUIRED])
            ),
            "steady_count": float(len([entry for entry in entries if entry.cadence_status is ReadinessCadenceStatus.STEADY])),
        },
        labels={"cadence_id": cadence_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_cycle.final_snapshot.runtime_stage,
        signals=(cadence_signal, resolved_cycle.cycle_signal, *resolved_cycle.final_snapshot.signals),
        alerts=resolved_cycle.final_snapshot.alerts,
        audit_entries=resolved_cycle.final_snapshot.audit_entries,
        active_controls=resolved_cycle.final_snapshot.active_controls,
    )
    return ReadinessCadence(
        cadence_id=cadence_id,
        cycle=resolved_cycle,
        entries=entries,
        cadence_signal=cadence_signal,
        final_snapshot=final_snapshot,
    )
