"""Missions collegium binding Leitstern doctrine to active mission portfolios."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .leitstern_doctrine import (
    DoctrineClause,
    DoctrineScope,
    DoctrineStatus,
    LeitsternDoctrine,
    build_leitstern_doctrine,
)
from .mission_profiles import MissionProfile, MissionScenario, mission_profile_for_name
from .portfolio_radar import PortfolioExposure, PortfolioRadar, PortfolioRadarEntry, build_portfolio_radar
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class CollegiumMandate(str, Enum):
    """Mission mandate assigned by the collegium."""

    STABILITY_CHAIR = "stability-chair"
    GOVERNANCE_CHAIR = "governance-chair"
    EXPANSION_CHAIR = "expansion-chair"


class CollegiumLane(str, Enum):
    """Portfolio lane in which a collegium seat operates."""

    CONTAINMENT_PORTFOLIO = "containment-portfolio"
    GOVERNANCE_PORTFOLIO = "governance-portfolio"
    EXPANSION_PORTFOLIO = "expansion-portfolio"


class CollegiumStatus(str, Enum):
    """Operational posture of a collegium seat."""

    RESERVED = "reserved"
    COORDINATING = "coordinating"
    DEPLOYED = "deployed"


@dataclass(frozen=True)
class CollegiumSeat:
    """One mission seat coupling doctrine to a mission profile and portfolio lane."""

    seat_id: str
    sequence: int
    clause_id: str
    mission_ref: str
    radar_entry_id: str
    collegium_mandate: CollegiumMandate
    collegium_lane: CollegiumLane
    collegium_status: CollegiumStatus
    mission_scenario: MissionScenario
    case_ids: tuple[str, ...]
    release_ready: bool
    collegium_weight: float
    coordination_window: int
    collegium_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "seat_id", _non_empty(self.seat_id, field_name="seat_id"))
        object.__setattr__(self, "clause_id", _non_empty(self.clause_id, field_name="clause_id"))
        object.__setattr__(self, "mission_ref", _non_empty(self.mission_ref, field_name="mission_ref"))
        object.__setattr__(self, "radar_entry_id", _non_empty(self.radar_entry_id, field_name="radar_entry_id"))
        object.__setattr__(self, "collegium_weight", _clamp01(self.collegium_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.coordination_window < 1:
            raise ValueError("coordination_window must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "seat_id": self.seat_id,
            "sequence": self.sequence,
            "clause_id": self.clause_id,
            "mission_ref": self.mission_ref,
            "radar_entry_id": self.radar_entry_id,
            "collegium_mandate": self.collegium_mandate.value,
            "collegium_lane": self.collegium_lane.value,
            "collegium_status": self.collegium_status.value,
            "mission_scenario": self.mission_scenario.value,
            "case_ids": list(self.case_ids),
            "release_ready": self.release_ready,
            "collegium_weight": self.collegium_weight,
            "coordination_window": self.coordination_window,
            "collegium_tags": list(self.collegium_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class MissionsCollegium:
    """Mission collegium binding doctrine clauses to portfolio-backed missions."""

    collegium_id: str
    leitstern_doctrine: LeitsternDoctrine
    portfolio_radar: PortfolioRadar
    seats: tuple[CollegiumSeat, ...]
    collegium_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "collegium_id", _non_empty(self.collegium_id, field_name="collegium_id"))

    @property
    def reserved_seat_ids(self) -> tuple[str, ...]:
        return tuple(seat.seat_id for seat in self.seats if seat.collegium_status is CollegiumStatus.RESERVED)

    @property
    def coordinating_seat_ids(self) -> tuple[str, ...]:
        return tuple(seat.seat_id for seat in self.seats if seat.collegium_status is CollegiumStatus.COORDINATING)

    @property
    def deployed_seat_ids(self) -> tuple[str, ...]:
        return tuple(seat.seat_id for seat in self.seats if seat.collegium_status is CollegiumStatus.DEPLOYED)

    def to_dict(self) -> dict[str, object]:
        return {
            "collegium_id": self.collegium_id,
            "leitstern_doctrine": self.leitstern_doctrine.to_dict(),
            "portfolio_radar": self.portfolio_radar.to_dict(),
            "seats": [seat.to_dict() for seat in self.seats],
            "collegium_signal": self.collegium_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "reserved_seat_ids": list(self.reserved_seat_ids),
            "coordinating_seat_ids": list(self.coordinating_seat_ids),
            "deployed_seat_ids": list(self.deployed_seat_ids),
        }


def _mission_profile(clause: DoctrineClause) -> MissionProfile:
    preset = {
        DoctrineStatus.GUARDED: "recovery-drill",
        DoctrineStatus.ADOPTED: "shadow-hardening",
        DoctrineStatus.ENSHRINED: "pilot-cutover",
    }[clause.doctrine_status]
    return mission_profile_for_name(preset)


def _matching_radar_entry(clause: DoctrineClause, portfolio_radar: PortfolioRadar) -> PortfolioRadarEntry:
    expected_exposure = {
        DoctrineScope.STEWARD_CANON: PortfolioExposure.CONTAINED,
        DoctrineScope.GOVERNANCE_CANON: PortfolioExposure.GOVERNED,
        DoctrineScope.AUTONOMY_CANON: PortfolioExposure.EXPANSIVE,
    }[clause.doctrine_scope]
    for entry in portfolio_radar.entries:
        if entry.exposure is expected_exposure:
            return entry
    raise ValueError(f"portfolio radar missing entry for {expected_exposure.value}")


def _mandate(clause: DoctrineClause) -> CollegiumMandate:
    return {
        DoctrineScope.STEWARD_CANON: CollegiumMandate.STABILITY_CHAIR,
        DoctrineScope.GOVERNANCE_CANON: CollegiumMandate.GOVERNANCE_CHAIR,
        DoctrineScope.AUTONOMY_CANON: CollegiumMandate.EXPANSION_CHAIR,
    }[clause.doctrine_scope]


def _lane(radar_entry: PortfolioRadarEntry) -> CollegiumLane:
    return {
        PortfolioExposure.CONTAINED: CollegiumLane.CONTAINMENT_PORTFOLIO,
        PortfolioExposure.GOVERNED: CollegiumLane.GOVERNANCE_PORTFOLIO,
        PortfolioExposure.EXPANSIVE: CollegiumLane.EXPANSION_PORTFOLIO,
    }[radar_entry.exposure]


def _status(clause: DoctrineClause) -> CollegiumStatus:
    return {
        DoctrineStatus.GUARDED: CollegiumStatus.RESERVED,
        DoctrineStatus.ADOPTED: CollegiumStatus.COORDINATING,
        DoctrineStatus.ENSHRINED: CollegiumStatus.DEPLOYED,
    }[clause.doctrine_status]


def _collegium_weight(clause: DoctrineClause, mission_profile: MissionProfile, radar_entry: PortfolioRadarEntry) -> float:
    return round(
        min(
            1.0,
            (clause.doctrine_strength + mission_profile.effective_observed_budget + radar_entry.budget_share) / 3.0,
        ),
        3,
    )


def _coordination_window(clause: DoctrineClause, mission_profile: MissionProfile, radar_entry: PortfolioRadarEntry) -> int:
    return max(clause.doctrine_window, radar_entry.review_window) + (1 if mission_profile.scenario is MissionScenario.CUTOVER else 0)


def build_missions_collegium(
    leitstern_doctrine: LeitsternDoctrine | None = None,
    portfolio_radar: PortfolioRadar | None = None,
    *,
    collegium_id: str = "missions-collegium",
) -> MissionsCollegium:
    """Build the mission collegium over Leitstern doctrine and portfolio radar."""

    resolved_doctrine = (
        build_leitstern_doctrine(doctrine_id=f"{collegium_id}-doctrine")
        if leitstern_doctrine is None
        else leitstern_doctrine
    )
    resolved_radar = build_portfolio_radar(radar_id=f"{collegium_id}-radar") if portfolio_radar is None else portfolio_radar
    seats = tuple(
        CollegiumSeat(
            seat_id=f"{collegium_id}-{clause.clause_id.removeprefix(f'{resolved_doctrine.doctrine_id}-')}",
            sequence=index,
            clause_id=clause.clause_id,
            mission_ref=mission_profile.mission_ref,
            radar_entry_id=radar_entry.entry_id,
            collegium_mandate=_mandate(clause),
            collegium_lane=_lane(radar_entry),
            collegium_status=_status(clause),
            mission_scenario=mission_profile.scenario,
            case_ids=tuple(dict.fromkeys((*clause.case_ids, *radar_entry.case_ids, mission_profile.mission_ref))),
            release_ready=clause.release_ready and radar_entry.release_ready,
            collegium_weight=_collegium_weight(clause, mission_profile, radar_entry),
            coordination_window=_coordination_window(clause, mission_profile, radar_entry),
            collegium_tags=tuple(
                dict.fromkeys(
                    (
                        *clause.doctrine_tags,
                        *radar_entry.control_tags,
                        mission_profile.scenario.value,
                        _mandate(clause).value,
                        _lane(radar_entry).value,
                        _status(clause).value,
                    )
                )
            ),
            summary=(
                f"{clause.clause_id} anchors mission {mission_profile.mission_ref} in "
                f"{_lane(radar_entry).value} as {_status(clause).value} collegium seat."
            ),
        )
        for index, clause in enumerate(resolved_doctrine.clauses, start=1)
        for mission_profile, radar_entry in [(_mission_profile(clause), _matching_radar_entry(clause, resolved_radar))]
    )
    if not seats:
        raise ValueError("missions collegium requires at least one seat")

    severity = "info"
    status = "collegium-deployed"
    if any(seat.collegium_status is CollegiumStatus.RESERVED for seat in seats):
        severity = "critical"
        status = "collegium-reserved"
    elif any(seat.collegium_status is CollegiumStatus.COORDINATING for seat in seats):
        severity = "warning"
        status = "collegium-coordinating"

    collegium_signal = TelemetrySignal(
        signal_name="missions-collegium",
        boundary=resolved_doctrine.doctrine_signal.boundary,
        correlation_id=collegium_id,
        severity=severity,
        status=status,
        metrics={
            "seat_count": float(len(seats)),
            "reserved_count": float(len([seat for seat in seats if seat.collegium_status is CollegiumStatus.RESERVED])),
            "coordinating_count": float(
                len([seat for seat in seats if seat.collegium_status is CollegiumStatus.COORDINATING])
            ),
            "deployed_count": float(len([seat for seat in seats if seat.collegium_status is CollegiumStatus.DEPLOYED])),
            "release_ready_count": float(len([seat for seat in seats if seat.release_ready])),
            "avg_collegium_weight": round(sum(seat.collegium_weight for seat in seats) / len(seats), 3),
        },
        labels={"collegium_id": collegium_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_doctrine.final_snapshot.runtime_stage,
        signals=(collegium_signal, resolved_radar.radar_signal, *resolved_doctrine.final_snapshot.signals),
        alerts=resolved_doctrine.final_snapshot.alerts,
        audit_entries=resolved_doctrine.final_snapshot.audit_entries,
        active_controls=resolved_doctrine.final_snapshot.active_controls,
    )
    return MissionsCollegium(
        collegium_id=collegium_id,
        leitstern_doctrine=resolved_doctrine,
        portfolio_radar=resolved_radar,
        seats=seats,
        collegium_signal=collegium_signal,
        final_snapshot=final_snapshot,
    )
