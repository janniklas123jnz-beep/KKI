"""Supremats register encoding sovereign manifest norms as supreme Leitstern constitutional entries."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .hoheits_manifest import (
    HoheitsGeltung,
    HoheitsGrad,
    HoheitsManifest,
    HoheitsNorm,
    HoheitsProzedur,
    build_hoheits_manifest,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class SuprematsKlasse(str, Enum):
    """Supremacy class that classifies one register entry."""

    SCHUTZ_SUPREMAT = "schutz-supremat"
    ORDNUNGS_SUPREMAT = "ordnungs-supremat"
    SOUVERAENITAETS_SUPREMAT = "souveraenitaets-supremat"


class SuprematsProzedur(str, Enum):
    """Supremacy procedure used to register the entry."""

    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SuprematsGeltung(str, Enum):
    """Canonical validity of the supreme register entry."""

    GESPERRT = "gesperrt"
    SUPREMIERT = "supremiert"
    GRUNDLEGEND_SUPREMIERT = "grundlegend-supremiert"


@dataclass(frozen=True)
class SuprematsNorm:
    """One supreme register entry derived from a sovereign manifest norm."""

    supremats_norm_id: str
    sequence: int
    hoheits_norm_id: str
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
    hoheits_grad: HoheitsGrad
    hoheits_prozedur: HoheitsProzedur
    supremats_klasse: SuprematsKlasse
    prozedur: SuprematsProzedur
    geltung: SuprematsGeltung
    supremats_norm_ids: tuple[str, ...]
    canonical: bool
    supremats_weight: float
    supremats_tier: int
    supremats_norm_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "supremats_norm_id", _non_empty(self.supremats_norm_id, field_name="supremats_norm_id"))
        object.__setattr__(self, "hoheits_norm_id", _non_empty(self.hoheits_norm_id, field_name="hoheits_norm_id"))
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
        object.__setattr__(self, "supremats_weight", _clamp01(self.supremats_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.supremats_tier < 1:
            raise ValueError("supremats_tier must be positive")
        if not self.supremats_norm_ids:
            raise ValueError("supremats_norm_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "supremats_norm_id": self.supremats_norm_id,
            "sequence": self.sequence,
            "hoheits_norm_id": self.hoheits_norm_id,
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
            "hoheits_grad": self.hoheits_grad.value,
            "hoheits_prozedur": self.hoheits_prozedur.value,
            "supremats_klasse": self.supremats_klasse.value,
            "prozedur": self.prozedur.value,
            "geltung": self.geltung.value,
            "supremats_norm_ids": list(self.supremats_norm_ids),
            "canonical": self.canonical,
            "supremats_weight": self.supremats_weight,
            "supremats_tier": self.supremats_tier,
            "supremats_norm_tags": list(self.supremats_norm_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class SuprematsRegister:
    """Supremacy register encoding Leitstern sovereign norms as supreme constitutional entries."""

    register_id: str
    hoheits_manifest: HoheitsManifest
    normen: tuple[SuprematsNorm, ...]
    register_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "register_id", _non_empty(self.register_id, field_name="register_id"))

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.supremats_norm_id for n in self.normen if n.geltung is SuprematsGeltung.GESPERRT)

    @property
    def supremiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.supremats_norm_id for n in self.normen if n.geltung is SuprematsGeltung.SUPREMIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.supremats_norm_id for n in self.normen if n.geltung is SuprematsGeltung.GRUNDLEGEND_SUPREMIERT)

    def to_dict(self) -> dict[str, object]:
        return {
            "register_id": self.register_id,
            "hoheits_manifest": self.hoheits_manifest.to_dict(),
            "normen": [n.to_dict() for n in self.normen],
            "register_signal": self.register_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "gesperrt_norm_ids": list(self.gesperrt_norm_ids),
            "supremiert_norm_ids": list(self.supremiert_norm_ids),
            "grundlegend_norm_ids": list(self.grundlegend_norm_ids),
        }


def _supremats_klasse(norm: HoheitsNorm) -> SuprematsKlasse:
    return {
        HoheitsGrad.SCHUTZ_GRAD: SuprematsKlasse.SCHUTZ_SUPREMAT,
        HoheitsGrad.ORDNUNGS_GRAD: SuprematsKlasse.ORDNUNGS_SUPREMAT,
        HoheitsGrad.SOUVERAENITAETS_GRAD: SuprematsKlasse.SOUVERAENITAETS_SUPREMAT,
    }[norm.hoheits_grad]


def _supremats_prozedur(norm: HoheitsNorm) -> SuprematsProzedur:
    return {
        HoheitsProzedur.NOTPROZEDUR: SuprematsProzedur.NOTPROZEDUR,
        HoheitsProzedur.REGELPROTOKOLL: SuprematsProzedur.REGELPROTOKOLL,
        HoheitsProzedur.PLENARPROTOKOLL: SuprematsProzedur.PLENARPROTOKOLL,
    }[norm.prozedur]


def _geltung(norm: HoheitsNorm) -> SuprematsGeltung:
    return {
        HoheitsGeltung.GESPERRT: SuprematsGeltung.GESPERRT,
        HoheitsGeltung.PROKLAMIERT: SuprematsGeltung.SUPREMIERT,
        HoheitsGeltung.GRUNDLEGEND_PROKLAMIERT: SuprematsGeltung.GRUNDLEGEND_SUPREMIERT,
    }[norm.geltung]


def _supremats_weight(norm: HoheitsNorm) -> float:
    bonus = {
        SuprematsGeltung.GESPERRT: 0.0,
        SuprematsGeltung.SUPREMIERT: 0.04,
        SuprematsGeltung.GRUNDLEGEND_SUPREMIERT: 0.08,
    }[_geltung(norm)]
    return round(min(1.0, norm.hoheits_weight + bonus), 3)


def _supremats_tier(norm: HoheitsNorm) -> int:
    return {
        SuprematsGeltung.GESPERRT: norm.hoheits_tier,
        SuprematsGeltung.SUPREMIERT: norm.hoheits_tier + 1,
        SuprematsGeltung.GRUNDLEGEND_SUPREMIERT: norm.hoheits_tier + 2,
    }[_geltung(norm)]


def build_supremats_register(
    hoheits_manifest: HoheitsManifest | None = None,
    *,
    register_id: str = "supremats-register",
) -> SuprematsRegister:
    """Build the supremacy register encoding Leitstern sovereign manifest norms."""

    resolved_manifest = (
        build_hoheits_manifest(manifest_id=f"{register_id}-manifest")
        if hoheits_manifest is None
        else hoheits_manifest
    )
    normen = tuple(
        SuprematsNorm(
            supremats_norm_id=f"{register_id}-{n.hoheits_norm_id.removeprefix(f'{resolved_manifest.manifest_id}-')}",
            sequence=index,
            hoheits_norm_id=n.hoheits_norm_id,
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
            hoheits_grad=n.hoheits_grad,
            hoheits_prozedur=n.prozedur,
            supremats_klasse=_supremats_klasse(n),
            prozedur=_supremats_prozedur(n),
            geltung=_geltung(n),
            supremats_norm_ids=n.hoheits_norm_ids,
            canonical=n.canonical and _geltung(n) is SuprematsGeltung.GRUNDLEGEND_SUPREMIERT,
            supremats_weight=_supremats_weight(n),
            supremats_tier=_supremats_tier(n),
            supremats_norm_tags=tuple(
                dict.fromkeys(
                    (
                        *n.hoheits_norm_tags,
                        _supremats_klasse(n).value,
                        _supremats_prozedur(n).value,
                        _geltung(n).value,
                    )
                )
            ),
            summary=(
                f"{n.hoheits_norm_id} registered as {_supremats_klasse(n).value} via "
                f"{_supremats_prozedur(n).value} with geltung {_geltung(n).value}."
            ),
        )
        for index, n in enumerate(resolved_manifest.normen, start=1)
    )
    if not normen:
        raise ValueError("supremats register requires at least one norm")

    severity = "info"
    status = "register-grundlegend-supremiert"
    if any(n.geltung is SuprematsGeltung.GESPERRT for n in normen):
        severity = "critical"
        status = "register-gesperrt"
    elif any(n.geltung is SuprematsGeltung.SUPREMIERT for n in normen):
        severity = "warning"
        status = "register-supremiert"

    register_signal = TelemetrySignal(
        signal_name="supremats-register",
        boundary=resolved_manifest.manifest_signal.boundary,
        correlation_id=register_id,
        severity=severity,
        status=status,
        metrics={
            "norm_count": float(len(normen)),
            "gesperrt_count": float(sum(1 for n in normen if n.geltung is SuprematsGeltung.GESPERRT)),
            "supremiert_count": float(sum(1 for n in normen if n.geltung is SuprematsGeltung.SUPREMIERT)),
            "grundlegend_count": float(sum(1 for n in normen if n.geltung is SuprematsGeltung.GRUNDLEGEND_SUPREMIERT)),
            "canonical_count": float(sum(1 for n in normen if n.canonical)),
            "avg_supremats_weight": round(sum(n.supremats_weight for n in normen) / len(normen), 3),
        },
        labels={"register_id": register_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_manifest.final_snapshot.runtime_stage,
        signals=(register_signal, *resolved_manifest.final_snapshot.signals),
        alerts=resolved_manifest.final_snapshot.alerts,
        audit_entries=resolved_manifest.final_snapshot.audit_entries,
        active_controls=resolved_manifest.final_snapshot.active_controls,
    )
    return SuprematsRegister(
        register_id=register_id,
        hoheits_manifest=resolved_manifest,
        normen=normen,
        register_signal=register_signal,
        final_snapshot=final_snapshot,
    )
