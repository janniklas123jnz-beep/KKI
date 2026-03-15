"""Deterministic benchmark harness over missions, waves, and release campaigns."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from .change_windows import ChangeWindow, open_change_window
from .escalation_coordinator import EscalationPlan, coordinate_escalations
from .incident_detector import IncidentCause, IncidentReport, IncidentSeverity, OperationsIncident, detect_incidents
from .mission_profiles import MissionProfile, MissionScenario, mission_profile_for_name
from .module_boundaries import ModuleBoundaryName
from .release_campaigns import ReleaseCampaign, ReleaseCampaignStatus, build_release_campaign
from .run_ledger import OperationsRunLedger, ledger_for_wave
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot
from .wave_orchestration import OperationsWave, WaveBudgetPolicy, run_operations_wave


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _frozen_mapping(data: Mapping[str, object] | None) -> Mapping[str, object]:
    return MappingProxyType(dict(data or {}))


def _ordered_union(*groups: tuple[str, ...]) -> tuple[str, ...]:
    ordered: list[str] = []
    for group in groups:
        for item in group:
            if item not in ordered:
                ordered.append(item)
    return tuple(ordered)


class BenchmarkReleaseMode(str, Enum):
    """Canonical release-path presets used by benchmark cases."""

    READY = "ready"
    GUARDED = "guarded"
    RECOVERY_ONLY = "recovery-only"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class BenchmarkCase:
    """Executable benchmark case spanning missions and a target release mode."""

    case_id: str
    title: str
    missions: tuple[MissionProfile, ...]
    release_mode: BenchmarkReleaseMode = BenchmarkReleaseMode.READY
    budget_policy: WaveBudgetPolicy | None = None
    labels: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))
        object.__setattr__(self, "title", _non_empty(self.title, field_name="title"))
        if not self.missions:
            raise ValueError("missions must not be empty")
        object.__setattr__(self, "labels", _frozen_mapping(self.labels))

    @property
    def mission_refs(self) -> tuple[str, ...]:
        return tuple(mission.mission_ref for mission in self.missions)

    def to_dict(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "title": self.title,
            "missions": [mission.to_dict() for mission in self.missions],
            "release_mode": self.release_mode.value,
            "budget_policy": None if self.budget_policy is None else self.budget_policy.to_dict(),
            "labels": dict(self.labels),
            "mission_refs": list(self.mission_refs),
        }


@dataclass(frozen=True)
class BenchmarkCaseResult:
    """Full benchmark result for a single benchmark case."""

    harness_id: str
    case: BenchmarkCase
    wave: OperationsWave
    ledger: OperationsRunLedger
    incident_report: IncidentReport
    escalation_plan: EscalationPlan
    change_window: ChangeWindow
    release_campaign: ReleaseCampaign
    benchmark_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "harness_id", _non_empty(self.harness_id, field_name="harness_id"))

    @property
    def status(self) -> ReleaseCampaignStatus:
        return self.release_campaign.status

    @property
    def promotion_ready(self) -> bool:
        return self.status is ReleaseCampaignStatus.READY and bool(self.release_campaign.promotion_refs)

    def to_dict(self) -> dict[str, object]:
        return {
            "harness_id": self.harness_id,
            "case": self.case.to_dict(),
            "wave": self.wave.to_dict(),
            "ledger": self.ledger.to_dict(),
            "incident_report": self.incident_report.to_dict(),
            "escalation_plan": self.escalation_plan.to_dict(),
            "change_window": self.change_window.to_dict(),
            "release_campaign": self.release_campaign.to_dict(),
            "benchmark_signal": self.benchmark_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "status": self.status.value,
            "promotion_ready": self.promotion_ready,
        }


@dataclass(frozen=True)
class BenchmarkHarness:
    """Aggregated deterministic benchmark harness over multiple benchmark cases."""

    harness_id: str
    cases: tuple[BenchmarkCase, ...]
    results: tuple[BenchmarkCaseResult, ...]
    harness_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "harness_id", _non_empty(self.harness_id, field_name="harness_id"))

    @property
    def ready_case_ids(self) -> tuple[str, ...]:
        return tuple(result.case.case_id for result in self.results if result.status is ReleaseCampaignStatus.READY)

    @property
    def guarded_case_ids(self) -> tuple[str, ...]:
        return tuple(result.case.case_id for result in self.results if result.status is ReleaseCampaignStatus.GUARDED)

    @property
    def recovery_case_ids(self) -> tuple[str, ...]:
        return tuple(result.case.case_id for result in self.results if result.status is ReleaseCampaignStatus.RECOVERY_ONLY)

    @property
    def blocked_case_ids(self) -> tuple[str, ...]:
        return tuple(result.case.case_id for result in self.results if result.status is ReleaseCampaignStatus.BLOCKED)

    @property
    def promotion_ready_refs(self) -> tuple[str, ...]:
        return _ordered_union(*(result.release_campaign.promotion_refs for result in self.results))

    def to_dict(self) -> dict[str, object]:
        return {
            "harness_id": self.harness_id,
            "cases": [case.to_dict() for case in self.cases],
            "results": [result.to_dict() for result in self.results],
            "harness_signal": self.harness_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "ready_case_ids": list(self.ready_case_ids),
            "guarded_case_ids": list(self.guarded_case_ids),
            "recovery_case_ids": list(self.recovery_case_ids),
            "blocked_case_ids": list(self.blocked_case_ids),
            "promotion_ready_refs": list(self.promotion_ready_refs),
        }


def _benchmark_case_signal(
    *,
    harness_id: str,
    case: BenchmarkCase,
    release_campaign: ReleaseCampaign,
) -> TelemetrySignal:
    severity = "info"
    if release_campaign.status is ReleaseCampaignStatus.BLOCKED:
        severity = "critical"
    elif release_campaign.status in {ReleaseCampaignStatus.GUARDED, ReleaseCampaignStatus.RECOVERY_ONLY}:
        severity = "warning"
    return TelemetrySignal(
        signal_name="benchmark-case",
        boundary=ModuleBoundaryName.TELEMETRY,
        correlation_id=f"{harness_id}-{case.case_id}",
        severity=severity,
        status=release_campaign.status.value,
        metrics={
            "mission_count": float(len(case.missions)),
            "promotion_count": float(len(release_campaign.promotion_refs)),
            "governance_review_count": float(len(release_campaign.governance_review_refs)),
            "recovery_count": float(len(release_campaign.recovery_only_refs)),
            "blocked_count": float(len(release_campaign.blocked_refs)),
        },
        labels={
            "case_id": case.case_id,
            "release_mode": case.release_mode.value,
        },
    )


def _override_incident_report(case: BenchmarkCase, base_report: IncidentReport) -> IncidentReport:
    if case.release_mode is BenchmarkReleaseMode.READY:
        return base_report

    mission_ref = case.mission_refs[0]
    severity = "warning"
    status = "attention-required"
    incident = OperationsIncident(
        incident_id=f"incident-{base_report.wave_id}-{case.release_mode.value}",
        wave_id=base_report.wave_id,
        severity=IncidentSeverity.WARNING,
        cause=IncidentCause.GOVERNANCE,
        summary=f"benchmark release path {case.release_mode.value} for mission {mission_ref}",
        mission_refs=(mission_ref,),
        trigger_statuses=("benchmark", case.release_mode.value),
        escalation_required=True,
        labels={"benchmark_case": case.case_id},
    )
    if case.release_mode is BenchmarkReleaseMode.GUARDED:
        incident = OperationsIncident(
            incident_id=f"incident-{base_report.wave_id}-guarded",
            wave_id=base_report.wave_id,
            severity=IncidentSeverity.WARNING,
            cause=IncidentCause.GOVERNANCE,
            summary=f"governance review required for mission {mission_ref}",
            mission_refs=(mission_ref,),
            trigger_statuses=("escalated",),
            escalation_required=True,
            labels={"benchmark_case": case.case_id},
        )
    elif case.release_mode is BenchmarkReleaseMode.RECOVERY_ONLY:
        incident = OperationsIncident(
            incident_id=f"incident-{base_report.wave_id}-recovery",
            wave_id=base_report.wave_id,
            severity=IncidentSeverity.WARNING,
            cause=IncidentCause.RECOVERY,
            summary=f"recovery restart required for mission {mission_ref}",
            mission_refs=(mission_ref,),
            trigger_statuses=("restart-active",),
            escalation_required=True,
            labels={"benchmark_case": case.case_id},
        )
    elif case.release_mode is BenchmarkReleaseMode.BLOCKED:
        severity = "critical"
        status = "critical-incidents"
        incident = OperationsIncident(
            incident_id=f"incident-{base_report.wave_id}-blocked",
            wave_id=base_report.wave_id,
            severity=IncidentSeverity.CRITICAL,
            cause=IncidentCause.RECOVERY,
            summary=f"critical containment required for mission {mission_ref}",
            mission_refs=(mission_ref,),
            trigger_statuses=("rollback-active",),
            escalation_required=True,
            labels={"benchmark_case": case.case_id},
        )

    incident_signal = TelemetrySignal(
        signal_name="incident-report",
        boundary=ModuleBoundaryName.TELEMETRY,
        correlation_id=base_report.wave_id,
        severity=severity,
        status=status,
        metrics={
            "incident_count": 1.0,
            "critical_count": 1.0 if incident.severity is IncidentSeverity.CRITICAL else 0.0,
            "warning_count": 1.0 if incident.severity is IncidentSeverity.WARNING else 0.0,
        },
        labels={
            "wave_id": base_report.wave_id,
            "benchmark_case": case.case_id,
            "release_mode": case.release_mode.value,
        },
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=base_report.final_snapshot.runtime_stage,
        signals=(incident_signal, *base_report.final_snapshot.signals),
        alerts=base_report.final_snapshot.alerts,
        audit_entries=base_report.final_snapshot.audit_entries,
        active_controls=base_report.final_snapshot.active_controls,
    )
    return IncidentReport(
        wave_id=base_report.wave_id,
        ledger=base_report.ledger,
        incidents=(incident,),
        incident_signal=incident_signal,
        final_snapshot=final_snapshot,
    )


def _run_case(harness_id: str, case: BenchmarkCase) -> BenchmarkCaseResult:
    wave = run_operations_wave(
        case.missions,
        wave_id=f"{harness_id}-{case.case_id}-wave",
        budget_policy=case.budget_policy,
    )
    ledger = ledger_for_wave(wave)
    incident_report = _override_incident_report(case, detect_incidents(ledger))
    escalation_plan = coordinate_escalations(incident_report)
    change_window = open_change_window((escalation_plan,), window_id=f"{harness_id}-{case.case_id}-window")
    release_campaign = build_release_campaign((change_window,), campaign_id=f"{harness_id}-{case.case_id}-campaign")
    benchmark_signal = _benchmark_case_signal(harness_id=harness_id, case=case, release_campaign=release_campaign)
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=release_campaign.final_snapshot.runtime_stage,
        signals=(benchmark_signal, release_campaign.campaign_signal, *release_campaign.final_snapshot.signals),
        alerts=release_campaign.final_snapshot.alerts,
        audit_entries=release_campaign.final_snapshot.audit_entries,
        active_controls=release_campaign.final_snapshot.active_controls,
    )
    return BenchmarkCaseResult(
        harness_id=harness_id,
        case=case,
        wave=wave,
        ledger=ledger,
        incident_report=incident_report,
        escalation_plan=escalation_plan,
        change_window=change_window,
        release_campaign=release_campaign,
        benchmark_signal=benchmark_signal,
        final_snapshot=final_snapshot,
    )


def benchmark_case_matrix() -> tuple[BenchmarkCase, ...]:
    """Return the canonical deterministic benchmark case matrix."""

    return (
        BenchmarkCase(
            case_id="pilot-ready",
            title="pilot cutover ready path",
            missions=(mission_profile_for_name("pilot-cutover"),),
            release_mode=BenchmarkReleaseMode.READY,
            labels={"scenario": MissionScenario.CUTOVER.value},
        ),
        BenchmarkCase(
            case_id="shadow-guarded",
            title="shadow hardening guarded path",
            missions=(
                MissionProfile(
                    mission_ref="benchmark-shadow-guarded",
                    title="benchmark shadow guarded",
                    scenario=MissionScenario.HARDENING,
                    runtime_stage=mission_profile_for_name("shadow-hardening").runtime_stage,
                    runtime_profile="resilient-runtime-dna",
                    target_boundary=ModuleBoundaryName.ROLLOUT,
                    budget_share=0.1,
                    observed_budget=0.09,
                    policy=mission_profile_for_name("shadow-hardening").policy,
                    labels={"scenario": MissionScenario.HARDENING.value},
                ),
            ),
            release_mode=BenchmarkReleaseMode.GUARDED,
            labels={"scenario": MissionScenario.HARDENING.value},
        ),
        BenchmarkCase(
            case_id="recovery-resume",
            title="recovery drill restart path",
            missions=(mission_profile_for_name("recovery-drill"),),
            release_mode=BenchmarkReleaseMode.RECOVERY_ONLY,
            labels={"scenario": MissionScenario.RECOVERY_DRILL.value},
        ),
        BenchmarkCase(
            case_id="pilot-containment",
            title="pilot cutover containment path",
            missions=(mission_profile_for_name("pilot-cutover"),),
            release_mode=BenchmarkReleaseMode.BLOCKED,
            labels={"scenario": MissionScenario.CUTOVER.value},
        ),
    )


def run_benchmark_harness(
    cases: tuple[BenchmarkCase, ...] | list[BenchmarkCase] | None = None,
    *,
    harness_id: str = "benchmark-harness",
) -> BenchmarkHarness:
    """Run the deterministic benchmark harness over a benchmark case matrix."""

    resolved_cases = tuple(benchmark_case_matrix() if cases is None else cases)
    if not resolved_cases:
        raise ValueError("cases must not be empty")
    results = tuple(_run_case(harness_id, case) for case in resolved_cases)

    severity = "info"
    status = "ready"
    if any(result.status is ReleaseCampaignStatus.BLOCKED for result in results):
        severity = "critical"
        status = "blocked"
    elif any(result.status is ReleaseCampaignStatus.RECOVERY_ONLY for result in results):
        severity = "warning"
        status = "recovery-only"
    elif any(result.status is ReleaseCampaignStatus.GUARDED for result in results):
        severity = "warning"
        status = "guarded"

    harness_signal = TelemetrySignal(
        signal_name="benchmark-harness",
        boundary=ModuleBoundaryName.TELEMETRY,
        correlation_id=harness_id,
        severity=severity,
        status=status,
        metrics={
            "case_count": float(len(results)),
            "ready_count": float(len([result for result in results if result.status is ReleaseCampaignStatus.READY])),
            "guarded_count": float(len([result for result in results if result.status is ReleaseCampaignStatus.GUARDED])),
            "recovery_count": float(len([result for result in results if result.status is ReleaseCampaignStatus.RECOVERY_ONLY])),
            "blocked_count": float(len([result for result in results if result.status is ReleaseCampaignStatus.BLOCKED])),
            "promotion_ready_count": float(len([result for result in results if result.promotion_ready])),
        },
        labels={"harness_id": harness_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=results[0].final_snapshot.runtime_stage,
        signals=(harness_signal, *(result.benchmark_signal for result in results), *(signal for result in results for signal in result.final_snapshot.signals)),
        alerts=tuple(alert for result in results for alert in result.final_snapshot.alerts),
        audit_entries=tuple(record for result in results for record in result.final_snapshot.audit_entries),
        active_controls=tuple(dict.fromkeys(control for result in results for control in result.final_snapshot.active_controls)),
    )
    return BenchmarkHarness(
        harness_id=harness_id,
        cases=resolved_cases,
        results=results,
        harness_signal=harness_signal,
        final_snapshot=final_snapshot,
    )
