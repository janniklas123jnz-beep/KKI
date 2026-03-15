"""Guardrail portfolio derived from the operational risk register."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .module_boundaries import ModuleBoundaryName
from .risk_register import RiskImpact, RiskLikelihood, RiskMitigationStatus, RiskRecord, RiskRegister, build_risk_register
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


class GuardrailPolicyMode(str, Enum):
    """Canonical guardrail policy modes."""

    MONITOR = "monitor"
    THROTTLE = "throttle"
    HOLD = "hold"
    CONTAIN = "contain"


class GuardrailDomain(str, Enum):
    """Canonical domains covered by a reusable guardrail."""

    GOVERNANCE = "governance"
    RECOVERY = "recovery"
    TELEMETRY = "telemetry"
    ROLLOUT = "rollout"


@dataclass(frozen=True)
class Guardrail:
    """Reusable operational guardrail derived from one registered risk."""

    guardrail_id: str
    case_id: str
    domain: GuardrailDomain
    owner: ModuleBoundaryName
    policy_mode: GuardrailPolicyMode
    threshold_key: str
    threshold_value: float
    summary: str
    source_risk: RiskRecord

    def __post_init__(self) -> None:
        object.__setattr__(self, "guardrail_id", _non_empty(self.guardrail_id, field_name="guardrail_id"))
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))
        object.__setattr__(self, "threshold_key", _non_empty(self.threshold_key, field_name="threshold_key"))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if not 0.0 <= float(self.threshold_value) <= 1.0:
            raise ValueError("threshold_value must be between 0.0 and 1.0")
        object.__setattr__(self, "threshold_value", float(self.threshold_value))

    def to_dict(self) -> dict[str, object]:
        return {
            "guardrail_id": self.guardrail_id,
            "case_id": self.case_id,
            "domain": self.domain.value,
            "owner": self.owner.value,
            "policy_mode": self.policy_mode.value,
            "threshold_key": self.threshold_key,
            "threshold_value": self.threshold_value,
            "summary": self.summary,
            "source_risk": self.source_risk.to_dict(),
        }


@dataclass(frozen=True)
class GuardrailPortfolio:
    """Aggregated reusable guardrail set over the operational risk register."""

    portfolio_id: str
    risk_register: RiskRegister
    guardrails: tuple[Guardrail, ...]
    portfolio_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "portfolio_id", _non_empty(self.portfolio_id, field_name="portfolio_id"))

    @property
    def blocking_case_ids(self) -> tuple[str, ...]:
        ordered: list[str] = []
        for guardrail in self.guardrails:
            if guardrail.policy_mode is not GuardrailPolicyMode.CONTAIN:
                continue
            if guardrail.case_id not in ordered:
                ordered.append(guardrail.case_id)
        return tuple(ordered)

    @property
    def owner_boundaries(self) -> tuple[ModuleBoundaryName, ...]:
        ordered: list[ModuleBoundaryName] = []
        for guardrail in self.guardrails:
            if guardrail.owner not in ordered:
                ordered.append(guardrail.owner)
        return tuple(ordered)

    @property
    def domains(self) -> tuple[GuardrailDomain, ...]:
        ordered: list[GuardrailDomain] = []
        for guardrail in self.guardrails:
            if guardrail.domain not in ordered:
                ordered.append(guardrail.domain)
        return tuple(ordered)

    def to_dict(self) -> dict[str, object]:
        return {
            "portfolio_id": self.portfolio_id,
            "risk_register": self.risk_register.to_dict(),
            "guardrails": [guardrail.to_dict() for guardrail in self.guardrails],
            "portfolio_signal": self.portfolio_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "blocking_case_ids": list(self.blocking_case_ids),
            "owner_boundaries": [owner.value for owner in self.owner_boundaries],
            "domains": [domain.value for domain in self.domains],
        }


def _threshold_for_risk(risk: RiskRecord) -> tuple[str, float]:
    if risk.mitigation_status is RiskMitigationStatus.BLOCKING:
        return ("release-readiness-floor", 0.2)
    if risk.owner is ModuleBoundaryName.GOVERNANCE:
        return ("governance-clearance", 0.65)
    if risk.owner is ModuleBoundaryName.RECOVERY:
        return ("recovery-resume-threshold", 0.72)
    return ("telemetry-drift-threshold", 0.85)


def _guardrail_for_risk(portfolio_id: str, risk: RiskRecord) -> Guardrail:
    domain = GuardrailDomain.TELEMETRY
    policy_mode = GuardrailPolicyMode.MONITOR
    if risk.owner is ModuleBoundaryName.GOVERNANCE:
        domain = GuardrailDomain.GOVERNANCE
        policy_mode = GuardrailPolicyMode.HOLD
    elif risk.owner is ModuleBoundaryName.RECOVERY:
        domain = GuardrailDomain.RECOVERY
        policy_mode = GuardrailPolicyMode.THROTTLE
    elif risk.owner is ModuleBoundaryName.ROLLOUT:
        domain = GuardrailDomain.ROLLOUT
        policy_mode = GuardrailPolicyMode.HOLD

    if risk.mitigation_status is RiskMitigationStatus.BLOCKING:
        domain = GuardrailDomain.RECOVERY
        policy_mode = GuardrailPolicyMode.CONTAIN

    threshold_key, threshold_value = _threshold_for_risk(risk)
    return Guardrail(
        guardrail_id=f"{portfolio_id}-{risk.case_id}-{domain.value}",
        case_id=risk.case_id,
        domain=domain,
        owner=risk.owner,
        policy_mode=policy_mode,
        threshold_key=threshold_key,
        threshold_value=threshold_value,
        summary=risk.summary,
        source_risk=risk,
    )


def build_guardrail_portfolio(
    risk_register: RiskRegister | None = None,
    *,
    portfolio_id: str = "guardrail-portfolio",
) -> GuardrailPortfolio:
    """Build reusable operational guardrails from the risk register."""

    resolved_register = build_risk_register(register_id=f"{portfolio_id}-register") if risk_register is None else risk_register
    guardrails = tuple(_guardrail_for_risk(portfolio_id, risk) for risk in resolved_register.risks)
    if not guardrails:
        raise ValueError("guardrail portfolio requires at least one guardrail")

    severity = "info"
    status = "monitoring"
    if any(guardrail.policy_mode is GuardrailPolicyMode.CONTAIN for guardrail in guardrails):
        severity = "critical"
        status = "containment-guardrails"
    elif any(guardrail.policy_mode in {GuardrailPolicyMode.HOLD, GuardrailPolicyMode.THROTTLE} for guardrail in guardrails):
        severity = "warning"
        status = "active-guardrails"

    portfolio_signal = TelemetrySignal(
        signal_name="guardrail-portfolio",
        boundary=ModuleBoundaryName.GOVERNANCE,
        correlation_id=portfolio_id,
        severity=severity,
        status=status,
        metrics={
            "guardrail_count": float(len(guardrails)),
            "contain_count": float(len([g for g in guardrails if g.policy_mode is GuardrailPolicyMode.CONTAIN])),
            "hold_count": float(len([g for g in guardrails if g.policy_mode is GuardrailPolicyMode.HOLD])),
            "throttle_count": float(len([g for g in guardrails if g.policy_mode is GuardrailPolicyMode.THROTTLE])),
            "monitor_count": float(len([g for g in guardrails if g.policy_mode is GuardrailPolicyMode.MONITOR])),
        },
        labels={"portfolio_id": portfolio_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_register.final_snapshot.runtime_stage,
        signals=(portfolio_signal, resolved_register.register_signal, *resolved_register.final_snapshot.signals),
        alerts=resolved_register.final_snapshot.alerts,
        audit_entries=resolved_register.final_snapshot.audit_entries,
        active_controls=resolved_register.final_snapshot.active_controls,
    )
    return GuardrailPortfolio(
        portfolio_id=portfolio_id,
        risk_register=resolved_register,
        guardrails=guardrails,
        portfolio_signal=portfolio_signal,
        final_snapshot=final_snapshot,
    )
