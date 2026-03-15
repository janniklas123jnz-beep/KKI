"""Exception register for recurring, unresolved, or policy-breaching cases."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .operations_steward import StewardDirectiveType
from .outcome_ledger import OutcomeLedger, OutcomeRecord, OutcomeStatus, build_outcome_ledger
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


class ExceptionSeverity(str, Enum):
    """Severity of a registered operational exception."""

    CRITICAL = "critical"
    HIGH = "high"
    MODERATE = "moderate"


class ExceptionKind(str, Enum):
    """Operational exception classes for non-routine situations."""

    UNRESOLVED = "unresolved"
    RECURRING = "recurring"
    POLICY_BREACH = "policy-breach"


@dataclass(frozen=True)
class ExceptionCase:
    """Explicit exception entry derived from outcome execution traces."""

    exception_id: str
    case_id: str
    sequence: int
    kind: ExceptionKind
    severity: ExceptionSeverity
    outcome_status: OutcomeStatus
    directive_type: StewardDirectiveType
    escalation_reason: str
    evidence_refs: tuple[str, ...]
    commitment_refs: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "exception_id", _non_empty(self.exception_id, field_name="exception_id"))
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))
        object.__setattr__(self, "escalation_reason", _non_empty(self.escalation_reason, field_name="escalation_reason"))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")

    def to_dict(self) -> dict[str, object]:
        return {
            "exception_id": self.exception_id,
            "case_id": self.case_id,
            "sequence": self.sequence,
            "kind": self.kind.value,
            "severity": self.severity.value,
            "outcome_status": self.outcome_status.value,
            "directive_type": self.directive_type.value,
            "escalation_reason": self.escalation_reason,
            "evidence_refs": list(self.evidence_refs),
            "commitment_refs": list(self.commitment_refs),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class ExceptionRegister:
    """Explicit register of non-routine operating exceptions."""

    register_id: str
    outcome_ledger: OutcomeLedger
    exceptions: tuple[ExceptionCase, ...]
    register_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "register_id", _non_empty(self.register_id, field_name="register_id"))

    @property
    def critical_case_ids(self) -> tuple[str, ...]:
        return tuple(item.case_id for item in self.exceptions if item.severity is ExceptionSeverity.CRITICAL)

    @property
    def recurring_case_ids(self) -> tuple[str, ...]:
        return tuple(item.case_id for item in self.exceptions if item.kind is ExceptionKind.RECURRING)

    @property
    def unresolved_case_ids(self) -> tuple[str, ...]:
        return tuple(item.case_id for item in self.exceptions if item.kind is ExceptionKind.UNRESOLVED)

    @property
    def policy_breach_case_ids(self) -> tuple[str, ...]:
        return tuple(item.case_id for item in self.exceptions if item.kind is ExceptionKind.POLICY_BREACH)

    def to_dict(self) -> dict[str, object]:
        return {
            "register_id": self.register_id,
            "outcome_ledger": self.outcome_ledger.to_dict(),
            "exceptions": [item.to_dict() for item in self.exceptions],
            "register_signal": self.register_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "critical_case_ids": list(self.critical_case_ids),
            "recurring_case_ids": list(self.recurring_case_ids),
            "unresolved_case_ids": list(self.unresolved_case_ids),
            "policy_breach_case_ids": list(self.policy_breach_case_ids),
        }


def _kind_for_record(record: OutcomeRecord) -> ExceptionKind:
    if record.directive_type is StewardDirectiveType.STABILIZE:
        return ExceptionKind.POLICY_BREACH
    if not record.resolved_within_sla:
        return ExceptionKind.UNRESOLVED
    return ExceptionKind.RECURRING


def _severity_for_record(record: OutcomeRecord) -> ExceptionSeverity:
    if record.directive_type is StewardDirectiveType.STABILIZE:
        return ExceptionSeverity.CRITICAL
    if not record.resolved_within_sla:
        return ExceptionSeverity.HIGH
    return ExceptionSeverity.MODERATE


def _escalation_reason(record: OutcomeRecord) -> str:
    if record.directive_type is StewardDirectiveType.STABILIZE:
        return f"{record.case_id} remains policy-critical after containment handling."
    if not record.resolved_within_sla:
        return f"{record.case_id} exceeded the planned execution horizon and stays unresolved."
    return f"{record.case_id} shows a recurring non-routine pattern that should be tracked explicitly."


def build_exception_register(
    outcome_ledger: OutcomeLedger | None = None,
    *,
    register_id: str = "exception-register",
) -> ExceptionRegister:
    """Build an explicit exception register from outcome execution traces."""

    resolved_ledger = build_outcome_ledger(ledger_id=f"{register_id}-ledger") if outcome_ledger is None else outcome_ledger
    exceptions = tuple(
        ExceptionCase(
            exception_id=f"{register_id}-{record.case_id}",
            case_id=record.case_id,
            sequence=index,
            kind=_kind_for_record(record),
            severity=_severity_for_record(record),
            outcome_status=record.outcome_status,
            directive_type=record.directive_type,
            escalation_reason=_escalation_reason(record),
            evidence_refs=record.evidence_refs,
            commitment_refs=record.commitment_refs,
            summary=f"{record.case_id} is registered as {_kind_for_record(record).value} after {record.outcome_status.value}.",
        )
        for index, record in enumerate((record for record in resolved_ledger.records if record.exception_candidate), start=1)
    )
    if not exceptions:
        raise ValueError("exception register requires at least one exception case")

    severity = "warning"
    status = "exception-tracked"
    if any(item.severity is ExceptionSeverity.CRITICAL for item in exceptions):
        severity = "critical"
        status = "critical-exceptions"

    register_signal = TelemetrySignal(
        signal_name="exception-register",
        boundary=resolved_ledger.ledger_signal.boundary,
        correlation_id=register_id,
        severity=severity,
        status=status,
        metrics={
            "exception_count": float(len(exceptions)),
            "critical_count": float(len([item for item in exceptions if item.severity is ExceptionSeverity.CRITICAL])),
            "high_count": float(len([item for item in exceptions if item.severity is ExceptionSeverity.HIGH])),
            "moderate_count": float(len([item for item in exceptions if item.severity is ExceptionSeverity.MODERATE])),
        },
        labels={"register_id": register_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_ledger.final_snapshot.runtime_stage,
        signals=(register_signal, resolved_ledger.ledger_signal, *resolved_ledger.final_snapshot.signals),
        alerts=resolved_ledger.final_snapshot.alerts,
        audit_entries=resolved_ledger.final_snapshot.audit_entries,
        active_controls=resolved_ledger.final_snapshot.active_controls,
    )
    return ExceptionRegister(
        register_id=register_id,
        outcome_ledger=resolved_ledger,
        exceptions=exceptions,
        register_signal=register_signal,
        final_snapshot=final_snapshot,
    )
