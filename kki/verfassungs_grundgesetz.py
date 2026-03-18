"""Verfassungs grundgesetz enshrining constitutional articles as the supreme Leitstern basic law."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .leitstern_konstitution import (
    KonstitutionsArtikel,
    KonstitutionsEbene,
    KonstitutionsProzedur,
    KonstitutionsRang,
    LeitsternKonstitution,
    build_leitstern_konstitution,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class GrundgesetzTitel(str, Enum):
    """Basic law title that classifies one supreme paragraph."""

    SCHUTZ_TITEL = "schutz-titel"
    ORDNUNGS_TITEL = "ordnungs-titel"
    SOUVERAENITAETS_TITEL = "souveraenitaets-titel"


class GrundgesetzProzedur(str, Enum):
    """Basic law procedure used to enshrine the paragraph."""

    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class GrundgesetzGeltung(str, Enum):
    """Canonical validity of the enshrined basic law paragraph."""

    GESPERRT = "gesperrt"
    VERBINDLICH = "verbindlich"
    GRUNDGESETZLICH = "grundgesetzlich"


@dataclass(frozen=True)
class GrundgesetzParagraph:
    """One supreme basic law paragraph derived from a constitutional article."""

    paragraph_id: str
    sequence: int
    artikel_id: str
    klausel_id: str
    artikel_ref_id: str
    resolution_id: str
    satz_id: str
    eintrag_id: str
    pfeiler_id: str
    norm_id: str
    abschnitt_id: str
    mandat_id: str
    fall_id: str
    line_id: str
    article_id: str
    entry_id: str
    section_id: str
    reference_key: str
    konstitutions_ebene: KonstitutionsEbene
    konstitutions_prozedur: KonstitutionsProzedur
    titel: GrundgesetzTitel
    prozedur: GrundgesetzProzedur
    geltung: GrundgesetzGeltung
    paragraph_ids: tuple[str, ...]
    canonical: bool
    grundgesetz_weight: float
    grundgesetz_tier: int
    paragraph_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "paragraph_id", _non_empty(self.paragraph_id, field_name="paragraph_id"))
        object.__setattr__(self, "artikel_id", _non_empty(self.artikel_id, field_name="artikel_id"))
        object.__setattr__(self, "klausel_id", _non_empty(self.klausel_id, field_name="klausel_id"))
        object.__setattr__(self, "artikel_ref_id", _non_empty(self.artikel_ref_id, field_name="artikel_ref_id"))
        object.__setattr__(self, "resolution_id", _non_empty(self.resolution_id, field_name="resolution_id"))
        object.__setattr__(self, "satz_id", _non_empty(self.satz_id, field_name="satz_id"))
        object.__setattr__(self, "eintrag_id", _non_empty(self.eintrag_id, field_name="eintrag_id"))
        object.__setattr__(self, "pfeiler_id", _non_empty(self.pfeiler_id, field_name="pfeiler_id"))
        object.__setattr__(self, "norm_id", _non_empty(self.norm_id, field_name="norm_id"))
        object.__setattr__(self, "abschnitt_id", _non_empty(self.abschnitt_id, field_name="abschnitt_id"))
        object.__setattr__(self, "mandat_id", _non_empty(self.mandat_id, field_name="mandat_id"))
        object.__setattr__(self, "fall_id", _non_empty(self.fall_id, field_name="fall_id"))
        object.__setattr__(self, "line_id", _non_empty(self.line_id, field_name="line_id"))
        object.__setattr__(self, "article_id", _non_empty(self.article_id, field_name="article_id"))
        object.__setattr__(self, "entry_id", _non_empty(self.entry_id, field_name="entry_id"))
        object.__setattr__(self, "section_id", _non_empty(self.section_id, field_name="section_id"))
        object.__setattr__(self, "reference_key", _non_empty(self.reference_key, field_name="reference_key"))
        object.__setattr__(self, "grundgesetz_weight", _clamp01(self.grundgesetz_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.grundgesetz_tier < 1:
            raise ValueError("grundgesetz_tier must be positive")
        if not self.paragraph_ids:
            raise ValueError("paragraph_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "paragraph_id": self.paragraph_id,
            "sequence": self.sequence,
            "artikel_id": self.artikel_id,
            "klausel_id": self.klausel_id,
            "artikel_ref_id": self.artikel_ref_id,
            "resolution_id": self.resolution_id,
            "satz_id": self.satz_id,
            "eintrag_id": self.eintrag_id,
            "pfeiler_id": self.pfeiler_id,
            "norm_id": self.norm_id,
            "abschnitt_id": self.abschnitt_id,
            "mandat_id": self.mandat_id,
            "fall_id": self.fall_id,
            "line_id": self.line_id,
            "article_id": self.article_id,
            "entry_id": self.entry_id,
            "section_id": self.section_id,
            "reference_key": self.reference_key,
            "konstitutions_ebene": self.konstitutions_ebene.value,
            "konstitutions_prozedur": self.konstitutions_prozedur.value,
            "titel": self.titel.value,
            "prozedur": self.prozedur.value,
            "geltung": self.geltung.value,
            "paragraph_ids": list(self.paragraph_ids),
            "canonical": self.canonical,
            "grundgesetz_weight": self.grundgesetz_weight,
            "grundgesetz_tier": self.grundgesetz_tier,
            "paragraph_tags": list(self.paragraph_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class VerfassungsGrundgesetz:
    """The supreme Leitstern basic law enshrining all constitutional articles."""

    grundgesetz_id: str
    leitstern_konstitution: LeitsternKonstitution
    paragraphen: tuple[GrundgesetzParagraph, ...]
    grundgesetz_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "grundgesetz_id", _non_empty(self.grundgesetz_id, field_name="grundgesetz_id"))

    @property
    def gesperrt_paragraph_ids(self) -> tuple[str, ...]:
        return tuple(p.paragraph_id for p in self.paragraphen if p.geltung is GrundgesetzGeltung.GESPERRT)

    @property
    def verbindlich_paragraph_ids(self) -> tuple[str, ...]:
        return tuple(p.paragraph_id for p in self.paragraphen if p.geltung is GrundgesetzGeltung.VERBINDLICH)

    @property
    def grundgesetzlich_paragraph_ids(self) -> tuple[str, ...]:
        return tuple(p.paragraph_id for p in self.paragraphen if p.geltung is GrundgesetzGeltung.GRUNDGESETZLICH)

    def to_dict(self) -> dict[str, object]:
        return {
            "grundgesetz_id": self.grundgesetz_id,
            "leitstern_konstitution": self.leitstern_konstitution.to_dict(),
            "paragraphen": [p.to_dict() for p in self.paragraphen],
            "grundgesetz_signal": self.grundgesetz_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "gesperrt_paragraph_ids": list(self.gesperrt_paragraph_ids),
            "verbindlich_paragraph_ids": list(self.verbindlich_paragraph_ids),
            "grundgesetzlich_paragraph_ids": list(self.grundgesetzlich_paragraph_ids),
        }


def _titel(artikel: KonstitutionsArtikel) -> GrundgesetzTitel:
    return {
        KonstitutionsEbene.SCHUTZ_EBENE: GrundgesetzTitel.SCHUTZ_TITEL,
        KonstitutionsEbene.ORDNUNGS_EBENE: GrundgesetzTitel.ORDNUNGS_TITEL,
        KonstitutionsEbene.SOUVERAENITAETS_EBENE: GrundgesetzTitel.SOUVERAENITAETS_TITEL,
    }[artikel.ebene]


def _prozedur(artikel: KonstitutionsArtikel) -> GrundgesetzProzedur:
    return {
        KonstitutionsProzedur.NOTPROZEDUR: GrundgesetzProzedur.NOTPROZEDUR,
        KonstitutionsProzedur.REGELPROTOKOLL: GrundgesetzProzedur.REGELPROTOKOLL,
        KonstitutionsProzedur.PLENARPROTOKOLL: GrundgesetzProzedur.PLENARPROTOKOLL,
    }[artikel.prozedur]


def _geltung(artikel: KonstitutionsArtikel) -> GrundgesetzGeltung:
    return {
        KonstitutionsRang.GESPERRT: GrundgesetzGeltung.GESPERRT,
        KonstitutionsRang.KONSTITUIERT: GrundgesetzGeltung.VERBINDLICH,
        KonstitutionsRang.GRUNDLEGEND_KONSTITUIERT: GrundgesetzGeltung.GRUNDGESETZLICH,
    }[artikel.rang]


def _grundgesetz_weight(artikel: KonstitutionsArtikel) -> float:
    bonus = {
        GrundgesetzGeltung.GESPERRT: 0.0,
        GrundgesetzGeltung.VERBINDLICH: 0.04,
        GrundgesetzGeltung.GRUNDGESETZLICH: 0.08,
    }[_geltung(artikel)]
    return round(min(1.0, artikel.konstitutions_weight + bonus), 3)


def _grundgesetz_tier(artikel: KonstitutionsArtikel) -> int:
    return {
        GrundgesetzGeltung.GESPERRT: artikel.konstitutions_tier,
        GrundgesetzGeltung.VERBINDLICH: artikel.konstitutions_tier + 1,
        GrundgesetzGeltung.GRUNDGESETZLICH: artikel.konstitutions_tier + 2,
    }[_geltung(artikel)]


def build_verfassungs_grundgesetz(
    leitstern_konstitution: LeitsternKonstitution | None = None,
    *,
    grundgesetz_id: str = "verfassungs-grundgesetz",
) -> VerfassungsGrundgesetz:
    """Build the supreme Leitstern basic law from constitutional articles."""

    resolved_konstitution = (
        build_leitstern_konstitution(konstitutions_id=f"{grundgesetz_id}-konstitution")
        if leitstern_konstitution is None
        else leitstern_konstitution
    )
    paragraphen = tuple(
        GrundgesetzParagraph(
            paragraph_id=f"{grundgesetz_id}-{a.artikel_id.removeprefix(f'{resolved_konstitution.konstitutions_id}-')}",
            sequence=index,
            artikel_id=a.artikel_id,
            klausel_id=a.klausel_id,
            artikel_ref_id=a.artikel_ref_id,
            resolution_id=a.resolution_id,
            satz_id=a.satz_id,
            eintrag_id=a.eintrag_id,
            pfeiler_id=a.pfeiler_id,
            norm_id=a.norm_id,
            abschnitt_id=a.abschnitt_id,
            mandat_id=a.mandat_id,
            fall_id=a.fall_id,
            line_id=a.line_id,
            article_id=a.article_id,
            entry_id=a.entry_id,
            section_id=a.section_id,
            reference_key=a.reference_key,
            konstitutions_ebene=a.ebene,
            konstitutions_prozedur=a.prozedur,
            titel=_titel(a),
            prozedur=_prozedur(a),
            geltung=_geltung(a),
            paragraph_ids=a.artikel_ids,
            canonical=a.canonical and _geltung(a) is GrundgesetzGeltung.GRUNDGESETZLICH,
            grundgesetz_weight=_grundgesetz_weight(a),
            grundgesetz_tier=_grundgesetz_tier(a),
            paragraph_tags=tuple(
                dict.fromkeys(
                    (
                        *a.artikel_tags,
                        _titel(a).value,
                        _prozedur(a).value,
                        _geltung(a).value,
                    )
                )
            ),
            summary=(
                f"{a.artikel_id} enshrined as {_titel(a).value} via "
                f"{_prozedur(a).value} with geltung {_geltung(a).value}."
            ),
        )
        for index, a in enumerate(resolved_konstitution.artikel, start=1)
    )
    if not paragraphen:
        raise ValueError("verfassungs grundgesetz requires at least one paragraph")

    severity = "info"
    status = "grundgesetz-grundgesetzlich"
    if any(p.geltung is GrundgesetzGeltung.GESPERRT for p in paragraphen):
        severity = "critical"
        status = "grundgesetz-gesperrt"
    elif any(p.geltung is GrundgesetzGeltung.VERBINDLICH for p in paragraphen):
        severity = "warning"
        status = "grundgesetz-verbindlich"

    grundgesetz_signal = TelemetrySignal(
        signal_name="verfassungs-grundgesetz",
        boundary=resolved_konstitution.konstitutions_signal.boundary,
        correlation_id=grundgesetz_id,
        severity=severity,
        status=status,
        metrics={
            "paragraph_count": float(len(paragraphen)),
            "gesperrt_count": float(sum(1 for p in paragraphen if p.geltung is GrundgesetzGeltung.GESPERRT)),
            "verbindlich_count": float(sum(1 for p in paragraphen if p.geltung is GrundgesetzGeltung.VERBINDLICH)),
            "grundgesetzlich_count": float(sum(1 for p in paragraphen if p.geltung is GrundgesetzGeltung.GRUNDGESETZLICH)),
            "canonical_count": float(sum(1 for p in paragraphen if p.canonical)),
            "avg_grundgesetz_weight": round(sum(p.grundgesetz_weight for p in paragraphen) / len(paragraphen), 3),
        },
        labels={"grundgesetz_id": grundgesetz_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_konstitution.final_snapshot.runtime_stage,
        signals=(grundgesetz_signal, *resolved_konstitution.final_snapshot.signals),
        alerts=resolved_konstitution.final_snapshot.alerts,
        audit_entries=resolved_konstitution.final_snapshot.audit_entries,
        active_controls=resolved_konstitution.final_snapshot.active_controls,
    )
    return VerfassungsGrundgesetz(
        grundgesetz_id=grundgesetz_id,
        leitstern_konstitution=resolved_konstitution,
        paragraphen=paragraphen,
        grundgesetz_signal=grundgesetz_signal,
        final_snapshot=final_snapshot,
    )
