"""Priority conclave consolidating missions, doctrine, and diplomacy into top selections."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .consensus_diplomacy import ConsensusDiplomacy, DiplomacyChannel, DiplomacyStatus
from .leitstern_doctrine import DoctrineClause, LeitsternDoctrine
from .missions_collegium import CollegiumLane, CollegiumSeat, CollegiumStatus, MissionsCollegium, build_missions_collegium
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class ConclavePriority(str, Enum):
    """Priority posture assigned by the conclave."""

    STABILITY_FIRST = "stability-first"
    GOVERNANCE_FOCUS = "governance-focus"
    RELEASE_VECTOR = "release-vector"


class ConclaveLane(str, Enum):
    """Top-selection lane used by the conclave."""

    CONTAINMENT_SLOT = "containment-slot"
    GOVERNANCE_SLOT = "governance-slot"
    EXPANSION_SLOT = "expansion-slot"


class ConclaveStatus(str, Enum):
    """Selection state reached by one conclave motion."""

    GUARDED = "guarded"
    SHORTLISTED = "shortlisted"
    ELECTED = "elected"


@dataclass(frozen=True)
class ConclaveMotion:
    """One prioritized top-selection motion derived from a collegium seat."""

    motion_id: str
    sequence: int
    selection_rank: int
    seat_id: str
    clause_id: str
    source_diplomacy_id: str
    mission_ref: str
    conclave_priority: ConclavePriority
    conclave_lane: ConclaveLane
    conclave_status: ConclaveStatus
    case_ids: tuple[str, ...]
    release_ready: bool
    priority_score: float
    vote_window: int
    conclave_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "motion_id", _non_empty(self.motion_id, field_name="motion_id"))
        object.__setattr__(self, "seat_id", _non_empty(self.seat_id, field_name="seat_id"))
        object.__setattr__(self, "clause_id", _non_empty(self.clause_id, field_name="clause_id"))
        object.__setattr__(self, "source_diplomacy_id", _non_empty(self.source_diplomacy_id, field_name="source_diplomacy_id"))
        object.__setattr__(self, "mission_ref", _non_empty(self.mission_ref, field_name="mission_ref"))
        object.__setattr__(self, "priority_score", _clamp01(self.priority_score))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.selection_rank < 1:
            raise ValueError("selection_rank must be positive")
        if self.vote_window < 1:
            raise ValueError("vote_window must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "motion_id": self.motion_id,
            "sequence": self.sequence,
            "selection_rank": self.selection_rank,
            "seat_id": self.seat_id,
            "clause_id": self.clause_id,
            "source_diplomacy_id": self.source_diplomacy_id,
            "mission_ref": self.mission_ref,
            "conclave_priority": self.conclave_priority.value,
            "conclave_lane": self.conclave_lane.value,
            "conclave_status": self.conclave_status.value,
            "case_ids": list(self.case_ids),
            "release_ready": self.release_ready,
            "priority_score": self.priority_score,
            "vote_window": self.vote_window,
            "conclave_tags": list(self.conclave_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class PriorityConclave:
    """Prioritized top-selection over missions, doctrine, and diplomacy."""

    conclave_id: str
    missions_collegium: MissionsCollegium
    consensus_diplomacy: ConsensusDiplomacy
    motions: tuple[ConclaveMotion, ...]
    conclave_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "conclave_id", _non_empty(self.conclave_id, field_name="conclave_id"))

    @property
    def guarded_motion_ids(self) -> tuple[str, ...]:
        return tuple(motion.motion_id for motion in self.motions if motion.conclave_status is ConclaveStatus.GUARDED)

    @property
    def shortlisted_motion_ids(self) -> tuple[str, ...]:
        return tuple(motion.motion_id for motion in self.motions if motion.conclave_status is ConclaveStatus.SHORTLISTED)

    @property
    def elected_motion_ids(self) -> tuple[str, ...]:
        return tuple(motion.motion_id for motion in self.motions if motion.conclave_status is ConclaveStatus.ELECTED)

    def to_dict(self) -> dict[str, object]:
        return {
            "conclave_id": self.conclave_id,
            "missions_collegium": self.missions_collegium.to_dict(),
            "consensus_diplomacy": self.consensus_diplomacy.to_dict(),
            "motions": [motion.to_dict() for motion in self.motions],
            "conclave_signal": self.conclave_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "guarded_motion_ids": list(self.guarded_motion_ids),
            "shortlisted_motion_ids": list(self.shortlisted_motion_ids),
            "elected_motion_ids": list(self.elected_motion_ids),
        }


def _priority(seat: CollegiumSeat) -> ConclavePriority:
    return {
        CollegiumStatus.RESERVED: ConclavePriority.STABILITY_FIRST,
        CollegiumStatus.COORDINATING: ConclavePriority.GOVERNANCE_FOCUS,
        CollegiumStatus.DEPLOYED: ConclavePriority.RELEASE_VECTOR,
    }[seat.collegium_status]


def _lane(seat: CollegiumSeat) -> ConclaveLane:
    return {
        CollegiumLane.CONTAINMENT_PORTFOLIO: ConclaveLane.CONTAINMENT_SLOT,
        CollegiumLane.GOVERNANCE_PORTFOLIO: ConclaveLane.GOVERNANCE_SLOT,
        CollegiumLane.EXPANSION_PORTFOLIO: ConclaveLane.EXPANSION_SLOT,
    }[seat.collegium_lane]


def _status(channel: DiplomacyChannel) -> ConclaveStatus:
    return {
        DiplomacyStatus.DEADLOCKED: ConclaveStatus.GUARDED,
        DiplomacyStatus.BROKERED: ConclaveStatus.SHORTLISTED,
        DiplomacyStatus.HARMONIZED: ConclaveStatus.ELECTED,
    }[channel.diplomacy_status]


def _priority_score(seat: CollegiumSeat, clause: DoctrineClause, channel: DiplomacyChannel) -> float:
    urgency_bonus = {
        ConclaveStatus.GUARDED: 0.12,
        ConclaveStatus.SHORTLISTED: 0.05,
        ConclaveStatus.ELECTED: 0.0,
    }[_status(channel)]
    score = (seat.collegium_weight + clause.doctrine_strength + channel.compromise_score) / 3.0
    return round(min(1.0, score + urgency_bonus), 3)


def _vote_window(seat: CollegiumSeat, clause: DoctrineClause, channel: DiplomacyChannel) -> int:
    if channel.diplomacy_status is DiplomacyStatus.DEADLOCKED:
        return max(seat.coordination_window, clause.doctrine_window)
    if channel.diplomacy_status is DiplomacyStatus.BROKERED:
        return max(seat.coordination_window, clause.doctrine_window) + 1
    return max(seat.coordination_window, clause.doctrine_window) + 2


def build_priority_conclave(
    missions_collegium: MissionsCollegium | None = None,
    consensus_diplomacy: ConsensusDiplomacy | None = None,
    *,
    conclave_id: str = "priority-conclave",
) -> PriorityConclave:
    """Build the prioritized top-selection over missions, doctrine, and diplomacy."""

    resolved_collegium = (
        build_missions_collegium(collegium_id=f"{conclave_id}-collegium")
        if missions_collegium is None
        else missions_collegium
    )
    resolved_diplomacy = (
        resolved_collegium.leitstern_doctrine.consensus_diplomacy
        if consensus_diplomacy is None
        else consensus_diplomacy
    )
    resolved_doctrine: LeitsternDoctrine = resolved_collegium.leitstern_doctrine
    clauses_by_id = {clause.clause_id: clause for clause in resolved_doctrine.clauses}
    channels_by_id = {channel.diplomacy_id: channel for channel in resolved_diplomacy.channels}

    raw_motions = []
    for seat in resolved_collegium.seats:
        clause = clauses_by_id[seat.clause_id]
        channel = channels_by_id[clause.source_diplomacy_id]
        priority = _priority(seat)
        lane = _lane(seat)
        status = _status(channel)
        priority_score = _priority_score(seat, clause, channel)
        vote_window = _vote_window(seat, clause, channel)
        raw_motions.append(
            {
                "seat": seat,
                "clause": clause,
                "channel": channel,
                "priority": priority,
                "lane": lane,
                "status": status,
                "priority_score": priority_score,
                "vote_window": vote_window,
                "case_ids": tuple(dict.fromkeys((*seat.case_ids, *clause.case_ids, *channel.case_ids))),
                "release_ready": seat.release_ready and channel.release_ready and status is ConclaveStatus.ELECTED,
                "conclave_tags": tuple(
                    dict.fromkeys(
                        (
                            *seat.collegium_tags,
                            *clause.doctrine_tags,
                            *channel.diplomacy_tags,
                            priority.value,
                            lane.value,
                            status.value,
                        )
                    )
                ),
                "summary": (
                    f"{seat.seat_id} enters the conclave as {priority.value} in {lane.value} "
                    f"and is ranked {status.value}."
                ),
            }
        )

    if not raw_motions:
        raise ValueError("priority conclave requires at least one motion")

    ordered_raw = tuple(
        sorted(
            raw_motions,
            key=lambda item: (
                {
                    ConclavePriority.STABILITY_FIRST: 0,
                    ConclavePriority.GOVERNANCE_FOCUS: 1,
                    ConclavePriority.RELEASE_VECTOR: 2,
                }[item["priority"]],
                -item["priority_score"],
                item["seat"].mission_ref,
            ),
        )
    )
    motions = tuple(
        ConclaveMotion(
            motion_id=f"{conclave_id}-{item['seat'].seat_id.removeprefix(f'{resolved_collegium.collegium_id}-')}",
            sequence=index,
            selection_rank=index,
            seat_id=item["seat"].seat_id,
            clause_id=item["clause"].clause_id,
            source_diplomacy_id=item["channel"].diplomacy_id,
            mission_ref=item["seat"].mission_ref,
            conclave_priority=item["priority"],
            conclave_lane=item["lane"],
            conclave_status=item["status"],
            case_ids=item["case_ids"],
            release_ready=item["release_ready"],
            priority_score=item["priority_score"],
            vote_window=item["vote_window"],
            conclave_tags=item["conclave_tags"],
            summary=item["summary"],
        )
        for index, item in enumerate(ordered_raw, start=1)
    )

    severity = "info"
    status = "conclave-elected"
    if any(motion.conclave_status is ConclaveStatus.GUARDED for motion in motions):
        severity = "critical"
        status = "conclave-guarded"
    elif any(motion.conclave_status is ConclaveStatus.SHORTLISTED for motion in motions):
        severity = "warning"
        status = "conclave-shortlisted"

    conclave_signal = TelemetrySignal(
        signal_name="priority-conclave",
        boundary=resolved_collegium.collegium_signal.boundary,
        correlation_id=conclave_id,
        severity=severity,
        status=status,
        metrics={
            "motion_count": float(len(motions)),
            "guarded_count": float(len([motion for motion in motions if motion.conclave_status is ConclaveStatus.GUARDED])),
            "shortlisted_count": float(
                len([motion for motion in motions if motion.conclave_status is ConclaveStatus.SHORTLISTED])
            ),
            "elected_count": float(len([motion for motion in motions if motion.conclave_status is ConclaveStatus.ELECTED])),
            "release_ready_count": float(len([motion for motion in motions if motion.release_ready])),
            "avg_priority_score": round(sum(motion.priority_score for motion in motions) / len(motions), 3),
        },
        labels={"conclave_id": conclave_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_collegium.final_snapshot.runtime_stage,
        signals=(conclave_signal, *resolved_collegium.final_snapshot.signals),
        alerts=resolved_collegium.final_snapshot.alerts,
        audit_entries=resolved_collegium.final_snapshot.audit_entries,
        active_controls=resolved_collegium.final_snapshot.active_controls,
    )
    return PriorityConclave(
        conclave_id=conclave_id,
        missions_collegium=resolved_collegium,
        consensus_diplomacy=resolved_diplomacy,
        motions=motions,
        conclave_signal=conclave_signal,
        final_snapshot=final_snapshot,
    )
