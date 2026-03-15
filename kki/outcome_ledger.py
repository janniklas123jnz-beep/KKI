"""Outcome ledger over executed steward workboard items."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .operations_steward import StewardDirectiveType
from .steward_workboard import StewardWorkboard, WorkboardItem, WorkboardLane, WorkboardQueue, build_steward_workboard
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class OutcomeStatus(str, Enum):
    """Canonical results of executed steward work."""

    CONTAINED = "contained"
    GOVERNED = "governed"
    TUNED = "tuned"
    OBSERVED = "observed"


@dataclass(frozen=True)
class OutcomeRecord:
    """Durable outcome trace for one workboard item."""

    record_id: str
    case_id: str
    sequence: int
    directive_type: StewardDirectiveType
    queue: WorkboardQueue
    lane: WorkboardLane
    outcome_status: OutcomeStatus
    outcome_ref: str
    confidence_score: float
    resolved_within_sla: bool
    exception_candidate: bool
    evidence_refs: tuple[str, ...]
    commitment_refs: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "record_id", _non_empty(self.record_id, field_name="record_id"))
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))
        object.__setattr__(self, "outcome_ref", _non_empty(self.outcome_ref, field_name="outcome_ref"))
        object.__setattr__(self, "confidence_score", _clamp01(self.confidence_score))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")

    def to_dict(self) -> dict[str, object]:
        return {
            "record_id": self.record_id,
            "case_id": self.case_id,
            "sequence": self.sequence,
            "directive_type": self.directive_type.value,
            "queue": self.queue.value,
            "lane": self.lane.value,
            "outcome_status": self.outcome_status.value,
            "outcome_ref": self.outcome_ref,
            "confidence_score": self.confidence_score,
            "resolved_within_sla": self.resolved_within_sla,
            "exception_candidate": self.exception_candidate,
            "evidence_refs": list(self.evidence_refs),
            "commitment_refs": list(self.commitment_refs),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class OutcomeLedger:
    """Persistent outcome trail over steward workboard execution."""

    ledger_id: str
    workboard: StewardWorkboard
    records: tuple[OutcomeRecord, ...]
    ledger_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "ledger_id", _non_empty(self.ledger_id, field_name="ledger_id"))

    @property
    def contained_case_ids(self) -> tuple[str, ...]:
        return tuple(record.case_id for record in self.records if record.outcome_status is OutcomeStatus.CONTAINED)

    @property
    def governed_case_ids(self) -> tuple[str, ...]:
        return tuple(record.case_id for record in self.records if record.outcome_status is OutcomeStatus.GOVERNED)

    @property
    def tuned_case_ids(self) -> tuple[str, ...]:
        return tuple(record.case_id for record in self.records if record.outcome_status is OutcomeStatus.TUNED)

    @property
    def observed_case_ids(self) -> tuple[str, ...]:
        return tuple(record.case_id for record in self.records if record.outcome_status is OutcomeStatus.OBSERVED)

    @property
    def exception_candidate_case_ids(self) -> tuple[str, ...]:
        return tuple(record.case_id for record in self.records if record.exception_candidate)

    def to_dict(self) -> dict[str, object]:
        return {
            "ledger_id": self.ledger_id,
            "workboard": self.workboard.to_dict(),
            "records": [record.to_dict() for record in self.records],
            "ledger_signal": self.ledger_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "contained_case_ids": list(self.contained_case_ids),
            "governed_case_ids": list(self.governed_case_ids),
            "tuned_case_ids": list(self.tuned_case_ids),
            "observed_case_ids": list(self.observed_case_ids),
            "exception_candidate_case_ids": list(self.exception_candidate_case_ids),
        }


def _outcome_status_for_item(item: WorkboardItem) -> OutcomeStatus:
    return {
        StewardDirectiveType.STABILIZE: OutcomeStatus.CONTAINED,
        StewardDirectiveType.GOVERN: OutcomeStatus.GOVERNED,
        StewardDirectiveType.ADAPT: OutcomeStatus.TUNED,
        StewardDirectiveType.MONITOR: OutcomeStatus.OBSERVED,
    }[item.directive_type]


def _resolved_within_sla(item: WorkboardItem) -> bool:
    return item.lane in {WorkboardLane.EXPEDITE, WorkboardLane.COMMITTED, WorkboardLane.WATCH}


def _exception_candidate(item: WorkboardItem) -> bool:
    return item.directive_type in {StewardDirectiveType.STABILIZE, StewardDirectiveType.ADAPT}


def build_outcome_ledger(
    workboard: StewardWorkboard | None = None,
    *,
    ledger_id: str = "outcome-ledger",
) -> OutcomeLedger:
    """Build a persistent outcome trace over steward workboard items."""

    resolved_workboard = build_steward_workboard(workboard_id=f"{ledger_id}-workboard") if workboard is None else workboard
    records = tuple(
        OutcomeRecord(
            record_id=f"{ledger_id}-{item.case_id}",
            case_id=item.case_id,
            sequence=index,
            directive_type=item.directive_type,
            queue=item.queue,
            lane=item.lane,
            outcome_status=_outcome_status_for_item(item),
            outcome_ref=f"outcome-{ledger_id}-{item.case_id}-{_outcome_status_for_item(item).value}",
            confidence_score=next(
                directive.confidence_score for directive in resolved_workboard.steward.directives if directive.case_id == item.case_id
            ),
            resolved_within_sla=_resolved_within_sla(item),
            exception_candidate=_exception_candidate(item),
            evidence_refs=item.evidence_refs,
            commitment_refs=item.commitment_refs,
            summary=f"{item.case_id} completed as { _outcome_status_for_item(item).value } through the {item.queue.value} queue.",
        )
        for index, item in enumerate(resolved_workboard.items, start=1)
    )
    if not records:
        raise ValueError("outcome ledger requires at least one record")

    severity = "info"
    status = "observed-outcomes"
    if any(record.outcome_status is OutcomeStatus.CONTAINED for record in records):
        severity = "warning"
        status = "stabilizing-outcomes"
    elif any(record.outcome_status is OutcomeStatus.GOVERNED for record in records):
        status = "governed-outcomes"

    ledger_signal = TelemetrySignal(
        signal_name="outcome-ledger",
        boundary=resolved_workboard.board_signal.boundary,
        correlation_id=ledger_id,
        severity=severity,
        status=status,
        metrics={
            "record_count": float(len(records)),
            "contained_count": float(len([record for record in records if record.outcome_status is OutcomeStatus.CONTAINED])),
            "governed_count": float(len([record for record in records if record.outcome_status is OutcomeStatus.GOVERNED])),
            "tuned_count": float(len([record for record in records if record.outcome_status is OutcomeStatus.TUNED])),
            "observed_count": float(len([record for record in records if record.outcome_status is OutcomeStatus.OBSERVED])),
            "exception_candidate_count": float(len([record for record in records if record.exception_candidate])),
        },
        labels={"ledger_id": ledger_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_workboard.final_snapshot.runtime_stage,
        signals=(ledger_signal, resolved_workboard.board_signal, *resolved_workboard.final_snapshot.signals),
        alerts=resolved_workboard.final_snapshot.alerts,
        audit_entries=resolved_workboard.final_snapshot.audit_entries,
        active_controls=resolved_workboard.final_snapshot.active_controls,
    )
    return OutcomeLedger(
        ledger_id=ledger_id,
        workboard=resolved_workboard,
        records=records,
        ledger_signal=ledger_signal,
        final_snapshot=final_snapshot,
    )
