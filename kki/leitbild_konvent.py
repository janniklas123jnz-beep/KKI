"""Leitbild konvent assembling anchored values into binding Leitstern resolutions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .werte_charta import (
    WerteArtikel,
    WerteCharta,
    WerteProzedur,
    WerteStatus,
    WerteTyp,
    build_werte_charta,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class LeitbildAusrichtung(str, Enum):
    """Guiding orientation that frames one leitbild resolution."""

    SCHUTZ_AUSRICHTUNG = "schutz-ausrichtung"
    ORDNUNGS_AUSRICHTUNG = "ordnungs-ausrichtung"
    SOUVERAENITAETS_AUSRICHTUNG = "souveraenitaets-ausrichtung"


class KonventProzedur(str, Enum):
    """Convention protocol used to pass the resolution."""

    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KonventBeschluss(str, Enum):
    """Canonical status of the passed leitbild resolution."""

    GESPERRT = "gesperrt"
    BESCHLOSSEN = "beschlossen"
    GRUNDLEGEND_BESCHLOSSEN = "grundlegend-beschlossen"


@dataclass(frozen=True)
class LeitbildResolution:
    """One leitbild resolution derived from an anchored value article."""

    resolution_id: str
    sequence: int
    artikel_id: str
    satz_id: str
    eintrag_id: str
    pfeiler_id: str
    klausel_id: str
    norm_id: str
    abschnitt_id: str
    artikel_ref_id: str
    mandat_id: str
    fall_id: str
    line_id: str
    article_id: str
    entry_id: str
    section_id: str
    reference_key: str
    werte_typ: WerteTyp
    werte_prozedur: WerteProzedur
    ausrichtung: LeitbildAusrichtung
    prozedur: KonventProzedur
    beschluss: KonventBeschluss
    resolution_ids: tuple[str, ...]
    canonical: bool
    konvent_weight: float
    konvent_tier: int
    resolution_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "resolution_id", _non_empty(self.resolution_id, field_name="resolution_id"))
        object.__setattr__(self, "artikel_id", _non_empty(self.artikel_id, field_name="artikel_id"))
        object.__setattr__(self, "satz_id", _non_empty(self.satz_id, field_name="satz_id"))
        object.__setattr__(self, "eintrag_id", _non_empty(self.eintrag_id, field_name="eintrag_id"))
        object.__setattr__(self, "pfeiler_id", _non_empty(self.pfeiler_id, field_name="pfeiler_id"))
        object.__setattr__(self, "klausel_id", _non_empty(self.klausel_id, field_name="klausel_id"))
        object.__setattr__(self, "norm_id", _non_empty(self.norm_id, field_name="norm_id"))
        object.__setattr__(self, "abschnitt_id", _non_empty(self.abschnitt_id, field_name="abschnitt_id"))
        object.__setattr__(self, "artikel_ref_id", _non_empty(self.artikel_ref_id, field_name="artikel_ref_id"))
        object.__setattr__(self, "mandat_id", _non_empty(self.mandat_id, field_name="mandat_id"))
        object.__setattr__(self, "fall_id", _non_empty(self.fall_id, field_name="fall_id"))
        object.__setattr__(self, "line_id", _non_empty(self.line_id, field_name="line_id"))
        object.__setattr__(self, "article_id", _non_empty(self.article_id, field_name="article_id"))
        object.__setattr__(self, "entry_id", _non_empty(self.entry_id, field_name="entry_id"))
        object.__setattr__(self, "section_id", _non_empty(self.section_id, field_name="section_id"))
        object.__setattr__(self, "reference_key", _non_empty(self.reference_key, field_name="reference_key"))
        object.__setattr__(self, "konvent_weight", _clamp01(self.konvent_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.konvent_tier < 1:
            raise ValueError("konvent_tier must be positive")
        if not self.resolution_ids:
            raise ValueError("resolution_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "resolution_id": self.resolution_id,
            "sequence": self.sequence,
            "artikel_id": self.artikel_id,
            "satz_id": self.satz_id,
            "eintrag_id": self.eintrag_id,
            "pfeiler_id": self.pfeiler_id,
            "klausel_id": self.klausel_id,
            "norm_id": self.norm_id,
            "abschnitt_id": self.abschnitt_id,
            "artikel_ref_id": self.artikel_ref_id,
            "mandat_id": self.mandat_id,
            "fall_id": self.fall_id,
            "line_id": self.line_id,
            "article_id": self.article_id,
            "entry_id": self.entry_id,
            "section_id": self.section_id,
            "reference_key": self.reference_key,
            "werte_typ": self.werte_typ.value,
            "werte_prozedur": self.werte_prozedur.value,
            "ausrichtung": self.ausrichtung.value,
            "prozedur": self.prozedur.value,
            "beschluss": self.beschluss.value,
            "resolution_ids": list(self.resolution_ids),
            "canonical": self.canonical,
            "konvent_weight": self.konvent_weight,
            "konvent_tier": self.konvent_tier,
            "resolution_tags": list(self.resolution_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class LeitbildKonvent:
    """Leitbild convention assembling Leitstern value articles into binding resolutions."""

    konvent_id: str
    werte_charta: WerteCharta
    resolutionen: tuple[LeitbildResolution, ...]
    konvent_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "konvent_id", _non_empty(self.konvent_id, field_name="konvent_id"))

    @property
    def gesperrt_resolution_ids(self) -> tuple[str, ...]:
        return tuple(r.resolution_id for r in self.resolutionen if r.beschluss is KonventBeschluss.GESPERRT)

    @property
    def beschlossen_resolution_ids(self) -> tuple[str, ...]:
        return tuple(r.resolution_id for r in self.resolutionen if r.beschluss is KonventBeschluss.BESCHLOSSEN)

    @property
    def grundlegend_resolution_ids(self) -> tuple[str, ...]:
        return tuple(r.resolution_id for r in self.resolutionen if r.beschluss is KonventBeschluss.GRUNDLEGEND_BESCHLOSSEN)

    def to_dict(self) -> dict[str, object]:
        return {
            "konvent_id": self.konvent_id,
            "werte_charta": self.werte_charta.to_dict(),
            "resolutionen": [r.to_dict() for r in self.resolutionen],
            "konvent_signal": self.konvent_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "gesperrt_resolution_ids": list(self.gesperrt_resolution_ids),
            "beschlossen_resolution_ids": list(self.beschlossen_resolution_ids),
            "grundlegend_resolution_ids": list(self.grundlegend_resolution_ids),
        }


def _ausrichtung(artikel: WerteArtikel) -> LeitbildAusrichtung:
    return {
        WerteTyp.SCHUTZ_WERT: LeitbildAusrichtung.SCHUTZ_AUSRICHTUNG,
        WerteTyp.ORDNUNGS_WERT: LeitbildAusrichtung.ORDNUNGS_AUSRICHTUNG,
        WerteTyp.SOUVERAENITAETS_WERT: LeitbildAusrichtung.SOUVERAENITAETS_AUSRICHTUNG,
    }[artikel.typ]


def _prozedur(artikel: WerteArtikel) -> KonventProzedur:
    return {
        WerteProzedur.NOTPROZEDUR: KonventProzedur.NOTPROZEDUR,
        WerteProzedur.REGELPROTOKOLL: KonventProzedur.REGELPROTOKOLL,
        WerteProzedur.PLENARPROTOKOLL: KonventProzedur.PLENARPROTOKOLL,
    }[artikel.prozedur]


def _beschluss(artikel: WerteArtikel) -> KonventBeschluss:
    return {
        WerteStatus.GESPERRT: KonventBeschluss.GESPERRT,
        WerteStatus.VERANKERT: KonventBeschluss.BESCHLOSSEN,
        WerteStatus.GRUNDLEGEND_VERANKERT: KonventBeschluss.GRUNDLEGEND_BESCHLOSSEN,
    }[artikel.status]


def _konvent_weight(artikel: WerteArtikel) -> float:
    bonus = {
        KonventBeschluss.GESPERRT: 0.0,
        KonventBeschluss.BESCHLOSSEN: 0.04,
        KonventBeschluss.GRUNDLEGEND_BESCHLOSSEN: 0.08,
    }[_beschluss(artikel)]
    return round(min(1.0, artikel.charta_weight + bonus), 3)


def _konvent_tier(artikel: WerteArtikel) -> int:
    return {
        KonventBeschluss.GESPERRT: artikel.charta_tier,
        KonventBeschluss.BESCHLOSSEN: artikel.charta_tier + 1,
        KonventBeschluss.GRUNDLEGEND_BESCHLOSSEN: artikel.charta_tier + 2,
    }[_beschluss(artikel)]


def build_leitbild_konvent(
    werte_charta: WerteCharta | None = None,
    *,
    konvent_id: str = "leitbild-konvent",
) -> LeitbildKonvent:
    """Build the leitbild convention assembling Leitstern value articles."""

    resolved_charta = (
        build_werte_charta(charta_id=f"{konvent_id}-charta")
        if werte_charta is None
        else werte_charta
    )
    resolutionen = tuple(
        LeitbildResolution(
            resolution_id=f"{konvent_id}-{a.artikel_id.removeprefix(f'{resolved_charta.charta_id}-')}",
            sequence=index,
            artikel_id=a.artikel_id,
            satz_id=a.satz_id,
            eintrag_id=a.eintrag_id,
            pfeiler_id=a.pfeiler_id,
            klausel_id=a.klausel_id,
            norm_id=a.norm_id,
            abschnitt_id=a.abschnitt_id,
            artikel_ref_id=a.artikel_ref_id,
            mandat_id=a.mandat_id,
            fall_id=a.fall_id,
            line_id=a.line_id,
            article_id=a.article_id,
            entry_id=a.entry_id,
            section_id=a.section_id,
            reference_key=a.reference_key,
            werte_typ=a.typ,
            werte_prozedur=a.prozedur,
            ausrichtung=_ausrichtung(a),
            prozedur=_prozedur(a),
            beschluss=_beschluss(a),
            resolution_ids=a.artikel_ids,
            canonical=a.canonical and _beschluss(a) is KonventBeschluss.GRUNDLEGEND_BESCHLOSSEN,
            konvent_weight=_konvent_weight(a),
            konvent_tier=_konvent_tier(a),
            resolution_tags=tuple(
                dict.fromkeys(
                    (
                        *a.artikel_tags,
                        _ausrichtung(a).value,
                        _prozedur(a).value,
                        _beschluss(a).value,
                    )
                )
            ),
            summary=(
                f"{a.artikel_id} resolved in {_ausrichtung(a).value} via "
                f"{_prozedur(a).value} with beschluss {_beschluss(a).value}."
            ),
        )
        for index, a in enumerate(resolved_charta.artikel, start=1)
    )
    if not resolutionen:
        raise ValueError("leitbild konvent requires at least one resolution")

    severity = "info"
    status = "konvent-grundlegend-beschlossen"
    if any(r.beschluss is KonventBeschluss.GESPERRT for r in resolutionen):
        severity = "critical"
        status = "konvent-gesperrt"
    elif any(r.beschluss is KonventBeschluss.BESCHLOSSEN for r in resolutionen):
        severity = "warning"
        status = "konvent-beschlossen"

    konvent_signal = TelemetrySignal(
        signal_name="leitbild-konvent",
        boundary=resolved_charta.charta_signal.boundary,
        correlation_id=konvent_id,
        severity=severity,
        status=status,
        metrics={
            "resolution_count": float(len(resolutionen)),
            "gesperrt_count": float(sum(1 for r in resolutionen if r.beschluss is KonventBeschluss.GESPERRT)),
            "beschlossen_count": float(sum(1 for r in resolutionen if r.beschluss is KonventBeschluss.BESCHLOSSEN)),
            "grundlegend_count": float(sum(1 for r in resolutionen if r.beschluss is KonventBeschluss.GRUNDLEGEND_BESCHLOSSEN)),
            "canonical_count": float(sum(1 for r in resolutionen if r.canonical)),
            "avg_konvent_weight": round(sum(r.konvent_weight for r in resolutionen) / len(resolutionen), 3),
        },
        labels={"konvent_id": konvent_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_charta.final_snapshot.runtime_stage,
        signals=(konvent_signal, *resolved_charta.final_snapshot.signals),
        alerts=resolved_charta.final_snapshot.alerts,
        audit_entries=resolved_charta.final_snapshot.audit_entries,
        active_controls=resolved_charta.final_snapshot.active_controls,
    )
    return LeitbildKonvent(
        konvent_id=konvent_id,
        werte_charta=resolved_charta,
        resolutionen=resolutionen,
        konvent_signal=konvent_signal,
        final_snapshot=final_snapshot,
    )
