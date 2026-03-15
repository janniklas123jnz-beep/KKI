"""Operations steward that unifies capacity, governance, recovery, policy, and learning."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .capacity_planner import CapacityPlanner, CapacityWindow, build_capacity_planner
from .escalation_router import EscalationRoutePath
from .governance_agenda import GovernanceAgenda, GovernanceAgendaItem, GovernanceAgendaStatus, build_governance_agenda
from .learning_register import LearningPatternType, LearningRecord, LearningRegister, build_learning_register
from .policy_tuner import PolicyTuneAction, PolicyTuneEntry, PolicyTuner, build_policy_tuner
from .recovery_drills import RecoveryDrill, RecoveryDrillStatus, RecoveryDrillSuite, build_recovery_drill_suite
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _agenda_item_by_case(agenda: GovernanceAgenda) -> dict[str, GovernanceAgendaItem]:
    return {item.case_id: item for item in agenda.items}


def _drill_by_case(drills: RecoveryDrillSuite) -> dict[str, RecoveryDrill]:
    return {drill.case_id: drill for drill in drills.drills}


def _tune_by_case(tuner: PolicyTuner) -> dict[str, PolicyTuneEntry]:
    return {entry.case_id: entry for entry in tuner.entries}


def _learning_by_case(register: LearningRegister) -> dict[str, LearningRecord]:
    return {record.case_id: record for record in register.records}


class StewardDirectiveType(str, Enum):
    """Canonical steering directives across the operations control stack."""

    STABILIZE = "stabilize"
    GOVERN = "govern"
    ADAPT = "adapt"
    MONITOR = "monitor"


class OperationsStewardStatus(str, Enum):
    """Overall operating state of the unified steward."""

    CRITICAL = "critical"
    ACTIVE = "active"
    STABLE = "stable"


@dataclass(frozen=True)
class StewardDirective:
    """Unified case directive synthesized from all operational control layers."""

    directive_id: str
    case_id: str
    sequence: int
    directive_type: StewardDirectiveType
    window: CapacityWindow
    route_path: EscalationRoutePath
    policy_action: PolicyTuneAction
    learning_pattern: LearningPatternType
    confidence_score: float
    evidence_refs: tuple[str, ...]
    commitment_refs: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "directive_id", _non_empty(self.directive_id, field_name="directive_id"))
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if not 0.0 <= float(self.confidence_score) <= 1.0:
            raise ValueError("confidence_score must be between 0.0 and 1.0")
        object.__setattr__(self, "confidence_score", float(self.confidence_score))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")

    def to_dict(self) -> dict[str, object]:
        return {
            "directive_id": self.directive_id,
            "case_id": self.case_id,
            "sequence": self.sequence,
            "directive_type": self.directive_type.value,
            "window": self.window.value,
            "route_path": self.route_path.value,
            "policy_action": self.policy_action.value,
            "learning_pattern": self.learning_pattern.value,
            "confidence_score": self.confidence_score,
            "evidence_refs": list(self.evidence_refs),
            "commitment_refs": list(self.commitment_refs),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class OperationsSteward:
    """Unified steering instance over the full readiness control loop."""

    steward_id: str
    capacity_planner: CapacityPlanner
    governance_agenda: GovernanceAgenda
    recovery_drills: RecoveryDrillSuite
    policy_tuner: PolicyTuner
    learning_register: LearningRegister
    directives: tuple[StewardDirective, ...]
    steward_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "steward_id", _non_empty(self.steward_id, field_name="steward_id"))

    @property
    def stabilize_case_ids(self) -> tuple[str, ...]:
        return tuple(d.case_id for d in self.directives if d.directive_type is StewardDirectiveType.STABILIZE)

    @property
    def govern_case_ids(self) -> tuple[str, ...]:
        return tuple(d.case_id for d in self.directives if d.directive_type is StewardDirectiveType.GOVERN)

    @property
    def adapt_case_ids(self) -> tuple[str, ...]:
        return tuple(d.case_id for d in self.directives if d.directive_type is StewardDirectiveType.ADAPT)

    @property
    def monitor_case_ids(self) -> tuple[str, ...]:
        return tuple(d.case_id for d in self.directives if d.directive_type is StewardDirectiveType.MONITOR)

    def to_dict(self) -> dict[str, object]:
        return {
            "steward_id": self.steward_id,
            "capacity_planner": self.capacity_planner.to_dict(),
            "governance_agenda": self.governance_agenda.to_dict(),
            "recovery_drills": self.recovery_drills.to_dict(),
            "policy_tuner": self.policy_tuner.to_dict(),
            "learning_register": self.learning_register.to_dict(),
            "directives": [directive.to_dict() for directive in self.directives],
            "steward_signal": self.steward_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "stabilize_case_ids": list(self.stabilize_case_ids),
            "govern_case_ids": list(self.govern_case_ids),
            "adapt_case_ids": list(self.adapt_case_ids),
            "monitor_case_ids": list(self.monitor_case_ids),
        }


def _directive_type_for_case(
    case_id: str,
    *,
    agenda_item: GovernanceAgendaItem | None,
    drill: RecoveryDrill | None,
    tune_entry: PolicyTuneEntry,
) -> StewardDirectiveType:
    if drill is not None and drill.status is RecoveryDrillStatus.ACTIVE:
        return StewardDirectiveType.STABILIZE
    if agenda_item is not None and agenda_item.agenda_status is GovernanceAgendaStatus.SCHEDULED:
        return StewardDirectiveType.GOVERN
    if tune_entry.action is PolicyTuneAction.TIGHTEN or tune_entry.action is PolicyTuneAction.CALIBRATE:
        return StewardDirectiveType.ADAPT
    return StewardDirectiveType.MONITOR


def build_operations_steward(
    capacity_planner: CapacityPlanner | None = None,
    governance_agenda: GovernanceAgenda | None = None,
    recovery_drills: RecoveryDrillSuite | None = None,
    policy_tuner: PolicyTuner | None = None,
    learning_register: LearningRegister | None = None,
    *,
    steward_id: str = "operations-steward",
) -> OperationsSteward:
    """Build a unified steward over capacity, governance, recovery, policy, and learning."""

    resolved_planner = build_capacity_planner(planner_id=f"{steward_id}-planner") if capacity_planner is None else capacity_planner
    resolved_agenda = build_governance_agenda(agenda_id=f"{steward_id}-agenda") if governance_agenda is None else governance_agenda
    resolved_drills = build_recovery_drill_suite(suite_id=f"{steward_id}-drills") if recovery_drills is None else recovery_drills
    resolved_tuner = build_policy_tuner(tuner_id=f"{steward_id}-tuner") if policy_tuner is None else policy_tuner
    resolved_register = build_learning_register(register_id=f"{steward_id}-register") if learning_register is None else learning_register

    agenda_by_case = _agenda_item_by_case(resolved_agenda)
    drill_by_case = _drill_by_case(resolved_drills)
    tune_by_case = _tune_by_case(resolved_tuner)
    learning_by_case = _learning_by_case(resolved_register)

    directives = tuple(
        StewardDirective(
            directive_id=f"{steward_id}-{plan_entry.case_id}",
            case_id=plan_entry.case_id,
            sequence=index,
            directive_type=_directive_type_for_case(
                plan_entry.case_id,
                agenda_item=agenda_by_case.get(plan_entry.case_id),
                drill=drill_by_case.get(plan_entry.case_id),
                tune_entry=tune_by_case[plan_entry.case_id],
            ),
            window=plan_entry.window,
            route_path=plan_entry.route_path,
            policy_action=tune_by_case[plan_entry.case_id].action,
            learning_pattern=learning_by_case[plan_entry.case_id].pattern_type,
            confidence_score=learning_by_case[plan_entry.case_id].confidence_score,
            evidence_refs=learning_by_case[plan_entry.case_id].evidence_refs,
            commitment_refs=learning_by_case[plan_entry.case_id].commitment_refs,
            summary=(
                f"{plan_entry.case_id} is stewarded through "
                f"{_directive_type_for_case(plan_entry.case_id, agenda_item=agenda_by_case.get(plan_entry.case_id), drill=drill_by_case.get(plan_entry.case_id), tune_entry=tune_by_case[plan_entry.case_id]).value} "
                f"in the {plan_entry.window.value} window."
            ),
        )
        for index, plan_entry in enumerate(resolved_planner.entries, start=1)
    )
    if not directives:
        raise ValueError("operations steward requires at least one directive")

    status = OperationsStewardStatus.STABLE
    severity = "info"
    if any(d.directive_type is StewardDirectiveType.STABILIZE for d in directives):
        status = OperationsStewardStatus.CRITICAL
        severity = "critical"
    elif any(d.directive_type in {StewardDirectiveType.GOVERN, StewardDirectiveType.ADAPT} for d in directives):
        status = OperationsStewardStatus.ACTIVE
        severity = "warning"

    steward_signal = TelemetrySignal(
        signal_name="operations-steward",
        boundary=resolved_planner.planner_signal.boundary,
        correlation_id=steward_id,
        severity=severity,
        status=status.value,
        metrics={
            "directive_count": float(len(directives)),
            "stabilize_count": float(len([d for d in directives if d.directive_type is StewardDirectiveType.STABILIZE])),
            "govern_count": float(len([d for d in directives if d.directive_type is StewardDirectiveType.GOVERN])),
            "adapt_count": float(len([d for d in directives if d.directive_type is StewardDirectiveType.ADAPT])),
            "monitor_count": float(len([d for d in directives if d.directive_type is StewardDirectiveType.MONITOR])),
            "avg_confidence": round(sum(d.confidence_score for d in directives) / len(directives), 3),
        },
        labels={"steward_id": steward_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_register.final_snapshot.runtime_stage,
        signals=(
            steward_signal,
            resolved_planner.planner_signal,
            resolved_agenda.agenda_signal,
            resolved_drills.drill_signal,
            resolved_tuner.tuner_signal,
            resolved_register.register_signal,
            *resolved_register.final_snapshot.signals,
        ),
        alerts=resolved_register.final_snapshot.alerts,
        audit_entries=resolved_register.final_snapshot.audit_entries,
        active_controls=resolved_register.final_snapshot.active_controls,
    )
    return OperationsSteward(
        steward_id=steward_id,
        capacity_planner=resolved_planner,
        governance_agenda=resolved_agenda,
        recovery_drills=resolved_drills,
        policy_tuner=resolved_tuner,
        learning_register=resolved_register,
        directives=directives,
        steward_signal=steward_signal,
        final_snapshot=final_snapshot,
    )
