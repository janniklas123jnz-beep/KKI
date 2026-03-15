"""Course corrector over scenario options and portfolio stress indicators."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .portfolio_radar import (
    PortfolioConcentration,
    PortfolioExposure,
    PortfolioOperatingSpread,
    PortfolioRadar,
)
from .scenario_chancery import (
    ScenarioChancery,
    ScenarioOfficeMode,
    ScenarioOfficeStatus,
    ScenarioOption,
    build_scenario_chancery,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class CourseCorrectionAction(str, Enum):
    """Deterministic course-correction moves for strategic options."""

    CONTAIN = "contain"
    REBALANCE = "rebalance"
    ACCELERATE = "accelerate"


class CourseCorrectionStatus(str, Enum):
    """Execution posture of a course-correction directive."""

    ENFORCED = "enforced"
    DIRECTED = "directed"
    CLEARED = "cleared"


@dataclass(frozen=True)
class CourseCorrectionDirective:
    """Resolved course-correction directive for one scenario option."""

    directive_id: str
    sequence: int
    option_id: str
    radar_entry_id: str
    action: CourseCorrectionAction
    status: CourseCorrectionStatus
    case_ids: tuple[str, ...]
    release_ready: bool
    correction_score: float
    stress_index: float
    review_window: int
    control_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "directive_id", _non_empty(self.directive_id, field_name="directive_id"))
        object.__setattr__(self, "option_id", _non_empty(self.option_id, field_name="option_id"))
        object.__setattr__(self, "radar_entry_id", _non_empty(self.radar_entry_id, field_name="radar_entry_id"))
        object.__setattr__(self, "correction_score", _clamp01(self.correction_score))
        object.__setattr__(self, "stress_index", _clamp01(self.stress_index))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.review_window < 1:
            raise ValueError("review_window must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "directive_id": self.directive_id,
            "sequence": self.sequence,
            "option_id": self.option_id,
            "radar_entry_id": self.radar_entry_id,
            "action": self.action.value,
            "status": self.status.value,
            "case_ids": list(self.case_ids),
            "release_ready": self.release_ready,
            "correction_score": self.correction_score,
            "stress_index": self.stress_index,
            "review_window": self.review_window,
            "control_tags": list(self.control_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class CourseCorrector:
    """Deterministic course corrector over scenarios and portfolio stress."""

    corrector_id: str
    scenario_chancery: ScenarioChancery
    portfolio_radar: PortfolioRadar
    directives: tuple[CourseCorrectionDirective, ...]
    corrector_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "corrector_id", _non_empty(self.corrector_id, field_name="corrector_id"))

    @property
    def enforced_directive_ids(self) -> tuple[str, ...]:
        return tuple(
            directive.directive_id for directive in self.directives if directive.status is CourseCorrectionStatus.ENFORCED
        )

    @property
    def directed_directive_ids(self) -> tuple[str, ...]:
        return tuple(
            directive.directive_id for directive in self.directives if directive.status is CourseCorrectionStatus.DIRECTED
        )

    @property
    def cleared_directive_ids(self) -> tuple[str, ...]:
        return tuple(
            directive.directive_id for directive in self.directives if directive.status is CourseCorrectionStatus.CLEARED
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "corrector_id": self.corrector_id,
            "scenario_chancery": self.scenario_chancery.to_dict(),
            "portfolio_radar": self.portfolio_radar.to_dict(),
            "directives": [directive.to_dict() for directive in self.directives],
            "corrector_signal": self.corrector_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "enforced_directive_ids": list(self.enforced_directive_ids),
            "directed_directive_ids": list(self.directed_directive_ids),
            "cleared_directive_ids": list(self.cleared_directive_ids),
        }


def _stress_index(option: ScenarioOption, radar: PortfolioRadar) -> float:
    entry = next(item for item in radar.entries if item.entry_id == option.radar_entry_id)
    concentration = {
        PortfolioConcentration.CONCENTRATED: 0.78,
        PortfolioConcentration.BALANCED: 0.52,
        PortfolioConcentration.DISTRIBUTED: 0.28,
    }[entry.concentration]
    exposure = {
        PortfolioExposure.CONTAINED: 0.2,
        PortfolioExposure.GOVERNED: 0.12,
        PortfolioExposure.EXPANSIVE: 0.04,
    }[entry.exposure]
    spread = {
        PortfolioOperatingSpread.NARROW: 0.12,
        PortfolioOperatingSpread.COORDINATED: 0.08,
        PortfolioOperatingSpread.BROAD: 0.04,
    }[entry.operating_spread]
    return round(concentration + exposure + spread - (0.06 if option.release_ready else 0.0), 3)


def _action_for_option(option: ScenarioOption) -> CourseCorrectionAction:
    return {
        ScenarioOfficeMode.STABILIZE: CourseCorrectionAction.CONTAIN,
        ScenarioOfficeMode.STEER: CourseCorrectionAction.REBALANCE,
        ScenarioOfficeMode.EXPAND: CourseCorrectionAction.ACCELERATE,
    }[option.mode]


def _status_for_option(option: ScenarioOption) -> CourseCorrectionStatus:
    return {
        ScenarioOfficeStatus.LOCKED: CourseCorrectionStatus.ENFORCED,
        ScenarioOfficeStatus.REVIEW: CourseCorrectionStatus.DIRECTED,
        ScenarioOfficeStatus.READY: CourseCorrectionStatus.CLEARED,
    }[option.status]


def _correction_score(option: ScenarioOption, stress_index: float) -> float:
    return round(max(option.comparison_score, stress_index), 3)


def build_course_corrector(
    scenario_chancery: ScenarioChancery | None = None,
    portfolio_radar: PortfolioRadar | None = None,
    *,
    corrector_id: str = "course-corrector",
) -> CourseCorrector:
    """Build deterministic course-correction directives over scenario options."""

    resolved_chancery = (
        build_scenario_chancery(chancery_id=f"{corrector_id}-chancery") if scenario_chancery is None else scenario_chancery
    )
    resolved_radar = resolved_chancery.portfolio_radar if portfolio_radar is None else portfolio_radar
    directives = tuple(
        CourseCorrectionDirective(
            directive_id=f"{corrector_id}-{option.option_id.removeprefix(f'{resolved_chancery.chancery_id}-')}",
            sequence=index,
            option_id=option.option_id,
            radar_entry_id=option.radar_entry_id,
            action=_action_for_option(option),
            status=_status_for_option(option),
            case_ids=option.case_ids,
            release_ready=option.release_ready,
            correction_score=_correction_score(option, _stress_index(option, resolved_radar)),
            stress_index=_stress_index(option, resolved_radar),
            review_window=option.review_window,
            control_tags=tuple(
                dict.fromkeys(
                    (
                        *option.control_tags,
                        _action_for_option(option).value,
                        _status_for_option(option).value,
                    )
                )
            ),
            summary=(
                f"{option.option_id} is corrected via {_action_for_option(option).value} "
                f"with {_status_for_option(option).value} status."
            ),
        )
        for index, option in enumerate(resolved_chancery.options, start=1)
    )
    if not directives:
        raise ValueError("course corrector requires at least one directive")

    severity = "info"
    status = "course-cleared"
    if any(directive.status is CourseCorrectionStatus.ENFORCED for directive in directives):
        severity = "critical"
        status = "course-enforced"
    elif any(directive.status is CourseCorrectionStatus.DIRECTED for directive in directives):
        severity = "warning"
        status = "course-directed"

    corrector_signal = TelemetrySignal(
        signal_name="course-corrector",
        boundary=resolved_chancery.chancery_signal.boundary,
        correlation_id=corrector_id,
        severity=severity,
        status=status,
        metrics={
            "directive_count": float(len(directives)),
            "enforced_count": float(
                len([directive for directive in directives if directive.status is CourseCorrectionStatus.ENFORCED])
            ),
            "directed_count": float(
                len([directive for directive in directives if directive.status is CourseCorrectionStatus.DIRECTED])
            ),
            "cleared_count": float(
                len([directive for directive in directives if directive.status is CourseCorrectionStatus.CLEARED])
            ),
            "release_ready_count": float(len([directive for directive in directives if directive.release_ready])),
            "avg_stress_index": round(sum(directive.stress_index for directive in directives) / len(directives), 3),
        },
        labels={"corrector_id": corrector_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_chancery.final_snapshot.runtime_stage,
        signals=(corrector_signal, *resolved_chancery.final_snapshot.signals),
        alerts=resolved_chancery.final_snapshot.alerts,
        audit_entries=resolved_chancery.final_snapshot.audit_entries,
        active_controls=resolved_chancery.final_snapshot.active_controls,
    )
    return CourseCorrector(
        corrector_id=corrector_id,
        scenario_chancery=resolved_chancery,
        portfolio_radar=resolved_radar,
        directives=directives,
        corrector_signal=corrector_signal,
        final_snapshot=final_snapshot,
    )
