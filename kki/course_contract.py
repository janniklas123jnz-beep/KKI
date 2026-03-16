"""Course contract fixing conclave selections into durable Leitstern agreements."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .priority_conclave import (
    ConclaveMotion,
    ConclavePriority,
    ConclaveStatus,
    PriorityConclave,
    build_priority_conclave,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class ContractParty(str, Enum):
    """Primary Leitstern party carrying the contract."""

    STEWARD_ASSEMBLY = "steward-assembly"
    GOVERNANCE_ASSEMBLY = "governance-assembly"
    AUTONOMY_ASSEMBLY = "autonomy-assembly"


class ContractCommitment(str, Enum):
    """Commitment level written into the course contract."""

    HOLD_LINE = "hold-line"
    ALIGN_LINE = "align-line"
    ADVANCE_LINE = "advance-line"


class ContractStatus(str, Enum):
    """Binding level of one course contract clause."""

    PROTECTIVE = "protective"
    OPERATIVE = "operative"
    BINDING = "binding"


@dataclass(frozen=True)
class ContractClause:
    """One durable contract clause derived from a conclave motion."""

    clause_id: str
    sequence: int
    motion_id: str
    mission_ref: str
    contract_party: ContractParty
    contract_commitment: ContractCommitment
    contract_status: ContractStatus
    case_ids: tuple[str, ...]
    release_ready: bool
    contract_strength: float
    enforcement_window: int
    contract_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "clause_id", _non_empty(self.clause_id, field_name="clause_id"))
        object.__setattr__(self, "motion_id", _non_empty(self.motion_id, field_name="motion_id"))
        object.__setattr__(self, "mission_ref", _non_empty(self.mission_ref, field_name="mission_ref"))
        object.__setattr__(self, "contract_strength", _clamp01(self.contract_strength))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.enforcement_window < 1:
            raise ValueError("enforcement_window must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "clause_id": self.clause_id,
            "sequence": self.sequence,
            "motion_id": self.motion_id,
            "mission_ref": self.mission_ref,
            "contract_party": self.contract_party.value,
            "contract_commitment": self.contract_commitment.value,
            "contract_status": self.contract_status.value,
            "case_ids": list(self.case_ids),
            "release_ready": self.release_ready,
            "contract_strength": self.contract_strength,
            "enforcement_window": self.enforcement_window,
            "contract_tags": list(self.contract_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class CourseContract:
    """Durable leadership contract over the prioritized Leitstern course."""

    contract_id: str
    priority_conclave: PriorityConclave
    clauses: tuple[ContractClause, ...]
    contract_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "contract_id", _non_empty(self.contract_id, field_name="contract_id"))

    @property
    def protective_clause_ids(self) -> tuple[str, ...]:
        return tuple(clause.clause_id for clause in self.clauses if clause.contract_status is ContractStatus.PROTECTIVE)

    @property
    def operative_clause_ids(self) -> tuple[str, ...]:
        return tuple(clause.clause_id for clause in self.clauses if clause.contract_status is ContractStatus.OPERATIVE)

    @property
    def binding_clause_ids(self) -> tuple[str, ...]:
        return tuple(clause.clause_id for clause in self.clauses if clause.contract_status is ContractStatus.BINDING)

    def to_dict(self) -> dict[str, object]:
        return {
            "contract_id": self.contract_id,
            "priority_conclave": self.priority_conclave.to_dict(),
            "clauses": [clause.to_dict() for clause in self.clauses],
            "contract_signal": self.contract_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "protective_clause_ids": list(self.protective_clause_ids),
            "operative_clause_ids": list(self.operative_clause_ids),
            "binding_clause_ids": list(self.binding_clause_ids),
        }


def _party(motion: ConclaveMotion) -> ContractParty:
    return {
        ConclavePriority.STABILITY_FIRST: ContractParty.STEWARD_ASSEMBLY,
        ConclavePriority.GOVERNANCE_FOCUS: ContractParty.GOVERNANCE_ASSEMBLY,
        ConclavePriority.RELEASE_VECTOR: ContractParty.AUTONOMY_ASSEMBLY,
    }[motion.conclave_priority]


def _commitment(motion: ConclaveMotion) -> ContractCommitment:
    return {
        ConclaveStatus.GUARDED: ContractCommitment.HOLD_LINE,
        ConclaveStatus.SHORTLISTED: ContractCommitment.ALIGN_LINE,
        ConclaveStatus.ELECTED: ContractCommitment.ADVANCE_LINE,
    }[motion.conclave_status]


def _status(motion: ConclaveMotion) -> ContractStatus:
    return {
        ConclaveStatus.GUARDED: ContractStatus.PROTECTIVE,
        ConclaveStatus.SHORTLISTED: ContractStatus.OPERATIVE,
        ConclaveStatus.ELECTED: ContractStatus.BINDING,
    }[motion.conclave_status]


def _contract_strength(motion: ConclaveMotion) -> float:
    bonus = {
        ContractStatus.PROTECTIVE: 0.0,
        ContractStatus.OPERATIVE: 0.06,
        ContractStatus.BINDING: 0.12,
    }[_status(motion)]
    return round(min(1.0, motion.priority_score + bonus), 3)


def _enforcement_window(motion: ConclaveMotion) -> int:
    if motion.conclave_status is ConclaveStatus.GUARDED:
        return motion.vote_window
    if motion.conclave_status is ConclaveStatus.SHORTLISTED:
        return motion.vote_window + 1
    return motion.vote_window + 2


def build_course_contract(
    priority_conclave: PriorityConclave | None = None,
    *,
    contract_id: str = "course-contract",
) -> CourseContract:
    """Build the durable leadership contract over the prioritized course."""

    resolved_conclave = (
        build_priority_conclave(conclave_id=f"{contract_id}-conclave")
        if priority_conclave is None
        else priority_conclave
    )
    clauses = tuple(
        ContractClause(
            clause_id=f"{contract_id}-{motion.motion_id.removeprefix(f'{resolved_conclave.conclave_id}-')}",
            sequence=index,
            motion_id=motion.motion_id,
            mission_ref=motion.mission_ref,
            contract_party=_party(motion),
            contract_commitment=_commitment(motion),
            contract_status=_status(motion),
            case_ids=motion.case_ids,
            release_ready=motion.release_ready and _status(motion) is ContractStatus.BINDING,
            contract_strength=_contract_strength(motion),
            enforcement_window=_enforcement_window(motion),
            contract_tags=tuple(
                dict.fromkeys(
                    (
                        *motion.conclave_tags,
                        _party(motion).value,
                        _commitment(motion).value,
                        _status(motion).value,
                    )
                )
            ),
            summary=(
                f"{motion.motion_id} is fixed as {_commitment(motion).value} under "
                f"{_party(motion).value} with {_status(motion).value} force."
            ),
        )
        for index, motion in enumerate(resolved_conclave.motions, start=1)
    )
    if not clauses:
        raise ValueError("course contract requires at least one clause")

    severity = "info"
    status = "contract-binding"
    if any(clause.contract_status is ContractStatus.PROTECTIVE for clause in clauses):
        severity = "critical"
        status = "contract-protective"
    elif any(clause.contract_status is ContractStatus.OPERATIVE for clause in clauses):
        severity = "warning"
        status = "contract-operative"

    contract_signal = TelemetrySignal(
        signal_name="course-contract",
        boundary=resolved_conclave.conclave_signal.boundary,
        correlation_id=contract_id,
        severity=severity,
        status=status,
        metrics={
            "clause_count": float(len(clauses)),
            "protective_count": float(
                len([clause for clause in clauses if clause.contract_status is ContractStatus.PROTECTIVE])
            ),
            "operative_count": float(len([clause for clause in clauses if clause.contract_status is ContractStatus.OPERATIVE])),
            "binding_count": float(len([clause for clause in clauses if clause.contract_status is ContractStatus.BINDING])),
            "release_ready_count": float(len([clause for clause in clauses if clause.release_ready])),
            "avg_contract_strength": round(sum(clause.contract_strength for clause in clauses) / len(clauses), 3),
        },
        labels={"contract_id": contract_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_conclave.final_snapshot.runtime_stage,
        signals=(contract_signal, *resolved_conclave.final_snapshot.signals),
        alerts=resolved_conclave.final_snapshot.alerts,
        audit_entries=resolved_conclave.final_snapshot.audit_entries,
        active_controls=resolved_conclave.final_snapshot.active_controls,
    )
    return CourseContract(
        contract_id=contract_id,
        priority_conclave=resolved_conclave,
        clauses=clauses,
        contract_signal=contract_signal,
        final_snapshot=final_snapshot,
    )
