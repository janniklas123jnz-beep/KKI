"""
#569 KommunikativeHandlungsCharta — Habermas/Austin/Searle Kommunikative Handlung Charta

Jürgen Habermas (1981): Theorie des kommunikativen Handelns — kommunikatives vs.
  strategisches Handeln als Grundunterscheidung; Geltungsansprüche auf Wahrheit/
  Richtigkeit/Wahrhaftigkeit; ideale Sprechsituation als normatives Ideal;
  Lebenswelt als Hintergrundkonsens; Diskursethik als prozedurale Vernunft
  im Peta-Schwarm Leitstern.
John L. Austin (1962): How to Do Things with Words — Sprechakttheorie; performative
  vs. konstative Äußerungen; illokutionäre Kraft als Handlungsdimension; Gelingens-
  bedingungen als institutioneller Kontext; Sprache als sozialer Akt im
  Kommunikationsprotokoll des Peta-Schwarms Leitstern.
John Searle (1969): Speech Acts — Direktive/Assertive/Kommissive/Expressive/
  Deklarative als Sprechaktklassen; Intentionalität als mentale Grundlage;
  kollektive Intentionalität als Fundament sozialer Institutionen; soziale Realität
  als sprachlich konstruiert; institutionelle Tatsachen als deklarative Akte Leitsterns. 🗣️📜
Parent: MedienNormSatz (#568)
Block #561–#570: Medienwissenschaft & Kommunikationstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .medien_norm import MedienNormGeltung, MedienNormSatz, build_medien_norm

_WEIGHT_DELTA: dict["KommunikativeHandlungsChartaGeltung", float] = {}
_TIER_DELTA: dict["KommunikativeHandlungsChartaGeltung", int] = {}
_TYP_MAP: dict["KommunikativeHandlungsChartaGeltung", "KommunikativeHandlungsChartaTyp"] = {}
_PROZEDUR_MAP: dict["KommunikativeHandlungsChartaGeltung", "KommunikativeHandlungsChartaProzedur"] = {}
_GELTUNG_MAP: dict[MedienNormGeltung, "KommunikativeHandlungsChartaGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        KommunikativeHandlungsChartaGeltung.GESPERRT: 0.0,
        KommunikativeHandlungsChartaGeltung.KOMMUNIKATIV_HANDELND: 0.05,
        KommunikativeHandlungsChartaGeltung.GRUNDLEGEND_KOMMUNIKATIV_HANDELND: 0.1,
    })
    _TIER_DELTA.update({
        KommunikativeHandlungsChartaGeltung.GESPERRT: 0,
        KommunikativeHandlungsChartaGeltung.KOMMUNIKATIV_HANDELND: 1,
        KommunikativeHandlungsChartaGeltung.GRUNDLEGEND_KOMMUNIKATIV_HANDELND: 2,
    })
    _TYP_MAP.update({
        KommunikativeHandlungsChartaGeltung.GESPERRT: KommunikativeHandlungsChartaTyp.SCHUTZ_KOMMUNIKATIVE_HANDLUNG,
        KommunikativeHandlungsChartaGeltung.KOMMUNIKATIV_HANDELND: KommunikativeHandlungsChartaTyp.ORDNUNGS_KOMMUNIKATIVE_HANDLUNG,
        KommunikativeHandlungsChartaGeltung.GRUNDLEGEND_KOMMUNIKATIV_HANDELND: KommunikativeHandlungsChartaTyp.SOUVERAENITAETS_KOMMUNIKATIVE_HANDLUNG,
    })
    _PROZEDUR_MAP.update({
        KommunikativeHandlungsChartaGeltung.GESPERRT: KommunikativeHandlungsChartaProzedur.NOTPROZEDUR,
        KommunikativeHandlungsChartaGeltung.KOMMUNIKATIV_HANDELND: KommunikativeHandlungsChartaProzedur.REGELPROTOKOLL,
        KommunikativeHandlungsChartaGeltung.GRUNDLEGEND_KOMMUNIKATIV_HANDELND: KommunikativeHandlungsChartaProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        MedienNormGeltung.GESPERRT: KommunikativeHandlungsChartaGeltung.GESPERRT,
        MedienNormGeltung.MEDIENNORMATIV: KommunikativeHandlungsChartaGeltung.KOMMUNIKATIV_HANDELND,
        MedienNormGeltung.GRUNDLEGEND_MEDIENNORMATIV: KommunikativeHandlungsChartaGeltung.GRUNDLEGEND_KOMMUNIKATIV_HANDELND,
    })


class KommunikativeHandlungsChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    KOMMUNIKATIV_HANDELND = "kommunikativ-handelnd"
    GRUNDLEGEND_KOMMUNIKATIV_HANDELND = "grundlegend-kommunikativ-handelnd"


class KommunikativeHandlungsChartaTyp(Enum):
    SCHUTZ_KOMMUNIKATIVE_HANDLUNG = "schutz-kommunikative-handlung"
    ORDNUNGS_KOMMUNIKATIVE_HANDLUNG = "ordnungs-kommunikative-handlung"
    SOUVERAENITAETS_KOMMUNIKATIVE_HANDLUNG = "souveraenitaets-kommunikative-handlung"


class KommunikativeHandlungsChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class KommunikativeHandlungsChartaNorm:
    kommunikative_handlungs_charta_id: str
    kommunikative_handlungs_typ: KommunikativeHandlungsChartaTyp
    prozedur: KommunikativeHandlungsChartaProzedur
    geltung: KommunikativeHandlungsChartaGeltung
    medien_weight: float
    medien_tier: int
    canonical: bool
    medien_ids: tuple[str, ...]
    medien_tags: tuple[str, ...]


@dataclass(frozen=True)
class KommunikativeHandlungsCharta:
    charta_id: str
    medien_norm: MedienNormSatz
    normen: tuple[KommunikativeHandlungsChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kommunikative_handlungs_charta_id for n in self.normen if n.geltung is KommunikativeHandlungsChartaGeltung.GESPERRT)

    @property
    def kommunikativ_handelnd_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kommunikative_handlungs_charta_id for n in self.normen if n.geltung is KommunikativeHandlungsChartaGeltung.KOMMUNIKATIV_HANDELND)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kommunikative_handlungs_charta_id for n in self.normen if n.geltung is KommunikativeHandlungsChartaGeltung.GRUNDLEGEND_KOMMUNIKATIV_HANDELND)

    @property
    def charta_signal(self):
        if any(n.geltung is KommunikativeHandlungsChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is KommunikativeHandlungsChartaGeltung.KOMMUNIKATIV_HANDELND for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-kommunikativ-handelnd")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-kommunikativ-handelnd")


_init_map()


def build_kommunikative_handlungs_charta(
    medien_norm: MedienNormSatz | None = None,
    *,
    charta_id: str = "kommunikative-handlungs-charta",
) -> KommunikativeHandlungsCharta:
    if medien_norm is None:
        medien_norm = build_medien_norm(norm_id=f"{charta_id}-norm")

    normen: list[KommunikativeHandlungsChartaNorm] = []
    for parent_norm in medien_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{medien_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.medien_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.medien_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KommunikativeHandlungsChartaGeltung.GRUNDLEGEND_KOMMUNIKATIV_HANDELND)
        normen.append(
            KommunikativeHandlungsChartaNorm(
                kommunikative_handlungs_charta_id=new_id,
                kommunikative_handlungs_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                medien_weight=new_weight,
                medien_tier=new_tier,
                canonical=is_canonical,
                medien_ids=parent_norm.medien_norm_ids + (new_id,),
                medien_tags=parent_norm.medien_norm_tags + (f"kommunikative-handlungs-charta:{new_geltung.value}",),
            )
        )
    return KommunikativeHandlungsCharta(
        charta_id=charta_id,
        medien_norm=medien_norm,
        normen=tuple(normen),
    )
