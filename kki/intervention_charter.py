"""Intervention charter over retained guideline vectors and release gates."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .guideline_compass import (
    CompassStatus,
    GuidelineCompass,
    GuidelinePrinciple,
    GuidelineVector,
    build_guideline_compass,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class InterventionRight(str, Enum):
    """Formal right to intervene on one strategic lane."""

    STEWARD_VETO = "steward-veto"
    GOVERNANCE_REVIEW = "governance-review"
    AUTONOMY_WINDOW = "autonomy-window"


class StopCondition(str, Enum):
    """Condition that forces an intervention stop."""

    HARD_BOUNDARY_BREACH = "hard-boundary-breach"
    CORRIDOR_DEVIATION = "corridor-deviation"
    WINDOW_EXHAUSTED = "window-exhausted"


class ReleaseThreshold(str, Enum):
    """Threshold required before the lane may proceed."""

    EXECUTIVE_OVERRIDE = "executive-override"
    GOVERNANCE_CLEARANCE = "governance-clearance"
    READINESS_QUORUM = "readiness-quorum"


class CharterStatus(str, Enum):
    """Current operating posture for one charter clause."""

    RESTRICTED = "restricted"
    GUARDED = "guarded"
    ENABLED = "enabled"


@dataclass(frozen=True)
class InterventionClause:
    """One charter clause built from a retained guideline vector."""

    clause_id: str
    sequence: int
    vector_id: str
    principle: GuidelinePrinciple
    intervention_right: InterventionRight
    stop_condition: StopCondition
    release_threshold: ReleaseThreshold
    charter_status: CharterStatus
    case_ids: tuple[str, ...]
    release_ready: bool
    approval_floor: float
    intervention_score: float
    charter_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "clause_id", _non_empty(self.clause_id, field_name="clause_id"))
        object.__setattr__(self, "vector_id", _non_empty(self.vector_id, field_name="vector_id"))
        object.__setattr__(self, "approval_floor", _clamp01(self.approval_floor))
        object.__setattr__(self, "intervention_score", _clamp01(self.intervention_score))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "clause_id": self.clause_id,
            "sequence": self.sequence,
            "vector_id": self.vector_id,
            "principle": self.principle.value,
            "intervention_right": self.intervention_right.value,
            "stop_condition": self.stop_condition.value,
            "release_threshold": self.release_threshold.value,
            "charter_status": self.charter_status.value,
            "case_ids": list(self.case_ids),
            "release_ready": self.release_ready,
            "approval_floor": self.approval_floor,
            "intervention_score": self.intervention_score,
            "charter_tags": list(self.charter_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class InterventionCharter:
    """Strategic charter that formalizes intervention rights and release gates."""

    charter_id: str
    guideline_compass: GuidelineCompass
    clauses: tuple[InterventionClause, ...]
    charter_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "charter_id", _non_empty(self.charter_id, field_name="charter_id"))

    @property
    def restricted_clause_ids(self) -> tuple[str, ...]:
        return tuple(clause.clause_id for clause in self.clauses if clause.charter_status is CharterStatus.RESTRICTED)

    @property
    def guarded_clause_ids(self) -> tuple[str, ...]:
        return tuple(clause.clause_id for clause in self.clauses if clause.charter_status is CharterStatus.GUARDED)

    @property
    def enabled_clause_ids(self) -> tuple[str, ...]:
        return tuple(clause.clause_id for clause in self.clauses if clause.charter_status is CharterStatus.ENABLED)

    def to_dict(self) -> dict[str, object]:
        return {
            "charter_id": self.charter_id,
            "guideline_compass": self.guideline_compass.to_dict(),
            "clauses": [clause.to_dict() for clause in self.clauses],
            "charter_signal": self.charter_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "restricted_clause_ids": list(self.restricted_clause_ids),
            "guarded_clause_ids": list(self.guarded_clause_ids),
            "enabled_clause_ids": list(self.enabled_clause_ids),
        }


def _intervention_right_for_vector(vector: GuidelineVector) -> InterventionRight:
    return {
        GuidelinePrinciple.STABILITY_FIRST: InterventionRight.STEWARD_VETO,
        GuidelinePrinciple.GOVERNED_PROGRESS: InterventionRight.GOVERNANCE_REVIEW,
        GuidelinePrinciple.BOUNDED_EXPANSION: InterventionRight.AUTONOMY_WINDOW,
    }[vector.principle]


def _stop_condition_for_vector(vector: GuidelineVector) -> StopCondition:
    return {
        CompassStatus.ANCHORED: StopCondition.HARD_BOUNDARY_BREACH,
        CompassStatus.GUIDED: StopCondition.CORRIDOR_DEVIATION,
        CompassStatus.OPEN: StopCondition.WINDOW_EXHAUSTED,
    }[vector.compass_status]


def _release_threshold_for_vector(vector: GuidelineVector) -> ReleaseThreshold:
    return {
        CompassStatus.ANCHORED: ReleaseThreshold.EXECUTIVE_OVERRIDE,
        CompassStatus.GUIDED: ReleaseThreshold.GOVERNANCE_CLEARANCE,
        CompassStatus.OPEN: ReleaseThreshold.READINESS_QUORUM,
    }[vector.compass_status]


def _charter_status_for_vector(vector: GuidelineVector) -> CharterStatus:
    return {
        CompassStatus.ANCHORED: CharterStatus.RESTRICTED,
        CompassStatus.GUIDED: CharterStatus.GUARDED,
        CompassStatus.OPEN: CharterStatus.ENABLED,
    }[vector.compass_status]


def _approval_floor(vector: GuidelineVector) -> float:
    if vector.compass_status is CompassStatus.ANCHORED:
        return 1.0
    if vector.compass_status is CompassStatus.GUIDED:
        return 0.67
    return 0.6 if vector.release_ready else 0.75


def _intervention_score(vector: GuidelineVector) -> float:
    return round((vector.guidance_score + _approval_floor(vector)) / 2.0, 3)


def build_intervention_charter(
    guideline_compass: GuidelineCompass | None = None,
    *,
    charter_id: str = "intervention-charter",
) -> InterventionCharter:
    """Build the intervention charter from retained guideline vectors."""

    resolved_compass = (
        build_guideline_compass(compass_id=f"{charter_id}-compass")
        if guideline_compass is None
        else guideline_compass
    )
    clauses = tuple(
        InterventionClause(
            clause_id=f"{charter_id}-{vector.vector_id.removeprefix(f'{resolved_compass.compass_id}-')}",
            sequence=index,
            vector_id=vector.vector_id,
            principle=vector.principle,
            intervention_right=_intervention_right_for_vector(vector),
            stop_condition=_stop_condition_for_vector(vector),
            release_threshold=_release_threshold_for_vector(vector),
            charter_status=_charter_status_for_vector(vector),
            case_ids=vector.case_ids,
            release_ready=vector.release_ready,
            approval_floor=_approval_floor(vector),
            intervention_score=_intervention_score(vector),
            charter_tags=tuple(
                dict.fromkeys(
                    (
                        *vector.control_tags,
                        _intervention_right_for_vector(vector).value,
                        _stop_condition_for_vector(vector).value,
                        _release_threshold_for_vector(vector).value,
                        _charter_status_for_vector(vector).value,
                    )
                )
            ),
            summary=(
                f"{vector.vector_id} grants {_intervention_right_for_vector(vector).value} "
                f"until {_stop_condition_for_vector(vector).value} under "
                f"{_release_threshold_for_vector(vector).value}."
            ),
        )
        for index, vector in enumerate(resolved_compass.vectors, start=1)
    )
    if not clauses:
        raise ValueError("intervention charter requires at least one clause")

    severity = "info"
    status = "charter-enabled"
    if any(clause.charter_status is CharterStatus.RESTRICTED for clause in clauses):
        severity = "critical"
        status = "charter-restricted"
    elif any(clause.charter_status is CharterStatus.GUARDED for clause in clauses):
        severity = "warning"
        status = "charter-guarded"

    charter_signal = TelemetrySignal(
        signal_name="intervention-charter",
        boundary=resolved_compass.compass_signal.boundary,
        correlation_id=charter_id,
        severity=severity,
        status=status,
        metrics={
            "clause_count": float(len(clauses)),
            "restricted_count": float(len([clause for clause in clauses if clause.charter_status is CharterStatus.RESTRICTED])),
            "guarded_count": float(len([clause for clause in clauses if clause.charter_status is CharterStatus.GUARDED])),
            "enabled_count": float(len([clause for clause in clauses if clause.charter_status is CharterStatus.ENABLED])),
            "release_ready_count": float(len([clause for clause in clauses if clause.release_ready])),
            "avg_intervention_score": round(
                sum(clause.intervention_score for clause in clauses) / len(clauses),
                3,
            ),
        },
        labels={"charter_id": charter_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_compass.final_snapshot.runtime_stage,
        signals=(charter_signal, *resolved_compass.final_snapshot.signals),
        alerts=resolved_compass.final_snapshot.alerts,
        audit_entries=resolved_compass.final_snapshot.audit_entries,
        active_controls=resolved_compass.final_snapshot.active_controls,
    )
    return InterventionCharter(
        charter_id=charter_id,
        guideline_compass=resolved_compass,
        clauses=clauses,
        charter_signal=charter_signal,
        final_snapshot=final_snapshot,
    )
