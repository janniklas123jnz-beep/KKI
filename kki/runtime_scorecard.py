"""Runtime scorecards over benchmark harness results."""

from __future__ import annotations

from dataclasses import dataclass

from .benchmark_harness import BenchmarkCaseResult, BenchmarkHarness, run_benchmark_harness
from .release_campaigns import ReleaseCampaignStatus
from .module_boundaries import ModuleBoundaryName
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass(frozen=True)
class RuntimeScorecardEntry:
    """Aggregated runtime quality scores for a single benchmark case."""

    case_id: str
    release_status: ReleaseCampaignStatus
    success_score: float
    stability_score: float
    recovery_score: float
    governance_score: float
    overall_score: float
    promotion_ready: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))
        object.__setattr__(self, "success_score", _clamp01(self.success_score))
        object.__setattr__(self, "stability_score", _clamp01(self.stability_score))
        object.__setattr__(self, "recovery_score", _clamp01(self.recovery_score))
        object.__setattr__(self, "governance_score", _clamp01(self.governance_score))
        object.__setattr__(self, "overall_score", _clamp01(self.overall_score))

    def to_dict(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "release_status": self.release_status.value,
            "success_score": self.success_score,
            "stability_score": self.stability_score,
            "recovery_score": self.recovery_score,
            "governance_score": self.governance_score,
            "overall_score": self.overall_score,
            "promotion_ready": self.promotion_ready,
        }


@dataclass(frozen=True)
class RuntimeScorecard:
    """Aggregated scorecard over a benchmark harness."""

    scorecard_id: str
    harness: BenchmarkHarness
    entries: tuple[RuntimeScorecardEntry, ...]
    scorecard_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "scorecard_id", _non_empty(self.scorecard_id, field_name="scorecard_id"))

    @property
    def average_overall_score(self) -> float:
        return sum(entry.overall_score for entry in self.entries) / len(self.entries)

    @property
    def healthy_case_ids(self) -> tuple[str, ...]:
        return tuple(
            entry.case_id
            for entry in self.entries
            if entry.release_status is ReleaseCampaignStatus.READY and entry.overall_score >= 0.8
        )

    @property
    def attention_case_ids(self) -> tuple[str, ...]:
        return tuple(
            entry.case_id
            for entry in self.entries
            if entry.release_status is not ReleaseCampaignStatus.READY or entry.overall_score < 0.8
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "scorecard_id": self.scorecard_id,
            "harness": self.harness.to_dict(),
            "entries": [entry.to_dict() for entry in self.entries],
            "scorecard_signal": self.scorecard_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "average_overall_score": self.average_overall_score,
            "healthy_case_ids": list(self.healthy_case_ids),
            "attention_case_ids": list(self.attention_case_ids),
        }


def _score_success(result: BenchmarkCaseResult) -> float:
    if result.status is ReleaseCampaignStatus.BLOCKED:
        return 0.22
    if result.status is ReleaseCampaignStatus.RECOVERY_ONLY:
        return 0.64 if result.wave.success else 0.56
    if result.status is ReleaseCampaignStatus.GUARDED:
        return 0.74 if result.wave.success else 0.62
    return 0.96 if result.wave.success and result.promotion_ready else 0.82


def _score_stability(result: BenchmarkCaseResult) -> float:
    alert_penalty = min(sum(entry.alert_count for entry in result.ledger.entries) * 0.04, 0.3)
    incident_penalty = min(len(result.incident_report.incidents) * 0.14, 0.56)
    severity_penalty = 0.0
    if result.benchmark_signal.severity == "critical":
        severity_penalty = 0.28
    elif result.benchmark_signal.severity == "warning":
        severity_penalty = 0.12
    return _clamp01(1.0 - alert_penalty - incident_penalty - severity_penalty)


def _score_recovery(result: BenchmarkCaseResult) -> float:
    if result.status is ReleaseCampaignStatus.BLOCKED:
        return 0.18
    if result.status is ReleaseCampaignStatus.RECOVERY_ONLY:
        return 0.72
    if result.status is ReleaseCampaignStatus.GUARDED:
        return 0.78
    return 0.9


def _score_governance(result: BenchmarkCaseResult) -> float:
    if result.status is ReleaseCampaignStatus.BLOCKED:
        return 0.2
    if result.status is ReleaseCampaignStatus.GUARDED:
        return 0.56
    if result.status is ReleaseCampaignStatus.RECOVERY_ONLY:
        return 0.68
    return 0.94


def _entry_for_result(result: BenchmarkCaseResult) -> RuntimeScorecardEntry:
    success_score = _score_success(result)
    stability_score = _score_stability(result)
    recovery_score = _score_recovery(result)
    governance_score = _score_governance(result)
    overall_score = (success_score + stability_score + recovery_score + governance_score) / 4.0
    return RuntimeScorecardEntry(
        case_id=result.case.case_id,
        release_status=result.status,
        success_score=success_score,
        stability_score=stability_score,
        recovery_score=recovery_score,
        governance_score=governance_score,
        overall_score=overall_score,
        promotion_ready=result.promotion_ready,
    )


def build_runtime_scorecard(
    harness: BenchmarkHarness | None = None,
    *,
    scorecard_id: str = "runtime-scorecard",
) -> RuntimeScorecard:
    """Build a runtime scorecard from a benchmark harness."""

    resolved_harness = run_benchmark_harness(harness_id=f"{scorecard_id}-harness") if harness is None else harness
    entries = tuple(_entry_for_result(result) for result in resolved_harness.results)
    average_overall = sum(entry.overall_score for entry in entries) / len(entries)
    severity = "info"
    status = "healthy"
    if any(entry.release_status is ReleaseCampaignStatus.BLOCKED for entry in entries):
        severity = "critical"
        status = "critical-review"
    elif any(entry.release_status in {ReleaseCampaignStatus.GUARDED, ReleaseCampaignStatus.RECOVERY_ONLY} for entry in entries):
        severity = "warning"
        status = "attention-required"

    scorecard_signal = TelemetrySignal(
        signal_name="runtime-scorecard",
        boundary=ModuleBoundaryName.TELEMETRY,
        correlation_id=scorecard_id,
        severity=severity,
        status=status,
        metrics={
            "entry_count": float(len(entries)),
            "average_overall_score": average_overall,
            "average_success_score": sum(entry.success_score for entry in entries) / len(entries),
            "average_stability_score": sum(entry.stability_score for entry in entries) / len(entries),
            "average_recovery_score": sum(entry.recovery_score for entry in entries) / len(entries),
            "average_governance_score": sum(entry.governance_score for entry in entries) / len(entries),
            "healthy_count": float(len([entry for entry in entries if entry.release_status is ReleaseCampaignStatus.READY])),
            "attention_count": float(len([entry for entry in entries if entry.release_status is not ReleaseCampaignStatus.READY])),
        },
        labels={"scorecard_id": scorecard_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_harness.final_snapshot.runtime_stage,
        signals=(scorecard_signal, resolved_harness.harness_signal, *(signal for result in resolved_harness.results for signal in result.final_snapshot.signals)),
        alerts=tuple(alert for result in resolved_harness.results for alert in result.final_snapshot.alerts),
        audit_entries=tuple(record for result in resolved_harness.results for record in result.final_snapshot.audit_entries),
        active_controls=tuple(dict.fromkeys(control for result in resolved_harness.results for control in result.final_snapshot.active_controls)),
    )
    return RuntimeScorecard(
        scorecard_id=scorecard_id,
        harness=resolved_harness,
        entries=entries,
        scorecard_signal=scorecard_signal,
        final_snapshot=final_snapshot,
    )
