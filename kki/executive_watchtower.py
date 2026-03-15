"""Executive watchtower over steward, program, and constitutional control layers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .operating_constitution import (
    ConstitutionalAuthority,
    OperatingConstitution,
    build_operating_constitution,
)
from .operations_cockpit import CockpitEntry, CockpitStatus, OperationsCockpit, build_operations_cockpit
from .program_controller import (
    ProgramController,
    ProgramControllerStatus,
    ProgramDirective,
    ProgramTrack,
    ProgramTrackType,
    build_program_controller,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class ExecutiveOrderMode(str, Enum):
    """Execution mode commanded by the executive watchtower."""

    EXECUTIVE_OVERRIDE = "executive-override"
    GOVERNED_EXECUTION = "governed-execution"
    AUTONOMY_WINDOW = "autonomy-window"


class ExecutiveWatchStatus(str, Enum):
    """High-level leadership state for an executive order."""

    LOCKED = "locked"
    COMMANDING = "commanding"
    READY = "ready"


@dataclass(frozen=True)
class ExecutiveOrder:
    """Top-level order for one controlled program track."""

    order_id: str
    sequence: int
    track_id: str
    track_type: ProgramTrackType
    directive: ProgramDirective
    authority: ConstitutionalAuthority
    mode: ExecutiveOrderMode
    watch_status: ExecutiveWatchStatus
    case_ids: tuple[str, ...]
    release_ready: bool
    command_budget: float
    escalation_window: int
    control_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "order_id", _non_empty(self.order_id, field_name="order_id"))
        object.__setattr__(self, "track_id", _non_empty(self.track_id, field_name="track_id"))
        object.__setattr__(self, "command_budget", _clamp01(self.command_budget))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.escalation_window < 1:
            raise ValueError("escalation_window must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "order_id": self.order_id,
            "sequence": self.sequence,
            "track_id": self.track_id,
            "track_type": self.track_type.value,
            "directive": self.directive.value,
            "authority": self.authority.value,
            "mode": self.mode.value,
            "watch_status": self.watch_status.value,
            "case_ids": list(self.case_ids),
            "release_ready": self.release_ready,
            "command_budget": self.command_budget,
            "escalation_window": self.escalation_window,
            "control_tags": list(self.control_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class ExecutiveWatchtower:
    """Top-level executive watchtower over programs and constitutional articles."""

    watchtower_id: str
    program_controller: ProgramController
    operating_constitution: OperatingConstitution
    operations_cockpit: OperationsCockpit
    orders: tuple[ExecutiveOrder, ...]
    watchtower_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "watchtower_id", _non_empty(self.watchtower_id, field_name="watchtower_id"))

    @property
    def locked_order_ids(self) -> tuple[str, ...]:
        return tuple(order.order_id for order in self.orders if order.watch_status is ExecutiveWatchStatus.LOCKED)

    @property
    def commanding_order_ids(self) -> tuple[str, ...]:
        return tuple(order.order_id for order in self.orders if order.watch_status is ExecutiveWatchStatus.COMMANDING)

    @property
    def ready_order_ids(self) -> tuple[str, ...]:
        return tuple(order.order_id for order in self.orders if order.watch_status is ExecutiveWatchStatus.READY)

    def to_dict(self) -> dict[str, object]:
        return {
            "watchtower_id": self.watchtower_id,
            "program_controller": self.program_controller.to_dict(),
            "operating_constitution": self.operating_constitution.to_dict(),
            "operations_cockpit": self.operations_cockpit.to_dict(),
            "orders": [order.to_dict() for order in self.orders],
            "watchtower_signal": self.watchtower_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "locked_order_ids": list(self.locked_order_ids),
            "commanding_order_ids": list(self.commanding_order_ids),
            "ready_order_ids": list(self.ready_order_ids),
        }


def _mode_for_authority(authority: ConstitutionalAuthority) -> ExecutiveOrderMode:
    return {
        ConstitutionalAuthority.STEWARD: ExecutiveOrderMode.EXECUTIVE_OVERRIDE,
        ConstitutionalAuthority.GOVERNANCE: ExecutiveOrderMode.GOVERNED_EXECUTION,
        ConstitutionalAuthority.AUTONOMY: ExecutiveOrderMode.AUTONOMY_WINDOW,
    }[authority]


def _watch_status(
    track: ProgramTrack,
    cockpit_entries: tuple[CockpitEntry, ...],
) -> ExecutiveWatchStatus:
    if any(entry.status is CockpitStatus.CRITICAL or entry.blocked_release for entry in cockpit_entries):
        return ExecutiveWatchStatus.LOCKED
    if track.status is ProgramControllerStatus.CONTROLLED or any(entry.status is CockpitStatus.ATTENTION for entry in cockpit_entries):
        return ExecutiveWatchStatus.COMMANDING
    return ExecutiveWatchStatus.READY


def _release_ready(
    track: ProgramTrack,
    authority: ConstitutionalAuthority,
    cockpit_entries: tuple[CockpitEntry, ...],
) -> bool:
    if not cockpit_entries:
        return False
    if any(entry.blocked_release or entry.status is CockpitStatus.CRITICAL for entry in cockpit_entries):
        return False
    if authority is ConstitutionalAuthority.AUTONOMY:
        return _watch_status(track, cockpit_entries) is ExecutiveWatchStatus.READY
    return all(entry.release_ready for entry in cockpit_entries)


def build_executive_watchtower(
    program_controller: ProgramController | None = None,
    operating_constitution: OperatingConstitution | None = None,
    operations_cockpit: OperationsCockpit | None = None,
    *,
    watchtower_id: str = "executive-watchtower",
) -> ExecutiveWatchtower:
    """Build the executive watchtower as the top leadership layer."""

    resolved_controller = (
        build_program_controller(controller_id=f"{watchtower_id}-controller")
        if program_controller is None
        else program_controller
    )
    resolved_constitution = (
        build_operating_constitution(
            program_controller=resolved_controller,
            constitution_id=f"{watchtower_id}-constitution",
        )
        if operating_constitution is None
        else operating_constitution
    )
    resolved_cockpit = (
        build_operations_cockpit(cockpit_id=f"{watchtower_id}-cockpit")
        if operations_cockpit is None
        else operations_cockpit
    )
    article_by_track = {article.track_id: article for article in resolved_constitution.articles}
    cockpit_by_case = {entry.case_id: entry for entry in resolved_cockpit.entries}

    orders = tuple(
        ExecutiveOrder(
            order_id=f"{watchtower_id}-{track.track_type.value}",
            sequence=index,
            track_id=track.track_id,
            track_type=track.track_type,
            directive=track.directive,
            authority=article_by_track[track.track_id].authority,
            mode=_mode_for_authority(article_by_track[track.track_id].authority),
            watch_status=_watch_status(
                track,
                tuple(cockpit_by_case[case_id] for case_id in track.case_ids if case_id in cockpit_by_case),
            ),
            case_ids=track.case_ids,
            release_ready=_release_ready(
                track,
                article_by_track[track.track_id].authority,
                tuple(cockpit_by_case[case_id] for case_id in track.case_ids if case_id in cockpit_by_case),
            ),
            command_budget=article_by_track[track.track_id].budget_ceiling,
            escalation_window=article_by_track[track.track_id].escalation_limit,
            control_tags=tuple(
                dict.fromkeys(
                    (
                        *track.control_tags,
                        *article_by_track[track.track_id].control_tags,
                    )
                )
            ),
            summary=(
                f"{track.track_type.value} is commanded in { _mode_for_authority(article_by_track[track.track_id].authority).value } "
                f"with {_watch_status(track, tuple(cockpit_by_case[case_id] for case_id in track.case_ids if case_id in cockpit_by_case)).value} watch status."
            ),
        )
        for index, track in enumerate(resolved_controller.tracks, start=1)
    )
    if not orders:
        raise ValueError("executive watchtower requires at least one order")

    severity = "info"
    status = "executive-ready"
    if any(order.watch_status is ExecutiveWatchStatus.LOCKED for order in orders):
        severity = "critical"
        status = "executive-locked"
    elif any(order.watch_status is ExecutiveWatchStatus.COMMANDING for order in orders):
        severity = "warning"
        status = "executive-commanding"

    watchtower_signal = TelemetrySignal(
        signal_name="executive-watchtower",
        boundary=resolved_controller.controller_signal.boundary,
        correlation_id=watchtower_id,
        severity=severity,
        status=status,
        metrics={
            "order_count": float(len(orders)),
            "locked_count": float(len([order for order in orders if order.watch_status is ExecutiveWatchStatus.LOCKED])),
            "commanding_count": float(
                len([order for order in orders if order.watch_status is ExecutiveWatchStatus.COMMANDING])
            ),
            "ready_count": float(len([order for order in orders if order.watch_status is ExecutiveWatchStatus.READY])),
            "release_ready_count": float(len([order for order in orders if order.release_ready])),
        },
        labels={"watchtower_id": watchtower_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_controller.final_snapshot.runtime_stage,
        signals=(
            watchtower_signal,
            resolved_controller.controller_signal,
            resolved_constitution.constitution_signal,
            resolved_cockpit.cockpit_signal,
            *resolved_controller.final_snapshot.signals,
        ),
        alerts=resolved_controller.final_snapshot.alerts,
        audit_entries=resolved_controller.final_snapshot.audit_entries,
        active_controls=resolved_controller.final_snapshot.active_controls,
    )
    return ExecutiveWatchtower(
        watchtower_id=watchtower_id,
        program_controller=resolved_controller,
        operating_constitution=resolved_constitution,
        operations_cockpit=resolved_cockpit,
        orders=orders,
        watchtower_signal=watchtower_signal,
        final_snapshot=final_snapshot,
    )
