"""Grundrechts senat encoding eternal norms as fundamental rights senate resolutions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .ewigkeits_norm import (
    EwigkeitsEintrag,
    EwigkeitsGeltung,
    EwigkeitsNorm,
    EwigkeitsProzedur,
    EwigkeitsTyp,
    build_ewigkeits_norm,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class SenatRang(str, Enum):
    """Senate rank that classifies one fundamental rights resolution."""

    SCHUTZ_SENAT = "schutz-senat"
    ORDNUNGS_SENAT = "ordnungs-senat"
    SOUVERAENITAETS_SENAT = "souveraenitaets-senat"


class SenatProzedur(str, Enum):
    """Senate procedure used to resolve the fundamental right."""

    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SenatGeltung(str, Enum):
    """Canonical validity of the senate fundamental rights resolution."""

    GESPERRT = "gesperrt"
    BESCHLOSSEN = "beschlossen"
    GRUNDLEGEND_BESCHLOSSEN = "grundlegend-beschlossen"


@dataclass(frozen=True)
class SenatNorm:
    """One senate fundamental rights norm derived from an eternal norm entry."""

    senat_norm_id: str
    sequence: int
    ewigkeits_eintrag_id: str
    paragraph_id: str
    artikel_id: str
    klausel_id: str
    resolution_id: str
    satz_id: str
    eintrag_id: str
    pfeiler_id: str
    abschnitt_id: str
    mandat_id: str
    fall_id: str
    line_id: str
    article_id: str
    entry_id: str
    section_id: str
    reference_key: str
    ewigkeits_typ: EwigkeitsTyp
    ewigkeits_prozedur: EwigkeitsProzedur
    senat_rang: SenatRang
    prozedur: SenatProzedur
    geltung: SenatGeltung
    senat_norm_ids: tuple[str, ...]
    canonical: bool
    senat_weight: float
    senat_tier: int
    senat_norm_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "senat_norm_id", _non_empty(self.senat_norm_id, field_name="senat_norm_id"))
        object.__setattr__(self, "ewigkeits_eintrag_id", _non_empty(self.ewigkeits_eintrag_id, field_name="ewigkeits_eintrag_id"))
        object.__setattr__(self, "paragraph_id", _non_empty(self.paragraph_id, field_name="paragraph_id"))
        object.__setattr__(self, "artikel_id", _non_empty(self.artikel_id, field_name="artikel_id"))
        object.__setattr__(self, "klausel_id", _non_empty(self.klausel_id, field_name="klausel_id"))
        object.__setattr__(self, "resolution_id", _non_empty(self.resolution_id, field_name="resolution_id"))
        object.__setattr__(self, "satz_id", _non_empty(self.satz_id, field_name="satz_id"))
        object.__setattr__(self, "eintrag_id", _non_empty(self.eintrag_id, field_name="eintrag_id"))
        object.__setattr__(self, "pfeiler_id", _non_empty(self.pfeiler_id, field_name="pfeiler_id"))
        object.__setattr__(self, "abschnitt_id", _non_empty(self.abschnitt_id, field_name="abschnitt_id"))
        object.__setattr__(self, "mandat_id", _non_empty(self.mandat_id, field_name="mandat_id"))
        object.__setattr__(self, "fall_id", _non_empty(self.fall_id, field_name="fall_id"))
        object.__setattr__(self, "line_id", _non_empty(self.line_id, field_name="line_id"))
        object.__setattr__(self, "article_id", _non_empty(self.article_id, field_name="article_id"))
        object.__setattr__(self, "entry_id", _non_empty(self.entry_id, field_name="entry_id"))
        object.__setattr__(self, "section_id", _non_empty(self.section_id, field_name="section_id"))
        object.__setattr__(self, "reference_key", _non_empty(self.reference_key, field_name="reference_key"))
        object.__setattr__(self, "senat_weight", _clamp01(self.senat_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.senat_tier < 1:
            raise ValueError("senat_tier must be positive")
        if not self.senat_norm_ids:
            raise ValueError("senat_norm_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "senat_norm_id": self.senat_norm_id,
            "sequence": self.sequence,
            "ewigkeits_eintrag_id": self.ewigkeits_eintrag_id,
            "paragraph_id": self.paragraph_id,
            "artikel_id": self.artikel_id,
            "klausel_id": self.klausel_id,
            "resolution_id": self.resolution_id,
            "satz_id": self.satz_id,
            "eintrag_id": self.eintrag_id,
            "pfeiler_id": self.pfeiler_id,
            "abschnitt_id": self.abschnitt_id,
            "mandat_id": self.mandat_id,
            "fall_id": self.fall_id,
            "line_id": self.line_id,
            "article_id": self.article_id,
            "entry_id": self.entry_id,
            "section_id": self.section_id,
            "reference_key": self.reference_key,
            "ewigkeits_typ": self.ewigkeits_typ.value,
            "ewigkeits_prozedur": self.ewigkeits_prozedur.value,
            "senat_rang": self.senat_rang.value,
            "prozedur": self.prozedur.value,
            "geltung": self.geltung.value,
            "senat_norm_ids": list(self.senat_norm_ids),
            "canonical": self.canonical,
            "senat_weight": self.senat_weight,
            "senat_tier": self.senat_tier,
            "senat_norm_tags": list(self.senat_norm_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class GrundrechtsSenat:
    """Fundamental rights senate encoding eternal Leitstern norms as senate resolutions."""

    senat_id: str
    ewigkeits_norm: EwigkeitsNorm
    normen: tuple[SenatNorm, ...]
    senat_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "senat_id", _non_empty(self.senat_id, field_name="senat_id"))

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.senat_norm_id for n in self.normen if n.geltung is SenatGeltung.GESPERRT)

    @property
    def beschlossen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.senat_norm_id for n in self.normen if n.geltung is SenatGeltung.BESCHLOSSEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.senat_norm_id for n in self.normen if n.geltung is SenatGeltung.GRUNDLEGEND_BESCHLOSSEN)

    def to_dict(self) -> dict[str, object]:
        return {
            "senat_id": self.senat_id,
            "ewigkeits_norm": self.ewigkeits_norm.to_dict(),
            "normen": [n.to_dict() for n in self.normen],
            "senat_signal": self.senat_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "gesperrt_norm_ids": list(self.gesperrt_norm_ids),
            "beschlossen_norm_ids": list(self.beschlossen_norm_ids),
            "grundlegend_norm_ids": list(self.grundlegend_norm_ids),
        }


def _senat_rang(eintrag: EwigkeitsEintrag) -> SenatRang:
    return {
        EwigkeitsTyp.SCHUTZ_EWIGKEIT: SenatRang.SCHUTZ_SENAT,
        EwigkeitsTyp.ORDNUNGS_EWIGKEIT: SenatRang.ORDNUNGS_SENAT,
        EwigkeitsTyp.SOUVERAENITAETS_EWIGKEIT: SenatRang.SOUVERAENITAETS_SENAT,
    }[eintrag.ewigkeits_typ]


def _senat_prozedur(eintrag: EwigkeitsEintrag) -> SenatProzedur:
    return {
        EwigkeitsProzedur.NOTPROZEDUR: SenatProzedur.NOTPROZEDUR,
        EwigkeitsProzedur.REGELPROTOKOLL: SenatProzedur.REGELPROTOKOLL,
        EwigkeitsProzedur.PLENARPROTOKOLL: SenatProzedur.PLENARPROTOKOLL,
    }[eintrag.prozedur]


def _geltung(eintrag: EwigkeitsEintrag) -> SenatGeltung:
    return {
        EwigkeitsGeltung.GESPERRT: SenatGeltung.GESPERRT,
        EwigkeitsGeltung.VEREWIGT: SenatGeltung.BESCHLOSSEN,
        EwigkeitsGeltung.GRUNDLEGEND_VEREWIGT: SenatGeltung.GRUNDLEGEND_BESCHLOSSEN,
    }[eintrag.geltung]


def _senat_weight(eintrag: EwigkeitsEintrag) -> float:
    bonus = {
        SenatGeltung.GESPERRT: 0.0,
        SenatGeltung.BESCHLOSSEN: 0.04,
        SenatGeltung.GRUNDLEGEND_BESCHLOSSEN: 0.08,
    }[_geltung(eintrag)]
    return round(min(1.0, eintrag.ewigkeits_weight + bonus), 3)


def _senat_tier(eintrag: EwigkeitsEintrag) -> int:
    return {
        SenatGeltung.GESPERRT: eintrag.ewigkeits_tier,
        SenatGeltung.BESCHLOSSEN: eintrag.ewigkeits_tier + 1,
        SenatGeltung.GRUNDLEGEND_BESCHLOSSEN: eintrag.ewigkeits_tier + 2,
    }[_geltung(eintrag)]


def build_grundrechts_senat(
    ewigkeits_norm: EwigkeitsNorm | None = None,
    *,
    senat_id: str = "grundrechts-senat",
) -> GrundrechtsSenat:
    """Build the fundamental rights senate encoding eternal Leitstern norms."""

    resolved_norm = (
        build_ewigkeits_norm(norm_id=f"{senat_id}-norm")
        if ewigkeits_norm is None
        else ewigkeits_norm
    )
    normen = tuple(
        SenatNorm(
            senat_norm_id=f"{senat_id}-{e.ewigkeits_eintrag_id.removeprefix(f'{resolved_norm.norm_id}-')}",
            sequence=index,
            ewigkeits_eintrag_id=e.ewigkeits_eintrag_id,
            paragraph_id=e.paragraph_id,
            artikel_id=e.artikel_id,
            klausel_id=e.klausel_id,
            resolution_id=e.resolution_id,
            satz_id=e.satz_id,
            eintrag_id=e.eintrag_id,
            pfeiler_id=e.pfeiler_id,
            abschnitt_id=e.abschnitt_id,
            mandat_id=e.mandat_id,
            fall_id=e.fall_id,
            line_id=e.line_id,
            article_id=e.article_id,
            entry_id=e.entry_id,
            section_id=e.section_id,
            reference_key=e.reference_key,
            ewigkeits_typ=e.ewigkeits_typ,
            ewigkeits_prozedur=e.prozedur,
            senat_rang=_senat_rang(e),
            prozedur=_senat_prozedur(e),
            geltung=_geltung(e),
            senat_norm_ids=e.ewigkeits_eintrag_ids,
            canonical=e.canonical and _geltung(e) is SenatGeltung.GRUNDLEGEND_BESCHLOSSEN,
            senat_weight=_senat_weight(e),
            senat_tier=_senat_tier(e),
            senat_norm_tags=tuple(
                dict.fromkeys(
                    (
                        *e.ewigkeits_eintrag_tags,
                        _senat_rang(e).value,
                        _senat_prozedur(e).value,
                        _geltung(e).value,
                    )
                )
            ),
            summary=(
                f"{e.ewigkeits_eintrag_id} resolved as {_senat_rang(e).value} via "
                f"{_senat_prozedur(e).value} with geltung {_geltung(e).value}."
            ),
        )
        for index, e in enumerate(resolved_norm.eintraege, start=1)
    )
    if not normen:
        raise ValueError("grundrechts senat requires at least one norm")

    severity = "info"
    status = "senat-grundlegend-beschlossen"
    if any(n.geltung is SenatGeltung.GESPERRT for n in normen):
        severity = "critical"
        status = "senat-gesperrt"
    elif any(n.geltung is SenatGeltung.BESCHLOSSEN for n in normen):
        severity = "warning"
        status = "senat-beschlossen"

    senat_signal = TelemetrySignal(
        signal_name="grundrechts-senat",
        boundary=resolved_norm.norm_signal.boundary,
        correlation_id=senat_id,
        severity=severity,
        status=status,
        metrics={
            "norm_count": float(len(normen)),
            "gesperrt_count": float(sum(1 for n in normen if n.geltung is SenatGeltung.GESPERRT)),
            "beschlossen_count": float(sum(1 for n in normen if n.geltung is SenatGeltung.BESCHLOSSEN)),
            "grundlegend_count": float(sum(1 for n in normen if n.geltung is SenatGeltung.GRUNDLEGEND_BESCHLOSSEN)),
            "canonical_count": float(sum(1 for n in normen if n.canonical)),
            "avg_senat_weight": round(sum(n.senat_weight for n in normen) / len(normen), 3),
        },
        labels={"senat_id": senat_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_norm.final_snapshot.runtime_stage,
        signals=(senat_signal, *resolved_norm.final_snapshot.signals),
        alerts=resolved_norm.final_snapshot.alerts,
        audit_entries=resolved_norm.final_snapshot.audit_entries,
        active_controls=resolved_norm.final_snapshot.active_controls,
    )
    return GrundrechtsSenat(
        senat_id=senat_id,
        ewigkeits_norm=resolved_norm,
        normen=normen,
        senat_signal=senat_signal,
        final_snapshot=final_snapshot,
    )
