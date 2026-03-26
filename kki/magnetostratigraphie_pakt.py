from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .biostratigraphie_manifest import BiostratigraphieManifest, build_biostratigraphie_manifest


class MagnetostratigraphiePaktTyp(Enum):
    POLARITAET = auto()
    CHRON = auto()
    POLUMKEHRUNG = auto()
    MAGNETISIERUNG = auto()
    SUSZEPTIBILITAET = auto()


class MagnetostratigraphiePaktProzedur(Enum):
    MESSUNG = auto()
    KORRELATION = auto()
    DATIERUNG = auto()
    MODELLIERUNG = auto()
    INTERPRETATION = auto()


_WEIGHT_DELTA = {
    MagnetostratigraphiePaktTyp.POLARITAET: 0.0,
    MagnetostratigraphiePaktTyp.CHRON: 1.7,
    MagnetostratigraphiePaktTyp.POLUMKEHRUNG: 3.4,
    MagnetostratigraphiePaktTyp.MAGNETISIERUNG: 5.1,
    MagnetostratigraphiePaktTyp.SUSZEPTIBILITAET: 6.8,
}
_TYP_MAP = {
    MagnetostratigraphiePaktTyp.POLARITAET: "polaritaet",
    MagnetostratigraphiePaktTyp.CHRON: "chron",
    MagnetostratigraphiePaktTyp.POLUMKEHRUNG: "polumkehrung",
    MagnetostratigraphiePaktTyp.MAGNETISIERUNG: "magnetisierung",
    MagnetostratigraphiePaktTyp.SUSZEPTIBILITAET: "suszeptibilitaet",
}
_PROZEDUR_MAP = {
    MagnetostratigraphiePaktProzedur.MESSUNG: "messung",
    MagnetostratigraphiePaktProzedur.KORRELATION: "korrelation",
    MagnetostratigraphiePaktProzedur.DATIERUNG: "datierung",
    MagnetostratigraphiePaktProzedur.MODELLIERUNG: "modellierung",
    MagnetostratigraphiePaktProzedur.INTERPRETATION: "interpretation",
}


@dataclass(frozen=True)
class MagnetostratigraphiePaktEintrag:
    typ: MagnetostratigraphiePaktTyp
    prozedur: MagnetostratigraphiePaktProzedur
    geochronologie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class MagnetostratigraphiePakt:
    eintraege: tuple[MagnetostratigraphiePaktEintrag, ...]
    canonical: bool = True

    def aggregates_pakt_signal(self) -> dict:
        return {
            "pakt_id": "magnetostratigraphie-pakt-876",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_magnetostratigraphie_pakt(parent: Optional[BiostratigraphieManifest] = None) -> MagnetostratigraphiePakt:
    if parent is None:
        parent = build_biostratigraphie_manifest()
    base = sum(n.geochronologie_weight for n in parent.normen)
    eintraege = tuple(
        MagnetostratigraphiePaktEintrag(
            typ=t,
            prozedur=list(MagnetostratigraphiePaktProzedur)[i],
            geochronologie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(MagnetostratigraphiePaktTyp)
    )
    return MagnetostratigraphiePakt(eintraege=eintraege)
