from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .kryosphaere_charta import KryosphaereCharta, build_kryosphaere_charta


class GlaziologieVerfassungTyp(Enum):
    GRUNDGESETZ = auto()
    FORSCHUNGSAUFTRAG = auto()
    BILDUNGSMANDAT = auto()
    ETHIKPRINZIP = auto()
    NACHHALTIGKEITSGEBOT = auto()


class GlaziologieVerfassungProzedur(Enum):
    RATIFIZIERUNG = auto()
    REVISION = auto()
    INKRAFTTRETEN = auto()
    AUSLEGUNG = auto()
    DURCHSETZUNG = auto()


_WEIGHT_DELTA = {
    GlaziologieVerfassungTyp.GRUNDGESETZ: 0.0,
    GlaziologieVerfassungTyp.FORSCHUNGSAUFTRAG: 2.1,
    GlaziologieVerfassungTyp.BILDUNGSMANDAT: 4.2,
    GlaziologieVerfassungTyp.ETHIKPRINZIP: 6.3,
    GlaziologieVerfassungTyp.NACHHALTIGKEITSGEBOT: 8.4,
}
_TYP_MAP = {
    GlaziologieVerfassungTyp.GRUNDGESETZ: "grundgesetz",
    GlaziologieVerfassungTyp.FORSCHUNGSAUFTRAG: "forschungsauftrag",
    GlaziologieVerfassungTyp.BILDUNGSMANDAT: "bildungsmandat",
    GlaziologieVerfassungTyp.ETHIKPRINZIP: "ethikprinzip",
    GlaziologieVerfassungTyp.NACHHALTIGKEITSGEBOT: "nachhaltigkeitsgebot",
}
_PROZEDUR_MAP = {
    GlaziologieVerfassungProzedur.RATIFIZIERUNG: "ratifizierung",
    GlaziologieVerfassungProzedur.REVISION: "revision",
    GlaziologieVerfassungProzedur.INKRAFTTRETEN: "inkrafttreten",
    GlaziologieVerfassungProzedur.AUSLEGUNG: "auslegung",
    GlaziologieVerfassungProzedur.DURCHSETZUNG: "durchsetzung",
}


@dataclass(frozen=True)
class GlaziologieVerfassungNorm:
    typ: GlaziologieVerfassungTyp
    prozedur: GlaziologieVerfassungProzedur
    glaziologie_weight: float
    glaziologie_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class GlaziologieVerfassung:
    normen: tuple[GlaziologieVerfassungNorm, ...]
    canonical: bool = True

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": "glaziologie-verfassung-900",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_glaziologie_verfassung(parent: Optional[KryosphaereCharta] = None) -> GlaziologieVerfassung:
    if parent is None:
        parent = build_kryosphaere_charta()
    base = sum(n.glaziologie_weight for n in parent.normen)
    tier_base = max(n.tier for n in parent.normen)
    normen = tuple(
        GlaziologieVerfassungNorm(
            typ=t,
            prozedur=list(GlaziologieVerfassungProzedur)[i],
            glaziologie_weight=base + _WEIGHT_DELTA[t],
            glaziologie_tier=tier_base + i + 1,
        )
        for i, t in enumerate(GlaziologieVerfassungTyp)
    )
    return GlaziologieVerfassung(normen=normen)
