"""Formal operating constitution over program control, autonomy, and exceptions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .autonomy_governor import AutonomyDecision, AutonomyGovernor, build_autonomy_governor
from .exception_register import ExceptionRegister, build_exception_register
from .program_controller import ProgramController, ProgramTrack, ProgramTrackType, build_program_controller
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class ConstitutionPrinciple(str, Enum):
    """Core principles that govern the operating model."""

    STABILITY_FIRST = "stability-first"
    GOVERNED_CHANGE = "governed-change"
    BOUNDED_AUTONOMY = "bounded-autonomy"


class ConstitutionalAuthority(str, Enum):
    """Authority level granted by the operating constitution."""

    STEWARD = "steward"
    GOVERNANCE = "governance"
    AUTONOMY = "autonomy"


@dataclass(frozen=True)
class ConstitutionArticle:
    """One formal constitutional article over a program track."""

    article_id: str
    sequence: int
    track_id: str
    principle: ConstitutionPrinciple
    authority: ConstitutionalAuthority
    case_ids: tuple[str, ...]
    budget_ceiling: float
    escalation_limit: int
    execution_rights: tuple[str, ...]
    control_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "article_id", _non_empty(self.article_id, field_name="article_id"))
        object.__setattr__(self, "track_id", _non_empty(self.track_id, field_name="track_id"))
        object.__setattr__(self, "budget_ceiling", _clamp01(self.budget_ceiling))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.escalation_limit < 1:
            raise ValueError("escalation_limit must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "article_id": self.article_id,
            "sequence": self.sequence,
            "track_id": self.track_id,
            "principle": self.principle.value,
            "authority": self.authority.value,
            "case_ids": list(self.case_ids),
            "budget_ceiling": self.budget_ceiling,
            "escalation_limit": self.escalation_limit,
            "execution_rights": list(self.execution_rights),
            "control_tags": list(self.control_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class OperatingConstitution:
    """Formal operating constitution consolidating the control stack."""

    constitution_id: str
    program_controller: ProgramController
    autonomy_governor: AutonomyGovernor
    exception_register: ExceptionRegister
    articles: tuple[ConstitutionArticle, ...]
    constitution_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "constitution_id", _non_empty(self.constitution_id, field_name="constitution_id"))

    @property
    def steward_article_ids(self) -> tuple[str, ...]:
        return tuple(article.article_id for article in self.articles if article.authority is ConstitutionalAuthority.STEWARD)

    @property
    def governance_article_ids(self) -> tuple[str, ...]:
        return tuple(article.article_id for article in self.articles if article.authority is ConstitutionalAuthority.GOVERNANCE)

    @property
    def autonomy_article_ids(self) -> tuple[str, ...]:
        return tuple(article.article_id for article in self.articles if article.authority is ConstitutionalAuthority.AUTONOMY)

    def to_dict(self) -> dict[str, object]:
        return {
            "constitution_id": self.constitution_id,
            "program_controller": self.program_controller.to_dict(),
            "autonomy_governor": self.autonomy_governor.to_dict(),
            "exception_register": self.exception_register.to_dict(),
            "articles": [article.to_dict() for article in self.articles],
            "constitution_signal": self.constitution_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "steward_article_ids": list(self.steward_article_ids),
            "governance_article_ids": list(self.governance_article_ids),
            "autonomy_article_ids": list(self.autonomy_article_ids),
        }


def _principle_for_track(track: ProgramTrack) -> ConstitutionPrinciple:
    return {
        ProgramTrackType.RESILIENCE: ConstitutionPrinciple.STABILITY_FIRST,
        ProgramTrackType.GOVERNANCE: ConstitutionPrinciple.GOVERNED_CHANGE,
        ProgramTrackType.ROUTINE: ConstitutionPrinciple.BOUNDED_AUTONOMY,
    }[track.track_type]


def _authority_for_track(track: ProgramTrack) -> ConstitutionalAuthority:
    return {
        ProgramTrackType.RESILIENCE: ConstitutionalAuthority.STEWARD,
        ProgramTrackType.GOVERNANCE: ConstitutionalAuthority.GOVERNANCE,
        ProgramTrackType.ROUTINE: ConstitutionalAuthority.AUTONOMY,
    }[track.track_type]


def _budget_ceiling(track: ProgramTrack) -> float:
    base = {
        ProgramTrackType.RESILIENCE: 1.0,
        ProgramTrackType.GOVERNANCE: 0.65,
        ProgramTrackType.ROUTINE: 0.35,
    }[track.track_type]
    return round(max(base, track.priority_score), 3)


def _escalation_limit(track: ProgramTrack) -> int:
    return {
        ProgramTrackType.RESILIENCE: 1,
        ProgramTrackType.GOVERNANCE: 2,
        ProgramTrackType.ROUTINE: 3,
    }[track.track_type]


def _execution_rights(
    track: ProgramTrack,
    autonomy_governor: AutonomyGovernor,
) -> tuple[str, ...]:
    if track.track_type is ProgramTrackType.RESILIENCE:
        return ("containment-override", "rollback-authority", "exception-lock")
    if track.track_type is ProgramTrackType.GOVERNANCE:
        return ("approval-gate", "change-window-control", "policy-calibration")
    autonomous_cases = tuple(
        assignment.case_id for assignment in autonomy_governor.assignments if assignment.decision is AutonomyDecision.AUTONOMOUS
    )
    rights = ["bounded-execution", "telemetry-watch", "rollback-ready"]
    if autonomous_cases:
        rights.append("routine-scale-out")
    return tuple(rights)


def _article_control_tags(track: ProgramTrack, exception_case_ids: set[str]) -> tuple[str, ...]:
    tags = list(track.control_tags)
    if any(case_id in exception_case_ids for case_id in track.case_ids):
        tags.append("exception-bounded")
    return tuple(dict.fromkeys(tags))


def build_operating_constitution(
    program_controller: ProgramController | None = None,
    autonomy_governor: AutonomyGovernor | None = None,
    exception_register: ExceptionRegister | None = None,
    *,
    constitution_id: str = "operating-constitution",
) -> OperatingConstitution:
    """Build the formal operating constitution for the current control stack."""

    resolved_controller = (
        build_program_controller(controller_id=f"{constitution_id}-controller")
        if program_controller is None
        else program_controller
    )
    resolved_governor = (
        build_autonomy_governor(governor_id=f"{constitution_id}-governor")
        if autonomy_governor is None
        else autonomy_governor
    )
    resolved_exceptions = (
        build_exception_register(register_id=f"{constitution_id}-exceptions")
        if exception_register is None
        else exception_register
    )
    exception_case_ids = set(
        resolved_exceptions.policy_breach_case_ids
        + resolved_exceptions.unresolved_case_ids
        + resolved_exceptions.recurring_case_ids
    )
    articles = tuple(
        ConstitutionArticle(
            article_id=f"{constitution_id}-{track.track_type.value}",
            sequence=index,
            track_id=track.track_id,
            principle=_principle_for_track(track),
            authority=_authority_for_track(track),
            case_ids=track.case_ids,
            budget_ceiling=_budget_ceiling(track),
            escalation_limit=_escalation_limit(track),
            execution_rights=_execution_rights(track, resolved_governor),
            control_tags=_article_control_tags(track, exception_case_ids),
            summary=(
                f"{track.track_type.value} assigns {_authority_for_track(track).value} authority "
                f"to {len(track.case_ids)} case(s) under {_principle_for_track(track).value}."
            ),
        )
        for index, track in enumerate(resolved_controller.tracks, start=1)
    )
    if not articles:
        raise ValueError("operating constitution requires at least one article")

    severity = "info"
    status = "constitutionalized"
    if any(article.authority is ConstitutionalAuthority.STEWARD for article in articles):
        severity = "warning"
        status = "steward-chartered"
    if any(article.authority is ConstitutionalAuthority.AUTONOMY for article in articles):
        status = "bounded-autonomy-chartered"

    constitution_signal = TelemetrySignal(
        signal_name="operating-constitution",
        boundary=resolved_controller.controller_signal.boundary,
        correlation_id=constitution_id,
        severity=severity,
        status=status,
        metrics={
            "article_count": float(len(articles)),
            "steward_article_count": float(
                len([article for article in articles if article.authority is ConstitutionalAuthority.STEWARD])
            ),
            "governance_article_count": float(
                len([article for article in articles if article.authority is ConstitutionalAuthority.GOVERNANCE])
            ),
            "autonomy_article_count": float(
                len([article for article in articles if article.authority is ConstitutionalAuthority.AUTONOMY])
            ),
            "avg_budget_ceiling": round(sum(article.budget_ceiling for article in articles) / len(articles), 3),
        },
        labels={"constitution_id": constitution_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_controller.final_snapshot.runtime_stage,
        signals=(
            constitution_signal,
            resolved_controller.controller_signal,
            resolved_governor.governor_signal,
            resolved_exceptions.register_signal,
            *resolved_controller.final_snapshot.signals,
        ),
        alerts=resolved_controller.final_snapshot.alerts,
        audit_entries=resolved_controller.final_snapshot.audit_entries,
        active_controls=resolved_controller.final_snapshot.active_controls,
    )
    return OperatingConstitution(
        constitution_id=constitution_id,
        program_controller=resolved_controller,
        autonomy_governor=resolved_governor,
        exception_register=resolved_exceptions,
        articles=articles,
        constitution_signal=constitution_signal,
        final_snapshot=final_snapshot,
    )
