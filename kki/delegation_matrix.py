"""Delegation matrix routing cabinet orders across Leitstern execution paths."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .execution_cabinet import (
    CabinetExecutionMode,
    CabinetOrder,
    CabinetRole,
    CabinetStatus,
    ExecutionCabinet,
    build_execution_cabinet,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class DelegationLane(str, Enum):
    """Primary delegation lane for one cabinet order."""

    STEWARD_PATH = "steward-path"
    GOVERNANCE_PATH = "governance-path"
    AUTONOMY_PATH = "autonomy-path"


class DelegationMode(str, Enum):
    """Delegation mode assigned by the matrix."""

    HARD_HANDOFF = "hard-handoff"
    GOVERNED_HANDOFF = "governed-handoff"
    ENABLED_HANDOFF = "enabled-handoff"


class DelegationStatus(str, Enum):
    """Current routing posture of one delegation entry."""

    PINNED = "pinned"
    ROUTED = "routed"
    OPEN = "open"


@dataclass(frozen=True)
class DelegationEntry:
    """One routed delegation entry derived from a cabinet order."""

    delegation_id: str
    sequence: int
    order_id: str
    cabinet_role: CabinetRole
    delegation_lane: DelegationLane
    delegation_mode: DelegationMode
    delegation_status: DelegationStatus
    case_ids: tuple[str, ...]
    release_ready: bool
    handoff_score: float
    recall_window: int
    delegation_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "delegation_id", _non_empty(self.delegation_id, field_name="delegation_id"))
        object.__setattr__(self, "order_id", _non_empty(self.order_id, field_name="order_id"))
        object.__setattr__(self, "handoff_score", _clamp01(self.handoff_score))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.recall_window < 1:
            raise ValueError("recall_window must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "delegation_id": self.delegation_id,
            "sequence": self.sequence,
            "order_id": self.order_id,
            "cabinet_role": self.cabinet_role.value,
            "delegation_lane": self.delegation_lane.value,
            "delegation_mode": self.delegation_mode.value,
            "delegation_status": self.delegation_status.value,
            "case_ids": list(self.case_ids),
            "release_ready": self.release_ready,
            "handoff_score": self.handoff_score,
            "recall_window": self.recall_window,
            "delegation_tags": list(self.delegation_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class DelegationMatrix:
    """Matrix routing cabinet orders into durable delegation paths."""

    matrix_id: str
    execution_cabinet: ExecutionCabinet
    delegations: tuple[DelegationEntry, ...]
    matrix_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "matrix_id", _non_empty(self.matrix_id, field_name="matrix_id"))

    @property
    def pinned_delegation_ids(self) -> tuple[str, ...]:
        return tuple(item.delegation_id for item in self.delegations if item.delegation_status is DelegationStatus.PINNED)

    @property
    def routed_delegation_ids(self) -> tuple[str, ...]:
        return tuple(item.delegation_id for item in self.delegations if item.delegation_status is DelegationStatus.ROUTED)

    @property
    def open_delegation_ids(self) -> tuple[str, ...]:
        return tuple(item.delegation_id for item in self.delegations if item.delegation_status is DelegationStatus.OPEN)

    def to_dict(self) -> dict[str, object]:
        return {
            "matrix_id": self.matrix_id,
            "execution_cabinet": self.execution_cabinet.to_dict(),
            "delegations": [item.to_dict() for item in self.delegations],
            "matrix_signal": self.matrix_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "pinned_delegation_ids": list(self.pinned_delegation_ids),
            "routed_delegation_ids": list(self.routed_delegation_ids),
            "open_delegation_ids": list(self.open_delegation_ids),
        }


def _delegation_lane(order: CabinetOrder) -> DelegationLane:
    return {
        CabinetRole.STEWARD_CHIEF: DelegationLane.STEWARD_PATH,
        CabinetRole.GOVERNANCE_MINISTER: DelegationLane.GOVERNANCE_PATH,
        CabinetRole.AUTONOMY_MINISTER: DelegationLane.AUTONOMY_PATH,
    }[order.cabinet_role]


def _delegation_mode(order: CabinetOrder) -> DelegationMode:
    return {
        CabinetExecutionMode.ENFORCE_HOLD: DelegationMode.HARD_HANDOFF,
        CabinetExecutionMode.COORDINATE_ALIGNMENT: DelegationMode.GOVERNED_HANDOFF,
        CabinetExecutionMode.AUTHORIZE_RELEASE: DelegationMode.ENABLED_HANDOFF,
    }[order.execution_mode]


def _delegation_status(order: CabinetOrder) -> DelegationStatus:
    return {
        CabinetStatus.LOCKED: DelegationStatus.PINNED,
        CabinetStatus.SUPERVISING: DelegationStatus.ROUTED,
        CabinetStatus.COMMISSIONED: DelegationStatus.OPEN,
    }[order.cabinet_status]


def _handoff_score(order: CabinetOrder) -> float:
    bonus = 0.08 if order.release_ready else 0.0
    return round(min(1.0, order.authority_band + bonus), 3)


def _recall_window(order: CabinetOrder) -> int:
    if order.cabinet_status is CabinetStatus.LOCKED:
        return 1
    if order.cabinet_status is CabinetStatus.SUPERVISING:
        return order.execution_window + 1
    return order.execution_window + 2


def build_delegation_matrix(
    execution_cabinet: ExecutionCabinet | None = None,
    *,
    matrix_id: str = "delegation-matrix",
) -> DelegationMatrix:
    """Build the delegation matrix over cabinet execution orders."""

    resolved_cabinet = (
        build_execution_cabinet(cabinet_id=f"{matrix_id}-cabinet")
        if execution_cabinet is None
        else execution_cabinet
    )
    delegations = tuple(
        DelegationEntry(
            delegation_id=f"{matrix_id}-{order.order_id.removeprefix(f'{resolved_cabinet.cabinet_id}-')}",
            sequence=index,
            order_id=order.order_id,
            cabinet_role=order.cabinet_role,
            delegation_lane=_delegation_lane(order),
            delegation_mode=_delegation_mode(order),
            delegation_status=_delegation_status(order),
            case_ids=order.case_ids,
            release_ready=order.release_ready and _delegation_status(order) is DelegationStatus.OPEN,
            handoff_score=_handoff_score(order),
            recall_window=_recall_window(order),
            delegation_tags=tuple(
                dict.fromkeys(
                    (
                        *order.cabinet_tags,
                        _delegation_lane(order).value,
                        _delegation_mode(order).value,
                        _delegation_status(order).value,
                    )
                )
            ),
            summary=(
                f"{order.order_id} routes through {_delegation_lane(order).value} as "
                f"{_delegation_mode(order).value} with {_delegation_status(order).value} status."
            ),
        )
        for index, order in enumerate(resolved_cabinet.orders, start=1)
    )
    if not delegations:
        raise ValueError("delegation matrix requires at least one entry")

    severity = "info"
    status = "delegation-open"
    if any(item.delegation_status is DelegationStatus.PINNED for item in delegations):
        severity = "critical"
        status = "delegation-pinned"
    elif any(item.delegation_status is DelegationStatus.ROUTED for item in delegations):
        severity = "warning"
        status = "delegation-routed"

    matrix_signal = TelemetrySignal(
        signal_name="delegation-matrix",
        boundary=resolved_cabinet.cabinet_signal.boundary,
        correlation_id=matrix_id,
        severity=severity,
        status=status,
        metrics={
            "delegation_count": float(len(delegations)),
            "pinned_count": float(len([item for item in delegations if item.delegation_status is DelegationStatus.PINNED])),
            "routed_count": float(len([item for item in delegations if item.delegation_status is DelegationStatus.ROUTED])),
            "open_count": float(len([item for item in delegations if item.delegation_status is DelegationStatus.OPEN])),
            "release_ready_count": float(len([item for item in delegations if item.release_ready])),
            "avg_handoff_score": round(sum(item.handoff_score for item in delegations) / len(delegations), 3),
        },
        labels={"matrix_id": matrix_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_cabinet.final_snapshot.runtime_stage,
        signals=(matrix_signal, *resolved_cabinet.final_snapshot.signals),
        alerts=resolved_cabinet.final_snapshot.alerts,
        audit_entries=resolved_cabinet.final_snapshot.audit_entries,
        active_controls=resolved_cabinet.final_snapshot.active_controls,
    )
    return DelegationMatrix(
        matrix_id=matrix_id,
        execution_cabinet=resolved_cabinet,
        delegations=delegations,
        matrix_signal=matrix_signal,
        final_snapshot=final_snapshot,
    )
