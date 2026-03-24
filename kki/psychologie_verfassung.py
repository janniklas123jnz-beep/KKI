from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kognitions_charta import KognitionsCharta, KognitionsChartaGeltung, build_kognitions_charta

_WEIGHT_DELTA: dict["PsychologieVerfassungsGeltung", float] = {}
_TIER_DELTA: dict["PsychologieVerfassungsGeltung", int] = {}
_TYP_MAP: dict["PsychologieVerfassungsGeltung", "PsychologieVerfassungsTyp"] = {}
_PROZEDUR_MAP: dict["PsychologieVerfassungsGeltung", "PsychologieVerfassungsProzedur"] = {}
_GELTUNG_MAP: dict[KognitionsChartaGeltung, "PsychologieVerfassungsGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        PsychologieVerfassungsGeltung.GESPERRT: 0.0,
        PsychologieVerfassungsGeltung.PSYCHE_SOUVERAEN: 0.05,
        PsychologieVerfassungsGeltung.GRUNDLEGEND_PSYCHE_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        PsychologieVerfassungsGeltung.GESPERRT: 0,
        PsychologieVerfassungsGeltung.PSYCHE_SOUVERAEN: 1,
        PsychologieVerfassungsGeltung.GRUNDLEGEND_PSYCHE_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        PsychologieVerfassungsGeltung.GESPERRT: PsychologieVerfassungsTyp.SCHUTZ_PSYCHOLOGIEVERFASSUNG,
        PsychologieVerfassungsGeltung.PSYCHE_SOUVERAEN: PsychologieVerfassungsTyp.ORDNUNGS_PSYCHOLOGIEVERFASSUNG,
        PsychologieVerfassungsGeltung.GRUNDLEGEND_PSYCHE_SOUVERAEN: PsychologieVerfassungsTyp.SOUVERAENITAETS_PSYCHOLOGIEVERFASSUNG,
    })
    _PROZEDUR_MAP.update({
        PsychologieVerfassungsGeltung.GESPERRT: PsychologieVerfassungsProzedur.NOTPROZEDUR,
        PsychologieVerfassungsGeltung.PSYCHE_SOUVERAEN: PsychologieVerfassungsProzedur.REGELPROTOKOLL,
        PsychologieVerfassungsGeltung.GRUNDLEGEND_PSYCHE_SOUVERAEN: PsychologieVerfassungsProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        KognitionsChartaGeltung.GESPERRT: PsychologieVerfassungsGeltung.GESPERRT,
        KognitionsChartaGeltung.KOGNITIONS_SOUVERAEN: PsychologieVerfassungsGeltung.PSYCHE_SOUVERAEN,
        KognitionsChartaGeltung.GRUNDLEGEND_KOGNITIONS_SOUVERAEN: PsychologieVerfassungsGeltung.GRUNDLEGEND_PSYCHE_SOUVERAEN,
    })


class PsychologieVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    PSYCHE_SOUVERAEN = "psyche-souverän"
    GRUNDLEGEND_PSYCHE_SOUVERAEN = "grundlegend-psyche-souverän"


class PsychologieVerfassungsTyp(Enum):
    SCHUTZ_PSYCHOLOGIEVERFASSUNG = "schutz-psychologieverfassung"
    ORDNUNGS_PSYCHOLOGIEVERFASSUNG = "ordnungs-psychologieverfassung"
    SOUVERAENITAETS_PSYCHOLOGIEVERFASSUNG = "souveraenitaets-psychologieverfassung"


class PsychologieVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class PsychologieVerfassungsNorm:
    psychologie_verfassung_id: str
    psychologie_typ: PsychologieVerfassungsTyp
    prozedur: PsychologieVerfassungsProzedur
    geltung: PsychologieVerfassungsGeltung
    psychologie_weight: float
    psychologie_tier: int
    canonical: bool
    psychologie_ids: tuple[str, ...]
    psychologie_tags: tuple[str, ...]


@dataclass(frozen=True)
class PsychologieVerfassung:
    verfassung_id: str
    kognitions_charta: KognitionsCharta
    normen: tuple[PsychologieVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.psychologie_verfassung_id for n in self.normen if n.geltung is PsychologieVerfassungsGeltung.GESPERRT)

    @property
    def psyche_souveraen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.psychologie_verfassung_id for n in self.normen if n.geltung is PsychologieVerfassungsGeltung.PSYCHE_SOUVERAEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.psychologie_verfassung_id for n in self.normen if n.geltung is PsychologieVerfassungsGeltung.GRUNDLEGEND_PSYCHE_SOUVERAEN)

    @property
    def verfassung_signal(self):
        if any(n.geltung is PsychologieVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is PsychologieVerfassungsGeltung.PSYCHE_SOUVERAEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-psyche-souveraen")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-psyche-souveraen")


_init_map()


def build_psychologie_verfassung(
    kognitions_charta: KognitionsCharta | None = None,
    *,
    verfassung_id: str = "psychologie-verfassung",
) -> PsychologieVerfassung:
    if kognitions_charta is None:
        kognitions_charta = build_kognitions_charta(charta_id=f"{verfassung_id}-charta")

    normen: list[PsychologieVerfassungsNorm] = []
    for parent_norm in kognitions_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.kognitions_charta_id.removeprefix(f'{kognitions_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.psychologie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.psychologie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is PsychologieVerfassungsGeltung.GRUNDLEGEND_PSYCHE_SOUVERAEN)
        normen.append(
            PsychologieVerfassungsNorm(
                psychologie_verfassung_id=new_id,
                psychologie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                psychologie_weight=new_weight,
                psychologie_tier=new_tier,
                canonical=is_canonical,
                psychologie_ids=parent_norm.psychologie_ids + (new_id,),
                psychologie_tags=parent_norm.psychologie_tags + (f"psychologie-verfassung:{new_geltung.value}",),
            )
        )
    return PsychologieVerfassung(
        verfassung_id=verfassung_id,
        kognitions_charta=kognitions_charta,
        normen=tuple(normen),
    )
