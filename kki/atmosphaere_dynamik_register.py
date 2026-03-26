from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .meteorologie_feld import MeteorologieFeld, build_meteorologie_feld


class AtmosphaereDynamikRegisterGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_METEOROLOGISCH = auto()
    METEOROLOGISCH = auto()
    METEOROLOGISCH_AKTIV = auto()
    METEOROLOGIE_SOUVERAEN = auto()


class AtmosphaereDynamikRegisterTyp(Enum):
    ATMOSPHAERENDYNAMIKREGISTER = auto()
    ATMOSPHAERENDYNAMIKSYSTEM = auto()
    ATMOSPHAERENDYNAMIKKOMPONENTE = auto()


class AtmosphaereDynamikRegisterProzedur(Enum):
    ATMOSPHAERENDYNAMIKANALYSE = auto()
    ATMOSPHAERENDYNAMIKSYNTHESE = auto()
    ATMOSPHAERENDYNAMIKBEWERTUNG = auto()


_WEIGHT_DELTA: dict[AtmosphaereDynamikRegisterGeltung, float] = {
    AtmosphaereDynamikRegisterGeltung.GESPERRT: 0.0,
    AtmosphaereDynamikRegisterGeltung.GRUNDLEGEND_METEOROLOGISCH: 1.3,
    AtmosphaereDynamikRegisterGeltung.METEOROLOGISCH: 2.6,
    AtmosphaereDynamikRegisterGeltung.METEOROLOGISCH_AKTIV: 3.9,
    AtmosphaereDynamikRegisterGeltung.METEOROLOGIE_SOUVERAEN: 5.2,
}

_TYP_MAP = {
    AtmosphaereDynamikRegisterGeltung.GESPERRT: AtmosphaereDynamikRegisterTyp.ATMOSPHAERENDYNAMIKREGISTER,
    AtmosphaereDynamikRegisterGeltung.GRUNDLEGEND_METEOROLOGISCH: AtmosphaereDynamikRegisterTyp.ATMOSPHAERENDYNAMIKKOMPONENTE,
    AtmosphaereDynamikRegisterGeltung.METEOROLOGISCH: AtmosphaereDynamikRegisterTyp.ATMOSPHAERENDYNAMIKKOMPONENTE,
    AtmosphaereDynamikRegisterGeltung.METEOROLOGISCH_AKTIV: AtmosphaereDynamikRegisterTyp.ATMOSPHAERENDYNAMIKSYSTEM,
    AtmosphaereDynamikRegisterGeltung.METEOROLOGIE_SOUVERAEN: AtmosphaereDynamikRegisterTyp.ATMOSPHAERENDYNAMIKSYSTEM,
}

_PROZEDUR_MAP = {
    AtmosphaereDynamikRegisterGeltung.GESPERRT: AtmosphaereDynamikRegisterProzedur.ATMOSPHAERENDYNAMIKANALYSE,
    AtmosphaereDynamikRegisterGeltung.GRUNDLEGEND_METEOROLOGISCH: AtmosphaereDynamikRegisterProzedur.ATMOSPHAERENDYNAMIKANALYSE,
    AtmosphaereDynamikRegisterGeltung.METEOROLOGISCH: AtmosphaereDynamikRegisterProzedur.ATMOSPHAERENDYNAMIKSYNTHESE,
    AtmosphaereDynamikRegisterGeltung.METEOROLOGISCH_AKTIV: AtmosphaereDynamikRegisterProzedur.ATMOSPHAERENDYNAMIKSYNTHESE,
    AtmosphaereDynamikRegisterGeltung.METEOROLOGIE_SOUVERAEN: AtmosphaereDynamikRegisterProzedur.ATMOSPHAERENDYNAMIKBEWERTUNG,
}


@dataclass(frozen=True)
class AtmosphaereDynamikRegisterEintrag:
    geltung: AtmosphaereDynamikRegisterGeltung
    meteorologie_weight: float
    meteorologie_tier: int
    meteorologie_ids: tuple[str, ...]
    meteorologie_tags: tuple[str, ...]
    typ: AtmosphaereDynamikRegisterTyp
    prozedur: AtmosphaereDynamikRegisterProzedur
    canonical: bool = True


@dataclass(frozen=True)
class AtmosphaereDynamikRegister:
    eintraege: tuple[AtmosphaereDynamikRegisterEintrag, ...]
    parent: Optional[MeteorologieFeld] = None


def build_atmosphaere_dynamik_register(parent: Optional[MeteorologieFeld] = None) -> AtmosphaereDynamikRegister:
    if parent is None:
        parent = build_meteorologie_feld()
    base = sum(n.meteorologie_weight for n in parent.normen)
    eintraege = tuple(
        AtmosphaereDynamikRegisterEintrag(
            geltung=g,
            meteorologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            meteorologie_tier=i + 1,
            meteorologie_ids=(f"atmosphaere-dynamik-register-{g.name.lower()}-001",),
            meteorologie_tags=("meteorologie", "atmosphaere", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(AtmosphaereDynamikRegisterGeltung)
    )
    return AtmosphaereDynamikRegister(eintraege=eintraege, parent=parent)
