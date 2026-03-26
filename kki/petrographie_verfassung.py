from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .gesteinsanalyse_charta import GesteinsanalyseCharta, build_gesteinsanalyse_charta


class PetrographieVerfassungTyp(Enum):
    GRUNDGESETZ = auto()
    FORSCHUNGSAUFTRAG = auto()
    BILDUNGSMANDAT = auto()
    ETHIKPRINZIP = auto()
    NACHHALTIGKEITSGEBOT = auto()


class PetrographieVerfassungProzedur(Enum):
    RATIFIZIERUNG = auto()
    REVISION = auto()
    INKRAFTTRETEN = auto()
    AUSLEGUNG = auto()
    DURCHSETZUNG = auto()


_WEIGHT_DELTA = {
    PetrographieVerfassungTyp.GRUNDGESETZ: 0.0,
    PetrographieVerfassungTyp.FORSCHUNGSAUFTRAG: 2.1,
    PetrographieVerfassungTyp.BILDUNGSMANDAT: 4.2,
    PetrographieVerfassungTyp.ETHIKPRINZIP: 6.3,
    PetrographieVerfassungTyp.NACHHALTIGKEITSGEBOT: 8.4,
}
_TYP_MAP = {
    PetrographieVerfassungTyp.GRUNDGESETZ: "grundgesetz",
    PetrographieVerfassungTyp.FORSCHUNGSAUFTRAG: "forschungsauftrag",
    PetrographieVerfassungTyp.BILDUNGSMANDAT: "bildungsmandat",
    PetrographieVerfassungTyp.ETHIKPRINZIP: "ethikprinzip",
    PetrographieVerfassungTyp.NACHHALTIGKEITSGEBOT: "nachhaltigkeitsgebot",
}
_PROZEDUR_MAP = {
    PetrographieVerfassungProzedur.RATIFIZIERUNG: "ratifizierung",
    PetrographieVerfassungProzedur.REVISION: "revision",
    PetrographieVerfassungProzedur.INKRAFTTRETEN: "inkrafttreten",
    PetrographieVerfassungProzedur.AUSLEGUNG: "auslegung",
    PetrographieVerfassungProzedur.DURCHSETZUNG: "durchsetzung",
}


@dataclass(frozen=True)
class PetrographieVerfassungNorm:
    typ: PetrographieVerfassungTyp
    prozedur: PetrographieVerfassungProzedur
    petrographie_weight: float
    petrographie_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class PetrographieVerfassung:
    normen: tuple[PetrographieVerfassungNorm, ...]
    canonical: bool = True

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": "petrographie-verfassung-890",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_petrographie_verfassung(parent: Optional[GesteinsanalyseCharta] = None) -> PetrographieVerfassung:
    if parent is None:
        parent = build_gesteinsanalyse_charta()
    base = sum(n.petrographie_weight for n in parent.normen)
    tier_base = max(n.tier for n in parent.normen)
    normen = tuple(
        PetrographieVerfassungNorm(
            typ=t,
            prozedur=list(PetrographieVerfassungProzedur)[i],
            petrographie_weight=base + _WEIGHT_DELTA[t],
            petrographie_tier=tier_base + i + 1,
        )
        for i, t in enumerate(PetrographieVerfassungTyp)
    )
    return PetrographieVerfassung(normen=normen)
