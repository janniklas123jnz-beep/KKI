"""Souveraenitaets akt ratifying charter articles into operative Leitstern sovereignty clauses."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .grundrechts_charta import (
    ChartaArtikel,
    ChartaGeltung,
    ChartaKapitel,
    ChartaVerfahren,
    GrundrechtsCharta,
    build_grundrechts_charta,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class AktSektion(str, Enum):
    """Sovereignty act section that enacts one charter article."""

    SCHUTZ_SEKTION = "schutz-sektion"
    ORDNUNGS_SEKTION = "ordnungs-sektion"
    SOUVERAENITAETS_SEKTION = "souveraenitaets-sektion"


class AktProzedur(str, Enum):
    """Enactment procedure applied to the charter article."""

    EILVERFAHREN = "eilverfahren"
    STANDARDVERFAHREN = "standardverfahren"
    VOLLVERFAHREN = "vollverfahren"


class AktStatus(str, Enum):
    """Operative status of the enacted sovereignty clause."""

    SUSPENDIERT = "suspendiert"
    RATIFIZIERT = "ratifiziert"
    SOUVERAEN = "souveraen"


@dataclass(frozen=True)
class AktKlausel:
    """One sovereignty clause derived from a charter article."""

    klausel_id: str
    sequence: int
    artikel_id: str
    mandat_id: str
    fall_id: str
    line_id: str
    article_id: str
    entry_id: str
    section_id: str
    reference_key: str
    charta_kapitel: ChartaKapitel
    charta_geltung: ChartaGeltung
    charta_verfahren: ChartaVerfahren
    sektion: AktSektion
    prozedur: AktProzedur
    akt_status: AktStatus
    klausel_ids: tuple[str, ...]
    operative: bool
    sovereignty_weight: float
    enactment_tier: int
    klausel_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "klausel_id", _non_empty(self.klausel_id, field_name="klausel_id"))
        object.__setattr__(self, "artikel_id", _non_empty(self.artikel_id, field_name="artikel_id"))
        object.__setattr__(self, "mandat_id", _non_empty(self.mandat_id, field_name="mandat_id"))
        object.__setattr__(self, "fall_id", _non_empty(self.fall_id, field_name="fall_id"))
        object.__setattr__(self, "line_id", _non_empty(self.line_id, field_name="line_id"))
        object.__setattr__(self, "article_id", _non_empty(self.article_id, field_name="article_id"))
        object.__setattr__(self, "entry_id", _non_empty(self.entry_id, field_name="entry_id"))
        object.__setattr__(self, "section_id", _non_empty(self.section_id, field_name="section_id"))
        object.__setattr__(self, "reference_key", _non_empty(self.reference_key, field_name="reference_key"))
        object.__setattr__(self, "sovereignty_weight", _clamp01(self.sovereignty_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.enactment_tier < 1:
            raise ValueError("enactment_tier must be positive")
        if not self.klausel_ids:
            raise ValueError("klausel_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "klausel_id": self.klausel_id,
            "sequence": self.sequence,
            "artikel_id": self.artikel_id,
            "mandat_id": self.mandat_id,
            "fall_id": self.fall_id,
            "line_id": self.line_id,
            "article_id": self.article_id,
            "entry_id": self.entry_id,
            "section_id": self.section_id,
            "reference_key": self.reference_key,
            "charta_kapitel": self.charta_kapitel.value,
            "charta_geltung": self.charta_geltung.value,
            "charta_verfahren": self.charta_verfahren.value,
            "sektion": self.sektion.value,
            "prozedur": self.prozedur.value,
            "akt_status": self.akt_status.value,
            "klausel_ids": list(self.klausel_ids),
            "operative": self.operative,
            "sovereignty_weight": self.sovereignty_weight,
            "enactment_tier": self.enactment_tier,
            "klausel_tags": list(self.klausel_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class SouveraenitaetsAkt:
    """Sovereignty act that enacts Leitstern charter articles as operative clauses."""

    akt_id: str
    grundrechts_charta: GrundrechtsCharta
    klauseln: tuple[AktKlausel, ...]
    akt_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "akt_id", _non_empty(self.akt_id, field_name="akt_id"))

    @property
    def suspendiert_klausel_ids(self) -> tuple[str, ...]:
        return tuple(k.klausel_id for k in self.klauseln if k.akt_status is AktStatus.SUSPENDIERT)

    @property
    def ratifiziert_klausel_ids(self) -> tuple[str, ...]:
        return tuple(k.klausel_id for k in self.klauseln if k.akt_status is AktStatus.RATIFIZIERT)

    @property
    def souveraen_klausel_ids(self) -> tuple[str, ...]:
        return tuple(k.klausel_id for k in self.klauseln if k.akt_status is AktStatus.SOUVERAEN)

    def to_dict(self) -> dict[str, object]:
        return {
            "akt_id": self.akt_id,
            "grundrechts_charta": self.grundrechts_charta.to_dict(),
            "klauseln": [k.to_dict() for k in self.klauseln],
            "akt_signal": self.akt_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "suspendiert_klausel_ids": list(self.suspendiert_klausel_ids),
            "ratifiziert_klausel_ids": list(self.ratifiziert_klausel_ids),
            "souveraen_klausel_ids": list(self.souveraen_klausel_ids),
        }


def _sektion(artikel: ChartaArtikel) -> AktSektion:
    return {
        ChartaKapitel.SCHUTZ_KAPITEL: AktSektion.SCHUTZ_SEKTION,
        ChartaKapitel.ORDNUNGS_KAPITEL: AktSektion.ORDNUNGS_SEKTION,
        ChartaKapitel.SOUVERAENITAETS_KAPITEL: AktSektion.SOUVERAENITAETS_SEKTION,
    }[artikel.kapitel]


def _prozedur(artikel: ChartaArtikel) -> AktProzedur:
    return {
        ChartaVerfahren.DRINGLICHE_EINTRAGUNG: AktProzedur.EILVERFAHREN,
        ChartaVerfahren.ORDENTLICHE_EINTRAGUNG: AktProzedur.STANDARDVERFAHREN,
        ChartaVerfahren.PLENARE_EINTRAGUNG: AktProzedur.VOLLVERFAHREN,
    }[artikel.verfahren]


def _akt_status(artikel: ChartaArtikel) -> AktStatus:
    return {
        ChartaGeltung.AUSGESETZT: AktStatus.SUSPENDIERT,
        ChartaGeltung.GELTEND: AktStatus.RATIFIZIERT,
        ChartaGeltung.GRUNDRECHT: AktStatus.SOUVERAEN,
    }[artikel.geltung]


def _sovereignty_weight(artikel: ChartaArtikel) -> float:
    bonus = {
        AktStatus.SUSPENDIERT: 0.0,
        AktStatus.RATIFIZIERT: 0.04,
        AktStatus.SOUVERAEN: 0.08,
    }[_akt_status(artikel)]
    return round(min(1.0, artikel.codex_weight + bonus), 3)


def _enactment_tier(artikel: ChartaArtikel) -> int:
    return {
        AktStatus.SUSPENDIERT: artikel.ratification_depth,
        AktStatus.RATIFIZIERT: artikel.ratification_depth + 1,
        AktStatus.SOUVERAEN: artikel.ratification_depth + 2,
    }[_akt_status(artikel)]


def build_souveraenitaets_akt(
    grundrechts_charta: GrundrechtsCharta | None = None,
    *,
    akt_id: str = "souveraenitaets-akt",
) -> SouveraenitaetsAkt:
    """Build the sovereignty act enacting Leitstern charter articles as operative clauses."""

    resolved_charta = (
        build_grundrechts_charta(charta_id=f"{akt_id}-charta")
        if grundrechts_charta is None
        else grundrechts_charta
    )
    klauseln = tuple(
        AktKlausel(
            klausel_id=f"{akt_id}-{artikel.artikel_id.removeprefix(f'{resolved_charta.charta_id}-')}",
            sequence=index,
            artikel_id=artikel.artikel_id,
            mandat_id=artikel.mandat_id,
            fall_id=artikel.fall_id,
            line_id=artikel.line_id,
            article_id=artikel.article_id,
            entry_id=artikel.entry_id,
            section_id=artikel.section_id,
            reference_key=artikel.reference_key,
            charta_kapitel=artikel.kapitel,
            charta_geltung=artikel.geltung,
            charta_verfahren=artikel.verfahren,
            sektion=_sektion(artikel),
            prozedur=_prozedur(artikel),
            akt_status=_akt_status(artikel),
            klausel_ids=artikel.artikel_ids,
            operative=artikel.enforceable and _akt_status(artikel) is AktStatus.SOUVERAEN,
            sovereignty_weight=_sovereignty_weight(artikel),
            enactment_tier=_enactment_tier(artikel),
            klausel_tags=tuple(
                dict.fromkeys(
                    (
                        *artikel.artikel_tags,
                        _sektion(artikel).value,
                        _prozedur(artikel).value,
                        _akt_status(artikel).value,
                    )
                )
            ),
            summary=(
                f"{artikel.artikel_id} enacted in {_sektion(artikel).value} via "
                f"{_prozedur(artikel).value} with status {_akt_status(artikel).value}."
            ),
        )
        for index, artikel in enumerate(resolved_charta.artikel, start=1)
    )
    if not klauseln:
        raise ValueError("souveraenitaets akt requires at least one klausel")

    severity = "info"
    status = "akt-souveraen"
    if any(k.akt_status is AktStatus.SUSPENDIERT for k in klauseln):
        severity = "critical"
        status = "akt-suspendiert"
    elif any(k.akt_status is AktStatus.RATIFIZIERT for k in klauseln):
        severity = "warning"
        status = "akt-ratifiziert"

    akt_signal = TelemetrySignal(
        signal_name="souveraenitaets-akt",
        boundary=resolved_charta.charta_signal.boundary,
        correlation_id=akt_id,
        severity=severity,
        status=status,
        metrics={
            "klausel_count": float(len(klauseln)),
            "suspendiert_count": float(sum(1 for k in klauseln if k.akt_status is AktStatus.SUSPENDIERT)),
            "ratifiziert_count": float(sum(1 for k in klauseln if k.akt_status is AktStatus.RATIFIZIERT)),
            "souveraen_count": float(sum(1 for k in klauseln if k.akt_status is AktStatus.SOUVERAEN)),
            "operative_count": float(sum(1 for k in klauseln if k.operative)),
            "avg_sovereignty_weight": round(sum(k.sovereignty_weight for k in klauseln) / len(klauseln), 3),
        },
        labels={"akt_id": akt_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_charta.final_snapshot.runtime_stage,
        signals=(akt_signal, *resolved_charta.final_snapshot.signals),
        alerts=resolved_charta.final_snapshot.alerts,
        audit_entries=resolved_charta.final_snapshot.audit_entries,
        active_controls=resolved_charta.final_snapshot.active_controls,
    )
    return SouveraenitaetsAkt(
        akt_id=akt_id,
        grundrechts_charta=resolved_charta,
        klauseln=klauseln,
        akt_signal=akt_signal,
        final_snapshot=final_snapshot,
    )
