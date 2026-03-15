"""Drift monitoring over baseline scorecards, replays, and guardrails."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .benchmark_harness import BenchmarkHarness
from .guardrail_portfolio import Guardrail, GuardrailPortfolio, build_guardrail_portfolio
from .module_boundaries import ModuleBoundaryName
from .release_campaigns import ReleaseCampaignStatus
from .runtime_scorecard import RuntimeScorecard, RuntimeScorecardEntry, build_runtime_scorecard
from .scenario_replay import ScenarioReplaySuite, build_scenario_replay
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class DriftSeverity(str, Enum):
    """Operational severity assigned to replay drift observations."""

    STABLE = "stable"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True)
class DriftObservation:
    """Per-case drift observation between baseline and replay execution."""

    case_id: str
    baseline_status: ReleaseCampaignStatus
    replay_status: ReleaseCampaignStatus
    baseline_overall_score: float
    replay_overall_score: float
    score_drift: float
    governance_drift: float
    recovery_drift: float
    guardrail_violations: tuple[str, ...]
    severity: DriftSeverity

    def __post_init__(self) -> None:
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))
        object.__setattr__(self, "baseline_overall_score", _clamp01(self.baseline_overall_score))
        object.__setattr__(self, "replay_overall_score", _clamp01(self.replay_overall_score))
        object.__setattr__(self, "score_drift", _clamp01(self.score_drift))
        object.__setattr__(self, "governance_drift", _clamp01(self.governance_drift))
        object.__setattr__(self, "recovery_drift", _clamp01(self.recovery_drift))

    @property
    def stable(self) -> bool:
        return self.severity is DriftSeverity.STABLE

    def to_dict(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "baseline_status": self.baseline_status.value,
            "replay_status": self.replay_status.value,
            "baseline_overall_score": self.baseline_overall_score,
            "replay_overall_score": self.replay_overall_score,
            "score_drift": self.score_drift,
            "governance_drift": self.governance_drift,
            "recovery_drift": self.recovery_drift,
            "guardrail_violations": list(self.guardrail_violations),
            "severity": self.severity.value,
            "stable": self.stable,
        }


@dataclass(frozen=True)
class DriftMonitor:
    """Aggregated drift monitor over baseline, replay, and guardrail state."""

    monitor_id: str
    baseline_scorecard: RuntimeScorecard
    replay_suite: ScenarioReplaySuite
    replay_scorecard: RuntimeScorecard
    guardrail_portfolio: GuardrailPortfolio
    observations: tuple[DriftObservation, ...]
    drift_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "monitor_id", _non_empty(self.monitor_id, field_name="monitor_id"))

    @property
    def violating_case_ids(self) -> tuple[str, ...]:
        return tuple(observation.case_id for observation in self.observations if observation.guardrail_violations)

    @property
    def governance_drift_case_ids(self) -> tuple[str, ...]:
        return tuple(
            observation.case_id
            for observation in self.observations
            if observation.governance_drift >= 0.08
            or any("governance_score" in violation for violation in observation.guardrail_violations)
        )

    @property
    def recovery_drift_case_ids(self) -> tuple[str, ...]:
        return tuple(
            observation.case_id
            for observation in self.observations
            if observation.recovery_drift >= 0.08
            or any(
                "recovery_score" in violation or "overall_score" in violation
                for violation in observation.guardrail_violations
            )
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "monitor_id": self.monitor_id,
            "baseline_scorecard": self.baseline_scorecard.to_dict(),
            "replay_suite": self.replay_suite.to_dict(),
            "replay_scorecard": self.replay_scorecard.to_dict(),
            "guardrail_portfolio": self.guardrail_portfolio.to_dict(),
            "observations": [observation.to_dict() for observation in self.observations],
            "drift_signal": self.drift_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "violating_case_ids": list(self.violating_case_ids),
            "governance_drift_case_ids": list(self.governance_drift_case_ids),
            "recovery_drift_case_ids": list(self.recovery_drift_case_ids),
        }


def _replay_harness(monitor_id: str, replay_suite: ScenarioReplaySuite) -> BenchmarkHarness:
    return BenchmarkHarness(
        harness_id=f"{monitor_id}-replay-harness",
        cases=tuple(result.result.case for result in replay_suite.results),
        results=tuple(result.result for result in replay_suite.results),
        harness_signal=replay_suite.replay_signal,
        final_snapshot=replay_suite.final_snapshot,
    )


def _metric_for_guardrail(entry: RuntimeScorecardEntry, guardrail: Guardrail) -> tuple[str, float]:
    if guardrail.threshold_key == "governance-clearance":
        return ("governance_score", entry.governance_score)
    if guardrail.threshold_key == "recovery-resume-threshold":
        return ("recovery_score", entry.recovery_score)
    if guardrail.threshold_key == "release-readiness-floor":
        return ("overall_score", entry.overall_score)
    return ("stability_score", entry.stability_score)


def _violations_for_entry(entry: RuntimeScorecardEntry, guardrails: tuple[Guardrail, ...]) -> tuple[str, ...]:
    violations: list[str] = []
    for guardrail in guardrails:
        metric_name, metric_value = _metric_for_guardrail(entry, guardrail)
        if entry.release_status is ReleaseCampaignStatus.BLOCKED and guardrail.threshold_key == "release-readiness-floor":
            violations.append(f"{guardrail.guardrail_id}:{metric_name}")
            continue
        if metric_value < guardrail.threshold_value:
            violations.append(f"{guardrail.guardrail_id}:{metric_name}")
    return tuple(violations)


def _severity_for_observation(
    *,
    score_drift: float,
    governance_drift: float,
    recovery_drift: float,
    violations: tuple[str, ...],
) -> DriftSeverity:
    if violations:
        return DriftSeverity.CRITICAL
    if score_drift >= 0.08 or governance_drift >= 0.08 or recovery_drift >= 0.08:
        return DriftSeverity.WARNING
    return DriftSeverity.STABLE


def _observation_for_entry(
    baseline_entry: RuntimeScorecardEntry,
    replay_entry: RuntimeScorecardEntry,
    guardrails: tuple[Guardrail, ...],
) -> DriftObservation:
    score_drift = abs(baseline_entry.overall_score - replay_entry.overall_score)
    governance_drift = abs(baseline_entry.governance_score - replay_entry.governance_score)
    recovery_drift = abs(baseline_entry.recovery_score - replay_entry.recovery_score)
    violations = _violations_for_entry(replay_entry, guardrails)
    severity = _severity_for_observation(
        score_drift=score_drift,
        governance_drift=governance_drift,
        recovery_drift=recovery_drift,
        violations=violations,
    )
    return DriftObservation(
        case_id=baseline_entry.case_id,
        baseline_status=baseline_entry.release_status,
        replay_status=replay_entry.release_status,
        baseline_overall_score=baseline_entry.overall_score,
        replay_overall_score=replay_entry.overall_score,
        score_drift=score_drift,
        governance_drift=governance_drift,
        recovery_drift=recovery_drift,
        guardrail_violations=violations,
        severity=severity,
    )


def build_drift_monitor(
    baseline_scorecard: RuntimeScorecard | None = None,
    replay_suite: ScenarioReplaySuite | None = None,
    guardrail_portfolio: GuardrailPortfolio | None = None,
    *,
    monitor_id: str = "drift-monitor",
) -> DriftMonitor:
    """Build a drift monitor from baseline scores, replays, and guardrails."""

    resolved_replay_suite = build_scenario_replay(replay_id=f"{monitor_id}-replay") if replay_suite is None else replay_suite
    resolved_baseline = (
        build_runtime_scorecard(resolved_replay_suite.source_harness, scorecard_id=f"{monitor_id}-baseline")
        if baseline_scorecard is None
        else baseline_scorecard
    )
    resolved_portfolio = (
        resolved_replay_suite.guardrail_portfolio
        if guardrail_portfolio is None
        else guardrail_portfolio
    )
    if resolved_portfolio is None:
        resolved_portfolio = build_guardrail_portfolio(portfolio_id=f"{monitor_id}-portfolio")
    replay_scorecard = build_runtime_scorecard(_replay_harness(monitor_id, resolved_replay_suite), scorecard_id=f"{monitor_id}-replay")

    baseline_by_case = {entry.case_id: entry for entry in resolved_baseline.entries}
    replay_by_case = {entry.case_id: entry for entry in replay_scorecard.entries}
    guardrails_by_case: dict[str, list[Guardrail]] = {}
    for guardrail in resolved_portfolio.guardrails:
        guardrails_by_case.setdefault(guardrail.case_id, []).append(guardrail)

    observations = tuple(
        _observation_for_entry(
            baseline_by_case[case_id],
            replay_by_case[case_id],
            tuple(guardrails_by_case.get(case_id, ())),
        )
        for case_id in replay_by_case
    )

    severity = "info"
    status = "stable"
    if any(observation.severity is DriftSeverity.CRITICAL for observation in observations):
        severity = "critical"
        status = "guardrail-violations"
    elif any(observation.severity is DriftSeverity.WARNING for observation in observations):
        severity = "warning"
        status = "drift-detected"

    drift_signal = TelemetrySignal(
        signal_name="drift-monitor",
        boundary=ModuleBoundaryName.TELEMETRY,
        correlation_id=monitor_id,
        severity=severity,
        status=status,
        metrics={
            "observation_count": float(len(observations)),
            "violating_count": float(len([o for o in observations if o.guardrail_violations])),
            "score_drift_count": float(len([o for o in observations if o.score_drift >= 0.08])),
            "governance_drift_count": float(
                len(
                    [
                        o
                        for o in observations
                        if o.governance_drift >= 0.08
                        or any("governance_score" in violation for violation in o.guardrail_violations)
                    ]
                )
            ),
            "recovery_drift_count": float(
                len(
                    [
                        o
                        for o in observations
                        if o.recovery_drift >= 0.08
                        or any(
                            "recovery_score" in violation or "overall_score" in violation
                            for violation in o.guardrail_violations
                        )
                    ]
                )
            ),
        },
        labels={"monitor_id": monitor_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_replay_suite.final_snapshot.runtime_stage,
        signals=(
            drift_signal,
            resolved_baseline.scorecard_signal,
            replay_scorecard.scorecard_signal,
            resolved_replay_suite.replay_signal,
            resolved_portfolio.portfolio_signal,
            *(signal for result in resolved_replay_suite.results for signal in result.final_snapshot.signals),
        ),
        alerts=resolved_replay_suite.final_snapshot.alerts,
        audit_entries=resolved_replay_suite.final_snapshot.audit_entries,
        active_controls=tuple(
            dict.fromkeys(
                (
                    *resolved_replay_suite.final_snapshot.active_controls,
                    *resolved_portfolio.final_snapshot.active_controls,
                )
            )
        ),
    )
    return DriftMonitor(
        monitor_id=monitor_id,
        baseline_scorecard=resolved_baseline,
        replay_suite=resolved_replay_suite,
        replay_scorecard=replay_scorecard,
        guardrail_portfolio=resolved_portfolio,
        observations=observations,
        drift_signal=drift_signal,
        final_snapshot=final_snapshot,
    )
