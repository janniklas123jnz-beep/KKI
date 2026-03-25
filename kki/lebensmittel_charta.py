from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .agrar_norm import AgrarNormSatz, build_agrar_norm


class LebensmittelChartaGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_LEBENSMITTELRECHTLICH = auto()
    LEBENSMITTELRECHTLICH = auto()
    LEBENSMITTELRECHTLICH_AKTIV = auto()
    LEBENSMITTEL_SOUVERAEN = auto()


class LebensmittelChartaTyp(Enum):
    LEBENSMITTELCHARTA = auto()
    LEBENSMITTELZULASSUNG = auto()
    QUALITAETSSICHERUNG = auto()


class LebensmittelChartaProzedur(Enum):
    LEBENSMITTELSICHERHEITSPRUEFUNG = auto()
    QUALITAETSKONTROLLE = auto()
    ZERTIFIZIERUNGSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[LebensmittelChartaGeltung, float] = {
    LebensmittelChartaGeltung.GESPERRT: 0.0,
    LebensmittelChartaGeltung.GRUNDLEGEND_LEBENSMITTELRECHTLICH: 2.0,
    LebensmittelChartaGeltung.LEBENSMITTELRECHTLICH: 4.0,
    LebensmittelChartaGeltung.LEBENSMITTELRECHTLICH_AKTIV: 6.0,
    LebensmittelChartaGeltung.LEBENSMITTEL_SOUVERAEN: 8.0,
}

_TYP_MAP = {
    LebensmittelChartaGeltung.GESPERRT: LebensmittelChartaTyp.LEBENSMITTELCHARTA,
    LebensmittelChartaGeltung.GRUNDLEGEND_LEBENSMITTELRECHTLICH: LebensmittelChartaTyp.LEBENSMITTELZULASSUNG,
    LebensmittelChartaGeltung.LEBENSMITTELRECHTLICH: LebensmittelChartaTyp.LEBENSMITTELZULASSUNG,
    LebensmittelChartaGeltung.LEBENSMITTELRECHTLICH_AKTIV: LebensmittelChartaTyp.QUALITAETSSICHERUNG,
    LebensmittelChartaGeltung.LEBENSMITTEL_SOUVERAEN: LebensmittelChartaTyp.QUALITAETSSICHERUNG,
}

_PROZEDUR_MAP = {
    LebensmittelChartaGeltung.GESPERRT: LebensmittelChartaProzedur.LEBENSMITTELSICHERHEITSPRUEFUNG,
    LebensmittelChartaGeltung.GRUNDLEGEND_LEBENSMITTELRECHTLICH: LebensmittelChartaProzedur.LEBENSMITTELSICHERHEITSPRUEFUNG,
    LebensmittelChartaGeltung.LEBENSMITTELRECHTLICH: LebensmittelChartaProzedur.QUALITAETSKONTROLLE,
    LebensmittelChartaGeltung.LEBENSMITTELRECHTLICH_AKTIV: LebensmittelChartaProzedur.QUALITAETSKONTROLLE,
    LebensmittelChartaGeltung.LEBENSMITTEL_SOUVERAEN: LebensmittelChartaProzedur.ZERTIFIZIERUNGSBEWERTUNG,
}


@dataclass(frozen=True)
class LebensmittelChartaNorm:
    geltung: LebensmittelChartaGeltung
    agrar_weight: float
    agrar_tier: int
    agrar_ids: tuple[str, ...]
    agrar_tags: tuple[str, ...]
    typ: LebensmittelChartaTyp
    prozedur: LebensmittelChartaProzedur
    canonical: bool = True


@dataclass(frozen=True)
class LebensmittelCharta:
    normen: tuple[LebensmittelChartaNorm, ...]
    parent: Optional[AgrarNormSatz] = None


def build_lebensmittel_charta(parent: Optional[AgrarNormSatz] = None) -> LebensmittelCharta:
    if parent is None:
        parent = build_agrar_norm()
    base = sum(e.agrar_norm_weight for e in parent.normen)
    tier_base = max(e.agrar_norm_tier for e in parent.normen)
    normen = tuple(
        LebensmittelChartaNorm(
            geltung=g,
            agrar_weight=round(base + _WEIGHT_DELTA[g], 4),
            agrar_tier=tier_base + i + 1,
            agrar_ids=(f"lebensmittel-{g.name.lower()}-001",),
            agrar_tags=("lebensmittel", "charta", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(LebensmittelChartaGeltung)
    )
    return LebensmittelCharta(normen=normen, parent=parent)
