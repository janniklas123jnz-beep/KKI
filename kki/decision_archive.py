"""Decision archive preserving directive consensus as durable records."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .data_models import PersistenceRecord
from .directive_consensus import (
    ConsensusDirective,
    ConsensusDirectiveStatus,
    ConsensusDirectiveType,
    DirectiveConsensus,
    build_directive_consensus,
)
from .module_boundaries import ModuleBoundaryName
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class ArchiveStatus(str, Enum):
    """Durable archival state for one consensus directive."""

    SEALED = "sealed"
    INDEXED = "indexed"
    CODIFIED = "codified"


class ArchiveRetention(str, Enum):
    """Retention posture for archived top-level decisions."""

    AUDIT = "audit"
    KNOWLEDGE = "knowledge"


@dataclass(frozen=True)
class ArchiveEntry:
    """One durable archive entry derived from a top-level directive."""

    entry_id: str
    sequence: int
    directive_id: str
    directive_type: ConsensusDirectiveType
    directive_status: ConsensusDirectiveStatus
    archive_status: ArchiveStatus
    retention: ArchiveRetention
    persistence_record: PersistenceRecord
    case_ids: tuple[str, ...]
    release_ready: bool
    retention_score: float
    archive_weight: float
    archive_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "entry_id", _non_empty(self.entry_id, field_name="entry_id"))
        object.__setattr__(self, "directive_id", _non_empty(self.directive_id, field_name="directive_id"))
        object.__setattr__(self, "retention_score", _clamp01(self.retention_score))
        object.__setattr__(self, "archive_weight", _clamp01(self.archive_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "entry_id": self.entry_id,
            "sequence": self.sequence,
            "directive_id": self.directive_id,
            "directive_type": self.directive_type.value,
            "directive_status": self.directive_status.value,
            "archive_status": self.archive_status.value,
            "retention": self.retention.value,
            "persistence_record": self.persistence_record.to_dict(),
            "case_ids": list(self.case_ids),
            "release_ready": self.release_ready,
            "retention_score": self.retention_score,
            "archive_weight": self.archive_weight,
            "archive_tags": list(self.archive_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class DecisionArchive:
    """Durable archive over the directive consensus layer."""

    archive_id: str
    directive_consensus: DirectiveConsensus
    entries: tuple[ArchiveEntry, ...]
    archive_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "archive_id", _non_empty(self.archive_id, field_name="archive_id"))

    @property
    def sealed_entry_ids(self) -> tuple[str, ...]:
        return tuple(entry.entry_id for entry in self.entries if entry.archive_status is ArchiveStatus.SEALED)

    @property
    def indexed_entry_ids(self) -> tuple[str, ...]:
        return tuple(entry.entry_id for entry in self.entries if entry.archive_status is ArchiveStatus.INDEXED)

    @property
    def codified_entry_ids(self) -> tuple[str, ...]:
        return tuple(entry.entry_id for entry in self.entries if entry.archive_status is ArchiveStatus.CODIFIED)

    def to_dict(self) -> dict[str, object]:
        return {
            "archive_id": self.archive_id,
            "directive_consensus": self.directive_consensus.to_dict(),
            "entries": [entry.to_dict() for entry in self.entries],
            "archive_signal": self.archive_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "sealed_entry_ids": list(self.sealed_entry_ids),
            "indexed_entry_ids": list(self.indexed_entry_ids),
            "codified_entry_ids": list(self.codified_entry_ids),
        }


def _archive_status_for_directive(directive: ConsensusDirective) -> ArchiveStatus:
    return {
        ConsensusDirectiveStatus.BINDING: ArchiveStatus.SEALED,
        ConsensusDirectiveStatus.NEGOTIATED: ArchiveStatus.INDEXED,
        ConsensusDirectiveStatus.RATIFIED: ArchiveStatus.CODIFIED,
    }[directive.directive_status]


def _retention_for_directive(directive: ConsensusDirective) -> ArchiveRetention:
    return {
        ConsensusDirectiveStatus.BINDING: ArchiveRetention.AUDIT,
        ConsensusDirectiveStatus.NEGOTIATED: ArchiveRetention.AUDIT,
        ConsensusDirectiveStatus.RATIFIED: ArchiveRetention.KNOWLEDGE,
    }[directive.directive_status]


def _retention_score(directive: ConsensusDirective) -> float:
    return round(max(directive.authority_score, directive.consensus_strength), 3)


def _archive_weight(directive: ConsensusDirective) -> float:
    release_bonus = 0.08 if directive.release_ready else 0.0
    return round(min(1.0, ((directive.authority_score + directive.consensus_strength) / 2.0) + release_bonus), 3)


def _persistence_record(
    archive_id: str,
    boundary: ModuleBoundaryName,
    directive: ConsensusDirective,
) -> PersistenceRecord:
    return PersistenceRecord(
        record_type="directive-consensus-archive-entry",
        boundary=boundary,
        schema_version="1.0",
        retention_class=_retention_for_directive(directive).value,
        payload={
            "archive_id": archive_id,
            "directive_id": directive.directive_id,
            "directive_type": directive.directive_type.value,
            "directive_status": directive.directive_status.value,
            "mandate": directive.mandate.value,
            "source_priority": directive.source_priority.value,
            "authority_score": directive.authority_score,
            "consensus_strength": directive.consensus_strength,
            "case_ids": list(directive.case_ids),
        },
    )


def build_decision_archive(
    directive_consensus: DirectiveConsensus | None = None,
    *,
    archive_id: str = "decision-archive",
) -> DecisionArchive:
    """Build the durable archive over final directive consensus."""

    resolved_consensus = (
        build_directive_consensus(consensus_id=f"{archive_id}-consensus")
        if directive_consensus is None
        else directive_consensus
    )
    entries = tuple(
        ArchiveEntry(
            entry_id=f"{archive_id}-{directive.directive_id.removeprefix(f'{resolved_consensus.consensus_id}-')}",
            sequence=index,
            directive_id=directive.directive_id,
            directive_type=directive.directive_type,
            directive_status=directive.directive_status,
            archive_status=_archive_status_for_directive(directive),
            retention=_retention_for_directive(directive),
            persistence_record=_persistence_record(
                archive_id,
                resolved_consensus.consensus_signal.boundary,
                directive,
            ),
            case_ids=directive.case_ids,
            release_ready=directive.release_ready,
            retention_score=_retention_score(directive),
            archive_weight=_archive_weight(directive),
            archive_tags=tuple(
                dict.fromkeys(
                    (
                        *directive.directive_tags,
                        _archive_status_for_directive(directive).value,
                        _retention_for_directive(directive).value,
                    )
                )
            ),
            summary=(
                f"{directive.directive_id} is preserved as "
                f"{_archive_status_for_directive(directive).value} archive with "
                f"{_retention_for_directive(directive).value} retention."
            ),
        )
        for index, directive in enumerate(resolved_consensus.directives, start=1)
    )
    if not entries:
        raise ValueError("decision archive requires at least one entry")

    severity = "info"
    status = "archive-codified"
    if any(entry.archive_status is ArchiveStatus.SEALED for entry in entries):
        severity = "critical"
        status = "archive-sealed"
    elif any(entry.archive_status is ArchiveStatus.INDEXED for entry in entries):
        severity = "warning"
        status = "archive-indexed"

    archive_signal = TelemetrySignal(
        signal_name="decision-archive",
        boundary=resolved_consensus.consensus_signal.boundary,
        correlation_id=archive_id,
        severity=severity,
        status=status,
        metrics={
            "entry_count": float(len(entries)),
            "sealed_count": float(len([entry for entry in entries if entry.archive_status is ArchiveStatus.SEALED])),
            "indexed_count": float(len([entry for entry in entries if entry.archive_status is ArchiveStatus.INDEXED])),
            "codified_count": float(len([entry for entry in entries if entry.archive_status is ArchiveStatus.CODIFIED])),
            "release_ready_count": float(len([entry for entry in entries if entry.release_ready])),
            "avg_archive_weight": round(sum(entry.archive_weight for entry in entries) / len(entries), 3),
        },
        labels={"archive_id": archive_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_consensus.final_snapshot.runtime_stage,
        signals=(archive_signal, *resolved_consensus.final_snapshot.signals),
        alerts=resolved_consensus.final_snapshot.alerts,
        audit_entries=resolved_consensus.final_snapshot.audit_entries,
        active_controls=resolved_consensus.final_snapshot.active_controls,
    )
    return DecisionArchive(
        archive_id=archive_id,
        directive_consensus=resolved_consensus,
        entries=entries,
        archive_signal=archive_signal,
        final_snapshot=final_snapshot,
    )
