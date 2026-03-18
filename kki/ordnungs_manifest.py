"""Ordnungs manifest proclaiming sovereignty clauses as supreme Leitstern directives."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .souveraenitaets_akt import (
    AktKlausel,
    AktProzedur,
    AktSektion,
    AktStatus,
    SouveraenitaetsAkt,
    build_souveraenitaets_akt,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class ManifestKapitel(str, Enum):
    """Manifest chapter that proclaims one sovereignty clause."""

    SCHUTZ_KAPITEL = "schutz-kapitel"
    ORDNUNGS_KAPITEL = "ordnungs-kapitel"
    SOUVERAENITAETS_KAPITEL = "souveraenitaets-kapitel"


class ManifestVerfahren(str, Enum):
    """Proclamation procedure used to enact the clause."""

    NOTVERFAHREN = "notverfahren"
    REGELVERFAHREN = "regelverfahren"
    PLENARVERFAHREN = "plenarverfahren"


class ManifestGeltung(str, Enum):
    """Legal force of the proclaimed manifest section."""

    GESPERRT = "gesperrt"
    PROKLAMIERT = "proklamiert"
    HOHEITSRECHT = "hoheitsrecht"


@dataclass(frozen=True)
class ManifestAbschnitt:
    """One manifest section derived from a sovereignty clause."""

    abschnitt_id: str
    sequence: int
    klausel_id: str
    artikel_id: str
    mandat_id: str
    fall_id: str
    line_id: str
    article_id: str
    entry_id: str
    section_id: str
    reference_key: str
    akt_sektion: AktSektion
    akt_status: AktStatus
    akt_prozedur: AktProzedur
    kapitel: ManifestKapitel
    verfahren: ManifestVerfahren
    geltung: ManifestGeltung
    abschnitt_ids: tuple[str, ...]
    promulgated: bool
    manifest_weight: float
    proclamation_rank: int
    abschnitt_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
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
        object.__setattr__(self, "manifest_weight", _clamp01(self.manifest_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.proclamation_rank < 1:
            raise ValueError("proclamation_rank must be positive")
        if not self.abschnitt_ids:
            raise ValueError("abschnitt_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "abschnitt_id": self.abschnitt_id,
            "sequence": self.sequence,
            "klausel_id": self.klausel_id,
            "artikel_id": self.artikel_id,
            "mandat_id": self.mandat_id,
            "fall_id": self.fall_id,
            "line_id": self.line_id,
            "article_id": self.article_id,
            "entry_id": self.entry_id,
            "section_id": self.section_id,
            "reference_key": self.reference_key,
            "akt_sektion": self.akt_sektion.value,
            "akt_status": self.akt_status.value,
            "akt_prozedur": self.akt_prozedur.value,
            "kapitel": self.kapitel.value,
            "verfahren": self.verfahren.value,
            "geltung": self.geltung.value,
            "abschnitt_ids": list(self.abschnitt_ids),
            "promulgated": self.promulgated,
            "manifest_weight": self.manifest_weight,
            "proclamation_rank": self.proclamation_rank,
            "abschnitt_tags": list(self.abschnitt_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class OrdnungsManifest:
    """Manifest proclaiming Leitstern sovereignty clauses as supreme order directives."""

    manifest_id: str
    souveraenitaets_akt: SouveraenitaetsAkt
    abschnitte: tuple[ManifestAbschnitt, ...]
    manifest_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "manifest_id", _non_empty(self.manifest_id, field_name="manifest_id"))

    @property
    def gesperrt_abschnitt_ids(self) -> tuple[str, ...]:
        return tuple(a.abschnitt_id for a in self.abschnitte if a.geltung is ManifestGeltung.GESPERRT)

    @property
    def proklamiert_abschnitt_ids(self) -> tuple[str, ...]:
        return tuple(a.abschnitt_id for a in self.abschnitte if a.geltung is ManifestGeltung.PROKLAMIERT)

    @property
    def hoheitsrecht_abschnitt_ids(self) -> tuple[str, ...]:
        return tuple(a.abschnitt_id for a in self.abschnitte if a.geltung is ManifestGeltung.HOHEITSRECHT)

    def to_dict(self) -> dict[str, object]:
        return {
            "manifest_id": self.manifest_id,
            "souveraenitaets_akt": self.souveraenitaets_akt.to_dict(),
            "abschnitte": [a.to_dict() for a in self.abschnitte],
            "manifest_signal": self.manifest_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "gesperrt_abschnitt_ids": list(self.gesperrt_abschnitt_ids),
            "proklamiert_abschnitt_ids": list(self.proklamiert_abschnitt_ids),
            "hoheitsrecht_abschnitt_ids": list(self.hoheitsrecht_abschnitt_ids),
        }


def _kapitel(klausel: AktKlausel) -> ManifestKapitel:
    return {
        AktSektion.SCHUTZ_SEKTION: ManifestKapitel.SCHUTZ_KAPITEL,
        AktSektion.ORDNUNGS_SEKTION: ManifestKapitel.ORDNUNGS_KAPITEL,
        AktSektion.SOUVERAENITAETS_SEKTION: ManifestKapitel.SOUVERAENITAETS_KAPITEL,
    }[klausel.sektion]


def _verfahren(klausel: AktKlausel) -> ManifestVerfahren:
    return {
        AktProzedur.EILVERFAHREN: ManifestVerfahren.NOTVERFAHREN,
        AktProzedur.STANDARDVERFAHREN: ManifestVerfahren.REGELVERFAHREN,
        AktProzedur.VOLLVERFAHREN: ManifestVerfahren.PLENARVERFAHREN,
    }[klausel.prozedur]


def _geltung(klausel: AktKlausel) -> ManifestGeltung:
    return {
        AktStatus.SUSPENDIERT: ManifestGeltung.GESPERRT,
        AktStatus.RATIFIZIERT: ManifestGeltung.PROKLAMIERT,
        AktStatus.SOUVERAEN: ManifestGeltung.HOHEITSRECHT,
    }[klausel.akt_status]


def _manifest_weight(klausel: AktKlausel) -> float:
    bonus = {
        ManifestGeltung.GESPERRT: 0.0,
        ManifestGeltung.PROKLAMIERT: 0.04,
        ManifestGeltung.HOHEITSRECHT: 0.08,
    }[_geltung(klausel)]
    return round(min(1.0, klausel.sovereignty_weight + bonus), 3)


def _proclamation_rank(klausel: AktKlausel) -> int:
    return {
        ManifestGeltung.GESPERRT: klausel.enactment_tier,
        ManifestGeltung.PROKLAMIERT: klausel.enactment_tier + 1,
        ManifestGeltung.HOHEITSRECHT: klausel.enactment_tier + 2,
    }[_geltung(klausel)]


def build_ordnungs_manifest(
    souveraenitaets_akt: SouveraenitaetsAkt | None = None,
    *,
    manifest_id: str = "ordnungs-manifest",
) -> OrdnungsManifest:
    """Build the order manifest proclaiming Leitstern sovereignty clauses."""

    resolved_akt = (
        build_souveraenitaets_akt(akt_id=f"{manifest_id}-akt")
        if souveraenitaets_akt is None
        else souveraenitaets_akt
    )
    abschnitte = tuple(
        ManifestAbschnitt(
            abschnitt_id=f"{manifest_id}-{klausel.klausel_id.removeprefix(f'{resolved_akt.akt_id}-')}",
            sequence=index,
            klausel_id=klausel.klausel_id,
            artikel_id=klausel.artikel_id,
            mandat_id=klausel.mandat_id,
            fall_id=klausel.fall_id,
            line_id=klausel.line_id,
            article_id=klausel.article_id,
            entry_id=klausel.entry_id,
            section_id=klausel.section_id,
            reference_key=klausel.reference_key,
            akt_sektion=klausel.sektion,
            akt_status=klausel.akt_status,
            akt_prozedur=klausel.prozedur,
            kapitel=_kapitel(klausel),
            verfahren=_verfahren(klausel),
            geltung=_geltung(klausel),
            abschnitt_ids=klausel.klausel_ids,
            promulgated=klausel.operative and _geltung(klausel) is ManifestGeltung.HOHEITSRECHT,
            manifest_weight=_manifest_weight(klausel),
            proclamation_rank=_proclamation_rank(klausel),
            abschnitt_tags=tuple(
                dict.fromkeys(
                    (
                        *klausel.klausel_tags,
                        _kapitel(klausel).value,
                        _verfahren(klausel).value,
                        _geltung(klausel).value,
                    )
                )
            ),
            summary=(
                f"{klausel.klausel_id} proclaimed in {_kapitel(klausel).value} via "
                f"{_verfahren(klausel).value} with geltung {_geltung(klausel).value}."
            ),
        )
        for index, klausel in enumerate(resolved_akt.klauseln, start=1)
    )
    if not abschnitte:
        raise ValueError("ordnungs manifest requires at least one abschnitt")

    severity = "info"
    status = "manifest-hoheitsrecht"
    if any(a.geltung is ManifestGeltung.GESPERRT for a in abschnitte):
        severity = "critical"
        status = "manifest-gesperrt"
    elif any(a.geltung is ManifestGeltung.PROKLAMIERT for a in abschnitte):
        severity = "warning"
        status = "manifest-proklamiert"

    manifest_signal = TelemetrySignal(
        signal_name="ordnungs-manifest",
        boundary=resolved_akt.akt_signal.boundary,
        correlation_id=manifest_id,
        severity=severity,
        status=status,
        metrics={
            "abschnitt_count": float(len(abschnitte)),
            "gesperrt_count": float(sum(1 for a in abschnitte if a.geltung is ManifestGeltung.GESPERRT)),
            "proklamiert_count": float(sum(1 for a in abschnitte if a.geltung is ManifestGeltung.PROKLAMIERT)),
            "hoheitsrecht_count": float(sum(1 for a in abschnitte if a.geltung is ManifestGeltung.HOHEITSRECHT)),
            "promulgated_count": float(sum(1 for a in abschnitte if a.promulgated)),
            "avg_manifest_weight": round(sum(a.manifest_weight for a in abschnitte) / len(abschnitte), 3),
        },
        labels={"manifest_id": manifest_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_akt.final_snapshot.runtime_stage,
        signals=(manifest_signal, *resolved_akt.final_snapshot.signals),
        alerts=resolved_akt.final_snapshot.alerts,
        audit_entries=resolved_akt.final_snapshot.audit_entries,
        active_controls=resolved_akt.final_snapshot.active_controls,
    )
    return OrdnungsManifest(
        manifest_id=manifest_id,
        souveraenitaets_akt=resolved_akt,
        abschnitte=abschnitte,
        manifest_signal=manifest_signal,
        final_snapshot=final_snapshot,
    )
