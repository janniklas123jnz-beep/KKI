from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .hydrologie_feld import HydrologieFeld, build_hydrologie_feld


class GrundwasserRegisterGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_HYDROLOGISCH = auto()
    HYDROLOGISCH = auto()
    HYDROLOGISCH_AKTIV = auto()
    HYDROLOGIE_SOUVERAEN = auto()


class GrundwasserRegisterTyp(Enum):
    GRUNDWASSERREGISTER = auto()
    GRUNDWASSERSYSTEM = auto()
    GRUNDWASSERKOMPONENTE = auto()


class GrundwasserRegisterProzedur(Enum):
    GRUNDWASSERANALYSE = auto()
    GRUNDWASSERSYNTHESE = auto()
    GRUNDWASSERBEWERTUNG = auto()


_WEIGHT_DELTA: dict[GrundwasserRegisterGeltung, float] = {
    GrundwasserRegisterGeltung.GESPERRT: 0.0,
    GrundwasserRegisterGeltung.GRUNDLEGEND_HYDROLOGISCH: 1.3,
    GrundwasserRegisterGeltung.HYDROLOGISCH: 2.6,
    GrundwasserRegisterGeltung.HYDROLOGISCH_AKTIV: 3.9,
    GrundwasserRegisterGeltung.HYDROLOGIE_SOUVERAEN: 5.2,
}

_TYP_MAP = {
    GrundwasserRegisterGeltung.GESPERRT: GrundwasserRegisterTyp.GRUNDWASSERREGISTER,
    GrundwasserRegisterGeltung.GRUNDLEGEND_HYDROLOGISCH: GrundwasserRegisterTyp.GRUNDWASSERKOMPONENTE,
    GrundwasserRegisterGeltung.HYDROLOGISCH: GrundwasserRegisterTyp.GRUNDWASSERKOMPONENTE,
    GrundwasserRegisterGeltung.HYDROLOGISCH_AKTIV: GrundwasserRegisterTyp.GRUNDWASSERSYSTEM,
    GrundwasserRegisterGeltung.HYDROLOGIE_SOUVERAEN: GrundwasserRegisterTyp.GRUNDWASSERSYSTEM,
}

_PROZEDUR_MAP = {
    GrundwasserRegisterGeltung.GESPERRT: GrundwasserRegisterProzedur.GRUNDWASSERANALYSE,
    GrundwasserRegisterGeltung.GRUNDLEGEND_HYDROLOGISCH: GrundwasserRegisterProzedur.GRUNDWASSERANALYSE,
    GrundwasserRegisterGeltung.HYDROLOGISCH: GrundwasserRegisterProzedur.GRUNDWASSERSYNTHESE,
    GrundwasserRegisterGeltung.HYDROLOGISCH_AKTIV: GrundwasserRegisterProzedur.GRUNDWASSERSYNTHESE,
    GrundwasserRegisterGeltung.HYDROLOGIE_SOUVERAEN: GrundwasserRegisterProzedur.GRUNDWASSERBEWERTUNG,
}


@dataclass(frozen=True)
class GrundwasserRegisterEintrag:
    geltung: GrundwasserRegisterGeltung
    hydrologie_weight: float
    hydrologie_tier: int
    hydrologie_ids: tuple[str, ...]
    hydrologie_tags: tuple[str, ...]
    typ: GrundwasserRegisterTyp
    prozedur: GrundwasserRegisterProzedur
    canonical: bool = True


@dataclass(frozen=True)
class GrundwasserRegister:
    eintraege: tuple[GrundwasserRegisterEintrag, ...]
    parent: Optional[HydrologieFeld] = None


def build_grundwasser_register(parent: Optional[HydrologieFeld] = None) -> GrundwasserRegister:
    if parent is None:
        parent = build_hydrologie_feld()
    base = sum(n.hydrologie_weight for n in parent.normen)
    eintraege = tuple(
        GrundwasserRegisterEintrag(
            geltung=g,
            hydrologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            hydrologie_tier=i + 1,
            hydrologie_ids=(f"grundwasser-register-{g.name.lower()}-001",),
            hydrologie_tags=("hydrologie", "grundwasser", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(GrundwasserRegisterGeltung)
    )
    return GrundwasserRegister(eintraege=eintraege, parent=parent)
