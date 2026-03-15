"""Reusable playbook catalog derived from learning, outcomes, and exceptions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .exception_register import ExceptionCase, ExceptionKind, ExceptionRegister, build_exception_register
from .learning_register import LearningPatternType, LearningRecord, LearningRegister, build_learning_register
from .outcome_ledger import OutcomeLedger, OutcomeRecord, OutcomeStatus, build_outcome_ledger
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


class PlaybookType(str, Enum):
    """Canonical operating playbook classes."""

    STABILIZATION = "stabilization"
    GOVERNANCE = "governance"
    ADAPTATION = "adaptation"
    MONITORING = "monitoring"


class PlaybookReadiness(str, Enum):
    """Operational reuse readiness for compiled playbooks."""

    STEWARD_GUIDED = "steward-guided"
    GOVERNED_STANDARD = "governed-standard"
    AUTONOMY_CANDIDATE = "autonomy-candidate"


@dataclass(frozen=True)
class PlaybookEntry:
    """Reusable operating recipe compiled from prior execution traces."""

    playbook_id: str
    case_id: str
    revision: int
    playbook_type: PlaybookType
    pattern_type: LearningPatternType
    outcome_status: OutcomeStatus
    readiness: PlaybookReadiness
    reusable: bool
    automation_candidate: bool
    trigger_refs: tuple[str, ...]
    commitment_refs: tuple[str, ...]
    guardrail_notes: tuple[str, ...]
    steps: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "playbook_id", _non_empty(self.playbook_id, field_name="playbook_id"))
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.revision < 1:
            raise ValueError("revision must be positive")

    def to_dict(self) -> dict[str, object]:
        return {
            "playbook_id": self.playbook_id,
            "case_id": self.case_id,
            "revision": self.revision,
            "playbook_type": self.playbook_type.value,
            "pattern_type": self.pattern_type.value,
            "outcome_status": self.outcome_status.value,
            "readiness": self.readiness.value,
            "reusable": self.reusable,
            "automation_candidate": self.automation_candidate,
            "trigger_refs": list(self.trigger_refs),
            "commitment_refs": list(self.commitment_refs),
            "guardrail_notes": list(self.guardrail_notes),
            "steps": list(self.steps),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class PlaybookCatalog:
    """Compiled catalog of reusable operating playbooks."""

    catalog_id: str
    learning_register: LearningRegister
    outcome_ledger: OutcomeLedger
    exception_register: ExceptionRegister
    playbooks: tuple[PlaybookEntry, ...]
    catalog_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "catalog_id", _non_empty(self.catalog_id, field_name="catalog_id"))

    @property
    def steward_guided_case_ids(self) -> tuple[str, ...]:
        return tuple(playbook.case_id for playbook in self.playbooks if playbook.readiness is PlaybookReadiness.STEWARD_GUIDED)

    @property
    def governed_case_ids(self) -> tuple[str, ...]:
        return tuple(playbook.case_id for playbook in self.playbooks if playbook.readiness is PlaybookReadiness.GOVERNED_STANDARD)

    @property
    def autonomy_candidate_case_ids(self) -> tuple[str, ...]:
        return tuple(playbook.case_id for playbook in self.playbooks if playbook.readiness is PlaybookReadiness.AUTONOMY_CANDIDATE)

    def to_dict(self) -> dict[str, object]:
        return {
            "catalog_id": self.catalog_id,
            "learning_register": self.learning_register.to_dict(),
            "outcome_ledger": self.outcome_ledger.to_dict(),
            "exception_register": self.exception_register.to_dict(),
            "playbooks": [playbook.to_dict() for playbook in self.playbooks],
            "catalog_signal": self.catalog_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "steward_guided_case_ids": list(self.steward_guided_case_ids),
            "governed_case_ids": list(self.governed_case_ids),
            "autonomy_candidate_case_ids": list(self.autonomy_candidate_case_ids),
        }


def _playbook_type_for_outcome(record: OutcomeRecord) -> PlaybookType:
    return {
        OutcomeStatus.CONTAINED: PlaybookType.STABILIZATION,
        OutcomeStatus.GOVERNED: PlaybookType.GOVERNANCE,
        OutcomeStatus.TUNED: PlaybookType.ADAPTATION,
        OutcomeStatus.OBSERVED: PlaybookType.MONITORING,
    }[record.outcome_status]


def _readiness_for_case(
    learning_record: LearningRecord,
    outcome_record: OutcomeRecord,
    exception_case: ExceptionCase | None,
) -> PlaybookReadiness:
    if exception_case is not None:
        return PlaybookReadiness.STEWARD_GUIDED
    if learning_record.reusable and outcome_record.outcome_status is OutcomeStatus.OBSERVED:
        return PlaybookReadiness.AUTONOMY_CANDIDATE
    return PlaybookReadiness.GOVERNED_STANDARD


def _guardrail_notes(
    learning_record: LearningRecord,
    outcome_record: OutcomeRecord,
    exception_case: ExceptionCase | None,
) -> tuple[str, ...]:
    notes: list[str] = [
        f"pattern:{learning_record.pattern_type.value}",
        f"outcome:{outcome_record.outcome_status.value}",
    ]
    if exception_case is not None:
        notes.append(f"exception:{exception_case.kind.value}")
        notes.append(f"severity:{exception_case.severity.value}")
    elif learning_record.reusable:
        notes.append("reusable:yes")
    else:
        notes.append("reusable:no")
    return tuple(notes)


def _steps_for_playbook(
    playbook_type: PlaybookType,
    readiness: PlaybookReadiness,
    exception_case: ExceptionCase | None,
) -> tuple[str, ...]:
    base_steps = {
        PlaybookType.STABILIZATION: (
            "Contain the affected boundary and preserve evidence.",
            "Apply the stabilized intervention with steward oversight.",
            "Recheck readiness before re-entry.",
        ),
        PlaybookType.GOVERNANCE: (
            "Review the governed change against active guardrails.",
            "Apply the calibrated operating recipe.",
            "Record approval and resulting telemetry.",
        ),
        PlaybookType.ADAPTATION: (
            "Replay the adaptation path with the tuned threshold.",
            "Verify the follow-up commitments are completed.",
            "Capture any residual drift before closure.",
        ),
        PlaybookType.MONITORING: (
            "Observe the monitored path against the learned threshold.",
            "Keep commitments visible during the watch window.",
            "Promote the recipe if the run stays routine.",
        ),
    }[playbook_type]
    if readiness is PlaybookReadiness.AUTONOMY_CANDIDATE:
        return (*base_steps, "Eligible for controlled autonomous execution.")
    if exception_case is not None:
        return (*base_steps, f"Escalate under {exception_case.kind.value} handling before closure.")
    return (*base_steps, "Execute under governed supervision.")


def build_playbook_catalog(
    learning_register: LearningRegister | None = None,
    outcome_ledger: OutcomeLedger | None = None,
    exception_register: ExceptionRegister | None = None,
    *,
    catalog_id: str = "playbook-catalog",
) -> PlaybookCatalog:
    """Compile reusable playbooks from learning, outcomes, and exception traces."""

    resolved_learning = (
        build_learning_register(register_id=f"{catalog_id}-learning") if learning_register is None else learning_register
    )
    resolved_outcomes = build_outcome_ledger(ledger_id=f"{catalog_id}-outcomes") if outcome_ledger is None else outcome_ledger
    resolved_exceptions = (
        build_exception_register(register_id=f"{catalog_id}-exceptions") if exception_register is None else exception_register
    )
    learning_by_case = {record.case_id: record for record in resolved_learning.records}
    outcome_by_case = {record.case_id: record for record in resolved_outcomes.records}
    exception_by_case = {record.case_id: record for record in resolved_exceptions.exceptions}
    playbooks = tuple(
        PlaybookEntry(
            playbook_id=f"{catalog_id}-{outcome_record.case_id}",
            case_id=outcome_record.case_id,
            revision=index,
            playbook_type=_playbook_type_for_outcome(outcome_record),
            pattern_type=learning_by_case[outcome_record.case_id].pattern_type,
            outcome_status=outcome_record.outcome_status,
            readiness=_readiness_for_case(
                learning_by_case[outcome_record.case_id],
                outcome_record,
                exception_by_case.get(outcome_record.case_id),
            ),
            reusable=learning_by_case[outcome_record.case_id].reusable,
            automation_candidate=_readiness_for_case(
                learning_by_case[outcome_record.case_id],
                outcome_record,
                exception_by_case.get(outcome_record.case_id),
            )
            is PlaybookReadiness.AUTONOMY_CANDIDATE,
            trigger_refs=learning_by_case[outcome_record.case_id].evidence_refs,
            commitment_refs=tuple(
                dict.fromkeys(
                    (*learning_by_case[outcome_record.case_id].commitment_refs, *outcome_record.commitment_refs)
                )
            ),
            guardrail_notes=_guardrail_notes(
                learning_by_case[outcome_record.case_id],
                outcome_record,
                exception_by_case.get(outcome_record.case_id),
            ),
            steps=_steps_for_playbook(
                _playbook_type_for_outcome(outcome_record),
                _readiness_for_case(
                    learning_by_case[outcome_record.case_id],
                    outcome_record,
                    exception_by_case.get(outcome_record.case_id),
                ),
                exception_by_case.get(outcome_record.case_id),
            ),
            summary=(
                f"{outcome_record.case_id} is cataloged as a "
                f"{_playbook_type_for_outcome(outcome_record).value} playbook "
                f"with {_readiness_for_case(learning_by_case[outcome_record.case_id], outcome_record, exception_by_case.get(outcome_record.case_id)).value} readiness."
            ),
        )
        for index, outcome_record in enumerate(resolved_outcomes.records, start=1)
    )
    if not playbooks:
        raise ValueError("playbook catalog requires at least one playbook")

    severity = "info"
    status = "catalog-governed"
    if any(playbook.readiness is PlaybookReadiness.STEWARD_GUIDED for playbook in playbooks):
        severity = "warning"
        status = "catalog-exception-guided"
    if any(playbook.readiness is PlaybookReadiness.AUTONOMY_CANDIDATE for playbook in playbooks):
        status = "catalog-autonomy-ready"

    catalog_signal = TelemetrySignal(
        signal_name="playbook-catalog",
        boundary=resolved_learning.register_signal.boundary,
        correlation_id=catalog_id,
        severity=severity,
        status=status,
        metrics={
            "playbook_count": float(len(playbooks)),
            "steward_guided_count": float(
                len([playbook for playbook in playbooks if playbook.readiness is PlaybookReadiness.STEWARD_GUIDED])
            ),
            "governed_count": float(
                len([playbook for playbook in playbooks if playbook.readiness is PlaybookReadiness.GOVERNED_STANDARD])
            ),
            "autonomy_candidate_count": float(
                len([playbook for playbook in playbooks if playbook.readiness is PlaybookReadiness.AUTONOMY_CANDIDATE])
            ),
        },
        labels={"catalog_id": catalog_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_learning.final_snapshot.runtime_stage,
        signals=(
            catalog_signal,
            resolved_learning.register_signal,
            resolved_outcomes.ledger_signal,
            resolved_exceptions.register_signal,
            *resolved_learning.final_snapshot.signals,
        ),
        alerts=resolved_learning.final_snapshot.alerts,
        audit_entries=resolved_learning.final_snapshot.audit_entries,
        active_controls=resolved_learning.final_snapshot.active_controls,
    )
    return PlaybookCatalog(
        catalog_id=catalog_id,
        learning_register=resolved_learning,
        outcome_ledger=resolved_outcomes,
        exception_register=resolved_exceptions,
        playbooks=playbooks,
        catalog_signal=catalog_signal,
        final_snapshot=final_snapshot,
    )
