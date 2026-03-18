"""Rechts fundament grounding authority clauses as load-bearing Leitstern legal pillars."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .autoritaets_dekret import (
    AutoritaetsDekret,
    DekretGeltung,
    DekretKlausel,
    DekretProzedur,
    DekretSektion,
    build_autoritaets_dekret,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class FundamentSaeule(str, Enum):
    """Legal foundation pillar that grounds one authority clause."""

    SCHUTZ_SAEULE = "schutz-saeule"
    ORDNUNGS_SAEULE = "ordnungs-saeule"
    SOUVERAENITAETS_SAEULE = "souveraenitaets-saeule"


class FundamentVerfahren(str, Enum):
    """Foundation procedure used to anchor the clause."""

    NOTVERFAHREN = "notverfahren"
    REGELVERFAHREN = "regelverfahren"
    PLENARVERFAHREN = "plenarverfahren"


class FundamentKraft(str, Enum):
    """Structural force of the grounded legal pillar."""

    GESPERRT = "gesperrt"
    FUNDIERT = "fundiert"
    TRAGENDES_RECHT = "tragendes-recht"


@dataclass(frozen=True)
class FundamentPfeiler:
    """One load-bearing legal pillar derived from an authority clause."""

    pfeiler_id: str
    sequence: int
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
    dekret_sektion: DekretSektion
    dekret_geltung: DekretGeltung
    dekret_prozedur: DekretProzedur
    saeule: FundamentSaeule
    verfahren: FundamentVerfahren
    kraft: FundamentKraft
    pfeiler_ids: tuple[str, ...]
    load_bearing: bool
    fundament_weight: float
    foundation_depth: int
    pfeiler_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
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
        object.__setattr__(self, "fundament_weight", _clamp01(self.fundament_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.foundation_depth < 1:
            raise ValueError("foundation_depth must be positive")
        if not self.pfeiler_ids:
            raise ValueError("pfeiler_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "pfeiler_id": self.pfeiler_id,
            "sequence": self.sequence,
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
            "dekret_sektion": self.dekret_sektion.value,
            "dekret_geltung": self.dekret_geltung.value,
            "dekret_prozedur": self.dekret_prozedur.value,
            "saeule": self.saeule.value,
            "verfahren": self.verfahren.value,
            "kraft": self.kraft.value,
            "pfeiler_ids": list(self.pfeiler_ids),
            "load_bearing": self.load_bearing,
            "fundament_weight": self.fundament_weight,
            "foundation_depth": self.foundation_depth,
            "pfeiler_tags": list(self.pfeiler_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class RechtsFundament:
    """Legal foundation grounding Leitstern authority clauses as load-bearing pillars."""

    fundament_id: str
    autoritaets_dekret: AutoritaetsDekret
    pfeiler: tuple[FundamentPfeiler, ...]
    fundament_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "fundament_id", _non_empty(self.fundament_id, field_name="fundament_id"))

    @property
    def gesperrt_pfeiler_ids(self) -> tuple[str, ...]:
        return tuple(p.pfeiler_id for p in self.pfeiler if p.kraft is FundamentKraft.GESPERRT)

    @property
    def fundiert_pfeiler_ids(self) -> tuple[str, ...]:
        return tuple(p.pfeiler_id for p in self.pfeiler if p.kraft is FundamentKraft.FUNDIERT)

    @property
    def tragendes_recht_pfeiler_ids(self) -> tuple[str, ...]:
        return tuple(p.pfeiler_id for p in self.pfeiler if p.kraft is FundamentKraft.TRAGENDES_RECHT)

    def to_dict(self) -> dict[str, object]:
        return {
            "fundament_id": self.fundament_id,
            "autoritaets_dekret": self.autoritaets_dekret.to_dict(),
            "pfeiler": [p.to_dict() for p in self.pfeiler],
            "fundament_signal": self.fundament_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "gesperrt_pfeiler_ids": list(self.gesperrt_pfeiler_ids),
            "fundiert_pfeiler_ids": list(self.fundiert_pfeiler_ids),
            "tragendes_recht_pfeiler_ids": list(self.tragendes_recht_pfeiler_ids),
        }


def _saeule(klausel: DekretKlausel) -> FundamentSaeule:
    return {
        DekretSektion.SCHUTZ_SEKTION: FundamentSaeule.SCHUTZ_SAEULE,
        DekretSektion.ORDNUNGS_SEKTION: FundamentSaeule.ORDNUNGS_SAEULE,
        DekretSektion.SOUVERAENITAETS_SEKTION: FundamentSaeule.SOUVERAENITAETS_SAEULE,
    }[klausel.sektion]


def _verfahren(klausel: DekretKlausel) -> FundamentVerfahren:
    return {
        DekretProzedur.NOTPROZEDUR: FundamentVerfahren.NOTVERFAHREN,
        DekretProzedur.REGELPROZEDUR: FundamentVerfahren.REGELVERFAHREN,
        DekretProzedur.PLENARPROZEDUR: FundamentVerfahren.PLENARVERFAHREN,
    }[klausel.prozedur]


def _kraft(klausel: DekretKlausel) -> FundamentKraft:
    return {
        DekretGeltung.GESPERRT: FundamentKraft.GESPERRT,
        DekretGeltung.VERORDNET: FundamentKraft.FUNDIERT,
        DekretGeltung.AUTORITAETSRECHT: FundamentKraft.TRAGENDES_RECHT,
    }[klausel.geltung]


def _fundament_weight(klausel: DekretKlausel) -> float:
    bonus = {
        FundamentKraft.GESPERRT: 0.0,
        FundamentKraft.FUNDIERT: 0.04,
        FundamentKraft.TRAGENDES_RECHT: 0.08,
    }[_kraft(klausel)]
    return round(min(1.0, klausel.dekret_weight + bonus), 3)


def _foundation_depth(klausel: DekretKlausel) -> int:
    return {
        FundamentKraft.GESPERRT: klausel.decree_order,
        FundamentKraft.FUNDIERT: klausel.decree_order + 1,
        FundamentKraft.TRAGENDES_RECHT: klausel.decree_order + 2,
    }[_kraft(klausel)]


def build_rechts_fundament(
    autoritaets_dekret: AutoritaetsDekret | None = None,
    *,
    fundament_id: str = "rechts-fundament",
) -> RechtsFundament:
    """Build the legal foundation grounding Leitstern authority clauses as pillars."""

    resolved_dekret = (
        build_autoritaets_dekret(dekret_id=f"{fundament_id}-dekret")
        if autoritaets_dekret is None
        else autoritaets_dekret
    )
    pfeiler = tuple(
        FundamentPfeiler(
            pfeiler_id=f"{fundament_id}-{k.klausel_id.removeprefix(f'{resolved_dekret.dekret_id}-')}",
            sequence=index,
            klausel_id=k.klausel_id,
            norm_id=k.norm_id,
            abschnitt_id=k.abschnitt_id,
            artikel_id=k.artikel_id,
            mandat_id=k.mandat_id,
            fall_id=k.fall_id,
            line_id=k.line_id,
            article_id=k.article_id,
            entry_id=k.entry_id,
            section_id=k.section_id,
            reference_key=k.reference_key,
            dekret_sektion=k.sektion,
            dekret_geltung=k.geltung,
            dekret_prozedur=k.prozedur,
            saeule=_saeule(k),
            verfahren=_verfahren(k),
            kraft=_kraft(k),
            pfeiler_ids=k.klausel_ids,
            load_bearing=k.decreed and _kraft(k) is FundamentKraft.TRAGENDES_RECHT,
            fundament_weight=_fundament_weight(k),
            foundation_depth=_foundation_depth(k),
            pfeiler_tags=tuple(
                dict.fromkeys(
                    (
                        *k.klausel_tags,
                        _saeule(k).value,
                        _verfahren(k).value,
                        _kraft(k).value,
                    )
                )
            ),
            summary=(
                f"{k.klausel_id} grounded as {_saeule(k).value} via "
                f"{_verfahren(k).value} with kraft {_kraft(k).value}."
            ),
        )
        for index, k in enumerate(resolved_dekret.klauseln, start=1)
    )
    if not pfeiler:
        raise ValueError("rechts fundament requires at least one pfeiler")

    severity = "info"
    status = "fundament-tragendes-recht"
    if any(p.kraft is FundamentKraft.GESPERRT for p in pfeiler):
        severity = "critical"
        status = "fundament-gesperrt"
    elif any(p.kraft is FundamentKraft.FUNDIERT for p in pfeiler):
        severity = "warning"
        status = "fundament-fundiert"

    fundament_signal = TelemetrySignal(
        signal_name="rechts-fundament",
        boundary=resolved_dekret.dekret_signal.boundary,
        correlation_id=fundament_id,
        severity=severity,
        status=status,
        metrics={
            "pfeiler_count": float(len(pfeiler)),
            "gesperrt_count": float(sum(1 for p in pfeiler if p.kraft is FundamentKraft.GESPERRT)),
            "fundiert_count": float(sum(1 for p in pfeiler if p.kraft is FundamentKraft.FUNDIERT)),
            "tragendes_recht_count": float(sum(1 for p in pfeiler if p.kraft is FundamentKraft.TRAGENDES_RECHT)),
            "load_bearing_count": float(sum(1 for p in pfeiler if p.load_bearing)),
            "avg_fundament_weight": round(sum(p.fundament_weight for p in pfeiler) / len(pfeiler), 3),
        },
        labels={"fundament_id": fundament_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_dekret.final_snapshot.runtime_stage,
        signals=(fundament_signal, *resolved_dekret.final_snapshot.signals),
        alerts=resolved_dekret.final_snapshot.alerts,
        audit_entries=resolved_dekret.final_snapshot.audit_entries,
        active_controls=resolved_dekret.final_snapshot.active_controls,
    )
    return RechtsFundament(
        fundament_id=fundament_id,
        autoritaets_dekret=resolved_dekret,
        pfeiler=pfeiler,
        fundament_signal=fundament_signal,
        final_snapshot=final_snapshot,
    )
