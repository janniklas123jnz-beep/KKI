"""Missions verfassung ratifying leitbild resolutions as constitutional Leitstern mission articles."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .leitbild_konvent import (
    KonventBeschluss,
    KonventProzedur,
    LeitbildAusrichtung,
    LeitbildKonvent,
    LeitbildResolution,
    build_leitbild_konvent,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class MissionsRang(str, Enum):
    """Mission rank that classifies one constitutional article."""

    SCHUTZ_RANG = "schutz-rang"
    ORDNUNGS_RANG = "ordnungs-rang"
    SOUVERAENITAETS_RANG = "souveraenitaets-rang"


class VerfassungsProzedur(str, Enum):
    """Constitutional procedure used to ratify the mission article."""

    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class VerfassungsStatus(str, Enum):
    """Canonical status of the ratified mission article."""

    GESPERRT = "gesperrt"
    RATIFIZIERT = "ratifiziert"
    GRUNDLEGEND_RATIFIZIERT = "grundlegend-ratifiziert"


@dataclass(frozen=True)
class MissionsArtikel:
    """One constitutional mission article derived from a leitbild resolution."""

    artikel_id: str
    sequence: int
    resolution_id: str
    artikel_ref_id: str
    satz_id: str
    eintrag_id: str
    pfeiler_id: str
    klausel_id: str
    norm_id: str
    abschnitt_id: str
    mandat_id: str
    fall_id: str
    line_id: str
    article_id: str
    entry_id: str
    section_id: str
    reference_key: str
    leitbild_ausrichtung: LeitbildAusrichtung
    konvent_prozedur: KonventProzedur
    rang: MissionsRang
    prozedur: VerfassungsProzedur
    status: VerfassungsStatus
    artikel_ids: tuple[str, ...]
    canonical: bool
    verfassungs_weight: float
    verfassungs_tier: int
    artikel_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "artikel_id", _non_empty(self.artikel_id, field_name="artikel_id"))
        object.__setattr__(self, "resolution_id", _non_empty(self.resolution_id, field_name="resolution_id"))
        object.__setattr__(self, "artikel_ref_id", _non_empty(self.artikel_ref_id, field_name="artikel_ref_id"))
        object.__setattr__(self, "satz_id", _non_empty(self.satz_id, field_name="satz_id"))
        object.__setattr__(self, "eintrag_id", _non_empty(self.eintrag_id, field_name="eintrag_id"))
        object.__setattr__(self, "pfeiler_id", _non_empty(self.pfeiler_id, field_name="pfeiler_id"))
        object.__setattr__(self, "klausel_id", _non_empty(self.klausel_id, field_name="klausel_id"))
        object.__setattr__(self, "norm_id", _non_empty(self.norm_id, field_name="norm_id"))
        object.__setattr__(self, "abschnitt_id", _non_empty(self.abschnitt_id, field_name="abschnitt_id"))
        object.__setattr__(self, "mandat_id", _non_empty(self.mandat_id, field_name="mandat_id"))
        object.__setattr__(self, "fall_id", _non_empty(self.fall_id, field_name="fall_id"))
        object.__setattr__(self, "line_id", _non_empty(self.line_id, field_name="line_id"))
        object.__setattr__(self, "article_id", _non_empty(self.article_id, field_name="article_id"))
        object.__setattr__(self, "entry_id", _non_empty(self.entry_id, field_name="entry_id"))
        object.__setattr__(self, "section_id", _non_empty(self.section_id, field_name="section_id"))
        object.__setattr__(self, "reference_key", _non_empty(self.reference_key, field_name="reference_key"))
        object.__setattr__(self, "verfassungs_weight", _clamp01(self.verfassungs_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.verfassungs_tier < 1:
            raise ValueError("verfassungs_tier must be positive")
        if not self.artikel_ids:
            raise ValueError("artikel_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "artikel_id": self.artikel_id,
            "sequence": self.sequence,
            "resolution_id": self.resolution_id,
            "artikel_ref_id": self.artikel_ref_id,
            "satz_id": self.satz_id,
            "eintrag_id": self.eintrag_id,
            "pfeiler_id": self.pfeiler_id,
            "klausel_id": self.klausel_id,
            "norm_id": self.norm_id,
            "abschnitt_id": self.abschnitt_id,
            "mandat_id": self.mandat_id,
            "fall_id": self.fall_id,
            "line_id": self.line_id,
            "article_id": self.article_id,
            "entry_id": self.entry_id,
            "section_id": self.section_id,
            "reference_key": self.reference_key,
            "leitbild_ausrichtung": self.leitbild_ausrichtung.value,
            "konvent_prozedur": self.konvent_prozedur.value,
            "rang": self.rang.value,
            "prozedur": self.prozedur.value,
            "status": self.status.value,
            "artikel_ids": list(self.artikel_ids),
            "canonical": self.canonical,
            "verfassungs_weight": self.verfassungs_weight,
            "verfassungs_tier": self.verfassungs_tier,
            "artikel_tags": list(self.artikel_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class MissionsVerfassung:
    """Mission constitution ratifying Leitstern leitbild resolutions as canonical articles."""

    verfassungs_id: str
    leitbild_konvent: LeitbildKonvent
    artikel: tuple[MissionsArtikel, ...]
    verfassungs_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "verfassungs_id", _non_empty(self.verfassungs_id, field_name="verfassungs_id"))

    @property
    def gesperrt_artikel_ids(self) -> tuple[str, ...]:
        return tuple(a.artikel_id for a in self.artikel if a.status is VerfassungsStatus.GESPERRT)

    @property
    def ratifiziert_artikel_ids(self) -> tuple[str, ...]:
        return tuple(a.artikel_id for a in self.artikel if a.status is VerfassungsStatus.RATIFIZIERT)

    @property
    def grundlegend_artikel_ids(self) -> tuple[str, ...]:
        return tuple(a.artikel_id for a in self.artikel if a.status is VerfassungsStatus.GRUNDLEGEND_RATIFIZIERT)

    def to_dict(self) -> dict[str, object]:
        return {
            "verfassungs_id": self.verfassungs_id,
            "leitbild_konvent": self.leitbild_konvent.to_dict(),
            "artikel": [a.to_dict() for a in self.artikel],
            "verfassungs_signal": self.verfassungs_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "gesperrt_artikel_ids": list(self.gesperrt_artikel_ids),
            "ratifiziert_artikel_ids": list(self.ratifiziert_artikel_ids),
            "grundlegend_artikel_ids": list(self.grundlegend_artikel_ids),
        }


def _rang(resolution: LeitbildResolution) -> MissionsRang:
    return {
        LeitbildAusrichtung.SCHUTZ_AUSRICHTUNG: MissionsRang.SCHUTZ_RANG,
        LeitbildAusrichtung.ORDNUNGS_AUSRICHTUNG: MissionsRang.ORDNUNGS_RANG,
        LeitbildAusrichtung.SOUVERAENITAETS_AUSRICHTUNG: MissionsRang.SOUVERAENITAETS_RANG,
    }[resolution.ausrichtung]


def _prozedur(resolution: LeitbildResolution) -> VerfassungsProzedur:
    return {
        KonventProzedur.NOTPROZEDUR: VerfassungsProzedur.NOTPROZEDUR,
        KonventProzedur.REGELPROTOKOLL: VerfassungsProzedur.REGELPROTOKOLL,
        KonventProzedur.PLENARPROTOKOLL: VerfassungsProzedur.PLENARPROTOKOLL,
    }[resolution.prozedur]


def _status(resolution: LeitbildResolution) -> VerfassungsStatus:
    return {
        KonventBeschluss.GESPERRT: VerfassungsStatus.GESPERRT,
        KonventBeschluss.BESCHLOSSEN: VerfassungsStatus.RATIFIZIERT,
        KonventBeschluss.GRUNDLEGEND_BESCHLOSSEN: VerfassungsStatus.GRUNDLEGEND_RATIFIZIERT,
    }[resolution.beschluss]


def _verfassungs_weight(resolution: LeitbildResolution) -> float:
    bonus = {
        VerfassungsStatus.GESPERRT: 0.0,
        VerfassungsStatus.RATIFIZIERT: 0.04,
        VerfassungsStatus.GRUNDLEGEND_RATIFIZIERT: 0.08,
    }[_status(resolution)]
    return round(min(1.0, resolution.konvent_weight + bonus), 3)


def _verfassungs_tier(resolution: LeitbildResolution) -> int:
    return {
        VerfassungsStatus.GESPERRT: resolution.konvent_tier,
        VerfassungsStatus.RATIFIZIERT: resolution.konvent_tier + 1,
        VerfassungsStatus.GRUNDLEGEND_RATIFIZIERT: resolution.konvent_tier + 2,
    }[_status(resolution)]


def build_missions_verfassung(
    leitbild_konvent: LeitbildKonvent | None = None,
    *,
    verfassungs_id: str = "missions-verfassung",
) -> MissionsVerfassung:
    """Build the mission constitution ratifying Leitstern leitbild resolutions."""

    resolved_konvent = (
        build_leitbild_konvent(konvent_id=f"{verfassungs_id}-konvent")
        if leitbild_konvent is None
        else leitbild_konvent
    )
    artikel = tuple(
        MissionsArtikel(
            artikel_id=f"{verfassungs_id}-{r.resolution_id.removeprefix(f'{resolved_konvent.konvent_id}-')}",
            sequence=index,
            resolution_id=r.resolution_id,
            artikel_ref_id=r.artikel_id,
            satz_id=r.satz_id,
            eintrag_id=r.eintrag_id,
            pfeiler_id=r.pfeiler_id,
            klausel_id=r.klausel_id,
            norm_id=r.norm_id,
            abschnitt_id=r.abschnitt_id,
            mandat_id=r.mandat_id,
            fall_id=r.fall_id,
            line_id=r.line_id,
            article_id=r.article_id,
            entry_id=r.entry_id,
            section_id=r.section_id,
            reference_key=r.reference_key,
            leitbild_ausrichtung=r.ausrichtung,
            konvent_prozedur=r.prozedur,
            rang=_rang(r),
            prozedur=_prozedur(r),
            status=_status(r),
            artikel_ids=r.resolution_ids,
            canonical=r.canonical and _status(r) is VerfassungsStatus.GRUNDLEGEND_RATIFIZIERT,
            verfassungs_weight=_verfassungs_weight(r),
            verfassungs_tier=_verfassungs_tier(r),
            artikel_tags=tuple(
                dict.fromkeys(
                    (
                        *r.resolution_tags,
                        _rang(r).value,
                        _prozedur(r).value,
                        _status(r).value,
                    )
                )
            ),
            summary=(
                f"{r.resolution_id} ratified as {_rang(r).value} via "
                f"{_prozedur(r).value} with status {_status(r).value}."
            ),
        )
        for index, r in enumerate(resolved_konvent.resolutionen, start=1)
    )
    if not artikel:
        raise ValueError("missions verfassung requires at least one artikel")

    severity = "info"
    status = "verfassung-grundlegend-ratifiziert"
    if any(a.status is VerfassungsStatus.GESPERRT for a in artikel):
        severity = "critical"
        status = "verfassung-gesperrt"
    elif any(a.status is VerfassungsStatus.RATIFIZIERT for a in artikel):
        severity = "warning"
        status = "verfassung-ratifiziert"

    verfassungs_signal = TelemetrySignal(
        signal_name="missions-verfassung",
        boundary=resolved_konvent.konvent_signal.boundary,
        correlation_id=verfassungs_id,
        severity=severity,
        status=status,
        metrics={
            "artikel_count": float(len(artikel)),
            "gesperrt_count": float(sum(1 for a in artikel if a.status is VerfassungsStatus.GESPERRT)),
            "ratifiziert_count": float(sum(1 for a in artikel if a.status is VerfassungsStatus.RATIFIZIERT)),
            "grundlegend_count": float(sum(1 for a in artikel if a.status is VerfassungsStatus.GRUNDLEGEND_RATIFIZIERT)),
            "canonical_count": float(sum(1 for a in artikel if a.canonical)),
            "avg_verfassungs_weight": round(sum(a.verfassungs_weight for a in artikel) / len(artikel), 3),
        },
        labels={"verfassungs_id": verfassungs_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_konvent.final_snapshot.runtime_stage,
        signals=(verfassungs_signal, *resolved_konvent.final_snapshot.signals),
        alerts=resolved_konvent.final_snapshot.alerts,
        audit_entries=resolved_konvent.final_snapshot.audit_entries,
        active_controls=resolved_konvent.final_snapshot.active_controls,
    )
    return MissionsVerfassung(
        verfassungs_id=verfassungs_id,
        leitbild_konvent=resolved_konvent,
        artikel=artikel,
        verfassungs_signal=verfassungs_signal,
        final_snapshot=final_snapshot,
    )
