"""Verfassungs kodex encoding senate resolutions as the supreme codified Leitstern constitutional law."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .grundrechts_senat import (
    GrundrechtsSenat,
    SenatGeltung,
    SenatNorm,
    SenatProzedur,
    SenatRang,
    build_grundrechts_senat,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class VerfassungsKodexRang(str, Enum):
    """Constitutional codex rank that classifies one supreme article."""

    SCHUTZ_KODEX = "schutz-kodex"
    ORDNUNGS_KODEX = "ordnungs-kodex"
    SOUVERAENITAETS_KODEX = "souveraenitaets-kodex"


class VerfassungsKodexProzedur(str, Enum):
    """Constitutional codex procedure used to codify the article."""

    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class VerfassungsKodexGeltung(str, Enum):
    """Canonical validity of the supreme codified constitutional article."""

    GESPERRT = "gesperrt"
    KODIFIZIERT = "kodifiziert"
    GRUNDLEGEND_KODIFIZIERT = "grundlegend-kodifiziert"


@dataclass(frozen=True)
class VerfassungsKodexNorm:
    """One supreme constitutional article derived from a fundamental rights senate norm."""

    verfassungs_kodex_norm_id: str
    sequence: int
    senat_norm_id: str
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
    senat_rang: SenatRang
    senat_prozedur: SenatProzedur
    kodex_rang: VerfassungsKodexRang
    prozedur: VerfassungsKodexProzedur
    geltung: VerfassungsKodexGeltung
    verfassungs_kodex_norm_ids: tuple[str, ...]
    canonical: bool
    kodex_weight: float
    kodex_tier: int
    verfassungs_kodex_norm_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "verfassungs_kodex_norm_id", _non_empty(self.verfassungs_kodex_norm_id, field_name="verfassungs_kodex_norm_id"))
        object.__setattr__(self, "senat_norm_id", _non_empty(self.senat_norm_id, field_name="senat_norm_id"))
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
        if not self.verfassungs_kodex_norm_ids:
            raise ValueError("verfassungs_kodex_norm_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "verfassungs_kodex_norm_id": self.verfassungs_kodex_norm_id,
            "sequence": self.sequence,
            "senat_norm_id": self.senat_norm_id,
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
            "senat_rang": self.senat_rang.value,
            "senat_prozedur": self.senat_prozedur.value,
            "kodex_rang": self.kodex_rang.value,
            "prozedur": self.prozedur.value,
            "geltung": self.geltung.value,
            "verfassungs_kodex_norm_ids": list(self.verfassungs_kodex_norm_ids),
            "canonical": self.canonical,
            "kodex_weight": self.kodex_weight,
            "kodex_tier": self.kodex_tier,
            "verfassungs_kodex_norm_tags": list(self.verfassungs_kodex_norm_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class VerfassungsKodex:
    """Supreme constitutional codex — the final codified crown of Leitstern's constitutional order."""

    kodex_id: str
    grundrechts_senat: GrundrechtsSenat
    normen: tuple[VerfassungsKodexNorm, ...]
    kodex_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "kodex_id", _non_empty(self.kodex_id, field_name="kodex_id"))

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.verfassungs_kodex_norm_id for n in self.normen if n.geltung is VerfassungsKodexGeltung.GESPERRT)

    @property
    def kodifiziert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.verfassungs_kodex_norm_id for n in self.normen if n.geltung is VerfassungsKodexGeltung.KODIFIZIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.verfassungs_kodex_norm_id for n in self.normen if n.geltung is VerfassungsKodexGeltung.GRUNDLEGEND_KODIFIZIERT)

    def to_dict(self) -> dict[str, object]:
        return {
            "kodex_id": self.kodex_id,
            "grundrechts_senat": self.grundrechts_senat.to_dict(),
            "normen": [n.to_dict() for n in self.normen],
            "kodex_signal": self.kodex_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "gesperrt_norm_ids": list(self.gesperrt_norm_ids),
            "kodifiziert_norm_ids": list(self.kodifiziert_norm_ids),
            "grundlegend_norm_ids": list(self.grundlegend_norm_ids),
        }


def _kodex_rang(norm: SenatNorm) -> VerfassungsKodexRang:
    return {
        SenatRang.SCHUTZ_SENAT: VerfassungsKodexRang.SCHUTZ_KODEX,
        SenatRang.ORDNUNGS_SENAT: VerfassungsKodexRang.ORDNUNGS_KODEX,
        SenatRang.SOUVERAENITAETS_SENAT: VerfassungsKodexRang.SOUVERAENITAETS_KODEX,
    }[norm.senat_rang]


def _kodex_prozedur(norm: SenatNorm) -> VerfassungsKodexProzedur:
    return {
        SenatProzedur.NOTPROZEDUR: VerfassungsKodexProzedur.NOTPROZEDUR,
        SenatProzedur.REGELPROTOKOLL: VerfassungsKodexProzedur.REGELPROTOKOLL,
        SenatProzedur.PLENARPROTOKOLL: VerfassungsKodexProzedur.PLENARPROTOKOLL,
    }[norm.prozedur]


def _geltung(norm: SenatNorm) -> VerfassungsKodexGeltung:
    return {
        SenatGeltung.GESPERRT: VerfassungsKodexGeltung.GESPERRT,
        SenatGeltung.BESCHLOSSEN: VerfassungsKodexGeltung.KODIFIZIERT,
        SenatGeltung.GRUNDLEGEND_BESCHLOSSEN: VerfassungsKodexGeltung.GRUNDLEGEND_KODIFIZIERT,
    }[norm.geltung]


def _kodex_weight(norm: SenatNorm) -> float:
    bonus = {
        VerfassungsKodexGeltung.GESPERRT: 0.0,
        VerfassungsKodexGeltung.KODIFIZIERT: 0.04,
        VerfassungsKodexGeltung.GRUNDLEGEND_KODIFIZIERT: 0.08,
    }[_geltung(norm)]
    return round(min(1.0, norm.senat_weight + bonus), 3)


def _kodex_tier(norm: SenatNorm) -> int:
    return {
        VerfassungsKodexGeltung.GESPERRT: norm.senat_tier,
        VerfassungsKodexGeltung.KODIFIZIERT: norm.senat_tier + 1,
        VerfassungsKodexGeltung.GRUNDLEGEND_KODIFIZIERT: norm.senat_tier + 2,
    }[_geltung(norm)]


def build_verfassungs_kodex(
    grundrechts_senat: GrundrechtsSenat | None = None,
    *,
    kodex_id: str = "verfassungs-kodex",
) -> VerfassungsKodex:
    """Build the supreme constitutional codex — crown of Leitstern's constitutional order."""

    resolved_senat = (
        build_grundrechts_senat(senat_id=f"{kodex_id}-senat")
        if grundrechts_senat is None
        else grundrechts_senat
    )
    normen = tuple(
        VerfassungsKodexNorm(
            verfassungs_kodex_norm_id=f"{kodex_id}-{n.senat_norm_id.removeprefix(f'{resolved_senat.senat_id}-')}",
            sequence=index,
            senat_norm_id=n.senat_norm_id,
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
            senat_rang=n.senat_rang,
            senat_prozedur=n.prozedur,
            kodex_rang=_kodex_rang(n),
            prozedur=_kodex_prozedur(n),
            geltung=_geltung(n),
            verfassungs_kodex_norm_ids=n.senat_norm_ids,
            canonical=n.canonical and _geltung(n) is VerfassungsKodexGeltung.GRUNDLEGEND_KODIFIZIERT,
            kodex_weight=_kodex_weight(n),
            kodex_tier=_kodex_tier(n),
            verfassungs_kodex_norm_tags=tuple(
                dict.fromkeys(
                    (
                        *n.senat_norm_tags,
                        _kodex_rang(n).value,
                        _kodex_prozedur(n).value,
                        _geltung(n).value,
                    )
                )
            ),
            summary=(
                f"{n.senat_norm_id} codified as {_kodex_rang(n).value} via "
                f"{_kodex_prozedur(n).value} with geltung {_geltung(n).value}."
            ),
        )
        for index, n in enumerate(resolved_senat.normen, start=1)
    )
    if not normen:
        raise ValueError("verfassungs kodex requires at least one norm")

    severity = "info"
    status = "kodex-grundlegend-kodifiziert"
    if any(n.geltung is VerfassungsKodexGeltung.GESPERRT for n in normen):
        severity = "critical"
        status = "kodex-gesperrt"
    elif any(n.geltung is VerfassungsKodexGeltung.KODIFIZIERT for n in normen):
        severity = "warning"
        status = "kodex-kodifiziert"

    kodex_signal = TelemetrySignal(
        signal_name="verfassungs-kodex",
        boundary=resolved_senat.senat_signal.boundary,
        correlation_id=kodex_id,
        severity=severity,
        status=status,
        metrics={
            "norm_count": float(len(normen)),
            "gesperrt_count": float(sum(1 for n in normen if n.geltung is VerfassungsKodexGeltung.GESPERRT)),
            "kodifiziert_count": float(sum(1 for n in normen if n.geltung is VerfassungsKodexGeltung.KODIFIZIERT)),
            "grundlegend_count": float(sum(1 for n in normen if n.geltung is VerfassungsKodexGeltung.GRUNDLEGEND_KODIFIZIERT)),
            "canonical_count": float(sum(1 for n in normen if n.canonical)),
            "avg_kodex_weight": round(sum(n.kodex_weight for n in normen) / len(normen), 3),
        },
        labels={"kodex_id": kodex_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_senat.final_snapshot.runtime_stage,
        signals=(kodex_signal, *resolved_senat.final_snapshot.signals),
        alerts=resolved_senat.final_snapshot.alerts,
        audit_entries=resolved_senat.final_snapshot.audit_entries,
        active_controls=resolved_senat.final_snapshot.active_controls,
    )
    return VerfassungsKodex(
        kodex_id=kodex_id,
        grundrechts_senat=resolved_senat,
        normen=normen,
        kodex_signal=kodex_signal,
        final_snapshot=final_snapshot,
    )
