"""Recurring recovery drills over blocked readiness cases."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .capacity_planner import CapacityLane, CapacityPlanner, build_capacity_planner
from .evidence_ledger import EvidenceLedger, EvidenceLedgerSource, build_evidence_ledger
from .escalation_router import EscalationRoutePath
from .recovery import RecoveryDisposition, RecoveryMode
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


class RecoveryDrillStatus(str, Enum):
    """Execution state for recurring recovery drills."""

    SCHEDULED = "scheduled"
    ACTIVE = "active"
    REENTRY_READY = "reentry-ready"


@dataclass(frozen=True)
class RecoveryDrill:
    """Recovery drill for one blocked case with explicit reentry conditions."""

    drill_id: str
    case_id: str
    cycle_index: int
    mode: RecoveryMode
    disposition: RecoveryDisposition
    status: RecoveryDrillStatus
    reentry_conditions: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    commitment_refs: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "drill_id", _non_empty(self.drill_id, field_name="drill_id"))
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.cycle_index < 1:
            raise ValueError("cycle_index must be positive")

    def to_dict(self) -> dict[str, object]:
        return {
            "drill_id": self.drill_id,
            "case_id": self.case_id,
            "cycle_index": self.cycle_index,
            "mode": self.mode.value,
            "disposition": self.disposition.value,
            "status": self.status.value,
            "reentry_conditions": list(self.reentry_conditions),
            "evidence_refs": list(self.evidence_refs),
            "commitment_refs": list(self.commitment_refs),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class RecoveryDrillSuite:
    """Recurring recovery drill schedule for blocked readiness paths."""

    suite_id: str
    capacity_planner: CapacityPlanner
    evidence_ledger: EvidenceLedger
    drills: tuple[RecoveryDrill, ...]
    drill_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "suite_id", _non_empty(self.suite_id, field_name="suite_id"))

    @property
    def active_case_ids(self) -> tuple[str, ...]:
        return tuple(drill.case_id for drill in self.drills if drill.status is RecoveryDrillStatus.ACTIVE)

    @property
    def scheduled_case_ids(self) -> tuple[str, ...]:
        return tuple(drill.case_id for drill in self.drills if drill.status is RecoveryDrillStatus.SCHEDULED)

    @property
    def reentry_ready_case_ids(self) -> tuple[str, ...]:
        return tuple(drill.case_id for drill in self.drills if drill.status is RecoveryDrillStatus.REENTRY_READY)

    def to_dict(self) -> dict[str, object]:
        return {
            "suite_id": self.suite_id,
            "capacity_planner": self.capacity_planner.to_dict(),
            "evidence_ledger": self.evidence_ledger.to_dict(),
            "drills": [drill.to_dict() for drill in self.drills],
            "drill_signal": self.drill_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "active_case_ids": list(self.active_case_ids),
            "scheduled_case_ids": list(self.scheduled_case_ids),
            "reentry_ready_case_ids": list(self.reentry_ready_case_ids),
        }


def _blocked_case_ids(planner: CapacityPlanner, ledger: EvidenceLedger) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            case_id
            for case_id in planner.immediate_case_ids
            if any(
                entry.case_id == case_id and entry.route_path is EscalationRoutePath.RECOVERY_CONTAINMENT
                for entry in ledger.entries
            )
        )
    )


def _reentry_conditions_for_case(case_id: str, ledger: EvidenceLedger) -> tuple[str, ...]:
    case_entries = tuple(entry for entry in ledger.entries if entry.case_id == case_id)
    conditions = ["recovery-containment-cleared"]
    if any(entry.source is EvidenceLedgerSource.REPLAY for entry in case_entries):
        conditions.append("replay-evidence-updated")
    if any(entry.source is EvidenceLedgerSource.REMEDIATION for entry in case_entries):
        conditions.append("remediation-commitments-complete")
    if any(entry.source is EvidenceLedgerSource.REVIEW for entry in case_entries):
        conditions.append("readiness-review-revalidated")
    return tuple(conditions)


def _status_for_case(case_id: str, planner: CapacityPlanner, conditions: tuple[str, ...]) -> RecoveryDrillStatus:
    plan_entry = next(entry for entry in planner.entries if entry.case_id == case_id)
    if plan_entry.lane is CapacityLane.ADMIT and "replay-evidence-updated" in conditions:
        return RecoveryDrillStatus.ACTIVE
    return RecoveryDrillStatus.SCHEDULED


def build_recovery_drill_suite(
    capacity_planner: CapacityPlanner | None = None,
    evidence_ledger: EvidenceLedger | None = None,
    *,
    suite_id: str = "recovery-drills",
) -> RecoveryDrillSuite:
    """Build recurring recovery drills and reentry conditions for blocked cases."""

    resolved_planner = build_capacity_planner(planner_id=f"{suite_id}-planner") if capacity_planner is None else capacity_planner
    resolved_ledger = build_evidence_ledger(ledger_id=f"{suite_id}-ledger") if evidence_ledger is None else evidence_ledger
    blocked_case_ids = _blocked_case_ids(resolved_planner, resolved_ledger)
    drills = []
    for index, case_id in enumerate(blocked_case_ids, start=1):
        conditions = _reentry_conditions_for_case(case_id, resolved_ledger)
        case_entries = tuple(entry for entry in resolved_ledger.entries if entry.case_id == case_id)
        status = _status_for_case(case_id, resolved_planner, conditions)
        evidence_refs = tuple(dict.fromkeys(ref for entry in case_entries for ref in entry.audit_refs))
        commitment_refs = tuple(dict.fromkeys(ref for entry in case_entries for ref in entry.commitment_refs))
        drills.append(
            RecoveryDrill(
                drill_id=f"{suite_id}-{case_id}",
                case_id=case_id,
                cycle_index=index,
                mode=RecoveryMode.ROLLBACK,
                disposition=RecoveryDisposition.CONTAIN,
                status=status,
                reentry_conditions=conditions,
                evidence_refs=evidence_refs,
                commitment_refs=commitment_refs,
                summary=f"{case_id} remains on a recurring rollback-containment drill until reentry conditions are satisfied.",
            )
        )
    resolved_drills = tuple(drills)
    if not resolved_drills:
        raise ValueError("recovery drills require at least one blocked case")

    severity = "warning"
    status = RecoveryDrillStatus.SCHEDULED.value
    if any(drill.status is RecoveryDrillStatus.ACTIVE for drill in resolved_drills):
        severity = "critical"
        status = RecoveryDrillStatus.ACTIVE.value
    elif any(drill.status is RecoveryDrillStatus.REENTRY_READY for drill in resolved_drills):
        severity = "info"
        status = RecoveryDrillStatus.REENTRY_READY.value

    drill_signal = TelemetrySignal(
        signal_name="recovery-drills",
        boundary=resolved_planner.planner_signal.boundary,
        correlation_id=suite_id,
        severity=severity,
        status=status,
        metrics={
            "drill_count": float(len(resolved_drills)),
            "active_count": float(len([drill for drill in resolved_drills if drill.status is RecoveryDrillStatus.ACTIVE])),
            "scheduled_count": float(len([drill for drill in resolved_drills if drill.status is RecoveryDrillStatus.SCHEDULED])),
            "reentry_ready_count": float(len([drill for drill in resolved_drills if drill.status is RecoveryDrillStatus.REENTRY_READY])),
        },
        labels={"suite_id": suite_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_planner.final_snapshot.runtime_stage,
        signals=(drill_signal, resolved_planner.planner_signal, resolved_ledger.ledger_signal, *resolved_ledger.final_snapshot.signals),
        alerts=resolved_ledger.final_snapshot.alerts,
        audit_entries=resolved_ledger.final_snapshot.audit_entries,
        active_controls=resolved_ledger.final_snapshot.active_controls,
    )
    return RecoveryDrillSuite(
        suite_id=suite_id,
        capacity_planner=resolved_planner,
        evidence_ledger=resolved_ledger,
        drills=resolved_drills,
        drill_signal=drill_signal,
        final_snapshot=final_snapshot,
    )
