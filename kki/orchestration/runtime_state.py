"""Operational orchestration state for the second build-phase block."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from kki.data_models import CoreState
from kki.module_boundaries import ModuleBoundaryName
from kki.runtime_dna import RuntimeDNA, RuntimeStage


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float, *, field_name: str) -> float:
    normalized = float(value)
    if not 0.0 <= normalized <= 1.0:
        raise ValueError(f"{field_name} must be between 0.0 and 1.0")
    return normalized


def _frozen_mapping(data: Mapping[str, object] | None) -> Mapping[str, object]:
    return MappingProxyType(dict(data or {}))


class OrchestrationStatus(str, Enum):
    """Canonical lifecycle states for the operational orchestration core."""

    BOOTSTRAPPING = "bootstrapping"
    STAGED = "staged"
    ACTIVE = "active"
    THROTTLED = "throttled"
    DEGRADED = "degraded"
    RECOVERY_HOLD = "recovery-hold"


class PressureLevel(str, Enum):
    """Derived pressure levels for orchestration health scoring."""

    NOMINAL = "nominal"
    ELEVATED = "elevated"
    HIGH = "high"
    CRITICAL = "critical"


class GateState(str, Enum):
    """Readiness state for an operational gate."""

    OPEN = "open"
    GUARDED = "guarded"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class OperationalPressure:
    """Aggregated pressure view for load, backlog, risks, and recovery drag."""

    load_factor: float
    queue_pressure: float
    risk_pressure: float
    recovery_pressure: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "load_factor", _clamp01(self.load_factor, field_name="load_factor"))
        object.__setattr__(self, "queue_pressure", _clamp01(self.queue_pressure, field_name="queue_pressure"))
        object.__setattr__(self, "risk_pressure", _clamp01(self.risk_pressure, field_name="risk_pressure"))
        object.__setattr__(
            self,
            "recovery_pressure",
            _clamp01(self.recovery_pressure, field_name="recovery_pressure"),
        )

    @property
    def score(self) -> float:
        return (
            (self.load_factor * 0.35)
            + (self.queue_pressure * 0.25)
            + (self.risk_pressure * 0.25)
            + (self.recovery_pressure * 0.15)
        )

    @property
    def level(self) -> PressureLevel:
        score = self.score
        if score < 0.35:
            return PressureLevel.NOMINAL
        if score < 0.6:
            return PressureLevel.ELEVATED
        if score < 0.8:
            return PressureLevel.HIGH
        return PressureLevel.CRITICAL

    def to_dict(self) -> dict[str, object]:
        return {
            "load_factor": self.load_factor,
            "queue_pressure": self.queue_pressure,
            "risk_pressure": self.risk_pressure,
            "recovery_pressure": self.recovery_pressure,
            "score": self.score,
            "level": self.level.value,
        }


@dataclass(frozen=True)
class GateReadiness:
    """Resolved gate readiness for dispatch, shadow, rollout, and recovery."""

    dispatch: GateState = GateState.OPEN
    shadow: GateState = GateState.OPEN
    rollout: GateState = GateState.GUARDED
    recovery: GateState = GateState.OPEN
    blockers: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        cleaned_blockers = tuple(blocker.strip() for blocker in self.blockers if blocker.strip())
        object.__setattr__(self, "blockers", cleaned_blockers)
        if GateState.BLOCKED in self.blocked_states() and not cleaned_blockers:
            raise ValueError("blocked gates require at least one blocker")

    def blocked_states(self) -> tuple[GateState, ...]:
        return tuple(
            gate_state
            for gate_state in (self.dispatch, self.shadow, self.rollout, self.recovery)
            if gate_state is GateState.BLOCKED
        )

    @property
    def blocked_gates(self) -> tuple[str, ...]:
        return tuple(
            gate_name
            for gate_name, gate_state in (
                ("dispatch", self.dispatch),
                ("shadow", self.shadow),
                ("rollout", self.rollout),
                ("recovery", self.recovery),
            )
            if gate_state is GateState.BLOCKED
        )

    @property
    def guarded_gates(self) -> tuple[str, ...]:
        return tuple(
            gate_name
            for gate_name, gate_state in (
                ("dispatch", self.dispatch),
                ("shadow", self.shadow),
                ("rollout", self.rollout),
                ("recovery", self.recovery),
            )
            if gate_state is GateState.GUARDED
        )

    @property
    def all_open(self) -> bool:
        return not self.blocked_gates and not self.guarded_gates

    def to_dict(self) -> dict[str, object]:
        return {
            "dispatch": self.dispatch.value,
            "shadow": self.shadow.value,
            "rollout": self.rollout.value,
            "recovery": self.recovery.value,
            "blocked_gates": list(self.blocked_gates),
            "guarded_gates": list(self.guarded_gates),
            "blockers": list(self.blockers),
        }


@dataclass(frozen=True)
class OrchestrationState:
    """Shared orchestration state for dispatch, gates, shadow, rollout, and recovery."""

    identity_slug: str
    runtime_stage: RuntimeStage
    status: OrchestrationStatus
    mission_ref: str | None
    budget_available: float
    budget_reserved: float
    recovery_budget_floor: float
    pressure: OperationalPressure
    gates: GateReadiness = field(default_factory=GateReadiness)
    open_risks: tuple[str, ...] = ()
    labels: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "identity_slug", _non_empty(self.identity_slug, field_name="identity_slug"))
        if self.mission_ref is not None:
            object.__setattr__(self, "mission_ref", _non_empty(self.mission_ref, field_name="mission_ref"))
        object.__setattr__(
            self,
            "budget_available",
            _clamp01(self.budget_available, field_name="budget_available"),
        )
        object.__setattr__(
            self,
            "budget_reserved",
            _clamp01(self.budget_reserved, field_name="budget_reserved"),
        )
        object.__setattr__(
            self,
            "recovery_budget_floor",
            _clamp01(self.recovery_budget_floor, field_name="recovery_budget_floor"),
        )
        if self.budget_reserved > self.budget_available:
            raise ValueError("budget_reserved must not exceed budget_available")
        if self.recovery_budget_floor > self.budget_available:
            raise ValueError("recovery_budget_floor must not exceed budget_available")
        cleaned_risks = tuple(risk.strip() for risk in self.open_risks if risk.strip())
        object.__setattr__(self, "open_risks", cleaned_risks)
        object.__setattr__(self, "labels", _frozen_mapping(self.labels))

    @property
    def dispatch_budget(self) -> float:
        return max(self.budget_available - self.budget_reserved, 0.0)

    @property
    def reserve_gap(self) -> float:
        return max(self.recovery_budget_floor - self.budget_reserved, 0.0)

    @property
    def recovery_ready(self) -> bool:
        return self.gates.recovery is not GateState.BLOCKED and self.reserve_gap == 0.0

    @property
    def gate_readiness(self) -> str:
        if self.gates.blocked_gates:
            return "blocked"
        if self.gates.guarded_gates:
            return "guarded"
        return "open"

    def health_markers(self) -> tuple[str, ...]:
        risk_marker = "risks-hot" if len(self.open_risks) >= 3 else ("risks-watch" if self.open_risks else "risks-clear")
        recovery_marker = "recovery-ready" if self.recovery_ready else "recovery-reserve-low"
        return (
            f"pressure:{self.pressure.level.value}",
            f"gates:{self.gate_readiness}",
            risk_marker,
            recovery_marker,
        )

    def health_status(self) -> str:
        if self.status is OrchestrationStatus.RECOVERY_HOLD or "gates:blocked" in self.health_markers():
            return "gated"
        if self.pressure.level is PressureLevel.CRITICAL:
            return "critical"
        if self.status in {OrchestrationStatus.DEGRADED, OrchestrationStatus.THROTTLED}:
            return "degraded"
        return "healthy"

    def to_core_state(self) -> CoreState:
        return CoreState(
            identity_slug=self.identity_slug,
            module_boundary=ModuleBoundaryName.ORCHESTRATION,
            runtime_stage=self.runtime_stage,
            status=self.status.value,
            budget=self.budget_available,
            labels={
                "mission_ref": self.mission_ref,
                "dispatch_budget": self.dispatch_budget,
                "pressure_level": self.pressure.level.value,
                "gate_readiness": self.gate_readiness,
                "health_status": self.health_status(),
                "health_markers": self.health_markers(),
                "open_risk_count": len(self.open_risks),
                "recovery_ready": self.recovery_ready,
                **dict(self.labels),
            },
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "identity_slug": self.identity_slug,
            "runtime_stage": self.runtime_stage.value,
            "status": self.status.value,
            "mission_ref": self.mission_ref,
            "budget_available": self.budget_available,
            "budget_reserved": self.budget_reserved,
            "dispatch_budget": self.dispatch_budget,
            "recovery_budget_floor": self.recovery_budget_floor,
            "reserve_gap": self.reserve_gap,
            "pressure": self.pressure.to_dict(),
            "gates": self.gates.to_dict(),
            "open_risks": list(self.open_risks),
            "health_status": self.health_status(),
            "health_markers": list(self.health_markers()),
            "labels": dict(self.labels),
        }


_ALLOWED_TRANSITIONS: dict[OrchestrationStatus, tuple[OrchestrationStatus, ...]] = {
    OrchestrationStatus.BOOTSTRAPPING: (
        OrchestrationStatus.STAGED,
        OrchestrationStatus.DEGRADED,
    ),
    OrchestrationStatus.STAGED: (
        OrchestrationStatus.ACTIVE,
        OrchestrationStatus.THROTTLED,
        OrchestrationStatus.DEGRADED,
    ),
    OrchestrationStatus.ACTIVE: (
        OrchestrationStatus.THROTTLED,
        OrchestrationStatus.DEGRADED,
        OrchestrationStatus.RECOVERY_HOLD,
    ),
    OrchestrationStatus.THROTTLED: (
        OrchestrationStatus.ACTIVE,
        OrchestrationStatus.DEGRADED,
        OrchestrationStatus.RECOVERY_HOLD,
    ),
    OrchestrationStatus.DEGRADED: (
        OrchestrationStatus.THROTTLED,
        OrchestrationStatus.RECOVERY_HOLD,
        OrchestrationStatus.ACTIVE,
    ),
    OrchestrationStatus.RECOVERY_HOLD: (
        OrchestrationStatus.STAGED,
        OrchestrationStatus.ACTIVE,
    ),
}


def orchestration_state_for_runtime(
    runtime_dna: RuntimeDNA,
    *,
    mission_ref: str | None,
    status: OrchestrationStatus = OrchestrationStatus.STAGED,
    budget_available: float | None = None,
    budget_reserved: float | None = None,
    pressure: OperationalPressure | None = None,
    gates: GateReadiness | None = None,
    open_risks: tuple[str, ...] = (),
    labels: Mapping[str, object] | None = None,
) -> OrchestrationState:
    """Build the canonical orchestration state from runtime DNA defaults."""

    available_budget = runtime_dna.thresholds.resource_budget if budget_available is None else float(budget_available)
    reserve_floor = runtime_dna.thresholds.recovery_reserve
    reserved_budget = reserve_floor if budget_reserved is None else float(budget_reserved)
    return OrchestrationState(
        identity_slug=runtime_dna.identity.slug,
        runtime_stage=runtime_dna.identity.stage,
        status=status,
        mission_ref=mission_ref,
        budget_available=available_budget,
        budget_reserved=reserved_budget,
        recovery_budget_floor=reserve_floor,
        pressure=pressure or OperationalPressure(0.22, 0.18, 0.14, 0.12),
        gates=gates or GateReadiness(),
        open_risks=open_risks,
        labels=labels,
    )


def advance_orchestration_state(
    state: OrchestrationState,
    *,
    status: OrchestrationStatus,
    mission_ref: str | None | object = ...,
    budget_available: float | None = None,
    budget_reserved: float | None = None,
    pressure: OperationalPressure | None = None,
    gates: GateReadiness | None = None,
    open_risks: tuple[str, ...] | None = None,
    labels: Mapping[str, object] | None = None,
) -> OrchestrationState:
    """Advance orchestration state through validated status transitions."""

    if status is not state.status and status not in _ALLOWED_TRANSITIONS[state.status]:
        raise ValueError(f"invalid orchestration transition: {state.status.value} -> {status.value}")
    next_mission_ref = state.mission_ref if mission_ref is ... else mission_ref
    next_labels = dict(state.labels)
    if labels:
        next_labels.update(labels)
    return OrchestrationState(
        identity_slug=state.identity_slug,
        runtime_stage=state.runtime_stage,
        status=status,
        mission_ref=next_mission_ref,
        budget_available=state.budget_available if budget_available is None else float(budget_available),
        budget_reserved=state.budget_reserved if budget_reserved is None else float(budget_reserved),
        recovery_budget_floor=state.recovery_budget_floor,
        pressure=pressure or state.pressure,
        gates=gates or state.gates,
        open_risks=state.open_risks if open_risks is None else open_risks,
        labels=next_labels,
    )
