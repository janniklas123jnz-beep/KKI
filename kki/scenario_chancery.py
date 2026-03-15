"""Scenario chancery over portfolio radar entries and strategic option comparisons."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .portfolio_radar import (
    PortfolioConcentration,
    PortfolioExposure,
    PortfolioOperatingSpread,
    PortfolioRadar,
    PortfolioRadarEntry,
    build_portfolio_radar,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class ScenarioOfficeMode(str, Enum):
    """Strategic move category chosen by the scenario chancery."""

    STABILIZE = "stabilize"
    STEER = "steer"
    EXPAND = "expand"


class ScenarioOfficeStatus(str, Enum):
    """Decision readiness status for a scenario option."""

    LOCKED = "locked"
    REVIEW = "review"
    READY = "ready"


@dataclass(frozen=True)
class ScenarioOption:
    """Comparable scenario option derived from one portfolio radar entry."""

    option_id: str
    sequence: int
    radar_entry_id: str
    mode: ScenarioOfficeMode
    status: ScenarioOfficeStatus
    case_ids: tuple[str, ...]
    release_ready: bool
    comparison_score: float
    confidence_score: float
    review_window: int
    control_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "option_id", _non_empty(self.option_id, field_name="option_id"))
        object.__setattr__(self, "radar_entry_id", _non_empty(self.radar_entry_id, field_name="radar_entry_id"))
        object.__setattr__(self, "comparison_score", _clamp01(self.comparison_score))
        object.__setattr__(self, "confidence_score", _clamp01(self.confidence_score))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.review_window < 1:
            raise ValueError("review_window must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "option_id": self.option_id,
            "sequence": self.sequence,
            "radar_entry_id": self.radar_entry_id,
            "mode": self.mode.value,
            "status": self.status.value,
            "case_ids": list(self.case_ids),
            "release_ready": self.release_ready,
            "comparison_score": self.comparison_score,
            "confidence_score": self.confidence_score,
            "review_window": self.review_window,
            "control_tags": list(self.control_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class ScenarioChancery:
    """Strategic chancery that compares portfolio-driven scenario options."""

    chancery_id: str
    portfolio_radar: PortfolioRadar
    options: tuple[ScenarioOption, ...]
    chancery_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "chancery_id", _non_empty(self.chancery_id, field_name="chancery_id"))

    @property
    def locked_option_ids(self) -> tuple[str, ...]:
        return tuple(option.option_id for option in self.options if option.status is ScenarioOfficeStatus.LOCKED)

    @property
    def review_option_ids(self) -> tuple[str, ...]:
        return tuple(option.option_id for option in self.options if option.status is ScenarioOfficeStatus.REVIEW)

    @property
    def ready_option_ids(self) -> tuple[str, ...]:
        return tuple(option.option_id for option in self.options if option.status is ScenarioOfficeStatus.READY)

    def to_dict(self) -> dict[str, object]:
        return {
            "chancery_id": self.chancery_id,
            "portfolio_radar": self.portfolio_radar.to_dict(),
            "options": [option.to_dict() for option in self.options],
            "chancery_signal": self.chancery_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "locked_option_ids": list(self.locked_option_ids),
            "review_option_ids": list(self.review_option_ids),
            "ready_option_ids": list(self.ready_option_ids),
        }


def _mode_for_entry(entry: PortfolioRadarEntry) -> ScenarioOfficeMode:
    return {
        PortfolioExposure.CONTAINED: ScenarioOfficeMode.STABILIZE,
        PortfolioExposure.GOVERNED: ScenarioOfficeMode.STEER,
        PortfolioExposure.EXPANSIVE: ScenarioOfficeMode.EXPAND,
    }[entry.exposure]


def _status_for_entry(entry: PortfolioRadarEntry) -> ScenarioOfficeStatus:
    if entry.exposure is PortfolioExposure.CONTAINED:
        return ScenarioOfficeStatus.LOCKED
    if entry.exposure is PortfolioExposure.GOVERNED:
        return ScenarioOfficeStatus.REVIEW
    return ScenarioOfficeStatus.READY


def _comparison_score(entry: PortfolioRadarEntry) -> float:
    concentration = {
        PortfolioConcentration.CONCENTRATED: 0.92,
        PortfolioConcentration.BALANCED: 0.68,
        PortfolioConcentration.DISTRIBUTED: 0.44,
    }[entry.concentration]
    spread_bonus = {
        PortfolioOperatingSpread.NARROW: 0.03,
        PortfolioOperatingSpread.COORDINATED: 0.08,
        PortfolioOperatingSpread.BROAD: 0.14,
    }[entry.operating_spread]
    readiness_bonus = 0.08 if entry.release_ready else 0.0
    return round(concentration + spread_bonus + readiness_bonus, 3)


def _confidence_score(entry: PortfolioRadarEntry) -> float:
    exposure_base = {
        PortfolioExposure.CONTAINED: 0.9,
        PortfolioExposure.GOVERNED: 0.66,
        PortfolioExposure.EXPANSIVE: 0.52,
    }[entry.exposure]
    readiness_bonus = 0.14 if entry.release_ready else 0.0
    return round(exposure_base + readiness_bonus - (entry.budget_share * 0.1), 3)


def build_scenario_chancery(
    portfolio_radar: PortfolioRadar | None = None,
    *,
    chancery_id: str = "scenario-chancery",
) -> ScenarioChancery:
    """Build comparable strategic scenario options over the portfolio radar."""

    resolved_radar = build_portfolio_radar(radar_id=f"{chancery_id}-radar") if portfolio_radar is None else portfolio_radar
    options = tuple(
        ScenarioOption(
            option_id=f"{chancery_id}-{entry.entry_id.removeprefix(f'{resolved_radar.radar_id}-')}",
            sequence=index,
            radar_entry_id=entry.entry_id,
            mode=_mode_for_entry(entry),
            status=_status_for_entry(entry),
            case_ids=entry.case_ids,
            release_ready=entry.release_ready,
            comparison_score=_comparison_score(entry),
            confidence_score=_confidence_score(entry),
            review_window=entry.review_window,
            control_tags=tuple(
                dict.fromkeys(
                    (
                        *entry.control_tags,
                        _mode_for_entry(entry).value,
                        _status_for_entry(entry).value,
                    )
                )
            ),
            summary=(
                f"{entry.entry_id} compares as {_mode_for_entry(entry).value} "
                f"with {_status_for_entry(entry).value} chancery posture."
            ),
        )
        for index, entry in enumerate(resolved_radar.entries, start=1)
    )
    if not options:
        raise ValueError("scenario chancery requires at least one option")

    severity = "info"
    status = "scenario-ready"
    if any(option.status is ScenarioOfficeStatus.LOCKED for option in options):
        severity = "critical"
        status = "scenario-locked"
    elif any(option.status is ScenarioOfficeStatus.REVIEW for option in options):
        severity = "warning"
        status = "scenario-review"

    chancery_signal = TelemetrySignal(
        signal_name="scenario-chancery",
        boundary=resolved_radar.radar_signal.boundary,
        correlation_id=chancery_id,
        severity=severity,
        status=status,
        metrics={
            "option_count": float(len(options)),
            "locked_count": float(len([option for option in options if option.status is ScenarioOfficeStatus.LOCKED])),
            "review_count": float(len([option for option in options if option.status is ScenarioOfficeStatus.REVIEW])),
            "ready_count": float(len([option for option in options if option.status is ScenarioOfficeStatus.READY])),
            "release_ready_count": float(len([option for option in options if option.release_ready])),
            "avg_comparison_score": round(sum(option.comparison_score for option in options) / len(options), 3),
        },
        labels={"chancery_id": chancery_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_radar.final_snapshot.runtime_stage,
        signals=(chancery_signal, *resolved_radar.final_snapshot.signals),
        alerts=resolved_radar.final_snapshot.alerts,
        audit_entries=resolved_radar.final_snapshot.audit_entries,
        active_controls=resolved_radar.final_snapshot.active_controls,
    )
    return ScenarioChancery(
        chancery_id=chancery_id,
        portfolio_radar=resolved_radar,
        options=options,
        chancery_signal=chancery_signal,
        final_snapshot=final_snapshot,
    )
