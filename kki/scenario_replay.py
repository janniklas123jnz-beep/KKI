"""Deterministic scenario replays over benchmark and guardrail chains."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .benchmark_harness import BenchmarkCase, BenchmarkCaseResult, BenchmarkHarness, run_benchmark_harness
from .guardrail_portfolio import Guardrail, GuardrailPolicyMode, GuardrailPortfolio, build_guardrail_portfolio
from .release_campaigns import ReleaseCampaignStatus
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


class ReplayMode(str, Enum):
    """Canonical replay modes selected from active guardrails."""

    OBSERVED = "observed-replay"
    GUARDED = "guarded-replay"
    CONTAINED = "contained-replay"


@dataclass(frozen=True)
class ScenarioReplayItem:
    """Replay request derived from a benchmark case and applicable guardrails."""

    replay_item_id: str
    source_case_id: str
    baseline_status: ReleaseCampaignStatus
    replay_mode: ReplayMode
    replay_case: BenchmarkCase
    guardrails: tuple[Guardrail, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "replay_item_id", _non_empty(self.replay_item_id, field_name="replay_item_id"))
        object.__setattr__(self, "source_case_id", _non_empty(self.source_case_id, field_name="source_case_id"))

    def to_dict(self) -> dict[str, object]:
        return {
            "replay_item_id": self.replay_item_id,
            "source_case_id": self.source_case_id,
            "baseline_status": self.baseline_status.value,
            "replay_mode": self.replay_mode.value,
            "replay_case": self.replay_case.to_dict(),
            "guardrails": [guardrail.to_dict() for guardrail in self.guardrails],
        }


@dataclass(frozen=True)
class ScenarioReplayResult:
    """Replay result for one replayed benchmark case."""

    replay_id: str
    item: ScenarioReplayItem
    result: BenchmarkCaseResult
    replay_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "replay_id", _non_empty(self.replay_id, field_name="replay_id"))

    @property
    def stable(self) -> bool:
        return self.item.baseline_status is self.result.status

    def to_dict(self) -> dict[str, object]:
        return {
            "replay_id": self.replay_id,
            "item": self.item.to_dict(),
            "result": self.result.to_dict(),
            "replay_signal": self.replay_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "stable": self.stable,
        }


@dataclass(frozen=True)
class ScenarioReplaySuite:
    """Aggregated replay suite over attention or blocked benchmark cases."""

    replay_id: str
    source_harness: BenchmarkHarness
    guardrail_portfolio: GuardrailPortfolio
    items: tuple[ScenarioReplayItem, ...]
    results: tuple[ScenarioReplayResult, ...]
    replay_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "replay_id", _non_empty(self.replay_id, field_name="replay_id"))

    @property
    def replayed_case_ids(self) -> tuple[str, ...]:
        return tuple(item.source_case_id for item in self.items)

    @property
    def unstable_case_ids(self) -> tuple[str, ...]:
        return tuple(result.item.source_case_id for result in self.results if not result.stable)

    @property
    def blocked_case_ids(self) -> tuple[str, ...]:
        return tuple(
            result.item.source_case_id
            for result in self.results
            if result.result.status is ReleaseCampaignStatus.BLOCKED
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "replay_id": self.replay_id,
            "source_harness": self.source_harness.to_dict(),
            "guardrail_portfolio": self.guardrail_portfolio.to_dict(),
            "items": [item.to_dict() for item in self.items],
            "results": [result.to_dict() for result in self.results],
            "replay_signal": self.replay_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "replayed_case_ids": list(self.replayed_case_ids),
            "unstable_case_ids": list(self.unstable_case_ids),
            "blocked_case_ids": list(self.blocked_case_ids),
        }


def _replay_mode_for_guardrails(guardrails: tuple[Guardrail, ...]) -> ReplayMode:
    if any(guardrail.policy_mode is GuardrailPolicyMode.CONTAIN for guardrail in guardrails):
        return ReplayMode.CONTAINED
    if any(guardrail.policy_mode in {GuardrailPolicyMode.HOLD, GuardrailPolicyMode.THROTTLE} for guardrail in guardrails):
        return ReplayMode.GUARDED
    return ReplayMode.OBSERVED


def _items_for_harness(
    replay_id: str,
    harness: BenchmarkHarness,
    portfolio: GuardrailPortfolio,
    *,
    include_ready: bool,
) -> tuple[ScenarioReplayItem, ...]:
    items: list[ScenarioReplayItem] = []
    for result in harness.results:
        if not include_ready and result.status is ReleaseCampaignStatus.READY:
            continue
        related_guardrails = tuple(
            guardrail for guardrail in portfolio.guardrails if guardrail.case_id == result.case.case_id
        )
        items.append(
            ScenarioReplayItem(
                replay_item_id=f"{replay_id}-{result.case.case_id}",
                source_case_id=result.case.case_id,
                baseline_status=result.status,
                replay_mode=_replay_mode_for_guardrails(related_guardrails),
                replay_case=result.case,
                guardrails=related_guardrails,
            )
        )
    return tuple(items)


def _result_for_item(replay_id: str, item: ScenarioReplayItem) -> ScenarioReplayResult:
    harness = run_benchmark_harness((item.replay_case,), harness_id=f"{replay_id}-{item.source_case_id}")
    result = harness.results[0]
    severity = "info" if result.status is item.baseline_status else "warning"
    if result.status is ReleaseCampaignStatus.BLOCKED:
        severity = "critical"
    replay_signal = TelemetrySignal(
        signal_name="scenario-replay",
        boundary=result.benchmark_signal.boundary,
        correlation_id=f"{replay_id}-{item.source_case_id}",
        severity=severity,
        status=result.status.value,
        metrics={
            "stable": float(result.status is item.baseline_status),
            "guardrail_count": float(len(item.guardrails)),
            "promotion_ready": float(result.promotion_ready),
        },
        labels={
            "source_case_id": item.source_case_id,
            "replay_mode": item.replay_mode.value,
        },
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=result.final_snapshot.runtime_stage,
        signals=(replay_signal, result.benchmark_signal, *result.final_snapshot.signals),
        alerts=result.final_snapshot.alerts,
        audit_entries=result.final_snapshot.audit_entries,
        active_controls=result.final_snapshot.active_controls,
    )
    return ScenarioReplayResult(
        replay_id=replay_id,
        item=item,
        result=result,
        replay_signal=replay_signal,
        final_snapshot=final_snapshot,
    )


def build_scenario_replay(
    harness: BenchmarkHarness | None = None,
    guardrail_portfolio: GuardrailPortfolio | None = None,
    *,
    replay_id: str = "scenario-replay",
    include_ready: bool = False,
) -> ScenarioReplaySuite:
    """Build deterministic replays for attention and blocked benchmark cases."""

    resolved_harness = run_benchmark_harness(harness_id=f"{replay_id}-harness") if harness is None else harness
    resolved_portfolio = (
        build_guardrail_portfolio(portfolio_id=f"{replay_id}-portfolio")
        if guardrail_portfolio is None
        else guardrail_portfolio
    )
    items = _items_for_harness(replay_id, resolved_harness, resolved_portfolio, include_ready=include_ready)
    if not items:
        raise ValueError("scenario replay requires at least one replay candidate")
    results = tuple(_result_for_item(replay_id, item) for item in items)

    severity = "info"
    status = "stable-replays"
    if any(result.result.status is ReleaseCampaignStatus.BLOCKED for result in results):
        severity = "critical"
        status = "blocked-replays"
    elif any(not result.stable for result in results):
        severity = "warning"
        status = "drifting-replays"
    elif any(result.result.status in {ReleaseCampaignStatus.GUARDED, ReleaseCampaignStatus.RECOVERY_ONLY} for result in results):
        severity = "warning"
        status = "attention-replays"

    replay_signal = TelemetrySignal(
        signal_name="scenario-replay",
        boundary=results[0].replay_signal.boundary,
        correlation_id=replay_id,
        severity=severity,
        status=status,
        metrics={
            "replay_count": float(len(results)),
            "stable_count": float(len([result for result in results if result.stable])),
            "blocked_count": float(len([result for result in results if result.result.status is ReleaseCampaignStatus.BLOCKED])),
            "guarded_count": float(
                len([result for result in results if result.result.status is ReleaseCampaignStatus.GUARDED])
            ),
        },
        labels={"replay_id": replay_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=results[0].final_snapshot.runtime_stage,
        signals=(replay_signal, *(result.replay_signal for result in results), *(signal for result in results for signal in result.final_snapshot.signals)),
        alerts=tuple(alert for result in results for alert in result.final_snapshot.alerts),
        audit_entries=tuple(record for result in results for record in result.final_snapshot.audit_entries),
        active_controls=tuple(dict.fromkeys(control for result in results for control in result.final_snapshot.active_controls)),
    )
    return ScenarioReplaySuite(
        replay_id=replay_id,
        source_harness=resolved_harness,
        guardrail_portfolio=resolved_portfolio,
        items=items,
        results=results,
        replay_signal=replay_signal,
        final_snapshot=final_snapshot,
    )
