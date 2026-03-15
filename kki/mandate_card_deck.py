"""Mandate card deck over strategic lanes, ownership, and review cadence."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .operating_constitution import ConstitutionalAuthority
from .strategy_council import (
    StrategyCouncil,
    StrategyCouncilStatus,
    StrategyEscalationMandate,
    StrategyLane,
    StrategyMandate,
    build_strategy_council,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class MandateExecutionScope(str, Enum):
    """Execution scope granted to one mandate card."""

    CONTAINMENT = "containment-scope"
    GOVERNED_CHANGE = "governed-change-scope"
    BOUNDED_EXPANSION = "bounded-expansion-scope"


class MandateReviewCadence(str, Enum):
    """Review cadence attached to a mandate card."""

    INCIDENT = "incident-cadence"
    GOVERNANCE = "governance-cadence"
    EXPANSION = "expansion-cadence"


@dataclass(frozen=True)
class MandateCard:
    """Explicit operating card for one strategic mandate."""

    card_id: str
    sequence: int
    mandate_id: str
    lane: StrategyLane
    owner: ConstitutionalAuthority
    execution_scope: MandateExecutionScope
    review_cadence: MandateReviewCadence
    case_ids: tuple[str, ...]
    release_ready: bool
    execution_budget: float
    review_window: int
    ownership_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "card_id", _non_empty(self.card_id, field_name="card_id"))
        object.__setattr__(self, "mandate_id", _non_empty(self.mandate_id, field_name="mandate_id"))
        object.__setattr__(self, "execution_budget", _clamp01(self.execution_budget))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.review_window < 1:
            raise ValueError("review_window must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "card_id": self.card_id,
            "sequence": self.sequence,
            "mandate_id": self.mandate_id,
            "lane": self.lane.value,
            "owner": self.owner.value,
            "execution_scope": self.execution_scope.value,
            "review_cadence": self.review_cadence.value,
            "case_ids": list(self.case_ids),
            "release_ready": self.release_ready,
            "execution_budget": self.execution_budget,
            "review_window": self.review_window,
            "ownership_tags": list(self.ownership_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class MandateCardDeck:
    """Structured deck of mandate cards derived from the strategy council."""

    deck_id: str
    strategy_council: StrategyCouncil
    cards: tuple[MandateCard, ...]
    deck_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "deck_id", _non_empty(self.deck_id, field_name="deck_id"))

    @property
    def steward_card_ids(self) -> tuple[str, ...]:
        return tuple(card.card_id for card in self.cards if card.owner is ConstitutionalAuthority.STEWARD)

    @property
    def governance_card_ids(self) -> tuple[str, ...]:
        return tuple(card.card_id for card in self.cards if card.owner is ConstitutionalAuthority.GOVERNANCE)

    @property
    def autonomy_card_ids(self) -> tuple[str, ...]:
        return tuple(card.card_id for card in self.cards if card.owner is ConstitutionalAuthority.AUTONOMY)

    def to_dict(self) -> dict[str, object]:
        return {
            "deck_id": self.deck_id,
            "strategy_council": self.strategy_council.to_dict(),
            "cards": [card.to_dict() for card in self.cards],
            "deck_signal": self.deck_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "steward_card_ids": list(self.steward_card_ids),
            "governance_card_ids": list(self.governance_card_ids),
            "autonomy_card_ids": list(self.autonomy_card_ids),
        }


def _owner_for_mandate(mandate: StrategyMandate) -> ConstitutionalAuthority:
    return {
        StrategyLane.STABILITY: ConstitutionalAuthority.STEWARD,
        StrategyLane.GOVERNANCE: ConstitutionalAuthority.GOVERNANCE,
        StrategyLane.EXPANSION: ConstitutionalAuthority.AUTONOMY,
    }[mandate.lane]


def _scope_for_mandate(mandate: StrategyMandate) -> MandateExecutionScope:
    return {
        StrategyEscalationMandate.CONTAINMENT: MandateExecutionScope.CONTAINMENT,
        StrategyEscalationMandate.REVIEW: MandateExecutionScope.GOVERNED_CHANGE,
        StrategyEscalationMandate.EXPANSION: MandateExecutionScope.BOUNDED_EXPANSION,
    }[mandate.escalation_mandate]


def _cadence_for_mandate(mandate: StrategyMandate) -> MandateReviewCadence:
    return {
        StrategyCouncilStatus.ESCALATED: MandateReviewCadence.INCIDENT,
        StrategyCouncilStatus.ORCHESTRATED: MandateReviewCadence.GOVERNANCE,
        StrategyCouncilStatus.PRIMED: MandateReviewCadence.EXPANSION,
    }[mandate.council_status]


def build_mandate_card_deck(
    strategy_council: StrategyCouncil | None = None,
    *,
    deck_id: str = "mandate-card-deck",
) -> MandateCardDeck:
    """Build explicit mandate cards from the strategy council lanes."""

    resolved_council = (
        build_strategy_council(council_id=f"{deck_id}-council") if strategy_council is None else strategy_council
    )
    cards = tuple(
        MandateCard(
            card_id=f"{deck_id}-{mandate.lane.value}",
            sequence=index,
            mandate_id=mandate.mandate_id,
            lane=mandate.lane,
            owner=_owner_for_mandate(mandate),
            execution_scope=_scope_for_mandate(mandate),
            review_cadence=_cadence_for_mandate(mandate),
            case_ids=mandate.case_ids,
            release_ready=mandate.release_ready,
            execution_budget=mandate.strategic_budget,
            review_window=mandate.review_window,
            ownership_tags=tuple(
                dict.fromkeys(
                    (
                        *mandate.control_tags,
                        _owner_for_mandate(mandate).value,
                        _scope_for_mandate(mandate).value,
                        _cadence_for_mandate(mandate).value,
                    )
                )
            ),
            summary=(
                f"{mandate.lane.value} is owned by {_owner_for_mandate(mandate).value} "
                f"with {_scope_for_mandate(mandate).value} under {_cadence_for_mandate(mandate).value}."
            ),
        )
        for index, mandate in enumerate(resolved_council.mandates, start=1)
    )
    if not cards:
        raise ValueError("mandate card deck requires at least one card")

    severity = "info"
    status = "mandate-expansion-owned"
    if any(card.owner is ConstitutionalAuthority.STEWARD for card in cards):
        severity = "critical"
        status = "mandate-containment-owned"
    elif any(card.owner is ConstitutionalAuthority.GOVERNANCE for card in cards):
        severity = "warning"
        status = "mandate-governed"

    deck_signal = TelemetrySignal(
        signal_name="mandate-card-deck",
        boundary=resolved_council.council_signal.boundary,
        correlation_id=deck_id,
        severity=severity,
        status=status,
        metrics={
            "card_count": float(len(cards)),
            "steward_card_count": float(len([card for card in cards if card.owner is ConstitutionalAuthority.STEWARD])),
            "governance_card_count": float(
                len([card for card in cards if card.owner is ConstitutionalAuthority.GOVERNANCE])
            ),
            "autonomy_card_count": float(len([card for card in cards if card.owner is ConstitutionalAuthority.AUTONOMY])),
            "release_ready_count": float(len([card for card in cards if card.release_ready])),
            "avg_execution_budget": round(sum(card.execution_budget for card in cards) / len(cards), 3),
        },
        labels={"deck_id": deck_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_council.final_snapshot.runtime_stage,
        signals=(deck_signal, *resolved_council.final_snapshot.signals),
        alerts=resolved_council.final_snapshot.alerts,
        audit_entries=resolved_council.final_snapshot.audit_entries,
        active_controls=resolved_council.final_snapshot.active_controls,
    )
    return MandateCardDeck(
        deck_id=deck_id,
        strategy_council=resolved_council,
        cards=cards,
        deck_signal=deck_signal,
        final_snapshot=final_snapshot,
    )
