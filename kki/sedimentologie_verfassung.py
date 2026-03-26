from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .alluvial_charta import AlluvialCharta, build_alluvial_charta


class SedimentologieVerfassungTyp(Enum):
    GRUNDGESETZ = auto()
    FORSCHUNGSAUFTRAG = auto()
    BILDUNGSMANDAT = auto()
    ETHIKPRINZIP = auto()
    NACHHALTIGKEITSGEBOT = auto()


class SedimentologieVerfassungProzedur(Enum):
    RATIFIZIERUNG = auto()
    REVISION = auto()
    INKRAFTTRETEN = auto()
    AUSLEGUNG = auto()
    DURCHSETZUNG = auto()


_WEIGHT_DELTA = {
    SedimentologieVerfassungTyp.GRUNDGESETZ: 0.0,
    SedimentologieVerfassungTyp.FORSCHUNGSAUFTRAG: 2.1,
    SedimentologieVerfassungTyp.BILDUNGSMANDAT: 4.2,
    SedimentologieVerfassungTyp.ETHIKPRINZIP: 6.3,
    SedimentologieVerfassungTyp.NACHHALTIGKEITSGEBOT: 8.4,
}
_TYP_MAP = {
    SedimentologieVerfassungTyp.GRUNDGESETZ: "grundgesetz",
    SedimentologieVerfassungTyp.FORSCHUNGSAUFTRAG: "forschungsauftrag",
    SedimentologieVerfassungTyp.BILDUNGSMANDAT: "bildungsmandat",
    SedimentologieVerfassungTyp.ETHIKPRINZIP: "ethikprinzip",
    SedimentologieVerfassungTyp.NACHHALTIGKEITSGEBOT: "nachhaltigkeitsgebot",
}
_PROZEDUR_MAP = {
    SedimentologieVerfassungProzedur.RATIFIZIERUNG: "ratifizierung",
    SedimentologieVerfassungProzedur.REVISION: "revision",
    SedimentologieVerfassungProzedur.INKRAFTTRETEN: "inkrafttreten",
    SedimentologieVerfassungProzedur.AUSLEGUNG: "auslegung",
    SedimentologieVerfassungProzedur.DURCHSETZUNG: "durchsetzung",
}


@dataclass(frozen=True)
class SedimentologieVerfassungNorm:
    typ: SedimentologieVerfassungTyp
    prozedur: SedimentologieVerfassungProzedur
    sedimentologie_weight: float
    sedimentologie_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class SedimentologieVerfassung:
    normen: tuple[SedimentologieVerfassungNorm, ...]
    canonical: bool = True

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": "sedimentologie-verfassung-870",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_sedimentologie_verfassung(parent: Optional[AlluvialCharta] = None) -> SedimentologieVerfassung:
    if parent is None:
        parent = build_alluvial_charta()
    base = sum(n.sedimentologie_weight for n in parent.normen)
    tier_base = max(n.tier for n in parent.normen)
    normen = tuple(
        SedimentologieVerfassungNorm(
            typ=t,
            prozedur=list(SedimentologieVerfassungProzedur)[i],
            sedimentologie_weight=base + _WEIGHT_DELTA[t],
            sedimentologie_tier=tier_base + i + 1,
        )
        for i, t in enumerate(SedimentologieVerfassungTyp)
    )
    return SedimentologieVerfassung(normen=normen)
