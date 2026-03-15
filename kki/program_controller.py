"""Program-wide controller over workboards, outcomes, exceptions, and federation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .exception_register import ExceptionRegister, build_exception_register
from .federation_coordination import (
    FederationAlignmentStatus,
    FederationCoordination,
    FederationDomain,
    build_federation_coordination,
)
from .outcome_ledger import OutcomeLedger, OutcomeStatus, build_outcome_ledger
from .steward_workboard import StewardWorkboard, WorkboardLane, WorkboardQueue, build_steward_workboard
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class ProgramTrackType(str, Enum):
    """Program-level steering lanes derived from federated operations."""

    RESILIENCE = "resilience-program"
    GOVERNANCE = "governance-program"
    ROUTINE = "routine-program"


class ProgramDirective(str, Enum):
    """Top-level steering directive for one program track."""

    INTERVENE = "intervene"
    STEER = "steer"
    SCALE = "scale"


class ProgramControllerStatus(str, Enum):
    """Operational state of a program track."""

    CRITICAL = "critical"
    CONTROLLED = "controlled"
    SCALING = "scaling"


@dataclass(frozen=True)
class ProgramTrack:
    """Program-wide steering aggregate over multiple cases."""

    track_id: str
    sequence: int
    track_type: ProgramTrackType
    domain: FederationDomain
    directive: ProgramDirective
    status: ProgramControllerStatus
    case_ids: tuple[str, ...]
    work_queues: tuple[str, ...]
    outcome_statuses: tuple[str, ...]
    control_tags: tuple[str, ...]
    priority_score: float
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "track_id", _non_empty(self.track_id, field_name="track_id"))
        object.__setattr__(self, "priority_score", _clamp01(self.priority_score))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "track_id": self.track_id,
            "sequence": self.sequence,
            "track_type": self.track_type.value,
            "domain": self.domain.value,
            "directive": self.directive.value,
            "status": self.status.value,
            "case_ids": list(self.case_ids),
            "work_queues": list(self.work_queues),
            "outcome_statuses": list(self.outcome_statuses),
            "control_tags": list(self.control_tags),
            "priority_score": self.priority_score,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class ProgramController:
    """Program-wide steering logic over federated operational signals."""

    controller_id: str
    workboard: StewardWorkboard
    outcome_ledger: OutcomeLedger
    exception_register: ExceptionRegister
    federation_coordination: FederationCoordination
    tracks: tuple[ProgramTrack, ...]
    controller_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "controller_id", _non_empty(self.controller_id, field_name="controller_id"))

    @property
    def critical_track_ids(self) -> tuple[str, ...]:
        return tuple(track.track_id for track in self.tracks if track.status is ProgramControllerStatus.CRITICAL)

    @property
    def controlled_track_ids(self) -> tuple[str, ...]:
        return tuple(track.track_id for track in self.tracks if track.status is ProgramControllerStatus.CONTROLLED)

    @property
    def scaling_track_ids(self) -> tuple[str, ...]:
        return tuple(track.track_id for track in self.tracks if track.status is ProgramControllerStatus.SCALING)

    def to_dict(self) -> dict[str, object]:
        return {
            "controller_id": self.controller_id,
            "workboard": self.workboard.to_dict(),
            "outcome_ledger": self.outcome_ledger.to_dict(),
            "exception_register": self.exception_register.to_dict(),
            "federation_coordination": self.federation_coordination.to_dict(),
            "tracks": [track.to_dict() for track in self.tracks],
            "controller_signal": self.controller_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "critical_track_ids": list(self.critical_track_ids),
            "controlled_track_ids": list(self.controlled_track_ids),
            "scaling_track_ids": list(self.scaling_track_ids),
        }


def _program_spec_for_domain(
    domain: FederationDomain,
    alignment_status: FederationAlignmentStatus,
) -> tuple[ProgramTrackType, ProgramDirective, ProgramControllerStatus]:
    if domain is FederationDomain.RESILIENCE:
        return (
            ProgramTrackType.RESILIENCE,
            ProgramDirective.INTERVENE,
            ProgramControllerStatus.CRITICAL if alignment_status is FederationAlignmentStatus.ESCALATED else ProgramControllerStatus.CONTROLLED,
        )
    if domain is FederationDomain.GOVERNANCE:
        return (ProgramTrackType.GOVERNANCE, ProgramDirective.STEER, ProgramControllerStatus.CONTROLLED)
    return (ProgramTrackType.ROUTINE, ProgramDirective.SCALE, ProgramControllerStatus.SCALING)


def _priority_score(
    domain: FederationDomain,
    alignment_status: FederationAlignmentStatus,
    exception_count: int,
    avg_risk: float,
) -> float:
    base = {
        FederationDomain.RESILIENCE: 0.72,
        FederationDomain.GOVERNANCE: 0.54,
        FederationDomain.AUTONOMY: 0.28,
    }[domain]
    alignment_bonus = {
        FederationAlignmentStatus.ESCALATED: 0.16,
        FederationAlignmentStatus.HANDOFF_REQUIRED: 0.08,
        FederationAlignmentStatus.ALIGNED: 0.0,
    }[alignment_status]
    exception_bonus = min(0.12, exception_count * 0.04)
    return round(base + alignment_bonus + exception_bonus + (avg_risk * 0.05), 3)


def build_program_controller(
    workboard: StewardWorkboard | None = None,
    outcome_ledger: OutcomeLedger | None = None,
    exception_register: ExceptionRegister | None = None,
    federation_coordination: FederationCoordination | None = None,
    *,
    controller_id: str = "program-controller",
) -> ProgramController:
    """Build program-wide steering logic from workboards, outcomes, exceptions, and federation."""

    resolved_workboard = build_steward_workboard(workboard_id=f"{controller_id}-workboard") if workboard is None else workboard
    resolved_outcomes = build_outcome_ledger(ledger_id=f"{controller_id}-outcomes") if outcome_ledger is None else outcome_ledger
    resolved_exceptions = (
        build_exception_register(register_id=f"{controller_id}-exceptions") if exception_register is None else exception_register
    )
    resolved_federation = (
        build_federation_coordination(coordination_id=f"{controller_id}-federation")
        if federation_coordination is None
        else federation_coordination
    )

    workboard_by_case = {item.case_id: item for item in resolved_workboard.items}
    outcome_by_case = {item.case_id: item for item in resolved_outcomes.records}
    exception_case_ids = set(resolved_exceptions.policy_breach_case_ids + resolved_exceptions.unresolved_case_ids + resolved_exceptions.recurring_case_ids)

    tracks: list[ProgramTrack] = []
    for sequence, cell in enumerate(resolved_federation.cells, start=1):
        track_type, directive, status = _program_spec_for_domain(cell.domain, cell.alignment_status)
        tracks.append(
            ProgramTrack(
                track_id=f"{controller_id}-{cell.domain.value}",
                sequence=sequence,
                track_type=track_type,
                domain=cell.domain,
                directive=directive,
                status=status,
                case_ids=cell.case_ids,
                work_queues=tuple(
                    dict.fromkeys(workboard_by_case[case_id].queue.value for case_id in cell.case_ids if case_id in workboard_by_case)
                ),
                outcome_statuses=tuple(
                    dict.fromkeys(outcome_by_case[case_id].outcome_status.value for case_id in cell.case_ids if case_id in outcome_by_case)
                ),
                control_tags=cell.control_tags,
                priority_score=_priority_score(
                    cell.domain,
                    cell.alignment_status,
                    len([case_id for case_id in cell.case_ids if case_id in exception_case_ids]),
                    cell.shared_risk_score,
                ),
                summary=f"{track_type.value} governs {len(cell.case_ids)} case(s) under {directive.value} steering.",
            )
        )
    resolved_tracks = tuple(tracks)
    if not resolved_tracks:
        raise ValueError("program controller requires at least one track")

    severity = "info"
    status = "program-scaling"
    if any(track.status is ProgramControllerStatus.CRITICAL for track in resolved_tracks):
        severity = "critical"
        status = "program-critical"
    elif any(track.status is ProgramControllerStatus.CONTROLLED for track in resolved_tracks):
        severity = "warning"
        status = "program-controlled"

    controller_signal = TelemetrySignal(
        signal_name="program-controller",
        boundary=resolved_federation.coordination_signal.boundary,
        correlation_id=controller_id,
        severity=severity,
        status=status,
        metrics={
            "track_count": float(len(resolved_tracks)),
            "critical_count": float(len([track for track in resolved_tracks if track.status is ProgramControllerStatus.CRITICAL])),
            "controlled_count": float(len([track for track in resolved_tracks if track.status is ProgramControllerStatus.CONTROLLED])),
            "scaling_count": float(len([track for track in resolved_tracks if track.status is ProgramControllerStatus.SCALING])),
            "avg_priority": round(sum(track.priority_score for track in resolved_tracks) / len(resolved_tracks), 3),
        },
        labels={"controller_id": controller_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_federation.final_snapshot.runtime_stage,
        signals=(
            controller_signal,
            resolved_workboard.board_signal,
            resolved_outcomes.ledger_signal,
            resolved_exceptions.register_signal,
            resolved_federation.coordination_signal,
            *resolved_federation.final_snapshot.signals,
        ),
        alerts=resolved_federation.final_snapshot.alerts,
        audit_entries=resolved_federation.final_snapshot.audit_entries,
        active_controls=resolved_federation.final_snapshot.active_controls,
    )
    return ProgramController(
        controller_id=controller_id,
        workboard=resolved_workboard,
        outcome_ledger=resolved_outcomes,
        exception_register=resolved_exceptions,
        federation_coordination=resolved_federation,
        tracks=resolved_tracks,
        controller_signal=controller_signal,
        final_snapshot=final_snapshot,
    )
