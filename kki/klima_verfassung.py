from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .klimaprognose_charta import KlimaprognoseCharta, build_klimaprognose_charta


class KlimaVerfassungGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_KLIMA_SOUVERAEN = auto()
    KLIMA_SOUVERAEN = auto()
    KLIMA_SOUVERAEN_AKTIV = auto()
    KLIMA_SOUVERAEN_ABSOLUT = auto()


class KlimaVerfassungTyp(Enum):
    KLIMAVERFASSUNG = auto()
    KLIMASOUVERAENITAET = auto()
    KLIMAKONSTITUTION = auto()


class KlimaVerfassungProzedur(Enum):
    KLIMAVERFASSUNGSANALYSE = auto()
    KLIMAVERFASSUNGSSYNTHESE = auto()
    KLIMAVERFASSUNGSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[KlimaVerfassungGeltung, float] = {
    KlimaVerfassungGeltung.GESPERRT: 0.0,
    KlimaVerfassungGeltung.GRUNDLEGEND_KLIMA_SOUVERAEN: 2.1,
    KlimaVerfassungGeltung.KLIMA_SOUVERAEN: 4.2,
    KlimaVerfassungGeltung.KLIMA_SOUVERAEN_AKTIV: 6.3,
    KlimaVerfassungGeltung.KLIMA_SOUVERAEN_ABSOLUT: 8.4,
}

_TYP_MAP = {
    KlimaVerfassungGeltung.GESPERRT: KlimaVerfassungTyp.KLIMAVERFASSUNG,
    KlimaVerfassungGeltung.GRUNDLEGEND_KLIMA_SOUVERAEN: KlimaVerfassungTyp.KLIMAKONSTITUTION,
    KlimaVerfassungGeltung.KLIMA_SOUVERAEN: KlimaVerfassungTyp.KLIMAKONSTITUTION,
    KlimaVerfassungGeltung.KLIMA_SOUVERAEN_AKTIV: KlimaVerfassungTyp.KLIMASOUVERAENITAET,
    KlimaVerfassungGeltung.KLIMA_SOUVERAEN_ABSOLUT: KlimaVerfassungTyp.KLIMASOUVERAENITAET,
}

_PROZEDUR_MAP = {
    KlimaVerfassungGeltung.GESPERRT: KlimaVerfassungProzedur.KLIMAVERFASSUNGSANALYSE,
    KlimaVerfassungGeltung.GRUNDLEGEND_KLIMA_SOUVERAEN: KlimaVerfassungProzedur.KLIMAVERFASSUNGSANALYSE,
    KlimaVerfassungGeltung.KLIMA_SOUVERAEN: KlimaVerfassungProzedur.KLIMAVERFASSUNGSSYNTHESE,
    KlimaVerfassungGeltung.KLIMA_SOUVERAEN_AKTIV: KlimaVerfassungProzedur.KLIMAVERFASSUNGSSYNTHESE,
    KlimaVerfassungGeltung.KLIMA_SOUVERAEN_ABSOLUT: KlimaVerfassungProzedur.KLIMAVERFASSUNGSBEWERTUNG,
}


@dataclass(frozen=True)
class KlimaVerfassungsNorm:
    geltung: KlimaVerfassungGeltung
    klima_weight: float
    klima_tier: int
    klima_ids: tuple[str, ...]
    klima_tags: tuple[str, ...]
    typ: KlimaVerfassungTyp
    prozedur: KlimaVerfassungProzedur
    canonical: bool = True


@dataclass(frozen=True)
class KlimaVerfassung:
    normen: tuple[KlimaVerfassungsNorm, ...]
    parent: Optional[KlimaprognoseCharta] = None

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": "klima-verfassung-750",
            "total_weight": round(sum(n.klima_weight for n in self.normen), 4),
            "norm_count": len(self.normen),
        }


def build_klima_verfassung(parent: Optional[KlimaprognoseCharta] = None) -> KlimaVerfassung:
    if parent is None:
        parent = build_klimaprognose_charta()
    base = sum(n.klima_weight for n in parent.normen)
    tier_base = max(n.klima_tier for n in parent.normen)
    normen = tuple(
        KlimaVerfassungsNorm(
            geltung=g,
            klima_weight=round(base + _WEIGHT_DELTA[g], 4),
            klima_tier=tier_base + i + 1,
            klima_ids=(f"klima-verfassung-{g.name.lower()}-001",),
            klima_tags=("klima", "verfassung", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(KlimaVerfassungGeltung)
    )
    return KlimaVerfassung(normen=normen, parent=parent)
