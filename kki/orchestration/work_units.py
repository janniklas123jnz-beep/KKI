"""Canonical work units, claims, and handoffs for operational orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from kki.module_boundaries import ModuleBoundaryName, module_boundary
from kki.orchestration.runtime_state import OrchestrationState
from kki.security.authorization import RoleName


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


class WorkPriority(str, Enum):
    """Scheduling priority for a canonical work unit."""

    BACKGROUND = "background"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class WorkStatus(str, Enum):
    """Lifecycle states for an operational work unit."""

    PLANNED = "planned"
    CLAIMED = "claimed"
    IN_PROGRESS = "in-progress"
    HANDED_OFF = "handed-off"
    BLOCKED = "blocked"
    COMPLETE = "complete"


class ClaimStatus(str, Enum):
    """Claim lifecycle for leased ownership of a work unit."""

    ACTIVE = "active"
    RELEASED = "released"
    EXPIRED = "expired"
    TRANSFERRED = "transferred"


class HandoffMode(str, Enum):
    """Operational handoff path between orchestration boundaries."""

    DIRECT = "direct"
    SHADOW = "shadow"
    RECOVERY = "recovery"


@dataclass(frozen=True)
class WorkCostProfile:
    """Cost surface used later by dispatch, throttling, and recovery planning."""

    execution_load: float
    coordination_load: float
    recovery_weight: float
    budget_share: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "execution_load", _clamp01(self.execution_load, field_name="execution_load"))
        object.__setattr__(
            self,
            "coordination_load",
            _clamp01(self.coordination_load, field_name="coordination_load"),
        )
        object.__setattr__(
            self,
            "recovery_weight",
            _clamp01(self.recovery_weight, field_name="recovery_weight"),
        )
        object.__setattr__(self, "budget_share", _clamp01(self.budget_share, field_name="budget_share"))

    @property
    def composite_load(self) -> float:
        return (
            (self.execution_load * 0.45)
            + (self.coordination_load * 0.25)
            + (self.recovery_weight * 0.30)
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "execution_load": self.execution_load,
            "coordination_load": self.coordination_load,
            "recovery_weight": self.recovery_weight,
            "budget_share": self.budget_share,
            "composite_load": self.composite_load,
        }


@dataclass(frozen=True)
class WorkUnit:
    """Shared unit of operational work for planning, dispatch, audit, and recovery."""

    unit_id: str
    title: str
    mission_ref: str
    correlation_id: str
    boundary: ModuleBoundaryName
    priority: WorkPriority
    status: WorkStatus
    cost_profile: WorkCostProfile
    required_capabilities: tuple[str, ...] = ()
    required_role: RoleName | None = None
    lease_window: int = 2
    max_retries: int = 1
    attempt: int = 0
    handoff_ref: str | None = None
    labels: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "unit_id", _non_empty(self.unit_id, field_name="unit_id"))
        object.__setattr__(self, "title", _non_empty(self.title, field_name="title"))
        object.__setattr__(self, "mission_ref", _non_empty(self.mission_ref, field_name="mission_ref"))
        object.__setattr__(self, "correlation_id", _non_empty(self.correlation_id, field_name="correlation_id"))
        module_boundary(self.boundary)
        if self.lease_window < 1:
            raise ValueError("lease_window must be >= 1")
        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        if self.attempt < 0:
            raise ValueError("attempt must be >= 0")
        if self.attempt > self.max_retries:
            raise ValueError("attempt must not exceed max_retries")
        if self.handoff_ref is not None:
            object.__setattr__(self, "handoff_ref", _non_empty(self.handoff_ref, field_name="handoff_ref"))
        cleaned_capabilities = tuple(cap.strip() for cap in self.required_capabilities if cap.strip())
        object.__setattr__(self, "required_capabilities", cleaned_capabilities)
        object.__setattr__(self, "labels", _frozen_mapping(self.labels))

    @property
    def ready_for_claim(self) -> bool:
        return self.status in {WorkStatus.PLANNED, WorkStatus.HANDED_OFF} and self.attempt <= self.max_retries

    @property
    def recovery_sensitive(self) -> bool:
        return self.priority is WorkPriority.CRITICAL or self.cost_profile.recovery_weight >= 0.5

    def to_dict(self) -> dict[str, object]:
        return {
            "unit_id": self.unit_id,
            "title": self.title,
            "mission_ref": self.mission_ref,
            "correlation_id": self.correlation_id,
            "boundary": self.boundary.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "cost_profile": self.cost_profile.to_dict(),
            "required_capabilities": list(self.required_capabilities),
            "required_role": self.required_role.value if self.required_role else None,
            "lease_window": self.lease_window,
            "max_retries": self.max_retries,
            "attempt": self.attempt,
            "handoff_ref": self.handoff_ref,
            "ready_for_claim": self.ready_for_claim,
            "recovery_sensitive": self.recovery_sensitive,
            "labels": dict(self.labels),
        }


@dataclass(frozen=True)
class WorkClaim:
    """Leased claim on a work unit for bounded execution ownership."""

    claim_id: str
    work_unit_id: str
    correlation_id: str
    boundary: ModuleBoundaryName
    owner_ref: str
    lease_window: int
    status: ClaimStatus = ClaimStatus.ACTIVE
    role_scope: RoleName | None = None
    handoff_ref: str | None = None
    labels: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "claim_id", _non_empty(self.claim_id, field_name="claim_id"))
        object.__setattr__(self, "work_unit_id", _non_empty(self.work_unit_id, field_name="work_unit_id"))
        object.__setattr__(self, "correlation_id", _non_empty(self.correlation_id, field_name="correlation_id"))
        object.__setattr__(self, "owner_ref", _non_empty(self.owner_ref, field_name="owner_ref"))
        module_boundary(self.boundary)
        if self.lease_window < 1:
            raise ValueError("lease_window must be >= 1")
        if self.handoff_ref is not None:
            object.__setattr__(self, "handoff_ref", _non_empty(self.handoff_ref, field_name="handoff_ref"))
        object.__setattr__(self, "labels", _frozen_mapping(self.labels))

    def to_dict(self) -> dict[str, object]:
        return {
            "claim_id": self.claim_id,
            "work_unit_id": self.work_unit_id,
            "correlation_id": self.correlation_id,
            "boundary": self.boundary.value,
            "owner_ref": self.owner_ref,
            "lease_window": self.lease_window,
            "status": self.status.value,
            "role_scope": self.role_scope.value if self.role_scope else None,
            "handoff_ref": self.handoff_ref,
            "labels": dict(self.labels),
        }


@dataclass(frozen=True)
class WorkHandoff:
    """Handoff contract for retry, replay, and cross-boundary continuation."""

    handoff_id: str
    work_unit_id: str
    correlation_id: str
    source_boundary: ModuleBoundaryName
    target_boundary: ModuleBoundaryName
    mode: HandoffMode
    reason: str
    retry_budget: int
    transfer_required: bool = True
    causation_id: str | None = None
    labels: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "handoff_id", _non_empty(self.handoff_id, field_name="handoff_id"))
        object.__setattr__(self, "work_unit_id", _non_empty(self.work_unit_id, field_name="work_unit_id"))
        object.__setattr__(self, "correlation_id", _non_empty(self.correlation_id, field_name="correlation_id"))
        object.__setattr__(self, "reason", _non_empty(self.reason, field_name="reason"))
        module_boundary(self.source_boundary)
        module_boundary(self.target_boundary)
        if self.source_boundary == self.target_boundary:
            raise ValueError("handoff must move work across boundaries")
        if self.retry_budget < 0:
            raise ValueError("retry_budget must be >= 0")
        if self.causation_id is not None:
            object.__setattr__(self, "causation_id", _non_empty(self.causation_id, field_name="causation_id"))
        object.__setattr__(self, "labels", _frozen_mapping(self.labels))

    def to_dict(self) -> dict[str, object]:
        return {
            "handoff_id": self.handoff_id,
            "work_unit_id": self.work_unit_id,
            "correlation_id": self.correlation_id,
            "source_boundary": self.source_boundary.value,
            "target_boundary": self.target_boundary.value,
            "mode": self.mode.value,
            "reason": self.reason,
            "retry_budget": self.retry_budget,
            "transfer_required": self.transfer_required,
            "causation_id": self.causation_id,
            "labels": dict(self.labels),
        }


_ALLOWED_WORK_TRANSITIONS: dict[WorkStatus, tuple[WorkStatus, ...]] = {
    WorkStatus.PLANNED: (WorkStatus.CLAIMED, WorkStatus.BLOCKED, WorkStatus.HANDED_OFF),
    WorkStatus.CLAIMED: (WorkStatus.IN_PROGRESS, WorkStatus.BLOCKED, WorkStatus.HANDED_OFF),
    WorkStatus.IN_PROGRESS: (WorkStatus.HANDED_OFF, WorkStatus.BLOCKED, WorkStatus.COMPLETE),
    WorkStatus.HANDED_OFF: (WorkStatus.CLAIMED, WorkStatus.BLOCKED, WorkStatus.COMPLETE),
    WorkStatus.BLOCKED: (WorkStatus.PLANNED, WorkStatus.HANDED_OFF, WorkStatus.COMPLETE),
    WorkStatus.COMPLETE: (),
}


def work_unit_for_state(
    state: OrchestrationState,
    *,
    title: str,
    boundary: ModuleBoundaryName | str,
    correlation_id: str,
    priority: WorkPriority = WorkPriority.NORMAL,
    execution_load: float | None = None,
    coordination_load: float | None = None,
    recovery_weight: float | None = None,
    budget_share: float | None = None,
    required_capabilities: tuple[str, ...] = (),
    required_role: RoleName | None = None,
    lease_window: int = 2,
    max_retries: int = 1,
    labels: Mapping[str, object] | None = None,
) -> WorkUnit:
    """Build a canonical work unit from orchestration state defaults."""

    target_boundary = boundary if isinstance(boundary, ModuleBoundaryName) else ModuleBoundaryName(boundary)
    mission_ref = state.mission_ref or "unassigned-mission"
    unit_id = f"wu-{mission_ref}-{target_boundary.value}-{correlation_id}"
    return WorkUnit(
        unit_id=unit_id,
        title=title,
        mission_ref=mission_ref,
        correlation_id=correlation_id,
        boundary=target_boundary,
        priority=priority,
        status=WorkStatus.PLANNED,
        cost_profile=WorkCostProfile(
            execution_load=state.pressure.load_factor if execution_load is None else execution_load,
            coordination_load=state.pressure.queue_pressure if coordination_load is None else coordination_load,
            recovery_weight=state.pressure.recovery_pressure if recovery_weight is None else recovery_weight,
            budget_share=min(state.dispatch_budget, 1.0) if budget_share is None else budget_share,
        ),
        required_capabilities=required_capabilities,
        required_role=required_role,
        lease_window=lease_window,
        max_retries=max_retries,
        labels={
            "orchestration_status": state.status.value,
            "pressure_level": state.pressure.level.value,
            "recovery_ready": state.recovery_ready,
            **dict(labels or {}),
        },
    )


def advance_work_unit(
    work_unit: WorkUnit,
    *,
    status: WorkStatus,
    attempt: int | None = None,
    handoff_ref: str | None | object = ...,
    labels: Mapping[str, object] | None = None,
) -> WorkUnit:
    """Advance a work unit through validated lifecycle transitions."""

    if status is not work_unit.status and status not in _ALLOWED_WORK_TRANSITIONS[work_unit.status]:
        raise ValueError(f"invalid work unit transition: {work_unit.status.value} -> {status.value}")
    next_labels = dict(work_unit.labels)
    if labels:
        next_labels.update(labels)
    next_handoff_ref = work_unit.handoff_ref if handoff_ref is ... else handoff_ref
    next_attempt = work_unit.attempt if attempt is None else attempt
    return WorkUnit(
        unit_id=work_unit.unit_id,
        title=work_unit.title,
        mission_ref=work_unit.mission_ref,
        correlation_id=work_unit.correlation_id,
        boundary=work_unit.boundary,
        priority=work_unit.priority,
        status=status,
        cost_profile=work_unit.cost_profile,
        required_capabilities=work_unit.required_capabilities,
        required_role=work_unit.required_role,
        lease_window=work_unit.lease_window,
        max_retries=work_unit.max_retries,
        attempt=next_attempt,
        handoff_ref=next_handoff_ref,
        labels=next_labels,
    )


def claim_for_work_unit(
    work_unit: WorkUnit,
    *,
    owner_ref: str,
    boundary: ModuleBoundaryName | str | None = None,
    role_scope: RoleName | None = None,
    lease_window: int | None = None,
    handoff: WorkHandoff | None = None,
    labels: Mapping[str, object] | None = None,
) -> WorkClaim:
    """Create the bounded ownership claim for a schedulable work unit."""

    if not work_unit.ready_for_claim:
        raise ValueError("work unit is not ready for claim")
    claim_boundary = work_unit.boundary if boundary is None else (
        boundary if isinstance(boundary, ModuleBoundaryName) else ModuleBoundaryName(boundary)
    )
    if handoff is not None:
        if handoff.work_unit_id != work_unit.unit_id:
            raise ValueError("handoff must reference the same work unit")
        if handoff.target_boundary != claim_boundary:
            raise ValueError("claim boundary must match handoff target boundary")
    return WorkClaim(
        claim_id=f"claim-{work_unit.unit_id}-{owner_ref}",
        work_unit_id=work_unit.unit_id,
        correlation_id=work_unit.correlation_id,
        boundary=claim_boundary,
        owner_ref=owner_ref,
        lease_window=work_unit.lease_window if lease_window is None else lease_window,
        role_scope=role_scope or work_unit.required_role,
        handoff_ref=handoff.handoff_id if handoff else work_unit.handoff_ref,
        labels=labels,
    )


def handoff_for_work_unit(
    work_unit: WorkUnit,
    *,
    target_boundary: ModuleBoundaryName | str,
    reason: str,
    mode: HandoffMode = HandoffMode.DIRECT,
    retry_budget: int | None = None,
    transfer_required: bool = True,
    causation_id: str | None = None,
    labels: Mapping[str, object] | None = None,
) -> WorkHandoff:
    """Create the canonical handoff contract for a work unit."""

    target = target_boundary if isinstance(target_boundary, ModuleBoundaryName) else ModuleBoundaryName(target_boundary)
    retries = work_unit.max_retries if retry_budget is None else retry_budget
    return WorkHandoff(
        handoff_id=f"handoff-{work_unit.unit_id}-{target.value}",
        work_unit_id=work_unit.unit_id,
        correlation_id=work_unit.correlation_id,
        source_boundary=work_unit.boundary,
        target_boundary=target,
        mode=mode,
        reason=reason,
        retry_budget=retries,
        transfer_required=transfer_required,
        causation_id=causation_id,
        labels=labels,
    )
