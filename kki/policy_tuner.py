"""Controlled guardrail and policy tuning over convergence and escalation data."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .convergence_simulator import ConvergenceSimulator, ConvergenceStatus, build_convergence_simulator
from .escalation_router import EscalationRoutePath, EscalationRouter, build_escalation_router
from .guardrail_portfolio import Guardrail, GuardrailPolicyMode, GuardrailPortfolio, build_guardrail_portfolio
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class PolicyTuneAction(str, Enum):
    """Canonical tuning actions derived from operational feedback."""

    TIGHTEN = "tighten"
    CALIBRATE = "calibrate"
    RELAX = "relax"


@dataclass(frozen=True)
class PolicyTuneEntry:
    """One controlled policy adjustment for a routed guardrail."""

    tune_id: str
    case_id: str
    route_path: EscalationRoutePath
    source_policy_mode: GuardrailPolicyMode
    tuned_policy_mode: GuardrailPolicyMode
    action: PolicyTuneAction
    threshold_key: str
    current_threshold: float
    tuned_threshold: float
    convergence_status: ConvergenceStatus
    residual_drift: float
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "tune_id", _non_empty(self.tune_id, field_name="tune_id"))
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))
        object.__setattr__(self, "threshold_key", _non_empty(self.threshold_key, field_name="threshold_key"))
        object.__setattr__(self, "current_threshold", _clamp01(self.current_threshold))
        object.__setattr__(self, "tuned_threshold", _clamp01(self.tuned_threshold))
        object.__setattr__(self, "residual_drift", _clamp01(self.residual_drift))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))

    def to_dict(self) -> dict[str, object]:
        return {
            "tune_id": self.tune_id,
            "case_id": self.case_id,
            "route_path": self.route_path.value,
            "source_policy_mode": self.source_policy_mode.value,
            "tuned_policy_mode": self.tuned_policy_mode.value,
            "action": self.action.value,
            "threshold_key": self.threshold_key,
            "current_threshold": self.current_threshold,
            "tuned_threshold": self.tuned_threshold,
            "convergence_status": self.convergence_status.value,
            "residual_drift": self.residual_drift,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class PolicyTuner:
    """Controlled set of guardrail adjustments derived from operational feedback."""

    tuner_id: str
    guardrail_portfolio: GuardrailPortfolio
    escalation_router: EscalationRouter
    convergence_simulator: ConvergenceSimulator
    entries: tuple[PolicyTuneEntry, ...]
    tuner_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "tuner_id", _non_empty(self.tuner_id, field_name="tuner_id"))

    @property
    def tightened_case_ids(self) -> tuple[str, ...]:
        return tuple(entry.case_id for entry in self.entries if entry.action is PolicyTuneAction.TIGHTEN)

    @property
    def calibrated_case_ids(self) -> tuple[str, ...]:
        return tuple(entry.case_id for entry in self.entries if entry.action is PolicyTuneAction.CALIBRATE)

    @property
    def relaxed_case_ids(self) -> tuple[str, ...]:
        return tuple(entry.case_id for entry in self.entries if entry.action is PolicyTuneAction.RELAX)

    def to_dict(self) -> dict[str, object]:
        return {
            "tuner_id": self.tuner_id,
            "guardrail_portfolio": self.guardrail_portfolio.to_dict(),
            "escalation_router": self.escalation_router.to_dict(),
            "convergence_simulator": self.convergence_simulator.to_dict(),
            "entries": [entry.to_dict() for entry in self.entries],
            "tuner_signal": self.tuner_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "tightened_case_ids": list(self.tightened_case_ids),
            "calibrated_case_ids": list(self.calibrated_case_ids),
            "relaxed_case_ids": list(self.relaxed_case_ids),
        }


def _route_by_case(router: EscalationRouter) -> dict[str, EscalationRoutePath]:
    return {route.case_id: route.path for route in router.routes}


def _projection_status_by_case(simulator: ConvergenceSimulator, cycle_index: int) -> dict[str, ConvergenceStatus | str]:
    projection = next(projection for projection in simulator.projections if projection.cycle_index == cycle_index)
    status_by_case: dict[str, ConvergenceStatus | str] = {}
    for case_id in projection.ready_case_ids:
        status_by_case[case_id] = "ready"
    for case_id in projection.attention_case_ids:
        status_by_case[case_id] = "attention"
    for case_id in projection.blocked_case_ids:
        status_by_case[case_id] = "blocked"
    return status_by_case


def _tuning_for_guardrail(
    tuner_id: str,
    guardrail: Guardrail,
    *,
    route_path: EscalationRoutePath,
    convergence_status: ConvergenceStatus,
    cycle_one_status: str,
    final_residual_drift: float,
) -> PolicyTuneEntry:
    tuned_policy_mode = guardrail.policy_mode
    action = PolicyTuneAction.CALIBRATE
    threshold_delta = 0.0

    if route_path is EscalationRoutePath.RECOVERY_CONTAINMENT or cycle_one_status == "blocked":
        action = PolicyTuneAction.TIGHTEN
        tuned_policy_mode = GuardrailPolicyMode.CONTAIN
        threshold_delta = 0.08
    elif route_path is EscalationRoutePath.RECOVERY_RESTART:
        action = PolicyTuneAction.TIGHTEN
        tuned_policy_mode = GuardrailPolicyMode.HOLD
        threshold_delta = 0.06
    elif route_path is EscalationRoutePath.GOVERNANCE_REVIEW:
        action = PolicyTuneAction.CALIBRATE
        tuned_policy_mode = GuardrailPolicyMode.HOLD
        threshold_delta = 0.05
    elif convergence_status is ConvergenceStatus.CONVERGED:
        action = PolicyTuneAction.RELAX
        tuned_policy_mode = GuardrailPolicyMode.MONITOR
        threshold_delta = -0.05

    tuned_threshold = _clamp01(guardrail.threshold_value + threshold_delta)
    return PolicyTuneEntry(
        tune_id=f"{tuner_id}-{guardrail.case_id}",
        case_id=guardrail.case_id,
        route_path=route_path,
        source_policy_mode=guardrail.policy_mode,
        tuned_policy_mode=tuned_policy_mode,
        action=action,
        threshold_key=guardrail.threshold_key,
        current_threshold=guardrail.threshold_value,
        tuned_threshold=tuned_threshold,
        convergence_status=convergence_status,
        residual_drift=final_residual_drift,
        summary=(
            f"{guardrail.case_id} tunes {guardrail.policy_mode.value} to {tuned_policy_mode.value} "
            f"after {route_path.value} and a {convergence_status.value} convergence outlook."
        ),
    )


def build_policy_tuner(
    guardrail_portfolio: GuardrailPortfolio | None = None,
    escalation_router: EscalationRouter | None = None,
    convergence_simulator: ConvergenceSimulator | None = None,
    *,
    tuner_id: str = "policy-tuner",
) -> PolicyTuner:
    """Build controlled guardrail adjustments from escalation and convergence state."""

    resolved_portfolio = build_guardrail_portfolio(portfolio_id=f"{tuner_id}-portfolio") if guardrail_portfolio is None else guardrail_portfolio
    resolved_router = build_escalation_router(router_id=f"{tuner_id}-router") if escalation_router is None else escalation_router
    resolved_simulator = (
        build_convergence_simulator(simulator_id=f"{tuner_id}-simulator") if convergence_simulator is None else convergence_simulator
    )

    route_by_case = _route_by_case(resolved_router)
    cycle_one_status_by_case = _projection_status_by_case(resolved_simulator, 1)
    final_projection = resolved_simulator.projections[-1]
    entries = tuple(
        _tuning_for_guardrail(
            tuner_id,
            guardrail,
            route_path=route_by_case[guardrail.case_id],
            convergence_status=final_projection.status,
            cycle_one_status=str(cycle_one_status_by_case[guardrail.case_id]),
            final_residual_drift=final_projection.residual_drift,
        )
        for guardrail in resolved_portfolio.guardrails
    )
    if not entries:
        raise ValueError("policy tuner requires at least one tune entry")

    severity = "info"
    status = "policy-relaxed"
    if any(entry.action is PolicyTuneAction.TIGHTEN for entry in entries):
        severity = "warning"
        status = "policy-tightening"
    elif any(entry.action is PolicyTuneAction.CALIBRATE for entry in entries):
        status = "policy-calibrated"

    tuner_signal = TelemetrySignal(
        signal_name="policy-tuner",
        boundary=resolved_router.router_signal.boundary,
        correlation_id=tuner_id,
        severity=severity,
        status=status,
        metrics={
            "entry_count": float(len(entries)),
            "tighten_count": float(len([entry for entry in entries if entry.action is PolicyTuneAction.TIGHTEN])),
            "calibrate_count": float(len([entry for entry in entries if entry.action is PolicyTuneAction.CALIBRATE])),
            "relax_count": float(len([entry for entry in entries if entry.action is PolicyTuneAction.RELAX])),
            "final_residual_drift": final_projection.residual_drift,
        },
        labels={"tuner_id": tuner_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_simulator.final_snapshot.runtime_stage,
        signals=(
            tuner_signal,
            resolved_portfolio.portfolio_signal,
            resolved_router.router_signal,
            resolved_simulator.simulator_signal,
            *resolved_simulator.final_snapshot.signals,
        ),
        alerts=resolved_simulator.final_snapshot.alerts,
        audit_entries=resolved_simulator.final_snapshot.audit_entries,
        active_controls=resolved_simulator.final_snapshot.active_controls,
    )
    return PolicyTuner(
        tuner_id=tuner_id,
        guardrail_portfolio=resolved_portfolio,
        escalation_router=resolved_router,
        convergence_simulator=resolved_simulator,
        entries=entries,
        tuner_signal=tuner_signal,
        final_snapshot=final_snapshot,
    )
