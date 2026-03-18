"""Hoheits manifest encoding chartered federal norms as proclaimed Leitstern sovereign mandates."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bundes_charta import (
    BundesCharta,
    BundesGeltung,
    BundesNorm,
    BundesProzedur,
    BundesRang,
    build_bundes_charta,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class HoheitsGrad(str, Enum):
    """Sovereign grade that classifies one manifest norm."""

    SCHUTZ_GRAD = "schutz-grad"
    ORDNUNGS_GRAD = "ordnungs-grad"
    SOUVERAENITAETS_GRAD = "souveraenitaets-grad"


class HoheitsProzedur(str, Enum):
    """Sovereign procedure used to proclaim the manifest."""

    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class HoheitsGeltung(str, Enum):
    """Canonical validity of the proclaimed sovereign norm."""

    GESPERRT = "gesperrt"
    PROKLAMIERT = "proklamiert"
    GRUNDLEGEND_PROKLAMIERT = "grundlegend-proklamiert"


@dataclass(frozen=True)
class HoheitsNorm:
    """One sovereign manifest norm derived from a chartered federal norm."""

    hoheits_norm_id: str
    sequence: int
    bundes_norm_id: str
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
    bundes_rang: BundesRang
    bundes_prozedur: BundesProzedur
    hoheits_grad: HoheitsGrad
    prozedur: HoheitsProzedur
    geltung: HoheitsGeltung
    hoheits_norm_ids: tuple[str, ...]
    canonical: bool
    hoheits_weight: float
    hoheits_tier: int
    hoheits_norm_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "hoheits_norm_id", _non_empty(self.hoheits_norm_id, field_name="hoheits_norm_id"))
        object.__setattr__(self, "bundes_norm_id", _non_empty(self.bundes_norm_id, field_name="bundes_norm_id"))
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
        object.__setattr__(self, "hoheits_weight", _clamp01(self.hoheits_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.hoheits_tier < 1:
            raise ValueError("hoheits_tier must be positive")
        if not self.hoheits_norm_ids:
            raise ValueError("hoheits_norm_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "hoheits_norm_id": self.hoheits_norm_id,
            "sequence": self.sequence,
            "bundes_norm_id": self.bundes_norm_id,
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
            "bundes_rang": self.bundes_rang.value,
            "bundes_prozedur": self.bundes_prozedur.value,
            "hoheits_grad": self.hoheits_grad.value,
            "prozedur": self.prozedur.value,
            "geltung": self.geltung.value,
            "hoheits_norm_ids": list(self.hoheits_norm_ids),
            "canonical": self.canonical,
            "hoheits_weight": self.hoheits_weight,
            "hoheits_tier": self.hoheits_tier,
            "hoheits_norm_tags": list(self.hoheits_norm_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class HoheitsManifest:
    """Sovereign manifest encoding Leitstern federal norms as proclaimed constitutional mandates."""

    manifest_id: str
    bundes_charta: BundesCharta
    normen: tuple[HoheitsNorm, ...]
    manifest_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "manifest_id", _non_empty(self.manifest_id, field_name="manifest_id"))

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.hoheits_norm_id for n in self.normen if n.geltung is HoheitsGeltung.GESPERRT)

    @property
    def proklamiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.hoheits_norm_id for n in self.normen if n.geltung is HoheitsGeltung.PROKLAMIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.hoheits_norm_id for n in self.normen if n.geltung is HoheitsGeltung.GRUNDLEGEND_PROKLAMIERT)

    def to_dict(self) -> dict[str, object]:
        return {
            "manifest_id": self.manifest_id,
            "bundes_charta": self.bundes_charta.to_dict(),
            "normen": [n.to_dict() for n in self.normen],
            "manifest_signal": self.manifest_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "gesperrt_norm_ids": list(self.gesperrt_norm_ids),
            "proklamiert_norm_ids": list(self.proklamiert_norm_ids),
            "grundlegend_norm_ids": list(self.grundlegend_norm_ids),
        }


def _hoheits_grad(norm: BundesNorm) -> HoheitsGrad:
    return {
        BundesRang.SCHUTZ_RANG: HoheitsGrad.SCHUTZ_GRAD,
        BundesRang.ORDNUNGS_RANG: HoheitsGrad.ORDNUNGS_GRAD,
        BundesRang.SOUVERAENITAETS_RANG: HoheitsGrad.SOUVERAENITAETS_GRAD,
    }[norm.bundes_rang]


def _hoheits_prozedur(norm: BundesNorm) -> HoheitsProzedur:
    return {
        BundesProzedur.NOTPROZEDUR: HoheitsProzedur.NOTPROZEDUR,
        BundesProzedur.REGELPROTOKOLL: HoheitsProzedur.REGELPROTOKOLL,
        BundesProzedur.PLENARPROTOKOLL: HoheitsProzedur.PLENARPROTOKOLL,
    }[norm.prozedur]


def _geltung(norm: BundesNorm) -> HoheitsGeltung:
    return {
        BundesGeltung.GESPERRT: HoheitsGeltung.GESPERRT,
        BundesGeltung.VERBUERGT: HoheitsGeltung.PROKLAMIERT,
        BundesGeltung.GRUNDLEGEND_VERBUERGT: HoheitsGeltung.GRUNDLEGEND_PROKLAMIERT,
    }[norm.geltung]


def _hoheits_weight(norm: BundesNorm) -> float:
    bonus = {
        HoheitsGeltung.GESPERRT: 0.0,
        HoheitsGeltung.PROKLAMIERT: 0.04,
        HoheitsGeltung.GRUNDLEGEND_PROKLAMIERT: 0.08,
    }[_geltung(norm)]
    return round(min(1.0, norm.bundes_weight + bonus), 3)


def _hoheits_tier(norm: BundesNorm) -> int:
    return {
        HoheitsGeltung.GESPERRT: norm.bundes_tier,
        HoheitsGeltung.PROKLAMIERT: norm.bundes_tier + 1,
        HoheitsGeltung.GRUNDLEGEND_PROKLAMIERT: norm.bundes_tier + 2,
    }[_geltung(norm)]


def build_hoheits_manifest(
    bundes_charta: BundesCharta | None = None,
    *,
    manifest_id: str = "hoheits-manifest",
) -> HoheitsManifest:
    """Build the sovereign manifest encoding Leitstern federal norms."""

    resolved_charta = (
        build_bundes_charta(charta_id=f"{manifest_id}-charta")
        if bundes_charta is None
        else bundes_charta
    )
    normen = tuple(
        HoheitsNorm(
            hoheits_norm_id=f"{manifest_id}-{n.bundes_norm_id.removeprefix(f'{resolved_charta.charta_id}-')}",
            sequence=index,
            bundes_norm_id=n.bundes_norm_id,
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
            bundes_rang=n.bundes_rang,
            bundes_prozedur=n.prozedur,
            hoheits_grad=_hoheits_grad(n),
            prozedur=_hoheits_prozedur(n),
            geltung=_geltung(n),
            hoheits_norm_ids=n.bundes_norm_ids,
            canonical=n.canonical and _geltung(n) is HoheitsGeltung.GRUNDLEGEND_PROKLAMIERT,
            hoheits_weight=_hoheits_weight(n),
            hoheits_tier=_hoheits_tier(n),
            hoheits_norm_tags=tuple(
                dict.fromkeys(
                    (
                        *n.bundes_norm_tags,
                        _hoheits_grad(n).value,
                        _hoheits_prozedur(n).value,
                        _geltung(n).value,
                    )
                )
            ),
            summary=(
                f"{n.bundes_norm_id} proclaimed as {_hoheits_grad(n).value} via "
                f"{_hoheits_prozedur(n).value} with geltung {_geltung(n).value}."
            ),
        )
        for index, n in enumerate(resolved_charta.normen, start=1)
    )
    if not normen:
        raise ValueError("hoheits manifest requires at least one norm")

    severity = "info"
    status = "manifest-grundlegend-proklamiert"
    if any(n.geltung is HoheitsGeltung.GESPERRT for n in normen):
        severity = "critical"
        status = "manifest-gesperrt"
    elif any(n.geltung is HoheitsGeltung.PROKLAMIERT for n in normen):
        severity = "warning"
        status = "manifest-proklamiert"

    manifest_signal = TelemetrySignal(
        signal_name="hoheits-manifest",
        boundary=resolved_charta.charta_signal.boundary,
        correlation_id=manifest_id,
        severity=severity,
        status=status,
        metrics={
            "norm_count": float(len(normen)),
            "gesperrt_count": float(sum(1 for n in normen if n.geltung is HoheitsGeltung.GESPERRT)),
            "proklamiert_count": float(sum(1 for n in normen if n.geltung is HoheitsGeltung.PROKLAMIERT)),
            "grundlegend_count": float(sum(1 for n in normen if n.geltung is HoheitsGeltung.GRUNDLEGEND_PROKLAMIERT)),
            "canonical_count": float(sum(1 for n in normen if n.canonical)),
            "avg_hoheits_weight": round(sum(n.hoheits_weight for n in normen) / len(normen), 3),
        },
        labels={"manifest_id": manifest_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_charta.final_snapshot.runtime_stage,
        signals=(manifest_signal, *resolved_charta.final_snapshot.signals),
        alerts=resolved_charta.final_snapshot.alerts,
        audit_entries=resolved_charta.final_snapshot.audit_entries,
        active_controls=resolved_charta.final_snapshot.active_controls,
    )
    return HoheitsManifest(
        manifest_id=manifest_id,
        bundes_charta=resolved_charta,
        normen=normen,
        manifest_signal=manifest_signal,
        final_snapshot=final_snapshot,
    )
