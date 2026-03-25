"""#718 — InformatikNorm: Normative Informatik-Standards (*_norm)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.verteilte_systeme_senat import VerteilteSystemeSenat, build_verteilte_systeme_senat


class InformatikNormGeltung(str, Enum):
    GESPERRT = "gesperrt"
    INFO_NORMATIV = "info-normativ"
    GRUNDLEGEND_INFO_NORMATIV = "grundlegend-info-normativ"


class InformatikNormTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class InformatikNormProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}
_GELTUNG_KEY_MAP: dict = {}


@dataclass(frozen=True)
class InformatikNormEintrag:
    norm_id: str
    geltung: InformatikNormGeltung
    typ: InformatikNormTyp
    prozedur: InformatikNormProzedur
    info_norm_weight: float
    info_norm_tier: int
    info_norm_ids: List[str]
    info_norm_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class InformatikNormSatz:
    norm_id: str
    normen: List[InformatikNormEintrag]
    parent: VerteilteSystemeSenat


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        "gesperrt": 0.0,
        "info-normativ": 0.05,
        "grundlegend-info-normativ": 0.1,
    })
    _TIER_DELTA.update({
        "gesperrt": 0,
        "info-normativ": 1,
        "grundlegend-info-normativ": 2,
    })
    _TYP_MAP.update({
        "gesperrt": InformatikNormTyp.BEOBACHTUNG,
        "info-normativ": InformatikNormTyp.ANALYSE,
        "grundlegend-info-normativ": InformatikNormTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        "gesperrt": InformatikNormProzedur.INITIALISIEREN,
        "info-normativ": InformatikNormProzedur.AKTIVIEREN,
        "grundlegend-info-normativ": InformatikNormProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        "verteilt-aktiv": InformatikNormGeltung.INFO_NORMATIV,
        "grundlegend-verteilt-aktiv": InformatikNormGeltung.GRUNDLEGEND_INFO_NORMATIV,
        "gesperrt": InformatikNormGeltung.GESPERRT,
    })
    _GELTUNG_KEY_MAP.update({
        InformatikNormGeltung.GESPERRT: "gesperrt",
        InformatikNormGeltung.INFO_NORMATIV: "info-normativ",
        InformatikNormGeltung.GRUNDLEGEND_INFO_NORMATIV: "grundlegend-info-normativ",
    })


_init_map()


def build_informatik_norm(*, norm_id: str = "informatik-norm") -> InformatikNormSatz:
    parent = build_verteilte_systeme_senat(senat_id=f"{norm_id}-parent")
    eintraege: List[InformatikNormEintrag] = []
    for g in InformatikNormGeltung:
        key = _GELTUNG_KEY_MAP[g]
        eintraege.append(InformatikNormEintrag(
            norm_id=f"{norm_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[key],
            prozedur=_PROZEDUR_MAP[key],
            info_norm_weight=round(sum(n.info_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[key]), 4),
            info_norm_tier=max(n.info_tier for n in parent.normen) + _TIER_DELTA[key],
            info_norm_ids=[f"in-{norm_id}-{g.value}-001", f"in-{norm_id}-{g.value}-002"],
            info_norm_tags=["info", "norm", g.value],
        ))
    return InformatikNormSatz(norm_id=norm_id, normen=eintraege, parent=parent)
