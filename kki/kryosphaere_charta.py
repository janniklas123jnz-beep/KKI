from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .glaziologie_norm import GlaziologieNorm, build_glaziologie_norm


class KryosphaereChartaTyp(Enum):
    SCHNEEDECKE = auto()
    SEEEIS = auto()
    PERMAFROST = auto()
    GLETSCHER = auto()
    EISSCHELFE = auto()


class KryosphaereChartaProzedur(Enum):
    MONITORING = auto()
    MODELLIERUNG = auto()
    PROJEKTION = auto()
    BEWERTUNG = auto()
    SCHUTZ = auto()


_WEIGHT_DELTA = {
    KryosphaereChartaTyp.SCHNEEDECKE: 0.0,
    KryosphaereChartaTyp.SEEEIS: 2.0,
    KryosphaereChartaTyp.PERMAFROST: 4.0,
    KryosphaereChartaTyp.GLETSCHER: 6.0,
    KryosphaereChartaTyp.EISSCHELFE: 8.0,
}
_TYP_MAP = {
    KryosphaereChartaTyp.SCHNEEDECKE: "schneedecke",
    KryosphaereChartaTyp.SEEEIS: "seeeis",
    KryosphaereChartaTyp.PERMAFROST: "permafrost",
    KryosphaereChartaTyp.GLETSCHER: "gletscher",
    KryosphaereChartaTyp.EISSCHELFE: "eisschelfe",
}
_PROZEDUR_MAP = {
    KryosphaereChartaProzedur.MONITORING: "monitoring",
    KryosphaereChartaProzedur.MODELLIERUNG: "modellierung",
    KryosphaereChartaProzedur.PROJEKTION: "projektion",
    KryosphaereChartaProzedur.BEWERTUNG: "bewertung",
    KryosphaereChartaProzedur.SCHUTZ: "schutz",
}


@dataclass(frozen=True)
class KryosphaereChartaNorm:
    typ: KryosphaereChartaTyp
    prozedur: KryosphaereChartaProzedur
    glaziologie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class KryosphaereCharta:
    normen: tuple[KryosphaereChartaNorm, ...]
    canonical: bool = True

    def aggregates_charta_signal(self) -> dict:
        return {
            "charta_id": "kryosphaere-charta-899",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_kryosphaere_charta(parent: Optional[GlaziologieNorm] = None) -> KryosphaereCharta:
    if parent is None:
        parent = build_glaziologie_norm()
    base = sum(e.glaziologie_norm_weight for e in parent.normen)
    tier_base = max(e.glaziologie_norm_tier for e in parent.normen)
    normen = tuple(
        KryosphaereChartaNorm(
            typ=t,
            prozedur=list(KryosphaereChartaProzedur)[i],
            glaziologie_weight=base + _WEIGHT_DELTA[t],
            tier=tier_base + i + 1,
        )
        for i, t in enumerate(KryosphaereChartaTyp)
    )
    return KryosphaereCharta(normen=normen)
