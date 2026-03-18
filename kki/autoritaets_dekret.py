"""Autoritaets dekret issuing constitutional norms as binding Leitstern authority clauses."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .leitordnung import (
    Leitordnung,
    OrdnungsKraft,
    OrdnungsNorm,
    OrdnungsRang,
    OrdnungsTyp,
    build_leitordnung,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class DekretSektion(str, Enum):
    """Authority decree section that issues one constitutional norm."""

    SCHUTZ_SEKTION = "schutz-sektion"
    ORDNUNGS_SEKTION = "ordnungs-sektion"
    SOUVERAENITAETS_SEKTION = "souveraenitaets-sektion"


class DekretProzedur(str, Enum):
    """Decree procedure applied when issuing the norm."""

    NOTPROZEDUR = "notprozedur"
    REGELPROZEDUR = "regelprozedur"
    PLENARPROZEDUR = "plenarprozedur"


class DekretGeltung(str, Enum):
    """Legal force of the issued authority clause."""

    GESPERRT = "gesperrt"
    VERORDNET = "verordnet"
    AUTORITAETSRECHT = "autoritaetsrecht"


@dataclass(frozen=True)
class DekretKlausel:
    """One authority clause derived from a constitutional norm."""

    klausel_id: str
    sequence: int
    norm_id: str
    abschnitt_id: str
    artikel_id: str
    mandat_id: str
    fall_id: str
    line_id: str
    article_id: str
    entry_id: str
    section_id: str
    reference_key: str
    ordnungs_rang: OrdnungsRang
    ordnungs_kraft: OrdnungsKraft
    ordnungs_typ: OrdnungsTyp
    sektion: DekretSektion
    prozedur: DekretProzedur
    geltung: DekretGeltung
    klausel_ids: tuple[str, ...]
    decreed: bool
    dekret_weight: float
    decree_order: int
    klausel_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "klausel_id", _non_empty(self.klausel_id, field_name="klausel_id"))
        object.__setattr__(self, "norm_id", _non_empty(self.norm_id, field_name="norm_id"))
        object.__setattr__(self, "abschnitt_id", _non_empty(self.abschnitt_id, field_name="abschnitt_id"))
        object.__setattr__(self, "artikel_id", _non_empty(self.artikel_id, field_name="artikel_id"))
        object.__setattr__(self, "mandat_id", _non_empty(self.mandat_id, field_name="mandat_id"))
        object.__setattr__(self, "fall_id", _non_empty(self.fall_id, field_name="fall_id"))
        object.__setattr__(self, "line_id", _non_empty(self.line_id, field_name="line_id"))
        object.__setattr__(self, "article_id", _non_empty(self.article_id, field_name="article_id"))
        object.__setattr__(self, "entry_id", _non_empty(self.entry_id, field_name="entry_id"))
        object.__setattr__(self, "section_id", _non_empty(self.section_id, field_name="section_id"))
        object.__setattr__(self, "reference_key", _non_empty(self.reference_key, field_name="reference_key"))
        object.__setattr__(self, "dekret_weight", _clamp01(self.dekret_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.decree_order < 1:
            raise ValueError("decree_order must be positive")
        if not self.klausel_ids:
            raise ValueError("klausel_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "klausel_id": self.klausel_id,
            "sequence": self.sequence,
            "norm_id": self.norm_id,
            "abschnitt_id": self.abschnitt_id,
            "artikel_id": self.artikel_id,
            "mandat_id": self.mandat_id,
            "fall_id": self.fall_id,
            "line_id": self.line_id,
            "article_id": self.article_id,
            "entry_id": self.entry_id,
            "section_id": self.section_id,
            "reference_key": self.reference_key,
            "ordnungs_rang": self.ordnungs_rang.value,
            "ordnungs_kraft": self.ordnungs_kraft.value,
            "ordnungs_typ": self.ordnungs_typ.value,
            "sektion": self.sektion.value,
            "prozedur": self.prozedur.value,
            "geltung": self.geltung.value,
            "klausel_ids": list(self.klausel_ids),
            "decreed": self.decreed,
            "dekret_weight": self.dekret_weight,
            "decree_order": self.decree_order,
            "klausel_tags": list(self.klausel_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class AutoritaetsDekret:
    """Authority decree issuing Leitstern constitutional norms as binding clauses."""

    dekret_id: str
    leitordnung: Leitordnung
    klauseln: tuple[DekretKlausel, ...]
    dekret_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "dekret_id", _non_empty(self.dekret_id, field_name="dekret_id"))

    @property
    def gesperrt_klausel_ids(self) -> tuple[str, ...]:
        return tuple(k.klausel_id for k in self.klauseln if k.geltung is DekretGeltung.GESPERRT)

    @property
    def verordnet_klausel_ids(self) -> tuple[str, ...]:
        return tuple(k.klausel_id for k in self.klauseln if k.geltung is DekretGeltung.VERORDNET)

    @property
    def autoritaetsrecht_klausel_ids(self) -> tuple[str, ...]:
        return tuple(k.klausel_id for k in self.klauseln if k.geltung is DekretGeltung.AUTORITAETSRECHT)

    def to_dict(self) -> dict[str, object]:
        return {
            "dekret_id": self.dekret_id,
            "leitordnung": self.leitordnung.to_dict(),
            "klauseln": [k.to_dict() for k in self.klauseln],
            "dekret_signal": self.dekret_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "gesperrt_klausel_ids": list(self.gesperrt_klausel_ids),
            "verordnet_klausel_ids": list(self.verordnet_klausel_ids),
            "autoritaetsrecht_klausel_ids": list(self.autoritaetsrecht_klausel_ids),
        }


def _sektion(norm: OrdnungsNorm) -> DekretSektion:
    return {
        OrdnungsRang.SCHUTZ_RANG: DekretSektion.SCHUTZ_SEKTION,
        OrdnungsRang.ORDNUNGS_RANG: DekretSektion.ORDNUNGS_SEKTION,
        OrdnungsRang.SOUVERAENITAETS_RANG: DekretSektion.SOUVERAENITAETS_SEKTION,
    }[norm.rang]


def _prozedur(norm: OrdnungsNorm) -> DekretProzedur:
    return {
        OrdnungsTyp.NOTORDNUNG: DekretProzedur.NOTPROZEDUR,
        OrdnungsTyp.REGELORDNUNG: DekretProzedur.REGELPROZEDUR,
        OrdnungsTyp.PLENARORDNUNG: DekretProzedur.PLENARPROZEDUR,
    }[norm.typ]


def _geltung(norm: OrdnungsNorm) -> DekretGeltung:
    return {
        OrdnungsKraft.BLOCKIERT: DekretGeltung.GESPERRT,
        OrdnungsKraft.WIRKSAM: DekretGeltung.VERORDNET,
        OrdnungsKraft.LEITEND: DekretGeltung.AUTORITAETSRECHT,
    }[norm.kraft]


def _dekret_weight(norm: OrdnungsNorm) -> float:
    bonus = {
        DekretGeltung.GESPERRT: 0.0,
        DekretGeltung.VERORDNET: 0.04,
        DekretGeltung.AUTORITAETSRECHT: 0.08,
    }[_geltung(norm)]
    return round(min(1.0, norm.ordnungs_weight + bonus), 3)


def _decree_order(norm: OrdnungsNorm) -> int:
    return {
        DekretGeltung.GESPERRT: norm.authority_level,
        DekretGeltung.VERORDNET: norm.authority_level + 1,
        DekretGeltung.AUTORITAETSRECHT: norm.authority_level + 2,
    }[_geltung(norm)]


def build_autoritaets_dekret(
    leitordnung: Leitordnung | None = None,
    *,
    dekret_id: str = "autoritaets-dekret",
) -> AutoritaetsDekret:
    """Build the authority decree issuing Leitstern constitutional norms."""

    resolved_ordnung = (
        build_leitordnung(ordnung_id=f"{dekret_id}-ordnung")
        if leitordnung is None
        else leitordnung
    )
    klauseln = tuple(
        DekretKlausel(
            klausel_id=f"{dekret_id}-{norm.norm_id.removeprefix(f'{resolved_ordnung.ordnung_id}-')}",
            sequence=index,
            norm_id=norm.norm_id,
            abschnitt_id=norm.abschnitt_id,
            artikel_id=norm.artikel_id,
            mandat_id=norm.mandat_id,
            fall_id=norm.fall_id,
            line_id=norm.line_id,
            article_id=norm.article_id,
            entry_id=norm.entry_id,
            section_id=norm.section_id,
            reference_key=norm.reference_key,
            ordnungs_rang=norm.rang,
            ordnungs_kraft=norm.kraft,
            ordnungs_typ=norm.typ,
            sektion=_sektion(norm),
            prozedur=_prozedur(norm),
            geltung=_geltung(norm),
            klausel_ids=norm.norm_ids,
            decreed=norm.supreme and _geltung(norm) is DekretGeltung.AUTORITAETSRECHT,
            dekret_weight=_dekret_weight(norm),
            decree_order=_decree_order(norm),
            klausel_tags=tuple(
                dict.fromkeys(
                    (
                        *norm.norm_tags,
                        _sektion(norm).value,
                        _prozedur(norm).value,
                        _geltung(norm).value,
                    )
                )
            ),
            summary=(
                f"{norm.norm_id} decreed in {_sektion(norm).value} via "
                f"{_prozedur(norm).value} with geltung {_geltung(norm).value}."
            ),
        )
        for index, norm in enumerate(resolved_ordnung.normen, start=1)
    )
    if not klauseln:
        raise ValueError("autoritaets dekret requires at least one klausel")

    severity = "info"
    status = "dekret-autoritaetsrecht"
    if any(k.geltung is DekretGeltung.GESPERRT for k in klauseln):
        severity = "critical"
        status = "dekret-gesperrt"
    elif any(k.geltung is DekretGeltung.VERORDNET for k in klauseln):
        severity = "warning"
        status = "dekret-verordnet"

    dekret_signal = TelemetrySignal(
        signal_name="autoritaets-dekret",
        boundary=resolved_ordnung.ordnungs_signal.boundary,
        correlation_id=dekret_id,
        severity=severity,
        status=status,
        metrics={
            "klausel_count": float(len(klauseln)),
            "gesperrt_count": float(sum(1 for k in klauseln if k.geltung is DekretGeltung.GESPERRT)),
            "verordnet_count": float(sum(1 for k in klauseln if k.geltung is DekretGeltung.VERORDNET)),
            "autoritaetsrecht_count": float(sum(1 for k in klauseln if k.geltung is DekretGeltung.AUTORITAETSRECHT)),
            "decreed_count": float(sum(1 for k in klauseln if k.decreed)),
            "avg_dekret_weight": round(sum(k.dekret_weight for k in klauseln) / len(klauseln), 3),
        },
        labels={"dekret_id": dekret_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_ordnung.final_snapshot.runtime_stage,
        signals=(dekret_signal, *resolved_ordnung.final_snapshot.signals),
        alerts=resolved_ordnung.final_snapshot.alerts,
        audit_entries=resolved_ordnung.final_snapshot.audit_entries,
        active_controls=resolved_ordnung.final_snapshot.active_controls,
    )
    return AutoritaetsDekret(
        dekret_id=dekret_id,
        leitordnung=resolved_ordnung,
        klauseln=klauseln,
        dekret_signal=dekret_signal,
        final_snapshot=final_snapshot,
    )
