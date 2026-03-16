"""Leitstern doctrine condensing diplomacy channels into durable principles."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .consensus_diplomacy import (
    ConsensusDiplomacy,
    DiplomacyChannel,
    DiplomacyPath,
    DiplomacyStatus,
    build_consensus_diplomacy,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class DoctrinePrinciple(str, Enum):
    """Durable Leitstern principle formed from diplomatic reconciliation."""

    BOUNDARY_PRIMACY = "boundary-primacy"
    GOVERNED_ALIGNMENT = "governed-alignment"
    EXPANSION_DISCIPLINE = "expansion-discipline"


class DoctrineScope(str, Enum):
    """Institutional scope in which one doctrine clause applies."""

    STEWARD_CANON = "steward-canon"
    GOVERNANCE_CANON = "governance-canon"
    AUTONOMY_CANON = "autonomy-canon"


class DoctrineStatus(str, Enum):
    """Current level of doctrinal consolidation."""

    GUARDED = "guarded"
    ADOPTED = "adopted"
    ENSHRINED = "enshrined"


@dataclass(frozen=True)
class DoctrineClause:
    """One durable doctrine clause derived from a diplomacy channel."""

    clause_id: str
    sequence: int
    source_diplomacy_id: str
    principle: DoctrinePrinciple
    doctrine_scope: DoctrineScope
    doctrine_status: DoctrineStatus
    case_ids: tuple[str, ...]
    release_ready: bool
    doctrine_strength: float
    doctrine_window: int
    doctrine_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "clause_id", _non_empty(self.clause_id, field_name="clause_id"))
        object.__setattr__(
            self,
            "source_diplomacy_id",
            _non_empty(self.source_diplomacy_id, field_name="source_diplomacy_id"),
        )
        object.__setattr__(self, "doctrine_strength", _clamp01(self.doctrine_strength))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.doctrine_window < 1:
            raise ValueError("doctrine_window must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "clause_id": self.clause_id,
            "sequence": self.sequence,
            "source_diplomacy_id": self.source_diplomacy_id,
            "principle": self.principle.value,
            "doctrine_scope": self.doctrine_scope.value,
            "doctrine_status": self.doctrine_status.value,
            "case_ids": list(self.case_ids),
            "release_ready": self.release_ready,
            "doctrine_strength": self.doctrine_strength,
            "doctrine_window": self.doctrine_window,
            "doctrine_tags": list(self.doctrine_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class LeitsternDoctrine:
    """Durable Leitstern doctrine built from consensus diplomacy."""

    doctrine_id: str
    consensus_diplomacy: ConsensusDiplomacy
    clauses: tuple[DoctrineClause, ...]
    doctrine_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "doctrine_id", _non_empty(self.doctrine_id, field_name="doctrine_id"))

    @property
    def guarded_clause_ids(self) -> tuple[str, ...]:
        return tuple(clause.clause_id for clause in self.clauses if clause.doctrine_status is DoctrineStatus.GUARDED)

    @property
    def adopted_clause_ids(self) -> tuple[str, ...]:
        return tuple(clause.clause_id for clause in self.clauses if clause.doctrine_status is DoctrineStatus.ADOPTED)

    @property
    def enshrined_clause_ids(self) -> tuple[str, ...]:
        return tuple(clause.clause_id for clause in self.clauses if clause.doctrine_status is DoctrineStatus.ENSHRINED)

    def to_dict(self) -> dict[str, object]:
        return {
            "doctrine_id": self.doctrine_id,
            "consensus_diplomacy": self.consensus_diplomacy.to_dict(),
            "clauses": [clause.to_dict() for clause in self.clauses],
            "doctrine_signal": self.doctrine_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "guarded_clause_ids": list(self.guarded_clause_ids),
            "adopted_clause_ids": list(self.adopted_clause_ids),
            "enshrined_clause_ids": list(self.enshrined_clause_ids),
        }


def _principle(channel: DiplomacyChannel) -> DoctrinePrinciple:
    return {
        DiplomacyStatus.DEADLOCKED: DoctrinePrinciple.BOUNDARY_PRIMACY,
        DiplomacyStatus.BROKERED: DoctrinePrinciple.GOVERNED_ALIGNMENT,
        DiplomacyStatus.HARMONIZED: DoctrinePrinciple.EXPANSION_DISCIPLINE,
    }[channel.diplomacy_status]


def _scope(channel: DiplomacyChannel) -> DoctrineScope:
    return {
        DiplomacyPath.VETO_TABLE: DoctrineScope.STEWARD_CANON,
        DiplomacyPath.GOVERNANCE_TABLE: DoctrineScope.GOVERNANCE_CANON,
        DiplomacyPath.AUTONOMY_TABLE: DoctrineScope.AUTONOMY_CANON,
    }[channel.diplomacy_path]


def _status(channel: DiplomacyChannel) -> DoctrineStatus:
    return {
        DiplomacyStatus.DEADLOCKED: DoctrineStatus.GUARDED,
        DiplomacyStatus.BROKERED: DoctrineStatus.ADOPTED,
        DiplomacyStatus.HARMONIZED: DoctrineStatus.ENSHRINED,
    }[channel.diplomacy_status]


def _doctrine_strength(channel: DiplomacyChannel) -> float:
    bonus = {
        DoctrineStatus.GUARDED: -0.04,
        DoctrineStatus.ADOPTED: 0.02,
        DoctrineStatus.ENSHRINED: 0.1,
    }[_status(channel)]
    return round(max(0.0, min(1.0, channel.compromise_score + bonus)), 3)


def _doctrine_window(channel: DiplomacyChannel) -> int:
    if channel.diplomacy_status is DiplomacyStatus.DEADLOCKED:
        return channel.negotiation_window
    if channel.diplomacy_status is DiplomacyStatus.BROKERED:
        return channel.negotiation_window + 1
    return channel.negotiation_window + 2


def build_leitstern_doctrine(
    consensus_diplomacy: ConsensusDiplomacy | None = None,
    *,
    doctrine_id: str = "leitstern-doctrine",
) -> LeitsternDoctrine:
    """Build the durable Leitstern doctrine over diplomacy channels."""

    resolved_diplomacy = (
        build_consensus_diplomacy(diplomacy_id=f"{doctrine_id}-diplomacy")
        if consensus_diplomacy is None
        else consensus_diplomacy
    )
    clauses = tuple(
        DoctrineClause(
            clause_id=f"{doctrine_id}-{channel.diplomacy_id.removeprefix(f'{resolved_diplomacy.diplomacy_id}-')}",
            sequence=index,
            source_diplomacy_id=channel.diplomacy_id,
            principle=_principle(channel),
            doctrine_scope=_scope(channel),
            doctrine_status=_status(channel),
            case_ids=channel.case_ids,
            release_ready=channel.release_ready and _status(channel) is DoctrineStatus.ENSHRINED,
            doctrine_strength=_doctrine_strength(channel),
            doctrine_window=_doctrine_window(channel),
            doctrine_tags=tuple(
                dict.fromkeys(
                    (
                        *channel.diplomacy_tags,
                        _principle(channel).value,
                        _scope(channel).value,
                        _status(channel).value,
                    )
                )
            ),
            summary=(
                f"{channel.diplomacy_id} is codified as {_principle(channel).value} within "
                f"{_scope(channel).value} and remains {_status(channel).value}."
            ),
        )
        for index, channel in enumerate(resolved_diplomacy.channels, start=1)
    )
    if not clauses:
        raise ValueError("leitstern doctrine requires at least one clause")

    severity = "info"
    status = "doctrine-enshrined"
    if any(clause.doctrine_status is DoctrineStatus.GUARDED for clause in clauses):
        severity = "critical"
        status = "doctrine-guarded"
    elif any(clause.doctrine_status is DoctrineStatus.ADOPTED for clause in clauses):
        severity = "warning"
        status = "doctrine-adopted"

    doctrine_signal = TelemetrySignal(
        signal_name="leitstern-doctrine",
        boundary=resolved_diplomacy.diplomacy_signal.boundary,
        correlation_id=doctrine_id,
        severity=severity,
        status=status,
        metrics={
            "clause_count": float(len(clauses)),
            "guarded_count": float(len([clause for clause in clauses if clause.doctrine_status is DoctrineStatus.GUARDED])),
            "adopted_count": float(len([clause for clause in clauses if clause.doctrine_status is DoctrineStatus.ADOPTED])),
            "enshrined_count": float(
                len([clause for clause in clauses if clause.doctrine_status is DoctrineStatus.ENSHRINED])
            ),
            "release_ready_count": float(len([clause for clause in clauses if clause.release_ready])),
            "avg_doctrine_strength": round(sum(clause.doctrine_strength for clause in clauses) / len(clauses), 3),
        },
        labels={"doctrine_id": doctrine_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_diplomacy.final_snapshot.runtime_stage,
        signals=(doctrine_signal, *resolved_diplomacy.final_snapshot.signals),
        alerts=resolved_diplomacy.final_snapshot.alerts,
        audit_entries=resolved_diplomacy.final_snapshot.audit_entries,
        active_controls=resolved_diplomacy.final_snapshot.active_controls,
    )
    return LeitsternDoctrine(
        doctrine_id=doctrine_id,
        consensus_diplomacy=resolved_diplomacy,
        clauses=clauses,
        doctrine_signal=doctrine_signal,
        final_snapshot=final_snapshot,
    )
