from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .geochronologie_feld import GeochronologieFeld, build_geochronologie_feld


class IsotopenRegisterTyp(Enum):
    URAN_BLEI = auto()
    KALIUM_ARGON = auto()
    RUBIDIUM_STRONTIUM = auto()
    SAMARIUM_NEODYM = auto()
    KOHLENSTOFF14 = auto()


class IsotopenRegisterProzedur(Enum):
    PROBENAHME = auto()
    AUFBEREITUNG = auto()
    MESSUNG = auto()
    AUSWERTUNG = auto()
    DOKUMENTATION = auto()


_WEIGHT_DELTA = {
    IsotopenRegisterTyp.URAN_BLEI: 0.0,
    IsotopenRegisterTyp.KALIUM_ARGON: 1.3,
    IsotopenRegisterTyp.RUBIDIUM_STRONTIUM: 2.6,
    IsotopenRegisterTyp.SAMARIUM_NEODYM: 3.9,
    IsotopenRegisterTyp.KOHLENSTOFF14: 5.2,
}
_TYP_MAP = {
    IsotopenRegisterTyp.URAN_BLEI: "uran_blei",
    IsotopenRegisterTyp.KALIUM_ARGON: "kalium_argon",
    IsotopenRegisterTyp.RUBIDIUM_STRONTIUM: "rubidium_strontium",
    IsotopenRegisterTyp.SAMARIUM_NEODYM: "samarium_neodym",
    IsotopenRegisterTyp.KOHLENSTOFF14: "kohlenstoff14",
}
_PROZEDUR_MAP = {
    IsotopenRegisterProzedur.PROBENAHME: "probenahme",
    IsotopenRegisterProzedur.AUFBEREITUNG: "aufbereitung",
    IsotopenRegisterProzedur.MESSUNG: "messung",
    IsotopenRegisterProzedur.AUSWERTUNG: "auswertung",
    IsotopenRegisterProzedur.DOKUMENTATION: "dokumentation",
}


@dataclass(frozen=True)
class IsotopenRegisterEintrag:
    typ: IsotopenRegisterTyp
    prozedur: IsotopenRegisterProzedur
    geochronologie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class IsotopenRegister:
    eintraege: tuple[IsotopenRegisterEintrag, ...]
    canonical: bool = True

    def aggregates_register_signal(self) -> dict:
        return {
            "register_id": "isotopen-register-872",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_isotopen_register(parent: Optional[GeochronologieFeld] = None) -> IsotopenRegister:
    if parent is None:
        parent = build_geochronologie_feld()
    base = sum(n.geochronologie_weight for n in parent.normen)
    eintraege = tuple(
        IsotopenRegisterEintrag(
            typ=t,
            prozedur=list(IsotopenRegisterProzedur)[i],
            geochronologie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(IsotopenRegisterTyp)
    )
    return IsotopenRegister(eintraege=eintraege)
