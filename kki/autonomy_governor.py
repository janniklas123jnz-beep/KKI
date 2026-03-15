"""Autonomy governor for controlled delegation of compiled playbooks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .exception_register import ExceptionCase, ExceptionRegister, build_exception_register
from .governance_agenda import GovernanceAgenda, GovernanceAgendaItem, build_governance_agenda
from .playbook_catalog import PlaybookCatalog, PlaybookEntry, PlaybookReadiness, build_playbook_catalog
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


class AutonomyDecision(str, Enum):
    """Delegation decision taken for a compiled playbook."""

    AUTONOMOUS = "autonomous"
    GOVERNANCE_REQUIRED = "governance-required"
    STEWARD_REQUIRED = "steward-required"


@dataclass(frozen=True)
class AutonomyAssignment:
    """Autonomy routing decision for one playbook case."""

    assignment_id: str
    case_id: str
    sequence: int
    decision: AutonomyDecision
    playbook_readiness: PlaybookReadiness
    automation_allowed: bool
    governance_required: bool
    control_tags: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    commitment_refs: tuple[str, ...]
    rationale: str
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "assignment_id", _non_empty(self.assignment_id, field_name="assignment_id"))
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))
        object.__setattr__(self, "rationale", _non_empty(self.rationale, field_name="rationale"))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")

    def to_dict(self) -> dict[str, object]:
        return {
            "assignment_id": self.assignment_id,
            "case_id": self.case_id,
            "sequence": self.sequence,
            "decision": self.decision.value,
            "playbook_readiness": self.playbook_readiness.value,
            "automation_allowed": self.automation_allowed,
            "governance_required": self.governance_required,
            "control_tags": list(self.control_tags),
            "evidence_refs": list(self.evidence_refs),
            "commitment_refs": list(self.commitment_refs),
            "rationale": self.rationale,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class AutonomyGovernor:
    """Controlled delegation layer over compiled operating playbooks."""

    governor_id: str
    playbook_catalog: PlaybookCatalog
    governance_agenda: GovernanceAgenda
    exception_register: ExceptionRegister
    assignments: tuple[AutonomyAssignment, ...]
    governor_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "governor_id", _non_empty(self.governor_id, field_name="governor_id"))

    @property
    def autonomous_case_ids(self) -> tuple[str, ...]:
        return tuple(item.case_id for item in self.assignments if item.decision is AutonomyDecision.AUTONOMOUS)

    @property
    def governance_required_case_ids(self) -> tuple[str, ...]:
        return tuple(item.case_id for item in self.assignments if item.decision is AutonomyDecision.GOVERNANCE_REQUIRED)

    @property
    def steward_required_case_ids(self) -> tuple[str, ...]:
        return tuple(item.case_id for item in self.assignments if item.decision is AutonomyDecision.STEWARD_REQUIRED)

    def to_dict(self) -> dict[str, object]:
        return {
            "governor_id": self.governor_id,
            "playbook_catalog": self.playbook_catalog.to_dict(),
            "governance_agenda": self.governance_agenda.to_dict(),
            "exception_register": self.exception_register.to_dict(),
            "assignments": [assignment.to_dict() for assignment in self.assignments],
            "governor_signal": self.governor_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "autonomous_case_ids": list(self.autonomous_case_ids),
            "governance_required_case_ids": list(self.governance_required_case_ids),
            "steward_required_case_ids": list(self.steward_required_case_ids),
        }


def _decision_for_case(
    playbook: PlaybookEntry,
    agenda_item: GovernanceAgendaItem | None,
    exception_case: ExceptionCase | None,
) -> AutonomyDecision:
    if exception_case is not None:
        return AutonomyDecision.STEWARD_REQUIRED
    if agenda_item is not None or playbook.readiness is PlaybookReadiness.GOVERNED_STANDARD:
        return AutonomyDecision.GOVERNANCE_REQUIRED
    return AutonomyDecision.AUTONOMOUS


def _control_tags(
    decision: AutonomyDecision,
    agenda_item: GovernanceAgendaItem | None,
    exception_case: ExceptionCase | None,
) -> tuple[str, ...]:
    if decision is AutonomyDecision.STEWARD_REQUIRED:
        return (
            "manual-oversight",
            "exception-escalation",
            f"exception:{exception_case.kind.value}" if exception_case is not None else "exception:unknown",
        )
    if decision is AutonomyDecision.GOVERNANCE_REQUIRED:
        queue = agenda_item.agenda_status.value if agenda_item is not None else "governed-standard"
        return ("approval-gate", "change-record", f"governance:{queue}")
    return ("telemetry-watch", "rollback-ready", "bounded-autonomy")


def _rationale(
    case_id: str,
    decision: AutonomyDecision,
    agenda_item: GovernanceAgendaItem | None,
    exception_case: ExceptionCase | None,
) -> str:
    if decision is AutonomyDecision.STEWARD_REQUIRED and exception_case is not None:
        return f"{case_id} stays under steward control because {exception_case.kind.value} remains active."
    if decision is AutonomyDecision.GOVERNANCE_REQUIRED and agenda_item is not None:
        return f"{case_id} requires governance handling through the {agenda_item.agenda_status.value} agenda lane."
    if decision is AutonomyDecision.GOVERNANCE_REQUIRED:
        return f"{case_id} remains a governed standard and needs an approval gate before execution."
    return f"{case_id} qualifies for bounded autonomous execution under active telemetry watch."


def build_autonomy_governor(
    playbook_catalog: PlaybookCatalog | None = None,
    governance_agenda: GovernanceAgenda | None = None,
    exception_register: ExceptionRegister | None = None,
    *,
    governor_id: str = "autonomy-governor",
) -> AutonomyGovernor:
    """Build a governor that decides which playbooks may execute autonomously."""

    resolved_catalog = build_playbook_catalog(catalog_id=f"{governor_id}-catalog") if playbook_catalog is None else playbook_catalog
    resolved_agenda = build_governance_agenda(agenda_id=f"{governor_id}-agenda") if governance_agenda is None else governance_agenda
    resolved_exceptions = (
        build_exception_register(register_id=f"{governor_id}-exceptions") if exception_register is None else exception_register
    )
    agenda_by_case = {item.case_id: item for item in resolved_agenda.items}
    exception_by_case = {item.case_id: item for item in resolved_exceptions.exceptions}
    assignments = tuple(
        AutonomyAssignment(
            assignment_id=f"{governor_id}-{playbook.case_id}",
            case_id=playbook.case_id,
            sequence=index,
            decision=_decision_for_case(
                playbook,
                agenda_by_case.get(playbook.case_id),
                exception_by_case.get(playbook.case_id),
            ),
            playbook_readiness=playbook.readiness,
            automation_allowed=_decision_for_case(
                playbook,
                agenda_by_case.get(playbook.case_id),
                exception_by_case.get(playbook.case_id),
            )
            is AutonomyDecision.AUTONOMOUS,
            governance_required=_decision_for_case(
                playbook,
                agenda_by_case.get(playbook.case_id),
                exception_by_case.get(playbook.case_id),
            )
            is AutonomyDecision.GOVERNANCE_REQUIRED,
            control_tags=_control_tags(
                _decision_for_case(
                    playbook,
                    agenda_by_case.get(playbook.case_id),
                    exception_by_case.get(playbook.case_id),
                ),
                agenda_by_case.get(playbook.case_id),
                exception_by_case.get(playbook.case_id),
            ),
            evidence_refs=playbook.trigger_refs,
            commitment_refs=playbook.commitment_refs,
            rationale=_rationale(
                playbook.case_id,
                _decision_for_case(
                    playbook,
                    agenda_by_case.get(playbook.case_id),
                    exception_by_case.get(playbook.case_id),
                ),
                agenda_by_case.get(playbook.case_id),
                exception_by_case.get(playbook.case_id),
            ),
            summary=(
                f"{playbook.case_id} is routed as "
                f"{_decision_for_case(playbook, agenda_by_case.get(playbook.case_id), exception_by_case.get(playbook.case_id)).value}."
            ),
        )
        for index, playbook in enumerate(resolved_catalog.playbooks, start=1)
    )
    if not assignments:
        raise ValueError("autonomy governor requires at least one assignment")

    severity = "info"
    status = "governed-autonomy"
    if any(item.decision is AutonomyDecision.STEWARD_REQUIRED for item in assignments):
        severity = "warning"
        status = "steward-guarded"
    if any(item.decision is AutonomyDecision.AUTONOMOUS for item in assignments):
        status = "autonomy-enabled"

    governor_signal = TelemetrySignal(
        signal_name="autonomy-governor",
        boundary=resolved_catalog.catalog_signal.boundary,
        correlation_id=governor_id,
        severity=severity,
        status=status,
        metrics={
            "assignment_count": float(len(assignments)),
            "autonomous_count": float(len([item for item in assignments if item.decision is AutonomyDecision.AUTONOMOUS])),
            "governance_required_count": float(
                len([item for item in assignments if item.decision is AutonomyDecision.GOVERNANCE_REQUIRED])
            ),
            "steward_required_count": float(
                len([item for item in assignments if item.decision is AutonomyDecision.STEWARD_REQUIRED])
            ),
        },
        labels={"governor_id": governor_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_catalog.final_snapshot.runtime_stage,
        signals=(
            governor_signal,
            resolved_catalog.catalog_signal,
            resolved_agenda.agenda_signal,
            resolved_exceptions.register_signal,
            *resolved_catalog.final_snapshot.signals,
        ),
        alerts=resolved_catalog.final_snapshot.alerts,
        audit_entries=resolved_catalog.final_snapshot.audit_entries,
        active_controls=resolved_catalog.final_snapshot.active_controls,
    )
    return AutonomyGovernor(
        governor_id=governor_id,
        playbook_catalog=resolved_catalog,
        governance_agenda=resolved_agenda,
        exception_register=resolved_exceptions,
        assignments=assignments,
        governor_signal=governor_signal,
        final_snapshot=final_snapshot,
    )
