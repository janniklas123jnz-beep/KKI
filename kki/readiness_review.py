"""Final readiness review over runtime scorecards and benchmark chains."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .benchmark_harness import BenchmarkHarness, run_benchmark_harness
from .module_boundaries import ModuleBoundaryName
from .release_campaigns import ReleaseCampaignStatus
from .runtime_scorecard import RuntimeScorecard, build_runtime_scorecard
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


class ReadinessFindingSeverity(str, Enum):
    """Canonical severity levels for readiness findings."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True)
class ReadinessFinding:
    """A concrete finding surfaced during the final readiness review."""

    finding_id: str
    case_id: str
    severity: ReadinessFindingSeverity
    summary: str
    recommendation: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "finding_id", _non_empty(self.finding_id, field_name="finding_id"))
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        object.__setattr__(self, "recommendation", _non_empty(self.recommendation, field_name="recommendation"))

    def to_dict(self) -> dict[str, object]:
        return {
            "finding_id": self.finding_id,
            "case_id": self.case_id,
            "severity": self.severity.value,
            "summary": self.summary,
            "recommendation": self.recommendation,
        }


@dataclass(frozen=True)
class ReadinessReview:
    """Final operational readiness review over the benchmark/scorecard chain."""

    review_id: str
    harness: BenchmarkHarness
    scorecard: RuntimeScorecard
    findings: tuple[ReadinessFinding, ...]
    review_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "review_id", _non_empty(self.review_id, field_name="review_id"))

    @property
    def healthy_case_ids(self) -> tuple[str, ...]:
        return self.scorecard.healthy_case_ids

    @property
    def attention_case_ids(self) -> tuple[str, ...]:
        return self.scorecard.attention_case_ids

    @property
    def blocked_case_ids(self) -> tuple[str, ...]:
        return tuple(
            result.case.case_id
            for result in self.harness.results
            if result.status is ReleaseCampaignStatus.BLOCKED
        )

    @property
    def release_ready(self) -> bool:
        return not self.blocked_case_ids and not any(
            finding.severity is ReadinessFindingSeverity.CRITICAL for finding in self.findings
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "review_id": self.review_id,
            "harness": self.harness.to_dict(),
            "scorecard": self.scorecard.to_dict(),
            "findings": [finding.to_dict() for finding in self.findings],
            "review_signal": self.review_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "healthy_case_ids": list(self.healthy_case_ids),
            "attention_case_ids": list(self.attention_case_ids),
            "blocked_case_ids": list(self.blocked_case_ids),
            "release_ready": self.release_ready,
        }


def _finding_for_result(review_id: str, case_id: str, status: ReleaseCampaignStatus, overall_score: float) -> ReadinessFinding | None:
    if status is ReleaseCampaignStatus.BLOCKED:
        return ReadinessFinding(
            finding_id=f"{review_id}-{case_id}-containment",
            case_id=case_id,
            severity=ReadinessFindingSeverity.CRITICAL,
            summary=f"{case_id} remains blocked by containment paths",
            recommendation="Resolve rollback containment and re-run benchmark readiness checks.",
        )
    if status is ReleaseCampaignStatus.RECOVERY_ONLY:
        return ReadinessFinding(
            finding_id=f"{review_id}-{case_id}-recovery",
            case_id=case_id,
            severity=ReadinessFindingSeverity.WARNING,
            summary=f"{case_id} is limited to recovery-only execution",
            recommendation="Stabilize recovery flow and restore promotion eligibility before rollout.",
        )
    if status is ReleaseCampaignStatus.GUARDED:
        return ReadinessFinding(
            finding_id=f"{review_id}-{case_id}-governance",
            case_id=case_id,
            severity=ReadinessFindingSeverity.WARNING,
            summary=f"{case_id} still requires governance review",
            recommendation="Close governance findings and re-evaluate guarded promotion criteria.",
        )
    if overall_score < 0.85:
        return ReadinessFinding(
            finding_id=f"{review_id}-{case_id}-score",
            case_id=case_id,
            severity=ReadinessFindingSeverity.INFO,
            summary=f"{case_id} is healthy but below target score reserve",
            recommendation="Improve operational headroom before broad rollout.",
        )
    return None


def build_readiness_review(
    scorecard: RuntimeScorecard | None = None,
    *,
    review_id: str = "readiness-review",
) -> ReadinessReview:
    """Build the final readiness review over the benchmark and scorecard chain."""

    resolved_scorecard = build_runtime_scorecard(scorecard_id=f"{review_id}-scorecard") if scorecard is None else scorecard
    harness = resolved_scorecard.harness
    findings = tuple(
        finding
        for entry in resolved_scorecard.entries
        for finding in (
            _finding_for_result(
                review_id,
                entry.case_id,
                entry.release_status,
                entry.overall_score,
            ),
        )
        if finding is not None
    )
    severity = "info"
    status = "ready"
    if any(finding.severity is ReadinessFindingSeverity.CRITICAL for finding in findings):
        severity = "critical"
        status = "not-ready"
    elif any(finding.severity is ReadinessFindingSeverity.WARNING for finding in findings):
        severity = "warning"
        status = "review-required"

    review_signal = TelemetrySignal(
        signal_name="readiness-review",
        boundary=ModuleBoundaryName.GOVERNANCE,
        correlation_id=review_id,
        severity=severity,
        status=status,
        metrics={
            "finding_count": float(len(findings)),
            "critical_finding_count": float(len([f for f in findings if f.severity is ReadinessFindingSeverity.CRITICAL])),
            "warning_finding_count": float(len([f for f in findings if f.severity is ReadinessFindingSeverity.WARNING])),
            "healthy_case_count": float(len(resolved_scorecard.healthy_case_ids)),
            "attention_case_count": float(len(resolved_scorecard.attention_case_ids)),
            "average_overall_score": resolved_scorecard.average_overall_score,
        },
        labels={"review_id": review_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_scorecard.final_snapshot.runtime_stage,
        signals=(review_signal, resolved_scorecard.scorecard_signal, harness.harness_signal, *(signal for result in harness.results for signal in result.final_snapshot.signals)),
        alerts=tuple(alert for result in harness.results for alert in result.final_snapshot.alerts),
        audit_entries=tuple(record for result in harness.results for record in result.final_snapshot.audit_entries),
        active_controls=tuple(dict.fromkeys(control for result in harness.results for control in result.final_snapshot.active_controls)),
    )
    return ReadinessReview(
        review_id=review_id,
        harness=harness,
        scorecard=resolved_scorecard,
        findings=findings,
        review_signal=review_signal,
        final_snapshot=final_snapshot,
    )
