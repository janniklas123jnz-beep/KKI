"""Execution cabinet translating archived directives into executable cabinet orders."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .decision_archive import (
    ArchiveEntry,
    ArchiveStatus,
    DecisionArchive,
    build_decision_archive,
)
from .directive_consensus import ConsensusDirectiveStatus, ConsensusDirectiveType
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class CabinetRole(str, Enum):
    """Cabinet role assigned to one archived top-level directive."""

    STEWARD_CHIEF = "steward-chief"
    GOVERNANCE_MINISTER = "governance-minister"
    AUTONOMY_MINISTER = "autonomy-minister"


class CabinetExecutionMode(str, Enum):
    """Execution mode used by the cabinet for one order."""

    ENFORCE_HOLD = "enforce-hold"
    COORDINATE_ALIGNMENT = "coordinate-alignment"
    AUTHORIZE_RELEASE = "authorize-release"


class CabinetStatus(str, Enum):
    """Current operating posture of one cabinet order."""

    LOCKED = "locked"
    SUPERVISING = "supervising"
    COMMISSIONED = "commissioned"


@dataclass(frozen=True)
class CabinetOrder:
    """One executable cabinet order derived from an archived directive."""

    order_id: str
    sequence: int
    entry_id: str
    directive_id: str
    cabinet_role: CabinetRole
    execution_mode: CabinetExecutionMode
    cabinet_status: CabinetStatus
    case_ids: tuple[str, ...]
    release_ready: bool
    authority_band: float
    execution_window: int
    cabinet_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "order_id", _non_empty(self.order_id, field_name="order_id"))
        object.__setattr__(self, "entry_id", _non_empty(self.entry_id, field_name="entry_id"))
        object.__setattr__(self, "directive_id", _non_empty(self.directive_id, field_name="directive_id"))
        object.__setattr__(self, "authority_band", _clamp01(self.authority_band))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.execution_window < 1:
            raise ValueError("execution_window must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "order_id": self.order_id,
            "sequence": self.sequence,
            "entry_id": self.entry_id,
            "directive_id": self.directive_id,
            "cabinet_role": self.cabinet_role.value,
            "execution_mode": self.execution_mode.value,
            "cabinet_status": self.cabinet_status.value,
            "case_ids": list(self.case_ids),
            "release_ready": self.release_ready,
            "authority_band": self.authority_band,
            "execution_window": self.execution_window,
            "cabinet_tags": list(self.cabinet_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class ExecutionCabinet:
    """Executable cabinet order built from the decision archive."""

    cabinet_id: str
    decision_archive: DecisionArchive
    orders: tuple[CabinetOrder, ...]
    cabinet_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "cabinet_id", _non_empty(self.cabinet_id, field_name="cabinet_id"))

    @property
    def locked_order_ids(self) -> tuple[str, ...]:
        return tuple(order.order_id for order in self.orders if order.cabinet_status is CabinetStatus.LOCKED)

    @property
    def supervising_order_ids(self) -> tuple[str, ...]:
        return tuple(order.order_id for order in self.orders if order.cabinet_status is CabinetStatus.SUPERVISING)

    @property
    def commissioned_order_ids(self) -> tuple[str, ...]:
        return tuple(order.order_id for order in self.orders if order.cabinet_status is CabinetStatus.COMMISSIONED)

    def to_dict(self) -> dict[str, object]:
        return {
            "cabinet_id": self.cabinet_id,
            "decision_archive": self.decision_archive.to_dict(),
            "orders": [order.to_dict() for order in self.orders],
            "cabinet_signal": self.cabinet_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "locked_order_ids": list(self.locked_order_ids),
            "supervising_order_ids": list(self.supervising_order_ids),
            "commissioned_order_ids": list(self.commissioned_order_ids),
        }


def _cabinet_role(entry: ArchiveEntry) -> CabinetRole:
    return {
        ConsensusDirectiveType.CONSTITUTIONAL_LOCK: CabinetRole.STEWARD_CHIEF,
        ConsensusDirectiveType.GOVERNED_COMPACT: CabinetRole.GOVERNANCE_MINISTER,
        ConsensusDirectiveType.EXPANSION_ACCORD: CabinetRole.AUTONOMY_MINISTER,
    }[entry.directive_type]


def _execution_mode(entry: ArchiveEntry) -> CabinetExecutionMode:
    return {
        ConsensusDirectiveStatus.BINDING: CabinetExecutionMode.ENFORCE_HOLD,
        ConsensusDirectiveStatus.NEGOTIATED: CabinetExecutionMode.COORDINATE_ALIGNMENT,
        ConsensusDirectiveStatus.RATIFIED: CabinetExecutionMode.AUTHORIZE_RELEASE,
    }[entry.directive_status]


def _cabinet_status(entry: ArchiveEntry) -> CabinetStatus:
    return {
        ArchiveStatus.SEALED: CabinetStatus.LOCKED,
        ArchiveStatus.INDEXED: CabinetStatus.SUPERVISING,
        ArchiveStatus.CODIFIED: CabinetStatus.COMMISSIONED,
    }[entry.archive_status]


def _authority_band(entry: ArchiveEntry) -> float:
    return round(max(entry.retention_score, entry.archive_weight), 3)


def _execution_window(entry: ArchiveEntry) -> int:
    if entry.archive_status is ArchiveStatus.SEALED:
        return 1
    if entry.archive_status is ArchiveStatus.INDEXED:
        return 2
    return 3


def build_execution_cabinet(
    decision_archive: DecisionArchive | None = None,
    *,
    cabinet_id: str = "execution-cabinet",
) -> ExecutionCabinet:
    """Build an executable cabinet order from archived top-level directives."""

    resolved_archive = (
        build_decision_archive(archive_id=f"{cabinet_id}-archive")
        if decision_archive is None
        else decision_archive
    )
    orders = tuple(
        CabinetOrder(
            order_id=f"{cabinet_id}-{entry.entry_id.removeprefix(f'{resolved_archive.archive_id}-')}",
            sequence=index,
            entry_id=entry.entry_id,
            directive_id=entry.directive_id,
            cabinet_role=_cabinet_role(entry),
            execution_mode=_execution_mode(entry),
            cabinet_status=_cabinet_status(entry),
            case_ids=entry.case_ids,
            release_ready=entry.release_ready and _cabinet_status(entry) is CabinetStatus.COMMISSIONED,
            authority_band=_authority_band(entry),
            execution_window=_execution_window(entry),
            cabinet_tags=tuple(
                dict.fromkeys(
                    (
                        *entry.archive_tags,
                        _cabinet_role(entry).value,
                        _execution_mode(entry).value,
                        _cabinet_status(entry).value,
                    )
                )
            ),
            summary=(
                f"{entry.entry_id} is executed by {_cabinet_role(entry).value} in "
                f"{_execution_mode(entry).value} mode under {_cabinet_status(entry).value} cabinet posture."
            ),
        )
        for index, entry in enumerate(resolved_archive.entries, start=1)
    )
    if not orders:
        raise ValueError("execution cabinet requires at least one order")

    severity = "info"
    status = "cabinet-commissioned"
    if any(order.cabinet_status is CabinetStatus.LOCKED for order in orders):
        severity = "critical"
        status = "cabinet-locked"
    elif any(order.cabinet_status is CabinetStatus.SUPERVISING for order in orders):
        severity = "warning"
        status = "cabinet-supervising"

    cabinet_signal = TelemetrySignal(
        signal_name="execution-cabinet",
        boundary=resolved_archive.archive_signal.boundary,
        correlation_id=cabinet_id,
        severity=severity,
        status=status,
        metrics={
            "order_count": float(len(orders)),
            "locked_count": float(len([order for order in orders if order.cabinet_status is CabinetStatus.LOCKED])),
            "supervising_count": float(
                len([order for order in orders if order.cabinet_status is CabinetStatus.SUPERVISING])
            ),
            "commissioned_count": float(
                len([order for order in orders if order.cabinet_status is CabinetStatus.COMMISSIONED])
            ),
            "release_ready_count": float(len([order for order in orders if order.release_ready])),
            "avg_authority_band": round(sum(order.authority_band for order in orders) / len(orders), 3),
        },
        labels={"cabinet_id": cabinet_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_archive.final_snapshot.runtime_stage,
        signals=(cabinet_signal, *resolved_archive.final_snapshot.signals),
        alerts=resolved_archive.final_snapshot.alerts,
        audit_entries=resolved_archive.final_snapshot.audit_entries,
        active_controls=resolved_archive.final_snapshot.active_controls,
    )
    return ExecutionCabinet(
        cabinet_id=cabinet_id,
        decision_archive=resolved_archive,
        orders=orders,
        cabinet_signal=cabinet_signal,
        final_snapshot=final_snapshot,
    )
