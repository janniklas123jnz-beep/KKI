"""#668 OekologieNorm — normative Ökologiestandards (*_norm pattern, parent: UmweltschutzSenat)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .umweltschutz_senat import UmweltschutzSenat, build_umweltschutz_senat

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class OekologieNormTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"
    SCHUTZ = "schutz"


class OekologieNormProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


class OekologieNormGeltung(str, Enum):
    GESPERRT = "gesperrt"
    OEKOLOGIE_NORMATIV = "oekologie-normativ"
    GRUNDLEGEND_OEKOLOGIE_NORMATIV = "grundlegend-oekologie-normativ"


@dataclass(frozen=True)
class OekologieNormEintrag:
    norm_id: str
    geltung: OekologieNormGeltung
    typ: OekologieNormTyp
    prozedur: OekologieNormProzedur
    oekologie_norm_weight: float
    oekologie_norm_tier: int
    oekologie_norm_ids: List[str]
    oekologie_norm_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class OekologieNormSatz:
    norm_id: str
    normen: List[OekologieNormEintrag]
    parent: UmweltschutzSenat


_GELTUNG_KEY_MAP: dict = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        "gesperrt": 0.0,
        "oekologie-normativ": 0.05,
        "grundlegend-oekologie-normativ": 0.1,
    })
    _TIER_DELTA.update({
        "gesperrt": 0,
        "oekologie-normativ": 1,
        "grundlegend-oekologie-normativ": 2,
    })
    _TYP_MAP.update({
        "gesperrt": OekologieNormTyp.BEOBACHTUNG,
        "oekologie-normativ": OekologieNormTyp.ANALYSE,
        "grundlegend-oekologie-normativ": OekologieNormTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        "gesperrt": OekologieNormProzedur.INITIALISIEREN,
        "oekologie-normativ": OekologieNormProzedur.AKTIVIEREN,
        "grundlegend-oekologie-normativ": OekologieNormProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        "umweltgeschuetzt": OekologieNormGeltung.OEKOLOGIE_NORMATIV,
        "grundlegend-umweltgeschuetzt": OekologieNormGeltung.GRUNDLEGEND_OEKOLOGIE_NORMATIV,
        "gesperrt": OekologieNormGeltung.GESPERRT,
    })
    _GELTUNG_KEY_MAP.update({
        OekologieNormGeltung.GESPERRT: "gesperrt",
        OekologieNormGeltung.OEKOLOGIE_NORMATIV: "oekologie-normativ",
        OekologieNormGeltung.GRUNDLEGEND_OEKOLOGIE_NORMATIV: "grundlegend-oekologie-normativ",
    })


_init_map()


def build_oekologie_norm(*, norm_id: str = "oekologie-norm") -> OekologieNormSatz:
    parent = build_umweltschutz_senat(senat_id=f"{norm_id}-parent")
    eintraege: List[OekologieNormEintrag] = []
    for g in OekologieNormGeltung:
        key = _GELTUNG_KEY_MAP[g]
        eintraege.append(OekologieNormEintrag(
            norm_id=f"{norm_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[key],
            prozedur=_PROZEDUR_MAP[key],
            oekologie_norm_weight=round(sum(n.oekologie_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[key]), 4),
            oekologie_norm_tier=max(n.oekologie_tier for n in parent.normen) + _TIER_DELTA[key],
            oekologie_norm_ids=[f"on-{norm_id}-{g.value}-001", f"on-{norm_id}-{g.value}-002"],
            oekologie_norm_tags=["oekologie", "norm", g.value],
        ))
    return OekologieNormSatz(norm_id=norm_id, normen=eintraege, parent=parent)
