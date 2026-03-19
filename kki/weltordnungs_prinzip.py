"""Weltordnungs prinzip encoding constitutional codex norms as world-order principles for Leitstern."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .verfassungs_kodex import (
    VerfassungsKodex,
    VerfassungsKodexGeltung,
    VerfassungsKodexNorm,
    VerfassungsKodexProzedur,
    VerfassungsKodexRang,
    build_verfassungs_kodex,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class WeltordnungsEbene(str, Enum):
    """World-order tier that classifies one principle norm."""

    SCHUTZ_ORDNUNG = "schutz-ordnung"
    ORDNUNGS_ORDNUNG = "ordnungs-ordnung"
    SOUVERAENITAETS_ORDNUNG = "souveraenitaets-ordnung"


class WeltordnungsProzedur(str, Enum):
    """World-order procedure used to establish the principle."""

    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class WeltordnungsGeltung(str, Enum):
    """Canonical validity of the world-order principle norm."""

    GESPERRT = "gesperrt"
    GEORDNET = "geordnet"
    GRUNDLEGEND_GEORDNET = "grundlegend-geordnet"


@dataclass(frozen=True)
class WeltordnungsNorm:
    """One world-order principle norm derived from a constitutional codex article."""

    weltordnungs_norm_id: str
    sequence: int
    verfassungs_kodex_norm_id: str
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
    kodex_rang: VerfassungsKodexRang
    kodex_prozedur: VerfassungsKodexProzedur
    weltordnungs_ebene: WeltordnungsEbene
    prozedur: WeltordnungsProzedur
    geltung: WeltordnungsGeltung
    weltordnungs_norm_ids: tuple[str, ...]
    canonical: bool
    weltordnungs_weight: float
    weltordnungs_tier: int
    weltordnungs_norm_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "weltordnungs_norm_id", _non_empty(self.weltordnungs_norm_id, field_name="weltordnungs_norm_id"))
        object.__setattr__(self, "verfassungs_kodex_norm_id", _non_empty(self.verfassungs_kodex_norm_id, field_name="verfassungs_kodex_norm_id"))
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
        object.__setattr__(self, "weltordnungs_weight", _clamp01(self.weltordnungs_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.weltordnungs_tier < 1:
            raise ValueError("weltordnungs_tier must be positive")
        if not self.weltordnungs_norm_ids:
            raise ValueError("weltordnungs_norm_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "weltordnungs_norm_id": self.weltordnungs_norm_id,
            "sequence": self.sequence,
            "verfassungs_kodex_norm_id": self.verfassungs_kodex_norm_id,
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
            "kodex_rang": self.kodex_rang.value,
            "kodex_prozedur": self.kodex_prozedur.value,
            "weltordnungs_ebene": self.weltordnungs_ebene.value,
            "prozedur": self.prozedur.value,
            "geltung": self.geltung.value,
            "weltordnungs_norm_ids": list(self.weltordnungs_norm_ids),
            "canonical": self.canonical,
            "weltordnungs_weight": self.weltordnungs_weight,
            "weltordnungs_tier": self.weltordnungs_tier,
            "weltordnungs_norm_tags": list(self.weltordnungs_norm_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class WeltordnungsPrinzip:
    """World-order principle encoding Leitstern constitutional norms as universal ordering mandates."""

    prinzip_id: str
    verfassungs_kodex: VerfassungsKodex
    normen: tuple[WeltordnungsNorm, ...]
    prinzip_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "prinzip_id", _non_empty(self.prinzip_id, field_name="prinzip_id"))

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.weltordnungs_norm_id for n in self.normen if n.geltung is WeltordnungsGeltung.GESPERRT)

    @property
    def geordnet_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.weltordnungs_norm_id for n in self.normen if n.geltung is WeltordnungsGeltung.GEORDNET)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.weltordnungs_norm_id for n in self.normen if n.geltung is WeltordnungsGeltung.GRUNDLEGEND_GEORDNET)

    def to_dict(self) -> dict[str, object]:
        return {
            "prinzip_id": self.prinzip_id,
            "verfassungs_kodex": self.verfassungs_kodex.to_dict(),
            "normen": [n.to_dict() for n in self.normen],
            "prinzip_signal": self.prinzip_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "gesperrt_norm_ids": list(self.gesperrt_norm_ids),
            "geordnet_norm_ids": list(self.geordnet_norm_ids),
            "grundlegend_norm_ids": list(self.grundlegend_norm_ids),
        }


def _weltordnungs_ebene(norm: VerfassungsKodexNorm) -> WeltordnungsEbene:
    return {
        VerfassungsKodexRang.SCHUTZ_KODEX: WeltordnungsEbene.SCHUTZ_ORDNUNG,
        VerfassungsKodexRang.ORDNUNGS_KODEX: WeltordnungsEbene.ORDNUNGS_ORDNUNG,
        VerfassungsKodexRang.SOUVERAENITAETS_KODEX: WeltordnungsEbene.SOUVERAENITAETS_ORDNUNG,
    }[norm.kodex_rang]


def _weltordnungs_prozedur(norm: VerfassungsKodexNorm) -> WeltordnungsProzedur:
    return {
        VerfassungsKodexProzedur.NOTPROZEDUR: WeltordnungsProzedur.NOTPROZEDUR,
        VerfassungsKodexProzedur.REGELPROTOKOLL: WeltordnungsProzedur.REGELPROTOKOLL,
        VerfassungsKodexProzedur.PLENARPROTOKOLL: WeltordnungsProzedur.PLENARPROTOKOLL,
    }[norm.prozedur]


def _geltung(norm: VerfassungsKodexNorm) -> WeltordnungsGeltung:
    return {
        VerfassungsKodexGeltung.GESPERRT: WeltordnungsGeltung.GESPERRT,
        VerfassungsKodexGeltung.KODIFIZIERT: WeltordnungsGeltung.GEORDNET,
        VerfassungsKodexGeltung.GRUNDLEGEND_KODIFIZIERT: WeltordnungsGeltung.GRUNDLEGEND_GEORDNET,
    }[norm.geltung]


def _weltordnungs_weight(norm: VerfassungsKodexNorm) -> float:
    bonus = {
        WeltordnungsGeltung.GESPERRT: 0.0,
        WeltordnungsGeltung.GEORDNET: 0.04,
        WeltordnungsGeltung.GRUNDLEGEND_GEORDNET: 0.08,
    }[_geltung(norm)]
    return round(min(1.0, norm.kodex_weight + bonus), 3)


def _weltordnungs_tier(norm: VerfassungsKodexNorm) -> int:
    return {
        WeltordnungsGeltung.GESPERRT: norm.kodex_tier,
        WeltordnungsGeltung.GEORDNET: norm.kodex_tier + 1,
        WeltordnungsGeltung.GRUNDLEGEND_GEORDNET: norm.kodex_tier + 2,
    }[_geltung(norm)]


def build_weltordnungs_prinzip(
    verfassungs_kodex: VerfassungsKodex | None = None,
    *,
    prinzip_id: str = "weltordnungs-prinzip",
) -> WeltordnungsPrinzip:
    """Build the world-order principle encoding Leitstern constitutional norms."""

    resolved_kodex = (
        build_verfassungs_kodex(kodex_id=f"{prinzip_id}-kodex")
        if verfassungs_kodex is None
        else verfassungs_kodex
    )
    normen = tuple(
        WeltordnungsNorm(
            weltordnungs_norm_id=f"{prinzip_id}-{n.verfassungs_kodex_norm_id.removeprefix(f'{resolved_kodex.kodex_id}-')}",
            sequence=index,
            verfassungs_kodex_norm_id=n.verfassungs_kodex_norm_id,
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
            kodex_rang=n.kodex_rang,
            kodex_prozedur=n.prozedur,
            weltordnungs_ebene=_weltordnungs_ebene(n),
            prozedur=_weltordnungs_prozedur(n),
            geltung=_geltung(n),
            weltordnungs_norm_ids=n.verfassungs_kodex_norm_ids,
            canonical=n.canonical and _geltung(n) is WeltordnungsGeltung.GRUNDLEGEND_GEORDNET,
            weltordnungs_weight=_weltordnungs_weight(n),
            weltordnungs_tier=_weltordnungs_tier(n),
            weltordnungs_norm_tags=tuple(
                dict.fromkeys(
                    (
                        *n.verfassungs_kodex_norm_tags,
                        _weltordnungs_ebene(n).value,
                        _weltordnungs_prozedur(n).value,
                        _geltung(n).value,
                    )
                )
            ),
            summary=(
                f"{n.verfassungs_kodex_norm_id} ordered as {_weltordnungs_ebene(n).value} via "
                f"{_weltordnungs_prozedur(n).value} with geltung {_geltung(n).value}."
            ),
        )
        for index, n in enumerate(resolved_kodex.normen, start=1)
    )
    if not normen:
        raise ValueError("weltordnungs prinzip requires at least one norm")

    severity = "info"
    status = "prinzip-grundlegend-geordnet"
    if any(n.geltung is WeltordnungsGeltung.GESPERRT for n in normen):
        severity = "critical"
        status = "prinzip-gesperrt"
    elif any(n.geltung is WeltordnungsGeltung.GEORDNET for n in normen):
        severity = "warning"
        status = "prinzip-geordnet"

    prinzip_signal = TelemetrySignal(
        signal_name="weltordnungs-prinzip",
        boundary=resolved_kodex.kodex_signal.boundary,
        correlation_id=prinzip_id,
        severity=severity,
        status=status,
        metrics={
            "norm_count": float(len(normen)),
            "gesperrt_count": float(sum(1 for n in normen if n.geltung is WeltordnungsGeltung.GESPERRT)),
            "geordnet_count": float(sum(1 for n in normen if n.geltung is WeltordnungsGeltung.GEORDNET)),
            "grundlegend_count": float(sum(1 for n in normen if n.geltung is WeltordnungsGeltung.GRUNDLEGEND_GEORDNET)),
            "canonical_count": float(sum(1 for n in normen if n.canonical)),
            "avg_weltordnungs_weight": round(sum(n.weltordnungs_weight for n in normen) / len(normen), 3),
        },
        labels={"prinzip_id": prinzip_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_kodex.final_snapshot.runtime_stage,
        signals=(prinzip_signal, *resolved_kodex.final_snapshot.signals),
        alerts=resolved_kodex.final_snapshot.alerts,
        audit_entries=resolved_kodex.final_snapshot.audit_entries,
        active_controls=resolved_kodex.final_snapshot.active_controls,
    )
    return WeltordnungsPrinzip(
        prinzip_id=prinzip_id,
        verfassungs_kodex=resolved_kodex,
        normen=normen,
        prinzip_signal=prinzip_signal,
        final_snapshot=final_snapshot,
    )
