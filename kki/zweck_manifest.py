"""Zweck manifest proclaiming ratified mission articles as purposeful Leitstern clauses."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .missions_verfassung import (
    MissionsArtikel,
    MissionsRang,
    MissionsVerfassung,
    VerfassungsProzedur,
    VerfassungsStatus,
    build_missions_verfassung,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class ZweckDimension(str, Enum):
    """Purpose dimension that frames one manifest clause."""

    SCHUTZ_DIMENSION = "schutz-dimension"
    ORDNUNGS_DIMENSION = "ordnungs-dimension"
    SOUVERAENITAETS_DIMENSION = "souveraenitaets-dimension"


class ManifestProzedur(str, Enum):
    """Proclamation protocol used to enshrine the purpose clause."""

    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class ManifestGeltung(str, Enum):
    """Canonical validity status of the proclaimed purpose clause."""

    GESPERRT = "gesperrt"
    PROKLAMIERT = "proklamiert"
    GRUNDLEGEND_PROKLAMIERT = "grundlegend-proklamiert"


@dataclass(frozen=True)
class ZweckKlausel:
    """One purpose clause derived from a ratified mission article."""

    klausel_id: str
    sequence: int
    artikel_id: str
    resolution_id: str
    artikel_ref_id: str
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
    missions_rang: MissionsRang
    verfassungs_prozedur: VerfassungsProzedur
    dimension: ZweckDimension
    prozedur: ManifestProzedur
    geltung: ManifestGeltung
    klausel_ids: tuple[str, ...]
    canonical: bool
    manifest_weight: float
    manifest_tier: int
    klausel_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "klausel_id", _non_empty(self.klausel_id, field_name="klausel_id"))
        object.__setattr__(self, "artikel_id", _non_empty(self.artikel_id, field_name="artikel_id"))
        object.__setattr__(self, "resolution_id", _non_empty(self.resolution_id, field_name="resolution_id"))
        object.__setattr__(self, "artikel_ref_id", _non_empty(self.artikel_ref_id, field_name="artikel_ref_id"))
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
        object.__setattr__(self, "manifest_weight", _clamp01(self.manifest_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.manifest_tier < 1:
            raise ValueError("manifest_tier must be positive")
        if not self.klausel_ids:
            raise ValueError("klausel_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "klausel_id": self.klausel_id,
            "sequence": self.sequence,
            "artikel_id": self.artikel_id,
            "resolution_id": self.resolution_id,
            "artikel_ref_id": self.artikel_ref_id,
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
            "missions_rang": self.missions_rang.value,
            "verfassungs_prozedur": self.verfassungs_prozedur.value,
            "dimension": self.dimension.value,
            "prozedur": self.prozedur.value,
            "geltung": self.geltung.value,
            "klausel_ids": list(self.klausel_ids),
            "canonical": self.canonical,
            "manifest_weight": self.manifest_weight,
            "manifest_tier": self.manifest_tier,
            "klausel_tags": list(self.klausel_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class ZweckManifest:
    """Purpose manifest proclaiming Leitstern mission articles as binding clauses."""

    manifest_id: str
    missions_verfassung: MissionsVerfassung
    klauseln: tuple[ZweckKlausel, ...]
    manifest_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "manifest_id", _non_empty(self.manifest_id, field_name="manifest_id"))

    @property
    def gesperrt_klausel_ids(self) -> tuple[str, ...]:
        return tuple(k.klausel_id for k in self.klauseln if k.geltung is ManifestGeltung.GESPERRT)

    @property
    def proklamiert_klausel_ids(self) -> tuple[str, ...]:
        return tuple(k.klausel_id for k in self.klauseln if k.geltung is ManifestGeltung.PROKLAMIERT)

    @property
    def grundlegend_klausel_ids(self) -> tuple[str, ...]:
        return tuple(k.klausel_id for k in self.klauseln if k.geltung is ManifestGeltung.GRUNDLEGEND_PROKLAMIERT)

    def to_dict(self) -> dict[str, object]:
        return {
            "manifest_id": self.manifest_id,
            "missions_verfassung": self.missions_verfassung.to_dict(),
            "klauseln": [k.to_dict() for k in self.klauseln],
            "manifest_signal": self.manifest_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "gesperrt_klausel_ids": list(self.gesperrt_klausel_ids),
            "proklamiert_klausel_ids": list(self.proklamiert_klausel_ids),
            "grundlegend_klausel_ids": list(self.grundlegend_klausel_ids),
        }


def _dimension(artikel: MissionsArtikel) -> ZweckDimension:
    return {
        MissionsRang.SCHUTZ_RANG: ZweckDimension.SCHUTZ_DIMENSION,
        MissionsRang.ORDNUNGS_RANG: ZweckDimension.ORDNUNGS_DIMENSION,
        MissionsRang.SOUVERAENITAETS_RANG: ZweckDimension.SOUVERAENITAETS_DIMENSION,
    }[artikel.rang]


def _prozedur(artikel: MissionsArtikel) -> ManifestProzedur:
    return {
        VerfassungsProzedur.NOTPROZEDUR: ManifestProzedur.NOTPROZEDUR,
        VerfassungsProzedur.REGELPROTOKOLL: ManifestProzedur.REGELPROTOKOLL,
        VerfassungsProzedur.PLENARPROTOKOLL: ManifestProzedur.PLENARPROTOKOLL,
    }[artikel.prozedur]


def _geltung(artikel: MissionsArtikel) -> ManifestGeltung:
    return {
        VerfassungsStatus.GESPERRT: ManifestGeltung.GESPERRT,
        VerfassungsStatus.RATIFIZIERT: ManifestGeltung.PROKLAMIERT,
        VerfassungsStatus.GRUNDLEGEND_RATIFIZIERT: ManifestGeltung.GRUNDLEGEND_PROKLAMIERT,
    }[artikel.status]


def _manifest_weight(artikel: MissionsArtikel) -> float:
    bonus = {
        ManifestGeltung.GESPERRT: 0.0,
        ManifestGeltung.PROKLAMIERT: 0.04,
        ManifestGeltung.GRUNDLEGEND_PROKLAMIERT: 0.08,
    }[_geltung(artikel)]
    return round(min(1.0, artikel.verfassungs_weight + bonus), 3)


def _manifest_tier(artikel: MissionsArtikel) -> int:
    return {
        ManifestGeltung.GESPERRT: artikel.verfassungs_tier,
        ManifestGeltung.PROKLAMIERT: artikel.verfassungs_tier + 1,
        ManifestGeltung.GRUNDLEGEND_PROKLAMIERT: artikel.verfassungs_tier + 2,
    }[_geltung(artikel)]


def build_zweck_manifest(
    missions_verfassung: MissionsVerfassung | None = None,
    *,
    manifest_id: str = "zweck-manifest",
) -> ZweckManifest:
    """Build the purpose manifest proclaiming Leitstern mission articles."""

    resolved_verfassung = (
        build_missions_verfassung(verfassungs_id=f"{manifest_id}-verfassung")
        if missions_verfassung is None
        else missions_verfassung
    )
    klauseln = tuple(
        ZweckKlausel(
            klausel_id=f"{manifest_id}-{a.artikel_id.removeprefix(f'{resolved_verfassung.verfassungs_id}-')}",
            sequence=index,
            artikel_id=a.artikel_id,
            resolution_id=a.resolution_id,
            artikel_ref_id=a.artikel_ref_id,
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
            missions_rang=a.rang,
            verfassungs_prozedur=a.prozedur,
            dimension=_dimension(a),
            prozedur=_prozedur(a),
            geltung=_geltung(a),
            klausel_ids=a.artikel_ids,
            canonical=a.canonical and _geltung(a) is ManifestGeltung.GRUNDLEGEND_PROKLAMIERT,
            manifest_weight=_manifest_weight(a),
            manifest_tier=_manifest_tier(a),
            klausel_tags=tuple(
                dict.fromkeys(
                    (
                        *a.artikel_tags,
                        _dimension(a).value,
                        _prozedur(a).value,
                        _geltung(a).value,
                    )
                )
            ),
            summary=(
                f"{a.artikel_id} proclaimed in {_dimension(a).value} via "
                f"{_prozedur(a).value} with geltung {_geltung(a).value}."
            ),
        )
        for index, a in enumerate(resolved_verfassung.artikel, start=1)
    )
    if not klauseln:
        raise ValueError("zweck manifest requires at least one klausel")

    severity = "info"
    status = "manifest-grundlegend-proklamiert"
    if any(k.geltung is ManifestGeltung.GESPERRT for k in klauseln):
        severity = "critical"
        status = "manifest-gesperrt"
    elif any(k.geltung is ManifestGeltung.PROKLAMIERT for k in klauseln):
        severity = "warning"
        status = "manifest-proklamiert"

    manifest_signal = TelemetrySignal(
        signal_name="zweck-manifest",
        boundary=resolved_verfassung.verfassungs_signal.boundary,
        correlation_id=manifest_id,
        severity=severity,
        status=status,
        metrics={
            "klausel_count": float(len(klauseln)),
            "gesperrt_count": float(sum(1 for k in klauseln if k.geltung is ManifestGeltung.GESPERRT)),
            "proklamiert_count": float(sum(1 for k in klauseln if k.geltung is ManifestGeltung.PROKLAMIERT)),
            "grundlegend_count": float(sum(1 for k in klauseln if k.geltung is ManifestGeltung.GRUNDLEGEND_PROKLAMIERT)),
            "canonical_count": float(sum(1 for k in klauseln if k.canonical)),
            "avg_manifest_weight": round(sum(k.manifest_weight for k in klauseln) / len(klauseln), 3),
        },
        labels={"manifest_id": manifest_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_verfassung.final_snapshot.runtime_stage,
        signals=(manifest_signal, *resolved_verfassung.final_snapshot.signals),
        alerts=resolved_verfassung.final_snapshot.alerts,
        audit_entries=resolved_verfassung.final_snapshot.audit_entries,
        active_controls=resolved_verfassung.final_snapshot.active_controls,
    )
    return ZweckManifest(
        manifest_id=manifest_id,
        missions_verfassung=resolved_verfassung,
        klauseln=klauseln,
        manifest_signal=manifest_signal,
        final_snapshot=final_snapshot,
    )
