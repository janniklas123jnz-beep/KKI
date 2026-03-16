"""Consensus diplomacy reconciling veto sluice channels into negotiated paths."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .veto_sluice import (
    RecallPath,
    ReleasePath,
    SluiceStatus,
    VetoChannel,
    VetoSluice,
    VetoStop,
    build_veto_sluice,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class DiplomacyPosture(str, Enum):
    """Negotiation posture taken for one sluice channel."""

    CONTAINMENT_TALKS = "containment-talks"
    REVIEW_COMPACT = "review-compact"
    RELEASE_ACCORD = "release-accord"


class DiplomacyPath(str, Enum):
    """Diplomatic path chosen to reconcile the channel."""

    VETO_TABLE = "veto-table"
    GOVERNANCE_TABLE = "governance-table"
    AUTONOMY_TABLE = "autonomy-table"


class DiplomacyStatus(str, Enum):
    """Current outcome of the diplomatic handling."""

    DEADLOCKED = "deadlocked"
    BROKERED = "brokered"
    HARMONIZED = "harmonized"


@dataclass(frozen=True)
class DiplomacyChannel:
    """One negotiated channel derived from a veto sluice channel."""

    diplomacy_id: str
    sequence: int
    source_channel_id: str
    posture: DiplomacyPosture
    diplomacy_path: DiplomacyPath
    diplomacy_status: DiplomacyStatus
    case_ids: tuple[str, ...]
    release_ready: bool
    compromise_score: float
    negotiation_window: int
    diplomacy_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "diplomacy_id", _non_empty(self.diplomacy_id, field_name="diplomacy_id"))
        object.__setattr__(self, "source_channel_id", _non_empty(self.source_channel_id, field_name="source_channel_id"))
        object.__setattr__(self, "compromise_score", _clamp01(self.compromise_score))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.negotiation_window < 1:
            raise ValueError("negotiation_window must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "diplomacy_id": self.diplomacy_id,
            "sequence": self.sequence,
            "source_channel_id": self.source_channel_id,
            "posture": self.posture.value,
            "diplomacy_path": self.diplomacy_path.value,
            "diplomacy_status": self.diplomacy_status.value,
            "case_ids": list(self.case_ids),
            "release_ready": self.release_ready,
            "compromise_score": self.compromise_score,
            "negotiation_window": self.negotiation_window,
            "diplomacy_tags": list(self.diplomacy_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class ConsensusDiplomacy:
    """Diplomacy layer reconciling veto sluice channels."""

    diplomacy_id: str
    veto_sluice: VetoSluice
    channels: tuple[DiplomacyChannel, ...]
    diplomacy_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "diplomacy_id", _non_empty(self.diplomacy_id, field_name="diplomacy_id"))

    @property
    def deadlocked_channel_ids(self) -> tuple[str, ...]:
        return tuple(item.diplomacy_id for item in self.channels if item.diplomacy_status is DiplomacyStatus.DEADLOCKED)

    @property
    def brokered_channel_ids(self) -> tuple[str, ...]:
        return tuple(item.diplomacy_id for item in self.channels if item.diplomacy_status is DiplomacyStatus.BROKERED)

    @property
    def harmonized_channel_ids(self) -> tuple[str, ...]:
        return tuple(item.diplomacy_id for item in self.channels if item.diplomacy_status is DiplomacyStatus.HARMONIZED)

    def to_dict(self) -> dict[str, object]:
        return {
            "diplomacy_id": self.diplomacy_id,
            "veto_sluice": self.veto_sluice.to_dict(),
            "channels": [item.to_dict() for item in self.channels],
            "diplomacy_signal": self.diplomacy_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "deadlocked_channel_ids": list(self.deadlocked_channel_ids),
            "brokered_channel_ids": list(self.brokered_channel_ids),
            "harmonized_channel_ids": list(self.harmonized_channel_ids),
        }


def _posture(channel: VetoChannel) -> DiplomacyPosture:
    return {
        SluiceStatus.BLOCKING: DiplomacyPosture.CONTAINMENT_TALKS,
        SluiceStatus.REVIEWING: DiplomacyPosture.REVIEW_COMPACT,
        SluiceStatus.CLEARING: DiplomacyPosture.RELEASE_ACCORD,
    }[channel.sluice_status]


def _diplomacy_path(channel: VetoChannel) -> DiplomacyPath:
    if channel.release_path is ReleasePath.EXECUTIVE_RELEASE or channel.recall_path is RecallPath.IMMEDIATE_RECALL:
        return DiplomacyPath.VETO_TABLE
    if channel.release_path is ReleasePath.GOVERNED_RELEASE or channel.recall_path is RecallPath.GOVERNED_RECALL:
        return DiplomacyPath.GOVERNANCE_TABLE
    return DiplomacyPath.AUTONOMY_TABLE


def _diplomacy_status(channel: VetoChannel) -> DiplomacyStatus:
    return {
        SluiceStatus.BLOCKING: DiplomacyStatus.DEADLOCKED,
        SluiceStatus.REVIEWING: DiplomacyStatus.BROKERED,
        SluiceStatus.CLEARING: DiplomacyStatus.HARMONIZED,
    }[channel.sluice_status]


def _compromise_score(channel: VetoChannel) -> float:
    posture_bonus = {
        SluiceStatus.BLOCKING: -0.08,
        SluiceStatus.REVIEWING: 0.0,
        SluiceStatus.CLEARING: 0.08,
    }[channel.sluice_status]
    return round(max(0.0, min(1.0, channel.guard_score + posture_bonus)), 3)


def _negotiation_window(channel: VetoChannel) -> int:
    if channel.sluice_status is SluiceStatus.BLOCKING:
        return channel.escalation_window
    if channel.sluice_status is SluiceStatus.REVIEWING:
        return channel.escalation_window + 1
    return channel.escalation_window + 2


def build_consensus_diplomacy(
    veto_sluice: VetoSluice | None = None,
    *,
    diplomacy_id: str = "consensus-diplomacy",
) -> ConsensusDiplomacy:
    """Build the diplomacy layer over veto sluice channels."""

    resolved_sluice = build_veto_sluice(sluice_id=f"{diplomacy_id}-sluice") if veto_sluice is None else veto_sluice
    channels = tuple(
        DiplomacyChannel(
            diplomacy_id=f"{diplomacy_id}-{channel.channel_id.removeprefix(f'{resolved_sluice.sluice_id}-')}",
            sequence=index,
            source_channel_id=channel.channel_id,
            posture=_posture(channel),
            diplomacy_path=_diplomacy_path(channel),
            diplomacy_status=_diplomacy_status(channel),
            case_ids=channel.case_ids,
            release_ready=channel.release_ready and _diplomacy_status(channel) is DiplomacyStatus.HARMONIZED,
            compromise_score=_compromise_score(channel),
            negotiation_window=_negotiation_window(channel),
            diplomacy_tags=tuple(
                dict.fromkeys(
                    (
                        *channel.sluice_tags,
                        _posture(channel).value,
                        _diplomacy_path(channel).value,
                        _diplomacy_status(channel).value,
                    )
                )
            ),
            summary=(
                f"{channel.channel_id} enters {_posture(channel).value} via "
                f"{_diplomacy_path(channel).value} and resolves as {_diplomacy_status(channel).value}."
            ),
        )
        for index, channel in enumerate(resolved_sluice.channels, start=1)
    )
    if not channels:
        raise ValueError("consensus diplomacy requires at least one channel")

    severity = "info"
    status = "diplomacy-harmonized"
    if any(item.diplomacy_status is DiplomacyStatus.DEADLOCKED for item in channels):
        severity = "critical"
        status = "diplomacy-deadlocked"
    elif any(item.diplomacy_status is DiplomacyStatus.BROKERED for item in channels):
        severity = "warning"
        status = "diplomacy-brokered"

    diplomacy_signal = TelemetrySignal(
        signal_name="consensus-diplomacy",
        boundary=resolved_sluice.sluice_signal.boundary,
        correlation_id=diplomacy_id,
        severity=severity,
        status=status,
        metrics={
            "channel_count": float(len(channels)),
            "deadlocked_count": float(len([item for item in channels if item.diplomacy_status is DiplomacyStatus.DEADLOCKED])),
            "brokered_count": float(len([item for item in channels if item.diplomacy_status is DiplomacyStatus.BROKERED])),
            "harmonized_count": float(len([item for item in channels if item.diplomacy_status is DiplomacyStatus.HARMONIZED])),
            "release_ready_count": float(len([item for item in channels if item.release_ready])),
            "avg_compromise_score": round(sum(item.compromise_score for item in channels) / len(channels), 3),
        },
        labels={"diplomacy_id": diplomacy_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_sluice.final_snapshot.runtime_stage,
        signals=(diplomacy_signal, *resolved_sluice.final_snapshot.signals),
        alerts=resolved_sluice.final_snapshot.alerts,
        audit_entries=resolved_sluice.final_snapshot.audit_entries,
        active_controls=resolved_sluice.final_snapshot.active_controls,
    )
    return ConsensusDiplomacy(
        diplomacy_id=diplomacy_id,
        veto_sluice=resolved_sluice,
        channels=channels,
        diplomacy_signal=diplomacy_signal,
        final_snapshot=final_snapshot,
    )
