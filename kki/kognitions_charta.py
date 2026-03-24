from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .psychologie_norm import PsychologieNormGeltung, PsychologieNormSatz, build_psychologie_norm

_WEIGHT_DELTA: dict["KognitionsChartaGeltung", float] = {}
_TIER_DELTA: dict["KognitionsChartaGeltung", int] = {}
_TYP_MAP: dict["KognitionsChartaGeltung", "KognitionsChartaTyp"] = {}
_PROZEDUR_MAP: dict["KognitionsChartaGeltung", "KognitionsChartaProzedur"] = {}
_GELTUNG_MAP: dict[PsychologieNormGeltung, "KognitionsChartaGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        KognitionsChartaGeltung.GESPERRT: 0.0,
        KognitionsChartaGeltung.KOGNITIONS_SOUVERAEN: 0.05,
        KognitionsChartaGeltung.GRUNDLEGEND_KOGNITIONS_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        KognitionsChartaGeltung.GESPERRT: 0,
        KognitionsChartaGeltung.KOGNITIONS_SOUVERAEN: 1,
        KognitionsChartaGeltung.GRUNDLEGEND_KOGNITIONS_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        KognitionsChartaGeltung.GESPERRT: KognitionsChartaTyp.SCHUTZ_KOGNITIONSCHARTA,
        KognitionsChartaGeltung.KOGNITIONS_SOUVERAEN: KognitionsChartaTyp.ORDNUNGS_KOGNITIONSCHARTA,
        KognitionsChartaGeltung.GRUNDLEGEND_KOGNITIONS_SOUVERAEN: KognitionsChartaTyp.SOUVERAENITAETS_KOGNITIONSCHARTA,
    })
    _PROZEDUR_MAP.update({
        KognitionsChartaGeltung.GESPERRT: KognitionsChartaProzedur.NOTPROZEDUR,
        KognitionsChartaGeltung.KOGNITIONS_SOUVERAEN: KognitionsChartaProzedur.REGELPROTOKOLL,
        KognitionsChartaGeltung.GRUNDLEGEND_KOGNITIONS_SOUVERAEN: KognitionsChartaProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        PsychologieNormGeltung.GESPERRT: KognitionsChartaGeltung.GESPERRT,
        PsychologieNormGeltung.PSYCHOLOGISCH_NORMATIV: KognitionsChartaGeltung.KOGNITIONS_SOUVERAEN,
        PsychologieNormGeltung.GRUNDLEGEND_PSYCHOLOGISCH_NORMATIV: KognitionsChartaGeltung.GRUNDLEGEND_KOGNITIONS_SOUVERAEN,
    })


class KognitionsChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    KOGNITIONS_SOUVERAEN = "kognitions-souverän"
    GRUNDLEGEND_KOGNITIONS_SOUVERAEN = "grundlegend-kognitions-souverän"


class KognitionsChartaTyp(Enum):
    SCHUTZ_KOGNITIONSCHARTA = "schutz-kognitionscharta"
    ORDNUNGS_KOGNITIONSCHARTA = "ordnungs-kognitionscharta"
    SOUVERAENITAETS_KOGNITIONSCHARTA = "souveraenitaets-kognitionscharta"


class KognitionsChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class KognitionsChartaNorm:
    kognitions_charta_id: str
    psychologie_typ: KognitionsChartaTyp
    prozedur: KognitionsChartaProzedur
    geltung: KognitionsChartaGeltung
    psychologie_weight: float
    psychologie_tier: int
    canonical: bool
    psychologie_ids: tuple[str, ...]
    psychologie_tags: tuple[str, ...]


@dataclass(frozen=True)
class KognitionsCharta:
    charta_id: str
    psychologie_norm: PsychologieNormSatz
    normen: tuple[KognitionsChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kognitions_charta_id for n in self.normen if n.geltung is KognitionsChartaGeltung.GESPERRT)

    @property
    def kognitions_souveraen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kognitions_charta_id for n in self.normen if n.geltung is KognitionsChartaGeltung.KOGNITIONS_SOUVERAEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kognitions_charta_id for n in self.normen if n.geltung is KognitionsChartaGeltung.GRUNDLEGEND_KOGNITIONS_SOUVERAEN)

    @property
    def charta_signal(self):
        if any(n.geltung is KognitionsChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is KognitionsChartaGeltung.KOGNITIONS_SOUVERAEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-kognitions-souveraen")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-kognitions-souveraen")


_init_map()


def build_kognitions_charta(
    psychologie_norm: PsychologieNormSatz | None = None,
    *,
    charta_id: str = "kognitions-charta",
) -> KognitionsCharta:
    if psychologie_norm is None:
        psychologie_norm = build_psychologie_norm(norm_id=f"{charta_id}-norm")

    normen: list[KognitionsChartaNorm] = []
    for parent_norm in psychologie_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{psychologie_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.psychologie_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.psychologie_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KognitionsChartaGeltung.GRUNDLEGEND_KOGNITIONS_SOUVERAEN)
        normen.append(
            KognitionsChartaNorm(
                kognitions_charta_id=new_id,
                psychologie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                psychologie_weight=new_weight,
                psychologie_tier=new_tier,
                canonical=is_canonical,
                psychologie_ids=parent_norm.psychologie_norm_ids + (new_id,),
                psychologie_tags=parent_norm.psychologie_norm_tags + (f"kognitions-charta:{new_geltung.value}",),
            )
        )
    return KognitionsCharta(
        charta_id=charta_id,
        psychologie_norm=psychologie_norm,
        normen=tuple(normen),
    )
