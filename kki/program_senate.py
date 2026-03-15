"""Program senate balancing charter clauses, programs, and executive orders."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .executive_watchtower import ExecutiveOrder, ExecutiveOrderMode, ExecutiveWatchStatus, ExecutiveWatchtower
from .intervention_charter import CharterStatus, InterventionCharter, InterventionClause, build_intervention_charter
from .program_controller import ProgramController, ProgramControllerStatus, ProgramDirective, ProgramTrack, ProgramTrackType
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class SenatePriority(str, Enum):
    """Priority posture used by the senate while balancing pressures."""

    CONSTITUTION_FIRST = "constitution-first"
    JOINT_REVIEW = "joint-review"
    PROGRAM_ADVANCE = "program-advance"


class SenateResolution(str, Enum):
    """Outcome reached by one senate seat."""

    VETO = "veto"
    NEGOTIATE = "negotiate"
    ENDORSE = "endorse"


class SenateBalanceStatus(str, Enum):
    """Balance state between charter, program, and executive pressure."""

    CONTESTED = "contested"
    BALANCED = "balanced"
    ALIGNED = "aligned"


@dataclass(frozen=True)
class SenateSeat:
    """One senate seat resolving one charter clause against program pressure."""

    seat_id: str
    sequence: int
    clause_id: str
    track_id: str
    order_id: str
    priority: SenatePriority
    resolution: SenateResolution
    balance_status: SenateBalanceStatus
    source_directive: ProgramDirective
    case_ids: tuple[str, ...]
    release_ready: bool
    tension_score: float
    consensus_score: float
    senate_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "seat_id", _non_empty(self.seat_id, field_name="seat_id"))
        object.__setattr__(self, "clause_id", _non_empty(self.clause_id, field_name="clause_id"))
        object.__setattr__(self, "track_id", _non_empty(self.track_id, field_name="track_id"))
        object.__setattr__(self, "order_id", _non_empty(self.order_id, field_name="order_id"))
        object.__setattr__(self, "tension_score", _clamp01(self.tension_score))
        object.__setattr__(self, "consensus_score", _clamp01(self.consensus_score))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "seat_id": self.seat_id,
            "sequence": self.sequence,
            "clause_id": self.clause_id,
            "track_id": self.track_id,
            "order_id": self.order_id,
            "priority": self.priority.value,
            "resolution": self.resolution.value,
            "balance_status": self.balance_status.value,
            "source_directive": self.source_directive.value,
            "case_ids": list(self.case_ids),
            "release_ready": self.release_ready,
            "tension_score": self.tension_score,
            "consensus_score": self.consensus_score,
            "senate_tags": list(self.senate_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class ProgramSenate:
    """Senate that balances charter clauses against program and executive priorities."""

    senate_id: str
    intervention_charter: InterventionCharter
    program_controller: ProgramController
    executive_watchtower: ExecutiveWatchtower
    seats: tuple[SenateSeat, ...]
    senate_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "senate_id", _non_empty(self.senate_id, field_name="senate_id"))

    @property
    def contested_seat_ids(self) -> tuple[str, ...]:
        return tuple(seat.seat_id for seat in self.seats if seat.balance_status is SenateBalanceStatus.CONTESTED)

    @property
    def balanced_seat_ids(self) -> tuple[str, ...]:
        return tuple(seat.seat_id for seat in self.seats if seat.balance_status is SenateBalanceStatus.BALANCED)

    @property
    def aligned_seat_ids(self) -> tuple[str, ...]:
        return tuple(seat.seat_id for seat in self.seats if seat.balance_status is SenateBalanceStatus.ALIGNED)

    def to_dict(self) -> dict[str, object]:
        return {
            "senate_id": self.senate_id,
            "intervention_charter": self.intervention_charter.to_dict(),
            "program_controller": self.program_controller.to_dict(),
            "executive_watchtower": self.executive_watchtower.to_dict(),
            "seats": [seat.to_dict() for seat in self.seats],
            "senate_signal": self.senate_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "contested_seat_ids": list(self.contested_seat_ids),
            "balanced_seat_ids": list(self.balanced_seat_ids),
            "aligned_seat_ids": list(self.aligned_seat_ids),
        }


def _track_type_for_clause(clause: InterventionClause) -> ProgramTrackType:
    return {
        CharterStatus.RESTRICTED: ProgramTrackType.RESILIENCE,
        CharterStatus.GUARDED: ProgramTrackType.GOVERNANCE,
        CharterStatus.ENABLED: ProgramTrackType.ROUTINE,
    }[clause.charter_status]


def _order_mode_for_clause(clause: InterventionClause) -> ExecutiveOrderMode:
    return {
        CharterStatus.RESTRICTED: ExecutiveOrderMode.EXECUTIVE_OVERRIDE,
        CharterStatus.GUARDED: ExecutiveOrderMode.GOVERNED_EXECUTION,
        CharterStatus.ENABLED: ExecutiveOrderMode.AUTONOMY_WINDOW,
    }[clause.charter_status]


def _priority_for_seat(clause: InterventionClause) -> SenatePriority:
    return {
        CharterStatus.RESTRICTED: SenatePriority.CONSTITUTION_FIRST,
        CharterStatus.GUARDED: SenatePriority.JOINT_REVIEW,
        CharterStatus.ENABLED: SenatePriority.PROGRAM_ADVANCE,
    }[clause.charter_status]


def _balance_status(clause: InterventionClause, track: ProgramTrack, order: ExecutiveOrder) -> SenateBalanceStatus:
    if (
        clause.charter_status is CharterStatus.RESTRICTED
        or track.status is ProgramControllerStatus.CRITICAL
        or order.watch_status is ExecutiveWatchStatus.LOCKED
    ):
        return SenateBalanceStatus.CONTESTED
    if (
        clause.charter_status is CharterStatus.GUARDED
        or track.status is ProgramControllerStatus.CONTROLLED
        or order.watch_status is ExecutiveWatchStatus.COMMANDING
    ):
        return SenateBalanceStatus.BALANCED
    return SenateBalanceStatus.ALIGNED


def _resolution(status: SenateBalanceStatus) -> SenateResolution:
    return {
        SenateBalanceStatus.CONTESTED: SenateResolution.VETO,
        SenateBalanceStatus.BALANCED: SenateResolution.NEGOTIATE,
        SenateBalanceStatus.ALIGNED: SenateResolution.ENDORSE,
    }[status]


def _tension_score(clause: InterventionClause, track: ProgramTrack, order: ExecutiveOrder) -> float:
    charter_pressure = max(clause.approval_floor, clause.intervention_score)
    operational_gap = abs(track.priority_score - order.command_budget)
    senate_gap = abs(charter_pressure - track.priority_score)
    return round(min(1.0, (operational_gap + senate_gap) / 2.0), 3)


def _consensus_score(
    clause: InterventionClause,
    track: ProgramTrack,
    order: ExecutiveOrder,
    status: SenateBalanceStatus,
) -> float:
    posture_bonus = {
        SenateBalanceStatus.CONTESTED: 0.0,
        SenateBalanceStatus.BALANCED: 0.08,
        SenateBalanceStatus.ALIGNED: 0.16,
    }[status]
    score = ((1.0 - _tension_score(clause, track, order)) + clause.intervention_score + order.command_budget) / 3.0
    return round(score + posture_bonus, 3)


def _resolve_governance_path(charter: InterventionCharter) -> tuple[ExecutiveWatchtower, ProgramController]:
    watchtower = (
        charter.guideline_compass.mandate_memory_store.course_corrector.scenario_chancery.portfolio_radar.mandate_card_deck.strategy_council.executive_watchtower
    )
    return watchtower, watchtower.program_controller


def build_program_senate(
    intervention_charter: InterventionCharter | None = None,
    *,
    senate_id: str = "program-senate",
) -> ProgramSenate:
    """Build the senate that balances charter clauses against program priorities."""

    resolved_charter = (
        build_intervention_charter(charter_id=f"{senate_id}-charter")
        if intervention_charter is None
        else intervention_charter
    )
    resolved_watchtower, resolved_controller = _resolve_governance_path(resolved_charter)
    tracks_by_type = {track.track_type: track for track in resolved_controller.tracks}
    orders_by_mode = {order.mode: order for order in resolved_watchtower.orders}

    seats = tuple(
        SenateSeat(
            seat_id=f"{senate_id}-{clause.clause_id.removeprefix(f'{resolved_charter.charter_id}-')}",
            sequence=index,
            clause_id=clause.clause_id,
            track_id=tracks_by_type[_track_type_for_clause(clause)].track_id,
            order_id=orders_by_mode[_order_mode_for_clause(clause)].order_id,
            priority=_priority_for_seat(clause),
            resolution=_resolution(
                _balance_status(
                    clause,
                    tracks_by_type[_track_type_for_clause(clause)],
                    orders_by_mode[_order_mode_for_clause(clause)],
                )
            ),
            balance_status=_balance_status(
                clause,
                tracks_by_type[_track_type_for_clause(clause)],
                orders_by_mode[_order_mode_for_clause(clause)],
            ),
            source_directive=tracks_by_type[_track_type_for_clause(clause)].directive,
            case_ids=tuple(
                dict.fromkeys(
                    (
                        *clause.case_ids,
                        *tracks_by_type[_track_type_for_clause(clause)].case_ids,
                        *orders_by_mode[_order_mode_for_clause(clause)].case_ids,
                    )
                )
            ),
            release_ready=(
                clause.release_ready
                and orders_by_mode[_order_mode_for_clause(clause)].release_ready
                and _resolution(
                    _balance_status(
                        clause,
                        tracks_by_type[_track_type_for_clause(clause)],
                        orders_by_mode[_order_mode_for_clause(clause)],
                    )
                )
                is SenateResolution.ENDORSE
            ),
            tension_score=_tension_score(
                clause,
                tracks_by_type[_track_type_for_clause(clause)],
                orders_by_mode[_order_mode_for_clause(clause)],
            ),
            consensus_score=_consensus_score(
                clause,
                tracks_by_type[_track_type_for_clause(clause)],
                orders_by_mode[_order_mode_for_clause(clause)],
                _balance_status(
                    clause,
                    tracks_by_type[_track_type_for_clause(clause)],
                    orders_by_mode[_order_mode_for_clause(clause)],
                ),
            ),
            senate_tags=tuple(
                dict.fromkeys(
                    (
                        *clause.charter_tags,
                        *tracks_by_type[_track_type_for_clause(clause)].control_tags,
                        *orders_by_mode[_order_mode_for_clause(clause)].control_tags,
                        _priority_for_seat(clause).value,
                        _resolution(
                            _balance_status(
                                clause,
                                tracks_by_type[_track_type_for_clause(clause)],
                                orders_by_mode[_order_mode_for_clause(clause)],
                            )
                        ).value,
                        _balance_status(
                            clause,
                            tracks_by_type[_track_type_for_clause(clause)],
                            orders_by_mode[_order_mode_for_clause(clause)],
                        ).value,
                    )
                )
            ),
            summary=(
                f"{clause.clause_id} resolves as "
                f"{_resolution(_balance_status(clause, tracks_by_type[_track_type_for_clause(clause)], orders_by_mode[_order_mode_for_clause(clause)])).value} "
                f"between {tracks_by_type[_track_type_for_clause(clause)].track_type.value} and "
                f"{orders_by_mode[_order_mode_for_clause(clause)].mode.value}."
            ),
        )
        for index, clause in enumerate(resolved_charter.clauses, start=1)
    )
    if not seats:
        raise ValueError("program senate requires at least one seat")

    severity = "info"
    status = "senate-aligned"
    if any(seat.balance_status is SenateBalanceStatus.CONTESTED for seat in seats):
        severity = "critical"
        status = "senate-contested"
    elif any(seat.balance_status is SenateBalanceStatus.BALANCED for seat in seats):
        severity = "warning"
        status = "senate-balanced"

    senate_signal = TelemetrySignal(
        signal_name="program-senate",
        boundary=resolved_charter.charter_signal.boundary,
        correlation_id=senate_id,
        severity=severity,
        status=status,
        metrics={
            "seat_count": float(len(seats)),
            "contested_count": float(len([seat for seat in seats if seat.balance_status is SenateBalanceStatus.CONTESTED])),
            "balanced_count": float(len([seat for seat in seats if seat.balance_status is SenateBalanceStatus.BALANCED])),
            "aligned_count": float(len([seat for seat in seats if seat.balance_status is SenateBalanceStatus.ALIGNED])),
            "release_ready_count": float(len([seat for seat in seats if seat.release_ready])),
            "avg_consensus_score": round(sum(seat.consensus_score for seat in seats) / len(seats), 3),
        },
        labels={"senate_id": senate_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_charter.final_snapshot.runtime_stage,
        signals=(senate_signal, *resolved_charter.final_snapshot.signals),
        alerts=resolved_charter.final_snapshot.alerts,
        audit_entries=resolved_charter.final_snapshot.audit_entries,
        active_controls=resolved_charter.final_snapshot.active_controls,
    )
    return ProgramSenate(
        senate_id=senate_id,
        intervention_charter=resolved_charter,
        program_controller=resolved_controller,
        executive_watchtower=resolved_watchtower,
        seats=seats,
        senate_signal=senate_signal,
        final_snapshot=final_snapshot,
    )
