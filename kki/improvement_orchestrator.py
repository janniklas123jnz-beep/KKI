"""Improvement-wave orchestration over actions, risks, guardrails, and drift."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .drift_monitor import DriftMonitor, DriftSeverity, build_drift_monitor
from .guardrail_portfolio import Guardrail, GuardrailPolicyMode, GuardrailPortfolio, build_guardrail_portfolio
from .module_boundaries import ModuleBoundaryName
from .review_action_plan import ReviewActionItem, ReviewActionPlan, ReviewActionPriority, build_review_action_plan
from .risk_register import RiskImpact, RiskMitigationStatus, RiskRecord, RiskRegister, build_risk_register
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


class ImprovementPriority(str, Enum):
    """Canonical priority bands for improvement waves."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ImprovementExecutionMode(str, Enum):
    """Execution modes that keep improvement waves safe under active controls."""

    CONTAINED = "contained"
    GOVERNED = "governed"
    RECOVERY = "recovery"
    OBSERVE = "observe"


@dataclass(frozen=True)
class ImprovementWave:
    """Prioritized and budgeted improvement wave for one case."""

    wave_id: str
    case_id: str
    sequence: int
    priority: ImprovementPriority
    execution_mode: ImprovementExecutionMode
    owner: ModuleBoundaryName
    budget_share: float
    target_status: str
    action_refs: tuple[str, ...]
    risk_refs: tuple[str, ...]
    guardrail_refs: tuple[str, ...]
    blocked_release: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "wave_id", _non_empty(self.wave_id, field_name="wave_id"))
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))
        object.__setattr__(self, "target_status", _non_empty(self.target_status, field_name="target_status"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if not 0.0 < float(self.budget_share) <= 1.0:
            raise ValueError("budget_share must be between 0.0 and 1.0")
        object.__setattr__(self, "budget_share", float(self.budget_share))

    def to_dict(self) -> dict[str, object]:
        return {
            "wave_id": self.wave_id,
            "case_id": self.case_id,
            "sequence": self.sequence,
            "priority": self.priority.value,
            "execution_mode": self.execution_mode.value,
            "owner": self.owner.value,
            "budget_share": self.budget_share,
            "target_status": self.target_status,
            "action_refs": list(self.action_refs),
            "risk_refs": list(self.risk_refs),
            "guardrail_refs": list(self.guardrail_refs),
            "blocked_release": self.blocked_release,
        }


@dataclass(frozen=True)
class ImprovementOrchestrator:
    """Ordered improvement waves derived from operational control layers."""

    orchestrator_id: str
    action_plan: ReviewActionPlan
    risk_register: RiskRegister
    guardrail_portfolio: GuardrailPortfolio
    drift_monitor: DriftMonitor
    waves: tuple[ImprovementWave, ...]
    orchestration_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "orchestrator_id", _non_empty(self.orchestrator_id, field_name="orchestrator_id"))

    @property
    def blocked_case_ids(self) -> tuple[str, ...]:
        return tuple(wave.case_id for wave in self.waves if wave.blocked_release)

    @property
    def owner_boundaries(self) -> tuple[ModuleBoundaryName, ...]:
        ordered: list[ModuleBoundaryName] = []
        for wave in self.waves:
            if wave.owner not in ordered:
                ordered.append(wave.owner)
        return tuple(ordered)

    def to_dict(self) -> dict[str, object]:
        return {
            "orchestrator_id": self.orchestrator_id,
            "action_plan": self.action_plan.to_dict(),
            "risk_register": self.risk_register.to_dict(),
            "guardrail_portfolio": self.guardrail_portfolio.to_dict(),
            "drift_monitor": self.drift_monitor.to_dict(),
            "waves": [wave.to_dict() for wave in self.waves],
            "orchestration_signal": self.orchestration_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "blocked_case_ids": list(self.blocked_case_ids),
            "owner_boundaries": [owner.value for owner in self.owner_boundaries],
        }


def _priority_for_case(
    actions: tuple[ReviewActionItem, ...],
    risks: tuple[RiskRecord, ...],
    guardrails: tuple[Guardrail, ...],
    drift_severity: DriftSeverity,
) -> ImprovementPriority:
    if any(action.blocked_release for action in actions) or any(
        risk.mitigation_status is RiskMitigationStatus.BLOCKING for risk in risks
    ) or any(guardrail.policy_mode is GuardrailPolicyMode.CONTAIN for guardrail in guardrails):
        return ImprovementPriority.CRITICAL
    if any(
        action.priority is ReviewActionPriority.HIGH for action in actions
    ) or any(
        risk.mitigation_status in {RiskMitigationStatus.ACTIVE, RiskMitigationStatus.BLOCKING}
        or risk.impact in {RiskImpact.HIGH, RiskImpact.CRITICAL}
        for risk in risks
    ) or drift_severity in {DriftSeverity.CRITICAL, DriftSeverity.WARNING}:
        return ImprovementPriority.HIGH
    if any(action.priority is ReviewActionPriority.MEDIUM for action in actions):
        return ImprovementPriority.MEDIUM
    return ImprovementPriority.LOW


def _execution_mode_for_case(guardrails: tuple[Guardrail, ...], priority: ImprovementPriority, owner: ModuleBoundaryName) -> ImprovementExecutionMode:
    if any(guardrail.policy_mode is GuardrailPolicyMode.CONTAIN for guardrail in guardrails) or priority is ImprovementPriority.CRITICAL:
        return ImprovementExecutionMode.CONTAINED
    if owner is ModuleBoundaryName.GOVERNANCE or any(guardrail.policy_mode is GuardrailPolicyMode.HOLD for guardrail in guardrails):
        return ImprovementExecutionMode.GOVERNED
    if owner is ModuleBoundaryName.RECOVERY or any(guardrail.policy_mode is GuardrailPolicyMode.THROTTLE for guardrail in guardrails):
        return ImprovementExecutionMode.RECOVERY
    return ImprovementExecutionMode.OBSERVE


def _owner_for_case(actions: tuple[ReviewActionItem, ...], risks: tuple[RiskRecord, ...]) -> ModuleBoundaryName:
    if actions:
        ordered = sorted(actions, key=lambda action: (action.priority.value, action.owner.value))
        return ordered[0].owner
    if risks:
        return risks[0].owner
    return ModuleBoundaryName.TELEMETRY


def _target_status_for_case(actions: tuple[ReviewActionItem, ...], priority: ImprovementPriority) -> str:
    if actions:
        ordered = sorted(
            actions,
            key=lambda action: (
                action.priority is not ReviewActionPriority.CRITICAL,
                action.priority is not ReviewActionPriority.HIGH,
                action.priority is not ReviewActionPriority.MEDIUM,
            ),
        )
        return ordered[0].target_status
    if priority is ImprovementPriority.CRITICAL:
        return "containment-cleared"
    if priority is ImprovementPriority.HIGH:
        return "promotion-restored"
    return "baseline-preserved"


def _budget_weights(waves: list[tuple[str, ImprovementPriority, tuple[Guardrail, ...], DriftSeverity]]) -> dict[str, float]:
    weights: dict[str, float] = {}
    total = 0.0
    for case_id, priority, guardrails, drift_severity in waves:
        weight = {
            ImprovementPriority.CRITICAL: 4.0,
            ImprovementPriority.HIGH: 3.0,
            ImprovementPriority.MEDIUM: 2.0,
            ImprovementPriority.LOW: 1.0,
        }[priority]
        weight += float(len(guardrails)) * 0.35
        if drift_severity is DriftSeverity.CRITICAL:
            weight += 0.5
        elif drift_severity is DriftSeverity.WARNING:
            weight += 0.25
        weights[case_id] = weight
        total += weight
    return {case_id: weight / total for case_id, weight in weights.items()}


def build_improvement_orchestrator(
    action_plan: ReviewActionPlan | None = None,
    risk_register: RiskRegister | None = None,
    guardrail_portfolio: GuardrailPortfolio | None = None,
    drift_monitor: DriftMonitor | None = None,
    *,
    orchestrator_id: str = "improvement-orchestrator",
) -> ImprovementOrchestrator:
    """Build ordered improvement waves from the current operational control loop."""

    resolved_action_plan = build_review_action_plan(plan_id=f"{orchestrator_id}-plan") if action_plan is None else action_plan
    resolved_risk_register = (
        build_risk_register(resolved_action_plan, register_id=f"{orchestrator_id}-register")
        if risk_register is None
        else risk_register
    )
    resolved_guardrail_portfolio = (
        build_guardrail_portfolio(resolved_risk_register, portfolio_id=f"{orchestrator_id}-portfolio")
        if guardrail_portfolio is None
        else guardrail_portfolio
    )
    resolved_drift_monitor = (
        build_drift_monitor(guardrail_portfolio=resolved_guardrail_portfolio, monitor_id=f"{orchestrator_id}-drift")
        if drift_monitor is None
        else drift_monitor
    )

    case_ids = tuple(
        dict.fromkeys(
            [
                *(action.case_id for action in resolved_action_plan.actions),
                *(risk.case_id for risk in resolved_risk_register.risks),
                *(observation.case_id for observation in resolved_drift_monitor.observations),
            ]
        )
    )
    action_map = {case_id: tuple(action for action in resolved_action_plan.actions if action.case_id == case_id) for case_id in case_ids}
    risk_map = {case_id: tuple(risk for risk in resolved_risk_register.risks if risk.case_id == case_id) for case_id in case_ids}
    guardrail_map = {
        case_id: tuple(guardrail for guardrail in resolved_guardrail_portfolio.guardrails if guardrail.case_id == case_id)
        for case_id in case_ids
    }
    observation_map = {observation.case_id: observation for observation in resolved_drift_monitor.observations}

    case_descriptors: list[tuple[str, ImprovementPriority, tuple[Guardrail, ...], DriftSeverity]] = []
    for case_id in case_ids:
        drift_severity = observation_map.get(case_id, None)
        resolved_severity = DriftSeverity.STABLE if drift_severity is None else drift_severity.severity
        priority = _priority_for_case(action_map[case_id], risk_map[case_id], guardrail_map[case_id], resolved_severity)
        case_descriptors.append((case_id, priority, guardrail_map[case_id], resolved_severity))
    budgets = _budget_weights(case_descriptors)

    ordered_cases = sorted(
        case_descriptors,
        key=lambda item: (
            {
                ImprovementPriority.CRITICAL: 0,
                ImprovementPriority.HIGH: 1,
                ImprovementPriority.MEDIUM: 2,
                ImprovementPriority.LOW: 3,
            }[item[1]],
            item[0],
        ),
    )

    waves: list[ImprovementWave] = []
    for index, (case_id, priority, guardrails, _drift) in enumerate(ordered_cases, start=1):
        actions = action_map[case_id]
        risks = risk_map[case_id]
        owner = _owner_for_case(actions, risks)
        waves.append(
            ImprovementWave(
                wave_id=f"{orchestrator_id}-{case_id}",
                case_id=case_id,
                sequence=index,
                priority=priority,
                execution_mode=_execution_mode_for_case(guardrails, priority, owner),
                owner=owner,
                budget_share=budgets[case_id],
                target_status=_target_status_for_case(actions, priority),
                action_refs=tuple(action.action_id for action in actions),
                risk_refs=tuple(risk.risk_id for risk in risks),
                guardrail_refs=tuple(guardrail.guardrail_id for guardrail in guardrails),
                blocked_release=any(action.blocked_release for action in actions),
            )
        )
    if not waves:
        raise ValueError("improvement orchestrator requires at least one wave")

    severity = "info"
    status = "planned-waves"
    if any(wave.priority is ImprovementPriority.CRITICAL for wave in waves):
        severity = "critical"
        status = "critical-waves"
    elif any(wave.priority is ImprovementPriority.HIGH for wave in waves):
        severity = "warning"
        status = "priority-waves"

    orchestration_signal = TelemetrySignal(
        signal_name="improvement-orchestrator",
        boundary=ModuleBoundaryName.GOVERNANCE,
        correlation_id=orchestrator_id,
        severity=severity,
        status=status,
        metrics={
            "wave_count": float(len(waves)),
            "critical_count": float(len([wave for wave in waves if wave.priority is ImprovementPriority.CRITICAL])),
            "high_count": float(len([wave for wave in waves if wave.priority is ImprovementPriority.HIGH])),
            "blocked_case_count": float(len([wave for wave in waves if wave.blocked_release])),
            "governed_count": float(len([wave for wave in waves if wave.execution_mode is ImprovementExecutionMode.GOVERNED])),
        },
        labels={"orchestrator_id": orchestrator_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_drift_monitor.final_snapshot.runtime_stage,
        signals=(
            orchestration_signal,
            resolved_action_plan.plan_signal,
            resolved_risk_register.register_signal,
            resolved_guardrail_portfolio.portfolio_signal,
            resolved_drift_monitor.drift_signal,
            *resolved_drift_monitor.final_snapshot.signals,
        ),
        alerts=resolved_drift_monitor.final_snapshot.alerts,
        audit_entries=resolved_drift_monitor.final_snapshot.audit_entries,
        active_controls=tuple(
            dict.fromkeys(
                (
                    *resolved_action_plan.final_snapshot.active_controls,
                    *resolved_risk_register.final_snapshot.active_controls,
                    *resolved_guardrail_portfolio.final_snapshot.active_controls,
                    *resolved_drift_monitor.final_snapshot.active_controls,
                )
            )
        ),
    )
    return ImprovementOrchestrator(
        orchestrator_id=orchestrator_id,
        action_plan=resolved_action_plan,
        risk_register=resolved_risk_register,
        guardrail_portfolio=resolved_guardrail_portfolio,
        drift_monitor=resolved_drift_monitor,
        waves=tuple(waves),
        orchestration_signal=orchestration_signal,
        final_snapshot=final_snapshot,
    )
