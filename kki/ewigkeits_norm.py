"""Ewigkeits norm encoding supreme register entries as eternally binding Leitstern norms."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .supremats_register import (
    SuprematsGeltung,
    SuprematsKlasse,
    SuprematsNorm,
    SuprematsProzedur,
    SuprematsRegister,
    build_supremats_register,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class EwigkeitsTyp(str, Enum):
    """Eternity type that classifies one eternal norm entry."""

    SCHUTZ_EWIGKEIT = "schutz-ewigkeit"
    ORDNUNGS_EWIGKEIT = "ordnungs-ewigkeit"
    SOUVERAENITAETS_EWIGKEIT = "souveraenitaets-ewigkeit"


class EwigkeitsProzedur(str, Enum):
    """Eternity procedure used to enshrine the norm."""

    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class EwigkeitsGeltung(str, Enum):
    """Canonical validity of the eternally binding norm."""

    GESPERRT = "gesperrt"
    VEREWIGT = "verewigt"
    GRUNDLEGEND_VEREWIGT = "grundlegend-verewigt"


@dataclass(frozen=True)
class EwigkeitsEintrag:
    """One eternal norm entry derived from a supreme register entry."""

    ewigkeits_eintrag_id: str
    sequence: int
    supremats_norm_id: str
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
    supremats_klasse: SuprematsKlasse
    supremats_prozedur: SuprematsProzedur
    ewigkeits_typ: EwigkeitsTyp
    prozedur: EwigkeitsProzedur
    geltung: EwigkeitsGeltung
    ewigkeits_eintrag_ids: tuple[str, ...]
    canonical: bool
    ewigkeits_weight: float
    ewigkeits_tier: int
    ewigkeits_eintrag_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "ewigkeits_eintrag_id", _non_empty(self.ewigkeits_eintrag_id, field_name="ewigkeits_eintrag_id"))
        object.__setattr__(self, "supremats_norm_id", _non_empty(self.supremats_norm_id, field_name="supremats_norm_id"))
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
        object.__setattr__(self, "ewigkeits_weight", _clamp01(self.ewigkeits_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.ewigkeits_tier < 1:
            raise ValueError("ewigkeits_tier must be positive")
        if not self.ewigkeits_eintrag_ids:
            raise ValueError("ewigkeits_eintrag_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "ewigkeits_eintrag_id": self.ewigkeits_eintrag_id,
            "sequence": self.sequence,
            "supremats_norm_id": self.supremats_norm_id,
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
            "supremats_klasse": self.supremats_klasse.value,
            "supremats_prozedur": self.supremats_prozedur.value,
            "ewigkeits_typ": self.ewigkeits_typ.value,
            "prozedur": self.prozedur.value,
            "geltung": self.geltung.value,
            "ewigkeits_eintrag_ids": list(self.ewigkeits_eintrag_ids),
            "canonical": self.canonical,
            "ewigkeits_weight": self.ewigkeits_weight,
            "ewigkeits_tier": self.ewigkeits_tier,
            "ewigkeits_eintrag_tags": list(self.ewigkeits_eintrag_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class EwigkeitsNorm:
    """Eternity norm encoding Leitstern supreme entries as eternally binding constitutional norms."""

    norm_id: str
    supremats_register: SuprematsRegister
    eintraege: tuple[EwigkeitsEintrag, ...]
    norm_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "norm_id", _non_empty(self.norm_id, field_name="norm_id"))

    @property
    def gesperrt_eintrag_ids(self) -> tuple[str, ...]:
        return tuple(e.ewigkeits_eintrag_id for e in self.eintraege if e.geltung is EwigkeitsGeltung.GESPERRT)

    @property
    def verewigt_eintrag_ids(self) -> tuple[str, ...]:
        return tuple(e.ewigkeits_eintrag_id for e in self.eintraege if e.geltung is EwigkeitsGeltung.VEREWIGT)

    @property
    def grundlegend_eintrag_ids(self) -> tuple[str, ...]:
        return tuple(e.ewigkeits_eintrag_id for e in self.eintraege if e.geltung is EwigkeitsGeltung.GRUNDLEGEND_VEREWIGT)

    def to_dict(self) -> dict[str, object]:
        return {
            "norm_id": self.norm_id,
            "supremats_register": self.supremats_register.to_dict(),
            "eintraege": [e.to_dict() for e in self.eintraege],
            "norm_signal": self.norm_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "gesperrt_eintrag_ids": list(self.gesperrt_eintrag_ids),
            "verewigt_eintrag_ids": list(self.verewigt_eintrag_ids),
            "grundlegend_eintrag_ids": list(self.grundlegend_eintrag_ids),
        }


def _ewigkeits_typ(norm: SuprematsNorm) -> EwigkeitsTyp:
    return {
        SuprematsKlasse.SCHUTZ_SUPREMAT: EwigkeitsTyp.SCHUTZ_EWIGKEIT,
        SuprematsKlasse.ORDNUNGS_SUPREMAT: EwigkeitsTyp.ORDNUNGS_EWIGKEIT,
        SuprematsKlasse.SOUVERAENITAETS_SUPREMAT: EwigkeitsTyp.SOUVERAENITAETS_EWIGKEIT,
    }[norm.supremats_klasse]


def _ewigkeits_prozedur(norm: SuprematsNorm) -> EwigkeitsProzedur:
    return {
        SuprematsProzedur.NOTPROZEDUR: EwigkeitsProzedur.NOTPROZEDUR,
        SuprematsProzedur.REGELPROTOKOLL: EwigkeitsProzedur.REGELPROTOKOLL,
        SuprematsProzedur.PLENARPROTOKOLL: EwigkeitsProzedur.PLENARPROTOKOLL,
    }[norm.prozedur]


def _geltung(norm: SuprematsNorm) -> EwigkeitsGeltung:
    return {
        SuprematsGeltung.GESPERRT: EwigkeitsGeltung.GESPERRT,
        SuprematsGeltung.SUPREMIERT: EwigkeitsGeltung.VEREWIGT,
        SuprematsGeltung.GRUNDLEGEND_SUPREMIERT: EwigkeitsGeltung.GRUNDLEGEND_VEREWIGT,
    }[norm.geltung]


def _ewigkeits_weight(norm: SuprematsNorm) -> float:
    bonus = {
        EwigkeitsGeltung.GESPERRT: 0.0,
        EwigkeitsGeltung.VEREWIGT: 0.04,
        EwigkeitsGeltung.GRUNDLEGEND_VEREWIGT: 0.08,
    }[_geltung(norm)]
    return round(min(1.0, norm.supremats_weight + bonus), 3)


def _ewigkeits_tier(norm: SuprematsNorm) -> int:
    return {
        EwigkeitsGeltung.GESPERRT: norm.supremats_tier,
        EwigkeitsGeltung.VEREWIGT: norm.supremats_tier + 1,
        EwigkeitsGeltung.GRUNDLEGEND_VEREWIGT: norm.supremats_tier + 2,
    }[_geltung(norm)]


def build_ewigkeits_norm(
    supremats_register: SuprematsRegister | None = None,
    *,
    norm_id: str = "ewigkeits-norm",
) -> EwigkeitsNorm:
    """Build the eternity norm encoding Leitstern supreme register entries."""

    resolved_register = (
        build_supremats_register(register_id=f"{norm_id}-register")
        if supremats_register is None
        else supremats_register
    )
    eintraege = tuple(
        EwigkeitsEintrag(
            ewigkeits_eintrag_id=f"{norm_id}-{n.supremats_norm_id.removeprefix(f'{resolved_register.register_id}-')}",
            sequence=index,
            supremats_norm_id=n.supremats_norm_id,
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
            supremats_klasse=n.supremats_klasse,
            supremats_prozedur=n.prozedur,
            ewigkeits_typ=_ewigkeits_typ(n),
            prozedur=_ewigkeits_prozedur(n),
            geltung=_geltung(n),
            ewigkeits_eintrag_ids=n.supremats_norm_ids,
            canonical=n.canonical and _geltung(n) is EwigkeitsGeltung.GRUNDLEGEND_VEREWIGT,
            ewigkeits_weight=_ewigkeits_weight(n),
            ewigkeits_tier=_ewigkeits_tier(n),
            ewigkeits_eintrag_tags=tuple(
                dict.fromkeys(
                    (
                        *n.supremats_norm_tags,
                        _ewigkeits_typ(n).value,
                        _ewigkeits_prozedur(n).value,
                        _geltung(n).value,
                    )
                )
            ),
            summary=(
                f"{n.supremats_norm_id} enshrined as {_ewigkeits_typ(n).value} via "
                f"{_ewigkeits_prozedur(n).value} with geltung {_geltung(n).value}."
            ),
        )
        for index, n in enumerate(resolved_register.normen, start=1)
    )
    if not eintraege:
        raise ValueError("ewigkeits norm requires at least one entry")

    severity = "info"
    status = "norm-grundlegend-verewigt"
    if any(e.geltung is EwigkeitsGeltung.GESPERRT for e in eintraege):
        severity = "critical"
        status = "norm-gesperrt"
    elif any(e.geltung is EwigkeitsGeltung.VEREWIGT for e in eintraege):
        severity = "warning"
        status = "norm-verewigt"

    norm_signal = TelemetrySignal(
        signal_name="ewigkeits-norm",
        boundary=resolved_register.register_signal.boundary,
        correlation_id=norm_id,
        severity=severity,
        status=status,
        metrics={
            "eintrag_count": float(len(eintraege)),
            "gesperrt_count": float(sum(1 for e in eintraege if e.geltung is EwigkeitsGeltung.GESPERRT)),
            "verewigt_count": float(sum(1 for e in eintraege if e.geltung is EwigkeitsGeltung.VEREWIGT)),
            "grundlegend_count": float(sum(1 for e in eintraege if e.geltung is EwigkeitsGeltung.GRUNDLEGEND_VEREWIGT)),
            "canonical_count": float(sum(1 for e in eintraege if e.canonical)),
            "avg_ewigkeits_weight": round(sum(e.ewigkeits_weight for e in eintraege) / len(eintraege), 3),
        },
        labels={"norm_id": norm_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_register.final_snapshot.runtime_stage,
        signals=(norm_signal, *resolved_register.final_snapshot.signals),
        alerts=resolved_register.final_snapshot.alerts,
        audit_entries=resolved_register.final_snapshot.audit_entries,
        active_controls=resolved_register.final_snapshot.active_controls,
    )
    return EwigkeitsNorm(
        norm_id=norm_id,
        supremats_register=resolved_register,
        eintraege=eintraege,
        norm_signal=norm_signal,
        final_snapshot=final_snapshot,
    )
