"""#638 LiteraturNorm — normative Literaturwissenschaft (*_norm pattern, parent: KomparatistikSenat)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .komparatistik_senat import KomparatistikSenat, build_komparatistik_senat

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class LiteraturNormTyp(str, Enum):
    ANALYTISCH = "analytisch"
    SYNTHETISCH = "synthetisch"
    HISTORISCH = "historisch"
    KOMPARATIV = "komparativ"


class LiteraturNormProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


class LiteraturNormGeltung(str, Enum):
    GESPERRT = "gesperrt"
    LITERARISCH_NORMATIV = "literarisch-normativ"
    GRUNDLEGEND_LITERARISCH_NORMATIV = "grundlegend-literarisch-normativ"


@dataclass(frozen=True)
class LiteraturNormEintrag:
    norm_id: str
    geltung: LiteraturNormGeltung
    typ: LiteraturNormTyp
    prozedur: LiteraturNormProzedur
    literatur_norm_weight: float
    literatur_norm_tier: int
    literatur_norm_ids: List[str]
    literatur_norm_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class LiteraturNormSatz:
    norm_id: str
    normen: List[LiteraturNormEintrag]
    parent: KomparatistikSenat


_GELTUNG_KEY_MAP: dict = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        "gesperrt": 0.0,
        "literarisch-normativ": 0.05,
        "grundlegend-literarisch-normativ": 0.1,
    })
    _TIER_DELTA.update({
        "gesperrt": 0,
        "literarisch-normativ": 1,
        "grundlegend-literarisch-normativ": 2,
    })
    _TYP_MAP.update({
        "gesperrt": LiteraturNormTyp.ANALYTISCH,
        "literarisch-normativ": LiteraturNormTyp.SYNTHETISCH,
        "grundlegend-literarisch-normativ": LiteraturNormTyp.HISTORISCH,
    })
    _PROZEDUR_MAP.update({
        "gesperrt": LiteraturNormProzedur.INITIALISIEREN,
        "literarisch-normativ": LiteraturNormProzedur.AKTIVIEREN,
        "grundlegend-literarisch-normativ": LiteraturNormProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        "komparatistisch": LiteraturNormGeltung.LITERARISCH_NORMATIV,
        "grundlegend-komparatistisch": LiteraturNormGeltung.GRUNDLEGEND_LITERARISCH_NORMATIV,
        "gesperrt": LiteraturNormGeltung.GESPERRT,
    })
    _GELTUNG_KEY_MAP.update({
        LiteraturNormGeltung.GESPERRT: "gesperrt",
        LiteraturNormGeltung.LITERARISCH_NORMATIV: "literarisch-normativ",
        LiteraturNormGeltung.GRUNDLEGEND_LITERARISCH_NORMATIV: "grundlegend-literarisch-normativ",
    })


_init_map()


def build_literatur_norm(*, norm_id: str = "literatur-norm") -> LiteraturNormSatz:
    parent = build_komparatistik_senat(senat_id=f"{norm_id}-parent")
    eintraege: List[LiteraturNormEintrag] = []
    for g in LiteraturNormGeltung:
        key = _GELTUNG_KEY_MAP[g]
        eintraege.append(LiteraturNormEintrag(
            norm_id=f"{norm_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[key],
            prozedur=_PROZEDUR_MAP[key],
            literatur_norm_weight=round(sum(n.literatur_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[key]), 4),
            literatur_norm_tier=max(n.literatur_tier for n in parent.normen) + _TIER_DELTA[key],
            literatur_norm_ids=[f"ln-{norm_id}-{g.value}-001", f"ln-{norm_id}-{g.value}-002"],
            literatur_norm_tags=["literaturwissenschaft", "norm", g.value],
        ))
    return LiteraturNormSatz(norm_id=norm_id, normen=eintraege, parent=parent)
