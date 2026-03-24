"""#628 MusikNorm — normative Musikwissenschaft (*_norm pattern, parent: MusikEthnologieSenat)."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List
from .musikethnologie_senat import MusikEthnologieSenat, build_musikethnologie_senat

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class MusikNormTyp(str, Enum):
    ANALYTISCH = "analytisch"
    SYNTHETISCH = "synthetisch"
    HISTORISCH = "historisch"
    KOMPARATIV = "komparativ"


class MusikNormProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


class MusikNormGeltung(str, Enum):
    GESPERRT = "gesperrt"
    MUSIKALISCH_NORMATIV = "musikalisch-normativ"
    GRUNDLEGEND_MUSIKALISCH_NORMATIV = "grundlegend-musikalisch-normativ"


@dataclass(frozen=True)
class MusikNormEintrag:
    norm_id: str
    geltung: MusikNormGeltung
    typ: MusikNormTyp
    prozedur: MusikNormProzedur
    musik_norm_weight: float
    musik_norm_tier: int
    musik_norm_ids: List[str]
    musik_norm_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class MusikNormSatz:
    norm_id: str
    normen: List[MusikNormEintrag]
    parent: MusikEthnologieSenat


_GELTUNG_KEY_MAP: dict = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        "gesperrt": 0.0,
        "musikalisch-normativ": 0.05,
        "grundlegend-musikalisch-normativ": 0.1,
    })
    _TIER_DELTA.update({
        "gesperrt": 0,
        "musikalisch-normativ": 1,
        "grundlegend-musikalisch-normativ": 2,
    })
    _TYP_MAP.update({
        "gesperrt": MusikNormTyp.ANALYTISCH,
        "musikalisch-normativ": MusikNormTyp.SYNTHETISCH,
        "grundlegend-musikalisch-normativ": MusikNormTyp.HISTORISCH,
    })
    _PROZEDUR_MAP.update({
        "gesperrt": MusikNormProzedur.INITIALISIEREN,
        "musikalisch-normativ": MusikNormProzedur.AKTIVIEREN,
        "grundlegend-musikalisch-normativ": MusikNormProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        "musikethnologisch": MusikNormGeltung.MUSIKALISCH_NORMATIV,
        "grundlegend-musikethnologisch": MusikNormGeltung.GRUNDLEGEND_MUSIKALISCH_NORMATIV,
        "gesperrt": MusikNormGeltung.GESPERRT,
    })
    _GELTUNG_KEY_MAP.update({
        MusikNormGeltung.GESPERRT: "gesperrt",
        MusikNormGeltung.MUSIKALISCH_NORMATIV: "musikalisch-normativ",
        MusikNormGeltung.GRUNDLEGEND_MUSIKALISCH_NORMATIV: "grundlegend-musikalisch-normativ",
    })


_init_map()


def build_musik_norm(*, norm_id: str = "musik-norm") -> MusikNormSatz:
    parent = build_musikethnologie_senat(senat_id=f"{norm_id}-parent")
    eintraege: List[MusikNormEintrag] = []
    for g in MusikNormGeltung:
        key = _GELTUNG_KEY_MAP[g]
        eintraege.append(MusikNormEintrag(
            norm_id=f"{norm_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[key],
            prozedur=_PROZEDUR_MAP[key],
            musik_norm_weight=round(sum(n.musik_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[key]), 4),
            musik_norm_tier=max(n.musik_tier for n in parent.normen) + _TIER_DELTA[key],
            musik_norm_ids=[f"mn-{norm_id}-{g.value}-001", f"mn-{norm_id}-{g.value}-002"],
            musik_norm_tags=["musikwissenschaft", "norm", g.value],
        ))
    return MusikNormSatz(norm_id=norm_id, normen=eintraege, parent=parent)
