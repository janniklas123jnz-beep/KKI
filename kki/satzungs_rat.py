"""Satzungs rat turning codex register entries into living Leitstern statute articles."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kodex_register import KodexRegister, KodexRegisterEntry, RegisterRetention, RegisterTier, build_kodex_register
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class RatBench(str, Enum):
    """Institutional bench interpreting one statute article."""

    STEWARD_BENCH = "steward-bench"
    GOVERNANCE_BENCH = "governance-bench"
    AUTONOMY_BENCH = "autonomy-bench"


class RatInterpretation(str, Enum):
    """Interpretation posture used by the statute council."""

    PROTECTIVE_READING = "protective-reading"
    GOVERNED_READING = "governed-reading"
    SOVEREIGN_READING = "sovereign-reading"


class RatStatus(str, Enum):
    """Binding force of one interpreted statute article."""

    PROVISIONAL = "provisional"
    RATIFIED = "ratified"
    ENSHRINED = "enshrined"


@dataclass(frozen=True)
class SatzungsRatArticle:
    """One living statute article derived from a codex register entry."""

    article_id: str
    sequence: int
    entry_id: str
    section_id: str
    reference_key: str
    register_tier: RegisterTier
    retention: RegisterRetention
    bench: RatBench
    interpretation: RatInterpretation
    rat_status: RatStatus
    case_ids: tuple[str, ...]
    release_ready: bool
    statute_weight: float
    precedent_window: int
    statute_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "article_id", _non_empty(self.article_id, field_name="article_id"))
        object.__setattr__(self, "entry_id", _non_empty(self.entry_id, field_name="entry_id"))
        object.__setattr__(self, "section_id", _non_empty(self.section_id, field_name="section_id"))
        object.__setattr__(self, "reference_key", _non_empty(self.reference_key, field_name="reference_key"))
        object.__setattr__(self, "statute_weight", _clamp01(self.statute_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.precedent_window < 1:
            raise ValueError("precedent_window must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "article_id": self.article_id,
            "sequence": self.sequence,
            "entry_id": self.entry_id,
            "section_id": self.section_id,
            "reference_key": self.reference_key,
            "register_tier": self.register_tier.value,
            "retention": self.retention.value,
            "bench": self.bench.value,
            "interpretation": self.interpretation.value,
            "rat_status": self.rat_status.value,
            "case_ids": list(self.case_ids),
            "release_ready": self.release_ready,
            "statute_weight": self.statute_weight,
            "precedent_window": self.precedent_window,
            "statute_tags": list(self.statute_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class SatzungsRat:
    """Living statute council interpreting the Leitstern codex register."""

    rat_id: str
    kodex_register: KodexRegister
    articles: tuple[SatzungsRatArticle, ...]
    rat_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "rat_id", _non_empty(self.rat_id, field_name="rat_id"))

    @property
    def provisional_article_ids(self) -> tuple[str, ...]:
        return tuple(article.article_id for article in self.articles if article.rat_status is RatStatus.PROVISIONAL)

    @property
    def ratified_article_ids(self) -> tuple[str, ...]:
        return tuple(article.article_id for article in self.articles if article.rat_status is RatStatus.RATIFIED)

    @property
    def enshrined_article_ids(self) -> tuple[str, ...]:
        return tuple(article.article_id for article in self.articles if article.rat_status is RatStatus.ENSHRINED)

    def to_dict(self) -> dict[str, object]:
        return {
            "rat_id": self.rat_id,
            "kodex_register": self.kodex_register.to_dict(),
            "articles": [article.to_dict() for article in self.articles],
            "rat_signal": self.rat_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "provisional_article_ids": list(self.provisional_article_ids),
            "ratified_article_ids": list(self.ratified_article_ids),
            "enshrined_article_ids": list(self.enshrined_article_ids),
        }


def _bench(entry: KodexRegisterEntry) -> RatBench:
    return {
        RegisterTier.RESERVED: RatBench.STEWARD_BENCH,
        RegisterTier.CURATED: RatBench.GOVERNANCE_BENCH,
        RegisterTier.CANONIZED: RatBench.AUTONOMY_BENCH,
    }[entry.register_tier]


def _interpretation(entry: KodexRegisterEntry) -> RatInterpretation:
    return {
        RegisterRetention.AUDIT: RatInterpretation.PROTECTIVE_READING,
        RegisterRetention.GOVERNANCE: RatInterpretation.GOVERNED_READING,
        RegisterRetention.CONSTITUTIONAL: RatInterpretation.SOVEREIGN_READING,
    }[entry.retention]


def _status(entry: KodexRegisterEntry) -> RatStatus:
    return {
        RegisterTier.RESERVED: RatStatus.PROVISIONAL,
        RegisterTier.CURATED: RatStatus.RATIFIED,
        RegisterTier.CANONIZED: RatStatus.ENSHRINED,
    }[entry.register_tier]


def _statute_weight(entry: KodexRegisterEntry) -> float:
    bonus = {
        RatStatus.PROVISIONAL: 0.0,
        RatStatus.RATIFIED: 0.04,
        RatStatus.ENSHRINED: 0.08,
    }[_status(entry)]
    return round(min(1.0, entry.register_weight + bonus), 3)


def _precedent_window(entry: KodexRegisterEntry) -> int:
    return {
        RatStatus.PROVISIONAL: 1,
        RatStatus.RATIFIED: 2,
        RatStatus.ENSHRINED: 3,
    }[_status(entry)]


def build_satzungs_rat(
    kodex_register: KodexRegister | None = None,
    *,
    rat_id: str = "satzungs-rat",
) -> SatzungsRat:
    """Build the living statute council over the Leitstern codex register."""

    resolved_register = build_kodex_register(register_id=f"{rat_id}-register") if kodex_register is None else kodex_register
    articles = tuple(
        SatzungsRatArticle(
            article_id=f"{rat_id}-{entry.entry_id.removeprefix(f'{resolved_register.register_id}-')}",
            sequence=index,
            entry_id=entry.entry_id,
            section_id=entry.section_id,
            reference_key=entry.reference_key,
            register_tier=entry.register_tier,
            retention=entry.retention,
            bench=_bench(entry),
            interpretation=_interpretation(entry),
            rat_status=_status(entry),
            case_ids=entry.case_ids,
            release_ready=entry.release_ready and _status(entry) is RatStatus.ENSHRINED,
            statute_weight=_statute_weight(entry),
            precedent_window=_precedent_window(entry),
            statute_tags=tuple(
                dict.fromkeys(
                    (
                        *entry.register_tags,
                        _bench(entry).value,
                        _interpretation(entry).value,
                        _status(entry).value,
                    )
                )
            ),
            summary=(
                f"{entry.entry_id} is interpreted by {_bench(entry).value} as "
                f"{_status(entry).value} statute under {_interpretation(entry).value}."
            ),
        )
        for index, entry in enumerate(resolved_register.entries, start=1)
    )
    if not articles:
        raise ValueError("satzungs rat requires at least one article")

    severity = "info"
    status = "rat-enshrined"
    if any(article.rat_status is RatStatus.PROVISIONAL for article in articles):
        severity = "critical"
        status = "rat-provisional"
    elif any(article.rat_status is RatStatus.RATIFIED for article in articles):
        severity = "warning"
        status = "rat-ratified"

    rat_signal = TelemetrySignal(
        signal_name="satzungs-rat",
        boundary=resolved_register.register_signal.boundary,
        correlation_id=rat_id,
        severity=severity,
        status=status,
        metrics={
            "article_count": float(len(articles)),
            "provisional_count": float(len([article for article in articles if article.rat_status is RatStatus.PROVISIONAL])),
            "ratified_count": float(len([article for article in articles if article.rat_status is RatStatus.RATIFIED])),
            "enshrined_count": float(len([article for article in articles if article.rat_status is RatStatus.ENSHRINED])),
            "release_ready_count": float(len([article for article in articles if article.release_ready])),
            "avg_statute_weight": round(sum(article.statute_weight for article in articles) / len(articles), 3),
        },
        labels={"rat_id": rat_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_register.final_snapshot.runtime_stage,
        signals=(rat_signal, *resolved_register.final_snapshot.signals),
        alerts=resolved_register.final_snapshot.alerts,
        audit_entries=resolved_register.final_snapshot.audit_entries,
        active_controls=resolved_register.final_snapshot.active_controls,
    )
    return SatzungsRat(
        rat_id=rat_id,
        kodex_register=resolved_register,
        articles=articles,
        rat_signal=rat_signal,
        final_snapshot=final_snapshot,
    )
