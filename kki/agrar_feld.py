from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .sport_verfassung import SportVerfassung, build_sport_verfassung


class AgrarFeldGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_AGRARWISSENSCHAFTLICH = auto()
    AGRARWISSENSCHAFTLICH = auto()
    AGRARWISSENSCHAFTLICH_AKTIV = auto()
    AGRAR_SOUVERAEN = auto()


class AgrarFeldTyp(Enum):
    AGRARFELD = auto()
    AGRARSYSTEM = auto()
    AGRARKOMPONENTE = auto()


class AgrarFeldProzedur(Enum):
    AGRARANALYSE = auto()
    AGRARSYNTHESE = auto()
    AGRARBEWERTUNG = auto()


_WEIGHT_DELTA: dict[AgrarFeldGeltung, float] = {
    AgrarFeldGeltung.GESPERRT: 0.0,
    AgrarFeldGeltung.GRUNDLEGEND_AGRARWISSENSCHAFTLICH: 1.2,
    AgrarFeldGeltung.AGRARWISSENSCHAFTLICH: 2.4,
    AgrarFeldGeltung.AGRARWISSENSCHAFTLICH_AKTIV: 3.6,
    AgrarFeldGeltung.AGRAR_SOUVERAEN: 5.0,
}

_TYP_MAP = {
    AgrarFeldGeltung.GESPERRT: AgrarFeldTyp.AGRARFELD,
    AgrarFeldGeltung.GRUNDLEGEND_AGRARWISSENSCHAFTLICH: AgrarFeldTyp.AGRARKOMPONENTE,
    AgrarFeldGeltung.AGRARWISSENSCHAFTLICH: AgrarFeldTyp.AGRARKOMPONENTE,
    AgrarFeldGeltung.AGRARWISSENSCHAFTLICH_AKTIV: AgrarFeldTyp.AGRARSYSTEM,
    AgrarFeldGeltung.AGRAR_SOUVERAEN: AgrarFeldTyp.AGRARSYSTEM,
}

_PROZEDUR_MAP = {
    AgrarFeldGeltung.GESPERRT: AgrarFeldProzedur.AGRARANALYSE,
    AgrarFeldGeltung.GRUNDLEGEND_AGRARWISSENSCHAFTLICH: AgrarFeldProzedur.AGRARANALYSE,
    AgrarFeldGeltung.AGRARWISSENSCHAFTLICH: AgrarFeldProzedur.AGRARSYNTHESE,
    AgrarFeldGeltung.AGRARWISSENSCHAFTLICH_AKTIV: AgrarFeldProzedur.AGRARSYNTHESE,
    AgrarFeldGeltung.AGRAR_SOUVERAEN: AgrarFeldProzedur.AGRARBEWERTUNG,
}


@dataclass(frozen=True)
class AgrarFeldNorm:
    geltung: AgrarFeldGeltung
    agrar_weight: float
    agrar_tier: int
    agrar_ids: tuple[str, ...]
    agrar_tags: tuple[str, ...]
    typ: AgrarFeldTyp
    prozedur: AgrarFeldProzedur
    canonical: bool = True


@dataclass(frozen=True)
class AgrarFeld:
    normen: tuple[AgrarFeldNorm, ...]
    parent: Optional[SportVerfassung] = None


def build_agrar_feld(parent: Optional[SportVerfassung] = None) -> AgrarFeld:
    if parent is None:
        parent = build_sport_verfassung()
    base = sum(n.sport_weight for n in parent.normen)
    normen = tuple(
        AgrarFeldNorm(
            geltung=g,
            agrar_weight=round(base + _WEIGHT_DELTA[g], 4),
            agrar_tier=i + 1,
            agrar_ids=(f"agrar-feld-{g.name.lower()}-001",),
            agrar_tags=("agrar", "feld", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(AgrarFeldGeltung)
    )
    return AgrarFeld(normen=normen, parent=parent)
