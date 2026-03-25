from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .tierhaltung_charta import TierhaltungCharta, build_tierhaltung_charta


class BodenkundeKodexGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_BODENKUNDLICH = auto()
    BODENKUNDLICH = auto()
    BODENKUNDLICH_AKTIV = auto()
    BODENKUNDE_SOUVERAEN = auto()


class BodenkundeKodexTyp(Enum):
    BODENKODEX = auto()
    BODENPROFILANALYSE = auto()
    BODENFRUCHTBARKEITSMESSUNG = auto()


class BodenkundeKodexProzedur(Enum):
    BODENTYPBESTIMMUNG = auto()
    NAEHRSTOFFANALYSE = auto()
    BODENSCHUTZBEWERTUNG = auto()


_WEIGHT_DELTA: dict[BodenkundeKodexGeltung, float] = {
    BodenkundeKodexGeltung.GESPERRT: 0.0,
    BodenkundeKodexGeltung.GRUNDLEGEND_BODENKUNDLICH: 1.5,
    BodenkundeKodexGeltung.BODENKUNDLICH: 3.0,
    BodenkundeKodexGeltung.BODENKUNDLICH_AKTIV: 4.5,
    BodenkundeKodexGeltung.BODENKUNDE_SOUVERAEN: 6.0,
}

_TYP_MAP = {
    BodenkundeKodexGeltung.GESPERRT: BodenkundeKodexTyp.BODENKODEX,
    BodenkundeKodexGeltung.GRUNDLEGEND_BODENKUNDLICH: BodenkundeKodexTyp.BODENPROFILANALYSE,
    BodenkundeKodexGeltung.BODENKUNDLICH: BodenkundeKodexTyp.BODENPROFILANALYSE,
    BodenkundeKodexGeltung.BODENKUNDLICH_AKTIV: BodenkundeKodexTyp.BODENFRUCHTBARKEITSMESSUNG,
    BodenkundeKodexGeltung.BODENKUNDE_SOUVERAEN: BodenkundeKodexTyp.BODENFRUCHTBARKEITSMESSUNG,
}

_PROZEDUR_MAP = {
    BodenkundeKodexGeltung.GESPERRT: BodenkundeKodexProzedur.BODENTYPBESTIMMUNG,
    BodenkundeKodexGeltung.GRUNDLEGEND_BODENKUNDLICH: BodenkundeKodexProzedur.BODENTYPBESTIMMUNG,
    BodenkundeKodexGeltung.BODENKUNDLICH: BodenkundeKodexProzedur.NAEHRSTOFFANALYSE,
    BodenkundeKodexGeltung.BODENKUNDLICH_AKTIV: BodenkundeKodexProzedur.NAEHRSTOFFANALYSE,
    BodenkundeKodexGeltung.BODENKUNDE_SOUVERAEN: BodenkundeKodexProzedur.BODENSCHUTZBEWERTUNG,
}


@dataclass(frozen=True)
class BodenkundeKodexEintrag:
    geltung: BodenkundeKodexGeltung
    agrar_weight: float
    agrar_tier: int
    agrar_ids: tuple[str, ...]
    agrar_tags: tuple[str, ...]
    typ: BodenkundeKodexTyp
    prozedur: BodenkundeKodexProzedur
    canonical: bool = True


@dataclass(frozen=True)
class BodenkundeKodex:
    eintraege: tuple[BodenkundeKodexEintrag, ...]
    parent: Optional[TierhaltungCharta] = None


def build_bodenkunde_kodex(parent: Optional[TierhaltungCharta] = None) -> BodenkundeKodex:
    if parent is None:
        parent = build_tierhaltung_charta()
    base = sum(n.agrar_weight for n in parent.normen)
    eintraege = tuple(
        BodenkundeKodexEintrag(
            geltung=g,
            agrar_weight=round(base + _WEIGHT_DELTA[g], 4),
            agrar_tier=i + 1,
            agrar_ids=(f"bodenkunde-{g.name.lower()}-001",),
            agrar_tags=("bodenkunde", "kodex", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(BodenkundeKodexGeltung)
    )
    return BodenkundeKodex(eintraege=eintraege, parent=parent)
