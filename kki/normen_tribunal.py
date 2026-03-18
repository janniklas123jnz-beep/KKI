"""Normen tribunal adjudicating mandate lines into binding Leitstern verdicts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .mandats_konvent import (
    KonventEbene,
    KonventMandat,
    KonventStatus,
    MandatsKonvent,
    MandatsLinie,
    build_mandats_konvent,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class TribunalKammer(str, Enum):
    """Chamber of the tribunal that hears one mandate case."""

    SCHUTZ_KAMMER = "schutz-kammer"
    ORDNUNGS_KAMMER = "ordnungs-kammer"
    SOUVERAENITAETS_KAMMER = "souveraenitaets-kammer"


class TribunalVerfahren(str, Enum):
    """Procedural track used for deliberation."""

    SUMMARISCHES_VERFAHREN = "summarisches-verfahren"
    ORDENTLICHES_VERFAHREN = "ordentliches-verfahren"
    VERFASSUNGSVERFAHREN = "verfassungsverfahren"


class TribunalUrteil(str, Enum):
    """Binding verdict rendered by the tribunal chamber."""

    ABGEWIESEN = "abgewiesen"
    BESTAETIGT = "bestaetigt"
    VERFASSUNGSGEBUNDEN = "verfassungsgebunden"


@dataclass(frozen=True)
class TribunalFall:
    """One adjudicated case derived from a mandate convention line."""

    fall_id: str
    sequence: int
    line_id: str
    article_id: str
    entry_id: str
    section_id: str
    reference_key: str
    konvent_mandat: KonventMandat
    konvent_ebene: KonventEbene
    konvent_status: KonventStatus
    kammer: TribunalKammer
    verfahren: TribunalVerfahren
    urteil: TribunalUrteil
    case_ids: tuple[str, ...]
    release_ready: bool
    verdict_weight: float
    deliberation_rounds: int
    fall_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "fall_id", _non_empty(self.fall_id, field_name="fall_id"))
        object.__setattr__(self, "line_id", _non_empty(self.line_id, field_name="line_id"))
        object.__setattr__(self, "article_id", _non_empty(self.article_id, field_name="article_id"))
        object.__setattr__(self, "entry_id", _non_empty(self.entry_id, field_name="entry_id"))
        object.__setattr__(self, "section_id", _non_empty(self.section_id, field_name="section_id"))
        object.__setattr__(self, "reference_key", _non_empty(self.reference_key, field_name="reference_key"))
        object.__setattr__(self, "verdict_weight", _clamp01(self.verdict_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.deliberation_rounds < 1:
            raise ValueError("deliberation_rounds must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "fall_id": self.fall_id,
            "sequence": self.sequence,
            "line_id": self.line_id,
            "article_id": self.article_id,
            "entry_id": self.entry_id,
            "section_id": self.section_id,
            "reference_key": self.reference_key,
            "konvent_mandat": self.konvent_mandat.value,
            "konvent_ebene": self.konvent_ebene.value,
            "konvent_status": self.konvent_status.value,
            "kammer": self.kammer.value,
            "verfahren": self.verfahren.value,
            "urteil": self.urteil.value,
            "case_ids": list(self.case_ids),
            "release_ready": self.release_ready,
            "verdict_weight": self.verdict_weight,
            "deliberation_rounds": self.deliberation_rounds,
            "fall_tags": list(self.fall_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class NormenTribunal:
    """Tribunal that adjudicates mandate lines into binding Leitstern verdicts."""

    tribunal_id: str
    mandats_konvent: MandatsKonvent
    faelle: tuple[TribunalFall, ...]
    tribunal_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "tribunal_id", _non_empty(self.tribunal_id, field_name="tribunal_id"))

    @property
    def abgewiesen_fall_ids(self) -> tuple[str, ...]:
        return tuple(f.fall_id for f in self.faelle if f.urteil is TribunalUrteil.ABGEWIESEN)

    @property
    def bestaetigt_fall_ids(self) -> tuple[str, ...]:
        return tuple(f.fall_id for f in self.faelle if f.urteil is TribunalUrteil.BESTAETIGT)

    @property
    def verfassungsgebunden_fall_ids(self) -> tuple[str, ...]:
        return tuple(f.fall_id for f in self.faelle if f.urteil is TribunalUrteil.VERFASSUNGSGEBUNDEN)

    def to_dict(self) -> dict[str, object]:
        return {
            "tribunal_id": self.tribunal_id,
            "mandats_konvent": self.mandats_konvent.to_dict(),
            "faelle": [f.to_dict() for f in self.faelle],
            "tribunal_signal": self.tribunal_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "abgewiesen_fall_ids": list(self.abgewiesen_fall_ids),
            "bestaetigt_fall_ids": list(self.bestaetigt_fall_ids),
            "verfassungsgebunden_fall_ids": list(self.verfassungsgebunden_fall_ids),
        }


def _kammer(line: MandatsLinie) -> TribunalKammer:
    return {
        KonventMandat.SCHUTZ_MANDAT: TribunalKammer.SCHUTZ_KAMMER,
        KonventMandat.ORDNUNGS_MANDAT: TribunalKammer.ORDNUNGS_KAMMER,
        KonventMandat.SOUVERAENITAETS_MANDAT: TribunalKammer.SOUVERAENITAETS_KAMMER,
    }[line.konvent_mandat]


def _verfahren(line: MandatsLinie) -> TribunalVerfahren:
    return {
        KonventStatus.BEGRENZT: TribunalVerfahren.SUMMARISCHES_VERFAHREN,
        KonventStatus.DELEGIERT: TribunalVerfahren.ORDENTLICHES_VERFAHREN,
        KonventStatus.VERANKERT: TribunalVerfahren.VERFASSUNGSVERFAHREN,
    }[line.konvent_status]


def _urteil(line: MandatsLinie) -> TribunalUrteil:
    return {
        KonventStatus.BEGRENZT: TribunalUrteil.ABGEWIESEN,
        KonventStatus.DELEGIERT: TribunalUrteil.BESTAETIGT,
        KonventStatus.VERANKERT: TribunalUrteil.VERFASSUNGSGEBUNDEN,
    }[line.konvent_status]


def _verdict_weight(line: MandatsLinie) -> float:
    bonus = {
        TribunalUrteil.ABGEWIESEN: 0.0,
        TribunalUrteil.BESTAETIGT: 0.04,
        TribunalUrteil.VERFASSUNGSGEBUNDEN: 0.08,
    }[_urteil(line)]
    return round(min(1.0, line.delegations_budget + bonus), 3)


def _deliberation_rounds(line: MandatsLinie) -> int:
    return {
        TribunalUrteil.ABGEWIESEN: line.handoff_window,
        TribunalUrteil.BESTAETIGT: line.handoff_window + 1,
        TribunalUrteil.VERFASSUNGSGEBUNDEN: line.handoff_window + 2,
    }[_urteil(line)]


def build_normen_tribunal(
    mandats_konvent: MandatsKonvent | None = None,
    *,
    tribunal_id: str = "normen-tribunal",
) -> NormenTribunal:
    """Build the norms tribunal adjudicating the Leitstern mandate convention."""

    resolved_konvent = (
        build_mandats_konvent(konvent_id=f"{tribunal_id}-konvent")
        if mandats_konvent is None
        else mandats_konvent
    )
    faelle = tuple(
        TribunalFall(
            fall_id=f"{tribunal_id}-{line.line_id.removeprefix(f'{resolved_konvent.konvent_id}-')}",
            sequence=index,
            line_id=line.line_id,
            article_id=line.article_id,
            entry_id=line.entry_id,
            section_id=line.section_id,
            reference_key=line.reference_key,
            konvent_mandat=line.konvent_mandat,
            konvent_ebene=line.konvent_ebene,
            konvent_status=line.konvent_status,
            kammer=_kammer(line),
            verfahren=_verfahren(line),
            urteil=_urteil(line),
            case_ids=line.case_ids,
            release_ready=line.release_ready and _urteil(line) is TribunalUrteil.VERFASSUNGSGEBUNDEN,
            verdict_weight=_verdict_weight(line),
            deliberation_rounds=_deliberation_rounds(line),
            fall_tags=tuple(
                dict.fromkeys(
                    (
                        *line.mandate_tags,
                        _kammer(line).value,
                        _verfahren(line).value,
                        _urteil(line).value,
                    )
                )
            ),
            summary=(
                f"{line.line_id} is adjudicated by {_kammer(line).value} via "
                f"{_verfahren(line).value} with verdict {_urteil(line).value}."
            ),
        )
        for index, line in enumerate(resolved_konvent.lines, start=1)
    )
    if not faelle:
        raise ValueError("normen tribunal requires at least one fall")

    severity = "info"
    status = "tribunal-verfassungsgebunden"
    if any(f.urteil is TribunalUrteil.ABGEWIESEN for f in faelle):
        severity = "critical"
        status = "tribunal-abgewiesen"
    elif any(f.urteil is TribunalUrteil.BESTAETIGT for f in faelle):
        severity = "warning"
        status = "tribunal-bestaetigt"

    tribunal_signal = TelemetrySignal(
        signal_name="normen-tribunal",
        boundary=resolved_konvent.konvent_signal.boundary,
        correlation_id=tribunal_id,
        severity=severity,
        status=status,
        metrics={
            "fall_count": float(len(faelle)),
            "abgewiesen_count": float(sum(1 for f in faelle if f.urteil is TribunalUrteil.ABGEWIESEN)),
            "bestaetigt_count": float(sum(1 for f in faelle if f.urteil is TribunalUrteil.BESTAETIGT)),
            "verfassungsgebunden_count": float(sum(1 for f in faelle if f.urteil is TribunalUrteil.VERFASSUNGSGEBUNDEN)),
            "release_ready_count": float(sum(1 for f in faelle if f.release_ready)),
            "avg_verdict_weight": round(sum(f.verdict_weight for f in faelle) / len(faelle), 3),
        },
        labels={"tribunal_id": tribunal_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_konvent.final_snapshot.runtime_stage,
        signals=(tribunal_signal, *resolved_konvent.final_snapshot.signals),
        alerts=resolved_konvent.final_snapshot.alerts,
        audit_entries=resolved_konvent.final_snapshot.audit_entries,
        active_controls=resolved_konvent.final_snapshot.active_controls,
    )
    return NormenTribunal(
        tribunal_id=tribunal_id,
        mandats_konvent=resolved_konvent,
        faelle=faelle,
        tribunal_signal=tribunal_signal,
        final_snapshot=final_snapshot,
    )
