"""Guideline compass over retained mandates and navigational constraints."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .course_corrector import CourseCorrectionAction
from .mandate_memory_store import (
    MandateMemoryRecord,
    MandateMemoryStatus,
    MandateMemoryStore,
    build_mandate_memory_store,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class GuidelinePrinciple(str, Enum):
    """Guiding principle retained for future strategic navigation."""

    STABILITY_FIRST = "stability-first"
    GOVERNED_PROGRESS = "governed-progress"
    BOUNDED_EXPANSION = "bounded-expansion"


class NavigationConstraint(str, Enum):
    """Navigational constraint derived from retained mandate memory."""

    HARD_BOUNDARY = "hard-boundary"
    GOVERNED_CORRIDOR = "governed-corridor"
    EXPANSION_WINDOW = "expansion-window"


class CompassStatus(str, Enum):
    """Current navigational posture of one guideline vector."""

    ANCHORED = "anchored"
    GUIDED = "guided"
    OPEN = "open"


@dataclass(frozen=True)
class GuidelineVector:
    """One durable guideline vector retained from the memory store."""

    vector_id: str
    sequence: int
    record_id: str
    source_action: CourseCorrectionAction
    principle: GuidelinePrinciple
    navigation_constraint: NavigationConstraint
    compass_status: CompassStatus
    case_ids: tuple[str, ...]
    release_ready: bool
    guidance_score: float
    renewal_window: int
    control_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "vector_id", _non_empty(self.vector_id, field_name="vector_id"))
        object.__setattr__(self, "record_id", _non_empty(self.record_id, field_name="record_id"))
        object.__setattr__(self, "guidance_score", _clamp01(self.guidance_score))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.renewal_window < 1:
            raise ValueError("renewal_window must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "vector_id": self.vector_id,
            "sequence": self.sequence,
            "record_id": self.record_id,
            "source_action": self.source_action.value,
            "principle": self.principle.value,
            "navigation_constraint": self.navigation_constraint.value,
            "compass_status": self.compass_status.value,
            "case_ids": list(self.case_ids),
            "release_ready": self.release_ready,
            "guidance_score": self.guidance_score,
            "renewal_window": self.renewal_window,
            "control_tags": list(self.control_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class GuidelineCompass:
    """Compass that converts retained mandate memory into navigational guidance."""

    compass_id: str
    mandate_memory_store: MandateMemoryStore
    vectors: tuple[GuidelineVector, ...]
    compass_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "compass_id", _non_empty(self.compass_id, field_name="compass_id"))

    @property
    def anchored_vector_ids(self) -> tuple[str, ...]:
        return tuple(vector.vector_id for vector in self.vectors if vector.compass_status is CompassStatus.ANCHORED)

    @property
    def guided_vector_ids(self) -> tuple[str, ...]:
        return tuple(vector.vector_id for vector in self.vectors if vector.compass_status is CompassStatus.GUIDED)

    @property
    def open_vector_ids(self) -> tuple[str, ...]:
        return tuple(vector.vector_id for vector in self.vectors if vector.compass_status is CompassStatus.OPEN)

    def to_dict(self) -> dict[str, object]:
        return {
            "compass_id": self.compass_id,
            "mandate_memory_store": self.mandate_memory_store.to_dict(),
            "vectors": [vector.to_dict() for vector in self.vectors],
            "compass_signal": self.compass_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "anchored_vector_ids": list(self.anchored_vector_ids),
            "guided_vector_ids": list(self.guided_vector_ids),
            "open_vector_ids": list(self.open_vector_ids),
        }


def _principle_for_record(record: MandateMemoryRecord) -> GuidelinePrinciple:
    return {
        CourseCorrectionAction.CONTAIN: GuidelinePrinciple.STABILITY_FIRST,
        CourseCorrectionAction.REBALANCE: GuidelinePrinciple.GOVERNED_PROGRESS,
        CourseCorrectionAction.ACCELERATE: GuidelinePrinciple.BOUNDED_EXPANSION,
    }[record.source_action]


def _constraint_for_record(record: MandateMemoryRecord) -> NavigationConstraint:
    return {
        MandateMemoryStatus.SEALED: NavigationConstraint.HARD_BOUNDARY,
        MandateMemoryStatus.REVIEW: NavigationConstraint.GOVERNED_CORRIDOR,
        MandateMemoryStatus.RENEWABLE: NavigationConstraint.EXPANSION_WINDOW,
    }[record.memory_status]


def _status_for_record(record: MandateMemoryRecord) -> CompassStatus:
    return {
        MandateMemoryStatus.SEALED: CompassStatus.ANCHORED,
        MandateMemoryStatus.REVIEW: CompassStatus.GUIDED,
        MandateMemoryStatus.RENEWABLE: CompassStatus.OPEN,
    }[record.memory_status]


def _guidance_score(record: MandateMemoryRecord) -> float:
    release_bonus = 0.08 if record.release_ready else 0.0
    return round(record.retention_score + release_bonus, 3)


def build_guideline_compass(
    mandate_memory_store: MandateMemoryStore | None = None,
    *,
    compass_id: str = "guideline-compass",
) -> GuidelineCompass:
    """Build the guideline compass from retained mandate memory."""

    resolved_store = (
        build_mandate_memory_store(store_id=f"{compass_id}-store")
        if mandate_memory_store is None
        else mandate_memory_store
    )
    vectors = tuple(
        GuidelineVector(
            vector_id=f"{compass_id}-{record.record_id.removeprefix(f'{resolved_store.store_id}-')}",
            sequence=index,
            record_id=record.record_id,
            source_action=record.source_action,
            principle=_principle_for_record(record),
            navigation_constraint=_constraint_for_record(record),
            compass_status=_status_for_record(record),
            case_ids=record.case_ids,
            release_ready=record.release_ready,
            guidance_score=_guidance_score(record),
            renewal_window=record.renewal_window,
            control_tags=tuple(
                dict.fromkeys(
                    (
                        *record.memory_tags,
                        _principle_for_record(record).value,
                        _constraint_for_record(record).value,
                        _status_for_record(record).value,
                    )
                )
            ),
            summary=(
                f"{record.record_id} anchors {_principle_for_record(record).value} "
                f"through {_constraint_for_record(record).value}."
            ),
        )
        for index, record in enumerate(resolved_store.records, start=1)
    )
    if not vectors:
        raise ValueError("guideline compass requires at least one vector")

    severity = "info"
    status = "compass-open"
    if any(vector.compass_status is CompassStatus.ANCHORED for vector in vectors):
        severity = "critical"
        status = "compass-anchored"
    elif any(vector.compass_status is CompassStatus.GUIDED for vector in vectors):
        severity = "warning"
        status = "compass-guided"

    compass_signal = TelemetrySignal(
        signal_name="guideline-compass",
        boundary=resolved_store.store_signal.boundary,
        correlation_id=compass_id,
        severity=severity,
        status=status,
        metrics={
            "vector_count": float(len(vectors)),
            "anchored_count": float(len([vector for vector in vectors if vector.compass_status is CompassStatus.ANCHORED])),
            "guided_count": float(len([vector for vector in vectors if vector.compass_status is CompassStatus.GUIDED])),
            "open_count": float(len([vector for vector in vectors if vector.compass_status is CompassStatus.OPEN])),
            "release_ready_count": float(len([vector for vector in vectors if vector.release_ready])),
            "avg_guidance_score": round(sum(vector.guidance_score for vector in vectors) / len(vectors), 3),
        },
        labels={"compass_id": compass_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_store.final_snapshot.runtime_stage,
        signals=(compass_signal, *resolved_store.final_snapshot.signals),
        alerts=resolved_store.final_snapshot.alerts,
        audit_entries=resolved_store.final_snapshot.audit_entries,
        active_controls=resolved_store.final_snapshot.active_controls,
    )
    return GuidelineCompass(
        compass_id=compass_id,
        mandate_memory_store=resolved_store,
        vectors=vectors,
        compass_signal=compass_signal,
        final_snapshot=final_snapshot,
    )
