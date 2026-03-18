"""Unions akt encoding legal norms as unified Leitstern union acts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .rechts_kodex import (
    KodexKlasse,
    KodexNorm,
    KodexProzedur,
    KodexStatus,
    RechtsKodex,
    build_rechts_kodex,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class UnionsTyp(str, Enum):
    """Union type that classifies one union act."""

    SCHUTZ_UNION = "schutz-union"
    ORDNUNGS_UNION = "ordnungs-union"
    SOUVERAENITAETS_UNION = "souveraenitaets-union"


class UnionsProzedur(str, Enum):
    """Union procedure used to enact the act."""

    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class UnionsGeltung(str, Enum):
    """Canonical validity of the union act."""

    GESPERRT = "gesperrt"
    VEREINT = "vereint"
    GRUNDLEGEND_VEREINT = "grundlegend-vereint"


@dataclass(frozen=True)
class UnionsNorm:
    """One union act derived from a codified legal norm."""

    unions_norm_id: str
    sequence: int
    kodex_norm_id: str
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
    kodex_klasse: KodexKlasse
    kodex_prozedur: KodexProzedur
    unions_typ: UnionsTyp
    prozedur: UnionsProzedur
    geltung: UnionsGeltung
    unions_norm_ids: tuple[str, ...]
    canonical: bool
    unions_weight: float
    unions_tier: int
    unions_norm_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "unions_norm_id", _non_empty(self.unions_norm_id, field_name="unions_norm_id"))
        object.__setattr__(self, "kodex_norm_id", _non_empty(self.kodex_norm_id, field_name="kodex_norm_id"))
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
        object.__setattr__(self, "unions_weight", _clamp01(self.unions_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.unions_tier < 1:
            raise ValueError("unions_tier must be positive")
        if not self.unions_norm_ids:
            raise ValueError("unions_norm_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "unions_norm_id": self.unions_norm_id,
            "sequence": self.sequence,
            "kodex_norm_id": self.kodex_norm_id,
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
            "kodex_klasse": self.kodex_klasse.value,
            "kodex_prozedur": self.kodex_prozedur.value,
            "unions_typ": self.unions_typ.value,
            "prozedur": self.prozedur.value,
            "geltung": self.geltung.value,
            "unions_norm_ids": list(self.unions_norm_ids),
            "canonical": self.canonical,
            "unions_weight": self.unions_weight,
            "unions_tier": self.unions_tier,
            "unions_norm_tags": list(self.unions_norm_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class UnionsAkt:
    """Union act encoding Leitstern legal norms as unified constitutional union acts."""

    akt_id: str
    rechts_kodex: RechtsKodex
    normen: tuple[UnionsNorm, ...]
    akt_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "akt_id", _non_empty(self.akt_id, field_name="akt_id"))

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.unions_norm_id for n in self.normen if n.geltung is UnionsGeltung.GESPERRT)

    @property
    def vereint_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.unions_norm_id for n in self.normen if n.geltung is UnionsGeltung.VEREINT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.unions_norm_id for n in self.normen if n.geltung is UnionsGeltung.GRUNDLEGEND_VEREINT)

    def to_dict(self) -> dict[str, object]:
        return {
            "akt_id": self.akt_id,
            "rechts_kodex": self.rechts_kodex.to_dict(),
            "normen": [n.to_dict() for n in self.normen],
            "akt_signal": self.akt_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "gesperrt_norm_ids": list(self.gesperrt_norm_ids),
            "vereint_norm_ids": list(self.vereint_norm_ids),
            "grundlegend_norm_ids": list(self.grundlegend_norm_ids),
        }


def _unions_typ(norm: KodexNorm) -> UnionsTyp:
    return {
        KodexKlasse.SCHUTZ_KLASSE: UnionsTyp.SCHUTZ_UNION,
        KodexKlasse.ORDNUNGS_KLASSE: UnionsTyp.ORDNUNGS_UNION,
        KodexKlasse.SOUVERAENITAETS_KLASSE: UnionsTyp.SOUVERAENITAETS_UNION,
    }[norm.klasse]


def _unions_prozedur(norm: KodexNorm) -> UnionsProzedur:
    return {
        KodexProzedur.NOTPROZEDUR: UnionsProzedur.NOTPROZEDUR,
        KodexProzedur.REGELPROTOKOLL: UnionsProzedur.REGELPROTOKOLL,
        KodexProzedur.PLENARPROTOKOLL: UnionsProzedur.PLENARPROTOKOLL,
    }[norm.prozedur]


def _geltung(norm: KodexNorm) -> UnionsGeltung:
    return {
        KodexStatus.GESPERRT: UnionsGeltung.GESPERRT,
        KodexStatus.KODIERT: UnionsGeltung.VEREINT,
        KodexStatus.GRUNDLEGEND_KODIERT: UnionsGeltung.GRUNDLEGEND_VEREINT,
    }[norm.status]


def _unions_weight(norm: KodexNorm) -> float:
    bonus = {
        UnionsGeltung.GESPERRT: 0.0,
        UnionsGeltung.VEREINT: 0.04,
        UnionsGeltung.GRUNDLEGEND_VEREINT: 0.08,
    }[_geltung(norm)]
    return round(min(1.0, norm.kodex_weight + bonus), 3)


def _unions_tier(norm: KodexNorm) -> int:
    return {
        UnionsGeltung.GESPERRT: norm.kodex_tier,
        UnionsGeltung.VEREINT: norm.kodex_tier + 1,
        UnionsGeltung.GRUNDLEGEND_VEREINT: norm.kodex_tier + 2,
    }[_geltung(norm)]


def build_unions_akt(
    rechts_kodex: RechtsKodex | None = None,
    *,
    akt_id: str = "unions-akt",
) -> UnionsAkt:
    """Build the union act encoding Leitstern legal norms."""

    resolved_kodex = (
        build_rechts_kodex(kodex_id=f"{akt_id}-kodex")
        if rechts_kodex is None
        else rechts_kodex
    )
    normen = tuple(
        UnionsNorm(
            unions_norm_id=f"{akt_id}-{n.kodex_norm_id.removeprefix(f'{resolved_kodex.kodex_id}-')}",
            sequence=index,
            kodex_norm_id=n.kodex_norm_id,
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
            kodex_klasse=n.klasse,
            kodex_prozedur=n.prozedur,
            unions_typ=_unions_typ(n),
            prozedur=_unions_prozedur(n),
            geltung=_geltung(n),
            unions_norm_ids=n.kodex_norm_ids,
            canonical=n.canonical and _geltung(n) is UnionsGeltung.GRUNDLEGEND_VEREINT,
            unions_weight=_unions_weight(n),
            unions_tier=_unions_tier(n),
            unions_norm_tags=tuple(
                dict.fromkeys(
                    (
                        *n.kodex_norm_tags,
                        _unions_typ(n).value,
                        _unions_prozedur(n).value,
                        _geltung(n).value,
                    )
                )
            ),
            summary=(
                f"{n.kodex_norm_id} enacted as {_unions_typ(n).value} via "
                f"{_unions_prozedur(n).value} with geltung {_geltung(n).value}."
            ),
        )
        for index, n in enumerate(resolved_kodex.normen, start=1)
    )
    if not normen:
        raise ValueError("unions akt requires at least one norm")

    severity = "info"
    status = "akt-grundlegend-vereint"
    if any(n.geltung is UnionsGeltung.GESPERRT for n in normen):
        severity = "critical"
        status = "akt-gesperrt"
    elif any(n.geltung is UnionsGeltung.VEREINT for n in normen):
        severity = "warning"
        status = "akt-vereint"

    akt_signal = TelemetrySignal(
        signal_name="unions-akt",
        boundary=resolved_kodex.kodex_signal.boundary,
        correlation_id=akt_id,
        severity=severity,
        status=status,
        metrics={
            "norm_count": float(len(normen)),
            "gesperrt_count": float(sum(1 for n in normen if n.geltung is UnionsGeltung.GESPERRT)),
            "vereint_count": float(sum(1 for n in normen if n.geltung is UnionsGeltung.VEREINT)),
            "grundlegend_count": float(sum(1 for n in normen if n.geltung is UnionsGeltung.GRUNDLEGEND_VEREINT)),
            "canonical_count": float(sum(1 for n in normen if n.canonical)),
            "avg_unions_weight": round(sum(n.unions_weight for n in normen) / len(normen), 3),
        },
        labels={"akt_id": akt_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_kodex.final_snapshot.runtime_stage,
        signals=(akt_signal, *resolved_kodex.final_snapshot.signals),
        alerts=resolved_kodex.final_snapshot.alerts,
        audit_entries=resolved_kodex.final_snapshot.audit_entries,
        active_controls=resolved_kodex.final_snapshot.active_controls,
    )
    return UnionsAkt(
        akt_id=akt_id,
        rechts_kodex=resolved_kodex,
        normen=normen,
        akt_signal=akt_signal,
        final_snapshot=final_snapshot,
    )
