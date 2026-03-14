"""Deterministic dispatch planning for operational work units."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from kki.orchestration.runtime_state import GateState, OrchestrationState, OrchestrationStatus, PressureLevel
from kki.orchestration.work_units import WorkPriority, WorkUnit
from kki.security.authorization import RoleName


class DispatchTriageMode(str, Enum):
    """Operational triage mode chosen for a dispatch planning cycle."""

    BALANCED = "balanced"
    BACKLOG = "backlog"
    RESERVE_PROTECTED = "reserve-protected"
    RECOVERY_PRIORITY = "recovery-priority"


class DispatchLane(str, Enum):
    """Planning lane for a work unit in the dispatch result."""

    ADMIT = "admit"
    DEFER = "defer"
    HOLD = "hold"
    BLOCK = "block"


@dataclass(frozen=True)
class DispatchAssignment:
    """Resolved dispatch decision for a single work unit."""

    work_unit: WorkUnit
    lane: DispatchLane
    priority_score: float
    rationale: str
    reserved_budget: float

    def to_dict(self) -> dict[str, object]:
        return {
            "work_unit": self.work_unit.to_dict(),
            "lane": self.lane.value,
            "priority_score": self.priority_score,
            "rationale": self.rationale,
            "reserved_budget": self.reserved_budget,
        }


@dataclass(frozen=True)
class DispatchPlan:
    """Deterministic dispatch plan over a batch of work units."""

    triage_mode: DispatchTriageMode
    dispatch_budget: float
    effective_budget: float
    consumed_budget: float
    reserve_gap: float
    max_parallel: int | None
    assignments: tuple[DispatchAssignment, ...]

    @property
    def admitted_unit_ids(self) -> tuple[str, ...]:
        return tuple(
            assignment.work_unit.unit_id for assignment in self.assignments if assignment.lane is DispatchLane.ADMIT
        )

    @property
    def held_unit_ids(self) -> tuple[str, ...]:
        return tuple(
            assignment.work_unit.unit_id for assignment in self.assignments if assignment.lane is DispatchLane.HOLD
        )

    @property
    def blocked_unit_ids(self) -> tuple[str, ...]:
        return tuple(
            assignment.work_unit.unit_id for assignment in self.assignments if assignment.lane is DispatchLane.BLOCK
        )

    @property
    def deferred_unit_ids(self) -> tuple[str, ...]:
        return tuple(
            assignment.work_unit.unit_id for assignment in self.assignments if assignment.lane is DispatchLane.DEFER
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "triage_mode": self.triage_mode.value,
            "dispatch_budget": self.dispatch_budget,
            "effective_budget": self.effective_budget,
            "consumed_budget": self.consumed_budget,
            "reserve_gap": self.reserve_gap,
            "max_parallel": self.max_parallel,
            "admitted_unit_ids": list(self.admitted_unit_ids),
            "held_unit_ids": list(self.held_unit_ids),
            "blocked_unit_ids": list(self.blocked_unit_ids),
            "deferred_unit_ids": list(self.deferred_unit_ids),
            "assignments": [assignment.to_dict() for assignment in self.assignments],
        }


_PRIORITY_WEIGHT = {
    WorkPriority.BACKGROUND: 0.2,
    WorkPriority.NORMAL: 0.45,
    WorkPriority.HIGH: 0.7,
    WorkPriority.CRITICAL: 1.0,
}


def _triage_mode_for_state(state: OrchestrationState, work_units: tuple[WorkUnit, ...]) -> DispatchTriageMode:
    if state.status is OrchestrationStatus.RECOVERY_HOLD or any(unit.recovery_sensitive for unit in work_units):
        if state.pressure.recovery_pressure >= 0.45 or not state.recovery_ready:
            return DispatchTriageMode.RECOVERY_PRIORITY
    if state.reserve_gap > 0.0 or state.pressure.level in {PressureLevel.HIGH, PressureLevel.CRITICAL}:
        return DispatchTriageMode.RESERVE_PROTECTED
    if state.pressure.queue_pressure >= 0.55 or len(work_units) >= 4:
        return DispatchTriageMode.BACKLOG
    return DispatchTriageMode.BALANCED


def dispatch_priority_score(work_unit: WorkUnit, state: OrchestrationState, *, triage_mode: DispatchTriageMode) -> float:
    """Compute a deterministic priority score for dispatch ordering."""

    score = _PRIORITY_WEIGHT[work_unit.priority] * 100.0
    score += work_unit.cost_profile.composite_load * 20.0
    score += max(0.0, 1.0 - work_unit.cost_profile.budget_share) * 10.0
    score += max(0, work_unit.max_retries - work_unit.attempt) * 2.0
    if work_unit.recovery_sensitive:
        score += 12.0
    if triage_mode is DispatchTriageMode.RECOVERY_PRIORITY and work_unit.recovery_sensitive:
        score += 18.0
    elif triage_mode is DispatchTriageMode.BACKLOG:
        score += state.pressure.queue_pressure * 8.0
    elif triage_mode is DispatchTriageMode.RESERVE_PROTECTED:
        score -= work_unit.cost_profile.budget_share * 15.0
    if work_unit.required_role is not None:
        score += 1.0
    return round(score, 3)


def build_dispatch_plan(
    state: OrchestrationState,
    work_units: tuple[WorkUnit, ...] | list[WorkUnit],
    *,
    available_roles: tuple[RoleName | str, ...] = (),
    max_parallel: int | None = None,
    allow_guarded_dispatch: bool = False,
) -> DispatchPlan:
    """Build the canonical dispatch plan with deterministic triage and reserve protection."""

    units = tuple(work_units)
    triage_mode = _triage_mode_for_state(state, units)
    dispatch_budget = state.dispatch_budget
    effective_budget = max(dispatch_budget - state.reserve_gap, 0.0)
    normalized_roles = {
        role if isinstance(role, RoleName) else RoleName(role)
        for role in available_roles
    }
    scored_units = sorted(
        units,
        key=lambda unit: (
            -dispatch_priority_score(unit, state, triage_mode=triage_mode),
            unit.cost_profile.budget_share,
            unit.unit_id,
        ),
    )

    assignments: list[DispatchAssignment] = []
    admitted = 0
    consumed_budget = 0.0

    for unit in scored_units:
        score = dispatch_priority_score(unit, state, triage_mode=triage_mode)
        lane = DispatchLane.ADMIT
        rationale = "work unit admitted for execution"

        if state.gates.dispatch is GateState.BLOCKED:
            lane = DispatchLane.BLOCK
            rationale = "dispatch gate is blocked"
        elif not unit.ready_for_claim:
            lane = DispatchLane.DEFER
            rationale = "work unit is not ready for claim"
        elif unit.required_role is not None and normalized_roles and unit.required_role not in normalized_roles:
            lane = DispatchLane.DEFER
            rationale = "required execution role is unavailable"
        elif max_parallel is not None and admitted >= max_parallel:
            lane = DispatchLane.HOLD
            rationale = "parallel dispatch limit reached"
        elif state.gates.dispatch is GateState.GUARDED and not allow_guarded_dispatch:
            if unit.priority in {WorkPriority.BACKGROUND, WorkPriority.NORMAL}:
                lane = DispatchLane.HOLD
                rationale = "guarded dispatch reserves capacity for higher-priority work"
        if lane is DispatchLane.ADMIT and triage_mode is DispatchTriageMode.RECOVERY_PRIORITY:
            if unit.priority in {WorkPriority.BACKGROUND, WorkPriority.NORMAL} and not unit.recovery_sensitive:
                lane = DispatchLane.HOLD
                rationale = "recovery-priority triage holds non-critical work"
        if lane is DispatchLane.ADMIT and triage_mode is DispatchTriageMode.RESERVE_PROTECTED:
            if unit.cost_profile.budget_share > effective_budget - consumed_budget:
                lane = DispatchLane.HOLD
                rationale = "reserve-protected triage keeps recovery and budget headroom intact"
        if lane is DispatchLane.ADMIT and unit.cost_profile.budget_share > effective_budget - consumed_budget:
            lane = DispatchLane.HOLD
            rationale = "dispatch budget exhausted for this planning cycle"

        reserved_budget = unit.cost_profile.budget_share if lane is DispatchLane.ADMIT else 0.0
        assignments.append(
            DispatchAssignment(
                work_unit=unit,
                lane=lane,
                priority_score=score,
                rationale=rationale,
                reserved_budget=reserved_budget,
            )
        )
        if lane is DispatchLane.ADMIT:
            admitted += 1
            consumed_budget += unit.cost_profile.budget_share

    return DispatchPlan(
        triage_mode=triage_mode,
        dispatch_budget=dispatch_budget,
        effective_budget=effective_budget,
        consumed_budget=round(consumed_budget, 6),
        reserve_gap=state.reserve_gap,
        max_parallel=max_parallel,
        assignments=tuple(assignments),
    )
