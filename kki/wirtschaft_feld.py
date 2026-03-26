"""
#961 WirtschaftFeld — Wirtschaftswissenschaft: Smith, Ricardo & Keynes.
Adam Smith (1776): The Wealth of Nations — unsichtbare Hand des Marktes;
  Arbeitsteilung als Produktivitätsquelle; Grundlage der klassischen Ökonomie
  und des freien Marktes als Koordinationsmechanismus.
David Ricardo (1817): Principles of Political Economy — komparativer Kostenvorteil;
  Freihandel als wohlfahrtssteigerndes Prinzip; Grundlage der Außenwirtschaftslehre.
John Maynard Keynes (1936): The General Theory of Employment, Interest and Money —
  Nachfragesteuerung durch Fiskalpolitik; Staatseingriff in Rezessionen;
  Multiplikatoreffekt als makroökonomisches Werkzeug.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .energie_verfassung import EnergieVerfassung, build_energie_verfassung


class WirtschaftFeldTyp(Enum):
    MIKOOEKONOMIE = auto()
    MAKROOEKONOMIE = auto()
    INSTITUTIONELLE_OEKONOMIE = auto()
    VERHALTENSORIENTIERTE_OEKONOMIE = auto()
    POLITISCHE_OEKONOMIE = auto()


class WirtschaftFeldProzedur(Enum):
    ANALYSE = auto()
    MODELLIERUNG = auto()
    PROGNOSE = auto()
    POLITIKEMPFEHLUNG = auto()
    EVALUATION = auto()


_WEIGHT_DELTA = {
    WirtschaftFeldTyp.MIKOOEKONOMIE: 0.0,
    WirtschaftFeldTyp.MAKROOEKONOMIE: 1.4,
    WirtschaftFeldTyp.INSTITUTIONELLE_OEKONOMIE: 2.8,
    WirtschaftFeldTyp.VERHALTENSORIENTIERTE_OEKONOMIE: 4.2,
    WirtschaftFeldTyp.POLITISCHE_OEKONOMIE: 5.6,
}
_TYP_MAP = {
    WirtschaftFeldTyp.MIKOOEKONOMIE: "mikooekonomie",
    WirtschaftFeldTyp.MAKROOEKONOMIE: "makrooekonomie",
    WirtschaftFeldTyp.INSTITUTIONELLE_OEKONOMIE: "institutionelle_oekonomie",
    WirtschaftFeldTyp.VERHALTENSORIENTIERTE_OEKONOMIE: "verhaltensorientierte_oekonomie",
    WirtschaftFeldTyp.POLITISCHE_OEKONOMIE: "politische_oekonomie",
}
_PROZEDUR_MAP = {
    WirtschaftFeldProzedur.ANALYSE: "analyse",
    WirtschaftFeldProzedur.MODELLIERUNG: "modellierung",
    WirtschaftFeldProzedur.PROGNOSE: "prognose",
    WirtschaftFeldProzedur.POLITIKEMPFEHLUNG: "politikempfehlung",
    WirtschaftFeldProzedur.EVALUATION: "evaluation",
}


@dataclass(frozen=True)
class WirtschaftFeldNorm:
    typ: WirtschaftFeldTyp
    prozedur: WirtschaftFeldProzedur
    finanz_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class WirtschaftFeld:
    normen: tuple[WirtschaftFeldNorm, ...]
    canonical: bool = True

    def aggregates_feld_signal(self) -> dict:
        return {
            "feld_id": "wirtschaft-feld-961",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_wirtschaft_feld(parent: Optional[EnergieVerfassung] = None) -> WirtschaftFeld:
    if parent is None:
        parent = build_energie_verfassung()
    base = sum(n.energie_weight for n in parent.normen)
    normen = tuple(
        WirtschaftFeldNorm(
            typ=t,
            prozedur=list(WirtschaftFeldProzedur)[i],
            finanz_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(WirtschaftFeldTyp)
    )
    return WirtschaftFeld(normen=normen)
