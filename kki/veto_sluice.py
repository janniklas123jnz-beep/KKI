"""Veto sluice guarding delegation routes with stop, release, and recall paths."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .delegation_matrix import (
    DelegationEntry,
    DelegationLane,
    DelegationMatrix,
    DelegationMode,
    DelegationStatus,
    build_delegation_matrix,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class VetoStop(str, Enum):
    """Explicit stop condition enforced by the sluice."""

    HARD_STOP = "hard-stop"
    REVIEW_STOP = "review-stop"
    OPEN_STOP = "open-stop"


class ReleasePath(str, Enum):
    """Release path exposed by the sluice."""

    EXECUTIVE_RELEASE = "executive-release"
    GOVERNED_RELEASE = "governed-release"
    AUTONOMY_RELEASE = "autonomy-release"


class RecallPath(str, Enum):
    """Recall path used to pull delegated work back."""

    IMMEDIATE_RECALL = "immediate-recall"
    GOVERNED_RECALL = "governed-recall"
    SUPERVISED_RECALL = "supervised-recall"


class SluiceStatus(str, Enum):
    """Current posture of one veto sluice channel."""

    BLOCKING = "blocking"
    REVIEWING = "reviewing"
    CLEARING = "clearing"


@dataclass(frozen=True)
class VetoChannel:
    """One guarded channel derived from a delegation entry."""

    channel_id: str
    sequence: int
    delegation_id: str
    delegation_lane: DelegationLane
    veto_stop: VetoStop
    release_path: ReleasePath
    recall_path: RecallPath
    sluice_status: SluiceStatus
    case_ids: tuple[str, ...]
    release_ready: bool
    guard_score: float
    escalation_window: int
    sluice_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "channel_id", _non_empty(self.channel_id, field_name="channel_id"))
        object.__setattr__(self, "delegation_id", _non_empty(self.delegation_id, field_name="delegation_id"))
        object.__setattr__(self, "guard_score", _clamp01(self.guard_score))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.escalation_window < 1:
            raise ValueError("escalation_window must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "channel_id": self.channel_id,
            "sequence": self.sequence,
            "delegation_id": self.delegation_id,
            "delegation_lane": self.delegation_lane.value,
            "veto_stop": self.veto_stop.value,
            "release_path": self.release_path.value,
            "recall_path": self.recall_path.value,
            "sluice_status": self.sluice_status.value,
            "case_ids": list(self.case_ids),
            "release_ready": self.release_ready,
            "guard_score": self.guard_score,
            "escalation_window": self.escalation_window,
            "sluice_tags": list(self.sluice_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class VetoSluice:
    """Sluice guarding delegation routes with explicit veto and recall controls."""

    sluice_id: str
    delegation_matrix: DelegationMatrix
    channels: tuple[VetoChannel, ...]
    sluice_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "sluice_id", _non_empty(self.sluice_id, field_name="sluice_id"))

    @property
    def blocking_channel_ids(self) -> tuple[str, ...]:
        return tuple(item.channel_id for item in self.channels if item.sluice_status is SluiceStatus.BLOCKING)

    @property
    def reviewing_channel_ids(self) -> tuple[str, ...]:
        return tuple(item.channel_id for item in self.channels if item.sluice_status is SluiceStatus.REVIEWING)

    @property
    def clearing_channel_ids(self) -> tuple[str, ...]:
        return tuple(item.channel_id for item in self.channels if item.sluice_status is SluiceStatus.CLEARING)

    def to_dict(self) -> dict[str, object]:
        return {
            "sluice_id": self.sluice_id,
            "delegation_matrix": self.delegation_matrix.to_dict(),
            "channels": [item.to_dict() for item in self.channels],
            "sluice_signal": self.sluice_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "blocking_channel_ids": list(self.blocking_channel_ids),
            "reviewing_channel_ids": list(self.reviewing_channel_ids),
            "clearing_channel_ids": list(self.clearing_channel_ids),
        }


def _veto_stop(entry: DelegationEntry) -> VetoStop:
    return {
        DelegationStatus.PINNED: VetoStop.HARD_STOP,
        DelegationStatus.ROUTED: VetoStop.REVIEW_STOP,
        DelegationStatus.OPEN: VetoStop.OPEN_STOP,
    }[entry.delegation_status]


def _release_path(entry: DelegationEntry) -> ReleasePath:
    return {
        DelegationMode.HARD_HANDOFF: ReleasePath.EXECUTIVE_RELEASE,
        DelegationMode.GOVERNED_HANDOFF: ReleasePath.GOVERNED_RELEASE,
        DelegationMode.ENABLED_HANDOFF: ReleasePath.AUTONOMY_RELEASE,
    }[entry.delegation_mode]


def _recall_path(entry: DelegationEntry) -> RecallPath:
    return {
        DelegationStatus.PINNED: RecallPath.IMMEDIATE_RECALL,
        DelegationStatus.ROUTED: RecallPath.GOVERNED_RECALL,
        DelegationStatus.OPEN: RecallPath.SUPERVISED_RECALL,
    }[entry.delegation_status]


def _sluice_status(entry: DelegationEntry) -> SluiceStatus:
    return {
        DelegationStatus.PINNED: SluiceStatus.BLOCKING,
        DelegationStatus.ROUTED: SluiceStatus.REVIEWING,
        DelegationStatus.OPEN: SluiceStatus.CLEARING,
    }[entry.delegation_status]


def _guard_score(entry: DelegationEntry) -> float:
    bonus = 0.08 if entry.release_ready else 0.0
    return round(min(1.0, entry.handoff_score + bonus), 3)


def _escalation_window(entry: DelegationEntry) -> int:
    if entry.delegation_status is DelegationStatus.PINNED:
        return 1
    if entry.delegation_status is DelegationStatus.ROUTED:
        return entry.recall_window
    return entry.recall_window + 1


def build_veto_sluice(
    delegation_matrix: DelegationMatrix | None = None,
    *,
    sluice_id: str = "veto-sluice",
) -> VetoSluice:
    """Build the veto sluice over delegation matrix routes."""

    resolved_matrix = (
        build_delegation_matrix(matrix_id=f"{sluice_id}-matrix")
        if delegation_matrix is None
        else delegation_matrix
    )
    channels = tuple(
        VetoChannel(
            channel_id=f"{sluice_id}-{entry.delegation_id.removeprefix(f'{resolved_matrix.matrix_id}-')}",
            sequence=index,
            delegation_id=entry.delegation_id,
            delegation_lane=entry.delegation_lane,
            veto_stop=_veto_stop(entry),
            release_path=_release_path(entry),
            recall_path=_recall_path(entry),
            sluice_status=_sluice_status(entry),
            case_ids=entry.case_ids,
            release_ready=entry.release_ready and _sluice_status(entry) is SluiceStatus.CLEARING,
            guard_score=_guard_score(entry),
            escalation_window=_escalation_window(entry),
            sluice_tags=tuple(
                dict.fromkeys(
                    (
                        *entry.delegation_tags,
                        _veto_stop(entry).value,
                        _release_path(entry).value,
                        _recall_path(entry).value,
                        _sluice_status(entry).value,
                    )
                )
            ),
            summary=(
                f"{entry.delegation_id} is guarded by {_veto_stop(entry).value} "
                f"with {_release_path(entry).value} and {_recall_path(entry).value}."
            ),
        )
        for index, entry in enumerate(resolved_matrix.delegations, start=1)
    )
    if not channels:
        raise ValueError("veto sluice requires at least one channel")

    severity = "info"
    status = "sluice-clearing"
    if any(item.sluice_status is SluiceStatus.BLOCKING for item in channels):
        severity = "critical"
        status = "sluice-blocking"
    elif any(item.sluice_status is SluiceStatus.REVIEWING for item in channels):
        severity = "warning"
        status = "sluice-reviewing"

    sluice_signal = TelemetrySignal(
        signal_name="veto-sluice",
        boundary=resolved_matrix.matrix_signal.boundary,
        correlation_id=sluice_id,
        severity=severity,
        status=status,
        metrics={
            "channel_count": float(len(channels)),
            "blocking_count": float(len([item for item in channels if item.sluice_status is SluiceStatus.BLOCKING])),
            "reviewing_count": float(len([item for item in channels if item.sluice_status is SluiceStatus.REVIEWING])),
            "clearing_count": float(len([item for item in channels if item.sluice_status is SluiceStatus.CLEARING])),
            "release_ready_count": float(len([item for item in channels if item.release_ready])),
            "avg_guard_score": round(sum(item.guard_score for item in channels) / len(channels), 3),
        },
        labels={"sluice_id": sluice_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_matrix.final_snapshot.runtime_stage,
        signals=(sluice_signal, *resolved_matrix.final_snapshot.signals),
        alerts=resolved_matrix.final_snapshot.alerts,
        audit_entries=resolved_matrix.final_snapshot.audit_entries,
        active_controls=resolved_matrix.final_snapshot.active_controls,
    )
    return VetoSluice(
        sluice_id=sluice_id,
        delegation_matrix=resolved_matrix,
        channels=channels,
        sluice_signal=sluice_signal,
        final_snapshot=final_snapshot,
    )
