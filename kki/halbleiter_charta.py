"""#683 — HalbleiterCharta: Leitfähigkeit, Dotierung & Bandstruktur."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import List
from kki.kristallstruktur_register import KristallstrukturRegister, build_kristallstruktur_register


class HalbleiterChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    HALBLEITER_AKTIV = "halbleiter-aktiv"
    GRUNDLEGEND_HALBLEITER_AKTIV = "grundlegend-halbleiter-aktiv"


class HalbleiterChartaTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class HalbleiterChartaProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class HalbleiterChartaNorm:
    norm_id: str
    geltung: HalbleiterChartaGeltung
    typ: HalbleiterChartaTyp
    prozedur: HalbleiterChartaProzedur
    material_weight: float
    material_tier: int
    material_ids: List[str]
    material_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class HalbleiterCharta:
    charta_id: str
    normen: List[HalbleiterChartaNorm]
    parent: KristallstrukturRegister


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        HalbleiterChartaGeltung.GESPERRT: 0.0,
        HalbleiterChartaGeltung.HALBLEITER_AKTIV: 0.05,
        HalbleiterChartaGeltung.GRUNDLEGEND_HALBLEITER_AKTIV: 0.1,
    })
    _TIER_DELTA.update({
        HalbleiterChartaGeltung.GESPERRT: 0,
        HalbleiterChartaGeltung.HALBLEITER_AKTIV: 1,
        HalbleiterChartaGeltung.GRUNDLEGEND_HALBLEITER_AKTIV: 2,
    })
    _TYP_MAP.update({
        HalbleiterChartaGeltung.GESPERRT: HalbleiterChartaTyp.BEOBACHTUNG,
        HalbleiterChartaGeltung.HALBLEITER_AKTIV: HalbleiterChartaTyp.ANALYSE,
        HalbleiterChartaGeltung.GRUNDLEGEND_HALBLEITER_AKTIV: HalbleiterChartaTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        HalbleiterChartaGeltung.GESPERRT: HalbleiterChartaProzedur.INITIALISIEREN,
        HalbleiterChartaGeltung.HALBLEITER_AKTIV: HalbleiterChartaProzedur.AKTIVIEREN,
        HalbleiterChartaGeltung.GRUNDLEGEND_HALBLEITER_AKTIV: HalbleiterChartaProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        HalbleiterChartaGeltung.GESPERRT: [HalbleiterChartaGeltung.GESPERRT],
        HalbleiterChartaGeltung.HALBLEITER_AKTIV: [HalbleiterChartaGeltung.HALBLEITER_AKTIV],
        HalbleiterChartaGeltung.GRUNDLEGEND_HALBLEITER_AKTIV: [HalbleiterChartaGeltung.GRUNDLEGEND_HALBLEITER_AKTIV],
    })


_init_map()


def build_halbleiter_charta(*, charta_id: str = "halbleiter-charta") -> HalbleiterCharta:
    parent = build_kristallstruktur_register(register_id=f"{charta_id}-parent")
    normen: List[HalbleiterChartaNorm] = []
    for g in HalbleiterChartaGeltung:
        normen.append(HalbleiterChartaNorm(
            norm_id=f"{charta_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            material_weight=round(sum(e.material_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            material_tier=max(e.material_tier for e in parent.eintraege) + _TIER_DELTA[g],
            material_ids=[f"hc-{charta_id}-{g.value}-001", f"hc-{charta_id}-{g.value}-002"],
            material_tags=["material", "halbleiter", g.value],
        ))
    return HalbleiterCharta(charta_id=charta_id, normen=normen, parent=parent)


# ── #973 Halbleiter-Charta — Halbleitermaterialien im KKI-Schwarm ──────────────
from .nanomaterial_register import NanomaterialRegister, build_nanomaterial_register  # noqa: E402


class HalbleiterTyp(Enum):
    SILIZIUM = auto()
    GALLIUMNITRID = auto()
    PEROWSKIT = auto()
    ORGANISCH = auto()
    ZWEI_DIMENSIONAL = auto()


class HalbleiterProzedur(Enum):
    DOTIERUNG = auto()
    EPITAXIE = auto()
    LITHOGRAPHIE = auto()
    AETZUNG = auto()
    PASSIVIERUNG = auto()


_H973_WEIGHT_DELTA = {
    HalbleiterTyp.SILIZIUM: 0.14,
    HalbleiterTyp.GALLIUMNITRID: 0.19,
    HalbleiterTyp.PEROWSKIT: 0.17,
    HalbleiterTyp.ORGANISCH: 0.13,
    HalbleiterTyp.ZWEI_DIMENSIONAL: 0.21,
}
_H973_TYP_MAP = {
    HalbleiterTyp.SILIZIUM: "Silizium-Halbleiter",
    HalbleiterTyp.GALLIUMNITRID: "Galliumnitrid-Halbleiter",
    HalbleiterTyp.PEROWSKIT: "Perowskit-Halbleiter",
    HalbleiterTyp.ORGANISCH: "Organischer Halbleiter",
    HalbleiterTyp.ZWEI_DIMENSIONAL: "2D-Halbleiter",
}
_H973_PROZEDUR_MAP = {
    HalbleiterProzedur.DOTIERUNG: "Dotierung",
    HalbleiterProzedur.EPITAXIE: "Epitaxie",
    HalbleiterProzedur.LITHOGRAPHIE: "Lithographie",
    HalbleiterProzedur.AETZUNG: "Ätzung",
    HalbleiterProzedur.PASSIVIERUNG: "Passivierung",
}


@dataclass(frozen=True)
class HalbleiterNorm:
    name: str
    material_weight: float
    material_tier: int


@dataclass(frozen=True)
class Halbleiter:
    normen: tuple[HalbleiterNorm, ...]


def build_halbleiter(parent=None) -> Halbleiter:
    basis = parent.normen[-1].material_weight if parent and hasattr(parent, 'normen') else 0.0
    tier_base = (max(n.material_tier for n in parent.normen) if parent and hasattr(parent, 'normen') else 0)
    items = []
    for i, t in enumerate(HalbleiterTyp):
        delta = _H973_WEIGHT_DELTA.get(t, 0.0)
        items.append(HalbleiterNorm(name=_H973_TYP_MAP[t], material_weight=round(basis + delta, 4), material_tier=tier_base + i + 1))
    return Halbleiter(normen=tuple(items))
