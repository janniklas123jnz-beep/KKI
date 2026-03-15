"""Pre-execution simulator for autonomous and manual interventions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .autonomy_governor import AutonomyAssignment, AutonomyDecision, AutonomyGovernor, build_autonomy_governor
from .exception_register import ExceptionCase, ExceptionKind, ExceptionRegister, build_exception_register
from .outcome_ledger import OutcomeLedger, OutcomeRecord, OutcomeStatus, build_outcome_ledger
from .playbook_catalog import PlaybookType
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class InterventionMode(str, Enum):
    """Execution mode being simulated."""

    AUTONOMOUS = "autonomous"
    GOVERNED = "governed"
    STEWARD = "steward"


class InterventionSimulationStatus(str, Enum):
    """Projected outcome of a planned intervention before execution."""

    READY = "ready"
    GUARDED = "guarded"
    AT_RISK = "at-risk"
    ROLLBACK_RECOMMENDED = "rollback-recommended"


class InterventionFallback(str, Enum):
    """Preferred fallback path if the intervention cannot proceed as planned."""

    OBSERVE_ONLY = "observe-only"
    APPROVAL_GATE = "approval-gate"
    MANUAL_RECOVERY = "manual-recovery"
    ROLLBACK = "rollback"


@dataclass(frozen=True)
class InterventionSimulation:
    """Projected execution trace for one planned intervention."""

    simulation_id: str
    case_id: str
    sequence: int
    intervention_mode: InterventionMode
    autonomy_decision: AutonomyDecision
    playbook_type: PlaybookType
    projected_status: InterventionSimulationStatus
    fallback_path: InterventionFallback
    projected_risk_score: float
    regression_risk: bool
    control_tags: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    commitment_refs: tuple[str, ...]
    rationale: str
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "simulation_id", _non_empty(self.simulation_id, field_name="simulation_id"))
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))
        object.__setattr__(self, "projected_risk_score", _clamp01(self.projected_risk_score))
        object.__setattr__(self, "rationale", _non_empty(self.rationale, field_name="rationale"))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")

    def to_dict(self) -> dict[str, object]:
        return {
            "simulation_id": self.simulation_id,
            "case_id": self.case_id,
            "sequence": self.sequence,
            "intervention_mode": self.intervention_mode.value,
            "autonomy_decision": self.autonomy_decision.value,
            "playbook_type": self.playbook_type.value,
            "projected_status": self.projected_status.value,
            "fallback_path": self.fallback_path.value,
            "projected_risk_score": self.projected_risk_score,
            "regression_risk": self.regression_risk,
            "control_tags": list(self.control_tags),
            "evidence_refs": list(self.evidence_refs),
            "commitment_refs": list(self.commitment_refs),
            "rationale": self.rationale,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class InterventionSimulator:
    """Pre-flight simulation layer over autonomy and exception state."""

    simulator_id: str
    autonomy_governor: AutonomyGovernor
    outcome_ledger: OutcomeLedger
    exception_register: ExceptionRegister
    simulations: tuple[InterventionSimulation, ...]
    simulator_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "simulator_id", _non_empty(self.simulator_id, field_name="simulator_id"))

    @property
    def ready_case_ids(self) -> tuple[str, ...]:
        return tuple(item.case_id for item in self.simulations if item.projected_status is InterventionSimulationStatus.READY)

    @property
    def guarded_case_ids(self) -> tuple[str, ...]:
        return tuple(item.case_id for item in self.simulations if item.projected_status is InterventionSimulationStatus.GUARDED)

    @property
    def at_risk_case_ids(self) -> tuple[str, ...]:
        return tuple(item.case_id for item in self.simulations if item.projected_status is InterventionSimulationStatus.AT_RISK)

    @property
    def rollback_case_ids(self) -> tuple[str, ...]:
        return tuple(
            item.case_id for item in self.simulations if item.projected_status is InterventionSimulationStatus.ROLLBACK_RECOMMENDED
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "simulator_id": self.simulator_id,
            "autonomy_governor": self.autonomy_governor.to_dict(),
            "outcome_ledger": self.outcome_ledger.to_dict(),
            "exception_register": self.exception_register.to_dict(),
            "simulations": [item.to_dict() for item in self.simulations],
            "simulator_signal": self.simulator_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "ready_case_ids": list(self.ready_case_ids),
            "guarded_case_ids": list(self.guarded_case_ids),
            "at_risk_case_ids": list(self.at_risk_case_ids),
            "rollback_case_ids": list(self.rollback_case_ids),
        }


def _mode_for_decision(decision: AutonomyDecision) -> InterventionMode:
    return {
        AutonomyDecision.AUTONOMOUS: InterventionMode.AUTONOMOUS,
        AutonomyDecision.GOVERNANCE_REQUIRED: InterventionMode.GOVERNED,
        AutonomyDecision.STEWARD_REQUIRED: InterventionMode.STEWARD,
    }[decision]


def _projected_status(
    assignment: AutonomyAssignment,
    exception_case: ExceptionCase | None,
) -> InterventionSimulationStatus:
    if exception_case is not None and exception_case.kind is ExceptionKind.POLICY_BREACH:
        return InterventionSimulationStatus.ROLLBACK_RECOMMENDED
    if exception_case is not None:
        return InterventionSimulationStatus.AT_RISK
    if assignment.decision is AutonomyDecision.GOVERNANCE_REQUIRED:
        return InterventionSimulationStatus.GUARDED
    return InterventionSimulationStatus.READY


def _fallback_path(status: InterventionSimulationStatus) -> InterventionFallback:
    return {
        InterventionSimulationStatus.READY: InterventionFallback.OBSERVE_ONLY,
        InterventionSimulationStatus.GUARDED: InterventionFallback.APPROVAL_GATE,
        InterventionSimulationStatus.AT_RISK: InterventionFallback.MANUAL_RECOVERY,
        InterventionSimulationStatus.ROLLBACK_RECOMMENDED: InterventionFallback.ROLLBACK,
    }[status]


def _projected_risk_score(
    assignment: AutonomyAssignment,
    outcome_record: OutcomeRecord,
    exception_case: ExceptionCase | None,
) -> float:
    if exception_case is not None and exception_case.kind is ExceptionKind.POLICY_BREACH:
        return 0.86
    if exception_case is not None and exception_case.kind is ExceptionKind.UNRESOLVED:
        return 0.74
    if assignment.decision is AutonomyDecision.GOVERNANCE_REQUIRED:
        return 0.48 if outcome_record.outcome_status is OutcomeStatus.GOVERNED else 0.54
    return 0.22 if outcome_record.outcome_status is OutcomeStatus.OBSERVED else 0.34


def _regression_risk(
    status: InterventionSimulationStatus,
    outcome_record: OutcomeRecord,
) -> bool:
    return status in {
        InterventionSimulationStatus.AT_RISK,
        InterventionSimulationStatus.ROLLBACK_RECOMMENDED,
    } or outcome_record.outcome_status is OutcomeStatus.TUNED


def _rationale(
    case_id: str,
    status: InterventionSimulationStatus,
    assignment: AutonomyAssignment,
    exception_case: ExceptionCase | None,
) -> str:
    if status is InterventionSimulationStatus.ROLLBACK_RECOMMENDED and exception_case is not None:
        return f"{case_id} should be rolled back in rehearsal because {exception_case.kind.value} remains critical."
    if status is InterventionSimulationStatus.AT_RISK and exception_case is not None:
        return f"{case_id} remains at risk because {exception_case.kind.value} is still unresolved before execution."
    if status is InterventionSimulationStatus.GUARDED:
        return f"{case_id} can proceed only through the governance gate defined by the autonomy governor."
    return f"{case_id} is stable enough for bounded autonomous execution with telemetry watch."


def build_intervention_simulator(
    autonomy_governor: AutonomyGovernor | None = None,
    outcome_ledger: OutcomeLedger | None = None,
    exception_register: ExceptionRegister | None = None,
    *,
    simulator_id: str = "intervention-simulator",
) -> InterventionSimulator:
    """Build a pre-execution simulator for planned interventions."""

    resolved_governor = (
        build_autonomy_governor(governor_id=f"{simulator_id}-governor") if autonomy_governor is None else autonomy_governor
    )
    resolved_outcomes = build_outcome_ledger(ledger_id=f"{simulator_id}-outcomes") if outcome_ledger is None else outcome_ledger
    resolved_exceptions = (
        build_exception_register(register_id=f"{simulator_id}-exceptions") if exception_register is None else exception_register
    )
    outcome_by_case = {record.case_id: record for record in resolved_outcomes.records}
    exception_by_case = {record.case_id: record for record in resolved_exceptions.exceptions}
    playbook_by_case = {record.case_id: record for record in resolved_governor.playbook_catalog.playbooks}
    simulations = tuple(
        InterventionSimulation(
            simulation_id=f"{simulator_id}-{assignment.case_id}",
            case_id=assignment.case_id,
            sequence=index,
            intervention_mode=_mode_for_decision(assignment.decision),
            autonomy_decision=assignment.decision,
            playbook_type=playbook_by_case[assignment.case_id].playbook_type,
            projected_status=_projected_status(assignment, exception_by_case.get(assignment.case_id)),
            fallback_path=_fallback_path(_projected_status(assignment, exception_by_case.get(assignment.case_id))),
            projected_risk_score=_projected_risk_score(
                assignment,
                outcome_by_case[assignment.case_id],
                exception_by_case.get(assignment.case_id),
            ),
            regression_risk=_regression_risk(
                _projected_status(assignment, exception_by_case.get(assignment.case_id)),
                outcome_by_case[assignment.case_id],
            ),
            control_tags=tuple(
                dict.fromkeys(
                    (*assignment.control_tags, *playbook_by_case[assignment.case_id].guardrail_notes)
                )
            ),
            evidence_refs=assignment.evidence_refs,
            commitment_refs=assignment.commitment_refs,
            rationale=_rationale(
                assignment.case_id,
                _projected_status(assignment, exception_by_case.get(assignment.case_id)),
                assignment,
                exception_by_case.get(assignment.case_id),
            ),
            summary=(
                f"{assignment.case_id} is projected as "
                f"{_projected_status(assignment, exception_by_case.get(assignment.case_id)).value} "
                f"with fallback {_fallback_path(_projected_status(assignment, exception_by_case.get(assignment.case_id))).value}."
            ),
        )
        for index, assignment in enumerate(resolved_governor.assignments, start=1)
    )
    if not simulations:
        raise ValueError("intervention simulator requires at least one simulation")

    severity = "info"
    status = "ready-interventions"
    if any(item.projected_status is InterventionSimulationStatus.ROLLBACK_RECOMMENDED for item in simulations):
        severity = "critical"
        status = "rollback-recommended"
    elif any(item.projected_status is InterventionSimulationStatus.AT_RISK for item in simulations):
        severity = "warning"
        status = "at-risk-interventions"
    elif any(item.projected_status is InterventionSimulationStatus.GUARDED for item in simulations):
        severity = "warning"
        status = "guarded-interventions"

    simulator_signal = TelemetrySignal(
        signal_name="intervention-simulator",
        boundary=resolved_governor.governor_signal.boundary,
        correlation_id=simulator_id,
        severity=severity,
        status=status,
        metrics={
            "simulation_count": float(len(simulations)),
            "ready_count": float(
                len([item for item in simulations if item.projected_status is InterventionSimulationStatus.READY])
            ),
            "guarded_count": float(
                len([item for item in simulations if item.projected_status is InterventionSimulationStatus.GUARDED])
            ),
            "at_risk_count": float(
                len([item for item in simulations if item.projected_status is InterventionSimulationStatus.AT_RISK])
            ),
            "rollback_count": float(
                len(
                    [
                        item
                        for item in simulations
                        if item.projected_status is InterventionSimulationStatus.ROLLBACK_RECOMMENDED
                    ]
                )
            ),
        },
        labels={"simulator_id": simulator_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_governor.final_snapshot.runtime_stage,
        signals=(
            simulator_signal,
            resolved_governor.governor_signal,
            resolved_outcomes.ledger_signal,
            resolved_exceptions.register_signal,
            *resolved_governor.final_snapshot.signals,
        ),
        alerts=resolved_governor.final_snapshot.alerts,
        audit_entries=resolved_governor.final_snapshot.audit_entries,
        active_controls=resolved_governor.final_snapshot.active_controls,
    )
    return InterventionSimulator(
        simulator_id=simulator_id,
        autonomy_governor=resolved_governor,
        outcome_ledger=resolved_outcomes,
        exception_register=resolved_exceptions,
        simulations=simulations,
        simulator_signal=simulator_signal,
        final_snapshot=final_snapshot,
    )
