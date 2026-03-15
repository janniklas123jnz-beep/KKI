"""Directive consensus consolidating senate outcomes into top-level directives."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .program_senate import (
    ProgramSenate,
    SenateBalanceStatus,
    SenatePriority,
    SenateResolution,
    SenateSeat,
    build_program_senate,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class ConsensusDirectiveType(str, Enum):
    """Top-level directive type produced by the final consensus layer."""

    CONSTITUTIONAL_LOCK = "constitutional-lock"
    GOVERNED_COMPACT = "governed-compact"
    EXPANSION_ACCORD = "expansion-accord"


class ConsensusDirectiveStatus(str, Enum):
    """Status of one consolidated directive."""

    BINDING = "binding"
    NEGOTIATED = "negotiated"
    RATIFIED = "ratified"


class ConsensusMandate(str, Enum):
    """Mandate conveyed by the final directive."""

    HOLD = "hold"
    ALIGN = "align"
    RELEASE = "release"


@dataclass(frozen=True)
class ConsensusDirective:
    """One consolidated directive resolved from a senate seat."""

    directive_id: str
    sequence: int
    seat_id: str
    directive_type: ConsensusDirectiveType
    directive_status: ConsensusDirectiveStatus
    mandate: ConsensusMandate
    source_priority: SenatePriority
    case_ids: tuple[str, ...]
    release_ready: bool
    authority_score: float
    consensus_strength: float
    directive_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "directive_id", _non_empty(self.directive_id, field_name="directive_id"))
        object.__setattr__(self, "seat_id", _non_empty(self.seat_id, field_name="seat_id"))
        object.__setattr__(self, "authority_score", _clamp01(self.authority_score))
        object.__setattr__(self, "consensus_strength", _clamp01(self.consensus_strength))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "directive_id": self.directive_id,
            "sequence": self.sequence,
            "seat_id": self.seat_id,
            "directive_type": self.directive_type.value,
            "directive_status": self.directive_status.value,
            "mandate": self.mandate.value,
            "source_priority": self.source_priority.value,
            "case_ids": list(self.case_ids),
            "release_ready": self.release_ready,
            "authority_score": self.authority_score,
            "consensus_strength": self.consensus_strength,
            "directive_tags": list(self.directive_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class DirectiveConsensus:
    """Final consensus layer over senate seats."""

    consensus_id: str
    program_senate: ProgramSenate
    directives: tuple[ConsensusDirective, ...]
    consensus_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "consensus_id", _non_empty(self.consensus_id, field_name="consensus_id"))

    @property
    def binding_directive_ids(self) -> tuple[str, ...]:
        return tuple(
            directive.directive_id for directive in self.directives if directive.directive_status is ConsensusDirectiveStatus.BINDING
        )

    @property
    def negotiated_directive_ids(self) -> tuple[str, ...]:
        return tuple(
            directive.directive_id
            for directive in self.directives
            if directive.directive_status is ConsensusDirectiveStatus.NEGOTIATED
        )

    @property
    def ratified_directive_ids(self) -> tuple[str, ...]:
        return tuple(
            directive.directive_id for directive in self.directives if directive.directive_status is ConsensusDirectiveStatus.RATIFIED
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "consensus_id": self.consensus_id,
            "program_senate": self.program_senate.to_dict(),
            "directives": [directive.to_dict() for directive in self.directives],
            "consensus_signal": self.consensus_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "binding_directive_ids": list(self.binding_directive_ids),
            "negotiated_directive_ids": list(self.negotiated_directive_ids),
            "ratified_directive_ids": list(self.ratified_directive_ids),
        }


def _directive_type_for_seat(seat: SenateSeat) -> ConsensusDirectiveType:
    return {
        SenateBalanceStatus.CONTESTED: ConsensusDirectiveType.CONSTITUTIONAL_LOCK,
        SenateBalanceStatus.BALANCED: ConsensusDirectiveType.GOVERNED_COMPACT,
        SenateBalanceStatus.ALIGNED: ConsensusDirectiveType.EXPANSION_ACCORD,
    }[seat.balance_status]


def _directive_status_for_seat(seat: SenateSeat) -> ConsensusDirectiveStatus:
    return {
        SenateResolution.VETO: ConsensusDirectiveStatus.BINDING,
        SenateResolution.NEGOTIATE: ConsensusDirectiveStatus.NEGOTIATED,
        SenateResolution.ENDORSE: ConsensusDirectiveStatus.RATIFIED,
    }[seat.resolution]


def _mandate_for_seat(seat: SenateSeat) -> ConsensusMandate:
    return {
        SenateResolution.VETO: ConsensusMandate.HOLD,
        SenateResolution.NEGOTIATE: ConsensusMandate.ALIGN,
        SenateResolution.ENDORSE: ConsensusMandate.RELEASE,
    }[seat.resolution]


def _authority_score(seat: SenateSeat) -> float:
    if seat.balance_status is SenateBalanceStatus.CONTESTED:
        return 1.0
    if seat.balance_status is SenateBalanceStatus.BALANCED:
        return max(0.67, seat.consensus_score)
    return max(0.6, seat.consensus_score)


def _consensus_strength(seat: SenateSeat) -> float:
    posture_bonus = {
        SenateBalanceStatus.CONTESTED: 0.08,
        SenateBalanceStatus.BALANCED: 0.04,
        SenateBalanceStatus.ALIGNED: 0.12,
    }[seat.balance_status]
    return round(((1.0 - seat.tension_score) + seat.consensus_score) / 2.0 + posture_bonus, 3)


def build_directive_consensus(
    program_senate: ProgramSenate | None = None,
    *,
    consensus_id: str = "directive-consensus",
) -> DirectiveConsensus:
    """Build the final directive consensus from senate outcomes."""

    resolved_senate = build_program_senate(senate_id=f"{consensus_id}-senate") if program_senate is None else program_senate
    directives = tuple(
        ConsensusDirective(
            directive_id=f"{consensus_id}-{seat.seat_id.removeprefix(f'{resolved_senate.senate_id}-')}",
            sequence=index,
            seat_id=seat.seat_id,
            directive_type=_directive_type_for_seat(seat),
            directive_status=_directive_status_for_seat(seat),
            mandate=_mandate_for_seat(seat),
            source_priority=seat.priority,
            case_ids=seat.case_ids,
            release_ready=seat.release_ready and _directive_status_for_seat(seat) is ConsensusDirectiveStatus.RATIFIED,
            authority_score=_authority_score(seat),
            consensus_strength=_consensus_strength(seat),
            directive_tags=tuple(
                dict.fromkeys(
                    (
                        *seat.senate_tags,
                        _directive_type_for_seat(seat).value,
                        _directive_status_for_seat(seat).value,
                        _mandate_for_seat(seat).value,
                    )
                )
            ),
            summary=(
                f"{seat.seat_id} consolidates into {_directive_type_for_seat(seat).value} "
                f"with {_directive_status_for_seat(seat).value} mandate {_mandate_for_seat(seat).value}."
            ),
        )
        for index, seat in enumerate(resolved_senate.seats, start=1)
    )
    if not directives:
        raise ValueError("directive consensus requires at least one directive")

    severity = "info"
    status = "consensus-ratified"
    if any(directive.directive_status is ConsensusDirectiveStatus.BINDING for directive in directives):
        severity = "critical"
        status = "consensus-binding"
    elif any(directive.directive_status is ConsensusDirectiveStatus.NEGOTIATED for directive in directives):
        severity = "warning"
        status = "consensus-negotiated"

    consensus_signal = TelemetrySignal(
        signal_name="directive-consensus",
        boundary=resolved_senate.senate_signal.boundary,
        correlation_id=consensus_id,
        severity=severity,
        status=status,
        metrics={
            "directive_count": float(len(directives)),
            "binding_count": float(
                len([directive for directive in directives if directive.directive_status is ConsensusDirectiveStatus.BINDING])
            ),
            "negotiated_count": float(
                len([directive for directive in directives if directive.directive_status is ConsensusDirectiveStatus.NEGOTIATED])
            ),
            "ratified_count": float(
                len([directive for directive in directives if directive.directive_status is ConsensusDirectiveStatus.RATIFIED])
            ),
            "release_ready_count": float(len([directive for directive in directives if directive.release_ready])),
            "avg_consensus_strength": round(
                sum(directive.consensus_strength for directive in directives) / len(directives),
                3,
            ),
        },
        labels={"consensus_id": consensus_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_senate.final_snapshot.runtime_stage,
        signals=(consensus_signal, *resolved_senate.final_snapshot.signals),
        alerts=resolved_senate.final_snapshot.alerts,
        audit_entries=resolved_senate.final_snapshot.audit_entries,
        active_controls=resolved_senate.final_snapshot.active_controls,
    )
    return DirectiveConsensus(
        consensus_id=consensus_id,
        program_senate=resolved_senate,
        directives=directives,
        consensus_signal=consensus_signal,
        final_snapshot=final_snapshot,
    )
