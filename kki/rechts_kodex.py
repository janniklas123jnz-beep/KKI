"""Rechts kodex encoding state norms as systematically codified Leitstern legal norms."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .staats_ordnung import (
    StaatsEbene,
    StaatsGeltung,
    StaatsNorm,
    StaatsOrdnung,
    StaatsProzedur,
    build_staats_ordnung,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class KodexKlasse(str, Enum):
    """Codex class that systematises one legal norm."""

    SCHUTZ_KLASSE = "schutz-klasse"
    ORDNUNGS_KLASSE = "ordnungs-klasse"
    SOUVERAENITAETS_KLASSE = "souveraenitaets-klasse"


class KodexProzedur(str, Enum):
    """Codification procedure used to encode the norm."""

    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KodexStatus(str, Enum):
    """Canonical status of the encoded legal norm."""

    GESPERRT = "gesperrt"
    KODIERT = "kodiert"
    GRUNDLEGEND_KODIERT = "grundlegend-kodiert"


@dataclass(frozen=True)
class KodexNorm:
    """One codified legal norm derived from a state norm."""

    kodex_norm_id: str
    sequence: int
    norm_id: str
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
    staats_ebene: StaatsEbene
    staats_prozedur: StaatsProzedur
    klasse: KodexKlasse
    prozedur: KodexProzedur
    status: KodexStatus
    kodex_norm_ids: tuple[str, ...]
    canonical: bool
    kodex_weight: float
    kodex_tier: int
    kodex_norm_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "kodex_norm_id", _non_empty(self.kodex_norm_id, field_name="kodex_norm_id"))
        object.__setattr__(self, "norm_id", _non_empty(self.norm_id, field_name="norm_id"))
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
        object.__setattr__(self, "kodex_weight", _clamp01(self.kodex_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.kodex_tier < 1:
            raise ValueError("kodex_tier must be positive")
        if not self.kodex_norm_ids:
            raise ValueError("kodex_norm_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "kodex_norm_id": self.kodex_norm_id,
            "sequence": self.sequence,
            "norm_id": self.norm_id,
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
            "staats_ebene": self.staats_ebene.value,
            "staats_prozedur": self.staats_prozedur.value,
            "klasse": self.klasse.value,
            "prozedur": self.prozedur.value,
            "status": self.status.value,
            "kodex_norm_ids": list(self.kodex_norm_ids),
            "canonical": self.canonical,
            "kodex_weight": self.kodex_weight,
            "kodex_tier": self.kodex_tier,
            "kodex_norm_tags": list(self.kodex_norm_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class RechtsKodex:
    """Legal codex encoding Leitstern state norms as systematically codified law."""

    kodex_id: str
    staats_ordnung: StaatsOrdnung
    normen: tuple[KodexNorm, ...]
    kodex_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "kodex_id", _non_empty(self.kodex_id, field_name="kodex_id"))

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kodex_norm_id for n in self.normen if n.status is KodexStatus.GESPERRT)

    @property
    def kodiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kodex_norm_id for n in self.normen if n.status is KodexStatus.KODIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kodex_norm_id for n in self.normen if n.status is KodexStatus.GRUNDLEGEND_KODIERT)

    def to_dict(self) -> dict[str, object]:
        return {
            "kodex_id": self.kodex_id,
            "staats_ordnung": self.staats_ordnung.to_dict(),
            "normen": [n.to_dict() for n in self.normen],
            "kodex_signal": self.kodex_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "gesperrt_norm_ids": list(self.gesperrt_norm_ids),
            "kodiert_norm_ids": list(self.kodiert_norm_ids),
            "grundlegend_norm_ids": list(self.grundlegend_norm_ids),
        }


def _klasse(norm: StaatsNorm) -> KodexKlasse:
    return {
        StaatsEbene.SCHUTZ_EBENE: KodexKlasse.SCHUTZ_KLASSE,
        StaatsEbene.ORDNUNGS_EBENE: KodexKlasse.ORDNUNGS_KLASSE,
        StaatsEbene.SOUVERAENITAETS_EBENE: KodexKlasse.SOUVERAENITAETS_KLASSE,
    }[norm.ebene]


def _prozedur(norm: StaatsNorm) -> KodexProzedur:
    return {
        StaatsProzedur.NOTPROZEDUR: KodexProzedur.NOTPROZEDUR,
        StaatsProzedur.REGELPROTOKOLL: KodexProzedur.REGELPROTOKOLL,
        StaatsProzedur.PLENARPROTOKOLL: KodexProzedur.PLENARPROTOKOLL,
    }[norm.prozedur]


def _status(norm: StaatsNorm) -> KodexStatus:
    return {
        StaatsGeltung.GESPERRT: KodexStatus.GESPERRT,
        StaatsGeltung.GEORDNET: KodexStatus.KODIERT,
        StaatsGeltung.GRUNDLEGEND_GEORDNET: KodexStatus.GRUNDLEGEND_KODIERT,
    }[norm.geltung]


def _kodex_weight(norm: StaatsNorm) -> float:
    bonus = {
        KodexStatus.GESPERRT: 0.0,
        KodexStatus.KODIERT: 0.04,
        KodexStatus.GRUNDLEGEND_KODIERT: 0.08,
    }[_status(norm)]
    return round(min(1.0, norm.staats_weight + bonus), 3)


def _kodex_tier(norm: StaatsNorm) -> int:
    return {
        KodexStatus.GESPERRT: norm.staats_tier,
        KodexStatus.KODIERT: norm.staats_tier + 1,
        KodexStatus.GRUNDLEGEND_KODIERT: norm.staats_tier + 2,
    }[_status(norm)]


def build_rechts_kodex(
    staats_ordnung: StaatsOrdnung | None = None,
    *,
    kodex_id: str = "rechts-kodex",
) -> RechtsKodex:
    """Build the legal codex encoding Leitstern state norms."""

    resolved_ordnung = (
        build_staats_ordnung(ordnung_id=f"{kodex_id}-ordnung")
        if staats_ordnung is None
        else staats_ordnung
    )
    normen = tuple(
        KodexNorm(
            kodex_norm_id=f"{kodex_id}-{n.norm_id.removeprefix(f'{resolved_ordnung.ordnung_id}-')}",
            sequence=index,
            norm_id=n.norm_id,
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
            staats_ebene=n.ebene,
            staats_prozedur=n.prozedur,
            klasse=_klasse(n),
            prozedur=_prozedur(n),
            status=_status(n),
            kodex_norm_ids=n.norm_ids,
            canonical=n.canonical and _status(n) is KodexStatus.GRUNDLEGEND_KODIERT,
            kodex_weight=_kodex_weight(n),
            kodex_tier=_kodex_tier(n),
            kodex_norm_tags=tuple(
                dict.fromkeys(
                    (
                        *n.norm_tags,
                        _klasse(n).value,
                        _prozedur(n).value,
                        _status(n).value,
                    )
                )
            ),
            summary=(
                f"{n.norm_id} codified as {_klasse(n).value} via "
                f"{_prozedur(n).value} with status {_status(n).value}."
            ),
        )
        for index, n in enumerate(resolved_ordnung.normen, start=1)
    )
    if not normen:
        raise ValueError("rechts kodex requires at least one norm")

    severity = "info"
    status = "kodex-grundlegend-kodiert"
    if any(n.status is KodexStatus.GESPERRT for n in normen):
        severity = "critical"
        status = "kodex-gesperrt"
    elif any(n.status is KodexStatus.KODIERT for n in normen):
        severity = "warning"
        status = "kodex-kodiert"

    kodex_signal = TelemetrySignal(
        signal_name="rechts-kodex",
        boundary=resolved_ordnung.staats_signal.boundary,
        correlation_id=kodex_id,
        severity=severity,
        status=status,
        metrics={
            "norm_count": float(len(normen)),
            "gesperrt_count": float(sum(1 for n in normen if n.status is KodexStatus.GESPERRT)),
            "kodiert_count": float(sum(1 for n in normen if n.status is KodexStatus.KODIERT)),
            "grundlegend_count": float(sum(1 for n in normen if n.status is KodexStatus.GRUNDLEGEND_KODIERT)),
            "canonical_count": float(sum(1 for n in normen if n.canonical)),
            "avg_kodex_weight": round(sum(n.kodex_weight for n in normen) / len(normen), 3),
        },
        labels={"kodex_id": kodex_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_ordnung.final_snapshot.runtime_stage,
        signals=(kodex_signal, *resolved_ordnung.final_snapshot.signals),
        alerts=resolved_ordnung.final_snapshot.alerts,
        audit_entries=resolved_ordnung.final_snapshot.audit_entries,
        active_controls=resolved_ordnung.final_snapshot.active_controls,
    )
    return RechtsKodex(
        kodex_id=kodex_id,
        staats_ordnung=resolved_ordnung,
        normen=normen,
        kodex_signal=kodex_signal,
        final_snapshot=final_snapshot,
    )
