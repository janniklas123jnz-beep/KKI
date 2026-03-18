"""Bundes charta encoding federal treaty norms as chartered Leitstern federal norms."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .foederal_vertrag import (
    FoederalGeltung,
    FoederalNorm,
    FoederalProzedur,
    FoederalTyp,
    FoederalVertrag,
    build_foederal_vertrag,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class BundesRang(str, Enum):
    """Federal rank that classifies one charter norm."""

    SCHUTZ_RANG = "schutz-rang"
    ORDNUNGS_RANG = "ordnungs-rang"
    SOUVERAENITAETS_RANG = "souveraenitaets-rang"


class BundesProzedur(str, Enum):
    """Federal procedure used to charter the norm."""

    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class BundesGeltung(str, Enum):
    """Canonical validity of the chartered federal norm."""

    GESPERRT = "gesperrt"
    VERBUERGT = "verbuergt"
    GRUNDLEGEND_VERBUERGT = "grundlegend-verbuergt"


@dataclass(frozen=True)
class BundesNorm:
    """One chartered federal norm derived from a federal treaty norm."""

    bundes_norm_id: str
    sequence: int
    foederal_norm_id: str
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
    foederal_typ: FoederalTyp
    foederal_prozedur: FoederalProzedur
    bundes_rang: BundesRang
    prozedur: BundesProzedur
    geltung: BundesGeltung
    bundes_norm_ids: tuple[str, ...]
    canonical: bool
    bundes_weight: float
    bundes_tier: int
    bundes_norm_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "bundes_norm_id", _non_empty(self.bundes_norm_id, field_name="bundes_norm_id"))
        object.__setattr__(self, "foederal_norm_id", _non_empty(self.foederal_norm_id, field_name="foederal_norm_id"))
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
        object.__setattr__(self, "bundes_weight", _clamp01(self.bundes_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.bundes_tier < 1:
            raise ValueError("bundes_tier must be positive")
        if not self.bundes_norm_ids:
            raise ValueError("bundes_norm_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "bundes_norm_id": self.bundes_norm_id,
            "sequence": self.sequence,
            "foederal_norm_id": self.foederal_norm_id,
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
            "foederal_typ": self.foederal_typ.value,
            "foederal_prozedur": self.foederal_prozedur.value,
            "bundes_rang": self.bundes_rang.value,
            "prozedur": self.prozedur.value,
            "geltung": self.geltung.value,
            "bundes_norm_ids": list(self.bundes_norm_ids),
            "canonical": self.canonical,
            "bundes_weight": self.bundes_weight,
            "bundes_tier": self.bundes_tier,
            "bundes_norm_tags": list(self.bundes_norm_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class BundesCharta:
    """Federal charter encoding Leitstern treaty norms as chartered constitutional guarantees."""

    charta_id: str
    foederal_vertrag: FoederalVertrag
    normen: tuple[BundesNorm, ...]
    charta_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "charta_id", _non_empty(self.charta_id, field_name="charta_id"))

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.bundes_norm_id for n in self.normen if n.geltung is BundesGeltung.GESPERRT)

    @property
    def verbuergt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.bundes_norm_id for n in self.normen if n.geltung is BundesGeltung.VERBUERGT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.bundes_norm_id for n in self.normen if n.geltung is BundesGeltung.GRUNDLEGEND_VERBUERGT)

    def to_dict(self) -> dict[str, object]:
        return {
            "charta_id": self.charta_id,
            "foederal_vertrag": self.foederal_vertrag.to_dict(),
            "normen": [n.to_dict() for n in self.normen],
            "charta_signal": self.charta_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "gesperrt_norm_ids": list(self.gesperrt_norm_ids),
            "verbuergt_norm_ids": list(self.verbuergt_norm_ids),
            "grundlegend_norm_ids": list(self.grundlegend_norm_ids),
        }


def _bundes_rang(norm: FoederalNorm) -> BundesRang:
    return {
        FoederalTyp.SCHUTZ_BUND: BundesRang.SCHUTZ_RANG,
        FoederalTyp.ORDNUNGS_BUND: BundesRang.ORDNUNGS_RANG,
        FoederalTyp.SOUVERAENITAETS_BUND: BundesRang.SOUVERAENITAETS_RANG,
    }[norm.foederal_typ]


def _bundes_prozedur(norm: FoederalNorm) -> BundesProzedur:
    return {
        FoederalProzedur.NOTPROZEDUR: BundesProzedur.NOTPROZEDUR,
        FoederalProzedur.REGELPROTOKOLL: BundesProzedur.REGELPROTOKOLL,
        FoederalProzedur.PLENARPROTOKOLL: BundesProzedur.PLENARPROTOKOLL,
    }[norm.prozedur]


def _geltung(norm: FoederalNorm) -> BundesGeltung:
    return {
        FoederalGeltung.GESPERRT: BundesGeltung.GESPERRT,
        FoederalGeltung.FOEDERIERT: BundesGeltung.VERBUERGT,
        FoederalGeltung.GRUNDLEGEND_FOEDERIERT: BundesGeltung.GRUNDLEGEND_VERBUERGT,
    }[norm.geltung]


def _bundes_weight(norm: FoederalNorm) -> float:
    bonus = {
        BundesGeltung.GESPERRT: 0.0,
        BundesGeltung.VERBUERGT: 0.04,
        BundesGeltung.GRUNDLEGEND_VERBUERGT: 0.08,
    }[_geltung(norm)]
    return round(min(1.0, norm.foederal_weight + bonus), 3)


def _bundes_tier(norm: FoederalNorm) -> int:
    return {
        BundesGeltung.GESPERRT: norm.foederal_tier,
        BundesGeltung.VERBUERGT: norm.foederal_tier + 1,
        BundesGeltung.GRUNDLEGEND_VERBUERGT: norm.foederal_tier + 2,
    }[_geltung(norm)]


def build_bundes_charta(
    foederal_vertrag: FoederalVertrag | None = None,
    *,
    charta_id: str = "bundes-charta",
) -> BundesCharta:
    """Build the federal charter encoding Leitstern treaty norms."""

    resolved_vertrag = (
        build_foederal_vertrag(vertrag_id=f"{charta_id}-vertrag")
        if foederal_vertrag is None
        else foederal_vertrag
    )
    normen = tuple(
        BundesNorm(
            bundes_norm_id=f"{charta_id}-{n.foederal_norm_id.removeprefix(f'{resolved_vertrag.vertrag_id}-')}",
            sequence=index,
            foederal_norm_id=n.foederal_norm_id,
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
            foederal_typ=n.foederal_typ,
            foederal_prozedur=n.prozedur,
            bundes_rang=_bundes_rang(n),
            prozedur=_bundes_prozedur(n),
            geltung=_geltung(n),
            bundes_norm_ids=n.foederal_norm_ids,
            canonical=n.canonical and _geltung(n) is BundesGeltung.GRUNDLEGEND_VERBUERGT,
            bundes_weight=_bundes_weight(n),
            bundes_tier=_bundes_tier(n),
            bundes_norm_tags=tuple(
                dict.fromkeys(
                    (
                        *n.foederal_norm_tags,
                        _bundes_rang(n).value,
                        _bundes_prozedur(n).value,
                        _geltung(n).value,
                    )
                )
            ),
            summary=(
                f"{n.foederal_norm_id} chartered as {_bundes_rang(n).value} via "
                f"{_bundes_prozedur(n).value} with geltung {_geltung(n).value}."
            ),
        )
        for index, n in enumerate(resolved_vertrag.normen, start=1)
    )
    if not normen:
        raise ValueError("bundes charta requires at least one norm")

    severity = "info"
    status = "charta-grundlegend-verbuergt"
    if any(n.geltung is BundesGeltung.GESPERRT for n in normen):
        severity = "critical"
        status = "charta-gesperrt"
    elif any(n.geltung is BundesGeltung.VERBUERGT for n in normen):
        severity = "warning"
        status = "charta-verbuergt"

    charta_signal = TelemetrySignal(
        signal_name="bundes-charta",
        boundary=resolved_vertrag.vertrag_signal.boundary,
        correlation_id=charta_id,
        severity=severity,
        status=status,
        metrics={
            "norm_count": float(len(normen)),
            "gesperrt_count": float(sum(1 for n in normen if n.geltung is BundesGeltung.GESPERRT)),
            "verbuergt_count": float(sum(1 for n in normen if n.geltung is BundesGeltung.VERBUERGT)),
            "grundlegend_count": float(sum(1 for n in normen if n.geltung is BundesGeltung.GRUNDLEGEND_VERBUERGT)),
            "canonical_count": float(sum(1 for n in normen if n.canonical)),
            "avg_bundes_weight": round(sum(n.bundes_weight for n in normen) / len(normen), 3),
        },
        labels={"charta_id": charta_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_vertrag.final_snapshot.runtime_stage,
        signals=(charta_signal, *resolved_vertrag.final_snapshot.signals),
        alerts=resolved_vertrag.final_snapshot.alerts,
        audit_entries=resolved_vertrag.final_snapshot.audit_entries,
        active_controls=resolved_vertrag.final_snapshot.active_controls,
    )
    return BundesCharta(
        charta_id=charta_id,
        foederal_vertrag=resolved_vertrag,
        normen=normen,
        charta_signal=charta_signal,
        final_snapshot=final_snapshot,
    )
