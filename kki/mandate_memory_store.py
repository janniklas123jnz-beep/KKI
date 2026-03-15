"""Mandate memory store over strategic cards and course-correction history."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .course_corrector import (
    CourseCorrectionAction,
    CourseCorrectionDirective,
    CourseCorrectionStatus,
    CourseCorrector,
    build_course_corrector,
)
from .mandate_card_deck import MandateCard, MandateCardDeck
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class MandateMemoryStatus(str, Enum):
    """Lifecycle status for a stored strategic mandate."""

    SEALED = "sealed"
    REVIEW = "review"
    RENEWABLE = "renewable"


@dataclass(frozen=True)
class MandateMemoryRecord:
    """Durable memory record for one strategic card and correction path."""

    record_id: str
    sequence: int
    card_id: str
    directive_id: str
    source_action: CourseCorrectionAction
    memory_status: MandateMemoryStatus
    case_ids: tuple[str, ...]
    release_ready: bool
    retention_score: float
    renewal_window: int
    memory_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "record_id", _non_empty(self.record_id, field_name="record_id"))
        object.__setattr__(self, "card_id", _non_empty(self.card_id, field_name="card_id"))
        object.__setattr__(self, "directive_id", _non_empty(self.directive_id, field_name="directive_id"))
        object.__setattr__(self, "retention_score", _clamp01(self.retention_score))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.renewal_window < 1:
            raise ValueError("renewal_window must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "record_id": self.record_id,
            "sequence": self.sequence,
            "card_id": self.card_id,
            "directive_id": self.directive_id,
            "source_action": self.source_action.value,
            "memory_status": self.memory_status.value,
            "case_ids": list(self.case_ids),
            "release_ready": self.release_ready,
            "retention_score": self.retention_score,
            "renewal_window": self.renewal_window,
            "memory_tags": list(self.memory_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class MandateMemoryStore:
    """Durable memory layer over strategic cards and course corrections."""

    store_id: str
    mandate_card_deck: MandateCardDeck
    course_corrector: CourseCorrector
    records: tuple[MandateMemoryRecord, ...]
    store_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "store_id", _non_empty(self.store_id, field_name="store_id"))

    @property
    def sealed_record_ids(self) -> tuple[str, ...]:
        return tuple(record.record_id for record in self.records if record.memory_status is MandateMemoryStatus.SEALED)

    @property
    def review_record_ids(self) -> tuple[str, ...]:
        return tuple(record.record_id for record in self.records if record.memory_status is MandateMemoryStatus.REVIEW)

    @property
    def renewable_record_ids(self) -> tuple[str, ...]:
        return tuple(record.record_id for record in self.records if record.memory_status is MandateMemoryStatus.RENEWABLE)

    def to_dict(self) -> dict[str, object]:
        return {
            "store_id": self.store_id,
            "mandate_card_deck": self.mandate_card_deck.to_dict(),
            "course_corrector": self.course_corrector.to_dict(),
            "records": [record.to_dict() for record in self.records],
            "store_signal": self.store_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "sealed_record_ids": list(self.sealed_record_ids),
            "review_record_ids": list(self.review_record_ids),
            "renewable_record_ids": list(self.renewable_record_ids),
        }


def _memory_status_for_directive(directive: CourseCorrectionDirective) -> MandateMemoryStatus:
    return {
        CourseCorrectionStatus.ENFORCED: MandateMemoryStatus.SEALED,
        CourseCorrectionStatus.DIRECTED: MandateMemoryStatus.REVIEW,
        CourseCorrectionStatus.CLEARED: MandateMemoryStatus.RENEWABLE,
    }[directive.status]


def _retention_score(card: MandateCard, directive: CourseCorrectionDirective) -> float:
    return round(max(card.execution_budget, directive.correction_score), 3)


def _renewal_window(directive: CourseCorrectionDirective) -> int:
    if directive.status is CourseCorrectionStatus.ENFORCED:
        return directive.review_window
    if directive.status is CourseCorrectionStatus.DIRECTED:
        return directive.review_window + 1
    return directive.review_window + 2


def build_mandate_memory_store(
    mandate_card_deck: MandateCardDeck | None = None,
    course_corrector: CourseCorrector | None = None,
    *,
    store_id: str = "mandate-memory-store",
) -> MandateMemoryStore:
    """Build a durable memory store over strategic cards and corrections."""

    resolved_corrector = (
        build_course_corrector(corrector_id=f"{store_id}-corrector") if course_corrector is None else course_corrector
    )
    resolved_deck = (
        resolved_corrector.portfolio_radar.mandate_card_deck if mandate_card_deck is None else mandate_card_deck
    )
    card_by_id = {card.card_id: card for card in resolved_deck.cards}
    card_id_by_radar_entry = {entry.entry_id: entry.card_id for entry in resolved_corrector.portfolio_radar.entries}

    records = tuple(
        MandateMemoryRecord(
            record_id=f"{store_id}-{directive.directive_id.removeprefix(f'{resolved_corrector.corrector_id}-')}",
            sequence=index,
            card_id=card_id_by_radar_entry[directive.radar_entry_id],
            directive_id=directive.directive_id,
            source_action=directive.action,
            memory_status=_memory_status_for_directive(directive),
            case_ids=directive.case_ids,
            release_ready=directive.release_ready,
            retention_score=_retention_score(card_by_id[card_id_by_radar_entry[directive.radar_entry_id]], directive),
            renewal_window=_renewal_window(directive),
            memory_tags=tuple(
                dict.fromkeys(
                    (
                        *directive.control_tags,
                        _memory_status_for_directive(directive).value,
                        "retained-release-ready" if directive.release_ready else "retained-guarded",
                    )
                )
            ),
            summary=(
                f"{directive.directive_id} is stored as {_memory_status_for_directive(directive).value} memory "
                f"for later renewal and review."
            ),
        )
        for index, directive in enumerate(resolved_corrector.directives, start=1)
    )
    if not records:
        raise ValueError("mandate memory store requires at least one record")

    severity = "info"
    status = "memory-renewable"
    if any(record.memory_status is MandateMemoryStatus.SEALED for record in records):
        severity = "critical"
        status = "memory-sealed"
    elif any(record.memory_status is MandateMemoryStatus.REVIEW for record in records):
        severity = "warning"
        status = "memory-review"

    store_signal = TelemetrySignal(
        signal_name="mandate-memory-store",
        boundary=resolved_corrector.corrector_signal.boundary,
        correlation_id=store_id,
        severity=severity,
        status=status,
        metrics={
            "record_count": float(len(records)),
            "sealed_count": float(len([record for record in records if record.memory_status is MandateMemoryStatus.SEALED])),
            "review_count": float(len([record for record in records if record.memory_status is MandateMemoryStatus.REVIEW])),
            "renewable_count": float(
                len([record for record in records if record.memory_status is MandateMemoryStatus.RENEWABLE])
            ),
            "release_ready_count": float(len([record for record in records if record.release_ready])),
            "avg_retention_score": round(sum(record.retention_score for record in records) / len(records), 3),
        },
        labels={"store_id": store_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_corrector.final_snapshot.runtime_stage,
        signals=(store_signal, *resolved_corrector.final_snapshot.signals),
        alerts=resolved_corrector.final_snapshot.alerts,
        audit_entries=resolved_corrector.final_snapshot.audit_entries,
        active_controls=resolved_corrector.final_snapshot.active_controls,
    )
    return MandateMemoryStore(
        store_id=store_id,
        mandate_card_deck=resolved_deck,
        course_corrector=resolved_corrector,
        records=records,
        store_signal=store_signal,
        final_snapshot=final_snapshot,
    )
