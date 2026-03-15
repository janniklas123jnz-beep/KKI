"""Portfolio radar over mandate cards, concentration, exposure, and operating spread."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .mandate_card_deck import MandateCard, MandateCardDeck, MandateExecutionScope, build_mandate_card_deck
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class PortfolioConcentration(str, Enum):
    """Portfolio concentration band for one strategic lane."""

    CONCENTRATED = "concentrated"
    BALANCED = "balanced"
    DISTRIBUTED = "distributed"


class PortfolioExposure(str, Enum):
    """Exposure posture visible in the portfolio radar."""

    CONTAINED = "contained"
    GOVERNED = "governed"
    EXPANSIVE = "expansive"


class PortfolioOperatingSpread(str, Enum):
    """Operational spread of one mandate lane."""

    NARROW = "narrow"
    COORDINATED = "coordinated"
    BROAD = "broad"


@dataclass(frozen=True)
class PortfolioRadarEntry:
    """One radar view over a mandate lane."""

    entry_id: str
    sequence: int
    card_id: str
    concentration: PortfolioConcentration
    exposure: PortfolioExposure
    operating_spread: PortfolioOperatingSpread
    case_ids: tuple[str, ...]
    release_ready: bool
    budget_share: float
    review_window: int
    control_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "entry_id", _non_empty(self.entry_id, field_name="entry_id"))
        object.__setattr__(self, "card_id", _non_empty(self.card_id, field_name="card_id"))
        object.__setattr__(self, "budget_share", _clamp01(self.budget_share))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.review_window < 1:
            raise ValueError("review_window must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "entry_id": self.entry_id,
            "sequence": self.sequence,
            "card_id": self.card_id,
            "concentration": self.concentration.value,
            "exposure": self.exposure.value,
            "operating_spread": self.operating_spread.value,
            "case_ids": list(self.case_ids),
            "release_ready": self.release_ready,
            "budget_share": self.budget_share,
            "review_window": self.review_window,
            "control_tags": list(self.control_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class PortfolioRadar:
    """Radar view over strategic mandate cards."""

    radar_id: str
    mandate_card_deck: MandateCardDeck
    entries: tuple[PortfolioRadarEntry, ...]
    radar_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "radar_id", _non_empty(self.radar_id, field_name="radar_id"))

    @property
    def concentrated_entry_ids(self) -> tuple[str, ...]:
        return tuple(entry.entry_id for entry in self.entries if entry.concentration is PortfolioConcentration.CONCENTRATED)

    @property
    def governed_entry_ids(self) -> tuple[str, ...]:
        return tuple(entry.entry_id for entry in self.entries if entry.exposure is PortfolioExposure.GOVERNED)

    @property
    def expansive_entry_ids(self) -> tuple[str, ...]:
        return tuple(entry.entry_id for entry in self.entries if entry.exposure is PortfolioExposure.EXPANSIVE)

    def to_dict(self) -> dict[str, object]:
        return {
            "radar_id": self.radar_id,
            "mandate_card_deck": self.mandate_card_deck.to_dict(),
            "entries": [entry.to_dict() for entry in self.entries],
            "radar_signal": self.radar_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "concentrated_entry_ids": list(self.concentrated_entry_ids),
            "governed_entry_ids": list(self.governed_entry_ids),
            "expansive_entry_ids": list(self.expansive_entry_ids),
        }


def _concentration_for_card(card: MandateCard, total_budget: float) -> PortfolioConcentration:
    share = card.execution_budget / total_budget if total_budget > 0.0 else 0.0
    if share >= 0.4:
        return PortfolioConcentration.CONCENTRATED
    if share >= 0.25:
        return PortfolioConcentration.BALANCED
    return PortfolioConcentration.DISTRIBUTED


def _exposure_for_card(card: MandateCard) -> PortfolioExposure:
    return {
        MandateExecutionScope.CONTAINMENT: PortfolioExposure.CONTAINED,
        MandateExecutionScope.GOVERNED_CHANGE: PortfolioExposure.GOVERNED,
        MandateExecutionScope.BOUNDED_EXPANSION: PortfolioExposure.EXPANSIVE,
    }[card.execution_scope]


def _operating_spread_for_card(card: MandateCard) -> PortfolioOperatingSpread:
    if card.review_window <= 1:
        return PortfolioOperatingSpread.NARROW
    if card.review_window <= 3:
        return PortfolioOperatingSpread.COORDINATED
    return PortfolioOperatingSpread.BROAD


def build_portfolio_radar(
    mandate_card_deck: MandateCardDeck | None = None,
    *,
    radar_id: str = "portfolio-radar",
) -> PortfolioRadar:
    """Build a portfolio radar over the mandate card deck."""

    resolved_deck = build_mandate_card_deck(deck_id=f"{radar_id}-deck") if mandate_card_deck is None else mandate_card_deck
    total_budget = sum(card.execution_budget for card in resolved_deck.cards)
    entries = tuple(
        PortfolioRadarEntry(
            entry_id=f"{radar_id}-{card.card_id.removeprefix(f'{resolved_deck.deck_id}-')}",
            sequence=index,
            card_id=card.card_id,
            concentration=_concentration_for_card(card, total_budget),
            exposure=_exposure_for_card(card),
            operating_spread=_operating_spread_for_card(card),
            case_ids=card.case_ids,
            release_ready=card.release_ready,
            budget_share=round(card.execution_budget / total_budget, 3) if total_budget > 0.0 else 0.0,
            review_window=card.review_window,
            control_tags=tuple(
                dict.fromkeys(
                    (
                        *card.ownership_tags,
                        _concentration_for_card(card, total_budget).value,
                        _exposure_for_card(card).value,
                        _operating_spread_for_card(card).value,
                    )
                )
            ),
            summary=(
                f"{card.card_id} appears as {_concentration_for_card(card, total_budget).value} "
                f"with {_exposure_for_card(card).value} exposure and {_operating_spread_for_card(card).value} spread."
            ),
        )
        for index, card in enumerate(resolved_deck.cards, start=1)
    )
    if not entries:
        raise ValueError("portfolio radar requires at least one entry")

    severity = "info"
    status = "portfolio-distributed"
    if any(entry.concentration is PortfolioConcentration.CONCENTRATED for entry in entries):
        severity = "critical"
        status = "portfolio-concentrated"
    elif any(entry.exposure is PortfolioExposure.GOVERNED for entry in entries):
        severity = "warning"
        status = "portfolio-governed"

    radar_signal = TelemetrySignal(
        signal_name="portfolio-radar",
        boundary=resolved_deck.deck_signal.boundary,
        correlation_id=radar_id,
        severity=severity,
        status=status,
        metrics={
            "entry_count": float(len(entries)),
            "concentrated_count": float(
                len([entry for entry in entries if entry.concentration is PortfolioConcentration.CONCENTRATED])
            ),
            "governed_exposure_count": float(
                len([entry for entry in entries if entry.exposure is PortfolioExposure.GOVERNED])
            ),
            "expansive_count": float(len([entry for entry in entries if entry.exposure is PortfolioExposure.EXPANSIVE])),
            "release_ready_count": float(len([entry for entry in entries if entry.release_ready])),
            "avg_budget_share": round(sum(entry.budget_share for entry in entries) / len(entries), 3),
        },
        labels={"radar_id": radar_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_deck.final_snapshot.runtime_stage,
        signals=(radar_signal, *resolved_deck.final_snapshot.signals),
        alerts=resolved_deck.final_snapshot.alerts,
        audit_entries=resolved_deck.final_snapshot.audit_entries,
        active_controls=resolved_deck.final_snapshot.active_controls,
    )
    return PortfolioRadar(
        radar_id=radar_id,
        mandate_card_deck=resolved_deck,
        entries=entries,
        radar_signal=radar_signal,
        final_snapshot=final_snapshot,
    )
