"""Mandats konvent reflecting statute articles into delegable Leitstern mandate lines."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .satzungs_rat import RatBench, RatInterpretation, RatStatus, SatzungsRat, SatzungsRatArticle, build_satzungs_rat
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class KonventMandat(str, Enum):
    """Delegable mandate posture assigned by the convention."""

    SCHUTZ_MANDAT = "schutz-mandat"
    ORDNUNGS_MANDAT = "ordnungs-mandat"
    SOUVERAENITAETS_MANDAT = "souveraenitaets-mandat"


class KonventEbene(str, Enum):
    """Leitstern level that receives one mandate line."""

    STEWARD_EBENE = "steward-ebene"
    GOVERNANCE_EBENE = "governance-ebene"
    AUTONOMIE_EBENE = "autonomie-ebene"


class KonventStatus(str, Enum):
    """Delegation force carried by one convention line."""

    BEGRENZT = "begrenzt"
    DELEGIERT = "delegiert"
    VERANKERT = "verankert"


@dataclass(frozen=True)
class MandatsLinie:
    """One delegable mandate line derived from a statute article."""

    line_id: str
    sequence: int
    article_id: str
    entry_id: str
    section_id: str
    reference_key: str
    bench: RatBench
    interpretation: RatInterpretation
    konvent_mandat: KonventMandat
    konvent_ebene: KonventEbene
    konvent_status: KonventStatus
    case_ids: tuple[str, ...]
    release_ready: bool
    delegations_budget: float
    handoff_window: int
    mandate_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "line_id", _non_empty(self.line_id, field_name="line_id"))
        object.__setattr__(self, "article_id", _non_empty(self.article_id, field_name="article_id"))
        object.__setattr__(self, "entry_id", _non_empty(self.entry_id, field_name="entry_id"))
        object.__setattr__(self, "section_id", _non_empty(self.section_id, field_name="section_id"))
        object.__setattr__(self, "reference_key", _non_empty(self.reference_key, field_name="reference_key"))
        object.__setattr__(self, "delegations_budget", _clamp01(self.delegations_budget))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.handoff_window < 1:
            raise ValueError("handoff_window must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "line_id": self.line_id,
            "sequence": self.sequence,
            "article_id": self.article_id,
            "entry_id": self.entry_id,
            "section_id": self.section_id,
            "reference_key": self.reference_key,
            "bench": self.bench.value,
            "interpretation": self.interpretation.value,
            "konvent_mandat": self.konvent_mandat.value,
            "konvent_ebene": self.konvent_ebene.value,
            "konvent_status": self.konvent_status.value,
            "case_ids": list(self.case_ids),
            "release_ready": self.release_ready,
            "delegations_budget": self.delegations_budget,
            "handoff_window": self.handoff_window,
            "mandate_tags": list(self.mandate_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class MandatsKonvent:
    """Convention that translates statute articles into delegable mandate lines."""

    konvent_id: str
    satzungs_rat: SatzungsRat
    lines: tuple[MandatsLinie, ...]
    konvent_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "konvent_id", _non_empty(self.konvent_id, field_name="konvent_id"))

    @property
    def begrenzt_line_ids(self) -> tuple[str, ...]:
        return tuple(line.line_id for line in self.lines if line.konvent_status is KonventStatus.BEGRENZT)

    @property
    def delegiert_line_ids(self) -> tuple[str, ...]:
        return tuple(line.line_id for line in self.lines if line.konvent_status is KonventStatus.DELEGIERT)

    @property
    def verankert_line_ids(self) -> tuple[str, ...]:
        return tuple(line.line_id for line in self.lines if line.konvent_status is KonventStatus.VERANKERT)

    def to_dict(self) -> dict[str, object]:
        return {
            "konvent_id": self.konvent_id,
            "satzungs_rat": self.satzungs_rat.to_dict(),
            "lines": [line.to_dict() for line in self.lines],
            "konvent_signal": self.konvent_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "begrenzt_line_ids": list(self.begrenzt_line_ids),
            "delegiert_line_ids": list(self.delegiert_line_ids),
            "verankert_line_ids": list(self.verankert_line_ids),
        }


def _mandat(article: SatzungsRatArticle) -> KonventMandat:
    return {
        RatInterpretation.PROTECTIVE_READING: KonventMandat.SCHUTZ_MANDAT,
        RatInterpretation.GOVERNED_READING: KonventMandat.ORDNUNGS_MANDAT,
        RatInterpretation.SOVEREIGN_READING: KonventMandat.SOUVERAENITAETS_MANDAT,
    }[article.interpretation]


def _ebene(article: SatzungsRatArticle) -> KonventEbene:
    return {
        RatBench.STEWARD_BENCH: KonventEbene.STEWARD_EBENE,
        RatBench.GOVERNANCE_BENCH: KonventEbene.GOVERNANCE_EBENE,
        RatBench.AUTONOMY_BENCH: KonventEbene.AUTONOMIE_EBENE,
    }[article.bench]


def _status(article: SatzungsRatArticle) -> KonventStatus:
    return {
        RatStatus.PROVISIONAL: KonventStatus.BEGRENZT,
        RatStatus.RATIFIED: KonventStatus.DELEGIERT,
        RatStatus.ENSHRINED: KonventStatus.VERANKERT,
    }[article.rat_status]


def _delegations_budget(article: SatzungsRatArticle) -> float:
    bonus = {
        KonventStatus.BEGRENZT: 0.0,
        KonventStatus.DELEGIERT: 0.04,
        KonventStatus.VERANKERT: 0.08,
    }[_status(article)]
    return round(min(1.0, article.statute_weight + bonus), 3)


def _handoff_window(article: SatzungsRatArticle) -> int:
    return {
        KonventStatus.BEGRENZT: article.precedent_window,
        KonventStatus.DELEGIERT: article.precedent_window + 1,
        KonventStatus.VERANKERT: article.precedent_window + 2,
    }[_status(article)]


def build_mandats_konvent(
    satzungs_rat: SatzungsRat | None = None,
    *,
    konvent_id: str = "mandats-konvent",
) -> MandatsKonvent:
    """Build the mandate convention over the living Leitstern statute."""

    resolved_rat = build_satzungs_rat(rat_id=f"{konvent_id}-rat") if satzungs_rat is None else satzungs_rat
    lines = tuple(
        MandatsLinie(
            line_id=f"{konvent_id}-{article.article_id.removeprefix(f'{resolved_rat.rat_id}-')}",
            sequence=index,
            article_id=article.article_id,
            entry_id=article.entry_id,
            section_id=article.section_id,
            reference_key=article.reference_key,
            bench=article.bench,
            interpretation=article.interpretation,
            konvent_mandat=_mandat(article),
            konvent_ebene=_ebene(article),
            konvent_status=_status(article),
            case_ids=article.case_ids,
            release_ready=article.release_ready and _status(article) is KonventStatus.VERANKERT,
            delegations_budget=_delegations_budget(article),
            handoff_window=_handoff_window(article),
            mandate_tags=tuple(
                dict.fromkeys(
                    (
                        *article.statute_tags,
                        _mandat(article).value,
                        _ebene(article).value,
                        _status(article).value,
                    )
                )
            ),
            summary=(
                f"{article.article_id} delegates {_mandat(article).value} to {_ebene(article).value} "
                f"as {_status(article).value} mandate line."
            ),
        )
        for index, article in enumerate(resolved_rat.articles, start=1)
    )
    if not lines:
        raise ValueError("mandats konvent requires at least one line")

    severity = "info"
    status = "konvent-verankert"
    if any(line.konvent_status is KonventStatus.BEGRENZT for line in lines):
        severity = "critical"
        status = "konvent-begrenzt"
    elif any(line.konvent_status is KonventStatus.DELEGIERT for line in lines):
        severity = "warning"
        status = "konvent-delegiert"

    konvent_signal = TelemetrySignal(
        signal_name="mandats-konvent",
        boundary=resolved_rat.rat_signal.boundary,
        correlation_id=konvent_id,
        severity=severity,
        status=status,
        metrics={
            "line_count": float(len(lines)),
            "begrenzt_count": float(len([line for line in lines if line.konvent_status is KonventStatus.BEGRENZT])),
            "delegiert_count": float(len([line for line in lines if line.konvent_status is KonventStatus.DELEGIERT])),
            "verankert_count": float(len([line for line in lines if line.konvent_status is KonventStatus.VERANKERT])),
            "release_ready_count": float(len([line for line in lines if line.release_ready])),
            "avg_delegations_budget": round(sum(line.delegations_budget for line in lines) / len(lines), 3),
        },
        labels={"konvent_id": konvent_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_rat.final_snapshot.runtime_stage,
        signals=(konvent_signal, *resolved_rat.final_snapshot.signals),
        alerts=resolved_rat.final_snapshot.alerts,
        audit_entries=resolved_rat.final_snapshot.audit_entries,
        active_controls=resolved_rat.final_snapshot.active_controls,
    )
    return MandatsKonvent(
        konvent_id=konvent_id,
        satzungs_rat=resolved_rat,
        lines=lines,
        konvent_signal=konvent_signal,
        final_snapshot=final_snapshot,
    )
