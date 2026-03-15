"""Persistent evidence ledger over review, replay, remediation, and routing."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .data_models import EvidenceRecord
from .escalation_router import EscalationRoutePath, EscalationRouter, build_escalation_router
from .module_boundaries import ModuleBoundaryName
from .readiness_review import (
    ReadinessFinding,
    ReadinessFindingSeverity,
    ReadinessReview,
    build_readiness_review,
)
from .remediation_campaigns import RemediationCampaign, RemediationCampaignStage, build_remediation_campaign
from .scenario_replay import ScenarioReplayResult, ScenarioReplaySuite, build_scenario_replay
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


class EvidenceLedgerSource(str, Enum):
    """Canonical source streams collected in the persistent evidence ledger."""

    REVIEW = "review"
    REPLAY = "replay"
    REMEDIATION = "remediation"


@dataclass(frozen=True)
class EvidenceLedgerEntry:
    """Persistent evidence record keyed to one case and one source stream."""

    ledger_entry_id: str
    case_id: str
    cycle_index: int
    source: EvidenceLedgerSource
    route_path: EscalationRoutePath
    boundary: ModuleBoundaryName
    evidence_record: EvidenceRecord
    audit_refs: tuple[str, ...]
    commitment_refs: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "ledger_entry_id", _non_empty(self.ledger_entry_id, field_name="ledger_entry_id"))
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.cycle_index < 1:
            raise ValueError("cycle_index must be positive")

    def to_dict(self) -> dict[str, object]:
        return {
            "ledger_entry_id": self.ledger_entry_id,
            "case_id": self.case_id,
            "cycle_index": self.cycle_index,
            "source": self.source.value,
            "route_path": self.route_path.value,
            "boundary": self.boundary.value,
            "evidence_record": self.evidence_record.to_dict(),
            "audit_refs": list(self.audit_refs),
            "commitment_refs": list(self.commitment_refs),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class EvidenceLedger:
    """Persistent evidence ledger spanning review, replay, remediation, and routing."""

    ledger_id: str
    review: ReadinessReview
    replay_suite: ScenarioReplaySuite
    remediation_campaign: RemediationCampaign
    escalation_router: EscalationRouter
    entries: tuple[EvidenceLedgerEntry, ...]
    ledger_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "ledger_id", _non_empty(self.ledger_id, field_name="ledger_id"))

    @property
    def case_ids(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(entry.case_id for entry in self.entries))

    @property
    def blocked_case_ids(self) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(
                entry.case_id
                for entry in self.entries
                if entry.route_path is EscalationRoutePath.RECOVERY_CONTAINMENT
            )
        )

    @property
    def governance_case_ids(self) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(
                entry.case_id for entry in self.entries if entry.route_path is EscalationRoutePath.GOVERNANCE_REVIEW
            )
        )

    @property
    def recovery_case_ids(self) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(
                entry.case_id
                for entry in self.entries
                if entry.route_path in {EscalationRoutePath.RECOVERY_RESTART, EscalationRoutePath.RECOVERY_CONTAINMENT}
            )
        )

    @property
    def commitment_refs(self) -> tuple[str, ...]:
        ordered: list[str] = []
        for entry in self.entries:
            for commitment_ref in entry.commitment_refs:
                if commitment_ref not in ordered:
                    ordered.append(commitment_ref)
        return tuple(ordered)

    def to_dict(self) -> dict[str, object]:
        return {
            "ledger_id": self.ledger_id,
            "review": self.review.to_dict(),
            "replay_suite": self.replay_suite.to_dict(),
            "remediation_campaign": self.remediation_campaign.to_dict(),
            "escalation_router": self.escalation_router.to_dict(),
            "entries": [entry.to_dict() for entry in self.entries],
            "ledger_signal": self.ledger_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "case_ids": list(self.case_ids),
            "blocked_case_ids": list(self.blocked_case_ids),
            "governance_case_ids": list(self.governance_case_ids),
            "recovery_case_ids": list(self.recovery_case_ids),
            "commitment_refs": list(self.commitment_refs),
        }


def _review_evidence(ledger_id: str, finding: ReadinessFinding) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_type="readiness-review-finding",
        subject=finding.case_id,
        correlation_id=ledger_id,
        audit_ref=f"audit-{ledger_id}-{finding.finding_id}",
        payload={
            "finding_id": finding.finding_id,
            "severity": finding.severity.value,
            "summary": finding.summary,
            "recommendation": finding.recommendation,
        },
    )


def _replay_evidence(ledger_id: str, result: ScenarioReplayResult) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_type="scenario-replay-result",
        subject=result.item.source_case_id,
        correlation_id=ledger_id,
        audit_ref=f"audit-{ledger_id}-{result.replay_id}-{result.item.source_case_id}",
        payload={
            "replay_id": result.replay_id,
            "replay_mode": result.item.replay_mode.value,
            "baseline_status": result.item.baseline_status.value,
            "replay_status": result.result.status.value,
            "stable": result.stable,
        },
    )


def _route_by_case(router: EscalationRouter) -> dict[str, object]:
    return {route.case_id: route for route in router.routes}


def _review_entries(
    ledger_id: str,
    review: ReadinessReview,
    router: EscalationRouter,
) -> tuple[EvidenceLedgerEntry, ...]:
    routes = _route_by_case(router)
    entries: list[EvidenceLedgerEntry] = []
    for finding in review.findings:
        route = routes[finding.case_id]
        evidence_record = _review_evidence(ledger_id, finding)
        entries.append(
            EvidenceLedgerEntry(
                ledger_entry_id=f"{ledger_id}-{finding.case_id}-review",
                case_id=finding.case_id,
                cycle_index=route.due_cycle,
                source=EvidenceLedgerSource.REVIEW,
                route_path=route.path,
                boundary=ModuleBoundaryName.GOVERNANCE,
                evidence_record=evidence_record,
                audit_refs=(evidence_record.audit_ref,),
                commitment_refs=(),
                summary=finding.summary,
            )
        )
    return tuple(entries)


def _replay_entries(
    ledger_id: str,
    replay_suite: ScenarioReplaySuite,
    router: EscalationRouter,
) -> tuple[EvidenceLedgerEntry, ...]:
    routes = _route_by_case(router)
    entries: list[EvidenceLedgerEntry] = []
    for result in replay_suite.results:
        route = routes[result.item.source_case_id]
        evidence_record = _replay_evidence(ledger_id, result)
        summary = f"{result.item.source_case_id} replay remained stable." if result.stable else f"{result.item.source_case_id} replay drifted from baseline."
        entries.append(
            EvidenceLedgerEntry(
                ledger_entry_id=f"{ledger_id}-{result.item.source_case_id}-replay",
                case_id=result.item.source_case_id,
                cycle_index=route.due_cycle,
                source=EvidenceLedgerSource.REPLAY,
                route_path=route.path,
                boundary=result.replay_signal.boundary,
                evidence_record=evidence_record,
                audit_refs=(evidence_record.audit_ref,),
                commitment_refs=(),
                summary=summary,
            )
        )
    return tuple(entries)


def _remediation_entries(
    ledger_id: str,
    remediation_campaign: RemediationCampaign,
    router: EscalationRouter,
) -> tuple[EvidenceLedgerEntry, ...]:
    routes = _route_by_case(router)
    entries: list[EvidenceLedgerEntry] = []
    for stage in remediation_campaign.stages:
        route = routes[stage.case_id]
        for index, evidence_record in enumerate(stage.evidence_records, start=1):
            entries.append(
                EvidenceLedgerEntry(
                    ledger_entry_id=f"{ledger_id}-{stage.case_id}-remediation-{index}-{stage.stage_type.value}",
                    case_id=stage.case_id,
                    cycle_index=route.due_cycle,
                    source=EvidenceLedgerSource.REMEDIATION,
                    route_path=route.path,
                    boundary=stage.owner,
                    evidence_record=evidence_record,
                    audit_refs=(evidence_record.audit_ref,),
                    commitment_refs=stage.commitment_refs,
                    summary=f"{stage.case_id} remediation evidence recorded for {stage.stage_type.value}.",
                )
            )
    return tuple(entries)


def build_evidence_ledger(
    review: ReadinessReview | None = None,
    replay_suite: ScenarioReplaySuite | None = None,
    remediation_campaign: RemediationCampaign | None = None,
    escalation_router: EscalationRouter | None = None,
    *,
    ledger_id: str = "evidence-ledger",
) -> EvidenceLedger:
    """Build a persistent evidence ledger over review, replay, remediation, and routing."""

    resolved_review = build_readiness_review(review_id=f"{ledger_id}-review") if review is None else review
    resolved_replay_suite = build_scenario_replay(replay_id=f"{ledger_id}-replay") if replay_suite is None else replay_suite
    resolved_remediation_campaign = (
        build_remediation_campaign(campaign_id=f"{ledger_id}-campaign")
        if remediation_campaign is None
        else remediation_campaign
    )
    resolved_router = build_escalation_router(router_id=f"{ledger_id}-router") if escalation_router is None else escalation_router
    entries = (
        *_review_entries(ledger_id, resolved_review, resolved_router),
        *_replay_entries(ledger_id, resolved_replay_suite, resolved_router),
        *_remediation_entries(ledger_id, resolved_remediation_campaign, resolved_router),
    )
    resolved_entries = tuple(entries)
    if not resolved_entries:
        raise ValueError("evidence ledger requires at least one entry")

    severity = "info"
    status = "steady-evidence"
    if any(entry.route_path is EscalationRoutePath.RECOVERY_CONTAINMENT for entry in resolved_entries):
        severity = "critical"
        status = "blocked-evidence"
    elif any(entry.route_path in {EscalationRoutePath.GOVERNANCE_REVIEW, EscalationRoutePath.RECOVERY_RESTART} for entry in resolved_entries):
        severity = "warning"
        status = "review-evidence"

    ledger_signal = TelemetrySignal(
        signal_name="evidence-ledger",
        boundary=ModuleBoundaryName.TELEMETRY,
        correlation_id=ledger_id,
        severity=severity,
        status=status,
        metrics={
            "entry_count": float(len(resolved_entries)),
            "case_count": float(len(tuple(dict.fromkeys(entry.case_id for entry in resolved_entries)))),
            "review_entry_count": float(len([entry for entry in resolved_entries if entry.source is EvidenceLedgerSource.REVIEW])),
            "replay_entry_count": float(len([entry for entry in resolved_entries if entry.source is EvidenceLedgerSource.REPLAY])),
            "remediation_entry_count": float(len([entry for entry in resolved_entries if entry.source is EvidenceLedgerSource.REMEDIATION])),
            "commitment_count": float(len(tuple(dict.fromkeys(ref for entry in resolved_entries for ref in entry.commitment_refs)))),
        },
        labels={"ledger_id": ledger_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_router.final_snapshot.runtime_stage,
        signals=(
            ledger_signal,
            resolved_review.review_signal,
            resolved_replay_suite.replay_signal,
            resolved_remediation_campaign.campaign_signal,
            resolved_router.router_signal,
            *resolved_router.final_snapshot.signals,
        ),
        alerts=resolved_router.final_snapshot.alerts,
        audit_entries=resolved_router.final_snapshot.audit_entries,
        active_controls=resolved_router.final_snapshot.active_controls,
    )
    return EvidenceLedger(
        ledger_id=ledger_id,
        review=resolved_review,
        replay_suite=resolved_replay_suite,
        remediation_campaign=resolved_remediation_campaign,
        escalation_router=resolved_router,
        entries=resolved_entries,
        ledger_signal=ledger_signal,
        final_snapshot=final_snapshot,
    )
