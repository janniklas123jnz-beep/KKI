"""Ledger views over operations waves and integrated runs."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .module_boundaries import ModuleBoundaryName
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot
from .wave_orchestration import OperationsWave, WaveMissionExecution


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _frozen_mapping(data: Mapping[str, object] | None) -> Mapping[str, object]:
    return MappingProxyType(dict(data or {}))


@dataclass(frozen=True)
class RunLedgerEntry:
    """Normalized ledger entry for a single mission execution inside a wave."""

    ledger_id: str
    wave_id: str
    mission_ref: str
    correlation_id: str
    dispatch_lane: str
    executed: bool
    success: bool
    highest_severity: str
    governance_status: str
    rollout_status: str
    recovery_status: str
    alert_count: int
    active_controls: tuple[str, ...]
    labels: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "ledger_id", _non_empty(self.ledger_id, field_name="ledger_id"))
        object.__setattr__(self, "wave_id", _non_empty(self.wave_id, field_name="wave_id"))
        object.__setattr__(self, "mission_ref", _non_empty(self.mission_ref, field_name="mission_ref"))
        object.__setattr__(self, "correlation_id", _non_empty(self.correlation_id, field_name="correlation_id"))
        object.__setattr__(self, "dispatch_lane", _non_empty(self.dispatch_lane, field_name="dispatch_lane"))
        if self.highest_severity not in {"info", "warning", "critical"}:
            raise ValueError("highest_severity must be one of: info, warning, critical")
        object.__setattr__(self, "labels", _frozen_mapping(self.labels))

    def to_dict(self) -> dict[str, object]:
        return {
            "ledger_id": self.ledger_id,
            "wave_id": self.wave_id,
            "mission_ref": self.mission_ref,
            "correlation_id": self.correlation_id,
            "dispatch_lane": self.dispatch_lane,
            "executed": self.executed,
            "success": self.success,
            "highest_severity": self.highest_severity,
            "governance_status": self.governance_status,
            "rollout_status": self.rollout_status,
            "recovery_status": self.recovery_status,
            "alert_count": self.alert_count,
            "active_controls": list(self.active_controls),
            "labels": dict(self.labels),
        }


@dataclass(frozen=True)
class OperationsRunLedger:
    """Aggregated ledger view for all mission executions in an operations wave."""

    wave_id: str
    entries: tuple[RunLedgerEntry, ...]
    wave_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "wave_id", _non_empty(self.wave_id, field_name="wave_id"))

    @property
    def executed_mission_refs(self) -> tuple[str, ...]:
        return tuple(entry.mission_ref for entry in self.entries if entry.executed)

    @property
    def held_mission_refs(self) -> tuple[str, ...]:
        return tuple(entry.mission_ref for entry in self.entries if entry.dispatch_lane == "hold")

    @property
    def blocked_mission_refs(self) -> tuple[str, ...]:
        return tuple(entry.mission_ref for entry in self.entries if entry.dispatch_lane == "block")

    @property
    def status_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for entry in self.entries:
            counts[entry.dispatch_lane] = counts.get(entry.dispatch_lane, 0) + 1
        return counts

    def to_dict(self) -> dict[str, object]:
        return {
            "wave_id": self.wave_id,
            "entries": [entry.to_dict() for entry in self.entries],
            "wave_signal": self.wave_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "executed_mission_refs": list(self.executed_mission_refs),
            "held_mission_refs": list(self.held_mission_refs),
            "blocked_mission_refs": list(self.blocked_mission_refs),
            "status_counts": self.status_counts,
        }


def _ledger_entry_for_execution(wave_id: str, execution: WaveMissionExecution) -> RunLedgerEntry:
    mission = execution.mission_profile
    assignment = execution.dispatch_assignment
    run = execution.operations_run
    correlation_id = (
        run.work_unit.correlation_id if run is not None else assignment.work_unit.correlation_id
    )
    highest_severity = run.final_snapshot.highest_severity() if run is not None else "warning"
    governance_status = run.human_governance.governance_signal.status if run is not None else "not-executed"
    rollout_status = run.rollout_state.phase.value if run is not None else "not-executed"
    recovery_status = run.recovery_orchestration.recovery_signal.status if run is not None else "not-executed"
    alert_count = len(run.final_snapshot.alerts) if run is not None else 0
    active_controls = () if run is None else run.final_snapshot.active_controls
    return RunLedgerEntry(
        ledger_id=f"ledger-{wave_id}-{mission.mission_ref}",
        wave_id=wave_id,
        mission_ref=mission.mission_ref,
        correlation_id=correlation_id,
        dispatch_lane=assignment.lane.value,
        executed=execution.executed,
        success=execution.success,
        highest_severity=highest_severity,
        governance_status=governance_status,
        rollout_status=rollout_status,
        recovery_status=recovery_status,
        alert_count=alert_count,
        active_controls=active_controls,
        labels={
            "mission_scenario": mission.scenario.value,
            "runtime_stage": mission.runtime_stage.value,
            "wave_id": wave_id,
            **dict(mission.labels),
        },
    )


def ledger_for_wave(wave: OperationsWave) -> OperationsRunLedger:
    """Create the canonical ledger view for an operations wave."""

    entries = tuple(_ledger_entry_for_execution(wave.wave_id, execution) for execution in wave.executions)
    ledger_signal = TelemetrySignal(
        signal_name="run-ledger",
        boundary=ModuleBoundaryName.TELEMETRY,
        correlation_id=wave.wave_id,
        severity=wave.final_snapshot.highest_severity(),
        status="compiled",
        metrics={
            "entry_count": float(len(entries)),
            "executed_count": float(len([entry for entry in entries if entry.executed])),
            "held_count": float(len([entry for entry in entries if entry.dispatch_lane == "hold"])),
            "blocked_count": float(len([entry for entry in entries if entry.dispatch_lane == "block"])),
        },
        labels={
            "wave_id": wave.wave_id,
            "wave_status": wave.wave_signal.status,
            "triage_mode": wave.dispatch_plan.triage_mode.value,
        },
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=wave.runtime_dna.identity.stage,
        signals=(ledger_signal, wave.wave_signal, *wave.final_snapshot.signals),
        alerts=wave.final_snapshot.alerts,
        audit_entries=wave.final_snapshot.audit_entries,
        active_controls=wave.final_snapshot.active_controls,
    )
    return OperationsRunLedger(
        wave_id=wave.wave_id,
        entries=entries,
        wave_signal=ledger_signal,
        final_snapshot=final_snapshot,
    )
