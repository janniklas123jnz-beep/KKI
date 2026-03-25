from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .pharma_feld import PharmaFeld, build_pharma_feld


class ArzneimittelRegisterGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_ARZNEIMITTEL = auto()
    ARZNEIMITTEL = auto()
    ARZNEIMITTEL_AKTIV = auto()
    ARZNEIMITTEL_SOUVERAEN = auto()


class ArzneimittelRegisterTyp(Enum):
    ARZNEIMITTELREGISTER = auto()
    WIRKSTOFFKATALOG = auto()
    ARZNEIMITTELDOSSIER = auto()


class ArzneimittelRegisterProzedur(Enum):
    ARZNEIMITTELREGISTRIERUNG = auto()
    WIRKSTOFFBEWERTUNG = auto()
    ZULASSUNGSPRUEFUNG = auto()


_WEIGHT_DELTA: dict[ArzneimittelRegisterGeltung, float] = {
    ArzneimittelRegisterGeltung.GESPERRT: 0.0,
    ArzneimittelRegisterGeltung.GRUNDLEGEND_ARZNEIMITTEL: 1.4,
    ArzneimittelRegisterGeltung.ARZNEIMITTEL: 2.8,
    ArzneimittelRegisterGeltung.ARZNEIMITTEL_AKTIV: 4.2,
    ArzneimittelRegisterGeltung.ARZNEIMITTEL_SOUVERAEN: 5.6,
}

_TYP_MAP = {
    ArzneimittelRegisterGeltung.GESPERRT: ArzneimittelRegisterTyp.ARZNEIMITTELREGISTER,
    ArzneimittelRegisterGeltung.GRUNDLEGEND_ARZNEIMITTEL: ArzneimittelRegisterTyp.ARZNEIMITTELDOSSIER,
    ArzneimittelRegisterGeltung.ARZNEIMITTEL: ArzneimittelRegisterTyp.ARZNEIMITTELDOSSIER,
    ArzneimittelRegisterGeltung.ARZNEIMITTEL_AKTIV: ArzneimittelRegisterTyp.WIRKSTOFFKATALOG,
    ArzneimittelRegisterGeltung.ARZNEIMITTEL_SOUVERAEN: ArzneimittelRegisterTyp.WIRKSTOFFKATALOG,
}

_PROZEDUR_MAP = {
    ArzneimittelRegisterGeltung.GESPERRT: ArzneimittelRegisterProzedur.ARZNEIMITTELREGISTRIERUNG,
    ArzneimittelRegisterGeltung.GRUNDLEGEND_ARZNEIMITTEL: ArzneimittelRegisterProzedur.ARZNEIMITTELREGISTRIERUNG,
    ArzneimittelRegisterGeltung.ARZNEIMITTEL: ArzneimittelRegisterProzedur.WIRKSTOFFBEWERTUNG,
    ArzneimittelRegisterGeltung.ARZNEIMITTEL_AKTIV: ArzneimittelRegisterProzedur.WIRKSTOFFBEWERTUNG,
    ArzneimittelRegisterGeltung.ARZNEIMITTEL_SOUVERAEN: ArzneimittelRegisterProzedur.ZULASSUNGSPRUEFUNG,
}


@dataclass(frozen=True)
class ArzneimittelRegisterEintrag:
    geltung: ArzneimittelRegisterGeltung
    pharma_weight: float
    pharma_tier: int
    pharma_ids: tuple[str, ...]
    pharma_tags: tuple[str, ...]
    typ: ArzneimittelRegisterTyp
    prozedur: ArzneimittelRegisterProzedur
    canonical: bool = True


@dataclass(frozen=True)
class ArzneimittelRegister:
    eintraege: tuple[ArzneimittelRegisterEintrag, ...]
    parent: Optional[PharmaFeld] = None


def build_arzneimittel_register(parent: Optional[PharmaFeld] = None) -> ArzneimittelRegister:
    if parent is None:
        parent = build_pharma_feld()
    base = sum(n.pharma_weight for n in parent.normen)
    eintraege = tuple(
        ArzneimittelRegisterEintrag(
            geltung=g,
            pharma_weight=round(base + _WEIGHT_DELTA[g], 4),
            pharma_tier=i + 1,
            pharma_ids=(f"arzneimittel-{g.name.lower()}-001",),
            pharma_tags=("arzneimittel", "register", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(ArzneimittelRegisterGeltung)
    )
    return ArzneimittelRegister(eintraege=eintraege, parent=parent)
