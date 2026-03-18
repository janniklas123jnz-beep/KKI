"""Leitordnung consolidating manifest sections into supreme Leitstern constitutional norms."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .ordnungs_manifest import (
    ManifestAbschnitt,
    ManifestGeltung,
    ManifestKapitel,
    ManifestVerfahren,
    OrdnungsManifest,
    build_ordnungs_manifest,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class OrdnungsRang(str, Enum):
    """Constitutional rank assigned to one manifest section."""

    SCHUTZ_RANG = "schutz-rang"
    ORDNUNGS_RANG = "ordnungs-rang"
    SOUVERAENITAETS_RANG = "souveraenitaets-rang"


class OrdnungsTyp(str, Enum):
    """Order type that governs how the norm is constituted."""

    NOTORDNUNG = "notordnung"
    REGELORDNUNG = "regelordnung"
    PLENARORDNUNG = "plenarordnung"


class OrdnungsKraft(str, Enum):
    """Legal force of the constitutional norm."""

    BLOCKIERT = "blockiert"
    WIRKSAM = "wirksam"
    LEITEND = "leitend"


@dataclass(frozen=True)
class OrdnungsNorm:
    """One constitutional norm derived from a manifest section."""

    norm_id: str
    sequence: int
    abschnitt_id: str
    klausel_id: str
    artikel_id: str
    mandat_id: str
    fall_id: str
    line_id: str
    article_id: str
    entry_id: str
    section_id: str
    reference_key: str
    manifest_kapitel: ManifestKapitel
    manifest_geltung: ManifestGeltung
    manifest_verfahren: ManifestVerfahren
    rang: OrdnungsRang
    typ: OrdnungsTyp
    kraft: OrdnungsKraft
    norm_ids: tuple[str, ...]
    supreme: bool
    ordnungs_weight: float
    authority_level: int
    norm_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "norm_id", _non_empty(self.norm_id, field_name="norm_id"))
        object.__setattr__(self, "abschnitt_id", _non_empty(self.abschnitt_id, field_name="abschnitt_id"))
        object.__setattr__(self, "klausel_id", _non_empty(self.klausel_id, field_name="klausel_id"))
        object.__setattr__(self, "artikel_id", _non_empty(self.artikel_id, field_name="artikel_id"))
        object.__setattr__(self, "mandat_id", _non_empty(self.mandat_id, field_name="mandat_id"))
        object.__setattr__(self, "fall_id", _non_empty(self.fall_id, field_name="fall_id"))
        object.__setattr__(self, "line_id", _non_empty(self.line_id, field_name="line_id"))
        object.__setattr__(self, "article_id", _non_empty(self.article_id, field_name="article_id"))
        object.__setattr__(self, "entry_id", _non_empty(self.entry_id, field_name="entry_id"))
        object.__setattr__(self, "section_id", _non_empty(self.section_id, field_name="section_id"))
        object.__setattr__(self, "reference_key", _non_empty(self.reference_key, field_name="reference_key"))
        object.__setattr__(self, "ordnungs_weight", _clamp01(self.ordnungs_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.authority_level < 1:
            raise ValueError("authority_level must be positive")
        if not self.norm_ids:
            raise ValueError("norm_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "norm_id": self.norm_id,
            "sequence": self.sequence,
            "abschnitt_id": self.abschnitt_id,
            "klausel_id": self.klausel_id,
            "artikel_id": self.artikel_id,
            "mandat_id": self.mandat_id,
            "fall_id": self.fall_id,
            "line_id": self.line_id,
            "article_id": self.article_id,
            "entry_id": self.entry_id,
            "section_id": self.section_id,
            "reference_key": self.reference_key,
            "manifest_kapitel": self.manifest_kapitel.value,
            "manifest_geltung": self.manifest_geltung.value,
            "manifest_verfahren": self.manifest_verfahren.value,
            "rang": self.rang.value,
            "typ": self.typ.value,
            "kraft": self.kraft.value,
            "norm_ids": list(self.norm_ids),
            "supreme": self.supreme,
            "ordnungs_weight": self.ordnungs_weight,
            "authority_level": self.authority_level,
            "norm_tags": list(self.norm_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class Leitordnung:
    """Constitutional order consolidating Leitstern manifest sections into supreme norms."""

    ordnung_id: str
    ordnungs_manifest: OrdnungsManifest
    normen: tuple[OrdnungsNorm, ...]
    ordnungs_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "ordnung_id", _non_empty(self.ordnung_id, field_name="ordnung_id"))

    @property
    def blockiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.kraft is OrdnungsKraft.BLOCKIERT)

    @property
    def wirksam_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.kraft is OrdnungsKraft.WIRKSAM)

    @property
    def leitend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.kraft is OrdnungsKraft.LEITEND)

    def to_dict(self) -> dict[str, object]:
        return {
            "ordnung_id": self.ordnung_id,
            "ordnungs_manifest": self.ordnungs_manifest.to_dict(),
            "normen": [n.to_dict() for n in self.normen],
            "ordnungs_signal": self.ordnungs_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "blockiert_norm_ids": list(self.blockiert_norm_ids),
            "wirksam_norm_ids": list(self.wirksam_norm_ids),
            "leitend_norm_ids": list(self.leitend_norm_ids),
        }


def _rang(abschnitt: ManifestAbschnitt) -> OrdnungsRang:
    return {
        ManifestKapitel.SCHUTZ_KAPITEL: OrdnungsRang.SCHUTZ_RANG,
        ManifestKapitel.ORDNUNGS_KAPITEL: OrdnungsRang.ORDNUNGS_RANG,
        ManifestKapitel.SOUVERAENITAETS_KAPITEL: OrdnungsRang.SOUVERAENITAETS_RANG,
    }[abschnitt.kapitel]


def _typ(abschnitt: ManifestAbschnitt) -> OrdnungsTyp:
    return {
        ManifestVerfahren.NOTVERFAHREN: OrdnungsTyp.NOTORDNUNG,
        ManifestVerfahren.REGELVERFAHREN: OrdnungsTyp.REGELORDNUNG,
        ManifestVerfahren.PLENARVERFAHREN: OrdnungsTyp.PLENARORDNUNG,
    }[abschnitt.verfahren]


def _kraft(abschnitt: ManifestAbschnitt) -> OrdnungsKraft:
    return {
        ManifestGeltung.GESPERRT: OrdnungsKraft.BLOCKIERT,
        ManifestGeltung.PROKLAMIERT: OrdnungsKraft.WIRKSAM,
        ManifestGeltung.HOHEITSRECHT: OrdnungsKraft.LEITEND,
    }[abschnitt.geltung]


def _ordnungs_weight(abschnitt: ManifestAbschnitt) -> float:
    bonus = {
        OrdnungsKraft.BLOCKIERT: 0.0,
        OrdnungsKraft.WIRKSAM: 0.04,
        OrdnungsKraft.LEITEND: 0.08,
    }[_kraft(abschnitt)]
    return round(min(1.0, abschnitt.manifest_weight + bonus), 3)


def _authority_level(abschnitt: ManifestAbschnitt) -> int:
    return {
        OrdnungsKraft.BLOCKIERT: abschnitt.proclamation_rank,
        OrdnungsKraft.WIRKSAM: abschnitt.proclamation_rank + 1,
        OrdnungsKraft.LEITEND: abschnitt.proclamation_rank + 2,
    }[_kraft(abschnitt)]


def build_leitordnung(
    ordnungs_manifest: OrdnungsManifest | None = None,
    *,
    ordnung_id: str = "leitordnung",
) -> Leitordnung:
    """Build the constitutional order consolidating Leitstern manifest sections."""

    resolved_manifest = (
        build_ordnungs_manifest(manifest_id=f"{ordnung_id}-manifest")
        if ordnungs_manifest is None
        else ordnungs_manifest
    )
    normen = tuple(
        OrdnungsNorm(
            norm_id=f"{ordnung_id}-{abschnitt.abschnitt_id.removeprefix(f'{resolved_manifest.manifest_id}-')}",
            sequence=index,
            abschnitt_id=abschnitt.abschnitt_id,
            klausel_id=abschnitt.klausel_id,
            artikel_id=abschnitt.artikel_id,
            mandat_id=abschnitt.mandat_id,
            fall_id=abschnitt.fall_id,
            line_id=abschnitt.line_id,
            article_id=abschnitt.article_id,
            entry_id=abschnitt.entry_id,
            section_id=abschnitt.section_id,
            reference_key=abschnitt.reference_key,
            manifest_kapitel=abschnitt.kapitel,
            manifest_geltung=abschnitt.geltung,
            manifest_verfahren=abschnitt.verfahren,
            rang=_rang(abschnitt),
            typ=_typ(abschnitt),
            kraft=_kraft(abschnitt),
            norm_ids=abschnitt.abschnitt_ids,
            supreme=abschnitt.promulgated and _kraft(abschnitt) is OrdnungsKraft.LEITEND,
            ordnungs_weight=_ordnungs_weight(abschnitt),
            authority_level=_authority_level(abschnitt),
            norm_tags=tuple(
                dict.fromkeys(
                    (
                        *abschnitt.abschnitt_tags,
                        _rang(abschnitt).value,
                        _typ(abschnitt).value,
                        _kraft(abschnitt).value,
                    )
                )
            ),
            summary=(
                f"{abschnitt.abschnitt_id} constituted as {_rang(abschnitt).value} via "
                f"{_typ(abschnitt).value} with kraft {_kraft(abschnitt).value}."
            ),
        )
        for index, abschnitt in enumerate(resolved_manifest.abschnitte, start=1)
    )
    if not normen:
        raise ValueError("leitordnung requires at least one norm")

    severity = "info"
    status = "ordnung-leitend"
    if any(n.kraft is OrdnungsKraft.BLOCKIERT for n in normen):
        severity = "critical"
        status = "ordnung-blockiert"
    elif any(n.kraft is OrdnungsKraft.WIRKSAM for n in normen):
        severity = "warning"
        status = "ordnung-wirksam"

    ordnungs_signal = TelemetrySignal(
        signal_name="leitordnung",
        boundary=resolved_manifest.manifest_signal.boundary,
        correlation_id=ordnung_id,
        severity=severity,
        status=status,
        metrics={
            "norm_count": float(len(normen)),
            "blockiert_count": float(sum(1 for n in normen if n.kraft is OrdnungsKraft.BLOCKIERT)),
            "wirksam_count": float(sum(1 for n in normen if n.kraft is OrdnungsKraft.WIRKSAM)),
            "leitend_count": float(sum(1 for n in normen if n.kraft is OrdnungsKraft.LEITEND)),
            "supreme_count": float(sum(1 for n in normen if n.supreme)),
            "avg_ordnungs_weight": round(sum(n.ordnungs_weight for n in normen) / len(normen), 3),
        },
        labels={"ordnung_id": ordnung_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_manifest.final_snapshot.runtime_stage,
        signals=(ordnungs_signal, *resolved_manifest.final_snapshot.signals),
        alerts=resolved_manifest.final_snapshot.alerts,
        audit_entries=resolved_manifest.final_snapshot.audit_entries,
        active_controls=resolved_manifest.final_snapshot.active_controls,
    )
    return Leitordnung(
        ordnung_id=ordnung_id,
        ordnungs_manifest=resolved_manifest,
        normen=normen,
        ordnungs_signal=ordnungs_signal,
        final_snapshot=final_snapshot,
    )
