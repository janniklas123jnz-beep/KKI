"""#708 — BiologieNorm: Normative Biologie-Standards (*_norm)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.immunologie_senat import ImmunologieSenat, build_immunologie_senat


class BiologieNormGeltung(str, Enum):
    GESPERRT = "gesperrt"
    BIO_NORMATIV = "bio-normativ"
    GRUNDLEGEND_BIO_NORMATIV = "grundlegend-bio-normativ"


class BiologieNormTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class BiologieNormProzedur(str, Enum):
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
class BiologieNormEintrag:
    norm_id: str
    geltung: BiologieNormGeltung
    typ: BiologieNormTyp
    prozedur: BiologieNormProzedur
    bio_norm_weight: float
    bio_norm_tier: int
    bio_norm_ids: List[str]
    bio_norm_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class BiologieNormSatz:
    norm_id: str
    normen: List[BiologieNormEintrag]
    parent: ImmunologieSenat


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        "gesperrt": 0.0,
        "bio-normativ": 0.05,
        "grundlegend-bio-normativ": 0.1,
    })
    _TIER_DELTA.update({
        "gesperrt": 0,
        "bio-normativ": 1,
        "grundlegend-bio-normativ": 2,
    })
    _TYP_MAP.update({
        "gesperrt": BiologieNormTyp.BEOBACHTUNG,
        "bio-normativ": BiologieNormTyp.ANALYSE,
        "grundlegend-bio-normativ": BiologieNormTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        "gesperrt": BiologieNormProzedur.INITIALISIEREN,
        "bio-normativ": BiologieNormProzedur.AKTIVIEREN,
        "grundlegend-bio-normativ": BiologieNormProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        "immunologisch-aktiv": BiologieNormGeltung.BIO_NORMATIV,
        "grundlegend-immunologisch-aktiv": BiologieNormGeltung.GRUNDLEGEND_BIO_NORMATIV,
        "gesperrt": BiologieNormGeltung.GESPERRT,
    })
    _GELTUNG_KEY_MAP.update({
        BiologieNormGeltung.GESPERRT: "gesperrt",
        BiologieNormGeltung.BIO_NORMATIV: "bio-normativ",
        BiologieNormGeltung.GRUNDLEGEND_BIO_NORMATIV: "grundlegend-bio-normativ",
    })


_init_map()


def build_biologie_norm(*, norm_id: str = "biologie-norm") -> BiologieNormSatz:
    parent = build_immunologie_senat(senat_id=f"{norm_id}-parent")
    eintraege: List[BiologieNormEintrag] = []
    for g in BiologieNormGeltung:
        key = _GELTUNG_KEY_MAP[g]
        eintraege.append(BiologieNormEintrag(
            norm_id=f"{norm_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[key],
            prozedur=_PROZEDUR_MAP[key],
            bio_norm_weight=round(sum(n.bio_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[key]), 4),
            bio_norm_tier=max(n.bio_tier for n in parent.normen) + _TIER_DELTA[key],
            bio_norm_ids=[f"bn-{norm_id}-{g.value}-001", f"bn-{norm_id}-{g.value}-002"],
            bio_norm_tags=["bio", "norm", g.value],
        ))
    return BiologieNormSatz(norm_id=norm_id, normen=eintraege, parent=parent)
