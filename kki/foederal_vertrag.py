"""Foederal vertrag encoding union acts as federally ratified Leitstern treaty norms."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .unions_akt import (
    UnionsAkt,
    UnionsGeltung,
    UnionsNorm,
    UnionsProzedur,
    UnionsTyp,
    build_unions_akt,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class FoederalTyp(str, Enum):
    """Federal type that classifies one treaty norm."""

    SCHUTZ_BUND = "schutz-bund"
    ORDNUNGS_BUND = "ordnungs-bund"
    SOUVERAENITAETS_BUND = "souveraenitaets-bund"


class FoederalProzedur(str, Enum):
    """Federal procedure used to ratify the treaty."""

    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class FoederalGeltung(str, Enum):
    """Canonical validity of the federal treaty norm."""

    GESPERRT = "gesperrt"
    FOEDERIERT = "foederiert"
    GRUNDLEGEND_FOEDERIERT = "grundlegend-foederiert"


@dataclass(frozen=True)
class FoederalNorm:
    """One federal treaty norm derived from a union act norm."""

    foederal_norm_id: str
    sequence: int
    unions_norm_id: str
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
    unions_typ: UnionsTyp
    unions_prozedur: UnionsProzedur
    foederal_typ: FoederalTyp
    prozedur: FoederalProzedur
    geltung: FoederalGeltung
    foederal_norm_ids: tuple[str, ...]
    canonical: bool
    foederal_weight: float
    foederal_tier: int
    foederal_norm_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "foederal_norm_id", _non_empty(self.foederal_norm_id, field_name="foederal_norm_id"))
        object.__setattr__(self, "unions_norm_id", _non_empty(self.unions_norm_id, field_name="unions_norm_id"))
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
        object.__setattr__(self, "foederal_weight", _clamp01(self.foederal_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.foederal_tier < 1:
            raise ValueError("foederal_tier must be positive")
        if not self.foederal_norm_ids:
            raise ValueError("foederal_norm_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "foederal_norm_id": self.foederal_norm_id,
            "sequence": self.sequence,
            "unions_norm_id": self.unions_norm_id,
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
            "unions_typ": self.unions_typ.value,
            "unions_prozedur": self.unions_prozedur.value,
            "foederal_typ": self.foederal_typ.value,
            "prozedur": self.prozedur.value,
            "geltung": self.geltung.value,
            "foederal_norm_ids": list(self.foederal_norm_ids),
            "canonical": self.canonical,
            "foederal_weight": self.foederal_weight,
            "foederal_tier": self.foederal_tier,
            "foederal_norm_tags": list(self.foederal_norm_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class FoederalVertrag:
    """Federal treaty encoding Leitstern union acts as federally ratified constitutional norms."""

    vertrag_id: str
    unions_akt: UnionsAkt
    normen: tuple[FoederalNorm, ...]
    vertrag_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "vertrag_id", _non_empty(self.vertrag_id, field_name="vertrag_id"))

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.foederal_norm_id for n in self.normen if n.geltung is FoederalGeltung.GESPERRT)

    @property
    def foederiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.foederal_norm_id for n in self.normen if n.geltung is FoederalGeltung.FOEDERIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.foederal_norm_id for n in self.normen if n.geltung is FoederalGeltung.GRUNDLEGEND_FOEDERIERT)

    def to_dict(self) -> dict[str, object]:
        return {
            "vertrag_id": self.vertrag_id,
            "unions_akt": self.unions_akt.to_dict(),
            "normen": [n.to_dict() for n in self.normen],
            "vertrag_signal": self.vertrag_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "gesperrt_norm_ids": list(self.gesperrt_norm_ids),
            "foederiert_norm_ids": list(self.foederiert_norm_ids),
            "grundlegend_norm_ids": list(self.grundlegend_norm_ids),
        }


def _foederal_typ(norm: UnionsNorm) -> FoederalTyp:
    return {
        UnionsTyp.SCHUTZ_UNION: FoederalTyp.SCHUTZ_BUND,
        UnionsTyp.ORDNUNGS_UNION: FoederalTyp.ORDNUNGS_BUND,
        UnionsTyp.SOUVERAENITAETS_UNION: FoederalTyp.SOUVERAENITAETS_BUND,
    }[norm.unions_typ]


def _foederal_prozedur(norm: UnionsNorm) -> FoederalProzedur:
    return {
        UnionsProzedur.NOTPROZEDUR: FoederalProzedur.NOTPROZEDUR,
        UnionsProzedur.REGELPROTOKOLL: FoederalProzedur.REGELPROTOKOLL,
        UnionsProzedur.PLENARPROTOKOLL: FoederalProzedur.PLENARPROTOKOLL,
    }[norm.prozedur]


def _geltung(norm: UnionsNorm) -> FoederalGeltung:
    return {
        UnionsGeltung.GESPERRT: FoederalGeltung.GESPERRT,
        UnionsGeltung.VEREINT: FoederalGeltung.FOEDERIERT,
        UnionsGeltung.GRUNDLEGEND_VEREINT: FoederalGeltung.GRUNDLEGEND_FOEDERIERT,
    }[norm.geltung]


def _foederal_weight(norm: UnionsNorm) -> float:
    bonus = {
        FoederalGeltung.GESPERRT: 0.0,
        FoederalGeltung.FOEDERIERT: 0.04,
        FoederalGeltung.GRUNDLEGEND_FOEDERIERT: 0.08,
    }[_geltung(norm)]
    return round(min(1.0, norm.unions_weight + bonus), 3)


def _foederal_tier(norm: UnionsNorm) -> int:
    return {
        FoederalGeltung.GESPERRT: norm.unions_tier,
        FoederalGeltung.FOEDERIERT: norm.unions_tier + 1,
        FoederalGeltung.GRUNDLEGEND_FOEDERIERT: norm.unions_tier + 2,
    }[_geltung(norm)]


def build_foederal_vertrag(
    unions_akt: UnionsAkt | None = None,
    *,
    vertrag_id: str = "foederal-vertrag",
) -> FoederalVertrag:
    """Build the federal treaty encoding Leitstern union acts."""

    resolved_akt = (
        build_unions_akt(akt_id=f"{vertrag_id}-akt")
        if unions_akt is None
        else unions_akt
    )
    normen = tuple(
        FoederalNorm(
            foederal_norm_id=f"{vertrag_id}-{n.unions_norm_id.removeprefix(f'{resolved_akt.akt_id}-')}",
            sequence=index,
            unions_norm_id=n.unions_norm_id,
            paragraph_id=n.paragraph_id,
            artikel_id=n.artikel_id,
            klausel_id=n.klausel_id,
            resolution_id=n.resolution_id,
            satz_id=n.satz_id,
            eintrag_id=n.eintrag_id,
            pfeiler_id=n.pfeiler_id,
            abschnitt_id=n.abschnitt_id,
            mandat_id=n.mandat_id,
            fall_id=n.fall_id,
            line_id=n.line_id,
            article_id=n.article_id,
            entry_id=n.entry_id,
            section_id=n.section_id,
            reference_key=n.reference_key,
            unions_typ=n.unions_typ,
            unions_prozedur=n.prozedur,
            foederal_typ=_foederal_typ(n),
            prozedur=_foederal_prozedur(n),
            geltung=_geltung(n),
            foederal_norm_ids=n.unions_norm_ids,
            canonical=n.canonical and _geltung(n) is FoederalGeltung.GRUNDLEGEND_FOEDERIERT,
            foederal_weight=_foederal_weight(n),
            foederal_tier=_foederal_tier(n),
            foederal_norm_tags=tuple(
                dict.fromkeys(
                    (
                        *n.unions_norm_tags,
                        _foederal_typ(n).value,
                        _foederal_prozedur(n).value,
                        _geltung(n).value,
                    )
                )
            ),
            summary=(
                f"{n.unions_norm_id} ratified as {_foederal_typ(n).value} via "
                f"{_foederal_prozedur(n).value} with geltung {_geltung(n).value}."
            ),
        )
        for index, n in enumerate(resolved_akt.normen, start=1)
    )
    if not normen:
        raise ValueError("foederal vertrag requires at least one norm")

    severity = "info"
    status = "vertrag-grundlegend-foederiert"
    if any(n.geltung is FoederalGeltung.GESPERRT for n in normen):
        severity = "critical"
        status = "vertrag-gesperrt"
    elif any(n.geltung is FoederalGeltung.FOEDERIERT for n in normen):
        severity = "warning"
        status = "vertrag-foederiert"

    vertrag_signal = TelemetrySignal(
        signal_name="foederal-vertrag",
        boundary=resolved_akt.akt_signal.boundary,
        correlation_id=vertrag_id,
        severity=severity,
        status=status,
        metrics={
            "norm_count": float(len(normen)),
            "gesperrt_count": float(sum(1 for n in normen if n.geltung is FoederalGeltung.GESPERRT)),
            "foederiert_count": float(sum(1 for n in normen if n.geltung is FoederalGeltung.FOEDERIERT)),
            "grundlegend_count": float(sum(1 for n in normen if n.geltung is FoederalGeltung.GRUNDLEGEND_FOEDERIERT)),
            "canonical_count": float(sum(1 for n in normen if n.canonical)),
            "avg_foederal_weight": round(sum(n.foederal_weight for n in normen) / len(normen), 3),
        },
        labels={"vertrag_id": vertrag_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_akt.final_snapshot.runtime_stage,
        signals=(vertrag_signal, *resolved_akt.final_snapshot.signals),
        alerts=resolved_akt.final_snapshot.alerts,
        audit_entries=resolved_akt.final_snapshot.audit_entries,
        active_controls=resolved_akt.final_snapshot.active_controls,
    )
    return FoederalVertrag(
        vertrag_id=vertrag_id,
        unions_akt=resolved_akt,
        normen=normen,
        vertrag_signal=vertrag_signal,
        final_snapshot=final_snapshot,
    )
