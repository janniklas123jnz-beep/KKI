"""Change-window coordination over escalation plans."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .escalation_coordinator import EscalationPath, EscalationPlan
from .module_boundaries import ModuleBoundaryName
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


class ChangeWindowStatus(str, Enum):
    """Canonical readiness states for coordinated change windows."""

    OPEN = "open"
    GUARDED = "guarded"
    RECOVERY_ONLY = "recovery-only"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ChangeWindowEntry:
    """Per-wave admission view inside a change window."""

    wave_id: str
    escalation_plan: EscalationPlan
    status: ChangeWindowStatus
    allowed_promotions: tuple[str, ...]
    recovery_only_refs: tuple[str, ...]
    blocked_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "wave_id", _non_empty(self.wave_id, field_name="wave_id"))

    def to_dict(self) -> dict[str, object]:
        return {
            "wave_id": self.wave_id,
            "escalation_plan": self.escalation_plan.to_dict(),
            "status": self.status.value,
            "allowed_promotions": list(self.allowed_promotions),
            "recovery_only_refs": list(self.recovery_only_refs),
            "blocked_refs": list(self.blocked_refs),
        }


@dataclass(frozen=True)
class ChangeWindow:
    """Aggregated change window over one or more escalation plans."""

    window_id: str
    entries: tuple[ChangeWindowEntry, ...]
    window_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "window_id", _non_empty(self.window_id, field_name="window_id"))

    @property
    def status(self) -> ChangeWindowStatus:
        return ChangeWindowStatus(self.window_signal.status)

    @property
    def allowed_promotions(self) -> tuple[str, ...]:
        ordered: list[str] = []
        for entry in self.entries:
            for mission_ref in entry.allowed_promotions:
                if mission_ref not in ordered:
                    ordered.append(mission_ref)
        return tuple(ordered)

    @property
    def recovery_only_refs(self) -> tuple[str, ...]:
        ordered: list[str] = []
        for entry in self.entries:
            for mission_ref in entry.recovery_only_refs:
                if mission_ref not in ordered:
                    ordered.append(mission_ref)
        return tuple(ordered)

    @property
    def blocked_refs(self) -> tuple[str, ...]:
        ordered: list[str] = []
        for entry in self.entries:
            for mission_ref in entry.blocked_refs:
                if mission_ref not in ordered:
                    ordered.append(mission_ref)
        return tuple(ordered)

    def to_dict(self) -> dict[str, object]:
        return {
            "window_id": self.window_id,
            "entries": [entry.to_dict() for entry in self.entries],
            "window_signal": self.window_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "status": self.status.value,
            "allowed_promotions": list(self.allowed_promotions),
            "recovery_only_refs": list(self.recovery_only_refs),
            "blocked_refs": list(self.blocked_refs),
        }


def _entry_for_plan(plan: EscalationPlan) -> ChangeWindowEntry:
    blocked = set(plan.blocked_release_refs)
    recovery_only = {
        directive.mission_ref
        for directive in plan.directives
        if directive.path in {EscalationPath.RECOVERY_RESTART, EscalationPath.ROLLBACK_CONTAINMENT}
    }
    guarded = set(plan.governance_review_refs)
    admitted = {
        entry.mission_ref
        for entry in plan.incident_report.ledger.entries
        if entry.executed and entry.success
    }
    allowed_promotions = tuple(sorted(admitted - blocked - recovery_only - guarded))
    recovery_only_refs = tuple(sorted(recovery_only))
    blocked_refs = tuple(sorted(blocked | guarded))
    status = ChangeWindowStatus.OPEN
    if any(directive.path is EscalationPath.ROLLBACK_CONTAINMENT for directive in plan.directives):
        status = ChangeWindowStatus.BLOCKED
    elif recovery_only_refs:
        status = ChangeWindowStatus.RECOVERY_ONLY
    elif blocked_refs:
        status = ChangeWindowStatus.GUARDED
    return ChangeWindowEntry(
        wave_id=plan.wave_id,
        escalation_plan=plan,
        status=status,
        allowed_promotions=allowed_promotions,
        recovery_only_refs=recovery_only_refs,
        blocked_refs=blocked_refs,
    )


def open_change_window(
    plans: tuple[EscalationPlan, ...] | list[EscalationPlan],
    *,
    window_id: str = "change-window",
) -> ChangeWindow:
    """Open a coordinated change window over one or more escalation plans."""

    resolved_plans = tuple(plans)
    if not resolved_plans:
        raise ValueError("plans must not be empty")
    entries = tuple(_entry_for_plan(plan) for plan in resolved_plans)
    severity = "info"
    status = ChangeWindowStatus.OPEN.value
    if any(entry.status is ChangeWindowStatus.BLOCKED for entry in entries):
        severity = "critical"
        status = ChangeWindowStatus.BLOCKED.value
    elif any(entry.status is ChangeWindowStatus.RECOVERY_ONLY for entry in entries):
        severity = "warning"
        status = ChangeWindowStatus.RECOVERY_ONLY.value
    elif any(entry.status is ChangeWindowStatus.GUARDED for entry in entries):
        severity = "warning"
        status = ChangeWindowStatus.GUARDED.value
    window_signal = TelemetrySignal(
        signal_name="change-window",
        boundary=ModuleBoundaryName.ROLLOUT,
        correlation_id=window_id,
        severity=severity,
        status=status,
        metrics={
            "wave_count": float(len(entries)),
            "allowed_count": float(sum(len(entry.allowed_promotions) for entry in entries)),
            "recovery_only_count": float(sum(len(entry.recovery_only_refs) for entry in entries)),
            "blocked_count": float(sum(len(entry.blocked_refs) for entry in entries)),
        },
        labels={"window_id": window_id},
    )
    first_stage = resolved_plans[0].final_snapshot.runtime_stage
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=first_stage,
        signals=(window_signal, *(entry.escalation_plan.escalation_signal for entry in entries), *(signal for entry in entries for signal in entry.escalation_plan.final_snapshot.signals)),
        alerts=tuple(alert for entry in entries for alert in entry.escalation_plan.final_snapshot.alerts),
        audit_entries=tuple(record for entry in entries for record in entry.escalation_plan.final_snapshot.audit_entries),
        active_controls=tuple(
            dict.fromkeys(control for entry in entries for control in entry.escalation_plan.final_snapshot.active_controls)
        ),
    )
    return ChangeWindow(
        window_id=window_id,
        entries=entries,
        window_signal=window_signal,
        final_snapshot=final_snapshot,
    )
