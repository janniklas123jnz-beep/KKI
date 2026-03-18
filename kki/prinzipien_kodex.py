"""Prinzipien kodex encoding registered principle entries as codified Leitstern principles."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .grundsatz_register import (
    GrundsatzRegister,
    RegisterEintrag,
    RegisterKategorie,
    RegisterProzedur,
    RegisterStatus,
    build_grundsatz_register,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class PrinzipienKlasse(str, Enum):
    """Principle class that encodes one codified entry."""

    SCHUTZ_KLASSE = "schutz-klasse"
    ORDNUNGS_KLASSE = "ordnungs-klasse"
    SOUVERAENITAETS_KLASSE = "souveraenitaets-klasse"


class PrinzipienProzedur(str, Enum):
    """Codification protocol used to encode the principle."""

    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class PrinzipienStatus(str, Enum):
    """Canonical status of the codified principle."""

    GESPERRT = "gesperrt"
    KODIFIZIERT = "kodifiziert"
    GRUNDLEGEND_KODIFIZIERT = "grundlegend-kodifiziert"


@dataclass(frozen=True)
class PrinzipienSatz:
    """One codified principle derived from a registered entry."""

    satz_id: str
    sequence: int
    eintrag_id: str
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
    register_kategorie: RegisterKategorie
    register_prozedur: RegisterProzedur
    klasse: PrinzipienKlasse
    prozedur: PrinzipienProzedur
    status: PrinzipienStatus
    satz_ids: tuple[str, ...]
    canonical: bool
    kodex_weight: float
    kodex_tier: int
    satz_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "satz_id", _non_empty(self.satz_id, field_name="satz_id"))
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
        object.__setattr__(self, "kodex_weight", _clamp01(self.kodex_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.kodex_tier < 1:
            raise ValueError("kodex_tier must be positive")
        if not self.satz_ids:
            raise ValueError("satz_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "satz_id": self.satz_id,
            "sequence": self.sequence,
            "eintrag_id": self.eintrag_id,
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
            "register_kategorie": self.register_kategorie.value,
            "register_prozedur": self.register_prozedur.value,
            "klasse": self.klasse.value,
            "prozedur": self.prozedur.value,
            "status": self.status.value,
            "satz_ids": list(self.satz_ids),
            "canonical": self.canonical,
            "kodex_weight": self.kodex_weight,
            "kodex_tier": self.kodex_tier,
            "satz_tags": list(self.satz_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class PrinzipienKodex:
    """Principle codex encoding Leitstern registered entries as canonical principles."""

    kodex_id: str
    grundsatz_register: GrundsatzRegister
    saetze: tuple[PrinzipienSatz, ...]
    kodex_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "kodex_id", _non_empty(self.kodex_id, field_name="kodex_id"))

    @property
    def gesperrt_satz_ids(self) -> tuple[str, ...]:
        return tuple(s.satz_id for s in self.saetze if s.status is PrinzipienStatus.GESPERRT)

    @property
    def kodifiziert_satz_ids(self) -> tuple[str, ...]:
        return tuple(s.satz_id for s in self.saetze if s.status is PrinzipienStatus.KODIFIZIERT)

    @property
    def grundlegend_satz_ids(self) -> tuple[str, ...]:
        return tuple(s.satz_id for s in self.saetze if s.status is PrinzipienStatus.GRUNDLEGEND_KODIFIZIERT)

    def to_dict(self) -> dict[str, object]:
        return {
            "kodex_id": self.kodex_id,
            "grundsatz_register": self.grundsatz_register.to_dict(),
            "saetze": [s.to_dict() for s in self.saetze],
            "kodex_signal": self.kodex_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "gesperrt_satz_ids": list(self.gesperrt_satz_ids),
            "kodifiziert_satz_ids": list(self.kodifiziert_satz_ids),
            "grundlegend_satz_ids": list(self.grundlegend_satz_ids),
        }


def _klasse(eintrag: RegisterEintrag) -> PrinzipienKlasse:
    return {
        RegisterKategorie.SCHUTZ_KATEGORIE: PrinzipienKlasse.SCHUTZ_KLASSE,
        RegisterKategorie.ORDNUNGS_KATEGORIE: PrinzipienKlasse.ORDNUNGS_KLASSE,
        RegisterKategorie.SOUVERAENITAETS_KATEGORIE: PrinzipienKlasse.SOUVERAENITAETS_KLASSE,
    }[eintrag.kategorie]


def _prozedur(eintrag: RegisterEintrag) -> PrinzipienProzedur:
    return {
        RegisterProzedur.NOTPROZEDUR: PrinzipienProzedur.NOTPROZEDUR,
        RegisterProzedur.REGELPROTOKOLL: PrinzipienProzedur.REGELPROTOKOLL,
        RegisterProzedur.PLENARPROTOKOLL: PrinzipienProzedur.PLENARPROTOKOLL,
    }[eintrag.prozedur]


def _status(eintrag: RegisterEintrag) -> PrinzipienStatus:
    return {
        RegisterStatus.GESPERRT: PrinzipienStatus.GESPERRT,
        RegisterStatus.EINGETRAGEN: PrinzipienStatus.KODIFIZIERT,
        RegisterStatus.GRUNDLEGEND_EINGETRAGEN: PrinzipienStatus.GRUNDLEGEND_KODIFIZIERT,
    }[eintrag.status]


def _kodex_weight(eintrag: RegisterEintrag) -> float:
    bonus = {
        PrinzipienStatus.GESPERRT: 0.0,
        PrinzipienStatus.KODIFIZIERT: 0.04,
        PrinzipienStatus.GRUNDLEGEND_KODIFIZIERT: 0.08,
    }[_status(eintrag)]
    return round(min(1.0, eintrag.register_weight + bonus), 3)


def _kodex_tier(eintrag: RegisterEintrag) -> int:
    return {
        PrinzipienStatus.GESPERRT: eintrag.registry_tier,
        PrinzipienStatus.KODIFIZIERT: eintrag.registry_tier + 1,
        PrinzipienStatus.GRUNDLEGEND_KODIFIZIERT: eintrag.registry_tier + 2,
    }[_status(eintrag)]


def build_prinzipien_kodex(
    grundsatz_register: GrundsatzRegister | None = None,
    *,
    kodex_id: str = "prinzipien-kodex",
) -> PrinzipienKodex:
    """Build the principle codex encoding Leitstern registered entries."""

    resolved_register = (
        build_grundsatz_register(register_id=f"{kodex_id}-register")
        if grundsatz_register is None
        else grundsatz_register
    )
    saetze = tuple(
        PrinzipienSatz(
            satz_id=f"{kodex_id}-{e.eintrag_id.removeprefix(f'{resolved_register.register_id}-')}",
            sequence=index,
            eintrag_id=e.eintrag_id,
            pfeiler_id=e.pfeiler_id,
            klausel_id=e.klausel_id,
            norm_id=e.norm_id,
            abschnitt_id=e.abschnitt_id,
            artikel_id=e.artikel_id,
            mandat_id=e.mandat_id,
            fall_id=e.fall_id,
            line_id=e.line_id,
            article_id=e.article_id,
            entry_id=e.entry_id,
            section_id=e.section_id,
            reference_key=e.reference_key,
            register_kategorie=e.kategorie,
            register_prozedur=e.prozedur,
            klasse=_klasse(e),
            prozedur=_prozedur(e),
            status=_status(e),
            satz_ids=e.eintrag_ids,
            canonical=e.canonical and _status(e) is PrinzipienStatus.GRUNDLEGEND_KODIFIZIERT,
            kodex_weight=_kodex_weight(e),
            kodex_tier=_kodex_tier(e),
            satz_tags=tuple(
                dict.fromkeys(
                    (
                        *e.eintrag_tags,
                        _klasse(e).value,
                        _prozedur(e).value,
                        _status(e).value,
                    )
                )
            ),
            summary=(
                f"{e.eintrag_id} codified in {_klasse(e).value} via "
                f"{_prozedur(e).value} with status {_status(e).value}."
            ),
        )
        for index, e in enumerate(resolved_register.eintraege, start=1)
    )
    if not saetze:
        raise ValueError("prinzipien kodex requires at least one satz")

    severity = "info"
    status = "kodex-grundlegend-kodifiziert"
    if any(s.status is PrinzipienStatus.GESPERRT for s in saetze):
        severity = "critical"
        status = "kodex-gesperrt"
    elif any(s.status is PrinzipienStatus.KODIFIZIERT for s in saetze):
        severity = "warning"
        status = "kodex-kodifiziert"

    kodex_signal = TelemetrySignal(
        signal_name="prinzipien-kodex",
        boundary=resolved_register.register_signal.boundary,
        correlation_id=kodex_id,
        severity=severity,
        status=status,
        metrics={
            "satz_count": float(len(saetze)),
            "gesperrt_count": float(sum(1 for s in saetze if s.status is PrinzipienStatus.GESPERRT)),
            "kodifiziert_count": float(sum(1 for s in saetze if s.status is PrinzipienStatus.KODIFIZIERT)),
            "grundlegend_count": float(sum(1 for s in saetze if s.status is PrinzipienStatus.GRUNDLEGEND_KODIFIZIERT)),
            "canonical_count": float(sum(1 for s in saetze if s.canonical)),
            "avg_kodex_weight": round(sum(s.kodex_weight for s in saetze) / len(saetze), 3),
        },
        labels={"kodex_id": kodex_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_register.final_snapshot.runtime_stage,
        signals=(kodex_signal, *resolved_register.final_snapshot.signals),
        alerts=resolved_register.final_snapshot.alerts,
        audit_entries=resolved_register.final_snapshot.audit_entries,
        active_controls=resolved_register.final_snapshot.active_controls,
    )
    return PrinzipienKodex(
        kodex_id=kodex_id,
        grundsatz_register=resolved_register,
        saetze=saetze,
        kodex_signal=kodex_signal,
        final_snapshot=final_snapshot,
    )
