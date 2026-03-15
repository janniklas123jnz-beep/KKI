"""Multi-cycle convergence simulator over readiness, governance, and recovery loops."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .continuous_readiness import ContinuousReadinessCycle, ContinuousReadinessStatus, build_continuous_readiness_cycle
from .governance_agenda import GovernanceAgenda, build_governance_agenda
from .recovery_drills import RecoveryDrillStatus, RecoveryDrillSuite, build_recovery_drill_suite
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


class ConvergenceStatus(str, Enum):
    """High-level convergence state across simulated cycles."""

    RESIDUAL_DRIFT = "residual-drift"
    STABILIZING = "stabilizing"
    CONVERGED = "converged"


@dataclass(frozen=True)
class ConvergenceProjection:
    """Projected readiness state for one simulated follow-up cycle."""

    projection_id: str
    cycle_index: int
    status: ConvergenceStatus
    ready_case_ids: tuple[str, ...]
    attention_case_ids: tuple[str, ...]
    blocked_case_ids: tuple[str, ...]
    governance_case_ids: tuple[str, ...]
    recovery_case_ids: tuple[str, ...]
    residual_drift: float
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "projection_id", _non_empty(self.projection_id, field_name="projection_id"))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        object.__setattr__(self, "residual_drift", max(0.0, min(1.0, float(self.residual_drift))))
        if self.cycle_index < 1:
            raise ValueError("cycle_index must be positive")

    def to_dict(self) -> dict[str, object]:
        return {
            "projection_id": self.projection_id,
            "cycle_index": self.cycle_index,
            "status": self.status.value,
            "ready_case_ids": list(self.ready_case_ids),
            "attention_case_ids": list(self.attention_case_ids),
            "blocked_case_ids": list(self.blocked_case_ids),
            "governance_case_ids": list(self.governance_case_ids),
            "recovery_case_ids": list(self.recovery_case_ids),
            "residual_drift": self.residual_drift,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class ConvergenceSimulator:
    """Projects whether the current control layers converge into a stable state."""

    simulator_id: str
    readiness_cycle: ContinuousReadinessCycle
    governance_agenda: GovernanceAgenda
    recovery_drills: RecoveryDrillSuite
    projections: tuple[ConvergenceProjection, ...]
    simulator_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "simulator_id", _non_empty(self.simulator_id, field_name="simulator_id"))

    @property
    def converged_cycle_index(self) -> int | None:
        for projection in self.projections:
            if projection.status is ConvergenceStatus.CONVERGED:
                return projection.cycle_index
        return None

    @property
    def final_ready_case_ids(self) -> tuple[str, ...]:
        return self.projections[-1].ready_case_ids

    @property
    def residual_case_ids(self) -> tuple[str, ...]:
        final_projection = self.projections[-1]
        return final_projection.attention_case_ids + final_projection.blocked_case_ids

    def to_dict(self) -> dict[str, object]:
        return {
            "simulator_id": self.simulator_id,
            "readiness_cycle": self.readiness_cycle.to_dict(),
            "governance_agenda": self.governance_agenda.to_dict(),
            "recovery_drills": self.recovery_drills.to_dict(),
            "projections": [projection.to_dict() for projection in self.projections],
            "simulator_signal": self.simulator_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "converged_cycle_index": self.converged_cycle_index,
            "final_ready_case_ids": list(self.final_ready_case_ids),
            "residual_case_ids": list(self.residual_case_ids),
        }


def _status_by_case(readiness_cycle: ContinuousReadinessCycle) -> dict[str, ContinuousReadinessStatus]:
    return {iteration.case_id: iteration.status for iteration in readiness_cycle.iterations}


def _project_case_status(
    case_id: str,
    cycle_index: int,
    *,
    base_status: ContinuousReadinessStatus,
    governance_case_ids: set[str],
    held_case_ids: set[str],
    drill_status_by_case: dict[str, RecoveryDrillStatus],
) -> ContinuousReadinessStatus:
    if base_status is ContinuousReadinessStatus.READY:
        return ContinuousReadinessStatus.READY

    drill_status = drill_status_by_case.get(case_id)
    if drill_status is RecoveryDrillStatus.ACTIVE:
        if cycle_index == 1:
            return ContinuousReadinessStatus.BLOCKED
        if cycle_index == 2:
            return ContinuousReadinessStatus.ATTENTION
        return ContinuousReadinessStatus.READY
    if drill_status is RecoveryDrillStatus.SCHEDULED:
        if cycle_index <= 2:
            return ContinuousReadinessStatus.BLOCKED
        if cycle_index == 3:
            return ContinuousReadinessStatus.ATTENTION
        return ContinuousReadinessStatus.READY
    if drill_status is RecoveryDrillStatus.REENTRY_READY:
        return ContinuousReadinessStatus.ATTENTION if cycle_index == 1 else ContinuousReadinessStatus.READY

    if case_id in governance_case_ids:
        return ContinuousReadinessStatus.ATTENTION if cycle_index == 1 else ContinuousReadinessStatus.READY
    if case_id in held_case_ids:
        return ContinuousReadinessStatus.ATTENTION if cycle_index < 3 else ContinuousReadinessStatus.READY
    return base_status


def _residual_drift_for_statuses(statuses: tuple[ContinuousReadinessStatus, ...]) -> float:
    if not statuses:
        return 0.0
    weight = {
        ContinuousReadinessStatus.READY: 0.0,
        ContinuousReadinessStatus.ATTENTION: 0.25,
        ContinuousReadinessStatus.BLOCKED: 0.5,
    }
    return round(sum(weight[status] for status in statuses) / len(statuses), 3)


def _projection_status(
    ready_case_ids: tuple[str, ...],
    attention_case_ids: tuple[str, ...],
    blocked_case_ids: tuple[str, ...],
) -> ConvergenceStatus:
    del ready_case_ids
    if blocked_case_ids:
        return ConvergenceStatus.RESIDUAL_DRIFT
    if attention_case_ids:
        return ConvergenceStatus.STABILIZING
    return ConvergenceStatus.CONVERGED


def build_convergence_simulator(
    readiness_cycle: ContinuousReadinessCycle | None = None,
    governance_agenda: GovernanceAgenda | None = None,
    recovery_drills: RecoveryDrillSuite | None = None,
    *,
    simulator_id: str = "convergence-simulator",
    horizon: int = 3,
) -> ConvergenceSimulator:
    """Project multiple readiness cycles to expose stabilization and residual drift."""

    if horizon < 1:
        raise ValueError("horizon must be positive")

    resolved_cycle = build_continuous_readiness_cycle(cycle_id=f"{simulator_id}-cycle") if readiness_cycle is None else readiness_cycle
    resolved_agenda = build_governance_agenda(agenda_id=f"{simulator_id}-agenda") if governance_agenda is None else governance_agenda
    resolved_drills = build_recovery_drill_suite(suite_id=f"{simulator_id}-drills") if recovery_drills is None else recovery_drills

    base_status_by_case = _status_by_case(resolved_cycle)
    case_ids = tuple(base_status_by_case)
    governance_case_ids = set(item.case_id for item in resolved_agenda.items)
    held_case_ids = set(resolved_agenda.capacity_planner.held_case_ids)
    drill_status_by_case = {drill.case_id: drill.status for drill in resolved_drills.drills}
    recovery_case_ids = tuple(drill_status_by_case)

    projections: list[ConvergenceProjection] = []
    for cycle_index in range(1, horizon + 1):
        projected_status_by_case = {
            case_id: _project_case_status(
                case_id,
                cycle_index,
                base_status=base_status_by_case[case_id],
                governance_case_ids=governance_case_ids,
                held_case_ids=held_case_ids,
                drill_status_by_case=drill_status_by_case,
            )
            for case_id in case_ids
        }
        ready_case_ids = tuple(case_id for case_id in case_ids if projected_status_by_case[case_id] is ContinuousReadinessStatus.READY)
        attention_case_ids = tuple(case_id for case_id in case_ids if projected_status_by_case[case_id] is ContinuousReadinessStatus.ATTENTION)
        blocked_case_ids = tuple(case_id for case_id in case_ids if projected_status_by_case[case_id] is ContinuousReadinessStatus.BLOCKED)
        residual_drift = _residual_drift_for_statuses(tuple(projected_status_by_case[case_id] for case_id in case_ids))
        status = _projection_status(ready_case_ids, attention_case_ids, blocked_case_ids)
        projections.append(
            ConvergenceProjection(
                projection_id=f"{simulator_id}-cycle-{cycle_index}",
                cycle_index=cycle_index,
                status=status,
                ready_case_ids=ready_case_ids,
                attention_case_ids=attention_case_ids,
                blocked_case_ids=blocked_case_ids,
                governance_case_ids=tuple(case_id for case_id in case_ids if case_id in governance_case_ids),
                recovery_case_ids=tuple(case_id for case_id in case_ids if case_id in recovery_case_ids),
                residual_drift=residual_drift,
                summary=(
                    f"Cycle {cycle_index} projects {len(ready_case_ids)} ready, "
                    f"{len(attention_case_ids)} attention and {len(blocked_case_ids)} blocked cases."
                ),
            )
        )

    resolved_projections = tuple(projections)
    final_projection = resolved_projections[-1]
    severity = "info"
    if final_projection.status is ConvergenceStatus.RESIDUAL_DRIFT:
        severity = "critical"
    elif final_projection.status is ConvergenceStatus.STABILIZING:
        severity = "warning"

    simulator_signal = TelemetrySignal(
        signal_name="convergence-simulator",
        boundary=resolved_cycle.cycle_signal.boundary,
        correlation_id=simulator_id,
        severity=severity,
        status=final_projection.status.value,
        metrics={
            "projection_count": float(len(resolved_projections)),
            "initial_residual_drift": resolved_projections[0].residual_drift,
            "final_residual_drift": final_projection.residual_drift,
            "converged_cycle_index": float(next((p.cycle_index for p in resolved_projections if p.status is ConvergenceStatus.CONVERGED), 0)),
            "governance_case_count": float(len(governance_case_ids)),
            "recovery_case_count": float(len(recovery_case_ids)),
        },
        labels={"simulator_id": simulator_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_cycle.final_snapshot.runtime_stage,
        signals=(
            simulator_signal,
            resolved_cycle.cycle_signal,
            resolved_agenda.agenda_signal,
            resolved_drills.drill_signal,
            *resolved_cycle.final_snapshot.signals,
        ),
        alerts=resolved_cycle.final_snapshot.alerts,
        audit_entries=resolved_cycle.final_snapshot.audit_entries,
        active_controls=resolved_cycle.final_snapshot.active_controls,
    )
    return ConvergenceSimulator(
        simulator_id=simulator_id,
        readiness_cycle=resolved_cycle,
        governance_agenda=resolved_agenda,
        recovery_drills=resolved_drills,
        projections=resolved_projections,
        simulator_signal=simulator_signal,
        final_snapshot=final_snapshot,
    )
