"""Multi-run wave orchestration over mission profiles and integrated operations runs."""

from __future__ import annotations

from dataclasses import dataclass

from .mission_profiles import MissionProfile, mission_profile_for_name
from .module_boundaries import ModuleBoundaryName
from .operations_run import IntegratedOperationsRun, run_integrated_operations
from .orchestration import (
    DispatchAssignment,
    DispatchLane,
    DispatchPlan,
    OperationalPressure,
    OrchestrationState,
    OrchestrationStatus,
    WorkPriority,
    build_dispatch_plan,
    orchestration_state_for_runtime,
    work_unit_for_state,
)
from .runtime_dna import RuntimeDNA, RuntimeHooks, RuntimeIdentity, RuntimeStage, RuntimeThresholds
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _clamp01(value: float, *, field_name: str) -> float:
    normalized = float(value)
    if not 0.0 <= normalized <= 1.0:
        raise ValueError(f"{field_name} must be between 0.0 and 1.0")
    return normalized


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


@dataclass(frozen=True)
class WaveBudgetPolicy:
    """Shared budget and parallelism policy for an operations wave."""

    total_budget: float
    reserve_floor: float
    max_parallel: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "total_budget", _clamp01(self.total_budget, field_name="total_budget"))
        object.__setattr__(self, "reserve_floor", _clamp01(self.reserve_floor, field_name="reserve_floor"))
        if self.reserve_floor >= self.total_budget:
            raise ValueError("reserve_floor must stay below total_budget")
        if self.max_parallel is not None and self.max_parallel < 1:
            raise ValueError("max_parallel must be >= 1")

    @property
    def dispatch_budget(self) -> float:
        return self.total_budget - self.reserve_floor

    def to_dict(self) -> dict[str, object]:
        return {
            "total_budget": self.total_budget,
            "reserve_floor": self.reserve_floor,
            "dispatch_budget": self.dispatch_budget,
            "max_parallel": self.max_parallel,
        }


@dataclass(frozen=True)
class WaveMissionExecution:
    """Execution result for a single mission within a wave."""

    mission_profile: MissionProfile
    dispatch_assignment: DispatchAssignment
    operations_run: IntegratedOperationsRun | None = None

    @property
    def executed(self) -> bool:
        return self.operations_run is not None

    @property
    def success(self) -> bool:
        return self.operations_run.success if self.operations_run is not None else False

    def to_dict(self) -> dict[str, object]:
        return {
            "mission_profile": self.mission_profile.to_dict(),
            "dispatch_assignment": self.dispatch_assignment.to_dict(),
            "operations_run": None if self.operations_run is None else self.operations_run.to_dict(),
            "executed": self.executed,
            "success": self.success,
        }


@dataclass(frozen=True)
class OperationsWave:
    """Coordinated operations wave over multiple mission profiles."""

    wave_id: str
    runtime_dna: RuntimeDNA
    orchestration_state: OrchestrationState
    budget_policy: WaveBudgetPolicy
    dispatch_plan: DispatchPlan
    missions: tuple[MissionProfile, ...]
    executions: tuple[WaveMissionExecution, ...]
    wave_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "wave_id", _non_empty(self.wave_id, field_name="wave_id"))

    @property
    def admitted_mission_refs(self) -> tuple[str, ...]:
        return tuple(
            execution.mission_profile.mission_ref
            for execution in self.executions
            if execution.dispatch_assignment.lane is DispatchLane.ADMIT
        )

    @property
    def held_mission_refs(self) -> tuple[str, ...]:
        return tuple(
            execution.mission_profile.mission_ref
            for execution in self.executions
            if execution.dispatch_assignment.lane is DispatchLane.HOLD
        )

    @property
    def blocked_mission_refs(self) -> tuple[str, ...]:
        return tuple(
            execution.mission_profile.mission_ref
            for execution in self.executions
            if execution.dispatch_assignment.lane is DispatchLane.BLOCK
        )

    @property
    def deferred_mission_refs(self) -> tuple[str, ...]:
        return tuple(
            execution.mission_profile.mission_ref
            for execution in self.executions
            if execution.dispatch_assignment.lane is DispatchLane.DEFER
        )

    @property
    def success(self) -> bool:
        executed = tuple(execution for execution in self.executions if execution.executed)
        return bool(executed) and not self.blocked_mission_refs and all(execution.success for execution in executed)

    def to_dict(self) -> dict[str, object]:
        return {
            "wave_id": self.wave_id,
            "runtime_dna": self.runtime_dna.to_dict(),
            "orchestration_state": self.orchestration_state.to_dict(),
            "budget_policy": self.budget_policy.to_dict(),
            "dispatch_plan": self.dispatch_plan.to_dict(),
            "missions": [mission.to_dict() for mission in self.missions],
            "executions": [execution.to_dict() for execution in self.executions],
            "wave_signal": self.wave_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "admitted_mission_refs": list(self.admitted_mission_refs),
            "held_mission_refs": list(self.held_mission_refs),
            "blocked_mission_refs": list(self.blocked_mission_refs),
            "deferred_mission_refs": list(self.deferred_mission_refs),
            "success": self.success,
        }


def _resolve_missions(missions: tuple[MissionProfile | str, ...] | list[MissionProfile | str]) -> tuple[MissionProfile, ...]:
    resolved = tuple(
        mission if isinstance(mission, MissionProfile) else mission_profile_for_name(mission)
        for mission in missions
    )
    if not resolved:
        raise ValueError("missions must not be empty")
    stages = {mission.runtime_stage for mission in resolved}
    if len(stages) != 1:
        raise ValueError("all wave missions must share the same runtime_stage")
    return resolved


def _default_budget_policy(missions: tuple[MissionProfile, ...]) -> WaveBudgetPolicy:
    return WaveBudgetPolicy(
        total_budget=min(mission.policy.resource_budget for mission in missions),
        reserve_floor=max(mission.policy.recovery_reserve for mission in missions),
        max_parallel=min(len(missions), 2),
    )


def _pressure_for_wave(missions: tuple[MissionProfile, ...], budget_policy: WaveBudgetPolicy) -> OperationalPressure:
    mission_count = len(missions)
    highest_budget = max(mission.budget_share for mission in missions)
    return OperationalPressure(
        load_factor=min(0.18 + (mission_count * 0.11), 0.92),
        queue_pressure=min(0.16 + (mission_count * 0.13), 0.95),
        risk_pressure=min(max(mission.policy.recovery_reserve for mission in missions) + 0.08, 0.9),
        recovery_pressure=min(max(highest_budget, budget_policy.reserve_floor), 0.95),
    )


def _wave_runtime_dna(*, wave_id: str, stage: RuntimeStage, budget_policy: WaveBudgetPolicy) -> RuntimeDNA:
    return RuntimeDNA(
        identity=RuntimeIdentity(system="kki", profile="wave-runtime-dna", version="0.1.0", stage=stage),
        hooks=RuntimeHooks(),
        thresholds=RuntimeThresholds(
            resource_budget=budget_policy.total_budget,
            resource_share_factor=min(max(budget_policy.dispatch_budget, 0.1), 0.5),
            recovery_reserve=budget_policy.reserve_floor,
            approval_window=2,
            meta_update_interval=4,
        ),
        extension_contracts=("identity", "telemetry", "security", "shadow", "recovery", "rollout"),
        metadata={"wave_id": wave_id, "coordination": "multi-run"},
    )


def _wave_signal(
    *,
    wave_id: str,
    orchestration_state: OrchestrationState,
    dispatch_plan: DispatchPlan,
    executions: tuple[WaveMissionExecution, ...],
) -> TelemetrySignal:
    blocked_count = len([execution for execution in executions if execution.dispatch_assignment.lane is DispatchLane.BLOCK])
    held_count = len([execution for execution in executions if execution.dispatch_assignment.lane is DispatchLane.HOLD])
    deferred_count = len([execution for execution in executions if execution.dispatch_assignment.lane is DispatchLane.DEFER])
    executed_count = len([execution for execution in executions if execution.executed])
    severity = "info"
    status = "executed"
    if blocked_count:
        severity = "critical"
        status = "blocked"
    elif held_count or deferred_count:
        severity = "warning"
        status = "partial"
    return TelemetrySignal(
        signal_name="operations-wave",
        boundary=ModuleBoundaryName.ORCHESTRATION,
        correlation_id=wave_id,
        severity=severity,
        status=status,
        metrics={
            "mission_count": float(len(executions)),
            "admitted_count": float(len(dispatch_plan.admitted_unit_ids)),
            "held_count": float(held_count),
            "blocked_count": float(blocked_count),
            "deferred_count": float(deferred_count),
            "executed_count": float(executed_count),
            "consumed_budget": dispatch_plan.consumed_budget,
            "effective_budget": dispatch_plan.effective_budget,
        },
        labels={
            "triage_mode": dispatch_plan.triage_mode.value,
            "runtime_stage": orchestration_state.runtime_stage.value,
            "wave_status": status,
        },
    )


def run_operations_wave(
    missions: tuple[MissionProfile | str, ...] | list[MissionProfile | str],
    *,
    wave_id: str = "operations-wave",
    budget_policy: WaveBudgetPolicy | None = None,
) -> OperationsWave:
    """Run a coordinated wave of mission profiles through shared dispatch planning."""

    resolved_missions = _resolve_missions(missions)
    shared_budget = budget_policy or _default_budget_policy(resolved_missions)
    stage = resolved_missions[0].runtime_stage
    runtime_dna = _wave_runtime_dna(wave_id=wave_id, stage=stage, budget_policy=shared_budget)
    orchestration_state = orchestration_state_for_runtime(
        runtime_dna,
        mission_ref=wave_id,
        status=OrchestrationStatus.ACTIVE if len(resolved_missions) > 1 else OrchestrationStatus.STAGED,
        budget_available=shared_budget.total_budget,
        budget_reserved=shared_budget.reserve_floor,
        pressure=_pressure_for_wave(resolved_missions, shared_budget),
        labels={
            "wave_id": wave_id,
            "mission_count": len(resolved_missions),
            "missions": tuple(mission.mission_ref for mission in resolved_missions),
        },
    )
    work_units = tuple(
        work_unit_for_state(
            orchestration_state,
            title=mission.title,
            boundary=mission.target_boundary,
            correlation_id=f"{wave_id}-{mission.mission_ref}",
            priority=mission.work_priority,
            budget_share=mission.budget_share,
            recovery_weight=mission.policy.recovery_reserve,
            labels={
                "mission_ref": mission.mission_ref,
                "mission_scenario": mission.scenario.value,
                "wave_id": wave_id,
                **dict(mission.labels),
            },
        )
        for mission in resolved_missions
    )
    available_roles = tuple(
        dict.fromkeys(role for mission in resolved_missions for role in mission.available_roles)
    )
    dispatch_plan = build_dispatch_plan(
        orchestration_state,
        work_units,
        available_roles=available_roles,
        max_parallel=shared_budget.max_parallel,
    )
    missions_by_ref = {mission.mission_ref: mission for mission in resolved_missions}
    executions: list[WaveMissionExecution] = []
    for index, assignment in enumerate(dispatch_plan.assignments, start=1):
        mission = missions_by_ref[assignment.work_unit.labels["mission_ref"]]
        run = None
        if assignment.lane is DispatchLane.ADMIT:
            run = run_integrated_operations(
                mission=mission,
                correlation_id=f"{wave_id}-{index:02d}-{mission.mission_ref}",
            )
        executions.append(
            WaveMissionExecution(
                mission_profile=mission,
                dispatch_assignment=assignment,
                operations_run=run,
            )
        )
    wave_signal = _wave_signal(
        wave_id=wave_id,
        orchestration_state=orchestration_state,
        dispatch_plan=dispatch_plan,
        executions=tuple(executions),
    )
    aggregated_signals = [wave_signal]
    aggregated_alerts = []
    aggregated_audit_entries = []
    aggregated_controls: list[str] = []
    for execution in executions:
        if execution.operations_run is None:
            continue
        aggregated_signals.extend(execution.operations_run.final_snapshot.signals)
        aggregated_alerts.extend(execution.operations_run.final_snapshot.alerts)
        aggregated_audit_entries.extend(execution.operations_run.final_snapshot.audit_entries)
        aggregated_controls.extend(execution.operations_run.final_snapshot.active_controls)
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=stage,
        signals=tuple(aggregated_signals),
        alerts=tuple(aggregated_alerts),
        audit_entries=tuple(aggregated_audit_entries),
        active_controls=tuple(dict.fromkeys(aggregated_controls)),
    )
    return OperationsWave(
        wave_id=wave_id,
        runtime_dna=runtime_dna,
        orchestration_state=orchestration_state,
        budget_policy=shared_budget,
        dispatch_plan=dispatch_plan,
        missions=resolved_missions,
        executions=tuple(executions),
        wave_signal=wave_signal,
        final_snapshot=final_snapshot,
    )
