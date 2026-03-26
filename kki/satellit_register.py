"""Satellit-Register #982 — Katalog der Satellitentechnologien im KKI-Schwarm."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

from .raumfahrt_feld import Raumfahrt, build_raumfahrt


class SatellitTyp(Enum):
    KOMMUNIKATION = "KOMMUNIKATION"
    ERDBEOBACHTUNG = "ERDBEOBACHTUNG"
    NAVIGATION = "NAVIGATION"
    WISSENSCHAFT = "WISSENSCHAFT"
    MILITAER = "MILITAER"


class SatellitProzedur(Enum):
    DESIGN = "DESIGN"
    INTEGRATION = "INTEGRATION"
    TEST = "TEST"
    LAUNCH = "LAUNCH"
    BETRIEB = "BETRIEB"


_WEIGHT_DELTA: dict[str, float] = {
    "KOMMUNIKATION": 0.13,
    "ERDBEOBACHTUNG": 0.15,
    "NAVIGATION": 0.17,
    "WISSENSCHAFT": 0.14,
    "MILITAER": 0.12,
}

_TYP_MAP: dict[SatellitTyp, str] = {
    SatellitTyp.KOMMUNIKATION: "Kommunikationssatellit",
    SatellitTyp.ERDBEOBACHTUNG: "Erdbeobachtungssatellit",
    SatellitTyp.NAVIGATION: "Navigationssatellit",
    SatellitTyp.WISSENSCHAFT: "Wissenschaftssatellit",
    SatellitTyp.MILITAER: "Militärsatellit",
}

_PROZEDUR_MAP: dict[SatellitProzedur, str] = {
    SatellitProzedur.DESIGN: "Design",
    SatellitProzedur.INTEGRATION: "Integration",
    SatellitProzedur.TEST: "Test",
    SatellitProzedur.LAUNCH: "Launch",
    SatellitProzedur.BETRIEB: "Betrieb",
}


@dataclass(frozen=True)
class SatellitEintrag:
    name: str
    raumfahrt_weight: float
    raumfahrt_tier: int


@dataclass(frozen=True)
class SatellitRegister:
    eintraege: tuple[SatellitEintrag, ...]


def build_satellit_register(parent=None) -> SatellitRegister:
    if parent and hasattr(parent, 'normen'):
        basis = parent.normen[-1].raumfahrt_weight
        tier_base = max(n.raumfahrt_tier for n in parent.normen)
    elif parent and hasattr(parent, 'eintraege'):
        basis = parent.eintraege[-1].raumfahrt_weight
        tier_base = max(e.raumfahrt_tier for e in parent.eintraege)
    else:
        basis = 0.0
        tier_base = 0
    items = []
    for i, t in enumerate(SatellitTyp):
        delta = _WEIGHT_DELTA.get(t.name, 0.0)
        items.append(SatellitEintrag(name=_TYP_MAP[t], raumfahrt_weight=round(basis + delta, 4), raumfahrt_tier=tier_base + i + 1))
    return SatellitRegister(eintraege=tuple(items))
