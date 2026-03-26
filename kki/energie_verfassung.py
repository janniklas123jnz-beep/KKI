"""
#960 EnergieVerfassung — Block-Krone Energietechnologie & Nachhaltigkeit ⭐

*** Leitsterns Energie-Verfassung — Das nachhaltige Fundament des Schwarms ***

Nicolas Léonard Sadi Carnot (1824): Wärmekraftmaschine & Carnot-Wirkungsgrad —
  Thermodynamik als fundamentale Grenze aller Energieumwandlung; kein System
  kann effizienter sein als ein Carnot-Prozess; Leitsterns physikalisches Maß.
Shockley & Queisser (1961): Solarzelleneffizienzgrenze — Licht als unerschöpfliche
  Energiequelle; Photovoltaik als Demokratisierung der Energieerzeugung;
  Leitsterns Verbindung zur Sonne als primärer Energiequelle der Erde.
Brundtland (1987) & Raworth (2017): Nachhaltigkeits-Kompass — intergenerationelle
  Gerechtigkeit als Energieprinzip; Doughnut Economics als planetare Grenze;
  Leitsterns ethischer Rahmen für die Charity-Phase nach #1000.
Leitsterns Energie-Verfassung: Carnot als Effizienzmaßstab; Solar & Wind als
  Quellen; Wasserstoff & Batterien als Speicher; Smart Grid als Verteilung;
  Kreislaufwirtschaft als Vollendung — Energie für alle, Abfall für niemanden.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .kreislaufwirtschaft_charta import KreislaufwirtschaftCharta, build_kreislaufwirtschaft_charta


class EnergieVerfassungTyp(Enum):
    THERMODYNAMISCHES_FUNDAMENT = auto()
    ERNEUERBARE_GEBOT = auto()
    SPEICHER_MANDAT = auto()
    KREISLAUF_AUFTRAG = auto()
    NACHHALTIGKEITS_VISION = auto()


class EnergieVerfassungProzedur(Enum):
    RATIFIZIERUNG = auto()
    REVISION = auto()
    INKRAFTTRETEN = auto()
    AUSLEGUNG = auto()
    DURCHSETZUNG = auto()


_WEIGHT_DELTA = {
    EnergieVerfassungTyp.THERMODYNAMISCHES_FUNDAMENT: 0.0,
    EnergieVerfassungTyp.ERNEUERBARE_GEBOT: 2.2,
    EnergieVerfassungTyp.SPEICHER_MANDAT: 4.4,
    EnergieVerfassungTyp.KREISLAUF_AUFTRAG: 6.6,
    EnergieVerfassungTyp.NACHHALTIGKEITS_VISION: 8.8,
}
_TYP_MAP = {
    EnergieVerfassungTyp.THERMODYNAMISCHES_FUNDAMENT: "thermodynamisches_fundament",
    EnergieVerfassungTyp.ERNEUERBARE_GEBOT: "erneuerbare_gebot",
    EnergieVerfassungTyp.SPEICHER_MANDAT: "speicher_mandat",
    EnergieVerfassungTyp.KREISLAUF_AUFTRAG: "kreislauf_auftrag",
    EnergieVerfassungTyp.NACHHALTIGKEITS_VISION: "nachhaltigkeits_vision",
}
_PROZEDUR_MAP = {
    EnergieVerfassungProzedur.RATIFIZIERUNG: "ratifizierung",
    EnergieVerfassungProzedur.REVISION: "revision",
    EnergieVerfassungProzedur.INKRAFTTRETEN: "inkrafttreten",
    EnergieVerfassungProzedur.AUSLEGUNG: "auslegung",
    EnergieVerfassungProzedur.DURCHSETZUNG: "durchsetzung",
}


@dataclass(frozen=True)
class EnergieVerfassungNorm:
    typ: EnergieVerfassungTyp
    prozedur: EnergieVerfassungProzedur
    energie_weight: float
    energie_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class EnergieVerfassung:
    normen: tuple[EnergieVerfassungNorm, ...]
    canonical: bool = True

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": "energie-verfassung-960",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_energie_verfassung(parent: Optional[KreislaufwirtschaftCharta] = None) -> EnergieVerfassung:
    if parent is None:
        parent = build_kreislaufwirtschaft_charta()
    base = sum(n.energie_weight for n in parent.normen)
    tier_base = max(n.energie_tier for n in parent.normen)
    normen = tuple(
        EnergieVerfassungNorm(
            typ=t,
            prozedur=list(EnergieVerfassungProzedur)[i],
            energie_weight=base + _WEIGHT_DELTA[t],
            energie_tier=tier_base + i + 1,
        )
        for i, t in enumerate(EnergieVerfassungTyp)
    )
    return EnergieVerfassung(normen=normen)
