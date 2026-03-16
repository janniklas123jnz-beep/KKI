"""Leitstern codex canonizing decision order, delegation, diplomacy, and contract."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .course_contract import ContractClause, ContractStatus, CourseContract, build_course_contract
from .delegation_matrix import DelegationEntry, DelegationMatrix
from .directive_consensus import ConsensusDirective, DirectiveConsensus
from .priority_conclave import PriorityConclave
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class CodexCanon(str, Enum):
    """Canonical Leitstern canon carried by one codex section."""

    DECISION_CANON = "decision-canon"
    GOVERNANCE_CANON = "governance-canon"
    EXPANSION_CANON = "expansion-canon"


class CodexAxis(str, Enum):
    """Primary axis stitched together by the codex."""

    DECISION_ORDER = "decision-order"
    DELEGATION_ORDER = "delegation-order"
    DIPLOMACY_ORDER = "diplomacy-order"


class CodexStatus(str, Enum):
    """Canonical force of one codex section."""

    GUARDED = "guarded"
    GOVERNED = "governed"
    CANONICAL = "canonical"


@dataclass(frozen=True)
class CodexSection:
    """One canonical codex section derived from a contract clause."""

    section_id: str
    sequence: int
    clause_id: str
    directive_id: str
    delegation_id: str
    mission_ref: str
    codex_canon: CodexCanon
    codex_axis: CodexAxis
    codex_status: CodexStatus
    case_ids: tuple[str, ...]
    release_ready: bool
    codex_strength: float
    codex_window: int
    codex_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "section_id", _non_empty(self.section_id, field_name="section_id"))
        object.__setattr__(self, "clause_id", _non_empty(self.clause_id, field_name="clause_id"))
        object.__setattr__(self, "directive_id", _non_empty(self.directive_id, field_name="directive_id"))
        object.__setattr__(self, "delegation_id", _non_empty(self.delegation_id, field_name="delegation_id"))
        object.__setattr__(self, "mission_ref", _non_empty(self.mission_ref, field_name="mission_ref"))
        object.__setattr__(self, "codex_strength", _clamp01(self.codex_strength))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.codex_window < 1:
            raise ValueError("codex_window must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "section_id": self.section_id,
            "sequence": self.sequence,
            "clause_id": self.clause_id,
            "directive_id": self.directive_id,
            "delegation_id": self.delegation_id,
            "mission_ref": self.mission_ref,
            "codex_canon": self.codex_canon.value,
            "codex_axis": self.codex_axis.value,
            "codex_status": self.codex_status.value,
            "case_ids": list(self.case_ids),
            "release_ready": self.release_ready,
            "codex_strength": self.codex_strength,
            "codex_window": self.codex_window,
            "codex_tags": list(self.codex_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class LeitsternCodex:
    """Canonical codex pulling together the full Leitstern institutional stack."""

    codex_id: str
    course_contract: CourseContract
    directive_consensus: DirectiveConsensus
    delegation_matrix: DelegationMatrix
    sections: tuple[CodexSection, ...]
    codex_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "codex_id", _non_empty(self.codex_id, field_name="codex_id"))

    @property
    def guarded_section_ids(self) -> tuple[str, ...]:
        return tuple(section.section_id for section in self.sections if section.codex_status is CodexStatus.GUARDED)

    @property
    def governed_section_ids(self) -> tuple[str, ...]:
        return tuple(section.section_id for section in self.sections if section.codex_status is CodexStatus.GOVERNED)

    @property
    def canonical_section_ids(self) -> tuple[str, ...]:
        return tuple(section.section_id for section in self.sections if section.codex_status is CodexStatus.CANONICAL)

    def to_dict(self) -> dict[str, object]:
        return {
            "codex_id": self.codex_id,
            "course_contract": self.course_contract.to_dict(),
            "directive_consensus": self.directive_consensus.to_dict(),
            "delegation_matrix": self.delegation_matrix.to_dict(),
            "sections": [section.to_dict() for section in self.sections],
            "codex_signal": self.codex_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "guarded_section_ids": list(self.guarded_section_ids),
            "governed_section_ids": list(self.governed_section_ids),
            "canonical_section_ids": list(self.canonical_section_ids),
        }


def _canon(clause: ContractClause) -> CodexCanon:
    return {
        ContractStatus.PROTECTIVE: CodexCanon.DECISION_CANON,
        ContractStatus.OPERATIVE: CodexCanon.GOVERNANCE_CANON,
        ContractStatus.BINDING: CodexCanon.EXPANSION_CANON,
    }[clause.contract_status]


def _axis(clause: ContractClause) -> CodexAxis:
    return {
        ContractStatus.PROTECTIVE: CodexAxis.DECISION_ORDER,
        ContractStatus.OPERATIVE: CodexAxis.DELEGATION_ORDER,
        ContractStatus.BINDING: CodexAxis.DIPLOMACY_ORDER,
    }[clause.contract_status]


def _status(clause: ContractClause) -> CodexStatus:
    return {
        ContractStatus.PROTECTIVE: CodexStatus.GUARDED,
        ContractStatus.OPERATIVE: CodexStatus.GOVERNED,
        ContractStatus.BINDING: CodexStatus.CANONICAL,
    }[clause.contract_status]


def _resolve_chain(contract: CourseContract) -> tuple[PriorityConclave, DirectiveConsensus, DelegationMatrix]:
    conclave = contract.priority_conclave
    diplomacy = conclave.consensus_diplomacy
    delegation_matrix = diplomacy.veto_sluice.delegation_matrix
    directive_consensus = delegation_matrix.execution_cabinet.decision_archive.directive_consensus
    return conclave, directive_consensus, delegation_matrix


def _directive_for_clause(clause: ContractClause, directive_consensus: DirectiveConsensus) -> ConsensusDirective:
    directives = {
        ContractStatus.PROTECTIVE: directive_consensus.directives[0],
        ContractStatus.OPERATIVE: directive_consensus.directives[1],
        ContractStatus.BINDING: directive_consensus.directives[2],
    }
    return directives[clause.contract_status]


def _delegation_for_clause(clause: ContractClause, delegation_matrix: DelegationMatrix) -> DelegationEntry:
    entries = {
        ContractStatus.PROTECTIVE: delegation_matrix.delegations[0],
        ContractStatus.OPERATIVE: delegation_matrix.delegations[1],
        ContractStatus.BINDING: delegation_matrix.delegations[2],
    }
    return entries[clause.contract_status]


def _codex_strength(clause: ContractClause) -> float:
    bonus = {
        CodexStatus.GUARDED: 0.0,
        CodexStatus.GOVERNED: 0.04,
        CodexStatus.CANONICAL: 0.1,
    }[_status(clause)]
    return round(min(1.0, clause.contract_strength + bonus), 3)


def _codex_window(clause: ContractClause) -> int:
    if clause.contract_status is ContractStatus.PROTECTIVE:
        return clause.enforcement_window
    if clause.contract_status is ContractStatus.OPERATIVE:
        return clause.enforcement_window + 1
    return clause.enforcement_window + 2


def build_leitstern_codex(
    course_contract: CourseContract | None = None,
    *,
    codex_id: str = "leitstern-codex",
) -> LeitsternCodex:
    """Build the canonical Leitstern codex over the completed institutional stack."""

    resolved_contract = build_course_contract(contract_id=f"{codex_id}-contract") if course_contract is None else course_contract
    _, resolved_directive_consensus, resolved_delegation_matrix = _resolve_chain(resolved_contract)
    sections = tuple(
        CodexSection(
            section_id=f"{codex_id}-{clause.clause_id.removeprefix(f'{resolved_contract.contract_id}-')}",
            sequence=index,
            clause_id=clause.clause_id,
            directive_id=_directive_for_clause(clause, resolved_directive_consensus).directive_id,
            delegation_id=_delegation_for_clause(clause, resolved_delegation_matrix).delegation_id,
            mission_ref=clause.mission_ref,
            codex_canon=_canon(clause),
            codex_axis=_axis(clause),
            codex_status=_status(clause),
            case_ids=tuple(
                dict.fromkeys(
                    (
                        *clause.case_ids,
                        *_directive_for_clause(clause, resolved_directive_consensus).case_ids,
                        *_delegation_for_clause(clause, resolved_delegation_matrix).case_ids,
                    )
                )
            ),
            release_ready=clause.release_ready and _status(clause) is CodexStatus.CANONICAL,
            codex_strength=_codex_strength(clause),
            codex_window=_codex_window(clause),
            codex_tags=tuple(
                dict.fromkeys(
                    (
                        *clause.contract_tags,
                        _canon(clause).value,
                        _axis(clause).value,
                        _status(clause).value,
                    )
                )
            ),
            summary=(
                f"{clause.clause_id} canonizes {_directive_for_clause(clause, resolved_directive_consensus).directive_id}, "
                f"{_delegation_for_clause(clause, resolved_delegation_matrix).delegation_id} and {clause.motion_id} as "
                f"{_status(clause).value} Leitstern law."
            ),
        )
        for index, clause in enumerate(resolved_contract.clauses, start=1)
    )
    if not sections:
        raise ValueError("leitstern codex requires at least one section")

    severity = "info"
    status = "codex-canonical"
    if any(section.codex_status is CodexStatus.GUARDED for section in sections):
        severity = "critical"
        status = "codex-guarded"
    elif any(section.codex_status is CodexStatus.GOVERNED for section in sections):
        severity = "warning"
        status = "codex-governed"

    codex_signal = TelemetrySignal(
        signal_name="leitstern-codex",
        boundary=resolved_contract.contract_signal.boundary,
        correlation_id=codex_id,
        severity=severity,
        status=status,
        metrics={
            "section_count": float(len(sections)),
            "guarded_count": float(len([section for section in sections if section.codex_status is CodexStatus.GUARDED])),
            "governed_count": float(len([section for section in sections if section.codex_status is CodexStatus.GOVERNED])),
            "canonical_count": float(len([section for section in sections if section.codex_status is CodexStatus.CANONICAL])),
            "release_ready_count": float(len([section for section in sections if section.release_ready])),
            "avg_codex_strength": round(sum(section.codex_strength for section in sections) / len(sections), 3),
        },
        labels={"codex_id": codex_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_contract.final_snapshot.runtime_stage,
        signals=(codex_signal, *resolved_contract.final_snapshot.signals),
        alerts=resolved_contract.final_snapshot.alerts,
        audit_entries=resolved_contract.final_snapshot.audit_entries,
        active_controls=resolved_contract.final_snapshot.active_controls,
    )
    return LeitsternCodex(
        codex_id=codex_id,
        course_contract=resolved_contract,
        directive_consensus=resolved_directive_consensus,
        delegation_matrix=resolved_delegation_matrix,
        sections=sections,
        codex_signal=codex_signal,
        final_snapshot=final_snapshot,
    )
