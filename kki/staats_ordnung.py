"""Staats ordnung imposing basic law paragraphs as binding Leitstern state norms."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .verfassungs_grundgesetz import (
    GrundgesetzGeltung,
    GrundgesetzParagraph,
    GrundgesetzProzedur,
    GrundgesetzTitel,
    VerfassungsGrundgesetz,
    build_verfassungs_grundgesetz,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class StaatsEbene(str, Enum):
    """State level that classifies one state norm."""

    SCHUTZ_EBENE = "schutz-ebene"
    ORDNUNGS_EBENE = "ordnungs-ebene"
    SOUVERAENITAETS_EBENE = "souveraenitaets-ebene"


class StaatsProzedur(str, Enum):
    """State procedure used to impose the norm."""

    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class StaatsGeltung(str, Enum):
    """Canonical validity of the imposed state norm."""

    GESPERRT = "gesperrt"
    GEORDNET = "geordnet"
    GRUNDLEGEND_GEORDNET = "grundlegend-geordnet"


@dataclass(frozen=True)
class StaatsNorm:
    """One state norm derived from a basic law paragraph."""

    norm_id: str
    sequence: int
    paragraph_id: str
    artikel_id: str
    klausel_id: str
    resolution_id: str
    satz_id: str
    eintrag_id: str
    pfeiler_id: str
    norm_ref_id: str
    abschnitt_id: str
    mandat_id: str
    fall_id: str
    line_id: str
    article_id: str
    entry_id: str
    section_id: str
    reference_key: str
    grundgesetz_titel: GrundgesetzTitel
    grundgesetz_prozedur: GrundgesetzProzedur
    ebene: StaatsEbene
    prozedur: StaatsProzedur
    geltung: StaatsGeltung
    norm_ids: tuple[str, ...]
    canonical: bool
    staats_weight: float
    staats_tier: int
    norm_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "norm_id", _non_empty(self.norm_id, field_name="norm_id"))
        object.__setattr__(self, "paragraph_id", _non_empty(self.paragraph_id, field_name="paragraph_id"))
        object.__setattr__(self, "artikel_id", _non_empty(self.artikel_id, field_name="artikel_id"))
        object.__setattr__(self, "klausel_id", _non_empty(self.klausel_id, field_name="klausel_id"))
        object.__setattr__(self, "resolution_id", _non_empty(self.resolution_id, field_name="resolution_id"))
        object.__setattr__(self, "satz_id", _non_empty(self.satz_id, field_name="satz_id"))
        object.__setattr__(self, "eintrag_id", _non_empty(self.eintrag_id, field_name="eintrag_id"))
        object.__setattr__(self, "pfeiler_id", _non_empty(self.pfeiler_id, field_name="pfeiler_id"))
        object.__setattr__(self, "norm_ref_id", _non_empty(self.norm_ref_id, field_name="norm_ref_id"))
        object.__setattr__(self, "abschnitt_id", _non_empty(self.abschnitt_id, field_name="abschnitt_id"))
        object.__setattr__(self, "mandat_id", _non_empty(self.mandat_id, field_name="mandat_id"))
        object.__setattr__(self, "fall_id", _non_empty(self.fall_id, field_name="fall_id"))
        object.__setattr__(self, "line_id", _non_empty(self.line_id, field_name="line_id"))
        object.__setattr__(self, "article_id", _non_empty(self.article_id, field_name="article_id"))
        object.__setattr__(self, "entry_id", _non_empty(self.entry_id, field_name="entry_id"))
        object.__setattr__(self, "section_id", _non_empty(self.section_id, field_name="section_id"))
        object.__setattr__(self, "reference_key", _non_empty(self.reference_key, field_name="reference_key"))
        object.__setattr__(self, "staats_weight", _clamp01(self.staats_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.staats_tier < 1:
            raise ValueError("staats_tier must be positive")
        if not self.norm_ids:
            raise ValueError("norm_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "norm_id": self.norm_id,
            "sequence": self.sequence,
            "paragraph_id": self.paragraph_id,
            "artikel_id": self.artikel_id,
            "klausel_id": self.klausel_id,
            "resolution_id": self.resolution_id,
            "satz_id": self.satz_id,
            "eintrag_id": self.eintrag_id,
            "pfeiler_id": self.pfeiler_id,
            "norm_ref_id": self.norm_ref_id,
            "abschnitt_id": self.abschnitt_id,
            "mandat_id": self.mandat_id,
            "fall_id": self.fall_id,
            "line_id": self.line_id,
            "article_id": self.article_id,
            "entry_id": self.entry_id,
            "section_id": self.section_id,
            "reference_key": self.reference_key,
            "grundgesetz_titel": self.grundgesetz_titel.value,
            "grundgesetz_prozedur": self.grundgesetz_prozedur.value,
            "ebene": self.ebene.value,
            "prozedur": self.prozedur.value,
            "geltung": self.geltung.value,
            "norm_ids": list(self.norm_ids),
            "canonical": self.canonical,
            "staats_weight": self.staats_weight,
            "staats_tier": self.staats_tier,
            "norm_tags": list(self.norm_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class StaatsOrdnung:
    """State order imposing Leitstern basic law paragraphs as binding state norms."""

    ordnung_id: str
    verfassungs_grundgesetz: VerfassungsGrundgesetz
    normen: tuple[StaatsNorm, ...]
    staats_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "ordnung_id", _non_empty(self.ordnung_id, field_name="ordnung_id"))

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is StaatsGeltung.GESPERRT)

    @property
    def geordnet_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is StaatsGeltung.GEORDNET)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is StaatsGeltung.GRUNDLEGEND_GEORDNET)

    def to_dict(self) -> dict[str, object]:
        return {
            "ordnung_id": self.ordnung_id,
            "verfassungs_grundgesetz": self.verfassungs_grundgesetz.to_dict(),
            "normen": [n.to_dict() for n in self.normen],
            "staats_signal": self.staats_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "gesperrt_norm_ids": list(self.gesperrt_norm_ids),
            "geordnet_norm_ids": list(self.geordnet_norm_ids),
            "grundlegend_norm_ids": list(self.grundlegend_norm_ids),
        }


def _ebene(paragraph: GrundgesetzParagraph) -> StaatsEbene:
    return {
        GrundgesetzTitel.SCHUTZ_TITEL: StaatsEbene.SCHUTZ_EBENE,
        GrundgesetzTitel.ORDNUNGS_TITEL: StaatsEbene.ORDNUNGS_EBENE,
        GrundgesetzTitel.SOUVERAENITAETS_TITEL: StaatsEbene.SOUVERAENITAETS_EBENE,
    }[paragraph.titel]


def _prozedur(paragraph: GrundgesetzParagraph) -> StaatsProzedur:
    return {
        GrundgesetzProzedur.NOTPROZEDUR: StaatsProzedur.NOTPROZEDUR,
        GrundgesetzProzedur.REGELPROTOKOLL: StaatsProzedur.REGELPROTOKOLL,
        GrundgesetzProzedur.PLENARPROTOKOLL: StaatsProzedur.PLENARPROTOKOLL,
    }[paragraph.prozedur]


def _geltung(paragraph: GrundgesetzParagraph) -> StaatsGeltung:
    return {
        GrundgesetzGeltung.GESPERRT: StaatsGeltung.GESPERRT,
        GrundgesetzGeltung.VERBINDLICH: StaatsGeltung.GEORDNET,
        GrundgesetzGeltung.GRUNDGESETZLICH: StaatsGeltung.GRUNDLEGEND_GEORDNET,
    }[paragraph.geltung]


def _staats_weight(paragraph: GrundgesetzParagraph) -> float:
    bonus = {
        StaatsGeltung.GESPERRT: 0.0,
        StaatsGeltung.GEORDNET: 0.04,
        StaatsGeltung.GRUNDLEGEND_GEORDNET: 0.08,
    }[_geltung(paragraph)]
    return round(min(1.0, paragraph.grundgesetz_weight + bonus), 3)


def _staats_tier(paragraph: GrundgesetzParagraph) -> int:
    return {
        StaatsGeltung.GESPERRT: paragraph.grundgesetz_tier,
        StaatsGeltung.GEORDNET: paragraph.grundgesetz_tier + 1,
        StaatsGeltung.GRUNDLEGEND_GEORDNET: paragraph.grundgesetz_tier + 2,
    }[_geltung(paragraph)]


def build_staats_ordnung(
    verfassungs_grundgesetz: VerfassungsGrundgesetz | None = None,
    *,
    ordnung_id: str = "staats-ordnung",
) -> StaatsOrdnung:
    """Build the state order imposing Leitstern basic law paragraphs as state norms."""

    resolved_grundgesetz = (
        build_verfassungs_grundgesetz(grundgesetz_id=f"{ordnung_id}-grundgesetz")
        if verfassungs_grundgesetz is None
        else verfassungs_grundgesetz
    )
    normen = tuple(
        StaatsNorm(
            norm_id=f"{ordnung_id}-{p.paragraph_id.removeprefix(f'{resolved_grundgesetz.grundgesetz_id}-')}",
            sequence=index,
            paragraph_id=p.paragraph_id,
            artikel_id=p.artikel_id,
            klausel_id=p.klausel_id,
            resolution_id=p.resolution_id,
            satz_id=p.satz_id,
            eintrag_id=p.eintrag_id,
            pfeiler_id=p.pfeiler_id,
            norm_ref_id=p.norm_id,
            abschnitt_id=p.abschnitt_id,
            mandat_id=p.mandat_id,
            fall_id=p.fall_id,
            line_id=p.line_id,
            article_id=p.article_id,
            entry_id=p.entry_id,
            section_id=p.section_id,
            reference_key=p.reference_key,
            grundgesetz_titel=p.titel,
            grundgesetz_prozedur=p.prozedur,
            ebene=_ebene(p),
            prozedur=_prozedur(p),
            geltung=_geltung(p),
            norm_ids=p.paragraph_ids,
            canonical=p.canonical and _geltung(p) is StaatsGeltung.GRUNDLEGEND_GEORDNET,
            staats_weight=_staats_weight(p),
            staats_tier=_staats_tier(p),
            norm_tags=tuple(
                dict.fromkeys(
                    (
                        *p.paragraph_tags,
                        _ebene(p).value,
                        _prozedur(p).value,
                        _geltung(p).value,
                    )
                )
            ),
            summary=(
                f"{p.paragraph_id} imposed at {_ebene(p).value} via "
                f"{_prozedur(p).value} with geltung {_geltung(p).value}."
            ),
        )
        for index, p in enumerate(resolved_grundgesetz.paragraphen, start=1)
    )
    if not normen:
        raise ValueError("staats ordnung requires at least one norm")

    severity = "info"
    status = "ordnung-grundlegend-geordnet"
    if any(n.geltung is StaatsGeltung.GESPERRT for n in normen):
        severity = "critical"
        status = "ordnung-gesperrt"
    elif any(n.geltung is StaatsGeltung.GEORDNET for n in normen):
        severity = "warning"
        status = "ordnung-geordnet"

    staats_signal = TelemetrySignal(
        signal_name="staats-ordnung",
        boundary=resolved_grundgesetz.grundgesetz_signal.boundary,
        correlation_id=ordnung_id,
        severity=severity,
        status=status,
        metrics={
            "norm_count": float(len(normen)),
            "gesperrt_count": float(sum(1 for n in normen if n.geltung is StaatsGeltung.GESPERRT)),
            "geordnet_count": float(sum(1 for n in normen if n.geltung is StaatsGeltung.GEORDNET)),
            "grundlegend_count": float(sum(1 for n in normen if n.geltung is StaatsGeltung.GRUNDLEGEND_GEORDNET)),
            "canonical_count": float(sum(1 for n in normen if n.canonical)),
            "avg_staats_weight": round(sum(n.staats_weight for n in normen) / len(normen), 3),
        },
        labels={"ordnung_id": ordnung_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_grundgesetz.final_snapshot.runtime_stage,
        signals=(staats_signal, *resolved_grundgesetz.final_snapshot.signals),
        alerts=resolved_grundgesetz.final_snapshot.alerts,
        audit_entries=resolved_grundgesetz.final_snapshot.audit_entries,
        active_controls=resolved_grundgesetz.final_snapshot.active_controls,
    )
    return StaatsOrdnung(
        ordnung_id=ordnung_id,
        verfassungs_grundgesetz=resolved_grundgesetz,
        normen=normen,
        staats_signal=staats_signal,
        final_snapshot=final_snapshot,
    )
