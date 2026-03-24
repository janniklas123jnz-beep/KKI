"""#648 MedizinNorm — normative Medizin & Gesundheitsstandards (*_norm pattern, parent: PharmazieSenat)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .pharmazie_senat import PharmazieSenat, build_pharmazie_senat

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class MedizinNormTyp(str, Enum):
    KLINISCH = "klinisch"
    THEORETISCH = "theoretisch"
    ANGEWANDT = "angewandt"
    PRAEVENTIV = "praeventiv"


class MedizinNormProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


class MedizinNormGeltung(str, Enum):
    GESPERRT = "gesperrt"
    MEDIZINISCH_NORMATIV = "medizinisch-normativ"
    GRUNDLEGEND_MEDIZINISCH_NORMATIV = "grundlegend-medizinisch-normativ"


@dataclass(frozen=True)
class MedizinNormEintrag:
    norm_id: str
    geltung: MedizinNormGeltung
    typ: MedizinNormTyp
    prozedur: MedizinNormProzedur
    medizin_norm_weight: float
    medizin_norm_tier: int
    medizin_norm_ids: List[str]
    medizin_norm_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class MedizinNormSatz:
    norm_id: str
    normen: List[MedizinNormEintrag]
    parent: PharmazieSenat


_GELTUNG_KEY_MAP: dict = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        "gesperrt": 0.0,
        "medizinisch-normativ": 0.05,
        "grundlegend-medizinisch-normativ": 0.1,
    })
    _TIER_DELTA.update({
        "gesperrt": 0,
        "medizinisch-normativ": 1,
        "grundlegend-medizinisch-normativ": 2,
    })
    _TYP_MAP.update({
        "gesperrt": MedizinNormTyp.KLINISCH,
        "medizinisch-normativ": MedizinNormTyp.THEORETISCH,
        "grundlegend-medizinisch-normativ": MedizinNormTyp.ANGEWANDT,
    })
    _PROZEDUR_MAP.update({
        "gesperrt": MedizinNormProzedur.INITIALISIEREN,
        "medizinisch-normativ": MedizinNormProzedur.AKTIVIEREN,
        "grundlegend-medizinisch-normativ": MedizinNormProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        "pharmazeutisch": MedizinNormGeltung.MEDIZINISCH_NORMATIV,
        "grundlegend-pharmazeutisch": MedizinNormGeltung.GRUNDLEGEND_MEDIZINISCH_NORMATIV,
        "gesperrt": MedizinNormGeltung.GESPERRT,
    })
    _GELTUNG_KEY_MAP.update({
        MedizinNormGeltung.GESPERRT: "gesperrt",
        MedizinNormGeltung.MEDIZINISCH_NORMATIV: "medizinisch-normativ",
        MedizinNormGeltung.GRUNDLEGEND_MEDIZINISCH_NORMATIV: "grundlegend-medizinisch-normativ",
    })


_init_map()


def build_medizin_norm(*, norm_id: str = "medizin-norm") -> MedizinNormSatz:
    parent = build_pharmazie_senat(senat_id=f"{norm_id}-parent")
    eintraege: List[MedizinNormEintrag] = []
    for g in MedizinNormGeltung:
        key = _GELTUNG_KEY_MAP[g]
        eintraege.append(MedizinNormEintrag(
            norm_id=f"{norm_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[key],
            prozedur=_PROZEDUR_MAP[key],
            medizin_norm_weight=round(sum(n.medizin_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[key]), 4),
            medizin_norm_tier=max(n.medizin_tier for n in parent.normen) + _TIER_DELTA[key],
            medizin_norm_ids=[f"mn-{norm_id}-{g.value}-001", f"mn-{norm_id}-{g.value}-002"],
            medizin_norm_tags=["medizin", "norm", g.value],
        ))
    return MedizinNormSatz(norm_id=norm_id, normen=eintraege, parent=parent)
