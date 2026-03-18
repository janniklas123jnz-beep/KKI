"""Leitstern konstitution constituting proclaimed purpose clauses as the supreme Leitstern charter."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .zweck_manifest import (
    ManifestGeltung,
    ManifestProzedur,
    ZweckDimension,
    ZweckKlausel,
    ZweckManifest,
    build_zweck_manifest,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class KonstitutionsEbene(str, Enum):
    """Constitutional level that anchors one supreme charter article."""

    SCHUTZ_EBENE = "schutz-ebene"
    ORDNUNGS_EBENE = "ordnungs-ebene"
    SOUVERAENITAETS_EBENE = "souveraenitaets-ebene"


class KonstitutionsProzedur(str, Enum):
    """Constitutional procedure used to constitute the charter article."""

    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KonstitutionsRang(str, Enum):
    """Canonical rank of the constituted charter article."""

    GESPERRT = "gesperrt"
    KONSTITUIERT = "konstituiert"
    GRUNDLEGEND_KONSTITUIERT = "grundlegend-konstituiert"


@dataclass(frozen=True)
class KonstitutionsArtikel:
    """One supreme charter article derived from a proclaimed purpose clause."""

    artikel_id: str
    sequence: int
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
    zweck_dimension: ZweckDimension
    manifest_prozedur: ManifestProzedur
    ebene: KonstitutionsEbene
    prozedur: KonstitutionsProzedur
    rang: KonstitutionsRang
    artikel_ids: tuple[str, ...]
    canonical: bool
    konstitutions_weight: float
    konstitutions_tier: int
    artikel_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
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
        object.__setattr__(self, "konstitutions_weight", _clamp01(self.konstitutions_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.konstitutions_tier < 1:
            raise ValueError("konstitutions_tier must be positive")
        if not self.artikel_ids:
            raise ValueError("artikel_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "artikel_id": self.artikel_id,
            "sequence": self.sequence,
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
            "zweck_dimension": self.zweck_dimension.value,
            "manifest_prozedur": self.manifest_prozedur.value,
            "ebene": self.ebene.value,
            "prozedur": self.prozedur.value,
            "rang": self.rang.value,
            "artikel_ids": list(self.artikel_ids),
            "canonical": self.canonical,
            "konstitutions_weight": self.konstitutions_weight,
            "konstitutions_tier": self.konstitutions_tier,
            "artikel_tags": list(self.artikel_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class LeitsternKonstitution:
    """The supreme Leitstern constitution elevating purpose clauses to foundational charter."""

    konstitutions_id: str
    zweck_manifest: ZweckManifest
    artikel: tuple[KonstitutionsArtikel, ...]
    konstitutions_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "konstitutions_id", _non_empty(self.konstitutions_id, field_name="konstitutions_id"))

    @property
    def gesperrt_artikel_ids(self) -> tuple[str, ...]:
        return tuple(a.artikel_id for a in self.artikel if a.rang is KonstitutionsRang.GESPERRT)

    @property
    def konstituiert_artikel_ids(self) -> tuple[str, ...]:
        return tuple(a.artikel_id for a in self.artikel if a.rang is KonstitutionsRang.KONSTITUIERT)

    @property
    def grundlegend_artikel_ids(self) -> tuple[str, ...]:
        return tuple(a.artikel_id for a in self.artikel if a.rang is KonstitutionsRang.GRUNDLEGEND_KONSTITUIERT)

    def to_dict(self) -> dict[str, object]:
        return {
            "konstitutions_id": self.konstitutions_id,
            "zweck_manifest": self.zweck_manifest.to_dict(),
            "artikel": [a.to_dict() for a in self.artikel],
            "konstitutions_signal": self.konstitutions_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "gesperrt_artikel_ids": list(self.gesperrt_artikel_ids),
            "konstituiert_artikel_ids": list(self.konstituiert_artikel_ids),
            "grundlegend_artikel_ids": list(self.grundlegend_artikel_ids),
        }


def _ebene(klausel: ZweckKlausel) -> KonstitutionsEbene:
    return {
        ZweckDimension.SCHUTZ_DIMENSION: KonstitutionsEbene.SCHUTZ_EBENE,
        ZweckDimension.ORDNUNGS_DIMENSION: KonstitutionsEbene.ORDNUNGS_EBENE,
        ZweckDimension.SOUVERAENITAETS_DIMENSION: KonstitutionsEbene.SOUVERAENITAETS_EBENE,
    }[klausel.dimension]


def _prozedur(klausel: ZweckKlausel) -> KonstitutionsProzedur:
    return {
        ManifestProzedur.NOTPROZEDUR: KonstitutionsProzedur.NOTPROZEDUR,
        ManifestProzedur.REGELPROTOKOLL: KonstitutionsProzedur.REGELPROTOKOLL,
        ManifestProzedur.PLENARPROTOKOLL: KonstitutionsProzedur.PLENARPROTOKOLL,
    }[klausel.prozedur]


def _rang(klausel: ZweckKlausel) -> KonstitutionsRang:
    return {
        ManifestGeltung.GESPERRT: KonstitutionsRang.GESPERRT,
        ManifestGeltung.PROKLAMIERT: KonstitutionsRang.KONSTITUIERT,
        ManifestGeltung.GRUNDLEGEND_PROKLAMIERT: KonstitutionsRang.GRUNDLEGEND_KONSTITUIERT,
    }[klausel.geltung]


def _konstitutions_weight(klausel: ZweckKlausel) -> float:
    bonus = {
        KonstitutionsRang.GESPERRT: 0.0,
        KonstitutionsRang.KONSTITUIERT: 0.04,
        KonstitutionsRang.GRUNDLEGEND_KONSTITUIERT: 0.08,
    }[_rang(klausel)]
    return round(min(1.0, klausel.manifest_weight + bonus), 3)


def _konstitutions_tier(klausel: ZweckKlausel) -> int:
    return {
        KonstitutionsRang.GESPERRT: klausel.manifest_tier,
        KonstitutionsRang.KONSTITUIERT: klausel.manifest_tier + 1,
        KonstitutionsRang.GRUNDLEGEND_KONSTITUIERT: klausel.manifest_tier + 2,
    }[_rang(klausel)]


def build_leitstern_konstitution(
    zweck_manifest: ZweckManifest | None = None,
    *,
    konstitutions_id: str = "leitstern-konstitution",
) -> LeitsternKonstitution:
    """Build the supreme Leitstern constitution from proclaimed purpose clauses."""

    resolved_manifest = (
        build_zweck_manifest(manifest_id=f"{konstitutions_id}-manifest")
        if zweck_manifest is None
        else zweck_manifest
    )
    artikel = tuple(
        KonstitutionsArtikel(
            artikel_id=f"{konstitutions_id}-{k.klausel_id.removeprefix(f'{resolved_manifest.manifest_id}-')}",
            sequence=index,
            klausel_id=k.klausel_id,
            artikel_ref_id=k.artikel_id,
            resolution_id=k.resolution_id,
            satz_id=k.satz_id,
            eintrag_id=k.eintrag_id,
            pfeiler_id=k.pfeiler_id,
            norm_id=k.norm_id,
            abschnitt_id=k.abschnitt_id,
            mandat_id=k.mandat_id,
            fall_id=k.fall_id,
            line_id=k.line_id,
            article_id=k.article_id,
            entry_id=k.entry_id,
            section_id=k.section_id,
            reference_key=k.reference_key,
            zweck_dimension=k.dimension,
            manifest_prozedur=k.prozedur,
            ebene=_ebene(k),
            prozedur=_prozedur(k),
            rang=_rang(k),
            artikel_ids=k.klausel_ids,
            canonical=k.canonical and _rang(k) is KonstitutionsRang.GRUNDLEGEND_KONSTITUIERT,
            konstitutions_weight=_konstitutions_weight(k),
            konstitutions_tier=_konstitutions_tier(k),
            artikel_tags=tuple(
                dict.fromkeys(
                    (
                        *k.klausel_tags,
                        _ebene(k).value,
                        _prozedur(k).value,
                        _rang(k).value,
                    )
                )
            ),
            summary=(
                f"{k.klausel_id} constituted at {_ebene(k).value} via "
                f"{_prozedur(k).value} with rang {_rang(k).value}."
            ),
        )
        for index, k in enumerate(resolved_manifest.klauseln, start=1)
    )
    if not artikel:
        raise ValueError("leitstern konstitution requires at least one artikel")

    severity = "info"
    status = "konstitution-grundlegend-konstituiert"
    if any(a.rang is KonstitutionsRang.GESPERRT for a in artikel):
        severity = "critical"
        status = "konstitution-gesperrt"
    elif any(a.rang is KonstitutionsRang.KONSTITUIERT for a in artikel):
        severity = "warning"
        status = "konstitution-konstituiert"

    konstitutions_signal = TelemetrySignal(
        signal_name="leitstern-konstitution",
        boundary=resolved_manifest.manifest_signal.boundary,
        correlation_id=konstitutions_id,
        severity=severity,
        status=status,
        metrics={
            "artikel_count": float(len(artikel)),
            "gesperrt_count": float(sum(1 for a in artikel if a.rang is KonstitutionsRang.GESPERRT)),
            "konstituiert_count": float(sum(1 for a in artikel if a.rang is KonstitutionsRang.KONSTITUIERT)),
            "grundlegend_count": float(sum(1 for a in artikel if a.rang is KonstitutionsRang.GRUNDLEGEND_KONSTITUIERT)),
            "canonical_count": float(sum(1 for a in artikel if a.canonical)),
            "avg_konstitutions_weight": round(sum(a.konstitutions_weight for a in artikel) / len(artikel), 3),
        },
        labels={"konstitutions_id": konstitutions_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_manifest.final_snapshot.runtime_stage,
        signals=(konstitutions_signal, *resolved_manifest.final_snapshot.signals),
        alerts=resolved_manifest.final_snapshot.alerts,
        audit_entries=resolved_manifest.final_snapshot.audit_entries,
        active_controls=resolved_manifest.final_snapshot.active_controls,
    )
    return LeitsternKonstitution(
        konstitutions_id=konstitutions_id,
        zweck_manifest=resolved_manifest,
        artikel=artikel,
        konstitutions_signal=konstitutions_signal,
        final_snapshot=final_snapshot,
    )
