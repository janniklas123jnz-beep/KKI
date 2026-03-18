"""Werte charta anchoring codified principles as foundational Leitstern values."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .prinzipien_kodex import (
    PrinzipienKlasse,
    PrinzipienKodex,
    PrinzipienProzedur,
    PrinzipienSatz,
    PrinzipienStatus,
    build_prinzipien_kodex,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class WerteTyp(str, Enum):
    """Value type that anchors one codified principle."""

    SCHUTZ_WERT = "schutz-wert"
    ORDNUNGS_WERT = "ordnungs-wert"
    SOUVERAENITAETS_WERT = "souveraenitaets-wert"


class WerteProzedur(str, Enum):
    """Anchoring protocol used to enshrine the value."""

    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class WerteStatus(str, Enum):
    """Canonical status of the anchored value article."""

    GESPERRT = "gesperrt"
    VERANKERT = "verankert"
    GRUNDLEGEND_VERANKERT = "grundlegend-verankert"


@dataclass(frozen=True)
class WerteArtikel:
    """One value article derived from a codified principle."""

    artikel_id: str
    sequence: int
    satz_id: str
    eintrag_id: str
    pfeiler_id: str
    klausel_id: str
    norm_id: str
    abschnitt_id: str
    artikel_ref_id: str
    mandat_id: str
    fall_id: str
    line_id: str
    article_id: str
    entry_id: str
    section_id: str
    reference_key: str
    prinzipien_klasse: PrinzipienKlasse
    prinzipien_prozedur: PrinzipienProzedur
    typ: WerteTyp
    prozedur: WerteProzedur
    status: WerteStatus
    artikel_ids: tuple[str, ...]
    canonical: bool
    charta_weight: float
    charta_tier: int
    artikel_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "artikel_id", _non_empty(self.artikel_id, field_name="artikel_id"))
        object.__setattr__(self, "satz_id", _non_empty(self.satz_id, field_name="satz_id"))
        object.__setattr__(self, "eintrag_id", _non_empty(self.eintrag_id, field_name="eintrag_id"))
        object.__setattr__(self, "pfeiler_id", _non_empty(self.pfeiler_id, field_name="pfeiler_id"))
        object.__setattr__(self, "klausel_id", _non_empty(self.klausel_id, field_name="klausel_id"))
        object.__setattr__(self, "norm_id", _non_empty(self.norm_id, field_name="norm_id"))
        object.__setattr__(self, "abschnitt_id", _non_empty(self.abschnitt_id, field_name="abschnitt_id"))
        object.__setattr__(self, "artikel_ref_id", _non_empty(self.artikel_ref_id, field_name="artikel_ref_id"))
        object.__setattr__(self, "mandat_id", _non_empty(self.mandat_id, field_name="mandat_id"))
        object.__setattr__(self, "fall_id", _non_empty(self.fall_id, field_name="fall_id"))
        object.__setattr__(self, "line_id", _non_empty(self.line_id, field_name="line_id"))
        object.__setattr__(self, "article_id", _non_empty(self.article_id, field_name="article_id"))
        object.__setattr__(self, "entry_id", _non_empty(self.entry_id, field_name="entry_id"))
        object.__setattr__(self, "section_id", _non_empty(self.section_id, field_name="section_id"))
        object.__setattr__(self, "reference_key", _non_empty(self.reference_key, field_name="reference_key"))
        object.__setattr__(self, "charta_weight", _clamp01(self.charta_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.charta_tier < 1:
            raise ValueError("charta_tier must be positive")
        if not self.artikel_ids:
            raise ValueError("artikel_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "artikel_id": self.artikel_id,
            "sequence": self.sequence,
            "satz_id": self.satz_id,
            "eintrag_id": self.eintrag_id,
            "pfeiler_id": self.pfeiler_id,
            "klausel_id": self.klausel_id,
            "norm_id": self.norm_id,
            "abschnitt_id": self.abschnitt_id,
            "artikel_ref_id": self.artikel_ref_id,
            "mandat_id": self.mandat_id,
            "fall_id": self.fall_id,
            "line_id": self.line_id,
            "article_id": self.article_id,
            "entry_id": self.entry_id,
            "section_id": self.section_id,
            "reference_key": self.reference_key,
            "prinzipien_klasse": self.prinzipien_klasse.value,
            "prinzipien_prozedur": self.prinzipien_prozedur.value,
            "typ": self.typ.value,
            "prozedur": self.prozedur.value,
            "status": self.status.value,
            "artikel_ids": list(self.artikel_ids),
            "canonical": self.canonical,
            "charta_weight": self.charta_weight,
            "charta_tier": self.charta_tier,
            "artikel_tags": list(self.artikel_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class WerteCharta:
    """Value charter anchoring Leitstern codified principles as foundational values."""

    charta_id: str
    prinzipien_kodex: PrinzipienKodex
    artikel: tuple[WerteArtikel, ...]
    charta_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "charta_id", _non_empty(self.charta_id, field_name="charta_id"))

    @property
    def gesperrt_artikel_ids(self) -> tuple[str, ...]:
        return tuple(a.artikel_id for a in self.artikel if a.status is WerteStatus.GESPERRT)

    @property
    def verankert_artikel_ids(self) -> tuple[str, ...]:
        return tuple(a.artikel_id for a in self.artikel if a.status is WerteStatus.VERANKERT)

    @property
    def grundlegend_artikel_ids(self) -> tuple[str, ...]:
        return tuple(a.artikel_id for a in self.artikel if a.status is WerteStatus.GRUNDLEGEND_VERANKERT)

    def to_dict(self) -> dict[str, object]:
        return {
            "charta_id": self.charta_id,
            "prinzipien_kodex": self.prinzipien_kodex.to_dict(),
            "artikel": [a.to_dict() for a in self.artikel],
            "charta_signal": self.charta_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "gesperrt_artikel_ids": list(self.gesperrt_artikel_ids),
            "verankert_artikel_ids": list(self.verankert_artikel_ids),
            "grundlegend_artikel_ids": list(self.grundlegend_artikel_ids),
        }


def _typ(satz: PrinzipienSatz) -> WerteTyp:
    return {
        PrinzipienKlasse.SCHUTZ_KLASSE: WerteTyp.SCHUTZ_WERT,
        PrinzipienKlasse.ORDNUNGS_KLASSE: WerteTyp.ORDNUNGS_WERT,
        PrinzipienKlasse.SOUVERAENITAETS_KLASSE: WerteTyp.SOUVERAENITAETS_WERT,
    }[satz.klasse]


def _prozedur(satz: PrinzipienSatz) -> WerteProzedur:
    return {
        PrinzipienProzedur.NOTPROZEDUR: WerteProzedur.NOTPROZEDUR,
        PrinzipienProzedur.REGELPROTOKOLL: WerteProzedur.REGELPROTOKOLL,
        PrinzipienProzedur.PLENARPROTOKOLL: WerteProzedur.PLENARPROTOKOLL,
    }[satz.prozedur]


def _status(satz: PrinzipienSatz) -> WerteStatus:
    return {
        PrinzipienStatus.GESPERRT: WerteStatus.GESPERRT,
        PrinzipienStatus.KODIFIZIERT: WerteStatus.VERANKERT,
        PrinzipienStatus.GRUNDLEGEND_KODIFIZIERT: WerteStatus.GRUNDLEGEND_VERANKERT,
    }[satz.status]


def _charta_weight(satz: PrinzipienSatz) -> float:
    bonus = {
        WerteStatus.GESPERRT: 0.0,
        WerteStatus.VERANKERT: 0.04,
        WerteStatus.GRUNDLEGEND_VERANKERT: 0.08,
    }[_status(satz)]
    return round(min(1.0, satz.kodex_weight + bonus), 3)


def _charta_tier(satz: PrinzipienSatz) -> int:
    return {
        WerteStatus.GESPERRT: satz.kodex_tier,
        WerteStatus.VERANKERT: satz.kodex_tier + 1,
        WerteStatus.GRUNDLEGEND_VERANKERT: satz.kodex_tier + 2,
    }[_status(satz)]


def build_werte_charta(
    prinzipien_kodex: PrinzipienKodex | None = None,
    *,
    charta_id: str = "werte-charta",
) -> WerteCharta:
    """Build the value charter anchoring Leitstern codified principles."""

    resolved_kodex = (
        build_prinzipien_kodex(kodex_id=f"{charta_id}-kodex")
        if prinzipien_kodex is None
        else prinzipien_kodex
    )
    artikel = tuple(
        WerteArtikel(
            artikel_id=f"{charta_id}-{s.satz_id.removeprefix(f'{resolved_kodex.kodex_id}-')}",
            sequence=index,
            satz_id=s.satz_id,
            eintrag_id=s.eintrag_id,
            pfeiler_id=s.pfeiler_id,
            klausel_id=s.klausel_id,
            norm_id=s.norm_id,
            abschnitt_id=s.abschnitt_id,
            artikel_ref_id=s.artikel_id,
            mandat_id=s.mandat_id,
            fall_id=s.fall_id,
            line_id=s.line_id,
            article_id=s.article_id,
            entry_id=s.entry_id,
            section_id=s.section_id,
            reference_key=s.reference_key,
            prinzipien_klasse=s.klasse,
            prinzipien_prozedur=s.prozedur,
            typ=_typ(s),
            prozedur=_prozedur(s),
            status=_status(s),
            artikel_ids=s.satz_ids,
            canonical=s.canonical and _status(s) is WerteStatus.GRUNDLEGEND_VERANKERT,
            charta_weight=_charta_weight(s),
            charta_tier=_charta_tier(s),
            artikel_tags=tuple(
                dict.fromkeys(
                    (
                        *s.satz_tags,
                        _typ(s).value,
                        _prozedur(s).value,
                        _status(s).value,
                    )
                )
            ),
            summary=(
                f"{s.satz_id} anchored in {_typ(s).value} via "
                f"{_prozedur(s).value} with status {_status(s).value}."
            ),
        )
        for index, s in enumerate(resolved_kodex.saetze, start=1)
    )
    if not artikel:
        raise ValueError("werte charta requires at least one artikel")

    severity = "info"
    status = "charta-grundlegend-verankert"
    if any(a.status is WerteStatus.GESPERRT for a in artikel):
        severity = "critical"
        status = "charta-gesperrt"
    elif any(a.status is WerteStatus.VERANKERT for a in artikel):
        severity = "warning"
        status = "charta-verankert"

    charta_signal = TelemetrySignal(
        signal_name="werte-charta",
        boundary=resolved_kodex.kodex_signal.boundary,
        correlation_id=charta_id,
        severity=severity,
        status=status,
        metrics={
            "artikel_count": float(len(artikel)),
            "gesperrt_count": float(sum(1 for a in artikel if a.status is WerteStatus.GESPERRT)),
            "verankert_count": float(sum(1 for a in artikel if a.status is WerteStatus.VERANKERT)),
            "grundlegend_count": float(sum(1 for a in artikel if a.status is WerteStatus.GRUNDLEGEND_VERANKERT)),
            "canonical_count": float(sum(1 for a in artikel if a.canonical)),
            "avg_charta_weight": round(sum(a.charta_weight for a in artikel) / len(artikel), 3),
        },
        labels={"charta_id": charta_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_kodex.final_snapshot.runtime_stage,
        signals=(charta_signal, *resolved_kodex.final_snapshot.signals),
        alerts=resolved_kodex.final_snapshot.alerts,
        audit_entries=resolved_kodex.final_snapshot.audit_entries,
        active_controls=resolved_kodex.final_snapshot.active_controls,
    )
    return WerteCharta(
        charta_id=charta_id,
        prinzipien_kodex=resolved_kodex,
        artikel=artikel,
        charta_signal=charta_signal,
        final_snapshot=final_snapshot,
    )
