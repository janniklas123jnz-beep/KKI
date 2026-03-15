"""Deterministic escalation routing over readiness cadence entries."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .module_boundaries import ModuleBoundaryName
from .readiness_cadence import (
    ReadinessCadence,
    ReadinessCadenceEntry,
    ReadinessCadenceStatus,
    ReadinessCadenceTrigger,
    build_readiness_cadence,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


class EscalationRoutePath(str, Enum):
    """Canonical target routes for readiness escalation handling."""

    GOVERNANCE_REVIEW = "governance-review"
    RECOVERY_RESTART = "recovery-restart"
    RECOVERY_CONTAINMENT = "recovery-containment"
    TELEMETRY_WATCH = "telemetry-watch"


@dataclass(frozen=True)
class EscalationRoute:
    """Deterministic route for one cadence entry."""

    route_id: str
    case_id: str
    cadence_entry_id: str
    path: EscalationRoutePath
    boundary: ModuleBoundaryName
    trigger: ReadinessCadenceTrigger
    due_cycle: int
    release_blocked: bool
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "route_id", _non_empty(self.route_id, field_name="route_id"))
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))
        object.__setattr__(self, "cadence_entry_id", _non_empty(self.cadence_entry_id, field_name="cadence_entry_id"))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.due_cycle < 1:
            raise ValueError("due_cycle must be positive")

    def to_dict(self) -> dict[str, object]:
        return {
            "route_id": self.route_id,
            "case_id": self.case_id,
            "cadence_entry_id": self.cadence_entry_id,
            "path": self.path.value,
            "boundary": self.boundary.value,
            "trigger": self.trigger.value,
            "due_cycle": self.due_cycle,
            "release_blocked": self.release_blocked,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class EscalationRouter:
    """Resolved routing table for readiness escalation handling."""

    router_id: str
    cadence: ReadinessCadence
    routes: tuple[EscalationRoute, ...]
    router_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "router_id", _non_empty(self.router_id, field_name="router_id"))

    @property
    def governance_case_ids(self) -> tuple[str, ...]:
        return tuple(route.case_id for route in self.routes if route.boundary is ModuleBoundaryName.GOVERNANCE)

    @property
    def recovery_case_ids(self) -> tuple[str, ...]:
        return tuple(route.case_id for route in self.routes if route.boundary is ModuleBoundaryName.RECOVERY)

    @property
    def telemetry_case_ids(self) -> tuple[str, ...]:
        return tuple(route.case_id for route in self.routes if route.boundary is ModuleBoundaryName.TELEMETRY)

    @property
    def blocked_case_ids(self) -> tuple[str, ...]:
        return tuple(route.case_id for route in self.routes if route.release_blocked)

    @property
    def focus_case_ids(self) -> tuple[str, ...]:
        return tuple(route.case_id for route in self.routes if route.due_cycle <= 2)

    def to_dict(self) -> dict[str, object]:
        return {
            "router_id": self.router_id,
            "cadence": self.cadence.to_dict(),
            "routes": [route.to_dict() for route in self.routes],
            "router_signal": self.router_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "governance_case_ids": list(self.governance_case_ids),
            "recovery_case_ids": list(self.recovery_case_ids),
            "telemetry_case_ids": list(self.telemetry_case_ids),
            "blocked_case_ids": list(self.blocked_case_ids),
            "focus_case_ids": list(self.focus_case_ids),
        }


def _route_for_entry(router_id: str, entry: ReadinessCadenceEntry) -> EscalationRoute:
    path = EscalationRoutePath.TELEMETRY_WATCH
    boundary = ModuleBoundaryName.TELEMETRY
    release_blocked = False
    summary = f"observe cadence for {entry.case_id} through telemetry watch."

    if entry.cadence_status is ReadinessCadenceStatus.ESCALATED:
        boundary = ModuleBoundaryName.RECOVERY
        release_blocked = True
        if entry.trigger is ReadinessCadenceTrigger.RECOVERY:
            path = EscalationRoutePath.RECOVERY_RESTART
            summary = f"restart recovery handling for {entry.case_id} in the current readiness cycle."
        else:
            path = EscalationRoutePath.RECOVERY_CONTAINMENT
            summary = f"contain and stabilize {entry.case_id} before it can re-enter readiness review."
    elif entry.cadence_status is ReadinessCadenceStatus.REVIEW_REQUIRED:
        if entry.trigger is ReadinessCadenceTrigger.RECOVERY:
            boundary = ModuleBoundaryName.RECOVERY
            path = EscalationRoutePath.RECOVERY_RESTART
            summary = f"route {entry.case_id} into recovery follow-up before the next readiness checkpoint."
        else:
            boundary = ModuleBoundaryName.GOVERNANCE
            path = EscalationRoutePath.GOVERNANCE_REVIEW
            summary = f"route {entry.case_id} into governance review for deterministic approval handling."

    return EscalationRoute(
        route_id=f"{router_id}-{entry.case_id}",
        case_id=entry.case_id,
        cadence_entry_id=entry.cadence_entry_id,
        path=path,
        boundary=boundary,
        trigger=entry.trigger,
        due_cycle=entry.due_cycle,
        release_blocked=release_blocked,
        summary=summary,
    )


def build_escalation_router(
    cadence: ReadinessCadence | None = None,
    *,
    router_id: str = "escalation-router",
) -> EscalationRouter:
    """Build deterministic governance, recovery, and telemetry routes from readiness cadence."""

    resolved_cadence = build_readiness_cadence(cadence_id=f"{router_id}-cadence") if cadence is None else cadence
    routes = tuple(_route_for_entry(router_id, entry) for entry in resolved_cadence.entries)
    if not routes:
        raise ValueError("escalation router requires at least one route")

    severity = "info"
    status = "telemetry-watch"
    if any(route.release_blocked for route in routes):
        severity = "critical"
        status = "critical-response"
    elif any(route.boundary is ModuleBoundaryName.GOVERNANCE for route in routes):
        severity = "warning"
        status = "response-required"

    router_signal = TelemetrySignal(
        signal_name="escalation-router",
        boundary=ModuleBoundaryName.GOVERNANCE,
        correlation_id=router_id,
        severity=severity,
        status=status,
        metrics={
            "route_count": float(len(routes)),
            "governance_count": float(len([route for route in routes if route.boundary is ModuleBoundaryName.GOVERNANCE])),
            "recovery_count": float(len([route for route in routes if route.boundary is ModuleBoundaryName.RECOVERY])),
            "telemetry_count": float(len([route for route in routes if route.boundary is ModuleBoundaryName.TELEMETRY])),
            "blocked_count": float(len([route for route in routes if route.release_blocked])),
            "focus_count": float(len([route for route in routes if route.due_cycle <= 2])),
        },
        labels={"router_id": router_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_cadence.final_snapshot.runtime_stage,
        signals=(router_signal, resolved_cadence.cadence_signal, *resolved_cadence.final_snapshot.signals),
        alerts=resolved_cadence.final_snapshot.alerts,
        audit_entries=resolved_cadence.final_snapshot.audit_entries,
        active_controls=resolved_cadence.final_snapshot.active_controls,
    )
    return EscalationRouter(
        router_id=router_id,
        cadence=resolved_cadence,
        routes=routes,
        router_signal=router_signal,
        final_snapshot=final_snapshot,
    )
