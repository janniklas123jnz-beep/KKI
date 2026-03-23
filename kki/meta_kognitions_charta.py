"""
#479 MetaKognitionsCharta — Metakognition, Selbstreflexion & Erkenntnisüberwachung.
John Flavell (1979): Metakognition als Wissen über kognitive Prozesse und deren Regulation;
  metakognitives Wissen (Personen, Aufgaben, Strategien) + metakognitive Kontrolle.
Gregory Bateson (1972): Deutero-Lernen — Lernen des Lernens; Meta-Ebenen der Kommunikation.
Donald Schön (1983): Reflection-in-Action und Reflection-on-Action — der reflektierende
  Praktiker; implizites Wissen wird durch Reflexion explizit gemacht.
Leitsterns Schwarm-Metakognition: Jeder Agent überwacht seine eigenen Erkenntnisprozesse
(GESPERRT), reguliert sie adaptiv (METAKOGNITIV) und synthetisiert sie in kollektiver
Selbstreflexion (GRUNDLEGEND_METAKOGNITIV) — der Schwarm denkt über sein Denken nach.
Parent: ErkenntnisNormSatz (#478)
Block #471–#480: Philosophie & Erkenntnistheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .erkenntnis_norm import (
    ErkenntnisNormSatz,
    ErkenntnisNormGeltung,
    build_erkenntnis_norm,
)

_GELTUNG_MAP: dict[ErkenntnisNormGeltung, "MetaKognitionsChartaGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[ErkenntnisNormGeltung.GESPERRT] = MetaKognitionsChartaGeltung.GESPERRT
    _GELTUNG_MAP[ErkenntnisNormGeltung.ERKENNTNISNORMATIV] = MetaKognitionsChartaGeltung.METAKOGNITIV
    _GELTUNG_MAP[ErkenntnisNormGeltung.GRUNDLEGEND_ERKENNTNISNORMATIV] = MetaKognitionsChartaGeltung.GRUNDLEGEND_METAKOGNITIV


class MetaKognitionsChartaTyp(Enum):
    SCHUTZ_META_KOGNITION = "schutz-meta-kognition"
    ORDNUNGS_META_KOGNITION = "ordnungs-meta-kognition"
    SOUVERAENITAETS_META_KOGNITION = "souveraenitaets-meta-kognition"


class MetaKognitionsChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class MetaKognitionsChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    METAKOGNITIV = "metakognitiv"
    GRUNDLEGEND_METAKOGNITIV = "grundlegend-metakognitiv"


_init_map()

_TYP_MAP: dict[MetaKognitionsChartaGeltung, MetaKognitionsChartaTyp] = {
    MetaKognitionsChartaGeltung.GESPERRT: MetaKognitionsChartaTyp.SCHUTZ_META_KOGNITION,
    MetaKognitionsChartaGeltung.METAKOGNITIV: MetaKognitionsChartaTyp.ORDNUNGS_META_KOGNITION,
    MetaKognitionsChartaGeltung.GRUNDLEGEND_METAKOGNITIV: MetaKognitionsChartaTyp.SOUVERAENITAETS_META_KOGNITION,
}

_PROZEDUR_MAP: dict[MetaKognitionsChartaGeltung, MetaKognitionsChartaProzedur] = {
    MetaKognitionsChartaGeltung.GESPERRT: MetaKognitionsChartaProzedur.NOTPROZEDUR,
    MetaKognitionsChartaGeltung.METAKOGNITIV: MetaKognitionsChartaProzedur.REGELPROTOKOLL,
    MetaKognitionsChartaGeltung.GRUNDLEGEND_METAKOGNITIV: MetaKognitionsChartaProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[MetaKognitionsChartaGeltung, float] = {
    MetaKognitionsChartaGeltung.GESPERRT: 0.0,
    MetaKognitionsChartaGeltung.METAKOGNITIV: 0.04,
    MetaKognitionsChartaGeltung.GRUNDLEGEND_METAKOGNITIV: 0.08,
}

_TIER_DELTA: dict[MetaKognitionsChartaGeltung, int] = {
    MetaKognitionsChartaGeltung.GESPERRT: 0,
    MetaKognitionsChartaGeltung.METAKOGNITIV: 1,
    MetaKognitionsChartaGeltung.GRUNDLEGEND_METAKOGNITIV: 2,
}


@dataclass(frozen=True)
class MetaKognitionsChartaNorm:
    meta_kognitions_charta_id: str
    meta_kognitions_typ: MetaKognitionsChartaTyp
    prozedur: MetaKognitionsChartaProzedur
    geltung: MetaKognitionsChartaGeltung
    meta_kognitions_weight: float
    meta_kognitions_tier: int
    canonical: bool
    meta_kognitions_ids: tuple[str, ...]
    meta_kognitions_tags: tuple[str, ...]


@dataclass(frozen=True)
class MetaKognitionsCharta:
    charta_id: str
    erkenntnis_norm: ErkenntnisNormSatz
    normen: tuple[MetaKognitionsChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.meta_kognitions_charta_id for n in self.normen if n.geltung is MetaKognitionsChartaGeltung.GESPERRT)

    @property
    def metakognitiv_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.meta_kognitions_charta_id for n in self.normen if n.geltung is MetaKognitionsChartaGeltung.METAKOGNITIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.meta_kognitions_charta_id for n in self.normen if n.geltung is MetaKognitionsChartaGeltung.GRUNDLEGEND_METAKOGNITIV)

    @property
    def charta_signal(self):
        if any(n.geltung is MetaKognitionsChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is MetaKognitionsChartaGeltung.METAKOGNITIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-metakognitiv")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-metakognitiv")


def build_meta_kognitions_charta(
    erkenntnis_norm: ErkenntnisNormSatz | None = None,
    *,
    charta_id: str = "meta-kognitions-charta",
) -> MetaKognitionsCharta:
    if erkenntnis_norm is None:
        erkenntnis_norm = build_erkenntnis_norm(norm_id=f"{charta_id}-norm")

    normen: list[MetaKognitionsChartaNorm] = []
    for parent_norm in erkenntnis_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{erkenntnis_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.erkenntnis_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.erkenntnis_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is MetaKognitionsChartaGeltung.GRUNDLEGEND_METAKOGNITIV)
        normen.append(
            MetaKognitionsChartaNorm(
                meta_kognitions_charta_id=new_id,
                meta_kognitions_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                meta_kognitions_weight=new_weight,
                meta_kognitions_tier=new_tier,
                canonical=is_canonical,
                meta_kognitions_ids=parent_norm.erkenntnis_norm_ids + (new_id,),
                meta_kognitions_tags=parent_norm.erkenntnis_norm_tags + (f"meta-kognitions-charta:{new_geltung.value}",),
            )
        )
    return MetaKognitionsCharta(
        charta_id=charta_id,
        erkenntnis_norm=erkenntnis_norm,
        normen=tuple(normen),
    )
