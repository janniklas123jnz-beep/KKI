"""Grundrechts charta encoding senate resolutions into supreme Leitstern charter articles."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .verfassungs_senat import (
    SenatsBeschluss,
    SenatsFraktion,
    SenatsSitzung,
    SenatsMandat,
    VerfassungsSenat,
    build_verfassungs_senat,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class ChartaKapitel(str, Enum):
    """Charter chapter that encodes one senate mandate."""

    SCHUTZ_KAPITEL = "schutz-kapitel"
    ORDNUNGS_KAPITEL = "ordnungs-kapitel"
    SOUVERAENITAETS_KAPITEL = "souveraenitaets-kapitel"


class ChartaVerfahren(str, Enum):
    """Registration procedure used to encode the mandate."""

    DRINGLICHE_EINTRAGUNG = "dringliche-eintragung"
    ORDENTLICHE_EINTRAGUNG = "ordentliche-eintragung"
    PLENARE_EINTRAGUNG = "plenare-eintragung"


class ChartaGeltung(str, Enum):
    """Legal force of the encoded charter article."""

    AUSGESETZT = "ausgesetzt"
    GELTEND = "geltend"
    GRUNDRECHT = "grundrecht"


@dataclass(frozen=True)
class ChartaArtikel:
    """One charter article derived from a senate mandate."""

    artikel_id: str
    sequence: int
    mandat_id: str
    fall_id: str
    line_id: str
    article_id: str
    entry_id: str
    section_id: str
    reference_key: str
    senat_fraktion: SenatsFraktion
    senat_beschluss: SenatsBeschluss
    senat_sitzung: SenatsSitzung
    kapitel: ChartaKapitel
    verfahren: ChartaVerfahren
    geltung: ChartaGeltung
    artikel_ids: tuple[str, ...]
    enforceable: bool
    codex_weight: float
    ratification_depth: int
    artikel_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "artikel_id", _non_empty(self.artikel_id, field_name="artikel_id"))
        object.__setattr__(self, "mandat_id", _non_empty(self.mandat_id, field_name="mandat_id"))
        object.__setattr__(self, "fall_id", _non_empty(self.fall_id, field_name="fall_id"))
        object.__setattr__(self, "line_id", _non_empty(self.line_id, field_name="line_id"))
        object.__setattr__(self, "article_id", _non_empty(self.article_id, field_name="article_id"))
        object.__setattr__(self, "entry_id", _non_empty(self.entry_id, field_name="entry_id"))
        object.__setattr__(self, "section_id", _non_empty(self.section_id, field_name="section_id"))
        object.__setattr__(self, "reference_key", _non_empty(self.reference_key, field_name="reference_key"))
        object.__setattr__(self, "codex_weight", _clamp01(self.codex_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if self.ratification_depth < 1:
            raise ValueError("ratification_depth must be positive")
        if not self.artikel_ids:
            raise ValueError("artikel_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "artikel_id": self.artikel_id,
            "sequence": self.sequence,
            "mandat_id": self.mandat_id,
            "fall_id": self.fall_id,
            "line_id": self.line_id,
            "article_id": self.article_id,
            "entry_id": self.entry_id,
            "section_id": self.section_id,
            "reference_key": self.reference_key,
            "senat_fraktion": self.senat_fraktion.value,
            "senat_beschluss": self.senat_beschluss.value,
            "senat_sitzung": self.senat_sitzung.value,
            "kapitel": self.kapitel.value,
            "verfahren": self.verfahren.value,
            "geltung": self.geltung.value,
            "artikel_ids": list(self.artikel_ids),
            "enforceable": self.enforceable,
            "codex_weight": self.codex_weight,
            "ratification_depth": self.ratification_depth,
            "artikel_tags": list(self.artikel_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class GrundrechtsCharta:
    """Charter encoding the Leitstern senate resolutions into supreme fundamental rights."""

    charta_id: str
    verfassungs_senat: VerfassungsSenat
    artikel: tuple[ChartaArtikel, ...]
    charta_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "charta_id", _non_empty(self.charta_id, field_name="charta_id"))

    @property
    def ausgesetzt_artikel_ids(self) -> tuple[str, ...]:
        return tuple(a.artikel_id for a in self.artikel if a.geltung is ChartaGeltung.AUSGESETZT)

    @property
    def geltend_artikel_ids(self) -> tuple[str, ...]:
        return tuple(a.artikel_id for a in self.artikel if a.geltung is ChartaGeltung.GELTEND)

    @property
    def grundrecht_artikel_ids(self) -> tuple[str, ...]:
        return tuple(a.artikel_id for a in self.artikel if a.geltung is ChartaGeltung.GRUNDRECHT)

    def to_dict(self) -> dict[str, object]:
        return {
            "charta_id": self.charta_id,
            "verfassungs_senat": self.verfassungs_senat.to_dict(),
            "artikel": [a.to_dict() for a in self.artikel],
            "charta_signal": self.charta_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "ausgesetzt_artikel_ids": list(self.ausgesetzt_artikel_ids),
            "geltend_artikel_ids": list(self.geltend_artikel_ids),
            "grundrecht_artikel_ids": list(self.grundrecht_artikel_ids),
        }


def _kapitel(mandat: SenatsMandat) -> ChartaKapitel:
    return {
        SenatsFraktion.SCHUTZ_FRAKTION: ChartaKapitel.SCHUTZ_KAPITEL,
        SenatsFraktion.ORDNUNGS_FRAKTION: ChartaKapitel.ORDNUNGS_KAPITEL,
        SenatsFraktion.SOUVERAENITAETS_FRAKTION: ChartaKapitel.SOUVERAENITAETS_KAPITEL,
    }[mandat.fraktion]


def _verfahren(mandat: SenatsMandat) -> ChartaVerfahren:
    return {
        SenatsSitzung.DRINGLICH_SITZUNG: ChartaVerfahren.DRINGLICHE_EINTRAGUNG,
        SenatsSitzung.ORDENTLICHE_SITZUNG: ChartaVerfahren.ORDENTLICHE_EINTRAGUNG,
        SenatsSitzung.PLENARSITZUNG: ChartaVerfahren.PLENARE_EINTRAGUNG,
    }[mandat.sitzung]


def _geltung(mandat: SenatsMandat) -> ChartaGeltung:
    return {
        SenatsBeschluss.UNGUELTIG: ChartaGeltung.AUSGESETZT,
        SenatsBeschluss.WIRKSAM: ChartaGeltung.GELTEND,
        SenatsBeschluss.GRUNDLEGEND: ChartaGeltung.GRUNDRECHT,
    }[mandat.beschluss]


def _codex_weight(mandat: SenatsMandat) -> float:
    bonus = {
        ChartaGeltung.AUSGESETZT: 0.0,
        ChartaGeltung.GELTEND: 0.04,
        ChartaGeltung.GRUNDRECHT: 0.08,
    }[_geltung(mandat)]
    return round(min(1.0, mandat.resolution_weight + bonus), 3)


def _ratification_depth(mandat: SenatsMandat) -> int:
    return {
        ChartaGeltung.AUSGESETZT: mandat.deliberation_quorum,
        ChartaGeltung.GELTEND: mandat.deliberation_quorum + 1,
        ChartaGeltung.GRUNDRECHT: mandat.deliberation_quorum + 2,
    }[_geltung(mandat)]


def build_grundrechts_charta(
    verfassungs_senat: VerfassungsSenat | None = None,
    *,
    charta_id: str = "grundrechts-charta",
) -> GrundrechtsCharta:
    """Build the fundamental rights charter encoding the Leitstern senate resolutions."""

    resolved_senat = (
        build_verfassungs_senat(senat_id=f"{charta_id}-senat")
        if verfassungs_senat is None
        else verfassungs_senat
    )
    artikel = tuple(
        ChartaArtikel(
            artikel_id=f"{charta_id}-{mandat.mandat_id.removeprefix(f'{resolved_senat.senat_id}-')}",
            sequence=index,
            mandat_id=mandat.mandat_id,
            fall_id=mandat.fall_id,
            line_id=mandat.line_id,
            article_id=mandat.article_id,
            entry_id=mandat.entry_id,
            section_id=mandat.section_id,
            reference_key=mandat.reference_key,
            senat_fraktion=mandat.fraktion,
            senat_beschluss=mandat.beschluss,
            senat_sitzung=mandat.sitzung,
            kapitel=_kapitel(mandat),
            verfahren=_verfahren(mandat),
            geltung=_geltung(mandat),
            artikel_ids=mandat.mandate_ids,
            enforceable=mandat.binding and _geltung(mandat) is ChartaGeltung.GRUNDRECHT,
            codex_weight=_codex_weight(mandat),
            ratification_depth=_ratification_depth(mandat),
            artikel_tags=tuple(
                dict.fromkeys(
                    (
                        *mandat.mandat_tags,
                        _kapitel(mandat).value,
                        _verfahren(mandat).value,
                        _geltung(mandat).value,
                    )
                )
            ),
            summary=(
                f"{mandat.mandat_id} encoded in {_kapitel(mandat).value} via "
                f"{_verfahren(mandat).value} with geltung {_geltung(mandat).value}."
            ),
        )
        for index, mandat in enumerate(resolved_senat.mandate, start=1)
    )
    if not artikel:
        raise ValueError("grundrechts charta requires at least one artikel")

    severity = "info"
    status = "charta-grundrecht"
    if any(a.geltung is ChartaGeltung.AUSGESETZT for a in artikel):
        severity = "critical"
        status = "charta-ausgesetzt"
    elif any(a.geltung is ChartaGeltung.GELTEND for a in artikel):
        severity = "warning"
        status = "charta-geltend"

    charta_signal = TelemetrySignal(
        signal_name="grundrechts-charta",
        boundary=resolved_senat.senat_signal.boundary,
        correlation_id=charta_id,
        severity=severity,
        status=status,
        metrics={
            "artikel_count": float(len(artikel)),
            "ausgesetzt_count": float(sum(1 for a in artikel if a.geltung is ChartaGeltung.AUSGESETZT)),
            "geltend_count": float(sum(1 for a in artikel if a.geltung is ChartaGeltung.GELTEND)),
            "grundrecht_count": float(sum(1 for a in artikel if a.geltung is ChartaGeltung.GRUNDRECHT)),
            "enforceable_count": float(sum(1 for a in artikel if a.enforceable)),
            "avg_codex_weight": round(sum(a.codex_weight for a in artikel) / len(artikel), 3),
        },
        labels={"charta_id": charta_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_senat.final_snapshot.runtime_stage,
        signals=(charta_signal, *resolved_senat.final_snapshot.signals),
        alerts=resolved_senat.final_snapshot.alerts,
        audit_entries=resolved_senat.final_snapshot.audit_entries,
        active_controls=resolved_senat.final_snapshot.active_controls,
    )
    return GrundrechtsCharta(
        charta_id=charta_id,
        verfassungs_senat=resolved_senat,
        artikel=artikel,
        charta_signal=charta_signal,
        final_snapshot=final_snapshot,
    )
