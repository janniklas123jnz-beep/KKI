"""Governance agenda over review-required readiness cases."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .capacity_planner import CapacityPlanner, CapacityWindow, build_capacity_planner
from .evidence_ledger import EvidenceLedger, EvidenceLedgerEntry, EvidenceLedgerSource, build_evidence_ledger
from .escalation_router import EscalationRoutePath
from .governance import HumanDecision
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


class GovernanceAgendaStatus(str, Enum):
    """Operational agenda state for human governance review."""

    QUEUED = "queued"
    SCHEDULED = "scheduled"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class GovernanceAgendaItem:
    """One governance decision item derived from evidence and capacity state."""

    agenda_item_id: str
    case_id: str
    sequence: int
    agenda_status: GovernanceAgendaStatus
    decision: HumanDecision
    window: CapacityWindow
    route_path: EscalationRoutePath
    evidence_refs: tuple[str, ...]
    commitment_refs: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "agenda_item_id", _non_empty(self.agenda_item_id, field_name="agenda_item_id"))
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")

    def to_dict(self) -> dict[str, object]:
        return {
            "agenda_item_id": self.agenda_item_id,
            "case_id": self.case_id,
            "sequence": self.sequence,
            "agenda_status": self.agenda_status.value,
            "decision": self.decision.value,
            "window": self.window.value,
            "route_path": self.route_path.value,
            "evidence_refs": list(self.evidence_refs),
            "commitment_refs": list(self.commitment_refs),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class GovernanceAgenda:
    """Ordered governance backlog over review-required readiness cases."""

    agenda_id: str
    capacity_planner: CapacityPlanner
    evidence_ledger: EvidenceLedger
    items: tuple[GovernanceAgendaItem, ...]
    agenda_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "agenda_id", _non_empty(self.agenda_id, field_name="agenda_id"))

    @property
    def scheduled_case_ids(self) -> tuple[str, ...]:
        return tuple(item.case_id for item in self.items if item.agenda_status is GovernanceAgendaStatus.SCHEDULED)

    @property
    def blocked_case_ids(self) -> tuple[str, ...]:
        return tuple(item.case_id for item in self.items if item.agenda_status is GovernanceAgendaStatus.BLOCKED)

    @property
    def queued_case_ids(self) -> tuple[str, ...]:
        return tuple(item.case_id for item in self.items if item.agenda_status is GovernanceAgendaStatus.QUEUED)

    def to_dict(self) -> dict[str, object]:
        return {
            "agenda_id": self.agenda_id,
            "capacity_planner": self.capacity_planner.to_dict(),
            "evidence_ledger": self.evidence_ledger.to_dict(),
            "items": [item.to_dict() for item in self.items],
            "agenda_signal": self.agenda_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "scheduled_case_ids": list(self.scheduled_case_ids),
            "blocked_case_ids": list(self.blocked_case_ids),
            "queued_case_ids": list(self.queued_case_ids),
        }


def _governance_evidence_entries(ledger: EvidenceLedger, case_id: str) -> tuple[EvidenceLedgerEntry, ...]:
    return tuple(
        entry
        for entry in ledger.entries
        if entry.case_id == case_id
        and (
            entry.route_path is EscalationRoutePath.GOVERNANCE_REVIEW
            or entry.source is EvidenceLedgerSource.REVIEW
        )
    )


def _agenda_status_for_case(case_id: str, planner: CapacityPlanner) -> GovernanceAgendaStatus:
    plan_entry = next(entry for entry in planner.entries if entry.case_id == case_id)
    if plan_entry.route_path is EscalationRoutePath.RECOVERY_CONTAINMENT:
        return GovernanceAgendaStatus.BLOCKED
    if plan_entry.window is CapacityWindow.CURRENT:
        return GovernanceAgendaStatus.SCHEDULED
    return GovernanceAgendaStatus.QUEUED


def _decision_for_status(status: GovernanceAgendaStatus) -> HumanDecision:
    if status is GovernanceAgendaStatus.SCHEDULED:
        return HumanDecision.APPROVE
    if status is GovernanceAgendaStatus.BLOCKED:
        return HumanDecision.HOLD
    return HumanDecision.ESCALATE


def build_governance_agenda(
    capacity_planner: CapacityPlanner | None = None,
    evidence_ledger: EvidenceLedger | None = None,
    *,
    agenda_id: str = "governance-agenda",
) -> GovernanceAgenda:
    """Build an ordered governance agenda from capacity and evidence state."""

    resolved_planner = build_capacity_planner(planner_id=f"{agenda_id}-planner") if capacity_planner is None else capacity_planner
    resolved_ledger = build_evidence_ledger(ledger_id=f"{agenda_id}-ledger") if evidence_ledger is None else evidence_ledger
    governance_case_ids = tuple(
        dict.fromkeys(
            case_id
            for case_id in resolved_ledger.case_ids
            if any(entry.route_path is EscalationRoutePath.GOVERNANCE_REVIEW for entry in _governance_evidence_entries(resolved_ledger, case_id))
        )
    )
    items: list[GovernanceAgendaItem] = []
    for sequence, case_id in enumerate(governance_case_ids, start=1):
        evidence_entries = _governance_evidence_entries(resolved_ledger, case_id)
        plan_entry = next(entry for entry in resolved_planner.entries if entry.case_id == case_id)
        agenda_status = _agenda_status_for_case(case_id, resolved_planner)
        evidence_refs = tuple(dict.fromkeys(ref for entry in evidence_entries for ref in entry.audit_refs))
        commitment_refs = tuple(dict.fromkeys(ref for entry in evidence_entries for ref in entry.commitment_refs))
        items.append(
            GovernanceAgendaItem(
                agenda_item_id=f"{agenda_id}-{case_id}",
                case_id=case_id,
                sequence=sequence,
                agenda_status=agenda_status,
                decision=_decision_for_status(agenda_status),
                window=plan_entry.window,
                route_path=plan_entry.route_path,
                evidence_refs=evidence_refs,
                commitment_refs=commitment_refs,
                summary=f"{case_id} is queued for deterministic governance review in the {plan_entry.window.value} window.",
            )
        )
    resolved_items = tuple(items)
    if not resolved_items:
        raise ValueError("governance agenda requires at least one agenda item")

    severity = "info"
    status = GovernanceAgendaStatus.QUEUED.value
    if any(item.agenda_status is GovernanceAgendaStatus.BLOCKED for item in resolved_items):
        severity = "critical"
        status = GovernanceAgendaStatus.BLOCKED.value
    elif any(item.agenda_status is GovernanceAgendaStatus.SCHEDULED for item in resolved_items):
        severity = "warning"
        status = GovernanceAgendaStatus.SCHEDULED.value

    agenda_signal = TelemetrySignal(
        signal_name="governance-agenda",
        boundary=resolved_planner.planner_signal.boundary,
        correlation_id=agenda_id,
        severity=severity,
        status=status,
        metrics={
            "item_count": float(len(resolved_items)),
            "scheduled_count": float(len([item for item in resolved_items if item.agenda_status is GovernanceAgendaStatus.SCHEDULED])),
            "blocked_count": float(len([item for item in resolved_items if item.agenda_status is GovernanceAgendaStatus.BLOCKED])),
            "queued_count": float(len([item for item in resolved_items if item.agenda_status is GovernanceAgendaStatus.QUEUED])),
        },
        labels={"agenda_id": agenda_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_planner.final_snapshot.runtime_stage,
        signals=(agenda_signal, resolved_planner.planner_signal, resolved_ledger.ledger_signal, *resolved_ledger.final_snapshot.signals),
        alerts=resolved_ledger.final_snapshot.alerts,
        audit_entries=resolved_ledger.final_snapshot.audit_entries,
        active_controls=resolved_ledger.final_snapshot.active_controls,
    )
    return GovernanceAgenda(
        agenda_id=agenda_id,
        capacity_planner=resolved_planner,
        evidence_ledger=resolved_ledger,
        items=resolved_items,
        agenda_signal=agenda_signal,
        final_snapshot=final_snapshot,
    )
