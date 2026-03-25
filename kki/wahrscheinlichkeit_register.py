from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .statistik_feld import StatistikFeld, build_statistik_feld


class WahrscheinlichkeitRegisterGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_PROBABILISTISCH = auto()
    PROBABILISTISCH = auto()
    PROBABILISTISCH_AKTIV = auto()
    WAHRSCHEINLICHKEIT_SOUVERAEN = auto()


class WahrscheinlichkeitRegisterTyp(Enum):
    WAHRSCHEINLICHKEITREGISTER = auto()
    WAHRSCHEINLICHKEITSRAUM = auto()
    VERTEILUNG = auto()


class WahrscheinlichkeitRegisterProzedur(Enum):
    PROBABILITAETSANALYSE = auto()
    VERTEILUNGSANALYSE = auto()
    STOCHASTISCHEBEWERTUNG = auto()


_WEIGHT_DELTA: dict[WahrscheinlichkeitRegisterGeltung, float] = {
    WahrscheinlichkeitRegisterGeltung.GESPERRT: 0.0,
    WahrscheinlichkeitRegisterGeltung.GRUNDLEGEND_PROBABILISTISCH: 1.3,
    WahrscheinlichkeitRegisterGeltung.PROBABILISTISCH: 2.6,
    WahrscheinlichkeitRegisterGeltung.PROBABILISTISCH_AKTIV: 3.9,
    WahrscheinlichkeitRegisterGeltung.WAHRSCHEINLICHKEIT_SOUVERAEN: 5.2,
}

_TYP_MAP = {
    WahrscheinlichkeitRegisterGeltung.GESPERRT: WahrscheinlichkeitRegisterTyp.WAHRSCHEINLICHKEITREGISTER,
    WahrscheinlichkeitRegisterGeltung.GRUNDLEGEND_PROBABILISTISCH: WahrscheinlichkeitRegisterTyp.VERTEILUNG,
    WahrscheinlichkeitRegisterGeltung.PROBABILISTISCH: WahrscheinlichkeitRegisterTyp.VERTEILUNG,
    WahrscheinlichkeitRegisterGeltung.PROBABILISTISCH_AKTIV: WahrscheinlichkeitRegisterTyp.WAHRSCHEINLICHKEITSRAUM,
    WahrscheinlichkeitRegisterGeltung.WAHRSCHEINLICHKEIT_SOUVERAEN: WahrscheinlichkeitRegisterTyp.WAHRSCHEINLICHKEITSRAUM,
}

_PROZEDUR_MAP = {
    WahrscheinlichkeitRegisterGeltung.GESPERRT: WahrscheinlichkeitRegisterProzedur.PROBABILITAETSANALYSE,
    WahrscheinlichkeitRegisterGeltung.GRUNDLEGEND_PROBABILISTISCH: WahrscheinlichkeitRegisterProzedur.PROBABILITAETSANALYSE,
    WahrscheinlichkeitRegisterGeltung.PROBABILISTISCH: WahrscheinlichkeitRegisterProzedur.VERTEILUNGSANALYSE,
    WahrscheinlichkeitRegisterGeltung.PROBABILISTISCH_AKTIV: WahrscheinlichkeitRegisterProzedur.VERTEILUNGSANALYSE,
    WahrscheinlichkeitRegisterGeltung.WAHRSCHEINLICHKEIT_SOUVERAEN: WahrscheinlichkeitRegisterProzedur.STOCHASTISCHEBEWERTUNG,
}


@dataclass(frozen=True)
class WahrscheinlichkeitRegisterEintrag:
    geltung: WahrscheinlichkeitRegisterGeltung
    stat_weight: float
    stat_tier: int
    stat_ids: tuple[str, ...]
    stat_tags: tuple[str, ...]
    typ: WahrscheinlichkeitRegisterTyp
    prozedur: WahrscheinlichkeitRegisterProzedur
    canonical: bool = True


@dataclass(frozen=True)
class WahrscheinlichkeitRegister:
    eintraege: tuple[WahrscheinlichkeitRegisterEintrag, ...]
    parent: Optional[StatistikFeld] = None


def build_wahrscheinlichkeit_register(parent: Optional[StatistikFeld] = None) -> WahrscheinlichkeitRegister:
    if parent is None:
        parent = build_statistik_feld()
    base = sum(n.stat_weight for n in parent.normen)
    eintraege = tuple(
        WahrscheinlichkeitRegisterEintrag(
            geltung=g,
            stat_weight=round(base + _WEIGHT_DELTA[g], 4),
            stat_tier=i + 1,
            stat_ids=(f"wahrscheinlichkeit-register-{g.name.lower()}-001",),
            stat_tags=("wahrscheinlichkeit", "register", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(WahrscheinlichkeitRegisterGeltung)
    )
    return WahrscheinlichkeitRegister(eintraege=eintraege, parent=parent)
