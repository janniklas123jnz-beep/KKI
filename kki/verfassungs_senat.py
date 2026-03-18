"""Verfassungs senat elevating tribunal falls into constitutional Leitstern resolutions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .normen_tribunal import (
    NormenTribunal,
    TribunalFall,
    TribunalKammer,
    TribunalUrteil,
    TribunalVerfahren,
    build_normen_tribunal,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class SenatsFraktion(str, Enum):
    """Senate faction that deliberates one tribunal fall."""

    SCHUTZ_FRAKTION = "schutz-fraktion"
    ORDNUNGS_FRAKTION = "ordnungs-fraktion"
    SOUVERAENITAETS_FRAKTION = "souveraenitaets-fraktion"


class SenatsSitzung(str, Enum):
    """Plenary session format used for deliberation."""

    DRINGLICH_SITZUNG = "dringlich-sitzung"
    ORDENTLICHE_SITZUNG = "ordentliche-sitzung"
    PLENARSITZUNG = "plenarsitzung"


class SenatsBeschluss(str, Enum):
    """Constitutional resolution issued by the senate."""

    UNGUELTIG = "ungueltig"
    WIRKSAM = "wirksam"
    GRUNDLEGEND = "grundlegend"


@dataclass(frozen=True)
class SenatsMandat:
    """One senate mandate derived from a tribunal fall."""

    mandat_id: str
    sequence: int
    fall_id: str
    line_id: str
    article_id: str
    entry_id: str
    section_id: str
    reference_key: str
    tribunal_kammer: TribunalKammer
    tribunal_urteil: TribunalUrteil
    tribunal_verfahren: TribunalVerfahren
    fraktion: SenatsFraktion
    sitzung: SenatsSitzung
    beschluss: SenatsBeschluss
    mandate_ids: tuple[str, ...]
    binding: bool
    resolution_weight: float
    deliberation_quorum: int
    mandat_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "mandat_id", _non_empty(self.mandat_id, field_name="mandat_id"))
        object.__setattr__(self, "fall_id", _non_empty(self.fall_id, field_name="fall_id"))
        object.__setattr__(self, "line_id", _non_empty(self.line_id, field_name="line_id"))
        object.__setattr__(self, "article_id", _non_empty(self.article_id, field_name="article_id"))
        object.__setattr__(self, "entry_id", _non_empty(self.entry_id, field_name="entry_id"))
        object.__setattr__(self, "section_id", _non_empty(self.section_id, field_name="section_id"))
        object.__setattr__(self, "reference_key", _non_empty(self.reference_key, field_name="reference_key"))
        object.__setattr__(self, "resolution_weight", _clamp01(self.resolution_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.deliberation_quorum < 1:
            raise ValueError("deliberation_quorum must be positive")
        if not self.mandate_ids:
            raise ValueError("mandate_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "mandat_id": self.mandat_id,
            "sequence": self.sequence,
            "fall_id": self.fall_id,
            "line_id": self.line_id,
            "article_id": self.article_id,
            "entry_id": self.entry_id,
            "section_id": self.section_id,
            "reference_key": self.reference_key,
            "tribunal_kammer": self.tribunal_kammer.value,
            "tribunal_urteil": self.tribunal_urteil.value,
            "tribunal_verfahren": self.tribunal_verfahren.value,
            "fraktion": self.fraktion.value,
            "sitzung": self.sitzung.value,
            "beschluss": self.beschluss.value,
            "mandate_ids": list(self.mandate_ids),
            "binding": self.binding,
            "resolution_weight": self.resolution_weight,
            "deliberation_quorum": self.deliberation_quorum,
            "mandat_tags": list(self.mandat_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class VerfassungsSenat:
    """Senate that elevates tribunal falls into constitutional Leitstern resolutions."""

    senat_id: str
    normen_tribunal: NormenTribunal
    mandate: tuple[SenatsMandat, ...]
    senat_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "senat_id", _non_empty(self.senat_id, field_name="senat_id"))

    @property
    def ungueltig_mandat_ids(self) -> tuple[str, ...]:
        return tuple(m.mandat_id for m in self.mandate if m.beschluss is SenatsBeschluss.UNGUELTIG)

    @property
    def wirksam_mandat_ids(self) -> tuple[str, ...]:
        return tuple(m.mandat_id for m in self.mandate if m.beschluss is SenatsBeschluss.WIRKSAM)

    @property
    def grundlegend_mandat_ids(self) -> tuple[str, ...]:
        return tuple(m.mandat_id for m in self.mandate if m.beschluss is SenatsBeschluss.GRUNDLEGEND)

    def to_dict(self) -> dict[str, object]:
        return {
            "senat_id": self.senat_id,
            "normen_tribunal": self.normen_tribunal.to_dict(),
            "mandate": [m.to_dict() for m in self.mandate],
            "senat_signal": self.senat_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "ungueltig_mandat_ids": list(self.ungueltig_mandat_ids),
            "wirksam_mandat_ids": list(self.wirksam_mandat_ids),
            "grundlegend_mandat_ids": list(self.grundlegend_mandat_ids),
        }


def _fraktion(fall: TribunalFall) -> SenatsFraktion:
    return {
        TribunalKammer.SCHUTZ_KAMMER: SenatsFraktion.SCHUTZ_FRAKTION,
        TribunalKammer.ORDNUNGS_KAMMER: SenatsFraktion.ORDNUNGS_FRAKTION,
        TribunalKammer.SOUVERAENITAETS_KAMMER: SenatsFraktion.SOUVERAENITAETS_FRAKTION,
    }[fall.kammer]


def _sitzung(fall: TribunalFall) -> SenatsSitzung:
    return {
        TribunalVerfahren.SUMMARISCHES_VERFAHREN: SenatsSitzung.DRINGLICH_SITZUNG,
        TribunalVerfahren.ORDENTLICHES_VERFAHREN: SenatsSitzung.ORDENTLICHE_SITZUNG,
        TribunalVerfahren.VERFASSUNGSVERFAHREN: SenatsSitzung.PLENARSITZUNG,
    }[fall.verfahren]


def _beschluss(fall: TribunalFall) -> SenatsBeschluss:
    return {
        TribunalUrteil.ABGEWIESEN: SenatsBeschluss.UNGUELTIG,
        TribunalUrteil.BESTAETIGT: SenatsBeschluss.WIRKSAM,
        TribunalUrteil.VERFASSUNGSGEBUNDEN: SenatsBeschluss.GRUNDLEGEND,
    }[fall.urteil]


def _resolution_weight(fall: TribunalFall) -> float:
    bonus = {
        SenatsBeschluss.UNGUELTIG: 0.0,
        SenatsBeschluss.WIRKSAM: 0.04,
        SenatsBeschluss.GRUNDLEGEND: 0.08,
    }[_beschluss(fall)]
    return round(min(1.0, fall.verdict_weight + bonus), 3)


def _deliberation_quorum(fall: TribunalFall) -> int:
    return {
        SenatsBeschluss.UNGUELTIG: fall.deliberation_rounds,
        SenatsBeschluss.WIRKSAM: fall.deliberation_rounds + 1,
        SenatsBeschluss.GRUNDLEGEND: fall.deliberation_rounds + 2,
    }[_beschluss(fall)]


def build_verfassungs_senat(
    normen_tribunal: NormenTribunal | None = None,
    *,
    senat_id: str = "verfassungs-senat",
) -> VerfassungsSenat:
    """Build the constitutional senate elevating Leitstern tribunal falls."""

    resolved_tribunal = (
        build_normen_tribunal(tribunal_id=f"{senat_id}-tribunal")
        if normen_tribunal is None
        else normen_tribunal
    )
    mandate = tuple(
        SenatsMandat(
            mandat_id=f"{senat_id}-{fall.fall_id.removeprefix(f'{resolved_tribunal.tribunal_id}-')}",
            sequence=index,
            fall_id=fall.fall_id,
            line_id=fall.line_id,
            article_id=fall.article_id,
            entry_id=fall.entry_id,
            section_id=fall.section_id,
            reference_key=fall.reference_key,
            tribunal_kammer=fall.kammer,
            tribunal_urteil=fall.urteil,
            tribunal_verfahren=fall.verfahren,
            fraktion=_fraktion(fall),
            sitzung=_sitzung(fall),
            beschluss=_beschluss(fall),
            mandate_ids=fall.case_ids,
            binding=fall.release_ready and _beschluss(fall) is SenatsBeschluss.GRUNDLEGEND,
            resolution_weight=_resolution_weight(fall),
            deliberation_quorum=_deliberation_quorum(fall),
            mandat_tags=tuple(
                dict.fromkeys(
                    (
                        *fall.fall_tags,
                        _fraktion(fall).value,
                        _sitzung(fall).value,
                        _beschluss(fall).value,
                    )
                )
            ),
            summary=(
                f"{fall.fall_id} elevated by {_fraktion(fall).value} in "
                f"{_sitzung(fall).value} as {_beschluss(fall).value}."
            ),
        )
        for index, fall in enumerate(resolved_tribunal.faelle, start=1)
    )
    if not mandate:
        raise ValueError("verfassungs senat requires at least one mandat")

    severity = "info"
    status = "senat-grundlegend"
    if any(m.beschluss is SenatsBeschluss.UNGUELTIG for m in mandate):
        severity = "critical"
        status = "senat-ungueltig"
    elif any(m.beschluss is SenatsBeschluss.WIRKSAM for m in mandate):
        severity = "warning"
        status = "senat-wirksam"

    senat_signal = TelemetrySignal(
        signal_name="verfassungs-senat",
        boundary=resolved_tribunal.tribunal_signal.boundary,
        correlation_id=senat_id,
        severity=severity,
        status=status,
        metrics={
            "mandat_count": float(len(mandate)),
            "ungueltig_count": float(sum(1 for m in mandate if m.beschluss is SenatsBeschluss.UNGUELTIG)),
            "wirksam_count": float(sum(1 for m in mandate if m.beschluss is SenatsBeschluss.WIRKSAM)),
            "grundlegend_count": float(sum(1 for m in mandate if m.beschluss is SenatsBeschluss.GRUNDLEGEND)),
            "binding_count": float(sum(1 for m in mandate if m.binding)),
            "avg_resolution_weight": round(sum(m.resolution_weight for m in mandate) / len(mandate), 3),
        },
        labels={"senat_id": senat_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_tribunal.final_snapshot.runtime_stage,
        signals=(senat_signal, *resolved_tribunal.final_snapshot.signals),
        alerts=resolved_tribunal.final_snapshot.alerts,
        audit_entries=resolved_tribunal.final_snapshot.audit_entries,
        active_controls=resolved_tribunal.final_snapshot.active_controls,
    )
    return VerfassungsSenat(
        senat_id=senat_id,
        normen_tribunal=resolved_tribunal,
        mandate=mandate,
        senat_signal=senat_signal,
        final_snapshot=final_snapshot,
    )
