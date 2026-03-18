"""Grundsatz register cataloguing legal pillars as canonical Leitstern principle entries."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .rechts_fundament import (
    FundamentKraft,
    FundamentPfeiler,
    FundamentSaeule,
    FundamentVerfahren,
    RechtsFundament,
    build_rechts_fundament,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class RegisterKategorie(str, Enum):
    """Register category that catalogues one legal pillar."""

    SCHUTZ_KATEGORIE = "schutz-kategorie"
    ORDNUNGS_KATEGORIE = "ordnungs-kategorie"
    SOUVERAENITAETS_KATEGORIE = "souveraenitaets-kategorie"


class RegisterProzedur(str, Enum):
    """Registration protocol used to catalogue the pillar."""

    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class RegisterStatus(str, Enum):
    """Canonical status of the registered principle entry."""

    GESPERRT = "gesperrt"
    EINGETRAGEN = "eingetragen"
    GRUNDLEGEND_EINGETRAGEN = "grundlegend-eingetragen"


@dataclass(frozen=True)
class RegisterEintrag:
    """One principle entry derived from a legal pillar."""

    eintrag_id: str
    sequence: int
    pfeiler_id: str
    klausel_id: str
    norm_id: str
    abschnitt_id: str
    artikel_id: str
    mandat_id: str
    fall_id: str
    line_id: str
    article_id: str
    entry_id: str
    section_id: str
    reference_key: str
    fundament_saeule: FundamentSaeule
    fundament_kraft: FundamentKraft
    fundament_verfahren: FundamentVerfahren
    kategorie: RegisterKategorie
    prozedur: RegisterProzedur
    status: RegisterStatus
    eintrag_ids: tuple[str, ...]
    canonical: bool
    register_weight: float
    registry_tier: int
    eintrag_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "eintrag_id", _non_empty(self.eintrag_id, field_name="eintrag_id"))
        object.__setattr__(self, "pfeiler_id", _non_empty(self.pfeiler_id, field_name="pfeiler_id"))
        object.__setattr__(self, "klausel_id", _non_empty(self.klausel_id, field_name="klausel_id"))
        object.__setattr__(self, "norm_id", _non_empty(self.norm_id, field_name="norm_id"))
        object.__setattr__(self, "abschnitt_id", _non_empty(self.abschnitt_id, field_name="abschnitt_id"))
        object.__setattr__(self, "artikel_id", _non_empty(self.artikel_id, field_name="artikel_id"))
        object.__setattr__(self, "mandat_id", _non_empty(self.mandat_id, field_name="mandat_id"))
        object.__setattr__(self, "fall_id", _non_empty(self.fall_id, field_name="fall_id"))
        object.__setattr__(self, "line_id", _non_empty(self.line_id, field_name="line_id"))
        object.__setattr__(self, "article_id", _non_empty(self.article_id, field_name="article_id"))
        object.__setattr__(self, "entry_id", _non_empty(self.entry_id, field_name="entry_id"))
        object.__setattr__(self, "section_id", _non_empty(self.section_id, field_name="section_id"))
        object.__setattr__(self, "reference_key", _non_empty(self.reference_key, field_name="reference_key"))
        object.__setattr__(self, "register_weight", _clamp01(self.register_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.registry_tier < 1:
            raise ValueError("registry_tier must be positive")
        if not self.eintrag_ids:
            raise ValueError("eintrag_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "eintrag_id": self.eintrag_id,
            "sequence": self.sequence,
            "pfeiler_id": self.pfeiler_id,
            "klausel_id": self.klausel_id,
            "norm_id": self.norm_id,
            "abschnitt_id": self.abschnitt_id,
            "artikel_id": self.artikel_id,
            "mandat_id": self.mandat_id,
            "fall_id": self.fall_id,
            "line_id": self.line_id,
            "article_id": self.article_id,
            "entry_id": self.entry_id,
            "section_id": self.section_id,
            "reference_key": self.reference_key,
            "fundament_saeule": self.fundament_saeule.value,
            "fundament_kraft": self.fundament_kraft.value,
            "fundament_verfahren": self.fundament_verfahren.value,
            "kategorie": self.kategorie.value,
            "prozedur": self.prozedur.value,
            "status": self.status.value,
            "eintrag_ids": list(self.eintrag_ids),
            "canonical": self.canonical,
            "register_weight": self.register_weight,
            "registry_tier": self.registry_tier,
            "eintrag_tags": list(self.eintrag_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class GrundsatzRegister:
    """Principle register cataloguing Leitstern legal pillars as canonical entries."""

    register_id: str
    rechts_fundament: RechtsFundament
    eintraege: tuple[RegisterEintrag, ...]
    register_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "register_id", _non_empty(self.register_id, field_name="register_id"))

    @property
    def gesperrt_eintrag_ids(self) -> tuple[str, ...]:
        return tuple(e.eintrag_id for e in self.eintraege if e.status is RegisterStatus.GESPERRT)

    @property
    def eingetragen_eintrag_ids(self) -> tuple[str, ...]:
        return tuple(e.eintrag_id for e in self.eintraege if e.status is RegisterStatus.EINGETRAGEN)

    @property
    def grundlegend_eintrag_ids(self) -> tuple[str, ...]:
        return tuple(e.eintrag_id for e in self.eintraege if e.status is RegisterStatus.GRUNDLEGEND_EINGETRAGEN)

    def to_dict(self) -> dict[str, object]:
        return {
            "register_id": self.register_id,
            "rechts_fundament": self.rechts_fundament.to_dict(),
            "eintraege": [e.to_dict() for e in self.eintraege],
            "register_signal": self.register_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "gesperrt_eintrag_ids": list(self.gesperrt_eintrag_ids),
            "eingetragen_eintrag_ids": list(self.eingetragen_eintrag_ids),
            "grundlegend_eintrag_ids": list(self.grundlegend_eintrag_ids),
        }


def _kategorie(pfeiler: FundamentPfeiler) -> RegisterKategorie:
    return {
        FundamentSaeule.SCHUTZ_SAEULE: RegisterKategorie.SCHUTZ_KATEGORIE,
        FundamentSaeule.ORDNUNGS_SAEULE: RegisterKategorie.ORDNUNGS_KATEGORIE,
        FundamentSaeule.SOUVERAENITAETS_SAEULE: RegisterKategorie.SOUVERAENITAETS_KATEGORIE,
    }[pfeiler.saeule]


def _prozedur(pfeiler: FundamentPfeiler) -> RegisterProzedur:
    return {
        FundamentVerfahren.NOTVERFAHREN: RegisterProzedur.NOTPROZEDUR,
        FundamentVerfahren.REGELVERFAHREN: RegisterProzedur.REGELPROTOKOLL,
        FundamentVerfahren.PLENARVERFAHREN: RegisterProzedur.PLENARPROTOKOLL,
    }[pfeiler.verfahren]


def _status(pfeiler: FundamentPfeiler) -> RegisterStatus:
    return {
        FundamentKraft.GESPERRT: RegisterStatus.GESPERRT,
        FundamentKraft.FUNDIERT: RegisterStatus.EINGETRAGEN,
        FundamentKraft.TRAGENDES_RECHT: RegisterStatus.GRUNDLEGEND_EINGETRAGEN,
    }[pfeiler.kraft]


def _register_weight(pfeiler: FundamentPfeiler) -> float:
    bonus = {
        RegisterStatus.GESPERRT: 0.0,
        RegisterStatus.EINGETRAGEN: 0.04,
        RegisterStatus.GRUNDLEGEND_EINGETRAGEN: 0.08,
    }[_status(pfeiler)]
    return round(min(1.0, pfeiler.fundament_weight + bonus), 3)


def _registry_tier(pfeiler: FundamentPfeiler) -> int:
    return {
        RegisterStatus.GESPERRT: pfeiler.foundation_depth,
        RegisterStatus.EINGETRAGEN: pfeiler.foundation_depth + 1,
        RegisterStatus.GRUNDLEGEND_EINGETRAGEN: pfeiler.foundation_depth + 2,
    }[_status(pfeiler)]


def build_grundsatz_register(
    rechts_fundament: RechtsFundament | None = None,
    *,
    register_id: str = "grundsatz-register",
) -> GrundsatzRegister:
    """Build the principle register cataloguing Leitstern legal pillars."""

    resolved_fundament = (
        build_rechts_fundament(fundament_id=f"{register_id}-fundament")
        if rechts_fundament is None
        else rechts_fundament
    )
    eintraege = tuple(
        RegisterEintrag(
            eintrag_id=f"{register_id}-{p.pfeiler_id.removeprefix(f'{resolved_fundament.fundament_id}-')}",
            sequence=index,
            pfeiler_id=p.pfeiler_id,
            klausel_id=p.klausel_id,
            norm_id=p.norm_id,
            abschnitt_id=p.abschnitt_id,
            artikel_id=p.artikel_id,
            mandat_id=p.mandat_id,
            fall_id=p.fall_id,
            line_id=p.line_id,
            article_id=p.article_id,
            entry_id=p.entry_id,
            section_id=p.section_id,
            reference_key=p.reference_key,
            fundament_saeule=p.saeule,
            fundament_kraft=p.kraft,
            fundament_verfahren=p.verfahren,
            kategorie=_kategorie(p),
            prozedur=_prozedur(p),
            status=_status(p),
            eintrag_ids=p.pfeiler_ids,
            canonical=p.load_bearing and _status(p) is RegisterStatus.GRUNDLEGEND_EINGETRAGEN,
            register_weight=_register_weight(p),
            registry_tier=_registry_tier(p),
            eintrag_tags=tuple(
                dict.fromkeys(
                    (
                        *p.pfeiler_tags,
                        _kategorie(p).value,
                        _prozedur(p).value,
                        _status(p).value,
                    )
                )
            ),
            summary=(
                f"{p.pfeiler_id} catalogued in {_kategorie(p).value} via "
                f"{_prozedur(p).value} with status {_status(p).value}."
            ),
        )
        for index, p in enumerate(resolved_fundament.pfeiler, start=1)
    )
    if not eintraege:
        raise ValueError("grundsatz register requires at least one eintrag")

    severity = "info"
    status = "register-grundlegend-eingetragen"
    if any(e.status is RegisterStatus.GESPERRT for e in eintraege):
        severity = "critical"
        status = "register-gesperrt"
    elif any(e.status is RegisterStatus.EINGETRAGEN for e in eintraege):
        severity = "warning"
        status = "register-eingetragen"

    register_signal = TelemetrySignal(
        signal_name="grundsatz-register",
        boundary=resolved_fundament.fundament_signal.boundary,
        correlation_id=register_id,
        severity=severity,
        status=status,
        metrics={
            "eintrag_count": float(len(eintraege)),
            "gesperrt_count": float(sum(1 for e in eintraege if e.status is RegisterStatus.GESPERRT)),
            "eingetragen_count": float(sum(1 for e in eintraege if e.status is RegisterStatus.EINGETRAGEN)),
            "grundlegend_count": float(sum(1 for e in eintraege if e.status is RegisterStatus.GRUNDLEGEND_EINGETRAGEN)),
            "canonical_count": float(sum(1 for e in eintraege if e.canonical)),
            "avg_register_weight": round(sum(e.register_weight for e in eintraege) / len(eintraege), 3),
        },
        labels={"register_id": register_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_fundament.final_snapshot.runtime_stage,
        signals=(register_signal, *resolved_fundament.final_snapshot.signals),
        alerts=resolved_fundament.final_snapshot.alerts,
        audit_entries=resolved_fundament.final_snapshot.audit_entries,
        active_controls=resolved_fundament.final_snapshot.active_controls,
    )
    return GrundsatzRegister(
        register_id=register_id,
        rechts_fundament=resolved_fundament,
        eintraege=eintraege,
        register_signal=register_signal,
        final_snapshot=final_snapshot,
    )
